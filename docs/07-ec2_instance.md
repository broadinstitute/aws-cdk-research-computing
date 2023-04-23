# Launch EC2 instances

First, assume the `typical_data_scientist` role.

Generate a new key pair using the AWS CLI:

```sh
# permissions needed to run this: `ec2:CreateKeyPair`
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
# this will show up as null if the instance is not running (or if it doesn't exist)
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
