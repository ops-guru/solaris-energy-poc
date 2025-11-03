# GitHub Actions Workflows

This directory contains CI/CD workflows for the Solaris Energy POC project.

## Workflows

### `deploy.yml` - Main Deployment Pipeline

**Triggers**: Push to `main` branch or manual workflow dispatch

**Jobs**:
1. **deploy-infrastructure**: Deploys CDK stacks to AWS
   - Synth CloudFormation templates
   - Diff changes
   - Deploy all stacks (with approval)
2. **deploy-lambda**: Packages and deploys Lambda functions
   - Zips Lambda code with dependencies
   - Uploads to S3
   - Updates Lambda function code

**Required Secrets**:
- `AWS_ROLE_ARN`: IAM role for GitHub Actions to assume

**Example Setup**:
```bash
# In AWS Console, create IAM role with trust relationship for GitHub OIDC
# Add role ARN to GitHub repository secrets
gh secret set AWS_ROLE_ARN --body "arn:aws:iam::ACCOUNT:role/GitHubActionsRole"
```

### `pr-validation.yml` - Pull Request Checks

**Triggers**: All pull requests to `main`

**Jobs**:
1. **lint-infrastructure**: Lint and validate CDK code
   - Python linting with ruff
   - Code formatting check with black
   - CDK synthesis validation
2. **validate-documentation**: Ensure required docs are present

**Expected Duration**: ~2-3 minutes

## Setup Instructions

### Prerequisites

1. **GitHub Repository**: Code pushed to GitHub
2. **AWS Account**: AWS account with CDK bootstrap
3. **IAM Role**: Role for GitHub Actions

### Create IAM Role for GitHub Actions

```bash
# 1. Create trust policy (trust-github.json)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR-ORG/solaris-energy-poc:*"
        }
      }
    }
  ]
}

# 2. Create role
aws iam create-role \
  --role-name GitHubActionsDeploymentRole \
  --assume-role-policy-document file://trust-github.json

# 3. Attach policies (or create custom policy with least privileges)
aws iam attach-role-policy \
  --role-name GitHubActionsDeploymentRole \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# 4. Get role ARN
aws iam get-role --role-name GitHubActionsDeploymentRole --query 'Role.Arn'
```

### Configure GitHub Secrets

```bash
# Using GitHub CLI
gh secret set AWS_ROLE_ARN --body "arn:aws:iam::ACCOUNT:role/GitHubActionsDeploymentRole"

# Or in GitHub UI:
# Settings → Secrets and variables → Actions → New repository secret
```

### Bootstrap CDK in AWS Account

```bash
# First time only, run locally or via GitHub Actions
cd infrastructure
source .venv/bin/activate
cdk bootstrap aws://ACCOUNT-NUMBER/us-east-1
```

## Usage

### Automatic Deployments

- Push to `main` → Triggers deployment pipeline
- PR opened → Triggers validation checks
- Manual dispatch → Can run deployment on demand

### Monitor Workflows

```bash
# View workflow runs
gh run list

# View specific run
gh run view <run-id>

# Watch logs in real-time
gh run watch
```

## Troubleshooting

### Deployment Failures

1. Check CloudFormation stack events in AWS Console
2. Review GitHub Actions logs for error details
3. Common issues:
   - IAM permissions too restrictive
   - Region resources unavailable
   - CDK not bootstrapped in account/region

### PR Validation Failures

1. Check linting errors
2. Fix code formatting: `black infrastructure/`
3. Run `cdk synth` locally to reproduce

## Customization

### Different Environments

Create workflow files for different environments:
- `.github/workflows/deploy-dev.yml`
- `.github/workflows/deploy-staging.yml`
- `.github/workflows/deploy-prod.yml`

### Conditional Deployments

Modify `deploy.yml` to use workflow_dispatch inputs:

```yaml
workflow_dispatch:
  inputs:
    environment:
      description: 'Environment to deploy'
      required: true
      type: choice
      options:
        - dev
        - staging
        - prod
```

## Security Best Practices

- ✅ Use OIDC for authentication (no stored AWS credentials)
- ✅ Least-privilege IAM policies
- ✅ GitHub secrets for sensitive values
- ⚠️ Add approval gates for production deployments
- ⚠️ Enable branch protection rules
- ⚠️ Review CloudFormation changes before apply

## Cost Considerations

- GitHub Actions: Free tier is 2000 minutes/month
- Each deployment: ~5-10 minutes
- Estimated: ~50-100 deployments/month before hitting limit

