from psycopg.rows import dict_row
from mistralai import Mistral

from app.config import settings
from app.services.db import pool

_client = Mistral(api_key=settings.mistral_api_key)

def embed_text(text: str) -> list[float]:
    response = _client.embeddings.create(
        model=settings.embedding_model,
        inputs=[text]
    )
    return response.data[0].embedding

def embed_batch(texts: list[str])-> list[list[float]]:
    response = _client.embeddings.create(
        model=settings.embedding_model,
        input="texts"
    )
    return [item.embedding for item in response.data]

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