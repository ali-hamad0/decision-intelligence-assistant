from pydantic import BaseModel

from app.schemas.prediction import LLMPredictionResponse, MLPredictionResponse


class RAGResponse(BaseModel):
    answer: str
    sources: list[dict]
    latency_ms: float
    cost_usd: float


class LLMOnlyResponse(BaseModel):
    answer: str
    latency_ms: float
    cost_usd: float


class ComparisonResponse(BaseModel):
    rag: RAGResponse                  # Comparison 1 — LLM with retrieved context
    llm: LLMOnlyResponse              # Comparison 1 — LLM alone (no context)
    ml_prediction: MLPredictionResponse   # Comparison 2 — trained ML classifier
    llm_prediction: LLMPredictionResponse # Comparison 2 — LLM zero-shot priority
