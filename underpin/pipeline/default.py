from ..config import UnderpinConfig
from ..utils.git import GitContext
from .. import templates

class DefaultPipeline:

    def __init__(self, config: UnderpinConfig) -> None:
        self.config = config


    def run(self, changes, **kwargs):
        """
        this simplest of pipelines will use the context to determine how to copy templates from a source
        and write them into the target location in the checkout repo following some conventions
        the git context ensure that we create a new branch for this session and then commits and merges the PR
        this results in manifests being written
        """

        #this checks out a branch and may do some clean up after
        with GitContext(self.config) as git:
            for app_source in changes:
                #generate uses the underline template generator to generate a set
                #which has write function to write all files to the target repo
                templates.generate(app_source, self.context).write(self.config.target_repo)

            git.merge()


    def __call__(self, changes, **kwargs):
        return self.run(changes, **kwargs)
