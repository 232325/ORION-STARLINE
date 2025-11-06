"""
Market Making Strategy
====================

Advanced market making strategy optimized for HFT operations
Provides liquidity to markets while managing inventory and risk
"""

import time
import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from threading import Lock

from ..core.orderbook import OrderBook
from ..core.latency_profiler import LatencyProfiler

@dataclass
class MarketMakingSignal:
    """Market making signal structure"""
    symbol: str
    side: str  # 'buy' or 'sell'
    price: float
    quantity: int
    confidence: float
    timestamp: float
    inventory_target: float
    skew_bps: float

@dataclass
class InventoryMetrics:
    """Inventory tracking metrics"""
    symbol: str
    current_position: float
    target_position: float
    inventory_risk: float
    pnl: float
    inventory_cost: float

class MarketMakingStrategy:
    """
    Advanced Market Making Strategy
    
    Provides liquidity while managing inventory and risk
    Optimized for microsecond-level decision making
    """
    
    def __init__(self, symbols: List[str], config: Dict[str, Any]):
        self.symbols = symbols
        self.config = config
        
        # Strategy parameters
        self.spread_multiplier = config.get('spread_multiplier', 1.2)
        self.inventory_target = config.get('inventory_target', 0.0)
        self.max_inventory = config.get('max_inventory', 1000)
        self.skew_factor = config.get('skew_factor', 0.5)
        self.rebalance_threshold = config.get('rebalance_threshold', 0.1)
        
        # Performance monitoring
        self.latency_profiler = LatencyProfiler()
        self.logger = logging.getLogger(__name__)
        
        # State tracking
        self.active_positions: Dict[str, float] = {}
        self.target_positions: Dict[str, float] = {}
        self.pnl_tracker: Dict[str, float] = {}
        
        # Market making parameters per asset class
        self.asset_params = self._initialize_asset_parameters()
        
        # Thread safety
        self.lock = Lock()
        
    def _initialize_asset_parameters(self) -> Dict[str, Dict[str, float]]:
        """Initialize asset-specific parameters"""
        return {
            # Stocks (NASDAQ/NYSE)
            'AAPL': {
                'base_spread_bps': 3.0,
                'volatility_adjustment': 1.0,
                'inventory_limit': 500,
                'rebalance_frequency': 0.1
            },
            'GOOGL': {
                'base_spread_bps': 4.0,
                'volatility_adjustment': 1.2,
                'inventory_limit': 300,
                'rebalance_frequency': 0.1
            },
            'MSFT': {
                'base_spread_bps': 3.5,
                'volatility_adjustment': 1.0,
                'inventory_limit': 400,
                'rebalance_frequency': 0.1
            },
            'TSLA': {
                'base_spread_bps': 6.0,
                'volatility_adjustment': 1.5,
                'inventory_limit': 200,
                'rebalance_frequency': 0.05
            },
            'NVDA': {
                'base_spread_bps': 5.0,
                'volatility_adjustment': 1.3,
                'inventory_limit': 300,
                'rebalance_frequency': 0.08
            },
            
            # Forex
            'EUR/USD': {
                'base_spread_bps': 0.8,
                'volatility_adjustment': 0.8,
                'inventory_limit': 100000,
                'rebalance_frequency': 0.2
            },
            'GBP/USD': {
                'base_spread_bps': 1.0,
                'volatility_adjustment': 0.9,
                'inventory_limit': 80000,
                'rebalance_frequency': 0.2
            },
            'USD/JPY': {
                'base_spread_bps': 0.9,
                'volatility_adjustment': 0.8,
                'inventory_limit': 500000,
                'rebalance_frequency': 0.2
            },
            'USD/CHF': {
                'base_spread_bps': 1.2,
                'volatility_adjustment': 0.9,
                'inventory_limit': 60000,
                'rebalance_frequency': 0.2
            },
            
            # Metals
            'XAU/USD': {
                'base_spread_bps': 2.0,
                'volatility_adjustment': 1.2,
                'inventory_limit': 100,
                'rebalance_frequency': 0.15
            },
            'XAG/USD': {
                'base_spread_bps': 4.0,
                'volatility_adjustment': 1.3,
                'inventory_limit': 1000,
                'rebalance_frequency': 0.15
            },
            'XPT/USD': {
                'base_spread_bps': 6.0,
                'volatility_adjustment': 1.4,
                'inventory_limit': 50,
                'rebalance_frequency': 0.12
            },
            'XPD/USD': {
                'base_spread_bps': 8.0,
                'volatility_adjustment': 1.5,
                'inventory_limit': 30,
                'rebalance_frequency': 0.1
            },
            
            # Crypto
            'BTC/USD': {
                'base_spread_bps': 5.0,
                'volatility_adjustment': 2.0,
                'inventory_limit': 10,
                'rebalance_frequency': 0.05
            },
            'ETH/USD': {
                'base_spread_bps': 7.0,
                'volatility_adjustment': 2.2,
                'inventory_limit': 50,
                'rebalance_frequency': 0.05
            }
        }
    
    async def generate_signals(self, order_books: Dict[str, OrderBook]) -> List[MarketMakingSignal]:
        """Generate market making signals"""
        start_time = self.latency_profiler.start_timer()
        
        try:
            signals = []
            
            for symbol in self.symbols:
                if symbol not in order_books:
                    continue
                
                order_book = order_books[symbol]
                
                # Generate signal for this symbol
                signal = await self._generate_symbol_signal(symbol, order_book)
                
                if signal:
                    signals.append(signal)
            
            # Record latency
            self.latency_profiler.end_timer(start_time, "market_making.generate_signals")
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error generating market making signals: {e}")
            self.latency_profiler.end_timer(start_time, "market_making.generate_signals")
            return []
    
    async def _generate_symbol_signal(self, symbol: str, order_book: OrderBook) -> Optional[MarketMakingSignal]:
        """Generate signal for specific symbol"""
        try:
            # Get market data
            best_bid = order_book.get_best_bid()
            best_ask = order_book.get_best_ask()
            
            if best_bid is None or best_ask is None:
                return None
            
            mid_price = (best_bid + best_ask) / 2
            spread = best_ask - best_bid
            
            # Get asset parameters
            params = self.asset_params.get(symbol, self._get_default_params())
            
            # Calculate dynamic spread
            current_spread_bps = (spread / mid_price) * 10000
            target_spread_bps = params['base_spread_bps'] * self.spread_multiplier
            
            # Adjust for market conditions
            volatility_factor = self._calculate_volatility_factor(order_book)
            adjusted_spread_bps = target_spread_bps * volatility_factor
            
            # Calculate optimal price levels
            bid_price, ask_price = self._calculate_optimal_prices(
                mid_price, adjusted_spread_bps
            )
            
            # Calculate inventory management
            inventory_signal = self._calculate_inventory_skew(
                symbol, order_book, bid_price, ask_price
            )
            
            # Apply inventory skew
            bid_price -= inventory_signal['bid_skew']
            ask_price += inventory_signal['ask_skew']
            
            # Calculate quantity based on volatility and spread
            quantity = self._calculate_optimal_quantity(
                symbol, current_spread_bps, adjusted_spread_bps
            )
            
            # Create signal
            signal = MarketMakingSignal(
                symbol=symbol,
                side='both',  # Market making provides both sides
                price=mid_price,
                quantity=quantity,
                confidence=self._calculate_confidence(order_book, spread),
                timestamp=time.time(),
                inventory_target=self.inventory_target,
                skew_bps=inventory_signal['total_skew']
            )
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    def _calculate_volatility_factor(self, order_book) -> float:
        """Calculate volatility-based spread adjustment"""
        try:
            # Calculate recent price volatility
            recent_ticks = order_book.get_tick_history(100) if hasattr(order_book, 'get_tick_history') else []
            
            if len(recent_ticks) < 10:
                return 1.0
            
            prices = [tick.last for tick in recent_ticks[-20:]]
            if len(prices) < 2:
                return 1.0
            
            returns = [np.log(prices[i]/prices[i-1]) for i in range(1, len(prices))]
            volatility = np.std(returns)
            
            # Adjust spread based on volatility
            volatility_factor = 1 + (volatility * 1000)  # Scale factor
            
            return max(0.5, min(3.0, volatility_factor))
            
        except Exception:
            return 1.0
    
    def _calculate_optimal_prices(self, mid_price: float, spread_bps: float) -> Tuple[float, float]:
        """Calculate optimal bid and ask prices"""
        half_spread = (spread_bps * mid_price) / 20000  # Convert bps to price
        
        bid_price = mid_price - half_spread
        ask_price = mid_price + half_spread
        
        return bid_price, ask_price
    
    def _calculate_inventory_skew(self, symbol: str, order_book: OrderBook, 
                                bid_price: float, ask_price: float) -> Dict[str, float]:
        """Calculate inventory-based price skewing"""
        try:
            current_position = self.active_positions.get(symbol, 0.0)
            target_position = self.target_positions.get(symbol, self.inventory_target)
            
            # Calculate inventory deviation
            inventory_deviation = current_position - target_position
            params = self.asset_params.get(symbol, self._get_default_params())
            
            max_inventory = params['inventory_limit']
            
            # Calculate skew magnitude
            if max_inventory != 0:
                inventory_ratio = abs(inventory_deviation) / max_inventory
                skew_magnitude = self.skew_factor * inventory_ratio
                
                # Apply skew to prices
                if inventory_deviation > 0:  # Long position
                    bid_skew = bid_price * skew_magnitude * 0.001  # Reduce bid
                    ask_skew = ask_price * skew_magnitude * 0.001  # Increase ask
                else:  # Short or neutral position
                    bid_skew = bid_price * skew_magnitude * 0.001  # Increase bid
                    ask_skew = ask_price * skew_magnitude * 0.001  # Reduce ask
            else:
                bid_skew = ask_skew = 0
            
            total_skew_bps = ((bid_skew + ask_skew) / ((bid_price + ask_price) / 2)) * 10000
            
            return {
                'bid_skew': bid_skew,
                'ask_skew': ask_skew,
                'total_skew': total_skew_bps
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating inventory skew: {e}")
            return {'bid_skew': 0, 'ask_skew': 0, 'total_skew': 0}
    
    def _calculate_optimal_quantity(self, symbol: str, current_spread_bps: float, 
                                  target_spread_bps: float) -> int:
        """Calculate optimal order quantity"""
        try:
            params = self.asset_params.get(symbol, self._get_default_params())
            base_quantity = params['inventory_limit'] // 10  # Conservative base size
            
            # Adjust based on spread efficiency
            if current_spread_bps < target_spread_bps:
                quantity_multiplier = 1.5  # Increase size in tight markets
            else:
                quantity_multiplier = 0.7  # Reduce size in wide markets
            
            # Adjust based on asset type
            if symbol in ['AAPL', 'MSFT']:  # Liquid stocks
                base_quantity *= 2
            elif symbol in ['XPT/USD', 'XPD/USD']:  # Less liquid metals
                base_quantity *= 0.5
            
            return int(base_quantity * quantity_multiplier)
            
        except Exception:
            return 100
    
    def _calculate_confidence(self, order_book, spread: float) -> float:
        """Calculate signal confidence based on market conditions"""
        try:
            # Base confidence
            confidence = 0.8
            
            # Adjust for spread tightness
            if spread > 0:
                spread_pct = spread / ((order_book.get_best_bid() + order_book.get_best_ask()) / 2)
                if spread_pct < 0.001:  # Very tight spreads
                    confidence += 0.15
                elif spread_pct > 0.01:  # Wide spreads
                    confidence -= 0.2
            
            # Adjust for book depth
            depth = order_book.get_market_depth(5)
            total_bid_volume = sum(level.total_quantity for level in depth['bids'])
            total_ask_volume = sum(level.total_quantity for level in depth['asks'])
            
            if total_bid_volume > 1000 and total_ask_volume > 1000:
                confidence += 0.1  # Good depth
            elif total_bid_volume < 100 or total_ask_volume < 100:
                confidence -= 0.3  # Poor depth
            
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.5
    
    def _get_default_params(self) -> Dict[str, float]:
        """Get default parameters for unknown symbols"""
        return {
            'base_spread_bps': 5.0,
            'volatility_adjustment': 1.0,
            'inventory_limit': 500,
            'rebalance_frequency': 0.1
        }
    
    def update_position(self, symbol: str, position_change: float, price: float):
        """Update position after trade execution"""
        with self.lock:
            if symbol not in self.active_positions:
                self.active_positions[symbol] = 0.0
            
            old_position = self.active_positions[symbol]
            self.active_positions[symbol] += position_change
            
            # Update P&L
            position_value_change = position_change * price
            if symbol not in self.pnl_tracker:
                self.pnl_tracker[symbol] = 0.0
            
            self.pnl_tracker[symbol] += position_value_change
            
            self.logger.debug(
                f"Position update - {symbol}: {old_position:.2f} -> "
                f"{self.active_positions[symbol]:.2f}, P&L: {position_value_change:.2f}"
            )
    
    def get_inventory_metrics(self, symbol: str) -> InventoryMetrics:
        """Get inventory metrics for symbol"""
        with self.lock:
            current_position = self.active_positions.get(symbol, 0.0)
            target_position = self.target_positions.get(symbol, self.inventory_target)
            
            params = self.asset_params.get(symbol, self._get_default_params())
            max_inventory = params['inventory_limit']
            
            # Calculate inventory risk (as percentage of limit)
            inventory_risk = abs(current_position) / max_inventory if max_inventory > 0 else 0
            
            return InventoryMetrics(
                symbol=symbol,
                current_position=current_position,
                target_position=target_position,
                inventory_risk=min(1.0, inventory_risk),
                pnl=self.pnl_tracker.get(symbol, 0.0),
                inventory_cost=current_position * 0.01  # Simplified cost model
            )
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """Get strategy status and performance"""
        with self.lock:
            total_pnl = sum(self.pnl_tracker.values())
            total_positions = sum(abs(pos) for pos in self.active_positions.values())
            
            inventory_metrics = {
                symbol: {
                    'position': self.active_positions.get(symbol, 0.0),
                    'target': self.target_positions.get(symbol, self.inventory_target),
                    'risk': self.get_inventory_metrics(symbol).inventory_risk,
                    'pnl': self.pnl_tracker.get(symbol, 0.0)
                }
                for symbol in self.symbols
            }
            
            return {
                'strategy': 'market_making',
                'active_symbols': len([s for s in self.active_positions.values() if s != 0]),
                'total_pnl': total_pnl,
                'total_positions': total_positions,
                'inventory_metrics': inventory_metrics,
                'latency_stats': self.latency_profiler.get_stats()
            }
    
    def get_update_interval(self) -> float:
        """Get strategy update interval"""
        return 0.01  # 10ms for high-frequency updates
    
    async def shutdown(self):
        """Shutdown strategy"""
        self.logger.info("Shutting down Market Making Strategy")
        # In a real implementation, this would cancel all pending orders
        # and close positions safely
        pass