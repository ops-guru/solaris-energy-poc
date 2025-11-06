# OpenSearch IAM ARN Configuration Issue

**Issue**: IAM ARN field resets to blank when editing, save appears to fail.

**Date**: 2025-11-06

---

## Problem Description

When trying to configure OpenSearch master user to use IAM ARN in AWS Console:
1. Click "Edit" on Fine-grained access control
2. Select "Set IAM ARN as master user"
3. Enter IAM ARN
4. Field resets to blank
5. Save fails

---

## Common Causes

### 1. Domain Not in "Active" State

**Check**:
```bash
aws opensearch describe-domain \
  --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --query 'DomainStatus.Processing' \
  --output text
```

**Solution**: Wait until domain is fully active before making changes.

### 2. Domain Configuration Change Already in Progress

**Check**: Domain status shows "Processing"

**Solution**: Wait for any pending configuration changes to complete before making new changes.

### 3. ARN Format Validation Issue

**Check**: Ensure ARN is correct format:
```
arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole12EFF6D7-bd7GiR8pj4uB
```

**Common Mistakes**:
- ❌ Missing `arn:aws:iam::` prefix
- ❌ Incorrect account ID
- ❌ Missing role name
- ❌ Extra spaces or special characters

### 4. Browser/Console UI Issue

**Try**:
- Clear browser cache
- Try different browser
- Try incognito/private mode
- Check browser console for JavaScript errors

### 5. Role Doesn't Exist or Wrong Account

**Verify Role Exists**:
```bash
aws iam get-role \
  --role-name ComputeStack-DocumentProcessorRole12EFF6D7-bd7GiR8pj4uB \
  --profile mavenlink-functions
```

---

## Alternative: Use AWS CLI

If the console isn't working, try using AWS CLI to update the configuration:

### Option 1: Update Domain Configuration (Advanced)

**⚠️ Warning**: This requires updating the entire domain configuration, which can cause downtime.

```bash
# Get current configuration
aws opensearch describe-domain-config \
  --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --region us-east-1 \
  > /tmp/domain-config.json

# Edit the JSON to set master user ARN
# Then apply the update
```

**Note**: This is complex and risky. Not recommended unless console completely fails.

### Option 2: Use AWS Console API (Recommended)

1. **Open Browser Developer Tools** (F12)
2. **Go to Network tab**
3. **Try to save the IAM ARN** in the console
4. **Look for the API call** that fails
5. **Check the error message** in the response

This will tell us exactly what error is occurring.

---

## Step-by-Step Troubleshooting

### Step 1: Verify Domain State

```bash
aws opensearch describe-domain \
  --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --query 'DomainStatus.{Processing:Processing,State:Processing,Endpoint:Endpoint}' \
  --output json
```

**Required**: Domain must be `Active` and `Processing: false`

### Step 2: Verify Role ARN

```bash
# Get the exact role ARN
DOC_ROLE=$(aws lambda get-function-configuration \
    --function-name solaris-poc-document-processor \
    --profile mavenlink-functions \
    --query 'Role' --output text)

echo "Role ARN: ${DOC_ROLE}"

# Verify role exists
aws iam get-role \
  --role-name $(echo ${DOC_ROLE} | rev | cut -d'/' -f1 | rev) \
  --profile mavenlink-functions
```

### Step 3: Check Current Configuration

```bash
aws opensearch describe-domain \
  --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --query 'DomainStatus.AdvancedSecurityOptions' \
  --output json
```

**Look for**:
- `InternalUserDatabaseEnabled: true` (needs to change)
- `MasterUserOptions.Type` (should change from "InternalUserDatabase" to "IAM")

### Step 4: Try Console with Exact Steps

1. **Open AWS Console** → OpenSearch Service
2. **Click domain**: `solaris-poc-vector-store`
3. **Click "Actions"** → **"Modify domain"**
4. **Scroll to "Fine-grained access control"**
5. **Click "Edit"** (not "Enable" - it's already enabled)
6. **IMPORTANT**: Don't change "Enable fine-grained access control" checkbox (keep it checked)
7. **Select "Set IAM ARN as master user"** radio button
8. **Paste the EXACT ARN** (copy from script output):
   ```
   arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole12EFF6D7-bd7GiR8pj4uB
   ```
9. **Click "Save changes"** at the bottom
10. **Wait for confirmation** - should show "Update in progress"

### Step 5: Check for Errors

**In Browser**:
- Open Developer Tools (F12)
- Go to Console tab
- Look for JavaScript errors
- Go to Network tab
- Try saving, look for failed requests
- Check error messages in response

**Common Errors**:
- "Domain is processing" - Wait for domain to be active
- "Invalid ARN format" - Check ARN format
- "Role not found" - Verify role exists in same account
- "Permission denied" - Check IAM permissions

---

## Alternative Solution: Use OpenSearch API Directly

If console continues to fail, we can configure role mappings without changing the master user type first, or use a different approach.

### Option: Keep Master User as Username/Password, Use Role Mappings

**Alternative approach** (if changing master user fails):
1. Keep master user as username/password for now
2. Configure role mappings to allow Lambda roles
3. Lambda still uses IAM authentication
4. OpenSearch maps IAM roles to internal roles

This might be easier and still works for Lambda access.

---

## Getting Help

**Check CloudWatch Logs**:
- OpenSearch domain logs (if enabled)
- Look for configuration change errors

**Check AWS Service Health**:
- AWS Service Health Dashboard
- OpenSearch Service status

**AWS Support**:
- If issue persists, contact AWS Support
- Provide domain name and ARN you're trying to set
- Include any error messages from browser console

---

## Quick Fix Script

Run this to get all the information you need:

```bash
./scripts/setup-opensearch-iam-auth.sh
```

This will output:
- Exact ARN to use
- Current domain configuration
- Step-by-step instructions

---

## Expected Behavior

**Success**:
1. Click "Save changes"
2. Console shows "Update in progress"
3. Domain status changes to "Processing"
4. Wait 5-10 minutes
5. Domain status returns to "Active"
6. Configuration shows IAM ARN as master user

**Failure Signs**:
- Field resets to blank immediately
- No "Update in progress" message
- Error message appears
- Browser console shows JavaScript errors

---

## Next Steps

1. **Verify domain is Active** (not Processing)
2. **Get exact ARN** from script
3. **Try saving again** with exact ARN
4. **Check browser console** for errors
5. **If still failing**: Consider alternative approach (role mappings without changing master user type)

