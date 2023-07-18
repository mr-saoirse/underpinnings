import subprocess
from underpin import logger
from pathlib import Path
from ..io import is_empty_dir
from underpin.utils import split_string_with_quotes


def run_command(command, cwd=None):
    # this does not always work but we are using this convention
    options = split_string_with_quotes(command)
    logger.debug(f"running command {command} in {cwd}")

    process = subprocess.Popen(
        options, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
    )

    status = "ok"
    out, err = process.communicate()

    if process.returncode and err:
        out = err
        status = "error"
        logger.warning(f"process-> {out}")
    elif out:
        logger.debug(out)

    return {"status": status, "data": out.decode().split("\n")}


def _branches(data):
    """
    category of temp helpers while we structure out command interface for git commands
    """
    return [d.replace("*", "").strip() for d in data]


class GitUri:
    def __init__(self, uri):
        """
        https://github.com/mr-saoirse/underpinnings.git
        git@github.com:mr-saoirse/underpinnings.git

        only for a special case for now - crude to spike
        """
        uri = str(uri)
        self._uri = uri
        self._scheme = "git" if "https://" not in uri else "https"
        # todo test for arb strings
        self._name = uri.split("/")[-1].split(".")[0]
        self._org = None
        try:
            self._org = uri.split("/")[-2].split(":")[-1]
        except:
            pass

    def __repr__(self) -> str:
        return self._uri

    def equals(self, other):
        if isinstance(other, str):
            other = GitUri(other)
        return other._name == self._name and other._org == self._org


class GitContext:
    """
    Git context points to a repository location but also creates an expectation about branches
    It can initialize a git repo into the directory or it get changes into an existing repo
    """

    # for testing using the cloned but this should be null and passed in
    def __init__(self, repo, branch=None, cwd="./underpin", main_branch="main") -> None:
        """
        current work directory is current
        """
        logger.info(f"Enter repo context {repo} -> CWD({cwd or 'local'})")
        self._cwd = cwd
        # expected branched
        self._repo = repo
        # this is the desired not the actual necessary
        self._branch = branch or main_branch
        # todo we can discover this
        self._main_branch = main_branch
        self._changes = []
        self._repo_name = Path(repo).name.split(".")[0]
        # when we are not specifying a current working directory its because our local is it
        self._local_repo_dir = f"{self._cwd}" if self._cwd else None
        self._set_branch_info()

    @property
    def current_git_repo(self):
        uri = self._current_git_context_repo
        if uri:
            return GitUri(uri)

    def __repr__(self) -> str:
        s = f"""
        cwd: {self._cwd}
        expected_repo: {self._repo}
        git_repo: {self.current_git_repo}
        expected_branch: {self.desired_branch}
        current_branch: {self.branch}
        is_expected_repo: {self.is_valid}
        """
        return s

    @property
    def is_valid(self):
        return GitUri(self._repo).equals(GitUri(self.current_git_repo))

    def add_all(self, message=None):
        message = message or "automated commit"
        self("git add .")
        self(f'git commit -m "{message}"')

        return self.get_changes()

    def _set_branch_info(self):
        """
        TODO: general get all the git context properly
        """
        self._current_git_context_repo = None
        self._current_branch = None

        try:
            self._current_git_context_repo = self("git config --get remote.origin.url")[
                "data"
            ][0]

            data = self("git branch --list")["data"]
            self._branches = []
            for d in data:
                is_current = "*" in d
                self._branches.append(d.replace("*", "").strip())
                if is_current:
                    self._current_branch = self._branches[-1]
        except Exception as ex:
            logger.warning(ex)
            logger.warning(
                f"The current working directory {self._cwd} does not seem to be a git repository"
            )

    def get_changes(self, against_origin=False):
        ans = (
            self("git diff --name-only main")
            if not against_origin
            else self("git diff --name-only origin/main")
        )
        return ans["data"]

    def merge(
        self,
        pr_name="Manifests generated from the ARepo",
        pr_change_note="List of apps changed",
    ):
        """
        use
        TODO: this can fail if there is an open /bad PR already so we need to see what to do about that.
        Typically it will mean making sure we got latest from main
        """
        logger.info(f"Committing from branch {self._current_branch}")
        self.add_all()
        # TODO:> todo determine what branch we are actually meaning to be on
        self(f"git rebase origin/{self._main_branch}")

        # TODO: here we assume the provider is github so we need to generalize this part
        self("git push origin bot.add_manifests")
        self(f"""gh pr create --title "{pr_name}" --body "{pr_change_note}" """)
        self("gh pr merge --auto --rebase")
        logger.info(f"Pushed pr [{pr_name}] and auto merged (pending checks)")

    def clone(self):
        if self._branch == self.main_branch_name:
            return run_command(f"git clone {self._repo}", cwd=self._cwd)
        return run_command(
            f"git clone -b {self._branch} {self._repo}",
            cwd=self._cwd,
        )

    def ensure_on_branch(self, branch_name, rebase_main=False):
        """
        This is setup to ensure s state - we may already be on the branch and we have an option to rebase
        - either the branch does not exist and we make and switch
        - the branch does exist and we switch
        """
        if branch_name != self._current_branch:
            if branch_name in self._branches:
                self(f"git checkout {branch_name}")

            else:
                r = self(f"git checkout -b {branch_name}")
        if rebase_main:
            self(f"git rebase origin/{self._main_branch}")
        return self._current_branch

    def create_branch(self, branch_name):
        r = self(f"git checkout -b {branch_name}")
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
                self.clone()
            else:
                # print(existing_source_files)
                logger.info(
                    f"Repo exists at {self._local_repo_dir} - ensure local branch is the one we want and up to date"
                )

        return self.branch

    @property
    def main_branch_name(self):
        return self._main_branch

    @property
    def branch(self):
        return self._current_branch

    @property
    def desired_branch(self):
        return self._branch

    def __enter__(self):
        # checkout depends on mode
        self.checkout()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """ """

        return False
