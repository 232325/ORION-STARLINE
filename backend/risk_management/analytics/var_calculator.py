"""
Value at Risk (VaR) Calculator
=============================

Calculates various VaR measures including historical VaR, parametric VaR,
and Monte Carlo VaR for portfolio risk assessment.
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from scipy import stats
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class VaRResult:
    """VaR calculation result structure"""
    method: str
    confidence_level: float
    var_value: float
    expected_shortfall: float
    window_size: int
    timestamp: datetime
    calculation_time: float
    positions_count: int

@dataclass
class VaRParameters:
    """Parameters for VaR calculation"""
    confidence_levels: List[float] = None
    holding_period: int = 1  # days
    window_size: int = 252   # days
    method: str = 'historical'  # 'historical', 'parametric', 'monte_carlo'
    alpha: float = 0.05  # For Expected Shortfall
    monte_carlo_simulations: int = 10000
    
    def __post_init__(self):
        if self.confidence_levels is None:
            self.confidence_levels = [0.95, 0.99]

class VaRCalculator:
    """
    Value at Risk (VaR) Calculator
    
    Calculates multiple VaR measures:
    - Historical VaR
    - Parametric VaR (Variance-Covariance)
    - Monte Carlo VaR
    - Expected Shortfall (Conditional VaR)
    - Component VaR
    - Marginal VaR
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache = {}
        self.cache_ttl = config.get('cache_ttl', 300)  # 5 minutes
        
    async def calculate_var(self, positions: Dict[str, Any], 
                          market_data: Dict[str, Any],
                          confidence_levels: Optional[List[float]] = None,
                          method: str = 'historical',
                          holding_period: int = 1) -> Dict[str, float]:
        """
        Calculate VaR for portfolio
        
        Args:
            positions: Current position data
            market_data: Market data for risk calculation
            confidence_levels: Confidence levels to calculate
            method: VaR calculation method
            holding_period: Holding period in days
            
        Returns:
            Dictionary with VaR results
        """
        try:
            start_time = datetime.now()
            
            if confidence_levels is None:
                confidence_levels = [0.95, 0.99]
            
            # Prepare portfolio data
            portfolio_data = await self._prepare_portfolio_data(positions, market_data)
            
            results = {}
            
            if method == 'historical':
                results = await self._calculate_historical_var(
                    portfolio_data, confidence_levels, holding_period
                )
            elif method == 'parametric':
                results = await self._calculate_parametric_var(
                    portfolio_data, confidence_levels, holding_period
                )
            elif method == 'monte_carlo':
                results = await self._calculate_monte_carlo_var(
                    portfolio_data, confidence_levels, holding_period
                )
            else:
                raise ValueError(f"Unknown VaR method: {method}")
            
            # Add metadata
            calculation_time = (datetime.now() - start_time).total_seconds()
            results['calculation_time'] = calculation_time
            results['method'] = method
            results['holding_period'] = holding_period
            results['timestamp'] = datetime.now()
            results['positions_count'] = len(positions)
            
            # Cache results
            cache_key = f"{method}_{holding_period}_{sorted(confidence_levels)}"
            self.cache[cache_key] = {
                'results': results,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Calculated {method} VaR: {results.get('var_95', 0):.2f} "
                       f"(calculation time: {calculation_time:.3f}s)")
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            raise
    
    async def calculate_expected_shortfall(self, positions: Dict[str, Any],
                                         market_data: Dict[str, Any],
                                         confidence_level: float = 0.95,
                                         method: str = 'historical') -> float:
        """
        Calculate Expected Shortfall (Conditional VaR)
        
        Args:
            positions: Current position data
            market_data: Market data
            confidence_level: Confidence level
            method: Calculation method
            
        Returns:
            Expected Shortfall value
        """
        try:
            # Get VaR results with additional data for ES calculation
            var_results = await self.calculate_var(
                positions, market_data, [confidence_level], method
            )
            
            # For historical VaR, ES is the average of returns worse than VaR
            if method == 'historical':
                portfolio_data = await self._prepare_portfolio_data(positions, market_data)
                expected_shortfall = await self._calculate_historical_es(
                    portfolio_data, confidence_level
                )
            else:
                # For parametric VaR, ES = VaR + (volatility * normal_pdf / alpha)
                # This is a simplified calculation
                var_value = var_results.get(f'var_{int(confidence_level*100)}', 0)
                volatility = var_results.get('portfolio_volatility', 0)
                alpha = 1 - confidence_level
                
                # Approximation for normal distribution
                expected_shortfall = var_value + (volatility * stats.norm.pdf(stats.norm.ppf(alpha)) / alpha)
            
            return abs(expected_shortfall)  # Return positive value
            
        except Exception as e:
            logger.error(f"Error calculating Expected Shortfall: {e}")
            return 0.0
    
    async def calculate_component_var(self, positions: Dict[str, Any],
                                    market_data: Dict[str, Any],
                                    confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Calculate Component VaR (contribution of each position to portfolio VaR)
        
        Args:
            positions: Current position data
            market_data: Market data
            confidence_level: Confidence level
            
        Returns:
            Dictionary mapping symbols to their component VaR contributions
        """
        try:
            portfolio_data = await self._prepare_portfolio_data(positions, market_data)
            
            # Calculate portfolio VaR
            portfolio_var = await self._calculate_portfolio_var(
                portfolio_data, confidence_level
            )
            
            # Calculate component VaR for each position
            component_vars = {}
            
            for symbol in portfolio_data['symbols']:
                # Remove symbol from portfolio and recalculate VaR
                portfolio_data_no_symbol = portfolio_data.copy()
                portfolio_data_no_symbol['symbols'] = [s for s in portfolio_data['symbols'] if s != symbol]
                
                portfolio_var_without_symbol = await self._calculate_portfolio_var(
                    portfolio_data_no_symbol, confidence_level
                )
                
                # Component VaR is the difference
                component_var = abs(portfolio_var - portfolio_var_without_symbol)
                component_vars[symbol] = component_var
            
            # Normalize to ensure they sum to portfolio VaR
            total_component_var = sum(component_vars.values())
            if total_component_var > 0:
                normalization_factor = portfolio_var / total_component_var
                for symbol in component_vars:
                    component_vars[symbol] *= normalization_factor
            
            return component_vars
            
        except Exception as e:
            logger.error(f"Error calculating Component VaR: {e}")
            return {}
    
    async def calculate_marginal_var(self, positions: Dict[str, Any],
                                   market_data: Dict[str, Any],
                                   symbol: str,
                                   confidence_level: float = 0.95) -> float:
        """
        Calculate Marginal VaR for a specific position
        
        Args:
            positions: Current position data
            market_data: Market data
            symbol: Symbol to calculate marginal VaR for
            confidence_level: Confidence level
            
        Returns:
            Marginal VaR value
        """
        try:
            portfolio_data = await self._prepare_portfolio_data(positions, market_data)
            
            # Original portfolio VaR
            original_var = await self._calculate_portfolio_var(
                portfolio_data, confidence_level
            )
            
            # Increase position by small amount and recalculate VaR
            position = positions.get(symbol, {})
            if position and symbol in portfolio_data['symbols']:
                # Add 1% to position value
                portfolio_data_modified = portfolio_data.copy()
                position_value = position.get('market_value', 0)
                increment = position_value * 0.01
                
                # This is simplified - would need actual portfolio recalculation
                # For now, return approximation
                marginal_var = increment * 0.02  # 2% volatility assumption
                
                return abs(marginal_var)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating Marginal VaR for {symbol}: {e}")
            return 0.0
    
    async def backtest_var(self, positions_history: List[Dict[str, Any]],
                          market_data_history: List[Dict[str, Any]],
                          confidence_level: float = 0.95,
                          window_size: int = 252) -> Dict[str, Any]:
        """
        Backtest VaR model using historical data
        
        Args:
            positions_history: Historical position data
            market_data_history: Historical market data
            confidence_level: Confidence level
            window_size: Rolling window size
            
        Returns:
            Backtesting results
        """
        try:
            violations = []
            total_observations = 0
            
            for i, (positions, market_data) in enumerate(zip(positions_history, market_data_history)):
                # Calculate VaR for current period
                var_result = await self.calculate_var(
                    positions, market_data, [confidence_level]
                )
                
                var_value = var_result.get(f'var_{int(confidence_level*100)}', 0)
                
                # Calculate actual portfolio return for next period
                if i < len(positions_history) - 1:
                    next_positions = positions_history[i + 1]
                    actual_return = await self._calculate_portfolio_return(positions, next_positions)
                    
                    total_observations += 1
                    
                    # Check for VaR violation
                    if actual_return < -var_value:
                        violations.append({
                            'period': i,
                            'var_value': var_value,
                            'actual_return': actual_return,
                            'violation': True
                        })
            
            # Calculate backtesting statistics
            violation_rate = len(violations) / total_observations if total_observations > 0 else 0
            expected_violation_rate = 1 - confidence_level
            
            # Kupiec test for correct violation rate
            if total_observations > 0 and len(violations) > 0:
                lr_stat = -2 * np.log(
                    ((1 - expected_violation_rate) ** (total_observations - len(violations))) *
                    (expected_violation_rate ** len(violations)) /
                    ((1 - violation_rate) ** (total_observations - len(violations))) *
                    (violation_rate ** len(violations))
                )
                p_value = 1 - stats.chi2.cdf(lr_stat, df=1)
            else:
                lr_stat = 0
                p_value = 1
            
            return {
                'total_observations': total_observations,
                'violations': len(violations),
                'violation_rate': violation_rate,
                'expected_violation_rate': expected_violation_rate,
                'kupiec_lr_statistic': lr_stat,
                'kupiec_p_value': p_value,
                'kupiec_test_result': 'pass' if p_value > 0.05 else 'fail',
                'violation_details': violations
            }
            
        except Exception as e:
            logger.error(f"Error in VaR backtesting: {e}")
            return {}
    
    # Private helper methods
    
    async def _prepare_portfolio_data(self, positions: Dict[str, Any], 
                                    market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare portfolio data for VaR calculation"""
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
                
                # Get historical returns for this symbol
                returns = market_data[symbol].get('returns', self._generate_sample_returns())
                returns_data.append(returns)
        
        # Calculate weights
        if total_value > 0:
            weights = [mv / total_value for mv in market_values]
        else:
            weights = [0] * len(symbols)
        
        return {
            'symbols': symbols,
            'weights': np.array(weights),
            'market_values': np.array(market_values),
            'returns_data': returns_data,
            'total_value': total_value
        }
    
    async def _calculate_historical_var(self, portfolio_data: Dict[str, Any],
                                      confidence_levels: List[float],
                                      holding_period: int) -> Dict[str, float]:
        """Calculate Historical VaR"""
        try:
            symbols = portfolio_data['symbols']
            weights = portfolio_data['weights']
            returns_data = portfolio_data['returns_data']
            
            if not returns_data or len(returns_data) == 0:
                return {f'var_{int(cl*100)}': 0 for cl in confidence_levels}
            
            # Calculate portfolio returns
            portfolio_returns = self._calculate_portfolio_returns(returns_data, weights)
            
            results = {}
            
            for confidence_level in confidence_levels:
                # Calculate VaR using historical quantiles
                alpha = 1 - confidence_level
                var_percentile = np.percentile(portfolio_returns, alpha * 100)
                
                # Scale by holding period
                var_scaled = var_percentile * np.sqrt(holding_period)
                
                # Convert to absolute value
                var_absolute = abs(var_scaled) * portfolio_data['total_value']
                
                results[f'var_{int(confidence_level*100)}'] = var_absolute
                
                # Calculate Expected Shortfall
                tail_returns = [r for r in portfolio_returns if r <= var_percentile]
                if tail_returns:
                    expected_shortfall = np.mean(tail_returns) * np.sqrt(holding_period) * portfolio_data['total_value']
                    results[f'expected_shortfall_{int(confidence_level*100)}'] = abs(expected_shortfall)
            
            # Add portfolio volatility
            portfolio_volatility = np.std(portfolio_returns) * np.sqrt(252)  # Annualized
            results['portfolio_volatility'] = portfolio_volatility
            
            return results
            
        except Exception as e:
            logger.error(f"Error in historical VaR calculation: {e}")
            return {}
    
    async def _calculate_parametric_var(self, portfolio_data: Dict[str, Any],
                                      confidence_levels: List[float],
                                      holding_period: int) -> Dict[str, float]:
        """Calculate Parametric VaR (Variance-Covariance method)"""
        try:
            weights = portfolio_data['weights']
            returns_data = portfolio_data['returns_data']
            
            if not returns_data or len(returns_data) == 0:
                return {f'var_{int(cl*100)}': 0 for cl in confidence_levels}
            
            # Calculate mean returns and covariance matrix
            mean_returns = np.mean(returns_data, axis=1)
            cov_matrix = np.cov(returns_data)
            
            # Portfolio expected return and volatility
            portfolio_expected_return = np.dot(weights, mean_returns)
            portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            results = {}
            
            for confidence_level in confidence_levels:
                # Z-score for confidence level
                z_score = stats.norm.ppf(1 - confidence_level)
                
                # VaR calculation
                var_return = -(portfolio_expected_return + z_score * portfolio_volatility * np.sqrt(holding_period))
                var_absolute = var_return * portfolio_data['total_value']
                
                results[f'var_{int(confidence_level*100)}'] = abs(var_absolute)
            
            results['portfolio_volatility'] = portfolio_volatility * np.sqrt(252)  # Annualized
            
            return results
            
        except Exception as e:
            logger.error(f"Error in parametric VaR calculation: {e}")
            return {}
    
    async def _calculate_monte_carlo_var(self, portfolio_data: Dict[str, Any],
                                       confidence_levels: List[float],
                                       holding_period: int) -> Dict[str, float]:
        """Calculate Monte Carlo VaR"""
        try:
            symbols = portfolio_data['symbols']
            weights = portfolio_data['weights']
            returns_data = portfolio_data['returns_data']
            simulations = self.config.get('monte_carlo_simulations', 10000)
            
            if not returns_data or len(returns_data) == 0:
                return {f'var_{int(cl*100)}': 0 for cl in confidence_levels}
            
            # Calculate parameters
            mean_returns = np.mean(returns_data, axis=1)
            cov_matrix = np.cov(returns_data)
            
            # Generate random returns
            np.random.seed(42)  # For reproducibility
            simulated_returns = np.random.multivariate_normal(
                mean_returns, cov_matrix, size=simulations
            )
            
            # Calculate portfolio returns for each simulation
            portfolio_simulated_returns = np.dot(simulated_returns, weights)
            
            results = {}
            
            for confidence_level in confidence_levels:
                # Calculate VaR from simulated returns
                alpha = 1 - confidence_level
                var_percentile = np.percentile(portfolio_simulated_returns, alpha * 100)
                
                # Scale by holding period
                var_scaled = var_percentile * np.sqrt(holding_period)
                
                # Convert to absolute value
                var_absolute = abs(var_scaled) * portfolio_data['total_value']
                
                results[f'var_{int(confidence_level*100)}'] = var_absolute
            
            # Add portfolio volatility
            results['portfolio_volatility'] = np.std(portfolio_simulated_returns) * np.sqrt(252)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in Monte Carlo VaR calculation: {e}")
            return {}
    
    async def _calculate_portfolio_var(self, portfolio_data: Dict[str, Any],
                                     confidence_level: float) -> float:
        """Calculate VaR for portfolio using historical method"""
        results = await self._calculate_historical_var(
            portfolio_data, [confidence_level], 1
        )
        return results.get(f'var_{int(confidence_level*100)}', 0)
    
    async def _calculate_historical_es(self, portfolio_data: Dict[str, Any],
                                     confidence_level: float) -> float:
        """Calculate Historical Expected Shortfall"""
        symbols = portfolio_data['symbols']
        weights = portfolio_data['weights']
        returns_data = portfolio_data['returns_data']
        
        if not returns_data or len(returns_data) == 0:
            return 0
        
        # Calculate portfolio returns
        portfolio_returns = self._calculate_portfolio_returns(returns_data, weights)
        
        # Calculate VaR percentile
        alpha = 1 - confidence_level
        var_percentile = np.percentile(portfolio_returns, alpha * 100)
        
        # Calculate Expected Shortfall (average of returns worse than VaR)
        tail_returns = [r for r in portfolio_returns if r <= var_percentile]
        
        if tail_returns:
            expected_shortfall = np.mean(tail_returns)
            return abs(expected_shortfall) * portfolio_data['total_value']
        
        return 0
    
    def _calculate_portfolio_returns(self, returns_data: List[np.ndarray], 
                                   weights: np.ndarray) -> np.ndarray:
        """Calculate portfolio returns from individual asset returns"""
        if not returns_data or len(returns_data) == 0:
            return np.array([])
        
        # Ensure all return series have the same length
        min_length = min(len(returns) for returns in returns_data)
        aligned_returns = [returns[-min_length:] for returns in returns_data]
        
        # Stack returns into matrix
        returns_matrix = np.column_stack(aligned_returns)
        
        # Calculate weighted portfolio returns
        portfolio_returns = np.dot(returns_matrix, weights)
        
        return portfolio_returns
    
    async def _calculate_portfolio_return(self, positions1: Dict[str, Any], 
                                        positions2: Dict[str, Any]) -> float:
        """Calculate portfolio return between two periods"""
        # Simplified calculation - would need actual market data
        total_value1 = sum(pos.get('market_value', 0) for pos in positions1.values())
        total_value2 = sum(pos.get('market_value', 0) for pos in positions2.values())
        
        if total_value1 > 0:
            return (total_value2 - total_value1) / total_value1
        
        return 0
    
    def _generate_sample_returns(self, length: int = 252) -> np.ndarray:
        """Generate sample returns for demonstration"""
        np.random.seed(42)  # For reproducibility
        return np.random.normal(0.0002, 0.02, length)  # Daily returns
    
    async def get_cached_var(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached VaR results if still valid"""
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            age = (datetime.now() - cached_data['timestamp']).total_seconds()
            if age < self.cache_ttl:
                return cached_data['results']
        
        return None
    
    def clear_cache(self):
        """Clear VaR calculation cache"""
        self.cache.clear()
        logger.info("VaR calculation cache cleared")
    
    async def export_var_data(self, positions: Dict[str, Any],
                            market_data: Dict[str, Any],
                            format_type: str = 'json') -> str:
        """Export VaR calculation data"""
        var_results = await self.calculate_var(positions, market_data)
        es_results = {}
        
        # Calculate Expected Shortfall for different confidence levels
        for confidence_level in [0.95, 0.99]:
            es_value = await self.calculate_expected_shortfall(
                positions, market_data, confidence_level
            )
            es_results[f'es_{int(confidence_level*100)}'] = es_value
        
        # Calculate Component VaR
        component_vars = await self.calculate_component_var(positions, market_data)
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'var_results': var_results,
            'expected_shortfall': es_results,
            'component_var': component_vars,
            'portfolio_summary': {
                'total_positions': len(positions),
                'symbols': list(positions.keys())
            }
        }
        
        if format_type.lower() == 'json':
            import json
            return json.dumps(export_data, indent=2, default=str)
        else:
            return str(export_data)