# Querying OpenSearch Vector Store - Guide

This guide shows you different ways to ask questions and query your OpenSearch vector store.

## Quick Start

The easiest way is using the provided Python script:

```bash
python scripts/query-opensearch.py "How do I troubleshoot low oil pressure?"
```

## Methods to Query OpenSearch

### Method 1: Python Script (Recommended)

The `query-opensearch.py` script provides an easy way to query from your terminal.

#### Setup

1. Install dependencies:
```bash
pip install opensearch-py boto3
```

2. Set environment variables (or pass as arguments):
```bash
export OPENSEARCH_ENDPOINT="search-solaris-poc-vector-store-xxxxx.us-east-1.es.amazonaws.com"
export OPENSEARCH_MASTER_USER="admin"
export OPENSEARCH_MASTER_PASSWORD="your-password"
export AWS_REGION="us-east-1"
```

#### Usage

**Single Query**:
```bash
python scripts/query-opensearch.py "What are the maintenance procedures for SMT60?"
```

**Interactive Mode** (keep asking questions):
```bash
python scripts/query-opensearch.py --interactive
```

**With Filters**:
```bash
python scripts/query-opensearch.py "oil pressure specifications" --turbine-model SMT60 --document-type technical-specs
```

**Custom Options**:
```bash
python scripts/query-opensearch.py "troubleshooting guide" \
  --endpoint "search-your-domain.us-east-1.es.amazonaws.com" \
  --username admin \
  --password "your-password" \
  --top-k 10
```

#### Features

- ✅ Semantic search using Bedrock embeddings
- ✅ Hybrid search (semantic + keyword matching)
- ✅ Metadata filtering (turbine model, document type)
- ✅ Pretty-printed results with scores
- ✅ Interactive mode for multiple queries

### Method 2: OpenSearch Dashboards (Web UI)

If you have access to OpenSearch Dashboards, you can query directly in the UI.

#### Access Dashboards

1. Go to AWS Console → OpenSearch Service
2. Click on your domain: `solaris-poc-vector-store`
3. Click "OpenSearch Dashboards URL" or "Dashboard URL"
4. Login with username: `admin` and your password

#### Using Dev Tools

1. In Dashboards, click **"Dev Tools"** in the left sidebar (or **"Console"**)
2. Run queries in the console:

**Basic Text Search**:
```json
GET /turbine-documents/_search
{
  "size": 5,
  "query": {
    "match": {
      "text": "oil pressure troubleshooting"
    }
  }
}
```

**Get All Documents** (to see what's indexed):
```json
GET /turbine-documents/_search
{
  "size": 10,
  "query": {
    "match_all": {}
  }
}
```

**Check Index Stats**:
```json
GET /turbine-documents/_count
```

**Filter by Turbine Model**:
```json
GET /turbine-documents/_search
{
  "size": 5,
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "text": "maintenance procedures"
          }
        },
        {
          "term": {
            "turbine_model.keyword": "SMT60"
          }
        }
      ]
    }
  }
}
```

**Note**: For semantic/k-NN search in Dashboards, you'll need to generate embeddings first and pass them in the query. The Python script handles this automatically.

#### Using Discover

1. Go to **"Discover"** in the left sidebar
2. Select index: `turbine-documents`
3. Use the search bar to query
4. Apply filters using the left sidebar (turbine_model, document_type, etc.)

### Method 3: AWS Lambda Test

You can test queries using the agent workflow Lambda function.

1. Go to AWS Console → Lambda
2. Find function: `solaris-poc-agent-workflow`
3. Create a test event:
```json
{
  "session_id": "test-session-123",
  "query": "How do I troubleshoot low oil pressure on SMT60?",
  "messages": []
}
```
4. Run the test and check the response

### Method 4: Python Code (Direct)

If you want to integrate into your own code:

```python
import boto3
import json
from opensearchpy import OpenSearch

# Generate embedding
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
response = bedrock.invoke_model(
    modelId="amazon.titan-embed-text-v1",
    body=json.dumps({"inputText": "your question here"}),
    contentType="application/json",
)
embedding = json.loads(response["body"].read())["embedding"]

# Connect to OpenSearch
client = OpenSearch(
    hosts=[{"host": "your-endpoint.us-east-1.es.amazonaws.com", "port": 443}],
    http_auth=("admin", "your-password"),
    use_ssl=True,
    verify_certs=True,
)

# Search
query = {
    "size": 5,
    "query": {
        "knn": {
            "embedding": {
                "vector": embedding,
                "k": 5
            }
        }
    }
}

results = client.search(index="turbine-documents", body=query)
print(results)
```

## Example Queries

Try these example questions:

**Troubleshooting**:
- "How do I troubleshoot low oil pressure?"
- "What causes high exhaust temperature?"
- "What should I check if the turbine won't start?"

**Maintenance**:
- "What are the scheduled maintenance intervals?"
- "How do I perform routine maintenance on SMT60?"
- "What maintenance is required at 500 hours?"

**Specifications**:
- "What are the operating specifications for SMT60?"
- "What is the maximum output power?"
- "What are the temperature limits?"

**Safety**:
- "What safety procedures should I follow?"
- "What are the emergency shutdown procedures?"
- "What PPE is required?"

## Understanding Results

Each search result includes:

- **text**: The actual content chunk from the document
- **source**: Path to the source document (S3 path)
- **page_number**: Page number in the original document
- **turbine_model**: Which turbine model this applies to (SMT60, SMT130, etc.)
- **document_type**: Type of document (technical-specs, operational, etc.)
- **score**: Relevance score (higher is better)

## Troubleshooting

### "Index does not exist"

The index `turbine-documents` may not exist yet. You need to process documents first:

1. Upload PDFs to S3
2. Trigger the document processor Lambda
3. Wait for indexing to complete

### "Cannot connect to OpenSearch"

If the domain is in a VPC, you need network access:

1. **Option 1**: Use VPN to connect to the VPC
2. **Option 2**: Use a bastion host or EC2 instance in the VPC
3. **Option 3**: Access via OpenSearch Dashboards (if public access is enabled)
4. **Option 4**: Query via Lambda function (Lambda has VPC access)

### "No results found"

Possible reasons:
- Index is empty (no documents processed yet)
- Query doesn't match any documents
- Try broader or different keywords
- Check if documents exist: `GET /turbine-documents/_count`

### "Bedrock access denied"

Make sure Bedrock model access is enabled:
1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Enable `amazon.titan-embed-text-v1`

## Advanced Usage

### Filtering Results

Filter by specific turbine model:
```bash
python scripts/query-opensearch.py "maintenance procedures" --turbine-model SMT60
```

Filter by document type:
```bash
python scripts/query-opensearch.py "safety procedures" --document-type operational
```

Combine filters:
```bash
python scripts/query-opensearch.py "specifications" \
  --turbine-model TM2500 \
  --document-type technical-specs
```

### Getting More Results

Increase the number of results:
```bash
python scripts/query-opensearch.py "troubleshooting" --top-k 10
```

### Custom Endpoint

If you need to specify a different endpoint:
```bash
python scripts/query-opensearch.py "your question" \
  --endpoint "search-custom-domain.us-east-1.es.amazonaws.com"
```

## Next Steps

Once you can query OpenSearch:

1. ✅ Test various question types
2. ✅ Verify results are relevant
3. ✅ Check if all documents are indexed
4. ✅ Integrate with agent workflow Lambda
5. ✅ Test end-to-end RAG functionality

For more information:
- See `lambda/agent-workflow/opensearch_helper.py` for the search implementation
- See `lambda/document-processor/README.md` for indexing documents
- See `docs/architecture.md` for overall architecture
