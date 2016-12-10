""" Implementation for a Worker that runs on the
local machine rather than remotely. """
import os
import sys
import shutil
from ..base_worker import BaseWorker, FileAttributes
from ..getuser import getuser

# Use LocalCommand implementation based on Python version.
if sys.version_info >= (3, 3):
    from .command33 import LocalCommand
else:
    from .command2 import LocalCommand

__all__ = [
    "LocalCommand",
    "LocalWorker"
]


class LocalWorker(BaseWorker):
    def __init__(self):
        super(LocalWorker, self).__init__(getuser(), "localhost")
        self._cwd = os.getcwd()
        self.environ = os.environ.copy()

    def _normalize_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(os.path.expanduser(path))
        else:
            return os.path.normpath(os.path.expanduser(os.path.join(self._cwd, path)))

    def chdir(self, path):
        with self._lock:
            self._cwd = self._normalize_path(path)

    @property
    def cwd(self):
        return self._cwd

    def listdir(self, path="."):
        return os.listdir(self._normalize_path(path))

    def get_file(self, remote_path, local_path):
        shutil.move(self._normalize_path(remote_path),
                    self._normalize_path(local_path))

    def put_file(self, local_path, remote_path):
        shutil.move(self._normalize_path(local_path),
                    self._normalize_path(remote_path))

    def stat(self, path, follow_symlinks=True):
        if follow_symlinks:
            stat = os.stat(self._normalize_path(path))
        else:
            stat = os.lstat(self._normalize_path(path))
        return FileAttributes(st_mode=stat.st_mode,
                              st_size=stat.st_size,
                              st_uid=stat.st_uid,
                              st_gid=stat.st_gid,
                              st_ino=stat.st_ino,
                              st_atime=stat.st_atime,
                              st_ctime=stat.st_ctime,
                              st_mtime=stat.st_mtime,
                              st_dev=stat.st_dev,
                              st_nlink=stat.st_nlink)

    def open(self, path, mode="r"):
        return open(self._normalize_path(path), mode)

    def execute(self, command):
        command = LocalCommand(self, command)
        self._commands.append(command)
        return command
