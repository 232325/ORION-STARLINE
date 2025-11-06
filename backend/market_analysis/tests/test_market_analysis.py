"""
Market Analysis Test Suite
==========================

Bozor tahlil tizimi uchun test fayllar.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_analysis import (
    PriceImpactModel, LiquidityAnalyzer, ForexSessionManager,
    MetalMarketAnalyzer, MarketRegimeDetector, AdaptiveStrategyManager
)


class TestPriceImpactModel(unittest.TestCase):
    """Price Impact Model testlari"""
    
    def setUp(self):
        self.model = PriceImpactModel()
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Test uchun sample ma'lumotlar"""
        dates = pd.date_range('2023-01-01', periods=1000, freq='1H')
        return pd.DataFrame({
            'open': 1.1000 + np.random.normal(0, 0.01, 1000),
            'high': 1.1050 + np.random.normal(0, 0.01, 1000),
            'low': 1.0950 + np.random.normal(0, 0.01, 1000),
            'close': 1.1000 + np.random.normal(0, 0.01, 1000),
            'volume': np.random.lognormal(10, 1, 1000)
        }, index=dates)
    
    def test_permanent_impact_calculation(self):
        """Doimiy impact hisoblash testi"""
        impact = self.model.calculate_permanent_impact(
            volume=100000,
            avg_volume=1000000,
            volatility=0.02,
            time_of_day=14
        )
        
        self.assertGreaterEqual(impact, 0)
        self.assertLessEqual(impact, 0.1)
    
    def test_temporary_impact_calculation(self):
        """Vaqtinchalik impact hisoblash testi"""
        impact = self.model.calculate_temporary_impact(
            volume=100000,
            avg_volume=1000000,
            order_book_depth=10000000,
            spread=0.0015
        )
        
        self.assertGreaterEqual(impact, 0)
        self.assertLessEqual(impact, 0.05)
    
    def test_total_impact_calculation(self):
        """Jami impact hisoblash testi"""
        total_impact = self.model.calculate_total_impact(
            volume=100000,
            avg_volume=1000000,
            volatility=0.02,
            time_of_day=14,
            order_book_depth=10000000,
            spread=0.0015
        )
        
        self.assertIn('total_impact', total_impact)
        self.assertIn('permanent_impact', total_impact)
        self.assertIn('temporary_impact', total_impact)
        self.assertGreaterEqual(total_impact['total_impact'], 0)


class TestLiquidityAnalyzer(unittest.TestCase):
    """Liquidity Analyzer testlari"""
    
    def setUp(self):
        self.analyzer = LiquidityAnalyzer()
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Sample market ma'lumotlari"""
        dates = pd.date_range('2023-01-01', periods=500, freq='1H')
        return pd.DataFrame({
            'open': 1.1000 + np.random.normal(0, 0.01, 500),
            'high': 1.1050 + np.random.normal(0, 0.01, 500),
            'low': 1.0950 + np.random.normal(0, 0.01, 500),
            'close': 1.1000 + np.random.normal(0, 0.01, 500),
            'volume': np.random.lognormal(8, 1, 500)
        }, index=dates)
    
    def test_liquidity_depth_analysis(self):
        """Liquidity chuqurlik tahlili"""
        result = self.analyzer.analyze_liquidity_depth(self.sample_data)
        
        self.assertIn('liquidity_score', result.columns)
        self.assertIn('combined_liquidity', result.columns)
        self.assertIn('liquidity_regime', result.columns)
        
        # Check scores are in reasonable range
        self.assertTrue(all(0 <= score <= 1 for score in result['liquidity_score'].dropna()))
    
    def test_liquidity_metrics(self):
        """Liquidity metriklari"""
        metrics = self.analyzer.calculate_liquidity_metrics(self.sample_data)
        
        self.assertIn('avg_volume', metrics)
        self.assertIn('volume_cv', metrics)
        self.assertIn('liquidity_efficiency', metrics)
        
        self.assertGreaterEqual(metrics['avg_volume'], 0)
        self.assertGreaterEqual(metrics['volume_cv'], 0)
    
    def test_liquidity_event_detection(self):
        """Liquidity voqealar aniqlash"""
        result = self.analyzer.detect_liquidity_events(self.sample_data, threshold=2.0)
        
        self.assertIn('volume_spike', result.columns)
        self.assertIn('volume_drought', result.columns)
        self.assertIn('liquidity_event_score', result.columns)


