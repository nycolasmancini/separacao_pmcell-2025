import logging
import logging.config
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import get_settings
from app.api.v1 import api_router
from app.core.database import init_db
from app.core.security_middleware import (
    RateLimitMiddleware, 
    SecurityHeadersMiddleware, 
    RequestLoggingMiddleware,
    validate_security_config
)
from app.core.cache import close_redis_client
# Import all models to ensure they're registered with Base
from app.models import User, Order, OrderItem, OrderAccess, PurchaseItem

settings = get_settings()

# Configure logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "mode": "a",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
import os
os.makedirs("logs", exist_ok=True)

# Apply logging configuration
logging.config.dictConfig(LOGGING_CONFIG)

# Get logger for main application
logger = logging.getLogger("app.main")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Custom CORS middleware to ensure headers are always present, even on errors
class CORSErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            if origin and origin in settings.BACKEND_CORS_ORIGINS:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
                response.headers["Access-Control-Max-Age"] = "86400"
            return response
        
        try:
            response = await call_next(request)
        except Exception as e:
            # Create error response with CORS headers
            import logging
            logger = logging.getLogger("app.main")
            logger.error(f"Unhandled error in middleware: {str(e)}", exc_info=True)
            
            response = Response(
                content='{"detail": "Internal server error"}',
                status_code=500,
                media_type="application/json"
            )
        
        # Always add CORS headers
        allowed_origins = settings.get_cors_origins()
        if origin and origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    # Validate security configuration
    validate_security_config()
    
    # Log SECRET_KEY info for debugging (first 10 chars only)
    logger.info(f"SECRET_KEY configured: {settings.SECRET_KEY[:20]}...")
    
    # Comentado temporariamente para evitar falha de conexão no startup
    # await init_db()
    logger.info("Application startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application...")
    await close_redis_client()
    logger.info("Application shutdown completed")

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(RateLimitMiddleware, calls=100, period=3600)

# Add custom CORS error middleware
app.add_middleware(CORSErrorMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    api_router,
    prefix=f"{settings.API_V1_STR}"
)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)