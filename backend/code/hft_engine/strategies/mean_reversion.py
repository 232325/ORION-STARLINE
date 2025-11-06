"""
Mean Reversion Strategy
======================

Mean reversion-based trading strategy for ranging markets
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
class MeanReversionSignal:
    """Mean reversion signal"""
    symbol: str
    signal_type: str  # 'buy', 'sell', 'close'
    confidence: float
    deviation_score: float
    price: float
    quantity: int
    timestamp: float

class MeanReversionStrategy:
    """Mean Reversion Trading Strategy"""
    
    def __init__(self, symbols: List[str], config: Dict[str, Any]):
        self.symbols = symbols
        self.config = config
        self.latency_profiler = LatencyProfiler()
        self.logger = logging.getLogger(__name__)
        
        self.lookback_period = config.get('lookback_period', 50)
        self.entry_threshold = config.get('entry_threshold', 2.0)  # Standard deviations
        self.exit_threshold = config.get('exit_threshold', 0.5)
        
    async def generate_signals(self, order_books: Dict[str, OrderBook]) -> List[MeanReversionSignal]:
        """Generate mean reversion signals"""
        start_time = self.latency_profiler.start_timer()
        
        try:
            signals = []
            
            for symbol in self.symbols:
                if symbol not in order_books:
                    continue
                
                order_book = order_books[symbol]
                signal = await self._analyze_mean_reversion(symbol, order_book)
                
                if signal:
                    signals.append(signal)
            
            self.latency_profiler.end_timer(start_time, "mean_reversion.generate_signals")
            return signals
            
        except Exception as e:
            self.logger.error(f"Error generating mean reversion signals: {e}")
            self.latency_profiler.end_timer(start_time, "mean_reversion.generate_signals")
            return []
    
    async def _analyze_mean_reversion(self, symbol: str, order_book: OrderBook) -> Optional[MeanReversionSignal]:
        """Analyze mean reversion for symbol"""
        try:
            best_bid = order_book.get_best_bid()
            best_ask = order_book.get_best_ask()
            
            if best_bid is None or best_ask is None:
                return None
            
            mid_price = (best_bid + best_ask) / 2
            
            # Simplified mean reversion calculation
            # In reality, this would use Bollinger Bands or similar
            mean_price = mid_price * 1.0  # Simplified mean
            std_deviation = mid_price * 0.02  # Simplified standard deviation
            
            deviation = (mid_price - mean_price) / std_deviation
            
            if abs(deviation) > self.entry_threshold:
                signal_type = 'buy' if deviation < -self.entry_threshold else 'sell'
                confidence = min(1.0, abs(deviation) / 3.0)
                
                return MeanReversionSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    confidence=confidence,
                    deviation_score=deviation,
                    price=mid_price,
                    quantity=50,
                    timestamp=time.time()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing mean reversion for {symbol}: {e}")
            return None
    
    def get_update_interval(self) -> float:
        return 0.1  # 100ms
    
    async def shutdown(self):
        self.logger.info("Shutting down Mean Reversion Strategy")