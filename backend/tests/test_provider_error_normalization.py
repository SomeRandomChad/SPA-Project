from fastapi.testclient import TestClient
from app.main import app
from app.llm.provider_errors import LLMProviderError

client = TestClient(app)

class RateLimitedProvider:
    async def complete(self, prompt: str) -> str:
        raise LLMProviderError(
            status_code=429,
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please retry after the specified time.",
            retry_after_seconds=10,
        )

def test_rate_limit_maps_to_429_error_shape(monkeypatch):
    import app.llm.factory as factory
    monkeypatch.setattr(factory, "get_llm_provider", lambda: RateLimitedProvider())

    resp = client.post("/rephrase", json={"text": "hello"})
    assert resp.status_code == 429
    assert resp.headers.get("Retry-After") == "10"
    body = resp.json()
    assert body["code"] == "RATE_LIMIT_EXCEEDED"
    assert "message" in body
    assert isinstance(body.get("details"), list)

class TimeoutProvider:
    async def complete(self, prompt: str) -> str:
        raise LLMProviderError(
            status_code=504,
            code="LLM_TIMEOUT",
            message="The LLM request timed out.",
        )

def test_timeout_maps_to_504_error_shape(monkeypatch):
    import app.llm.factory as factory
    monkeypatch.setattr(factory, "get_llm_provider", lambda: TimeoutProvider())

    resp = client.post("/rephrase", json={"text": "hello"})
    assert resp.status_code == 504
    body = resp.json()
    assert body["code"] == "LLM_TIMEOUT"
    assert isinstance(body["message"], str)
    assert "details" in body
    assert isinstance(body["details"], list)