class TestForexSessionManager(unittest.TestCase):
    """Forex Session Manager testlari"""
    
    def setUp(self):
        self.session_manager = ForexSessionManager()
    
    def test_current_session_detection(self):
        """Joriy session aniqlash"""
        current_time = datetime(2023, 6, 15, 14, 30)  # 14:30 UTC
        session = self.session_manager.get_current_session(current_time)
        
        self.assertIsNotNone(session)
        self.assertIsInstance(session.name, str)
        self.assertIsInstance(session.volatility_multiplier, float)
        self.assertIsInstance(session.liquidity_multiplier, float)
    
    def test_session_schedule(self):
        """Session jadvali"""
        schedule = self.session_manager.get_session_schedule()
        
        self.assertIn('Asian', schedule)
        self.assertIn('European', schedule)
        self.assertIn('American', schedule)
        
        for session_name, session_info in schedule.items():
            self.assertIn('start', session_info)
            self.assertIn('end', session_info)
            self.assertIn('duration_hours', session_info)
    
    def test_optimal_trading_hours(self):
        """Optimal trading soatlari"""
        recommendations = self.session_manager.get_optimal_trading_hours('EURUSD')
        
        self.assertIn('pair_type', recommendations)
        self.assertIn('general_recommendations', recommendations)
        self.assertIn('current_session', recommendations)
        
        self.assertEqual(recommendations['pair_type'], 'major')
    
    def test_overlap_analysis(self):
        """Overlap tahlili"""
        current_time = datetime(2023, 6, 15, 14, 30)
        analysis = self.session_manager.analyze_session_overlap_opportunities(current_time)
        
        self.assertIn('overlap_opportunities', analysis)
        self.assertIn('current_analysis', analysis)
        
        opportunities = analysis['overlap_opportunities']
        self.assertIn('europe_america_overlap', opportunities)


