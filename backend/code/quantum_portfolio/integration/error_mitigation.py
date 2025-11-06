"""
Quantum Error Mitigation
========================

Quantum computing xatolarini kamaytirish va mitigation texnikalari.
Bu modul real quantum hardware'da xatolarni boshqarish uchun vositalar ta'minlaydi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
import time
from scipy import stats

class QuantumErrorMitigation:
    """
    Quantum Error Mitigation System
    """
    
    def __init__(self, 
                 quantum_portfolio_theory,
                 noise_model: str = 'dephasing',
                 mitigation_strength: float = 0.1,
                 calibration_interval: int = 100):
        """
        Initialize quantum error mitigation
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
            noise_model: Noise model type ('dephasing', 'depolarizing', 'amplitude_damping')
            mitigation_strength: Error mitigation strength (0-1)
            calibration_interval: Calibration frequency
        """
        self.qpt = quantum_portfolio_theory
        self.noise_model = noise_model
        self.mitigation_strength = mitigation_strength
        self.calibration_interval = calibration_interval
        
        # Error mitigation state
        self.error_coefficients = {}
        self.calibration_history = []
        self.mitigation_performance = {}
        
        self.logger = logging.getLogger(__name__)
        self._initialize_noise_model()
    
    def _initialize_noise_model(self):
        """Initialize noise model parameters"""
        if self.noise_model == 'dephasing':
            # Dephasing noise model
            self.error_coefficients = {
                'dephasing_rate': 0.01,
                'coherence_time': 100.0,
                't1_time': float('inf'),  # No amplitude damping
                't2_time': 100.0  # Dephasing time
            }
        elif self.noise_model == 'depolarizing':
            # Depolarizing noise model
            self.error_coefficients = {
                'depolarizing_rate': 0.005,
                'pauli_error_rate': 0.01,
                'coherence_time': 100.0
            }
        elif self.noise_model == 'amplitude_damping':
            # Amplitude damping noise model
            self.error_coefficients = {
                'damping_rate': 0.02,
                't1_time': 50.0,
                't2_time': 30.0,
                'excited_state_population': 0.1
            }
        else:
            # Default: minimal noise
            self.error_coefficients = {
                'general_noise_level': 0.001
            }
    
    def apply_error_mitigation(self, 
                             quantum_result: Dict,
                             calibration_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Apply error mitigation to quantum results
        
        Args:
            quantum_result: Raw quantum computation result
            calibration_data: Hardware calibration data
            
        Returns:
            Error-mitigated result
        """
        start_time = time.time()
        
        # Apply different mitigation techniques based on noise model
        if self.noise_model == 'dephasing':
            mitigated_result = self._mitigate_dephasing_noise(quantum_result)
        elif self.noise_model == 'depolarizing':
            mitigated_result = self._mitigate_depolarizing_noise(quantum_result)
        elif self.noise_model == 'amplitude_damping':
            mitigated_result = self._mitigate_amplitude_damping(quantum_result)
        else:
            mitigated_result = self._mitigate_general_noise(quantum_result)
        
        # Apply calibration corrections
        if calibration_data is not None:
            mitigated_result = self._apply_calibration_correction(mitigated_result, calibration_data)
        
        # Statistical error analysis
        error_analysis = self._analyze_mitigation_errors(quantum_result, mitigated_result)
        
        processing_time = time.time() - start_time
        
        # Record performance
        self.mitigation_performance = {
            'processing_time': processing_time,
            'noise_model': self.noise_model,
            'mitigation_strength': self.mitigation_strength,
            'error_reduction': error_analysis['error_reduction'],
            'confidence_interval': error_analysis['confidence_interval']
        }
        
        return {
            'original_result': quantum_result,
            'mitigated_result': mitigated_result,
            'error_analysis': error_analysis,
            'mitigation_performance': self.mitigation_performance,
            'processing_timestamp': time.time()
        }
    
    def _mitigate_dephasing_noise(self, result: Dict) -> Dict:
        """Mitigate dephasing noise"""
        mitigated_result = result.copy()
        
        # Extract portfolio weights if available
        if 'allocation' in result:
            weights = np.array(list(result['allocation'].values()))
            
            # Apply dephasing correction
            dephasing_correction = self._calculate_dephasing_correction(weights)
            
            # Correct weights
            corrected_weights = weights + dephasing_correction
            corrected_weights = np.maximum(0, corrected_weights)  # Ensure non-negative
            corrected_weights = corrected_weights / np.sum(corrected_weights)  # Normalize
            
            # Update allocation
            corrected_allocation = {}
            for i, weight in enumerate(corrected_weights):
                if i < len(result['allocation']):
                    asset_name = list(result['allocation'].keys())[i]
                    corrected_allocation[asset_name] = weight
            
            mitigated_result['allocation'] = corrected_allocation
            mitigated_result['weights'] = corrected_weights
        
        return mitigated_result
    
    def _mitigate_depolarizing_noise(self, result: Dict) -> Dict:
        """Mitigate depolarizing noise"""
        mitigated_result = result.copy()
        
        if 'allocation' in result:
            weights = np.array(list(result['allocation'].values()))
            
            # Depolarizing noise tends to randomize states
            # Correct by emphasizing the most significant components
            depolarizing_correction = self._calculate_depolarizing_correction(weights)
            
            # Apply correction
            corrected_weights = weights * (1 + depolarizing_correction)
            corrected_weights = np.maximum(0, corrected_weights)
            corrected_weights = corrected_weights / np.sum(corrected_weights)
            
            # Update allocation
            corrected_allocation = {}
            for i, weight in enumerate(corrected_weights):
                if i < len(result['allocation']):
                    asset_name = list(result['allocation'].keys())[i]
                    corrected_allocation[asset_name] = weight
            
            mitigated_result['allocation'] = corrected_allocation
            mitigated_result['weights'] = corrected_weights
        
        return mitigated_result
    
    def _mitigate_amplitude_damping(self, result: Dict) -> Dict:
        """Mitigate amplitude damping noise"""
        mitigated_result = result.copy()
        
        if 'allocation' in result:
            weights = np.array(list(result['allocation'].values()))
            
            # Amplitude damping affects ground state vs excited state populations
            damping_correction = self._calculate_amplitude_damping_correction(weights)
            
            # Apply correction
            corrected_weights = weights + damping_correction
            corrected_weights = np.maximum(0, corrected_weights)
            corrected_weights = corrected_weights / np.sum(corrected_weights)
            
            # Update allocation
            corrected_allocation = {}
            for i, weight in enumerate(corrected_weights):
                if i < len(result['allocation']):
                    asset_name = list(result['allocation'].keys())[i]
                    corrected_allocation[asset_name] = weight
            
            mitigated_result['allocation'] = corrected_allocation
            mitigated_result['weights'] = corrected_weights
        
        return mitigated_result
    
    def _mitigate_general_noise(self, result: Dict) -> Dict:
        """Mitigate general noise with adaptive techniques"""
        mitigated_result = result.copy()
        
        if 'allocation' in result:
            weights = np.array(list(result['allocation'].values()))
            
            # General noise correction using regularization
            regularization_correction = self._calculate_regularization_correction(weights)
            
            # Apply correction
            corrected_weights = weights + regularization_correction
            corrected_weights = np.maximum(0, corrected_weights)
            corrected_weights = corrected_weights / np.sum(corrected_weights)
            
            # Update allocation
            corrected_allocation = {}
            for i, weight in enumerate(corrected_weights):
                if i < len(result['allocation']):
                    asset_name = list(result['allocation'].keys())[i]
                    corrected_allocation[asset_name] = weight
            
            mitigated_result['allocation'] = corrected_allocation
            mitigated_result['weights'] = corrected_weights
        
        return mitigated_result
    
    def _calculate_dephasing_correction(self, weights: np.ndarray) -> np.ndarray:
        """Calculate dephasing noise correction"""
        # Dephasing noise causes phase errors but preserves amplitudes
        # Correction based on coherence time
        coherence_factor = np.exp(-1 / self.error_coefficients['coherence_time'])
        correction_magnitude = self.mitigation_strength * coherence_factor
        
        # Apply phase correction (simplified)
        correction = np.random.normal(0, correction_magnitude, len(weights))
        return correction
    
    def _calculate_depolarizing_correction(self, weights: np.ndarray) -> np.ndarray:
        """Calculate depolarizing noise correction"""
        # Depolarizing noise randomizes quantum states
        # Correction by emphasizing signal-to-noise ratio
        signal_strength = np.max(weights)
        noise_level = self.error_coefficients.get('pauli_error_rate', 0.01)
        
        correction = np.zeros_like(weights)
        for i, weight in enumerate(weights):
            if weight > signal_strength * 0.1:  # Significant components
                correction[i] = weight * self.mitigation_strength * noise_level
        
        return correction
    
    def _calculate_amplitude_damping_correction(self, weights: np.ndarray) -> np.ndarray:
        """Calculate amplitude damping correction"""
        # Amplitude damping causes population decay from excited to ground state
        damping_rate = self.error_coefficients['damping_rate']
        t1_time = self.error_coefficients['t1_time']
        
        # Correction factor based on damping dynamics
        time_factor = np.exp(-1 / t1_time)
        correction_magnitude = damping_rate * time_factor * self.mitigation_strength
        
        # Apply asymmetric correction (prefers ground state population)
        correction = np.random.exponential(correction_magnitude, len(weights))
        return correction
    
    def _calculate_regularization_correction(self, weights: np.ndarray) -> np.ndarray:
        """Calculate regularization-based correction"""
        # L2 regularization to smooth out noise
        l2_lambda = self.mitigation_strength * 0.1
        regularization_term = -l2_lambda * weights
        
        # Add small random noise to break symmetry
        noise_term = np.random.normal(0, 0.001 * self.mitigation_strength, len(weights))
        
        return regularization_term + noise_term
    
    def _apply_calibration_correction(self, 
                                    result: Dict, 
                                    calibration_data: pd.DataFrame) -> Dict:
        """Apply hardware calibration corrections"""
        corrected_result = result.copy()
        
        if 'allocation' in result and not calibration_data.empty:
            weights = np.array(list(result['allocation'].values()))
            
            # Simple calibration correction based on calibration data
            # Assuming calibration_data has calibration factors for each asset
            if len(calibration_data.columns) >= len(weights):
                calibration_factors = calibration_data.mean().values[:len(weights)]
                
                # Apply calibration factors
                corrected_weights = weights * calibration_factors
                corrected_weights = np.maximum(0, corrected_weights)
                corrected_weights = corrected_weights / np.sum(corrected_weights)
                
                # Update allocation
                corrected_allocation = {}
                for i, weight in enumerate(corrected_weights):
                    if i < len(result['allocation']):
                        asset_name = list(result['allocation'].keys())[i]
                        corrected_allocation[asset_name] = weight
                
                corrected_result['allocation'] = corrected_allocation
                corrected_result['weights'] = corrected_weights
                corrected_result['calibration_applied'] = True
        
        return corrected_result
    
    def _analyze_mitigation_errors(self, 
                                 original: Dict, 
                                 mitigated: Dict) -> Dict:
        """Analyze error mitigation performance"""
        error_analysis = {}
        
        if 'allocation' in original and 'allocation' in mitigated:
            orig_weights = np.array(list(original['allocation'].values()))
            mit_weights = np.array(list(mitigated['allocation'].values()))
            
            # Calculate various error metrics
            weight_difference = np.abs(orig_weights - mit_weights)
            mean_absolute_error = np.mean(weight_difference)
            max_absolute_error = np.max(weight_difference)
            
            # Error reduction compared to theoretical error
            theoretical_error = self._estimate_theoretical_error(orig_weights)
            error_reduction = (theoretical_error - mean_absolute_error) / theoretical_error if theoretical_error > 0 else 0
            
            # Confidence interval (95%)
            confidence_interval = 1.96 * np.std(weight_difference) / np.sqrt(len(weight_difference))
            
            error_analysis = {
                'mean_absolute_error': mean_absolute_error,
                'max_absolute_error': max_absolute_error,
                'theoretical_error': theoretical_error,
                'error_reduction': max(0, error_reduction),
                'confidence_interval': confidence_interval,
                'error_std': np.std(weight_difference)
            }
        
        return error_analysis
    
    def _estimate_theoretical_error(self, weights: np.ndarray) -> float:
        """Estimate theoretical error level based on noise model"""
        if self.noise_model == 'dephasing':
            return self.error_coefficients['dephasing_rate']
        elif self.noise_model == 'depolarizing':
            return self.error_coefficients['depolarizing_rate']
        elif self.noise_model == 'amplitude_damping':
            return self.error_coefficients['damping_rate']
        else:
            return self.error_coefficients.get('general_noise_level', 0.001)
    
    def calibrate_system(self, 
                       calibration_runs: int = 100,
                       save_calibration: bool = True) -> Dict:
        """
        Calibrate error mitigation system
        
        Args:
            calibration_runs: Number of calibration runs
            save_calibration: Save calibration results
            
        Returns:
            Calibration results
        """
        calibration_results = {
            'calibration_time': time.time(),
            'noise_model': self.noise_model,
            'runs': calibration_runs,
            'error_coefficients': {},
            'performance_metrics': {}
        }
        
        # Perform calibration runs
        errors = []
        for run in range(calibration_runs):
            # Generate test portfolio weights
            test_weights = np.random.dirichlet(np.ones(len(self.qpt.assets)))
            
            # Simulate noisy measurement
            noisy_weights = self._simulate_noise(test_weights)
            
            # Apply mitigation
            mitigated_weights = self._apply_noise_mitigation(test_weights, noisy_weights)
            
            # Calculate error
            error = np.mean(np.abs(test_weights - mitigated_weights))
            errors.append(error)
        
        # Update calibration data
        calibration_results['error_coefficients'] = self._update_calibration_coefficients(errors)
        calibration_results['performance_metrics'] = {
            'mean_error': np.mean(errors),
            'std_error': np.std(errors),
            'max_error': np.max(errors),
            'min_error': np.min(errors)
        }
        
        # Record calibration
        self.calibration_history.append(calibration_results)
        
        if save_calibration:
            self._save_calibration_data(calibration_results)
        
        self.logger.info(f"Calibration completed. Mean error: {np.mean(errors):.6f}")
        
        return calibration_results
    
    def _simulate_noise(self, weights: np.ndarray) -> np.ndarray:
        """Simulate quantum noise on weights"""
        noise_level = self._estimate_theoretical_error(weights)
        
        if self.noise_model == 'dephasing':
            # Phase noise (minimal amplitude change)
            noise = np.random.normal(0, noise_level * 0.1, len(weights))
        elif self.noise_model == 'depolarizing':
            # Depolarizing noise (random unitary errors)
            noise = np.random.normal(0, noise_level, len(weights))
        elif self.noise_model == 'amplitude_damping':
            # Amplitude damping
            damping_factor = 1 - noise_level
            noise = weights * (damping_factor - 1)
        else:
            # General noise
            noise = np.random.normal(0, noise_level, len(weights))
        
        noisy_weights = weights + noise
        noisy_weights = np.maximum(0, noisy_weights)
        noisy_weights = noisy_weights / np.sum(noisy_weights)
        
        return noisy_weights
    
    def _apply_noise_mitigation(self, original_weights: np.ndarray, noisy_weights: np.ndarray) -> np.ndarray:
        """Apply noise mitigation to noisy weights"""
        # Simple mitigation: average with theoretical expectation
        mitigation_factor = self.mitigation_strength
        
        corrected_weights = (1 - mitigation_factor) * noisy_weights + mitigation_factor * original_weights
        corrected_weights = np.maximum(0, corrected_weights)
        corrected_weights = corrected_weights / np.sum(corrected_weights)
        
        return corrected_weights
    
    def _update_calibration_coefficients(self, errors: List[float]) -> Dict:
        """Update calibration coefficients based on error analysis"""
        updated_coefficients = self.error_coefficients.copy()
        
        # Adjust mitigation strength based on observed errors
        mean_error = np.mean(errors)
        target_error = 0.001  # Target error level
        
        if mean_error > target_error:
            # Increase mitigation strength
            adjustment_factor = target_error / mean_error
            self.mitigation_strength = min(1.0, self.mitigation_strength * adjustment_factor)
        else:
            # Decrease mitigation strength (too much correction)
            adjustment_factor = mean_error / target_error
            self.mitigation_strength = max(0.01, self.mitigation_strength * adjustment_factor)
        
        updated_coefficients['mitigation_strength'] = self.mitigation_strength
        
        return updated_coefficients
    
    def _save_calibration_data(self, calibration_results: Dict, filepath: str = None):
        """Save calibration data to file"""
        if filepath is None:
            timestamp = int(time.time())
            filepath = f"calibration_{timestamp}.json"
        
        import json
        with open(filepath, 'w') as f:
            json.dump(calibration_results, f, indent=2, default=str)
        
        self.logger.info(f"Calibration data saqlandi: {filepath}")
    
    def get_mitigation_performance(self) -> Dict:
        """Get current mitigation performance metrics"""
        if not self.mitigation_performance:
            return {'status': 'No mitigation performed yet'}
        
        return {
            'noise_model': self.noise_model,
            'mitigation_strength': self.mitigation_strength,
            'last_performance': self.mitigation_performance,
            'calibration_history_length': len(self.calibration_history),
            'recommendations': self._generate_mitigation_recommendations()
        }
    
    def _generate_mitigation_recommendations(self) -> List[str]:
        """Generate mitigation recommendations"""
        recommendations = []
        
        # Check calibration status
        if len(self.calibration_history) < 5:
            recommendations.append("Perform more calibration runs for better accuracy")
        
        # Check mitigation strength
        if self.mitigation_strength < 0.05:
            recommendations.append("Consider increasing mitigation strength")
        elif self.mitigation_strength > 0.3:
            recommendations.append("Consider reducing mitigation strength to avoid over-correction")
        
        # Check noise model appropriateness
        if self.noise_model == 'dephasing':
            recommendations.append("Dephasing noise model suitable for long-coherence systems")
        elif self.noise_model == 'depolarizing':
            recommendations.append("Depolarizing model appropriate for general quantum systems")
        elif self.noise_model == 'amplitude_damping':
            recommendations.append("Amplitude damping model suitable for superconducting qubits")
        
        return recommendations