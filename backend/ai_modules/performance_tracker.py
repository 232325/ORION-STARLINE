"""
Performance Tracker Module - Orion Starline AI Trading System
Author: AI Development Team
Description: Comprehensive performance tracking and analysis system
"""

import asyncio
import numpy as np
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict
import statistics
import math
import warnings
warnings.filterwarnings('ignore')


class PerformanceMetric(Enum):
    """Performance metric types"""
    ACCURACY = "accuracy"
    WIN_RATE = "win_rate"
    PROFIT_LOSS = "profit_loss"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    CALMAR_RATIO = "calmar_ratio"
    INFORMATION_RATIO = "information_ratio"
    BETA = "beta"
    ALPHA = "alpha"
    VOLATILITY = "volatility"
    RESPONSE_TIME = "response_time"
    USER_ENGAGEMENT = "user_engagement"


@dataclass
class TradeData:
    """Individual trade data structure"""
    timestamp: datetime
    instrument: str
    signal_type: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    profit_loss: Optional[float]
    success: Optional[bool]
    duration: Optional[float]
    strategy: str
    risk_score: float
    confidence: float


@dataclass
class PerformanceSnapshot:
    """Performance snapshot at specific time"""
    timestamp: datetime
    total_trades: int
    winning_trades: int
    total_pnl: float
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    current_drawdown: float
    volatility: float
    avg_response_time: float
    active_strategies: int
    risk_exposure: float
    liquidity_score: float
    market_conditions: Dict[str, Any]
    benchmark_comparison: Dict[str, float]


@dataclass
class RiskMetrics:
    """Risk-related performance metrics"""
    var_95: float  # Value at Risk 95%
    var_99: float  # Value at Risk 99%
    expected_shortfall: float
    beta: float
    correlation: float
    tracking_error: float
    information_ratio: float
    calmar_ratio: float
    sortino_ratio: float


