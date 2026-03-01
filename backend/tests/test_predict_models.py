import pytest
from pydantic import ValidationError

from main import PredictRequest, predict


def test_predict_supports_multiple_models():
    payload = PredictRequest(revenue=120000, cost=80000, growth_rate=0.12, model_type="ai_ensemble")
    body = predict(payload)

    assert body["model_type"] == "ai_ensemble"
    assert "confidence" in body
    assert "volatility_index" in body


def test_predict_rejects_unknown_model_type():
    with pytest.raises(ValidationError):
        PredictRequest(revenue=120000, cost=80000, growth_rate=0.12, model_type="unknown")
