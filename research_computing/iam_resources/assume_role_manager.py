import yaml
from aws_cdk import aws_iam as iam
from aws_cdk import Stack
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AssumeRoleManager:
    """
    Create trust policies for roles based on assignments.
    """

    def __init__(self, assume_role_file: str):
        with open(assume_role_file, "r") as f:
            assume_role = yaml.safe_load(f)

        self.assignments = assume_role["assignments"]

    def create_trust_policies(self, stack: Stack):
        """
        Create trust policies for roles based on assignments
        """

        for assignment in self.assignments:
            entity = assignment["entity"]
            entity_type = assignment["type"]
            role_name = assignment["role"]

            # https://stackoverflow.com/a/50281540
            # You cannot specify IAM groups as principals

            if entity_type == "user":
                entity_list = [entity]
            elif entity_type == "group":
                group_dict = {
                    group["name"]: group["users"]
                    for group in stack.user_group_manager.groups
                }
                entity_list = group_dict[entity]
            elif entity_type == "arn":
                entity_list = [entity]
            else:
                raise Exception(f"Unknown identity type {entity_type}")

            role = stack.policy_role_manager.created_roles[role_name]

            for entity in entity_list:
                if entity_type == "arn":
                    arn_principal = entity
                else:
                    user = stack.user_group_manager.created_users[entity]

                    user.add_to_policy(
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["sts:AssumeRole"],
                            resources=[role.role_arn],
                        )
                    )

                    arn_principal = user.user_arn

                role.assume_role_policy.add_statements(
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=["sts:AssumeRole"],
                        principals=[iam.ArnPrincipal(arn_principal)],
                    )
                )
