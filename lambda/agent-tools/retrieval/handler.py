"""
AgentCore Retrieval Tool Lambda

Provides an OpenSearch-backed retrieval API that returns citations, excerpts,
and pre-signed document links aligned with AgentCore tool contract.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

import boto3

from opensearch_helper import (
    get_opensearch_client,
    search_documents,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

OPENSEARCH_ENDPOINT = os.environ.get("OPENSEARCH_ENDPOINT", "")
OPENSEARCH_INDEX = os.environ.get("OPENSEARCH_INDEX", "turbine-documents")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "amazon.titan-embed-text-v1")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DOCUMENTS_BUCKET = os.environ.get("DOCUMENTS_BUCKET", "")

S3_CLIENT = boto3.client("s3") if DOCUMENTS_BUCKET else None


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Entry point compatible with AgentCore tool invocation."""
    logger.info("Received event: %s", json.dumps(event))

    try:
        request = _parse_event(event)
    except ValueError as error:
        return _response(400, {"error": str(error)})

    try:
        opensearch_client = get_opensearch_client(OPENSEARCH_ENDPOINT, AWS_REGION)
        documents = search_documents(
            opensearch_client,
            OPENSEARCH_INDEX,
            request["query"],
            filters=request.get("filters"),
            top_k=request.get("top_k", 5),
            embedding_model=EMBEDDING_MODEL,
            region=AWS_REGION,
        )
    except Exception as error:  # pylint: disable=broad-except
        logger.error("Search error: %s", error, exc_info=True)
        return _response(500, {"error": "Retrieval failure"})

    citations = _format_results(documents)

    return _response(
        200,
        {
            "query": request["query"],
            "citations": citations,
            "result_count": len(citations),
        },
    )


def _parse_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize incoming AgentCore tool invocation payload."""
    if "body" in event:
        payload = event["body"]
        if isinstance(payload, str):
            payload = json.loads(payload or "{}")
    else:
        payload = event

    query = (payload.get("query") or "").strip()
    if not query:
        raise ValueError("query is required")

    filters = payload.get("filters")
    if filters and not isinstance(filters, dict):
        raise ValueError("filters must be an object when provided")

    result = {
        "query": query,
        "filters": filters,
        "top_k": min(int(payload.get("top_k", 5)), 20),
    }
    logger.info("Parsed request: %s", json.dumps(result))
    return result


def _format_results(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare citation payload with normalized scores and pre-signed links."""
    if not documents:
        return []

    max_score = max(doc.get("score", 0.0) for doc in documents) or 1.0

    citations: List[Dict[str, Any]] = []
    for doc in documents:
        source = doc.get("source", "unknown")
        metadata = doc.get("metadata") or {}
        page = metadata.get("page")

        normalized = max(min(doc.get("score", 0.0) / max_score, 1.0), 0.0)

        excerpt = doc.get("content", "")
        if len(excerpt) > 500:
            excerpt = f"{excerpt[:497]}..."

        citations.append(
            {
                "source": source,
                "page": page,
                "excerpt": excerpt,
                "relevance_score": normalized,
                "url": _generate_presigned_url(source, page),
                "turbine_model": doc.get("turbine_model"),
                "document_type": doc.get("document_type"),
            }
        )

    return citations


def _generate_presigned_url(
    object_key: Optional[str], page: Optional[int]
) -> Optional[str]:
    if not DOCUMENTS_BUCKET or not S3_CLIENT or not object_key:
        return None

    try:
        url = S3_CLIENT.generate_presigned_url(
            "get_object",
            Params={"Bucket": DOCUMENTS_BUCKET, "Key": object_key},
            ExpiresIn=900,
        )
        if page:
            return f"{url}#page={page}"
        return url
    except Exception as error:  # pylint: disable=broad-except
        logger.warning("Failed to sign URL for %s: %s", object_key, error)
        return None


def _response(status: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
        },
        "body": json.dumps(body),
    }

