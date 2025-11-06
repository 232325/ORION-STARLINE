"""
Performance Optimization Engine - Orion Starline AI Trading System
================================================================

Bu modul javob vaqti, resurslarni optimizatsiya qilish va AI modellarning 
ishlab chiqarish samaradorligini yaxshilash uchun mo'ljallangan.

Asosiy Funksiyalar:
- Response Time Optimization: Javob vaqtini qisqartirish
- Intelligent Caching: Redis/Memory caching strategiyalari
- Load Balancing: Resource yuklarni taqsimlash
- Model Switching: Dinamik model tanlash
- Resource Management: Memory va CPU optimizatsiya
- Cost Optimization: API narxini pasaytirish
- Async Processing: Asinxron ishlov berish
- Auto-scaling: Avtomatik масштабландыру

Foydalanish:
```python
from ai_modules.performance_optimization import (
    PerformanceOptimizer, 
    CacheManager, 
    LoadBalancer, 
    ModelManager,
    ResourceMonitor
)

# Performance optimization
optimizer = PerformanceOptimizer()
await optimizer.optimize_system()

# Cache management
cache = CacheManager()
result = await cache.get_cached_result("key", compute_function)

# Load balancing
balancer = LoadBalancer()
node = await balancer.select_best_node()
```
"""

import asyncio
import logging
import time
import json
import redis
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import asynccontextmanager
from enum import Enum
import weakref
import functools
import hashlib
import pickle
import gc
import sys
import os
import resource
from abc import ABC, abstractmethod

# Logging setup
logger = logging.getLogger(__name__)

# =============================================================================
# DATA STRUCTURES AND ENUMS
# =============================================================================

class OptimizationLevel(Enum):
    """Optimizatsiya darajalari"""
    MINIMAL = "minimal"      # Kam o'zgarish
    MODERATE = "moderate"    # O'rtacha optimizatsiya
    AGGRESSIVE = "aggressive" # Faol optimizatsiya
    MAXIMUM = "maximum"      # Maksimal optimizatsiya

class CacheStrategy(Enum):
    """Caching strategiyalari"""
    LRU = "lru"              # Least Recently Used
    LFU = "lfu"              # Least Frequently Used
    TTL = "ttl"              # Time To Live
    ADAPTIVE = "adaptive"    # Adaptive caching

class LoadBalanceStrategy(Enum):
    """Load balancing strategiyalari"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    FASTEST_RESPONSE = "fastest_response"

class ModelType(Enum):
    """Model turlari"""
    OPENAI_GPT = "openai_gpt"
    ANTHROPIC_CLAUDE = "anthropic_claude"
    HUGGING_FACE = "hugging_face"
    LOCAL_MODEL = "local_model"

@dataclass
class PerformanceMetrics:
    """Performance metrikalari"""
    response_time: float
    throughput: float
    memory_usage: float
    cpu_usage: float
    cache_hit_rate: float
    error_rate: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ResourceUsage:
    """Resurs foydalanish ma'lumotlari"""
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_usage: float
    network_io: Dict[str, int]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CostMetrics:
    """Xarajat metrikalari"""
    api_calls: int
    total_cost: float
    cost_per_request: float
    model_costs: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CacheEntry:
    """Cache yozuvi"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl: Optional[int] = None

@dataclass
class LoadBalancedNode:
    """Load balanced tugun"""
    node_id: str
    host: str
    port: int
    weight: float = 1.0
    current_load: int = 0
    response_time: float = 0.0
    last_health_check: datetime = field(default_factory=datetime.now)
    is_healthy: bool = True

@dataclass
class ModelPerformance:
    """Model performance ma'lumotlari"""
    model_type: ModelType
    model_name: str
    response_time: float
    accuracy: float
    cost_per_request: float
    usage_count: int
    last_used: datetime

# =============================================================================
# ABSTRACT BASE CLASSES
# =============================================================================

