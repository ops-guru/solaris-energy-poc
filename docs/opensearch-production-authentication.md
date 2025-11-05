# OpenSearch Production Authentication Patterns

## Production Scenario

- **Service-to-Service**: Lambda functions → OpenSearch (automated)
- **Human Access**: Operators accessing OpenSearch Dashboards (ad-hoc queries, debugging)
- **Security Requirements**: Compliance, auditability, least privilege
- **User Scale**: 10-20 operators, multiple Lambda functions

## Authentication Options Comparison

### Option 1: IAM-Based Authentication (Service-to-Service)

**Best For**: Lambda functions, EC2 instances, ECS tasks, EKS pods

**How It Works**:
- Services use IAM roles (no passwords)
- OpenSearch checks IAM credentials via AWS SigV4 signing
- Fine-grained access control (FGAC) maps IAM roles to OpenSearch roles

**Pros**:
- ✅ **No password management** (credentials rotate automatically)
- ✅ **Strong security** (IAM policies, no secrets in environment variables)
- ✅ **Audit trail** (CloudTrail logs all access)
- ✅ **Least privilege** (IAM policies control access)
- ✅ **Production standard** (recommended by AWS)

**Cons**:
- ❌ **Not for human users** (Dashboards don't support IAM auth directly)
- ❌ **More complex setup** (requires FGAC role mappings)

**Implementation**:
```python
# Lambda uses IAM role - no password needed
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

credentials = boto3.Session().get_credentials()
aws_auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    'us-east-1',
    'es',
    session_token=credentials.token
)

client = OpenSearch(
    hosts=[{'host': endpoint, 'port': 443}],
    http_auth=aws_auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)
```

### Option 2: Federated Access (SAML/OIDC) + IAM Hybrid

**Best For**: Human users accessing Dashboards, combined with IAM for services

**How It Works**:
- **Humans**: SAML/OIDC → Identity Provider (e.g., AWS SSO, Okta, Azure AD) → OpenSearch Dashboards
- **Services**: IAM roles (as above)
- FGAC maps both SAML groups and IAM roles to OpenSearch roles

**Pros**:
- ✅ **Single Sign-On** for operators (no separate passwords)
- ✅ **Centralized identity management** (manage users in IdP)
- ✅ **IAM for services** (secure, automated)
- ✅ **Audit trail** (both IdP and CloudTrail)
- ✅ **Enterprise standard** (common in large orgs)

**Cons**:
- ❌ **More complex setup** (requires IdP configuration)
- ❌ **IdP dependency** (need Identity Provider)
- ❌ **Additional cost** (IdP service)

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                    Authentication Flow                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Operators (Human Users)                                      │
│      ↓                                                         │
│  [AWS SSO / Okta / Azure AD]                                 │
│      ↓ (SAML/OIDC)                                            │
│  [OpenSearch Dashboards]                                      │
│      ↓ (FGAC Role Mapping)                                    │
│  [OpenSearch Domain]                                          │
│                                                               │
│  Lambda Functions (Services)                                  │
│      ↓                                                         │
│  [IAM Role]                                                   │
│      ↓ (AWS SigV4)                                            │
│  [OpenSearch Domain]                                          │
│      ↓ (FGAC Role Mapping)                                    │
│  [OpenSearch Domain]                                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Option 3: Fine-Grained Access Control (Internal Users)

**Best For**: POC, small teams, simple deployments

**How It Works**:
- Username/password stored in OpenSearch
- FGAC maps users to roles
- Works for both humans and services

**Pros**:
- ✅ **Simple setup** (no external dependencies)
- ✅ **Works immediately** (what we're using now)
- ✅ **No additional services** (self-contained)

**Cons**:
- ❌ **Password management** (credentials in environment variables or secrets)
- ❌ **Manual user management** (create/update users manually)
- ❌ **Less secure** (passwords can be compromised)
- ❌ **Not enterprise standard** (scales poorly)

## Production Recommendation: **Hybrid Approach (IAM + Federated)**

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Production Authentication                   │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Service Access (Automated)                                    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Lambda Functions → IAM Roles → OpenSearch            │    │
│  │ • Document Processor                                  │    │
│  │ • Agent Workflow                                      │    │
│  │ • No passwords, auto-rotating credentials             │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                │
│  Human Access (Operators)                                      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Operators → AWS SSO/SAML → OpenSearch Dashboards    │    │
│  │ • Troubleshooting queries                            │    │
│  │ • Debugging RAG results                              │    │
│  │ • Single sign-on, centralized management             │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Implementation Strategy

#### Phase 1: IAM for Services (Immediate)

**Priority**: High (Security, Compliance)

1. **Update Lambda Functions**:
   - Remove password from environment variables
   - Use IAM role credentials (AWS4Auth)
   - Update OpenSearch client initialization

2. **Configure OpenSearch FGAC**:
   - Create OpenSearch roles for Lambda functions
   - Map IAM roles to OpenSearch roles
   - Set appropriate permissions (read/write indexes)

3. **Benefits**:
   - Eliminates password exposure
   - Automatic credential rotation
   - Better audit trail

#### Phase 2: Federated Access for Users (Future)

**Priority**: Medium (User Experience)

1. **Set up Identity Provider**:
   - AWS SSO (easiest, if already using AWS Organizations)
   - Or Okta/Azure AD (if already in use)

2. **Configure SAML/OIDC in OpenSearch**:
   - Enable SAML/OIDC authentication
   - Map IdP groups to OpenSearch roles

3. **Benefits**:
   - Single sign-on for operators
   - Centralized user management
   - Better user experience

## Detailed Comparison

| Aspect | IAM (Services) | Federated (Users) | Internal Users (Current) |
|--------|----------------|-------------------|-------------------------|
| **Security** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Password Management** | ✅ None needed | ✅ Managed by IdP | ❌ Manual |
| **Auditability** | ⭐⭐⭐⭐⭐ (CloudTrail) | ⭐⭐⭐⭐⭐ (IdP + CloudTrail) | ⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Setup Complexity** | Medium | High | Low |
| **Cost** | Free (IAM) | IdP cost | Free |
| **Best For** | Services | Humans | POC/Small teams |

## Migration Path: POC → Production

### Step 1: Immediate (IAM for Services)

**Why**: Eliminates password security risk

**Changes Needed**:
- Update Lambda functions to use IAM authentication
- Configure OpenSearch FGAC role mappings
- Remove passwords from environment variables
- Move to Secrets Manager for any remaining secrets

**Timeline**: 2-4 hours

### Step 2: Short-term (Secrets Manager)

**Why**: Better secret management

**Changes Needed**:
- Store any remaining secrets in AWS Secrets Manager
- Update Lambda to retrieve from Secrets Manager
- Add automatic rotation

**Timeline**: 1-2 hours

### Step 3: Long-term (Federated Access)

**Why**: Better user experience for operators

**Changes Needed**:
- Set up Identity Provider (AWS SSO or external)
- Configure SAML/OIDC in OpenSearch
- Create role mappings for user groups
- Train operators on SSO access

**Timeline**: 4-8 hours (depends on IdP complexity)

## Cost Analysis

### IAM Authentication
- **Cost**: Free (part of AWS IAM)
- **Additional Services**: None needed

### Federated Access
- **AWS SSO**: Free (if using AWS Organizations)
- **External IdP** (Okta/Azure AD): ~$2-8/user/month
- **Cost for 10-20 operators**: $20-160/month

## Compliance Considerations

### IAM + Federated Approach Supports:

- ✅ **SOC 2**: Audit trails, access controls
- ✅ **HIPAA**: Encryption, access logging
- ✅ **GDPR**: Access controls, audit logging
- ✅ **PCI DSS**: Least privilege, monitoring

### Audit Requirements:

- **Service Access**: CloudTrail logs all IAM-based access
- **User Access**: IdP logs + CloudTrail (if using AWS SSO)
- **OpenSearch Access Logs**: Enable in OpenSearch for detailed audit

## Recommendation Summary

**For Production with 10-20 operators:**

✅ **Primary**: IAM-based authentication for Lambda functions  
✅ **Secondary**: Federated access (SAML/OIDC) for operator Dashboards access  
❌ **Avoid**: Internal user database with passwords for services

**Rationale**:
- IAM eliminates password security risks for automated services
- Federated access provides better UX for operators
- Combines security best practices with operational efficiency
- Scales to enterprise requirements

**Next Steps**:
1. Update Lambda functions to use IAM authentication (Phase 1)
2. Plan federated access setup (Phase 2)
3. Document authentication patterns for operations team
