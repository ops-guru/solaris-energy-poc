# Testing the RAG Flow

**Purpose**: Guide for testing the end-to-end RAG (Retrieval-Augmented Generation) flow to verify conversations, LLM, and semantic search work correctly.

**Last Updated**: 2025-11-05

---

## Overview

The RAG flow consists of:
1. **Document Processing**: Upload documents → Extract text → Generate embeddings → Store in OpenSearch
2. **Query Processing**: User query → Generate query embedding → Search OpenSearch → Retrieve relevant docs
3. **LLM Response**: Context + Query → Bedrock Nova Pro → Generate answer with citations

---

## Prerequisites

1. **Infrastructure Deployed**:
   - OpenSearch domain created and accessible
   - Lambda functions deployed (document-processor, agent-workflow)
   - IAM roles configured for OpenSearch access
   - OpenSearch master user set to IAM ARN (not password)

2. **AWS CLI Configured**:
   ```bash
   export AWS_PROFILE=mavenlink-functions
   export AWS_REGION=us-east-1
   ```

3. **Dependencies**:
   - `jq` installed (for JSON parsing)
   - AWS CLI v2

---

## Quick Test Script

Use the provided test script:

```bash
cd scripts
./test-rag-flow.sh
```

This script will:
1. Invoke the document processor to create test chunks
2. Wait for OpenSearch indexing
3. Test the agent workflow with sample queries
4. Display results and metrics

---

## Manual Testing Steps

### Step 1: Process a Test Document

**Purpose**: Populate OpenSearch with test data

```bash
# Create test payload
cat > /tmp/test-doc-payload.json <<EOF
{
  "s3_bucket": "solaris-poc-documents-<account-id>",
  "s3_key": "test/turbine-manual-test.pdf",
  "turbine_model": "SMT60",
  "document_type": "manual"
}
EOF

# Invoke document processor
aws lambda invoke \
  --function-name solaris-poc-document-processor \
  --payload file:///tmp/test-doc-payload.json \
  --profile mavenlink-functions \
  --region us-east-1 \
  --cli-binary-format raw-in-base64-out \
  /tmp/doc-response.json

# Check response
cat /tmp/doc-response.json | jq '.'
```

**Expected Response**:
```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Successfully processed 3 chunks\", \"chunks_stored\": 3}"
}
```

**Verify**:
- `chunks_stored` > 0
- Check CloudWatch logs: `/aws/lambda/solaris-poc-document-processor`

### Step 2: Test Agent Workflow Query

**Purpose**: Verify RAG retrieval and LLM response

```bash
# Create test query payload
cat > /tmp/test-query-payload.json <<EOF
{
  "session_id": "test-session-001",
  "query": "How do I troubleshoot low oil pressure on SMT60?",
  "messages": []
}
EOF

# Invoke agent workflow
aws lambda invoke \
  --function-name solaris-poc-agent-workflow \
  --payload file:///tmp/test-query-payload.json \
  --profile mavenlink-functions \
  --region us-east-1 \
  --cli-binary-format raw-in-base64-out \
  /tmp/agent-response.json

# Parse response
RESPONSE_BODY=$(cat /tmp/agent-response.json | jq -r '.body')
echo "${RESPONSE_BODY}" | jq '.'
```

**Expected Response**:
```json
{
  "session_id": "test-session-001",
  "response": "Based on the documentation...",
  "citations": [
    {
      "source": "test/turbine-manual-test.pdf",
      "excerpt": "Troubleshooting guide for SMT60...",
      "relevance_score": 0.85
    }
  ],
  "confidence_score": 0.82,
  "turbine_model": "SMT60",
  "messages": [...]
}
```

**Verify**:
- `citations` array has at least one item
- `confidence_score` > 0.6
- `response` contains relevant answer
- `turbine_model` is detected correctly

### Step 3: Test via API Gateway

**Purpose**: Test the complete frontend → API → Lambda flow

```bash
# Get API Gateway URL and API key
API_URL=$(aws apigateway get-rest-apis \
  --profile mavenlink-functions \
  --query 'items[?name==`solaris-poc-api`].id' \
  --output text)

API_KEY=$(aws apigateway get-api-keys \
  --profile mavenlink-functions \
  --include-values \
  --query 'items[?name==`solaris-poc-api-key`].value' \
  --output text)

# Test query
curl -X POST "https://${API_URL}.execute-api.us-east-1.amazonaws.com/prod/chat" \
  -H "x-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-002",
    "query": "What are the operation procedures for SMT60?",
    "messages": []
  }' | jq '.'
```

---

## Test Queries

Use these test queries to verify different aspects:

