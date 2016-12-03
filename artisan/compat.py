import sys
__all__ = [
    "monotonic",
    "Lock",
    "Semaphore"
]

try:
    from time import monotonic
except ImportError:
    try:
        from monotonic import monotonic
    except RuntimeError:
        from time import time as monotonic

if sys.version_info >= (3, 0, 0):
    from threading import Lock, Semaphore
else:
    import threading

    class Lock(object):
        """ Lock that implements the Python 3.x functionality
        of having the timeout parameter available for acquire. """
        def __init__(self):
            self._lock = threading.Lock()

        def acquire(self, blocking=True, timeout=None):
            if blocking:
                if timeout is None:
                    return self._lock.acquire(blocking=True)
                else:
                    start_time = monotonic()
                    while True:
                        if self._lock.acquire(blocking=False):
                            return True
                        if monotonic() - start_time > timeout:
                            return False
            else:
                return self._lock.acquire(blocking=False)

        def release(self):
            self._lock.release()

        def __enter__(self):
            self._lock.acquire()
            return self

        def __exit__(self, *_):
            self._lock.release()

    class Semaphore(object):
        """ Semaphore that implements the Python 3.x functionality
        of having the timeout parameter available for acquire. """
        def __init__(self, value):
            self._semaphore = threading.Semaphore(value)

        def acquire(self, blocking=True, timeout=None):
            if blocking:
                if timeout is None:
                    return self._semaphore.acquire(blocking=True)
                else:
                    start_time = monotonic()
                    while True:
                        if self._semaphore.acquire(blocking=False):
                            return True
                        if monotonic() - start_time > timeout:
                            return False
            else:
                return self._semaphore.acquire(blocking=False)

        def release(self):
            self._semaphore.release()
