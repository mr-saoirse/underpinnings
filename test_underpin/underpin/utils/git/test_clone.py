"""
The purpose of the clone tests is to always know what changes were being proposed on a branch at any moment in time
for this we need to get the diff with that branch and the main branch at that revision

KEY POINT
we have a desired state we want to be in and we test that we can arrive at that state from any state
the state is the be checked out on the source branch locally
we also want to know what are/were the changes being proposed by that branch at the time it was merged if was merged Or now with the main branch
after we determine the change set, we want to know what the rebase version of the app looks like and template it
"""

import pytest


def test_clone_current_unmerged():
    pass


def test_clone_current_just_merged():
    pass


def test_clone_current_merged_old_branch():
    pass
