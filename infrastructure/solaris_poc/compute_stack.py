"""Compute infrastructure stack - Lambda functions."""
import aws_cdk as cdk
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import Duration
from constructs import Construct
import os


class ComputeStack(cdk.Stack):
    """Lambda compute infrastructure for Solaris POC."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc=None,
        security_group=None,
        documents_bucket=None,
        sessions_table=None,
        opensearch_domain=None,
        opensearch_endpoint=None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Document Processor Lambda
        # Note: For initial POC, Lambda layer is deferred - functions include dependencies directly
        self.document_processor_lambda = self._create_document_processor(
            common_layer=None,  # Defer layer implementation
            vpc=vpc,
            security_group=security_group,
            documents_bucket=documents_bucket,
            opensearch_domain=opensearch_domain,
            opensearch_endpoint=opensearch_endpoint,
        )

        # Output Lambda function ARNs
        cdk.CfnOutput(
            self,
            "DocumentProcessorLambdaArn",
            value=self.document_processor_lambda.function_arn,
            description="Document Processor Lambda ARN",
        )

    def _create_document_processor(
        self,
        common_layer,
        vpc,
        security_group,
        documents_bucket,
        opensearch_domain,
        opensearch_endpoint,
    ) -> _lambda.Function:
        """Create document processor Lambda function."""

        # Lambda execution role with permissions
        lambda_role = iam.Role(
            self,
            "DocumentProcessorRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaVPCAccessExecutionRole"
                )
            ],
        )

        # S3 permissions
        if documents_bucket:
            documents_bucket.grant_read(lambda_role)

        # Bedrock permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["bedrock:InvokeModel"],
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v1"
                ],
            )
        )

        # OpenSearch permissions (if domain provided)
        if opensearch_domain:
            lambda_role.add_to_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["es:*"],
                    resources=[f"{opensearch_domain.domain_arn}/*"],
                )
            )

        # CloudWatch Logs
        log_group = logs.LogGroup(
            self,
            "DocumentProcessorLogs",
            log_group_name=f"/aws/lambda/solaris-poc-document-processor",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Lambda function
        lambda_function = _lambda.Function(
            self,
            "DocumentProcessor",
            function_name="solaris-poc-document-processor",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda/document-processor"),
            role=lambda_role,
            memory_size=1024,
            timeout=Duration.minutes(15),  # 15 minutes for large documents
            layers=[common_layer] if common_layer else [],
            vpc=vpc,
            vpc_subnets=None,  # Use default subnets
            security_groups=[security_group] if security_group else None,
            environment={
                "OPENSEARCH_ENDPOINT": opensearch_endpoint or "",
                "OPENSEARCH_INDEX": "turbine-documents",
                "EMBEDDING_MODEL": "amazon.titan-embed-text-v1",
                "OPENSEARCH_MASTER_USER": "admin",
                # Password should be stored in Secrets Manager in production
                "OPENSEARCH_MASTER_PASSWORD": "TempP@ssw0rd123!Ch@ngeInProd",
                # AWS_REGION is automatically provided by Lambda runtime
            },
            log_group=log_group,
        )

        return lambda_function

