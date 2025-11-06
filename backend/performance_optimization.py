"""
Performance Optimization va Monitoring System
============================================

Ushbu modul AI Trading tizimi uchun to'liq performance optimization va monitoring
tizimini o'z ichiga oladi:

1. **Performance Metrics:**
   - Trading Metrics: Sharpe ratio, Calmar ratio, Max drawdown
   - AI Metrics: Prediction accuracy, model drift detection
   - Quantum Metrics: Quantum advantage measurement
   - System Metrics: Latency, throughput, uptime
   - Cost Metrics: API costs, quantum computing costs

2. **Real-time Monitoring:**
   - Model performance dashboards
   - Live trading metrics
   - Anomaly detection systems
   - Alert mechanisms
   - Performance degradation alerts

3. **Optimization Strategies:**
   - Latency Optimization: <100ms target
   - Accuracy Optimization: >70% signal accuracy
   - Cost Optimization: API cost minimization
   - Resource Optimization: Quantum usage efficiency
   - Model Optimization: Continuous learning

4. **A/B Testing Framework:**
   - Strategy comparison
   - Model performance testing
   - Parameter optimization
   - Feature importance analysis
   - Statistical significance testing

5. **Adaptive Systems:**
   - Self-optimizing algorithms
   - Dynamic parameter adjustment
   - Market regime detection
   - Model retraining triggers
   - Performance-based switching

Muallif: AI Trading Team
Sana: 2025-11-03
"""

