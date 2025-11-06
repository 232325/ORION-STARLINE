"""
Concept Drift Detection - Ma'lumotlar taqsimotidagi o'zgarishlarni aniqlash
Real-time drift detection, online algorithms, va adaptation mechanisms
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import warnings
from abc import ABC, abstractmethod
from collections import deque, defaultdict
from scipy import stats
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

@dataclass
class DriftConfig:
    """Drift detection konfiguratsiyasi"""
    # Window sizes
    reference_window_size: int = 1000
    detection_window_size: int = 100
    buffer_size: int = 5000
    
    # Statistical tests
    significance_level: float = 0.05
    test_method: str = 'ks'  # 'ks', 'chi2', 'ad', 'ks_multi'
    
    # Performance-based detection
    performance_threshold: float = 0.05
    performance_window_size: int = 50
    min_samples_for_drift: int = 30
    
    # Adaptive thresholds
    adaptive_threshold: bool = True
    threshold_decay: float = 0.99
    threshold_min: float = 0.01
    threshold_max: float = 0.5
    
    # Detection algorithms
    enable_ks_test: bool = True
    enable_page_hinkley: bool = True
    enable_ddm: bool = True
    enable_eddm: bool = True
    enable_adwin: bool = True
    
    # Online algorithms
    online_learning_rate: float = 0.01
    forgetting_factor: float = 0.9
    
    # Alerting
    alert_callbacks: List[Callable] = field(default_factory=list)
    alert_cooldown: int = 100  # Samples

@dataclass
class DriftEvent:
    """Drift event ma'lumotlari"""
    timestamp: datetime
    drift_type: str  # 'sudden', 'gradual', 'recurring'
    detection_method: str
    drift_strength: float
    affected_features: List[str]
    performance_impact: float
    alert_message: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class StatisticalDriftDetector:
    """Statistical test based drift detection"""
    
    def __init__(self, config: DriftConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.StatisticalDrift")
        
        # Data storage
        self.reference_data = deque(maxlen=config.reference_window_size)
        self.current_data = deque(maxlen=config.detection_window_size)
        
        # Detection history
        self.drift_history = []
        self.statistical_scores = deque(maxlen=100)
        
        # Adaptive threshold
        self.current_threshold = config.performance_threshold
        
    def update(self, new_sample: np.ndarray, metadata: Dict[str, Any] = None) -> bool:
        """Update detector with new sample"""
        self.current_data.append(new_sample)
        
        # Store in reference if we have space
        if len(self.reference_data) < self.config.reference_window_size:
            self.reference_data.append(new_sample)
            return False
        
        # Check for drift
        if len(self.current_data) >= self.config.detection_window_size:
            drift_detected = self._detect_statistical_drift(metadata)
            
            if drift_detected:
                # Create drift event
                drift_event = DriftEvent(
                    timestamp=datetime.now(),
                    drift_type=self._classify_drift_type(),
                    detection_method='statistical',
                    drift_strength=self._calculate_drift_strength(),
                    affected_features=self._get_affected_features(),
                    performance_impact=0.0,  # Will be updated by performance detector
                    alert_message=f"Statistical drift detected using {self.config.test_method} test"
                )
                
                self.drift_history.append(drift_event)
                self._trigger_alert(drift_event)
                
                # Reset current window
                self.current_data.clear()
            
            return drift_detected
        
        return False
    
    def _detect_statistical_drift(self, metadata: Dict[str, Any] = None) -> bool:
        """Detect drift using statistical tests"""
        if len(self.reference_data) < self.config.min_samples_for_drift:
            return False
        
        # Convert deques to arrays
        reference_array = np.array(list(self.reference_data))
        current_array = np.array(list(self.current_data))
        
        drift_detected = False
        
        if self.config.test_method == 'ks' and self.config.enable_ks_test:
            drift_detected = self._kolmogorov_smirnov_test(reference_array, current_array)
        elif self.config.test_method == 'chi2' and self.config.enable_ks_test:
            drift_detected = self._chi_square_test(reference_array, current_array)
        elif self.config.test_method == 'ad' and self.config.enable_ks_test:
            drift_detected = self._anderson_darling_test(reference_array, current_array)
        elif self.config.test_method == 'ks_multi':
            drift_detected = self._multivariate_ks_test(reference_array, current_array)
        
        # Calculate and store statistical score
        score = self._calculate_statistical_score(reference_array, current_array)
        self.statistical_scores.append(score)
        
        return drift_detected
    
    def _kolmogorov_smirnov_test(self, ref_data: np.ndarray, curr_data: np.ndarray) -> bool:
        """Kolmogorov-Smirnov test for drift detection"""
        try:
            if ref_data.ndim > 1:
                # For multivariate data, test each feature
                p_values = []
                for i in range(ref_data.shape[1]):
                    statistic, p_value = stats.ks_2samp(ref_data[:, i], curr_data[:, i])
                    p_values.append(p_value)
                
                # Use Bonferroni correction
                corrected_p = min(p_values) * len(p_values)
                drift_detected = corrected_p < self.config.significance_level
            else:
                statistic, p_value = stats.ks_2samp(ref_data, curr_data)
                drift_detected = p_value < self.config.significance_level
            
            return drift_detected
            
        except Exception as e:
            self.logger.warning(f"KS test failed: {e}")
            return False
    
    def _chi_square_test(self, ref_data: np.ndarray, curr_data: np.ndarray) -> bool:
        """Chi-square test for drift detection"""
        try:
            # Discretize continuous data
            ref_binned = np.digitize(ref_data.flatten(), bins=20)
            curr_binned = np.digitize(curr_data.flatten(), bins=20)
            
            # Create contingency table
            all_values = np.concatenate([ref_binned, curr_binned])
            unique_values = np.unique(all_values)
            
            ref_counts = np.array([np.sum(ref_binned == val) for val in unique_values])
            curr_counts = np.array([np.sum(curr_binned == val) for val in unique_values])
            
            # Chi-square test
            chi2_stat, p_value = stats.chisquare(np.column_stack([ref_counts, curr_counts]))
            
            drift_detected = p_value < self.config.significance_level
            return drift_detected
            
        except Exception as e:
            self.logger.warning(f"Chi-square test failed: {e}")
            return False
    
    def _anderson_darling_test(self, ref_data: np.ndarray, curr_data: np.ndarray) -> bool:
        """Anderson-Darling test for drift detection"""
        try:
            # Normalize data
            ref_normalized = (ref_data - np.mean(ref_data)) / (np.std(ref_data) + 1e-8)
            curr_normalized = (curr_data - np.mean(curr_data)) / (np.std(curr_data) + 1e-8)
            
            # Anderson-Darling statistic (simplified)
            combined_data = np.concatenate([ref_normalized, curr_normalized])
            sorted_data = np.sort(combined_data)
            
            ref_size = len(ref_normalized)
            curr_size = len(curr_normalized)
            
            # Calculate AD statistic
            ad_stat = 0
            for i in range(len(sorted_data)):
                F_ref = np.sum(ref_normalized <= sorted_data[i]) / ref_size
                F_curr = np.sum(curr_normalized <= sorted_data[i]) / curr_size
                
                # Simplified AD calculation
                if F_ref > 0 and F_ref < 1 and F_curr > 0 and F_curr < 1:
                    ad_stat += (2 * i + 1) * (np.log(F_ref) + np.log(1 - F_curr))
            
            # Critical values (simplified)
            critical_value = 2.492  # For 5% significance level
            drift_detected = ad_stat > critical_value
            
            return drift_detected
            
        except Exception as e:
            self.logger.warning(f"Anderson-Darling test failed: {e}")
            return False
    
    def _multivariate_ks_test(self, ref_data: np.ndarray, curr_data: np.ndarray) -> bool:
        """Multivariate KS test using maximum mean discrepancy"""
        try:
            # Calculate means and covariances
            ref_mean = np.mean(ref_data, axis=0)
            curr_mean = np.mean(curr_data, axis=0)
            
            ref_cov = np.cov(ref_data.T)
            curr_cov = np.cov(curr_data.T)
            
            # Mean difference
            mean_diff = np.linalg.norm(ref_mean - curr_mean)
            
            # Covariance difference (simplified)
            cov_diff = np.linalg.norm(ref_cov - curr_cov)
            
            # Combined statistic
            statistic = mean_diff + 0.5 * cov_diff
            
            # Store score
            self.last_statistic = statistic
            
            # Compare with adaptive threshold
            threshold = self._get_adaptive_threshold()
            drift_detected = statistic > threshold
            
            return drift_detected
            
        except Exception as e:
            self.logger.warning(f"Multivariate KS test failed: {e}")
            return False
    
    def _calculate_statistical_score(self, ref_data: np.ndarray, curr_data: np.ndarray) -> float:
        """Calculate overall statistical score"""
        try:
            # Distance between means
            mean_distance = np.linalg.norm(np.mean(ref_data, axis=0) - np.mean(curr_data, axis=0))
            
            # Distance between variances
            ref_var = np.var(ref_data, axis=0)
            curr_var = np.var(curr_data, axis=0)
            var_distance = np.linalg.norm(ref_var - curr_var)
            
            # Combined score
            score = mean_distance + 0.5 * var_distance
            return score
            
        except Exception as e:
            self.logger.warning(f"Statistical score calculation failed: {e}")
            return 0.0
    
    def _classify_drift_type(self) -> str:
        """Classify the type of drift"""
        if len(self.statistical_scores) < 10:
            return 'unknown'
        
        recent_scores = list(self.statistical_scores)[-10:]
        
        # Check for sudden drift
        if len(recent_scores) >= 2:
            score_diff = recent_scores[-1] - recent_scores[-2]
            if score_diff > 0.1:  # Threshold for sudden change
                return 'sudden'
        
        # Check for gradual drift
        if len(recent_scores) >= 5:
            trend = np.polyfit(range(5), recent_scores[-5:], 1)[0]
            if trend > 0.01:  # Positive trend indicates gradual increase
                return 'gradual'
        
        return 'recurring'
    
    def _calculate_drift_strength(self) -> float:
        """Calculate strength of drift"""
        if not self.statistical_scores:
            return 0.0
        
        current_score = self.statistical_scores[-1]
        baseline_score = np.mean(list(self.statistical_scores)[:-1]) if len(self.statistical_scores) > 1 else 0
        
        if baseline_score > 0:
            strength = (current_score - baseline_score) / baseline_score
            return max(0, min(1, strength))  # Normalize to [0, 1]
        
        return 0.0
    
    def _get_affected_features(self) -> List[str]:
        """Get list of features affected by drift"""
        # Simplified: return empty list (would need feature-level analysis)
        return []
    
    def _get_adaptive_threshold(self) -> float:
        """Get adaptive threshold"""
        if not self.config.adaptive_threshold:
            return self.config.performance_threshold
        
        # Decay threshold over time
        self.current_threshold *= self.config.threshold_decay
        self.current_threshold = np.clip(
            self.current_threshold, 
            self.config.threshold_min, 
            self.config.threshold_max
        )
        
        return self.current_threshold
    
    def _trigger_alert(self, drift_event: DriftEvent) -> None:
        """Trigger alert callbacks"""
        for callback in self.config.alert_callbacks:
            try:
                callback(drift_event)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")

class PerformanceBasedDriftDetector:
    """Drift detection based on model performance degradation"""
    
    def __init__(self, config: DriftConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.PerformanceDrift")
        
        # Performance tracking
        self.performance_history = deque(maxlen=config.performance_window_size)
        self.baseline_performance = None
        self.drift_history = []
        
        # Model state
        self.current_model = None
        self.reference_model = None
        
        # Alert cooldown
        self.last_alert_time = 0
        
    def set_models(self, current_model: BaseEstimator, reference_model: BaseEstimator = None) -> None:
        """Set current and reference models"""
        self.current_model = current_model
        self.reference_model = reference_model or current_model
        
        if self.baseline_performance is None:
            self.logger.info("Baseline performance established")
    
    def update_performance(self, predictions: np.ndarray, true_labels: np.ndarray) -> bool:
        """Update performance tracking and check for drift"""
        # Calculate performance
        if len(np.unique(true_labels)) <= 2:  # Classification
            accuracy = accuracy_score(true_labels, predictions)
        else:  # Regression
            accuracy = 1 / (1 + mean_squared_error(true_labels, predictions))  # Convert to 0-1 scale
        
        self.performance_history.append(accuracy)
        
        # Check for drift
        if len(self.performance_history) >= self.config.performance_window_size:
            drift_detected = self._detect_performance_drift()
            
            if drift_detected and (len(self.performance_history) - self.last_alert_time) > self.config.alert_cooldown:
                # Create drift event
                current_acc = np.mean(list(self.performance_history)[-10:])
                baseline_acc = self.baseline_performance or current_acc
                
                drift_event = DriftEvent(
                    timestamp=datetime.now(),
                    drift_type='performance_degradation',
                    detection_method='performance',
                    drift_strength=(baseline_acc - current_acc) / baseline_acc if baseline_acc > 0 else 0,
                    affected_features=['performance'],
                    performance_impact=baseline_acc - current_acc,
                    alert_message=f"Performance degradation detected: {current_acc:.3f} vs {baseline_acc:.3f}"
                )
                
                self.drift_history.append(drift_event)
                self._trigger_alert(drift_event)
                self.last_alert_time = len(self.performance_history)
                
                return True
        
        return False
    
    def _detect_performance_drift(self) -> bool:
        """Detect drift based on performance degradation"""
        if len(self.performance_history) < self.config.performance_window_size:
            return False
        
        # Set baseline if not established
        if self.baseline_performance is None:
            self.baseline_performance = np.mean(list(self.performance_history)[:self.config.performance_window_size//2])
            return False
        
        # Calculate recent performance
        recent_performance = np.mean(list(self.performance_history)[-10:])
        performance_drop = self.baseline_performance - recent_performance
        
        # Check against threshold
        threshold = self.config.performance_threshold
        drift_detected = performance_drop > threshold
        
        if drift_detected:
            self.logger.warning(f"Performance drift detected: drop = {performance_drop:.4f}, threshold = {threshold}")
        
        return drift_detected
    
    def _trigger_alert(self, drift_event: DriftEvent) -> None:
        """Trigger alert callbacks"""
        for callback in self.config.alert_callbacks:
            try:
                callback(drift_event)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")

class OnlineDriftDetector:
    """Online drift detection algorithms"""
    
    def __init__(self, config: DriftConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.OnlineDrift")
        
        # Page-Hinkley detector
        self.page_hinkley = PageHinkleyDetector(config)
        
        # DDM (Drift Detection Method)
        self.ddm = DDMDetector(config)
        
        # EDDM (Early Drift Detection Method)
        self.eddm = EDDMDetector(config)
        
        # ADWIN (Adaptive Windowing)
        self.adwin = ADWINDetector(config)
        
        # Drift history
        self.drift_history = []
        
    def update(self, prediction: Union[int, float], true_value: Union[int, float]) -> List[DriftEvent]:
        """Update all online detectors"""
        detected_drifts = []
        
        # Update Page-Hinkley
        if self.config.enable_page_hinkley:
            ph_drift = self.page_hinkley.update(prediction, true_value)
            if ph_drift:
                drift_event = DriftEvent(
                    timestamp=datetime.now(),
                    drift_type='sudden',
                    detection_method='page_hinkley',
                    drift_strength=1.0,
                    affected_features=['prediction'],
                    performance_impact=0.0,
                    alert_message="Page-Hinkley detected sudden drift"
                )
                detected_drifts.append(drift_event)
        
        # Update DDM
        if self.config.enable_ddm:
            ddm_drift = self.ddm.update(prediction, true_value)
            if ddm_drift:
                drift_event = DriftEvent(
                    timestamp=datetime.now(),
                    drift_type='sudden',
                    detection_method='ddm',
                    drift_strength=1.0,
                    affected_features=['prediction'],
                    performance_impact=0.0,
                    alert_message="DDM detected drift"
                )
                detected_drifts.append(drift_event)
        
        # Update EDDM
        if self.config.enable_eddm:
            eddm_drift = self.eddm.update(prediction, true_value)
            if eddm_drift:
                drift_event = DriftEvent(
                    timestamp=datetime.now(),
                    drift_type='gradual',
                    detection_method='eddm',
                    drift_strength=0.8,
                    affected_features=['prediction'],
                    performance_impact=0.0,
                    alert_message="EDDM detected gradual drift"
                )
                detected_drifts.append(drift_event)
        
        # Update ADWIN
        if self.config.enable_adwin:
            adwin_drift = self.adwin.update(prediction, true_value)
            if adwin_drift:
                drift_event = DriftEvent(
                    timestamp=datetime.now(),
                    drift_type='gradual',
                    detection_method='adwin',
                    drift_strength=0.9,
                    affected_features=['prediction'],
                    performance_impact=0.0,
                    alert_message="ADWIN detected drift"
                )
                detected_drifts.append(drift_event)
        
        # Store in history
        self.drift_history.extend(detected_drifts)
        
        # Trigger alerts
        for drift_event in detected_drifts:
            self._trigger_alert(drift_event)
        
        return detected_drifts
    
    def _trigger_alert(self, drift_event: DriftEvent) -> None:
        """Trigger alert callbacks"""
        for callback in self.config.alert_callbacks:
            try:
                callback(drift_event)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")

class PageHinkleyDetector:
    """Page-Hinkley test for drift detection"""
    
    def __init__(self, config: DriftConfig):
        self.config = config
        self.reset()
    
    def reset(self):
        """Reset detector state"""
        self.sum_ = 0
        self.min_sum = 0
        self.num_instances = 0
    
    def update(self, prediction: Union[int, float], true_value: Union[int, float]) -> bool:
        """Update Page-Hinkley detector"""
        error = 1.0 if prediction != true_value else 0.0
        
        self.sum_ += error - 0.5  # Center at 0
        self.min_sum = min(self.min_sum, self.sum_)
        self.num_instances += 1
        
        # Check for drift
        threshold = 50.0  # Can be made adaptive
        drift_detected = (self.sum_ - self.min_sum) > threshold
        
        if drift_detected:
            self.reset()  # Reset after detection
        
        return drift_detected

class DDMDetector:
    """Drift Detection Method"""
    
    def __init__(self, config: DriftConfig):
        self.config = config
        self.reset()
    
    def reset(self):
        """Reset detector state"""
        self.num_instances = 0
        self.error_count = 0
        self.num_errors = 0
        self.min_num_errors = float('inf')
        self.min_float = float('inf')
    
    def update(self, prediction: Union[int, float], true_value: Union[int, float]) -> bool:
        """Update DDM detector"""
        error = 1.0 if prediction != true_value else 0.0
        self.num_instances += 1
        self.num_errors += error
        
        if self.num_instances > 30:  # Minimum samples
            error_rate = self.num_errors / self.num_instances
            float_ = (2.0 * (np.log(np.log(self.num_instances)) / self.num_instances)) ** 0.5
            
            # Check warning level
            warning_threshold = error_rate + float_
            if warning_threshold < self.min_float:
                self.min_float = warning_threshold
                self.min_num_errors = self.num_errors
            
            # Check drift level
            drift_threshold = error_rate + 2.0 * float_
            drift_detected = drift_threshold < self.min_float
            
            if drift_detected:
                self.reset()
            
            return drift_detected
        
        return False

class EDDMDetector:
    """Early Drift Detection Method"""
    
    def __init__(self, config: DriftConfig):
        self.config = config
        self.reset()
    
    def reset(self):
        """Reset detector state"""
        self.errors = []
        self.mean_error = 0
        self.std_error = 0
        self.last_error = None
    
    def update(self, prediction: Union[int, float], true_value: Union[int, float]) -> bool:
        """Update EDDM detector"""
        error = 1.0 if prediction != true_value else 0.0
        
        if self.last_error is not None:
            self.errors.append(abs(error - self.last_error))
            self.last_error = error
            
            if len(self.errors) > 30:  # Minimum samples
                self.mean_error = np.mean(self.errors)
                self.std_error = np.std(self.errors)
                
                if len(self.errors) > 300:
                    # Remove old errors
                    self.errors = self.errors[-200:]
                
                # Check for drift
                warning_threshold = (self.mean_error + 2 * self.std_error) / 1.308  # Normalized
                drift_threshold = (self.mean_error + 3 * self.std_error) / 1.308
                
                # This is a simplified version - would need proper implementation
                drift_detected = self.mean_error > drift_threshold
                
                return drift_detected
        else:
            self.last_error = error
        
        return False

class ADWINDetector:
    """ADaptive WINdowing detector"""
    
    def __init__(self, config: DriftConfig):
        self.config = config
        self.reset()
    
    def reset(self):
        """Reset detector state"""
        self.window = []
        self.last_cut = 0
        self.n = 0
    
    def update(self, prediction: Union[int, float], true_value: Union[int, float]) -> bool:
        """Update ADWIN detector"""
        error = 1.0 if prediction != true_value else 0.0
        self.window.append(error)
        self.n += 1
        
        if len(self.window) > 30:  # Minimum samples
            # Find cut point
            for i in range(len(self.window) - 1):
                left_window = self.window[:i+1]
                right_window = self.window[i+1:]
                
                if len(left_window) > 5 and len(right_window) > 5:
                    left_mean = np.mean(left_window)
                    right_mean = np.mean(right_window)
                    
                    # ADWIN criterion
                    n_left = len(left_window)
                    n_right = len(right_window)
                    delta = 0.002  # Confidence parameter
                    
                    bound = np.sqrt((2 * np.log(2/delta)) / n_left) + np.sqrt((2 * np.log(2/delta)) / n_right)
                    
                    if abs(left_mean - right_mean) > bound:
                        # Drift detected
                        self.window = right_window  # Keep only recent data
                        self.last_cut = i
                        return True
        
        return False

class ComprehensiveDriftDetector:
    """Comprehensive drift detection system combining multiple methods"""
    
    def __init__(self, config: DriftConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ComprehensiveDrift")
        
        # Initialize detectors
        self.statistical_detector = StatisticalDriftDetector(config)
        self.performance_detector = PerformanceBasedDriftDetector(config)
        self.online_detector = OnlineDriftDetector(config)
        
        # Combined detection
        self.drift_votes = deque(maxlen=10)
        self.consensus_threshold = 0.6  # 60% of detectors must agree
        
        # Drift events
        self.all_drift_events = []
        self.last_consensus_drift = None
    
    def set_model(self, model: BaseEstimator) -> None:
        """Set model for performance tracking"""
        self.performance_detector.set_models(model)
    
    def update(self, sample: np.ndarray, prediction: Union[int, float], 
              true_value: Union[int, float], metadata: Dict[str, Any] = None) -> List[DriftEvent]:
        """Update all detectors and return combined results"""
        
        all_drift_events = []
        votes = 0
        
        # Statistical drift detection
        if self.statistical_detector.update(sample, metadata):
            votes += 1
        
        # Performance-based drift detection
        if self.performance_detector.update_performance(
            np.array([prediction]), np.array([true_value])
        ):
            votes += 1
        
        # Online drift detection
        online_events = self.online_detector.update(prediction, true_value)
        if online_events:
            votes += 1
            all_drift_events.extend(online_events)
        
        # Record votes
        self.drift_votes.append(votes / 3.0)  # Normalize to [0, 1]
        
        # Consensus-based drift detection
        consensus_vote = np.mean(list(self.drift_votes)) if self.drift_votes else 0
        
        if (consensus_vote > self.consensus_threshold and 
            (self.last_consensus_drift is None or 
             datetime.now() - self.last_consensus_drift > timedelta(minutes=5))):
            
            consensus_event = DriftEvent(
                timestamp=datetime.now(),
                drift_type='consensus',
                detection_method='consensus',
                drift_strength=consensus_vote,
                affected_features=['all'],
                performance_impact=0.0,
                alert_message=f"Consensus drift detected: {consensus_vote:.2f} agreement"
            )
            
            all_drift_events.append(consensus_event)
            self.last_consensus_drift = datetime.now()
        
        # Store all events
        self.all_drift_events.extend(all_drift_events)
        
        return all_drift_events
    
    def get_drift_summary(self) -> Dict[str, Any]:
        """Get comprehensive drift detection summary"""
        if not self.all_drift_events:
            return {'status': 'no_drift_detected'}
        
        # Recent drift events (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_events = [e for e in self.all_drift_events if e.timestamp > cutoff_time]
        
        # Drift statistics
        drift_types = defaultdict(int)
        detection_methods = defaultdict(int)
        
        for event in recent_events:
            drift_types[event.drift_type] += 1
            detection_methods[event.detection_method] += 1
        
        # Average drift strength
        avg_drift_strength = np.mean([e.drift_strength for e in recent_events]) if recent_events else 0
        
        return {
            'status': 'drift_detected' if recent_events else 'no_recent_drift',
            'total_events': len(self.all_drift_events),
            'recent_events': len(recent_events),
            'drift_types': dict(drift_types),
            'detection_methods': dict(detection_methods),
            'avg_drift_strength': avg_drift_strength,
            'consensus_trend': np.mean(list(self.drift_votes)) if self.drift_votes else 0,
            'last_drift_time': self.all_drift_events[-1].timestamp if self.all_drift_events else None
        }
    
    def visualize_drift_history(self, save_path: Optional[str] = None) -> Dict[str, str]:
        """Create drift detection visualizations"""
        if not self.all_drift_events:
            return {}
        
        plots = {}
        
        # Drift events timeline
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Drift events over time
        plt.subplot(2, 2, 1)
        drift_times = [e.timestamp for e in self.all_drift_events]
        drift_strengths = [e.drift_strength for e in self.all_drift_events]
        
        plt.scatter(drift_times, drift_strengths, alpha=0.6)
        plt.xlabel('Time')
        plt.ylabel('Drift Strength')
        plt.title('Drift Events Over Time')
        plt.xticks(rotation=45)
        
        # Plot 2: Drift types distribution
        plt.subplot(2, 2, 2)
        drift_types = defaultdict(int)
        for event in self.all_drift_events:
            drift_types[event.drift_type] += 1
        
        plt.pie(drift_types.values(), labels=drift_types.keys(), autopct='%1.1f%%')
        plt.title('Drift Types Distribution')
        
        # Plot 3: Detection methods effectiveness
        plt.subplot(2, 2, 3)
        detection_methods = defaultdict(int)
        for event in self.all_drift_events:
            detection_methods[event.detection_method] += 1
        
        plt.bar(detection_methods.keys(), detection_methods.values())
        plt.xlabel('Detection Method')
        plt.ylabel('Detections Count')
        plt.title('Detection Methods Effectiveness')
        plt.xticks(rotation=45)
        
        # Plot 4: Consensus voting trend
        plt.subplot(2, 2, 4)
        if self.drift_votes:
            plt.plot(range(len(self.drift_votes)), list(self.drift_votes))
            plt.axhline(y=self.consensus_threshold, color='r', linestyle='--', label='Consensus Threshold')
            plt.xlabel('Time')
            plt.ylabel('Consensus Vote')
            plt.title('Consensus Drift Voting Trend')
            plt.legend()
        
        plt.tight_layout()
        
        if save_path:
            plot_path = f"{save_path}/drift_detection_plots.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plots['drift_analysis'] = plot_path
        
        plt.close()
        
        return plots

# Alert handling utilities
def create_email_alert(email_address: str) -> Callable[[DriftEvent], None]:
    """Create email alert callback"""
    def send_email_alert(drift_event: DriftEvent) -> None:
        print(f"EMAIL ALERT to {email_address}: {drift_event.alert_message}")
        # In practice, would integrate with email service
    return send_email_alert

def create_webhook_alert(webhook_url: str) -> Callable[[DriftEvent], None]:
    """Create webhook alert callback"""
    def send_webhook_alert(drift_event: DriftEvent) -> None:
        payload = {
            'event': 'drift_detected',
            'message': drift_event.alert_message,
            'timestamp': drift_event.timestamp.isoformat(),
            'drift_type': drift_event.drift_type,
            'strength': drift_event.drift_strength
        }
        print(f"WEBHOOK to {webhook_url}: {payload}")
        # In practice, would make HTTP request to webhook
    return send_webhook_alert

def create_log_alert() -> Callable[[DriftEvent], None]:
    """Create logging alert callback"""
    def log_alert(drift_event: DriftEvent) -> None:
        print(f"LOG: {drift_event.alert_message}")
    return log_alert

# Quick setup function
def setup_comprehensive_drift_detector(config: Optional[DriftConfig] = None, 
                                     alert_callbacks: List[Callable] = None) -> ComprehensiveDriftDetector:
    """Setup comprehensive drift detector with alerts"""
    
    if config is None:
        config = DriftConfig()
    
    if alert_callbacks is None:
        alert_callbacks = [create_log_alert()]
    
    config.alert_callbacks = alert_callbacks
    
    detector = ComprehensiveDriftDetector(config)
    return detector