# Architecture Overview

The Solaris Energy operator assistant combines a LangGraph reasoning pipeline, Amazon Bedrock AgentCore, and an OpenSearch-backed knowledge base. The default request path is:

```
User Browser ──▶ Next.js Frontend ──▶ AgentCore Runtime
                                   ▲             │
                                   │             ▼
                         Retrieval Tool (Lambda) ─┬─▶ LangGraph Workflow
                                                 └─▶ OpenSearch Vector Index

Manual PDFs ──▶ S3 ──▶ Document Processor Lambda ──▶ Titan Embeddings ──▶ OpenSearch
```

## Core Components

| Component | Notes |
|-----------|-------|
| **Next.js Frontend** | Chat UI (React + Tailwind) calling the AgentCore agent endpoint directly. |
| **AgentCore Runtime** | Manages the agent, conversation memory, and tool invocation. |
| **Agent Workflow Lambda** | LangGraph pipeline: query transformer → telemetry fetcher → RAG retriever → Grok/Nova reasoner → guardrail validator. |
| **Document Processor Lambda** | Triggered by S3 uploads, extracts PDF text, performs hierarchical chunking, generates Titan embeddings, and indexes OpenSearch. |
| **OpenSearch** | k-NN index (`turbine-documents`) holding turbine manuals with metadata. |
| **Agent Retrieval Tool Lambda** | Exposes the RAG workflow to AgentCore as an action group. |

An API Gateway + Lambda path still exists for legacy clients, but the frontend does not depend on it.

## LangGraph Workflow (Agent Workflow Lambda)

1. **Query Transformer** – normalises turbine aliases, language hints, and produces a structured prompt.
2. **Telemetry Fetcher** – optionally fetches recent telemetry via the AgentCore gateway (feature-flagged).
3. **Knowledge Retriever** – hybrid OpenSearch search with neighbour chunk stitching for richer context.
4. **Reasoning Engine** – Grok API (primary) with Bedrock Nova Pro fallback and shared prompt templates.
5. **Response Validator** – runs Bedrock Guardrails, blends relevance scores, attaches warnings for low confidence.

Details live in [agentcore-langgraph-workflow.md](agentcore-langgraph-workflow.md).

## CDK Stacks

| Stack | Responsibilities |
|-------|------------------|
| **NetworkStack** | VPC, subnets, security groups, VPC endpoints for Bedrock/OpenSearch. |
| **StorageStack** | S3 manual bucket, (legacy) DynamoDB session table. |
| **VectorStoreStack** | OpenSearch domain with k-NN index and IAM access. |
| **ComputeStack** | Document processor Lambda, LangGraph workflow Lambda, AgentCore retrieval tool Lambda. |
| **ApiStack** | API Gateway + Lambda route (legacy compatibility). |
| **AgentCoreStack** | Publishes the agent definition to SSM and surfaces the retrieval Lambda ARN for tool registration. |

## Data Flow Summary

1. **Manual ingestion**  
   Upload PDFs to the `manuals/` prefix. The document processor Lambda extracts text, chunks it hierarchically, stores embeddings, and refreshes the OpenSearch index.

2. **Chat interaction**  
   - Frontend calls the AgentCore agent endpoint.  
   - AgentCore invokes the retrieval tool Lambda (LangGraph workflow).  
   - The workflow retrieves context from OpenSearch, optionally fetches telemetry, reasons with Grok/Bedrock, and returns an answer and citations.  
   - AgentCore manages memory and returns the response to the frontend.

## External Integrations

- **Amazon Bedrock** – Nova Pro fallback LLM, Titan embeddings, Guardrails.
- **Grok API** – primary reasoning model (requires `GROK_API_URL`/`GROK_API_KEY`).
- **AgentCore Gateway** – optional telemetry feed (e.g., Amazon Timestream).

## Observability

- CloudWatch Logs for each Lambda.
- AgentCore telemetry/observability dashboards (when enabled).
- OpenSearch slow/audit logs (optional).

## Reference Docs

- [Agent Workflow Deep Dive](agentcore-langgraph-workflow.md)
- [AgentCore Migration Plan](agentcore-migration-plan.md)
- [Document Ingestion Pipeline](document-ingestion-pipeline.md)
- [Testing the RAG Flow](testing-rag-flow.md)

