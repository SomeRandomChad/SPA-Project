from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_rephrase_contract_is_stable():
    res = client.post("/rephrase", json={"text": "hello"})
    assert res.status_code == 200

    data = res.json()
    assert set(data.keys()) == {"professional", "casual", "polite", "social"}
    assert all(isinstance(v, str) for v in data.values())