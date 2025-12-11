import os
import time
import requests
from typing import List, Dict, Any, Tuple

# Default configuration (prioritized free/efficient coding/debugging models; at least 10)
PREFERRED_MODELS: List[str] = [
    # Strong coding/reasoning, large context (often free-tier)
    "deepseek/deepseek-reasoner",
    "deepseek/deepseek-chat",
    "qwen/qwen-2-72b-instruct",
    "qwen/qwen-2-7b-instruct",
    # Mixture-of-experts and coding-tuned options
    "mistralai/mixtral-8x7b-instruct",
    "mistralai/mistral-7b-instruct",
    "nousresearch/nous-hermes-2-mixtral-8x7b-sft",
    "openchat/openchat-7b",
    # Additional free/low-cost coding-friendly models
    "snowflake/snowflake-arctic-instruct",
    "meta-llama/llama-3-8b-instruct",
    "meta-llama/llama-3-70b-instruct",
    "tiiuae/falcon-180b-chat",
]
ENABLE_FREE_FALLBACK = os.getenv("OPENROUTER_ENABLE_FREE_FALLBACK", "true").lower() == "true"
FORCE_FREE_ONLY = os.getenv("OPENROUTER_FORCE_FREE_ONLY", "true").lower() == "true"
MAX_RETRIES = 6
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_REFERRER = os.getenv("OPENROUTER_REFERRER", "http://localhost")
OPENROUTER_TITLE = os.getenv("OPENROUTER_TITLE", "AI Engine Microservice")


def _fetch_available_models() -> Dict[str, dict]:
    """Fetch available models from OpenRouter and return a dict keyed by model id."""
    if not OPENROUTER_API_KEY:
        return {}

    try:
        resp = requests.get(
            f"{OPENROUTER_BASE_URL}/models",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=15,
        )
        if resp.status_code != 200:
            print(f"[OpenRouter] Failed to fetch models: {resp.status_code} {resp.text}")
            return {}
        data = resp.json()
        models = data.get("data", []) or data.get("models", [])
        model_map = {}
        for m in models:
            model_id = m.get("id")
            if not model_id:
                continue
            # Pricing may include prompt/completion. Consider free if prompt == 0
            pricing = m.get("pricing") or {}
            prompt_cost = pricing.get("prompt", pricing.get("input", None))
            is_free = prompt_cost == 0
            context_length = m.get("context_length") or m.get("max_context_length")
            model_map[model_id] = {
                "id": model_id,
                "context_length": context_length or 0,
                "is_free": is_free,
                "raw": m,
            }
        return model_map
    except Exception as e:
        print(f"[OpenRouter] Error fetching models: {e}")
        return {}


def _select_candidates(
    available: Dict[str, dict],
    min_context: int,
    preferred: List[str],
    enable_free_fallback: bool,
) -> List[str]:
    """Build an ordered candidate list respecting preferences, context, and free fallback."""
    candidates = []

    def eligible(model_id: str) -> bool:
        info = available.get(model_id)
        if info is None:
            return False
        if FORCE_FREE_ONLY and not info.get("is_free"):
            return False
        return info.get("context_length", 0) >= min_context

    # Preferred in order
    for mid in preferred:
        if eligible(mid):
            candidates.append(mid)

    # Free fallbacks (not already included)
    if enable_free_fallback:
        free_models = [
            mid
            for mid, meta in available.items()
            if meta.get("is_free")
            and meta.get("context_length", 0) >= min_context
            and mid not in candidates
        ]
        candidates.extend(free_models)

    # Any remaining models with sufficient context
    for mid, meta in available.items():
        if mid in candidates:
            continue
        if meta.get("context_length", 0) >= min_context and (not FORCE_FREE_ONLY or meta.get("is_free")):
            candidates.append(mid)

    return candidates


def _should_retry(status_code: int, error_body: str) -> bool:
    if status_code in (429, 500, 502, 503, 504):
        return True
    if "context_length_exceeded" in error_body or "context_length" in error_body:
        return True
    if "model_not_available" in error_body or "provider_error" in error_body:
        return True
    return False


def ask(
    *,
    messages: List[Dict[str, str]],
    min_context: int = 8000,
    preferred_models: List[str] | None = None,
    enable_free_fallback: bool | None = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    """
    Ask OpenRouter with automatic model selection and fallbacks.
    Returns dict: { model_used, fallbacks_attempted, content, raw_response }
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OpenRouter API key not configured")

    preferred = preferred_models or PREFERRED_MODELS
    free_fallback = ENABLE_FREE_FALLBACK if enable_free_fallback is None else enable_free_fallback

    available = _fetch_available_models()
    candidates = _select_candidates(available, min_context, preferred, free_fallback)

    if not candidates:
        raise RuntimeError("No OpenRouter models available that satisfy context requirements")

    fallbacks: List[str] = []
    last_error: Tuple[int, str] | None = None

    for attempt, model_id in enumerate(candidates[:MAX_RETRIES], start=1):
        fallbacks.append(model_id)
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": OPENROUTER_REFERRER,
                "X-Title": OPENROUTER_TITLE,
            }
            body = {
                "model": model_id,
                "messages": messages,
                "temperature": 0.1,
                "top_p": 0.8,
                "max_tokens": 2000,
            }
            resp = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=body,
                timeout=timeout,
            )

            if resp.status_code == 200:
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {
                    "model_used": model_id,
                    "fallbacks_attempted": fallbacks,
                    "content": content,
                    "raw_response": data,
                }

            # Handle retryable errors
            error_text = resp.text
            if _should_retry(resp.status_code, error_text) and attempt < MAX_RETRIES:
                last_error = (resp.status_code, error_text)
                time.sleep(1)  # brief backoff
                continue

            # Non-retryable or out of retries
            raise RuntimeError(f"OpenRouter error {resp.status_code}: {error_text}")

        except requests.exceptions.Timeout as e:
            last_error = (408, str(e))
            if attempt < MAX_RETRIES:
                time.sleep(1)
                continue
            raise RuntimeError(f"OpenRouter timeout: {e}")
        except requests.exceptions.RequestException as e:
            last_error = (0, str(e))
            if attempt < MAX_RETRIES:
                time.sleep(1)
                continue
            raise RuntimeError(f"OpenRouter network error: {e}")

    # If we exit loop without return, all retries failed
    if last_error:
        code, text = last_error
        raise RuntimeError(f"All model attempts failed. Last error {code}: {text}")
    raise RuntimeError("All model attempts failed for unknown reasons")

