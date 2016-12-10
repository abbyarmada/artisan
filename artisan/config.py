import os


class ArtisanYaml(object):
    def __init__(self, path):
        self.nodes = {}
        self.jobs = {}
        self.path = path
        self._last_mtime = os.stat(path).st_mtime

    def _check_last_mtime(self):
        try:
            new_mtime = os.stat(self.path).st_mtime
            if new_mtime > self._last_mtime:
                self._last_mtime = new_mtime
                return True
        except OSError:
            pass
        return False


def load_artisan_yml(path):
    """ Loads an .artisan.yml file into an
    ArtisanYaml object that can be used to """
    pass
