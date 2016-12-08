import sys
from tests.base_worker_test import _BaseWorkerTestCase, _safe_close
from artisan.worker import LocalWorker, LocalCommand

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest
try:
    from time import monotonic
except ImportError:
    from time import time as monotonic


class TestLocalWorker(unittest.TestCase, _BaseWorkerTestCase):
    COMMAND_TYPE = LocalCommand

    def make_worker(self):
        worker = LocalWorker()
        self.addCleanup(_safe_close, worker)
        return worker
