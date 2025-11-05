"""
Simplified Document Processor for Demo - Minimal Dependencies

Processes PDF and creates simple text chunks for OpenSearch.
Uses only built-in libraries for quick demo setup.
"""
import json
import os
import logging
import base64
from typing import Any, Dict, List
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client("s3")
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
opensearch_endpoint = os.environ.get("OPENSEARCH_ENDPOINT", "")

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Simplified handler for demo - creates basic text chunks."""
    try:
        logger.info(f"Processing document: {event}")
        
        bucket = event.get("s3_bucket")
        key = event.get("s3_key")
        turbine_model = event.get("turbine_model", "SMT60")
        document_type = event.get("document_type", "unknown")
        
        if not bucket or not key:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "s3_bucket and s3_key required"})
            }
        
        logger.info(f"Processing s3://{bucket}/{key}")
        
        # For demo: Create mock chunks with document metadata
        # In production, this would extract text from PDF
        
        chunks = [
            {
                "text": f"Technical specifications for {turbine_model} turbine system. This document contains detailed operational parameters, performance metrics, and maintenance guidelines.",
                "metadata": {
                    "turbine_model": turbine_model,
                    "document_type": document_type,
                    "source": key,
                    "chunk_index": 0
                }
            },
            {
                "text": f"Operation procedures for {turbine_model}. Follow manufacturer guidelines for safe operation. Monitor system parameters regularly.",
                "metadata": {
                    "turbine_model": turbine_model,
                    "document_type": document_type,
                    "source": key,
                    "chunk_index": 1
                }
            },
            {
                "text": f"Troubleshooting guide for {turbine_model}. Common issues include oil pressure warnings, temperature alarms, and vibration alerts. Consult maintenance manual for detailed procedures.",
                "metadata": {
                    "turbine_model": turbine_model,
                    "document_type": document_type,
                    "source": key,
                    "chunk_index": 2
                }
            }
        ]
        
        logger.info(f"Created {len(chunks)} demo chunks")
        
        # Generate embeddings (using Bedrock Titan)
        enriched_chunks = []
        for i, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding_response = bedrock_runtime.invoke_model(
                    modelId="amazon.titan-embed-text-v1",
                    body=json.dumps({"inputText": chunk["text"]})
                )
                embedding_body = json.loads(embedding_response["body"].read())
                embedding = embedding_body.get("embedding", [])
                
                enriched_chunks.append({
                    "text": chunk["text"],
                    "embedding": embedding,
                    "metadata": chunk["metadata"]
                })
                
                logger.info(f"Generated embedding for chunk {i+1}/{len(chunks)}")
            except Exception as e:
                logger.warning(f"Failed to generate embedding for chunk {i}: {e}")
        
        # Store in OpenSearch (simplified - direct HTTP request)
        if opensearch_endpoint:
            stored_count = store_in_opensearch(enriched_chunks)
            logger.info(f"Stored {stored_count} chunks in OpenSearch")
        else:
            logger.warning("OpenSearch endpoint not configured")
            stored_count = 0
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Successfully processed {len(enriched_chunks)} chunks",
                "document": key,
                "turbine_model": turbine_model,
                "document_type": document_type,
                "chunks_stored": stored_count
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


def store_in_opensearch(chunks: List[Dict[str, Any]]) -> int:
    """Store chunks in OpenSearch using opensearch-py client."""
    try:
        from opensearchpy import OpenSearch
    except ImportError:
        # Fallback to requests if opensearch-py not available
        import urllib3
        import requests
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    username = os.environ.get("OPENSEARCH_MASTER_USER", "admin")
    password = os.environ.get("OPENSEARCH_MASTER_PASSWORD", "")
    index_name = os.environ.get("OPENSEARCH_INDEX", "turbine-documents")
    
    if not opensearch_endpoint:
        return 0
    
    stored = 0
    
    try:
        # Try using opensearch-py client
        from opensearchpy import OpenSearch
        client = OpenSearch(
            hosts=[{"host": opensearch_endpoint.replace("https://", "").replace("http://", ""), "port": 443}],
            http_auth=(username, password),
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False,
        )
        
        # Ensure index exists with k-NN mapping
        if not client.indices.exists(index=index_name):
            client.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "text": {"type": "text"},
                            "embedding": {
                                "type": "knn_vector",
                                "dimension": 1536,
                            },
                            "turbine_model": {"type": "keyword"},
                            "document_type": {"type": "keyword"},
                            "source": {"type": "keyword"},
                        }
                    }
                }
            )
        
        # Index documents
        for i, chunk in enumerate(chunks):
            try:
                doc_id = f"{chunk['metadata']['source']}-{i}".replace("/", "-")
                doc = {
                    "text": chunk["text"],
                    "embedding": chunk["embedding"],
                    "turbine_model": chunk["metadata"]["turbine_model"],
                    "document_type": chunk["metadata"]["document_type"],
                    "source": chunk["metadata"]["source"],
                }
                client.index(index=index_name, id=doc_id, body=doc)
                stored += 1
            except Exception as e:
                logger.warning(f"Failed to store chunk {i}: {e}")
                
    except ImportError:
        # Fallback to requests
        import requests
        base_url = f"https://{opensearch_endpoint}"
        for i, chunk in enumerate(chunks):
            try:
                doc_id = f"{chunk['metadata']['source']}-{i}".replace("/", "-")
                url = f"{base_url}/{index_name}/_doc/{doc_id}"
                doc = {
                    "text": chunk["text"],
                    "embedding": chunk["embedding"],
                    "turbine_model": chunk["metadata"]["turbine_model"],
                    "document_type": chunk["metadata"]["document_type"],
                    "source": chunk["metadata"]["source"],
                }
                response = requests.put(
                    url,
                    json=doc,
                    auth=(username, password),
                    verify=False,
                    timeout=10
                )
                if response.status_code in [200, 201]:
                    stored += 1
            except Exception as e:
                logger.warning(f"Failed to store chunk {i}: {e}")
    
    return stored
