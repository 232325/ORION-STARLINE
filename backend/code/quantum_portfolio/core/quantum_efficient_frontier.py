"""
Quantum Efficient Frontier Implementation
=========================================

Quantum-enhanced efficient frontier calculations and visualization.
Bu modul quantum computing yordamida efficient frontier ni hisoblash va tahlil qilish.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize
import logging

class QuantumEfficientFrontier:
    """
    Quantum Efficient Frontier - Optimized portfolio selection in quantum space
    """
    
    def __init__(self, quantum_portfolio_theory):
        """
        Initialize quantum efficient frontier
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
        """
        self.qpt = quantum_portfolio_theory
        self.frontier_data = None
        self.capital_market_line = None
        self.quantum_region = None
        
        self.logger = logging.getLogger(__name__)
    
    def construct_quantum_efficient_frontier(self, 
                                           n_portfolios: int = 200,
                                           risk_range: Optional[Tuple[float, float]] = None,
                                           quantum_noise_level: float = 0.01) -> Dict:
        """
        Quantum efficient frontier construction
        
        Args:
            n_portfolios: Portfolio count for frontier
            risk_range: Risk range (volatility)
            quantum_noise_level: Quantum noise level in calculations
            
        Returns:
            Complete frontier data with quantum enhancements
        """
        if self.qpt.covariance_matrix is None:
            raise ValueError("Avval portfolio ma'lumotlarini yuklang")
        
        # Get expected returns and covariance
        expected_returns = self.qpt._quantum_expected_returns()
        covariance_matrix = self.qpt.covariance_matrix.copy()
        
        # Add quantum noise to covariance matrix
        quantum_noise = np.random.normal(0, quantum_noise_level, 
                                       covariance_matrix.shape)
        covariance_matrix += quantum_noise
        
        # Define risk range if not provided
        if risk_range is None:
            min_risk = np.sqrt(np.min(np.diag(covariance_matrix))) * 0.5
            max_risk = np.sqrt(np.max(np.diag(covariance_matrix))) * 2.0
            risk_range = (min_risk, max_risk)
        
        # Create target risk levels
        target_risks = np.linspace(risk_range[0], risk_range[1], n_portfolios)
        
        efficient_portfolios = []
        frontier_points = []
        
        for target_risk in target_risks:
            try:
                portfolio = self._optimize_for_risk(target_risk, expected_returns, covariance_matrix)
                if portfolio['success']:
                    efficient_portfolios.append(portfolio)
                    frontier_points.append((portfolio['volatility'], portfolio['expected_return']))
            except Exception as e:
                self.logger.warning(f"Risk {target_risk} uchun optimizatsiya muvaffaqiyatsiz: {e}")
                continue
        
        if not efficient_portfolios:
            raise RuntimeError("Efficient frontier yaratish uchun bitta ham muvaffaqiyatli portfolio topilmadi")
        
        # Sort by risk
        frontier_points.sort(key=lambda x: x[0])
        
        # Extract efficient frontier data
        efficient_returns = [point[1] for point in frontier_points]
        efficient_risks = [point[0] for point in frontier_points]
        
        # Calculate capital market line
        self.capital_market_line = self._calculate_capital_market_line(
            efficient_portfolios, efficient_risks, efficient_returns
        )
        
        # Identify quantum advantage regions
        self.quantum_region = self._identify_quantum_advantage_regions(
            efficient_portfolios, efficient_risks, efficient_returns
        )
        
        self.frontier_data = {
            'efficient_portfolios': efficient_portfolios,
            'efficient_returns': efficient_returns,
            'efficient_risks': efficient_risks,
            'capital_market_line': self.capital_market_line,
            'quantum_regions': self.quantum_region,
            'quantum_noise_level': quantum_noise_level
        }
        
        self.logger.info(f"Quantum efficient frontier yaratildi: {len(efficient_portfolios)} portfolio")
        return self.frontier_data
    
    def _optimize_for_risk(self, 
                         target_risk: float,
                         expected_returns: np.ndarray,
                         covariance_matrix: np.ndarray) -> Dict:
        """
        Specific risk level uchun optimizatsiya
        """
        n_assets = len(expected_returns)
        
        # Objective: maximize expected return for given risk
        def objective(weights):
            return -np.sum(weights * expected_returns)  # Minimize negative return
        
        # Risk constraint
        def risk_constraint(weights):
            portfolio_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
            return portfolio_risk - target_risk
        
        # Budget constraint
        def budget_constraint(weights):
            return np.sum(weights) - 1.0
        
        # Bounds
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': budget_constraint},
            {'type': 'ineq', 'fun': risk_constraint}
        ]
        
        # Initial guess
        x0 = np.ones(n_assets) / n_assets
        
        # Optimization
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9, 'disp': False}
        )
        
        if result.success:
            weights = result.x
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
            
            # Calculate quantum enhanced metrics
            quantum_entropy = self.qpt._calculate_quantum_entropy(weights)
            quantum_coherence = self.qpt._calculate_quantum_coherence(weights)
            
            return {
                'weights': weights,
                'expected_return': portfolio_return,
                'volatility': portfolio_risk,
                'sharpe_ratio': (portfolio_return - self.qpt.risk_free_rate) / portfolio_risk,
                'quantum_entropy': quantum_entropy,
                'quantum_coherence': quantum_coherence,
                'quantum_advantage': quantum_entropy * 0.1 + quantum_coherence * 0.05,
                'success': True
            }
        else:
            return {'success': False, 'message': result.message}
    
    def _calculate_capital_market_line(self, 
                                     portfolios: List[Dict],
                                     risks: List[float],
                                     returns: List[float]) -> Dict:
        """
        Capital Market Line hisoblash
        """
        if not portfolios:
            return {}
        
        # Find tangent portfolio (maximum Sharpe ratio)
        max_sharpe_idx = np.argmax([p['sharpe_ratio'] for p in portfolios])
        tangent_portfolio = portfolios[max_sharpe_idx]
        
        # Risk-free rate
        rf_rate = self.qpt.risk_free_rate
        
        # Capital Market Line parameters
        tangent_return = tangent_portfolio['expected_return']
        tangent_risk = tangent_portfolio['volatility']
        
        # Slope (Sharpe ratio of tangent portfolio)
        slope = (tangent_return - rf_rate) / tangent_risk
        
        # Capital Market Line equation: E(R) = rf_rate + slope * risk
        cml_risks = np.linspace(0, max(risks) * 1.5, 100)
        cml_returns = rf_rate + slope * cml_risks
        
        return {
            'tangent_portfolio': tangent_portfolio,
            'risk_free_rate': rf_rate,
            'slope': slope,
            'cml_risks': cml_risks.tolist(),
            'cml_returns': cml_returns.tolist(),
            'tangency_point': (tangent_risk, tangent_return)
        }
    
    def _identify_quantum_advantage_regions(self, 
                                          portfolios: List[Dict],
                                          risks: List[float],
                                          returns: List[float]) -> Dict:
        """
        Quantum advantage regions identification
        """
        if not portfolios:
            return {}
        
        # Calculate quantum advantage metrics for each portfolio
        quantum_advantages = [p.get('quantum_advantage', 0) for p in portfolios]
        
        # Identify regions with highest quantum advantage
        sorted_indices = np.argsort(quantum_advantages)[::-1]  # Sort descending
        
        high_quantum_advantage_portfolios = [portfolios[i] for i in sorted_indices[:20]]
        high_quantum_risks = [risks[i] for i in sorted_indices[:20]]
        high_quantum_returns = [returns[i] for i in sorted_indices[:20]]
        
        # Find quantum sweet spot (high return, high quantum advantage)
        quantum_scores = []
        for i, portfolio in enumerate(portfolios):
            # Score based on return and quantum advantage
            normalized_return = (portfolio['expected_return'] - min(returns)) / (max(returns) - min(returns))
            quantum_score = normalized_return * 0.6 + quantum_advantages[i] * 0.4
            quantum_scores.append(quantum_score)
        
        sweet_spot_idx = np.argmax(quantum_scores)
        
        return {
            'high_quantum_advantage_portfolios': high_quantum_advantage_portfolios,
            'high_quantum_risks': high_quantum_risks,
            'high_quantum_returns': high_quantum_returns,
            'quantum_sweet_spot': {
                'portfolio': portfolios[sweet_spot_idx],
                'risk': risks[sweet_spot_idx],
                'return': returns[sweet_spot_idx],
                'quantum_score': quantum_scores[sweet_spot_idx]
            },
            'quantum_advantage_threshold': np.percentile(quantum_advantages, 75)
        }
    
    def find_optimal_portfolio(self, 
                             risk_tolerance: str = 'moderate',
                             target_sharpe: Optional[float] = None) -> Dict:
        """
        Optimal portfolio topish
        
        Args:
            risk_tolerance: 'conservative', 'moderate', 'aggressive'
            target_sharpe: Target Sharpe ratio
            
        Returns:
            Optimal portfolio selection
        """
        if not self.frontier_data:
            raise ValueError("Avval efficient frontier yarating")
        
        portfolios = self.frontier_data['efficient_portfolios']
        
        if target_sharpe is not None:
            # Find portfolio closest to target Sharpe ratio
            sharpe_ratios = [p['sharpe_ratio'] for p in portfolios]
            best_idx = np.argmin([abs(sr - target_sharpe) for sr in sharpe_ratios])
            optimal_portfolio = portfolios[best_idx]
        else:
            # Risk tolerance based selection
            if risk_tolerance == 'conservative':
                # Low risk preference
                sorted_by_risk = sorted(portfolios, key=lambda x: x['volatility'])
                optimal_portfolio = sorted_by_risk[0]
            elif risk_tolerance == 'aggressive':
                # High return preference
                sorted_by_return = sorted(portfolios, key=lambda x: x['expected_return'], reverse=True)
                optimal_portfolio = sorted_by_return[0]
            else:  # moderate
                # Best Sharpe ratio
                optimal_portfolio = max(portfolios, key=lambda x: x['sharpe_ratio'])
        
        # Add asset allocations
        asset_allocation = {}
        for i, weight in enumerate(optimal_portfolio['weights']):
            if weight > 0.001:  # Only include significant weights
                asset_allocation[self.qpt.assets[i]] = weight
        
        optimal_portfolio['asset_allocation'] = asset_allocation
        optimal_portfolio['risk_tolerance'] = risk_tolerance
        
        return optimal_portfolio
    
    def visualize_frontier(self, 
                          save_path: Optional[str] = None,
                          show_quantum_regions: bool = True) -> None:
        """
        Efficient frontier visualization
        
        Args:
            save_path: PNG fayl saqlash yo'li
            show_quantum_regions: Quantum regions ko'rsatish
        """
        if not self.frontier_data:
            raise ValueError("Avval efficient frontier yarating")
        
        plt.figure(figsize=(12, 8))
        
        risks = self.frontier_data['efficient_risks']
        returns = self.frontier_data['efficient_returns']
        
        # Plot efficient frontier
        plt.plot(risks, returns, 'b-', linewidth=2, label='Quantum Efficient Frontier')
        
        # Plot capital market line
        if self.capital_market_line:
            cml_risks = self.capital_market_line['cml_risks']
            cml_returns = self.capital_market_line['cml_returns']
            plt.plot(cml_risks, cml_returns, 'r--', linewidth=2, label='Capital Market Line')
            
            # Mark tangent portfolio
            tangency = self.capital_market_line['tangency_point']
            plt.plot(tangency[0], tangency[1], 'ro', markersize=10, label='Tangent Portfolio')
        
        # Plot quantum advantage regions
        if show_quantum_regions and self.quantum_region:
            high_risks = self.quantum_region['high_quantum_risks']
            high_returns = self.quantum_region['high_quantum_returns']
            
            plt.scatter(high_risks, high_returns, 
                       c='green', alpha=0.6, s=50, label='High Quantum Advantage')
            
            # Mark quantum sweet spot
            sweet_spot = self.quantum_region['quantum_sweet_spot']
            plt.plot(sweet_spot['risk'], sweet_spot['return'], 
                    'go', markersize=15, label='Quantum Sweet Spot')
        
        # Plot individual assets
        expected_returns = self.qpt._quantum_expected_returns()
        asset_risks = np.sqrt(np.diag(self.qpt.covariance_matrix))
        
        for i, asset in enumerate(self.qpt.assets):
            plt.plot(asset_risks[i], expected_returns[i], 'ko', markersize=8)
            plt.annotate(asset, (asset_risks[i], expected_returns[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        plt.xlabel('Volatility (Risk)')
        plt.ylabel('Expected Return')
        plt.title('Quantum Efficient Frontier')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add quantum advantage annotation
        if self.quantum_region:
            sweet_spot = self.quantum_region['quantum_sweet_spot']
            plt.annotate(f"Quantum Sweet Spot\\nReturn: {sweet_spot['return']:.3f}\\nRisk: {sweet_spot['risk']:.3f}\\nScore: {sweet_spot['quantum_score']:.3f}",
                        xy=(sweet_spot['risk'], sweet_spot['return']),
                        xytext=(50, 50), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Frontier visualization saqlandi: {save_path}")
        else:
            plt.show()
    
    def analyze_portfolio_performance(self, 
                                    portfolio_weights: np.ndarray,
                                    benchmark_weights: Optional[np.ndarray] = None) -> Dict:
        """
        Portfolio performance analysis
        
        Args:
            portfolio_weights: Portfolio og'irliklari
            benchmark_weights: Benchmark og'irliklari
            
        Returns:
            Performance metrics
        """
        # Calculate portfolio metrics
        portfolio_return = np.sum(portfolio_weights * self.qpt._quantum_expected_returns())
        portfolio_risk = np.sqrt(np.dot(portfolio_weights, 
                                      np.dot(self.qpt.covariance_matrix, portfolio_weights)))
        
        portfolio_entropy = self.qpt._calculate_quantum_entropy(portfolio_weights)
        portfolio_coherence = self.qpt._calculate_quantum_coherence(portfolio_weights)
        
        # Risk decomposition
        risk_decomposition = self.qpt.quantum_risk_decomposition(portfolio_weights)
        
        # Performance analysis
        analysis = {
            'portfolio_return': portfolio_return,
            'portfolio_risk': portfolio_risk,
            'portfolio_sharpe': (portfolio_return - self.qpt.risk_free_rate) / portfolio_risk,
            'quantum_entropy': portfolio_entropy,
            'quantum_coherence': portfolio_coherence,
            'quantum_diversification': risk_decomposition['quantum_diversification'],
            'concentration_risk': risk_decomposition['concentration_risk'],
            'risk_decomposition': risk_decomposition
        }
        
        # Benchmark comparison
        if benchmark_weights is not None:
            benchmark_return = np.sum(benchmark_weights * self.qpt._quantum_expected_returns())
            benchmark_risk = np.sqrt(np.dot(benchmark_weights, 
                                          np.dot(self.qpt.covariance_matrix, benchmark_weights)))
            
            analysis['benchmark_return'] = benchmark_return
            analysis['benchmark_risk'] = benchmark_risk
            analysis['benchmark_sharpe'] = (benchmark_return - self.qpt.risk_free_rate) / benchmark_risk
            analysis['outperformance_return'] = portfolio_return - benchmark_return
            analysis['outperformance_risk'] = portfolio_risk - benchmark_risk
            analysis['outperformance_sharpe'] = analysis['portfolio_sharpe'] - analysis['benchmark_sharpe']
        
        return analysis
    
    def get_risk_contribution_matrix(self) -> np.ndarray:
        """
        Asset'lar o'rtasidagi risk contribution matrix
        """
        if self.frontier_data is None:
            return None
        
        n_assets = len(self.qpt.assets)
        contribution_matrix = np.zeros((n_assets, n_assets))
        
        # Calculate marginal contributions for each portfolio on frontier
        for portfolio in self.frontier_data['efficient_portfolios']:
            weights = portfolio['weights']
            portfolio_risk = portfolio['volatility']
            
            for i in range(n_assets):
                for j in range(n_assets):
                    # Marginal contribution of asset i to asset j's risk
                    marginal_contrib = weights[i] * self.qpt.covariance_matrix[i][j] * weights[j]
                    contribution_matrix[i][j] += marginal_contrib
        
        # Average across all portfolios
        n_portfolios = len(self.frontier_data['efficient_portfolios'])
        if n_portfolios > 0:
            contribution_matrix /= n_portfolios
        
        return contribution_matrix
    
    def export_frontier_data(self, filepath: str) -> None:
        """
        Frontier ma'lumotlarini export qilish
        """
        if not self.frontier_data:
            raise ValueError("Avval efficient frontier yarating")
        
        export_data = {
            'frontier_data': self.frontier_data,
            'assets': self.qpt.assets,
            'timestamp': pd.Timestamp.now().isoformat(),
            'quantum_parameters': {
                'coherence_time': self.qpt.quantum_coherence_time,
                'risk_free_rate': self.qpt.risk_free_rate
            }
        }
        
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
        
        export_data = recursive_convert(export_data)
        
        with open(filepath, 'w') as f:
            import json
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Frontier ma'lumotlari export qilindi: {filepath}")