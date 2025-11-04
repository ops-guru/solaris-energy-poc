#!/usr/bin/env bash
#
# Explore OpenSearch and Bedrock Deployment
# 
# This script helps you explore the OpenSearch Service deployment and 
# check Bedrock model access for the Solaris Energy POC.
#
# Usage:
#   ./scripts/explore-opensearch-bedrock.sh [AWS_PROFILE]
#
# Example:
#   ./scripts/explore-opensearch-bedrock.sh mavenlink-functions
#

set -euo pipefail

# Configuration
AWS_PROFILE="${1:-mavenlink-functions}"
AWS_REGION="${AWS_REGION:-us-east-1}"
DOMAIN_NAME="solaris-poc-vector-store"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_section() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Validate AWS CLI
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Validate AWS credentials
log_info "Validating AWS credentials for profile: ${AWS_PROFILE}..."
if ! aws sts get-caller-identity --profile "${AWS_PROFILE}" &> /dev/null; then
    log_error "Failed to authenticate with AWS. Please check your credentials."
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile "${AWS_PROFILE}" --query Account --output text)
log_success "Authenticated as Account: ${AWS_ACCOUNT_ID}, Region: ${AWS_REGION}"

# ============================================================================
# OPENSEARCH EXPLORATION
# ============================================================================

log_section "OpenSearch Service Domain: ${DOMAIN_NAME}"

log_info "Checking if OpenSearch domain exists..."
if aws opensearch describe-domain --domain-name "${DOMAIN_NAME}" --profile "${AWS_PROFILE}" --region "${AWS_REGION}" &> /dev/null; then
    log_success "OpenSearch domain found!"
    
    # Get domain details
    log_info "Fetching domain details..."
    DOMAIN_INFO=$(aws opensearch describe-domain --domain-name "${DOMAIN_NAME}" --profile "${AWS_PROFILE}" --region "${AWS_REGION}")
    
    # Parse key information
    ENDPOINT=$(echo "${DOMAIN_INFO}" | jq -r '.DomainStatus.Endpoint // .DomainStatus.Endpoints.vpc // "N/A"')
    DOMAIN_ID=$(echo "${DOMAIN_INFO}" | jq -r '.DomainStatus.DomainId // "N/A"')
    VERSION=$(echo "${DOMAIN_INFO}" | jq -r '.DomainStatus.ElasticsearchVersion // "N/A"')
    CLUSTER_STATUS=$(echo "${DOMAIN_INFO}" | jq -r '.DomainStatus.Processing // "N/A"')
    CREATED=$(echo "${DOMAIN_INFO}" | jq -r '.DomainStatus.Created // "N/A"')
    
    echo ""
    echo -e "${GREEN}Domain Details:${NC}"
    echo -e "  Name:         ${CYAN}${DOMAIN_NAME}${NC}"
    echo -e "  Domain ID:    ${CYAN}${DOMAIN_ID}${NC}"
    echo -e "  Version:      ${CYAN}${VERSION}${NC}"
    echo -e "  Status:       ${CYAN}${CLUSTER_STATUS}${NC}"
    echo -e "  Created:      ${CYAN}${CREATED}${NC}"
    echo -e "  Endpoint:     ${CYAN}${ENDPOINT}${NC}"
    
    # Get VPC configuration
    VPC_ID=$(echo "${DOMAIN_INFO}" | jq -r '.DomainStatus.VPCOptions.VPCId // "N/A"')
    if [ "${VPC_ID}" != "N/A" ] && [ "${VPC_ID}" != "null" ]; then
        echo -e "  VPC ID:       ${CYAN}${VPC_ID}${NC}"
        SUBNET_IDS=$(echo "${DOMAIN_INFO}" | jq -r '.DomainStatus.VPCOptions.SubnetIds[]? // empty' | tr '\n' ',' | sed 's/,$//')
        if [ -n "${SUBNET_IDS}" ]; then
            echo -e "  Subnets:      ${CYAN}${SUBNET_IDS}${NC}"
        fi
    fi
    
    # Get security group
    SECURITY_GROUP_IDS=$(echo "${DOMAIN_INFO}" | jq -r '.DomainStatus.VPCOptions.SecurityGroupIds[]? // empty' | tr '\n' ',' | sed 's/,$//')
    if [ -n "${SECURITY_GROUP_IDS}" ]; then
        echo -e "  Security Groups: ${CYAN}${SECURITY_GROUP_IDS}${NC}"
    fi
    
    # Check access
    echo ""
    if [ "${CLUSTER_STATUS}" = "false" ]; then
        log_success "Domain is active and ready!"
        
        # Provide access instructions
        echo ""
        log_info "Accessing OpenSearch Dashboards:"
        echo "  1. Go to AWS Console → OpenSearch Service"
        echo "  2. Click on domain: ${DOMAIN_NAME}"
        echo "  3. Click 'OpenSearch Dashboards URL' (or 'Dashboard URL')"
        echo "  4. Login credentials:"
        echo "     Username: admin"
        echo "     Password: Check CloudFormation outputs or Secrets Manager"
        echo ""
        echo "  Or access directly via:"
        echo "    https://${ENDPOINT}"
        echo ""
        
        log_info "Connecting from Lambda/Code:"
        echo "  Endpoint: ${ENDPOINT}"
        echo "  Username: admin"
        echo "  Password: TempP@ssw0rd123!Ch@ngeInProd (check your deployment)"
        echo ""
        
        # Try to get index information (if accessible)
        log_info "Checking for existing indices..."
        # Note: This would require proper credentials and network access
        echo "  (To check indices, use OpenSearch Dashboards or configure proper access)"
        
    else
        log_warning "Domain is still processing. Wait for it to become active."
    fi
    
    # CloudFormation stack reference
    echo ""
    log_info "Related CloudFormation Stack:"
    STACK_NAME=$(aws cloudformation list-stacks \
        --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
        --profile "${AWS_PROFILE}" \
        --region "${AWS_REGION}" \
        --query "StackSummaries[?contains(StackName, 'VectorStore')].StackName" \
        --output text 2>/dev/null || echo "")
    
    if [ -n "${STACK_NAME}" ]; then
        echo "  Stack: ${CYAN}${STACK_NAME}${NC}"
        echo "  View in console: https://console.aws.amazon.com/cloudformation/home?region=${AWS_REGION}#/stacks"
    else
        log_warning "CloudFormation stack not found. Domain may have been created manually."
    fi
    
