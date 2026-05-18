"""Provider selection. Env-driven per Master Spec §4.4."""

from __future__ import annotations

from app.ai.providers.base import LLMProvider
from app.settings import get_settings


def get_provider() -> LLMProvider:
    settings = get_settings()
    if settings.shield_llm_provider == "anthropic":
        from app.ai.providers.anthropic import AnthropicProvider

        return AnthropicProvider(api_key=settings.anthropic_api_key)
    raise NotImplementedError(
        f"LLM provider {settings.shield_llm_provider!r} not wired up yet. "
        "Add an implementation under app/ai/providers/ and register it here."
    )
