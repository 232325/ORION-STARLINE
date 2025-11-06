"""
Rate Limiting Moduli
====================

Bu modul quyidagi rate limiting algoritmlarini ta'minlaydi:
- Token Bucket Algorithm
- Sliding Window Rate Limiting
- Per-user rate limits
- API endpoint rate limits
- Burst handling

@author: Security Team
@version: 1.0.0
"""

import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque, defaultdict
from threading import Lock, RLock
import hashlib
import redis
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit konfiguratsiyasi"""
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    requests_per_day: int = 86400
    burst_limit: int = 10
    window_size: int = 60  # soniyalarda


@dataclass 
class EndpointConfig:
    """API endpoint uchun rate limit konfiguratsiyasi"""
    endpoint: str
    config: RateLimitConfig
    priority: int = 1
    exempt_users: List[str] = field(default_factory=list)


class TokenBucket:
    """Token Bucket Algorithm Implementation"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """Token iste'mol qilish"""
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Tokenlarni to'ldirish"""
        now = time.time()
        time_passed = now - self.last_refill
        
        if time_passed > 0:
            tokens_to_add = int(time_passed * self.refill_rate)
            if tokens_to_add > 0:
                self.tokens = min(self.capacity, self.tokens + tokens_to_add)
                self.last_refill = now
    
    def get_tokens(self) -> int:
        """Mavjud tokenlar sonini olish"""
        with self.lock:
            self._refill()
            return self.tokens


class SlidingWindowRateLimiter:
    """Sliding Window Rate Limiting Implementation"""
    
    def __init__(self, window_size: int = 60, max_requests: int = 60):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = defaultdict(deque)
        self.lock = RLock()
    
    def is_allowed(self, identifier: str) -> bool:
        """So'rov ruxsat berilganligini tekshirish"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_size
            
            # Eski so'rovlarni tozalash
            while (self.requests[identifier] and 
                   self.requests[identifier][0] < window_start):
                self.requests[identifier].popleft()
            
            # Limit tekshirish
            if len(self.requests[identifier]) >= self.max_requests:
                return False
            
            # Yangi so'rov qo'shish
            self.requests[identifier].append(now)
            return True
    
    def get_request_count(self, identifier: str) -> int:
        """Berilgan vaqt oralig'ida so'rovlar sonini olish"""
        with self.lock:
            now = time.time()
            window_start = now - self.window_size
            
            # Eski so'rovlarni tozalash
            while (self.requests[identifier] and 
                   self.requests[identifier][0] < window_start):
                self.requests[identifier].popleft()
            
            return len(self.requests[identifier])
    
    def reset_window(self, identifier: str):
        """Berilgan identifikator uchun oynani qayta sozlash"""
        with self.lock:
            if identifier in self.requests:
                self.requests[identifier].clear()


class LeakyBucket:
    """Leaky Bucket Algorithm Implementation"""
    
    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water = 0
        self.last_leak = time.time()
        self.lock = Lock()
    
    def process(self, water_amount: int) -> bool:
        """So'rovni qayta ishlash"""
        with self.lock:
            self._leak()
            
            if self.water + water_amount <= self.capacity:
                self.water += water_amount
                return True
            return False
    
    def _leak(self):
        """Suvni oqizish"""
        now = time.time()
        time_passed = now - self.last_leak
        
        if time_passed > 0:
            leaked = int(time_passed * self.leak_rate)
            if leaked > 0:
                self.water = max(0, self.water - leaked)
                self.last_leak = now
    
    def get_water_level(self) -> float:
        """Suv darajasini olish"""
        with self.lock:
            self._leak()
            return self.water


