# User Management

The [AWS best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#bp-users-federation-idp>) says that you should not create access keys for users.
Instead, you should use an identity provider (IdP) to federate users to AWS.
However, if you need to create access keys for a user, you can do so using the AWS CLI.

To create an access key for a user:

```sh
USER=user1
CREDENTIALS=/tmp/credentials_${USER}.json
# permissions needed to run this: `iam:CreateAccessKey`
aws iam create-access-key --user-name ${USER} > ${CREDENTIALS} # this is insecure, but it's just for testing
```

To delete all access keys for a user:

```sh
USER=user1
# permissions needed to run this: `iam:ListAccessKeys` and `iam:DeleteAccessKey`
aws iam list-access-keys --user-name ${USER} | jq -r '.AccessKeyMetadata[].AccessKeyId' | xargs -I {} aws iam delete-access-key --user-name ${USER} --access-key-id {}
```

To create a password for a user:

```sh
USER=user1
# permissions needed to run this: `iam:CreateLoginProfile`
aws iam create-login-profile --user-name ${USER} --password password1
```

To deactivate a user's password:

```sh
USER=user1
# permissions needed to run this: `iam:UpdateLoginProfile`
aws iam update-login-profile --user-name ${USER} --password-reset-required
```

To list MFA devices for a user:

```sh
USER=user1
# permissions needed to run this: `iam:ListMFADevices`
aws iam list-mfa-devices --user-name ${USER}
```
