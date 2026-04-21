from pydantic import BaseModel


class MLPredictionResponse(BaseModel):
    priority: str
    confidence: float
    latency_ms: float


class LLMPredictionResponse(BaseModel):
    priority: str
    confidence: float | None = None   # 0.0–1.0 self-reported by the LLM
    reasoning: str
    latency_ms: float
    cost_usd: float
