"""
Position Monitoring System
=========================

Real-time position tracking and monitoring for risk management.
Tracks individual positions, calculates exposures, and monitors limits.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class Position:
    """Individual position data structure"""
    symbol: str
    asset_class: str
    quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    timestamp: datetime
    stop_loss: float = 0.0
    take_profit: float = 0.0
    position_limit: float = 0.0
    liquidity_ratio: float = 1.0
    correlation: float = 0.0
    beta: float = 1.0
    
    def __post_init__(self):
        """Calculate derived values after initialization"""
        self.market_value = self.quantity * self.current_price
        self.unrealized_pnl = self.quantity * (self.current_price - self.avg_cost)

@dataclass
class PositionMetrics:
    """Position-level risk metrics"""
    symbol: str
    var_contribution: float
    beta_contribution: float
    correlation_risk: float
    liquidity_risk: float
    concentration_risk: float

@dataclass
class PortfolioPositionSummary:
    """Portfolio position summary"""
    total_positions: int
    total_market_value: float
    total_unrealized_pnl: float
    total_realized_pnl: float
    largest_position: float
    position_concentration: float
    gross_exposure: float
    net_exposure: float

class PositionMonitor:
    """
    Real-time position monitoring system
    
    Tracks positions across all asset classes, monitors limits,
    calculates position-level risk metrics, and provides
    real-time updates to risk management system.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        
        # Position storage
        self.positions: Dict[str, Position] = {}
        self.position_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.position_updates: deque = deque(maxlen=10000)
        
        # Metrics tracking
        self.portfolio_metrics = None
        self.position_metrics: Dict[str, PositionMetrics] = {}
        
        # Event callbacks
        self.position_update_callbacks: List[Callable] = []
        self.limit_violation_callbacks: List[Callable] = []
        
        # Configuration
        self.update_interval = config.get('update_interval', 1.0)  # seconds
        self.position_history_retention = config.get('history_retention', 24)  # hours
        self.limit_check_interval = config.get('limit_check_interval', 5.0)  # seconds
        
        # Monitoring state
        self.last_update = None
        self.position_change_threshold = config.get('position_change_threshold', 0.001)  # 0.1%
        self.max_positions = config.get('max_positions', 1000)
        
    async def initialize(self):
        """Initialize position monitoring system"""
        try:
            logger.info("Initializing Position Monitor...")
            
            # Load initial positions
            await self._load_positions()
            
            # Start background tasks
            asyncio.create_task(self._position_update_loop())
            asyncio.create_task(self._limit_monitoring_loop())
            
            logger.info("Position Monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Position Monitor: {e}")
            raise
    
    async def start(self):
        """Start position monitoring"""
        self.running = True
        logger.info("Starting position monitoring...")
    
    async def stop(self):
        """Stop position monitoring"""
        self.running = False
        logger.info("Stopping position monitoring...")
    
    async def _load_positions(self):
        """Load current positions from data source"""
        try:
            # This would typically load from trading system/database
            # For now, creating sample positions for demonstration
            
            sample_positions = {
                'AAPL': {
                    'symbol': 'AAPL',
                    'asset_class': 'equity',
                    'quantity': 100,
                    'avg_cost': 150.0,
                    'current_price': 155.0,
                    'timestamp': datetime.now(),
                    'stop_loss': 140.0,
                    'take_profit': 165.0,
                    'position_limit': 500000.0
                },
                'GOOGL': {
                    'symbol': 'GOOGL',
                    'asset_class': 'equity', 
                    'quantity': 50,
                    'avg_cost': 2800.0,
                    'current_price': 2850.0,
                    'timestamp': datetime.now(),
                    'stop_loss': 2700.0,
                    'take_profit': 2900.0,
                    'position_limit': 1000000.0
                },
                'EURUSD': {
                    'symbol': 'EURUSD',
                    'asset_class': 'forex',
                    'quantity': 100000,  # Forex units
                    'avg_cost': 1.1000,
                    'current_price': 1.1025,
                    'timestamp': datetime.now(),
                    'stop_loss': 1.0950,
                    'take_profit': 1.1080,
                    'position_limit': 50000000.0
                },
                'GC': {
                    'symbol': 'GC',  # Gold futures
                    'asset_class': 'commodity',
                    'quantity': 10,  # Contracts
                    'avg_cost': 1800.0,
                    'current_price': 1820.0,
                    'timestamp': datetime.now(),
                    'stop_loss': 1775.0,
                    'take_profit': 1850.0,
                    'position_limit': 1000000.0
                }
            }
            
            for symbol, pos_data in sample_positions.items():
                position = Position(**pos_data)
                await self.update_position(position)
                
            logger.info(f"Loaded {len(sample_positions)} initial positions")
            
        except Exception as e:
            logger.error(f"Error loading positions: {e}")
    
    async def update_position(self, position: Position):
        """Update a single position with new data"""
        try:
            old_position = self.positions.get(position.symbol)
            
            # Store in history
            self.position_history[position.symbol].append({
                'timestamp': position.timestamp,
                'quantity': position.quantity,
                'price': position.current_price,
                'market_value': position.market_value,
                'unrealized_pnl': position.unrealized_pnl
            })
            
            # Update current position
            self.positions[position.symbol] = position
            
            # Check for significant changes
            if old_position:
                change_pct = self._calculate_position_change(old_position, position)
                if abs(change_pct) > self.position_change_threshold:
                    await self._handle_significant_change(old_position, position, change_pct)
            
            # Update metrics
            await self._update_position_metrics(position)
            
            # Add to update queue
            self.position_updates.append({
                'symbol': position.symbol,
                'position': position,
                'timestamp': datetime.now()
            })
            
            # Notify callbacks
            for callback in self.position_update_callbacks:
                try:
                    await callback({
                        'symbol': position.symbol,
                        'position': position,
                        'change': change_pct if old_position else 0
                    })
                except Exception as e:
                    logger.error(f"Error in position update callback: {e}")
            
            logger.debug(f"Updated position {position.symbol}: {position.quantity} @ {position.current_price}")
            
        except Exception as e:
            logger.error(f"Error updating position {position.symbol}: {e}")
    
    async def get_current_positions(self) -> Dict[str, Position]:
        """Get all current positions"""
        return self.positions.copy()
    
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get specific position"""
        return self.positions.get(symbol)
    
    async def get_portfolio_summary(self) -> PortfolioPositionSummary:
        """Get portfolio position summary"""
        if not self.positions:
            return PortfolioPositionSummary(0, 0, 0, 0, 0, 0, 0, 0)
        
        total_market_value = sum(pos.market_value for pos in self.positions.values())
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        total_realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
        
        # Calculate exposures
        gross_exposure = sum(abs(pos.market_value) for pos in self.positions.values())
        
        # Net exposure calculation (simplified)
        long_exposure = sum(pos.market_value for pos in self.positions.values() if pos.quantity > 0)
        short_exposure = sum(abs(pos.market_value) for pos in self.positions.values() if pos.quantity < 0)
        net_exposure = long_exposure - short_exposure
        
        # Position concentration
        if total_market_value > 0:
            largest_position = max(pos.market_value for pos in self.positions.values())
            position_concentration = largest_position / total_market_value
        else:
            largest_position = 0
            position_concentration = 0
        
        return PortfolioPositionSummary(
            total_positions=len(self.positions),
            total_market_value=total_market_value,
            total_unrealized_pnl=total_unrealized_pnl,
            total_realized_pnl=total_realized_pnl,
            largest_position=largest_position,
            position_concentration=position_concentration,
            gross_exposure=gross_exposure,
            net_exposure=net_exposure
        )
    
    async def get_positions_by_asset_class(self) -> Dict[str, List[Position]]:
        """Group positions by asset class"""
        positions_by_class = defaultdict(list)
        for position in self.positions.values():
            positions_by_class[position.asset_class].append(position)
        return dict(positions_by_class)
    
    async def get_position_metrics(self, symbol: str) -> Optional[PositionMetrics]:
        """Get position-level risk metrics"""
        return self.position_metrics.get(symbol)
    
    async def get_risk_attribution(self) -> Dict[str, PositionMetrics]:
        """Get risk attribution for all positions"""
        return self.position_metrics.copy()
    
    async def get_recent_updates(self, minutes: int = 5) -> List[Dict]:
        """Get position updates from recent minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_updates = []
        
        for update in list(self.position_updates):
            if update['timestamp'] >= cutoff_time:
                recent_updates.append(update)
        
        return recent_updates
    
    def add_position_update_callback(self, callback: Callable):
        """Add callback for position updates"""
        self.position_update_callbacks.append(callback)
    
    def add_limit_violation_callback(self, callback: Callable):
        """Add callback for limit violations"""
        self.limit_violation_callbacks.append(callback)
    
    async def check_position_limits(self) -> List[Dict[str, Any]]:
        """Check all positions against limits"""
        violations = []
        
        for symbol, position in self.positions.items():
            # Check position size limit
            if (position.position_limit > 0 and 
                abs(position.market_value) > position.position_limit):
                violations.append({
                    'type': 'position_size_limit',
                    'symbol': symbol,
                    'current_value': abs(position.market_value),
                    'limit': position.position_limit,
                    'excess': abs(position.market_value) - position.position_limit,
                    'severity': 'high' if abs(position.market_value) > position.position_limit * 1.5 else 'medium'
                })
            
            # Check unrealized loss limit
            loss_limit = self.config.get('position_loss_limit', 0.1)  # 10% loss limit
            if position.unrealized_pnl < 0:
                loss_pct = abs(position.unrealized_pnl) / max(abs(position.market_value), 1)
                if loss_pct > loss_limit:
                    violations.append({
                        'type': 'unrealized_loss_limit',
                        'symbol': symbol,
                        'loss_amount': abs(position.unrealized_pnl),
                        'loss_percentage': loss_pct,
                        'limit': loss_limit,
                        'excess': loss_pct - loss_limit,
                        'severity': 'high' if loss_pct > loss_limit * 1.5 else 'medium'
                    })
        
        # Check portfolio-level limits
        portfolio_summary = await self.get_portfolio_summary()
        
        # Check maximum concentration
        max_concentration = self.config.get('max_concentration', 0.25)  # 25% max concentration
        if portfolio_summary.position_concentration > max_concentration:
            violations.append({
                'type': 'concentration_limit',
                'current_concentration': portfolio_summary.position_concentration,
                'limit': max_concentration,
                'excess': portfolio_summary.position_concentration - max_concentration,
                'severity': 'high'
            })
        
        # Check gross exposure limit
        max_gross_exposure = self.config.get('max_gross_exposure', 10000000)  # $10M default
        if portfolio_summary.gross_exposure > max_gross_exposure:
            violations.append({
                'type': 'gross_exposure_limit',
                'current_exposure': portfolio_summary.gross_exposure,
                'limit': max_gross_exposure,
                'excess': portfolio_summary.gross_exposure - max_gross_exposure,
                'severity': 'medium'
            })
        
        # Notify callbacks for violations
        for violation in violations:
            for callback in self.limit_violation_callbacks:
                try:
                    await callback(violation)
                except Exception as e:
                    logger.error(f"Error in limit violation callback: {e}")
        
        return violations
    
    async def _position_update_loop(self):
        """Background loop for position updates"""
        while self.running:
            try:
                await self._update_portfolio_metrics()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in position update loop: {e}")
                await asyncio.sleep(1)
    
    async def _limit_monitoring_loop(self):
        """Background loop for limit monitoring"""
        while self.running:
            try:
                violations = await self.check_position_limits()
                if violations:
                    logger.warning(f"Found {len(violations)} position limit violations")
                await asyncio.sleep(self.limit_check_interval)
            except Exception as e:
                logger.error(f"Error in limit monitoring loop: {e}")
                await asyncio.sleep(1)
    
    def _calculate_position_change(self, old: Position, new: Position) -> float:
        """Calculate percentage change in position value"""
        old_value = abs(old.market_value)
        new_value = abs(new.market_value)
        
        if old_value == 0:
            return 1.0 if new_value > 0 else 0
        
        return (new_value - old_value) / old_value
    
    async def _handle_significant_change(self, old: Position, new: Position, change_pct: float):
        """Handle significant position changes"""
        logger.info(f"Significant position change for {new.symbol}: {change_pct:.2%}")
        
        # Could trigger additional risk checks here
        
    async def _update_position_metrics(self, position: Position):
        """Update position-level risk metrics"""
        try:
            # Calculate VaR contribution (simplified)
            var_contribution = self._calculate_var_contribution(position)
            
            # Calculate beta contribution
            beta_contribution = self._calculate_beta_contribution(position)
            
            # Calculate correlation risk
            correlation_risk = abs(position.correlation)
            
            # Calculate liquidity risk
            liquidity_risk = 1 / max(position.liquidity_ratio, 0.01)
            
            # Calculate concentration risk
            portfolio_summary = await self.get_portfolio_summary()
            concentration_risk = abs(position.market_value) / max(portfolio_summary.total_market_value, 1)
            
            metrics = PositionMetrics(
                symbol=position.symbol,
                var_contribution=var_contribution,
                beta_contribution=beta_contribution,
                correlation_risk=correlation_risk,
                liquidity_risk=liquidity_risk,
                concentration_risk=concentration_risk
            )
            
            self.position_metrics[position.symbol] = metrics
            
        except Exception as e:
            logger.error(f"Error updating position metrics for {position.symbol}: {e}")
    
    def _calculate_var_contribution(self, position: Position) -> float:
        """Calculate VaR contribution for position"""
        # Simplified VaR calculation
        volatility = self.config.get('default_volatility', 0.02)  # 2% default
        position_var = position.market_value * volatility * 2.33  # 95% confidence
        return abs(position_var)
    
    def _calculate_beta_contribution(self, position: Position) -> float:
        """Calculate beta contribution for position"""
        return abs(position.beta * position.market_value)
    
    async def _update_portfolio_metrics(self):
        """Update portfolio-level metrics"""
        try:
            self.portfolio_metrics = await self.get_portfolio_summary()
            self.last_update = datetime.now()
        except Exception as e:
            logger.error(f"Error updating portfolio metrics: {e}")
    
    async def close_position(self, symbol: str) -> bool:
        """Close a position (for risk control actions)"""
        try:
            if symbol in self.positions:
                position = self.positions[symbol]
                
                # This would integrate with trading system to close position
                # For now, just mark as closed
                
                logger.info(f"Closing position {symbol}")
                del self.positions[symbol]
                
                # Update history
                self.position_history[symbol].append({
                    'timestamp': datetime.now(),
                    'action': 'closed',
                    'final_value': position.market_value,
                    'final_pnl': position.unrealized_pnl
                })
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")
            return False
    
    async def reduce_position(self, symbol: str, reduction_pct: float) -> bool:
        """Reduce position size by percentage"""
        try:
            if symbol in self.positions and 0 < reduction_pct < 1:
                position = self.positions[symbol]
                new_quantity = position.quantity * (1 - reduction_pct)
                position.quantity = new_quantity
                position.market_value = new_quantity * position.current_price
                position.unrealized_pnl = new_quantity * (position.current_price - position.avg_cost)
                
                await self.update_position(position)
                
                logger.info(f"Reduced position {symbol} by {reduction_pct:.1%}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error reducing position {symbol}: {e}")
            return False