class TestMetalMarketAnalyzer(unittest.TestCase):
    """Metal Market Analyzer testlari"""
    
    def setUp(self):
        self.analyzer = MetalMarketAnalyzer()
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Sample metal price data"""
        dates = pd.date_range('2023-01-01', periods=200, freq='1D')
        return pd.DataFrame({
            'open': 1800 + np.random.normal(0, 20, 200),
            'high': 1810 + np.random.normal(0, 20, 200),
            'low': 1790 + np.random.normal(0, 20, 200),
            'close': 1800 + np.random.normal(0, 20, 200),
            'volume': np.random.lognormal(8, 1, 200)
        }, index=dates)
    
    def test_market_opening_patterns(self):
        """Bozor ochilish patternlari"""
        patterns = self.analyzer.analyze_market_opening_patterns('XAUUSD', self.sample_data)
        
        self.assertIn('opening_gap_analysis', patterns)
        self.assertIn('day_of_week_patterns', patterns)
        self.assertIn('overall_opening_characteristics', patterns)
    
    def test_market_closing_patterns(self):
        """Bozor yopilish patternlari"""
        patterns = self.analyzer.analyze_market_closing_patterns('XAUUSD', self.sample_data)
        
        self.assertIn('closing_minute_patterns', patterns)
        self.assertIn('intraday_closing_stats', patterns)
    
    def test_seasonal_patterns(self):
        """Seasonal patternlar"""
        patterns = self.analyzer.analyze_seasonal_patterns('XAUUSD', self.sample_data)
        
        self.assertIn('monthly_patterns', patterns)
        self.assertIn('seasonal_recommendations', patterns)
    
    def test_optimal_trading_hours(self):
        """Optimal trading soatlari"""
        hours = self.analyzer.get_optimal_trading_hours('XAUUSD')
        
        self.assertIn('optimal_hours', hours)
        self.assertIn('hour_recommendations', hours)
        self.assertIn('session_overview', hours)
        
        self.assertIsInstance(hours['optimal_hours'], list)
    
    def test_market_report_creation(self):
        """Bozor hisoboti yaratish"""
        report = self.analyzer.create_metal_market_report('XAUUSD', self.sample_data)
        
        self.assertIn('symbol', report)
        self.assertIn('market_characteristics', report)
        self.assertIn('opening_patterns', report)
        self.assertIn('closing_patterns', report)
        self.assertIn('seasonal_patterns', report)
        self.assertIn('trading_recommendations', report)


class TestMarketRegimeDetector(unittest.TestCase):
    """Market Regime Detector testlari"""
    
    def setUp(self):
        self.detector = MarketRegimeDetector()
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Sample market data"""
        dates = pd.date_range('2023-01-01', periods=200, freq='1H')
        return pd.DataFrame({
            'open': 1.1000 + np.cumsum(np.random.normal(0, 0.001, 200)),
            'high': 1.1050 + np.cumsum(np.random.normal(0, 0.001, 200)),
            'low': 1.0950 + np.cumsum(np.random.normal(0, 0.001, 200)),
            'close': 1.1000 + np.cumsum(np.random.normal(0, 0.001, 200)),
            'volume': np.random.lognormal(8, 1, 200)
        }, index=dates)
    
    def test_trending_ranging_detection(self):
        """Trending/ranging rejim aniqlash"""
        regimes = self.detector.detect_trending_ranging_regime(self.sample_data, window=20)
        
        self.assertIsInstance(regimes, pd.Series)
        self.assertTrue(len(regimes) > 0)
        
        # Check for valid regime values
        valid_regimes = {'trending', 'ranging'}
        unique_regimes = set(regimes.dropna().unique())
        self.assertTrue(unique_regimes.issubset(valid_regimes))
    
    def test_volatility_regime_detection(self):
        """Volatility rejim aniqlash"""
        regimes = self.detector.detect_volatility_regime(self.sample_data, window=20)
        
        self.assertIsInstance(regimes, pd.Series)
        self.assertTrue(len(regimes) > 0)
        
        # Check for valid volatility regime values
        valid_regimes = {'high_volatility', 'normal_volatility', 'low_volatility'}
        unique_regimes = set(regimes.dropna().unique())
        self.assertTrue(unique_regimes.issubset(valid_regimes))
    
    def test_liquidity_regime_detection(self):
        """Liquidity rejim aniqlash"""
        regimes = self.detector.detect_liquidity_regime(self.sample_data, window=20)
        
        self.assertIsInstance(regimes, pd.Series)
        
        # Check for valid liquidity regime values
        valid_regimes = {'high_liquidity', 'normal_liquidity', 'low_liquidity'}
        unique_regimes = set(regimes.dropna().unique())
        self.assertTrue(unique_regimes.issubset(valid_regimes))
    
    def test_regime_transitions_analysis(self):
        """Rejim o'tish tahlili"""
        transitions = self.detector.analyze_regime_transitions(self.sample_data)
        
        self.assertIn('trend_transitions', transitions)
        self.assertIn('volatility_transitions', transitions)
        self.assertIn('combined_regime_changes', transitions)
        
        self.assertIsInstance(transitions['trend_transitions'], list)
        self.assertIsInstance(transitions['volatility_transitions'], list)


class TestAdaptiveStrategyManager(unittest.TestCase):
    """Adaptive Strategy Manager testlari"""
    
    def setUp(self):
        self.manager = AdaptiveStrategyManager()
    
    def test_strategy_selection(self):
        """Strategiya tanlash"""
        result = self.manager.select_optimal_strategy(
            market_regime='trending',
            liquidity_level='high_liquidity',
            volatility_level='high_volatility'
        )
        
        self.assertIn('selected_strategy', result)
        self.assertIn('score', result)
        self.assertIn('configuration', result)
        self.assertIn('alternative_strategies', result)
        
        self.assertIsInstance(result['selected_strategy'], str)
        self.assertIsInstance(result['score'], float)
        self.assertIsInstance(result['alternative_strategies'], list)
    
    def test_strategy_adaptation(self):
        """Strategiya moslashtirish"""
        performance_metrics = {
            'win_rate': 0.45,
            'max_drawdown_pct': 18.5
        }
        
        adapted_config = self.manager.adapt_strategy_parameters(
            'trend_following', performance_metrics
        )
        
        self.assertIn('position_sizing', adapted_config)
        self.assertIn('stop_loss_pct', adapted_config)
        self.assertIn('take_profit_pct', adapted_config)
        
        # Performance-based adjustments
        self.assertLess(adapted_config['position_sizing'], 1.2)  # Should be reduced
        self.assertGreater(adapted_config['stop_loss_pct'], 0.03)  # Should be increased
    
    def test_strategy_switching_conditions(self):
        """Strategiya o'zgartirish shartlari"""
        # Poor performance
        should_switch, reason = self.manager.switch_strategy_conditions(
            current_performance={'recent_return_pct': -6.0},
            market_conditions={}
        )
        self.assertTrue(should_switch)
        self.assertEqual(reason, 'poor_performance')
        
        # No change needed
        should_switch, reason = self.manager.switch_strategy_conditions(
            current_performance={'recent_return_pct': 2.0},
            market_conditions={'regime_changed': False, 'volatility_spike': False}
        )
        self.assertFalse(should_switch)
        self.assertEqual(reason, 'no_change_needed')


