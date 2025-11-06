"""
Multi-Asset Quantum Portfolio moduli
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import warnings
import json
import sqlite3
from abc import ABC, abstractmethod

from config.quantum_config import PortfolioConfig, AssetType, MarketConfig
from utils.quantum_utils import MathUtils, QuantumUtils, QuantumOptimizer, PerformanceUtils, ensure_positive_definite
from portfolio_optimization.quantum_optimization import QuantumPortfolioOptimizer, PortfolioAsset

@dataclass
class MultiAssetPortfolio:
    """Multi-asset portfolio struktura"""
    name: str
    description: str = ""
    assets: List[PortfolioAsset] = field(default_factory=list)
    weights: np.ndarray = field(default_factory=lambda: np.array([]))
    target_weights: np.ndarray = field(default_factory=lambda: np.array([]))
    transaction_costs: float = 0.001
    rebalance_frequency: int = 30  # days
    last_rebalance: datetime = field(default_factory=datetime.now)
    performance_history: List[Dict] = field(default_factory=list)
    quantum_enhancements: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if len(self.weights) == 0 and len(self.assets) > 0:
            self.weights = np.ones(len(self.assets)) / len(self.assets)
        if len(self.target_weights) == 0 and len(self.assets) > 0:
            self.target_weights = np.ones(len(self.assets)) / len(self.assets)
    
    def add_asset(self, asset: PortfolioAsset, target_weight: float = None):
        """Portfolio ga asset qo'shish"""
        self.assets.append(asset)
        
        if target_weight is not None:
            new_target = np.append(self.target_weights, target_weight)
        else:
            new_target = np.append(self.target_weights, 0.1)  # Default weight
        
        # Normalize weights
        new_target = new_target / np.sum(new_target)
        self.target_weights = new_target
        
        # Update current weights
        if len(self.weights) == len(self.assets) - 1:
            self.weights = np.append(self.weights, 0.0)
        elif len(self.weights) == 0:
            self.weights = np.array([1.0])
    
    def remove_asset(self, symbol: str):
        """Portfolio dan asset ni o'chirish"""
        for i, asset in enumerate(self.assets):
            if asset.symbol == symbol:
                self.assets.pop(i)
                self.weights = np.delete(self.weights, i)
                self.target_weights = np.delete(self.target_weights, i)
                
                # Renormalize weights
                if len(self.weights) > 0:
                    self.weights = self.weights / np.sum(self.weights)
                    self.target_weights = self.target_weights / np.sum(self.target_weights)
                break
    
    def update_weights(self, new_weights: np.ndarray, normalize: bool = True):
        """Portfolio weights ni yangilash"""
        if normalize:
            new_weights = new_weights / np.sum(new_weights)
        
        if len(new_weights) == len(self.assets):
            self.weights = new_weights
        else:
            raise ValueError("Weights length must match number of assets")
    
    def get_portfolio_value(self, prices: Dict[str, float]) -> float:
        """Portfolio qiymati"""
        total_value = 0
        for i, asset in enumerate(self.assets):
            if asset.symbol in prices:
                asset_value = prices[asset.symbol] * self.weights[i]
                total_value += asset_value
        return total_value
    
    def rebalance_needed(self, tolerance: float = 0.05) -> bool:
        """Rebalancing kerakligini tekshirish"""
        if len(self.weights) == 0 or len(self.target_weights) == 0:
            return False
        
        weight_diff = np.abs(self.weights - self.target_weights)
        return np.any(weight_diff > tolerance)

