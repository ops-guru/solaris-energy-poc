# Solaris Energy Infrastructure - AWS AgentCore POC

AI-powered operator assistant chatbot for turbine troubleshooting, powered by AWS Bedrock AgentCore, LangGraph, and OpenSearch RAG.

## Overview

This POC demonstrates an enterprise-grade operator assistant that provides real-time, context-aware troubleshooting guidance for gas turbines using:
- **AWS Bedrock AgentCore**: Agent orchestration, memory, and tool execution
- **LangGraph**: Multi-step reasoning workflow
- **OpenSearch**: High-precision RAG with hierarchical chunking
- **Bedrock Claude 3.5 Sonnet / Nova Pro**: Multi-LLM support for quality evaluation

## Repository Structure

```
solaris-energy-poc/
├── infrastructure/          # CDK IaC templates
├── lambda/                  # Lambda function code (Python)
├── frontend/                # Next.js web UI
├── manuals/                 # Turbine documentation (13 PDFs)
├── docs/                    # Architecture, deployment guides
├── scripts/                 # Utility scripts
└── tests/                   # Integration and unit tests
```

## Current Status

✅ **Phase 0**: Document acquisition complete (13 PDFs, ~95 MB)  
✅ **Phase 1**: Infrastructure as Code setup complete (Network, Storage, OpenSearch stacks)  
🚧 **Phase 2**: Lambda functions and CI/CD scaffolding in progress  
⏳ **Phase 3-6**: Pending implementation

## Quick Start

### Prerequisites

- AWS CLI configured with credentials
- Python 3.12+
- Node.js 18+ (for frontend)
- AWS CDK CLI

**AWS Profile**: This project uses the `mavenlink-functions` AWS profile (Account: 720119760662)

### Local Development

```bash
# Set up infrastructure
cd infrastructure
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Synthesize CloudFormation templates
cdk synth

# Deploy to AWS (when ready)
# Note: Uses mavenlink-functions profile by default
cdk deploy --all
```

### Document Processing

```bash
# Download turbine manuals
cd scripts
./download_manuals.sh

# Upload to S3 (after infrastructure deployment)
aws s3 sync ../manuals/ s3://<bucket-name>/manuals/
```

## Turbine Models Supported

1. **SMT60** (5.7 MW) - Solar Turbines Taurus 60
2. **SMT130** (16.5 MW) - Solar Turbines Titan 130
3. **TM2500** (35 MW) - GE LM2500+G4

## Architecture

```
User → CloudFront → API Gateway → Lambda → LangGraph Workflow
                                              ↓
                                    AgentCore (Memory, Tools)
                                              ↓
                                    Bedrock LLM + OpenSearch RAG
                                              ↓
                                    Response + Citations
```

For detailed architecture, see [docs/architecture.md](docs/architecture.md)

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [API Specification](docs/api-spec.yaml)
- [IaC Tool Evaluation](docs/iac-tool-evaluation.md)
- [Document Download Summary](docs/document-download-summary.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

Proprietary - Solaris Energy Infrastructure POC

## Contact

For questions or issues, contact the development team.

