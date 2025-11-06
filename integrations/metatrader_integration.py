"""
MetaTrader 4/5 Integratsiya Moduli
Orion Starline Trading Platform

Ushbu modul MetaTrader 4 va MetaTrader 5 platformalariga ulanish,
real-time ma'lumot olish va trading operatsiyalarini bajarish imkonini beradi.

Xususiyatlari:
- MetaTrader 4/5 ga ulanish
- Real-time narx ma'lumotlari
- Buy/sell orderlari
- Account holati monitoring
- Position tracking
- News va event olish

Muallif: Orion Starline Team
Sana: 2025-11-05
"""

import asyncio
import logging
import json
import struct
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import socket
import time
import threading

from .third_party_integrations import ThirdPartyIntegration, IntegrationConfig, IntegrationType, IntegrationStatus

logger = logging.getLogger(__name__)


class MTOrderType(Enum):
    """MetaTrader order turlari"""
    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5


class MTOrderStatus(Enum):
    """MetaTrader order holatlari"""
    PLACED = 0
    FILLED = 1
    PARTIALLY_FILLED = 2
    CANCELLED = 3
    REJECTED = 4


class MTPosition:
    """MetaTrader pozitsiya ma'lumotlari"""
    
    def __init__(self):
        self.ticket = 0
        self.symbol = ""
        self.type = 0  # 0=Buy, 1=Sell
        self.volume = 0.0
        self.price_open = 0.0
        self.price_current = 0.0
        self.profit = 0.0
        self.swap = 0.0
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MTOrder:
    """MetaTrader order ma'lumotlari"""
    
    def __init__(self):
        self.ticket = 0
        self.symbol = ""
        self.type = 0
        self.volume = 0.0
        self.price = 0.0
        self.sl = 0.0  # Stop Loss
        self.tp = 0.0  # Take Profit
        self.comment = ""
        self.status = MTOrderStatus.PLACED
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        return data


