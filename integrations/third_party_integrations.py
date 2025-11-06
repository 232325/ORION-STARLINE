"""
Uchinchi Tomon Integratsiya Tizimi
Orion Starline Trading Platform

Ushbu modul turli xil uchinchi tomon xizmatlari va API'larni integratsiya qilish uchun
asosiy interfeys va boshqaruv tizimini ta'minlaydi.

Xususiyatlari:
- MetaTrader 4/5 integratsiyasi
- Interactive Brokers integratsiyasi  
- TradingView integratsiyasi
- Slack/Discord webhook integratsiyasi
- Boshqa brokerlar API'lari
- Webhook tizimi

Muallif: Orion Starline Team
Sana: 2025-11-05
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import aiohttp
import websockets
from enum import Enum

# Logging konfiguratsiya
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationType(Enum):
    """Integratsiya turlari"""
    METATRADER = "metatrader"
    INTERACTIVE_BROKERS = "interactive_brokers"
    TRADINGVIEW = "tradingview"
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    BROKER_API = "broker_api"


class IntegrationStatus(Enum):
    """Integratsiya holatlari"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class IntegrationConfig:
    """Integratsiya konfiguratsiyasi"""
    integration_type: IntegrationType
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    server_url: Optional[str] = None
    port: Optional[int] = None
    timeout: int = 30
    retry_attempts: int = 3
    auto_reconnect: bool = True
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konfiguratsiyani dict ga o'tkazish"""
        data = asdict(self)
        data['integration_type'] = self.integration_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntegrationConfig':
        """Dict dan IntegrationConfig obyektini yaratish"""
        data['integration_type'] = IntegrationType(data['integration_type'])
        return cls(**data)


@dataclass
class IntegrationEvent:
    """Integratsiya voqeasi"""
    integration_type: IntegrationType
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    status: IntegrationStatus

    def to_dict(self) -> Dict[str, Any]:
        """Voqeani dict ga o'tkazish"""
        data = asdict(self)
        data['integration_type'] = self.integration_type.value
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class ThirdPartyIntegration(ABC):
    """Uchinchi tomon integratsiyasi uchun asosiy klass"""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.status = IntegrationStatus.DISCONNECTED
        self.last_connected: Optional[datetime] = None
        self.connection_count = 0
        self.error_count = 0
        self.event_handlers: List[callable] = []

    @abstractmethod
    async def connect(self) -> bool:
        """Ulanish"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Ulanishni uzish"""
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """Holat tekshirish"""
        pass

    async def send_data(self, data: Dict[str, Any]) -> bool:
        """Ma'lumot yuborish"""
        try:
            logger.info(f"Sending data to {self.config.integration_type.value}: {data}")
            return True
        except Exception as e:
            logger.error(f"Error sending data to {self.config.integration_type.value}: {e}")
            return False

    async def receive_data(self) -> Optional[Dict[str, Any]]:
        """Ma'lumot olish"""
        try:
            # Bu metod override qilinishi kerak
            return None
        except Exception as e:
            logger.error(f"Error receiving data from {self.config.integration_type.value}: {e}")
            return None

    def add_event_handler(self, handler: callable):
        """Voqealar uchun handler qo'shish"""
        self.event_handlers.append(handler)

    def remove_event_handler(self, handler: callable):
        """Voqealar uchun handler olib tashlash"""
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)

    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Voqeani emit qilish"""
        event = IntegrationEvent(
            integration_type=self.config.integration_type,
            event_type=event_type,
            timestamp=datetime.now(),
            data=data,
            status=self.status
        )

        for handler in self.event_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Salomatlik tekshiruvi"""
        return {
            "integration_type": self.config.integration_type.value,
            "status": self.status.value,
            "last_connected": self.last_connected.isoformat() if self.last_connected else None,
            "connection_count": self.connection_count,
            "error_count": self.error_count,
            "uptime": (datetime.now() - self.last_connected).total_seconds() if self.last_connected else 0
        }


