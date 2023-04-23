# Credentials and Roles

To export the access key and secret access key as environment variables:

```sh
USER=user1
CREDENTIALS=/tmp/credentials_${USER}.json
export AWS_ACCESS_KEY_ID=$(cat ${CREDENTIALS} | jq -j '.AccessKey.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(cat ${CREDENTIALS} | jq -j '.AccessKey.SecretAccessKey')
unset AWS_SESSION_TOKEN # do this just in case you had previously assumed a role

# verify that the credentials work
aws sts get-caller-identity
```

Try out a command to which the user does not have access without assuming a role:

```sh
aws s3 ls s3://ipdata-dev/folder2/
```

To assume a role, e.g., `typical_data_scientist` that will give access to the S3 bucket (and other resources):

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

# time until which the credentials are valid
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