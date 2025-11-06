#!/usr/bin/env python3
"""
Test Suite for NFT Hedge Fund System
Comprehensive testing of all system components
"""

import unittest
import asyncio
import time
import numpy as np
from typing import Dict, List

# Import system components
from nft_hedge_fund_system import NFTHedgeFundSystem, MetalType, SystemStatus
from strategies.hedging_strategies import (
    HedgingPortfolioManager, MetalPriceData, HedgeStrategy,
    StaticDynamicHedging, VolatilityTargetingHedging
)
from quantum_algorithms.quantum_portfolio_optimizer import (
    QuantumPortfolioOptimizer, MetalData as QuantumMetalData
)
from governance.governance_system import (
    NFTHedgeFundGovernance, ProposalType, ProposalStatus
)
from config import Config

class TestNFTHedgeFundSystem(unittest.TestCase):
    """Test suite for main NFT Hedge Fund System"""
    
    def setUp(self):
        """Set up test environment"""
        # Initialize system with small test capital
        self.fund = NFTHedgeFundSystem("TestNFTFund", 100000)  # $100K test fund
        self.fund.auto_rebalance = True
        self.fund.risk_limit_enabled = True
        
    def test_system_initialization(self):
        """Test system initialization"""
        self.assertEqual(self.fund.fund_name, "TestNFTFund")
        self.assertEqual(self.fund.initial_capital, 100000)
        self.assertEqual(self.fund.current_capital, 100000)
        self.assertEqual(self.fund.status, SystemStatus.RUNNING)
    
    async def test_trading_cycle(self):
        """Test trading cycle execution"""
        # Run one trading cycle
        await self.fund.run_trading_cycle()
        
        # Check that system is still running
        self.assertEqual(self.fund.status, SystemStatus.RUNNING)
        
        # Check that capital is still positive
        self.assertGreater(self.fund.current_capital, 0)
    
    def test_system_status(self):
        """Test system status retrieval"""
        status = self.fund.get_system_status()
        
        self.assertIn("fund_name", status)
        self.assertIn("status", status)
        self.assertIn("current_capital", status)
        self.assertIn("initial_capital", status)
        
        self.assertEqual(status["fund_name"], "TestNFTFund")
        self.assertEqual(status["initial_capital"], 100000)

class TestQuantumAlgorithms(unittest.TestCase):
    """Test suite for quantum algorithms"""
    
    def setUp(self):
        """Set up quantum algorithm test environment"""
        # Create sample metal data
        self.metal_data = [
            QuantumMetalData(
                symbol=MetalType.GOLD,
                current_price=2000.0,
                volatility=0.15,
                expected_return=0.05,
                correlation={MetalType.SILVER: 0.8},
                market_cap=1000000
            ),
            QuantumMetalData(
                symbol=MetalType.SILVER,
                current_price=25.0,
                volatility=0.30,
                expected_return=0.08,
                correlation={MetalType.GOLD: 0.8},
                market_cap=500000
            )
        ]
        
        self.optimizer = QuantumPortfolioOptimizer(self.metal_data)
    
    def test_optimizer_initialization(self):
        """Test quantum optimizer initialization"""
        self.assertIsNotNone(self.optimizer)
        self.assertEqual(len(self.optimizer.metals), 2)
        self.assertEqual(self.optimizer.n_metals, 2)
    
    def test_quantum_state_initialization(self):
        """Test quantum state initialization"""
        states = self.optimizer.initialize_quantum_states()
        
        self.assertIsInstance(states, dict)
        self.assertEqual(len(states), 2)
        
        for metal, state in states.items():
            self.assertIsNotNone(state.amplitude)
            self.assertIsNotNone(state.probability)
            self.assertGreaterEqual(state.probability, 0)
            self.assertLessEqual(state.probability, 1)
    
    def test_classical_optimization(self):
        """Test classical portfolio optimization"""
        weights = self.optimizer._classical_optimization(1.0)
        
        self.assertIsInstance(weights, dict)
        self.assertEqual(len(weights), 2)
        
        # Check weights sum to approximately 1
        total_weight = sum(weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=6)
        
        # Check all weights are non-negative
        for weight in weights.values():
            self.assertGreaterEqual(weight, 0)
    
    def test_quantum_optimization(self):
        """Test quantum portfolio optimization"""
        weights = self.optimizer.quantum_portfolio_optimization(
            risk_aversion=1.0,
            quantum_advantage=True
        )
        
        self.assertIsInstance(weights, dict)
        self.assertEqual(len(weights), 2)
        
        # Check weights are reasonable
        for metal, weight in weights.items():
            self.assertGreaterEqual(weight, 0)
            self.assertLessEqual(weight, 1)
    
    def test_quantum_volatility_modeling(self):
        """Test quantum volatility modeling"""
        volatilities = self.optimizer.quantum_volatility_modeling()
        
        self.assertIsInstance(volatilities, dict)
        self.assertEqual(len(volatilities), 2)
        
        for metal, vol in volatilities.items():
            self.assertGreater(vol, 0)
            self.assertIsInstance(vol, float)

