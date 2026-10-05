'''
LLM provider registry and factory utilities.

Central place to:
    - enumerate the available providers
    - build LLM instances for a given provider/model
    - list the selectable models per provider and capability (text / vision)
'''
import json
import time
import urllib.request
from typing import List, Optional

from llm.base_llm import BaseLLM, ChatLLM
from llm.gemini_llm import (
    DEFAULT_GEMINI_MODEL,
    GeminiChatLLM,
    GeminiLLM,
)
from llm.openrouter_llm import (
    DEFAULT_OPENROUTER_MODEL,
    OpenRouterChatLLM,
    OpenRouterLLM,
)

PROVIDER_GEMINI = "gemini"
PROVIDER_OPENROUTER = "openrouter"

PROVIDERS = [PROVIDER_GEMINI, PROVIDER_OPENROUTER]

# Human readable labels for the UI.
PROVIDER_LABELS = {
    PROVIDER_GEMINI: "Google Gemini",
    PROVIDER_OPENROUTER: "OpenRouter",
}

# Language models the user can choose from.
# NOTE: these are only fallbacks for the UI dropdown. The model string is passed
# straight through to the provider, so any valid model id also works.
GEMINI_TEXT_MODELS = [
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]

# Gemini models are natively multimodal, so the vision list matches the text list.
GEMINI_VISION_MODELS = list(GEMINI_TEXT_MODELS)

OPENROUTER_FALLBACK_TEXT_MODELS = [
    "openai/gpt-4o-mini",
    "openai/gpt-5-mini",
    "anthropic/claude-haiku-4.5",
    "anthropic/claude-sonnet-4.5",
    "google/gemini-2.5-flash",
    "deepseek/deepseek-v4.1-flash",
    "meta-llama/llama-4-maverick",
    "qwen/qwen3.5-flash-02-23",
]

OPENROUTER_FALLBACK_VISION_MODELS = [
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
    "anthropic/claude-haiku-4.5",
    "anthropic/claude-sonnet-4.5",
    "google/gemini-2.5-flash",
    "meta-llama/llama-4-maverick",
    "qwen/qwen3-vl-235b-a22b-instruct",
    "z-ai/glm-4.6v",
]

DEFAULT_MODELS = {
    PROVIDER_GEMINI: {
        "text": DEFAULT_GEMINI_MODEL,
        "vision": DEFAULT_GEMINI_MODEL,
    },
    PROVIDER_OPENROUTER: {
        "text": DEFAULT_OPENROUTER_MODEL,
        "vision": DEFAULT_OPENROUTER_MODEL,
    },
}

# Which environment variable holds the API key for each provider.
PROVIDER_API_KEY_ENV = {
    PROVIDER_GEMINI: "GEMINI_API_KEY",
    PROVIDER_OPENROUTER: "OPENROUTER_API_KEY",
}

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
_OPENROUTER_MODELS_CACHE = {"data": None, "fetched_at": 0.0}
_OPENROUTER_MODELS_TTL = 60 * 60  # seconds

# Tokens that mark a Gemini model as non-chat (TTS, image, audio, agents, ...).
GEMINI_MODELS_EXCLUDE = (
    "tts", "image", "lyria", "robotics", "computer-use", "deep-research",
    "antigravity", "transcribe", "embedding", "aqa", "native-audio", "-live",
)
GEMINI_MODELS_INCLUDE_PREFIXES = ("gemini-", "gemma-")
_GEMINI_MODELS_CACHE = {"data": None, "fetched_at": 0.0}
_GEMINI_MODELS_TTL = 60 * 60  # seconds


def _is_gemini_chat_model(name: str) -> bool:
    if name.startswith("nano-banana"):
        return False
    if not name.startswith(GEMINI_MODELS_INCLUDE_PREFIXES):
        return False
    if any(token in name for token in GEMINI_MODELS_EXCLUDE):
        return False
    return True


def fetch_gemini_models(force: bool = False) -> List[str]:
    '''
    List the Gemini models available to the configured API key (needs a key).

    Results are cached for an hour. Returns an empty list when no key is set or
    the request fails, so the caller can fall back to the static list.
    '''
    now = time.time()
    cached = _GEMINI_MODELS_CACHE
    if (
        not force
        and cached["data"] is not None
        and now - cached["fetched_at"] < _GEMINI_MODELS_TTL
    ):
        return cached["data"]

    try:
        from llm.gemini_llm import get_gemini_client

        client = get_gemini_client()
        names = []
        for model in client.models.list():
            actions = getattr(model, "supported_actions", None) or []
            name = (model.name or "").replace("models/", "")
            if actions and "generateContent" not in actions:
                continue
            if _is_gemini_chat_model(name):
                names.append(name)
        names = sorted(set(names))
        if names:
            cached["data"] = names
            cached["fetched_at"] = now
        return cached["data"] or []
    except Exception as exc:  # missing key / network -> static fallback
        print(f"Could not fetch Gemini models: {exc}")
        return cached["data"] or []


def get_default_provider() -> str:
    return PROVIDER_GEMINI


