# OpenSearch Serverless vs Provisioned - Migration Guide

## Current Setup: Provisioned OpenSearch

**Current Configuration**:
- Type: Provisioned cluster (OpenSearch Domain)
- Instance: t3.small.search (1 data node)
- Monthly Cost: ~$50 (fixed)
- VPC: Direct VPC deployment
- Access Control: Fine-grained access control with master user

## Recommendation: Switch to Serverless for POC

### Why Serverless is Better for POC

1. **Cost Savings**: 
   - Pay-per-use pricing (~$0.24/OCU-hour)
   - No charges when idle
   - Estimated POC cost: ~$10-20/month vs $50/month fixed

2. **Simplicity**:
   - No capacity planning
   - Automatic scaling
   - Zero maintenance

3. **POC-Friendly**:
   - Perfect for demo scenarios
   - Easy to tear down
   - Lower operational overhead

### Migration Considerations

**CDK Implementation**:
- OpenSearch Serverless requires L1 constructs (`CfnServerlessCollection`)
- VPC integration via VPC endpoints (not direct VPC deployment)
- Access control via data access policies (IAM-based, not fine-grained access control)

**Lambda Changes Needed**:
- Authentication switches from basic auth (username/password) to IAM-based
- Endpoint format changes
- IAM policies for data access

**Estimated Migration Effort**: 2-3 hours

## Migration Option

I can convert the `VectorStoreStack` to use OpenSearch Serverless. This would involve:

1. Replace `opensearch.Domain` with `CfnServerlessCollection`
2. Update Lambda IAM roles to include serverless access policies
3. Modify Lambda environment variables (remove username/password, add IAM auth)
4. Update VPC configuration to use VPC endpoints
5. Update client initialization code in Lambda functions

**Benefits**:
- Lower monthly costs (~60-80% reduction)
- Better suited for POC/demo use
- Automatic scaling
- Easier to manage

**Tradeoffs**:
- Requires IAM-based authentication (slightly different pattern)
- L1 constructs (less CDK-native, but fully supported)
- VPC endpoints instead of direct VPC integration

Would you like me to proceed with converting to OpenSearch Serverless?
