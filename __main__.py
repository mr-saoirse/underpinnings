import typer
from typing import Optional
from pathlib import Path
from underpin.config import UnderpinConfig
from underpin.pipeline.default import DefaultPipeline
from underpin.utils import io
from underpin import schema
from underpin.utils.git import GitContext
from underpin.schema import ChangeSet
from underpin import logger

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
    source_local_dir: Optional[str] = typer.Option(None, "--source_out_dir", "-o"),
    source_branch: Optional[str] = typer.Option(None, "--source_branch", "-b"),
):
    """
    Either clone a branch, checkout a branch or point to a checked out local branch
    source local uses ./underpin by default
    the source branch is recommended but we can fetch the master branch for testing
     or if we want to use it but get the changes based on the diff with the ref branch
    when the repo exists we automatically try to switch to the branch in the local location or complain
    we should diff the remote to see if there are changes that need to be pulled with our local branch (master or feature)
    all of this can be done in the clone op to make sure we know both the changes and the source code

    """

    # purge-state option

    config = UnderpinConfig("config/config.yaml")

    logger.info(config._data)

    # change this to use a git context with options and checkout the feature (or main branch as required)
    # but conscious of getting the change set by some means which is one of the main purposes - often the rebased app with master is where the manifest will come from
    # checkout function is used only to test
    # logger.info(checkout(config.source_repo, source_branch, source_local_dir))
    with GitContext(config.source_repo, branch="sa.test_branch") as g:
        changes = g.changed_files
        matched_changes = config.match_app_changes(changes)
        logger.info(matched_changes)


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

    change_set = None
    if change_set_file:
        change_set = io.read(change_set_file, type=schema.ChangeSet)
    else:
        """
        we expect that the source is not on master and that the changes are based on the feature branch changes
        but if the context did not specify a branch then we cannot determine these changes and we need another mode,
        a mode that specifies the changes to migrate - usually this should be just for testing that we do this
        """
        change_set = ChangeSet.from_file_change_set(
            app_changes(config.local_target_repo)
        )

    pipeline(change_set)


if __name__ == "__main__":
    app()
