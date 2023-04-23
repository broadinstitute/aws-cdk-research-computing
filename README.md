
# CloudFormation Stacks for Research Computing

Here, we use AWS CDK to create CloudFormation stacks for research computing.

At present, it contains two stacks:

- `DevBucketStack`: creates a bucket for development purposes
- `IAMResources`: creates IAM resources for a research project

`DevBucketStack` needs only a single parameter, `dev_bucket_name`, which is the name of the bucket.
The parameter can be specified either in the `cdk.json` file or on the command line using the `--context` option (see below)

`IAMResources` also needs a single parameter, `config_folder`, which is the path to the folder containing the configuration files.
There are four parameter files in the `configs` folder:

- `user_group.yaml`: configure users and groups
- `role_policy.yaml`: configure policies and roles
- `action_mapping.yaml`: maps short action names to full, IAM action names
- `assume_role.yaml`: assigns roles to users or other roles

The repo contains two sets of configuration files:

- `configs/local`: configuration files for the research team ("local"). This shows examples of setting up different types of access to resource, including collaborator access to a prefix in a bucket.
- `configs/collab`: configuration files for a collaborator. This shows how a collaborator should setup their infrastructure to access the S3 resources shared by the research team.

In the example, the collaborator `IAMResources` stack needs to be set up first because the local `IAMResources` stack refers to a role created in the collaborator stack.

## Setup

To manually create a virtualenv on MacOS and Linux:

```sh
python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```sh
source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```sh
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```sh
pip install -r requirements.txt
```

## Deploy

First create the collaborator stack

```sh
cdk deploy IAMResources-collab --context config_folder="configs/collab" --app "python3 app_collab.py"
```

Then create the local stack

```sh
cdk deploy DevBucket
cdk deploy IAMResources --context config_folder="configs/local"
```

## Creating access keys and passwords for users

The [AWS best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#bp-users-federation-idp>) says that you should not create access keys for users.
Instead, you should use an identity provider (IdP) to federate users to AWS.
However, if you need to create access keys for a user, you can do so using the AWS CLI.

To create an access key for a user, run the following command; admin permissions (or at least `iam:CreateAccessKey`) needed:

```sh
USER=user1
CREDENTIALS=/tmp/credentials_${USER}.json
# permissions needed to run this: `iam:CreateAccessKey`
aws iam create-access-key --user-name ${USER} > ${CREDENTIALS} # this is insecure, but it's just for testing
```

To delete all access keys for a user, run the following command; admin permissions (or at least `iam:ListAccessKeys` and `iam:DeleteAccessKey` ) needed:

```sh
USER=user1
# permissions needed to run this: `iam:ListAccessKeys` and `iam:DeleteAccessKey`
aws iam list-access-keys --user-name ${USER} | jq -r '.AccessKeyMetadata[].AccessKeyId' | xargs -I {} aws iam delete-access-key --user-name ${USER} --access-key-id {}
```

To create a password for a user, run the following command:

```sh
USER=user1
# permissions needed to run this: `iam:CreateLoginProfile`
aws iam create-login-profile --user-name ${USER} --password password1
```

To deactivate a user's password, run the following command:

```sh
USER=user1
# permissions needed to run this: `iam:UpdateLoginProfile`
aws iam update-login-profile --user-name ${USER} --password-reset-required
```

To list MFA devices for a user, run the following command:

```sh
USER=user1
# permissions needed to run this: `iam:ListMFADevices`
aws iam list-mfa-devices --user-name ${USER}
```

## Using credentials and assuming roles

To export the access key and secret access key as environment variables, run the following command:

```sh
USER=user1
CREDENTIALS=/tmp/credentials_${USER}.json
export AWS_ACCESS_KEY_ID=$(cat ${CREDENTIALS} | jq -j '.AccessKey.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(cat ${CREDENTIALS} | jq -j '.AccessKey.SecretAccessKey')
unset AWS_SESSION_TOKEN # do this just in case you had previously assumed a role
# verify that the credentials work
aws sts get-caller-identity
```

Try out a command that the user does not have access to without assuming a role:

```sh
aws s3 ls s3://ipdata-dev/folder2/
```

To assume a role, e.g., `typical_data_scientist` run the following command:

```sh
ROLE=typical_data_scientist
ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account)

ROLE_CREDENTIALS=/tmp/credentials_${ROLE}.json # this is insecure, but it's just for testing

aws sts assume-role --role-arn arn:aws:iam::${ACCOUNT_ID}:role/${ROLE} --role-session-name ${ROLE} > ${ROLE_CREDENTIALS}

# view the credentials
cat ${ROLE_CREDENTIALS}

