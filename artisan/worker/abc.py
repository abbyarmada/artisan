""" Abstract base class for the Worker interface. """
import re
import sys
import subprocess
from ..compat import Lock

_PYTHON_BINARIES = ["python",
                    "python2",
                    "python3",
                    "python3.3",
                    "python3.4",
                    "python3.5"]
_PYTHON_REGEX = re.compile(b'^([^(\\s]+)[^\d(]*\\((\\d+), (\\d+), (\\d+),.*$')
__all__ = [
    "BaseCommand",
    "BaseWorker"
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

    @property
    def python_executable(self):
        with self._lock:
            if self._python_executable is None:
                sys.version_info

    def _find_python_executables(self):
        """ Finds all Python installations on the
        Worker that can be accessed from the basic
        PATH configuration that exists on the Worker. """
        pythons = {}
        commands = []
        with self._lock:
            for binary in _PYTHON_BINARIES:
                commands.append(self.execute(("%s -c \"import sys; print(sys.executable,"
                                              " tuple(sys.version_info))\"" % binary)))
            for command in commands:
                assert isinstance(command, BaseCommand)
                command.wait()
                if command.exit_status == 0:
                    match = _PYTHON_REGEX.match(command.stdout)
                    if match:
                        path, major, minor, micro = match.groups()
                        if isinstance(path, bytes):
                            path = path.decode("utf-8")
                        pythons[(int(major), int(minor), int(micro))] = path

        return pythons
