"""
Tests for the /compare endpoint and supporting services.
LLM and vector-store calls are mocked so tests run offline without API keys.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.schemas.prediction import MLPredictionResponse, LLMPredictionResponse
from app.schemas.comparison import RAGResponse, LLMOnlyResponse, ComparisonResponse

client = TestClient(app)

# ── Fixtures / helpers ────────────────────────────────────────────────────────

ML_PRED = MLPredictionResponse(priority="urgent", confidence=0.82, latency_ms=5.0)
LLM_PRED = LLMPredictionResponse(
    priority="urgent", reasoning="Account locked is urgent.", latency_ms=300.0, cost_usd=0.0001
)
RAG_ANSWER = ("Your account can be unlocked by resetting your password.", 210.0, 0.0002)
LLM_ANSWER = ("Please try resetting your password.", 180.0, 0.0001)
SOURCES = [{"text": "Reset your password via the login page.", "id": "doc1", "distance": 0.12}]


def _mock_gather(*args, **kwargs):
    import asyncio
    return asyncio.coroutine(lambda: (SOURCES, LLM_ANSWER, ML_PRED, LLM_PRED))()


# ── Feature extractor (pure function — no mocking needed) ─────────────────────

def test_extract_features_urgent_signals():
    from app.services.feature_extractor import extract_features

    text = "URGENT!!! I cannot login at all!!!"
    features = extract_features(text)

    assert features["exclamation_count"] >= 3
    assert features["uppercase_ratio"] > 0.2
    assert features["negation_count"] >= 1
    assert features["text_length"] == float(len(text))


def test_extract_features_normal_text():
    from app.services.feature_extractor import extract_features

    features = extract_features("How do I update my billing address?")

    assert features["exclamation_count"] == 0.0
    assert features["multiple_punctuation"] == 0.0


# ── ML model (mocked joblib load) ─────────────────────────────────────────────

def test_predict_priority_ml_returns_schema():
    import numpy as np

    mock_model = MagicMock()
    mock_model.predict.return_value = ["urgent"]
    mock_model.predict_proba.return_value = np.array([[0.18, 0.82]])

    artifact = {"model": mock_model, "feature_columns": [
        "text_length", "exclamation_count", "uppercase_ratio",
        "multiple_punctuation", "sentiment_compound", "sentiment_neg", "negation_count",
    ]}

    with patch("app.services.ml_model._load_model", return_value=artifact):
        from app.services.ml_model import predict_priority_ml
        # Clear lru_cache so the patch takes effect
        predict_priority_ml.__wrapped__ if hasattr(predict_priority_ml, "__wrapped__") else None

        result = predict_priority_ml("My account is locked!")

    assert isinstance(result, MLPredictionResponse)
    assert result.priority == "urgent"
    assert 0.0 <= result.confidence <= 1.0
    assert result.latency_ms >= 0


# ── /compare endpoint (mocked LLM + vector store) ─────────────────────────────

def test_compare_endpoint_happy_path():
    with (
        patch("app.routers.compare.retrieve", return_value=SOURCES),
        patch("app.routers.compare.answer_query", side_effect=[LLM_ANSWER, RAG_ANSWER]),
        patch("app.routers.compare.predict_priority_ml", return_value=ML_PRED),
        patch("app.routers.compare.predict_priority_llm", return_value=LLM_PRED),
    ):
        response = client.post("/compare", json={"text": "My account has been locked"})

    assert response.status_code == 200
    data = response.json()

    assert "rag" in data
    assert "llm" in data
    assert "ml_prediction" in data
    assert "llm_prediction" in data

    assert data["ml_prediction"]["priority"] in ("urgent", "normal")
    assert data["llm_prediction"]["priority"] in ("urgent", "normal")


def test_compare_endpoint_missing_body():
    response = client.post("/compare", json={})
    assert response.status_code == 422


# ── /health ────────────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
