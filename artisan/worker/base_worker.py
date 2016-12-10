""" Interface for the Worker class that must
be implemented by all Worker implementations. """
from collections import namedtuple
from ..compat import Lock

__all__ = [
    "BaseWorker",
    "FileAttributes"
]


FileAttributes = namedtuple("FileAttributes", ["st_mode",
                                               "st_ino",
                                               "st_dev",
                                               "st_nlink",
                                               "st_uid",
                                               "st_gid",
                                               "st_size",
                                               "st_atime",
                                               "st_mtime",
                                               "st_ctime"])


class BaseWorker(object):
    def __init__(self, user, host):
        self._lock = Lock()
        self.user = user
        self.host = host
        self.environ = {}

        self._pool = None
        self._commands = []
        self._closed = False

    def __str__(self):
        return "<Worker user=%s host=%s>" % (self.user, self.host)

    def __repr__(self):
        return str(self)

    def execute(self, command):
        raise NotImplementedError()

    @property
    def pool(self):
        return self._pool

    @property
    def cwd(self):
        raise NotImplementedError()

    def chdir(self, path):
        raise NotImplementedError()

    def listdir(self, path="."):
        raise NotImplementedError()

    def get_file(self, remote_path, local_path):
        raise NotImplementedError()

    def put_file(self, local_path, remote_path):
        raise NotImplementedError()

    def stat(self, path, follow_symlinks=True):
        raise NotImplementedError()

    def open(self, path, mode="r"):
        raise NotImplementedError()

    @property
    def closed(self):
        return self._closed

    def close(self):
        with self._lock:
            if self._closed:
                raise ValueError("Worker is already closed.")
            self._closed = True
            for command in self._commands:
                try:
                    command.cancel()
                except ValueError:
                    pass
