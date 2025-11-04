# Exploring OpenSearch and Bedrock Deployments

This guide helps you explore the OpenSearch Service deployment and work with Bedrock in the AWS Console for the Solaris Energy POC.

## Quick Start Script

If you have AWS CLI configured, you can use the exploration script:

```bash
./scripts/explore-opensearch-bedrock.sh mavenlink-functions
```

This script will:
- Check if OpenSearch domain is deployed
- Display domain details (endpoint, status, VPC config)
- List available Bedrock models
- Test Bedrock model access
- Provide console links and access instructions

## Manual Exploration in AWS Console

### 1. Exploring OpenSearch Service

#### Check if Domain is Deployed

1. Go to [AWS OpenSearch Service Console](https://console.aws.amazon.com/es/home?region=us-east-1)
2. Look for domain: **`solaris-poc-vector-store`**
3. Check the status:
   - ✅ **Active**: Domain is ready
   - ⏳ **Processing**: Still being created (wait 10-20 minutes)
   - ❌ **Not found**: Domain not deployed yet

#### View Domain Details

If the domain exists, click on it to see:

- **Endpoint**: The OpenSearch endpoint URL (e.g., `search-solaris-poc-vector-store-xxxxx.us-east-1.es.amazonaws.com`)
- **Dashboard URL**: Link to OpenSearch Dashboards
- **VPC Configuration**: Which VPC and subnets it's in
- **Security Groups**: Which security groups are attached
- **Access Policy**: Fine-grained access control settings

#### Access OpenSearch Dashboards

1. In the domain details, click **"OpenSearch Dashboards URL"** or **"Dashboard URL"**
2. You'll be prompted for credentials:
   - **Username**: `admin`
   - **Password**: Check one of these sources:
     - CloudFormation stack outputs (if deployed via CDK)
     - Secrets Manager (if configured)
     - Default password from deployment: `TempP@ssw0rd123!Ch@ngeInProd` (check your actual deployment)

#### Explore in Dashboards

Once logged in, you can:

1. **Check Indices**:
   - Go to **Stack Management** → **Index Management**
   - Look for index: `turbine-documents`
   - Check if it has documents (document count)

2. **View Index Mapping**:
   - Click on the `turbine-documents` index
   - Go to **Mappings** tab
   - Verify k-NN vector field exists: `embedding` (dimension 1536)

3. **Search Test**:
   - Go to **Discover** in the left sidebar
   - Select index: `turbine-documents`
   - Try a text search or k-NN search query

4. **Query Data**:
   - Use **Dev Tools** (or **Console**) to run queries:
   ```json
   GET /turbine-documents/_search
   {
     "size": 10,
     "query": {
       "match_all": {}
     }
   }
   ```

#### Domain Configuration Summary

Based on the CDK deployment:

- **Domain Name**: `solaris-poc-vector-store`
- **Version**: OpenSearch 2.11
- **Instance Type**: t3.small.search
- **Nodes**: 1 data node (single AZ for cost optimization)
- **Storage**: 20 GB GP3 EBS volume
- **Encryption**: Enabled (at rest and in transit)
- **Network**: Deployed in VPC private subnets
- **Access**: Fine-grained access control with master user `admin`

### 2. Working with AWS Bedrock

#### Access Bedrock Console

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/home?region=us-east-1)
2. Make sure you're in the correct region: **us-east-1**

#### Check Model Access

1. In the left sidebar, click **"Model access"**
2. Click **"Manage model access"**
3. Check if these models are enabled (check the boxes):
   - ✅ **Claude 3.5 Sonnet** (`anthropic.claude-3-5-sonnet-20241022-v2:0`)
   - ✅ **Amazon Titan Embeddings G1 - Text** (`amazon.titan-embed-text-v1`)

4. If they're not enabled:
   - Select the models you need
   - Click **"Save changes"**
   - Access is usually granted immediately (no approval needed for these models)

#### Test Models in Playground

**Claude 3.5 Sonnet (Chat)**:

1. Go to **"Playgrounds"** → **"Chat"**
2. Select model: `Claude 3.5 Sonnet`
3. Try a test prompt:
   ```
   Hello! Can you help me troubleshoot a gas turbine issue?
   ```
4. Verify the response is generated

**Titan Embeddings (Text)**:

1. Go to **"Playgrounds"** → **"Text"**
2. Select model: `Amazon Titan Embeddings G1 - Text`
3. Enter text: `gas turbine maintenance procedures`
4. Click **"Run"**
5. You should see an embedding vector (array of 1536 numbers)

#### View Model Details

1. Go to **"Foundation models"**
2. Filter by provider: **Anthropic** or **Amazon**
3. Click on a model to see:
   - Model ID
   - Input/output token limits
   - Supported regions
   - Pricing information

### 3. Checking Deployment Status

#### Via CloudFormation

