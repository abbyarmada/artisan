import os
import getpass
import sys
from tests.base_worker_test import _BaseWorkerTestCase, _safe_close
from artisan.worker import SshWorker, SshCommand

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest
try:
    from time import monotonic
except ImportError:
    from time import time as monotonic


@unittest.skipUnless("ARTISAN_SSH_PASSWORD" in os.environ, ("Set the environment variable ARTISAN_SSH_PASSWORD"
                                                            " to be able to test the SshWorker tests."))
class TestSshWorker(unittest.TestCase, _BaseWorkerTestCase):
    COMMAND_TYPE = SshCommand

    def make_worker(self):
        worker = SshWorker("localhost", getpass.getuser(), password=os.environ["ARTISAN_SSH_PASSWORD"])
        self.addCleanup(_safe_close, worker)
        return worker
