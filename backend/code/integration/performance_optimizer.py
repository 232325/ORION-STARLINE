"""
FastAPI Performance Optimizer
============================

FastAPI ilovasi uchun comprehensive performance optimization moduli.
Quyidagi imkoniyatlarni taqdim etadi:

- Metriklar to'plash va monitoring
- LRU va TTL caching tizimlari
- Database/API connection pooling
- Query optimizatsiya
- Load balancing
- Real-time performance monitoring
- Automatic performance alerts
- FastAPI middleware integratsiya

Foydalanish:
    from performance_optimizer import PerformanceOptimizer, performance_monitor
    
    optimizer = PerformanceOptimizer()
    
    # Cache decorator
    @optimizer.cache(cache_type='lru')
    async def expensive_operation():
        return await some_expensive_function()
    
    # FastAPI middleware
    app = FastAPI()
    app.add_middleware(performance_monitor)
"""

import asyncio
import logging
import time
import cProfile
import pstats
import io
import functools
import psutil
import redis
import aioredis
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
import threading
import json
import statistics
import weakref
import gc
from contextlib import asynccontextmanager
from pathlib import Path
import traceback
import sys
import signal
import resource
import os

try:
    from fastapi import FastAPI, Request, Response, HTTPException
    from fastapi.middleware.base import BaseHTTPMiddleware
    from fastapi.responses import JSONResponse
    from starlette.middleware.base import RequestResponseEndpoint
    from starlette.types import ASGIApp
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Placeholder for FastAPI types
    class FastAPI:
        pass
    class Request:
        pass
    class Response:
        pass
    class BaseHTTPMiddleware:
        pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrikalari"""
    function_name: str
    call_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    last_called: Optional[datetime] = None
    memory_usage: float = 0.0  # MB


class LRUCache:
    """
    Least Recently Used Cache
    
    Tez-tez ishlatilmaydigan ma'lumotlarni avtomatik o'chiradi
    """
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache: OrderedDict = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Cache dan ma'lumot olish"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            
            self.misses += 1
            return None
    
    def put(self, key: str, value: Any):
        """Cache ga ma'lumot qo'shish"""
        with self.lock:
            if key in self.cache:
                # Update and move to end
                self.cache.move_to_end(key)
            else:
                # Add new item
                self.cache[key] = value
                
                # Remove oldest if capacity exceeded
                if len(self.cache) > self.capacity:
                    self.cache.popitem(last=False)
    
    def clear(self):
        """Cache ni tozalash"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    @property
    def hit_rate(self) -> float:
        """Cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total * 100 if total > 0 else 0.0
    
    def stats(self) -> Dict[str, Any]:
        """Cache statistikasi"""
        return {
            'size': len(self.cache),
            'capacity': self.capacity,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hit_rate
        }


class TTLCache:
    """
    Time-To-Live Cache
    
    Ma'lumotlar belgilangan vaqtdan keyin avtomatik o'chiriladi
    """
    
    def __init__(self, ttl: int = 3600):  # 1 hour default
        self.ttl = ttl  # seconds
        self.cache: Dict[str, tuple] = {}  # key: (value, expiry_time)
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Cache dan ma'lumot olish"""
        with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                
                # Check if expired
                if time.time() < expiry:
                    return value
                else:
                    # Remove expired item
                    del self.cache[key]
            
            return None
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None):
        """Cache ga ma'lumot qo'shish"""
        ttl = ttl or self.ttl
        expiry = time.time() + ttl
        
        with self.lock:
            self.cache[key] = (value, expiry)
    
    def clear(self):
        """Cache ni tozalash"""
        with self.lock:
            self.cache.clear()
    
    def cleanup_expired(self):
        """Expired items ni o'chirish"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expiry) in self.cache.items()
                if current_time >= expiry
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)


class ConnectionPool:
    """
    Connection Pool Manager
    
    Database va API connectionlarni reuse qilish uchun
    """
    
    def __init__(self, factory: Callable, min_size: int = 5, max_size: int = 20):
        self.factory = factory
        self.min_size = min_size
        self.max_size = max_size
        
        self.pool: List[Any] = []
        self.in_use: set = set()
        self.lock = asyncio.Lock()
        
        self.created_count = 0
        self.acquired_count = 0
        self.released_count = 0
    
    async def initialize(self):
        """Pool ni initialize qilish"""
        for _ in range(self.min_size):
            conn = await self._create_connection()
            self.pool.append(conn)
    
    async def _create_connection(self) -> Any:
        """Yangi connection yaratish"""
        if asyncio.iscoroutinefunction(self.factory):
            conn = await self.factory()
        else:
            conn = self.factory()
        
        self.created_count += 1
        return conn
    
    async def acquire(self) -> Any:
        """Connection olish"""
        async with self.lock:
            # Try to get from pool
            if self.pool:
                conn = self.pool.pop()
                self.in_use.add(id(conn))
                self.acquired_count += 1
                return conn
            
            # Create new if not at max capacity
            if len(self.in_use) < self.max_size:
                conn = await self._create_connection()
                self.in_use.add(id(conn))
                self.acquired_count += 1
                return conn
            
            # Wait for available connection
            logger.warning("Connection pool exhausted, waiting...")
            await asyncio.sleep(0.1)
            return await self.acquire()
    
    async def release(self, conn: Any):
        """Connection ni qaytarish"""
        async with self.lock:
            conn_id = id(conn)
            
            if conn_id in self.in_use:
                self.in_use.remove(conn_id)
                self.pool.append(conn)
                self.released_count += 1
    
    async def close_all(self):
        """Barcha connectionlarni yopish"""
        async with self.lock:
            # Close all connections
            for conn in self.pool:
                if hasattr(conn, 'close'):
                    if asyncio.iscoroutinefunction(conn.close):
                        await conn.close()
                    else:
                        conn.close()
            
            self.pool.clear()
            self.in_use.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Pool statistikasi"""
        return {
            'available': len(self.pool),
            'in_use': len(self.in_use),
            'total_created': self.created_count,
            'total_acquired': self.acquired_count,
            'total_released': self.released_count
        }


