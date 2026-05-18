"""LLM provider abstraction.

Per Master Spec §4.4 the provider is environment-configurable. Anthropic
Claude is the v1 default (`SHIELD_LLM_PROVIDER=anthropic`,
`SHIELD_LLM_MODEL=claude-opus-4-7`). Each concrete provider implements the
`LLMProvider` protocol and is selected by `get_provider()` at request time.
"""

from __future__ import annotations

from app.ai.providers.base import LLMProvider, LLMResponse
from app.ai.providers.factory import get_provider

__all__ = ["LLMProvider", "LLMResponse", "get_provider"]
