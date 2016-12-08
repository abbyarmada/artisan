import re
import paramiko
from .command import SshCommand
from ..base_worker import BaseWorker

_SSH_ENVIRONMENT_VARIABLES = set([b'SSH_CLIENT', b'SSH_CONNECTION', b'_'])
_ENVIRONMENT_REGEX = re.compile(b'^([^=]+)=(.*)$')


class SshWorker(BaseWorker):
    def __init__(self, host, username, *args, **kwargs):
        super(SshWorker, self).__init__(host, username)
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(host, username=username, *args, **kwargs)
        self._sftp = self._ssh.open_sftp()  # type: paramiko.SFTPClient

        self.environ = self._get_environment()

    def execute(self, command):
        command = SshCommand(self._ssh, self, command)
        self._commands.append(command)
        return command

    def close(self):
        super(SshWorker, self).close()
        with self._lock:
            self._sftp.close()
            self._sftp = None
            self._ssh.close()
            self._ssh = None

    @property
    def cwd(self):
        return self._sftp.getcwd()

    def chdir(self, path):
        with self._lock:
            self._sftp.chdir(path)

    def listdir(self, path="."):
        with self._lock:
            return self._sftp.listdir(path)

    def _get_environment(self):
        """ Gets the current environment variables
        present on the remote machine and returns them
        as a dictionary to be used for worker.environ """
        command = self.execute(("python -c \"import os, sys; sys.stdout.write("
                                "'\\n'.join(['%s=%s' % (k, v) for k, v in "
                                "os.environ.items()]))\""))
        command.wait(0.1)
        if command.exit_status != 0:
            print(command.exit_status, command.stdout, command.stderr)
            return {}

        environ = {}
        for line in command.stdout.split(b'\n'):
            match = _ENVIRONMENT_REGEX.match(line.strip())
            if match:
                key, val = match.groups()
                if key in _SSH_ENVIRONMENT_VARIABLES:
                    continue
                if isinstance(key, bytes):
                    key = key.decode("utf-8")
                    val = val.decode("utf-8")
                environ[key] = val

        return environ
