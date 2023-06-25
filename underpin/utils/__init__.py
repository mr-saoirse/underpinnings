from loguru import logger as loguru_logger
from .funcs import *
import sys
import os

LOG_LEVEL = os.environ.get("UNDERPIN_LOG_LEVEL", "INFO")

loguru_logger.remove()
loguru_logger.add(sys.stderr, level=LOG_LEVEL)  # or sys.stdout or other file object
