import random
import threading
from .priority import PriorityRule
from ..compat import cmp_to_key

__all__ = [
    "JobQueue"
]


def _random_cmp(a, b):
    """ Similar to a regular compare except
    that on equality will return a random
    choice rather than a 0. """
    if a > b:
        return 1
    elif b > a:
        return -1
    else:
        return random.choice([-1, 1])


class JobQueue(object):
    def __init__(self):
        self._lock = threading.RLock()
        self._job_queue = []
        self._job_priority = []
        self._priority_rules = []

    def push_job(self, job):
        """ Pushes a Job into the queue. """
        with self._lock:
            priority = 0.0
            for rule in self._priority_rules:
                priority += rule.get_priority(job)
            job_len = len(self._job_priority)
            if not job_len:
                self._job_priority.append(priority)
                self._job_queue.append(job)
            else:
                for i in range(job_len):
                    if self._job_priority[i] < priority:
                        self._job_priority.insert(i, priority)
                        self._job_queue.insert(i, job)
                        break
                else:
                    self._job_priority.append(priority)
                    self._job_queue.append(job)

    def peek_job(self):
        """ Peeks at but doesn't remove the next
        Job in the queue. Returns None if it's empty. """
        with self._lock:
            if not self._job_queue:
                return None
            return self._job_queue[0]

    def pop_job(self):
        """ Removes and returns the next Job in the
        queue. Returns None if it's empty. """
        with self._lock:
            if not self._job_queue:
                return None
            job = self._job_queue[0]
            del self._job_queue[0]
            del self._job_priority[0]
            return job

    @property
    def empty(self):
        with self._lock:
            return False if self._job_queue else True

    @property
    def jobs(self):
        with self._lock:
            return self._job_queue[:]

    @property
    def priority_rules(self):
        with self._lock:
            return self._priority_rules[:]

    def add_priority_rule(self, func):
        """ Adds a rule to how priority of
        Jobs is calculated. Returns the rule
        for use with removing. """
        rule = PriorityRule(func)
        with self._lock:
            self._priority_rules.append(rule)
            self._reorganize_queue()
        return rule

    def remove_priority_rule(self, rule):
        """ Removes a rule about how
        the priority of each Job is calculated."""
        with self._lock:
            for i, other in enumerate(self._priority_rules):
                if other is rule:
                    break
            else:
                raise ValueError("PriorityRule not found within JobQueue's rules.")
            del self._priority_rules[i]
            self._reorganize_queue()

    def _reorganize_queue(self):
        """ Reorganizes the queue of Jobs against the rules
        that have been added to the JobQueue. """
        with self._lock:
            new_priority = {}
            for job in self._job_queue:
                priority = 0.0
                for rule in self._priority_rules:
                    assert isinstance(rule, PriorityRule)
                    priority += rule.get_priority(job)
                new_priority[job] = priority

            compare_func = cmp_to_key(lambda a, b: _random_cmp(
                                      new_priority[a],
                                      new_priority[b]))
            new_queue = sorted(new_priority.keys(), key=compare_func, reverse=True)
            self._job_queue = new_queue
            self._job_priority = [new_priority[job] for job in self._job_queue]
