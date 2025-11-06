"""
Orion Starline Microservices Architecture
==========================================

Bu fayl mikroservislar arxitekturasini boshqarish uchun zarur
komponentlarni va xizmatlarni o'z ichiga oladi.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from datetime import datetime, timedelta
import aiohttp
import redis.asyncio as redis
from contextlib import asynccontextmanager


class ServiceType(Enum):
    """Xizmat turlari"""
    AUTH_SERVICE = "auth-service"
    TRADING_SERVICE = "trading-service"
    MARKET_DATA_SERVICE = "market-data-service"
    PORTFOLIO_SERVICE = "portfolio-service"
    NOTIFICATION_SERVICE = "notification-service"
    ANALYTICS_SERVICE = "analytics-service"
    USER_SERVICE = "user-service"
    RISK_SERVICE = "risk-service"


@dataclass
class ServiceConfig:
    """Xizmat konfiguratsiyasi"""
    name: str
    service_type: ServiceType
    replicas: int = 3
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    port: int = 8000
    health_check_path: str = "/health"
    dependencies: List[str] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    auto_scale: bool = True
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70


@dataclass
class ServiceInstance:
    """Xizmat instance"""
    id: str
    name: str
    service_type: ServiceType
    host: str
    port: int
    status: str = "running"
    last_health_check: Optional[datetime] = None
    load: float = 0.0
    dependencies: List[str] = field(default_factory=list)


class ServiceDiscovery:
    """Xizmat kashfiyoti va ro'yxatga olish sistemi"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.services: Dict[str, ServiceInstance] = {}
        self.logger = logging.getLogger(__name__)
        
    async def register_service(self, service: ServiceInstance) -> bool:
        """Xizmatni ro'yxatga olish"""
        try:
            key = f"service:{service.name}:{service.id}"
            service_data = {
                "id": service.id,
                "name": service.name,
                "service_type": service.service_type.value,
                "host": service.host,
                "port": service.port,
                "status": service.status,
                "load": service.load,
                "dependencies": service.dependencies,
                "last_health_check": datetime.now().isoformat()
            }
            
            await self.redis_client.hset(key, mapping=service_data)
            await self.redis_client.expire(key, 300)  # 5 daqiqa TTL
            self.services[f"{service.name}:{service.id}"] = service
            
            self.logger.info(f"Xizmat ro'yxatga olindi: {service.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Xizmat ro'yxatga olishda xatolik: {e}")
            return False
    
    async def discover_services(self, service_type: ServiceType) -> List[ServiceInstance]:
        """Xizmatlarni qidirish"""
        try:
            pattern = f"service:*:{service_type.value}"
            keys = await self.redis_client.keys(pattern)
            services = []
            
            for key in keys:
                service_data = await self.redis_client.hgetall(key)
                if service_data:
                    service = ServiceInstance(
                        id=service_data["id"],
                        name=service_data["name"],
                        service_type=service_type,
                        host=service_data["host"],
                        port=int(service_data["port"]),
                        status=service_data["status"],
                        load=float(service_data.get("load", 0.0))
                    )
                    services.append(service)
                    
            return services
        except Exception as e:
            self.logger.error(f"Xizmat qidirishda xatolik: {e}")
            return []
    
    async def health_check(self, service_name: str) -> bool:
        """Xizmat sog'liqni tekshirish"""
        try:
            pattern = f"service:{service_name}:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                service_data = await self.redis_client.hgetall(key)
                service_url = f"http://{service_data['host']}:{service_data['port']}/health"
                
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(service_url, timeout=5) as response:
                            if response.status == 200:
                                await self.redis_client.hset(key, "last_health_check", datetime.now().isoformat())
                                return True
                    except asyncio.TimeoutError:
                        self.logger.warning(f"Health check timeout: {service_url}")
                        
            return False
        except Exception as e:
            self.logger.error(f"Health check xatolik: {e}")
            return False


class LoadBalancer:
    """Load balancer - xizmatlar o'rtasida yukni taqsimlash"""
    
    def __init__(self, service_discovery: ServiceDiscovery):
        self.service_discovery = service_discovery
        self.logger = logging.getLogger(__name__)
    
    async def route_request(self, service_type: ServiceType, request_data: Dict[str, Any]) -> Optional[str]:
        """So'rovni xizmatga yo'naltirish"""
        try:
            services = await self.service_discovery.discover_services(service_type)
            if not services:
                return None
            
            # Eng kam yuklangan xizmatni tanlash (Round Robin)
            healthy_services = [s for s in services if s.status == "running"]
            if not healthy_services:
                return None
            
            # Load bo'yicha eng yaxshi xizmatni tanlash
            best_service = min(healthy_services, key=lambda s: s.load)
            
            service_url = f"http://{best_service.host}:{best_service.port}"
            return service_url
            
        except Exception as e:
            self.logger.error(f"Load balancing xatolik: {e}")
            return None


