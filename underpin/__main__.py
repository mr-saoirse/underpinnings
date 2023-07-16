"""
For simplicity it is assumed that source and target repos will live in
/HOME/.underpin/cloned/[REPO.git]
For example, underpinning is an example source repo which would live in K8s at
/root/.underpin/underpinnings.git

This simple thing is easy to test and then in the following scenarios we use symlinks or volume mounts
- local dev, dev project symlinked to /HOME/.underpin/cloned/project.git/
- docker or K8s volume mounts to /HOME/.underpin/cloned/project.git/

For example do
ln -s /Users/sirsh/code/mr_saoirse/underpinnings ~/.underpin/cloned/underpinnings

"""

import typer
from typing import Optional
from pathlib import Path
from underpin.config import UnderpinConfig
from underpin.pipeline.default import DefaultPipeline
from underpin.utils import io
from underpin import schema
from underpin.utils.git import GitContext, app_changes
from underpin.schema import ChangeSet
from underpin import logger, UNDERPIN_GIT_ROOT, CONFIG_HOME
from underpin.utils.io import run_command
from underpin.utils import generate_markdown_table
from json import loads as json_loads
from glob import glob

app = typer.Typer()

template_app = typer.Typer()
app.add_typer(template_app, name="template")

infra_app = typer.Typer()
app.add_typer(infra_app, name="infra")


build_app = typer.Typer()
app.add_typer(build_app, name="build")


# @build_app.command("containers")
# def build_app_containers(
#     config_file: Optional[str] = typer.Option(None, "--config", "-c"),
#     dir: Optional[str] = typer.Option(None, "--dir", "-d"),
# ):
#     config = UnderpinConfig(config_file or CONFIG_HOME)

#     # iterate app actions or use just one app if dir is specified

#     #


# @build_app.command("kustomize")
# def build_app_update(
#     config_file: Optional[str] = typer.Option(None, "--config", "-c"),
#     dir: Optional[str] = typer.Option(None, "--dir", "-d"),
# ):
#     config = UnderpinConfig(config_file or CONFIG_HOME)

#     target = GitContext(config.target_repo, cwd=UNDERPIN_GIT_ROOT)
#     changes = target.get_changes()
#     logger.info(changes)

#     # not sure if we need this - can we tag with the image we are going to build and be done it
#     # iterate app actions or use just one app if dir is specified
#     # run_command("kustomize set-image {action.kustomization.image}")


@app.command("update")
def app_update(
    sha: Optional[str] = typer.Option(None, "--sha", "-h"),
    app_dir: Optional[str] = typer.Option(None, "--app-dir", "-d"),
    source_repo: Optional[str] = typer.Option(None, "--source-repo", "-s"),
    target_repo: Optional[str] = typer.Option(None, "--target-repo", "-t"),
):
    """
    Mirroring the pipeline runner, here we can determine actions for all apps and push changes to target
    By default we do not need to inspect what happened at source and just commit whatever is in our branch
    But we leave some scaffolding here to think more about it
    """
    if app_dir == "":
        app_dir = None

    # if not Path(CONFIG_HOME).is_file():
    #     UnderpinConfig.configure(source_repo, target_repo)

    # internal generate config so need for config - test file exists
    # manage the paths for source and target based on app dir context
    config = UnderpinConfig(
        CONFIG_HOME, source_repo=source_repo, target_repo=target_repo
    )
    logger.info(
        f"{config.source_repo}->{config.target_repo} using hash {sha} for app {app_dir}"
    )

    # map app dir as filter to the app manifest - it is usually written relative to the source repo
    with GitContext(config.source_repo) as source:
        app_actions = []  # underpin report
        # changes = DefaultPipeline(config).map_changes_to_target_changes(changes)

    target = GitContext(config.target_repo)
    changes = target.get_changes() if not app_dir else source.sub_folders(app_dir)
    logger.info(f"target app changes: {changes}")
    return target.merge(
        pr_change_note=generate_markdown_table(app_actions, "Applied Underpin Actions")
    )


@app.command("run")
def app_run(
    sha: Optional[str] = typer.Option(None, "--sha", "-h"),
    app_dir: Optional[str] = typer.Option(None, "--app-dir", "-d"),
    source_repo: Optional[str] = typer.Option(None, "--source-repo", "-s"),
    target_repo: Optional[str] = typer.Option(None, "--target-repo", "-t"),
):
    """
    sha: the sha is a branch id used to tag docker images and target branches
    app_dir: is an optional parameter but one used mostly in production.
             For dev it can be omitted and we operate on the git context change files
             In production we would pass a change set from upstream process
             The app dir can be inferred within a source repo but also mapped to a target repo app-manifest
    source_repo: is the the Applications Git Repo (ARepo) that we generate apps from
    target_repo: is the the Infrastructure Git Repo (IRepo) that we send app templates to

    The basic runner can be used for dev, docker or k8 simple mode
    - for dev operate on a branch and template changed apps
    - for docker, do the same but mount the local
    - for K8s, workflow should pass an app dir

    """

    # TODO refactor config so it does not need to exist
    config = UnderpinConfig(
        CONFIG_HOME, source_repo=source_repo, target_repo=target_repo
    )
    logger.info(
        f"{config.source_repo}->{config.target_repo} using hash {sha} for app {app_dir}"
    )

    """
    checkout the target repo to which we send manifests
    """
    with GitContext(config.target_repo, branch=sha or "test") as target:
        target.checkout()

    """
    this works for docker or local dev - we can mount a local git repo to wherever the app dir is
    for kubernetes we can also point the app dir to the application(s) location where the (source) git repo is cloned
    """
    with GitContext(config.source_repo, cwd=app_dir) as source:
        """
        we can navigate anywhere into a git repo and get changes or all apps from that root
        this is a simple strategy to test two different modes which in practice may have different entrypoints
        """
        changes = source.get_changes() if not app_dir else source.sub_folders(app_dir)
        pipeline = DefaultPipeline(config)
        pipeline(changes)

    # this output should by pydantic->json and collected in argo workflow etc.
    return {"job deets"}


