"""
This is a crude adapter - it is interesting to think where these adapters would live 
they are ways to template standard objects with some opinionated bits
the best thing might be to add them as underpinnings in the source repo
but we can some defaults here
"""

# TODO annotations e.g. to support things like otel or whatever


def make_knative(template):
    """
    THE KNATIVE TEMPLATE
    Many of these templates should have a general common form with custom patches so we should to this a bit more intelligently
    """
    return f"""
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../module

commonAnnotations:
    underpin.io/app: {template.namespace}-{template.name}

namePrefix: {template.name}-
namespace: {template.namespace}

images:
- name: {template.image}
  newTag: "{template.tag}"
"""


def make_deployment(template):
    """
    THE DEPLOYMENT TEMPLATE
    Many of these templates should have a general common form with custom patches so we should to this a bit more intelligently
    """
    return f"""
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../module

commonAnnotations:
    underpin.io/app: {template.namespace}-{template.name}

namePrefix: {template.name}-
namespace: {template.namespace}

patches:
- target:
   kind: Service
  patch: |-
    - op: replace
        path: /spec/selector/app
        value: {template.name}-{template.module}
- target:
   kind: Deployment
  patch: |-
    - op: replace
        path: /spec/template/spec/containers/0/resources/requests/memory
        value: {template.memory}

images:
- name: {template.image}
  newTag: "{template.tag}"
"""


def make_argo_simple_workflow(template):
    """
    THE ARGO WORKFLOW SIMPLE JOB TEMPLATE
    Many of these templates should have a general common form with custom patches so we should to this a bit more intelligently
    """
    return f"""
    """
