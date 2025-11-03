# Infrastructure as Code - AWS CDK

This directory contains the AWS CDK infrastructure definitions for the Solaris Energy POC.

## Stack Architecture

```
app.py
├── NetworkStack          # VPC, subnets, security groups
├── StorageStack          # S3, DynamoDB
├── VectorStoreStack      # OpenSearch for RAG
├── ComputeStack          # Lambda functions
├── BedrockStack          # AgentCore, Guardrails
├── ApiStack              # API Gateway
└── ObservabilityStack    # CloudWatch dashboards, alarms
```

## Prerequisites

- Python 3.12+
- AWS CLI configured
- CDK CLI: `npm install -g aws-cdk`
- AWS_PROFILE set or credentials configured

**Note**: This project uses the `mavenlink-functions` AWS profile by default.  
To use a different profile, set `export AWS_PROFILE=<your-profile>` before running CDK commands.

## Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap aws://ACCOUNT-NUMBER/REGION

# Synthesize CloudFormation
cdk synth

# View diff
cdk diff

# Deploy all stacks
cdk deploy --all

# Deploy specific stack
cdk deploy NetworkStack
```

## Development

```bash
# Watch mode (auto-synthesize on change)
cdk watch

# List all stacks
cdk list

# Destroy all stacks
cdk destroy --all
```

## Stack Dependencies

Stack deployment order is automatically handled by CDK:
1. NetworkStack (foundation)
2. StorageStack → NetworkStack
3. VectorStoreStack → NetworkStack
4. ComputeStack → NetworkStack, StorageStack
5. BedrockStack
6. ApiStack → ComputeStack
7. ObservabilityStack → All stacks

## Configuration

Environment-specific configuration via CDK context in `cdk.json`:

```json
{
  "context": {
    "environment": "poc",
    "region": "us-east-1"
  }
}
```

Or via environment variables:
```bash
export CDK_DEFAULT_ACCOUNT=123456789012
export CDK_DEFAULT_REGION=us-east-1
```

## Troubleshooting

### Bootstrap Issues
```bash
cdk bootstrap --trust <account-id>
```

### VPC Not Found
Ensure NetworkStack is deployed before dependent stacks.

### Lambda Layer Issues
Layers must be deployed before functions that use them.

### AgentCore Resource Not Found
Bedrock resources may require manual setup via AWS Console or CLI.

## Security

- All resources deployed in VPC with security groups
- S3 buckets with versioning and encryption
- DynamoDB with encryption at rest
- Lambda with least-privilege IAM roles
- API Gateway with API keys and rate limiting

## Cost Estimation

**Monthly POC Costs (estimated)**:
- Bedrock (Claude 3.5 Sonnet): ~$50-100
- OpenSearch (t3.small.search): ~$50
- Lambda: ~$5-10
- DynamoDB (on-demand): ~$5
- S3/CloudFront: ~$5
- **Total**: ~$115-170/month

See [../docs/cost-estimate.md](../docs/cost-estimate.md) for details.

## Next Steps

1. ✅ CDK project structure created
2. ⏳ Implement NetworkStack (VPC, subnets)
3. ⏳ Implement StorageStack (S3, DynamoDB)
4. ⏳ Implement VectorStoreStack (OpenSearch)
5. ⏳ Implement ComputeStack (Lambda functions)
6. ⏳ Implement BedrockStack (AgentCore resources)
7. ⏳ Implement ApiStack (API Gateway)
8. ⏳ Implement ObservabilityStack (CloudWatch)

