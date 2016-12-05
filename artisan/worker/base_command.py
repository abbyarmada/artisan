import subprocess
from .base_worker import BaseWorker
from ..compat import Lock

__all__ = [
    "BaseCommand"
]


class BaseCommand(object):
    def __init__(self, worker, command):
        assert isinstance(worker, BaseWorker)
        self._lock = Lock()
        self.worker = worker
        self.command = command

        self._cancelled = False
        self._exit_status = None
        self._stdout = b''
        self._stderr = b''

    def _check_exit(self):
        if self._exit_status is None:
            self._read_all(0.0)

    @property
    def stderr(self):
        self._check_exit()
        return self._stderr

    @property
    def stdout(self):
        self._check_exit()
        return self._stdout

    @property
    def exit_status(self):
        self._check_exit()
        return self._exit_status

    def wait(self, timeout=None):
        while self._exit_status is None:
            self._read_all(timeout)

    def _read_all(self, timeout=0.0):
        raise NotImplementedError()

    def cancel(self):
        raise NotImplementedError()

    @property
    def cancelled(self):
        return self._cancelled

    def _create_subprocess(self):
        return subprocess.Popen(self.command,
                                shell=True,
                                cwd=self.worker.cwd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=self.worker.environ)
