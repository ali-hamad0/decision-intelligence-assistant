import logging
import time
import warnings
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

from app.schemas.prediction import MLPredictionResponse
from app.services.feature_extractor import extract_features

logger = logging.getLogger(__name__)

_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "priority_model.joblib"


@lru_cache(maxsize=1)
def _load_model() -> dict:
    logger.info("Loading ML model from %s", _MODEL_PATH)
    return joblib.load(_MODEL_PATH)


def predict_priority_ml(text: str) -> MLPredictionResponse:
    start = time.perf_counter()

    artifact = _load_model()
    model = artifact["model"]
    feature_columns = artifact["feature_columns"]

    features = extract_features(text)
    X = pd.DataFrame([features])[feature_columns]

    label = str(model.predict(X)[0])
    confidence = float(max(model.predict_proba(X)[0]))

    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    return MLPredictionResponse(priority=label, confidence=confidence, latency_ms=latency_ms)