class PerformanceTracker:
    """
    Advanced Performance Tracking System
    Comprehensive analytics for AI trading performance
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.logger = self._setup_logging()
        
        # Data storage
        self.trades: List[TradeData] = []
        self.snapshots: List[PerformanceSnapshot] = []
        self.benchmarks: Dict[str, pd.DataFrame] = {}
        self.metrics_history: Dict[str, List[float]] = defaultdict(list)
        
        # Real-time tracking
        self.current_positions: Dict[str, float] = {}
        self.active_strategies: Dict[str, Dict] = {}
        self.risk_parameters: Dict[str, float] = {}
        
        # Performance thresholds
        self.alert_thresholds: Dict[str, Tuple[float, float]] = {
            'win_rate': (0.3, 0.8),
            'sharpe_ratio': (-2.0, 5.0),
            'max_drawdown': (0.0, 0.3),
            'var_95': (0.0, 0.15),
            'response_time': (0.1, 5.0)
        }
        
        # Machine learning components
        self.prediction_models: Dict[str, Any] = {}
        self.ensemble_weights: Dict[str, float] = {}
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            'data_retention_days': 365,
            'calculation_frequency': '1h',
            'benchmark_tickers': ['SPY', 'QQQ', 'VIX'],
            'risk_free_rate': 0.02,
            'rebalance_frequency': '1d',
            'lookback_periods': [30, 90, 180, 365],
            'enable_predictions': True,
            'enable_attribution': True,
            'ml_model_config': {
                'ensemble_size': 5,
                'cross_validation_folds': 5,
                'feature_importance_threshold': 0.1
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('PerformanceTracker')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def add_trade(self, trade: TradeData) -> None:
        """
        Add a new trade to tracking system
        """
        try:
            self.trades.append(trade)
            self._update_current_positions(trade)
            self._calculate_real_time_metrics()
            self.logger.info(f"Added trade: {trade.instrument} - ${trade.profit_loss:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error adding trade: {e}")
    
    def add_snapshot(self, snapshot: PerformanceSnapshot) -> None:
        """
        Add performance snapshot
        """
        self.snapshots.append(snapshot)
        self._update_metrics_history(snapshot)
    
    def _update_current_positions(self, trade: TradeData) -> None:
        """Update current positions based on trade"""
        instrument = trade.instrument
        
        if trade.signal_type == 'BUY':
            if instrument in self.current_positions:
                self.current_positions[instrument] += trade.quantity
            else:
                self.current_positions[instrument] = trade.quantity
        else:  # SELL
            if instrument in self.current_positions:
                self.current_positions[instrument] -= trade.quantity
            else:
                self.current_positions[instrument] = -trade.quantity
    
    def _update_metrics_history(self, snapshot: PerformanceSnapshot) -> None:
        """Update metrics history for time series analysis"""
        metrics = asdict(snapshot)
        for metric, value in metrics.items():
            if isinstance(value, (int, float)) and not metric == 'timestamp':
                self.metrics_history[metric].append(value)
    
    def _calculate_real_time_metrics(self) -> Dict[str, float]:
        """Calculate real-time performance metrics"""
        if not self.trades:
            return {}
        
        recent_trades = self._get_recent_trades(30)  # Last 30 days
        
        return {
            'real_time_pnl': self._calculate_total_pnl(recent_trades),
            'real_time_win_rate': self._calculate_win_rate(recent_trades),
            'real_time_sharpe': self._calculate_sharpe_ratio(recent_trades),
            'current_exposure': self._calculate_exposure(),
            'daily_pnl': self._calculate_daily_pnl(),
            'volatility_estimate': self._estimate_volatility(recent_trades),
            'drawdown_current': self._calculate_current_drawdown()
        }
    
    def _get_recent_trades(self, days: int) -> List[TradeData]:
        """Get trades from recent period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [t for t in self.trades if t.timestamp >= cutoff_date]
    
    def _calculate_total_pnl(self, trades: List[TradeData]) -> float:
        """Calculate total profit/loss"""
        return sum(t.profit_loss for t in trades if t.profit_loss is not None)
    
    def _calculate_win_rate(self, trades: List[TradeData]) -> float:
        """Calculate win rate"""
        if not trades:
            return 0.0
        
        successful_trades = [t for t in trades if t.success is True]
        return len(successful_trades) / len(trades)
    
    def _calculate_sharpe_ratio(self, trades: List[TradeData], risk_free_rate: float = None) -> float:
        """Calculate Sharpe ratio"""
        if not trades or len(trades) < 2:
            return 0.0
        
        if risk_free_rate is None:
            risk_free_rate = self.config['risk_free_rate']
        
        returns = [t.profit_loss for t in trades if t.profit_loss is not None]
        
        if not returns or statistics.stdev(returns) == 0:
            return 0.0
        
        excess_returns = [r - risk_free_rate/252 for r in returns]  # Daily risk-free rate
        return statistics.mean(excess_returns) / statistics.stdev(excess_returns)
    
    def _calculate_exposure(self) -> float:
        """Calculate current market exposure"""
        return sum(abs(pos) for pos in self.current_positions.values())
    
    def _calculate_daily_pnl(self) -> float:
        """Calculate daily P&L"""
        today = datetime.now().date()
        today_trades = [t for t in self.trades if t.timestamp.date() == today]
        return sum(t.profit_loss for t in today_trades if t.profit_loss is not None)
    
    def _estimate_volatility(self, trades: List[TradeData]) -> float:
        """Estimate current volatility"""
        if not trades:
            return 0.0
        
        returns = [t.profit_loss for t in trades if t.profit_loss is not None and t.profit_loss != 0]
        
        if len(returns) < 2:
            return 0.0
        
        return statistics.stdev(returns) * math.sqrt(252)  # Annualized volatility
    
    def _calculate_current_drawdown(self) -> float:
        """Calculate current drawdown from peak"""
        if not self.snapshots:
            return 0.0
        
        equity_curve = [s.total_pnl for s in self.snapshots]
        peak = max(equity_curve)
        current = equity_curve[-1]
        
        if peak == 0:
            return 0.0
        
        return (peak - current) / peak
    
    def get_performance_metrics(self, lookback_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics
        """
        try:
            recent_trades = self._get_recent_trades(lookback_days)
            
            # Basic metrics
            metrics = {
                'period_days': lookback_days,
                'total_trades': len(recent_trades),
                'total_pnl': self._calculate_total_pnl(recent_trades),
                'win_rate': self._calculate_win_rate(recent_trades),
                'average_trade': statistics.mean([t.profit_loss for t in recent_trades if t.profit_loss]) if recent_trades else 0,
                'best_trade': max([t.profit_loss for t in recent_trades if t.profit_loss]) if recent_trades else 0,
                'worst_trade': min([t.profit_loss for t in recent_trades if t.profit_loss]) if recent_trades else 0,
            }
            
            # Risk metrics
            risk_metrics = self._calculate_risk_metrics(recent_trades)
            metrics.update(risk_metrics)
            
            # Advanced metrics
            if len(recent_trades) >= 10:
                metrics.update(self._calculate_advanced_metrics(recent_trades))
            
            # Strategy performance
            metrics['strategy_performance'] = self._analyze_strategy_performance(recent_trades)
            
            # Market regime analysis
            metrics['regime_analysis'] = self._analyze_market_regimes()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    def _calculate_risk_metrics(self, trades: List[TradeData]) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics"""
        if not trades:
            return {}
        
        returns = [t.profit_loss for t in trades if t.profit_loss is not None]
        
        if len(returns) < 5:
            return {
                'volatility': 0.0,
                'max_drawdown': 0.0,
                'var_95': 0.0,
                'sortino_ratio': 0.0,
                'calmar_ratio': 0.0
            }
        
        # Basic risk metrics
        volatility = statistics.stdev(returns) * math.sqrt(252) if len(returns) > 1 else 0
        max_drawdown = self._calculate_max_drawdown(trades)
        var_95 = self._calculate_var(returns, 0.95)
        
        # Advanced ratios
        sharpe = self._calculate_sharpe_ratio(trades)
        sortino = self._calculate_sortino_ratio(trades)
        calmar = self._calculate_calmar_ratio(trades)
        
        return {
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'var_99': self._calculate_var(returns, 0.99),
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'tracking_error': self._calculate_tracking_error(trades),
            'information_ratio': self._calculate_information_ratio(trades)
        }
    
    def _calculate_max_drawdown(self, trades: List[TradeData]) -> float:
        """Calculate maximum drawdown"""
        if not trades:
            return 0.0
        
        cumulative_pnl = []
        running_total = 0
        
        for trade in trades:
            running_total += trade.profit_loss or 0
            cumulative_pnl.append(running_total)
        
        if not cumulative_pnl:
            return 0.0
        
        max_drawdown = 0
        peak = cumulative_pnl[0]
        
        for pnl in cumulative_pnl:
            if pnl > peak:
                peak = pnl
            else:
                drawdown = (peak - pnl) / abs(peak) if peak != 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _calculate_var(self, returns: List[float], confidence_level: float) -> float:
        """Calculate Value at Risk"""
        if not returns:
            return 0.0
        
        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        return abs(min(sorted_returns[:index]))
    
    def _calculate_sortino_ratio(self, trades: List[TradeData]) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        if not trades or len(trades) < 2:
            return 0.0
        
        returns = [t.profit_loss for t in trades if t.profit_loss is not None]
        risk_free_rate = self.config['risk_free_rate'] / 252  # Daily
        
        excess_returns = [r - risk_free_rate for r in returns]
        downside_returns = [r for r in excess_returns if r < 0]
        
        if not downside_returns or statistics.stdev(downside_returns) == 0:
            return 0.0
        
        avg_excess_return = statistics.mean(excess_returns)
        downside_deviation = statistics.stdev(downside_returns)
        
        return avg_excess_return / downside_deviation
    
    def _calculate_calmar_ratio(self, trades: List[TradeData]) -> float:
        """Calculate Calmar ratio"""
        total_pnl = self._calculate_total_pnl(trades)
        max_drawdown = self._calculate_max_drawdown(trades)
        
        if max_drawdown == 0:
            return 0.0
        
        return total_pnl / max_drawdown
    
    def _calculate_tracking_error(self, trades: List[TradeData]) -> float:
        """Calculate tracking error vs benchmark"""
        # This would require benchmark data
        # For now, return a placeholder
        return 0.0
    
    def _calculate_information_ratio(self, trades: List[TradeData]) -> float:
        """Calculate information ratio"""
        # This would require benchmark data
        # For now, return Sharpe ratio as proxy
        return self._calculate_sharpe_ratio(trades)
    
    def _calculate_advanced_metrics(self, trades: List[TradeData]) -> Dict[str, Any]:
        """Calculate advanced performance metrics"""
        returns = [t.profit_loss for t in trades if t.profit_loss is not None]
        
        if len(returns) < 10:
            return {}
        
        # Skewness and Kurtosis
        mean_return = statistics.mean(returns)
        stdev_return = statistics.stdev(returns) if len(returns) > 1 else 0
        
        if stdev_return == 0:
            return {}
        
        skewness = statistics.pstdev(returns) / (stdev_return ** 3) if len(returns) > 2 else 0
        kurtosis = statistics.pstdev(returns) / (stdev_return ** 4) if len(returns) > 3 else 0
        
        # Winning/losing streaks
        streaks = self._calculate_streaks(trades)
        
        return {
            'skewness': skewness,
            'kurtosis': kurtosis,
            'winning_streak': streaks['winning'],
            'losing_streak': streaks['losing'],
            'profit_factor': self._calculate_profit_factor(trades),
            'consecutive_wins': streaks['consecutive_wins'],
            'consecutive_losses': streaks['consecutive_losses']
        }
    
    def _calculate_streaks(self, trades: List[TradeData]) -> Dict[str, int]:
        """Calculate winning/losing streaks"""
        if not trades:
            return {'winning': 0, 'losing': 0, 'consecutive_wins': 0, 'consecutive_losses': 0}
        
        winning_streak = 0
        losing_streak = 0
        max_winning_streak = 0
        max_losing_streak = 0
        
        for trade in trades:
            if trade.success is True:
                winning_streak += 1
                losing_streak = 0
                max_winning_streak = max(max_winning_streak, winning_streak)
            elif trade.success is False:
                losing_streak += 1
                winning_streak = 0
                max_losing_streak = max(max_losing_streak, losing_streak)
        
        return {
            'winning': max_winning_streak,
            'losing': max_losing_streak,
            'consecutive_wins': winning_streak,
            'consecutive_losses': losing_streak
        }
    
    def _calculate_profit_factor(self, trades: List[TradeData]) -> float:
        """Calculate profit factor"""
        profits = sum(t.profit_loss for t in trades if t.profit_loss and t.profit_loss > 0)
        losses = abs(sum(t.profit_loss for t in trades if t.profit_loss and t.profit_loss < 0))
        
        if losses == 0:
            return float('inf') if profits > 0 else 0.0
        
        return profits / losses
    
    def _analyze_strategy_performance(self, trades: List[TradeData]) -> Dict[str, Any]:
        """Analyze performance by strategy"""
        strategy_performance = defaultdict(lambda: {
            'trades': 0, 'pnl': 0, 'win_rate': 0, 'avg_trade': 0
        })
        
        for trade in trades:
            strategy = trade.strategy
            if strategy not in strategy_performance:
                continue
            
            perf = strategy_performance[strategy]
            perf['trades'] += 1
            perf['pnl'] += trade.profit_loss or 0
        
        # Calculate additional metrics for each strategy
        for strategy, perf in strategy_performance.items():
            strategy_trades = [t for t in trades if t.strategy == strategy]
            if strategy_trades:
                winning_trades = [t for t in strategy_trades if t.success is True]
                perf['win_rate'] = len(winning_trades) / len(strategy_trades) if strategy_trades else 0
                perf['avg_trade'] = perf['pnl'] / perf['trades'] if perf['trades'] > 0 else 0
        
        return dict(strategy_performance)
    
    def _analyze_market_regimes(self) -> Dict[str, Any]:
        """Analyze performance in different market regimes"""
        return {
            'trend_following_performance': 0.0,
            'mean_reversion_performance': 0.0,
            'volatility_regime': 'unknown',
            'market_stress_indicator': 0.0
        }
    
    def get_benchmark_comparison(self, benchmarks: List[str] = None) -> Dict[str, Any]:
        """Compare performance against benchmarks"""
        if benchmarks is None:
            benchmarks = self.config['benchmark_tickers']
        
        # This would require actual benchmark data
        # For now, return placeholder comparison
        return {
            'vs_spy': {'outperformance': 0.0, 'tracking_error': 0.0},
            'vs_qqq': {'outperformance': 0.0, 'tracking_error': 0.0},
            'information_ratio': 0.0
        }
    
    def generate_performance_report(self, period_days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            metrics = self.get_performance_metrics(period_days)
            benchmark_comparison = self.get_benchmark_comparison()
            
            report = {
                'report_date': datetime.now().isoformat(),
                'report_period': f"Last {period_days} days",
                'executive_summary': self._generate_executive_summary(metrics),
                'performance_metrics': metrics,
                'benchmark_comparison': benchmark_comparison,
                'risk_assessment': self._assess_risk_level(metrics),
                'recommendations': self._generate_recommendations(metrics),
                'alerts': self._check_performance_alerts(metrics)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {}
    
    def _generate_executive_summary(self, metrics: Dict[str, Any]) -> str:
        """Generate executive summary"""
        win_rate = metrics.get('win_rate', 0) * 100
        total_pnl = metrics.get('total_pnl', 0)
        sharpe = metrics.get('sharpe_ratio', 0)
        
        summary = f"""
        Performance Summary (Last Period):
        • Total P&L: ${total_pnl:,.2f}
        • Win Rate: {win_rate:.1f}%
        • Sharpe Ratio: {sharpe:.2f}
        • Total Trades: {metrics.get('total_trades', 0)}
        """
        
        return summary.strip()
    
    def _assess_risk_level(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Assess current risk level"""
        var_95 = metrics.get('var_95', 0)
        max_drawdown = metrics.get('max_drawdown', 0)
        volatility = metrics.get('volatility', 0)
        
        risk_level = "LOW"
        if var_95 > 0.1 or max_drawdown > 0.2 or volatility > 0.3:
            risk_level = "HIGH"
        elif var_95 > 0.05 or max_drawdown > 0.1 or volatility > 0.2:
            risk_level = "MEDIUM"
        
        return {
            'overall_risk_level': risk_level,
            'var_risk': 'HIGH' if var_95 > 0.1 else 'MEDIUM' if var_95 > 0.05 else 'LOW',
            'drawdown_risk': 'HIGH' if max_drawdown > 0.2 else 'MEDIUM' if max_drawdown > 0.1 else 'LOW',
            'volatility_risk': 'HIGH' if volatility > 0.3 else 'MEDIUM' if volatility > 0.2 else 'LOW'
        }
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        win_rate = metrics.get('win_rate', 0)
        sharpe = metrics.get('sharpe_ratio', 0)
        max_drawdown = metrics.get('max_drawdown', 0)
        
        if win_rate < 0.4:
            recommendations.append("Win rate is below acceptable threshold. Consider improving signal quality.")
        
        if sharpe < 1.0:
            recommendations.append("Sharpe ratio suggests poor risk-adjusted returns. Review risk management.")
        
        if max_drawdown > 0.15:
            recommendations.append("High drawdown detected. Implement stricter position sizing and stop-loss rules.")
        
        if not recommendations:
            recommendations.append("Performance metrics are within acceptable ranges. Continue current strategy.")
        
        return recommendations
    
    def _check_performance_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check for performance alerts"""
        alerts = []
        
        # Check win rate alert
        win_rate = metrics.get('win_rate', 0.5)
        if win_rate < self.alert_thresholds['win_rate'][0]:
            alerts.append({
                'type': 'WIN_RATE_LOW',
                'message': f"Win rate ({win_rate:.1%}) below minimum threshold",
                'severity': 'HIGH'
            })
        elif win_rate > self.alert_thresholds['win_rate'][1]:
            alerts.append({
                'type': 'WIN_RATE_HIGH',
                'message': f"Win rate ({win_rate:.1%}) above normal range",
                'severity': 'INFO'
            })
        
        # Check drawdown alert
        max_drawdown = metrics.get('max_drawdown', 0)
        if max_drawdown > self.alert_thresholds['max_drawdown'][1]:
            alerts.append({
                'type': 'DRAWDOWN_HIGH',
                'message': f"Drawdown ({max_drawdown:.1%}) exceeds threshold",
                'severity': 'HIGH'
            })
        
        return alerts
    
    def export_performance_data(self, format_type: str = 'json') -> str:
        """Export performance data"""
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'trades': [asdict(trade) for trade in self.trades],
                'snapshots': [asdict(snapshot) for snapshot in self.snapshots],
                'metrics_history': dict(self.metrics_history)
            }
            
            if format_type.lower() == 'json':
                return json.dumps(export_data, indent=2, default=str)
            elif format_type.lower() == 'csv':
                # Convert to DataFrame and return CSV
                df = pd.DataFrame(export_data['trades'])
                return df.to_csv(index=False)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return ""


# Demo function
def demo_performance_tracker():
    """Demonstrate performance tracker capabilities"""
    print("=== Performance Tracker Demo ===\n")
    
    # Initialize tracker
    tracker = PerformanceTracker()
    
    # Generate sample trades
    import random
    from datetime import timedelta
    
    sample_strategies = ['momentum', 'mean_reversion', 'arbitrage', 'ml_prediction']
    sample_instruments = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'SPY']
    
    for i in range(100):
        trade = TradeData(
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30)),
            instrument=random.choice(sample_instruments),
            signal_type=random.choice(['BUY', 'SELL']),
            entry_price=random.uniform(1.0, 200.0),
            exit_price=random.uniform(1.0, 200.0),
            quantity=random.uniform(0.1, 10.0),
            profit_loss=random.uniform(-100, 200),
            success=random.choice([True, False]),
            duration=random.uniform(1, 1440),  # minutes
            strategy=random.choice(sample_strategies),
            risk_score=random.uniform(0.1, 0.9),
            confidence=random.uniform(0.5, 0.95)
        )
        tracker.add_trade(trade)
    
    # Generate performance report
    print("Generating performance metrics...")
    metrics = tracker.get_performance_metrics(30)
    
    print(f"Total Trades: {metrics.get('total_trades', 0)}")
    print(f"Total P&L: ${metrics.get('total_pnl', 0):,.2f}")
    print(f"Win Rate: {metrics.get('win_rate', 0):.1%}")
    print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"Max Drawdown: {metrics.get('max_drawdown', 0):.1%}")
    print(f"Volatility: {metrics.get('volatility', 0):.1%}")
    
    # Generate comprehensive report
    print("\nGenerating comprehensive report...")
    report = tracker.generate_performance_report(30)
    
    if report:
        print(f"Executive Summary: {report['executive_summary']}")
        print(f"Risk Level: {report['risk_assessment']['overall_risk_level']}")
        print(f"Recommendations: {len(report['recommendations'])} items")
        print(f"Alerts: {len(report['alerts'])} items")
    
    print("\n=== Demo Complete ===")
    
    return tracker


if __name__ == "__main__":
    demo_performance_tracker()