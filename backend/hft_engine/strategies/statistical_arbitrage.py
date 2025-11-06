"""
Statistical Arbitrage Strategy
============================

Advanced statistical arbitrage using mean reversion and pairs trading
Optimized for identifying and exploiting statistical relationships
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
class StatisticalSignal:
    """Statistical arbitrage signal"""
    symbol_pair: str  # e.g., "AAPL_MSFT"
    signal_type: str  # 'long_short', 'short_long', 'close_position'
    confidence: float
    z_score: float
    entry_price_1: float
    entry_price_2: float
    quantity_ratio: float
    expected_profit: float
    timestamp: float
    hold_duration: float  # Expected hold time

class StatisticalArbitrageStrategy:
    """
    Statistical Arbitrage Strategy
    
    Uses statistical methods to identify mean-reverting opportunities
    """
    
    def __init__(self, symbols: List[str], config: Dict[str, Any]):
        self.symbols = symbols
        self.config = config
        
        # Strategy parameters
        self.lookback_period = config.get('lookback_period', 100)
        self.entry_threshold = config.get('entry_threshold', 2.0)  # Z-score
        self.exit_threshold = config.get('exit_threshold', 0.5)  # Z-score
        self.max_hold_time = config.get('max_hold_time', 3600)  # 1 hour
        self.min_correlation = config.get('min_correlation', 0.7)
        
        # Performance monitoring
        self.latency_profiler = LatencyProfiler()
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.price_data: Dict[str, List[Tuple[float, float]]] = {}  # (timestamp, price)
        self.correlations: Dict[str, float] = {}
        self.active_positions: Dict[str, Dict[str, Any]] = {}
        
        # Statistical models
        self.pairs = self._initialize_pairs()
        
        # Thread safety
        self.lock = Lock()
        
    def _initialize_pairs(self) -> List[Tuple[str, str]]:
        """Initialize symbol pairs for statistical analysis"""
        return [
            # Stock pairs
            ('AAPL', 'MSFT'),
            ('GOOGL', 'META'),  # Large tech
            ('TSLA', 'RIVN'),   # EV manufacturers
            ('NVDA', 'AMD'),    # GPU/semiconductor
            
            # Crypto pairs
            ('BTC/USD', 'ETH/USD'),
            
            # Commodities pairs
            ('XAU/USD', 'XAG/USD'),  # Gold vs Silver
            ('XPT/USD', 'XPD/USD'),  # Platinum vs Palladium
            
            # Forex pairs (cross-currency)
            ('EUR/USD', 'GBP/USD'),
            ('USD/JPY', 'USD/CHF')
        ]
    
    async def generate_signals(self, order_books: Dict[str, OrderBook]) -> List[StatisticalSignal]:
        """Generate statistical arbitrage signals"""
        start_time = self.latency_profiler.start_timer()
        
        try:
            signals = []
            
            # Update price data from order books
            await self._update_price_data(order_books)
            
            # Analyze each pair for opportunities
            for pair in self.pairs:
                if all(symbol in order_books for symbol in pair):
                    signal = await self._analyze_pair(pair, order_books)
                    if signal:
                        signals.append(signal)
            
            # Record latency
            self.latency_profiler.end_timer(start_time, "stat_arb.generate_signals")
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error generating statistical arbitrage signals: {e}")
            self.latency_profiler.end_timer(start_time, "stat_arb.generate_signals")
            return []
    
    async def _update_price_data(self, order_books: Dict[str, OrderBook]):
        """Update price data from order books"""
        current_time = time.time()
        
        for symbol in self.symbols:
            if symbol in order_books:
                order_book = order_books[symbol]
                best_bid = order_book.get_best_bid()
                best_ask = order_book.get_best_ask()
                
                if best_bid is not None and best_ask is not None:
                    mid_price = (best_bid + best_ask) / 2
                    
                    if symbol not in self.price_data:
                        self.price_data[symbol] = []
                    
                    self.price_data[symbol].append((current_time, mid_price))
                    
                    # Keep only recent data
                    if len(self.price_data[symbol]) > 1000:
                        self.price_data[symbol] = self.price_data[symbol][-500:]
    
    async def _analyze_pair(self, pair: Tuple[str, str], order_books: Dict[str, OrderBook]) -> Optional[StatisticalSignal]:
        """Analyze pair for statistical arbitrage opportunity"""
        symbol1, symbol2 = pair
        
        try:
            # Get recent price data
            prices1 = [p[1] for p in self.price_data.get(symbol1, [])[-self.lookback_period:]]
            prices2 = [p[1] for p in self.price_data.get(symbol2, [])[-self.lookback_period:]]
            
            if len(prices1) < 20 or len(prices2) < 20:
                return None
            
            # Calculate correlation
            correlation = np.corrcoef(prices1, prices2)[0, 1]
            
            # Check if correlation is significant
            if abs(correlation) < self.min_correlation:
                return None
            
            # Calculate spread and its statistics
            spread = np.array(prices1) - np.array(prices2)
            spread_mean = np.mean(spread)
            spread_std = np.std(spread)
            
            # Get current spread
            current_spread = prices1[-1] - prices2[-1]
            
            # Calculate z-score
            if spread_std > 0:
                z_score = (current_spread - spread_mean) / spread_std
            else:
                z_score = 0
            
            # Check if position exists for this pair
            pair_key = f"{symbol1}_{symbol2}"
            current_position = self.active_positions.get(pair_key)
            
            # Entry signals
            if current_position is None:
                if abs(z_score) > self.entry_threshold:
                    if z_score > 0:
                        # Spread is high - short symbol1, long symbol2
                        signal_type = 'short_long'
                    else:
                        # Spread is low - long symbol1, short symbol2
                        signal_type = 'long_short'
                    
                    return StatisticalSignal(
                        symbol_pair=pair_key,
                        signal_type=signal_type,
                        confidence=min(1.0, abs(z_score) / 3.0),
                        z_score=z_score,
                        entry_price_1=prices1[-1],
                        entry_price_2=prices2[-1],
                        quantity_ratio=1.0,  # Equal quantity for simplicity
                        expected_profit=abs(z_score) * 0.01,  # Simplified profit estimate
                        timestamp=time.time(),
                        hold_duration=self.max_hold_time
                    )
            
            # Exit signals
            elif current_position:
                if abs(z_score) < self.exit_threshold:
                    return StatisticalSignal(
                        symbol_pair=pair_key,
                        signal_type='close_position',
                        confidence=0.9,
                        z_score=z_score,
                        entry_price_1=current_position['price1'],
                        entry_price_2=current_position['price2'],
                        quantity_ratio=current_position['ratio'],
                        expected_profit=current_position.get('unrealized_pnl', 0),
                        timestamp=time.time(),
                        hold_duration=0
                    )
                
                # Check for maximum hold time
                if time.time() - current_position['entry_time'] > self.max_hold_time:
                    return StatisticalSignal(
                        symbol_pair=pair_key,
                        signal_type='close_position',
                        confidence=0.8,
                        z_score=z_score,
                        entry_price_1=current_position['price1'],
                        entry_price_2=current_position['price2'],
                        quantity_ratio=current_position['ratio'],
                        expected_profit=current_position.get('unrealized_pnl', 0),
                        timestamp=time.time(),
                        hold_duration=0
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing pair {pair}: {e}")
            return None
    
    def update_position(self, signal: StatisticalSignal, executed: bool = True):
        """Update position after signal execution"""
        with self.lock:
            if executed:
                if signal.signal_type == 'close_position':
                    # Close existing position
                    if signal.symbol_pair in self.active_positions:
                        del self.active_positions[signal.symbol_pair]
                else:
                    # Open new position
                    self.active_positions[signal.symbol_pair] = {
                        'type': signal.signal_type,
                        'entry_time': signal.timestamp,
                        'price1': signal.entry_price_1,
                        'price2': signal.entry_price_2,
                        'ratio': signal.quantity_ratio,
                        'z_score': signal.z_score,
                        'unrealized_pnl': 0.0
                    }
    
    def calculate_unrealized_pnl(self, current_prices: Dict[str, float]):
        """Calculate unrealized P&L for all positions"""
        with self.lock:
            for pair_key, position in self.active_positions.items():
                try:
                    symbol1, symbol2 = pair_key.split('_', 1)
                    
                    price1 = current_prices.get(symbol1)
                    price2 = current_prices.get(symbol2)
                    
                    if price1 and price2:
                        if position['type'] == 'long_short':
                            # Long symbol1, short symbol2
                            pnl1 = (price1 - position['price1']) * position['ratio']
                            pnl2 = (position['price2'] - price2) * position['ratio']
                        else:  # short_long
                            # Short symbol1, long symbol2
                            pnl1 = (position['price1'] - price1) * position['ratio']
                            pnl2 = (price2 - position['price2']) * position['ratio']
                        
                        position['unrealized_pnl'] = pnl1 + pnl2
                
                except Exception as e:
                    self.logger.error(f"Error calculating P&L for {pair_key}: {e}")
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """Get strategy status and performance"""
        with self.lock:
            total_unrealized_pnl = sum(
                pos.get('unrealized_pnl', 0) for pos in self.active_positions.values()
            )
            
            return {
                'strategy': 'statistical_arbitrage',
                'active_positions': len(self.active_positions),
                'total_unrealized_pnl': total_unrealized_pnl,
                'pairs_analyzed': len(self.pairs),
                'correlations_tracked': len(self.correlations),
                'positions': {
                    pair_key: {
                        'type': pos['type'],
                        'entry_time': pos['entry_time'],
                        'z_score': pos['z_score'],
                        'unrealized_pnl': pos.get('unrealized_pnl', 0)
                    }
                    for pair_key, pos in self.active_positions.items()
                },
                'latency_stats': self.latency_profiler.get_stats()
            }
    
    def get_update_interval(self) -> float:
        """Get strategy update interval"""
        return 0.1  # 100ms for statistical analysis
    
    async def shutdown(self):
        """Shutdown strategy"""
        self.logger.info("Shutting down Statistical Arbitrage Strategy")
        # Close all positions
        with self.lock:
            self.active_positions.clear()