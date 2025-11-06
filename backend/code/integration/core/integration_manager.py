"""
Integration Manager
==================

Bu modul barcha modullar o'rtasida integratsiyani boshqaradi.
U service discovery, event-driven architecture va plugin architecture-ni qo'llab-quvvatlaydi.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from concurrent.futures import ThreadPoolExecutor

from .plugin_manager import PluginManager
from .service_discovery import ServiceDiscovery
from .event_system import EventSystem
from .message_queue import MessageQueue

class ModuleStatus(Enum):
    """Modul holati"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class ModuleInfo:
    """Modul haqida ma'lumot"""
    name: str
    version: str
    module_type: str
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    status: ModuleStatus = ModuleStatus.INITIALIZING
    health_score: float = 1.0
    last_heartbeat: float = field(default_factory=time.time)
    config: Dict[str, Any] = field(default_factory=dict)

class IntegrationManager:
    """
    Asosiy Integration Manager
    
    Barcha modullar o'rtasida integratsiyani boshqaradi,
    service discovery, event handling va communication-ni ta'minlaydi.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.modules: Dict[str, ModuleInfo] = {}
        self.plugin_manager = PluginManager()
        self.service_discovery = ServiceDiscovery()
        self.event_system = EventSystem()
        self.message_queue = MessageQueue()
        
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Event handlers
        self.module_event_handlers: Dict[str, Callable] = {}
        
        self.running = False
        self._lock = threading.RLock()
    
    async def initialize(self) -> bool:
        """Integration manager-ni ishga tushirish"""
        try:
            self.logger.info("Integration Manager ishga tushirilmoqda...")
            
            # Komponentlarni ishga tushirish
            await self.plugin_manager.initialize()
            await self.service_discovery.initialize()
            await self.event_system.initialize()
            await self.message_queue.initialize()
            
            # Event handlers ni sozlash
            self._setup_event_handlers()
            
            # Heartbeat monitoring
            self._start_heartbeat_monitor()
            
            self.running = True
            self.logger.info("Integration Manager muvaffaqiyatli ishga tushdi")
            return True
            
        except Exception as e:
            self.logger.error(f"Integration Manager ishga tushishda xato: {e}")
            return False
    
    async def shutdown(self):
        """Integration Manager-ni to'xtatish"""
        self.logger.info("Integration Manager to'xtatilmoqda...")
        
        self.running = False
        
        # Barcha modullarni to'xtatish
        with self._lock:
            for module_info in self.modules.values():
                await self._stop_module(module_info)
        
        # Komponentlarni to'xtatish
        await self.message_queue.shutdown()
        await self.event_system.shutdown()
        await self.service_discovery.shutdown()
        await self.plugin_manager.shutdown()
        
        self.executor.shutdown(wait=True)
        self.logger.info("Integration Manager to'xtatildi")
    
    def register_module(self, module_info: ModuleInfo) -> bool:
        """Modulni ro'yxatga olish"""
        try:
            with self._lock:
                self.logger.info(f"Modul ro'yxatga olinmoqda: {module_info.name}")
                
                # Dependencies tekshirish
                if not self._check_dependencies(module_info):
                    self.logger.error(f"Modul dependencies topilmadi: {module_info.name}")
                    return False
                
                # Modulni ro'yxatga olish
                self.modules[module_info.name] = module_info
                module_info.status = ModuleStatus.ACTIVE
                
                # Service discovery ga qo'shish
                self.service_discovery.register_service(
                    module_info.name, 
                    module_info.capabilities,
                    module_info.config
                )
                
                # Event system ga ulash
                self.event_system.subscribe_to_events(
                    f"module.{module_info.name}",
                    self._handle_module_event
                )
                
                self.logger.info(f"Modul muvaffaqiyatli ro'yxatga olindi: {module_info.name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Modul ro'yxatga olishda xato: {e}")
            return False
    
    def unregister_module(self, module_name: str) -> bool:
        """Modulni ro'yxatdan o'chirish"""
        try:
            with self._lock:
                if module_name not in self.modules:
                    self.logger.warning(f"Modul topilmadi: {module_name}")
                    return False
                
                module_info = self.modules[module_name]
                module_info.status = ModuleStatus.STOPPED
                
                # Service discovery dan o'chirish
                self.service_discovery.unregister_service(module_name)
                
                # Event subscription ni o'chirish
                self.event_system.unsubscribe_from_events(
                    f"module.{module_name}",
                    self._handle_module_event
                )
                
                # Ro'yxatdan o'chirish
                del self.modules[module_name]
                
                self.logger.info(f"Modul ro'yxatdan o'chirildi: {module_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Modul ro'yxatdan o'chirishda xato: {e}")
            return False
    
    async def send_message(self, source_module: str, target_module: str, 
                          message_type: str, data: Any, priority: int = 1) -> bool:
        """Modullar o'rtasida xabar yuborish"""
        try:
            # Target modul mavjudligini tekshirish
            if target_module not in self.modules:
                self.logger.error(f"Target modul topilmadi: {target_module}")
                return False
            
            # Source modul mavjudligini tekshirish
            if source_module not in self.modules:
                self.logger.error(f"Source modul topilmadi: {source_module}")
                return False
            
            message = {
                'source': source_module,
                'target': target_module,
                'type': message_type,
                'data': data,
                'timestamp': time.time(),
                'priority': priority
            }
            
            # Message queue ga joylash
            await self.message_queue.put(message)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Xabar yuborishda xato: {e}")
            return False
    
    async def broadcast_message(self, source_module: str, message_type: str, 
                              data: Any, target_capability: str = None) -> bool:
        """Barcha modullarga xabar yuborish"""
        try:
            targets = []
            
            # Target capability bo'yicha filtr
            if target_capability:
                for module_name, module_info in self.modules.items():
                    if target_capability in module_info.capabilities:
                        targets.append(module_name)
            else:
                targets = list(self.modules.keys())
            
            # Xabarlarni yuborish
            for target in targets:
                if target != source_module:  # O'ziga xabar yubormaslik
                    await self.send_message(source_module, target, message_type, data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Broadcast xabar yuborishda xato: {e}")
            return False
    
    def get_module_status(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Modul holatini olish"""
        if module_name not in self.modules:
            return None
        
        module_info = self.modules[module_name]
        return {
            'name': module_info.name,
            'version': module_info.version,
            'type': module_info.module_type,
            'status': module_info.status.value,
            'health_score': module_info.health_score,
            'last_heartbeat': module_info.last_heartbeat,
            'capabilities': module_info.capabilities,
            'dependencies': module_info.dependencies
        }
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """Barcha modullar ro'yxatini olish"""
        return [self.get_module_status(name) for name in self.modules.keys()]
    
    def get_healthy_modules(self) -> List[str]:
        """Salomatlik darajasi yaxshi modullar ro'yxati"""
        healthy_modules = []
        current_time = time.time()
        
        for module_name, module_info in self.modules.items():
            if (module_info.status == ModuleStatus.ACTIVE and
                module_info.health_score > 0.7 and
                current_time - module_info.last_heartbeat < 30):  # 30 sekund ichida
                healthy_modules.append(module_name)
        
        return healthy_modules
    
    def _setup_event_handlers(self):
        """Event handlers ni sozlash"""
        # Message queue dan xabarlarni olish
        self.message_queue.subscribe(self._handle_message)
        
        # Module events
        self.event_system.subscribe_to_events(
            "module.*", 
            self._handle_module_lifecycle_event
        )
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Xabarni qayta ishlash"""
        try:
            target = message.get('target')
            if target and target in self.modules:
                # Target modulga event yuborish
                await self.event_system.emit_event(
                    f"message.{target}",
                    message
                )
        except Exception as e:
            self.logger.error(f"Xabar qayta ishlashda xato: {e}")
    
    async def _handle_module_event(self, event_type: str, event_data: Dict[str, Any]):
        """Modul event-larini qayta ishlash"""
        try:
            module_name = event_data.get('module')
            if module_name and module_name in self.modules:
                # Health score yangilash
                if event_type == 'heartbeat':
                    self.modules[module_name].last_heartbeat = time.time()
                elif event_type == 'error':
                    self.modules[module_name].health_score *= 0.9
                    self.modules[module_name].status = ModuleStatus.ERROR
                elif event_type == 'recovery':
                    self.modules[module_name].health_score = min(1.0, 
                        self.modules[module_name].health_score + 0.1)
                    self.modules[module_name].status = ModuleStatus.ACTIVE
        except Exception as e:
            self.logger.error(f"Modul event qayta ishlashda xato: {e}")
    
    async def _handle_module_lifecycle_event(self, event_type: str, event_data: Dict[str, Any]):
        """Modul lifecycle event-larini qayta ishlash"""
        try:
            if event_type == 'module.started':
                module_name = event_data.get('module')
                if module_name in self.modules:
                    self.modules[module_name].status = ModuleStatus.ACTIVE
            elif event_type == 'module.stopped':
                module_name = event_data.get('module')
                if module_name in self.modules:
                    self.modules[module_name].status = ModuleStatus.STOPPED
        except Exception as e:
            self.logger.error(f"Modul lifecycle event qayta ishlashda xato: {e}")
    
    def _check_dependencies(self, module_info: ModuleInfo) -> bool:
        """Modul dependencies-ni tekshirish"""
        for dependency in module_info.dependencies:
            if dependency not in self.modules:
                self.logger.error(f"Dependency topilmadi: {dependency}")
                return False
        return True
    
    async def _stop_module(self, module_info: ModuleInfo):
        """Modulni to'xtatish"""
        try:
            module_info.status = ModuleStatus.STOPPED
            self.logger.info(f"Modul to'xtatildi: {module_info.name}")
        except Exception as e:
            self.logger.error(f"Modul to'xtatishda xato: {e}")
    
    def _start_heartbeat_monitor(self):
        """Heartbeat monitoring ni boshlash"""
        def monitor():
            while self.running:
                try:
                    current_time = time.time()
                    for module_name, module_info in self.modules.items():
                        if (current_time - module_info.last_heartbeat > 60 and
                            module_info.status == ModuleStatus.ACTIVE):
                            # Heartbeat timeout
                            module_info.health_score *= 0.8
                            if module_info.health_score < 0.3:
                                module_info.status = ModuleStatus.ERROR
                                self.event_system.emit_event(
                                    "module.error",
                                    {'module': module_name, 'reason': 'heartbeat_timeout'}
                                )
                except Exception as e:
                    self.logger.error(f"Heartbeat monitoring da xato: {e}")
                
                time.sleep(10)  # 10 soniya
        self.executor.submit(monitor)