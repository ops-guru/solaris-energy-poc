"""
API Handler Lambda for Chat Endpoints

Handles:
- POST /chat - Send query to agent workflow
- GET /chat/{session_id} - Get session history
- DELETE /chat/{session_id} - Delete session
"""
import json
import os
import logging
from typing import Any, Dict
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
AGENT_WORKFLOW_FUNCTION_NAME = os.environ.get("AGENT_WORKFLOW_FUNCTION_NAME", "")
SESSIONS_TABLE_NAME = os.environ.get("SESSIONS_TABLE_NAME", "solaris-poc-sessions")

# AWS clients
lambda_client = boto3.client("lambda")
dynamodb = boto3.resource("dynamodb")
sessions_table = dynamodb.Table(SESSIONS_TABLE_NAME)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    API Gateway Lambda proxy integration handler.
    
    Routes:
    - POST /chat -> process_query
    - GET /chat/{session_id} -> get_session_history
    - DELETE /chat/{session_id} -> delete_session
    """
    try:
        http_method = event.get("httpMethod", "")
        path = event.get("path", "")
        path_parameters = event.get("pathParameters") or {}
        body = event.get("body", "{}")

        logger.info(f"Received {http_method} {path}")

        # Route based on HTTP method and path
        if http_method == "POST" and path == "/chat":
            return process_query(json.loads(body) if body else {})

        elif http_method == "GET" and path.startswith("/chat/"):
            session_id = path_parameters.get("session_id") or path.split("/")[-1]
            return get_session_history(session_id)

        elif http_method == "DELETE" and path.startswith("/chat/"):
            session_id = path_parameters.get("session_id") or path.split("/")[-1]
            return delete_session(session_id)

        else:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Not found"}),
            }

    except Exception as e:
        logger.error(f"Handler error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }


def process_query(body: Dict[str, Any]) -> Dict[str, Any]:
    """Process a chat query by invoking the agent workflow Lambda."""
    try:
        query = body.get("query", "").strip()
        session_id = body.get("session_id", "").strip()

        if not query:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Query is required"}),
            }

        # Generate session ID if not provided
        if not session_id:
            import uuid
            session_id = f"session-{uuid.uuid4().hex[:12]}"

        # Load session history from DynamoDB
        try:
            response = sessions_table.get_item(Key={"session_id": session_id})
            messages = response.get("Item", {}).get("messages", [])
        except ClientError as e:
            logger.warning(f"Could not load session: {e}")
            messages = []

        # Prepare payload for agent workflow
        payload = {
            "session_id": session_id,
            "query": query,
            "messages": messages,
        }

        # Invoke agent workflow Lambda
        response = lambda_client.invoke(
            FunctionName=AGENT_WORKFLOW_FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )

        # Parse response
        response_payload = json.loads(response["Payload"].read())
        workflow_response = json.loads(response_payload.get("body", "{}"))

        if response_payload.get("statusCode") != 200:
            return {
                "statusCode": response_payload.get("statusCode", 500),
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps(workflow_response),
            }

        # Save updated session to DynamoDB
        try:
            from datetime import datetime, timedelta

            sessions_table.put_item(
                Item={
                    "session_id": session_id,
                    "messages": workflow_response.get("messages", []),
                    "last_updated": datetime.utcnow().isoformat(),
                    "ttl": int(
                        (datetime.utcnow() + timedelta(days=30)).timestamp()
                    ),  # 30 day TTL
                }
            )
        except ClientError as e:
            logger.warning(f"Could not save session: {e}")

        # Return response
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "session_id": session_id,
                "response": workflow_response.get("response", ""),
                "citations": workflow_response.get("citations", []),
                "confidence_score": workflow_response.get("confidence_score", 0.0),
                "turbine_model": workflow_response.get("turbine_model"),
            }),
        }

    except Exception as e:
        logger.error(f"Process query error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }


def get_session_history(session_id: str) -> Dict[str, Any]:
    """Retrieve session history from DynamoDB."""
    try:
        if not session_id:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Session ID is required"}),
            }

        response = sessions_table.get_item(Key={"session_id": session_id})
        item = response.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Session not found"}),
            }

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "session_id": session_id,
                "messages": item.get("messages", []),
                "last_updated": item.get("last_updated"),
            }),
        }

    except Exception as e:
        logger.error(f"Get session history error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }


def delete_session(session_id: str) -> Dict[str, Any]:
    """Delete a session from DynamoDB."""
    try:
        if not session_id:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Session ID is required"}),
            }

        sessions_table.delete_item(Key={"session_id": session_id})

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Session deleted"}),
        }

    except Exception as e:
        logger.error(f"Delete session error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }
