"""API infrastructure stack - API Gateway."""
import aws_cdk as cdk
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class ApiStack(cdk.Stack):
    """API Gateway infrastructure for Solaris POC."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        agent_workflow_lambda: _lambda.IFunction = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        if not agent_workflow_lambda:
            raise ValueError("agent_workflow_lambda is required")

        # REST API
        self.api = apigateway.RestApi(
            self,
            "SolarisPocApi",
            rest_api_name="Solaris POC API",
            description="API for Solaris Energy POC operator assistant",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],  # POC only - restrict in production
                allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                ],
                max_age=cdk.Duration.seconds(3600),
            ),
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,  # Requests per second
                throttling_burst_limit=200,
                logging_level=apigateway.MethodLoggingLevel.INFO,
            ),
        )

        # API Key for rate limiting
        api_key = self.api.add_api_key(
            "ApiKey",
            api_key_name="solaris-poc-api-key",
        )

        # Usage plan
        usage_plan = self.api.add_usage_plan(
            "UsagePlan",
            name="solaris-poc-usage-plan",
            throttle=apigateway.ThrottleSettings(
                rate_limit=50,  # Requests per second
                burst_limit=100,
            ),
            quota=apigateway.QuotaSettings(
                limit=10000,  # Requests per day
                period=apigateway.Period.DAY,
            ),
        )
        usage_plan.add_api_key(api_key)

        # Lambda integration for agent workflow
        agent_integration = apigateway.LambdaIntegration(
            agent_workflow_lambda,
            proxy=True,
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header."
                        "Access-Control-Allow-Origin": "'*'"
                    },
                )
            ],
        )

        # Chat endpoint: POST /chat
        chat_resource = self.api.root.add_resource("chat")
        chat_resource.add_method(
            "POST",
            agent_integration,
            api_key_required=True,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header."
                        "Access-Control-Allow-Origin": True
                    },
                ),
                apigateway.MethodResponse(status_code="400"),
                apigateway.MethodResponse(status_code="500"),
            ],
        )

        # Session history endpoint: GET /chat/{session_id}
        session_resource = chat_resource.add_resource("{session_id}")
        session_resource.add_method(
            "GET",
            agent_integration,
            api_key_required=True,
        )

        # Delete session endpoint: DELETE /chat/{session_id}
        session_resource.add_method(
            "DELETE",
            agent_integration,
            api_key_required=True,
        )

        # Outputs
        cdk.CfnOutput(
            self,
            "ApiUrl",
            value=self.api.url,
            description="API Gateway endpoint URL",
        )

        cdk.CfnOutput(
            self,
            "ApiKeyId",
            value=api_key.key_id,
            description="API Key ID (retrieve value from AWS Console)",
        )

