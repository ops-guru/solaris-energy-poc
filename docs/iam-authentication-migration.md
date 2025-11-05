# IAM Authentication Migration Guide

**Status**: ✅ Code Migration Complete  
**Date**: 2025-11-04  
**Next Step**: Deploy via CI/CD and configure OpenSearch Master User to use IAM ARN

## Deployment Process

This project uses **GitHub Actions for automated CI/CD**. After committing and pushing changes:

1. **GitHub Actions** automatically triggers on push to `main` branch
2. CDK synthesis validates the infrastructure changes
3. All stacks are deployed to AWS automatically
4. Lambda functions are packaged and deployed with updated code

**No manual `cdk deploy` needed** - the pipeline handles everything.

For local testing or one-off deployments, you can still use `cdk deploy --all` with the `mavenlink-functions` AWS profile, but production deployments should always go through the CI/CD pipeline.

## Changes Made

### 1. Lambda Functions Updated ✅

#### Document Processor (`lambda/document-processor/handler.py`)
- ✅ Removed password-based authentication
- ✅ Added IAM authentication using `requests-aws4auth`
- ✅ Uses Lambda execution role credentials
- ✅ No environment variables for username/password

#### Agent Workflow (`lambda/agent-workflow/handler.py` & `opensearch_helper.py`)
- ✅ Removed password-based authentication
- ✅ Updated `get_opensearch_client()` to use IAM only
- ✅ Removed `OPENSEARCH_USER` and `OPENSEARCH_PASSWORD` environment variables

### 2. Infrastructure Updated ✅

#### ComputeStack (`infrastructure/solaris_poc/compute_stack.py`)
- ✅ Removed `OPENSEARCH_MASTER_USER` environment variable
- ✅ Removed `OPENSEARCH_MASTER_PASSWORD` environment variable
- ✅ Lambda functions now use IAM roles for authentication

#### Requirements Files
- ✅ Added `requests-aws4auth>=1.2.3` to both Lambda function requirements

### 3. OpenSearch Domain Configuration ⚠️

**Manual Configuration Required**: The OpenSearch domain currently uses internal user database with username/password. We need to configure it to use IAM for the master user.

## Manual Configuration Steps

### Step 1: Get Lambda Role ARNs

After deploying the updated stacks, get the Lambda role ARNs:

```bash
# Document Processor role ARN
DOC_ROLE=$(aws lambda get-function-configuration \
  --function-name solaris-poc-document-processor \
  --profile mavenlink-functions \
  --region us-east-1 \
  --query 'Role' --output text)

echo "Document Processor Role: $DOC_ROLE"

# Agent Workflow role ARN
AGENT_ROLE=$(aws lambda get-function-configuration \
  --function-name solaris-poc-agent-workflow \
  --profile mavenlink-functions \
  --region us-east-1 \
  --query 'Role' --output text)

echo "Agent Workflow Role: $AGENT_ROLE"
```

### Step 2: Configure OpenSearch Master User

**Option A: Via AWS Console** (Recommended for first-time setup)

