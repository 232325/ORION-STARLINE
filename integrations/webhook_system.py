"""
Webhook Tizimi Moduli
Orion Starline Trading Platform

Ushbu modul webhook xizmatlari bilan integratsiyani ta'minlaydi:
- TradingView
- Slack
- Discord
- Telegram
- Webhook servislari (Zapier, IFTTT)
- Custom webhooks

Xususiyatlari:
- Outgoing webhooks
- Incoming webhooks
- Event filtering
- Retry mechanisms
- Rate limiting
- Security validation

Muallif: Orion Starline Team
Sana: 2025-11-05
"""

import asyncio
import logging
import json
import hashlib
import hmac
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import websockets
from urllib.parse import urlparse, parse_qs
import secrets

from .third_party_integrations import ThirdPartyIntegration, IntegrationConfig, IntegrationType, IntegrationStatus

logger = logging.getLogger(__name__)


class WebhookType(Enum):
    """Webhook turlari"""
    TRADINGVIEW = "tradingview"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    ZAPIER = "zapier"
    IFTTT = "ifttt"
    CUSTOM = "custom"
    OUTGOING = "outgoing"
    INCOMING = "incoming"


class WebhookStatus(Enum):
    """Webhook holatlari"""
    INACTIVE = "inactive"
    LISTENING = "listening"
    SENDING = "sending"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


class WebhookEvent:
    """Webhook voqeasi"""
    
    def __init__(self, webhook_type: WebhookType, event_type: str, data: Dict[str, Any]):
        self.webhook_type = webhook_type
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()
        self.id = secrets.token_hex(8)
        self.retry_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "webhook_type": self.webhook_type.value,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "retry_count": self.retry_count
        }


@dataclass
class WebhookEndpoint:
    """Webhook endpoint ma'lumotlari"""
    url: str
    method: str = "POST"
    headers: Dict[str, str] = None
    timeout: int = 30
    retry_attempts: int = 3
    rate_limit: int = 100  # Per minute
    enabled: bool = True
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {"Content-Type": "application/json"}


@dataclass
class WebhookSecurity:
    """Webhook xavfsizlik sozlamalari"""
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    signature_header: str = "X-Webhook-Signature"
    timestamp_header: str = "X-Webhook-Timestamp"
    verify_tolerance: int = 300  # 5 minutes


