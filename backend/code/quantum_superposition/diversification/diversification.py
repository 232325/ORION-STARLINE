"""
Quantum Diversification Model
============================

Quantum entanglement va superposition asosida diversifikatsiya modellari.
"""

import numpy as np
import cmath
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from scipy.optimize import minimize
from scipy.linalg import norm, eigh, sqrtm
from scipy.stats import entropy
import matplotlib.pyplot as plt

try:
    from ..core.quantum_state import QuantumPortfolioState
    from ..core.entanglement import QuantumEntanglement, EntanglementConfig
except ImportError:
    # Fallback for standalone execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from core.quantum_state import QuantumPortfolioState
    from core.entanglement import QuantumEntanglement, EntanglementConfig


@dataclass
class QuantumDiversificationConfig:
    """Quantum diversifikatsiya konfiguratsiya parametrlari"""
    target_diversification: float = 0.7  # Maqsad diversifikatsiya darajasi
    entanglement_benefit_factor: float = 0.1  # Entanglement foyda koeffitsiyenti
    quantum_correlation_threshold: float = 0.3  # Quantum korrelatsiya threshold
    max_entanglement_correlation: float = 0.8  # Maksimal entanglement korrelatsiya
    diversification_preference: float = 1.0  # Diversifikatsiya afzalligi
    risk_parity_weight: float = 0.5  # Risk parity vazni


