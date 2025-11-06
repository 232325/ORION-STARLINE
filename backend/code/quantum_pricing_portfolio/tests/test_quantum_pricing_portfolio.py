"""
Quantum Pricing Portfolio - Test va Demo
"""
import numpy as np
import pandas as pd
from typing import Dict
from datetime import datetime, timedelta
import sys
import os

# Add the quantum_pricing_portfolio directory to Python path
quantum_portfolio_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, quantum_portfolio_path)

from config.quantum_config import QuantumPricingConfig, MetalType, AssetType
from metal_futures.metal_pricing import MetalFuturesQuantumPricer, create_metal_futures_portfolio
from pricing_models.quantum_models import QuantumPricingModelFactory, quantum_consensus_pricing, OptionContract
from portfolio_optimization.quantum_optimization import QuantumPortfolioOptimizer, PortfolioAsset
from multi_asset_portfolio.portfolio_manager import MultiAssetPortfolioManager, QuantumPortfolioTemplates
from __init__ import QuantumPricingPortfolioEngine, create_demo_portfolio

class QuantumPricingPortfolioTest:
    """Quantum Pricing Portfolio Test Suite"""
    
    def __init__(self):
        self.config = QuantumPricingConfig()
        self.test_results = {}
    
    def test_metal_futures_pricing(self) -> Dict:
        """Test metal futures pricing"""
        print("\n=== Metal Futures Quantum Pricing Test ===")
        
        try:
            # Create metal pricer
            pricer = MetalFuturesQuantumPricer(self.config.metals)
            
            # Test current prices
            current_prices = {
                MetalType.GOLD: 2000.0,
                MetalType.SILVER: 25.0,
                MetalType.PLATINUM: 1000.0,
                MetalType.PALLADIUM: 2000.0
            }
            
            # Test pricing for each metal
            results = {}
            for metal, price in current_prices.items():
                # Create sample contract
                from metal_futures.metal_pricing import MetalContract
                contract = MetalContract(
                    metal_type=metal,
                    expiration_month=3,
                    expiration_year=datetime.now().year + 1,
                    strike_price=price * 1.02
                )
                
                # Price the contract
                pricing_result = pricer.price_metal_future(metal, price, contract)
                risk_metrics = pricer.quantum_risk_metrics(metal, price, contract)
                
                results[metal.value] = {
                    'pricing': pricing_result,
                    'risk_metrics': risk_metrics
                }
                
                print(f"{metal.value}: ${pricing_result['fair_value']:.2f} (Risk: {risk_metrics['quantum_risk_score']:.3f})")
            
            # Test cross-metal arbitrage
            arbitrage_opportunities = pricer.cross_metal_arbitrage(current_prices, np.eye(4))
            print(f"\nArbitrage Opportunities: {len(arbitrage_opportunities)}")
            
            self.test_results['metal_futures'] = {
                'status': 'PASS',
                'results': results,
                'arbitrage_count': len(arbitrage_opportunities)
            }
            
            return self.test_results['metal_futures']
            
        except Exception as e:
            print(f"Metal futures test failed: {e}")
            self.test_results['metal_futures'] = {'status': 'FAIL', 'error': str(e)}
            return self.test_results['metal_futures']
    
    def test_quantum_pricing_models(self) -> Dict:
        """Test quantum pricing models"""
        print("\n=== Quantum Pricing Models Test ===")
        
        try:
            # Create test option
            option = OptionContract(
                S=100.0, K=105.0, T=0.25, r=0.02, sigma=0.2, option_type='call'
            )
            
            # Create models
            models = QuantumPricingModelFactory.create_ensemble(
                ['black_scholes', 'monte_carlo', 'binomial'], 
                self.config.quantum
            )
            
            results = {}
            print("Individual Models:")
            for name, model in models.items():
                try:
                    result = model.price(option)
                    greeks = model.greeks(option)
                    
                    price_key = 'quantum_consensus' if 'quantum_consensus' in result else ('quantum_price' if 'quantum_price' in result else 'fair_value')
                    results[name] = {
                        'price': result[price_key],
                        'greeks': greeks
                    }
                    
                    print(f"{name}: ${result[price_key]:.4f}")
                    print(f"  Delta: {greeks.get('delta', 0):.4f}, Gamma: {greeks.get('gamma', 0):.4f}")
                    
                except Exception as e:
                    print(f"{name}: Error - {e}")
                    results[name] = {'error': str(e)}
            
            # Consensus pricing
            consensus_result = quantum_consensus_pricing(models, option)
            print(f"\nConsensus Price: ${consensus_result['consensus_price']:.4f}")
            print(f"Model Confidence: {consensus_result['model_confidence']:.4f}")
            
            self.test_results['pricing_models'] = {
                'status': 'PASS',
                'individual_results': results,
                'consensus_result': consensus_result
            }
            
            return self.test_results['pricing_models']
            
        except Exception as e:
            print(f"Pricing models test failed: {e}")
            self.test_results['pricing_models'] = {'status': 'FAIL', 'error': str(e)}
            return self.test_results['pricing_models']
    
    def test_portfolio_optimization(self) -> Dict:
        """Test portfolio optimization"""
        print("\n=== Portfolio Optimization Test ===")
        
        try:
            # Create test assets
            assets = [
                PortfolioAsset("AAPL", AssetType.STOCKS, 0.12, 0.25, 150.0, 2e12, "Technology"),
                PortfolioAsset("GOOGL", AssetType.STOCKS, 0.15, 0.30, 2800.0, 1.8e12, "Technology"),
                PortfolioAsset("TSLA", AssetType.STOCKS, 0.25, 0.50, 800.0, 800e9, "Automotive"),
                PortfolioAsset("GOLD", AssetType.METALS, 0.08, 0.20, 2000.0, None, "Commodity")
            ]
            
            expected_returns = np.array([0.12, 0.15, 0.25, 0.08])
            covariance_matrix = np.array([
                [0.0625, 0.0300, 0.0400, 0.0100],
                [0.0300, 0.0900, 0.0350, 0.0150],
                [0.0400, 0.0350, 0.2500, 0.0200],
                [0.0100, 0.0150, 0.0200, 0.0400]
            ])
            
            # Test optimizer
            optimizer = QuantumPortfolioOptimizer(self.config.portfolio)
            
            # Mean variance optimization
            print("Mean-Variance Optimization:")
            mv_result = optimizer.optimize_portfolio(assets, expected_returns, covariance_matrix, 'mean_variance')
            print(f"Expected Return: {mv_result['expected_return']:.4f}")
            print(f"Volatility: {mv_result['volatility']:.4f}")
            print(f"Sharpe Ratio: {mv_result['sharpe_ratio']:.4f}")
            print(f"Quantum Enhancement: {mv_result['quantum_enhancement']:.4f}")
            
            # Risk parity
            print("\nRisk Parity:")
            rp_result = optimizer.optimize_portfolio(assets, expected_returns, covariance_matrix, 'risk_parity')
            print(f"Risk Parity Score: {rp_result['risk_parity_score']:.4f}")
            print(f"Risk Concentration: {rp_result['risk_concentration']:.4f}")
            
            # Diversification
            print("\nDiversification:")
            div_result = optimizer.optimize_portfolio(assets, expected_returns, covariance_matrix, 'diversification')
            print(f"Diversification Ratio: {div_result['diversification_ratio']:.4f}")
            print(f"Effective Assets: {div_result['effective_number_of_assets']:.2f}")
            
            self.test_results['portfolio_optimization'] = {
                'status': 'PASS',
                'mean_variance': mv_result,
                'risk_parity': rp_result,
                'diversification': div_result
            }
            
            return self.test_results['portfolio_optimization']
            
        except Exception as e:
            print(f"Portfolio optimization test failed: {e}")
            self.test_results['portfolio_optimization'] = {'status': 'FAIL', 'error': str(e)}
            return self.test_results['portfolio_optimization']
    
    def test_multi_asset_portfolio(self) -> Dict:
        """Test multi-asset portfolio management"""
        print("\n=== Multi-Asset Portfolio Test ===")
        
        try:
            # Create manager
            manager = MultiAssetPortfolioManager(self.config.portfolio, self.config.market)
            
            # Create portfolio
            portfolio = QuantumPortfolioTemplates.create_balanced_portfolio()
            manager.portfolios['test_portfolio'] = portfolio
            
            print(f"Created portfolio: {portfolio.name}")
            print(f"Number of assets: {len(portfolio.assets)}")
            
            # Optimize portfolio
            optimization_result = manager.optimize_portfolio('test_portfolio')
            print(f"\nOptimization Results:")
            print(f"Expected Return: {optimization_result['portfolio_metrics']['expected_return']:.4f}")
            print(f"Volatility: {optimization_result['portfolio_metrics']['volatility']:.4f}")
            
            # Portfolio performance
            performance = manager.get_portfolio_performance('test_portfolio')
            print(f"Portfolio Sharpe Ratio: {performance['portfolio_metrics']['sharpe_ratio']:.4f}")
            
            # Test rebalancing
            rebalancing_result = manager.rebalance_portfolio('test_portfolio')
            print(f"\nRebalancing Status: {rebalancing_result['rebalancing_successful']}")
            
            # Generate report
            report = manager.generate_portfolio_report('test_portfolio')
            print(f"Portfolio Value: ${report['portfolio_info']['total_value']:.2f}")
            
            self.test_results['multi_asset_portfolio'] = {
                'status': 'PASS',
                'optimization': optimization_result,
                'performance': performance,
                'rebalancing': rebalancing_result,
                'report': report
            }
            
            return self.test_results['multi_asset_portfolio']
            
        except Exception as e:
            print(f"Multi-asset portfolio test failed: {e}")
            self.test_results['multi_asset_portfolio'] = {'status': 'FAIL', 'error': str(e)}
            return self.test_results['multi_asset_portfolio']
    
    def test_full_system_integration(self) -> Dict:
        """Test full system integration"""
        print("\n=== Full System Integration Test ===")
        
        try:
            # Create main engine
            engine = QuantumPricingPortfolioEngine(self.config)
            
            # Create comprehensive portfolio
            portfolio_result = engine.create_comprehensive_portfolio("Integration Test Portfolio")
            
            print(f"Portfolio Created: {portfolio_result['portfolio']['portfolio_info']['name']}")
            print(f"Total Assets: {portfolio_result['portfolio']['portfolio_info']['num_assets']}")
            print(f"Expected Return: {portfolio_result['portfolio']['risk_metrics']['expected_return']:.4f}")
            print(f"Sharpe Ratio: {portfolio_result['portfolio']['risk_metrics']['sharpe_ratio']:.4f}")
            
            # Test metal futures pricing
            gold_pricing = engine.price_metal_futures(MetalType.GOLD, 2000.0)
            print(f"\nGold Futures Pricing: {len(gold_pricing['contracts'])} contracts")
            
            # Test option pricing
            from pricing_models.quantum_models import OptionContract
            test_option = OptionContract(S=100, K=105, T=0.25, r=0.02, sigma=0.2, option_type='call')
            option_result = engine.price_option_with_quantum_models(test_option)
            print(f"Option Consensus Price: ${option_result['consensus_result']['consensus_price']:.4f}")
            
            # Test trading strategy
            trading_result = engine.execute_quantum_trading_strategy("Integration Test Portfolio", 'rebalancing')
            print(f"Trading Strategy: {trading_result['strategy']}")
            
            # Generate dashboard
            dashboard = engine.generate_quantum_portfolio_dashboard("Integration Test Portfolio")
            print(f"Dashboard Generated: {dashboard['timestamp']}")
            
            # System status
            status = engine.get_system_status()
            print(f"System Status: {status['status']}")
            
            self.test_results['full_integration'] = {
                'status': 'PASS',
                'portfolio_result': portfolio_result,
                'gold_pricing': gold_pricing,
                'option_pricing': option_result,
                'trading_strategy': trading_result,
                'dashboard': dashboard,
                'system_status': status
            }
            
            return self.test_results['full_integration']
            
        except Exception as e:
            print(f"Full system integration test failed: {e}")
            self.test_results['full_integration'] = {'status': 'FAIL', 'error': str(e)}
            return self.test_results['full_integration']
    
    def run_all_tests(self) -> Dict[str, Dict]:
        """Run all tests"""
        print("Quantum Pricing Portfolio - Test Suite")
        print("=" * 60)
        
        tests = [
            self.test_metal_futures_pricing,
            self.test_quantum_pricing_models,
            self.test_portfolio_optimization,
            self.test_multi_asset_portfolio,
            self.test_full_system_integration
        ]
        
        for test in tests:
            test()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result['status'] == 'PASS')
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result['status'] == 'PASS' else "✗ FAIL"
            print(f"{test_name}: {status}")
            if result['status'] == 'FAIL':
                print(f"  Error: {result.get('error', 'Unknown error')}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return self.test_results

def demo_quantum_pricing_portfolio():
    """Quantum Pricing Portfolio Demo"""
    print("Quantum Pricing Portfolio - Full Demo")
    print("=" * 60)
    
    try:
        # Run demo
        demo_result = create_demo_portfolio()
        
        print(f"\nPortfolio Overview:")
        portfolio = demo_result['portfolio']['portfolio']
        print(f"Name: {portfolio['portfolio_info']['name']}")
        print(f"Assets: {portfolio['portfolio_info']['num_assets']}")
        print(f"Value: ${portfolio['portfolio_info']['total_value']:.2f}")
        
        print(f"\nPerformance Metrics:")
        metrics = portfolio['risk_metrics']
        print(f"Expected Return: {metrics['expected_return']:.4f} ({metrics['expected_return']*100:.1f}%)")
        print(f"Volatility: {metrics['volatility']:.4f} ({metrics['volatility']*100:.1f}%)")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
        print(f"Max Drawdown: {metrics['max_drawdown']:.4f} ({metrics['max_drawdown']*100:.1f}%)")
        
        print(f"\nMetal Futures Pricing:")
        gold = demo_result['metal_pricing']['gold']
        silver = demo_result['metal_pricing']['silver']
        print(f"Gold: {len(gold['contracts'])} contracts")
        print(f"Silver: {len(silver['contracts'])} contracts")
        
        print(f"\nSystem Dashboard:")
        dashboard = demo_result['dashboard']
        print(f"Status: {dashboard['system_status']}")
        performance = dashboard['system_performance']
        print(f"Quantum Enhancement: {performance['quantum_enhancement_factor']:.3f}")
        print(f"Optimization Success Rate: {performance['optimization_success_rate']}")
        
        print(f"\nSystem Status:")
        status = demo_result['system_status']
        print(f"Overall Status: {status['status']}")
        print(f"Total Portfolios: {status['performance']['total_portfolios']}")
        
        return demo_result
        
    except Exception as e:
        print(f"Demo failed: {e}")
        return None

if __name__ == "__main__":
    # Run tests
    test_suite = QuantumPricingPortfolioTest()
    test_results = test_suite.run_all_tests()
    
    print("\n" + "=" * 60)
    print("RUNNING DEMO...")
    print("=" * 60)
    
    # Run demo
    demo_result = demo_quantum_pricing_portfolio()
    
    if demo_result:
        print("\nDemo completed successfully!")
    else:
        print("\nDemo failed.")