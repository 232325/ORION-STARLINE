"""
A/B Testing Integration for Self-Learning Trading Fund
====================================================

Model va strategiya performancelarini A/B test orqali taqqoslash.
Experiments va variantlarni boshqarish.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from datetime import datetime, timedelta
import warnings
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque, defaultdict
import threading
import queue
import time
import json
import hashlib
import uuid
from scipy import stats
import matplotlib.pyplot as plt

from ..core.base_algorithm import BaseAlgorithm
from ..core.adaptive_model import AdaptiveModel
from ..core.performance_tracker import PerformanceTracker

class ExperimentType(Enum):
    """Experiment turlari"""
    MODEL_COMPARISON = "Model_Comparison"
    STRATEGY_COMPARISON = "Strategy_Comparison"
    PARAMETER_TUNING = "Parameter_Tuning"
    FEATURE_COMPARISON = "Feature_Comparison"
    THRESHOLD_OPTIMIZATION = "Threshold_Optimization"
    FEATURE_ENGINEERING = "Feature_Engineering"

class ExperimentStatus(Enum):
    """Experiment holati"""
    DRAFT = "Draft"
    RUNNING = "Running"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    STOPPED = "Stopped"
    ARCHIVED = "Archived"

class StatisticalTest(Enum):
    """Statistik testlar"""
    T_TEST = "T_Test"
    WILCOXON = "Wilcoxon"
    MANN_WHITNEY = "Mann_Whitney"
    CHI_SQUARE = "Chi_Square"
    KS_TEST = "KS_Test"
    ANOVA = "ANOVA"

@dataclass
class ExperimentVariant:
    """Experiment variant"""
    variant_id: str
    name: str
    description: str
    configuration: Dict[str, Any]
    traffic_allocation: float  # 0-1
    model: Optional[Any] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    sample_count: int = 0
    is_control: bool = False

@dataclass
class Experiment:
    """Experiment"""
    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    status: ExperimentStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    variants: Dict[str, ExperimentVariant] = field(default_factory=dict)
    primary_metric: str = "accuracy"
    confidence_level: float = 0.95
    minimum_sample_size: int = 100
    maximum_duration_days: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExperimentResult:
    """Experiment natijasi"""
    experiment_id: str
    variant_id: str
    timestamp: datetime
    metric_value: float
    sample_data: Optional[Any] = None
    additional_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class StatisticalAnalysis:
    """Statistik tahlil"""
    test_type: StatisticalTest
    p_value: float
    statistic: float
    effect_size: float
    confidence_interval: Tuple[float, float]
    significant: bool
    interpretation: str

class ABTestingManager(BaseAlgorithm):
    """A/B test boshqaruvchisi"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.config = config or {}
        
        # Experiment management
        self.experiments: Dict[str, Experiment] = {}
        self.experiment_results: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Traffic routing
        self.user_assignments: Dict[str, str] = {}
        self.traffic_splitter = TrafficSplitter()
        
        # Performance tracking
        self.performance_tracker = PerformanceTracker()
        
        # Configuration
        self.default_confidence_level = self.config.get('default_confidence_level', 0.95)
        self.minimum_sample_size = self.config.get('minimum_sample_size', 100)
        self.max_experiments_concurrent = self.config.get('max_experiments_concurrent', 5)
        
        # Threading
        self.analysis_thread = None
        self.running = False
        
    def create_experiment(self, name: str, experiment_type: ExperimentType,
                        variants: List[ExperimentVariant],
                        primary_metric: str = "accuracy",
                        **kwargs) -> str:
        """Experiment yaratish"""
        
        experiment_id = str(uuid.uuid4())
        
        # Validate variants
        total_allocation = sum(v.traffic_allocation for v in variants)
        if abs(total_allocation - 1.0) > 0.01:
            raise ValueError("Traffic allocation must sum to 1.0")
        
        # Create experiment
        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            description=kwargs.get('description', ''),
            experiment_type=experiment_type,
            status=ExperimentStatus.DRAFT,
            created_at=datetime.now(),
            primary_metric=primary_metric,
            confidence_level=kwargs.get('confidence_level', self.default_confidence_level),
            minimum_sample_size=kwargs.get('minimum_sample_size', self.minimum_sample_size),
            maximum_duration_days=kwargs.get('maximum_duration_days', 30),
            variants={v.variant_id: v for v in variants}
        )
        
        # Mark control variant
        control_variants = [v for v in variants if v.is_control]
        if len(control_variants) != 1:
            raise ValueError("Exactly one control variant required")
        
        self.experiments[experiment_id] = experiment
        
        logging.info(f"Created experiment {name} with ID {experiment_id}")
        
        return experiment_id
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Experiment ni boshlash"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        
        if experiment.status != ExperimentStatus.DRAFT:
            logging.warning(f"Experiment {experiment_id} is not in draft status")
            return False
        
        # Validate experiment
        if not self._validate_experiment(experiment):
            logging.error(f"Experiment {experiment_id} validation failed")
            return False
        
        # Start experiment
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now()
        
        # Initialize traffic routing
        self._initialize_traffic_routing(experiment)
        
        # Start analysis monitoring
        if not self.running:
            self._start_analysis_monitoring()
        
        logging.info(f"Started experiment {experiment.name} ({experiment_id})")
        
        return True
    
    def stop_experiment(self, experiment_id: str, reason: str = "manual") -> bool:
        """Experiment ni to'xtatish"""
        
        if experiment_id not in self.experiments:
            return False
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.STOPPED
        experiment.ended_at = datetime.now()
        experiment.metadata['stop_reason'] = reason
        
        logging.info(f"Stopped experiment {experiment_id}: {reason}")
        
        return True
    
    def assign_user_to_variant(self, user_id: str, experiment_id: str) -> str:
        """Foydalanuvchini variantga tayinlash"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        
        if experiment.status != ExperimentStatus.RUNNING:
            raise ValueError(f"Experiment {experiment_id} is not running")
        
        # Check if user already assigned
        assignment_key = f"{user_id}_{experiment_id}"
        if assignment_key in self.user_assignments:
            return self.user_assignments[assignment_key]
        
        # Assign variant based on traffic allocation
        variant_id = self.traffic_splitter.assign_variant(user_id, experiment)
        
        # Store assignment
        self.user_assignments[assignment_key] = variant_id
        
        return variant_id
    
    def record_result(self, experiment_id: str, variant_id: str,
                    metric_value: float, additional_metrics: Optional[Dict[str, float]] = None,
                    sample_data: Optional[Any] = None) -> bool:
        """Natijani qayd etish"""
        
        if experiment_id not in self.experiments:
            logging.error(f"Experiment {experiment_id} not found")
            return False
        
        if variant_id not in self.experiments[experiment_id].variants:
            logging.error(f"Variant {variant_id} not found in experiment {experiment_id}")
            return False
        
        # Create result
        result = ExperimentResult(
            experiment_id=experiment_id,
            variant_id=variant_id,
            timestamp=datetime.now(),
            metric_value=metric_value,
            sample_data=sample_data,
            additional_metrics=additional_metrics or {}
        )
        
        # Store result
        self.experiment_results[experiment_id].append(result)
        
        # Update variant metrics
        variant = self.experiments[experiment_id].variants[variant_id]
        variant.sample_count += 1
        
        # Update running average
        for metric_name, metric_value in result.additional_metrics.items():
            if metric_name not in variant.performance_metrics:
                variant.performance_metrics[metric_name] = 0.0
            
            # Exponential moving average
            alpha = 0.1
            variant.performance_metrics[metric_name] = (
                alpha * metric_value + (1 - alpha) * variant.performance_metrics[metric_name]
            )
        
        return True
    
    def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """Experiment holati olish"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        results = self.experiment_results[experiment_id]
        
        # Calculate statistics
        variant_stats = {}
        for variant_id, variant in experiment.variants.items():
            variant_results = [r for r in results if r.variant_id == variant_id]
            
            if variant_results:
                metric_values = [r.metric_value for r in variant_results]
                variant_stats[variant_id] = {
                    'sample_size': len(variant_results),
                    'mean': np.mean(metric_values),
                    'std': np.std(metric_values),
                    'min': np.min(metric_values),
                    'max': np.max(metric_values),
                    'median': np.median(metric_values),
                    'confidence_interval': self._calculate_confidence_interval(metric_values, experiment.confidence_level),
                    'traffic_allocation': variant.traffic_allocation
                }
            else:
                variant_stats[variant_id] = {
                    'sample_size': 0,
                    'mean': 0,
                    'std': 0,
                    'traffic_allocation': variant.traffic_allocation
                }
        
        # Check if experiment should be stopped
        should_stop = False
        stop_reason = None
        
        if experiment.status == ExperimentStatus.RUNNING:
            should_stop, stop_reason = self._should_stop_experiment(experiment, variant_stats)
        
        return {
            'experiment_id': experiment_id,
            'name': experiment.name,
            'status': experiment.status.value,
            'experiment_type': experiment.experiment_type.value,
            'created_at': experiment.created_at.isoformat(),
            'started_at': experiment.started_at.isoformat() if experiment.started_at else None,
            'duration_days': (datetime.now() - experiment.created_at).days,
            'primary_metric': experiment.primary_metric,
            'confidence_level': experiment.confidence_level,
            'should_stop': should_stop,
            'stop_reason': stop_reason,
            'variant_statistics': variant_stats,
            'total_samples': sum(stats['sample_size'] for stats in variant_stats.values())
        }
    
    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Experiment tahlili"""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        results = self.experiment_results[experiment_id]
        
        if not results:
            return {'error': 'No results available for analysis'}
        
        # Find control variant
        control_variant = None
        treatment_variants = []
        
        for variant_id, variant in experiment.variants.items():
            if variant.is_control:
                control_variant = variant_id
            else:
                treatment_variants.append(variant_id)
        
        if not control_variant:
            return {'error': 'No control variant found'}
        
        # Collect data for analysis
        control_data = [r.metric_value for r in results if r.variant_id == control_variant]
        
        analysis_results = {
            'experiment_id': experiment_id,
            'control_variant': control_variant,
            'treatment_comparisons': [],
            'overall_summary': self._generate_overall_summary(experiment, results),
            'recommendation': ''
        }
        
        # Compare each treatment variant with control
        for treatment_id in treatment_variants:
            treatment_data = [r.metric_value for r in results if r.variant_id == treatment_id]
            
            if len(control_data) < 10 or len(treatment_data) < 10:
                analysis_results['treatment_comparisons'].append({
                    'treatment_variant': treatment_id,
                    'error': 'Insufficient data for statistical analysis'
                })
                continue
            
            # Perform statistical test
            comparison = self._compare_variants(control_data, treatment_data, experiment.confidence_level)
            comparison['treatment_variant'] = treatment_id
            comparison['control_variant'] = control_variant
            
            analysis_results['treatment_comparisons'].append(comparison)
        
        # Generate recommendation
        analysis_results['recommendation'] = self._generate_recommendation(analysis_results['treatment_comparisons'])
        
        return analysis_results
    
    def _validate_experiment(self, experiment: Experiment) -> bool:
        """Experiment validatsiya"""
        
        # Check variants
        if len(experiment.variants) < 2:
            logging.error("At least 2 variants required")
            return False
        
        # Check traffic allocation
        total_allocation = sum(v.traffic_allocation for v in experiment.variants.values())
        if abs(total_allocation - 1.0) > 0.01:
            logging.error("Traffic allocation must sum to 1.0")
            return False
        
        # Check control variant
        control_count = sum(1 for v in experiment.variants.values() if v.is_control)
        if control_count != 1:
            logging.error("Exactly one control variant required")
            return False
        
        return True
    
    def _initialize_traffic_routing(self, experiment: Experiment):
        """Traffic routing ni boshlash"""
        
        # Initialize traffic splitter with variant weights
        variant_weights = {v.variant_id: v.traffic_allocation for v in experiment.variants.values()}
        self.traffic_splitter.set_weights(variant_weights)
    
    def _start_analysis_monitoring(self):
        """Tahlil monitoringni boshlash"""
        
        if self.running:
            return
        
        self.running = True
        self.analysis_thread = threading.Thread(target=self._analysis_monitor_worker, daemon=True)
        self.analysis_thread.start()
        
        logging.info("A/B test analysis monitoring started")
    
    def _analysis_monitor_worker(self):
        """Tahlil monitoring worker"""
        
        while self.running:
            try:
                # Check running experiments
                for experiment_id, experiment in self.experiments.items():
                    if experiment.status == ExperimentStatus.RUNNING:
                        status = self.get_experiment_status(experiment_id)
                        
                        # Check if should stop
                        if status['should_stop']:
                            self.stop_experiment(experiment_id, status['stop_reason'])
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Analysis monitoring error: {str(e)}")
                time.sleep(60)
    
    def _should_stop_experiment(self, experiment: Experiment, variant_stats: Dict[str, Any]) -> Tuple[bool, str]:
        """Experiment ni to'xtatish kerakligini aniqlash"""
        
        # Check minimum sample size
        min_samples_reached = all(stats['sample_size'] >= experiment.minimum_sample_size 
                                 for stats in variant_stats.values())
        
        if not min_samples_reached:
            return False, "Insufficient sample size"
        
        # Check maximum duration
        if experiment.started_at:
            duration = (datetime.now() - experiment.started_at).days
            if duration >= experiment.maximum_duration_days:
                return True, f"Maximum duration of {experiment.maximum_duration_days} days reached"
        
        # Check for statistical significance
        analysis = self.analyze_experiment(experiment.experiment_id)
        
        if 'treatment_comparisons' in analysis:
            for comparison in analysis['treatment_comparisons']:
                if 'statistical_test' in comparison and comparison['statistical_test']['significant']:
                    return True, "Statistical significance achieved"
        
        return False, "Continue running"
    
    def _calculate_confidence_interval(self, data: List[float], confidence_level: float) -> Tuple[float, float]:
        """Confidence interval hisoblash"""
        
        if len(data) < 2:
            return (0.0, 0.0)
        
        mean = np.mean(data)
        sem = stats.sem(data)  # Standard error of mean
        
        # Calculate confidence interval
        interval = stats.t.interval(confidence_level, len(data) - 1, loc=mean, scale=sem)
        
        return interval
    
    def _compare_variants(self, control_data: List[float], treatment_data: List[float],
                        confidence_level: float) -> Dict[str, Any]:
        """Variantlarni taqqoslash"""
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(treatment_data, control_data)
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((len(treatment_data) - 1) * np.var(treatment_data, ddof=1) + 
                             (len(control_data) - 1) * np.var(control_data, ddof=1)) / 
                            (len(treatment_data) + len(control_data) - 2))
        
        cohens_d = (np.mean(treatment_data) - np.mean(control_data)) / pooled_std
        
        # Determine significance
        alpha = 1 - confidence_level
        is_significant = p_value < alpha
        
        # Effect size interpretation
        if abs(cohens_d) < 0.2:
            effect_interpretation = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_interpretation = "small"
        elif abs(cohens_d) < 0.8:
            effect_interpretation = "medium"
        else:
            effect_interpretation = "large"
        
        # Confidence intervals for means
        control_ci = self._calculate_confidence_interval(control_data, confidence_level)
        treatment_ci = self._calculate_confidence_interval(treatment_data, confidence_level)
        
        # Difference confidence interval
        diff_mean = np.mean(treatment_data) - np.mean(control_data)
        diff_se = np.sqrt(np.var(treatment_data)/len(treatment_data) + np.var(control_data)/len(control_data))
        diff_ci = stats.t.interval(confidence_level, len(treatment_data) + len(control_data) - 2, 
                                  loc=diff_mean, scale=diff_se)
        
        return {
            'control_mean': np.mean(control_data),
            'treatment_mean': np.mean(treatment_data),
            'difference': diff_mean,
            'relative_improvement': (np.mean(treatment_data) - np.mean(control_data)) / np.mean(control_data),
            'statistical_test': {
                'test_type': 't_test',
                'statistic': t_stat,
                'p_value': p_value,
                'significant': is_significant,
                'effect_size': cohens_d,
                'effect_interpretation': effect_interpretation
            },
            'confidence_intervals': {
                'control': control_ci,
                'treatment': treatment_ci,
                'difference': diff_ci
            },
            'sample_sizes': {
                'control': len(control_data),
                'treatment': len(treatment_data)
            }
        }
    
    def _generate_overall_summary(self, experiment: Experiment, results: deque) -> Dict[str, Any]:
        """Umumiy xulosa yaratish"""
        
        total_samples = len(results)
        
        if total_samples == 0:
            return {'error': 'No data available'}
        
        # Overall metrics
        all_values = [r.metric_value for r in results]
        
        return {
            'total_samples': total_samples,
            'overall_mean': np.mean(all_values),
            'overall_std': np.std(all_values),
            'experiment_duration_days': (datetime.now() - experiment.created_at).days,
            'variants_tested': len(experiment.variants),
            'daily_sample_rate': total_samples / max((datetime.now() - experiment.created_at).days, 1)
        }
    
    def _generate_recommendation(self, comparisons: List[Dict[str, Any]]) -> str:
        """Tavsiya yaratish"""
        
        if not comparisons:
            return "Insufficient data for recommendation"
        
        significant_winners = []
        
        for comparison in comparisons:
            if 'error' in comparison:
                continue
            
            test = comparison.get('statistical_test', {})
            if test.get('significant', False):
                effect_size = test.get('effect_size', 0)
                relative_improvement = comparison.get('relative_improvement', 0)
                
                if effect_size > 0 and relative_improvement > 0:
                    significant_winners.append({
                        'variant': comparison['treatment_variant'],
                        'improvement': relative_improvement,
                        'effect_size': effect_size,
                        'p_value': test.get('p_value', 1.0)
                    })
        
        if not significant_winners:
            return "No statistically significant improvements found. Continue monitoring or consider different variants."
        
        # Sort by improvement
        best_winner = max(significant_winners, key=lambda x: x['improvement'])
        
        return (f"Implement variant {best_winner['variant']} - "
                f"{best_winner['improvement']:.1%} improvement with "
                f"{best_winner['effect_size']:.2f} effect size "
                f"(p-value: {best_winner['p_value']:.4f})")
    
    def get_all_experiments_summary(self) -> Dict[str, Any]:
        """Barcha experimentlar xulosasi"""
        
        summary = {
            'total_experiments': len(self.experiments),
            'running_experiments': 0,
            'completed_experiments': 0,
            'experiments_by_type': defaultdict(int),
            'experiments_by_status': defaultdict(int)
        }
        
        for experiment in self.experiments.values():
            summary['experiments_by_type'][experiment.experiment_type.value] += 1
            summary['experiments_by_status'][experiment.status.value] += 1
            
            if experiment.status == ExperimentStatus.RUNNING:
                summary['running_experiments'] += 1
            elif experiment.status == ExperimentStatus.COMPLETED:
                summary['completed_experiments'] += 1
        
        return dict(summary)

