import yaml
from pathlib import Path


class UnderpinConfig:
    def __init__(self, uri: str) -> None:
        self._data = {}
        # todo test s3://
        with open(uri) as f:
            self._data = yaml.safe_load(f)

    def __getitem__(self, key: str):
        return self._data.get(key)

    def items(self):
        return self._data.items()

    def match_app_changes(self, changes):
        prefix = self._data.get("metadata", {}).get("source-root")

        return [c for c in changes if prefix in c] if prefix else changes

    @property
    def source_repo(self):
        # TODO: safey
        return self["repos"]["source"]

    # def get_source_repo_local_dir(self, create=True):
    #     """
    #     for now a default convention is used but this can be configured in other ways
    #     """
    #     uri = f"{Path.home()}/.underpin/{Path(self.source_repo).name}"
    #     if not Path(uri).exists():
    #         Path(uri).mkdir(parents=True, exist_ok=True)

    #     return uri