class TestHedgingStrategies(unittest.TestCase):
    """Test suite for hedging strategies"""
    
    def setUp(self):
        """Set up hedging strategy test environment"""
        self.portfolio_manager = HedgingPortfolioManager()
        
        # Create sample market data
        self.market_data = {
            MetalType.GOLD: MetalPriceData(
                metal=MetalType.GOLD,
                current_price=2000.0,
                bid=1999.5,
                ask=2000.5,
                volume=1000000,
                open_interest=500000,
                implied_volatility=0.15,
                historical_volatility=0.12,
                timestamp=time.time()
            ),
            MetalType.SILVER: MetalPriceData(
                metal=MetalType.SILVER,
                current_price=25.0,
                bid=24.95,
                ask=25.05,
                volume=2000000,
                open_interest=800000,
                implied_volatility=0.25,
                historical_volatility=0.22,
                timestamp=time.time()
            )
        }
        
        self.portfolio_exposure = {
            MetalType.GOLD: 50000.0,    # $50K
            MetalType.SILVER: 20000.0   # $20K
        }
    
    def test_portfolio_manager_initialization(self):
        """Test portfolio manager initialization"""
        self.assertIsNotNone(self.portfolio_manager)
        self.assertEqual(len(self.portfolio_manager.strategies), 4)
    
    def test_optimal_hedge_ratio_calculation(self):
        """Test optimal hedge ratio calculation"""
        ratios = self.portfolio_manager.calculate_optimal_hedge_ratios(
            self.market_data, self.portfolio_exposure
        )
        
        self.assertIsInstance(ratios, dict)
        self.assertEqual(len(ratios), 2)
        
        for metal, ratio in ratios.items():
            self.assertGreaterEqual(ratio, 0)
            self.assertLessEqual(ratio, 1)
    
    def test_static_dynamic_hedging(self):
        """Test static-dynamic hedging strategy"""
        strategy = StaticDynamicHedging()
        
        ratios = strategy.calculate_hedge_ratio(
            self.market_data, self.portfolio_exposure
        )
        
        self.assertIsInstance(ratios, dict)
        for metal, ratio in ratios.items():
            self.assertGreaterEqual(ratio, 0.3)  # Minimum ratio
            self.assertLessEqual(ratio, 0.95)    # Maximum ratio
    
    def test_volatility_targeting_hedging(self):
        """Test volatility targeting strategy"""
        strategy = VolatilityTargetingHedging()
        
        ratios = strategy.calculate_hedge_ratio(
            self.market_data, self.portfolio_exposure
        )
        
        self.assertIsInstance(ratios, dict)
        for metal, ratio in ratios.items():
            self.assertGreaterEqual(ratio, 0.2)
            self.assertLessEqual(ratio, 0.9)

class TestGovernanceSystem(unittest.TestCase):
    """Test suite for governance system"""
    
    def setUp(self):
        """Set up governance test environment"""
        self.governance = NFTHedgeFundGovernance("TestFund", 100000)
        
        # Add some voting power
        self.governance.vote_weights["alice"] = 1000.0
        self.governance.vote_weights["bob"] = 1500.0
        self.governance.total_voting_power = 2500.0
    
    def test_governance_initialization(self):
        """Test governance system initialization"""
        self.assertEqual(self.governance.fund_name, "TestFund")
        self.assertEqual(self.governance.current_nav, 100000)
        self.assertEqual(self.governance.initial_nav, 100000)
        self.assertEqual(self.governance.performance_fee_rate, 0.20)
        self.assertEqual(self.governance.management_fee_rate, 0.02)
    
    def test_proposal_creation(self):
        """Test governance proposal creation"""
        proposal_id = self.governance.create_proposal(
            proposer="alice",
            proposal_type=ProposalType.PERFORMANCE_FEE_CHANGE,
            title="Test Proposal",
            description="Test proposal description",
            parameters={"new_rate": 0.15}
        )
        
        self.assertIsNotNone(proposal_id)
        self.assertIn(proposal_id, self.governance.proposals)
        
        proposal = self.governance.proposals[proposal_id]
        self.assertEqual(proposal.proposal_type, ProposalType.PERFORMANCE_FEE_CHANGE)
        self.assertEqual(proposal.title, "Test Proposal")
    
    def test_voting(self):
        """Test proposal voting"""
        proposal_id = self.governance.create_proposal(
            proposer="alice",
            proposal_type=ProposalType.PERFORMANCE_FEE_CHANGE,
            title="Test Proposal",
            description="Test proposal",
            parameters={"new_rate": 0.15}
        )
        
        # Cast votes
        success = self.governance.cast_vote(proposal_id, "alice", 1, 1000.0)
        self.assertTrue(success)
        
        success = self.governance.cast_vote(proposal_id, "bob", 1, 1500.0)
        self.assertTrue(success)
        
        proposal = self.governance.proposals[proposal_id]
        self.assertEqual(proposal.votes_for, 2500.0)
        self.assertEqual(proposal.votes_against, 0)
    
    def test_performance_fee_calculation(self):
        """Test performance fee calculation"""
        # Set NAV above high water mark
        self.governance.current_nav = 110000  # 10% gain
        
        fee = self.governance.calculate_performance_fees()
        self.assertGreater(fee, 0)
        
        # Fee should be 20% of the excess return
        expected_fee = (110000 - 100000) * 0.20  # $2000
        self.assertAlmostEqual(fee, expected_fee, places=2)

class TestConfig(unittest.TestCase):
    """Test suite for configuration system"""
    
    def test_config_loading(self):
        """Test configuration loading for different environments"""
        # Test development config
        dev_config = Config("development").get_config()
        self.assertEqual(dev_config.environment.value, "development")
        self.assertEqual(dev_config.fund_name, "QuantumMetal NFT Fund (Dev)")
        
        # Test testing config
        test_config = Config("testing").get_config()
        self.assertEqual(test_config.environment.value, "testing")
        self.assertEqual(test_config.fund_name, "QuantumMetal NFT Fund (Test)")
    
    def test_oracle_configuration(self):
        """Test oracle configuration"""
        config = Config("development").get_config()
        
        self.assertGreater(len(config.oracle_providers), 0)
        
        for oracle in config.oracle_providers:
            self.assertIsNotNone(oracle.name)
            self.assertIsNotNone(oracle.provider_type)
            self.assertGreater(oracle.weight, 0)
    
    def test_strategy_configuration(self):
        """Test strategy configuration"""
        config = Config("development").get_config()
        
        self.assertGreater(len(config.strategies), 0)
        
        total_weight = sum(strategy.weight for strategy in config.strategies if strategy.enabled)
        self.assertAlmostEqual(total_weight, 1.0, places=1)  # Allow small tolerance
    
    def test_risk_configuration(self):
        """Test risk configuration"""
        config = Config("development").get_config()
        
        self.assertGreater(config.risk_config.max_drawdown, 0)
        self.assertLess(config.risk_config.max_drawdown, 1)
        self.assertGreater(config.risk_config.var_limit, 0)
        self.assertLess(config.risk_config.var_limit, 1)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid configuration should have no errors
        config = Config("development")
        errors = config.validate_config()
        
        # The development config should be valid
        self.assertEqual(len(errors), 0, f"Configuration has errors: {errors}")

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    async def test_full_system_integration(self):
        """Test full system integration"""
        # Create a small fund for testing
        fund = NFTHedgeFundSystem("IntegrationTestFund", 50000)
        
        # Initialize quantum optimizer
        market_data = {
            MetalType.GOLD: MetalPriceData(
                metal=MetalType.GOLD,
                current_price=2000.0,
                bid=1999.5,
                ask=2000.5,
                volume=1000000,
                open_interest=500000,
                implied_volatility=0.15,
                historical_volatility=0.12,
                timestamp=time.time()
            )
        }
        
        await fund.initialize_quantum_optimizer(market_data)
        
        # Run a few trading cycles
        for i in range(3):
            await fund.run_trading_cycle()
            
            # Check system is still running
            self.assertEqual(fund.status, SystemStatus.RUNNING)
        
        # Generate a report
        report = await fund.generate_report()
        self.assertIn("system_status", report)
        self.assertIn("governance_report", report)
        self.assertIn("performance_report", report)
        
        # Cleanup
        await fund.shutdown()
        self.assertEqual(fund.status, SystemStatus.SHUTDOWN)