else
    log_error "OpenSearch domain '${DOMAIN_NAME}' not found!"
    echo ""
    log_info "The domain may not be deployed yet. To deploy:"
    echo "  cd infrastructure"
    echo "  export AWS_PROFILE=${AWS_PROFILE}"
    echo "  cdk deploy VectorStoreStack"
    echo ""
    log_info "Or check all domains:"
    aws opensearch list-domain-names --profile "${AWS_PROFILE}" --region "${AWS_REGION}" --output table
fi

# ============================================================================
# BEDROCK EXPLORATION
# ============================================================================

log_section "AWS Bedrock Model Access"

log_info "Checking Bedrock model access..."

# List available foundation models
MODELS=$(aws bedrock list-foundation-models --profile "${AWS_PROFILE}" --region "${AWS_REGION}" --query 'modelSummaries[?providerName==`Anthropic` || providerName==`Amazon`]' 2>/dev/null || echo "[]")

if [ "${MODELS}" != "[]" ] && [ -n "${MODELS}" ]; then
    log_success "Bedrock is accessible!"
    echo ""
    
    # Check for Claude models
    CLAUDE_MODELS=$(echo "${MODELS}" | jq -r '.[] | select(.modelId | contains("claude")) | "\(.modelId) (\(.providerName))"' 2>/dev/null || echo "")
    if [ -n "${CLAUDE_MODELS}" ]; then
        echo -e "${GREEN}Available Claude Models:${NC}"
        echo "${CLAUDE_MODELS}" | while read -r model; do
            echo -e "  ${CYAN}• ${model}${NC}"
        done
        echo ""
    fi
    
    # Check for Titan models
    TITAN_MODELS=$(echo "${MODELS}" | jq -r '.[] | select(.modelId | contains("titan")) | "\(.modelId) (\(.providerName))"' 2>/dev/null || echo "")
    if [ -n "${TITAN_MODELS}" ]; then
        echo -e "${GREEN}Available Titan Models:${NC}"
        echo "${TITAN_MODELS}" | while read -r model; do
            echo -e "  ${CYAN}• ${model}${NC}"
        done
        echo ""
    fi
    
    # Check model access status
    log_info "Checking specific model access..."
    
    # Models used in the project
    PROJECT_MODELS=(
        "anthropic.claude-3-5-sonnet-20241022-v2:0"
        "amazon.titan-embed-text-v1"
    )
    
    for model in "${PROJECT_MODELS[@]}"; do
        if echo "${MODELS}" | jq -e ".[] | select(.modelId == \"${model}\")" &> /dev/null; then
            log_success "  ${model} - Available"
        else
            log_warning "  ${model} - May need access request"
        fi
    done
    
    echo ""
    log_info "Accessing Bedrock in AWS Console:"
    echo "  https://console.aws.amazon.com/bedrock/home?region=${AWS_REGION}"
    echo ""
    echo "  To request model access:"
    echo "  1. Go to 'Model access' in the left sidebar"
    echo "  2. Click 'Manage model access'"
    echo "  3. Select the models you need (Claude 3.5 Sonnet, Titan Embeddings)"
    echo "  4. Click 'Save changes'"
    echo "  5. Wait for access to be granted (usually instant for most models)"
    echo ""
    
    # Try a test invocation (optional)
    log_info "Testing Bedrock invocation (optional)..."
    TEST_RESULT=$(aws bedrock-runtime invoke-model \
        --model-id "amazon.titan-embed-text-v1" \
        --body '{"inputText":"test"}' \
        --content-type "application/json" \
        --accept "application/json" \
        --profile "${AWS_PROFILE}" \
        --region "${AWS_REGION}" \
        /tmp/bedrock-test.json 2>&1 || echo "ERROR")
    
    if echo "${TEST_RESULT}" | grep -q "ERROR"; then
        ERROR_MSG=$(echo "${TEST_RESULT}" | grep -i "error" | head -1)
        if echo "${ERROR_MSG}" | grep -qi "access"; then
            log_warning "Model access may not be granted. Request access in console."
        else
            log_warning "Test invocation failed: ${ERROR_MSG}"
        fi
    else
        log_success "Bedrock invocation test successful!"
        rm -f /tmp/bedrock-test.json
    fi
    
