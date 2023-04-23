
# Deployment

First create the collaborator stack.
For testing purposes, this can be run in the same account as the local stack.

```sh
cdk deploy IAMResources-collab --context config_folder="configs/collab" --app "python3 app_collab.py"
```

Then create the local stack

```sh
cdk deploy DevBucket
cdk deploy IAMResources --context config_folder="configs/local"
cdk deploy Network --context config_folder="configs/local"
cdk deploy LaunchTemplate --context config_folder="configs/local"
```