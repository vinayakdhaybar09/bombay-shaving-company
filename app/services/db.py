import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import settings

pool = ConnectionPool(settings.database_url, min_size=1, max_size=5, kwargs={"row_factory": dict_row})

def fetch_products_by_ids(product_ids: list[str]) -> list[dict]:
    """The core 'verified facts' fetch - used by every specialist."""
    if not product_ids:
        return[]
    with pool.connection() as conn:
        rows = conn.execute(
            "SELECT * FROM products WHERE id = ANY(%s)", (product_ids,),
        ).fetchall()
    return rows


def fetch_products_by_filters(category: str | None = None, price_max: float | None = None, in_stock_only: bool = True, limit: int = 20) -> list[dict]:
    """Hard-constraint filtering - used before / alongside sementic search."""
    clauses, params = [], []
    if category: 
        clauses.append("category ILIKE %s")
        params.append(category)
    if price_max is not None:
        clauses.append("price <= %s")
        params.append(price_max)
    if in_stock_only:
        clauses.append("availability_status = 'in_stock'")
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"SELECT * FROM products {where} ORDER BY rating DESC NULLS LAST LIMIT %s"
    params.append(limit)
    with pool.connection() as conn:
        return conn.execute(query, params).fetchall()

def fetch_categories() -> list[dict]:
    with pool.connection() as conn:
        return conn.execute(
            "SELECT category, COUNT(*) AS product_count FROM products GROUP BY category ORDER BY product_count DESC"
        ).fetchall()