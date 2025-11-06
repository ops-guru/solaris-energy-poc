# Fix OpenSearch Console IAM ARN Field Reset Issue

**Issue**: IAM ARN field resets to blank when editing in AWS Console, save fails.

---

## Quick Diagnosis

The fact that `InternalUserDatabaseEnabled: false` suggests the domain might already be configured for IAM, but the console isn't showing it. This could be a console UI issue.

---

## Solution Options

### Option 1: Check Current Configuration First

Before trying to change, verify what's currently configured:

```bash
# Get detailed configuration
aws opensearch describe-domain-config \
  --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --region us-east-1 \
  --query 'DomainConfig.AdvancedSecurityOptions.Options' \
  --output json
```

**Look for**:
- `MasterUserOptions` - Should show current master user configuration
- If it shows an IAM ARN, it's already configured!
- If it shows `MasterUserName`, it's still using username/password

### Option 2: Try Browser Workarounds

**Clear Browser State**:
1. **Clear browser cache** for AWS Console
2. **Try incognito/private mode**
3. **Try different browser** (Chrome, Firefox, Safari)
4. **Disable browser extensions** that might interfere

**Console-Specific Steps**:
1. **Refresh the page** before clicking Edit
2. **Don't click Edit multiple times** - wait for page to fully load
3. **Type ARN slowly** - sometimes paste doesn't work, try typing
4. **Copy ARN exactly** - no extra spaces before/after

### Option 3: Use AWS CLI (If Console Fails)

**⚠️ Warning**: This requires updating the entire domain configuration. Proceed carefully.

**Step 1: Get Current Configuration**

```bash
# Export current configuration
aws opensearch describe-domain-config \
  --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --region us-east-1 \
  > /tmp/opensearch-config.json
```

**Step 2: Create Update Configuration**

Create a file with the update (this is complex - see AWS docs for exact format).

**Note**: OpenSearch domain updates via CLI are complex and can cause downtime. This is not recommended unless absolutely necessary.

### Option 4: Check for Existing Configuration

**The domain might already be configured!**

If `InternalUserDatabaseEnabled: false`, the domain is likely already using IAM. The issue might be:
1. **Console UI not showing current value** (display bug)
2. **Role mappings not configured** (need to set up in OpenSearch Dashboards)
3. **Master user ARN is set, but wrong role** (need to verify)

**Test if IAM is working**:
```bash
./scripts/test-opensearch-iam-access.sh
```

If the test passes, IAM is already configured and working - you just need to set up role mappings!

### Option 5: Alternative Approach - Use Role Mappings Without Changing Master User

**If changing master user keeps failing**, try this:

1. **Keep master user as username/password** for now
2. **Configure role mappings** to allow Lambda IAM roles
3. **Lambda still uses IAM authentication**
4. **OpenSearch maps IAM roles to internal roles**

This approach:
- ✅ Lambda uses IAM (no passwords)
- ✅ Master user can still be username/password (for Dashboards access)
- ✅ Role mappings connect IAM roles to OpenSearch permissions
- ✅ Easier to configure (less console issues)

---

## Step-by-Step: Console Fix Attempt

### Exact Steps (Try These in Order)

1. **Verify Domain is Active**:
   ```bash
   aws opensearch describe-domain \
     --domain-name solaris-poc-vector-store \
     --profile mavenlink-functions \
     --query 'DomainStatus.Processing' \
     --output text
   ```
   Must be `False`

2. **Get Exact ARN**:
   ```bash
   ./scripts/setup-opensearch-iam-auth.sh
   ```
   Copy the exact ARN shown

3. **In AWS Console**:
   - Go to OpenSearch Service
   - Click domain: `solaris-poc-vector-store`
   - **Wait for page to fully load** (30 seconds)
   - Click **"Actions"** → **"Modify domain"**
   - **Scroll down slowly** to "Fine-grained access control"
   - **DO NOT** uncheck "Enable fine-grained access control" checkbox
   - Click **"Edit"** (not "Enable")
   - **Wait 2-3 seconds** for form to load
   - Select **"Set IAM ARN as master user"** radio button
   - **Clear the field** if it has placeholder text
   - **Type the ARN** (don't paste - type it):
     ```
     arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole12EFF6D7-bd7GiR8pj4uB
     ```
   - **Verify it's still there** (don't click away)
   - **Scroll to bottom** of page
   - Click **"Save changes"**
   - **Wait for confirmation** message

4. **Check for Errors**:
   - Look for red error messages
   - Check browser console (F12 → Console tab)
   - Check Network tab for failed API calls

---

## If Console Still Fails

### Workaround: Test Current Configuration

Even if the console shows blank, the domain might already be configured:

```bash
# Test if IAM authentication is already working
./scripts/test-opensearch-iam-access.sh
```

**If test passes**: IAM is configured! Just need role mappings.

**If test fails**: Need to configure IAM authentication.

### Alternative: Contact AWS Support

If the console consistently fails:
1. **Open AWS Support case**
2. **Provide**:
   - Domain name: `solaris-poc-vector-store`
   - Region: `us-east-1`
   - Issue: "Cannot set IAM ARN as master user - field resets to blank"
   - ARN attempting to set: `arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole12EFF6D7-bd7GiR8pj4uB`
   - Screenshot of console
   - Browser console errors (if any)

---

## Immediate Next Step

**Test if IAM is already working**:

```bash
./scripts/test-opensearch-iam-access.sh
```

This will tell us if:
- ✅ IAM authentication is already configured and working
- ❌ IAM authentication needs to be configured
- ⚠️  Role mappings need to be set up

**Based on the test results**, we can determine the next steps.

---

## Summary

**The console field resetting is likely a UI bug**. Try:

1. ✅ **Test current configuration** - IAM might already be working
2. ✅ **Browser workarounds** - Clear cache, try different browser
3. ✅ **Type ARN instead of paste** - Sometimes paste doesn't work
4. ✅ **Check browser console** - Look for JavaScript errors
5. ✅ **Verify domain is Active** - Not Processing

If all else fails, we can proceed with role mappings assuming IAM is configured, or contact AWS Support.

