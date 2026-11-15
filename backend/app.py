from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import json
import uuid
import logging
from .errors import PipelineError
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from .pipeline import DATA, ROOT, Search, run

app = FastAPI(title='TimeScope')
DATA.mkdir(parents=True, exist_ok=True)
SHOWCASE = ROOT/'frontend/dist/showcase'
executor = ThreadPoolExecutor(max_workers=1)
lock = Lock()
jobs = {}

def persist(identifier, state):
    folder = DATA / identifier
    folder.mkdir(parents=True, exist_ok=True)
    temporary = folder / 'job.json.tmp'
    temporary.write_text(json.dumps(state, allow_nan=False))
    temporary.replace(folder / 'job.json')


def process(query, identifier):
    def update(message):
        state = {'status':'running','id':identifier,'message':message,'query':query.model_dump()}
        jobs[identifier] = state
        persist(identifier, state)
    try:
        jobs[identifier] = run(query,identifier,update)
    except PipelineError as exc:
        jobs[identifier] = {'status':'failed','id':identifier,'message':str(exc),'code':exc.code,'retryable':exc.retryable,'query':query.model_dump()}
    except Exception:
        logging.exception('Processing failed for session %s',identifier)
        jobs[identifier] = {'status':'failed','id':identifier,'message':'This field could not be processed. Try another field or retry; diagnostic details are recorded on the server.','code':'processing_failed','retryable':True,'query':query.model_dump()}
    finally:
        try:
            persist(identifier, jobs[identifier])
        except OSError:
            logging.exception('Could not persist status for session %s', identifier)
        finally:
            lock.release()

@app.get('/api/health')
def health():
    return {'status':'ok','mode':'development','live_search':'available'}

@app.post('/api/sessions',status_code=202)
def create(query: Search):
    if not lock.acquire(blocking=False):
        raise HTTPException(429,'A processing job is running. Try again shortly.')
    identifier = uuid.uuid4().hex
    jobs[identifier] = {'status':'queued','id':identifier,'message':'Waiting for processing','query':query.model_dump()}
    try:
        persist(identifier, jobs[identifier])
        executor.submit(process,query,identifier)
    except Exception:
        jobs.pop(identifier, None)
        lock.release()
        logging.exception('Could not queue session %s', identifier)
        raise HTTPException(503,'Processing could not start. Please retry shortly.')
    return {'id':identifier}

@app.get('/api/sessions/{identifier}')
def get(identifier: str):
    if len(identifier)!=32 or any(c not in '0123456789abcdef' for c in identifier):
        raise HTTPException(404,'Unknown session')
    if identifier in jobs:
        return jobs[identifier]
    path = DATA/identifier/'manifest.json'
    if path.exists():
        return json.loads(path.read_text())
    status_path = DATA/identifier/'job.json'
    if status_path.exists():
        state = json.loads(status_path.read_text())
        if state['status'] in ('queued','running'):
            state.update(status='failed',code='interrupted',retryable=True,
                         message='Processing was interrupted by a backend restart. Retry this field to start a new search.')
            persist(identifier, state)
        return state
    bundled = read_example(SHOWCASE/identifier/'manifest.json')
    if bundled is not None:
        return bundled
    raise HTTPException(404,'Unknown session; submit again.')

def read_example(path):
    try:
        manifest = json.loads(path.read_text())
        if manifest.get('status') != 'ready' or len(manifest.get('frames', [])) < 2:
            return None
        if not all((path.parent / f['image'].rsplit('/',1)[-1]).is_file() for f in manifest['frames']):
            return None
        # Do not fabricate query metadata for incomplete bundles.
        for key in ('ra','dec','fov'):
            if key not in manifest['query']:
                return None
        return manifest
    except (OSError, ValueError, KeyError, TypeError):
        return None


@app.get('/api/examples')
def examples():
    results = {}
    # Local sequences override bundled copies with the same identity.
    for root in (SHOWCASE, DATA):
        for path in sorted(root.glob('*/manifest.json')):
            manifest = read_example(path)
            if manifest is None:
                continue
            identifier = path.parent.name
            results[identifier] = {'id':identifier,'query':manifest['query'],
                'frames':len(manifest['frames']), 'partial':manifest.get('partial',False),
                'bundled':root == SHOWCASE, 'label':manifest.get('label'),
                'description':manifest.get('description'), 'preview':manifest['frames'][0]['image'],
                'start':manifest['frames'][0].get('date'), 'end':manifest['frames'][-1].get('date')}
    return sorted(results.values(), key=lambda item: (item['partial'], -item['frames'], item['id']))

app.mount('/artifacts', StaticFiles(directory=DATA), name='artifacts')
if (ROOT/'frontend/dist').exists():
    app.mount('/',StaticFiles(directory=ROOT/'frontend/dist',html=True),name='frontend')
