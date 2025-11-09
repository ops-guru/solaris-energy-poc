"""
Agent Workflow Lambda Handler with RAG

Performs retrieval-augmented generation using OpenSearch vector store.
"""
import json
import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3

# Import OpenSearch and LLM helpers
try:
    from opensearch_helper import (
        get_opensearch_client,
        search_documents,
    )
    OPENSEARCH_AVAILABLE = True
except ImportError:
    OPENSEARCH_AVAILABLE = False
    logging.warning("OpenSearch helper not available")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Standard CORS headers for API Gateway proxy integration
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Api-Key",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
}

# Environment variables
OPENSEARCH_ENDPOINT = os.environ.get("OPENSEARCH_ENDPOINT", "")
OPENSEARCH_INDEX = os.environ.get("OPENSEARCH_INDEX", "turbine-documents")
EMBEDDING_MODEL = os.environ.get(
    "EMBEDDING_MODEL", "amazon.titan-embed-text-v1"
)
LLM_MODEL = os.environ.get(
    "LLM_MODEL", "amazon.nova-pro-v1:0"
)
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DOCUMENTS_BUCKET = os.environ.get("DOCUMENTS_BUCKET", "")

S3_CLIENT = boto3.client("s3") if DOCUMENTS_BUCKET else None


def invoke_bedrock_llm(
    prompt: str, context: str = "", conversation_history: List[Dict] = None
) -> str:
    """Invoke Bedrock LLM with prompt and context."""
    import boto3
    
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    
    # Build system message
    system_message = (
        "You are an expert assistant for gas turbine operations and "
        "troubleshooting. Use the provided documentation context to answer "
        "questions accurately. Always cite your sources. If the context "
        "doesn't contain relevant information, say so clearly."
    )
    
    # Build user prompt with context
    user_content = prompt
    if context:
        user_content = (
            f"Context from documentation:\n{context}\n\n"
            f"User question: {prompt}\n\n"
            "Please answer the question using the context above. "
            "If the context is relevant, cite the sources. If not, "
            "acknowledge that you don't have that information in the "
            "provided documentation."
        )
    
    # Build messages array for Nova Pro (only user and assistant roles)
    messages = []
    
    # Add conversation history if available
    if conversation_history:
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            # Convert to Nova format (only user and assistant roles allowed)
            if role in ["user", "assistant"]:
                messages.append({
                    "role": role,
                    "content": [{"text": content}]
                })
    
    # Add current user message
    messages.append({
        "role": "user",
        "content": [{"text": user_content}]
    })
    
    # Nova Pro uses messages format with system as separate field (not in messages array)
    body = {
        "system": [{"text": system_message}],  # System message passed separately
        "messages": messages,  # Only user and assistant roles
        "inferenceConfig": {
            "maxTokens": 2048,
            "temperature": 0.7,
            "topP": 0.9,
        }
    }
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId=LLM_MODEL,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response["body"].read())
        # Nova Pro returns output.message.content array
        output = response_body.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])
        if content and len(content) > 0:
            return content[0].get("text", "")
        return ""
    except Exception as e:
        logger.error(f"Bedrock LLM error: {e}", exc_info=True)
        return f"I encountered an error generating a response: {str(e)}"


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Agent workflow handler with RAG retrieval.
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
            messages = body.get("messages", [])
        else:
            # Direct invocation format
            session_id = event.get("session_id", f"session-{datetime.now().isoformat()}")
            query = event.get("query", "")
            messages = event.get("messages", [])
        
        if not query:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Query is required"}),
            }
        
        # Step 1: Perform RAG retrieval from OpenSearch
        retrieved_docs = []
        citations = []
        turbine_model = None
        
        if OPENSEARCH_AVAILABLE and OPENSEARCH_ENDPOINT:
            try:
                # Connect to OpenSearch (using IAM authentication)
                opensearch_client = get_opensearch_client(
                    OPENSEARCH_ENDPOINT,
                    AWS_REGION
                )
                
                # Extract turbine model from query if mentioned
                query_lower = query.lower()
                if "smt60" in query_lower or "smt 60" in query_lower:
                    turbine_model = "SMT60"
                elif "smt130" in query_lower or "smt 130" in query_lower:
                    turbine_model = "SMT130"
                elif "tm2500" in query_lower:
                    turbine_model = "TM2500"
                
                # Build filters if turbine model detected
                filters = {"turbine_model": turbine_model} if turbine_model else None
                
                # Search OpenSearch
                retrieved_docs = search_documents(
                    opensearch_client,
                    OPENSEARCH_INDEX,
                    query,
                    filters=filters,
                    top_k=5,
                    embedding_model=EMBEDDING_MODEL,
                    region=AWS_REGION
                )
                
                # Build citations from results
                max_raw_score = max(
                    (doc.get("score", 0.0) for doc in retrieved_docs), default=0.0
                )

                for doc in retrieved_docs:
                    raw_score = doc.get("score", 0.0)
                    normalized_score = (
                        raw_score / max_raw_score if max_raw_score > 0 else 0.0
                    )
                    normalized_score = min(max(normalized_score, 0.0), 1.0)

                    source = doc.get("source", "Unknown")
                    page = doc.get("page")
                    excerpt = doc.get("content", "")
                    if len(excerpt) > 250:
                        excerpt = f"{excerpt[:247]}..."

                    citations.append({
                        "source": source,
                        "page": page,
                        "excerpt": excerpt,
                        "relevance_score": normalized_score,
                        "url": generate_presigned_document_url(source, page),
                    })

                logger.info(
                    f"Retrieved {len(retrieved_docs)} docs from OpenSearch"
                )
                
            except Exception as e:
                logger.warning(f"OpenSearch retrieval error: {e}", exc_info=True)
                # Continue without RAG if OpenSearch fails
        
        # Step 2: Build context from retrieved documents
        context = ""
        if retrieved_docs:
            context_parts = []
            for i, doc in enumerate(retrieved_docs, 1):
                source = doc.get("source", "Unknown")
                content = doc.get("content", "")
                context_parts.append(f"[Document {i} - Source: {source}]\n{content}\n")
            context = "\n".join(context_parts)
        else:
            context = "No relevant documentation found in the knowledge base."
            logger.info("No documents retrieved from OpenSearch")
        
        # Step 3: Generate LLM response with context
        response_text = invoke_bedrock_llm(query, context, messages)
        
        # Step 4: Calculate confidence score based on retrieval quality
        if not retrieved_docs:
            confidence_score = 0.5
        elif not citations:
            confidence_score = 0.6
        else:
            confidence_score = calculate_confidence_from_scores(
                [c.get("relevance_score", 0.0) for c in citations]
            )
        
        # Step 5: Build response
        response_data = {
            "session_id": session_id,
            "response": response_text,
            "citations": citations,
            "confidence_score": confidence_score,
            "turbine_model": turbine_model,
            "messages": messages + [
                {"role": "user", "content": query, "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": response_text, "timestamp": datetime.now().isoformat()}
            ],
            "error": None,
        }
        
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(response_data),
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": str(e),
                "session_id": event.get("session_id", "unknown"),
                "response": "I encountered an error processing your request.",
                "citations": [],
                "confidence_score": 0.0,
            }),
        }


def generate_presigned_document_url(
    source_key: Optional[str], page: Optional[int]
) -> Optional[str]:
    """Return a pre-signed URL to the source document, optionally anchored to a page."""
    if not DOCUMENTS_BUCKET or not S3_CLIENT or not source_key:
        return None

    try:
        presigned = S3_CLIENT.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": DOCUMENTS_BUCKET,
                "Key": source_key,
            },
            ExpiresIn=3600,
        )

        if page:
            return f"{presigned}#page={page}"
        return presigned
    except Exception as error:  # pylint: disable=broad-except
        logger.warning(
            "Failed to generate pre-signed URL for %s: %s",
            source_key,
            error,
        )
        return None


def calculate_confidence_from_scores(scores: List[float]) -> float:
    """Map normalized relevance scores (0-1) to a confidence value."""
    if not scores:
        return 0.6

    avg_score = sum(scores) / len(scores)
    # Base confidence at 0.6, add up to 0.35 based on average relevance
    return min(0.95, 0.6 + (avg_score * 0.35))
