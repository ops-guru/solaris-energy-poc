"""
Next-generation AgentCore workflow handler implementing the full
multi-step architecture described in the operator assistant
recommendations.

This handler leaves the existing implementation untouched and
introduces a LangGraph-powered pipeline with the following nodes:

1. QueryTransformer  – prompt shaping, turbine intent detection,
                       and query enrichment.
2. DataFetcher       – optional AgentCore gateway integration with
                       Timestream (guarded by feature flags).
3. KnowledgeRetriever – hierarchical + semantic retrieval from
                        OpenSearch with neighbor stitching.
4. ReasoningEngine   – Grok primary reasoning (falls back to Bedrock).
5. ResponseValidator – Bedrock Guardrails enforcement and confidence
                       gating prior to returning the response.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict

import boto3
import requests
from langgraph.graph import END, StateGraph

try:
    # Reuse existing helper utilities without modifying them.
    from opensearch_helper import (
        get_opensearch_client,
        search_documents,
    )
except ImportError:  # pragma: no cover - module should exist in Lambda package
    get_opensearch_client = None  # type: ignore
    search_documents = None  # type: ignore

try:
    from llm_clients import get_bedrock_client, invoke_llm
except ImportError:  # pragma: no cover
    get_bedrock_client = None  # type: ignore
    invoke_llm = None  # type: ignore

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Environment Configuration
# ---------------------------------------------------------------------------

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
OPENSEARCH_ENDPOINT = os.environ.get("OPENSEARCH_ENDPOINT", "")
OPENSEARCH_INDEX = os.environ.get("OPENSEARCH_INDEX", "turbine-documents")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "amazon.titan-embed-text-v1")

DATA_FETCH_ENABLED = os.environ.get("DATA_FETCH_ENABLED", "false").lower() == "true"
AGENTCORE_GATEWAY_URL = os.environ.get("AGENTCORE_GATEWAY_URL")
AGENTCORE_GATEWAY_API_KEY = os.environ.get("AGENTCORE_GATEWAY_API_KEY")

GROK_API_URL = os.environ.get("GROK_API_URL")
GROK_API_KEY = os.environ.get("GROK_API_KEY")
GROK_TIMEOUT_SECONDS = int(os.environ.get("GROK_TIMEOUT_SECONDS", "30"))

GUARDRAIL_ID = os.environ.get("BEDROCK_GUARDRAIL_ID")
GUARDRAIL_VERSION = os.environ.get("BEDROCK_GUARDRAIL_VERSION", "1")
MIN_CONFIDENCE_SCORE = float(os.environ.get("MIN_CONFIDENCE_SCORE", "0.75"))

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Requested-With,X-Api-Key",
    "Access-Control-Allow-Methods": "OPTIONS,POST",
}

# Model selection configuration
DEFAULT_MODEL_CONFIG = {
    "default_model": "nova_pro",
    "fallback_model": "nova_pro",
    "models": {
        "nova_pro": {
            "display_name": "Amazon Nova Pro",
            "type": "bedrock",
            "model_id": "amazon.nova-pro-v1:0",
            "inference_config": {
                "max_tokens": 2048,
                "temperature": 0.4,
            },
        },
        "claude_4_5": {
            "display_name": "Anthropic Claude 4.5 Sonnet",
            "type": "bedrock",
            "model_id": "anthropic.claude-4.5-sonnet-20250205-v1:0",
            "inference_config": {
                "max_tokens": 2048,
                "temperature": 0.3,
            },
        },
        "grok": {
            "display_name": "Grok Operator Assistant",
            "type": "grok",
            "requires": ["GROK_API_URL", "GROK_API_KEY"],
        },
    },
}

MODEL_CONFIG_PATH = os.environ.get(
    "AGENT_MODEL_CONFIG_PATH",
    os.path.join(os.path.dirname(__file__), "agent_model_config.json"),
)

def _load_model_config() -> Dict[str, Any]:
    try:
        with open(MODEL_CONFIG_PATH, "r", encoding="utf-8") as config_file:
            loaded = json.load(config_file)
            return loaded
    except FileNotFoundError:
        logger.warning(
            "Model configuration file not found at %s. Using defaults.",
            MODEL_CONFIG_PATH,
        )
    except json.JSONDecodeError as exc:
        logger.error(
            "Invalid JSON in model configuration file %s: %s. Using defaults.",
            MODEL_CONFIG_PATH,
            exc,
        )
    except Exception as exc:  # pragma: no cover
        logger.error(
            "Unexpected error loading model configuration %s: %s. Using defaults.",
            MODEL_CONFIG_PATH,
            exc,
        )
    return DEFAULT_MODEL_CONFIG.copy()


MODEL_CONFIG: Dict[str, Any] = _load_model_config()


# ---------------------------------------------------------------------------
# Agent State Definition
# ---------------------------------------------------------------------------
# Agent State Definition
# ---------------------------------------------------------------------------


class AgentState(TypedDict, total=False):
    """Shared state dictionary propagated through LangGraph nodes."""

    session_id: str
    query: str
    transformed_query: str
    query_metadata: Dict[str, Any]
    messages: List[Dict[str, Any]]
    turbine_model: Optional[str]
    data_points: List[Dict[str, Any]]
    data_fetch_status: str
    retrieved_documents: List[Dict[str, Any]]
    hierarchical_context: str
    citations: List[Dict[str, Any]]
    llm_response: str
    response_metadata: Dict[str, Any]
    confidence_score: float
    guardrail_result: Dict[str, Any]
    errors: List[str]


# ---------------------------------------------------------------------------
# Utility Helpers
# ---------------------------------------------------------------------------

TURBINE_ALIASES = {
    "smt60": "SMT60",
    "taurus60": "SMT60",
    "taurus-60": "SMT60",
    "smt130": "SMT130",
    "titan130": "SMT130",
    "titan-130": "SMT130",
    "tm2500": "TM2500",
    "lm2500": "TM2500",
}


def detect_turbine_model(query: str) -> Optional[str]:
    query_lower = query.lower()
    for alias, canonical in TURBINE_ALIASES.items():
        if alias in query_lower:
            return canonical
    return None


def enrich_query(query: str, turbine_model: Optional[str], messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build an enriched query payload capturing inferred intent, context
    windows, and any operator-provided hints.
    """
    recent_context = [
        msg.get("content", "")
        for msg in messages[-3:]
        if msg.get("role") == "user"
    ]
    enriched = {
        "original_query": query,
        "turbine_model": turbine_model,
        "detected_language": detect_language(query),
        "recent_user_context": [ctx for ctx in recent_context if ctx],
    }
    if turbine_model:
        enriched["query_with_model_hint"] = f"{query} (turbine model: {turbine_model})"
    else:
        enriched["query_with_model_hint"] = query
    return enriched


