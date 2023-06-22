from .GitContext import GitContext
from pathlib import Path
import subprocess
from ..io import write, read
from underpin import logger


def switch_local(branch, cwd):
    pass


# TODO we could move this into a git context as its very stateful
def checkout(
    repo,
    branch=None,
    out_dir=None,
    git_provider="github",
    main_branch="main",
    strategy="target-main",
):
    """
    clones into target output dir (we also need a source)
    - for target  (infra) we need a location for the main branch - we get latest and open a target branch - no need to diff
    - actually its assumed are operating IN the context of that infra branch *NB*** but the source branch is being copied from
    - for the source, we really want the proposed changes at the present time
    - we just need to do some checks for bootstrapping (the state we want us the latest changes i.e. what the full content is and what the list of changed apps are)

    if the dir is empty it should delete it first or we can go in and fetch - under ephemeral assumptions we just use a test mode fetch latest if exists
    this is supposed to be run in a K8s ephemeral pod normally

    using the provider can maybe simplify some tasks e.g. with github we can use things like <gh pr diff> that might take other commands or require other assumptions TBD

    #write state to /.underpin/.checkoutstate

    the strategy to rebase-branch is the default for how we template. we can either only the feature branch to get changes and then get the rebase changes with master to template
    OR we can just use the state that is the feature branch with target-feature - this would depend later on how we want to update manifests in our infra. our assumption is manifests are only updated when we merge to main
    we are merely using a feature branch as a change detector
    NOTE a mode we can use is to use branch main here and then write changes through another means i.e. if we already know the changes we can save them to the underpin state and just read them here

    """

    # check if we have already cloned or clone master

    out_dir = out_dir or f"{Path.home()}/.underpin/cloned/"
    repo_name = Path(repo).name
    expected_wd = f"{out_dir}/{repo_name}"
    out_branch = branch
    # check if target exists

    if not Path(expected_wd).exists():
        logger.info(
            f"The repository has not been cloned to the location {expected_wd}, cloning now..."
        )
        options = ["git", "clone", repo, out_dir]

        # normally we want to clone a specific branch which contains changes of interest under the apps
        if branch:
            options = ["git", "clone", "-b", branch, repo, out_dir]

        process = subprocess.Popen(
            options, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if not process.stdout.read():
            logger.warning(process.stderr.read())
            # return strong type messages
            return False
    else:
        logger.info(
            f"The repository has been cloned to this location. Ensuring we are on branch {branch}"
        )

        # test the branch is always there locally
        options = ["git", "checkout", branch]
        process = subprocess.Popen(
            options, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=expected_wd
        )

        if not process.stdout.read():
            logger.warning(process.stderr.read())
            # return strong type messages
            return False

    # we can only determine changes if the branch is not main
    # otherwise we MUST provide changes in another way - THERE is a danger in the state being stale here
    if branch != main_branch:
        logger.info(f"Determining relevant changes on {branch}")
        options = ["git", "diff", "--name-only", f"origin/{main_branch}"]
        process = subprocess.Popen(
            options, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=expected_wd
        )
        file_changes = process.stdout.read()
        logger.info(f"The following changes were made: {file_changes}")
        logger.info(
            f"Creating a new rebased state and rebase origin main into it to apply templates. TODO warnings if you are time traveling"
        )
        # TODO that i collect ALL the changes that were proposed on the PR for this branch and not just the latest instance? - i actually dont care as such but i DO NEED to know if the app was changed at all
        # im not sure i need to worry about commit history like this or possible re-opened branches - we should be able to assume if something is in main now, the manifests were already pushed
        write(
            {"file_changes": file_changes},
            f"{Path.home()}/.underpin/.state.changed_files.yaml",
        )
        # TODO testing inline with the gh tool that the PR on the branch agrees with the diff

        logger.info(f"Checking out a rebase branch and rebase origin main branch")
        options = ["git", "switch", "-c", f"{branch}.rebased"]
        process = subprocess.Popen(
            options, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=expected_wd
        )

        options = ["git", "rebase", f"origin/{main_branch}"]
        process = subprocess.Popen(
            options, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=expected_wd
        )
        out_branch = f"{branch}.rebased"

    # process for the remote branch, CWD, get changed files on the branch that are being proposed with master
    # for github use the PR
    # otherwise for now assume master is at the moment in time we think and just ask for the git diff
    # always operate in the context of the target branch with the changes that we want (safe??) - maybe try a rebase locally assuming that we will only push merged changes of the app for latest context
    # if we rebase after that means we know the changes that were being proposed ??
    # but we do want to test for idempotence in our local processes

    # return strong type messages
    return {"branch": out_branch, "changes": app_changes(repo)}


def app_changes(repo, cache=True):
    """
    This function gets changes and returns a structured list of app changes

    it diff --name-only origin/<branch> OR checkout branch and then we need the proposed changes in any case with main


    test if the feature branch has been merged / if it is used the master and just use the feature branch to determine the changes

    #how to find out if the branch is already merged AND not currently open:. if its nots merged just clone if it is clone master
    #either way use PR to get the changes
    #gh search prs -H <branch> --json number
    #gh pr view <number> --json files --jq '.files.[].path'

    we should have a version of this as not dependant on github obviously but this is good for testing

    """

    return read(f"{Path.home()}/.underpin/.state.changed_files.yaml")
