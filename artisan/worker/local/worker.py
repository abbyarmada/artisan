import os
import sys
from ..abc import (
    BaseWorker
)
from ..getuser import getuser

# Use LocalCommand implementation based on Python version.
if sys.version_info >= (3, 3):
    from .command32 import LocalCommand
else:
    from .command2 import LocalCommand


class LocalWorker(BaseWorker):
    def __init__(self):
        super(LocalWorker, self).__init__(getuser(), "localhost")
        self._cwd = os.getcwd()
        self.environ = os.environ.copy()

    def chdir(self, path):
        with self._lock:
            if os.path.isabs(path):
                self._cwd = os.path.normpath(os.path.expanduser(path))
            else:
                self._cwd = os.path.normpath(os.path.expanduser(os.path.join(self._cwd, path)))

    @property
    def cwd(self):
        return self._cwd

    def listdir(self):
        return os.listdir(self._cwd)

    def execute(self, command):
        return LocalCommand(self, command)