class CircuitBreaker:
    """Circuit Breaker - xizmat muammolarini oldini olish"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_counts: Dict[str, int] = {}
        self.last_failure_time: Dict[str, datetime] = {}
        self.state: Dict[str, str] = {}  # closed, open, half-open
        self.logger = logging.getLogger(__name__)
    
    async def call(self, service_name: str, func, *args, **kwargs):
        """Funksiyani Circuit Breaker bilan chaqirish"""
        if self.state.get(service_name) == "open":
            if self._should_attempt_reset(service_name):
                self.state[service_name] = "half-open"
            else:
                raise Exception(f"Service {service_name} is currently unavailable (circuit open)")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success(service_name)
            return result
        except Exception as e:
            self._on_failure(service_name)
            raise e
    
    def _should_attempt_reset(self, service_name: str) -> bool:
        """Resetga urinish kerakligini tekshirish"""
        last_failure = self.last_failure_time.get(service_name)
        if last_failure and (datetime.now() - last_failure).total_seconds() > self.timeout:
            return True
        return False
    
    def _on_success(self, service_name: str):
        """Muvaffaqiyatli chaqirish"""
        self.failure_counts[service_name] = 0
        self.state[service_name] = "closed"
    
    def _on_failure(self, service_name: str):
        """Muvaffaqiyatsiz chaqirish"""
        self.failure_counts[service_name] = self.failure_counts.get(service_name, 0) + 1
        self.last_failure_time[service_name] = datetime.now()
        
        if self.failure_counts[service_name] >= self.failure_threshold:
            self.state[service_name] = "open"
            self.logger.warning(f"Circuit breaker opened for {service_name}")


class MicroservicesOrchestrator:
    """Mikroservislar orkestrator"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.service_discovery = ServiceDiscovery(redis_url)
        self.load_balancer = LoadBalancer(self.service_discovery)
        self.circuit_breaker = CircuitBreaker()
        self.service_configs: Dict[str, ServiceConfig] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_service_config(self, config: ServiceConfig):
        """Xizmat konfiguratsiyasini ro'yxatga olish"""
        self.service_configs[config.name] = config
        self.logger.info(f"Xizmat konfiguratsiyasi ro'yxatga olindi: {config.name}")
    
    async def deploy_service(self, config: ServiceConfig, instances: List[str]) -> bool:
        """Xizmatni joylashtirish"""
        try:
            deployed_instances = []
            
            for i, instance_id in enumerate(instances):
                instance = ServiceInstance(
                    id=instance_id,
                    name=config.name,
                    service_type=config.service_type,
                    host=f"{config.name}-service-{i}",
                    port=config.port,
                    dependencies=config.dependencies
                )
                
                success = await self.service_discovery.register_service(instance)
                if success:
                    deployed_instances.append(instance_id)
                else:
                    self.logger.error(f"Instance {instance_id} joylashtirishda xatolik")
            
            self.logger.info(f"Xizmat {config.name} {len(deployed_instances)} instance bilan joylashtirildi")
            return len(deployed_instances) == len(instances)
            
        except Exception as e:
            self.logger.error(f"Xizmat joylashtirishda xatolik: {e}")
            return False
    
    async def scale_service(self, service_name: str, target_replicas: int) -> bool:
        """Xizmasshtabini o'zgartirish"""
        try:
            config = self.service_configs.get(service_name)
            if not config:
                raise ValueError(f"Service config topilmadi: {service_name}")
            
            current_instances = await self.service_discovery.discover_services(config.service_type)
            current_replicas = len(current_instances)
            
            if target_replicas > current_replicas:
                # Yangi instance yaratish
                new_instances = [f"{service_name}-replica-{i}" for i in range(current_replicas, target_replicas)]
                await self.deploy_service(config, new_instances)
            elif target_replicas < current_replicas:
                # Instance o'chirish
                instances_to_remove = current_instances[target_replicas:]
                for instance in instances_to_remove:
                    key = f"service:{instance.name}:{instance.id}"
                    await self.service_discovery.redis_client.delete(key)
            
            self.logger.info(f"Xizmat {service_name} {target_replicas} replikaga o'zgartirildi")
            return True
            
        except Exception as e:
            self.logger.error(f"Scale qilishda xatolik: {e}")
            return False
    
    async def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Xizmat holatini olish"""
        try:
            config = self.service_configs.get(service_name)
            if not config:
                return {"error": "Service config topilmadi"}
            
            instances = await self.service_discovery.discover_services(config.service_type)
            
            status = {
                "service_name": service_name,
                "target_replicas": config.replicas,
                "current_replicas": len(instances),
                "instances": [],
                "overall_health": "healthy"
            }
            
            for instance in instances:
                instance_status = {
                    "id": instance.id,
                    "host": instance.host,
                    "port": instance.port,
                    "status": instance.status,
                    "load": instance.load,
                    "health": "unknown"
                }
                
                if await self.service_discovery.health_check(instance.name):
                    instance_status["health"] = "healthy"
                else:
                    instance_status["health"] = "unhealthy"
                    status["overall_health"] = "unhealthy"
                
                status["instances"].append(instance_status)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Status olishda xatolik: {e}")
            return {"error": str(e)}


# Service Factory
class ServiceFactory:
    """Xizmat yaratish factory"""
    
    @staticmethod
    def create_auth_service() -> ServiceConfig:
        return ServiceConfig(
            name="auth-service",
            service_type=ServiceType.AUTH_SERVICE,
            replicas=3,
            port=8001,
            dependencies=["user-service"],
            environment_vars={
                "JWT_SECRET": "your-jwt-secret",
                "DATABASE_URL": "postgresql://user:pass@db:5432/auth_db"
            }
        )
    
    @staticmethod
    def create_trading_service() -> ServiceConfig:
        return ServiceConfig(
            name="trading-service",
            service_type=ServiceType.TRADING_SERVICE,
            replicas=5,
            port=8002,
            dependencies=["market-data-service", "risk-service"],
            environment_vars={
                "MARKET_DATA_API": "http://market-data-service:8003",
                "REDIS_URL": "redis://redis:6379"
            }
        )
    
    @staticmethod
    def create_market_data_service() -> ServiceConfig:
        return ServiceConfig(
            name="market-data-service",
            service_type=ServiceType.MARKET_DATA_SERVICE,
            replicas=2,
            port=8003,
            environment_vars={
                "MARKET_DATA_PROVIDER": "external-api",
                "CACHE_TTL": "300"
            }
        )


# Global orchestrator instance
orchestrator = MicroservicesOrchestrator()

# Xizmatlarni ro'yxatga olish
orchestrator.register_service_config(ServiceFactory.create_auth_service())
orchestrator.register_service_config(ServiceFactory.create_trading_service())
orchestrator.register_service_config(ServiceFactory.create_market_data_service())


if __name__ == "__main__":
    async def demo():
        """Demo - mikroservislar arxitekturasini ko'rsatish"""
        print("🚀 Orion Starline Mikroservislar Arxitekturasi")
        print("=" * 50)
        
        # Auth service joylashtirish
        auth_instances = ["auth-1", "auth-2", "auth-3"]
        success = await orchestrator.deploy_service(
            ServiceFactory.create_auth_service(), 
            auth_instances
        )
        print(f"Auth service joylashtirish: {'✅' if success else '❌'}")
        
        # Trading service joylashtirish
        trading_instances = ["trading-1", "trading-2", "trading-3", "trading-4", "trading-5"]
        success = await orchestrator.deploy_service(
            ServiceFactory.create_trading_service(), 
            trading_instances
        )
        print(f"Trading service joylashtirish: {'✅' if success else '❌'}")
        
        # Market data service joylashtirish
        md_instances = ["md-1", "md-2"]
        success = await orchestrator.deploy_service(
            ServiceFactory.create_market_data_service(), 
            md_instances
        )
        print(f"Market Data service joylashtirish: {'✅' if success else '❌'}")
        
        # Servislar holatini ko'rsatish
        print("\n📊 Servislar Holati:")
        for service_name in ["auth-service", "trading-service", "market-data-service"]:
            status = await orchestrator.get_service_status(service_name)
            print(f"\n{service_name}:")
            print(f"  Target replicas: {status['target_replicas']}")
            print(f"  Current replicas: {status['current_replicas']}")
            print(f"  Overall health: {status['overall_health']}")
            
            for instance in status['instances']:
                print(f"    - {instance['id']}: {instance['status']} (load: {instance['load']:.2f})")
        
        # Scale test
        print("\n⚡ Scale Test:")
        success = await orchestrator.scale_service("auth-service", 5)
        print(f"Auth service scale (5 replicas): {'✅' if success else '❌'}")
        
        final_status = await orchestrator.get_service_status("auth-service")
        print(f"Auth service final replicas: {final_status['current_replicas']}")
        
        print("\n🎉 Demo tugallandi!")
    
    asyncio.run(demo())