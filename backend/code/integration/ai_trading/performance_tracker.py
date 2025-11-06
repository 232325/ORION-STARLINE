"""
Performance Tracker
==================

AI model performance tracking va monitoring.
Model accuracy, precision, recall, Sharpe ratio va boshqa metrics.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import statistics
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from .model_integration import ModelPrediction, ModelType
from .signal_aggregator import TradingSignal, AggregationResult

class MetricType(Enum):
    """Performance metric turlari"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    AVERAGE_RETURN = "average_return"
    VOLATILITY = "volatility"
    CONFIDENCE_CORRELATION = "confidence_correlation"

class ModelStatus(Enum):
    """Model status"""
    TRAINING = "training"
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"
    RETIRED = "retired"

@dataclass
class PerformanceMetric:
    """Performance metric ma'lumot"""
    metric_type: MetricType
    value: float
    timestamp: float
    period: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelPerformanceReport:
    """Model performance report"""
    model_name: str
    model_type: ModelType
    report_period: str
    start_date: float
    end_date: float
    total_predictions: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    average_return: float
    volatility: float
    confidence_score: float
    timestamp: float
    recommendations: List[str] = field(default_factory=list)

@dataclass
class BacktestResult:
    """Backtest result"""
    model_name: str
    symbol: str
    strategy: str
    start_date: float
    end_date: float
    initial_capital: float
    final_capital: float
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    trades: List[Dict[str, Any]] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)

