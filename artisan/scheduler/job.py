import threading
__all__ = [
    "Job"
]


class Job(object):
    def __init__(self):
        self._status = "ACTIVE"
        self._lock = threading.Lock()

    @property
    def status(self):
        with self._lock:
            return self._status
