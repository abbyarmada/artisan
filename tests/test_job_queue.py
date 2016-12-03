import itertools
import sys
from artisan.scheduler import (
    JobQueue,
    Job
)

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest


class WeightedJob(Job):
    def __init__(self, weight):
        super(WeightedJob, self).__init__()
        self.weight = weight


def weight_rule(job):
    return getattr(job, "weight", 0)


class TestJobQueue(unittest.TestCase):
    def test_empty_queue_init(self):
        queue = JobQueue()
        self.assertTrue(queue.empty)

    def test_empty_queue_single_push(self):
        queue = JobQueue()
        queue.push_job(Job())
        self.assertFalse(queue.empty)
        queue.pop_job()
        self.assertTrue(queue.empty)

    def test_empty_queue_multiple_pushes(self):
        queue = JobQueue()
        queue.push_job(Job())
        self.assertFalse(queue.empty)
        queue.push_job(Job())
        self.assertFalse(queue.empty)
        queue.pop_job()
        self.assertFalse(queue.empty)
        queue.pop_job()
        self.assertTrue(queue.empty)

    def test_push_pop_same_job(self):
        queue = JobQueue()
        job = Job()
        queue.push_job(job)
        self.assertIs(queue.pop_job(), job)

    def test_peek_job(self):
        queue = JobQueue()
        job = Job()
        queue.push_job(job)
        self.assertIs(queue.peek_job(), job)
        self.assertFalse(queue.empty)
        self.assertIs(queue.peek_job(), job)

    def test_pop_empty(self):
        queue = JobQueue()
        self.assertIs(queue.pop_job(), None)
        job = Job()
        queue.push_job(job)
        self.assertIs(queue.pop_job(), job)
        self.assertIs(queue.pop_job(), None)

    def test_job_pop_ordering(self):
        for combo in itertools.permutations([WeightedJob(1), WeightedJob(2), WeightedJob(3)]):
            queue = JobQueue()
            queue.add_priority_rule(weight_rule)

            for job in combo:
                queue.push_job(job)

            job = queue.pop_job()
            self.assertEqual(job.weight, 3)
            job = queue.pop_job()
            self.assertEqual(job.weight, 2)
            job = queue.pop_job()
            self.assertEqual(job.weight, 1)