class MultiAssetDataProvider:
    """Multi-asset data provider"""
    
    def __init__(self, config: MarketConfig = None):
        self.config = config or MarketConfig()
        self.data_cache = {}
        self.last_update = None
    
    def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Joriy narxlarni olish"""
        # Simplified implementation
        # Haqiqiy implementatsiyada real market data API ishlatish kerak
        
        mock_prices = {
            'AAPL': 150.0,
            'GOOGL': 2800.0,
            'TSLA': 800.0,
            'MSFT': 300.0,
            'AMZN': 3200.0,
            'NVDA': 500.0,
            'GOLD': 2000.0,
            'SILVER': 25.0,
            'PLATINUM': 1000.0,
            'PALLADIUM': 2000.0,
            'EUR/USD': 1.10,
            'GBP/USD': 1.35,
            'USD/JPY': 110.0,
            'USD/CHF': 0.92,
            'AUD/USD': 0.75
        }
        
        return {symbol: mock_prices.get(symbol, 100.0) for symbol in symbols}
    
    def get_historical_returns(self, symbols: List[str], days: int = 252) -> pd.DataFrame:
        """Tarixiy returnlar"""
        # Mock historical data
        np.random.seed(42)  # Reproducible results
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        data = {}
        
        for symbol in symbols:
            # Generate realistic return patterns
            base_return = np.random.normal(0.0005, 0.02, days)  # Daily returns
            
            # Add market correlation
            market_factor = np.random.normal(0, 0.01, days)
            symbol_returns = base_return + 0.3 * market_factor
            
            data[symbol] = symbol_returns
        
        returns_df = pd.DataFrame(data, index=dates)
        return returns_df
    
    def get_market_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Bozor ma'lumotlari"""
        # Mock market data
        market_data = {}
        
        for symbol in symbols:
            if symbol in ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'NVDA']:
                # Stock data
                market_data[symbol] = {
                    'asset_type': 'stocks',
                    'market_cap': np.random.uniform(1e9, 3e12),
                    'beta': np.random.normal(1.0, 0.3),
                    'sector': np.random.choice(['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer']),
                    'dividend_yield': np.random.uniform(0, 0.05)
                }
            elif symbol in ['GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM']:
                # Metal data
                market_data[symbol] = {
                    'asset_type': 'metals',
                    'volatility': np.random.uniform(0.15, 0.40),
                    'correlation_to_gold': np.random.uniform(0.3, 0.8) if symbol != 'GOLD' else 1.0,
                    'storage_cost': 0.02,
                    'convenience_yield': np.random.uniform(0, 0.05)
                }
            elif '/' in symbol:
                # Forex data
                market_data[symbol] = {
                    'asset_type': 'forex',
                    'base_currency': symbol.split('/')[0],
                    'quote_currency': symbol.split('/')[1],
                    'interest_rate_diff': np.random.uniform(-0.05, 0.05),
                    'volatility': np.random.uniform(0.05, 0.25)
                }
        
        return market_data
    
    def get_correlation_matrix(self, symbols: List[str]) -> np.ndarray:
        """Correlation matrix olish"""
        returns_data = self.get_historical_returns(symbols)
        return returns_data.corr().values

