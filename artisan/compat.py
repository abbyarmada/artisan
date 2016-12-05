import sys
__all__ = [
    "monotonic",
    "Lock",
    "Semaphore",
    "RLock",
    "cmp_to_key"
]

try:
    from time import monotonic
except ImportError:
    try:
        from monotonic import monotonic
    except RuntimeError:
        from time import time as monotonic

if sys.version_info >= (3, 0, 0):
    from threading import Lock, Semaphore, RLock
else:
    import threading

    class _BaseLock(object):
        """ Lock that implements the Python 3.x functionality
        of having the timeout parameter available for acquire. """
        def __init__(self, lock):
            self._lock = lock

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


    class Lock(_BaseLock):
        def __init__(self):
            super(Lock, self).__init__(threading.Lock())


    class RLock(_BaseLock):
        def __init__(self):
            super(RLock, self).__init__(threading.RLock())


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

try:
    from functools import cmp_to_key
except ImportError:
    def cmp_to_key(cmp):
        class K(object):
            __slots__ = ['obj']

            def __init__(self, obj, *_):
                self.obj = obj

            def __lt__(self, other):
                return cmp(self.obj, other.obj) < 0

            def __gt__(self, other):
                return cmp(self.obj, other.obj) > 0

            def __eq__(self, other):
                return cmp(self.obj, other.obj) == 0

            def __le__(self, other):
                return cmp(self.obj, other.obj) <= 0

            def __ge__(self, other):
                return cmp(self.obj, other.obj) >= 0

            def __ne__(self, other):
                return cmp(self.obj, other.obj) != 0

            def __hash__(self):
                raise TypeError('hash not implemented')

        return K
