import pytest
from underpin.utils.git import GitContext
from underpin import UNDERPIN_GIT_ROOT, logger


def test_gitcontext_switch_branch():
    pass


def test_gitcontext_alt_branch():
    pass


def test_gitcontext_init_source_clone():
    with GitContext(
        "git@github.com:mr-saoirse/underpinnings.git",
        branch=None,
        cwd=UNDERPIN_GIT_ROOT,
    ) as g:
        logger.info("expecting to clone into the underpin")


def test_gitcontext_init_source():
    with GitContext("git@github.com:mr-saoirse/underpinnings.git", branch=None) as g:
        logger.info(
            "expecting to use the current branch - check underpin branch and and repo"
        )
        logger.info(f"{g.current_repo}, {g.current_branch}")

        assert (
            g._repo_name == "underpinnings"
        ), f"the repo name is not as expected - {g._repo_name} != underpinnings"


def test_gitcontext_init_source_sub_folder():
    with GitContext(
        "git@github.com:mr-saoirse/underpinnings.git", cwd="./apps/", branch=None
    ) as g:
        logger.info(
            "expecting to use the current branch - check underpin branch and and repo"
        )
        logger.info(f"{g.current_repo}, {g.current_branch}")

        assert (
            g._repo_name == "underpinnings"
        ), f"the repo name is not as expected - {g._repo_name} != underpinnings"


def test_gitcontext_init_source_clone_and_init():
    with GitContext(
        "git@github.com:mr-saoirse/underpinnings.git",
        branch=None,
        cwd=UNDERPIN_GIT_ROOT,
    ) as g:
        logger.info("expecting to clone into the underpin")
        # clones in enter - enter will always drop down into the repo if it can

    # # ^ having ensure we have git for source in underpin which we only do for testing
    with GitContext(
        "git@github.com:mr-saoirse/underpinnings.git",
        branch=None,
        cwd=UNDERPIN_GIT_ROOT,
    ) as g:
        logger.info(
            "Expecting as per first test except different dir, everything should work"
        )
        assert (
            g._repo_name == "underpinnings"
        ), f"the repo name is not as expected - {g._repo_name} != underpinnings"


def test_gitcontext_checkout_target_main_branch():
    with GitContext(
        "git@github.com:mr-saoirse/cloud-stack.git",
        branch=None,
        cwd=UNDERPIN_GIT_ROOT,
    ) as g:
        logger.info("expecting to clone into the underpin")
        # clones in enter - enter will always drop down into the repo if it can


def test_gitcontext_checkout_target_switch_branch():
    with GitContext(
        "git@github.com:mr-saoirse/cloud-stack.git",
        branch="test",
        cwd=UNDERPIN_GIT_ROOT,
    ) as g:
        logger.info("expecting to clone into the underpin")
        # clones in enter - enter will always drop down into the repo if it can
