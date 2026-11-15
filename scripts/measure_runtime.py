"""Offline resource replay of preserved REAL FITS; never contacts IRSA.

Run with a separate empty TIMESCOPE_DATA_DIR. The source fixtures are outside it.
Five distinct job IDs exercise processing and aggregate runtime growth.
"""
import argparse
import hashlib
import json
import resource
import shutil
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from astropy.table import Table
from astropy.time import Time
from backend import pipeline as p
from backend.storage import runtime_store

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fixture',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    fixture=args.fixture.resolve()
    if fixture.is_relative_to(p.DATA):raise ValueError('Fixtures must be outside disposable runtime storage')
    manifest=json.loads((fixture/'manifest.json').read_text())
    paths={}
    rows=[]
    for frame in manifest['frames']:
        original=fixture/(Path(frame['image']).stem+'.fits')
        digest=hashlib.sha256(original.read_bytes()).hexdigest()
        if digest!=frame['sha256']:raise ValueError('Source checksum mismatch')
        paths[frame['source_url']]=original
        rows.append((frame['obs_id'],frame['collection'],float(Time(frame['date']).mjd),frame['source_url']))
    inventory=Table(rows=rows,names=['obs_id','obs_collection','t_min','access_url'])
    inventory.meta['discovery_method']='offline-real-fits-resource-replay'
    store=runtime_store(p.DATA)
    def replay(url,params,dest):
        source=paths[url]
        with store.reserve(source.stat().st_size):shutil.copyfile(source,dest)
        return hashlib.sha256(dest.read_bytes()).hexdigest()
    p.download=replay
    measurements=[]
    for i in range(5):
        start=time.monotonic()
        result=p.run(p.Search(**manifest['query']),f'{i+1:032x}',inventory=inventory)
        measurements.append({'job':i+1,'elapsed_seconds':round(time.monotonic()-start,3),
            'frames':len(result['frames']),'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'runtime_bytes':store.size(),'evictions':store.evicted})
    report={'kind':'offline real FITS processing, no network; neither cold nor warm live-search latency',
        'python':sys.version,'fixture_sha256':hashlib.sha256((fixture/'manifest.json').read_bytes()).hexdigest(),
        'runtime_limit_bytes':store.limit,'measurements':measurements}
    for name in ['memory.current','memory.max','memory.peak']:
        path=Path('/sys/fs/cgroup')/name
        if path.exists():report['local_cgroup_'+name]=path.read_text().strip()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
