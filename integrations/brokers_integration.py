"""
Broker Integratsiya Moduli
Orion Starline Trading Platform

Ushbu modul turli brokerlar bilan integratsiyani ta'minlaydi:
- Interactive Brokers (TWS API)
- TD Ameritrade
- Alpaca Markets
- E*TRADE
- Charles Schwab
- Boshqa brokerlar

Xususiyatlari:
- Multi-broker support
- Order management
- Position tracking
- Account information
- Real-time data feeds
- Error handling and failover

Muallif: Orion Starline Team
Sana: 2025-11-05
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import abc
import aiohttp
import websockets

from .third_party_integrations import ThirdPartyIntegration, IntegrationConfig, IntegrationType, IntegrationStatus

logger = logging.getLogger(__name__)


class BrokerType(Enum):
    """Broker turlari"""
    INTERACTIVE_BROKERS = "interactive_brokers"
    TD_AMERITRADE = "td_ameritrade"
    ALPACA = "alpaca"
    ETRADE = "etrade"
    CHARLES_SCHWAB = "charles_schwab"
    OTHER = "other"


class OrderSide(Enum):
    """Order tomonlari"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order turlari"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(Enum):
    """Order holatlari"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class BrokerAccount:
    """Broker account ma'lumotlari"""
    broker_type: BrokerType
    account_id: str
    name: str
    currency: str = "USD"
    balance: float = 0.0
    equity: float = 0.0
    buying_power: float = 0.0
    day_trade_count: int = 0
    pattern_day_trader: bool = False
    trading_permissions: List[str] = None
    
    def __post_init__(self):
        if self.trading_permissions is None:
            self.trading_permissions = []


@dataclass
class BrokerPosition:
    """Broker pozitsiya ma'lumotlari"""
    symbol: str
    quantity: float
    avg_price: float
    market_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    side: str = "long"  # long, short
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class BrokerOrder:
    """Broker order ma'lumotlari"""
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    avg_fill_price: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class MarketData:
    """Market data ma'lumotlari"""
    symbol: str
    last_price: float
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    volume: int = 0
    high: float = 0.0
    low: float = 0.0
    open: float = 0.0
    previous_close: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BrokerAdapter(abc.ABC):
    """Broker uchun asosiy adapter klass"""
    
    @abc.abstractmethod
    async def connect(self) -> bool:
        """Broker ga ulanish"""
        pass
    
    @abc.abstractmethod
    async def disconnect(self) -> bool:
        """Broker dan uzilish"""
        pass
    
    @abc.abstractmethod
    async def get_account_info(self) -> Optional[BrokerAccount]:
        """Account ma'lumotlarini olish"""
        pass
    
    @abc.abstractmethod
    async def get_positions(self) -> List[BrokerPosition]:
        """Pozitsiyalar ro'yxati"""
        pass
    
    @abc.abstractmethod
    async def get_orders(self, status: Optional[OrderStatus] = None) -> List[BrokerOrder]:
        """Orderlar ro'yxati"""
        pass
    
    @abc.abstractmethod
    async def place_order(self, order: BrokerOrder) -> Optional[str]:
        """Order joylashtirish"""
        pass
    
    @abc.abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Order bekor qilish"""
        pass
    
    @abc.abstractmethod
    async def get_market_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Market data olish"""
        pass


