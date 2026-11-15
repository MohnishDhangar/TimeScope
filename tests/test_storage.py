"""Storage controls use synthetic byte fixtures, never archive traffic."""
import os
import time
import pytest
from backend.storage import RuntimeStore
from backend.errors import PipelineError


def put(path,size,age=0):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b'x'*size)
    os.utime(path,(time.time()-age,time.time()-age))
    os.utime(path.parent,(time.time()-age,time.time()-age))


def test_aggregate_counts_duplicate_fits_parts_and_internal_arrays(tmp_path):
    store=RuntimeStore(tmp_path,limit=100,ttl=3600)
    put(tmp_path/'cutout-cache/a.fits',30,age=20)
    put(tmp_path/'session/0.fits',30,age=10)
    put(tmp_path/'session/1.part',10,age=10)
    put(tmp_path/'session/aligned.npz',20,age=10)
    assert store.size()==90
    with store.pin(tmp_path/'session'),store.reserve(30):
        assert not (tmp_path/'cutout-cache/a.fits').exists()
        assert (tmp_path/'session/aligned.npz').exists()
        assert store.size()+store.reserved<=100


def test_active_job_and_active_response_lease_prevent_eviction(tmp_path):
    store=RuntimeStore(tmp_path,limit=100,ttl=1)
    put(tmp_path/'active/0.png',60,age=20)
    put(tmp_path/'response/0.png',30,age=20)
    with store.pin(tmp_path/'active'),store.pin(tmp_path/'response'):
        with pytest.raises(PipelineError,match='storage is full'):
            with store.reserve(20):pass
        assert store.size()==90
    store.cleanup()
    assert store.size()==0


def test_oldest_inactive_session_evicted_first(tmp_path):
    store=RuntimeStore(tmp_path,limit=100,ttl=10000)
    put(tmp_path/'older/0.png',40,age=20)
    put(tmp_path/'newer/0.png',40,age=10)
    with store.reserve(30):
        assert not (tmp_path/'older').exists()
        assert (tmp_path/'newer').exists()


def test_cleanup_expires_failed_sessions_and_abandoned_parts(tmp_path):
    store=RuntimeStore(tmp_path,limit=100,ttl=10)
    put(tmp_path/'failed/job.json',10,age=20)
    put(tmp_path/'abandoned/0.part',10,age=20)
    store.cleanup()
    assert store.size()==0


def test_reservation_released_after_error_and_atomic_json(tmp_path):
    store=RuntimeStore(tmp_path,limit=1000,ttl=100)
    with pytest.raises(RuntimeError):
        with store.reserve(300):raise RuntimeError('test writer error')
    assert store.reserved==0
    store.write_json(tmp_path/'session/job.json',{'status':'failed'})
    assert not list(tmp_path.rglob('*.tmp'))
    assert 'failed' in (tmp_path/'session/job.json').read_text()


def test_outside_symlink_never_counted_or_traversed(tmp_path):
    root=tmp_path/'runtime';root.mkdir()
    external=tmp_path/'external';external.mkdir()
    put(external/'secret',50)
    (root/'escaped').symlink_to(external,target_is_directory=True)
    store=RuntimeStore(root,limit=100,ttl=1)
    assert store.size()==0
    os.utime(root/'escaped',(time.time()-20,time.time()-20),follow_symlinks=False)
    store.cleanup()
    assert (external/'secret').exists()
