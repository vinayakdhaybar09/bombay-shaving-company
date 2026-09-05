import json
from app.services.embeddings import embed_batch
from app.services.db import pool

with open("assets/blogs-chunks-data.json") as f:
    data = json.load(f)

rows_input = []
for blog in data["blogs"]:
    for chunk in blog["chunks"]:
        rows_input.append((blog, chunk))

texts = [c.get("searchable_text") or f"{c['heading']}\n{c['content']}" for _, c in rows_input]
vectors = embed_batch(texts)

rows = []
for (blog, chunk), vec in zip(rows_input, vectors):
    rows.append((
        blog["id"], blog["title"], blog["category"], blog["url"],
        chunk["heading"], chunk["content"], vec,
    ))

with pool.connection() as conn:
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO blog_chunks (blog_id, blog_title, blog_category, blog_url, heading, content, embedding)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            rows,
        )
    conn.commit()

print(f"Loaded {len(rows)} blog chunks.")
pool.close()