1. Go to [CloudFormation Console](https://console.aws.amazon.com/cloudformation/home?region=us-east-1)
2. Look for stacks:
   - `VectorStoreStack` (OpenSearch domain)
   - `NetworkStack` (VPC, security groups)
   - `ComputeStack` (Lambda functions)
   - `StorageStack` (S3, DynamoDB)

3. Click on `VectorStoreStack` to see:
   - Stack status
   - Outputs (including OpenSearch endpoint)
   - Resources created

#### Get OpenSearch Endpoint via CLI

```bash
# If you have AWS CLI configured
aws cloudformation describe-stacks \
  --stack-name VectorStoreStack \
  --profile mavenlink-functions \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchEndpoint`].OutputValue' \
  --output text
```

#### Check Lambda Functions

1. Go to [Lambda Console](https://console.aws.amazon.com/lambda/home?region=us-east-1)
2. Look for functions:
   - `solaris-poc-document-processor`
   - `solaris-poc-agent-workflow`

3. Check environment variables:
   - `OPENSEARCH_ENDPOINT`: Should point to your OpenSearch domain
   - `OPENSEARCH_MASTER_USER`: `admin`
   - `OPENSEARCH_MASTER_PASSWORD`: [password]
   - `EMBEDDING_MODEL`: `amazon.titan-embed-text-v1`
   - `LLM_MODEL`: `anthropic.claude-3-5-sonnet-20241022-v2:0`

### 4. Testing Integration

#### Test Bedrock Access from Lambda

1. Go to Lambda function: `solaris-poc-document-processor`
2. Create a test event:
   ```json
   {
     "s3_bucket": "solaris-poc-documents-XXXXX-us-east-1",
     "s3_key": "manuals/test.pdf",
     "turbine_model": "SMT60",
     "document_type": "technical-specs"
   }
   ```
3. Run the test and check CloudWatch logs for:
   - Successful Bedrock API calls
   - Embedding generation
   - OpenSearch indexing

#### Test OpenSearch Connection

From a Lambda test or locally with proper VPC access:

```python
import boto3
from opensearchpy import OpenSearch

endpoint = "your-opensearch-endpoint.us-east-1.es.amazonaws.com"
client = OpenSearch(
    hosts=[{'host': endpoint, 'port': 443}],
    http_auth=('admin', 'your-password'),
    use_ssl=True,
    verify_certs=True
)

# Test connection
info = client.info()
print(f"Connected to OpenSearch: {info['version']['number']}")

# Check if index exists
exists = client.indices.exists(index='turbine-documents')
print(f"Index exists: {exists}")
```

### 5. Common Issues & Troubleshooting

#### OpenSearch Domain Not Found

**Cause**: Domain not deployed yet

**Solution**:
```bash
cd infrastructure
export AWS_PROFILE=mavenlink-functions
cdk deploy VectorStoreStack
```

#### Cannot Access OpenSearch Dashboards

**Possible causes**:
1. Domain is still processing (wait 10-20 minutes after creation)
2. Wrong credentials (check CloudFormation outputs)
3. Network/VPC access issues (domain is in private subnet)

**Solution**:
- For VPC deployment, you need network access to the VPC (VPN, bastion host, or VPC endpoint)
- Check security group rules allow access from your IP/network

#### Bedrock Models Not Available

**Cause**: Model access not granted

**Solution**:
1. Go to Bedrock Console → Model access
2. Enable the required models
3. Wait a few seconds for access to propagate

#### "Access Denied" for Bedrock

**Possible causes**:
1. IAM permissions missing
2. Model access not granted
3. Wrong region

**Solution**:
- Check IAM policies include `bedrock:InvokeModel` permission
- Verify model access in Bedrock console
- Ensure you're using `us-east-1` region

### 6. Useful Console Links

- **OpenSearch Service**: https://console.aws.amazon.com/es/home?region=us-east-1
- **Bedrock**: https://console.aws.amazon.com/bedrock/home?region=us-east-1
- **CloudFormation**: https://console.aws.amazon.com/cloudformation/home?region=us-east-1
- **Lambda**: https://console.aws.amazon.com/lambda/home?region=us-east-1
- **VPC**: https://console.aws.amazon.com/vpc/home?region=us-east-1

### 7. Next Steps

After verifying everything is set up:

1. ✅ **OpenSearch**: Domain active, can access Dashboards
2. ✅ **Bedrock**: Models enabled and accessible
3. ✅ **Lambda**: Functions have correct environment variables
4. ✅ **Network**: VPC and security groups configured

You can now:
- Process documents via the document processor Lambda
- Query OpenSearch from the agent workflow Lambda
- Test RAG functionality end-to-end

## Additional Resources

- [OpenSearch Service Documentation](https://docs.aws.amazon.com/opensearch-service/)
- [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/)
- [CDK Infrastructure README](../infrastructure/README.md)
- [Architecture Documentation](./architecture.md)
