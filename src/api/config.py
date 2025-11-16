from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Gemini
    gemini_api_key: str
    
    # API Settings
    api_title: str = "Context API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list[str] = ["*"]
    
    # Railway
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

