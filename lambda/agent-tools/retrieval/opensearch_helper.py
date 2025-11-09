"""
Shared OpenSearch helper functions reused by AgentCore tool Lambda.
"""
import json
import boto3
import logging
from typing import Any, Dict, List, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import ConnectionTimeout
from requests_aws4auth import AWS4Auth

logger = logging.getLogger(__name__)


def get_opensearch_client(
    endpoint: str,
    region: str = "us-east-1",
) -> OpenSearch:
    """Create and return an OpenSearch client using IAM authentication."""
    endpoint = endpoint.replace("https://", "").replace("http://", "")
    credentials = boto3.Session().get_credentials()
    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        "es",
        session_token=credentials.token,
    )

    client = OpenSearch(
        hosts=[{"host": endpoint, "port": 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=10,
    )
    return client


def generate_embedding(
    text: str,
    model_id: str = "amazon.titan-embed-text-v1",
    region: str = "us-east-1",
) -> List[float]:
    """Generate embeddings using Bedrock Titan embedding model."""
    bedrock = boto3.client("bedrock-runtime", region_name=region)
    payload = json.dumps({"inputText": text})
    response = bedrock.invoke_model(modelId=model_id, body=payload)
    response_body = json.loads(response["body"].read())
    embedding = response_body.get("embedding", [])
    if not embedding:
        logger.warning("Received empty embedding response")
    return embedding


def search_documents(
    client: OpenSearch,
    index: str,
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 5,
    embedding_model: str = "amazon.titan-embed-text-v1",
    region: str = "us-east-1",
) -> List[Dict[str, Any]]:
    """Perform hybrid search (semantic + keyword) on OpenSearch."""
    try:
        query_embedding = generate_embedding(query, embedding_model, region)

        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding,
                                    "k": top_k,
                                }
                            }
                        },
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["text^2", "source"],
                                "type": "best_fields",
                                "fuzziness": "AUTO",
                            }
                        },
                    ],
                    "must": [],
                    "minimum_should_match": 1,
                }
            },
            "_source": [
                "text",
                "metadata",
                "source",
                "turbine_model",
                "document_type",
            ],
        }

        if filters:
            filter_clauses = []
            for key, value in filters.items():
                if key in ("turbine_model", "document_type"):
                    filter_clauses.append({"term": {key: value}})
                else:
                    filter_clauses.append({"term": {f"metadata.{key}.keyword": value}})

            if filter_clauses:
                search_query["query"]["bool"]["must"] = filter_clauses

        response = client.search(
            index=index,
            body=search_query,
            request_timeout=10,
        )

        results = []
        for hit in response.get("hits", {}).get("hits", []):
            source = hit["_source"]
            results.append(
                {
                    "content": source.get("text", ""),
                    "source": source.get("source", "Unknown"),
                    "page": source.get("metadata", {}).get("page"),
                    "turbine_model": source.get("turbine_model"),
                    "document_type": source.get("document_type"),
                    "score": hit.get("_score", 0.0),
                    "metadata": source.get("metadata", {}),
                }
            )

        logger.info("Search returned %s results for query: %s", len(results), query[:50])
        return results

    except ConnectionTimeout as timeout_error:
        logger.warning("OpenSearch query timed out: %s", timeout_error)
        return []
    except Exception as error:  # pylint: disable=broad-except
        logger.error("Search error: %s", error, exc_info=True)
        return []

