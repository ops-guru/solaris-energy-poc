# Frontend Setup Guide

This guide explains how to configure the Next.js frontend to connect to the deployed API Gateway.

## Getting the API Gateway URL

After deploying the infrastructure with CDK, you can get the API Gateway URL in several ways:

### Option 1: From CDK Outputs (Recommended)

After deploying the ApiStack, CDK will display the output:

```bash
cd infrastructure
export AWS_PROFILE=mavenlink-functions  # or your profile
cdk deploy ApiStack

# Look for output like:
# ApiStack.ApiUrl = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
```

### Option 2: From AWS Console

1. Go to AWS Console → API Gateway
2. Find the API named "Solaris POC API"
3. Click on it → Stages → `prod`
4. Copy the "Invoke URL" (format: `https://{api-id}.execute-api.{region}.amazonaws.com/prod`)

### Option 3: Using AWS CLI

```bash
# List all APIs
aws apigateway get-rest-apis --profile mavenlink-functions

# Get the API ID, then get the URL
API_ID=your-api-id-here
REGION=us-east-1  # or your region

echo "https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod"
```

### Option 4: From CloudFormation Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name ApiStack \
  --profile mavenlink-functions \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

## Setting the Environment Variable

Once you have the API URL, create or update `.env.local` in the `frontend/` directory:

```bash
cd frontend
cp .env.local.example .env.local
```

Then edit `.env.local`:

```env
# API Gateway endpoint URL
NEXT_PUBLIC_API_URL=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod

# API Key (optional, but recommended)
# Get this from AWS Console → API Gateway → API Keys
# Or from CDK outputs: ApiStack.ApiKeyId
NEXT_PUBLIC_API_KEY=your-api-key-value-here
```

## Getting the API Key

The API Gateway is configured with API key authentication. To get the API key value:

### Option 1: From AWS Console

1. Go to AWS Console → API Gateway
2. Click "API Keys" in the left menu
3. Find the key named "solaris-poc-api-key"
4. Click on it → Show API key

### Option 2: Using AWS CLI

```bash
# List API keys
aws apigateway get-api-keys --profile mavenlink-functions

# Get the key ID from CDK output: ApiStack.ApiKeyId
# Then get the key value
KEY_ID=your-key-id-here
aws apigateway get-api-key \
  --api-key $KEY_ID \
  --include-value \
  --profile mavenlink-functions \
  --query 'value' \
  --output text
```

## Testing the Configuration

1. Start the development server:
```bash
cd frontend
npm run dev
```

2. Open [http://localhost:3000](http://localhost:3000)

3. If configured correctly, you should see the chat interface with a welcome message.

4. If you see "Configuration Required", check:
   - The `.env.local` file exists and has the correct URL
   - The URL format is correct (starts with `https://` and ends with `/prod`)
   - No extra spaces or quotes around the URL

## Format Summary

The API URL format is:
```
https://{api-id}.execute-api.{region}.amazonaws.com/{stage}
```

Where:
- `{api-id}`: Unique API Gateway ID (e.g., `abc123xyz`)
- `{region}`: AWS region (e.g., `us-east-1`)
- `{stage}`: Deployment stage (always `prod` for this POC)

Example:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
```

## Troubleshooting

### "Configuration Required" Error
- Verify `.env.local` exists in the `frontend/` directory
- Check the file has `NEXT_PUBLIC_API_URL` set correctly
- Restart the Next.js dev server after changing `.env.local`

### CORS Errors
- Ensure the API Gateway CORS is configured (already done in ApiStack)
- Check browser console for specific CORS error messages
- Verify the API URL is correct

### 403 Forbidden Errors
- Check that the API key is set correctly in `.env.local`
- Verify the API key is active in AWS Console
- Ensure the usage plan is associated with the API key

### Network Errors
- Verify the infrastructure is deployed: `cdk list`
- Check API Gateway is accessible: `curl https://your-api-url/chat`
- Ensure your network can reach AWS API Gateway endpoints