class MTAccount:
    """MetaTrader account ma'lumotlari"""
    
    def __init__(self):
        self.login = 0
        self.name = ""
        self.trade_mode = 0
        self.leverage = 0
        self.balance = 0.0
        self.credit = 0.0
        self.profit = 0.0
        self.equity = 0.0
        self.margin = 0.0
        self.free_margin = 0.0
        self.margin_level = 0.0
        self.currency = ""
        self.server = ""
        self.trade_allowed = False
        self.expert_enabled = False
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MTQuote:
    """MetaTrader quote ma'lumotlari"""
    
    def __init__(self):
        self.symbol = ""
        self.bid = 0.0
        self.ask = 0.0
        self.spread = 0.0
        self.timestamp = datetime.now()
        self.digits = 5
        self.point = 0.00001
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class MetaTraderIntegration(ThirdPartyIntegration):
    """MetaTrader 4/5 integratsiyasi klassi"""

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.mt_version = "MT5"  # MT4 or MT5
        self.socket_connection = None
        self.account_info = MTAccount()
        self.positions: List[MTPosition] = []
        self.quotes: Dict[str, MTQuote] = {}
        self.orders: List[MTOrder] = []
        
        # Real-time data callbacks
        self.quote_callbacks = []
        self.order_callbacks = []
        self.position_callbacks = []
        self.account_callbacks = []
        
        # Connection settings
        self.command_timeout = 5.0
        self.data_timeout = 1.0
        self.max_retries = 3

    async def connect(self) -> bool:
        """MetaTrader ga ulanish"""
        try:
            self.status = IntegrationStatus.CONNECTING
            await self.emit_event("connecting", {"type": "connection"})
            
            # Socket connection yaratish
            if not await self._create_socket_connection():
                self.status = IntegrationStatus.ERROR
                return False
            
            # Account ma'lumotlarini olish
            if not await self._get_account_info():
                logger.warning("Could not get account info, but continuing...")
            
            # Symbol ma'lumotlarini yuklash
            if not await self._load_symbols():
                logger.warning("Could not load symbols, but continuing...")
            
            # Real-time data stream start
            asyncio.create_task(self._start_real_time_data_stream())
            
            self.status = IntegrationStatus.CONNECTED
            self.last_connected = datetime.now()
            await self.emit_event("connected", {"type": "connection"})
            
            logger.info(f"Connected to MetaTrader {self.mt_version}")
            return True
            
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.error_count += 1
            logger.error(f"Error connecting to MetaTrader: {e}")
            await self.emit_event("error", {"type": "connection", "error": str(e)})
            return False

    async def disconnect(self) -> bool:
        """MetaTrader dan uzilish"""
        try:
            self.status = IntegrationStatus.DISCONNECTED
            
            if self.socket_connection:
                self.socket_connection.close()
                self.socket_connection = None
            
            await self.emit_event("disconnected", {"type": "connection"})
            logger.info("Disconnected from MetaTrader")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from MetaTrader: {e}")
            return False

    async def is_connected(self) -> bool:
        """Ulanish holatini tekshirish"""
        return (self.status == IntegrationStatus.CONNECTED and 
                self.socket_connection is not None)

    async def _create_socket_connection(self) -> bool:
        """Socket ulanish yaratish"""
        try:
            server_url = self.config.server_url or "localhost"
            port = self.config.port or 443 if self.mt_version == "MT5" else 1883
            
            # Bu yerda real MetaTrader Expert Advisor bilan aloqani ta'minlash
            # Simulyatsiya uchun socket yaratamiz
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_connection.settimeout(self.command_timeout)
            
            # Mock connection (real implementatsiyada Expert Advisor bilan bog'lanish)
            logger.info(f"Creating connection to {server_url}:{port}")
            
            # Simulyatsiya uchun muvaffaqiyatli connection qaytaramiz
            return True
            
        except Exception as e:
            logger.error(f"Error creating socket connection: {e}")
            return False

    async def _get_account_info(self) -> bool:
        """Account ma'lumotlarini olish"""
        try:
            # Real implementatsiyada MetaTrader API orqali account ma'lumotlari olinadi
            # Bu yerda mock data qaytaramiz
            
            self.account_info = MTAccount()
            self.account_info.login = 12345678
            self.account_info.name = "Demo Account"
            self.account_info.balance = 10000.0
            self.account_info.equity = 10000.0
            self.account_info.margin = 0.0
            self.account_info.free_margin = 10000.0
            self.account_info.currency = "USD"
            self.account_info.server = "Demo-Server"
            self.account_info.trade_allowed = True
            self.account_info.expert_enabled = True
            
            logger.info("Account info retrieved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return False

    async def _load_symbols(self) -> bool:
        """Symbollarni yuklash"""
        try:
            # Real symbol list (bu yerda mock data)
            demo_symbols = [
                "EURUSD", "GBPUSD", "USDJPY", "USDCHF", 
                "XAUUSD", "XAGUSD", "USOIL", "UKBRENT"
            ]
            
            for symbol in demo_symbols:
                self.quotes[symbol] = MTQuote()
                self.quotes[symbol].symbol = symbol
                self.quotes[symbol].bid = 1.0500 + (hash(symbol) % 100) / 10000
                self.quotes[symbol].ask = self.quotes[symbol].bid + 0.0001
                self.quotes[symbol].spread = 0.0001
            
            logger.info(f"Loaded {len(demo_symbols)} symbols")
            return True
            
        except Exception as e:
            logger.error(f"Error loading symbols: {e}")
            return False

    async def _start_real_time_data_stream(self):
        """Real-time data stream boshlash"""
        while await self.is_connected():
            try:
                # Price update simulyatsiyasi
                for symbol in self.quotes:
                    quote = self.quotes[symbol]
                    # Random price movement
                    price_change = (hash(symbol + str(time.time())) % 20 - 10) / 100000
                    quote.bid += price_change
                    quote.ask = quote.bid + quote.spread
                    quote.timestamp = datetime.now()
                    
                    # Quote callbacks call
                    for callback in self.quote_callbacks:
                        await callback(quote)
                
                await asyncio.sleep(self.data_timeout)
                
            except Exception as e:
                logger.error(f"Error in real-time data stream: {e}")
                await asyncio.sleep(5)

    async def get_quotes(self, symbols: List[str]) -> Dict[str, MTQuote]:
        """Quote ma'lumotlarini olish"""
        try:
            if not await self.is_connected():
                raise ConnectionError("Not connected to MetaTrader")
            
            result = {}
            for symbol in symbols:
                if symbol in self.quotes:
                    result[symbol] = self.quotes[symbol]
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting quotes: {e}")
            return {}

    async def get_positions(self) -> List[MTPosition]:
        """Pozitsiyalar ro'yxatini olish"""
        try:
            if not await self.is_connected():
                raise ConnectionError("Not connected to MetaTrader")
            
            # Real implementatsiyada MetaTrader API orqali pozitsiyalar olinadi
            # Bu yerda mock data qaytaramiz
            
            return self.positions
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []

    async def get_orders(self) -> List[MTOrder]:
        """Orderlar ro'yxatini olish"""
        try:
            if not await self.is_connected():
                raise ConnectionError("Not connected to MetaTrader")
            
            return self.orders
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []

    async def place_order(self, symbol: str, order_type: MTOrderType, 
                         volume: float, price: float = 0.0,
                         sl: float = 0.0, tp: float = 0.0,
                         comment: str = "") -> bool:
        """Order joylashtirish"""
        try:
            if not await self.is_connected():
                raise ConnectionError("Not connected to MetaTrader")
            
            # Order validation
            if volume <= 0:
                raise ValueError("Volume must be positive")
            
            # Real implementatsiyada MetaTrader API orqali order yuboriladi
            # Bu yerda order ni local ro'yxatga qo'shamiz
            
            order = MTOrder()
            order.symbol = symbol
            order.type = order_type.value
            order.volume = volume
            order.price = price
            order.sl = sl
            order.tp = tp
            order.comment = comment
            order.timestamp = datetime.now()
            
            # Mock order placement success
            order.ticket = len(self.orders) + 1000000
            order.status = MTOrderStatus.FILLED
            self.orders.append(order)
            
            # Order callbacks call
            for callback in self.order_callbacks:
                await callback(order)
            
            await self.emit_event("order_placed", {
                "symbol": symbol,
                "type": order_type.name,
                "volume": volume,
                "price": price,
                "ticket": order.ticket
            })
            
            logger.info(f"Order placed: {symbol} {order_type.name} {volume} @ {price}")
            return True
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            await self.emit_event("order_error", {
                "symbol": symbol,
                "error": str(e)
            })
            return False

    async def close_position(self, ticket: int) -> bool:
        """Pozitsiyani yopish"""
        try:
            if not await self.is_connected():
                raise ConnectionError("Not connected to MetaTrader")
            
            # Real implementatsiyada MetaTrader API orqali position yopiladi
            # Bu yerda local ro'yxatdan olib tashlaymiz
            
            for i, position in enumerate(self.positions):
                if position.ticket == ticket:
                    self.positions.pop(i)
                    await self.emit_event("position_closed", {
                        "ticket": ticket,
                        "profit": position.profit
                    })
                    logger.info(f"Position closed: ticket {ticket}")
                    return True
            
            logger.warning(f"Position not found: ticket {ticket}")
            return False
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False

    async def modify_order(self, ticket: int, sl: float = None, 
                          tp: float = None) -> bool:
        """Order o'zgartirish"""
        try:
            if not await self.is_connected():
                raise ConnectionError("Not connected to MetaTrader")
            
            for order in self.orders:
                if order.ticket == ticket:
                    if sl is not None:
                        order.sl = sl
                    if tp is not None:
                        order.tp = tp
                    
                    await self.emit_event("order_modified", {
                        "ticket": ticket,
                        "sl": sl,
                        "tp": tp
                    })
                    logger.info(f"Order modified: ticket {ticket}")
                    return True
            
            logger.warning(f"Order not found: ticket {ticket}")
            return False
            
        except Exception as e:
            logger.error(f"Error modifying order: {e}")
            return False

    async def get_account_info(self) -> Optional[MTAccount]:
        """Account ma'lumotlarini olish"""
        try:
            if not await self.is_connected():
                return None
            
            # Refresh account info
            await self._get_account_info()
            
            for callback in self.account_callbacks:
                await callback(self.account_info)
            
            return self.account_info
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None

    def add_quote_callback(self, callback):
        """Quote callback qo'shish"""
        self.quote_callbacks.append(callback)

    def add_order_callback(self, callback):
        """Order callback qo'shish"""
        self.order_callbacks.append(callback)

    def add_position_callback(self, callback):
        """Position callback qo'shish"""
        self.position_callbacks.append(callback)

    def add_account_callback(self, callback):
        """Account callback qo'shish"""
        self.account_callbacks.append(callback)

    async def health_check(self) -> Dict[str, Any]:
        """Salomatlik tekshiruvi"""
        base_health = await super().health_check()
        
        additional_info = {
            "mt_version": self.mt_version,
            "account_login": self.account_info.login,
            "account_balance": self.account_info.balance,
            "active_positions": len(self.positions),
            "pending_orders": len(self.orders),
            "loaded_symbols": len(self.quotes),
            "real_time_stream_active": await self.is_connected()
        }
        
        base_health.update(additional_info)
        return base_health

    async def send_data(self, data: Dict[str, Any]) -> bool:
        """Ma'lumot yuborish (override)"""
        try:
            action = data.get("action")
            
            if action == "place_order":
                return await self.place_order(
                    symbol=data["symbol"],
                    order_type=MTOrderType(data["order_type"]),
                    volume=data["volume"],
                    price=data.get("price", 0.0),
                    sl=data.get("sl", 0.0),
                    tp=data.get("tp", 0.0),
                    comment=data.get("comment", "")
                )
            
            elif action == "close_position":
                return await self.close_position(data["ticket"])
            
            elif action == "modify_order":
                return await self.modify_order(
                    ticket=data["ticket"],
                    sl=data.get("sl"),
                    tp=data.get("tp")
                )
            
            elif action == "get_quotes":
                quotes = await self.get_quotes(data["symbols"])
                return len(quotes) > 0
            
            else:
                logger.warning(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending data to MetaTrader: {e}")
            return False


# Factory function
def create_metatrader_integration(config: IntegrationConfig) -> MetaTraderIntegration:
    """MetaTrader integratsiyasini yaratish"""
    if config.integration_type != IntegrationType.METATRADER:
        raise ValueError(f"Invalid integration type: {config.integration_type}")
    
    return MetaTraderIntegration(config)


# Demo funksiya
async def demo_metatrader_integration():
    """Demo MetaTrader integratsiyasi"""
    print("=== MetaTrader Integration Demo ===")
    
    # Integration yaratish
    config = IntegrationConfig(
        integration_type=IntegrationType.METATRADER,
        name="MT5_Demo",
        enabled=True,
        server_url="localhost",
        port=443
    )
    
    integration = create_metatrader_integration(config)
    
    # Event handlers
    async def on_quote_update(quote: MTQuote):
        print(f"Quote Update: {quote.symbol} Bid: {quote.bid} Ask: {quote.ask}")
    
    async def on_order_update(order: MTOrder):
        print(f"Order Update: {order.symbol} {order.status.name} Ticket: {order.ticket}")
    
    integration.add_quote_callback(on_quote_update)
    integration.add_order_callback(on_order_update)
    
    # Connection test
    success = await integration.connect()
    print(f"Connection success: {success}")
    
    if success:
        # Account info olish
        account = await integration.get_account_info()
        if account:
            print(f"Account: {account.name}, Balance: {account.balance}")
        
        # Quotes olish
        quotes = await integration.get_quotes(["EURUSD", "GBPUSD"])
        print(f"Quotes: {len(quotes)}")
        
        # Order joylashtirish
        order_success = await integration.place_order(
            symbol="EURUSD",
            order_type=MTOrderType.BUY,
            volume=0.1,
            price=1.0500,
            sl=1.0450,
            tp=1.0550,
            comment="Demo order"
        )
        print(f"Order placed: {order_success}")
        
        # Health check
        health = await integration.health_check()
        print(f"Health: {json.dumps(health, indent=2, default=str)}")
        
        # Disconnect
        await integration.disconnect()
    
    print("=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(demo_metatrader_integration())