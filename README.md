# Underpinnings

Underpinnings is an experimental utility for translating between infrastructure K8s Repos and the user application repos that rely on them. What does that even me though?
This represents a separation of concerns between a managed cluster (probably managed by people who care about how Kubernetes works) and people who just want to deploy into that infrastructure in a sort of X as a Service fashion.
The trouble is that within a given org that manages its own infrastructure the boundaries tend to blur. Underpinnings tries, in an opinionated way, to separate those concerns clearly with some patterns. It focuses on two things

- Managing (docker) versions in microservice environments (pinnings)
- Managing template abstractions (DSL to K8s conversions)

Ultimately this allows for the generation of manifests related to apps in one repo to be sent to another repo (Managed by Argo CD). As such, it takes one very specific and often messy task within an entire CI/CD pipeline and puts some scaffolding around it.


# How to use it

Install it with homebrew or pip and run `underpin scaffold <my-cloud>`. You will be asked to specify
- source repo
- target repo  
- aws key (only tested for AWS for now)
- OPEN AI key (optional)

If you want to get the cluster stack you can clone it. Part of this is creating a management cluster.
If you want to generate a cluster, a Pulumi up command can be used  to generate a cluster on AWS but it is expected (recommended) that you already have a cluster.
If you do generate a cluster or bring your own, it simply needs ArgoCD to be installed. 
Once you have a cluster, you can then  use the cloned stack repository to add other things but that is entirely optional. 

- If you look at the sample cluster, it is assumed there is an app-manifests folder in your target repo. You can configure that through an environment variable to be any folder name or override it when submitting commands.
- Underpinnings can take jobs and build apps that get pushed to your management cluster. You can test this wth the cli but usually this will run as a workflow on your management cluster. 
- here is a sample command
```
underpin template path/my-namespace/my-app 
```

What does this do? it will check out a branch with some hash on the target repo and write manifests into the target repo in that branc. there are options for branch name, plan only etc etc. but lets follow the normal path.
If we say --commit it will also commit the change on the master branch otherwise can get the branch hash that was returned and call 
```
underpin commit hash
```

Now if we look at what happened it might seem strange. Why we (a) template something that would be templated with K or H anyway and then essentially move something from one repo to another? We answering the second part, this is supposed to be part of a build process where we move something from an app repo to an infra repo.
The second part is an abstraction that underpinnings introduces to intercept app builds to build specifically in different ways and to intercept templating both of which are treated as a specific concern. This enables "values only" apps

an underpinnings values file looks like this

```
version:
metadata:
  namespace:
  name:
repos: 
  source:
  target:
module:
image: 
resources:
    memory:
    storage:
conf:
  takes a custom format/spec per module and can be anything. this would be how you choose a different storage class for example
```

# launch the api
Underpinnings runs in different ways, locally or on cluster. There is a swagger endpoint (knative or Fast API) which is used to receive jobs. You can also ask basic questions about the status of apps. The current version is very crude and just uses blob storage to store data.

## After the basic setup
You now have a CLI, a management cluster and a scaffolded cluster project that you can configure. The cluster manifests is simply a clone of this which is for bootstrapping a standard cluster with observability stack.
One of the applications is the underpinnings workflow. 


TODO
- postgres instance for some data
- 
 



