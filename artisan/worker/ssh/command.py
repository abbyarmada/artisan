import paramiko
from ..base_command import BaseCommand
from ...compat import monotonic

__all__ = [
    "SshCommand"
]


class SshCommand(BaseCommand):
    def __init__(self, client, worker, command):
        assert isinstance(client, paramiko.SSHClient)
        super(SshCommand, self).__init__(worker, command)
        command = " ".join(["export %s=%s;" % (key, val) for
                            key, val in worker.environ.items()] + [command])
        _, stdout_file, _ = client.exec_command(command)
        self._channel = stdout_file.channel

    def _read_all(self, timeout=0.0):
        with self._lock:
            if self._channel is None:
                return self._exit_status, b'', b''
            if timeout is None:
                self._channel.setblocking(True)
            else:
                self._channel.setblocking(False)
            start_time = monotonic()
            stdout = []
            stderr = []
            try:
                while True:
                    if self._channel.recv_ready():
                        stdout.append(self._channel.recv(8192))
                    if self._channel.recv_stderr_ready():
                        stderr.append(self._channel.recv_stderr(8192))
                    if self._channel.exit_status_ready():
                        self._exit_status = self._channel.recv_exit_status()
                        break
                    if timeout is None or monotonic() - start_time > timeout:
                        break
            except paramiko.SSHException:
                pass

            # One last attempt to read from the channel.
            try:
                if self._channel.recv_ready():
                    stdout.append(self._channel.recv(8192))
                if self._channel.recv_stderr_ready():
                    stderr.append(self._channel.recv_stderr(8192))
            except paramiko.SSHException:
                pass

            stdout = b''.join(stdout)
            stderr = b''.join(stderr)

            self._stdout += stdout
            self._stderr += stderr

            return self._exit_status, stdout, stderr

    def cancel(self):
        with self._lock:
            if self._cancelled:
                raise ValueError("Command is already cancelled.")
            self._channel.close()
            self._channel = None
            self._cancelled = True
