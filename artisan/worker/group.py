import threading
from .base_worker import BaseWorker

__all__ = [
    "WorkerGroup"
]


class _WorkerGroupBarrier(object):
    def __init__(self, parties):
        self._count = 0
        self._parties = parties
        self._lock = threading.Lock()
        self._full = threading.Condition()

    def wait(self):
        self._full.acquire()
        full = False
        with self._lock:
            self._count += 1
            if self._count == self._parties:
                full = True
        if full:
            self._full.notify_all()
            self._count = 0
        else:
            self._full.wait()
        self._full.release()


class WorkerGroup(object):
    def __init__(self):
        self._lock = threading.Lock()
        self._workers = []
        self._locks = {}
        self._barriers = {}

    @property
    def workers(self):
        return self._workers[:]

    def add_worker(self, worker):
        if not isinstance(worker, BaseWorker):
            raise ValueError("Non-worker added to WorkerGroup.")
        with self._lock:
            if worker in self._workers:
                raise ValueError("Worker already in this group.")
            with worker._lock:
                self._workers.append(worker)

    def remove_worker(self, worker):
        with self._lock:
            if worker not in self._workers:
                raise ValueError("Worker is not in this group.")
            with worker._lock:
                self._workers.remove(worker)

    def create_lock(self, name):
        with self._lock:
            if name in self._locks:
                raise ValueError("Lock with the name `%s` already in WorkerGroup." % name)
            self._locks[name] = threading.Lock()

    def acquire_lock(self, name):
        self._locks[name].acquire()
        return self._locks[name]

    def release_lock(self, name):
        self._locks[name].release()

    def create_barrier(self, name):
        with self._lock:
            if name in self._barriers:
                raise ValueError("Barrier with the name `%s` already in WorkerGroup." % name)
            self._barriers[name] = _WorkerGroupBarrier(len(self._workers))

    def wait_barrier(self, name):
        self._barriers[name].wait()
