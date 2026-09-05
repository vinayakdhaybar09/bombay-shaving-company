CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Source of truth product data (from bombay-shaving-product-data.json)
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    url TEXT,
    image_url TEXT,
    images JSONB,
    description TEXT,
    price NUMERIC,
    original_price NUMERIC,
    discount_percentage NUMERIC,
    rating NUMERIC,
    review_count INTEGER,
    features JSONB,
    detailed_information JSONB,   -- about_the_product, how_to_use, ingredients,
                                   -- benefits, key_features, manufacturing_information, faqs
    sku TEXT,
    availability_status TEXT,
    source JSONB
);

-- Trigram index for fuzzy name matching (entity resolution)
CREATE INDEX IF NOT EXISTS idx_products_name_trgm
    ON products USING gin (name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);
CREATE INDEX IF NOT EXISTS idx_products_price ON products (price);

-- Enrichment data + embeddings (from products-enriched.json)
CREATE TABLE IF NOT EXISTS product_embeddings (
    product_id TEXT PRIMARY KEY REFERENCES products (id),
    skin_type TEXT[],
    hair_beard_concern TEXT[],
    concern_tags TEXT[],
    other_tags TEXT[],
    gender_target TEXT,
    product_type_normalized TEXT,
    routine_step TEXT[],
    usage_frequency TEXT,
    price_tier TEXT,
    key_ingredients TEXT[],
    short_benefit_summary TEXT,
    searchable_text TEXT,
    embedding VECTOR(1024)
);

CREATE INDEX IF NOT EXISTS idx_product_embeddings_vec
    ON product_embeddings USING hnsw (embedding vector_cosine_ops);

-- Blog chunks (from blogs-chunks-data.json)
CREATE TABLE IF NOT EXISTS blog_chunks (
    id SERIAL PRIMARY KEY,
    blog_id TEXT NOT NULL,
    blog_title TEXT,
    blog_category TEXT,
    blog_url TEXT,
    heading TEXT,
    content TEXT,
    embedding VECTOR(1024)
);

CREATE INDEX IF NOT EXISTS idx_blog_chunks_vec
    ON blog_chunks USING hnsw (embedding vector_cosine_ops);

-- Company knowledge: FAQs, policies, contact info
-- (source file bsc-company-knowledge.json — see note in Phase 2)
CREATE TABLE IF NOT EXISTS company_knowledge (
    id SERIAL PRIMARY KEY,
    entry_type TEXT NOT NULL,   -- 'faq' | 'policy' | 'contact'
    category TEXT,
    question TEXT,
    answer TEXT NOT NULL,
    embedding VECTOR(1024)
);

CREATE INDEX IF NOT EXISTS idx_company_knowledge_vec
    ON company_knowledge USING hnsw (embedding vector_cosine_ops);