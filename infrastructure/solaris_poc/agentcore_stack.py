"""AgentCore configuration stack."""
from __future__ import annotations

import json
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import (
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_s3 as s3,
    aws_ssm as ssm,
    custom_resources as cr,
)
from constructs import Construct


class AgentCoreConfigStack(cdk.Stack):
    """Publishes AgentCore agent definition and supporting configuration."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        retrieval_tool_lambda: _lambda.IFunction,
        documents_bucket: s3.Bucket,
        agent_name: str = "solaris-operator-assistant",
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        definition = self._load_agent_definition_template(
            retrieval_tool_lambda.function_arn,
            documents_bucket.bucket_arn,
        )

        agent_parameter = ssm.StringParameter(
            self,
            "AgentDefinitionParameter",
            parameter_name="/solaris/agentcore/agent-definition",
            string_value=json.dumps(definition, indent=2),
        )

        tool_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["lambda:InvokeFunction"],
            resources=[retrieval_tool_lambda.function_arn],
        )

        ssm.StringParameter(
            self,
            "AgentRequiredPolicy",
            parameter_name="/solaris/agentcore/required-policy",
            string_value=json.dumps(tool_policy.to_statement_json(), indent=2),
        )

        cdk.CfnOutput(
            self,
            "AgentDefinitionParameterName",
            value=agent_parameter.parameter_name,
            description="SSM parameter storing AgentCore agent definition JSON",
        )

        cdk.CfnOutput(
            self,
            "AgentRetrievalToolArn",
            value=retrieval_tool_lambda.function_arn,
            description="Lambda ARN to register as AgentCore retrieval tool",
        )

        agent_resource_role = iam.Role(
            self,
            "AgentCoreResourceRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Role used by AgentCore to invoke retrieval Lambda and access resources.",
        )
        retrieval_tool_lambda.grant_invoke(agent_resource_role)

        custom_resource = self._provision_agent_core(
            agent_name=agent_name,
            agent_definition=definition,
            retrieval_tool_lambda=retrieval_tool_lambda,
            agent_resource_role=agent_resource_role,
        )

        cdk.CfnOutput(
            self,
            "AgentCoreAgentIdOutput",
            value=custom_resource.get_att_string("AgentId"),
            description="Provisioned AgentCore agent ID",
        )

        cdk.CfnOutput(
            self,
            "AgentCoreAgentId",
            value=custom_resource.get_att_string("AgentId"),
            description="Provisioned AgentCore agent ID",
        )

        cdk.CfnOutput(
            self,
            "AgentCoreResourceRoleArn",
            value=agent_resource_role.role_arn,
            description="IAM role assumed by AgentCore for resource access",
        )

    def _load_agent_definition_template(
        self,
        retrieval_lambda_arn: str,
        documents_bucket_arn: str,
    ) -> dict[str, object]:
        template_path = (
            Path(__file__)
            .resolve()
            .parents[1]
            .joinpath("agentcore", "agent_definition_template.json")
        )
        template = json.loads(template_path.read_text(encoding="utf-8"))

        template["tools"][0]["lambdaArn"] = retrieval_lambda_arn
        template.setdefault("permissions", {})
        template["permissions"]["documentsBucketArn"] = documents_bucket_arn

        return template

    def _provision_agent_core(
        self,
        agent_name: str,
        agent_definition: dict[str, object],
        retrieval_tool_lambda: _lambda.IFunction,
        agent_resource_role: iam.Role,
    ) -> cdk.CustomResource:
        """Create the custom resource that provisions the AgentCore agent."""
        handler = _lambda.Function(
            self,
            "AgentCoreProvisionerFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="agentcore_custom_resource.lambda_handler",
            code=_lambda.Code.from_asset(
                path=str(Path(__file__).resolve().parent),
                bundling=cdk.BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        "cp agentcore_custom_resource.py /asset-output/",
                    ],
                ),
            ),
            timeout=cdk.Duration.minutes(5),
        )

        handler.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    # New AgentCore control plane APIs surfaced under the Bedrock namespace
                    "bedrock:CreateAgent",
                    "bedrock:UpdateAgent",
                    "bedrock:ListAgents",
                    "bedrock:CreateAgentActionGroup",
                    "bedrock:UpdateAgentActionGroup",
                    "bedrock:ListAgentActionGroups",
                    "bedrock:PrepareAgent",
                    "bedrock:GetAgent",
                    # Backward compatibility while the service transitions namespaces
                    "bedrock-agent:CreateAgent",
                    "bedrock-agent:UpdateAgent",
                    "bedrock-agent:ListAgents",
                    "bedrock-agent:CreateAgentActionGroup",
                    "bedrock-agent:UpdateAgentActionGroup",
                    "bedrock-agent:ListAgentActionGroups",
                    "bedrock-agent:PrepareAgent",
                    "bedrock-agent:GetAgent",
                ],
                resources=["*"],
            )
        )

        handler.add_to_role_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=[agent_resource_role.role_arn],
            )
        )

        provider = cr.Provider(
            self,
            "AgentCoreProvisionerProvider",
            on_event_handler=handler,
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        return cdk.CustomResource(
            self,
            "AgentCoreProvisioner",
            service_token=provider.service_token,
            properties={
                "Region": self.region,
                "AgentName": agent_name,
                "RetrievalLambdaArn": retrieval_tool_lambda.function_arn,
                "AgentResourceRoleArn": agent_resource_role.role_arn,
                "AgentDefinition": json.dumps(agent_definition),
            },
        )

