#!/usr/bin/env python3
"""
Query OpenSearch Vector Store

This script allows you to query the OpenSearch vector store with natural language questions.
It performs semantic (k-NN) search using Bedrock embeddings.

Usage:
    python scripts/query-opensearch.py "How do I troubleshoot low oil pressure?"

Requirements:
    - OpenSearch domain accessible (from VPC or via VPN)
    - Bedrock model access enabled
    - Environment variables or command-line arguments for connection
"""

import os
import sys
import json
import boto3
import argparse
from typing import Dict, List, Optional, Any
from opensearchpy import OpenSearch, RequestsHttpConnection


def get_bedrock_client(region: str = "us-east-1"):
    """Create Bedrock runtime client."""
    return boto3.client("bedrock-runtime", region_name=region)


def generate_embedding(text: str, model: str = "amazon.titan-embed-text-v1", region: str = "us-east-1") -> List[float]:
    """Generate embedding vector using Bedrock Titan."""
    bedrock = get_bedrock_client(region)
    
    body = json.dumps({"inputText": text})
    
    response = bedrock.invoke_model(
        modelId=model,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    
    response_body = json.loads(response["body"].read())
    return response_body.get("embedding", [])


def get_opensearch_client(endpoint: str, username: str, password: str) -> OpenSearch:
    """Create OpenSearch client."""
    # Remove protocol if present
    endpoint = endpoint.replace("https://", "").replace("http://", "")
    host = endpoint.split(":")[0] if ":" in endpoint else endpoint
    
    return OpenSearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=(username, password),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30,
    )


def search_opensearch(
    client: OpenSearch,
    index: str,
    query: str,
    embedding: List[float],
    top_k: int = 5,
    filters: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Perform hybrid semantic + keyword search."""
    
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
                                "vector": embedding,
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
        "_source": ["text", "source", "page_number", "turbine_model", "document_type", "chunk_index"],
    }
    
    # Add metadata filters
    if filters:
        filter_clauses = []
        for key, value in filters.items():
            filter_clauses.append({"term": {f"{key}.keyword": value}})
        
        if filter_clauses:
            search_query["query"]["bool"]["must"] = filter_clauses
    
    # Execute search
    response = client.search(index=index, body=search_query)
    
    # Format results
    results = []
    for hit in response.get("hits", {}).get("hits", []):
        source = hit["_source"]
        results.append({
            "text": source.get("text", ""),
            "source": source.get("source", "Unknown"),
            "page_number": source.get("page_number"),
            "turbine_model": source.get("turbine_model"),
            "document_type": source.get("document_type"),
            "chunk_index": source.get("chunk_index"),
            "score": hit.get("_score", 0.0),
        })
    
    return results


def print_results(results: List[Dict[str, Any]], query: str):
    """Pretty print search results."""
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"Found {len(results)} results")
    print(f"{'='*80}\n")
    
    for i, result in enumerate(results, 1):
        print(f"Result {i} (Score: {result['score']:.4f})")
        print(f"  Source: {result['source']}")
        if result['page_number']:
            print(f"  Page: {result['page_number']}")
        if result['turbine_model']:
            print(f"  Turbine Model: {result['turbine_model']}")
        if result['document_type']:
            print(f"  Document Type: {result['document_type']}")
        print(f"\n  Content:")
        text = result['text'][:500]  # First 500 chars
        if len(result['text']) > 500:
            text += "..."
        print(f"  {text}")
        print(f"\n{'-'*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Query OpenSearch vector store with natural language questions"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Your question or search query"
    )
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("OPENSEARCH_ENDPOINT"),
        help="OpenSearch endpoint (or set OPENSEARCH_ENDPOINT env var)"
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("OPENSEARCH_MASTER_USER", "admin"),
        help="OpenSearch username (or set OPENSEARCH_MASTER_USER env var)"
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("OPENSEARCH_MASTER_PASSWORD"),
        help="OpenSearch password (or set OPENSEARCH_MASTER_PASSWORD env var)"
    )
    parser.add_argument(
        "--index",
        default=os.environ.get("OPENSEARCH_INDEX", "turbine-documents"),
        help="OpenSearch index name (default: turbine-documents)"
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION", "us-east-1"),
        help="AWS region (default: us-east-1)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    parser.add_argument(
        "--turbine-model",
        help="Filter by turbine model (e.g., SMT60, SMT130, TM2500)"
    )
    parser.add_argument(
        "--document-type",
        help="Filter by document type (e.g., technical-specs, operational)"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode - keep asking questions"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.query and not args.interactive:
        parser.print_help()
        sys.exit(1)
    
    if not args.endpoint:
        print("ERROR: OpenSearch endpoint required. Set OPENSEARCH_ENDPOINT or use --endpoint")
        sys.exit(1)
    
    if not args.password:
        print("ERROR: OpenSearch password required. Set OPENSEARCH_MASTER_PASSWORD or use --password")
        sys.exit(1)
    
    # Create clients
    print("Connecting to OpenSearch...")
    try:
        opensearch_client = get_opensearch_client(args.endpoint, args.username, args.password)
        
        # Test connection
        info = opensearch_client.info()
        print(f"✅ Connected to OpenSearch {info['version']['number']}")
    except Exception as e:
        print(f"❌ Failed to connect to OpenSearch: {e}")
        print("\nTips:")
        print("  - Check if OpenSearch domain is accessible from your network")
        print("  - Verify endpoint URL is correct")
        print("  - If domain is in VPC, you may need VPN or bastion host access")
        sys.exit(1)
    
    # Check if index exists
    if not opensearch_client.indices.exists(index=args.index):
        print(f"❌ Index '{args.index}' does not exist")
        print(f"\nAvailable indices:")
        indices = opensearch_client.indices.get_alias()
        for idx in indices:
            print(f"  - {idx}")
        sys.exit(1)
    
    # Get index stats
    stats = opensearch_client.count(index=args.index)
    doc_count = stats['count']
    print(f"✅ Index '{args.index}' has {doc_count} documents\n")
    
    if doc_count == 0:
        print("⚠️  Warning: Index is empty. You may need to process documents first.")
        print("   See lambda/document-processor/README.md for how to index documents.\n")
    
    # Interactive or single query mode
    while True:
        if not args.query and args.interactive:
            query = input("\nEnter your question (or 'quit' to exit): ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            if not query:
                continue
        elif args.query:
            query = args.query
        else:
            break
        
        print(f"\n🔍 Searching for: '{query}'")
        print("   Generating embedding...")
        
        try:
            # Generate embedding
            embedding = generate_embedding(query, region=args.region)
            print(f"   ✅ Embedding generated ({len(embedding)} dimensions)")
            
            # Build filters
            filters = {}
            if args.turbine_model:
                filters["turbine_model"] = args.turbine_model
            if args.document_type:
                filters["document_type"] = args.document_type
            
            # Search
            print(f"   Searching index '{args.index}'...")
            results = search_opensearch(
                opensearch_client,
                args.index,
                query,
                embedding,
                top_k=args.top_k,
                filters=filters if filters else None,
            )
            
            # Print results
            print_results(results, query)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Exit if not interactive
        if not args.interactive:
            break
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
