"""
Quantum Risk Metrics
===================

Quantum-specific risk metrics va measurement tizimi.
Quantum error analysis, fidelity tracking, NISQ device limitations.

Muallif: Quantum Portfolio Team
 Sana: 2025-11-03
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import minimize
import json

@dataclass
class QuantumErrorMetrics:
    """Quantum computation error metrics"""
    gate_fidelity: float
    measurement_fidelity: float
    coherence_time: float
    depolarizing_noise: float
    readoud_error: float
    total_error_rate: float
    
@dataclass
class NISQLimitations:
    """NISQ device limitations"""
    max_qubits: int
    max_gates: int
    max_circuit_depth: int
    coherence_time_limit: float
    gate_time: float
    measurement_time: float
    
@dataclass
class QuantumAdvantageMetrics:
    """Quantum advantage measurement"""
    speedup_ratio: float
    problem_size_threshold: int
    current_advantage: bool
    theoretical_speedup: float
    practical_speedup: float
    error_overhead_factor: float

class QuantumRiskMetrics:
    """Quantum-specific risk metrics and analysis"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # NISQ device specifications (typical current devices)
        self.nisq_limitations = NISQLimitations(
            max_qubits=127,  # IBM Heron
            max_gates=1000,
            max_circuit_depth=200,
            coherence_time_limit=100e-6,  # 100 microseconds
            gate_time=50e-9,  # 50 nanoseconds
            measurement_time=1e-6  # 1 microsecond
        )
        
        # Quantum risk parameters
        self.quantum_risk_params = {
            'error_correction_overhead': 1000,  # Surface code overhead
            'fault_tolerance_threshold': 0.001,  # 0.1% error rate threshold
            'quantum_volume_limit': 128,  # Typical quantum volume
            'max_shots': 8192,  # Maximum measurement shots
            'decoherence_factor': 0.1,  # Typical decoherence rate
        }
        
        # Historical quantum performance data
        self.quantum_performance_history = []
        
    async def calculate_quantum_error_risk(self, qubits_used: int, 
                                         circuit_depth: int,
                                         algorithm_type: str = 'VQE') -> Dict[str, float]:
        """Calculate quantum computation error risk"""
        try:
            # Base error rates for NISQ devices
            base_gate_error = 0.001  # 0.1% per gate
            base_measurement_error = 0.01  # 1% measurement error
            base_depolarizing_error = 0.005  # 0.5% depolarizing error
            
            # Circuit-specific error calculations
            gate_errors = circuit_depth * base_gate_error
            measurement_errors = qubits_used * base_measurement_error
            depolarizing_errors = circuit_depth * base_depolarizing_error * (qubits_used / self.nisq_limitations.max_qubits)
            
            # Algorithm-specific error factors
            algorithm_factors = {
                'VQE': 1.0,  # Baseline
                'QAOA': 1.2,  # More sensitive to errors
                'ANNEALING': 0.8,  # More robust
                'HYBRID': 0.9  # Hybrid approach reduces errors
            }
            
            algorithm_factor = algorithm_factors.get(algorithm_type, 1.0)
            
            # Coherence time risk
            total_coherence_time = circuit_depth * self.nisq_limitations.gate_time
            coherence_risk = min(1.0, total_coherence_time / self.nisq_limitations.coherence_time_limit)
            
            # Overall error rate calculation
            total_error_rate = (gate_errors + measurement_errors + depolarizing_errors) * algorithm_factor
            total_error_rate = min(1.0, total_error_rate + coherence_risk * 0.1)
            
            # Error propagation to portfolio optimization
            portfolio_error_risk = self._calculate_portfolio_error_propagation(total_error_rate)
            
            error_metrics = {
                'total_error_rate': total_error_rate,
                'gate_error_rate': gate_errors,
                'measurement_error_rate': measurement_errors,
                'depolarizing_error_rate': depolarizing_errors,
                'coherence_risk': coherence_risk,
                'algorithm_factor': algorithm_factor,
                'portfolio_error_risk': portfolio_error_risk,
                'qubits_used': qubits_used,
                'circuit_depth': circuit_depth,
                'algorithm_type': algorithm_type
            }
            
            self.logger.info(f"Quantum error risk calculated: {total_error_rate:.4f}")
            return error_metrics
            
        except Exception as e:
            self.logger.error(f"Quantum error risk calculation failed: {str(e)}")
            return {}
            
    def _calculate_portfolio_error_propagation(self, quantum_error_rate: float) -> float:
        """Calculate how quantum errors propagate to portfolio results"""
        # Simplified error propagation model
        # In practice, this would involve detailed circuit analysis
        
        # Portfolio optimization is sensitive to weight accuracy
        weight_error_amplification = 5.0  # 5x amplification factor
        risk_calculation_error = quantum_error_rate * weight_error_amplification
        
        # Expected value calculations more sensitive than variance
        expected_value_error = risk_calculation_error * 2.0
        variance_error = risk_calculation_error * 1.5
        
        # Overall portfolio error risk
        portfolio_error = np.sqrt(expected_value_error**2 + variance_error**2)
        
        return min(1.0, portfolio_error)
        
    async def assess_nisq_feasibility(self, problem_size: int, 
                                    algorithm_type: str) -> Dict[str, Any]:
        """Assess NISQ device feasibility for problem"""
        try:
            # Estimate required resources
            qubits_needed = self._estimate_qubits_needed(problem_size, algorithm_type)
            gates_needed = self._estimate_gates_needed(problem_size, algorithm_type)
            circuit_depth_needed = self._estimate_circuit_depth(problem_size, algorithm_type)
            
            # Check NISQ limitations
            feasibility_checks = {
                'qubits_feasible': qubits_needed <= self.nisq_limitations.max_qubits,
                'gates_feasible': gates_needed <= self.nisq_limitations.max_gates,
                'circuit_depth_feasible': circuit_depth_needed <= self.nisq_limitations.max_circuit_depth,
                'coherence_feasible': self._check_coherence_feasibility(circuit_depth_needed),
                'overall_feasible': True  # Will be updated below
            }
            
            # Calculate resource utilization
            resource_utilization = {
                'qubits_utilization': qubits_needed / self.nisq_limitations.max_qubits,
                'gates_utilization': gates_needed / self.nisq_limitations.max_gates,
                'depth_utilization': circuit_depth_needed / self.nisq_limitations.max_circuit_depth,
                'coherence_utilization': self._calculate_coherence_utilization(circuit_depth_needed)
            }
            
            # Overall feasibility
            overall_feasible = all([
                feasibility_checks['qubits_feasible'],
                feasibility_checks['gates_feasible'], 
                feasibility_checks['circuit_depth_feasible'],
                feasibility_checks['coherence_feasible']
            ])
            feasibility_checks['overall_feasible'] = overall_feasible
            
            # Recommended approach
            recommended_approach = self._recommend_quantum_approach(
                qubits_needed, gates_needed, circuit_depth_needed, algorithm_type
            )
            
            # Risk assessment
            risk_assessment = {
                'high_risk_factors': [],
                'medium_risk_factors': [],
                'risk_score': 0.0
            }
            
            # Identify risk factors
            if resource_utilization['qubits_utilization'] > 0.8:
                risk_assessment['high_risk_factors'].append('qubit_resource_constrained')
            elif resource_utilization['qubits_utilization'] > 0.6:
                risk_assessment['medium_risk_factors'].append('qubit_resource_high')
                
            if resource_utilization['gates_utilization'] > 0.8:
                risk_assessment['high_risk_factors'].append('gate_resource_constrained')
            elif resource_utilization['gates_utilization'] > 0.6:
                risk_assessment['medium_risk_factors'].append('gate_resource_high')
                
            if resource_utilization['depth_utilization'] > 0.8:
                risk_assessment['high_risk_factors'].append('circuit_depth_limited')
            elif resource_utilization['depth_utilization'] > 0.6:
                risk_assessment['medium_risk_factors'].append('circuit_depth_high')
                
            # Calculate overall risk score
            risk_score = (
                len(risk_assessment['high_risk_factors']) * 30 +
                len(risk_assessment['medium_risk_factors']) * 15
            )
            risk_assessment['risk_score'] = min(100, risk_score)
            
            feasibility_assessment = {
                'problem_size': problem_size,
                'algorithm_type': algorithm_type,
                'required_resources': {
                    'qubits': qubits_needed,
                    'gates': gates_needed,
                    'circuit_depth': circuit_depth_needed
                },
                'feasibility_checks': feasibility_checks,
                'resource_utilization': resource_utilization,
                'recommended_approach': recommended_approach,
                'risk_assessment': risk_assessment,
                'nisq_device_ready': overall_feasible,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"NISQ feasibility assessed for problem size {problem_size}: {'feasible' if overall_feasible else 'not feasible'}")
            return feasibility_assessment
            
        except Exception as e:
            self.logger.error(f"NISQ feasibility assessment failed: {str(e)}")
            return {}
            
    def _estimate_qubits_needed(self, problem_size: int, algorithm_type: str) -> int:
        """Estimate qubits needed for problem"""
        if algorithm_type == 'VQE':
            # VQE typically needs: asset qubits + constraint qubits + objective qubits + ancilla
            asset_qubits = max(4, int(np.log2(problem_size)) + 1)
            constraint_qubits = int(np.log2(problem_size)) + 1
            objective_qubits = 6
            ancilla_qubits = asset_qubits + constraint_qubits + 2
            return asset_qubits + constraint_qubits + objective_qubits + ancilla_qubits
            
        elif algorithm_type == 'QAOA':
            # QAOA needs encoding qubits + parameter qubits
            encoding_qubits = max(3, int(np.log2(problem_size)))
            parameter_qubits = int(np.log2(problem_size)) + 1
            return encoding_qubits + parameter_qubits
            
        elif algorithm_type == 'ANNEALING':
            # Annealing typically more efficient in qubit usage
            return max(2, int(np.log2(problem_size)) + 1)
            
        else:
            return max(4, problem_size)
            
    def _estimate_gates_needed(self, problem_size: int, algorithm_type: str) -> int:
        """Estimate quantum gates needed"""
        if algorithm_type == 'VQE':
            # VQE: preparation gates + variational gates + measurement gates
            prep_gates = problem_size * 2
            var_gates = problem_size ** 2
            measure_gates = problem_size
            return prep_gates + var_gates + measure_gates
            
        elif algorithm_type == 'QAOA':
            # QAOA: mixing + problem Hamiltonians
            return problem_size * int(np.log2(problem_size)) * 2
            
        elif algorithm_type == 'ANNEALING':
            # Annealing typically has lower gate count
            return int(problem_size * 1.5)
            
        else:
            return problem_size * 2
            
    def _estimate_circuit_depth(self, problem_size: int, algorithm_type: str) -> int:
        """Estimate circuit depth"""
        if algorithm_type == 'VQE':
            # VQE depth scales with problem complexity
            return max(10, int(np.log2(problem_size)) * 5)
            
        elif algorithm_type == 'QAOA':
            # QAOA depth proportional to p parameter
            return int(np.log2(problem_size)) * 10
            
        elif algorithm_type == 'ANNEALING':
            # Annealing has different depth metric
            return int(np.log2(problem_size)) * 2
            
        else:
            return problem_size
            
    def _check_coherence_feasibility(self, circuit_depth: int) -> bool:
        """Check if circuit depth is within coherence limits"""
        total_gate_time = circuit_depth * self.nisq_limitations.gate_time
        return total_gate_time < self.nisq_limitations.coherence_time_limit
        
    def _calculate_coherence_utilization(self, circuit_depth: int) -> float:
        """Calculate coherence time utilization"""
        total_gate_time = circuit_depth * self.nisq_limitations.gate_time
        return total_gate_time / self.nisq_limitations.coherence_time_limit
        
    def _recommend_quantum_approach(self, qubits: int, gates: int, 
                                  depth: int, algorithm_type: str) -> Dict[str, str]:
        """Recommend quantum approach based on constraints"""
        recommendations = {
            'primary_approach': '',
            'fallback_approach': '',
            'optimization_suggestions': []
        }
        
        if qubits > self.nisq_limitations.max_qubits * 0.8:
            recommendations['primary_approach'] = 'Classical optimization'
            recommendations['fallback_approach'] = 'Hybrid quantum-classical'
            recommendations['optimization_suggestions'].append('Reduce problem size or use problem decomposition')
            
        elif gates > self.nisq_limitations.max_gates * 0.8:
            recommendations['primary_approach'] = f'{algorithm_type} with gate optimization'
            recommendations['fallback_approach'] = 'Variational circuit optimization'
            recommendations['optimization_suggestions'].append('Use more efficient gate sets')
            
        elif depth > self.nisq_limitations.max_circuit_depth * 0.8:
            recommendations['primary_approach'] = f'{algorithm_type} with depth reduction'
            recommendations['fallback_approach'] = 'Shallow circuit variants'
            recommendations['optimization_suggestions'].append('Use shallower circuit architectures')
            
        else:
            recommendations['primary_approach'] = f'Direct {algorithm_type}'
            recommendations['fallback_approach'] = f'Optimized {algorithm_type}'
            
        return recommendations
        
    async def calculate_quantum_advantage(self, problem_sizes: List[int],
                                        algorithm_type: str) -> Dict[str, Any]:
        """Calculate quantum advantage metrics"""
        try:
            advantage_analysis = {}
            
            for size in problem_sizes:
                # Classical complexity estimation
                classical_time = self._estimate_classical_complexity(size)
                
                # Quantum complexity estimation  
                quantum_time = await self._estimate_quantum_complexity(size, algorithm_type)
                
                # Error overhead calculation
                error_overhead = await self._calculate_error_overhead(size, algorithm_type)
                
                # Practical quantum time (including error correction)
                practical_quantum_time = quantum_time * (1 + error_overhead)
                
                # Speedup calculation
                theoretical_speedup = classical_time / quantum_time if quantum_time > 0 else 0
                practical_speedup = classical_time / practical_quantum_time if practical_quantum_time > 0 else 0
                
                # Quantum advantage assessment
                advantage_achieved = practical_speedup > 1.2  # 20% threshold for advantage
                
                advantage_analysis[f'size_{size}'] = {
                    'problem_size': size,
                    'classical_time': classical_time,
                    'quantum_time': quantum_time,
                    'practical_quantum_time': practical_quantum_time,
                    'error_overhead': error_overhead,
                    'theoretical_speedup': theoretical_speedup,
                    'practical_speedup': practical_speedup,
                    'advantage_achieved': advantage_achieved,
                    'breakeven_point': theoretical_speedup >= 1.0,
                    'quantum_readiness': advantage_achieved and size <= self.nisq_limitations.max_qubits
                }
                
            # Overall quantum advantage assessment
            all_advantages = [result['advantage_achieved'] for result in advantage_analysis.values()]
            all_speedups = [result['practical_speedup'] for result in advantage_analysis.values()]
            
            overall_assessment = {
                'sizes_with_advantage': sum(all_advantages),
                'average_speedup': np.mean(all_speedups) if all_speedups else 0,
                'max_speedup': max(all_speedups) if all_speedups else 0,
                'min_speedup': min(all_speedups) if all_speedups else 0,
                'optimal_size_range': self._find_optimal_size_range(advantage_analysis),
                'quantum_readiness_score': len([s for s in all_advantages if s]) / len(all_advantages) if all_advantages else 0
            }
            
            quantum_advantage_metrics = QuantumAdvantageMetrics(
                speedup_ratio=overall_assessment['average_speedup'],
                problem_size_threshold=overall_assessment['optimal_size_range'][1],
                current_advantage=overall_assessment['quantum_readiness_score'] > 0.5,
                theoretical_speedup=overall_assessment['max_speedup'],
                practical_speedup=overall_assessment['average_speedup'],
                error_overhead_factor=0.2  # Typical error overhead
            )
            
            self.logger.info(f"Quantum advantage calculated for {algorithm_type}: {overall_assessment['average_speedup']:.2f}x")
            
            return {
                'detailed_analysis': advantage_analysis,
                'overall_assessment': overall_assessment,
                'quantum_advantage_metrics': {
                    'speedup_ratio': quantum_advantage_metrics.speedup_ratio,
                    'problem_size_threshold': quantum_advantage_metrics.problem_size_threshold,
                    'current_advantage': quantum_advantage_metrics.current_advantage,
                    'theoretical_speedup': quantum_advantage_metrics.theoretical_speedup,
                    'practical_speedup': quantum_advantage_metrics.practical_speedup,
                    'error_overhead_factor': quantum_advantage_metrics.error_overhead_factor
                },
                'recommendations': self._generate_quantum_recommendations(advantage_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Quantum advantage calculation failed: {str(e)}")
            return {}
            
    def _estimate_classical_complexity(self, problem_size: int) -> float:
        """Estimate classical computation complexity (time in seconds)"""
        # Mean-variance optimization: O(n^3)
        operations = problem_size ** 3
        time_per_operation = 1e-9  # 1 nanosecond per operation
        return operations * time_per_operation
        
    async def _estimate_quantum_complexity(self, problem_size: int, 
                                         algorithm_type: str) -> float:
        """Estimate quantum computation complexity"""
        # NISQ device operation times
        gate_operation_time = self.nisq_limitations.gate_time
        measurement_time = self.nisq_limitations.measurement_time
        
        if algorithm_type == 'VQE':
            circuit_gates = problem_size ** 2
            iterations = 100  # Typical VQE iterations
            shots_per_iteration = 1000
            
            total_time = (circuit_gates * gate_operation_time + measurement_time) * iterations * shots_per_iteration
            return total_time
            
        elif algorithm_type == 'QAOA':
            circuit_gates = problem_size * int(np.log2(problem_size))
            p_layers = 5  # QAOA parameter p
            shots = 1000
            
            total_time = (circuit_gates * gate_operation_time + measurement_time) * p_layers * shots
            return total_time
            
        elif algorithm_type == 'ANNEALING':
            # Annealing time (simplified)
            annealing_time = 1e-6  # 1 microsecond annealing
            reads = 1000  # Number of reads
            return annealing_time * reads
            
        else:
            # Default estimation
            circuit_gates = problem_size * 2
            total_time = circuit_gates * gate_operation_time * 1000
            return total_time
            
    async def _calculate_error_overhead(self, problem_size: int, 
                                      algorithm_type: str) -> float:
        """Calculate error correction overhead"""
        # Error rates
        base_error_rate = 0.001  # 0.1% per gate
        
        if algorithm_type == 'VQE':
            circuit_gates = problem_size ** 2
            total_errors = circuit_gates * base_error_rate
            
        elif algorithm_type == 'QAOA':
            circuit_gates = problem_size * int(np.log2(problem_size))
            total_errors = circuit_gates * base_error_rate
            
        elif algorithm_type == 'ANNEALING':
            total_errors = base_error_rate * 10  # Simplified for annealing
            
        else:
            circuit_gates = problem_size * 2
            total_errors = circuit_gates * base_error_rate
            
        # Error correction overhead (surface code)
        # Typically requires 100-1000x more resources
        error_correction_overhead = self.quantum_risk_params['error_correction_overhead']
        
        return min(10.0, total_errors * error_correction_overhead)
        
    def _find_optimal_size_range(self, advantage_analysis: Dict[str, Any]) -> Tuple[int, int]:
        """Find optimal problem size range for quantum advantage"""
        # Filter sizes with advantage and quantum readiness
        viable_sizes = []
        
        for size_key, result in advantage_analysis.items():
            if (result['advantage_achieved'] and 
                result['quantum_readiness'] and 
                result['practical_speedup'] > 1.5):  # Minimum 50% speedup
                viable_sizes.append(result['problem_size'])
                
        if viable_sizes:
            return (min(viable_sizes), max(viable_sizes))
        else:
            # Return typical NISQ range
            return (5, 20)
            
    def _generate_quantum_recommendations(self, advantage_analysis: Dict[str, Any]) -> List[str]:
        """Generate quantum computing recommendations"""
        recommendations = []
        
        # Analyze overall results
        all_sizes = list(advantage_analysis.keys())
        
        if not all_sizes:
            return ["Insufficient data for recommendations"]
            
        # Size-based recommendations
        max_size_with_advantage = max([
            result['problem_size'] for result in advantage_analysis.values()
            if result['advantage_achieved']
        ], default=0)
        
        if max_size_with_advantage > 0:
            recommendations.append(f"Quantum advantage achievable up to portfolio size {max_size_with_advantage}")
        else:
            recommendations.append("Quantum advantage not currently achievable for portfolio optimization")
            
        # Error handling recommendations
        high_overhead_sizes = [
            result['problem_size'] for result in advantage_analysis.values()
            if result['error_overhead'] > 2.0
        ]
        
        if high_overhead_sizes:
            recommendations.append(f"High error overhead for sizes {high_overhead_sizes} - consider error mitigation")
            
        # Algorithm recommendations
        best_speedup = max([
            result['practical_speedup'] for result in advantage_analysis.values()
        ], default=0)
        
        if best_speedup > 2.0:
            recommendations.append("Strong quantum advantage potential - prioritize quantum implementation")
        elif best_speedup > 1.2:
            recommendations.append("Moderate quantum advantage - consider hybrid approaches")
        else:
            recommendations.append("Limited quantum advantage - focus on classical optimization")
            
        # NISQ limitations
        recommendations.append("Consider NISQ device limitations when implementing quantum algorithms")
        recommendations.append("Implement error mitigation and noise reduction techniques")
        
        return recommendations
        
    async def track_quantum_performance(self, portfolio_id: str, 
                                      quantum_metrics: Dict[str, Any],
                                      performance_results: Dict[str, float]):
        """Track quantum computation performance over time"""
        try:
            performance_record = {
                'portfolio_id': portfolio_id,
                'timestamp': datetime.now().isoformat(),
                'quantum_metrics': quantum_metrics.copy(),
                'performance_results': performance_results.copy(),
                'analysis_timestamp': datetime.now()
            }
            
            self.quantum_performance_history.append(performance_record)
            
            # Keep only recent history
            cutoff_time = datetime.now() - timedelta(days=30)
            self.quantum_performance_history = [
                record for record in self.quantum_performance_history
                if datetime.fromisoformat(record['timestamp']) > cutoff_time
            ]
            
            self.logger.info(f"Quantum performance tracked for {portfolio_id}")
            
        except Exception as e:
            self.logger.error(f"Quantum performance tracking failed: {str(e)}")
            
    def get_quantum_risk_report(self, portfolio_id: str = None) -> Dict[str, Any]:
        """Generate comprehensive quantum risk report"""
        try:
            # Filter by portfolio if specified
            history = self.quantum_performance_history
            if portfolio_id:
                history = [record for record in history if record['portfolio_id'] == portfolio_id]
                
            if not history:
                return {"error": "No quantum performance data available"}
                
            # Analyze historical performance
            error_rates = []
            fidelity_scores = []
            computation_times = []
            
            for record in history:
                qm = record['quantum_metrics']
                error_rates.append(qm.get('total_error_rate', 0))
                fidelity_scores.append(1 - qm.get('total_error_rate', 0))  # Simplified fidelity
                computation_times.append(record['performance_results'].get('computation_time', 0))
                
            # Calculate summary statistics
            risk_summary = {
                'average_error_rate': np.mean(error_rates) if error_rates else 0,
                'max_error_rate': np.max(error_rates) if error_rates else 0,
                'error_rate_trend': self._calculate_trend(error_rates),
                'average_fidelity': np.mean(fidelity_scores) if fidelity_scores else 0,
                'average_computation_time': np.mean(computation_times) if computation_times else 0,
                'performance_consistency': 1 - (np.std(computation_times) / np.mean(computation_times)) if computation_times and np.mean(computation_times) > 0 else 0
            }
            
            # Risk assessment
            risk_level = self._assess_quantum_risk_level(risk_summary)
            
            # Generate recommendations
            recommendations = self._generate_quantum_risk_recommendations(risk_summary)
            
            return {
                'portfolio_id': portfolio_id,
                'report_timestamp': datetime.now().isoformat(),
                'data_points': len(history),
                'risk_summary': risk_summary,
                'risk_level': risk_level,
                'recommendations': recommendations,
                'nisq_device_recommendations': self._get_nisq_recommendations(),
                'quantum_readiness': self._assess_quantum_readiness(risk_summary)
            }
            
        except Exception as e:
            self.logger.error(f"Quantum risk report generation failed: {str(e)}")
            return {}
            
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for values"""
        if len(values) < 2:
            return "insufficient_data"
            
        # Simple linear trend calculation
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.001:
            return "increasing"
        elif slope < -0.001:
            return "decreasing"
        else:
            return "stable"
            
    def _assess_quantum_risk_level(self, risk_summary: Dict[str, float]) -> str:
        """Assess overall quantum risk level"""
        error_rate = risk_summary.get('average_error_rate', 0)
        fidelity = risk_summary.get('average_fidelity', 1.0)
        
        if error_rate > 0.05 or fidelity < 0.90:
            return "HIGH"
        elif error_rate > 0.02 or fidelity < 0.95:
            return "MEDIUM"
        else:
            return "LOW"
            
    def _generate_quantum_risk_recommendations(self, risk_summary: Dict[str, float]) -> List[str]:
        """Generate quantum risk management recommendations"""
        recommendations = []
        
        error_rate = risk_summary.get('average_error_rate', 0)
        fidelity = risk_summary.get('average_fidelity', 1.0)
        trend = risk_summary.get('error_rate_trend', 'stable')
        
        # Error rate recommendations
        if error_rate > 0.05:
            recommendations.append("High quantum error rates detected - implement advanced error mitigation")
        elif error_rate > 0.02:
            recommendations.append("Moderate quantum error rates - consider hybrid quantum-classical approaches")
            
        # Fidelity recommendations
        if fidelity < 0.90:
            recommendations.append("Low quantum fidelity - consider NISQ device with better coherence")
        elif fidelity < 0.95:
            recommendations.append("Moderate quantum fidelity - optimize circuit design and parameters")
            
        # Trend recommendations
        if trend == "increasing":
            recommendations.append("Quantum error rates are increasing - check device calibration and noise levels")
        elif trend == "decreasing":
            recommendations.append("Quantum performance improving - consider scaling up quantum usage")
            
        # General recommendations
        recommendations.append("Implement quantum error correction for production workloads")
        recommendations.append("Monitor quantum device calibration regularly")
        recommendations.append("Use quantum classical hybrid algorithms for better reliability")
        
        return recommendations
        
    def _get_nisq_recommendations(self) -> List[str]:
        """Get NISQ device recommendations"""
        return [
            f"Current NISQ devices limited to {self.nisq_limitations.max_qubits} qubits",
            f"Maximum circuit depth: {self.nisq_limitations.max_circuit_depth} gates",
            f"Coherence time limit: {self.nisq_limitations.coherence_time_limit * 1e6:.1f} microseconds",
            "Consider fault-tolerant quantum computers for larger problems",
            "Use error mitigation techniques for NISQ-era quantum computing"
        ]
        
    def _assess_quantum_readiness(self, risk_summary: Dict[str, float]) -> Dict[str, Any]:
        """Assess quantum readiness for portfolio optimization"""
        # Quantum readiness criteria
        criteria = {
            'error_rate_acceptable': risk_summary.get('average_error_rate', 1) < 0.02,
            'fidelity_sufficient': risk_summary.get('average_fidelity', 0) > 0.95,
            'performance_consistent': risk_summary.get('performance_consistency', 0) > 0.7,
            'problem_size_suitable': True  # Would check against problem sizes
        }
        
        readiness_score = sum(criteria.values()) / len(criteria) * 100
        
        return {
            'readiness_score': readiness_score,
            'criteria_met': criteria,
            'readiness_level': self._categorize_readiness(readiness_score),
            'quantum_advantage_potential': readiness_score > 70
        }
        
    def _categorize_readiness(self, score: float) -> str:
        """Categorize quantum readiness level"""
        if score >= 80:
            return "HIGH"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "LOW"
        else:
            return "NOT_READY"

# Usage example
async def example_quantum_risk_metrics():
    """Example quantum risk metrics usage"""
    # Create quantum risk metrics calculator
    qrm = QuantumRiskMetrics()
    
    # Calculate quantum error risk
    error_metrics = await qrm.calculate_quantum_error_risk(
        qubits_used=20,
        circuit_depth=50,
        algorithm_type='VQE'
    )
    
    print("Quantum Error Risk Analysis:")
    print(f"- Total Error Rate: {error_metrics.get('total_error_rate', 0):.4f}")
    print(f"- Portfolio Error Risk: {error_metrics.get('portfolio_error_risk', 0):.4f}")
    print(f"- Algorithm Factor: {error_metrics.get('algorithm_factor', 1):.2f}")
    
    # Assess NISQ feasibility
    feasibility = await qrm.assess_nisq_feasibility(
        problem_size=50,
        algorithm_type='VQE'
    )
    
    print(f"\\nNISQ Feasibility Assessment:")
    print(f"- Overall Feasible: {feasibility.get('nisq_device_ready', False)}")
    print(f"- Risk Score: {feasibility.get('risk_assessment', {}).get('risk_score', 0)}")
    print(f"- Recommended Approach: {feasibility.get('recommended_approach', {}).get('primary_approach', 'Unknown')}")
    
    # Calculate quantum advantage
    problem_sizes = [10, 20, 50, 100]
    advantage = await qrm.calculate_quantum_advantage(problem_sizes, 'VQE')
    
    print(f"\\nQuantum Advantage Analysis:")
    print(f"- Average Speedup: {advantage.get('overall_assessment', {}).get('average_speedup', 0):.2f}x")
    print(f"- Optimal Size Range: {advantage.get('overall_assessment', {}).get('optimal_size_range', (0, 0))}")
    print(f"- Quantum Readiness Score: {advantage.get('overall_assessment', {}).get('quantum_readiness_score', 0):.1%}")
    
    # Generate quantum risk report
    qrm.quantum_performance_history.append({
        'portfolio_id': 'test_portfolio',
        'timestamp': datetime.now().isoformat(),
        'quantum_metrics': error_metrics,
        'performance_results': {'computation_time': 2.5, 'accuracy': 0.95}
    })
    
    risk_report = qrm.get_quantum_risk_report('test_portfolio')
    print(f"\\nQuantum Risk Report:")
    print(f"- Risk Level: {risk_report.get('risk_level', 'Unknown')}")
    print(f"- Quantum Readiness: {risk_report.get('quantum_readiness', {}).get('readiness_level', 'Unknown')}")

if __name__ == "__main__":
    asyncio.run(example_quantum_risk_metrics())