class TestIntegration(unittest.TestCase):
    """Tizim integratsiya testlari"""
    
    def setUp(self):
        # Initialize all components
        self.price_impact_model = PriceImpactModel()
        self.liquidity_analyzer = LiquidityAnalyzer()
        self.session_manager = ForexSessionManager()
        self.metal_analyzer = MetalMarketAnalyzer()
        self.regime_detector = MarketRegimeDetector()
        self.strategy_manager = AdaptiveStrategyManager()
        
        # Generate sample data
        self.sample_data = self._generate_comprehensive_data()
    
    def _generate_comprehensive_data(self):
        """Comprehensive sample data"""
        dates = pd.date_range('2023-01-01', periods=1000, freq='1H')
        data = pd.DataFrame({
            'open': 1.1000 + np.cumsum(np.random.normal(0, 0.001, 1000)),
            'high': 1.1050 + np.cumsum(np.random.normal(0, 0.001, 1000)),
            'low': 1.0950 + np.cumsum(np.random.normal(0, 0.001, 1000)),
            'close': 1.1000 + np.cumsum(np.random.normal(0, 0.001, 1000)),
            'volume': np.random.lognormal(8, 1, 1000)
        }, index=dates)
        
        # Ensure high > low and close between high and low
        data['high'] = np.maximum(data['high'], data[['open', 'close']].max(axis=1))
        data['low'] = np.minimum(data['low'], data[['open', 'close']].min(axis=1))
        
        return data
    
    def test_complete_workflow(self):
        """To'liq ish jarayoni testi"""
        # 1. Market regime detection
        regimes = self.regime_detector.detect_trending_ranging_regime(self.sample_data)
        current_regime = regimes.iloc[-1]
        
        # 2. Liquidity analysis
        liquidity_data = self.liquidity_analyzer.analyze_liquidity_depth(self.sample_data)
        current_liquidity = liquidity_data['liquidity_regime'].iloc[-1]
        
        # 3. Session analysis
        current_session = self.session_manager.get_current_session()
        
        # 4. Strategy selection
        strategy_result = self.strategy_manager.select_optimal_strategy(
            market_regime=current_regime,
            liquidity_level=current_liquidity,
            volatility_level='normal_volatility'
        )
        
        # 5. Price impact analysis
        impact = self.price_impact_model.calculate_total_impact(
            volume=100000,
            avg_volume=5000000,
            volatility=0.02,
            time_of_day=14,
            order_book_depth=10000000,
            spread=0.0015
        )
        
        # Verification
        self.assertIn(current_regime, ['trending', 'ranging'])
        self.assertIn(current_liquidity, ['excellent', 'good', 'fair', 'poor', 'very_poor'])
        self.assertIsNotNone(current_session.name)
        self.assertIn('selected_strategy', strategy_result)
        self.assertIn('total_impact', impact)
        
        # Integration assertions
        self.assertGreaterEqual(strategy_result['score'], 0)
        self.assertGreaterEqual(impact['total_impact'], 0)
    
    def test_metal_market_integration(self):
        """Metal bozor integratsiya testi"""
        # Generate metal-like data (gold)
        metal_data = self.sample_data.copy()
        metal_data = metal_data * 1800  # Scale to gold prices
        
        # Metal market analysis
        metal_report = self.metal_analyzer.create_metal_market_report('XAUUSD', metal_data)
        
        self.assertIn('symbol', metal_report)
        self.assertIn('market_characteristics', metal_report)
        self.assertEqual(metal_report['symbol'], 'XAUUSD')
        
        # Check reasonable volatility for gold
        if metal_report['market_characteristics']['trading_days_analyzed'] > 0:
            self.assertGreater(metal_report['market_characteristics']['volatility_pct'], 0)
    
    def test_real_time_simulation(self):
        """Real vaqt simulatsiyasi"""
        # Simulate real-time trading decisions
        decisions = []
        
        for i in range(min(50, len(self.sample_data))):  # Test first 50 periods
            current_data = self.sample_data.iloc[:i+1]
            
            if len(current_data) < 20:  # Need minimum data
                continue
            
            # Market analysis
            regime = self.regime_detector.detect_trending_ranging_regime(current_data).iloc[-1]
            liquidity = self.liquidity_analyzer.analyze_liquidity_depth(current_data)
            current_liquidity = liquidity['liquidity_regime'].iloc[-1]
            
            # Strategy decision
            strategy = self.strategy_manager.select_optimal_strategy(
                market_regime=regime,
                liquidity_level=current_liquidity,
                volatility_level='normal_volatility'
            )
            
            # Price impact assessment
            impact = self.price_impact_model.calculate_total_impact(
                volume=50000,
                avg_volume=current_data['volume'].mean(),
                volatility=0.02,
                time_of_day=current_data.index[-1].hour,
                order_book_depth=5000000,
                spread=0.0015
            )
            
            decision = {
                'timestamp': current_data.index[-1],
                'regime': regime,
                'liquidity': current_liquidity,
                'strategy': strategy['selected_strategy'],
                'impact': impact['total_impact']
            }
            decisions.append(decision)
        
        # Verify decisions were made
        self.assertGreater(len(decisions), 10)
        
        # Check decision quality
        for decision in decisions[:5]:  # Check first few decisions
            self.assertIn('regime', decision)
            self.assertIn('liquidity', decision)
            self.assertIn('strategy', decision)
            self.assertIn('impact', decision)
            self.assertGreaterEqual(decision['impact'], 0)


