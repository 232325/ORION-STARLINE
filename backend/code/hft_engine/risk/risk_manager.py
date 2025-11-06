"""
Risk Management System
=====================

Comprehensive risk management for HFT operations
Monitors and controls various risk factors in real-time
"""

import time
import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from threading import Lock

from ..core.orderbook import OrderBook
from .position_limits import PositionLimits
from .market_risk import MarketRisk
from .operational_risk import OperationalRisk

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskMetrics:
    """Risk metrics structure"""
    total_exposure: float
    var_95: float  # Value at Risk (95% confidence)
    max_drawdown: float
    leverage_ratio: float
    concentration_risk: float
    liquidity_risk: float
    timestamp: float

@dataclass
class RiskAlert:
    """Risk alert structure"""
    alert_id: str
    severity: RiskLevel
    category: str  # 'position', 'market', 'operational'
    message: str
    timestamp: float
    symbol: Optional[str] = None
    threshold_exceeded: Optional[float] = None
    current_value: Optional[float] = None

class RiskManager:
    """
    Comprehensive Risk Management System
    
    Monitors and controls all risk factors in HFT operations
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Risk limits
        self.max_position_size = config.get('max_position_size', 100000)
        self.max_exposure_per_symbol = config.get('max_exposure_per_symbol', 10000)
        self.max_portfolio_var = config.get('max_portfolio_var', 5000)
        self.max_leverage = config.get('max_leverage', 3.0)
        self.max_concentration = config.get('max_concentration', 0.2)  # 20% per symbol
        
        # Performance monitoring
        self.logger = logging.getLogger(__name__)
        self.risk_lock = Lock()
        
        # Risk components
        self.position_limits = PositionLimits(config.get('position_limits', {}))
        self.market_risk = MarketRisk(config.get('market_risk', {}))
        self.operational_risk = OperationalRisk(config.get('operational_risk', {}))
        
        # Risk tracking
        self.risk_metrics_history: List[RiskMetrics] = []
        self.active_alerts: Dict[str, RiskAlert] = {}
        self.risk_level = RiskLevel.LOW
        
        # Portfolio tracking
        self.positions: Dict[str, float] = {}
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.total_exposure = 0.0
        
        # Risk statistics
        self.daily_var: Optional[float] = None
        self.max_drawdown_pct = 0.0
        self.last_portfolio_value = 1_000_000  # Starting capital
        
    async def initialize(self) -> bool:
        """Initialize risk management system"""
        try:
            self.logger.info("Initializing Risk Management System...")
            
            # Initialize risk components
            await self.position_limits.initialize()
            await self.market_risk.initialize()
            await self.operational_risk.initialize()
            
            self.logger.info("Risk Management System initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Risk Management System: {e}")
            return False
    
    async def check_signal(self, signal) -> bool:
        """Check if trading signal passes risk checks"""
        try:
            with self.risk_lock:
                # Position size check
                if not self.position_limits.check_position_size(signal.symbol, signal.quantity):
                    self._create_alert(
                        RiskLevel.HIGH,
                        'position',
                        f"Position size limit exceeded for {signal.symbol}",
                        signal.symbol,
                        signal.quantity
                    )
                    return False
                
                # Concentration risk check
                if not self.check_concentration_risk(signal.symbol, signal.quantity):
                    self._create_alert(
                        RiskLevel.MEDIUM,
                        'position',
                        f"Concentration risk exceeded for {signal.symbol}",
                        signal.symbol,
                        signal.quantity
                    )
                    return False
                
                # Market risk check
                if not await self.market_risk.check_market_conditions(signal.symbol):
                    self._create_alert(
                        RiskLevel.MEDIUM,
                        'market',
                        f"Poor market conditions for {signal.symbol}",
                        signal.symbol
                    )
                    return False
                
                # Leverage check
                if not self.check_leverage_limits(signal.quantity):
                    self._create_alert(
                        RiskLevel.CRITICAL,
                        'position',
                        "Leverage limit exceeded"
                    )
                    return False
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error checking signal risk: {e}")
            return False
    
    async def check_portfolio_risk(self, positions: Dict[str, float], 
                                 order_books: Dict[str, OrderBook]) -> bool:
        """Check overall portfolio risk"""
        try:
            with self.risk_lock:
                # Update positions
                self.positions = positions.copy()
                
                # Calculate portfolio metrics
                await self._calculate_portfolio_metrics(order_books)
                
                # Check VaR limits
                if self.daily_var and self.daily_var > self.max_portfolio_var:
                    self._create_alert(
                        RiskLevel.HIGH,
                        'market',
                        f"Portfolio VaR exceeded: {self.daily_var:.2f}",
                        threshold_exceeded=self.max_portfolio_var,
                        current_value=self.daily_var
                    )
                    return False
                
                # Check drawdown limits
                if self.max_drawdown_pct > 0.1:  # 10% drawdown
                    self._create_alert(
                        RiskLevel.HIGH,
                        'position',
                        f"Maximum drawdown exceeded: {self.max_drawdown_pct:.2%}"
                    )
                    return False
                
                # Check operational risk
                if not await self.operational_risk.check_system_health():
                    self._create_alert(
                        RiskLevel.CRITICAL,
                        'operational',
                        "System health check failed"
                    )
                    return False
                
                # Update risk level
                self._update_risk_level()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error checking portfolio risk: {e}")
            return False
    
    async def _calculate_portfolio_metrics(self, order_books: Dict[str, OrderBook]):
        """Calculate comprehensive portfolio metrics"""
        try:
            total_market_value = 0.0
            total_exposure = 0.0
            position_concentrations = {}
            
            # Calculate current market values
            for symbol, position in self.positions.items():
                if symbol in order_books:
                    order_book = order_books[symbol]
                    best_bid = order_book.get_best_bid()
                    best_ask = order_book.get_best_ask()
                    
                    if best_bid is not None and best_ask is not None:
                        mid_price = (best_bid + best_ask) / 2
                        market_value = abs(position * mid_price)
                        total_market_value += market_value
                        total_exposure += market_value
                        
                        # Calculate concentration
                        if total_market_value > 0:
                            position_concentrations[symbol] = market_value / total_market_value
            
            self.total_exposure = total_exposure
            
            # Calculate VaR (simplified)
            self.daily_var = self._calculate_var(total_market_value)
            
            # Calculate current drawdown
            current_portfolio_value = self.last_portfolio_value + self.realized_pnl + self.unrealized_pnl
            if current_portfolio_value < self.last_portfolio_value:
                drawdown = (self.last_portfolio_value - current_portfolio_value) / self.last_portfolio_value
                self.max_drawdown_pct = max(self.max_drawdown_pct, drawdown)
            
            # Store metrics
            risk_metrics = RiskMetrics(
                total_exposure=total_exposure,
                var_95=self.daily_var or 0.0,
                max_drawdown=self.max_drawdown_pct,
                leverage_ratio=self._calculate_leverage_ratio(),
                concentration_risk=max(position_concentrations.values()) if position_concentrations else 0.0,
                liquidity_risk=self._calculate_liquidity_risk(order_books),
                timestamp=time.time()
            )
            
            self.risk_metrics_history.append(risk_metrics)
            
            # Keep only recent metrics
            if len(self.risk_metrics_history) > 1000:
                self.risk_metrics_history = self.risk_metrics_history[-500:]
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio metrics: {e}")
    
    def _calculate_var(self, portfolio_value: float) -> Optional[float]:
        """Calculate Value at Risk (simplified)"""
        try:
            if len(self.risk_metrics_history) < 10:
                return None
            
            # Get recent returns
            recent_metrics = self.risk_metrics_history[-20:]
            returns = []
            
            for i in range(1, len(recent_metrics)):
                prev_value = recent_metrics[i-1].total_exposure
                curr_value = recent_metrics[i].total_exposure
                
                if prev_value > 0:
                    return_rate = (curr_value - prev_value) / prev_value
                    returns.append(return_rate)
            
            if returns:
                # Calculate 95% VaR
                sorted_returns = sorted(returns)
                var_index = int(0.05 * len(sorted_returns))
                var_95 = sorted_returns[var_index] if var_index < len(sorted_returns) else sorted_returns[0]
                
                return abs(var_95 * portfolio_value)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating VaR: {e}")
            return None
    
    def _calculate_leverage_ratio(self) -> float:
        """Calculate current leverage ratio"""
        if self.last_portfolio_value > 0:
            return self.total_exposure / self.last_portfolio_value
        return 0.0
    
    def _calculate_liquidity_risk(self, order_books: Dict[str, OrderBook]) -> float:
        """Calculate liquidity risk score"""
        try:
            total_liquidity = 0.0
            total_exposure = 0.0
            
            for symbol, position in self.positions.items():
                if symbol in order_books:
                    order_book = order_books[symbol]
                    depth = order_book.get_market_depth(5)
                    
                    bid_volume = sum(level.total_quantity for level in depth['bids'])
                    ask_volume = sum(level.total_quantity for level in depth['asks'])
                    total_book_liquidity = bid_volume + ask_volume
                    
                    total_liquidity += total_book_liquidity
                    total_exposure += abs(position)
            
            if total_exposure > 0:
                liquidity_ratio = total_liquidity / total_exposure
                # Higher ratio = lower liquidity risk
                return max(0.0, min(1.0, 1.0 - liquidity_ratio / 1000.0))
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating liquidity risk: {e}")
            return 0.0
    
    def check_concentration_risk(self, symbol: str, quantity: int) -> bool:
        """Check concentration risk for symbol"""
        try:
            # Calculate potential new position size
            current_position = self.positions.get(symbol, 0.0)
            new_position = current_position + quantity
            
            # Calculate concentration percentage
            total_positions = sum(abs(pos) for pos in self.positions.values()) + abs(new_position)
            
            if total_positions > 0:
                concentration = abs(new_position) / total_positions
                return concentration <= self.max_concentration
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking concentration risk: {e}")
            return True
    
    def check_leverage_limits(self, quantity: int) -> bool:
        """Check leverage limits"""
        try:
            new_exposure = self.total_exposure + abs(quantity * 1000)  # Simplified price
            leverage_ratio = new_exposure / self.last_portfolio_value if self.last_portfolio_value > 0 else 0
            
            return leverage_ratio <= self.max_leverage
            
        except Exception as e:
            self.logger.error(f"Error checking leverage limits: {e}")
            return True
    
    def _create_alert(self, severity: RiskLevel, category: str, message: str, 
                     symbol: Optional[str] = None, threshold_exceeded: Optional[float] = None,
                     current_value: Optional[float] = None):
        """Create risk alert"""
        alert_id = f"{category}_{severity.value}_{int(time.time() * 1000000)}"
        
        alert = RiskAlert(
            alert_id=alert_id,
            severity=severity,
            category=category,
            message=message,
            timestamp=time.time(),
            symbol=symbol,
            threshold_exceeded=threshold_exceeded,
            current_value=current_value
        )
        
        self.active_alerts[alert_id] = alert
        
        # Log alert
        log_level = {
            RiskLevel.LOW: logging.INFO,
            RiskLevel.MEDIUM: logging.WARNING,
            RiskLevel.HIGH: logging.ERROR,
            RiskLevel.CRITICAL: logging.CRITICAL
        }.get(severity, logging.WARNING)
        
        self.logger.log(log_level, f"RISK ALERT [{severity.value.upper()}]: {message}")
        
        # Clean up old alerts
        self._cleanup_old_alerts()
    
    def _cleanup_old_alerts(self):
        """Remove old alerts"""
        current_time = time.time()
        cutoff_time = current_time - 3600  # 1 hour
        
        expired_alerts = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.timestamp < cutoff_time
        ]
        
        for alert_id in expired_alerts:
            del self.active_alerts[alert_id]
    
    def _update_risk_level(self):
        """Update overall risk level based on current metrics"""
        risk_score = 0
        
        # Check VaR
        if self.daily_var and self.daily_var > self.max_portfolio_var * 0.8:
            risk_score += 2
        
        # Check drawdown
        if self.max_drawdown_pct > 0.05:  # 5%
            risk_score += 2
        
        # Check leverage
        if self._calculate_leverage_ratio() > self.max_leverage * 0.8:
            risk_score += 1
        
        # Check alerts
        critical_alerts = len([a for a in self.active_alerts.values() if a.severity == RiskLevel.CRITICAL])
        if critical_alerts > 0:
            risk_score += 3
        
        high_alerts = len([a for a in self.active_alerts.values() if a.severity == RiskLevel.HIGH])
        if high_alerts > 2:
            risk_score += 1
        
        # Update risk level
        if risk_score >= 5:
            self.risk_level = RiskLevel.CRITICAL
        elif risk_score >= 3:
            self.risk_level = RiskLevel.HIGH
        elif risk_level >= 1:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW
    
    def get_risk_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive risk dashboard"""
        with self.risk_lock:
            latest_metrics = self.risk_metrics_history[-1] if self.risk_metrics_history else None
            
            return {
                'risk_level': self.risk_level.value,
                'total_exposure': self.total_exposure,
                'daily_var': self.daily_var,
                'max_drawdown_pct': self.max_drawdown_pct,
                'leverage_ratio': self._calculate_leverage_ratio(),
                'concentration_risk': latest_metrics.concentration_risk if latest_metrics else 0.0,
                'liquidity_risk': latest_metrics.liquidity_risk if latest_metrics else 0.0,
                'active_alerts': len(self.active_alerts),
                'critical_alerts': len([a for a in self.active_alerts.values() if a.severity == RiskLevel.CRITICAL]),
                'alerts_detail': [asdict(alert) for alert in list(self.active_alerts.values())[-10:]],
                'position_concentration': {
                    symbol: abs(position) / sum(abs(pos) for pos in self.positions.values())
                    for symbol, position in self.positions.items()
                    if self.positions
                },
                'system_health': {
                    'position_limits_healthy': self.position_limits.is_healthy(),
                    'market_risk_healthy': self.market_risk.is_healthy(),
                    'operational_risk_healthy': self.operational_risk.is_healthy()
                }
            }
    
    def update_position(self, symbol: str, position_change: float, pnl_change: float):
        """Update position and P&L"""
        with self.risk_lock:
            if symbol not in self.positions:
                self.positions[symbol] = 0.0
            
            self.positions[symbol] += position_change
            
            if pnl_change > 0:
                self.realized_pnl += pnl_change
            else:
                self.unrealized_pnl += abs(pnl_change)
    
    async def shutdown(self):
        """Shutdown risk management system"""
        self.logger.info("Shutting down Risk Management System")
        
        # Shutdown risk components
        await self.position_limits.shutdown()
        await self.market_risk.shutdown()
        await self.operational_risk.shutdown()
        
        self.logger.info("Risk Management System shutdown complete")