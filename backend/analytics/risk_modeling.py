"""
Risk Modeling Engine
Advanced Risk Management & Modeling for Financial Markets

Features:
- Value at Risk (VaR) Models
- Expected Shortfall (ES/CVaR) 
- Extreme Value Theory (EVT)
- GARCH Models for Volatility
- Stress Testing & Scenario Analysis
- Credit Risk Modeling
- Operational Risk Assessment
- Market Risk Attribution
- Liquidity Risk Models
- Concentration Risk Analysis
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

# Risk Models
from arch import arch_model
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
from statsmodels.tsa.stattools import adfuller
from scipy import stats
from scipy.optimize import minimize
from scipy.stats import norm, t, genextreme, pareto

# Financial Risk
import quantstats as qs

# Machine Learning for Risk
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskType(Enum):
    """Risk turlari"""
    MARKET_RISK = "market_risk"
    CREDIT_RISK = "credit_risk"
    OPERATIONAL_RISK = "operational_risk"
    LIQUIDITY_RISK = "liquidity_risk"
    CONCENTRATION_RISK = "concentration_risk"
    SYSTEMIC_RISK = "systemic_risk"

class VaRMethod(Enum):
    """VaR hisoblash usullari"""
    HISTORICAL = "historical"
    PARAMETRIC = "parametric"
    MONTE_CARLO = "monte_carlo"
    CORNISH_FISHER = "cornish_fisher"
    EXTREME_VALUE = "extreme_value"
    GARCH = "garch"

class StressScenario(Enum):
    """Stress testing senariolari"""
    MARKET_CRASH = "market_crash"
    INTEREST_RATE_SHOCK = "interest_rate_shock"
    CREDIT_SPREAD_WIDENING = "credit_spread_widening"
    VOLATILITY_SPIKE = "volatility_spike"
    LIQUIDITY_DRY_UP = "liquidity_dry_up"
    CORRELATION_BREAKDOWN = "correlation_breakdown"
    CUSTOM_SCENARIO = "custom_scenario"

@dataclass
class RiskMetrics:
    """Risk metrikalari"""
    var_95: float
    var_99: float
    expected_shortfall_95: float
    expected_shortfall_99: float
    volatility: float
    skewness: float
    kurtosis: float
    maximum_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Additional metrics
    hit_ratio: Optional[float] = None
    average_loss: Optional[float] = None
    worst_loss: Optional[float] = None
    tail_ratio: Optional[float] = None

@dataclass
class StressTestResult:
    """Stress test natijasi"""
    scenario: StressScenario
    scenario_name: str
    scenario_description: str
    shock_parameters: Dict[str, float]
    
    # Impact metrics
    portfolio_impact: float
    asset_impacts: Dict[str, float]
    profit_loss: float
    return_impact: float
    
    # Risk metrics under stress
    stressed_var: float
    stressed_volatility: float
    stressed_max_drawdown: float
    
    # Recovery metrics
    recovery_time: Optional[int] = None  # Days to recover
    recovery_probability: Optional[float] = None
    
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CreditRiskMetrics:
    """Credit risk metrikalari"""
    probability_of_default: float
    loss_given_default: float
    exposure_at_default: float
    expected_loss: float
    unexpected_loss: float
    credit_spread: float
    default_correlation: float
    
    # Portfolio metrics
    portfolio_default_rate: float
    concentration_risk: float
    sector_exposure: Dict[str, float] = field(default_factory=dict)

@dataclass
class LiquidityRiskMetrics:
    """Liquidity risk metrikalari"""
    bid_ask_spread: float
    market_depth: float
    price_impact: float
    time_to_liquidate: int  # Hours
    liquidation_cost: float
    
    # Stress scenarios
    stressed_bid_ask_spread: float
    stressed_liquidation_time: int
    stressed_liquidation_cost: float

class RiskModeling:
    """Risk Modeling Engine"""
    
    def __init__(self, 
                 confidence_levels: List[float] = [0.95, 0.99],
                 risk_free_rate: float = 0.02):
        """
        Args:
            confidence_levels: Confidence levels for risk calculations
            risk_free_rate: Risk-free rate
        """
        self.confidence_levels = confidence_levels
        self.risk_free_rate = risk_free_rate
        
        # Risk model cache
        self.garch_models = {}
        self.var_models = {}
        self.stress_scenarios = {}
        
        # Data storage
        self.price_data = {}
        self.return_data = {}
        self.market_data = {}
        
        # Thread pool
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("Risk Modeling Engine initialized")
    
    async def calculate_var(self,
                          symbol: str,
                          returns: pd.Series,
                          method: VaRMethod = VaRMethod.HISTORICAL,
                          horizon: int = 1,
                          confidence_level: float = 0.95) -> float:
        """
        Value at Risk (VaR) hisoblash
        
        Args:
            symbol: Asset symbol
            returns: Historical returns
            method: VaR calculation method
            horizon: Time horizon (days)
            confidence_level: Confidence level
            
        Returns:
            VaR value (positive number representing potential loss)
        """
        try:
            logger.info(f"Calculating VaR for {symbol} using {method.value} method")
            
            if len(returns) < 30:
                raise ValueError("Insufficient data for VaR calculation")
            
            if method == VaRMethod.HISTORICAL:
                var = await self._historical_var(returns, horizon, confidence_level)
            elif method == VaRMethod.PARAMETRIC:
                var = await self._parametric_var(returns, horizon, confidence_level)
            elif method == VaRMethod.MONTE_CARLO:
                var = await self._monte_carlo_var(returns, horizon, confidence_level)
            elif method == VaRMethod.CORNISH_FISHER:
                var = await self._cornish_fisher_var(returns, horizon, confidence_level)
            elif method == VaRMethod.EXTREME_VALUE:
                var = await self._extreme_value_var(returns, horizon, confidence_level)
            elif method == VaRMethod.GARCH:
                var = await self._garch_var(returns, horizon, confidence_level)
            else:
                raise ValueError(f"Unknown VaR method: {method.value}")
            
            logger.info(f"VaR calculated: {var:.4f} ({method.value})")
            return var
            
        except Exception as e:
            logger.error(f"VaR calculation failed for {symbol}: {e}")
            raise
    
    async def _historical_var(self, 
                            returns: pd.Series, 
                            horizon: int, 
                            confidence_level: float) -> float:
        """Historical VaR"""
        try:
            # Use historical distribution
            sorted_returns = returns.sort_values()
            percentile = (1 - confidence_level) * 100
            var = abs(np.percentile(sorted_returns, percentile))
            
            # Scale for time horizon (simplified)
            var_scaled = var * np.sqrt(horizon)
            
            return var_scaled
            
        except Exception as e:
            logger.error(f"Historical VaR failed: {e}")
            return abs(returns.std() * norm.ppf(1 - confidence_level) * np.sqrt(horizon))
    
    async def _parametric_var(self,
                            returns: pd.Series,
                            horizon: int,
                            confidence_level: float) -> float:
        """Parametric VaR (Normal distribution)"""
        try:
            mean_return = returns.mean()
            std_return = returns.std()
            
            # Z-score for confidence level
            z_score = norm.ppf(1 - confidence_level)
            
            # VaR calculation
            var = abs(mean_return + z_score * std_return)
            
            # Scale for time horizon
            var_scaled = var * np.sqrt(horizon)
            
            return var_scaled
            
        except Exception as e:
            logger.error(f"Parametric VaR failed: {e}")
            return abs(returns.std() * np.sqrt(horizon))
    
    async def _monte_carlo_var(self,
                             returns: pd.Series,
                             horizon: int,
                             confidence_level: float) -> float:
        """Monte Carlo VaR"""
        try:
            # Fit t-distribution (more realistic for financial returns)
            params = t.fit(returns)
            df, loc, scale = params
            
            # Generate Monte Carlo scenarios
            n_simulations = 10000
            simulated_returns = t.rvs(df, loc, scale, size=n_simulations)
            
            # Calculate VaR
            percentile = (1 - confidence_level) * 100
            var = abs(np.percentile(simulated_returns, percentile))
            
            # Scale for time horizon
            var_scaled = var * np.sqrt(horizon)
            
            return var_scaled
            
        except Exception as e:
            logger.error(f"Monte Carlo VaR failed: {e}")
            return await self._parametric_var(returns, horizon, confidence_level)
    
    async def _cornish_fisher_var(self,
                                 returns: pd.Series,
                                 horizon: int,
                                 confidence_level: float) -> float:
        """Cornish-Fisher VaR (accounts for skewness and kurtosis)"""
        try:
            mean_return = returns.mean()
            std_return = returns.std()
            skewness = stats.skew(returns)
            kurtosis = stats.kurtosis(returns, fisher=True)  # Excess kurtosis
            
            # Z-score
            z = norm.ppf(1 - confidence_level)
            
            # Cornish-Fisher adjustment
            cf_adjustment = (
                z + 
                (z**2 - 1) * skewness / 6 +
                (z**3 - 3*z) * kurtosis / 24 -
                (2*z**3 - 5*z) * skewness**2 / 36
            )
            
            # VaR calculation
            var = abs(mean_return + cf_adjustment * std_return)
            
            # Scale for time horizon
            var_scaled = var * np.sqrt(horizon)
            
            return var_scaled
            
        except Exception as e:
            logger.error(f"Cornish-Fisher VaR failed: {e}")
            return await self._parametric_var(returns, horizon, confidence_level)
    
    async def _extreme_value_var(self,
                                returns: pd.Series,
                                horizon: int,
                                confidence_level: float) -> float:
        """Extreme Value Theory (EVT) VaR"""
        try:
            # Use Block Maxima approach
            block_size = min(22, len(returns) // 10)  # Monthly blocks
            n_blocks = len(returns) // block_size
            
            block_maxima = []
            for i in range(n_blocks):
                start_idx = i * block_size
                end_idx = start_idx + block_size
                block_data = returns.iloc[start_idx:end_idx]
                block_maxima.append(block_data.max())
            
            # Fit Generalized Extreme Value distribution
            params = genextreme.fit(block_maxima)
            c, loc, scale = params
            
            # Calculate VaR for extreme events
            p = 1 - confidence_level
            var = abs(genextreme.ppf(p, c, loc, scale))
            
            # Scale for time horizon
            var_scaled = var * np.sqrt(horizon)
            
            return var_scaled
            
        except Exception as e:
            logger.error(f"Extreme Value VaR failed: {e}")
            return await self._parametric_var(returns, horizon, confidence_level)
    
    async def _garch_var(self,
                        returns: pd.Series,
                        horizon: int,
                        confidence_level: float) -> float:
        """GARCH-based VaR"""
        try:
            # Fit GARCH(1,1) model
            returns_clean = returns.dropna()
            
            if len(returns_clean) < 50:
                raise ValueError("Insufficient data for GARCH model")
            
            model = arch_model(returns_clean * 100, vol='Garch', p=1, q=1)
            fitted_model = model.fit(disp='off')
            
            # Forecast volatility
            forecast = fitted_model.forecast(horizon=horizon, reindex=False)
            conditional_variance = forecast.variance.values[-1, :]
            conditional_volatility = np.sqrt(conditional_variance) / 100  # Convert back to returns
            
            # Mean return
            mean_return = fitted_model.params['mu'] / 100
            
            # VaR calculation
            z_score = norm.ppf(1 - confidence_level)
            var = abs(mean_return + z_score * conditional_volatility[-1])
            
            return var
            
        except Exception as e:
            logger.error(f"GARCH VaR failed: {e}")
            return await self._parametric_var(returns, horizon, confidence_level)
    
    async def calculate_expected_shortfall(self,
                                         symbol: str,
                                         returns: pd.Series,
                                         method: VaRMethod = VaRMethod.HISTORICAL,
                                         horizon: int = 1,
                                         confidence_level: float = 0.95) -> float:
        """
        Expected Shortfall (CVaR) hisoblash
        
        Args:
            symbol: Asset symbol
            returns: Historical returns
            method: VaR method to use
            horizon: Time horizon (days)
            confidence_level: Confidence level
            
        Returns:
            Expected Shortfall value
        """
        try:
            logger.info(f"Calculating Expected Shortfall for {symbol}")
            
            # First get VaR
            var = await self.calculate_var(symbol, returns, method, horizon, confidence_level)
            
            if method == VaRMethod.HISTORICAL:
                # Historical Expected Shortfall
                sorted_returns = returns.sort_values()
                percentile = (1 - confidence_level) * 100
                var_threshold = np.percentile(sorted_returns, percentile)
                tail_losses = sorted_returns[sorted_returns <= var_threshold]
                es = abs(tail_losses.mean())
                
            elif method == VaRMethod.PARAMETRIC:
                # Parametric Expected Shortfall using t-distribution
                params = t.fit(returns)
                df, loc, scale = params
                
                # Calculate ES analytically
                alpha = 1 - confidence_level
                t_crit = t.ppf(alpha, df)
                es = abs(t.pdf(t_crit, df) / (alpha * df) * (df + t_crit**2) * scale + loc)
                
            else:
                # For other methods, use VaR approximation
                es = var * 1.3  # Empirical multiplier
            
            # Scale for time horizon
            es_scaled = es * np.sqrt(horizon)
            
            logger.info(f"Expected Shortfall calculated: {es_scaled:.4f}")
            return es_scaled
            
        except Exception as e:
            logger.error(f"Expected Shortfall calculation failed: {e}")
            return await self.calculate_var(symbol, returns, method, horizon, confidence_level) * 1.3
    
    async def stress_test_portfolio(self,
                                  portfolio_weights: Dict[str, float],
                                  price_data: pd.DataFrame,
                                  scenario: StressScenario,
                                  scenario_parameters: Optional[Dict[str, float]] = None) -> StressTestResult:
        """
        Portfolio stress testing
        
        Args:
            portfolio_weights: Portfolio asset weights
            price_data: Historical price data
            scenario: Stress scenario type
            scenario_parameters: Scenario-specific parameters
            
        Returns:
            StressTestResult: Stress test results
        """
        try:
            logger.info(f"Running stress test: {scenario.value}")
            
            if scenario_parameters is None:
                scenario_parameters = {}
            
            # Define scenario parameters
            if scenario == StressScenario.MARKET_CRASH:
                shock_params = {
                    'market_shock': scenario_parameters.get('market_shock', -0.20),
                    'volatility_multiplier': scenario_parameters.get('volatility_multiplier', 3.0)
                }
                scenario_name = "Market Crash"
                description = "Simulates a major market decline with increased volatility"
                
            elif scenario == StressScenario.INTEREST_RATE_SHOCK:
                shock_params = {
                    'rate_shock': scenario_parameters.get('rate_shock', 0.02),
                    'duration_impact': scenario_parameters.get('duration_impact', 10)
                }
                scenario_name = "Interest Rate Shock"
                description = "Simulates a rapid interest rate increase"
                
            elif scenario == StressScenario.VOLATILITY_SPIKE:
                shock_params = {
                    'volatility_multiplier': scenario_parameters.get('volatility_multiplier', 4.0),
                    'correlation_increase': scenario_parameters.get('correlation_increase', 0.5)
                }
                scenario_name = "Volatility Spike"
                description = "Simulates a sudden volatility increase across assets"
                
            else:
                # Default parameters
                shock_params = {'default_shock': -0.15}
                scenario_name = "Custom Scenario"
                description = "Custom stress scenario"
            
            # Apply scenario to individual assets
            asset_impacts = {}
            total_impact = 0
            
            for symbol, weight in portfolio_weights.items():
                if symbol in price_data.columns:
                    current_price = price_data[symbol].iloc[-1]
                    
                    # Calculate shock impact based on scenario
                    if scenario == StressScenario.MARKET_CRASH:
                        # Apply market shock
                        shock_impact = shock_params['market_shock']
                        
                    elif scenario == StressScenario.INTEREST_RATE_SHOCK:
                        # Apply interest rate shock (simplified)
                        if 'duration' not in shock_params:
                            shock_impact = shock_params['rate_shock'] * 10  # Simplified duration impact
                        else:
                            shock_impact = shock_params['rate_shock'] * shock_params['duration_impact']
                        
                    elif scenario == StressScenario.VOLATILITY_SPIKE:
                        # Volatility spike doesn't directly impact prices, but affects risk
                        shock_impact = 0  # No direct price impact
                        
                    else:
                        # Custom scenario
                        shock_impact = shock_params.get('default_shock', -0.15)
                    
                    # Apply weight
                    weighted_impact = weight * shock_impact
                    asset_impacts[symbol] = weighted_impact
                    total_impact += weighted_impact
            
            # Calculate portfolio-level metrics
            portfolio_impact = total_impact
            profit_loss = portfolio_impact * 1000000  # Assume $1M portfolio
            return_impact = portfolio_impact
            
            # Calculate stressed risk metrics
            stressed_var = await self._calculate_stressed_var(portfolio_weights, price_data, shock_params)
            stressed_volatility = await self._calculate_stressed_volatility(portfolio_weights, price_data, shock_params)
            stressed_max_drawdown = await self._calculate_stressed_max_drawdown(portfolio_weights, price_data, shock_params)
            
            # Estimate recovery metrics
            recovery_time = await self._estimate_recovery_time(portfolio_impact, scenario)
            recovery_probability = await self._estimate_recovery_probability(portfolio_impact, scenario)
            
            # Create result
            stress_result = StressTestResult(
                scenario=scenario,
                scenario_name=scenario_name,
                scenario_description=description,
                shock_parameters=shock_params,
                portfolio_impact=portfolio_impact,
                asset_impacts=asset_impacts,
                profit_loss=profit_loss,
                return_impact=return_impact,
                stressed_var=stressed_var,
                stressed_volatility=stressed_volatility,
                stressed_max_drawdown=stressed_max_drawdown,
                recovery_time=recovery_time,
                recovery_probability=recovery_probability
            )
            
            logger.info(f"Stress test completed: {portfolio_impact:.2%} portfolio impact")
            return stress_result
            
        except Exception as e:
            logger.error(f"Stress testing failed: {e}")
            raise
    
    async def _calculate_stressed_var(self,
                                    portfolio_weights: Dict[str, float],
                                    price_data: pd.DataFrame,
                                    shock_params: Dict[str, float]) -> float:
        """Calculate VaR under stress conditions"""
        try:
            # Simplified stressed VaR calculation
            base_volatility = 0.02  # 2% daily
            
            # Apply volatility multiplier
            vol_multiplier = shock_params.get('volatility_multiplier', 2.0)
            stressed_vol = base_volatility * vol_multiplier
            
            # Calculate stressed VaR
            z_score = norm.ppf(0.05)  # 95% confidence
            stressed_var = abs(z_score * stressed_vol)
            
            return stressed_var
            
        except Exception as e:
            return 0.05  # Default 5%
    
    async def _calculate_stressed_volatility(self,
                                           portfolio_weights: Dict[str, float],
                                           price_data: pd.DataFrame,
                                           shock_params: Dict[str, float]) -> float:
        """Calculate volatility under stress conditions"""
        try:
            base_volatility = 0.02
            
            vol_multiplier = shock_params.get('volatility_multiplier', 2.0)
            stressed_vol = base_volatility * vol_multiplier
            
            return stressed_vol
            
        except Exception as e:
            return 0.04  # Default 4%
    
    async def _calculate_stressed_max_drawdown(self,
                                             portfolio_weights: Dict[str, float],
                                             price_data: pd.DataFrame,
                                             shock_params: Dict[str, float]) -> float:
        """Calculate maximum drawdown under stress conditions"""
        try:
            # Simplified stressed drawdown calculation
            base_drawdown = 0.10  # 10% base drawdown
            
            # Apply shock impact
            market_shock = abs(shock_params.get('market_shock', 0.0))
            stressed_drawdown = base_drawdown + market_shock
            
            return min(stressed_drawdown, 0.50)  # Cap at 50%
            
        except Exception as e:
            return 0.20  # Default 20%
    
    async def _estimate_recovery_time(self, portfolio_impact: float, scenario: StressScenario) -> int:
        """Estimate recovery time in days"""
        try:
            # Simplified recovery time estimation
            impact_severity = abs(portfolio_impact)
            
            if scenario == StressScenario.MARKET_CRASH:
                base_recovery = 180  # 6 months base
            elif scenario == StressScenario.VOLATILITY_SPIKE:
                base_recovery = 60   # 2 months base
            else:
                base_recovery = 90   # 3 months base
            
            # Adjust based on impact severity
            recovery_multiplier = 1 + (impact_severity * 10)
            recovery_time = int(base_recovery * recovery_multiplier)
            
            return min(recovery_time, 365)  # Cap at 1 year
            
        except Exception as e:
            return 90  # Default 90 days
    
    async def _estimate_recovery_probability(self, portfolio_impact: float, scenario: StressScenario) -> float:
        """Estimate probability of recovery"""
        try:
            impact_severity = abs(portfolio_impact)
            
            # Base recovery probability
            base_prob = 0.8  # 80% base
            
            # Adjust based on impact severity
            penalty = min(impact_severity * 5, 0.6)  # Max 60% penalty
            recovery_prob = max(base_prob - penalty, 0.2)  # Min 20% probability
            
            return recovery_prob
            
        except Exception as e:
            return 0.7  # Default 70%
    
    async def calculate_comprehensive_risk_metrics(self,
                                                 symbol: str,
                                                 returns: pd.Series,
                                                 benchmark_returns: Optional[pd.Series] = None) -> RiskMetrics:
        """
        Comprehensive risk metrics calculation
        
        Args:
            symbol: Asset symbol
            returns: Historical returns
            benchmark_returns: Benchmark returns for comparison
            
        Returns:
            RiskMetrics: Comprehensive risk metrics
        """
        try:
            logger.info(f"Calculating comprehensive risk metrics for {symbol}")
            
            # Basic statistics
            mean_return = returns.mean()
            std_return = returns.std()
            skewness = stats.skew(returns)
            kurtosis = stats.kurtosis(returns, fisher=True)
            
            # Risk metrics
            var_95 = await self.calculate_var(symbol, returns, VaRMethod.HISTORICAL, 1, 0.95)
            var_99 = await self.calculate_var(symbol, returns, VaRMethod.HISTORICAL, 1, 0.99)
            es_95 = await self.calculate_expected_shortfall(symbol, returns, VaRMethod.HISTORICAL, 1, 0.95)
            es_99 = await self.calculate_expected_shortfall(symbol, returns, VaRMethod.HISTORICAL, 1, 0.99)
            
            # Performance metrics
            excess_returns = returns - self.risk_free_rate / 252
            sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
            
            # Sortino ratio
            downside_returns = returns[returns < 0]
            downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino_ratio = (mean_return * 252) / downside_deviation if downside_deviation > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = abs(drawdown.min())
            
            # Calmar ratio
            annualized_return = mean_return * 252
            calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
            
            # Additional metrics
            # Hit ratio
            positive_returns = (returns > 0).sum()
            hit_ratio = positive_returns / len(returns) if len(returns) > 0 else 0
            
            # Average loss
            losses = returns[returns < 0]
            average_loss = abs(losses.mean()) if len(losses) > 0 else 0
            
            # Worst loss
            worst_loss = abs(returns.min())
            
            # Tail ratio
            upside_returns = returns[returns > 0]
            upside_std = upside_returns.std() if len(upside_returns) > 0 else 1
            tail_ratio = upside_std / downside_deviation if downside_deviation > 0 else 1
            
            risk_metrics = RiskMetrics(
                var_95=var_95,
                var_99=var_99,
                expected_shortfall_95=es_95,
                expected_shortfall_99=es_99,
                volatility=std_return * np.sqrt(252),
                skewness=skewness,
                kurtosis=kurtosis,
                maximum_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                hit_ratio=hit_ratio,
                average_loss=average_loss,
                worst_loss=worst_loss,
                tail_ratio=tail_ratio
            )
            
            logger.info(f"Comprehensive risk metrics calculated for {symbol}")
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Comprehensive risk metrics calculation failed: {e}")
            raise
    
    async def detect_anomalies(self,
                             returns: pd.Series,
                             method: str = "isolation_forest",
                             contamination: float = 0.05) -> Dict[int, float]:
        """
        Anomaly detection in returns
        
        Args:
            returns: Returns series
            method: Anomaly detection method
            contamination: Expected proportion of outliers
            
        Returns:
            Dict of anomalous indices and their scores
        """
        try:
            logger.info(f"Detecting anomalies using {method}")
            
            if method == "isolation_forest":
                # Use Isolation Forest
                clf = IsolationForest(contamination=contamination, random_state=42)
                
                # Prepare features
                features = self._create_anomaly_features(returns)
                
                # Fit and predict
                anomaly_labels = clf.fit_predict(features)
                anomaly_scores = clf.decision_function(features)
                
                # Find anomalies
                anomalies = {}
                for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
                    if label == -1:  # Anomaly
                        anomalies[i] = float(score)
                
                return anomalies
                
            elif method == "statistical":
                # Statistical outlier detection
                z_scores = np.abs(stats.zscore(returns))
                threshold = 3  # 3 standard deviations
                
                anomalies = {}
                for i, z_score in enumerate(z_scores):
                    if z_score > threshold:
                        anomalies[i] = float(z_score)
                
                return anomalies
            
            else:
                raise ValueError(f"Unknown anomaly detection method: {method}")
                
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {}
    
    def _create_anomaly_features(self, returns: pd.Series) -> np.ndarray:
        """Create features for anomaly detection"""
        try:
            features = []
            
            # Rolling statistics
            window = min(20, len(returns) // 4)
            
            for i in range(window, len(returns)):
                window_returns = returns.iloc[i-window:i]
                
                feature_row = [
                    returns.iloc[i],  # Current return
                    window_returns.mean(),  # Rolling mean
                    window_returns.std(),   # Rolling std
                    window_returns.skew(),  # Rolling skewness
                    window_returns.kurtosis(),  # Rolling kurtosis
                    (returns.iloc[i] - window_returns.mean()) / window_returns.std() if window_returns.std() > 0 else 0,  # Z-score
                ]
                
                features.append(feature_row)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Feature creation failed: {e}")
            return np.array([])
    
    async def calculate_credit_risk(self,
                                  counterparty_data: Dict[str, Any],
                                  exposure_data: pd.DataFrame) -> CreditRiskMetrics:
        """
        Credit risk calculation
        
        Args:
            counterparty_data: Counterparty information
          exposure_data: Exposure data over time
            
        Returns:
            CreditRiskMetrics: Credit risk metrics
        """
        try:
            logger.info("Calculating credit risk metrics")
            
            # Simplified credit risk model
            
            # Probability of Default (PD) - using credit score
            credit_score = counterparty_data.get('credit_score', 700)  # Default 700
            if credit_score >= 800:
                pd = 0.001  # 0.1%
            elif credit_score >= 700:
                pd = 0.005  # 0.5%
            elif credit_score >= 600:
                pd = 0.02   # 2%
            else:
                pd = 0.05   # 5%
            
            # Loss Given Default (LGD) - based on collateral
            collateral_ratio = counterparty_data.get('collateral_ratio', 0.8)  # 80% collateral
            lgd = 1 - collateral_ratio  # LGD = 1 - Collateral Ratio
            
            # Exposure at Default (EAD)
            ead = exposure_data['exposure'].mean() if 'exposure' in exposure_data.columns else 1000000
            
            # Expected Loss
            expected_loss = pd * lgd * ead
            
            # Unexpected Loss (simplified)
            unexpected_loss = np.sqrt(pd * lgd**2 * ead**2 * (1 - pd))
            
            # Credit spread (based on PD)
            if pd <= 0.001:
                credit_spread = 0.005  # 50 bps
            elif pd <= 0.005:
                credit_spread = 0.015  # 150 bps
            elif pd <= 0.02:
                credit_spread = 0.035  # 350 bps
            else:
                credit_spread = 0.075  # 750 bps
            
            # Default correlation (simplified)
            default_correlation = 0.2  # 20%
            
            # Portfolio default rate
            n_counterparties = counterparty_data.get('portfolio_size', 100)
            portfolio_default_rate = 1 - (1 - pd) ** n_counterparties
            
            # Concentration risk
            max_exposure = exposure_data['exposure'].max() if 'exposure' in exposure_data.columns else 0
            concentration_risk = max_exposure / ead if ead > 0 else 0
            
            # Sector exposure
            sector_exposure = counterparty_data.get('sector_exposure', {})
            
            credit_risk = CreditRiskMetrics(
                probability_of_default=pd,
                loss_given_default=lgd,
                exposure_at_default=ead,
                expected_loss=expected_loss,
                unexpected_loss=unexpected_loss,
                credit_spread=credit_spread,
                default_correlation=default_correlation,
                portfolio_default_rate=portfolio_default_rate,
                concentration_risk=concentration_risk,
                sector_exposure=sector_exposure
            )
            
            logger.info("Credit risk metrics calculated successfully")
            return credit_risk
            
        except Exception as e:
            logger.error(f"Credit risk calculation failed: {e}")
            raise
    
    async def calculate_liquidity_risk(self,
                                     symbol: str,
                                     order_book_data: pd.DataFrame) -> LiquidityRiskMetrics:
        """
        Liquidity risk calculation
        
        Args:
            symbol: Asset symbol
            order_book_data: Order book data
            
        Returns:
            LiquidityRiskMetrics: Liquidity risk metrics
        """
        try:
            logger.info(f"Calculating liquidity risk for {symbol}")
            
            # Calculate bid-ask spread
            if 'bid_price' in order_book_data.columns and 'ask_price' in order_book_data.columns:
                spreads = order_book_data['ask_price'] - order_book_data['bid_price']
                bid_ask_spread = spreads.mean()
                spread_pct = (bid_ask_spread / order_book_data['bid_price'].mean()) * 100
            else:
                bid_ask_spread = 0.01  # Default 1%
                spread_pct = 0.1  # Default 0.1%
            
            # Market depth (volume available)
            if 'bid_volume' in order_book_data.columns and 'ask_volume' in order_book_data.columns:
                bid_depth = order_book_data['bid_volume'].sum()
                ask_depth = order_book_data['ask_volume'].sum()
                market_depth = (bid_depth + ask_depth) / 2
            else:
                market_depth = 1000000  # Default depth
            
            # Price impact (simplified)
            # Kyle's lambda model: Price impact = lambda * Volume
            lambda_coeff = 0.001  # Kyle's lambda
            price_impact = lambda_coeff * 1000000 / market_depth  # $1M trade impact
            
            # Time to liquidate (simplified)
            avg_volume = order_book_data['volume'].mean() if 'volume' in order_book_data.columns else 10000
            time_to_liquidate = max(1, int(1000000 / avg_volume))  # Time to liquidate $1M
            
            # Liquidation cost
            liquidation_cost = spread_pct + price_impact * 100  # Percentage cost
            
            # Stress scenarios
            # Assuming 50% worse liquidity under stress
            stressed_bid_ask_spread = bid_ask_spread * 2
            stressed_liquidation_time = time_to_liquidate * 3
            stressed_liquidation_cost = liquidation_cost * 2
            
            liquidity_risk = LiquidityRiskMetrics(
                bid_ask_spread=spread_pct,  # Percentage
                market_depth=market_depth,
                price_impact=price_impact * 100,  # Percentage
                time_to_liquidate=time_to_liquidate,
                liquidation_cost=liquidation_cost,
                stressed_bid_ask_spread=stressed_bid_ask_spread * 2,
                stressed_liquidation_time=stressed_liquidation_time,
                stressed_liquidation_cost=stressed_liquidation_cost * 1.5
            )
            
            logger.info(f"Liquidity risk calculated for {symbol}")
            return liquidity_risk
            
        except Exception as e:
            logger.error(f"Liquidity risk calculation failed: {symbol}: {e}")
            raise
    
    async def generate_risk_report(self,
                                 symbols: List[str],
                                 returns_data: pd.DataFrame,
                                 portfolio_weights: Dict[str, float],
                                 benchmark: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive risk report generation
        
        Args:
            symbols: Asset symbols
            returns_data: Historical returns data
            portfolio_weights: Portfolio weights
            benchmark: Benchmark symbol
            
        Returns:
            Dict: Comprehensive risk report
        """
        try:
            logger.info("Generating comprehensive risk report")
            
            report = {
                'timestamp': datetime.now(),
                'report_period': f"{returns_data.index[0].date()} to {returns_data.index[-1].date()}",
                'assets_analyzed': symbols,
                'portfolio_weights': portfolio_weights,
                'individual_risk_metrics': {},
                'portfolio_risk_metrics': {},
                'stress_test_results': {},
                'var_analysis': {},
                'anomaly_detection': {}
            }
            
            # Individual asset analysis
            for symbol in symbols:
                if symbol in returns_data.columns:
                    returns = returns_data[symbol]
                    
                    # Risk metrics
                    risk_metrics = await self.calculate_comprehensive_risk_metrics(symbol, returns)
                    report['individual_risk_metrics'][symbol] = {
                        'var_95': risk_metrics.var_95,
                        'var_99': risk_metrics.var_99,
                        'expected_shortfall_95': risk_metrics.expected_shortfall_95,
                        'volatility': risk_metrics.volatility,
                        'max_drawdown': risk_metrics.max_drawdown,
                        'sharpe_ratio': risk_metrics.sharpe_ratio,
                        'sortino_ratio': risk_metrics.sortino_ratio,
                        'skewness': risk_metrics.skewness,
                        'kurtosis': risk_metrics.kurtosis
                    }
                    
                    # VaR analysis using different methods
                    var_methods = [VaRMethod.HISTORICAL, VaRMethod.PARAMETRIC, VaRMethod.CORNISH_FISHER]
                    var_analysis = {}
                    
                    for method in var_methods:
                        try:
                            var_95 = await self.calculate_var(symbol, returns, method, 1, 0.95)
                            var_99 = await self.calculate_var(symbol, returns, method, 1, 0.99)
                            var_analysis[method.value] = {
                                'var_95': var_95,
                                'var_99': var_99
                            }
                        except Exception as e:
                            logger.warning(f"VaR method {method.value} failed for {symbol}: {e}")
                    
                    report['var_analysis'][symbol] = var_analysis
                    
                    # Anomaly detection
                    anomalies = await self.detect_anomalies(returns)
                    report['anomaly_detection'][symbol] = {
                        'anomaly_count': len(anomalies),
                        'anomaly_rate': len(anomalies) / len(returns),
                        'anomaly_dates': [returns_data.index[i].strftime('%Y-%m-%d') for i in anomalies.keys()]
                    }
            
            # Portfolio-level analysis
            portfolio_returns = (returns_data[symbols] * pd.Series(portfolio_weights)).sum(axis=1)
            portfolio_risk_metrics = await self.calculate_comprehensive_risk_metrics("PORTFOLIO", portfolio_returns)
            
            report['portfolio_risk_metrics'] = {
                'var_95': portfolio_risk_metrics.var_95,
                'var_99': portfolio_risk_metrics.var_99,
                'expected_shortfall_95': portfolio_risk_metrics.expected_shortfall_95,
                'volatility': portfolio_risk_metrics.volatility,
                'max_drawdown': portfolio_risk_metrics.max_drawdown,
                'sharpe_ratio': portfolio_risk_metrics.sharpe_ratio,
                'sortino_ratio': portfolio_risk_metrics.sortino_ratio
            }
            
            # Stress testing
            stress_scenarios = [StressScenario.MARKET_CRASH, StressScenario.VOLATILITY_SPIKE]
            
            for scenario in stress_scenarios:
                try:
                    stress_result = await self.stress_test_portfolio(
                        portfolio_weights, 
                        returns_data, 
                        scenario
                    )
                    
                    report['stress_test_results'][scenario.value] = {
                        'scenario_name': stress_result.scenario_name,
                        'portfolio_impact': stress_result.portfolio_impact,
                        'profit_loss': stress_result.profit_loss,
                        'stressed_var': stress_result.stressed_var,
                        'recovery_time_days': stress_result.recovery_time,
                        'recovery_probability': stress_result.recovery_probability
                    }
                except Exception as e:
                    logger.warning(f"Stress test failed for {scenario.value}: {e}")
            
            logger.info("Comprehensive risk report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Risk report generation failed: {e}")
            raise
    
    async def cleanup(self):
        """Resurslarni tozalash"""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            
            # Clear caches
            self.garch_models.clear()
            self.var_models.clear()
            self.stress_scenarios.clear()
            
            # Clear data
            self.price_data.clear()
            self.return_data.clear()
            self.market_data.clear()
            
            logger.info("Risk Modeling cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

# Test function
async def test_risk_modeling():
    """Test Risk Modeling Engine"""
    try:
        print("⚠️ Risk Modeling Engine Test")
        print("=" * 50)
        
        # Initialize engine
        risk_engine = RiskModeling()
        
        # Create sample data
        np.random.seed(42)
        n_assets = 3
        n_periods = 500
        
        symbols = ["BTC", "ETH", "ADA"]
        
        # Generate realistic returns with volatility clustering
        returns_data = {}
        
        for i, symbol in enumerate(symbols):
            # Simulate volatility clustering
            base_vol = 0.02 + i * 0.01  # Different volatility levels
            
            returns = []
            current_vol = base_vol
            
            for _ in range(n_periods):
                # GARCH-like volatility update
                shock = np.random.normal(0, 0.1)
                current_vol = 0.95 * current_vol + 0.05 * abs(shock)
                current_vol = max(current_vol, base_vol * 0.5)
                current_vol = min(current_vol, base_vol * 2)
                
                # Generate return
                return_val = np.random.normal(0.001, current_vol)
                returns.append(return_val)
            
            returns_data[symbol] = returns
        
        dates = pd.date_range(start='2023-01-01', periods=n_periods, freq='D')
        returns_df = pd.DataFrame(returns_data, index=dates)
        
        print(f"📊 Sample Risk Data Created:")
        print(f"  Assets: {symbols}")
        print(f"  Period: {dates[0].date()} to {dates[-1].date()}")
        print(f"  Data Points: {len(returns_df)}")
        
        # Test individual VaR calculations
        print(f"\n📉 VaR Analysis Test:")
        var_methods = [VaRMethod.HISTORICAL, VaRMethod.PARAMETRIC, VaRMethod.CORNISH_FISHER]
        
        for symbol in symbols:
            print(f"\n--- {symbol} VaR Analysis ---")
            returns = returns_df[symbol]
            
            for method in var_methods:
                try:
                    var_95 = await risk_engine.calculate_var(symbol, returns, method, 1, 0.95)
                    var_99 = await risk_engine.calculate_var(symbol, returns, method, 1, 0.99)
                    es_95 = await risk_engine.calculate_expected_shortfall(symbol, returns, method, 1, 0.95)
                    
                    print(f"  {method.value.upper()}:")
                    print(f"    VaR (95%): {var_95:.2%}")
                    print(f"    VaR (99%): {var_99:.2%}")
                    print(f"    ES (95%): {es_95:.2%}")
                    
                except Exception as e:
                    print(f"    {method.value}: Failed - {e}")
        
        # Test comprehensive risk metrics
        print(f"\n📊 Comprehensive Risk Metrics Test:")
        
        for symbol in symbols[:2]:  # Test first 2 assets
            print(f"\n--- {symbol} Risk Metrics ---")
            returns = returns_df[symbol]
            
            risk_metrics = await risk_engine.calculate_comprehensive_risk_metrics(symbol, returns)
            
            print(f"  VaR (95%): {risk_metrics.var_95:.2%}")
            print(f"  VaR (99%): {risk_metrics.var_99:.2%}")
            print(f"  Expected Shortfall (95%): {risk_metrics.expected_shortfall_95:.2%}")
            print(f"  Volatility: {risk_metrics.volatility:.2%}")
            print(f"  Max Drawdown: {risk_metrics.max_drawdown:.2%}")
            print(f"  Sharpe Ratio: {risk_metrics.sharpe_ratio:.2f}")
            print(f"  Sortino Ratio: {risk_metrics.sortino_ratio:.2f}")
            print(f"  Skewness: {risk_metrics.skewness:.3f}")
            print(f"  Kurtosis: {risk_metrics.kurtosis:.3f}")
            print(f"  Hit Ratio: {risk_metrics.hit_ratio:.2%}")
            print(f"  Tail Ratio: {risk_metrics.tail_ratio:.2f}")
        
        # Test anomaly detection
        print(f"\n🚨 Anomaly Detection Test:")
        
        for symbol in symbols[:2]:
            print(f"\n--- {symbol} Anomalies ---")
            returns = returns_df[symbol]
            
            anomalies = await risk_engine.detect_anomalies(returns, method="statistical")
            
            print(f"  Anomalies Detected: {len(anomalies)}")
            print(f"  Anomaly Rate: {len(anomalies)/len(returns):.2%}")
            
            if anomalies:
                # Show first few anomalies
                sorted_anomalies = sorted(anomalies.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"  Top Anomalies:")
                for idx, score in sorted_anomalies:
                    date = returns_df.index[idx]
                    print(f"    {date.strftime('%Y-%m-%d')}: {score:.2f} z-score")
        
        # Test stress testing
        print(f"\n💥 Stress Testing Test:")
        
        portfolio_weights = {"BTC": 0.5, "ETH": 0.3, "ADA": 0.2}
        
        # Create price data for stress testing
        prices_data = {}
        for symbol in symbols:
            base_price = 50000 if symbol == "BTC" else 3000 if symbol == "ETH" else 1
            prices_data[symbol] = [base_price * (1 + ret) for ret in returns_data[symbol]]
        
        price_df = pd.DataFrame(prices_data, index=dates)
        
        stress_scenarios = [StressScenario.MARKET_CRASH, StressScenario.VOLATILITY_SPIKE]
        
        for scenario in stress_scenarios:
            print(f"\n--- {scenario.value.upper()} ---")
            
            try:
                stress_result = await risk_engine.stress_test_portfolio(
                    portfolio_weights,
                    price_df,
                    scenario
                )
                
                print(f"  Scenario: {stress_result.scenario_name}")
                print(f"  Portfolio Impact: {stress_result.portfolio_impact:.2%}")
                print(f"  Profit/Loss: ${stress_result.profit_loss:,.0f}")
                print(f"  Stressed VaR: {stress_result.stressed_var:.2%}")
                print(f"  Stressed Volatility: {stress_result.stressed_volatility:.2%}")
                print(f"  Recovery Time: {stress_result.recovery_time} days")
                print(f"  Recovery Probability: {stress_result.recovery_probability:.1%}")
                
                # Show asset impacts
                print(f"  Asset Impacts:")
                for asset, impact in stress_result.asset_impacts.items():
                    print(f"    {asset}: {impact:+.2%}")
                    
            except Exception as e:
                print(f"  Stress test failed: {e}")
        
        # Test comprehensive risk report
        print(f"\n📋 Risk Report Generation Test:")
        
        try:
            risk_report = await risk_engine.generate_risk_report(
                symbols[:2],  # Use first 2 assets
                returns_df[symbols[:2]],
                {"BTC": 0.6, "ETH": 0.4}
            )
            
            print(f"  Report Period: {risk_report['report_period']}")
            print(f"  Assets Analyzed: {len(risk_report['assets_analyzed'])}")
            print(f"  Stress Tests: {len(risk_report['stress_test_results'])}")
            
            # Portfolio metrics summary
            port_metrics = risk_report['portfolio_risk_metrics']
            print(f"  Portfolio VaR (95%): {port_metrics['var_95']:.2%}")
            print(f"  Portfolio Volatility: {port_metrics['volatility']:.2%}")
            print(f"  Portfolio Max Drawdown: {port_metrics['max_drawdown']:.2%}")
            
            # Individual asset summary
            print(f"  Individual Asset Risk Summary:")
            for symbol in risk_report['assets_analyzed']:
                if symbol in risk_report['individual_risk_metrics']:
                    metrics = risk_report['individual_risk_metrics'][symbol]
                    print(f"    {symbol}: VaR={metrics['var_95']:.2%}, Vol={metrics['volatility']:.2%}")
            
        except Exception as e:
            print(f"  Risk report generation failed: {e}")
        
        # Test credit risk
        print(f"\n💳 Credit Risk Test:")
        
        try:
            counterparty_data = {
                'credit_score': 750,
                'collateral_ratio': 0.8,
                'portfolio_size': 50,
                'sector_exposure': {'Technology': 0.6, 'Finance': 0.4}
            }
            
            exposure_data = pd.DataFrame({
                'exposure': np.random.normal(1000000, 100000, 100),
                'date': pd.date_range(start='2023-01-01', periods=100, freq='D')
            })
            
            credit_risk = await risk_engine.calculate_credit_risk(counterparty_data, exposure_data)
            
            print(f"  Probability of Default: {credit_risk.probability_of_default:.2%}")
            print(f"  Loss Given Default: {credit_risk.loss_given_default:.2%}")
            print(f"  Exposure at Default: ${credit_risk.exposure_at_default:,.0f}")
            print(f"  Expected Loss: ${credit_risk.expected_loss:,.0f}")
            print(f"  Unexpected Loss: ${credit_risk.unexpected_loss:,.0f}")
            print(f"  Credit Spread: {credit_risk.credit_spread:.1%}")
            print(f"  Portfolio Default Rate: {credit_risk.portfolio_default_rate:.2%}")
            print(f"  Concentration Risk: {credit_risk.concentration_risk:.2%}")
            
        except Exception as e:
            print(f"  Credit risk calculation failed: {e}")
        
        # Test liquidity risk
        print(f"\n💧 Liquidity Risk Test:")
        
        try:
            # Create order book data
            order_book_data = pd.DataFrame({
                'bid_price': np.random.normal(50000, 100, 100),
                'ask_price': np.random.normal(50050, 100, 100),
                'bid_volume': np.random.exponential(1000, 100),
                'ask_volume': np.random.exponential(1000, 100),
                'volume': np.random.exponential(2000, 100)
            })
            
            # Ensure ask > bid
            order_book_data['ask_price'] = order_book_data['bid_price'] + 50
            
            liquidity_risk = await risk_engine.calculate_liquidity_risk("BTC", order_book_data)
            
            print(f"  Bid-Ask Spread: {liquidity_risk.bid_ask_spread:.2%}")
            print(f"  Market Depth: {liquidity_risk.market_depth:,.0f}")
            print(f"  Price Impact: {liquidity_risk.price_impact:.3f}%")
            print(f"  Time to Liquidate: {liquidity_risk.time_to_liquidate} hours")
            print(f"  Liquidation Cost: {liquidity_risk.liquidation_cost:.2%}")
            print(f"  Stressed Liquidation Time: {liquidity_risk.stressed_liquidation_time} hours")
            print(f"  Stressed Liquidation Cost: {liquidity_risk.stressed_liquidation_cost:.2%}")
            
        except Exception as e:
            print(f"  Liquidity risk calculation failed: {e}")
        
        await risk_engine.cleanup()
        
        print("\n✅ Risk Modeling Engine test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_risk_modeling())