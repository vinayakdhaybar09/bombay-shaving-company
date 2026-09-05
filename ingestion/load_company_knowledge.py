import json
from app.services.embeddings import embed_batch
from app.services.db import pool

with open("assets/bsc-company-knowledge.json") as f:
    data = json.load(f)

# Each entry: (entry_type, category, question, answer, text_to_embed)
entries: list[tuple[str, str | None, str | None, str, str]] = []

for faq in data.get("faqs", []):
    entries.append((
        "faq", faq.get("category"), faq["question"], faq["answer"],
        f"{faq['question']} {faq['answer']}",
    ))

for policy in data.get("policies", []):
    topic = policy.get("topic")
    entries.append((
        "policy", None, topic, policy["content"],
        policy.get("searchable_text") or f"{topic or ''} {policy['content']}",
    ))

# contact is a flat dict, not a list — iterate its key/value pairs directly
for channel, value in data.get("contact", {}).items():
    label = channel.replace("_", " ").title()  # e.g. "support_email" -> "Support Email"
    entries.append(("contact", None, label, str(value), f"{label}: {value}"))

for social in data.get("social_handles", []):
    label = f"{social['platform']}: {social['handle']}"
    entries.append(("social", None, label, social["url"], f"{label} {social['url']}"))

texts = [e[4] for e in entries]
vectors = embed_batch(texts)

rows = [(e[0], e[1], e[2], e[3], vec) for e, vec in zip(entries, vectors)]

with pool.connection() as conn:
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO company_knowledge (entry_type, category, question, answer, embedding)
            VALUES (%s,%s,%s,%s,%s)
            """,
            rows,
        )
    conn.commit()

counts = {t: sum(1 for e in entries if e[0] == t) for t in ("faq", "policy", "contact", "social")}
print(f"Loaded {len(rows)} company knowledge entries: {counts}")
pool.close()