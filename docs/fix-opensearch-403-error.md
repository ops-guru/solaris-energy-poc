# Fix OpenSearch 403 Error - IAM Authentication Configuration

**Date**: 2025-11-06  
**Issue**: Lambda functions getting `403 Forbidden` when accessing OpenSearch  
**Root Cause**: OpenSearch domain is using username/password authentication, but Lambda code uses IAM authentication

---

## Problem Summary

**Error**: 
```
HEAD https://vpc-solaris-poc-vector-store-.../turbine-documents [status:403]
AuthorizationException(403, '')
Error checking/creating index
```

**Root Cause**:
- ✅ Lambda code is using IAM authentication (`AWS4Auth`)
- ❌ OpenSearch domain is configured with username/password (`InternalUserDatabaseEnabled: true`)
- ❌ Mismatch causes 403 Forbidden errors

---

## Solution

Configure OpenSearch domain to use IAM authentication for the master user.

### Step 1: Get Lambda Role ARNs

Run the helper script:
```bash
./scripts/setup-opensearch-iam-auth.sh
```

Or manually:
```bash
# Document Processor Role
DOC_ROLE=$(aws lambda get-function-configuration \
    --function-name solaris-poc-document-processor \
    --profile mavenlink-functions \
    --query 'Role' --output text)

# Agent Workflow Role  
AGENT_ROLE=$(aws lambda get-function-configuration \
    --function-name solaris-poc-agent-workflow \
    --profile mavenlink-functions \
    --query 'Role' --output text)

echo "Document Processor: ${DOC_ROLE}"
echo "Agent Workflow: ${AGENT_ROLE}"
```

**Expected Output**:
```
Document Processor: arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole12EFF6D7-bd7GiR8pj4uB
Agent Workflow: arn:aws:iam::720119760662:role/ComputeStack-AgentWorkflowRole7F667481-1MYYKva7Ya6a
```

### Step 2: Configure OpenSearch Master User to IAM ARN

**⚠️ This must be done in AWS Console** (cannot be automated via CLI/CDK easily):

1. **Open AWS Console**:
   - Go to: https://console.aws.amazon.com/es/home?region=us-east-1
   - Click on domain: `solaris-poc-vector-store`

2. **Modify Domain**:
   - Click **"Actions"** → **"Modify domain"**
   - Scroll to **"Fine-grained access control"** section
   - Click **"Edit"**

3. **Change Master User**:
   - Select **"Master user"** → **"IAM ARN"** (not "Master user name")
   - Enter the Document Processor role ARN:
     ```
     arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole12EFF6D7-bd7GiR8pj4uB
     ```
   - Click **"Save changes"**

4. **Wait for Update**:
   - Domain update takes 5-10 minutes
   - Status will show "Processing" during update
   - Wait until status is "Active"

### Step 3: Configure Role Mappings in OpenSearch

After master user is set to IAM, configure role mappings:

#### Option A: Via OpenSearch Dashboards (Recommended)

1. **Access Dashboards**:
   - In OpenSearch console, click **"OpenSearch Dashboards URL"**
   - Sign in using AWS SSO (you'll need to assume the master user IAM role)

2. **Create OpenSearch Role**:
   - Navigate to **Security** → **Roles**
   - Click **"Create role"**
   - Role name: `lambda-access-role`
   - **Index permissions**:
     - Index: `turbine-documents`
     - Permissions: `read`, `write`, `create_index`, `manage`
   - **Cluster permissions**:
     - `cluster_monitor`
     - `cluster_composite_ops`
   - Click **"Create"**

3. **Map IAM Roles**:
   - Navigate to **Security** → **Role Mappings**
   - Click **"Create role mapping"**
   - Role: `lambda-access-role`
   - **Backend roles**: Add both Lambda role ARNs:
     ```
     arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole12EFF6D7-bd7GiR8pj4uB
     arn:aws:iam::720119760662:role/ComputeStack-AgentWorkflowRole7F667481-1MYYKva7Ya6a
     ```
   - Click **"Create"**

#### Option B: Via OpenSearch REST API

```bash
# Get OpenSearch endpoint
ENDPOINT=$(aws opensearch describe-domain \
    --domain-name solaris-poc-vector-store \
    --profile mavenlink-functions \
    --query 'DomainStatus.Endpoint' \
    --output text)

# Create role (requires AWS SigV4 signing)
# Use AWS CLI with SigV4 signing or use Python script
```

See `docs/iam-authentication-migration.md` for REST API examples.

### Step 4: Verify Configuration

1. **Test Document Processor**:
   ```bash
   aws lambda invoke \
     --function-name solaris-poc-document-processor \
     --payload '{"s3_bucket": "solaris-poc-documents-720119760662-us-east-1", "s3_key": "manuals/Solaris_SMT60_Technical_Specs.pdf", "turbine_model": "SMT60", "document_type": "technical-specs"}' \
     --cli-binary-format raw-in-base64-out \
     --profile mavenlink-functions \
     /tmp/test-output.json
   
   cat /tmp/test-output.json | jq
   ```

2. **Check CloudWatch Logs**:
   ```bash
   aws logs tail /aws/lambda/solaris-poc-document-processor \
     --since 5m \
     --profile mavenlink-functions \
     | grep -i "index\|stored\|error\|successfully"
   ```

3. **Expected Success**:
   - ✅ No 403 errors
   - ✅ Index created successfully
   - ✅ Chunks stored (chunks_stored > 0)

---

## Why This Can't Be Automated in CDK

CDK's `AdvancedSecurityOptions` doesn't support directly setting master user to IAM ARN during initial domain creation when fine-grained access control is first enabled. The domain must be created first, then the master user can be changed to IAM ARN.

**Workaround Options**:
1. **Manual Configuration** (Current approach) - Configure via console
2. **Custom Resource** - Create a Lambda-backed custom resource to configure after domain creation
3. **Two-Stage Deployment** - Deploy domain, then update master user, then configure role mappings

For POC, manual configuration is acceptable. For production, consider a custom resource.

---

## Current Status

- ✅ Lambda code migrated to IAM authentication
- ✅ Lambda roles have OpenSearch permissions (`es:*`)
- ❌ OpenSearch domain still using username/password
- ⏳ **Action Required**: Configure OpenSearch master user to IAM ARN (manual step)

---

## After Configuration

Once configured, the Lambda functions will:
- ✅ Authenticate using IAM (no passwords)
- ✅ Access OpenSearch using role mappings
- ✅ Create indices and store documents
- ✅ Query documents for RAG retrieval

---

**Next Steps**: Follow Step 2 above to configure OpenSearch master user to IAM ARN, then Step 3 to configure role mappings.

