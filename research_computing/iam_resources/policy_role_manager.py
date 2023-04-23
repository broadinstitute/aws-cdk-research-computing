import yaml
from aws_cdk import aws_iam as iam
from aws_cdk import Stack


class PolicyRoleManager:
    """
    Create policies and roles.
    """

    def __init__(self, role_policy_file: str, action_mapping_file: str):
        with open(role_policy_file, "r") as f:
            roles_policies = yaml.safe_load(f)

        self.policies = roles_policies["policies"]

        self.roles = roles_policies["roles"]

        with open(action_mapping_file, "r") as file:
            self.action_mapping = yaml.safe_load(file)

    def _get_effective_actions(self, actions: list) -> list:
        """
        Get effective actions based on action mapping.

        For example, if the action is `"read_only"`, the effective actions may be defined in the action mapping file as
        `["s3:GetObject", "s3:ListBucket"]`.

        In this case,

        `_get_effective_actions(["read_only"]) -> ["s3:GetObject", "s3:ListBucket"]`

        """
        effective_actions = []
        for action in actions:
            effective_actions.extend(self.action_mapping[action])

        return effective_actions

    def create_policies(self, stack: Stack) -> None:
        """
        Create policies.
        """
        self.created_policies = {}

        for policy in self.policies:
            statements = []

            resources = policy["resources"]

            resources = [
                iam.Role.from_role_name(
                    stack, "fetched-" + resource.split(":")[-1], resource.split(":")[-1]
                ).role_arn
                if resource.startswith("role:")
                else resource
                for resource in resources
            ]

            for action_dict in self._get_effective_actions(policy["actions"]):
                statement = iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[action_dict["action"]],
                    resources=resources,
                    conditions=action_dict.get("condition"),
                )
                statements.append(statement)

            # ListBucket needs to be handled separately
            for action in policy["actions"]:
                if action in ["read_only", "read_write"]:
                    for resource in policy["resources"]:
                        bucket_name, prefix = resource.split(":")[-1].split("/", 1)

                        statement = iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["s3:ListBucket"],
                            resources=[f"arn:aws:s3:::{bucket_name}"],
                            conditions={"StringLike": {"s3:prefix": [prefix]}},
                        )
                        statements.append(statement)

            self.created_policies[policy["name"]] = iam.ManagedPolicy(
                stack,
                policy["name"],
                statements=statements,
                managed_policy_name=policy["name"],
            )

    def create_roles(self, stack: Stack) -> None:
        """
        Create roles.
        """
        self.created_roles = {}

        for role in self.roles:
            self.created_roles[role["name"]] = iam.Role(
                stack,
                role["name"],
                assumed_by=iam.ArnPrincipal(f"arn:aws:iam::{stack.account}:root"),
                role_name=role["name"],
            )

            for policy in role["policies"]:
                self.created_roles[role["name"]].add_managed_policy(
                    self.created_policies[policy]
                )
                self.created_roles[role["name"]].node.add_dependency(
                    self.created_policies[policy]
                )

    def create_trust_policies_instance_profiles(self, stack: Stack) -> None:
        """
        Create instance trust policies and instance profiles.

        The roles that will be assumed by EC2 instances need to
        1. have a trust policy that allows EC2 to assume the role.
        2. have an instance profile associated with them.
        """

        # We assume that the roles for which the resources are other roles, will be assumed by EC2 instances.
        role_names = set(
            [
                resource.split(":")[-1]
                for policy in self.policies
                for resource in policy["resources"]
                if resource.startswith("role:")
            ]
        )

        self.created_instance_profiles = {}

        for role_name in role_names:
            role = self.created_roles[role_name]

            role.assume_role_policy.add_statements(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["sts:AssumeRole"],
                    principals=[iam.ServicePrincipal("ec2.amazonaws.com")],
                )
            )

            role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                )
            )

            instance_profile = iam.CfnInstanceProfile(
                stack,
                "instance-profile-" + role_name,
                instance_profile_name=role_name,
                roles=[role_name],
            )

            instance_profile.node.add_dependency(role)

            self.created_instance_profiles[role_name] = instance_profile
