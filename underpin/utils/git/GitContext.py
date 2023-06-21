import subprocess
from underpin import logger
from pathlib import Path
from pprint import pprint

UNDERPIN_GIT_ROOT = f"{Path.home()}/.underpin/cloned"


def run_command(command, cwd=None):
    # this does not always work but we are using this convention
    options = command.split(" ")

    logger.debug(f"running command {command} in {cwd}")

    process = subprocess.Popen(
        options, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
    )

    status = "ok"
    out, err = process.communicate()

    if not out:
        out = err
        status = "error"
        logger.warning(out)

    return {"status": status, "data": out.decode().split("\n")}


class GitContext:
    # for testing using the cloned but this should be null and passed in
    def __init__(
        self, repo, branch=None, cwd=UNDERPIN_GIT_ROOT, main_branch="main"
    ) -> None:
        """
        current work directory is current
        """
        self._cwd = cwd or "."
        self._repo = repo
        self._branch = branch or main_branch
        self._cwd_abs = cwd
        # todo we can discover this
        self._main_branch = main_branch
        self._changes = []
        repo_name = Path(repo).name
        self._local_repo_dir = f"{self._cwd}/{repo_name}"

    def changed_files(self):
        return self._changes

    def checkout(self):
        """ """

        existing_source_files = None
        if Path(self._local_repo_dir).exists():
            existing_source_files = Path(self._local_repo_dir).iterdir()
        # if the current directory is empty, clone into
        if not existing_source_files:
            logger.info(
                f"Assuming you want to clone into the empty directory {self._cwd}"
            )
            # set branch when cloning so we dont need to switch
            self.clone()
        else:
            print(existing_source_files)
            logger.info(
                f"Repo exists at {self._local_repo_dir} - ensuring local branch is the one we want and up to date"
            )
            # clean this up either within a context or partial
            run_command(f"git checkout {self._branch}", cwd=self._local_repo_dir)
            run_command(f"git fetch", cwd=self._local_repo_dir)
            run_command(f"git pull", cwd=self._local_repo_dir)
            changes = run_command(
                f"git diff --name-only origin/{self._main_branch}",
                cwd=self._local_repo_dir,
            )

            self._changes = changes

    @property
    def main_branch_name(self):
        return self._main_branch

    def clone(self):
        if self._branch != self.main_branch_name:
            return run_command(f"git clone {self._repo} {self._cwd}")
        return run_command(
            f"git clone -b {self._branch} {self._repo} {self._local_repo_dir}"
        )

    def rebase(self, main=True, origin=True):
        pass

    def __enter__(self):
        self.checkout()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        dump underpin state e.g. changed files and current context for last merged
        """
        return True
