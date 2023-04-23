
# Introduction

Stacks for setting up AWS resources for research computing.

- `DevBucketStack`: bucket
- `IAMResources`: users, groups, roles, and policies
- `NetworkStack`: VPC and subnets
- `LaunchTemplateStack`: launch template for EC2 instances

`DevBucketStack` needs only a single parameter, `dev_bucket_name`, which is the name of the bucket.
The parameter can be specified either in the `cdk.json` file or on the command line using the `--context` option (see below)

All other stacks require the parameter `config_folder`, which is the path to the folder containing the configuration files:

- `IAMResources` uses `user_group.yaml`, `role_policy.yaml`, `action_mapping.yaml`, `assume_role.yaml`
- `NetworkStack` uses `network.yaml`
- `LaunchTemplateStack` uses `launch_template.yaml`

The repo contains two sets of configuration files:

- `configs/local`: configuration files for the research team ("local").
- `configs/collab`: configuration files for a collaborator to enable access to the S3 resources shared by the research team.

In the example, the collaborator `IAMResources` stack needs to be set up first because the local `IAMResources` stack refers to a role created in the collaborator stack.
More on this below.

CRITICAL NOTE: The `DevBucketStack` does not have termination protection enabled! This is because the bucket is used for testing and development and it is not intended to be used in production. If you want to use this stack in production, you should enable termination protection.