1. Go to [OpenSearch Service Console](https://console.aws.amazon.com/es/home?region=us-east-1)
2. Click on domain: `solaris-poc-vector-store`
3. Click **"Actions"** → **"Modify domain"**
4. Scroll to **"Fine-grained access control"** section
5. Click **"Edit"**
6. Select **"Master user"** → **"IAM ARN"**
7. Enter the Document Processor role ARN:
   ```
   arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole-XXXXX
   ```
8. Click **"Save changes"**
9. Wait 5-10 minutes for changes to propagate

**Option B: Via AWS CLI**

```bash
# Get current domain configuration
aws opensearch describe-domain \
  --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --region us-east-1 \
  --query 'DomainStatus.AdvancedSecurityOptions'

# Update master user to IAM ARN
# Note: This requires updating the domain configuration
# You may need to use a custom resource or modify via console
```

**⚠️ Important**: Changing the master user requires domain configuration update, which may take 5-10 minutes and could cause brief interruption.

### Step 3: Configure OpenSearch Role Mappings

After setting the master user to an IAM ARN, configure role mappings so Lambda functions can access OpenSearch:

**Via OpenSearch Dashboards**:

1. Access OpenSearch Dashboards (you'll need to use the master user IAM role to sign in)
2. Navigate to **Security** → **Roles**
3. Create a role (e.g., `lambda-access-role`) with permissions:
   - **Index permissions**: `turbine-documents` (read, write, manage)
   - **Cluster permissions**: `cluster_monitor`, `cluster_composite_ops`
4. Navigate to **Security** → **Role Mappings**
5. Map IAM roles to OpenSearch roles:
   - Map Document Processor role → `lambda-access-role`
   - Map Agent Workflow role → `lambda-access-role`

**Via OpenSearch REST API**:

```bash
# Create role mapping
curl -X PUT "https://vpc-solaris-poc-vector-store-xxxxx.us-east-1.es.amazonaws.com/_plugins/_security/api/rolesmapping/lambda-access-role" \
  -H 'Content-Type: application/json' \
  -u "arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole-XXXXX" \
  -d '{
    "backend_roles": [
      "arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole-XXXXX",
      "arn:aws:iam::720119760662:role/ComputeStack-AgentWorkflowRole-XXXXX"
    ]
  }'
```

**⚠️ Note**: You'll need to authenticate using the master user IAM role. This may require using AWS SigV4 signing.

### Step 4: Verify Configuration

1. **Test Document Processor**:
   ```bash
   aws lambda invoke \
     --function-name solaris-poc-document-processor \
     --payload '{"s3_bucket": "solaris-poc-documents-720119760662-us-east-1", "s3_key": "manuals/Solaris_SMT60_Technical_Specs.pdf", "turbine_model": "SMT60", "document_type": "technical-specs"}' \
     --cli-binary-format raw-in-base64-out \
     --profile mavenlink-functions \
     --region us-east-1 \
     /tmp/test-output.json
   
   cat /tmp/test-output.json | jq
   ```

2. **Check CloudWatch Logs**:
   ```bash
   aws logs tail /aws/lambda/solaris-poc-document-processor \
     --since 5m \
     --profile mavenlink-functions \
     --region us-east-1 \
     | grep -i "index\|stored\|error\|successfully"
   ```

3. **Test Agent Workflow**:
   ```bash
   aws lambda invoke \
     --function-name solaris-poc-agent-workflow \
     --payload '{"query": "How do I troubleshoot low oil pressure?", "session_id": "test-iam"}' \
     --cli-binary-format raw-in-base64-out \
     --profile mavenlink-functions \
     --region us-east-1 \
     /tmp/test-agent.json
   
   cat /tmp/test-agent.json | jq
   ```

## Expected Behavior After Migration

### ✅ Success Indicators

- Lambda functions connect to OpenSearch without password errors
- Document processor successfully creates index and stores chunks
- Agent workflow successfully retrieves documents from OpenSearch
- CloudWatch logs show no authentication errors

### ❌ Common Issues

**Issue**: `403 Forbidden` errors  
**Solution**: Check role mappings in OpenSearch, ensure Lambda roles are mapped correctly

**Issue**: `401 Unauthorized` errors  
**Solution**: Verify OpenSearch master user is set to IAM ARN (not password)

**Issue**: Cannot access OpenSearch Dashboards  
**Solution**: Use AWS SSO or configure federated access (see `opensearch-production-authentication.md`)

## Security Benefits

✅ **No passwords in environment variables** - Eliminates credential exposure risk  
✅ **Automatic credential rotation** - IAM credentials rotate automatically  
✅ **Better audit trail** - CloudTrail logs all IAM-based access  
✅ **Least privilege** - IAM policies control access granularly  
✅ **Production-ready** - Aligns with AWS security best practices

## Next Steps

1. Deploy updated infrastructure: `cdk deploy --all`
2. Configure OpenSearch master user to use IAM ARN (Step 2 above)
3. Configure OpenSearch role mappings (Step 3 above)
4. Test Lambda functions (Step 4 above)
5. Verify no authentication errors in CloudWatch logs

## References

- [OpenSearch IAM Authentication](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html)
- [OpenSearch Role Mappings](https://opensearch.org/docs/latest/security/access-control/users-roles/)
- [Production Authentication Guide](./opensearch-production-authentication.md)
