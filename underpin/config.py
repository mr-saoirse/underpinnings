import yaml
from pathlib import Path
from underpin import logger, CONFIG_HOME
from underpin.utils.io import write


def _config_template_simple(source, target, image=None):
    return {
        "version": "underpin.io/alpha1",
        "metadata": {"namespace": "default", "source-root": "samples"},
        "repos": {"source": source, "target": target},
    }


class UnderpinConfig:
    def __init__(self, uri: str) -> None:
        self._data = {}
        # todo test s3://
        with open(uri) as f:
            self._data = yaml.safe_load(f)

    @staticmethod
    def configure():
        logger.info(
            "Environment needs to be configured. Enter the source and target git repos below..."
        )
        s = input("Source repo:")
        t = input("Target repo:")

        if s and t:
            write(_config_template_simple(s, t), CONFIG_HOME)

    def __getitem__(self, key: str):
        return self._data.get(key)

    def items(self):
        return self._data.items()

    def match_app_changes(self, changes):
        prefix = self.app_root

        # TODO: this should be much better and agnostic to patterns of /. A generalized configuration schema is needed here at the system level (UTEST)
        changes = [
            c for c in changes if prefix in c and f"{prefix}/" == c[: len(f"{prefix}/")]
        ]
        changes = set([str(Path(c).parent) for c in changes if Path(c).is_file()])

        return changes

    @property
    def app_root(self):
        prefix = self._data.get("metadata", {}).get("source-root")
        return prefix

    @property
    def source_repo(self):
        # TODO: safety
        return self["repos"]["source"]

    @property
    def source_repo_name(self):
        return Path(self.source_repo).name.split(".")[0]

    @property
    def target_repo(self):
        return self["repos"]["target"]

    @property
    def target_repo_name(self):
        return Path(self.target_repo).name.split(".")[0]
