"""
Orion Starline Cache Sistemi
============================

Bu fayl Redis asosida caching strategiyalari va
performans optimizatsiyasi uchun cache tizimini o'z ichiga oladi.
"""

import asyncio
import json
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
from contextlib import asynccontextmanager
import pickle


class CacheStrategy(Enum):
    """Cache strategiyalari"""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"
    CACHE_ASIDE = "cache_aside"
    READ_THROUGH = "read_through"


class InvalidationStrategy(Enum):
    """Cache invalidation strategiyalari"""
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    MANUAL = "manual"
    LRU = "lru"
    LFU = "lfu"


@dataclass
class CacheConfig:
    """Cache konfiguratsiyasi"""
    name: str
    strategy: CacheStrategy
    ttl: int = 300  # 5 daqiqa default
    max_size: int = 10000
    compression: bool = True
    serialization_format: str = "json"  # json, pickle
    invalidation: InvalidationStrategy = InvalidationStrategy.TIME_BASED


@dataclass
class CacheStats:
    """Cache statistikasi"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    current_size: int = 0
    hit_rate: float = 0.0


class CacheKeyGenerator:
    """Cache kalitlari yaratish uchun generator"""
    
    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        """Kalit yaratish"""
        # Args va kwargs ni string ga o'girish
        key_parts = [prefix]
        
        for arg in args:
            key_parts.append(str(arg))
        
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        key_string = "|".join(key_parts)
        
        # Hash qilish (uzun kalitlar uchun)
        if len(key_string) > 200:
            return f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()[:16]}"
        
        return key_string
    
    @staticmethod
    def generate_user_key(user_id: str, resource: str, **params) -> str:
        """Foydalanuvchi kaliti"""
        return CacheKeyGenerator.generate_key(f"user:{user_id}", resource, **params)
    
    @staticmethod
    def generate_market_key(symbol: str, timeframe: str, **params) -> str:
        """Bozor kaliti"""
        return CacheKeyGenerator.generate_key(f"market:{symbol}", timeframe, **params)
    
    @staticmethod
    def generate_session_key(session_id: str) -> str:
        """Session kaliti"""
        return f"session:{session_id}"


class CacheSerializer:
    """Cache ma'lumotlarini serializatsiya qilish"""
    
    @staticmethod
    def serialize(data: Any, format: str = "json") -> bytes:
        """Ma'lumotlarni serializatsiya qilish"""
        if format == "json":
            return json.dumps(data, default=str).encode()
        elif format == "pickle":
            return pickle.dumps(data)
        else:
            raise ValueError(f"Unsupported serialization format: {format}")
    
    @staticmethod
    def deserialize(data: bytes, format: str = "json") -> Any:
        """Ma'lumotlarni deserializatsiya qilish"""
        if format == "json":
            return json.loads(data.decode())
        elif format == "pickle":
            return pickle.loads(data)
        else:
            raise ValueError(f"Unsupported serialization format: {format}")