class CrossAssetOptimizer:
    """Cross-asset correlation optimizer"""
    
    def __init__(self, portfolio: MultiAssetPortfolio, data_provider: MultiAssetDataProvider):
        self.portfolio = portfolio
        self.data_provider = data_provider
        self.optimizer = QuantumPortfolioOptimizer()
    
    def optimize_cross_asset_allocation(self, target_volatility: float = None) -> Dict[str, Union[np.ndarray, float]]:
        """Cross-asset allocation optimization"""
        if len(self.portfolio.assets) == 0:
            return {'error': 'Portfolio has no assets'}
        
        # Get data
        symbols = [asset.symbol for asset in self.portfolio.assets]
        expected_returns = np.array([asset.expected_return for asset in self.portfolio.assets])
        correlation_matrix = self.data_provider.get_correlation_matrix(symbols)
        
        # Get volatilities
        returns_data = self.data_provider.get_historical_returns(symbols)
        volatilities = returns_data.std().values * np.sqrt(252)  # Annualized
        
        # Create covariance matrix
        covariance_matrix = correlation_matrix * np.outer(volatilities, volatilities)
        covariance_matrix = ensure_positive_definite(covariance_matrix)
        
        # Cross-asset optimization
        results = {}
        
        # Mean-variance optimization
        mv_result = self.optimizer.optimize_portfolio(
            self.portfolio.assets, expected_returns, covariance_matrix, 'mean_variance')
        results['mean_variance'] = mv_result
        
        # Risk parity optimization
        rp_result = self.optimizer.optimize_portfolio(
            self.portfolio.assets, expected_returns, covariance_matrix, 'risk_parity')
        results['risk_parity'] = rp_result
        
        # Diversification optimization
        div_result = self.optimizer.optimize_portfolio(
            self.portfolio.assets, expected_returns, covariance_matrix, 'diversification')
        results['diversification'] = div_result
        
        # Cross-asset consensus
        consensus_weights = self._calculate_cross_asset_consensus(results)
        
        # Calculate portfolio metrics
        portfolio_metrics = self._calculate_cross_asset_metrics(consensus_weights, expected_returns, covariance_matrix)
        
        return {
            'individual_optimizations': results,
            'consensus_weights': consensus_weights,
            'portfolio_metrics': portfolio_metrics,
            'cross_asset_insights': self._generate_cross_asset_insights(consensus_weights, correlation_matrix, volatilities),
            'optimization_timestamp': datetime.now()
        }
    
    def _calculate_cross_asset_consensus(self, results: Dict) -> np.ndarray:
        """Cross-asset consensus calculation"""
        weights_list = []
        weights_list.append(results['mean_variance']['optimal_weights'])
        weights_list.append(results['risk_parity']['optimal_weights'])
        weights_list.append(results['diversification']['optimal_weights'])
        
        # Weighted average
        weights_array = np.array(weights_list)
        weights = np.mean(weights_array, axis=0)
        
        return weights / np.sum(weights)  # Normalize
    
    def _calculate_cross_asset_metrics(self, weights: np.ndarray, expected_returns: np.ndarray, 
                                     covariance_matrix: np.ndarray) -> Dict[str, float]:
        """Cross-asset portfolio metrics"""
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        
        # Asset allocation breakdown
        asset_types = {}
        if hasattr(self.portfolio, 'assets') and len(self.portfolio.assets) == len(weights):
            for i, asset in enumerate(self.portfolio.assets):
                asset_type = asset.asset_type.value
                if asset_type not in asset_types:
                    asset_types[asset_type] = 0
                asset_types[asset_type] += weights[i]
        
        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio,
            'asset_allocation': asset_types,
            'concentration_risk': np.sum(weights**2),
            'diversification_benefit': self._calculate_diversification_benefit(weights, covariance_matrix)
        }
    
    def _calculate_diversification_benefit(self, weights: np.ndarray, covariance_matrix: np.ndarray) -> float:
        """Diversification benefit calculation"""
        # Weighted average volatility
        volatilities = np.sqrt(np.diag(covariance_matrix))
        weighted_avg_vol = np.dot(weights, volatilities)
        
        # Portfolio volatility
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        
        # Diversification benefit
        if portfolio_vol > 0:
            benefit = (weighted_avg_vol - portfolio_vol) / weighted_avg_vol
        else:
            benefit = 0
        
        return max(0, benefit)
    
    def _generate_cross_asset_insights(self, weights: np.ndarray, correlation_matrix: np.ndarray, 
                                     volatilities: np.ndarray) -> List[str]:
        """Cross-asset insights generation"""
        insights = []
        
        # Correlation insights
        high_corr_pairs = []
        for i in range(len(correlation_matrix)):
            for j in range(i+1, len(correlation_matrix)):
                if correlation_matrix[i, j] > 0.7:
                    high_corr_pairs.append((i, j, correlation_matrix[i, j]))
        
        if high_corr_pairs:
            insights.append(f"High correlation detected between {len(high_corr_pairs)} asset pairs")
        
        # Volatility insights
        high_vol_assets = np.where(volatilities > 0.3)[0]
        if len(high_vol_assets) > 0:
            insights.append(f"{len(high_vol_assets)} high-volatility assets in portfolio")
        
        # Concentration insights
        concentration = np.sum(weights**2)
        if concentration > 0.3:
            insights.append("High concentration risk detected")
        
        return insights

