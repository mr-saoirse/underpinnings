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
from typing import Optional
from pydantic import Field, root_validator
from . import yaml_templates
from underpin.utils.k8s import coerce_kubernetes_name


def dispatcher(uri, config=None):
    logger.info(f"Inspecting {uri}")
    contents = list(glob(f"{uri}/*"))

    if len(contents) == 1 and Path(contents[0]).name == "underpin.yaml":
        return UnderpinTemplate.build(uri)

    """
    inspects the contents of a folder and builds a template handler
    this will use some conventions and can improve in future

    - under underpin.yaml this takes precedence and underpinnings controls
    - else if Dockerfile, its built and use when creating manifests for this app
    - if requirements they are added to any generated dockerfile
    - if there is a python file(s) they are copied to any generated dockerfile and a main.py is used as an entry point unless configured or any sole file is used as entry point
    - a dockerfile reference is generated with build hash - it is used in any kustomization file
    - for bentoml the output of the build step will be the dockerfile:> not here we are generating a knative app and we just need the build output

    - copy or generate docker file -> register build step and handler for image build callback -> generate manifests or copy manifests -> update kustomize to point to docker image/hash

    - it may be that we record all kustomize or image references and then at the final stage of the pipeline we re-write all the kustomizations - for now we leave a reference to a unique app image
      leave these under /.underpin/app-cache/fqn-name/config.yaml

      we may add transformers to templates for mapping between templates
    """
    pass


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
        return UnderpinTemplate(**read(underpin_config), name=app_name)

    def write(self, dir):
        """
        for each manifest write to outdir
        write the config of the templating process to /apps-cache
        """
        logger.info(f"Writing files to {dir}")
        self.write_dockerfile(dir)
        self.write_kustomizefile(dir)
        self.write_action(dir)

    def write_dockerfile(self, dir):
        pass

    def write_kustomizefile(self, dir):
        write(yaml_templates.make_deployment(self), f"{dir}/kustomization.yaml")

    def write_dockerfile(self, dir):
        pass

    def write_action(self, dir):
        write(
            {
                "build": [
                    {"type": "docker", "image": self.image},
                    {"type": "kustomization", "path": f"{dir}/kustomization.yaml"},
                ]
            },
            f"{dir}/actions.yaml",
        )


# move these other ones to their own files later
class UnderpinDockerizedAppTemplate(UnderpinTemplate):
    """
    this template copies anything containing a docker file and instigates a build process and updates manifests
    """

    pass


class UnderpinKubernetesAppTemplate(UnderpinTemplate):
    """
    this template copies verbatim anything recognized or assumed to be helm or kustomized or plain K8s
    """

    pass


class UnderpinBentoMLAppTemplate(UnderpinTemplate):
    """
    this template manages anything with a bentoml file and instigates a BentoML build process
    - simply templates a knative app
    - needs the output of a build step to kustomize the knative app
    """

    pass
