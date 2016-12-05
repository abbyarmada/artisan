from ..compat import Lock

__all__ = [
    "BaseWorker"
]


class BaseWorker(object):
    def __init__(self, user, host):
        self._lock = Lock()
        self.user = user
        self.host = host
        self.environ = {}

        self._pool = None
        self._group = None
        self._commands = []
        self._closed = False
        self._python_executable = None

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
    def group(self):
        return self._group

    @property
    def cwd(self):
        raise NotImplementedError()

    def chdir(self, path):
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
