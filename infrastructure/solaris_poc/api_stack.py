"""API infrastructure stack - API Gateway."""
import aws_cdk as cdk
from aws_cdk import aws_apigateway as apigateway
from constructs import Construct


class ApiStack(cdk.Stack):
    """API Gateway infrastructure for Solaris POC."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: REST API with Lambda integration
        # TODO: CORS configuration
        # TODO: API keys and usage plans
        # TODO: Rate limiting

        pass

