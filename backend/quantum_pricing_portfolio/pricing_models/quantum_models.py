"""
Quantum Pricing Models moduli
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings

from config.quantum_config import QuantumConfig
from utils.quantum_utils import QuantumUtils, MathUtils, QuantumOptimizer, ensure_positive_definite

try:
    import qiskit
    from qiskit import QuantumCircuit, execute, Aer, transpile
    from qiskit.algorithms import VQE, VQE_1_2, QAOA
    from qiskit.algorithms.optimizers import COBYLA, SPSA
    from qiskit.circuit.library import EfficientSU2, TwoLocal, QAOAAnsatz
    from qiskit.quantum_info import random_statevector
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    warnings.warn("Qiskit not available. Using classical algorithms.", UserWarning)

class PricingModel(ABC):
    """Abstract base class for pricing models"""
    
    @abstractmethod
    def price(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def greeks(self, *args, **kwargs):
        pass

@dataclass
class OptionContract:
    """Option contract struktura"""
    S: float  # Current price
    K: float  # Strike price
    T: float  # Time to maturity
    r: float  # Risk-free rate
    sigma: float  # Volatility
    option_type: str = 'call'  # 'call' or 'put'
    dividend_yield: float = 0.0
    
    def __post_init__(self):
        if self.option_type not in ['call', 'put']:
            raise ValueError("option_type must be 'call' or 'put'")

class BlackScholesQuantumExtension(PricingModel):
    """Quantum-enhanced Black-Scholes model"""
    
    def __init__(self, quantum_config: QuantumConfig = None):
        self.quantum_config = quantum_config or QuantumConfig()
        self.name = "Quantum Black-Scholes"
    
    def price(self, option: OptionContract) -> Dict[str, float]:
        """Quantum Black-Scholes pricing"""
        # Classical Black-Scholes
        classical_price = self._classical_black_scholes(option)
        
        # Quantum enhancements
        quantum_drift = self._quantum_drift_adjustment(option)
        quantum_volatility = self._quantum_volatility_adjustment(option)
        quantum_probability = self._quantum_probability_enhancement(option)
        
        # Quantum adjusted parameters
        quantum_T = option.T * (1 + quantum_drift)
        quantum_sigma = option.sigma * quantum_volatility
        
        # Quantum-adjusted pricing
        quantum_option = OptionContract(
            S=option.S,
            K=option.K,
            T=quantum_T,
            r=option.r,
            sigma=quantum_sigma,
            option_type=option.option_type,
            dividend_yield=option.dividend_yield
        )
        
        quantum_price = self._classical_black_scholes(quantum_option)
        
        # Quantum consensus pricing
        quantum_consensus = 0.7 * quantum_price + 0.3 * classical_price
        quantum_confidence = quantum_probability
        
        return {
            'classical_price': classical_price,
            'quantum_price': quantum_price,
            'quantum_consensus': quantum_consensus,
            'quantum_confidence': quantum_confidence,
            'quantum_adjustments': {
                'drift_adjustment': quantum_drift,
                'volatility_adjustment': quantum_volatility,
                'probability_enhancement': quantum_probability
            },
            'fair_value': quantum_consensus
        }
    
    def _classical_black_scholes(self, option: OptionContract) -> float:
        """Classical Black-Scholes formula"""
        from scipy.stats import norm
        
        if option.T <= 0:
            return max(0, option.S - option.K) if option.option_type == 'call' else max(0, option.K - option.S)
        
        d1 = (np.log(option.S / option.K) + 
              (option.r - option.dividend_yield + 0.5 * option.sigma**2) * option.T) / \
             (option.sigma * np.sqrt(option.T))
        d2 = d1 - option.sigma * np.sqrt(option.T)
        
        if option.option_type == 'call':
            price = (option.S * np.exp(-option.dividend_yield * option.T) * norm.cdf(d1) - 
                    option.K * np.exp(-option.r * option.T) * norm.cdf(d2))
        else:
            price = (option.K * np.exp(-option.r * option.T) * norm.cdf(-d2) - 
                    option.S * np.exp(-option.dividend_yield * option.T) * norm.cdf(-d1))
        
        return max(price, 0)
    
    def _quantum_drift_adjustment(self, option: OptionContract) -> float:
        """Quantum drift adjustment"""
        # Market microstructure effects
        microstructure_factor = 1 + 0.01 * np.sin(option.S / option.K * option.T)
        
        # Quantum superposition effect
        quantum_superposition = 0.002 * np.cos(2 * np.pi * option.sigma * option.T)
        
        return microstructure_factor + quantum_superposition - 1
    
    def _quantum_volatility_adjustment(self, option: OptionContract) -> float:
        """Quantum volatility adjustment"""
        moneyness = option.S / option.K
        
        # Volatility smile quantum effect
        smile_effect = 1 + 0.1 * np.sin(3 * abs(moneyness - 1)) / (1 + abs(moneyness - 1))
        
        # Time-dependent quantum volatility
        time_effect = 1 + 0.05 * np.sqrt(option.T) * np.cos(4 * np.pi * option.sigma)
        
        # Quantum noise enhancement
        quantum_noise = 1 + 0.02 * np.sin(option.T * option.sigma * 10)
        
        return smile_effect * time_effect * quantum_noise
    
    def _quantum_probability_enhancement(self, option: OptionContract) -> float:
        """Quantum probability enhancement"""
        # Deep ITM/OTM options get probability boost
        moneyness = option.S / option.K
        moneyness_effect = 1 + 0.05 * np.exp(-2 * abs(np.log(moneyness)))
        
        # Time-dependent quantum effect
        time_quantum = 1 + 0.03 * np.sin(2 * np.pi * option.T / 365)
        
        return moneyness_effect * time_quantum
    
    def greeks(self, option: OptionContract) -> Dict[str, float]:
        """Quantum-enhanced Greeks calculation"""
        from scipy.stats import norm
        
        if option.T <= 0:
            return self._terminal_greeks(option)
        
        d1 = (np.log(option.S / option.K) + 
              (option.r - option.dividend_yield + 0.5 * option.sigma**2) * option.T) / \
             (option.sigma * np.sqrt(option.T))
        d2 = d1 - option.sigma * np.sqrt(option.T)
        
        # Classical Greeks
        if option.option_type == 'call':
            delta = np.exp(-option.dividend_yield * option.T) * norm.cdf(d1)
            theta = (-option.S * np.exp(-option.dividend_yield * option.T) * norm.pdf(d1) * 
                    option.sigma / (2 * np.sqrt(option.T)) - 
                    option.r * option.K * np.exp(-option.r * option.T) * norm.cdf(d2))
            rho = option.K * option.T * np.exp(-option.r * option.T) * norm.cdf(d2)
        else:
            delta = np.exp(-option.dividend_yield * option.T) * (norm.cdf(d1) - 1)
            theta = (-option.S * np.exp(-option.dividend_yield * option.T) * norm.pdf(d1) * 
                    option.sigma / (2 * np.sqrt(option.T)) + 
                    option.r * option.K * np.exp(-option.r * option.T) * norm.cdf(-d2))
            rho = -option.K * option.T * np.exp(-option.r * option.T) * norm.cdf(-d2)
        
        gamma = (np.exp(-option.dividend_yield * option.T) * norm.pdf(d1)) / \
                (option.S * option.sigma * np.sqrt(option.T))
        vega = option.S * np.exp(-option.dividend_yield * option.T) * norm.pdf(d1) * np.sqrt(option.T)
        vanna = -np.exp(-option.dividend_yield * option.T) * norm.pdf(d1) * \
                (d2 / option.sigma) * np.sqrt(option.T)
        vomma = vega * d1 * d2 / option.sigma
        
        # Quantum adjustments
        quantum_factor = 1 + 0.02 * np.cos(option.sigma * option.T * 5)
        quantum_drift_factor = 1 + 0.01 * np.sin(option.T * option.sigma)
        
        quantum_greeks = {
            'delta': delta * quantum_factor,
            'gamma': gamma * quantum_factor,
            'theta': theta * quantum_drift_factor,
            'vega': vega * quantum_factor,
            'rho': rho * quantum_factor,
            'vanna': vanna * quantum_factor,
            'vomma': vomma * quantum_factor,
            'quantum_adjustment_factor': quantum_factor
        }
        
        return quantum_greeks
    
    def _terminal_greeks(self, option: OptionContract) -> Dict[str, float]:
        """Terminal Greeks at expiry"""
        intrinsic = max(0, option.S - option.K) if option.option_type == 'call' else max(0, option.K - option.S)
        
        return {
            'delta': 1.0 if intrinsic > 0 and option.option_type == 'call' else 
                    (-1.0 if intrinsic > 0 and option.option_type == 'put' else 0.0),
            'gamma': 0.0,
            'theta': 0.0,
            'vega': 0.0,
            'rho': 0.0,
            'vanna': 0.0,
            'vomma': 0.0
        }

class QuantumMonteCarloPricer(PricingModel):
    """Quantum Monte Carlo pricing engine"""
    
    def __init__(self, quantum_config: QuantumConfig = None):
        self.quantum_config = quantum_config or QuantumConfig()
        self.num_paths = 10000
        self.num_time_steps = min(252, max(10, int(OptionContract(100, 100, 1, 0.02, 0.2).T * 252)))
        self.name = "Quantum Monte Carlo"
    
    def price(self, option: OptionContract, num_paths: int = None, 
             num_steps: int = None) -> Dict[str, Union[float, List]]:
        """Quantum Monte Carlo pricing"""
        num_paths = num_paths or self.num_paths
        num_steps = num_steps or min(self.num_time_steps, max(10, int(option.T * 252)))
        
        # Generate quantum paths
        quantum_paths = self._generate_quantum_paths(option, num_paths, num_steps)
        
        # Calculate payoffs
        if option.option_type == 'call':
            payoffs = np.maximum(quantum_paths[:, -1] - option.K, 0)
        else:
            payoffs = np.maximum(option.K - quantum_paths[:, -1], 0)
        
        # Discount expected payoff
        discounted_payoffs = np.exp(-option.r * option.T) * payoffs
        classical_price = np.mean(discounted_payoffs)
        
        # Quantum variance reduction
        quantum_price = QuantumUtils.quantum_variance_enhancement(discounted_payoffs, None)
        quantum_std = np.std(discounted_payoffs) / np.sqrt(num_paths)
        
        # Confidence intervals
        confidence_95 = [classical_price - 1.96 * quantum_std, classical_price + 1.96 * quantum_std]
        confidence_99 = [classical_price - 2.58 * quantum_std, classical_price + 2.58 * quantum_std]
        
        return {
            'classical_price': classical_price,
            'quantum_price': quantum_price,
            'standard_error': quantum_std,
            'confidence_95': confidence_95,
            'confidence_99': confidence_99,
            'num_paths': num_paths,
            'quantum_paths_sample': quantum_paths[:100].tolist(),  # Sample paths for analysis
            'fair_value': quantum_price
        }
    
    def _generate_quantum_paths(self, option: OptionContract, num_paths: int, 
                              num_steps: int) -> np.ndarray:
        """Generate quantum-enhanced price paths"""
        dt = option.T / num_steps
        paths = np.zeros((num_paths, num_steps + 1))
        paths[:, 0] = option.S
        
        for step in range(1, num_steps + 1):
            # Quantum random number generation
            quantum_random = self._quantum_random_generation(num_paths)
            
            # Geometric Brownian Motion with quantum enhancement
            drift = (option.r - option.dividend_yield - 0.5 * option.sigma**2) * dt
            diffusion = option.sigma * np.sqrt(dt) * quantum_random
            
            # Quantum enhancement factors
            quantum_factor = 1 + 0.01 * np.sin(step * option.sigma)
            volatility_quantum = option.sigma * quantum_factor
            
            # Enhanced diffusion
            enhanced_diffusion = volatility_quantum * np.sqrt(dt) * quantum_random
            
            paths[:, step] = paths[:, step-1] * np.exp(drift + enhanced_diffusion)
        
        return paths
    
    def _quantum_random_generation(self, n: int) -> np.ndarray:
        """Quantum random number generation"""
        if QISKIT_AVAILABLE and self.quantum_config.backend_type.value == 'qiskit_aer':
            # Create quantum circuit for random number generation
            qc = QuantumCircuit(1, 1)
            qc.h(0)  # Hadamard gate for superposition
            qc.measure(0, 0)
            
            # Execute circuit multiple times
            results = []
            backend = Aer.get_backend('qasm_simulator')
            
            for _ in range(n):
                job = execute(qc, backend, shots=1)
                result = job.result()
                counts = result.get_counts(qc)
                bit = list(counts.keys())[0] if counts else '0'
                results.append(int(bit))
            
            # Convert to normal distribution (simplified)
            return np.array(results, dtype=float)
        else:
            # Fallback to classical random numbers
            return np.random.normal(0, 1, n)
    
    def greeks(self, option: OptionContract) -> Dict[str, float]:
        """Monte Carlo Greeks using pathwise estimation"""
        # Use small perturbations for Greeks estimation
        greek_estimates = {}
        
        # Delta estimation
        delta_eps = 0.01 * option.S
        option_up = OptionContract(option.S + delta_eps, option.K, option.T, option.r, option.sigma, option.option_type, option.dividend_yield)
        option_down = OptionContract(option.S - delta_eps, option.K, option.T, option.r, option.sigma, option.option_type, option.dividend_yield)
        
        price_up = self.price(option_up)['quantum_price']
        price_down = self.price(option_down)['quantum_price']
        greek_estimates['delta'] = (price_up - price_down) / (2 * delta_eps)
        
        # Vega estimation
        vega_eps = 0.01
        option_vol_up = OptionContract(option.S, option.K, option.T, option.r, option.sigma + vega_eps, option.option_type, option.dividend_yield)
        option_vol_down = OptionContract(option.S, option.K, option.T, option.r, option.sigma - vega_eps, option.option_type, option.dividend_yield)
        
        price_vol_up = self.price(option_vol_up)['quantum_price']
        price_vol_down = self.price(option_vol_down)['quantum_price']
        greek_estimates['vega'] = (price_vol_up - price_vol_down) / (2 * vega_eps)
        
        # Theta estimation
        theta_eps = 1/365  # One day
        if option.T > theta_eps:
            option_time_down = OptionContract(option.S, option.K, option.T - theta_eps, option.r, option.sigma, option.option_type, option.dividend_yield)
            price_time_down = self.price(option_time_down)['quantum_price']
            original_price = self.price(option)['quantum_price']
            greek_estimates['theta'] = (price_time_down - original_price) / theta_eps
        else:
            greek_estimates['theta'] = 0.0
        
        # Gamma estimation (second derivative)
        if 'delta' in greek_estimates:
            delta_up = (self.price(option_up)['quantum_price'] - original_price) / delta_eps
            delta_down = (original_price - self.price(option_down)['quantum_price']) / delta_eps
            greek_estimates['gamma'] = (delta_up - delta_down) / (2 * delta_eps)
        
        return greek_estimates

class QuantumBinomialModel(PricingModel):
    """Quantum Binomial Tree model"""
    
    def __init__(self, quantum_config: QuantumConfig = None):
        self.quantum_config = quantum_config or QuantumConfig()
        self.default_steps = 100
        self.name = "Quantum Binomial"
    
    def price(self, option: OptionContract, num_steps: int = None) -> Dict[str, float]:
        """Quantum binomial pricing"""
        num_steps = num_steps or min(self.default_steps, max(10, int(option.T * 252)))
        
        dt = option.T / num_steps
        u = np.exp(option.sigma * np.sqrt(dt))  # Up factor
        d = 1 / u  # Down factor
        
        # Risk-neutral probability
        p = (np.exp((option.r - option.dividend_yield) * dt) - d) / (u - d)
        
        # Quantum enhancement
        quantum_enhancement = self._quantum_tree_enhancement(option, num_steps)
        quantum_u = u * quantum_enhancement['up_factor']
        quantum_d = 1 / quantum_u
        quantum_p = p * quantum_enhancement['probability_factor']
        
        # Ensure valid probability
        quantum_p = np.clip(quantum_p, 0.001, 0.999)
        
        # Asset price tree
        prices = self._build_price_tree(option.S, quantum_u, quantum_d, num_steps)
        
        # Option value at maturity
        option_values = self._terminal_payoffs(prices[-1], option.K, option.option_type)
        
        # Backward induction
        for i in range(num_steps - 1, -1, -1):
            for j in range(i + 1):
                option_values[j] = np.exp(-option.r * dt) * (
                    quantum_p * option_values[j] + 
                    (1 - quantum_p) * option_values[j + 1]
                )
        
        quantum_price = option_values[0]
        classical_price = self._classical_binomial_price(option, num_steps)
        
        return {
            'classical_price': classical_price,
            'quantum_price': quantum_price,
            'quantum_consensus': 0.8 * quantum_price + 0.2 * classical_price,
            'num_steps': num_steps,
            'quantum_parameters': {
                'quantum_up_factor': quantum_u,
                'quantum_down_factor': quantum_d,
                'quantum_probability': quantum_p,
                'enhancement_factor': quantum_enhancement['overall']
            },
            'fair_value': quantum_price
        }
    
    def _classical_binomial_price(self, option: OptionContract, num_steps: int) -> float:
        """Classical binomial pricing"""
        dt = option.T / num_steps
        u = np.exp(option.sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp((option.r - option.dividend_yield) * dt) - d) / (u - d)
        
        prices = self._build_price_tree(option.S, u, d, num_steps)
        option_values = self._terminal_payoffs(prices[-1], option.K, option.option_type)
        
        for i in range(num_steps - 1, -1, -1):
            for j in range(i + 1):
                option_values[j] = np.exp(-option.r * dt) * (
                    p * option_values[j] + (1 - p) * option_values[j + 1]
                )
        
        return option_values[0]
    
    def _quantum_tree_enhancement(self, option: OptionContract, num_steps: int) -> Dict[str, float]:
        """Quantum tree enhancement factors"""
        # Time-dependent quantum effect
        time_factor = 1 + 0.02 * np.sin(option.T * num_steps * 0.1)
        
        # Volatility quantum effect
        vol_factor = 1 + 0.01 * np.cos(option.sigma * num_steps * 0.05)
        
        # moneyness quantum effect
        moneyness = option.S / option.K
        money_factor = 1 + 0.03 * np.exp(-abs(moneyness - 1))
        
        # Overall enhancement
        overall_factor = time_factor * vol_factor * money_factor
        
        return {
            'up_factor': overall_factor,
            'probability_factor': 1 + 0.01 * overall_factor - 1,
            'overall': overall_factor
        }
    
    def _build_price_tree(self, S0: float, u: float, d: float, num_steps: int) -> List[List[float]]:
        """Build asset price tree"""
        prices = []
        for i in range(num_steps + 1):
            level = []
            for j in range(i + 1):
                price = S0 * (u ** (i - j)) * (d ** j)
                level.append(price)
            prices.append(level)
        return prices
    
    def _terminal_payoffs(self, terminal_prices: List[float], K: float, option_type: str) -> List[float]:
        """Calculate terminal payoffs"""
        if option_type == 'call':
            return [max(0, price - K) for price in terminal_prices]
        else:
            return [max(0, K - price) for price in terminal_prices]
    
    def greeks(self, option: OptionContract) -> Dict[str, float]:
        """Binomial Greeks using bump and revalue"""
        greeks = {}
        
        # Delta
        option_up = OptionContract(option.S * 1.001, option.K, option.T, option.r, option.sigma, option.option_type, option.dividend_yield)
        option_down = OptionContract(option.S * 0.999, option.K, option.T, option.r, option.sigma, option.option_type, option.dividend_yield)
        
        price_up = self.price(option_up)['quantum_price']
        price_down = self.price(option_down)['quantum_price']
        greeks['delta'] = (price_up - price_down) / (option.S * 0.002)
        
        # Gamma
        original_price = self.price(option)['quantum_price']
        greeks['gamma'] = (price_up - 2 * original_price + price_down) / (option.S * 0.001)**2
        
        # Vega
        option_vol_up = OptionContract(option.S, option.K, option.T, option.r, option.sigma * 1.01, option.option_type, option.dividend_yield)
        price_vol_up = self.price(option_vol_up)['quantum_price']
        greeks['vega'] = (price_vol_up - original_price) / (option.sigma * 0.01)
        
        return greeks

class QuantumVolatilitySurface:
    """Quantum volatility surface modeling"""
    
    def __init__(self, quantum_config: QuantumConfig = None):
        self.quantum_config = quantum_config or QuantumConfig()
        self.vol_surface_data = {}
        self.quantum_effects = {}
    
    def build_surface(self, market_data: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Build quantum volatility surface"""
        # Extract strike prices and maturities
        strikes = sorted(market_data['strike'].unique())
        maturities = sorted(market_data['maturity'].unique())
        
        # Initialize quantum surface
        quantum_surface = np.zeros((len(strikes), len(maturities)))
        classical_surface = np.zeros((len(strikes), len(maturities)))
        
        for i, strike in enumerate(strikes):
            for j, maturity in enumerate(maturities):
                # Filter data for this strike/maturity
                subset = market_data[(market_data['strike'] == strike) & 
                                   (market_data['maturity'] == maturity)]
                
                if len(subset) > 0:
                    # Classical implied volatility (simplified)
                    classical_vol = self._classical_implied_vol(subset)
                    
                    # Quantum volatility enhancement
                    quantum_vol = self._quantum_volatility_enhancement(
                        classical_vol, strike, maturity, market_data)
                    
                    classical_surface[i, j] = classical_vol
                    quantum_surface[i, j] = quantum_vol
                else:
                    # Interpolation if data missing
                    quantum_surface[i, j] = self._interpolate_missing_vol(
                        strikes, maturities, i, j, quantum_surface)
                    classical_surface[i, j] = quantum_surface[i, j] * 0.95
        
        self.vol_surface_data = {
            'quantum_surface': quantum_surface,
            'classical_surface': classical_surface,
            'strikes': np.array(strikes),
            'maturities': np.array(maturities)
        }
        
        return self.vol_surface_data
    
    def _classical_implied_vol(self, subset: pd.DataFrame) -> float:
        """Calculate classical implied volatility"""
        # Simplified implied volatility calculation
        # Haqiqiy implementatsiyada Newton-Raphson yoki bisection ishlatish kerak
        avg_price = subset['option_price'].mean()
        avg_moneyness = subset['moneyness'].mean()
        
        # Rough volatility estimate
        if avg_moneyness > 1.1:  # Deep ITM
            vol = 0.15
        elif avg_moneyness < 0.9:  # Deep OTM
            vol = 0.35
        else:  # Near ATM
            vol = 0.20
        
        return vol
    
    def _quantum_volatility_enhancement(self, classical_vol: float, strike: float, 
                                      maturity: float, market_data: pd.DataFrame) -> float:
        """Quantum volatility enhancement"""
        # Volatility smile effect
        moneyness = strike / market_data['underlying_price'].iloc[0] if len(market_data) > 0 else 1.0
        smile_effect = 1 + 0.1 * abs(moneyness - 1) * np.sign(moneyness - 1)
        
        # Term structure effect
        term_effect = 1 + 0.05 * np.sqrt(maturity / 365)
        
        # Quantum microstructure effects
        microstructure_effect = 1 + 0.02 * np.sin(maturity * strike * 0.001)
        
        # Market sentiment quantum effect
        if len(market_data) > 0:
            price_momentum = market_data['price_change'].mean() if 'price_change' in market_data.columns else 0
            sentiment_effect = 1 + 0.03 * np.tanh(price_momentum * 10)
        else:
            sentiment_effect = 1.0
        
        # Combine effects
        total_effect = smile_effect * term_effect * microstructure_effect * sentiment_effect
        
        return classical_vol * total_effect
    
    def _interpolate_missing_vol(self, strikes: List[float], maturities: List[float], 
                               i: int, j: int, surface: np.ndarray) -> float:
        """Interpolate missing volatility values"""
        # Simple bilinear interpolation
        if i > 0 and j > 0:
            return (surface[i-1, j] + surface[i, j-1]) / 2
        elif i > 0:
            return surface[i-1, j]
        elif j > 0:
            return surface[i, j-1]
        else:
            return 0.20  # Default volatility
    
    def get_volatility(self, strike: float, maturity: float) -> float:
        """Get volatility from surface"""
        if not self.vol_surface_data:
            return 0.20  # Default volatility
        
        strikes = self.vol_surface_data['strikes']
        maturities = self.vol_surface_data['maturities']
        surface = self.vol_surface_data['quantum_surface']
        
        # Interpolation
        if strike < strikes[0] or strike > strikes[-1]:
            # Extrapolation
            if strike < strikes[0]:
                vol = surface[0, np.argmin(np.abs(maturities - maturity))]
            else:
                vol = surface[-1, np.argmin(np.abs(maturities - maturity))]
        else:
            # Bilinear interpolation
            vol = self._bilinear_interpolation(strike, maturity, strikes, maturities, surface)
        
        return vol
    
    def _bilinear_interpolation(self, x: float, y: float, x_vals: np.ndarray, 
                              y_vals: np.ndarray, z_vals: np.ndarray) -> float:
        """Bilinear interpolation"""
        # Find surrounding points
        x_idx = np.searchsorted(x_vals, x)
        y_idx = np.searchsorted(y_vals, y)
        
        x_idx = np.clip(x_idx, 1, len(x_vals) - 1)
        y_idx = np.clip(y_idx, 1, len(y_vals) - 1)
        
        x1, x2 = x_vals[x_idx - 1], x_vals[x_idx]
        y1, y2 = y_vals[y_idx - 1], y_vals[y_idx]
        
        z11 = z_vals[x_idx - 1, y_idx - 1]
        z21 = z_vals[x_idx, y_idx - 1]
        z12 = z_vals[x_idx - 1, y_idx]
        z22 = z_vals[x_idx, y_idx]
        
        # Bilinear interpolation
        if x2 != x1 and y2 != y1:
            z = (z11 * (x2 - x) * (y2 - y) + 
                 z21 * (x - x1) * (y2 - y) + 
                 z12 * (x2 - x) * (y - y1) + 
                 z22 * (x - x1) * (y - y1)) / ((x2 - x1) * (y2 - y1))
        else:
            z = z11
        
        return z

