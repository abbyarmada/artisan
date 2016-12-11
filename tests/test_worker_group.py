import random
import sys
import time
import threading
from artisan.worker import LocalWorker, WorkerGroup

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest
try:
    from time import monotonic
except ImportError:
    from time import time as monotonic


class WorkerThread(threading.Thread):
    def __init__(self, worker, func, *args, **kwargs):
        super(WorkerThread, self).__init__()
        self._worker = worker
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._func(self._worker, *self._args, **self._kwargs)


def _safe_close(worker):
    try:
        worker.close()
    except Exception:
        pass


class TestWorkerGroup(unittest.TestCase):
    def make_worker(self):
        worker = LocalWorker()
        self.addCleanup(_safe_close, worker)
        return worker

    def test_worker_group_property(self):
        worker = self.make_worker()
        group = WorkerGroup()
        self.assertNotIn(worker, group.workers)
        group.add_worker(worker)
        self.assertIn(worker, group.workers)

    def test_group_add_non_worker(self):
        group = WorkerGroup()
        self.assertRaises(ValueError, group.add_worker, object())

    def test_group_add_worker_again(self):
        worker = self.make_worker()
        group = WorkerGroup()
        group.add_worker(worker)
        self.assertRaises(ValueError, group.add_worker, worker)

    def test_group_remove_worker(self):
        worker = self.make_worker()
        group = WorkerGroup()
        group.add_worker(worker)
        self.assertIn(worker, group.workers)
        group.remove_worker(worker)
        self.assertNotIn(worker, group.workers)

    def test_remove_worker_not_in_group(self):
        worker = self.make_worker()
        group = WorkerGroup()
        self.assertRaises(ValueError, group.remove_worker, worker)
        group.add_worker(worker)
        self.assertIn(worker, group.workers)
        group.remove_worker(worker)
        self.assertRaises(ValueError, group.remove_worker, worker)

    def test_lock_timing(self):
        group = WorkerGroup()
        workers = [self.make_worker() for _ in range(5)]
        for worker in workers:
            group.add_worker(worker)
        group.create_lock("test")
        times = []

        def acquire_lock_with_timing(_):
            group.acquire_lock("test")
            start_time = monotonic()
            time.sleep(0.1)
            end_time = monotonic()
            times.append((start_time, end_time))
            group.release_lock("test")

        threads = []
        for worker in workers:
            thread = WorkerThread(worker, acquire_lock_with_timing)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        for i, (start1, end1) in enumerate(times):
            for j, (start2, end2) in enumerate(times):
                if i == j:
                    continue
                self.assertFalse(start1 < start2 < end1)
                self.assertFalse(start2 < start1 < end2)
                self.assertFalse(start1 < end2 < end1)
                self.assertFalse(start2 < end1 < end2)

    def test_barrier_timing(self):
        group = WorkerGroup()
        workers = [self.make_worker() for _ in range(5)]
        for worker in workers:
            group.add_worker(worker)
        group.create_barrier("test")
        times = []

        def wait_barrier_with_timing(_):
            time.sleep(random.randint(1, 10) / 10.0)
            start_time = monotonic()
            group.wait_barrier("test")
            end_time = monotonic()
            times.append((start_time, end_time))

        threads = []
        for worker in workers:
            thread = WorkerThread(worker, wait_barrier_with_timing)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        for (start, _) in times:
            for (_, end) in times:
                self.assertTrue(start < end)

    def test_create_lock_already_in_group(self):
        group = WorkerGroup()
        group.create_lock("test")
        self.assertRaises(ValueError, group.create_lock, "test")

    def test_create_barrier_already_in_group(self):
        group = WorkerGroup()
        group.create_barrier("test")
        self.assertRaises(ValueError, group.create_barrier, "test")
