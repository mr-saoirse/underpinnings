from ..config import UnderpinConfig
from .. import templates
from underpin import logger


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

        for app_source in self.config.match_app_changes(changes):
            logger.info(f"Processing app:> {app_source}")
            # generate uses the underline template generator to generate a set
            # which has write function to write all files to the target repo
            # templates.generate(app_source, self.context).write(self.config.target_repo)

    def __call__(self, changes, **kwargs):
        return self.run(changes, **kwargs)
