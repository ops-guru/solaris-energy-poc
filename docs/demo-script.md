# AgentCore Operator Assistant – Demo & Presentation Script

Use this script to deliver a 20–30 minute client presentation or to record a narrated demo video. The flow assumes you are sharing slides plus live screen segments.

---

## 0. Preparation Checklist

- Deploy the latest build to the demo AWS account; confirm the AgentCore workflow Lambda is pointed at the LangGraph handler.
- Seed the OpenSearch index with recent manuals; verify the document processor has run.
- Set `AGENT_MODEL_KEY` if you plan to highlight Grok or Claude 4.5 during the demo; otherwise the system defaults to Nova Pro.
- Confirm API Gateway URL, Web UI credentials, AgentCore console access, and CloudWatch dashboard URL.
- Open tabs in advance:
  - Web chat UI
  - GitHub repo (docs + `agent_model_config.json`)
  - AgentCore workspace (memory view, container runtime status)
  - Lucidchart (optional) or architecture slides
  - CloudWatch dashboard (AgentCore observability)
  - S3 console folder for manuals (to show ingestion)
  - Lambda CloudWatch Logs for Document Processor

---

## 1. Introduction (2–3 minutes)

**Slide / Talking Points**
- “Solaris Energy Operator Assistant” – purpose: accelerate turbine troubleshooting, surface SOPs, protect safety.
- Stack anchors: AWS-native, AgentCore foundation, multi-model LLM strategy (Nova, Grok, Claude).
- Desired outcomes: consistent guidance, lower MTTR, auditability.

**Script**
> “We built an operator assistant that leverages AgentCore on AWS to deliver grounded, actionable answers for turbine issues. The platform balances fast retrieval of manuals with real-time telemetry and enforces safety guardrails.”

Transition: “Let’s see it in action, then peel back the architecture and engineering.”

---

## 2. Live System Demonstration (8–10 minutes)

### 2.1 Operator Workflow
- Show the chat UI.
- Ask a realistic question (example: “SMT60 turbine oil pressure low — what steps should I take?”).
- Point out:
  - Turbine model auto-detected.
  - Citations with manual pages (click a citation to show presigned S3 link).
  - Confidence score and guardrail note if present.

**Script cues**
> “Notice the response references the exact maintenance section, giving operators confidence. The system highlights the confidence score derived from retrieval quality and telemetry availability.”
> “Behind the scenes, AgentCore’s managed memory keeps the dialogue state—no DynamoDB writes are required for turn-by-turn context.”

### 2.2 Multimodel Toggle (optional)
- Switch environment variable `AGENT_MODEL_KEY` or mention `agent_model_config.json`.
- Run the same query to show slight difference between Nova vs. Grok vs. Claude.

**Script cues**
> “Here I’ve switched to Claude 4.5. The fallback mechanism is automatic; if Grok is unavailable, we revert to Nova without manual intervention.”

### 2.3 Telemetry Fetch (if enabled)
- Trigger a scenario where EventBridge ingests an anomaly or show telemetry overlay in the response.

> “When telemetry is accessible, the workflow fetches it via the AgentCore secure gateway. The reasoning engine fuses that data with SOPs to adjust advice.”

### 2.4 RAG Knowledge Update (Document Ingestion)
- Switch to the S3 console; upload or drag a new SOP PDF into the manuals bucket (use a small sample file).
- Show the Document Processor Lambda log stream capturing:
  - S3 trigger received
  - Hierarchical chunking steps
  - Titan embedding generation
  - OpenSearch index write counts
- Return to OpenSearch (Dev Tools or Dashboard) to confirm new documents/chunks.
- Back in the chat UI, ask a question referencing the newly added content; highlight citations pointing to the fresh document.

**Script cues**
> “Ingesting updated SOPs is this simple—drop the file in S3. The document processor Lambda chunks it, generates embeddings, and pushes them into the OpenSearch vector store with hierarchical metadata. Moments later, the assistant is citing the new material.”

---

## 3. Architecture Deep Dive (6–8 minutes)

