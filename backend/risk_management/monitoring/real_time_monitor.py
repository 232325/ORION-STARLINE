"""
Real-Time Risk Monitoring System
===============================

Provides continuous real-time monitoring of portfolio risk metrics,
position changes, and market conditions.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque
import json

logger = logging.getLogger(__name__)

@dataclass
class MarketUpdate:
    """Market data update structure"""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    bid: float = 0.0
    ask: float = 0.0
    spread: float = 0.0
    liquidity_score: float = 1.0

@dataclass
class RiskThreshold:
    """Risk threshold definition for monitoring"""
    metric_name: str
    threshold_value: float
    comparison_operator: str  # 'gt', 'lt', 'eq'
    severity: str  # 'info', 'warning', 'error', 'critical'
    asset_class: str = "all"
    symbol: str = "all"

@dataclass
class RiskEvent:
    """Risk event detected by monitoring system"""
    event_type: str
    severity: str
    timestamp: datetime
    symbol: Optional[str] = None
    metric_value: float = 0.0
    threshold: float = 0.0
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

class RealTimeMonitor:
    """
    Real-time risk monitoring system
    
    Continuously monitors:
    - Market data updates
    - Position changes
    - Risk metric thresholds
    - Portfolio exposures
    - Liquidity conditions
    - Market volatility
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        
        # Market data storage
        self.market_data: Dict[str, MarketUpdate] = {}
        self.market_history: Dict[str, deque] = {}
        self.market_updates: deque = deque(maxlen=10000)
        
        # Monitoring state
        self.risk_thresholds: List[RiskThreshold] = []
        self.monitoring_active = False
        self.last_update = None
        
        # Event tracking
        self.risk_events: deque = deque(maxlen=1000)
        self.event_counts: Dict[str, int] = {}
        
        # Callback handlers
        self.position_callbacks: List[Callable] = []
        self.portfolio_callbacks: List[Callable] = []
        self.market_callbacks: List[Callable] = []
        self.risk_callbacks: List[Callable] = []
        
        # Configuration
        self.update_interval = config.get('update_interval', 1.0)  # seconds
        self.market_data_ttl = config.get('market_data_ttl', 60)  # seconds
        self.max_events_per_minute = config.get('max_events_per_minute', 100)
        
        # Performance tracking
        self.performance_metrics = {
            'updates_processed': 0,
            'events_generated': 0,
            'avg_response_time': 0.0,
            'last_performance_check': datetime.now()
        }
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
    
    def _initialize_default_thresholds(self):
        """Initialize default risk monitoring thresholds"""
        
        # Price movement thresholds
        self.add_threshold(RiskThreshold(
            metric_name="price_change_pct",
            threshold_value=0.05,  # 5% price change
            comparison_operator="gt",
            severity="warning",
            description="Rapid price movement detected"
        ))
        
        # Volume thresholds
        self.add_threshold(RiskThreshold(
            metric_name="volume_spike",
            threshold_value=2.0,  # 2x normal volume
            comparison_operator="gt",
            severity="warning",
            description="Unusual volume spike detected"
        ))
        
        # Spread thresholds
        self.add_threshold(RiskThreshold(
            metric_name="bid_ask_spread",
            threshold_value=0.01,  # 1% spread
            comparison_operator="gt",
            severity="info",
            description="Wide bid-ask spread detected"
        ))
        
        # Liquidity thresholds
        self.add_threshold(RiskThreshold(
            metric_name="liquidity_score",
            threshold_value=0.1,  # Low liquidity score
            comparison_operator="lt",
            severity="warning",
            description="Low liquidity detected"
        ))
        
        # Portfolio exposure thresholds
        self.add_threshold(RiskThreshold(
            metric_name="sector_concentration",
            threshold_value=0.30,  # 30% sector concentration
            comparison_operator="gt",
            severity="error",
            description="High sector concentration detected"
        ))
        
        logger.info(f"Initialized {len(self.risk_thresholds)} default risk thresholds")
    
    def add_threshold(self, threshold: RiskThreshold):
        """Add a new risk threshold"""
        self.risk_thresholds.append(threshold)
        logger.debug(f"Added risk threshold: {threshold.metric_name}")
    
    def remove_threshold(self, metric_name: str, asset_class: str = "all") -> bool:
        """Remove risk threshold by name and asset class"""
        original_count = len(self.risk_thresholds)
        self.risk_thresholds = [
            t for t in self.risk_thresholds 
            if not (t.metric_name == metric_name and t.asset_class == asset_class)
        ]
        
        if len(self.risk_thresholds) < original_count:
            logger.info(f"Removed risk threshold: {metric_name}")
            return True
        return False
    
    def add_position_callback(self, callback: Callable):
        """Add callback for position updates"""
        self.position_callbacks.append(callback)
    
    def add_portfolio_callback(self, callback: Callable):
        """Add callback for portfolio updates"""
        self.portfolio_callbacks.append(callback)
    
    def add_market_callback(self, callback: Callable):
        """Add callback for market updates"""
        self.market_callbacks.append(callback)
    
    def add_risk_callback(self, callback: Callable):
        """Add callback for risk events"""
        self.risk_callbacks.append(callback)
    
    async def start(self):
        """Start real-time monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitoring_active = True
        
        logger.info("Starting real-time risk monitoring...")
        
        # Start monitoring tasks
        asyncio.create_task(self._market_data_monitoring_loop())
        asyncio.create_task(self._risk_threshold_monitoring_loop())
        asyncio.create_task(self._performance_monitoring_loop())
        
        # Start market data simulation (in real implementation, this would connect to data feeds)
        asyncio.create_task(self._market_data_simulation_loop())
        
    async def stop(self):
        """Stop real-time monitoring"""
        self.running = False
        self.monitoring_active = False
        
        logger.info("Stopping real-time risk monitoring...")
    
    async def update_market_data(self, market_update: MarketUpdate):
        """Update market data for a symbol"""
        try:
            # Update current market data
            self.market_data[market_update.symbol] = market_update
            
            # Add to history
            if market_update.symbol not in self.market_history:
                self.market_history[market_update.symbol] = deque(maxlen=1000)
            
            self.market_history[market_update.symbol].append(market_update)
            
            # Add to update queue
            self.market_updates.append({
                'symbol': market_update.symbol,
                'update': market_update,
                'timestamp': datetime.now()
            })
            
            # Notify callbacks
            for callback in self.market_callbacks:
                try:
                    await callback(market_update)
                except Exception as e:
                    logger.error(f"Error in market callback: {e}")
            
            # Check thresholds
            await self._check_thresholds_for_symbol(market_update.symbol)
            
            logger.debug(f"Updated market data for {market_update.symbol}: {market_update.price}")
            
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
    
    async def get_current_market_data(self) -> Dict[str, MarketUpdate]:
        """Get current market data for all symbols"""
        return self.market_data.copy()
    
    async def get_market_history(self, symbol: str, minutes: int = 5) -> List[MarketUpdate]:
        """Get market data history for a symbol"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        history = []
        
        for update in list(self.market_history.get(symbol, [])):
            if update.timestamp >= cutoff_time:
                history.append(update)
        
        return history
    
    async def get_recent_events(self, minutes: int = 5) -> List[RiskEvent]:
        """Get risk events from recent minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_events = []
        
        for event in list(self.risk_events):
            if event.timestamp >= cutoff_time:
                recent_events.append(event)
        
        return recent_events
    
    async def get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk monitoring metrics"""
        metrics = {
            'timestamp': datetime.now(),
            'symbols_monitored': len(self.market_data),
            'active_thresholds': len([t for t in self.risk_thresholds if t.asset_class != "disabled"]),
            'events_24h': len([e for e in self.risk_events 
                             if e.timestamp >= datetime.now() - timedelta(hours=24)]),
            'events_per_type': self.event_counts.copy(),
            'performance_metrics': self.performance_metrics.copy(),
            'last_update': self.last_update,
            'monitoring_status': 'active' if self.monitoring_active else 'inactive'
        }
        
        return metrics
    
    async def force_risk_assessment(self) -> List[RiskEvent]:
        """Force a risk assessment check across all monitored data"""
        events = []
        
        # Check all symbols against all thresholds
        for symbol in self.market_data.keys():
            symbol_events = await self._check_thresholds_for_symbol(symbol)
            events.extend(symbol_events)
        
        return events
    
    # Private monitoring methods
    
    async def _market_data_monitoring_loop(self):
        """Background loop for market data monitoring"""
        while self.running:
            try:
                # Clean old market data
                await self._clean_old_market_data()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in market data monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _risk_threshold_monitoring_loop(self):
        """Background loop for risk threshold monitoring"""
        while self.running:
            try:
                # This would check portfolio-level thresholds
                # Implementation depends on portfolio data integration
                
                await asyncio.sleep(self.update_interval * 5)  # Less frequent than market data
                
            except Exception as e:
                logger.error(f"Error in risk threshold monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _performance_monitoring_loop(self):
        """Background loop for performance monitoring"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Log performance summary
                logger.info(f"Performance: {self.performance_metrics}")
                
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _market_data_simulation_loop(self):
        """Simulate market data updates (for demonstration)"""
        while self.running:
            try:
                # This simulates market data updates
                # In real implementation, connect to actual data feeds
                
                sample_symbols = ['AAPL', 'GOOGL', 'EURUSD', 'GC']
                for symbol in sample_symbols:
                    current_data = self.market_data.get(symbol)
                    
                    if current_data:
                        # Simulate price movement
                        import random
                        price_change = random.uniform(-0.01, 0.01)  # ±1%
                        new_price = current_data.price * (1 + price_change)
                        
                        # Create market update
                        market_update = MarketUpdate(
                            symbol=symbol,
                            price=new_price,
                            volume=random.uniform(1000, 10000),
                            timestamp=datetime.now(),
                            bid=new_price * 0.999,
                            ask=new_price * 1.001,
                            spread=(new_price * 1.001) - (new_price * 0.999),
                            liquidity_score=random.uniform(0.5, 1.0)
                        )
                        
                        await self.update_market_data(market_update)
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in market data simulation: {e}")
                await asyncio.sleep(1)
    
    async def _check_thresholds_for_symbol(self, symbol: str) -> List[RiskEvent]:
        """Check all thresholds for a specific symbol"""
        events = []
        market_update = self.market_data.get(symbol)
        
        if not market_update:
            return events
        
        try:
            for threshold in self.risk_thresholds:
                if threshold.symbol != "all" and threshold.symbol != symbol:
                    continue
                
                # Get current metric value
                metric_value = await self._get_metric_value(threshold.metric_name, market_update)
                
                # Check threshold
                threshold_triggered = self._evaluate_threshold(metric_value, threshold)
                
                if threshold_triggered:
                    event = RiskEvent(
                        event_type=threshold.metric_name,
                        severity=threshold.severity,
                        timestamp=datetime.now(),
                        symbol=symbol,
                        metric_value=metric_value,
                        threshold=threshold.threshold_value,
                        description=threshold.description,
                        data={
                            'symbol': symbol,
                            'market_update': market_update.__dict__
                        }
                    )
                    
                    # Check event rate limiting
                    if not await self._is_rate_limited(event):
                        events.append(event)
                        self._record_event(event)
                        
                        # Notify callbacks
                        for callback in self.risk_callbacks:
                            try:
                                await callback(event)
                            except Exception as e:
                                logger.error(f"Error in risk callback: {e}")
                
        except Exception as e:
            logger.error(f"Error checking thresholds for {symbol}: {e}")
        
        return events
    
    async def _get_metric_value(self, metric_name: str, market_update: MarketUpdate) -> float:
        """Get metric value from market update"""
        if metric_name == "price":
            return market_update.price
        elif metric_name == "volume":
            return market_update.volume
        elif metric_name == "bid_ask_spread":
            return market_update.spread
        elif metric_name == "liquidity_score":
            return market_update.liquidity_score
        elif metric_name == "price_change_pct":
            # Calculate price change from history
            history = list(self.market_history.get(market_update.symbol, []))
            if len(history) >= 2:
                previous_price = history[-2].price
                change_pct = abs(market_update.price - previous_price) / previous_price
                return change_pct
            return 0.0
        else:
            return 0.0
    
    def _evaluate_threshold(self, value: float, threshold: RiskThreshold) -> bool:
        """Evaluate if threshold is triggered"""
        if threshold.comparison_operator == "gt":
            return value > threshold.threshold_value
        elif threshold.comparison_operator == "lt":
            return value < threshold.threshold_value
        elif threshold.comparison_operator == "eq":
            return abs(value - threshold.threshold_value) < 0.001
        else:
            return False
    
    def _record_event(self, event: RiskEvent):
        """Record risk event"""
        self.risk_events.append(event)
        self.event_counts[event.event_type] = self.event_counts.get(event.event_type, 0) + 1
        
        logger.warning(f"Risk event: {event.severity} - {event.description}")
    
    async def _is_rate_limited(self, event: RiskEvent) -> bool:
        """Check if event should be rate limited"""
        # Simple rate limiting - count events per minute
        minute_ago = datetime.now() - timedelta(minutes=1)
        recent_events = [e for e in self.risk_events if e.timestamp >= minute_ago]
        
        return len(recent_events) >= self.max_events_per_minute
    
    async def _clean_old_market_data(self):
        """Clean old market data"""
        cutoff_time = datetime.now() - timedelta(seconds=self.market_data_ttl)
        
        # Clean current market data
        expired_symbols = []
        for symbol, data in self.market_data.items():
            if data.timestamp < cutoff_time:
                expired_symbols.append(symbol)
        
        for symbol in expired_symbols:
            del self.market_data[symbol]
    
    async def _update_performance_metrics(self):
        """Update performance metrics"""
        current_time = datetime.now()
        
        if self.last_update:
            response_time = (current_time - self.last_update).total_seconds()
            self.performance_metrics['avg_response_time'] = (
                (self.performance_metrics['avg_response_time'] * 0.9) + (response_time * 0.1)
            )
        
        self.performance_metrics['updates_processed'] += len(self.market_updates)
        self.performance_metrics['events_generated'] += len(self.risk_events)
        self.last_update = current_time
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get detailed monitoring system status"""
        return {
            'running': self.running,
            'monitoring_active': self.monitoring_active,
            'symbols_tracked': len(self.market_data),
            'thresholds_configured': len(self.risk_thresholds),
            'events_last_hour': len([e for e in self.risk_events 
                                   if e.timestamp >= datetime.now() - timedelta(hours=1)]),
            'performance_metrics': self.performance_metrics.copy(),
            'system_health': 'healthy' if self.running else 'stopped'
        }
    
    async def reset_monitoring_stats(self):
        """Reset monitoring statistics"""
        self.risk_events.clear()
        self.event_counts.clear()
        self.performance_metrics = {
            'updates_processed': 0,
            'events_generated': 0,
            'avg_response_time': 0.0,
            'last_performance_check': datetime.now()
        }
        
        logger.info("Monitoring statistics reset")
    
    async def export_monitoring_data(self, format_type: str = 'json') -> str:
        """Export monitoring data"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'market_data': {symbol: update.__dict__ for symbol, update in self.market_data.items()},
            'risk_events': [event.__dict__ for event in list(self.risk_events)],
            'thresholds': [threshold.__dict__ for threshold in self.risk_thresholds],
            'performance_metrics': self.performance_metrics.copy()
        }
        
        if format_type.lower() == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            return str(data)