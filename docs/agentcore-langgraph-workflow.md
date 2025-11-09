# AgentCore LangGraph Workflow

This document captures the design and behaviour of the AgentCore handler now shipped in `lambda/agent-workflow/handler.py`. The implementation satisfies the architectural recommendations outlined in `docs/Recommendations on Operator Assistant Chatbot.md`.

## Overview

- **Pipeline Framework:** LangGraph `StateGraph` orchestrating the five recommended nodes: QueryTransformer → DataFetcher → KnowledgeRetriever → ReasoningEngine → ResponseValidator.
- **Primary Reasoner:** Grok API (configurable via `GROK_API_URL` + `GROK_API_KEY`) with Bedrock LLM fallback.
- **Guardrails:** Bedrock `ApplyGuardrail` invoked prior to response delivery, enforcing toxicity, denied-topic, and grounding policies. Responses failing guardrails are suppressed with a safety message.
- **Confidence Management:** Normalised relevance plus telemetry availability determine a blended confidence score. Scores below `MIN_CONFIDENCE_SCORE` append an explicit operator warning.
- **Telemetry Integration:** Optional AgentCore gateway fetch to Amazon Timestream (`DATA_FETCH_ENABLED=true`). Failures are surfaced but non-blocking.
- **Retrieval Enhancements:** Hybrid semantic search (Titan embeddings + BM25) augmented with neighbour-chunk stitching to reconstruct hierarchical context from manual metadata (`chunk_index`, section hints, headings).

## Node Responsibilities

- **QueryTransformer:** Detects turbine model aliases, infers language, and produces an enriched prompt with explicit turbine hints. Metadata is timestamped for downstream auditing.
- **DataFetcher:** Calls the AgentCore gateway (`/timeseries`) with session, turbine, and intent metadata. A feature flag guards environments without telemetry access.
- **KnowledgeRetriever:** Reuses existing OpenSearch helpers but post-processes hits to fetch adjacent chunks via `_mget`, building richer hierarchical context strings and citation payloads.
- **ReasoningEngine:** Packages query, context, telemetry, and citations into the Grok request; if Grok is unreachable, falls back to Bedrock (`LLM_MODEL`, default Nova Pro) through the existing `llm_clients` helper.
- **ResponseValidator:** Applies Bedrock Guardrails, enforces confidence thresholds, and records guardrail outcomes alongside any appended warnings.

## Configuration

Key environment variables:

- `AWS_REGION`, `OPENSEARCH_ENDPOINT`, `OPENSEARCH_INDEX`, `EMBEDDING_MODEL`
- `DATA_FETCH_ENABLED`, `AGENTCORE_GATEWAY_URL`, `AGENTCORE_GATEWAY_API_KEY`
- `GROK_API_URL`, `GROK_API_KEY`, `GROK_TIMEOUT_SECONDS`
- `BEDROCK_GUARDRAIL_ID`, `BEDROCK_GUARDRAIL_VERSION`, `MIN_CONFIDENCE_SCORE`
- `AGENT_MODEL_CONFIG_PATH` (optional): override the location of `agent_model_config.json`
- `AGENT_MODEL_KEY` / `AGENT_SELECTED_MODEL`: choose the active model key at runtime

Dependencies are declared in `lambda/agent-workflow/requirements.txt` (notably `langgraph` and `requests` in addition to the existing packages).

### Model Selection

- Configuration lives in `lambda/agent-workflow/agent_model_config.json`. The default entry points to Nova Pro; alternatives include Grok and Claude 4.5.
- Update `default_model` to change the default or set `AGENT_MODEL_KEY=claude_4_5` (for example) to switch without redeploying.
- The handler automatically falls back to the configured `fallback_model` if the selected model is unavailable (e.g., Grok credentials missing).

## Adoption Notes

- The handler preserves compatibility with the existing event schema; switch by updating the Lambda entry point or aliasing.
- Guardrail evaluation responses and aggregated errors are returned to clients, simplifying observability.
- Telemetry endpoints and Grok credentials must be provisioned before enabling the corresponding features; otherwise, the pipeline logs soft failures and continues.

