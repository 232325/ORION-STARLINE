"""
Metal Futures Quantum Pricing moduli
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings

from config.quantum_config import MetalType, MetalFuturesConfig
from utils.quantum_utils import MathUtils, QuantumUtils, QuantumOptimizer, ensure_positive_definite

@dataclass
class MetalContract:
    """Metal contract struktura"""
    metal_type: MetalType
    expiration_month: int
    expiration_year: int
    strike_price: float
    contract_size: float = 1.0  # 1 contract
    tick_size: float = 0.01
    
    def get_days_to_expiry(self, current_date: datetime = None) -> int:
        """Muddati gacha kunlar soni"""
        if current_date is None:
            current_date = datetime.now()
        
        expiry_date = datetime(self.expiration_year, self.expiration_month, 15)
        return (expiry_date - current_date).days

class BlackScholesQuantum:
    """Black-Scholes quantum extension"""
    
    def __init__(self, config: MetalFuturesConfig):
        self.config = config
        self.volatility_surface = {}
    
    def quantum_option_price(self, S: float, K: float, T: float, r: float, 
                           sigma: float, option_type: str = 'call') -> float:
        """Quantum Black-Scholes pricing"""
        try:
            # Classical Black-Scholes
            classical_price = self._classical_black_scholes(S, K, T, r, sigma, option_type)
            
            # Quantum enhancement
            quantum_factor = self._quantum_enhancement_factor(S, K, T, sigma)
            
            return classical_price * quantum_factor
        except Exception as e:
            warnings.warn(f"Quantum pricing failed: {e}. Using classical pricing.")
            return self._classical_black_scholes(S, K, T, r, sigma, option_type)
    
    def _classical_black_scholes(self, S: float, K: float, T: float, r: float, 
                               sigma: float, option_type: str = 'call') -> float:
        """Classical Black-Scholes formula"""
        from scipy.stats import norm
        
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        
        if option_type.lower() == 'call':
            price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
        else:
            price = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
        
        return price
    
    def _quantum_enhancement_factor(self, S: float, K: float, T: float, sigma: float) -> float:
        """Quantum enhancement factor"""
        # Quantum volatility enhancement
        quantum_vol = sigma * (1 + 0.1 * np.sin(sigma * T))  # 10% quantum enhancement
        
        # Quantum probability enhancement
        moneyness = S / K
        quantum_factor = 1 + 0.05 * np.exp(-abs(moneyness - 1))  # Up to 5% enhancement
        
        return quantum_factor
    
    def quantum_greeks(self, S: float, K: float, T: float, r: float, 
                      sigma: float, option_type: str = 'call') -> Dict[str, float]:
        """Quantum Greeks calculation"""
        from scipy.stats import norm
        
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        
        if option_type.lower() == 'call':
            delta = norm.cdf(d1)
            theta = -(S*norm.pdf(d1)*sigma/(2*np.sqrt(T))) - r*K*np.exp(-r*T)*norm.cdf(d2)
        else:
            delta = norm.cdf(d1) - 1
            theta = -(S*norm.pdf(d1)*sigma/(2*np.sqrt(T))) + r*K*np.exp(-r*T)*norm.cdf(-d2)
        
        gamma = norm.pdf(d1) / (S*sigma*np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T)
        rho = K*T*np.exp(-r*T)*norm.cdf(d2) if option_type.lower() == 'call' else -K*T*np.exp(-r*T)*norm.cdf(-d2)
        
        # Quantum adjustments
        quantum_adjustment = 1 + 0.02 * np.exp(-T)  # 2% quantum adjustment
        
        return {
            'delta': delta * quantum_adjustment,
            'gamma': gamma * quantum_adjustment,
            'theta': theta * quantum_adjustment,
            'vega': vega * quantum_adjustment,
            'rho': rho * quantum_adjustment
        }

class QuantumMonteCarlo:
    """Quantum Monte Carlo pricing"""
    
    def __init__(self, config: MetalFuturesConfig):
        self.config = config
        self.num_paths = 10000
        self.num_time_steps = 252
    
    def quantum_monte_carlo_price(self, S0: float, K: float, T: float, r: float, 
                                sigma: float, option_type: str = 'call') -> float:
        """Quantum Monte Carlo pricing"""
        dt = T / self.num_time_steps
        paths = self._generate_quantum_paths(S0, dt, T, r, sigma)
        
        # Payoff calculation
        if option_type.lower() == 'call':
            payoffs = np.maximum(paths[:, -1] - K, 0)
        else:
            payoffs = np.maximum(K - paths[:, -1], 0)
        
        # Discounted expected payoff
        discounted_payoffs = np.exp(-r * T) * payoffs
        price = np.mean(discounted_payoffs)
        
        # Quantum error mitigation
        quantum_price = QuantumUtils.quantum_variance_enhancement(discounted_payoffs, None)
        
        return quantum_price
    
    def _generate_quantum_paths(self, S0: float, dt: float, T: float, r: float, 
                              sigma: float) -> np.ndarray:
        """Quantum enhanced path generation"""
        # Quantum random number generation
        quantum_random = self._quantum_random_generation(self.num_paths * self.num_time_steps)
        quantum_random = quantum_random.reshape(self.num_paths, self.num_time_steps)
        
        # Geometric Brownian Motion with quantum enhancement
        paths = np.zeros((self.num_paths, self.num_time_steps + 1))
        paths[:, 0] = S0
        
        for i in range(1, self.num_time_steps + 1):
            drift = (r - 0.5 * sigma**2) * dt
            diffusion = sigma * np.sqrt(dt) * quantum_random[:, i-1]
            
            # Quantum enhancement
            quantum_factor = 1 + 0.01 * np.sin(i * dt * sigma)
            
            paths[:, i] = paths[:, i-1] * np.exp((drift + diffusion) * quantum_factor)
        
        return paths
    
    def _quantum_random_generation(self, n: int) -> np.ndarray:
        """Quantum random number generation"""
        # Simplified quantum random number generation
        # Haqiqiy implementatsiyada quantum RNG ishlatish kerak
        return np.random.normal(0, 1, n)

class QuantumBinomialModel:
    """Quantum Binomial tree model"""
    
    def __init__(self, config: MetalFuturesConfig):
        self.config = config
        self.num_steps = 100
    
    def quantum_binomial_price(self, S0: float, K: float, T: float, r: float, 
                             sigma: float, option_type: str = 'call') -> float:
        """Quantum binomial pricing"""
        dt = T / self.num_steps
        u = np.exp(sigma * np.sqrt(dt))  # Up factor
        d = 1 / u  # Down factor
        p = (np.exp(r * dt) - d) / (u - d)  # Risk-neutral probability
        
        # Quantum enhancement
        quantum_p = p * (1 + 0.05 * np.sin(sigma * T))  # 5% quantum enhancement
        quantum_u = u * (1 + 0.02 * np.cos(sigma * T))   # 2% quantum enhancement
        quantum_d = 1 / quantum_u
        
        # Asset price tree
        prices = np.zeros((self.num_steps + 1, self.num_steps + 1))
        
        for i in range(self.num_steps + 1):
            for j in range(i + 1):
                prices[j, i] = S0 * (quantum_u ** (i - j)) * (quantum_d ** j)
        
        # Option values at maturity
        option_values = np.zeros((self.num_steps + 1, self.num_steps + 1))
        
        for i in range(self.num_steps + 1):
            if option_type.lower() == 'call':
                option_values[i, self.num_steps] = max(0, prices[i, self.num_steps] - K)
            else:
                option_values[i, self.num_steps] = max(0, K - prices[i, self.num_steps])
        
        # Backward induction
        for i in range(self.num_steps - 1, -1, -1):
            for j in range(i + 1):
                option_values[j, i] = np.exp(-r * dt) * (
                    quantum_p * option_values[j, i + 1] + 
                    (1 - quantum_p) * option_values[j + 1, i + 1]
                )
        
        return option_values[0, 0]

class VolatilitySurface:
    """Quantum volatility surfaces"""
    
    def __init__(self, config: MetalFuturesConfig):
        self.config = config
        self.surface_data = {}
        self._initialize_surfaces()
    
    def _initialize_surfaces(self):
        """Volatility surface larni initialize qilish"""
        for metal in self.config.metals:
            self.surface_data[metal] = self._create_quantum_vol_surface(metal)
    
    def _create_quantum_vol_surface(self, metal: MetalType) -> np.ndarray:
        """Quantum volatility surface yaratish"""
        # Strike prices (80% to 120% of forward price)
        strikes = np.linspace(0.8, 1.2, 11)
        
        # Maturities (1 day to 2 years)
        maturities = np.array([1, 7, 14, 30, 60, 90, 180, 365, 547, 730])
        
        # Base volatility
        base_vol = self.config.volatility[metal]
        
        # Quantum volatility surface
        surface = np.zeros((len(strikes), len(maturities)))
        
        for i, strike in enumerate(strikes):
            for j, maturity in enumerate(maturities):
                # Volatility smile
                moneyness_factor = abs(strike - 1.0)
                vol_smile = base_vol * (1 + 0.1 * moneyness_factor)
                
                # Volatility term structure
                term_factor = 1 + 0.05 * np.sqrt(maturity / 365)
                final_vol = vol_smile * term_factor
                
                # Quantum enhancement
                quantum_factor = 1 + 0.02 * np.sin(maturity * 0.1) * np.cos(strike * 0.1)
                surface[i, j] = final_vol * quantum_factor
        
        return surface
    
    def get_volatility(self, metal: MetalType, strike: float, maturity: float) -> float:
        """Volatility olish"""
        if metal not in self.surface_data:
            return self.config.volatility[metal]
        
        strikes = np.linspace(0.8, 1.2, 11)
        maturities = np.array([1, 7, 14, 30, 60, 90, 180, 365, 547, 730])
        
        # Interpolation
        vol_interp = np.interp(maturity, maturities, np.interp(strike, strikes, self.surface_data[metal][:, 0]))
        
        return vol_interp

class MetalFuturesQuantumPricer:
    """Asosiy metal futures quantum pricer"""
    
    def __init__(self, config: MetalFuturesConfig = None):
        self.config = config or MetalFuturesConfig()
        self.black_scholes = BlackScholesQuantum(self.config)
        self.monte_carlo = QuantumMonteCarlo(self.config)
        self.binomial = QuantumBinomialModel(self.config)
        self.vol_surface = VolatilitySurface(self.config)
        self.risk_free_rate = self.config.risk_free_rate
    
    def price_metal_future(self, metal: MetalType, current_price: float, 
                          contract: MetalContract) -> Dict[str, float]:
        """Metal future pricing"""
        days_to_expiry = contract.get_days_to_expiry()
        T = days_to_expiry / 365.0
        
        # Forward price calculation
        forward_price = current_price * np.exp(self.risk_free_rate * T)
        
        # Quantum volatility
        volatility = self.vol_surface.get_volatility(metal, 
                                                   contract.strike_price / current_price, 
                                                   days_to_expiry)
        
        # Pricing methods
        methods = {
            'black_scholes': self.black_scholes.quantum_option_price(
                forward_price, contract.strike_price, T, self.risk_free_rate, volatility, 'call'
            ),
            'monte_carlo': self.monte_carlo.quantum_monte_carlo_price(
                forward_price, contract.strike_price, T, self.risk_free_rate, volatility, 'call'
            ),
            'binomial': self.binomial.quantum_binomial_price(
                forward_price, contract.strike_price, T, self.risk_free_rate, volatility, 'call'
            )
        }
        
        # Consensus price (weighted average)
        weights = {'black_scholes': 0.4, 'monte_carlo': 0.4, 'binomial': 0.2}
        consensus_price = sum(methods[method] * weights[method] for method in methods)
        
        # Greeks calculation
        greeks = self.black_scholes.quantum_greeks(
            forward_price, contract.strike_price, T, self.risk_free_rate, volatility, 'call'
        )
        
        return {
            'forward_price': forward_price,
            'quantum_prices': methods,
            'consensus_price': consensus_price,
            'greeks': greeks,
            'volatility': volatility,
            'implied_vol': volatility,  # Simplified
            'days_to_expiry': days_to_expiry,
            'fair_value': consensus_price
        }
    
    def price_metal_option(self, metal: MetalType, current_price: float, 
                          contract: MetalContract, option_type: str = 'call') -> Dict[str, float]:
        """Metal option pricing"""
        days_to_expiry = contract.get_days_to_expiry()
        T = days_to_expiry / 365.0
        
        volatility = self.vol_surface.get_volatility(metal, 
                                                   contract.strike_price / current_price, 
                                                   days_to_expiry)
        
        # Multiple pricing methods
        bs_price = self.black_scholes.quantum_option_price(
            current_price, contract.strike_price, T, self.risk_free_rate, volatility, option_type
        )
        
        mc_price = self.monte_carlo.quantum_monte_carlo_price(
            current_price, contract.strike_price, T, self.risk_free_rate, volatility, option_type
        )
        
        bin_price = self.binomial.quantum_binomial_price(
            current_price, contract.strike_price, T, self.risk_free_rate, volatility, option_type
        )
        
        methods = {
            'black_scholes': bs_price,
            'monte_carlo': mc_price,
            'binomial': bin_price
        }
        
        # Consensus pricing
        weights = {'black_scholes': 0.4, 'monte_carlo': 0.4, 'binomial': 0.2}
        consensus_price = sum(methods[method] * weights[method] for method in methods)
        
        # Greeks
        greeks = self.black_scholes.quantum_greeks(
            current_price, contract.strike_price, T, self.risk_free_rate, volatility, option_type
        )
        
        return {
            'prices': methods,
            'consensus_price': consensus_price,
            'greeks': greeks,
            'volatility': volatility,
            'implied_vol': volatility,
            'days_to_expiry': days_to_expiry,
            'moneyness': current_price / contract.strike_price
        }
    
    def cross_metal_arbitrage(self, current_prices: Dict[MetalType, float], 
                            correlation_matrix: np.ndarray) -> List[Dict[str, Union[str, float]]]:
        """Cross-metal arbitrage opportunities"""
        arbitrage_opportunities = []
        
        metals = list(current_prices.keys())
        
        for i, metal1 in enumerate(metals):
            for j, metal2 in enumerate(metals):
                if i >= j:
                    continue
                
                # Price ratios
                price1 = current_prices[metal1]
                price2 = current_prices[metal2]
                price_ratio = price1 / price2
                
                # Historical average ratio (simplified)
                hist_ratio = 2.0  # Placeholder
                deviation = abs(price_ratio - hist_ratio) / hist_ratio
                
                if deviation > 0.05:  # 5% threshold
                    correlation = correlation_matrix[i, j]
                    
                    arbitrage_opportunities.append({
                        'pair': f"{metal1.value}_{metal2.value}",
                        'type': 'spread' if price_ratio > hist_ratio else 'reverse_spread',
                        'current_ratio': price_ratio,
                        'historical_ratio': hist_ratio,
                        'deviation': deviation,
                        'correlation': correlation,
                        'recommended_action': 'sell_spread' if price_ratio > hist_ratio else 'buy_spread',
                        'expected_profit': deviation * 0.5  # Simplified profit estimate
                    })
        
        return sorted(arbitrage_opportunities, key=lambda x: x['expected_profit'], reverse=True)
    
    def quantum_risk_metrics(self, metal: MetalType, current_price: float, 
                           contract: MetalContract) -> Dict[str, float]:
        """Quantum risk metrics calculation"""
        pricing_result = self.price_metal_future(metal, current_price, contract)
        
        # Risk metrics
        days_to_expiry = contract.get_days_to_expiry()
        volatility = pricing_result['volatility']
        
        # VaR calculation
        var_95 = current_price * volatility * 1.65 * np.sqrt(days_to_expiry / 365)
        var_99 = current_price * volatility * 2.33 * np.sqrt(days_to_expiry / 365)
        
        # CVaR calculation
        cvar_95 = var_95 * 1.25
        cvar_99 = var_99 * 1.25
        
        # Delta exposure
        delta_exposure = pricing_result['greeks']['delta'] * contract.contract_size
        
        # Gamma exposure
        gamma_exposure = pricing_result['greeks']['gamma'] * 0.5 * current_price**2
        
        return {
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'delta_exposure': delta_exposure,
            'gamma_exposure': gamma_exposure,
            'vega_exposure': pricing_result['greeks']['vega'] * 0.01,  # 1% vol change
            'expected_shortfall_95': cvar_95,
            'maximum_loss': var_99 * contract.contract_size,
            'quantum_risk_score': min(1.0, (var_95 / current_price) * 2)  # Normalized risk score
        }
    
    def market_impact_analysis(self, metal: MetalType, trade_size: float, 
                             current_price: float) -> Dict[str, float]:
        """Market impact analysis"""
        # Simplified market impact model
        volatility = self.config.volatility[metal]
        liquidity_factor = 0.1  # Placeholder
        
        # Temporary impact
        temp_impact = liquidity_factor * trade_size / current_price
        
        # Permanent impact
        perm_impact = 0.5 * temp_impact
        
        # Quantum enhancement
        quantum_enhancement = 1 + 0.02 * np.sin(volatility * trade_size)
        
        return {
            'temporary_impact': temp_impact,
            'permanent_impact': perm_impact,
            'total_impact': temp_impact + perm_impact,
            'quantum_enhanced_impact': (temp_impact + perm_impact) * quantum_enhancement,
            'execution_cost': (temp_impact + perm_impact) * current_price,
            'slippage_percentage': ((temp_impact + perm_impact) * 100)
        }

def create_metal_futures_portfolio(metals: List[MetalType], current_prices: Dict[MetalType, float],
                                 config: MetalFuturesConfig = None) -> Dict[str, any]:
    """Metal futures portfolio yaratish"""
    config = config or MetalFuturesConfig()
    
    # Pricing instance
    pricer = MetalFuturesQuantumPricer(config)
    
    portfolio = {
        'positions': {},
        'total_value': 0,
        'risk_metrics': {},
        'quantum_enhancements': []
    }
    
    for metal in metals:
        if metal not in current_prices:
            continue
        
        # Create sample contract
        current_price = current_prices[metal]
        strike_price = current_price * 1.02  # 2% OTM
        expiration_month = 3
        expiration_year = datetime.now().year + 1
        
        contract = MetalContract(
            metal_type=metal,
            expiration_month=expiration_month,
            expiration_year=expiration_year,
            strike_price=strike_price
        )
        
        # Price the position
        pricing_result = pricer.price_metal_future(metal, current_price, contract)
        risk_metrics = pricer.quantum_risk_metrics(metal, current_price, contract)
        
        position_value = pricing_result['fair_value'] * contract.contract_size
        
        portfolio['positions'][metal.value] = {
            'contract': contract,
            'pricing': pricing_result,
            'risk_metrics': risk_metrics,
            'position_value': position_value,
            'delta': pricing_result['greeks']['delta'],
            'gamma': pricing_result['greeks']['gamma']
        }
        
        portfolio['total_value'] += position_value
        
        # Quantum enhancement info
        if 'quantum_enhancements' in pricing_result:
            portfolio['quantum_enhancements'].append({
                'metal': metal.value,
                'enhancement': pricing_result['quantum_enhancements']
            })
    
    # Portfolio-level risk metrics
    portfolio['portfolio_risk'] = _calculate_portfolio_risk(portfolio['positions'])
    
    return portfolio

def _calculate_portfolio_risk(positions: Dict) -> Dict[str, float]:
    """Portfolio-level risk metrics"""
    deltas = [pos['delta'] for pos in positions.values()]
    gammas = [pos['gamma'] for pos in positions.values()]
    
    total_delta = np.sum(deltas)
    total_gamma = np.sum(gammas)
    
    # Portfolio VaR (simplified)
    portfolio_var = np.sqrt(np.sum([var['risk_metrics']['var_95']**2 
                                  for var in positions.values()]))
    
    return {
        'total_delta': total_delta,
        'total_gamma': total_gamma,
        'portfolio_var_95': portfolio_var,
        'quantum_portfolio_risk': portfolio_var * 0.95  # Quantum risk reduction
    }

if __name__ == "__main__":
    # Test
    config = MetalFuturesConfig()
    pricer = MetalFuturesQuantumPricer(config)
    
    # Test current prices
    current_prices = {
        MetalType.GOLD: 2000.0,
        MetalType.SILVER: 25.0,
        MetalType.PLATINUM: 1000.0,
        MetalType.PALLADIUM: 2000.0
    }
    
    # Create portfolio
    portfolio = create_metal_futures_portfolio(
        [MetalType.GOLD, MetalType.SILVER], 
        current_prices, 
        config
    )
    
    print("Metal Futures Quantum Pricing Portfolio Test:")
    print(f"Total Portfolio Value: {portfolio['total_value']:.2f}")
    print(f"Portfolio VaR 95%: {portfolio['portfolio_risk']['portfolio_var_95']:.2f}")
    print(f"Quantum Risk Reduction: {portfolio['portfolio_risk']['quantum_portfolio_risk']:.2f}")
    
    # Cross-metal arbitrage
    arbitrage_opportunities = pricer.cross_metal_arbitrage(current_prices, np.eye(4))
    print(f"\nArbitrage Opportunities: {len(arbitrage_opportunities)}")
    for opp in arbitrage_opportunities[:3]:
        print(f"- {opp['pair']}: {opp['expected_profit']:.3f}")