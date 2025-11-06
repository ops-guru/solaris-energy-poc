#!/bin/bash
# Script to configure OpenSearch for IAM authentication
# This is a helper script - some steps must be done manually in AWS Console

set -e

AWS_PROFILE="${AWS_PROFILE:-mavenlink-functions}"
AWS_REGION="${AWS_REGION:-us-east-1}"
OPENSEARCH_DOMAIN="solaris-poc-vector-store"

echo "🔐 OpenSearch IAM Authentication Setup"
echo "======================================"
echo ""

# Get Lambda role ARNs
echo "📋 Getting Lambda role ARNs..."
DOC_ROLE=$(aws lambda get-function-configuration \
    --function-name solaris-poc-document-processor \
    --profile "${AWS_PROFILE}" \
    --region "${AWS_REGION}" \
    --query 'Role' --output text)

AGENT_ROLE=$(aws lambda get-function-configuration \
    --function-name solaris-poc-agent-workflow \
    --profile "${AWS_PROFILE}" \
    --region "${AWS_REGION}" \
    --query 'Role' --output text)

echo "✅ Document Processor Role:"
echo "   ${DOC_ROLE}"
echo ""
echo "✅ Agent Workflow Role:"
echo "   ${AGENT_ROLE}"
echo ""

# Check current OpenSearch configuration
echo "📊 Checking OpenSearch domain configuration..."
ADV_SEC=$(aws opensearch describe-domain \
    --domain-name "${OPENSEARCH_DOMAIN}" \
    --profile "${AWS_PROFILE}" \
    --region "${AWS_REGION}" \
    --query 'DomainStatus.AdvancedSecurityOptions' \
    --output json 2>/dev/null || echo "{}")

MASTER_USER_TYPE=$(echo "${ADV_SEC}" | jq -r '.MasterUserOptions.Type // "unknown"')
MASTER_USER_NAME=$(echo "${ADV_SEC}" | jq -r '.MasterUserOptions.MasterUserName // "unknown"')

echo "Current master user type: ${MASTER_USER_TYPE}"
echo "Current master user name: ${MASTER_USER_NAME}"
echo ""

if [ "${MASTER_USER_TYPE}" = "IAM" ]; then
    echo "✅ OpenSearch is already configured for IAM authentication!"
    echo ""
    echo "Next: Configure role mappings in OpenSearch Dashboards"
    echo "   See: docs/iam-authentication-migration.md"
else
    echo "⚠️  OpenSearch is using ${MASTER_USER_TYPE} authentication (not IAM)"
    echo ""
    echo "📝 Manual Steps Required (Cannot be automated via CLI):"
    echo ""
    echo "1. Go to AWS Console:"
    echo "   https://console.aws.amazon.com/es/home?region=${AWS_REGION}"
    echo ""
    echo "2. Click on domain: ${OPENSEARCH_DOMAIN}"
    echo ""
    echo "3. Click 'Actions' → 'Modify domain'"
    echo ""
    echo "4. Scroll to 'Fine-grained access control' section"
    echo ""
    echo "5. Click 'Edit'"
    echo ""
    echo "6. Select 'Master user' → 'IAM ARN'"
    echo ""
    echo "7. Enter this ARN as the master user:"
    echo "   ${DOC_ROLE}"
    echo ""
    echo "8. Click 'Save changes'"
    echo ""
    echo "9. Wait 5-10 minutes for changes to propagate"
    echo ""
    echo "10. After master user is set to IAM, configure role mappings:"
    echo "    - Access OpenSearch Dashboards"
    echo "    - Go to Security → Roles"
    echo "    - Create role 'lambda-access-role' with permissions:"
    echo "      * Index: turbine-documents (read, write, manage)"
    echo "      * Cluster: cluster_monitor, cluster_composite_ops"
    echo "    - Go to Security → Role Mappings"
    echo "    - Map these IAM roles to 'lambda-access-role':"
    echo "      * ${DOC_ROLE}"
    echo "      * ${AGENT_ROLE}"
    echo ""
fi

# Check access policy
echo "🔍 Checking OpenSearch access policy..."
ACCESS_POLICY=$(aws opensearch describe-domain \
    --domain-name "${OPENSEARCH_DOMAIN}" \
    --profile "${AWS_PROFILE}" \
    --region "${AWS_REGION}" \
    --query 'DomainStatus.AccessPolicies' \
    --output text 2>/dev/null || echo "{}")

echo "Access policy configured: $(if [ -z "${ACCESS_POLICY}" ] || [ "${ACCESS_POLICY}" = "{}" ]; then echo "❌ Not set"; else echo "✅ Set"; fi)"
echo ""

if [ -z "${ACCESS_POLICY}" ] || [ "${ACCESS_POLICY}" = "{}" ]; then
    echo "⚠️  Access policy is not set. You may need to add an access policy."
    echo ""
    echo "Recommended access policy (add in AWS Console → Domain → Actions → Modify domain → Access policies):"
    echo ""
    cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "${DOC_ROLE}",
          "${AGENT_ROLE}"
        ]
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:${AWS_REGION}:$(aws sts get-caller-identity --profile ${AWS_PROFILE} --query Account --output text):domain/${OPENSEARCH_DOMAIN}/*"
    }
  ]
}
EOF
    echo ""
fi

echo "✅ Setup information retrieved!"
echo ""
echo "📚 For detailed instructions, see: docs/iam-authentication-migration.md"

