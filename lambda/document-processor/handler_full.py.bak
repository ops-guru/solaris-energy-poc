"""
Document Processor Lambda Function

Processes PDF documents from S3, extracts text with hierarchical chunking,
generates embeddings, and stores vectors in OpenSearch for RAG retrieval.
"""
import json
import os
import boto3
from typing import Dict, Any, List
import logging
import io
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import pdfplumber
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime')

# Configuration from environment variables
OPENSEARCH_ENDPOINT = os.environ.get('OPENSEARCH_ENDPOINT')
OPENSEARCH_INDEX = os.environ.get('OPENSEARCH_INDEX', 'turbine-documents')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'amazon.titan-embed-text-v1')
OPENSEARCH_MASTER_USER = os.environ.get('OPENSEARCH_MASTER_USER', 'admin')
OPENSEARCH_MASTER_PASSWORD = os.environ.get('OPENSEARCH_MASTER_PASSWORD')

# OpenSearch client (initialized on first use)
opensearch_client = None


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for document processing.

    Expected event format:
    {
        "s3_bucket": "bucket-name",
        "s3_key": "path/to/document.pdf",
        "turbine_model": "SMT60",
        "document_type": "technical-specs"
    }
    """
    try:
        logger.info(f"Processing document: {event}")

        # Extract document info from event
        bucket = event.get('s3_bucket')
        key = event.get('s3_key')
        turbine_model = event.get('turbine_model', 'general')
        document_type = event.get('document_type', 'unknown')

        if not bucket or not key:
            raise ValueError("s3_bucket and s3_key are required in event")

        # Load PDF from S3
        logger.info(f"Loading PDF from s3://{bucket}/{key}")
        documents = load_pdf_from_s3(bucket, key)

        # Chunk documents hierarchically
        logger.info(f"Chunking {len(documents)} documents")
        chunks = chunk_documents(documents)

        # Generate embeddings for each chunk
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        enriched_chunks = generate_embeddings(chunks, turbine_model, document_type)

        # Store in OpenSearch
        logger.info(f"Storing {len(enriched_chunks)} chunks in OpenSearch")
        store_in_opensearch(enriched_chunks)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed {len(enriched_chunks)} chunks',
                'document': key,
                'turbine_model': turbine_model,
                'document_type': document_type
            })
        }

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def load_pdf_from_s3(bucket: str, key: str) -> List[Document]:
    """Load PDF document from S3 and extract text."""
    logger.info(f"Downloading PDF from s3://{bucket}/{key}")
    
    # Download PDF from S3
    response = s3_client.get_object(Bucket=bucket, Key=key)
    pdf_bytes = response['Body'].read()
    
    # Extract text from PDF using pdfplumber
    documents = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        logger.info(f"Extracting text from {len(pdf.pages)} pages")
        
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            
            if text and text.strip():
                # Create LangChain Document with metadata
                doc = Document(
                    page_content=text,
                    metadata={
                        'source': f"s3://{bucket}/{key}",
                        'page_number': page_num,
                        'total_pages': len(pdf.pages),
                    }
                )
                documents.append(doc)
    
    logger.info(f"Extracted {len(documents)} pages with text")
    return documents


def chunk_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Chunk documents hierarchically with overlap for continuity.

    Uses recursive character splitter that respects sentence boundaries.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Split documents into chunks
    chunks = text_splitter.split_documents(documents)
    
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks


def generate_embeddings(chunks: List[Document], turbine_model: str, document_type: str) -> List[Dict[str, Any]]:
    """
    Generate embeddings for each chunk using Bedrock Titan.

    Adds metadata to each chunk for filtering and retrieval.
    """
    enriched_chunks = []
    
    for idx, chunk in enumerate(chunks):
        try:
            # Prepare request body for Titan Embeddings model
            request_body = {
                "inputText": chunk.page_content
            }
            
            # Invoke Bedrock Titan Embeddings model
            response = bedrock_runtime.invoke_model(
                modelId=EMBEDDING_MODEL,
                body=json.dumps(request_body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')
            
            if not embedding:
                logger.warning(f"No embedding returned for chunk {idx}")
                continue
            
            # Create enriched chunk with metadata
            enriched_chunk = {
                'text': chunk.page_content,
                'embedding': embedding,
                'metadata': {
                    **chunk.metadata,
                    'turbine_model': turbine_model,
                    'document_type': document_type,
                    'chunk_index': idx,
                    'processed_at': datetime.utcnow().isoformat(),
                }
            }
            
            enriched_chunks.append(enriched_chunk)
            
            # Log progress every 10 chunks
            if (idx + 1) % 10 == 0:
                logger.info(f"Generated embeddings for {idx + 1}/{len(chunks)} chunks")
        
        except Exception as e:
            logger.error(f"Error generating embedding for chunk {idx}: {str(e)}")
            # Continue processing other chunks
            continue
    
    logger.info(f"Successfully generated {len(enriched_chunks)} embeddings")
    return enriched_chunks


def get_opensearch_client():
    """Initialize OpenSearch client with basic authentication."""
    global opensearch_client
    
    if opensearch_client is not None:
        return opensearch_client
    
    if not OPENSEARCH_ENDPOINT:
        raise ValueError("OPENSEARCH_ENDPOINT environment variable not set")
    
    if not OPENSEARCH_MASTER_USER or not OPENSEARCH_MASTER_PASSWORD:
        raise ValueError("OpenSearch credentials not configured")
    
    # Parse endpoint to get host
    endpoint_parts = OPENSEARCH_ENDPOINT.replace('https://', '').split(':')
    host = endpoint_parts[0]
    port = int(endpoint_parts[1]) if len(endpoint_parts) > 1 else 443
    
    opensearch_client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=(OPENSEARCH_MASTER_USER, OPENSEARCH_MASTER_PASSWORD),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30,
    )
    
    logger.info(f"Initialized OpenSearch client for {OPENSEARCH_ENDPOINT}")
    return opensearch_client


def ensure_index_exists():
    """Ensure OpenSearch index exists with proper k-NN mapping."""
    client = get_opensearch_client()
    
    # Check if index exists
    if client.indices.exists(index=OPENSEARCH_INDEX):
        logger.info(f"Index {OPENSEARCH_INDEX} already exists")
        return
    
    # Create index with k-NN mapping
    index_mapping = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 100
            },
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": "standard"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "text": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 1536,  # Titan Embeddings dimension
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "faiss"
                    }
                },
                "turbine_model": {
                    "type": "keyword"
                },
                "document_type": {
                    "type": "keyword"
                },
                "source": {
                    "type": "text"
                },
                "page_number": {
                    "type": "integer"
                },
                "chunk_index": {
                    "type": "integer"
                },
                "processed_at": {
                    "type": "date"
                }
            }
        }
    }
    
    client.indices.create(index=OPENSEARCH_INDEX, body=index_mapping)
    logger.info(f"Created OpenSearch index: {OPENSEARCH_INDEX}")


def store_in_opensearch(enriched_chunks: List[Dict[str, Any]]) -> None:
    """
    Store enriched chunks in OpenSearch with embeddings and metadata.

    Creates index with k-NN field mapping if it doesn't exist.
    """
    if not enriched_chunks:
        logger.warning("No chunks to store in OpenSearch")
        return
    
    # Ensure index exists with proper mapping
    ensure_index_exists()
    
    client = get_opensearch_client()
    
    # Prepare documents for bulk indexing
    actions = []
    for chunk in enriched_chunks:
        doc = {
            "text": chunk['text'],
            "embedding": chunk['embedding'],
            "turbine_model": chunk['metadata'].get('turbine_model'),
            "document_type": chunk['metadata'].get('document_type'),
            "source": chunk['metadata'].get('source'),
            "page_number": chunk['metadata'].get('page_number'),
            "chunk_index": chunk['metadata'].get('chunk_index'),
            "processed_at": chunk['metadata'].get('processed_at'),
        }
        
        actions.append({
            "_index": OPENSEARCH_INDEX,
            "_id": f"{chunk['metadata'].get('source', 'unknown')}_{chunk['metadata'].get('page_number', 0)}_{chunk['metadata'].get('chunk_index', 0)}",
            "_source": doc
        })
    
    # Bulk index documents
    try:
        success, failed = bulk(client, actions, chunk_size=100, request_timeout=60)
        logger.info(f"Successfully indexed {success} documents, {len(failed)} failed")
        
        if failed:
            logger.warning(f"Failed to index {len(failed)} documents")
            for item in failed[:5]:  # Log first 5 failures
                logger.warning(f"Failed item: {item}")
    
    except Exception as e:
        logger.error(f"Error bulk indexing documents: {str(e)}")
        raise


# Utility functions for testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "s3_bucket": "test-bucket",
        "s3_key": "manuals/test-doc.pdf",
        "turbine_model": "SMT60",
        "document_type": "technical-specs"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))

