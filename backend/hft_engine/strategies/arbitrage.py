"""
Arbitrage Strategy
=================

Cross-asset and cross-market arbitrage detection and execution
Optimized for identifying and exploiting price discrepancies
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
class ArbitrageOpportunity:
    """Arbitrage opportunity structure"""
    symbol: str
    opportunity_type: str  # 'price_spread', 'triangular', 'cross_market'
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread_bps: float
    quantity: int
    profit_potential: float
    confidence: float
    timestamp: float
    execution_window: float  # Time window for execution

@dataclass
class MarketCorrelation:
    """Market correlation data"""
    symbol1: str
    symbol2: str
    correlation: float
    last_updated: float

class ArbitrageStrategy:
    """
    Advanced Arbitrage Strategy
    
    Detects and exploits price discrepancies across markets and assets
    """
    
    def __init__(self, symbols: List[str], config: Dict[str, Any]):
        self.symbols = symbols
        self.config = config
        
        # Strategy parameters
        self.min_spread_bps = config.get('min_spread_bps', 5.0)
        self.max_execution_time_us = config.get('max_execution_time_us', 500)
        self.max_position_size = config.get('max_position_size', 1000)
        self.correlation_threshold = config.get('correlation_threshold', 0.8)
        
        # Performance monitoring
        self.latency_profiler = LatencyProfiler()
        self.logger = logging.getLogger(__name__)
        
        # Market data storage
        self.price_history: Dict[str, List[Tuple[float, float]]] = {}  # (timestamp, price)
        self.market_correlations: Dict[str, MarketCorrelation] = {}
        self.active_opportunities: List[ArbitrageOpportunity] = []
        
        # Exchange mapping
        self.exchange_symbols = self._initialize_exchange_symbols()
        self.exchange_latencies = self._initialize_exchange_latencies()
        
        # Thread safety
        self.lock = Lock()
        
    def _initialize_exchange_symbols(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize symbols available on each exchange"""
        return {
            'NASDAQ': {
                'stocks': ['AAPL', 'MSFT'],
                'etf': ['SPY', 'QQQ'],
                'indices': ['NASDAQ_IXIC']
            },
            'NYSE': {
                'stocks': ['GOOGL', 'TSLA', 'NVDA'],
                'etf': ['SPY', 'DIA'],
                'indices': ['SPX', 'DJI']
            },
            'FOREX': {
                'majors': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF'],
                'crosses': ['EUR/GBP', 'EUR/JPY', 'GBP/JPY']
            },
            'CRYPTO': {
                'major': ['BTC/USD', 'ETH/USD'],
                'altcoin': ['ADA/USD', 'DOT/USD']
            },
            'METALS': {
                'precious': ['XAU/USD', 'XAG/USD'],
                'industrial': ['XPT/USD', 'XPD/USD']
            }
        }
    
    def _initialize_exchange_latencies(self) -> Dict[str, float]:
        """Initialize exchange latencies (microseconds)"""
        return {
            'NASDAQ': 50,
            'NYSE': 55,
            'FOREX': 30,
            'CRYPTO': 40,
            'METALS': 60
        }
    
    async def generate_signals(self, order_books: Dict[str, OrderBook]) -> List[ArbitrageOpportunity]:
        """Generate arbitrage opportunities"""
        start_time = self.latency_profiler.start_timer()
        
        try:
            opportunities = []
            
            # 1. Cross-exchange arbitrage
            cross_market_ops = await self._detect_cross_market_arbitrage(order_books)
            opportunities.extend(cross_market_ops)
            
            # 2. Triangular arbitrage (for forex)
            triangular_ops = await self._detect_triangular_arbitrage(order_books)
            opportunities.extend(triangular_ops)
            
            # 3. Statistical arbitrage
            stat_arb_ops = await self._detect_statistical_arbitrage(order_books)
            opportunities.extend(stat_arb_ops)
            
            # 4. Time-based arbitrage
            time_arbitrage_ops = await self._detect_time_arbitrage(order_books)
            opportunities.extend(time_arbitrage_ops)
            
            # Filter and rank opportunities
            filtered_opportunities = self._filter_opportunities(opportunities)
            
            # Record latency
            self.latency_profiler.end_timer(start_time, "arbitrage.generate_signals")
            
            return filtered_opportunities
            
        except Exception as e:
            self.logger.error(f"Error generating arbitrage signals: {e}")
            self.latency_profiler.end_timer(start_time, "arbitrage.generate_signals")
            return []
    
    async def _detect_cross_market_arbitrage(self, order_books: Dict[str, OrderBook]) -> List[ArbitrageOpportunity]:
        """Detect cross-market arbitrage opportunities"""
        opportunities = []
        
        # Group symbols by asset type
        stocks = [s for s in self.symbols if s in ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']]
        forex = [s for s in self.symbols if '/' in s and len(s.split('/')) == 2]
        
        for symbol_group in [stocks, forex]:
            for symbol in symbol_group:
                if symbol not in order_books:
                    continue
                
                order_book = order_books[symbol]
                best_bid = order_book.get_best_bid()
                best_ask = order_book.get_best_ask()
                
                if best_bid is None or best_ask is None:
                    continue
                
                mid_price = (best_bid + best_ask) / 2
                current_time = time.time()
                
                # Store price history
                if symbol not in self.price_history:
                    self.price_history[symbol] = []
                
                self.price_history[symbol].append((current_time, mid_price))
                
                # Keep only recent prices (last 1000)
                if len(self.price_history[symbol]) > 1000:
                    self.price_history[symbol] = self.price_history[symbol][-500:]
                
                # Check for price volatility arbitrage
                if len(self.price_history[symbol]) >= 10:
                    recent_prices = [p[1] for p in self.price_history[symbol][-10:]]
                    price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
                    
                    # Large price movement arbitrage
                    if abs(price_change) > 0.002:  # 0.2% movement
                        opportunity = ArbitrageOpportunity(
                            symbol=symbol,
                            opportunity_type='price_spread',
                            buy_exchange='PRIMARY',
                            sell_exchange='PRIMARY',
                            buy_price=best_ask,
                            sell_price=best_bid,
                            spread_bps=abs(price_change) * 10000,
                            quantity=self.max_position_size // 10,
                            profit_potential=abs(price_change) * self.max_position_size * mid_price,
                            confidence=min(1.0, abs(price_change) * 100),
                            timestamp=current_time,
                            execution_window=1.0  # 1 second window
                        )
                        opportunities.append(opportunity)
        
        return opportunities
    
    async def _detect_triangular_arbitrage(self, order_books: Dict[str, OrderBook]) -> List[ArbitrageOpportunity]:
        """Detect triangular arbitrage opportunities (primarily for forex)"""
        opportunities = []
        
        # Forex triangular arbitrage: EUR/USD, GBP/USD, EUR/GBP
        forex_triplets = [
            ['EUR/USD', 'GBP/USD', 'EUR/GBP'],
            ['USD/JPY', 'EUR/JPY', 'EUR/USD'],
            ['GBP/JPY', 'GBP/USD', 'USD/JPY']
        ]
        
        for triplet in forex_triplets:
            if all(symbol in order_books for symbol in triplet):
                opportunity = await self._analyze_triangular_opportunity(triplet, order_books)
                if opportunity:
                    opportunities.append(opportunity)
        
        # Crypto triangular arbitrage
        crypto_triplets = [
            ['BTC/USD', 'ETH/USD', 'BTC/ETH'],
            ['ETH/USD', 'ADA/USD', 'ETH/ADA']
        ]
        
        for triplet in crypto_triplets:
            if all(symbol in order_books for symbol in triplet):
                opportunity = await self._analyze_triangular_opportunity(triplet, order_books)
                if opportunity:
                    opportunities.append(opportunity)
        
        return opportunities
    
    async def _analyze_triangular_opportunity(self, triplet: List[str], order_books: Dict[str, OrderBook]) -> Optional[ArbitrageOpportunity]:
        """Analyze triangular arbitrage for a triplet of symbols"""
        try:
            prices = {}
            spreads = {}
            
            for symbol in triplet:
                order_book = order_books[symbol]
                best_bid = order_book.get_best_bid()
                best_ask = order_book.get_best_ask()
                
                if best_bid is None or best_ask is None:
                    return None
                
                prices[symbol] = (best_bid + best_ask) / 2
                spreads[symbol] = best_ask - best_bid
            
            # Calculate theoretical triangular arbitrage
            if 'EUR/USD' in triplet and 'GBP/USD' in triplet and 'EUR/GBP' in triplet:
                # EUR/USD, GBP/USD, EUR/GBP
                theoretical_eur_gbp = prices['EUR/USD'] / prices['GBP/USD']
                actual_eur_gbp = prices['EUR/GBP']
                discrepancy = (actual_eur_gbp - theoretical_eur_gbp) / theoretical_eur_gbp
                
                if abs(discrepancy) > 0.0005:  # 5 basis points
                    quantity = self.max_position_size // 10
                    profit = abs(discrepancy) * quantity * prices['EUR/USD']
                    
                    return ArbitrageOpportunity(
                        symbol=f"TRI_{triplet[0]}_{triplet[1]}_{triplet[2]}",
                        opportunity_type='triangular',
                        buy_exchange='FOREX',
                        sell_exchange='FOREX',
                        buy_price=prices[min(triplet, key=lambda x: prices[x])],
                        sell_price=prices[max(triplet, key=lambda x: prices[x])],
                        spread_bps=abs(discrepancy) * 10000,
                        quantity=quantity,
                        profit_potential=profit,
                        confidence=min(1.0, abs(discrepancy) * 1000),
                        timestamp=time.time(),
                        execution_window=2.0
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing triangular opportunity: {e}")
            return None
    
    async def _detect_statistical_arbitrage(self, order_books: Dict[str, OrderBook]) -> List[ArbitrageOpportunity]:
        """Detect statistical arbitrage opportunities"""
        opportunities = []
        
        # Stock pairs for pairs trading
        stock_pairs = [
            ('AAPL', 'MSFT'),
            ('GOOGL', 'META'),
            ('TSLA', 'RIVN')
        ]
        
        for pair in stock_pairs:
            if all(symbol in order_books for symbol in pair):
                opportunity = await self._analyze_pairs_opportunity(pair, order_books)
                if opportunity:
                    opportunities.append(opportunity)
        
        # Crypto pairs
        crypto_pairs = [
            ('BTC/USD', 'ETH/USD')
        ]
        
        for pair in crypto_pairs:
            if all(symbol in order_books for symbol in pair):
                opportunity = await self._analyze_pairs_opportunity(pair, order_books)
                if opportunity:
                    opportunities.append(opportunity)
        
        return opportunities
    
    async def _analyze_pairs_opportunity(self, pair: Tuple[str, str], order_books: Dict[str, OrderBook]) -> Optional[ArbitrageOpportunity]:
        """Analyze pairs trading opportunity"""
        try:
            symbol1, symbol2 = pair
            prices = {}
            
            for symbol in pair:
                order_book = order_books[symbol]
                best_bid = order_book.get_best_bid()
                best_ask = order_book.get_best_ask()
                
                if best_bid is None or best_ask is None:
                    return None
                
                prices[symbol] = (best_bid + best_ask) / 2
            
            # Calculate price ratio
            ratio = prices[symbol1] / prices[symbol2]
            
            # Check if we have historical ratio data
            ratio_key = f"{symbol1}_{symbol2}"
            if ratio_key not in self.market_correlations:
                self.market_correlations[ratio_key] = MarketCorrelation(
                    symbol1=symbol1,
                    symbol2=symbol2,
                    correlation=0.8,  # Default correlation
                    last_updated=time.time()
                )
            
            correlation_data = self.market_correlations[ratio_key]
            
            # Simplified z-score calculation
            if len(self.price_history.get(symbol1, [])) >= 20 and len(self.price_history.get(symbol2, [])) >= 20:
                recent_ratios = []
                for i in range(-20, 0):
                    if i < len(self.price_history.get(symbol1, [])) and i < len(self.price_history.get(symbol2, [])):
                        p1 = self.price_history[symbol1][i][1]
                        p2 = self.price_history[symbol2][i][1]
                        if p2 != 0:
                            recent_ratios.append(p1 / p2)
                
                if recent_ratios:
                    mean_ratio = np.mean(recent_ratios)
                    std_ratio = np.std(recent_ratios)
                    
                    if std_ratio > 0:
                        z_score = (ratio - mean_ratio) / std_ratio
                        
                        # Generate signal if z-score is extreme
                        if abs(z_score) > 2.0:  # 2 standard deviations
                            quantity = self.max_position_size // 20
                            spread_bps = abs(z_score) * 100
                            
                            return ArbitrageOpportunity(
                                symbol=f"PAIRS_{symbol1}_{symbol2}",
                                opportunity_type='statistical',
                                buy_exchange='PRIMARY',
                                sell_exchange='PRIMARY',
                                buy_price=prices[symbol1] if z_score < 0 else prices[symbol2],
                                sell_price=prices[symbol2] if z_score < 0 else prices[symbol1],
                                spread_bps=spread_bps,
                                quantity=quantity,
                                profit_potential=abs(z_score) * quantity * min(prices.values()),
                                confidence=min(1.0, abs(z_score) / 3.0),
                                timestamp=time.time(),
                                execution_window=10.0
                            )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing pairs opportunity: {e}")
            return None
    
    async def _detect_time_arbitrage(self, order_books: Dict[str, OrderBook]) -> List[ArbitrageOpportunity]:
        """Detect time-based arbitrage opportunities"""
        opportunities = []
        
        current_time = time.time()
        
        # Market opening/closing arbitrage (simplified simulation)
        for symbol in self.symbols:
            if symbol in order_books:
                order_book = order_books[symbol]
                best_bid = order_book.get_best_bid()
                best_ask = order_book.get_best_ask()
                
                if best_bid is None or best_ask is None:
                    continue
                
                # Simulate market opening/closing gaps
                gap_multiplier = 1.0
                if 9.5 <= (current_time % 86400) / 3600 <= 10.5:  # Market open hour
                    gap_multiplier = 1.5
                elif 15.5 <= (current_time % 86400) / 3600 <= 16.5:  # Market close hour
                    gap_multiplier = 1.3
                
                mid_price = (best_bid + best_ask) / 2
                spread = best_ask - best_bid
                
                if spread * gap_multiplier > mid_price * 0.001:  # Significant spread increase
                    opportunity = ArbitrageOpportunity(
                        symbol=symbol,
                        opportunity_type='time_arbitrage',
                        buy_exchange='PRIMARY',
                        sell_exchange='PRIMARY',
                        buy_price=best_ask,
                        sell_price=best_bid,
                        spread_bps=(spread * gap_multiplier / mid_price) * 10000,
                        quantity=self.max_position_size // 15,
                        profit_potential=spread * gap_multiplier * self.max_position_size // 15,
                        confidence=0.7,
                        timestamp=current_time,
                        execution_window=30.0
                    )
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _filter_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """Filter and rank arbitrage opportunities"""
        # Filter by minimum spread
        filtered = [
            op for op in opportunities 
            if op.spread_bps >= self.min_spread_bps
        ]
        
        # Sort by profit potential (descending)
        filtered.sort(key=lambda x: x.profit_potential, reverse=True)
        
        # Limit number of opportunities
        max_opportunities = self.config.get('max_opportunities', 20)
        return filtered[:max_opportunities]
    
    def update_price_history(self, symbol: str, price: float):
        """Update price history for correlation analysis"""
        with self.lock:
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            
            self.price_history[symbol].append((time.time(), price))
            
            # Keep only recent data
            if len(self.price_history[symbol]) > 2000:
                self.price_history[symbol] = self.price_history[symbol][-1000:]
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """Get strategy status and performance"""
        with self.lock:
            return {
                'strategy': 'arbitrage',
                'active_opportunities': len(self.active_opportunities),
                'price_history_symbols': len(self.price_history),
                'market_correlations': len(self.market_correlations),
                'latency_stats': self.latency_profiler.get_stats(),
                'exchange_latencies': self.exchange_latencies.copy(),
                'recent_opportunities': len([op for op in self.active_opportunities if time.time() - op.timestamp < 60])
            }
    
    def get_update_interval(self) -> float:
        """Get strategy update interval"""
        return 0.005  # 5ms for high-frequency arbitrage detection
    
    async def shutdown(self):
        """Shutdown strategy"""
        self.logger.info("Shutting down Arbitrage Strategy")
        # Clear active opportunities
        with self.lock:
            self.active_opportunities.clear()
        pass