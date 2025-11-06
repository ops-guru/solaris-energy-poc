# Lambda RAG Setup Status

**Purpose**: Current status of Lambda-based RAG implementation for proving conversations, LLM, and semantic search work.

**Date**: 2025-11-05  
**Status**: 🟡 Ready for Testing

---

## Overview

We're focusing on getting the Lambda-based setup working first to prove:
1. ✅ Conversations work (session management)
2. ⏳ LLM/Semantic search works (RAG retrieval)
3. ⏳ Relevant answers are returned to chat queries

Once proven, we'll migrate to AgentCore-based infrastructure.

---

## What We've Fixed

### ✅ Document Processor (`lambda/document-processor/handler.py`)

**Changes**:
- ✅ Updated to use IAM authentication (no passwords)
- ✅ Improved error handling and logging
- ✅ Fixed document structure for OpenSearch indexing
- ✅ Added proper metadata handling
- ✅ Enhanced index creation logic

**Key Features**:
- Creates OpenSearch index automatically if it doesn't exist
- Generates embeddings using Bedrock Titan
- Stores documents with proper structure (text, embedding, metadata)
- Uses IAM authentication via AWS4Auth

### ✅ Agent Workflow (`lambda/agent-workflow/handler.py`)

**Status**: Already using IAM authentication

**Key Features**:
- RAG retrieval from OpenSearch
- Hybrid search (semantic k-NN + keyword BM25)
- LLM response generation with Nova Pro
- Citation generation
- Confidence scoring

### ✅ OpenSearch Helper (`lambda/agent-workflow/opensearch_helper.py`)

**Changes**:
- ✅ Fixed filter query to use direct fields (turbine_model, document_type)
- ✅ Improved error handling

**Key Features**:
- IAM authentication
- Semantic search with embeddings
- Keyword search with fuzzy matching
- Metadata filtering

---

## Current Architecture

```
User Query
    ↓
API Gateway (REST API)
    ↓
Agent Workflow Lambda
    ↓
┌─────────────────────────┐
│ 1. Generate Query Embedding (Bedrock Titan) │
│ 2. Search OpenSearch (k-NN + BM25)          │
│ 3. Retrieve Top-K Documents                 │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 4. Build Context from Docs                  │
│ 5. Invoke Bedrock Nova Pro                  │
│ 6. Generate Response with Citations         │
└─────────────────────────┘
    ↓
Response to User
```

---

## Testing Checklist

### Prerequisites
- [ ] OpenSearch domain deployed and accessible
- [ ] OpenSearch master user configured to use IAM ARN (not password)
- [ ] Lambda functions deployed with latest code
- [ ] IAM roles have OpenSearch permissions
- [ ] Bedrock access to Nova Pro and Titan Embeddings

### Step 1: Process Test Document
- [ ] Invoke document processor with test payload
- [ ] Verify chunks are created (check CloudWatch logs)
- [ ] Verify embeddings are generated
- [ ] Verify documents are stored in OpenSearch
- [ ] Verify index is created (if it didn't exist)

**Test Command**:
```bash
aws lambda invoke \
  --function-name solaris-poc-document-processor \
  --payload '{"s3_bucket":"solaris-poc-documents-<account>","s3_key":"test/doc.pdf","turbine_model":"SMT60","document_type":"manual"}' \
  --profile mavenlink-functions \
  --cli-binary-format raw-in-base64-out \
  /tmp/response.json
```

### Step 2: Test RAG Retrieval
- [ ] Invoke agent workflow with test query
- [ ] Verify OpenSearch search returns documents
- [ ] Verify citations are generated
- [ ] Verify confidence score is reasonable (> 0.6)

**Test Command**:
```bash
aws lambda invoke \
  --function-name solaris-poc-agent-workflow \
  --payload '{"session_id":"test-001","query":"How do I troubleshoot low oil pressure?","messages":[]}' \
  --profile mavenlink-functions \
  --cli-binary-format raw-in-base64-out \
  /tmp/response.json
```

### Step 3: Test LLM Response
- [ ] Verify LLM receives context from retrieved documents
- [ ] Verify response references the documentation
- [ ] Verify response is relevant to the query
- [ ] Verify citations are included in response

### Step 4: Test End-to-End
- [ ] Test via API Gateway (if deployed)
- [ ] Test from frontend (if running)
- [ ] Verify session management works
- [ ] Test multiple queries in same session

---

## Known Issues & Fixes

### Issue: OpenSearch Authentication
**Status**: ✅ Fixed
**Solution**: Migrated to IAM authentication, removed password-based auth

### Issue: Filter Query Not Working
**Status**: ✅ Fixed
**Solution**: Updated filter to use direct fields (turbine_model, document_type) instead of metadata.path

### Issue: Index Creation
**Status**: ✅ Fixed
**Solution**: Added automatic index creation in document processor

---

## Next Steps

1. **Deploy Latest Code**:
   ```bash
   cd infrastructure
   cdk deploy ComputeStack
   ```

2. **Process Test Document**:
   - Use the test script: `scripts/test-rag-flow.sh`
   - Or manually invoke document processor

3. **Test RAG Flow**:
   - Use test queries to verify retrieval
   - Check CloudWatch logs for any errors
   - Verify citations and confidence scores

4. **Verify LLM Responses**:
   - Test with various queries
   - Verify responses reference documentation
   - Check that answers are relevant

5. **Once Working**:
   - Process real turbine manuals
   - Improve chunking strategy
   - Tune search parameters
   - Add monitoring and metrics

---

## Files Modified

### Lambda Functions
- `lambda/document-processor/handler.py` - IAM auth, improved indexing
- `lambda/agent-workflow/opensearch_helper.py` - Fixed filter queries

### Documentation
- `docs/testing-rag-flow.md` - Testing guide
- `docs/lambda-rag-setup-status.md` - This document

### Scripts
- `scripts/test-rag-flow.sh` - Automated test script

---

## CloudWatch Logs to Monitor

**Document Processor**:
- Log Group: `/aws/lambda/solaris-poc-document-processor`
- Key Logs: "Stored chunk", "Refreshed index", "Failed to store"

**Agent Workflow**:
- Log Group: `/aws/lambda/solaris-poc-agent-workflow`
- Key Logs: "Retrieved X docs", "Search returned", "Bedrock LLM error"

---

## Success Criteria

✅ **Document Processing**:
- Documents processed successfully
- Embeddings generated
- Documents stored in OpenSearch
- Index created automatically

✅ **RAG Retrieval**:
- Queries return relevant documents
- Citations include source and excerpt
- Relevance scores reasonable (> 0.5)

✅ **LLM Response**:
- Responses reference documentation
- Answers relevant to query
- Confidence scores reasonable (> 0.6)

✅ **End-to-End**:
- Frontend → API → Lambda works
- Session management works
- Multiple queries work

---

## Migration to AgentCore

Once the Lambda-based setup is proven to work, we'll migrate to AgentCore:

1. **Replace Lambda with AgentCore**:
   - Use Bedrock AgentCore for orchestration
   - Replace LangGraph workflow with AgentCore actions
   - Use AgentCore memory instead of DynamoDB sessions

2. **Keep RAG Components**:
   - OpenSearch vector store (unchanged)
   - Document processor (may need adjustments)
   - Embedding generation (unchanged)

3. **Benefits**:
   - Better session memory management
   - Built-in tool execution
   - Improved conversation flow
   - AWS-managed orchestration

---

**Status**: Ready for testing. Use `scripts/test-rag-flow.sh` to verify the complete flow.