def detect_language(text: str) -> str:
    """
    Lightweight language detection.
    Falls back to English when heuristics are inconclusive.
    """
    # Simple heuristic using Unicode ranges.
    # For production, integrate a dedicated language ID model.
    try:
        non_ascii = sum(1 for c in text if ord(c) > 127)
        ratio = non_ascii / max(len(text), 1)
        if ratio > 0.2:
            return "unknown-non-ascii"
    except Exception:  # pragma: no cover
        pass
    return "en"


def ensure_errors(state: AgentState) -> List[str]:
    """Guarantee an errors list is available."""
    return state.get("errors", [])


def get_model_entry(model_key: Optional[str]) -> Optional[Dict[str, Any]]:
    if not model_key:
        return None
    return MODEL_CONFIG.get("models", {}).get(model_key)


def resolve_model_key() -> str:
    override = (
        os.environ.get("AGENT_MODEL_KEY")
        or os.environ.get("AGENT_SELECTED_MODEL")
        or os.environ.get("LLM_MODEL_KEY")
    )
    models = MODEL_CONFIG.get("models", {})
    if override:
        if override in models:
            return override
        logger.warning("Requested model key %s not found in configuration; using default.", override)

    default_key = MODEL_CONFIG.get("default_model")
    if default_key in models:
        return default_key

    if models:
        first_key = next(iter(models))
        logger.warning("Default model key missing; falling back to first available key %s.", first_key)
        return first_key

    logger.error("Model configuration contains no models; reverting to built-in Nova Pro.")
    return "nova_pro"