class CacheBackend(ABC):
    """Cache backend abstract class"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        pass

class ModelProvider(ABC):
    """Model provider abstract class"""
    
    @abstractmethod
    async def process_request(self, prompt: str, **kwargs) -> Any:
        pass
    
    @abstractmethod
    def get_cost(self, token_count: int) -> float:
        pass

# =============================================================================
# MEMORY CACHE IMPLEMENTATION
# =============================================================================

class MemoryCache(CacheBackend):
    """In-memory cache implementation"""
    
    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.strategy = strategy
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: deque = deque()
        self._lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Cache'dan qiymat olish"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                
                # TTL tekshirish
                if entry.ttl:
                    age = (datetime.now() - entry.created_at).total_seconds()
                    if age > entry.ttl:
                        del self._cache[key]
                        return None
                
                # Access tracking
                entry.accessed_at = datetime.now()
                entry.access_count += 1
                
                # Move to end for LRU
                if self.strategy == CacheStrategy.LRU:
                    if key in self._access_order:
                        self._access_order.remove(key)
                    self._access_order.append(key)
                
                return entry.value
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Cache'ga qiymat saqlash"""
        with self._lock:
            # Check if we need to evict
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict()
            
            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                ttl=ttl
            )
            
            self._cache[key] = entry
            
            if self.strategy == CacheStrategy.LRU:
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)
            
            return True
    
    async def delete(self, key: str) -> bool:
        """Cache'dan o'chirish"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return True
            return False
    
    async def clear(self) -> bool:
        """Butun cache'ni tozalash"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            return True
    
    async def _evict(self):
        """Evict entry according to strategy"""
        if not self._cache:
            return
        
        if self.strategy == CacheStrategy.LRU and self._access_order:
            # Remove least recently used
            key = self._access_order.popleft()
            del self._cache[key]
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            lfu_key = min(self._cache.keys(), 
                         key=lambda k: self._cache[k].access_count)
            del self._cache[lfu_key]
            if lfu_key in self._access_order:
                self._access_order.remove(lfu_key)
        else:
            # Remove random entry
            key = next(iter(self._cache.keys()))
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Cache statistikalari"""
        with self._lock:
            total_requests = sum(entry.access_count for entry in self._cache.values())
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "strategy": self.strategy.value,
                "total_requests": total_requests,
                "hit_rate": total_requests / max(1, len(self._cache))
            }

# =============================================================================
# REDIS CACHE IMPLEMENTATION
# =============================================================================

class RedisCache(CacheBackend):
    """Redis cache implementation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 default_ttl: int = 3600):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._client: Optional[redis.Redis] = None
        self._connected = False
    
    def _get_client(self) -> redis.Redis:
        """Redis client olish"""
        if not self._client:
            try:
                self._client = redis.from_url(self.redis_url)
                self._client.ping()
                self._connected = True
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self._connected = False
                # Fallback to in-memory
                self._client = None
        return self._client
    
    async def get(self, key: str) -> Optional[Any]:
        """Redis'dan qiymat olish"""
        client = self._get_client()
        if not client or not self._connected:
            return None
        
        try:
            data = client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Redis'ga qiymat saqlash"""
        client = self._get_client()
        if not client or not self._connected:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            data = pickle.dumps(value)
            client.setex(key, ttl, data)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Redis'dan o'chirish"""
        client = self._get_client()
        if not client or not self._connected:
            return False
        
        try:
            return bool(client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Redis'ni tozalash"""
        client = self._get_client()
        if not client or not self._connected:
            return False
        
        try:
            client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False

# =============================================================================
# CACHE MANAGER
# =============================================================================

