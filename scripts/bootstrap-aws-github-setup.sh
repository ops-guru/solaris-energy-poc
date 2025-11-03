#!/usr/bin/env bash
#
# Bootstrap script for AWS GitHub Actions CI/CD setup
# This script creates the necessary IAM resources for GitHub OIDC-based deployments
#
# Usage:
#   ./scripts/bootstrap-aws-github-setup.sh [AWS_PROFILE] [GITHUB_ORG] [GITHUB_REPO]
#
# Example:
#   ./scripts/bootstrap-aws-github-setup.sh mavenlink-functions ops-guru solaris-energy-poc
#

set -euo pipefail

# Configuration
AWS_PROFILE="${1:-default}"
GITHUB_ORG="${2:-ops-guru}"
GITHUB_REPO="${3:-solaris-energy-poc}"
ROLE_NAME="GitHubActions${GITHUB_REPO//-/}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "\n${BLUE}━━━${NC} $1 ${BLUE}━━━${NC}"
}

# Validate AWS CLI is installed
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Validate AWS credentials work
log_info "Validating AWS credentials for profile: ${AWS_PROFILE}..."
if ! aws sts get-caller-identity --profile "${AWS_PROFILE}" &> /dev/null; then
    log_error "Failed to authenticate with AWS. Please check your credentials."
    exit 1
fi

log_success "AWS credentials validated"

# Get AWS account ID
log_info "Getting AWS account information..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile "${AWS_PROFILE}" --query Account --output text)
AWS_REGION=$(aws configure get region --profile "${AWS_PROFILE}" 2>/dev/null || echo "us-east-1")

log_success "Account ID: ${AWS_ACCOUNT_ID}, Region: ${AWS_REGION}"

# Step 1: Create GitHub OIDC Provider
log_step "Step 1: Checking GitHub OIDC Provider"

OIDC_PROVIDER_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"

if aws iam list-open-id-connect-providers --profile "${AWS_PROFILE}" --query "OpenIDConnectProviderList[?Arn=='${OIDC_PROVIDER_ARN}'].Arn" --output text | grep -q "${OIDC_PROVIDER_ARN}"; then
    log_warning "GitHub OIDC Provider already exists"
else
    log_info "Creating GitHub OIDC Provider..."
    if aws iam create-open-id-connect-provider \
        --url https://token.actions.githubusercontent.com \
        --client-id-list sts.amazonaws.com \
        --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
        --profile "${AWS_PROFILE}" &> /dev/null; then
        log_success "GitHub OIDC Provider created"
    else
        log_error "Failed to create OIDC Provider (may already exist)"
    fi
fi

# Step 2: Create IAM Role
log_step "Step 2: Creating IAM Role for GitHub Actions"

# Check if role exists
if aws iam get-role --role-name "${ROLE_NAME}" --profile "${AWS_PROFILE}" &> /dev/null; then
    log_warning "IAM Role '${ROLE_NAME}' already exists"
    log_info "Updating trust policy..."
    
    # Update trust policy
    cat > /tmp/github-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "${OIDC_PROVIDER_ARN}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:${GITHUB_ORG}/${GITHUB_REPO}:ref:refs/heads/main"
        }
      }
    }
  ]
}
EOF
    
    aws iam update-assume-role-policy \
        --role-name "${ROLE_NAME}" \
        --policy-document file:///tmp/github-trust-policy.json \
        --profile "${AWS_PROFILE}" > /dev/null
    
    log_success "Trust policy updated"
else
    log_info "Creating IAM Role '${ROLE_NAME}'..."
    
    # Create trust policy
    cat > /tmp/github-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "${OIDC_PROVIDER_ARN}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:${GITHUB_ORG}/${GITHUB_REPO}:ref:refs/heads/main"
        }
      }
    }
  ]
}
EOF
    
    # Create role
    aws iam create-role \
        --role-name "${ROLE_NAME}" \
        --assume-role-policy-document file:///tmp/github-trust-policy.json \
        --description "IAM role for ${GITHUB_REPO} GitHub Actions CI/CD" \
        --profile "${AWS_PROFILE}" > /dev/null
    
    log_success "IAM Role created: ${ROLE_NAME}"
fi

# Step 3: Attach Policies
log_step "Step 3: Attaching IAM Policies"

log_info "Attaching PowerUserAccess policy..."
aws iam attach-role-policy \
    --role-name "${ROLE_NAME}" \
    --policy-arn arn:aws:iam::aws:policy/PowerUserAccess \
    --profile "${AWS_PROFILE}" > /dev/null 2>&1 || log_warning "Policy may already be attached"

log_success "Policies attached"

# Step 4: Get Role ARN
log_step "Step 4: Getting Role ARN"

ROLE_ARN=$(aws iam get-role --role-name "${ROLE_NAME}" --profile "${AWS_PROFILE}" --query 'Role.Arn' --output text)

log_success "Role ARN: ${ROLE_ARN}"

# Step 5: Bootstrap CDK
log_step "Step 5: Bootstrapping AWS CDK"

log_info "Checking if CDK is already bootstrapped..."
BOOTSTRAP_BUCKET="cdk-hnb659fds-assets-${AWS_ACCOUNT_ID}-${AWS_REGION}"

if aws s3 ls "s3://${BOOTSTRAP_BUCKET}" --profile "${AWS_PROFILE}" &> /dev/null; then
    log_warning "CDK appears to be already bootstrapped in this region"
else
    log_info "Bootstrapping CDK in ${AWS_REGION}..."
    
    if command -v cdk &> /dev/null; then
        cdk bootstrap aws://${AWS_ACCOUNT_ID}/${AWS_REGION} --profile "${AWS_PROFILE}" || log_error "CDK bootstrap failed"
    else
        log_warning "CDK CLI not found. Skipping bootstrap."
        log_info "You can bootstrap later with: cdk bootstrap aws://${AWS_ACCOUNT_ID}/${AWS_REGION}"
    fi
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_success "AWS GitHub Actions Setup Complete!"
echo ""
echo "Role Name:       ${ROLE_NAME}"
echo "Role ARN:        ${ROLE_ARN}"
echo "Account ID:      ${AWS_ACCOUNT_ID}"
echo "Region:          ${AWS_REGION}"
echo ""
echo "Next Step: Add the Role ARN to GitHub Secrets:"
echo ""
echo "  gh secret set AWS_ROLE_ARN --body \"${ROLE_ARN}\""
echo ""
echo "Or via GitHub UI:"
echo "  https://github.com/${GITHUB_ORG}/${GITHUB_REPO}/settings/secrets/actions"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup
rm -f /tmp/github-trust-policy.json

