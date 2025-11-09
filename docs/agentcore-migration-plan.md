AgentCore Migration Plan
========================

Context
-------

- Current RAG workflow runs in two Lambdas (`document-processor`, `agent-workflow`) orchestrated by LangGraph-lite logic inside the agent Lambda.
- State (sessions, memory) lives in DynamoDB; orchestration, tool calling, and routing are custom code.
- Desired end state leverages **AgentCore** for managed orchestration, memory, tool execution, and native Bedrock integration while preserving existing AWS infrastructure primitives (OpenSearch, S3-based ingestion) where practical.

Goals
-----

1. Replace the bespoke LangGraph runner with an AgentCore agent that owns conversation flow, memory, and tool selection.
2. Preserve current retrieval pipeline (S3 ingest → OpenSearch) while exposing it as an AgentCore tool.
3. Maintain CI/CD deployment path and IAM guardrails; keep secrets out of code.
4. Enable future multi-agent expansions (analytics agent, maintenance agent) by structuring reusable tool + capability definitions.

Key AgentCore Concepts
----------------------

- **Workspace**: logical container for agents, tools, and memory. Needs IAM role with Bedrock + tool access.
- **Agent Definition**: JSON resource describing instructions, tools, routing, fallback LLM, memory configuration.
- **Tools**: REST/Lambda capability definitions AgentCore can invoke. Our initial set:
  - `RetrieveManualChunks` → hits OpenSearch vector index.
  - `InvokeMaintenanceKnowledge` (future) → calls additional APIs or curated knowledge.
  - `TriggerDocumentIngest` (optional admin tool) → kicks off Lambda ingest flow.
- **Memory Store**: AgentCore-provided short-term memory (conversation) and optional long-term store (S3/Dynamo). We can deprecate DynamoDB session table once AgentCore handles memory.

Migration Phases
----------------

### Phase 0 – Foundation (current sprint)

- Create AgentCore workspace via infrastructure (CDK custom resource or manual for POC).
- Provision IAM role (`AgentCoreExecutionRole`) with:
  - Bedrock `InvokeModel`
  - Lambda invoke (for ingest tool)
  - OpenSearch access via existing data-plane policy
  - S3 read for manual links
- Define base agent spec (YAML/JSON in repo) with instructions mirroring current system prompt, referencing Nova Pro.
- Expose OpenSearch retrieval and document metadata formatting as a reusable Lambda tool API.
- Set up API Gateway (or AgentCore-hosted endpoint) to front the agent; ensure CORS alignment with frontend.

### Phase 1 – Dual-Run (safe migration)

- Keep current Lambda workflow running; add feature flag in frontend to toggle between **Lambda** and **AgentCore** backends.
- Route ingestion + retrieval calls through shared modules so both paths reuse the same logic.
- Instrument logging/metrics to compare response fidelity (citations, latency, fallback rate).

### Phase 2 – Cutover

- Remove Lambda orchestration path once AgentCore parity confirmed.
- Update CI/CD to deploy AgentCore artifacts (agent definition, tool registration) using AWS CLI / CloudFormation custom resources.
- Decommission DynamoDB session table if unused; migrate analytics hooks to AgentCore memory export.
- Adjust documentation (`docs/`) and scripts to reference AgentCore invocation paths.

Infrastructure Changes
----------------------

- **CDK Modules**:
  - New stack or nested construct: `AgentCoreStack`
  - Resources: IAM role, secrets (API key if using AgentCore API endpoint), tool Lambda functions (if not already existing), outputs for frontend.
- **GitHub Actions**:
  - Add step to package and deploy AgentCore configuration (likely AWS CLI `bedrock-agent` commands once available, or custom script hitting AWS SDK).
  - Ensure workflow conditionally runs only on `main` but supports manual dispatch for feature branches.
- **Frontend**:
  - API client update to handle AgentCore endpoint schema (likely `/agents/{agentId}/assistants/{assistantId}/sessions/{sessionId}` style) and streaming responses (if adopting SSE).
  - Maintain compatibility fallback for existing Lambda endpoint during dual-run.

Risks & Mitigations
-------------------

- **AgentCore availability / feature gaps**: keep Lambda path until AgentCore proves stable; abstract agent client in frontend.
- **Tool auth complexity**: use IAM roles assumed by AgentCore; avoid API keys inside agent prompts.
- **Deployment complexity**: encapsulate AgentCore config in infrastructure code to avoid manual drift.
- **Latency**: monitor CloudWatch metrics; adjust retrieval tool chunk size or embedding logic if AgentCore introduces additional overhead.

Next Steps
----------

1. Decide on infrastructure approach for creating the AgentCore workspace (CDK custom resource vs. manual provisioning for POC).
2. Spike: build Lambda-backed API that wraps existing OpenSearch retrieval into AgentCore tool contract (input schema, output citations).
3. Author agent definition file (YAML/JSON) and version it in repo.
4. Update frontend service layer to toggle between Lambda and AgentCore endpoints via environment flag.