class CacheManager:
    """Keng qamrovli cache manager"""
    
    def __init__(self, backend: Optional[CacheBackend] = None,
                 memory_cache: Optional[MemoryCache] = None,
                 redis_cache: Optional[RedisCache] = None):
        self.memory_cache = memory_cache or MemoryCache()
        self.redis_cache = redis_cache
        self.backend = backend or self.memory_cache
        self.hits = 0
        self.misses = 0
        self._stats_lock = threading.RLock()
    
    async def get_cached_result(self, key: str, 
                              compute_function: Callable,
                              ttl: Optional[int] = None) -> Any:
        """Cached natija olish yoki hisoblash"""
        # Try memory cache first
        result = await self.backend.get(key)
        
        with self._stats_lock:
            if result is not None:
                self.hits += 1
                return result
            else:
                self.misses += 1
        
        # Compute if not in cache
        try:
            if asyncio.iscoroutinefunction(compute_function):
                result = await compute_function()
            else:
                result = compute_function()
            
            # Store in cache
            await self.backend.set(key, result, ttl)
            return result
        except Exception as e:
            logger.error(f"Cache compute error: {e}")
            raise
    
    def cache_key(self, *args, **kwargs) -> str:
        """Cache kalit yaratish"""
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Cache statistikalari"""
        with self._stats_lock:
            total = self.hits + self.misses
            hit_rate = self.hits / max(1, total)
            
            backend_stats = getattr(self.backend, 'get_stats', lambda: {})()
            
            return {
                "hits": self.hits,
                "misses": self.misses,
                "total": total,
                "hit_rate": hit_rate,
                "backend": type(self.backend).__name__,
                "backend_stats": backend_stats
            }

# =============================================================================
# LOAD BALANCER
# =============================================================================

class LoadBalancer:
    """Load balancer implementation"""
    
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.nodes: Dict[str, LoadBalancedNode] = {}
        self.current_index = 0
        self._lock = threading.RLock()
    
    def add_node(self, node: LoadBalancedNode):
        """Tugun qo'shish"""
        with self._lock:
            self.nodes[node.node_id] = node
            logger.info(f"Added node: {node.node_id}")
    
    def remove_node(self, node_id: str):
        """Tugun o'chirish"""
        with self._lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
                logger.info(f"Removed node: {node_id}")
    
    async def select_best_node(self) -> Optional[LoadBalancedNode]:
        """Eng yaxshi tugun tanlash"""
        with self._lock:
            healthy_nodes = [node for node in self.nodes.values() 
                           if node.is_healthy]
            
            if not healthy_nodes:
                return None
            
            if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
                return self._select_round_robin(healthy_nodes)
            elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
                return self._select_least_connections(healthy_nodes)
            elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
                return self._select_weighted_round_robin(healthy_nodes)
            elif self.strategy == LoadBalanceStrategy.FASTEST_RESPONSE:
                return self._select_fastest_response(healthy_nodes)
            
            return healthy_nodes[0]
    
    def _select_round_robin(self, nodes: List[LoadBalancedNode]) -> LoadBalancedNode:
        """Round-robin selection"""
        node = nodes[self.current_index % len(nodes)]
        self.current_index += 1
        return node
    
    def _select_least_connections(self, nodes: List[LoadBalancedNode]) -> LoadBalancedNode:
        """Least connections selection"""
        return min(nodes, key=lambda n: n.current_load)
    
    def _select_weighted_round_robin(self, nodes: List[LoadBalancedNode]) -> LoadBalancedNode:
        """Weighted round-robin selection"""
        total_weight = sum(node.weight for node in nodes)
        import random
        target = random.uniform(0, total_weight)
        current = 0
        
        for node in nodes:
            current += node.weight
            if current >= target:
                return node
        
        return nodes[-1]
    
    def _select_fastest_response(self, nodes: List[LoadBalancedNode]) -> LoadBalancedNode:
        """Fastest response selection"""
        return min(nodes, key=lambda n: n.response_time)
    
    def update_node_load(self, node_id: str, response_time: float):
        """Tugun yukini yangilash"""
        with self._lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.response_time = response_time
                node.last_health_check = datetime.now()
    
    def health_check(self):
        """Sog'liq tekshirish"""
        with self._lock:
            for node in self.nodes.values():
                # Simple health check - in real implementation, 
                # you'd make actual HTTP requests
                node.is_healthy = True
                node.last_health_check = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """Load balancer statistikalari"""
        with self._lock:
            return {
                "total_nodes": len(self.nodes),
                "healthy_nodes": sum(1 for n in self.nodes.values() if n.is_healthy),
                "strategy": self.strategy.value,
                "nodes": [
                    {
                        "id": node.node_id,
                        "load": node.current_load,
                        "response_time": node.response_time,
                        "healthy": node.is_healthy,
                        "weight": node.weight
                    }
                    for node in self.nodes.values()
                ]
            }

# =============================================================================
# MODEL MANAGER
# =============================================================================

class ModelManager:
    """Dynamic model selection va management"""
    
    def __init__(self):
        self.models: Dict[str, ModelProvider] = {}
        self.performance_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        self.cost_tracker: Dict[str, float] = defaultdict(float)
        self.usage_count: Dict[str, int] = defaultdict(int)
        self._lock = threading.RLock()
    
    def register_model(self, model_id: str, provider: ModelProvider, 
                      model_type: ModelType):
        """Model ro'yxatga olish"""
        with self._lock:
            self.models[model_id] = {
                "provider": provider,
                "type": model_type,
                "registered_at": datetime.now()
            }
            logger.info(f"Registered model: {model_id}")
    
    async def select_optimal_model(self, 
                                 task_type: str = "general",
                                 cost_budget: Optional[float] = None,
                                 latency_requirement: Optional[float] = None) -> Optional[str]:
        """Optimal model tanlash"""
        with self._lock:
            if not self.models:
                return None
            
            candidates = []
            
            for model_id, model_info in self.models.items():
                performance = self._get_model_performance(model_id)
                if performance:
                    candidates.append((model_id, model_info, performance))
            
            if not candidates:
                return list(self.models.keys())[0]
            
            # Score models
            scores = []
            for model_id, model_info, perf in candidates:
                score = self._calculate_model_score(
                    perf, cost_budget, latency_requirement
                )
                scores.append((score, model_id, model_info, perf))
            
            # Return best scored model
            scores.sort(key=lambda x: x[0], reverse=True)
            return scores[0][1] if scores else None
    
    def _get_model_performance(self, model_id: str) -> Optional[ModelPerformance]:
        """Model performance ma'lumotlari"""
        history = self.performance_history[model_id]
        if not history:
            return None
        
        avg_response_time = sum(h.response_time for h in history) / len(history)
        avg_accuracy = sum(h.accuracy for h in history) / len(history)
        total_usage = self.usage_count[model_id]
        
        return ModelPerformance(
            model_type=self.models[model_id]["type"],
            model_name=model_id,
            response_time=avg_response_time,
            accuracy=avg_accuracy,
            cost_per_request=self.cost_tracker[model_id] / max(1, total_usage),
            usage_count=total_usage,
            last_used=max((h.timestamp for h in history), default=datetime.now())
        )
    
    def _calculate_model_score(self, perf: ModelPerformance, 
                             cost_budget: Optional[float],
                             latency_requirement: Optional[float]) -> float:
        """Model scoring"""
        score = 0.0
        
        # Accuracy weight (40%)
        score += perf.accuracy * 0.4
        
        # Response time weight (30%) - inverse relationship
        if latency_requirement and perf.response_time > 0:
            time_score = max(0, 1 - (perf.response_time / latency_requirement))
            score += time_score * 0.3
        
        # Cost weight (20%) - inverse relationship
        if cost_budget and perf.cost_per_request > 0:
            cost_score = max(0, 1 - (perf.cost_per_request / cost_budget))
            score += cost_score * 0.2
        
        # Usage weight (10%) - favor models with good usage
        if perf.usage_count > 0:
            usage_score = min(1.0, perf.usage_count / 1000)  # Normalize to 1000
            score += usage_score * 0.1
        
        return score
    
    async def record_performance(self, model_id: str, 
                               response_time: float, 
                               accuracy: float,
                               cost: float):
        """Performance yozib olish"""
        with self._lock:
            self.performance_history[model_id].append(
                ModelPerformance(
                    model_type=self.models[model_id]["type"],
                    model_name=model_id,
                    response_time=response_time,
                    accuracy=accuracy,
                    cost_per_request=cost,
                    usage_count=1,
                    last_used=datetime.now()
                )
            )
            self.cost_tracker[model_id] += cost
            self.usage_count[model_id] += 1
    
    def get_model_comparison(self) -> Dict[str, Any]:
        """Model taqqoslash"""
        with self._lock:
            comparison = {}
            
            for model_id in self.models.keys():
                perf = self._get_model_performance(model_id)
                if perf:
                    comparison[model_id] = {
                        "response_time": perf.response_time,
                        "accuracy": perf.accuracy,
                        "cost_per_request": perf.cost_per_request,
                        "usage_count": perf.usage_count,
                        "total_cost": self.cost_tracker[model_id]
                    }
            
            return comparison

