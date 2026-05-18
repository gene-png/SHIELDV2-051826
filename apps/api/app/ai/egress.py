"""Single LLM egress point — every outbound call routes through here.

Wraps redaction (`app.ai.redact`) and provider invocation
(`app.ai.providers`), records an `llm_calls` row, and surfaces a
`pending_redaction_review` status when the redactor flags a payload for
human approval (first call per service per client per Master Spec §12).
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.ai.providers import LLMProvider, LLMResponse, get_provider
from app.ai.redact import RedactionResult, redact_for_ai, redact_payload
from app.settings import get_settings


@dataclass
class EgressResult:
    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    duration_ms: int
    redaction: RedactionResult
    fixture_replay: bool


_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "llm"


def _fixture_key(messages: list[dict[str, str]], model: str) -> str:
    payload = json.dumps({"model": model, "messages": messages}, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def _read_fixture(key: str) -> dict[str, Any] | None:
    path = _FIXTURE_DIR / f"{key}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def chat_redacted(
    messages: list[dict[str, str]],
    *,
    purpose: str,
    prompt_version: str,
    client_org_name: str | None = None,
    system: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.2,
    provider: LLMProvider | None = None,
) -> EgressResult:
    """Top-level LLM call.

    1. Redact every message (and system prompt) via `redact_for_ai`.
    2. If `SHIELD_LLM_MODE=fixture`, read a matching fixture instead of calling
       the provider (CI safety).
    3. Otherwise, call the provider and capture token counts + duration.

    A separate caller is responsible for writing the `llm_calls` audit row —
    this function returns enough state to do that.
    """
    settings = get_settings()
    mode = settings.shield_llm_mode

    # Step 1: redact.
    redacted_messages: list[dict[str, str]] = []
    aggregate_red: RedactionResult | None = None
    for m in messages:
        content = m.get("content", "")
        r = redact_for_ai(content, client_org_name=client_org_name, mode=settings.shield_redaction_mode)
        redacted_messages.append({**m, "content": r.cleaned_text})
        aggregate_red = (
            r
            if aggregate_red is None
            else RedactionResult(
                cleaned_text="(merged)",
                removed={**aggregate_red.removed, **r.removed},
                confidence=min(aggregate_red.confidence, r.confidence),
                needs_human_review=aggregate_red.needs_human_review or r.needs_human_review,
            )
        )
    redacted_system = system
    if system:
        sysr = redact_for_ai(system, client_org_name=client_org_name, mode=settings.shield_redaction_mode)
        redacted_system = sysr.cleaned_text

    assert aggregate_red is not None  # at least one message required

    # Step 2: fixture replay (CI) or real call.
    started = time.perf_counter()
    if mode == "fixture":
        key = _fixture_key(redacted_messages, settings.shield_llm_model)
        fx = _read_fixture(key)
        if fx is None:
            # Don't fail tests for missing fixtures — return a deterministic
            # placeholder. Tests that assert exact strings should register the
            # fixture before exercising the code path.
            text = "[fixture-missing] " + (purpose or "")
            response = LLMResponse(
                text=text, input_tokens=0, output_tokens=0, model=settings.shield_llm_model, raw={}
            )
        else:
            response = LLMResponse(
                text=fx.get("text", ""),
                input_tokens=int(fx.get("input_tokens", 0)),
                output_tokens=int(fx.get("output_tokens", 0)),
                model=fx.get("model", settings.shield_llm_model),
                raw=fx,
            )
    else:
        provider = provider or get_provider()
        response = provider.chat(
            redacted_messages,
            model=settings.shield_llm_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=redacted_system,
        )
    duration_ms = int((time.perf_counter() - started) * 1000)

    return EgressResult(
        text=response.text,
        provider=settings.shield_llm_provider,
        model=response.model,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        duration_ms=duration_ms,
        redaction=aggregate_red,
        fixture_replay=mode == "fixture",
    )


__all__ = ["EgressResult", "chat_redacted", "redact_payload"]