class QuantumDynamicRebalancer:
    """Quantum dynamic rebalancing engine"""
    
    def __init__(self, portfolio: MultiAssetPortfolio, config: PortfolioConfig = None):
        self.portfolio = portfolio
        self.config = config or PortfolioConfig()
        self.rebalance_history = []
    
    def should_rebalance(self, market_data: Dict[str, float], trigger_threshold: float = None) -> Dict[str, bool]:
        """Rebalancing kerakligini tekshirish"""
        if trigger_threshold is None:
            trigger_threshold = 0.05  # 5% threshold
        
        trigger_threshold = min(trigger_threshold, self.config.risk_tolerance)
        
        # Calculate current weights
        current_weights = self._calculate_current_weights(market_data)
        
        # Check for significant deviations
        weight_deviations = np.abs(current_weights - self.portfolio.target_weights)
        should_rebalance = np.any(weight_deviations > trigger_threshold)
        
        # Time-based rebalancing
        days_since_rebalance = (datetime.now() - self.portfolio.last_rebalance).days
        time_based_rebalance = days_since_rebalance >= self.config.rebalance_frequency
        
        return {
            'rebalance_needed': should_rebalance or time_based_rebalance,
            'weight_deviations': weight_deviations,
            'max_deviation': np.max(weight_deviations),
            'time_based_trigger': time_based_rebalance,
            'days_since_rebalance': days_since_rebalance
        }
    
    def quantum_rebalance(self, market_data: Dict[str, float], optimization_results: Dict = None) -> Dict[str, any]:
        """Quantum-enhanced rebalancing"""
        if optimization_results is None:
            raise ValueError("Optimization results required for quantum rebalancing")
        
        # Current weights
        current_weights = self._calculate_current_weights(market_data)
        
        # Target weights from optimization
        optimal_weights = optimization_results.get('consensus_weights', current_weights)
        
        # Calculate transaction costs
        weight_changes = np.abs(optimal_weights - current_weights)
        transaction_costs = np.sum(weight_changes) * self.portfolio.transaction_costs
        
        # Quantum rebalancing optimization
        quantum_weights = self._quantum_rebalancing_algorithm(current_weights, optimal_weights, market_data)
        
        # Rebalancing execution plan
        execution_plan = self._create_execution_plan(current_weights, quantum_weights, market_data)
        
        # Update portfolio
        self.portfolio.update_weights(quantum_weights)
        self.portfolio.last_rebalance = datetime.now()
        
        # Record rebalancing
        rebalancing_record = {
            'timestamp': datetime.now(),
            'current_weights': current_weights,
            'optimal_weights': optimal_weights,
            'quantum_weights': quantum_weights,
            'transaction_costs': transaction_costs,
            'execution_plan': execution_plan,
            'optimization_used': optimization_results.get('optimization_timestamp')
        }
        
        self.rebalance_history.append(rebalancing_record)
        
        return {
            'rebalancing_successful': True,
            'quantum_weights': quantum_weights,
            'transaction_costs': transaction_costs,
            'execution_plan': execution_plan,
            'expected_improvement': self._calculate_expected_improvement(current_weights, quantum_weights, optimization_results),
            'record': rebalancing_record
        }
    
    def _calculate_current_weights(self, market_data: Dict[str, float]) -> np.ndarray:
        """Joriy weights hisoblash"""
        if len(self.portfolio.weights) == 0:
            return np.array([])
        
        # Get current portfolio value
        current_values = {}
        total_value = 0
        
        for i, asset in enumerate(self.portfolio.assets):
            if asset.symbol in market_data:
                price = market_data[asset.symbol]
                # Assuming equal position sizes for simplicity
                value = price * 1.0  # Normalized position
                current_values[asset.symbol] = value
                total_value += value
        
        # Calculate weights
        if total_value > 0:
            weights = np.array([current_values.get(asset.symbol, 0) / total_value 
                              for asset in self.portfolio.assets])
        else:
            weights = np.ones(len(self.portfolio.assets)) / len(self.portfolio.assets)
        
        return weights
    
    def _quantum_rebalancing_algorithm(self, current_weights: np.ndarray, optimal_weights: np.ndarray, 
                                     market_data: Dict[str, float]) -> np.ndarray:
        """Quantum rebalancing algorithm"""
        # Start with optimal weights
        quantum_weights = optimal_weights.copy()
        
        # Apply quantum constraints
        for i, asset in enumerate(self.portfolio.assets):
            if hasattr(asset, 'get_weight_bounds'):
                min_weight, max_weight = asset.get_weight_bounds()
                quantum_weights[i] = np.clip(quantum_weights[i], min_weight, max_weight)
        
        # Transaction cost optimization
        quantum_weights = self._optimize_transaction_costs(current_weights, quantum_weights)
        
        # Quantum enhancement
        quantum_weights = self._apply_quantum_rebalancing_enhancement(quantum_weights)
        
        return quantum_weights / np.sum(quantum_weights)  # Normalize
    
    def _optimize_transaction_costs(self, current_weights: np.ndarray, optimal_weights: np.ndarray) -> np.ndarray:
        """Transaction cost optimization"""
        # Gradient descent to minimize transaction costs while staying close to optimal
        learning_rate = 0.1
        max_iterations = 100
        
        weights = current_weights.copy()
        
        for _ in range(max_iterations):
            # Transaction cost gradient
            cost_gradient = np.sign(weights - optimal_weights) * self.portfolio.transaction_costs
            
            # Update weights
            weights = weights - learning_rate * cost_gradient
            
            # Constraints
            weights = np.maximum(weights, 0)
            weights = weights / np.sum(weights)
        
        return weights
    
    def _apply_quantum_rebalancing_enhancement(self, weights: np.ndarray) -> np.ndarray:
        """Quantum rebalancing enhancement"""
        # Quantum smoothing
        quantum_factor = 1 + 0.02 * np.sin(np.sum(weights) * len(weights) * np.pi)
        
        enhanced_weights = weights * quantum_factor
        enhanced_weights = np.maximum(enhanced_weights, 0)
        
        return enhanced_weights / np.sum(enhanced_weights)
    
    def _create_execution_plan(self, current_weights: np.ndarray, target_weights: np.ndarray, 
                             market_data: Dict[str, float]) -> List[Dict]:
        """Rebalancing execution plan"""
        execution_plan = []
        
        for i, asset in enumerate(self.portfolio.assets):
            weight_change = target_weights[i] - current_weights[i]
            
            if abs(weight_change) > 0.001:  # Only significant changes
                execution_plan.append({
                    'symbol': asset.symbol,
                    'asset_type': asset.asset_type.value,
                    'current_weight': current_weights[i],
                    'target_weight': target_weights[i],
                    'weight_change': weight_change,
                    'action': 'buy' if weight_change > 0 else 'sell',
                    'estimated_cost': abs(weight_change) * self.portfolio.transaction_costs,
                    'market_impact': self._estimate_market_impact(asset, abs(weight_change), market_data)
                })
        
        return sorted(execution_plan, key=lambda x: abs(x['weight_change']), reverse=True)
    
    def _estimate_market_impact(self, asset: PortfolioAsset, weight_change: float, 
                              market_data: Dict[str, float]) -> float:
        """Market impact estimation"""
        # Simplified market impact model
        base_impact = weight_change * 0.1  # 10% of weight change
        
        # Asset-specific factors
        if asset.asset_type == AssetType.STOCKS:
            impact_multiplier = 1.5
        elif asset.asset_type == AssetType.METALS:
            impact_multiplier = 2.0
        else:  # Forex
            impact_multiplier = 0.5
        
        return base_impact * impact_multiplier
    
    def _calculate_expected_improvement(self, current_weights: np.ndarray, quantum_weights: np.ndarray, 
                                      optimization_results: Dict) -> float:
        """Expected improvement from rebalancing"""
        current_metrics = optimization_results.get('portfolio_metrics', {})
        if not current_metrics:
            return 0.0
        
        # Calculate expected return improvement
        current_return = current_metrics.get('expected_return', 0)
        
        # Simplified improvement estimate
        weight_change_cost = np.sum(np.abs(quantum_weights - current_weights)) * self.portfolio.transaction_costs
        
        expected_improvement = max(0, 0.02 - weight_change_cost)  # 2% baseline improvement minus costs
        
        return expected_improvement

