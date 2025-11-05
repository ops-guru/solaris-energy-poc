# OpenSearch Version Upgrade Notes

## Upgrade Details

**From**: OpenSearch 2.11  
**To**: OpenSearch 2.19  
**Domain**: `solaris-poc-vector-store`

## Upgrade Process

### Timeline
- **Duration**: Typically 10-30 minutes (depends on domain size)
- **Status Check**: Domain will show "Processing" during upgrade
- **Availability**: Domain remains available during upgrade (rolling upgrade)

### What to Expect

1. **Console Status**: 
   - Domain status will show "Processing" during upgrade
   - Version will show as updating

2. **No Downtime**: 
   - OpenSearch uses rolling upgrade
   - Service remains available

3. **After Upgrade**:
   - Domain status returns to "Active"
   - New version visible in console
   - May need to wait a few minutes for full stabilization

## Checking Upgrade Status

### Via Console
1. Go to [OpenSearch Service Console](https://console.aws.amazon.com/es/home?region=us-east-1)
2. Click on domain: `solaris-poc-vector-store`
3. Check status:
   - "Active" = Upgrade complete
   - "Processing" = Still upgrading

### Via CLI
```bash
aws opensearch describe-domain \
  --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --region us-east-1 \
  --query 'DomainStatus.{Version:Version,Processing:Processing,UpgradeProcessing:UpgradeProcessing}'
```

## Post-Upgrade Steps

After upgrade completes (domain status = "Active"):

1. **Wait 5 minutes** for full stabilization
2. **Reset master password** (if needed) - upgrade might require re-authentication
3. **Test authentication** - Verify Lambda can connect
4. **Re-test document processing** - Trigger Lambda to create index

## Version-Specific Notes

### OpenSearch 2.19 Changes
- Improved security features
- Better performance
- Enhanced k-NN plugin support
- Updated fine-grained access control

### Compatibility
- ✅ All current Lambda functions compatible
- ✅ k-NN vector search unchanged
- ✅ API endpoints unchanged
- ✅ Fine-grained access control unchanged

## Troubleshooting Post-Upgrade

If issues persist after upgrade:

1. **Check domain status** is "Active" (not "Processing")
2. **Verify password** is still set correctly
3. **Test basic connectivity** from Lambda
4. **Check CloudWatch logs** for new error messages

## Next Steps

Once upgrade completes:
1. Verify domain is "Active"
2. Proceed with password reset/troubleshooting (see `opensearch-403-troubleshooting.md`)
3. Test document processor Lambda
4. Verify index creation
