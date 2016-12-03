import sys
from artisan.worker import WorkerPool, LocalWorker

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest


def _safe_close(pool):
    for worker in pool._pool:
        try:
            worker.close()
        except Exception:
            pass


class TestWorkerPool(unittest.TestCase):
    def make_pool(self, max_workers=1):
        pool = WorkerPool(max_workers, lambda: LocalWorker())
        self.addCleanup(_safe_close, pool)
        return pool

    def test_unique_worker(self):
        pool = self.make_pool(1)
        worker1 = pool.acquire(0.1)
        pool.release(worker1)
        worker2 = pool.acquire(0.1)
        self.assertIsNot(worker1, worker2)

    def test_properties(self):
        pool = self.make_pool(3)

        self.assertEqual(pool.max_workers, 3)
        self.assertEqual(pool.workers_free, 3)
        self.assertEqual(pool.workers_used, 0)

        worker = pool.acquire()

        self.assertEqual(pool.max_workers, 3)
        self.assertEqual(pool.workers_free, 2)
        self.assertEqual(pool.workers_used, 1)

        pool.release(worker)

        self.assertEqual(pool.max_workers, 3)
        self.assertEqual(pool.workers_free, 3)
        self.assertEqual(pool.workers_used, 0)

    def test_acquire_empty_pool(self):
        pool = self.make_pool(1)
        worker = pool.acquire(0.1)
        self.assertIs(pool.acquire(0.1), None)
        pool.release(worker)

    def test_worker_closed_on_release(self):
        pool = self.make_pool(1)
        worker = pool.acquire(0.1)
        self.assertFalse(worker.closed)
        pool.release(worker)
        self.assertTrue(worker.closed)

    def test_release_worker_not_in_pool(self):
        pool = self.make_pool(1)
        pool.acquire(0.1)
        self.assertRaises(ValueError, pool.release, object())

    def test_setup_step_called(self):
        token = object()

        def step(w):
            setattr(w, "token", token)

        pool = self.make_pool(1)
        pool.add_worker_setup_step(step)
        worker = pool.acquire(0.1)

        self.assertIs(getattr(worker, "token", None), token)

    def test_cleanup_step_called(self):
        token = object()

        def step(w):
            setattr(w, "token", token)

        pool = self.make_pool(1)
        pool.add_worker_cleanup_step(step)
        worker = pool.acquire(0.1)
        pool.release(worker)
        self.assertIs(getattr(worker, "token", None), token)

    def test_setup_and_cleanup_step_called(self):
        token1 = object()
        token2 = object()

        def setup_step(w):
            setattr(w, "token", token1)

        def cleanup_step(w):
            setattr(w, "token", token2)

        pool = self.make_pool(1)
        pool.add_worker_setup_step(setup_step)
        pool.add_worker_cleanup_step(cleanup_step)
        worker = pool.acquire(0.1)
        self.assertIs(getattr(worker, "token", None), token1)
        pool.release(worker)
        self.assertIs(getattr(worker, "token", None), token2)

    def test_release_closed_worker(self):
        pool = self.make_pool(1)
        worker = pool.acquire(0.1)
        worker.close()
        self.assertEqual(pool.workers_free, 0)
        pool.release(worker)
        self.assertEqual(pool.workers_free, 1)

    def test_worker_has_pool(self):
        pool = self.make_pool(1)
        worker = pool.acquire(0.1)
        self.assertIs(worker.pool, pool)
