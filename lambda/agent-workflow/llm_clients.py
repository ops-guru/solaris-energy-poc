"""
LLM Client Helper Module

Provides utilities for invoking AWS Bedrock LLMs (Claude, Nova, etc.).
"""
import json
import logging
from typing import Any, Dict, List, Optional
import boto3

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)


def get_bedrock_client(region: str = "us-east-1"):
    """Create and return a Bedrock runtime client."""
    return boto3.client("bedrock-runtime", region_name=region)


ALLOWED_ROLES = {"user", "assistant"}


def _normalize_role(role: str) -> str:
    lowered = (role or "user").lower()
    if lowered in ALLOWED_ROLES:
        return lowered
    # Treat anything else (including "system") as assistant narration
    return "assistant"


def _extract_text(message: Any) -> str:
    if hasattr(message, "content"):
        return str(getattr(message, "content", ""))
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(message)


def format_conversation_history(messages: List[Any]) -> List[Dict[str, str]]:
    """Normalize history into role/text pairs for later conversion."""
    formatted: List[Dict[str, str]] = []
    for msg in messages:
        if hasattr(msg, "role"):
            raw_role = getattr(msg, "role", "user")
        elif isinstance(msg, dict):
            raw_role = msg.get("role", "user")
        else:
            raw_role = "user"
        role = _normalize_role(str(raw_role))
        formatted.append({
            "role": role,
            "text": _extract_text(msg),
        })
    return formatted


def invoke_llm(
    client: Any,
    model_id: str,
    system_prompt: str,
    user_prompt: str,
    conversation_history: Optional[List[Any]] = None,
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    """
    Invoke Bedrock LLM model (Claude, Nova, etc.).
    
    Args:
        client: Bedrock runtime client
        model_id: Model identifier (e.g., "anthropic.claude-3-5-sonnet-20241022-v2:0")
        system_prompt: System prompt
        user_prompt: User prompt
        conversation_history: Optional conversation history
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
    
    Returns:
        Generated response text
    """
    try:
        formatted_history = format_conversation_history(conversation_history or [])

        # Determine API format based on model
        if "claude" in model_id.lower():
            # Claude 3.x format
            messages = [
                {
                    "role": entry["role"],
                    "content": [{"type": "text", "text": entry["text"]}],
                }
                for entry in formatted_history
            ]
            messages.append(
                {"role": "user", "content": [{"type": "text", "text": user_prompt}]}
            )
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_prompt,
                "messages": messages,
            }
        elif "nova" in model_id.lower():
            messages = [
                {
                    "role": entry["role"],
                    "content": [{"text": entry["text"]}],
                }
                for entry in formatted_history
            ]
            messages.append(
                {"role": "user", "content": [{"text": user_prompt}]}
            )
            body = {
                "system": [{"text": system_prompt}],
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": temperature,
                },
            }
        elif "amazon.titan" in model_id.lower():
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            body = {
                "inputText": combined_prompt,
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens,
                    "temperature": temperature,
                },
            }
        else:
            # Default to Claude-style formatting
            messages = [
                {
                    "role": entry["role"],
                    "content": [{"type": "text", "text": entry["text"]}],
                }
                for entry in formatted_history
            ]
            messages.append(
                {"role": "user", "content": [{"type": "text", "text": user_prompt}]}
            )
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_prompt,
                "messages": messages,
            }
        
        # Invoke model
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        
        # Parse response
        response_body = json.loads(response["body"].read())
        logger.info(
            "LLM raw response for %s: %s",
            model_id,
            json.dumps(response_body)[:4000],
        )
        
        # Extract text based on model type
        if "claude" in model_id.lower():
            # Claude returns content array
            content = response_body.get("content", [])
            if content and isinstance(content, list):
                text_parts = [
                    item.get("text", "")
                    for item in content
                    if item.get("type") == "text"
                ]
                return "".join(text_parts)
            return ""
        elif "nova" in model_id.lower() or "amazon.titan" in model_id.lower():
            # Titan/Nova returns results array
            results = response_body.get("results", [])
            if results:
                first = results[0]
                output_text = first.get("outputText")
                if output_text:
                    return output_text
                output = first.get("output")
                if isinstance(output, dict):
                    message = output.get("message")
                    if isinstance(message, dict):
                        content = message.get("content", [])
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict):
                                text_val = item.get("text") or item.get("value")
                                if text_val:
                                    text_parts.append(text_val)
                        if text_parts:
                            return "".join(text_parts)
                # Some payloads return top-level output array
                output_items = first.get("output", [])
                if isinstance(output_items, list):
                    text_parts = []
                    for item in output_items:
                        if isinstance(item, dict):
                            text_val = item.get("text") or item.get("value")
                            if text_val:
                                text_parts.append(text_val)
                    if text_parts:
                        return "".join(text_parts)
                logger.warning(
                    "Nova results missing text content",
                    extra={
                        "model_id": model_id,
                        "result_keys": list(first.keys()),
                    },
                )
            # Some responses (notably non-streaming Nova) return top-level output
            top_output = response_body.get("output")
            if isinstance(top_output, dict):
                message = top_output.get("message")
                if isinstance(message, dict):
                    content = message.get("content", [])
                    if isinstance(content, list):
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict):
                                text_val = item.get("text") or item.get("value")
                                if text_val:
                                    text_parts.append(text_val)
                        if text_parts:
                            return "".join(text_parts)
            elif isinstance(top_output, list):
                text_parts = []
                for item in top_output:
                    if isinstance(item, dict):
                        text_val = item.get("text") or item.get("value")
                        if text_val:
                            text_parts.append(text_val)
                if text_parts:
                    return "".join(text_parts)
            logger.warning(
                "LLM empty results",
                extra={
                    "model_id": model_id,
                    "response_body": response_body,
                },
            )
            return ""
        else:
            # Fallback
            return response_body.get("content", [{}])[0].get("text", "") if response_body.get("content") else ""
        
    except Exception as e:
        logger.error(f"LLM invocation error: {str(e)}", exc_info=True)
        raise


def switch_llm_model(
    current_model: str,
    target_model: str,
) -> str:
    """
    Switch between LLM models (Claude, Nova, Grok).
    
    Args:
        current_model: Current model ID
        target_model: Target model ID
    
    Returns:
        New model ID to use
    """
    # Model mapping
    model_map = {
        "claude": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "nova": "amazon.nova-pro-v1:0",
        "grok": "grok-beta",  # Placeholder until Grok API available
    }
    
    target_lower = target_model.lower()
    if target_lower in model_map:
        new_model = model_map[target_lower]
        logger.info(f"Switching from {current_model} to {new_model}")
        return new_model
    
    logger.warning(f"Unknown target model: {target_model}, keeping {current_model}")
    return current_model
