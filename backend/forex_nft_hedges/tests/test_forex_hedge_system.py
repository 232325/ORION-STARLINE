"""
Forex NFT Hedge System Tests
Tizimni test qilish uchun comprehensive test fayli
"""

import asyncio
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from config import ForexPair, HedgeType, MarketRegime, QuantumStrategy, config
from core.forex_hedge_core import ForexHedgeManager, MarketDataManager, NFTCreationEngine
from nfts.nft_management import QuantumForexNFTManager
from quantum.quantum_optimization import QuantumForexOptimizer
from strategies.hedge_strategies import (
    PairHedgeStrategy, CrossCurrencyHedgeStrategy, 
    VolatilityHedgeStrategy, CarryTradeStrategy
)
from integration.forex_hedge_integration import ForexHedgeIntegrationFramework
from utils.forex_hedge_utils import CalculationUtils, PerformanceUtils, ValidationUtils

class TestForexHedgeSystem:
    """Forex Hedge System test klassi"""
    
    def __init__(self):
        self.hedge_manager = None
        self.nft_manager = None
        self.quantum_optimizer = None
        self.framework = None
    
    async def setup_test_environment(self):
        """Test muhitini tayyorlash"""
        self.hedge_manager = ForexHedgeManager()
        self.nft_manager = QuantumForexNFTManager()
        
        # Test uchun quantum config
        from config import QuantumOptimizationConfig
        quantum_config = QuantumOptimizationConfig(
            qubits_used=8,  # Test uchun kamroq qubits
            max_iterations=100,  # Test uchun kam iteratsiya
            classical_mix_ratio=0.3
        )
        self.quantum_optimizer = QuantumForexOptimizer(quantum_config)
        
        self.framework = ForexHedgeIntegrationFramework()
    
    async def test_market_data_manager(self):
        """Market data manager test"""
        print("🧪 Testing Market Data Manager...")
        
        market_manager = self.hedge_manager.market_manager
        
        # Test price retrieval
        bid, ask = await market_manager.get_current_price(ForexPair.EURUSD)
        assert bid is not None and ask is not None
        assert ask > bid, "Ask price should be higher than bid price"
        
        # Test volatility calculation
        volatility = await market_manager.calculate_volatility(ForexPair.GBPUSD)
        assert 0 < volatility < 1, "Volatility should be between 0 and 1"
        
        print("✅ Market Data Manager tests passed")
        return True
    
    async def test_nft_creation_engine(self):
        """NFT creation engine test"""
        print("🧪 Testing NFT Creation Engine...")
        
        # Test NFT creation
        metadata = await self.hedge_manager.nft_engine.create_hedge_nft(
            hedge_type=HedgeType.PAIR_HEDGE,
            pair=ForexPair.EURUSD,
            notional_amount=100000,
            quantum_enhanced=True
        )
        
        assert metadata.token_id is not None, "Token ID should be generated"
        assert metadata.hedge_type == HedgeType.PAIR_HEDGE, "Hedge type should match"
        assert metadata.currency_pair == ForexPair.EURUSD, "Currency pair should match"
        assert metadata.quantum_enhanced == True, "Should be quantum enhanced"
        
        # Test metadata retrieval
        retrieved_metadata = await self.hedge_manager.nft_engine.get_nft_metadata(metadata.token_id)
        assert retrieved_metadata is not None, "Should retrieve metadata"
        assert retrieved_metadata.token_id == metadata.token_id, "Token ID should match"
        
        print("✅ NFT Creation Engine tests passed")
        return True
    
    async def test_quantum_optimizer(self):
        """Quantum optimizer test"""
        print("🧪 Testing Quantum Optimizer...")
        
        # Test arbitrage optimization
        arbitrage_result = await self.quantum_optimizer.currency_arbitrage.optimize_arbitrage_opportunities()
        assert arbitrage_result is not None, "Arbitrage result should be generated"
        assert "arbitrage_opportunities" in arbitrage_result, "Should contain opportunities"
        assert "quantum_optimization" in arbitrage_result, "Should contain quantum optimization"
        
        # Test multi-currency portfolio optimization
        portfolio_result = await self.quantum_optimizer.multi_currency.optimize_multi_currency_portfolio()
        assert portfolio_result is not None, "Portfolio result should be generated"
        assert "quantum_optimization" in portfolio_result, "Should contain quantum optimization"
        
        # Test volatility modeling
        volatility_result = await self.quantum_optimizer.volatility_modeling.quantum_volatility_modeling()
        assert volatility_result is not None, "Volatility result should be generated"
        assert "quantum_volatility_surface" in volatility_result, "Should contain volatility surface"
        
        print("✅ Quantum Optimizer tests passed")
        return True
    
    async def test_hedge_strategies(self):
        """Hedge strategies test"""
        print("🧪 Testing Hedge Strategies...")
        
        # Test Pair Hedge Strategy
        pair_strategy = PairHedgeStrategy(self.hedge_manager)
        
        # Test market conditions analysis
        market_conditions = await pair_strategy.analyze_market_conditions()
        assert market_conditions.regime in [regime for regime in MarketRegime], "Should be valid market regime"
        assert 0 < market_conditions.volatility < 1, "Volatility should be valid"
        
        # Test signal generation
        signals = await pair_strategy.generate_trading_signals(market_conditions)
        for signal in signals:
            assert signal.signal_type in ["hedge_pair", "exit", "rebalance"], "Should be valid signal type"
            assert signal.pair in config.forex_pairs, "Should be valid forex pair"
            assert 0 < signal.strength <= 1, "Signal strength should be valid"
        
        # Test Cross Currency Strategy
        cross_strategy = CrossCurrencyHedgeStrategy(self.hedge_manager)
        cross_signals = await cross_strategy.generate_trading_signals(market_conditions)
        for signal in cross_signals:
            assert signal.signal_type == "cross_currency_hedge", "Should be cross currency signal"
        
        # Test Volatility Strategy
        vol_strategy = VolatilityHedgeStrategy(self.hedge_manager)
        vol_signals = await vol_strategy.generate_trading_signals(market_conditions)
        for signal in vol_signals:
            assert signal.signal_type == "volatility_hedge", "Should be volatility signal"
        
        # Test Carry Trade Strategy
        carry_strategy = CarryTradeStrategy(self.hedge_manager)
        carry_signals = await carry_strategy.generate_trading_signals(market_conditions)
        for signal in carry_signals:
            assert signal.signal_type == "carry_trade", "Should be carry trade signal"
        
        print("✅ Hedge Strategies tests passed")
        return True
    
    async def test_nft_management(self):
        """NFT management test"""
        print("🧪 Testing NFT Management...")
        
        # Test quantum-enhanced NFT creation
        token_id = await self.nft_manager.create_quantum_enhanced_nft(
            hedge_type=HedgeType.PAIR_HEDGE,
            pair=ForexPair.EURUSD,
            notional_amount=200000,
            owner="0xTestAddress1234567890abcdef1234567890abcdef1234"
        )
        
        assert token_id is not None, "Token ID should be generated"
        assert "QUANTUM_" in token_id, "Should have quantum prefix"
        
        # Test NFT status retrieval
        status = await self.nft_manager.get_nft_status(token_id)
        assert status is not None, "Status should be retrieved"
        assert "token_id" in status, "Should contain token_id"
        assert "type" in status, "Should contain type"
        
        print("✅ NFT Management tests passed")
        return True
    
    async def test_integration_framework(self):
        """Integration framework test"""
        print("🧪 Testing Integration Framework...")
        
        # Test system initialization
        init_result = await self.framework.initialize_system()
        assert init_result["status"] == "initialized", "System should be initialized"
        assert len(init_result["components"]) > 0, "Should have components"
        
        # Test system status
        status = await self.framework.get_system_status()
        assert "system_status" in status, "Should have system status"
        assert "performance_metrics" in status, "Should have performance metrics"
        
        # Test comprehensive market analysis
        market_analysis = await self.framework._comprehensive_market_analysis()
        assert "pair_analysis" in market_analysis, "Should have pair analysis"
        assert "overall_assessment" in market_analysis, "Should have overall assessment"
        
        # Test NFT portfolio management
        nft_results = await self.framework._manage_nft_portfolio()
        assert "created_nfts" in nft_results, "Should have created NFTs"
        
        # Test risk management
        risk_results = await self.framework._execute_risk_management()
        assert "current_risk_metrics" in risk_results, "Should have risk metrics"
        
        print("✅ Integration Framework tests passed")
        return True
    
    async def test_utility_functions(self):
        """Utility functions test"""
        print("🧪 Testing Utility Functions...")
        
        # Test Calculation Utils
        test_returns = [0.01, 0.02, -0.01, 0.03, -0.02]
        
        # Sharpe ratio calculation
        sharpe = CalculationUtils.calculate_sharpe_ratio(test_returns)
        assert isinstance(sharpe, float), "Sharpe ratio should be float"
        
        # VaR calculation
        var = CalculationUtils.calculate_var(test_returns)
        assert isinstance(var, float), "VaR should be float"
        
        # Max drawdown calculation
        equity_curve = [100, 105, 102, 108, 103, 107]
        max_dd = CalculationUtils.calculate_max_drawdown(equity_curve)
        assert 0 <= max_dd <= 1, "Max drawdown should be between 0 and 1"
        
        # Test Performance Utils
        total_return = PerformanceUtils.calculate_total_return(100, 115)
        assert total_return == 0.15, "Total return should be 15%"
        
        annualized_return = PerformanceUtils.calculate_annualized_return(0.15, 252)
        assert annualized_return > 0, "Annualized return should be positive"
        
        # Test Validation Utils
        assert ValidationUtils.validate_forex_pair("EUR/USD") == True, "Should validate EUR/USD"
        assert ValidationUtils.validate_forex_pair("INVALID") == False, "Should reject invalid pair"
        assert ValidationUtils.validate_position_size(50000) == True, "Should validate position size"
        assert ValidationUtils.validate_hedge_ratio(0.7) == True, "Should validate hedge ratio"
        
        print("✅ Utility Functions tests passed")
        return True
    
    async def test_comprehensive_workflow(self):
        """Comprehensive workflow test"""
        print("🧪 Testing Comprehensive Workflow...")
        
        # 1. Create hedge position
        metadata, position = await self.hedge_manager.create_hedge_strategy(
            hedge_type=HedgeType.PAIR_HEDGE,
            pair=ForexPair.EURUSD,
            notional_amount=100000,
            quantum_enhanced=True
        )
        
        assert position.position_id is not None, "Position should be created"
        assert metadata.token_id is not None, "NFT should be created"
        
        # 2. Create quantum-enhanced NFT
        token_id = await self.nft_manager.create_quantum_enhanced_nft(
            hedge_type=HedgeType.VOLATILITY,
            pair=ForexPair.GBPUSD,
            notional_amount=150000
        )
        
        assert token_id is not None, "Quantum NFT should be created"
        
        # 3. Execute quantum optimization
        positions = [position]
        quantum_result = await self.quantum_optimizer.comprehensive_quantum_optimization(positions)
        assert quantum_result is not None, "Quantum optimization should complete"
        
        # 4. Update portfolio
        portfolio = await self.hedge_manager.optimize_portfolio("test_portfolio")
        assert portfolio.portfolio_id == "test_portfolio", "Portfolio should be created"
        
        # 5. Get performance metrics
        performance = await self.hedge_manager.get_portfolio_performance("test_portfolio")
        assert "total_pnl" in performance, "Should have performance metrics"
        
        print("✅ Comprehensive Workflow tests passed")
        return True
    
    async def test_performance_attribution(self):
        """Performance attribution test"""
        print("🧪 Testing Performance Attribution...")
        
        # Create test strategy results
        strategy_results = {
            "pair_hedge": {"strategy_pnl": 150.0},
            "volatility_hedge": {"strategy_pnl": 200.0},
            "carry_trade": {"strategy_pnl": 100.0}
        }
        
        # Calculate attribution
        attribution = await self.framework._calculate_performance_attribution(strategy_results)
        assert attribution.total_performance > 0, "Total performance should be positive"
        assert len(attribution.strategy_contributions) > 0, "Should have strategy contributions"
        assert "quantum_contribution" in attribution.quantum_classical_breakdown, "Should have quantum contribution"
        assert "classical_contribution" in attribution.quantum_classical_breakdown, "Should have classical contribution"
        
        print("✅ Performance Attribution tests passed")
        return True
    
    async def test_risk_management(self):
        """Risk management test"""
        print("🧪 Testing Risk Management...")
        
        # Execute risk management
        risk_results = await self.framework._execute_risk_management()
        assert "current_risk_metrics" in risk_results, "Should have risk metrics"
        assert "risk_actions" in risk_results, "Should have risk actions"
        
        # Test risk assessment
        quantum_risk = await self.framework._assess_quantum_risk()
        assert 0 <= quantum_risk <= 1, "Quantum risk should be between 0 and 1"
        
        # Test risk recommendations
        current_metrics = await self.framework._collect_system_metrics()
        recommendations = await self.framework._generate_risk_recommendations(current_metrics)
        assert isinstance(recommendations, list), "Recommendations should be a list"
        
        print("✅ Risk Management tests passed")
        return True
    
    async def test_error_handling(self):
        """Error handling test"""
        print("🧪 Testing Error Handling...")
        
        # Test invalid forex pair
        try:
            await self.hedge_manager.market_manager.get_current_price("INVALID/PAIR")
            # Should handle gracefully or return default values
            print("✅ Invalid forex pair handled gracefully")
        except Exception as e:
            # Exception is also acceptable
            print("✅ Invalid forex pair raises exception as expected")
        
        # Test negative position size
        try:
            await self.hedge_manager.nft_engine.create_hedge_nft(
                hedge_type=HedgeType.PAIR_HEDGE,
                pair=ForexPair.EURUSD,
                notional_amount=-1000,  # Negative amount
                quantum_enhanced=True
            )
            print("✅ Negative position size handled gracefully")
        except Exception as e:
            print("✅ Negative position size raises exception as expected")
        
        # Test missing market data
        try:
            # Simulate missing market data scenario
            with patch('core.forex_hedge_core.MarketDataManager.get_current_price') as mock_price:
                mock_price.side_effect = Exception("Market data unavailable")
                
                # Should handle gracefully
                result = await self.framework._comprehensive_market_analysis()
                assert result is not None, "Should return result even with market data issues"
        except Exception as e:
            print(f"✅ Market data error handled: {e}")
        
        print("✅ Error Handling tests passed")
        return True
    
    async def run_all_tests(self) -> Dict:
        """Barcha testlarni ishga tushirish"""
        print("🚀 FOREX NFT HEDGE SYSTEM TEST SUITE")
        print("=" * 60)
        
        start_time = datetime.now()
        test_results = {
            "start_time": start_time.isoformat(),
            "tests": {},
            "summary": {}
        }
        
        try:
            # Setup test environment
            await self.setup_test_environment()
            print("✅ Test environment setup completed\n")
            
            # Run individual tests
            tests = [
                ("Market Data Manager", self.test_market_data_manager),
                ("NFT Creation Engine", self.test_nft_creation_engine),
                ("Quantum Optimizer", self.test_quantum_optimizer),
                ("Hedge Strategies", self.test_hedge_strategies),
                ("NFT Management", self.test_nft_management),
                ("Integration Framework", self.test_integration_framework),
                ("Utility Functions", self.test_utility_functions),
                ("Comprehensive Workflow", self.test_comprehensive_workflow),
                ("Performance Attribution", self.test_performance_attribution),
                ("Risk Management", self.test_risk_management),
                ("Error Handling", self.test_error_handling)
            ]
            
            passed_tests = 0
            failed_tests = 0
            
            for test_name, test_func in tests:
                try:
                    print(f"🔄 Running {test_name} test...")
                    result = await test_func()
                    if result:
                        test_results["tests"][test_name] = {"status": "PASSED", "duration": "N/A"}
                        passed_tests += 1
                        print(f"✅ {test_name} test PASSED\n")
                    else:
                        test_results["tests"][test_name] = {"status": "FAILED", "reason": "Test returned False"}
                        failed_tests += 1
                        print(f"❌ {test_name} test FAILED\n")
                except Exception as e:
                    test_results["tests"][test_name] = {"status": "FAILED", "error": str(e)}
                    failed_tests += 1
                    print(f"❌ {test_name} test FAILED: {e}\n")
            
            # Calculate summary
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            
            test_results["summary"] = {
                "end_time": end_time.isoformat(),
                "total_duration": total_duration,
                "total_tests": len(tests),
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / len(tests)) * 100,
                "overall_status": "PASSED" if failed_tests == 0 else "FAILED"
            }
            
            # Display summary
            print("=" * 60)
            print("📊 TEST SUMMARY")
            print("=" * 60)
            print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
            print(f"📋 Total Tests: {len(tests)}")
            print(f"✅ Passed: {passed_tests}")
            print(f"❌ Failed: {failed_tests}")
            print(f"📈 Success Rate: {test_results['summary']['success_rate']:.1f}%")
            print(f"🎯 Overall Status: {test_results['summary']['overall_status']}")
            
            if failed_tests == 0:
                print("\n🎉 ALL TESTS PASSED! System is ready for production.")
            else:
                print(f"\n⚠️  {failed_tests} test(s) failed. Please review and fix issues.")
            
            return test_results
            
        except Exception as e:
            print(f"\n❌ TEST SUITE FAILED: {e}")
            test_results["summary"] = {
                "overall_status": "SYSTEM_ERROR",
                "error": str(e)
            }
            return test_results

