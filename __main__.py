import typer
from typing import Optional
from pathlib import Path
from underpin.config import UnderpinConfig
from underpin.pipeline.default import DefaultPipeline
from underpin.utils import io
from underpin import schema
from underpin.utils.git import GitContext, app_changes
from underpin.schema import ChangeSet
from underpin import logger, UNDERPIN_GIT_ROOT
import os

app = typer.Typer()

template_app = typer.Typer()
app.add_typer(template_app, name="template")


@template_app.command("create")
def template_app_validate(
    name: Optional[str] = typer.Option(None, "--name", "-n"),
):
    pass


@app.command("init")
def app_init(
    target_branch: Optional[str] = typer.Option(None, "--target_branch", "-b"),
    target_local_dir: Optional[str] = typer.Option(None, "--target_out_dir", "-o"),
):
    """
    underpin generates a target repo away from the current repo to write files into and commit
    the target branch can be auto-generated with a hash in practice
    """

    config = UnderpinConfig("config/config.yaml")
    target_branch = target_branch or "bot.add_manifests"
    logger.info(config._data)

    with GitContext(config.target_repo, cwd=UNDERPIN_GIT_ROOT) as g:
        g.create_branch(target_branch)
        logger.info(f"create target repo to {g}")
        # if we need to do anything to the target we can here


@app.command("run")
def app_run(
    sha: Optional[str] = typer.Option(None, "--sha_hash", "-h"),
    change_set_file: Optional[str] = typer.Option(None, "--file", "-f"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c"),
):
    """
    we can get a change set from input or the branch and process all apps
    a config file can be passed in order used from the one in the module
    sha hash is used for the entire build context
    """
    config = UnderpinConfig(config_file or "config/config.yaml")
    """
    the default pipeline could be swapped for other pipelines in future 
    but it may be we only need one pipeline and managed templates
    """
    pipeline = DefaultPipeline(config)

    target = GitContext(config.target_repo, cwd=UNDERPIN_GIT_ROOT)

    with GitContext(config.source_repo) as g:
        changes = g.get_changed_files()
        logger.debug(f"changed files {changes}")
        pipeline(changes)
        target.merge()


if __name__ == "__main__":
    app()
