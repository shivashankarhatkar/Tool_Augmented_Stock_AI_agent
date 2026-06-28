"""Centralized application settings, loaded from environment variables / .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    #llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_provider: str = Field(default="gemini", alias="LLM_PROVIDER")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    # Tool API keys
    alpha_vantage_api_key: str = Field(default="", alias="ALPHA_VANTAGE_API_KEY")
    news_api_key: str = Field(default="", alias="NEWS_API_KEY")
    serpapi_api_key: str = Field(default="", alias="SERPAPI_API_KEY")

    # RAG
    chroma_db_path: str = Field(default="./data/chroma_db", alias="CHROMA_DB_PATH")
    books_dir: str = Field(default="./data/books", alias="BOOKS_DIR")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    rag_collection_name: str = Field(default="investing_books", alias="RAG_COLLECTION_NAME")
    rag_top_k: int = Field(default=4, alias="RAG_TOP_K")

    # App
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


settings = Settings()