else
    log_error "Unable to list Bedrock models. Check:"
    echo "  1. Bedrock is enabled in region: ${AWS_REGION}"
    echo "  2. IAM permissions for bedrock:ListFoundationModels"
    echo "  3. AWS Console: https://console.aws.amazon.com/bedrock/home?region=${AWS_REGION}"
    echo ""
fi

# ============================================================================
# SUMMARY & NEXT STEPS
# ============================================================================

log_section "Summary & Next Steps"

echo -e "${GREEN}✅ Exploration Complete!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. ${CYAN}Access OpenSearch Dashboards:${NC}"
echo "   - Go to AWS Console → OpenSearch Service"
echo "   - Select domain: ${DOMAIN_NAME}"
echo "   - Click 'Dashboard URL' or 'OpenSearch Dashboards URL'"
echo "   - Login: admin / [password from CloudFormation or Secrets Manager]"
echo ""
echo "2. ${CYAN}Request Bedrock Model Access (if needed):${NC}"
echo "   - Go to: https://console.aws.amazon.com/bedrock/home?region=${AWS_REGION}"
echo "   - Navigate to 'Model access' → 'Manage model access'"
echo "   - Enable: Claude 3.5 Sonnet and Titan Embeddings"
echo ""
echo "3. ${CYAN}Test OpenSearch Connection:${NC}"
echo "   - Use OpenSearch Dashboards to create/test queries"
echo "   - Check if 'turbine-documents' index exists"
echo "   - Test k-NN search functionality"
echo ""
echo "4. ${CYAN}Test Bedrock Models:${NC}"
echo "   - Use Bedrock Playground in console to test models"
echo "   - Or use AWS CLI to invoke models programmatically"
echo ""
echo "For more information, see:"
echo "  - docs/architecture.md"
echo "  - lambda/document-processor/README.md"
echo ""
