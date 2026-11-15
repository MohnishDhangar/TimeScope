"""Bounded ephemeral runtime files, with process-local writer/read leases.

One application process is required. Reservations are conservative: reserved
bytes and existing files are counted together until the write completes.
"""
from contextlib import contextmanager
from collections import Counter
from pathlib import Path
from threading import RLock
import json
import os
import shutil
import time
from .errors import PipelineError


class RuntimeStore:
    def __init__(self, root, limit=None, ttl=None):
        self.root = Path(root).resolve()
        self.limit = limit if limit is not None else int(os.getenv('TIMESCOPE_MAX_CACHE_MB', '512')) * 1024**2
        self.ttl = ttl if ttl is not None else int(os.getenv('TIMESCOPE_SESSION_TTL_SECONDS', '21600'))
        if self.limit <= 0 or self.ttl <= 0:
            raise ValueError('Runtime storage limit and TTL must be positive')
        self.mutex = RLock()
        self.pins = Counter()
        self.reserved = 0
        self.evicted = 0
        self.root.mkdir(parents=True, exist_ok=True)

    def size(self):
        return sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file() and not p.is_symlink())

    def _protected(self, path):
        return any(count and (path == p or path in p.parents or p in path.parents) for p,count in self.pins.items())

    def _remove(self, path):
        if path.is_symlink():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)
        self.evicted += 1

    def cleanup(self, required=0):
        with self.mutex:
            now = time.time()
            candidates = []
            for path in self.root.iterdir():
                if path.name == 'cutout-cache' and path.is_dir() and not path.is_symlink():
                    candidates.extend(path.iterdir())
                else:
                    candidates.append(path)
            candidates.sort(key=lambda p:p.lstat().st_mtime)
            for path in list(candidates):
                if not self._protected(path) and now-path.lstat().st_mtime > self.ttl:
                    self._remove(path)
                    candidates.remove(path)
            usage = self.size()
            for path in candidates:
                if usage+self.reserved+required <= self.limit:
                    break
                if not self._protected(path):
                    self._remove(path)
                    usage = self.size()
            if usage+self.reserved+required > self.limit:
                raise PipelineError('Temporary storage is full while data is in use. Retry after the active job finishes.', 'capacity_exhausted', True)
            return usage

    @contextmanager
    def pin(self, path):
        path = Path(path).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError('Lease outside runtime storage')
        with self.mutex:
            self.pins[path] += 1
        try:
            yield
        finally:
            with self.mutex:
                self.pins[path] -= 1
                if not self.pins[path]:del self.pins[path]

    @contextmanager
    def reserve(self, size):
        with self.mutex:
            self.cleanup(size)
            self.reserved += size
        try:
            yield
        finally:
            with self.mutex:self.reserved -= size

    def write_json(self, path, data):
        encoded = json.dumps(data, indent=2, allow_nan=False).encode()
        path = Path(path)
        with self.pin(path.parent), self.reserve(len(encoded)):
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix+'.tmp')
            try:
                temporary.write_bytes(encoded)
                temporary.replace(path)
            finally:
                temporary.unlink(missing_ok=True)


_stores = {}
_stores_lock = RLock()

def runtime_store(root):
    key = str(Path(root).resolve())
    with _stores_lock:
        if key not in _stores:_stores[key] = RuntimeStore(root)
        return _stores[key]
