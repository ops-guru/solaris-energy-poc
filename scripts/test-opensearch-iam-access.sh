#!/bin/bash
# Test script to verify OpenSearch IAM authentication is working

set -e

AWS_PROFILE="${AWS_PROFILE:-mavenlink-functions}"
AWS_REGION="${AWS_REGION:-us-east-1}"
OPENSEARCH_DOMAIN="solaris-poc-vector-store"

echo "🔍 Testing OpenSearch IAM Access"
echo "================================"
echo ""

# Get OpenSearch endpoint (try multiple methods)
echo "Getting OpenSearch endpoint..."

# Method 1: Get from CloudFormation stack outputs (most reliable for VPC domains)
ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name VectorStoreStack \
    --profile "${AWS_PROFILE}" \
    --region "${AWS_REGION}" \
    --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchEndpoint`].OutputValue' \
    --output text 2>/dev/null)

# Method 2: Try regular endpoint
if [ -z "${ENDPOINT}" ] || [ "${ENDPOINT}" = "None" ] || [ "${ENDPOINT}" = "null" ]; then
    ENDPOINT=$(aws opensearch describe-domain \
        --domain-name "${OPENSEARCH_DOMAIN}" \
        --profile "${AWS_PROFILE}" \
        --region "${AWS_REGION}" \
        --query 'DomainStatus.Endpoint' \
        --output text 2>/dev/null)
fi

# Method 3: Try VPC endpoint (for VPC domains)
if [ -z "${ENDPOINT}" ] || [ "${ENDPOINT}" = "None" ] || [ "${ENDPOINT}" = "null" ]; then
    ENDPOINT_V2=$(aws opensearch describe-domain \
        --domain-name "${OPENSEARCH_DOMAIN}" \
        --profile "${AWS_PROFILE}" \
        --region "${AWS_REGION}" \
        --query 'DomainStatus.EndpointV2' \
        --output json 2>/dev/null)
    
    if [ -n "${ENDPOINT_V2}" ] && [ "${ENDPOINT_V2}" != "null" ]; then
        # VPC domain - extract VPC endpoint (try different JSON structures)
        ENDPOINT=$(echo "${ENDPOINT_V2}" | jq -r '.VPC_ENDPOINTS[0].ENDPOINT // .vpc_endpoints[0].endpoint // to_entries[0].value // empty' 2>/dev/null)
    fi
fi

if [ -z "${ENDPOINT}" ] || [ "${ENDPOINT}" = "None" ] || [ "${ENDPOINT}" = "null" ]; then
    echo "⚠️  Could not get OpenSearch endpoint"
    echo ""
    echo "The domain is in a VPC. You can find the endpoint in AWS Console:"
    echo "  1. Go to OpenSearch Service"
    echo "  2. Click domain: ${OPENSEARCH_DOMAIN}"
    echo "  3. Look for 'VPC endpoint' or check CloudFormation stack outputs"
    echo ""
    echo "Or manually set it:"
    echo "  export OPENSEARCH_ENDPOINT='vpc-solaris-poc-vector-store-xxxxx.us-east-1.es.amazonaws.com'"
    echo ""
    exit 1
fi

echo "✅ Endpoint: ${ENDPOINT}"
echo ""

# Get Lambda role ARN
DOC_ROLE=$(aws lambda get-function-configuration \
    --function-name solaris-poc-document-processor \
    --profile "${AWS_PROFILE}" \
    --region "${AWS_REGION}" \
    --query 'Role' --output text)

echo "Testing with role: ${DOC_ROLE}"
echo ""

# Test IAM authentication using Python
cat > /tmp/test_opensearch_iam.py <<'PYTHON_EOF'
import sys
import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

endpoint = sys.argv[1]
region = sys.argv[2]

print(f"Testing IAM authentication to {endpoint}...")

try:
    # Get AWS credentials
    credentials = boto3.Session().get_credentials()
    if not credentials:
        print("❌ Failed to get AWS credentials")
        sys.exit(1)
    
    # Create IAM auth
    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'es',
        session_token=credentials.token
    )
    
    # Create OpenSearch client
    client = OpenSearch(
        hosts=[{"host": endpoint.replace("https://", "").replace("http://", ""), "port": 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30,
    )
    
    # Test connection - check cluster health
    print("Testing cluster health check...")
    health = client.cluster.health()
    print(f"✅ Cluster health: {health['status']}")
    
    # Test index operations
    index_name = "turbine-documents"
    print(f"\nTesting index operations on '{index_name}'...")
    
    # Check if index exists
    exists = client.indices.exists(index=index_name)
    if exists:
        print(f"✅ Index '{index_name}' exists")
        
        # Get index stats
        stats = client.indices.stats(index=index_name)
        doc_count = stats['indices'][index_name]['total']['docs']['count']
        print(f"✅ Index has {doc_count} documents")
    else:
        print(f"⚠️  Index '{index_name}' does not exist")
        print("Attempting to create index...")
        try:
            client.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "text": {"type": "text"},
                            "embedding": {
                                "type": "knn_vector",
                                "dimension": 1536,
                            },
                            "turbine_model": {"type": "keyword"},
                            "document_type": {"type": "keyword"},
                            "source": {"type": "keyword"},
                        }
                    }
                }
            )
            print(f"✅ Successfully created index '{index_name}'")
        except Exception as e:
            print(f"❌ Failed to create index: {e}")
            sys.exit(1)
    
    print("\n✅ All tests passed! IAM authentication is working.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_EOF

echo "Running IAM authentication test..."
python3 /tmp/test_opensearch_iam.py "${ENDPOINT}" "${AWS_REGION}" \
    --profile "${AWS_PROFILE}" 2>&1 || {
    echo ""
    echo "⚠️  Test failed. This could mean:"
    echo "   1. IAM authentication not configured yet"
    echo "   2. Role mappings not set up"
    echo "   3. OpenSearch endpoint not accessible"
    echo ""
    echo "Next steps:"
    echo "  1. Configure OpenSearch master user to IAM ARN"
    echo "  2. Set up role mappings in OpenSearch Dashboards"
    echo "  3. Verify endpoint is accessible from your network"
}

rm -f /tmp/test_opensearch_iam.py

