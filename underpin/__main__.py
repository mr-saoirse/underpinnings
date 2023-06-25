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


app = typer.Typer()

template_app = typer.Typer()
app.add_typer(template_app, name="template")

infra_app = typer.Typer()
app.add_typer(infra_app, name="infra")


build_app = typer.Typer()
app.add_typer(build_app, name="build")


@build_app.command("containers")
def build_app_containers(
    config_file: Optional[str] = typer.Option(None, "--config", "-c"),
    dir: Optional[str] = typer.Option(None, "--dir", "-d"),
    **kwargs,
):
    config = UnderpinConfig(config_file or CONFIG_HOME)

    # iterate app actions or use just one app if dir is specified

    #


@build_app.command("kustomize")
def build_app_update(
    config_file: Optional[str] = typer.Option(None, "--config", "-c"),
    dir: Optional[str] = typer.Option(None, "--dir", "-d"),
):
    config = UnderpinConfig(config_file or CONFIG_HOME)

    target = GitContext(config.target_repo, cwd=UNDERPIN_GIT_ROOT)
    changes = target.get_changes()
    logger.info(changes)

    # not sure if we need this - can we tag with the image we are going to build and be done it
    # iterate app actions or use just one app if dir is specified
    # run_command("kustomize set-image {action.kustomization.image}")


@infra_app.command("update")
def infra_app_update(
    config_file: Optional[str] = typer.Option(None, "--config", "-c"),
    dir: Optional[str] = typer.Option(None, "--dir", "-d"),
    pins: Optional[str] = typer.Option(None, "--pinnings", "-p"),
    **kwargs,
):
    """
    we can provide a config source for how the image tags are to be updated
    run kustomize on all
    and commit the repo
    """
    config = UnderpinConfig(config_file or CONFIG_HOME)

    # templates.update_images(pins)

    # get the underpin report which will also be archived somewhere
    app_actions = []

    target = GitContext(config.target_repo, cwd=UNDERPIN_GIT_ROOT)

    return target.merge(
        pr_change_note=generate_markdown_table(app_actions, "Applied Underpin Actions")
    )


@template_app.command("create")
def template_app_validate(
    name: Optional[str] = typer.Option(None, "--name", "-n"),
):
    pass


@app.command("init")
def app_init(
    target_branch: Optional[str] = typer.Option(None, "--target_branch", "-b"),
    target_local_dir: Optional[str] = typer.Option(None, "--target_out_dir", "-o"),
    **kwargs,
):
    """
    underpin generates a target repo away from the current repo to write files into and commit
    the target branch can be auto-generated with a hash in practice
    """

    # TODO: if branch exists handle this case properly

    if not Path(CONFIG_HOME).is_file():
        UnderpinConfig.configure()

    config = UnderpinConfig(CONFIG_HOME)
    target_branch = target_branch or "bot.add_manifests"
    logger.debug(config._data)

    with GitContext(config.target_repo, cwd=UNDERPIN_GIT_ROOT) as g:
        g.create_branch(target_branch)
        logger.info(f"create target repo to {g}")
        # if we need to do anything to the target we can here


@app.command("run")
def app_run(
    sha: Optional[str] = typer.Option(None, "--sha-hash", "-h"),
    job: Optional[str] = typer.Option(None, "--job", "-j"),
    source_dir: Optional[str] = typer.Option(None, "--source-dir", "-d"),
    source_repo: Optional[str] = typer.Option(None, "--source-repo", "-s"),
    target_repo: Optional[str] = typer.Option(None, "--target-repo", "-t"),
):
    """
    Running without any parameters loads context from a config file which is good for testing or having presets for a particular repo

    However a typical mode is to send parameters in a workflow and in that context we configure the source and target repo in the runner
    and then we pass the app job as json

    The sha/hash is passed into any job for labeling images

    """

    if job:
        job = json_loads(job)
        logger.info(f"Loaded job {job}")

    config = UnderpinConfig(
        CONFIG_HOME, source_repo=source_repo, target_repo=target_repo
    )

    """
    the default pipeline could be swapped for other pipelines in future 
    but it may be we only need one pipeline and managed templates
    """
    pipeline = DefaultPipeline(config)

    target = GitContext(config.target_repo, cwd=UNDERPIN_GIT_ROOT)
    # TODO verify target branch is correct e.g. not main

    with GitContext(config.source_repo, cwd=source_dir) as g:
        changes = g.get_changes()
        logger.debug(f"changed files {changes}")
        pipeline(changes)

    # we do not necessarily added until just before commit but this is good for change tracing after each step
    additions = target.add_all()
    logger.debug(f"Added target changes {additions}")


if __name__ == "__main__":
    app()

# TODO
# Test adding build actions
# Test final validation:> we should get the properly modules in the cloud stack and kustomize should tell us if it is ok. Also Validate the PR that was pushed since it get into some bad states
