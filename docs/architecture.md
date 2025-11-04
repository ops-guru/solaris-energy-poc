# Solaris Energy Infrastructure POC - Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          OPERATOR INTERFACE                             │
│                                                                         │
│                    ┌──────────────────────────────┐                    │
│                    │    Next.js Web Chat UI       │                    │
│                    │  (React + TypeScript)        │                    │
│                    └──────────────┬───────────────┘                    │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │ HTTPS
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                               │
│                                                                         │
│                    ┌──────────────────────────────┐                  │
│                    │    AWS API Gateway            │                  │
│                    │  - REST API                   │                  │
│                    │  - API Keys Authentication    │                  │
│                    │  - Rate Limiting              │                  │
│                    └──────────────┬───────────────┘                    │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         COMPUTE LAYER (VPC)                             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    Lambda: Agent Workflow                        │ │
│  │                                                                  │ │
│  │  ┌──────────────────────────────────────────────────────────┐   │ │
│  │  │           LangGraph Workflow Engine                      │   │ │
│  │  │                                                           │   │ │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │ │
│  │  │  │   Query      │→│  Knowledge    │→│  Reasoning    │  │   │ │
│  │  │  │ Transformer  │  │  Retriever   │  │  Engine      │  │   │ │
│  │  │  └──────────────┘  └──────┬───────┘  └──────┬───────┘  │   │ │
│  │  │                           │                  │          │   │ │
│  │  │  ┌──────────────┐  ┌──────┴───────┐  ┌──────┴───────┐  │   │ │
│  │  │  │   Response   │←│  Response     │←│  Data         │  │   │ │
│  │  │  │   Validator  │  │  Generator    │  │  Fetcher      │  │   │ │
│  │  │  └──────────────┘  └───────────────┘  └───────────────┘  │   │ │
│  │  └──────────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │              Lambda: Document Processor                          │ │
│  │  - PDF Extraction (pdfplumber)                                  │ │
│  │  - Hierarchical Chunking                                        │ │
│  │  - Embedding Generation (Bedrock Titan)                         │ │
│  │  - OpenSearch Indexing                                          │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │              Lambda: API Handlers                                │ │
│  │  - Chat endpoint handler                                        │ │
│  │  - Session management                                           │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ↓               ↓               ↓
┌───────────────────────────┐  ┌───────────────────────────┐  ┌───────────────────────────┐
│   AI SERVICES (Bedrock)   │  │   VECTOR STORE            │  │   STORAGE LAYER           │
│                           │  │                           │  │                           │
│  ┌─────────────────────┐ │  │  ┌─────────────────────┐  │  │  ┌─────────────────────┐  │
│  │  AgentCore          │ │  │  │  OpenSearch Domain  │  │  │  │  S3 Bucket          │  │
│  │  - Orchestration    │ │  │  │  - k-NN Plugin      │  │  │  │  - Turbine Manuals  │  │
│  │  - Memory           │ │  │  │  - HNSW Index       │  │  │  │  - PDF Documents     │  │
│  │  - Tool Execution   │ │  │  │  - Vector Search    │  │  │  └─────────────────────┘  │
│  └─────────────────────┘ │  │  └─────────────────────┘  │  │                           │
│                           │  │                           │  │  ┌─────────────────────┐  │
│  ┌─────────────────────┐ │  │  ┌─────────────────────┐  │  │  │  DynamoDB Table     │  │
│  │  Claude 3.5 Sonnet  │ │  │  │  Index:             │  │  │  │  - Chat Sessions    │  │
│  │  - Primary LLM      │ │  │  │  turbine-documents  │  │  │  │  - User Feedback    │  │
│  └─────────────────────┘ │  │  └─────────────────────┘  │  │  │  - Config Data      │  │
│                           │  │                           │  │  └─────────────────────┘  │
│  ┌─────────────────────┐ │  │                           │  │                           │
│  │  Amazon Nova Pro    │ │  │                           │  │                           │
│  │  - Alternative LLM  │ │  │                           │  │                           │
│  └─────────────────────┘ │  │                           │  │                           │
│                           │  │                           │  │                           │
│  ┌─────────────────────┐ │  │                           │  │                           │
│  │  Bedrock Titan      │ │  │                           │  │                           │
│  │  - Embeddings       │ │  │                           │  │                           │
│  └─────────────────────┘ │  │                           │  │                           │
│                           │  │                           │  │                           │
│  ┌─────────────────────┐ │  │                           │  │                           │
│  │  Guardrails         │ │  │                           │  │                           │
│  │  - Content Filter   │ │  │                           │  │                           │
│  └─────────────────────┘ │  │                           │  │                           │
└───────────────────────────┘  └───────────────────────────┘  └───────────────────────────┘
```

## Data Flow

### 1. Query Processing Flow

```
Operator Query
    ↓