class MultiAssetPortfolioManager:
    """Multi-asset portfolio manager"""
    
    def __init__(self, config: PortfolioConfig = None, market_config: MarketConfig = None):
        self.config = config or PortfolioConfig()
        self.market_config = market_config or MarketConfig()
        self.data_provider = MultiAssetDataProvider(self.market_config)
        self.portfolios = {}
        self.optimization_cache = {}
    
    def create_portfolio(self, name: str, description: str = "") -> MultiAssetPortfolio:
        """Portfolio yaratish"""
        portfolio = MultiAssetPortfolio(name=name, description=description)
        self.portfolios[name] = portfolio
        return portfolio
    
    def add_asset_to_portfolio(self, portfolio_name: str, asset: PortfolioAsset, target_weight: float = None):
        """Portfolio ga asset qo'shish"""
        if portfolio_name not in self.portfolios:
            self.create_portfolio(portfolio_name)
        
        portfolio = self.portfolios[portfolio_name]
        portfolio.add_asset(asset, target_weight)
    
    def optimize_portfolio(self, portfolio_name: str, method: str = 'consensus') -> Dict[str, any]:
        """Portfolio optimization"""
        if portfolio_name not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_name} not found")
        
        portfolio = self.portfolios[portfolio_name]
        
        if len(portfolio.assets) == 0:
            return {'error': 'Portfolio has no assets'}
        
        # Get data
        symbols = [asset.symbol for asset in portfolio.assets]
        market_data = self.data_provider.get_market_data(symbols)
        current_prices = self.data_provider.get_current_prices(symbols)
        
        # Cross-asset optimization
        cross_asset_optimizer = CrossAssetOptimizer(portfolio, self.data_provider)
        optimization_results = cross_asset_optimizer.optimize_cross_asset_allocation()
        
        # Update portfolio weights
        if 'consensus_weights' in optimization_results:
            portfolio.update_weights(optimization_results['consensus_weights'])
        
        # Cache results
        self.optimization_cache[portfolio_name] = optimization_results
        
        return optimization_results
    
    def rebalance_portfolio(self, portfolio_name: str, force_rebalance: bool = False) -> Dict[str, any]:
        """Portfolio rebalancing"""
        if portfolio_name not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_name} not found")
        
        portfolio = self.portfolios[portfolio_name]
        
        # Get optimization results
        if portfolio_name not in self.optimization_cache:
            self.optimize_portfolio(portfolio_name)
        
        optimization_results = self.optimization_cache[portfolio_name]
        
        # Get current market data
        symbols = [asset.symbol for asset in portfolio.assets]
        current_prices = self.data_provider.get_current_prices(symbols)
        
        # Check if rebalancing needed
        rebalancer = QuantumDynamicRebalancer(portfolio, self.config)
        rebalance_check = rebalancer.should_rebalance(current_prices)
        
        if not force_rebalance and not rebalance_check['rebalance_needed']:
            return {
                'rebalance_needed': False,
                'reason': 'No significant deviations detected',
                'days_since_rebalance': rebalance_check['days_since_rebalance']
            }
        
        # Perform rebalancing
        rebalancing_result = rebalancer.quantum_rebalance(current_prices, optimization_results)
        
        return rebalancing_result
    
    def get_portfolio_performance(self, portfolio_name: str, days: int = 252) -> Dict[str, any]:
        """Portfolio performance hisoblash"""
        if portfolio_name not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_name} not found")
        
        portfolio = self.portfolios[portfolio_name]
        
        # Get historical data
        symbols = [asset.symbol for asset in portfolio.assets]
        returns_data = self.data_provider.get_historical_returns(symbols, days)
        
        # Calculate portfolio returns
        if len(portfolio.weights) == len(portfolio.assets):
            portfolio_returns = np.dot(returns_data.values, portfolio.weights)
        else:
            portfolio_returns = np.mean(returns_data.values, axis=1)  # Equal weighted
        
        # Calculate metrics
        metrics = PerformanceUtils.calculate_portfolio_metrics(
            pd.DataFrame({'portfolio': portfolio_returns}), 
            np.array([1.0])
        )
        
        # Asset contribution analysis
        asset_contributions = {}
        for i, asset in enumerate(portfolio.assets):
            if len(portfolio.weights) > i:
                contribution = returns_data.iloc[:, i].mean() * portfolio.weights[i] * 252
                asset_contributions[asset.symbol] = contribution
        
        return {
            'portfolio_metrics': metrics,
            'asset_contributions': asset_contributions,
            'returns_data': returns_data,
            'portfolio_returns': portfolio_returns,
            'calculation_date': datetime.now()
        }
    
    def generate_portfolio_report(self, portfolio_name: str) -> Dict[str, any]:
        """Portfolio hisoboti"""
        if portfolio_name not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_name} not found")
        
        portfolio = self.portfolios[portfolio_name]
        
        # Get performance
        performance = self.get_portfolio_performance(portfolio_name)
        
        # Get current prices
        if len(portfolio.assets) > 0:
            symbols = [asset.symbol for asset in portfolio.assets]
            current_prices = self.data_provider.get_current_prices(symbols)
            current_value = portfolio.get_portfolio_value(current_prices)
        else:
            current_prices = {}
            current_value = 0
        
        # Asset allocation
        asset_allocation = {}
        if len(portfolio.weights) == len(portfolio.assets):
            for i, asset in enumerate(portfolio.assets):
                asset_allocation[asset.symbol] = {
                    'weight': portfolio.weights[i],
                    'asset_type': asset.asset_type.value,
                    'sector': asset.sector,
                    'current_price': current_prices.get(asset.symbol, 0)
                }
        
        report = {
            'portfolio_info': {
                'name': portfolio.name,
                'description': portfolio.description,
                'num_assets': len(portfolio.assets),
                'total_value': current_value,
                'last_rebalance': portfolio.last_rebalance,
                'rebalance_frequency': portfolio.rebalance_frequency
            },
            'performance': performance['portfolio_metrics'],
            'asset_allocation': asset_allocation,
            'risk_metrics': {
                'expected_return': performance['portfolio_metrics'].get('annualized_return', 0),
                'volatility': performance['portfolio_metrics'].get('volatility', 0),
                'sharpe_ratio': performance['portfolio_metrics'].get('sharpe_ratio', 0),
                'max_drawdown': performance['portfolio_metrics'].get('max_drawdown', 0)
            },
            'optimization_status': 'completed' if portfolio_name in self.optimization_cache else 'pending'
        }
        
        # Add optimization insights if available
        if portfolio_name in self.optimization_cache:
            optimization_results = self.optimization_cache[portfolio_name]
            report['optimization_insights'] = optimization_results.get('cross_asset_insights', [])
        
        return report
    
    def save_portfolio(self, portfolio_name: str, filepath: str = None):
        """Portfolio ni faylga saqlash"""
        if portfolio_name not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_name} not found")
        
        portfolio = self.portfolios[portfolio_name]
        
        portfolio_data = {
            'name': portfolio.name,
            'description': portfolio.description,
            'assets': [
                {
                    'symbol': asset.symbol,
                    'asset_type': asset.asset_type.value,
                    'expected_return': asset.expected_return,
                    'volatility': asset.volatility,
                    'current_price': asset.current_price,
                    'market_cap': asset.market_cap,
                    'sector': asset.sector
                }
                for asset in portfolio.assets
            ],
            'weights': portfolio.weights.tolist(),
            'target_weights': portfolio.target_weights.tolist(),
            'transaction_costs': portfolio.transaction_costs,
            'rebalance_frequency': portfolio.rebalance_frequency,
            'last_rebalance': portfolio.last_rebalance.isoformat(),
            'performance_history': portfolio.performance_history,
            'quantum_enhancements': portfolio.quantum_enhancements
        }
        
        if filepath is None:
            filepath = f"{portfolio_name}_portfolio.json"
        
        with open(filepath, 'w') as f:
            json.dump(portfolio_data, f, indent=2, default=str)
        
        return f"Portfolio saved to {filepath}"
    
    def load_portfolio(self, filepath: str) -> MultiAssetPortfolio:
        """Portfolio ni fayldan yuklash"""
        with open(filepath, 'r') as f:
            portfolio_data = json.load(f)
        
        # Create portfolio
        portfolio = MultiAssetPortfolio(
            name=portfolio_data['name'],
            description=portfolio_data['description']
        )
        
        # Add assets
        for asset_data in portfolio_data['assets']:
            asset = PortfolioAsset(
                symbol=asset_data['symbol'],
                asset_type=AssetType(asset_data['asset_type']),
                expected_return=asset_data['expected_return'],
                volatility=asset_data['volatility'],
                current_price=asset_data['current_price'],
                market_cap=asset_data.get('market_cap'),
                sector=asset_data.get('sector')
            )
            portfolio.add_asset(asset)
        
        # Set weights
        portfolio.weights = np.array(portfolio_data['weights'])
        portfolio.target_weights = np.array(portfolio_data['target_weights'])
        portfolio.transaction_costs = portfolio_data['transaction_costs']
        portfolio.rebalance_frequency = portfolio_data['rebalance_frequency']
        portfolio.last_rebalance = datetime.fromisoformat(portfolio_data['last_rebalance'])
        portfolio.performance_history = portfolio_data['performance_history']
        portfolio.quantum_enhancements = portfolio_data['quantum_enhancements']
        
        # Add to manager
        self.portfolios[portfolio.name] = portfolio
        
        return portfolio

