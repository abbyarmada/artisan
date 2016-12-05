import paramiko
from .command import SshCommand
from ..base_worker import BaseWorker


class SshWorker(BaseWorker):
    def __init__(self, host, username, *args, **kwargs):
        super(BaseWorker, self).__init__()
        self._ssh = paramiko.SSHClient()
        self._ssh.connect(host, username=username, *args, **kwargs)
        self._sftp = self._ssh.open_sftp()  # type: paramiko.SFTPClient

    def execute(self, command):
        command = SshCommand(self._ssh.invoke_shell(), self, command)
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

    def listdir(self, path):
        with self._lock:
            return self._sftp.listdir(path)
