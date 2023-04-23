import yaml
from aws_cdk import aws_iam as iam
from aws_cdk import Stack


class UserGroupManager:
    """
    Create users and groups.
    """

    def __init__(self, user_group_file: str):
        with open(user_group_file, "r") as f:
            users_groups = yaml.safe_load(f)

        self.groups = users_groups["groups"]
        self.users = users_groups["users"]

    def create_users_groups(self, stack: Stack):
        # Create groups
        self.created_groups = {
            group_config["name"]: iam.Group(
                stack, group_config["name"], group_name=group_config["name"]
            )
            for group_config in self.groups
        }

        # Create users
        self.created_users = {
            user_config["name"]: iam.User(
                stack, user_config["name"], user_name=user_config["name"]
            )
            for user_config in self.users
        }

        # Assign users to groups
        for group in self.groups:
            for user_name in group["users"]:
                self.created_groups[group["name"]].add_user(
                    self.created_users[user_name]
                )
