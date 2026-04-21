# Decision Intelligence Assistant

A full-stack AI application that runs **two side-by-side comparisons** for every support ticket:

| Comparison | Option A | Option B |
|---|---|---|
| **Answer quality** | RAG (retrieved context + LLM) | LLM-only (no retrieval) |
| **Priority prediction** | ML classifier (Random Forest) | LLM zero-shot (Llama 3.3 70B) |

Built for Week 3 of the AIE Bootcamp.

---

## Architecture

```
frontend/   React + Vite  →  submits ticket text
backend/    FastAPI        →  four async tasks via asyncio.gather
  ├── services/vector_store.py   Chroma + sentence-transformers
  ├── services/llm_client.py     Groq (OpenAI-compatible)
  └── services/ml_model.py       Random Forest (joblib)
notebooks/  Training + evaluation notebook
```

---

## Quick start (Docker)

```bash
# 1. Copy and fill in your Groq API key
cp .env.example .env
#    GROQ_API_KEY=gsk-...

# 2. Build and run
docker compose up --build

# Frontend →  http://localhost:5173
# Backend  →  http://localhost:8000/docs
```

---

## Local development

**Backend**

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/compare` | Four-way comparison (main endpoint) |
| `POST` | `/predict/ml` | ML classifier only |
| `POST` | `/predict/llm` | LLM zero-shot only |
| `POST` | `/rag` | RAG answer only |
| `POST` | `/llm` | LLM-only answer |

Interactive docs: `http://localhost:8000/docs`

---

## ML model

The Random Forest classifier is trained in `notebooks/notebook.ipynb`.

**Features (7):** `text_length`, `exclamation_count`, `uppercase_ratio`, `multiple_punctuation`, `sentiment_compound`, `sentiment_neg`, `negation_count`

**Labels:** `urgent` / `normal` via weak supervision (keyword rules + punctuation signals)

**Results on held-out test set:**

| Model | Accuracy |
|---|---|
| Dummy (majority) | ~68% |
| Logistic Regression + TF-IDF | ~72% |
| **Random Forest + Engineered (production)** | **~70%** |
| Random Forest + TF-IDF | ~92%* |
| Gradient Boosting + Engineered | ~69% |

*TF-IDF model learns the labeling keywords directly — high accuracy is not genuine generalisation. The engineered-features model is more honest and defensible.

---

## Environment variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `GROQ_MODEL` | Model ID (default: `llama-3.3-70b-versatile`) |
| `GROQ_BASE_URL` | Groq base URL |
| `VITE_API_BASE_URL` | Backend URL seen by the browser |