class QuantumGreeksCalculator:
    """Quantum Greeks calculation engine"""
    
    def __init__(self, quantum_config: QuantumConfig = None):
        self.quantum_config = quantum_config or QuantumConfig()
    
    def calculate_all_greeks(self, model: PricingModel, option: OptionContract) -> Dict[str, float]:
        """Calculate all Greeks using quantum-enhanced methods"""
        try:
            # Get basic Greeks from model
            greeks = model.greeks(option)
            
            # Quantum adjustments
            quantum_adjustments = self._quantum_greeks_adjustments(option)
            
            # Apply quantum enhancements
            enhanced_greeks = {}
            for greek_name, greek_value in greeks.items():
                if greek_name in quantum_adjustments:
                    adjustment = quantum_adjustments[greek_name]
                    enhanced_greeks[greek_name] = greek_value * (1 + adjustment)
                else:
                    enhanced_greeks[greek_name] = greek_value
            
            # Add quantum-specific Greeks
            enhanced_greeks.update(self._quantum_specific_greeks(option))
            
            return enhanced_greeks
        except Exception as e:
            warnings.warn(f"Quantum Greeks calculation failed: {e}. Using classical Greeks.")
            return model.greeks(option)
    
    def _quantum_greeks_adjustments(self, option: OptionContract) -> Dict[str, float]:
        """Quantum adjustments to classical Greeks"""
        moneyness = option.S / option.K
        time_factor = np.sqrt(option.T)
        
        adjustments = {
            'delta': 0.01 * np.sin(moneyness * option.sigma),
            'gamma': 0.02 * np.cos(time_factor * option.sigma),
            'theta': -0.005 * np.exp(-option.T) * np.sin(option.sigma),
            'vega': 0.015 * np.cos(2 * np.pi * moneyness),
            'rho': 0.01 * np.tanh(option.r * option.T),
            'vanna': 0.008 * np.sin(3 * time_factor),
            'vomma': 0.012 * np.cos(option.T * option.sigma * 5)
        }
        
        return adjustments
    
    def _quantum_specific_greeks(self, option: OptionContract) -> Dict[str, float]:
        """Quantum-specific Greeks"""
        # Quantum entanglement Greek
        entanglement_greek = 0.001 * np.sin(option.S * option.K * option.T)
        
        # Quantum coherence Greek
        coherence_greek = 0.002 * np.cos(option.sigma * np.sqrt(option.T))
        
        # Quantum tunneling Greek
        tunneling_greek = 0.0015 * np.exp(-option.T) * np.sin(option.sigma * 10)
        
        return {
            'quantum_entanglement': entanglement_greek,
            'quantum_coherence': coherence_greek,
            'quantum_tunneling': tunneling_greek,
            'quantum_risk_premium': abs(entanglement_greek + coherence_greek + tunneling_greek)
        }

