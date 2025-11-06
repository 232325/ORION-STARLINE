"""
Market Data Feed System
======================

High-performance market data feed with microsecond-level latency
Optimized for real-time market data processing and distribution
"""

import asyncio
import time
import logging
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from threading import Thread, Lock
from queue import Queue, Empty
import zlib

@dataclass
class TickData:
    """Individual market tick"""
    symbol: str
    timestamp: float
    bid: float
    ask: float
    last: float
    volume: int
    bid_size: int
    ask_size: int
    trade_count: int
    
    @property
    def mid_price(self) -> float:
        return (self.bid + self.ask) / 2
    
    @property
    def spread(self) -> float:
        return self.ask - self.bid
    
    @property
    def spread_bps(self) -> float:
        if self.mid_price > 0:
            return (self.spread / self.mid_price) * 10000
        return 0

@dataclass
class BarData:
    """OHLCV bar data"""
    symbol: str
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    interval: str  # 1m, 5m, 1h, 1d

class MarketDataFeed:
    """
    High-Performance Market Data Feed
    
    Handles real-time market data with minimal latency
    """
    
    def __init__(self, symbols: List[str], config: Dict[str, Any]):
        self.symbols = symbols
        self.config = config
        
        # Data storage
        self.latest_ticks: Dict[str, TickData] = {}
        self.tick_history: Dict[str, List[TickData]] = {}
        self.bar_data: Dict[str, List[BarData]] = {}
        
        # Performance tracking
        self.received_ticks = 0
        self.processed_ticks = 0
        self.last_tick_time = 0.0
        self.tick_latencies = []
        self.lock = Lock()
        
        # Callbacks
        self.tick_callbacks: List[Callable[[TickData], None]] = []
        self.symbol_callbacks: Dict[str, List[Callable[[TickData], None]]] = {}
        
        # Threading
        self.is_running = False
        self.feed_thread = None
        self.data_queue = Queue(maxsize=10000)
        
        # Network optimization settings
        self.use_compression = config.get('compress_data', True)
        self.batch_size = config.get('batch_size', 100)
        self.update_frequency = config.get('update_frequency', 1000)  # Hz
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize callbacks for all symbols
        for symbol in symbols:
            self.symbol_callbacks[symbol] = []
            self.tick_history[symbol] = []
    
    async def initialize(self) -> bool:
        """Initialize market data feed"""
        try:
            self.logger.info(f"Initializing market data feed for {len(self.symbols)} symbols")
            
            # Initialize data structures
            for symbol in self.symbols:
                self.latest_ticks[symbol] = None
                self.bar_data[symbol] = []
            
            # Initialize mock data generators for different asset classes
            await self._initialize_data_generators()
            
            self.logger.info("Market data feed initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize market data feed: {e}")
            return False
    
    async def _initialize_data_generators(self):
        """Initialize data generators for different asset classes"""
        
        # Mock data generator for simulation
        self.data_generators = {
            'AAPL': self._generate_stock_data,
            'GOOGL': self._generate_stock_data,
            'MSFT': self._generate_stock_data,
            'TSLA': self._generate_stock_data,
            'NVDA': self._generate_stock_data,
            'EUR/USD': self._generate_forex_data,
            'GBP/USD': self._generate_forex_data,
            'USD/JPY': self._generate_forex_data,
            'USD/CHF': self._generate_forex_data,
            'XAU/USD': self._generate_metals_data,
            'XAG/USD': self._generate_metals_data,
            'XPT/USD': self._generate_metals_data,
            'XPD/USD': self._generate_metals_data,
            'BTC/USD': self._generate_crypto_data,
            'ETH/USD': self._generate_crypto_data
        }
    
    async def start(self):
        """Start the market data feed"""
        if self.is_running:
            return
        
        self.logger.info("Starting market data feed...")
        self.is_running = True
        
        # Start feed thread
        self.feed_thread = Thread(target=self._feed_worker, daemon=True)
        self.feed_thread.start()
        
        self.logger.info("Market data feed started")
    
    def _feed_worker(self):
        """Worker thread for processing market data"""
        self.logger.info("Market data feed worker started")
        
        # Simulate market data generation
        current_prices = self._initialize_prices()
        
        while self.is_running:
            try:
                start_time = time.perf_counter()
                
                # Generate data for each symbol
                for symbol in self.symbols:
                    if symbol in self.data_generators:
                        tick = self.data_generators[symbol](symbol, current_prices[symbol])
                        
                        # Update current price
                        current_prices[symbol] = tick.last
                        
                        # Add to queue
                        try:
                            if self.use_compression:
                                compressed_data = zlib.compress(json.dumps(asdict(tick)).encode())
                                self.data_queue.put((symbol, compressed_data), timeout=0.001)
                            else:
                                self.data_queue.put((symbol, tick), timeout=0.001)
                        except:
                            pass  # Queue full, skip this tick
                
                # Process queued data
                self._process_data_queue()
                
                # Control frequency
                elapsed = time.perf_counter() - start_time
                sleep_time = max(0, (1.0 / self.update_frequency) - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error in feed worker: {e}")
                time.sleep(0.001)
        
        self.logger.info("Market data feed worker stopped")
    
    def _initialize_prices(self) -> Dict[str, float]:
        """Initialize base prices for all symbols"""
        base_prices = {}
        
        # Stock prices (realistic values)
        base_prices.update({
            'AAPL': 150.0,
            'GOOGL': 2800.0,
            'MSFT': 320.0,
            'TSLA': 200.0,
            'NVDA': 800.0
        })
        
        # Forex rates
        base_prices.update({
            'EUR/USD': 1.1000,
            'GBP/USD': 1.3500,
            'USD/JPY': 110.00,
            'USD/CHF': 0.9200
        })
        
        # Metals prices
        base_prices.update({
            'XAU/USD': 1800.0,  # Gold
            'XAG/USD': 25.0,    # Silver
            'XPT/USD': 1200.0,  # Platinum
            'XPD/USD': 2800.0   # Palladium
        })
        
        # Crypto prices
        base_prices.update({
            'BTC/USD': 45000.0,
            'ETH/USD': 3000.0
        })
        
        return base_prices
    
    def _generate_stock_data(self, symbol: str, current_price: float) -> TickData:
        """Generate realistic stock data"""
        import random
        
        # Simulate price movement
        change_pct = random.gauss(0, 0.001)  # 0.1% volatility
        new_price = current_price * (1 + change_pct)
        
        # Realistic spreads for stocks (in basis points)
        spread_bps = random.uniform(1, 10)  # 1-10 bps
        spread = (new_price * spread_bps) / 10000
        
        bid = new_price - spread / 2
        ask = new_price + spread / 2
        
        return TickData(
            symbol=symbol,
            timestamp=time.time(),
            bid=round(bid, 2),
            ask=round(ask, 2),
            last=round(new_price, 2),
            volume=random.randint(100, 10000),
            bid_size=random.randint(1, 1000),
            ask_size=random.randint(1, 1000),
            trade_count=random.randint(1, 50)
        )
    
    def _generate_forex_data(self, symbol: str, current_price: float) -> TickData:
        """Generate realistic forex data"""
        import random
        
        # Forex typically has lower volatility
        change_pct = random.gauss(0, 0.0005)  # 0.05% volatility
        new_price = current_price * (1 + change_pct)
        
        # Forex spreads are smaller
        spread_bps = random.uniform(0.5, 3)  # 0.5-3 bps
        spread = (new_price * spread_bps) / 10000
        
        bid = new_price - spread / 2
        ask = new_price + spread / 2
        
        return TickData(
            symbol=symbol,
            timestamp=time.time(),
            bid=round(bid, 5),
            ask=round(ask, 5),
            last=round(new_price, 5),
            volume=random.randint(1000, 100000),
            bid_size=random.randint(1, 10000),
            ask_size=random.randint(1, 10000),
            trade_count=random.randint(10, 200)
        )
    
    def _generate_metals_data(self, symbol: str, current_price: float) -> TickData:
        """Generate realistic metals data"""
        import random
        
        change_pct = random.gauss(0, 0.002)  # 0.2% volatility
        new_price = current_price * (1 + change_pct)
        
        spread_bps = random.uniform(2, 15)  # 2-15 bps
        spread = (new_price * spread_bps) / 10000
        
        bid = new_price - spread / 2
        ask = new_price + spread / 2
        
        return TickData(
            symbol=symbol,
            timestamp=time.time(),
            bid=round(bid, 2),
            ask=round(ask, 2),
            last=round(new_price, 2),
            volume=random.randint(500, 50000),
            bid_size=random.randint(1, 5000),
            ask_size=random.randint(1, 5000),
            trade_count=random.randint(5, 100)
        )
    
    def _generate_crypto_data(self, symbol: str, current_price: float) -> TickData:
        """Generate realistic crypto data"""
        import random
        
        # Crypto has higher volatility
        change_pct = random.gauss(0, 0.005)  # 0.5% volatility
        new_price = current_price * (1 + change_pct)
        
        # Crypto spreads vary widely
        spread_bps = random.uniform(5, 50)  # 5-50 bps
        spread = (new_price * spread_bps) / 10000
        
        bid = new_price - spread / 2
        ask = new_price + spread / 2
        
        return TickData(
            symbol=symbol,
            timestamp=time.time(),
            bid=round(bid, 2),
            ask=round(ask, 2),
            last=round(new_price, 2),
            volume=random.randint(100, 50000),
            bid_size=random.randint(1, 1000),
            ask_size=random.randint(1, 1000),
            trade_count=random.randint(1, 100)
        )
    
    def _process_data_queue(self):
        """Process queued market data"""
        processed_count = 0
        
        try:
            while processed_count < self.batch_size:
                try:
                    symbol, data = self.data_queue.get(timeout=0.001)
                    
                    # Decompress if needed
                    if self.use_compression:
                        if isinstance(data, bytes):
                            decompressed = zlib.decompress(data).decode()
                            tick_data = json.loads(decompressed)
                            tick = TickData(**tick_data)
                        else:
                            continue
                    else:
                        tick = data
                    
                    # Process tick
                    self._process_tick(tick)
                    processed_count += 1
                    
                except Empty:
                    break
                except Exception as e:
                    self.logger.error(f"Error processing queue item: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error processing data queue: {e}")
    
    def _process_tick(self, tick: TickData):
        """Process individual tick data"""
        with self.lock:
            start_time = time.perf_counter()
            
            try:
                # Update latest tick
                self.latest_ticks[tick.symbol] = tick
                
                # Add to history
                self.tick_history[tick.symbol].append(tick)
                
                # Keep history size manageable
                if len(self.tick_history[tick.symbol]) > 10000:
                    self.tick_history[tick.symbol] = self.tick_history[tick.symbol][-5000:]
                
                # Generate bars if needed
                self._update_bars(tick)
                
                # Call callbacks
                for callback in self.tick_callbacks:
                    try:
                        callback(tick)
                    except Exception as e:
                        self.logger.error(f"Error in tick callback: {e}")
                
                # Symbol-specific callbacks
                for callback in self.symbol_callbacks.get(tick.symbol, []):
                    try:
                        callback(tick)
                    except Exception as e:
                        self.logger.error(f"Error in symbol callback: {e}")
                
                # Update statistics
                self.received_ticks += 1
                self.processed_ticks += 1
                self.last_tick_time = tick.timestamp
                
                # Record latency
                process_time = time.perf_counter() - start_time
                if len(self.tick_latencies) < 1000:
                    self.tick_latencies.append(process_time * 1_000_000)  # Convert to microseconds
                else:
                    self.tick_latencies.pop(0)
                    self.tick_latencies.append(process_time * 1_000_000)
                
            except Exception as e:
                self.logger.error(f"Error processing tick: {e}")
    
    def _update_bars(self, tick: TickData):
        """Update OHLCV bars"""
        # This is a simplified implementation
        # In a real system, this would be more sophisticated
        symbol_bars = self.bar_data.get(tick.symbol, [])
        
        # Get or create current minute bar
        current_minute = int(tick.timestamp // 60) * 60
        
        if symbol_bars:
            last_bar = symbol_bars[-1]
            if int(last_bar.timestamp // 60) == current_minute:
                # Update existing bar
                last_bar.high = max(last_bar.high, tick.last)
                last_bar.low = min(last_bar.low, tick.last)
                last_bar.close = tick.last
                last_bar.volume += tick.volume
            else:
                # Create new bar
                new_bar = BarData(
                    symbol=tick.symbol,
                    timestamp=current_minute,
                    open=tick.last,
                    high=tick.last,
                    low=tick.last,
                    close=tick.last,
                    volume=tick.volume,
                    interval='1m'
                )
                symbol_bars.append(new_bar)
        else:
            # Create first bar
            new_bar = BarData(
                symbol=tick.symbol,
                timestamp=current_minute,
                open=tick.last,
                high=tick.last,
                low=tick.last,
                close=tick.last,
                volume=tick.volume,
                interval='1m'
            )
            symbol_bars.append(new_bar)
        
        # Keep only recent bars
        if len(symbol_bars) > 1000:
            self.bar_data[tick.symbol] = symbol_bars[-500:]
    
    def subscribe_tick(self, callback: Callable[[TickData], None]):
        """Subscribe to all tick data"""
        self.tick_callbacks.append(callback)
    
    def subscribe_symbol(self, symbol: str, callback: Callable[[TickData], None]):
        """Subscribe to specific symbol data"""
        if symbol in self.symbol_callbacks:
            self.symbol_callbacks[symbol].append(callback)
    
    def get_latest_tick(self, symbol: str) -> Optional[TickData]:
        """Get latest tick for symbol"""
        with self.lock:
            return self.latest_ticks.get(symbol)
    
    def get_latest_data(self, symbol: str) -> Optional[Dict]:
        """Get latest market data for symbol"""
        tick = self.get_latest_tick(symbol)
        if tick:
            return asdict(tick)
        return None
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest price for symbol"""
        tick = self.get_latest_tick(symbol)
        return tick.last if tick else None
    
    def get_tick_history(self, symbol: str, limit: int = 100) -> List[TickData]:
        """Get tick history for symbol"""
        with self.lock:
            return self.tick_history.get(symbol, [])[-limit:]
    
    def get_bar_data(self, symbol: str, interval: str = '1m', limit: int = 100) -> List[BarData]:
        """Get bar data for symbol"""
        bars = self.bar_data.get(symbol, [])
        filtered_bars = [bar for bar in bars if bar.interval == interval]
        return filtered_bars[-limit:]
    
    def get_feed_statistics(self) -> Dict[str, Any]:
        """Get feed performance statistics"""
        with self.lock:
            avg_latency = sum(self.tick_latencies) / len(self.tick_latencies) if self.tick_latencies else 0
            max_latency = max(self.tick_latencies) if self.tick_latencies else 0
            
            return {
                'is_running': self.is_running,
                'received_ticks': self.received_ticks,
                'processed_ticks': self.processed_ticks,
                'last_tick_time': self.last_tick_time,
                'avg_latency_us': avg_latency,
                'max_latency_us': max_latency,
                'queue_size': self.data_queue.qsize(),
                'symbols_count': len(self.symbols)
            }
    
    async def shutdown(self):
        """Shutdown the market data feed"""
        self.logger.info("Shutting down market data feed...")
        self.is_running = False
        
        if self.feed_thread and self.feed_thread.is_alive():
            self.feed_thread.join(timeout=1.0)
        
        # Clear queues and data
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
            except Empty:
                break
        
        self.logger.info("Market data feed shutdown complete")