"""Redactor regression suite — every PII kind plus adversarial fixtures.

Master Spec §12: "Treat the redactor as a security boundary, not a cosmetic
step." When a real-world payload defeats the redactor, add it here BEFORE
fixing the regex. Tests guard against regression.
"""

from __future__ import annotations

import pytest

from app.ai.redact import redact_for_ai, redact_payload
from app.models.enums import PiiKind


@pytest.mark.unit
def test_email_stripped() -> None:
    r = redact_for_ai("Email me at alice@example.org for details.")
    assert "[EMAIL]" in r.cleaned_text
    assert "alice@example.org" not in r.cleaned_text
    assert r.removed[PiiKind.EMAIL] == 1


@pytest.mark.unit
def test_phone_variants() -> None:
    samples = [
        "+1 (555) 123-4567",
        "555-123-4567",
        "555.123.4567",
        "(555) 123-4567 x 1234",
    ]
    for s in samples:
        r = redact_for_ai(f"Call me at {s}.")
        assert "[PHONE]" in r.cleaned_text, f"phone not stripped: {s}"


@pytest.mark.unit
def test_ssn_and_ein_distinct() -> None:
    r = redact_for_ai("SSN 123-45-6789 and EIN 12-3456789")
    assert "[SSN]" in r.cleaned_text
    assert "[EIN]" in r.cleaned_text
    assert r.removed[PiiKind.SSN] == 1
    assert r.removed[PiiKind.EIN] == 1


@pytest.mark.unit
def test_street_address() -> None:
    r = redact_for_ai("1500 Pennsylvania Avenue NW Suite 200")
    assert "[ADDRESS]" in r.cleaned_text


@pytest.mark.unit
def test_po_box() -> None:
    r = redact_for_ai("Send to P.O. Box 12345")
    assert "[ADDRESS]" in r.cleaned_text


@pytest.mark.unit
def test_client_org_name_replaced() -> None:
    r = redact_for_ai(
        "Nexus Federal Solutions Inc. reports a low maturity rating across...",
        client_org_name="Nexus Federal Solutions Inc.",
    )
    assert "[CLIENT]" in r.cleaned_text
    assert "Nexus" not in r.cleaned_text
    assert r.removed[PiiKind.CLIENT_ORG_NAME] == 1


@pytest.mark.unit
def test_signature_block() -> None:
    r = redact_for_ai("Sincerely,\nJane Smith")
    assert "[SIGNATURE_BLOCK]" in r.cleaned_text


@pytest.mark.unit
def test_payload_recursive_walk() -> None:
    payload = {
        "system": "Acme Compliance",
        "contacts": ["alice@acme.io", "555-123-4567"],
        "meta": {"signed_by": "Sincerely,\nBob Robertson"},
    }
    cleaned, agg = redact_payload(payload, client_org_name="Acme")
    assert cleaned["contacts"][0] == "[EMAIL]"
    assert cleaned["contacts"][1].startswith("[PHONE]")
    assert "[SIGNATURE_BLOCK]" in cleaned["meta"]["signed_by"]
    assert agg.removed[PiiKind.EMAIL] == 1
    assert agg.removed[PiiKind.PHONE] == 1


@pytest.mark.unit
def test_off_mode_flags_for_review() -> None:
    r = redact_for_ai("contact alice@example.org", mode="off")
    assert r.needs_human_review is True
    assert "alice@example.org" in r.cleaned_text  # not redacted in off mode
