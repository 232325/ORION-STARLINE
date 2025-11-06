"""
Quantum Portfolio Optimization for Precious Metals
Advanced quantum algorithms for metal trading with superposition strategies
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math
from scipy.optimize import minimize
from scipy.stats import norm
import cvxpy as cp
import logging

class MetalType(Enum):
    GOLD = "XAU"
    SILVER = "XAG" 
    PLATINUM = "XPT"
    PALLADIUM = "XPD"

@dataclass
class MetalData:
    """Metal price and volatility data"""
    symbol: MetalType
    current_price: float
    volatility: float
    expected_return: float
    correlation: Dict[MetalType, float]
    market_cap: float

@dataclass
class QuantumPosition:
    """Quantum superposition position"""
    metal: MetalType
    amplitude: complex  # Quantum amplitude
    probability: float  # |amplitude|^2
    classical_weight: float
    quantum_coherent: bool

class QuantumPortfolioOptimizer:
    """
    Quantum Portfolio Optimizer for precious metals
    Uses quantum superposition and quantum annealing concepts
    """
    
    def __init__(self, metal_data: List[MetalData]):
        self.metal_data = {m.symbol: m for m in metal_data}
        self.metals = list(self.metal_data.keys())
        self.n_metals = len(self.metals)
        self.quantum_states = {}
        
        # Initialize quantum parameters
        self.quantum_depth = 10
        self.coherence_threshold = 0.85
        self.entanglement_strength = 0.1
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def initialize_quantum_states(self) -> Dict[MetalType, QuantumPosition]:
        """Initialize quantum superposition states for all metals"""
        quantum_positions = {}
        
        for metal in self.metals:
            data = self.metal_data[metal]
            
            # Initialize quantum amplitude based on expected return and volatility
            expected_return = data.expected_return
            volatility = data.volatility
            
            # Quantum amplitude with phase information
            amplitude_magnitude = math.sqrt(abs(expected_return) / (volatility + 1e-10))
            phase = math.atan2(expected_return, volatility)
            
            amplitude = amplitude_magnitude * complex(math.cos(phase), math.sin(phase))
            probability = abs(amplitude) ** 2
            
            # Classical weight based on market cap and risk
            classical_weight = self._calculate_classical_weight(data)
            
            quantum_positions[metal] = QuantumPosition(
                metal=metal,
                amplitude=amplitude,
                probability=probability,
                classical_weight=classical_weight,
                quantum_coherent=True
            )
            
        self.quantum_states = quantum_positions
        return quantum_positions
    
    def quantum_portfolio_optimization(
        self, 
        risk_aversion: float = 1.0,
        quantum_advantage: bool = True
    ) -> Dict[MetalType, float]:
        """
        Optimize portfolio using quantum algorithms
        
        Args:
            risk_aversion: Risk aversion parameter
            quantum_advantage: Whether to use quantum superposition
            
        Returns:
            Optimal weights for each metal
        """
        self.logger.info("Starting quantum portfolio optimization...")
        
        if quantum_advantage:
            return self._quantum_optimization(risk_aversion)
        else:
            return self._classical_optimization(risk_aversion)
    
    def _quantum_optimization(self, risk_aversion: float) -> Dict[MetalType, float]:
        """Quantum-enhanced portfolio optimization"""
        
        # Step 1: Create quantum superposition of portfolios
        superposition_portfolios = self._create_portfolio_superposition()
        
        # Step 2: Apply quantum interference patterns
        interference_patterns = self._calculate_quantum_interference(superposition_portfolios)
        
        # Step 3: Quantum annealing to find optimal state
        optimal_portfolio = self._quantum_annealing(
            superposition_portfolios, 
            interference_patterns, 
            risk_aversion
        )
        
        # Step 4: Collapse quantum state to classical weights
        classical_weights = self._collapse_to_classical(optimal_portfolio)
        
        self.logger.info(f"Quantum optimization complete. Weights: {classical_weights}")
        return classical_weights
    
    def _classical_optimization(self, risk_aversion: float) -> Dict[MetalType, float]:
        """Classical portfolio optimization as baseline"""
        returns = np.array([self.metal_data[m].expected_return for m in self.metals])
        cov_matrix = self._build_covariance_matrix()
        
        # Mean-variance optimization
        weights = cp.Variable(self.n_metals)
        
        expected_return = returns.T @ weights
        risk = cp.quad_form(weights, cov_matrix)
        
        # Objective: maximize expected return - risk_aversion * risk
        objective = cp.Maximize(expected_return - risk_aversion * risk)
        
        constraints = [
            cp.sum(weights) == 1,  # Budget constraint
            weights >= 0,          # No short selling
            weights <= 1           # Maximum allocation
        ]
        
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        if problem.status == cp.OPTIMAL:
            weights_dict = {
                metal: float(weights.value[i]) 
                for i, metal in enumerate(self.metals)
            }
            self.logger.info(f"Classical optimization complete. Status: {problem.status}")
            return weights_dict
        else:
            raise RuntimeError(f"Optimization failed: {problem.status}")
    
    def _create_portfolio_superposition(self) -> List[Dict[MetalType, float]]:
        """Create quantum superposition of different portfolio strategies"""
        
        strategies = []
        
        # Strategy 1: Equal weight
        equal_weights = {metal: 1.0/self.n_metals for metal in self.metals}
        strategies.append(equal_weights)
        
        # Strategy 2: Risk parity
        risk_parity_weights = self._risk_parity_weights()
        strategies.append(risk_parity_weights)
        
        # Strategy 3: Maximum Sharpe ratio
        max_sharpe_weights = self._max_sharpe_weights()
        strategies.append(max_sharpe_weights)
        
        # Strategy 4: Minimum variance
        min_var_weights = self._min_variance_weights()
        strategies.append(min_var_weights)
        
        # Strategy 5: Momentum-based
        momentum_weights = self._momentum_weights()
        strategies.append(momentum_weights)
        
        # Add quantum variations of each strategy
        quantum_strategies = []
        for base_strategy in strategies:
            for _ in range(self.quantum_depth):
                # Apply quantum noise
                quantum_strategy = self._apply_quantum_noise(base_strategy)
                quantum_strategies.append(quantum_strategy)
        
        return quantum_strategies
    
    def _calculate_quantum_interference(
        self, 
        portfolios: List[Dict[MetalType, float]]
    ) -> np.ndarray:
        """Calculate quantum interference patterns between portfolios"""
        
        n_portfolios = len(portfolios)
        interference_matrix = np.zeros((n_portfolios, n_portfolios), dtype=complex)
        
        for i in range(n_portfolios):
            for j in range(i, n_portfolios):
                if i == j:
                    interference_matrix[i, j] = 1.0  # Self-interference
                else:
                    # Calculate quantum coherence between portfolios
                    coherence = self._calculate_portfolio_coherence(
                        portfolios[i], 
                        portfolios[j]
                    )
                    interference_matrix[i, j] = coherence
                    interference_matrix[j, i] = np.conj(coherence)
        
        return interference_matrix
    
    def _quantum_annealing(
        self,
        portfolios: List[Dict[MetalType, float]],
        interference: np.ndarray,
        risk_aversion: float
    ) -> Dict[MetalType, float]:
        """Quantum annealing to find optimal portfolio state"""
        
        n_portfolios = len(portfolios)
        
        # Initialize quantum amplitudes
        amplitudes = np.ones(n_portfolios, dtype=complex) / math.sqrt(n_portfolios)
        
        # Quantum annealing schedule
        annealing_steps = 100
        initial_temp = 10.0
        final_temp = 0.01
        
        for step in range(annealing_steps):
            temp = initial_temp * (final_temp / initial_temp) ** (step / annealing_steps)
            
            # Calculate classical energy for each portfolio
            energies = np.array([
                self._calculate_portfolio_energy(portfolio, risk_aversion)
                for portfolio in portfolios
            ])
            
            # Quantum tunneling probability
            quantum_factor = 1.0 / (1.0 + math.exp(energies / temp))
            
            # Update amplitudes using quantum evolution
            for i in range(n_portfolios):
                new_amplitude = amplitudes[i] * quantum_factor[i]
                # Apply quantum interference
                interference_sum = sum(
                    amplitudes[j] * interference[i, j] 
                    for j in range(n_portfolios)
                )
                amplitudes[i] = (new_amplitude + 0.1 * interference_sum) / math.sqrt(n_portfolios)
            
            # Renormalize amplitudes
            amplitudes /= np.linalg.norm(amplitudes)
        
        # Select portfolio with highest probability
        probabilities = np.abs(amplitudes) ** 2
        optimal_idx = np.argmax(probabilities)
        
        return portfolios[optimal_idx]
    
    def _calculate_portfolio_energy(
        self, 
        portfolio: Dict[MetalType, float], 
        risk_aversion: float
    ) -> float:
        """Calculate energy (negative utility) of portfolio"""
        
        weights = np.array([portfolio[metal] for metal in self.metals])
        returns = np.array([self.metal_data[m].expected_return for m in self.metals])
        cov_matrix = self._build_covariance_matrix()
        
        expected_return = np.dot(weights, returns)
        variance = np.dot(weights, np.dot(cov_matrix, weights))
        
        # Mean-variance utility (negative for energy)
        utility = expected_return - 0.5 * risk_aversion * variance
        return -utility  # Energy is negative utility
    
    def _collapse_to_classical(self, quantum_portfolio: Dict[MetalType, float]) -> Dict[MetalType, float]:
        """Collapse quantum superposition to classical portfolio weights"""
        
        # Apply quantum coherence threshold
        coherent_metals = [
            metal for metal, pos in self.quantum_states.items() 
            if pos.quantum_coherent
        ]
        
        # Normalize weights and apply constraints
        total_weight = sum(quantum_portfolio.values())
        if total_weight > 0:
            classical_weights = {
                metal: weight / total_weight 
                for metal, weight in quantum_portfolio.items()
            }
        else:
            classical_weights = {metal: 1.0/self.n_metals for metal in self.metals}
        
        # Apply quantum-enhanced constraints
        min_weight = 0.01  # Minimum 1% allocation
        max_weight = 0.60  # Maximum 60% allocation
        
        for metal in classical_weights:
            classical_weights[metal] = max(min_weight, min(max_weight, classical_weights[metal]))
        
        # Renormalize to sum to 1
        total = sum(classical_weights.values())
        classical_weights = {k: v/total for k, v in classical_weights.items()}
        
        return classical_weights
    
    def quantum_volatility_modeling(self, lookback_period: int = 30) -> Dict[MetalType, float]:
        """
        Model volatility using quantum superposition of volatility regimes
        
        Returns:
            Quantum-adjusted volatilities for each metal
        """
        
        quantum_volatilities = {}
        
        for metal in self.metals:
            data = self.metal_data[metal]
            
            # Classical volatility
            classical_vol = data.volatility
            
            # Quantum volatility states (low, medium, high volatility regimes)
            vol_regimes = [
                classical_vol * 0.7,  # Low volatility
                classical_vol,        # Current volatility
                classical_vol * 1.4   # High volatility
            ]
            
            # Quantum amplitudes for each regime
            amplitudes = [
                complex(math.sqrt(0.2), 0),      # 20% probability low vol
                complex(math.sqrt(0.6), 0),      # 60% probability current vol
                complex(math.sqrt(0.2), 0)       # 20% probability high vol
            ]
            
            # Quantum superposition of volatilities
            quantum_vol = sum(amp * vol for amp, vol in zip(amplitudes, vol_regimes))
            quantum_volatilities[metal] = abs(quantum_vol)
        
        return quantum_volatilities
    
    def quantum_correlation_analysis(self) -> Dict[Tuple[MetalType, MetalType], float]:
        """
        Analyze correlations using quantum entanglement concepts
        
        Returns:
            Quantum-adjusted correlation matrix
        """
        
        correlations = {}
        
        for i, metal1 in enumerate(self.metals):
            for j, metal2 in enumerate(self.metals):
                if i <= j:  # Only calculate upper triangle
                    # Classical correlation
                    classical_corr = self.metal_data[metal1].correlation.get(metal2, 0.0)
                    
                    # Quantum correlation with entanglement
                    if i == j:
                        quantum_corr = 1.0
                    else:
                        # Apply quantum entanglement adjustment
                        entanglement_factor = 1.0 + self.entanglement_strength * math.sin(
                            i * j * math.pi / self.n_metals
                        )
                        quantum_corr = classical_corr * entanglement_factor
                    
                    # Ensure correlation is within [-1, 1]
                    quantum_corr = max(-1.0, min(1.0, quantum_corr))
                    
                    correlations[(metal1, metal2)] = quantum_corr
                    if i != j:
                        correlations[(metal2, metal1)] = quantum_corr
        
        return correlations
    
    def superposition_allocation_strategy(
        self, 
        risk_budget: float = 0.15
    ) -> Dict[MetalType, Dict[str, float]]:
        """
        Create superposition-based asset allocation strategy
        
        Args:
            risk_budget: Total risk budget (annual volatility target)
            
        Returns:
            Multi-state allocation strategy
        """
        
        quantum_states = {}
        
        for metal in self.metals:
            data = self.metal_data[metal]
            
            # Define quantum states for different market scenarios
            states = {
                "bull_market": {
                    "probability": 0.3,
                    "allocation": min(1.0, data.expected_return * 10)  # Scale by expected return
                },
                "bear_market": {
                    "probability": 0.2,
                    "allocation": 0.1  # Conservative allocation
                },
                "volatile_market": {
                    "probability": 0.3,
                    "allocation": data.volatility / 10  # Scale by volatility
                },
                "stable_market": {
                    "probability": 0.2,
                    "allocation": 0.5  # Balanced allocation
                }
            }
            
            # Normalize allocations
            total_allocation = sum(state["allocation"] for state in states.values())
            if total_allocation > 0:
                for state in states.values():
                    state["allocation"] /= total_allocation
            
            quantum_states[metal] = states
        
        return quantum_states
    
    # Helper methods
    def _calculate_classical_weight(self, data: MetalData) -> float:
        """Calculate classical weight based on market cap and risk metrics"""
        market_factor = math.log(data.market_cap + 1) / 10  # Log-scale market cap factor
        risk_factor = 1.0 / (1.0 + data.volatility)  # Inverse volatility factor
        return (market_factor + risk_factor) / 2
    
    def _build_covariance_matrix(self) -> np.ndarray:
        """Build covariance matrix from correlations"""
        cov_matrix = np.zeros((self.n_metals, self.n_metals))
        
        for i, metal1 in enumerate(self.metals):
            for j, metal2 in enumerate(self.metals):
                if i == j:
                    cov_matrix[i, j] = self.metal_data[metal1].volatility ** 2
                else:
                    corr = self.metal_data[metal1].correlation.get(metal2, 0.0)
                    vol1 = self.metal_data[metal1].volatility
                    vol2 = self.metal_data[metal2].volatility
                    cov_matrix[i, j] = corr * vol1 * vol2
        
        return cov_matrix
    
    def _calculate_portfolio_coherence(
        self, 
        portfolio1: Dict[MetalType, float], 
        portfolio2: Dict[MetalType, float]
    ) -> complex:
        """Calculate quantum coherence between two portfolios"""
        
        # Quantum coherence measure based on weight overlap
        overlap = sum(min(w1, w2) for w1, w2 in zip(
            portfolio1.values(), portfolio2.values()
        ))
        
        # Convert to complex amplitude
        coherence_magnitude = math.sqrt(overlap)
        phase = math.pi * overlap  # Phase based on overlap
        
        return coherence_magnitude * complex(math.cos(phase), math.sin(phase))
    
    def _apply_quantum_noise(self, base_portfolio: Dict[MetalType, float]) -> Dict[MetalType, float]:
        """Apply quantum noise to portfolio weights"""
        
        quantum_portfolio = {}
        noise_level = 0.05  # 5% noise
        
        for metal, weight in base_portfolio.items():
            # Add quantum noise
            noise = np.random.normal(0, noise_level * weight)
            quantum_portfolio[metal] = max(0, weight + noise)
        
        # Renormalize
        total = sum(quantum_portfolio.values())
        if total > 0:
            quantum_portfolio = {k: v/total for k, v in quantum_portfolio.items()}
        
        return quantum_portfolio
    
    def _risk_parity_weights(self) -> Dict[MetalType, float]:
        """Calculate risk parity weights"""
        volatilities = [self.metal_data[m].volatility for m in self.metals]
        inv_vol = [1/v if v > 0 else 0 for v in volatilities]
        total_inv = sum(inv_vol)
        
        return {
            metal: inv_vol[i] / total_inv 
            for i, metal in enumerate(self.metals)
        }
    
    def _max_sharpe_weights(self) -> Dict[MetalType, float]:
        """Calculate maximum Sharpe ratio weights"""
        # Simplified: use expected return / volatility ratio
        ratios = [self.metal_data[m].expected_return / self.metal_data[m].volatility 
                 for m in self.metals]
        total_ratio = sum(max(r, 0) for r in ratios)  # Only positive ratios
        
        if total_ratio == 0:
            return {metal: 1.0/self.n_metals for metal in self.metals}
        
        return {
            metal: max(ratios[i], 0) / total_ratio 
            for i, metal in enumerate(self.metals)
        }
    
    def _min_variance_weights(self) -> Dict[MetalType, float]:
        """Calculate minimum variance weights"""
        volatilities = [self.metal_data[m].volatility ** 2 for m in self.metals]
        total_var = sum(volatilities)
        
        return {
            metal: volatilities[i] / total_var 
            for i, metal in enumerate(self.metals)
        }
    
    def _momentum_weights(self) -> Dict[MetalType, float]:
        """Calculate momentum-based weights"""
        returns = [self.metal_data[m].expected_return for m in self.metals]
        total_return = sum(max(r, 0) for r in returns)
        
        if total_return == 0:
            return {metal: 1.0/self.n_metals for metal in self.metals}
        
        return {
            metal: max(returns[i], 0) / total_return 
            for i, metal in enumerate(self.metals)
        }
    
    def get_quantum_advantage_metrics(self) -> Dict[str, float]:
        """Calculate metrics showing quantum advantage over classical methods"""
        
        classical_weights = self._classical_optimization(1.0)
        quantum_weights = self._quantum_optimization(1.0)
        
        # Calculate portfolio metrics
        classical_return = self._calculate_portfolio_return(classical_weights)
        quantum_return = self._calculate_portfolio_return(quantum_weights)
        
        classical_vol = self._calculate_portfolio_volatility(classical_weights)
        quantum_vol = self._calculate_portfolio_volatility(quantum_weights)
        
        classical_sharpe = classical_return / classical_vol if classical_vol > 0 else 0
        quantum_sharpe = quantum_return / quantum_vol if quantum_vol > 0 else 0
        
        return {
            "return_improvement": (quantum_return - classical_return) / classical_return if classical_return != 0 else 0,
            "volatility_reduction": (classical_vol - quantum_vol) / classical_vol if classical_vol != 0 else 0,
            "sharpe_improvement": (quantum_sharpe - classical_sharpe) / classical_sharpe if classical_sharpe != 0 else 0,
            "quantum_coherence": self._calculate_average_coherence()
        }
    
    def _calculate_portfolio_return(self, weights: Dict[MetalType, float]) -> float:
        """Calculate expected portfolio return"""
        return sum(
            weights[metal] * self.metal_data[metal].expected_return
            for metal in self.metals
        )
    
    def _calculate_portfolio_volatility(self, weights: Dict[MetalType, float]) -> float:
        """Calculate portfolio volatility"""
        weights_array = np.array([weights[metal] for metal in self.metals])
        cov_matrix = self._build_covariance_matrix()
        return math.sqrt(np.dot(weights_array, np.dot(cov_matrix, weights_array)))
    
    def _calculate_average_coherence(self) -> float:
        """Calculate average quantum coherence across all metals"""
        if not self.quantum_states:
            return 0.0
        
        coherences = [
            pos.probability for pos in self.quantum_states.values()
            if pos.quantum_coherent
        ]
        
        return sum(coherences) / len(coherences) if coherences else 0.0


# Example usage and testing
if __name__ == "__main__":
    # Sample metal data
    metal_data = [
        MetalData(
            symbol=MetalType.GOLD,
            current_price=2000.0,
            volatility=0.15,
            expected_return=0.05,
            correlation={
                MetalType.SILVER: 0.8,
                MetalType.PLATINUM: 0.7,
                MetalType.PALLADIUM: 0.6
            },
            market_cap=1000000
        ),
        MetalData(
            symbol=MetalType.SILVER,
            current_price=25.0,
            volatility=0.30,
            expected_return=0.08,
            correlation={
                MetalType.GOLD: 0.8,
                MetalType.PLATINUM: 0.75,
                MetalType.PALLADIUM: 0.65
            },
            market_cap=500000
        ),
        MetalData(
            symbol=MetalType.PLATINUM,
            current_price=1000.0,
            volatility=0.25,
            expected_return=0.06,
            correlation={
                MetalType.GOLD: 0.7,
                MetalType.SILVER: 0.75,
                MetalType.PALLADIUM: 0.8
            },
            market_cap=200000
        ),
        MetalData(
            symbol=MetalType.PALLADIUM,
            current_price=2000.0,
            volatility=0.40,
            expected_return=0.10,
            correlation={
                MetalType.GOLD: 0.6,
                MetalType.SILVER: 0.65,
                MetalType.PLATINUM: 0.8
            },
            market_cap=100000
        )
    ]
    
    # Initialize quantum optimizer
    optimizer = QuantumPortfolioOptimizer(metal_data)
    optimizer.initialize_quantum_states()
    
    # Run quantum optimization
    quantum_weights = optimizer.quantum_portfolio_optimization(
        risk_aversion=1.0,
        quantum_advantage=True
    )
    
    print("Quantum Portfolio Weights:")
    for metal, weight in quantum_weights.items():
        print(f"{metal.value}: {weight:.4f}")
    
    # Calculate quantum advantage metrics
    advantage_metrics = optimizer.get_quantum_advantage_metrics()
    print("\nQuantum Advantage Metrics:")
    for metric, value in advantage_metrics.items():
        print(f"{metric}: {value:.4f}")
    
    # Run volatility modeling
    quantum_volatilities = optimizer.quantum_volatility_modeling()
    print("\nQuantum Volatilities:")
    for metal, vol in quantum_volatilities.items():
        print(f"{metal.value}: {vol:.4f}")
    
    # Run correlation analysis
    quantum_correlations = optimizer.quantum_correlation_analysis()
    print("\nQuantum Correlations:")
    for (metal1, metal2), corr in quantum_correlations.items():
        if metal1 != metal2:
            print(f"{metal1.value}-{metal2.value}: {corr:.4f}")