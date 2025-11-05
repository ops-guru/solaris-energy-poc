# OpenSearch 403 Forbidden - Troubleshooting Guide

## Current Issue

**Symptom**: Lambda function getting `403 Forbidden` when trying to:
- Check if index exists
- Create index
- Store documents in OpenSearch

**Lambda**: `solaris-poc-document-processor`
**OpenSearch Domain**: `solaris-poc-vector-store`

## Root Cause Analysis

403 Forbidden typically means **authentication succeeded but authorization failed**, or **authentication is failing**. For OpenSearch with fine-grained access control, this could be:

1. **Password mismatch** between Lambda environment variable and OpenSearch console
2. **Access policy** not allowing the Lambda's IAM role
3. **Fine-grained access control** requires role mappings
4. **Password not properly saved** in OpenSearch console

## Step-by-Step Fix

### Step 1: Verify Password in OpenSearch Console

1. Go to [OpenSearch Service Console](https://console.aws.amazon.com/es/home?region=us-east-1)
2. Click on domain: **`solaris-poc-vector-store`**
3. Go to **"Security configuration"** tab (or click "Actions" → "Modify domain")
4. Under **"Fine-grained access control"**:
   - Verify **"Master username"** is: `admin`
   - Check if there's a **"Master user password"** field
   - If password field shows `*****` or is hidden, you need to **set it again**

5. **Reset the password**:
   - Click **"Edit"** on Fine-grained access control
   - Set **"Master user password"** to: `TempP@ssw0rd123!Ch@ngeInProd`
   - **Important**: Choose **"Master user password"** option (not IAM)
   - Save the configuration

6. **Wait 5-10 minutes** for the password change to propagate

### Step 2: Verify Lambda Environment Variables

**Current Lambda configuration** (verified):
```json
{
  "OPENSEARCH_ENDPOINT": "vpc-solaris-poc-vector-store-...",
  "OPENSEARCH_INDEX": "turbine-documents",
  "OPENSEARCH_MASTER_USER": "admin",
  "OPENSEARCH_MASTER_PASSWORD": "TempP@ssw0rd123!Ch@ngeInProd"
}
```

**Verify these match exactly** what's in the OpenSearch console.

### Step 3: Check OpenSearch Access Policy

The access policy must allow the Lambda's IAM role. Check the access policy:

1. In OpenSearch console, domain details page
2. Click **"Actions"** → **"Modify domain"** → **"Access policies"** tab
3. Verify the access policy includes something like:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole*"
        ]
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:720119760662:domain/solaris-poc-vector-store/*"
    }
  ]
}
```

**If access policy is empty or doesn't include the Lambda role**, add it.

### Step 4: Check Fine-Grained Access Control Settings

1. In OpenSearch console → Domain → **"Security configuration"**
2. Under **"Fine-grained access control"**:
   - **Enabled**: Should be ✅ Yes
   - **Master user name**: `admin`
   - **Master user password**: Should be set (not using IAM)

3. **Important**: If using **"Internal user database"** (not IAM), make sure:
   - Master username: `admin`
   - Master password: `TempP@ssw0rd123!Ch@ngeInProd` (matches Lambda)

### Step 5: Verify IAM Role Permissions

The Lambda's IAM role needs OpenSearch permissions:

```bash
# Get the role name
ROLE_NAME=$(aws lambda get-function-configuration \
  --function-name solaris-poc-document-processor \
  --profile mavenlink-functions \
  --region us-east-1 \
  --query 'Role' --output text | rev | cut -d'/' -f1 | rev)

echo "Role: $ROLE_NAME"

# Check attached policies
aws iam list-attached-role-policies \
  --role-name "$ROLE_NAME" \
  --profile mavenlink-functions
```

The role should have policies that allow `es:*` on the OpenSearch domain.

### Step 6: Test Authentication

Once password is reset, wait 10 minutes, then test:

```bash
# Re-invoke the document processor
aws lambda invoke \
  --function-name solaris-poc-document-processor \
  --payload '{"s3_bucket": "solaris-poc-documents-720119760662-us-east-1", "s3_key": "manuals/Solaris_SMT60_Technical_Specs.pdf", "turbine_model": "SMT60", "document_type": "technical-specs"}' \
  --cli-binary-format raw-in-base64-out \
  --profile mavenlink-functions \
  --region us-east-1 \
  /tmp/test-output.json

# Check logs
aws logs tail /aws/lambda/solaris-poc-document-processor \
  --since 2m \
  --profile mavenlink-functions \
  --region us-east-1 \
  | grep -i "index\|stored\|403\|successfully"
```

## Common Issues & Solutions

### Issue 1: Password Not Saving

**Symptom**: Password field shows `*****` but you're not sure if it saved

**Solution**: 
- OpenSearch sometimes doesn't show password confirmation
- Try saving again with the exact password
- Wait 10 minutes after saving

### Issue 2: Access Policy Blocks Everything

**Symptom**: Access policy is too restrictive or missing

**Solution**: Update access policy to allow the Lambda role:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:ACCOUNT:domain/solaris-poc-vector-store/*"
    }
  ]
}
```

**⚠️ Warning**: The `"AWS": "*"` is permissive for POC. For production, restrict to specific roles.

### Issue 3: Fine-Grained Access Control Configuration

**Symptom**: Fine-grained access control is enabled but not configured correctly

**Solution**:
- Make sure you're using **"Internal user database"** (not IAM)
- Master username: `admin`
- Master password: Must match Lambda environment variable exactly

### Issue 4: VPC Endpoint Issues

**Symptom**: Lambda can't reach OpenSearch (different from 403)

**Solution**:
- This would be a different error (connection timeout, not 403)
- Check security groups allow Lambda → OpenSearch on port 443
- Check VPC route tables

## Verification Checklist

- [ ] Password reset in OpenSearch console
- [ ] Waited 10 minutes after password change
- [ ] Lambda environment variables match OpenSearch config
- [ ] Access policy includes Lambda role (or allows `*` for POC)
- [ ] Fine-grained access control uses "Internal user database"
- [ ] Master username is `admin` (matches Lambda)
- [ ] IAM role has `es:*` permissions
- [ ] Security groups allow Lambda → OpenSearch connectivity

## Next Steps After Fix

Once authentication works:

1. Re-invoke document processor Lambda
2. Check CloudWatch logs for:
   - ✅ `"Creating index turbine-documents"`
   - ✅ `"Successfully created index turbine-documents"`
   - ✅ `"Stored X chunks in OpenSearch"` (where X > 0)
3. Verify index exists (see `check-opensearch-index.md`)

## Alternative: Use IAM Authentication

If basic auth continues to fail, we could switch to IAM-based authentication:

1. Change OpenSearch to use IAM for master user
2. Update Lambda to use IAM role credentials (no password)
3. Requires changes to both OpenSearch config and Lambda code

**This is more complex but more secure for production.**
