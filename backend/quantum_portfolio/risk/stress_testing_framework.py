"""
Stress Testing Framework
=======================

Quantum portfolio stress testing va scenario analysis tizimi.
Historical shock testing, Monte Carlo scenarios, correlation breakdowns.

Muallif: Quantum Portfolio Team
 Sana: 2025-11-03
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from scipy import stats
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

@dataclass
class StressScenario:
    """Stress testing scenario definition"""
    name: str
    description: str
    shock_parameters: Dict[str, float]
    correlation_changes: Dict[str, float]
    volatility_multiplier: float
    probability: float
    time_horizon_days: int
    affected_assets: List[str]

@dataclass
class StressTestResult:
    """Stress test result"""
    scenario_name: str
    original_portfolio_value: float
    stressed_portfolio_value: float
    portfolio_loss: float
    loss_percentage: float
    worst_case_loss: float
    expected_shortfall: float
    var_95: float
    var_99: float
    stress_test_timestamp: datetime
    recovery_time_estimate: float

class StressTestingFramework:
    """Portfolio stress testing framework"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Default stress scenarios
        self.scenarios = self._initialize_default_scenarios()
        
        # Historical stress periods
        self.historical_periods = {
            '2008_financial_crisis': {
                'start_date': '2008-09-01',
                'end_date': '2009-03-01',
                'description': 'Lehman Brothers collapse and credit crisis'
            },
            'covid_pandemic': {
                'start_date': '2020-02-01',
                'end_date': '2020-04-01',
                'description': 'COVID-19 pandemic market crash'
            },
            '2022_rate_hikes': {
                'start_date': '2022-01-01',
                'end_date': '2022-12-31',
                'description': 'Federal Reserve rate hiking cycle'
            },
            'china_trade_war': {
                'start_date': '2018-03-01',
                'end_date': '2019-12-31',
                'description': 'US-China trade tensions'
            }
        }
        
        # Stress testing parameters
        self.default_confidence_levels = [0.95, 0.99]
        self.monte_carlo_simulations = self.config.get('monte_carlo_simulations', 10000)
        
    def _initialize_default_scenarios(self) -> List[StressScenario]:
        """Initialize default stress scenarios"""
        return [
            # Market crash scenarios
            StressScenario(
                name="Severe_Market_Crash",
                description="Severe market crash with equity drops of 40%+",
                shock_parameters={
                    'equities': -0.45,
                    'bonds': 0.15,
                    'commodities': -0.35,
                    'crypto': -0.60,
                    'real_estate': -0.25
                },
                correlation_changes={
                    'equity_bond': -0.3,  # Becomes more negative
                    'equity_commodity': 0.4,  # Increases correlation
                    'bond_commodity': 0.2
                },
                volatility_multiplier=3.0,
                probability=0.02,  # 2% annual probability
                time_horizon_days=30,
                affected_assets=['equities', 'bonds', 'commodities']
            ),
            
            # Interest rate shock
            StressScenario(
                name="Interest_Rate_Shock",
                description="Sudden interest rate hike of 300 basis points",
                shock_parameters={
                    'long_bonds': -0.20,
                    'short_bonds': -0.05,
                    'financial_stocks': -0.30,
                    'utilities': -0.25,
                    'real_estate': -0.15
                },
                correlation_changes={
                    'bond_equity': -0.4,
                    'duration_sensitive_assets': 0.5
                },
                volatility_multiplier=2.5,
                probability=0.05,
                time_horizon_days=60,
                affected_assets=['bonds', 'interest_sensitive_stocks']
            ),
            
            # Credit crisis
            StressScenario(
                name="Credit_Crisis",
                description="Credit markets seize up with high yield spreads widening",
                shock_parameters={
                    'high_yield_bonds': -0.35,
                    'investment_grade': -0.10,
                    'financial_stocks': -0.40,
                    'emerging_markets': -0.25
                },
                correlation_changes={
                    'credit_equity': 0.8,  # Becomes highly correlated
                    'spread_sensitive': 0.6
                },
                volatility_multiplier=4.0,
                probability=0.03,
                time_horizon_days=90,
                affected_assets=['credit', 'financial', 'emerging_markets']
            ),
            
            # Commodity shock
            StressScenario(
                name="Commodity_Shock",
                description="Major commodity price shock with oil at $30",
                shock_parameters={
                    'oil': -0.50,
                    'gold': 0.20,
                    'agriculture': -0.30,
                    'mining_stocks': -0.40,
                    'energy_stocks': -0.35
                },
                correlation_changes={
                    'oil_equity': -0.3,
                    'gold_dollar': -0.5,
                    'commodity_sensitive': 0.7
                },
                volatility_multiplier=2.0,
                probability=0.08,
                time_horizon_days=45,
                affected_assets=['commodities', 'energy', 'mining']
            ),
            
            # Quantum computing disruption
            StressScenario(
                name="Quantum_Disruption",
                description="Quantum computing disruption of traditional algorithms",
                shock_parameters={
                    'traditional_tech': -0.25,
                    'quantum_stocks': 0.50,
                    'software': -0.15,
                    'cybersecurity': -0.20
                },
                correlation_changes={
                    'tech_sub_sectors': 0.6,
                    'quantum_related': 0.8
                },
                volatility_multiplier=2.5,
                probability=0.10,
                time_horizon_days=120,
                affected_assets=['technology', 'quantum', 'cybersecurity']
            )
        ]
        
    async def run_historical_stress_test(self, portfolio_weights: np.ndarray,
                                       asset_returns: pd.DataFrame,
                                       scenario_name: str) -> StressTestResult:
        """Run historical stress test using past crisis periods"""
        try:
            if scenario_name not in self.historical_periods:
                raise ValueError(f"Unknown historical scenario: {scenario_name}")
                
            period = self.historical_periods[scenario_name]
            start_date = pd.to_datetime(period['start_date'])
            end_date = pd.to_datetime(period['end_date'])
            
            # Filter returns data for the period
            period_returns = asset_returns[(asset_returns.index >= start_date) & 
                                         (asset_returns.index <= end_date)]
            
            if period_returns.empty:
                raise ValueError(f"No data available for period {start_date} to {end_date}")
                
            # Calculate stressed portfolio returns
            portfolio_returns = np.dot(period_returns.values, portfolio_weights)
            
            # Calculate stress metrics
            original_value = 100.0  # Starting portfolio value
            stressed_values = [original_value]
            
            for daily_return in portfolio_returns:
                new_value = stressed_values[-1] * (1 + daily_return)
                stressed_values.append(new_value)
                
            final_value = stressed_values[-1]
            portfolio_loss = original_value - final_value
            loss_percentage = portfolio_loss / original_value
            
            # Calculate risk metrics
            var_95 = np.percentile(portfolio_returns, 5)
            var_99 = np.percentile(portfolio_returns, 1)
            
            tail_returns = portfolio_returns[portfolio_returns <= var_95]
            expected_shortfall = abs(np.mean(tail_returns)) if len(tail_returns) > 0 else 0
            
            # Recovery time estimate (days to recover to 95% of original value)
            recovery_threshold = original_value * 0.95
            recovery_days = 0
            for i, value in enumerate(stressed_values):
                if value >= recovery_threshold:
                    recovery_days = i
                    break
                    
            self.logger.info(f"Historical stress test completed - {scenario_name}: {loss_percentage:.2%} loss")
            
            return StressTestResult(
                scenario_name=scenario_name,
                original_portfolio_value=original_value,
                stressed_portfolio_value=final_value,
                portfolio_loss=portfolio_loss,
                loss_percentage=loss_percentage,
                worst_case_loss=abs(min(portfolio_returns)),
                expected_shortfall=expected_shortfall,
                var_95=abs(var_95),
                var_99=abs(var_99),
                stress_test_timestamp=datetime.now(),
                recovery_time_estimate=recovery_days
            )
            
        except Exception as e:
            self.logger.error(f"Historical stress test failed: {str(e)}")
            raise
            
    async def run_scenario_stress_test(self, portfolio_weights: np.ndarray,
                                     asset_volatility: np.ndarray,
                                     scenario: StressScenario) -> StressTestResult:
        """Run scenario-based stress test"""
        try:
            # Calculate stressed returns for each asset class
            stressed_returns = {}
            
            for asset_class, shock in scenario.shock_parameters.items():
                base_vol = asset_volatility[list(asset_volatility.index).index(asset_class)] \
                          if asset_class in asset_volatility.index else 0.20
                
                # Apply shock and volatility increase
                stressed_vol = base_vol * scenario.volatility_multiplier
                stressed_return = shock + np.random.normal(0, stressed_vol)
                stressed_returns[asset_class] = stressed_return
                
            # Calculate stressed portfolio return
            portfolio_return = sum(stressed_returns.get(asset, 0) * weight 
                                 for asset, weight in zip(asset_volatility.index, portfolio_weights))
            
            # Calculate stress metrics
            original_value = 100.0
            stressed_value = original_value * (1 + portfolio_return)
            portfolio_loss = original_value - stressed_value
            loss_percentage = portfolio_loss / original_value
            
            # Monte Carlo for VaR and ES estimation
            simulations = self.monte_carlo_simulations
            simulated_returns = []
            
            for _ in range(simulations):
                # Generate random stressed returns
                sim_returns = {}
                for asset_class, base_shock in scenario.shock_parameters.items():
                    base_vol = asset_volatility[list(asset_volatility.index).index(asset_class)] \
                              if asset_class in asset_volatility.index else 0.20
                    sim_return = base_shock + np.random.normal(0, base_vol * scenario.volatility_multiplier)
                    sim_returns[asset_class] = sim_return
                    
                # Portfolio return
                sim_portfolio_return = sum(sim_returns.get(asset, 0) * weight 
                                         for asset, weight in zip(asset_volatility.index, portfolio_weights))
                simulated_returns.append(sim_portfolio_return)
                
            simulated_returns = np.array(simulated_returns)
            
            # Calculate risk metrics
            var_95 = abs(np.percentile(simulated_returns, 5))
            var_99 = abs(np.percentile(simulated_returns, 1))
            
            tail_returns = simulated_returns[simulated_returns <= -var_95]
            expected_shortfall = abs(np.mean(tail_returns)) if len(tail_returns) > 0 else 0
            
            # Recovery time estimate
            recovery_days = max(1, scenario.time_horizon_days * loss_percentage * 10)
            
            self.logger.info(f"Scenario stress test completed - {scenario.name}: {loss_percentage:.2%} loss")
            
            return StressTestResult(
                scenario_name=scenario.name,
                original_portfolio_value=original_value,
                stressed_portfolio_value=stressed_value,
                portfolio_loss=portfolio_loss,
                loss_percentage=loss_percentage,
                worst_case_loss=abs(min(simulated_returns)),
                expected_shortfall=expected_shortfall,
                var_95=var_95,
                var_99=var_99,
                stress_test_timestamp=datetime.now(),
                recovery_time_estimate=recovery_days
            )
            
        except Exception as e:
            self.logger.error(f"Scenario stress test failed: {str(e)}")
            raise
            
    async def run_correlation_breakdown_test(self, portfolio_weights: np.ndarray,
                                           correlation_matrix: np.ndarray,
                                           asset_returns: pd.DataFrame) -> Dict[str, Any]:
        """Test portfolio under correlation breakdown scenarios"""
        try:
            # Test different correlation scenarios
            correlation_scenarios = {
                'perfect_positive': 1.0,
                'perfect_negative': -1.0,
                'high_positive': 0.9,
                'high_negative': -0.9,
                'zero_correlation': 0.0,
                'current_correlation': 'current'
            }
            
            results = {}
            
            for scenario_name, target_correlation in correlation_scenarios.items():
                if scenario_name == 'current_correlation':
                    # Use current correlation matrix
                    modified_corr = correlation_matrix.copy()
                else:
                    # Create modified correlation matrix
                    modified_corr = np.ones_like(correlation_matrix)
                    np.fill_diagonal(modified_corr, 1.0)
                    
                    # Set off-diagonal elements to target correlation
                    for i in range(modified_corr.shape[0]):
                        for j in range(i + 1, modified_corr.shape[1]):
                            modified_corr[i, j] = target_correlation
                            modified_corr[j, i] = target_correlation
                            
                # Ensure correlation matrix is valid
                eigenvals = np.linalg.eigvals(modified_corr)
                if np.any(eigenvals <= 0):
                    # Adjust to ensure positive definiteness
                    modified_corr = modified_corr + np.eye(modified_corr.shape[0]) * 0.1
                    
                # Generate returns with modified correlation
                n_assets = len(portfolio_weights)
                n_days = 252  # One year of daily returns
                
                # Generate independent normal variables
                z = np.random.normal(0, 1, (n_days, n_assets))
                
                # Apply correlation structure
                L = np.linalg.cholesky(modified_corr)
                correlated_returns = z @ L.T
                
                # Scale to reasonable volatility
                annual_vol = 0.20  # 20% annual volatility
                daily_vol = annual_vol / np.sqrt(252)
                correlated_returns = correlated_returns * daily_vol
                
                # Calculate portfolio returns
                portfolio_returns = np.dot(correlated_returns, portfolio_weights)
                
                # Calculate metrics
                portfolio_vol = np.std(portfolio_returns) * np.sqrt(252)
                max_drawdown = self._calculate_max_drawdown(portfolio_returns)
                
                results[scenario_name] = {
                    'annual_volatility': portfolio_vol,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': np.mean(portfolio_returns) * 252 / portfolio_vol if portfolio_vol > 0 else 0,
                    'correlation_scenario': target_correlation
                }
                
            self.logger.info(f"Correlation breakdown test completed with {len(results)} scenarios")
            return results
            
        except Exception as e:
            self.logger.error(f"Correlation breakdown test failed: {str(e)}")
            return {}
            
    async def run_liquidity_stress_test(self, portfolio_weights: np.ndarray,
                                      asset_liquidity: Dict[str, float],
                                      stress_liquidity_reduction: float = 0.7) -> Dict[str, Any]:
        """Test portfolio liquidity under stress conditions"""
        try:
            # Calculate current liquidity metrics
            weighted_liquidity = sum(weight * asset_liquidity.get(asset, 0.5) 
                                   for weight, asset in zip(portfolio_weights, asset_liquidity.keys()))
            
            # Stress liquidity by reducing it
            stressed_liquidity = {}
            for asset, liquidity in asset_liquidity.items():
                stressed_liquidity[asset] = liquidity * (1 - stress_liquidity_reduction)
                
            # Calculate stressed liquidity metrics
            weighted_stressed_liquidity = sum(weight * stressed_liquidity.get(asset, 0.1) 
                                            for weight, asset in zip(portfolio_weights, asset_liquidity.keys()))
            
            # Estimate liquidation time
            base_liquidation_time = 1.0  # days
            liquidation_multiplier = (1 - weighted_stressed_liquidity) / max(0.1, weighted_liquidity)
            estimated_liquidation_time = base_liquidation_time * liquidation_multiplier
            
            # Liquidation cost estimation
            base_transaction_cost = 0.001  # 10 basis points
            stressed_transaction_cost = base_transaction_cost * (1 + stress_liquidity_reduction)
            total_liquidation_cost = sum(weight * stressed_transaction_cost 
                                       for weight in portfolio_weights)
            
            liquidity_analysis = {
                'current_liquidity_score': weighted_liquidity,
                'stressed_liquidity_score': weighted_stressed_liquidity,
                'liquidity_reduction_percentage': (weighted_liquidity - weighted_stressed_liquidity) / weighted_liquidity,
                'estimated_liquidation_time_days': estimated_liquidation_time,
                'liquidation_cost_percentage': total_liquidation_cost * 100,
                'liquidity_risk_score': max(0, 1 - weighted_stressed_liquidity),
                'liquidity_stress_level': self._categorize_liquidity_stress(weighted_stressed_liquidity)
            }
            
            self.logger.info(f"Liquidity stress test completed - Liquidity score: {weighted_stressed_liquidity:.3f}")
            return liquidity_analysis
            
        except Exception as e:
            self.logger.error(f"Liquidity stress test failed: {str(e)}")
            return {}
            
    async def run_systematic_stress_test(self, portfolio_weights: np.ndarray,
                                       asset_returns: pd.DataFrame,
                                       asset_volatility: Dict[str, float]) -> Dict[str, Any]:
        """Run comprehensive systematic stress test"""
        try:
            all_results = {}
            
            # Run all scenario tests
            for scenario in self.scenarios:
                result = await self.run_scenario_stress_test(
                    portfolio_weights, 
                    pd.Series(asset_volatility), 
                    scenario
                )
                all_results[scenario.name] = {
                    'loss_percentage': result.loss_percentage,
                    'var_95': result.var_95,
                    'var_99': result.var_99,
                    'expected_shortfall': result.expected_shortfall,
                    'recovery_time': result.recovery_time_estimate,
                    'scenario_description': scenario.description
                }
                
            # Run key historical tests
            historical_scenarios = ['2008_financial_crisis', 'covid_pandemic']
            for hist_scenario in historical_scenarios:
                if hist_scenario in self.historical_periods:
                    result = await self.run_historical_stress_test(
                        portfolio_weights, 
                        asset_returns, 
                        hist_scenario
                    )
                    all_results[hist_scenario] = {
                        'loss_percentage': result.loss_percentage,
                        'var_95': result.var_95,
                        'var_99': result.var_99,
                        'expected_shortfall': result.expected_shortfall,
                        'recovery_time': result.recovery_time_estimate,
                        'scenario_description': self.historical_periods[hist_scenario]['description']
                    }
                    
            # Calculate aggregate stress metrics
            all_losses = [result['loss_percentage'] for result in all_results.values()]
            portfolio_stress_metrics = {
                'worst_case_loss': max(all_losses),
                'average_loss': np.mean(all_losses),
                'stress_var_95': np.percentile(all_losses, 95),
                'stress_var_99': np.percentile(all_losses, 99),
                'tail_loss_expectation': np.mean([loss for loss in all_losses if loss > np.percentile(all_losses, 90)]),
                'resilience_score': 1 - np.std(all_losses),  # Lower volatility = higher resilience
                'total_scenarios_tested': len(all_results),
                'extreme_scenarios_failed': len([loss for loss in all_losses if loss > 0.20])  # >20% loss
            }
            
            # Risk-adjusted stress score
            stress_score = self._calculate_stress_score(portfolio_stress_metrics)
            portfolio_stress_metrics['overall_stress_score'] = stress_score
            
            self.logger.info(f"Systematic stress test completed - Overall stress score: {stress_score:.2f}")
            
            return {
                'individual_results': all_results,
                'aggregate_metrics': portfolio_stress_metrics,
                'stress_level': self._categorize_stress_level(stress_score),
                'recommendations': self._generate_stress_recommendations(all_results, portfolio_stress_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Systematic stress test failed: {str(e)}")
            return {}
            
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return abs(np.min(drawdown))
        
    def _categorize_liquidity_stress(self, liquidity_score: float) -> str:
        """Categorize liquidity stress level"""
        if liquidity_score >= 0.7:
            return "LOW"
        elif liquidity_score >= 0.4:
            return "MEDIUM"
        elif liquidity_score >= 0.2:
            return "HIGH"
        else:
            return "CRITICAL"
            
    def _calculate_stress_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall stress score (0-100, higher is worse)"""
        weights = {
            'worst_case_loss': 0.3,
            'stress_var_99': 0.25,
            'tail_loss_expectation': 0.2,
            'extreme_scenarios_failed': 0.15,
            'resilience_score': 0.1
        }
        
        score = 0
        for metric, weight in weights.items():
            if metric == 'resilience_score':
                # For resilience score, lower is better
                score += (1 - metrics[metric]) * weight * 100
            else:
                score += metrics[metric] * weight * 100
                
        return min(100, max(0, score))
        
    def _categorize_stress_level(self, stress_score: float) -> str:
        """Categorize overall stress level"""
        if stress_score <= 20:
            return "LOW"
        elif stress_score <= 40:
            return "MODERATE"
        elif stress_score <= 60:
            return "HIGH"
        elif stress_score <= 80:
            return "VERY_HIGH"
        else:
            return "EXTREME"
            
    def _generate_stress_recommendations(self, results: Dict[str, Any], 
                                       metrics: Dict[str, float]) -> List[str]:
        """Generate stress test recommendations"""
        recommendations = []
        
        # Worst case recommendations
        if metrics['worst_case_loss'] > 0.30:
            recommendations.append("Portfolio shows extreme vulnerability - consider significant diversification")
            
        # VaR recommendations
        if metrics['stress_var_99'] > 0.25:
            recommendations.append("High tail risk detected - implement tail hedging strategies")
            
        # Recovery time recommendations
        if metrics['worst_case_loss'] > 0.15:
            recovery_years = metrics['worst_case_loss'] / 0.10  # Assume 10% annual recovery rate
            recommendations.append(f"Recovery may take {recovery_years:.1f} years - consider more defensive positioning")
            
        # Liquidity recommendations
        # This would be added if liquidity test results were included
        # if liquidity_stress == "HIGH" or liquidity_stress == "CRITICAL":
        #     recommendations.append("Poor liquidity under stress - increase allocation to liquid assets")
            
        # Diversification recommendations
        if metrics['extreme_scenarios_failed'] > 3:
            recommendations.append("Too many scenarios show extreme losses - improve diversification")
            
        # Resilience recommendations
        if metrics['resilience_score'] < 0.3:
            recommendations.append("Low resilience score - portfolio too concentrated or correlated")
            
        return recommendations
        
    def add_custom_scenario(self, scenario: StressScenario):
        """Add custom stress scenario"""
        self.scenarios.append(scenario)
        self.logger.info(f"Added custom stress scenario: {scenario.name}")
        
    def remove_scenario(self, scenario_name: str):
        """Remove stress scenario"""
        self.scenarios = [s for s in self.scenarios if s.name != scenario_name]
        self.logger.info(f"Removed stress scenario: {scenario_name}")
        
    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """Get list of available stress scenarios"""
        return [
            {
                'name': scenario.name,
                'description': scenario.description,
                'probability': scenario.probability,
                'time_horizon': scenario.time_horizon_days,
                'affected_assets': scenario.affected_assets
            }
            for scenario in self.scenarios
        ]

# Usage example
async def example_stress_testing():
    """Example stress testing usage"""
    # Create stress testing framework
    framework = StressTestingFramework()
    
    # Mock portfolio data
    portfolio_weights = np.array([0.3, 0.25, 0.2, 0.15, 0.1])  # 5 assets
    asset_volatility = pd.Series([0.20, 0.25, 0.18, 0.22, 0.30])
    
    # Mock asset returns (in production, this would be real data)
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
    n_assets = len(portfolio_weights)
    returns_data = np.random.normal(0.001, 0.02, (len(dates), n_assets))
    asset_returns = pd.DataFrame(returns_data, index=dates)
    
    # Run scenario stress test
    scenario = framework.scenarios[0]  # Severe market crash
    result = await framework.run_scenario_stress_test(portfolio_weights, asset_volatility, scenario)
    
    print(f"Scenario: {result.scenario_name}")
    print(f"Portfolio Loss: {result.loss_percentage:.2%}")
    print(f"VaR (95%): {result.var_95:.2%}")
    print(f"Expected Shortfall: {result.expected_shortfall:.2%}")
    print(f"Recovery Time: {result.recovery_time_estimate:.1f} days")
    
    # Run systematic stress test
    systematic_results = await framework.run_systematic_stress_test(
        portfolio_weights, asset_returns, asset_volatility.to_dict()
    )
    
    print(f"\\nSystematic Stress Test Results:")
    print(f"Overall Stress Score: {systematic_results['aggregate_metrics']['overall_stress_score']:.1f}")
    print(f"Stress Level: {systematic_results['stress_level']}")
    print(f"Worst Case Loss: {systematic_results['aggregate_metrics']['worst_case_loss']:.2%}")
    print(f"\\nRecommendations:")
    for rec in systematic_results['recommendations']:
        print(f"- {rec}")

if __name__ == "__main__":
    asyncio.run(example_stress_testing())