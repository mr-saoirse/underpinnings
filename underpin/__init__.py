from . import schema, pipeline, utils
from .utils import loguru_logger as logger
from .utils.io import read
from pathlib import Path
import os

# "/mnt/vol"  # Path.home() #<-todo env var or default to home. in K8s assume its mnt vol
HOME = Path.home()

UNDERPIN_GIT_ROOT = f"{HOME}/.underpin/cloned"  # f"{Path.home()}/.underpin/cloned"
CONFIG_HOME = f"{HOME}/.underpin/config.yaml"
UNDERPIN_APP_ROOT = "apps"
