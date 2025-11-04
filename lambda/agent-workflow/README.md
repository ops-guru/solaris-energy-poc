# Agent Workflow Lambda

Multi-step reasoning workflow using LangGraph to process operator queries and provide troubleshooting assistance.

## Overview

This Lambda function orchestrates a 5-node LangGraph workflow:

1. **QueryTransformer** - Enhances and transforms user queries, detects turbine models
2. **KnowledgeRetriever** - Performs RAG search on OpenSearch to find relevant documentation
3. **ReasoningEngine** - Invokes Bedrock LLM (Claude/Nova) to generate responses
4. **ResponseValidator** - Validates, formats, and adds citations to responses
5. **DataFetcher** - Placeholder for future Timestream integration

## Architecture

```
User Query
    ↓
QueryTransformer → Detect turbine model, enhance query
    ↓
KnowledgeRetriever → RAG search on OpenSearch
    ↓
ReasoningEngine → Generate LLM response with context
    ↓
ResponseValidator → Format and validate response
    ↓
DataFetcher → (Stubbed) Future Timestream integration
    ↓
Response with Citations
```

## Environment Variables

- `OPENSEARCH_ENDPOINT` - OpenSearch domain endpoint
- `OPENSEARCH_INDEX` - Index name (default: `turbine-documents`)
- `OPENSEARCH_MASTER_USER` - Master username
- `OPENSEARCH_MASTER_PASSWORD` - Master password
- `AWS_REGION` - AWS region (default: `us-east-1`)
- `LLM_MODEL` - Bedrock model ID (default: Claude 3.5 Sonnet)
- `EMBEDDING_MODEL` - Bedrock embedding model (default: Titan)

## Input Format

```json
{
  "session_id": "session-123",
  "query": "How do I troubleshoot low oil pressure on SMT60?",
  "messages": [
    {"role": "user", "content": "Previous question..."},
    {"role": "assistant", "content": "Previous answer..."}
  ]
}
```

## Output Format

```json
{
  "statusCode": 200,
  "body": {
    "session_id": "session-123",
    "response": "Formatted response with citations...",
    "citations": [
      {"source": "SMT60_Manual.pdf", "page": 45, "relevance_score": 0.92}
    ],
    "confidence_score": 0.85,
    "turbine_model": "SMT60",
    "messages": [...],
    "error": null
  }
}
```

## Dependencies

- `langgraph` - Workflow orchestration
- `langchain-core` - Core LangChain components
- `langchain-aws` - AWS Bedrock integration
- `opensearch-py` - OpenSearch client
- `boto3` - AWS SDK
- `pydantic` - Data validation

## Files

- `handler.py` - Main Lambda handler and LangGraph workflow definition
- `opensearch_helper.py` - OpenSearch client and search utilities
- `llm_clients.py` - Bedrock LLM invocation utilities

## Testing

Test locally with a mock event:

```python
event = {
    "session_id": "test-session",
    "query": "How do I start the SMT60 turbine?",
    "messages": []
}

# Invoke handler
from handler import lambda_handler
response = lambda_handler(event, None)
print(response)
```

## Next Steps

- [ ] Add Bedrock Guardrails integration for content filtering
- [ ] Implement Timestream data fetching
- [ ] Add multi-LLM evaluation framework
- [ ] Implement response caching
- [ ] Add metrics and monitoring