class PerformanceTracker:
    """
    Performance Tracker
    
    AI model performance-ni track qilish, monitoring va analysis.
    Comprehensive metrics, reporting va alerting.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.performance_history: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.model_predictions: Dict[str, List[ModelPrediction]] = defaultdict(list)
        self.actual_outcomes: Dict[str, List[Any]] = defaultdict(list)
        self.model_status: Dict[str, ModelStatus] = {}
        
        # Real-time tracking
        self.recent_predictions: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.performance_alerts: List[Dict[str, Any]] = []
        
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Configuration
        self.alert_threshold = self.config.get('alert_threshold', 0.1)
        self.performance_window = self.config.get('performance_window', 100)
        self.metric_calculation_interval = self.config.get('metric_interval', 300)  # 5 minutes
        
        # Risk-free rate for Sharpe ratio calculation
        self.risk_free_rate = self.config.get('risk_free_rate', 0.02)  # 2% annual
        
        # Benchmark for comparison
        self.benchmark_data: Dict[str, List[float]] = {}
    
    async def initialize(self) -> bool:
        """Performance Tracker-ni ishga tushirish"""
        try:
            self.logger.info("Performance Tracker ishga tushirilmoqda...")
            
            # Start performance monitoring
            await self._start_performance_monitoring()
            
            # Initialize benchmark data
            await self._initialize_benchmarks()
            
            self.logger.info("Performance Tracker muvaffaqiyatli ishga tushdi")
            return True
            
        except Exception as e:
            self.logger.error(f"Performance Tracker ishga tushishda xato: {e}")
            return False
    
    async def _start_performance_monitoring(self):
        """Performance monitoring ni boshlash"""
        async def monitor_performance():
            while True:
                try:
                    await self._calculate_periodic_metrics()
                    await asyncio.sleep(self.metric_calculation_interval)
                except Exception as e:
                    self.logger.error(f"Performance monitoring da xato: {e}")
                    await asyncio.sleep(60)
        
        asyncio.create_task(monitor_performance())
    
    async def _initialize_benchmarks(self):
        """Benchmark data initialization"""
        # This would typically load historical benchmark data
        # For now, create some dummy benchmark data
        symbols = ['BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD']
        
        for symbol in symbols:
            # Generate random benchmark returns
            np.random.seed(42)  # For reproducible results
            benchmark_returns = np.random.normal(0.0005, 0.02, 1000)  # Daily returns
            self.benchmark_data[symbol] = benchmark_returns.tolist()
    
    async def track_prediction(self, model_name: str, prediction: ModelPrediction,
                             actual_outcome: Any = None):
        """Prediction va outcome track qilish"""
        try:
            # Prediction save
            self.model_predictions[model_name].append(prediction)
            self.recent_predictions[model_name].append(prediction)
            
            # Actual outcome save (if available)
            if actual_outcome is not None:
                self.actual_outcomes[model_name].append(actual_outcome)
            
            # Real-time metrics update
            await self._update_real_time_metrics(model_name)
            
            self.logger.debug(f"Prediction tracked for model {model_name}")
            
        except Exception as e:
            self.logger.error(f"Prediction tracking da xato {model_name}: {e}")
    
    async def _update_real_time_metrics(self, model_name: str):
        """Real-time metrics update"""
        try:
            predictions = list(self.recent_predictions[model_name])
            if len(predictions) < 10:  # Minimum data for meaningful metrics
                return
            
            # Calculate recent accuracy
            accuracy = await self._calculate_recent_accuracy(model_name)
            
            # Calculate average confidence
            avg_confidence = statistics.mean(pred.confidence for pred in predictions)
            
            # Calculate prediction frequency
            prediction_frequency = len(predictions) / max(1, 
                (predictions[-1].timestamp - predictions[0].timestamp))
            
            # Add to performance history
            metric = PerformanceMetric(
                metric_type=MetricType.ACCURACY,
                value=accuracy,
                timestamp=time.time(),
                period="realtime",
                metadata={'model_name': model_name}
            )
            self.performance_history[model_name].append(metric)
            
            confidence_metric = PerformanceMetric(
                metric_type=MetricType.CONFIDENCE_CORRELATION,
                value=avg_confidence,
                timestamp=time.time(),
                period="realtime",
                metadata={'model_name': model_name}
            )
            self.performance_history[model_name].append(confidence_metric)
            
            # Check for alerts
            await self._check_performance_alerts(model_name)
            
        except Exception as e:
            self.logger.error(f"Real-time metrics update da xato: {e}")
    
    async def _calculate_recent_accuracy(self, model_name: str) -> float:
        """Recent accuracy calculation"""
        try:
            predictions = self.model_predictions[model_name]
            outcomes = self.actual_outcomes[model_name]
            
            if len(outcomes) == 0:
                return 0.0
            
            # Match predictions with outcomes
            min_length = min(len(predictions), len(outcomes))
            if min_length == 0:
                return 0.0
            
            recent_predictions = predictions[-min_length:]
            recent_outcomes = outcomes[-min_length:]
            
            # Calculate accuracy
            correct_predictions = 0
            total_predictions = len(recent_predictions)
            
            for pred, outcome in zip(recent_predictions, recent_outcomes):
                # Simplified accuracy calculation
                # In reality, this would depend on the specific prediction type
                if abs(pred.confidence - outcome.get('confidence', 0.5)) < 0.3:
                    correct_predictions += 1
            
            return correct_predictions / total_predictions if total_predictions > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Recent accuracy calculation da xato: {e}")
            return 0.0
    
    async def _calculate_periodic_metrics(self):
        """Periodic metrics calculation"""
        try:
            for model_name in self.model_predictions.keys():
                await self._calculate_model_metrics(model_name)
            
        except Exception as e:
            self.logger.error(f"Periodic metrics calculation da xato: {e}")
    
    async def _calculate_model_metrics(self, model_name: str):
        """Model uchun comprehensive metrics calculation"""
        try:
            predictions = self.model_predictions[model_name]
            if len(predictions) < 10:
                return
            
            # Get model type
            model_type = predictions[0].model_type
            
            # Calculate various metrics
            metrics = {}
            
            # Basic accuracy metrics
            accuracy = await self._calculate_accuracy(model_name)
            precision = await self._calculate_precision(model_name)
            recall = await self._calculate_recall(model_name)
            f1_score = await self._calculate_f1_score(precision, recall)
            
            metrics[MetricType.ACCURACY] = accuracy
            metrics[MetricType.PRECISION] = precision
            metrics[MetricType.RECALL] = recall
            metrics[MetricType.F1_SCORE] = f1_score
            
            # Trading-specific metrics
            if predictions:
                sharpe_ratio = await self._calculate_sharpe_ratio(model_name)
                max_drawdown = await self._calculate_max_drawdown(model_name)
                win_rate = await self._calculate_win_rate(model_name)
                avg_return = await self._calculate_average_return(model_name)
                volatility = await self._calculate_volatility(model_name)
                
                metrics[MetricType.SHARPE_RATIO] = sharpe_ratio
                metrics[MetricType.MAX_DRAWDOWN] = max_drawdown
                metrics[MetricType.WIN_RATE] = win_rate
                metrics[MetricType.AVERAGE_RETURN] = avg_return
                metrics[MetricType.VOLATILITY] = volatility
            
            # Store metrics
            current_time = time.time()
            for metric_type, value in metrics.items():
                metric = PerformanceMetric(
                    metric_type=metric_type,
                    value=value,
                    timestamp=current_time,
                    period="daily"
                )
                self.performance_history[model_name].append(metric)
            
            # Update model status
            await self._update_model_status(model_name, metrics)
            
        except Exception as e:
            self.logger.error(f"Model metrics calculation da xato {model_name}: {e}")
    
    async def _calculate_accuracy(self, model_name: str) -> float:
        """Accuracy calculation"""
        predictions = self.model_predictions[model_name]
        outcomes = self.actual_outcomes[model_name]
        
        if len(outcomes) == 0:
            return 0.0
        
        # Simplified accuracy for demo
        min_length = min(len(predictions), len(outcomes))
        if min_length == 0:
            return 0.0
        
        # For demo purposes, assume higher confidence predictions are more accurate
        recent_predictions = predictions[-min_length:]
        correct_predictions = sum(1 for pred in recent_predictions if pred.confidence > 0.7)
        
        return correct_predictions / min_length
    
    async def _calculate_precision(self, model_name: str) -> float:
        """Precision calculation"""
        # Simplified precision calculation
        predictions = self.model_predictions[model_name]
        
        if len(predictions) < 10:
            return 0.0
        
        # High confidence positive predictions
        high_confidence_positives = sum(
            1 for pred in predictions 
            if pred.confidence > 0.8 and pred.prediction.get('signal_type', 0) != 0
        )
        
        total_positives = sum(
            1 for pred in predictions 
            if pred.prediction.get('signal_type', 0) != 0
        )
        
        return high_confidence_positives / max(1, total_positives)
    
    async def _calculate_recall(self, model_name: str) -> float:
        """Recall calculation"""
        # Simplified recall calculation
        predictions = self.model_predictions[model_name]
        
        if len(predictions) < 10:
            return 0.0
        
        # High confidence correct positives out of all actual positives
        # This is simplified - in reality you'd need actual positive cases
        correct_high_confidence = sum(
            1 for pred in predictions 
            if pred.confidence > 0.8
        )
        
        total_actual_positives = len(predictions) // 2  # Simplified assumption
        
        return correct_high_confidence / max(1, total_actual_positives)
    
    async def _calculate_f1_score(self, precision: float, recall: float) -> float:
        """F1 Score calculation"""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    async def _calculate_sharpe_ratio(self, model_name: str) -> float:
        """Sharpe ratio calculation"""
        try:
            predictions = self.model_predictions[model_name]
            if len(predictions) < 20:
                return 0.0
            
            # Calculate returns from predictions
            returns = []
            for i in range(1, len(predictions)):
                # Simplified return calculation
                prev_conf = predictions[i-1].confidence
                curr_conf = predictions[i].confidence
                return_val = (curr_conf - prev_conf) / max(prev_conf, 0.1)
                returns.append(return_val)
            
            if not returns:
                return 0.0
            
            mean_return = statistics.mean(returns)
            std_return = statistics.stdev(returns) if len(returns) > 1 else 0.0
            
            if std_return == 0:
                return 0.0
            
            # Annualized Sharpe ratio
            daily_sharpe = (mean_return - self.risk_free_rate/252) / std_return
            return daily_sharpe * np.sqrt(252)  # Annualized
            
        except Exception as e:
            self.logger.error(f"Sharpe ratio calculation da xato: {e}")
            return 0.0
    
    async def _calculate_max_drawdown(self, model_name: str) -> float:
        """Maximum drawdown calculation"""
        try:
            predictions = self.model_predictions[model_name]
            if len(predictions) < 10:
                return 0.0
            
            # Create equity curve from predictions
            equity = [1.0]  # Start with 1.0
            
            for pred in predictions[1:]:
                # Simplified equity calculation
                signal_change = pred.confidence - 0.5  # Centered around 0.5
                return_val = signal_change * 0.02  # 2% max change per prediction
                new_equity = equity[-1] * (1 + return_val)
                equity.append(max(0.1, new_equity))  # Prevent negative equity
            
            # Calculate drawdown
            peak = equity[0]
            max_drawdown = 0.0
            
            for value in equity:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
            
            return max_drawdown
            
        except Exception as e:
            self.logger.error(f"Max drawdown calculation da xato: {e}")
            return 0.0
    
    async def _calculate_win_rate(self, model_name: str) -> float:
        """Win rate calculation"""
        predictions = self.model_predictions[model_name]
        if len(predictions) < 10:
            return 0.0
        
        # Simplified win rate based on confidence
        # Higher confidence predictions are considered wins
        wins = sum(1 for pred in predictions if pred.confidence > 0.7)
        return wins / len(predictions)
    
    async def _calculate_average_return(self, model_name: str) -> float:
        """Average return calculation"""
        try:
            predictions = self.model_predictions[model_name]
            if len(predictions) < 10:
                return 0.0
            
            returns = []
            for i in range(1, len(predictions)):
                prev_conf = predictions[i-1].confidence
                curr_conf = predictions[i].confidence
                return_val = (curr_conf - prev_conf) / max(prev_conf, 0.1)
                returns.append(return_val)
            
            return statistics.mean(returns) if returns else 0.0
            
        except Exception as e:
            self.logger.error(f"Average return calculation da xato: {e}")
            return 0.0
    
    async def _calculate_volatility(self, model_name: str) -> float:
        """Volatility calculation"""
        try:
            predictions = self.model_predictions[model_name]
            if len(predictions) < 10:
                return 0.0
            
            returns = []
            for i in range(1, len(predictions)):
                prev_conf = predictions[i-1].confidence
                curr_conf = predictions[i].confidence
                return_val = (curr_conf - prev_conf) / max(prev_conf, 0.1)
                returns.append(return_val)
            
            return statistics.stdev(returns) if len(returns) > 1 else 0.0
            
        except Exception as e:
            self.logger.error(f"Volatility calculation da xato: {e}")
            return 0.0
    
    async def _update_model_status(self, model_name: str, metrics: Dict[MetricType, float]):
        """Model status update"""
        try:
            current_status = self.model_status.get(model_name, ModelStatus.ACTIVE)
            
            # Determine if status should change
            accuracy = metrics.get(MetricType.ACCURACY, 0.0)
            sharpe_ratio = metrics.get(MetricType.SHARPE_RATIO, 0.0)
            win_rate = metrics.get(MetricType.WIN_RATE, 0.0)
            
            new_status = current_status
            
            # Status change logic
            if accuracy < 0.4 or sharpe_ratio < -1.0:
                new_status = ModelStatus.FAILED
            elif accuracy < 0.6 or win_rate < 0.4:
                new_status = ModelStatus.DEGRADED
            elif accuracy > 0.7 and sharpe_ratio > 1.0:
                new_status = ModelStatus.ACTIVE
            # else keep current status
            
            if new_status != current_status:
                self.model_status[model_name] = new_status
                self.logger.info(f"Model {model_name} status changed to {new_status.value}")
                
                # Create alert
                alert = {
                    'model_name': model_name,
                    'old_status': current_status.value,
                    'new_status': new_status.value,
                    'timestamp': time.time(),
                    'metrics': {metric_type.value: value for metric_type, value in metrics.items()}
                }
                self.performance_alerts.append(alert)
            
        except Exception as e:
            self.logger.error(f"Model status update da xato: {e}")
    
    async def _check_performance_alerts(self, model_name: str):
        """Performance alerts checking"""
        try:
            recent_metrics = self.performance_history[model_name][-10:]
            if not recent_metrics:
                return
            
            accuracy_metric = next(
                (m for m in recent_metrics if m.metric_type == MetricType.ACCURACY), 
                None
            )
            
            if accuracy_metric and accuracy_metric.value < self.alert_threshold:
                alert = {
                    'model_name': model_name,
                    'alert_type': 'low_accuracy',
                    'value': accuracy_metric.value,
                    'threshold': self.alert_threshold,
                    'timestamp': time.time()
                }
                self.performance_alerts.append(alert)
                self.logger.warning(f"Low accuracy alert for model {model_name}: {accuracy_metric.value:.3f}")
            
        except Exception as e:
            self.logger.error(f"Performance alert checking da xato: {e}")
    
    def get_model_performance(self, model_name: str, 
                            metric_types: List[MetricType] = None,
                            period: str = "daily") -> Dict[str, Any]:
        """Model performance olish"""
        try:
            if model_name not in self.performance_history:
                return {}
            
            if metric_types is None:
                metric_types = list(MetricType)
            
            # Filter metrics by period
            relevant_metrics = [
                metric for metric in self.performance_history[model_name]
                if metric.period == period and metric.metric_type in metric_types
            ]
            
            # Group by metric type
            performance_data = defaultdict(list)
            for metric in relevant_metrics:
                performance_data[metric.metric_type.value].append({
                    'value': metric.value,
                    'timestamp': metric.timestamp
                })
            
            # Calculate current values (most recent)
            current_values = {}
            for metric_type, data in performance_data.items():
                if data:
                    # Get most recent value
                    sorted_data = sorted(data, key=lambda x: x['timestamp'])
                    current_values[metric_type] = sorted_data[-1]['value']
            
            # Status information
            status_info = {
                'status': self.model_status.get(model_name, ModelStatus.ACTIVE).value,
                'total_predictions': len(self.model_predictions.get(model_name, [])),
                'last_prediction': self.model_predictions[model_name][-1].timestamp if self.model_predictions.get(model_name) else None
            }
            
            return {
                'model_name': model_name,
                'current_metrics': current_values,
                'historical_data': dict(performance_data),
                'status': status_info
            }
            
        except Exception as e:
            self.logger.error(f"Model performance olishda xato: {e}")
            return {}
    
    def get_all_models_performance(self, 
                                 metric_types: List[MetricType] = None) -> Dict[str, Dict[str, Any]]:
        """Barcha modellar performance"""
        return {
            model_name: self.get_model_performance(model_name, metric_types)
            for model_name in self.model_predictions.keys()
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Performance summary"""
        try:
            total_models = len(self.model_predictions)
            active_models = sum(1 for status in self.model_status.values() 
                              if status == ModelStatus.ACTIVE)
            degraded_models = sum(1 for status in self.model_status.values() 
                                if status == ModelStatus.DEGRADED)
            failed_models = sum(1 for status in self.model_status.values() 
                              if status == ModelStatus.FAILED)
            
            total_predictions = sum(len(preds) for preds in self.model_predictions.values())
            
            # Recent alerts
            recent_alerts = [
                alert for alert in self.performance_alerts
                if time.time() - alert.get('timestamp', 0) < 3600  # Last hour
            ]
            
            # Best performing model
            best_model = None
            best_accuracy = 0.0
            
            for model_name in self.model_predictions.keys():
                model_perf = self.get_model_performance(model_name)
                accuracy = model_perf.get('current_metrics', {}).get('accuracy', 0.0)
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_model = model_name
            
            return {
                'total_models': total_models,
                'active_models': active_models,
                'degraded_models': degraded_models,
                'failed_models': failed_models,
                'total_predictions': total_predictions,
                'recent_alerts_count': len(recent_alerts),
                'best_model': best_model,
                'best_accuracy': best_accuracy,
                'system_health': 'healthy' if failed_models == 0 else 'degraded'
            }
            
        except Exception as e:
            self.logger.error(f"Performance summary da xato: {e}")
            return {}
    
    def get_performance_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Performance alerts olish"""
        cutoff_time = time.time() - (hours * 3600)
        return [
            alert for alert in self.performance_alerts
            if alert.get('timestamp', 0) > cutoff_time
        ]
    
    async def run_backtest(self, model_name: str, symbol: str, 
                          start_date: float, end_date: float,
                          initial_capital: float = 10000) -> Optional[BacktestResult]:
        """Model backtest run"""
        try:
            self.logger.info(f"Backtest starting for {model_name} on {symbol}")
            
            # Get model predictions in the date range
            predictions = self.model_predictions.get(model_name, [])
            relevant_predictions = [
                pred for pred in predictions
                if start_date <= pred.timestamp <= end_date
            ]
            
            if not relevant_predictions:
                self.logger.warning(f"No predictions found for backtest period")
                return None
            
            # Simulate trading
            capital = initial_capital
            equity_curve = [capital]
            trades = []
            
            position = 0  # 0: no position, 1: long, -1: short
            entry_price = 0
            
            for i, prediction in enumerate(relevant_predictions):
                signal_type = prediction.prediction.get('signal_type', 0)
                confidence = prediction.confidence
                price = 100  # Simplified price
                
                # Trading logic
                if signal_type == 1 and position != 1:  # Buy signal
                    if position == -1:  # Close short position
                        pnl = (entry_price - price) * 1000  # Simplified
                        capital += pnl
                        trades.append({
                            'type': 'close_short',
                            'price': price,
                            'pnl': pnl,
                            'timestamp': prediction.timestamp
                        })
                    
                    # Open long position
                    position = 1
                    entry_price = price
                    trades.append({
                        'type': 'open_long',
                        'price': price,
                        'confidence': confidence,
                        'timestamp': prediction.timestamp
                    })
                
                elif signal_type == -1 and position != -1:  # Sell signal
                    if position == 1:  # Close long position
                        pnl = (price - entry_price) * 1000  # Simplified
                        capital += pnl
                        trades.append({
                            'type': 'close_long',
                            'price': price,
                            'pnl': pnl,
                            'timestamp': prediction.timestamp
                        })
                    
                    # Open short position
                    position = -1
                    entry_price = price
                    trades.append({
                        'type': 'open_short',
                        'price': price,
                        'confidence': confidence,
                            'timestamp': prediction.timestamp
                    })
                
                # Update equity curve
                if position != 0:
                    unrealized_pnl = (price - entry_price) * position * 1000
                    equity_curve.append(capital + unrealized_pnl)
                else:
                    equity_curve.append(capital)
            
            # Close any remaining position
            if position != 0:
                final_price = 105  # Simplified final price
                if position == 1:
                    pnl = (final_price - entry_price) * 1000
                else:
                    pnl = (entry_price - final_price) * 1000
                capital += pnl
                trades.append({
                    'type': f'close_{"long" if position == 1 else "short"}',
                    'price': final_price,
                    'pnl': pnl,
                    'timestamp': relevant_predictions[-1].timestamp
                })
                equity_curve[-1] = capital
            
            # Calculate metrics
            total_return = (capital - initial_capital) / initial_capital
            winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
            winning_trade_count = len(winning_trades)
            losing_trade_count = len(trades) - winning_trade_count
            
            win_rate = winning_trade_count / max(1, len(trades))
            
            # Simplified Sharpe ratio
            returns = np.diff(equity_curve) / equity_curve[:-1]
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0
            
            # Max drawdown
            peak = equity_curve[0]
            max_drawdown = 0
            for value in equity_curve:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
            
            # Profit factor
            gross_profit = sum(t['pnl'] for t in winning_trades)
            gross_loss = abs(sum(t['pnl'] for t in trades if t.get('pnl', 0) < 0))
            profit_factor = gross_profit / max(1, gross_loss)
            
            result = BacktestResult(
                model_name=model_name,
                symbol=symbol,
                strategy="AI_Prediction",
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                final_capital=capital,
                total_return=total_return,
                annualized_return=total_return * (252 / max(1, len(relevant_predictions))),  # Simplified
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                total_trades=len(trades),
                winning_trades=winning_trade_count,
                losing_trades=losing_trade_count,
                trades=trades,
                equity_curve=equity_curve
            )
            
            self.logger.info(f"Backtest completed for {model_name}: {total_return:.2%} return")
            return result
            
        except Exception as e:
            self.logger.error(f"Backtest da xato {model_name}: {e}")
            return None