from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import setup_logging
from app.routers import compare, health, llm, predict_llm, predict_ml, rag

setup_logging()

app = FastAPI(title="Decision Intelligence Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(predict_ml.router)
app.include_router(predict_llm.router)
app.include_router(rag.router)
app.include_router(llm.router)
app.include_router(compare.router)
