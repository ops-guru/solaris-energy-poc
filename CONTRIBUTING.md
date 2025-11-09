# Contributing Guide

Thanks for helping evolve the Solaris Energy operator assistant. This document summarizes the day‑to‑day dev workflow and expectations.

## Environment Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- AWS CLI + access to the target account
- AWS CDK (`npm install -g aws-cdk`)
- Docker (for Lambda bundling)

### Bootstrapping the repo

```bash
git clone https://github.com/ops-guru/solaris-energy-poc.git
cd solaris-energy-poc

# Infrastructure dependencies
cd infrastructure
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Lambda dependencies (for local testing)
cd ../lambda
python3 -m venv .venv && source .venv/bin/activate
pip install -r agent-workflow/requirements.txt

# Frontend
cd ../frontend
npm install
```

## Development Workflow

1. Branch from `main` or the active feature branch (e.g. `LangGraph_implementation`).
2. Implement changes with tests and docs.
3. Run the relevant checks:
   - `pytest` for Lambda units/integration (when added)
   - `npm run lint`, `npm run build` in `frontend/`
   - `./scripts/test-rag-flow.sh` for RAG smoke validation
4. `cdk synth` (and optionally `cdk diff`) before pushing infrastructure changes.
5. Open a pull request and request review.

> **CI/CD**  
> GitHub Actions deploys both `main` and `LangGraph_implementation`. Pushes must be green before merging.

## Coding Standards

### Python
- Black formatting (`black .`)
- Ruff linting (`ruff check .`)
- Type hints required for new functions
- Keep imports sorted (use `ruff --fix` or `isort`)

### TypeScript/React
- ESLint + Prettier (`npm run lint`)
- Functional components + React hooks
- Co-locate component-specific styles

## Testing Expectations

| Layer          | Command                                        | Notes                                |
|---------------|------------------------------------------------|--------------------------------------|
| Lambda units  | `pytest` (per module)                          | Add focused tests for new helpers    |
| Integration   | `./scripts/test-rag-flow.sh`                   | Validates ingestion + agent workflow |
| Frontend      | `npm run lint` / `npm run build`               | Ensure build stays production-ready  |

End-to-end browser tests can be triggered manually or via Playwright (TBD).

## AgentCore + Infrastructure Changes

- CDK changes live under `infrastructure/`. Always run `cdk synth` locally first.
- AgentCore provisioning currently requires CLI/API steps (see README). If you change the agent definition or tool shape, update `docs/agentcore-langgraph-workflow.md` and the `AgentCoreStack`.
- Expose new infrastructure outputs through CDK so the frontend and scripts can consume them without manual edits.

## Documentation

- Keep `README.md` and `docs/` in sync with behaviour changes.
- Major workflow or architecture updates belong in `docs/agentcore-langgraph-workflow.md` or `docs/architecture.md`.
- Remove stale notes as part of your PRs—“docs rot” counts as technical debt.

## Pull Requests

Before requesting review:

- [ ] Code formatted & linted
- [ ] Tests added/updated and passing
- [ ] Docs updated (README, docs/, inline comments)
- [ ] CI is green
- [ ] No secret material committed

Questions or issues? Open a GitHub issue or tag the maintainers in Slack.

