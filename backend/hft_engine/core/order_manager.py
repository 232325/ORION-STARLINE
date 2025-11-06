"""
Order Manager System
===================

High-performance order management system for HFT operations
Handles order routing, execution, and management with microsecond-level latency
"""

import asyncio
import time
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from threading import Lock

class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILL = "partial_fill"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class TimeInForce(Enum):
    GTC = "gtc"  # Good Till Cancelled
    IOC = "ioc"  # Immediate Or Cancel
    FOK = "fok"  # Fill Or Kill
    DAY = "day"

@dataclass
class OrderRequest:
    """Order request structure"""
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: int
    price: Optional[float] = None
    order_type: str = 'limit'
    time_in_force: str = 'gtc'
    client_order_id: Optional[str] = None
    
    def __post_init__(self):
        if self.client_order_id is None:
            self.client_order_id = str(uuid.uuid4())

@dataclass
class OrderResponse:
    """Order response structure"""
    order_id: str
    client_order_id: str
    symbol: str
    status: str
    side: str
    quantity: int
    filled_quantity: int
    price: Optional[float]
    avg_fill_price: Optional[float]
    timestamp: float
    rejection_reason: Optional[str] = None

@dataclass
class Trade:
    """Trade execution record"""
    trade_id: str
    order_id: str
    symbol: str
    side: str
    price: float
    quantity: int
    timestamp: float
    commission: float = 0.0

