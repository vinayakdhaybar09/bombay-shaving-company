from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url : str
    mistral_api_key : str
    huggingfacehub_api_token: str
    embedding_model : str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim : int = 384

    model_config = SettingsConfigDict(
        env_file = ".env"
    )
    
settings = Settings()