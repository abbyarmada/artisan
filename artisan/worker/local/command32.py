""" Worker implementation for Python 3.3+ which
has access to timeout in Popen.communicate() """
import subprocess
from ..abc import (
    BaseCommand
)
__all__ = [
    "LocalCommand"
]


class LocalCommand(BaseCommand):
    def __init__(self, worker, command):
        super(LocalCommand, self).__init__(worker, command)
        self._proc = subprocess.Popen(command,
                                      shell=True,
                                      cwd=self.worker.cwd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      env=self.worker.environ)
        self._stdout = b''
        self._stderr = b''
        self._exit_status = None

    def _read_all(self, timeout=0.0):
        with self._lock:
            if self._proc is None:
                return b'', b''
            try:
                self._proc.poll()
                stdout, stderr = self._proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                stdout, stderr = b'', b''
            if self._exit_status is None:
                if self._proc and self._proc.returncode is not None:
                    self._exit_status = self._proc.returncode
            if stdout:
                self._stdout += stdout
            if stderr:
                self._stderr += stderr
            return self._exit_status, stdout, stderr

    def wait(self, timeout=None):
        while self._exit_status is None:
            self._read_all(timeout)

    @property
    def exit_status(self):
        if self._exit_status is None:
            self._read_all(0.0)
        return self._exit_status

    def cancel(self):
        with self._lock:
            if self._cancelled:
                raise ValueError("Command is already cancelled.")
            self._proc.kill()
            self._proc = None
            self._cancelled = True

    @property
    def stderr(self):
        if self._exit_status is None:
            self._read_all(0.0)
        return self._stderr

    @property
    def stdout(self):
        if self._exit_status is None:
            self._read_all(0.0)
        return self._stdout
