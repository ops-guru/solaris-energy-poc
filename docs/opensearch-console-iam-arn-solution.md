# OpenSearch Console IAM ARN Field Reset - Solution

**Issue**: IAM ARN field resets to blank when editing in AWS Console.

**Status**: Domain shows `InternalUserDatabaseEnabled: false`, which suggests IAM might already be configured.

---

## Key Insight

The domain configuration shows `InternalUserDatabaseEnabled: false`, which **typically means IAM authentication is already configured**. The console UI might just have a display bug.

---

## Solution: Test if IAM is Already Working

Since we can't easily test from your local machine (VPC domain), let's test using the Lambda function itself:

### Option 1: Test via Lambda (Recommended)

The Lambda functions are in the VPC and can access OpenSearch. Let's test if IAM authentication is working:

```bash
# This will test if the document processor can access OpenSearch
aws lambda invoke \
  --function-name solaris-poc-document-processor \
  --payload '{
    "s3_bucket": "solaris-poc-documents-720119760662-us-east-1",
    "s3_key": "manuals/Solaris_SMT60_Technical_Specs.pdf",
    "turbine_model": "SMT60",
    "document_type": "technical-specs"
  }' \
  --cli-binary-format raw-in-base64-out \
  --profile mavenlink-functions \
  /tmp/test-output.json

# Check the response
cat /tmp/test-output.json | jq '.'

# Check CloudWatch logs for OpenSearch access
aws logs tail /aws/lambda/solaris-poc-document-processor \
  --since 2m \
  --profile mavenlink-functions \
  | grep -i "opensearch\|index\|stored\|403\|401"
```

**If you see**:
- ✅ "Stored X chunks" - IAM is working!
- ❌ "403 Forbidden" - IAM needs to be configured
- ❌ "401 Unauthorized" - Master user needs to be set to IAM ARN

### Option 2: Console Workarounds

If IAM is not configured, try these console workarounds:

#### Workaround A: Manual JavaScript Injection

1. **Open AWS Console** → OpenSearch → Domain
2. **Click "Actions"** → **"Modify domain"**
3. **Scroll to "Fine-grained access control"**
4. **Click "Edit"**
5. **Select "Set IAM ARN as master user"**
6. **Open Browser Developer Tools** (F12)
7. **Go to Console tab**
8. **Run this JavaScript**:
   ```javascript
   // Find the IAM ARN input field and set value
   const inputs = Array.from(document.querySelectorAll('input'));
   const iamInput = inputs.find(input => 
     input.placeholder?.includes('ARN') || 
     input.id?.includes('iam') || 
     input.name?.includes('iam') ||
     input.getAttribute('aria-label')?.includes('IAM ARN')
   );
   if (iamInput) {
     iamInput.value = 'arn:aws:iam::720119760662:role/ComputeStack-DocumentProcessorRole12EFF6D7-bd7GiR8pj4uB';
     iamInput.dispatchEvent(new Event('input', { bubbles: true }));
     iamInput.dispatchEvent(new Event('change', { bubbles: true }));
     console.log('✅ Set IAM ARN:', iamInput.value);
   } else {
     console.log('❌ Could not find IAM ARN input field');
     console.log('Available inputs:', inputs.map(i => ({id: i.id, name: i.name, placeholder: i.placeholder})));
   }
   ```
9. **Verify the field shows the ARN**
10. **Click "Save changes"**

#### Workaround B: Use Browser Extension

Some browser extensions can help with form auto-fill that might work better than manual entry.

#### Workaround C: Try Different Browser

Sometimes browser-specific issues can be resolved by switching browsers:
- Try Chrome
- Try Firefox  
- Try Safari
- Try Edge

---

## Alternative: Use Role Mappings Without Changing Master User

If changing the master user keeps failing, you can use this approach:

### Keep Master User as Username/Password, Use Role Mappings

1. **Master user stays as username/password** (for OpenSearch Dashboards access)
2. **Configure role mappings** to allow Lambda IAM roles to access OpenSearch
3. **Lambda uses IAM authentication** - OpenSearch maps IAM roles to internal roles

**This works because**:
- Fine-grained access control supports **both** IAM users and internal users
- Role mappings can connect IAM roles to OpenSearch roles
- Lambda authenticates with IAM, OpenSearch grants permissions via role mapping

**Steps**:
1. Access OpenSearch Dashboards (using username/password master user)
2. Go to Security → Role Mappings
3. Map Lambda IAM role ARNs to OpenSearch roles with permissions

This is actually a common production pattern!

---

## Recommended Next Steps

1. **Test if IAM is already working**:
   ```bash
   # Invoke document processor and check logs
   aws lambda invoke \
     --function-name solaris-poc-document-processor \
     --payload '{"s3_bucket":"solaris-poc-documents-720119760662-us-east-1","s3_key":"manuals/Solaris_SMT60_Technical_Specs.pdf","turbine_model":"SMT60","document_type":"technical-specs"}' \
     --cli-binary-format raw-in-base64-out \
     --profile mavenlink-functions \
     /tmp/test.json && \
   aws logs tail /aws/lambda/solaris-poc-document-processor --since 2m --profile mavenlink-functions | grep -i "403\|401\|stored\|index"
   ```

2. **If 403/401 errors**: IAM not configured - try console workarounds
3. **If "Stored X chunks"**: IAM is working! Just need role mappings

---

## Console Field Reset - Likely Causes

1. **JavaScript validation error** - Field clears on validation failure
2. **Form state management bug** - Console UI bug
3. **Network request failing** - API call fails silently
4. **Domain in processing state** - Can't accept changes
5. **Permission issue** - User doesn't have permission to modify

**Check Browser Console** (F12 → Console tab) for errors when you try to save.

---

The key is to **test if IAM is already working via Lambda** - that's the real test, not what the console shows!

