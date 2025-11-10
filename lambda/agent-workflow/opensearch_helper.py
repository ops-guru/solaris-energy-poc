"""
OpenSearch Helper Module

Provides utilities for connecting to OpenSearch and performing RAG searches.
"""
import json
import boto3
import logging
from typing import Any, Dict, List, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import ConnectionTimeout
from requests.exceptions import ReadTimeout
from requests_aws4auth import AWS4Auth

logger = logging.getLogger(__name__)


def get_opensearch_client(
    endpoint: str,
    region: str = "us-east-1",
) -> OpenSearch:
    """
    Create and return an OpenSearch client using IAM authentication.
    
    Args:
        endpoint: OpenSearch domain endpoint (without https://)
        region: AWS region
    
    Returns:
        OpenSearch client instance
    """
    # Remove protocol if present
    endpoint = endpoint.replace("https://", "").replace("http://", "")
    
    # Get AWS credentials from Lambda execution role
    credentials = boto3.Session().get_credentials()
    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'es',
        session_token=credentials.token
    )
    
    # Create OpenSearch client with IAM authentication
    client = OpenSearch(
        hosts=[{"host": endpoint, "port": 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=60,
        max_retries=3,
        retry_on_timeout=True,
    )
    
    logger.info(f"OpenSearch client created for endpoint: {endpoint}")
    return client


def generate_embedding(
    text: str,
    embedding_model: str,
    region: str = "us-east-1",
) -> List[float]:
    """
    Generate embedding vector using Bedrock Titan.
    
    Args:
        text: Text to embed
        embedding_model: Bedrock model ID
        region: AWS region
    
    Returns:
        Embedding vector as list of floats
    """
    bedrock = boto3.client("bedrock-runtime", region_name=region)
    
    # Prepare request
    body = json.dumps({"inputText": text})
    
    # Invoke Bedrock
    response = bedrock.invoke_model(
        modelId=embedding_model,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    
    # Parse response
    response_body = json.loads(response["body"].read())
    embedding = response_body.get("embedding", [])
    
    logger.debug(f"Generated embedding of length {len(embedding)}")
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
    """
    Perform hybrid search (semantic + keyword) on OpenSearch.
    
    Args:
        client: OpenSearch client
        index: Index name
        query: Search query text
        filters: Optional metadata filters (e.g., {"turbine_model": "SMT60"})
        top_k: Number of results to return
        embedding_model: Bedrock embedding model ID
        region: AWS region
    
    Returns:
        List of document results with content and metadata
    """
    try:
        # Generate embedding for semantic search
        query_embedding = generate_embedding(query, embedding_model, region)
        
        # Build search query
        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        # Semantic search (k-NN)
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding,
                                    "k": top_k,
                                }
                            }
                        },
                        # Keyword search (BM25)
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
            "_source": ["text", "metadata", "source", "turbine_model", "document_type"],
        }
        
        # Add metadata filters
        if filters:
            filter_clauses = []
            for key, value in filters.items():
                # Try both direct field and metadata.field paths
                if key == "turbine_model":
                    filter_clauses.append({"term": {"turbine_model": value}})
                elif key == "document_type":
                    filter_clauses.append({"term": {"document_type": value}})
                else:
                    # Fallback to metadata path
                    filter_clauses.append({"term": {f"metadata.{key}.keyword": value}})
            
            if filter_clauses:
                search_query["query"]["bool"]["must"] = filter_clauses
        
        # Execute search
        response = client.search(
            index=index,
            body=search_query,
            request_timeout=25,
        )
        
        # Format results
        results = []
        for hit in response.get("hits", {}).get("hits", []):
            source = hit["_source"]
            results.append({
                "content": source.get("text", ""),
                "source": source.get("source", "Unknown"),
                "page": source.get("metadata", {}).get("page"),
                "turbine_model": source.get("turbine_model"),
                "document_type": source.get("document_type"),
                "score": hit.get("_score", 0.0),
                "metadata": source.get("metadata", {}),
            })
        
        logger.info(f"Search returned {len(results)} results for query: {query[:50]}")
        return results
        
    except (ConnectionTimeout, ReadTimeout) as timeout_error:
        logger.warning("OpenSearch query timed out: %s", timeout_error)
        return []
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        return []
