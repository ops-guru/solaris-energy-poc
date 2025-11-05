"""
Simple Mock Agent Workflow Lambda Handler for Demo

Returns a working response quickly without full LangGraph processing.
"""
import json
import logging
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Simple mock handler for demo purposes.
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle API Gateway proxy integration
        if "httpMethod" in event or "requestContext" in event:
            body_str = event.get("body", "{}")
            if isinstance(body_str, str):
                body = json.loads(body_str)
            else:
                body = body_str
            
            session_id = body.get("session_id", f"session-{datetime.now().isoformat()}")
            query = body.get("query", "")
        else:
            # Direct invocation format
            session_id = event.get("session_id", f"session-{datetime.now().isoformat()}")
            query = event.get("query", "")
        
        if not query:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Query is required"}),
            }
        
        # Mock response for demo
        response_text = f"""Thank you for your question: "{query}"

This is a demo response from the Solaris Energy Operator Assistant. 

**Demo Features:**
- ✅ API Gateway integration working
- ✅ Lambda function responding
- ✅ Session management active
- ✅ RAG infrastructure ready

**Next Steps:**
- Process turbine manuals into OpenSearch
- Enable full LangGraph workflow
- Connect to real documentation

**Session ID:** {session_id}"""

        # Return mock response
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "session_id": session_id,
                "response": response_text,
                "citations": [
                    {
                        "source": "Demo Documentation",
                        "page": 1,
                        "excerpt": "This is a demo citation for testing purposes."
                    }
                ],
                "confidence_score": 0.85,
                "turbine_model": "SMT60",
                "messages": [
                    {"role": "user", "content": query, "timestamp": datetime.now().isoformat()},
                    {"role": "assistant", "content": response_text, "timestamp": datetime.now().isoformat()}
                ],
                "error": None,
            }),
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }
