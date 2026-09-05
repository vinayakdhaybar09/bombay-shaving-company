import time
from mistralai.client import Mistral

from app.config import settings
from app.services.db import pool

_client = Mistral(api_key=settings.mistral_api_key)
_EMBED_MODEL = settings.embedding_model
_BATCH_SIZE = 64

def embed_text(text: str) -> list[float]:
    return embed_batch([text])[0]

def embed_batch(texts: list[str], max_retries: int = 3)-> list[list[float]]:
    all_vectors: list[list[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        chunk = texts[i : i + _BATCH_SIZE]
        for attempt in range(max_retries):
            try:
                response = _client.embeddings.create(model=_EMBED_MODEL, inputs=chunk)
                all_vectors.extend([d.embedding for d in response.data])
                break
            except Exception:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
    return all_vectors

def search_products(query_embedding: list[float], top_k: int = 15) -> list[dict]:
    with pool.connection() as conn:
        return conn.execute(
            """
            SELECT product_id, 1 - (embedding <=> %s::vector) AS similarity
            FROM product_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """, 
            (query_embedding, query_embedding, top_k)
        ).fetchall()

def search_blogs(query_embedding: list[float], top_k: 5) -> list[dict]:
    with pool.connection() as conn:
        return conn.execute(
            """
            SELECT blog_title, blog_url, heading, content, 1 - (embedding <=> %s::vector) AS similarity
            FROM blog_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, query_embedding, top_k)
        ).fetchall()

def search_company_knowledge(query_embedding: list[float], top_k: int = 3) -> list[dict]:
    with pool.connection() as conn:
        return conn.execute(
            """
            SELECT entry_type, question, answer, 1 - (embedding <=> %s::vector) AS similarity
            FROM company_knowledge
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, query_embedding, top_k)
        ).fetchall()