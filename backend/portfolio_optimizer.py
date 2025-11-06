"""
Multi-Asset Portfolio Optimizer
==============================

Bu modul turli xil optimizatsiya usullarini qo'llab-quvvatlaydigan
ko'p aktivli portfolio optimizatorini o'z ichiga oladi.

Funksiyalar:
- Modern Portfolio Theory (Markowitz)
- Black-Litterman model
- Risk parity optimization
- Maximum Sharpe ratio
- Minimum variance portfolio
- Value at Risk (VaR)
- Conditional VaR (CVaR)
- Quantum-inspired optimization
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize, differential_evolution
from scipy.linalg import inv, cholesky
from sklearn.decomposition import PCA
from sklearn.covariance import LedoitWolf
import warnings
warnings.filterwarnings('ignore')

class QuantumInspiredOptimizer:
    """Quantum-inspired optimization algorithms for portfolio optimization."""
    
    def __init__(self, n_qubits=20, population_size=50, iterations=100):
        self.n_qubits = n_qubits
        self.population_size = population_size
        self.iterations = iterations
        self.quantum_states = []
    
    def quantum_state_initialization(self, n_assets):
        """Quantum states initialization."""
        # Create complex quantum states
        real_parts = np.random.randn(self.population_size, n_assets)
        imag_parts = np.random.randn(self.population_size, n_assets)
        self.quantum_states = real_parts + 1j * imag_parts
        
        # Normalize quantum states
        for i in range(self.population_size):
            norm = np.linalg.norm(self.quantum_states[i])
            if norm > 0:
                self.quantum_states[i] /= norm
    
    def quantum_measurement(self, weights):
        """Quantum measurement to get classical weights."""
        probabilities = np.abs(weights) ** 2
        probabilities = probabilities / np.sum(probabilities)
        return probabilities
    
    def optimize_portfolio(self, mean_returns, cov_matrix, constraints=None):
        """Quantum-inspired portfolio optimization."""
        n_assets = len(mean_returns)
        
        if constraints is None:
            constraints = self.default_constraints(n_assets)
        
        # Initialize quantum states
        self.quantum_state_initialization(n_assets)
        
        best_portfolio = None
        best_fitness = float('inf')
        
        for iteration in range(self.iterations):
            for state_idx in range(self.population_size):
                # Convert quantum state to classical weights
                classical_weights = self.quantum_measurement(
                    self.quantum_states[state_idx]
                )
                
                # Apply constraints
                classical_weights = self.apply_constraints(
                    classical_weights, constraints
                )
                
                # Calculate fitness (risk-adjusted return)
                fitness = self.calculate_portfolio_fitness(
                    classical_weights, mean_returns, cov_matrix
                )
                
                # Update best portfolio
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_portfolio = classical_weights.copy()
                
                # Quantum gate operations
                self.quantum_states[state_idx] = self.quantum_gate_operations(
                    self.quantum_states[state_idx], mean_returns, cov_matrix
                )
        
        return best_portfolio
    
    def quantum_gate_operations(self, quantum_state, mean_returns, cov_matrix):
        """Apply quantum gate operations."""
        n_assets = len(quantum_state)
        
        # Hadamard-like rotation
        rotation_angle = 0.1
        for i in range(n_assets):
            if quantum_state[i].real >= 0:
                new_real = quantum_state[i].real * np.cos(rotation_angle) - \
                          quantum_state[i].imag * np.sin(rotation_angle)
                new_imag = quantum_state[i].real * np.sin(rotation_angle) + \
                          quantum_state[i].imag * np.cos(rotation_angle)
                quantum_state[i] = complex(new_real, new_imag)
        
        # Normalize
        norm = np.linalg.norm(quantum_state)
        if norm > 0:
            quantum_state /= norm
        
        return quantum_state
    
    def default_constraints(self, n_assets):
        """Default constraints for portfolio optimization."""
        return {
            'max_weight': 0.4,  # Maximum single position
            'min_weight': 0.0,  # Minimum single position
            'target_return': 0.12,  # Target annual return
            'max_risk': 0.25,  # Maximum risk level
            'sector_limits': {},  # Sector allocation limits
            'geographic_limits': {}  # Geographic allocation limits
        }
    
    def apply_constraints(self, weights, constraints):
        """Apply constraints to portfolio weights."""
        # Maximum weight constraint
        weights = np.maximum(weights, constraints['min_weight'])
        weights = np.minimum(weights, constraints['max_weight'])
        
        # Normalize weights
        if np.sum(weights) > 0:
            weights = weights / np.sum(weights)
        
        return weights
    
    def calculate_portfolio_fitness(self, weights, mean_returns, cov_matrix):
        """Calculate portfolio fitness (risk-adjusted return)."""
        portfolio_return = np.dot(weights, mean_returns)
        portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
        portfolio_std = np.sqrt(portfolio_variance)
        
        # Risk-adjusted return (higher is better, so we minimize negative)
        fitness = -portfolio_return / max(portfolio_std, 1e-8)
        
        return fitness

class ModernPortfolioTheory:
    """Modern Portfolio Theory (Markowitz) optimization."""
    
    def __init__(self, risk_free_rate=0.02):
        self.risk_free_rate = risk_free_rate
    
    def calculate_efficient_frontier(self, mean_returns, cov_matrix, 
                                   num_portfolios=100):
        """Calculate the efficient frontier."""
        n_assets = len(mean_returns)
        
        # Range of expected returns
        min_ret = np.min(mean_returns)
        max_ret = np.max(mean_returns)
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)
        
        efficient_portfolios = []
        
        for target_return in target_returns:
            # Minimize variance for target return
            weights = self.minimize_variance(
                mean_returns, cov_matrix, target_return
            )
            if weights is not None:
                efficient_portfolios.append({
                    'return': target_return,
                    'weights': weights,
                    'variance': np.dot(weights, np.dot(cov_matrix, weights)),
                    'std': np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                })
        
        return efficient_portfolios
    
    def minimize_variance(self, mean_returns, cov_matrix, target_return):
        """Minimize portfolio variance for target return."""
        n_assets = len(mean_returns)
        
        # Constraints: weights sum to 1, portfolio return equals target
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.dot(x, mean_returns) - target_return}
        )
        
        # Bounds: weights between 0 and 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess
        initial_guess = np.ones(n_assets) / n_assets
        
        # Objective function: minimize variance
        objective = lambda x: np.dot(x, np.dot(cov_matrix, x))
        
        try:
            result = minimize(
                objective, initial_guess, method='SLSQP',
                bounds=bounds, constraints=constraints
            )
            if result.success:
                return result.x
        except:
            pass
        
        return None
    
    def optimize_maximum_sharpe(self, mean_returns, cov_matrix):
        """Find the maximum Sharpe ratio portfolio."""
        n_assets = len(mean_returns)
        
        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        
        # Bounds: weights between 0 and 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess
        initial_guess = np.ones(n_assets) / n_assets
        
        # Objective function: minimize negative Sharpe ratio
        objective = lambda x: -self.calculate_sharpe_ratio(
            x, mean_returns, cov_matrix
        )
        
        result = minimize(
            objective, initial_guess, method='SLSQP',
            bounds=bounds, constraints=constraints
        )
        
        if result.success:
            return result.x
        return None
    
    def optimize_minimum_variance(self, mean_returns, cov_matrix):
        """Find the minimum variance portfolio."""
        n_assets = len(mean_returns)
        
        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        
        # Bounds: weights between 0 and 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess
        initial_guess = np.ones(n_assets) / n_assets
        
        # Objective function: minimize variance
        objective = lambda x: np.dot(x, np.dot(cov_matrix, x))
        
        result = minimize(
            objective, initial_guess, method='SLSQP',
            bounds=bounds, constraints=constraints
        )
        
        if result.success:
            return result.x
        return None
    
    def calculate_sharpe_ratio(self, weights, mean_returns, cov_matrix, 
                             risk_free_rate=None):
        """Calculate Sharpe ratio."""
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        portfolio_return = np.dot(weights, mean_returns)
        portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
        portfolio_std = np.sqrt(portfolio_variance)
        
        if portfolio_std == 0:
            return 0
        
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
        return sharpe_ratio

class BlackLittermanModel:
    """Black-Litterman model for portfolio optimization."""
    
    def __init__(self, risk_aversion=3, risk_free_rate=0.02):
        self.risk_aversion = risk_aversion
        self.risk_free_rate = risk_free_rate
    
    def fit(self, market_caps, implied_returns, cov_matrix, 
           views=None, view_confidence=None):
        """Fit the Black-Litterman model."""
        self.market_caps = market_caps
        self.cov_matrix = cov_matrix
        self.n_assets = len(market_caps)
        
        # Market capital weights
        self.market_weights = market_caps / np.sum(market_caps)
        
        # Implied returns (from CAPM)
        self.implied_returns = implied_returns
        
        # Investor views
        self.views = views
        self.view_confidence = view_confidence
        
        # Adjust covariance matrix for estimation error
        self.cov_matrix_adjusted = self.adjust_covariance_matrix()
        
        # Calculate implied equilibrium returns
        self.equilibrium_returns = self.calculate_equilibrium_returns()
        
        # Combine views with equilibrium
        self.returns_with_views = self.combine_views_with_equilibrium()
        
        # Calculate final returns and covariance
        self.final_returns = self.returns_with_views
        self.final_cov_matrix = self.calculate_final_covariance()
        
        return self
    
    def adjust_covariance_matrix(self):
        """Adjust covariance matrix for estimation error."""
        # Use Ledoit-Wolf estimator to reduce noise
        lw = LedoitWolf()
        adjusted_cov = lw.fit(self.cov_matrix).covariance_
        return adjusted_cov
    
    def calculate_equilibrium_returns(self):
        """Calculate equilibrium returns."""
        # Excess returns calculation
        tau = 0.05  # Confidence parameter
        
        try:
            inv_cov = inv(self.cov_matrix_adjusted)
            equilibrium_returns = self.risk_aversion * np.dot(
                self.cov_matrix_adjusted, self.market_weights
            ) + self.risk_free_rate
            return equilibrium_returns
        except:
            # Fallback to simple calculation
            return np.ones(self.n_assets) * 0.10
    
    def combine_views_with_equilibrium(self):
        """Combine investor views with equilibrium returns."""
        if self.views is None:
            return self.equilibrium_returns
        
        # P matrix (views on asset combinations)
        P = np.eye(self.n_assets)  # Identity for simplicity
        
        # Q matrix (view returns)
        Q = self.views
        
        # Omega matrix (view uncertainty)
        omega = np.diag(np.ones(self.n_assets) * 0.01)
        
        tau = 0.05
        
        try:
            # Black-Litterman formula
            M1 = inv(tau * self.cov_matrix_adjusted)
            M2 = np.dot(P.T, inv(omega))
            M3 = np.dot(P, M1)
            
            combined_returns = np.dot(
                inv(M1 + np.dot(M2, P)), 
                np.dot(M1, self.equilibrium_returns) + np.dot(M2, Q)
            )
            
            return combined_returns
        except:
            # Fallback to equilibrium returns
            return self.equilibrium_returns
    
    def calculate_final_covariance(self):
        """Calculate final covariance matrix."""
        tau = 0.05
        
        try:
            # Posterior covariance
            cov_inv = inv(tau * self.cov_matrix_adjusted)
            posterior_cov = inv(cov_inv + np.eye(self.n_assets) * 100)
            return posterior_cov
        except:
            return self.cov_matrix_adjusted

class RiskParityOptimizer:
    """Risk parity portfolio optimization."""
    
    def __init__(self, risk_budget=None):
        self.risk_budget = risk_budget or {i: 1.0 for i in range(20)}  # Default equal risk
    
    def optimize(self, cov_matrix, target_risk=None):
        """Optimize for risk parity."""
        n_assets = cov_matrix.shape[0]
        
        # Default equal risk contribution
        if target_risk is None:
            target_risk = np.ones(n_assets) / n_assets
        
        # Constraints
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        
        # Bounds
        bounds = tuple((0.001, 1) for _ in range(n_assets))
        
        # Initial guess
        initial_guess = np.ones(n_assets) / n_assets
        
        # Objective function: minimize risk contribution deviation
        objective = lambda x: self.risk_parity_objective(x, cov_matrix, target_risk)
        
        result = minimize(
            objective, initial_guess, method='SLSQP',
            bounds=bounds, constraints=constraints
        )
        
        if result.success:
            return result.x
        return initial_guess
    
    def risk_parity_objective(self, weights, cov_matrix, target_risk):
        """Risk parity objective function."""
        portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
        marginal_contrib = np.dot(cov_matrix, weights)
        
        risk_contrib = weights * marginal_contrib / portfolio_variance
        
        # Calculate deviation from target risk
        deviation = np.sum((risk_contrib - target_risk) ** 2)
        return deviation

class RiskMetrics:
    """Calculate various risk metrics."""
    
    def __init__(self, confidence_level=0.95):
        self.confidence_level = confidence_level
    
    def calculate_var(self, returns, method='historical', alpha=None):
        """Calculate Value at Risk (VaR)."""
        if method == 'historical':
            return np.percentile(returns, (1 - self.confidence_level) * 100)
        elif method == 'parametric':
            return self._parametric_var(returns, alpha)
        elif method == 'monte_carlo':
            return self._monte_carlo_var(returns, alpha)
        else:
            raise ValueError("Invalid VaR calculation method")
    
    def _parametric_var(self, returns, alpha=None):
        """Parametric VaR calculation."""
        if alpha is None:
            alpha = returns.std()
        
        z_score = self._z_score()
        mean_return = returns.mean()
        
        return mean_return - z_score * alpha
    
    def _monte_carlo_var(self, returns, alpha=None):
        """Monte Carlo VaR calculation."""
        n_simulations = 10000
        n_observations = len(returns)
        
        if alpha is None:
            alpha = returns.std()
        
        mean_return = returns.mean()
        
        # Generate random returns
        simulated_returns = np.random.normal(
            mean_return, alpha, (n_simulations, n_observations)
        )
        
        # Calculate VaR for each simulation
        var_estimates = []
        for i in range(n_simulations):
            var_estimate = np.percentile(
                simulated_returns[i], (1 - self.confidence_level) * 100
            )
            var_estimates.append(var_estimate)
        
        return np.mean(var_estimates)
    
    def calculate_cvar(self, returns, method='historical', alpha=None):
        """Calculate Conditional Value at Risk (CVaR)."""
        var = self.calculate_var(returns, method, alpha)
        
        if method == 'historical':
            tail_losses = returns[returns <= var]
            if len(tail_losses) > 0:
                return tail_losses.mean()
            else:
                return var
        elif method in ['parametric', 'monte_carlo']:
            # For parametric methods, CVaR is approximate
            return var * 1.5  # Simple approximation
        else:
            return var
    
    def calculate_max_drawdown(self, returns):
        """Calculate maximum drawdown."""
        # Calculate cumulative returns
        cumulative = (1 + returns).cumprod()
        
        # Calculate running maximum
        running_max = cumulative.expanding().max()
        
        # Calculate drawdown
        drawdown = (cumulative - running_max) / running_max
        
        return drawdown.min()
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio."""
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        
        if returns.std() == 0:
            return 0
        
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    def calculate_sortino_ratio(self, returns, risk_free_rate=0.02):
        """Calculate Sortino ratio."""
        excess_returns = returns - risk_free_rate / 252
        
        # Calculate downside deviation
        downside_returns = returns[returns < risk_free_rate / 252]
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_deviation = np.std(downside_returns)
        
        if downside_deviation == 0:
            return float('inf')
        
        return np.sqrt(252) * excess_returns.mean() / downside_deviation
    
    def calculate_information_ratio(self, portfolio_returns, benchmark_returns):
        """Calculate Information ratio."""
        active_returns = portfolio_returns - benchmark_returns
        
        if np.std(active_returns) == 0:
            return 0
        
        return np.sqrt(252) * active_returns.mean() / np.std(active_returns)
    
    def _z_score(self):
        """Get Z-score for confidence level."""
        from scipy.stats import norm
        return norm.ppf(1 - self.confidence_level)

