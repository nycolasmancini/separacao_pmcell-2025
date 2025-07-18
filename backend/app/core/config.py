import os
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
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    ALLOWED_ORIGINS: Optional[str] = None
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./pmcell.db")
    MAX_CONNECTIONS: int = 20
    CONNECTION_TIMEOUT: int = 30
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Admin
    ADMIN_PASSWORD: str = "thmpv321"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # "text" or "json"
    
    # Caching
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour default
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }
    
    def get_cors_origins(self) -> list[str]:
        """Get CORS origins based on environment"""
        if self.ALLOWED_ORIGINS:
            # Production: use specific origins
            origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
            return origins
        else:
            # Development: use default localhost origins
            return self.BACKEND_CORS_ORIGINS


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()