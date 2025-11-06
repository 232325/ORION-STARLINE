"""
Live Trading Dashboard Backend
================================

Real-time trading monitoring dashboard.
Position tracking, PnL monitoring, order management.

Features:
- Real-time position monitoring
- Live PnL tracking
- Order book visualization
- Trade execution monitoring
- Portfolio allocation
- Risk metrics real-time
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np


class PositionSide(Enum):
    """Position side enum"""
    LONG = "long"
    SHORT = "short"


class OrderStatus(Enum):
    """Order status enum"""
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderType(Enum):
    """Order type enum"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"


@dataclass
class Position:
    """Trading position"""
    position_id: str
    symbol: str
    side: PositionSide
    entry_price: float
    current_price: float
    size: float
    leverage: float
    
    # PnL
    unrealized_pnl: float
    unrealized_pnl_percent: float
    realized_pnl: float
    
    # Risk
    stop_loss: Optional[float]
    take_profit: Optional[float]
    liquidation_price: Optional[float]
    
    # Timing
    opened_at: datetime
    last_update: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'position_id': self.position_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'size': self.size,
            'leverage': self.leverage,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percent': self.unrealized_pnl_percent,
            'realized_pnl': self.realized_pnl,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'liquidation_price': self.liquidation_price,
            'opened_at': self.opened_at.isoformat(),
            'last_update': self.last_update.isoformat()
        }


@dataclass
class Order:
    """Trading order"""
    order_id: str
    symbol: str
    side: PositionSide
    order_type: OrderType
    status: OrderStatus
    
    price: float
    size: float
    filled_size: float
    remaining_size: float
    
    # Execution
    avg_fill_price: Optional[float]
    commission: float
    
    # Timing
    created_at: datetime
    updated_at: datetime
    filled_at: Optional[datetime]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'order_type': self.order_type.value,
            'status': self.status.value,
            'price': self.price,
            'size': self.size,
            'filled_size': self.filled_size,
            'remaining_size': self.remaining_size,
            'avg_fill_price': self.avg_fill_price,
            'commission': self.commission,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'filled_at': self.filled_at.isoformat() if self.filled_at else None
        }


@dataclass
class PortfolioSnapshot:
    """Portfolio snapshot at a point in time"""
    timestamp: datetime
    total_value: float
    cash_balance: float
    positions_value: float
    
    # PnL
    total_pnl: float
    total_pnl_percent: float
    daily_pnl: float
    daily_pnl_percent: float
    
    # Exposure
    long_exposure: float
    short_exposure: float
    net_exposure: float
    gross_exposure: float
    
    # Risk
    margin_used: float
    margin_available: float
    margin_ratio: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_value': self.total_value,
            'cash_balance': self.cash_balance,
            'positions_value': self.positions_value,
            'total_pnl': self.total_pnl,
            'total_pnl_percent': self.total_pnl_percent,
            'daily_pnl': self.daily_pnl,
            'daily_pnl_percent': self.daily_pnl_percent,
            'long_exposure': self.long_exposure,
            'short_exposure': self.short_exposure,
            'net_exposure': self.net_exposure,
            'gross_exposure': self.gross_exposure,
            'margin_used': self.margin_used,
            'margin_available': self.margin_available,
            'margin_ratio': self.margin_ratio
        }