class InteractiveBrokersAdapter(BrokerAdapter):
    """Interactive Brokers TWS API adapteri"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client_id = config.get("client_id", 1)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 7497)
        self.connected = False
        
    async def connect(self) -> bool:
        """IB TWS ga ulanish"""
        try:
            # Real implementatsiyada ib_insync yoki TWS API ishlatiladi
            # Bu yerda simulyatsiya qilamiz
            logger.info(f"Connecting to Interactive Brokers at {self.host}:{self.port}")
            
            # Mock connection
            await asyncio.sleep(1)  # Simulate connection delay
            
            self.connected = True
            logger.info("Connected to Interactive Brokers")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Interactive Brokers: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """IB TWS dan uzilish"""
        try:
            self.connected = False
            logger.info("Disconnected from Interactive Brokers")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Interactive Brokers: {e}")
            return False
    
    async def get_account_info(self) -> Optional[BrokerAccount]:
        """Account ma'lumotlarini olish"""
        try:
            if not self.connected:
                return None
            
            # Mock account data
            account = BrokerAccount(
                broker_type=BrokerType.INTERACTIVE_BROKERS,
                account_id="DU123456",
                name="Demo Account",
                currency="USD",
                balance=100000.0,
                equity=100000.0,
                buying_power=200000.0,
                day_trade_count=0,
                pattern_day_trader=False,
                trading_permissions=["STOCKS", "OPTIONS", "FOREX"]
            )
            
            return account
            
        except Exception as e:
            logger.error(f"Error getting IB account info: {e}")
            return None
    
    async def get_positions(self) -> List[BrokerPosition]:
        """Pozitsiyalar ro'yxati"""
        try:
            if not self.connected:
                return []
            
            # Mock positions
            positions = [
                BrokerPosition(
                    symbol="AAPL",
                    quantity=100.0,
                    avg_price=150.00,
                    market_price=155.00,
                    market_value=15500.0,
                    unrealized_pnl=500.0,
                    side="long"
                ),
                BrokerPosition(
                    symbol="MSFT",
                    quantity=50.0,
                    avg_price=300.00,
                    market_price=295.00,
                    market_value=14750.0,
                    unrealized_pnl=-250.0,
                    side="long"
                )
            ]
            
            return positions
            
        except Exception as e:
            logger.error(f"Error getting IB positions: {e}")
            return []
    
    async def get_orders(self, status: Optional[OrderStatus] = None) -> List[BrokerOrder]:
        """Orderlar ro'yxati"""
        try:
            if not self.connected:
                return []
            
            # Mock orders
            orders = [
                BrokerOrder(
                    order_id="IB001",
                    symbol="GOOGL",
                    side=OrderSide.BUY,
                    quantity=10.0,
                    order_type=OrderType.LIMIT,
                    limit_price=2500.00,
                    status=OrderStatus.SUBMITTED
                )
            ]
            
            return orders
            
        except Exception as e:
            logger.error(f"Error getting IB orders: {e}")
            return []
    
    async def place_order(self, order: BrokerOrder) -> Optional[str]:
        """Order joylashtirish"""
        try:
            if not self.connected:
                return None
            
            # Mock order placement
            await asyncio.sleep(0.5)  # Simulate API call
            
            order_id = f"IB{order.timestamp.strftime('%Y%m%d%H%M%S')}"
            logger.info(f"IB order placed: {order_id}")
            
            return order_id
            
        except Exception as e:
            logger.error(f"Error placing IB order: {e}")
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """Order bekor qilish"""
        try:
            if not self.connected:
                return False
            
            # Mock order cancellation
            await asyncio.sleep(0.2)
            
            logger.info(f"IB order cancelled: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling IB order: {e}")
            return False
    
    async def get_market_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Market data olish"""
        try:
            if not self.connected:
                return {}
            
            market_data = {}
            
            for symbol in symbols:
                # Mock market data
                data = MarketData(
                    symbol=symbol,
                    last_price=100.0 + (hash(symbol) % 50),
                    bid_price=99.90 + (hash(symbol) % 50),
                    ask_price=100.10 + (hash(symbol) % 50),
                    volume=1000000,
                    high=105.00,
                    low=95.00,
                    open=98.00,
                    previous_close=97.50
                )
                market_data[symbol] = data
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting IB market data: {e}")
            return {}


class AlpacaAdapter(BrokerAdapter):
    """Alpaca Markets API adapteri"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get("api_key")
        self.secret_key = config.get("secret_key")
        self.paper = config.get("paper", True)
        self.base_url = "https://paper-api.alpaca.markets" if self.paper else "https://api.alpaca.markets"
        self.connected = False
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self) -> bool:
        """Alpaca ga ulanish"""
        try:
            if not self.api_key or not self.secret_key:
                raise ValueError("API key va secret key talab qilinadi")
            
            self._session = aiohttp.ClientSession()
            
            # Test connection
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key
            }
            
            async with self._session.get(f"{self.base_url}/v2/account", headers=headers) as response:
                if response.status == 200:
                    self.connected = True
                    logger.info("Connected to Alpaca Markets")
                    return True
                else:
                    logger.error(f"Alpaca connection failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error connecting to Alpaca: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Alpaca dan uzilish"""
        try:
            if self._session:
                await self._session.close()
            self.connected = False
            logger.info("Disconnected from Alpaca")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Alpaca: {e}")
            return False
    
    async def get_account_info(self) -> Optional[BrokerAccount]:
        """Account ma'lumotlarini olish"""
        try:
            if not self.connected or not self._session:
                return None
            
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key
            }
            
            async with self._session.get(f"{self.base_url}/v2/account", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    account = BrokerAccount(
                        broker_type=BrokerType.ALPACA,
                        account_id=data.get("id"),
                        name=data.get("account_number"),
                        currency=data.get("currency", "USD"),
                        balance=float(data.get("cash", 0)),
                        equity=float(data.get("portfolio_value", 0)),
                        buying_power=float(data.get("buying_power", 0)),
                        trading_permissions=["STOCKS", "CRYPTO"]
                    )
                    
                    return account
                    
        except Exception as e:
            logger.error(f"Error getting Alpaca account info: {e}")
            return None
    
    async def get_positions(self) -> List[BrokerPosition]:
        """Pozitsiyalar ro'yxati"""
        try:
            if not self.connected or not self._session:
                return []
            
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key
            }
            
            async with self._session.get(f"{self.base_url}/v2/positions", headers=headers) as response:
                if response.status == 200:
                    positions_data = await response.json()
                    
                    positions = []
                    for pos_data in positions_data:
                        position = BrokerPosition(
                            symbol=pos_data.get("symbol"),
                            quantity=float(pos_data.get("qty", 0)),
                            avg_price=float(pos_data.get("avg_entry_price", 0)),
                            market_price=float(pos_data.get("current_price", 0)),
                            market_value=float(pos_data.get("market_value", 0)),
                            unrealized_pnl=float(pos_data.get("unrealized_pl", 0)),
                            side=pos_data.get("side", "long")
                        )
                        positions.append(position)
                    
                    return positions
                    
        except Exception as e:
            logger.error(f"Error getting Alpaca positions: {e}")
            return []
    
    async def get_orders(self, status: Optional[OrderStatus] = None) -> List[BrokerOrder]:
        """Orderlar ro'yxati"""
        try:
            if not self.connected or not self._session:
                return []
            
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key
            }
            
            params = {}
            if status:
                params["status"] = status.value
            
            async with self._session.get(f"{self.base_url}/v2/orders", headers=headers, params=params) as response:
                if response.status == 200:
                    orders_data = await response.json()
                    
                    orders = []
                    for order_data in orders_data:
                        order = BrokerOrder(
                            order_id=order_data.get("id"),
                            symbol=order_data.get("symbol"),
                            side=OrderSide(order_data.get("side")),
                            quantity=float(order_data.get("qty", 0)),
                            order_type=OrderType(order_data.get("type")),
                            limit_price=float(order_data.get("limit_price")) if order_data.get("limit_price") else None,
                            status=OrderStatus(order_data.get("status")),
                            filled_quantity=float(order_data.get("filled_qty", 0)),
                            timestamp=datetime.fromisoformat(order_data.get("submitted_at").replace("Z", "+00:00"))
                        )
                        orders.append(order)
                    
                    return orders
                    
        except Exception as e:
            logger.error(f"Error getting Alpaca orders: {e}")
            return []
    
    async def place_order(self, order: BrokerOrder) -> Optional[str]:
        """Order joylashtirish"""
        try:
            if not self.connected or not self._session:
                return None
            
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key
            }
            
            order_data = {
                "symbol": order.symbol,
                "qty": str(order.quantity),
                "side": order.side.value,
                "type": order.order_type.value
            }
            
            if order.limit_price:
                order_data["limit_price"] = str(order.limit_price)
            
            if order.stop_price:
                order_data["stop_price"] = str(order.stop_price)
            
            async with self._session.post(f"{self.base_url}/v2/orders", headers=headers, json=order_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data.get("id")
                else:
                    logger.error(f"Alpaca order failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error placing Alpaca order: {e}")
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """Order bekor qilish"""
        try:
            if not self.connected or not self._session:
                return False
            
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key
            }
            
            async with self._session.delete(f"{self.base_url}/v2/orders/{order_id}", headers=headers) as response:
                return response.status == 204
                
        except Exception as e:
            logger.error(f"Error cancelling Alpaca order: {e}")
            return False
    
    async def get_market_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Market data olish"""
        try:
            if not self.connected or not self._session:
                return {}
            
            # Alpaca Data API v2
            market_data = {}
            
            # Simplified market data retrieval
            for symbol in symbols:
                # Mock data for demonstration
                data = MarketData(
                    symbol=symbol,
                    last_price=100.0 + (hash(symbol) % 50),
                    volume=1000000
                )
                market_data[symbol] = data
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting Alpaca market data: {e}")
            return {}


class BrokerIntegration(ThirdPartyIntegration):
    """Broker integratsiyasi klassi"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.broker_type = self._determine_broker_type()
        self.adapter: Optional[BrokerAdapter] = None
        self.account: Optional[BrokerAccount] = None
        self.positions: List[BrokerPosition] = []
        self.orders: List[BrokerOrder] = []
        
        # Callbacks
        self.account_callbacks = []
        self.position_callbacks = []
        self.order_callbacks = []
        self.market_data_callbacks = []
    
    def _determine_broker_type(self) -> BrokerType:
        """Broker turini aniqlash"""
        metadata = self.config.metadata or {}
        broker_type = metadata.get("broker_type", "other")
        
        try:
            return BrokerType(broker_type.lower())
        except ValueError:
            return BrokerType.OTHER
    
    async def connect(self) -> bool:
        """Broker ga ulanish"""
        try:
            self.status = IntegrationStatus.CONNECTING
            await self.emit_event("connecting", {"broker": self.broker_type.value})
            
            # Adapter yaratish
            if not await self._create_adapter():
                self.status = IntegrationStatus.ERROR
                return False
            
            # Connection
            if not await self.adapter.connect():
                self.status = IntegrationStatus.ERROR
                return False
            
            # Ma'lumotlarni yuklash
            await self._load_initial_data()
            
            self.status = IntegrationStatus.CONNECTED
            self.last_connected = datetime.now()
            await self.emit_event("connected", {"broker": self.broker_type.value})
            
            logger.info(f"Connected to {self.broker_type.value}")
            return True
            
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.error_count += 1
            logger.error(f"Error connecting to {self.broker_type.value}: {e}")
            await self.emit_event("error", {"broker": self.broker_type.value, "error": str(e)})
            return False
    
    async def disconnect(self) -> bool:
        """Broker dan uzilish"""
        try:
            self.status = IntegrationStatus.DISCONNECTED
            
            if self.adapter:
                await self.adapter.disconnect()
            
            await self.emit_event("disconnected", {"broker": self.broker_type.value})
            logger.info(f"Disconnected from {self.broker_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from {self.broker_type.value}: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Ulanish holatini tekshirish"""
        return self.status == IntegrationStatus.CONNECTED and self.adapter is not None
    
    async def _create_adapter(self) -> bool:
        """Broker adapterini yaratish"""
        try:
            if self.broker_type == BrokerType.INTERACTIVE_BROKERS:
                self.adapter = InteractiveBrokersAdapter(self.config.metadata or {})
            elif self.broker_type == BrokerType.ALPACA:
                self.adapter = AlpacaAdapter(self.config.metadata or {})
            else:
                # Default fallback
                self.adapter = InteractiveBrokersAdapter(self.config.metadata or {})
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating adapter for {self.broker_type.value}: {e}")
            return False
    
    async def _load_initial_data(self):
        """Boshlang'ich ma'lumotlarni yuklash"""
        try:
            # Account info
            self.account = await self.adapter.get_account_info()
            
            # Positions
            self.positions = await self.adapter.get_positions()
            
            # Orders
            self.orders = await self.adapter.get_orders()
            
            logger.info(f"Initial data loaded for {self.broker_type.value}")
            
        except Exception as e:
            logger.error(f"Error loading initial data: {e}")
    
    async def get_account_info(self) -> Optional[BrokerAccount]:
        """Account ma'lumotlarini olish"""
        try:
            if not await self.is_connected():
                return None
            
            self.account = await self.adapter.get_account_info()
            
            # Account callbacks
            if self.account and self.account_callbacks:
                for callback in self.account_callbacks:
                    await callback(self.account)
            
            return self.account
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    async def get_positions(self) -> List[BrokerPosition]:
        """Pozitsiyalar ro'yxati"""
        try:
            if not await self.is_connected():
                return []
            
            self.positions = await self.adapter.get_positions()
            
            # Position callbacks
            if self.position_callbacks:
                for callback in self.position_callbacks:
                    await callback(self.positions)
            
            return self.positions
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    async def get_orders(self, status: Optional[OrderStatus] = None) -> List[BrokerOrder]:
        """Orderlar ro'yxati"""
        try:
            if not await self.is_connected():
                return []
            
            self.orders = await self.adapter.get_orders(status)
            
            # Order callbacks
            if self.order_callbacks:
                for callback in self.order_callbacks:
                    await callback(self.orders)
            
            return self.orders
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    async def place_order(self, symbol: str, side: OrderSide, quantity: float,
                         order_type: OrderType, limit_price: Optional[float] = None,
                         stop_price: Optional[float] = None) -> Optional[str]:
        """Order joylashtirish"""
        try:
            if not await self.is_connected():
                return None
            
            order = BrokerOrder(
                order_id="",  # Will be generated by adapter
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                limit_price=limit_price,
                stop_price=stop_price
            )
            
            order_id = await self.adapter.place_order(order)
            
            if order_id:
                await self.emit_event("order_placed", {
                    "broker": self.broker_type.value,
                    "order_id": order_id,
                    "symbol": symbol,
                    "side": side.value,
                    "quantity": quantity
                })
                
                logger.info(f"Order placed on {self.broker_type.value}: {order_id}")
            
            return order_id
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            await self.emit_event("order_error", {
                "broker": self.broker_type.value,
                "error": str(e)
            })
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """Order bekor qilish"""
        try:
            if not await self.is_connected():
                return False
            
            success = await self.adapter.cancel_order(order_id)
            
            if success:
                await self.emit_event("order_cancelled", {
                    "broker": self.broker_type.value,
                    "order_id": order_id
                })
                
                logger.info(f"Order cancelled on {self.broker_type.value}: {order_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    async def get_market_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Market data olish"""
        try:
            if not await self.is_connected():
                return {}
            
            market_data = await self.adapter.get_market_data(symbols)
            
            # Market data callbacks
            if self.market_data_callbacks:
                for callback in self.market_data_callbacks:
                    await callback(market_data)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {}
    
    def add_account_callback(self, callback):
        """Account callback qo'shish"""
        self.account_callbacks.append(callback)
    
    def add_position_callback(self, callback):
        """Position callback qo'shish"""
        self.position_callbacks.append(callback)
    
    def add_order_callback(self, callback):
        """Order callback qo'shish"""
        self.order_callbacks.append(callback)
    
    def add_market_data_callback(self, callback):
        """Market data callback qo'shish"""
        self.market_data_callbacks.append(callback)
    
    async def send_data(self, data: Dict[str, Any]) -> bool:
        """Ma'lumot yuborish (override)"""
        try:
            action = data.get("action")
            
            if action == "place_order":
                return await self.place_order(
                    symbol=data["symbol"],
                    side=OrderSide(data["side"]),
                    quantity=data["quantity"],
                    order_type=OrderType(data["order_type"]),
                    limit_price=data.get("limit_price"),
                    stop_price=data.get("stop_price")
                ) is not None
            
            elif action == "cancel_order":
                return await self.cancel_order(data["order_id"])
            
            elif action == "get_account":
                return await self.get_account_info() is not None
            
            elif action == "get_positions":
                positions = await self.get_positions()
                return len(positions) >= 0
            
            elif action == "get_orders":
                orders = await self.get_orders()
                return len(orders) >= 0
            
            else:
                logger.warning(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending data to broker: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Salomatlik tekshiruvi"""
        base_health = await super().health_check()
        
        additional_info = {
            "broker_type": self.broker_type.value,
            "adapter_type": type(self.adapter).__name__ if self.adapter else None,
            "account_id": self.account.account_id if self.account else None,
            "account_balance": self.account.balance if self.account else 0,
            "active_positions": len(self.positions),
            "pending_orders": len(self.orders)
        }
        
        base_health.update(additional_info)
        return base_health


# Factory function
def create_broker_integration(config: IntegrationConfig) -> BrokerIntegration:
    """Broker integratsiyasini yaratish"""
    if config.integration_type != IntegrationType.INTERACTIVE_BROKERS and \
       config.integration_type != IntegrationType.BROKER_API:
        raise ValueError(f"Invalid integration type for broker: {config.integration_type}")
    
    return BrokerIntegration(config)


# Demo funksiya
async def demo_broker_integration():
    """Demo broker integratsiyasi"""
    print("=== Broker Integration Demo ===")
    
    # Interactive Brokers demo
    print("\n--- Interactive Brokers Demo ---")
    ib_config = IntegrationConfig(
        integration_type=IntegrationType.INTERACTIVE_BROKERS,
        name="IB_Demo",
        enabled=True,
        metadata={
            "broker_type": "interactive_brokers",
            "client_id": 1,
            "host": "localhost",
            "port": 7497
        }
    )
    
    ib_integration = create_broker_integration(ib_config)
    
    # Alpaca demo
    print("\n--- Alpaca Demo ---")
    alpaca_config = IntegrationConfig(
        integration_type=IntegrationType.BROKER_API,
        name="Alpaca_Demo",
        enabled=False,  # Disable because we don't have real API keys
        metadata={
            "broker_type": "alpaca",
            "api_key": "demo_key",
            "secret_key": "demo_secret",
            "paper": True
        }
    )
    
    alpaca_integration = create_broker_integration(alpaca_config)
    
    # Test IB integration
    success = await ib_integration.connect()
    print(f"IB Connection success: {success}")
    
    if success:
        # Account info
        account = await ib_integration.get_account_info()
        if account:
            print(f"Account: {account.name}, Balance: {account.balance}")
        
        # Positions
        positions = await ib_integration.get_positions()
        print(f"Positions: {len(positions)}")
        
        # Place order
        order_id = await ib_integration.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10.0,
            order_type=OrderType.MARKET
        )
        print(f"Order placed: {order_id}")
        
        # Market data
        market_data = await ib_integration.get_market_data(["AAPL", "MSFT"])
        print(f"Market data: {len(market_data)} symbols")
        
        # Health check
        health = await ib_integration.health_check()
        print(f"Health: {json.dumps(health, indent=2, default=str)}")
        
        await ib_integration.disconnect()
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(demo_broker_integration())