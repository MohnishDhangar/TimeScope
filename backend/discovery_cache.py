"""Exact-region metadata reuse. Never substitutes preview frames or another field."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlsplit
from astropy.table import Table
from .storage import runtime_store

SNAPSHOTS = Path(__file__).parent/'discovery_snapshots'
MAX_AGE_SECONDS = 24*3600


def query_identity(search):
    return {'ra':float(search.ra),'dec':float(search.dec),'fov':float(search.fov),
            'collections':['spherex_dr1','spherex_qr3'],'maxrec':1000,
            'geometry':'circumscribed-circle-v1'}


def query_key(search):
    return hashlib.sha256(json.dumps(query_identity(search),sort_keys=True).encode()).hexdigest()


def record(search,rows,retrieved_utc=None):
    entries=[]
    for row in rows:
        url=str(row['access_url']);p=urlsplit(url)
        if p.scheme!='https' or p.netloc!='irsa.ipac.caltech.edu' or not p.path.startswith('/ibe/data/spherex/'):
            continue
        entries.append([str(row['obs_id']),str(row['obs_collection']),float(row['t_min']),url])
    return {'schema_version':1,'query':query_identity(search),
            'retrieved_utc':retrieved_utc or datetime.now(timezone.utc).isoformat(),
            'discovery_method':rows.meta.get('discovery_method','astroquery-sia-v2'),
            'query_overflow':bool(rows.meta.get('query_overflow',False) or len(rows)>=1000),'rows':entries}


def save(search,rows,root):
    # Partial saved-inventory subsets are never promoted to complete query caches.
    if rows.meta.get('discovery_limited'):return
    runtime_store(root).write_json(Path(root)/'discovery-cache'/f'{query_key(search)}.json',record(search,rows))


def load(search,root):
    key=query_key(search)
    store=runtime_store(root)
    with store.mutex,store.pin(Path(root)/'discovery-cache'):
        for source in [Path(root)/'discovery-cache'/f'{key}.json', SNAPSHOTS/f'{key}.json']:
            try:
                if source.is_symlink() or source.stat().st_size>16*1024*1024:continue
                data=json.loads(source.read_text())
                if data['schema_version']!=1 or data['query']!=query_identity(search):continue
                age=time.time()-datetime.fromisoformat(data['retrieved_utc']).timestamp()
                if not 0<=age<=MAX_AGE_SECONDS:continue
                if len(data['rows'])>1000:continue
                rows=Table(rows=data['rows'],names=['obs_id','obs_collection','t_min','access_url'])
                validated=record(search,rows)
                if len(validated['rows'])!=len(rows):continue
                if any(str(row['obs_collection']) not in data['query']['collections'] for row in rows):continue
                rows.meta.update(discovery_method='exact-query-cached-inventory',
                    discovery_cached=True,inventory_retrieved_utc=data['retrieved_utc'],
                    inventory_age_seconds=round(age,1),original_discovery_method=data['discovery_method'],
                    query_overflow=data.get('query_overflow',False),
                    inventory_snapshot_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
                return rows
            except (OSError,ValueError,KeyError,TypeError,OverflowError):continue
    return None
