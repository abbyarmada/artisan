import sys
from artisan.worker import BaseWorker

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest


class TestBaseWorker(unittest.TestCase):
    def test_str(self):
        worker = BaseWorker("user", "host")
        self.assertEqual(str(worker), "<Worker user=user host=host>")

    def test_repr(self):
        worker = BaseWorker("user", "host")
        self.assertEqual(repr(worker), "<Worker user=user host=host>")