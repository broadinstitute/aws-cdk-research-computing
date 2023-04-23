from aws_cdk import aws_ec2 as ec2, aws_ssm as ssm, Stack, CfnOutput
import yaml
from constructs import Construct


class LaunchTemplateStack(Stack):
    def __init__(self, scope: Construct, id: str, config_folder: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        with open(f"{config_folder}/launch_template.yaml") as file:
            params = yaml.safe_load(file)

        for lt_params in params["launch_templates"]:
            launch_template = ec2.CfnLaunchTemplate(
                self,
                lt_params["name"],
                launch_template_name=lt_params["name"],
                launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                    image_id=lt_params["image_id_ssm"],
                    instance_type=lt_params["instance_type"],
                ),
            )
