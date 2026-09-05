import json
from app.services.embeddings import embed_batch
from app. services.db import pool

with open("assets/products-enriched.json") as f:
    data = json.load(f)

all_products = [p for category in data for p in category["products"]]
texts = [p["searchable_text"] for p in all_products]
vectors = embed_batch(texts)

rows = []
for p, vec in zip(all_products, vectors):
    rows.append((
        p["product_id"], p.get("skin_type", []), p.get("hair_beard_concern", []),
        p.get("concern_tags", []), p.get("other_tags", []), p.get("gender_target"),
        p.get("product_type_normalized"), p.get("routine_step", []), p.get("usage_frequency"),
        p.get("price_tier"), p.get("key_ingredients", []), p.get("short_benefit_summary"),
        p["searchable_text"], vec,
    ))

with pool.connection() as conn:
    with conn.cursor() as cur:
        cur.executemany(
            """
                INSERT INTO product_embeddings (product_id, skin_type, hair_beard_concern, concern_tags,
                                            other_tags, gender_target, product_type_normalized,
                                            routine_step, usage_frequency, price_tier, key_ingredients,
                                            short_benefit_summary, searchable_text, embedding)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (product_id) DO UPDATE SET
                searchable_text = EXCLUDED.searchable_text, embedding = EXCLUDED.embedding
            """,
            rows,
        )
    conn.commit()

print(f"Embedded and loaded {len(rows)} products.")
pool.close()