def resolve_fallback_model_key(primary_key: str) -> Optional[str]:
    fallback_key = MODEL_CONFIG.get("fallback_model")
    if fallback_key and fallback_key != primary_key and get_model_entry(fallback_key):
        return fallback_key
    if primary_key != "nova_pro" and get_model_entry("nova_pro"):
        return "nova_pro"
    if primary_key != MODEL_CONFIG.get("default_model") and get_model_entry(MODEL_CONFIG.get("default_model")):
        return MODEL_CONFIG.get("default_model")
    return None


def fetch_neighbor_chunks(
    client: Any,
    index: str,
    source: Optional[str],
    chunk_index: Optional[int],
    window: int = 1,
) -> List[Dict[str, Any]]:
    """
    Retrieve adjacent chunks for hierarchical context reconstruction.
    """
    if not client or source is None or chunk_index is None:
        return []

    doc_ids = []
    for offset in range(-window, window + 1):
        if offset == 0:
            continue
        doc_ids.append(
            {
                "_index": index,
                "_id": f"{source}-{chunk_index + offset}".replace("/", "-").replace(" ", "-"),
            }
        )

    if not doc_ids:
        return []

    try:
        response = client.mget(body={"docs": doc_ids})
    except Exception as exc:  # pragma: no cover - safety logging
        logger.debug("Failed to fetch neighbor chunks: %s", exc)
        return []

    neighbors: List[Dict[str, Any]] = []
    for doc in response.get("docs", []):
        if doc.get("found"):
            neighbors.append(doc.get("_source", {}))
    return neighbors


def build_hierarchical_context(documents: List[Dict[str, Any]]) -> str:
    """
    Assemble a hierarchical context string from retrieved documents and
    their neighbors, preserving section relationships when metadata is
    available.
    """
    if not documents:
        return "No relevant documentation found in the knowledge base."

    context_parts: List[str] = []
    for idx, doc in enumerate(documents, start=1):
        metadata = doc.get("metadata", {})
        header = metadata.get("section_path") or metadata.get("heading") or metadata.get("section") or "Unknown Section"
        source = doc.get("source", "Unknown Source")
        page = metadata.get("page")
        header_line = f"[Doc {idx}] Source: {source}"
        if page is not None:
            header_line += f" (page {page})"
        header_line += f" | Section: {header}"

        context_parts.append(header_line)
        context_parts.append(doc.get("content") or doc.get("text") or "")

        neighbors = doc.get("neighbors", [])
        for neighbor in neighbors:
            neighbor_meta = neighbor.get("metadata", {})
            subsection = neighbor_meta.get("section_path") or neighbor_meta.get("heading") or neighbor_meta.get("section")
            if subsection:
                context_parts.append(f"  [Neighbor] {subsection}: {neighbor.get('text', '')}")
            else:
                context_parts.append(f"  [Neighbor] {neighbor.get('text', '')}")

        context_parts.append("")  # spacing

    return "\n".join(context_parts).strip()


