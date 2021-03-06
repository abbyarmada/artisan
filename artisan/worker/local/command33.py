""" Worker implementation for Python 3.3+ which
has access to timeout in Popen.communicate() """
import os
import sys
import subprocess
from ..base_command import BaseCommand
__all__ = [
    "LocalCommand"
]


class LocalCommand(BaseCommand):
    def __init__(self, worker, command, environment=None):
        super(LocalCommand, self).__init__(worker, command)
        if environment is None:
            environment = worker.environ.copy()

        # PATH should be in the environment to be able to find binaries.
        if "PATH" not in environment and "PATH" in os.environ:
            environment["PATH"] = os.environ["PATH"]

        # Windows requires this environment variable to be set before executing.
        if sys.platform == "win32" and "SYSTEMROOT" in os.environ:
            environment["SYSTEMROOT"] = os.environ["SYSTEMROOT"]

        self._proc = self._create_subprocess(environment)

    def _read_all(self, timeout=0.0):
        with self._lock:
            if self._proc is None:
                return self._exit_status, b'', b''
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

    def cancel(self):
        with self._lock:
            if self._cancelled:
                raise ValueError("Command is already cancelled.")
            self._proc.kill()
            self._proc = None
            self._cancelled = True