class OrderManager:
    """
    High-Performance Order Manager
    
    Handles order routing and execution with minimal latency
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Order storage
        self.pending_orders: Dict[str, OrderRequest] = {}
        self.active_orders: Dict[str, OrderResponse] = {}
        self.completed_orders: Dict[str, OrderResponse] = {}
        self.trades: List[Trade] = []
        
        # Performance tracking
        self.order_count = 0
        self.fill_count = 0
        self.rejection_count = 0
        self.last_order_time = 0.0
        self.execution_latencies = []
        
        # Exchange connections (simulated)
        self.exchanges = self._initialize_exchanges()
        
        # Thread safety
        self.lock = Lock()
        
        self.logger = logging.getLogger(__name__)
        
    def _initialize_exchanges(self) -> Dict[str, Dict]:
        """Initialize exchange connections"""
        return {
            'NASDAQ': {
                'name': 'NASDAQ',
                'url': 'wss://api.nasdaq.com/orders',
                'status': 'connected',
                'latency_us': 50,
                'throughput': 10000
            },
            'NYSE': {
                'name': 'NYSE', 
                'url': 'wss://api.nyse.com/orders',
                'status': 'connected',
                'latency_us': 55,
                'throughput': 10000
            },
            'FOREX': {
                'name': 'FOREX',
                'url': 'wss://api.forex.com/orders',
                'status': 'connected',
                'latency_us': 30,
                'throughput': 20000
            },
            'CRYPTO': {
                'name': 'CRYPTO',
                'url': 'wss://api.crypto.com/orders',
                'status': 'connected',
                'latency_us': 40,
                'throughput': 15000
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize order manager"""
        try:
            self.logger.info("Initializing Order Manager...")
            
            # Initialize exchange connections
            for exchange in self.exchanges.values():
                # Simulate connection establishment
                await asyncio.sleep(0.001)  # 1ms simulated connection time
                
            self.logger.info("Order Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Order Manager: {e}")
            return False
    
    async def start(self):
        """Start order manager"""
        self.logger.info("Starting Order Manager...")
        # Order manager is typically always ready for operations
        self.logger.info("Order Manager started")
    
    def _get_exchange_for_symbol(self, symbol: str) -> str:
        """Determine exchange for symbol"""
        stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
        forex_symbols = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF']
        crypto_symbols = ['BTC/USD', 'ETH/USD']
        
        if symbol in stock_symbols:
            return 'NASDAQ' if symbol in ['AAPL', 'MSFT'] else 'NYSE'
        elif symbol in forex_symbols:
            return 'FOREX'
        elif symbol in crypto_symbols:
            return 'CRYPTO'
        else:
            return 'NASDAQ'  # Default
    
    async def execute_order(self, symbol: str, side: str, quantity: int, 
                          price: Optional[float] = None, order_type: str = 'limit') -> OrderResponse:
        """Execute trading order with minimal latency"""
        start_time = time.perf_counter()
        
        try:
            # Generate order request
            order_request = OrderRequest(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                order_type=order_type
            )
            
            # Validate order
            validation_result = self._validate_order(order_request)
            if not validation_result['valid']:
                return OrderResponse(
                    order_id=str(uuid.uuid4()),
                    client_order_id=order_request.client_order_id,
                    symbol=symbol,
                    status='rejected',
                    side=side,
                    quantity=quantity,
                    filled_quantity=0,
                    price=price,
                    avg_fill_price=None,
                    timestamp=time.time(),
                    rejection_reason=validation_result['reason']
                )
            
            # Route order to exchange
            exchange = self._get_exchange_for_symbol(symbol)
            order_id = await self._route_order(order_request, exchange)
            
            if not order_id:
                # Order rejected by exchange
                rejection_reason = f"Exchange {exchange} rejected order"
                return OrderResponse(
                    order_id="",
                    client_order_id=order_request.client_order_id,
                    symbol=symbol,
                    status='rejected',
                    side=side,
                    quantity=quantity,
                    filled_quantity=0,
                    price=price,
                    avg_fill_price=None,
                    timestamp=time.time(),
                    rejection_reason=rejection_reason
                )
            
            # Create order response
            order_response = OrderResponse(
                order_id=order_id,
                client_order_id=order_request.client_order_id,
                symbol=symbol,
                status='submitted',
                side=side,
                quantity=quantity,
                filled_quantity=0,
                price=price,
                avg_fill_price=None,
                timestamp=time.time()
            )
            
            # Track order
            with self.lock:
                self.pending_orders[order_id] = order_request
                self.active_orders[order_id] = order_response
                self.order_count += 1
                self.last_order_time = time.time()
            
            # Simulate order processing and potential fills
            asyncio.create_task(self._process_order_fills(order_response))
            
            # Record latency
            execution_time = time.perf_counter() - start_time
            self._record_latency(execution_time)
            
            return order_response
            
        except Exception as e:
            self.logger.error(f"Error executing order: {e}")
            return OrderResponse(
                order_id="",
                client_order_id="",
                symbol=symbol,
                status='rejected',
                side=side,
                quantity=quantity,
                filled_quantity=0,
                price=price,
                avg_fill_price=None,
                timestamp=time.time(),
                rejection_reason=str(e)
            )
    
    def _validate_order(self, order: OrderRequest) -> Dict[str, Any]:
        """Validate order before submission"""
        
        # Check symbol
        if not order.symbol:
            return {'valid': False, 'reason': 'Invalid symbol'}
        
        # Check side
        if order.side not in ['buy', 'sell']:
            return {'valid': False, 'reason': 'Invalid side'}
        
        # Check quantity
        if order.quantity <= 0:
            return {'valid': False, 'reason': 'Invalid quantity'}
        
        # Check price for limit orders
        if order.order_type == 'limit' and order.price is None:
            return {'valid': False, 'reason': 'Limit order requires price'}
        
        # Check positive price
        if order.price is not None and order.price <= 0:
            return {'valid': False, 'reason': 'Invalid price'}
        
        return {'valid': True, 'reason': None}
    
    async def _route_order(self, order: OrderRequest, exchange: str) -> Optional[str]:
        """Route order to exchange"""
        try:
            exchange_info = self.exchanges[exchange]
            
            if exchange_info['status'] != 'connected':
                return None
            
            # Simulate exchange order submission
            # In real system, this would send order via FIX protocol or proprietary API
            await asyncio.sleep(0.00001)  # 10 microseconds simulated latency
            
            # Generate order ID
            order_id = f"{exchange}_{int(time.time() * 1_000_000)}"
            
            return order_id
            
        except Exception as e:
            self.logger.error(f"Error routing order to {exchange}: {e}")
            return None
    
    async def _process_order_fills(self, order_response: OrderResponse):
        """Process order fills (simulated)"""
        try:
            # Simulate order execution
            await asyncio.sleep(0.001)  # 1ms delay before processing
            
            with self.lock:
                if order_response.order_id in self.active_orders:
                    current_order = self.active_orders[order_response.order_id]
                    
                    # Simulate partial or full fill
                    import random
                    
                    if random.random() < 0.9:  # 90% fill rate
                        if random.random() < 0.3:  # 30% partial fill
                            fill_quantity = current_order.quantity // 2
                            current_order.status = 'partial_fill'
                            current_order.filled_quantity = fill_quantity
                            current_order.avg_fill_price = current_order.price
                        else:  # Full fill
                            fill_quantity = current_order.quantity
                            current_order.status = 'filled'
                            current_order.filled_quantity = fill_quantity
                            current_order.avg_fill_price = current_order.price
                        
                        # Create trade record
                        trade = Trade(
                            trade_id=str(uuid.uuid4()),
                            order_id=order_response.order_id,
                            symbol=current_order.symbol,
                            side=current_order.side,
                            price=current_order.price,
                            quantity=fill_quantity,
                            timestamp=time.time()
                        )
                        
                        self.trades.append(trade)
                        self.fill_count += 1
                        
                        # If fully filled, move to completed
                        if current_order.status == 'filled':
                            self.completed_orders[order_response.order_id] = current_order
                            del self.active_orders[order_response.order_id]
                    else:
                        # Order rejected
                        current_order.status = 'rejected'
                        current_order.rejection_reason = 'Market conditions'
                        self.rejection_count += 1
                        self.completed_orders[order_response.order_id] = current_order
                        del self.active_orders[order_response.order_id]
        
        except Exception as e:
            self.logger.error(f"Error processing order fills: {e}")
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel existing order"""
        try:
            with self.lock:
                if order_id not in self.active_orders:
                    return False
                
                current_order = self.active_orders[order_id]
                
                # Simulate cancel request
                await asyncio.sleep(0.00001)  # 10 microseconds
                
                if current_order.status in ['filled', 'cancelled', 'rejected']:
                    return False
                
                # Update order status
                current_order.status = 'cancelled'
                self.completed_orders[order_id] = current_order
                del self.active_orders[order_id]
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    async def modify_order(self, order_id: str, new_quantity: Optional[int] = None, 
                          new_price: Optional[float] = None) -> bool:
        """Modify existing order"""
        try:
            with self.lock:
                if order_id not in self.active_orders:
                    return False
                
                current_order = self.active_orders[order_id]
                
                if current_order.status in ['filled', 'cancelled', 'rejected']:
                    return False
                
                # Simulate modify request
                await asyncio.sleep(0.00001)  # 10 microseconds
                
                if new_quantity is not None:
                    current_order.quantity = new_quantity
                
                if new_price is not None:
                    current_order.price = new_price
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error modifying order {order_id}: {e}")
            return False
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get order status"""
        with self.lock:
            # Check active orders
            if order_id in self.active_orders:
                return asdict(self.active_orders[order_id])
            
            # Check completed orders
            if order_id in self.completed_orders:
                return asdict(self.completed_orders[order_id])
            
            return None
    
    def get_all_orders(self, status: Optional[str] = None) -> List[Dict]:
        """Get all orders"""
        with self.lock:
            all_orders = []
            
            # Add active orders
            for order in self.active_orders.values():
                order_dict = asdict(order)
                if status is None or order.status == status:
                    all_orders.append(order_dict)
            
            # Add completed orders
            for order in self.completed_orders.values():
                order_dict = asdict(order)
                if status is None or order.status == status:
                    all_orders.append(order_dict)
            
            return all_orders
    
    def get_recent_trades(self, limit: int = 100) -> List[Dict]:
        """Get recent trades"""
        with self.lock:
            recent_trades = self.trades[-limit:] if self.trades else []
            return [asdict(trade) for trade in recent_trades]
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary"""
        with self.lock:
            position_summary = {}
            
            # Calculate positions from trades
            for trade in self.trades:
                symbol = trade.symbol
                if symbol not in position_summary:
                    position_summary[symbol] = {
                        'quantity': 0,
                        'avg_price': 0,
                        'total_cost': 0
                    }
                
                if trade.side == 'buy':
                    position_summary[symbol]['total_cost'] += trade.price * trade.quantity
                    position_summary[symbol]['quantity'] += trade.quantity
                else:
                    position_summary[symbol]['total_cost'] -= trade.price * trade.quantity
                    position_summary[symbol]['quantity'] -= trade.quantity
                
                if position_summary[symbol]['quantity'] != 0:
                    position_summary[symbol]['avg_price'] = (
                        position_summary[symbol]['total_cost'] / position_summary[symbol]['quantity']
                    )
            
            return {
                'total_orders': self.order_count,
                'filled_orders': self.fill_count,
                'rejected_orders': self.rejection_count,
                'active_orders': len(self.active_orders),
                'total_trades': len(self.trades),
                'positions': position_summary
            }
    
    def _record_latency(self, execution_time: float):
        """Record execution latency"""
        latency_us = execution_time * 1_000_000  # Convert to microseconds
        
        if len(self.execution_latencies) < 1000:
            self.execution_latencies.append(latency_us)
        else:
            self.execution_latencies.pop(0)
            self.execution_latencies.append(latency_us)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        with self.lock:
            if self.execution_latencies:
                avg_latency = sum(self.execution_latencies) / len(self.execution_latencies)
                max_latency = max(self.execution_latencies)
                min_latency = min(self.execution_latencies)
            else:
                avg_latency = max_latency = min_latency = 0
            
            return {
                'total_orders': self.order_count,
                'fill_rate': (self.fill_count / self.order_count * 100) if self.order_count > 0 else 0,
                'rejection_rate': (self.rejection_count / self.order_count * 100) if self.order_count > 0 else 0,
                'avg_latency_us': avg_latency,
                'max_latency_us': max_latency,
                'min_latency_us': min_latency,
                'active_orders': len(self.active_orders),
                'completed_orders': len(self.completed_orders),
                'total_trades': len(self.trades)
            }
    
    async def shutdown(self):
        """Shutdown order manager"""
        self.logger.info("Shutting down Order Manager...")
        
        # Cancel all active orders
        active_order_ids = list(self.active_orders.keys())
        for order_id in active_order_ids:
            await self.cancel_order(order_id)
        
        self.logger.info("Order Manager shutdown complete")