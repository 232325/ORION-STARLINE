"""
Quantum State Module
===================

Quantum superposition holatlari va portfolio quantum state representations.
"""

import numpy as np
import cmath
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from scipy.linalg import norm


@dataclass
class QuantumState:
    """
    Asosiy quantum holat klassi
    
    Quantum holatlarni ifodalash va boshqarish uchun ishlatiladi.
    """
    
    amplitudes: np.ndarray
    basis_states: List[str]
    
    def __post_init__(self):
        """Quantum holat normalizatsiyasi"""
        self.normalize()
    
    def normalize(self) -> None:
        """Holat vektorini normalizatsiya qilish"""
        norm_factor = norm(self.amplitudes)
        if norm_factor > 0:
            self.amplitudes = self.amplitudes / norm_factor
    
    def get_probabilities(self) -> np.ndarray:
        """Har bir holatning ehtimolligini olish"""
        return np.abs(self.amplitudes) ** 2
    
    def measure(self) -> str:
        """Quantum o'lchov operatsiyasi"""
        probabilities = self.get_probabilities()
        return np.random.choice(self.basis_states, p=probabilities)
    
    def superposition_with(self, other: 'QuantumState', alpha: float = None) -> 'QuantumState':
        """Ikki quantum holatning superposition yaratish"""
        if alpha is None:
            alpha = 1 / np.sqrt(2)
        
        # Amplitude kombinatsiyasi
        combined_amplitudes = alpha * self.amplitudes + np.sqrt(1 - alpha**2) * other.amplitudes
        combined_states = self.basis_states + other.basis_states
        
        return QuantumState(combined_amplitudes, combined_states)
    
    def expectation_value(self, operator: np.ndarray) -> complex:
        """Operatorning expectation qiymati"""
        return np.dot(np.conj(self.amplitudes), np.dot(operator, self.amplitudes))
    
    def fidelity(self, other: 'QuantumState') -> float:
        """Ikki holat o'rtasidagi fidelity"""
        inner_product = np.abs(np.dot(np.conj(self.amplitudes), other.amplitudes))
        return inner_product**2


