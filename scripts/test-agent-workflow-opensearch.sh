#!/bin/bash
# Test Agent Workflow Lambda's OpenSearch access

set -e

AWS_PROFILE="${AWS_PROFILE:-mavenlink-functions}"
AWS_REGION="${AWS_REGION:-us-east-1}"
FUNCTION_NAME="${FUNCTION_NAME:-solaris-poc-agent-workflow}"

echo "🧪 Testing Agent Workflow OpenSearch Access"
echo "==========================================="
echo ""

# Test query
QUERY="What is the maximum power output of the SMT60 turbine?"
SESSION_ID="test-$(date +%s)"

echo "📤 Invoking Lambda with query: '$QUERY'"
echo ""

# Invoke Lambda
aws lambda invoke \
  --function-name "${FUNCTION_NAME}" \
  --payload "{\"query\":\"${QUERY}\",\"session_id\":\"${SESSION_ID}\"}" \
  --cli-binary-format raw-in-base64-out \
  --profile "${AWS_PROFILE}" \
  --region "${AWS_REGION}" \
  /tmp/agent-workflow-test.json

echo ""
echo "📥 Lambda Response:"
cat /tmp/agent-workflow-test.json | jq '.'

echo ""
echo "📋 Response Summary:"
RESPONSE=$(cat /tmp/agent-workflow-test.json)

# Check for errors
if echo "$RESPONSE" | jq -e '.body.error' > /dev/null 2>&1; then
    echo "❌ Error in response:"
    echo "$RESPONSE" | jq '.body.error'
fi

# Check citations
CITATIONS=$(echo "$RESPONSE" | jq -r '.body | fromjson | .citations | length // 0')
if [ "$CITATIONS" -gt 0 ]; then
    echo "✅ Retrieved $CITATIONS citations from OpenSearch"
    echo "$RESPONSE" | jq '.body | fromjson | .citations[] | {source: .source, score: .relevance_score}'
else
    echo "⚠️  No citations retrieved (may indicate OpenSearch access issue)"
fi

# Check confidence score
CONFIDENCE=$(echo "$RESPONSE" | jq -r '.body | fromjson | .confidence_score // 0')
echo ""
echo "📊 Confidence Score: $CONFIDENCE"

echo ""
echo "🔍 Checking CloudWatch Logs..."
echo ""

# Check recent logs for OpenSearch errors
aws logs tail "/aws/lambda/${FUNCTION_NAME}" \
  --since 3m \
  --profile "${AWS_PROFILE}" \
  --region "${AWS_REGION}" \
  --format short \
  | grep -iE "403|401|Retrieved|OpenSearch|error|AuthorizationException" \
  | tail -10

echo ""
echo "✅ Test complete!"
echo ""
echo "If you see 403 errors, configure OpenSearch role mappings:"
echo "  See: docs/opensearch-role-mapping-setup.md"
echo ""
echo "Agent Workflow Role ARN:"
echo "  arn:aws:iam::720119760662:role/ComputeStack-AgentWorkflowRole7F667481-1MYYKva7Ya6a"