[Web UI] → Natural language input
    ↓
[API Gateway] → Authentication, rate limiting
    ↓
[Agent Workflow Lambda] → LangGraph orchestration
    ↓
[Query Transformer] → Extract intent, detect turbine model
    ↓
[Knowledge Retriever] → Hybrid RAG search on OpenSearch
    ↓
[Reasoning Engine] → Bedrock LLM with context
    ↓
[Response Validator] → Format, add citations, guardrails check
    ↓
[Response] → Return to operator with source citations
```

### 2. Document Processing Flow

```
PDF Document (S3)
    ↓
[Document Processor Lambda] → Triggered by S3 event
    ↓
[PDF Extraction] → pdfplumber extracts text
    ↓
[Hierarchical Chunking] → Split into semantic chunks
    ↓
[Embedding Generation] → Bedrock Titan creates vectors
    ↓
[OpenSearch Indexing] → Store vectors with metadata
    ↓
[Knowledge Base] → Ready for RAG queries
```

### 3. Session Management Flow

```
Chat Session Start
    ↓
[API Handler] → Create session ID
    ↓
[DynamoDB] → Store session metadata
    ↓
[Agent Workflow] → Maintain conversation context
    ↓
[User Feedback] → Store feedback (thumbs up/down)
    ↓
[DynamoDB] → Update session with feedback
```

## Network Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           VPC (10.0.0.0/16)                             │
│                                                                         │
│  ┌──────────────────────────┐      ┌──────────────────────────┐        │
│  │  Public Subnet (AZ-1)    │      │  Public Subnet (AZ-2)    │        │
│  │  10.0.1.0/24             │      │  10.0.2.0/24             │        │
│  │                          │      │                          │        │
│  │  - NAT Gateway           │      │  - NAT Gateway (POC: 1)  │        │
│  │  - VPC Endpoints         │      │                          │        │
│  └──────────────────────────┘      └──────────────────────────┘        │
│                                                                         │
│  ┌──────────────────────────┐      ┌──────────────────────────┐        │
│  │  Private Subnet (AZ-1)   │      │  Private Subnet (AZ-2)   │        │
│  │  10.0.11.0/24            │      │  10.0.12.0/24            │        │
│  │                          │      │                          │        │
│  │  - Lambda Functions      │      │  - Lambda Functions      │        │
│  │  - OpenSearch Domain     │      │  - (Future: Multi-AZ)     │        │
│  │    (t3.small.search)     │      │                          │        │
│  └──────────────────────────┘      └──────────────────────────┘        │
│                                                                         │
│  Security Groups:                                                      │
│  - Lambda Security Group (egress to OpenSearch)                        │
│  - OpenSearch Security Group (ingress from Lambda)                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Infrastructure Stacks

### Stack Dependencies

```
NetworkStack (Foundation)
    ↓
    ├──→ StorageStack (S3, DynamoDB)
    │
    ├──→ VectorStoreStack (OpenSearch)
    │       ↓
    │       └──→ ComputeStack (Lambda functions)
    │               ↓
    │               └──→ ApiStack (API Gateway)
    │
    └──→ (Future) BedrockStack
    └──→ (Future) ObservabilityStack
