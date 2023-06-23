from . import UnderpinTemplate
from .UnderpinTemplate import dispatcher


class UnderpinTemplateSet:
    def write(self, path):
        return None


def generate(app, config):
    return dispatcher(app, config)
