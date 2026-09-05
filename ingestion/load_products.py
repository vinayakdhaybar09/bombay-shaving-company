import json
from app.services.db import pool

with open("assets/bombay-shaving-product-data.json") as f:
    data = json.load(f)

rows = []

for category in data["categories"]:
    for p in category["products"]:
        rows.append((
            p["id"], p["category"], p["name"], p.get("url"), p.get("image_url"),
            json.dumps(p.get("images", [])), p.get("description"),
            p.get("price"), p.get("original_price"), p.get("discount_percentage"),
            p.get("rating"), p.get("review_count"),
            json.dumps(p.get("features", [])),
            json.dumps(p.get("detailed_information", {})),
            p.get("specifications", {}).get("sku"),
            p.get("availability", {}).get("status"),
            json.dumps(p.get("source", {})),
        ))

with pool.connection() as conn:
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO products (id, category, name, url, image_url, images, description,
                                price, original_price, discount_percentage, rating, review_count,
                                features, detailed_information, sku, availability_status, source)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id) DO UPDATE SET
                price = EXCLUDED.price, availability_status = EXCLUDED.availability_status
            """,
            rows,
        )
    conn.commit()

print(f"Loaded {len(rows)} products.")
pool.close()