def normalize_citations(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create citation payloads with normalized relevance scores derived
    from retrieval metadata.
    """
    if not documents:
        return []

    max_score = max(doc.get("score", 0.0) for doc in documents)
    if max_score <= 0:
        max_score = 1.0

    citations: List[Dict[str, Any]] = []
    for doc in documents:
        metadata = doc.get("metadata", {})
        normalized_score = min(max(doc.get("score", 0.0) / max_score, 0.0), 1.0)
        citations.append(
            {
                "source": doc.get("source"),
                "page": metadata.get("page"),
                "relevance_score": round(normalized_score, 3),
                "excerpt": (doc.get("content") or doc.get("text") or "")[:500],
                "section": metadata.get("section_path") or metadata.get("heading"),
            }
        )
    return citations


def combine_confidence(document_citations: List[Dict[str, Any]], data_points: List[Dict[str, Any]]) -> float:
    """
    Blend retrieval relevance with data availability to form a confidence score.
    """
    if not document_citations:
        base_confidence = 0.4
    else:
        avg_relevance = sum(c["relevance_score"] for c in document_citations) / len(document_citations)
        base_confidence = 0.55 + (avg_relevance * 0.35)

    if data_points:
        base_confidence += 0.05

    return min(0.98, round(base_confidence, 3))


def call_grok_api(payload: Dict[str, Any]) -> Optional[str]:
    """
    Invoke the external Grok reasoning API.
    """
    if not GROK_API_URL or not GROK_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            GROK_API_URL,
            headers=headers,
            json=payload,
            timeout=GROK_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        body = response.json()
        return body.get("response") or body.get("text")
    except requests.RequestException as exc:
        logger.warning("Grok API call failed: %s", exc, exc_info=True)
        return None


def apply_bedrock_guardrail(response_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply Bedrock Guardrails to the generated response. Returns the
    guardrail evaluation payload.
    """
    if not GUARDRAIL_ID:
        return {"status": "skipped", "details": "Guardrail ID not configured"}

    bedrock = boto3.client("bedrock", region_name=AWS_REGION)
    input_payload = {
        "text": response_text,
        "contextAttributes": {
            "confidenceScore": context.get("confidence_score"),
            "turbineModel": context.get("turbine_model"),
        },
    }
    try:
        result = bedrock.apply_guardrail(
            guardrailIdentifier=GUARDRAIL_ID,
            guardrailVersion=GUARDRAIL_VERSION,
            input=[{"type": "text", "text": json.dumps(input_payload)}],
        )
        return {"status": "applied", "result": result}
    except Exception as exc:  # pragma: no cover
        logger.error("Guardrail application failed: %s", exc, exc_info=True)
        return {"status": "error", "details": str(exc)}


# ---------------------------------------------------------------------------
# Model Invocation Helpers
# ---------------------------------------------------------------------------

def run_bedrock_model(model_entry: Optional[Dict[str, Any]], state: AgentState, errors: List[str]) -> Optional[str]:
    if not model_entry:
        errors.append("Bedrock model entry unavailable for invocation.")
        return None
    if not get_bedrock_client or not invoke_llm:
        errors.append("Bedrock client helpers not available in runtime package.")
        return None

    model_id = model_entry.get("model_id")
    if not model_id:
        errors.append("Bedrock model configuration missing model_id.")
        return None

    inference_config = model_entry.get("inference_config", {})
    max_tokens = inference_config.get("max_tokens", 2048)
    temperature = inference_config.get("temperature", 0.4)

    bedrock_client = get_bedrock_client(AWS_REGION)
    system_prompt = (
        "You are an expert assistant for gas turbine operations. "
        "Incorporate telemetry data and retrieved documentation to provide "
        "actionable, safety-conscious guidance. Always cite your sources."
    )
    user_prompt = (
        f"Operator question: {state['query']}\n\n"
        f"Transformed query: {state.get('transformed_query')}\n\n"
        "Context from knowledge base:\n"
        f"{state.get('hierarchical_context')}\n\n"
        "Recent telemetry points:\n"
        f"{json.dumps(state.get('data_points', []), default=str)}\n"
    )

    try:
        return invoke_llm(
            client=bedrock_client,
            model_id=model_id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            conversation_history=state.get("messages", []),
            max_tokens=max_tokens,
            temperature=temperature,
        )
    except Exception as exc:  # pragma: no cover
        errors.append(f"Bedrock invocation failed for model {model_id}: {exc}")
        logger.error("Bedrock invocation error for %s: %s", model_id, exc, exc_info=True)
        return None


# ---------------------------------------------------------------------------
# LangGraph Node Implementations
# ---------------------------------------------------------------------------

def query_transformer(state: AgentState) -> AgentState:
    query = state["query"]
    messages = state.get("messages", [])

    turbine_model = detect_turbine_model(query)
    enriched_payload = enrich_query(query, turbine_model, messages)

    transformed_query = enriched_payload["query_with_model_hint"]
    metadata = {
        "intent": "diagnostic_query",
        "language": enriched_payload["detected_language"],
        "turbine_model": turbine_model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "transformed_query": transformed_query,
        "query_metadata": metadata,
        "turbine_model": turbine_model,
    }


def data_fetcher(state: AgentState) -> AgentState:
    errors = ensure_errors(state)
    if not DATA_FETCH_ENABLED or not AGENTCORE_GATEWAY_URL:
        return {
            "data_points": [],
            "data_fetch_status": "disabled",
            "errors": errors,
        }

    turbine_model = state.get("turbine_model")
    payload = {
        "session_id": state["session_id"],
        "turbine_model": turbine_model,
        "query_metadata": state.get("query_metadata", {}),
        "variables": ["temperature", "pressure", "vibration"],
        "lookback_minutes": 30,
    }

    headers = {"x-api-key": AGENTCORE_GATEWAY_API_KEY} if AGENTCORE_GATEWAY_API_KEY else {}
    try:
        response = requests.post(
            f"{AGENTCORE_GATEWAY_URL.rstrip('/')}/timeseries",
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        body = response.json()
        return {
            "data_points": body.get("data", []),
            "data_fetch_status": "success",
            "errors": errors,
        }
    except requests.RequestException as exc:
        logger.warning("Data fetch failed: %s", exc, exc_info=True)
        errors.append(f"DataFetcher: {exc}")
        return {
            "data_points": [],
            "data_fetch_status": "error",
            "errors": errors,
        }


def knowledge_retriever(state: AgentState) -> AgentState:
    errors = ensure_errors(state)
    if not get_opensearch_client or not search_documents or not OPENSEARCH_ENDPOINT:
        errors.append("KnowledgeRetriever: OpenSearch not configured")
        return {
            "retrieved_documents": [],
            "hierarchical_context": "Knowledge retrieval is currently unavailable.",
            "citations": [],
            "errors": errors,
        }

    transformed_query = state.get("transformed_query") or state["query"]
    turbine_model = state.get("turbine_model")

    try:
        client = get_opensearch_client(OPENSEARCH_ENDPOINT, AWS_REGION)
        filters = {"turbine_model": turbine_model} if turbine_model else None
        documents = search_documents(
            client=client,
            index=OPENSEARCH_INDEX,
            query=transformed_query,
            filters=filters,
            top_k=5,
            embedding_model=EMBEDDING_MODEL,
            region=AWS_REGION,
        )

        # Stitch hierarchical neighbors for each result
        for doc in documents:
            metadata = doc.get("metadata", {})
            neighbors = fetch_neighbor_chunks(
                client=client,
                index=OPENSEARCH_INDEX,
                source=doc.get("source"),
                chunk_index=metadata.get("chunk_index"),
            )
            doc["neighbors"] = neighbors

        hierarchical_context = build_hierarchical_context(documents)
        citations = normalize_citations(documents)
        return {
            "retrieved_documents": documents,
            "hierarchical_context": hierarchical_context,
            "citations": citations,
            "errors": errors,
        }
    except Exception as exc:  # pragma: no cover
        logger.error("KnowledgeRetriever failure: %s", exc, exc_info=True)
        errors.append(f"KnowledgeRetriever: {exc}")
        return {
            "retrieved_documents": [],
            "hierarchical_context": "Knowledge retrieval failed.",
            "citations": [],
            "errors": errors,
        }


def reasoning_engine(state: AgentState) -> AgentState:
    errors = ensure_errors(state)
    citations = state.get("citations", [])

    primary_model_key = resolve_model_key()
    primary_entry = get_model_entry(primary_model_key)
    used_model_key = primary_model_key
    response_text: Optional[str] = None
    grok_invoked = False

    if not primary_entry:
        errors.append(f"Model configuration missing entry for key '{primary_model_key}'. Falling back to Nova Pro.")
        primary_model_key = "nova_pro"
        primary_entry = get_model_entry(primary_model_key)
        used_model_key = primary_model_key

    if primary_entry and primary_entry.get("type") == "grok":
        grok_payload = {
            "messages": state.get("messages", []),
            "query": state["query"],
            "transformed_query": state.get("transformed_query"),
            "turbine_model": state.get("turbine_model"),
            "hierarchical_context": state.get("hierarchical_context"),
            "data_points": state.get("data_points", []),
            "citations": citations,
        }
        response_text = call_grok_api(grok_payload)
        grok_invoked = True

        if not response_text:
            fallback_key = resolve_fallback_model_key(primary_model_key)
            if fallback_key:
                fallback_entry = get_model_entry(fallback_key)
                response_text = run_bedrock_model(fallback_entry, state, errors)
                used_model_key = fallback_key
            else:
                errors.append("Grok selected but no fallback Bedrock model configured.")
    else:
        response_text = run_bedrock_model(primary_entry, state, errors)
        if response_text is None:
            fallback_key = resolve_fallback_model_key(primary_model_key)
            if fallback_key:
                fallback_entry = get_model_entry(fallback_key)
                response_text = run_bedrock_model(fallback_entry, state, errors)
                used_model_key = fallback_key

    if not response_text:
        errors.append("ReasoningEngine unable to produce a response from configured models.")
        response_text = "Unable to generate a response at this time."

    response_metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_key": used_model_key,
        "model_display": (get_model_entry(used_model_key) or {}).get("display_name"),
        "grok_invoked": grok_invoked,
    }

    return {
        "llm_response": response_text,
        "response_metadata": response_metadata,
        "errors": errors,
    }


def response_validator(state: AgentState) -> AgentState:
    errors = ensure_errors(state)
    citations = state.get("citations", [])
    data_points = state.get("data_points", [])
    llm_response = state.get("llm_response", "")

    confidence_score = combine_confidence(citations, data_points)
    guardrail_result = apply_bedrock_guardrail(
        response_text=llm_response,
        context={
            "confidence_score": confidence_score,
            "turbine_model": state.get("turbine_model"),
        },
    )

    if guardrail_result.get("status") == "error":
        errors.append(f"Guardrail error: {guardrail_result.get('details')}")

    if guardrail_result.get("status") == "applied":
        outcomes = guardrail_result.get("result", {}).get("outputs", [])
        if outcomes:
            compliance = outcomes[0].get("complianceStatus")
            if compliance != "COMPLIANT":
                errors.append(f"Guardrail non-compliance: {compliance}")
                llm_response = (
                    "I am unable to provide that information safely. "
                    "Please consult the turbine supervisor or engineering support."
                )

    if confidence_score < MIN_CONFIDENCE_SCORE:
        errors.append(
            f"Confidence threshold not met (score={confidence_score}, "
            f"threshold={MIN_CONFIDENCE_SCORE})"
        )
        llm_response += (
            "\n\nConfidence in the retrieved information is below the "
            "required threshold. Please verify with a senior operator."
        )

    return {
        "llm_response": llm_response,
        "confidence_score": confidence_score,
        "guardrail_result": guardrail_result,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# LangGraph Assembly
# ---------------------------------------------------------------------------

graph = StateGraph(AgentState)
graph.add_node("QueryTransformer", query_transformer)
graph.add_node("DataFetcher", data_fetcher)
graph.add_node("KnowledgeRetriever", knowledge_retriever)
graph.add_node("ReasoningEngine", reasoning_engine)
graph.add_node("ResponseValidator", response_validator)

graph.set_entry_point("QueryTransformer")
graph.add_edge("QueryTransformer", "DataFetcher")
graph.add_edge("DataFetcher", "KnowledgeRetriever")
graph.add_edge("KnowledgeRetriever", "ReasoningEngine")
graph.add_edge("ReasoningEngine", "ResponseValidator")
graph.add_edge("ResponseValidator", END)

compiled_graph = graph.compile()


# ---------------------------------------------------------------------------
# Lambda Handler
# ---------------------------------------------------------------------------

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point for the LangGraph-based agent. Accepts the same
    payload shape as the legacy handler while providing the enhanced
    behaviour outlined in the recommendations.
    """
    logger.info("New AgentCore LangGraph handler received event: %s", json.dumps(event))

    if "httpMethod" in event:
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 204,
                "headers": CORS_HEADERS,
                "body": "",
            }
        body = event.get("body", "{}")
        if isinstance(body, str):
            payload = json.loads(body or "{}")
        else:
            payload = body
    else:
        payload = event

    if "query" not in payload and "inputText" in payload:
        payload["query"] = payload["inputText"]

    session_id = payload.get("session_id") or f"session-{datetime.now(timezone.utc).isoformat()}"
    query = payload.get("query")
    messages = payload.get("messages", [])

    if not query:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Query is required"}),
        }

    initial_state: AgentState = {
        "session_id": session_id,
        "query": query,
        "messages": messages,
        "errors": [],
    }

    final_state = compiled_graph.invoke(initial_state)

    response_payload = {
        "session_id": session_id,
        "response": final_state.get("llm_response"),
        "citations": final_state.get("citations", []),
        "confidence_score": final_state.get("confidence_score"),
        "turbine_model": final_state.get("turbine_model"),
        "data_points": final_state.get("data_points", []),
        "guardrail_result": final_state.get("guardrail_result"),
        "response_metadata": final_state.get("response_metadata"),
        "errors": final_state.get("errors", []),
        "messages": messages + [
            {"role": "user", "content": query, "timestamp": datetime.now(timezone.utc).isoformat()},
            {
                "role": "assistant",
                "content": final_state.get("llm_response"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ],
    }

    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": json.dumps(response_payload),
    }


