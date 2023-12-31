import yaml
from pathlib import Path
from underpin import logger, CONFIG_HOME, UNDERPIN_APP_ROOT, UNDERPIN_GIT_ROOT
from underpin.utils.io import write


def _config_template_simple(source, target, image=None):
    return {
        "version": "underpin.io/alpha1",
        "metadata": {"namespace": "default", "source-root": "samples"},
        "repos": {"source": source, "target": target},
    }


class UnderpinConfig:
    def __init__(self, uri: str, source_repo=None, target_repo=None) -> None:
        self._data = {}
        # todo test s3://

        if not Path(uri).is_file() and source_repo is not None:
            UnderpinConfig.configure(source_repo=source_repo, target_repo=target_repo)
        with open(uri) as f:
            self._data = yaml.safe_load(f)
        if "repos" not in self._data:
            self._data["repos"] = {}
            self._data["metadata"] = {"source_root": UNDERPIN_APP_ROOT}

        if source_repo:
            self._data["source"] = source_repo
        if target_repo:
            self._data["target"] = source_repo

        if not Path(UNDERPIN_GIT_ROOT):
            logger.debug(f"Ensuring the git root exists at {UNDERPIN_GIT_ROOT}")
            Path(UNDERPIN_GIT_ROOT).mkdir(exist_ok=True)
        # rewrite config

    @staticmethod
    def configure(source_repo=None, target_repo=None):
        logger.info(
            "Environment needs to be configured. Enter or pass in the source and target git repos below..."
        )
        s = source_repo or input("Source repo:")
        t = target_repo or input("Target repo:")

        if s and t:
            logger.info(f"Writing to {CONFIG_HOME}")
            Path(CONFIG_HOME).parent.mkdir(exist_ok=True, parents=True)
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
        prefix = self._data.get("metadata", {}).get("source-root", "apps")
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
