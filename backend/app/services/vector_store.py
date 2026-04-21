import logging
from functools import lru_cache
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_CHROMA_PATH = Path(__file__).resolve().parents[2] / "chroma_data"
_COLLECTION_NAME = "support_tickets"
_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_TOP_K = 3


@lru_cache(maxsize=1)
def _get_collection() -> chromadb.Collection:
    logger.info("Loading Chroma collection from %s", _CHROMA_PATH)
    client = chromadb.PersistentClient(path=str(_CHROMA_PATH))
    return client.get_collection(_COLLECTION_NAME)


@lru_cache(maxsize=1)
def _get_embedder() -> SentenceTransformer:
    logger.info("Loading embedding model %s", _EMBED_MODEL)
    return SentenceTransformer(_EMBED_MODEL)


def retrieve(query: str) -> list[dict]:
    embedder = _get_embedder()
    collection = _get_collection()

    query_embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=_TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    sources = []
    for text, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        sources.append({
            "text": text,
            "priority": meta.get("priority", "unknown"),
            "similarity_score": round(1 - distance, 4),
        })

    logger.info(
        "Retrieved %d sources for query '%.50s' — scores: %s",
        len(sources),
        query,
        [s["similarity_score"] for s in sources],
    )
    return sources
