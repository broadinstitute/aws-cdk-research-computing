from constructs import Construct
from aws_cdk import Duration
from aws_cdk import Stack
from aws_cdk import aws_s3 as s3


class DevBucketStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Specify the bucket name - useful if you need this value fixed
        dev_bucket_name = self.node.try_get_context("dev_bucket_name")

        # specify lifecycle rules
        lifecycle_rules = [
            s3.LifecycleRule(
                id="IntelligentTieringRule",
                enabled=True,
                transitions=[
                    s3.Transition(
                        storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                        transition_after=Duration.days(0),
                    )
                ],
            ),
            s3.LifecycleRule(
                id="AbortIncompleteMultipartUploadRule",
                enabled=True,
                abort_incomplete_multipart_upload_after=Duration.days(7),
                noncurrent_version_expiration=Duration.days(7),
                expired_object_delete_marker=True,
            ),
        ]

        dev_bucket = s3.Bucket(
            self,
            "DevOpenDataBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            enforce_ssl=True,
            bucket_name=dev_bucket_name,
            lifecycle_rules=lifecycle_rules,
            versioned=True,
            cors=[
                s3.CorsRule(
                    allowed_headers=["*"],
                    allowed_methods=[s3.HttpMethods.HEAD, s3.HttpMethods.GET],
                    allowed_origins=["*"],
                    exposed_headers=["ETag", "x-amz-meta-custom-header"],
                    max_age=3000,
                )
            ],
        )