# =============================================================================
# RESOURCE MONITOR
# =============================================================================

class ResourceMonitor:
    """Resurs monitoring"""
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.resource_history: deque = deque(maxlen=1000)
        self.alerts: List[Dict] = []
        self._lock = threading.RLock()
    
    def start_monitoring(self):
        """Monitoring boshlash"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Monitoring to'xtatish"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self):
        """Monitoring loop"""
        while self.is_monitoring:
            try:
                usage = self.get_current_usage()
                
                with self._lock:
                    self.resource_history.append(usage)
                    self._check_alerts(usage)
                
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(self.monitoring_interval)
    
    def get_current_usage(self) -> ResourceUsage:
        """Hozirgi resurs foydalanish"""
        # CPU va memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_mb=memory.used / (1024 * 1024),
            disk_usage=disk.percent,
            network_io={
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        )
    
    def _check_alerts(self, usage: ResourceUsage):
        """Ogohlantirish tekshirish"""
        alerts = []
        
        # CPU alert
        if usage.cpu_percent > 90:
            alerts.append({
                "type": "cpu_high",
                "message": f"CPU usage: {usage.cpu_percent:.1f}%",
                "severity": "high",
                "timestamp": datetime.now()
            })
        
        # Memory alert
        if usage.memory_percent > 90:
            alerts.append({
                "type": "memory_high",
                "message": f"Memory usage: {usage.memory_percent:.1f}%",
                "severity": "high",
                "timestamp": datetime.now()
            })
        
        # Disk alert
        if usage.disk_usage > 95:
            alerts.append({
                "type": "disk_high",
                "message": f"Disk usage: {usage.disk_usage:.1f}%",
                "severity": "critical",
                "timestamp": datetime.now()
            })
        
        if alerts:
            self.alerts.extend(alerts)
            for alert in alerts:
                logger.warning(f"Resource alert: {alert['message']}")
    
    def get_resource_stats(self, period: int = 60) -> Dict[str, Any]:
        """Resurs statistikalari"""
        with self._lock:
            recent_usage = list(self.resource_history)[-period:]
            
            if not recent_usage:
                return {"error": "No data available"}
            
            cpu_values = [u.cpu_percent for u in recent_usage]
            memory_values = [u.memory_percent for u in recent_usage]
            
            return {
                "period_seconds": period,
                "samples": len(recent_usage),
                "cpu": {
                    "avg": sum(cpu_values) / len(cpu_values),
                    "min": min(cpu_values),
                    "max": max(cpu_values)
                },
                "memory": {
                    "avg": sum(memory_values) / len(memory_values),
                    "min": min(memory_values),
                    "max": max(memory_values)
                },
                "alerts_count": len([a for a in self.alerts 
                                   if a["timestamp"] > datetime.now() - timedelta(seconds=period)])
            }
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict]:
        """So'nggi ogohlantirishlar"""
        with self._lock:
            return list(self.alerts)[-count:]

