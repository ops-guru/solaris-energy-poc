#!/bin/bash
# Test script for RAG flow: Document Processing → OpenSearch → Agent Workflow → LLM

set -e

echo "🧪 Testing RAG Flow for Solaris Energy POC"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
AWS_PROFILE="${AWS_PROFILE:-mavenlink-functions}"
AWS_REGION="${AWS_REGION:-us-east-1}"
DOC_PROCESSOR_FUNCTION="solaris-poc-document-processor"
AGENT_WORKFLOW_FUNCTION="solaris-poc-agent-workflow"

# Get actual bucket name from AWS (or use provided)
if [ -z "${S3_BUCKET}" ]; then
    echo "Detecting S3 bucket name..."
    S3_BUCKET=$(aws s3api list-buckets \
        --profile "${AWS_PROFILE}" \
        --query "Buckets[?contains(Name, 'solaris-poc-documents')].Name" \
        --output text \
        --region "${AWS_REGION}" 2>/dev/null | head -1)
    
    if [ -z "${S3_BUCKET}" ]; then
        # Fallback: try to get from CloudFormation stack outputs
        S3_BUCKET=$(aws cloudformation describe-stacks \
            --stack-name StorageStack \
            --profile "${AWS_PROFILE}" \
            --region "${AWS_REGION}" \
            --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucketName`].OutputValue' \
            --output text 2>/dev/null)
        
        if [ -z "${S3_BUCKET}" ]; then
            echo "⚠️  Could not detect S3 bucket. Using default pattern."
            AWS_ACCOUNT_ID=$(aws sts get-caller-identity \
                --profile "${AWS_PROFILE}" \
                --query Account \
                --output text 2>/dev/null)
            S3_BUCKET="solaris-poc-documents-${AWS_ACCOUNT_ID}-${AWS_REGION}"
        fi
    fi
fi

# Find an actual PDF file in the manuals folder
echo "Finding PDF files in S3 bucket..."
ACTUAL_PDF=$(aws s3 ls "s3://${S3_BUCKET}/manuals/" \
    --profile "${AWS_PROFILE}" \
    --recursive \
    --region "${AWS_REGION}" 2>/dev/null | \
    grep -E "\.pdf$" | \
    awk '{print $4}' | \
    head -1)

if [ -z "${ACTUAL_PDF}" ]; then
    echo "⚠️  No PDF files found in manuals/ folder. Using default test file."
    TEST_DOC_KEY="manuals/Solaris_SMT60_Technical_Specs.pdf"
else
    TEST_DOC_KEY="${ACTUAL_PDF}"
    echo "✅ Found PDF: ${TEST_DOC_KEY}"
fi

# Extract turbine model and document type from filename/path
# Defaults to SMT60 and technical-specs if we can't determine
TURBINE_MODEL="SMT60"
DOCUMENT_TYPE="technical-specs"

if echo "${TEST_DOC_KEY}" | grep -qi "smt60\|taurus60"; then
    TURBINE_MODEL="SMT60"
elif echo "${TEST_DOC_KEY}" | grep -qi "smt130\|titan130"; then
    TURBINE_MODEL="SMT130"
elif echo "${TEST_DOC_KEY}" | grep -qi "tm2500\|lm2500"; then
    TURBINE_MODEL="TM2500"
fi

if echo "${TEST_DOC_KEY}" | grep -qi "operational\|operation\|procedure"; then
    DOCUMENT_TYPE="operational"
elif echo "${TEST_DOC_KEY}" | grep -qi "maintenance"; then
    DOCUMENT_TYPE="maintenance"
elif echo "${TEST_DOC_KEY}" | grep -qi "troubleshoot\|trouble"; then
    DOCUMENT_TYPE="troubleshooting"
elif echo "${TEST_DOC_KEY}" | grep -qi "reference"; then
    DOCUMENT_TYPE="reference"
elif echo "${TEST_DOC_KEY}" | grep -qi "spec\|specification"; then
    DOCUMENT_TYPE="technical-specs"
fi

echo "Configuration:"
echo "  AWS Profile: ${AWS_PROFILE}"
echo "  AWS Region: ${AWS_REGION}"
echo "  Document Processor: ${DOC_PROCESSOR_FUNCTION}"
echo "  Agent Workflow: ${AGENT_WORKFLOW_FUNCTION}"
echo "  S3 Bucket: ${S3_BUCKET}"
echo "  PDF File: ${TEST_DOC_KEY}"
echo ""

# Step 1: Process a test document
echo -e "${YELLOW}Step 1: Processing test document...${NC}"
DOC_PAYLOAD=$(cat <<EOF
{
  "s3_bucket": "${S3_BUCKET}",
  "s3_key": "${TEST_DOC_KEY}",
  "turbine_model": "${TURBINE_MODEL}",
  "document_type": "${DOCUMENT_TYPE}"
}
EOF
)

echo "Invoking document processor..."
echo "  Bucket: ${S3_BUCKET}"
echo "  Key: ${TEST_DOC_KEY}"
echo "  Turbine Model: ${TURBINE_MODEL}"
echo "  Document Type: ${DOCUMENT_TYPE}"
DOC_RESPONSE=$(aws lambda invoke \
  --function-name "${DOC_PROCESSOR_FUNCTION}" \
  --payload "${DOC_PAYLOAD}" \
  --profile "${AWS_PROFILE}" \
  --region "${AWS_REGION}" \
  --cli-binary-format raw-in-base64-out \
  /tmp/doc-processor-response.json)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Document processor invoked successfully${NC}"
    cat /tmp/doc-processor-response.json | jq '.'
    CHUNKS_STORED=$(cat /tmp/doc-processor-response.json | jq -r '.chunks_stored // 0')
    echo "Chunks stored: ${CHUNKS_STORED}"
    
    if [ "${CHUNKS_STORED}" -eq "0" ]; then
        echo -e "${RED}⚠️  Warning: No chunks were stored. Check CloudWatch logs.${NC}"
    fi
else
    echo -e "${RED}❌ Document processor failed${NC}"
    exit 1
fi

echo ""
echo "Waiting 5 seconds for OpenSearch to index..."
sleep 5

# Step 2: Test agent workflow with a query
echo -e "${YELLOW}Step 2: Testing agent workflow with query...${NC}"

TEST_QUERIES=(
    "How do I troubleshoot low oil pressure on SMT60?"
    "What are the operation procedures for SMT60?"
    "What are common issues with SMT60 turbines?"
)

for QUERY in "${TEST_QUERIES[@]}"; do
    echo ""
    echo "Query: ${QUERY}"
    
    AGENT_PAYLOAD=$(cat <<EOF
{
  "session_id": "test-session-$(date +%s)",
  "query": "${QUERY}",
  "messages": []
}
EOF
)
    
    echo "Invoking agent workflow..."
    AGENT_RESPONSE=$(aws lambda invoke \
      --function-name "${AGENT_WORKFLOW_FUNCTION}" \
      --payload "${AGENT_PAYLOAD}" \
      --profile "${AWS_PROFILE}" \
      --region "${AWS_REGION}" \
      --cli-binary-format raw-in-base64-out \
      /tmp/agent-workflow-response.json)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Agent workflow invoked successfully${NC}"
        
        # Parse response
        RESPONSE_BODY=$(cat /tmp/agent-workflow-response.json | jq -r '.body // .')
        if [ "${RESPONSE_BODY}" != "null" ] && [ -n "${RESPONSE_BODY}" ]; then
            # If body is a string, parse it
            if echo "${RESPONSE_BODY}" | jq . > /dev/null 2>&1; then
                echo "${RESPONSE_BODY}" | jq '.'
            else
                echo "${RESPONSE_BODY}"
            fi
        else
            cat /tmp/agent-workflow-response.json | jq '.'
        fi
        
        # Extract key metrics
        CITATIONS_COUNT=$(cat /tmp/agent-workflow-response.json | jq -r '[.body // . | fromjson | .citations // []] | length' 2>/dev/null || echo "0")
        CONFIDENCE=$(cat /tmp/agent-workflow-response.json | jq -r '.body // . | fromjson | .confidence_score // 0' 2>/dev/null || echo "0")
        
        echo ""
        echo "Metrics:"
        echo "  Citations: ${CITATIONS_COUNT}"
        echo "  Confidence: ${CONFIDENCE}"
        
        if [ "${CITATIONS_COUNT}" -gt "0" ]; then
            echo -e "${GREEN}✅ RAG retrieval working - found ${CITATIONS_COUNT} citations${NC}"
        else
            echo -e "${YELLOW}⚠️  No citations found - RAG may not be working${NC}"
        fi
    else
        echo -e "${RED}❌ Agent workflow failed${NC}"
    fi
    
    echo ""
    echo "---"
done

echo ""
echo -e "${GREEN}✅ Test complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Check CloudWatch logs for detailed information:"
echo "     - Document Processor: /aws/lambda/${DOC_PROCESSOR_FUNCTION}"
echo "     - Agent Workflow: /aws/lambda/${AGENT_WORKFLOW_FUNCTION}"
echo "  2. Verify OpenSearch index has documents:"
echo "     aws opensearch describe-domain --domain-name solaris-poc-vector-store --profile ${AWS_PROFILE}"
echo "  3. Test via API Gateway (if deployed):"
echo "     curl -X POST https://<api-id>.execute-api.${AWS_REGION}.amazonaws.com/prod/chat \\"
echo "       -H 'x-api-key: <your-api-key>' \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"query\": \"How do I troubleshoot low oil pressure?\"}'"

