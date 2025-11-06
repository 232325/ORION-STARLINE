"""
Quantum-Classical Hybrid System
===============================

Quantum va classical algoritmlarni uyg'un kombinatsiya qilish.
Bu modul real-world quantum computing va classical computing integratsiyasini amalga oshiradi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

class QuantumClassicalHybridSystem:
    """
    Quantum-Classical Hybrid System for Portfolio Optimization
    """
    
    def __init__(self, 
                 quantum_portfolio_theory,
                 classical_optimizer_type: str = 'scipy',
                 quantum_optimizer_type: str = 'quantum_annealing',
                 hybrid_strategy: str = 'adaptive',
                 max_quantum_assets: int = 20):
        """
        Initialize hybrid system
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
            classical_optimizer_type: Classical optimizer ('scipy', 'cvxpy', 'gurobi')
            quantum_optimizer_type: Quantum optimizer type
            hybrid_strategy: Hybrid strategy ('adaptive', 'parallel', 'sequential')
            max_quantum_assets: Maximum assets for quantum processing
        """
        self.qpt = quantum_portfolio_theory
        self.classical_optimizer_type = classical_optimizer_type
        self.quantum_optimizer_type = quantum_optimizer_type
        self.hybrid_strategy = hybrid_strategy
        self.max_quantum_assets = max_quantum_assets
        
        # Performance tracking
        self.classical_performance = {}
        self.quantum_performance = {}
        self.hybrid_performance = {}
        
        # Optimization results
        self.classical_results = None
        self.quantum_results = None
        self.hybrid_results = None
        
        self.logger = logging.getLogger(__name__)
    
    def optimize_portfolio(self, 
                          target_return: Optional[float] = None,
                          risk_aversion: float = 1.0,
                          risk_tolerance: str = 'moderate',
                          enable_parallel: bool = True) -> Dict:
        """
        Hybrid portfolio optimization
        
        Args:
            target_return: Target portfolio return
            risk_aversion: Risk aversion parameter
            risk_tolerance: Risk tolerance level
            enable_parallel: Enable parallel optimization
            
        Returns:
            Hybrid optimization results
        """
        n_assets = len(self.qpt.assets)
        
        start_time = time.time()
        
        # Determine optimization approach based on strategy and constraints
        if self.hybrid_strategy == 'adaptive':
            optimization_plan = self._create_adaptive_plan(n_assets, risk_tolerance)
        elif self.hybrid_strategy == 'parallel':
            optimization_plan = self._create_parallel_plan()
        else:  # sequential
            optimization_plan = self._create_sequential_plan()
        
        # Execute optimization plan
        if enable_parallel and self.hybrid_strategy == 'parallel':
            results = self._execute_parallel_optimization(optimization_plan, target_return, risk_aversion)
        else:
            results = self._execute_sequential_optimization(optimization_plan, target_return, risk_aversion)
        
        execution_time = time.time() - start_time
        
        # Post-process results
        final_results = self._post_process_results(results, execution_time)
        
        return final_results
    
    def _create_adaptive_plan(self, n_assets: int, risk_tolerance: str) -> Dict:
        """Create adaptive optimization plan"""
        # Decide optimization approach based on problem characteristics
        plan = {
            'classical_weight': 0.0,
            'quantum_weight': 0.0,
            'use_quantum': False,
            'use_classical': False,
            'strategy': 'adaptive'
        }
        
        # Adaptive rules
        if n_assets > self.max_quantum_assets:
            # Too many assets for quantum, use classical primarily
            plan['classical_weight'] = 0.8
            plan['quantum_weight'] = 0.2
            plan['use_classical'] = True
            plan['use_quantum'] = True
        elif n_assets <= 5 and risk_tolerance in ['aggressive', 'very_aggressive']:
            # Small problem, use quantum for potential advantage
            plan['classical_weight'] = 0.3
            plan['quantum_weight'] = 0.7
            plan['use_classical'] = True
            plan['use_quantum'] = True
        else:
            # Balanced approach
            plan['classical_weight'] = 0.6
            plan['quantum_weight'] = 0.4
            plan['use_classical'] = True
            plan['use_quantum'] = True
        
        return plan
    
    def _create_parallel_plan(self) -> Dict:
        """Create parallel optimization plan"""
        return {
            'classical_weight': 0.5,
            'quantum_weight': 0.5,
            'use_classical': True,
            'use_quantum': True,
            'strategy': 'parallel'
        }
    
    def _create_sequential_plan(self) -> Dict:
        """Create sequential optimization plan"""
        return {
            'classical_weight': 0.7,
            'quantum_weight': 0.3,
            'use_classical': True,
            'use_quantum': True,
            'strategy': 'sequential'
        }
    
    def _execute_sequential_optimization(self, 
                                       plan: Dict, 
                                       target_return: Optional[float], 
                                       risk_aversion: float) -> Dict:
        """Execute sequential optimization"""
        results = {}
        
        # Classical optimization
        if plan['use_classical']:
            classical_start = time.time()
            results['classical'] = self._run_classical_optimization(target_return, risk_aversion)
            results['classical']['execution_time'] = time.time() - classical_start
        
        # Quantum optimization
        if plan['use_quantum']:
            quantum_start = time.time()
            results['quantum'] = self._run_quantum_optimization(target_return, risk_aversion)
            results['quantum']['execution_time'] = time.time() - quantum_start
        
        # Combine results
        if 'classical' in results and 'quantum' in results:
            results['hybrid'] = self._combine_results(
                results['classical'], results['quantum'], plan
            )
        
        return results
    
    def _execute_parallel_optimization(self, 
                                     plan: Dict, 
                                     target_return: Optional[float], 
                                     risk_aversion: float) -> Dict:
        """Execute parallel optimization"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit optimization tasks
            future_to_method = {}
            
            if plan['use_classical']:
                future_classical = executor.submit(self._run_classical_optimization, target_return, risk_aversion)
                future_to_method[future_classical] = 'classical'
            
            if plan['use_quantum']:
                future_quantum = executor.submit(self._run_quantum_optimization, target_return, risk_aversion)
                future_to_method[future_quantum] = 'quantum'
            
            # Collect results
            for future in as_completed(future_to_method):
                method = future_to_method[future]
                start_time = time.time()
                try:
                    result = future.result()
                    result['execution_time'] = time.time() - start_time
                    results[method] = result
                except Exception as exc:
                    self.logger.error(f"{method} optimization failed: {exc}")
                    results[method] = {'error': str(exc)}
        
        # Combine results
        if 'classical' in results and 'quantum' in results:
            results['hybrid'] = self._combine_results(
                results['classical'], results['quantum'], plan
            )
        
        return results
    
    def _run_classical_optimization(self, 
                                  target_return: Optional[float], 
                                  risk_aversion: float) -> Dict:
        """Run classical optimization"""
        try:
            from scipy.optimize import minimize
            
            n_assets = len(self.qpt.assets)
            
            # Define objective function
            def objective(weights):
                expected_returns = self.qpt._quantum_expected_returns()
                portfolio_return = np.sum(weights * expected_returns)
                portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
                
                utility = portfolio_return - 0.5 * risk_aversion * portfolio_variance
                
                # Return penalty
                penalty = 0
                if target_return is not None and portfolio_return < target_return:
                    penalty = (target_return - portfolio_return) ** 2
                
                return -(utility - penalty)
            
            # Constraints
            constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
            if target_return is not None:
                constraints.append({
                    'type': 'eq',
                    'fun': lambda w: np.sum(w * self.qpt._quantum_expected_returns()) - target_return
                })
            
            # Bounds
            bounds = [(0, 1) for _ in range(n_assets)]
            
            # Initial guess
            x0 = np.ones(n_assets) / n_assets
            
            # Optimize
            result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                weights = result.x
                allocation = {asset: weight for asset, weight in zip(self.qpt.assets, weights) 
                             if weight > 0.001}
                
                portfolio_return = np.sum(weights * self.qpt._quantum_expected_returns())
                portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
                portfolio_volatility = np.sqrt(portfolio_variance)
                
                return {
                    'allocation': allocation,
                    'weights': weights,
                    'expected_return': portfolio_return,
                    'volatility': portfolio_volatility,
                    'sharpe_ratio': (portfolio_return - self.qpt.risk_free_rate) / portfolio_volatility,
                    'optimization_status': 'success',
                    'method': 'classical'
                }
            else:
                return {
                    'optimization_status': 'failed',
                    'message': result.message,
                    'method': 'classical'
                }
        
        except Exception as e:
            return {
                'optimization_status': 'error',
                'error': str(e),
                'method': 'classical'
            }
    
    def _run_quantum_optimization(self, 
                                target_return: Optional[float], 
                                risk_aversion: float) -> Dict:
        """Run quantum optimization"""
        try:
            from .quantum_annealing import QuantumAnnealingOptimizer
            
            # Create quantum optimizer
            qao = QuantumAnnealingOptimizer(self.qpt)
            
            # Run optimization
            results = qao.optimize_portfolio(
                target_return=target_return,
                risk_aversion=risk_aversion,
                quantum_enhancement=True
            )
            
            if results['optimization_status'] == 'success':
                return {
                    'allocation': results.get('portfolio_statistics', {}).get('allocation', {}),
                    'expected_return': results.get('portfolio_statistics', {}).get('expected_return', 0),
                    'volatility': results.get('portfolio_statistics', {}).get('volatility', 0),
                    'sharpe_ratio': results.get('portfolio_statistics', {}).get('sharpe_ratio', 0),
                    'quantum_entropy': results.get('portfolio_statistics', {}).get('quantum_entropy', 0),
                    'quantum_coherence': results.get('portfolio_statistics', {}).get('quantum_coherence', 0),
                    'optimization_status': 'success',
                    'method': 'quantum',
                    'additional_metrics': results
                }
            else:
                return {
                    'optimization_status': 'failed',
                    'message': results.get('message', 'Unknown error'),
                    'method': 'quantum'
                }
        
        except Exception as e:
            return {
                'optimization_status': 'error',
                'error': str(e),
                'method': 'quantum'
            }
    
    def _combine_results(self, 
                        classical_result: Dict, 
                        quantum_result: Dict, 
                        plan: Dict) -> Dict:
        """Combine classical and quantum results"""
        if classical_result['optimization_status'] != 'success':
            return quantum_result
        if quantum_result['optimization_status'] != 'success':
            return classical_result
        
        # Weight combination
        classical_weight = plan['classical_weight']
        quantum_weight = plan['quantum_weight']
        
        # Combine weights
        classical_weights = np.array(list(classical_result['allocation'].values()))
        quantum_weights = np.array(list(quantum_result['allocation'].values()))
        
        # Ensure same length
        max_len = max(len(classical_weights), len(quantum_weights))
        if len(classical_weights) < max_len:
            classical_weights = np.pad(classical_weights, (0, max_len - len(classical_weights)))
        if len(quantum_weights) < max_len:
            quantum_weights = np.pad(quantum_weights, (0, max_len - len(quantum_weights)))
        
        # Weighted combination
        combined_weights = classical_weight * classical_weights + quantum_weight * quantum_weights
        
        # Renormalize
        combined_weights = combined_weights / np.sum(combined_weights)
        
        # Calculate portfolio metrics
        expected_return = np.sum(combined_weights * self.qpt._quantum_expected_returns())
        portfolio_variance = np.dot(combined_weights, np.dot(self.qpt.covariance_matrix, combined_weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Create allocation dict
        combined_allocation = {}
        for i, weight in enumerate(combined_weights):
            if weight > 0.001 and i < len(self.qpt.assets):
                combined_allocation[self.qpt.assets[i]] = weight
        
        return {
            'allocation': combined_allocation,
            'weights': combined_weights,
            'expected_return': expected_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': (expected_return - self.qpt.risk_free_rate) / portfolio_volatility,
            'classical_contribution': classical_weight,
            'quantum_contribution': quantum_weight,
            'optimization_status': 'success',
            'method': 'hybrid',
            'classical_result': classical_result,
            'quantum_result': quantum_result
        }
    
    def _post_process_results(self, results: Dict, execution_time: float) -> Dict:
        """Post-process optimization results"""
        # Extract best method
        best_method = None
        best_sharpe = -float('inf')
        
        for method, result in results.items():
            if result['optimization_status'] == 'success':
                sharpe = result.get('sharpe_ratio', -float('inf'))
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_method = method
        
        # Add performance metrics
        performance_summary = {
            'execution_time': execution_time,
            'methods_tested': list(results.keys()),
            'best_method': best_method,
            'best_sharpe_ratio': best_sharpe,
            'classical_time': results.get('classical', {}).get('execution_time', 0),
            'quantum_time': results.get('quantum', {}).get('execution_time', 0)
        }
        
        final_results = {
            'optimization_results': results,
            'performance_summary': performance_summary,
            'recommendation': self._generate_recommendation(results, performance_summary)
        }
        
        return final_results
    
    def _generate_recommendation(self, results: Dict, performance: Dict) -> str:
        """Generate optimization recommendation"""
        best_method = performance['best_method']
        
        if best_method == 'classical':
            return "Classical optimization performed best. Consider this for similar problems."
        elif best_method == 'quantum':
            return "Quantum optimization showed advantage. Quantum computing may be beneficial for this problem size."
        elif best_method == 'hybrid':
            return "Hybrid approach provided best results. Combination of quantum and classical methods is recommended."
        else:
            return "Optimization had mixed results. Consider adjusting parameters or problem formulation."
    
    def benchmark_optimization_methods(self, 
                                     test_problems: List[Dict],
                                     save_results: bool = True) -> Dict:
        """
        Benchmark different optimization methods
        
        Args:
            test_problems: List of test problem configurations
            save_results: Save benchmark results
            
        Returns:
            Benchmark results
        """
        benchmark_results = {
            'test_problems': len(test_problems),
            'methods': ['classical', 'quantum', 'hybrid'],
            'results': []
        }
        
        for i, problem in enumerate(test_problems):
            self.logger.info(f"Testing problem {i+1}/{len(test_problems)}")
            
            problem_result = {
                'problem_id': i,
                'problem_config': problem,
                'classical': {},
                'quantum': {},
                'hybrid': {}
            }
            
            # Test each method
            for method in benchmark_results['methods']:
                try:
                    start_time = time.time()
                    
                    if method == 'classical':
                        result = self._run_classical_optimization(
                            problem.get('target_return'),
                            problem.get('risk_aversion', 1.0)
                        )
                    elif method == 'quantum':
                        result = self._run_quantum_optimization(
                            problem.get('target_return'),
                            problem.get('risk_aversion', 1.0)
                        )
                    else:  # hybrid
                        result = self.optimize_portfolio(
                            target_return=problem.get('target_return'),
                            risk_aversion=problem.get('risk_aversion', 1.0)
                        )
                    
                    execution_time = time.time() - start_time
                    
                    # Store result
                    if method == 'hybrid':
                        problem_result[method] = {
                            'status': result['optimization_results'].get('hybrid', {}).get('optimization_status', 'failed'),
                            'sharpe_ratio': result['optimization_results'].get('hybrid', {}).get('sharpe_ratio', 0),
                            'execution_time': result['performance_summary']['execution_time'],
                            'success': True
                        }
                    else:
                        problem_result[method] = {
                            'status': result.get('optimization_status', 'failed'),
                            'sharpe_ratio': result.get('sharpe_ratio', 0),
                            'execution_time': result.get('execution_time', execution_time),
                            'success': True
                        }
                
                except Exception as e:
                    problem_result[method] = {
                        'status': 'error',
                        'error': str(e),
                        'execution_time': 0,
                        'success': False
                    }
                    self.logger.error(f"Method {method} failed for problem {i}: {e}")
            
            benchmark_results['results'].append(problem_result)
        
        # Calculate summary statistics
        benchmark_results['summary'] = self._calculate_benchmark_summary(benchmark_results['results'])
        
        if save_results:
            self._save_benchmark_results(benchmark_results)
        
        return benchmark_results
    
    def _calculate_benchmark_summary(self, results: List[Dict]) -> Dict:
        """Calculate benchmark summary statistics"""
        summary = {}
        
        for method in ['classical', 'quantum', 'hybrid']:
            method_results = [r[method] for r in results if r[method]['success']]
            
            if method_results:
                summary[method] = {
                    'success_rate': len(method_results) / len(results),
                    'average_sharpe': np.mean([r['sharpe_ratio'] for r in method_results]),
                    'average_time': np.mean([r['execution_time'] for r in method_results]),
                    'best_sharpe': max([r['sharpe_ratio'] for r in method_results]),
                    'worst_sharpe': min([r['sharpe_ratio'] for r in method_results])
                }
        
        return summary
    
    def _save_benchmark_results(self, results: Dict, filepath: str = "benchmark_results.json"):
        """Save benchmark results to file"""
        import json
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Benchmark results saqlandi: {filepath}")
    
    def visualize_hybrid_comparison(self, results: Dict, save_path: Optional[str] = None):
        """Visualize hybrid optimization comparison"""
        if 'optimization_results' not in results:
            self.logger.warning("Optimization results topilmadi")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Quantum-Classical Hybrid Optimization Comparison', fontsize=16)
        
        optimization_results = results['optimization_results']
        
        # 1. Method comparison
        methods = list(optimization_results.keys())
        sharpe_ratios = []
        execution_times = []
        
        for method in methods:
            if optimization_results[method]['optimization_status'] == 'success':
                sharpe_ratios.append(optimization_results[method].get('sharpe_ratio', 0))
                execution_times.append(optimization_results[method].get('execution_time', 0))
            else:
                sharpe_ratios.append(0)
                execution_times.append(0)
        
        axes[0, 0].bar(methods, sharpe_ratios, color=['blue', 'red', 'green'][:len(methods)])
        axes[0, 0].set_title('Sharpe Ratio Comparison')
        axes[0, 0].set_ylabel('Sharpe Ratio')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Execution time comparison
        axes[0, 1].bar(methods, execution_times, color=['lightblue', 'pink', 'lightgreen'][:len(methods)])
        axes[0, 1].set_title('Execution Time Comparison')
        axes[0, 1].set_ylabel('Execution Time (seconds)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Risk-return scatter
        if 'hybrid' in optimization_results and optimization_results['hybrid']['optimization_status'] == 'success':
            hybrid_result = optimization_results['hybrid']
            axes[1, 0].scatter(hybrid_result.get('volatility', 0), 
                             hybrid_result.get('expected_return', 0),
                             s=100, color='green', label='Hybrid', marker='*')
            
            if 'classical' in optimization_results and optimization_results['classical']['optimization_status'] == 'success':
                classical_result = optimization_results['classical']
                axes[1, 0].scatter(classical_result.get('volatility', 0), 
                                 classical_result.get('expected_return', 0),
                                 s=100, color='blue', label='Classical', marker='o')
            
            if 'quantum' in optimization_results and optimization_results['quantum']['optimization_status'] == 'success':
                quantum_result = optimization_results['quantum']
                axes[1, 0].scatter(quantum_result.get('volatility', 0), 
                                 quantum_result.get('expected_return', 0),
                                 s=100, color='red', label='Quantum', marker='s')
            
            axes[1, 0].set_xlabel('Volatility')
            axes[1, 0].set_ylabel('Expected Return')
            axes[1, 0].set_title('Risk-Return Comparison')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Performance summary
        if 'performance_summary' in results:
            perf = results['performance_summary']
            summary_text = f"""
            Best Method: {perf.get('best_method', 'Unknown')}
            Best Sharpe: {perf.get('best_sharpe_ratio', 0):.4f}
            Total Time: {perf.get('execution_time', 0):.2f}s
            Classical Time: {perf.get('classical_time', 0):.2f}s
            Quantum Time: {perf.get('quantum_time', 0):.2f}s
            """
            
            axes[1, 1].text(0.1, 0.5, summary_text, transform=axes[1, 1].transAxes,
                           fontsize=12, verticalalignment='center')
            axes[1, 1].set_title('Performance Summary')
            axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Hybrid comparison visualization saqlandi: {save_path}")
        else:
            plt.show()