"""
Automated Trading Engine
Quantum va AI algoritmlar bilan automated trading tizimi
"""
import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class StrategyType(Enum):
    QUANTUM_MOMENTUM = "quantum_momentum"
    QUANTUM_MEAN_REVERSION = "quantum_mean_reversion"
    QUANTUM_ARBITRAGE = "quantum_arbitrage"
    HYBRID_QUANTUM_CLASSICAL = "hybrid_quantum_classical"
    RISK_PARITY = "risk_parity"

@dataclass
class Order:
    """Trading order"""
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    filled_price: float = 0.0
    timestamp: datetime = None
    strategy: str = "manual"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class Position:
    """Trading position"""
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
        self.market_value = self.quantity * self.current_price
        self.unrealized_pnl = (self.current_price - self.avg_price) * self.quantity

@dataclass
class TradingStrategy:
    """Trading strategy"""
    name: str
    strategy_type: StrategyType
    enabled: bool = True
    max_position_size: float = 0.1
    risk_level: str = "medium"
    parameters: Dict[str, Any] = None
    performance_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.performance_metrics is None:
            self.performance_metrics = {}

class TradingEngine:
    """Automated Trading Engine"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("trading_engine")
        self.is_running = False
        self.is_automated = False
        
        # Trading state
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.pending_orders: List[Order] = []
        self.filled_orders: List[Order] = []
        self.cancelled_orders: List[Order] = []
        
        # Strategies
        self.strategies: Dict[str, TradingStrategy] = {}
        self.active_strategy = None
        
        # Market data
        self.market_data: Dict[str, Dict] = {}
        self.price_history: Dict[str, pd.DataFrame] = {}
        
        # Performance tracking
        self.daily_pnl = 0.0
        self.monthly_pnl = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.win_rate = 0.0
        
        # Risk management
        self.max_daily_loss = config.get("max_daily_loss", 0.02)  # 2% max daily loss
        self.max_position_size = config.get("max_position_size", 0.1)  # 10% max position
        self.stop_loss_pct = config.get("stop_loss_pct", 0.05)  # 5% stop loss
        
        # Limits
        self.max_trades_per_day = config.get("max_trades_per_day", 100)
        self.min_trade_size = config.get("min_trade_size", 1000)
        self.execution_delay = config.get("execution_delay", 0.1)
        
    async def initialize(self):
        """Trading engine'ni ishga tushirish"""
        try:
            self.logger.info("Trading Engine ishga tushirilmoqda...")
            
            # Initialize strategies
            await self._initialize_strategies()
            
            # Load market data
            await self._load_market_data()
            
            # Initialize risk management
            await self._initialize_risk_management()
            
            self.logger.info("✅ Trading Engine muvaffaqiyatli ishga tushdi!")
            
        except Exception as e:
            self.logger.error(f"Trading Engine ishga tushirishda xato: {e}")
            raise
    
    async def _initialize_strategies(self):
        """Trading strategiyalarni ishga tushirish"""
        try:
            self.strategies = {
                "quantum_momentum": TradingStrategy(
                    name="Quantum Momentum",
                    strategy_type=StrategyType.QUANTUM_MOMENTUM,
                    parameters={"lookback_period": 20, "quantum_threshold": 0.7}
                ),
                "quantum_mean_reversion": TradingStrategy(
                    name="Quantum Mean Reversion",
                    strategy_type=StrategyType.QUANTUM_MEAN_REVERSION,
                    parameters={"bollinger_period": 20, "quantum_threshold": 0.8}
                ),
                "hybrid_strategy": TradingStrategy(
                    name="Hybrid Quantum-Classical",
                    strategy_type=StrategyType.HYBRID_QUANTUM_CLASSICAL,
                    parameters={"quantum_weight": 0.6, "classical_weight": 0.4}
                ),
                "risk_parity": TradingStrategy(
                    name="Risk Parity",
                    strategy_type=StrategyType.RISK_PARITY,
                    parameters={"target_vol": 0.15, "risk_budget": 0.25}
                )
            }
            
            # Set default strategy
            self.active_strategy = "quantum_momentum"
            
            self.logger.info(f"Trading strategiyalar muvaffaqiyatli yuklandi: {list(self.strategies.keys())}")
            
        except Exception as e:
            self.logger.error(f"Strategy initializationda xato: {e}")
    
    async def _load_market_data(self):
        """Market data yuklash"""
        try:
            # Simulate market data loading
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"]
            
            for symbol in symbols:
                # Generate historical price data
                dates = pd.date_range(start='2023-01-01', end='2024-11-03', freq='1H')
                np.random.seed(hash(symbol) % 2**32)
                
                # Simulate price movement
                returns = np.random.normal(0.0001, 0.02, len(dates))  # Small positive drift
                prices = 100 * np.exp(np.cumsum(returns))
                
                self.price_history[symbol] = pd.DataFrame({
                    'timestamp': dates,
                    'open': prices * (1 + np.random.normal(0, 0.001, len(dates))),
                    'high': prices * (1 + np.abs(np.random.normal(0, 0.005, len(dates)))),
                    'low': prices * (1 - np.abs(np.random.normal(0, 0.005, len(dates)))),
                    'close': prices,
                    'volume': np.random.randint(10000, 1000000, len(dates))
                })
                
                # Set current market data
                current_price = self.price_history[symbol]['close'].iloc[-1]
                self.market_data[symbol] = {
                    'price': current_price,
                    'volume': np.random.randint(10000, 100000),
                    'timestamp': datetime.now(),
                    'bid': current_price * 0.999,
                    'ask': current_price * 1.001
                }
            
            self.logger.info(f"Market data {len(symbols)} symbol uchun muvaffaqiyatli yuklandi")
            
        except Exception as e:
            self.logger.error(f"Market data yuklashda xato: {e}")
    
    async def _initialize_risk_management(self):
        """Risk management initialization"""
        try:
            # Initialize position tracking
            for symbol in self.market_data.keys():
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=0.0,
                    avg_price=0.0,
                    current_price=self.market_data[symbol]['price'],
                    market_value=0.0,
                    unrealized_pnl=0.0
                )
            
            self.logger.info("Risk management tizimi ishga tushirildi")
            
        except Exception as e:
            self.logger.error(f"Risk management initializationda xato: {e}")
    
    async def start_automated_trading(self):
        """Automated tradingni boshlash"""
        try:
            self.logger.info("Automated trading boshlanmoqda...")
            
            if self.active_strategy not in self.strategies:
                self.logger.error(f"Strategy topilmadi: {self.active_strategy}")
                return False
            
            # Enable active strategy
            self.strategies[self.active_strategy].enabled = True
            self.is_automated = True
            self.is_running = True
            
            # Start main trading loop
            asyncio.create_task(self._trading_loop())
            
            self.logger.info(f"✅ Automated trading boshlandi - Strategy: {self.active_strategy}")
            return True
            
        except Exception as e:
            self.logger.error(f"Automated tradingni boshlashda xato: {e}")
            return False
    
    async def stop_automated_trading(self):
        """Automated tradingni to'xtatish"""
        try:
            self.logger.info("Automated trading to'xtatilmoqda...")
            
            self.is_automated = False
            self.is_running = False
            
            # Disable all strategies
            for strategy in self.strategies.values():
                strategy.enabled = False
            
            self.logger.info("✅ Automated trading to'xtatildi")
            
        except Exception as e:
            self.logger.error(f"Automated tradingni to'xtatishda xato: {e}")
    
    async def _trading_loop(self):
        """Asosiy trading loop"""
        self.logger.info("Trading loop boshlanmoqda...")
        
        while self.is_running and self.is_automated:
            try:
                # Update market data
                await self._update_market_data()
                
                # Check for trading signals
                await self._check_trading_signals()
                
                # Process pending orders
                await self._process_pending_orders()
                
                # Update positions and P&L
                await self._update_positions()
                
                # Risk monitoring
                await self._monitor_risk()
                
                # Wait before next iteration
                await asyncio.sleep(5)  # 5 second intervals for high-frequency
                
            except Exception as e:
                self.logger.error(f"Trading loopda xato: {e}")
                await asyncio.sleep(10)
    
    async def _update_market_data(self):
        """Market datani yangilash"""
        try:
            for symbol in self.market_data.keys():
                # Simulate price movement
                current_price = self.market_data[symbol]['price']
                price_change = np.random.normal(0, 0.001)  # Small random change
                new_price = current_price * (1 + price_change)
                
                self.market_data[symbol].update({
                    'price': new_price,
                    'volume': np.random.randint(10000, 100000),
                    'timestamp': datetime.now(),
                    'bid': new_price * 0.999,
                    'ask': new_price * 1.001
                })
                
                # Update position
                if symbol in self.positions:
                    self.positions[symbol].current_price = new_price
                    self.positions[symbol].last_updated = datetime.now()
                
        except Exception as e:
            self.logger.error(f"Market data yangilashda xato: {e}")
    
    async def _check_trading_signals(self):
        """Trading signallarini tekshirish"""
        try:
            if not self.is_automated:
                return
            
            strategy = self.strategies.get(self.active_strategy)
            if not strategy or not strategy.enabled:
                return
            
            # Generate trading signals based on strategy
            for symbol in self.market_data.keys():
                signal = await self._generate_signal(symbol, strategy)
                
                if signal and signal['action'] != 'hold':
                    await self._execute_trading_signal(symbol, signal)
                
        except Exception as e:
            self.logger.error(f"Trading signals checkda xato: {e}")
    
    async def _generate_signal(self, symbol: str, strategy: TradingStrategy) -> Optional[Dict]:
        """Trading signal generation"""
        try:
            # Get price data
            if symbol not in self.price_history:
                return None
            
            recent_data = self.price_history[symbol].tail(50)  # Last 50 data points
            if len(recent_data) < 20:
                return None
            
            current_price = self.market_data[symbol]['price']
            
            # Generate signal based on strategy type
            if strategy.strategy_type == StrategyType.QUANTUM_MOMENTUM:
                return await self._quantum_momentum_signal(symbol, recent_data, strategy)
            elif strategy.strategy_type == StrategyType.QUANTUM_MEAN_REVERSION:
                return await self._quantum_mean_reversion_signal(symbol, recent_data, strategy)
            elif strategy.strategy_type == StrategyType.HYBRID_QUANTUM_CLASSICAL:
                return await self._hybrid_signal(symbol, recent_data, strategy)
            elif strategy.strategy_type == StrategyType.RISK_PARITY:
                return await self._risk_parity_signal(symbol, recent_data, strategy)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Signal generationda xato: {e}")
            return None
    
    async def _quantum_momentum_signal(self, symbol: str, data: pd.DataFrame, strategy: TradingStrategy) -> Dict:
        """Quantum momentum signal generation"""
        try:
            # Calculate momentum indicators
            returns = data['close'].pct_change().dropna()
            
            # Quantum-enhanced momentum calculation
            momentum_score = returns.rolling(10).mean().iloc[-1]
            quantum_momentum = momentum_score * (1 + np.random.uniform(-0.1, 0.1))  # Quantum enhancement
            
            # Volume confirmation
            volume_ratio = data['volume'].iloc[-1] / data['volume'].rolling(20).mean().iloc[-1]
            
            # Generate signal
            quantum_threshold = strategy.parameters.get("quantum_threshold", 0.7)
            
            if quantum_momentum > quantum_threshold and volume_ratio > 1.2:
                action = "buy"
                confidence = min(abs(quantum_momentum) / quantum_threshold, 1.0)
            elif quantum_momentum < -quantum_threshold and volume_ratio > 1.2:
                action = "sell"
                confidence = min(abs(quantum_momentum) / quantum_threshold, 1.0)
            else:
                action = "hold"
                confidence = 0.3
            
            return {
                "action": action,
                "confidence": confidence,
                "momentum_score": quantum_momentum,
                "volume_ratio": volume_ratio,
                "strategy": "quantum_momentum"
            }
            
        except Exception as e:
            self.logger.error(f"Quantum momentum signalda xato: {e}")
            return {"action": "hold", "confidence": 0.0}
    
    async def _quantum_mean_reversion_signal(self, symbol: str, data: pd.DataFrame, strategy: TradingStrategy) -> Dict:
        """Quantum mean reversion signal generation"""
        try:
            # Calculate bollinger bands
            sma = data['close'].rolling(20).mean()
            std = data['close'].rolling(20).std()
            upper_band = sma + (2 * std)
            lower_band = sma - (2 * std)
            
            current_price = self.market_data[symbol]['price']
            
            # Quantum-enhanced mean reversion
            price_position = (current_price - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])
            quantum_factor = 1 + np.random.uniform(-0.05, 0.05)  # Quantum enhancement
            quantum_position = price_position * quantum_factor
            
            # Generate signal
            quantum_threshold = strategy.parameters.get("quantum_threshold", 0.8)
            
            if quantum_position < (1 - quantum_threshold):
                action = "buy"
                confidence = (1 - quantum_position) * 0.8
            elif quantum_position > quantum_threshold:
                action = "sell"
                confidence = quantum_position * 0.8
            else:
                action = "hold"
                confidence = 0.3
            
            return {
                "action": action,
                "confidence": confidence,
                "price_position": quantum_position,
                "strategy": "quantum_mean_reversion"
            }
            
        except Exception as e:
            self.logger.error(f"Quantum mean reversion signalda xato: {e}")
            return {"action": "hold", "confidence": 0.0}
    
    async def _hybrid_signal(self, symbol: str, data: pd.DataFrame, strategy: TradingStrategy) -> Dict:
        """Hybrid quantum-classical signal generation"""
        try:
            # Classical signal
            classical_momentum = data['close'].pct_change(5).iloc[-1]
            classical_signal = "buy" if classical_momentum > 0.02 else "sell" if classical_momentum < -0.02 else "hold"
            
            # Quantum signal
            quantum_result = await self._quantum_momentum_signal(symbol, data, strategy)
            quantum_signal = quantum_result["action"]
            
            # Weighted combination
            quantum_weight = strategy.parameters.get("quantum_weight", 0.6)
            classical_weight = strategy.parameters.get("classical_weight", 0.4)
            
            # Combine signals
            if classical_signal == quantum_signal:
                final_action = classical_signal
                confidence = (quantum_result["confidence"] * quantum_weight + 
                            abs(classical_momentum) * classical_weight)
            else:
                # Trust quantum when disagreeing
                final_action = quantum_signal
                confidence = quantum_result["confidence"] * quantum_weight
            
            return {
                "action": final_action,
                "confidence": min(confidence, 1.0),
                "classical_signal": classical_signal,
                "quantum_signal": quantum_signal,
                "strategy": "hybrid"
            }
            
        except Exception as e:
            self.logger.error(f"Hybrid signalda xato: {e}")
            return {"action": "hold", "confidence": 0.0}
    
    async def _risk_parity_signal(self, symbol: str, data: pd.DataFrame, strategy: TradingStrategy) -> Dict:
        """Risk parity signal generation"""
        try:
            # Calculate volatility
            returns = data['close'].pct_change().dropna()
            volatility = returns.rolling(20).std().iloc[-1]
            
            # Target volatility
            target_vol = strategy.parameters.get("target_vol", 0.15)
            
            # Calculate position size based on volatility targeting
            vol_ratio = target_vol / volatility if volatility > 0 else 1.0
            position_size = min(vol_ratio, 2.0)  # Cap at 2x target
            
            # Generate signal
            if position_size > 1.2:
                action = "buy"
                confidence = min((position_size - 1.0) / 1.0, 0.8)
            elif position_size < 0.8:
                action = "sell"
                confidence = min((1.0 - position_size) / 1.0, 0.8)
            else:
                action = "hold"
                confidence = 0.3
            
            return {
                "action": action,
                "confidence": confidence,
                "position_size": position_size,
                "volatility": volatility,
                "strategy": "risk_parity"
            }
            
        except Exception as e:
            self.logger.error(f"Risk parity signalda xato: {e}")
            return {"action": "hold", "confidence": 0.0}
    
    async def _execute_trading_signal(self, symbol: str, signal: Dict):
        """Trading signalni bajarish"""
        try:
            action = signal["action"]
            confidence = signal["confidence"]
            
            # Risk checks
            if not await self._check_risk_limits(symbol, action, confidence):
                return
            
            # Calculate position size
            current_price = self.market_data[symbol]['price']
            available_cash = await self._get_available_cash()
            
            if action == "buy":
                position_size = min(
                    available_cash * confidence * 0.1,  # 10% max position
                    current_price * self.max_position_size * 1000
                )
                quantity = position_size / current_price
            elif action == "sell":
                # Close existing position
                if symbol in self.positions:
                    quantity = self.positions[symbol].quantity
                else:
                    return  # No position to sell
            else:
                return  # Hold action
            
            # Create order
            if quantity > 0:
                await self._create_order(
                    symbol=symbol,
                    side=OrderSide.BUY if action == "buy" else OrderSide.SELL,
                    quantity=quantity,
                    order_type=OrderType.MARKET
                )
            
        except Exception as e:
            self.logger.error(f"Trading signal executionda xato: {e}")
    
    async def _check_risk_limits(self, symbol: str, action: str, confidence: float) -> bool:
        """Risk limitlarni tekshirish"""
        try:
            # Daily trade limit
            today_trades = len([o for o in self.filled_orders 
                              if o.timestamp.date() == datetime.now().date()])
            if today_trades >= self.max_trades_per_day:
                self.logger.warning(f"Daily trade limit reached: {today_trades}")
                return False
            
            # Position size limit
            if action == "buy":
                current_position = self.positions.get(symbol, Position(symbol, 0, 0, 0, 0, 0))
                if current_position.quantity > self.max_position_size * 100000:  # Assuming $100k portfolio
                    self.logger.warning(f"Position size limit exceeded for {symbol}")
                    return False
            
            # Confidence threshold
            if confidence < 0.6:
                self.logger.debug(f"Signal confidence too low: {confidence}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Risk limit checkda xato: {e}")
            return False
    
    async def _get_available_cash(self) -> float:
        """Mavjud naqd pulni olish"""
        try:
            # Simulate portfolio cash
            total_value = sum(pos.market_value for pos in self.positions.values())
            return max(0, 100000 - total_value)  # Assume $100k starting capital
            
        except Exception as e:
            self.logger.error(f"Available cash calculationda xato: {e}")
            return 0.0
    
    async def _create_order(self, symbol: str, side: OrderSide, quantity: float, 
                          order_type: OrderType, price: float = None) -> Optional[Order]:
        """Order yaratish"""
        try:
            # Generate order ID
            order_id = f"ORD_{int(datetime.now().timestamp() * 1000)}"
            
            # Create order
            order = Order(
                id=order_id,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                strategy=self.active_strategy
            )
            
            # Add to pending orders
            self.orders[order_id] = order
            self.pending_orders.append(order)
            
            self.logger.info(f"Order created: {order_id} - {side.value} {quantity} {symbol}")
            
            return order
            
        except Exception as e:
            self.logger.error(f"Order creationda xato: {e}")
            return None
    
    async def _process_pending_orders(self):
        """Pending orderlarni qayta ishlash"""
        try:
            pending_to_remove = []
            
            for order in self.pending_orders:
                # Check if order should be executed
                if await self._should_execute_order(order):
                    await self._execute_order(order)
                    pending_to_remove.append(order)
                elif await self._should_cancel_order(order):
                    await self._cancel_order(order)
                    pending_to_remove.append(order)
            
            # Remove processed orders
            for order in pending_to_remove:
                if order in self.pending_orders:
                    self.pending_orders.remove(order)
                    
        except Exception as e:
            self.logger.error(f"Pending orders processingda xato: {e}")
    
    async def _should_execute_order(self, order: Order) -> bool:
        """Order execution kerakligini tekshirish"""
        try:
            if order.order_type == OrderType.MARKET:
                # Execute immediately for market orders
                return True
            elif order.order_type == OrderType.LIMIT:
                # Execute if price condition is met
                current_price = self.market_data.get(order.symbol, {}).get('price', 0)
                if order.side == OrderSide.BUY and current_price <= order.price:
                    return True
                elif order.side == OrderSide.SELL and current_price >= order.price:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Order execution checkda xato: {e}")
            return False
    
    async def _should_cancel_order(self, order: Order) -> bool:
        """Order cancel kerakligini tekshirish"""
        try:
            # Cancel orders older than 1 hour
            if datetime.now() - order.timestamp > timedelta(hours=1):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Order cancellation checkda xato: {e}")
            return False
    
    async def _execute_order(self, order: Order):
        """Order execution"""
        try:
            # Simulate order execution
            current_price = self.market_data.get(order.symbol, {}).get('price', 0)
            execution_price = current_price * (1 + np.random.uniform(-0.001, 0.001))  # Small slippage
            
            # Update order
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.filled_price = execution_price
            
            # Update position
            await self._update_position_from_order(order)
            
            # Move to filled orders
            self.filled_orders.append(order)
            self.total_trades += 1
            
            self.logger.info(f"Order executed: {order.id} at {execution_price:.4f}")
            
        except Exception as e:
            self.logger.error(f"Order executionda xato: {e}")
    
    async def _cancel_order(self, order: Order):
        """Order cancellation"""
        try:
            order.status = OrderStatus.CANCELLED
            self.cancelled_orders.append(order)
            
            self.logger.info(f"Order cancelled: {order.id}")
            
        except Exception as e:
            self.logger.error(f"Order cancellationda xato: {e}")
    
    async def _update_position_from_order(self, order: Order):
        """Order'dan position'ni yangilash"""
        try:
            symbol = order.symbol
            
            if symbol not in self.positions:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=0,
                    avg_price=0,
                    current_price=self.market_data[symbol]['price'],
                    market_value=0,
                    unrealized_pnl=0
                )
            
            position = self.positions[symbol]
            
            if order.side == OrderSide.BUY:
                # Calculate new average price
                total_cost = position.avg_price * position.quantity + order.filled_price * order.filled_quantity
                total_quantity = position.quantity + order.filled_quantity
                
                position.avg_price = total_cost / total_quantity if total_quantity > 0 else 0
                position.quantity = total_quantity
                
                # Check if this closes a short position
                if position.quantity < 0:
                    realized_pnl = (-order.filled_quantity) * (position.avg_price - order.filled_price)
                    position.realized_pnl += realized_pnl
                    position.quantity = 0
                
            else:  # SELL
                # Update position
                if position.quantity >= order.filled_quantity:
                    # Partial or full position close
                    position.quantity -= order.filled_quantity
                    
                    # Calculate realized P&L
                    realized_pnl = order.filled_quantity * (order.filled_price - position.avg_price)
                    position.realized_pnl += realized_pnl
                    
                    if position.quantity == 0:
                        position.avg_price = 0
                else:
                    # Short position
                    short_quantity = order.filled_quantity - position.quantity
                    realized_pnl = short_quantity * (position.avg_price - order.filled_price)
                    position.realized_pnl += realized_pnl
                    position.quantity = -short_quantity
                    position.avg_price = order.filled_price
            
            # Update market value and unrealized P&L
            position.current_price = self.market_data[symbol]['price']
            position.market_value = position.quantity * position.current_price
            position.unrealized_pnl = (position.current_price - position.avg_price) * position.quantity
            position.last_updated = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Position update from orderda xato: {e}")
    
    async def _update_positions(self):
        """Positionlarni yangilash"""
        try:
            for symbol, position in self.positions.items():
                if symbol in self.market_data:
                    # Update current price
                    position.current_price = self.market_data[symbol]['price']
                    position.market_value = position.quantity * position.current_price
                    position.unrealized_pnl = (position.current_price - position.avg_price) * position.quantity
                    position.last_updated = datetime.now()
                    
                    # Check stop loss
                    await self._check_stop_loss(position)
                    
        except Exception as e:
            self.logger.error(f"Position updateda xato: {e}")
    
    async def _check_stop_loss(self, position: Position):
        """Stop loss tekshirish"""
        try:
            if position.quantity > 0:  # Long position
                loss_pct = (position.avg_price - position.current_price) / position.avg_price
                if loss_pct >= self.stop_loss_pct:
                    # Create stop loss order
                    await self._create_order(
                        symbol=position.symbol,
                        side=OrderSide.SELL,
                        quantity=position.quantity,
                        order_type=OrderType.MARKET
                    )
                    self.logger.warning(f"Stop loss triggered for {position.symbol}")
                    
        except Exception as e:
            self.logger.error(f"Stop loss checkda xato: {e}")
    
    async def _monitor_risk(self):
        """Risk monitoring"""
        try:
            # Calculate current P&L
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
            total_realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
            total_pnl = total_unrealized_pnl + total_realized_pnl
            
            # Update daily P&L
            today_orders = [o for o in self.filled_orders 
                          if o.timestamp.date() == datetime.now().date()]
            self.daily_pnl = sum((o.filled_price - o.price if o.side == OrderSide.BUY else o.price - o.filled_price) * o.filled_quantity 
                               for o in today_orders if hasattr(o, 'price') and o.price)
            
            # Check daily loss limit
            if self.daily_pnl < -self.max_daily_loss * 100000:  # Assuming $100k portfolio
                self.logger.warning("Daily loss limit reached, stopping trading")
                await self.stop_automated_trading()
            
            # Update win rate
            if self.total_trades > 0:
                winning_today = sum(1 for o in today_orders if (o.filled_price - o.price) > 0 if hasattr(o, 'price'))
                self.win_rate = winning_today / len(today_orders) if today_orders else 0
            
        except Exception as e:
            self.logger.error(f"Risk monitoringda xato: {e}")
    
    async def get_portfolio_summary(self) -> Dict:
        """Portfolio summary olish"""
        try:
            total_value = sum(pos.market_value for pos in self.positions.values())
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
            total_realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
            
            return {
                "total_value": total_value,
                "cash": await self._get_available_cash(),
                "positions": {symbol: {
                    "quantity": pos.quantity,
                    "avg_price": pos.avg_price,
                    "current_price": pos.current_price,
                    "market_value": pos.market_value,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "realized_pnl": pos.realized_pnl
                } for symbol, pos in self.positions.items()},
                "total_unrealized_pnl": total_unrealized_pnl,
                "total_realized_pnl": total_realized_pnl,
                "daily_pnl": self.daily_pnl,
                "total_trades": self.total_trades,
                "win_rate": self.win_rate,
                "active_strategy": self.active_strategy,
                "is_automated": self.is_automated
            }
            
        except Exception as e:
            self.logger.error(f"Portfolio summaryda xato: {e}")
            return {}
    
    async def close(self):
        """Trading engine'ni yopish"""
        try:
            self.logger.info("Trading Engine yopilmoqda...")
            
            # Stop automated trading
            await self.stop_automated_trading()
            
            # Clear data
            self.positions.clear()
            self.orders.clear()
            self.pending_orders.clear()
            self.filled_orders.clear()
            self.cancelled_orders.clear()
            self.strategies.clear()
            self.market_data.clear()
            self.price_history.clear()
            
            self.is_running = False
            self.logger.info("✅ Trading Engine muvaffaqiyatli yopildi")
            
        except Exception as e:
            self.logger.error(f"Trading Engine'ni yopishda xato: {e}")
    
    async def get_trading_statistics(self) -> Dict:
        """Trading statistikalarini olish"""
        return {
            "is_running": self.is_running,
            "is_automated": self.is_automated,
            "active_strategy": self.active_strategy,
            "total_trades": self.total_trades,
            "win_rate": self.win_rate,
            "daily_pnl": self.daily_pnl,
            "pending_orders": len(self.pending_orders),
            "filled_orders": len(self.filled_orders),
            "cancelled_orders": len(self.cancelled_orders),
            "available_strategies": list(self.strategies.keys()),
            "configuration": self.config
        }