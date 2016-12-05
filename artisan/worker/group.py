import threading
from .base_worker import BaseWorker

__all__ = [
    "WorkerGroup"
]


class WorkerGroup(object):
    def __init__(self):
        self._lock = threading.Lock()
        self._workers = []

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
                if worker.group:
                    raise ValueError("Worker already in another group.")
                worker._group = self
                self._workers.append(worker)

    def remove_worker(self, worker):
        with self._lock:
            if worker not in self._workers:
                raise ValueError("Worker is not in this group.")
            with worker._lock:
                worker._group = None
                self._workers.remove(worker)
