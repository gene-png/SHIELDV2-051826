"""LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    raw: dict[str, Any]


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        system: str | None = None,
    ) -> LLMResponse:
        """Synchronous chat call. Workers call this; the egress layer wraps it."""