class AssetAllocator:
    """Multi-asset class allocation with constraints."""
    
    def __init__(self, min_weights=None, max_weights=None):
        self.min_weights = min_weights or {}
        self.max_weights = max_weights or {}
    
    def optimize_multi_asset_portfolio(self, assets_data, constraints=None):
        """Optimize multi-asset portfolio with constraints."""
        if constraints is None:
            constraints = self.default_constraints()
        
        # Extract asset classes
        stocks = self._extract_stocks_data(assets_data)
        forex = self._extract_forex_data(assets_data)
        metals = self._extract_metals_data(assets_data)
        
        # Optimize each asset class
        stock_weights = self._optimize_stock_allocation(stocks, constraints)
        forex_weights = self._optimize_forex_allocation(forex, constraints)
        metals_weights = self._optimize_metals_allocation(metals, constraints)
        
        # Combine allocations
        final_portfolio = self._combine_allocations(
            stock_weights, forex_weights, metals_weights, constraints
        )
        
        return final_portfolio
    
    def _extract_stocks_data(self, assets_data):
        """Extract stock data."""
        stocks = {
            'technology': self._get_tech_sector_data(assets_data),
            'healthcare': self._get_healthcare_sector_data(assets_data),
            'finance': self._get_finance_sector_data(assets_data),
            'energy': self._get_energy_sector_data(assets_data)
        }
        return stocks
    
    def _extract_forex_data(self, assets_data):
        """Extract forex data."""
        forex = {
            'EURUSD': assets_data.get('EURUSD', {'return': 0.05, 'vol': 0.12}),
            'GBPUSD': assets_data.get('GBPUSD', {'return': 0.04, 'vol': 0.15}),
            'USDJPY': assets_data.get('USDJPY', {'return': 0.02, 'vol': 0.10}),
            'USDCHF': assets_data.get('USDCHF', {'return': 0.01, 'vol': 0.08}),
            'AUDUSD': assets_data.get('AUDUSD', {'return': 0.06, 'vol': 0.18}),
            'USDCAD': assets_data.get('USDCAD', {'return': 0.03, 'vol': 0.12})
        }
        return forex
    
    def _extract_metals_data(self, assets_data):
        """Extract metals data."""
        metals = {
            'gold': assets_data.get('GOLD', {'return': 0.04, 'vol': 0.16}),
            'silver': assets_data.get('SILVER', {'return': 0.06, 'vol': 0.22}),
            'platinum': assets_data.get('PLATINUM', {'return': 0.05, 'vol': 0.20}),
            'palladium': assets_data.get('PALLADIUM', {'return': 0.08, 'vol': 0.28})
        }
        return metals
    
    def _get_tech_sector_data(self, assets_data):
        """Get technology sector data."""
        tech_assets = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META']
        return {
            asset: assets_data.get(asset, {'return': 0.15, 'vol': 0.25})
            for asset in tech_assets
        }
    
    def _get_healthcare_sector_data(self, assets_data):
        """Get healthcare sector data."""
        healthcare_assets = ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO']
        return {
            asset: assets_data.get(asset, {'return': 0.10, 'vol': 0.18})
            for asset in healthcare_assets
        }
    
    def _get_finance_sector_data(self, assets_data):
        """Get finance sector data."""
        finance_assets = ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C']
        return {
            asset: assets_data.get(asset, {'return': 0.08, 'vol': 0.20})
            for asset in finance_assets
        }
    
    def _get_energy_sector_data(self, assets_data):
        """Get energy sector data."""
        energy_assets = ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD']
        return {
            asset: assets_data.get(asset, {'return': 0.07, 'vol': 0.25})
            for asset in energy_assets
        }
    
    def _optimize_stock_allocation(self, stocks, constraints):
        """Optimize stock sector allocation."""
        sectors = list(stocks.keys())
        n_sectors = len(sectors)
        
        # Default sector limits
        sector_limits = constraints.get('sector_limits', {
            'technology': 0.30,
            'healthcare': 0.25,
            'finance': 0.25,
            'energy': 0.20
        })
        
        # Calculate sector returns and risks
        sector_returns = []
        for sector in sectors:
            assets_data = stocks[sector]
            returns = [asset_data['return'] for asset_data in assets_data.values()]
            sector_returns.append(np.mean(returns))
        
        sector_returns = np.array(sector_returns)
        
        # Simple allocation based on risk-adjusted returns
        allocation_weights = np.exp(sector_returns * 2)  # Exponential weighting
        allocation_weights = allocation_weights / np.sum(allocation_weights)
        
        # Apply sector limits
        for i, sector in enumerate(sectors):
            max_limit = sector_limits.get(sector, 0.5)
            allocation_weights[i] = min(allocation_weights[i], max_limit)
        
        # Re-normalize
        allocation_weights = allocation_weights / np.sum(allocation_weights)
        
        return dict(zip(sectors, allocation_weights))
    
    def _optimize_forex_allocation(self, forex, constraints):
        """Optimize forex allocation."""
        pairs = list(forex.keys())
        
        # Simple equal weight allocation with minor adjustments
        base_weight = 1.0 / len(pairs)
        weights = {pair: base_weight for pair in pairs}
        
        # Apply constraints
        for pair in pairs:
            max_weight = constraints.get('max_forex_weight', 0.25)
            weights[pair] = min(weights[pair], max_weight)
        
        return weights
    
    def _optimize_metals_allocation(self, metals, constraints):
        """Optimize metals allocation."""
        metal_names = list(metals.keys())
        
        # Calculate risk-adjusted returns
        adjusted_returns = []
        for metal in metal_names:
            data = metals[metal]
            risk_adj_return = data['return'] / max(data['vol'], 0.01)
            adjusted_returns.append(risk_adj_return)
        
        # Weight based on risk-adjusted returns
        weights_array = np.array(adjusted_returns)
        weights_array = np.exp(weights_array)  # Exponential weighting
        weights_array = weights_array / np.sum(weights_array)
        
        return dict(zip(metal_names, weights_array))
    
    def _combine_allocations(self, stock_weights, forex_weights, metals_weights, constraints):
        """Combine all asset class allocations."""
        # Asset class allocation weights
        class_weights = constraints.get('asset_class_weights', {
            'stocks': 0.60,
            'forex': 0.25,
            'metals': 0.15
        })
        
        # Create final portfolio
        final_portfolio = {}
        
        # Add stocks
        for sector, weight in stock_weights.items():
            final_portfolio[f"stocks_{sector}"] = weight * class_weights['stocks']
        
        # Add forex
        for pair, weight in forex_weights.items():
            final_portfolio[f"forex_{pair}"] = weight * class_weights['forex']
        
        # Add metals
        for metal, weight in metals_weights.items():
            final_portfolio[f"metals_{metal}"] = weight * class_weights['metals']
        
        return final_portfolio
    
    def default_constraints(self):
        """Default allocation constraints."""
        return {
            'asset_class_weights': {
                'stocks': 0.60,
                'forex': 0.25,
                'metals': 0.15
            },
            'sector_limits': {
                'technology': 0.30,
                'healthcare': 0.25,
                'finance': 0.25,
                'energy': 0.20
            },
            'max_forex_weight': 0.25,
            'max_metal_weight': 0.15,
            'liquidity_requirements': 0.10,
            'transaction_cost_budget': 0.01
        }