### 1. Troubleshooting Query
```json
{
  "query": "How do I troubleshoot low oil pressure on SMT60?",
  "expected": "Should retrieve troubleshooting documentation"
}
```

### 2. Procedure Query
```json
{
  "query": "What are the startup procedures for SMT60?",
  "expected": "Should retrieve operational procedures"
}
```

### 3. General Query
```json
{
  "query": "Tell me about SMT60 turbine specifications",
  "expected": "Should retrieve technical specifications"
}
```

### 4. Model-Specific Query
```json
{
  "query": "What are common issues with SMT130 turbines?",
  "expected": "Should filter by turbine_model: SMT130"
}
```

---

## Troubleshooting

### Issue: No Citations Returned

**Symptoms**:
- `citations` array is empty
- `confidence_score` is low (< 0.6)

**Possible Causes**:
1. **OpenSearch index is empty**
   - Check: CloudWatch logs for document processor
   - Fix: Process a document first

2. **OpenSearch authentication failed**
   - Check: CloudWatch logs for 403 Forbidden errors
   - Fix: Verify IAM role has OpenSearch permissions, master user is IAM ARN

3. **Index doesn't exist**
   - Check: CloudWatch logs for index creation errors
   - Fix: Document processor should create index automatically

4. **Embedding generation failed**
   - Check: CloudWatch logs for Bedrock errors
   - Fix: Verify Bedrock permissions and model availability

**Debug Steps**:
```bash
# Check document processor logs
aws logs tail /aws/lambda/solaris-poc-document-processor \
  --profile mavenlink-functions \
  --follow

# Check agent workflow logs
aws logs tail /aws/lambda/solaris-poc-agent-workflow \
  --profile mavenlink-functions \
  --follow
```

### Issue: LLM Returns Generic Response

**Symptoms**:
- Response doesn't reference the documentation
- Response says "I don't have that information"

**Possible Causes**:
1. **No context retrieved**
   - Check: `citations` array in response
   - Fix: Ensure documents are in OpenSearch

2. **Context not passed to LLM**
   - Check: CloudWatch logs for LLM invocation
   - Fix: Verify `invoke_bedrock_llm` receives context

3. **LLM model not available**
   - Check: CloudWatch logs for model errors
   - Fix: Verify Nova Pro access in Bedrock

**Debug Steps**:
```bash
# Check if context is being built
aws logs filter-log-events \
  --log-group-name /aws/lambda/solaris-poc-agent-workflow \
  --filter-pattern "Retrieved" \
  --profile mavenlink-functions
```

### Issue: OpenSearch Connection Failed

**Symptoms**:
- 403 Forbidden errors
- Connection timeout errors

**Possible Causes**:
1. **IAM authentication not configured**
   - Check: OpenSearch master user is IAM ARN
   - Fix: Update OpenSearch domain security configuration

2. **Lambda role missing permissions**
   - Check: IAM role has `es:*` permissions
   - Fix: Update Lambda execution role

3. **VPC configuration**
   - Check: Lambda is in correct VPC/subnet
   - Fix: Verify VPC endpoints or NAT gateway

**Debug Steps**:
```bash
# Check OpenSearch domain status
aws opensearch describe-domain \
  --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --query 'DomainStatus.Processing' \
  --output text

# Check Lambda VPC configuration
aws lambda get-function-configuration \
  --function-name solaris-poc-agent-workflow \
  --profile mavenlink-functions \
  --query 'VpcConfig' \
  --output json
```

---

## Success Criteria

✅ **Document Processing**:
- Documents are processed successfully
- Embeddings are generated
- Documents are stored in OpenSearch
- Index is created automatically

✅ **RAG Retrieval**:
- Queries return relevant documents
- Citations include source and excerpt
- Relevance scores are reasonable (> 0.5)

✅ **LLM Response**:
- Responses reference the documentation
- Answers are relevant to the query
- Confidence scores are reasonable (> 0.6)

✅ **End-to-End Flow**:
- Frontend → API Gateway → Lambda works
- Session management works
- Multiple queries in same session work

---

## Next Steps

Once the RAG flow is working:

1. **Process Real Documents**: Upload actual turbine manuals
2. **Improve Chunking**: Implement better text extraction and chunking
3. **Enhance Search**: Tune hybrid search (semantic + keyword)
4. **Add Monitoring**: Set up CloudWatch dashboards
5. **Optimize Performance**: Cache embeddings, optimize queries

---

## References

- [OpenSearch Documentation](https://opensearch.org/docs/)
- [Bedrock Nova Pro Documentation](https://docs.aws.amazon.com/bedrock/)
- [Lambda Debugging Guide](https://docs.aws.amazon.com/lambda/latest/dg/troubleshooting.html)

