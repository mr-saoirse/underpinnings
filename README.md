# Underpinnings

Underpinnings is an experimental utility to explore a two-repo pattern for migrating templated apps from an "applications" repo to a K8s "infrastructure" repo. To learn more see the [docs] but the following is a brief explanation:

Infrastructure repos (IRepos) are managed by Dev Ops people or people that are keen to dive into the management of K8s clusters while applications repos (ARepos) are the realm of application developers who build many applications (on many docker images).
Microservices systems lead to a profusion of apps and docker images that need to be managed and deployed into Kubernetes infrastructure. Application developers typically do not care about the details of how things are deployed once they have the resources they need to run their applications.
There are of course many engineers who are happy to work in either space and indeed many teams have arrived at good solutions to manage these environments.


Underpinnings takes the perspective that special tooling could be useful sitting between ARepos and IRepos and that some patterns and abstractions are worth thinking about. 
- How to create a separation of concerns between I and A
- How to create abstract and simple application templates that can be translated into Kubernetes applications
- How to manage docker and other container builds and their versions when mapping between A and I

## installation

```
pip install underpin

#run against your own ARepo (see docs for guidelines)
underpin run --app-dir <your local cloned apps> --target-repo <git-remote-repo>

#run using the sample defaults
underpin run --all
```
The result of this run is to write manifests into a new branch for the target repo. (SSH will be used if needed)  


For docker we can mount a local repo containing some apps or we can use the sample apps in the docker image (see notes below about changes and the `--all` flag). We should mount an ssh key if we want to push changes to a target but for testing template generation this is not necessary.

```
docker run underpinnings run --all -v ssh-stuff

#using mounts to check the target
docker run underpinnings run --all -v ssh-stuff, target repo mount

#using mounts to check the target and also use your own repo
docker run underpinnings run --all -v ssh-stuff, source-dir, target repo mount
```

To run underpin as a simple Argo Workflow, apply the sample one-step to your cluster and execute.

```
git clone <>
kubectl apply -f kubernetes/workflow/one-step.yaml
#submit workflow
```

---

Underpinning creates a target repo for infrastructure. It is useful to think of underpinning running in the context of the source or ARepo, either inline in the repo are as part of builds, building the ARepo. Then the target repo has its own Git Context managed by underpin as a conduit to send transfer manifests. 
Consider a basic config file. This can be set up to run underpin on changes in your local repo. It can be saved like this or running `underpin init` will create the context. This is simple an alternative to passing the arguments from above. In practice the arguments are more useful for running in Kubernetes.

```yaml
version: underpin.io/alpha1
metadata:
  namespace: default
  app-dir: samples
  app-uri: default/deployment
repos:
  source: git@github.com:mr-saoirse/underpinnings.git
  target: git@github.com:mr-saoirse/cloud-stack.git

```

Underpinnings will initialize the target repo into `home/.underpin/cloned/<target>`

 
A pipeline can be run to generate all hydrated templates with

```
underpin run
```

which will translates applications under  `app-dir: samples` and "hydrate" applications for K8s. There are some default templates in underpin or additional ones can be added to the IRepo in `repo/.unpderpinnings`. These are adapters that convert simple values files into more complex K8s app templates.

Following this we build any docker images, update image manifests, write to the target IRepo and push. ArgoCD will then manage the applications in the IRepo, syncing to the cluster(s). See the workflow for more details
After all images have been build, the manifests we generated with the run command (and saved in the checked out target repo) can be pushed up to the infra repo.


```
underpin infra update
```

These steps can all be tested locally but the intent is these run in a CI/CD pipeline runner (see the workflow)

## running in the workflow

The above is for testing. In the workflow the following occurs
- we clone the ARepo into `/app/`
- we build any master docker images in the ARepo
- we init the target IRepo on a volume `home/.underpin/cloned/<target>`
- We fan out over changed apps with the parameters to process each app and write to the IRepo
  - we run `underpin run -app-dir=<app-location>` - this will be tagged with a docker image that will be built or the master one we already built. Same hash used in either case. Outputs are added to the IRepo location.
  - we build the docker app from that /tmp/context location, which is a self-contained app  
     - this uses Kaniko as the build provider or Bentoml etc.
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


# Notes on convention
We lean on conventions to make the basic setup easy. The ARepo is assumed to be mounted to some folder `/app` or to be run in the current working directory. This is done so that the Docker or Kubernetes context require minimal initialization. For testing we normally run in `cwd` but for Docker or Kubernetes we will mount a volume. The apps are assumed to be under `app/apps` and indeed underpin reference projected stores all apps at `/apps` - these are apps that are intended to be templated and deployed. When running in the current working director, its assumed that directory is also a git repo and underpin will check if it is the source repo. As such the order of precedence is
- `app-dir` is checked and overrides any other values
- Executing from the current working directory which is a git repository that matches the configured source repository - there is a folder calls `/apps` or matching `UNDERPIN_APP_DIR` in this repository
- If there is not a current execution context that qualifies (including setting env), it is assumed that there is a repo that qualifies at `/app/` - there must be a folder called `/apps` within that app.
Otherwise the `--app-dir` must be set - or error

To use the Docker version, default parameters mean the sample app in the underpin project can be used to test the run command and generate manifests in the target repo. However, you can also mount another directory into `/app/apps` to replace the apps that underpin will operate on. In the Kubernetes setting, we also clone the ARepo into `/app` so by default it will operate on the source repo there. 

All of these conventions can be replaced with config files or parameters e.g `--app-dir` replaces where underpin will look for apps. For development setting `UNDERPIN_APP_DIR` will override the default. It is recommended setting this in .envrc in the home repo. 

The target repo is always created at initialization or runtime at `home/.underpin/cloned/<repo>` and SSH is used. As such, for docker or K8s we need to specify an SSH key - HTTPS authentication has not been tested.

Underpin requires changes on a branch by default to generate a change set. By adding `--all` to the run, all apps (under the conventional director discussed above) are templated. Actually this is just a testing utility because normally we would require a git context and realistic changes on some branch but to test locally or in Docker it is convenient to not require changes but still test the action of pushing templates into the target repo. 

Underpin always writes a job output file to `tmp/underpin/out.json` and this can be used by Argo Workflows. (check home dir instead)

## Underpinning templates

We store templates for module by type under the source repo in `.underpinnings/modules` for now. These are used by applications and we apply the Underpin template values to these templates to generate Kustomize files or Dockerfile or anything else in the target. They are suffixed with the template engine type and different templating engines can be used. The default is .py which is simple for our use case.

While this makes sense for development, the templates are actually owned by infrastructure (IRepo) and not the ARepo. In general, the applications will simply supply values to managed modules in the IRepo for manifests while Docker templates could still be owned in the ARepo. We could imagine some sort of merge strategy to use information from both source and target. This is all for future, for now we just work in the source repo.