async def run_async_tests():
    """Run async tests"""
    print("Running async integration tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add integration test
    integration_test = TestIntegration()
    suite.addTest(integration_test, 'test_full_system_integration')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("NFT HEDGE FUND SYSTEM - TEST SUITE")
    print("=" * 60)
    
    # Test results
    all_results = []
    
    # Run sync tests
    print("\n1. Running System Tests...")
    system_suite = unittest.TestLoader().loadTestsFromTestCase(TestNFTHedgeFundSystem)
    system_runner = unittest.TextTestRunner(verbosity=1)
    system_result = system_runner.run(system_suite)
    all_results.append(system_result.wasSuccessful())
    
    print("\n2. Running Quantum Algorithm Tests...")
    quantum_suite = unittest.TestLoader().loadTestsFromTestCase(TestQuantumAlgorithms)
    quantum_runner = unittest.TextTestRunner(verbosity=1)
    quantum_result = quantum_runner.run(quantum_suite)
    all_results.append(quantum_result.wasSuccessful())
    
    print("\n3. Running Hedging Strategy Tests...")
    strategy_suite = unittest.TestLoader().loadTestsFromTestCase(TestHedgingStrategies)
    strategy_runner = unittest.TextTestRunner(verbosity=1)
    strategy_result = strategy_runner.run(strategy_suite)
    all_results.append(strategy_result.wasSuccessful())
    
    print("\n4. Running Governance System Tests...")
    governance_suite = unittest.TestLoader().loadTestsFromTestCase(TestGovernanceSystem)
    governance_runner = unittest.TextTestRunner(verbosity=1)
    governance_result = governance_runner.run(governance_suite)
    all_results.append(governance_result.wasSuccessful())
    
    print("\n5. Running Configuration Tests...")
    config_suite = unittest.TestLoader().loadTestsFromTestCase(TestConfig)
    config_runner = unittest.TextTestRunner(verbosity=1)
    config_result = config_runner.run(config_suite)
    all_results.append(config_result.wasSuccessful())
    
    # Run async tests
    print("\n6. Running Integration Tests...")
    async_success = asyncio.run(run_async_tests())
    all_results.append(async_success)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    test_suites = [
        "System Tests",
        "Quantum Algorithm Tests", 
        "Hedging Strategy Tests",
        "Governance System Tests",
        "Configuration Tests",
        "Integration Tests"
    ]
    
    for i, (suite_name, success) in enumerate(zip(test_suites, all_results)):
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{i+1}. {suite_name}: {status}")
    
    total_passed = sum(all_results)
    total_tests = len(all_results)
    
    print(f"\nTotal: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! System is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)