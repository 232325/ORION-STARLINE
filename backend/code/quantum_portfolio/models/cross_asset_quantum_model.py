"""
Cross-Asset Quantum Model
=========================

Multi-asset klasslar (Stocks, Forex, Metals) uchun cross-asset quantum model.
Bu modul turli asset klasslari o'rtasida quantum portfolio optimizatsiyasini amalga oshiradi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
from scipy.optimize import minimize
import matplotlib.pyplot as plt

class CrossAssetQuantumModel:
    """
    Cross-Asset Quantum Model - Turli asset klasslari uchun unified quantum model
    """
    
    def __init__(self,
                 stocks_model,
                 forex_model,
                 metals_model,
                 quantum_coherence_time: float = 100.0,
                 correlation_structure: str = 'quantum_enhanced'):
        """
        Initialize cross-asset quantum model
        
        Args:
            stocks_model: StocksQuantumModel instance
            forex_model: ForexQuantumModel instance  
            metals_model: MetalsQuantumModel instance
            quantum_coherence_time: Quantum coherence time
            correlation_structure: Correlation structure type
        """
        self.stocks_model = stocks_model
        self.forex_model = forex_model
        self.metals_model = metals_model
        
        self.quantum_coherence_time = quantum_coherence_time
        self.correlation_structure = correlation_structure
        
        # Combined asset universe
        self.combined_assets = {}
        self.asset_class_weights = {}
        
        # Cross-asset quantum entanglement
        self.inter_class_entanglement = {}
        self.intra_class_entanglement = {}
        
        # Portfolio allocation constraints
        self.allocation_constraints = {
            'stocks_max': 0.6,
            'forex_max': 0.3,
            'metals_max': 0.4,
            'min_diversification': 3,  # Minimum number of asset classes
            'max_single_asset': 0.2    # Maximum single asset weight
        }
        
        self.logger = logging.getLogger(__name__)
        self._initialize_cross_asset_structure()
    
    def _initialize_cross_asset_structure(self):
        """Cross-asset structure initialization"""
        # Combine all assets
        if hasattr(self.stocks_model, 'stocks'):
            for stock in self.stocks_model.stocks:
                self.combined_assets[stock] = 'stocks'
        
        if hasattr(self.forex_model, 'currency_pairs'):
            for pair in self.forex_model.currency_pairs:
                self.combined_assets[pair] = 'forex'
        
        if hasattr(self.metals_model, 'metals'):
            for metal in self.metals_model.metals:
                self.combined_assets[metal] = 'metals'
        
        # Initialize inter-class entanglement
        self._calculate_inter_class_entanglement()
        
        # Initialize intra-class entanglement
        self._calculate_intra_class_entanglement()
        
        self.logger.info(f"Cross-asset model initialized: {len(self.combined_assets)} total assets")
    
    def _calculate_inter_class_entanglement(self):
        """Inter-class entanglement calculation"""
        # Stocks-Forex entanglement
        stocks_forex_entanglement = 0.3  # Moderate correlation
        
        # Stocks-Metals entanglement  
        stocks_metals_entanglement = 0.2  # Lower correlation
        
        # Forex-Metals entanglement
        forex_metals_entanglement = 0.25  # Moderate correlation
        
        self.inter_class_entanglement = {
            'stocks_forex': stocks_forex_entanglement,
            'stocks_metals': stocks_metals_entanglement,
            'forex_metals': forex_metals_entanglement
        }
    
    def _calculate_intra_class_entanglement(self):
        """Intra-class entanglement calculation"""
        # Calculate within-class entanglements
        self.intra_class_entanglement = {
            'stocks': self._calculate_stocks_entanglement(),
            'forex': self._calculate_forex_entanglement(),
            'metals': self._calculate_metals_entanglement()
        }
    
    def _calculate_stocks_entanglement(self) -> Dict:
        """Stocks intra-class entanglement"""
        if not hasattr(self.stocks_model, 'quantum_states'):
            return {}
        
        entanglement = {}
        stocks = list(self.stocks_model.quantum_states.keys())
        
        for i, stock1 in enumerate(stocks):
            for j, stock2 in enumerate(stocks):
                if i < j:
                    state1 = self.stocks_model.quantum_states[stock1]
                    state2 = self.stocks_model.quantum_states[stock2]
                    
                    # Quantum entanglement measure
                    entanglement_strength = np.abs(np.vdot(state1, state2)) ** 2
                    entanglement[f'{stock1}_{stock2}'] = entanglement_strength
        
        return entanglement
    
    def _calculate_forex_entanglement(self) -> Dict:
        """Forex intra-class entanglement"""
        if not hasattr(self.forex_model, 'currency_states'):
            return {}
        
        entanglement = {}
        pairs = list(self.forex_model.currency_states.keys())
        
        for i, pair1 in enumerate(pairs):
            for j, pair2 in enumerate(pairs):
                if i < j:
                    state1 = self.forex_model.currency_states[pair1]
                    state2 = self.forex_model.currency_states[pair2]
                    
                    # Currency entanglement based on common currencies
                    common_currencies = {pair1[:3], pair1[3:]} & {pair2[:3], pair2[3:]}
                    if common_currencies:
                        entanglement_strength = 0.8 if len(common_currencies) == 1 else 0.4
                    else:
                        entanglement_strength = 0.1
                    
                    entanglement[f'{pair1}_{pair2}'] = entanglement_strength
        
        return entanglement
    
    def _calculate_metals_entanglement(self) -> Dict:
        """Metals intra-class entanglement"""
        if not hasattr(self.metals_model, 'metal_quantum_states'):
            return {}
        
        entanglement = {}
        metals = list(self.metals_model.metal_quantum_states.keys())
        
        for i, metal1 in enumerate(metals):
            for j, metal2 in enumerate(metals):
                if i < j:
                    state1 = self.metals_model.metal_quantum_states[metal1]
                    state2 = self.metals_model.metal_quantum_states[metal2]
                    
                    # Quantum entanglement based on safe haven similarity
                    chars1 = self.metals_model.metal_characteristics[metal1]
                    chars2 = self.metals_model.metal_characteristics[metal2]
                    
                    safe_haven_similarity = 1 - abs(chars1['safe_haven'] - chars2['safe_haven'])
                    entanglement_strength = safe_haven_similarity * 0.7
                    
                    entanglement[f'{metal1}_{metal2}'] = entanglement_strength
        
        return entanglement
    
    def load_combined_data(self, 
                          stocks_data: Optional[pd.DataFrame] = None,
                          forex_data: Optional[pd.DataFrame] = None,
                          metals_data: Optional[pd.DataFrame] = None,
                          correlation_data: Optional[pd.DataFrame] = None):
        """
        Combined data loading
        
        Args:
            stocks_data: Stock returns data
            forex_data: Forex returns data  
            metals_data: Metals returns data
            correlation_data: Cross-asset correlation data
        """
        # Load data for each asset class
        if stocks_data is not None:
            self.stocks_model.load_data(stocks_data)
        
        if forex_data is not None:
            self.forex_model.load_data(forex_data)
        
        if metals_data is not None:
            self.metals_model.load_data(metals_data)
        
        # Store combined returns
        self.combined_returns = self._combine_returns_data()
        
        # Calculate quantum correlation matrix
        self.quantum_correlation_matrix = self._calculate_cross_asset_correlation()
        
        self.logger.info("Combined data loaded successfully")
    
    def _combine_returns_data(self) -> pd.DataFrame:
        """Combine returns data from all asset classes"""
        returns_list = []
        
        # Add stocks returns
        if hasattr(self.stocks_model, 'returns_data') and self.stocks_model.returns_data is not None:
            stocks_returns = self.stocks_model.returns_data.copy()
            stocks_returns.columns = [f"{col}_STOCK" for col in stocks_returns.columns]
            returns_list.append(stocks_returns)
        
        # Add forex returns
        if hasattr(self.forex_model, 'returns_data') and self.forex_model.returns_data is not None:
            forex_returns = self.forex_model.returns_data.copy()
            forex_returns.columns = [f"{col}_FOREX" for col in forex_returns.columns]
            returns_list.append(forex_returns)
        
        # Add metals returns
        if hasattr(self.metals_model, 'returns_data') and self.metals_model.returns_data is not None:
            metals_returns = self.metals_model.returns_data.copy()
            metals_returns.columns = [f"{col}_METAL" for col in metals_returns.columns]
            returns_list.append(metals_returns)
        
        if not returns_list:
            raise ValueError("Hech qanday returns ma'lumotlari topilmadi")
        
        # Combine all returns
        combined_returns = pd.concat(returns_list, axis=1)
        
        # Align dates and remove NaN values
        combined_returns = combined_returns.dropna()
        
        return combined_returns
    
    def _calculate_cross_asset_correlation(self) -> np.ndarray:
        """Calculate cross-asset correlation matrix with quantum enhancements"""
        # Classical correlation
        classical_corr = self.combined_returns.corr().values
        
        # Apply quantum enhancements based on asset classes
        n_assets = len(self.combined_returns.columns)
        quantum_corr = classical_corr.copy()
        
        # Get asset class for each column
        asset_classes = []
        for col in self.combined_returns.columns:
            if col.endswith('_STOCK'):
                asset_classes.append('stocks')
            elif col.endswith('_FOREX'):
                asset_classes.append('forex')
            elif col.endswith('_METAL'):
                asset_classes.append('metals')
            else:
                asset_classes.append('unknown')
        
        # Apply quantum corrections
        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                class_i = asset_classes[i]
                class_j = asset_classes[j]
                
                if class_i != class_j:
                    # Inter-class correlation enhancement
                    entanglement_key = f"{min(class_i, class_j)}_{max(class_i, class_j)}"
                    if entanglement_key in self.inter_class_entanglement:
                        entanglement = self.inter_class_entanglement[entanglement_key]
                        quantum_corr[i, j] = classical_corr[i, j] * (1 + entanglement * 0.1)
                        quantum_corr[j, i] = classical_corr[i, j] * (1 + entanglement * 0.1)
                else:
                    # Intra-class quantum enhancement
                    if class_i in self.intra_class_entanglement:
                        # Apply quantum enhancement based on intra-class entanglement
                        quantum_corr[i, j] *= 1.05
                        quantum_corr[j, i] *= 1.05
        
        return quantum_corr
    
    def quantum_optimization_objective(self, 
                                     weights: np.ndarray,
                                     target_return: Optional[float] = None,
                                     risk_aversion: float = 1.0,
                                     quantum_enhancement: float = 0.1) -> float:
        """
        Quantum optimization objective function
        
        Args:
            weights: Portfolio weights
            target_return: Target portfolio return
            risk_aversion: Risk aversion parameter
            quantum_enhancement: Quantum enhancement strength
            
        Returns:
            Negative utility (for minimization)
        """
        # Expected returns
        expected_returns = self._get_expected_returns()
        
        # Portfolio return
        portfolio_return = np.sum(weights * expected_returns)
        
        # Portfolio variance
        portfolio_variance = np.dot(weights, np.dot(self.quantum_correlation_matrix, weights))
        
        # Base utility
        utility = portfolio_return - 0.5 * risk_aversion * portfolio_variance
        
        # Quantum enhancements
        quantum_diversification = self._calculate_quantum_diversification(weights)
        quantum_coherence = self._calculate_portfolio_coherence(weights)
        quantum_entanglement = self._calculate_portfolio_entanglement(weights)
        
        # Cross-asset quantum effects
        cross_asset_effects = self._calculate_cross_asset_effects(weights)
        
        # Total quantum enhancement
        total_quantum_enhancement = (quantum_diversification * 0.3 + 
                                   quantum_coherence * 0.3 + 
                                   quantum_entanglement * 0.2 + 
                                   cross_asset_effects * 0.2) * quantum_enhancement
        
        # Add penalty for target return if specified
        return_penalty = 0
        if target_return is not None and portfolio_return < target_return:
            return_penalty = (target_return - portfolio_return) ** 2
        
        # Final utility
        final_utility = utility + total_quantum_enhancement - return_penalty
        
        return -final_utility  # Return negative for minimization
    
    def _get_expected_returns(self) -> np.ndarray:
        """Get expected returns for all assets"""
        expected_returns = []
        
        # Add stocks returns
        if hasattr(self.stocks_model, 'stock_returns') and self.stocks_model.stock_returns is not None:
            stocks_returns = self.stocks_model.stock_returns.mean().values
            expected_returns.extend(stocks_returns)
        
        # Add forex returns
        if hasattr(self.forex_model, 'returns_data') and self.forex_model.returns_data is not None:
            forex_returns = self.forex_model.returns_data.mean().values
            expected_returns.extend(forex_returns)
        
        # Add metals returns
        if hasattr(self.metals_model, 'returns_data') and self.metals_model.returns_data is not None:
            metals_returns = self.metals_model.returns_data.mean().values
            expected_returns.extend(metals_returns)
        
        return np.array(expected_returns)
    
    def _calculate_quantum_diversification(self, weights: np.ndarray) -> float:
        """Calculate quantum diversification measure"""
        # Shannon entropy
        positive_weights = weights[weights > 0]
        if len(positive_weights) == 0:
            return 0
        
        normalized_weights = positive_weights / np.sum(positive_weights)
        entropy = -np.sum(normalized_weights * np.log2(normalized_weights + 1e-8))
        
        # Maximum possible entropy for this number of assets
        max_entropy = np.log2(len(positive_weights))
        
        # Normalized entropy
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return normalized_entropy
    
    def _calculate_portfolio_coherence(self, weights: np.ndarray) -> float:
        """Calculate portfolio quantum coherence"""
        coherence = 0.0
        total_weight = np.sum(weights)
        
        if total_weight == 0:
            return 0
        
        # Stocks coherence
        if hasattr(self.stocks_model, 'quantum_states') and len(weights) > 0:
            stocks_count = len(self.stocks_model.quantum_states)
            for i, stock in enumerate(self.stocks_model.quantum_states.keys()):
                if i < len(weights):
                    quantum_state = self.stocks_model.quantum_states[stock]
                    off_diagonal = np.abs(quantum_state[0] * np.conj(quantum_state[1]))
                    coherence += (weights[i] / total_weight) * off_diagonal
        
        # Forex coherence
        if hasattr(self.forex_model, 'currency_states'):
            start_idx = len(self.stocks_model.quantum_states) if hasattr(self.stocks_model, 'quantum_states') else 0
            for i, pair in enumerate(self.forex_model.currency_states.keys()):
                idx = start_idx + i
                if idx < len(weights):
                    quantum_state = self.forex_model.currency_states[pair]
                    off_diagonal = np.abs(quantum_state[0] * np.conj(quantum_state[1]))
                    coherence += (weights[idx] / total_weight) * off_diagonal
        
        # Metals coherence
        if hasattr(self.metals_model, 'metal_quantum_states'):
            start_idx = len(self.stocks_model.quantum_states) if hasattr(self.stocks_model, 'quantum_states') else 0
            start_idx += len(self.forex_model.currency_states) if hasattr(self.forex_model, 'currency_states') else 0
            
            for i, metal in enumerate(self.metals_model.metal_quantum_states.keys()):
                idx = start_idx + i
                if idx < len(weights):
                    quantum_state = self.metals_model.metal_quantum_states[metal]
                    off_diagonal = np.abs(quantum_state[0] * np.conj(quantum_state[1]))
                    coherence += (weights[idx] / total_weight) * off_diagonal
        
        return coherence
    
    def _calculate_portfolio_entanglement(self, weights: np.ndarray) -> float:
        """Calculate portfolio quantum entanglement"""
        total_entanglement = 0.0
        total_weight = np.sum(weights)
        
        if total_weight == 0:
            return 0
        
        # Calculate pairwise entanglement
        n_assets = len(weights)
        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                if weights[i] > 0 and weights[j] > 0:
                    weight_product = (weights[i] * weights[j]) / (total_weight ** 2)
                    
                    # Get asset names based on index
                    asset_i = self._get_asset_by_index(i)
                    asset_j = self._get_asset_by_index(j)
                    
                    if asset_i and asset_j:
                        entanglement = self._get_pair_entanglement(asset_i, asset_j)
                        total_entanglement += weight_product * entanglement
        
        return total_entanglement
    
    def _get_asset_by_index(self, index: int) -> Optional[str]:
        """Get asset name by index"""
        # Stocks
        if hasattr(self.stocks_model, 'stocks'):
            stocks_count = len(self.stocks_model.stocks)
            if index < stocks_count:
                return f"{self.stocks_model.stocks[index]}_STOCK"
            index -= stocks_count
        
        # Forex
        if hasattr(self.forex_model, 'currency_pairs'):
            forex_count = len(self.forex_model.currency_pairs)
            if index < forex_count:
                return f"{self.forex_model.currency_pairs[index]}_FOREX"
            index -= forex_count
        
        # Metals
        if hasattr(self.metals_model, 'metals'):
            metals_count = len(self.metals_model.metals)
            if index < metals_count:
                return f"{self.metals_model.metals[index]}_METAL"
        
        return None
    
    def _get_pair_entanglement(self, asset1: str, asset2: str) -> float:
        """Get entanglement between two assets"""
        # Extract base asset names and classes
        class1 = asset1.split('_')[1] if '_' in asset1 else 'unknown'
        class2 = asset2.split('_')[1] if '_' in asset2 else 'unknown'
        base1 = asset1.split('_')[0]
        base2 = asset2.split('_')[0]
        
        if class1 == class2:
            # Intra-class entanglement
            if class1 in self.intra_class_entanglement:
                pair_key = f"{base1}_{base2}" if base1 < base2 else f"{base2}_{base1}"
                return self.intra_class_entanglement[class1].get(pair_key, 0.1)
        else:
            # Inter-class entanglement
            entanglement_key = f"{min(class1, class2)}_{max(class1, class2)}"
            return self.inter_class_entanglement.get(entanglement_key, 0.2)
        
        return 0.1  # Default entanglement
    
    def _calculate_cross_asset_effects(self, weights: np.ndarray) -> float:
        """Calculate cross-asset quantum effects"""
        # Asset class weights
        stocks_weight = 0
        forex_weight = 0
        metals_weight = 0
        
        index = 0
        
        # Stocks weight
        if hasattr(self.stocks_model, 'stocks'):
            stocks_count = len(self.stocks_model.stocks)
            stocks_weight = np.sum(weights[index:index + stocks_count])
            index += stocks_count
        
        # Forex weight
        if hasattr(self.forex_model, 'currency_pairs'):
            forex_count = len(self.forex_model.currency_pairs)
            forex_weight = np.sum(weights[index:index + forex_count])
            index += forex_count
        
        # Metals weight
        if hasattr(self.metals_model, 'metals'):
            metals_count = len(self.metals_model.metals)
            metals_weight = np.sum(weights[index:index + metals_count])
        
        # Cross-asset diversification benefit
        class_weights = [stocks_weight, forex_weight, metals_weight]
        positive_weights = [w for w in class_weights if w > 0]
        
        if len(positive_weights) >= 2:
            # Benefits from holding multiple asset classes
            cross_asset_benefit = len(positive_weights) / 3.0  # Normalized by max classes
        else:
            cross_asset_benefit = 0
        
        return cross_asset_benefit
    
    def optimize_cross_asset_portfolio(self, 
                                     objective_type: str = 'quantum_enhanced',
                                     risk_tolerance: str = 'moderate',
                                     target_return: Optional[float] = None) -> Dict:
        """
        Cross-asset portfolio optimization
        
        Args:
            objective_type: Optimization objective type
            risk_tolerance: Risk tolerance level
            target_return: Target portfolio return
            
        Returns:
            Optimization results
        """
        n_assets = len(self.combined_returns.columns)
        
        # Risk aversion mapping
        risk_tolerances = {
            'conservative': 2.0,
            'moderate': 1.0,
            'aggressive': 0.5,
            'very_aggressive': 0.2
        }
        
        risk_aversion = risk_tolerances.get(risk_tolerance, 1.0)
        
        # Objective function
        def objective(weights):
            return self.quantum_optimization_objective(weights, target_return, risk_aversion)
        
        # Constraints
        constraints = []
        
        # Budget constraint
        constraints.append({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        
        # Return constraint
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda w: np.sum(w * self._get_expected_returns()) - target_return
            })
        
        # Asset class constraints
        index = 0
        
        # Stocks max
        if hasattr(self.stocks_model, 'stocks'):
            stocks_count = len(self.stocks_model.stocks)
            constraints.append({
                'type': 'ineq',
                'fun': lambda w, idx=index, cnt=stocks_count: self.allocation_constraints['stocks_max'] - np.sum(w[idx:idx+cnt])
            })
            index += stocks_count
        
        # Forex max
        if hasattr(self.forex_model, 'currency_pairs'):
            forex_count = len(self.forex_model.currency_pairs)
            constraints.append({
                'type': 'ineq', 
                'fun': lambda w, idx=index, cnt=forex_count: self.allocation_constraints['forex_max'] - np.sum(w[idx:idx+cnt])
            })
            index += forex_count
        
        # Metals max
        if hasattr(self.metals_model, 'metals'):
            metals_count = len(self.metals_model.metals)
            constraints.append({
                'type': 'ineq',
                'fun': lambda w, idx=index, cnt=metals_count: self.allocation_constraints['metals_max'] - np.sum(w[idx:idx+cnt])
            })
        
        # Bounds
        bounds = [(0, self.allocation_constraints['max_single_asset']) for _ in range(n_assets)]
        
        # Initial guess
        x0 = np.ones(n_assets) / n_assets
        
        # Optimization
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            weights = result.x
            allocation = self._create_allocation_dict(weights)
            
            # Calculate portfolio metrics
            portfolio_return = np.sum(weights * self._get_expected_returns())
            portfolio_variance = np.dot(weights, np.dot(self.quantum_correlation_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            # Quantum metrics
            quantum_diversification = self._calculate_quantum_diversification(weights)
            quantum_coherence = self._calculate_portfolio_coherence(weights)
            quantum_entanglement = self._calculate_portfolio_entanglement(weights)
            cross_asset_effects = self._calculate_cross_asset_effects(weights)
            
            return {
                'allocation': allocation,
                'weights': weights,
                'portfolio_return': portfolio_return,
                'portfolio_volatility': portfolio_volatility,
                'sharpe_ratio': portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0,
                'quantum_diversification': quantum_diversification,
                'quantum_coherence': quantum_coherence,
                'quantum_entanglement': quantum_entanglement,
                'cross_asset_effects': cross_asset_effects,
                'objective_type': objective_type,
                'risk_tolerance': risk_tolerance,
                'optimization_status': 'success'
            }
        else:
            return {
                'optimization_status': 'failed',
                'message': result.message,
                'objective_type': objective_type
            }
    
    def _create_allocation_dict(self, weights: np.ndarray) -> Dict:
        """Create allocation dictionary"""
        allocation = {}
        asset_names = list(self.combined_returns.columns)
        
        for i, weight in enumerate(weights):
            if weight > 0.001:  # Only include significant weights
                allocation[asset_names[i]] = weight
        
        return allocation
    
    def stress_test_cross_asset_portfolio(self, 
                                        weights: np.ndarray,
                                        stress_scenarios: List[Dict] = None) -> Dict:
        """
        Cross-asset portfolio stress testing
        
        Args:
            weights: Portfolio weights
            stress_scenarios: List of stress scenarios
            
        Returns:
            Stress test results
        """
        if stress_scenarios is None:
            stress_scenarios = self._get_default_stress_scenarios()
        
        stress_results = {}
        
        for scenario_name, scenario in stress_scenarios.items():
            # Apply scenario shocks
            stressed_returns = self._apply_stress_scenario(weights, scenario)
            
            # Calculate portfolio impact
            portfolio_return = np.mean(stressed_returns)
            portfolio_volatility = np.std(stressed_returns)
            
            # Calculate VaR
            var_95 = -np.percentile(stressed_returns, 5)
            var_99 = -np.percentile(stressed_returns, 1)
            
            # Asset class impacts
            class_impacts = self._calculate_class_impacts(weights, stressed_returns)
            
            stress_results[scenario_name] = {
                'portfolio_return': portfolio_return,
                'portfolio_volatility': portfolio_volatility,
                'var_95': var_95,
                'var_99': var_99,
                'class_impacts': class_impacts,
                'scenario_description': scenario
            }
        
        # Aggregate results
        summary = {
            'worst_case_var_95': max([r['var_95'] for r in stress_results.values()]),
            'worst_case_var_99': max([r['var_99'] for r in stress_results.values()]),
            'average_return_impact': np.mean([r['portfolio_return'] for r in stress_results.values()]),
            'scenarios_tested': len(stress_scenarios)
        }
        
        stress_results['summary'] = summary
        
        return stress_results
    
    def _get_default_stress_scenarios(self) -> Dict:
        """Default stress testing scenarios"""
        return {
            'market_crash': {
                'type': 'equity_shock',
                'stocks_shock': -0.3,
                'metals_shock': 0.1,  # Safe haven benefit
                'forex_shock': -0.1
            },
            'interest_rate_spike': {
                'type': 'rate_shock',
                'stocks_shock': -0.15,
                'metals_shock': -0.1,
                'forex_shock': 0.05
            },
            'currency_crisis': {
                'type': 'currency_shock',
                'forex_volatility_multiplier': 3.0,
                'stocks_shock': -0.1,
                'metals_shock': 0.05
            },
            'inflation_spike': {
                'type': 'inflation_shock',
                'metals_shock': 0.2,  # Inflation hedge
                'stocks_shock': -0.1,
                'forex_shock': -0.05
            }
        }
    
    def _apply_stress_scenario(self, weights: np.ndarray, scenario: Dict) -> np.ndarray:
        """Apply stress scenario to portfolio"""
        # Base portfolio returns
        base_returns = self._calculate_portfolio_returns(weights)
        
        scenario_type = scenario['type']
        
        if scenario_type == 'equity_shock':
            stressed_returns = base_returns.copy()
            # Apply shocks by asset class
            stocks_shock = scenario.get('stocks_shock', 0)
            metals_shock = scenario.get('metals_shock', 0)
            forex_shock = scenario.get('forex_shock', 0)
            
            # Apply shocks (simplified)
            stressed_returns += stocks_shock * 0.5 + metals_shock * 0.3 + forex_shock * 0.2
            
        elif scenario_type == 'rate_shock':
            stressed_returns = base_returns - 0.1 * abs(base_returns)
            
        elif scenario_type == 'currency_shock':
            volatility_multiplier = scenario.get('forex_volatility_multiplier', 2.0)
            stressed_returns = base_returns * volatility_multiplier
            
        elif scenario_type == 'inflation_shock':
            stressed_returns = base_returns + 0.05  # Inflation premium
            
        else:
            stressed_returns = base_returns
        
        return stressed_returns
    
    def _calculate_portfolio_returns(self, weights: np.ndarray) -> np.ndarray:
        """Calculate portfolio returns"""
        portfolio_returns = (self.combined_returns * weights).sum(axis=1)
        return portfolio_returns.values
    
    def _calculate_class_impacts(self, weights: np.ndarray, stressed_returns: np.ndarray) -> Dict:
        """Calculate asset class impacts from stress scenario"""
        class_impacts = {}
        
        # Calculate weights by class
        index = 0
        
        # Stocks
        if hasattr(self.stocks_model, 'stocks'):
            stocks_count = len(self.stocks_model.stocks)
            stocks_weight = np.sum(weights[index:index + stocks_count])
            stocks_return = np.sum(weights[index:index + stocks_count] * 
                                 self.combined_returns.iloc[:, index:index + stocks_count].mean().values)
            class_impacts['stocks'] = {
                'weight': stocks_weight,
                'base_return': stocks_return,
                'stress_impact': stocks_weight * np.mean(stressed_returns) * 0.8  # Approximate
            }
            index += stocks_count
        
        # Forex
        if hasattr(self.forex_model, 'currency_pairs'):
            forex_count = len(self.forex_model.currency_pairs)
            forex_weight = np.sum(weights[index:index + forex_count])
            forex_return = np.sum(weights[index:index + forex_count] * 
                                self.combined_returns.iloc[:, index:index + forex_count].mean().values)
            class_impacts['forex'] = {
                'weight': forex_weight,
                'base_return': forex_return,
                'stress_impact': forex_weight * np.mean(stressed_returns) * 0.6  # Approximate
            }
            index += forex_count
        
        # Metals
        if hasattr(self.metals_model, 'metals'):
            metals_weight = np.sum(weights[index:])
            metals_return = np.sum(weights[index:] * 
                                 self.combined_returns.iloc[:, index:].mean().values)
            class_impacts['metals'] = {
                'weight': metals_weight,
                'base_return': metals_return,
                'stress_impact': metals_weight * np.mean(stressed_returns) * 0.4  # Approximate
            }
        
        return class_impacts
    
    def visualize_cross_asset_analysis(self, 
                                     weights: Optional[np.ndarray] = None,
                                     save_path: Optional[str] = None) -> None:
        """Cross-asset analysis visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Cross-Asset Quantum Analysis Dashboard', fontsize=16)
        
        # 1. Quantum correlation heatmap
        if hasattr(self, 'quantum_correlation_matrix'):
            im = axes[0, 0].imshow(self.quantum_correlation_matrix, cmap='RdBu_r', 
                                 aspect='auto', vmin=-1, vmax=1)
            axes[0, 0].set_title('Cross-Asset Quantum Correlation Matrix')
            axes[0, 0].set_xticks(range(len(self.combined_returns.columns)))
            axes[0, 0].set_yticks(range(len(self.combined_returns.columns)))
            axes[0, 0].set_xticklabels(self.combined_returns.columns, rotation=90)
            axes[0, 0].set_yticklabels(self.combined_returns.columns)
            plt.colorbar(im, ax=axes[0, 0])
        
        # 2. Asset class weights (if optimization done)
        if weights is not None:
            class_weights = self._get_class_weights(weights)
            
            axes[0, 1].pie(class_weights.values(), labels=class_weights.keys(), autopct='%1.1f%%')
            axes[0, 1].set_title('Asset Class Allocation')
        
        # 3. Inter-class entanglement
        entanglement_data = list(self.inter_class_entanglement.values())
        entanglement_labels = list(self.inter_class_entanglement.keys())
        
        axes[1, 0].bar(entanglement_labels, entanglement_data, alpha=0.7)
        axes[1, 0].set_title('Inter-Class Quantum Entanglement')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].set_ylabel('Entanglement Strength')
        
        # 4. Combined returns distribution
        if hasattr(self, 'combined_returns'):
            combined_returns = self.combined_returns.mean(axis=1)
            axes[1, 1].hist(combined_returns, bins=50, alpha=0.7, color='skyblue')
            axes[1, 1].set_title('Combined Portfolio Returns Distribution')
            axes[1, 1].set_xlabel('Returns')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].axvline(combined_returns.mean(), color='red', linestyle='--', 
                             label=f'Mean: {combined_returns.mean():.4f}')
            axes[1, 1].legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Cross-asset analysis visualization saqlandi: {save_path}")
        else:
            plt.show()
    
    def _get_class_weights(self, weights: np.ndarray) -> Dict:
        """Get weights by asset class"""
        class_weights = {}
        index = 0
        
        # Stocks
        if hasattr(self.stocks_model, 'stocks'):
            stocks_count = len(self.stocks_model.stocks)
            class_weights['stocks'] = np.sum(weights[index:index + stocks_count])
            index += stocks_count
        
        # Forex
        if hasattr(self.forex_model, 'currency_pairs'):
            forex_count = len(self.forex_model.currency_pairs)
            class_weights['forex'] = np.sum(weights[index:index + forex_count])
            index += forex_count
        
        # Metals
        if hasattr(self.metals_model, 'metals'):
            class_weights['metals'] = np.sum(weights[index:])
        
        return class_weights
    
    def save_model_state(self, filepath: str):
        """Model state saqlash"""
        model_state = {
            'combined_assets': self.combined_assets,
            'allocation_constraints': self.allocation_constraints,
            'quantum_coherence_time': self.quantum_coherence_time,
            'correlation_structure': self.correlation_structure,
            'inter_class_entanglement': self.inter_class_entanglement,
            'intra_class_entanglement': self.intra_class_entanglement,
            'model_states': {
                'stocks': self.stocks_model.__class__.__name__,
                'forex': self.forex_model.__class__.__name__,
                'metals': self.metals_model.__class__.__name__
            }
        }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(model_state, f, indent=2, default=str)
        
        self.logger.info(f"Cross-asset model state saqlandi: {filepath}")
    
    def load_model_state(self, filepath: str):
        """Model state yuklash"""
        import json
        with open(filepath, 'r') as f:
            model_state = json.load(f)
        
        self.combined_assets = model_state['combined_assets']
        self.allocation_constraints = model_state['allocation_constraints']
        self.quantum_coherence_time = model_state['quantum_coherence_time']
        self.correlation_structure = model_state['correlation_structure']
        self.inter_class_entanglement = model_state['inter_class_entanglement']
        self.intra_class_entanglement = model_state['intra_class_entanglement']
        
        self.logger.info(f"Cross-asset model state yuklandi: {filepath}")