### 3.1 Diagram Narrative
- Display the Lucidchart or architecture slide generated from `docs/architecture-diagram-description.md`.
- Walk through sections: Operator Experience → API Gateway → VPC Compute.
- Highlight the LangGraph nodes: QueryTransformer, DataFetcher, KnowledgeRetriever, ReasoningEngine, ResponseValidator.
- Call out the AgentCore runtime container that hosts the workflow and exposes encrypted session memory APIs consumed by the Lambda.

**Script cues**
> “LangGraph keeps the workflow transparent. Each node is observable and independently testable, so we can evolve logic without rewriting the Lambda.”

### 3.2 Data & Model Pathways
- Explain the model selection JSON (`agent_model_config.json`) and guardrails integration.
- Call out OpenSearch hybrid retrieval, neighbor chunk stitching, Titan embeddings.
- Cover S3 + Document Processor pipeline; mention hierarchical metadata.

### 3.3 Deployment Footprint
- Briefly mention VPC layout, IAM isolation, Secrets Manager, DynamoDB for sessions.
- Reference the infrastructure stacks (Network, Storage, VectorStore, Compute, API) from `docs/architecture.md`.

---

## 4. Feature Value Highlights (4–5 minutes)

### 4.1 High-Quality Responses
- Reinforce retrieval accuracy (hierarchical context, citations).
- Safety: guardrail enforcement, confidence thresholds, explicit warnings.

### 4.2 Operational Efficiency
- Repo docs: point to `docs/agentcore-langgraph-workflow.md`, `docs/Recommendations…`.
- Show `agent_model_config.json` for quick runtime tuning.
- CI/CD story: mention CDK stacks, GitHub Actions (describe pipeline steps).
- Memory story: AgentCore-managed memory replaces the old DynamoDB session table, offers encrypted recall, and reduces operational overhead.
- Content pipeline: document ingestion Lambda, S3 triggers, OpenSearch indexing, hierarchical metadata enabling immediate RAG updates.

### 4.3 Flexibility
- Multi-model configuration without redeploy.
- Feature flags for telemetry integration (`DATA_FETCH_ENABLED`).
- Future hooks: EventBridge triggers, additional tools via AgentCore.

**Script cues**
> “The repo captures not just code but the runbook for deployment. A new environment can be stood up by following the documented CDK bootstrap and ingest pipeline scripts.”

---

## 5. Observability Segment (5 minutes)

### 5.1 CloudWatch Dashboards
- Open the CloudWatch dashboard created for AgentCore (mention widgets: Lambda duration/error rate, RAG retrieval metrics, guardrail outcomes).
- Point out logs structured with session IDs, guardrail status, model key, and AgentCore memory usage metrics (cache hits, eviction counts).

**Script cues**
> “We enhanced CloudWatch with guardrail pass/fail metrics and confidence score distributions. Operators can audit every response, including telemetry calls.”

### 5.2 Alerts & Tracing
- Describe planned or configured alarms (e.g., OpenSearch latency, Bedrock errors).
- Mention future integration with AWS X-Ray for tracing LangGraph nodes.
- Note CloudWatch alarms covering Document Processor failures and ingestion latency so the RAG corpus stays fresh.

---

## 6. Closing & Q&A (3 minutes)

- Recap: “Live assistant with grounded guidance, safe responses, easy to deploy.”
- Outline next steps for the client (POC rollout, integration with their data, customization).
- Invite questions on any portion: live demo, architecture, operations.

**Script cues**
> “We’d love to collaborate on aligning this assistant with your specific turbines and playbooks. The modular architecture means we can plug in your telemetry sources and SOPs quickly.”

---

## Appendix – Optional Demo Variations

- **Failover Scenario**: Disable OpenSearch to show graceful degradation and low confidence warning.
- **Guardrail Trigger**: Ask an off-topic or disallowed question to demonstrate response blocking.
- **Document Ingestion**: Upload a manual to S3, run the document processor, highlight new chunks in OpenSearch.
- **CI/CD Walkthrough**: Show GitHub Action logs deploying CDK and Lambda bundles.
- **AgentCore Memory Console**: Open the AgentCore portal to demonstrate per-session memory snapshots and container health.
- **OpenSearch Monitoring**: Display the OpenSearch dashboard showing recent ingestion events and index health.

Use these as live or recorded inserts depending on audience interests.

