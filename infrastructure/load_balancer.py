"""
Orion Starline Load Balancer
============================

Bu fayl yukni taqsimlash, CDN integration va 
traffic management uchun load balancer tizimini o'z ichiga oladi.
"""

import asyncio
import hashlib
import json
import logging
import random
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import aiohttp
import statistics
from contextlib import asynccontextmanager


class LoadBalancingStrategy(Enum):
    """Load balancing strategiyalari"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    RESOURCE_BASED = "resource_based"
    ADAPTIVE = "adaptive"


class HealthCheckStatus(Enum):
    """Health check holatlari"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    WARNING = "warning"
    UNKNOWN = "unknown"


@dataclass
class Server:
    """Server konfiguratsiyasi"""
    id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    response_time: float = 0.0
    last_health_check: Optional[datetime] = None
    status: HealthCheckStatus = HealthCheckStatus.UNKNOWN
    error_count: int = 0
    success_count: int = 0
    last_used: Optional[datetime] = None
    geographic_region: str = "us-east"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0


@dataclass
class LoadBalancerConfig:
    """Load balancer konfiguratsiyasi"""
    name: str
    strategy: LoadBalancingStrategy
    health_check_interval: int = 30
    health_check_timeout: int = 5
    health_check_path: str = "/health"
    max_retries: int = 3
    retry_delay: float = 0.1
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    response_time_threshold: float = 5.0
    enable_circuit_breaker: bool = True
    enable_cdn: bool = True
    cdn_cache_ttl: int = 300


@dataclass
class Request:
    """HTTP so'rov"""
    id: str
    client_ip: str
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[bytes]
    start_time: datetime
    timeout: float = 30.0
    priority: int = 1


@dataclass
class Response:
    """HTTP javob"""
    status_code: int
    headers: Dict[str, str]
    body: Optional[bytes]
    server_id: str
    response_time: float
    cached: bool = False