def run_performance_benchmark():
    """Performance benchmark test"""
    print("\n=== Performance Benchmark ===")
    
    # Initialize components
    model = PriceImpactModel()
    analyzer = LiquidityAnalyzer()
    session_mgr = ForexSessionManager()
    
    # Generate large dataset
    large_data = pd.DataFrame({
        'open': 1.1000 + np.random.normal(0, 0.01, 10000),
        'high': 1.1050 + np.random.normal(0, 0.01, 10000),
        'low': 1.0950 + np.random.normal(0, 0.01, 10000),
        'close': 1.1000 + np.random.normal(0, 0.01, 10000),
        'volume': np.random.lognormal(8, 1, 10000)
    })
    
    # Benchmark price impact calculation
    start_time = datetime.now()
    for _ in range(100):
        model.calculate_total_impact(
            volume=100000,
            avg_volume=1000000,
            volatility=0.02,
            time_of_day=14,
            order_book_depth=10000000,
            spread=0.0015
        )
    price_impact_time = (datetime.now() - start_time).total_seconds()
    
    # Benchmark liquidity analysis
    start_time = datetime.now()
    analyzer.analyze_liquidity_depth(large_data)
    liquidity_time = (datetime.now() - start_time).total_seconds()
    
    # Benchmark session management
    start_time = datetime.now()
    for _ in range(100):
        session_mgr.get_current_session()
    session_time = (datetime.now() - start_time).total_seconds()
    
    print(f"Price Impact (100 calculations): {price_impact_time:.4f}s")
    print(f"Liquidity Analysis (10K records): {liquidity_time:.4f}s")
    print(f"Session Management (100 calls): {session_time:.4f}s")
    
    return {
        'price_impact_per_calculation': price_impact_time / 100,
        'liquidity_analysis_per_record': liquidity_time / 10000,
        'session_management_per_call': session_time / 100
    }


if __name__ == '__main__':
    # Run all tests
    print("Market Analysis System Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPriceImpactModel,
        TestLiquidityAnalyzer,
        TestForexSessionManager,
        TestMetalMarketAnalyzer,
        TestMarketRegimeDetector,
        TestAdaptiveStrategyManager,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run performance benchmark
    performance_results = run_performance_benchmark()
    
    # Summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    print(f"\n=== Performance Summary ===")
    for metric, value in performance_results.items():
        print(f"{metric}: {value:.6f}s")
    
    if result.failures or result.errors:
        print(f"\nSome tests failed. Please review the issues above.")
        exit(1)
    else:
        print(f"\nAll tests passed! System is ready for deployment.")
        exit(0)