import os
import yaml


class ArtisanYaml(object):
    def __init__(self, path):
        self.nodes = {}
        self.jobs = {}
        self.path = path
        self._last_mtime = os.stat(path).st_mtime
        self.reload_yaml()

    def reload_yaml(self):
        """ Reloads the .artisan.yml file
        into this configuration object and
        returns the entities that are changed. """
        with open(self.path, mode="r") as f:
            raw_yaml = yaml.load(f.read())
            pools = raw_yaml.get("pools", {})
            jobs = raw_yaml.get("jobs", {})

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