class ThirdPartyIntegrationManager:
    """Uchinchi tomon integratsiyalarini boshqaruvchi klass"""

    def __init__(self):
        self.integrations: Dict[str, ThirdPartyIntegration] = {}
        self.configs: Dict[str, IntegrationConfig] = {}
        self.global_event_handlers: List[callable] = []
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager kirish"""
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager chiqish"""
        await self.disconnect_all()
        if self._session:
            await self._session.close()

    async def add_integration(self, integration: ThirdPartyIntegration, config: IntegrationConfig):
        """Integratsiya qo'shish"""
        self.integrations[config.name] = integration
        self.configs[config.name] = config
        
        # Integratsiya voqealari uchun global handler qo'shish
        integration.add_event_handler(self._handle_integration_event)

        logger.info(f"Added integration: {config.name} ({config.integration_type.value})")

    async def remove_integration(self, name: str) -> bool:
        """Integratsiyani olib tashlash"""
        if name in self.integrations:
            integration = self.integrations[name]
            await integration.disconnect()
            del self.integrations[name]
            del self.configs[name]
            logger.info(f"Removed integration: {name}")
            return True
        return False

    async def connect_integration(self, name: str) -> bool:
        """Ma'lum integratsiyaga ulanish"""
        if name not in self.integrations:
            logger.error(f"Integration not found: {name}")
            return False

        integration = self.integrations[name]
        config = self.configs[name]

        if not config.enabled:
            logger.warning(f"Integration {name} is disabled")
            return False

        try:
            await integration.emit_event("connecting", {"name": name})
            success = await integration.connect()
            
            if success:
                integration.status = IntegrationStatus.CONNECTED
                integration.connection_count += 1
                integration.last_connected = datetime.now()
                await integration.emit_event("connected", {"name": name})
                logger.info(f"Connected to integration: {name}")
            else:
                integration.status = IntegrationStatus.ERROR
                await integration.emit_event("connection_failed", {"name": name})
                
            return success
            
        except Exception as e:
            integration.status = IntegrationStatus.ERROR
            integration.error_count += 1
            logger.error(f"Error connecting to {name}: {e}")
            await integration.emit_event("error", {"name": name, "error": str(e)})
            return False

    async def disconnect_integration(self, name: str) -> bool:
        """Ma'lum integratsiyani uzish"""
        if name not in self.integrations:
            return False

        integration = self.integrations[name]
        
        try:
            await integration.emit_event("disconnecting", {"name": name})
            success = await integration.disconnect()
            
            if success:
                integration.status = IntegrationStatus.DISCONNECTED
                await integration.emit_event("disconnected", {"name": name})
                logger.info(f"Disconnected from integration: {name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error disconnecting from {name}: {e}")
            return False

    async def connect_all(self) -> Dict[str, bool]:
        """Barcha integratsiyalarni ulash"""
        results = {}
        
        # Parallel connection attempts
        tasks = []
        for name in self.integrations.keys():
            tasks.append(self.connect_integration(name))
        
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, name in enumerate(self.integrations.keys()):
            results[name] = not isinstance(results_list[i], Exception) and results_list[i] is True
        
        return results

    async def disconnect_all(self):
        """Barcha integratsiyalarni uzish"""
        for name in list(self.integrations.keys()):
            await self.disconnect_integration(name)

    async def send_to_integration(self, name: str, data: Dict[str, Any]) -> bool:
        """Ma'lum integratsiyaga ma'lumot yuborish"""
        if name not in self.integrations:
            return False
        
        integration = self.integrations[name]
        if integration.status != IntegrationStatus.CONNECTED:
            return False
        
        return await integration.send_data(data)

    async def broadcast_to_all(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """Barcha ulangan integratsiyalarga ma'lumot yuborish"""
        results = {}
        
        for name, integration in self.integrations.items():
            if integration.status == IntegrationStatus.CONNECTED:
                results[name] = await integration.send_data(data)
            else:
                results[name] = False
        
        return results

    async def get_integration_status(self) -> Dict[str, Dict[str, Any]]:
        """Barcha integratsiyalar holatini olish"""
        status = {}
        
        for name, integration in self.integrations.items():
            status[name] = await integration.health_check()
        
        return status

    async def reconnect_failed_integrations(self) -> Dict[str, bool]:
        """Xato bo'lgan integratsiyalarni qayta ulash"""
        results = {}
        
        for name, integration in self.integrations.items():
            config = self.configs[name]
            
            if integration.status == IntegrationStatus.ERROR and config.auto_reconnect:
                results[name] = await self.connect_integration(name)
            else:
                results[name] = False
        
        return results

    def add_global_event_handler(self, handler: callable):
        """Global voqealar uchun handler qo'shish"""
        self.global_event_handlers.append(handler)

    def remove_global_event_handler(self, handler: callable):
        """Global voqealar uchun handler olib tashlash"""
        if handler in self.global_event_handlers:
            self.global_event_handlers.remove(handler)

    async def _handle_integration_event(self, event: IntegrationEvent):
        """Integratsiya voqealarini global handler'larga yuborish"""
        for handler in self.global_event_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in global event handler: {e}")

    async def save_configs(self, filepath: str):
        """Konfiguratsiyalarni saqlash"""
        configs_data = {}
        for name, config in self.configs.items():
            configs_data[name] = config.to_dict()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(configs_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Integration configs saved to {filepath}")

    async def load_configs(self, filepath: str):
        """Konfiguratsiyalarni yuklash"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                configs_data = json.load(f)
            
            for name, data in configs_data.items():
                config = IntegrationConfig.from_dict(data)
                self.configs[name] = config
            
            logger.info(f"Integration configs loaded from {filepath}")
            
        except FileNotFoundError:
            logger.warning(f"Config file not found: {filepath}")
        except Exception as e:
            logger.error(f"Error loading configs: {e}")


# Utility funksiyalar
async def create_integration_manager() -> ThirdPartyIntegrationManager:
    """Integration manager yaratish"""
    return ThirdPartyIntegrationManager()


async def demo_integration_manager():
    """Demo integratsiya manager"""
    print("=== Uchinchi Tomon Integratsiya Tizimi Demo ===")
    
    async with await create_integration_manager() as manager:
        # Integration configurations yaratish
        configs = [
            IntegrationConfig(
                integration_type=IntegrationType.METATRADER,
                name="MT5_Broker1",
                enabled=True,
                server_url="192.168.1.100",
                port=443
            ),
            IntegrationConfig(
                integration_type=IntegrationType.INTERACTIVE_BROKERS,
                name="IB_Gateway",
                enabled=True,
                server_url="localhost",
                port=7497
            ),
            IntegrationConfig(
                integration_type=IntegrationType.TRADINGVIEW,
                name="TradingView_Pro",
                enabled=True,
                api_key="demo_key"
            ),
            IntegrationConfig(
                integration_type=IntegrationType.SLACK,
                name="Slack_Trading",
                enabled=True,
                webhook_url="https://hooks.slack.com/services/demo"
            )
        ]
        
        # Demo integratsiyalar yaratish
        for config in configs:
            # Bu yerda real integratsiya klasslari yaratiladi
            print(f"Creating integration: {config.name} ({config.integration_type.value})")
        
        # Manager holatini ko'rsatish
        status = await manager.get_integration_status()
        print(f"\nIntegration Status: {json.dumps(status, indent=2, ensure_ascii=False)}")
        
        # Test ma'lumot yuborish
        test_data = {
            "message": "Test ma'lumoti",
            "timestamp": datetime.now().isoformat(),
            "type": "test_event"
        }
        
        print(f"\nTest ma'lumot yuborish: {test_data}")
        results = await manager.broadcast_to_all(test_data)
        print(f"Yuborish natijalari: {results}")


if __name__ == "__main__":
    asyncio.run(demo_integration_manager())