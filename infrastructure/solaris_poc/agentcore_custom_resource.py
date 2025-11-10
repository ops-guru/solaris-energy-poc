"""Custom resource handler for provisioning Amazon Bedrock AgentCore agents."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict

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
        agent_resource_role_arn: str,
    ) -> None:
        self.region = region
        self.agent_name = agent_name
        self.retrieval_lambda_arn = retrieval_lambda_arn
        self.agent_definition = agent_definition
        self.agent_resource_role_arn = agent_resource_role_arn

        session = boto3.Session(region_name=region)
        self.client = session.client("bedrock-agent")

    def ensure_agent(self) -> Dict[str, Any]:
        """Create or update the agent and associated retrieval action group."""
        agent_id, agent_version = self._create_or_update_agent()
        action_group_arn = self._create_or_update_action_group(agent_id, agent_version)
        endpoint = self._prepare_agent(agent_id)

        data = {
            "AgentId": agent_id,
            "ActionGroupArn": action_group_arn,
        }
        if endpoint:
            data["AgentEndpoint"] = endpoint
        return data

    # --- internal helpers ---

    def _create_or_update_agent(self) -> tuple[str, str]:
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
                agentResourceRoleArn=self.agent_resource_role_arn,
            )
            # Bedrock may omit agentVersion from GetAgent for draft agents; fall back to the summary
            agent_version = existing.get("agentVersion")
            if not agent_version:
                agent_description = self.client.get_agent(agentId=agent_id)
                agent_version = agent_description.get("agent", {}).get("agentVersion")
            if not agent_version:
                agent_version = "DRAFT"
            return agent_id, agent_version

        logger.info("Creating new AgentCore agent %s", self.agent_name)
        response = self.client.create_agent(
            agentName=self.agent_name,
            instruction=instruction,
            foundationModel=model_id,
            description=description,
            agentResourceRoleArn=self.agent_resource_role_arn,
        )
        agent = response["agent"]
        agent_version = agent.get("agentVersion") or "DRAFT"
        return agent["agentId"], agent_version

    def _create_or_update_action_group(self, agent_id: str, agent_version: str) -> str:
        """Create or update the retrieval tool action group."""
        action_groups = self.client.list_agent_action_groups(
            agentId=agent_id,
            agentVersion=agent_version,
        )
        existing = next(
            (
                group
                for group in action_groups.get("agentActionGroupSummaries", [])
                if group.get("actionGroupName") == "RetrieveManualChunks"
            ),
            None,
        )

        executor = {
            "lambda": self.retrieval_lambda_arn,
        }

        tool_definition = self.agent_definition["tools"][0]
        input_schema = tool_definition.get("inputSchema", {}) or {"type": "object"}
        if not isinstance(input_schema, dict):
            input_schema = {"type": "object"}
        properties = input_schema.get("properties", {})
        required = set(input_schema.get("required", []))

        def resolve_type(prop: dict) -> str:
            prop_type = prop.get("type", "string")
            if isinstance(prop_type, list):
                prop_type = prop_type[0] if prop_type else "string"
            return {
                "string": "string",
                "number": "number",
                "integer": "integer",
                "boolean": "boolean",
                "array": "array",
            }.get(prop_type, "string")

        function_schema = {
            "functions": [
                {
                    "name": tool_definition.get("name", "RetrieveManualChunks"),
                    "description": tool_definition.get(
                        "description", "Retrieves relevant manual excerpts with citations."
                    ),
                    "requireConfirmation": "DISABLED",
                    "parameters": {
                        name: {
                            "description": spec.get("description", ""),
                            "type": resolve_type(spec),
                            "required": name in required,
                        }
                        for name, spec in properties.items()
                    },
                }
            ]
        }

        if existing:
            logger.info("Updating existing action group for agent %s", agent_id)
            self.client.update_agent_action_group(
                agentId=agent_id,
                agentVersion=agent_version,
                agentActionGroupId=existing["actionGroupId"],
                actionGroupName="RetrieveManualChunks",
                actionGroupExecutor=executor,
                description="Retrieves relevant manual excerpts with citations.",
                functionSchema=function_schema,
            )
            action_group_id = existing["actionGroupId"]
        else:
            logger.info("Creating action group for agent %s", agent_id)
            response = self.client.create_agent_action_group(
                agentId=agent_id,
                agentVersion=agent_version,
                actionGroupName="RetrieveManualChunks",
                description="Retrieves relevant manual excerpts with citations.",
                actionGroupExecutor=executor,
                functionSchema=function_schema,
            )
            action_group_id = response["agentActionGroup"]["agentActionGroupId"]

        detail = self.client.get_agent_action_group(
            agentId=agent_id,
            agentVersion=agent_version,
            agentActionGroupId=action_group_id,
        )
        agent_action_group = detail.get("agentActionGroup", {})
        return agent_action_group.get("agentActionGroupArn", action_group_id)

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
    agent_resource_role_arn = props["AgentResourceRoleArn"]

    if request_type == "Delete":
        # No-op: deleting the agent is optional and could surprise operators
        return {"Status": "SUCCESS"}

    provisioner = AgentCoreProvisioner(
        region=region,
        agent_name=agent_name,
        retrieval_lambda_arn=retrieval_lambda_arn,
        agent_definition=agent_definition,
        agent_resource_role_arn=agent_resource_role_arn,
    )

    try:
        result = provisioner.ensure_agent()
        physical_id = result.get("AgentId") or agent_name
        return {
            "PhysicalResourceId": physical_id,
            "Data": result,
        }
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to provision AgentCore agent: %s", exc)
        raise RuntimeError(f"Failed to provision AgentCore agent: {exc}") from exc

