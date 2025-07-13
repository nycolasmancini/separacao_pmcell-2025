from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "PMCELL - Separação de Pedidos"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:5175",  # Para cobrir qualquer porta que o Vite usar
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./pmcell.db"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Admin
    ADMIN_PASSWORD: str = "thmpv321"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()