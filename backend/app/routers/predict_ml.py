import logging

from fastapi import APIRouter, HTTPException

from app.schemas.prediction import MLPredictionResponse
from app.schemas.query import QueryRequest
from app.services.ml_model import predict_priority_ml

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/ml", response_model=MLPredictionResponse)
def predict_ml(request: QueryRequest) -> MLPredictionResponse:
    logger.info("ML prediction request for text: %.60s", request.text)
    try:
        return predict_priority_ml(request.text)
    except Exception as e:
        logger.error("ML prediction failed: %s", e)
        raise HTTPException(status_code=500, detail="ML prediction failed")
