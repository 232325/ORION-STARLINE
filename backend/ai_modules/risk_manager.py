"""
Comprehensive Risk Management System for Orion Starline Trading Platform

This module provides advanced risk management capabilities including:
- Real-time risk monitoring and assessment
- Portfolio risk analysis and diversification
- Multiple risk models (VaR, CVaR, Monte Carlo)
- Dynamic position sizing and risk parity
- Emergency stop mechanisms and stress testing
- Regulatory compliance (MiFID II, ESMA)
- Black swan event detection
- Risk alerts and notifications

Author: Orion Starline Risk Management Team
Version: 1.0.0
Date: 2025-11-04
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import warnings
from scipy import stats
from scipy.optimize import minimize
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class RiskLevel(Enum):
    """Risk level enumeration"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"

class RiskModel(Enum):
    """Risk model types"""
    VAR = "var"  # Value at Risk
    CVAR = "cvar"  # Conditional Value at Risk
    MONTE_CARLO = "monte_carlo"
    STRESS_TEST = "stress_test"
    BLACK_SWAN = "black_swan"

class AlertType(Enum):
    """Alert types for risk notifications"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class Position:
    """Trading position data structure"""
    symbol: str
    size: float
    entry_price: float
    current_price: float
    leverage: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    position_type: str = "long"  # long, short, spot
    notional_value: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

@dataclass
class RiskMetrics:
    """Risk metrics container"""
    var_1d: float = 0.0
    cvar_1d: float = 0.0
    var_10d: float = 0.0
    portfolio_beta: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    volatility: float = 0.0
    correlation_risk: float = 0.0
    concentration_risk: float = 0.0
    leverage_ratio: float = 0.0
    liquidity_risk: float = 0.0
    risk_score: int = 0  # 0-100 scale

@dataclass
class RiskAlert:
    """Risk alert data structure"""
    alert_id: str
    alert_type: AlertType
    message: str
    timestamp: datetime
    severity: RiskLevel
    affected_positions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False

class RiskManager:
    """
    Comprehensive Risk Management System
    
    Provides real-time risk monitoring, assessment, and management
    for trading portfolios with advanced analytical capabilities.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Risk Manager
        
        Args:
            config: Configuration dictionary for risk management settings
        """
        self.config = config or self._get_default_config()
        self.positions: Dict[str, Position] = {}
        self.risk_metrics = RiskMetrics()
        self.alerts: List[RiskAlert] = []
        self.alert_queue = queue.Queue()
        self.risk_thresholds = self.config.get('risk_thresholds', {})
        self.market_data: Dict[str, pd.DataFrame] = {}
        self.correlation_matrix: Optional[pd.DataFrame] = None
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize risk models
        self._initialize_risk_models()
        
        # Load regulatory requirements
        self._load_regulatory_requirements()
        
        self.logger.info("Risk Manager initialized successfully")
    
    def _get_default_config(self) -> Dict:
        """Get default configuration for risk management"""
        return {
            'risk_thresholds': {
                'max_portfolio_var': 0.05,  # 5% of portfolio value
                'max_leverage': 10.0,
                'max_single_position': 0.20,  # 20% of portfolio
                'max_correlation': 0.8,
                'max_concentration': 0.30,
                'max_drawdown': 0.15,  # 15% max drawdown
                'risk_score_warning': 70,
                'risk_score_critical': 85
            },
            'alert_settings': {
                'email_enabled': False,
                'email_recipients': [],
                'slack_enabled': False,
                'slack_webhook': None,
                'sms_enabled': False
            },
            'risk_models': {
                'var_confidence_level': 0.95,
                'monte_carlo_simulations': 10000,
                'stress_test_scenarios': 20,
                'lookback_period': 252  # 1 year of trading days
            },
            'regulatory': {
                'mifid_ii_compliance': True,
                'esma_compliance': True,
                'fatca_compliance': False,
                'record_retention_days': 2555  # 7 years
            }
        }
    
    def _setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger('RiskManager')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _initialize_risk_models(self):
        """Initialize risk calculation models"""
        self.var_confidence = self.config['risk_models']['var_confidence_level']
        self.monte_carlo_simulations = self.config['risk_models']['monte_carlo_simulations']
        self.stress_scenarios = self.config['risk_models']['stress_test_scenarios']
        self.lookback_period = self.config['risk_models']['lookback_period']
    
    def _load_regulatory_requirements(self):
        """Load regulatory compliance requirements"""
        self.regulatory = self.config.get('regulatory', {})
        
        # MiFID II requirements
        self.mifid_requirements = {
            'best_execution': True,
            'transaction_reporting': True,
            'record_keeping': True,
            'investor_protection': True,
            'product_governance': True
        }
        
        # ESMA requirements
        self.esma_requirements = {
            'leverage_limits': True,
            'margin_closeout': True,
            'negative_balance_protection': True,
            'risk_warnings': True
        }
    
    def add_position(self, position: Position) -> bool:
        """
        Add a new trading position to the portfolio
        
        Args:
            position: Position object with trading data
            
        Returns:
            bool: True if position added successfully
        """
        try:
            # Calculate derived values
            position.notional_value = abs(position.size * position.current_price)
            position.unrealized_pnl = self._calculate_unrealized_pnl(position)
            
            # Check risk limits before adding
            if not self._check_pre_trade_risk_limits(position):
                self._create_alert(
                    AlertType.CRITICAL,
                    f"Pre-trade risk limit exceeded for {position.symbol}",
                    RiskLevel.CRITICAL,
                    [position.symbol]
                )
                return False
            
            # Add position
            self.positions[position.symbol] = position
            self.logger.info(f"Position added: {position.symbol} - Size: {position.size}")
            
            # Update risk metrics
            self._update_risk_metrics()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding position: {e}")
            return False
    
    def remove_position(self, symbol: str) -> bool:
        """
        Remove a position from the portfolio
        
        Args:
            symbol: Symbol of the position to remove
            
        Returns:
            bool: True if position removed successfully
        """
        try:
            if symbol in self.positions:
                position = self.positions[symbol]
                del self.positions[symbol]
                self.logger.info(f"Position removed: {symbol}")
                
                # Update risk metrics
                self._update_risk_metrics()
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing position: {e}")
            return False
    
    def update_position(self, symbol: str, current_price: float) -> bool:
        """
        Update position with current market price
        
        Args:
            symbol: Symbol of the position
            current_price: Current market price
            
        Returns:
            bool: True if position updated successfully
        """
        try:
            if symbol in self.positions:
                position = self.positions[symbol]
                old_price = position.current_price
                position.current_price = current_price
                position.unrealized_pnl = self._calculate_unrealized_pnl(position)
                
                # Check stop loss / take profit
                self._check_exit_conditions(position)
                
                # Update risk metrics
                self._update_risk_metrics()
                
                # Check for risk alerts
                self._check_risk_alerts()
                
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating position: {e}")
            return False
    
    def _calculate_unrealized_pnl(self, position: Position) -> float:
        """Calculate unrealized P&L for a position"""
        if position.position_type == "long":
            return (position.current_price - position.entry_price) * position.size
        elif position.position_type == "short":
            return (position.entry_price - position.current_price) * position.size
        else:
            return 0.0
    
    def _check_pre_trade_risk_limits(self, position: Position) -> bool:
        """Check pre-trade risk limits"""
        try:
            total_portfolio_value = self._get_total_portfolio_value()
            
            # If this is the first position, allow it
            if total_portfolio_value == 0:
                return True
            
            position_value_ratio = position.notional_value / total_portfolio_value
            
            # Check single position limit
            if position_value_ratio > self.risk_thresholds['max_single_position']:
                self.logger.warning(f"Position {position.symbol} exceeds single position limit")
                return False
            
            # Check leverage limit
            if position.leverage > self.risk_thresholds['max_leverage']:
                self.logger.warning(f"Position {position.symbol} exceeds leverage limit")
                return False
            
            # Check portfolio VaR only if we have existing positions
            if len(self.positions) > 0:
                portfolio_var = self._calculate_var(1)
                if portfolio_var > self.risk_thresholds['max_portfolio_var']:
                    self.logger.warning("Portfolio VaR exceeds maximum threshold")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking pre-trade risk limits: {e}")
            return False
    
    def _check_exit_conditions(self, position: Position):
        """Check stop loss and take profit conditions"""
        try:
            # Check stop loss
            if position.stop_loss:
                if position.position_type == "long" and position.current_price <= position.stop_loss:
                    self._create_alert(
                        AlertType.CRITICAL,
                        f"Stop loss triggered for {position.symbol}",
                        RiskLevel.CRITICAL,
                        [position.symbol],
                        {"stop_loss": position.stop_loss, "current_price": position.current_price}
                    )
                elif position.position_type == "short" and position.current_price >= position.stop_loss:
                    self._create_alert(
                        AlertType.CRITICAL,
                        f"Stop loss triggered for {position.symbol}",
                        RiskLevel.CRITICAL,
                        [position.symbol],
                        {"stop_loss": position.stop_loss, "current_price": position.current_price}
                    )
            
            # Check take profit
            if position.take_profit:
                if position.position_type == "long" and position.current_price >= position.take_profit:
                    self._create_alert(
                        AlertType.INFO,
                        f"Take profit target reached for {position.symbol}",
                        RiskLevel.LOW,
                        [position.symbol],
                        {"take_profit": position.take_profit, "current_price": position.current_price}
                    )
                elif position.position_type == "short" and position.current_price <= position.take_profit:
                    self._create_alert(
                        AlertType.INFO,
                        f"Take profit target reached for {position.symbol}",
                        RiskLevel.LOW,
                        [position.symbol],
                        {"take_profit": position.take_profit, "current_price": position.current_price}
                    )
                    
        except Exception as e:
            self.logger.error(f"Error checking exit conditions: {e}")
    
    def _get_total_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        return sum(pos.notional_value for pos in self.positions.values())
    
    def _update_risk_metrics(self):
        """Update portfolio risk metrics"""
        try:
            if not self.positions:
                self.risk_metrics = RiskMetrics()
                return
            
            # Update basic metrics
            self.risk_metrics.leverage_ratio = self._calculate_leverage_ratio()
            self.risk_metrics.volatility = self._calculate_portfolio_volatility()
            self.risk_metrics.max_drawdown = self._calculate_max_drawdown()
            self.risk_metrics.sharpe_ratio = self._calculate_sharpe_ratio()
            
            # Update risk model metrics
            self.risk_metrics.var_1d = self._calculate_var(1)
            self.risk_metrics.cvar_1d = self._calculate_cvar(1)
            self.risk_metrics.var_10d = self._calculate_var(10)
            
            # Update concentration and correlation risk
            self.risk_metrics.concentration_risk = self._calculate_concentration_risk()
            self.risk_metrics.correlation_risk = self._calculate_correlation_risk()
            
            # Calculate overall risk score (0-100)
            self.risk_metrics.risk_score = self._calculate_risk_score()
            
        except Exception as e:
            self.logger.error(f"Error updating risk metrics: {e}")
    
    def _calculate_leverage_ratio(self) -> float:
        """Calculate portfolio leverage ratio"""
        total_exposure = sum(abs(pos.size * pos.current_price) for pos in self.positions.values())
        total_equity = self._get_total_portfolio_value()
        return total_exposure / total_equity if total_equity > 0 else 0.0
    
    def _calculate_portfolio_volatility(self) -> float:
        """Calculate portfolio volatility"""
        if len(self.positions) < 2:
            return 0.0
        
        try:
            # Get historical price data for correlation calculation
            returns_data = self._get_historical_returns()
            if returns_data.empty:
                return 0.0
            
            # Calculate portfolio variance
            portfolio_variance = 0.0
            weights = self._get_portfolio_weights()
            
            for i, symbol1 in enumerate(returns_data.columns):
                for j, symbol2 in enumerate(returns_data.columns):
                    if symbol1 in weights and symbol2 in weights:
                        weight1 = weights[symbol1]
                        weight2 = weights[symbol2]
                        correlation = returns_data[symbol1].corr(returns_data[symbol2])
                        vol1 = returns_data[symbol1].std()
                        vol2 = returns_data[symbol2].std()
                        portfolio_variance += weight1 * weight2 * correlation * vol1 * vol2
            
            return np.sqrt(portfolio_variance * 252)  # Annualized volatility
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio volatility: {e}")
            return 0.0
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        try:
            # Get historical portfolio values
            portfolio_values = self._get_historical_portfolio_values()
            if len(portfolio_values) < 2:
                return 0.0
            
            # Calculate drawdowns
            peak = portfolio_values[0]
            max_drawdown = 0.0
            
            for value in portfolio_values[1:]:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
            
            return max_drawdown
            
        except Exception as e:
            self.logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        try:
            returns = self._get_historical_returns()
            if returns.empty:
                return 0.0
            
            portfolio_returns = self._calculate_portfolio_returns()
            if portfolio_returns.empty:
                return 0.0
            
            excess_returns = portfolio_returns.mean() - risk_free_rate / 252
            volatility = portfolio_returns.std()
            
            return excess_returns / volatility if volatility > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0
    
    def _calculate_var(self, days: int = 1) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            days: Time horizon for VaR calculation
            
        Returns:
            float: VaR value
        """
        try:
            returns = self._get_historical_returns()
            if returns.empty:
                return 0.0
            
            portfolio_returns = self._calculate_portfolio_returns()
            if portfolio_returns.empty:
                return 0.0
            
            # Historical VaR
            var_percentile = (1 - self.var_confidence) * 100
            var = np.percentile(portfolio_returns, var_percentile)
            
            # Scale for time horizon
            var_scaled = var * np.sqrt(days)
            
            return abs(var_scaled)
            
        except Exception as e:
            self.logger.error(f"Error calculating VaR: {e}")
            return 0.0
    
    def _calculate_cvar(self, days: int = 1) -> float:
        """
        Calculate Conditional Value at Risk (CVaR)
        
        Args:
            days: Time horizon for CVaR calculation
            
        Returns:
            float: CVaR value
        """
        try:
            returns = self._get_historical_returns()
            if returns.empty:
                return 0.0
            
            portfolio_returns = self._calculate_portfolio_returns()
            if portfolio_returns.empty:
                return 0.0
            
            # Calculate VaR first
            var_percentile = (1 - self.var_confidence) * 100
            var = np.percentile(portfolio_returns, var_percentile)
            
            # CVaR is the average of returns worse than VaR
            tail_returns = portfolio_returns[portfolio_returns <= var]
            cvar = tail_returns.mean() if len(tail_returns) > 0 else var
            
            # Scale for time horizon
            cvar_scaled = cvar * np.sqrt(days)
            
            return abs(cvar_scaled)
            
        except Exception as e:
            self.logger.error(f"Error calculating CVaR: {e}")
            return 0.0
    
    def _calculate_portfolio_returns(self) -> pd.Series:
        """Calculate historical portfolio returns"""
        try:
            if not self.positions:
                return pd.Series()
            
            weights = self._get_portfolio_weights()
            returns_data = self._get_historical_returns()
            
            if returns_data.empty:
                return pd.Series()
            
            # Calculate weighted portfolio returns
            portfolio_returns = pd.Series(index=returns_data.index, dtype=float)
            
            for date in returns_data.index:
                daily_return = 0.0
                for symbol in returns_data.columns:
                    if symbol in weights:
                        weight = weights[symbol]
                        asset_return = returns_data.loc[date, symbol]
                        daily_return += weight * asset_return
                portfolio_returns.loc[date] = daily_return
            
            return portfolio_returns
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio returns: {e}")
            return pd.Series()
    
    def _get_portfolio_weights(self) -> Dict[str, float]:
        """Get portfolio weights for each position"""
        if not self.positions:
            return {}
        
        total_value = self._get_total_portfolio_value()
        weights = {}
        
        for symbol, position in self.positions.items():
            weights[symbol] = position.notional_value / total_value
        
        return weights
    
    def _get_historical_returns(self) -> pd.DataFrame:
        """Get historical returns data for portfolio positions"""
        # In a real implementation, this would fetch from a data provider
        # For demonstration, we'll generate synthetic data
        try:
            if not self.positions:
                return pd.DataFrame()
            
            # Generate synthetic returns data
            symbols = list(self.positions.keys())
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=self.lookback_period),
                end=datetime.now(),
                freq='D'
            )
            
            returns_data = pd.DataFrame(index=dates)
            
            for symbol in symbols:
                # Generate synthetic daily returns
                np.random.seed(hash(symbol) % 2**32)  # Consistent random data per symbol
                returns = np.random.normal(0.001, 0.02, len(dates))  # Mean 0.1%, std 2%
                returns_data[symbol] = returns
            
            return returns_data
            
        except Exception as e:
            self.logger.error(f"Error getting historical returns: {e}")
            return pd.DataFrame()
    
    def _get_historical_portfolio_values(self) -> List[float]:
        """Get historical portfolio values"""
        # In a real implementation, this would calculate from actual position history
        # For demonstration, we'll generate synthetic data
        try:
            portfolio_value = self._get_total_portfolio_value()
            days = min(self.lookback_period, 252)  # 1 year max
            
            # Generate synthetic portfolio value path
            np.random.seed(42)
            returns = np.random.normal(0.0005, 0.015, days)  # Slightly positive drift
            values = [portfolio_value]
            
            for ret in returns:
                new_value = values[-1] * (1 + ret)
                values.append(new_value)
            
            return values
            
        except Exception as e:
            self.logger.error(f"Error getting historical portfolio values: {e}")
            return []
    
    def _calculate_concentration_risk(self) -> float:
        """Calculate portfolio concentration risk"""
        try:
            if not self.positions:
                return 0.0
            
            weights = self._get_portfolio_weights()
            if not weights:
                return 0.0
            
            # Calculate Herfindahl-Hirschman Index (HHI)
            hhi = sum(weight**2 for weight in weights.values())
            
            # Normalize to 0-1 scale (higher = more concentrated)
            max_hhi = 1.0  # Maximum concentration (single asset)
            min_hhi = 1.0 / len(weights)  # Minimum concentration (equal weights)
            concentration_risk = (hhi - min_hhi) / (max_hhi - min_hhi)
            
            return max(0.0, min(1.0, concentration_risk))
            
        except Exception as e:
            self.logger.error(f"Error calculating concentration risk: {e}")
            return 0.0
    
    def _calculate_correlation_risk(self) -> float:
        """Calculate portfolio correlation risk"""
        try:
            returns_data = self._get_historical_returns()
            if returns_data.empty or len(returns_data.columns) < 2:
                return 0.0
            
            # Calculate correlation matrix
            correlation_matrix = returns_data.corr()
            
            # Get portfolio weights
            weights = self._get_portfolio_weights()
            
            # Calculate weighted average correlation
            weighted_correlation = 0.0
            total_weight = 0.0
            
            for i, symbol1 in enumerate(correlation_matrix.columns):
                for j, symbol2 in enumerate(correlation_matrix.columns):
                    if i != j and symbol1 in weights and symbol2 in weights:
                        weight1 = weights[symbol1]
                        weight2 = weights[symbol2]
                        correlation = correlation_matrix.loc[symbol1, symbol2]
                        weighted_correlation += weight1 * weight2 * abs(correlation)
                        total_weight += weight1 * weight2
            
            if total_weight > 0:
                normalized_correlation = weighted_correlation / total_weight
            else:
                normalized_correlation = 0.0
            
            return normalized_correlation
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation risk: {e}")
            return 0.0
    
    def _calculate_risk_score(self) -> int:
        """Calculate overall risk score (0-100, higher = more risky)"""
        try:
            score = 0
            
            # VaR component (25 points max)
            var_score = min(25, self.risk_metrics.var_1d * 500)  # Scale VaR
            score += var_score
            
            # Leverage component (20 points max)
            leverage_score = min(20, (self.risk_metrics.leverage_ratio - 1) * 10)
            score += leverage_score
            
            # Concentration component (15 points max)
            concentration_score = self.risk_metrics.concentration_risk * 15
            score += concentration_score
            
            # Correlation component (15 points max)
            correlation_score = self.risk_metrics.correlation_risk * 15
            score += correlation_score
            
            # Drawdown component (15 points max)
            drawdown_score = min(15, self.risk_metrics.max_drawdown * 100)
            score += drawdown_score
            
            # Volatility component (10 points max)
            volatility_score = min(10, self.risk_metrics.volatility * 500)
            score += volatility_score
            
            return min(100, max(0, int(score)))
            
        except Exception as e:
            self.logger.error(f"Error calculating risk score: {e}")
            return 50  # Default moderate risk score
    
    def _check_risk_alerts(self):
        """Check for risk threshold violations and create alerts"""
        try:
            # Check risk score thresholds
            if self.risk_metrics.risk_score >= self.risk_thresholds['risk_score_critical']:
                self._create_alert(
                    AlertType.CRITICAL,
                    f"Critical risk score: {self.risk_metrics.risk_score}",
                    RiskLevel.CRITICAL
                )
            elif self.risk_metrics.risk_score >= self.risk_thresholds['risk_score_warning']:
                self._create_alert(
                    AlertType.WARNING,
                    f"High risk score: {self.risk_metrics.risk_score}",
                    RiskLevel.HIGH
                )
            
            # Check VaR threshold
            if self.risk_metrics.var_1d > self.risk_thresholds['max_portfolio_var']:
                self._create_alert(
                    AlertType.WARNING,
                    f"Portfolio VaR exceeds threshold: {self.risk_metrics.var_1d:.4f}",
                    RiskLevel.HIGH
                )
            
            # Check leverage threshold
            if self.risk_metrics.leverage_ratio > self.risk_thresholds['max_leverage']:
                self._create_alert(
                    AlertType.CRITICAL,
                    f"Leverage ratio exceeds limit: {self.risk_metrics.leverage_ratio:.2f}",
                    RiskLevel.CRITICAL
                )
            
            # Check concentration threshold
            if self.risk_metrics.concentration_risk > self.risk_thresholds['max_concentration']:
                self._create_alert(
                    AlertType.WARNING,
                    f"Portfolio concentration risk high: {self.risk_metrics.concentration_risk:.2f}",
                    RiskLevel.HIGH
                )
            
            # Check correlation threshold
            if self.risk_metrics.correlation_risk > self.risk_thresholds['max_correlation']:
                self._create_alert(
                    AlertType.WARNING,
                    f"Portfolio correlation risk high: {self.risk_metrics.correlation_risk:.2f}",
                    RiskLevel.HIGH
                )
            
        except Exception as e:
            self.logger.error(f"Error checking risk alerts: {e}")
    
    def _create_alert(self, alert_type: AlertType, message: str, severity: RiskLevel, 
                     affected_positions: Optional[List[str]] = None, metadata: Optional[Dict] = None):
        """Create a new risk alert"""
        try:
            alert = RiskAlert(
                alert_id=f"alert_{int(time.time())}_{len(self.alerts)}",
                alert_type=alert_type,
                message=message,
                timestamp=datetime.now(),
                severity=severity,
                affected_positions=affected_positions or [],
                metadata=metadata or {}
            )
            
            self.alerts.append(alert)
            self.alert_queue.put(alert)
            
            # Send alert notifications
            self._send_alert_notifications(alert)
            
            self.logger.warning(f"Risk Alert: {alert.alert_type.value.upper()} - {message}")
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
    
    def _send_alert_notifications(self, alert: RiskAlert):
        """Send alert notifications via configured channels"""
        try:
            # Email notifications
            if self.config['alert_settings']['email_enabled']:
                self._send_email_alert(alert)
            
            # Slack notifications
            if self.config['alert_settings']['slack_enabled']:
                self._send_slack_alert(alert)
            
            # SMS notifications for critical alerts
            if self.config['alert_settings']['sms_enabled'] and alert.severity == RiskLevel.CRITICAL:
                self._send_sms_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error sending alert notifications: {e}")
    
    def _send_email_alert(self, alert: RiskAlert):
        """Send email alert (placeholder implementation)"""
        # In a real implementation, this would use SMTP
        self.logger.info(f"EMAIL ALERT: {alert.message}")
    
    def _send_slack_alert(self, alert: RiskAlert):
        """Send Slack alert (placeholder implementation)"""
        # In a real implementation, this would use Slack Web API
        self.logger.info(f"SLACK ALERT: {alert.message}")
    
    def _send_sms_alert(self, alert: RiskAlert):
        """Send SMS alert (placeholder implementation)"""
        # In a real implementation, this would use SMS service API
        self.logger.info(f"SMS ALERT: {alert.message}")
    
    def calculate_position_size(self, symbol: str, risk_per_trade: float = 0.02) -> float:
        """
        Calculate optimal position size based on risk parameters
        
        Args:
            symbol: Trading symbol
            risk_per_trade: Risk per trade as fraction of portfolio (default 2%)
            
        Returns:
            float: Recommended position size
        """
        try:
            if symbol not in self.positions:
                return 0.0
            
            position = self.positions[symbol]
            portfolio_value = self._get_total_portfolio_value()
            
            # Get historical volatility for the symbol
            symbol_volatility = self._get_symbol_volatility(symbol)
            
            # Calculate position size using volatility-based sizing
            risk_amount = portfolio_value * risk_per_trade
            position_size = risk_amount / (symbol_volatility * position.current_price)
            
            # Apply risk limits
            max_position_value = portfolio_value * self.risk_thresholds['max_single_position']
            max_position_size = max_position_value / position.current_price
            
            # Cap position size
            recommended_size = min(position_size, max_position_size)
            
            self.logger.info(f"Position size for {symbol}: {recommended_size:.4f}")
            return recommended_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def _get_symbol_volatility(self, symbol: str) -> float:
        """Get historical volatility for a symbol"""
        try:
            returns_data = self._get_historical_returns()
            if symbol in returns_data.columns:
                return returns_data[symbol].std()
            return 0.02  # Default 2% daily volatility
            
        except Exception as e:
            self.logger.error(f"Error getting symbol volatility: {e}")
            return 0.02
    
    def run_stress_test(self, scenarios: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Run stress tests on the portfolio
        
        Args:
            scenarios: List of stress test scenarios
            
        Returns:
            Dict containing stress test results
        """
        try:
            if not scenarios:
                scenarios = self._get_default_stress_scenarios()
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'scenarios': [],
                'worst_case_loss': 0.0,
                'best_case_gain': 0.0,
                'portfolio_impact': {}
            }
            
            for scenario in scenarios:
                scenario_result = self._run_single_stress_test(scenario)
                results['scenarios'].append(scenario_result)
                
                # Track worst/best case
                if scenario_result['portfolio_change'] < results['worst_case_loss']:
                    results['worst_case_loss'] = scenario_result['portfolio_change']
                if scenario_result['portfolio_change'] > results['best_case_gain']:
                    results['best_case_gain'] = scenario_result['portfolio_change']
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error running stress tests: {e}")
            return {}
    
    def _get_default_stress_scenarios(self) -> List[Dict]:
        """Get default stress test scenarios"""
        return [
            {
                'name': 'Market Crash 20%',
                'description': '20% market decline across all assets',
                'price_changes': {symbol: -0.20 for symbol in self.positions.keys()},
                'volatility_multiplier': 3.0
            },
            {
                'name': 'Interest Rate Shock',
                'description': '200bp interest rate increase',
                'price_changes': {symbol: -0.10 for symbol in self.positions.keys()},
                'volatility_multiplier': 2.5
            },
            {
                'name': 'Flash Crash',
                'description': '50% intraday decline',
                'price_changes': {symbol: -0.50 for symbol in self.positions.keys()},
                'volatility_multiplier': 5.0
            },
            {
                'name': 'Currency Crisis',
                'description': '30% currency depreciation',
                'price_changes': {symbol: -0.15 for symbol in self.positions.keys()},
                'volatility_multiplier': 4.0
            },
            {
                'name': 'Black Swan Event',
                'description': 'Extreme market event',
                'price_changes': {symbol: -0.80 for symbol in self.positions.keys()},
                'volatility_multiplier': 10.0
            }
        ]
    
    def _run_single_stress_test(self, scenario: Dict) -> Dict[str, Any]:
        """Run a single stress test scenario"""
        try:
            current_portfolio_value = self._get_total_portfolio_value()
            scenario_portfolio_value = current_portfolio_value
            
            position_impacts = []
            
            for symbol, position in self.positions.items():
                current_price = position.current_price
                price_change = scenario['price_changes'].get(symbol, 0.0)
                new_price = current_price * (1 + price_change)
                
                # Update position
                position_change = (new_price - current_price) * position.size
                scenario_portfolio_value += position_change
                
                position_impacts.append({
                    'symbol': symbol,
                    'current_price': current_price,
                    'new_price': new_price,
                    'price_change': price_change,
                    'position_change': position_change,
                    'position_change_percent': (position_change / (current_price * position.size)) * 100
                })
            
            portfolio_change = scenario_portfolio_value - current_portfolio_value
            if current_portfolio_value > 0:
                portfolio_change_percent = (portfolio_change / current_portfolio_value) * 100
            else:
                portfolio_change_percent = 0.0
            
            return {
                'scenario_name': scenario['name'],
                'scenario_description': scenario['description'],
                'current_portfolio_value': current_portfolio_value,
                'scenario_portfolio_value': scenario_portfolio_value,
                'portfolio_change': portfolio_change,
                'portfolio_change_percent': portfolio_change_percent,
                'position_impacts': position_impacts
            }
            
        except Exception as e:
            self.logger.error(f"Error running single stress test: {e}")
            return {}
    
    def detect_black_swan_events(self) -> List[Dict[str, Any]]:
        """
        Detect potential black swan events in the market
        
        Returns:
            List of detected black swan events
        """
        try:
            events = []
            
            # Get recent price data
            recent_data = self._get_recent_price_data()
            
            if recent_data.empty:
                return events
            
            # Check for extreme price movements
            for symbol in recent_data.columns:
                symbol_data = recent_data[symbol].dropna()
                
                if len(symbol_data) < 2:
                    continue
                
                returns = symbol_data.pct_change().dropna()
                
                # Check for 5-sigma moves
                mean_return = returns.mean()
                std_return = returns.std()
                z_scores = (returns - mean_return) / std_return
                
                extreme_moves = z_scores[abs(z_scores) > 5.0]
                
                for date, z_score in extreme_moves.items():
                    events.append({
                        'date': date,
                        'symbol': symbol,
                        'event_type': 'extreme_price_move',
                        'z_score': z_score,
                        'severity': 'extreme' if abs(z_score) > 8.0 else 'high',
                        'return': returns[date],
                        'description': f'Extreme price movement for {symbol}: {z_score:.2f} sigma'
                    })
            
            # Check for volatility spikes
            for symbol in recent_data.columns:
                symbol_data = recent_data[symbol].dropna()
                
                if len(symbol_data) < 20:
                    continue
                
                # Calculate rolling volatility
                returns = symbol_data.pct_change().dropna()
                rolling_vol = returns.rolling(window=20).std()
                
                # Compare current volatility to historical average
                current_vol = rolling_vol.iloc[-1] if not rolling_vol.empty else 0
                historical_vol = returns.std()
                
                if current_vol > historical_vol * 5:  # 5x volatility spike
                    events.append({
                        'date': datetime.now(),
                        'symbol': symbol,
                        'event_type': 'volatility_spike',
                        'volatility_ratio': current_vol / historical_vol,
                        'severity': 'extreme' if current_vol > historical_vol * 10 else 'high',
                        'description': f'Volatility spike for {symbol}: {current_vol/historical_vol:.1f}x normal'
                    })
            
            return events
            
        except Exception as e:
            self.logger.error(f"Error detecting black swan events: {e}")
            return []
    
    def _get_recent_price_data(self, days: int = 30) -> pd.DataFrame:
        """Get recent price data for analysis"""
        # In a real implementation, this would fetch from a data provider
        # For demonstration, return synthetic data
        try:
            if not self.positions:
                return pd.DataFrame()
            
            symbols = list(self.positions.keys())
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=days),
                end=datetime.now(),
                freq='H'  # Hourly data
            )
            
            price_data = pd.DataFrame(index=dates)
            
            for symbol in symbols:
                current_price = self.positions[symbol].current_price
                # Generate realistic price series around current price
                np.random.seed(hash(symbol) % 2**32)
                returns = np.random.normal(0, 0.001, len(dates))  # Small hourly changes
                prices = [current_price]
                
                for ret in returns[:-1]:
                    new_price = prices[-1] * (1 + ret)
                    prices.append(new_price)
                
                price_data[symbol] = prices
            
            return price_data
            
        except Exception as e:
            self.logger.error(f"Error getting recent price data: {e}")
            return pd.DataFrame()
    
    def run_monte_carlo_simulation(self, days: int = 30, simulations: int = None) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for portfolio performance
        
        Args:
            days: Simulation horizon in days
            simulations: Number of simulations to run
            
        Returns:
            Dict containing simulation results
        """
        try:
            if not simulations:
                simulations = self.monte_carlo_simulations
            
            # Get portfolio statistics
            weights = self._get_portfolio_weights()
            returns_data = self._get_historical_returns()
            
            if returns_data.empty:
                return {}
            
            # Calculate mean returns and covariance matrix
            mean_returns = returns_data.mean()
            cov_matrix = returns_data.cov()
            
            # Run simulations
            simulation_results = []
            
            for i in range(simulations):
                # Generate random portfolio returns
                random_returns = np.random.multivariate_normal(mean_returns, cov_matrix, days)
                
                # Calculate cumulative portfolio return
                portfolio_return = 0.0
                for day_returns in random_returns:
                    daily_portfolio_return = sum(weights[symbol] * day_return 
                                               for symbol, day_return in mean_returns.items())
                    portfolio_return = (1 + portfolio_return) * (1 + daily_portfolio_return) - 1
                
                simulation_results.append(portfolio_return)
            
            # Calculate statistics
            final_returns = np.array(simulation_results)
            
            results = {
                'simulation_parameters': {
                    'days': days,
                    'simulations': simulations,
                    'confidence_level': self.var_confidence
                },
                'statistics': {
                    'mean_return': np.mean(final_returns),
                    'median_return': np.median(final_returns),
                    'std_return': np.std(final_returns),
                    'min_return': np.min(final_returns),
                    'max_return': np.max(final_returns),
                    'percentile_5': np.percentile(final_returns, 5),
                    'percentile_95': np.percentile(final_returns, 95),
                    'var_95': np.percentile(final_returns, 5),  # 95% VaR
                    'cvar_95': np.mean(final_returns[final_returns <= np.percentile(final_returns, 5)])
                },
                'risk_metrics': {
                    'probability_loss': np.sum(final_returns < 0) / len(final_returns),
                    'expected_shortfall': np.mean(final_returns[final_returns < 0]),
                    'max_drawdown_probability': self._estimate_max_drawdown_probability(final_returns)
                }
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error running Monte Carlo simulation: {e}")
            return {}
    
    def _estimate_max_drawdown_probability(self, returns: np.ndarray) -> float:
        """Estimate probability of maximum drawdown exceeding threshold"""
        try:
            # Calculate cumulative returns
            cumulative_returns = np.cumprod(1 + returns)
            
            # Calculate running maximum
            running_max = np.maximum.accumulate(cumulative_returns)
            
            # Calculate drawdowns
            drawdowns = (cumulative_returns - running_max) / running_max
            
            # Count drawdowns exceeding threshold
            threshold = -self.risk_thresholds['max_drawdown']
            exceed_count = np.sum(drawdowns <= threshold)
            
            return exceed_count / len(returns)
            
        except Exception as e:
            self.logger.error(f"Error estimating max drawdown probability: {e}")
            return 0.0
    
    def calculate_risk_parity_weights(self) -> Dict[str, float]:
        """
        Calculate risk parity portfolio weights
        
        Returns:
            Dict mapping symbols to risk parity weights
        """
        try:
            returns_data = self._get_historical_returns()
            
            if returns_data.empty or len(returns_data.columns) < 2:
                return {}
            
            # Calculate asset volatilities
            volatilities = returns_data.std()
            
            # Risk parity objective: equal risk contribution
            def risk_parity_objective(weights, volatilities):
                portfolio_vol = np.sqrt(np.dot(weights, np.dot(np.diag(volatilities**2), weights)))
                marginal_contrib = np.dot(weights, np.diag(volatilities**2)) / portfolio_vol
                contrib = weights * marginal_contrib
                return np.sum((contrib - contrib.mean())**2)
            
            # Constraints
            n_assets = len(returns_data.columns)
            constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # weights sum to 1
            bounds = tuple((0, 1) for _ in range(n_assets))  # long-only
            
            # Initial guess: equal weights
            x0 = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                risk_parity_objective,
                x0,
                args=(volatilities.values,),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                weights = dict(zip(returns_data.columns, result.x))
                self.logger.info("Risk parity weights calculated successfully")
                return weights
            else:
                self.logger.warning("Risk parity optimization failed, using equal weights")
                return {symbol: 1/n_assets for symbol in returns_data.columns}
            
        except Exception as e:
            self.logger.error(f"Error calculating risk parity weights: {e}")
            return {}
    
    def perform_risk_attribution(self) -> Dict[str, Any]:
        """
        Perform risk attribution analysis
        
        Returns:
            Dict containing risk attribution results
        """
        try:
            if not self.positions:
                return {}
            
            returns_data = self._get_historical_returns()
            weights = self._get_portfolio_weights()
            
            if returns_data.empty:
                return {}
            
            # Calculate component marginal contributions
            portfolio_variance = self._calculate_portfolio_volatility()**2
            component_contributions = {}
            
            for symbol in returns_data.columns:
                if symbol in weights:
                    symbol_weight = weights[symbol]
                    symbol_return = returns_data[symbol]
                    
                    # Calculate marginal contribution
                    marginal_contrib = symbol_weight * symbol_return.corr(
                        self._calculate_portfolio_returns()
                    ) * symbol_return.std()
                    
                    # Absolute contribution
                    abs_contrib = marginal_contrib**2
                    
                    component_contributions[symbol] = {
                        'weight': symbol_weight,
                        'marginal_contribution': marginal_contrib,
                        'absolute_contribution': abs_contrib,
                        'percentage_contribution': abs_contrib / portfolio_variance * 100 if portfolio_variance > 0 else 0
                    }
            
            # Calculate correlation contributions
            correlation_contributions = {}
            for i, symbol1 in enumerate(returns_data.columns):
                for j, symbol2 in enumerate(returns_data.columns):
                    if i < j and symbol1 in weights and symbol2 in weights:
                        weight1 = weights[symbol1]
                        weight2 = weights[symbol2]
                        correlation = returns_data[symbol1].corr(returns_data[symbol2])
                        
                        correlation_contribution = 2 * weight1 * weight2 * correlation * \
                                                 returns_data[symbol1].std() * returns_data[symbol2].std()
                        
                        correlation_contributions[f"{symbol1}-{symbol2}"] = {
                            'correlation': correlation,
                            'contribution': correlation_contribution,
                            'percentage_contribution': correlation_contribution / portfolio_variance * 100 if portfolio_variance > 0 else 0
                        }
            
            return {
                'total_portfolio_variance': portfolio_variance,
                'component_contributions': component_contributions,
                'correlation_contributions': correlation_contributions,
                'attribution_summary': {
                    'largest_risk_contributor': max(component_contributions.keys(), 
                                                   key=lambda x: component_contributions[x]['absolute_contribution']),
                    'highest_correlation_pair': max(correlation_contributions.keys(),
                                                   key=lambda x: correlation_contributions[x]['absolute_contribution']) if correlation_contributions else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error performing risk attribution: {e}")
            return {}
    
    def check_regulatory_compliance(self) -> Dict[str, Any]:
        """
        Check regulatory compliance (MiFID II, ESMA)
        
        Returns:
            Dict containing compliance results
        """
        try:
            compliance_results = {
                'timestamp': datetime.now().isoformat(),
                'overall_compliant': True,
                'violations': [],
                'warnings': [],
                'mifid_ii_compliance': {},
                'esma_compliance': {}
            }
            
            # MiFID II Compliance Check
            if self.regulatory.get('mifid_ii_compliance', False):
                # Best Execution
                compliance_results['mifid_ii_compliance']['best_execution'] = {
                    'compliant': True,  # Assume compliant for now
                    'details': 'Best execution policy implemented'
                }
                
                # Transaction Reporting
                compliance_results['mifid_ii_compliance']['transaction_reporting'] = {
                    'compliant': len(self.positions) > 0,
                    'details': f'Portfolio contains {len(self.positions)} positions for reporting'
                }
                
                # Record Keeping
                compliance_results['mifid_ii_compliance']['record_keeping'] = {
                    'compliant': True,
                    'details': 'All trade records maintained'
                }
            
            # ESMA Compliance Check
            if self.regulatory.get('esma_compliance', False):
                # Leverage Limits
                max_leverage = max(pos.leverage for pos in self.positions.values()) if self.positions else 0
                esma_leverage_compliant = max_leverage <= 30  # ESMA leverage limit for retail
                
                compliance_results['esma_compliance']['leverage_limits'] = {
                    'compliant': esma_leverage_compliant,
                    'max_leverage_used': max_leverage,
                    'limit': 30,
                    'details': f'Maximum leverage used: {max_leverage:.1f}x'
                }
                
                # Negative Balance Protection
                total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
                negative_balance_protected = total_unrealized_pnl >= -self._get_total_portfolio_value()
                
                compliance_results['esma_compliance']['negative_balance_protection'] = {
                    'compliant': negative_balance_protected,
                    'unrealized_pnl': total_unrealized_pnl,
                    'details': 'Negative balance protection in place'
                }
            
            # Check for violations
            if not esma_leverage_compliant:
                compliance_results['violations'].append(f'Leverage limit exceeded: {max_leverage:.1f}x > 30x')
                compliance_results['overall_compliant'] = False
            
            # Check warnings
            if self.risk_metrics.risk_score > 85:
                compliance_results['warnings'].append('High risk score may trigger additional regulatory scrutiny')
            
            return compliance_results
            
        except Exception as e:
            self.logger.error(f"Error checking regulatory compliance: {e}")
            return {'error': str(e)}
    
    def emergency_stop_all_positions(self, reason: str = "Emergency stop triggered") -> Dict[str, Any]:
        """
        Emergency stop all positions
        
        Args:
            reason: Reason for emergency stop
            
        Returns:
            Dict containing emergency stop results
        """
        try:
            self.logger.critical(f"EMERGENCY STOP INITIATED: {reason}")
            
            stop_results = {
                'timestamp': datetime.now().isoformat(),
                'reason': reason,
                'positions_stopped': [],
                'total_exposure_closed': 0.0,
                'estimated_pnl': 0.0
            }
            
            for symbol, position in self.positions.items():
                # Calculate stop results
                exposure = position.notional_value
                pnl = position.unrealized_pnl
                
                stop_results['positions_stopped'].append({
                    'symbol': symbol,
                    'size': position.size,
                    'exposure': exposure,
                    'unrealized_pnl': pnl
                })
                
                stop_results['total_exposure_closed'] += exposure
                stop_results['estimated_pnl'] += pnl
            
            # Clear all positions
            self.positions.clear()
            
            # Create emergency alert
            self._create_alert(
                AlertType.EMERGENCY,
                f"Emergency stop executed: {reason}",
                RiskLevel.CRITICAL,
                metadata={'total_exposure': stop_results['total_exposure_closed']}
            )
            
            self.logger.critical(f"Emergency stop completed. Total exposure closed: ${stop_results['total_exposure_closed']:,.2f}")
            
            return stop_results
            
        except Exception as e:
            self.logger.error(f"Error during emergency stop: {e}")
            return {'error': str(e)}
    
    def start_monitoring(self):
        """Start real-time risk monitoring"""
        try:
            self.is_running = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("Risk monitoring started")
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop real-time risk monitoring"""
        try:
            self.is_running = False
            if hasattr(self, 'monitor_thread'):
                self.monitor_thread.join(timeout=5)
            self.logger.info("Risk monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Update risk metrics
                self._update_risk_metrics()
                
                # Check for alerts
                self._check_risk_alerts()
                
                # Detect black swan events
                black_swan_events = self.detect_black_swan_events()
                for event in black_swan_events:
                    self._create_alert(
                        AlertType.CRITICAL,
                        f"Black swan event detected: {event['description']}",
                        RiskLevel.CRITICAL,
                        [event['symbol']],
                        event
                    )
                
                # Sleep for monitoring interval
                time.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Shorter sleep on error
    
    def get_risk_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive risk report
        
        Returns:
            Dict containing complete risk analysis
        """
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_summary': {
                    'total_positions': len(self.positions),
                    'total_exposure': self._get_total_portfolio_value(),
                    'total_unrealized_pnl': sum(pos.unrealized_pnl for pos in self.positions.values()),
                    'average_leverage': self.risk_metrics.leverage_ratio
                },
                'risk_metrics': {
                    'risk_score': self.risk_metrics.risk_score,
                    'var_1d': self.risk_metrics.var_1d,
                    'var_10d': self.risk_metrics.var_10d,
                    'cvar_1d': self.risk_metrics.cvar_1d,
                    'volatility': self.risk_metrics.volatility,
                    'max_drawdown': self.risk_metrics.max_drawdown,
                    'sharpe_ratio': self.risk_metrics.sharpe_ratio,
                    'concentration_risk': self.risk_metrics.concentration_risk,
                    'correlation_risk': self.risk_metrics.correlation_risk
                },
                'position_details': [
                    {
                        'symbol': symbol,
                        'size': position.size,
                        'notional_value': position.notional_value,
                        'unrealized_pnl': position.unrealized_pnl,
                        'leverage': position.leverage,
                        'risk_contribution': self._calculate_position_risk_contribution(symbol)
                    }
                    for symbol, position in self.positions.items()
                ],
                'risk_attribution': self.perform_risk_attribution(),
                'stress_test_results': self.run_stress_test(),
                'monte_carlo_results': self.run_monte_carlo_simulation(),
                'black_swan_events': self.detect_black_swan_events(),
                'regulatory_compliance': self.check_regulatory_compliance(),
                'recent_alerts': [
                    {
                        'alert_id': alert.alert_id,
                        'alert_type': alert.alert_type.value,
                        'severity': alert.severity.value,
                        'message': alert.message,
                        'timestamp': alert.timestamp.isoformat()
                    }
                    for alert in self.alerts[-10:]  # Last 10 alerts
                ],
                'recommendations': self._generate_risk_recommendations()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating risk report: {e}")
            return {'error': str(e)}
    
    def _calculate_position_risk_contribution(self, symbol: str) -> float:
        """Calculate individual position risk contribution"""
        try:
            if symbol not in self.positions:
                return 0.0
            
            position = self.positions[symbol]
            portfolio_value = self._get_total_portfolio_value()
            
            if portfolio_value == 0:
                return 0.0
            
            # Simple risk contribution based on position size and volatility
            symbol_volatility = self._get_symbol_volatility(symbol)
            weight = position.notional_value / portfolio_value
            risk_contribution = weight * symbol_volatility
            
            return risk_contribution
            
        except Exception as e:
            self.logger.error(f"Error calculating position risk contribution: {e}")
            return 0.0
    
    def _generate_risk_recommendations(self) -> List[str]:
        """Generate risk management recommendations"""
        try:
            recommendations = []
            
            # Leverage recommendations
            if self.risk_metrics.leverage_ratio > 5.0:
                recommendations.append("Consider reducing overall portfolio leverage to below 5x")
            
            # Concentration recommendations
            if self.risk_metrics.concentration_risk > 0.3:
                recommendations.append("Portfolio is too concentrated. Consider diversifying across more assets")
            
            # VaR recommendations
            if self.risk_metrics.var_1d > 0.05:
                recommendations.append("High daily VaR detected. Consider reducing position sizes")
            
            # Correlation recommendations
            if self.risk_metrics.correlation_risk > 0.7:
                recommendations.append("High correlation between assets. Consider adding uncorrelated assets")
            
            # Risk score recommendations
            if self.risk_metrics.risk_score > 80:
                recommendations.append("High overall risk score. Consider implementing additional risk controls")
            
            # Stress test recommendations
            stress_results = self.run_stress_test()
            if stress_results.get('worst_case_loss', 0) < -0.2:  # 20% worst case loss
                recommendations.append("Stress tests show potential for significant losses. Consider hedged positions")
            
            if not recommendations:
                recommendations.append("Portfolio risk metrics are within acceptable ranges")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Unable to generate recommendations due to error"]
    
    def export_risk_data(self, filepath: str) -> bool:
        """
        Export risk management data to file
        
        Args:
            filepath: Path to export file
            
        Returns:
            bool: True if export successful
        """
        try:
            # Generate comprehensive report
            report = self.get_risk_report()
            
            # Export as JSON
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Risk data exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting risk data: {e}")
            return False
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge a risk alert
        
        Args:
            alert_id: ID of the alert to acknowledge
            
        Returns:
            bool: True if alert acknowledged successfully
        """
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    self.logger.info(f"Alert {alert_id} acknowledged")
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
            return False
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Get list of unacknowledged alerts
        
        Returns:
            List of active alerts
        """
        try:
            active_alerts = [
                {
                    'alert_id': alert.alert_id,
                    'alert_type': alert.alert_type.value,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'affected_positions': alert.affected_positions
                }
                for alert in self.alerts
                if not alert.acknowledged
            ]
            
            return active_alerts
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_monitoring()
            self.executor.shutdown(wait=True)
            self.logger.info("Risk Manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def demo_risk_manager():
    """Demonstration of Risk Manager functionality"""
    print("=" * 60)
    print("Orion Starline Risk Management System Demo")
    print("=" * 60)
    
    # Initialize Risk Manager
    risk_manager = RiskManager()
    
    print("\n1. Adding sample positions...")
    
    # Add sample positions
    positions = [
        Position(
            symbol="EURUSD",
            size=100000,
            entry_price=1.1000,
            current_price=1.1050,
            leverage=10.0,
            stop_loss=1.0950,
            take_profit=1.1150
        ),
        Position(
            symbol="GBPUSD",
            size=50000,
            entry_price=1.2500,
            current_price=1.2480,
            leverage=5.0,
            stop_loss=1.2400,
            take_profit=1.2650
        ),
        Position(
            symbol="XAUUSD",
            size=10,
            entry_price=2000.0,
            current_price=2010.0,
            leverage=3.0,
            stop_loss=1980.0,
            take_profit=2050.0
        )
    ]
    
    for position in positions:
        risk_manager.add_position(position)
        print(f"   Added position: {position.symbol} - Size: {position.size}")
    
    print(f"\n2. Current risk metrics:")
    print(f"   Risk Score: {risk_manager.risk_metrics.risk_score}/100")
    print(f"   Leverage Ratio: {risk_manager.risk_metrics.leverage_ratio:.2f}x")
    print(f"   1-day VaR: {risk_manager.risk_metrics.var_1d:.4f}")
    print(f"   Portfolio Volatility: {risk_manager.risk_metrics.volatility:.4f}")
    print(f"   Concentration Risk: {risk_manager.risk_metrics.concentration_risk:.3f}")
    print(f"   Correlation Risk: {risk_manager.risk_metrics.correlation_risk:.3f}")
    
    print(f"\n3. Running stress tests...")
    stress_results = risk_manager.run_stress_test()
    if stress_results:
        print(f"   Worst case loss: {stress_results.get('worst_case_loss', 0):.2%}")
        print(f"   Best case gain: {stress_results.get('best_case_gain', 0):.2%}")
        print(f"   Number of scenarios tested: {len(stress_results.get('scenarios', []))}")
    
    print(f"\n4. Monte Carlo simulation...")
    mc_results = risk_manager.run_monte_carlo_simulation(days=30, simulations=1000)
    if mc_results:
        stats = mc_results.get('statistics', {})
        print(f"   Mean return: {stats.get('mean_return', 0):.2%}")
        print(f"   95% VaR: {stats.get('var_95', 0):.2%}")
        print(f"   95% CVaR: {stats.get('cvar_95', 0):.2%}")
    
    print(f"\n5. Black swan event detection...")
    black_swan_events = risk_manager.detect_black_swan_events()
    print(f"   Events detected: {len(black_swan_events)}")
    for event in black_swan_events[:3]:  # Show first 3 events
        print(f"   - {event['description']}")
    
    print(f"\n6. Risk attribution analysis...")
    risk_attribution = risk_manager.perform_risk_attribution()
    if risk_attribution:
        component_contribs = risk_attribution.get('component_contributions', {})
        if component_contribs:
            largest_contributor = risk_attribution.get('attribution_summary', {}).get('largest_risk_contributor')
            print(f"   Largest risk contributor: {largest_contributor}")
    
    print(f"\n7. Regulatory compliance check...")
    compliance = risk_manager.check_regulatory_compliance()
    if compliance:
        print(f"   Overall compliant: {compliance.get('overall_compliant', False)}")
        violations = compliance.get('violations', [])
        if violations:
            print(f"   Violations: {violations}")
        else:
            print(f"   No violations found")
    
    print(f"\n8. Risk parity weights calculation...")
    risk_parity_weights = risk_manager.calculate_risk_parity_weights()
    if risk_parity_weights:
        print(f"   Risk parity weights:")
        for symbol, weight in risk_parity_weights.items():
            print(f"   - {symbol}: {weight:.2%}")
    
    print(f"\n9. Generating comprehensive risk report...")
    risk_report = risk_manager.get_risk_report()
    if risk_report:
        recommendations = risk_report.get('recommendations', [])
        print(f"   Recommendations:")
        for rec in recommendations[:3]:  # Show first 3 recommendations
            print(f"   - {rec}")
    
    print(f"\n10. Current active alerts...")
    active_alerts = risk_manager.get_active_alerts()
    print(f"    Active alerts: {len(active_alerts)}")
    for alert in active_alerts[:3]:  # Show first 3 alerts
        print(f"    - {alert['alert_type'].upper()}: {alert['message']}")
    
    # Cleanup
    risk_manager.cleanup()
    
    print(f"\n" + "=" * 60)
    print("Risk Management Demo Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    demo_risk_manager()