class HealthChecker:
    """Server health checker"""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def check_server_health(self, server: Server) -> HealthCheckStatus:
        """Server health ni tekshirish"""
        try:
            url = f"http://{server.host}:{server.port}{self.config.health_check_path}"
            
            timeout = aiohttp.ClientTimeout(total=self.config.health_check_timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = time.time()
                async with session.get(url) as response:
                    response_time = time.time() - start_time
                    
                    server.response_time = response_time
                    server.last_health_check = datetime.now()
                    
                    if response.status == 200:
                        server.status = HealthCheckStatus.HEALTHY
                        server.success_count += 1
                        return HealthCheckStatus.HEALTHY
                    else:
                        server.status = HealthCheckStatus.UNHEALTHY
                        server.error_count += 1
                        return HealthCheckStatus.UNHEALTHY
                        
        except asyncio.TimeoutError:
            server.status = HealthCheckStatus.UNHEALTHY
            server.error_count += 1
            self.logger.warning(f"Health check timeout for {server.id}")
            return HealthCheckStatus.UNHEALTHY
            
        except Exception as e:
            server.status = HealthCheckStatus.UNHEALTHY
            server.error_count += 1
            self.logger.error(f"Health check error for {server.id}: {e}")
            return HealthCheckStatus.UNHEALTHY
    
    async def check_servers_health(self, servers: List[Server]) -> Dict[str, HealthCheckStatus]:
        """Barcha serverlarni tekshirish"""
        tasks = [self.check_server_health(server) for server in servers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        status_map = {}
        for server, result in zip(servers, results):
            if isinstance(result, Exception):
                status_map[server.id] = HealthCheckStatus.UNHEALTHY
                self.logger.error(f"Health check failed for {server.id}: {result}")
            else:
                status_map[server.id] = result
        
        return status_map


class CircuitBreaker:
    """Circuit breaker - server muammolarini oldini olish"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_counts: Dict[str, int] = {}
        self.last_failure_time: Dict[str, datetime] = {}
        self.state: Dict[str, str] = {}  # closed, open, half-open
        self.logger = logging.getLogger(__name__)
    
    def is_circuit_open(self, server_id: str) -> bool:
        """Circuit ochiqmi tekshirish"""
        state = self.state.get(server_id, "closed")
        
        if state == "open":
            last_failure = self.last_failure_time.get(server_id)
            if last_failure and (datetime.now() - last_failure).total_seconds() > self.timeout:
                # Half-open state ga o'tish
                self.state[server_id] = "half-open"
                return False
            return True
        
        return False
    
    def record_success(self, server_id: str):
        """Muvaffaqiyatli so'rovni qayd qilish"""
        self.failure_counts[server_id] = 0
        self.state[server_id] = "closed"
    
    def record_failure(self, server_id: str):
        """Muvaffaqiyatsiz so'rovni qayd qilish"""
        self.failure_counts[server_id] = self.failure_counts.get(server_id, 0) + 1
        self.last_failure_time[server_id] = datetime.now()
        
        if self.failure_counts[server_id] >= self.failure_threshold:
            self.state[server_id] = "open"
            self.logger.warning(f"Circuit breaker opened for {server_id}")


class CDNManager:
    """CDN Manager - Content Delivery Network"""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.cdn_providers = {
            "cloudflare": self._cloudflare_integration,
            "aws_cloudfront": self._aws_cloudfront_integration,
            "azure_cdn": self._azure_cdn_integration
        }
        self.cache_rules = {}
        self.logger = logging.getLogger(__name__)
    
    async def _cloudflare_integration(self, request: Request) -> Dict[str, Any]:
        """Cloudflare CDN integration"""
        return {
            "provider": "cloudflare",
            "cache_key": f"cf:{hashlib.md5(f'{request.path}:{request.headers.get('User-Agent', '')}'.encode()).hexdigest()}",
            "cache_ttl": self.config.cdn_cache_ttl,
            "purge_url": f"https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache"
        }
    
    async def _aws_cloudfront_integration(self, request: Request) -> Dict[str, Any]:
        """AWS CloudFront integration"""
        return {
            "provider": "cloudfront",
            "distribution_id": "DISTRIBUTION_ID",
            "cache_key": f"cf:{hashlib.md5(request.path.encode()).hexdigest()[:16]}",
            "cache_ttl": self.config.cdn_cache_ttl
        }
    
    async def _azure_cdn_integration(self, request: Request) -> Dict[str, Any]:
        """Azure CDN integration"""
        return {
            "provider": "azure_cdn",
            "endpoint": "ENDPOINT_NAME.azureedge.net",
            "cache_key": f"azure:{hashlib.md5(request.path.encode()).hexdigest()[:16]}",
            "cache_ttl": self.config.cdn_cache_ttl
        }
    
    async def get_cache_info(self, request: Request, provider: str = "cloudflare") -> Dict[str, Any]:
        """CDN cache ma'lumotlarini olish"""
        if not self.config.enable_cdn:
            return {"cached": False}
        
        integration_func = self.cdn_providers.get(provider)
        if integration_func:
            return await integration_func(request)
        
        return {"cached": False}
    
    async def should_cache_request(self, request: Request) -> bool:
        """So'rov cache qilinishi kerakligini aniqlash"""
        # Cache qilinmaydigan so'rovlar
        no_cache_paths = ["/api/auth", "/api/login", "/api/trade"]
        no_cache_methods = ["POST", "PUT", "DELETE"]
        
        if request.method in no_cache_methods:
            return False
        
        if any(request.path.startswith(path) for path in no_cache_paths):
            return False
        
        return True


class LoadBalancer:
    """Asosiy Load Balancer"""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.servers: Dict[str, Server] = {}
        self.health_checker = HealthChecker(config)
        self.circuit_breaker = CircuitBreaker(
            config.circuit_breaker_threshold,
            config.circuit_breaker_timeout
        )
        self.cdn_manager = CDNManager(config)
        self.current_round_robin_index = 0
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "requests_per_second": 0.0
        }
        self.logger = logging.getLogger(__name__)
    
    def add_server(self, server: Server):
        """Server qo'shish"""
        self.servers[server.id] = server
        self.logger.info(f"Server added: {server.id} ({server.host}:{server.port})")
    
    def remove_server(self, server_id: str):
        """Server o'chirish"""
        if server_id in self.servers:
            del self.servers[server_id]
            self.logger.info(f"Server removed: {server_id}")
    
    def get_available_servers(self) -> List[Server]:
        """Mavjud serverlarni olish"""
        available_servers = []
        
        for server in self.servers.values():
            if (server.status == HealthCheckStatus.HEALTHY and
                not self.circuit_breaker.is_circuit_open(server.id) and
                server.current_connections < server.max_connections):
                available_servers.append(server)
        
        return available_servers
    
    async def select_server(self, request: Request) -> Optional[Server]:
        """So'rov uchun server tanlash"""
        available_servers = self.get_available_servers()
        
        if not available_servers:
            self.logger.error("No available servers")
            return None
        
        if self.config.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return await self._round_robin_selection(available_servers)
        elif self.config.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return await self._least_connections_selection(available_servers)
        elif self.config.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return await self._weighted_round_robin_selection(available_servers)
        elif self.config.strategy == LoadBalancingStrategy.IP_HASH:
            return await self._ip_hash_selection(available_servers, request.client_ip)
        elif self.config.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return await self._least_response_time_selection(available_servers)
        elif self.config.strategy == LoadBalancingStrategy.RESOURCE_BASED:
            return await self._resource_based_selection(available_servers)
        elif self.config.strategy == LoadBalancingStrategy.ADAPTIVE:
            return await self._adaptive_selection(available_servers)
        else:
            return available_servers[0]
    
    async def _round_robin_selection(self, servers: List[Server]) -> Server:
        """Round Robin tanlash"""
        server = servers[self.current_round_robin_index % len(servers)]
        self.current_round_robin_index += 1
        return server
    
    async def _least_connections_selection(self, servers: List[Server]) -> Server:
        """Eng kam ulanishlarga ega server tanlash"""
        return min(servers, key=lambda s: s.current_connections)
    
    async def _weighted_round_robin_selection(self, servers: List[Server]) -> Server:
        """Weighted Round Robin tanlash"""
        # Og'irliklar bo'yicha tanlash
        total_weight = sum(server.weight for server in servers)
        if total_weight == 0:
            return random.choice(servers)
        
        target = random.randint(1, total_weight)
        current_weight = 0
        
        for server in servers:
            current_weight += server.weight
            if current_weight >= target:
                return server
        
        return servers[-1]
    
    async def _ip_hash_selection(self, servers: List[Server], client_ip: str) -> Server:
        """IP hash bo'yicha tanlash"""
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        server_index = hash_value % len(servers)
        return servers[server_index]
    
    async def _least_response_time_selection(self, servers: List[Server]) -> Server:
        """Eng tez javob beruvchi server tanlash"""
        return min(servers, key=lambda s: s.response_time)
    
    async def _resource_based_selection(self, servers: List[Server]) -> Server:
        """Resurs usage bo'yicha tanlash"""
        def score_server(server):
            cpu_score = server.cpu_usage / 100.0
            memory_score = server.memory_usage / 100.0
            connection_score = server.current_connections / server.max_connections
            return (cpu_score + memory_score + connection_score) / 3
        
        return min(servers, key=score_server)
    
    async def _adaptive_selection(self, servers: List[Server]) -> Server:
        """Adaptive tanlash - real-time performance bo'yicha"""
        if not servers:
            return None
        
        # Performance scoring
        scores = []
        for server in servers:
            # Response time score (lower is better)
            response_score = 1 / (1 + server.response_time)
            
            # Connection score (fewer connections is better)
            connection_score = 1 - (server.current_connections / server.max_connections)
            
            # Health score
            health_score = 1.0 if server.status == HealthCheckStatus.HEALTHY else 0.1
            
            # Success rate score
            total_requests = server.success_count + server.error_count
            success_score = server.success_count / total_requests if total_requests > 0 else 0.5
            
            # Combined score
            total_score = (response_score * 0.3 + 
                          connection_score * 0.2 + 
                          health_score * 0.3 + 
                          success_score * 0.2)
            
            scores.append((server, total_score))
        
        # Eng yuqori ballga ega serverni tanlash
        best_server = max(scores, key=lambda x: x[1])[0]
        return best_server
    
    async def forward_request(self, request: Request) -> Response:
        """So'rovni server ga yo'naltirish"""
        self.stats["total_requests"] += 1
        
        # Server tanlash
        server = await self.select_server(request)
        if not server:
            return Response(
                status_code=503,
                headers={},
                body=b"Service Unavailable",
                server_id="none",
                response_time=0.0,
                cached=False
            )
        
        # CDN cache tekshirish
        cached_response = None
        if await self.cdn_manager.should_cache_request(request):
            # CDN cache dan tekshirish (bu yerda implementation kerak)
            pass
        
        # So'rovni server ga yuborish
        try:
            server.current_connections += 1
            server.last_used = datetime.now()
            
            async with aiohttp.ClientSession() as session:
                url = f"http://{server.host}:{server.port}{request.path}"
                
                start_time = time.time()
                async with session.request(
                    request.method,
                    url,
                    headers=request.headers,
                    data=request.body,
                    timeout=aiohttp.ClientTimeout(total=request.timeout)
                ) as resp:
                    response_time = time.time() - start_time
                    
                    # Response ma'lumotlarini olish
                    response_body = await resp.read()
                    response_headers = dict(resp.headers)
                    
                    # Server statistikasini yangilash
                    server.response_time = response_time
                    server.success_count += 1
                    
                    # Circuit breaker ni muvaffaqiyatli qilish
                    if self.config.enable_circuit_breaker:
                        self.circuit_breaker.record_success(server.id)
                    
                    self.stats["successful_requests"] += 1
                    self.stats["average_response_time"] = (
                        (self.stats["average_response_time"] * 0.9) + (response_time * 0.1)
                    )
                    
                    return Response(
                        status_code=resp.status,
                        headers=response_headers,
                        body=response_body,
                        server_id=server.id,
                        response_time=response_time,
                        cached=cached_response is not None
                    )
        
        except asyncio.TimeoutError:
            if self.config.enable_circuit_breaker:
                self.circuit_breaker.record_failure(server.id)
            
            server.error_count += 1
            self.stats["failed_requests"] += 1
            
            return Response(
                status_code=504,
                headers={},
                body=b"Gateway Timeout",
                server_id=server.id,
                response_time=request.timeout,
                cached=False
            )
        
        except Exception as e:
            if self.config.enable_circuit_breaker:
                self.circuit_breaker.record_failure(server.id)
            
            server.error_count += 1
            self.stats["failed_requests"] += 1
            self.logger.error(f"Request forwarding error: {e}")
            
            return Response(
                status_code=500,
                headers={},
                body=b"Internal Server Error",
                server_id=server.id,
                response_time=0.0,
                cached=False
            )
        
        finally:
            server.current_connections = max(0, server.current_connections - 1)
    
    async def health_check_loop(self):
        """Doimiy health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                servers = list(self.servers.values())
                if servers:
                    health_statuses = await self.health_checker.check_servers_health(servers)
                    
                    # Server status larni yangilash
                    for server_id, status in health_statuses.items():
                        if server_id in self.servers:
                            self.servers[server_id].status = status
                
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
    
    async def start_monitoring(self):
        """Monitoring ni boshlash"""
        asyncio.create_task(self.health_check_loop())
        self.logger.info("Load balancer monitoring started")
    
    def get_stats(self) -> Dict[str, Any]:
        """Load balancer statistikasini olish"""
        server_stats = {}
        for server_id, server in self.servers.items():
            total_requests = server.success_count + server.error_count
            success_rate = server.success_count / total_requests if total_requests > 0 else 0
            
            server_stats[server_id] = {
                "status": server.status.value,
                "current_connections": server.current_connections,
                "max_connections": server.max_connections,
                "response_time": server.response_time,
                "success_rate": success_rate,
                "total_requests": total_requests,
                "cpu_usage": server.cpu_usage,
                "memory_usage": server.memory_usage,
                "last_health_check": server.last_health_check.isoformat() if server.last_health_check else None
            }
        
        return {
            "global_stats": self.stats,
            "server_stats": server_stats,
            "available_servers": len(self.get_available_servers()),
            "total_servers": len(self.servers),
            "strategy": self.config.strategy.value
        }


class TrafficManager:
    """Traffic Management - Rate limiting, DDoS protection"""
    
    def __init__(self):
        self.request_counts = {}
        self.blocked_ips = {}
        self.logger = logging.getLogger(__name__)
    
    async def check_rate_limit(self, client_ip: str, limit: int = 100, window: int = 60) -> bool:
        """Rate limit tekshirish"""
        current_time = time.time()
        window_start = current_time - window
        
        # IP uchun request history ni tozalash
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # Eski requestlarni olib tashlash
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip] 
            if req_time > window_start
        ]
        
        # Yangi request qo'shish
        self.request_counts[client_ip].append(current_time)
        
        # Limit ni tekshirish
        if len(self.request_counts[client_ip]) > limit:
            self.blocked_ips[client_ip] = current_time + (window * 2)  # 2x window uchun block
            self.logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        return True
    
    def is_blocked(self, client_ip: str) -> bool:
        """IP block qilinganmi tekshirish"""
        if client_ip in self.blocked_ips:
            if time.time() < self.blocked_ips[client_ip]:
                return True
            else:
                # Block vaqti tugagan, o'chirish
                del self.blocked_ips[client_ip]
        return False
    
    async def cleanup_blocked_ips(self):
        """Block qilingan IP larni tozalash"""
        current_time = time.time()
        expired_ips = [
            ip for ip, block_until in self.blocked_ips.items()
            if current_time >= block_until
        ]
        
        for ip in expired_ips:
            del self.blocked_ips[ip]
        
        # Request counts ni ham tozalash
        expired_request_counts = [
            ip for ip, requests in self.request_counts.items()
            if not requests or max(requests) < current_time - 3600  # 1 soat
        ]
        
        for ip in expired_request_counts:
            del self.request_counts[ip]


class OrionStarlineLoadBalancer:
    """Orion Starline uchun Load Balancer"""
    
    def __init__(self):
        self.config = LoadBalancerConfig(
            name="orion-starline-lb",
            strategy=LoadBalancingStrategy.ADAPTIVE,
            health_check_interval=30,
            max_retries=3,
            enable_circuit_breaker=True,
            enable_cdn=True,
            cdn_cache_ttl=300
        )
        
        self.load_balancer = LoadBalancer(self.config)
        self.traffic_manager = TrafficManager()
        self.logger = logging.getLogger(__name__)
        
        self._setup_servers()
    
    def _setup_servers(self):
        """Serverlarni sozlash"""
        # Auth Service servers
        auth_servers = [
            Server("auth-1", "auth-service-1", 8001, weight=2, max_connections=500),
            Server("auth-2", "auth-service-2", 8001, weight=2, max_connections=500),
            Server("auth-3", "auth-service-3", 8001, weight=1, max_connections=500),
        ]
        
        # Trading Service servers
        trading_servers = [
            Server("trading-1", "trading-service-1", 8002, weight=3, max_connections=1000),
            Server("trading-2", "trading-service-2", 8002, weight=3, max_connections=1000),
            Server("trading-3", "trading-service-3", 8002, weight=2, max_connections=1000),
            Server("trading-4", "trading-service-4", 8002, weight=2, max_connections=1000),
            Server("trading-5", "trading-service-5", 8002, weight=1, max_connections=1000),
        ]
        
        # Market Data Service servers
        market_data_servers = [
            Server("md-1", "market-data-service-1", 8003, weight=2, max_connections=800),
            Server("md-2", "market-data-service-2", 8003, weight=2, max_connections=800),
        ]
        
        # Serverlarni load balancer ga qo'shish
        for server in auth_servers + trading_servers + market_data_servers:
            self.load_balancer.add_server(server)
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Request ni qayta ishlash"""
        # Rate limiting tekshirish
        client_ip = request_data.get("client_ip", "unknown")
        
        if self.traffic_manager.is_blocked(client_ip):
            return {
                "status": 429,
                "response": {"error": "Too Many Requests"},
                "server_id": "blocked",
                "cached": False
            }
        
        if not await self.traffic_manager.check_rate_limit(client_ip):
            return {
                "status": 429,
                "response": {"error": "Rate limit exceeded"},
                "server_id": "rate_limited",
                "cached": False
            }
        
        # Request obyektini yaratish
        request = Request(
            id=request_data.get("request_id", f"req_{time.time()}"),
            client_ip=client_ip,
            method=request_data.get("method", "GET"),
            path=request_data.get("path", "/"),
            headers=request_data.get("headers", {}),
            body=request_data.get("body"),
            start_time=datetime.now()
        )
        
        # Load balancer orqali so'rovni yuborish
        response = await self.load_balancer.forward_request(request)
        
        return {
            "status": response.status_code,
            "response": response.body.decode() if response.body else "",
            "headers": response.headers,
            "server_id": response.server_id,
            "response_time": response.response_time,
            "cached": response.cached
        }
    
    async def start(self):
        """Load balancer ni boshlash"""
        await self.load_balancer.start_monitoring()
        
        # Cleanup task
        asyncio.create_task(self._periodic_cleanup())
        
        self.logger.info("Orion Starline Load Balancer started")
    
    async def _periodic_cleanup(self):
        """Davriy tozalash"""
        while True:
            await asyncio.sleep(300)  # 5 daqiqa
            await self.traffic_manager.cleanup_blocked_ips()


# Global load balancer instance
_global_load_balancer: Optional[OrionStarlineLoadBalancer] = None

def get_global_load_balancer() -> OrionStarlineLoadBalancer:
    """Global load balancer olish"""
    global _global_load_balancer
    if _global_load_balancer is None:
        _global_load_balancer = OrionStarlineLoadBalancer()
    return _global_load_balancer


if __name__ == "__main__":
    async def demo():
        """Demo - Load Balancer ishlatish"""
        print("🚀 Orion Starline Load Balancer")
        print("=" * 50)
        
        # Load balancer yaratish
        lb = get_global_load_balancer()
        await lb.start()
        
        # Test requests
        print("⚡ Test Requestlari:")
        
        test_requests = [
            {
                "request_id": "req_1",
                "client_ip": "192.168.1.100",
                "method": "GET",
                "path": "/api/auth/health",
                "headers": {"User-Agent": "TestClient/1.0"}
            },
            {
                "request_id": "req_2",
                "client_ip": "192.168.1.101",
                "method": "GET",
                "path": "/api/trading/positions",
                "headers": {"User-Agent": "TestClient/1.0"}
            },
            {
                "request_id": "req_3",
                "client_ip": "192.168.1.102",
                "method": "GET",
                "path": "/api/market-data/EURUSD",
                "headers": {"User-Agent": "TestClient/1.0"}
            }
        ]
        
        # Requestlarni yuborish
        for i, request_data in enumerate(test_requests, 1):
            start_time = time.time()
            result = await lb.handle_request(request_data)
            end_time = time.time()
            
            print(f"Request {i}:")
            print(f"  Status: {result['status']}")
            print(f"  Server: {result['server_id']}")
            print(f"  Response time: {result['response_time']:.3f}s")
            print(f"  Cached: {result['cached']}")
            print()
        
        # Load balancing strategiyalarini test qilish
        print("🔄 Load Balancing Strategy Test:")
        for strategy in LoadBalancingStrategy:
            lb.config.strategy = strategy
            print(f"Strategy: {strategy.value}")
            
            # 10 ta request yuborish
            servers_used = {}
            for i in range(10):
                request_data = {
                    "request_id": f"test_{i}",
                    "client_ip": f"192.168.1.{i % 255}",
                    "method": "GET",
                    "path": "/api/test",
                    "headers": {}
                }
                
                result = await lb.handle_request(request_data)
                server_id = result['server_id']
                servers_used[server_id] = servers_used.get(server_id, 0) + 1
            
            print(f"  Servers used: {servers_used}")
            print()
        
        # Load Balancer Statistics
        print("📊 Load Balancer Statistics:")
        stats = lb.load_balancer.get_stats()
        print(f"Total requests: {stats['global_stats']['total_requests']}")
        print(f"Successful requests: {stats['global_stats']['successful_requests']}")
        print(f"Failed requests: {stats['global_stats']['failed_requests']}")
        print(f"Average response time: {stats['global_stats']['average_response_time']:.3f}s")
        print(f"Available servers: {stats['available_servers']}/{stats['total_servers']}")
        print(f"Current strategy: {stats['strategy']}")
        
        print("\n🎉 Demo tugallandi!")
    
    asyncio.run(demo())