"""
AI Portfolio Manager
===================

Intelligent portfolio management tizimi:
- Asset allocation optimization
- Risk-based portfolio construction
- Dynamic rebalancing
- Correlation analysis
- Diversification strategies
- ESG integration
- Performance attribution

Risk Management:
- Portfolio VaR calculation
- Risk budgeting
- Stress testing
- Scenario analysis
- Volatility forecasting

Advanced Features:
- Machine learning allocation models
- Reinforcement learning for rebalancing
- Factor models (Fama-French)
- Black-Litterman model
- Risk parity strategies
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
import warnings
from abc import ABC, abstractmethod

# Scientific computing
from scipy import optimize
from scipy.stats import norm, t
from scipy.special import comb
import cvxpy as cp

# Machine Learning
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error

# Reinforcement Learning
try:
    from stable_baselines3 import PPO, A2C, DDPG
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.callbacks import BaseCallback
    RL_AVAILABLE = True
except ImportError:
    RL_AVAILABLE = False
    warnings.warn("Stable Baselines3 not available. RL features will be disabled.")

# Deep Learning
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Deep learning features will be disabled.")

# Plotting and visualization
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Asset:
    """Asset data class"""
    symbol: str
    name: str
    asset_class: str  # equity, bond, commodity, crypto, etc.
    sector: str
    region: str
    market_cap: float
    current_price: float
    historical_data: pd.DataFrame
    fundamental_data: Dict = field(default_factory=dict)
    esg_score: float = 0.0
    
    def __post_init__(self):
        if self.historical_data.empty:
            raise ValueError(f"Historical data is required for {self.symbol}")

@dataclass
class PortfolioConstraint:
    """Portfolio constraints"""
    min_weight: float = 0.0
    max_weight: float = 1.0
    sector_limits: Dict[str, float] = field(default_factory=dict)
    region_limits: Dict[str, float] = field(default_factory=dict)
    asset_class_limits: Dict[str, float] = field(default_factory=dict)
    rebalancing_threshold: float = 0.05  # 5% threshold for rebalancing
    max_turnover: float = 0.25  # Maximum 25% turnover per rebalancing

@dataclass
class RiskParameters:
    """Risk management parameters"""
    var_confidence: float = 0.95
    max_portfolio_var: float = 0.05  # 5% VaR
    max_single_position: float = 0.10  # 10% max single position
    max_sector_concentration: float = 0.30  # 30% max sector allocation
    max_region_concentration: float = 0.50  # 50% max region allocation
    correlation_threshold: float = 0.80
    stress_test_scenarios: List[Dict] = field(default_factory=list)

class BaseOptimizationModel(ABC):
    """Base class for optimization models"""
    
    @abstractmethod
    def optimize(self, returns: np.ndarray, expected_returns: np.ndarray, 
                 cov_matrix: np.ndarray, constraints: PortfolioConstraint) -> np.ndarray:
        pass

class MeanVarianceOptimizer(BaseOptimizationModel):
    """Mean-Variance optimization model"""
    
    def __init__(self, risk_aversion: float = 1.0):
        self.risk_aversion = risk_aversion
    
    def optimize(self, returns: np.ndarray, expected_returns: np.ndarray, 
                 cov_matrix: np.ndarray, constraints: PortfolioConstraint) -> np.ndarray:
        n_assets = len(expected_returns)
        
        # Define optimization variables
        weights = cp.Variable(n_assets)
        
        # Objective: maximize expected return - risk_penalty * variance
        expected_return = expected_returns.T @ weights
        portfolio_variance = cp.quad_form(weights, cov_matrix)
        
        objective = cp.Maximize(expected_return - self.risk_aversion * portfolio_variance)
        
        # Constraints
        constraints_list = [
            cp.sum(weights) == 1,  # Full investment
            weights >= constraints.min_weight,
            weights <= constraints.max_weight,
        ]
        
        # Solve optimization problem
        problem = cp.Problem(objective, constraints_list)
        problem.solve()
        
        if problem.status != cp.OPTIMAL:
            logger.warning(f"Optimization failed with status: {problem.status}")
            return np.ones(n_assets) / n_assets  # Equal weights as fallback
        
        return np.array(weights.value)

class RiskParityOptimizer(BaseOptimizationModel):
    """Risk parity optimization model"""
    
    def optimize(self, returns: np.ndarray, expected_returns: np.ndarray, 
                 cov_matrix: np.ndarray, constraints: PortfolioConstraint) -> np.ndarray:
        n_assets = len(expected_returns)
        
        # Define optimization variables
        weights = cp.Variable(n_assets)
        risk_budget = cp.Variable(n_assets)
        
        # Calculate portfolio risk contribution
        portfolio_vol = cp.sqrt(cp.quad_form(weights, cov_matrix))
        risk_contrib = cp.multiply(weights, cov_matrix @ weights) / portfolio_vol
        
        # Objective: minimize deviation from equal risk contribution
        target_risk_contrib = portfolio_vol / n_assets
        objective = cp.Minimize(cp.sum_squares(risk_contrib - target_risk_contrib))
        
        # Constraints
        constraints_list = [
            cp.sum(weights) == 1,
            weights >= constraints.min_weight,
            weights <= constraints.max_weight,
        ]
        
        # Solve optimization problem
        problem = cp.Problem(objective, constraints_list)
        problem.solve()
        
        if problem.status != cp.OPTIMAL:
            logger.warning(f"Risk parity optimization failed with status: {problem.status}")
            return np.ones(n_assets) / n_assets
        
        return np.array(weights.value)

class BlackLittermanOptimizer(BaseOptimizationModel):
    """Black-Litterman model implementation"""
    
    def __init__(self, risk_aversion: float = 1.0, confidence_level: float = 0.25):
        self.risk_aversion = risk_aversion
        self.confidence_level = confidence_level
    
    def _calculate_implied_returns(self, cov_matrix: np.ndarray, market_caps: np.ndarray) -> np.ndarray:
        """Calculate implied equilibrium returns"""
        market_portfolio = market_caps / np.sum(market_caps)
        risk_free_rate = 0.02  # Assume 2% risk-free rate
        
        pi = self.risk_aversion * cov_matrix @ market_portfolio
        return pi + risk_free_rate
    
    def optimize(self, returns: np.ndarray, expected_returns: np.ndarray, 
                 cov_matrix: np.ndarray, constraints: PortfolioConstraint) -> np.ndarray:
        n_assets = len(expected_returns)
        market_caps = np.array([1.0] * n_assets)  # Assume equal market caps
        
        # Calculate implied equilibrium returns
        pi = self._calculate_implied_returns(cov_matrix, market_caps)
        
        # Combine market views with equilibrium returns
        P = np.eye(n_assets)  # Views matrix
        Q = expected_returns  # View returns
        omega = np.diag(np.diag(P @ cov_matrix @ P.T) / self.confidence_level)
        
        # Black-Litterman formula
        tau = 0.025  # Scaling factor
        M1 = np.linalg.inv(tau * cov_matrix)
        M2 = P.T @ np.linalg.inv(omega) @ P
        M3 = np.linalg.inv(tau * cov_matrix) @ pi
        M4 = P.T @ np.linalg.inv(omega) @ Q
        
        mu_bl = np.linalg.inv(M1 + M2) @ (M3 + M4)
        
        # Optimize portfolio with Black-Litterman returns
        weights = cp.Variable(n_assets)
        portfolio_variance = cp.quad_form(weights, cov_matrix)
        expected_return = mu_bl.T @ weights
        
        objective = cp.Maximize(expected_return - self.risk_aversion * portfolio_variance)
        
        constraints_list = [
            cp.sum(weights) == 1,
            weights >= constraints.min_weight,
            weights <= constraints.max_weight,
        ]
        
        problem = cp.Problem(objective, constraints_list)
        problem.solve()
        
        if problem.status != cp.OPTIMAL:
            logger.warning(f"Black-Litterman optimization failed with status: {problem.status}")
            return np.ones(n_assets) / n_assets
        
        return np.array(weights.value)

class FactorModel:
    """Fama-French factor model implementation"""
    
    def __init__(self, factors: List[str] = None):
        self.factors = factors or ['MKT', 'SMB', 'HML', 'RMW', 'CMA']
        self.factor_loadings = None
        self.factor_returns = None
        self.residual_variance = None
    
    def fit(self, returns: pd.DataFrame, factor_data: pd.DataFrame) -> Dict:
        """Fit factor model to returns data"""
        aligned_data = returns.join(factor_data, how='inner').dropna()
        
        if aligned_data.empty:
            raise ValueError("No matching data between returns and factors")
        
        n_assets = len(returns.columns)
        n_factors = len(self.factors)
        
        self.factor_loadings = np.zeros((n_assets, n_factors))
        self.factor_returns = aligned_data[self.factors].values
        self.residual_variance = np.zeros(n_assets)
        
        # Fit each asset's returns to factors
        for i, asset in enumerate(returns.columns):
            if asset in aligned_data.columns:
                asset_returns = aligned_data[asset].values
                X = aligned_data[self.factors].values
                
                # Remove NaN values
                valid_idx = ~(np.isnan(asset_returns) | np.isnan(X).any(axis=1))
                if np.sum(valid_idx) > n_factors:
                    X_clean = X[valid_idx]
                    y_clean = asset_returns[valid_idx]
                    
                    # OLS regression
                    try:
                        beta = np.linalg.lstsq(X_clean, y_clean, rcond=None)[0]
                        self.factor_loadings[i, :] = beta
                        residuals = y_clean - X_clean @ beta
                        self.residual_variance[i] = np.var(residuals)
                    except np.linalg.LinAlgError:
                        logger.warning(f"Failed to fit factor model for {asset}")
        
        # Calculate factor covariance matrix
        self.factor_cov = np.cov(self.factor_returns.T)
        
        return {
            'factor_loadings': self.factor_loadings,
            'factor_covariance': self.factor_cov,
            'residual_variance': self.residual_variance
        }
    
    def predict_return(self, asset_idx: int, factor_forecast: np.ndarray) -> float:
        """Predict expected return for an asset using factor forecasts"""
        if self.factor_loadings is None:
            raise ValueError("Model must be fitted before prediction")
        
        return np.dot(self.factor_loadings[asset_idx], factor_forecast)
    
    def predict_covariance(self, factor_cov: np.ndarray = None) -> np.ndarray:
        """Predict asset covariance matrix using factor model"""
        if self.factor_loadings is None:
            raise ValueError("Model must be fitted before prediction")
        
        if factor_cov is None:
            factor_cov = self.factor_cov
        
        # Systematic risk: B * F * B'
        systematic_cov = self.factor_loadings @ factor_cov @ self.factor_loadings.T
        
        # Idiosyncratic risk
        idiosyncratic_cov = np.diag(self.residual_variance)
        
        return systematic_cov + idiosyncratic_cov

class RiskManager:
    """Portfolio risk management"""
    
    def __init__(self, params: RiskParameters):
        self.params = params
    
    def calculate_var(self, returns: np.ndarray, weights: np.ndarray, 
                     method: str = 'historical', confidence: float = None) -> float:
        """Calculate Value at Risk (VaR)"""
        if confidence is None:
            confidence = self.params.var_confidence
        
        portfolio_returns = np.dot(returns, weights)
        
        if method == 'historical':
            var = np.percentile(portfolio_returns, (1 - confidence) * 100)
        elif method == 'parametric':
            mu = np.mean(portfolio_returns)
            sigma = np.std(portfolio_returns)
            var = mu + sigma * norm.ppf(1 - confidence)
        elif method == 'monte_carlo':
            # Monte Carlo simulation
            n_simulations = 10000
            simulated_returns = np.random.normal(
                np.mean(portfolio_returns), 
                np.std(portfolio_returns), 
                n_simulations
            )
            var = np.percentile(simulated_returns, (1 - confidence) * 100)
        
        return abs(var)  # VaR is typically expressed as positive number
    
    def calculate_expected_shortfall(self, returns: np.ndarray, weights: np.ndarray,
                                   confidence: float = None) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        if confidence is None:
            confidence = self.params.var_confidence
        
        portfolio_returns = np.dot(returns, weights)
        var = self.calculate_var(returns, weights, confidence=confidence)
        
        # Expected shortfall is the average of returns worse than VaR
        tail_returns = portfolio_returns[portfolio_returns <= -var]
        return abs(np.mean(tail_returns)) if len(tail_returns) > 0 else var
    
    def stress_test(self, returns: np.ndarray, weights: np.ndarray, 
                   scenarios: List[Dict] = None) -> Dict[str, float]:
        """Stress test portfolio against various scenarios"""
        if scenarios is None:
            scenarios = self.params.stress_test_scenarios
        
        results = {}
        current_portfolio_value = 100  # Base value for stress testing
        
        for scenario in scenarios:
            scenario_name = scenario.get('name', 'Unknown Scenario')
            shocks = scenario.get('shocks', {})
            
            # Apply shocks to returns
            stressed_returns = returns.copy()
            for asset_idx, shock in shocks.items():
                stressed_returns[:, asset_idx] *= (1 + shock)
            
            # Calculate stressed portfolio return
            stressed_portfolio_return = np.dot(stressed_returns.mean(axis=0), weights)
            stressed_value = current_portfolio_value * (1 + stressed_portfolio_return)
            
            results[scenario_name] = (stressed_value - current_portfolio_value) / current_portfolio_value
        
        return results
    
    def calculate_correlation_matrix(self, returns: np.ndarray) -> np.ndarray:
        """Calculate correlation matrix"""
        return np.corrcoef(returns.T)
    
    def detect_correlation_breakdown(self, current_corr: np.ndarray, 
                                   historical_corrs: List[np.ndarray],
                                   threshold: float = None) -> Dict:
        """Detect correlation breakdown"""
        if threshold is None:
            threshold = self.params.correlation_threshold
        
        breakdown_assets = []
        breakdown_regions = []
        
        for i, historical_corr in enumerate(historical_corrs):
            if len(historical_corr.shape) == 2 and current_corr.shape == historical_corr.shape:
                # Find correlations that have significantly changed
                corr_diff = np.abs(current_corr - historical_corr)
                significant_changes = np.where(corr_diff > threshold)
                
                for asset1, asset2 in zip(significant_changes[0], significant_changes[1]):
                    breakdown_assets.append((asset1, asset2, corr_diff[asset1, asset2]))
        
        return {
            'breakdown_assets': breakdown_assets,
            'correlation_drift': np.mean([np.abs(current_corr - hist_corr).mean() 
                                        for hist_corr in historical_corrs 
                                        if hist_corr.shape == current_corr.shape])
        }

class ESGIntegrator:
    """ESG (Environmental, Social, Governance) integration"""
    
    def __init__(self, esg_weights: Dict[str, float] = None):
        self.esg_weights = esg_weights or {'E': 0.4, 'S': 0.3, 'G': 0.3}
    
    def calculate_esg_score(self, assets: List[Asset]) -> np.ndarray:
        """Calculate ESG scores for assets"""
        return np.array([asset.esg_score for asset in assets])
    
    def esg_constraint_optimization(self, returns: np.ndarray, expected_returns: np.ndarray,
                                  cov_matrix: np.ndarray, esg_scores: np.ndarray,
                                  min_esg_score: float = 0.5) -> np.ndarray:
        """Optimize portfolio with ESG constraints"""
        n_assets = len(expected_returns)
        
        weights = cp.Variable(n_assets)
        
        # Objective: maximize expected return subject to ESG constraint
        expected_return = expected_returns.T @ weights
        portfolio_esg_score = esg_scores.T @ weights
        
        objective = cp.Maximize(expected_return)
        
        # Constraints
        constraints = [
            cp.sum(weights) == 1,
            weights >= 0,
            weights <= 1,
            portfolio_esg_score >= min_esg_score,
        ]
        
        # Add risk constraint
        portfolio_variance = cp.quad_form(weights, cov_matrix)
        constraints.append(portfolio_variance <= 0.1)  # Maximum 10% variance
        
        problem = cp.Problem(objective, constraints)
        problem.solve()
        
        if problem.status != cp.OPTIMAL:
            logger.warning(f"ESG optimization failed with status: {problem.status}")
            return np.ones(n_assets) / n_assets
        
        return np.array(weights.value)

class MachineLearningAllocator:
    """Machine learning-based asset allocation"""
    
    def __init__(self, model_type: str = 'random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = None
    
    def prepare_features(self, returns: np.ndarray, factors: np.ndarray = None,
                        sentiment: np.ndarray = None, macro_data: np.ndarray = None) -> np.ndarray:
        """Prepare features for ML model"""
        features = []
        
        # Historical return features
        if returns is not None and len(returns.shape) > 1:
            # Rolling statistics
            rolling_mean = np.mean(returns[-20:], axis=0)  # 20-day rolling mean
            rolling_std = np.std(returns[-20:], axis=0)    # 20-day rolling std
            features.extend([rolling_mean, rolling_std])
        
        # Market factors
        if factors is not None:
            features.append(factors)
        
        # Sentiment data
        if sentiment is not None:
            features.append(sentiment)
        
        # Macro-economic data
        if macro_data is not None:
            features.append(macro_data)
        
        if not features:
            return np.array([]).reshape(len(returns), 0) if returns is not None else np.array([])
        
        return np.hstack(features)
    
    def train_model(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Dict:
        """Train ML model for return prediction"""
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif self.model_type == 'ridge':
            self.model = Ridge(alpha=1.0)
        else:
            self.model = LinearRegression()
        
        # Time series split for validation
        tscv = TimeSeriesSplit(n_splits=5)
        scores = []
        
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Predict and evaluate
            y_pred = self.model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            scores.append(mse)
        
        avg_score = np.mean(scores)
        
        # Feature importance (for tree-based models)
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = self.model.feature_importances_
        
        return {'cv_score': avg_score, 'feature_importance': self.feature_importance}
    
    def predict_returns(self, X: np.ndarray) -> np.ndarray:
        """Predict expected returns using trained model"""
        if self.model is None:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

class ReinforcementLearningRebalancer:
    """Reinforcement Learning for portfolio rebalancing"""
    
    def __init__(self, env_config: Dict = None):
        self.env_config = env_config or {}
        self.model = None
        self.is_trained = False
    
    def create_env(self, returns: np.ndarray, initial_weights: np.ndarray,
                   transaction_cost: float = 0.001):
        """Create trading environment for RL"""
        if not RL_AVAILABLE:
            raise ImportError("Stable Baselines3 is required for RL features")
        
        class PortfolioEnv:
            def __init__(self, returns, initial_weights, transaction_cost):
                self.returns = returns
                self.initial_weights = initial_weights
                self.transaction_cost = transaction_cost
                self.current_step = 0
                self.max_steps = len(returns) - 1
                self.action_space = gym.spaces.Box(-1, 1, (len(initial_weights),))
                self.observation_space = gym.spaces.Box(-np.inf, np.inf, (len(initial_weights) * 2,))
                self.current_weights = initial_weights.copy()
                self.portfolio_value = 1.0
                self.portfolio_history = [1.0]
            
            def reset(self):
                self.current_step = 0
                self.current_weights = self.initial_weights.copy()
                self.portfolio_value = 1.0
                self.portfolio_history = [1.0]
                return self._get_observation()
            
            def step(self, action):
                # Normalize action to be weights
                new_weights = self._softmax(action)
                
                # Calculate transaction cost
                weight_diff = np.abs(new_weights - self.current_weights)
                turnover = np.sum(weight_diff)
                cost = turnover * self.transaction_cost
                
                # Update portfolio
                self.current_weights = new_weights
                portfolio_return = np.dot(self.returns[self.current_step], self.current_weights)
                self.portfolio_value *= (1 + portfolio_return - cost)
                self.portfolio_history.append(self.portfolio_value)
                self.current_step += 1
                
                # Reward function: maximize portfolio value with penalty for high turnover
                reward = portfolio_return - cost - 0.01 * turnover
                
                # Done flag
                done = self.current_step >= self.max_steps
                
                # Observation
                obs = self._get_observation()
                
                return obs, reward, done, {'portfolio_value': self.portfolio_value}
            
            def _get_observation(self):
                return np.concatenate([self.current_weights, self.portfolio_history[-5:]])
            
            def _softmax(self, x):
                exp_x = np.exp(x - np.max(x))
                return exp_x / np.sum(exp_x)
        
        import gym
        env = PortfolioEnv(returns, initial_weights, transaction_cost)
        return env
    
    def train(self, returns: np.ndarray, initial_weights: np.ndarray, 
              algorithm: str = 'PPO', total_timesteps: int = 100000) -> Dict:
        """Train RL agent for portfolio rebalancing"""
        if not RL_AVAILABLE:
            raise ImportError("Stable Baselines3 is required for RL features")
        
        # Create environment
        env = self.create_env(returns, initial_weights)
        
        # Create agent
        if algorithm == 'PPO':
            self.model = PPO('MlpPolicy', env, verbose=1)
        elif algorithm == 'A2C':
            self.model = A2C('MlpPolicy', env, verbose=1)
        else:
            self.model = DDPG('MlpPolicy', env, verbose=1)
        
        # Train agent
        self.model.learn(total_timesteps=total_timesteps)
        self.is_trained = True
        
        return {'training_completed': True, 'algorithm': algorithm}
    
    def get_rebalancing_action(self, observation: np.ndarray) -> np.ndarray:
        """Get rebalancing action from trained agent"""
        if not self.is_trained:
            raise ValueError("Model must be trained before getting actions")
        
        action, _ = self.model.predict(observation)
        return action

class PerformanceAttribution:
    """Portfolio performance attribution analysis"""
    
    def __init__(self):
        self.attribution_results = {}
    
    def calculate_benchmark_return(self, returns: np.ndarray, benchmark_weights: np.ndarray) -> np.ndarray:
        """Calculate benchmark return"""
        return np.dot(returns, benchmark_weights)
    
    def calculate_active_return(self, portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> np.ndarray:
        """Calculate active return"""
        return portfolio_returns - benchmark_returns
    
    def calculate_selection_effect(self, returns: np.ndarray, portfolio_weights: np.ndarray,
                                 benchmark_weights: np.ndarray) -> np.ndarray:
        """Calculate selection effect"""
        return (portfolio_weights - benchmark_weights) @ returns.T
    
    def calculate_allocation_effect(self, returns: np.ndarray, portfolio_weights: np.ndarray,
                                 benchmark_weights: np.ndarray, benchmark_returns: np.ndarray) -> np.ndarray:
        """Calculate allocation effect"""
        return (portfolio_weights - benchmark_weights) @ benchmark_returns
    
    def full_attribution_analysis(self, returns: np.ndarray, portfolio_weights: np.ndarray,
                                benchmark_weights: np.ndarray, benchmark_returns: np.ndarray) -> Dict:
        """Full performance attribution analysis"""
        # Calculate component returns
        portfolio_return = np.dot(returns, portfolio_weights)
        benchmark_return = self.calculate_benchmark_return(returns, benchmark_weights)
        active_return = self.calculate_active_return(portfolio_return, benchmark_return)
        
        # Calculate effects
        selection_effect = self.calculate_selection_effect(returns, portfolio_weights, benchmark_weights)
        allocation_effect = self.calculate_allocation_effect(returns, portfolio_weights, benchmark_weights, benchmark_return)
        
        # Sector attribution
        sector_attribution = self._calculate_sector_attribution(returns, portfolio_weights, benchmark_weights)
        
        return {
            'portfolio_return': portfolio_return,
            'benchmark_return': benchmark_return,
            'active_return': active_return,
            'selection_effect': selection_effect,
            'allocation_effect': allocation_effect,
            'total_attribution': selection_effect + allocation_effect,
            'sector_attribution': sector_attribution,
            'attribution_efficiency': (selection_effect + allocation_effect) / abs(active_return) if active_return != 0 else 0
        }
    
    def _calculate_sector_attribution(self, returns: np.ndarray, portfolio_weights: np.ndarray,
                                    benchmark_weights: np.ndarray) -> Dict:
        """Calculate sector-level attribution (placeholder implementation)"""
        # This would require sector classification of assets
        # For now, return a simplified version
        return {
            'technology': 0.01,
            'healthcare': 0.005,
            'financials': -0.002,
            'energy': 0.003
        }

class AIPortfolioManager:
    """Main AI Portfolio Manager class"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.assets = []
        self.constraints = PortfolioConstraint()
        self.risk_params = RiskParameters()
        
        # Initialize components
        self.optimizers = {
            'mean_variance': MeanVarianceOptimizer(),
            'risk_parity': RiskParityOptimizer(),
            'black_litterman': BlackLittermanOptimizer()
        }
        
        self.factor_model = FactorModel()
        self.risk_manager = RiskManager(self.risk_params)
        self.esg_integrator = ESGIntegrator()
        self.ml_allocator = MachineLearningAllocator()
        self.performance_attributor = PerformanceAttribution()
        
        # RL rebalancer (optional)
        if RL_AVAILABLE:
            self.rl_rebalancer = ReinforcementLearningRebalancer()
        else:
            self.rl_rebalancer = None
        
        # Current portfolio state
        self.current_weights = None
        self.portfolio_history = []
        self.risk_metrics = {}
    
    def add_asset(self, asset: Asset) -> None:
        """Add asset to the portfolio universe"""
        self.assets.append(asset)
        logger.info(f"Added asset: {asset.symbol}")
    
    def set_constraints(self, constraints: PortfolioConstraint) -> None:
        """Set portfolio constraints"""
        self.constraints = constraints
        logger.info("Portfolio constraints updated")
    
    def set_risk_parameters(self, risk_params: RiskParameters) -> None:
        """Set risk management parameters"""
        self.risk_params = risk_params
        self.risk_manager = RiskManager(self.risk_params)
        logger.info("Risk parameters updated")
    
    def calculate_portfolio_metrics(self, returns: np.ndarray = None) -> Dict:
        """Calculate comprehensive portfolio metrics"""
        if returns is None and self.assets:
            # Use historical data from assets
            returns = np.array([asset.historical_data['close'].pct_change().dropna().values 
                              for asset in self.assets]).T
        
        if returns is None or self.current_weights is None:
            return {}
        
        portfolio_returns = np.dot(returns, self.current_weights)
        
        # Basic metrics
        total_return = np.prod(1 + portfolio_returns) - 1
        annualized_return = np.mean(portfolio_returns) * 252
        volatility = np.std(portfolio_returns) * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Risk metrics
        var_95 = self.risk_manager.calculate_var(returns, self.current_weights, confidence=0.95)
        var_99 = self.risk_manager.calculate_var(returns, self.current_weights, confidence=0.99)
        expected_shortfall = self.risk_manager.calculate_expected_shortfall(returns, self.current_weights)
        
        # Downside metrics
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_deviation = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = annualized_return / downside_deviation if downside_deviation > 0 else 0
        
        # Max drawdown
        cumulative_returns = np.cumprod(1 + portfolio_returns)
        rolling_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = np.min(drawdown)
        
        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'var_95': var_95,
            'var_99': var_99,
            'expected_shortfall': expected_shortfall,
            'downside_deviation': downside_deviation,
            'max_drawdown': max_drawdown,
            'current_weights': self.current_weights,
            'number_of_assets': len(self.current_weights),
            'portfolio_concentration': np.max(self.current_weights)
        }
        
        self.risk_metrics = metrics
        return metrics
    
    def optimize_portfolio(self, method: str = 'mean_variance', 
                          expected_returns: np.ndarray = None,
                          returns_data: np.ndarray = None) -> np.ndarray:
        """Optimize portfolio using specified method"""
        if not self.assets:
            raise ValueError("No assets in portfolio universe")
        
        # Prepare data
        n_assets = len(self.assets)
        
        if returns_data is None:
            returns_data = np.array([asset.historical_data['close'].pct_change().dropna().values 
                                   for asset in self.assets]).T
        
        if expected_returns is None:
            # Use historical mean returns
            expected_returns = np.mean(returns_data, axis=0)
        
        # Calculate covariance matrix
        cov_matrix = np.cov(returns_data.T)
        
        # Add regularization for numerical stability
        cov_matrix += np.eye(n_assets) * 1e-8
        
        # Select optimizer
        if method not in self.optimizers:
            method = 'mean_variance'
        
        optimizer = self.optimizers[method]
        
        # Optimize
        optimal_weights = optimizer.optimize(returns_data, expected_returns, cov_matrix, self.constraints)
        
        # Ensure weights are valid
        optimal_weights = np.maximum(0, optimal_weights)
        if np.sum(optimal_weights) > 0:
            optimal_weights = optimal_weights / np.sum(optimal_weights)
        
        self.current_weights = optimal_weights
        logger.info(f"Portfolio optimized using {method}")
        
        return optimal_weights
    
    def rebalance_portfolio(self, method: str = 'threshold', tolerance: float = None) -> Dict:
        """Rebalance portfolio based on method"""
        if self.current_weights is None:
            raise ValueError("Portfolio must be optimized before rebalancing")
        
        if tolerance is None:
            tolerance = self.constraints.rebalancing_threshold
        
        if method == 'threshold':
            return self._rebalance_threshold(tolerance)
        elif method == 'calendar':
            return self._rebalance_calendar()
        elif method == 'rl_based' and self.rl_rebalancer and self.rl_rebalancer.is_trained:
            return self._rebalance_rl()
        else:
            return self._rebalance_threshold(tolerance)
    
    def _rebalance_threshold(self, tolerance: float) -> Dict:
        """Rebalance when weights drift beyond threshold"""
        if self.current_weights is None:
            return {'action': 'no_rebalance', 'reason': 'No current weights'}
        
        # Calculate target weights (assume equal weights for simplicity)
        target_weights = np.ones(len(self.current_weights)) / len(self.current_weights)
        
        # Check if rebalancing is needed
        weight_drift = np.abs(self.current_weights - target_weights)
        max_drift = np.max(weight_drift)
        
        if max_drift <= tolerance:
            return {
                'action': 'no_rebalance',
                'reason': f'Maximum weight drift {max_drift:.4f} below threshold {tolerance:.4f}',
                'current_weights': self.current_weights,
                'target_weights': target_weights
            }
        
        # Calculate rebalancing trades
        rebalance_weights = self.current_weights.copy()
        trades = []
        
        for i, (current, target) in enumerate(zip(self.current_weights, target_weights)):
            if abs(current - target) > tolerance:
                trade_size = target - current
                rebalance_weights[i] = target
                trades.append({
                    'asset_index': i,
                    'asset_symbol': self.assets[i].symbol,
                    'trade_size': trade_size,
                    'current_weight': current,
                    'new_weight': target
                })
        
        # Normalize weights to sum to 1
        rebalance_weights = np.maximum(0, rebalance_weights)
        rebalance_weights = rebalance_weights / np.sum(rebalance_weights)
        
        # Update current weights
        self.current_weights = rebalance_weights
        
        return {
            'action': 'rebalance',
            'reason': f'Weight drift {max_drift:.4f} exceeds threshold {tolerance:.4f}',
            'trades': trades,
            'turnover': np.sum([abs(trade['trade_size']) for trade in trades]),
            'new_weights': rebalance_weights
        }
    
    def _rebalance_calendar(self) -> Dict:
        """Calendar-based rebalancing (quarterly assumption)"""
        # Simple implementation - would need to track last rebalance date
        today = datetime.now()
        # For demo purposes, always rebalance
        return self._rebalance_threshold(0.01)  # Lower threshold for calendar rebalancing
    
    def _rebalance_rl(self) -> Dict:
        """RL-based rebalancing"""
        if not (self.rl_rebalancer and self.rl_rebalancer.is_trained):
            return {'action': 'fallback', 'reason': 'RL model not available'}
        
        # Get current observation
        observation = np.concatenate([self.current_weights, [1.0]])  # Simplified observation
        
        # Get action from RL agent
        action = self.rl_rebalancer.get_rebalancing_action(observation)
        
        # Convert action to weights
        new_weights = self.rl_rebalancer._softmax(action)
        
        # Update weights
        self.current_weights = new_weights
        
        return {
            'action': 'rl_rebalance',
            'new_weights': new_weights,
            'action_vector': action
        }
    
    def run_stress_test(self, scenarios: List[Dict] = None) -> Dict:
        """Run comprehensive stress test"""
        if self.current_weights is None:
            raise ValueError("Portfolio must be optimized before stress testing")
        
        # Default stress scenarios
        default_scenarios = [
            {
                'name': 'Market Crash',
                'shocks': {i: -0.20 for i in range(len(self.assets))}
            },
            {
                'name': 'Interest Rate Shock',
                'shocks': {i: 0.10 for i in range(len(self.assets)) if self.assets[i].asset_class == 'bond'}
            },
            {
                'name': 'Sector Rotation',
                'shocks': {i: 0.15 for i, asset in enumerate(self.assets) if asset.sector == 'technology'}
            }
        ]
        
        stress_scenarios = scenarios or default_scenarios
        
        # Prepare returns data
        returns_data = np.array([asset.historical_data['close'].pct_change().dropna().values 
                               for asset in self.assets]).T
        
        # Run stress tests
        stress_results = self.risk_manager.stress_test(returns_data, self.current_weights, stress_scenarios)
        
        # Calculate additional risk metrics
        var_results = {
            'var_95': self.risk_manager.calculate_var(returns_data, self.current_weights, confidence=0.95),
            'var_99': self.risk_manager.calculate_var(returns_data, self.current_weights, confidence=0.99),
            'expected_shortfall': self.risk_manager.calculate_expected_shortfall(returns_data, self.current_weights)
        }
        
        return {
            'stress_test_results': stress_results,
            'var_analysis': var_results,
            'scenarios_tested': len(stress_scenarios)
        }
    
    def generate_report(self, include_charts: bool = True) -> str:
        """Generate comprehensive portfolio report"""
        if not self.current_weights:
            return "Portfolio not yet optimized. Please run optimize_portfolio() first."
        
        # Calculate metrics
        metrics = self.calculate_portfolio_metrics()
        
        # Generate report
        report = []
        report.append("=== AI PORTFOLIO MANAGER REPORT ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Portfolio Summary
        report.append("PORTFOLIO SUMMARY:")
        report.append(f"Number of Assets: {metrics['number_of_assets']}")
        report.append(f"Total Return: {metrics['total_return']:.4f}")
        report.append(f"Annualized Return: {metrics['annualized_return']:.4f}")
        report.append(f"Volatility: {metrics['volatility']:.4f}")
        report.append(f"Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
        report.append(f"Sortino Ratio: {metrics['sortino_ratio']:.4f}")
        report.append("")
        
        # Risk Metrics
        report.append("RISK METRICS:")
        report.append(f"VaR (95%): {metrics['var_95']:.4f}")
        report.append(f"VaR (99%): {metrics['var_99']:.4f}")
        report.append(f"Expected Shortfall: {metrics['expected_shortfall']:.4f}")
        report.append(f"Maximum Drawdown: {metrics['max_drawdown']:.4f}")
        report.append(f"Downside Deviation: {metrics['downside_deviation']:.4f}")
        report.append("")
        
        # Portfolio Composition
        report.append("PORTFOLIO COMPOSITION:")
        for i, (asset, weight) in enumerate(zip(self.assets, metrics['current_weights'])):
            if weight > 0.01:  # Only show significant positions
                report.append(f"{asset.symbol:10} {weight:8.4f} ({weight*100:6.2f}%)")
        report.append("")
        
        # Performance Attribution
        if hasattr(self, 'benchmark_weights') and self.benchmark_weights is not None:
            returns_data = np.array([asset.historical_data['close'].pct_change().dropna().values 
                                   for asset in self.assets]).T
            attribution = self.performance_attributor.full_attribution_analysis(
                returns_data, metrics['current_weights'], self.benchmark_weights, 
                np.dot(returns_data, self.benchmark_weights)
            )
            
            report.append("PERFORMANCE ATTRIBUTION:")
            report.append(f"Active Return: {attribution['active_return']:.4f}")
            report.append(f"Selection Effect: {attribution['selection_effect']:.4f}")
            report.append(f"Allocation Effect: {attribution['allocation_effect']:.4f}")
            report.append("")
        
        return "\n".join(report)
    
    def save_portfolio_state(self, filepath: str) -> None:
        """Save current portfolio state"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'current_weights': self.current_weights.tolist() if self.current_weights is not None else None,
            'assets': [
                {
                    'symbol': asset.symbol,
                    'name': asset.name,
                    'asset_class': asset.asset_class,
                    'sector': asset.sector,
                    'region': asset.region,
                    'market_cap': asset.market_cap,
                    'current_price': asset.current_price,
                    'esg_score': asset.esg_score
                }
                for asset in self.assets
            ],
            'risk_metrics': self.risk_metrics,
            'constraints': {
                'min_weight': self.constraints.min_weight,
                'max_weight': self.constraints.max_weight,
                'rebalancing_threshold': self.constraints.rebalancing_threshold
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Portfolio state saved to {filepath}")
    
    def load_portfolio_state(self, filepath: str) -> None:
        """Load portfolio state from file"""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        # Restore basic state
        if state.get('current_weights'):
            self.current_weights = np.array(state['current_weights'])
        
        # Restore constraints
        if 'constraints' in state:
            constraints_data = state['constraints']
            self.constraints.min_weight = constraints_data.get('min_weight', 0.0)
            self.constraints.max_weight = constraints_data.get('max_weight', 1.0)
            self.constraints.rebalancing_threshold = constraints_data.get('rebalancing_threshold', 0.05)
        
        logger.info(f"Portfolio state loaded from {filepath}")

# Demo function to test the portfolio manager
def demo_portfolio_manager():
    """Demonstrate AI Portfolio Manager functionality"""
    print("=== AI PORTFOLIO MANAGER DEMO ===")
    
    # Create sample assets
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    
    # Generate sample historical data
    def generate_sample_data(scenario='normal'):
        prices = 100 * (1 + np.random.normal(0, 0.02, len(dates))).cumprod()
        return pd.DataFrame({'close': prices}, index=dates)
    
    # Create sample assets
    sample_assets = [
        Asset(
            symbol='AAPL', name='Apple Inc.', asset_class='equity', sector='technology',
            region='US', market_cap=3000000000000, current_price=150.0,
            historical_data=generate_sample_data(), esg_score=7.5
        ),
        Asset(
            symbol='MSFT', name='Microsoft Corp.', asset_class='equity', sector='technology',
            region='US', market_cap=2500000000000, current_price=300.0,
            historical_data=generate_sample_data(), esg_score=8.2
        ),
        Asset(
            symbol='TSLA', name='Tesla Inc.', asset_class='equity', sector='automotive',
            region='US', market_cap=800000000000, current_price=200.0,
            historical_data=generate_sample_data(), esg_score=6.8
        ),
        Asset(
            symbol='JNJ', name='Johnson & Johnson', asset_class='equity', sector='healthcare',
            region='US', market_cap=450000000000, current_price=160.0,
            historical_data=generate_sample_data(), esg_score=9.1
        ),
        Asset(
            symbol='TLT', name='iShares 20+ Year Treasury', asset_class='bond', sector='government',
            region='US', market_cap=50000000000, current_price=100.0,
            historical_data=generate_sample_data(), esg_score=8.5
        )
    ]
    
    # Initialize portfolio manager
    pm = AIPortfolioManager()
    
    # Add assets
    for asset in sample_assets:
        pm.add_asset(asset)
    
    # Set constraints
    constraints = PortfolioConstraint(
        min_weight=0.05, max_weight=0.40,
        rebalancing_threshold=0.03
    )
    pm.set_constraints(constraints)
    
    # Set risk parameters
    risk_params = RiskParameters(
        var_confidence=0.95,
        max_portfolio_var=0.08,
        max_single_position=0.25
    )
    pm.set_risk_parameters(risk_params)
    
    print(f"Added {len(sample_assets)} assets to portfolio universe")
    
    # Optimize portfolio using different methods
    print("\n--- Mean Variance Optimization ---")
    weights_mv = pm.optimize_portfolio(method='mean_variance')
    metrics_mv = pm.calculate_portfolio_metrics()
    print(f"Annualized Return: {metrics_mv['annualized_return']:.4f}")
    print(f"Volatility: {metrics_mv['volatility']:.4f}")
    print(f"Sharpe Ratio: {metrics_mv['sharpe_ratio']:.4f}")
    
    print("\n--- Risk Parity Optimization ---")
    weights_rp = pm.optimize_portfolio(method='risk_parity')
    metrics_rp = pm.calculate_portfolio_metrics()
    print(f"Annualized Return: {metrics_rp['annualized_return']:.4f}")
    print(f"Volatility: {metrics_rp['volatility']:.4f}")
    print(f"Sharpe Ratio: {metrics_rp['sharpe_ratio']:.4f}")
    
    # Rebalance portfolio
    print("\n--- Portfolio Rebalancing ---")
    rebalance_result = pm.rebalance_portfolio(method='threshold')
    print(f"Rebalancing Action: {rebalance_result['action']}")
    if rebalance_result['action'] != 'no_rebalance':
        print(f"Number of Trades: {len(rebalance_result['trades'])}")
        print(f"Turnover: {rebalance_result['turnover']:.4f}")
    
    # Run stress tests
    print("\n--- Stress Testing ---")
    stress_results = pm.run_stress_test()
    for scenario, result in stress_results['stress_test_results'].items():
        print(f"{scenario}: {result:.4f}")
    
    # Performance attribution (if benchmark available)
    pm.benchmark_weights = np.ones(len(sample_assets)) / len(sample_assets)  # Equal weight benchmark
    print("\n--- Performance Attribution ---")
    attribution_report = pm.performance_attributor.full_attribution_analysis(
        np.array([asset.historical_data['close'].pct_change().dropna().values for asset in sample_assets]).T,
        pm.current_weights,
        pm.benchmark_weights,
        np.dot(np.array([asset.historical_data['close'].pct_change().dropna().values for asset in sample_assets]).T, pm.benchmark_weights)
    )
    print(f"Active Return: {attribution_report['active_return']:.4f}")
    print(f"Selection Effect: {attribution_report['selection_effect']:.4f}")
    print(f"Allocation Effect: {attribution_report['allocation_effect']:.4f}")
    
    # ESG Integration
    print("\n--- ESG Integration ---")
    esg_scores = np.array([asset.esg_score for asset in sample_assets]) / 10.0  # Normalize to 0-1
    esg_weights = pm.esg_integrator.esg_constraint_optimization(
        np.array([asset.historical_data['close'].pct_change().dropna().values for asset in sample_assets]).T,
        np.mean(np.array([asset.historical_data['close'].pct_change().dropna().values for asset in sample_assets]).T, axis=0),
        np.cov(np.array([asset.historical_data['close'].pct_change().dropna().values for asset in sample_assets]).T),
        esg_scores,
        min_esg_score=0.7
    )
    print("ESG-constrained optimization completed")
    
    # Generate comprehensive report
    print("\n--- Comprehensive Report ---")
    report = pm.generate_report(include_charts=False)
    print(report)
    
    print("\n=== DEMO COMPLETED ===")
    return pm

if __name__ == "__main__":
    # Run demo
    portfolio_manager = demo_portfolio_manager()
    
    # Save portfolio state
    portfolio_manager.save_portfolio_state("portfolio_state.json")
    print("\nPortfolio state saved successfully!")