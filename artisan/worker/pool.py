from .compat import Semaphore, Lock
__all__ = [
    "WorkerPool"
]


class WorkerPool(object):
    def __init__(self, max_workers, worker_factory, *args, **kwargs):
        self._lock = Lock()
        self._semaphore = Semaphore(max_workers)
        self._pool = []
        self._max_workers = max_workers
        self._worker_factory = worker_factory
        self._args = args
        self._kwargs = kwargs
        self._setup_steps = []
        self._cleanup_steps = []

    @property
    def max_workers(self):
        return self._max_workers

    @property
    def workers_free(self):
        """ Gets the number of workers that
        are free in the pool. """
        with self._lock:
            return self._max_workers - len(self._pool)

    @property
    def workers_used(self):
        """ Get the number of workers that are
        currently being used in the pool. """
        with self._lock:
            return len(self._pool)

    def _create_new_worker(self):
        """ Creates a new worker from the
        factory method. """
        with self._lock:
            worker = self._worker_factory(*self._args, **self._kwargs)
            self._pool.append(worker)
            return worker

    def acquire(self, timeout=None):
        """ Acquires a worker from the pool. """
        success = self._semaphore.acquire(timeout=timeout)
        if not success:
            return None
        worker = self._create_new_worker()
        worker._pool = self
        with self._lock:
            for setup_step in self._setup_steps:
                setup_step(worker)
        return worker

    def release(self, worker):
        """ Releases a worker back into the pool. """
        with self._lock:
            for i, other_worker in enumerate(self._pool):
                if other_worker is worker:
                    del self._pool[i]
                    break
            else:
                raise ValueError("Worker is not from this pool.")
            for cleanup_step in self._cleanup_steps:
                cleanup_step(worker)
            try:
                worker.close()
            except Exception:
                pass
        self._semaphore.release()

    def add_worker_setup_step(self, func):
        """ Adds a step that is taken whenever a worker
        is acquired from the pool. The only parameter
        for the function is the reserved worker. """
        with self._lock:
            self._setup_steps.append(func)

    def add_worker_cleanup_step(self, func):
        """ Adds a step that is taken whenever a worker
        is released into the pool. The only parameter
        for the function is the released worker. """
        with self._lock:
            self._cleanup_steps.append(func)
