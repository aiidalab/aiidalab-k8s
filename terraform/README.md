# AiIDAlab Terraform Deploy

*Based on https://github.com/pangeo-data/terraform-deploy.*

## Introduction

This repository provides instructions and configuration files to create an AiiDAlab (JupyterHub)-ready kubernetes cluster on Amazon Web Services (AWS) infrastructure with [Terraform](https://www.terraform.io).

The guide to deploy this JupyterHub-ready infrastructure can be summarized as:
- Download Terraform, its dependencies, and the repository.
- Configure a few settings for the infrastructure and for the AWS CLI.
- Deploy the infrastructure using Terraform commands.

Important: This document describes how to create a kubernetes cluster suitable to deploy an instance of AiiDAlab.
After deploying the infrastructure, you still need to install AiiDAlab on the cluster.
For that, follow the instructions provided in the README.md file located at the root of this repository.

## Deployment Instructions

The following instructions were tested with:

 - Terraform v0.14.6
 - aws-cli/2.1.3 Python/3.7.3 Linux/5.4.0-60-generic exe/x86_64.ubuntu.18
 - kubectl v1.20
 - helm v.3.5.2

### Install Terraform, dependencies, and this GitHub repo

In order to deploy the configuration in this repo, you need to have the following tools installed within your environment:

- [Terraform](https://www.terraform.io/downloads.html)
- [AWS CLI](https://aws.amazon.com/cli/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Helm](https://helm.sh/docs/intro/install/)

You will also need to clone this repository, e.g., with:

```
git clone git@github.com:aiidalab/aiidalab-k8s.git
cd aiidalab-k8s/aws/terraform
```

### Configuration

#### Configure the AWS CLI

You need to have the `aws` CLI configured to run correctly from your local machine - terraform will just read from the same source.
The [documentation on configuring AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) should help.

The `aws-creds` configuration directory is used to setup a `terraform-bot` user that has exactly tailored permissions to setup the kubernetes infrastructure.
It is not strictly necessary to use the bot user to create the cluster, however it is recommended to follow the principle of least privilege and the following instructions are going to assume the use of the bot user.
By default (as in, what is uncommented), the folder will lead to the creation of a new user named `terraform-bot` with policy attachments for the minimal policy set and EFS permissions.
Those policies are defined in the `iam.tf` file.

If you want to create this user, go into `aws-creds/iam.tfvars` and make sure the value of `profile` is the correct awscli profile you want to use.
Then, run the following:

```
cd aws-creds
terraform init
terraform apply -var-file=iam.tfvars
```

Terraform will show the plan to create the IAM policy, an IAM user, and the attachment of two policies onto the user.
Confirm the apply command and Terraform will let you know when it's finished.

Note: The AWS profile used to execute this plan will require permisions to create new users, please review AWS documentation regarding the Identity and Access Management (IAM) in case of issues relating to lack of permissions.

You will then have to configure `terraform-bot`'s credentials in the AWS Console.
Go and generate access keys for the user, then put them into your command line with

```
aws configure --profile terraform-bot
```

Later, you will tell Terraform to use this profile when running commands so that it has only the permissions it needs when deploying the infrastructure.

#### Configure your Infrastructure

The terraform deployment needs several variable names set before it can start, which are defined in `aws/variables.tf`.
The variables that should likely be changed for a specific deployment are further specified in the `aws/aiidalab-cluster.tfvars` file.
Prior to deployment you should adjust it for your needs, e.g., change the region and names most appropriate for your deployment.
The profile only needs to be changed if you are not using the `terraform-bot` user from the last step.

After adjusting all variables and within the `aws/` folder, run
```
terraform init
```
to configure terraform for deployment.
This will download all required modules and run a basic consistency check on the configuration.

### Infrastructure Deployment

WARNING: THE FOLLOWING STEPS WILL CREATE POTENTIALLY EXPENSIVE RESOURCES WITHIN YOUR AWS INFRASTRCTURE!
DO NOT PROCEED UNLESS YOU FULLY UNDERSTAND WHAT RESOURCES ARE GOING TO BE CREATED, HOW TO MONITOR THEM, AND MOST IMPORTANTLY HOW TO DESTROY THEM!

#### First-Time Deployment

After successful initialization, we will create the plan for resource creation with:
```
terraform plan -var-file=aiidalab-cluster.tfvars
```

The plan is a list of the lowest-level resources it can give you.
After reviewing the plan (and ensuring that you understand all resources that are going to be created at least on a high level), apply it with:
```
terraform apply -var-file=aiidalab-cluster.tfvars
```

The initial setup of the infrastructure will take about 15 min or even more (the EKS cluster alone takes about 10 minutes to be created).
Terraform will create most resources in parallel unless there are dependencies.

NOTE: If the resource creation takes too long, some commands can timeout.
This issue can usually be resolved by simply running `terraform apply ...` again.

The creation of the kubernetes cluster was successful if the `apply` command exits without error.

#### Configure kubectl

To inspect and interact with the cluster infrastructure, you will need to configure `kubectl` and `helm`; terraform does not modify the configuration automatically by default.
To configure kubectl, execute the following command, replacing the values in `<>` with those applicable to your deployment:

```
aws eks update-kubeconfig --name=<cluster-name> --region=<region> --profile=<profile>
```

Now you are able to interact with the kubernetes cluster.
For example, the following commands should run without error:

```
aws eks list-clusters --region=<region> --profile=<profile>
aws eks describe-cluster --region=<region> --profile=<profile> --name=<cluster-name>
kubectl cluster-info
kubectl get pods -A
kubectl get nodes -A
helm list -A
```

You should be able to see
- A list of clusters on your account, including the one you just made
- Information about the cluster you just made
- Basic information about the kubernetes cluster
- All of the pods (individual software) present on machines in the
cluster
- All of the nodes (actual machines) in the cluster, which should just
be one core node
- All of the Helm releases on the cluster, which should be the
`efs-provisioner` and the `cluster-autoscaler`.

If there were problems with deployment, these commands might fail or give you insight into the problems.

#### Modifying the Infrastructure

NOTE: Do not modify AWS resources with the console if you created them with Terraform.
This can cause unintended problems for Terraform because it can't see the resource changes you made.

If you want to change some of the values or infrastructure, you can fiddle with the `.tf` files and then run `terraform apply -var-file=aiidalab-cluster.tfvars` again.
Terraform will compare the new plan to the old plan that you already deployed and see what is has to do to get from one to the other.
For individual resources, this may be an easy in-place modification, others may have to be destroyed and re-created, and others still may just be different resources, so you delete them and make the replacements.
Terraform takes care of all of this for you but will show you what it intends to do in the plan it outputs.

NOTE: If you change the worker group templates and there are existing nodes when you run `terraform apply ...`, it wil not apply the changes to existing nodes.
You will have to manually drain the node by setting the desired number of nodes to 0 in the AWS Console, wait for the nodes to disappear, then set the desired number of nodes to 1 once `terraform apply ...` has finished.

NOTE: Changing the desired number of nodes after the worker group template has been created will not work unless you do so in the AWS Console.
Terraform does not affect that after the worker group template has been created.

#### Tear Down

It is recommended to uninstall the AiiDAlab cluster installation with helm prior to deleting the resources.
For that, follow the instructions provided in the README.md file located at the root of this repository.

If you do not want these resources on your account forever (since they cost you money), you can tear it all down with one command per directory.
Terraform remembers everything it has currently built, so as long as you provide the `.tfvars` file, it will find the resources correctly and remove them in the reverse order that they were built!

Running `terraform destroy ...` will generate a plan similar to `terraform apply ...`, but it will indicate that it is deleting resources, not deploying them.
Again, you will be prompted to confirm the plan by typing `yes`.

```
terraform destroy --var-file=aiidalab-cluster.tfvars
```

The `destroy` command can time out trying to destroy some of the Kubernetes resources, but re-running it usually solves the issue.
If you put anything on your cluster (besides the `efs-provisioner` and the `cluster-autoscaler`), you should remove it before running `terraform destroy ...`.
Since Terraform isn't detecting what software is on your cluster (it only knows what it put on the cluster), it does not know how to remove it, and that can lead to issues.

Removing the `terraform-bot` user will require to manually delete the access keys in the AWS Console.
Then, you can delete the Terraform entries.

```
cd ../aws-creds/
terraform destroy -var-file=iam.tfvars
```

If you set your local kubeconfig to point to this cluster, you can remove that with the following:

```
kubectl config delete-cluster <your-cluster-arn>
kubectl config delete-context <your-cluster-context>
kubectl config unset users.<user-name>
```

You can get those variables with the corresponding commands:
- `your-cluster-arn`: `kubectl config get-clusters`
- `your-cluster-context`: `kubectl config get-contexts`
- `user-name`: `kubectl config view`, the name you want will look
something like
`arn:aws:eks:us-west-2:############:cluster/<your-cluster>`.

If you had a previous `kubectl` context set, you may also want to set it to be something else with

```
kubectl config use-context <different context>
```
