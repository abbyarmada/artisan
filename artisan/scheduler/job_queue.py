import functools
import random
import threading
from .priority import PriorityRule

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
            low, high = 0, len(self._job_queue) - 1
            while low < high:
                index = low + (high - low) // 2
                print(low, index, high)
                index_priority = self._job_priority[index]
                print(priority, index_priority)
                if index_priority < priority:
                    low = index + 1
                elif index_priority > priority:
                    high = index - 1
                else:
                    low = index
                    break

            self._job_priority.insert(low, priority)
            self._job_queue.insert(low, job)

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
            for i, other in self._priority_rules:
                if other is rule:
                    break
            else:
                raise ValueError("PriorityRule not found within JobQueue's rules.")
            del self._priority_rules[i]
            self._reorganize_queue()

    def _reorganize_queue(self):
        with self._lock:
            new_priority = {}
            for job in self._job_queue:
                priority = 0.0
                for rule in self._priority_rules:
                    assert isinstance(rule, PriorityRule)
                    priority += rule.get_priority(job)
                new_priority[job] = priority

            new_queue = sorted(new_priority,
                               key=functools.cmp_to_key(lambda a, b: _random_cmp(new_priority[a],
                                                                                  new_priority[b])))
            self._job_queue = new_queue
            self._job_priority = [new_priority[job] for job in self._job_queue]