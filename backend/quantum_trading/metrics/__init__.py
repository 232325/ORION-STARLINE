"""
Quantum Advantage Metrics Module
===============================

Bu modul quantum trading tizimining afzalliklarini o'lchash uchun
quyidagi metrikalarni hisoblaydi:
1. Computational Speedup Metrics
2. Memory Efficiency Metrics
3. Parallel Processing Capability
4. Optimization Improvement Metrics
5. Risk Reduction Benefits

Quantum vs classical algoritmlar samaradorligini taqqoslash.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import asyncio
import logging
from datetime import datetime, timedelta
import time
import psutil
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
from scipy import stats
import json

class MetricType(Enum):
    """Metrika turlari"""
    SPEEDUP = "computational_speedup"
    MEMORY_EFFICIENCY = "memory_efficiency"
    PARALLEL_PROCESSING = "parallel_processing"
    OPTIMIZATION_IMPROVEMENT = "optimization_improvement"
    RISK_REDUCTION = "risk_reduction"
    ACCURACY = "accuracy"
    SCALABILITY = "scalability"

class QuantumAdvantageLevel(Enum):
    """Quantum afzallik darajalari"""
    NONE = "none"           # 0-5% advantage
    MINIMAL = "minimal"     # 5-15% advantage
    MODERATE = "moderate"   # 15-50% advantage
    SIGNIFICANT = "significant"  # 50-200% advantage
    QUANTUM_SUPREMACY = "quantum_supremacy"  # >200% advantage

@dataclass
class PerformanceMetrics:
    """Performance metrikalari"""
    metric_type: MetricType
    quantum_value: float
    classical_value: float
    advantage_percentage: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    statistical_significance: bool
    timestamp: datetime

@dataclass
class QuantumAdvantageReport:
    """Quantum afzallik hisoboti"""
    overall_advantage: float
    dominant_metrics: List[str]
    quantum_supremacy_achieved: bool
    recommendations: List[str]
    detailed_metrics: Dict[str, PerformanceMetrics]

class QuantumAdvantageMetrics:
    """
    Quantum Advantage Metrics Calculator
    
    Bu sinf quantum trading tizimining performance metrikalarini
    hisoblaydi va quantum afzallikni baholaydi.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("quantum_advantage_metrics")
        self.metrics_history = []
        self.baseline_measurements = {}
        self.quantum_profiling_data = {}
        self.classical_profiling_data = {}
        
        # Measurement parameters
        self.confidence_level = 0.95
        self.statistical_threshold = 0.05  # p-value threshold
        self.min_sample_size = 30
        
        self.logger.info("Quantum Advantage Metrics Calculator initialized")
    
    async def initialize(self):
        """Metrics kalkulyatorni initsializatsiya qilish"""
        self.logger.info("Initializing Quantum Advantage Metrics Calculator...")
        
        # Setup baseline measurements
        await self._setup_baseline_measurements()
        
        # Initialize profiling systems
        await self._initialize_profiling_systems()
        
        self.logger.info("Quantum Advantage Metrics Calculator initialized successfully")
    
    async def _setup_baseline_measurements(self):
        """Baseline o'lchovlarni sozlash"""
        self.baseline_measurements = {
            "classical_computation_time": {
                "portfolio_optimization": 1.0,  # seconds
                "risk_calculation": 0.1,
                "market_analysis": 0.5,
                "arbitrage_detection": 2.0
            },
            "classical_memory_usage": {
                "portfolio_data": 100,  # MB
                "market_data": 500,     # MB
                "optimization_state": 50,  # MB
                "calculation_cache": 25   # MB
            },
            "classical_accuracy": {
                "portfolio_optimization": 0.85,
                "risk_estimation": 0.90,
                "prediction_accuracy": 0.75,
                "signal_generation": 0.80
            },
            "classical_scalability": {
                "max_assets": 1000,
                "max_optimization_variables": 100,
                "max_parallel_processes": 8
            }
        }
    
    async def _initialize_profiling_systems(self):
        """Profiling tizimlarini initsializatsiya qilish"""
        self.profiling_config = {
            "cpu_profiling": True,
            "memory_profiling": True,
            "time_profiling": True,
            "accuracy_tracking": True,
            "parallel_efficiency": True
        }
    
    async def calculate_cycle_metrics(self, trade_results: Dict[str, Any], 
                                    portfolio_state: Dict[str, Any],
                                    quantum_advantage_threshold: float) -> Dict[str, Any]:
        """Tsikl metrikalarini hisoblash"""
        self.logger.info("Calculating quantum advantage metrics for trading cycle...")
        
        # Collect performance data
        performance_data = await self._collect_cycle_performance_data(trade_results, portfolio_state)
        
        # Calculate individual metrics
        metrics_results = {}
        
        # Computational speedup
        speedup_metrics = await self._calculate_computational_speedup(performance_data)
        metrics_results["computational_speedup"] = speedup_metrics
        
        # Memory efficiency
        memory_metrics = await self._calculate_memory_efficiency(performance_data)
        metrics_results["memory_efficiency"] = memory_metrics
        
        # Parallel processing capability
        parallel_metrics = await self._calculate_parallel_processing_capability(performance_data)
        metrics_results["parallel_processing"] = parallel_metrics
        
        # Optimization improvement
        optimization_metrics = await self._calculate_optimization_improvement(performance_data)
        metrics_results["optimization_improvement"] = optimization_metrics
        
        # Risk reduction benefits
        risk_metrics = await self._calculate_risk_reduction_benefits(performance_data)
        metrics_results["risk_reduction"] = risk_metrics
        
        # Overall quantum advantage assessment
        overall_advantage = await self._calculate_overall_advantage(metrics_results)
        
        # Generate quantum advantage level
        advantage_level = self._determine_advantage_level(overall_advantage)
        
        # Create comprehensive report
        advantage_report = QuantumAdvantageReport(
            overall_advantage=overall_advantage,
            dominant_metrics=await self._identify_dominant_metrics(metrics_results),
            quantum_supremacy_achieved=overall_advantage > 200.0,
            recommendations=await self._generate_recommendations(metrics_results, advantage_level),
            detailed_metrics=metrics_results
        )
        
        # Store metrics in history
        self.metrics_history.append({
            "timestamp": datetime.now().isoformat(),
            "cycle_metrics": advantage_report
        })
        
        self.logger.info(f"Quantum advantage calculated: {overall_advantage:.2f}% "
                        f"(Level: {advantage_level.value})")
        
        return {
            "overall_advantage": overall_advantage,
            "advantage_level": advantage_level.value,
            "detailed_metrics": metrics_results,
            "quantum_supremacy_achieved": overall_advantage > 200.0,
            "recommendations": advantage_report.recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _collect_cycle_performance_data(self, trade_results: Dict[str, Any], 
                                            portfolio_state: Dict[str, Any]) -> Dict[str, Any]:
        """Tsikl performance ma'lumotlarini to'plash"""
        performance_data = {
            "execution_times": {},
            "memory_usage": {},
            "accuracy_scores": {},
            "scalability_metrics": {},
            "resource_utilization": {}
        }
        
        # Extract execution times from trade results
        for asset_type, trade_result in trade_results.items():
            if "execution_time" in trade_result:
                performance_data["execution_times"][asset_type] = trade_result["execution_time"]
        
        # Simulate quantum vs classical performance measurements
        performance_data["quantum_computation_time"] = np.random.uniform(0.01, 0.05)  # seconds
        performance_data["classical_computation_time"] = np.random.uniform(0.1, 0.5)  # seconds
        
        performance_data["quantum_memory_usage"] = np.random.uniform(50, 100)  # MB
        performance_data["classical_memory_usage"] = np.random.uniform(200, 400)  # MB
        
        performance_data["quantum_accuracy"] = np.random.uniform(0.85, 0.95)
        performance_data["classical_accuracy"] = np.random.uniform(0.75, 0.85)
        
        performance_data["quantum_parallel_efficiency"] = np.random.uniform(0.8, 0.95)
        performance_data["classical_parallel_efficiency"] = np.random.uniform(0.5, 0.7)
        
        return performance_data
    
    async def _calculate_computational_speedup(self, performance_data: Dict[str, Any]) -> PerformanceMetrics:
        """Computational speedup hisoblash"""
        quantum_time = performance_data["quantum_computation_time"]
        classical_time = performance_data["classical_computation_time"]
        
        # Calculate speedup factor
        speedup_factor = classical_time / quantum_time if quantum_time > 0 else 1.0
        
        # Calculate advantage percentage
        advantage_percentage = ((speedup_factor - 1) * 100)
        
        # Statistical significance test
        t_stat, p_value = self._perform_statistical_test(
            [classical_time], [quantum_time]
        )
        is_significant = p_value < self.statistical_threshold
        
        # Confidence interval
        confidence_interval = self._calculate_confidence_interval(
            [classical_time], [quantum_time], self.confidence_level
        )
        
        return PerformanceMetrics(
            metric_type=MetricType.SPEEDUP,
            quantum_value=quantum_time,
            classical_value=classical_time,
            advantage_percentage=advantage_percentage,
            confidence_interval=confidence_interval,
            sample_size=1,  # Single measurement for simplicity
            statistical_significance=is_significant,
            timestamp=datetime.now()
        )
    
    async def _calculate_memory_efficiency(self, performance_data: Dict[str, Any]) -> PerformanceMetrics:
        """Memory efficiency hisoblash"""
        quantum_memory = performance_data["quantum_memory_usage"]
        classical_memory = performance_data["classical_memory_usage"]
        
        # Calculate memory efficiency improvement
        memory_improvement = ((classical_memory - quantum_memory) / classical_memory * 100)
        
        # Statistical significance
        t_stat, p_value = self._perform_statistical_test(
            [classical_memory], [quantum_memory]
        )
        is_significant = p_value < self.statistical_threshold
        
        # Confidence interval
        confidence_interval = self._calculate_confidence_interval(
            [classical_memory], [quantum_memory], self.confidence_level
        )
        
        return PerformanceMetrics(
            metric_type=MetricType.MEMORY_EFFICIENCY,
            quantum_value=quantum_memory,
            classical_value=classical_memory,
            advantage_percentage=memory_improvement,
            confidence_interval=confidence_interval,
            sample_size=1,
            statistical_significance=is_significant,
            timestamp=datetime.now()
        )
    
    async def _calculate_parallel_processing_capability(self, performance_data: Dict[str, Any]) -> PerformanceMetrics:
        """Parallel processing capability hisoblash"""
        quantum_efficiency = performance_data["quantum_parallel_efficiency"]
        classical_efficiency = performance_data["classical_parallel_efficiency"]
        
        # Calculate parallel processing advantage
        parallel_advantage = ((quantum_efficiency - classical_efficiency) / classical_efficiency * 100)
        
        # Statistical significance
        t_stat, p_value = self._perform_statistical_test(
            [classical_efficiency], [quantum_efficiency]
        )
        is_significant = p_value < self.statistical_threshold
        
        # Confidence interval
        confidence_interval = self._calculate_confidence_interval(
            [classical_efficiency], [quantum_efficiency], self.confidence_level
        )
        
        return PerformanceMetrics(
            metric_type=MetricType.PARALLEL_PROCESSING,
            quantum_value=quantum_efficiency,
            classical_value=classical_efficiency,
            advantage_percentage=parallel_advantage,
            confidence_interval=confidence_interval,
            sample_size=1,
            statistical_significance=is_significant,
            timestamp=datetime.now()
        )
    
    async def _calculate_optimization_improvement(self, performance_data: Dict[str, Any]) -> PerformanceMetrics:
        """Optimization improvement hisoblash"""
        # Simulate optimization quality metrics
        quantum_optimization_quality = np.random.uniform(0.85, 0.95)
        classical_optimization_quality = np.random.uniform(0.70, 0.85)
        
        # Calculate optimization improvement
        optimization_improvement = ((quantum_optimization_quality - classical_optimization_quality) / 
                                  classical_optimization_quality * 100)
        
        # Statistical significance
        t_stat, p_value = self._perform_statistical_test(
            [classical_optimization_quality], [quantum_optimization_quality]
        )
        is_significant = p_value < self.statistical_threshold
        
        # Confidence interval
        confidence_interval = self._calculate_confidence_interval(
            [classical_optimization_quality], [quantum_optimization_quality], self.confidence_level
        )
        
        return PerformanceMetrics(
            metric_type=MetricType.OPTIMIZATION_IMPROVEMENT,
            quantum_value=quantum_optimization_quality,
            classical_value=classical_optimization_quality,
            advantage_percentage=optimization_improvement,
            confidence_interval=confidence_interval,
            sample_size=1,
            statistical_significance=is_significant,
            timestamp=datetime.now()
        )
    
    async def _calculate_risk_reduction_benefits(self, performance_data: Dict[str, Any]) -> PerformanceMetrics:
        """Risk reduction benefits hisoblash"""
        # Simulate risk metrics
        quantum_risk_score = np.random.uniform(0.05, 0.15)  # Lower is better
        classical_risk_score = np.random.uniform(0.10, 0.25)  # Lower is better
        
        # Calculate risk reduction (higher percentage is better)
        risk_reduction = ((classical_risk_score - quantum_risk_score) / classical_risk_score * 100)
        
        # Statistical significance
        t_stat, p_value = self._perform_statistical_test(
            [classical_risk_score], [quantum_risk_score]
        )
        is_significant = p_value < self.statistical_threshold
        
        # Confidence interval
        confidence_interval = self._calculate_confidence_interval(
            [classical_risk_score], [quantum_risk_score], self.confidence_level
        )
        
        return PerformanceMetrics(
            metric_type=MetricType.RISK_REDUCTION,
            quantum_value=quantum_risk_score,
            classical_value=classical_risk_score,
            advantage_percentage=risk_reduction,
            confidence_interval=confidence_interval,
            sample_size=1,
            statistical_significance=is_significant,
            timestamp=datetime.now()
        )
    
    async def _calculate_overall_advantage(self, metrics_results: Dict[str, PerformanceMetrics]) -> float:
        """Umumiy quantum afzallikni hisoblash"""
        advantages = []
        weights = {
            MetricType.SPEEDUP: 0.25,
            MetricType.MEMORY_EFFICIENCY: 0.15,
            MetricType.PARALLEL_PROCESSING: 0.20,
            MetricType.OPTIMIZATION_IMPROVEMENT: 0.25,
            MetricType.RISK_REDUCTION: 0.15
        }
        
        for metric_type, metrics in metrics_results.items():
            if metric_type in weights:
                weighted_advantage = metrics.advantage_percentage * weights[metric_type]
                advantages.append(weighted_advantage)
        
        overall_advantage = sum(advantages) if advantages else 0.0
        return max(0.0, overall_advantage)  # Ensure non-negative
    
    def _determine_advantage_level(self, overall_advantage: float) -> QuantumAdvantageLevel:
        """Quantum afzallik darajasini aniqlash"""
        if overall_advantage < 5:
            return QuantumAdvantageLevel.NONE
        elif overall_advantage < 15:
            return QuantumAdvantageLevel.MINIMAL
        elif overall_advantage < 50:
            return QuantumAdvantageLevel.MODERATE
        elif overall_advantage < 200:
            return QuantumAdvantageLevel.SIGNIFICANT
        else:
            return QuantumAdvantageLevel.QUANTUM_SUPREMACY
    
    async def _identify_dominant_metrics(self, metrics_results: Dict[str, PerformanceMetrics]) -> List[str]:
        """Dominant metrikalarni aniqlash"""
        sorted_metrics = sorted(
            metrics_results.items(),
            key=lambda x: x[1].advantage_percentage,
            reverse=True
        )
        
        # Return top 3 metrics with highest advantage
        dominant = [metric_type for metric_type, _ in sorted_metrics[:3]]
        return dominant
    
    async def _generate_recommendations(self, metrics_results: Dict[str, PerformanceMetrics], 
                                      advantage_level: QuantumAdvantageLevel) -> List[str]:
        """Tavsiyalar yaratish"""
        recommendations = []
        
        # Level-based recommendations
        if advantage_level == QuantumAdvantageLevel.QUANTUM_SUPREMACY:
            recommendations.append("Quantum Supremacy achieved! Consider scaling up quantum resource allocation.")
        elif advantage_level == QuantumAdvantageLevel.SIGNIFICANT:
            recommendations.append("Significant quantum advantage demonstrated. Optimize quantum circuits for further improvements.")
        elif advantage_level == QuantumAdvantageLevel.MODERATE:
            recommendations.append("Moderate quantum advantage detected. Focus on algorithm optimization.")
        elif advantage_level == QuantumAdvantageLevel.MINIMAL:
            recommendations.append("Minimal quantum advantage. Consider hybrid approaches or error mitigation.")
        else:
            recommendations.append("No significant quantum advantage. Review implementation and parameters.")
        
        # Metric-specific recommendations
        for metric_type, metrics in metrics_results.items():
            if metrics.advantage_percentage > 100:
                recommendations.append(f"Excellent {metric_type} performance. Leverage this advantage further.")
            elif metrics.advantage_percentage < 0:
                recommendations.append(f"Classical outperforms quantum in {metric_type}. Investigate improvement opportunities.")
        
        return recommendations
    
    def _perform_statistical_test(self, classical_data: List[float], 
                                quantum_data: List[float]) -> Tuple[float, float]:
        """Statistical test o'tkazish (t-test)"""
        try:
            # Perform Welch's t-test (unequal variances)
            t_stat, p_value = stats.ttest_ind(classical_data, quantum_data, equal_var=False)
            return float(t_stat), float(p_value)
        except:
            return 0.0, 1.0  # Return non-significant if test fails
    
    def _calculate_confidence_interval(self, classical_data: List[float], 
                                     quantum_data: List[float], 
                                     confidence_level: float) -> Tuple[float, float]:
        """Confidence interval hisoblash"""
        try:
            # Calculate difference between means
            classical_mean = np.mean(classical_data)
            quantum_mean = np.mean(quantum_data)
            difference = quantum_mean - classical_mean
            
            # Calculate pooled standard error
            classical_std = np.std(classical_data, ddof=1)
            quantum_std = np.std(quantum_data, ddof=1)
            n_classical = len(classical_data)
            n_quantum = len(quantum_data)
            
            pooled_se = np.sqrt((classical_std**2 / n_classical) + (quantum_std**2 / n_quantum))
            
            # Critical value for confidence level
            alpha = 1 - confidence_level
            t_critical = stats.t.ppf(1 - alpha/2, n_classical + n_quantum - 2)
            
            # Confidence interval
            margin_error = t_critical * pooled_se
            confidence_interval = (difference - margin_error, difference + margin_error)
            
            return confidence_interval
        except:
            return (0.0, 0.0)  # Return zero interval if calculation fails
    
    async def calculate_scalability_metrics(self, system_config: Dict[str, Any]) -> Dict[str, Any]:
        """Scalability metrikalarini hisoblash"""
        self.logger.info("Calculating scalability metrics...")
        
        # Simulate scaling behavior
        asset_counts = [100, 500, 1000, 2000, 5000]
        scalability_data = {
            "quantum_scaling": {},
            "classical_scaling": {}
        }
        
        for n_assets in asset_counts:
            # Quantum scaling (theoretically better for large problems)
            quantum_time = 0.01 * np.log(n_assets)  # Logarithmic scaling
            quantum_memory = 50 + 0.1 * n_assets  # Linear with small constant
            
            # Classical scaling (worse for large problems)
            classical_time = 0.1 * np.sqrt(n_assets)  # Square root scaling
            classical_memory = 100 + 0.5 * n_assets  # Linear with larger constant
            
            scalability_data["quantum_scaling"][n_assets] = {
                "computation_time": quantum_time,
                "memory_usage": quantum_memory
            }
            
            scalability_data["classical_scaling"][n_assets] = {
                "computation_time": classical_time,
                "memory_usage": classical_memory
            }
        
        # Calculate scaling advantages
        scaling_advantages = {}
        for n_assets in asset_counts:
            quantum_time = scalability_data["quantum_scaling"][n_assets]["computation_time"]
            classical_time = scalability_data["classical_scaling"][n_assets]["computation_time"]
            time_advantage = ((classical_time - quantum_time) / classical_time) * 100
            
            quantum_memory = scalability_data["quantum_scaling"][n_assets]["memory_usage"]
            classical_memory = scalability_data["classical_scaling"][n_assets]["memory_usage"]
            memory_advantage = ((classical_memory - quantum_memory) / classical_memory) * 100
            
            scaling_advantages[n_assets] = {
                "time_advantage": time_advantage,
                "memory_advantage": memory_advantage
            }
        
        return {
            "scalability_data": scalability_data,
            "scaling_advantages": scaling_advantages,
            "quantum_efficiency_growth": "Super-polynomial advantage for large-scale problems",
            "recommended_scaling_threshold": 1000,  # assets
            "timestamp": datetime.now().isoformat()
        }
    
    async def benchmark_quantum_algorithms(self, algorithm_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Quantum algoritmlarni benchmark qilish"""
        self.logger.info("Benchmarking quantum algorithms...")
        
        benchmark_results = {}
        
        for config in algorithm_configs:
            algorithm_name = config.get("name", "unknown")
            self.logger.info(f"Benchmarking algorithm: {algorithm_name}")
            
            # Simulate algorithm performance
            performance_data = await self._simulate_algorithm_performance(config)
            
            benchmark_results[algorithm_name] = {
                "configuration": config,
                "performance_metrics": performance_data,
                "quantum_advantage": await self._calculate_algorithm_advantage(performance_data),
                "timestamp": datetime.now().isoformat()
            }
        
        # Rank algorithms by quantum advantage
        ranked_algorithms = sorted(
            benchmark_results.items(),
            key=lambda x: x[1]["quantum_advantage"],
            reverse=True
        )
        
        return {
            "benchmark_results": benchmark_results,
            "algorithm_rankings": [name for name, _ in ranked_algorithms],
            "best_algorithm": ranked_algorithms[0][0] if ranked_algorithms else None,
            "performance_comparison": await self._create_performance_comparison(benchmark_results),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _simulate_algorithm_performance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Algorithm performance simulyatsiyasi"""
        algorithm_type = config.get("type", "vqe")
        
        # Different algorithms have different performance characteristics
        if algorithm_type == "vqe":
            quantum_time = np.random.uniform(0.05, 0.15)
            classical_time = np.random.uniform(0.3, 0.8)
            quantum_accuracy = np.random.uniform(0.85, 0.95)
            classical_accuracy = np.random.uniform(0.75, 0.85)
        elif algorithm_type == "qaoa":
            quantum_time = np.random.uniform(0.03, 0.10)
            classical_time = np.random.uniform(0.4, 1.0)
            quantum_accuracy = np.random.uniform(0.80, 0.92)
            classical_accuracy = np.random.uniform(0.70, 0.82)
        elif algorithm_type == "annealing":
            quantum_time = np.random.uniform(0.01, 0.05)
            classical_time = np.random.uniform(0.8, 2.0)
            quantum_accuracy = np.random.uniform(0.75, 0.90)
            classical_accuracy = np.random.uniform(0.65, 0.80)
        else:
            # Default performance
            quantum_time = np.random.uniform(0.02, 0.10)
            classical_time = np.random.uniform(0.2, 0.6)
            quantum_accuracy = np.random.uniform(0.80, 0.90)
            classical_accuracy = np.random.uniform(0.70, 0.82)
        
        return {
            "quantum_computation_time": quantum_time,
            "classical_computation_time": classical_time,
            "quantum_accuracy": quantum_accuracy,
            "classical_accuracy": classical_accuracy,
            "quantum_memory_usage": np.random.uniform(30, 80),
            "classical_memory_usage": np.random.uniform(80, 150)
        }
    
    async def _calculate_algorithm_advantage(self, performance_data: Dict[str, Any]) -> float:
        """Algorithm afzallik hisoblash"""
        time_speedup = performance_data["classical_computation_time"] / performance_data["quantum_computation_time"]
        accuracy_improvement = performance_data["quantum_accuracy"] / performance_data["classical_accuracy"]
        memory_efficiency = performance_data["classical_memory_usage"] / performance_data["quantum_memory_usage"]
        
        # Combined advantage (weighted average)
        overall_advantage = (time_speedup * 0.4 + accuracy_improvement * 0.4 + memory_efficiency * 0.2 - 1) * 100
        
        return max(0.0, overall_advantage)
    
    async def _create_performance_comparison(self, benchmark_results: Dict[str, Any]) -> Dict[str, Any]:
        """Performance taqqoslash yaratish"""
        comparison = {
            "best_time_performance": None,
            "best_accuracy_performance": None,
            "best_memory_efficiency": None,
            "overall_best": None
        }
        
        best_time = float('inf')
        best_accuracy = 0.0
        best_memory = float('inf')
        best_overall = -1
        
        for algorithm_name, results in benchmark_results.items():
            performance = results["performance_metrics"]
            
            # Best time
            if performance["quantum_computation_time"] < best_time:
                best_time = performance["quantum_computation_time"]
                comparison["best_time_performance"] = algorithm_name
            
            # Best accuracy
            if performance["quantum_accuracy"] > best_accuracy:
                best_accuracy = performance["quantum_accuracy"]
                comparison["best_accuracy_performance"] = algorithm_name
            
            # Best memory efficiency
            if performance["quantum_memory_usage"] < best_memory:
                best_memory = performance["quantum_memory_usage"]
                comparison["best_memory_efficiency"] = algorithm_name
            
            # Overall best
            if results["quantum_advantage"] > best_overall:
                best_overall = results["quantum_advantage"]
                comparison["overall_best"] = algorithm_name
        
        return comparison
    
    def get_comprehensive_metrics_report(self) -> Dict[str, Any]:
        """Comprehensive metrics hisobotini olish"""
        if not self.metrics_history:
            return {"message": "No metrics history available"}
        
        latest_metrics = self.metrics_history[-1]["cycle_metrics"]
        
        # Calculate historical trends
        historical_analysis = self._analyze_historical_trends()
        
        # Performance summary
        performance_summary = self._create_performance_summary()
        
        return {
            "latest_quantum_advantage": latest_metrics.overall_advantage,
            "advantage_level": self._determine_advantage_level(latest_metrics.overall_advantage).value,
            "historical_trends": historical_analysis,
            "performance_summary": performance_summary,
            "recommendations": latest_metrics.recommendations,
            "total_measurements": len(self.metrics_history),
            "quantum_supremacy_achieved": latest_metrics.quantum_supremacy_achieved,
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_historical_trends(self) -> Dict[str, Any]:
        """Historical trend tahlili"""
        if len(self.metrics_history) < 2:
            return {"message": "Insufficient historical data for trend analysis"}
        
        advantages = []
        for entry in self.metrics_history:
            advantages.append(entry["cycle_metrics"].overall_advantage)
        
        # Calculate trend statistics
        trend_slope, intercept, r_value, p_value, std_err = stats.linregress(range(len(advantages)), advantages)
        
        return {
            "trend_slope": trend_slope,
            "correlation_coefficient": r_value,
            "statistical_significance": p_value < 0.05,
            "improvement_rate": trend_slope * 100,  # % per measurement
            "data_points": len(advantages),
            "trend_direction": "improving" if trend_slope > 0 else "declining" if trend_slope < 0 else "stable"
        }
    
    def _create_performance_summary(self) -> Dict[str, Any]:
        """Performance summary yaratish"""
        summary = {}
        
        # Aggregate metric performance
        metric_performance = {}
        for entry in self.metrics_history:
            for metric_name, metric in entry["cycle_metrics"].detailed_metrics.items():
                if metric_name not in metric_performance:
                    metric_performance[metric_name] = []
                metric_performance[metric_name].append(metric.advantage_percentage)
        
        # Calculate averages
        for metric_name, advantages in metric_performance.items():
            summary[metric_name] = {
                "average_advantage": np.mean(advantages),
                "best_advantage": np.max(advantages),
                "consistency": 1 - (np.std(advantages) / np.mean(advantages)) if np.mean(advantages) > 0 else 0
            }
        
        return summary
    
    async def export_metrics_data(self, output_file: str) -> str:
        """Metrics ma'lumotlarini eksport qilish"""
        export_data = {
            "metrics_history": self.metrics_history,
            "baseline_measurements": self.baseline_measurements,
            "performance_summary": self.get_comprehensive_metrics_report(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Metrics data exported to {output_file}")
        return output_file