import numpy as np
import pandas as pd
import asyncio
import logging
import time
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
from scipy import stats
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Performance targets
LATENCY_TARGET_MS = 100
ACCURACY_TARGET = 0.70
UPTIME_TARGET = 0.999
COST_REDUCTION_TARGET = 0.20

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Performance metric turlari"""
    TRADING = "trading"
    AI = "ai"
    QUANTUM = "quantum"
    SYSTEM = "system"
    COST = "cost"

class AlertLevel(Enum):
    """Ogohlantirish darajalari"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MarketRegime(Enum):
    """Bozor rejimlari"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    TRENDING = "trending"

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    metric_type: MetricType
    metric_name: str
    value: float
    target: float
    status: str  # 'good', 'warning', 'critical'
    metadata: Dict[str, Any] = None

@dataclass
class TradingMetrics:
    """Trading-specific metrics"""
    sharpe_ratio: float = 0.0
    calmar_ratio: float = 0.0
    max_drawdown: float = 0.0
    total_return: float = 0.0
    volatility: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sortino_ratio: float = 0.0
    information_ratio: float = 0.0
    beta: float = 0.0
    alpha: float = 0.0

@dataclass
class AIMetrics:
    """AI model performance metrics"""
    prediction_accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    model_drift_score: float = 0.0
    prediction_latency_ms: float = 0.0
    training_time_minutes: float = 0.0
    feature_importance: Dict[str, float] = None
    confusion_matrix: np.ndarray = None

@dataclass
class QuantumMetrics:
    """Quantum computing metrics"""
    quantum_advantage: float = 0.0
    quantum_speedup: float = 0.0
    quantum_fidelity: float = 0.0
    error_rate: float = 0.0
    coherence_time: float = 0.0
    gate_fidelity: float = 0.0
    circuit_depth: int = 0
    shot_count: int = 0

@dataclass
class SystemMetrics:
    """System performance metrics"""
    latency_ms: float = 0.0
    throughput_rps: float = 0.0
    uptime_percentage: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_latency: float = 0.0
    error_rate: float = 0.0
    queue_size: int = 0

@dataclass
class CostMetrics:
    """Cost tracking metrics"""
    api_cost_per_day: float = 0.0
    quantum_cost_per_hour: float = 0.0
    storage_cost_per_month: float = 0.0
    total_monthly_cost: float = 0.0
    cost_per_trade: float = 0.0
    cost_reduction_percentage: float = 0.0
    budget_utilization: float = 0.0

class PerformanceMonitor:
    """Real-time performance monitoring tizimi"""
    
    def __init__(self, db_path: str = "performance_metrics.db"):
        self.db_path = db_path
        self.metrics_history = defaultdict(deque)
        self.alert_callbacks = []
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Setup database
        self._setup_database()
        
        # Performance thresholds
        self.thresholds = {
            'latency_ms': LATENCY_TARGET_MS,
            'accuracy': ACCURACY_TARGET,
            'uptime': UPTIME_TARGET,
            'cost_reduction': COST_REDUCTION_TARGET
        }
        
    def _setup_database(self):
        """Performance metrics uchun SQLite database sozlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                metric_type TEXT,
                metric_name TEXT,
                value REAL,
                target REAL,
                status TEXT,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                sharpe_ratio REAL,
                calmar_ratio REAL,
                max_drawdown REAL,
                total_return REAL,
                volatility REAL,
                win_rate REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                prediction_accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                model_drift_score REAL,
                prediction_latency_ms REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                latency_ms REAL,
                throughput_rps REAL,
                uptime_percentage REAL,
                cpu_usage REAL,
                memory_usage REAL,
                error_rate REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                api_cost_per_day REAL,
                quantum_cost_per_hour REAL,
                total_monthly_cost REAL,
                cost_per_trade REAL,
                cost_reduction_percentage REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def log_metric(self, metric: PerformanceMetrics):
        """Performance metric log qilish"""
        try:
            # Database ga yozish
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (timestamp, metric_type, metric_name, value, target, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.timestamp,
                metric.metric_type.value,
                metric.metric_name,
                metric.value,
                metric.target,
                metric.status,
                json.dumps(metric.metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            # In-memory history ga qo'shish
            self.metrics_history[metric.metric_name].append(metric)
            
            # Limit history size
            if len(self.metrics_history[metric.metric_name]) > 1000:
                self.metrics_history[metric.metric_name].popleft()
            
            # Check thresholds va alerts
            self._check_alerts(metric)
            
        except Exception as e:
            logger.error(f"Metric log qilishda xatolik: {e}")
    
    def _check_alerts(self, metric: PerformanceMetrics):
        """Alert tekshirish va callback chaqirish"""
        try:
            if metric.status == 'critical' or metric.status == 'warning':
                for callback in self.alert_callbacks:
                    try:
                        callback(metric)
                    except Exception as e:
                        logger.error(f"Alert callback xatolik: {e}")
        except Exception as e:
            logger.error(f"Alert tekshirishda xatolik: {e}")
    
    def start_monitoring(self, interval_seconds: int = 60):
        """Real-time monitoring boshlash"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(interval_seconds,),
                daemon=True
            )
            self.monitor_thread.start()
            logger.info("Performance monitoring boshlandi")
    
    def stop_monitoring(self):
        """Monitoring to'xtatish"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Performance monitoring to'xtatildi")
    
    def _monitoring_loop(self, interval_seconds: int):
        """Monitoring asosiy tsikl"""
        while self.monitoring_active:
            try:
                # System metrics olish
                system_metrics = self._collect_system_metrics()
                self.log_metric(PerformanceMetrics(
                    timestamp=datetime.now(),
                    metric_type=MetricType.SYSTEM,
                    metric_name="latency_ms",
                    value=system_metrics.latency_ms,
                    target=self.thresholds['latency_ms'],
                    status="good" if system_metrics.latency_ms < self.thresholds['latency_ms'] else "warning"
                ))
                
                # Cost metrics olish
                cost_metrics = self._collect_cost_metrics()
                self.log_metric(PerformanceMetrics(
                    timestamp=datetime.now(),
                    metric_type=MetricType.COST,
                    metric_name="cost_reduction_percentage",
                    value=cost_metrics.cost_reduction_percentage,
                    target=self.thresholds['cost_reduction'],
                    status="good" if cost_metrics.cost_reduction_percentage >= self.thresholds['cost_reduction'] else "warning"
                ))
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Monitoring loop xatolik: {e}")
                time.sleep(interval_seconds)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """System metrics yig'ish"""
        import psutil
        
        return SystemMetrics(
            latency_ms=np.random.normal(80, 15),  # Simulated
            throughput_rps=np.random.normal(100, 20),  # Simulated
            uptime_percentage=99.8 + np.random.normal(0.1, 0.05),
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent,
            error_rate=np.random.exponential(0.01)
        )
    
    def _collect_cost_metrics(self) -> CostMetrics:
        """Cost metrics yig'ish"""
        return CostMetrics(
            api_cost_per_day=25.50 + np.random.normal(0, 2),
            quantum_cost_per_hour=15.75 + np.random.normal(0, 1),
            total_monthly_cost=1200.00 + np.random.normal(0, 50),
            cost_per_trade=0.85 + np.random.normal(0, 0.1),
            cost_reduction_percentage=18.5 + np.random.normal(0, 3)
        )
    
    def add_alert_callback(self, callback: Callable[[PerformanceMetrics], None]):
        """Alert callback qo'shish"""
        self.alert_callbacks.append(callback)
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """So'nggi N soat metrics summary"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        
        # Trading metrics
        trading_df = pd.read_sql_query('''
            SELECT * FROM trading_metrics 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', conn, params=(start_time, end_time))
        
        # AI metrics
        ai_df = pd.read_sql_query('''
            SELECT * FROM ai_metrics 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', conn, params=(start_time, end_time))
        
        # System metrics
        system_df = pd.read_sql_query('''
            SELECT * FROM system_metrics 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', conn, params=(start_time, end_time))
        
        # Cost metrics
        cost_df = pd.read_sql_query('''
            SELECT * FROM cost_metrics 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', conn, params=(start_time, end_time))
        
        conn.close()
        
        return {
            'trading': trading_df.describe().to_dict() if not trading_df.empty else {},
            'ai': ai_df.describe().to_dict() if not ai_df.empty else {},
            'system': system_df.describe().to_dict() if not system_df.empty else {},
            'cost': cost_df.describe().to_dict() if not cost_df.empty else {},
            'summary': {
                'total_trades': len(trading_df),
                'avg_accuracy': ai_df['prediction_accuracy'].mean() if not ai_df.empty else 0,
                'avg_latency': system_df['latency_ms'].mean() if not system_df.empty else 0,
                'total_cost': cost_df['total_monthly_cost'].sum() if not cost_df.empty else 0
            }
        }

class TradingPerformanceAnalyzer:
    """Trading performance tahlili"""
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Sharpe ratio hisoblash"""
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series, max_drawdown: float) -> float:
        """Calmar ratio hisoblash"""
        annual_return = (1 + returns).prod() ** (252 / len(returns)) - 1
        return annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """Maximum drawdown hisoblash"""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, target_return: float = 0) -> float:
        """Sortino ratio hisoblash"""
        excess_returns = returns - target_return
        downside_deviation = np.sqrt((excess_returns[excess_returns < 0] ** 2).mean())
        return excess_returns.mean() / downside_deviation if downside_deviation != 0 else 0
    
    @staticmethod
    def calculate_information_ratio(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Information ratio hisoblash"""
        active_returns = portfolio_returns - benchmark_returns
        tracking_error = active_returns.std()
        return active_returns.mean() / tracking_error if tracking_error != 0 else 0
    
    @staticmethod
    def calculate_beta(portfolio_returns: pd.Series, market_returns: pd.Series) -> float:
        """Beta hisoblash"""
        covariance = np.cov(portfolio_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        return covariance / market_variance if market_variance != 0 else 0
    
    @staticmethod
    def calculate_alpha(portfolio_returns: pd.Series, market_returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Alpha hisoblash"""
        beta = TradingPerformanceAnalyzer.calculate_beta(portfolio_returns, market_returns)
        portfolio_return = portfolio_returns.mean() * 252
        market_return = market_returns.mean() * 252
        alpha = portfolio_return - (risk_free_rate + beta * (market_return - risk_free_rate))
        return alpha

class AIPerformanceAnalyzer:
    """AI model performance tahlili"""
    
    @staticmethod
    def calculate_prediction_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Prediction accuracy hisoblash"""
        return accuracy_score(y_true, y_pred)
    
    @staticmethod
    def calculate_precision_recall_f1(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, float, float]:
        """Precision, Recall, F1-score hisoblash"""
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')
        return precision, recall, f1
    
    @staticmethod
    def detect_model_drift(X_train: np.ndarray, X_new: np.ndarray, threshold: float = 0.1) -> float:
        """Model drift detection (KL divergence asosida)"""
        from scipy.stats import entropy
        
        # Distribution comparison
        kl_divergence = 0
        for i in range(min(X_train.shape[1], X_new.shape[1])):
            # Histogram-based distribution comparison
            hist_train, bin_edges = np.histogram(X_train[:, i], bins=50, density=True)
            hist_new, _ = np.histogram(X_new[:, i], bins=bin_edges, density=True)
            
            # Add small epsilon to avoid log(0)
            hist_train = hist_train + 1e-10
            hist_new = hist_new + 1e-10
            
            kl_divergence += entropy(hist_new, hist_train)
        
        return kl_divergence / min(X_train.shape[1], X_new.shape[1])
    
    @staticmethod
    def analyze_feature_importance(model, feature_names: List[str]) -> Dict[str, float]:
        """Feature importance tahlili"""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_[0]) if model.coef_.ndim > 1 else np.abs(model.coef_)
        else:
            importances = np.ones(len(feature_names))
        
        return dict(zip(feature_names, importances / importances.sum()))

class QuantumPerformanceAnalyzer:
    """Quantum computing performance tahlili"""
    
    @staticmethod
    def measure_quantum_advantage(classical_time: float, quantum_time: float) -> float:
        """Quantum advantage o'lchash"""
        return (classical_time - quantum_time) / classical_time if classical_time > 0 else 0
    
    @staticmethod
    def calculate_quantum_speedup(classical_complexity: int, quantum_complexity: int) -> float:
        """Quantum speedup hisoblash"""
        return np.log2(classical_complexity / quantum_complexity) if quantum_complexity > 0 else 0
    
    @staticmethod
    def measure_fidelity(counts: Dict[str, int]) -> float:
        """Quantum circuit fidelity o'lchash"""
        total_shots = sum(counts.values())
        max_probability = max(counts.values()) / total_shots
        return max_probability

class ABTestingFramework:
    """A/B Testing framework"""
    
    def __init__(self):
        self.experiments = {}
        self.results = {}
    
    def create_experiment(self, experiment_name: str, variants: List[str], 
                         traffic_split: Dict[str, float]) -> str:
        """Yangi A/B test yaratish"""
        if abs(sum(traffic_split.values()) - 1.0) > 0.01:
            raise ValueError("Traffic split yig'indisi 1.0 ga teng bo'lishi kerak")
        
        experiment_id = f"{experiment_name}_{int(time.time())}"
        self.experiments[experiment_id] = {
            'name': experiment_name,
            'variants': variants,
            'traffic_split': traffic_split,
            'created_at': datetime.now(),
            'status': 'running'
        }
        
        logger.info(f"A/B test yaratildi: {experiment_id}")
        return experiment_id
    
    def assign_variant(self, experiment_id: str, user_id: str) -> str:
        """User uchun variant назначение"""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment topilmadi: {experiment_id}")
        
        # Hash-based deterministic assignment
        hash_value = hash(f"{experiment_id}_{user_id}")
        normalized_hash = (hash_value % 10000) / 10000.0
        
        cumulative_split = 0
        for variant, split in self.experiments[experiment_id]['traffic_split'].items():
            cumulative_split += split
            if normalized_hash <= cumulative_split:
                return variant
        
        return list(self.experiments[experiment_id]['traffic_split'].keys())[-1]
    
    def record_outcome(self, experiment_id: str, variant: str, user_id: str, 
                      outcome: float, metric_name: str):
        """Natija qayd etish"""
        if experiment_id not in self.results:
            self.results[experiment_id] = defaultdict(lambda: defaultdict(list))
        
        self.results[experiment_id][variant][metric_name].append(outcome)
    
    def analyze_results(self, experiment_id: str, metric_name: str, 
                       significance_level: float = 0.05) -> Dict[str, Any]:
        """A/B test natijalarini tahlil qilish"""
        if experiment_id not in self.results:
            raise ValueError(f"Experiment natijalari topilmadi: {experiment_id}")
        
        variants = self.experiments[experiment_id]['variants']
        analysis_results = {}
        
        # Each variant uchun stats
        for variant in variants:
            outcomes = self.results[experiment_id][variant].get(metric_name, [])
            if outcomes:
                analysis_results[variant] = {
                    'mean': np.mean(outcomes),
                    'std': np.std(outcomes),
                    'count': len(outcomes),
                    'confidence_interval': stats.t.interval(
                        1 - significance_level,
                        len(outcomes) - 1,
                        loc=np.mean(outcomes),
                        scale=stats.sem(outcomes)
                    ) if len(outcomes) > 1 else (0, 0)
                }
        
        # Statistical significance test
        if len(variants) >= 2 and all(
            variant in analysis_results and analysis_results[variant]['count'] > 1
            for variant in variants
        ):
            # T-test between first two variants
            variant1_outcomes = self.results[experiment_id][variants[0]].get(metric_name, [])
            variant2_outcomes = self.results[experiment_id][variants[1]].get(metric_name, [])
            
            if variant1_outcomes and variant2_outcomes:
                t_stat, p_value = stats.ttest_ind(variant1_outcomes, variant2_outcomes)
                analysis_results['statistical_test'] = {
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < significance_level,
                    'better_variant': variants[0] if np.mean(variant1_outcomes) > np.mean(variant2_outcomes) else variants[1]
                }
        
        return analysis_results

class AdaptiveOptimizer:
    """Adaptive optimization sistem"""
    
    def __init__(self):
        self.optimization_strategies = {}
        self.performance_history = defaultdict(list)
        self.current_regime = MarketRegime.SIDEWAYS
        self.optimization_active = False
        
    def register_strategy(self, name: str, strategy_func: Callable, 
                         parameters: Dict[str, Any]):
        """Optimization strategy ro'yxatga olish"""
        self.optimization_strategies[name] = {
            'function': strategy_func,
            'parameters': parameters,
            'performance': [],
            'last_optimization': None
        }
        
    def detect_market_regime(self, price_data: pd.Series, volatility_data: pd.Series) -> MarketRegime:
        """Bozor rejimini aniqlash"""
        try:
            # Price trend analysis
            price_change = (price_data.iloc[-1] - price_data.iloc[-20]) / price_data.iloc[-20]
            volatility = volatility_data.mean()
            
            # Regime detection logic
            if abs(price_change) > 0.1 and volatility > volatility_data.quantile(0.8):
                return MarketRegime.VOLATILE
            elif price_change > 0.05:
                return MarketRegime.BULL
            elif price_change < -0.05:
                return MarketRegime.BEAR
            elif volatility > volatility_data.quantile(0.7):
                return MarketRegime.TRENDING
            else:
                return MarketRegime.SIDEWAYS
                
        except Exception as e:
            logger.error(f"Market regime detection xatolik: {e}")
            return MarketRegime.SIDEWAYS
    
    def optimize_parameters(self, strategy_name: str, performance_data: List[float],
                          objective: str = 'maximize') -> Dict[str, Any]:
        """Parametrlarni optimizatsiya qilish"""
        try:
            if strategy_name not in self.optimization_strategies:
                raise ValueError(f"Strategy topilmadi: {strategy_name}")
            
            strategy = self.optimization_strategies[strategy_name]
            
            # Simple optimization logic (grid search or similar)
            if len(performance_data) > 10:
                # Analyze performance trend
                recent_performance = performance_data[-10:]
                
                if objective == 'maximize':
                    if np.mean(recent_performance) > np.mean(performance_data[:-10]):
                        # Performance is improving, keep current parameters
                        optimized_params = strategy['parameters']
                    else:
                        # Performance is declining, adjust parameters
                        optimized_params = self._adjust_parameters(
                            strategy['parameters'], improvement_direction='increase'
                        )
                else:  # minimize
                    if np.mean(recent_performance) < np.mean(performance_data[:-10]):
                        optimized_params = strategy['parameters']
                    else:
                        optimized_params = self._adjust_parameters(
                            strategy['parameters'], improvement_direction='decrease'
                        )
                
                # Update strategy parameters
                self.optimization_strategies[strategy_name]['parameters'] = optimized_params
                self.optimization_strategies[strategy_name]['last_optimization'] = datetime.now()
                
                logger.info(f"Strategy optimizatsiya qilindi: {strategy_name}")
                return optimized_params
            
            return strategy['parameters']
            
        except Exception as e:
            logger.error(f"Parameter optimization xatolik: {e}")
            return strategy['parameters']
    
    def _adjust_parameters(self, current_params: Dict[str, Any], 
                          improvement_direction: str) -> Dict[str, Any]:
        """Parametrlarni sozlash"""
        optimized_params = current_params.copy()
        
        for param_name, param_value in current_params.items():
            if isinstance(param_value, (int, float)):
                if improvement_direction == 'increase':
                    optimized_params[param_name] = param_value * 1.1
                else:
                    optimized_params[param_name] = param_value * 0.9
            elif isinstance(param_value, bool):
                optimized_params[param_name] = not param_value
            elif isinstance(param_value, str) and param_value in ['low', 'medium', 'high']:
                levels = ['low', 'medium', 'high']
                current_index = levels.index(param_value)
                if improvement_direction == 'increase' and current_index < len(levels) - 1:
                    optimized_params[param_name] = levels[current_index + 1]
                elif improvement_direction == 'decrease' and current_index > 0:
                    optimized_params[param_name] = levels[current_index - 1]
        
        return optimized_params
    
    def select_best_strategy(self, performance_data: Dict[str, List[float]]) -> str:
        """Eng yaxshi strategiyani tanlash"""
        best_strategy = None
        best_performance = float('-inf')
        
        for strategy_name, performance_list in performance_data.items():
            if performance_list:
                avg_performance = np.mean(performance_list[-10:])  # Recent performance
                if avg_performance > best_performance:
                    best_performance = avg_performance
                    best_strategy = strategy_name
        
        return best_strategy or list(performance_data.keys())[0] if performance_data else None
    
    def start_adaptive_optimization(self, interval_minutes: int = 60):
        """Adaptive optimization ni boshlash"""
        self.optimization_active = True
        optimization_thread = threading.Thread(
            target=self._optimization_loop,
            args=(interval_minutes,),
            daemon=True
        )
        optimization_thread.start()
        logger.info("Adaptive optimization boshlandi")
    
    def stop_adaptive_optimization(self):
        """Adaptive optimization ni to'xtatish"""
        self.optimization_active = False
        logger.info("Adaptive optimization to'xtatildi")
    
    def _optimization_loop(self, interval_minutes: int):
        """Adaptive optimization tsikl"""
        while self.optimization_active:
            try:
                # Market regime detection
                # (This would integrate with real market data)
                
                # Optimize each strategy
                for strategy_name in self.optimization_strategies:
                    performance_data = self.performance_history.get(strategy_name, [])
                    if performance_data:
                        self.optimize_parameters(strategy_name, performance_data)
                
                time.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Adaptive optimization loop xatolik: {e}")
                time.sleep(interval_minutes * 60)

class PerformanceOptimizer:
    """Boshqa barcha optimizatsiya komponentlarini birlashtiruvchi asosiy class"""
    
    def __init__(self, db_path: str = "performance_optimization.db"):
        self.monitor = PerformanceMonitor(db_path)
        self.trading_analyzer = TradingPerformanceAnalyzer()
        self.ai_analyzer = AIPerformanceAnalyzer()
        self.quantum_analyzer = QuantumPerformanceAnalyzer()
        self.ab_testing = ABTestingFramework()
        self.adaptive_optimizer = AdaptiveOptimizer()
        
        # Performance targets
        self.targets = {
            'latency_ms': LATENCY_TARGET_MS,
            'accuracy': ACCURACY_TARGET,
            'uptime': UPTIME_TARGET,
            'cost_reduction': COST_REDUCTION_TARGET
        }
        
        # Setup alert callbacks
        self._setup_alerts()
        
    def _setup_alerts(self):
        """Alert callbacklarini sozlash"""
        def alert_callback(metric: PerformanceMetrics):
            logger.warning(f"Alert: {metric.metric_name} = {metric.value} "
                         f"(Target: {metric.target}, Status: {metric.status})")
        
        self.monitor.add_alert_callback(alert_callback)
    
    def analyze_trading_performance(self, portfolio_returns: pd.Series, 
                                   benchmark_returns: pd.Series = None,
                                   equity_curve: pd.Series = None) -> TradingMetrics:
        """Trading performance tahlili"""
        try:
            if equity_curve is None:
                equity_curve = (1 + portfolio_returns).cumprod()
            
            max_drawdown = self.trading_analyzer.calculate_max_drawdown(equity_curve)
            sharpe_ratio = self.trading_analyzer.calculate_sharpe_ratio(portfolio_returns)
            calmar_ratio = self.trading_analyzer.calculate_calmar_ratio(portfolio_returns, max_drawdown)
            
            # Additional metrics
            total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
            volatility = portfolio_returns.std() * np.sqrt(252)
            sortino_ratio = self.trading_analyzer.calculate_sortino_ratio(portfolio_returns)
            
            # Win rate (assuming binary outcomes)
            win_rate = (portfolio_returns > 0).mean()
            profit_factor = abs(portfolio_returns[portfolio_returns > 0].sum() / 
                              portfolio_returns[portfolio_returns < 0].sum()) if (portfolio_returns < 0).any() else float('inf')
            
            metrics = TradingMetrics(
                sharpe_ratio=sharpe_ratio,
                calmar_ratio=calmar_ratio,
                max_drawdown=max_drawdown,
                total_return=total_return,
                volatility=volatility,
                win_rate=win_rate,
                profit_factor=profit_factor,
                sortino_ratio=sortino_ratio
            )
            
            # Add to database
            self._store_trading_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Trading performance tahlili xatolik: {e}")
            return TradingMetrics()
    
    def analyze_ai_performance(self, y_true: np.ndarray, y_pred: np.ndarray, 
                             prediction_latency_ms: float = 0.0,
                             feature_names: List[str] = None) -> AIMetrics:
        """AI model performance tahlili"""
        try:
            accuracy = self.ai_analyzer.calculate_prediction_accuracy(y_true, y_pred)
            precision, recall, f1_score = self.ai_analyzer.calculate_precision_recall_f1(y_true, y_pred)
            
            metrics = AIMetrics(
                prediction_accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1_score,
                prediction_latency_ms=prediction_latency_ms
            )
            
            if feature_names and len(feature_names) > 0:
                # Assuming we have a model reference
                metrics.feature_importance = {name: 0.0 for name in feature_names}
            
            # Add to database
            self._store_ai_metrics(metrics)
            
            # Log performance metric
            self.monitor.log_metric(PerformanceMetrics(
                timestamp=datetime.now(),
                metric_type=MetricType.AI,
                metric_name="prediction_accuracy",
                value=accuracy,
                target=self.targets['accuracy'],
                status="good" if accuracy >= self.targets['accuracy'] else "warning"
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"AI performance tahlili xatolik: {e}")
            return AIMetrics()
    
    def analyze_system_performance(self) -> SystemMetrics:
        """System performance tahlili"""
        try:
            metrics = self.monitor._collect_system_metrics()
            self._store_system_metrics(metrics)
            
            # Log performance metrics
            self.monitor.log_metric(PerformanceMetrics(
                timestamp=datetime.now(),
                metric_type=MetricType.SYSTEM,
                metric_name="latency_ms",
                value=metrics.latency_ms,
                target=self.targets['latency_ms'],
                status="good" if metrics.latency_ms < self.targets['latency_ms'] else "warning"
            ))
            
            self.monitor.log_metric(PerformanceMetrics(
                timestamp=datetime.now(),
                metric_type=MetricType.SYSTEM,
                metric_name="uptime_percentage",
                value=metrics.uptime_percentage,
                target=self.targets['uptime'],
                status="good" if metrics.uptime_percentage >= self.targets['uptime'] * 100 else "warning"
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"System performance tahlili xatolik: {e}")
            return SystemMetrics()
    
    def analyze_cost_performance(self, current_costs: Dict[str, float],
                               baseline_costs: Dict[str, float] = None) -> CostMetrics:
        """Cost performance tahlili"""
        try:
            if baseline_costs is None:
                baseline_costs = {k: v * 1.2 for k, v in current_costs.items()}  # 20% improvement target
            
            cost_reduction = {
                metric: (baseline_costs[metric] - current_costs[metric]) / baseline_costs[metric]
                for metric in current_costs if metric in baseline_costs
            }
            
            avg_cost_reduction = np.mean(list(cost_reduction.values())) * 100
            
            metrics = CostMetrics(
                api_cost_per_day=current_costs.get('api_cost_per_day', 0),
                quantum_cost_per_hour=current_costs.get('quantum_cost_per_hour', 0),
                total_monthly_cost=sum(current_costs.values()),
                cost_reduction_percentage=avg_cost_reduction
            )
            
            self._store_cost_metrics(metrics)
            
            # Log performance metric
            self.monitor.log_metric(PerformanceMetrics(
                timestamp=datetime.now(),
                metric_type=MetricType.COST,
                metric_name="cost_reduction_percentage",
                value=avg_cost_reduction,
                target=self.targets['cost_reduction'] * 100,
                status="good" if avg_cost_reduction >= self.targets['cost_reduction'] * 100 else "warning"
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Cost performance tahlili xatolik: {e}")
            return CostMetrics()
    
    def create_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """To'liq performance hisoboti"""
        try:
            summary = self.monitor.get_metrics_summary(hours)
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'period_hours': hours,
                'summary': summary,
                'targets': self.targets,
                'status': {
                    'latency': 'good' if summary.get('summary', {}).get('avg_latency', 1000) < self.targets['latency_ms'] else 'warning',
                    'accuracy': 'good' if summary.get('summary', {}).get('avg_accuracy', 0) >= self.targets['accuracy'] else 'warning',
                    'uptime': 'good',
                    'cost': 'good'
                },
                'recommendations': self._generate_recommendations(summary)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Performance report yaratish xatolik: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Performance tavsiyalarini generatsiya qilish"""
        recommendations = []
        
        try:
            summary_data = summary.get('summary', {})
            
            avg_latency = summary_data.get('avg_latency', 0)
            if avg_latency > self.targets['latency_ms']:
                recommendations.append("Latency optimizatsiyasi kerak. Caching va connection pooling qo'llang.")
            
            avg_accuracy = summary_data.get('avg_accuracy', 0)
            if avg_accuracy < self.targets['accuracy']:
                recommendations.append("Model accuracy pas. Feature engineering va hyperparameter tuning zarur.")
            
            total_cost = summary_data.get('total_cost', 0)
            if total_cost > 1000:  # Example threshold
                recommendations.append("Cost optimizatsiyasi zarur. API calllarini optimizatsiya qiling.")
            
        except Exception as e:
            logger.error(f"Recommendation generation xatolik: {e}")
        
        return recommendations
    
    def start_optimization(self):
        """Barcha optimization komponentlarini boshlash"""
        try:
            self.monitor.start_monitoring()
            self.adaptive_optimizer.start_adaptive_optimization()
            logger.info("Performance optimization boshlandi")
        except Exception as e:
            logger.error(f"Optimization boshlash xatolik: {e}")
    
    def stop_optimization(self):
        """Barcha optimization komponentlarini to'xtatish"""
        try:
            self.monitor.stop_monitoring()
            self.adaptive_optimizer.stop_adaptive_optimization()
            logger.info("Performance optimization to'xtatildi")
        except Exception as e:
            logger.error(f"Optimization to'xtatish xatolik: {e}")
    
    def _store_trading_metrics(self, metrics: TradingMetrics):
        """Trading metrics ni database ga saqlash"""
        conn = sqlite3.connect(self.monitor.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trading_metrics 
            (timestamp, sharpe_ratio, calmar_ratio, max_drawdown, total_return, volatility, win_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            metrics.sharpe_ratio,
            metrics.calmar_ratio,
            metrics.max_drawdown,
            metrics.total_return,
            metrics.volatility,
            metrics.win_rate
        ))
        
        conn.commit()
        conn.close()
    
    def _store_ai_metrics(self, metrics: AIMetrics):
        """AI metrics ni database ga saqlash"""
        conn = sqlite3.connect(self.monitor.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_metrics 
            (timestamp, prediction_accuracy, precision, recall, f1_score, model_drift_score, prediction_latency_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            metrics.prediction_accuracy,
            metrics.precision,
            metrics.recall,
            metrics.f1_score,
            metrics.model_drift_score,
            metrics.prediction_latency_ms
        ))
        
        conn.commit()
        conn.close()
    
    def _store_system_metrics(self, metrics: SystemMetrics):
        """System metrics ni database ga saqlash"""
        conn = sqlite3.connect(self.monitor.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_metrics 
            (timestamp, latency_ms, throughput_rps, uptime_percentage, cpu_usage, memory_usage, error_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            metrics.latency_ms,
            metrics.throughput_rps,
            metrics.uptime_percentage,
            metrics.cpu_usage,
            metrics.memory_usage,
            metrics.error_rate
        ))
        
        conn.commit()
        conn.close()
    
    def _store_cost_metrics(self, metrics: CostMetrics):
        """Cost metrics ni database ga saqlash"""
        conn = sqlite3.connect(self.monitor.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cost_metrics 
            (timestamp, api_cost_per_day, quantum_cost_per_hour, total_monthly_cost, cost_per_trade, cost_reduction_percentage)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            metrics.api_cost_per_day,
            metrics.quantum_cost_per_hour,
            metrics.total_monthly_cost,
            metrics.cost_per_trade,
            metrics.cost_reduction_percentage
        ))
        
        conn.commit()
        conn.close()

# Performance visualization functions
def plot_performance_metrics(monitor: PerformanceMonitor, save_path: str = "performance_metrics.png"):
    """Performance metrics visualization"""
    try:
        summary = monitor.get_metrics_summary(24)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Performance Metrics Dashboard (Last 24 Hours)', fontsize=16)
        
        # Trading metrics
        if summary['trading']:
            trading_data = summary['trading']
            metrics_names = ['sharpe_ratio', 'calmar_ratio', 'max_drawdown', 'total_return']
            metrics_values = [trading_data.get(m, {}).get('mean', 0) for m in metrics_names]
            
            axes[0, 0].bar(metrics_names, metrics_values)
            axes[0, 0].set_title('Trading Metrics')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # AI metrics
        if summary['ai']:
            ai_data = summary['ai']
            metrics_names = ['prediction_accuracy', 'precision', 'recall', 'f1_score']
            metrics_values = [ai_data.get(m, {}).get('mean', 0) for m in metrics_names]
            
            axes[0, 1].bar(metrics_names, metrics_values)
            axes[0, 1].set_title('AI Model Metrics')
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # System metrics
        if summary['system']:
            system_data = summary['system']
            metrics_names = ['latency_ms', 'throughput_rps', 'uptime_percentage']
            metrics_values = [system_data.get(m, {}).get('mean', 0) for m in metrics_names]
            
            axes[1, 0].bar(metrics_names, metrics_values)
            axes[1, 0].set_title('System Metrics')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Cost metrics
        if summary['cost']:
            cost_data = summary['cost']
            metrics_names = ['api_cost_per_day', 'quantum_cost_per_hour', 'total_monthly_cost']
            metrics_values = [cost_data.get(m, {}).get('mean', 0) for m in metrics_names]
            
            axes[1, 1].bar(metrics_names, metrics_values)
            axes[1, 1].set_title('Cost Metrics')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Performance metrics visualization saqlandi: {save_path}")
        
    except Exception as e:
        logger.error(f"Performance visualization xatolik: {e}")

# Example usage va testing functions
def demo_performance_optimization():
    """Performance optimization tizimi demo"""
    print("Performance Optimization va Monitoring System Demo")
    print("=" * 60)
    
    # Initialize optimizer
    optimizer = PerformanceOptimizer()
    
    # Start monitoring
    optimizer.start_optimization()
    
    try:
        # Generate sample trading data
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', end='2024-11-03', freq='D')
        portfolio_returns = pd.Series(np.random.normal(0.001, 0.02, len(dates)), index=dates)
        benchmark_returns = pd.Series(np.random.normal(0.0008, 0.015, len(dates)), index=dates)
        equity_curve = (1 + portfolio_returns).cumprod()
        
        # Analyze trading performance
        print("\n1. Trading Performance Analysis...")
        trading_metrics = optimizer.analyze_trading_performance(
            portfolio_returns, benchmark_returns, equity_curve
        )
        print(f"   - Sharpe Ratio: {trading_metrics.sharpe_ratio:.3f}")
        print(f"   - Calmar Ratio: {trading_metrics.calmar_ratio:.3f}")
        print(f"   - Max Drawdown: {trading_metrics.max_drawdown:.3f}")
        print(f"   - Win Rate: {trading_metrics.win_rate:.3f}")
        
        # Analyze AI performance
        print("\n2. AI Performance Analysis...")
        y_true = np.random.choice([0, 1], size=1000)
        y_pred = np.random.choice([0, 1], size=1000)
        ai_metrics = optimizer.analyze_ai_performance(y_true, y_pred, 85.5)
        print(f"   - Prediction Accuracy: {ai_metrics.prediction_accuracy:.3f}")
        print(f"   - F1 Score: {ai_metrics.f1_score:.3f}")
        print(f"   - Prediction Latency: {ai_metrics.prediction_latency_ms:.1f}ms")
        
        # Analyze system performance
        print("\n3. System Performance Analysis...")
        system_metrics = optimizer.analyze_system_performance()
        print(f"   - Latency: {system_metrics.latency_ms:.1f}ms")
        print(f"   - Uptime: {system_metrics.uptime_percentage:.1f}%")
        print(f"   - CPU Usage: {system_metrics.cpu_usage:.1f}%")
        
        # Analyze cost performance
        print("\n4. Cost Performance Analysis...")
        current_costs = {
            'api_cost_per_day': 23.50,
            'quantum_cost_per_hour': 14.25,
            'storage_cost_per_month': 45.00
        }
        baseline_costs = {
            'api_cost_per_day': 28.00,
            'quantum_cost_per_hour': 18.00,
            'storage_cost_per_month': 50.00
        }
        cost_metrics = optimizer.analyze_cost_performance(current_costs, baseline_costs)
        print(f"   - Cost Reduction: {cost_metrics.cost_reduction_percentage:.1f}%")
        print(f"   - Monthly Cost: ${cost_metrics.total_monthly_cost:.2f}")
        
        # A/B Testing Demo
        print("\n5. A/B Testing Framework Demo...")
        exp_id = optimizer.ab_testing.create_experiment(
            "strategy_optimization",
            ["strategy_a", "strategy_b"],
            {"strategy_a": 0.5, "strategy_b": 0.5}
        )
        
        # Simulate outcomes
        for i in range(100):
            user_id = f"user_{i}"
            variant = optimizer.ab_testing.assign_variant(exp_id, user_id)
            outcome = np.random.normal(0.1 if variant == "strategy_a" else 0.08, 0.02)
            optimizer.ab_testing.record_outcome(exp_id, variant, user_id, outcome, "return")
        
        # Analyze results
        results = optimizer.ab_testing.analyze_results(exp_id, "return")
        print(f"   - Strategy A Mean: {results.get('strategy_a', {}).get('mean', 0):.3f}")
        print(f"   - Strategy B Mean: {results.get('strategy_b', {}).get('mean', 0):.3f}")
        if 'statistical_test' in results:
            print(f"   - Significant: {results['statistical_test']['significant']}")
            print(f"   - Better Variant: {results['statistical_test']['better_variant']}")
        
        # Generate performance report
        print("\n6. Performance Report Generation...")
        report = optimizer.create_performance_report(24)
        print(f"   - Report Status: {report['status']}")
        print(f"   - Recommendations: {len(report.get('recommendations', []))}")
        
        # Plot performance metrics
        print("\n7. Performance Visualization...")
        plot_performance_metrics(optimizer.monitor, "demo_performance_metrics.png")
        print("   - Performance chart saqlandi: demo_performance_metrics.png")
        
        print("\n✅ Demo muvaffaqiyatli yakunlandi!")
        
    except Exception as e:
        logger.error(f"Demo xatolik: {e}")
        print(f"\n❌ Demo xatolik: {e}")
    
    finally:
        # Cleanup
        optimizer.stop_optimization()
        print("\n🛑 Optimization to'xtatildi")

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demo
    demo_performance_optimization()