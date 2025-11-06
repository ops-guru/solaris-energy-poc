# Fixes for Test Script Errors

**Date**: 2025-11-06  
**Issues Found**: Two critical errors in test script execution

---

## Issues Identified

### Issue 1: Document Processor - Missing Dependencies
**Error**: `"No module named 'opensearchpy'"`

**Root Cause**: 
- CDK's `Code.from_asset()` doesn't automatically install Python dependencies from `requirements.txt`
- Lambda functions were deployed without bundled dependencies

**Fix Applied**:
- Added Docker bundling to CDK Lambda function definitions
- CDK now installs dependencies from `requirements.txt` during deployment
- Uses `BundlingOptions` with Docker to install pip packages

**Code Change**:
```python
code=_lambda.Code.from_asset(
    "../lambda/document-processor",
    bundling=BundlingOptions(
        image=_lambda.Runtime.PYTHON_3_12.bundling_image,
        command=[
            "bash",
            "-c",
            "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output",
        ],
    ),
)
```

### Issue 2: Agent Workflow - Nova Pro API Format Error
**Error**: `"Malformed input request: #: required key [messages] not found"`

**Root Cause**:
- Nova Pro uses `messages` format (like Claude), not `inputText` format (like Titan)
- Code was using incorrect API format

**Fix Applied**:
- Changed from `inputText` format to `messages` format
- Updated request structure to use `messages` array with `role` and `content`
- Changed config from `textGenerationConfig` to `inferenceConfig`
- Updated response parsing to match Nova Pro's response structure

**Code Changes**:
```python
# OLD (incorrect):
body = {
    "inputText": combined_prompt,
    "textGenerationConfig": {
        "maxTokenCount": 2048,
        "temperature": 0.7,
        "topP": 0.9,
    }
}

# NEW (correct):
body = {
    "messages": [
        {
            "role": "system",
            "content": [{"text": system_message}]
        },
        {
            "role": "user",
            "content": [{"text": user_content}]
        }
    ],
    "inferenceConfig": {
        "maxTokens": 2048,
        "temperature": 0.7,
        "topP": 0.9,
    }
}

# Response parsing:
output = response_body.get("output", {})
message = output.get("message", {})
content = message.get("content", [])
text = content[0].get("text", "") if content else ""
```

---

## Files Modified

1. **`lambda/agent-workflow/handler.py`**:
   - Updated `invoke_bedrock_llm()` function to use Nova Pro messages format
   - Changed request structure and response parsing

2. **`infrastructure/solaris_poc/compute_stack.py`**:
   - Added `BundlingOptions` import
   - Added Docker bundling to document processor Lambda
   - Added Docker bundling to agent workflow Lambda

---

## Next Steps

1. **Commit and Push**: These fixes need to be committed and deployed
2. **Redeploy**: CI/CD pipeline will redeploy Lambda functions with:
   - Dependencies properly bundled
   - Correct Nova Pro API format
3. **Re-test**: Run test script again to verify fixes work

---

## Verification

After deployment, test script should:
- ✅ Successfully process documents (dependencies installed)
- ✅ Successfully generate LLM responses (Nova Pro API format correct)
- ✅ Return citations and responses as expected

---

## Notes

- Docker bundling requires Docker to be running during `cdk synth` or `cdk deploy`
- If Docker is not available, consider using Lambda layers or manual bundling
- Nova Pro API format matches Claude's format (messages-based), not Titan's (inputText-based)

