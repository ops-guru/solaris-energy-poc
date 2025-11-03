# IaC Tool Evaluation for AWS Bedrock AgentCore POC

**Date**: 2025-10-31  
**Purpose**: Select optimal Infrastructure as Code tool for deploying AWS AgentCore POC

## Tools Evaluated

### 1. AWS CloudFormation
**Pros:**
- Native AWS service, best integration
- Declarative YAML/JSON format
- Robust resource coverage for standard AWS services
- Built-in change sets and drift detection

**Cons:**
- Limited support for new services (like Bedrock AgentCore) may require WaitConditions
- Verbose YAML can be hard to maintain
- No programming constructs (loops, conditionals limited)

**AgentCore Support**: Potentially limited as AgentCore is a newer service

### 2. AWS CDK (Cloud Development Kit)
**Pros:**
- **Python support** (matches our Lambda functions)
- Object-oriented abstractions, reusable constructs
- Type safety with IDE autocomplete
- Can generate CloudFormation under the hood
- Active development and community
- L1, L2, L3 constructs for various abstraction levels

**Cons:**
- Requires compilation step
- Larger learning curve than CloudFormation
- May need to implement custom constructs for AgentCore if no L2 available

**AgentCore Support**: May require custom L1 constructs or CDK extensions

### 3. Terraform
**Pros:**
- Huge ecosystem with community modules
- State management is explicit
- Multi-cloud capability (not needed here)
- Mature AWS provider with good resource coverage

**Cons:**
- HCL syntax takes getting used to
- State file management complexity
- Add-on Python support via `terragrunt` but adds complexity
- AWS provider may lag behind new services

**AgentCore Support**: Depends on AWS provider version, may require `awscc` provider for latest features

## Decision Matrix

| Criteria | Weight | CloudFormation | CDK (Python) | Terraform |
|----------|--------|----------------|--------------|-----------|
| Python Integration | 25% | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| AgentCore Support | 30% | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Developer Experience | 20% | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| AWS Integration | 15% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Learning Curve | 10% | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

## Decision

**Selected**: **AWS CDK (Python)**

### Rationale

1. **Python Consistency**: All Lambda functions will be in Python, so maintaining IaC in Python keeps the codebase unified
2. **Extensibility**: Can create custom constructs for AgentCore if native L2 not available
3. **Modern Tooling**: Better IDE support, type checking, autocomplete
4. **Flexibility**: Can fall back to raw CloudFormation for any unsupported resources
5. **Team Familiarity**: Likely more familiar to Python developers than HCL or verbose YAML

### Mitigation Strategies

**If AgentCore has limited CDK support:**
1. Use L1 constructs (raw CloudFormation resources) wrapped in Python classes
2. Implement custom constructs for AgentCore-specific resources
3. Use `aws-sam-cli` or `cdklocal` for testing
4. Document manual steps for any AgentCore resources not yet in CDK

**Backup Plan**: 
- Start with CDK for majority of infrastructure (VPC, Lambda, OpenSearch, etc.)
- Use CloudFormation or AWS CLI scripts for AgentCore-specific resources
- Gradually move to full CDK as support improves

## Implementation Approach

### CDK Stack Structure

```
infrastructure/
├── app.py                  # CDK app entry point
├── solaris_poc/
│   ├── __init__.py
│   ├── network_stack.py    # VPC, subnets, security groups
│   ├── storage_stack.py    # S3, DynamoDB
│   ├── compute_stack.py    # Lambda functions
│   ├── vector_store_stack.py  # OpenSearch
│   ├── bedrock_stack.py    # AgentCore, Guardrails
│   ├── api_stack.py        # API Gateway
│   └── observability_stack.py  # CloudWatch, dashboards
├── cdk.json               # CDK configuration
├── requirements.txt       # CDK dependencies
└── README.md             # Deployment instructions
```

### Dependencies

```requirements.txt
aws-cdk-lib>=2.150.0
constructs>=10.0.0,<11.0.0
```

## Next Steps

1. ✅ Initialize CDK project structure
2. Create network stack (VPC, subnets)
3. Create storage stack (S3, DynamoDB)
4. Create vector store stack (OpenSearch)
5. Create compute stack (Lambda)
6. Create bedrock stack (AgentCore resources)
7. Create API stack (API Gateway)
8. Create observability stack (CloudWatch)
9. Implement GitHub Actions workflow
10. Document deployment process

---

**Recommendation**: Proceed with AWS CDK (Python) for IaC implementation

