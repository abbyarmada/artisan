__all__ = [
    "JobFailureException",
    "WorkerLostException",
    "JobCancelledException",
    "JobErrorException"
]


class JobFailureException(Exception):
    """ Exception which would cause a Job to
    fail. Includes a `cause` which is to be
    displayed for users. """
    def __init__(self, cause):
        self.cause = cause
        super(JobFailureException, self).__init__()

    def __repr__(self):
        return "<JobFailureException cause=%s>" % self.cause


class WorkerLostException(JobFailureException):
    """ Exception for when during a Job a
    worker becomes unavailable unexpectedly
    or disconnects in the case of an SshWorker. """
    pass


class JobCancelledException(JobFailureException):
    """ Exception for when a Job is cancelled
    by some external force.  Usually this is
    by a user manually cancelling a Job."""
    pass


class JobErrorException(JobFailureException):
    """ If an Exception that is not caught occurs
    during a Job then this exception is raised
    with that exception attached. """
    pass
