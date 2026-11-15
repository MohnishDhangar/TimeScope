from fastapi.testclient import TestClient
from backend.app import app
client = TestClient(app)

def test_health():
    assert client.get('/api/health').json()['status']=='ok'

def test_invalid_search_never_starts_job():
    assert client.post('/api/sessions',json={'ra':0,'dec':91}).status_code==422

def test_unknown_session():
    assert client.get('/api/sessions/not-a-session').status_code==404

def test_public_error_hides_internal_exception(monkeypatch, tmp_path):
    from backend import app as module
    from backend.pipeline import Search
    monkeypatch.setattr(module, 'DATA', tmp_path)
    def fail(*args):raise RuntimeError('HTTPSConnectionPool private internal details')
    monkeypatch.setattr(module,'run',fail)
    assert module.lock.acquire(blocking=False)
    module.process(Search(ra=10,dec=20),'e'*32)
    result=client.get('/api/sessions/'+'e'*32).json()
    assert result['status']=='failed' and result['retryable']
    assert 'HTTPSConnectionPool' not in result['message']
    assert not module.lock.locked()


def test_interrupted_job_recovers_query_and_retry_after_restart(monkeypatch, tmp_path):
    from backend import app as module
    monkeypatch.setattr(module, 'DATA', tmp_path)
    identifier = 'a'*32
    query = {'ra':42, 'dec':-30, 'fov':8, 'frames':6}
    module.persist(identifier, {'id':identifier,'status':'running','query':query,'message':'Downloading'})
    # Simulate a fresh process: the job is on disk, not in the in-memory jobs map.
    monkeypatch.setattr(module, 'jobs', {})
    result = client.get('/api/sessions/'+identifier).json()
    assert result['status'] == 'failed'
    assert result['code'] == 'interrupted' and result['retryable']
    assert result['query'] == query
    assert client.get('/api/sessions/'+identifier).json() == result


def test_ready_manifest_takes_precedence_over_stale_running_status(monkeypatch, tmp_path):
    import json
    from backend import app as module
    monkeypatch.setattr(module, 'DATA', tmp_path)
    monkeypatch.setattr(module, 'jobs', {})
    identifier = 'b'*32
    module.persist(identifier, {'status':'running'})
    manifest = {'id':identifier,'status':'ready','frames':[]}
    (tmp_path/identifier/'manifest.json').write_text(json.dumps(manifest))
    assert client.get('/api/sessions/'+identifier).json() == manifest


def test_examples_exclude_missing_previews_and_broken_manifests(monkeypatch, tmp_path):
    import json
    from backend import app as module
    monkeypatch.setattr(module, 'DATA', tmp_path)
    monkeypatch.setattr(module, 'SHOWCASE', tmp_path/'no-bundle')
    for identifier in ['a'*32,'b'*32]:
        folder = tmp_path/identifier
        folder.mkdir()
        manifest = {'status':'ready','query':{'ra':10,'dec':20,'fov':5},
                    'frames':[{'image':'/artifacts/'+identifier+'/0.png'}, {'image':'/artifacts/'+identifier+'/1.png'}]}
        (folder/'manifest.json').write_text(json.dumps(manifest))
    for name in ['0.png','1.png']:(tmp_path/('a'*32)/name).write_bytes(b'preview fixture')
    broken = tmp_path/('c'*32)
    broken.mkdir()
    (broken/'manifest.json').write_text('{')
    results = client.get('/api/examples').json()
    assert len(results) == 1 and results[0]['id'] == 'a'*32
    assert results[0]['frames'] == 2


def test_queue_persistence_failure_releases_capacity(monkeypatch, tmp_path):
    from backend import app as module
    monkeypatch.setattr(module, 'DATA', tmp_path)
    def fail(*args):raise OSError('disk full')
    monkeypatch.setattr(module, 'persist', fail)
    response = client.post('/api/sessions',json={'ra':42,'dec':-30})
    assert response.status_code == 503
    assert not module.lock.locked()


def test_fresh_backend_serves_real_bundled_example(monkeypatch, tmp_path):
    from backend import app as module
    monkeypatch.setattr(module, 'DATA', tmp_path/'empty')
    monkeypatch.setattr(module, 'jobs', {})
    entries = client.get('/api/examples').json()
    assert entries and all(item['bundled'] for item in entries)
    identifier = entries[0]['id']
    result = client.get('/api/sessions/'+identifier)
    assert result.status_code == 200
    manifest = result.json()
    assert manifest['cached_showcase'] and len(manifest['frames']) >= 2
    for frame in manifest['frames']:
        assert client.get(frame['image']).status_code == 200
    assert client.get('/api/health').json()['live_search'] == 'available'


def test_bundle_never_substitutes_unknown_session(monkeypatch, tmp_path):
    from backend import app as module
    monkeypatch.setattr(module, 'DATA', tmp_path)
    monkeypatch.setattr(module, 'jobs', {})
    assert client.get('/api/sessions/'+'f'*32).status_code == 404


def test_local_example_deduplicates_bundled_identity(monkeypatch, tmp_path):
    import json
    from backend import app as module
    monkeypatch.setattr(module, 'DATA', tmp_path)
    entry = client.get('/api/examples').json()[0]
    manifest = json.loads((module.SHOWCASE/entry['id']/'manifest.json').read_text())
    folder = tmp_path/entry['id']
    folder.mkdir()
    for frame in manifest['frames']:
        (folder/frame['image'].rsplit('/',1)[-1]).write_bytes(b'test preview')
    (folder/'manifest.json').write_text(json.dumps(manifest))
    entries = client.get('/api/examples').json()
    matches = [item for item in entries if item['id'] == entry['id']]
    assert len(matches) == 1 and not matches[0]['bundled']