# Predefined portfolio templates
class QuantumPortfolioTemplates:
    """Quantum portfolio templates"""
    
    @staticmethod
    def create_balanced_portfolio() -> MultiAssetPortfolio:
        """Balanced portfolio yaratish"""
        assets = [
            PortfolioAsset("AAPL", AssetType.STOCKS, 0.12, 0.25, 150.0, 2e12, "Technology"),
            PortfolioAsset("MSFT", AssetType.STOCKS, 0.10, 0.20, 300.0, 2.5e12, "Technology"),
            PortfolioAsset("GOLD", AssetType.METALS, 0.08, 0.20, 2000.0, None, "Commodity"),
            PortfolioAsset("EUR/USD", AssetType.FOREX, 0.05, 0.15, 1.10, None, "Currency"),
        ]
        
        portfolio = MultiAssetPortfolio(
            name="Balanced Quantum Portfolio",
            description="Diversified portfolio across stocks, metals, and forex"
        )
        
        for asset in assets:
            portfolio.add_asset(asset, 0.25)
        
        return portfolio
    
    @staticmethod
    def create_aggressive_growth_portfolio() -> MultiAssetPortfolio:
        """Aggressive growth portfolio"""
        assets = [
            PortfolioAsset("TSLA", AssetType.STOCKS, 0.25, 0.50, 800.0, 800e9, "Automotive"),
            PortfolioAsset("NVDA", AssetType.STOCKS, 0.30, 0.60, 500.0, 1e12, "Technology"),
            PortfolioAsset("PALLADIUM", AssetType.METALS, 0.15, 0.35, 2000.0, None, "Commodity"),
        ]
        
        portfolio = MultiAssetPortfolio(
            name="Aggressive Growth Quantum Portfolio",
            description="High-risk, high-reward quantum portfolio"
        )
        
        weights = [0.4, 0.4, 0.2]
        for i, asset in enumerate(assets):
            portfolio.add_asset(asset, weights[i])
        
        return portfolio
    
    @staticmethod
    def create_conservative_portfolio() -> MultiAssetPortfolio:
        """Conservative portfolio"""
        assets = [
            PortfolioAsset("MSFT", AssetType.STOCKS, 0.10, 0.20, 300.0, 2.5e12, "Technology"),
            PortfolioAsset("GOLD", AssetType.METALS, 0.08, 0.20, 2000.0, None, "Commodity"),
            PortfolioAsset("USD/CHF", AssetType.FOREX, 0.03, 0.10, 0.92, None, "Currency"),
            PortfolioAsset("PLATINUM", AssetType.METALS, 0.06, 0.25, 1000.0, None, "Commodity"),
        ]
        
        portfolio = MultiAssetPortfolio(
            name="Conservative Quantum Portfolio",
            description="Low-risk quantum portfolio for capital preservation"
        )
        
        for asset in assets:
            portfolio.add_asset(asset, 0.25)
        
        return portfolio

