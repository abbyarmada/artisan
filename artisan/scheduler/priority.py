__all__ = [
    "PriorityRule"
]


class PriorityRule(object):
    def __init__(self, func):
        self._func = func

    def get_priority(self, job):
        priority = self._func(job)
        if not isinstance(priority, (float, int)):
            raise ValueError("PriorityRule must return a float or int.")
        return priority
