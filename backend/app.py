from concurrent.futures import ThreadPoolExecutor
from threading import Lock, RLock
from collections import deque
from contextlib import ExitStack
import os
import re
import time
from datetime import datetime, timezone
import json
import uuid
import logging
from .errors import PipelineError
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from .storage import runtime_store
from .pipeline import DATA, ROOT, Search, run, PROCESSOR_VERSION

app = FastAPI(title='TimeScope')
DATA.mkdir(parents=True, exist_ok=True)
SHOWCASE = ROOT/'frontend/dist/showcase'
executor = ThreadPoolExecutor(max_workers=1)
lock = Lock()
jobs = {}
state_lock = RLock()
admissions = deque()
archive_status = {'status':'not_checked','checked_utc':None}


def identifier_valid(identifier):
    return bool(re.fullmatch('[a-f0-9]{32}', identifier))


def maintain():
    store = runtime_store(DATA)
    try:
        store.cleanup()
    except PipelineError:
        pass  # Readers remain available when all eviction candidates are leased.
    with state_lock:
        # Disk remains the source of truth when an inactive memory record is pruned.
        for key in list(jobs):
            if not store._protected(DATA/key) and not (DATA/key).exists():
                jobs.pop(key, None)
        for key in list(jobs):
            if len(jobs) <= 64:break
            if jobs[key]['status'] not in ('queued','running'):
                jobs.pop(key, None)


def persist(identifier, state):
    runtime_store(DATA).write_json(DATA/identifier/'job.json',state)


def process(query, identifier):
    def update(message):
        state = {'status':'running','id':identifier,'message':message,'query':query.model_dump()}
        jobs[identifier] = state
        persist(identifier, state)
    try:
        # Keep the existing one-job policy, but avoid a 90-second discovery
        # lock-out in public mode. Remaining budget is reserved for FITS work.
        jobs[identifier] = run(query,identifier,update,discovery_budget_s=60)
        archive_status.update(status='processing_succeeded',checked_utc=jobs[identifier].get('created_utc'))
    except PipelineError as exc:
        archive_status.update(status=exc.code,checked_utc=datetime.now(timezone.utc).isoformat())
        jobs[identifier] = {'status':'failed','id':identifier,'message':str(exc),'code':exc.code,'retryable':exc.retryable,'query':query.model_dump()}
        if hasattr(exc,'attempt_log'):
            jobs[identifier].update(http_status=getattr(exc,'status',None),
                discovery_attempts=len(exc.attempt_log),discovery_failures=exc.attempt_log,
                discovery_elapsed_seconds=getattr(exc,'elapsed_seconds',None))
    except Exception:
        logging.exception('Processing failed for session %s',identifier)
        jobs[identifier] = {'status':'failed','id':identifier,'message':'This field could not be processed. Try another field or retry; diagnostic details are recorded on the server.','code':'processing_failed','retryable':True,'query':query.model_dump()}
    finally:
        try:
            persist(identifier, jobs[identifier])
        except (OSError, PipelineError):
            logging.exception('Could not persist status for session %s', identifier)
        finally:
            lock.release()

@app.get('/api/health')
def health():
    return {'status':'ok','mode':'full_application','live_search':'available',
            'processing':'busy' if lock.locked() else 'idle',
            'archive':dict(archive_status),'storage_limit_bytes':runtime_store(DATA).limit,
            'session_ttl_seconds':runtime_store(DATA).ttl,
            'notice':'Application health does not establish current IRSA availability.'}

