"""
Dashboard Data Module - Orion Starline AI Trading System
Author: AI Development Team
Description: Dashboard integration, visualization, and real-time data export
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, deque
import statistics
import math
import warnings
warnings.filterwarnings('ignore')

# Import other performance modules
from performance_tracker import PerformanceTracker, PerformanceSnapshot, TradeData
from real_time_monitor import RealTimeMonitor, Alert, MonitoringMode


class ChartType(Enum):
    """Chart types for visualization"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    CANDLESTICK = "candlestick"
    GAUGE = "gauge"
    TREEMAP = "treemap"


class TimeFrame(Enum):
    """Time frame options"""
    REAL_TIME = "1m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1M"
    QUARTER = "3M"
    YEAR = "1Y"


@dataclass
class ChartConfig:
    """Chart configuration"""
    title: str
    chart_type: ChartType
    x_axis: str
    y_axis: str
    series: List[str]
    timeframe: TimeFrame
    color_scheme: str = "default"
    show_legend: bool = True
    show_grid: bool = True
    height: int = 400
    width: int = 800


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    id: str
    title: str
    widget_type: str
    position: Dict[str, int]  # x, y, width, height
    data_source: str
    config: ChartConfig
    refresh_interval: int = 30  # seconds
    enabled: bool = True


@dataclass
class PerformanceAlert:
    """Performance alert for dashboard"""
    id: str
    timestamp: datetime
    alert_type: str
    title: str
    message: str
    severity: str
    metric_value: float
    threshold: float
    actions: List[str]
    acknowledged: bool = False


@dataclass
class BenchmarkData:
    """Benchmark comparison data"""
    symbol: str
    performance: Dict[str, float]
    correlation: float
    tracking_error: float
    information_ratio: float
    outperformance_periods: Dict[str, float]


