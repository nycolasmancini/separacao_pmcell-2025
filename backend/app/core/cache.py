"""
Cache configuration and utilities for Redis caching
"""
import json
import pickle
from typing import Any, Optional, Union
from functools import wraps
import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Redis connection instance
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client instance"""
    global _redis_client
    
    if _redis_client is None:
        try:
            # Only create Redis client in production
            if settings.ENVIRONMENT == "production":
                redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379')
                _redis_client = redis.from_url(redis_url, decode_responses=False)
                
                # Test connection
                await _redis_client.ping()
                logger.info("Redis connection established")
            else:
                logger.info("Redis disabled in development mode")
                return None
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            _redis_client = None
    
    return _redis_client


async def close_redis_client():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


class Cache:
    """Cache utilities with Redis backend"""
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        client = await get_redis_client()
        if not client:
            return None
            
        try:
            value = await client.get(key)
            if value:
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        
        return None
    
    @staticmethod
    async def set(key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL in seconds"""
        client = await get_redis_client()
        if not client:
            return False
            
        try:
            serialized = pickle.dumps(value)
            await client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    @staticmethod
    async def delete(key: str) -> bool:
        """Delete key from cache"""
        client = await get_redis_client()
        if not client:
            return False
            
        try:
            await client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    @staticmethod
    async def delete_pattern(pattern: str) -> int:
        """Delete keys matching pattern"""
        client = await get_redis_client()
        if not client:
            return 0
            
        try:
            keys = await client.keys(pattern)
            if keys:
                return await client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0


def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = await Cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            # Cache the result
            await Cache.set(cache_key, result, ttl)
            logger.debug(f"Cache set for {cache_key}")
            
            return result
        
        return wrapper
    return decorator


# Common cache keys
class CacheKeys:
    """Common cache key patterns"""
    
    ORDERS_LIST = "orders:list"
    ORDER_DETAIL = "order:detail:{order_id}"
    ORDER_STATS = "orders:stats"
    USER_PROFILE = "user:profile:{user_id}"
    PDF_PARSED = "pdf:parsed:{file_hash}"
    
    @staticmethod
    def orders_list_key(page: int = 1, status: str = "", user_id: int = None) -> str:
        """Generate key for orders list"""
        return f"orders:list:page_{page}:status_{status}:user_{user_id}"
    
    @staticmethod
    def order_detail_key(order_id: int) -> str:
        """Generate key for order detail"""
        return f"order:detail:{order_id}"
    
    @staticmethod
    def pdf_cache_key(file_content: bytes) -> str:
        """Generate key for PDF parsing cache"""
        import hashlib
        file_hash = hashlib.md5(file_content).hexdigest()
        return f"pdf:parsed:{file_hash}"


# Cache invalidation helpers
class CacheInvalidator:
    """Helper class for cache invalidation"""
    
    @staticmethod
    async def invalidate_orders_cache():
        """Invalidate all orders-related cache"""
        await Cache.delete_pattern("orders:*")
        await Cache.delete_pattern("order:*")
    
    @staticmethod
    async def invalidate_order_cache(order_id: int):
        """Invalidate specific order cache"""
        await Cache.delete(CacheKeys.order_detail_key(order_id))
        await Cache.delete_pattern("orders:list:*")
        await Cache.delete(CacheKeys.ORDER_STATS)
    
    @staticmethod
    async def invalidate_user_cache(user_id: int):
        """Invalidate user-related cache"""
        await Cache.delete(f"user:profile:{user_id}")
        await Cache.delete_pattern("orders:list:*")