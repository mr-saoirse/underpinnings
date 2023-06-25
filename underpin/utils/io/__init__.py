import yaml
from pathlib import Path
import subprocess


def read(f):
    with open(f) as f:
        return yaml.safe_load(f)


def write(data, f, make_dir=False):
    if make_dir:
        Path(f).parent.mkdir(exist_ok=True, parents=True)
    with open(f, "w") as f:
        if isinstance(data, str):
            f.write(data)
        else:
            yaml.safe_dump(data, f)


def is_empty_dir(dir):
    existing_source_files = None
    if Path(dir).is_dir():
        existing_source_files = list(Path(dir).iterdir())
        return len(existing_source_files) == 0
    return False


def run_command(command, cwd=None):
    options = command.split(" ")
    process = subprocess.Popen(
        options, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
    )

    out, err = process.communicate()

    return out
