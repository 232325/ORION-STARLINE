"""
Portfolio Optimizer Engine
Portfolio Optimization - Advanced Portfolio Management & Optimization

Features:
- Mean-Variance Optimization
- Black-Litterman Model
- Risk Parity Portfolio
- Minimum Variance Portfolio
- Maximum Sharpe Ratio Portfolio
- CVaR Optimization
- Dynamic Asset Allocation
- Rebalancing Strategies
- Performance Attribution
- Risk Budgeting
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from decimal import Decimal, ROUND_DOWN
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
import json
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

# Optimization
from scipy.optimize import minimize, differential_evolution
from scipy.linalg import LinAlgError
import cvxpy as cp

# Portfolio Theory
import quantstats as qs

# Risk Management
from sklearn.covariance import LedoitWolf, OAS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationMethod(Enum):
    """Optimizatsiya usullari"""
    MEAN_VARIANCE = "mean_variance"
    BLACK_LITTERMAN = "black_litterman"
    RISK_PARITY = "risk_parity"
    MINIMUM_VARIANCE = "minimum_variance"
    MAXIMUM_SHARPE = "maximum_sharpe"
    MAXIMUM_DIVERSIFICATION = "maximum_diversification"
    CVAR_OPTIMIZATION = "cvar_optimization"
    EQUAL_WEIGHTS = "equal_weights"
    MARKET_CAP = "market_cap"

class RebalanceFrequency(Enum):
    """Rebalancing chastotasi"""
    NEVER = "never"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    THRESHOLD = "threshold"

class RiskConstraint(Enum):
    """Risk cheklovlari"""
    MAX_VOLATILITY = "max_volatility"
    MAX_VAR = "max_var"
    MAX_CVAR = "max_cvar"
    MAX_DRAWDOWN = "max_drawdown"
    MAX_CONCENTRATION = "max_concentration"

@dataclass
class PortfolioConstraints:
    """Portfolio cheklovlari"""
    # Basic constraints
    min_weight: float = 0.0
    max_weight: float = 1.0
    max_single_asset: float = 0.3
    
    # Risk constraints
    max_volatility: Optional[float] = None
    max_var: Optional[float] = None
    max_cvar: Optional[float] = None
    max_drawdown: Optional[float] = None
    
    # Sector/Geographic constraints
    sector_limits: Dict[str, float] = field(default_factory=dict)
    region_limits: Dict[str, float] = field(default_factory=dict)
    
    # Transaction costs
    transaction_cost: float = 0.001  # 0.1%

@dataclass
class PortfolioWeights:
    """Portfolio vaznlar"""
    symbol: str
    weight: float
    allocation_value: float
    current_price: float
    quantity: float
    
@dataclass
class PortfolioOptimization:
    """Portfolio optimizatsiya natijasi"""
    method: OptimizationMethod
    weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    var_95: float
    cvar_95: float
    max_drawdown: float
    diversification_ratio: float
    
    # Optimization details
    objective_value: float
    constraints_satisfied: bool
    optimization_time: float
    
    # Additional metrics
    effective_number: float  # Effective number of assets
    concentration_risk: float
    turnover: Optional[float] = None
    
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PortfolioPerformance:
    """Portfolio performance"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    
    # Risk metrics
    var_95: float
    cvar_95: float
    beta: Optional[float] = None
    alpha: Optional[float] = None
    
    # Attribution
    return_attribution: Dict[str, float] = field(default_factory=dict)
    risk_attribution: Dict[str, float] = field(default_factory=dict)
    
    # Period analysis
    daily_returns: List[float] = field(default_factory=list)
    rolling_metrics: Dict[str, List[float]] = field(default_factory=dict)

@dataclass
class RebalanceRecommendation:
    """Rebalancing tavsiyasi"""
    current_weights: Dict[str, float]
    target_weights: Dict[str, float]
    trades: List[Dict[str, Any]]
    estimated_cost: float
    expected_improvement: float
    rebalance_reason: str
    
    timestamp: datetime = field(default_factory=datetime.now)

