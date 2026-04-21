FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency manifests first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev extras)
ENV UV_HTTP_TIMEOUT=120
RUN uv sync --frozen --no-dev

# Copy application code and artefacts
COPY app/ ./app/
COPY models/ ./models/
COPY chroma_data/ ./chroma_data/

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
