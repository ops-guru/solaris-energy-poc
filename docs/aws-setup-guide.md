# AWS Setup Guide for GitHub Actions Deployment

This guide walks you through setting up AWS authentication for the GitHub Actions deployment pipeline.

## Prerequisites

- AWS CLI configured with admin access
- GitHub repository with Actions enabled
- Repository name: `solaris-energy-poc`
- Organization: `ops-guru`

## Quick Setup (Automated)

For fastest setup, use the provided bootstrap script:

```bash
# Run bootstrap script with your AWS profile and GitHub details
./scripts/bootstrap-aws-github-setup.sh [AWS_PROFILE] [GITHUB_ORG] [GITHUB_REPO]

# Example
./scripts/bootstrap-aws-github-setup.sh mavenlink-functions ops-guru solaris-energy-poc
```

This script automates all steps below. For manual setup, continue reading.

---

## Step 1: Create GitHub OIDC Provider in AWS

First, we need to configure AWS to trust GitHub Actions:

```bash
# Get the GitHub thumbprint
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

**Note**: If the OIDC provider already exists, you'll get an error - that's okay!

## Step 2: Create IAM Role for GitHub Actions

Create a trust policy file:

```bash
cat > /tmp/github-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR-ACCOUNT-ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:ops-guru/solaris-energy-poc:ref:refs/heads/main"
        }
      }
    }
  ]
}
EOF

# Replace YOUR-ACCOUNT-ID with your actual AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
sed -i.bak "s/YOUR-ACCOUNT-ID/$AWS_ACCOUNT_ID/g" /tmp/github-trust-policy.json
```

Create the IAM role:

```bash
aws iam create-role \
  --role-name GitHubActionsSolarisPOC \
  --assume-role-policy-document file:///tmp/github-trust-policy.json

# Attach power user policy (or create a custom limited policy)
aws iam attach-role-policy \
  --role-name GitHubActionsSolarisPOC \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
```

Get the role ARN:

```bash
aws iam get-role --role-name GitHubActionsSolarisPOC --query 'Role.Arn' --output text
```

## Step 3: Configure GitHub Secret

Add the IAM role ARN as a GitHub secret:

```bash
# Using GitHub CLI
gh secret set AWS_ROLE_ARN

# Or via GitHub web UI:
# 1. Go to https://github.com/ops-guru/solaris-energy-poc/settings/secrets/actions
# 2. Click "New repository secret"
# 3. Name: AWS_ROLE_ARN
# 4. Value: arn:aws:iam::ACCOUNT:role/GitHubActionsSolarisPOC
# 5. Click "Add secret"
```

## Step 4: Bootstrap CDK in AWS

Before deployment works, bootstrap CDK in your AWS account:

```bash
# Get your AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Bootstrap CDK
cd infrastructure
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cdk bootstrap aws://$AWS_ACCOUNT_ID/us-east-1
```

## Step 5: Run Deployment

Once the secret is configured, the GitHub Actions workflow will:

1. Assume the IAM role via OIDC
2. Install CDK dependencies
3. Run `cdk synth` to validate
4. Run `cdk deploy --all` to deploy infrastructure

Monitor the deployment:

```bash
gh workflow view deploy.yml
gh run watch
```

## Troubleshooting

### "Credentials could not be loaded"
- **Cause**: GitHub secret `AWS_ROLE_ARN` not configured
- **Fix**: Follow Step 3 above to add the secret

### "Could not assume role"
- **Cause**: IAM role trust policy incorrect or OIDC provider missing
- **Fix**: Re-run Step 1 and Step 2, verify account ID matches

### "Stack already exists"
- **Cause**: Previous deployment attempt
- **Fix**: `cdk destroy --all` or use different stack names

### "Access denied to OpenSearch"
- **Cause**: Fine-grained access control needs manual setup
- **Fix**: Document manual steps for AgentCore resources

## Alternative: Skip GitHub Actions (Local Deployment)

If you prefer to deploy locally instead:

```bash
# Configure AWS credentials locally
aws configure

# Deploy from your machine
cd infrastructure
source .venv/bin/activate
cdk deploy --all
```

## Security Best Practices

✅ **Do**:
- Use OIDC (no stored AWS credentials)
- Least-privilege IAM policies
- Separate roles for different environments
- Enable CloudTrail logging

❌ **Don't**:
- Store AWS credentials in GitHub
- Use admin access for CI/CD
- Share IAM roles across projects
- Skip security reviews

## Next Steps

After successful deployment:
1. Verify infrastructure in AWS Console
2. Process sample documents
3. Test Lambda functions
4. Build agent workflow
5. Deploy API & Frontend

---

**Need Help?** Check the troubleshooting section or review AWS CDK documentation.

