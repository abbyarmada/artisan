import os
import sys
import shutil
from ..base_worker import BaseWorker
from ..getuser import getuser

# Use LocalCommand implementation based on Python version.
if sys.version_info >= (3, 3):
    from .command33 import LocalCommand
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

    def get_file(self, remote_path, local_path):
        shutil.move(remote_path, local_path)

    def put_file(self, local_path, remote_path):
        shutil.move(local_path, remote_path)

    def open(self, path, mode="r"):
        return open(path, mode)

    def execute(self, command):
        command = LocalCommand(self, command)
        self._commands.append(command)
        return command
