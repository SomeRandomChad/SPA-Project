import pytest
from fastapi.testclient import TestClient

# Adjust this import if your app is located elsewhere
from app.main import app


client = TestClient(app)


def assert_frozen_response_shape(payload: dict) -> None:
    # exact keys and all string values
    assert set(payload.keys()) == {"professional", "casual", "polite", "social"}
    assert all(isinstance(payload[k], str) for k in payload.keys())


def assert_error_shape(payload: dict) -> None:
    # minimal contract for your Error schema
    assert isinstance(payload, dict)
    assert payload.get("code") == "VALIDATION_ERROR"
    assert isinstance(payload.get("message"), str)
    # details is optional but if present, it should be a list of objects
    if "details" in payload and payload["details"] is not None:
        assert isinstance(payload["details"], list)
        for item in payload["details"]:
            assert isinstance(item, dict)
            assert isinstance(item.get("field"), str)
            assert isinstance(item.get("issue"), str)
            if "hint" in item and item["hint"] is not None:
                assert isinstance(item["hint"], str)


def test_rephrase_200_returns_frozen_contract_shape():
    resp = client.post("/rephrase", json={"text": "Hello world"})
    assert resp.status_code == 200

    body = resp.json()
    assert_frozen_response_shape(body)


def test_rephrase_400_returns_error_shape_for_empty_text():
    # Empty string should trigger validation failure => 400 with Error shape
    resp = client.post("/rephrase", json={"text": ""})
    assert resp.status_code == 400

    body = resp.json()
    assert_error_shape(body)


def test_rephrase_400_returns_error_shape_for_missing_text_field():
    # Missing required field should trigger validation failure => 400 with Error shape
    resp = client.post("/rephrase", json={})
    assert resp.status_code == 400

    body = resp.json()
    assert_error_shape(body)
