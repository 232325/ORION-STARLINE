"""
Quantum Pricing Portfolio - Asosiy Orchestrator
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import warnings
import json
import logging
from dataclasses import asdict

from config.quantum_config import QuantumPricingConfig, MetalType, AssetType
from metal_futures.metal_pricing import MetalFuturesQuantumPricer, create_metal_futures_portfolio
from pricing_models.quantum_models import QuantumPricingModelFactory, quantum_consensus_pricing
from portfolio_optimization.quantum_optimization import QuantumPortfolioOptimizer, PortfolioAsset
from multi_asset_portfolio.portfolio_manager import (
    MultiAssetPortfolioManager, QuantumPortfolioTemplates, MultiAssetPortfolio
)
from utils.quantum_utils import MathUtils, QuantumUtils, DataUtils

class QuantumPricingPortfolioEngine:
    """Quantum Pricing Portfolio - Asosiy Engine"""
    
    def __init__(self, config: QuantumPricingConfig = None):
        self.config = config or QuantumPricingConfig()
        self.logger = self._setup_logging()
        
        # Initialize components
        self.metal_pricer = None
        self.pricing_models = None
        self.portfolio_optimizer = None
        self.portfolio_manager = None
        
        # Market data cache
        self.market_data_cache = {}
        self.optimization_cache = {}
        
        # Performance tracking
        self.performance_history = []
        self.quantum_enhancements = {}
        
        self._initialize_components()
    
    def _setup_logging(self) -> logging.Logger:
        """Logging setup"""
        logger = logging.getLogger(f"QuantumPricingPortfolio_{datetime.now().strftime('%Y%m%d')}")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_components(self):
        """Initialize all components"""
        try:
            # Metal futures pricer
            self.metal_pricer = MetalFuturesQuantumPricer(self.config.metals)
            
            # Pricing models
            self.pricing_models = QuantumPricingModelFactory.create_ensemble(
                ['black_scholes', 'monte_carlo', 'binomial'], 
                self.config.quantum
            )
            
            # Portfolio optimizer
            self.portfolio_optimizer = QuantumPortfolioOptimizer(self.config.portfolio)
            
            # Portfolio manager
            self.portfolio_manager = MultiAssetPortfolioManager(
                self.config.portfolio, 
                self.config.market
            )
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            warnings.warn(f"Component initialization failed: {e}")
    
    def price_metal_futures(self, metal_type: MetalType, current_price: float, 
                          contract_months: List[int] = None, year: int = None) -> Dict[str, Any]:
        """Metal futures pricing"""
        if self.metal_pricer is None:
            raise ValueError("Metal pricer not initialized")
        
        if contract_months is None:
            contract_months = [3, 6, 9, 12]  # Quarterly
        
        if year is None:
            year = datetime.now().year + 1
        
        results = {}
        
        for month in contract_months:
            # Create contract
            from .metal_futures.metal_pricing import MetalContract
            contract = MetalContract(
                metal_type=metal_type,
                expiration_month=month,
                expiration_year=year,
                strike_price=current_price * 1.02  # 2% OTM
            )
            
            # Price the contract
            pricing_result = self.metal_pricer.price_metal_future(metal_type, current_price, contract)
            risk_metrics = self.metal_pricer.quantum_risk_metrics(metal_type, current_price, contract)
            
            results[f"{year}-{month:02d}"] = {
                'pricing': pricing_result,
                'risk_metrics': risk_metrics,
                'contract_details': {
                    'expiration': f"{year}-{month:02d}",
                    'strike': contract.strike_price,
                    'days_to_expiry': contract.get_days_to_expiry()
                }
            }
        
        return {
            'metal': metal_type.value,
            'current_price': current_price,
            'contracts': results,
            'quantum_enhancements': self._get_metal_quantum_enhancements(metal_type),
            'timestamp': datetime.now()
        }
    
    def price_option_with_quantum_models(self, option_contract, model_types: List[str] = None) -> Dict[str, Any]:
        """Quantum models bilan option pricing"""
        if model_types is None:
            model_types = ['black_scholes', 'monte_carlo', 'binomial']
        
        # Create models
        models = QuantumPricingModelFactory.create_ensemble(model_types, self.config.quantum)
        
        # Consensus pricing
        consensus_result = quantum_consensus_pricing(models, option_contract)
        
        # Individual model results
        individual_results = {}
        for model_name, model in models.items():
            try:
                result = model.price(option_contract)
                greeks = model.greeks(option_contract)
                
                price_key = 'quantum_consensus' if 'quantum_consensus' in result else ('quantum_price' if 'quantum_price' in result else 'fair_value')
                individual_results[model_name] = {
                    'price': result[price_key],
                    'greeks': greeks
                }
            except Exception as e:
                self.logger.warning(f"Model {model_name} failed: {e}")
                individual_results[model_name] = {'error': str(e)}
        
        return {
            'consensus_result': consensus_result,
            'individual_results': individual_results,
            'model_confidence': consensus_result.get('model_confidence', 0),
            'quantum_enhancement': np.mean([res.get('quantum_adjustments', {}).get('enhancement_factor', 0) 
                                          for res in individual_results.values() if 'quantum_adjustments' in res])
        }
    
    def optimize_multi_asset_portfolio(self, assets: List[PortfolioAsset], 
                                     portfolio_type: str = 'balanced') -> Dict[str, Any]:
        """Multi-asset portfolio optimization"""
        if self.portfolio_manager is None:
            raise ValueError("Portfolio manager not initialized")
        
        # Create portfolio
        portfolio_names = {
            'balanced': 'Quantum Balanced Portfolio',
            'aggressive': 'Quantum Aggressive Portfolio', 
            'conservative': 'Quantum Conservative Portfolio'
        }
        
        portfolio_name = portfolio_names.get(portfolio_type, 'Custom Quantum Portfolio')
        
        # Create portfolio in manager
        portfolio = self.portfolio_manager.create_portfolio(portfolio_name)
        
        # Add assets
        for asset in assets:
            target_weight = 1.0 / len(assets) if portfolio_type == 'balanced' else None
            self.portfolio_manager.add_asset_to_portfolio(portfolio_name, asset, target_weight)
        
        # Optimize
        optimization_result = self.portfolio_manager.optimize_portfolio(portfolio_name)
        
        # Add quantum insights
        quantum_insights = self._generate_quantum_portfolio_insights(optimization_result)
        
        return {
            'portfolio_name': portfolio_name,
            'optimization_result': optimization_result,
            'quantum_insights': quantum_insights,
            'portfolio_type': portfolio_type,
            'timestamp': datetime.now()
        }
    
    def create_comprehensive_portfolio(self, portfolio_name: str = None, 
                                     include_metals: bool = True,
                                     include_stocks: bool = True,
                                     include_forex: bool = True) -> Dict[str, Any]:
        """Comprehensive multi-asset portfolio creation"""
        if portfolio_name is None:
            portfolio_name = f"Comprehensive Quantum Portfolio {datetime.now().strftime('%Y%m%d')}"
        
        # Create portfolio
        portfolio = self.portfolio_manager.create_portfolio(portfolio_name)
        
        # Add assets based on selection
        if include_stocks:
            stocks = [
                PortfolioAsset("AAPL", AssetType.STOCKS, 0.12, 0.25, 150.0, 2e12, "Technology"),
                PortfolioAsset("MSFT", AssetType.STOCKS, 0.10, 0.20, 300.0, 2.5e12, "Technology"),
                PortfolioAsset("TSLA", AssetType.STOCKS, 0.25, 0.50, 800.0, 800e9, "Automotive"),
                PortfolioAsset("NVDA", AssetType.STOCKS, 0.30, 0.60, 500.0, 1e12, "Technology")
            ]
            
            for stock in stocks:
                self.portfolio_manager.add_asset_to_portfolio(portfolio_name, stock, 0.15)
        
        if include_metals:
            metals = [
                PortfolioAsset("GOLD", AssetType.METALS, 0.08, 0.20, 2000.0, None, "Commodity"),
                PortfolioAsset("SILVER", AssetType.METALS, 0.10, 0.25, 25.0, None, "Commodity"),
                PortfolioAsset("PLATINUM", AssetType.METALS, 0.06, 0.30, 1000.0, None, "Commodity")
            ]
            
            for metal in metals:
                self.portfolio_manager.add_asset_to_portfolio(portfolio_name, metal, 0.10)
        
        if include_forex:
            forex_pairs = [
                PortfolioAsset("EUR/USD", AssetType.FOREX, 0.05, 0.15, 1.10, None, "Currency"),
                PortfolioAsset("GBP/USD", AssetType.FOREX, 0.04, 0.20, 1.35, None, "Currency"),
                PortfolioAsset("USD/JPY", AssetType.FOREX, 0.03, 0.12, 110.0, None, "Currency")
            ]
            
            for forex in forex_pairs:
                self.portfolio_manager.add_asset_to_portfolio(portfolio_name, forex, 0.05)
        
        # Optimize portfolio
        optimization_result = self.portfolio_manager.optimize_portfolio(portfolio_name)
        
        # Get performance
        performance = self.portfolio_manager.get_portfolio_performance(portfolio_name)
        
        # Generate report
        report = self.portfolio_manager.generate_portfolio_report(portfolio_name)
        
        return {
            'portfolio': report,
            'optimization': optimization_result,
            'performance': performance,
            'quantum_enhancements': self._calculate_portfolio_quantum_enhancements(optimization_result),
            'creation_timestamp': datetime.now()
        }
    
    def execute_quantum_trading_strategy(self, portfolio_name: str, 
                                       strategy_type: str = 'rebalancing') -> Dict[str, Any]:
        """Quantum trading strategy execution"""
        if portfolio_name not in self.portfolio_manager.portfolios:
            raise ValueError(f"Portfolio {portfolio_name} not found")
        
        portfolio = self.portfolio_manager.portfolios[portfolio_name]
        
        if strategy_type == 'rebalancing':
            # Dynamic rebalancing
            rebalancing_result = self.portfolio_manager.rebalance_portfolio(portfolio_name)
            
            return {
                'strategy': 'quantum_rebalancing',
                'result': rebalancing_result,
                'expected_improvement': rebalancing_result.get('expected_improvement', 0),
                'transaction_costs': rebalancing_result.get('transaction_costs', 0),
                'timestamp': datetime.now()
            }
        
        elif strategy_type == 'arbitrage':
            # Cross-metal arbitrage
            if self.metal_pricer is None:
                raise ValueError("Metal pricer not initialized for arbitrage")
            
            current_prices = {
                MetalType.GOLD: 2000.0,
                MetalType.SILVER: 25.0,
                MetalType.PLATINUM: 1000.0,
                MetalType.PALLADIUM: 2000.0
            }
            
            # Create correlation matrix
            correlation_matrix = np.eye(4)
            correlation_matrix[0, 1] = correlation_matrix[1, 0] = 0.70  # Gold-Silver
            correlation_matrix[0, 2] = correlation_matrix[2, 0] = 0.60  # Gold-Platinum
            correlation_matrix[0, 3] = correlation_matrix[3, 0] = 0.50  # Gold-Palladium
            correlation_matrix[1, 2] = correlation_matrix[2, 1] = 0.80  # Silver-Platinum
            correlation_matrix[1, 3] = correlation_matrix[3, 1] = 0.60  # Silver-Palladium
            correlation_matrix[2, 3] = correlation_matrix[3, 2] = 0.75  # Platinum-Palladium
            
            arbitrage_opportunities = self.metal_pricer.cross_metal_arbitrage(current_prices, correlation_matrix)
            
            return {
                'strategy': 'quantum_arbitrage',
                'opportunities': arbitrage_opportunities,
                'timestamp': datetime.now()
            }
        
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
    
    def generate_quantum_portfolio_dashboard(self, portfolio_name: str = None) -> Dict[str, Any]:
        """Quantum portfolio dashboard generation"""
        dashboard_data = {
            'timestamp': datetime.now(),
            'system_status': 'operational',
            'quantum_components': {
                'metal_pricing': self.metal_pricer is not None,
                'pricing_models': self.pricing_models is not None,
                'portfolio_optimizer': self.portfolio_optimizer is not None,
                'portfolio_manager': self.portfolio_manager is not None
            }
        }
        
        if portfolio_name and portfolio_name in self.portfolio_manager.portfolios:
            # Portfolio-specific dashboard
            portfolio = self.portfolio_manager.portfolios[portfolio_name]
            
            # Get performance
            performance = self.portfolio_manager.get_portfolio_performance(portfolio_name)
            
            # Get optimization results
            if portfolio_name in self.portfolio_manager.optimization_cache:
                optimization = self.portfolio_manager.optimization_cache[portfolio_name]
            else:
                optimization = self.portfolio_manager.optimize_portfolio(portfolio_name)
            
            dashboard_data['portfolio_dashboard'] = {
                'portfolio_info': {
                    'name': portfolio.name,
                    'num_assets': len(portfolio.assets),
                    'total_value': portfolio.get_portfolio_value(
                        self.portfolio_manager.data_provider.get_current_prices([asset.symbol for asset in portfolio.assets])
                    ),
                    'last_rebalance': portfolio.last_rebalance
                },
                'performance_metrics': performance['portfolio_metrics'],
                'optimization_status': 'optimized',
                'quantum_enhancements': self._calculate_portfolio_quantum_enhancements(optimization)
            }
            
            # Risk metrics
            if 'portfolio_metrics' in optimization:
                metrics = optimization['portfolio_metrics']
                dashboard_data['risk_metrics'] = {
                    'expected_return': metrics.get('expected_return', 0),
                    'volatility': metrics.get('volatility', 0),
                    'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                    'max_drawdown': metrics.get('max_drawdown', 0)
                }
        
        # System performance
        dashboard_data['system_performance'] = {
            'quantum_enhancement_factor': np.mean(list(self.quantum_enhancements.values())) if self.quantum_enhancements else 0,
            'optimization_success_rate': 0.95,  # Mock value
            'average_processing_time': '0.5s',  # Mock value
            'cache_hit_rate': 0.85  # Mock value
        }
        
        return dashboard_data
    
    def backtest_quantum_strategy(self, portfolio_name: str, start_date: datetime, 
                                end_date: datetime, strategy_type: str = 'quantum_optimization') -> Dict[str, Any]:
        """Quantum strategy backtesting"""
        if portfolio_name not in self.portfolio_manager.portfolios:
            raise ValueError(f"Portfolio {portfolio_name} not found")
        
        # Mock backtesting implementation
        # Haqiqiy implementatsiyada historical data va simulation kerak
        
        portfolio = self.portfolio_manager.portfolios[portfolio_name]
        
        # Generate mock historical performance
        days = (end_date - start_date).days
        returns = np.random.normal(0.001, 0.02, days)  # Daily returns
        
        # Quantum enhancement simulation
        quantum_returns = returns * (1 + 0.05 * np.sin(np.arange(days) * 0.1))  # 5% enhancement
        
        # Calculate metrics
        classical_metrics = PerformanceUtils.calculate_portfolio_metrics(
            pd.DataFrame({'returns': returns}), np.array([1.0])
        )
        
        quantum_metrics = PerformanceUtils.calculate_portfolio_metrics(
            pd.DataFrame({'returns': quantum_returns}), np.array([1.0])
        )
        
        # Backtest results
        backtest_results = {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': days
            },
            'classical_performance': classical_metrics,
            'quantum_performance': quantum_metrics,
            'quantum_advantage': {
                'return_improvement': quantum_metrics['annualized_return'] - classical_metrics['annualized_return'],
                'risk_reduction': classical_metrics['volatility'] - quantum_metrics['volatility'],
                'sharpe_improvement': quantum_metrics['sharpe_ratio'] - classical_metrics['sharpe_ratio']
            },
            'drawdown_analysis': {
                'max_drawdown_classical': classical_metrics['max_drawdown'],
                'max_drawdown_quantum': quantum_metrics['max_drawdown'],
                'drawdown_improvement': classical_metrics['max_drawdown'] - quantum_metrics['max_drawdown']
            },
            'quantum_consistency': {
                'daily_positive_returns': np.sum(quantum_returns > 0) / len(quantum_returns),
                'volatility_stability': np.std(quantum_returns) / np.mean(np.abs(quantum_returns)),
                'enhancement_stability': np.std(quantum_returns - returns) / np.mean(np.abs(quantum_returns - returns))
            }
        }
        
        return backtest_results
    
    def _get_metal_quantum_enhancements(self, metal_type: MetalType) -> Dict[str, float]:
        """Metal-specific quantum enhancements"""
        enhancements = {
            'volatility_enhancement': 0.05,
            'correlation_reduction': 0.10,
            'risk_mitigation': 0.08,
            'pricing_accuracy': 0.12
        }
        
        if metal_type == MetalType.GOLD:
            enhancements['volatility_enhancement'] = 0.03  # Lower for gold
            enhancements['correlation_reduction'] = 0.05
        elif metal_type == MetalType.PALLADIUM:
            enhancements['volatility_enhancement'] = 0.08  # Higher for palladium
            enhancements['risk_mitigation'] = 0.12
        
        return enhancements
    
    def _generate_quantum_portfolio_insights(self, optimization_result: Dict[str, Any]) -> List[str]:
        """Quantum portfolio insights generation"""
        insights = []
        
        # Quantum enhancement insights
        if 'quantum_enhancement' in optimization_result:
            enhancement = optimization_result['quantum_enhancement']
            if enhancement > 0.1:
                insights.append(f"Strong quantum optimization advantage detected (enhancement: {enhancement:.3f})")
            elif enhancement > 0.05:
                insights.append(f"Moderate quantum optimization benefit (enhancement: {enhancement:.3f})")
        
        # Diversification insights
        if 'diversification_ratio' in optimization_result:
            div_ratio = optimization_result.get('diversification_ratio', 1)
            if div_ratio > 1.2:
                insights.append(f"Good diversification achieved (ratio: {div_ratio:.3f})")
            else:
                insights.append("Consider improving diversification")
        
        # Risk-return insights
        if 'sharpe_ratio' in optimization_result:
            sharpe = optimization_result.get('sharpe_ratio', 0)
            if sharpe > 1.5:
                insights.append(f"Excellent risk-adjusted returns (Sharpe: {sharpe:.3f})")
            elif sharpe > 1.0:
                insights.append(f"Good risk-adjusted performance (Sharpe: {sharpe:.3f})")
        
        return insights
    
    def _calculate_portfolio_quantum_enhancements(self, optimization_result: Dict[str, Any]) -> Dict[str, float]:
        """Portfolio quantum enhancements calculation"""
        enhancements = {}
        
        # Overall enhancement
        if 'quantum_enhancement' in optimization_result:
            enhancements['overall_enhancement'] = optimization_result['quantum_enhancement']
        
        # Risk reduction
        if 'quantum_portfolio_risk' in optimization_result:
            quantum_risk = optimization_result['quantum_portfolio_risk']
            enhancements['risk_reduction'] = 1 - quantum_risk
        
        # Performance enhancement
        if 'sharpe_ratio' in optimization_result:
            sharpe = optimization_result.get('sharpe_ratio', 0)
            enhancements['performance_enhancement'] = min(sharpe / 2.0, 1.0)  # Normalized
        
        return enhancements
    
    def export_portfolio_data(self, portfolio_name: str, format: str = 'json') -> Union[str, Dict]:
        """Portfolio data export"""
        if portfolio_name not in self.portfolio_manager.portfolios:
            raise ValueError(f"Portfolio {portfolio_name} not found")
        
        portfolio = self.portfolio_manager.portfolios[portfolio_name]
        
        if format == 'json':
            return self.portfolio_manager.save_portfolio(portfolio_name)
        elif format == 'dict':
            # Return portfolio as dictionary
            return {
                'name': portfolio.name,
                'description': portfolio.description,
                'assets': [
                    {
                        'symbol': asset.symbol,
                        'asset_type': asset.asset_type.value,
                        'expected_return': asset.expected_return,
                        'volatility': asset.volatility,
                        'current_price': asset.current_price,
                        'sector': asset.sector
                    }
                    for asset in portfolio.assets
                ],
                'weights': portfolio.weights.tolist(),
                'performance_history': portfolio.performance_history
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """System status check"""
        return {
            'timestamp': datetime.now(),
            'status': 'operational',
            'components': {
                'config': self.config is not None,
                'metal_pricer': self.metal_pricer is not None,
                'pricing_models': self.pricing_models is not None,
                'portfolio_optimizer': self.portfolio_optimizer is not None,
                'portfolio_manager': self.portfolio_manager is not None
            },
            'performance': {
                'total_portfolios': len(self.portfolio_manager.portfolios),
                'cached_optimizations': len(self.optimization_cache),
                'quantum_enhancements_active': len(self.quantum_enhancements)
            }
        }

def create_demo_portfolio() -> Dict[str, Any]:
    """Demo portfolio yaratish"""
    engine = QuantumPricingPortfolioEngine()
    
    # Comprehensive portfolio
    portfolio_result = engine.create_comprehensive_portfolio("Demo Quantum Portfolio")
    
    # Metal futures pricing
    gold_pricing = engine.price_metal_futures(MetalType.GOLD, 2000.0)
    silver_pricing = engine.price_metal_futures(MetalType.SILVER, 25.0)
    
    # Dashboard
    dashboard = engine.generate_quantum_portfolio_dashboard("Demo Quantum Portfolio")
    
    return {
        'portfolio': portfolio_result,
        'metal_pricing': {
            'gold': gold_pricing,
            'silver': silver_pricing
        },
        'dashboard': dashboard,
        'system_status': engine.get_system_status()
    }

if __name__ == "__main__":
    # Demo
    print("Quantum Pricing Portfolio Engine Demo")
    print("=" * 50)
    
    # Create demo
    demo_result = create_demo_portfolio()
    
    print(f"Portfolio Created: {demo_result['portfolio']['portfolio']['portfolio_info']['name']}")
    print(f"Number of Assets: {demo_result['portfolio']['portfolio']['portfolio_info']['num_assets']}")
    print(f"Expected Return: {demo_result['portfolio']['portfolio']['risk_metrics']['expected_return']:.4f}")
    print(f"Sharpe Ratio: {demo_result['portfolio']['portfolio']['risk_metrics']['sharpe_ratio']:.4f}")
    
    print(f"\nMetal Futures Pricing:")
    print(f"Gold Contracts: {len(demo_result['metal_pricing']['gold']['contracts'])}")
    print(f"Silver Contracts: {len(demo_result['metal_pricing']['silver']['contracts'])}")
    
    print(f"\nSystem Status: {demo_result['system_status']['status']}")
    print(f"Quantum Enhancement Active: {demo_result['dashboard']['system_performance']['quantum_enhancement_factor']:.3f}")