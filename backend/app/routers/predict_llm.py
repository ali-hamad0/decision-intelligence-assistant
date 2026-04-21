import logging

from fastapi import APIRouter, HTTPException

from app.schemas.prediction import LLMPredictionResponse
from app.schemas.query import QueryRequest
from app.services.llm_client import predict_priority_llm

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/llm", response_model=LLMPredictionResponse)
def predict_llm(request: QueryRequest) -> LLMPredictionResponse:
    logger.info("LLM prediction request: %.60s", request.text)
    try:
        return predict_priority_llm(request.text)
    except Exception as e:
        logger.error("LLM prediction failed: %s", e)
        raise HTTPException(status_code=500, detail="LLM prediction failed")
