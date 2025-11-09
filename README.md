# Solaris Energy Operator Assistant

Production-ready operator assistant for Solaris Energy field engineers, built on AWS Bedrock AgentCore, LangGraph, and OpenSearch-powered RAG.

## What’s Included

- **LangGraph Agent Workflow** (`lambda/agent-workflow/handler.py`): multi-node pipeline (query transform → telemetry fetch → OpenSearch retrieval → Grok/Bedrock reasoning → guardrail validation).
- **RAG Infrastructure**: document processor Lambda, k-NN OpenSearch index, and hierarchical chunking pipeline.
- **AgentCore Tooling**: retrieval Lambda exposed as an AgentCore action group plus SSM-held agent definition for automated provisioning.
- **Next.js Frontend** (`frontend/`): chat UI that talks directly to the AgentCore runtime.
- **CDK Infrastructure** (`infrastructure/`): VPC, storage, OpenSearch, compute stacks, API Gateway (optional legacy path), and AgentCore configuration stack.

## Repository Layout

```
solaris-energy-poc/
├── infrastructure/            # CDK stacks (network, storage, OpenSearch, compute, AgentCore config)
├── lambda/                    # Lambda sources (document processor, agent workflow, utilities)
├── frontend/                  # Next.js application
├── docs/                      # Design + operational docs
├── scripts/                   # Utility scripts (manual ingestion, tests)
└── manuals/                   # Sample turbine PDFs (sync to S3)
```

## Deploying from Scratch

### 1. Prerequisites

- AWS account with permissions for CDK + Bedrock AgentCore
- AWS CLI configured (the repo uses the `mavenlink-functions` profile in examples)
- Python 3.12+, Node.js 18+, Docker (for Lambda bundling)
- AWS CDK CLI (`npm install -g aws-cdk`)

### 2. Bootstrap & Deploy Infrastructure

```bash
cd infrastructure
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional: cdk synth to inspect templates
cdk deploy --all --profile mavenlink-functions
```

Key outputs:
- `AgentCoreStack.AgentDefinitionParameterName` – SSM parameter containing the agent definition JSON
- `AgentCoreStack.AgentRetrievalToolArn` – Lambda ARN for the retrieval tool
- S3 bucket / OpenSearch endpoint / Lambda ARNs for reference

### 3. Provision the AgentCore Agent

Agent creation currently leverages the AWS CLI (automation via a CDK custom resource is planned). Example:

```bash
AGENT_DEF=$(aws ssm get-parameter \
  --name /solaris/agentcore/agent-definition \
  --query 'Parameter.Value' \
  --output text \
  --profile mavenlink-functions)

aws bedrock-agent create-agent \
  --agent-name "solaris-operator-assistant" \
  --agent-version "1.0.0" \
  --instruction "$(echo "$AGENT_DEF" | jq -r '.instructions')" \
  --foundation-model "$(echo "$AGENT_DEF" | jq -r '.defaultModelId')" \
  --profile mavenlink-functions

AGENT_ID=<returned-agent-id>
TOOL_ARN=$(aws cloudformation describe-stacks \
  --stack-name AgentCoreStack \
  --query "Stacks[0].Outputs[?OutputKey=='AgentRetrievalToolArn'].OutputValue" \
  --output text \
  --profile mavenlink-functions)

aws bedrock-agent create-agent-action-group \
  --agent-id "$AGENT_ID" \
  --action-group-name "RetrieveManualChunks" \
  --action-group-executor "{\"lambda\": {\"lambda\": \"$TOOL_ARN\"}}" \
  --profile mavenlink-functions

aws bedrock-agent prepare-agent --agent-id "$AGENT_ID" --profile mavenlink-functions
```

Record the invocation endpoint returned from `get-agent` (or the console). That URL becomes `NEXT_PUBLIC_AGENTCORE_URL` for the frontend.

### 4. Load Manuals into OpenSearch

```bash
cd scripts
./download_manuals.sh          # optional if PDFs not already in manuals/
aws s3 sync ../manuals/ s3://<documents-bucket>/manuals/
```

The document-processor Lambda will process new uploads automatically (three-level chunking + Titan embeddings).

### 5. Run the Frontend

```bash
cd ../frontend
npm install

cat <<EOF > .env.local
NEXT_PUBLIC_AGENTCORE_URL=https://<agent-endpoint>/invoke
NEXT_PUBLIC_AGENTCORE_API_KEY=<optional-if-agent-enforces-api-key>
EOF

npm run dev
```

Browse to `http://localhost:3000` and chat with the agent.

### 6. Regression Tests

- Lambda + RAG end-to-end smoke test: `./scripts/test-rag-flow.sh`
- Frontend lint/build: `npm run lint` / `npm run build`

## Operational Docs

- [Architecture](docs/architecture.md)
- [Agent Workflow (LangGraph)](docs/agentcore-langgraph-workflow.md)
- [AgentCore Migration Notes](docs/agentcore-migration-plan.md)
- [Document Ingestion Pipeline](docs/document-ingestion-pipeline.md)
- [Testing the RAG Flow](docs/testing-rag-flow.md)
- [AWS Setup Guide](docs/aws-setup-guide.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, testing expectations, and workflow.

## License

Proprietary – Solaris Energy Infrastructure POC. Please contact the project maintainers for usage questions.

