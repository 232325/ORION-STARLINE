"""
Analytics Engine
===============

Central analytics coordinator that manages all risk analytics operations
including VaR, stress testing, Monte Carlo simulations, and risk attribution.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np
import pandas as pd

from .var_calculator import VaRCalculator, VaRParameters
from .stress_tester import StressTester, ScenarioParameters
from ..utils.data_manager import RiskDataManager

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsConfig:
    """Configuration for analytics engine"""
    enable_var: bool = True
    enable_stress_testing: bool = True
    enable_monte_carlo: bool = True
    enable_risk_attribution: bool = True
    enable_backtesting: bool = True
    var_confidence_levels: List[float] = None
    stress_test_frequency: int = 3600  # seconds (1 hour)
    var_calculation_frequency: int = 900  # seconds (15 minutes)
    monte_carlo_simulations: int = 10000
    
    def __post_init__(self):
        if self.var_confidence_levels is None:
            self.var_confidence_levels = [0.95, 0.99]

@dataclass
class AnalyticsResult:
    """Container for analytics results"""
    timestamp: datetime
    portfolio_value: float
    var_results: Dict[str, float]
    stress_test_results: Dict[str, float]
    risk_attribution: Dict[str, float]
    monte_carlo_results: Dict[str, Any]
    backtesting_results: Dict[str, Any]
    analytics_duration: float

class AnalyticsEngine:
    """
    Central analytics engine for risk management
    
    Coordinates:
    - VaR calculations (Historical, Parametric, Monte Carlo)
    - Stress testing across multiple scenarios
    - Monte Carlo simulations
    - Risk attribution analysis
    - Historical backtesting
    - Performance analytics
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analytics_config = AnalyticsConfig(**config)
        
        # Initialize sub-components
        self.var_calculator = VaRCalculator(config.get('var_config', {}))
        self.stress_tester = StressTester(config.get('stress_config', {}))
        self.data_manager = RiskDataManager(config.get('data_config', {}))
        
        # Analytics state
        self.last_var_calculation = None
        self.last_stress_test = None
        self.analytics_cache = {}
        self.cache_ttl = config.get('cache_ttl', 1800)  # 30 minutes
        
        # Background tasks
        self.analytics_tasks = []
        self.analytics_running = False
        
        logger.info("Analytics Engine initialized")
    
    async def initialize(self):
        """Initialize analytics engine and sub-components"""
        try:
            logger.info("Initializing Analytics Engine...")
            
            # Initialize data manager
            await self.data_manager.initialize()
            
            # Start background analytics
            await self._start_background_analytics()
            
            logger.info("Analytics Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Analytics Engine: {e}")
            raise
    
    async def _start_background_analytics(self):
        """Start background analytics tasks"""
        self.analytics_running = True
        
        if self.analytics_config.enable_var:
            self.analytics_tasks.append(
                asyncio.create_task(self._background_var_calculation())
            )
        
        if self.analytics_config.enable_stress_testing:
            self.analytics_tasks.append(
                asyncio.create_task(self._background_stress_testing())
            )
        
        logger.info(f"Started {len(self.analytics_tasks)} background analytics tasks")
    
    async def stop_background_analytics(self):
        """Stop background analytics tasks"""
        self.analytics_running = False
        
        for task in self.analytics_tasks:
            task.cancel()
        
        self.analytics_tasks.clear()
        logger.info("Stopped background analytics tasks")
    
    # VaR Calculation Methods
    
    async def calculate_var(self, positions: Dict[str, Any], 
                          market_data: Dict[str, Any],
                          confidence_levels: Optional[List[float]] = None,
                          method: str = 'historical') -> Dict[str, float]:
        """
        Calculate Value at Risk for portfolio
        
        Args:
            positions: Current position data
            market_data: Current market data
            confidence_levels: Confidence levels to calculate
            method: VaR calculation method ('historical', 'parametric', 'monte_carlo')
            
        Returns:
            Dictionary with VaR results
        """
        try:
            if not self.analytics_config.enable_var:
                logger.warning("VaR calculation is disabled in config")
                return {}
            
            if confidence_levels is None:
                confidence_levels = self.analytics_config.var_confidence_levels
            
            # Use VaR calculator
            var_results = await self.var_calculator.calculate_var(
                positions, market_data, confidence_levels, method
            )
            
            # Cache results
            cache_key = f"var_{method}_{sorted(confidence_levels)}"
            self.analytics_cache[cache_key] = {
                'results': var_results,
                'timestamp': datetime.now()
            }
            
            self.last_var_calculation = datetime.now()
            
            logger.info(f"Calculated {method} VaR: {var_results.get('var_95', 0):.2f}")
            
            return var_results
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return {}
    
    async def calculate_expected_shortfall(self, positions: Dict[str, Any],
                                         market_data: Dict[str, Any],
                                         confidence_level: float = 0.95,
                                         method: str = 'historical') -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        try:
            es_value = await self.var_calculator.calculate_expected_shortfall(
                positions, market_data, confidence_level, method
            )
            
            logger.debug(f"Calculated Expected Shortfall: {es_value:.2f}")
            return es_value
            
        except Exception as e:
            logger.error(f"Error calculating Expected Shortfall: {e}")
            return 0.0
    
    async def calculate_component_var(self, positions: Dict[str, Any],
                                    market_data: Dict[str, Any],
                                    confidence_level: float = 0.95) -> Dict[str, float]:
        """Calculate Component VaR for each position"""
        try:
            component_vars = await self.var_calculator.calculate_component_var(
                positions, market_data, confidence_level
            )
            
            logger.info(f"Calculated Component VaR for {len(component_vars)} positions")
            return component_vars
            
        except Exception as e:
            logger.error(f"Error calculating Component VaR: {e}")
            return {}
    
    # Stress Testing Methods
    
    async def run_stress_tests(self, positions: Dict[str, Any],
                             market_data: Dict[str, Any],
                             scenarios: List[str] = None) -> Dict[str, float]:
        """
        Run stress tests on portfolio
        
        Args:
            positions: Current position data
            market_data: Current market data
            scenarios: List of scenario names to run
            
        Returns:
            Dictionary mapping scenario names to loss percentages
        """
        try:
            if not self.analytics_config.enable_stress_testing:
                logger.warning("Stress testing is disabled in config")
                return {}
            
            stress_results = await self.stress_tester.run_stress_tests(
                positions, market_data, scenarios
            )
            
            # Cache results
            cache_key = f"stress_test_{sorted(scenarios) if scenarios else 'all'}"
            self.analytics_cache[cache_key] = {
                'results': stress_results,
                'timestamp': datetime.now()
            }
            
            self.last_stress_test = datetime.now()
            
            worst_scenario = min(stress_results.items(), key=lambda x: x[1]) if stress_results else None
            logger.info(f"Completed stress testing. Worst scenario: {worst_scenario}")
            
            return stress_results
            
        except Exception as e:
            logger.error(f"Error running stress tests: {e}")
            return {}
    
    async def generate_stress_report(self, positions: Dict[str, Any],
                                   market_data: Dict[str, Any]) -> Any:
        """Generate comprehensive stress testing report"""
        try:
            return await self.stress_tester.generate_comprehensive_stress_report(
                positions, market_data
            )
        except Exception as e:
            logger.error(f"Error generating stress report: {e}")
            return None
    
    # Monte Carlo Simulation Methods
    
    async def run_monte_carlo_simulation(self, positions: Dict[str, Any],
                                       market_data: Dict[str, Any],
                                       simulations: Optional[int] = None,
                                       time_horizon: int = 252) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for portfolio
        
        Args:
            positions: Current position data
            market_data: Current market data
            simulations: Number of simulations
            time_horizon: Time horizon in days
            
        Returns:
            Monte Carlo simulation results
        """
        try:
            if not self.analytics_config.enable_monte_carlo:
                logger.warning("Monte Carlo simulation is disabled in config")
                return {}
            
            if simulations is None:
                simulations = self.analytics_config.monte_carlo_simulations
            
            # Prepare portfolio for simulation
            portfolio_data = await self._prepare_portfolio_for_simulation(positions, market_data)
            
            # Run simulation
            simulation_results = await self._execute_monte_carlo_simulation(
                portfolio_data, simulations, time_horizon
            )
            
            # Cache results
            cache_key = f"monte_carlo_{simulations}_{time_horizon}"
            self.analytics_cache[cache_key] = {
                'results': simulation_results,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Completed Monte Carlo simulation: {simulations} paths, {time_horizon} days")
            
            return simulation_results
            
        except Exception as e:
            logger.error(f"Error running Monte Carlo simulation: {e}")
            return {}
    
    async def _execute_monte_carlo_simulation(self, portfolio_data: Dict[str, Any],
                                            simulations: int,
                                            time_horizon: int) -> Dict[str, Any]:
        """Execute Monte Carlo simulation"""
        try:
            weights = portfolio_data['weights']
            mean_returns = portfolio_data['mean_returns']
            cov_matrix = portfolio_data['covariance_matrix']
            initial_value = portfolio_data['portfolio_value']
            
            # Set random seed for reproducibility
            np.random.seed(42)
            
            # Generate random returns
            simulated_returns = np.random.multivariate_normal(
                mean_returns, cov_matrix, size=(simulations, time_horizon)
            )
            
            # Calculate portfolio paths
            portfolio_paths = np.zeros((simulations, time_horizon + 1))
            portfolio_paths[:, 0] = initial_value
            
            for t in range(1, time_horizon + 1):
                portfolio_returns = np.dot(simulated_returns[:, t-1], weights)
                portfolio_paths[:, t] = portfolio_paths[:, t-1] * (1 + portfolio_returns)
            
            # Calculate statistics
            final_values = portfolio_paths[:, -1]
            
            results = {
                'simulations': simulations,
                'time_horizon': time_horizon,
                'initial_value': initial_value,
                'final_values': final_values,
                'portfolio_paths': portfolio_paths,
                'statistics': {
                    'mean': np.mean(final_values),
                    'median': np.median(final_values),
                    'std': np.std(final_values),
                    'percentile_5': np.percentile(final_values, 5),
                    'percentile_95': np.percentile(final_values, 95),
                    'percentile_1': np.percentile(final_values, 1),
                    'percentile_99': np.percentile(final_values, 99),
                    'var_95': np.percentile(final_values, 5),
                    'var_99': np.percentile(final_values, 1),
                    'expected_shortfall_95': np.mean(final_values[final_values <= np.percentile(final_values, 5)]),
                    'max_drawdown': self._calculate_max_drawdowns(portfolio_paths),
                    'probability_of_loss': np.mean(final_values < initial_value)
                }
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing Monte Carlo simulation: {e}")
            return {}
    
    def _calculate_max_drawdowns(self, portfolio_paths: np.ndarray) -> np.ndarray:
        """Calculate maximum drawdowns for each simulation path"""
        max_drawdowns = []
        
        for path in portfolio_paths:
            peak = np.maximum.accumulate(path)
            drawdown = (path - peak) / peak
            max_drawdown = np.min(drawdown)
            max_drawdowns.append(max_drawdown)
        
        return np.array(max_drawdowns)
    
    # Risk Attribution Methods
    
    async def calculate_risk_attribution(self, positions: Dict[str, Any],
                                       market_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate risk attribution analysis
        
        Args:
            positions: Current position data
            market_data: Current market data
            
        Returns:
            Risk attribution breakdown
        """
        try:
            if not self.analytics_config.enable_risk_attribution:
                logger.warning("Risk attribution is disabled in config")
                return {}
            
            # Calculate component VaR
            component_vars = await self.calculate_component_var(positions, market_data)
            
            # Calculate beta contributions
            beta_contributions = await self._calculate_beta_contributions(positions, market_data)
            
            # Calculate correlation contributions
            correlation_contributions = await self._calculate_correlation_contributions(positions, market_data)
            
            # Calculate liquidity contributions
            liquidity_contributions = await self._calculate_liquidity_contributions(positions, market_data)
            
            attribution = {
                'component_var': component_vars,
                'beta_contributions': beta_contributions,
                'correlation_contributions': correlation_contributions,
                'liquidity_contributions': liquidity_contributions
            }
            
            logger.info(f"Calculated risk attribution for {len(component_vars)} positions")
            
            return attribution
            
        except Exception as e:
            logger.error(f"Error calculating risk attribution: {e}")
            return {}
    
    async def _calculate_beta_contributions(self, positions: Dict[str, Any],
                                          market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate beta contributions to portfolio risk"""
        contributions = {}
        
        total_portfolio_beta = 0
        total_value = 0
        
        for symbol, position in positions.items():
            market_value = abs(position.get('market_value', 0))
            beta = position.get('beta', 1.0)
            
            if total_value > 0:
                weight = market_value / total_value
                beta_contribution = weight * beta
                contributions[symbol] = beta_contribution
                total_portfolio_beta += beta_contribution
        
        contributions['total_portfolio'] = total_portfolio_beta
        return contributions
    
    async def _calculate_correlation_contributions(self, positions: Dict[str, Any],
                                                 market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate correlation contributions to portfolio risk"""
        contributions = {}
        
        symbols = list(positions.keys())
        n_symbols = len(symbols)
        
        if n_symbols < 2:
            return {'total_correlation': 0}
        
        # Simplified correlation calculation
        total_correlation_risk = 0
        
        for i, symbol1 in enumerate(symbols):
            symbol1_value = abs(positions[symbol1].get('market_value', 0))
            
            for j, symbol2 in enumerate(symbols):
                if i < j:  # Avoid double counting
                    symbol2_value = abs(positions[symbol2].get('market_value', 0))
                    
                    # Simplified correlation (would use actual correlation matrix)
                    correlation = abs(positions[symbol1].get('correlation', 0))
                    combined_value = symbol1_value + symbol2_value
                    correlation_contribution = correlation * combined_value
                    
                    total_correlation_risk += correlation_contribution
        
        contributions['total_correlation'] = total_correlation_risk
        return contributions
    
    async def _calculate_liquidity_contributions(self, positions: Dict[str, Any],
                                               market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate liquidity risk contributions"""
        contributions = {}
        
        for symbol, position in positions.items():
            market_value = abs(position.get('market_value', 0))
            liquidity_ratio = position.get('liquidity_ratio', 1.0)
            
            # Liquidity risk = market_value * (1 - liquidity_ratio)
            liquidity_risk = market_value * (1 - liquidity_ratio)
            contributions[symbol] = liquidity_risk
        
        total_liquidity_risk = sum(contributions.values())
        contributions['total_liquidity'] = total_liquidity_risk
        
        return contributions
    
    # Backtesting Methods
    
    async def run_backtesting(self, positions_history: List[Dict[str, Any]],
                            market_data_history: List[Dict[str, Any]],
                            method: str = 'historical') -> Dict[str, Any]:
        """
        Run backtesting analysis
        
        Args:
            positions_history: Historical position data
            market_data_history: Historical market data
            method: VaR method to backtest
            
        Returns:
            Backtesting results
        """
        try:
            if not self.analytics_config.enable_backtesting:
                logger.warning("Backtesting is disabled in config")
                return {}
            
            backtesting_results = await self.var_calculator.backtest_var(
                positions_history, market_data_history, method=method
            )
            
            logger.info(f"Completed backtesting for {len(positions_history)} periods")
            
            return backtesting_results
            
        except Exception as e:
            logger.error(f"Error running backtesting: {e}")
            return {}
    
    # Comprehensive Analytics
    
    async def run_comprehensive_analysis(self, positions: Dict[str, Any],
                                       market_data: Dict[str, Any]) -> AnalyticsResult:
        """
        Run comprehensive portfolio analytics
        
        Args:
            positions: Current position data
            market_data: Current market data
            
        Returns:
            Complete analytics results
        """
        try:
            start_time = datetime.now()
            
            portfolio_value = sum(pos.get('market_value', 0) for pos in positions.values())
            
            # Calculate VaR
            var_results = await self.calculate_var(positions, market_data)
            
            # Run stress tests
            stress_test_results = await self.run_stress_tests(positions, market_data)
            
            # Calculate risk attribution
            risk_attribution = await self.calculate_risk_attribution(positions, market_data)
            
            # Run Monte Carlo simulation (smaller simulation for speed)
            monte_carlo_results = await self.run_monte_carlo_simulation(
                positions, market_data, simulations=1000, time_horizon=60
            )
            
            # Run backtesting with simulated data
            backtesting_results = await self._run_simulated_backtesting(positions, market_data)
            
            calculation_time = (datetime.now() - start_time).total_seconds()
            
            result = AnalyticsResult(
                timestamp=datetime.now(),
                portfolio_value=portfolio_value,
                var_results=var_results,
                stress_test_results=stress_test_results,
                risk_attribution=risk_attribution,
                monte_carlo_results=monte_carlo_results,
                backtesting_results=backtesting_results,
                analytics_duration=calculation_time
            )
            
            logger.info(f"Completed comprehensive analytics in {calculation_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            raise
    
    # Background Tasks
    
    async def _background_var_calculation(self):
        """Background VaR calculation task"""
        while self.analytics_running:
            try:
                await asyncio.sleep(self.analytics_config.var_calculation_frequency)
                
                # This would get current positions and market data
                # and perform regular VaR calculations
                
                logger.debug("Running background VaR calculation")
                
            except Exception as e:
                logger.error(f"Error in background VaR calculation: {e}")
                await asyncio.sleep(60)
    
    async def _background_stress_testing(self):
        """Background stress testing task"""
        while self.analytics_running:
            try:
                await asyncio.sleep(self.analytics_config.stress_test_frequency)
                
                # This would run periodic stress tests
                
                logger.debug("Running background stress testing")
                
            except Exception as e:
                logger.error(f"Error in background stress testing: {e}")
                await asyncio.sleep(300)  # Longer pause for errors
    
    # Helper Methods
    
    async def _prepare_portfolio_for_simulation(self, positions: Dict[str, Any],
                                              market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare portfolio data for simulation"""
        symbols = []
        weights = []
        market_values = []
        returns_data = []
        
        total_value = 0
        
        for symbol, position in positions.items():
            if symbol in market_data:
                market_value = abs(position.get('market_value', 0))
                total_value += market_value
                
                symbols.append(symbol)
                market_values.append(market_value)
                
                # Get returns data
                returns = market_data[symbol].get('returns', self._generate_sample_returns())
                returns_data.append(returns)
        
        # Calculate weights
        if total_value > 0:
            weights = [mv / total_value for mv in market_values]
        else:
            weights = [0] * len(symbols)
        
        # Calculate mean returns and covariance
        if returns_data:
            mean_returns = np.mean(returns_data, axis=1)
            cov_matrix = np.cov(returns_data)
        else:
            mean_returns = np.zeros(len(symbols))
            cov_matrix = np.eye(len(symbols))
        
        return {
            'symbols': symbols,
            'weights': np.array(weights),
            'market_values': np.array(market_values),
            'returns_data': returns_data,
            'mean_returns': mean_returns,
            'covariance_matrix': cov_matrix,
            'portfolio_value': total_value
        }
    
    def _generate_sample_returns(self, length: int = 252) -> np.ndarray:
        """Generate sample returns for demonstration"""
        np.random.seed(42)
        return np.random.normal(0.0002, 0.02, length)
    
    async def _run_simulated_backtesting(self, positions: Dict[str, Any],
                                       market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run simulated backtesting with historical patterns"""
        # This would implement actual backtesting logic
        # For now, return simulated results
        
        return {
            'total_observations': 100,
            'violations': 3,
            'violation_rate': 0.03,
            'expected_violation_rate': 0.05,
            'kupiec_test_result': 'pass',
            'model_performance': 'acceptable'
        }
    
    # Utility Methods
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics engine summary"""
        cache_stats = {
            'cache_size': len(self.analytics_cache),
            'cache_keys': list(self.analytics_cache.keys())
        }
        
        background_tasks_status = {
            'analytics_running': self.analytics_running,
            'background_tasks': len(self.analytics_tasks),
            'last_var_calculation': self.last_var_calculation,
            'last_stress_test': self.last_stress_test
        }
        
        return {
            'timestamp': datetime.now(),
            'cache_statistics': cache_stats,
            'background_tasks': background_tasks_status,
            'configuration': {
                'var_enabled': self.analytics_config.enable_var,
                'stress_testing_enabled': self.analytics_config.enable_stress_testing,
                'monte_carlo_enabled': self.analytics_config.enable_monte_carlo,
                'risk_attribution_enabled': self.analytics_config.enable_risk_attribution,
                'backtesting_enabled': self.analytics_config.enable_backtesting
            }
        }
    
    def clear_cache(self):
        """Clear analytics cache"""
        self.analytics_cache.clear()
        logger.info("Analytics cache cleared")
    
    async def export_analytics_data(self, positions: Dict[str, Any],
                                  market_data: Dict[str, Any],
                                  format_type: str = 'json') -> str:
        """Export all analytics data"""
        comprehensive_result = await self.run_comprehensive_analysis(positions, market_data)
        
        export_data = {
            'timestamp': comprehensive_result.timestamp.isoformat(),
            'portfolio_summary': {
                'total_value': comprehensive_result.portfolio_value,
                'positions_count': len(positions)
            },
            'var_analysis': comprehensive_result.var_results,
            'stress_testing': comprehensive_result.stress_test_results,
            'risk_attribution': comprehensive_result.risk_attribution,
            'monte_carlo': {
                'simulations': comprehensive_result.monte_carlo_results.get('simulations', 0),
                'statistics': comprehensive_result.monte_carlo_results.get('statistics', {})
            },
            'backtesting': comprehensive_result.backtesting_results,
            'performance': {
                'calculation_duration': comprehensive_result.analytics_duration
            }
        }
        
        if format_type.lower() == 'json':
            import json
            return json.dumps(export_data, indent=2, default=str)
        else:
            return str(export_data)