if __name__ == "__main__":
    # Test
    from ..config.quantum_config import AssetType
    
    print("Multi-Asset Quantum Portfolio Test:")
    print("=" * 50)
    
    # Create manager
    manager = MultiAssetPortfolioManager()
    
    # Create portfolio
    portfolio = QuantumPortfolioTemplates.create_balanced_portfolio()
    manager.portfolios['test_portfolio'] = portfolio
    
    print(f"Created portfolio: {portfolio.name}")
    print(f"Number of assets: {len(portfolio.assets)}")
    
    # Optimize portfolio
    optimization_result = manager.optimize_portfolio('test_portfolio')
    print(f"\nOptimization completed: {optimization_result['portfolio_metrics']['expected_return']:.4f}")
    
    # Portfolio performance
    performance = manager.get_portfolio_performance('test_portfolio')
    print(f"Portfolio Sharpe Ratio: {performance['portfolio_metrics']['sharpe_ratio']:.4f}")
    
    # Generate report
    report = manager.generate_portfolio_report('test_portfolio')
    print(f"\nPortfolio Report Generated:")
    print(f"Total Value: {report['portfolio_info']['total_value']:.2f}")
    print(f"Expected Return: {report['risk_metrics']['expected_return']:.4f}")
    print(f"Volatility: {report['risk_metrics']['volatility']:.4f}")
    
    # Test rebalancing
    rebalancing_result = manager.rebalance_portfolio('test_portfolio')
    print(f"\nRebalancing Status: {rebalancing_result['rebalancing_successful']}")
    
    # Cross-asset insights
    if 'cross_asset_insights' in optimization_result:
        print("\nCross-Asset Insights:")
        for insight in optimization_result['cross_asset_insights']:
            print(f"- {insight}")