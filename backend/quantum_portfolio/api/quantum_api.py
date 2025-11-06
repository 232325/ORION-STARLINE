"""
Quantum Portfolio API Interface
==============================

Main quantum portfolio optimization API interface.
Unified interface for all quantum optimization operations.

Muallif: Quantum Portfolio Team
 Sana: 2025-11-03
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import json

# Import quantum portfolio modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.quantum_portfolio_theory import QuantumPortfolioTheory
from core.quantum_efficient_frontier import QuantumEfficientFrontier
from models.cross_asset_quantum_model import CrossAssetQuantumModel
from algorithms.variational_quantum import VariationalQuantumAlgorithm
from integration.hybrid_system import HybridQuantumClassicalSystem

@dataclass
class OptimizationRequest:
    """Portfolio optimization request"""
    portfolio_id: str
    assets: List[str]
    constraints: Dict[str, Any]
    quantum_algorithm: str
    target_return: Optional[float] = None
    max_risk: Optional[float] = None
    risk_free_rate: float = 0.02
    investment_budget: float = 1.0
    include_risk_measures: bool = True

@dataclass
class OptimizationResult:
    """Portfolio optimization result"""
    portfolio_id: str
    weights: np.ndarray
    expected_return: float
    risk: float
    sharpe_ratio: float
    algorithm_used: str
    computation_time: float
    quantum_metrics: Dict[str, Any]
    timestamp: datetime

class QuantumPortfolioAPI:
    """Main quantum portfolio optimization API"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.portfolio_theory = QuantumPortfolioTheory()
        self.efficient_frontier = QuantumEfficientFrontier()
        self.cross_asset_model = CrossAssetQuantumModel()
        self.vqe_algorithm = VariationalQuantumAlgorithm()
        self.hybrid_system = HybridQuantumClassicalSystem()
        
        # API state
        self.active_optimizations = {}
        self.optimization_history = {}
        
    async def optimize_portfolio(self, request: OptimizationRequest) -> OptimizationResult:
        """Optimize portfolio using quantum algorithms"""
        try:
            self.logger.info(f"Starting portfolio optimization: {request.portfolio_id}")
            
            # Validate request
            await self._validate_optimization_request(request)
            
            # Start optimization
            start_time = datetime.now()
            
            # Choose quantum algorithm
            quantum_result = await self._execute_quantum_optimization(request)
            
            computation_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(
                quantum_result['weights'], request.assets
            )
            
            # Create result
            result = OptimizationResult(
                portfolio_id=request.portfolio_id,
                weights=quantum_result['weights'],
                expected_return=portfolio_metrics['expected_return'],
                risk=portfolio_metrics['risk'],
                sharpe_ratio=portfolio_metrics['sharpe_ratio'],
                algorithm_used=request.quantum_algorithm,
                computation_time=computation_time,
                quantum_metrics=quantum_result.get('quantum_metrics', {}),
                timestamp=datetime.now()
            )
            
            # Store result
            self.optimization_history[request.portfolio_id] = result
            self.active_optimizations.pop(request.portfolio_id, None)
            
            self.logger.info(f"Portfolio optimization completed: {request.portfolio_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Portfolio optimization failed: {str(e)}")
            raise
            
    async def _execute_quantum_optimization(self, request: OptimizationRequest) -> Dict[str, Any]:
        """Execute quantum optimization algorithm"""
        
        # Set up constraints
        constraints = self._setup_constraints(request)
        
        if request.quantum_algorithm == "VQE":
            return await self._run_vqe_optimization(request, constraints)
        elif request.quantum_algorithm == "QAOA":
            return await self._run_qaoa_optimization(request, constraints)
        elif request.quantum_algorithm == "ANNEALING":
            return await self._run_annealing_optimization(request, constraints)
        elif request.quantum_algorithm == "HYBRID":
            return await self._run_hybrid_optimization(request, constraints)
        else:
            raise ValueError(f"Unsupported quantum algorithm: {request.quantum_algorithm}")
            
    async def _run_vqe_optimization(self, request: OptimizationRequest, 
                                  constraints: Dict) -> Dict[str, Any]:
        """Run VQE optimization"""
        # Prepare quantum circuit
        circuit_data = self.vqe_algorithm.prepare_portfolio_circuit(
            weights_shape=(len(request.assets),),
            constraints=constraints
        )
        
        # Run VQE
        result = await self.vqe_algorithm.optimize_portfolio(
            circuit_data=circuit_data,
            assets=request.assets,
            target_return=request.target_return,
            max_risk=request.max_risk
        )
        
        return {
            'weights': result.optimal_weights,
            'quantum_metrics': {
                'circuit_depth': circuit_data.get('depth', 0),
                'qubits_used': circuit_data.get('qubits', 0),
                'convergence_iterations': result.iterations,
                'final_energy': result.energy
            }
        }
        
    async def _run_qaoa_optimization(self, request: OptimizationRequest,
                                   constraints: Dict) -> Dict[str, Any]:
        """Run QAOA optimization"""
        # Similar implementation for QAOA
        # For brevity, using VQE as placeholder
        return await self._run_vqe_optimization(request, constraints)
        
    async def _run_annealing_optimization(self, request: OptimizationRequest,
                                        constraints: Dict) -> Dict[str, Any]:
        """Run quantum annealing optimization"""
        # Import here to avoid circular import
        from algorithms.quantum_annealing import QuantumAnnealingOptimizer
        
        annealing = QuantumAnnealingOptimizer()
        
        # Convert constraints to annealing format
        qp_problem = self._convert_to_qubo(request, constraints)
        
        result = await annealing.optimize_portfolio(qp_problem, request.assets)
        
        return {
            'weights': result.optimal_weights,
            'quantum_metrics': {
                'annealing_time': result.computation_time,
                'final_energy': result.energy,
                'num_reads': result.num_reads
            }
        }
        
    async def _run_hybrid_optimization(self, request: OptimizationRequest,
                                     constraints: Dict) -> Dict[str, Any]:
        """Run hybrid quantum-classical optimization"""
        result = await self.hybrid_system.optimize_portfolio(
            assets=request.assets,
            constraints=constraints,
            quantum_algorithm=request.quantum_algorithm,
            target_return=request.target_return,
            max_risk=request.max_risk
        )
        
        return {
            'weights': result['weights'],
            'quantum_metrics': result.get('quantum_metrics', {}),
            'classical_metrics': result.get('classical_metrics', {})
        }
        
    def _setup_constraints(self, request: OptimizationRequest) -> Dict[str, Any]:
        """Setup portfolio constraints"""
        constraints = {
            'budget': request.investment_budget,
            'long_only': True,  # Default: no short selling
            'max_weight': 0.4,  # Default: max 40% per asset
            'min_weight': 0.05,  # Default: min 5% per asset
            'risk_free_rate': request.risk_free_rate
        }
        
        # Merge with user constraints
        if request.constraints:
            constraints.update(request.constraints)
            
        return constraints
        
    def _convert_to_qubo(self, request: OptimizationRequest, 
                        constraints: Dict) -> Dict[str, Any]:
        """Convert portfolio optimization to QUBO format"""
        # This would typically involve transforming the portfolio problem
        # into quadratic unconstrained binary optimization format
        
        n_assets = len(request.assets)
        
        # Create QUBO matrix (simplified)
        Q = np.random.randn(n_assets, n_assets) * 0.1
        
        # Add budget constraint penalty
        budget_penalty = 1.0
        for i in range(n_assets):
            Q[i, i] -= 2 * budget_penalty
            
        return {
            'Q': Q,
            'linear_biases': np.random.randn(n_assets) * 0.1,
            'constraints': constraints
        }
        
    def _calculate_portfolio_metrics(self, weights: np.ndarray, 
                                   assets: List[str]) -> Dict[str, float]:
        """Calculate portfolio performance metrics"""
        # This is simplified - in practice, would use actual asset data
        expected_return = np.random.uniform(0.05, 0.15)  # Placeholder
        risk = np.random.uniform(0.1, 0.3)  # Placeholder
        sharpe_ratio = (expected_return - 0.02) / risk if risk > 0 else 0
        
        return {
            'expected_return': expected_return,
            'risk': risk,
            'sharpe_ratio': sharpe_ratio
        }
        
    async def _validate_optimization_request(self, request: OptimizationRequest):
        """Validate optimization request"""
        if not request.assets:
            raise ValueError("Assets list cannot be empty")
            
        if request.target_return is not None and not 0 < request.target_return < 1:
            raise ValueError("Target return must be between 0 and 1")
            
        if request.max_risk is not None and not 0 < request.max_risk < 1:
            raise ValueError("Max risk must be between 0 and 1")
            
        supported_algorithms = ["VQE", "QAOA", "ANNEALING", "HYBRID"]
        if request.quantum_algorithm not in supported_algorithms:
            raise ValueError(f"Algorithm {request.quantum_algorithm} not supported")
            
    async def get_efficient_frontier(self, assets: List[str], 
                                   n_points: int = 50) -> Dict[str, Any]:
        """Get quantum efficient frontier"""
        try:
            self.logger.info(f"Computing efficient frontier for {len(assets)} assets")
            
            # Use quantum efficient frontier algorithm
            frontier_result = await self.efficient_frontier.compute_frontier(
                assets=assets,
                num_points=n_points,
                algorithm="VQE"
            )
            
            return {
                'assets': assets,
                'frontier_points': frontier_result.points,
                'algorithm_used': 'Quantum Efficient Frontier',
                'computation_time': frontier_result.computation_time,
                'quantum_metrics': frontier_result.quantum_metrics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Efficient frontier computation failed: {str(e)}")
            raise
            
    async def get_portfolio_performance(self, portfolio_id: str) -> Dict[str, Any]:
        """Get portfolio performance analysis"""
        if portfolio_id not in self.optimization_history:
            raise ValueError(f"Portfolio {portfolio_id} not found")
            
        result = self.optimization_history[portfolio_id]
        
        # Additional performance analysis
        performance_analysis = {
            'portfolio_id': portfolio_id,
            'current_performance': {
                'expected_return': result.expected_return,
                'risk': result.risk,
                'sharpe_ratio': result.sharpe_ratio,
                'weights': result.weights.tolist()
            },
            'optimization_details': {
                'algorithm_used': result.algorithm_used,
                'computation_time': result.computation_time,
                'quantum_metrics': result.quantum_metrics,
                'timestamp': result.timestamp.isoformat()
            },
            'risk_analysis': await self._analyze_portfolio_risk(result.weights),
            'allocation_analysis': await self._analyze_allocation(result.weights)
        }
        
        return performance_analysis
        
    async def _analyze_portfolio_risk(self, weights: np.ndarray) -> Dict[str, Any]:
        """Analyze portfolio risk metrics"""
        # Simplified risk analysis
        concentration_risk = np.max(weights) if len(weights) > 0 else 0
        diversification_ratio = len(weights[weights > 0.01]) / len(weights) if len(weights) > 0 else 0
        
        return {
            'concentration_risk': concentration_risk,
            'diversification_ratio': diversification_risk,
            'risk_score': concentration_risk * (1 - diversification_ratio)
        }
        
    async def _analyze_allocation(self, weights: np.ndarray) -> Dict[str, Any]:
        """Analyze portfolio allocation"""
        if len(weights) == 0:
            return {}
            
        return {
            'largest_allocation': np.max(weights),
            'smallest_allocation': np.min(weights),
            'average_allocation': np.mean(weights),
            'allocation_std': np.std(weights),
            'num_holdings': len(weights[weights > 0.01])
        }
        
    async def get_quantum_metrics(self, portfolio_id: str) -> Dict[str, Any]:
        """Get detailed quantum computation metrics"""
        if portfolio_id not in self.optimization_history:
            raise ValueError(f"Portfolio {portfolio_id} not found")
            
        result = self.optimization_history[portfolio_id]
        
        return {
            'portfolio_id': portfolio_id,
            'algorithm_details': {
                'algorithm': result.algorithm_used,
                'computation_time': result.computation_time,
                'quantum_metrics': result.quantum_metrics
            },
            'quantum_advantage_analysis': await self._analyze_quantum_advantage(
                result.quantum_metrics
            ),
            'performance_comparison': await self._compare_with_classical(
                result.algorithm_used, len(result.weights)
            )
        }
        
    async def _analyze_quantum_advantage(self, quantum_metrics: Dict) -> Dict[str, Any]:
        """Analyze quantum advantage metrics"""
        return {
            'qubits_utilized': quantum_metrics.get('qubits_used', 0),
            'circuit_depth': quantum_metrics.get('circuit_depth', 0),
            'estimated_classical_time': self._estimate_classical_comparison(len(quantum_metrics)),
            'quantum_speedup': quantum_metrics.get('convergence_iterations', 0),
            'error_rate': quantum_metrics.get('error_rate', 0.0)
        }
        
    def _estimate_classical_comparison(self, problem_size: int) -> float:
        """Estimate equivalent classical computation time"""
        # Simplified classical complexity: O(n^3) for mean-variance optimization
        operations = problem_size ** 3
        return operations * 1e-6  # microseconds
        
    async def _compare_with_classical(self, quantum_algorithm: str, 
                                    problem_size: int) -> Dict[str, Any]:
        """Compare quantum vs classical performance"""
        quantum_time = self._estimate_quantum_time(quantum_algorithm, problem_size)
        classical_time = self._estimate_classical_comparison(problem_size)
        
        return {
            'quantum_time': quantum_time,
            'classical_time': classical_time,
            'speedup_ratio': classical_time / quantum_time if quantum_time > 0 else 0,
            'advantage_achieved': quantum_time < classical_time
        }
        
    def _estimate_quantum_time(self, algorithm: str, problem_size: int) -> float:
        """Estimate quantum computation time"""
        # Simplified estimation based on algorithm and problem size
        base_time = problem_size * 0.1  # milliseconds
        algorithm_overhead = {
            'VQE': 1.2,
            'QAOA': 1.5,
            'ANNEALING': 0.8,
            'HYBRID': 1.0
        }
        
        return base_time * algorithm_overhead.get(algorithm, 1.0)
        
    def get_api_status(self) -> Dict[str, Any]:
        """Get API status information"""
        return {
            'status': 'operational',
            'version': '1.0.0',
            'active_optimizations': len(self.active_optimizations),
            'completed_optimizations': len(self.optimization_history),
            'supported_algorithms': ['VQE', 'QAOA', 'ANNEALING', 'HYBRID'],
            'timestamp': datetime.now().isoformat()
        }
        
    def get_optimization_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get optimization history"""
        history = []
        for portfolio_id, result in list(self.optimization_history.items())[-limit:]:
            history.append({
                'portfolio_id': portfolio_id,
                'expected_return': result.expected_return,
                'risk': result.risk,
                'sharpe_ratio': result.sharpe_ratio,
                'algorithm_used': result.algorithm_used,
                'timestamp': result.timestamp.isoformat()
            })
        return history

# Usage example
async def example_usage():
    """Example usage of Quantum Portfolio API"""
    api = QuantumPortfolioAPI()
    
    # Optimize portfolio
    request = OptimizationRequest(
        portfolio_id="example_portfolio",
        assets=["AAPL", "GOOGL", "MSFT", "TSLA"],
        constraints={},
        quantum_algorithm="VQE",
        target_return=0.10,
        max_risk=0.20
    )
    
    result = await api.optimize_portfolio(request)
    print(f"Optimization result: {result}")
    
    # Get efficient frontier
    frontier = await api.get_efficient_frontier(request.assets)
    print(f"Efficient frontier computed with {len(frontier['frontier_points'])} points")
    
    # Get portfolio performance
    performance = await api.get_portfolio_performance(request.portfolio_id)
    print(f"Portfolio performance: {performance}")

if __name__ == "__main__":
    asyncio.run(example_usage())