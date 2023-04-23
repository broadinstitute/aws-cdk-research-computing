import yaml
from aws_cdk import aws_ec2 as ec2, Stack, Fn
from constructs import Construct


class NetworkStack(Stack):
    def __init__(self, scope: Construct, id: str, config_folder: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        with open(f"{config_folder}/network.yaml") as file:
            params = yaml.safe_load(file)

        created_vpcs = {
            params_vpc["name"]: ec2.Vpc(
                self,
                id=params_vpc["name"],
                vpc_name=params_vpc["name"],
                ip_addresses=ec2.IpAddresses.cidr(params_vpc["cidr"]),
                max_azs=params_vpc["max_azs"],
                nat_gateways=params_vpc["nat_gateways"],
            )
            for params_vpc in params["vpcs"]
        }

        created_security_groups = {
            params_security_group["name"]: ec2.SecurityGroup(
                self,
                id=params_security_group["name"],
                security_group_name=params_security_group["name"],
                vpc=created_vpcs[params_security_group["vpc"]],
                allow_all_outbound=True,
                description=params_security_group["description"],
            )
            for params_security_group in params["security_groups"]
        }

        for params_security_group in params["security_groups"]:
            for params_ingress in params_security_group["ingress"]:
                for allowed_cidr_block in params_ingress["allowed_cidr_blocks"]:
                    created_security_groups[
                        params_security_group["name"]
                    ].add_ingress_rule(
                        peer=ec2.Peer.ipv4(allowed_cidr_block),
                        connection=ec2.Port.tcp(params_ingress["port"]),
                        description=params_ingress["description"],
                    )