class DistributedCache:
    """Taqsimlangan cache tizimi"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", db: int = 0):
        self.redis_client = redis.from_url(redis_url, db=db)
        self.logger = logging.getLogger(__name__)
        self.configs: Dict[str, CacheConfig] = {}
        self.stats: Dict[str, CacheStats] = {}
        
    def register_cache(self, config: CacheConfig):
        """Cache konfiguratsiyasini ro'yxatga olish"""
        self.configs[config.name] = config
        self.stats[config.name] = CacheStats()
        self.logger.info(f"Cache registered: {config.name}")
    
    async def get(self, key: str, cache_name: str = "default") -> Optional[Any]:
        """Cache dan olish"""
        try:
            config = self.configs.get(cache_name)
            if not config:
                return None
            
            # Redis dan olish
            cached_data = await self.redis_client.get(key)
            if cached_data is None:
                self.stats[cache_name].misses += 1
                return None
            
            # Deserializatsiya
            data = CacheSerializer.deserialize(cached_data, config.serialization_format)
            self.stats[cache_name].hits += 1
            
            return data
            
        except Exception as e:
            self.logger.error(f"Cache get xatolik: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        cache_name: str = "default"
    ) -> bool:
        """Cache ga saqlash"""
        try:
            config = self.configs.get(cache_name)
            if not config:
                return False
            
            # TTL belgilash
            if ttl is None:
                ttl = config.ttl
            
            # Serializatsiya
            serialized_data = CacheSerializer.serialize(value, config.serialization_format)
            
            # Redis ga saqlash
            await self.redis_client.setex(key, ttl, serialized_data)
            
            # Size statistikasi
            self.stats[cache_name].current_size = await self.redis_client.dbsize()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache set xatolik: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Cache dan o'chirish"""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            self.logger.error(f"Cache delete xatolik: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Pattern bo'yicha tozalash"""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            self.logger.error(f"Pattern clear xatolik: {e}")
            return 0
    
    async def get_stats(self, cache_name: str) -> Optional[CacheStats]:
        """Cache statistikasini olish"""
        stats = self.stats.get(cache_name)
        if stats and stats.hits + stats.misses > 0:
            total_requests = stats.hits + stats.misses
            stats.hit_rate = stats.hits / total_requests
        return stats
    
    async def invalidate_user_cache(self, user_id: str):
        """Foydalanuvchi cache ni invalidatsiya qilish"""
        pattern = f"user:{user_id}:*"
        deleted_count = await self.clear_pattern(pattern)
        self.logger.info(f"User cache invalidated for {user_id}: {deleted_count} keys")
    
    async def invalidate_market_cache(self, symbol: str):
        """Bozor cache ni invalidatsiya qilish"""
        pattern = f"market:{symbol}:*"
        deleted_count = await self.clear_pattern(pattern)
        self.logger.info(f"Market cache invalidated for {symbol}: {deleted_count} keys")


class CacheDecorator:
    """Cache decorator - funksiyalar uchun"""
    
    def __init__(self, cache: DistributedCache, cache_name: str = "default"):
        self.cache = cache
        self.cache_name = cache_name
    
    def cache_result(
        self,
        ttl: Optional[int] = None,
        key_generator: Optional[Callable] = None,
        invalidate_on: Optional[List[str]] = None
    ):
        """Funksiya natijasini cache ga saqlash"""
        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                # Kalit yaratish
                if key_generator:
                    cache_key = key_generator(*args, **kwargs)
                else:
                    # Default kalit
                    cache_key = CacheKeyGenerator.generate_key(
                        f"{func.__module__}:{func.__name__}",
                        *args, **kwargs
                    )
                
                # Cache dan olish
                cached_result = await self.cache.get(cache_key, self.cache_name)
                if cached_result is not None:
                    return cached_result
                
                # Funksiya bajarish
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Cache ga saqlash
                await self.cache.set(cache_key, result, ttl, self.cache_name)
                
                return result
            
            return async_wrapper
        return decorator


class CacheWarmer:
    """Cache warming - muhim ma'lumotlarni oldindan yuklash"""
    
    def __init__(self, cache: DistributedCache):
        self.cache = cache
        self.logger = logging.getLogger(__name__)
    
    async def warm_user_cache(self, user_id: str, user_data_func, trading_data_func):
        """Foydalanuvchi cache ni oldindan to'ldirish"""
        try:
            # Foydalanuvchi ma'lumotlari
            user_data = await user_data_func(user_id)
            user_cache_key = CacheKeyGenerator.generate_user_key(user_id, "profile")
            await self.cache.set(user_cache_key, user_data, cache_name="user_cache")
            
            # Trading ma'lumotlari
            trading_data = await trading_data_func(user_id)
            trading_cache_key = CacheKeyGenerator.generate_user_key(user_id, "trading")
            await self.cache.set(trading_cache_key, trading_data, cache_name="trading_cache")
            
            self.logger.info(f"User cache warmed for {user_id}")
            
        except Exception as e:
            self.logger.error(f"Warm user cache xatolik: {e}")
    
    async def warm_market_cache(self, symbols: List[str], market_data_func):
        """Bozor cache ni oldindan to'ldirish"""
        try:
            for symbol in symbols:
                # Bozor ma'lumotlari
                market_data = await market_data_func(symbol)
                cache_key = CacheKeyGenerator.generate_market_key(symbol, "1h")
                await self.cache.set(cache_key, market_data, cache_name="market_cache")
            
            self.logger.info(f"Market cache warmed for {len(symbols)} symbols")
            
        except Exception as e:
            self.logger.error(f"Warm market cache xatolik: {e}")