class WebhookManager:
    """Webhook boshqaruvchi"""
    
    def __init__(self):
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.incoming_handlers: Dict[str, Callable] = {}
        self.outgoing_queue: asyncio.Queue = asyncio.Queue()
        self.rate_limiters: Dict[str, List[datetime]] = {}
        self.security_config: Optional[WebhookSecurity] = None
        self.is_running = False
        self._tasks: List[asyncio.Task] = []
    
    def add_endpoint(self, name: str, endpoint: WebhookEndpoint):
        """Webhook endpoint qo'shish"""
        self.endpoints[name] = endpoint
        logger.info(f"Added webhook endpoint: {name} -> {endpoint.url}")
    
    def remove_endpoint(self, name: str):
        """Webhook endpoint olib tashlash"""
        if name in self.endpoints:
            del self.endpoints[name]
            logger.info(f"Removed webhook endpoint: {name}")
    
    def add_incoming_handler(self, webhook_type: str, handler: Callable):
        """Incoming webhook handler qo'shish"""
        self.incoming_handlers[webhook_type] = handler
        logger.info(f"Added incoming handler for: {webhook_type}")
    
    def set_security_config(self, security: WebhookSecurity):
        """Xavfsizlik konfiguratsiyasini o'rnatish"""
        self.security_config = security
    
    async def send_webhook(self, name: str, data: Dict[str, Any]) -> bool:
        """Webhook yuborish"""
        try:
            if name not in self.endpoints:
                logger.error(f"Webhook endpoint not found: {name}")
                return False
            
            endpoint = self.endpoints[name]
            if not endpoint.enabled:
                logger.warning(f"Webhook endpoint disabled: {name}")
                return False
            
            # Rate limiting check
            if not await self._check_rate_limit(name, endpoint.rate_limit):
                logger.warning(f"Rate limit exceeded for: {name}")
                return False
            
            # Prepare request
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.request(
                        method=endpoint.method,
                        url=endpoint.url,
                        json=data,
                        headers=endpoint.headers,
                        timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
                    ) as response:
                        success = response.status < 400
                        
                        if success:
                            logger.info(f"Webhook sent successfully: {name}")
                            await self._record_success(name)
                        else:
                            logger.error(f"Webhook failed: {name} - Status: {response.status}")
                            await self._record_failure(name)
                        
                        return success
                        
                except asyncio.TimeoutError:
                    logger.error(f"Webhook timeout: {name}")
                    await self._record_failure(name)
                    return False
                except Exception as e:
                    logger.error(f"Webhook error: {name} - {e}")
                    await self._record_failure(name)
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending webhook {name}: {e}")
            return False
    
    async def broadcast_webhook(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """Barcha aktiv webhook'larga yuborish"""
        results = {}
        
        for name, endpoint in self.endpoints.items():
            if endpoint.enabled:
                results[name] = await self.send_webhook(name, data)
            else:
                results[name] = False
        
        return results
    
    async def _check_rate_limit(self, name: str, limit: int) -> bool:
        """Rate limit tekshiruvi"""
        now = datetime.now()
        
        # Clean old timestamps
        if name in self.rate_limiters:
            self.rate_limiters[name] = [
                timestamp for timestamp in self.rate_limiters[name]
                if now - timestamp < timedelta(minutes=1)
            ]
        else:
            self.rate_limiters[name] = []
        
        # Check limit
        current_count = len(self.rate_limiters[name])
        if current_count >= limit:
            return False
        
        # Add current timestamp
        self.rate_limiters[name].append(now)
        return True
    
    async def _record_success(self, name: str):
        """Muvaffaqiyatli webhook qayd qilish"""
        # Implementation for metrics/logging
        pass
    
    async def _record_failure(self, name: str):
        """Muvaffaqiyatsiz webhook qayd qilish"""
        # Implementation for metrics/logging
        pass
    
    async def start(self):
        """Webhook manager ni boshlash"""
        if self.is_running:
            return
        
        self.is_running = True
        self._tasks.append(asyncio.create_task(self._process_queue()))
        logger.info("Webhook manager started")
    
    async def stop(self):
        """Webhook manager ni to'xtatish"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        self._tasks.clear()
        logger.info("Webhook manager stopped")
    
    async def _process_queue(self):
        """Queue dan webhook'larni qayta ishlash"""
        while self.is_running:
            try:
                # Get webhook from queue
                data = await asyncio.wait_for(self.outgoing_queue.get(), timeout=1.0)
                
                # Send webhook
                await self.broadcast_webhook(data)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing webhook queue: {e}")


class TradingViewIntegration(ThirdPartyIntegration):
    """TradingView webhook integratsiyasi"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.webhook_manager = WebhookManager()
        self.signals_callbacks = []
        
        # TradingView webhook endpoint setup
        self._setup_tradingview_endpoints()
    
    def _setup_tradingview_endpoints(self):
        """TradingView endpoint'larini sozlash"""
        webhook_url = self.config.metadata.get("webhook_url") if self.config.metadata else None
        
        if webhook_url:
            endpoint = WebhookEndpoint(
                url=webhook_url,
                method="POST",
                headers={"Content-Type": "application/json"}
            )
            self.webhook_manager.add_endpoint("tradingview_alerts", endpoint)
        
        # Incoming webhook handler
        self.webhook_manager.add_incoming_handler("tradingview", self._handle_tradingview_webhook)
    
    async def connect(self) -> bool:
        """TradingView webhook'lariga ulanish"""
        try:
            self.status = IntegrationStatus.CONNECTING
            await self.emit_event("connecting", {"type": "webhook"})
            
            # Start webhook manager
            await self.webhook_manager.start()
            
            self.status = IntegrationStatus.CONNECTED
            self.last_connected = datetime.now()
            await self.emit_event("connected", {"type": "webhook"})
            
            logger.info("Connected to TradingView webhook")
            return True
            
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.error_count += 1
            logger.error(f"Error connecting to TradingView webhook: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """TradingView webhook'dan uzilish"""
        try:
            await self.webhook_manager.stop()
            self.status = IntegrationStatus.DISCONNECTED
            await self.emit_event("disconnected", {"type": "webhook"})
            logger.info("Disconnected from TradingView webhook")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from TradingView webhook: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Webhook holatini tekshirish"""
        return self.status == IntegrationStatus.CONNECTED
    
    async def send_trading_signal(self, symbol: str, action: str, 
                                 price: Optional[float] = None,
                                 quantity: Optional[float] = None,
                                 stop_loss: Optional[float] = None,
                                 take_profit: Optional[float] = None) -> bool:
        """TradingView signal yuborish"""
        try:
            signal_data = {
                "symbol": symbol,
                "action": action,  # buy, sell, close
                "price": price,
                "quantity": quantity,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "timestamp": datetime.now().isoformat(),
                "source": "orion_starline"
            }
            
            success = await self.webhook_manager.send_webhook("tradingview_alerts", signal_data)
            
            if success:
                await self.emit_event("signal_sent", {
                    "symbol": symbol,
                    "action": action,
                    "price": price
                })
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending trading signal: {e}")
            return False
    
    async def _handle_tradingview_webhook(self, data: Dict[str, Any]):
        """TradingView webhook ma'lumotlarini qayta ishlash"""
        try:
            event = WebhookEvent(WebhookType.TRADINGVIEW, "tradingview_alert", data)
            
            # Signal callbacks
            for callback in self.signals_callbacks:
                await callback(event)
            
            await self.emit_event("signal_received", data)
            
        except Exception as e:
            logger.error(f"Error handling TradingView webhook: {e}")
    
    def add_signal_callback(self, callback: Callable):
        """TradingView signal callback qo'shish"""
        self.signals_callbacks.append(callback)
    
    async def send_data(self, data: Dict[str, Any]) -> bool:
        """Ma'lumot yuborish (override)"""
        try:
            action = data.get("action")
            
            if action == "send_signal":
                return await self.send_trading_signal(
                    symbol=data["symbol"],
                    action=data["signal_action"],
                    price=data.get("price"),
                    quantity=data.get("quantity"),
                    stop_loss=data.get("stop_loss"),
                    take_profit=data.get("take_profit")
                )
            
            else:
                logger.warning(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending data to TradingView: {e}")
            return False


class SlackIntegration(ThirdPartyIntegration):
    """Slack webhook integratsiyasi"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.webhook_manager = WebhookManager()
        self.message_callbacks = []
        
        # Slack webhook setup
        self._setup_slack_endpoints()
    
    def _setup_slack_endpoints(self):
        """Slack endpoint'larini sozlash"""
        webhook_url = self.config.metadata.get("webhook_url") if self.config.metadata else None
        
        if webhook_url:
            endpoint = WebhookEndpoint(
                url=webhook_url,
                method="POST",
                headers={"Content-Type": "application/json"}
            )
            self.webhook_manager.add_endpoint("slack_alerts", endpoint)
        
        # Incoming webhook handler
        self.webhook_manager.add_incoming_handler("slack", self._handle_slack_webhook)
    
    async def connect(self) -> bool:
        """Slack webhook'ga ulanish"""
        try:
            self.status = IntegrationStatus.CONNECTING
            await self.emit_event("connecting", {"type": "webhook"})
            
            await self.webhook_manager.start()
            
            self.status = IntegrationStatus.CONNECTED
            self.last_connected = datetime.now()
            await self.emit_event("connected", {"type": "webhook"})
            
            logger.info("Connected to Slack webhook")
            return True
            
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.error_count += 1
            logger.error(f"Error connecting to Slack webhook: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Slack webhook'dan uzilish"""
        try:
            await self.webhook_manager.stop()
            self.status = IntegrationStatus.DISCONNECTED
            await self.emit_event("disconnected", {"type": "webhook"})
            logger.info("Disconnected from Slack webhook")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Slack webhook: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Slack webhook holatini tekshirish"""
        return self.status == IntegrationStatus.CONNECTED
    
    async def send_message(self, message: str, channel: str = None, 
                          username: str = "Orion Trading Bot",
                          icon_emoji: str = ":chart_with_upwards_trend:") -> bool:
        """Slack xabar yuborish"""
        try:
            slack_data = {
                "text": message,
                "username": username,
                "icon_emoji": icon_emoji
            }
            
            if channel:
                slack_data["channel"] = channel
            
            success = await self.webhook_manager.send_webhook("slack_alerts", slack_data)
            
            if success:
                await self.emit_event("message_sent", {
                    "message": message,
                    "channel": channel
                })
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return False
    
    async def send_trading_alert(self, symbol: str, action: str, 
                               price: float, confidence: float = None) -> bool:
        """Trading alert yuborish"""
        try:
            alert_message = f"🚨 *Trading Alert*\n"
            alert_message += f"*Symbol:* {symbol}\n"
            alert_message += f"*Action:* {action.upper()}\n"
            alert_message += f"*Price:* ${price}\n"
            
            if confidence:
                alert_message += f"*Confidence:* {confidence}%\n"
            
            alert_message += f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return await self.send_message(alert_message)
            
        except Exception as e:
            logger.error(f"Error sending trading alert: {e}")
            return False
    
    async def _handle_slack_webhook(self, data: Dict[str, Any]):
        """Slack webhook ma'lumotlarini qayta ishlash"""
        try:
            event = WebhookEvent(WebhookType.SLACK, "slack_message", data)
            
            # Message callbacks
            for callback in self.message_callbacks:
                await callback(event)
            
            await self.emit_event("message_received", data)
            
        except Exception as e:
            logger.error(f"Error handling Slack webhook: {e}")
    
    def add_message_callback(self, callback: Callable):
        """Slack message callback qo'shish"""
        self.message_callbacks.append(callback)


class DiscordIntegration(ThirdPartyIntegration):
    """Discord webhook integratsiyasi"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.webhook_manager = WebhookManager()
        self.message_callbacks = []
        
        # Discord webhook setup
        self._setup_discord_endpoints()
    
    def _setup_discord_endpoints(self):
        """Discord endpoint'larini sozlash"""
        webhook_url = self.config.metadata.get("webhook_url") if self.config.metadata else None
        
        if webhook_url:
            endpoint = WebhookEndpoint(
                url=webhook_url,
                method="POST",
                headers={"Content-Type": "application/json"}
            )
            self.webhook_manager.add_endpoint("discord_alerts", endpoint)
    
    async def connect(self) -> bool:
        """Discord webhook'ga ulanish"""
        try:
            self.status = IntegrationStatus.CONNECTING
            await self.emit_event("connecting", {"type": "webhook"})
            
            await self.webhook_manager.start()
            
            self.status = IntegrationStatus.CONNECTED
            self.last_connected = datetime.now()
            await self.emit_event("connected", {"type": "webhook"})
            
            logger.info("Connected to Discord webhook")
            return True
            
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.error_count += 1
            logger.error(f"Error connecting to Discord webhook: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Discord webhook'dan uzilish"""
        try:
            await self.webhook_manager.stop()
            self.status = IntegrationStatus.DISCONNECTED
            await self.emit_event("disconnected", {"type": "webhook"})
            logger.info("Disconnected from Discord webhook")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Discord webhook: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Discord webhook holatini tekshirish"""
        return self.status == IntegrationStatus.CONNECTED
    
    async def send_message(self, content: str, username: str = "Orion Trading Bot",
                          avatar_url: str = None) -> bool:
        """Discord xabar yuborish"""
        try:
            discord_data = {
                "content": content,
                "username": username
            }
            
            if avatar_url:
                discord_data["avatar_url"] = avatar_url
            
            success = await self.webhook_manager.send_webhook("discord_alerts", discord_data)
            
            if success:
                await self.emit_event("message_sent", {
                    "content": content,
                    "username": username
                })
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
            return False
    
    async def send_embed(self, title: str, description: str, 
                        color: int = 0x00ff00, fields: List[Dict] = None) -> bool:
        """Discord embed xabar yuborish"""
        try:
            embed = {
                "title": title,
                "description": description,
                "color": color,
                "timestamp": datetime.now().isoformat()
            }
            
            if fields:
                embed["fields"] = fields
            
            discord_data = {
                "embeds": [embed]
            }
            
            return await self.webhook_manager.send_webhook("discord_alerts", discord_data)
            
        except Exception as e:
            logger.error(f"Error sending Discord embed: {e}")
            return False


class WebhookSystemIntegration(ThirdPartyIntegration):
    """Umumiy webhook tizimi integratsiyasi"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.webhook_manager = WebhookManager()
        self.integrations: Dict[str, ThirdPartyIntegration] = {}
        
        # Security setup
        security_config = self.config.metadata.get("security") if self.config.metadata else None
        if security_config:
            self.webhook_manager.set_security_config(
                WebhookSecurity(**security_config)
            )
    
    async def connect(self) -> bool:
        """Webhook tizimini boshlash"""
        try:
            self.status = IntegrationStatus.CONNECTING
            await self.emit_event("connecting", {"type": "webhook_system"})
            
            await self.webhook_manager.start()
            
            self.status = IntegrationStatus.CONNECTED
            self.last_connected = datetime.now()
            await self.emit_event("connected", {"type": "webhook_system"})
            
            logger.info("Webhook system started")
            return True
            
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.error_count += 1
            logger.error(f"Error starting webhook system: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Webhook tizimini to'xtatish"""
        try:
            await self.webhook_manager.stop()
            self.status = IntegrationStatus.DISCONNECTED
            await self.emit_event("disconnected", {"type": "webhook_system"})
            logger.info("Webhook system stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping webhook system: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Webhook tizim holatini tekshirish"""
        return self.status == IntegrationStatus.CONNECTED
    
    def add_webhook_endpoint(self, name: str, endpoint: WebhookEndpoint):
        """Webhook endpoint qo'shish"""
        self.webhook_manager.add_endpoint(name, endpoint)
    
    def add_integration(self, name: str, integration: ThirdPartyIntegration):
        """Webhook integratsiyasi qo'shish"""
        self.integrations[name] = integration
    
    async def send_broadcast(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """Barcha webhook endpoint'larga yuborish"""
        return await self.webhook_manager.broadcast_webhook(data)
    
    async def verify_webhook_signature(self, payload: str, signature: str, 
                                      timestamp: str) -> bool:
        """Webhook imzolash tekshiruvi"""
        if not self.webhook_manager.security_config:
            return True  # No security configured
        
        try:
            # Check timestamp tolerance
            webhook_time = datetime.fromtimestamp(float(timestamp))
            now = datetime.now()
            
            if abs(now - webhook_time) > timedelta(seconds=self.webhook_manager.security_config.verify_tolerance):
                return False
            
            # Verify signature
            expected_signature = hmac.new(
                self.webhook_manager.security_config.secret_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False


# Factory functions
def create_tradingview_integration(config: IntegrationConfig) -> TradingViewIntegration:
    """TradingView integratsiyasini yaratish"""
    if config.integration_type != IntegrationType.TRADINGVIEW:
        raise ValueError(f"Invalid integration type for TradingView: {config.integration_type}")
    
    return TradingViewIntegration(config)


def create_slack_integration(config: IntegrationConfig) -> SlackIntegration:
    """Slack integratsiyasini yaratish"""
    if config.integration_type != IntegrationType.SLACK:
        raise ValueError(f"Invalid integration type for Slack: {config.integration_type}")
    
    return SlackIntegration(config)


def create_discord_integration(config: IntegrationConfig) -> DiscordIntegration:
    """Discord integratsiyasini yaratish"""
    if config.integration_type != IntegrationType.DISCORD:
        raise ValueError(f"Invalid integration type for Discord: {config.integration_type}")
    
    return DiscordIntegration(config)


def create_webhook_system_integration(config: IntegrationConfig) -> WebhookSystemIntegration:
    """Webhook tizimi integratsiyasini yaratish"""
    if config.integration_type != IntegrationType.WEBHOOK:
        raise ValueError(f"Invalid integration type for webhook: {config.integration_type}")
    
    return WebhookSystemIntegration(config)


# Demo funksiya
async def demo_webhook_system():
    """Demo webhook tizimi"""
    print("=== Webhook System Demo ===")
    
    # TradingView demo
    print("\n--- TradingView Integration Demo ---")
    tradingview_config = IntegrationConfig(
        integration_type=IntegrationType.TRADINGVIEW,
        name="TradingView_Webhooks",
        enabled=True,
        metadata={
            "webhook_url": "https://hooks.tradingview.com/hooks/demo"
        }
    )
    
    tv_integration = create_tradingview_integration(tradingview_config)
    
    # Slack demo
    print("\n--- Slack Integration Demo ---")
    slack_config = IntegrationConfig(
        integration_type=IntegrationType.SLACK,
        name="Slack_Alerts",
        enabled=True,
        metadata={
            "webhook_url": "https://hooks.slack.com/services/demo"
        }
    )
    
    slack_integration = create_slack_integration(slack_config)
    
    # Discord demo
    print("\n--- Discord Integration Demo ---")
    discord_config = IntegrationConfig(
        integration_type=IntegrationType.DISCORD,
        name="Discord_Trading",
        enabled=True,
        metadata={
            "webhook_url": "https://discord.com/api/webhooks/demo"
        }
    )
    
    discord_integration = create_discord_integration(discord_config)
    
    # Webhook system demo
    print("\n--- Webhook System Demo ---")
    webhook_config = IntegrationConfig(
        integration_type=IntegrationType.WEBHOOK,
        name="Webhook_System",
        enabled=True
    )
    
    webhook_system = create_webhook_system_integration(webhook_config)
    
    # Add integrations to webhook system
    webhook_system.add_integration("tradingview", tv_integration)
    webhook_system.add_integration("slack", slack_integration)
    webhook_system.add_integration("discord", discord_integration)
    
    # Connect to webhook system
    success = await webhook_system.connect()
    print(f"Webhook system connected: {success}")
    
    if success:
        # Send test signals
        print("\n--- Sending Test Signals ---")
        
        # TradingView signal
        signal_success = await tv_integration.send_trading_signal(
            symbol="EURUSD",
            action="buy",
            price=1.0850,
            quantity=0.1,
            stop_loss=1.0800,
            take_profit=1.0900
        )
        print(f"TradingView signal sent: {signal_success}")
        
        # Slack alert
        alert_success = await slack_integration.send_trading_alert(
            symbol="BTCUSD",
            action="SELL",
            price=45000.0,
            confidence=85
        )
        print(f"Slack alert sent: {alert_success}")
        
        # Discord message
        message_success = await discord_integration.send_message(
            "🚀 New trading opportunity detected!"
        )
        print(f"Discord message sent: {message_success}")
        
        # System broadcast
        broadcast_data = {
            "event": "system_alert",
            "message": "System maintenance completed",
            "timestamp": datetime.now().isoformat()
        }
        
        broadcast_results = await webhook_system.send_broadcast(broadcast_data)
        print(f"Broadcast results: {broadcast_results}")
        
        # Health check
        health = await webhook_system.health_check()
        print(f"System health: {json.dumps(health, indent=2, default=str)}")
        
        await webhook_system.disconnect()
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(demo_webhook_system())