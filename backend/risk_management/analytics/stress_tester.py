"""
Stress Testing Engine
====================

Comprehensive stress testing system for portfolio risk assessment.
Tests portfolio performance under various adverse scenarios.
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class StressScenario(Enum):
    """Predefined stress scenarios"""
    MARKET_CRASH = "market_crash"
    VOLATILITY_SPIKE = "volatility_spike"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    CORRELATION_BREAKDOWN = "correlation_breakdown"
    INTEREST_RATE_SHOCK = "interest_rate_shock"
    CURRENCY_DEVALUATION = "currency_devaluation"
    COMMODITY_PRICE_SHOCK = "commodity_price_shock"
    RECESSION_SCENARIO = "recession_scenario"
    GEOPOLITICAL_CRISIS = "geopolitical_crisis"
    REGULATORY_CHANGE = "regulatory_change"

@dataclass
class ScenarioParameters:
    """Parameters defining a stress scenario"""
    name: str
    scenario_type: StressScenario
    description: str
    market_shocks: Dict[str, float] = field(default_factory=dict)  # symbol -> shock %
    volatility_multiplier: float = 1.0
    correlation_shock: float = 0.0  # Additional correlation
    liquidity_impact: float = 0.0  # Liquidity reduction %
    duration_days: int = 10
    probability: float = 0.01  # Annual probability
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class StressTestResult:
    """Result of stress testing"""
    scenario_name: str
    scenario_type: StressScenario
    original_portfolio_value: float
    stressed_portfolio_value: float
    loss_amount: float
    loss_percentage: float
    var_impact: float
    max_drawdown: float
    time_to_recovery: int  # days
    affected_positions: List[Dict[str, Any]] = field(default_factory=list)
    recovery_scenarios: List[Dict[str, float]] = field(default_factory=list)

@dataclass
class StressTestReport:
    """Comprehensive stress testing report"""
    timestamp: datetime
    scenarios_tested: List[StressTestResult]
    worst_case_scenario: StressTestResult
    average_loss: float
    portfolio_resilience_score: float
    recommendations: List[str] = field(default_factory=list)
    stress_test_duration: float

class StressTester:
    """
    Comprehensive stress testing engine
    
    Tests portfolio performance under various adverse scenarios:
    - Market crashes
    - Volatility spikes  
    - Liquidity crises
    - Correlation breakdowns
    - Interest rate shocks
    - Currency devaluations
    - Custom scenarios
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.predefined_scenarios = {}
        self.custom_scenarios = {}
        
        # Initialize predefined scenarios
        self._initialize_predefined_scenarios()
    
    def _initialize_predefined_scenarios(self):
        """Initialize predefined stress scenarios"""
        
        # Market Crash Scenario
        self.predefined_scenarios[StressScenario.MARKET_CRASH] = ScenarioParameters(
            name="Market Crash",
            scenario_type=StressScenario.MARKET_CRASH,
            description="Severe market decline with broad-based sell-off",
            market_shocks={
                'equity': -0.25,      # -25% equity markets
                'AAPL': -0.30,        # Individual stock shocks
                'GOOGL': -0.28,
                'EURUSD': -0.05,      # Forex impact
                'GC': -0.15          # Gold impact
            },
            volatility_multiplier=3.0,
            correlation_shock=0.3,
            liquidity_impact=0.5,
            duration_days=10,
            probability=0.02
        )
        
        # Volatility Spike Scenario
        self.predefined_scenarios[StressScenario.VOLATILITY_SPIKE] = ScenarioParameters(
            name="Volatility Spike",
            scenario_type=StressScenario.VOLATILITY_SPIKE,
            description="Extreme volatility increase without directional bias",
            market_shocks={
                'equity': 0.0,        # No directional bias
                'forex': 0.0,
                'commodity': 0.0
            },
            volatility_multiplier=5.0,
            correlation_shock=0.5,
            liquidity_impact=0.3,
            duration_days=5,
            probability=0.05
        )
        
        # Liquidity Crisis Scenario
        self.predefined_scenarios[StressScenario.LIQUIDITY_CRISIS] = ScenarioParameters(
            name="Liquidity Crisis",
            scenario_type=StressScenario.LIQUIDITY_CRISIS,
            description="Severe liquidity reduction across markets",
            market_shocks={
                'equity': -0.15,
                'forex': -0.10,
                'commodity': -0.20
            },
            volatility_multiplier=2.0,
            correlation_shock=0.4,
            liquidity_impact=0.8,  # 80% liquidity reduction
            duration_days=20,
            probability=0.01
        )
        
        # Correlation Breakdown Scenario
        self.predefined_scenarios[StressScenario.CORRELATION_BREAKDOWN] = ScenarioParameters(
            name="Correlation Breakdown",
            scenario_type=StressScenario.CORRELATION_BREAKDOWN,
            description="Historical correlations break down, assets move independently",
            market_shocks={
                'equity': -0.10,
                'forex': 0.05,
                'commodity': -0.15
            },
            volatility_multiplier=2.5,
            correlation_shock=0.9,  # High correlation shock
            liquidity_impact=0.2,
            duration_days=30,
            probability=0.03
        )
        
        # Interest Rate Shock Scenario
        self.predefined_scenarios[StressScenario.INTEREST_RATE_SHOCK] = ScenarioParameters(
            name="Interest Rate Shock",
            scenario_type=StressScenario.INTEREST_RATE_SHOCK,
            description="Sudden interest rate changes impact rates-sensitive assets",
            market_shocks={
                'equity': -0.12,
                'forex': 0.08,        # Currency impact from rate differentials
                'commodity': -0.05
            },
            volatility_multiplier=2.0,
            correlation_shock=0.2,
            liquidity_impact=0.1,
            duration_days=15,
            probability=0.04
        )
        
        # Currency Devaluation Scenario
        self.predefined_scenarios[StressScenario.CURRENCY_DEVALUATION] = ScenarioParameters(
            name="Currency Devaluation",
            scenario_type=StressScenario.CURRENCY_DEVALUATION,
            description="Major currency devaluation affecting international holdings",
            market_shocks={
                'EURUSD': -0.15,      # Euro devaluation
                'equity': -0.08,      # Equity impact from currency effects
                'commodity': 0.05     # Commodity benefit from weaker currency
            },
            volatility_multiplier=2.5,
            correlation_shock=0.3,
            liquidity_impact=0.4,
            duration_days=25,
            probability=0.02
        )
        
        # Commodity Price Shock Scenario
        self.predefined_scenarios[StressScenario.COMMODITY_PRICE_SHOCK] = ScenarioParameters(
            name="Commodity Price Shock",
            scenario_type=StressScenario.COMMODITY_PRICE_SHOCK,
            description="Sudden commodity price movements",
            market_shocks={
                'GC': -0.35,          # Gold price shock
                'equity': -0.06,
                'forex': 0.03
            },
            volatility_multiplier=3.0,
            correlation_shock=0.2,
            liquidity_impact=0.3,
            duration_days=12,
            probability=0.03
        )
        
        logger.info(f"Initialized {len(self.predefined_scenarios)} predefined stress scenarios")
    
    async def run_stress_tests(self, positions: Dict[str, Any],
                             market_data: Dict[str, Any],
                             scenarios: List[str] = None,
                             custom_scenarios: List[ScenarioParameters] = None) -> Dict[str, float]:
        """
        Run stress tests on portfolio
        
        Args:
            positions: Current portfolio positions
            market_data: Current market data
            scenarios: List of scenario names to run
            custom_scenarios: Custom scenario parameters
            
        Returns:
            Dictionary mapping scenario names to loss amounts
        """
        try:
            start_time = datetime.now()
            
            # Default to running all predefined scenarios
            if scenarios is None:
                scenarios = list(self.predefined_scenarios.keys())
            
            results = {}
            
            # Prepare portfolio data
            portfolio_value = sum(pos.get('market_value', 0) for pos in positions.values())
            
            # Run predefined scenarios
            for scenario_name in scenarios:
                if scenario_name in self.predefined_scenarios:
                    scenario = self.predefined_scenarios[scenario_name]
                    result = await self._run_single_stress_test(
                        positions, market_data, scenario, portfolio_value
                    )
                    results[scenario_name] = result.loss_percentage
                else:
                    logger.warning(f"Unknown scenario: {scenario_name}")
            
            # Run custom scenarios
            if custom_scenarios:
                for i, custom_scenario in enumerate(custom_scenarios):
                    scenario_name = f"custom_scenario_{i+1}"
                    result = await self._run_single_stress_test(
                        positions, market_data, custom_scenario, portfolio_value
                    )
                    results[scenario_name] = result.loss_percentage
            
            total_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Completed stress testing for {len(results)} scenarios in {total_time:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Error running stress tests: {e}")
            raise
    
    async def _run_single_stress_test(self, positions: Dict[str, Any],
                                    market_data: Dict[str, Any],
                                    scenario: ScenarioParameters,
                                    portfolio_value: float) -> StressTestResult:
        """Run a single stress test scenario"""
        try:
            # Apply market shocks
            stressed_positions = await self._apply_market_shocks(
                positions, market_data, scenario
            )
            
            # Calculate stressed portfolio value
            stressed_portfolio_value = sum(
                pos.get('stressed_market_value', 0) 
                for pos in stressed_positions.values()
            )
            
            # Calculate impacts
            loss_amount = portfolio_value - stressed_portfolio_value
            loss_percentage = loss_amount / portfolio_value if portfolio_value > 0 else 0
            
            # Calculate VaR impact
            var_impact = await self._calculate_var_impact(
                positions, stressed_positions, portfolio_value
            )
            
            # Calculate max drawdown
            max_drawdown = await self._calculate_max_drawdown(
                positions, stressed_positions
            )
            
            # Estimate recovery time
            time_to_recovery = await self._estimate_recovery_time(
                scenario, loss_percentage
            )
            
            # Get affected positions
            affected_positions = self._identify_affected_positions(
                positions, stressed_positions
            )
            
            # Generate recovery scenarios
            recovery_scenarios = await self._generate_recovery_scenarios(
                scenario, loss_percentage
            )
            
            return StressTestResult(
                scenario_name=scenario.name,
                scenario_type=scenario.scenario_type,
                original_portfolio_value=portfolio_value,
                stressed_portfolio_value=stressed_portfolio_value,
                loss_amount=abs(loss_amount),
                loss_percentage=abs(loss_percentage),
                var_impact=abs(var_impact),
                max_drawdown=abs(max_drawdown),
                time_to_recovery=time_to_recovery,
                affected_positions=affected_positions,
                recovery_scenarios=recovery_scenarios
            )
            
        except Exception as e:
            logger.error(f"Error running stress test for {scenario.name}: {e}")
            raise
    
    async def _apply_market_shocks(self, positions: Dict[str, Any],
                                 market_data: Dict[str, Any],
                                 scenario: ScenarioParameters) -> Dict[str, Any]:
        """Apply market shocks to positions"""
        stressed_positions = {}
        
        for symbol, position in positions.items():
            stressed_position = position.copy()
            
            # Get base shock for this asset
            shock_pct = self._get_shock_for_symbol(symbol, position, scenario)
            
            # Apply volatility multiplier
            if scenario.volatility_multiplier > 1.0:
                volatility_shock = np.random.normal(0, 0.02 * scenario.volatility_multiplier)
                shock_pct += volatility_shock
            
            # Calculate stressed price and value
            current_price = position.get('current_price', 0)
            original_market_value = position.get('market_value', 0)
            
            stressed_price = current_price * (1 + shock_pct)
            stressed_market_value = original_market_value * (1 + shock_pct)
            
            # Apply liquidity impact
            if scenario.liquidity_impact > 0:
                # Reduce stressed value further due to liquidity
                liquidity_adjustment = 1 - (scenario.liquidity_impact * 0.5)
                stressed_market_value *= liquidity_adjustment
            
            # Update position with stressed values
            stressed_position.update({
                'stressed_price': stressed_price,
                'stressed_market_value': stressed_market_value,
                'shock_applied': shock_pct,
                'liquidity_impact': scenario.liquidity_impact
            })
            
            stressed_positions[symbol] = stressed_position
        
        return stressed_positions
    
    def _get_shock_for_symbol(self, symbol: str, position: Dict[str, Any],
                            scenario: ScenarioParameters) -> float:
        """Get shock percentage for a specific symbol"""
        
        # First check for specific symbol shocks
        if symbol in scenario.market_shocks:
            return scenario.market_shocks[symbol]
        
        # Then check for asset class shocks
        asset_class = position.get('asset_class', 'unknown')
        if asset_class in scenario.market_shocks:
            return scenario.market_shocks[asset_class]
        
        # Default shock for unknown symbols
        return scenario.market_shocks.get('default', 0.0)
    
    async def _calculate_var_impact(self, original_positions: Dict[str, Any],
                                  stressed_positions: Dict[str, Any],
                                  original_portfolio_value: float) -> float:
        """Calculate VaR impact from stress scenario"""
        try:
            # Simplified VaR impact calculation
            original_var = 0.02 * original_portfolio_value  # Assume 2% VaR
            
            stressed_portfolio_value = sum(
                pos.get('stressed_market_value', 0) 
                for pos in stressed_positions.values()
            )
            
            stressed_var = 0.05 * stressed_portfolio_value  # Assume higher VaR in stress
            
            return stressed_var - original_var
            
        except Exception as e:
            logger.error(f"Error calculating VaR impact: {e}")
            return 0.0
    
    async def _calculate_max_drawdown(self, original_positions: Dict[str, Any],
                                    stressed_positions: Dict[str, Any]) -> float:
        """Calculate maximum drawdown from stress scenario"""
        try:
            original_total = sum(pos.get('market_value', 0) for pos in original_positions.values())
            stressed_total = sum(pos.get('stressed_market_value', 0) for pos in stressed_positions.values())
            
            if original_total > 0:
                return (stressed_total - original_total) / original_total
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    async def _estimate_recovery_time(self, scenario: ScenarioParameters,
                                    loss_percentage: float) -> int:
        """Estimate time to recover from stress scenario"""
        try:
            # Base recovery time on scenario duration and loss severity
            base_recovery = scenario.duration_days
            
            # Adjust based on loss severity
            if loss_percentage > 0.3:  # >30% loss
                recovery_multiplier = 3.0
            elif loss_percentage > 0.15:  # >15% loss
                recovery_multiplier = 2.0
            elif loss_percentage > 0.05:  # >5% loss
                recovery_multiplier = 1.5
            else:
                recovery_multiplier = 1.0
            
            return int(base_recovery * recovery_multiplier)
            
        except Exception as e:
            logger.error(f"Error estimating recovery time: {e}")
            return scenario.duration_days
    
    def _identify_affected_positions(self, original_positions: Dict[str, Any],
                                   stressed_positions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify positions most affected by stress scenario"""
        affected = []
        
        for symbol in original_positions:
            if symbol in stressed_positions:
                original_pos = original_positions[symbol]
                stressed_pos = stressed_positions[symbol]
                
                original_value = original_pos.get('market_value', 0)
                stressed_value = stressed_pos.get('stressed_market_value', 0)
                
                if original_value > 0:
                    impact_pct = (original_value - stressed_value) / original_value
                    
                    if abs(impact_pct) > 0.01:  # More than 1% impact
                        affected.append({
                            'symbol': symbol,
                            'asset_class': original_pos.get('asset_class', 'unknown'),
                            'original_value': original_value,
                            'stressed_value': stressed_value,
                            'impact_amount': original_value - stressed_value,
                            'impact_percentage': impact_pct
                        })
        
        # Sort by impact amount
        affected.sort(key=lambda x: abs(x['impact_amount']), reverse=True)
        return affected[:10]  # Top 10 most affected
    
    async def _generate_recovery_scenarios(self, scenario: ScenarioParameters,
                                         loss_percentage: float) -> List[Dict[str, float]]:
        """Generate potential recovery scenarios"""
        scenarios = []
        
        # Base recovery rate
        base_recovery_rate = 0.05  # 5% per day base
        
        # Adjust based on scenario type and severity
        if scenario.scenario_type == StressScenario.LIQUIDITY_CRISIS:
            recovery_rate = base_recovery_rate * 0.3  # Slower recovery
        elif scenario.scenario_type == StressScenario.MARKET_CRASH:
            recovery_rate = base_recovery_rate * 0.5  # Moderate recovery
        else:
            recovery_rate = base_recovery_rate
        
        # Generate different recovery paths
        for i, days in enumerate([30, 60, 90, 180]):
            recovery_pct = min(1.0, recovery_rate * days)
            recovery_scenarios.append({
                'scenario': f'recovery_scenario_{i+1}',
                'recovery_days': days,
                'recovery_percentage': recovery_pct,
                'remaining_loss': max(0, loss_percentage * (1 - recovery_pct))
            })
        
        return recovery_scenarios
    
    async def generate_comprehensive_stress_report(self, positions: Dict[str, Any],
                                                 market_data: Dict[str, Any]) -> StressTestReport:
        """Generate comprehensive stress testing report"""
        try:
            start_time = datetime.now()
            
            # Run all predefined scenarios
            all_scenarios = list(StressScenario)
            stress_results = await self.run_stress_tests(positions, market_data, all_scenarios)
            
            # Convert to detailed results
            detailed_results = []
            portfolio_value = sum(pos.get('market_value', 0) for pos in positions.values())
            
            for scenario_name in stress_results:
                if scenario_name in self.predefined_scenarios:
                    scenario = self.predefined_scenarios[scenario_name]
                    detailed_result = await self._run_single_stress_test(
                        positions, market_data, scenario, portfolio_value
                    )
                    detailed_results.append(detailed_result)
            
            # Find worst case scenario
            if detailed_results:
                worst_case = max(detailed_results, key=lambda x: abs(x.loss_percentage))
            else:
                worst_case = None
            
            # Calculate average loss
            losses = [abs(r.loss_percentage) for r in detailed_results]
            average_loss = np.mean(losses) if losses else 0.0
            
            # Calculate resilience score (0-100)
            if worst_case:
                resilience_score = max(0, 100 - abs(worst_case.loss_percentage) * 100)
            else:
                resilience_score = 100.0
            
            # Generate recommendations
            recommendations = self._generate_stress_recommendations(detailed_results)
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            return StressTestReport(
                timestamp=datetime.now(),
                scenarios_tested=detailed_results,
                worst_case_scenario=worst_case,
                average_loss=average_loss,
                portfolio_resilience_score=resilience_score,
                recommendations=recommendations,
                stress_test_duration=total_time
            )
            
        except Exception as e:
            logger.error(f"Error generating comprehensive stress report: {e}")
            raise
    
    def _generate_stress_recommendations(self, stress_results: List[StressTestResult]) -> List[str]:
        """Generate risk management recommendations based on stress test results"""
        recommendations = []
        
        # Analyze results
        losses = [abs(r.loss_percentage) for r in stress_results]
        worst_loss = max(losses) if losses else 0
        
        if worst_loss > 0.3:  # >30% worst case loss
            recommendations.append("Portfolio shows extreme vulnerability. Consider significant risk reduction.")
        elif worst_loss > 0.2:  # >20% loss
            recommendations.append("Portfolio shows high vulnerability. Implement additional risk controls.")
        elif worst_loss > 0.1:  # >10% loss
            recommendations.append("Moderate vulnerability detected. Review position concentrations.")
        
        # Analyze scenarios with highest impact
        sorted_results = sorted(stress_results, key=lambda x: abs(x.loss_percentage), reverse=True)
        
        if sorted_results:
            top_scenarios = sorted_results[:3]
            scenario_names = [r.scenario_name for r in top_scenarios]
            recommendations.append(f"Most vulnerable to: {', '.join(scenario_names)}. Diversify accordingly.")
        
        # Check recovery times
        long_recovery = [r for r in stress_results if r.time_to_recovery > 90]
        if long_recovery:
            recommendations.append("Some scenarios show extended recovery periods. Improve liquidity management.")
        
        # Check for diversification issues
        equity_focused_losses = [r for r in stress_results if 'equity' in r.scenario_name.lower()]
        if equity_focused_losses:
            recommendations.append("Portfolio is heavily equity-focused. Consider diversifying across asset classes.")
        
        return recommendations
    
    def add_custom_scenario(self, scenario: ScenarioParameters):
        """Add a custom stress scenario"""
        self.custom_scenarios[scenario.name] = scenario
        logger.info(f"Added custom stress scenario: {scenario.name}")
    
    def remove_scenario(self, scenario_name: str) -> bool:
        """Remove a custom scenario"""
        if scenario_name in self.custom_scenarios:
            del self.custom_scenarios[scenario_name]
            logger.info(f"Removed custom scenario: {scenario_name}")
            return True
        return False
    
    def get_available_scenarios(self) -> Dict[str, str]:
        """Get list of available stress scenarios"""
        all_scenarios = {}
        
        # Add predefined scenarios
        for scenario_type, scenario in self.predefined_scenarios.items():
            all_scenarios[scenario_type.value] = scenario.description
        
        # Add custom scenarios
        for name, scenario in self.custom_scenarios.items():
            all_scenarios[f"custom_{name}"] = scenario.description
        
        return all_scenarios
    
    async def export_stress_test_data(self, positions: Dict[str, Any],
                                    market_data: Dict[str, Any],
                                    format_type: str = 'json') -> str:
        """Export stress test data"""
        report = await self.generate_comprehensive_stress_report(positions, market_data)
        
        export_data = {
            'timestamp': report.timestamp.isoformat(),
            'summary': {
                'scenarios_tested': len(report.scenarios_tested),
                'worst_case_loss': report.worst_case_scenario.loss_percentage if report.worst_case_scenario else 0,
                'average_loss': report.average_loss,
                'resilience_score': report.portfolio_resilience_score,
                'test_duration': report.stress_test_duration
            },
            'scenario_results': [
                {
                    'name': result.scenario_name,
                    'loss_percentage': result.loss_percentage,
                    'loss_amount': result.loss_amount,
                    'max_drawdown': result.max_drawdown,
                    'recovery_time': result.time_to_recovery
                }
                for result in report.scenarios_tested
            ],
            'recommendations': report.recommendations
        }
        
        if format_type.lower() == 'json':
            return json.dumps(export_data, indent=2, default=str)
        else:
            return str(export_data)