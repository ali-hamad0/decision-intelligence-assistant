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

**Why no separate vector-db container?**
Chroma runs in persistent mode (embedded, not client-server). The embeddings are stored as files inside the container and persisted via a named Docker volume (`chroma_data`). A separate container would add network overhead and operational complexity for no benefit at this scale — 5,000 tickets fit comfortably in-process.

---

## Quick start (Docker)

```bash
# 1. Copy and fill in your Groq API key
cp .env.example .env
#    GROQ_API_KEY=gsk-...

# 2. Build and start all services
docker compose up --build

# Frontend →  http://localhost:5173
# Backend  →  http://localhost:8000/docs
```

**Stop the stack**
```bash
docker compose down
```

**Rebuild from scratch** (re-downloads dependencies, clears named volumes)
```bash
docker compose down --volumes
docker compose up --build
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

## Design decisions

### RAG vs LLM-only — written analysis

RAG consistently produces more grounded answers. When a user asks "my order hasn't arrived, what do I do?", the LLM-only path answers generically from training data. The RAG path retrieves 3 real past tickets with similar complaints and builds its answer around concrete precedents — the response references the actual steps that worked for those customers.

The trade-off: RAG costs more (one embedding lookup + longer prompt = higher token count) and is slower (~200–400ms extra latency for retrieval). For a support assistant where answer quality matters more than raw speed, RAG is the right default. LLM-only is useful when retrieval returns low-similarity results (similarity score < 0.1) — in that case, the retrieved context adds noise, not signal.

### Why Random Forest over Logistic Regression + TF-IDF

LR + TF-IDF scores 94% accuracy but this is dishonest: it directly reads the urgency keywords from the raw text — the same keywords we used to create the labels. It is learning our rule, not learning urgency. The Random Forest on 7 engineered features scores 70%, but those features capture real signals (emotional intensity, tone, frustration markers) that generalise better to unseen language. See notebook Section 5 for the full comparison.

### Why Chroma (no separate vector-db container)

Chroma runs in persistent mode — no server process, no network call, just files on disk. The 5,000-ticket store fits in 7 MB. A separate container (Qdrant, Weaviate) would add network overhead, a health-check dependency, and operational complexity for no measurable benefit at this scale.

---

## Known limitations

- **Weak supervision leakage**: the ML model partly learns the labeling rule (keyword detection) rather than true urgency. Accuracy on genuinely ambiguous tickets is lower than the headline 70%. Documented honestly in notebook Section 9.
- **Small RAG corpus**: only 5,000 tickets are indexed. Similarity scores are often low (0.1–0.3) because the corpus cannot cover every topic. A larger index would improve retrieval relevance.
- **LLM accuracy not measured on full test set**: running 180,000 Groq API calls would cost ~$18 and take hours. The LLM accuracy shown in the comparison table is therefore not reported — only the ML model's 70% is a real measured number.
- **Ephemeral Docker volumes**: running `docker compose down --volumes` deletes the named volumes. The chroma_data is also baked into the Docker image (via `COPY chroma_data/`), so the next `docker compose up --build` restores it automatically.
- **VITE_API_BASE_URL is build-time**: changing the backend URL requires a frontend rebuild. For production, this would be handled by a reverse proxy.

---

## Environment variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `GROQ_MODEL` | Model ID (default: `llama-3.3-70b-versatile`) |
| `GROQ_BASE_URL` | Groq base URL |
| `VITE_API_BASE_URL` | Backend URL seen by the browser |
