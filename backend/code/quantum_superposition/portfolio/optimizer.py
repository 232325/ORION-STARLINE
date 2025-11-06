"""
Quantum Portfolio Optimizer
===========================

Quantum algorithms asosida portfolio optimizatsiya.
"""

import numpy as np
import cmath
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from scipy.optimize import minimize, differential_evolution
from scipy.linalg import norm, eigh
import matplotlib.pyplot as plt

try:
    from ..core.quantum_state import QuantumPortfolioState
    from ..models.quantum_portfolio import QuantumPortfolioModel
    from ..algorithms.vqe import QuantumVQE
    from ..algorithms.qaoa import QuantumQAOA
except ImportError:
    # Fallback for standalone execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from core.quantum_state import QuantumPortfolioState
    from models.quantum_portfolio import QuantumPortfolioModel
    from algorithms.vqe import QuantumVQE
    from algorithms.qaoa import QuantumQAOA


@dataclass
class OptimizerConfig:
    """Optimizer konfiguratsiya parametrlari"""
    algorithm: str = 'quantum'  # 'quantum', 'classical', 'hybrid'
    target_return: float = 0.12  # Maqsad daromad
    risk_tolerance: float = 0.15  # Risk tolerance
    max_iterations: int = 1000  # Maksimal iterations
    convergence_threshold: float = 1e-6  # Konvergentsiya threshold
    quantum_algorithm: str = 'vqe'  # 'vqe', 'qaoa'
    constraint_weights: Dict[str, float] = None  # Weight cheklovlari


