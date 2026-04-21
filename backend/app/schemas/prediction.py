from pydantic import BaseModel


class MLPredictionResponse(BaseModel):
    priority: str
    confidence: float
    latency_ms: float


class LLMPredictionResponse(BaseModel):
    priority: str
    reasoning: str
    latency_ms: float
    cost_usd: float
