"""AgentCore configuration stack."""
from __future__ import annotations

import json
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import (
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_ssm as ssm,
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

