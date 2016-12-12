import enum
import threading
__all__ = [
    "Job",
    "JobStatus"
]


class JobStatus(enum.Enum):
    SCHEDULED = "Scheduled"
    ACTIVE = "Active"
    SUCCESS = "Success"
    UNSTABLE = "Unstable"
    FAILURE = "Failure"


class Job(object):
    def __init__(self):
        self._status = JobStatus.SCHEDULED
        self._lock = threading.Lock()

    @property
    def status(self):
        with self._lock:
            return self._status