class TrafficSplitter:
    """Traffic bo'lish"""
    
    def __init__(self):
        self.variant_weights = {}
        self.hash_function = hashlib.md5
        
    def set_weights(self, weights: Dict[str, float]):
        """Variant vaznlarini o'rnatish"""
        self.variant_weights = weights
    
    def assign_variant(self, user_id: str, experiment: Experiment) -> str:
        """Foydalanuvchini variantga tayinlash"""
        
        if not self.variant_weights:
            # Default to first variant
            return list(experiment.variants.keys())[0]
        
        # Hash user_id to get consistent assignment
        hash_value = int(self.hash_function(user_id.encode()).hexdigest(), 16)
        normalized_hash = hash_value % 10000 / 10000.0  # 0-1 range
        
        # Assign based on cumulative weights
        cumulative = 0.0
        for variant_id, weight in self.variant_weights.items():
            cumulative += weight
            if normalized_hash <= cumulative:
                return variant_id
        
        # Fallback to last variant
        return list(self.variant_weights.keys())[-1]

class ExperimentVisualizer:
    """Experiment vizualizatsiya"""
    
    @staticmethod
    def plot_experiment_results(experiment_results: Dict[str, Any], save_path: Optional[str] = None):
        """Experiment natijalarini chizish"""
        
        if 'variant_statistics' not in experiment_results:
            logging.warning("No variant statistics available for plotting")
            return
        
        variants = experiment_results['variant_statistics']
        variant_names = list(variants.keys())
        means = [variants[v]['mean'] for v in variant_names]
        stds = [variants[v]['std'] for v in variant_names]
        
        # Create plot
        plt.figure(figsize=(10, 6))
        
        bars = plt.bar(variant_names, means, yerr=stds, capsize=5, alpha=0.7)
        
        # Color control variant differently
        for i, (name, variant) in enumerate(variants.items()):
            if any(v.name == name for v in experiment_results.get('experiment_variants', [])):
                bars[i].set_color('blue')  # Control
            else:
                bars[i].set_color('orange')  # Treatment
        
        plt.title(f"Experiment Results: {experiment_results['name']}")
        plt.xlabel("Variants")
        plt.ylabel(experiment_results['primary_metric'].title())
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            logging.info(f"Experiment plot saved to {save_path}")
        
        plt.show()

