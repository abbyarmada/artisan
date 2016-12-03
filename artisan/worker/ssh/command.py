import paramiko
from ..abc import BaseCommand
from ...compat import monotonic

__all__ = [
    "SshCommand"
]


class SshCommand(BaseCommand):
    def __init__(self, channel, worker, command):
        assert isinstance(channel, paramiko.Channel)
        super(SshCommand, self).__init__(worker, command)
        self._channel = channel

    def _read_all(self, timeout=0.0):
        with self._lock:
            if self._channel is None:
                return self._exit_status, b'', b''
            if timeout is None:
                self._channel.setblocking(True)
            else:
                self._channel.setblocking(False)
            start_time = monotonic()
            while timeout is None or monotonic() - start_time < timeout:
                if self._channel.recv_ready():
                    self._stdout = self._channel.recv(8192)
                if self._channel.recv_stderr_ready():
                    self._stderr = self._channel.recv_stderr(8192)
                if self._channel.exit_status_ready():
                    self._exit_status = self._channel.recv_exit_status()
                    break

    def wait(self, timeout=None):
        while self._exit_status is None:
            self._read_all(timeout)

    def cancel(self):
        with self._lock:
            if self._cancelled:
                raise ValueError("Command is already cancelled.")
            self._channel.close()
            self._channel = None
            self._cancelled = True
