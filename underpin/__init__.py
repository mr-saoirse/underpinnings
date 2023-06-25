from . import schema, pipeline, utils
from .utils import loguru_logger as logger
from .utils.io import read
from pathlib import Path

UNDERPIN_GIT_ROOT = f"{Path.home()}/.underpin/cloned"
CONFIG_HOME = f"{Path.home()}/.underpin/config.yaml"
