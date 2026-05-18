"""Smoke test for the FastAPI bootstrap. Scaffolding placeholder until §3 lands."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health() -> None:
    from app.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "shield-api"
