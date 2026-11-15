"""Package a verified, cached real-data sequence for backend-independent viewing."""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.pipeline import ROOT, DATA

def export(identifier):
    source=DATA/identifier
    manifest=json.loads((source/'manifest.json').read_text())
    if manifest.get('status') != 'ready' or len(manifest.get('frames', [])) < 2:
        raise ValueError('Only completed sequences with at least two real frames can be exported.')
    target=ROOT/'frontend/public/showcase'/identifier
    target.mkdir(parents=True,exist_ok=True)
    manifest['cached_showcase']=True
    for f in manifest['frames']:
        name=Path(f['image']).name
        shutil.copyfile(source/name,target/name)
        f['image']=f'/showcase/{identifier}/{name}'
    manifest['manifest_url']=f'/showcase/{identifier}/manifest.json'
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False))
    entries = []
    for path in sorted(target.parent.glob('*/manifest.json')):
        item = json.loads(path.read_text())
        if item.get('status') == 'ready' and len(item.get('frames', [])) >= 2:
            entries.append({'id':path.parent.name,'query':item['query'],
                            'frames':len(item['frames']),'partial':item.get('partial',False),
                            'label':item.get('label'), 'description':item.get('description'),
                            'preview':item['frames'][0]['image'],
                            'start':item['frames'][0].get('date'),'end':item['frames'][-1].get('date')})
    (target.parent/'index.json').write_text(json.dumps(entries,indent=2))
    print('Exported',len(manifest['frames']),'real PNG previews and provenance; no synthetic assets.')
if __name__=='__main__':export(sys.argv[1])
