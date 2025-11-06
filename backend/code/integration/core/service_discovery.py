"""
Service Discovery
================

Service discovery xizmati - modullar o'rtasida xizmatlar topish va ro'yxatga olish.
Dynamic service discovery, health checking va load balancing ta'minlaydi.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from concurrent.futures import ThreadPoolExecutor
import hashlib

class ServiceStatus(Enum):
    """Xizmat holati"""
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"

@dataclass
class ServiceInfo:
    """Xizmat haqida ma'lumot"""
    name: str
    version: str
    host: str
    port: int
    protocol: str
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    health_check_url: Optional[str] = None
    load_balanced: bool = False
    instances: List[str] = field(default_factory=list)
    last_health_check: float = field(default_factory=time.time)
    response_time: float = 0.0
    error_count: int = 0

class ServiceDiscovery:
    """
    Service Discovery xizmati
    
    Modullar o'rtasida service discovery, health checking 
    va load balancing ta'minlaydi.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.services: Dict[str, ServiceInfo] = {}
        self.service_tags: Dict[str, List[str]] = {}  # tag -> service names
        self.service_providers: Dict[str, str] = {}  # service -> provider module
        
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Health check configuration
        self.health_check_interval = self.config.get('health_check_interval', 30)
        self.health_check_timeout = self.config.get('health_check_timeout', 5)
        self.max_failures = self.config.get('max_failures', 3)
        
        self.running = False
    
    async def initialize(self) -> bool:
        """Service Discovery-ni ishga tushirish"""
        try:
            self.logger.info("Service Discovery ishga tushirilmoqda...")
            
            # Health check monitoring
            self.running = True
            self._start_health_check_monitor()
            
            self.logger.info("Service Discovery muvaffaqiyatli ishga tushdi")
            return True
            
        except Exception as e:
            self.logger.error(f"Service Discovery ishga tushishda xato: {e}")
            return False
    
    async def shutdown(self):
        """Service Discovery-ni to'xtatish"""
        self.logger.info("Service Discovery to'xtatilmoqda...")
        
        self.running = False
        self.services.clear()
        self.service_tags.clear()
        self.service_providers.clear()
        
        self.executor.shutdown(wait=True)
        self.logger.info("Service Discovery to'xtatildi")
    
    async def register_service(self, service_name: str, capabilities: List[str], 
                             metadata: Dict[str, Any] = None, 
                             provider_module: str = None) -> str:
        """Xizmatni ro'yxatga olish"""
        try:
            # Unique service instance ID yaratish
            service_id = self._generate_service_id(service_name)
            
            service_info = ServiceInfo(
                name=service_name,
                version=metadata.get('version', '1.0.0') if metadata else '1.0.0',
                host=metadata.get('host', 'localhost') if metadata else 'localhost',
                port=metadata.get('port', 8000) if metadata else 8000,
                protocol=metadata.get('protocol', 'http') if metadata else 'http',
                capabilities=capabilities,
                metadata=metadata or {},
                load_balanced=metadata.get('load_balanced', False) if metadata else False
            )
            
            self.services[service_id] = service_info
            if provider_module:
                self.service_providers[service_id] = provider_module
            
            # Capabilities bo'yicha indexlash
            for capability in capabilities:
                if capability not in self.service_tags:
                    self.service_tags[capability] = []
                self.service_tags[capability].append(service_id)
            
            # Health check URL setup
            if service_info.health_check_url is None:
                service_info.health_check_url = self._build_health_check_url(service_info)
            
            # Immediate health check
            await self._check_service_health(service_info)
            
            self.logger.info(f"Xizmat ro'yxatga olindi: {service_name} ({service_id})")
            return service_id
            
        except Exception as e:
            self.logger.error(f"Xizmat ro'yxatga olishda xato: {e}")
            return ""
    
    async def unregister_service(self, service_id: str) -> bool:
        """Xizmatni ro'yxatdan o'chirish"""
        try:
            if service_id not in self.services:
                self.logger.warning(f"Xizmat topilmadi: {service_id}")
                return False
            
            service_info = self.services[service_id]
            
            # Capabilities dan o'chirish
            for capability in service_info.capabilities:
                if capability in self.service_tags:
                    self.service_tags[capability] = [
                        sid for sid in self.service_tags[capability] 
                        if sid != service_id
                    ]
                    if not self.service_tags[capability]:
                        del self.service_tags[capability]
            
            # Service provider dan o'chirish
            if service_id in self.service_providers:
                del self.service_providers[service_id]
            
            # Service dan o'chirish
            del self.services[service_id]
            
            self.logger.info(f"Xizmat ro'yxatdan o'chirildi: {service_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Xizmat ro'yxatdan o'chirishda xato: {e}")
            return False
    
    def discover_services(self, capability: str = None, 
                         tags: List[str] = None,
                         status_filter: ServiceStatus = None) -> List[str]:
        """Xizmatlarni topish"""
        try:
            candidate_services = []
            
            # Capabilities bo'yicha filtr
            if capability:
                if capability in self.service_tags:
                    candidate_services.extend(self.service_tags[capability])
            else:
                candidate_services = list(self.services.keys())
            
            # Tags bo'yicha filtr
            if tags:
                candidate_services = [
                    sid for sid in candidate_services 
                    if self._has_tags(sid, tags)
                ]
            
            # Status bo'yicha filtr
            if status_filter:
                candidate_services = [
                    sid for sid in candidate_services 
                    if self.services[sid].status == status_filter
                ]
            
            return candidate_services
            
        except Exception as e:
            self.logger.error(f"Xizmat discoveryda xato: {e}")
            return []
    
    def get_service_info(self, service_id: str) -> Optional[ServiceInfo]:
        """Xizmat ma'lumotini olish"""
        return self.services.get(service_id)
    
    def get_service_url(self, service_id: str) -> Optional[str]:
        """Xizmat URLini olish"""
        service_info = self.services.get(service_id)
        if not service_info:
            return None
        
        return f"{service_info.protocol}://{service_info.host}:{service_info.port}"
    
    async def check_service_health(self, service_id: str) -> bool:
        """Xizmat health check"""
        try:
            if service_id not in self.services:
                return False
            
            service_info = self.services[service_id]
            return await self._check_service_health(service_info)
            
        except Exception as e:
            self.logger.error(f"Xizmat health checkda xato {service_id}: {e}")
            return False
    
    async def get_healthy_services(self, capability: str = None) -> List[str]:
        """Salomat xizmatlar ro'yxati"""
        try:
            all_services = self.discover_services(capability, status_filter=None)
            healthy_services = []
            
            for service_id in all_services:
                service_info = self.services[service_id]
                if (service_info.status == ServiceStatus.HEALTHY and
                    time.time() - service_info.last_health_check < 60):  # 1 daqiqa ichida
                    healthy_services.append(service_id)
            
            return healthy_services
            
        except Exception as e:
            self.logger.error(f"Salomat xizmatlar olishda xato: {e}")
            return []
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Xizmat statistics"""
        total_services = len(self.services)
        
        status_counts = {}
        for service_info in self.services.values():
            status = service_info.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        capability_counts = {}
        for service_info in self.services.values():
            for capability in service_info.capabilities:
                capability_counts[capability] = capability_counts.get(capability, 0) + 1
        
        return {
            'total_services': total_services,
            'status_distribution': status_counts,
            'capability_distribution': capability_counts,
            'unique_capabilities': len(self.service_tags)
        }
    
    def _generate_service_id(self, service_name: str) -> str:
        """Unique service ID yaratish"""
        timestamp = str(time.time())
        hash_input = f"{service_name}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def _build_health_check_url(self, service_info: ServiceInfo) -> str:
        """Health check URL yaratish"""
        base_url = self.get_service_url(service_info.id)
        return f"{base_url}/health" if base_url else None
    
    def _has_tags(self, service_id: str, tags: List[str]) -> bool:
        """Xizmatning tegishli taglarga ega ekanligini tekshirish"""
        if service_id not in self.services:
            return False
        
        service_info = self.services[service_id]
        for tag in tags:
            if tag not in service_info.metadata.get('tags', []):
                return False
        return True
    
    async def _check_service_health(self, service_info: ServiceInfo) -> bool:
        """Service health check implementation"""
        try:
            if not service_info.health_check_url:
                # Health check URL yo'q, healthy deb hisoblaymiz
                service_info.status = ServiceStatus.HEALTHY
                service_info.last_health_check = time.time()
                return True
            
            # HTTP health check
            import aiohttp
            
            start_time = time.time()
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.health_check_timeout)
            ) as session:
                async with session.get(service_info.health_check_url) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        service_info.status = ServiceStatus.HEALTHY
                        service_info.response_time = response_time
                        service_info.error_count = 0
                        service_info.last_health_check = time.time()
                        return True
                    else:
                        service_info.error_count += 1
                        if service_info.error_count >= self.max_failures:
                            service_info.status = ServiceStatus.UNHEALTHY
                        return False
                        
        except Exception as e:
            self.logger.error(f"Health check da xato {service_info.name}: {e}")
            service_info.error_count += 1
            if service_info.error_count >= self.max_failures:
                service_info.status = ServiceStatus.UNHEALTHY
            return False
    
    def _start_health_check_monitor(self):
        """Health check monitoring ni boshlash"""
        def monitor():
            while self.running:
                try:
                    current_time = time.time()
                    
                    for service_id, service_info in self.services.items():
                        # Scheduled health check
                        if (current_time - service_info.last_health_check >= 
                            self.health_check_interval):
                            # Async health check ni sync contextda ishlatish
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(
                                self._check_service_health(service_info)
                            )
                            loop.close()
                            
                except Exception as e:
                    self.logger.error(f"Health check monitoring da xato: {e}")
                
                time.sleep(10)  # 10 soniya interval
        
        self.executor.submit(monitor)
    
    async def update_service_metadata(self, service_id: str, 
                                    metadata: Dict[str, Any]) -> bool:
        """Xizmat metadata-ni yangilash"""
        try:
            if service_id not in self.services:
                return False
            
            self.services[service_id].metadata.update(metadata)
            
            # If capabilities changed, update index
            new_capabilities = metadata.get('capabilities', [])
            old_capabilities = self.services[service_id].capabilities
            
            if new_capabilities != old_capabilities:
                # Remove from old capability indexes
                for capability in old_capabilities:
                    if capability in self.service_tags:
                        self.service_tags[capability] = [
                            sid for sid in self.service_tags[capability] 
                            if sid != service_id
                        ]
                        if not self.service_tags[capability]:
                            del self.service_tags[capability]
                
                # Add to new capability indexes
                for capability in new_capabilities:
                    if capability not in self.service_tags:
                        self.service_tags[capability] = []
                    self.service_tags[capability].append(service_id)
                
                self.services[service_id].capabilities = new_capabilities
            
            self.logger.info(f"Xizmat metadata yangilandi: {service_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Xizmat metadata yangilashda xato: {e}")
            return False
    
    def find_services_by_provider(self, provider_module: str) -> List[str]:
        """Provider modul bo'yicha xizmatlar topish"""
        return [
            service_id for service_id, provider 
            in self.service_providers.items() 
            if provider == provider_module
        ]
    
    def get_load_balanced_instances(self, service_name: str) -> List[str]:
        """Load balanced service instances"""
        return [
            service_id for service_id, service_info in self.services.items()
            if service_info.name == service_name and service_info.load_balanced
        ]