class LiveTradingDashboard:
    """
    Live Trading Dashboard Backend
    
    Real-time monitoring of trading activity, positions, and portfolio.
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.cash_balance = initial_capital
        
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.portfolio_history: List[PortfolioSnapshot] = []
        
        # Price simulation
        self.prices: Dict[str, float] = {
            'BTC/USDT': 50000.0,
            'ETH/USDT': 3000.0,
            'SOL/USDT': 100.0
        }
        
        # Start price update task
        self._price_update_task = None
    
    async def start(self):
        """Start dashboard"""
        self._price_update_task = asyncio.create_task(self._update_prices())
    
    async def stop(self):
        """Stop dashboard"""
        if self._price_update_task:
            self._price_update_task.cancel()
    
    async def _update_prices(self):
        """Update prices continuously"""
        while True:
            try:
                # Simulate price changes
                for symbol in self.prices:
                    change = np.random.normal(0, 0.005)
                    self.prices[symbol] *= (1 + change)
                
                # Update positions
                await self._update_positions()
                
                # Record portfolio snapshot
                await self._record_portfolio_snapshot()
                
                await asyncio.sleep(1)  # Update every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error updating prices: {e}")
    
    async def _update_positions(self):
        """Update position prices and PnL"""
        for position in self.positions.values():
            # Update current price
            position.current_price = self.prices.get(position.symbol, position.current_price)
            position.last_update = datetime.now()
            
            # Calculate PnL
            if position.side == PositionSide.LONG:
                pnl = (position.current_price - position.entry_price) * position.size
            else:
                pnl = (position.entry_price - position.current_price) * position.size
            
            position.unrealized_pnl = pnl * position.leverage
            position.unrealized_pnl_percent = (
                pnl / (position.entry_price * position.size) * position.leverage
            )
            
            # Check stop loss / take profit
            if position.stop_loss:
                if position.side == PositionSide.LONG and position.current_price <= position.stop_loss:
                    await self.close_position(position.position_id, reason="Stop Loss")
                elif position.side == PositionSide.SHORT and position.current_price >= position.stop_loss:
                    await self.close_position(position.position_id, reason="Stop Loss")
            
            if position.take_profit:
                if position.side == PositionSide.LONG and position.current_price >= position.take_profit:
                    await self.close_position(position.position_id, reason="Take Profit")
                elif position.side == PositionSide.SHORT and position.current_price <= position.take_profit:
                    await self.close_position(position.position_id, reason="Take Profit")
    
    async def _record_portfolio_snapshot(self):
        """Record current portfolio state"""
        positions_value = sum(
            pos.size * pos.current_price for pos in self.positions.values()
        )
        
        total_value = self.cash_balance + positions_value
        
        # Calculate exposures
        long_exposure = sum(
            pos.size * pos.current_price * pos.leverage
            for pos in self.positions.values()
            if pos.side == PositionSide.LONG
        )
        
        short_exposure = sum(
            pos.size * pos.current_price * pos.leverage
            for pos in self.positions.values()
            if pos.side == PositionSide.SHORT
        )
        
        # Calculate PnL
        total_unrealized_pnl = sum(
            pos.unrealized_pnl for pos in self.positions.values()
        )
        
        total_realized_pnl = sum(
            pos.realized_pnl for pos in self.positions.values()
        )
        
        total_pnl = total_unrealized_pnl + total_realized_pnl
        
        # Daily PnL (last 24h)
        day_ago = datetime.now() - timedelta(days=1)
        recent_snapshots = [
            s for s in self.portfolio_history
            if s.timestamp >= day_ago
        ]
        
        if recent_snapshots:
            daily_pnl = total_value - recent_snapshots[0].total_value
            daily_pnl_percent = daily_pnl / recent_snapshots[0].total_value
        else:
            daily_pnl = 0
            daily_pnl_percent = 0
        
        # Margin
        margin_used = long_exposure + short_exposure
        margin_available = self.cash_balance
        margin_ratio = margin_used / (margin_used + margin_available) if (margin_used + margin_available) > 0 else 0
        
        snapshot = PortfolioSnapshot(
            timestamp=datetime.now(),
            total_value=total_value,
            cash_balance=self.cash_balance,
            positions_value=positions_value,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl / self.initial_capital,
            daily_pnl=daily_pnl,
            daily_pnl_percent=daily_pnl_percent,
            long_exposure=long_exposure,
            short_exposure=short_exposure,
            net_exposure=long_exposure - short_exposure,
            gross_exposure=long_exposure + short_exposure,
            margin_used=margin_used,
            margin_available=margin_available,
            margin_ratio=margin_ratio
        )
        
        self.portfolio_history.append(snapshot)
        
        # Keep only last 24 hours
        cutoff = datetime.now() - timedelta(days=1)
        self.portfolio_history = [
            s for s in self.portfolio_history
            if s.timestamp >= cutoff
        ]
    
    async def open_position(
        self,
        symbol: str,
        side: PositionSide,
        size: float,
        leverage: float = 1.0,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Position:
        """
        Open new position
        
        Args:
            symbol: Trading symbol
            side: Position side (long/short)
            size: Position size
            leverage: Leverage multiplier
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Position object
        """
        position_id = f"pos_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        entry_price = self.prices.get(symbol, 0)
        current_price = entry_price
        
        # Calculate liquidation price
        if leverage > 1:
            if side == PositionSide.LONG:
                liquidation_price = entry_price * (1 - 1/leverage)
            else:
                liquidation_price = entry_price * (1 + 1/leverage)
        else:
            liquidation_price = None
        
        position = Position(
            position_id=position_id,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            current_price=current_price,
            size=size,
            leverage=leverage,
            unrealized_pnl=0.0,
            unrealized_pnl_percent=0.0,
            realized_pnl=0.0,
            stop_loss=stop_loss,
            take_profit=take_profit,
            liquidation_price=liquidation_price,
            opened_at=datetime.now(),
            last_update=datetime.now()
        )
        
        self.positions[position_id] = position
        
        # Deduct margin from cash
        margin_required = size * entry_price / leverage
        self.cash_balance -= margin_required
        
        return position
    
    async def close_position(
        self,
        position_id: str,
        reason: str = "Manual Close"
    ) -> Dict[str, Any]:
        """
        Close position
        
        Args:
            position_id: Position ID
            reason: Close reason
            
        Returns:
            Close result
        """
        if position_id not in self.positions:
            return {'error': 'Position not found'}
        
        position = self.positions[position_id]
        
        # Calculate final PnL
        exit_price = position.current_price
        
        if position.side == PositionSide.LONG:
            pnl = (exit_price - position.entry_price) * position.size
        else:
            pnl = (position.entry_price - exit_price) * position.size
        
        pnl *= position.leverage
        
        # Return margin + PnL to cash
        margin = position.size * position.entry_price / position.leverage
        self.cash_balance += margin + pnl
        
        # Update realized PnL
        position.realized_pnl = pnl
        
        # Remove position
        del self.positions[position_id]
        
        return {
            'position_id': position_id,
            'symbol': position.symbol,
            'side': position.side.value,
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'size': position.size,
            'pnl': pnl,
            'pnl_percent': pnl / (position.entry_price * position.size) * position.leverage,
            'reason': reason,
            'closed_at': datetime.now().isoformat()
        }
    
    async def place_order(
        self,
        symbol: str,
        side: PositionSide,
        order_type: OrderType,
        size: float,
        price: Optional[float] = None
    ) -> Order:
        """
        Place trading order
        
        Args:
            symbol: Trading symbol
            side: Order side
            order_type: Order type
            size: Order size
            price: Limit price (for limit orders)
            
        Returns:
            Order object
        """
        order_id = f"ord_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if order_type == OrderType.MARKET:
            price = self.prices.get(symbol, 0)
        
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            status=OrderStatus.PENDING,
            price=price,
            size=size,
            filled_size=0.0,
            remaining_size=size,
            avg_fill_price=None,
            commission=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            filled_at=None
        )
        
        self.orders[order_id] = order
        
        # Auto-fill market orders
        if order_type == OrderType.MARKET:
            await self._fill_order(order_id)
        
        return order
    
    async def _fill_order(self, order_id: str):
        """Fill order"""
        order = self.orders.get(order_id)
        if not order:
            return
        
        order.status = OrderStatus.FILLED
        order.filled_size = order.size
        order.remaining_size = 0.0
        order.avg_fill_price = order.price
        order.commission = order.size * order.price * 0.001  # 0.1% commission
        order.filled_at = datetime.now()
        order.updated_at = datetime.now()
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel order"""
        if order_id not in self.orders:
            return {'error': 'Order not found'}
        
        order = self.orders[order_id]
        
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            return {'error': f'Cannot cancel order in status {order.status.value}'}
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        
        return {
            'order_id': order_id,
            'status': 'cancelled',
            'cancelled_at': datetime.now().isoformat()
        }
    
    def get_portfolio_snapshot(self) -> PortfolioSnapshot:
        """Get current portfolio snapshot"""
        if self.portfolio_history:
            return self.portfolio_history[-1]
        
        # Create initial snapshot
        return PortfolioSnapshot(
            timestamp=datetime.now(),
            total_value=self.initial_capital,
            cash_balance=self.cash_balance,
            positions_value=0.0,
            total_pnl=0.0,
            total_pnl_percent=0.0,
            daily_pnl=0.0,
            daily_pnl_percent=0.0,
            long_exposure=0.0,
            short_exposure=0.0,
            net_exposure=0.0,
            gross_exposure=0.0,
            margin_used=0.0,
            margin_available=self.cash_balance,
            margin_ratio=0.0
        )
    
    def get_equity_curve(self, period: str = "24h") -> List[Dict[str, Any]]:
        """Get equity curve data"""
        if period == "24h":
            cutoff = datetime.now() - timedelta(days=1)
        elif period == "7d":
            cutoff = datetime.now() - timedelta(days=7)
        elif period == "30d":
            cutoff = datetime.now() - timedelta(days=30)
        else:
            cutoff = datetime.now() - timedelta(days=1)
        
        snapshots = [
            s for s in self.portfolio_history
            if s.timestamp >= cutoff
        ]
        
        return [
            {
                'timestamp': s.timestamp.isoformat(),
                'total_value': s.total_value,
                'pnl': s.total_pnl,
                'pnl_percent': s.total_pnl_percent
            }
            for s in snapshots
        ]
    
    def get_positions(self) -> List[Position]:
        """Get all open positions"""
        return list(self.positions.values())
    
    def get_orders(
        self,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Get orders with optional status filter"""
        orders = list(self.orders.values())
        
        if status:
            orders = [o for o in orders if o.status == status]
        
        # Sort by creation date descending
        orders.sort(key=lambda o: o.created_at, reverse=True)
        
        return orders
    
    def get_position_allocation(self) -> Dict[str, float]:
        """Get position allocation by symbol"""
        total_value = sum(
            pos.size * pos.current_price
            for pos in self.positions.values()
        )
        
        if total_value == 0:
            return {}
        
        allocation = {}
        for position in self.positions.values():
            position_value = position.size * position.current_price
            allocation[position.symbol] = position_value / total_value
        
        return allocation
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics"""
        snapshot = self.get_portfolio_snapshot()
        
        # Calculate VAR (Value at Risk)
        if len(self.portfolio_history) > 100:
            returns = [
                (self.portfolio_history[i].total_value - self.portfolio_history[i-1].total_value) 
                / self.portfolio_history[i-1].total_value
                for i in range(1, len(self.portfolio_history))
            ]
            
            var_95 = np.percentile(returns, 5) * snapshot.total_value
            var_99 = np.percentile(returns, 1) * snapshot.total_value
        else:
            var_95 = 0
            var_99 = 0
        
        return {
            'margin_ratio': snapshot.margin_ratio,
            'leverage': snapshot.gross_exposure / snapshot.total_value if snapshot.total_value > 0 else 0,
            'net_exposure_ratio': snapshot.net_exposure / snapshot.total_value if snapshot.total_value > 0 else 0,
            'var_95': var_95,
            'var_99': var_99,
            'num_positions': len(self.positions),
            'largest_position': max(
                [pos.size * pos.current_price for pos in self.positions.values()],
                default=0
            )
        }


# Global instance
live_dashboard = LiveTradingDashboard()


async def test_live_dashboard():
    """Test live trading dashboard"""
    dashboard = LiveTradingDashboard(initial_capital=10000.0)
    
    await dashboard.start()
    
    # Open some positions
    pos1 = await dashboard.open_position(
        symbol="BTC/USDT",
        side=PositionSide.LONG,
        size=0.1,
        leverage=2.0,
        stop_loss=45000.0,
        take_profit=55000.0
    )
    
    print(f"Opened position: {pos1.position_id}")
    print(f"Entry price: {pos1.entry_price}")
    
    # Wait for price updates
    await asyncio.sleep(5)
    
    # Get portfolio snapshot
    snapshot = dashboard.get_portfolio_snapshot()
    print(f"\nPortfolio Value: ${snapshot.total_value:.2f}")
    print(f"Total PnL: ${snapshot.total_pnl:.2f} ({snapshot.total_pnl_percent:.2%})")
    
    # Close position
    result = await dashboard.close_position(pos1.position_id)
    print(f"\nClosed position: {result['pnl']:.2f}")
    
    await dashboard.stop()


if __name__ == "__main__":
    asyncio.run(test_live_dashboard())