# =============================================================================
# COST TRACKER
# =============================================================================

class CostTracker:
    """API xarajatlarini kuzatish"""
    
    def __init__(self):
        self.cost_history: deque = deque(maxlen=10000)
        self.model_costs: Dict[str, float] = defaultdict(float)
        self.daily_budget: Optional[float] = None
        self.monthly_budget: Optional[float] = None
        self._lock = threading.RLock()
    
    def set_budgets(self, daily: Optional[float] = None, 
                   monthly: Optional[float] = None):
        """Budgetlar belgilash"""
        with self._lock:
            self.daily_budget = daily
            self.monthly_budget = monthly
    
    def record_api_call(self, model_id: str, tokens: int, cost: float,
                       response_time: float):
        """API chaqiruv yozib olish"""
        with self._lock:
            metrics = CostMetrics(
                api_calls=1,
                total_cost=cost,
                cost_per_request=cost,
                model_costs={model_id: cost}
            )
            self.cost_history.append(metrics)
            self.model_costs[model_id] += cost
    
    def get_cost_analysis(self, period_hours: int = 24) -> Dict[str, Any]:
        """Xarajat tahlili"""
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=period_hours)
            recent_costs = [c for c in self.cost_history 
                          if c.timestamp > cutoff]
            
            if not recent_costs:
                return {"error": "No cost data available"}
            
            total_cost = sum(c.total_cost for c in recent_costs)
            total_calls = sum(c.api_calls for c in recent_costs)
            
            model_breakdown = defaultdict(float)
            for c in recent_costs:
                for model, cost in c.model_costs.items():
                    model_breakdown[model] += cost
            
            analysis = {
                "period_hours": period_hours,
                "total_cost": total_cost,
                "total_calls": total_calls,
                "avg_cost_per_call": total_cost / max(1, total_calls),
                "model_breakdown": dict(model_breakdown),
                "daily_average": total_cost / (period_hours / 24)
            }
            
            # Budget checks
            if self.daily_budget:
                analysis["daily_budget_usage"] = min(100, 
                                                   (total_cost / self.daily_budget) * 100)
                analysis["daily_budget_remaining"] = max(0, 
                                                       self.daily_budget - total_cost)
            
            if self.monthly_budget:
                analysis["monthly_budget_usage"] = min(100, 
                                                     (total_cost / self.monthly_budget) * 100)
                analysis["monthly_budget_remaining"] = max(0, 
                                                        self.monthly_budget - total_cost)
            
            return analysis
    
    def get_optimization_suggestions(self) -> List[str]:
        """Optimizatsiya takliflar"""
        suggestions = []
        analysis = self.get_cost_analysis(24)
        
        if "error" in analysis:
            return ["Xarajat ma'lumotlari mavjud emas"]
        
        # Model cost comparison
        model_costs = analysis.get("model_breakdown", {})
        if model_costs:
            most_expensive = max(model_costs.items(), key=lambda x: x[1])
            suggestions.append(
                f"Eng qimmat model: {most_expensive[0]} "
                f"(${most_expensive[1]:.2f})"
            )
        
        # High cost detection
        if analysis.get("total_cost", 0) > 100:
            suggestions.append("Yuqori xarajat - model tanlashni qayta ko'rib chiqish kerak")
        
        # Frequency analysis
        if analysis.get("total_calls", 0) > 1000:
            suggestions.append("Ko'p API chaqiruvlari - caching strategiyalarini kuchaytirish")
        
        return suggestions

# =============================================================================
# ASYNC PROCESSING OPTIMIZER
# =============================================================================

