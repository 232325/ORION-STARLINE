"""
Model Updater - Model yangilash va boshqaruv tizimi
Model performance monitoring, updating va deployment management
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import json
import pickle
import shutil
from pathlib import Path
import threading
import time
import schedule
from pathlib import Path
import hashlib
import joblib
import warnings
warnings.filterwarnings('ignore')

# ML va monitoring kutubxonalar
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import os

# Email va notification
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders

@dataclass
class ModelUpdateEvent:
    """Model yangilanish voqeasi"""
    event_type: str  # 'performance_degradation', 'drift_detected', 'scheduled_update'
    model_name: str
    current_version: str
    new_version: str
    trigger_reason: str
    confidence_score: float
    timestamp: datetime
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    rollback_info: Optional[Dict[str, Any]] = None

@dataclass
class DeploymentConfig:
    """Deployment konfiguratsiyasi"""
    environment: str  # 'dev', 'staging', 'prod'
    canary_percentage: float
    health_check_enabled: bool
    rollback_enabled: bool
    monitoring_duration: int  # minutes
    alert_thresholds: Dict[str, float]

@dataclass
class ModelMetrics:
    """Model metrikalari"""
    model_name: str
    version: str
    timestamp: datetime
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    latency_p50: float
    latency_p95: float
    throughput: float
    error_rate: float
    data_freshness: float
    drift_score: float

class ModelVersionManager:
    """Model versiyasini boshqarish"""
    
    def __init__(self, base_path: str = "models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.version_registry = self._load_version_registry()
        
    def _load_version_registry(self) -> Dict[str, Any]:
        """Versiya registry yuklash"""
        registry_path = self.base_path / "version_registry.json"
        try:
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load version registry: {e}")
        
        return {"models": {}}
    
    def _save_version_registry(self):
        """Versiya registry saqlash"""
        registry_path = self.base_path / "version_registry.json"
        try:
            with open(registry_path, 'w') as f:
                json.dump(self.version_registry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save version registry: {e}")
    
    def create_model_version(self, model: Any, model_name: str, metadata: Dict[str, Any]) -> str:
        """Yangi model versiyasi yaratish"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"v_{timestamp}"
        
        # Model faylini saqlash
        model_path = self.base_path / f"{model_name}_{version}.pkl"
        joblib.dump(model, model_path)
        
        # Metadata saqlash
        metadata.update({
            'version': version,
            'created_at': datetime.now().isoformat(),
            'model_path': str(model_path),
            'checksum': self._calculate_checksum(model_path)
        })
        
        metadata_path = self.base_path / f"{model_name}_{version}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Registry yangilash
        if model_name not in self.version_registry['models']:
            self.version_registry['models'][model_name] = {
                'current_version': version,
                'versions': []
            }
        
        self.version_registry['models'][model_name]['current_version'] = version
        self.version_registry['models'][model_name]['versions'].append({
            'version': version,
            'created_at': metadata['created_at'],
            'metadata': metadata,
            'status': 'active'
        })
        
        self._save_version_registry()
        
        self.logger.info(f"Created model version {version} for {model_name}")
        return version
    
    def rollback_to_version(self, model_name: str, target_version: str) -> bool:
        """Oldingi versiyaga qaytish"""
        try:
            if model_name in self.version_registry['models']:
                # Load target model
                model_path = self.base_path / f"{model_name}_{target_version}.pkl"
                if model_path.exists():
                    # Archive current version
                    current_version = self.version_registry['models'][model_name]['current_version']
                    self._archive_version(model_name, current_version)
                    
                    # Set new current version
                    self.version_registry['models'][model_name]['current_version'] = target_version
                    self._save_version_registry()
                    
                    self.logger.info(f"Rolled back {model_name} from current version to {target_version}")
                    return True
            
            self.logger.error(f"Could not rollback {model_name} to {target_version}")
            return False
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def _archive_version(self, model_name: str, version: str):
        """Versiyani arxivga joylash"""
        archived_path = self.base_path / "archived"
        archived_path.mkdir(exist_ok=True)
        
        model_path = self.base_path / f"{model_name}_{version}.pkl"
        metadata_path = self.base_path / f"{model_name}_{version}_metadata.json"
        
        if model_path.exists():
            shutil.move(str(model_path), str(archived_path / model_path.name))
        if metadata_path.exists():
            shutil.move(str(metadata_path), str(archived_path / metadata_path.name))
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Fayl checksum hisoblash"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Could not calculate checksum: {e}")
            return ""

