import sys
from artisan.worker import LocalWorker, WorkerGroup

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest


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
        self.assertIs(worker.group, None)
        self.assertNotIn(worker, group.workers)
        group.add_worker(worker)
        self.assertIs(worker.group, group)
        self.assertIn(worker, group.workers)

    def test_group_add_non_worker(self):
        group = WorkerGroup()
        self.assertRaises(ValueError, group.add_worker, object())

    def test_group_add_worker_again(self):
        worker = self.make_worker()
        group = WorkerGroup()
        group.add_worker(worker)
        self.assertRaises(ValueError, group.add_worker, worker)

    def test_group_worker_already_in_group(self):
        worker = self.make_worker()
        group1 = WorkerGroup()
        group2 = WorkerGroup()
        group1.add_worker(worker)
        self.assertRaises(ValueError, group2.add_worker, worker)

    def test_group_remove_worker(self):
        worker = self.make_worker()
        group = WorkerGroup()
        group.add_worker(worker)
        self.assertIs(worker.group, group)
        self.assertIn(worker, group.workers)
        group.remove_worker(worker)
        self.assertIs(worker.group, None)
        self.assertNotIn(worker, group.workers)

    def test_remove_worker_not_in_group(self):
        worker = self.make_worker()
        group = WorkerGroup()
        self.assertRaises(ValueError, group.remove_worker, worker)
        group.add_worker(worker)
        self.assertIs(worker.group, group)
        self.assertIn(worker, group.workers)
        group.remove_worker(worker)
        self.assertRaises(ValueError, group.remove_worker, worker)
