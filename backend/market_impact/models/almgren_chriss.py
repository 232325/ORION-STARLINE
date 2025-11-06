"""
Almgren-Chriss Price Impact Model

Bu model optimal execution va temporary va permanent price impact larni hisobga oladi.

Model assumptions:
- Permanent impact: Market microstructure ta'siri
- Temporary impact: Order book dan sarflash
- Optimal execution: Risk-return trade-off

Robert Almgren va Neil Chriss tomonidan ishlab chiqilgan.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from scipy.optimize import minimize_scalar


@dataclass
class AlmgrenChrissParameters:
    """Almgren-Chriss model parametrlari"""
    eta: float  # Permanent impact coefficient
    gamma: float  # Temporary impact coefficient  
    sigma: float  # Asset volatility
    T: float  # Trading horizon
    lambda_risk: float  # Risk aversion parameter


class AlmgrenChrissModel:
    """
    Almgren-Chriss Model - Optimal execution va price impact
    """
    
    def __init__(self, parameters: AlmgrenChrissParameters):
        """
        Initialize model
        
        Args:
            parameters: Model parametrlari
        """
        self.eta = parameters.eta
        self.gamma = parameters.gamma
        self.sigma = parameters.sigma
        self.T = parameters.T
        self.lambda_risk = parameters.lambda_risk
        
    def calculate_permanent_impact(self, trade_rate: float) -> float:
        """
        Permanent price impact hisoblash
        
        Args:
            trade_rate: Trade tezligi (shares per unit time)
            
        Returns:
            Permanent price impact
        """
        # Permanent impact proportional to trade rate
        permanent_impact = self.eta * trade_rate
        return permanent_impact
        
    def calculate_temporary_impact(self, trade_rate: float, 
                                 remaining_shares: float) -> float:
        """
        Temporary price impact hisoblash
        
        Args:
            trade_rate: Trade tezligi
            remaining_shares: Qolgan shares soni
            
        Returns:
            Temporary price impact
        """
        # Temporary impact depends on trade rate and urgency
        urgency_factor = 1.0 + remaining_shares / 1000  # More urgent when fewer shares left
        temporary_impact = self.gamma * trade_rate * urgency_factor
        return temporary_impact
        
    def calculate_total_impact(self, trade_rate: float, 
                             remaining_shares: float) -> float:
        """
        Total price impact hisoblash
        
        Args:
            trade_rate: Trade tezligi
            remaining_shares: Qolgan shares soni
            
        Returns:
            Total price impact
        """
        permanent = self.calculate_permanent_impact(trade_rate)
        temporary = self.calculate_temporary_impact(trade_rate, remaining_shares)
        
        return permanent + temporary
        
    def optimal_trade_rate(self, x: float, s: float) -> float:
        """
        Optimal trade rate hisoblash
        
        Args:
            x: Shares to trade
            s: Remaining shares
            
        Returns:
            Optimal trade rate
        """
        # Optimal rate formula: nu = x/T + lambda * sigma^2 * (x - s*T/2) / (2*gamma)
        optimal_rate = (x / self.T + 
                       self.lambda_risk * self.sigma**2 * (x - s * self.T / 2) / (2 * self.gamma))
        
        return optimal_rate
        
    def calculate_implementation_shortfall(self, initial_shares: float,
                                        optimal_execution: bool = True) -> Dict[str, float]:
        """
        Implementation shortfall hisoblash
        
        Args:
            initial_shares: Boshlang'ich shares soni
            optimal_execution: Optimal execution yoki naive execution
            
        Returns:
            Implementation shortfall components
        """
        if optimal_execution:
            # Optimal execution strategy
            T_half = self.T / 2
            
            # Permanent cost component
            permanent_cost = self.eta * initial_shares**2 / (2 * self.T)
            
            # Temporary cost component  
            temporary_cost = (self.gamma * initial_shares**3) / (3 * self.T**2)
            
            # Risk cost component
            risk_cost = self.lambda_risk * self.sigma**2 * initial_shares**2 / (4 * self.T)
            
        else:
            # Naive execution strategy (constant rate)
            # All at once
            permanent_cost = self.eta * initial_shares**2
            temporary_cost = self.gamma * initial_shares**2
            risk_cost = 0.0
            
        total_shortfall = permanent_cost + temporary_cost + risk_cost
        
        return {
            'permanent_cost': permanent_cost,
            'temporary_cost': temporary_cost,
            'risk_cost': risk_cost,
            'total_shortfall': total_shortfall,
            'bps_cost': total_shortfall / initial_shares * 10000
        }
        
    def generate_optimal_execution_schedule(self, total_shares: int,
                                         num_intervals: int = 100) -> Dict[str, np.ndarray]:
        """
        Optimal execution schedule yaratish
        
        Args:
            total_shares: Umumiy shares soni
            num_intervals: Intervals soni
            
        Returns:
            Execution schedule
        """
        # Time intervals
        time_steps = np.linspace(0, self.T, num_intervals + 1)
        dt = self.T / num_intervals
        
        # Initialize arrays
        shares_remaining = np.zeros(len(time_steps))
        trade_rates = np.zeros(len(time_steps))
        prices = np.zeros(len(time_steps))
        
        # Initial conditions
        shares_remaining[0] = total_shares
        trade_rates[0] = total_shares / self.T  # Initial optimal rate
        prices[0] = 100.0  # Starting price
        
        # Optimal execution simulation
        for i in range(1, len(time_steps)):
            s = shares_remaining[i-1]
            shares_left = i * dt  # Time elapsed
            
            # Optimal trade rate
            optimal_rate = self.optimal_trade_rate(total_shares, shares_left)
            
            # Execute trades
            shares_traded = optimal_rate * dt
            shares_remaining[i] = max(0, s - shares_traded)
            trade_rates[i-1] = optimal_rate
            
            # Price impact
            impact = self.calculate_total_impact(optimal_rate, shares_remaining[i])
            prices[i] = prices[i-1] + impact
            
        # Add final trade to complete execution
        if shares_remaining[-1] > 0:
            final_rate = shares_remaining[-1] / dt
            trade_rates[-1] = final_rate
            
        return {
            'time_steps': time_steps,
            'shares_remaining': shares_remaining,
            'trade_rates': trade_rates,
            'prices': prices,
            'cumulative_cost': self.calculate_cumulative_cost(trade_rates, dt)
        }
        
    def calculate_cumulative_cost(self, trade_rates: np.ndarray, dt: float) -> np.ndarray:
        """
        Cumulative trading cost hisoblash
        
        Args:
            trade_rates: Trade rates
            dt: Time step
            
        Returns:
            Cumulative costs
        """
        cumulative_cost = np.zeros(len(trade_rates))
        
        for i in range(1, len(trade_rates)):
            # Calculate cost for this period
            cost = (self.eta * trade_rates[i-1]**2 + 
                   self.gamma * trade_rates[i-1]**2) * dt
            
            cumulative_cost[i] = cumulative_cost[i-1] + cost
            
        return cumulative_cost
        
    def backtest_execution_strategy(self, historical_data: pd.DataFrame,
                                  shares_to_trade: int) -> Dict[str, float]:
        """
        Execution strategy backtesting
        
        Args:
            historical_data: Historical price data
            shares_to_trade: Shares to trade
            
        Returns:
            Backtest results
        """
        if len(historical_data) < 100:
            return {'error': 'Insufficient data for backtesting'}
            
        # Generate optimal schedule
        schedule = self.generate_optimal_execution_schedule(shares_to_trade)
        
        # Simulate execution with actual price data
        actual_costs = []
        simulated_costs = []
        
        for i in range(len(schedule['trade_rates'])):
            # Get actual price from data (simplified - would need to map to actual timestamps)
            if i < len(historical_data):
                actual_price = historical_data.iloc[i]['close']
            else:
                actual_price = historical_data.iloc[-1]['close']
                
            # Actual cost with slippage
            trade_rate = schedule['trade_rates'][i]
            actual_slippage = 0.001 * trade_rate  # 1 bp per unit rate
            actual_cost = actual_price * (1 + actual_slippage)
            actual_costs.append(actual_cost)
            
            # Model predicted cost
            model_impact = self.calculate_total_impact(trade_rate, shares_to_trade * (1 - i/len(schedule['trade_rates'])))
            model_cost = actual_price * (1 + model_impact)
            simulated_costs.append(model_cost)
            
        # Calculate metrics
        total_actual_cost = sum(actual_costs)
        total_model_cost = sum(simulated_costs)
        cost_difference = total_actual_cost - total_model_cost
        
        return {
            'total_actual_cost': total_actual_cost,
            'total_model_cost': total_model_cost,
            'cost_difference': cost_difference,
            'relative_error': cost_difference / total_actual_cost if total_actual_cost > 0 else 0,
            'schedule': schedule
        }
        
    def optimize_risk_parameters(self, target_cost_reduction: float = 0.1) -> Dict[str, float]:
        """
        Risk parameters optimization
        
        Args:
            target_cost_reduction: Target cost reduction
            
        Returns:
            Optimized parameters
        """
        def objective(lambda_risk):
            # Calculate cost with this lambda
            params = AlmgrenChrissParameters(
                eta=self.eta, gamma=self.gamma, sigma=self.sigma,
                T=self.T, lambda_risk=lambda_risk
            )
            model = AlmgrenChrissModel(params)
            cost = model.calculate_implementation_shortfall(1000)['total_shortfall']
            
            # Target: minimize cost with constraint on reduction
            return abs(cost - target_cost_reduction)
            
        # Optimize
        result = minimize_scalar(objective, bounds=(0.001, 10.0), method='bounded')
        
        return {
            'optimal_lambda_risk': result.x,
            'optimized_cost': objective(result.x),
            'cost_reduction': self.calculate_implementation_shortfall(1000)['total_shortfall'] - objective(result.x)
        }
        
    def estimate_impact_coefficients(self, trade_data: pd.DataFrame) -> Dict[str, float]:
        """
        Impact coefficients estimation
        
        Args:
            trade_data: Trade execution data
            
        Returns:
            Estimated coefficients
        """
        if len(trade_data) < 50:
            return {'error': 'Insufficient data for estimation'}
            
        # Required columns: trade_size, price_impact, volatility
        trade_sizes = trade_data['trade_size'].values
        price_impacts = trade_data['price_impact'].values
        volatilities = trade_data.get('volatility', [self.sigma] * len(trade_sizes))
        
        # Model: price_impact = eta * trade_rate + gamma * trade_rate^2
        # Linear regression approach
        from scipy import stats
        
        # Prepare data
        trade_rates = trade_sizes  # Assuming unit time
        x = np.column_stack([trade_rates, trade_rates**2])
        
        # Regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, price_impacts)
        
        return {
            'eta_estimate': slope,
            'gamma_estimate': intercept,
            'r_squared': r_value ** 2,
            'correlation': np.corrcoef(trade_rates, price_impacts)[0, 1]
        }
        
    def calculate_volatility_impact(self, volatility_surface: np.ndarray,
                                  time_horizon: float) -> Dict[str, float]:
        """
        Volatility impact hisoblash
        
        Args:
            volatility_surface: Volatility surface (different strikes/times)
            time_horizon: Time horizon
            
        Returns:
            Volatility impact metrics
        """
        # Calculate average volatility impact
        avg_volatility = np.mean(volatility_surface)
        
        # Risk cost scales with volatility
        risk_cost_impact = self.lambda_risk * avg_volatility**2 * time_horizon
        
        # Temporary cost also affected by volatility
        temp_cost_impact = self.gamma * avg_volatility * 0.5  # Adjustment factor
        
        return {
            'avg_volatility': avg_volatility,
            'risk_cost_impact': risk_cost_impact,
            'temporary_cost_impact': temp_cost_impact,
            'total_volatility_impact': risk_cost_impact + temp_cost_impact
        }
        
    def get_model_statistics(self) -> Dict[str, float]:
        """
        Model statistikalari
        
        Returns:
            Dictionary with model statistics
        """
        return {
            'eta': self.eta,
            'gamma': self.gamma,
            'sigma': self.sigma,
            'T': self.T,
            'lambda_risk': self.lambda_risk,
            'permanent_impact_sensitivity': self.eta,
            'temporary_impact_sensitivity': self.gamma,
            'volatility_sensitivity': self.sigma
        }
        
    def compare_strategies(self, total_shares: int) -> Dict[str, Dict[str, float]]:
        """
        Different execution strategies ni taqqoslash
        
        Args:
            total_shares: Umumiy shares soni
            
        Returns:
            Strategy comparison
        """
        strategies = {}
        
        # Optimal Almgren-Chriss
        ac_result = self.calculate_implementation_shortfall(total_shares, optimal_execution=True)
        strategies['Almgren-Chriss'] = ac_result
        
        # VWAP strategy (constant rate)
        vwap_params = AlmgrenChrissParameters(
            eta=self.eta, gamma=self.gamma, sigma=self.sigma,
            T=self.T, lambda_risk=0.0  # No risk consideration
        )
        vwap_model = AlmgrenChrissModel(vwap_params)
        vwap_result = vwap_model.calculate_implementation_shortfall(total_shares, optimal_execution=False)
        strategies['VWAP'] = vwap_result
        
        # Aggressive strategy (all at once)
        aggressive_params = AlmgrenChrissParameters(
            eta=self.eta*2, gamma=self.gamma*2, sigma=self.sigma,
            T=0.01, lambda_risk=0.0  # Very short horizon
        )
        aggressive_model = AlmgrenChrissModel(aggressive_params)
        aggressive_result = aggressive_model.calculate_implementation_shortfall(total_shares, optimal_execution=False)
        strategies['Aggressive'] = aggressive_result
        
        return strategies