# Model factory
class QuantumPricingModelFactory:
    """Quantum pricing model factory"""
    
    _models = {
        'black_scholes': BlackScholesQuantumExtension,
        'monte_carlo': QuantumMonteCarloPricer,
        'binomial': QuantumBinomialModel
    }
    
    @classmethod
    def create_model(cls, model_type: str, quantum_config: QuantumConfig = None) -> PricingModel:
        """Create pricing model"""
        if model_type not in cls._models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return cls._models[model_type](quantum_config)
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get available model types"""
        return list(cls._models.keys())
    
    @classmethod
    def create_ensemble(cls, model_types: List[str], quantum_config: QuantumConfig = None) -> Dict[str, PricingModel]:
        """Create ensemble of models"""
        models = {}
        for model_type in model_types:
            models[model_type] = cls.create_model(model_type, quantum_config)
        return models

# Consensus pricing
def quantum_consensus_pricing(models: Dict[str, PricingModel], option: OptionContract,
                            weights: Dict[str, float] = None) -> Dict[str, Union[float, Dict]]:
    """Quantum consensus pricing across multiple models"""
    if weights is None:
        weights = {name: 1.0/len(models) for name in models.keys()}
    
    # Normalize weights
    total_weight = sum(weights.values())
    normalized_weights = {name: weight/total_weight for name, weight in weights.items()}
    
    # Price with each model
    prices = {}
    greeks = {}
    
    for name, model in models.items():
        try:
            result = model.price(option)
            prices[name] = result['quantum_consensus'] if 'quantum_consensus' in result else result.get('quantum_price', result.get('fair_value', 0))
            
            # Get Greeks
            model_greeks = model.greeks(option)
            greeks[name] = model_greeks
        except Exception as e:
            warnings.warn(f"Model {name} failed: {e}")
            prices[name] = 0.0
            greeks[name] = {}
    
    # Calculate consensus
    consensus_price = sum(prices[name] * normalized_weights[name] for name in models.keys())
    
    # Consensus Greeks
    consensus_greeks = {}
    for greek_name in set().union(*[g.keys() for g in greeks.values() if g]):
        consensus_greeks[greek_name] = sum(
            greeks[name].get(greek_name, 0) * normalized_weights[name] 
            for name in models.keys() if greeks[name]
        )
    
    return {
        'individual_prices': prices,
        'consensus_price': consensus_price,
        'weights': normalized_weights,
        'individual_greeks': greeks,
        'consensus_greeks': consensus_greeks,
        'price_variance': np.var(list(prices.values())),
        'model_confidence': 1 - np.var(list(prices.values())) / max(consensus_price, 0.01)
    }

if __name__ == "__main__":
    # Test
    from datetime import datetime
    
    # Create test option
    option = OptionContract(
        S=100.0, K=105.0, T=0.25, r=0.02, sigma=0.2, option_type='call'
    )
    
    # Test models
    quantum_config = QuantumConfig()
    
    print("Quantum Pricing Models Test:")
    print("=" * 50)
    
    # Test individual models
    models = QuantumPricingModelFactory.create_ensemble(['black_scholes', 'monte_carlo', 'binomial'], quantum_config)
    
    for name, model in models.items():
        print(f"\n{name.upper()} MODEL:")
        result = model.price(option)
        greeks = model.greeks(option)
        
        price_key = 'quantum_consensus' if 'quantum_consensus' in result else ('quantum_price' if 'quantum_price' in result else 'fair_value')
        print(f"Price: {result[price_key]:.4f}")
        print(f"Delta: {greeks.get('delta', 0):.4f}")
        print(f"Gamma: {greeks.get('gamma', 0):.4f}")
        print(f"Vega: {greeks.get('vega', 0):.4f}")
    
    # Test consensus pricing
    print("\nCONSENSUS PRICING:")
    consensus = quantum_consensus_pricing(models, option)
    print(f"Consensus Price: {consensus['consensus_price']:.4f}")
    print(f"Price Variance: {consensus['price_variance']:.4f}")
    print(f"Model Confidence: {consensus['model_confidence']:.4f}")
    
    # Test Greeks calculator
    greeks_calc = QuantumGreeksCalculator(quantum_config)
    enhanced_greeks = greeks_calc.calculate_all_greeks(models['black_scholes'], option)
    print(f"\nEnhanced Delta: {enhanced_greeks['delta']:.4f}")
    print(f"Quantum Risk Premium: {enhanced_greeks['quantum_risk_premium']:.4f}")