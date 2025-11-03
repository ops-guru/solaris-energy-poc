"""Storage infrastructure stack - S3, DynamoDB."""
import aws_cdk as cdk
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_s3_deployment as s3_deploy
from aws_cdk import RemovalPolicy
from constructs import Construct


class StorageStack(cdk.Stack):
    """Storage infrastructure for Solaris POC."""

    def __init__(self, scope: Construct, construct_id: str, vpc=None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for document storage
        self.documents_bucket = s3.Bucket(
            self,
            "DocumentsBucket",
            bucket_name=f"solaris-poc-documents-{self.account}-{self.region}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,  # Don't delete valuable documents
            auto_delete_objects=False,  # Keep documents on stack deletion
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="MoveOldVersions",
                    noncurrent_version_expiration=cdk.Duration.days(90),
                )
            ],
        )

        # S3 bucket for frontend web hosting
        self.frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            bucket_name=f"solaris-poc-frontend-{self.account}-{self.region}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            website_index_document="index.html",
            website_error_document="error.html",
            removal_policy=RemovalPolicy.DESTROY,
        )

        # DynamoDB table for conversation sessions
        self.sessions_table = dynamodb.Table(
            self,
            "SessionsTable",
            table_name="solaris-poc-sessions",
            partition_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # POC data, safe to delete
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            time_to_live_attribute="ttl",  # Auto-delete old sessions
        )

        # DynamoDB table for LLM configuration
        self.config_table = dynamodb.Table(
            self,
            "ConfigTable",
            table_name="solaris-poc-config",
            partition_key=dynamodb.Attribute(
                name="config_key",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )

        # Add initial LLM configuration
        cdk.CfnOutput(
            self,
            "InitialLLMConfig",
            value="claude-3.5-sonnet",
            description="Default LLM model",
        )