class DashboardDataManager:
    """
    Advanced Dashboard Data Management System
    Real-time data preparation for performance dashboards
    """
    
    def __init__(self, performance_tracker: PerformanceTracker, 
                 real_time_monitor: RealTimeMonitor = None,
                 config: Dict[str, Any] = None):
        self.performance_tracker = performance_tracker
        self.real_time_monitor = real_time_monitor
        self.config = config or self._default_config()
        self.logger = self._setup_logging()
        
        # Dashboard data storage
        self.dashboard_cache: Dict[str, Any] = {}
        self.chart_data: Dict[str, List[Dict]] = defaultdict(list)
        self.aggregation_cache: Dict[str, pd.DataFrame] = {}
        
        # Real-time data streams
        self.data_streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.last_update: Dict[str, datetime] = {}
        
        # Widget configurations
        self.dashboard_widgets: Dict[str, DashboardWidget] = {}
        self.preset_dashboards: Dict[str, Dict] = {}
        
        # Benchmark data
        self.benchmark_data: Dict[str, BenchmarkData] = {}
        self.comparative_analysis: Dict[str, Any] = {}
        
        # Goal tracking
        self.goals: Dict[str, Dict] = {}
        self.achievements: List[Dict] = []
        
        # Performance history
        self.equity_curve: List[Dict] = []
        self.drawdown_periods: List[Dict] = []
        self.performance_attribution: Dict[str, Any] = {}
        
        self._initialize_presets()
        self._setup_dashboard_widgets()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            'dashboard_refresh_rate': 30,
            'cache_timeout_minutes': 5,
            'max_data_points': 10000,
            'enable_real_time': True,
            'default_timeframe': TimeFrame.DAY,
            'benchmark_symbols': ['SPY', 'QQQ', 'VIX', 'EURUSD'],
            'goal_tracking_enabled': True,
            'achievement_system_enabled': True
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('DashboardDataManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_presets(self) -> None:
        """Initialize preset dashboard configurations"""
        self.preset_dashboards = {
            'overview': {
                'name': 'Performance Overview',
                'description': 'Key performance metrics and summary',
                'widgets': [
                    'equity_curve',
                    'key_metrics',
                    'recent_trades',
                    'performance_alerts',
                    'goal_progress'
                ]
            },
            'detailed': {
                'name': 'Detailed Analysis',
                'description': 'Comprehensive performance analysis',
                'widgets': [
                    'equity_curve',
                    'drawdown_chart',
                    'return_distribution',
                    'strategy_performance',
                    'risk_metrics',
                    'benchmark_comparison'
                ]
            },
            'real_time': {
                'name': 'Real-time Monitor',
                'description': 'Live performance monitoring',
                'widgets': [
                    'real_time_metrics',
                    'live_alerts',
                    'system_health',
                    'trend_analysis',
                    'anomaly_detection'
                ]
            },
            'risk': {
                'name': 'Risk Management',
                'description': 'Risk analysis and monitoring',
                'widgets': [
                    'risk_metrics',
                    'var_analysis',
                    'correlation_matrix',
                    'stress_tests',
                    'position_analysis'
                ]
            }
        }
    
    def _setup_dashboard_widgets(self) -> None:
        """Setup default dashboard widgets"""
        widgets = [
            DashboardWidget(
                id="equity_curve",
                title="Equity Curve",
                widget_type="line_chart",
                position={"x": 0, "y": 0, "width": 8, "height": 4},
                data_source="equity_curve",
                config=ChartConfig(
                    title="Portfolio Equity Curve",
                    chart_type=ChartType.LINE,
                    x_axis="timestamp",
                    y_axis="equity",
                    series=["portfolio_equity", "benchmark_equity"],
                    timeframe=TimeFrame.DAY
                )
            ),
            DashboardWidget(
                id="key_metrics",
                title="Key Performance Metrics",
                widget_type="gauge_chart",
                position={"x": 8, "y": 0, "width": 4, "height": 4},
                data_source="key_metrics",
                config=ChartConfig(
                    title="Performance Dashboard",
                    chart_type=ChartType.GAUGE,
                    x_axis="metric",
                    y_axis="value",
                    series=["win_rate", "sharpe_ratio", "max_drawdown"],
                    timeframe=TimeFrame.REAL_TIME
                )
            ),
            DashboardWidget(
                id="recent_trades",
                title="Recent Trades",
                widget_type="table",
                position={"x": 0, "y": 4, "width": 6, "height": 4},
                data_source="recent_trades",
                config=ChartConfig(
                    title="Trading Activity",
                    chart_type=ChartType.TREEMAP,
                    x_axis="timestamp",
                    y_axis="profit_loss",
                    series=["instrument", "strategy"],
                    timeframe=TimeFrame.DAY
                )
            ),
            DashboardWidget(
                id="performance_alerts",
                title="Performance Alerts",
                widget_type="alert_list",
                position={"x": 6, "y": 4, "width": 6, "height": 4},
                data_source="performance_alerts",
                config=ChartConfig(
                    title="System Alerts",
                    chart_type=ChartType.BAR,
                    x_axis="timestamp",
                    y_axis="severity",
                    series=["alert_type"],
                    timeframe=TimeFrame.HOUR
                )
            ),
            DashboardWidget(
                id="drawdown_chart",
                title="Drawdown Analysis",
                widget_type="area_chart",
                position={"x": 0, "y": 8, "width": 6, "height": 3},
                data_source="drawdown_data",
                config=ChartConfig(
                    title="Drawdown Periods",
                    chart_type=ChartType.LINE,
                    x_axis="timestamp",
                    y_axis="drawdown",
                    series=["drawdown", "current_drawdown"],
                    timeframe=TimeFrame.DAY
                )
            ),
            DashboardWidget(
                id="strategy_performance",
                title="Strategy Performance",
                widget_type="bar_chart",
                position={"x": 6, "y": 8, "width": 6, "height": 3},
                data_source="strategy_metrics",
                config=ChartConfig(
                    title="Performance by Strategy",
                    chart_type=ChartType.BAR,
                    x_axis="strategy",
                    y_axis="total_return",
                    series=["win_rate", "sharpe_ratio"],
                    timeframe=TimeFrame.MONTH
                )
            )
        ]
        
        for widget in widgets:
            self.dashboard_widgets[widget.id] = widget
    
    def get_dashboard_data(self, dashboard_name: str = 'overview', 
                          timeframe: TimeFrame = None) -> Dict[str, Any]:
        """
        Get complete dashboard data for specified dashboard
        """
        try:
            if timeframe is None:
                timeframe = self.config['default_timeframe']
            
            if dashboard_name not in self.preset_dashboards:
                raise ValueError(f"Dashboard '{dashboard_name}' not found")
            
            dashboard_config = self.preset_dashboards[dashboard_name]
            
            # Get all widget data
            dashboard_data = {
                'dashboard_info': {
                    'name': dashboard_config['name'],
                    'description': dashboard_config['description'],
                    'last_updated': datetime.now().isoformat(),
                    'timeframe': timeframe.value
                },
                'widgets': {}
            }
            
            for widget_id in dashboard_config['widgets']:
                if widget_id in self.dashboard_widgets:
                    widget = self.dashboard_widgets[widget_id]
                    if widget.enabled:
                        widget_data = self._get_widget_data(widget, timeframe)
                        dashboard_data['widgets'][widget_id] = widget_data
            
            # Add summary statistics
            dashboard_data['summary'] = self._generate_dashboard_summary()
            
            # Cache the result
            cache_key = f"{dashboard_name}_{timeframe.value}"
            self.dashboard_cache[cache_key] = dashboard_data
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {}
    
    def _get_widget_data(self, widget: DashboardWidget, timeframe: TimeFrame) -> Dict[str, Any]:
        """Get data for specific widget"""
        try:
            data_source = widget.data_source
            
            if data_source == "equity_curve":
                return self._get_equity_curve_data(timeframe)
            elif data_source == "key_metrics":
                return self._get_key_metrics_data(timeframe)
            elif data_source == "recent_trades":
                return self._get_recent_trades_data(timeframe)
            elif data_source == "performance_alerts":
                return self._get_performance_alerts_data(timeframe)
            elif data_source == "drawdown_data":
                return self._get_drawdown_data(timeframe)
            elif data_source == "strategy_metrics":
                return self._get_strategy_performance_data(timeframe)
            elif data_source == "real_time_metrics":
                return self._get_real_time_metrics_data()
            elif data_source == "live_alerts":
                return self._get_live_alerts_data()
            elif data_source == "risk_metrics":
                return self._get_risk_metrics_data(timeframe)
            else:
                return {'error': f"Data source '{data_source}' not found"}
                
        except Exception as e:
            self.logger.error(f"Error getting widget data for {widget.id}: {e}")
            return {'error': str(e)}
    
    def _get_equity_curve_data(self, timeframe: TimeFrame) -> Dict[str, Any]:
        """Get equity curve data"""
        try:
            # Generate equity curve from trades
            if not self.performance_tracker.trades:
                return {'data': [], 'labels': []}
            
            trades = sorted(self.performance_tracker.trades, key=lambda x: x.timestamp)
            
            # Aggregate data by timeframe
            aggregated_data = self._aggregate_trades_by_timeframe(trades, timeframe)
            
            equity_curve = []
            running_total = 0
            
            for point in aggregated_data:
                running_total += point['profit_loss']
                equity_curve.append({
                    'timestamp': point['timestamp'].isoformat(),
                    'equity': running_total,
                    'period_pnl': point['profit_loss'],
                    'trades_count': point['trades_count']
                })
            
            # Add benchmark comparison if available
            benchmark_equity = self._get_benchmark_equity_curve(timeframe, len(equity_curve))
            
            return {
                'data': equity_curve,
                'benchmark': benchmark_equity,
                'chart_config': {
                    'x_axis': 'timestamp',
                    'y_axis': 'equity',
                    'series': ['equity', 'benchmark'],
                    'chart_type': 'line'
                },
                'statistics': {
                    'current_equity': equity_curve[-1]['equity'] if equity_curve else 0,
                    'peak_equity': max([p['equity'] for p in equity_curve]) if equity_curve else 0,
                    'total_return': ((equity_curve[-1]['equity'] if equity_curve else 0) - 100) / 100 if equity_curve else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting equity curve data: {e}")
            return {'data': [], 'error': str(e)}
    
    def _get_key_metrics_data(self, timeframe: TimeFrame) -> Dict[str, Any]:
        """Get key performance metrics data"""
        try:
            metrics = self.performance_tracker.get_performance_metrics(30)  # Last 30 days
            
            gauge_data = [
                {
                    'metric': 'Win Rate',
                    'value': metrics.get('win_rate', 0) * 100,
                    'max': 100,
                    'min': 0,
                    'threshold_low': 30,
                    'threshold_high': 80,
                    'unit': '%'
                },
                {
                    'metric': 'Sharpe Ratio',
                    'value': metrics.get('sharpe_ratio', 0),
                    'max': 5,
                    'min': -2,
                    'threshold_low': 0,
                    'threshold_high': 3,
                    'unit': ''
                },
                {
                    'metric': 'Max Drawdown',
                    'value': metrics.get('max_drawdown', 0) * 100,
                    'max': 30,
                    'min': 0,
                    'threshold_low': 5,
                    'threshold_high': 15,
                    'unit': '%'
                },
                {
                    'metric': 'Total P&L',
                    'value': metrics.get('total_pnl', 0),
                    'max': metrics.get('total_pnl', 0) * 2 if metrics.get('total_pnl', 0) > 0 else 1000,
                    'min': 0,
                    'threshold_low': 0,
                    'threshold_high': metrics.get('total_pnl', 0) if metrics.get('total_pnl', 0) > 0 else 500,
                    'unit': '$'
                }
            ]
            
            return {
                'gauges': gauge_data,
                'summary_stats': {
                    'total_trades': metrics.get('total_trades', 0),
                    'avg_trade': metrics.get('average_trade', 0),
                    'best_trade': metrics.get('best_trade', 0),
                    'worst_trade': metrics.get('worst_trade', 0),
                    'profit_factor': metrics.get('profit_factor', 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting key metrics data: {e}")
            return {'gauges': [], 'error': str(e)}
    
    def _get_recent_trades_data(self, timeframe: TimeFrame) -> Dict[str, Any]:
        """Get recent trades data for table/treemap"""
        try:
            if not self.performance_tracker.trades:
                return {'trades': [], 'summary': {}}
            
            # Get recent trades
            recent_trades = self._filter_trades_by_timeframe(
                self.performance_tracker.trades, timeframe
            )
            
            # Format for table
            table_data = []
            for trade in recent_trades[-20:]:  # Last 20 trades
                table_data.append({
                    'timestamp': trade.timestamp.isoformat(),
                    'instrument': trade.instrument,
                    'signal_type': trade.signal_type,
                    'entry_price': trade.entry_price,
                    'exit_price': trade.exit_price,
                    'quantity': trade.quantity,
                    'profit_loss': trade.profit_loss or 0,
                    'success': trade.success,
                    'duration_minutes': trade.duration,
                    'strategy': trade.strategy,
                    'risk_score': trade.risk_score,
                    'confidence': trade.confidence
                })
            
            # Summary by instrument
            instrument_summary = defaultdict(lambda: {
                'trades': 0, 'total_pnl': 0, 'win_rate': 0, 'avg_trade': 0
            })
            
            for trade in recent_trades:
                summary = instrument_summary[trade.instrument]
                summary['trades'] += 1
                summary['total_pnl'] += trade.profit_loss or 0
                if trade.success:
                    summary['wins'] = summary.get('wins', 0) + 1
            
            for instrument, data in instrument_summary.items():
                data['win_rate'] = data['wins'] / data['trades'] if data['trades'] > 0 else 0
                data['avg_trade'] = data['total_pnl'] / data['trades'] if data['trades'] > 0 else 0
                del data['wins']  # Remove temporary field
            
            return {
                'trades': table_data,
                'summary': dict(instrument_summary),
                'total_count': len(recent_trades)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting recent trades data: {e}")
            return {'trades': [], 'error': str(e)}
    
    def _get_performance_alerts_data(self, timeframe: TimeFrame) -> Dict[str, Any]:
        """Get performance alerts data"""
        try:
            alerts_data = []
            
            # Get alerts from real-time monitor
            if self.real_time_monitor:
                for alert in self.real_time_monitor.active_alerts.values():
                    alerts_data.append({
                        'id': alert.id,
                        'timestamp': alert.timestamp.isoformat(),
                        'title': alert.rule_name,
                        'message': alert.message,
                        'severity': alert.severity.value,
                        'metric': alert.metric,
                        'value': alert.current_value,
                        'threshold': alert.threshold,
                        'acknowledged': alert.acknowledged
                    })
                
                # Get recent alert history
                recent_alerts = [
                    alert for alert in self.real_time_monitor.alert_history
                    if alert.timestamp >= datetime.now() - timedelta(hours=24)
                ]
                
                for alert in recent_alerts[-10:]:  # Last 10 alerts
                    alerts_data.append({
                        'id': alert.id,
                        'timestamp': alert.timestamp.isoformat(),
                        'title': alert.rule_name,
                        'message': alert.message,
                        'severity': alert.severity.value,
                        'metric': alert.metric,
                        'value': alert.current_value,
                        'threshold': alert.threshold,
                        'acknowledged': alert.acknowledged
                    })
            
            # Sort by timestamp (most recent first)
            alerts_data.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Alert summary by severity
            severity_counts = defaultdict(int)
            for alert in alerts_data:
                severity_counts[alert['severity']] += 1
            
            return {
                'alerts': alerts_data[:20],  # Last 20 alerts
                'summary': {
                    'total_count': len(alerts_data),
                    'by_severity': dict(severity_counts),
                    'acknowledged_count': sum(1 for a in alerts_data if a['acknowledged'])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance alerts data: {e}")
            return {'alerts': [], 'error': str(e)}
    
    def _get_drawdown_data(self, timeframe: TimeFrame) -> Dict[str, Any]:
        """Get drawdown analysis data"""
        try:
            if not self.performance_tracker.snapshots:
                return {'data': [], 'summary': {}}
            
            # Calculate drawdown from equity curve
            equity_curve = []
            for snapshot in self.performance_tracker.snapshots:
                equity_curve.append({
                    'timestamp': snapshot.timestamp,
                    'equity': snapshot.total_pnl,
                    'peak': snapshot.total_pnl
                })
            
            # Calculate drawdown
            max_equity = 0
            drawdown_data = []
            
            for point in equity_curve:
                if point['equity'] > max_equity:
                    max_equity = point['equity']
                
                drawdown = (max_equity - point['equity']) / max_equity if max_equity > 0 else 0
                
                drawdown_data.append({
                    'timestamp': point['timestamp'].isoformat(),
                    'drawdown': drawdown * 100,  # Percentage
                    'equity': point['equity'],
                    'peak_equity': max_equity
                })
            
            # Current drawdown
            current_drawdown = drawdown_data[-1]['drawdown'] if drawdown_data else 0
            max_drawdown = max([d['drawdown'] for d in drawdown_data]) if drawdown_data else 0
            
            return {
                'data': drawdown_data,
                'summary': {
                    'current_drawdown': current_drawdown,
                    'max_drawdown': max_drawdown,
                    'drawdown_periods': len([d for d in drawdown_data if d['drawdown'] > 5])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting drawdown data: {e}")
            return {'data': [], 'error': str(e)}
    
    def _get_strategy_performance_data(self, timeframe: TimeFrame) -> Dict[str, Any]:
        """Get strategy performance data"""
        try:
            metrics = self.performance_tracker.get_performance_metrics(30)
            strategy_performance = metrics.get('strategy_performance', {})
            
            if not strategy_performance:
                return {'strategies': [], 'summary': {}}
            
            chart_data = []
            for strategy, perf in strategy_performance.items():
                chart_data.append({
                    'strategy': strategy,
                    'total_pnl': perf.get('pnl', 0),
                    'total_trades': perf.get('trades', 0),
                    'win_rate': perf.get('win_rate', 0) * 100,
                    'avg_trade': perf.get('avg_trade', 0),
                    'profit_factor': perf.get('pnl', 0) / max(1, perf.get('trades', 1))
                })
            
            return {
                'strategies': chart_data,
                'summary': {
                    'best_strategy': max(strategy_performance.items(), 
                                       key=lambda x: x[1].get('pnl', 0))[0] if strategy_performance else None,
                    'total_strategies': len(strategy_performance),
                    'average_win_rate': np.mean([p.get('win_rate', 0) for p in strategy_performance.values()]) * 100
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting strategy performance data: {e}")
            return {'strategies': [], 'error': str(e)}
    
    def _get_real_time_metrics_data(self) -> Dict[str, Any]:
        """Get real-time metrics data"""
        try:
            if not self.real_time_monitor:
                return {'metrics': {}, 'trends': {}}
            
            real_time_data = self.real_time_monitor.get_real_time_metrics()
            
            return {
                'metrics': real_time_data['performance_metrics'],
                'trends': real_time_data['trend_analysis'],
                'system_health': real_time_data['system_health'],
                'last_update': real_time_data['timestamp']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics data: {e}")
            return {'metrics': {}, 'error': str(e)}
    
    def _get_live_alerts_data(self) -> Dict[str, Any]:
        """Get live alerts data"""
        try:
            if not self.real_time_monitor:
                return {'alerts': []}
            
            live_alerts = []
            for alert in self.real_time_monitor.active_alerts.values():
                live_alerts.append(asdict(alert))
            
            return {
                'alerts': live_alerts,
                'count': len(live_alerts),
                'active_severities': list(set(a.severity.value for a in self.real_time_monitor.active_alerts.values()))
            }
            
        except Exception as e:
            self.logger.error(f"Error getting live alerts data: {e}")
            return {'alerts': [], 'error': str(e)}
    
    def _get_risk_metrics_data(self, timeframe: TimeFrame) -> Dict[str, Any]:
        """Get risk metrics data"""
        try:
            metrics = self.performance_tracker.get_performance_metrics(30)
            
            risk_data = {
                'var_95': metrics.get('var_95', 0) * 100,
                'var_99': metrics.get('var_99', 0) * 100,
                'volatility': metrics.get('volatility', 0) * 100,
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'sortino_ratio': metrics.get('sortino_ratio', 0),
                'max_drawdown': metrics.get('max_drawdown', 0) * 100,
                'calmar_ratio': metrics.get('calmar_ratio', 0),
                'tracking_error': metrics.get('tracking_error', 0)
            }
            
            # Risk level assessment
            risk_level = self._assess_risk_level(risk_data)
            
            return {
                'metrics': risk_data,
                'risk_level': risk_level,
                'thresholds': {
                    'var_95': 10,  # 10%
                    'var_99': 15,  # 15%
                    'volatility': 25,  # 25%
                    'max_drawdown': 15  # 15%
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk metrics data: {e}")
            return {'metrics': {}, 'error': str(e)}
    
    def _assess_risk_level(self, risk_data: Dict[str, float]) -> str:
        """Assess overall risk level"""
        risk_score = 0
        
        if risk_data.get('var_95', 0) > 10:
            risk_score += 2
        elif risk_data.get('var_95', 0) > 5:
            risk_score += 1
        
        if risk_data.get('max_drawdown', 0) > 15:
            risk_score += 2
        elif risk_data.get('max_drawdown', 0) > 10:
            risk_score += 1
        
        if risk_data.get('volatility', 0) > 25:
            risk_score += 1
        
        if risk_score >= 4:
            return "HIGH"
        elif risk_score >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_dashboard_summary(self) -> Dict[str, Any]:
        """Generate dashboard summary statistics"""
        try:
            metrics = self.performance_tracker.get_performance_metrics(30)
            
            return {
                'total_trades': metrics.get('total_trades', 0),
                'total_pnl': metrics.get('total_pnl', 0),
                'win_rate': metrics.get('win_rate', 0),
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'max_drawdown': metrics.get('max_drawdown', 0),
                'active_strategies': len(metrics.get('strategy_performance', {})),
                'last_trade': self.performance_tracker.trades[-1].timestamp.isoformat() if self.performance_tracker.trades else None,
                'system_status': 'healthy' if self.real_time_monitor and len(self.real_time_monitor.active_alerts) == 0 else 'alerts_active'
            }
            
        except Exception as e:
            self.logger.error(f"Error generating dashboard summary: {e}")
            return {}
    
    def _aggregate_trades_by_timeframe(self, trades: List[TradeData], timeframe: TimeFrame) -> List[Dict]:
        """Aggregate trades by specified timeframe"""
        if not trades:
            return []
        
        # Group trades by timeframe
        grouped_trades = defaultdict(list)
        
        for trade in trades:
            if timeframe == TimeFrame.REAL_TIME:
                key = trade.timestamp.replace(minute=0, second=0, microsecond=0)
            elif timeframe == TimeFrame.HOUR:
                key = trade.timestamp.replace(minute=0, second=0, microsecond=0)
            elif timeframe == TimeFrame.DAY:
                key = trade.timestamp.date()
            elif timeframe == TimeFrame.WEEK:
                # Get Monday of the week
                days_since_monday = trade.timestamp.weekday()
                monday = trade.timestamp - timedelta(days=days_since_monday)
                key = monday.date()
            elif timeframe == TimeFrame.MONTH:
                key = (trade.timestamp.year, trade.timestamp.month)
            else:
                key = trade.timestamp.date()
            
            grouped_trades[key].append(trade)
        
        # Aggregate data
        aggregated = []
        for period, period_trades in grouped_trades.items():
            total_pnl = sum(t.profit_loss or 0 for t in period_trades)
            
            aggregated.append({
                'timestamp': period if isinstance(period, datetime) else datetime.combine(period, datetime.min.time()),
                'profit_loss': total_pnl,
                'trades_count': len(period_trades)
            })
        
        return sorted(aggregated, key=lambda x: x['timestamp'])
    
    def _filter_trades_by_timeframe(self, trades: List[TradeData], timeframe: TimeFrame) -> List[TradeData]:
        """Filter trades by timeframe"""
        if not trades:
            return []
        
        current_time = datetime.now()
        
        if timeframe == TimeFrame.REAL_TIME:
            cutoff = current_time - timedelta(hours=1)
        elif timeframe == TimeFrame.HOUR:
            cutoff = current_time - timedelta(hours=24)
        elif timeframe == TimeFrame.DAY:
            cutoff = current_time - timedelta(days=7)
        elif timeframe == TimeFrame.WEEK:
            cutoff = current_time - timedelta(weeks=4)
        elif timeframe == TimeFrame.MONTH:
            cutoff = current_time - timedelta(days=30)
        else:
            cutoff = current_time - timedelta(days=30)
        
        return [t for t in trades if t.timestamp >= cutoff]
    
    def _get_benchmark_equity_curve(self, timeframe: TimeFrame, length: int) -> List[Dict]:
        """Get benchmark equity curve for comparison"""
        # This would fetch actual benchmark data
        # For now, return simulated data
        if length == 0:
            return []
        
        benchmark_curve = []
        for i in range(min(length, 100)):
            # Simulate benchmark performance (slightly positive trend)
            equity = 100 * (1 + 0.0005 * i)  # 0.05% daily growth
            benchmark_curve.append({
                'timestamp': (datetime.now() - timedelta(days=length-i)).isoformat(),
                'equity': equity
            })
        
        return benchmark_curve
    
    # Goal tracking and achievements
    def set_performance_goal(self, goal_id: str, goal_type: str, target_value: float, 
                           timeframe_days: int = 30) -> None:
        """Set performance goal"""
        self.goals[goal_id] = {
            'id': goal_id,
            'type': goal_type,
            'target_value': target_value,
            'timeframe_days': timeframe_days,
            'created_at': datetime.now(),
            'status': 'active'
        }
    
    def get_goal_progress(self) -> Dict[str, Any]:
        """Get progress on all active goals"""
        goal_progress = {}
        
        for goal_id, goal in self.goals.items():
            if goal['status'] != 'active':
                continue
            
            current_value = self._get_current_metric_value(goal['type'])
            progress = (current_value / goal['target_value']) * 100 if goal['target_value'] != 0 else 0
            
            goal_progress[goal_id] = {
                'goal': goal,
                'current_value': current_value,
                'progress_percent': min(progress, 100),
                'days_remaining': max(0, goal['timeframe_days'] - (datetime.now() - goal['created_at']).days)
            }
        
        return goal_progress
    
    def _get_current_metric_value(self, metric_type: str) -> float:
        """Get current value for a metric type"""
        metrics = self.performance_tracker.get_performance_metrics(30)
        
        metric_mapping = {
            'win_rate': metrics.get('win_rate', 0) * 100,
            'total_pnl': metrics.get('total_pnl', 0),
            'sharpe_ratio': metrics.get('sharpe_ratio', 0),
            'max_drawdown': metrics.get('max_drawdown', 0) * 100
        }
        
        return metric_mapping.get(metric_type, 0)
    
    def check_achievements(self) -> List[Dict]:
        """Check for new achievements"""
        achievements = []
        metrics = self.performance_tracker.get_performance_metrics(30)
        
        # Win rate achievements
        win_rate = metrics.get('win_rate', 0) * 100
        if win_rate >= 70:
            achievements.append({
                'id': 'high_win_rate',
                'title': 'High Win Rate Achiever',
                'description': f'Achieved {win_rate:.1f}% win rate',
                'timestamp': datetime.now(),
                'type': 'performance'
            })
        
        # Profit achievements
        total_pnl = metrics.get('total_pnl', 0)
        if total_pnl >= 1000:
            achievements.append({
                'id': 'profit_milestone',
                'title': 'Profit Milestone',
                'description': f'Generated ${total_pnl:,.2f} in profits',
                'timestamp': datetime.now(),
                'type': 'financial'
            })
        
        # Add to achievements list
        for achievement in achievements:
            if achievement not in self.achievements:
                self.achievements.append(achievement)
        
        return achievements
    
    def export_dashboard_data(self, dashboard_name: str = 'overview', 
                            format_type: str = 'json') -> str:
        """Export dashboard data"""
        try:
            data = {
                'export_info': {
                    'dashboard': dashboard_name,
                    'exported_at': datetime.now().isoformat(),
                    'format': format_type
                },
                'dashboard_data': self.get_dashboard_data(dashboard_name),
                'widget_config': {wid: asdict(widget) for wid, widget in self.dashboard_widgets.items()},
                'goals_progress': self.get_goal_progress(),
                'achievements': self.achievements
            }
            
            if format_type.lower() == 'json':
                return json.dumps(data, indent=2, default=str)
            elif format_type.lower() == 'csv':
                # Convert equity curve to CSV if available
                dashboard_data = data['dashboard_data']
                if 'equity_curve' in dashboard_data.get('widgets', {}):
                    eq_data = dashboard_data['widgets']['equity_curve']['data']
                    if eq_data:
                        df = pd.DataFrame(eq_data)
                        return df.to_csv(index=False)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Error exporting dashboard data: {e}")
            return ""


# Demo function
def demo_dashboard_data():
    """Demonstrate dashboard data management capabilities"""
    print("=== Dashboard Data Manager Demo ===\n")
    
    # Import other modules
    from performance_tracker import demo_performance_tracker
    from real_time_monitor import demo_real_time_monitor
    
    # Initialize components
    print("Initializing performance tracker...")
    performance_tracker = demo_performance_tracker()
    
    print("Initializing real-time monitor...")
    real_time_monitor = demo_real_time_monitor()
    
    # Initialize dashboard data manager
    print("Initializing dashboard data manager...")
    dashboard_manager = DashboardDataManager(performance_tracker, real_time_monitor)
    
    # Set some performance goals
    print("Setting performance goals...")
    dashboard_manager.set_performance_goal('win_rate_target', 'win_rate', 60.0, 30)
    dashboard_manager.set_performance_goal('profit_target', 'total_pnl', 500.0, 30)
    dashboard_manager.set_performance_goal('sharpe_target', 'sharpe_ratio', 1.5, 30)
    
    # Get overview dashboard
    print("\nGenerating overview dashboard...")
    overview_data = dashboard_manager.get_dashboard_data('overview')
    
    if overview_data:
        print(f"Dashboard: {overview_data['dashboard_info']['name']}")
        print(f"Description: {overview_data['dashboard_info']['description']}")
        print(f"Widgets: {len(overview_data['widgets'])}")
        
        # Show summary
        summary = overview_data.get('summary', {})
        print(f"\nSummary Statistics:")
        print(f"  Total Trades: {summary.get('total_trades', 0)}")
        print(f"  Total P&L: ${summary.get('total_pnl', 0):,.2f}")
        print(f"  Win Rate: {summary.get('win_rate', 0):.1%}")
        print(f"  Active Strategies: {summary.get('active_strategies', 0)}")
    
    # Get real-time dashboard
    print("\nGenerating real-time dashboard...")
    realtime_data = dashboard_manager.get_dashboard_data('real_time')
    
    if realtime_data:
        print(f"Real-time Widgets: {len(realtime_data['widgets'])}")
    
    # Get detailed dashboard
    print("\nGenerating detailed dashboard...")
    detailed_data = dashboard_manager.get_dashboard_data('detailed')
    
    if detailed_data:
        print(f"Detailed Widgets: {len(detailed_data['widgets'])}")
    
    # Check goal progress
    print("\nChecking goal progress...")
    goal_progress = dashboard_manager.get_goal_progress()
    
    for goal_id, progress in goal_progress.items():
        goal = progress['goal']
        print(f"Goal: {goal['type']}")
        print(f"  Target: {goal['target_value']}")
        print(f"  Current: {progress['current_value']:.2f}")
        print(f"  Progress: {progress['progress_percent']:.1f}%")
        print(f"  Days Remaining: {progress['days_remaining']}")
    
    # Check achievements
    print("\nChecking achievements...")
    achievements = dashboard_manager.check_achievements()
    
    if achievements:
        for achievement in achievements:
            print(f"Achievement: {achievement['title']}")
            print(f"  Description: {achievement['description']}")
    else:
        print("No new achievements yet.")
    
    # Export data
    print("\nExporting dashboard data...")
    export_data = dashboard_manager.export_dashboard_data('overview', 'json')
    
    if export_data:
        print("Export successful (JSON format)")
        print(f"Export data size: {len(export_data)} characters")
    
    # Show available widgets
    print(f"\nAvailable Dashboard Widgets:")
    for widget_id, widget in dashboard_manager.dashboard_widgets.items():
        print(f"  {widget_id}: {widget.title}")
    
    print(f"\nAvailable Preset Dashboards:")
    for preset_id, preset in dashboard_manager.preset_dashboards.items():
        print(f"  {preset_id}: {preset['name']}")
    
    print("\n=== Dashboard Data Manager Demo Complete ===")
    
    return dashboard_manager


if __name__ == "__main__":
    demo_dashboard_data()