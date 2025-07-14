"""
Health check endpoints for monitoring and load balancers
"""
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.core.cache import get_redis_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Store application start time
_start_time = time.time()


@router.get("/health")
async def health_check():
    """Basic health check for load balancers"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with dependencies"""
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": start_time,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    # Database health check
    try:
        result = await db.execute(text("SELECT 1"))
        db_latency = time.time() - start_time
        health_status["checks"]["database"] = {
            "status": "healthy",
            "latency_ms": round(db_latency * 1000, 2),
            "type": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Redis health check (if enabled)
    redis_client = await get_redis_client()
    if redis_client:
        try:
            redis_start = time.time()
            await redis_client.ping()
            redis_latency = time.time() - redis_start
            health_status["checks"]["redis"] = {
                "status": "healthy",
                "latency_ms": round(redis_latency * 1000, 2)
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            health_status["checks"]["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            # Redis is optional, don't mark overall as unhealthy
    else:
        health_status["checks"]["redis"] = {
            "status": "disabled",
            "message": "Redis not configured"
        }
    
    # Overall response time
    total_time = time.time() - start_time
    health_status["response_time_ms"] = round(total_time * 1000, 2)
    
    # Return appropriate status code
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check for Kubernetes-style deployments"""
    try:
        # Check if database is ready
        await db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": time.time(),
            "service": settings.APP_NAME
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": time.time()
            }
        )


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes-style deployments"""
    return {
        "status": "alive",
        "timestamp": time.time(),
        "service": settings.APP_NAME
    }


@router.get("/metrics")
async def basic_metrics():
    """Basic application metrics"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
        "uptime_seconds": time.time() - _start_time,
        # Add more metrics as needed
    }