# set environment variables
export AWS_ACCESS_KEY_ID=$(cat ${ROLE_CREDENTIALS} | jq -j '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(cat ${ROLE_CREDENTIALS} | jq -j '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(cat ${ROLE_CREDENTIALS} | jq -j '.Credentials.SessionToken')

# time untilwhich the credentials are valid
cat ${ROLE_CREDENTIALS} | jq -j '.Credentials.Expiration'

# verify that the credentials work
aws sts get-caller-identity
```

Now that you have assumed the role, you can run the command that you were not able to run before:

```sh
date > /tmp/test.txt; aws s3 cp /tmp/test.txt s3://ipdata-dev/folder2/
aws s3 ls s3://ipdata-dev/folder2/
```

You still can't do everything, e.g., you can't list the top-level bucket:

```sh
aws s3 ls s3://ipdata-dev/
# An error occurred (AccessDenied) when calling the ListObjectsV2 operation: Access Denied
```

or list a different prefix:

```sh
aws s3 ls s3://ipdata-dev/folder1/
# An error occurred (AccessDenied) when calling the ListObjectsV2 operation: Access Denied
```

## Collaborator access

```sh
USER=collaborator_user1
CREDENTIALS=/tmp/credentials_${USER}.json
# permissions needed to run this: `iam:CreateAccessKey`
aws iam create-access-key --user-name ${USER} > ${CREDENTIALS} # this is insecure, but it's just for testing
```

```sh
USER=collaborator_user1
CREDENTIALS=/tmp/credentials_${USER}.json
export AWS_ACCESS_KEY_ID=$(cat ${CREDENTIALS} | jq -j '.AccessKey.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(cat ${CREDENTIALS} | jq -j '.AccessKey.SecretAccessKey')
unset AWS_SESSION_TOKEN # do this just in case you had previously assumed a role

# verify that the credentials work
aws sts get-caller-identity
```

This will fail:

```sh
aws s3 ls s3://ipdata-dev/collaborator-folder1/
```

Need to assume the role first:

```sh
ROLE=requestor-bucket-ipdata-dev
ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account)

ROLE_CREDENTIALS=/tmp/credentials_${ROLE}.json # this is insecure, but it's just for testing

aws sts assume-role --role-arn arn:aws:iam::${ACCOUNT_ID}:role/${ROLE} --role-session-name ${ROLE} > ${ROLE_CREDENTIALS}

cat ${ROLE_CREDENTIALS}

export AWS_ACCESS_KEY_ID=$(cat ${ROLE_CREDENTIALS} | jq -j '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(cat ${ROLE_CREDENTIALS} | jq -j '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(cat ${ROLE_CREDENTIALS} | jq -j '.Credentials.SessionToken')

# duration for which the credentials are valid
cat ${ROLE_CREDENTIALS} | jq -j '.Credentials.Expiration'

# verify that the credentials work
aws sts get-caller-identity
```

Now this will work:

```sh
aws s3 ls s3://ipdata-dev/collaborator-folder1/
```

But this will not:

```sh
date > /tmp/test.txt; aws s3 cp /tmp/test.txt s3://ipdata-dev/collaborator-folder1/
# An error occurred (AccessDenied) when calling the PutObject operation: Access Denied
```

## Launch EC2 instance

Generate a new key pair using the AWS CLI:

```sh
aws ec2 create-key-pair --key-name MyKeyPair --query 'KeyMaterial' --output text > ~/Desktop/MyKeyPair.pem
```

This command will create a new key pair named MyKeyPair and save the private key in a file called MyKeyPair.pem.
Make sure to protect the private key file, as it's needed to access your instances.

Set the correct permissions for the key pair file:

```sh
chmod 400 ~/Desktop/MyKeyPair.pem
```

Launch the instance

```sh
VPC_NAME=vpc-dev
SECURITY_GROUP_NAME=ssh_from_vpn
LAUNCH_TEMPLATE_NAME=lt-small

LAUNCH_TEMPLATE_ID=$(aws ec2 describe-launch-templates --launch-template-names ${LAUNCH_TEMPLATE_NAME} | jq -r '.LaunchTemplates[0].LaunchTemplateId')
VPC_ID=$(aws ec2 describe-vpcs --filters Name=tag:Name,Values=${VPC_NAME} | jq -r '.Vpcs[0].VpcId')
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters Name=vpc-id,Values=${VPC_ID} --filters Name=group-name,Values=${SECURITY_GROUP_NAME}| jq -r '.SecurityGroups[0].GroupId')

SUBNET_ID=$(aws ec2 describe-subnets --filters Name=vpc-id,Values=${VPC_ID} | jq -r 'first(.Subnets[] | select(.AvailabilityZone == "us-east-1a" and .MapPublicIpOnLaunch == true) | .SubnetId)')

echo $SUBNET_ID

INSTANCE_NAME=ec2-test

INSTANCE_PROFILE_NAME=minimal

aws ec2 run-instances --launch-template LaunchTemplateId=${LAUNCH_TEMPLATE_ID} --key-name MyKeyPair --security-group-ids ${SECURITY_GROUP_ID} --subnet-id ${SUBNET_ID} --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${INSTANCE_NAME}}]" --iam-instance-profile Name=${INSTANCE_PROFILE_NAME} # --dry-run
```

Get the instance id

```sh
INSTANCE_ID=$(aws ec2 describe-instances --filters Name=tag:Name,Values=${INSTANCE_NAME} --filters Name=instance-state-name,Values=running | jq -r '.Reservations[0].Instances[0].InstanceId')
echo ${INSTANCE_ID}
```

Connect to the instance

```sh

# get the public ip address
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids ${INSTANCE_ID} | jq -r '.Reservations[0].Instances[0].PublicIpAddress')
echo ${PUBLIC_IP}

# get the status of the instance
aws ec2 describe-instance-status --instance-ids ${INSTANCE_ID}

# connect to the instance once ready
ssh -i ~/Desktop/MyKeyPair.pem ec2-user@${PUBLIC_IP}
```

Terminate the instance

```sh
aws ec2 terminate-instances --instance-ids ${INSTANCE_ID}
```

## Addendum

### Useful commands

- `cdk ls`          list all stacks in the app
- `cdk synth`       emits the synthesized CloudFormation template
- `cdk deploy`      deploy this stack to your default AWS account/region
- `cdk diff`        compare deployed stack with current state
- `cdk docs`        open CDK documentation