class RateLimiterManager:
    """Rate Limit Manager - Barcha rate limiting algoritmlarini boshqaruvchi"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
            except Exception as e:
                logger.warning(f"Redis ulanish muvaffaqiyatsiz: {e}")
        
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, SlidingWindowRateLimiter] = {}
        self.leaky_buckets: Dict[str, LeakyBucket] = {}
        self.endpoint_configs: Dict[str, EndpointConfig] = {}
        self.user_limits: Dict[str, RateLimitConfig] = {}
        self.global_config = RateLimitConfig()
        
        self.lock = RLock()
    
    def add_endpoint_config(self, config: EndpointConfig):
        """Endpoint konfiguratsiyasi qo'shish"""
        with self.lock:
            self.endpoint_configs[config.endpoint] = config
    
    def set_user_limit(self, user_id: str, config: RateLimitConfig):
        """User uchun limit belgilash"""
        with self.lock:
            self.user_limits[user_id] = config
    
    def check_rate_limit(self, identifier: str, endpoint: str = "default") -> Tuple[bool, Dict[str, int]]:
        """Rate limit tekshirish"""
        with self.lock:
            # Endpoint konfiguratsiyasini olish
            config = self.endpoint_configs.get(endpoint, EndpointConfig(endpoint, self.global_config))
            
            # Admin foydalanuvchilari uchun tekshirish
            if identifier in config.exempt_users:
                return True, {"allowed": 1, "remaining": 999}
            
            # User specific limit
            user_config = self.user_limits.get(identifier, config.config)
            
            # Token bucket tekshirish
            bucket_key = f"token:{identifier}:{endpoint}"
            if bucket_key not in self.token_buckets:
                refill_rate = user_config.requests_per_minute / 60.0
                self.token_buckets[bucket_key] = TokenBucket(user_config.burst_limit, refill_rate)
            
            token_allowed = self.token_buckets[bucket_key].consume(1)
            
            # Sliding window tekshirish  
            window_key = f"window:{identifier}:{endpoint}"
            if window_key not in self.sliding_windows:
                self.sliding_windows[window_key] = SlidingWindowRateLimiter(
                    window_size=user_config.window_size,
                    max_requests=user_config.requests_per_minute
                )
            
            window_allowed = self.sliding_windows[window_key].is_allowed(identifier)
            
            # Umumiy natija
            allowed = token_allowed and window_allowed
            
            metrics = {
                "allowed": 1 if allowed else 0,
                "remaining": self._get_remaining_requests(identifier, endpoint),
                "reset_time": int(time.time() + user_config.window_size)
            }
            
            return allowed, metrics
    
    def _get_remaining_requests(self, identifier: str, endpoint: str) -> int:
        """Qolgan so'rovlar sonini hisoblash"""
        config = self.endpoint_configs.get(endpoint, EndpointConfig(endpoint, self.global_config))
        user_config = self.user_limits.get(identifier, config.config)
        
        bucket_key = f"token:{identifier}:{endpoint}"
        if bucket_key in self.token_buckets:
            tokens = self.token_buckets[bucket_key].get_tokens()
            return min(tokens, user_config.requests_per_minute)
        
        return user_config.requests_per_minute
    
    def get_metrics(self, identifier: str = None) -> Dict[str, Any]:
        """Metriklarni olish"""
        with self.lock:
            metrics = {
                "total_buckets": len(self.token_buckets),
                "total_windows": len(self.sliding_windows),
                "total_users": len(self.user_limits),
                "total_endpoints": len(self.endpoint_configs)
            }
            
            if identifier:
                # Specific user metrics
                user_metrics = {}
                for bucket_key, bucket in self.token_buckets.items():
                    if identifier in bucket_key:
                        user_metrics[bucket_key] = {
                            "tokens": bucket.get_tokens(),
                            "capacity": bucket.capacity
                        }
                metrics["user_metrics"] = user_metrics
            
            return metrics
    
    def cleanup_expired(self):
        """Muddat tugagan ma'lumotlarni tozalash"""
        with self.lock:
            current_time = time.time()
            
            # Eski token bucketlarni tozalash
            expired_buckets = []
            for key, bucket in self.token_buckets.items():
                if bucket.last_refill < current_time - 3600:  # 1 soat
                    expired_buckets.append(key)
            
            for key in expired_buckets:
                del self.token_buckets[key]
            
            logger.info(f"Tozalangan expired buckets: {len(expired_buckets)}")
    
    async def async_check_rate_limit(self, identifier: str, endpoint: str = "default") -> Tuple[bool, Dict[str, int]]:
        """Asinxron rate limit tekshirish"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.check_rate_limit, identifier, endpoint)
    
    def export_config(self) -> Dict[str, Any]:
        """Konfiguratsiyani eksport qilish"""
        with self.lock:
            return {
                "endpoints": {
                    endpoint: {
                        "config": {
                            "requests_per_minute": config.config.requests_per_minute,
                            "requests_per_hour": config.config.requests_per_hour,
                            "requests_per_day": config.config.requests_per_day,
                            "burst_limit": config.config.burst_limit,
                            "window_size": config.config.window_size
                        },
                        "priority": config.priority,
                        "exempt_users": config.exempt_users
                    }
                    for endpoint, config in self.endpoint_configs.items()
                },
                "users": {
                    user_id: {
                        "requests_per_minute": config.requests_per_minute,
                        "requests_per_hour": config.requests_per_hour,
                        "requests_per_day": config.requests_per_day,
                        "burst_limit": config.burst_limit
                    }
                    for user_id, config in self.user_limits.items()
                }
            }


class BurstHandler:
    """Burst so'rovlarni qayta ishlash"""
    
    def __init__(self, max_burst_duration: int = 10):
        self.max_burst_duration = max_burst_duration
        self.burst_windows: Dict[str, Tuple[float, int]] = {}  # (start_time, request_count)
        self.lock = Lock()
    
    def handle_burst(self, identifier: str) -> Tuple[bool, Dict[str, int]]:
        """Burst qayta ishlash"""
        with self.lock:
            now = time.time()
            
            if identifier in self.burst_windows:
                start_time, request_count = self.burst_windows[identifier]
                
                # Vaqt oynasini tekshirish
                if now - start_time <= self.max_burst_duration:
                    request_count += 1
                    self.burst_windows[identifier] = (start_time, request_count)
                    
                    # Burst limit tekshirish
                    burst_limit = self.max_burst_duration * 10  # Har soniyada 10 ta so'rov
                    if request_count > burst_limit:
                        return False, {
                            "status": "burst_exceeded",
                            "requests": request_count,
                            "limit": burst_limit,
                            "reset_time": int(start_time + self.max_burst_duration)
                        }
                    
                    return True, {
                        "status": "burst_allowed",
                        "requests": request_count,
                        "remaining": burst_limit - request_count
                    }
                else:
                    # Yangi burst oynasi
                    self.burst_windows[identifier] = (now, 1)
                    return True, {
                        "status": "new_burst",
                        "requests": 1,
                        "remaining": self.max_burst_duration * 10 - 1
                    }
            else:
                # Yangi burst oynasi
                self.burst_windows[identifier] = (now, 1)
                return True, {
                    "status": "burst_started", 
                    "requests": 1,
                    "remaining": self.max_burst_duration * 10 - 1
                }