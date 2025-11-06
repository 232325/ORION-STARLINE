"""
Momentum Strategy
================

Momentum-based trading strategy for trending markets
"""

import time
import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..core.orderbook import OrderBook
from ..core.latency_profiler import LatencyProfiler

@dataclass
class MomentumSignal:
    """Momentum trading signal"""
    symbol: str
    signal_type: str  # 'long', 'short', 'close'
    confidence: float
    momentum_score: float
    price: float
    quantity: int
    timestamp: float

class MomentumStrategy:
    """Momentum Trading Strategy"""
    
    def __init__(self, symbols: List[str], config: Dict[str, Any]):
        self.symbols = symbols
        self.config = config
        self.latency_profiler = LatencyProfiler()
        self.logger = logging.getLogger(__name__)
        
        self.momentum_period = config.get('momentum_period', 20)
        self.lookback_period = config.get('lookback_period', 100)
        self.entry_threshold = config.get('entry_threshold', 0.02)
        
    async def generate_signals(self, order_books: Dict[str, OrderBook]) -> List[MomentumSignal]:
        """Generate momentum signals"""
        start_time = self.latency_profiler.start_timer()
        
        try:
            signals = []
            
            for symbol in self.symbols:
                if symbol not in order_books:
                    continue
                
                order_book = order_books[symbol]
                signal = await self._analyze_momentum(symbol, order_book)
                
                if signal:
                    signals.append(signal)
            
            self.latency_profiler.end_timer(start_time, "momentum.generate_signals")
            return signals
            
        except Exception as e:
            self.logger.error(f"Error generating momentum signals: {e}")
            self.latency_profiler.end_timer(start_time, "momentum.generate_signals")
            return []
    
    async def _analyze_momentum(self, symbol: str, order_book: OrderBook) -> Optional[MomentumSignal]:
        """Analyze momentum for symbol"""
        try:
            best_bid = order_book.get_best_bid()
            best_ask = order_book.get_best_ask()
            
            if best_bid is None or best_ask is None:
                return None
            
            mid_price = (best_bid + best_ask) / 2
            
            # Simplified momentum calculation
            # In reality, this would use historical price data
            momentum_score = np.random.uniform(-0.05, 0.05)  # Simulated
            
            if abs(momentum_score) > self.entry_threshold:
                signal_type = 'long' if momentum_score > 0 else 'short'
                confidence = min(1.0, abs(momentum_score) * 10)
                
                return MomentumSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    confidence=confidence,
                    momentum_score=momentum_score,
                    price=mid_price,
                    quantity=100,
                    timestamp=time.time()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing momentum for {symbol}: {e}")
            return None
    
    def get_update_interval(self) -> float:
        return 0.05  # 50ms
    
    async def shutdown(self):
        self.logger.info("Shutting down Momentum Strategy")