class CacheManager:
    """Cache manager - barcha cache operatsiyalarini boshqarish"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.cache = DistributedCache(redis_url)
        self.decorator = CacheDecorator(self.cache)
        self.warmer = CacheWarmer(self.cache)
        self.logger = logging.getLogger(__name__)
        
        # Standart cache larni ro'yxatga olish
        self._setup_default_caches()
    
    def _setup_default_caches(self):
        """Standart cache larni sozlash"""
        
        # User cache
        user_cache = CacheConfig(
            name="user_cache",
            strategy=CacheStrategy.CACHE_ASIDE,
            ttl=1800,  # 30 daqiqa
            max_size=5000,
            invalidation=InvalidationStrategy.EVENT_BASED
        )
        self.cache.register_cache(user_cache)
        
        # Trading cache
        trading_cache = CacheConfig(
            name="trading_cache",
            strategy=CacheStrategy.WRITE_THROUGH,
            ttl=60,  # 1 daqiqa
            max_size=10000,
            invalidation=InvalidationStrategy.TIME_BASED
        )
        self.cache.register_cache(trading_cache)
        
        # Market data cache
        market_cache = CacheConfig(
            name="market_cache",
            strategy=CacheStrategy.READ_THROUGH,
            ttl=30,  # 30 soniya
            max_size=5000,
            invalidation=InvalidationStrategy.TIME_BASED
        )
        self.cache.register_cache(market_cache)
        
        # Session cache
        session_cache = CacheConfig(
            name="session_cache",
            strategy=CacheStrategy.WRITE_THROUGH,
            ttl=3600,  # 1 soat
            max_size=2000,
            invalidation=InvalidationStrategy.MANUAL
        )
        self.cache.register_cache(session_cache)
        
        # Analytics cache
        analytics_cache = CacheConfig(
            name="analytics_cache",
            strategy=CacheStrategy.CACHE_ASIDE,
            ttl=300,  # 5 daqiqa
            max_size=2000,
            invalidation=InvalidationStrategy.LRU
        )
        self.cache.register_cache(analytics_cache)
    
    @asynccontextmanager
    async def cache_session(self, user_id: str):
        """Foydalanuvchi session uchun cache context manager"""
        session_key = CacheKeyGenerator.generate_session_key(f"user_{user_id}")
        
        try:
            # Session ma'lumotlarini yuklash
            session_data = await self.cache.get(session_key, "session_cache")
            if session_data is None:
                session_data = {"user_id": user_id, "created_at": datetime.now()}
                await self.cache.set(session_key, session_data, "session_cache")
            
            yield session_data
            
        finally:
            # Session ma'lumotlarini yangilash
            await self.cache.set(session_key, session_data, "session_cache")
    
    async def get_cached_user_profile(self, user_id: str, db_get_user) -> Dict[str, Any]:
        """Foydalanuvchi profilini cache dan olish"""
        cache_key = CacheKeyGenerator.generate_user_key(user_id, "profile")
        
        # Cache dan olish
        cached_profile = await self.cache.get(cache_key, "user_cache")
        if cached_profile:
            return cached_profile
        
        # Database dan olish va cache ga saqlash
        profile = await db_get_user(user_id)
        await self.cache.set(cache_key, profile, "user_cache")
        
        return profile
    
    async def get_cached_market_data(self, symbol: str, timeframe: str, api_call) -> Dict[str, Any]:
        """Bozor ma'lumotlarini cache dan olish"""
        cache_key = CacheKeyGenerator.generate_market_key(symbol, timeframe)
        
        # Cache dan olish
        cached_data = await self.cache.get(cache_key, "market_cache")
        if cached_data:
            return cached_data
        
        # API chaqiruv va cache ga saqlash
        data = await api_call(symbol, timeframe)
        await self.cache.set(cache_key, data, "market_cache")
        
        return data
    
    async def invalidate_on_trade(self, user_id: str):
        """Trading operatsiyasi vaqtida cache ni invalidatsiya qilish"""
        await self.cache.invalidate_user_cache(user_id)
        
        # Trading history cache
        await self.cache.clear_pattern(f"user:{user_id}:trading*")
        
        # Portfolio cache
        await self.cache.clear_pattern(f"user:{user_id}:portfolio*")
        
        self.logger.info(f"Cache invalidated on trade for user {user_id}")
    
    async def cleanup_expired_cache(self):
        """Muddati o'tgan cache larni tozalash"""
        try:
            # Redis dan expire qilingan kalitlarni tozalash
            await self.cache.redis_client.execute_command("FT.DROPINDEX")
            # Note: Redis da expire qilingan kalitlar avtomatik tozalanadi
            self.logger.info("Expired cache cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup xatolik: {e}")
    
    async def get_cache_metrics(self) -> Dict[str, Any]:
        """Cache metrikalarini olish"""
        metrics = {}
        
        for cache_name in self.cache.stats.keys():
            stats = await self.cache.get_stats(cache_name)
            if stats:
                metrics[cache_name] = {
                    "hits": stats.hits,
                    "misses": stats.misses,
                    "hit_rate": round(stats.hit_rate, 3),
                    "current_size": stats.current_size,
                    "evictions": stats.evictions
                }
        
        return metrics


