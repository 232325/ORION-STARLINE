"""
Performance Tracker - Real-time performance monitoring va analytics
Comprehensive performance tracking va alerting system
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
import warnings
from collections import deque
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings('ignore')

@dataclass
class PerformanceConfig:
    """Performance tracking konfiguratsiyasi"""
    window_size: int = 1000  # Performance window size
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'min_accuracy': 0.6,
        'max_drawdown': 0.15,
        'min_sharpe': 0.5,
        'max_volatility': 0.3
    })
    reporting_frequency: int = 50  # Report every N iterations
    save_history: bool = True
    plot_generation: bool = True
    alert_callbacks: List[Callable] = field(default_factory=list)

@dataclass
class AlertEvent:
    """Alert event ma'lumotlari"""
    timestamp: datetime
    alert_type: str
    message: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    current_value: float
    threshold_value: float
    metric_name: str

@dataclass
class PerformanceSnapshot:
    """Performance snapshot ma'lumotlari"""
    timestamp: datetime
    iteration: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    sharpe_ratio: float
    total_return: float
    max_drawdown: float
    volatility: float
    win_rate: float
    avg_trade_duration: float
    profit_factor: float
    calibration_error: float

class PerformanceTracker:
    """Comprehensive performance tracking system"""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.PerformanceTracker")
        
        # Performance data storage
        self.snapshots = deque(maxlen=config.window_size)
        self.performance_history = deque(maxlen=config.window_size)
        self.alert_history = deque(maxlen=100)
        
        # Rolling metrics
        self.rolling_accuracy = deque(maxlen=100)
        self.rolling_returns = deque(maxlen=100)
        self.rolling_drawdown = deque(maxlen=100)
        
        # Benchmark comparison
        self.benchmark_returns = None
        self.benchmark_name = "Market Index"
        
        # Alert system
        self.alert_callbacks = config.alert_callbacks
        self.last_alert_time = {}
        
        # Performance state
        self.current_iteration = 0
        self.best_performance = {}
        self.worst_performance = {}
        self.performance_trends = {}
        
    def record_performance(self, 
                          predictions: np.ndarray, 
                          actual: np.ndarray, 
                          returns: Optional[np.ndarray] = None,
                          trade_metadata: Optional[Dict] = None) -> PerformanceSnapshot:
        """Performance ma'lumotlarini saqlash"""
        
        # Calculate core metrics
        accuracy = np.mean(predictions == actual)
        precision = self._calculate_precision(predictions, actual)
        recall = self._calculate_recall(predictions, actual)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Calculate trading metrics
        sharpe_ratio, total_return, max_drawdown, volatility = 0, 0, 0, 0
        win_rate, avg_trade_duration, profit_factor = 0, 0, 0
        
        if returns is not None:
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
            total_return = np.prod(1 + returns) - 1
            max_drawdown = self._calculate_max_drawdown(returns)
            volatility = np.std(returns)
            win_rate = np.mean(returns > 0)
            avg_trade_duration = trade_metadata.get('avg_duration', 0) if trade_metadata else 0
            profit_factor = self._calculate_profit_factor(returns)
        
        # Calculate calibration error
        calibration_error = self._calculate_calibration_error(predictions, actual)
        
        # Create snapshot
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            iteration=self.current_iteration,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            sharpe_ratio=sharpe_ratio,
            total_return=total_return,
            max_drawdown=max_drawdown,
            volatility=volatility,
            win_rate=win_rate,
            avg_trade_duration=avg_trade_duration,
            profit_factor=profit_factor,
            calibration_error=calibration_error
        )
        
        # Store snapshot
        self.snapshots.append(snapshot)
        self.performance_history.append({
            'accuracy': accuracy,
            'return': total_return,
            'sharpe': sharpe_ratio,
            'timestamp': datetime.now()
        })
        
        # Update rolling metrics
        self.rolling_accuracy.append(accuracy)
        if returns is not None:
            self.rolling_returns.extend(returns)
            self.rolling_drawdown.append(max_drawdown)
        
        # Check for alerts
        self._check_alerts(snapshot)
        
        # Update best/worst performance
        self._update_performance_bounds(snapshot)
        
        # Update trends
        self._update_trends(snapshot)
        
        self.current_iteration += 1
        
        return snapshot
    
    def _calculate_precision(self, predictions: np.ndarray, actual: np.ndarray) -> float:
        """Precision ni hisoblash"""
        true_positives = np.sum((predictions == 1) & (actual == 1))
        false_positives = np.sum((predictions == 1) & (actual == 0))
        return true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    
    def _calculate_recall(self, predictions: np.ndarray, actual: np.ndarray) -> float:
        """Recall ni hisoblash"""
        true_positives = np.sum((predictions == 1) & (actual == 1))
        false_negatives = np.sum((predictions == 0) & (actual == 1))
        return true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    
    def _calculate_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Sharpe ratio ni hisoblash"""
        if len(returns) == 0 or np.std(returns) == 0:
            return 0
        excess_returns = np.mean(returns) - risk_free_rate / 252  # Daily risk-free rate
        return excess_returns / np.std(returns) * np.sqrt(252)  # Annualized
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Maximum drawdown ni hisoblash"""
        if len(returns) == 0:
            return 0
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return np.min(drawdown)
    
    def _calculate_profit_factor(self, returns: np.ndarray) -> float:
        """Profit factor ni hisoblash"""
        if len(returns) == 0:
            return 0
        winning_trades = returns[returns > 0]
        losing_trades = returns[returns < 0]
        
        gross_profit = np.sum(winning_trades) if len(winning_trades) > 0 else 0
        gross_loss = np.abs(np.sum(losing_trades)) if len(losing_trades) > 0 else 1
        
        return gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    def _calculate_calibration_error(self, predictions: np.ndarray, actual: np.ndarray) -> float:
        """Prediction calibration error ni hisoblash"""
        # Simple calibration error based on confidence vs accuracy
        confidence = np.mean(predictions)  # Simplified confidence measure
        accuracy = np.mean(predictions == actual)
        return abs(confidence - accuracy)
    
    def _check_alerts(self, snapshot: PerformanceSnapshot) -> None:
        """Alert larni tekshirish"""
        current_time = datetime.now()
        
        # Check threshold violations
        for metric_name, threshold in self.config.alert_thresholds.items():
            value = getattr(snapshot, metric_name.replace('min_', '').replace('max_', ''), None)
            if value is not None:
                alert_triggered = False
                severity = 'low'
                
                if metric_name.startswith('min_') and value < threshold:
                    alert_triggered = True
                    severity = 'high' if value < threshold * 0.8 else 'medium'
                elif metric_name.startswith('max_') and value > threshold:
                    alert_triggered = True
                    severity = 'high' if value > threshold * 1.2 else 'medium'
                
                if alert_triggered:
                    # Rate limiting for alerts
                    alert_key = f"{metric_name}_{snapshot.iteration // 100}"
                    if (alert_key not in self.last_alert_time or 
                        current_time - self.last_alert_time[alert_key] > timedelta(minutes=5)):
                        
                        alert = AlertEvent(
                            timestamp=current_time,
                            alert_type='threshold_violation',
                            message=f"{metric_name} breached: {value:.4f} < {threshold}",
                            severity=severity,
                            current_value=value,
                            threshold_value=threshold,
                            metric_name=metric_name
                        )
                        
                        self._trigger_alert(alert)
                        self.last_alert_time[alert_key] = current_time
    
    def _trigger_alert(self, alert: AlertEvent) -> None:
        """Alert ni trigger qilish"""
        self.alert_history.append(alert)
        self.logger.warning(f"ALERT [{alert.severity.upper()}]: {alert.message}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    def _update_performance_bounds(self, snapshot: PerformanceSnapshot) -> None:
        """Best va worst performance larni yangilash"""
        metrics = ['accuracy', 'total_return', 'sharpe_ratio', 'f1_score']
        
        for metric in metrics:
            value = getattr(snapshot, metric, 0)
            if metric not in self.best_performance or value > self.best_performance[metric]['value']:
                self.best_performance[metric] = {
                    'value': value,
                    'iteration': snapshot.iteration,
                    'timestamp': snapshot.timestamp
                }
            
            if metric not in self.worst_performance or value < self.worst_performance[metric]['value']:
                self.worst_performance[metric] = {
                    'value': value,
                    'iteration': snapshot.iteration,
                    'timestamp': snapshot.timestamp
                }
    
    def _update_trends(self, snapshot: PerformanceSnapshot) -> None:
        """Performance trends ni yangilash"""
        if len(self.snapshots) < 10:
            return
        
        recent_snapshots = list(self.snapshots)[-10:]
        
        for metric in ['accuracy', 'total_return', 'sharpe_ratio']:
            values = [getattr(s, metric, 0) for s in recent_snapshots]
            
            # Simple trend calculation
            if len(values) >= 5:
                recent_trend = np.polyfit(range(5), values[-5:], 1)[0]
                self.performance_trends[metric] = recent_trend
    
    def add_alert_callback(self, callback: Callable[[AlertEvent], None]) -> None:
        """Alert callback qo'shish"""
        self.alert_callbacks.append(callback)
    
    def set_benchmark(self, benchmark_returns: np.ndarray, benchmark_name: str = "Market Index") -> None:
        """Benchmark ma'lumotlarini o'rnatish"""
        self.benchmark_returns = benchmark_returns
        self.benchmark_name = benchmark_name
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Comprehensive performance report"""
        if not self.snapshots:
            return {"error": "No performance data available"}
        
        latest = self.snapshots[-1]
        
        # Calculate rolling averages
        rolling_accuracy = np.mean(list(self.rolling_accuracy)[-50:]) if self.rolling_accuracy else 0
        rolling_return = np.mean(list(self.rolling_returns)[-50:]) if self.rolling_returns else 0
        
        # Calculate benchmark comparison
        benchmark_info = {}
        if self.benchmark_returns is not None:
            model_cumulative = np.prod(1 + list(self.rolling_returns)) - 1 if self.rolling_returns else 0
            benchmark_cumulative = np.prod(1 + self.benchmark_returns) - 1
            excess_return = model_cumulative - benchmark_cumulative
            benchmark_info = {
                'excess_return': excess_return,
                'outperformance': excess_return > 0
            }
        
        return {
            'current_performance': {
                'accuracy': latest.accuracy,
                'total_return': latest.total_return,
                'sharpe_ratio': latest.sharpe_ratio,
                'max_drawdown': latest.max_drawdown,
                'win_rate': latest.win_rate,
                'profit_factor': latest.profit_factor
            },
            'rolling_averages': {
                'accuracy_50': rolling_accuracy,
                'return_50': rolling_return
            },
            'best_performance': self.best_performance,
            'worst_performance': self.worst_performance,
            'trends': self.performance_trends,
            'benchmark_comparison': benchmark_info,
            'total_iterations': self.current_iteration,
            'recent_alerts': [alert.message for alert in list(self.alert_history)[-5:]]
        }
    
    def generate_performance_plots(self, save_path: Optional[str] = None) -> Dict[str, str]:
        """Performance visualization plots ni yaratish"""
        if not self.snapshots:
            return {}
        
        plots = {}
        
        # Convert snapshots to DataFrame for plotting
        df = pd.DataFrame([{
            'iteration': s.iteration,
            'accuracy': s.accuracy,
            'total_return': s.total_return,
            'sharpe_ratio': s.sharpe_ratio,
            'max_drawdown': s.max_drawdown,
            'win_rate': s.win_rate
        } for s in self.snapshots])
        
        # Performance over time plot
        plt.figure(figsize=(15, 10))
        
        plt.subplot(2, 3, 1)
        plt.plot(df['iteration'], df['accuracy'])
        plt.title('Accuracy over Time')
        plt.xlabel('Iteration')
        plt.ylabel('Accuracy')
        
        plt.subplot(2, 3, 2)
        plt.plot(df['iteration'], df['total_return'])
        plt.title('Cumulative Return over Time')
        plt.xlabel('Iteration')
        plt.ylabel('Cumulative Return')
        
        plt.subplot(2, 3, 3)
        plt.plot(df['iteration'], df['sharpe_ratio'])
        plt.title('Sharpe Ratio over Time')
        plt.xlabel('Iteration')
        plt.ylabel('Sharpe Ratio')
        
        plt.subplot(2, 3, 4)
        plt.plot(df['iteration'], df['max_drawdown'])
        plt.title('Maximum Drawdown over Time')
        plt.xlabel('Iteration')
        plt.ylabel('Max Drawdown')
        
        plt.subplot(2, 3, 5)
        plt.plot(df['iteration'], df['win_rate'])
        plt.title('Win Rate over Time')
        plt.xlabel('Iteration')
        plt.ylabel('Win Rate')
        
        plt.subplot(2, 3, 6)
        if 'volatility' in df.columns:
            plt.plot(df['iteration'], df['volatility'])
            plt.title('Volatility over Time')
            plt.xlabel('Iteration')
            plt.ylabel('Volatility')
        
        plt.tight_layout()
        
        if save_path:
            plot_path = f"{save_path}/performance_plots.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plots['overview'] = plot_path
        
        plt.close()
        
        return plots
    
    def export_performance_data(self, filepath: str) -> None:
        """Performance ma'lumotlarini eksport qilish"""
        if not self.snapshots:
            return
        
        data = []
        for snapshot in self.snapshots:
            data.append({
                'timestamp': snapshot.timestamp.isoformat(),
                'iteration': snapshot.iteration,
                'accuracy': snapshot.accuracy,
                'precision': snapshot.precision,
                'recall': snapshot.recall,
                'f1_score': snapshot.f1_score,
                'sharpe_ratio': snapshot.sharpe_ratio,
                'total_return': snapshot.total_return,
                'max_drawdown': snapshot.max_drawdown,
                'volatility': snapshot.volatility,
                'win_rate': snapshot.win_rate,
                'avg_trade_duration': snapshot.avg_trade_duration,
                'profit_factor': snapshot.profit_factor,
                'calibration_error': snapshot.calibration_error
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        self.logger.info(f"Performance data exported to {filepath}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[AlertEvent]:
        """So'nggi alert larni olish"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp > cutoff_time]
    
    def reset_tracking(self) -> None:
        """Tracking ma'lumotlarini tozalash"""
        self.snapshots.clear()
        self.performance_history.clear()
        self.alert_history.clear()
        self.rolling_accuracy.clear()
        self.rolling_returns.clear()
        self.rolling_drawdown.clear()
        self.current_iteration = 0
        self.best_performance.clear()
        self.worst_performance.clear()
        self.performance_trends.clear()
        self.last_alert_time.clear()
        
        self.logger.info("Performance tracking data reset")

class AlertHandler:
    """Alert handling system"""
    
    def __init__(self, alert_channels: List[str] = None):
        self.alert_channels = alert_channels or ['log', 'email', 'webhook']
        self.alert_handlers = {
            'log': self._log_alert,
            'email': self._email_alert,
            'webhook': self._webhook_alert
        }
        
    def _log_alert(self, alert: AlertEvent) -> None:
        """Log alert"""
        logging.warning(f"ALERT [{alert.severity}]: {alert.message}")
    
    def _email_alert(self, alert: AlertEvent) -> None:
        """Email alert - placeholder"""
        # Email sending logic would go here
        pass
    
    def _webhook_alert(self, alert: AlertEvent) -> None:
        """Webhook alert - placeholder"""
        # Webhook sending logic would go here
        pass
    
    def handle_alert(self, alert: AlertEvent) -> None:
        """Alert ni handle qilish"""
        for channel in self.alert_channels:
            if channel in self.alert_handlers:
                try:
                    self.alert_handlers[channel](alert)
                except Exception as e:
                    logging.error(f"Error handling alert on channel {channel}: {e}")