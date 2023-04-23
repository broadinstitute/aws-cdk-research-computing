# AWS CloudFormation Stack to do the following:
# 1. Create user groups
# 2. Create users
# 3. Create policies
# 4. Attach policies to groups
# 5. Attach groups to users

from constructs import Construct
from aws_cdk import Stack
import logging
from .iam_resources.user_group_manager import UserGroupManager
from .iam_resources.policy_role_manager import PolicyRoleManager
from .iam_resources.assume_role_manager import AssumeRoleManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class IAMResourcesStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, config_folder: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.user_group_manager = UserGroupManager(
            # user_group_file=self.node.try_get_context("user_group_file")
            user_group_file=f"{config_folder}/user_group.yaml"
        )

        self.policy_role_manager = PolicyRoleManager(
            # role_policy_file=self.node.try_get_context("role_policy_file"),
            # action_mapping_file=self.node.try_get_context("action_mapping_file"),
            role_policy_file=f"{config_folder}/role_policy.yaml",
            action_mapping_file=f"{config_folder}/action_mapping.yaml",
        )

        self.assume_role_manager = AssumeRoleManager(
            # assume_role_file=self.node.try_get_context("assume_role_file"),
            assume_role_file=f"{config_folder}/assume_role.yaml",
        )

        self.user_group_manager.create_users_groups(stack=self)

        self.policy_role_manager.create_policies(stack=self)

        self.policy_role_manager.create_roles(stack=self)

        self.policy_role_manager.create_trust_policies_instance_profiles(stack=self)

        self.assume_role_manager.create_trust_policies(stack=self)