# @template_app.command("create")
# def template_app_validate(
#     name: Optional[str] = typer.Option(None, "--name", "-n"),
# ):
#     pass


# @app.command("init")
# def app_init(
#     target_branch: Optional[str] = typer.Option(None, "--target_branch", "-b"),
#     target_local_dir: Optional[str] = typer.Option(None, "--target_out_dir", "-o"),
# ):
#     """
#     underpin generates a target repo away from the current repo to write files into and commit
#     the target branch can be auto-generated with a hash in practice
#     """

#     # TODO: if branch exists handle this case properly

#     if not Path(CONFIG_HOME).is_file():
#         UnderpinConfig.configure()

#     config = UnderpinConfig(CONFIG_HOME)
#     target_branch = target_branch or "bot.add_manifests"
#     logger.debug(config._data)

#     with GitContext(config.target_repo, cwd=UNDERPIN_GIT_ROOT) as g:
#         g.create_branch(target_branch)
#         logger.info(f"create target repo to {g}")
#         # if we need to do anything to the target we can here


@app.command("run_old")
def app_run_old(
    sha: Optional[str] = typer.Option(None, "--sha-hash", "-h"),
    app_dir: Optional[str] = typer.Option(None, "--app-dir", "-d"),
    source_repo: Optional[str] = typer.Option(None, "--source-repo", "-s"),
    target_repo: Optional[str] = typer.Option(None, "--target-repo", "-t"),
    # --all option
):
    """
    Running without any parameters loads context from a config file which is good for testing or having presets for a particular repo

    However a typical mode is to send parameters in a workflow and in that context we configure the source and target repo in the runner
    and then we pass the app job as json

    The sha/hash is passed into any job for labeling images
    """

    # try not to require a job. the data should be in source control and nowhere else - we just to point to the location
    # if job:
    #     job = json_loads(job)
    #     logger.info(f"Loaded job {job}")

    config = UnderpinConfig(
        CONFIG_HOME, source_repo=source_repo, target_repo=target_repo
    )

    """
    the default pipeline could be swapped for other pipelines in future 
    but it may be we only need one pipeline and managed templates
    """
    pipeline = DefaultPipeline(config)

    target = GitContext(config.target_repo, cwd=UNDERPIN_GIT_ROOT)
    # running from scratch - generate the branch for the target
    target.ensure_on_branch(sha)
    # TODO verify target branch is correct e.g. not main

    # first validate the app dir that is passed in - its either an app or current working dir
    if not GitContext(config.source_repo, cwd=app_dir).is_valid:
        # if that is not valid, which will be the case for containerized contexts, then check the mount
        if GitContext(config.source_repo, cwd=UNDERPIN_MOUNTED_SOURCE_DIR).is_valid:
            app_dir = UNDERPIN_MOUNTED_SOURCE_DIR
        else:
            raise Exception(
                "No valid app context - must operate from or mount the source repository that was configured"
            )

    # the normal context is to just pass an empty or valid app dir but its assumed its the source
    with GitContext(config.source_repo, cwd=app_dir) as g:
        changes = g.get_changes()
        logger.debug(f"changed files {changes}")
        pipeline(changes)  # or --all

    # we do not necessarily added until just before commit but this is good for change tracing after each step
    additions = target.add_all()
    logger.debug(f"Added target changes {additions}")


@app.command("test")
def app_run_test(
    sha: Optional[str] = typer.Option(None, "--sha-hash", "-h"),
    app_dir: Optional[str] = typer.Option(None, "--app-dir", "-d"),
    source_repo: Optional[str] = typer.Option(None, "--source-repo", "-s"),
    target_repo: Optional[str] = typer.Option(None, "--target-repo", "-t"),
    # --all option
):
    config = UnderpinConfig(
        CONFIG_HOME, source_repo=source_repo, target_repo=target_repo
    )

    ctx = GitContext(config.source_repo, cwd=app_dir)

    logger.debug(ctx)

    logger.info(ctx.is_valid)


if __name__ == "__main__":
    app()

# TODO
# Test adding build actions
# Test final validation:> we should get the properly modules in the cloud stack and kustomize should tell us if it is ok. Also Validate the PR that was pushed since it get into some bad states

# 1. test the different home contexts with mounts [run from ., run from lib elsewhere, run from env var]
# 2. test the ssh keys - test mounting and push
# 3. run as a workflow
# 4. test the template locations - we can load from underpinnings in source or target
# 5. test the actual deployment manifests that are generated
# 6.