```

### Current Implementation Status

- ✅ **NetworkStack**: VPC, subnets, NAT gateway, security groups, VPC endpoints
- ✅ **StorageStack**: S3 buckets, DynamoDB tables
- ✅ **VectorStoreStack**: OpenSearch domain with k-NN
- ✅ **ComputeStack**: Lambda functions (Agent Workflow, Document Processor, API Handlers)
- ✅ **ApiStack**: API Gateway with Lambda integration
- ⏳ **BedrockStack**: AgentCore configuration (pending)
- ⏳ **ObservabilityStack**: CloudWatch dashboards (pending)

## Security Architecture

### Encryption

- **At Rest**: 
  - S3: Server-side encryption (SSE-S3)
  - DynamoDB: Encryption at rest enabled
  - OpenSearch: Encryption at rest enabled

- **In Transit**:
  - HTTPS/TLS for all API communications
  - OpenSearch: Node-to-node encryption enabled
  - VPC endpoints for AWS services

### Access Control

- **Network**: VPC isolation, private subnets for sensitive components
- **IAM**: Least-privilege roles for Lambda functions
- **API**: API Gateway API keys for authentication
- **Content**: Bedrock Guardrails for content filtering

### Monitoring

- **CloudWatch**: Logs, metrics, alarms
- **CloudTrail**: API audit logging
- **X-Ray**: Distributed tracing (future)

## Scalability & Performance

### Current Configuration (POC)

- **OpenSearch**: Single AZ, t3.small.search instance
- **Lambda**: 512 MB memory, 3-minute timeout
- **VPC**: Single NAT gateway (cost-optimized)

### Production Considerations

- **Multi-AZ**: OpenSearch zone awareness
- **Auto Scaling**: Lambda concurrency, OpenSearch scaling
- **Caching**: CloudFront for static assets, API response caching
- **Load Balancing**: Multiple NAT gateways, API Gateway throttling

## Cost Optimization

### POC Monthly Estimate (~$115-170)

- VPC & Networking: ~$50
- S3 Storage: ~$5
- DynamoDB: ~$5
- OpenSearch: ~$50
- Lambda: ~$1
- Bedrock: ~$50-100 (usage-based)

### Cost Reduction Strategies

- Single-AZ deployment for POC
- Minimal NAT gateway usage
- VPC endpoints to reduce NAT costs
- On-demand pricing for DynamoDB
- Reserved capacity for production (future)

## Deployment Architecture

### CI/CD Pipeline

```
GitHub Repository
    ↓
[GitHub Actions] → OIDC Authentication
    ↓
[CDK Synthesis] → Validate templates
    ↓
[AWS Deployment] → cdk deploy --all
    ↓
[Infrastructure] → Stacks deployed in order
    ↓
[Lambda Deployment] → Package and deploy functions
    ↓
[Health Checks] → Validate deployment
```

## Integration Points

### External Systems (Future)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Solaris Pulse Integration                            │
│                                                                         │
│  [Agent Workflow] → Work Order API → [Solaris Pulse]                   │
│                                                                         │
│  Capabilities:                                                          │
│  - Generate work orders from troubleshooting steps                     │
│  - Query maintenance schedules                                         │
│  - Update service records                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Future Enhancements

- **Timestream Integration**: Real-time sensor data for predictive maintenance
- **Grok API**: Alternative LLM provider (when available)
- **Multi-language Support**: Internationalization
- **Mobile App**: Native mobile interface

---

## Component Details

### Lambda Functions

1. **Agent Workflow Lambda**
   - LangGraph workflow orchestration
   - 5-node workflow: Query Transformer → Knowledge Retriever → Reasoning Engine → Response Validator → Data Fetcher
   - Memory: 512 MB - 1 GB
   - Timeout: 3 minutes

2. **Document Processor Lambda**
   - PDF extraction and processing
   - Embedding generation
   - OpenSearch indexing
   - Triggered by S3 events

3. **API Handler Lambda**
   - Chat endpoint handler
   - Session management
   - Request/response formatting

### OpenSearch Configuration

- **Version**: OpenSearch 2.11
- **Instance**: t3.small.search (1 data node)
- **Storage**: 20 GB GP3 EBS volume
- **Index**: `turbine-documents`
- **Features**: k-NN plugin, HNSW algorithm
- **Security**: Fine-grained access control, master user authentication

### Bedrock Models

- **Primary LLM**: Claude 3.5 Sonnet (anthropic.claude-3-5-sonnet-20241022-v2:0)
- **Alternative LLM**: Amazon Nova Pro (future)
- **Embeddings**: Bedrock Titan Embeddings (amazon.titan-embed-text-v1)
- **Guardrails**: Bedrock Guardrails for content filtering

---

*Last Updated: 2025-01-31*
*Architecture Version: 1.0*