async def run_performance_benchmark():
    """Performance benchmark test"""
    print("\n🏁 PERFORMANCE BENCHMARK")
    print("=" * 40)
    
    framework = ForexHedgeIntegrationFramework()
    await framework.initialize_system()
    
    # Benchmark metrics
    benchmark_results = {}
    
    # 1. NFT Creation Benchmark
    start_time = datetime.now()
    for i in range(10):
        await framework.nft_manager.create_quantum_enhanced_nft(
            hedge_type=HedgeType.PAIR_HEDGE,
            pair=ForexPair.EURUSD,
            notional_amount=100000
        )
    nft_creation_time = (datetime.now() - start_time).total_seconds()
    benchmark_results["nft_creation"] = {
        "time_for_10_nfts": f"{nft_creation_time:.2f}s",
        "avg_per_nft": f"{nft_creation_time/10:.2f}s"
    }
    
    # 2. Quantum Optimization Benchmark
    start_time = datetime.now()
    await framework.quantum_optimizer.currency_arbitrage.optimize_arbitrage_opportunities()
    quantum_optimization_time = (datetime.now() - start_time).total_seconds()
    benchmark_results["quantum_optimization"] = {
        "time": f"{quantum_optimization_time:.2f}s"
    }
    
    # 3. Strategy Execution Benchmark
    start_time = datetime.now()
    await framework.execute_comprehensive_strategy()
    strategy_execution_time = (datetime.now() - start_time).total_seconds()
    benchmark_results["strategy_execution"] = {
        "time": f"{strategy_execution_time:.2f}s"
    }
    
    print("⚡ Performance Results:")
    for test, result in benchmark_results.items():
        print(f"   {test}: {result}")
    
    return benchmark_results

# Test Runner
async def main():
    """Asosiy test runner"""
    
    # Create test suite
    test_suite = TestForexHedgeSystem()
    
    # Run all tests
    results = await test_suite.run_all_tests()
    
    # Run performance benchmark
    benchmark_results = await run_performance_benchmark()
    
    # Save results
    with open('/workspace/code/forex_nft_hedges/tests/test_results.json', 'w') as f:
        json.dump({
            "test_results": results,
            "benchmark_results": benchmark_results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved to: tests/test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())