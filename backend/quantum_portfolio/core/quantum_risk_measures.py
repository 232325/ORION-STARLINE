"""
Quantum Risk Measures Implementation
====================================

Quantum-enhanced risk measures and assessment tools.
Bu modul quantum computing yordamida risk o'lchovlarini hisoblash va tahlil qilish.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
from scipy import stats
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt

class QuantumRiskMeasures:
    """
    Quantum Risk Measures - Advanced risk assessment using quantum computing
    """
    
    def __init__(self, quantum_portfolio_theory):
        """
        Initialize quantum risk measures
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
        """
        self.qpt = quantum_portfolio_theory
        self.risk_metrics = {}
        
        self.logger = logging.getLogger(__name__)
    
    def quantum_value_at_risk(self, 
                            weights: np.ndarray,
                            confidence_levels: List[float] = [0.95, 0.99],
                            time_horizon: int = 1,
                            quantum_enhancement: bool = True) -> Dict:
        """
        Quantum Value at Risk (VaR) calculation
        
        Args:
            weights: Portfolio weights
            confidence_levels: Confidence levels for VaR
            time_horizon: Time horizon in days
            quantum_enhancement: Apply quantum corrections
            
        Returns:
            VaR values for each confidence level
        """
        if self.qpt.returns_data is None:
            raise ValueError("Portfolio returns ma'lumotlari mavjud emas")
        
        # Historical returns
        portfolio_returns = self._calculate_portfolio_returns(weights)
        
        # Quantum enhancement of returns distribution
        if quantum_enhancement:
            enhanced_returns = self._apply_quantum_corrections(portfolio_returns)
        else:
            enhanced_returns = portfolio_returns
        
        # Calculate VaR for each confidence level
        var_results = {}
        
        for confidence in confidence_levels:
            # Historical VaR
            historical_var = -np.percentile(enhanced_returns, (1 - confidence) * 100)
            
            # Parametric VaR (assuming normal distribution)
            mean_return = np.mean(enhanced_returns)
            std_return = np.std(enhanced_returns)
            z_score = stats.norm.ppf(1 - confidence)
            parametric_var = -(mean_return + z_score * std_return * np.sqrt(time_horizon))
            
            # Monte Carlo VaR (simplified)
            mc_var = self._monte_carlo_var(weights, confidence, time_horizon)
            
            # Quantum-adjusted VaR
            quantum_var = self._quantum_var_adjustment(historical_var, parametric_var, mc_var)
            
            var_results[f'VaR_{int(confidence*100)}'] = {
                'historical': historical_var,
                'parametric': parametric_var,
                'monte_carlo': mc_var,
                'quantum_adjusted': quantum_var,
                'confidence_level': confidence
            }
        
        return var_results
    
    def quantum_expected_shortfall(self, 
                                 weights: np.ndarray,
                                 confidence_levels: List[float] = [0.95, 0.99],
                                 time_horizon: int = 1) -> Dict:
        """
        Quantum Expected Shortfall (CVaR) calculation
        
        Args:
            weights: Portfolio weights
            confidence_levels: Confidence levels
            time_horizon: Time horizon in days
            
        Returns:
            Expected Shortfall values
        """
        # Get VaR values first
        var_results = self.quantum_value_at_risk(weights, confidence_levels, time_horizon)
        
        portfolio_returns = self._calculate_portfolio_returns(weights)
        enhanced_returns = self._apply_quantum_corrections(portfolio_returns)
        
        es_results = {}
        
        for confidence in confidence_levels:
            var_value = var_results[f'VaR_{int(confidence*100)}']['quantum_adjusted']
            
            # Historical Expected Shortfall
            threshold_returns = enhanced_returns[enhanced_returns <= -var_value]
            historical_es = -np.mean(threshold_returns) if len(threshold_returns) > 0 else var_value
            
            # Quantum Expected Shortfall enhancement
            quantum_corr_factor = self._calculate_quantum_correlation_factor(weights)
            quantum_es = historical_es * (1 + quantum_corr_factor * 0.1)
            
            es_results[f'ES_{int(confidence*100)}'] = {
                'historical_es': historical_es,
                'quantum_es': quantum_es,
                'quantum_correlation_factor': quantum_corr_factor,
                'confidence_level': confidence
            }
        
        return es_results
    
    def quantum_maximum_drawdown(self, 
                               weights: np.ndarray,
                               period: str = '1Y') -> Dict:
        """
        Quantum Maximum Drawdown analysis
        
        Args:
            weights: Portfolio weights
            period: Analysis period ('1M', '3M', '6M', '1Y', '3Y', '5Y')
            
        Returns:
            Maximum drawdown metrics
        """
        portfolio_returns = self._calculate_portfolio_returns(weights)
        portfolio_prices = (1 + portfolio_returns).cumprod()
        
        # Calculate running maximum
        running_max = portfolio_prices.expanding().max()
        
        # Calculate drawdown
        drawdown = (portfolio_prices - running_max) / running_max
        
        # Maximum drawdown
        max_drawdown = drawdown.min()
        
        # Drawdown duration analysis
        in_drawdown = drawdown < 0
        drawdown_periods = []
        
        start_idx = None
        for i, is_dd in enumerate(in_drawdown):
            if is_dd and start_idx is None:
                start_idx = i
            elif not is_dd and start_idx is not None:
                drawdown_periods.append(i - start_idx)
                start_idx = None
        
        # Average drawdown duration
        avg_drawdown_duration = np.mean(drawdown_periods) if drawdown_periods else 0
        
        # Recovery time (simplified)
        max_dd_idx = drawdown.idxmin()
        recovery_prices = portfolio_prices[max_dd_idx:]
        recovery_idx = (recovery_prices >= running_max.iloc[max_dd_idx]).idxmax() if len(recovery_prices) > 0 else None
        recovery_time = (recovery_idx - max_dd_idx) if recovery_idx is not None else None
        
        # Quantum drawdown enhancement
        quantum_dd_factor = self._calculate_quantum_drawdown_factor(weights)
        
        return {
            'maximum_drawdown': max_drawdown,
            'maximum_drawdown_date': max_dd_idx,
            'average_drawdown_duration': avg_drawdown_duration,
            'recovery_time': recovery_time,
            'quantum_drawdown_factor': quantum_dd_factor,
            'drawdown_series': drawdown,
            'number_of_drawdowns': len(drawdown_periods)
        }
    
    def quantum_beta_calculation(self, 
                               weights: np.ndarray,
                               market_returns: Optional[pd.Series] = None,
                               market_name: str = 'market') -> Dict:
        """
        Quantum Beta calculation for portfolio
        
        Args:
            weights: Portfolio weights
            market_returns: Market benchmark returns
            market_name: Benchmark name
            
        Returns:
            Beta and related metrics
        """
        portfolio_returns = self._calculate_portfolio_returns(weights)
        
        # If market returns not provided, create synthetic market
        if market_returns is None:
            market_returns = self._create_synthetic_market()
        
        # Align data
        aligned_data = pd.concat([portfolio_returns, market_returns], axis=1).dropna()
        portfolio_aligned = aligned_data.iloc[:, 0]
        market_aligned = aligned_data.iloc[:, 1]
        
        # Classical beta
        classical_beta = np.cov(portfolio_aligned, market_aligned)[0, 1] / np.var(market_aligned)
        
        # Quantum beta calculation
        quantum_beta = self._calculate_quantum_beta(portfolio_aligned, market_aligned)
        
        # Alpha calculation
        portfolio_mean = np.mean(portfolio_aligned)
        market_mean = np.mean(market_aligned)
        quantum_alpha = portfolio_mean - quantum_beta * market_mean
        
        # R-squared
        r_squared = np.corrcoef(portfolio_aligned, market_aligned)[0, 1] ** 2
        
        # Information ratio
        excess_returns = portfolio_aligned - market_aligned
        information_ratio = np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) > 0 else 0
        
        return {
            'classical_beta': classical_beta,
            'quantum_beta': quantum_beta,
            'alpha': quantum_alpha,
            'r_squared': r_squared,
            'information_ratio': information_ratio,
            'correlation': np.corrcoef(portfolio_aligned, market_aligned)[0, 1],
            'market_name': market_name
        }
    
    def quantum_tail_risk_measures(self, 
                                 weights: np.ndarray,
                                 tail_percentiles: List[float] = [1, 5, 10]) -> Dict:
        """
        Quantum tail risk measures
        
        Args:
            weights: Portfolio weights
            tail_percentiles: Tail percentiles to analyze
            
        Returns:
            Tail risk metrics
        """
        portfolio_returns = self._calculate_portfolio_returns(weights)
        enhanced_returns = self._apply_quantum_corrections(portfolio_returns)
        
        tail_risk_results = {}
        
        for percentile in tail_percentiles:
            tail_threshold = np.percentile(enhanced_returns, percentile)
            tail_returns = enhanced_returns[enhanced_returns <= tail_threshold]
            
            # Tail risk metrics
            tail_mean = np.mean(tail_returns) if len(tail_returns) > 0 else tail_threshold
            tail_std = np.std(tail_returns) if len(tail_returns) > 0 else 0
            tail_skewness = stats.skew(tail_returns) if len(tail_returns) > 0 else 0
            tail_kurtosis = stats.kurtosis(tail_returns) if len(tail_returns) > 0 else 0
            
            # Quantum tail risk enhancement
            quantum_tail_factor = self._calculate_quantum_tail_factor(weights, tail_threshold)
            
            tail_risk_results[f'tail_{percentile}'] = {
                'threshold': tail_threshold,
                'mean_return': tail_mean,
                'volatility': tail_std,
                'skewness': tail_skewness,
                'kurtosis': tail_kurtosis,
                'tail_occurrences': len(tail_returns),
                'quantum_tail_factor': quantum_tail_factor
            }
        
        # Overall tail risk assessment
        all_tail_returns = []
        for percentile in tail_percentiles:
            tail_threshold = np.percentile(enhanced_returns, percentile)
            tail_returns = enhanced_returns[enhanced_returns <= tail_threshold]
            all_tail_returns.extend(tail_returns)
        
        overall_tail_risk = {
            'total_tail_events': len(all_tail_returns),
            'tail_risk_concentration': len(all_tail_returns) / len(enhanced_returns),
            'average_tail_loss': np.mean(all_tail_returns) if all_tail_returns else 0,
            'tail_risk_sharpe': np.mean(all_tail_returns) / np.std(all_tail_returns) if all_tail_returns and np.std(all_tail_returns) > 0 else 0
        }
        
        tail_risk_results['overall'] = overall_tail_risk
        
        return tail_risk_results
    
    def quantum_stress_testing(self, 
                             weights: np.ndarray,
                             stress_scenarios: List[Dict] = None) -> Dict:
        """
        Quantum stress testing framework
        
        Args:
            weights: Portfolio weights
            stress_scenarios: List of stress scenarios
            
        Returns:
            Stress test results
        """
        if stress_scenarios is None:
            stress_scenarios = self._get_default_stress_scenarios()
        
        stress_results = {}
        
        for scenario_name, scenario_data in stress_scenarios.items():
            # Apply scenario shocks
            stressed_returns = self._apply_stress_scenario(weights, scenario_data)
            
            # Calculate portfolio impact
            portfolio_return = np.mean(stressed_returns)
            portfolio_volatility = np.std(stressed_returns)
            
            # Calculate VaR under stress
            stressed_var_95 = -np.percentile(stressed_returns, 5)
            stressed_var_99 = -np.percentile(stressed_returns, 1)
            
            # Quantum stress factor
            quantum_stress_factor = self._calculate_quantum_stress_factor(weights, scenario_data)
            
            stress_results[scenario_name] = {
                'expected_return': portfolio_return,
                'volatility': portfolio_volatility,
                'var_95': stressed_var_95,
                'var_99': stressed_var_99,
                'quantum_stress_factor': quantum_stress_factor,
                'scenario_data': scenario_data
            }
        
        # Aggregate stress test summary
        summary = self._create_stress_test_summary(stress_results)
        stress_results['summary'] = summary
        
        return stress_results
    
    def _calculate_portfolio_returns(self, weights: np.ndarray) -> pd.Series:
        """Portfolio returns hisoblash"""
        if self.qpt.returns_data is None:
            raise ValueError("Returns ma'lumotlari mavjud emas")
        
        portfolio_returns = (self.qpt.returns_data * weights).sum(axis=1)
        return portfolio_returns
    
    def _apply_quantum_corrections(self, returns: pd.Series) -> np.ndarray:
        """Quantum corrections returns ga qo'llash"""
        # Convert to numpy for calculations
        returns_array = returns.values
        
        # Apply quantum noise model
        quantum_noise = np.random.normal(0, 0.001, len(returns_array))
        
        # Apply quantum interference patterns
        interference_pattern = self._generate_quantum_interference(len(returns_array))
        
        # Combined quantum effect
        quantum_corrections = quantum_noise * interference_pattern
        
        return returns_array + quantum_corrections
    
    def _generate_quantum_interference(self, n_points: int) -> np.ndarray:
        """Quantum interference pattern generation"""
        # Coherence time-based interference
        coherence_periods = int(self.qpt.quantum_coherence_time / 10)  # Simplified
        
        interference = np.ones(n_points)
        
        for i in range(n_points):
            # Sine wave interference based on coherence time
            phase = 2 * np.pi * i / coherence_periods
            interference[i] = 1 + 0.1 * np.sin(phase)
        
        return interference
    
    def _monte_carlo_var(self, weights: np.ndarray, confidence: float, time_horizon: int) -> float:
        """Monte Carlo VaR simulation"""
        n_simulations = 10000
        
        # Generate random scenarios
        random_scenarios = np.random.multivariate_normal(
            np.zeros(len(weights)),
            self.qpt.covariance_matrix,
            n_simulations
        )
        
        # Calculate portfolio returns
        portfolio_returns = np.dot(random_scenarios, weights)
        
        # Apply time scaling
        portfolio_returns *= np.sqrt(time_horizon)
        
        # Calculate VaR
        var = -np.percentile(portfolio_returns, (1 - confidence) * 100)
        
        return var
    
    def _quantum_var_adjustment(self, historical_var: float, parametric_var: float, mc_var: float) -> float:
        """Quantum VaR adjustment"""
        # Weighted average with quantum weights
        weights = [0.4, 0.3, 0.3]  # Historical, Parametric, MC
        combined_var = weights[0] * historical_var + weights[1] * parametric_var + weights[2] * mc_var
        
        # Quantum enhancement factor
        quantum_factor = np.exp(-self.qpt.quantum_coherence_time / 100)
        
        return combined_var * (1 + quantum_factor * 0.05)
    
    def _calculate_quantum_correlation_factor(self, weights: np.ndarray) -> float:
        """Quantum correlation factor hisoblash"""
        # Calculate portfolio concentration
        concentration = np.sum(weights ** 2)
        
        # Quantum correlation based on entanglement
        quantum_corr = 0.0
        for i in range(len(weights)):
            for j in range(i + 1, len(weights)):
                if i < len(self.qpt.assets) and j < len(self.qpt.assets):
                    asset1, asset2 = self.qpt.assets[i], self.qpt.assets[j]
                    entanglement = self.qpt._calculate_entanglement(asset1, asset2)
                    quantum_corr += entanglement * weights[i] * weights[j]
        
        return quantum_corr * (1 - concentration)
    
    def _calculate_quantum_drawdown_factor(self, weights: np.ndarray) -> float:
        """Quantum drawdown factor hisoblash"""
        # Diversification factor
        diversification = 1 - np.sum(weights ** 2)
        
        # Quantum coherence factor
        quantum_coherence = self.qpt._calculate_quantum_coherence(weights)
        
        return diversification * quantum_coherence
    
    def _calculate_quantum_beta(self, portfolio_returns: pd.Series, market_returns: pd.Series) -> float:
        """Quantum beta calculation"""
        # Classical covariance and variance
        classical_cov = np.cov(portfolio_returns, market_returns)[0, 1]
        market_var = np.var(market_returns)
        
        # Quantum adjustments
        quantum_correlation = np.corrcoef(portfolio_returns, market_returns)[0, 1]
        quantum_adjustment = np.exp(-self.qpt.quantum_coherence_time / 50)
        
        # Quantum beta
        quantum_beta = (classical_cov / market_var) * (1 + quantum_correlation * quantum_adjustment * 0.1)
        
        return quantum_beta
    
    def _create_synthetic_market(self) -> pd.Series:
        """Synthetic market returns yaratish"""
        # Simple market proxy based on all assets
        if self.qpt.returns_data is not None:
            market_returns = self.qpt.returns_data.mean(axis=1)
            return market_returns
        else:
            return pd.Series(np.random.normal(0.001, 0.02, 252), 
                           index=pd.date_range('2023-01-01', periods=252))
    
    def _calculate_quantum_tail_factor(self, weights: np.ndarray, tail_threshold: float) -> float:
        """Quantum tail factor hisoblash"""
        # Tail risk concentration
        tail_concentration = np.sum(weights[weights > 0.1])  # High concentration in tail
        
        # Quantum entanglement in tail conditions
        quantum_tail_entanglement = 0.0
        for i, weight in enumerate(weights):
            if weight > 0.05:  # Significant weight
                quantum_state = self.qpt.quantum_states.get(self.qpt.assets[i], np.array([1, 0]))
                tail_entanglement = np.abs(quantum_state[0] * np.conj(quantum_state[1]))
                quantum_tail_entanglement += tail_entanglement * weight
        
        return tail_concentration * quantum_tail_entanglement
    
    def _get_default_stress_scenarios(self) -> Dict:
        """Default stress testing scenarios"""
        return {
            'market_crash': {
                'type': 'equity_shock',
                'shock_size': -0.2,
                'affected_assets': 'equities'
            },
            'interest_rate_spike': {
                'type': 'rate_shock',
                'shock_size': 0.02,
                'affected_assets': 'all'
            },
            'volatility_spike': {
                'type': 'volatility_shock',
                'shock_multiplier': 2.0,
                'affected_assets': 'all'
            },
            'credit_spread_widening': {
                'type': 'credit_shock',
                'shock_size': 0.05,
                'affected_assets': 'credit'
            }
        }
    
    def _apply_stress_scenario(self, weights: np.ndarray, scenario: Dict) -> np.ndarray:
        """Stress scenario portfolio returns ga qo'llash"""
        portfolio_returns = self._calculate_portfolio_returns(weights)
        
        scenario_type = scenario['type']
        
        if scenario_type == 'equity_shock':
            shock_size = scenario['shock_size']
            stressed_returns = portfolio_returns + shock_size
        
        elif scenario_type == 'rate_shock':
            shock_size = scenario['shock_size']
            stressed_returns = portfolio_returns - shock_size * 0.1  # Simplified impact
        
        elif scenario_type == 'volatility_shock':
            multiplier = scenario['shock_multiplier']
            stressed_returns = portfolio_returns * multiplier
        
        elif scenario_type == 'credit_shock':
            shock_size = scenario['shock_size']
            stressed_returns = portfolio_returns - shock_size
        
        else:
            stressed_returns = portfolio_returns
        
        return stressed_returns.values
    
    def _calculate_quantum_stress_factor(self, weights: np.ndarray, scenario: Dict) -> float:
        """Quantum stress factor hisoblash"""
        # Portfolio concentration under stress
        concentration = np.max(weights)
        
        # Scenario severity
        severity = abs(scenario.get('shock_size', 0)) + scenario.get('shock_multiplier', 1) - 1
        
        # Quantum stress response
        quantum_response = self.qpt._calculate_quantum_coherence(weights)
        
        return concentration * severity * quantum_response
    
    def _create_stress_test_summary(self, stress_results: Dict) -> Dict:
        """Stress test summary yaratish"""
        # Extract worst case scenarios
        worst_var_95 = max([result['var_95'] for name, result in stress_results.items() 
                           if name != 'summary'])
        worst_var_99 = max([result['var_99'] for name, result in stress_results.items() 
                           if name != 'summary'])
        
        # Average impact
        avg_impact = np.mean([result['expected_return'] for name, result in stress_results.items() 
                             if name != 'summary'])
        
        # Most severe scenario
        most_severe = min(stress_results.items(), 
                         key=lambda x: x[1]['expected_return'] if x[0] != 'summary' else float('inf'))
        
        return {
            'worst_var_95': worst_var_95,
            'worst_var_99': worst_var_99,
            'average_impact': avg_impact,
            'most_severe_scenario': most_severe[0],
            'total_scenarios_tested': len([k for k in stress_results.keys() if k != 'summary'])
        }
    
    def visualize_risk_metrics(self, 
                             weights: np.ndarray,
                             save_path: Optional[str] = None) -> None:
        """Risk metrics visualization"""
        # Get risk metrics
        var_results = self.quantum_value_at_risk(weights)
        es_results = self.quantum_expected_shortfall(weights)
        dd_results = self.quantum_maximum_drawdown(weights)
        
        # Create subplot
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Quantum Risk Metrics Dashboard', fontsize=16)
        
        # VaR comparison
        var_levels = [95, 99]
        var_values = [var_results[f'VaR_{level}']['quantum_adjusted'] for level in var_levels]
        
        axes[0, 0].bar([f'VaR {level}%' for level in var_levels], var_values, color='red', alpha=0.7)
        axes[0, 0].set_title('Value at Risk (VaR)')
        axes[0, 0].set_ylabel('VaR')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Expected Shortfall
        es_values = [es_results[f'ES_{level}']['quantum_es'] for level in var_levels]
        
        axes[0, 1].bar([f'ES {level}%' for level in var_levels], es_values, color='orange', alpha=0.7)
        axes[0, 1].set_title('Expected Shortfall (ES)')
        axes[0, 1].set_ylabel('Expected Shortfall')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Drawdown series
        axes[1, 0].plot(dd_results['drawdown_series'], color='blue', alpha=0.7)
        axes[1, 0].axhline(y=dd_results['maximum_drawdown'], color='red', 
                          linestyle='--', label=f'Max DD: {dd_results["maximum_drawdown"]:.2%}')
        axes[1, 0].set_title('Drawdown Analysis')
        axes[1, 0].set_ylabel('Drawdown')
        axes[1, 0].legend()
        
        # Risk metrics summary
        metrics_text = f"""
        Max Drawdown: {dd_results['maximum_drawdown']:.2%}
        Recovery Time: {dd_results['recovery_time']} days
        Quantum DD Factor: {dd_results['quantum_drawdown_factor']:.3f}
        Number of DD: {dd_results['number_of_drawdowns']}
        """
        
        axes[1, 1].text(0.1, 0.5, metrics_text, transform=axes[1, 1].transAxes, 
                       fontsize=12, verticalalignment='center')
        axes[1, 1].set_title('Risk Metrics Summary')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Risk metrics visualization saqlandi: {save_path}")
        else:
            plt.show()