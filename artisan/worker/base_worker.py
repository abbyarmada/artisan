""" Interface for the Worker class that must
be implemented by all Worker implementations. """
import re
from collections import namedtuple
from ..compat import RLock
from ..util import convert_to_string
__all__ = [
    "BaseWorker",
    "FileAttributes"
]
_VERSION_INFO_REGEX = re.compile(b'^\((\d+), (\d+), (\d+).*$')


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
        self._lock = RLock()
        self.user = user
        self.host = host
        self.environ = {}

        self._dist_info = None
        self._tempdir = None
        self._python_version = None
        self._python_executable = None
        self._virtualenv_path = None
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

    def isdir(self, path):
        raise NotImplementedError()

    def open(self, path, mode="r"):
        raise NotImplementedError()

    @property
    def tempdir(self):
        if self._tempdir is None:
            with self._lock:
                if self._tempdir is None:
                    code = "import sys, tempfile; sys.stdout.write(tempfile.gettempdir())"
                    command = self.execute_python(code)
                    command.wait(1.0)
                    self._tempdir = convert_to_string(command.stdout)
        return self._tempdir

    def execute_python(self, code):
        return self.execute("%s -c \"%s\"" % (self.python_executable, code.replace("\n", "\\n")))

    @property
    def python_version(self):
        if self._python_version is None:
            with self._lock:
                if self._python_version is None:
                    version_code = "import sys; print(tuple(sys.version_info))"
                    command = self.execute_python(version_code)
                    command.wait(1.0)
                    match = _VERSION_INFO_REGEX.match(command.stdout)
                    if match:
                        self._python_version = tuple(int(x) for x in match.groups())
        return self._python_version

    @property
    def python_executable(self):
        if self._python_executable is None:
            with self._lock:
                self._find_python_executable()
        return self._python_executable

    def _find_python_executable(self):
        if self._python_executable is not None:
            return
        commands = []
        base_command = "%s -c \"import sys; sys.stdout.write(sys.executable)\""
        for python_name in ["python3",
                            "python",
                            "python2"]:
            command = self.execute(base_command % python_name)
            commands.append(command)
        for command in commands:
            command.wait(1.0)
            if command.exit_status == 0:
                python_executable = convert_to_string(command.stdout.strip())
                self._python_executable = python_executable
                break

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