@app.post('/api/sessions',status_code=202)
def create(query: Search):
    try:
        maintain()
    except PipelineError as exc:
        raise HTTPException(503, str(exc))
    with state_lock:
        store = runtime_store(DATA)
        with store.mutex:
            for path in DATA.glob('*/manifest.json'):
                cached = read_example(path)
                if cached and cached.get('processor_version') == PROCESSOR_VERSION and cached.get('query') == query.model_dump():
                    return {'id':path.parent.name,'reused':True,'message':'Reusing a retained exact-query session; no new archive retrieval.'}
        now = time.monotonic()
        while admissions and now-admissions[0] >= 3600:admissions.popleft()
        if len(admissions) >= int(os.getenv('TIMESCOPE_MAX_JOBS_PER_HOUR','12')):
            raise HTTPException(429,'The global hourly search limit is reached. Explore a bundled field or retry later.',headers={'Retry-After':'300'})
        if not lock.acquire(blocking=False):
            raise HTTPException(429,'Another scientific job is active. Existing examples remain available; retry shortly.',headers={'Retry-After':'15'})
        identifier = uuid.uuid4().hex
        jobs[identifier] = {'status':'queued','id':identifier,'message':'Waiting for processing','query':query.model_dump()}
        try:
            persist(identifier, jobs[identifier])
            # Pin before submit so HTTP cleanup cannot evict a queued job.
            lease = store.pin(DATA/identifier)
            lease.__enter__()
            def execute():
                try:process(query,identifier)
                finally:lease.__exit__(None,None,None)
            try:
                executor.submit(execute)
            except Exception:
                lease.__exit__(None,None,None)
                raise
            admissions.append(now)
        except Exception:
            jobs.pop(identifier, None)
            lock.release()
            logging.exception('Could not queue session %s', identifier)
            raise HTTPException(503,'Processing could not start. Please retry shortly.')
    return {'id':identifier,'reused':False}

@app.get('/api/sessions/{identifier}')
def get(identifier: str):
    if not identifier_valid(identifier):
        raise HTTPException(404,'Unknown session')
    maintain()
    if (DATA/identifier).is_symlink():
        raise HTTPException(404,'Unknown session')
    store = runtime_store(DATA)
    with store.mutex, store.pin(DATA/identifier):
        return get_retained(identifier)

def get_retained(identifier):
    if identifier in jobs:
        return jobs[identifier]
    path = DATA/identifier/'manifest.json'
    if path.is_symlink():raise HTTPException(404,'Unknown session')
    if path.exists():
        return json.loads(path.read_text())
    status_path = DATA/identifier/'job.json'
    if status_path.is_symlink():raise HTTPException(404,'Unknown session')
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
    raise HTTPException(404,'This temporary session has expired or is unavailable. Retry the saved coordinates; bundled examples remain available.')

def read_example(path):
    try:
        if path.is_symlink() or path.parent.is_symlink():return None
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
    maintain()
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

@app.get('/artifacts/{identifier}/{name}')
def artifact(identifier: str, name: str):
    if not identifier_valid(identifier) or not (name == 'manifest.json' or re.fullmatch(r'[0-9]{1,2}\.png',name)):
        raise HTTPException(404,'Unknown public artifact')
    store = runtime_store(DATA)
    stack = ExitStack()
    try:
        with store.mutex:
            try:store.cleanup()
            except PipelineError:pass
            folder = DATA/identifier
            path = folder/name
            if folder.is_symlink() or path.is_symlink() or not path.resolve().is_relative_to(DATA.resolve()):
                raise HTTPException(404,'Unknown public artifact')
            stack.enter_context(store.pin(folder))
            handle = stack.enter_context(path.open('rb'))
            length = path.stat().st_size
    except FileNotFoundError:
        stack.close()
        raise HTTPException(404,'Artifact expired or unavailable')
    except Exception:
        stack.close()
        raise
    def chunks():
        try:
            while block := handle.read(65536):yield block
        finally:
            stack.close()
    return StreamingResponse(chunks(),media_type='application/json' if name=='manifest.json' else 'image/png',
        headers={'Content-Length':str(length),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'},
        background=BackgroundTask(stack.close))

if (ROOT/'frontend/dist').exists():
    app.mount('/',StaticFiles(directory=ROOT/'frontend/dist',html=True),name='frontend')
