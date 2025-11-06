"""
HFT Core Engine
==============

Microsecond-level latency HFT trading engine
Optimized for high-performance trading operations
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock

from .orderbook import OrderBook
from .market_data import MarketDataFeed
from .order_manager import OrderManager
from .latency_profiler import LatencyProfiler

@dataclass
class TradingSignal:
    """Trading signal structure"""
    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float
    price: float
    quantity: int
    timestamp: float
    strategy: str

class HFTEngine:
    """
    High-Frequency Trading Engine
    
    Main orchestrator for all HFT operations with microsecond-level latency
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.market_data_feed = None
        self.order_manager = None
        self.order_books: Dict[str, OrderBook] = {}
        self.strategies = {}
        self.risk_manager = None
        
        # Performance monitoring
        self.latency_profiler = LatencyProfiler()
        self.engine_lock = Lock()
        
        # Trading state
        self.is_running = False
        self.active_positions: Dict[str, float] = {}
        self.pnl_tracker = {}
        
        # Asset symbols
        self.stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
        self.forex_symbols = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF']
        self.metals_symbols = ['XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD']
        self.crypto_symbols = ['BTC/USD', 'ETH/USD']
        
        self.all_symbols = (
            self.stock_symbols + self.forex_symbols + 
            self.metals_symbols + self.crypto_symbols
        )
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=16)
        
    async def initialize(self) -> bool:
        """Initialize all HFT components"""
        try:
            self.logger.info("Initializing HFT Engine...")
            
            # Initialize market data feed
            self.market_data_feed = MarketDataFeed(self.all_symbols, self.config)
            await self.market_data_feed.initialize()
            
            # Initialize order manager
            self.order_manager = OrderManager(self.config)
            await self.order_manager.initialize()
            
            # Initialize order books for all symbols
            for symbol in self.all_symbols:
                self.order_books[symbol] = OrderBook(symbol)
                
            # Initialize risk manager
            from ..risk.risk_manager import RiskManager
            self.risk_manager = RiskManager(self.config)
            await self.risk_manager.initialize()
            
            # Load trading strategies
            await self._load_strategies()
            
            self.logger.info("HFT Engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize HFT Engine: {e}")
            return False
    
    async def _load_strategies(self):
        """Load all trading strategies"""
        from ..strategies.market_making import MarketMakingStrategy
        from ..strategies.arbitrage import ArbitrageStrategy
        from ..strategies.statistical_arbitrage import StatisticalArbitrageStrategy
        
        # Market Making Strategy
        self.strategies['market_making'] = MarketMakingStrategy(
            symbols=self.all_symbols,
            config=self.config.get('market_making', {})
        )
        
        # Arbitrage Strategy
        self.strategies['arbitrage'] = ArbitrageStrategy(
            symbols=self.all_symbols,
            config=self.config.get('arbitrage', {})
        )
        
        # Statistical Arbitrage Strategy
        self.strategies['stat_arb'] = StatisticalArbitrageStrategy(
            symbols=self.all_symbols,
            config=self.config.get('stat_arb', {})
        )
    
    async def start(self):
        """Start the HFT trading engine"""
        if self.is_running:
            self.logger.warning("HFT Engine is already running")
            return
            
        self.logger.info("Starting HFT Trading Engine...")
        self.is_running = True
        
        # Start market data feed
        await self.market_data_feed.start()
        
        # Start order manager
        await self.order_manager.start()
        
        # Start strategy execution tasks
        strategy_tasks = []
        for strategy_name, strategy in self.strategies.items():
            task = asyncio.create_task(self._run_strategy(strategy_name, strategy))
            strategy_tasks.append(task)
        
        # Start main trading loop
        trading_task = asyncio.create_task(self._trading_loop())
        
        self.logger.info("HFT Engine started successfully")
        
        # Wait for all tasks
        try:
            await asyncio.gather(*strategy_tasks, trading_task)
        except asyncio.CancelledError:
            self.logger.info("HFT Engine tasks cancelled")
        except Exception as e:
            self.logger.error(f"Error in HFT Engine: {e}")
        finally:
            await self.shutdown()
    
    async def _run_strategy(self, strategy_name: str, strategy):
        """Run individual trading strategy"""
        self.logger.info(f"Starting strategy: {strategy_name}")
        
        while self.is_running:
            try:
                start_time = time.perf_counter()
                
                # Generate signals from strategy
                signals = await strategy.generate_signals(self.order_books)
                
                # Process signals
                for signal in signals:
                    await self._process_trading_signal(signal)
                
                # Calculate strategy latency
                end_time = time.perf_counter()
                latency = (end_time - start_time) * 1_000_000  # Convert to microseconds
                self.latency_profiler.record_strategy_latency(strategy_name, latency)
                
                # Strategy-specific sleep
                await asyncio.sleep(strategy.get_update_interval())
                
            except Exception as e:
                self.logger.error(f"Error in strategy {strategy_name}: {e}")
                await asyncio.sleep(0.001)  # Brief pause before retry
    
    async def _trading_loop(self):
        """Main trading loop"""
        self.logger.info("Starting main trading loop")
        
        while self.is_running:
            try:
                loop_start = time.perf_counter()
                
                # Update order books
                await self._update_order_books()
                
                # Risk management check
                await self._risk_management_check()
                
                # Update positions and PnL
                await self._update_positions()
                
                # Performance monitoring
                loop_end = time.perf_counter()
                loop_latency = (loop_end - loop_start) * 1_000_000
                self.latency_profiler.record_trading_loop_latency(loop_latency)
                
                # Minimal sleep to maintain latency
                await asyncio.sleep(0.000001)  # 1 microsecond
                
            except Exception as e:
                self.logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(0.001)
    
    async def _process_trading_signal(self, signal: TradingSignal):
        """Process individual trading signal"""
        try:
            # Risk check
            if not await self.risk_manager.check_signal(signal):
                return
            
            # Execute order
            order_result = await self.order_manager.execute_order(
                symbol=signal.symbol,
                side=signal.signal_type,
                quantity=signal.quantity,
                price=signal.price
            )
            
            # Update positions
            if order_result.success:
                self.active_positions[signal.symbol] = (
                    self.active_positions.get(signal.symbol, 0) + 
                    (signal.quantity if signal.signal_type == 'BUY' else -signal.quantity)
                )
                
                self.logger.info(
                    f"Signal executed: {signal.symbol} {signal.signal_type} "
                    f"{signal.quantity} @ {signal.price}"
                )
            
        except Exception as e:
            self.logger.error(f"Error processing signal: {e}")
    
    async def _update_order_books(self):
        """Update all order books with latest market data"""
        update_tasks = []
        for symbol, order_book in self.order_books.items():
            task = asyncio.create_task(order_book.update_from_feed(
                self.market_data_feed.get_latest_data(symbol)
            ))
            update_tasks.append(task)
        
        if update_tasks:
            await asyncio.gather(*update_tasks, return_exceptions=True)
    
    async def _risk_management_check(self):
        """Perform risk management checks"""
        try:
            await self.risk_manager.check_portfolio_risk(
                positions=self.active_positions,
                order_books=self.order_books
            )
        except Exception as e:
            self.logger.error(f"Risk management check failed: {e}")
    
    async def _update_positions(self):
        """Update current positions and PnL"""
        for symbol in self.all_symbols:
            try:
                current_price = self.market_data_feed.get_latest_price(symbol)
                if current_price:
                    position = self.active_positions.get(symbol, 0)
                    if symbol not in self.pnl_tracker:
                        self.pnl_tracker[symbol] = {'realized': 0, 'unrealized': 0}
                    
                    self.pnl_tracker[symbol]['unrealized'] = position * current_price
            except Exception as e:
                self.logger.error(f"Error updating position for {symbol}: {e}")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            'latency_stats': self.latency_profiler.get_stats(),
            'active_positions': self.active_positions.copy(),
            'pnl': self.pnl_tracker.copy(),
            'order_books_status': {
                symbol: ob.get_book_stats() 
                for symbol, ob in self.order_books.items()
            },
            'strategies_status': {
                name: strategy.get_status() 
                for name, strategy in self.strategies.items()
            }
        }
    
    async def shutdown(self):
        """Shutdown the HFT engine"""
        self.logger.info("Shutting down HFT Engine...")
        self.is_running = False
        
        # Shutdown strategies
        for strategy_name, strategy in self.strategies.items():
            try:
                await strategy.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down strategy {strategy_name}: {e}")
        
        # Shutdown components
        if self.market_data_feed:
            await self.market_data_feed.shutdown()
        
        if self.order_manager:
            await self.order_manager.shutdown()
        
        if self.risk_manager:
            await self.risk_manager.shutdown()
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        self.logger.info("HFT Engine shutdown complete")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get engine health status"""
        return {
            'is_running': self.is_running,
            'active_symbols': len(self.order_books),
            'loaded_strategies': len(self.strategies),
            'total_positions': len(self.active_positions),
            'last_trade_time': time.time(),
            'system_load': self.latency_profiler.get_current_load()
        }