class AsyncProcessor:
    """Asinxron processing optimizatsiya"""
    
    def __init__(self, max_workers: int = 10, batch_size: int = 50):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.processed_count = 0
        self.failed_count = 0
        self._processing = False
    
    async def process_batch(self, tasks: List[Callable], 
                          process_function: Callable) -> List[Any]:
        """Batch processing"""
        results = []
        
        # Process in batches
        for i in range(0, len(tasks), self.batch_size):
            batch = tasks[i:i + self.batch_size]
            batch_results = await self._process_batch_async(batch, process_function)
            results.extend(batch_results)
        
        return results
    
    async def _process_batch_async(self, batch: List[Callable], 
                                 process_function: Callable) -> List[Any]:
        """Asinxron batch processing"""
        loop = asyncio.get_event_loop()
        
        # Create tasks for concurrent execution
        tasks = []
        for task in batch:
            if asyncio.iscoroutinefunction(process_function):
                tasks.append(asyncio.create_task(process_function(task)))
            else:
                tasks.append(loop.run_in_executor(self.executor, process_function, task))
        
        # Wait for all tasks to complete
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter results and handle exceptions
        results = []
        for result in completed_tasks:
            if isinstance(result, Exception):
                self.failed_count += 1
                logger.error(f"Batch processing error: {result}")
            else:
                results.append(result)
                self.processed_count += 1
        
        return results
    
    async def process_streaming(self, data_stream: Any, 
                              process_function: Callable) -> AsyncIterator[Any]:
        """Streaming data processing"""
        self._processing = True
        
        try:
            async for item in data_stream:
                if not self._processing:
                    break
                
                # Process item
                if asyncio.iscoroutinefunction(process_function):
                    result = await process_function(item)
                else:
                    result = process_function(item)
                
                yield result
                
        finally:
            self._processing = False
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Processing statistikalari"""
        return {
            "processed": self.processed_count,
            "failed": self.failed_count,
            "success_rate": self.processed_count / max(1, self.processed_count + self.failed_count),
            "max_workers": self.max_workers,
            "batch_size": self.batch_size,
            "is_processing": self._processing
        }

# =============================================================================
# AUTO-SCALING MANAGER
# =============================================================================

class AutoScaler:
    """Avtomatik масштабландыру manager"""
    
    def __init__(self, resource_monitor: ResourceMonitor):
        self.resource_monitor = resource_monitor
        self.scaling_rules: List[Dict] = []
        self.scale_up_thresholds = {
            "cpu": 80,
            "memory": 80,
            "queue_size": 100
        }
        self.scale_down_thresholds = {
            "cpu": 30,
            "memory": 30,
            "queue_size": 10
        }
        self.scaling_history: List[Dict] = []
        self._lock = threading.RLock()
    
    def add_scaling_rule(self, metric: str, threshold: float, 
                        action: str, cooldown: int = 60):
        """Scaling qoida qo'shish"""
        with self._lock:
            self.scaling_rules.append({
                "metric": metric,
                "threshold": threshold,
                "action": action,  # "scale_up" or "scale_down"
                "cooldown": cooldown,
                "last_triggered": None
            })
    
    async def check_scaling_conditions(self) -> List[str]:
        """Scaling shartlarini tekshirish"""
        with self._lock:
            actions = []
            current_time = datetime.now()
            
            # Get current resource usage
            usage = self.resource_monitor.get_current_usage()
            
            for rule in self.scaling_rules:
                # Check cooldown
                if (rule["last_triggered"] and 
                    (current_time - rule["last_triggered"]).total_seconds() < rule["cooldown"]):
                    continue
                
                # Check metric
                metric_value = self._get_metric_value(usage, rule["metric"])
                if metric_value is None:
                    continue
                
                # Check if threshold is met
                if ((rule["action"] == "scale_up" and metric_value > rule["threshold"]) or
                    (rule["action"] == "scale_down" and metric_value < rule["threshold"])):
                    
                    actions.append(f"{rule['action']}: {rule['metric']} = {metric_value:.1f}")
                    rule["last_triggered"] = current_time
                    
                    # Record scaling action
                    self.scaling_history.append({
                        "timestamp": current_time,
                        "action": rule["action"],
                        "metric": rule["metric"],
                        "value": metric_value,
                        "threshold": rule["threshold"]
                    })
            
            return actions
    
    def _get_metric_value(self, usage: ResourceUsage, metric: str) -> Optional[float]:
        """Metrik qiymatini olish"""
        if metric == "cpu":
            return usage.cpu_percent
        elif metric == "memory":
            return usage.memory_percent
        elif metric == "disk":
            return usage.disk_usage
        return None
    
    async def execute_scaling_action(self, action: str) -> bool:
        """Scaling action bajarish"""
        logger.info(f"Executing scaling action: {action}")
        
        try:
            if action.startswith("scale_up"):
                return await self._scale_up()
            elif action.startswith("scale_down"):
                return await self._scale_down()
            return False
        except Exception as e:
            logger.error(f"Scaling action failed: {e}")
            return False
    
    async def _scale_up(self) -> bool:
        """Scale up"""
        # In a real implementation, this would:
        # - Add more instances
        # - Increase resource allocation
        # - Start additional workers
        logger.info("Scaling up resources")
        return True
    
    async def _scale_down(self) -> bool:
        """Scale down"""
        # In a real implementation, this would:
        # - Remove instances
        # - Decrease resource allocation
        # - Stop unnecessary workers
        logger.info("Scaling down resources")
        return True
    
    def get_scaling_stats(self) -> Dict[str, Any]:
        """Scaling statistikalari"""
        with self._lock:
            return {
                "total_scaling_actions": len(self.scaling_history),
                "scale_up_count": len([a for a in self.scaling_history if a["action"] == "scale_up"]),
                "scale_down_count": len([a for a in self.scaling_history if a["action"] == "scale_down"]),
                "rules_count": len(self.scaling_rules),
                "recent_actions": self.scaling_history[-10:] if self.scaling_history else []
            }

# =============================================================================
# MAIN PERFORMANCE OPTIMIZER
# =============================================================================

