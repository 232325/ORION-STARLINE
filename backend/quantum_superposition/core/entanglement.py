"""
Quantum Entanglement Module
==========================

Quantum entanglement va korrelatsiya operatsiyalari.
"""

import numpy as np
import cmath
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from scipy.linalg import norm, sqrtm, logm
from scipy.optimize import minimize
import matplotlib.pyplot as plt

from .quantum_state import QuantumPortfolioState, QuantumState


@dataclass
class EntanglementConfig:
    """Entanglement konfiguratsiya parametrlari"""
    entanglement_threshold: float = 0.5  # Entanglement threshold
    correlation_decay_rate: float = 0.1  # Korrelatsiya decay rate
    entanglement_strength: float = 1.0  # Entanglement kuchi
    max_entangled_assets: int = 4  # Maksimal entangled assetlar soni


class QuantumEntanglement:
    """
    Quantum Entanglement Management
    
    Portfolio assetlari o'rtasida quantum entanglement va korrelatsiyani boshqarish.
    """
    
    def __init__(self, config: EntanglementConfig = None):
        self.config = config or EntanglementConfig()
        self.entangled_pairs = {}
        self.entanglement_matrix = None
        self.correlation_history = {}
        
    def create_bell_state(self, asset1: str, asset2: str) -> Dict:
        """
        Bell state yaratish (2-asset entanglement)
        
        Args:
            asset1: Birinchi asset
            asset2: Ikkinchi asset
        
        Returns:
            Bell state va entangled pair ma'lumotlari
        """
        basis_states = ['00', '01', '10', '11']
        amplitudes = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)  # |00⟩ + |11⟩
        
        bell_state = QuantumState(amplitudes, basis_states)
        
        entangled_pair = {
            'assets': (asset1, asset2),
            'bell_state': bell_state,
            'entanglement_type': 'bell_state',
            'correlation_strength': 1.0,
            'entanglement_entropy': self._calculate_entanglement_entropy(bell_state)
        }
        
        self.entangled_pairs[(asset1, asset2)] = entangled_pair
        
        return entangled_pair
    
    def create_ghz_state(self, assets: List[str]) -> Dict:
        """
        GHZ state yaratish (multi-asset entanglement)
        
        Args:
            assets: Entangled bo'lishi kerak assetlar
        
        Returns:
            GHZ state ma'lumotlari
        """
        n_assets = len(assets)
        if n_assets > self.config.max_entangled_assets:
            raise ValueError(f"Ko'p asset: maksimal {self.config.max_entangled_assets} ta")
        
        # GHZ state: |000...0⟩ + |111...1⟩
        n_basis_states = 2**n_assets
        amplitudes = np.zeros(n_basis_states, dtype=complex)
        amplitudes[0] = 1/np.sqrt(2)  # |00...0⟩
        amplitudes[-1] = 1/np.sqrt(2)  # |11...1⟩
        
        basis_states = [format(i, f'0{n_assets}b') for i in range(n_basis_states)]
        ghz_state = QuantumState(amplitudes, basis_states)
        
        ghz_entanglement = {
            'assets': tuple(assets),
            'ghz_state': ghz_state,
            'entanglement_type': 'ghz_state',
            'correlation_strength': 1.0,
            'entanglement_entropy': self._calculate_entanglement_entropy(ghz_state),
            'multipartite_entanglement': self._calculate_multipartite_entanglement(ghz_state, n_assets)
        }
        
        self.entangled_pairs[tuple(assets)] = ghz_entanglement
        
        return ghz_entanglement
    
    def entangle_portfolios(self, portfolio1: QuantumPortfolioState,
                          portfolio2: QuantumPortfolioState,
                          entanglement_type: str = 'bell') -> Dict:
        """
        Portfolio'lar o'rtasida entanglement yaratish
        
        Args:
            portfolio1: Birinchi portfolio
            portfolio2: Ikkinchi portfolio
            entanglement_type: Entanglement turi ('bell', 'partial', 'continuous')
        
        Returns:
            Entanglement ma'lumotlari
        """
        if len(portfolio1.assets) != len(portfolio2.assets):
            # Dimensional matching
            n_assets = min(len(portfolio1.assets), len(portfolio2.assets))
            assets1 = portfolio1.assets[:n_assets]
            assets2 = portfolio2.assets[:n_assets]
        else:
            assets1 = portfolio1.assets
            assets2 = portfolio2.assets
        
        if entanglement_type == 'bell':
            # Simplified Bell state for portfolios
            if len(assets1) == 1 and len(assets2) == 1:
                entangled_state = self.create_bell_state(assets1[0], assets2[0])
            else:
                # Multi-asset Bell-like entanglement
                n_total = len(assets1) + len(assets2)
                n_basis = 2**n_total
                amplitudes = np.zeros(n_basis, dtype=complex)
                
                # Create superposition of correlated states
                amplitudes[0] = 1/np.sqrt(2)  # |00...0⟩
                amplitudes[-1] = 1/np.sqrt(2)  # |11...1⟩
                
                basis_states = [format(i, f'0{n_total}b') for i in range(n_basis)]
                entangled_state = QuantumState(amplitudes, basis_states)
        
        elif entanglement_type == 'partial':
            # Partial entanglement (not maximally entangled)
            entanglement_strength = self.config.entanglement_strength
            amplitudes = np.zeros((2, 2), dtype=complex)
            amplitudes[0, 0] = np.sqrt(entanglement_strength)
            amplitudes[1, 1] = np.sqrt(1 - entanglement_strength)
            
            # Convert to state vector
            state_amplitudes = amplitudes.flatten()
            entangled_state = QuantumState(state_amplitudes, ['00', '01', '10', '11'])
        
        else:
            raise ValueError(f"Noma'lum entanglement type: {entanglement_type}")
        
        # Calculate entanglement measures
        entanglement_measures = self._calculate_entanglement_measures(entangled_state, len(assets1))
        
        portfolio_entanglement = {
            'portfolio1': portfolio1,
            'portfolio2': portfolio2,
            'entangled_state': entangled_state,
            'entanglement_type': entanglement_type,
            'entanglement_measures': entanglement_measures,
            'correlation_strength': entanglement_measures.get('entanglement_entropy', 0),
            'fidelity': entanglement_measures.get('fidelity', 0)
        }
        
        return portfolio_entanglement
    
    def measure_entanglement(self, entangled_system: Dict) -> Dict:
        """
        Entangled system o'lchovi
        
        Args:
            entangled_system: Entangled system ma'lumotlari
        
        Returns:
            Measurement results
        """
        entangled_state = entangled_system['entangled_state']
        
        # Perform Bell measurement
        measurement_results = []
        n_measurements = 1000
        
        for _ in range(n_measurements):
            result = entangled_state.measure()
            measurement_results.append(result)
        
        # Correlation analysis
        correlations = {}
        unique_results = set(measurement_results)
        
        for result in unique_results:
            count = measurement_results.count(result)
            correlations[result] = count / n_measurements
        
        # Check for quantum correlations
        # In Bell state, we should see strong correlations in basis states
        expected_correlations = {
            '00': 0.5,
            '11': 0.5,
            '01': 0.0,
            '10': 0.0
        }
        
        correlation_error = np.mean([
            abs(correlations.get(state, 0) - expected_correlations[state])
            for state in expected_correlations
        ])
        
        is_quantum_correlated = correlation_error < 0.1
        
        return {
            'measurement_results': measurement_results,
            'frequencies': correlations,
            'expected_frequencies': expected_correlations,
            'correlation_error': correlation_error,
            'is_quantum_correlated': is_quantum_correlated,
            'bell_inequality_violation': self._check_bell_inequality(measurement_results),
            'quantum_violation': correlation_error < 0.1
        }
    
    def quantum_correlation_analysis(self, portfolio1: QuantumPortfolioState,
                                   portfolio2: QuantumPortfolioState) -> Dict:
        """
        Portfolio'lar o'rtasida quantum korrelatsiya tahlili
        
        Args:
            portfolio1: Birinchi portfolio
            portfolio2: Ikkinchi portfolio
        
        Returns:
            Quantum korrelatsiya analizi
        """
        # Create entanglement
        entanglement = self.entangle_portfolios(portfolio1, portfolio2)
        entangled_state = entanglement['entangled_state']
        
        # Measure correlations
        measurement = self.measure_entanglement(entanglement)
        
        # Quantum correlation metrics
        correlation_strength = entanglement['correlation_strength']
        entanglement_entropy = entanglement['entanglement_measures']['entanglement_entropy']
        
        # Portfolio-specific correlations
        portfolio1_corr = np.corrcoef(
            portfolio1.get_portfolio_weights(),
            portfolio2.get_portfolio_weights()
        )[0, 1]
        
        # Quantum vs classical comparison
        classical_correlation = np.abs(portfolio1_corr)
        quantum_correlation = np.abs(entanglement_entropy)
        
        advantage = quantum_correlation - classical_correlation
        
        return {
            'entanglement': entanglement,
            'measurement': measurement,
            'correlation_strength': correlation_strength,
            'entanglement_entropy': entanglement_entropy,
            'classical_correlation': classical_correlation,
            'quantum_correlation': quantum_correlation,
            'quantum_advantage': advantage,
            'is_quantum_advantage': advantage > 0.1,
            'portfolio_correlation': portfolio1_corr
        }
    
    def entanglement_swapping(self, portfolio1: QuantumPortfolioState,
                            portfolio2: QuantumPortfolioState,
                            portfolio3: QuantumPortfolioState) -> Dict:
        """
        Entanglement swapping operatsiyasi
        
        Args:
            portfolio1: Birinchi portfolio
            portfolio2: Ikkinchi portfolio
            portfolio3: Uchinchi portfolio
        
        Returns:
            Entanglement swapping natijasi
        """
        # Create entanglement between 1-2 and 2-3
        entanglement_12 = self.entangle_portfolios(portfolio1, portfolio2)
        entanglement_23 = self.entangle_portfolios(portfolio2, portfolio3)
        
        # Perform Bell measurement on portfolio2 (central system)
        # This would require actual quantum operations
        # For simulation, we calculate theoretical results
        
        # After measurement, 1 and 3 become entangled
        swapped_entanglement = self._simulate_entanglement_swapping(
            entanglement_12, entanglement_23
        )
        
        return {
            'original_entanglements': [entanglement_12, entanglement_23],
            'swapped_entanglement': swapped_entanglement,
            'success_probability': swapped_entanglement.get('success_probability', 0.5),
            'entanglement_fidelity': swapped_entanglement.get('fidelity', 0.8)
        }
    
    def quantum_error_correction(self, entangled_system: Dict,
                               error_rate: float = 0.01) -> Dict:
        """
        Quantum error correction (simulated)
        
        Args:
            entangled_system: Error correction qilinadigan entangled system
            error_rate: Error rate
        
        Returns:
            Error correction natijasi
        """
        entangled_state = entangled_system['entangled_state']
        
        # Simulate quantum errors
        original_state = entangled_state.amplitudes.copy()
        
        # Apply random errors (bit flips, phase flips)
        n_qubits = len(entangled_state.basis_states[0])
        error_matrix = np.eye(len(entangled_state.amplitudes))
        
        # Random error application
        for _ in range(int(error_rate * 1000)):
            error_type = np.random.choice(['bit_flip', 'phase_flip', 'depolarizing'])
            
            if error_type == 'bit_flip':
                # Random bit flip
                flip_idx = np.random.randint(len(entangled_state.amplitudes))
                error_matrix[flip_idx, flip_idx] *= -1
            
            elif error_type == 'phase_flip':
                # Phase flip
                phase_error = np.exp(1j * np.pi * np.random.random())
                error_matrix *= phase_error
            
            elif error_type == 'depolarizing':
                # Depolarizing error (simplified)
                depolarizing_factor = 1 - error_rate
                error_matrix *= depolarizing_factor
        
        # Apply error
        errored_amplitudes = np.dot(error_matrix, original_state)
        errored_state = QuantumState(errored_amplitudes, entangled_state.basis_states)
        
        # Error detection and correction (simplified)
        error_syndrome = self._calculate_error_syndrome(original_state, errored_amplitudes)
        corrected_amplitudes = self._apply_error_correction(original_state, error_syndrome)
        corrected_state = QuantumState(corrected_amplitudes, entangled_state.basis_states)
        
        # Calculate correction success
        fidelity_before = np.abs(np.dot(np.conj(original_state), errored_amplitudes))**2
        fidelity_after = np.abs(np.dot(np.conj(original_state), corrected_amplitudes))**2
        
        return {
            'original_state': entangled_state,
            'errored_state': errored_state,
            'corrected_state': corrected_state,
            'error_syndrome': error_syndrome,
            'fidelity_before': fidelity_before,
            'fidelity_after': fidelity_after,
            'correction_improvement': fidelity_after - fidelity_before,
            'error_rate': error_rate,
            'correction_success': fidelity_after > fidelity_before
        }
    
    def _calculate_entanglement_entropy(self, state: QuantumState) -> float:
        """Entanglement entropy hisoblash"""
        # Calculate reduced density matrix entropy
        # Simplified calculation - in practice, need proper partial trace
        
        # For a pure state, entanglement entropy is related to Schmidt decomposition
        amplitudes = state.amplitudes
        probabilities = np.abs(amplitudes)**2
        
        # Shannon entropy approximation for entanglement entropy
        entropy = 0
        for p in probabilities:
            if p > 0:
                entropy -= p * np.log2(p)
        
        return entropy
    
    def _calculate_multipartite_entanglement(self, state: QuantumState, n_parties: int) -> float:
        """Multipartite entanglement hisoblash"""
        # Simplified multipartite entanglement measure
        amplitudes = state.amplitudes
        probabilities = np.abs(amplitudes)**2
        
        # Generalized entanglement entropy
        max_entropy = np.log2(2**n_parties)
        actual_entropy = 0
        
        for p in probabilities:
            if p > 0:
                actual_entropy -= p * np.log2(p)
        
        return actual_entropy / max_entropy
    
    def _calculate_entanglement_measures(self, state: QuantumState, n_qubits: int) -> Dict:
        """Comprehensive entanglement measures"""
        # Simplified entanglement measures
        entropy = self._calculate_entanglement_entropy(state)
        
        # Concurrence (for 2-qubit states)
        concurrence = 0
        if n_qubits == 2 and len(state.basis_states) == 4:
            # Calculate concurrence for Bell-like states
            concurrence = 2 * np.abs(state.amplitudes[0] * state.amplitudes[-1])
        
        # Fidelity with maximally entangled state
        max_entangled = np.ones(len(state.amplitudes)) / np.sqrt(len(state.amplitudes))
        fidelity = np.abs(np.dot(np.conj(max_entangled), state.amplitudes))**2
        
        return {
            'entanglement_entropy': entropy,
            'concurrence': concurrence,
            'fidelity': fidelity,
            'purity': np.sum(np.abs(state.amplitudes)**4),
            'nonlinearity': 1 - np.sum(np.abs(state.amplitudes)**2)**2
        }
    
    def _check_bell_inequality(self, measurement_results: List[str]) -> float:
        """Bell inequality check"""
        # Simplified CHSH inequality check
        # Count correlations in different basis measurements
        
        results_array = np.array([int(result, 2) for result in measurement_results])
        
        # For CHSH: E(a,b) - E(a,b') + E(a',b) + E(a',b') <= 2
        # Simplified calculation
        correlation_00_00 = np.mean(results_array)  # E(a,b)
        correlation_00_01 = np.mean(results_array)  # E(a,b')
        correlation_01_00 = np.mean(results_array)  # E(a',b)
        correlation_01_01 = np.mean(results_array)  # E(a',b')
        
        chsh_value = (correlation_00_00 - correlation_00_01 + 
                     correlation_01_00 + correlation_01_01)
        
        # Classical bound is 2, quantum can reach 2.828
        violation = abs(chsh_value) - 2
        
        return violation
    
    def _simulate_entanglement_swapping(self, entanglement1: Dict, 
                                      entanglement2: Dict) -> Dict:
        """Entanglement swapping simulation"""
        # Theoretical calculation of entanglement swapping success
        
        # Success probability depends on Bell measurement
        success_probability = 0.25  # 25% for ideal Bell measurement
        
        # Fidelity after swapping
        original_fidelity1 = entanglement1.get('fidelity', 0.8)
        original_fidelity2 = entanglement2.get('fidelity', 0.8)
        swapped_fidelity = np.sqrt(original_fidelity1 * original_fidelity2)
        
        return {
            'success_probability': success_probability,
            'fidelity': swapped_fidelity,
            'entanglement_strength': original_fidelity1 * original_fidelity2,
            'swapped_state_type': 'bell_state'
        }
    
    def _calculate_error_syndrome(self, original: np.ndarray, errored: np.ndarray) -> Dict:
        """Calculate error syndrome"""
        # Simplified error syndrome calculation
        error_size = np.linalg.norm(original - errored)
        
        syndrome = {
            'error_detected': error_size > 0.01,
            'error_magnitude': error_size,
            'error_type': 'unknown'  # In practice, would identify specific error
        }
        
        return syndrome
    
    def _apply_error_correction(self, original: np.ndarray, syndrome: Dict) -> np.ndarray:
        """Apply error correction based on syndrome"""
        if not syndrome['error_detected']:
            return original
        
        # Simplified error correction
        # In practice, would use specific error-correcting codes
        corrected = original.copy()
        
        # Simple error reduction
        error_magnitude = syndrome['error_magnitude']
        correction_factor = 1 - error_magnitude * 0.5  # Partial correction
        
        corrected = corrected / np.linalg.norm(corrected) * correction_factor
        corrected = corrected / np.linalg.norm(corrected)  # Renormalize
        
        return corrected