class QuantumPortfolioState:
    """
    Portfolio uchun quantum holat klassi
    
    Portfolio assetlari uchun quantum superposition holatini boshqaradi.
    """
    
    def __init__(self, assets: List[str], weights: np.ndarray = None):
        self.assets = assets
        self.n_assets = len(assets)
        
        if weights is None:
            # Equal superposition
            weights = np.ones(self.n_assets) / np.sqrt(self.n_assets)
        
        self.state = QuantumState(weights, assets)
        self.returns_history = {}
        self.risk_factors = {}
    
    def set_portfolio_state(self, weights: np.ndarray) -> None:
        """Portfolio holatini yangilash"""
        if len(weights) != self.n_assets:
            raise ValueError("Weightlar soni assetlar soniga mos kelmadi")
        
        self.state = QuantumState(weights, self.assets)
    
    def get_expected_return(self, returns_matrix: np.ndarray) -> float:
        """Portfolio kutish daromadini hisoblash"""
        weights = self.state.amplitudes
        return np.dot(weights, np.mean(returns_matrix, axis=1))
    
    def get_risk(self, covariance_matrix: np.ndarray) -> float:
        """Portfolio riskini hisoblash"""
        weights = self.state.amplitudes
        risk = np.dot(weights, np.dot(covariance_matrix, np.conj(weights)))
        return np.sqrt(np.real(risk))
    
    def get_sharpe_ratio(self, returns_matrix: np.ndarray, 
                        covariance_matrix: np.ndarray, 
                        risk_free_rate: float = 0.02) -> float:
        """Sharpe ratio hisoblash"""
        expected_return = self.get_expected_return(returns_matrix)
        risk = self.get_risk(covariance_matrix)
        
        if risk == 0:
            return 0
        
        return (expected_return - risk_free_rate) / risk
    
    def quantum_measure(self) -> str:
        """Portfolio quantum o'lchovi"""
        return self.state.measure()
    
    def collapse_to_asset(self, asset: str) -> 'QuantumPortfolioState':
        """Portfolio holatini bir assetga collapse qilish"""
        if asset not in self.assets:
            raise ValueError(f"Asset {asset} mavjud emas")
        
        asset_idx = self.assets.index(asset)
        new_weights = np.zeros(self.n_assets)
        new_weights[asset_idx] = 1.0
        
        return QuantumPortfolioState(self.assets, new_weights)
    
    def create_superposition(self, other: 'QuantumPortfolioState', 
                           alpha: float = None) -> 'QuantumPortfolioState':
        """Boshqa portfolio bilan superposition yaratish"""
        if alpha is None:
            alpha = 1 / np.sqrt(2)
        
        # Asset nomlarini birlashtirish
        all_assets = list(set(self.assets + other.assets))
        n_total = len(all_assets)
        
        # Weight vektorlarini moslashtirish
        weights1 = np.zeros(n_total, dtype=complex)
        weights2 = np.zeros(n_total, dtype=complex)
        
        for i, asset in enumerate(all_assets):
            if asset in self.assets:
                weights1[i] = self.state.amplitudes[self.assets.index(asset)]
            if asset in other.assets:
                weights2[i] = other.state.amplitudes[other.assets.index(asset)]
        
        # Superposition yaratish
        combined_amplitudes = alpha * weights1 + np.sqrt(1 - alpha**2) * weights2
        
        return QuantumPortfolioState(all_assets, combined_amplitudes)
    
    def quantum_correlation_with(self, other: 'QuantumPortfolioState') -> float:
        """Boshqa portfolio bilan quantum korrelatsiya"""
        # State vektorlarini moslashtirish
        all_assets = list(set(self.assets + other.assets))
        n_total = len(all_assets)
        
        weights1 = np.zeros(n_total, dtype=complex)
        weights2 = np.zeros(n_total, dtype=complex)
        
        for i, asset in enumerate(all_assets):
            if asset in self.assets:
                weights1[i] = self.state.amplitudes[self.assets.index(asset)]
            if asset in other.assets:
                weights2[i] = other.state.amplitudes[other.assets.index(asset)]
        
        # Fidelity hisoblash
        inner_product = np.abs(np.dot(np.conj(weights1), weights2))
        return inner_product**2
    
    def add_noise(self, noise_level: float = 0.01) -> None:
        """Quantum holatga noise qo'shish"""
        noise = np.random.normal(0, noise_level, self.n_assets) + \
                1j * np.random.normal(0, noise_level, self.n_assets)
        self.state.amplitudes += noise
        self.state.normalize()
    
    def get_state_vector(self) -> np.ndarray:
        """Holat vektorini qaytarish"""
        return self.state.amplitudes.copy()
    
    def get_info(self) -> Dict:
        """Portfolio holati haqida ma'lumot"""
        return {
            'assets': self.assets,
            'weights': self.get_portfolio_weights(),
            'expected_return': 'Hisoblash uchun returns_data kerak',
            'quantum_correlation': self.state.get_probabilities(),
            'state_vector': self.get_state_vector()
        }
    
    def get_portfolio_weights(self) -> np.ndarray:
        """Real portfolio weights (amplitudes moduli)"""
        return np.abs(self.state.amplitudes) ** 2


def create_portfolio_quantum_state(assets: List[str], 
                                 returns_data: np.ndarray,
                                 target_weights: np.ndarray = None) -> QuantumPortfolioState:
    """
    Returns ma'lumotlari asosida portfolio quantum holati yaratish
    """
    if target_weights is None:
        # Equal weights
        target_weights = np.ones(len(assets)) / len(assets)
    
    # Returns asosida quantum amplitudes hisoblash
    mean_returns = np.mean(returns_data, axis=1)
    positive_returns = np.maximum(mean_returns, 0.001)  # Minimum positive value
    
    # Normalize weights
    weights = positive_returns / np.sum(positive_returns)
    
    return QuantumPortfolioState(assets, weights)


def quantum_entangle_portfolios(portfolio1: QuantumPortfolioState,
                              portfolio2: QuantumPortfolioState) -> Tuple[QuantumPortfolioState, QuantumPortfolioState]:
    """Portfolio'larni quantum entanglement qilish"""
    # Bell state yaratish
    combined_assets = list(set(portfolio1.assets + portfolio2.assets))
    n_assets = len(combined_assets)
    
    if n_assets != 2:
        raise ValueError("Bell state uchun faqat 2 asset kerak")
    
    # Bell state amplitudes
    amplitudes = np.array([1/np.sqrt(2), 1/np.sqrt(2), 0, 0], dtype=complex)
    basis_states = ['00', '01', '10', '11']
    
    bell_state = QuantumState(amplitudes, basis_states)
    
    return bell_state, combined_assets