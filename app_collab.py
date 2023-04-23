#!/usr/bin/env python3

import aws_cdk as cdk
from research_computing.bucket_stack import DevBucketStack
from research_computing.iam_resources_stack import IAMResourcesStack
from pathlib import Path

app = cdk.App()

config_folder = app.node.try_get_context("config_folder")

if not (Path(config_folder).exists() and Path(config_folder).is_dir()):
    raise ValueError(f"Invalid config folder: {config_folder}")

IAMResourcesStack(app, "IAMResources-collab", config_folder=config_folder)

app.synth()
