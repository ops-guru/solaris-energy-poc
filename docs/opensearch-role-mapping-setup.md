# OpenSearch Role Mapping Setup

## Current Status

✅ **Document Processor Lambda**: Can write to OpenSearch (index creation and document storage working)
❌ **Agent Workflow Lambda**: Cannot read from OpenSearch (403 error: `no permissions for [indices:data/read/search]`)

Both Lambdas authenticate via IAM successfully, but OpenSearch needs role mappings configured to grant the Agent Workflow role read permissions.

## The Problem

OpenSearch Fine-grained Access Control (FGAC) requires explicit role mappings to grant permissions. The Document Processor role can write because it's likely been granted admin permissions (as the master user), but the Agent Workflow role needs read permissions explicitly configured.

## Solution: Configure Role Mappings

There are two approaches:

### Approach 1: OpenSearch Dashboards (Recommended)

1. **Access OpenSearch Dashboards**:
   - AWS Console → OpenSearch → Domain: `solaris-poc-vector-store`
   - Click "OpenSearch Dashboards URL" (requires VPN or bastion if domain is in VPC)
   - Or use `https://<domain-endpoint>/_dashboards`

2. **Login** (if required):
   - If master user is IAM ARN: Use AWS IAM credentials
   - If master user is username/password: Use those credentials

3. **Configure Role Mappings**:
   - Navigate to: **Security** → **Roles** → **all_access** (or create a custom role)
   - Click **Mapped users** tab
   - Click **Manage mapping**
   - Add IAM role ARN: `arn:aws:iam::720119760662:role/ComputeStack-AgentWorkflowRole7F667481-1MYYKva7Ya6a`
   - Click **Map**

4. **Create Custom Role (Better Practice)**:
   - **Security** → **Roles** → **Create role**
   - Role name: `lambda-read-role`
   - Index permissions:
     - Index patterns: `turbine-documents`
     - Permissions: `read`, `read` (document-level)
   - Cluster permissions: None needed
   - Click **Create**
   - Map the Agent Workflow role ARN to this custom role

### Approach 2: REST API (If Dashboards Not Accessible)

If you can't access Dashboards, you can use the OpenSearch REST API:

```bash
# Get the OpenSearch endpoint
ENDPOINT="vpc-solaris-poc-vector-store-6jo7ag22uxlh2qlse7mgnhrmay.us-east-1.es.amazonaws.com"
ROLE_ARN="arn:aws:iam::720119760662:role/ComputeStack-AgentWorkflowRole7F667481-1MYYKva7Ya6a"

# Sign the request (requires AWS credentials)
aws es describe-domain --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --region us-east-1

# Create role mapping via REST API (requires signing)
# This is complex - use Dashboards if possible
```

### Approach 3: AWS CLI (OpenSearch Serverless Only)

If using OpenSearch Serverless, you can use AWS CLI. However, for provisioned domains, role mappings must be configured in Dashboards or via the REST API.

## Verify Configuration

After configuring role mappings, test the Agent Workflow:

```bash
aws lambda invoke \
  --function-name solaris-poc-agent-workflow \
  --payload '{"query":"What is the maximum power output of the SMT60 turbine?","session_id":"test-123"}' \
  --cli-binary-format raw-in-base64-out \
  --profile mavenlink-functions \
  /tmp/agent-test.json

# Check logs
aws logs tail /aws/lambda/solaris-poc-agent-workflow \
  --since 2m \
  --profile mavenlink-functions | grep -i "Retrieved\|403\|error"
```

Success criteria:
- ✅ No 403 errors in logs
- ✅ Logs show "Retrieved X docs from OpenSearch"
- ✅ Response includes citations and confidence score > 0.5

## Lambda Role ARNs

For reference, here are the Lambda role ARNs:

- **Document Processor**: `arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole12EFF6D7-<suffix>`
- **Agent Workflow**: `arn:aws:iam::720119760662:role/ComputeStack-AgentWorkflowRole7F667481-1MYYKva7Ya6a`

You can retrieve the exact ARNs using:

```bash
aws iam list-roles \
  --profile mavenlink-functions \
  --query 'Roles[?contains(RoleName, `DocumentProcessor`) || contains(RoleName, `AgentWorkflow`)].{Name:RoleName,Arn:Arn}' \
  --output table
```

## Next Steps

1. ✅ Document Processor can write (verified)
2. ⏳ Configure Agent Workflow role mapping for read access
3. ⏳ Test end-to-end RAG flow
4. ⏳ Process all PDF documents from S3
5. ⏳ Test with real user queries via frontend

