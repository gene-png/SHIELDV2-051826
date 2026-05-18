"""PII redaction — the v1 primary security control.

Master Spec §12 states: "Treat the redactor as a security boundary, not a
cosmetic step." Every outbound LLM payload routes through `redact_for_ai()`
(or `redact_payload()` for nested structures). The result records:

- the cleaned text
- a per-PII-kind count of items stripped
- a confidence score
- a `needs_human_review` flag the egress layer honors by enqueueing the
  call as `pending_redaction_review` until a consultant approves the
  redacted payload (first call per service per client).

The corpus of adversarial fixtures lives in `redact_test_corpus.py` and is
exercised by `apps/api/tests/unit/test_redactor.py`. Add new edge cases there
before relaxing any regex; redaction failures are security findings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.models.enums import PiiKind

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(
    r"(?<![\w.])[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,24}(?![\w.])"
)

# US + intl phone, tolerant of "ext", spaces, dashes, parens, "+", and "x".
PHONE_RE = re.compile(
    r"""(?xi)
    (?<![\w])
    (?:\+?\d{1,3}[\s\-.]?)?           # country code
    (?:\(?\d{3}\)?[\s\-.]?){1,2}      # area + exchange
    \d{4}                              # subscriber
    (?:\s*(?:x|ext\.?)\s*\d{2,6})?    # extension
    (?![\w])
    """
)

# SSN (avoid TIN/EIN overlap by leading whitespace/word-boundary).
SSN_RE = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")

# EIN: 2 digits, dash, 7 digits.
EIN_RE = re.compile(r"(?<!\d)\d{2}-\d{7}(?!\d)")

# CAGE code: 5 chars uppercase alphanumeric, no I or O.
CAGE_RE = re.compile(r"\b(?:CAGE[\s:#-]*)?([0-9A-HJ-NP-Z]{5})\b")

# Contract numbers: heuristic — government-style alphanumeric blocks 10+ chars,
# often prefixed FA, W91, N00, HQ, etc.
CONTRACT_RE = re.compile(
    r"\b(?:FA|W\d{2}|N\d{2}|HQ|HC|GS|SP|SPM|FE|F0|GS\-)[A-Z0-9\-]{6,30}\b"
)

# US street address heuristic: number + street word + optional unit.
STREET_RE = re.compile(
    r"""(?xi)
    \b
    \d{1,6}\s+
    [A-Za-z0-9.\-' ]{1,80}?
    \s+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?|
        Court|Ct\.?|Way|Place|Pl\.?|Parkway|Pkwy\.?|Highway|Hwy\.?|Square|Sq\.?|
        Trail|Tr\.?|Terrace|Ter\.?)
    (?:\s+(?:Suite|Ste\.?|Floor|Fl\.?|Unit|Apt\.?|#)\s*[A-Za-z0-9\-]+)?
    \b
    """
)

# PO Box heuristic.
PO_BOX_RE = re.compile(r"\bP\.?\s*O\.?\s*Box\s+\d{1,8}\b", re.IGNORECASE)

# Sign-off heuristic: common closers + a name on the next line.
SIGNATURE_RE = re.compile(
    r"(?m)^(Sincerely|Regards|Best regards|Best|Warm regards|Thanks|Thank you|"
    r"Cheers|Respectfully|Yours truly|Cordially)[,\.]?\s*\n[^\n]{1,80}",
    re.IGNORECASE,
)


@dataclass
class RedactionResult:
    cleaned_text: str
    removed: dict[PiiKind, int] = field(default_factory=dict)
    confidence: float = 1.0
    needs_human_review: bool = False
    notes: list[str] = field(default_factory=list)

    def total_removed(self) -> int:
        return sum(self.removed.values())


def _bump(removed: dict[PiiKind, int], kind: PiiKind, n: int = 1) -> None:
    removed[kind] = removed.get(kind, 0) + n


def _scrub_client_org_name(text: str, client_org_name: str | None, removed: dict[PiiKind, int]) -> str:
    if not client_org_name or len(client_org_name) < 3:
        return text
    pattern = re.compile(re.escape(client_org_name), re.IGNORECASE)
    cleaned, count = pattern.subn("[CLIENT]", text)
    if count:
        _bump(removed, PiiKind.CLIENT_ORG_NAME, count)
    return cleaned


def _strip_pattern(
    pattern: re.Pattern[str],
    text: str,
    replacement: str,
    kind: PiiKind,
    removed: dict[PiiKind, int],
) -> str:
    cleaned, count = pattern.subn(replacement, text)
    if count:
        _bump(removed, kind, count)
    return cleaned


def redact_for_ai(
    text: str,
    *,
    client_org_name: str | None = None,
    mode: str = "strict",
) -> RedactionResult:
    """Run every PII stripper against ``text`` in `strict` mode order.

    `standard` mode skips the heuristic person-name passes; `off` is forbidden
    outside dev (enforced at the settings layer).
    """
    if mode == "off":
        # Settings layer should already have refused this in non-dev. Surface
        # it loudly in case it slipped through.
        return RedactionResult(
            cleaned_text=text,
            confidence=0.0,
            needs_human_review=True,
            notes=["mode=off — redaction was bypassed"],
        )

    removed: dict[PiiKind, int] = {}
    out = text

    out = _scrub_client_org_name(out, client_org_name, removed)
    out = _strip_pattern(EMAIL_RE, out, "[EMAIL]", PiiKind.EMAIL, removed)
    out = _strip_pattern(PHONE_RE, out, "[PHONE]", PiiKind.PHONE, removed)
    out = _strip_pattern(SSN_RE, out, "[SSN]", PiiKind.SSN, removed)
    out = _strip_pattern(EIN_RE, out, "[EIN]", PiiKind.EIN, removed)
    out = _strip_pattern(CAGE_RE, out, "[CAGE]", PiiKind.CAGE_CODE, removed)
    out = _strip_pattern(CONTRACT_RE, out, "[CONTRACT]", PiiKind.CONTRACT_NUMBER, removed)
    out = _strip_pattern(STREET_RE, out, "[ADDRESS]", PiiKind.STREET_ADDRESS, removed)
    out = _strip_pattern(PO_BOX_RE, out, "[ADDRESS]", PiiKind.STREET_ADDRESS, removed)
    out = _strip_pattern(SIGNATURE_RE, out, "[SIGNATURE_BLOCK]", PiiKind.SIGNATURE_BLOCK, removed)

    # Person-name detection is intentionally lightweight in v1 — flag for review
    # when the strict mode is requested and no name-strip backend is wired up.
    needs_review = mode == "strict" and removed.get(PiiKind.CLIENT_ORG_NAME, 0) == 0 and bool(
        client_org_name
    )

    return RedactionResult(
        cleaned_text=out,
        removed=removed,
        confidence=0.9 if removed else 1.0,
        needs_human_review=needs_review,
    )


def redact_payload(
    payload: Any,
    *,
    client_org_name: str | None = None,
    mode: str = "strict",
) -> tuple[Any, RedactionResult]:
    """Recursively redact every string leaf in ``payload``.

    Lists and dict values are walked; dict keys are kept verbatim (they are
    typically schema names, not PII).
    """
    aggregate = RedactionResult(cleaned_text="", removed={}, confidence=1.0)

    def _walk(node: Any) -> Any:
        if isinstance(node, str):
            r = redact_for_ai(node, client_org_name=client_org_name, mode=mode)
            for k, n in r.removed.items():
                aggregate.removed[k] = aggregate.removed.get(k, 0) + n
            if r.needs_human_review:
                aggregate.needs_human_review = True
            aggregate.confidence = min(aggregate.confidence, r.confidence)
            return r.cleaned_text
        if isinstance(node, list):
            return [_walk(x) for x in node]
        if isinstance(node, dict):
            return {k: _walk(v) for k, v in node.items()}
        return node

    cleaned = _walk(payload)
    aggregate.cleaned_text = "(structured payload — see object form)"
    return cleaned, aggregate
