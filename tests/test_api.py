"""Integration-style tests for the FastAPI HTTP layer (health check + validation only;
the /query test below is skipped by default since it requires live LLM API keys)."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_validation_rejects_short_query():
    response = client.post("/query", json={"query": "hi"})
    assert response.status_code == 422


@pytest.mark.skip(reason="Requires a configured LLM provider API key; run manually as a smoke test.")
def test_query_end_to_end():
    response = client.post("/query", json={"query": "What is the current price of AAPL?"})
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
