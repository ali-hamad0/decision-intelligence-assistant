import json
import logging
import time
from functools import lru_cache

from openai import OpenAI

from app.core.config import get_settings
from app.schemas.prediction import LLMPredictionResponse

logger = logging.getLogger(__name__)

# Groq llama-3.3-70b-versatile pricing per million tokens
_INPUT_COST_PER_M = 0.59
_OUTPUT_COST_PER_M = 0.79


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(api_key=settings.groq_api_key, base_url=settings.groq_base_url)


def _calc_cost(prompt_tokens: int, completion_tokens: int) -> float:
    return round(
        prompt_tokens * _INPUT_COST_PER_M / 1_000_000
        + completion_tokens * _OUTPUT_COST_PER_M / 1_000_000,
        6,
    )


def predict_priority_llm(text: str) -> LLMPredictionResponse:
    client = _get_client()
    settings = get_settings()
    start = time.perf_counter()

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a customer support ticket classifier. "
                    "Classify the ticket as 'urgent' or 'normal'. "
                    "Respond with JSON only: "
                    '{"priority": "urgent" or "normal", "confidence": 0.0-1.0, "reasoning": "one sentence"}'
                ),
            },
            {"role": "user", "content": text},
        ],
    )

    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    cost_usd = _calc_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
    content = response.choices[0].message.content

    try:
        parsed = json.loads(content)
        priority = parsed.get("priority", "normal")
        confidence = float(parsed["confidence"]) if "confidence" in parsed else None
        reasoning = parsed.get("reasoning", "")
    except (json.JSONDecodeError, KeyError, ValueError):
        logger.warning("LLM returned non-JSON: %.100s", content)
        priority = "normal"
        confidence = None
        reasoning = content[:200]

    logger.info("LLM priority: %s conf=%.2f (%.0fms, $%.6f)", priority, confidence or 0, latency_ms, cost_usd)
    return LLMPredictionResponse(
        priority=priority,
        confidence=confidence,
        reasoning=reasoning,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
    )


def answer_query(text: str, sources: list[str] | None = None) -> tuple[str, float, float]:
    client = _get_client()
    settings = get_settings()
    start = time.perf_counter()

    if sources:
        context = "\n\n".join(f"- {s}" for s in sources)
        user_content = f"Context from past support tickets:\n{context}\n\nQuestion: {text}"
    else:
        user_content = text

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful customer support assistant. Answer the user's question clearly and concisely.",
            },
            {"role": "user", "content": user_content},
        ],
    )

    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    cost_usd = _calc_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
    answer = response.choices[0].message.content

    logger.info("LLM answer (%.0fms, $%.6f)", latency_ms, cost_usd)
    return answer, latency_ms, cost_usd