class Profiler:
    """
    Code Profiler
    
    Function execution time va memory usage ni track qilish
    """
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.lock = threading.Lock()
    
    def profile(self, func: Callable) -> Callable:
        """Function profiling decorator"""
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                memory_used = end_memory - start_memory
                
                self._record_metric(func.__name__, duration, memory_used)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                memory_used = end_memory - start_memory
                
                self._record_metric(func.__name__, duration, memory_used)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    def _record_metric(self, func_name: str, duration: float, memory_used: float):
        """Metrikani saqlash"""
        with self.lock:
            if func_name not in self.metrics:
                self.metrics[func_name] = PerformanceMetrics(function_name=func_name)
            
            metric = self.metrics[func_name]
            metric.call_count += 1
            metric.total_time += duration
            metric.avg_time = metric.total_time / metric.call_count
            metric.min_time = min(metric.min_time, duration)
            metric.max_time = max(metric.max_time, duration)
            metric.last_called = datetime.now()
            metric.memory_usage = memory_used
    
    def get_stats(self, func_name: Optional[str] = None) -> Dict[str, Any]:
        """Statistikani olish"""
        if func_name:
            metric = self.metrics.get(func_name)
            if metric:
                return {
                    'call_count': metric.call_count,
                    'total_time': metric.total_time,
                    'avg_time': metric.avg_time,
                    'min_time': metric.min_time,
                    'max_time': metric.max_time,
                    'last_called': metric.last_called.isoformat() if metric.last_called else None,
                    'memory_usage': metric.memory_usage
                }
            return {}
        
        # Return all metrics
        return {
            name: {
                'call_count': m.call_count,
                'avg_time': m.avg_time,
                'total_time': m.total_time,
                'memory_usage': m.memory_usage
            }
            for name, m in self.metrics.items()
        }
    
    def print_stats(self):
        """Statistikani chop etish"""
        logger.info("=" * 80)
        logger.info("Performance Statistics")
        logger.info("=" * 80)
        
        # Sort by total time
        sorted_metrics = sorted(
            self.metrics.values(),
            key=lambda m: m.total_time,
            reverse=True
        )
        
        for metric in sorted_metrics:
            logger.info(f"\nFunction: {metric.function_name}")
            logger.info(f"  Calls: {metric.call_count}")
            logger.info(f"  Total Time: {metric.total_time:.3f}s")
            logger.info(f"  Avg Time: {metric.avg_time:.3f}s")
            logger.info(f"  Min Time: {metric.min_time:.3f}s")
            logger.info(f"  Max Time: {metric.max_time:.3f}s")
            logger.info(f"  Memory: {metric.memory_usage:.2f} MB")


