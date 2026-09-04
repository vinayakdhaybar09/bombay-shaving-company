import psycopg
from app.config import settings

with open("ingestion/db_schema.sql") as file:
    sql = file.read()

with psycopg.connect(settings.database_url) as conn:
    with conn.cursor() as cur:
        cur.execute(sql)

print("Database schema created successfully!")