"""
templates provide a declarative way to describe transformations so they start as Pydnatic types that wrap some config
these are ultimately expanded into into other files until they becomes K8s manifests or Dockerfiles
they can only be constructed as pydantic objects but they have processing logic
"""

from pydantic import BaseModel
from pathlib import Path
from glob import glob
from underpin import logger
from underpin.utils.io import read, write
from typing import Optional, Union
from pydantic import Field, root_validator
from underpin.templates import template_containers, template_yaml
from underpin.utils import coerce_kubernetes_name
import shutil


def dispatcher(uri, config=None):
    logger.info(f"Inspecting {uri}")
    contents = list(glob(f"{uri}/*"))

    if Path(contents[0]).name == "underpin.yaml":
        # if there is a docker file in here we can write it out and create an action
        # if there is an underpin we can always handle if the thing is valid
        return UnderpinTemplate.build(uri)

    if "bentofile.yaml" in contents:
        # TODO
        return UnderpinBentoMLAppTemplate(uri)

    if "kustomize.yaml" in contents:
        # TODO
        return UnderpinKubernetesAppTemplate(uri)

    if "Dockerfile" not in contents:
        # there may need to be another aspect of this - gray area
        return UnderpinDockerizeAppTemplate(uri)

    return UnderpinKubernetesAppTemplate(uri)


class UnderpinTemplate(BaseModel):
    """
    this is the most raw template and can use an underpin.yaml file to infer from config
    if there is a python file it is package on a app dockerfile
    if there are requirements they are written into the dockerfile
    the base of the dockerfile is assumed to be based on the repo wide docker image unless another image is specified

    module: deployment
    #image: testing
    resources:
    memory: 10G
    storage: 1G
    conf: {}

    """

    module: str
    name: str
    source_uri: str
    image: Optional[str] = Field(default="underpin.docker.something")
    namespace: Optional[str] = Field(default="default")
    memory: Optional[str] = Field(default="1Gi")
    storage: Optional[str] = Field(default="1G")
    conf: dict = Field(default_factory=dict)
    tag: Optional[str] = Field(default="latest")

    @root_validator
    def k8s(cls, values):
        values["module"] = coerce_kubernetes_name(values["module"])
        values["name"] = coerce_kubernetes_name(values["name"])
        values["namespace"] = coerce_kubernetes_name(values["namespace"])

        return values

    @staticmethod
    def build(uri):
        contents = list(glob(f"{uri}/*"))
        underpin_config = contents[0]
        # convention to name the app based on the tail
        app_name = str(Path(uri).parts[-1])
        return UnderpinTemplate(**read(underpin_config), name=app_name, source_uri=uri)

    def write(self, dir):
        """
        for each manifest write to outdir
        write the config of the templating process to /apps-cache
        """
        logger.info(f"Writing files to {dir}")

        self.write_dockerfile(dir)
        self.write_kustomizefile(dir)
        self.write_action(dir)
        self.copy_other(dir)

    def copy_other(self, dir):
        pass

    def write_kustomizefile(self, dir):
        write(template_yaml.make_deployment(self), f"{dir}/kustomization.yaml")

    def write_dockerfile(self, dir):
        # if app has docker file copy it by default - otherwise subclass could generate one
        if "Dockerfile" in list(glob(dir)):
            shutil.copy(f"{self.source_uri}/Dockerfile", dir)

    def write_action(self, dir):
        # these actions are actually need configuration because base class may have a different actions
        write(
            {
                "build": [
                    {"type": "docker", "image": self.image},
                    # {"type": "kustomization", "path": f"{dir}/kustomization.yaml"},
                ]
            },
            f"{dir}/.underpin/actions.yaml",
            True,
        )


# move these other ones to their own files later
class UnderpinDockerizeAppTemplate(UnderpinTemplate):
    """
    this template copies anything containing a docker file and instigates a build process and updates manifests
    """

    def write_dockerfile(self, dir):
        # if app has docker file copy it by default - otherwise subclass could generate one
        entry_point = None
        write(
            template_containers.docker_default(
                self, self.source_uri, entry_point=entry_point
            ),
            f"{dir}/kustomization.yaml",
        )


class UnderpinKubernetesAppTemplate(UnderpinTemplate):
    """
    this template copies verbatim anything recognized or assumed to be helm or kustomized or plain K8s
    """

    def copy_other(self, dir):
        shutil.copytree(self.source_uri, dir)


class KnativeAppTemplate(UnderpinKubernetesAppTemplate):
    """
    this template manages anything with a bentoml file and instigates a BentoML build process
    - simply templates a knative app
    - needs the output of a build step to kustomize the knative app
    """

    def write_kustomizefile(self, dir):
        write(template_yaml.make_knative(self), f"{dir}/kustomization.yaml")


class UnderpinBentoMLAppTemplate(KnativeAppTemplate):
    """
    this template manages anything with a bentoml file and instigates a BentoML build process
    - simply templates a knative app
    - needs the output of a build step to kustomize the knative app
    """

    def write_action(self, dir):
        """
        Bentoml needs a specific build action
        """
        write(
            {
                "build": [
                    {"type": "bentoml", "image": self.image},
                ]
            },
            f"{dir}/.underpin/actions.yaml",
            True,
        )
