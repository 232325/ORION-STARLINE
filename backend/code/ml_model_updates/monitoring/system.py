"""
Model Monitoring System
ML model drift detection, performance monitoring, va alerting
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import time
from collections import deque, defaultdict
import warnings

# ML va statistik kutubxonalar
try:
    from scipy import stats
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
except ImportError:
    stats = None
    sklearn = None

@dataclass
class MonitoringMetrics:
    """Monitoring metrikalari"""
    timestamp: datetime
    model_name: str
    version_id: str
    
    # Performance metrics
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    
    # Data quality metrics
    data_quality_score: float
    missing_values_ratio: float
    outlier_ratio: float
    
    # Drift metrics
    feature_drift_score: float
    prediction_drift_score: float
    concept_drift_score: float
    
    # System metrics
    prediction_latency_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    
    # Alert status
    alert_level: str = "normal"  # normal, warning, critical
    alert_message: str = ""

@dataclass
class DriftAnalysis:
    """Drift tahlili natijalari"""
    feature_name: str
    drift_type: str  # feature_drift, concept_drift, prediction_drift
    drift_score: float
    drift_detected: bool
    statistical_test: str
    p_value: float
    threshold: float
    timestamp: datetime

class DataQualityMonitor:
    """Ma'lumotlar sifati nazorati"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def check_data_quality(self, data: pd.DataFrame) -> Dict[str, float]:
        """Ma'lumotlar sifatini tekshirish"""
        quality_metrics = {}
        
        # Missing values
        missing_ratio = data.isnull().sum().sum() / (len(data) * len(data.columns))
        quality_metrics['missing_values_ratio'] = missing_ratio
        
        # Duplicated rows
        duplicate_ratio = data.duplicated().sum() / len(data)
        quality_metrics['duplicate_ratio'] = duplicate_ratio
        
        # Outliers (IQR method)
        outlier_ratio = self._calculate_outlier_ratio(data)
        quality_metrics['outlier_ratio'] = outlier_ratio
        
        # Data type consistency
        type_consistency = self._check_data_types(data)
        quality_metrics['type_consistency'] = type_consistency
        
        # Overall quality score
        quality_metrics['overall_score'] = (
            (1 - missing_ratio) * 0.3 +
            (1 - duplicate_ratio) * 0.2 +
            (1 - outlier_ratio) * 0.3 +
            type_consistency * 0.2
        )
        
        return quality_metrics
        
    def _calculate_outlier_ratio(self, data: pd.DataFrame) -> float:
        """Outlier nisbatini hisoblash"""
        if data.select_dtypes(include=[np.number]).empty:
            return 0.0
            
        numeric_data = data.select_dtypes(include=[np.number])
        outlier_count = 0
        total_count = 0
        
        for column in numeric_data.columns:
            Q1 = numeric_data[column].quantile(0.25)
            Q3 = numeric_data[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = ((numeric_data[column] < lower_bound) | 
                       (numeric_data[column] > upper_bound)).sum()
            
            outlier_count += outliers
            total_count += len(numeric_data)
            
        return outlier_count / total_count if total_count > 0 else 0.0
        
    def _check_data_types(self, data: pd.DataFrame) -> float:
        """Data type konsistentligini tekshirish"""
        # Oddiy implementatsiya
        return 1.0  # Barcha data type'lar consistent deb faraz qilish

class DriftDetector:
    """Model drift detection"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.baseline_data = {}
        self.baseline_stats = {}
        
    def set_baseline(self, data: pd.DataFrame, target_column: str):
        """Baseline data'ni o'rnatish"""
        self.baseline_data[target_column] = data
        
        # Baseline statistikalarni hisoblash
        self.baseline_stats[target_column] = {
            'feature_means': data.drop(columns=[target_column]).mean(),
            'feature_stds': data.drop(columns=[target_column]).std(),
            'feature_correlations': data.drop(columns=[target_column]).corr(),
            'target_distribution': data[target_column].value_counts(normalize=True).to_dict()
        }
        
    def detect_feature_drift(self, new_data: pd.DataFrame, target_column: str) -> List[DriftAnalysis]:
        """Feature drift detection"""
        if target_column not in self.baseline_data:
            self.logger.warning(f"Baseline data topilmadi: {target_column}")
            return []
            
        drift_results = []
        baseline = self.baseline_data[target_column]
        
        # Har bir feature uchun drift tekshirish
        for feature in new_data.drop(columns=[target_column]).columns:
            if feature in baseline.drop(columns=[target_column]).columns:
                
                # Kolmogorov-Smirnov test
                if stats:
                    statistic, p_value = stats.ks_2samp(
                        baseline[feature].dropna(),
                        new_data[feature].dropna()
                    )
                else:
                    # Fallback - simple statistical comparison
                    baseline_mean = baseline[feature].mean()
                    baseline_std = baseline[feature].std()
                    new_mean = new_data[feature].mean()
                    new_std = new_data[feature].std()
                    
                    statistic = abs(baseline_mean - new_mean) / (baseline_std + 1e-8)
                    p_value = 0.05 if statistic > 0.1 else 0.5
                    
                # Drift score hisoblash
                drift_score = min(statistic, 1.0)
                threshold = self.config.get('feature_drift_threshold', 0.1)
                drift_detected = drift_score > threshold
                
                drift_analysis = DriftAnalysis(
                    feature_name=feature,
                    drift_type="feature_drift",
                    drift_score=drift_score,
                    drift_detected=drift_detected,
                    statistical_test="ks_2samp",
                    p_value=p_value,
                    threshold=threshold,
                    timestamp=datetime.now()
                )
                
                drift_results.append(drift_analysis)
                
        return drift_results
        
    def detect_concept_drift(self, predictions: np.ndarray, true_labels: np.ndarray) -> DriftAnalysis:
        """Concept drift detection"""
        if len(predictions) != len(true_labels):
            raise ValueError("Predictions va true_labels uzunligi mos emas")
            
        # Oddiy concept drift detection
        # Hozircha accuracy trend asosida
        accuracy = np.mean(predictions == true_labels) if sklearn else 0.8
        
        # Baseline accuracy
        baseline_accuracy = self.config.get('baseline_accuracy', 0.9)
        
        # Drift score
        drift_score = max(0, baseline_accuracy - accuracy) / baseline_accuracy
        threshold = self.config.get('concept_drift_threshold', 0.1)
        drift_detected = drift_score > threshold
        
        return DriftAnalysis(
            feature_name="concept_drift",
            drift_type="concept_drift",
            drift_score=drift_score,
            drift_detected=drift_detected,
            statistical_test="accuracy_degradation",
            p_value=0.05 if drift_detected else 0.8,
            threshold=threshold,
            timestamp=datetime.now()
        )
        
    def detect_prediction_drift(self, predictions: np.ndarray, baseline_predictions: np.ndarray) -> DriftAnalysis:
        """Prediction drift detection"""
        if stats:
            statistic, p_value = stats.ks_2samp(baseline_predictions, predictions)
        else:
            # Simple statistical comparison
            baseline_mean = np.mean(baseline_predictions)
            current_mean = np.mean(predictions)
            baseline_std = np.std(baseline_predictions)
            
            statistic = abs(baseline_mean - current_mean) / (baseline_std + 1e-8)
            p_value = 0.05 if statistic > 0.1 else 0.5
            
        drift_score = min(statistic, 1.0)
        threshold = self.config.get('prediction_drift_threshold', 0.1)
        drift_detected = drift_score > threshold
        
        return DriftAnalysis(
            feature_name="prediction_drift",
            drift_type="prediction_drift",
            drift_score=drift_score,
            drift_detected=drift_detected,
            statistical_test="ks_2samp",
            p_value=p_value,
            threshold=threshold,
            timestamp=datetime.now()
        )

class PerformanceMonitor:
    """Model performance monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.performance_history = deque(maxlen=1000)
        
    def calculate_performance_metrics(self, predictions: np.ndarray, 
                                    true_labels: np.ndarray) -> Dict[str, float]:
        """Performance metrikalarni hisoblash"""
        if len(predictions) != len(true_labels):
            raise ValueError("Predictions va true_labels uzunligi mos emas")
            
        metrics = {}
        
        # Classification metrics
        if sklearn:
            metrics['accuracy'] = accuracy_score(true_labels, predictions)
            
            if len(np.unique(true_labels)) > 2:  # Multi-class
                metrics['precision'] = precision_score(true_labels, predictions, average='weighted')
                metrics['recall'] = recall_score(true_labels, predictions, average='weighted')
                metrics['f1_score'] = f1_score(true_labels, predictions, average='weighted')
            else:  # Binary classification
                metrics['precision'] = precision_score(true_labels, predictions)
                metrics['recall'] = recall_score(true_labels, predictions)
                metrics['f1_score'] = f1_score(true_labels, predictions)
        else:
            # Fallback metrics
            metrics['accuracy'] = np.mean(predictions == true_labels)
            metrics['precision'] = metrics['accuracy'] * 0.95  # Approximation
            metrics['recall'] = metrics['accuracy'] * 0.95
            metrics['f1_score'] = metrics['accuracy'] * 0.9
            
        return metrics
        
    def track_prediction_latency(self, prediction_times: List[float]) -> Dict[str, float]:
        """Prediction latency tracking"""
        if not prediction_times:
            return {'avg_latency_ms': 0, 'p95_latency_ms': 0, 'p99_latency_ms': 0}
            
        latency_ms = [t * 1000 for t in prediction_times]  # Convert to milliseconds
        
        return {
            'avg_latency_ms': np.mean(latency_ms),
            'p95_latency_ms': np.percentile(latency_ms, 95),
            'p99_latency_ms': np.percentile(latency_ms, 99)
        }
        
    def check_performance_degradation(self, current_metrics: Dict[str, float], 
                                    baseline_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Performance degradation tekshirish"""
        degradation = {}
        
        for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
            if metric in current_metrics and metric in baseline_metrics:
                current = current_metrics[metric]
                baseline = baseline_metrics[metric]
                
                if baseline > 0:
                    degradation_ratio = max(0, (baseline - current) / baseline)
                    degradation[metric] = {
                        'current': current,
                        'baseline': baseline,
                        'degradation_ratio': degradation_ratio,
                        'degraded': degradation_ratio > self.config.get('performance_threshold', 0.05)
                    }
                    
        return degradation

class AlertManager:
    """Alert boshqaruvchisi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.alert_channels = config.get('alert_channels', ['email', 'webhook'])
        self.alert_rules = config.get('alert_rules', {})
        self.alert_history = deque(maxlen=1000)
        
    def should_alert(self, metrics: MonitoringMetrics) -> Tuple[str, str]:
        """Alert kerak yoki yo'qligini tekshirish"""
        alert_level = "normal"
        alert_message = ""
        
        # Critical alerts
        if metrics.accuracy < self.config.get('critical_accuracy_threshold', 0.7):
            alert_level = "critical"
            alert_message = f"Model accuracy juda past: {metrics.accuracy:.3f}"
        elif metrics.feature_drift_score > self.config.get('critical_drift_threshold', 0.3):
            alert_level = "critical"
            alert_message = f"Yuqori feature drift: {metrics.feature_drift_score:.3f}"
        elif metrics.data_quality_score < self.config.get('critical_quality_threshold', 0.7):
            alert_level = "critical"
            alert_message = f"Ma'lumotlar sifati past: {metrics.data_quality_score:.3f}"
            
        # Warning alerts
        elif alert_level == "normal":
            if metrics.accuracy < self.config.get('warning_accuracy_threshold', 0.85):
                alert_level = "warning"
                alert_message = f"Model accuracy pasaymoqda: {metrics.accuracy:.3f}"
            elif metrics.feature_drift_score > self.config.get('warning_drift_threshold', 0.15):
                alert_level = "warning"
                alert_message = f"Feature drift aniqlangan: {metrics.feature_drift_score:.3f}"
            elif metrics.data_quality_score < self.config.get('warning_quality_threshold', 0.85):
                alert_level = "warning"
                alert_message = f"Ma'lumotlar sifati pasaymoqda: {metrics.data_quality_score:.3f}"
                
        return alert_level, alert_message
        
    def send_alert(self, alert_level: str, alert_message: str, 
                  model_name: str, metrics: MonitoringMetrics):
        """Alert yuborish"""
        
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'alert_level': alert_level,
            'message': alert_message,
            'metrics': asdict(metrics)
        }
        
        # Alert tarixiga qo'shish
        self.alert_history.append(alert_data)
        
        # Alert channels ga yuborish
        for channel in self.alert_channels:
            try:
                self._send_to_channel(channel, alert_data)
            except Exception as e:
                self.logger.error(f"Alert yuborish xatosi {channel}: {str(e)}")
                
        self.logger.warning(f"Alert yuborildi [{alert_level}]: {alert_message}")
        
    def _send_to_channel(self, channel: str, alert_data: Dict[str, Any]):
        """Channel bo'yicha alert yuborish"""
        if channel == 'email':
            self._send_email_alert(alert_data)
        elif channel == 'webhook':
            self._send_webhook_alert(alert_data)
        elif channel == 'log':
            self.logger.warning(f"Alert: {alert_data['message']}")
            
    def _send_email_alert(self, alert_data: Dict[str, Any]):
        """Email alert yuborish"""
        # Hozircha faqat log
        self.logger.info(f"Email alert: {alert_data['message']}")
        
    def _send_webhook_alert(self, alert_data: Dict[str, Any]):
        """Webhook alert yuborish"""
        # Hozircha faqat log
        self.logger.info(f"Webhook alert: {alert_data['message']}")

class ModelMonitoringSystem:
    """Umumiy model monitoring tizimi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Komponentlar
        self.data_quality_monitor = DataQualityMonitor(config.get('data_quality', {}))
        self.drift_detector = DriftDetector(config.get('drift_detection', {}))
        self.performance_monitor = PerformanceMonitor(config.get('performance', {}))
        self.alert_manager = AlertManager(config.get('alerts', {}))
        
        # State
        self.monitoring_status = {}
        self.baseline_data = {}
        self.metrics_history = defaultdict(deque)
        
        # Monitoring flags
        self.is_monitoring = False
        self.monitoring_thread = None
        
    def start_monitoring(self, model_name: str):
        """Monitoring boshlanishi"""
        if self.is_monitoring:
            self.logger.warning("Monitoring allaqachon ishga tushgan")
            return
            
        self.is_monitoring = True
        self.monitoring_status[model_name] = "running"
        
        self.logger.info(f"Model monitoring boshlandi: {model_name}")
        
    def stop_monitoring(self, model_name: str):
        """Monitoring to'xtashi"""
        self.is_monitoring = False
        self.monitoring_status[model_name] = "stopped"
        
        self.logger.info(f"Model monitoring to'xtadi: {model_name}")
        
    def set_baseline(self, model_name: str, baseline_data: pd.DataFrame, target_column: str):
        """Baseline data o'rnatish"""
        self.baseline_data[model_name] = baseline_data
        self.drift_detector.set_baseline(baseline_data, target_column)
        
        self.logger.info(f"Baseline o'rnatildi: {model_name}")
        
    def monitor_prediction(self, model_name: str, version_id: str,
                          predictions: np.ndarray, true_labels: np.ndarray,
                          prediction_latency: float = None) -> MonitoringMetrics:
        """Prediction monitoring"""
        
        timestamp = datetime.now()
        
        # Performance metrics
        performance_metrics = self.performance_monitor.calculate_performance_metrics(
            predictions, true_labels
        )
        
        # Data quality (prediction batch uchun)
        # Bu yerda haqiqiy data yo'q, shuning uchun placeholder
        data_quality_metrics = {
            'overall_score': 0.95,
            'missing_values_ratio': 0.01,
            'duplicate_ratio': 0.005,
            'outlier_ratio': 0.02,
            'type_consistency': 1.0
        }
        
        # Drift detection
        feature_drift_score = 0.05  # Placeholder
        prediction_drift_score = 0.03  # Placeholder
        concept_drift_score = 0.02  # Placeholder
        
        if model_name in self.baseline_data:
            # Concept drift detection
            concept_drift = self.drift_detector.detect_concept_drift(predictions, true_labels)
            concept_drift_score = concept_drift.drift_score
            
        # System metrics
        memory_usage_mb = 100.0  # Placeholder
        cpu_usage_percent = 25.0  # Placeholder
        
        # Monitoring metrics yaratish
        metrics = MonitoringMetrics(
            timestamp=timestamp,
            model_name=model_name,
            version_id=version_id,
            accuracy=performance_metrics.get('accuracy', 0.0),
            precision=performance_metrics.get('precision', 0.0),
            recall=performance_metrics.get('recall', 0.0),
            f1_score=performance_metrics.get('f1_score', 0.0),
            data_quality_score=data_quality_metrics['overall_score'],
            missing_values_ratio=data_quality_metrics['missing_values_ratio'],
            outlier_ratio=data_quality_metrics['outlier_ratio'],
            feature_drift_score=feature_drift_score,
            prediction_drift_score=prediction_drift_score,
            concept_drift_score=concept_drift_score,
            prediction_latency_ms=prediction_latency * 1000 if prediction_latency else 0.0,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent
        )
        
        # Alert checking
        alert_level, alert_message = self.alert_manager.should_alert(metrics)
        metrics.alert_level = alert_level
        metrics.alert_message = alert_message
        
        # Alert yuborish
        if alert_level in ['warning', 'critical']:
            self.alert_manager.send_alert(alert_level, alert_message, model_name, metrics)
            
        # Metrics ni tarixga qo'shish
        self.metrics_history[model_name].append(metrics)
        
        self.logger.debug(f"Monitoring completed: {model_name}, accuracy={metrics.accuracy:.3f}")
        return metrics
        
    def check_data_drift(self, model_name: str, new_data: pd.DataFrame, 
                        target_column: str) -> List[DriftAnalysis]:
        """Data drift tekshirish"""
        if model_name not in self.baseline_data:
            self.logger.warning(f"Baseline data topilmadi: {model_name}")
            return []
            
        drift_results = self.drift_detector.detect_feature_drift(new_data, target_column)
        
        # Drift results log
        for drift in drift_results:
            if drift.drift_detected:
                self.logger.warning(f"Drift detected: {model_name} - {drift.feature_name} "
                                  f"({drift.drift_type}): score={drift.drift_score:.3f}")
                
        return drift_results
        
    def get_monitoring_summary(self, model_name: str, hours: int = 24) -> Dict[str, Any]:
        """Monitoring xulosasi olish"""
        if model_name not in self.metrics_history:
            return {}
            
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history[model_name] 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
            
        # Averages
        avg_accuracy = np.mean([m.accuracy for m in recent_metrics])
        avg_drift_score = np.mean([m.feature_drift_score for m in recent_metrics])
        avg_quality_score = np.mean([m.data_quality_score for m in recent_metrics])
        
        # Alert statistics
        alert_counts = {
            'critical': len([m for m in recent_metrics if m.alert_level == 'critical']),
            'warning': len([m for m in recent_metrics if m.alert_level == 'warning']),
            'normal': len([m for m in recent_metrics if m.alert_level == 'normal'])
        }
        
        # Trends
        accuracies = [m.accuracy for m in recent_metrics]
        accuracy_trend = "stable"
        if len(accuracies) > 5:
            recent_5 = accuracies[-5:]
            first_5 = accuracies[:5]
            if np.mean(recent_5) > np.mean(first_5) + 0.02:
                accuracy_trend = "improving"
            elif np.mean(recent_5) < np.mean(first_5) - 0.02:
                accuracy_trend = "declining"
                
        return {
            'model_name': model_name,
            'time_range_hours': hours,
            'total_predictions': len(recent_metrics),
            'average_accuracy': avg_accuracy,
            'average_drift_score': avg_drift_score,
            'average_quality_score': avg_quality_score,
            'accuracy_trend': accuracy_trend,
            'alert_statistics': alert_counts,
            'last_update': recent_metrics[-1].timestamp.isoformat() if recent_metrics else None
        }
        
    def get_performance_trends(self, model_name: str, days: int = 7) -> Dict[str, Any]:
        """Performance trend tahlili"""
        if model_name not in self.metrics_history:
            return {}
            
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_metrics = [
            m for m in self.metrics_history[model_name] 
            if m.timestamp >= cutoff_time
        ]
        
        if len(recent_metrics) < 2:
            return {}
            
        # Daily aggregations
        daily_metrics = defaultdict(list)
        for metric in recent_metrics:
            day = metric.timestamp.date()
            daily_metrics[day].append(metric)
            
        trend_data = {}
        for day, day_metrics in daily_metrics.items():
            accuracy_values = [m.accuracy for m in day_metrics]
            trend_data[day.isoformat()] = {
                'avg_accuracy': np.mean(accuracy_values),
                'min_accuracy': np.min(accuracy_values),
                'max_accuracy': np.max(accuracy_values),
                'num_predictions': len(accuracy_values)
            }
            
        return trend_data
        
    def export_monitoring_data(self, model_name: str, output_path: str) -> bool:
        """Monitoring ma'lumotlarini eksport qilish"""
        try:
            if model_name not in self.metrics_history:
                return False
                
            data = []
            for metric in self.metrics_history[model_name]:
                data.append(asdict(metric))
                
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            self.logger.info(f"Monitoring data exported: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Export xatosi: {str(e)}")
            return False