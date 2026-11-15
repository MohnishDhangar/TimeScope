import shutil
from pathlib import Path
import numpy as np
import pytest
from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
from backend import pipeline as p
from backend.errors import FrameUnavailable, PipelineError

@pytest.fixture
def fake_archive(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'DATA',tmp_path)
    rows=Table(rows=[(str(i),'spherex_dr1',float(i),f'https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/2/{i}.fits') for i in range(6)],names=['obs_id','obs_collection','t_min','access_url'])
    monkeypatch.setattr(p.Irsa,'query_sia',lambda **kw:rows)
    monkeypatch.setattr(p,'selection',lambda rows,count:list(rows)[:count])
    def generate(url,params,dest):
        i=int(Path(url).stem)
        w=WCS(naxis=2);w.wcs.ctype=['RA---TAN','DEC--TAN'];w.wcs.crval=[10,20];w.wcs.crpix=[31,31];w.wcs.cdelt=[-.002,.002]
        h=w.to_header();h['DATE-OBS']=f'2025-05-{i+1:02d}T00:00:00';h['OBSID']=str(i);h['DETECTOR']=2;h['BUNIT']='MJy/sr'
        h['CTYPE1W']='LINEAR';h['CTYPE2W']='LINEAR';h['CRVAL1W']=1.;h['CRVAL2W']=.1
        fits.HDUList([fits.PrimaryHDU(),fits.ImageHDU(np.ones((64,64)),header=h,name='IMAGE'),fits.ImageHDU(np.zeros((64,64),dtype='int32'),name='FLAGS')]).writeto(dest,overwrite=True)
        return 'synthetic-test-checksum'
    return generate

def test_one_503_keeps_other_frames_and_reports_partial(fake_archive,monkeypatch,tmp_path):
    def download(url,params,dest):
        if url.endswith('/0.fits'):raise FrameUnavailable('IRSA returned HTTP 503.',503)
        return fake_archive(url,params,dest)
    monkeypatch.setattr(p,'download',download)
    result=p.run(p.Search(ra=10,dec=20,frames=3),'partial')
    assert result['partial'] and len(result['frames'])==2
    assert result['failed_frames'][0]['http_status']==503
    assert [f['obs_id'] for f in result['frames']]==['1','2']

def test_persistent_failure_is_bounded_and_actionable(fake_archive,monkeypatch,tmp_path):
    calls=[]
    def fail(*args):calls.append(1);raise FrameUnavailable('IRSA returned HTTP 503.',503)
    monkeypatch.setattr(p,'download',fail)
    with pytest.raises(PipelineError,match='at least two') as exc:p.run(p.Search(ra=10,dec=20),'failed')
    assert len(calls)==3
    assert exc.value.retryable
    assert (tmp_path/'failed/retrieval-report.json').exists()
    assert not (tmp_path/'failed/manifest.json').exists()

def test_success_cache_is_scoped_to_request(tmp_path,monkeypatch):
    import json,hashlib
    monkeypatch.setattr(p,'DATA',tmp_path)
    url='https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/2/a.fits';params={'center':'10,20d','size':.1}
    key=hashlib.sha256(json.dumps([url,params],sort_keys=True).encode()).hexdigest()
    cache=tmp_path/'cutout-cache';cache.mkdir();(cache/f'{key}.fits').write_bytes(b'previously-validated-cutout')
    class NoNetwork:
        def __init__(self):raise AssertionError('Network requested for cached data')
    monkeypatch.setattr(p.requests,'Session',NoNetwork)
    assert p.download(url,params,tmp_path/'copy.fits')==hashlib.sha256(b'previously-validated-cutout').hexdigest()
    with pytest.raises(AssertionError):p.download(url,{'center':'11,20d','size':.1},tmp_path/'different.fits')

def test_failed_download_leaves_no_partial_file(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'DATA',tmp_path)
    class Response:
        status_code=503
        def __enter__(self):return self
        def __exit__(self,*a):pass
    class Session:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def mount(self,*a):pass
        def get(self,*a,**kw):return Response()
    monkeypatch.setattr(p.requests,'Session',Session)
    with pytest.raises(FrameUnavailable) as exc:p.download('https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/2/a.fits',{},tmp_path/'a.fits')
    assert exc.value.status==503
    assert not (tmp_path/'a.part').exists()

def test_failed_capabilities_falls_back_and_keeps_chronological_pairs(fake_archive,monkeypatch):
    rows=Table(rows=[(str(i),'spherex_dr1',float(i),f'https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/2/{i}.fits') for i in (2,0,1)],names=['obs_id','obs_collection','t_min','access_url'])
    rows.meta['discovery_method']='direct-sia-v2'
    def fail(**kwargs):raise RuntimeError('capabilities unavailable')
    monkeypatch.setattr(p.Irsa,'query_sia',fail)
    monkeypatch.setattr(p,'direct_sia',lambda search:rows)
    monkeypatch.setattr(p,'download',fake_archive)
    result=p.run(p.Search(ra=10,dec=20,frames=3),'fallback')
    assert result['discovery_method']=='direct-sia-v2'
    assert [f['obs_id'] for f in result['frames']]==['0','1','2']
    assert [f['image'].split('/')[-1] for f in result['frames']]==['1.png','2.png','0.png']
    assert [(p['a'],p['b']) for p in result['diagnostics']['pairs']]==[(0,1),(0,2),(1,2)]


@pytest.mark.parametrize('kind',['runtime-cache','bundled-historical'])
def test_exact_inventory_fallback_fetches_requested_cutouts_and_discloses_reuse(fake_archive,monkeypatch,tmp_path,kind):
    from backend import discovery_cache
    from datetime import datetime,timezone
    import json
    query=p.Search(ra=10,dec=20,frames=3)
    rows=Table(rows=[(str(i),'spherex_dr1',float(i),f'https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/2/{i}.fits') for i in range(3)],names=['obs_id','obs_collection','t_min','access_url'])
    if kind=='runtime-cache':discovery_cache.save(query,rows,tmp_path)
    else:
        bundle=tmp_path/'bundle';bundle.mkdir()
        monkeypatch.setattr(discovery_cache,'SNAPSHOTS',bundle)
        (bundle/f'{discovery_cache.query_key(query)}.json').write_text(json.dumps(discovery_cache.record(query,rows)))
    def unavailable(*args,**kwargs):raise RuntimeError('synthetic discovery outage')
    monkeypatch.setattr(p.Irsa,'query_sia',unavailable)
    monkeypatch.setattr(p,'direct_sia',unavailable)
    requests=[]
    def download(url,params,dest):
        requests.append(params.copy())
        return fake_archive(url,params,dest)
    monkeypatch.setattr(p,'download',download)
    result=p.run(query,'cached-discovery')
    assert result['status']=='ready' and result['discovery_cached']
    assert all(r['center']=='10.0,20.0d' for r in requests)
    assert len(requests)==3
    assert result['inventory_kind']==kind
    assert result['discovery_provenance']['inventory_kind']==kind
    assert any('This is not a fresh archive discovery query.' in w for w in result['warnings'])
    assert all(not f['cutout_cached'] for f in result['frames'])