class PortfolioOptimizer:
    """Main portfolio optimizer class combining all methods."""
    
    def __init__(self, risk_free_rate=0.02, confidence_level=0.95):
        self.risk_free_rate = risk_free_rate
        self.confidence_level = confidence_level
        
        # Initialize all optimizers
        self.mpt_optimizer = ModernPortfolioTheory(risk_free_rate)
        self.bl_model = BlackLittermanModel(risk_free_rate=risk_free_rate)
        self.risk_parity = RiskParityOptimizer()
        self.quantum_optimizer = QuantumInspiredOptimizer()
        self.risk_metrics = RiskMetrics(confidence_level)
        self.asset_allocator = AssetAllocator()
    
    def optimize_portfolio(self, returns_data, method='quantum', 
                          constraints=None, target_metrics=None):
        """Main optimization function."""
        if constraints is None:
            constraints = self.default_constraints()
        
        if target_metrics is None:
            target_metrics = self.default_target_metrics()
        
        # Prepare data
        mean_returns = self._prepare_returns_data(returns_data)
        cov_matrix = self._prepare_covariance_matrix(returns_data)
        
        # Perform optimization based on method
        if method == 'quantum':
            weights = self.quantum_optimizer.optimize_portfolio(
                mean_returns, cov_matrix, constraints
            )
        elif method == 'mpt_max_sharpe':
            weights = self.mpt_optimizer.optimize_maximum_sharpe(
                mean_returns, cov_matrix
            )
        elif method == 'mpt_min_variance':
            weights = self.mpt_optimizer.optimize_minimum_variance(
                mean_returns, cov_matrix
            )
        elif method == 'black_litterman':
            weights = self._optimize_black_litterman(
                mean_returns, cov_matrix, returns_data, constraints
            )
        elif method == 'risk_parity':
            weights = self.risk_parity.optimize(cov_matrix)
        else:
            raise ValueError(f"Unknown optimization method: {method}")
        
        # Calculate portfolio metrics
        portfolio_metrics = self._calculate_portfolio_metrics(
            weights, mean_returns, cov_matrix, returns_data
        )
        
        return {
            'weights': weights,
            'metrics': portfolio_metrics,
            'method': method,
            'constraints': constraints
        }
    
    def _prepare_returns_data(self, returns_data):
        """Prepare returns data for optimization."""
        if isinstance(returns_data, dict):
            # Extract mean returns
            mean_returns = np.array([data.get('return', 0.05) 
                                   for data in returns_data.values()])
        else:
            # Assume DataFrame or array
            mean_returns = np.mean(returns_data, axis=0)
        
        return mean_returns
    
    def _prepare_covariance_matrix(self, returns_data):
        """Prepare covariance matrix."""
        if isinstance(returns_data, dict):
            # Create covariance matrix from provided data
            n_assets = len(returns_data)
            cov_matrix = np.eye(n_assets) * 0.01  # Initialize with small values
            
            for i, (asset1, data1) in enumerate(returns_data.items()):
                for j, (asset2, data2) in enumerate(returns_data.items()):
                    if i == j:
                        # Variance on diagonal
                        vol1 = data1.get('vol', 0.20)
                        cov_matrix[i, j] = vol1 ** 2
                    else:
                        # Correlation between assets (simplified)
                        vol1 = data1.get('vol', 0.20)
                        vol2 = data2.get('vol', 0.20)
                        correlation = 0.3  # Default correlation
                        cov_matrix[i, j] = correlation * vol1 * vol2
        else:
            # Calculate from actual returns data
            cov_matrix = np.cov(returns_data.T)
        
        return cov_matrix
    
    def _optimize_black_litterman(self, mean_returns, cov_matrix, returns_data, constraints):
        """Optimize using Black-Litterman model."""
        n_assets = len(mean_returns)
        
        # Create market cap weights (equal weight for simplicity)
        market_caps = np.ones(n_assets)
        
        # Create implied returns (slight modification of actual returns)
        implied_returns = mean_returns * 1.1  # Slight bullish bias
        
        # Fit Black-Litterman model
        bl_result = self.bl_model.fit(
            market_caps, implied_returns, cov_matrix,
            views=None, view_confidence=None
        )
        
        # Optimize portfolio with Black-Litterman inputs
        mpt_optimizer = ModernPortfolioTheory(self.risk_free_rate)
        weights = mpt_optimizer.optimize_maximum_sharpe(
            bl_result.final_returns, bl_result.final_cov_matrix
        )
        
        return weights
    
    def _calculate_portfolio_metrics(self, weights, mean_returns, cov_matrix, returns_data):
        """Calculate comprehensive portfolio metrics."""
        metrics = {}
        
        # Basic metrics
        portfolio_return = np.dot(weights, mean_returns)
        portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
        portfolio_std = np.sqrt(portfolio_variance)
        
        metrics['expected_return'] = portfolio_return
        metrics['volatility'] = portfolio_std
        metrics['sharpe_ratio'] = self.risk_metrics.calculate_sharpe_ratio(
            np.array([portfolio_return]), self.risk_free_rate
        )
        
        # Risk metrics (simulated for demonstration)
        simulated_returns = np.random.normal(
            portfolio_return, portfolio_std, 252
        )
        
        metrics['var_95'] = self.risk_metrics.calculate_var(simulated_returns)
        metrics['cvar_95'] = self.risk_metrics.calculate_cvar(simulated_returns)
        metrics['max_drawdown'] = self.risk_metrics.calculate_max_drawdown(
            pd.Series(simulated_returns)
        )
        
        # Additional metrics
        metrics['sortino_ratio'] = self.risk_metrics.calculate_sortino_ratio(
            pd.Series(simulated_returns), self.risk_free_rate
        )
        
        return metrics
    
    def default_constraints(self):
        """Default optimization constraints."""
        return {
            'max_weight': 0.40,
            'min_weight': 0.00,
            'target_return': 0.12,
            'max_risk': 0.25,
            'sector_limits': {
                'technology': 0.30,
                'healthcare': 0.25,
                'finance': 0.25,
                'energy': 0.20
            },
            'geographic_limits': {
                'US': 0.60,
                'Europe': 0.25,
                'Asia': 0.15
            },
            'liquidity_requirements': 0.10,
            'transaction_cost_budget': 0.01
        }
    
    def default_target_metrics(self):
        """Default target metrics."""
        return {
            'target_sharpe_ratio': 1.5,
            'max_var_95': -0.05,
            'max_cvar_95': -0.08,
            'max_drawdown': -0.15
        }
    
    def backtest_portfolio(self, historical_data, weights, rebalance_frequency='M'):
        """Backtest portfolio performance."""
        # This is a simplified backtesting implementation
        results = {
            'total_return': 0.0,
            'annualized_return': 0.0,
            'annualized_volatility': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0
        }
        
        # Simulate portfolio returns
        portfolio_returns = []
        for period in range(len(historical_data) - 1):
            period_return = np.dot(weights, 
                                  historical_data.iloc[period].values)
            portfolio_returns.append(period_return)
        
        portfolio_returns = np.array(portfolio_returns)
        
        # Calculate metrics
        results['total_return'] = np.prod(1 + portfolio_returns) - 1
        results['annualized_return'] = (1 + results['total_return']) ** (252 / len(portfolio_returns)) - 1
        results['annualized_volatility'] = np.std(portfolio_returns) * np.sqrt(252)
        results['sharpe_ratio'] = (results['annualized_return'] - self.risk_free_rate) / results['annualized_volatility']
        
        # Calculate drawdown
        cumulative = pd.Series((1 + portfolio_returns).cumprod())
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        results['max_drawdown'] = drawdown.min()
        
        # Win rate
        positive_returns = len(portfolio_returns[portfolio_returns > 0])
        results['win_rate'] = positive_returns / len(portfolio_returns)
        
        return results
    
    def generate_portfolio_report(self, optimization_result):
        """Generate comprehensive portfolio report."""
        weights = optimization_result['weights']
        metrics = optimization_result['metrics']
        method = optimization_result['method']
        
        report = f"""
=== PORTFOLIO OPTIMIZATION REPORT ===

Optimization Method: {method.upper()}
Risk-Free Rate: {self.risk_free_rate:.2%}
Confidence Level: {self.confidence_level:.1%}

=== PORTFOLIO ALLOCATION ===
"""
        
        for i, weight in enumerate(weights):
            if weight > 0.01:  # Only show significant allocations
                report += f"Asset {i+1}: {weight:.2%}\n"
        
        report += f"""
=== RISK METRICS ===
Expected Return: {metrics['expected_return']:.2%}
Volatility: {metrics['volatility']:.2%}
Sharpe Ratio: {metrics['sharpe_ratio']:.2f}

Value at Risk (95%): {metrics['var_95']:.2%}
Conditional VaR (95%): {metrics['cvar_95']:.2%}
Maximum Drawdown: {metrics['max_drawdown']:.2%}
Sortino Ratio: {metrics['sortino_ratio']:.2f}

=== RISK ASSESSMENT ===
Risk Level: {'Low' if metrics['volatility'] < 0.15 else 'Medium' if metrics['volatility'] < 0.25 else 'High'}
Return/Risk Profile: {'Good' if metrics['sharpe_ratio'] > 1.0 else 'Moderate' if metrics['sharpe_ratio'] > 0.5 else 'Poor'}
"""
        
        return report

