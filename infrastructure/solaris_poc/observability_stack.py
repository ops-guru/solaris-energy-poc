"""Observability stack - CloudWatch, dashboards, alarms."""
import aws_cdk as cdk
from aws_cdk import aws_cloudwatch as cloudwatch
from constructs import Construct


class ObservabilityStack(cdk.Stack):
    """Observability infrastructure for Solaris POC."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: CloudWatch dashboard with metrics
        # TODO: CloudWatch alarms
        # TODO: X-Ray tracing configuration
        # TODO: Log groups for Lambda

        pass