class PerformanceMonitor:
    """Model performance monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []
        self.alerts = []
        
    def collect_metrics(self, model_name: str, predictions: np.ndarray, 
                       actuals: pd.Series, inference_time: float) -> ModelMetrics:
        """Performance metrikalari to'plash"""
        # Calculate basic metrics
        mse = mean_squared_error(actuals, predictions)
        mae = mean_absolute_error(actuals, predictions)
        r2 = r2_score(actuals, predictions)
        
        # Additional metrics
        throughput = len(predictions) / inference_time if inference_time > 0 else 0
        error_rate = 0.0  # Mock error rate
        
        # Data freshness (mock)
        data_freshness = 0.95
        
        # Drift score (mock)
        drift_score = 0.05
        
        metrics = ModelMetrics(
            model_name=model_name,
            version="current",  # Get from registry
            timestamp=datetime.now(),
            accuracy=1 - mse,  # Mock accuracy
            precision=0.90,    # Mock precision
            recall=0.88,       # Mock recall
            f1_score=0.89,     # Mock f1_score
            latency_p50=inference_time,
            latency_p95=inference_time * 1.5,
            throughput=throughput,
            error_rate=error_rate,
            data_freshness=data_freshness,
            drift_score=drift_score
        )
        
        self.metrics_history.append(metrics)
        self.logger.info(f"Collected metrics for {model_name}: R2={r2:.3f}, Latency={inference_time:.3f}s")
        
        return metrics
    
    def analyze_performance_trends(self, model_name: str, window_size: int = 100) -> Dict[str, Any]:
        """Performance trendlarini tahlil qilish"""
        model_metrics = [m for m in self.metrics_history if m.model_name == model_name]
        
        if len(model_metrics) < window_size:
            return {'status': 'insufficient_data', 'trend': 'unknown'}
        
        recent_metrics = model_metrics[-window_size:]
        
        # Calculate trends
        r2_trend = self._calculate_trend([m.r2_score for m in recent_metrics])
        latency_trend = self._calculate_trend([m.latency_p50 for m in recent_metrics])
        throughput_trend = self._calculate_trend([m.throughput for m in recent_metrics])
        
        # Anomaly detection
        anomalies = self._detect_anomalies(recent_metrics)
        
        return {
            'model_name': model_name,
            'window_size': window_size,
            'trends': {
                'r2_score': r2_trend,
                'latency': latency_trend,
                'throughput': throughput_trend
            },
            'anomalies': anomalies,
            'status': 'analyzed',
            'analysis_time': datetime.now()
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Trend hisoblash"""
        if len(values) < 2:
            return 'unknown'
        
        # Simple linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if abs(slope) < 0.001:
            return 'stable'
        elif slope > 0:
            return 'improving'
        else:
            return 'degrading'
    
    def _detect_anomalies(self, metrics: List[ModelMetrics]) -> List[Dict[str, Any]]:
        """Anomaliyalarni aniqlash"""
        anomalies = []
        
        if len(metrics) < 10:
            return anomalies
        
        # Simple threshold-based anomaly detection
        r2_values = [m.r2_score for m in metrics]
        r2_mean = np.mean(r2_values)
        r2_std = np.std(r2_values)
        r2_threshold = r2_mean - 2 * r2_std
        
        for i, metric in enumerate(metrics):
            if metric.r2_score < r2_threshold:
                anomalies.append({
                    'timestamp': metric.timestamp,
                    'type': 'low_accuracy',
                    'value': metric.r2_score,
                    'threshold': r2_threshold,
                    'severity': 'high' if metric.r2_score < r2_mean - 3 * r2_std else 'medium'
                })
        
        return anomalies

class DriftDetector:
    """Data drift aniqlash"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.reference_data = {}
        self.drift_history = []
        
    def set_reference_data(self, feature_name: str, data: np.ndarray):
        """Reference ma'lumotlar o'rnatish"""
        self.reference_data[feature_name] = {
            'data': data,
            'mean': np.mean(data),
            'std': np.std(data),
            'timestamp': datetime.now()
        }
        self.logger.info(f"Reference data set for feature: {feature_name}")
    
    def detect_drift(self, new_data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Data drift aniqlash"""
        drift_results = {}
        overall_drift_score = 0
        drift_count = 0
        
        for feature_name, new_values in new_data.items():
            if feature_name in self.reference_data:
                ref_data = self.reference_data[feature_name]['data']
                
                # Statistical drift detection
                drift_score = self._calculate_statistical_drift(ref_data, new_values)
                
                # Distribution comparison
                ks_statistic, p_value = self._kolmogorov_smirnov_test(ref_data, new_values)
                
                drift_results[feature_name] = {
                    'drift_score': drift_score,
                    'ks_statistic': ks_statistic,
                    'p_value': p_value,
                    'drift_detected': drift_score > 0.3 or p_value < 0.05,
                    'timestamp': datetime.now()
                }
                
                if drift_score > 0.1:  # Count significant drifts
                    overall_drift_score += drift_score
                    drift_count += 1
        
        # Overall drift assessment
        if drift_count > 0:
            overall_drift_score /= drift_count
        
        drift_assessment = {
            'feature_drifts': drift_results,
            'overall_drift_score': overall_drift_score,
            'drift_detected': overall_drift_score > 0.3,
            'drift_severity': self._categorize_drift_severity(overall_drift_score),
            'timestamp': datetime.now()
        }
        
        self.drift_history.append(drift_assessment)
        self.logger.info(f"Drift detection completed. Overall score: {overall_drift_score:.3f}")
        
        return drift_assessment
    
    def _calculate_statistical_drift(self, reference: np.ndarray, new_data: np.ndarray) -> float:
        """Statistik drift hisoblash"""
        ref_mean, ref_std = np.mean(reference), np.std(reference)
        new_mean, new_std = np.mean(new_data), np.std(new_data)
        
        # Calculate mean and standard deviation shifts
        mean_shift = abs(new_mean - ref_mean) / (ref_std + 1e-8)
        std_shift = abs(new_std - ref_std) / (ref_std + 1e-8)
        
        # Combined drift score
        drift_score = (mean_shift + std_shift) / 2
        return min(drift_score, 1.0)  # Cap at 1.0
    
    def _kolmogorov_smirnov_test(self, reference: np.ndarray, new_data: np.ndarray) -> Tuple[float, float]:
        """Kolmogorov-Smirnov test"""
        from scipy import stats
        try:
            ks_stat, p_value = stats.ks_2samp(reference, new_data)
            return ks_stat, p_value
        except ImportError:
            # Fallback without scipy
            self.logger.warning("scipy not available, using simplified drift detection")
            return 0.1, 0.5  # Mock values
    
    def _categorize_drift_severity(self, drift_score: float) -> str:
        """Drift severity kategoriyasi"""
        if drift_score < 0.1:
            return 'none'
        elif drift_score < 0.3:
            return 'low'
        elif drift_score < 0.5:
            return 'medium'
        else:
            return 'high'

class ABLayoutManager:
    """A/B testing layout management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.active_tests = {}
        self.test_results = []
        
    def create_canary_deployment(self, model_name: str, new_model: Any, 
                               new_version: str, canary_percentage: float = 0.1) -> Dict[str, Any]:
        """Canary deployment yaratish"""
        deployment_config = {
            'model_name': model_name,
            'new_model': new_model,
            'new_version': new_version,
            'canary_percentage': canary_percentage,
            'start_time': datetime.now(),
            'status': 'canary_active',
            'metrics': {
                'canary_requests': 0,
                'control_requests': 0,
                'canary_errors': 0,
                'control_errors': 0
            }
        }
        
        test_id = f"{model_name}_{new_version}_{int(time.time())}"
        self.active_tests[test_id] = deployment_config
        
        self.logger.info(f"Created canary deployment for {model_name} with {canary_percentage*100}% traffic")
        return {'test_id': test_id, 'config': deployment_config}
    
    def route_request(self, test_id: str, user_id: str) -> str:
        """Traffic routing (control yoki canary)"""
        if test_id not in self.active_tests:
            return 'control'
        
        # Simple hash-based routing
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        canary_percentage = self.active_tests[test_id]['canary_percentage']
        
        # Convert percentage to fraction
        if hash_value % 100 < canary_percentage * 100:
            return 'canary'
        return 'control'
    
    def record_test_metrics(self, test_id: str, route: str, success: bool, 
                          response_time: float, prediction: float, actual: Optional[float] = None):
        """Test metrikalari qayd etish"""
        if test_id not in self.active_tests:
            return
        
        metrics = self.active_tests[test_id]['metrics']
        
        if route == 'canary':
            metrics['canary_requests'] += 1
            if not success:
                metrics['canary_errors'] += 1
        else:
            metrics['control_requests'] += 1
            if not success:
                metrics['control_errors'] += 1
        
        # Store performance metrics
        if 'performance_data' not in self.active_tests[test_id]:
            self.active_tests[test_id]['performance_data'] = []
        
        self.active_tests[test_id]['performance_data'].append({
            'route': route,
            'success': success,
            'response_time': response_time,
            'prediction': prediction,
            'actual': actual,
            'timestamp': datetime.now()
        })
    
    def evaluate_canary(self, test_id: str, evaluation_duration: int = 60) -> Dict[str, Any]:
        """Canary test natijalarini baholash"""
        if test_id not in self.active_tests:
            return {'error': 'Test not found'}
        
        test_data = self.active_tests[test_id]
        metrics = test_data['metrics']
        
        # Calculate success rates
        canary_success_rate = (metrics['canary_requests'] - metrics['canary_errors']) / max(metrics['canary_requests'], 1)
        control_success_rate = (metrics['control_requests'] - metrics['control_errors']) / max(metrics['control_requests'], 1)
        
        # Performance comparison
        performance_data = test_data.get('performance_data', [])
        canary_performance = [d for d in performance_data if d['route'] == 'canary' and d['success']]
        control_performance = [d for d in performance_data if d['route'] == 'control' and d['success']]
        
        # Simple evaluation criteria
        canary_acceptable = (
            canary_success_rate >= 0.95 and  # 95% success rate
            canary_success_rate >= control_success_rate - 0.02  # No more than 2% worse than control
        )
        
        evaluation_result = {
            'test_id': test_id,
            'evaluation_time': datetime.now(),
            'duration_minutes': (datetime.now() - test_data['start_time']).total_seconds() / 60,
            'metrics': {
                'canary_success_rate': canary_success_rate,
                'control_success_rate': control_success_rate,
                'canary_requests': metrics['canary_requests'],
                'control_requests': metrics['control_requests'],
                'canary_errors': metrics['canary_errors'],
                'control_errors': metrics['control_errors']
            },
            'decision': 'promote' if canary_acceptable else 'rollback',
            'confidence': abs(canary_success_rate - control_success_rate) * 10  # Simple confidence measure
        }
        
        # Update test status
        if evaluation_result['decision'] == 'promote':
            test_data['status'] = 'promoted'
        else:
            test_data['status'] = 'rollback'
        
        self.test_results.append(evaluation_result)
        
        self.logger.info(f"Canary evaluation for {test_id}: {evaluation_result['decision']}")
        return evaluation_result

class NotificationManager:
    """Bildirishnomalar boshqaruvchi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.email_config = config.get('email', {})
        self.slack_config = config.get('slack', {})
        
    def send_alert(self, alert_type: str, message: str, severity: str = 'medium', 
                  recipients: List[str] = None):
        """Ogohlantirish yuborish"""
        if severity == 'high':
            self._send_email_alert(alert_type, message, recipients)
            self._send_slack_alert(alert_type, message, severity)
        elif severity == 'medium':
            self._send_email_alert(alert_type, message, recipients)
        else:
            self._log_alert(alert_type, message)
        
        self.logger.info(f"Alert sent - Type: {alert_type}, Severity: {severity}")
    
    def _send_email_alert(self, alert_type: str, message: str, recipients: List[str] = None):
        """Email orqali ogohlantirish"""
        if not recipients:
            recipients = self.email_config.get('recipients', [])
        
        if not recipients:
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.email_config.get('from_email', 'noreply@system.com')
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"[{alert_type.upper()}] Model Update Alert"
            
            body = f"""
Model Update System Alert
            
Alert Type: {alert_type}
Severity: Medium
Timestamp: {datetime.now().isoformat()}

Message:
{message}

This is an automated alert from the Model Update System.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email (requires proper SMTP configuration)
            server = smtplib.SMTP(self.email_config.get('smtp_server', 'localhost'), 
                                self.email_config.get('smtp_port', 587))
            server.starttls()
            server.login(self.email_config.get('username', ''), 
                        self.email_config.get('password', ''))
            
            text = msg.as_string()
            server.sendmail(msg['From'], recipients, text)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def _send_slack_alert(self, alert_type: str, message: str, severity: str):
        """Slack orqali ogohlantirish"""
        # Mock Slack integration
        self.logger.info(f"SLACK ALERT: [{severity.upper()}] {alert_type}: {message}")
    
    def _log_alert(self, alert_type: str, message: str):
        """Faqat log orqali ogohlantirish"""
        self.logger.info(f"ALERT LOG: {alert_type}: {message}")

class ModelUpdater:
    """Asosiy model yangilovchi"""
    
    def __init__(self, config_path: str = "config/model_updater_config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize components
        self.version_manager = ModelVersionManager(self.config.get('model_path', 'models'))
        self.performance_monitor = PerformanceMonitor(self.config)
        self.drift_detector = DriftDetector(self.config)
        self.ab_layout_manager = ABLayoutManager(self.config)
        self.notification_manager = NotificationManager(self.config)
        
        # State tracking
        self.update_queue = []
        self.active_updates = {}
        self.rollback_history = []
        
        self.logger.info("Model Updater initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Konfiguratsiyani yuklash"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "model_path": "models",
                "update_thresholds": {
                    "performance_degradation": 0.05,
                    "drift_threshold": 0.3,
                    "latency_increase": 0.2
                },
                "canary": {
                    "percentage": 0.1,
                    "duration_minutes": 60,
                    "success_threshold": 0.95
                },
                "monitoring": {
                    "check_interval_minutes": 15,
                    "alert_cooldown_hours": 1
                },
                "email": {
                    "smtp_server": "localhost",
                    "smtp_port": 587,
                    "recipients": ["admin@example.com"]
                }
            }
    
    def _setup_logging(self) -> logging.Logger:
        """Logging sozlamalari"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def check_and_update_models(self) -> List[ModelUpdateEvent]:
        """Modellarni tekshirish va yangilash zarurligini aniqlash"""
        self.logger.info("Starting model health check")
        
        update_events = []
        
        # Simulate model checking
        models_to_check = [
            {"name": "fraud_detection", "current_performance": 0.92, "baseline_performance": 0.95},
            {"name": "price_prediction", "current_performance": 0.87, "baseline_performance": 0.90},
            {"name": "customer_churn", "current_performance": 0.78, "baseline_performance": 0.80}
        ]
        
        for model_info in models_to_check:
            model_name = model_info["name"]
            current_perf = model_info["current_performance"]
            baseline_perf = model_info["baseline_performance"]
            
            # Check performance degradation
            performance_threshold = self.config['update_thresholds']['performance_degradation']
            if current_perf < baseline_perf * (1 - performance_threshold):
                event = await self._trigger_model_update(
                    model_name, 'performance_degradation', {
                        'current': current_perf,
                        'baseline': baseline_perf,
                        'degradation': (baseline_perf - current_perf) / baseline_perf
                    }
                )
                update_events.append(event)
            
            # Check for data drift
            drift_score = self._simulate_drift_check(model_name)
            drift_threshold = self.config['update_thresholds']['drift_threshold']
            if drift_score > drift_threshold:
                event = await self._trigger_model_update(
                    model_name, 'data_drift', {
                        'drift_score': drift_score,
                        'threshold': drift_threshold
                    }
                )
                update_events.append(event)
        
        self.logger.info(f"Model health check completed. {len(update_events)} update events triggered")
        return update_events
    
    def _simulate_drift_check(self, model_name: str) -> float:
        """Data drift simulyatsiya"""
        # Mock drift score based on model name
        import random
        base_drift = random.uniform(0.1, 0.4)
        return base_drift
    
    async def _trigger_model_update(self, model_name: str, update_reason: str, 
                                  context: Dict[str, Any]) -> ModelUpdateEvent:
        """Model yangilashni boshlash"""
        self.logger.info(f"Triggering model update for {model_name}: {update_reason}")
        
        # Create update event
        current_version = self._get_current_version(model_name)
        new_version = self._generate_new_version()
        
        event = ModelUpdateEvent(
            event_type=update_reason,
            model_name=model_name,
            current_version=current_version,
            new_version=new_version,
            trigger_reason=json.dumps(context),
            confidence_score=self._calculate_trigger_confidence(context),
            timestamp=datetime.now(),
            status='pending'
        )
        
        # Queue the update
        self.update_queue.append(event)
        
        # Start processing if not already running
        if len(self.active_updates) == 0:
            asyncio.create_task(self._process_update_queue())
        
        return event
    
    def _get_current_version(self, model_name: str) -> str:
        """Joriy versiyani olish"""
        if model_name in self.version_manager.version_registry['models']:
            return self.version_manager.version_registry['models'][model_name]['current_version']
        return 'v_initial'
    
    def _generate_new_version(self) -> str:
        """Yangi versiya yaratish"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"v_{timestamp}"
    
    def _calculate_trigger_confidence(self, context: Dict[str, Any]) -> float:
        """Trigger confidence hisoblash"""
        if 'degradation' in context:
            return min(context['degradation'] * 10, 1.0)  # Scale degradation
        elif 'drift_score' in context:
            return min(context['drift_score'] * 2, 1.0)  # Scale drift
        return 0.5
    
    async def _process_update_queue(self):
        """Update navbatini qayta ishlash"""
        self.logger.info("Starting update queue processing")
        
        while self.update_queue:
            event = self.update_queue.pop(0)
            self.active_updates[event.model_name] = event
            
            try:
                result = await self._process_single_update(event)
                event.status = 'completed'
                self.logger.info(f"Update completed for {event.model_name}: {result}")
                
            except Exception as e:
                event.status = 'failed'
                self.logger.error(f"Update failed for {event.model_name}: {e}")
                
                # Trigger rollback if needed
                if event.status == 'failed':
                    await self._trigger_rollback(event)
            
            # Remove from active updates
            if event.model_name in self.active_updates:
                del self.active_updates[event.model_name]
    
    async def _process_single_update(self, event: ModelUpdateEvent) -> Dict[str, Any]:
        """Bitta yangilashni qayta ishlash"""
        self.logger.info(f"Processing update for {event.model_name}")
        
        # Simulate model retraining
        self.logger.info("Starting model retraining...")
        await asyncio.sleep(2)  # Simulate training time
        
        # Create new model (mock)
        from sklearn.ensemble import RandomForestRegressor
        new_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Save new model version
        metadata = {
            'event_type': event.event_type,
            'trigger_context': event.trigger_reason,
            'confidence_score': event.confidence_score
        }
        
        new_version = self.version_manager.create_model_version(
            new_model, event.model_name, metadata
        )
        
        # Setup canary deployment
        canary_config = self.config.get('canary', {})
        deployment_result = self._setup_canary_deployment(
            event.model_name, new_model, new_version, canary_config
        )
        
        # Monitor canary
        canary_result = await self._monitor_canary_deployment(
            deployment_result['test_id'], canary_config.get('duration_minutes', 60)
        )
        
        return {
            'new_version': new_version,
            'canary_test_id': deployment_result['test_id'],
            'canary_result': canary_result,
            'update_successful': canary_result['decision'] == 'promote'
        }
    
    def _setup_canary_deployment(self, model_name: str, new_model: Any, 
                               new_version: str, canary_config: Dict[str, Any]) -> Dict[str, Any]:
        """Canary deployment o'rnatish"""
        canary_percentage = canary_config.get('percentage', 0.1)
        
        return self.ab_layout_manager.create_canary_deployment(
            model_name, new_model, new_version, canary_percentage
        )
    
    async def _monitor_canary_deployment(self, test_id: str, duration_minutes: int) -> Dict[str, Any]:
        """Canary deployment monitoring"""
        self.logger.info(f"Monitoring canary deployment for {duration_minutes} minutes")
        
        # Simulate monitoring period
        await asyncio.sleep(2)  # Shortened for demo
        
        # Evaluate canary
        result = self.ab_layout_manager.evaluate_canary(test_id, duration_minutes)
        
        return result
    
    async def _trigger_rollback(self, event: ModelUpdateEvent):
        """Rollback trigger"""
        self.logger.info(f"Triggering rollback for {event.model_name}")
        
        # Rollback to previous version
        rollback_success = self.version_manager.rollback_to_version(
            event.model_name, event.current_version
        )
        
        if rollback_success:
            self.rollback_history.append({
                'model_name': event.model_name,
                'failed_version': event.new_version,
                'rolled_back_to': event.current_version,
                'timestamp': datetime.now(),
                'reason': event.event_type
            })
            
            # Send notification
            self.notification_manager.send_alert(
                'model_rollback',
                f"Model {event.model_name} rolled back to {event.current_version} due to {event.event_type}",
                'high'
            )
        else:
            self.logger.error(f"Rollback failed for {event.model_name}")
    
    def setup_monitoring_schedule(self):
        """Monitoring jadvalini o'rnatish"""
        check_interval = self.config.get('monitoring', {}).get('check_interval_minutes', 15)
        
        # Schedule periodic checks
        schedule.every(check_interval).minutes.do(lambda: asyncio.create_task(self.check_and_update_models()))
        
        self.logger.info(f"Monitoring schedule setup: every {check_interval} minutes")
    
    def start_monitoring(self):
        """Monitoring ishga tushirish"""
        self.logger.info("Starting model monitoring system")
        
        # Setup schedule
        self.setup_monitoring_schedule()
        
        # Start scheduler in background
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        self.logger.info("Model monitoring system started")
    
    async def force_model_update(self, model_name: str, reason: str = "manual") -> ModelUpdateEvent:
        """Majburiy model yangilash"""
        self.logger.info(f"Force update requested for {model_name}: {reason}")
        
        return await self._trigger_model_update(model_name, 'manual_trigger', {
            'reason': reason,
            'forced': True
        })
    
    def get_system_status(self) -> Dict[str, Any]:
        """Tizim holatini olish"""
        return {
            'timestamp': datetime.now().isoformat(),
            'update_queue_size': len(self.update_queue),
            'active_updates': len(self.active_updates),
            'total_models': len(self.version_manager.version_registry['models']),
            'rollback_count': len(self.rollback_history),
            'canary_tests': len(self.ab_layout_manager.active_tests),
            'monitoring_active': True
        }

# Main execution
if __name__ == "__main__":
    async def main():
        """Test va demo"""
        print("Model Updater System Demo")
        print("=" * 40)
        
        # Initialize updater
        updater = ModelUpdater()
        
        # System status
        status = updater.get_system_status()
        print(f"System Status: {json.dumps(status, indent=2)}")
        
        # Check and update models
        print("\nRunning model health check...")
        update_events = await updater.check_and_update_models()
        
        if update_events:
            print(f"Found {len(update_events)} models that need updates:")
            for event in update_events:
                print(f"  - {event.model_name}: {event.event_type} (confidence: {event.confidence_score:.2f})")
        else:
            print("All models are healthy!")
        
        # Force update example
        print("\nForcing update on one model...")
        force_event = await updater.force_model_update("fraud_detection", "manual_test")
        print(f"Force update triggered: {force_event.model_name} v{force_event.new_version}")
        
        # Show system status after updates
        print(f"\nFinal System Status: {json.dumps(updater.get_system_status(), indent=2)}")
    
    # Run the demo
    asyncio.run(main())