# Usage Example and Testing
def create_sample_assets_data():
    """Create sample assets data for testing."""
    return {
        'AAPL': {'return': 0.15, 'vol': 0.25},
        'MSFT': {'return': 0.12, 'vol': 0.20},
        'GOOGL': {'return': 0.18, 'vol': 0.30},
        'JNJ': {'return': 0.08, 'vol': 0.15},
        'PFE': {'return': 0.10, 'vol': 0.22},
        'JPM': {'return': 0.06, 'vol': 0.18},
        'BAC': {'return': 0.07, 'vol': 0.20},
        'XOM': {'return': 0.05, 'vol': 0.25},
        'CVX': {'return': 0.04, 'vol': 0.22},
        'EURUSD': {'return': 0.03, 'vol': 0.12},
        'GBPUSD': {'return': 0.04, 'vol': 0.15},
        'GOLD': {'return': 0.04, 'vol': 0.16},
        'SILVER': {'return': 0.06, 'vol': 0.22}
    }

def run_optimization_examples():
    """Run optimization examples."""
    print("Multi-Asset Portfolio Optimizer Test")
    print("=" * 50)
    
    # Initialize optimizer
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    
    # Create sample data
    assets_data = create_sample_assets_data()
    
    # Test different optimization methods
    methods = ['quantum', 'mpt_max_sharpe', 'mpt_min_variance', 'risk_parity']
    
    for method in methods:
        print(f"\n--- {method.upper()} Optimization ---")
        try:
            result = optimizer.optimize_portfolio(
                assets_data, method=method
            )
            
            print(f"Expected Return: {result['metrics']['expected_return']:.2%}")
            print(f"Volatility: {result['metrics']['volatility']:.2%}")
            print(f"Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
            print(f"VaR (95%): {result['metrics']['var_95']:.2%}")
            
        except Exception as e:
            print(f"Error in {method}: {e}")
    
    # Test multi-asset allocation
    print("\n--- Multi-Asset Allocation ---")
    try:
        allocator = AssetAllocator()
        multi_asset_result = allocator.optimize_multi_asset_portfolio(assets_data)
        
        print("\nAsset Class Allocation:")
        for asset, weight in multi_asset_result.items():
            if weight > 0.01:
                print(f"{asset}: {weight:.2%}")
                
    except Exception as e:
        print(f"Error in multi-asset allocation: {e}")
    
    print("\n=== Optimization Complete ===")

if __name__ == "__main__":
    run_optimization_examples()