# Cache decorators
def cached_result(
    ttl: int = 300,
    cache_name: str = "default",
    key_prefix: str = ""
):
    """Funksiya natijasini cache qilish decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_manager = get_global_cache_manager()
            
            # Kalit yaratish
            if key_prefix:
                cache_key = CacheKeyGenerator.generate_key(key_prefix, *args, **kwargs)
            else:
                cache_key = CacheKeyGenerator.generate_key(f"{func.__name__}", *args, **kwargs)
            
            # Cache dan olish
            result = await cache_manager.cache.get(cache_key, cache_name)
            if result is not None:
                return result
            
            # Funksiya bajarish
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache ga saqlash
            await cache_manager.cache.set(cache_key, result, ttl, cache_name)
            
            return result
        return wrapper
    return decorator


# Global cache manager instance
_global_cache_manager: Optional[CacheManager] = None

def get_global_cache_manager() -> CacheManager:
    """Global cache manager olish"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    return _global_cache_manager


if __name__ == "__main__":
    async def demo():
        """Demo - Cache sistemi ishlatish"""
        print("🚀 Orion Starline Cache Sistemi")
        print("=" * 50)
        
        # Cache manager yaratish
        cache_manager = CacheManager()
        
        # User ma'lumotlari demo
        user_id = "user_12345"
        
        async def fake_db_get_user(user_id):
            await asyncio.sleep(0.1)  # Database delay simulation
            return {
                "id": user_id,
                "name": "John Doe",
                "email": "john@example.com",
                "balance": 10000,
                "created_at": "2023-01-01"
            }
        
        async def fake_trading_api(symbol, timeframe):
            await asyncio.sleep(0.05)  # API delay simulation
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "price": 1.2345,
                "volume": 1000000,
                "timestamp": datetime.now().isoformat()
            }
        
        # Cache performance test
        print("⚡ Cache Performance Test:")
        
        # Birinchi chaqiruv (cache miss)
        start_time = datetime.now()
        profile = await cache_manager.get_cached_user_profile(user_id, fake_db_get_user)
        first_call_time = (datetime.now() - start_time).total_seconds()
        
        # Ikkinchi chaqiruv (cache hit)
        start_time = datetime.now()
        cached_profile = await cache_manager.get_cached_user_profile(user_id, fake_db_get_user)
        second_call_time = (datetime.now() - start_time).total_seconds()
        
        print(f"Birinchi chaqiruv vaqti: {first_call_time:.3f}s (cache miss)")
        print(f"Ikkinchi chaqiruv vaqti: {second_call_time:.3f}s (cache hit)")
        print(f"Tezlash: {first_call_time/second_call_time:.1f}x")
        
        # Market data cache test
        print("\n📊 Market Data Cache Test:")
        symbol = "EURUSD"
        timeframe = "1h"
        
        start_time = datetime.now()
        market_data = await cache_manager.get_cached_market_data(symbol, timeframe, fake_trading_api)
        first_md_time = (datetime.now() - start_time).total_seconds()
        
        start_time = datetime.now()
        cached_market_data = await cache_manager.get_cached_market_data(symbol, timeframe, fake_trading_api)
        second_md_time = (datetime.now() - start_time).total_seconds()
        
        print(f"Market data birinchi: {first_md_time:.3f}s")
        print(f"Market data cached: {second_md_time:.3f}s")
        
        # Cache metrics
        print("\n📈 Cache Metrics:")
        metrics = await cache_manager.get_cache_metrics()
        for cache_name, stats in metrics.items():
            print(f"{cache_name}:")
            print(f"  Hit rate: {stats['hit_rate']:.1%}")
            print(f"  Current size: {stats['current_size']}")
            print(f"  Hits: {stats['hits']}, Misses: {stats['misses']}")
        
        # Cache invalidation test
        print("\n🗑️ Cache Invalidation Test:")
        await cache_manager.invalidate_on_trade(user_id)
        print(f"User {user_id} uchun cache invalidatsiya qilindi")
        
        # Session cache test
        print("\n🔐 Session Cache Test:")
        async with cache_manager.cache_session(user_id) as session:
            session["last_activity"] = datetime.now()
            session["action_count"] = session.get("action_count", 0) + 1
            print(f"Session updated: {session}")
        
        print("\n🎉 Demo tugallandi!")
        print(f"💾 Jami cache kalitlari: {await cache_manager.cache.redis_client.dbsize()}")
    
    asyncio.run(demo())