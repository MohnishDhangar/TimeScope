"""Small-field, qualitative SPHEREx viewer pipeline. No detection claims."""
from pathlib import Path
from urllib.parse import urlsplit
from datetime import datetime, timezone
import os
import hashlib
import json
import math
import time
import shutil
import logging
import io
from contextvars import ContextVar
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astroquery.ipac.irsa import Irsa
from reproject import reproject_interp
from PIL import Image
from .diagnostics import compare
from .discovery import direct_sia
from .discovery_cache import load as cached_discovery, save as save_discovery
from .storage import runtime_store
from .errors import PipelineError, FrameUnavailable
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('TIMESCOPE_DATA_DIR', str(ROOT / 'data'))).expanduser().resolve()
DEADLINE = ContextVar('pipeline_deadline', default=None)
CUTOUT_REUSE = ContextVar('cutout_reuse', default=False)

def check_deadline():
    if DEADLINE.get() is not None and time.monotonic() >= DEADLINE.get():
        raise PipelineError('Processing time budget reached. Retry with fewer frames or a smaller field.', 'job_timeout', True)

class Search(BaseModel):
    ra: float = Field(ge=0, lt=360, allow_inf_nan=False)
    dec: float = Field(ge=-90, le=90, allow_inf_nan=False)
    fov: float = Field(default=5, ge=1, le=15, allow_inf_nan=False)
    frames: int = Field(default=6, ge=2, le=12)

def selection(rows, count):
    # obs_id alone is NOT unique: simultaneous detector exposures share it.
    unique = {}
    for row in rows:
        url = str(row['access_url'])
        detector = urlsplit(url).path.split('/')[-2]
        key = (str(row['obs_id']), detector)
        if key not in unique or str(row['obs_collection']) == 'spherex_dr1':
            unique[key] = row
    groups = {}
    for (_, detector), row in unique.items():
        groups.setdefault(detector, []).append(row)
    if not groups:
        raise ValueError('No spectral images found for these coordinates.')
    group = max(groups.values(), key=lambda g: len({float(r['t_min']) for r in g}))
    by_time = {float(r['t_min']): r for r in group}
    ordered = [by_time[t] for t in sorted(by_time)]
    if len(ordered) < 2:
        raise ValueError('Fewer than two distinct observation times found.')
    return [ordered[i] for i in np.unique(np.linspace(0, len(ordered)-1, min(count,len(ordered))).astype(int))]