# Demo va test
if __name__ == "__main__":
    # A/B testing manager testi
    manager = ABTestingManager({
        'default_confidence_level': 0.95,
        'minimum_sample_size': 50,
        'max_experiments_concurrent': 3
    })
    
    print("=== A/B TESTING MANAGER TEST ===")
    
    # Create mock models
    class MockModel:
        def __init__(self, model_type="baseline"):
            self.model_type = model_type
            self.performance = np.random.uniform(0.6, 0.8)
        
        def predict(self, X):
            return np.random.randint(0, 2, len(X) if hasattr(X, '__len__') else 1)
    
    # Create variants
    control_variant = ExperimentVariant(
        variant_id="control_v1",
        name="Baseline Model",
        description="Current production model",
        configuration={"model_type": "baseline", "learning_rate": 0.001},
        traffic_allocation=0.5,
        model=MockModel("baseline"),
        is_control=True
    )
    
    treatment_variant = ExperimentVariant(
        variant_id="treatment_v1", 
        name="Improved Model",
        description="New model with enhanced features",
        configuration={"model_type": "improved", "learning_rate": 0.01},
        traffic_allocation=0.5,
        model=MockModel("improved"),
        is_control=False
    )
    
    # Create experiment
    experiment_id = manager.create_experiment(
        name="Model Comparison Test",
        experiment_type=ExperimentType.MODEL_COMPARISON,
        variants=[control_variant, treatment_variant],
        primary_metric="accuracy",
        description="Comparing baseline vs improved model"
    )
    
    print(f"Created experiment: {experiment_id}")
    
    # Start experiment
    success = manager.start_experiment(experiment_id)
    print(f"Experiment started: {success}")
    
    # Simulate results
    np.random.seed(42)
    
    for day in range(10):
        for sample in range(20):
            # Simulate user assignments
            user_id = f"user_{day}_{sample}"
            variant_id = manager.assign_user_to_variant(user_id, experiment_id)
            
            # Simulate metric values
            if variant_id == "control_v1":
                metric_value = np.random.normal(0.72, 0.05)
            else:
                metric_value = np.random.normal(0.75, 0.06)  # Slightly better
            
            # Add additional metrics
            additional_metrics = {
                "precision": metric_value * np.random.uniform(0.9, 1.0),
                "recall": metric_value * np.random.uniform(0.85, 0.95),
                "f1_score": metric_value * np.random.uniform(0.88, 0.98)
            }
            
            # Record result
            manager.record_result(experiment_id, variant_id, metric_value, additional_metrics)
    
    # Check experiment status
    status = manager.get_experiment_status(experiment_id)
    print(f"\n=== EXPERIMENT STATUS ===")
    print(f"Name: {status['name']}")
    print(f"Status: {status['status']}")
    print(f"Total samples: {status['total_samples']}")
    print(f"Duration: {status['duration_days']} days")
    
    # Show variant statistics
    for variant_id, stats in status['variant_statistics'].items():
        print(f"Variant {variant_id}: {stats['sample_size']} samples, "
              f"mean={stats['mean']:.3f}±{stats['std']:.3f}")
    
    # Analyze experiment
    analysis = manager.analyze_experiment(experiment_id)
    print(f"\n=== EXPERIMENT ANALYSIS ===")
    print(f"Recommendation: {analysis['recommendation']}")
    
    if analysis['treatment_comparisons']:
        for comparison in analysis['treatment_comparisons']:
            if 'error' not in comparison:
                test = comparison['statistical_test']
                print(f"Treatment vs Control:")
                print(f"  Difference: {comparison['difference']:.3f}")
                print(f"  Improvement: {comparison['relative_improvement']:.1%}")
                print(f"  P-value: {test['p_value']:.4f}")
                print(f"  Significant: {test['significant']}")
                print(f"  Effect size: {test['effect_size']:.2f} ({test['effect_interpretation']})")
    
    # Test multiple experiments
    # Create another experiment
    model1 = MockModel("variant_a")
    model2 = MockModel("variant_b")
    
    variant_a = ExperimentVariant(
        variant_id="variant_a",
        name="Algorithm A", 
        description="Algorithm A configuration",
        configuration={"algorithm": "A", "threshold": 0.5},
        traffic_allocation=0.5,
        model=model1,
        is_control=True
    )
    
    variant_b = ExperimentVariant(
        variant_id="variant_b",
        name="Algorithm B",
        description="Algorithm B configuration", 
        configuration={"algorithm": "B", "threshold": 0.6},
        traffic_allocation=0.5,
        model=model2,
        is_control=False
    )
    
    experiment2_id = manager.create_experiment(
        name="Algorithm Comparison",
        experiment_type=ExperimentType.STRATEGY_COMPARISON,
        variants=[variant_a, variant_b],
        primary_metric="f1_score"
    )
    
    # Start second experiment
    manager.start_experiment(experiment2_id)
    
    # Get all experiments summary
    all_summary = manager.get_all_experiments_summary()
    print(f"\n=== ALL EXPERIMENTS SUMMARY ===")
    print(f"Total experiments: {all_summary['total_experiments']}")
    print(f"Running: {all_summary['running_experiments']}")
    print(f"Completed: {all_summary['completed_experiments']}")
    print("By type:", dict(all_summary['experiments_by_type']))
    print("By status:", dict(all_summary['experiments_by_status']))
    
    print("\n=== A/B TESTING TEST COMPLETED ===")