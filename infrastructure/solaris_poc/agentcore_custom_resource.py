"""Custom resource handler for provisioning Amazon Bedrock AgentCore agents."""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AgentCoreProvisioner:
    """Wrapper around the Bedrock AgentCore control plane APIs."""

    def __init__(
        self,
        region: str,
        agent_name: str,
        retrieval_lambda_arn: str,
        agent_definition: Dict[str, Any],
    ) -> None:
        self.region = region
        self.agent_name = agent_name
        self.retrieval_lambda_arn = retrieval_lambda_arn
        self.agent_definition = agent_definition

        session = boto3.Session(region_name=region)
        self.client = session.client("bedrock-agent")

    def ensure_agent(self) -> Dict[str, Any]:
        """Create or update the agent and associated retrieval action group."""
        agent_id = self._create_or_update_agent()
        action_group_arn = self._create_or_update_action_group(agent_id)
        endpoint = self._prepare_agent(agent_id)

        data = {
            "AgentId": agent_id,
            "ActionGroupArn": action_group_arn,
        }
        if endpoint:
            data["AgentEndpoint"] = endpoint
        return data

    # --- internal helpers ---

    def _create_or_update_agent(self) -> str:
        """Create the agent if it does not exist, otherwise update."""
        try:
            response = self.client.list_agents()
            existing = next(
                (agent for agent in response.get("agentSummaries", []) if agent["agentName"] == self.agent_name),
                None,
            )
        except self.client.exceptions.ValidationException:
            existing = None

        instruction = self.agent_definition.get("instructions", "")
        model_id = self.agent_definition.get("defaultModelId")
        description = self.agent_definition.get("description", "")

        if existing:
            agent_id = existing["agentId"]
            logger.info("Updating existing AgentCore agent %s", agent_id)
            self.client.update_agent(
                agentId=agent_id,
                agentName=self.agent_name,
                instruction=instruction,
                foundationModel=model_id,
                description=description,
            )
            return agent_id

        logger.info("Creating new AgentCore agent %s", self.agent_name)
        response = self.client.create_agent(
            agentName=self.agent_name,
            instruction=instruction,
            foundationModel=model_id,
            description=description,
        )
        return response["agent"]["agentId"]

    def _create_or_update_action_group(self, agent_id: str) -> str:
        """Create or update the retrieval tool action group."""
        action_groups = self.client.list_agent_action_groups(agentId=agent_id)
        existing = next(
            (
                group
                for group in action_groups.get("agentActionGroupSummaries", [])
                if group["agentActionGroupName"] == "RetrieveManualChunks"
            ),
            None,
        )

        executor = {
            "lambda": {
                "lambdaArn": self.retrieval_lambda_arn,
            }
        }

        input_schema = self.agent_definition["tools"][0].get("inputSchema", {})

        if existing:
            logger.info("Updating existing action group for agent %s", agent_id)
            self.client.update_agent_action_group(
                agentId=agent_id,
                agentActionGroupId=existing["agentActionGroupId"],
                agentActionGroupName="RetrieveManualChunks",
                actionGroupExecutor=executor,
                description="Retrieves relevant turbine manual excerpts with citations.",
                apiSchema={"payload": json.dumps(input_schema)},
            )
            return existing["agentActionGroupArn"]

        logger.info("Creating action group for agent %s", agent_id)
        response = self.client.create_agent_action_group(
            agentId=agent_id,
            agentActionGroupName="RetrieveManualChunks",
            description="Retrieves relevant turbine manual excerpts with citations.",
            actionGroupExecutor=executor,
            apiSchema={"payload": json.dumps(input_schema)},
        )
        return response["agentActionGroup"]["agentActionGroupArn"]

    def _prepare_agent(self, agent_id: str) -> str:
        """Publish the agent to make it invokable and return the endpoint."""
        logger.info("Preparing agent %s for invocation", agent_id)
        self.client.prepare_agent(agentId=agent_id)
        # The endpoint is returned via get_agent once the rollout completes
        response = self.client.get_agent(agentId=agent_id)
        agent = response.get("agent", {})
        # agentArn is populated once the deployment finishes preparing. Fallback to agentId.
        return agent.get("agentArn") or agent.get("agentId") or agent_id


def lambda_handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    """Entry point for the CloudFormation custom resource."""
    logger.info("Received event: %s", json.dumps(event))
    request_type = event["RequestType"]

    props = event["ResourceProperties"]
    region = props["Region"]
    agent_name = props["AgentName"]
    retrieval_lambda_arn = props["RetrievalLambdaArn"]
    agent_definition = json.loads(props["AgentDefinition"])

    if request_type == "Delete":
        # No-op: deleting the agent is optional and could surprise operators
        return {"Status": "SUCCESS"}

    provisioner = AgentCoreProvisioner(
        region=region,
        agent_name=agent_name,
        retrieval_lambda_arn=retrieval_lambda_arn,
        agent_definition=agent_definition,
    )

    try:
        result = provisioner.ensure_agent()
        return {
            "Status": "SUCCESS",
            "Data": result,
        }
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to provision AgentCore agent: %s", exc)
        return {
            "Status": "FAILED",
            "Reason": str(exc),
        }

