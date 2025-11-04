# API Handlers Lambda

API Gateway Lambda integration for chat endpoints.

## Endpoints

### POST /chat
Send a query to the agent workflow.

**Request:**
```json
{
  "query": "How do I troubleshoot low oil pressure on SMT60?",
  "session_id": "session-123"  // Optional
}
```

**Response:**
```json
{
  "session_id": "session-123",
  "response": "Based on the documentation...",
  "citations": [...],
  "confidence_score": 0.85,
  "turbine_model": "SMT60"
}
```

### GET /chat/{session_id}
Retrieve conversation history for a session.

**Response:**
```json
{
  "session_id": "session-123",
  "messages": [...],
  "last_updated": "2025-11-04T12:00:00"
}
```

### DELETE /chat/{session_id}
Delete a session and its history.

**Response:**
```json
{
  "message": "Session deleted"
}
```

## Environment Variables

- `AGENT_WORKFLOW_FUNCTION_NAME` - Name of the agent workflow Lambda
- `SESSIONS_TABLE_NAME` - DynamoDB table for sessions

## Dependencies

- `boto3` - AWS SDK
