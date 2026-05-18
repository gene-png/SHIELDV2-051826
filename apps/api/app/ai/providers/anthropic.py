"""Anthropic Claude provider (default for v1).

Lazy-imports the SDK so unit tests that exercise the redactor or the egress
layer don't require the dependency or an API key. The egress layer chooses
fixture-replay when `SHIELD_LLM_MODE=fixture`, so unit/integration CI never
needs to hit a real API.
"""

from __future__ import annotations

from typing import Any

from app.ai.providers.base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set; either provide one or run with "
                "SHIELD_LLM_MODE=fixture."
            )
        from anthropic import Anthropic

        self._client = Anthropic(api_key=api_key)

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        system: str | None = None,
    ) -> LLMResponse:
        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system
        result = self._client.messages.create(**kwargs)
        # Anthropic returns content as a list of blocks; concatenate text blocks.
        text = "".join(getattr(b, "text", "") for b in getattr(result, "content", []))
        usage = getattr(result, "usage", None)
        return LLMResponse(
            text=text,
            input_tokens=getattr(usage, "input_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "output_tokens", 0) if usage else 0,
            model=model,
            raw=result.model_dump() if hasattr(result, "model_dump") else {},
        )
