"""
Simplified Document Processor for Demo - Minimal Dependencies

Processes PDF and creates simple text chunks for OpenSearch.
Uses only built-in libraries for quick demo setup.
"""
import json
import os
import logging
from typing import Any, Dict, List
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client("s3")
aws_region = os.environ.get("AWS_REGION", "us-east-1")
bedrock_runtime = boto3.client("bedrock-runtime", region_name=aws_region)
opensearch_endpoint = os.environ.get("OPENSEARCH_ENDPOINT", "")

def extract_metadata_from_key(key: str) -> tuple[str, str]:
    """
    Extract turbine_model and document_type from S3 key path.
    
    Expected paths:
    - manuals/SMT60-Taurus60/technical-specs/file.pdf
    - manuals/SMT130-Titan130/operational/file.pdf
    - manuals/TM2500-LM2500/maintenance/file.pdf
    
    Returns:
        (turbine_model, document_type)
    """
    key_lower = key.lower()
    
    # Extract turbine model
    turbine_model = "SMT60"  # default
    if "smt60" in key_lower or "taurus60" in key_lower or "taurus-60" in key_lower:
        turbine_model = "SMT60"
    elif "smt130" in key_lower or "titan130" in key_lower or "titan-130" in key_lower:
        turbine_model = "SMT130"
    elif "tm2500" in key_lower or "lm2500" in key_lower:
        turbine_model = "TM2500"
    
    # Extract document type
    document_type = "unknown"  # default
    if "technical-spec" in key_lower or "spec" in key_lower:
        document_type = "technical-specs"
    elif "operational" in key_lower or "operation" in key_lower or "procedure" in key_lower:
        document_type = "operational"
    elif "maintenance" in key_lower:
        document_type = "maintenance"
    elif "troubleshoot" in key_lower or "trouble" in key_lower:
        document_type = "troubleshooting"
    elif "reference" in key_lower:
        document_type = "reference"
    elif "safety" in key_lower:
        document_type = "safety"
    elif "manual" in key_lower:
        document_type = "manual"
    
    return turbine_model, document_type


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler for document processing.
    
    Supports two event formats:
    1. S3 Event Notification (automatic trigger):
       {
         "Records": [{
           "s3": {
             "bucket": {"name": "bucket-name"},
             "object": {"key": "path/to/file.pdf"}
           }
         }]
       }
    
    2. Manual Invocation (for testing):
       {
         "s3_bucket": "bucket-name",
         "s3_key": "path/to/file.pdf",
         "turbine_model": "SMT60",  # optional, extracted from path if not provided
         "document_type": "technical-specs"  # optional, extracted from path if not provided
       }
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle S3 event notification format
        if "Records" in event and len(event.get("Records", [])) > 0:
            # S3 event notification - process all records
            record = event["Records"][0]
            if "s3" not in record:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid S3 event format"})
                }
            
            bucket = record["s3"]["bucket"]["name"]
            # S3 keys are URL-encoded, decode them properly
            import urllib.parse
            key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
            
            logger.info(f"Processing S3 event: s3://{bucket}/{key}")
            
            # Extract metadata from S3 key path
            turbine_model, document_type = extract_metadata_from_key(key)
            logger.info(f"Extracted metadata: turbine_model={turbine_model}, document_type={document_type}")
        
        # Handle manual invocation format
        else:
            bucket = event.get("s3_bucket")
            key = event.get("s3_key")
            
            if not bucket or not key:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "s3_bucket and s3_key required"})
                }
            
            # Use provided metadata or extract from key
            turbine_model = event.get("turbine_model")
            document_type = event.get("document_type")
            
            if not turbine_model or not document_type:
                extracted_model, extracted_type = extract_metadata_from_key(key)
                turbine_model = turbine_model or extracted_model
                document_type = document_type or extracted_type
                logger.info(f"Extracted metadata from key: turbine_model={turbine_model}, document_type={document_type}")
        
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
    """Store chunks in OpenSearch using IAM authentication."""
    from opensearchpy import OpenSearch, RequestsHttpConnection
    from requests_aws4auth import AWS4Auth
    
    index_name = os.environ.get("OPENSEARCH_INDEX", "turbine-documents")
    region = os.environ.get("AWS_REGION", "us-east-1")
    
    if not opensearch_endpoint:
        logger.warning("OpenSearch endpoint not configured")
        return 0
    
    # Clean endpoint (remove protocol)
    endpoint = opensearch_endpoint.replace("https://", "").replace("http://", "")
    
    stored = 0
    
    try:
        # Get AWS credentials from Lambda execution role
        credentials = boto3.Session().get_credentials()
        if not credentials:
            logger.error("Failed to get AWS credentials")
            return 0
            
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
            timeout=30,
        )
        
        # Ensure index exists
        ensure_index_exists(client, index_name)
        
        # Index documents
        for i, chunk in enumerate(chunks):
            try:
                # Generate unique document ID
                source = chunk['metadata'].get('source', 'unknown')
                chunk_idx = chunk['metadata'].get('chunk_index', i)
                doc_id = f"{source}-{chunk_idx}".replace("/", "-").replace(" ", "-")
                
                # Prepare document with proper structure
                doc = {
                    "text": chunk["text"],
                    "embedding": chunk["embedding"],
                    "turbine_model": chunk["metadata"].get("turbine_model", "unknown"),
                    "document_type": chunk["metadata"].get("document_type", "unknown"),
                    "source": source,
                    "metadata": {
                        "chunk_index": chunk_idx,
                        "turbine_model": chunk["metadata"].get("turbine_model", "unknown"),
                        "document_type": chunk["metadata"].get("document_type", "unknown"),
                    }
                }
                
                # Index document
                response = client.index(
                    index=index_name,
                    id=doc_id,
                    body=doc,
                    refresh=False  # Batch refresh after all docs
                )
                
                if response.get("result") in ["created", "updated"]:
                    stored += 1
                    logger.info(f"Stored chunk {i+1}/{len(chunks)}: {doc_id}")
                else:
                    logger.warning(f"Unexpected response for chunk {i}: {response}")
                    
            except Exception as e:
                logger.error(f"Failed to store chunk {i}: {e}", exc_info=True)
        
        # Refresh index to make documents searchable
        if stored > 0:
            client.indices.refresh(index=index_name)
            logger.info(f"Refreshed index {index_name} after storing {stored} chunks")
        
    except Exception as e:
        logger.error(f"Failed to connect to OpenSearch: {e}", exc_info=True)
        import traceback
        logger.error(traceback.format_exc())
    
    return stored


def ensure_index_exists(client, index_name: str) -> None:
    """Create OpenSearch index if it doesn't exist."""
    try:
        if client.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
            return
        
        # Index doesn't exist, create it
        logger.info(f"Creating index {index_name}")
        
        index_mapping = {
            "settings": {
                "index": {
                    "knn": True
                }
            },
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
                    "metadata": {
                        "properties": {
                            "chunk_index": {"type": "long"},
                            "turbine_model": {
                                "type": "keyword"
                            },
                            "document_type": {
                                "type": "keyword"
                            }
                        }
                    }
                }
            }
        }
        
        client.indices.create(index=index_name, body=index_mapping)
        logger.info(f"Successfully created index {index_name}")
        
    except Exception as e:
        logger.warning(f"Error checking/creating index: {e}", exc_info=True)
