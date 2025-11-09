# AgentCore Architecture – Lucidchart AI Prompt

This document provides the detailed textual specification to feed into Lucidchart’s “Describe a diagram” AI so it can generate a high-fidelity AWS architecture diagram for the Solaris Energy Operator Assistant built on AgentCore.

## How to Brief Lucidchart AI

- Start the request with a title (e.g., “Solaris Energy Operator Assistant – AgentCore Architecture”).
- Use container/group keywords so the AI draws swimlanes or nested AWS groups (e.g., “Group: Operator Experience”, “AWS VPC Private Subnet”).
- List shapes with an explicit label, optional icon, and type. For AWS managed services, reference the service name so the correct icon is selected (e.g., “AWS Lambda (Agent Workflow)”).
- Define connections with clear directional verbs: “connects to”, “sends HTTPS request to”, “reads from”.
- Call out conditional/optional paths using notes (e.g., “Optional telemetry fetch when DATA_FETCH_ENABLED=true”).
- Mention data stores with their write/read direction.
- Include annotations for guardrails, confidence scoring, and fallback behaviour so those are represented as callouts.

## Prompt Text for Lucidchart AI

```
Diagram Title: Solaris Energy Operator Assistant – AgentCore Architecture

Group: Operator Experience
  - Shape: External User (Turbine Operator)
    connects to
  - Shape: Web Chat UI (Next.js Frontend)
    note: Hosted in Vercel/AWS Amplify, collects operator questions and displays citations.

Group: Edge / API Layer
  - Shape: Amazon CloudFront (optional, future) connects to Web Chat UI via CDN caching.
  - Shape: Amazon API Gateway (REST, API Keys)
    connects to AWS Lambda (Chat API Handler) over HTTPS.
  - Shape: AWS Lambda (Chat API Handler)
    note: Validates session tokens, persists chat state, forwards requests to Agent Workflow Lambda.

Group: AWS VPC – Private Subnet (Compute)
  - Shape: AWS Lambda (Agent Workflow – LangGraph)
    note: Runs QueryTransformer → DataFetcher → KnowledgeRetriever → ReasoningEngine → ResponseValidator nodes.
  - Shape: AWS Lambda (Document Processor)
    note: Triggered by S3 events; performs PDF extraction, hierarchical chunking, Titan embeddings, writes to OpenSearch.
  - Shape: Amazon EventBridge (Anomaly Bus)
    note: Optional trigger that pushes structured turbine alarms into Agent Workflow.

Connections inside Agent Workflow Lambda:
  - QueryTransformer node detects turbine model, language, enriches prompt metadata.
  - DataFetcher node (conditional) calls AgentCore Secure Gateway → Amazon Timestream (Time-series telemetry) over HTTPS with API key.
  - KnowledgeRetriever node performs hybrid search against Amazon OpenSearch Service (vector + BM25) and stitches neighbor chunks for hierarchical context.
  - ReasoningEngine node selects model via agent_model_config.json:
        Path 1: HTTPS request to Grok API (external SaaS) with context.
        Path 2: AWS Bedrock (Amazon Nova Pro) via InvokeModel.
        Path 3: AWS Bedrock (Anthropic Claude 4.5 Sonnet) via InvokeModel.
    note: Grok is primary when configured; Nova Pro is default; Claude 4.5 available via runtime switch. Responses include citations and telemetry summaries.
  - ResponseValidator node calls AWS Bedrock Guardrails (ApplyGuardrail) and enforces MIN_CONFIDENCE_SCORE threshold before returning output.

Outputs from Agent Workflow Lambda:
  - Sends formatted answer with citations back to Chat API Handler Lambda.
  - Writes session transcript, confidence score, guardrail status to Amazon DynamoDB (ChatSessions table).

Group: AWS VPC – Private Subnet (Data Plane)
  - Shape: Amazon OpenSearch Service (turbine-documents index)
      receives embeddings from Document Processor Lambda.
      serves semantic search results to Agent Workflow Lambda.
  - Shape: Amazon S3 (Turbine Manuals Bucket)
      triggers Document Processor Lambda on new/updated manuals.
  - Shape: Amazon DynamoDB (ChatSessions table)
      stores conversation history, thumbs up/down feedback, guardrail outcomes.
  - Shape: AWS Secrets Manager
      stores API keys (Grok, AgentCore Gateway), OpenSearch credentials, guardrail identifiers.

Group: External / SaaS
  - Shape: Grok Reasoning API (HTTP Endpoint)
      Receives POST from ReasoningEngine node with context and returns draft response.
  - Shape: AgentCore Secure Gateway
      validates signed requests from DataFetcher, proxies to Amazon Timestream, enforces least privilege.

Supporting Services:
  - Shape: AWS CloudWatch (Logs & Metrics) monitors Lambdas, API Gateway, Guardrail outputs.
  - Shape: AWS X-Ray (future) traces Agent Workflow execution.
  - Shape: AWS CodePipeline / GitHub Actions (CI/CD) deploys CDK stacks and Lambda code.

Return Path:
  - Chat API Handler Lambda sends HTTPS response to API Gateway → Web Chat UI → Operator with final answer, citations, confidence score, guardrail status.

Notes:
  - Highlight optional telemetry path and fallback model choice in the diagram.
  - Indicate that EventBridge anomaly events can auto-populate the operator chat with “What’s happening?” prompts.
  - Show that Document Processor keeps OpenSearch index warm with hierarchical chunk metadata to enable neighbor stitching.
```