class PerformanceOptimizer:
    """Asosiy performance optimization tizimi"""
    
    def __init__(self, optimization_level: OptimizationLevel = OptimizationLevel.MODERATE):
        self.optimization_level = optimization_level
        self.cache_manager = CacheManager()
        self.load_balancer = LoadBalancer()
        self.model_manager = ModelManager()
        self.resource_monitor = ResourceMonitor()
        self.cost_tracker = CostTracker()
        self.async_processor = AsyncProcessor()
        self.auto_scaler = AutoScaler(self.resource_monitor)
        
        # Start monitoring
        self.resource_monitor.start_monitoring()
        
        # Setup default scaling rules
        self._setup_default_scaling_rules()
    
    def _setup_default_scaling_rules(self):
        """Default scaling qoidalari"""
        for threshold, metric in [("cpu", "cpu"), ("memory", "memory")]:
            self.auto_scaler.add_scaling_rule(metric, 80, "scale_up", 300)
            self.auto_scaler.add_scaling_rule(metric, 30, "scale_down", 600)
    
    async def optimize_system(self) -> Dict[str, Any]:
        """Tizimni optimizatsiya qilish"""
        logger.info("Starting system optimization...")
        
        optimization_results = {
            "timestamp": datetime.now(),
            "level": self.optimization_level.value,
            "optimizations": []
        }
        
        try:
            # 1. Resource optimization
            resource_result = await self._optimize_resources()
            optimization_results["optimizations"].append(("resources", resource_result))
            
            # 2. Cache optimization
            cache_result = await self._optimize_caching()
            optimization_results["optimizations"].append(("caching", cache_result))
            
            # 3. Load balancing optimization
            load_balance_result = await self._optimize_load_balancing()
            optimization_results["optimizations"].append(("load_balancing", load_balance_result))
            
            # 4. Model optimization
            model_result = await self._optimize_models()
            optimization_results["optimizations"].append(("models", model_result))
            
            # 5. Async processing optimization
            async_result = await self._optimize_async_processing()
            optimization_results["optimizations"].append(("async_processing", async_result))
            
            # 6. Auto-scaling check
            scaling_result = await self._check_scaling()
            optimization_results["optimizations"].append(("auto_scaling", scaling_result))
            
            optimization_results["status"] = "completed"
            logger.info("System optimization completed successfully")
            
        except Exception as e:
            optimization_results["status"] = "error"
            optimization_results["error"] = str(e)
            logger.error(f"Optimization error: {e}")
        
        return optimization_results
    
    async def _optimize_resources(self) -> Dict[str, Any]:
        """Resurs optimizatsiyasi"""
        # Force garbage collection
        collected = gc.collect()
        
        # Get current usage
        usage = self.resource_monitor.get_current_usage()
        
        results = {
            "garbage_collected": collected,
            "memory_usage": usage.memory_percent,
            "cpu_usage": usage.cpu_percent,
            "recommendations": []
        }
        
        # Add recommendations
        if usage.memory_percent > 80:
            results["recommendations"].append("Memory usage is high - consider optimization")
        
        if usage.cpu_percent > 80:
            results["recommendations"].append("CPU usage is high - consider load balancing")
        
        return results
    
    async def _optimize_caching(self) -> Dict[str, Any]:
        """Caching optimizatsiyasi"""
        stats = self.cache_manager.get_cache_stats()
        
        results = {
            "cache_hit_rate": stats.get("hit_rate", 0),
            "cache_size": stats.get("size", 0),
            "recommendations": []
        }
        
        # Recommendations based on hit rate
        if stats.get("hit_rate", 0) < 0.7:
            results["recommendations"].append(
                "Low cache hit rate - consider improving cache key strategy"
            )
        
        if stats.get("size", 0) / stats.get("max_size", 1) > 0.9:
            results["recommendations"].append(
                "Cache is near capacity - consider increasing cache size"
            )
        
        return results
    
    async def _optimize_load_balancing(self) -> Dict[str, Any]:
        """Load balancing optimizatsiyasi"""
        stats = self.load_balancer.get_stats()
        
        results = {
            "total_nodes": stats.get("total_nodes", 0),
            "healthy_nodes": stats.get("healthy_nodes", 0),
            "recommendations": []
        }
        
        # Health check
        self.load_balancer.health_check()
        updated_stats = self.load_balancer.get_stats()
        
        if updated_stats.get("healthy_nodes", 0) < stats.get("total_nodes", 0):
            results["recommendations"].append(
                "Some nodes are unhealthy - check node status"
            )
        
        return results
    
    async def _optimize_models(self) -> Dict[str, Any]:
        """Model optimizatsiyasi"""
        comparison = self.model_manager.get_model_comparison()
        
        results = {
            "model_count": len(self.model_manager.models),
            "comparisons": comparison,
            "recommendations": []
        }
        
        # Find best performing model
        if comparison:
            best_model = max(comparison.items(), 
                           key=lambda x: x[1].get("accuracy", 0))
            results["best_model"] = best_model[0]
            
            # Cost analysis
            total_cost = sum(model.get("total_cost", 0) for model in comparison.values())
            if total_cost > 100:
                results["recommendations"].append(
                    f"High total cost (${total_cost:.2f}) - consider cost optimization"
                )
        
        return results
    
    async def _optimize_async_processing(self) -> Dict[str, Any]:
        """Asinxron processing optimizatsiyasi"""
        stats = self.async_processor.get_processing_stats()
        
        results = {
            "success_rate": stats.get("success_rate", 0),
            "processing_rate": stats.get("processed", 0),
            "recommendations": []
        }
        
        # Recommendations
        if stats.get("success_rate", 1) < 0.95:
            results["recommendations"].append(
                "Low success rate - check error handling"
            )
        
        return results
    
    async def _check_scaling(self) -> Dict[str, Any]:
        """Scaling tekshirish"""
        # Check scaling conditions
        scaling_actions = await self.auto_scaler.check_scaling_conditions()
        
        results = {
            "scaling_actions": scaling_actions,
            "stats": self.auto_scaler.get_scaling_stats(),
            "recommendations": []
        }
        
        # Execute scaling actions
        for action in scaling_actions:
            await self.auto_scaler.execute_scaling_action(action)
        
        return results
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Performance dashboard ma'lumotlari"""
        return {
            "timestamp": datetime.now(),
            "optimization_level": self.optimization_level.value,
            "cache_stats": self.cache_manager.get_cache_stats(),
            "load_balancer_stats": self.load_balancer.get_stats(),
            "resource_stats": self.resource_monitor.get_resource_stats(),
            "cost_analysis": self.cost_tracker.get_cost_analysis(),
            "model_comparison": self.model_manager.get_model_comparison(),
            "async_processing_stats": self.async_processor.get_processing_stats(),
            "scaling_stats": self.auto_scaler.get_scaling_stats()
        }
    
    def get_optimization_recommendations(self) -> List[str]:
        """Optimizatsiya takiflari"""
        recommendations = []
        
        # Cache recommendations
        cache_stats = self.cache_manager.get_cache_stats()
        if cache_stats.get("hit_rate", 1) < 0.7:
            recommendations.append(
                "Cache hit rate ni yaxshilash - cache strategiyasini qayta ko'rib chiqish"
            )
        
        # Cost recommendations
        cost_suggestions = self.cost_tracker.get_optimization_suggestions()
        recommendations.extend(cost_suggestions)
        
        # Resource recommendations
        resource_stats = self.resource_monitor.get_resource_stats(1)
        if resource_stats.get("cpu", {}).get("avg", 0) > 80:
            recommendations.append(
                "CPU yuklanishi yuqori - load balancing yoki scaling kerak"
            )
        
        if resource_stats.get("memory", {}).get("avg", 0) > 80:
            recommendations.append(
                "Memory yuklanishi yuqori - garbage collection yoki resurs optimizatsiyasi kerak"
            )
        
        return recommendations
    
    async def stop(self):
        """Optimizator to'xtatish"""
        self.resource_monitor.stop_monitoring()
        self.async_processor.executor.shutdown(wait=True)
        logger.info("Performance optimizer stopped")