class PortfolioOptimizer:
    """Portfolio Optimization Engine"""
    
    def __init__(self, 
                 risk_free_rate: float = 0.02,
                 confidence_level: float = 0.95):
        """
        Args:
            risk_free_rate: Risk-free rate (annual)
            confidence_level: Confidence level for risk calculations
        """
        self.risk_free_rate = risk_free_rate
        self.confidence_level = confidence_level
        
        # Data storage
        self.returns_data = {}
        self.covariance_matrix = {}
        self.expected_returns = {}
        
        # Optimization cache
        self.optimization_cache = {}
        
        # Thread pool
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("Portfolio Optimizer Engine initialized")
    
    async def optimize_portfolio(self,
                               symbols: List[str],
                               returns_data: pd.DataFrame,
                               method: OptimizationMethod = OptimizationMethod.MEAN_VARIANCE,
                               constraints: Optional[PortfolioConstraints] = None,
                               risk_aversion: float = 1.0) -> PortfolioOptimization:
        """
        Portfolio optimizatsiya
        
        Args:
            symbols: Asset symbols
            returns_data: Historical returns data
            method: Optimization method
            constraints: Portfolio constraints
            risk_aversion: Risk aversion parameter
            
        Returns:
            PortfolioOptimization: Optimization results
        """
        try:
            logger.info(f"Optimizing portfolio with {method.value} method")
            
            if constraints is None:
                constraints = PortfolioConstraints()
            
            # Prepare data
            asset_returns = returns_data[symbols].dropna()
            n_assets = len(symbols)
            
            if n_assets == 0:
                raise ValueError("No assets found")
            
            # Calculate expected returns and covariance
            expected_returns = asset_returns.mean().values
            covariance_matrix = asset_returns.cov().values
            
            # Handle ill-conditioned covariance matrix
            try:
                covariance_matrix = self._regularize_covariance(covariance_matrix)
            except Exception as e:
                logger.warning(f"Covariance regularization failed: {e}")
            
            # Run optimization based on method
            start_time = datetime.now()
            
            if method == OptimizationMethod.MEAN_VARIANCE:
                result = await self._optimize_mean_variance(
                    expected_returns, covariance_matrix, constraints, risk_aversion
                )
            elif method == OptimizationMethod.RISK_PARITY:
                result = await self._optimize_risk_parity(
                    expected_returns, covariance_matrix, constraints
                )
            elif method == OptimizationMethod.MINIMUM_VARIANCE:
                result = await self._optimize_minimum_variance(
                    expected_returns, covariance_matrix, constraints
                )
            elif method == OptimizationMethod.MAXIMUM_SHARPE:
                result = await self._optimize_maximum_sharpe(
                    expected_returns, covariance_matrix, constraints
                )
            elif method == OptimizationMethod.EQUAL_WEIGHTS:
                result = await self._optimize_equal_weights(
                    symbols, expected_returns, covariance_matrix
                )
            elif method == OptimizationMethod.BLACK_LITTERMAN:
                result = await self._optimize_black_litterman(
                    symbols, expected_returns, covariance_matrix, constraints
                )
            else:
                raise ValueError(f"Optimization method {method.value} not implemented")
            
            optimization_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate additional metrics
            weights_dict = dict(zip(symbols, result))
            
            portfolio_return = np.dot(weights_dict, expected_returns)
            portfolio_variance = np.dot(weights_dict, np.dot(covariance_matrix, weights_dict))
            portfolio_volatility = np.sqrt(portfolio_variance)
            portfolio_sharpe = (portfolio_return - self.risk_free_rate) / portfolio_volatility
            
            # Risk metrics
            portfolio_var = self._calculate_var(returns_data[symbols] @ pd.Series(weights_dict))
            portfolio_cvar = self._calculate_cvar(returns_data[symbols] @ pd.Series(weights_dict))
            portfolio_dd = self._calculate_max_drawdown(returns_data[symbols] @ pd.Series(weights_dict))
            
            # Diversification metrics
            div_ratio = self._calculate_diversification_ratio(weights_dict, covariance_matrix)
            effective_assets = 1 / np.sum(np.array(list(weights_dict.values()))**2)
            concentration = max(weights_dict.values())
            
            # Create result
            optimization_result = PortfolioOptimization(
                method=method,
                weights=weights_dict,
                expected_return=portfolio_return,
                expected_volatility=portfolio_volatility,
                sharpe_ratio=portfolio_sharpe,
                var_95=portfolio_var,
                cvar_95=portfolio_cvar,
                max_drawdown=portfolio_dd,
                diversification_ratio=div_ratio,
                objective_value=0,  # Would need to calculate based on objective function
                constraints_satisfied=self._check_constraints(weights_dict, constraints),
                optimization_time=optimization_time,
                effective_number=effective_assets,
                concentration_risk=concentration
            )
            
            logger.info(f"Portfolio optimization completed in {optimization_time:.2f}s")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Portfolio optimization failed: {e}")
            raise
    
    async def _optimize_mean_variance(self,
                                    expected_returns: np.ndarray,
                                    covariance_matrix: np.ndarray,
                                    constraints: PortfolioConstraints,
                                    risk_aversion: float) -> np.ndarray:
        """Mean-Variance optimization"""
        try:
            n_assets = len(expected_returns)
            
            # Define variables
            weights = cp.Variable(n_assets)
            
            # Objective function: maximize utility = return - (risk_aversion/2) * variance
            portfolio_return = expected_returns.T @ weights
            portfolio_variance = cp.quad_form(weights, covariance_matrix)
            objective = portfolio_return - (risk_aversion / 2) * portfolio_variance
            
            # Constraints
            constraints_list = [
                cp.sum(weights) == 1,  # Weights sum to 1
                weights >= constraints.min_weight,
                weights <= constraints.max_weight
            ]
            
            # Add concentration constraint
            if constraints.max_single_asset < 1.0:
                constraints_list.append(weights <= constraints.max_single_asset)
            
            # Add risk constraints
            if constraints.max_volatility:
                portfolio_variance = cp.quad_form(weights, covariance_matrix)
                constraints_list.append(portfolio_variance <= constraints.max_volatility**2)
            
            # Solve optimization problem
            problem = cp.Problem(cp.Maximize(objective), constraints_list)
            problem.solve(verbose=False)
            
            if problem.status not in ["infeasible", "unbounded"]:
                return weights.value
            else:
                logger.warning(f"Mean-variance optimization failed: {problem.status}")
                return np.ones(n_assets) / n_assets  # Fallback to equal weights
                
        except Exception as e:
            logger.error(f"Mean-variance optimization failed: {e}")
            return np.ones(len(expected_returns)) / len(expected_returns)
    
    async def _optimize_risk_parity(self,
                                  expected_returns: np.ndarray,
                                  covariance_matrix: np.ndarray,
                                  constraints: PortfolioConstraints) -> np.ndarray:
        """Risk Parity optimization"""
        try:
            n_assets = len(expected_returns)
            
            # Define variables
            weights = cp.Variable(n_assets)
            risk_contrib = cp.Variable(n_assets)
            
            # Risk parity constraint: each asset contributes equally to portfolio risk
            portfolio_variance = cp.quad_form(weights, covariance_matrix)
            
            constraints_list = [
                cp.sum(weights) == 1,
                weights >= constraints.min_weight,
                weights <= constraints.max_weight
            ]
            
            # Risk contribution constraints
            for i in range(n_assets):
                constraints_list.append(
                    risk_contrib[i] == weights[i] * (covariance_matrix[i, :] @ weights) / portfolio_variance
                )
            
            # Equal risk contribution constraint
            for i in range(n_assets - 1):
                constraints_list.append(risk_contrib[i] == risk_contrib[i + 1])
            
            # Objective: minimize deviation from equal risk contribution
            target_risk_contrib = 1.0 / n_assets
            objective = cp.sum_squares(risk_contrib - target_risk_contrib)
            
            problem = cp.Problem(cp.Minimize(objective), constraints_list)
            problem.solve(verbose=False)
            
            if problem.status not in ["infeasible", "unbounded"]:
                return weights.value
            else:
                logger.warning(f"Risk parity optimization failed: {problem.status}")
                return np.ones(n_assets) / n_assets
                
        except Exception as e:
            logger.error(f"Risk parity optimization failed: {e}")
            return np.ones(len(expected_returns)) / len(expected_returns)
    
    async def _optimize_minimum_variance(self,
                                       expected_returns: np.ndarray,
                                       covariance_matrix: np.ndarray,
                                       constraints: PortfolioConstraints) -> np.ndarray:
        """Minimum Variance optimization"""
        try:
            n_assets = len(expected_returns)
            
            weights = cp.Variable(n_assets)
            portfolio_variance = cp.quad_form(weights, covariance_matrix)
            
            constraints_list = [
                cp.sum(weights) == 1,
                weights >= constraints.min_weight,
                weights <= constraints.max_weight
            ]
            
            if constraints.max_single_asset < 1.0:
                constraints_list.append(weights <= constraints.max_single_asset)
            
            problem = cp.Problem(cp.Minimize(portfolio_variance), constraints_list)
            problem.solve(verbose=False)
            
            if problem.status not in ["infeasible", "unbounded"]:
                return weights.value
            else:
                logger.warning(f"Minimum variance optimization failed: {problem.status}")
                return np.ones(n_assets) / n_assets
                
        except Exception as e:
            logger.error(f"Minimum variance optimization failed: {e}")
            return np.ones(len(expected_returns)) / len(expected_returns)
    
    async def _optimize_maximum_sharpe(self,
                                     expected_returns: np.ndarray,
                                     covariance_matrix: np.ndarray,
                                     constraints: PortfolioConstraints) -> np.ndarray:
        """Maximum Sharpe Ratio optimization"""
        try:
            n_assets = len(expected_returns)
            
            weights = cp.Variable(n_assets)
            portfolio_return = expected_returns.T @ weights
            portfolio_variance = cp.quad_form(weights, covariance_matrix)
            
            # Objective: maximize Sharpe ratio = (return - rf) / std
            # Equivalent to minimizing variance for given return
            target_return = np.max(expected_returns)  # Target high return
            
            constraints_list = [
                cp.sum(weights) == 1,
                portfolio_return >= target_return * 0.8,  # At least 80% of max return
                weights >= constraints.min_weight,
                weights <= constraints.max_weight
            ]
            
            if constraints.max_single_asset < 1.0:
                constraints_list.append(weights <= constraints.max_single_asset)
            
            problem = cp.Problem(cp.Minimize(portfolio_variance), constraints_list)
            problem.solve(verbose=False)
            
            if problem.status not in ["infeasible", "unbounded"]:
                return weights.value
            else:
                logger.warning(f"Maximum Sharpe optimization failed: {problem.status}")
                return np.ones(n_assets) / n_assets
                
        except Exception as e:
            logger.error(f"Maximum Sharpe optimization failed: {e}")
            return np.ones(len(expected_returns)) / len(expected_returns)
    
    async def _optimize_equal_weights(self,
                                    symbols: List[str],
                                    expected_returns: np.ndarray,
                                    covariance_matrix: np.ndarray) -> np.ndarray:
        """Equal weights portfolio"""
        return np.ones(len(symbols)) / len(symbols)
    
    async def _optimize_black_litterman(self,
                                      symbols: List[str],
                                      expected_returns: np.ndarray,
                                      covariance_matrix: np.ndarray,
                                      constraints: PortfolioConstraints) -> np.ndarray:
        """Black-Litterman model (simplified implementation)"""
        try:
            # Simplified Black-Litterman with market equilibrium
            n_assets = len(symbols)
            
            # Market capitalization weights (simplified - equal weights)
            market_weights = np.ones(n_assets) / n_assets
            
            # Risk aversion parameter
            risk_aversion = 2.5
            
            # Calculate implied returns
            implied_returns = risk_aversion * np.dot(covariance_matrix, market_weights)
            
            # Combine with historical returns (simplified)
            tau = 0.025  # Confidence parameter
            adjusted_returns = (1 - tau) * expected_returns + tau * implied_returns
            
            # Use mean-variance optimization with adjusted returns
            return await self._optimize_mean_variance(
                adjusted_returns, covariance_matrix, constraints, risk_aversion
            )
            
        except Exception as e:
            logger.error(f"Black-Litterman optimization failed: {e}")
            return np.ones(len(expected_returns)) / len(expected_returns)
    
    def _regularize_covariance(self, covariance_matrix: np.ndarray, shrinkage: str = 'ledoit_wolf') -> np.ndarray:
        """Covariance matrix regularization"""
        try:
            if shrinkage == 'ledoit_wolf':
                lw = LedoitWolf()
                shrunk_cov = lw.fit(covariance_matrix).covariance_
                return shrunk_cov
            elif shrinkage == 'oas':
                oas = OAS()
                shrunk_cov = oas.fit(covariance_matrix).covariance_
                return shrunk_cov
            else:
                # Add small regularization to diagonal
                regularized = covariance_matrix.copy()
                np.fill_diagonal(regularized, np.diag(regularized) + 1e-6)
                return regularized
                
        except Exception as e:
            logger.warning(f"Covariance regularization failed: {e}")
            return covariance_matrix + np.eye(len(covariance_matrix)) * 1e-6
    
    def _calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Value at Risk calculation"""
        try:
            var = np.percentile(returns, (1 - confidence_level) * 100)
            return abs(var)
        except Exception as e:
            logger.warning(f"VaR calculation failed: {e}")
            return 0.0
    
    def _calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Conditional Value at Risk calculation"""
        try:
            var = self._calculate_var(returns, confidence_level)
            cvar = abs(returns[returns <= var].mean())
            return cvar
        except Exception as e:
            logger.warning(f"CVaR calculation failed: {e}")
            return 0.0
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Maximum drawdown calculation"""
        try:
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            return abs(drawdown.min())
        except Exception as e:
            logger.warning(f"Max drawdown calculation failed: {e}")
            return 0.0
    
    def _calculate_diversification_ratio(self, 
                                       weights: Dict[str, float], 
                                       covariance_matrix: np.ndarray) -> float:
        """Diversification ratio calculation"""
        try:
            weights_array = np.array(list(weights.values()))
            portfolio_variance = np.dot(weights_array, np.dot(covariance_matrix, weights_array))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            weighted_volatilities = []
            for i, weight in enumerate(weights_array):
                asset_vol = np.sqrt(covariance_matrix[i, i])
                weighted_volatilities.append(weight * asset_vol)
            
            weighted_avg_vol = sum(weighted_volatilities)
            
            if weighted_avg_vol > 0:
                div_ratio = weighted_avg_vol / portfolio_volatility
            else:
                div_ratio = 1.0
            
            return div_ratio
            
        except Exception as e:
            logger.warning(f"Diversification ratio calculation failed: {e}")
            return 1.0
    
    def _check_constraints(self, 
                         weights: Dict[str, float], 
                         constraints: PortfolioConstraints) -> bool:
        """Check if constraints are satisfied"""
        try:
            # Basic constraints
            if any(w < constraints.min_weight for w in weights.values()):
                return False
            
            if any(w > constraints.max_weight for w in weights.values()):
                return False
            
            if any(w > constraints.max_single_asset for w in weights.values()):
                return False
            
            # Sum check
            if abs(sum(weights.values()) - 1.0) > 1e-6:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Constraint check failed: {e}")
            return False
    
    async def calculate_portfolio_performance(self,
                                            portfolio_returns: pd.Series,
                                            benchmark_returns: Optional[pd.Series] = None) -> PortfolioPerformance:
        """
        Portfolio performance hisoblash
        
        Args:
            portfolio_returns: Portfolio daily returns
            benchmark_returns: Benchmark returns for comparison
            
        Returns:
            PortfolioPerformance: Performance metrics
        """
        try:
            logger.info("Calculating portfolio performance")
            
            # Basic performance metrics
            total_return = (1 + portfolio_returns).prod() - 1
            annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
            volatility = portfolio_returns.std() * np.sqrt(252)
            
            # Risk-adjusted metrics
            excess_returns = portfolio_returns - self.risk_free_rate / 252
            sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
            
            # Downside deviation for Sortino ratio
            downside_returns = portfolio_returns[portfolio_returns < 0]
            downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino_ratio = annualized_return / downside_deviation if downside_deviation > 0 else 0
            
            # Maximum drawdown
            max_dd = self._calculate_max_drawdown(portfolio_returns)
            calmar_ratio = annualized_return / max_dd if max_dd > 0 else 0
            
            # Risk metrics
            var_95 = self._calculate_var(portfolio_returns, 0.95)
            cvar_95 = self._calculate_cvar(portfolio_returns, 0.95)
            
            # Beta and Alpha (if benchmark provided)
            beta = None
            alpha = None
            if benchmark_returns is not None:
                # Align data
                common_index = portfolio_returns.index.intersection(benchmark_returns.index)
                portfolio_aligned = portfolio_returns[common_index]
                benchmark_aligned = benchmark_returns[common_index]
                
                if len(common_index) > 1:
                    covariance = np.cov(portfolio_aligned, benchmark_aligned)[0, 1]
                    benchmark_variance = np.var(benchmark_aligned)
                    beta = covariance / benchmark_variance if benchmark_variance > 0 else None
                    
                    if beta is not None:
                        alpha = annualized_return - beta * (1 + self.risk_free_rate) + self.risk_free_rate
            
            # Rolling metrics
            rolling_sharpe = self._calculate_rolling_sharpe(portfolio_returns)
            rolling_vol = self._calculate_rolling_volatility(portfolio_returns)
            
            performance_result = PortfolioPerformance(
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                max_drawdown=max_dd,
                calmar_ratio=calmar_ratio,
                var_95=var_95,
                cvar_95=cvar_95,
                beta=beta,
                alpha=alpha,
                daily_returns=portfolio_returns.tolist(),
                rolling_metrics={
                    'sharpe_ratio': rolling_sharpe,
                    'volatility': rolling_vol
                }
            )
            
            logger.info("Portfolio performance calculated successfully")
            return performance_result
            
        except Exception as e:
            logger.error(f"Portfolio performance calculation failed: {e}")
            raise
    
    def _calculate_rolling_sharpe(self, returns: pd.Series, window: int = 252) -> List[float]:
        """Rolling Sharpe ratio calculation"""
        try:
            rolling_sharpe = []
            for i in range(len(returns)):
                if i >= window - 1:
                    window_returns = returns.iloc[i-window+1:i+1]
                    excess_returns = window_returns - self.risk_free_rate / 252
                    sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
                    rolling_sharpe.append(sharpe)
                else:
                    rolling_sharpe.append(np.nan)
            
            return rolling_sharpe
            
        except Exception as e:
            logger.warning(f"Rolling Sharpe calculation failed: {e}")
            return []
    
    def _calculate_rolling_volatility(self, returns: pd.Series, window: int = 252) -> List[float]:
        """Rolling volatility calculation"""
        try:
            rolling_vol = returns.rolling(window).std() * np.sqrt(252)
            return rolling_vol.tolist()
            
        except Exception as e:
            logger.warning(f"Rolling volatility calculation failed: {e}")
            return []
    
    async def generate_rebalance_recommendation(self,
                                              current_weights: Dict[str, float],
                                              target_weights: Dict[str, float],
                                              current_prices: Dict[str, float],
                                              portfolio_value: float,
                                              constraints: PortfolioConstraints,
                                              threshold: float = 0.05) -> RebalanceRecommendation:
        """
        Rebalancing tavsiya yaratish
        
        Args:
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights
            current_prices: Current asset prices
            portfolio_value: Total portfolio value
            constraints: Portfolio constraints
            threshold: Rebalancing threshold (5%)
            
        Returns:
            RebalanceRecommendation: Rebalancing recommendation
        """
        try:
            logger.info("Generating rebalancing recommendation")
            
            # Calculate weight differences
            weight_differences = {}
            for symbol in target_weights.keys():
                current_weight = current_weights.get(symbol, 0.0)
                target_weight = target_weights[symbol]
                weight_differences[symbol] = target_weight - current_weight
            
            # Identify trades needed (above threshold)
            trades = []
            total_trade_value = 0
            
            for symbol, weight_diff in weight_differences.items():
                if abs(weight_diff) >= threshold:
                    trade_value = weight_diff * portfolio_value
                    current_price = current_prices.get(symbol, 0)
                    quantity = trade_value / current_price if current_price > 0 else 0
                    
                    trades.append({
                        'symbol': symbol,
                        'action': 'buy' if weight_diff > 0 else 'sell',
                        'current_weight': current_weights.get(symbol, 0.0),
                        'target_weight': target_weights[symbol],
                        'weight_difference': weight_diff,
                        'trade_value': trade_value,
                        'quantity': quantity,
                        'current_price': current_price
                    })
                    
                    total_trade_value += abs(trade_value)
            
            # Calculate transaction costs
            estimated_cost = total_trade_value * constraints.transaction_cost
            
            # Estimate expected improvement (simplified)
            # This would need more sophisticated calculation in reality
            expected_improvement = sum(abs(w_diff) * 0.1 for w_diff in weight_differences.values())  # 10% improvement per % rebalanced
            
            # Determine rebalance reason
            rebalance_reason = "Periodic rebalancing"
            if max(abs(w_diff) for w_diff in weight_differences.values()) > 0.1:
                rebalance_reason = "Significant drift detected"
            
            recommendation = RebalanceRecommendation(
                current_weights=current_weights,
                target_weights=target_weights,
                trades=trades,
                estimated_cost=estimated_cost,
                expected_improvement=expected_improvement,
                rebalance_reason=rebalance_reason
            )
            
            logger.info(f"Rebalancing recommendation generated: {len(trades)} trades")
            return recommendation
            
        except Exception as e:
            logger.error(f"Rebalancing recommendation failed: {e}")
            raise
    
    async def backtest_portfolio_strategy(self,
                                        symbols: List[str],
                                        returns_data: pd.DataFrame,
                                        optimization_method: OptimizationMethod,
                                        rebalance_frequency: RebalanceFrequency,
                                        constraints: Optional[PortfolioConstraints] = None,
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Portfolio strategy backtesting
        
        Args:
            symbols: Asset symbols
            returns_data: Historical returns data
            optimization_method: Optimization method
            rebalance_frequency: Rebalancing frequency
            constraints: Portfolio constraints
            start_date: Backtest start date
            end_date: Backtest end date
            
        Returns:
            Dict: Backtest results
        """
        try:
            logger.info(f"Backtesting portfolio strategy: {optimization_method.value}")
            
            if constraints is None:
                constraints = PortfolioConstraints()
            
            # Filter data by date range
            if start_date or end_date:
                mask = pd.Series(True, index=returns_data.index)
                if start_date:
                    mask = mask & (returns_data.index >= start_date)
                if end_date:
                    mask = mask & (returns_data.index <= end_date)
                returns_data = returns_data[mask]
            
            # Initialize tracking
            portfolio_weights_history = []
            portfolio_returns_history = []
            rebalance_dates = []
            
            current_weights = {symbol: 1.0/len(symbols) for symbol in symbols}  # Equal weights start
            
            # Run backtest
            rebalance_period = self._get_rebalance_period(rebalance_frequency)
            last_rebalance = returns_data.index[0] if len(returns_data) > 0 else None
            
            for i, (date, row) in enumerate(returns_data.iterrows()):
                # Check if rebalancing is needed
                if (last_rebalance is None or 
                    (date - last_rebalance).days >= rebalance_period or
                    self._needs_threshold_rebalance(current_weights, {symbol: row[symbol] for symbol in symbols})):
                    
                    # Optimize portfolio
                    optimization_result = await self.optimize_portfolio(
                        symbols, 
                        returns_data.iloc[:i+1], 
                        optimization_method, 
                        constraints
                    )
                    
                    current_weights = optimization_result.weights
                    last_rebalance = date
                    rebalance_dates.append(date)
                    logger.info(f"Rebalanced on {date.strftime('%Y-%m-%d')}: {len(current_weights)} assets")
                
                # Calculate portfolio return for this period
                portfolio_return = sum(current_weights[symbol] * row[symbol] for symbol in symbols if symbol in row)
                portfolio_returns_history.append(portfolio_return)
                portfolio_weights_history.append(current_weights.copy())
            
            # Convert to DataFrame
            portfolio_returns = pd.Series(portfolio_returns_history, index=returns_data.index)
            
            # Calculate performance
            performance = await self.calculate_portfolio_performance(portfolio_returns)
            
            # Calculate turnover
            if len(portfolio_weights_history) > 1:
                turnover = self._calculate_turnover(portfolio_weights_history)
            else:
                turnover = 0.0
            
            # Compile results
            backtest_results = {
                'portfolio_returns': portfolio_returns,
                'performance_metrics': performance,
                'rebalance_dates': rebalance_dates,
                'weights_history': portfolio_weights_history,
                'final_weights': current_weights,
                'turnover': turnover,
                'optimization_method': optimization_method.value,
                'rebalance_frequency': rebalance_frequency.value,
                'total_periods': len(returns_data),
                'rebalance_count': len(rebalance_dates)
            }
            
            logger.info(f"Backtest completed: {len(portfolio_returns)} periods, {len(rebalance_dates)} rebalances")
            return backtest_results
            
        except Exception as e:
            logger.error(f"Portfolio backtesting failed: {e}")
            raise
    
    def _get_rebalance_period(self, frequency: RebalanceFrequency) -> int:
        """Get rebalance period in days"""
        period_map = {
            RebalanceFrequency.NEVER: 999999,
            RebalanceFrequency.DAILY: 1,
            RebalanceFrequency.WEEKLY: 7,
            RebalanceFrequency.MONTHLY: 30,
            RebalanceFrequency.QUARTERLY: 90,
            RebalanceFrequency.ANNUALLY: 365,
            RebalanceFrequency.THRESHOLD: 30  # Default when using threshold
        }
        return period_map.get(frequency, 30)
    
    def _needs_threshold_rebalance(self, 
                                 current_weights: Dict[str, float], 
                                 new_weights: Dict[str, float],
                                 threshold: float = 0.05) -> bool:
        """Check if rebalancing needed due to threshold"""
        try:
            for symbol in current_weights.keys():
                current_weight = current_weights[symbol]
                target_weight = new_weights.get(symbol, 0.0)
                if abs(current_weight - target_weight) > threshold:
                    return True
            return False
            
        except Exception as e:
            return False
    
    def _calculate_turnover(self, weights_history: List[Dict[str, float]]) -> float:
        """Calculate portfolio turnover"""
        try:
            total_turnover = 0
            for i in range(1, len(weights_history)):
                current = weights_history[i]
                previous = weights_history[i-1]
                
                period_turnover = sum(abs(current.get(symbol, 0) - previous.get(symbol, 0)) 
                                    for symbol in current.keys())
                total_turnover += period_turnover
            
            return total_turnover / (len(weights_history) - 1) if len(weights_history) > 1 else 0
            
        except Exception as e:
            return 0.0
    
    async def analyze_risk_contribution(self,
                                      weights: Dict[str, float],
                                      covariance_matrix: np.ndarray) -> Dict[str, float]:
        """Risk contribution analysis"""
        try:
            weights_array = np.array(list(weights.values()))
            portfolio_variance = np.dot(weights_array, np.dot(covariance_matrix, weights_array))
            
            risk_contributions = {}
            for i, symbol in enumerate(weights.keys()):
                marginal_contrib = np.sum(weights_array[i] * covariance_matrix[i, :])
                risk_contrib = weights_array[i] * marginal_contrib / portfolio_variance
                risk_contributions[symbol] = risk_contrib
            
            return risk_contributions
            
        except Exception as e:
            logger.error(f"Risk contribution analysis failed: {e}")
            return {}
    
    async def cleanup(self):
        """Resurslarni tozalash"""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            
            # Clear caches
            self.returns_data.clear()
            self.covariance_matrix.clear()
            self.expected_returns.clear()
            self.optimization_cache.clear()
            
            logger.info("Portfolio Optimizer cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

# Test function
async def test_portfolio_optimizer():
    """Test Portfolio Optimizer Engine"""
    try:
        print("💼 Portfolio Optimizer Engine Test")
        print("=" * 50)
        
        # Initialize engine
        optimizer = PortfolioOptimizer()
        
        # Create sample data
        np.random.seed(42)
        n_assets = 5
        n_periods = 252
        
        symbols = ["BTC", "ETH", "ADA", "DOT", "LINK"]
        
        # Generate correlated returns
        base_returns = np.random.multivariate_normal(
            mean=np.array([0.001] * n_assets),
            cov=np.array([[1, 0.3, 0.2, 0.1, 0.15],
                         [0.3, 1, 0.25, 0.12, 0.18],
                         [0.2, 0.25, 1, 0.15, 0.1],
                         [0.1, 0.12, 0.15, 1, 0.2],
                         [0.15, 0.18, 0.1, 0.2, 1]]) * 0.02,
            size=n_periods
        )
        
        dates = pd.date_range(start='2023-01-01', periods=n_periods, freq='D')
        returns_data = pd.DataFrame(base_returns, index=dates, columns=symbols)
        
        print(f"📊 Sample Portfolio Data Created:")
        print(f"  Assets: {symbols}")
        print(f"  Period: {dates[0].date()} to {dates[-1].date()}")
        print(f"  Data Points: {len(returns_data)}")
        
        # Create constraints
        constraints = PortfolioConstraints(
            min_weight=0.05,
            max_weight=0.6,
            max_single_asset=0.4,
            max_volatility=0.25
        )
        
        # Test different optimization methods
        methods = [
            OptimizationMethod.EQUAL_WEIGHTS,
            OptimizationMethod.MINIMUM_VARIANCE,
            OptimizationMethod.RISK_PARITY,
            OptimizationMethod.MEAN_VARIANCE
        ]
        
        print(f"\n🔧 Portfolio Optimization Results:")
        optimization_results = {}
        
        for method in methods:
            print(f"\n--- {method.value.upper()} ---")
            
            result = await optimizer.optimize_portfolio(
                symbols, 
                returns_data, 
                method, 
                constraints
            )
            
            optimization_results[method.value] = result
            
            print(f"  Expected Return: {result.expected_return:.2%}")
            print(f"  Volatility: {result.expected_volatility:.2%}")
            print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
            print(f"  VaR (95%): {result.var_95:.2%}")
            print(f"  Max Drawdown: {result.max_drawdown:.2%}")
            print(f"  Diversification Ratio: {result.diversification_ratio:.2f}")
            print(f"  Effective Assets: {result.effective_number:.1f}")
            print(f"  Top Holdings:")
            
            sorted_weights = sorted(result.weights.items(), key=lambda x: x[1], reverse=True)
            for symbol, weight in sorted_weights[:3]:
                print(f"    {symbol}: {weight:.1%}")
        
        # Test performance calculation
        print(f"\n📈 Performance Analysis Test:")
        
        # Use Mean Variance results
        mv_weights = optimization_results[OptimizationMethod.MEAN_VARIANCE.value].weights
        
        # Calculate portfolio returns
        portfolio_returns = (returns_data * pd.Series(mv_weights)).sum(axis=1)
        
        performance = await optimizer.calculate_portfolio_performance(portfolio_returns)
        
        print(f"  Total Return: {performance.total_return:.2%}")
        print(f"  Annualized Return: {performance.annualized_return:.2%}")
        print(f"  Volatility: {performance.volatility:.2%}")
        print(f"  Sharpe Ratio: {performance.sharpe_ratio:.2f}")
        print(f"  Sortino Ratio: {performance.sortino_ratio:.2f}")
        print(f"  Max Drawdown: {performance.max_drawdown:.2%}")
        print(f"  Calmar Ratio: {performance.calmar_ratio:.2f}")
        print(f"  VaR (95%): {performance.var_95:.2%}")
        print(f"  CVaR (95%): {performance.cvar_95:.2%}")
        
        # Test rebalancing recommendation
        print(f"\n🔄 Rebalancing Recommendation Test:")
        
        current_weights = {symbol: 0.2 for symbol in symbols}  # Equal weights
        target_weights = mv_weights
        current_prices = {symbol: np.random.uniform(100, 1000) for symbol in symbols}
        portfolio_value = 100000
        
        rebalance_rec = await optimizer.generate_rebalance_recommendation(
            current_weights,
            target_weights,
            current_prices,
            portfolio_value,
            constraints
        )
        
        print(f"  Rebalance Reason: {rebalance_rec.rebalance_reason}")
        print(f"  Number of Trades: {len(rebalance_rec.trades)}")
        print(f"  Estimated Cost: ${rebalance_rec.estimated_cost:,.2f}")
        print(f"  Expected Improvement: {rebalance_rec.expected_improvement:.1%}")
        
        if rebalance_rec.trades:
            print(f"  Top Trades:")
            for trade in sorted(rebalance_rec.trades, key=lambda x: abs(x['weight_difference']), reverse=True)[:3]:
                print(f"    {trade['action'].upper()} {trade['symbol']}: {trade['weight_difference']:+.1%}")
        
        # Test backtesting
        print(f"\n⏰ Backtesting Test:")
        
        backtest_results = await optimizer.backtest_portfolio_strategy(
            symbols,
            returns_data,
            OptimizationMethod.RISK_PARITY,
            RebalanceFrequency.MONTHLY,
            constraints
        )
        
        perf = backtest_results['performance_metrics']
        print(f"  Strategy: {backtest_results['optimization_method']}")
        print(f"  Rebalance Frequency: {backtest_results['rebalance_frequency']}")
        print(f"  Total Periods: {backtest_results['total_periods']}")
        print(f"  Rebalance Count: {backtest_results['rebalance_count']}")
        print(f"  Portfolio Turnover: {backtest_results['turnover']:.1%}")
        print(f"  Final Total Return: {perf.total_return:.2%}")
        print(f"  Final Sharpe Ratio: {perf.sharpe_ratio:.2f}")
        print(f"  Final Max Drawdown: {perf.max_drawdown:.2%}")
        
        # Test risk contribution analysis
        print(f"\n⚠️ Risk Contribution Analysis Test:")
        
        risk_contrib = await optimizer.analyze_risk_contribution(
            mv_weights,
            returns_data.cov().values
        )
        
        print(f"  Risk Contributions:")
        sorted_risk = sorted(risk_contrib.items(), key=lambda x: x[1], reverse=True)
        for symbol, contrib in sorted_risk:
            print(f"    {symbol}: {contrib:.1%}")
        
        await optimizer.cleanup()
        
        print("\n✅ Portfolio Optimizer Engine test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_portfolio_optimizer())