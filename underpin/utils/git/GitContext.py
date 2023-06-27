from pathlib import Path
import subprocess
from typing import Any
from underpin import logger, UNDERPIN_GIT_ROOT
from underpin.utils import split_string_with_quotes
from ..io import is_empty_dir


class GitContext:
    def __init__(
        self, origin_uri, local_dir=None, branch=None, main_branch="main", **kwargs
    ) -> None:
        """
        The git context is expected to initialize into a location where the origin repo has already been cloned
        This could be
        - a mounted /app folder
        - a local dev branch

        origin uri can be anywhere in the context of the the git repo
        it is expected we will also want to define a default apps folder under the root of the repo
        the apps folder can be a sub folder of the apps

        For the target repo pattern, we can also clone into a target location has a special case
        we put a lock on this use case whereby we will only clone into HOME/.underpin/cloned

        local_dir: this is the parent directory of the repo ALWAYS
                   we can reproduce the full path as CWD/repo_name
        we can always be anywhere under the git repo

        """
        self._main_branch = main_branch
        self._origin_uri = origin_uri
        self._local_dir = local_dir or Path.cwd()
        self._repo_name = self._origin_uri.split("/")[-1].split(".")[0]
        self._branch = branch or main_branch
        self._repo_info = self._get_repo_info()

    # def __call__(self, command):
    #     return run_command(command, cwd=self._local_repo_dir)
    def __enter__(self):
        """
        this is reserved for when we want to specifically enter a checkout state
        - for target this is safe in that we create repos and branches in the underpin home
        - but for the source repo actually its assumed we are already in the correct context and this is for validation
        """
        # checkout depends on mode
        self.checkout()

        return self

    def __call__(self, command: str, cwd=None) -> Any:
        return self._run_command(command, cwd=cwd or self._local_dir)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """ """

        return False

    def _get_repo_info(self):
        """ """
        cleaner = lambda s: s.replace("*", "").strip()
        data = self.run_command_list_result("git branch --list")
        self._current_branch = [cleaner(d) for d in data if "*" in d]
        self._branches = [cleaner(d) for d in data]
        self._current_repo = self.run_command_single_result(
            "git config --get remote.origin.url"
        )
        self._changes = self.get_changes()

        return {}

    @property
    def current_repo(self):
        return self._current_repo

    @property
    def current_branch(self):
        return self._current_branch

    @property
    def local_repo_dir(self):
        return f"{self._local_dir}/{self._repo_name}"

    def get_changes(self, against_origin=False):
        r = (
            self("git diff --name-only main")
            if not against_origin
            else self("git diff --name-only origin/main")
        )
        return r["data"]

    def ensure_branch(self, branch):
        pass

    def checkout(self):
        """
        We always have the parent root to where we clone things
        and if we know the name of the
        """
        # the first thing is just a check or safety. generally this class should not know about a special dir
        if self._local_dir == UNDERPIN_GIT_ROOT and is_empty_dir(self.local_repo_dir):
            logger.info(
                f"Assuming you want to clone into the empty directory {self._local_dir}"
            )
            self.clone()
        else:
            # print(existing_source_files)
            logger.info(
                f"Repo exists at {self._local_dir} - ensure local branch is the one we want and up to date"
            )

    def clone(self):
        if self._branch == self.main_branch_name:
            return self(f"git clone {self._repo}", cwd=self._local_dir)
        return self(
            f"git clone -b {self._branch} {self._repo}",
            cwd=self._local_dir,
        )

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

    def commit_all(self):
        message = message or "automated commit"
        self("git add .")
        self(f'git commit -m "{message}"')
        return self.get_changes()

    def run_command_single_result(self, command):
        r = self(command)
        if r["status"] == "ok":
            return r["data"][0]
        raise Exception(f"Command failed {r['data']}")

    def run_command_list_result(self, command):
        r = self(command)
        if r["status"] == "ok":
            return r["data"]
        raise Exception(f"Command failed {r['data']}")

    def _run_command(self, command, cwd=None):
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
