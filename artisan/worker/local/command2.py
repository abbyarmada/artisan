""" Worker implementation for Python 2.6+ where
subprocess.Popen doesn't define timeouts for any
of it's functions. """
import os
import sys
import threading
from ..base_command import BaseCommand
from ...compat import monotonic

try:  # Python 3.x
    from queue import Queue, Empty
except ImportError:  # Python 2.x
    from Queue import Queue, Empty

__all__ = [
    "LocalCommand"
]


class _QueueThread(threading.Thread):
    def __init__(self, stream):
        super(_QueueThread, self).__init__()
        self._stream = stream
        self.queue = Queue()
        self.stop = False

    def run(self):
        try:
            for line in iter(self._stream.readline, b''):
                if self.stop:  # Skip coverage
                    break
                self.queue.put(line)
            self._stream.close()
        except Exception:  # Skip coverage
            pass
        self.stop = True


class LocalCommand(BaseCommand):
    def __init__(self, worker, command, environment=None):
        super(LocalCommand, self).__init__(worker, command)
        if environment is None:
            environment = worker.environ.copy()

        # PATH should be in the environment to be able to find binaries.
        if "PATH" not in environment and "PATH" in os.environ:
            environment["PATH"] = os.environ["PATH"]

        # Windows requires this environment variable to be set before executing.
        if sys.platform == "win32" and "SYSTEMROOT" in os.environ:
            environment["SYSTEMROOT"] = os.environ["SYSTEMROOT"]

        self._proc = self._create_subprocess(environment)
        self._queue_threads = [_QueueThread(self._proc.stdout),
                               _QueueThread(self._proc.stderr)]
        self._queue_stdout = self._queue_threads[0].queue
        self._queue_stderr = self._queue_threads[1].queue
        for thread in self._queue_threads:
            thread.start()

    def _read_all(self, timeout=0.001):
        with self._lock:
            if self._proc is None:
                return self._exit_status, b'', b''
            start_time = monotonic()
            while timeout is None or monotonic() - start_time <= timeout:
                if self._exit_status is None:
                    self._exit_status = self._proc.poll()
                stdout = []
                try:
                    while True:
                        stdout.append(self._queue_stdout.get_nowait())
                except Empty:
                    pass
                stderr = []
                try:
                    while True:
                        stderr.append(self._queue_stderr.get_nowait())
                except Empty:
                    pass
                stdout = b''.join(stdout)
                stderr = b''.join(stderr)
                if stdout:
                    self._stdout += stdout
                if stderr:
                    self._stderr += stderr
                if stdout or stderr or self._exit_status is not None:
                    return self._exit_status, stdout, stderr

            # This line will probably never get reached
            # because subprocess.Popen.poll() actually
            # waits for the process to exit but it's here anyways.
            return self._exit_status, b'', b''  # Skip coverage

    def _is_not_complete(self):
        return (self._exit_status is None or
                self._queue_stdout.qsize() > 0 or
                self._queue_stderr.qsize() > 0 or
                not self._queue_threads[0].stop or
                not self._queue_threads[1].stop)

    def cancel(self):
        with self._lock:
            if self._cancelled:
                raise ValueError("Command is already cancelled.")
            try:
                self._proc.kill()
            except Exception:
                pass
            for thread in self._queue_threads:
                thread.stop = True
            self._queue_threads = None
            self._proc = None
            self._cancelled = True
