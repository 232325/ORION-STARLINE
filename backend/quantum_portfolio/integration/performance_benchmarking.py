"""
Quantum Performance Benchmarking
================================

Quantum portfolio sistemi performance benchmarking.
Bu modul tizimning performance metriklarini o'lchash va solishtirish uchun.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor

class QuantumPerformanceBenchmarking:
    """
    Performance Benchmarking for Quantum Portfolio System
    """
    
    def __init__(self, quantum_portfolio_theory):
        """
        Initialize performance benchmarking
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
        """
        self.qpt = quantum_portfolio_theory
        self.benchmark_results = {}
        self.performance_metrics = {}
        self.resource_usage = {}
        
        self.logger = logging.getLogger(__name__)
    
    def run_comprehensive_benchmark(self, 
                                  test_configurations: List[Dict]) -> Dict:
        """
        Run comprehensive performance benchmark
        
        Args:
            test_configurations: List of test configurations
            
        Returns:
            Comprehensive benchmark results
        """
        benchmark_results = {
            'timestamp': time.time(),
            'test_configurations': len(test_configurations),
            'results': [],
            'summary': {},
            'system_info': self._get_system_info()
        }
        
        # System resource monitoring
        monitor_thread = threading.Thread(target=self._monitor_resources)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Run each test configuration
        for i, config in enumerate(test_configurations):
            self.logger.info(f"Running benchmark {i+1}/{len(test_configurations)}")
            
            test_result = self._run_single_benchmark(config)
            benchmark_results['results'].append(test_result)
        
        # Calculate summary statistics
        benchmark_results['summary'] = self._calculate_benchmark_summary(benchmark_results['results'])
        
        # Save results
        self._save_benchmark_results(benchmark_results)
        
        self.benchmark_results = benchmark_results
        return benchmark_results
    
    def _run_single_benchmark(self, config: Dict) -> Dict:
        """Run single benchmark test"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Extract configuration
        n_assets = config.get('n_assets', 10)
        optimization_method = config.get('method', 'classical')
        target_return = config.get('target_return')
        risk_aversion = config.get('risk_aversion', 1.0)
        
        # Create test data if needed
        if n_assets != len(self.qpt.assets):
            self._create_test_portfolio(n_assets)
        
        # Run optimization
        optimization_result = self._run_optimization_test(optimization_method, target_return, risk_aversion)
        
        # Collect metrics
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        return {
            'configuration': config,
            'execution_time': execution_time,
            'memory_usage': memory_usage,
            'optimization_result': optimization_result,
            'success': optimization_result.get('optimization_status') == 'success',
            'metrics': self._extract_performance_metrics(optimization_result)
        }
    
    def _create_test_portfolio(self, n_assets: int):
        """Create test portfolio with specified number of assets"""
        # Generate synthetic asset names
        test_assets = [f'TEST_ASSET_{i}' for i in range(n_assets)]
        self.qpt.assets = test_assets
        self.qpt.n_assets = n_assets
        
        # Create synthetic returns data
        np.random.seed(42)  # For reproducible results
        n_days = 252
        returns_data = np.random.multivariate_normal(
            mean=np.random.normal(0.001, 0.0005, n_assets),
            cov=np.random.rand(n_assets, n_assets) * 0.0001 + np.eye(n_assets) * 0.01,
            size=n_days
        )
        
        # Set up portfolio data
        returns_df = pd.DataFrame(returns_data, columns=test_assets)
        self.qpt.load_data(returns_df)
        
        self.logger.info(f"Test portfolio created with {n_assets} assets")
    
    def _run_optimization_test(self, 
                             method: str, 
                             target_return: Optional[float], 
                             risk_aversion: float) -> Dict:
        """Run optimization test with specified method"""
        try:
            if method == 'classical':
                from scipy.optimize import minimize
                
                n_assets = len(self.qpt.assets)
                
                def objective(weights):
                    expected_returns = self.qpt._quantum_expected_returns()
                    portfolio_return = np.sum(weights * expected_returns)
                    portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
                    
                    utility = portfolio_return - 0.5 * risk_aversion * portfolio_variance
                    
                    penalty = 0
                    if target_return is not None and portfolio_return < target_return:
                        penalty = (target_return - portfolio_return) ** 2
                    
                    return -(utility - penalty)
                
                constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
                if target_return is not None:
                    constraints.append({
                        'type': 'eq',
                        'fun': lambda w: np.sum(w * self.qpt._quantum_expected_returns()) - target_return
                    })
                
                bounds = [(0, 1) for _ in range(n_assets)]
                x0 = np.ones(n_assets) / n_assets
                
                result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
                
                if result.success:
                    weights = result.x
                    portfolio_return = np.sum(weights * self.qpt._quantum_expected_returns())
                    portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
                    portfolio_volatility = np.sqrt(portfolio_variance)
                    
                    return {
                        'optimization_status': 'success',
                        'weights': weights,
                        'expected_return': portfolio_return,
                        'volatility': portfolio_volatility,
                        'sharpe_ratio': (portfolio_return - self.qpt.risk_free_rate) / portfolio_volatility,
                        'method': method
                    }
                else:
                    return {
                        'optimization_status': 'failed',
                        'message': result.message,
                        'method': method
                    }
            
            elif method == 'quantum_annealing':
                from ..algorithms.quantum_annealing import QuantumAnnealingOptimizer
                
                qao = QuantumAnnealingOptimizer(self.qpt)
                result = qao.optimize_portfolio(
                    target_return=target_return,
                    risk_aversion=risk_aversion
                )
                
                if result['optimization_status'] == 'success':
                    weights = result['best_solution']
                    portfolio_return = np.sum(weights * self.qpt._quantum_expected_returns())
                    portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
                    portfolio_volatility = np.sqrt(portfolio_variance)
                    
                    return {
                        'optimization_status': 'success',
                        'weights': weights,
                        'expected_return': portfolio_return,
                        'volatility': portfolio_volatility,
                        'sharpe_ratio': (portfolio_return - self.qpt.risk_free_rate) / portfolio_volatility,
                        'method': method,
                        'additional_metrics': result
                    }
                else:
                    return {
                        'optimization_status': 'failed',
                        'message': result.get('message', 'Unknown error'),
                        'method': method
                    }
            
            else:
                return {
                    'optimization_status': 'error',
                    'error': f'Unknown method: {method}',
                    'method': method
                }
        
        except Exception as e:
            return {
                'optimization_status': 'error',
                'error': str(e),
                'method': method
            }
    
    def _extract_performance_metrics(self, result: Dict) -> Dict:
        """Extract performance metrics from optimization result"""
        metrics = {}
        
        if result.get('optimization_status') == 'success':
            # Basic performance metrics
            metrics['return'] = result.get('expected_return', 0)
            metrics['volatility'] = result.get('volatility', 0)
            metrics['sharpe_ratio'] = result.get('sharpe_ratio', 0)
            
            # Portfolio-specific metrics
            if 'weights' in result:
                weights = result['weights']
                
                # Diversification metrics
                weights_sum_squares = np.sum(weights ** 2)
                metrics['concentration_ratio'] = weights_sum_squares
                
                # Number of significant positions
                significant_positions = np.sum(weights > 0.01)
                metrics['num_significant_positions'] = significant_positions
                
                # Maximum position size
                metrics['max_position'] = np.max(weights)
                
                # Entropy (diversification measure)
                positive_weights = weights[weights > 0]
                if len(positive_weights) > 0:
                    normalized_weights = positive_weights / np.sum(positive_weights)
                    entropy = -np.sum(normalized_weights * np.log2(normalized_weights + 1e-8))
                    metrics['entropy'] = entropy
                else:
                    metrics['entropy'] = 0
            
            # Method-specific metrics
            if result.get('method') == 'quantum_annealing':
                metrics['quantum_specific'] = {
                    'iterations': result.get('additional_metrics', {}).get('total_iterations', 0),
                    'acceptance_rate': result.get('additional_metrics', {}).get('acceptance_rate', 0)
                }
        
        return metrics
    
    def _monitor_resources(self):
        """Monitor system resources during benchmarking"""
        # This would run in a separate thread to monitor CPU, memory, etc.
        # Simplified implementation
        self.resource_usage = {
            'peak_memory': psutil.Process().memory_info().rss / 1024 / 1024,  # MB
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total / 1024 / 1024 / 1024  # GB
        }
    
    def _get_system_info(self) -> Dict:
        """Get system information"""
        return {
            'python_version': str(sys.version),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'platform': sys.platform,
            'processor': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
        }
    
    def _calculate_benchmark_summary(self, results: List[Dict]) -> Dict:
        """Calculate benchmark summary statistics"""
        if not results:
            return {}
        
        # Separate successful and failed results
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        summary = {
            'total_tests': len(results),
            'successful_tests': len(successful_results),
            'failed_tests': len(failed_results),
            'success_rate': len(successful_results) / len(results) if results else 0
        }
        
        if successful_results:
            # Performance statistics
            execution_times = [r['execution_time'] for r in successful_results]
            memory_usage = [r['memory_usage'] for r in successful_results]
            
            summary['performance_stats'] = {
                'avg_execution_time': np.mean(execution_times),
                'std_execution_time': np.std(execution_times),
                'min_execution_time': np.min(execution_times),
                'max_execution_time': np.max(execution_times),
                'avg_memory_usage': np.mean(memory_usage),
                'std_memory_usage': np.std(memory_usage)
            }
            
            # Performance by method
            method_performance = {}
            for result in successful_results:
                method = result['configuration'].get('method', 'unknown')
                if method not in method_performance:
                    method_performance[method] = []
                method_performance[method].append(result['execution_time'])
            
            summary['method_performance'] = {
                method: {
                    'avg_time': np.mean(times),
                    'std_time': np.std(times),
                    'count': len(times)
                }
                for method, times in method_performance.items()
            }
            
            # Quality metrics
            sharpe_ratios = [r['optimization_result'].get('sharpe_ratio', 0) for r in successful_results]
            summary['quality_stats'] = {
                'avg_sharpe_ratio': np.mean(sharpe_ratios),
                'std_sharpe_ratio': np.std(sharpe_ratios),
                'min_sharpe_ratio': np.min(sharpe_ratios),
                'max_sharpe_ratio': np.max(sharpe_ratios)
            }
        
        return summary
    
    def _save_benchmark_results(self, results: Dict, filepath: str = None):
        """Save benchmark results to file"""
        if filepath is None:
            timestamp = int(time.time())
            filepath = f"benchmark_results_{timestamp}.json"
        
        import json
        
        # Convert numpy arrays to lists for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            return obj
        
        def recursive_convert(data):
            if isinstance(data, dict):
                return {k: recursive_convert(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [recursive_convert(item) for item in data]
            else:
                return convert_numpy(data)
        
        json_results = recursive_convert(results)
        
        with open(filepath, 'w') as f:
            json.dump(json_results, f, indent=2, default=str)
        
        self.logger.info(f"Benchmark results saqlandi: {filepath}")
    
    def compare_methods(self, method_comparison: Dict) -> Dict:
        """
        Compare different optimization methods
        
        Args:
            method_comparison: Method comparison configuration
            
        Returns:
            Method comparison results
        """
        comparison_results = {
            'methods': list(method_comparison.keys()),
            'comparison_metrics': [],
            'recommendations': []
        }
        
        # Run each method with same configuration
        base_config = method_comparison.get('base_config', {})
        
        for method in comparison_results['methods']:
            config = base_config.copy()
            config['method'] = method
            
            result = self._run_single_benchmark(config)
            comparison_results['comparison_metrics'].append({
                'method': method,
                'execution_time': result['execution_time'],
                'memory_usage': result['memory_usage'],
                'success': result['success'],
                'sharpe_ratio': result['optimization_result'].get('sharpe_ratio', 0)
            })
        
        # Generate recommendations
        successful_metrics = [m for m in comparison_results['comparison_metrics'] if m['success']]
        
        if successful_metrics:
            # Best performance
            fastest = min(successful_metrics, key=lambda x: x['execution_time'])
            best_quality = max(successful_metrics, key=lambda x: x['sharpe_ratio'])
            
            comparison_results['recommendations'] = [
                f"Fastest method: {fastest['method']} ({fastest['execution_time']:.4f}s)",
                f"Highest Sharpe ratio: {best_quality['method']} ({best_quality['sharpe_ratio']:.4f})"
            ]
        
        return comparison_results
    
    def generate_performance_report(self, 
                                  save_path: Optional[str] = None,
                                  include_plots: bool = True) -> str:
        """Generate comprehensive performance report"""
        if not self.benchmark_results:
            return "No benchmark results available"
        
        results = self.benchmark_results
        summary = results['summary']
        
        # Generate report text
        report = f"""
        QUANTUM PORTFOLIO SYSTEM PERFORMANCE REPORT
        ==========================================
        
        Timestamp: {time.ctime(results['timestamp'])}
        System Info: {results['system_info']['cpu_count']} CPUs, {results['system_info']['memory_total_gb']:.1f}GB RAM
        
        BENCHMARK SUMMARY
        -----------------
        Total Tests: {summary['total_tests']}
        Successful Tests: {summary['successful_tests']}
        Failed Tests: {summary['failed_tests']}
        Success Rate: {summary['success_rate']:.2%}
        
        """
        
        if 'performance_stats' in summary:
            perf = summary['performance_stats']
            report += f"""
        PERFORMANCE STATISTICS
        ---------------------
        Average Execution Time: {perf['avg_execution_time']:.4f}s ± {perf['std_execution_time']:.4f}s
        Min/Max Execution Time: {perf['min_execution_time']:.4f}s / {perf['max_execution_time']:.4f}s
        Average Memory Usage: {perf['avg_memory_usage']:.2f}MB ± {perf['std_memory_usage']:.2f}MB
            """
        
        if 'method_performance' in summary:
            report += "\nMETHOD PERFORMANCE\n-----------------\n"
            for method, stats in summary['method_performance'].items():
                report += f"{method:20}: {stats['avg_time']:.4f}s ± {stats['std_time']:.4f}s ({stats['count']} tests)\n"
        
        if 'quality_stats' in summary:
            quality = summary['quality_stats']
            report += f"""
        QUALITY STATISTICS
        -----------------
        Average Sharpe Ratio: {quality['avg_sharpe_ratio']:.4f} ± {quality['std_sharpe_ratio']:.4f}
        Min/Max Sharpe Ratio: {quality['min_sharpe_ratio']:.4f} / {quality['max_sharpe_ratio']:.4f}
            """
        
        # Add recommendations
        report += "\nRECOMMENDATIONS\n---------------\n"
        report += self._generate_report_recommendations(summary)
        
        # Save report
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report)
            self.logger.info(f"Performance report saqlandi: {save_path}")
        
        return report
    
    def _generate_report_recommendations(self, summary: Dict) -> str:
        """Generate recommendations based on benchmark results"""
        recommendations = []
        
        # Success rate recommendations
        if summary['success_rate'] < 0.8:
            recommendations.append("- Success rate is low. Consider debugging optimization algorithms.")
        
        # Performance recommendations
        if 'performance_stats' in summary:
            avg_time = summary['performance_stats']['avg_execution_time']
            if avg_time > 5.0:
                recommendations.append("- Average execution time is high. Consider optimization improvements.")
        
        # Quality recommendations
        if 'quality_stats' in summary:
            avg_sharpe = summary['quality_stats']['avg_sharpe_ratio']
            if avg_sharpe < 0.5:
                recommendations.append("- Sharpe ratios are low. Review risk management parameters.")
        
        return "\n".join(recommendations) if recommendations else "- Performance looks good!"