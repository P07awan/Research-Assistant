from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LangSmith Configuration
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_TRACING: str = ""
    LANGSMITH_ENDPOINT: str = ""
    langsmith_project: str = ""
    
    # Local storage configuration
    UPLOAD_DIR: str = "uploads"
    BACKEND_URL: str = "http://127.0.0.1:8000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create a global settings instance
settings = Settings()