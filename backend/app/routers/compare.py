import asyncio
import logging

from fastapi import APIRouter, HTTPException

from app.schemas.comparison import ComparisonResponse, LLMOnlyResponse, RAGResponse
from app.schemas.query import QueryRequest
from app.services.llm_client import answer_query, predict_priority_llm
from app.services.ml_model import predict_priority_ml
from app.services.vector_store import LOW_SIMILARITY_THRESHOLD, retrieve

logger = logging.getLogger(__name__)

router = APIRouter(tags=["compare"])


@router.post("/compare", response_model=ComparisonResponse)
async def compare(request: QueryRequest) -> ComparisonResponse:
    """
    Four-way comparison for every query:
      1. RAG answer       — LLM with retrieved context       (Comparison 1)
      2. LLM-only answer  — LLM alone, no context            (Comparison 1)
      3. ML prediction    — trained Random Forest classifier  (Comparison 2)
      4. LLM prediction   — LLM zero-shot priority label      (Comparison 2)
    """
    logger.info("Compare request: %.60s", request.text)
    try:
        # Run retrieval, LLM-only answer, and both priority predictions in parallel
        sources, llm_result, ml_pred, llm_pred = await asyncio.gather(
            asyncio.to_thread(retrieve, request.text),
            asyncio.to_thread(answer_query, request.text),
            asyncio.to_thread(predict_priority_ml, request.text),
            asyncio.to_thread(predict_priority_llm, request.text),
        )

        # RAG answer uses the sources retrieved above
        source_texts = [s["text"] for s in sources]
        rag_answer, rag_latency, rag_cost = await asyncio.to_thread(
            answer_query, request.text, source_texts
        )

        llm_answer, llm_latency, llm_cost = llm_result

        best_score = max((s["similarity_score"] for s in sources), default=0.0)
        low_similarity = best_score < LOW_SIMILARITY_THRESHOLD
        if low_similarity:
            logger.warning(
                "Low similarity retrieval (best=%.3f < threshold=%.2f) — RAG context may be off-topic",
                best_score,
                LOW_SIMILARITY_THRESHOLD,
            )

        return ComparisonResponse(
            rag=RAGResponse(
                answer=rag_answer,
                sources=sources,
                low_similarity=low_similarity,
                latency_ms=rag_latency,
                cost_usd=rag_cost,
            ),
            llm=LLMOnlyResponse(
                answer=llm_answer,
                latency_ms=llm_latency,
                cost_usd=llm_cost,
            ),
            ml_prediction=ml_pred,
            llm_prediction=llm_pred,
        )
    except Exception as e:
        logger.error("Compare failed: %s", e)
        raise HTTPException(status_code=500, detail="Compare request failed")
