from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url : str
    mistral_api_key : str
    embedding_model : str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim : int = 384

    class config:
        env_file = ".env"

settings = Settings()