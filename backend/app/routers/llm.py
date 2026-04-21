import logging

from fastapi import APIRouter, HTTPException

from app.schemas.comparison import LLMOnlyResponse
from app.schemas.query import QueryRequest
from app.services.llm_client import answer_query

logger = logging.getLogger(__name__)

router = APIRouter(tags=["llm"])


@router.post("/llm", response_model=LLMOnlyResponse)
def llm_answer(request: QueryRequest) -> LLMOnlyResponse:
    logger.info("LLM-only request: %.60s", request.text)
    try:
        answer, latency_ms, cost_usd = answer_query(request.text, sources=None)
        return LLMOnlyResponse(answer=answer, latency_ms=latency_ms, cost_usd=cost_usd)
    except Exception as e:
        logger.error("LLM-only failed: %s", e)
        raise HTTPException(status_code=500, detail="LLM request failed")
