"""
Quantum Portfolio Theory Implementation
======================================

Modern quantum portfolio theory implementation using quantum computing principles.
Bu modul quantum computing yordamida portfel nazariyasini amalga oshiradi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
from scipy.optimize import minimize
import json

class QuantumPortfolioTheory:
    """
    Quantum Portfolio Theory - Modern portfolio theory asosidagi quantum implementatsiya
    """
    
    def __init__(self, 
                 assets: List[str],
                 risk_free_rate: float = 0.02,
                 quantum_coherence_time: float = 100.0):
        """
        Quantum Portfolio Theory initialize qilish
        
        Args:
            assets: Asset nomlari ro'yxati
            risk_free_rate: Risk-free daromad stavkasi
            quantum_coherence_time: Quantum coherence vaqti (microseconds)
        """
        self.assets = assets
        self.n_assets = len(assets)
        self.risk_free_rate = risk_free_rate
        self.quantum_coherence_time = quantum_coherence_time
        
        # Quantum states va operators
        self.quantum_states = {}
        self.hamiltonian_operators = {}
        
        # Portfolio historical data
        self.price_data = None
        self.returns_data = None
        self.covariance_matrix = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self._setup_quantum_operators()
        
    def _setup_quantum_operators(self):
        """Quantum operators va states ni sozlash"""
        # Pauli operators for quantum portfolio representation
        self.pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
        self.pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        self.pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
        self.identity = np.eye(2, dtype=complex)
        
        # Initialize quantum states for each asset
        for i, asset in enumerate(self.assets):
            # Assetning risk va return qiymatlari asosida quantum state yaratish
            asset_state = self._create_asset_quantum_state(i)
            self.quantum_states[asset] = asset_state
            
    def _create_asset_quantum_state(self, asset_index: int) -> np.ndarray:
        """
        Har bir asset uchun quantum state yaratish
        Assetning risk va return xarakteristikalari asosida
        """
        # Asset index asosida quantum state amplitude
        alpha = 0.8 + 0.2 * np.random.random()  # |0⟩ amplitude
        beta = np.sqrt(1 - alpha**2)           # |1⟩ amplitude
        
        # Quantum state (superposition of risk-return states)
        quantum_state = np.array([alpha, beta], dtype=complex)
        
        # Phase encoding for portfolio representation
        phase = 2 * np.pi * asset_index / self.n_assets
        quantum_state *= np.exp(1j * phase)
        
        return quantum_state
    
    def load_data(self, price_data: pd.DataFrame):
        """
        Portfolio ma'lumotlarini yuklash
        
        Args:
            price_data: Asset narxlari DataFrame'i
        """
        self.price_data = price_data
        self.returns_data = price_data.pct_change().dropna()
        
        # Calculate quantum-enhanced covariance matrix
        self.covariance_matrix = self._calculate_quantum_covariance()
        
        self.logger.info(f"Portfolio data yuklandi: {len(self.assets)} assetlar")
    
    def _calculate_quantum_covariance(self) -> np.ndarray:
        """
        Quantum-enhanced covariance matrix hisoblash
        Classical covariance va quantum corrections qo'shish
        """
        # Classical covariance calculation
        classical_cov = self.returns_data.cov().values
        
        # Quantum corrections based on entanglement
        n_assets = len(self.assets)
        quantum_corrections = np.zeros((n_assets, n_assets))
        
        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                # Quantum entanglement factor
                entanglement_factor = self._calculate_entanglement(self.assets[i], self.assets[j])
                
                # Apply quantum correction
                quantum_corrections[i, j] = classical_cov[i, j] * (1 + entanglement_factor)
                quantum_corrections[j, i] = classical_cov[i, j] * (1 + entanglement_factor)
        
        # Combine classical and quantum components
        enhanced_cov = classical_cov + quantum_corrections
        
        return enhanced_cov
    
    def _calculate_entanglement(self, asset1: str, asset2: str) -> float:
        """
        Asset'lar orasidagi quantum entanglement darajasini hisoblash
        """
        # Simple entanglement calculation based on correlation and quantum coherence
        if asset1 in self.returns_data.columns and asset2 in self.returns_data.columns:
            correlation = self.returns_data[asset1].corr(self.returns_data[asset2])
            entanglement = correlation * np.exp(-self.quantum_coherence_time / 50.0)
            return entanglement
        return 0.0
    
    def quantum_mean_variance_optimization(self, 
                                         target_return: Optional[float] = None,
                                         risk_aversion: float = 1.0) -> Dict:
        """
        Quantum Mean-Variance Optimization
        
        Args:
            target_return: Maqsad daromad (None bo'lsa efficient frontier)
            risk_aversion: Risk aversion parameter
            
        Returns:
            Optimized portfolio weights
        """
        if self.covariance_matrix is None:
            raise ValueError("Portfolio ma'lumotlarini avval yuklang")
        
        n_assets = len(self.assets)
        
        # Expected returns (quantum-enhanced)
        expected_returns = self._quantum_expected_returns()
        
        # Objective function: Quantum utility maximization
        def quantum_objective(weights):
            # Classical mean-variance component
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_variance = np.dot(weights, np.dot(self.covariance_matrix, weights))
            
            # Quantum enhancement terms
            quantum_entropy = self._calculate_quantum_entropy(weights)
            quantum_coherence = self._calculate_quantum_coherence(weights)
            
            # Combined quantum utility function
            utility = (portfolio_return - 
                      0.5 * risk_aversion * portfolio_variance +
                      quantum_entropy * 0.1 +
                      quantum_coherence * 0.05)
            
            return -utility  # Minimize negative utility
        
        # Constraints
        constraints = []
        
        # Budget constraint (weights sum to 1)
        constraints.append({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        
        # Return constraint (if target return specified)
        if target_return is not None:
            constraints.append({
                'type': 'eq', 
                'fun': lambda w: np.sum(w * expected_returns) - target_return
            })
        
        # Bounds (no short selling for simplicity)
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # Initial guess (equal weights)
        x0 = np.ones(n_assets) / n_assets
        
        # Optimization
        result = minimize(
            quantum_objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            portfolio_weights = result.x
            portfolio_stats = self._calculate_portfolio_stats(portfolio_weights)
            
            return {
                'weights': portfolio_weights,
                'expected_return': portfolio_stats['return'],
                'volatility': portfolio_stats['volatility'],
                'sharpe_ratio': portfolio_stats['sharpe_ratio'],
                'quantum_utility': portfolio_stats['quantum_utility'],
                'optimization_status': 'success'
            }
        else:
            raise RuntimeError(f"Optimizatsiya muvaffaqiyatsiz: {result.message}")
    
    def _quantum_expected_returns(self) -> np.ndarray:
        """
        Quantum-enhanced expected returns hisoblash
        """
        # Classical expected returns
        classical_returns = self.returns_data.mean().values
        
        # Quantum corrections
        quantum_corrections = np.zeros(self.n_assets)
        
        for i, asset in enumerate(self.assets):
            # Quantum state-based return enhancement
            quantum_state = self.quantum_states[asset]
            enhancement = np.real(np.conj(quantum_state[0]) * quantum_state[1])
            quantum_corrections[i] = classical_returns[i] * (1 + enhancement * 0.1)
        
        return classical_returns + quantum_corrections
    
    def _calculate_quantum_entropy(self, weights: np.ndarray) -> float:
        """
        Portfolio entropy hisoblash (diversification measure)
        """
        # Normalize weights
        weights = weights[weights > 0]  # Only positive weights
        if len(weights) == 0:
            return 0
        
        weights = weights / np.sum(weights)
        
        # Shannon entropy
        entropy = -np.sum(weights * np.log2(weights + 1e-8))
        
        # Quantum enhancement
        quantum_entanglement = 0.0
        for i in range(len(weights)):
            for j in range(i + 1, len(weights)):
                # Asset entanglement contribution
                asset_i = self.assets[i]
                asset_j = self.assets[j]
                entanglement = self._calculate_entanglement(asset_i, asset_j)
                quantum_entanglement += entanglement * weights[i] * weights[j]
        
        return entropy + quantum_entanglement * 0.5
    
    def _calculate_quantum_coherence(self, weights: np.ndarray) -> float:
        """
        Portfolio quantum coherence hisoblash
        """
        # Quantum coherence based on weight distribution
        coherence = 0.0
        
        for i, weight in enumerate(weights):
            if weight > 0:
                asset = self.assets[i]
                quantum_state = self.quantum_states[asset]
                
                # Off-diagonal elements contribute to coherence
                coherence += weight * np.abs(quantum_state[0] * np.conj(quantum_state[1]))
        
        return coherence
    
    def _calculate_portfolio_stats(self, weights: np.ndarray) -> Dict:
        """
        Portfolio statistics hisoblash
        """
        expected_return = np.sum(weights * self._quantum_expected_returns())
        variance = np.dot(weights, np.dot(self.covariance_matrix, weights))
        volatility = np.sqrt(variance)
        
        # Sharpe ratio
        excess_return = expected_return - self.risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        # Quantum utility
        quantum_utility = self._calculate_quantum_entropy(weights) * 0.1 + \
                         self._calculate_quantum_coherence(weights) * 0.05
        
        return {
            'return': expected_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'quantum_utility': quantum_utility
        }
    
    def generate_quantum_efficient_frontier(self, 
                                           n_portfolios: int = 100,
                                           target_range: Optional[Tuple[float, float]] = None) -> Dict:
        """
        Quantum efficient frontier yaratish
        
        Args:
            n_portfolios: Yaratiladigan portfolio soni
            target_range: Daromad oralig'i (min, max)
            
        Returns:
            Efficient frontier data
        """
        if target_range is None:
            returns = self._quantum_expected_returns()
            target_range = (returns.min() - 0.01, returns.max() + 0.01)
        
        target_returns = np.linspace(target_range[0], target_range[1], n_portfolios)
        frontier_portfolios = []
        
        for target_ret in target_returns:
            try:
                portfolio = self.quantum_mean_variance_optimization(target_return=target_ret)
                frontier_portfolios.append(portfolio)
            except:
                # Skip failed optimizations
                continue
        
        # Extract frontier data
        frontier_returns = [p['expected_return'] for p in frontier_portfolios]
        frontier_risks = [p['volatility'] for p in frontier_portfolios]
        frontier_sharpe = [p['sharpe_ratio'] for p in frontier_portfolios]
        
        # Sort by risk
        sorted_indices = np.argsort(frontier_risks)
        sorted_returns = [frontier_returns[i] for i in sorted_indices]
        sorted_risks = [frontier_risks[i] for i in sorted_indices]
        sorted_sharpe = [frontier_sharpe[i] for i in sorted_indices]
        
        return {
            'returns': sorted_returns,
            'risks': sorted_risks,
            'sharpe_ratios': sorted_sharpe,
            'portfolios': [frontier_portfolios[i] for i in sorted_indices],
            'efficient_frontier': 'quantum_enhanced'
        }
    
    def quantum_risk_decomposition(self, weights: np.ndarray) -> Dict:
        """
        Portfolio risk decomposition (quantum-enhanced)
        """
        total_risk = np.dot(weights, np.dot(self.covariance_matrix, weights))
        
        # Individual asset contributions
        marginal_contributions = []
        for i, weight in enumerate(weights):
            # Calculate marginal risk contribution
            marginal_risk = weight * np.dot(self.covariance_matrix[i], weights)
            marginal_contributions.append(marginal_risk)
        
        # Diversification ratio (quantum-enhanced)
        weighted_volatility = np.sum(weights * np.sqrt(np.diag(self.covariance_matrix)))
        diversification_ratio = weighted_volatility / np.sqrt(total_risk)
        
        # Quantum diversification enhancement
        quantum_diversification = self._calculate_quantum_entropy(weights) / np.log(len(weights))
        
        return {
            'total_risk': total_risk,
            'marginal_contributions': marginal_contributions,
            'diversification_ratio': diversification_ratio,
            'quantum_diversification': quantum_diversification,
            'concentration_risk': 1 - np.max(weights) if len(weights) > 0 else 0
        }
    
    def save_quantum_state(self, filepath: str):
        """Quantum state va ma'lumotlarni saqlash"""
        state_data = {
            'assets': self.assets,
            'quantum_states': {
                asset: state.tolist() 
                for asset, state in self.quantum_states.items()
            },
            'covariance_matrix': self.covariance_matrix.tolist() if self.covariance_matrix is not None else None,
            'quantum_coherence_time': self.quantum_coherence_time
        }
        
        with open(filepath, 'w') as f:
            json.dump(state_data, f, indent=2)
        
        self.logger.info(f"Quantum state saqlandi: {filepath}")
    
    def load_quantum_state(self, filepath: str):
        """Quantum state va ma'lumotlarni yuklash"""
        with open(filepath, 'r') as f:
            state_data = json.load(f)
        
        self.assets = state_data['assets']
        self.n_assets = len(self.assets)
        self.quantum_coherence_time = state_data['quantum_coherence_time']
        
        # Restore quantum states
        self.quantum_states = {
            asset: np.array(state) 
            for asset, state in state_data['quantum_states'].items()
        }
        
        # Restore covariance matrix
        if state_data['covariance_matrix']:
            self.covariance_matrix = np.array(state_data['covariance_matrix'])
        
        self.logger.info(f"Quantum state yuklandi: {filepath}")