import subprocess
from .base_worker import BaseWorker
from ..compat import RLock, monotonic

__all__ = [
    "BaseCommand"
]


class BaseCommand(object):
    def __init__(self, worker, command):
        assert isinstance(worker, BaseWorker)
        self._lock = RLock()
        self.worker = worker
        self.command = command

        self._cancelled = False
        self._exit_status = None
        self._stdout = b''
        self._stderr = b''
        self._callbacks_called = False
        self._callbacks = []

    def _check_exit(self):
        if self._is_not_complete():
            self._read_all(0.0)
            if not self._is_not_complete():
                self._on_complete()

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
        start_time = monotonic()
        read_timeout = timeout
        not_complete = self._is_not_complete()
        while self._is_not_complete():
            self._read_all(read_timeout)
            if timeout is not None:
                current_time = monotonic()
                if current_time - start_time > timeout:
                    break
                read_timeout = max(0.0, (start_time + timeout) - current_time)
        if not_complete:
            self._on_complete()

    def _is_not_complete(self):
        return self._exit_status is None

    def _read_all(self, timeout=0.0):
        raise NotImplementedError()

    def cancel(self):
        raise NotImplementedError()

    @property
    def cancelled(self):
        return self._cancelled

    def _on_complete(self):
        with self._lock:
            if not self._callbacks_called:
                self._callbacks_called = True
                for callback in self._callbacks:
                    callback(self)

    def _create_subprocess(self, environment=None):
        return subprocess.Popen(self.command,
                                shell=True,
                                cwd=self.worker.cwd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=environment)

    def add_callback(self, callback):
        self._callbacks.append(callback)