# =============================================================================
# DECORATORS AND HELPERS
# =============================================================================

def performance_monitor(func: Callable) -> Callable:
    """Performance monitoring decorator"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.debug(f"Function {func.__name__} took {execution_time:.4f} seconds")
    return wrapper

def cache_result(cache_manager: CacheManager, ttl: Optional[int] = None):
    """Caching decorator"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager.cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            result = await cache_manager.backend.get(cache_key)
            if result is not None:
                return result
            
            # Compute and cache
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache_manager.backend.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

def rate_limiter(max_calls: int, time_window: int = 60):
    """Rate limiting decorator"""
    def decorator(func: Callable) -> Callable:
        calls = deque()
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old calls
            while calls and now - calls[0] > time_window:
                calls.popleft()
            
            # Check limit
            if len(calls) >= max_calls:
                wait_time = time_window - (now - calls[0]) + 1
                logger.warning(f"Rate limit exceeded for {func.__name__}, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                return await wrapper(*args, **kwargs)
            
            # Record call
            calls.append(now)
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main classes
    "PerformanceOptimizer",
    "CacheManager", 
    "LoadBalancer",
    "ModelManager",
    "ResourceMonitor",
    "CostTracker",
    "AsyncProcessor",
    "AutoScaler",
    
    # Cache implementations
    "MemoryCache",
    "RedisCache",
    "CacheBackend",
    
    # Data structures
    "PerformanceMetrics",
    "ResourceUsage",
    "CostMetrics",
    "CacheEntry",
    "LoadBalancedNode",
    "ModelPerformance",
    
    # Enums
    "OptimizationLevel",
    "CacheStrategy",
    "LoadBalanceStrategy",
    "ModelType",
    
    # Decorators
    "performance_monitor",
    "cache_result",
    "rate_limiter"
]

__version__ = "1.0.0"
__author__ = "Orion Starline AI Team"