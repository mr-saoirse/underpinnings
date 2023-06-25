# Underpinnings

Underpinnings is an experimental utility to explore a two-repo pattern for migrating templated apps from an "applications" repo to a K8s "infrastructure" repo.

Infrastructure repos (IRepos) are managed by Dev Ops people or people that are keen to dive into the management of K8s clusters while applications repos (ARepos) are the realm of application developers who build many applications (on many docker images).
Microservices systems lead to a profusion of apps and docker images that need to be managed and deployed into Kubernetes infrastructure. Application developers typically do not care about the details of how things are deployed once they have the resources they need to run their applications.
There are of course many engineers who are happy to work in either space and indeed many teams have arrived at good solutions to manage these environments.


Underpinnings takes the perspective that special tooling could be useful sitting between ARepos and IRepos and that some patterns and abstractions are worth thinking about. 
- How to create a separation of concerns between I and A
- How to create abstract and simple application templates that can be translated into Kubernetes applications
- How to manage docker and other container builds and their versions when mapping between A and I

## Usage

Underpinning creates a target repo for infrastructure. It is useful to think of underpinning running in the context of the source or ARepo, either inline in the repo are as part of builds, building the ARepo. Then the target repo has its own Git Context managed by underpin as a conduit to send transfer manifests. 
Consider a basic config file

```yaml
version: underpin.io/alpha1
metadata:
  namespace: default
  source-root: samples
  app-uri: default/deployment
repos:
  source: git@github.com:mr-saoirse/underpinnings.git
  target: git@github.com:mr-saoirse/cloud-stack.git

```

Underpinnings will initialize the target repo into `~/.underpin/cloned/<target>`

```
underpin init
```

Then a pipeline can be run to generate all hydrated templates with

```
underpin run
```

which will translates applications under  `source-root: samples` and "hydrate" applications for K8s. There are some default templates in underpin or you additional ones can be added to the IRepo in `repo/.unpderpinnings`. These are adapters that convert simple values files into more complex K8s app templates.

Following this we build any docker images, update image manifests, write to the target IRepo and push. ArgoCD will then manage the applications in the IRepo, syncing to the cluster(s)

1. We build containers and determine tags
```
underpin build containers
```

2. We then tag manifests. However its assumed for simplicity that we can choose some super tag that we just write into the kustomize in the previous stage and we control the tags or SHA or whatever it is all docker images are re-pinned with for this build.
Allowing for other ways to get those tags is not hard its just unnecessary complexity for a PoC
```
#we dont need this really yet 
underpin build kustomize
```

3. We finally update the infra

```
underpin infra update
```


These steps can all be tested locally but the intent is these run in a CI/CD pipeline runner.

## running in the workflow

The above is for testing. In the workflow the following occurs
- we clone the ARepo
- we Build any master docker images in the ARepo
- we init the target IRepo on a volume 
- We fan out over changed apps with the parameters to process each app and write to the IRepo
  - we run `underpin run -n=<app-name> -o tmp/context/app/build`
  - we build the docker app from that /tmp/context location, which is a self-contained app  
     - this uses Kaniko as the build provider or Bentoml etc.
  - we set kustomize image on the app for whatever build context and image is needed
  - we copy to app target in the IRepo
- we fan in and merge the IRepo changes

## running as a GitHub action
### mode 1: trigger the workflow
In this mode, the cloud native in you may want to separate your build processes into something that can be run and tested on K8s. Alternatively see mode 2
In this first mode, we use an Argo Workflow that runs on our management cluster to build our ARepo and transfer the manifests into the IRepo. ArgoCD then takes these manifests and deploys them to all clusters under management.

### mode 2: run as inline action on app folders
In mode 2 we use just run underpin in a git action (which runs on a docker image). Here we need to pass app changes into the underpin step and it will transform and generate manifests that get pushed to the target repo (for all app changes). For each app we run all the steps above to generate templates, build containers and tag manifests. We push each app to the target IRepo.


### other commands

Following are some commands for interacting with the Applications repo which is considered the source.

```
#see what changes have been observed on the ARepo branch or in the context
underpin source --changes
#preview a template e..g all docker files and yaml files used for the app
underpin source template <app-name>  
```

Underpin also has a simple agent to helm with templating

```
underpin agent <>
```