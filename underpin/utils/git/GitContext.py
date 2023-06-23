import subprocess
from underpin import logger
from pathlib import Path
from ..io import is_empty_dir


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
        if len(err):
            out = err
            status = "error"
            # hack - i need to fix what is a warning
            for ok in ["Switched to a new branch", "Cloning into"]:
                if ok in str(out):
                    status = "ok"
            if status != "ok":
                logger.warning(f"process-> {out}")
    else:
        logger.debug(out)

    return {"status": status, "data": out.decode().split("\n")}


def _branches(data):
    """
    category of temp helpers while we structure out command interface for git commands
    """
    return [d.replace("*", "").strip() for d in data]


class GitContext:
    # for testing using the cloned but this should be null and passed in
    def __init__(self, repo, branch=None, cwd=None, main_branch="main") -> None:
        """
        current work directory is current
        """
        logger.info(f"Enter repo context {repo} -> CWD({cwd or 'local'})")

        self._cwd = cwd
        self._repo = repo
        self._branch = branch or main_branch
        # todo we can discover this
        self._main_branch = main_branch
        self._changes = []
        self._repo_name = Path(repo).name.split(".")[0]

        # when we are not specifying a current working directory its because our local is it
        self._local_repo_dir = f"{self._cwd}/{self._repo_name}" if self._cwd else None

    def merge(self):
        """
        use

        git push origin bot/branch123
        #this uses the branch we are on for the github provider
        gh pr create --title "Manifests generated from the ARepo" --body "List of apps changed"
        gh pr merge --auto --rebase

        """
        pass

    def get_changed_files(self):
        r = self("git diff --name-only origin/main")
        return r["data"]

    def clone(self):
        if self._branch == self.main_branch_name:
            return run_command(f"git clone {self._repo}", cwd=self._cwd)
        return run_command(
            f"git clone -b {self._branch} {self._repo}",
            cwd=self._cwd,
        )

    def create_branch(self, branch_name):
        r = self(f"git checkout -b {branch_name}")
        self._branch = branch_name
        return r

    def __call__(self, command):
        return run_command(command, cwd=self._local_repo_dir)

    def checkout(self):
        """
        checkout the branch and determine changes
        this is done so underpin can generate templates for the changed file
        """

        # could rename this to managed i.e. we have a local repo somewhere and we are managing it
        # when this is empty, it means we are in a normal git context "user managed" - we should make these abstractions cleaner

        if self._local_repo_dir:
            if is_empty_dir(self._local_repo_dir):
                logger.info(
                    f"Assuming you want to clone into the empty directory {self._cwd}"
                )
                # set branch when cloning so we dont need to switch
                response = self.clone()
            else:
                # print(existing_source_files)
                logger.info(
                    f"Repo exists at {self._local_repo_dir} - ensure local branch is the one we want and up to date"
                )
                self("git branch")

    @property
    def main_branch_name(self):
        return self._main_branch

    @property
    def branch(self):
        return self._branch

    def __enter__(self):
        # checkout depends on mode
        self.checkout()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """ """

        return False