class QuantumDiversificationModel:
    """
    Quantum Diversification Model
    
    Quantum entanglement va superposition asosida portfolio diversifikatsiyasi.
    """
    
    def __init__(self, config: QuantumDiversificationConfig = None):
        self.config = config or QuantumDiversificationConfig()
        self.entanglement_manager = QuantumEntanglement()
        
        self.asset_universes = {}
        self.quantum_correlations = {}
        self.diversification_metrics = {}
        self.entanglement_benefits = {}
        
    def analyze_asset_universe(self, assets: List[str], 
                             returns_data: np.ndarray,
                             correlation_data: np.ndarray = None) -> Dict:
        """
        Asset universe quantum analizi
        
        Args:
            assets: Asset ro'yxati
            returns_data: Returns ma'lumotlari
            correlation_data: Korrelatsiya ma'lumotlari
        
        Returns:
            Asset universe analysis
        """
        n_assets = len(assets)
        
        # Quantum state representations
        asset_states = {}
        for i, asset in enumerate(assets):
            if i < len(returns_data):
                asset_returns = returns_data[i]
                # Quantum amplitude based on returns
                mean_return = np.mean(asset_returns)
                volatility = np.std(asset_returns)
                
                # Quantum amplitude calculation
                amplitude = max(0.01, mean_return) / (volatility + 0.001)
                amplitude = min(amplitude, 2.0)  # Cap amplitude
                
                asset_states[asset] = {
                    'amplitude': amplitude,
                    'mean_return': mean_return,
                    'volatility': volatility,
                    'quantum_weight': amplitude / np.sum([max(0.01, np.mean(returns_data[j])) 
                                                       for j in range(min(len(returns_data), len(assets)))])
                }
        
        # Quantum correlations
        quantum_correlations = self._calculate_quantum_correlations(asset_states)
        
        # Entanglement structure
        entanglement_structure = self._analyze_entanglement_structure(asset_states, quantum_correlations)
        
        # Diversification potential
        diversification_analysis = self._assess_diversification_potential(asset_states, quantum_correlations)
        
        self.asset_universes[tuple(assets)] = {
            'asset_states': asset_states,
            'quantum_correlations': quantum_correlations,
            'entanglement_structure': entanglement_structure,
            'diversification_analysis': diversification_analysis
        }
        
        return {
            'asset_states': asset_states,
            'quantum_correlations': quantum_correlations,
            'entanglement_structure': entanglement_structure,
            'diversification_analysis': diversification_analysis,
            'quantum_efficiency': diversification_analysis['quantum_efficiency']
        }
    
    def quantum_optimal_diversification(self, target_weights: Dict[str, float],
                                      asset_analysis: Dict = None) -> Dict:
        """
        Quantum optimal diversifikatsiya strategiyasi
        
        Args:
            target_weights: Maqsad weightlar
            asset_analysis: Asset analysis ma'lumotlari
        
        Returns:
            Optimal diversification strategy
        """
        if asset_analysis is None:
            raise ValueError("Asset analysis ma'lumotlari kerak")
        
        assets = list(target_weights.keys())
        current_weights = np.array([target_weights[asset] for asset in assets])
        
        # Quantum optimization objective
        def quantum_diversification_objective(weights):
            weights = weights / norm(weights)
            
            # Traditional diversification (HHI minimization)
            hhi = np.sum(weights**2)
            diversification_penalty = hhi
            
            # Quantum entanglement benefits
            entanglement_benefit = 0
            asset_states = asset_analysis['asset_states']
            
            for i, asset1 in enumerate(assets):
                for j, asset2 in enumerate(assets):
                    if i < j:
                        # Quantum correlation benefit
                        corr_key = f"{asset1}_{asset2}"
                        if corr_key in asset_analysis['quantum_correlations']:
                            quantum_corr = asset_analysis['quantum_correlations'][corr_key]
                            entanglement_benefit += weights[i] * weights[j] * quantum_corr
            
            # Risk parity component
            asset_volatilities = [asset_states[asset]['volatility'] for asset in assets]
            risk_parity_deviation = np.sum((weights * asset_volatilities - np.mean(weights * asset_volatilities))**2)
            
            # Combined objective
            total_objective = (diversification_penalty - 
                             self.config.entanglement_benefit_factor * entanglement_benefit +
                             self.config.risk_parity_weight * risk_parity_deviation)
            
            return total_objective
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
            {'type': 'ineq', 'fun': lambda x: np.min(x) - 0.01}  # Minimum weight
        ]
        
        # Bounds
        bounds = [(0.01, 0.4) for _ in range(len(assets))]  # Max 40% per asset
        
        # Optimization
        result = minimize(quantum_diversification_objective, current_weights,
                        method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            optimal_weights = result.x / norm(result.x)
        else:
            optimal_weights = current_weights
        
        # Calculate final metrics
        final_diversification = 1 - np.sum(optimal_weights**2)
        quantum_efficiency = self._calculate_quantum_efficiency(optimal_weights, asset_analysis)
        
        # Diversification improvements
        improvement_analysis = self._analyze_diversification_improvement(
            current_weights, optimal_weights, asset_analysis
        )
        
        return {
            'optimal_weights': {assets[i]: optimal_weights[i] for i in range(len(assets))},
            'final_diversification': final_diversification,
            'quantum_efficiency': quantum_efficiency,
            'improvement_analysis': improvement_analysis,
            'optimization_success': result.success,
            'entanglement_benefits': self._calculate_entanglement_portfolio_benefit(
                optimal_weights, assets, asset_analysis
            )
        }
    
    def entanglement_based_correlation_clustering(self, correlation_threshold: float = None) -> Dict:
        """
        Entanglement asosida korrelatsiya clustering
        
        Args:
            correlation_threshold: Clustering threshold
        
        Returns:
            Correlation clusters
        """
        if correlation_threshold is None:
            correlation_threshold = self.config.quantum_correlation_threshold
        
        # Get latest asset universe analysis
        if not self.asset_universes:
            return {'error': 'Asset universe analysis mavjud emas'}
        
        latest_analysis = list(self.asset_universes.values())[-1]
        asset_states = latest_analysis['asset_states']
        quantum_correlations = latest_analysis['quantum_correlations']
        
        assets = list(asset_states.keys())
        n_assets = len(assets)
        
        # Create correlation matrix
        correlation_matrix = np.eye(n_assets)
        
        for i, asset1 in enumerate(assets):
            for j, asset2 in enumerate(assets):
                if i != j:
                    corr_key = f"{asset1}_{asset2}"
                    if corr_key in quantum_correlations:
                        correlation_matrix[i, j] = quantum_correlations[corr_key]
                    else:
                        correlation_matrix[i, j] = np.random.uniform(-0.3, 0.3)  # Default
        
        # Clustering using quantum correlation
        clusters = self._quantum_correlation_clustering(correlation_matrix, assets, correlation_threshold)
        
        # Cluster analysis
        cluster_metrics = {}
        for cluster_id, cluster_assets in clusters.items():
            cluster_weights = np.ones(len(cluster_assets)) / len(cluster_assets)
            
            cluster_metrics[cluster_id] = {
                'assets': cluster_assets,
                'size': len(cluster_assets),
                'internal_correlation': np.mean([correlation_matrix[assets.index(a1)][assets.index(a2)] 
                                               for i, a1 in enumerate(cluster_assets) 
                                               for j, a2 in enumerate(cluster_assets) 
                                               if i != j]),
                'quantum_efficiency': 1 - np.sum(cluster_weights**4),
                'diversification_score': 1 - np.sum(cluster_weights**2),
                'entanglement_strength': self._calculate_cluster_entanglement(cluster_assets, quantum_correlations)
            }
        
        return {
            'correlation_matrix': correlation_matrix,
            'clusters': clusters,
            'cluster_metrics': cluster_metrics,
            'n_clusters': len(clusters),
            'correlation_threshold': correlation_threshold,
            'clustering_quality': np.mean([metrics['quantum_efficiency'] 
                                         for metrics in cluster_metrics.values()])
        }
    
    def quantum_risk_parity_optimization(self, target_risk_budget: Dict[str, float] = None,
                                       volatility_data: Dict[str, float] = None) -> Dict:
        """
        Quantum risk parity optimization
        
        Args:
            target_risk_budget: Maqsad risk budget
            volatility_data: Volatilite ma'lumotlari
        
        Returns:
            Risk parity optimization results
        """
        if not self.asset_universes:
            return {'error': 'Asset universe analysis mavjud emas'}
        
        latest_analysis = list(self.asset_universes.values())[-1]
        asset_states = latest_analysis['asset_states']
        assets = list(asset_states.keys())
        
        # Default risk parity if not specified
        if target_risk_budget is None:
            target_risk_budget = {asset: 1.0 / len(assets) for asset in assets}
        
        if volatility_data is None:
            volatility_data = {asset: asset_states[asset]['volatility'] for asset in assets}
        
        def quantum_risk_parity_objective(weights):
            weights = weights / norm(weights)
            
            # Risk contributions
            risk_contributions = weights * np.array([volatility_data[asset] for asset in assets])
            
            # Risk parity objective (minimize deviation from equal risk)
            target_risk_contribution = np.sum(risk_contributions) / len(assets)
            risk_parity_deviation = np.sum((risk_contributions - target_risk_contribution)**2)
            
            # Quantum diversification component
            quantum_diversification = 1 - np.sum(weights**2)
            
            # Entanglement benefit
            entanglement_benefit = 0
            quantum_correlations = latest_analysis['quantum_correlations']
            
            for i, asset1 in enumerate(assets):
                for j, asset2 in enumerate(assets):
                    if i < j:
                        corr_key = f"{asset1}_{asset2}"
                        if corr_key in quantum_correlations:
                            entanglement_benefit += weights[i] * weights[j] * quantum_correlations[corr_key]
            
            # Combined objective
            total_objective = (risk_parity_deviation - 
                             self.config.entanglement_benefit_factor * entanglement_benefit +
                             (1 - self.config.diversification_preference) * quantum_diversification)
            
            return total_objective
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}]
        bounds = [(0.01, 0.5) for _ in range(len(assets))]
        
        # Initial weights
        initial_weights = np.array([1.0 / len(assets)] * len(assets))
        
        # Optimization
        result = minimize(quantum_risk_parity_objective, initial_weights,
                        method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            optimal_weights = result.x / norm(result.x)
        else:
            optimal_weights = initial_weights
        
        # Calculate final risk parity
        risk_contributions = optimal_weights * np.array([volatility_data[asset] for asset in assets])
        risk_parity_metrics = {
            'risk_contributions': dict(zip(assets, risk_contributions)),
            'risk_parity_deviation': np.std(risk_contributions) / np.mean(risk_contributions),
            'effective_risk_budget': dict(zip(assets, optimal_weights)),
            'quantum_efficiency': 1 - np.sum(optimal_weights**4)
        }
        
        return {
            'optimal_weights': dict(zip(assets, optimal_weights)),
            'risk_parity_metrics': risk_parity_metrics,
            'optimization_success': result.success,
            'quantum_diversification': 1 - np.sum(optimal_weights**2),
            'entanglement_benefits': self._calculate_entanglement_portfolio_benefit(
                optimal_weights, assets, latest_analysis
            )
        }
    
    def dynamic_diversification_rebalancing(self, current_portfolio: QuantumPortfolioState,
                                          market_conditions: Dict,
                                          rebalance_threshold: float = 0.05) -> Dict:
        """
        Dinamik diversifikatsiya rebalancing
        
        Args:
            current_portfolio: Joriy portfolio
            market_conditions: Bozor shartlari
            rebalance_threshold: Rebalancing threshold
        
        Returns:
            Rebalancing strategy
        """
        current_weights = current_portfolio.get_portfolio_weights()
        assets = current_portfolio.assets
        
        # Market condition adjustments
        volatility = market_conditions.get('volatility', 0.15)
        correlation_environment = market_conditions.get('correlation_environment', 0.3)
        market_stress = market_conditions.get('market_stress', 0.0)
        
        # Dynamic target diversification
        if market_stress > 0.2:
            # High stress - increase diversification
            target_diversification = min(0.9, self.config.target_diversification * 1.2)
            diversification_preference = 1.5
        elif volatility > 0.25:
            # High volatility - moderate diversification increase
            target_diversification = min(0.85, self.config.target_diversification * 1.1)
            diversification_preference = 1.2
        else:
            target_diversification = self.config.target_diversification
            diversification_preference = 1.0
        
        # Rebalancing decision
        current_diversification = 1 - np.sum(current_weights**2)
        diversification_gap = target_diversification - current_diversification
        
        needs_rebalancing = abs(diversification_gap) > rebalance_threshold
        
        if needs_rebalancing:
            # Calculate new target weights
            target_weights = self._calculate_dynamic_target_weights(
                assets, current_weights, target_diversification, diversification_preference
            )
            
            # Calculate rebalancing impact
            weight_changes = target_weights - current_weights
            rebalancing_cost = np.sum(np.abs(weight_changes)) * 0.001  # 0.1% transaction cost
            
            # Expected benefit
            new_diversification = 1 - np.sum(target_weights**2)
            diversification_benefit = new_diversification - current_diversification
            quantum_benefit = self._calculate_quantum_rebalancing_benefit(
                current_weights, target_weights, assets
            )
            
            net_benefit = diversification_benefit + quantum_benefit - rebalancing_cost
            
            rebalancing_recommendation = {
                'action': 'REBALANCE',
                'target_weights': target_weights,
                'weight_changes': weight_changes,
                'diversification_improvement': diversification_benefit,
                'quantum_benefit': quantum_benefit,
                'rebalancing_cost': rebalancing_cost,
                'net_benefit': net_benefit,
                'recommended': net_benefit > rebalancing_cost * 2
            }
        else:
            rebalancing_recommendation = {
                'action': 'HOLD',
                'reason': f'Diversification gap ({diversification_gap:.3f}) below threshold',
                'current_diversification': current_diversification,
                'target_diversification': target_diversification
            }
        
        return {
            'rebalancing_decision': rebalancing_recommendation,
            'current_diversification': current_diversification,
            'target_diversification': target_diversification,
            'market_adjustments': {
                'volatility_adjustment': volatility,
                'correlation_environment': correlation_environment,
                'stress_adjustment': market_stress
            },
            'diversification_gap': diversification_gap
        }
    
    def _calculate_quantum_correlations(self, asset_states: Dict) -> Dict:
        """Quantum korrelatsiyalar hisoblash"""
        assets = list(asset_states.keys())
        quantum_correlations = {}
        
        for i, asset1 in enumerate(assets):
            for j, asset2 in enumerate(assets):
                if i < j:
                    # Quantum correlation based on returns and volatilities
                    returns1 = asset_states[asset1]['mean_return']
                    returns2 = asset_states[asset2]['mean_return']
                    vol1 = asset_states[asset1]['volatility']
                    vol2 = asset_states[asset2]['volatility']
                    
                    # Enhanced correlation calculation
                    correlation = np.corrcoef([returns1, returns2])[0, 1] if i != j else 1.0
                    
                    # Quantum enhancement based on volatility similarity
                    vol_similarity = 1 - abs(vol1 - vol2) / (vol1 + vol2)
                    quantum_correlation = 0.7 * correlation + 0.3 * vol_similarity
                    
                    quantum_correlations[f"{asset1}_{asset2}"] = quantum_correlation
        
        return quantum_correlations
    
    def _analyze_entanglement_structure(self, asset_states: Dict, 
                                      quantum_correlations: Dict) -> Dict:
        """Entanglement structure analizi"""
        assets = list(asset_states.keys())
        
        # Strong correlations (potential entanglement)
        strong_correlations = []
        weak_correlations = []
        
        for corr_key, corr_value in quantum_correlations.items():
            if corr_value > self.config.max_entanglement_correlation:
                strong_correlations.append((corr_key, corr_value))
            elif corr_value < self.config.quantum_correlation_threshold:
                weak_correlations.append((corr_key, corr_value))
        
        # Entanglement network analysis
        entanglement_network = self._build_entanglement_network(assets, quantum_correlations)
        
        return {
            'strong_correlations': strong_correlations,
            'weak_correlations': weak_correlations,
            'entanglement_network': entanglement_network,
            'network_density': len(strong_correlations) / (len(assets) * (len(assets) - 1) / 2),
            'diversification_potential': len(weak_correlations) / len(quantum_correlations)
        }
    
    def _assess_diversification_potential(self, asset_states: Dict, 
                                        quantum_correlations: Dict) -> Dict:
        """Diversifikatsiya potentsialini baholash"""
        assets = list(asset_states.keys())
        
        # Maximum possible diversification
        max_diversification = 1 - 1 / len(assets)
        
        # Current diversification level (equal weights)
        current_diversification = 1 - 1 / len(assets)
        
        # Quantum efficiency
        quantum_efficiency = current_diversification / max_diversification
        
        # Correlation-based assessment
        avg_correlation = np.mean(list(quantum_correlations.values()))
        diversification_score = 1 - avg_correlation
        
        # Risk-adjusted diversification
        asset_volatilities = [asset_states[asset]['volatility'] for asset in assets]
        weighted_variance = np.mean(asset_volatilities) ** 2
        risk_adjusted_diversification = current_diversification * (1 / (1 + weighted_variance))
        
        return {
            'max_diversification': max_diversification,
            'current_diversification': current_diversification,
            'quantum_efficiency': quantum_efficiency,
            'diversification_score': diversification_score,
            'risk_adjusted_diversification': risk_adjusted_diversification,
            'avg_correlation': avg_correlation,
            'improvement_potential': max_diversification - current_diversification
        }
    
    def _quantum_correlation_clustering(self, correlation_matrix: np.ndarray, 
                                      assets: List[str], 
                                      threshold: float) -> Dict:
        """Quantum korrelatsiya clustering"""
        n_assets = len(assets)
        clusters = {}
        cluster_id = 0
        assigned = set()
        
        for i in range(n_assets):
            if i in assigned:
                continue
            
            # Start new cluster
            cluster_assets = [assets[i]]
            cluster_indices = [i]
            assigned.add(i)
            
            # Add correlated assets
            for j in range(i + 1, n_assets):
                if j not in assigned and correlation_matrix[i, j] > threshold:
                    cluster_assets.append(assets[j])
                    cluster_indices.append(j)
                    assigned.add(j)
            
            # Only create cluster if it has more than 1 asset
            if len(cluster_assets) > 1:
                clusters[f"cluster_{cluster_id}"] = cluster_assets
                cluster_id += 1
        
        # Add remaining single assets as individual clusters
        for i in range(n_assets):
            if i not in assigned:
                clusters[f"cluster_{cluster_id}"] = [assets[i]]
                cluster_id += 1
        
        return clusters
    
    def _calculate_cluster_entanglement(self, cluster_assets: List[str], 
                                      quantum_correlations: Dict) -> float:
        """Cluster entanglement hisoblash"""
        if len(cluster_assets) < 2:
            return 0
        
        entanglement_strength = 0
        pair_count = 0
        
        for i, asset1 in enumerate(cluster_assets):
            for j, asset2 in enumerate(cluster_assets):
                if i < j:
                    corr_key = f"{asset1}_{asset2}"
                    if corr_key in quantum_correlations:
                        entanglement_strength += quantum_correlations[corr_key]
                        pair_count += 1
        
        return entanglement_strength / pair_count if pair_count > 0 else 0
    
    def _calculate_quantum_efficiency(self, weights: np.ndarray, 
                                    asset_analysis: Dict) -> float:
        """Quantum efficiency hisoblash"""
        hhi = np.sum(weights**2)
        diversification = 1 - hhi
        
        # Quantum enhancement factor
        quantum_correlations = asset_analysis['quantum_correlations']
        avg_correlation = np.mean(list(quantum_correlations.values()))
        quantum_enhancement = 1 - avg_correlation
        
        return diversification * (1 + quantum_enhancement)
    
    def _analyze_diversification_improvement(self, current_weights: np.ndarray,
                                           optimal_weights: np.ndarray,
                                           asset_analysis: Dict) -> Dict:
        """Diversifikatsiya improvement analizi"""
        current_div = 1 - np.sum(current_weights**2)
        optimal_div = 1 - np.sum(optimal_weights**2)
        
        improvement = optimal_div - current_div
        
        # Risk improvement
        current_risk = np.sqrt(np.sum(current_weights**2 * 0.15**2))
        optimal_risk = np.sqrt(np.sum(optimal_weights**2 * 0.15**2))
        risk_improvement = current_risk - optimal_risk
        
        # Quantum benefits
        quantum_efficiency_current = self._calculate_quantum_efficiency(current_weights, asset_analysis)
        quantum_efficiency_optimal = self._calculate_quantum_efficiency(optimal_weights, asset_analysis)
        quantum_improvement = quantum_efficiency_optimal - quantum_efficiency_current
        
        return {
            'diversification_improvement': improvement,
            'risk_improvement': risk_improvement,
            'quantum_efficiency_improvement': quantum_improvement,
            'relative_improvement': improvement / current_div if current_div > 0 else 0
        }
    
    def _calculate_entanglement_portfolio_benefit(self, weights: np.ndarray, 
                                                assets: List[str],
                                                asset_analysis: Dict) -> Dict:
        """Portfolio entanglement benefit hisoblash"""
        quantum_correlations = asset_analysis['quantum_correlations']
        
        total_entanglement_benefit = 0
        entanglement_pairs = 0
        
        for i, asset1 in enumerate(assets):
            for j, asset2 in enumerate(assets):
                if i < j:
                    corr_key = f"{asset1}_{asset2}"
                    if corr_key in quantum_correlations:
                        correlation = quantum_correlations[corr_key]
                        pair_benefit = weights[i] * weights[j] * correlation
                        total_entanglement_benefit += pair_benefit
                        entanglement_pairs += 1
        
        avg_entanglement_benefit = total_entanglement_benefit / entanglement_pairs if entanglement_pairs > 0 else 0
        
        return {
            'total_entanglement_benefit': total_entanglement_benefit,
            'average_pair_benefit': avg_entanglement_benefit,
            'entanglement_pairs': entanglement_pairs,
            'entanglement_efficiency': total_entanglement_benefit / np.sum(weights**2)
        }
    
    def _build_entanglement_network(self, assets: List[str], 
                                  quantum_correlations: Dict) -> Dict:
        """Entanglement network qurish"""
        network = {
            'nodes': assets,
            'edges': [],
            'clusters': []
        }
        
        # Strong correlations as edges
        for corr_key, corr_value in quantum_correlations.items():
            if corr_value > self.config.max_entanglement_correlation * 0.7:
                asset1, asset2 = corr_key.split('_')
                network['edges'].append({
                    'source': asset1,
                    'target': asset2,
                    'strength': corr_value
                })
        
        return network
    
    def _calculate_dynamic_target_weights(self, assets: List[str], 
                                        current_weights: np.ndarray,
                                        target_diversification: float,
                                        diversification_preference: float) -> np.ndarray:
        """Dinamik target weights hisoblash"""
        n_assets = len(assets)
        
        # Start with inverse volatility weights
        volatility_weights = np.ones(n_assets)
        
        # Adjust for diversification target
        target_hhi = 1 - target_diversification
        diversification_adjustment = target_hhi / (1/n_assets)
        
        # Combine preferences
        adjusted_weights = volatility_weights * diversification_adjustment * diversification_preference
        
        # Normalize
        adjusted_weights = adjusted_weights / np.sum(adjusted_weights)
        
        return adjusted_weights
    
    def _calculate_quantum_rebalancing_benefit(self, current_weights: np.ndarray,
                                             target_weights: np.ndarray,
                                             assets: List[str]) -> float:
        """Quantum rebalancing benefit hisoblash"""
        # Quantum coherence benefit from rebalancing
        current_coherence = 1 - np.sum(current_weights**4)
        target_coherence = 1 - np.sum(target_weights**4)
        
        coherence_benefit = target_coherence - current_coherence
        
        # Entanglement improvement
        entanglement_improvement = np.sum(target_weights**2) - np.sum(current_weights**2)
        
        return 0.02 * coherence_benefit + 0.01 * entanglement_improvement