def get_default_model(provider: str, capability: str = "text") -> str:
    """Return the default model id for a provider/capability, with a safe fallback."""
    provider_models = DEFAULT_MODELS.get(provider, {})
    if capability in provider_models:
        return provider_models[capability]
    return provider_models.get("text", DEFAULT_GEMINI_MODEL)


def _model_supports(model: dict, capability: str) -> bool:
    arch = model.get("architecture", {}) or {}
    outputs = arch.get("output_modalities") or []
    inputs = arch.get("input_modalities") or []

    # Only offer models that produce text (skip image/audio generation models).
    if outputs and "text" not in outputs:
        return False
    if capability == "vision":
        return "image" in inputs
    return True


def fetch_openrouter_models(force: bool = False) -> List[dict]:
    '''
    Fetch the live OpenRouter model catalog (public endpoint, no key required).

    Results are cached for an hour. Returns an empty list on any failure so the
    caller can fall back to the static list.
    '''
    now = time.time()
    cached = _OPENROUTER_MODELS_CACHE
    if (
        not force
        and cached["data"] is not None
        and now - cached["fetched_at"] < _OPENROUTER_MODELS_TTL
    ):
        return cached["data"]

    try:
        req = urllib.request.Request(
            OPENROUTER_MODELS_URL,
            headers={"User-Agent": "jishoGenAI"},
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        data = payload.get("data", []) or []
        cached["data"] = data
        cached["fetched_at"] = now
        return data
    except Exception as exc:  # network / parsing errors -> static fallback
        print(f"Could not fetch OpenRouter models: {exc}")
        return cached["data"] or []


def get_models(provider: str, capability: str = "text") -> List[str]:
    '''
    List selectable model ids for a provider.

    Args:
        provider: one of PROVIDERS.
        capability: "text" or "vision".
    '''
    if provider == PROVIDER_GEMINI:
        # Prefer the live list (keeps deprecations from breaking the dropdown),
        # falling back to the curated static list when no key/network is available.
        live_models = fetch_gemini_models()
        if live_models:
            return live_models
        return GEMINI_VISION_MODELS if capability == "vision" else GEMINI_TEXT_MODELS

    if provider == PROVIDER_OPENROUTER:
        catalog = fetch_openrouter_models()
        ids = [
            m["id"]
            for m in catalog
            if m.get("id") and ":batch" not in m["id"] and _model_supports(m, capability)
        ]
        if ids:
            return sorted(set(ids))
        return (
            OPENROUTER_FALLBACK_VISION_MODELS
            if capability == "vision"
            else OPENROUTER_FALLBACK_TEXT_MODELS
        )

    return []


def openrouter_model_reasoning_mandatory(model: Optional[str]) -> bool:
    '''
    True when OpenRouter reports the model mandates reasoning (so it cannot be
    disabled). Unknown/offline models return False, so reasoning is disabled by
    default for everything we can.
    '''
    if not model:
        return False
    for entry in fetch_openrouter_models():
        if entry.get("id") == model:
            return bool((entry.get("reasoning") or {}).get("mandatory"))
    return False


def resolve_model(provider: str, model: Optional[str], capability: str = "text") -> str:
    '''
    Validate a model id against the available list, falling back to the
    provider default when it is missing or stale (e.g. a retired model).
    '''
    if model and model in get_models(provider, capability):
        return model
    return get_default_model(provider, capability)


def create_llm(
    provider: str = PROVIDER_GEMINI,
    model: Optional[str] = None,
    system_message: str = "",
    api_key: Optional[str] = None,
    capability: str = "text",
) -> BaseLLM:
    '''
    Build a stateless LLM for the given provider/model.

    Args:
        provider: PROVIDER_GEMINI or PROVIDER_OPENROUTER.
        model: model id. Defaults to the provider default when omitted.
        system_message: system prompt.
        api_key: optional key override (e.g. entered in the settings UI).
        capability: "text" or "vision"; used to resolve the default model.
    '''
    model = model or get_default_model(provider, capability)

    if provider == PROVIDER_OPENROUTER:
        return OpenRouterLLM(
            system_message = system_message,
            model = model,
            api_key = api_key,
            disable_reasoning = not openrouter_model_reasoning_mandatory(model),
        )
    return GeminiLLM(
        system_message = system_message,
        model = model,
        api_key = api_key,
    )


def create_chat_llm(
    provider: str = PROVIDER_GEMINI,
    model: Optional[str] = None,
    system_message: str = "",
    api_key: Optional[str] = None,
    capability: str = "text",
) -> ChatLLM:
    '''Build a stateful chat LLM for the given provider/model.'''
    model = model or get_default_model(provider, capability)

    if provider == PROVIDER_OPENROUTER:
        return OpenRouterChatLLM(
            system_message = system_message,
            model = model,
            api_key = api_key,
            disable_reasoning = not openrouter_model_reasoning_mandatory(model),
        )
    return GeminiChatLLM(
        system_message = system_message,
        model = model,
        api_key = api_key,
    )
