from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class BadProvider:
    async def complete(self, prompt: str) -> str:
        return "not json at all"

def test_invalid_model_output_returns_500_error_shape(monkeypatch):
    import app.llm.factory as factory

    monkeypatch.setattr(factory, "get_llm_provider", lambda: BadProvider())

    resp = client.post("/rephrase", json={"text": "hello"})
    assert resp.status_code == 500

    body = resp.json()
    assert body["code"] == "INTERNAL_ERROR"
    assert isinstance(body["message"], str)
    assert "details" in body
    assert isinstance(body["details"], list)
