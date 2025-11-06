"""
Quantum Utility Functions Implementation
========================================

Quantum-enhanced utility functions for portfolio optimization.
Bu modul quantum utility funksiyalarini portfolio optimizatsiya uchun amalga oshiradi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
import logging
from scipy.optimize import minimize
import matplotlib.pyplot as plt

class QuantumUtilityFunctions:
    """
    Quantum Utility Functions - Advanced utility theory using quantum computing
    """
    
    def __init__(self, quantum_portfolio_theory):
        """
        Initialize quantum utility functions
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
        """
        self.qpt = quantum_portfolio_theory
        self.utility_functions = {}
        
        # Utility function types
        self.utility_types = {
            'classical': self._classical_utility,
            'quantum': self._quantum_utility,
            'quantum_entangled': self._quantum_entangled_utility,
            'quantum_coherent': self._quantum_coherent_utility,
            'quantum_risk_aversion': self._quantum_risk_aversion_utility,
            'quantum_diversification': self._quantum_diversification_utility,
            'quantum_information': self._quantum_information_utility
        }
        
        self.logger = logging.getLogger(__name__)
    
    def calculate_utility(self, 
                         weights: np.ndarray,
                         utility_type: str = 'quantum',
                         **kwargs) -> Dict:
        """
        Portfolio utility hisoblash
        
        Args:
            weights: Portfolio weights
            utility_type: Utility function type
            **kwargs: Additional parameters
            
        Returns:
            Utility value and components
        """
        if utility_type not in self.utility_types:
            raise ValueError(f"Qo'llab-quvvatlanmaydigan utility type: {utility_type}")
        
        utility_func = self.utility_types[utility_type]
        
        # Calculate utility
        result = utility_func(weights, **kwargs)
        
        # Add metadata
        result['utility_type'] = utility_type
        result['weights'] = weights
        
        return result
    
    def _classical_utility(self, 
                          weights: np.ndarray,
                          risk_aversion: float = 1.0,
                          target_return: Optional[float] = None) -> Dict:
        """
        Classical (Cobb-Douglas style) utility function
        """
        # Calculate portfolio statistics
        expected_return = np.sum(weights * self.qpt._quantum_expected_returns())
        portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
        volatility = np.sqrt(portfolio_variance)
        
        # Classical mean-variance utility
        utility = expected_return - 0.5 * risk_aversion * portfolio_variance
        
        # Add return constraint if specified
        penalty = 0
        if target_return is not None and expected_return < target_return:
            penalty = (target_return - expected_return) ** 2
        
        total_utility = utility - penalty
        
        return {
            'utility': total_utility,
            'expected_return': expected_return,
            'volatility': volatility,
            'risk_penalty': 0.5 * risk_aversion * portfolio_variance,
            'return_constraint_penalty': penalty,
            'utility_components': {
                'return_component': expected_return,
                'risk_component': -0.5 * risk_aversion * portfolio_variance
            }
        }
    
    def _quantum_utility(self, 
                        weights: np.ndarray,
                        risk_aversion: float = 1.0,
                        coherence_weight: float = 0.1) -> Dict:
        """
        Basic quantum utility function with coherence enhancement
        """
        # Classical base
        classical_result = self._classical_utility(weights, risk_aversion)
        
        # Quantum coherence
        quantum_coherence = self.qpt._calculate_quantum_coherence(weights)
        
        # Quantum entropy (diversification)
        quantum_entropy = self.qpt._calculate_quantum_entropy(weights)
        
        # Quantum enhancement
        quantum_enhancement = (quantum_coherence * coherence_weight + 
                             quantum_entropy * (1 - coherence_weight))
        
        # Enhanced utility
        enhanced_utility = classical_result['utility'] + quantum_enhancement
        
        return {
            'utility': enhanced_utility,
            'expected_return': classical_result['expected_return'],
            'volatility': classical_result['volatility'],
            'quantum_coherence': quantum_coherence,
            'quantum_entropy': quantum_entropy,
            'quantum_enhancement': quantum_enhancement,
            'utility_components': {
                **classical_result['utility_components'],
                'quantum_enhancement': quantum_enhancement
            }
        }
    
    def _quantum_entangled_utility(self, 
                                 weights: np.ndarray,
                                 risk_aversion: float = 1.0,
                                 entanglement_strength: float = 0.2) -> Dict:
        """
        Quantum entangled utility function
        Accounts for quantum entanglement between assets
        """
        # Base quantum utility
        quantum_result = self._quantum_utility(weights, risk_aversion)
        
        # Calculate pairwise entanglement
        total_entanglement = 0.0
        entanglement_contributions = {}
        
        for i in range(len(weights)):
            for j in range(i + 1, len(weights)):
                if i < len(self.qpt.assets) and j < len(self.qpt.assets):
                    asset1, asset2 = self.qpt.assets[i], self.qpt.assets[j]
                    entanglement = self.qpt._calculate_entanglement(asset1, asset2)
                    
                    # Asset weight contribution to entanglement
                    weight_product = weights[i] * weights[j]
                    entanglement_contribution = entanglement * weight_product
                    
                    total_entanglement += entanglement_contribution
                    entanglement_contributions[f'{asset1}-{asset2}'] = entanglement_contribution
        
        # Entangled utility enhancement
        entangled_enhancement = total_entanglement * entanglement_strength
        
        # Enhanced utility with entanglement
        entangled_utility = quantum_result['utility'] + entangled_enhancement
        
        return {
            'utility': entangled_utility,
            'expected_return': quantum_result['expected_return'],
            'volatility': quantum_result['volatility'],
            'total_entanglement': total_entanglement,
            'entangled_enhancement': entangled_enhancement,
            'entanglement_contributions': entanglement_contributions,
            'utility_components': {
                **quantum_result['utility_components'],
                'entangled_enhancement': entangled_enhancement
            }
        }
    
    def _quantum_coherent_utility(self, 
                                weights: np.ndarray,
                                risk_aversion: float = 1.0,
                                coherence_enhancement: float = 0.15) -> Dict:
        """
        Quantum coherent utility with phase alignment
        """
        # Base quantum utility
        quantum_result = self._quantum_utility(weights, risk_aversion)
        
        # Calculate quantum phase alignment
        phase_alignment = self._calculate_phase_alignment(weights)
        
        # Quantum coherence with phase effects
        coherent_coherence = quantum_result['quantum_coherence'] * (1 + phase_alignment)
        
        # Coherent enhancement
        coherent_enhancement = coherent_coherence * coherence_enhancement
        
        # Coherent utility
        coherent_utility = quantum_result['utility'] + coherent_enhancement
        
        return {
            'utility': coherent_utility,
            'expected_return': quantum_result['expected_return'],
            'volatility': quantum_result['volatility'],
            'phase_alignment': phase_alignment,
            'coherent_coherence': coherent_coherence,
            'coherent_enhancement': coherent_enhancement,
            'utility_components': {
                **quantum_result['utility_components'],
                'coherent_enhancement': coherent_enhancement
            }
        }
    
    def _quantum_risk_aversion_utility(self, 
                                     weights: np.ndarray,
                                     risk_aversion: float = 1.0,
                                     quantum_risk_sensitivity: float = 0.25) -> Dict:
        """
        Quantum-enhanced risk aversion utility
        """
        # Base calculations
        expected_return = np.sum(weights * self.qpt._quantum_expected_returns())
        portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
        volatility = np.sqrt(portfolio_variance)
        
        # Quantum risk measures
        quantum_risk = self._calculate_quantum_risk(weights)
        tail_risk = self._calculate_quantum_tail_risk(weights)
        
        # Risk aversion adjustment
        quantum_risk_adjustment = risk_aversion * (1 + quantum_risk_sensitivity)
        
        # Enhanced variance with quantum risk
        enhanced_variance = portfolio_variance + quantum_risk * 0.1 + tail_risk * 0.05
        
        # Quantum risk-averse utility
        utility = expected_return - 0.5 * quantum_risk_adjustment * enhanced_variance
        
        # Risk decomposition
        risk_decomposition = self.qpt.quantum_risk_decomposition(weights)
        
        return {
            'utility': utility,
            'expected_return': expected_return,
            'volatility': volatility,
            'quantum_risk': quantum_risk,
            'tail_risk': tail_risk,
            'enhanced_variance': enhanced_variance,
            'risk_decomposition': risk_decomposition,
            'utility_components': {
                'return_component': expected_return,
                'quantum_risk_component': -0.5 * quantum_risk_adjustment * enhanced_variance
            }
        }
    
    def _quantum_diversification_utility(self, 
                                       weights: np.ndarray,
                                       risk_aversion: float = 1.0,
                                       diversification_premium: float = 0.1) -> Dict:
        """
        Quantum diversification utility
        Emphasizes diversification benefits through quantum measures
        """
        # Base quantum utility
        quantum_result = self._quantum_utility(weights, risk_aversion)
        
        # Quantum diversification measures
        quantum_entropy = quantum_result['quantum_entropy']
        quantum_diversification = self._calculate_quantum_diversification_measure(weights)
        
        # Classical diversification ratio
        classical_diversification = quantum_result['risk_decomposition']['diversification_ratio']
        
        # Diversification premium
        diversification_bonus = (quantum_diversification + classical_diversification) * diversification_premium
        
        # Diversified utility
        diversified_utility = quantum_result['utility'] + diversification_bonus
        
        return {
            'utility': diversified_utility,
            'expected_return': quantum_result['expected_return'],
            'volatility': quantum_result['volatility'],
            'quantum_diversification': quantum_diversification,
            'classical_diversification': classical_diversification,
            'diversification_bonus': diversification_bonus,
            'diversification_components': {
                'entropy_component': quantum_entropy * diversification_premium,
                'ratio_component': classical_diversification * diversification_premium
            },
            'utility_components': {
                **quantum_result['utility_components'],
                'diversification_bonus': diversification_bonus
            }
        }
    
    def _quantum_information_utility(self, 
                                   weights: np.ndarray,
                                   risk_aversion: float = 1.0,
                                   information_weight: float = 0.2) -> Dict:
        """
        Quantum information utility
        Incorporates quantum information theory principles
        """
        # Base calculations
        expected_return = np.sum(weights * self.qpt._quantum_expected_returns())
        portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
        volatility = np.sqrt(portfolio_variance)
        
        # Quantum information measures
        quantum_information = self._calculate_quantum_information_content(weights)
        mutual_information = self._calculate_mutual_information(weights)
        conditional_entropy = self._calculate_conditional_entropy(weights)
        
        # Information-based enhancement
        information_enhancement = (quantum_information * 0.4 + 
                                 mutual_information * 0.3 + 
                                 (1 - conditional_entropy) * 0.3) * information_weight
        
        # Information utility
        utility = (expected_return - 0.5 * risk_aversion * portfolio_variance + 
                  information_enhancement)
        
        return {
            'utility': utility,
            'expected_return': expected_return,
            'volatility': volatility,
            'quantum_information': quantum_information,
            'mutual_information': mutual_information,
            'conditional_entropy': conditional_entropy,
            'information_enhancement': information_enhancement,
            'utility_components': {
                'return_component': expected_return,
                'risk_component': -0.5 * risk_aversion * portfolio_variance,
                'information_component': information_enhancement
            }
        }
    
    def optimize_portfolio_utility(self, 
                                  utility_type: str = 'quantum',
                                  risk_tolerance: str = 'moderate',
                                  **kwargs) -> Dict:
        """
        Portfolio optimization using quantum utility functions
        """
        # Set risk aversion based on risk tolerance
        risk_tolerances = {
            'conservative': 2.0,
            'moderate': 1.0,
            'aggressive': 0.5,
            'very_aggressive': 0.2
        }
        
        risk_aversion = risk_tolerances.get(risk_tolerance, 1.0)
        
        n_assets = len(self.qpt.assets)
        
        # Utility function for optimization
        def utility_objective(weights):
            result = self.calculate_utility(weights, utility_type, 
                                          risk_aversion=risk_aversion, **kwargs)
            return -result['utility']  # Minimize negative utility
        
        # Constraints
        constraints = []
        
        # Budget constraint
        constraints.append({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        
        # Bounds
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # Initial guess (equal weights)
        x0 = np.ones(n_assets) / n_assets
        
        # Optimization
        result = minimize(
            utility_objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9, 'disp': False}
        )
        
        if result.success:
            weights = result.x
            
            # Calculate final utility
            final_utility = self.calculate_utility(weights, utility_type, 
                                                  risk_aversion=risk_aversion, **kwargs)
            
            # Asset allocation
            allocation = {asset: weight for asset, weight in zip(self.qpt.assets, weights) 
                         if weight > 0.001}
            
            final_utility['optimal_weights'] = weights
            final_utility['asset_allocation'] = allocation
            final_utility['optimization_status'] = 'success'
            final_utility['utility_type'] = utility_type
            final_utility['risk_tolerance'] = risk_tolerance
            
            return final_utility
        else:
            return {
                'optimization_status': 'failed',
                'message': result.message,
                'utility_type': utility_type
            }
    
    def compare_utility_functions(self, 
                                weights: np.ndarray,
                                utility_types: List[str] = None) -> Dict:
        """
        Utility function comparison
        """
        if utility_types is None:
            utility_types = ['classical', 'quantum', 'quantum_entangled', 
                           'quantum_coherent', 'quantum_risk_aversion']
        
        comparison_results = {}
        
        for utility_type in utility_types:
            try:
                result = self.calculate_utility(weights, utility_type)
                comparison_results[utility_type] = result
            except Exception as e:
                self.logger.warning(f"Utility function {utility_type} hisoblashda xato: {e}")
                continue
        
        # Find best performing utility function
        if comparison_results:
            best_utility = max(comparison_results.items(), key=lambda x: x[1]['utility'])
            
            comparison_results['best_utility_function'] = {
                'type': best_utility[0],
                'value': best_utility[1]['utility']
            }
        
        return comparison_results
    
    def visualize_utility_landscape(self, 
                                   utility_types: List[str] = None,
                                   n_points: int = 100,
                                   save_path: Optional[str] = None) -> None:
        """
        Utility function visualization in 2D portfolio space
        """
        if utility_types is None:
            utility_types = ['classical', 'quantum', 'quantum_entangled']
        
        # Create 2D grid for visualization (first 2 assets)
        if len(self.qpt.assets) < 2:
            self.logger.warning("Kamida 2 asset kerak")
            return
        
        w1_range = np.linspace(0, 1, n_points)
        w2_range = np.linspace(0, 1, n_points)
        W1, W2 = np.meshgrid(w1_range, w2_range)
        
        # Normalize weights
        n_assets = len(self.qpt.assets)
        W3_to_n = np.maximum(0, 1 - W1 - W2)  # Remaining assets equally distributed
        
        fig, axes = plt.subplots(1, len(utility_types), figsize=(6*len(utility_types), 5))
        if len(utility_types) == 1:
            axes = [axes]
        
        fig.suptitle('Quantum Utility Landscapes', fontsize=16)
        
        for idx, utility_type in enumerate(utility_types):
            ax = axes[idx]
            U = np.zeros_like(W1)
            
            # Calculate utility for each point
            for i in range(n_points):
                for j in range(n_points):
                    if W1[i, j] + W2[i, j] <= 1:
                        # Create full weight vector
                        weights = np.zeros(n_assets)
                        weights[0] = W1[i, j]
                        weights[1] = W2[i, j]
                        weights[2:] = W3_to_n[i, j] / (n_assets - 2) if n_assets > 2 else 0
                        
                        # Calculate utility
                        try:
                            result = self.calculate_utility(weights, utility_type)
                            U[i, j] = result['utility']
                        except:
                            U[i, j] = np.nan
            
            # Plot contour
            contour = ax.contourf(W1, W2, U, levels=20, cmap='viridis')
            plt.colorbar(contour, ax=ax, label='Utility')
            
            ax.set_xlabel(f'{self.qpt.assets[0]} Weight')
            ax.set_ylabel(f'{self.qpt.assets[1]} Weight')
            ax.set_title(f'{utility_type.replace("_", " ").title()} Utility')
            
            # Add equal weight point
            equal_weights = np.ones(n_assets) / n_assets
            ax.plot(equal_weights[0], equal_weights[1], 'ro', markersize=8, label='Equal Weight')
            ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Utility landscape visualization saqlandi: {save_path}")
        else:
            plt.show()
    
    def _calculate_phase_alignment(self, weights: np.ndarray) -> float:
        """Quantum phase alignment calculation"""
        total_phase = 0.0
        weighted_phase = 0.0
        
        for i, weight in enumerate(weights):
            if weight > 0 and i < len(self.qpt.assets):
                asset = self.qpt.assets[i]
                quantum_state = self.qpt.quantum_states.get(asset, np.array([1, 0]))
                
                # Phase from quantum state
                phase = np.angle(quantum_state[0] * np.conj(quantum_state[1]))
                total_phase += phase
                weighted_phase += phase * weight
        
        # Alignment measure
        if total_phase != 0:
            alignment = weighted_phase / total_phase
        else:
            alignment = 0.0
        
        return np.abs(alignment)
    
    def _calculate_quantum_risk(self, weights: np.ndarray) -> float:
        """Quantum-specific risk measure"""
        # Portfolio concentration
        concentration = np.sum(weights ** 2)
        
        # Quantum entanglement risk
        entanglement_risk = 0.0
        for i in range(len(weights)):
            for j in range(i + 1, len(weights)):
                if i < len(self.qpt.assets) and j < len(self.qpt.assets):
                    asset1, asset2 = self.qpt.assets[i], self.qpt.assets[j]
                    entanglement = self.qpt._calculate_entanglement(asset1, asset2)
                    entanglement_risk += entanglement * weights[i] * weights[j]
        
        return concentration + entanglement_risk
    
    def _calculate_quantum_tail_risk(self, weights: np.ndarray) -> float:
        """Quantum tail risk calculation"""
        portfolio_returns = (self.qpt.returns_data * weights).sum(axis=1)
        
        # Tail probability (bottom 5%)
        tail_threshold = np.percentile(portfolio_returns, 5)
        tail_probability = len(portfolio_returns[portfolio_returns <= tail_threshold]) / len(portfolio_returns)
        
        # Quantum tail risk enhancement
        quantum_enhancement = self.qpt._calculate_quantum_coherence(weights)
        
        return tail_probability * (1 + quantum_enhancement)
    
    def _calculate_quantum_diversification_measure(self, weights: np.ndarray) -> float:
        """Quantum diversification measure"""
        # Shannon entropy
        positive_weights = weights[weights > 0]
        if len(positive_weights) == 0:
            return 0
        
        normalized_weights = positive_weights / np.sum(positive_weights)
        entropy = -np.sum(normalized_weights * np.log2(normalized_weights + 1e-8))
        
        # Quantum entanglement contribution
        entanglement_contribution = 0.0
        for i in range(len(weights)):
            for j in range(i + 1, len(weights)):
                if i < len(self.qpt.assets) and j < len(self.qpt.assets):
                    asset1, asset2 = self.qpt.assets[i], self.qpt.assets[j]
                    entanglement = self.qpt._calculate_entanglement(asset1, asset2)
                    entanglement_contribution += entanglement * weights[i] * weights[j]
        
        return entropy + entanglement_contribution
    
    def _calculate_quantum_information_content(self, weights: np.ndarray) -> float:
        """Quantum information content"""
        # Portfolio complexity
        complexity = -np.sum(weights * np.log2(weights + 1e-8))
        
        # Quantum information from states
        quantum_info = 0.0
        for i, weight in enumerate(weights):
            if weight > 0 and i < len(self.qpt.assets):
                quantum_state = self.qpt.quantum_states.get(self.qpt.assets[i], np.array([1, 0]))
                state_entropy = -np.sum(np.abs(quantum_state) ** 2 * np.log2(np.abs(quantum_state) ** 2 + 1e-8))
                quantum_info += weight * state_entropy
        
        return complexity + quantum_info
    
    def _calculate_mutual_information(self, weights: np.ndarray) -> float:
        """Mutual information between assets"""
        if self.qpt.returns_data is None:
            return 0
        
        total_mutual_info = 0.0
        valid_pairs = 0
        
        for i in range(len(self.qpt.assets)):
            for j in range(i + 1, len(self.qpt.assets)):
                asset1, asset2 = self.qpt.assets[i], self.qpt.assets[j]
                
                if asset1 in self.qpt.returns_data.columns and asset2 in self.qpt.returns_data.columns:
                    returns1 = self.qpt.returns_data[asset1]
                    returns2 = self.qpt.returns_data[asset2]
                    
                    # Simple mutual information approximation
                    correlation = returns1.corr(returns2)
                    mutual_info = -0.5 * np.log(1 - correlation ** 2) if abs(correlation) < 1 else 1.0
                    
                    # Weight by portfolio allocation
                    weight_factor = weights[i] * weights[j]
                    total_mutual_info += mutual_info * weight_factor
                    valid_pairs += 1
        
        return total_mutual_info / max(valid_pairs, 1)
    
    def _calculate_conditional_entropy(self, weights: np.ndarray) -> float:
        """Conditional entropy measure"""
        if self.qpt.returns_data is None:
            return 0
        
        # Portfolio conditional entropy based on weights
        weighted_entropy = 0.0
        
        for i, weight in enumerate(weights):
            if weight > 0 and i < len(self.qpt.assets):
                asset = self.qpt.assets[i]
                if asset in self.qpt.returns_data.columns:
                    returns = self.qpt.returns_data[asset]
                    asset_entropy = self._calculate_asset_entropy(returns)
                    weighted_entropy += weight * asset_entropy
        
        return weighted_entropy
    
    def _calculate_asset_entropy(self, returns: pd.Series) -> float:
        """Calculate entropy for a single asset"""
        # Simple binning approach
        hist, _ = np.histogram(returns, bins=20, density=True)
        hist = hist + 1e-8  # Avoid log(0)
        hist = hist / np.sum(hist)  # Normalize
        entropy = -np.sum(hist * np.log2(hist))
        return entropy