class QuantumCorrelation:
    """
    Quantum Correlation Analysis
    
    Portfolio'lar o'rtasida quantum korrelatsiya tahlili va boshqarish.
    """
    
    def __init__(self):
        self.correlation_matrix = None
        self.quantum_correlations = {}
        self.classical_correlations = {}
        
    def calculate_quantum_covariance(self, portfolios: List[QuantumPortfolioState]) -> np.ndarray:
        """Quantum covariance matrix hisoblash"""
        n_portfolios = len(portfolios)
        covariance_matrix = np.zeros((n_portfolios, n_portfolios))
        
        for i, port_i in enumerate(portfolios):
            for j, port_j in enumerate(portfolios):
                if i == j:
                    # Variance
                    weights_i = port_i.get_portfolio_weights()
                    variance = np.sum(weights_i**2 * 0.15**2)  # Simplified variance
                    covariance_matrix[i, j] = variance
                else:
                    # Covariance with quantum correlation
                    weights_i = port_i.get_portfolio_weights()
                    weights_j = port_j.get_portfolio_weights()
                    
                    # Quantum correlation factor
                    quantum_corr = port_i.quantum_correlation_with(port_j)
                    
                    # Classical correlation
                    classical_corr = np.corrcoef(weights_i, weights_j)[0, 1]
                    
                    # Combined correlation
                    combined_corr = 0.7 * quantum_corr + 0.3 * classical_corr
                    
                    covariance_matrix[i, j] = combined_corr * np.sqrt(
                        np.sum(weights_i**2 * 0.15**2) * 
                        np.sum(weights_j**2 * 0.15**2)
                    )
        
        return covariance_matrix
    
    def quantum_factor_model(self, portfolios: List[QuantumPortfolioState],
                           n_factors: int = 3) -> Dict:
        """Quantum factor model yaratish"""
        # Create factor structure based on quantum correlations
        correlation_matrix = self.calculate_quantum_covariance(portfolios)
        
        # Factor decomposition (simplified)
        eigenvals, eigenvecs = np.linalg.eigh(correlation_matrix)
        
        # Select top factors
        factor_loadings = eigenvecs[:, -n_factors:]
        factor_variances = eigenvals[-n_factors:]
        
        # Quantum factor interpretation
        quantum_factors = []
        for i in range(n_factors):
            factor_weights = factor_loadings[:, i]
            factor_portfolios = [portfolios[j] for j in range(len(portfolios)) 
                               if abs(factor_weights[j]) > 0.1]
            
            quantum_factors.append({
                'factor_id': f'quantum_factor_{i+1}',
                'variance_explained': factor_variances[i] / np.sum(eigenvals),
                'factor_portfolios': [portfolios[j].assets for j in range(len(portfolios)) 
                                    if abs(factor_weights[j]) > 0.1],
                'factor_weights': factor_weights,
                'interpretation': self._interpret_quantum_factor(factor_portfolios)
            })
        
        return {
            'factor_loadings': factor_loadings,
            'factor_variances': factor_variances,
            'quantum_factors': quantum_factors,
            'total_variance_explained': np.sum(factor_variances) / np.sum(eigenvals),
            'quantum_correlation_strength': np.mean(np.abs(factor_loadings))
        }
    
    def _interpret_quantum_factor(self, portfolios: List[QuantumPortfolioState]) -> str:
        """Quantum factor interpretatsiyasi"""
        if len(portfolios) == 0:
            return "No significant portfolios"
        elif len(portfolios) == 1:
            return f"Single portfolio factor: {portfolios[0].assets}"
        elif len(portfolios) <= 3:
            assets = [asset for portfolio in portfolios for asset in portfolio.assets]
            return f"Small quantum cluster: {assets}"
        else:
            return "Large quantum entangled network"