class LoadBalancer:
    """
    Simple Load Balancer
    
    Workload ni multiple workers orasida taqsimlash
    """
    
    def __init__(self, workers: List[Any], strategy: str = 'round_robin'):
        """
        Args:
            workers: Worker list
            strategy: 'round_robin', 'least_loaded', 'random'
        """
        self.workers = workers
        self.strategy = strategy
        self.current_index = 0
        self.worker_loads: Dict[int, int] = {i: 0 for i in range(len(workers))}
        self.lock = asyncio.Lock()
    
    async def get_worker(self) -> Any:
        """Worker olish"""
        async with self.lock:
            if self.strategy == 'round_robin':
                worker = self.workers[self.current_index]
                self.current_index = (self.current_index + 1) % len(self.workers)
                return worker
            
            elif self.strategy == 'least_loaded':
                # Find worker with minimum load
                min_load_index = min(self.worker_loads, key=self.worker_loads.get)
                self.worker_loads[min_load_index] += 1
                return self.workers[min_load_index]
            
            elif self.strategy == 'random':
                import random
                return random.choice(self.workers)
            
            else:
                raise ValueError(f"Unknown strategy: {self.strategy}")
    
    async def release_worker(self, worker: Any):
        """Worker ni bo'shatish"""
        async with self.lock:
            worker_index = self.workers.index(worker)
            if worker_index in self.worker_loads:
                self.worker_loads[worker_index] = max(0, self.worker_loads[worker_index] - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Load balancer statistikasi"""
        return {
            'total_workers': len(self.workers),
            'strategy': self.strategy,
            'worker_loads': self.worker_loads
        }


class QueryOptimizer:
    """
    Database Query Optimizer
    
    Query performance ni optimize qilish
    """
    
    def __init__(self):
        self.query_cache = LRUCache(capacity=500)
        self.slow_queries: List[Dict[str, Any]] = []
        self.slow_query_threshold = 1.0  # seconds
    
    def optimize_query(self, query: str) -> str:
        """SQL query ni optimize qilish"""
        optimized = query
        
        # Remove extra whitespace
        optimized = ' '.join(optimized.split())
        
        # Add LIMIT if not present for SELECT queries
        if 'SELECT' in optimized.upper() and 'LIMIT' not in optimized.upper():
            optimized += ' LIMIT 1000'
        
        return optimized
    
    async def execute_with_cache(self, query: str, executor: Callable) -> Any:
        """Query ni cache bilan execute qilish"""
        # Check cache
        cached_result = self.query_cache.get(query)
        if cached_result is not None:
            return cached_result
        
        # Execute query
        start_time = time.time()
        
        if asyncio.iscoroutinefunction(executor):
            result = await executor(query)
        else:
            result = executor(query)
        
        duration = time.time() - start_time
        
        # Track slow queries
        if duration > self.slow_query_threshold:
            self.slow_queries.append({
                'query': query,
                'duration': duration,
                'timestamp': datetime.now()
            })
            
            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]
        
        # Cache result
        self.query_cache.put(query, result)
        
        return result
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Eng sekin query larni olish"""
        sorted_queries = sorted(
            self.slow_queries,
            key=lambda q: q['duration'],
            reverse=True
        )
        return sorted_queries[:limit]


class PerformanceOptimizer:
    """
    Comprehensive Performance Optimizer for FastAPI
    
    Barcha optimization vositalarini birlashtiradi va FastAPI
    ilovalari uchun maxsus xususiyatlarni taqdim etadi.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize core components
        self.lru_cache = LRUCache(capacity=self.config.get('cache_size', 1000))
        self.ttl_cache = TTLCache(ttl=self.config.get('cache_ttl', 3600))
        self.profiler = Profiler()
        self.query_optimizer = QueryOptimizer()
        
        # Connection pools
        self.connection_pools: Dict[str, ConnectionPool] = {}
        
        # Redis cache (optional)
        self.redis_client: Optional[Union[redis.Redis, aioredis.Redis]] = None
        self.redis_enabled = self.config.get('redis_enabled', False)
        if self.redis_enabled:
            self._setup_redis()
        
        # Performance monitoring
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        self.monitoring_interval = self.config.get('monitoring_interval', 60)
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Alert thresholds
        self.alert_thresholds = {
            'cpu_percent': self.config.get('cpu_threshold', 80.0),
            'memory_percent': self.config.get('memory_threshold', 85.0),
            'response_time': self.config.get('response_time_threshold', 5.0),  # seconds
            'error_rate': self.config.get('error_rate_threshold', 5.0)  # percentage
        }
        
        # Request tracking
        self.request_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'errors': 0,
            'last_request': None
        })
        
        # Performance alerts
        self.alert_handlers: List[Callable] = []
        
        # Resource monitoring
        self.baseline_resources = self._capture_baseline()
        
        logger.info("Performance Optimizer initialized")
    
    def _setup_redis(self):
        """Redis connection setup"""
        try:
            redis_config = self.config.get('redis', {})
            
            if redis_config.get('use_aioredis', True):
                # Async Redis
                self.redis_client = aioredis.from_url(
                    redis_config.get('url', 'redis://localhost:6379'),
                    password=redis_config.get('password'),
                    decode_responses=True
                )
            else:
                # Sync Redis
                self.redis_client = redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    password=redis_config.get('password'),
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                
                # Test connection
                self.redis_client.ping()
                
            logger.info("Redis cache initialized")
            
        except Exception as e:
            logger.warning(f"Redis setup failed: {e}. Continuing without Redis.")
            self.redis_enabled = False
    
    def _capture_baseline(self) -> Dict[str, Any]:
        """Capture baseline resource usage"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total,
                'baseline_time': datetime.now()
            }
        except Exception:
            return {}
    
    def add_alert_handler(self, handler: Callable):
        """Add performance alert handler"""
        self.alert_handlers.append(handler)
    
    def _trigger_alert(self, alert_type: str, message: str, value: float):
        """Trigger performance alert"""
        alert_data = {
            'type': alert_type,
            'message': message,
            'value': value,
            'threshold': self.alert_thresholds.get(alert_type),
            'timestamp': datetime.now(),
            'baseline': self.baseline_resources
        }
        
        logger.warning(f"PERFORMANCE ALERT [{alert_type}]: {message} (Value: {value:.2f})")
        
        # Call alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert_data)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    def track_request(self, endpoint: str, response_time: float, status_code: int):
        """Track request performance"""
        stats = self.request_stats[endpoint]
        stats['count'] += 1
        stats['total_time'] += response_time
        stats['last_request'] = datetime.now()
        
        if status_code >= 400:
            stats['errors'] += 1
        
        # Check for alerts
        if response_time > self.alert_thresholds['response_time']:
            self._trigger_alert(
                'response_time', 
                f"Slow response on {endpoint}",
                response_time
            )
        
        # Calculate error rate
        if stats['count'] > 0:
            error_rate = (stats['errors'] / stats['count']) * 100
            if error_rate > self.alert_thresholds['error_rate']:
                self._trigger_alert(
                    'error_rate',
                    f"High error rate on {endpoint}",
                    error_rate
                )
    
    def cache(self, cache_type: str = 'lru', ttl: Optional[int] = None, key_prefix: str = ''):
        """Advanced caching decorator with Redis support"""
        def decorator(func: Callable) -> Callable:
            cache_key_prefix = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                key_parts = [cache_key_prefix]
                if args:
                    key_parts.append(str(args))
                if kwargs:
                    key_parts.append(str(sorted(kwargs.items())))
                cache_key = ":".join(key_parts)
                
                # Try to get from cache
                cached_result = None
                
                if cache_type == 'lru':
                    cached_result = self.lru_cache.get(cache_key)
                elif cache_type == 'ttl':
                    cached_result = self.ttl_cache.get(cache_key)
                elif cache_type == 'redis' and self.redis_enabled:
                    try:
                        if isinstance(self.redis_client, aioredis.Redis):
                            cached_result = await self.redis_client.get(cache_key)
                            if cached_result:
                                import json
                                cached_result = json.loads(cached_result)
                        else:
                            cached_result = self.redis_client.get(cache_key)
                            if cached_result:
                                import json
                                cached_result = json.loads(cached_result)
                    except Exception as e:
                        logger.warning(f"Redis cache get failed: {e}")
                
                if cached_result is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cached_result
                
                # Execute function
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    
                    # Store in cache
                    if cache_type == 'lru':
                        self.lru_cache.put(cache_key, result)
                    elif cache_type == 'ttl':
                        self.ttl_cache.put(cache_key, result, ttl=ttl)
                    elif cache_type == 'redis' and self.redis_enabled:
                        try:
                            import json
                            serialized_result = json.dumps(result, default=str)
                            
                            if isinstance(self.redis_client, aioredis.Redis):
                                await self.redis_client.setex(
                                    cache_key, ttl or 3600, serialized_result
                                )
                            else:
                                self.redis_client.setex(
                                    cache_key, ttl or 3600, serialized_result
                                )
                        except Exception as e:
                            logger.warning(f"Redis cache put failed: {e}")
                    
                    execution_time = time.time() - start_time
                    logger.debug(f"Function {func.__name__} executed in {execution_time:.3f}s")
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Function {func.__name__} failed after {execution_time:.3f}s: {e}")
                    raise
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Generate cache key
                key_parts = [cache_key_prefix]
                if args:
                    key_parts.append(str(args))
                if kwargs:
                    key_parts.append(str(sorted(kwargs.items())))
                cache_key = ":".join(key_parts)
                
                # Try to get from cache
                cached_result = None
                
                if cache_type == 'lru':
                    cached_result = self.lru_cache.get(cache_key)
                elif cache_type == 'ttl':
                    cached_result = self.ttl_cache.get(cache_key)
                elif cache_type == 'redis' and self.redis_enabled:
                    try:
                        cached_result = self.redis_client.get(cache_key)
                        if cached_result:
                            import json
                            cached_result = json.loads(cached_result)
                    except Exception as e:
                        logger.warning(f"Redis cache get failed: {e}")
                
                if cached_result is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cached_result
                
                # Execute function
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    
                    # Store in cache (sync only for LRU/TTL)
                    if cache_type in ['lru', 'ttl']:
                        if cache_type == 'lru':
                            self.lru_cache.put(cache_key, result)
                        else:
                            self.ttl_cache.put(cache_key, result, ttl=ttl)
                    
                    execution_time = time.time() - start_time
                    logger.debug(f"Function {func.__name__} executed in {execution_time:.3f}s")
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Function {func.__name__} failed after {execution_time:.3f}s: {e}")
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    async def invalidate_cache(self, pattern: str = None, cache_type: str = 'lru'):
        """Invalidate cache entries"""
        if cache_type == 'lru':
            if pattern:
                # Remove matching keys from LRU cache
                keys_to_remove = [
                    key for key in self.lru_cache.cache.keys() 
                    if pattern in key
                ]
                for key in keys_to_remove:
                    self.lru_cache.cache.pop(key, None)
            else:
                self.lru_cache.clear()
                
        elif cache_type == 'ttl':
            if pattern:
                keys_to_remove = [
                    key for key in self.ttl_cache.cache.keys() 
                    if pattern in key
                ]
                for key in keys_to_remove:
                    self.ttl_cache.cache.pop(key, None)
            else:
                self.ttl_cache.clear()
                
        elif cache_type == 'redis' and self.redis_enabled:
            try:
                if pattern:
                    keys = []
                    if isinstance(self.redis_client, aioredis.Redis):
                        keys = await self.redis_client.keys(f"*{pattern}*")
                        if keys:
                            await self.redis_client.delete(*keys)
                    else:
                        keys = self.redis_client.keys(f"*{pattern}*")
                        if keys:
                            self.redis_client.delete(*keys)
                else:
                    if isinstance(self.redis_client, aioredis.Redis):
                        await self.redis_client.flushdb()
                    else:
                        self.redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Redis cache invalidation failed: {e}")
        
        logger.info(f"Cache invalidated - type: {cache_type}, pattern: {pattern}")
    
    def profile(self, func: Callable) -> Callable:
        """Enhanced profiling decorator with error tracking"""
        return self.profiler.profile(func)
    
    def monitor_performance(self, **kwargs):
        """Performance monitoring decorator with detailed tracking"""
        def decorator(func: Callable) -> Callable:
            monitored_attributes = kwargs.get('attributes', {})
            track_memory = kwargs.get('track_memory', True)
            track_cpu = kwargs.get('track_cpu', True)
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Pre-execution monitoring
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024 if track_memory else 0
                start_cpu = psutil.Process().cpu_percent() if track_cpu else 0
                
                # Execute function with profiling
                result = await self.profiler.profile(func)(*args, **kwargs)
                
                # Post-execution monitoring
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024 if track_memory else 0
                end_cpu = psutil.Process().cpu_percent() if track_cpu else 0
                
                execution_time = end_time - start_time
                memory_delta = end_memory - start_memory if track_memory else 0
                
                # Log performance metrics
                logger.info(
                    f"Performance [{func.__name__}]: "
                    f"time={execution_time:.3f}s, "
                    f"memory_delta={memory_delta:.2f}MB"
                    + (f", cpu_delta={end_cpu - start_cpu:.1f}%" if track_cpu else "")
                )
                
                # Store custom attributes
                if monitored_attributes:
                    for attr_name, attr_value in monitored_attributes.items():
                        setattr(result, attr_name, attr_value) if hasattr(result, attr_name) else None
                
                return result
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Pre-execution monitoring
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024 if track_memory else 0
                start_cpu = psutil.Process().cpu_percent() if track_cpu else 0
                
                # Execute function with profiling
                result = self.profiler.profile(func)(*args, **kwargs)
                
                # Post-execution monitoring
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024 if track_memory else 0
                end_cpu = psutil.Process().cpu_percent() if track_cpu else 0
                
                execution_time = end_time - start_time
                memory_delta = end_memory - start_memory if track_memory else 0
                
                # Log performance metrics
                logger.info(
                    f"Performance [{func.__name__}]: "
                    f"time={execution_time:.3f}s, "
                    f"memory_delta={memory_delta:.2f}MB"
                    + (f", cpu_delta={end_cpu - start_cpu:.1f}%" if track_cpu else "")
                )
                
                # Store custom attributes
                if monitored_attributes:
                    for attr_name, attr_value in monitored_attributes.items():
                        setattr(result, attr_name, attr_value) if hasattr(result, attr_name) else None
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    async def create_connection_pool(self, name: str, factory: Callable,
                                    min_size: int = 5, max_size: int = 20):
        """Connection pool yaratish"""
        pool = ConnectionPool(factory, min_size, max_size)
        await pool.initialize()
        self.connection_pools[name] = pool
        logger.info(f"Connection pool '{name}' created with {min_size}-{max_size} connections")
    
    async def get_connection(self, pool_name: str) -> Any:
        """Connection olish"""
        if pool_name not in self.connection_pools:
            raise ValueError(f"Connection pool '{pool_name}' not found")
        return await self.connection_pools[pool_name].acquire()
    
    async def release_connection(self, pool_name: str, conn: Any):
        """Connection qaytarish"""
        if pool_name not in self.connection_pools:
            raise ValueError(f"Connection pool '{pool_name}' not found")
        await self.connection_pools[pool_name].release(conn)
    
    async def start_monitoring(self):
        """Performance monitoring ni boshlash"""
        if not self.monitoring_enabled:
            return
        
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Performance monitoring ni to'xtatish"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Enhanced monitoring loop with detailed metrics and alerts"""
        logger.info("Starting enhanced performance monitoring...")
        
        while True:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Network statistics
                network = psutil.net_io_counters()
                
                # Process information
                process = psutil.Process()
                process_memory = process.memory_info()
                process_cpu = process.cpu_percent()
                
                # Check for system alerts
                if cpu_percent > self.alert_thresholds['cpu_percent']:
                    self._trigger_alert('cpu_percent', f"High CPU usage: {cpu_percent}%", cpu_percent)
                
                if memory.percent > self.alert_thresholds['memory_percent']:
                    self._trigger_alert('memory_percent', f"High memory usage: {memory.percent}%", memory.percent)
                
                # Log detailed metrics
                logger.info("=" * 80)
                logger.info("DETAILED PERFORMANCE METRICS")
                logger.info("=" * 80)
                
                logger.info(f"CPU Usage: {cpu_percent}% (Threshold: {self.alert_thresholds['cpu_percent']}%)")
                logger.info(f"Memory Usage: {memory.percent}% ({memory.used / 1024 / 1024 / 1024:.2f} GB / {memory.total / 1024 / 1024 / 1024:.2f} GB)")
                logger.info(f"Disk Usage: {disk.percent}% ({disk.used / 1024 / 1024 / 1024:.2f} GB / {disk.total / 1024 / 1024 / 1024:.2f} GB)")
                logger.info(f"Process Memory: {process_memory.rss / 1024 / 1024:.2f} MB")
                logger.info(f"Process CPU: {process_cpu}%")
                logger.info(f"Network I/O: Bytes sent={network.bytes_sent / 1024 / 1024:.2f} MB, Bytes recv={network.bytes_recv / 1024 / 1024:.2f} MB")
                
                # Cache statistics
                lru_stats = self.lru_cache.stats()
                logger.info(f"\nLRU Cache: Size={lru_stats['size']}, Hit rate={lru_stats['hit_rate']:.1f}%")
                
                if self.redis_enabled:
                    try:
                        if isinstance(self.redis_client, aioredis.Redis):
                            redis_info = await self.redis_client.info()
                        else:
                            redis_info = self.redis_client.info()
                        
                        logger.info(f"Redis: Connected clients={redis_info.get('connected_clients', 0)}, "
                                  f"Used memory={redis_info.get('used_memory_human', 'N/A')}")
                    except Exception as e:
                        logger.warning(f"Redis info failed: {e}")
                
                # Connection pool statistics
                for name, pool in self.connection_pools.items():
                    pool_stats = pool.stats()
                    logger.info(f"\nConnection Pool '{name}': Available={pool_stats['available']}, "
                              f"In Use={pool_stats['in_use']}, Total Created={pool_stats['total_created']}")
                
                # Top request statistics
                logger.info(f"\nTop Request Endpoints:")
                sorted_requests = sorted(
                    self.request_stats.items(),
                    key=lambda x: x[1]['total_time'],
                    reverse=True
                )[:5]
                
                for endpoint, stats in sorted_requests:
                    avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
                    error_rate = (stats['errors'] / stats['count'] * 100) if stats['count'] > 0 else 0
                    logger.info(f"  {endpoint}: "
                              f"Count={stats['count']}, "
                              f"Avg Time={avg_time:.3f}s, "
                              f"Error Rate={error_rate:.1f}%")
                
                # Slow queries
                slow_queries = self.query_optimizer.get_slow_queries(limit=3)
                if slow_queries:
                    logger.info(f"\nSlowest Queries:")
                    for query in slow_queries:
                        logger.info(f"  {query['duration']:.3f}s - {query['query'][:80]}...")
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                logger.error(traceback.format_exc())
                await asyncio.sleep(10)  # Wait before retrying
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Comprehensive performance report"""
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        process = psutil.Process()
        
        # Request statistics summary
        total_requests = sum(stats['count'] for stats in self.request_stats.values())
        total_errors = sum(stats['errors'] for stats in self.request_stats.values())
        overall_error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        # Cache statistics with Redis (sync)
        cache_stats = {
            'lru_cache': self.lru_cache.stats()
        }
        
        if self.redis_enabled:
            try:
                if hasattr(self.redis_client, 'info'):
                    redis_info = self.redis_client.info()
                else:
                    redis_info = {'connected_clients': 0, 'used_memory_human': 'N/A', 'keyspace_hits': 0, 'keyspace_misses': 0}
                cache_stats['redis'] = {
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'used_memory_human': redis_info.get('used_memory_human', 'N/A'),
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0),
                }
            except Exception as e:
                cache_stats['redis'] = {'error': str(e)}
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / 1024 / 1024 / 1024,
                'memory_total_gb': memory.total / 1024 / 1024 / 1024,
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / 1024 / 1024 / 1024,
                'disk_total_gb': disk.total / 1024 / 1024 / 1024,
                'network_bytes_sent_mb': network.bytes_sent / 1024 / 1024,
                'network_bytes_recv_mb': network.bytes_recv / 1024 / 1024,
                'process_memory_mb': process.memory_info().rss / 1024 / 1024,
                'process_cpu_percent': process.cpu_percent()
            },
            'profiler': self.profiler.get_stats(),
            'cache': cache_stats,
            'connection_pools': {
                name: pool.stats()
                for name, pool in self.connection_pools.items()
            },
            'request_statistics': {
                'total_requests': total_requests,
                'total_errors': total_errors,
                'overall_error_rate': overall_error_rate,
                'endpoints': {
                    endpoint: {
                        'count': stats['count'],
                        'total_time': stats['total_time'],
                        'avg_time': stats['total_time'] / stats['count'] if stats['count'] > 0 else 0,
                        'errors': stats['errors'],
                        'error_rate': (stats['errors'] / stats['count'] * 100) if stats['count'] > 0 else 0,
                        'last_request': stats['last_request'].isoformat() if stats['last_request'] else None
                    }
                    for endpoint, stats in self.request_stats.items()
                }
            },
            'slow_queries': self.query_optimizer.get_slow_queries(limit=10),
            'alerts': {
                'thresholds': self.alert_thresholds,
                'triggered': []
            },
            'baseline': self.baseline_resources
        }
        
        return report
    
    async def get_performance_report_async(self) -> Dict[str, Any]:
        """Async version of performance report"""
        return await asyncio.to_thread(self.get_performance_report)
    
    def print_report(self):
        """Enhanced performance report printing"""
        report = self.get_performance_report()
        
        logger.info("=" * 80)
        logger.info("COMPREHENSIVE PERFORMANCE REPORT")
        logger.info("=" * 80)
        logger.info(f"Generated: {report['timestamp']}")
        
        # System metrics
        logger.info("\n📊 SYSTEM METRICS:")
        logger.info(f"  CPU Usage: {report['system']['cpu_percent']:.1f}% "
                   f"(Alert threshold: {self.alert_thresholds['cpu_percent']}%)")
        logger.info(f"  Memory Usage: {report['system']['memory_percent']:.1f}% "
                   f"({report['system']['memory_used_gb']:.2f} GB / {report['system']['memory_total_gb']:.2f} GB)")
        logger.info(f"  Disk Usage: {report['system']['disk_percent']:.1f}% "
                   f"({report['system']['disk_used_gb']:.2f} GB / {report['system']['disk_total_gb']:.2f} GB)")
        logger.info(f"  Process Memory: {report['system']['process_memory_mb']:.1f} MB")
        logger.info(f"  Network I/O: {report['system']['network_bytes_sent_mb']:.1f} MB sent, "
                   f"{report['system']['network_bytes_recv_mb']:.1f} MB received")
        
        # Request statistics
        logger.info(f"\n📈 REQUEST STATISTICS:")
        logger.info(f"  Total Requests: {report['request_statistics']['total_requests']}")
        logger.info(f"  Total Errors: {report['request_statistics']['total_errors']}")
        logger.info(f"  Overall Error Rate: {report['request_statistics']['overall_error_rate']:.1f}%")
        
        if report['request_statistics']['endpoints']:
            logger.info(f"\n  Top Endpoints by Response Time:")
            sorted_endpoints = sorted(
                report['request_statistics']['endpoints'].items(),
                key=lambda x: x[1]['avg_time'],
                reverse=True
            )[:5]
            
            for endpoint, stats in sorted_endpoints:
                logger.info(f"    {endpoint[:40]:<40} | "
                          f"Count: {stats['count']:>5} | "
                          f"Avg: {stats['avg_time']:.3f}s | "
                          f"Errors: {stats['errors']} ({stats['error_rate']:.1f}%)")
        
        # Cache statistics
        logger.info(f"\n💾 CACHE STATISTICS:")
        logger.info(f"  LRU Cache: {report['cache']['lru_cache']}")
        
        if 'redis' in report['cache'] and 'error' not in report['cache']['redis']:
            redis_stats = report['cache']['redis']
            logger.info(f"  Redis: {redis_stats}")
        
        # Connection pools
        if report['connection_pools']:
            logger.info(f"\n🔗 CONNECTION POOLS:")
            for name, stats in report['connection_pools'].items():
                logger.info(f"  {name}: Available={stats['available']}, "
                          f"In Use={stats['in_use']}, "
                          f"Total Created={stats['total_created']}")
        
        # Slow queries
        if report['slow_queries']:
            logger.info(f"\n🐌 SLOW QUERIES:")
            for query in report['slow_queries'][:5]:
                logger.info(f"  {query['duration']:.3f}s - {query['query'][:80]}...")
        
        # Performance insights
        logger.info(f"\n💡 PERFORMANCE INSIGHTS:")
        
        # Check for performance issues
        issues = []
        
        if report['system']['cpu_percent'] > self.alert_thresholds['cpu_percent']:
            issues.append(f"High CPU usage ({report['system']['cpu_percent']:.1f}%)")
        
        if report['system']['memory_percent'] > self.alert_thresholds['memory_percent']:
            issues.append(f"High memory usage ({report['system']['memory_percent']:.1f}%)")
        
        if report['request_statistics']['overall_error_rate'] > self.alert_thresholds['error_rate']:
            issues.append(f"High error rate ({report['request_statistics']['overall_error_rate']:.1f}%)")
        
        if report['cache']['lru_cache']['hit_rate'] < 70:
            issues.append(f"Low cache hit rate ({report['cache']['lru_cache']['hit_rate']:.1f}%)")
        
        if issues:
            logger.warning("  ⚠️  Performance Issues Detected:")
            for issue in issues:
                logger.warning(f"    • {issue}")
        else:
            logger.info("  ✅ No performance issues detected")
        
        logger.info("=" * 80)


    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint data"""
        report = await self.get_performance_report_async() if asyncio.iscoroutine(
            self.get_performance_report()) else self.get_performance_report()
        
        # Determine health status
        cpu_percent = report['system']['cpu_percent']
        memory_percent = report['system']['memory_percent']
        error_rate = report['request_statistics']['overall_error_rate']
        
        status = "healthy"
        issues = []
        
        if cpu_percent > self.alert_thresholds['cpu_percent']:
            status = "degraded"
            issues.append(f"High CPU: {cpu_percent:.1f}%")
        
        if memory_percent > self.alert_thresholds['memory_percent']:
            status = "degraded"
            issues.append(f"High Memory: {memory_percent:.1f}%")
        
        if error_rate > self.alert_thresholds['error_rate']:
            status = "unhealthy"
            issues.append(f"High Error Rate: {error_rate:.1f}%")
        
        return {
            "status": status,
            "issues": issues,
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "error_rate": error_rate,
                "cache_hit_rate": report['cache']['lru_cache']['hit_rate']
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def optimize_memory(self):
        """Memory optimization: garbage collection and cache cleanup"""
        logger.info("Running memory optimization...")
        
        # Clear expired TTL cache entries
        expired_count = self.ttl_cache.cleanup_expired()
        
        # Garbage collection
        collected = gc.collect()
        
        # Clear low-priority caches if memory usage is high
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 80:
            # Clear some LRU cache entries
            cache_size = len(self.lru_cache.cache)
            clear_count = min(cache_size // 4, 100)  # Clear 25% or max 100 items
            
            for _ in range(clear_count):
                if self.lru_cache.cache:
                    self.lru_cache.cache.popitem(last=False)
            
            logger.info(f"Cleared {clear_count} cache entries due to high memory usage")
        
        logger.info(f"Memory optimization complete: {expired_count} expired entries cleared, "
                   f"{collected} objects garbage collected")
    
    def export_metrics(self, format: str = 'json', filepath: Optional[str] = None) -> str:
        """Export performance metrics to file"""
        report = self.get_performance_report()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format.lower() == 'json':
            filepath = filepath or f"performance_report_{timestamp}.json"
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        
        elif format.lower() == 'txt':
            filepath = filepath or f"performance_report_{timestamp}.txt"
            # Redirect logs to capture print_report output
            import io
            log_capture_string = io.StringIO()
            ch = logging.StreamHandler(log_capture_string)
            ch.setLevel(logging.INFO)
            logger.addHandler(ch)
            
            self.print_report()
            
            log_contents = log_capture_string.getvalue()
            logger.removeHandler(ch)
            
            with open(filepath, 'w') as f:
                f.write(log_contents)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Performance metrics exported to {filepath}")
        return filepath
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Performance Optimizer resources...")
        
        # Stop monitoring
        await self.stop_monitoring()
        
        # Close connection pools
        for pool in self.connection_pools.values():
            await pool.close_all()
        
        # Close Redis connection
        if self.redis_client:
            try:
                if isinstance(self.redis_client, aioredis.Redis):
                    await self.redis_client.close()
                else:
                    self.redis_client.close()
            except Exception as e:
                logger.warning(f"Redis cleanup error: {e}")
        
        # Clear caches
        self.lru_cache.clear()
        self.ttl_cache.clear()
        
        logger.info("Performance Optimizer cleanup completed")


if FASTAPI_AVAILABLE:
    class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
        """FastAPI middleware for automatic performance monitoring"""
        
        def __init__(self, app: ASGIApp, optimizer: PerformanceOptimizer):
            super().__init__(app)
            self.optimizer = optimizer
        
        async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
        ) -> Response:
            # Start timing
            start_time = time.time()
            
            # Get client info
            client_ip = request.client.host if request.client else "unknown"
            method = request.method
            path = request.url.path
            
            try:
                # Process request
                response = await call_next(request)
                
                # Calculate response time
                response_time = time.time() - start_time
                
                # Track request
                endpoint = f"{method} {path}"
                self.optimizer.track_request(endpoint, response_time, response.status_code)
                
                # Add performance headers
                response.headers["X-Response-Time"] = f"{response_time:.3f}"
                response.headers["X-Process-Time"] = f"{time.time() - start_time:.3f}"
                
                # Log slow requests
                if response_time > self.optimizer.alert_thresholds['response_time']:
                    logger.warning(
                        f"Slow request: {endpoint} took {response_time:.3f}s "
                        f"(client: {client_ip})"
                    )
                
                return response
                
            except Exception as e:
                # Track failed requests
                response_time = time.time() - start_time
                endpoint = f"{method} {path}"
                self.optimizer.track_request(endpoint, response_time, 500)
                
                logger.error(f"Request failed: {endpoint} - {str(e)}")
                raise
    
    def performance_monitor(optimizer: PerformanceOptimizer) -> Callable:
        """Factory function to create performance monitoring middleware"""
        def middleware(app: FastAPI) -> FastAPI:
            app.add_middleware(PerformanceMonitoringMiddleware, optimizer=optimizer)
            return app
        return middleware
    
    async def setup_fastapi_optimization(
        app: FastAPI, 
        optimizer: PerformanceOptimizer,
        health_endpoint: str = "/health",
        metrics_endpoint: str = "/metrics"
    ) -> FastAPI:
        """Setup FastAPI app with performance optimization"""
        
        @app.get(health_endpoint)
        async def health_check_endpoint():
            """Health check endpoint"""
            return await optimizer.health_check()
        
        @app.get(metrics_endpoint)
        async def metrics_endpoint():
            """Performance metrics endpoint"""
            return await optimizer.get_performance_report_async()
        
        @app.post("/optimize-memory")
        async def optimize_memory_endpoint():
            """Manual memory optimization"""
            await optimizer.optimize_memory()
            return {"message": "Memory optimization completed"}
        
        @app.post("/clear-cache")
        async def clear_cache_endpoint(cache_type: str = "lru", pattern: str = None):
            """Clear cache endpoint"""
            await optimizer.invalidate_cache(pattern, cache_type)
            return {"message": f"Cache cleared: {cache_type}"}
        
        # Add performance monitoring middleware
        app.add_middleware(PerformanceMonitoringMiddleware, optimizer=optimizer)
        
        # Start performance monitoring
        await optimizer.start_monitoring()
        
        logger.info(f"FastAPI optimization setup complete. Endpoints: {health_endpoint}, {metrics_endpoint}")
        return app


# Utility functions
def performance_timer(func: Callable) -> Callable:
    """Simple performance timer decorator"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
        return result
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
        return result
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def memory_usage_tracker(func: Callable) -> Callable:
    """Memory usage tracking decorator"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        result = await func(*args, **kwargs)
        
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = end_memory - start_memory
        
        logger.info(f"{func.__name__} memory usage: {memory_delta:+.2f} MB")
        return result
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        result = func(*args, **kwargs)
        
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = end_memory - start_memory
        
        logger.info(f"{func.__name__} memory usage: {memory_delta:+.2f} MB")
        return result
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


# Example usage and demo
async def main():
    """Comprehensive Performance Optimizer Demo"""
    
    # Configuration
    config = {
        'cache_size': 100,
        'cache_ttl': 300,
        'monitoring_enabled': True,
        'monitoring_interval': 10,
        'cpu_threshold': 70.0,
        'memory_threshold': 80.0,
        'response_time_threshold': 2.0,
        'error_rate_threshold': 5.0,
        'redis_enabled': False,  # Set to True if Redis is available
        'redis': {
            'url': 'redis://localhost:6379',
            'use_aioredis': True
        }
    }
    
    optimizer = PerformanceOptimizer(config)
    
    # Add alert handler
    def alert_handler(alert_data):
        print(f"🚨 ALERT: {alert_data['message']}")
    
    optimizer.add_alert_handler(alert_handler)
    
    # Start monitoring
    await optimizer.start_monitoring()
    
    # Test functions with different optimization decorators
    @optimizer.cache(cache_type='lru', key_prefix='calc')
    @optimizer.profile
    async def expensive_calculation(x: int) -> int:
        """Expensive calculation with LRU caching and profiling"""
        await asyncio.sleep(0.1)  # Simulate expensive operation
        return x * x
    
    @optimizer.cache(cache_type='ttl', ttl=60, key_prefix='data')
    @optimizer.monitor_performance(track_memory=True, track_cpu=True)
    async def fetch_data(data_id: str) -> Dict[str, Any]:
        """Data fetching with TTL caching and performance monitoring"""
        await asyncio.sleep(0.05)  # Simulate I/O operation
        return {
            'id': data_id,
            'data': f'Sample data for {data_id}',
            'timestamp': datetime.now().isoformat()
        }
    
    @performance_timer
    async def simple_operation(value: int) -> int:
        """Simple operation with timer"""
        await asyncio.sleep(0.01)
        return value + 10
    
    @memory_usage_tracker
    def memory_intensive_operation():
        """Memory intensive operation"""
        data = []
        for i in range(10000):
            data.append({
                'id': i,
                'value': i * 2,
                'timestamp': datetime.now().isoformat()
            })
        return len(data)
    
    # Test different caching scenarios
    print("\n" + "="*60)
    print("TESTING CACHING AND PROFILING")
    print("="*60)
    
    # Test LRU caching
    print("\n🔄 Testing LRU Cache:")
    for i in range(5):
        result = await expensive_calculation(5)
        print(f"  Call {i+1}: Result = {result}")
    
    # Test TTL caching
    print("\n⏰ Testing TTL Cache:")
    for i in range(3):
        result = await fetch_data(f"user_{i}")
        print(f"  Call {i+1}: {result['id']} - {result['timestamp']}")
    
    # Test simple operations
    print("\n⚡ Testing Simple Operations:")
    for i in range(3):
        result = await simple_operation(i)
        print(f"  Operation {i+1}: {result}")
    
    # Test memory operations
    print("\n💾 Testing Memory Operations:")
    count = memory_intensive_operation()
    print(f"  Memory operation result: {count} items created")
    
    # Test request tracking
    print("\n📊 Testing Request Tracking:")
    optimizer.track_request("GET /api/test", 0.5, 200)
    optimizer.track_request("GET /api/test", 0.3, 200)
    optimizer.track_request("POST /api/data", 1.2, 201)
    optimizer.track_request("GET /api/error", 0.8, 500)
    
    # Test health check
    print("\n🏥 Testing Health Check:")
    health = await optimizer.health_check()
    print(f"  Health Status: {health['status']}")
    print(f"  Issues: {health['issues']}")
    print(f"  Metrics: {health['metrics']}")
    
    # Wait a bit for monitoring data
    print("\n⏳ Waiting for monitoring data...")
    await asyncio.sleep(15)
    
    # Print comprehensive report
    print("\n" + "="*60)
    print("COMPREHENSIVE PERFORMANCE REPORT")
    print("="*60)
    optimizer.print_report()
    
    # Export metrics
    print("\n📁 Exporting Metrics:")
    json_file = optimizer.export_metrics(format='json')
    txt_file = optimizer.export_metrics(format='txt')
    print(f"  JSON report: {json_file}")
    print(f"  TXT report: {txt_file}")
    
    # Test memory optimization
    print("\n🧹 Testing Memory Optimization:")
    await optimizer.optimize_memory()
    
    # Test cache invalidation
    print("\n🗑️ Testing Cache Invalidation:")
    await optimizer.invalidate_cache(pattern='calc', cache_type='lru')
    
    # Stop monitoring
    print("\n⏹️ Stopping monitoring...")
    await optimizer.stop_monitoring()
    
    # Cleanup
    print("\n🧽 Cleanup...")
    await optimizer.cleanup()
    
    print("\n✅ Demo completed successfully!")


async def fastapi_demo():
    """FastAPI integration demo"""
    if not FASTAPI_AVAILABLE:
        print("FastAPI not available. Install with: pip install fastapi")
        return
    
    from fastapi import FastAPI
    import uvicorn
    
    # Create FastAPI app
    app = FastAPI(title="Performance Optimizer Demo", version="1.0.0")
    
    # Initialize optimizer
    optimizer = PerformanceOptimizer({
        'monitoring_enabled': True,
        'monitoring_interval': 30,
        'cache_size': 200
    })
    
    # Setup FastAPI optimization
    app = await setup_fastapi_optimization(
        app, 
        optimizer,
        health_endpoint="/health",
        metrics_endpoint="/metrics"
    )
    
    # Add some test endpoints
    @app.get("/api/data/{item_id}")
    @optimizer.cache(cache_type='lru', key_prefix='api_data')
    async def get_data(item_id: int):
        """Get data with caching"""
        await asyncio.sleep(0.1)
        return {
            "id": item_id,
            "name": f"Item {item_id}",
            "value": item_id * 100
        }
    
    @app.post("/api/process")
    async def process_data(data: dict):
        """Process data with profiling"""
        await optimizer.profiler.profile(lambda: asyncio.sleep(0.05))
        return {"message": "Data processed", "result": data}
    
    # Start server
    print("Starting FastAPI demo server...")
    print("Visit http://localhost:8000/health and http://localhost:8000/metrics")
    print("Press Ctrl+C to stop")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\nShutting down...")
        await optimizer.cleanup()


if __name__ == '__main__':
    import sys
    
    print("🚀 FastAPI Performance Optimizer Demo")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'fastapi':
        # Run FastAPI demo
        print("Running FastAPI integration demo...")
        asyncio.run(fastapi_demo())
    else:
        # Run basic demo
        print("Running comprehensive performance optimizer demo...")
        asyncio.run(main())