class QuantumPortfolioOptimizer:
    """
    Quantum Portfolio Optimizer
    
    Quantum algoritmlar asosida portfolio optimizatsiya.
    """
    
    def __init__(self, config: OptimizerConfig = None):
        self.config = config or OptimizerConfig()
        
        # Optimization components
        self.quantum_portfolio_model = QuantumPortfolioModel()
        self.quantum_optimizer = None
        self.classical_optimizer = None
        
        # Portfolio state
        self.portfolio_state = None
        self.optimization_history = []
        self.algorithm_comparison = {}
        
    def initialize_portfolio(self, assets: List[str], 
                           returns_data: np.ndarray = None,
                           covariance_matrix: np.ndarray = None) -> QuantumPortfolioState:
        """
        Portfolio'ni optimizatsiya uchun tayyorlash
        
        Args:
            assets: Portfolio assetlari
            returns_data: Returns ma'lumotlari
            covariance_matrix: Covariance matrix
        
        Returns:
            Initialized portfolio state
        """
        if returns_data is not None:
            # Returns ma'lumotlari asosida initialize
            if len(returns_data) != len(assets):
                raise ValueError("Returns data uzunligi assetlar soniga mos emas")
        
        self.portfolio_state = self.quantum_portfolio_model.initialize_portfolio(
            assets, returns_data
        )
        
        # Store additional data for optimization
        self._store_optimization_data(returns_data, covariance_matrix)
        
        return self.portfolio_state
    
    def optimize(self, optimization_method: str = None) -> Dict:
        """
        Portfolio optimizatsiya
        
        Args:
            optimization_method: Optimization usuli
        
        Returns:
            Optimization natijalari
        """
        if optimization_method is None:
            optimization_method = self.config.algorithm
        
        if self.portfolio_state is None:
            raise ValueError("Portfolio initialize qilinmagan")
        
        print(f"Starting {optimization_method} optimization...")
        
        if optimization_method == 'quantum':
            return self._quantum_optimization()
        elif optimization_method == 'classical':
            return self._classical_optimization()
        elif optimization_method == 'hybrid':
            return self._hybrid_optimization()
        else:
            raise ValueError(f"Noma'lum optimization method: {optimization_method}")
    
    def _quantum_optimization(self) -> Dict:
        """Quantum optimization algoritmi"""
        returns_data = getattr(self, '_returns_data', None)
        covariance_matrix = getattr(self, '_covariance_matrix', None)
        
        if self.config.quantum_algorithm == 'vqe':
            return self._vqe_optimization(returns_data, covariance_matrix)
        elif self.config.quantum_algorithm == 'qaoa':
            return self._qaoa_optimization(returns_data, covariance_matrix)
        else:
            raise ValueError(f"Noma'lum quantum algorithm: {self.config.quantum_algorithm}")
    
    def _vqe_optimization(self, returns_data: np.ndarray, 
                         covariance_matrix: np.ndarray = None) -> Dict:
        """VQE optimization"""
        # Initialize VQE
        vqe_config = self._create_vqe_config()
        vqe_optimizer = QuantumVQE(vqe_config)
        
        # Setup problem
        vqe_optimizer.setup_portfolio_problem(
            self.portfolio_state, returns_data, covariance_matrix
        )
        
        # Optimize
        vqe_results = vqe_optimizer.optimize()
        
        if vqe_results['success']:
            # Update portfolio state
            optimal_weights = vqe_results['portfolio_weights']
            self.portfolio_state.set_portfolio_state(optimal_weights)
            
            # Calculate metrics
            expected_return = self.portfolio_state.get_expected_return(returns_data)
            risk = self.portfolio_state.get_risk(covariance_matrix) if covariance_matrix is not None \
                   else np.sqrt(np.sum(optimal_weights**2 * 0.15**2))
            
            quantum_metrics = {
                'vqe_energy': vqe_results['optimal_energy'],
                'quantum_coherence': 1 - np.sum(optimal_weights**4),
                'entanglement_strength': self._calculate_entanglement_strength(optimal_weights),
                'optimization_success': vqe_results['success']
            }
            
            optimization_result = {
                'method': 'VQE',
                'optimal_weights': optimal_weights,
                'expected_return': expected_return,
                'risk': risk,
                'sharpe_ratio': expected_return / risk if risk > 0 else 0,
                'quantum_metrics': quantum_metrics,
                'vqe_details': vqe_results,
                'algorithm_convergence': vqe_optimizer.analyze_optimization_convergence()
            }
        else:
            optimization_result = {
                'method': 'VQE',
                'success': False,
                'error': vqe_results.get('error', 'VQE optimization failed')
            }
        
        self.optimization_history.append(optimization_result)
        return optimization_result
    
    def _qaoa_optimization(self, returns_data: np.ndarray,
                         covariance_matrix: np.ndarray = None) -> Dict:
        """QAOA optimization"""
        # Initialize QAOA
        qaoa_config = self._create_qaoa_config()
        qaoa_optimizer = QuantumQAOA(qaoa_config)
        
        # Setup problem
        qaoa_optimizer.setup_portfolio_problem(
            self.portfolio_state, returns_data, covariance_matrix
        )
        
        # Optimize
        qaoa_results = qaoa_optimizer.optimize()
        
        if qaoa_results['success']:
            # Extract optimal weights
            portfolio_weights_result = qaoa_results['portfolio_weights']
            optimal_weights = portfolio_weights_result.get('best_weights', np.ones(len(self.portfolio_state.assets)) / len(self.portfolio_state.assets))
            
            # Update portfolio state
            self.portfolio_state.set_portfolio_state(optimal_weights)
            
            # Calculate metrics
            expected_return = self.portfolio_state.get_expected_return(returns_data)
            risk = self.portfolio_state.get_risk(covariance_matrix) if covariance_matrix is not None \
                   else np.sqrt(np.sum(optimal_weights**2 * 0.15**2))
            
            quantum_metrics = {
                'qaoa_energy': qaoa_results['optimal_energy'],
                'approximation_ratio': qaoa_optimizer.analyze_approximation_ratio()['approximation_ratio'],
                'measurement_entropy': portfolio_weights_result.get('measurement_entropy', 0),
                'optimization_success': qaoa_results['success']
            }
            
            optimization_result = {
                'method': 'QAOA',
                'optimal_weights': optimal_weights,
                'expected_return': expected_return,
                'risk': risk,
                'sharpe_ratio': expected_return / risk if risk > 0 else 0,
                'quantum_metrics': quantum_metrics,
                'qaoa_details': qaoa_results,
                'algorithm_analysis': qaoa_optimizer.analyze_approximation_ratio()
            }
        else:
            optimization_result = {
                'method': 'QAOA',
                'success': False,
                'error': qaoa_results.get('error', 'QAOA optimization failed')
            }
        
        self.optimization_history.append(optimization_result)
        return optimization_result
    
    def _classical_optimization(self) -> Dict:
        """Classical optimization algoritmi"""
        returns_data = getattr(self, '_returns_data', None)
        covariance_matrix = getattr(self, '_covariance_matrix', None)
        
        # Classical optimization using quantum portfolio model
        classical_results = self.quantum_portfolio_model.quantum_optimization(
            returns_data, covariance_matrix
        )
        
        if classical_results['best_result']['success']:
            optimal_weights = classical_results['best_result']['optimal_weights']
            
            # Update portfolio state
            self.portfolio_state.set_portfolio_state(optimal_weights)
            
            optimization_result = {
                'method': 'Classical',
                'optimal_weights': optimal_weights,
                'expected_return': classical_results['best_result']['expected_return'],
                'risk': classical_results['best_result']['quantum_risk'],
                'sharpe_ratio': classical_results['best_result']['sharpe_ratio'],
                'optimization_details': classical_results['best_result'],
                'classical_metrics': {
                    'optimization_method': classical_results['best_method'],
                    'convergence_iterations': classical_results['quantum_metrics'].get('convergence_iterations', 0)
                }
            }
        else:
            optimization_result = {
                'method': 'Classical',
                'success': False,
                'error': 'Classical optimization failed'
            }
        
        self.optimization_history.append(optimization_result)
        return optimization_result
    
    def _hybrid_optimization(self) -> Dict:
        """Hybrid optimization (Classical + Quantum)"""
        returns_data = getattr(self, '_returns_data', None)
        covariance_matrix = getattr(self, '_covariance_matrix', None)
        
        # First: Classical optimization
        print("Starting classical optimization...")
        classical_result = self._classical_optimization()
        
        # Second: Quantum optimization with classical initialization
        print("Starting quantum optimization...")
        quantum_result = self._quantum_optimization()
        
        # Compare results
        comparison = self._compare_optimization_results(classical_result, quantum_result)
        
        # Select best result
        best_result = classical_result if comparison['classical_better'] else quantum_result
        
        hybrid_result = {
            'method': 'Hybrid',
            'best_result': best_result,
            'comparison': comparison,
            'classical_result': classical_result,
            'quantum_result': quantum_result,
            'hybrid_advantage': comparison.get('quantum_advantage', 0)
        }
        
        self.optimization_history.append(hybrid_result)
        return hybrid_result
    
    def compare_algorithms(self) -> Dict:
        """Turli algoritmlarni taqqoslash"""
        if len(self.optimization_history) < 2:
            return {'error': 'Kamida 2 ta optimization history kerak'}
        
        results = {}
        
        # Separate by method
        for result in self.optimization_history:
            method = result['method']
            if method not in results:
                results[method] = []
            results[method].append(result)
        
        # Compare performance metrics
        comparison = {}
        
        for method, method_results in results.items():
            if method_results:
                latest_result = method_results[-1]
                
                comparison[method] = {
                    'latest_sharpe_ratio': latest_result.get('sharpe_ratio', 0),
                    'latest_expected_return': latest_result.get('expected_return', 0),
                    'latest_risk': latest_result.get('risk', 0),
                    'success_rate': sum(1 for r in method_results if r.get('success', False)) / len(method_results),
                    'avg_sharpe_ratio': np.mean([r.get('sharpe_ratio', 0) for r in method_results if 'sharpe_ratio' in r])
                }
        
        # Find best algorithm
        best_method = max(comparison.keys(), 
                         key=lambda k: comparison[k]['avg_sharpe_ratio'])
        
        self.algorithm_comparison = {
            'comparison_results': comparison,
            'best_algorithm': best_method,
            'best_performance': comparison[best_method],
            'recommendation': f"Use {best_method} algorithm for best performance"
        }
        
        return self.algorithm_comparison
    
    def _create_vqe_config(self) -> 'VQEConfig':
        """VQE konfiguratsiya yaratish"""
        from ..algorithms.vqe import VQEConfig
        
        return VQEConfig(
            n_qubits=min(len(self.portfolio_state.assets), 6),
            n_layers=3,
            max_iterations=self.config.max_iterations,
            tolerance=self.config.convergence_threshold,
            optimization_method='COBYLA'
        )
    
    def _create_qaoa_config(self) -> 'QAOAConfig':
        """QAOA konfiguratsiya yaratish"""
        from ..algorithms.qaoa import QAOAConfig
        
        return QAOAConfig(
            n_qubits=min(len(self.portfolio_state.assets), 6),
            p_levels=3,
            max_iterations=self.config.max_iterations,
            tolerance=self.config.convergence_threshold,
            optimization_method='COBYLA'
        )
    
    def _store_optimization_data(self, returns_data: np.ndarray, 
                               covariance_matrix: np.ndarray) -> None:
        """Optimization data'ni saqlash"""
        self._returns_data = returns_data
        self._covariance_matrix = covariance_matrix
    
    def _calculate_entanglement_strength(self, weights: np.ndarray) -> float:
        """Entanglement strength hisoblash"""
        if len(weights) < 2:
            return 0
        
        entanglement = 0
        pair_count = 0
        
        for i in range(len(weights)):
            for j in range(i+1, len(weights)):
                if weights[i] > 0.01 and weights[j] > 0.01:
                    entanglement += weights[i] * weights[j]
                    pair_count += 1
        
        return entanglement / pair_count if pair_count > 0 else 0
    
    def _compare_optimization_results(self, classical_result: Dict, 
                                    quantum_result: Dict) -> Dict:
        """Optimization natijalarini taqqoslash"""
        classical_sharpe = classical_result.get('sharpe_ratio', 0)
        quantum_sharpe = quantum_result.get('sharpe_ratio', 0)
        
        classical_return = classical_result.get('expected_return', 0)
        quantum_return = quantum_result.get('expected_return', 0)
        
        classical_risk = classical_result.get('risk', float('inf'))
        quantum_risk = quantum_result.get('risk', float('inf'))
        
        # Comparison metrics
        sharpe_improvement = quantum_sharpe - classical_sharpe
        return_improvement = quantum_return - classical_return
        risk_improvement = classical_risk - quantum_risk
        
        # Overall assessment
        quantum_advantage = (sharpe_improvement > 0.01 and 
                           return_improvement > 0.001)
        classical_better = not quantum_advantage
        
        return {
            'classical_better': classical_better,
            'quantum_advantage': quantum_advantage,
            'sharpe_improvement': sharpe_improvement,
            'return_improvement': return_improvement,
            'risk_improvement': risk_improvement,
            'performance_scores': {
                'classical': {
                    'sharpe_ratio': classical_sharpe,
                    'expected_return': classical_return,
                    'risk': classical_risk
                },
                'quantum': {
                    'sharpe_ratio': quantum_sharpe,
                    'expected_return': quantum_return,
                    'risk': quantum_risk
                }
            }
        }
    
    def get_optimization_summary(self) -> Dict:
        """Optimization umumiy xulosasi"""
        if not self.optimization_history:
            return {'error': 'Optimization history mavjud emas'}
        
        latest_result = self.optimization_history[-1]
        
        summary = {
            'portfolio_assets': self.portfolio_state.assets if self.portfolio_state else [],
            'latest_optimization': {
                'method': latest_result['method'],
                'success': latest_result.get('success', False),
                'sharpe_ratio': latest_result.get('sharpe_ratio', 0),
                'expected_return': latest_result.get('expected_return', 0),
                'risk': latest_result.get('risk', 0)
            },
            'optimization_count': len(self.optimization_history),
            'best_sharpe_ratio': max([r.get('sharpe_ratio', 0) for r in self.optimization_history]),
            'algorithm_comparison': self.algorithm_comparison
        }
        
        return summary
    
    def reset_optimizer(self) -> None:
        """Optimizer'ni qayta sozlash"""
        self.portfolio_state = None
        self.optimization_history = []
        self.algorithm_comparison = {}
        self._returns_data = None
        self._covariance_matrix = None
        print("Optimizer reset completed")