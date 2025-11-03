# Document Processor Lambda

Processes PDF documents from S3, extracts text, generates embeddings, and stores vectors in OpenSearch for RAG retrieval.

## Overview

This Lambda function is the first step in building the knowledge base for the operator assistant. It processes turbine documentation PDFs and makes them searchable through semantic search.

## Architecture

```
S3 Document → Lambda → PDF Extraction → Text Chunking → Embeddings → OpenSearch
```

## Function Flow

1. **Load PDF from S3**: Download document using S3 SDK
2. **Extract Text**: Use pdfplumber to extract text from each page
3. **Chunk Documents**: Split text into ~1000 character chunks with 200 char overlap
4. **Generate Embeddings**: Call Bedrock Titan Embeddings for each chunk
5. **Store Vectors**: Bulk insert into OpenSearch with metadata

## Input Event Format

```json
{
  "s3_bucket": "solaris-poc-documents-123456-us-east-1",
  "s3_key": "manuals/SMT60-Taurus60/technical-specs/Solaris_SMT60_Technical_Specs.pdf",
  "turbine_model": "SMT60",
  "document_type": "technical-specs"
}
```

## Output

```json
{
  "statusCode": 200,
  "body": {
    "message": "Successfully processed 45 chunks",
    "document": "manuals/SMT60-Taurus60/technical-specs/Solaris_SMT60_Technical_Specs.pdf",
    "turbine_model": "SMT60",
    "document_type": "technical-specs"
  }
}
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENSEARCH_ENDPOINT` | OpenSearch domain endpoint | - | Yes |
| `OPENSEARCH_INDEX` | Index name | `turbine-documents` | No |
| `AWS_REGION` | AWS region | `us-east-1` | No |
| `EMBEDDING_MODEL` | Bedrock model ID | `amazon.titan-embed-text-v1` | No |
| `OPENSEARCH_MASTER_USER` | OpenSearch username | `admin` | No |
| `OPENSEARCH_MASTER_PASSWORD` | OpenSearch password | - | Yes |

## OpenSearch Index Mapping

The function automatically creates the index with this mapping:

```json
{
  "mappings": {
    "properties": {
      "text": {"type": "text"},
      "embedding": {
        "type": "knn_vector",
        "dimension": 1536,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "faiss"
        }
      },
      "turbine_model": {"type": "keyword"},
      "document_type": {"type": "keyword"},
      "source": {"type": "text"},
      "page_number": {"type": "integer"},
      "chunk_index": {"type": "integer"},
      "processed_at": {"type": "date"}
    }
  }
}
```

## Processing Details

### Chunking Strategy

- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters for context continuity
- **Separators**: Paragraph (`\n\n`), line break (`\n`), sentence (`. `), word, character
- **Benefits**: Maintains sentence boundaries, preserves context across chunks

### Embedding Generation

- **Model**: Bedrock Titan Embeddings (1536 dimensions)
- **Cost**: ~$0.0001 per 1k tokens
- **Average**: ~$0.05 per document
- **Batching**: Sequential with progress logging every 10 chunks

### Metadata Enrichment

Each chunk includes:
- Source S3 path
- Page number
- Chunk index
- Turbine model (SMT60, SMT130, TM2500, etc.)
- Document type (technical-specs, operational, safety, etc.)
- Processing timestamp

## Error Handling

- **PDF Extraction**: Logs skipped pages with no text
- **Embedding Failures**: Continues processing other chunks
- **OpenSearch Errors**: Logs failed items, returns partial success
- **Critical Errors**: Returns 500 with error message

## Performance

### Expected Processing Times

| Document Size | Pages | Chunks | Time | Cost (Bedrock) |
|---------------|-------|--------|------|----------------|
| Small (1-5 MB) | 10-50 | 20-100 | ~2-5 min | ~$0.01-0.02 |
| Medium (5-15 MB) | 50-150 | 100-300 | ~5-15 min | ~$0.02-0.06 |
| Large (15+ MB) | 150+ | 300+ | 15+ min | ~$0.06+ |

### Lambda Configuration

**Recommended Settings**:
- Memory: 512-1024 MB
- Timeout: 15 minutes (900 seconds)
- Architecture: x86_64
- Runtime: Python 3.12

## Local Testing

```bash
# Install dependencies
cd lambda/document-processor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export OPENSEARCH_ENDPOINT="https://search-domain.us-east-1.es.amazonaws.com"
export OPENSEARCH_MASTER_USER="admin"
export OPENSEARCH_MASTER_PASSWORD="your-password"
export AWS_REGION="us-east-1"

# Test with sample event
python3 -c "
import handler
event = {
    's3_bucket': 'your-bucket',
    's3_key': 'manuals/test.pdf',
    'turbine_model': 'SMT60',
    'document_type': 'technical-specs'
}
result = handler.lambda_handler(event, None)
print(result)
"
```

## Deployment

Package and deploy via CDK as part of ComputeStack:

```bash
# From infrastructure directory
cdk deploy ComputeStack
```

Or use GitHub Actions workflow (automatic on main branch push).

## Dependencies

See `requirements.txt` for full list:
- `boto3` - AWS SDK
- `opensearch-py` - OpenSearch client
- `langchain-text-splitters` - Text chunking
- `pdfplumber` - PDF extraction
- `pydantic` - Data validation

## Troubleshooting

### Common Issues

1. **"OPENSEARCH_ENDPOINT not set"**
   - Add to Lambda environment variables

2. **"No embedding returned"**
   - Check Bedrock model access permissions
   - Verify `EMBEDDING_MODEL` is correct

3. **"Failed to index documents"**
   - Check OpenSearch credentials
   - Verify network connectivity from Lambda to OpenSearch
   - Check security group rules

4. **"Lambda timeout"**
   - Increase timeout to 15 minutes
   - Process large documents in batches

## Next Steps

After successful processing:
1. Verify documents in OpenSearch (check index stats)
2. Test retrieval with sample queries
3. Build agent workflow Lambda to query documents
4. Implement LangGraph RAG retrieval node

