#!/usr/bin/env python3

import aws_cdk as cdk
from research_computing.bucket_stack import DevBucketStack
from research_computing.iam_resources_stack import IAMResourcesStack
from research_computing.network_stack import NetworkStack
from research_computing.launch_template_stack import LaunchTemplateStack
from pathlib import Path

app = cdk.App()

config_folder = app.node.try_get_context("config_folder")

if not (Path(config_folder).exists() and Path(config_folder).is_dir()):
    raise ValueError(f"Invalid config folder: {config_folder}")

DevBucketStack(app, "DevBucket", termination_protection=False)

IAMResourcesStack(app, "IAMResources", config_folder=config_folder)

NetworkStack(app, "Network", config_folder=config_folder, termination_protection=False)

LaunchTemplateStack(app, "LaunchTemplate", config_folder=config_folder)

app.synth()