def download(url, params, dest):
    p = urlsplit(url)
    if p.scheme != 'https' or p.netloc != 'irsa.ipac.caltech.edu' or not p.path.startswith('/ibe/data/spherex/'):
        raise ValueError('Unexpected archive URL.')
    # Cache keys include exact coordinates and field size; never reuse another field.
    key = hashlib.sha256(json.dumps([url,params],sort_keys=True).encode()).hexdigest()
    cache = DATA/'cutout-cache'/f'{key}.fits'
    cache.parent.mkdir(parents=True,exist_ok=True)
    store = runtime_store(DATA)
    CUTOUT_REUSE.set(dest.exists())
    check_deadline()
    with store.mutex:
        if cache.exists():
            with store.pin(cache), store.pin(dest.parent), store.reserve(cache.stat().st_size):
                shutil.copyfile(cache,dest)
                CUTOUT_REUSE.set(True)
    if not dest.exists():
        tmp = dest.with_suffix('.part')
        try:
            with store.pin(dest.parent), store.reserve(64*1024*1024), requests.Session() as client:
                client.mount('https://', HTTPAdapter(max_retries=Retry(total=2, backoff_factor=1,
                    status_forcelist=[429,502,503,504],raise_on_status=False,respect_retry_after_header=False)))
                with client.get(url, params=params, timeout=(10,30), stream=True, allow_redirects=False) as response:
                    if response.status_code != 200:
                        raise FrameUnavailable(f'IRSA returned HTTP {response.status_code} for this observation.',response.status_code)
                    size = 0
                    with tmp.open('wb') as out:
                        for chunk in response.iter_content(65536):
                            check_deadline()
                            size += len(chunk)
                            if size > 64*1024*1024:
                                raise FrameUnavailable('This cutout exceeds the 64 MiB download limit.')
                            out.write(chunk)
            try:
                with fits.open(tmp) as h:
                    if 'IMAGE' not in h or 'FLAGS' not in h:
                        raise FrameUnavailable('IRSA returned a cutout without required science extensions.')
            except (OSError,ValueError) as exc:
                raise FrameUnavailable('IRSA returned an unreadable FITS cutout.') from exc
            tmp.replace(dest)
            with store.pin(cache), store.pin(dest.parent), store.reserve(dest.stat().st_size):
                shutil.copyfile(dest,cache)
        except requests.RequestException as exc:
            raise FrameUnavailable('IRSA did not respond successfully before the download retry limit.') from exc
        finally:
            tmp.unlink(missing_ok=True)
    digest = hashlib.sha256()
    with dest.open('rb') as original:
        for block in iter(lambda:original.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()

def run(search, job, progress=lambda _: None, *, inventory=None):
    store = runtime_store(DATA)
    token = DEADLINE.set(time.monotonic()+240)
    try:
        with store.pin(DATA/job):
            store.cleanup()
            return _run(search, job, progress, inventory=inventory)
    finally:
        DEADLINE.reset(token)

def _run(search, job, progress, *, inventory=None):
    folder = DATA / job
    folder.mkdir(parents=True, exist_ok=True)
    progress('Searching IRSA')
    Irsa.TIMEOUT = 60
    # Circumscribe the square output field. Search cap is disclosed in manifest.
    if inventory is not None:
        rows = inventory
    else:
        try:
            rows = Irsa.query_sia(pos=(search.ra,search.dec,search.fov/120*math.sqrt(2)),collection=['spherex_dr1','spherex_qr3'],maxrec=1000)
        except Exception:
            logging.warning('Archive client discovery failed; trying direct SIA query')
            progress('Retrying discovery through direct SIA')
            try:
                rows = direct_sia(search)
            except Exception as exc:
                rows = cached_discovery(search, DATA)
                if rows is None:
                    logging.exception('Both IRSA discovery routes failed; no exact-query inventory available')
                    raise PipelineError('IRSA observation search is unavailable. Try again shortly; your coordinates have not been replaced with example data.', 'archive_search_unavailable', True) from exc
                logging.warning('Reusing exact-query metadata from %s after discovery failure',rows.meta['inventory_retrieved_utc'])
                progress('Discovery unavailable: reusing exact-query metadata; retrieving cutouts for this field')
        if not rows.meta.get('discovery_cached'):
            save_discovery(search, rows, DATA)
    check_deadline()
    inventory_text = io.StringIO()
    rows.write(inventory_text,format='ascii.ecsv')
    inventory_bytes = inventory_text.getvalue().encode()
    with runtime_store(DATA).reserve(len(inventory_bytes)):
        (folder/'discovery.ecsv').write_bytes(inventory_bytes)
    del inventory_text, inventory_bytes
    try:
        selected = selection(rows,search.frames)
    except ValueError as exc:
        raise PipelineError(str(exc),'insufficient_observations',False) from exc
    size = max(16, math.ceil(search.fov*60/6.15))
    ref = WCS(naxis=2)
    ref.wcs.ctype = ['RA---TAN','DEC--TAN']
    ref.wcs.crval = [search.ra, search.dec]
    ref.wcs.crpix = [(size+1)/2,(size+1)/2]
    ref.wcs.cdelt = [-search.fov/60/size,search.fov/60/size]
    arrays, frames, failures = [], [], []
    consecutive_failures = 0
    started = time.monotonic()
    for i,row in enumerate(selected):
        check_deadline()
        if consecutive_failures >= 3 or time.monotonic()-started > 240:
            failures.extend({'obs_id':str(r['obs_id']),'source_url':str(r['access_url']),'reason':'Not attempted: archive failure/time budget reached.'} for r in selected[i:])
            break
        progress(f'Downloading and aligning {i+1}/{len(selected)} · {len(frames)} usable · {len(failures)} skipped')
        url = str(row['access_url'])
        params = {'center':f'{search.ra},{search.dec}d','size': search.fov/60*1.5}
        path = folder/f'{i}.fits'
        CUTOUT_REUSE.set(False)
        try:
            digest = download(url,params,path)
        except FrameUnavailable as exc:
            logging.warning('Skipping %s: %s',url,exc)
            failures.append({'obs_id':str(row['obs_id']),'source_url':url,'reason':str(exc),'http_status':exc.status})
            consecutive_failures += 1
            continue
        consecutive_failures = 0
        with fits.open(path) as h:
            head = h['IMAGE'].header
            if head.get('NAXIS1',0)*head.get('NAXIS2',0) > 1024**2:
                raise PipelineError('Cutout dimensions exceed the bounded preview limit. Try a smaller field.', 'cutout_too_large', True)
            w = WCS(head,h).celestial
            values = h['IMAGE'].data.astype(float)
            flags = h['FLAGS'].data.astype(np.int64)
            # Conservative preview policy: retain SOURCE and FULLSAMPLE informational bits.
            bad = (flags & ~((1<<21)|(1<<12))) != 0
            values[bad] = np.nan
            aligned, footprint = reproject_interp((values,w),ref,shape_out=(size,size))
            valid = np.isfinite(aligned) & (footprint > 0)
            if valid.mean() < .1:
                failures.append({'obs_id':str(row['obs_id']),'source_url':url,'reason':'Less than 10% valid output coverage.'})
                continue
            aligned[~valid] = np.nan
            x,y = w.world_to_pixel_values(search.ra,search.dec)
            spectral_header = head.copy()
            for key in list(spectral_header):
                if key.startswith(('A_','B_','AP_','BP_')):
                    del spectral_header[key]
            sw = WCS(spectral_header,h,key='W')
            wave = sw.all_pix2world([[x,y]],0)[0]
            center_wave = float(wave[0]) if np.isfinite(wave[0]) else None
            # WCS transformation self-consistency, not measured source registration.
            rx,ry = w.world_to_pixel_values(*w.pixel_to_world_values(x,y))
            arrays.append(aligned)
            frames.append({'obs_id':str(head['OBSID']), 'date':str(head['DATE-OBS']),
              'detector':int(head['DETECTOR']), 'unit':str(head['BUNIT']),
              'collection':str(row['obs_collection']), 'source_url':url,'cutout_parameters':params,
              'sha256':digest,'cutout_cached':CUTOUT_REUSE.get(),'wavelength_um_at_center':center_wave,'coverage':float(valid.mean()),
              'wcs_roundtrip_pixels':float(np.hypot(rx-x,ry-y)),
              'image':f'/artifacts/{job}/{i}.png'})
    runtime_store(DATA).write_json(folder/'retrieval-report.json', {'query':search.model_dump(),'usable_frames':len(frames),'failed_frames':failures})
    if len(frames) < 2:
        raise PipelineError(f'Only {len(frames)} usable observation(s) could be loaded; at least two are needed. {len(failures)} were skipped due to retrieval or coverage problems. Try again shortly. Successfully downloaded cutouts are cached.', 'insufficient_usable_frames', True)
    ordered = sorted(zip(frames, arrays), key=lambda item: item[0]['date'])
    frames, arrays = map(list, zip(*ordered))
    finite = np.concatenate([a[np.isfinite(a)] for a in arrays])
    low,high = np.percentile(finite,[1,99.5])
    for array,frame in zip(arrays,frames):
        level = np.arcsinh(10*np.clip((array-low)/max(high-low,1e-12),0,1))/np.arcsinh(10)
        gray = (np.nan_to_num(level)*255).astype('uint8')
        rgba = np.dstack([gray,gray,gray,np.isfinite(array).astype('uint8')*255])
        # FITS row 0 is the south edge for this north-up TAN grid.
        check_deadline()
        with runtime_store(DATA).reserve(rgba.nbytes+65536):
            Image.fromarray(rgba[::-1]).save(folder/Path(frame['image']).name)
    manifest = {'schema_version':1,'processor_version':'bounded-v2','status':'ready','id':job,'query':search.model_dump(),
       'discovery_limited':rows.meta.get('discovery_limited',False),
       'discovery_cached':rows.meta.get('discovery_cached',False),
       'inventory_kind':rows.meta.get('inventory_kind'),
       'discovery_provenance':dict(rows.meta),
       'discovery_method':rows.meta.get('discovery_method','astroquery-sia-v2'),
       'created_utc':datetime.now(timezone.utc).isoformat(),'rows_found':len(rows),
       'failed_frames':failures,'requested_frames':search.frames,'partial':len(frames)<len(selected),'possibly_truncated':len(rows)>=1000 or rows.meta.get('query_overflow',False),'frames':frames,
       'reference_wcs':dict(ref.to_header()),'display_range':[float(low),float(high)],
       'warnings':['Qualitative viewing only: wavelength and PSF matching have not been validated.',
       'No motion or variability detection is claimed. Bright-peak checks are preliminary, not catalog-confirmed stationary-source residuals.',
       'Preview excludes all flagged pixels except SOURCE and FULLSAMPLE; originals are preserved.']}
    if manifest['discovery_limited']:
        manifest['warnings'].append('Selected from a saved inventory whose footprints contain the requested center; this is not a complete archive search.')
    if manifest['discovery_cached']:
        manifest['warnings'].append('Archive metadata snapshot retrieved '+rows.meta['inventory_retrieved_utc']+'. Observations released after that date may be missing. This is not a fresh archive discovery query.')
    reports = []
    for a in range(len(arrays)):
        for b in range(a+1, len(arrays)):
            report = compare(arrays[a], arrays[b], abs(ref.wcs.cdelt[0])*3600)
            report.update(a=a, b=b, quantitative_comparison_allowed=False)
            reports.append(report)
    manifest['diagnostics'] = {'method':'bright-peak-centroids-v1', 'pairs':reports,
        'limitations':'Exploratory geometry; wavelength and PSF compatibility not established.'}
    manifest['temporary_session'] = True
    manifest['expires_utc'] = datetime.fromtimestamp(time.time()+runtime_store(DATA).ttl, timezone.utc).isoformat()
    runtime_store(DATA).write_json(folder/'manifest.json',manifest)
    return manifest
