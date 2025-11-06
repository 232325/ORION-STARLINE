"""
AI Trading System - Cache Manager
Redis va in-memory caching xizmati
"""

import asyncio
import json
import time
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import logging
from cachetools import TTLCache
import aioredis
import pickle

from ..config.settings import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """Cache boshqaruvchisi"""
    
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.memory_cache = TTLCache(maxsize=settings.CACHE_MAX_SIZE, ttl=settings.CACHE_TTL)
        self.is_connected = False
    
    async def initialize(self):
        """Cache tizimini boshlash"""
        try:
            # Redis connection
            redis_url = settings.REDIS_URL
            self.redis_client = aioredis.from_url(redis_url)
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("Redis cache muvaffaqiyatli ulandi")
            
            # Set default TTL for different data types
            await self._setup_cache_configurations()
            
        except Exception as e:
            logger.warning(f"Redis ga ulanishda xato: {e}. In-memory cache ishlatilmoqda")
            self.is_connected = False
    
    async def _setup_cache_configurations(self):
        """Cache konfiguratsiyasini o'rnatish"""
        if not self.is_connected:
            return
        
        try:
            # Set default configurations
            await self.redis_client.set("cache:default_ttl", str(settings.CACHE_TTL))
            await self.redis_client.set("cache:max_size", str(settings.CACHE_MAX_SIZE))
            
            logger.info("Cache konfiguratsiyasi o'rnatildi")
        except Exception as e:
            logger.error(f"Cache konfiguratsiya xatosi: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Ma'lumotni cache'dan olish"""
        try:
            # Try Redis first if connected
            if self.is_connected:
                value = await self.redis_client.get(key)
                if value is not None:
                    return pickle.loads(value)
            
            # Fallback to memory cache
            return self.memory_cache.get(key)
            
        except Exception as e:
            logger.error(f"Cache'dan olish xatosi ({key}): {e}")
            return self.memory_cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Ma'lumotni cache'ga saqlash"""
        try:
            ttl = ttl or settings.CACHE_TTL
            
            # Store in Redis if connected
            if self.is_connected:
                await self.redis_client.setex(
                    key,
                    ttl,
                    pickle.dumps(value)
                )
            
            # Always store in memory cache as backup
            self.memory_cache[key] = value
            
            return True
            
        except Exception as e:
            logger.error(f"Cache'ga saqlash xatosi ({key}): {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Ma'lumotni cache'dan o'chirish"""
        try:
            # Delete from Redis if connected
            if self.is_connected:
                await self.redis_client.delete(key)
            
            # Remove from memory cache
            self.memory_cache.pop(key, None)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache'dan o'chirish xatosi ({key}): {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Ma'lumot mavjudligini tekshirish"""
        try:
            # Check Redis first
            if self.is_connected:
                exists_redis = await self.redis_client.exists(key)
                if exists_redis:
                    return True
            
            # Check memory cache
            return key in self.memory_cache
            
        except Exception as e:
            logger.error(f"Cache mavjudlik tekshirish xatosi ({key}): {e}")
            return key in self.memory_cache
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Pattern bo'yicha cache ma'lumotlarini o'chirish"""
        try:
            deleted_count = 0
            
            # Clear memory cache patterns
            keys_to_delete = []
            for key in self.memory_cache.keys():
                if pattern.replace("*", "") in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                self.memory_cache.pop(key, None)
                deleted_count += 1
            
            # Clear Redis patterns if connected
            if self.is_connected:
                redis_keys = await self.redis_client.keys(pattern)
                if redis_keys:
                    deleted_redis = await self.redis_client.delete(*redis_keys)
                    deleted_count += deleted_redis
            
            logger.info(f"Pattern '{pattern}' bo'yicha {deleted_count} cache entry o'chirildi")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Pattern invalidatsiya xatosi ({pattern}): {e}")
            return 0
    
    async def clear_all(self) -> bool:
        """Barcha cache ma'lumotlarini tozalash"""
        try:
            # Clear memory cache
            self.memory_cache.clear()
            
            # Clear Redis if connected
            if self.is_connected:
                await self.redis_client.flushdb()
            
            logger.info("Barcha cache ma'lumotlari tozalandi")
            return True
            
        except Exception as e:
            logger.error(f"Cache tozalash xatosi: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Cache statistik ma'lumotlari"""
        try:
            stats = {
                "memory_cache": {
                    "size": len(self.memory_cache),
                    "max_size": settings.CACHE_MAX_SIZE,
                    "ttl": settings.CACHE_TTL,
                    "hit_rate": getattr(self.memory_cache, 'hit_rate', 0.0)
                },
                "redis_cache": {
                    "connected": self.is_connected,
                    "info": {}
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Get Redis stats if connected
            if self.is_connected:
                redis_info = await self.redis_client.info()
                stats["redis_cache"]["info"] = {
                    "used_memory": redis_info.get("used_memory_human"),
                    "connected_clients": redis_info.get("connected_clients"),
                    "total_commands_processed": redis_info.get("total_commands_processed"),
                    "keyspace_hits": redis_info.get("keyspace_hits"),
                    "keyspace_misses": redis_info.get("keyspace_misses")
                }
                
                # Calculate hit rate
                hits = redis_info.get("keyspace_hits", 0)
                misses = redis_info.get("keyspace_misses", 0)
                total_requests = hits + misses
                if total_requests > 0:
                    stats["redis_cache"]["hit_rate"] = hits / total_requests
            
            return stats
            
        except Exception as e:
            logger.error(f"Cache statistika olish xatosi: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def warm_up_cache(self):
        """Cache'ni qizdirish - muhim ma'lumotlarni oldindan yuklash"""
        try:
            logger.info("Cache qizdirish boshlandi...")
            
            # Warm up common data
            warm_up_keys = [
                "system:status",
                "market:overview",
                "trading:pairs",
                "user:preferences",
                "config:settings"
            ]
            
            for key in warm_up_keys:
                if not await self.exists(key):
                    # Mock data for demonstration
                    mock_data = {
                        "key": key,
                        "data": f"Mock data for {key}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await self.set(key, mock_data, ttl=3600)  # 1 hour
            
            logger.info("Cache qizdirish yakunlandi")
            
        except Exception as e:
            logger.error(f"Cache qizdirish xatosi: {e}")
    
    async def cleanup(self):
        """Cache tizimini tozalash"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis connection yopildi")
            
            self.memory_cache.clear()
            logger.info("Memory cache tozalandi")
            
        except Exception as e:
            logger.error(f"Cache cleanup xatosi: {e}")
    
    # Context manager support
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

# Global cache manager instance
cache_manager = CacheManager()

# Cache decorators
def cached(ttl: int = 3600, key_prefix: str = ""):
    """Cache decorator for functions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Store in cache
            await cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {cache_key}, stored result")
            
            return result
        return wrapper
    return decorator

# Cache utilities
async def get_or_set_cache(key: str, fetch_func, ttl: int = 3600) -> Any:
    """Cache'dan olish yoki yo'q bo'lsa, bajarish va saqlash"""
    # Try to get from cache
    cached_data = await cache_manager.get(key)
    if cached_data is not None:
        return cached_data
    
    # Fetch fresh data
    fresh_data = await fetch_func() if asyncio.iscoroutinefunction(fetch_func) else fetch_func()
    
    # Store in cache
    await cache_manager.set(key, fresh_data, ttl)
    
    return fresh_data

async def invalidate_user_cache(user_id: str):
    """Foydalanuvchi bilan bog'liq cache ma'lumotlarini o'chirish"""
    patterns = [
        f"user:{user_id}:*",
        f"trading:{user_id}:*",
        f"settings:{user_id}:*",
        f"portfolio:{user_id}:*"
    ]
    
    total_deleted = 0
    for pattern in patterns:
        deleted = await cache_manager.invalidate_pattern(pattern)
        total_deleted += deleted
    
    logger.info(f"User {user_id} cache entries o'chirildi: {total_deleted}")
    return total_deleted

async def cache_market_data(symbol: str, data: Dict[str, Any]):
    """Market ma'lumotlarini cache'ga saqlash"""
    key = f"market:data:{symbol}"
    ttl = 300  # 5 minutes for market data
    await cache_manager.set(key, data, ttl)

async def get_cached_market_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Market ma'lumotlarini cache'dan olish"""
    key = f"market:data:{symbol}"
    return await cache_manager.get(key)

async def cache_trading_signals(data: List[Dict[str, Any]]):
    """Trading signals'ni cache'ga saqlash"""
    key = "trading:signals:latest"
    ttl = 600  # 10 minutes for signals
    await cache_manager.set(key, data, ttl)

async def get_cached_trading_signals() -> Optional[List[Dict[str, Any]]]:
    """Trading signals'ni cache'dan olish"""
    key = "trading:signals:latest"
    return await cache_manager.get(key)

# Initialize cache on module import
logger.info("Cache Manager moduli yuklandi")