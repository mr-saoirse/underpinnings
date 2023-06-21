from .GitContext import GitContext
from pathlib import Path
import subprocess
from warnings import warn
from ..io import write

def clone(repo, branch=None, out_dir=None):
    """
    clones into target output dir
    if the dir is empty it should be deleted first or we can go in and fetch??
    this is supposed to be run in a K8s ephemeral pod normally


    #write state to /.underpin/.checkoutstate

    
    """
    out_dir = out_dir or f"{Path.home()}/.underpin/cloned/"
    options = ['git', 'clone', repo, out_dir]

    #normally we want to clone a specific branch which contains changes of interest under the apps
    if branch:
        options =  ['git', 'clone', '-b', branch, repo, out_dir]

    process = subprocess.Popen(options, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if not process.stdout.read():
        warn(process.stderr.read())
        return False

    return True


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
    file_changes = []

    write({
        'file_changes' : file_changes
    }, f"{Path.home()}/.underpin/.state.changed_files.yaml")

    return file_changes