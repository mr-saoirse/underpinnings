"""
This is a crude adapter - it is interesting to think where these adapters would live 
they are ways to template standard objects with some opinionated bits
the best thing might be to add them as underpinnings in the source repo
but we can some defaults here
"""


def make_deployment(template):
    # something needs to sanitize variables
    return f"""
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../module

commonAnnotations:
    underpinnings.io/app: {template.namespace}-{template.name}

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


# make_knative

# make workflow type

#
