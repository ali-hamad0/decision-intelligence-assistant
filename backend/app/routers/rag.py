import logging

from fastapi import APIRouter, HTTPException

from app.schemas.comparison import RAGResponse
from app.schemas.query import QueryRequest
from app.services.llm_client import answer_query
from app.services.vector_store import retrieve

logger = logging.getLogger(__name__)

router = APIRouter(tags=["rag"])


@router.post("/rag", response_model=RAGResponse)
def rag_answer(request: QueryRequest) -> RAGResponse:
    logger.info("RAG request: %.60s", request.text)
    try:
        sources = retrieve(request.text)
        source_texts = [s["text"] for s in sources]
        answer, latency_ms, cost_usd = answer_query(request.text, sources=source_texts)
        return RAGResponse(answer=answer, sources=sources, latency_ms=latency_ms, cost_usd=cost_usd)
    except Exception as e:
        logger.error("RAG failed: %s", e)
        raise HTTPException(status_code=500, detail="RAG request failed")
