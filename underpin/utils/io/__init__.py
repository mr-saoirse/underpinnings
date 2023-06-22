import yaml
from pathlib import Path


def read(f):
    with open(f):
        return yaml.safe_load_all(f)


def write(data, f):
    with open(f, "w"):
        return yaml.safe_dump_all(f)


def is_empty_dir(dir):
    existing_source_files = None
    if Path(dir).is_dir():
        existing_source_files = list(Path(dir).iterdir())
        return len(existing_source_files) == 0
    return False
