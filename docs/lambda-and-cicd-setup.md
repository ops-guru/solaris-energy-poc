# Lambda Functions and CI/CD Setup

**Date**: 2025-10-31  
**Status**: Initial Lambda functions scaffolded, GitHub Actions workflows created

## Lambda Functions Structure

### ✅ Document Processor

**Location**: `lambda/document-processor/`

**Purpose**: Process PDF documents from S3, extract text, generate embeddings, store in OpenSearch

**Key Components**:
- PDF loading from S3
- Hierarchical text chunking with overlap
- Bedrock Titan embeddings generation
- OpenSearch vector storage

**Dependencies** (`requirements.txt`):
```
boto3>=1.34.0
opensearch-py>=2.6.0
langchain>=0.3.0
langchain-community>=0.3.0
pdfplumber>=0.10.0
PyPDF2>=3.0.0
pydantic>=2.0.0
```

**TODO**:
- Implement `load_pdf_from_s3()` with proper PDF extraction
- Complete `generate_embeddings()` with Bedrock invocation
- Complete `store_in_opensearch()` with index mapping and bulk insert
- Add OpenSearch client initialization with AWS auth
- Implement hierarchical chunking preserving document structure

**Expected Event Format**:
```json
{
  "s3_bucket": "solaris-poc-documents-123456-us-east-1",
  "s3_key": "manuals/SMT60-Taurus60/technical-specs/Solaris_SMT60_Technical_Specs.pdf",
  "turbine_model": "SMT60",
  "document_type": "technical-specs"
}
```

## GitHub Actions Workflows

### ✅ Main Deployment Pipeline

**File**: `.github/workflows/deploy.yml`

**Triggers**:
- Push to `main` branch
- Manual workflow dispatch

**Jobs**:

#### 1. deploy-infrastructure
- Checkout code
- Setup Python 3.12
- Configure AWS credentials via OIDC
- Install CDK dependencies
- Run `cdk synth`
- Run `cdk diff`
- Run `cdk deploy --all` (main branch only)

#### 2. deploy-lambda
- Package Lambda functions
- Deploy to AWS
- **Status**: Placeholder, pending Lambda stack implementation

**Required Secrets**:
- `AWS_ROLE_ARN`: IAM role for GitHub Actions

### ✅ PR Validation Pipeline

**File**: `.github/workflows/pr-validation.yml`

**Triggers**: All pull requests to `main`

**Jobs**:

#### 1. lint-infrastructure
- Python linting with `ruff`
- Code formatting check with `black`
- CDK synthesis validation

#### 2. validate-documentation
- Checks for required documentation files
- Ensures consistency

## IAM Setup Required

### GitHub OIDC Provider

First time setup in AWS account:

```bash
# Create OIDC provider for GitHub
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### IAM Role for GitHub Actions

Create role with trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR-ORG/solaris-energy-poc:*"
        }
      }
    }
  ]
}
```

Attach permissions policy with least-privilege:
- CloudFormation access
- CDK bootstrap permissions
- Ability to create/update/delete stacks
- Lambda deployment permissions
- S3 bucket access for Lambda code

## Next Steps

### Immediate
1. ✅ Lambda handler scaffold created
2. ✅ GitHub Actions workflows created
3. ⏳ Implement document processor PDF extraction
4. ⏳ Implement Bedrock embedding generation
5. ⏳ Implement OpenSearch indexing

### Short Term
1. Complete document processor implementation
2. Create agent workflow Lambda function
3. Create API handler Lambda functions
4. Implement ComputeStack in CDK
5. Test end-to-end document processing

### Medium Term
1. Add LangGraph implementation for agent workflow
2. Integrate with AgentCore
3. Add frontend deployment to pipeline
4. Set up monitoring and alerts

## Testing Strategy

### Local Testing

```bash
# Test document processor
cd lambda/document-processor
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python handler.py
```

### Integration Testing

```bash
# Deploy to AWS via GitHub Actions
gh workflow run deploy.yml

# Or deploy via CDK
cd infrastructure
cdk deploy ComputeStack
```

## Implementation Notes

### PDF Processing Challenges

1. **Multi-column layouts**: May need layout analysis
2. **Tables and diagrams**: Consider preserving visual structure
3. **Headers/footers**: Strip or label appropriately
4. **Multi-page continuity**: Overlap helps maintain context

### Chunking Strategy

Recommended parameters:
- Chunk size: 1000 characters
- Overlap: 200 characters  
- Separators: Paragraph, sentence, word boundaries
- Metadata: Page number, section, turbine model, doc type

### Embedding Considerations

- Bedrock Titan `amazon.titan-embed-text-v1`: 1536 dimensions
- Batch processing for efficiency
- Handle failures gracefully with retries
- Store original text alongside embeddings

### OpenSearch Index Mapping

```json
{
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 1536,
        "method": {
          "engine": "faiss",
          "space_type": "cosinesimil",
          "name": "hnsw"
        }
      },
      "text": {"type": "text"},
      "turbine_model": {"type": "keyword"},
      "document_type": {"type": "keyword"},
      "page_number": {"type": "integer"},
      "metadata": {"type": "object"}
    }
  }
}
```

## Cost Estimates

### Lambda Execution

- Document processing: ~60s per document
- Memory: 512 MB
- Concurrency: 1 (sequential processing)
- 100 documents/month: ~$0.17

### Bedrock Embeddings

- Titan Embeddings: $0.0001 per 1k tokens
- Average document: 50k tokens
- 100 documents: ~$0.50

### OpenSearch Storage

- 100 documents × 20 chunks × 8KB avg = ~16 MB
- Well within included storage

**Total**: < $1/month for document processing

## Security Considerations

✅ **Implemented**:
- Least-privilege IAM roles
- OIDC authentication (no stored credentials)
- Encryption at rest and in transit

⚠️ **TODO**:
- Add VPC configuration for Lambda
- Implement secrets management for OpenSearch password
- Add input validation and sanitization
- Enable CloudTrail logging

---

**Status**: Lambda scaffold ready, CI/CD pipelines configured, implementation in progress

