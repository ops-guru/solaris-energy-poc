# OpenSearch & Bedrock Exploration Summary

## What We've Set Up

### 1. Exploration Script

Created `scripts/explore-opensearch-bedrock.sh` - A comprehensive script that:

- ✅ Checks if OpenSearch domain is deployed
- ✅ Displays domain configuration details
- ✅ Lists available Bedrock models
- ✅ Tests Bedrock model access
- ✅ Provides console links and access instructions

**Usage**:
```bash
./scripts/explore-opensearch-bedrock.sh mavenlink-functions
```

**Note**: Requires AWS CLI configured with the `mavenlink-functions` profile.

### 2. Documentation Guide

Created `docs/explore-opensearch-bedrock.md` - A detailed guide covering:

- ✅ Step-by-step OpenSearch console exploration
- ✅ Bedrock model access and testing
- ✅ Deployment status checking
- ✅ Troubleshooting common issues
- ✅ Testing integrations

## Quick Access Guide

### OpenSearch Service

**Console Link**: https://console.aws.amazon.com/es/home?region=us-east-1

**Domain Name**: `solaris-poc-vector-store`

**Quick Checks**:
1. Is the domain deployed? → Check console for domain status
2. Access Dashboards → Click "Dashboard URL" in domain details
3. Credentials → Username: `admin`, Password: Check CloudFormation outputs

### AWS Bedrock

**Console Link**: https://console.aws.amazon.com/bedrock/home?region=us-east-1

**Required Models**:
- `anthropic.claude-3-5-sonnet-20241022-v2:0` (Claude 3.5 Sonnet)
- `amazon.titan-embed-text-v1` (Titan Embeddings)

**Quick Steps**:
1. Go to "Model access" → "Manage model access"
2. Enable the models above
3. Test in Playgrounds (Chat or Text)

## Current Deployment Status

Based on the CDK infrastructure:

### ✅ Configured (Code Ready)

- **OpenSearch Domain**: `solaris-poc-vector-store`
  - Version: OpenSearch 2.11
  - Instance: t3.small.search (1 node)
  - Storage: 20 GB GP3
  - VPC deployment in private subnets
  - Fine-grained access control enabled

- **Bedrock Integration**:
  - VPC endpoint configured for Bedrock
  - Lambda functions have Bedrock permissions
  - Models specified: Claude 3.5 Sonnet, Titan Embeddings

### ⚠️ To Verify

1. **Domain Deployment**: Check if `VectorStoreStack` is deployed
2. **Model Access**: Verify Bedrock models are enabled
3. **Network Access**: Ensure you can reach OpenSearch (VPC access)

## Next Steps

1. **Run the Exploration Script**:
   ```bash
   cd /path/to/solaris-energy-poc
   ./scripts/explore-opensearch-bedrock.sh mavenlink-functions
   ```

2. **Or Use Console**:
   - Follow the guide in `docs/explore-opensearch-bedrock.md`
   - Check OpenSearch domain status
   - Enable Bedrock models if needed

3. **If Not Deployed**:
   ```bash
   cd infrastructure
   export AWS_PROFILE=mavenlink-functions
   cdk deploy VectorStoreStack
   ```

## What You Can Do

Once OpenSearch and Bedrock are accessible:

### In OpenSearch Dashboards:
- ✅ View existing indices (e.g., `turbine-documents`)
- ✅ Run search queries (text and k-NN vector search)
- ✅ Inspect index mappings
- ✅ Monitor cluster health

### In Bedrock Console:
- ✅ Test Claude 3.5 Sonnet in Chat Playground
- ✅ Generate embeddings with Titan in Text Playground
- ✅ View model details and pricing
- ✅ Manage model access

### Integration Testing:
- ✅ Test document processing Lambda → OpenSearch indexing
- ✅ Test agent workflow Lambda → Bedrock → OpenSearch RAG
- ✅ Verify end-to-end document search functionality

## Files Created

1. `scripts/explore-opensearch-bedrock.sh` - Automated exploration script
2. `docs/explore-opensearch-bedrock.md` - Detailed console guide
3. `docs/exploration-summary.md` - This summary document

## Need Help?

- **Script Issues**: Check AWS CLI configuration and credentials
- **Console Access**: See troubleshooting in `docs/explore-opensearch-bedrock.md`
- **Deployment**: Check `infrastructure/README.md` for CDK deployment guide
