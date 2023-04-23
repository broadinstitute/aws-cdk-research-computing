# Collaborator access

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

# time until which the credentials are valid
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