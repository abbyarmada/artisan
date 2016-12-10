import arrow

__all__ = [
    "BaseTrigger",
    "ScheduledTrigger"
]


class BaseTrigger(object):
    def __init__(self, user, cause, params=None):
        """ Base trigger interface to be implemented
        by all other triggers.  This object describes
        how a Job was scheduled. """
        self.user = user
        self.cause = cause
        self.trigger_time = arrow.now()
        self.params = params

    def __repr__(self):
        return "<Trigger user=%s cause=%s params=%s>" % (self.user,
                                                         self.cause,
                                                         self.params)


class ScheduledTrigger(BaseTrigger):
    def __init__(self, params=None):
        """ Trigger for if the Job was given a schedule
        and the schedule automatically scheduled the
        Job to be executed. """
        super(ScheduledTrigger, self).__init__("Artisan",
                                               "Scheduled by an automatic trigger.",
                                               params)


class ManualTrigger(BaseTrigger):
    def __init__(self, user, params=None):
        super(ManualTrigger, self).__init__(user, "Scheduled by `%s`." % user, params)
