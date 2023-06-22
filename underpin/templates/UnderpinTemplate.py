"""
templates provide a declarative way to describe transformations so they start as Pydnatic types that wrap some config
these are ultimately expanded into into other files until they becomes K8s manifests or Dockerfiles
they can only be constructed as pydantic objects but they have processing logic
"""

from pydantic import BaseModel

def dispatcher(uri):
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

    """

    def write(self):
        """
        for each manifest write to outdir
        write the config of the templating process to /apps-cache
        """
        pass

    def write_dockerfile(self):
        pass

    def write_kustomizefile(self):
        pass

    def manifests(self):
        pass

#move these other ones to their own files later
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

