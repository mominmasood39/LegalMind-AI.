"""Configuration settings for LegalMind-AI backend."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "LegalMind-AI"
    app_version: str = "1.0.0"
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    max_document_size_mb: int = 10
    demo_mode: bool = True  # When True, uses mock responses instead of real AI calls

    class Config:
        env_file = ".env"


settings = Settings()
