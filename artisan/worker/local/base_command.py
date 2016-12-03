import subprocess
from ..abc import BaseCommand

__all__ = [
    "BaseLocalCommand"
]


class BaseLocalCommand(BaseCommand):
    def __init__(self, worker, command):
        super(BaseLocalCommand, self).__init__(worker, command)

        self._stdout = b''
        self._stderr = b''
        self._exit_status = None

    def _create_subprocess(self):
        return subprocess.Popen(self.command,
                                shell=True,
                                cwd=self.worker.cwd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=self.worker.environ)

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

    @property
    def exit_status(self):
        if self._exit_status is None:
            self._read_all(0.0)
        return self._exit_status

    def wait(self, timeout=None):
        while self._exit_status is None:
            self._read_all(timeout)

    def _read_all(self, timeout=0.0):
        raise NotImplementedError()
