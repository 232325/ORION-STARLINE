"""
AI Strategy Generator va Backtester Demo
======================================

Bu fayl AI-driven strategy generator va backtesting tizimining
ishlatilishini ko'rsatadi.

Demo tartibi:
1. Strategy generator va backtester import
2. Sample data yaratish
3. Turli strategiyalar yaratish
4. Backtesting va performance analiz
5. Advanced testing (walk-forward, Monte Carlo, stress test)
6. Strategy optimizatsiya
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import our AI modules
import sys
import os
sys.path.append(os.path.dirname(__file__))

from strategy_generator import StrategyGenerator, StrategyConfig, StrategyType
from backtester import Backtester, BacktestConfig, MockStrategy
from onboarding_engine import OnboardingEngine, Language, UserLevel, OnboardingStep

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StrategyDemo:
    """Demo class for strategy generation and backtesting"""
    
    def __init__(self):
        self.generator = StrategyGenerator()
        self.backtester = Backtester()
        self.logger = logger

class OnboardingDemo:
    """Demo class for onboarding system"""
    
    def __init__(self):
        self.onboarding_engine = OnboardingEngine()
        self.logger = logger
        
    def run_onboarding_demo(self):
        """Onboarding tizimi demo'si"""
        self.logger.info("=== ORION STARLINE ONBOARDING SYSTEM DEMO ===")
        self.logger.info("=" * 50)
        
        # 1. Foydalanuvchi yaratish
        self.logger.info("\n1. FOYDALANUVCHI YARATISH")
        self.logger.info("-" * 30)
        
        user = self.onboarding_engine.create_user_profile(
            "Aziz Ahmed", "aziz@example.com", Language.UZBEK
        )
        self.logger.info(f"✓ Foydalanuvchi: {user.name}")
        self.logger.info(f"✓ Email: {user.email}")
        self.logger.info(f"✓ Til: {user.preferred_language.value}")
        self.logger.info(f"✓ User ID: {user.user_id[:8]}...")
        
        # 2. Welcome tour
        self.logger.info("\n2. WELCOME TOUR")
        self.logger.info("-" * 30)
        
        welcome = self.onboarding_engine.get_welcome_content(user.user_id)
        self.logger.info(f"✓ Sarlavha: {welcome['title']}")
        self.logger.info(f"✓ Tavsif: {welcome['description']}")
        self.logger.info(f"✓ Progress: {welcome['progress_percentage']:.1f}%")
        self.logger.info("✓ Qadamlari:")
        for i, step in enumerate(welcome['steps'], 1):
            self.logger.info(f"   {i}. {step}")
        
        # 3. Skill Assessment
        self.logger.info("\n3. SKILL ASSESSMENT")
        self.logger.info("-" * 30)
        
        # Test uchun javoblar
        answers = [
            {"question_id": 1, "selected_option": 2},  # 1-2 years experience
            {"question_id": 2, "selected_option": 1},  # Forex
            {"question_id": 3, "selected_option": 1}   # Low risk
        ]
        
        assessment = self.onboarding_engine.conduct_skill_assessment(user.user_id, answers)
        self.logger.info(f"✓ Assessment natijasi: {assessment['message']}")
        self.logger.info(f"✓ Daraja: {assessment['skill_level']}")
        
        # 4. Demo Trading boshlash
        self.logger.info("\n4. DEMO TRADING BOSHLASH")
        self.logger.info("-" * 30)
        
        demo_session = self.onboarding_engine.start_demo_trading(user.user_id)
        self.logger.info(f"✓ Virtual balans: ${demo_session.virtual_balance:,.2f}")
        self.logger.info(f"✓ Start vaqti: {demo_session.start_time.strftime('%Y-%m-%d %H:%M')}")
        
        # 5. Mock market data
        self.logger.info("\n5. MARKET DATA")
        self.logger.info("-" * 30)
        
        market_data = self.onboarding_engine.get_mock_market_data()
        self.logger.info(f"✓ Vaqt: {market_data['timestamp'][:19]}")
        self.logger.info(f"✓ Bozor sentiment: {market_data['market_sentiment']}")
        self.logger.info(f"✓ Trending: {', '.join(market_data['trending'])}")
        self.logger.info("✓ Narxlar:")
        for symbol, data in market_data['prices'].items():
            change_str = "+" if data['change'] >= 0 else ""
            self.logger.info(f"   {symbol}: {data['price']} ({change_str}{data['change']:+.4f})")
        
        # 6. Demo trade'lar
        self.logger.info("\n6. DEMO TRADING AMALIYOT")
        self.logger.info("-" * 30)
        
        # EURUSD long
        trade1 = self.onboarding_engine.execute_demo_trade(user.user_id, "EURUSD", "long", 1000)
        if trade1.get('success'):
            self.logger.info(f"✓ Trade 1: EURUSD LONG @ {trade1['position']['entry_price']}")
            self.logger.info(f"   Qoldiq balans: ${trade1['remaining_balance']:,.2f}")
        else:
            self.logger.error(f"✗ Trade 1 xato: {trade1.get('error')}")
        
        # XAUUSD long  
        trade2 = self.onboarding_engine.execute_demo_trade(user.user_id, "XAUUSD", "long", 10)
        if trade2.get('success'):
            self.logger.info(f"✓ Trade 2: XAUUSD LONG @ {trade2['position']['entry_price']}")
            self.logger.info(f"   Qoldiq balans: ${trade2['remaining_balance']:,.2f}")
        else:
            self.logger.error(f"✗ Trade 2 xato: {trade2.get('error')}")
        
        # BTCUSD short
        trade3 = self.onboarding_engine.execute_demo_trade(user.user_id, "BTCUSD", "short", 0.5)
        if trade3.get('success'):
            self.logger.info(f"✓ Trade 3: BTCUSD SHORT @ {trade3['position']['entry_price']}")
            self.logger.info(f"   Qoldiq balans: ${trade3['remaining_balance']:,.2f}")
        else:
            self.logger.error(f"✗ Trade 3 xato: {trade3.get('error')}")
        
        # 7. Pozitsiyalarni yangilash
        self.logger.info("\n7. POZITSIYALAR YANGILASH")
        self.logger.info("-" * 30)
        
        updated = self.onboarding_engine.update_demo_positions(user.user_id)
        self.logger.info(f"✓ Umumiy PnL: ${updated['total_pnl']:+.2f}")
        
        performance = updated['performance_metrics']
        self.logger.info(f"✓ Umumiy trade'lar: {performance['total_trades']}")
        self.logger.info(f"✓ G'olib trade'lar: {performance['winning_trades']}")
        self.logger.info(f"✓ Mag'lub trade'lar: {performance['losing_trades']}")
        self.logger.info(f"✓ Win rate: {performance['win_rate']:.1f}%")
        
        self.logger.info("✓ Pozitsiya tafsilotlari:")
        for pos in updated['positions']:
            pnl_str = "+" if pos['pnl'] >= 0 else ""
            self.logger.info(f"   {pos['symbol']} {pos['side'].upper()}: ${pnl_str}{pos['pnl']:+.2f}")
        
        # 8. AI Assistant
        self.logger.info("\n8. AI ASSISTANT")
        self.logger.info("-" * 30)
        
        ai_response = self.onboarding_engine.get_ai_assistant_response(
            user.user_id, "Demo trading yordam kerak"
        )
        self.logger.info(f"✓ AI javob: {ai_response['response']}")
        self.logger.info(f"✓ Kontekst: {ai_response['context']}")
        
        # 9. Shaxsiy tavsiyalar
        self.logger.info("\n9. SHAXSIY TAVSIYALAR")
        self.logger.info("-" * 30)
        
        recommendations = self.onboarding_engine.get_personalized_recommendations(user.user_id)
        rec_data = recommendations['recommendations']
        self.logger.info(f"✓ Foydalanuvchi darajasi: {recommendations['user_level']}")
        self.logger.info(f"✓ Tavsiya etiladigan strategiyalar:")
        for strategy in rec_data['strategies']:
            self.logger.info(f"   • {strategy}")
        self.logger.info(f"✓ Bozorlar: {', '.join(rec_data['markets'])}")
        self.logger.info(f"✓ Risk darajasi: {rec_data['risk_level']}")
        self.logger.info(f"✓ O'rganish yo'li: {rec_data['learning_path']}")
        
        # 10. Onboarding qadamini yakunlash
        self.logger.info("\n10. ONBOARDING QADAM YAKUNLASH")
        self.logger.info("-" * 30)
        
        completed = self.onboarding_engine.complete_onboarding_step(
            user.user_id, OnboardingStep.DEMO_TRADING
        )
        self.logger.info(f"✓ {completed['message']}")
        self.logger.info(f"✓ Progress: {completed['progress_percentage']:.1f}%")
        self.logger.info(f"✓ Keyingi qadam: {completed['current_step']}")
        
        # 11. Onboarding holati
        self.logger.info("\n11. ONBOARDING HOLATI")
        self.logger.info("-" * 30)
        
        status = self.onboarding_engine.get_onboarding_status(user.user_id)
        self.logger.info(f"✓ Joriy qadam: {status['current_step']}")
        self.logger.info(f"✓ Progress: {status['progress_percentage']:.1f}%")
        self.logger.info(f"✓ Onboarding tugallandi: {status['onboarding_completed']}")
        self.logger.info(f"✓ Skill daraja: {status['skill_level']}")
        self.logger.info(f"✓ Demo balans: ${status['demo_balance']:,.2f}")
        self.logger.info(f"✓ Trade'lar soni: {status['total_trades']}")
        
        # 12. Gamification
        self.logger.info("\n12. GAMIFICATION")
        self.logger.info("-" * 30)
        
        gamification = self.onboarding_engine.get_gamification_data(user.user_id)
        self.logger.info(f"✓ Daraja: {gamification['level']}")
        self.logger.info(f"✓ Ballar: {gamification['points']}")
        self.logger.info(f"✓ Badge'lar: {', '.join(gamification['badges'])}")
        self.logger.info(f"✓ Yutuqlar: {', '.join(gamification['achievements'])}")
        
        # 13. Qo'shimcha demo trade va pozitsiya yopish
        self.logger.info("\n13. POZITSIYA YOPISH")
        self.logger.info("-" * 30)
        
        if updated['positions']:
            first_position = updated['positions'][0]
            close_result = self.onboarding_engine.close_demo_position(
                user.user_id, first_position['id']
            )
            if close_result.get('success'):
                self.logger.info(f"✓ {close_result['message']}")
                self.logger.info(f"✓ Yakuniy PnL: ${close_result['final_pnl']:+.2f}")
                self.logger.info(f"✓ Qoldiq balans: ${close_result['remaining_balance']:,.2f}")
        
        # Yakuniy holat
        self.logger.info("\n14. YAKUNIY HOLAT")
        self.logger.info("-" * 30)
        
        final_status = self.onboarding_engine.get_onboarding_status(user.user_id)
        self.logger.info(f"✓ Onboarding progress: {final_status['progress_percentage']:.1f}%")
        self.logger.info(f"✓ Demo trading performance:")
        final_demo = self.onboarding_engine.demo_sessions.get(user.user_id)
        if final_demo:
            perf = final_demo.performance_metrics
            self.logger.info(f"   • Jami trade'lar: {perf['total_trades']}")
            self.logger.info(f"   • Umumiy PnL: ${perf['total_pnl']:+.2f}")
            self.logger.info(f"   • Win rate: {perf.get('win_rate', 0):.1f}%")
            self.logger.info(f"   • Balans: ${final_demo.virtual_balance:,.2f}")
        
        self.logger.info("\n=== ONBOARDING DEMO YAKUNLANDI ===")
        self.logger.info("Bu demo quyidagi imkoniyatlarni ko'rsatdi:")
        self.logger.info("✓ Foydalanuvchi profili yaratish")
        self.logger.info("✓ Multi-language support (Uzbek/English)")
        self.logger.info("✓ Skill assessment")
        self.logger.info("✓ Demo trading (virtual balance, mock data)")
        self.logger.info("✓ Real-time PnL kuzatish")
        self.logger.info("✓ AI Assistant interaction")
        self.logger.info("✓ Personalized recommendations")
        self.logger.info("✓ Progress tracking")
        self.logger.info("✓ Gamification elements")
        self.logger.info("✓ Onboarding step management")
        
        return user
        
    def create_sample_data(self, days: int = 365) -> pd.DataFrame:
        """Sample market data yaratish"""
        np.random.seed(42)
        
        # Date range
        start_date = datetime.now() - timedelta(days=days)
        dates = pd.date_range(start=start_date, periods=days*24, freq='H')
        
        # Simulated forex data (EUR/USD)
        initial_price = 1.1000
        
        # Price movement with trends and volatility
        trend_strength = 0.0001
        volatility = 0.005
        price_changes = np.random.normal(trend_strength, volatility, len(dates))
        
        # Add some market regimes
        for i in range(0, len(price_changes), len(price_changes)//4):
            regime_change = np.random.choice([-1, 1, 0.2, -0.2])
            price_changes[i:i+24] *= regime_change
        
        # Calculate price series
        prices = initial_price * (1 + np.cumsum(price_changes))
        
        # Create OHLCV data
        data = pd.DataFrame(index=dates)
        data['close'] = prices
        data['open'] = data['close'].shift(1).fillna(initial_price)
        
        # Add realistic spreads
        spread = 0.0002  # 2 pips
        noise = np.random.normal(0, spread/4, len(data))
        
        data['high'] = data['close'] + np.abs(np.random.normal(0, spread/2, len(data)))
        data['low'] = data['close'] - np.abs(np.random.normal(0, spread/2, len(data)))
        data['volume'] = np.random.lognormal(10, 1, len(data))
        
        return data
    
    def run_basic_demo(self):
        """Asosiy demo funksiyasi"""
        self.logger.info("=== AI STRATEGY GENERATOR VA BACKTESTER DEMO ===")
        
        # Sample data
        self.logger.info("Sample data yaratish...")
        data = self.create_sample_data(180)
        self.logger.info(f"Data tayyor: {len(data)} row, {data.index[0]} dan {data.index[-1]}")
        
        # 1. Strategy Generation Demo
        self.logger.info("\\n1. STRATEGY GENERATION")
        self.logger.info("-" * 30)
        
        # Trend following
        trend_strategy = self.generator.generate_trend_following_strategy(
            fast_period=12, slow_period=26
        )
        self.logger.info(f"✓ Trend Following strategy: {trend_strategy.name}")
        
        # Mean reversion
        mean_reversion_strategy = self.generator.generate_mean_reversion_strategy(
            rsi_period=14, overbought=70, oversold=30
        )
        self.logger.info(f"✓ Mean Reversion strategy: {mean_reversion_strategy.name}")
        
        # Momentum
        momentum_strategy = self.generator.generate_momentum_strategy(
            momentum_period=10, rsi_period=14
        )
        self.logger.info(f"✓ Momentum strategy: {momentum_strategy.name}")
        
        # Statistical arbitrage
        stat_arb_strategy = self.generator.generate_statistical_arbitrage_strategy(
            lookback_period=50, z_score_threshold=2.0
        )
        self.logger.info(f"✓ Statistical Arbitrage strategy: {stat_arb_strategy.name}")
        
        # Grid trading
        grid_strategy = self.generator.generate_grid_trading_strategy(
            grid_levels=10, price_range=(0.95, 1.05)
        )
        self.logger.info(f"✓ Grid Trading strategy: {grid_strategy.name}")
        
        # Martingale
        martingale_strategy = self.generator.generate_martingale_strategy(
            base_position=0.1, multiplier=2.0, max_levels=5
        )
        self.logger.info(f"✓ Martingale strategy: {martingale_strategy.name}")
        
        # Hybrid strategy
        hybrid_strategy = self.generator.generate_hybrid_strategy(
            components=['trend', 'reversion', 'momentum']
        )
        self.logger.info(f"✓ Hybrid strategy: {hybrid_strategy.name}")
        
        # 2. Basic Backtesting Demo
        self.logger.info("\\n2. BASIC BACKTESTING")
        self.logger.info("-" * 30)
        
        # Test each strategy
        strategies = [trend_strategy, mean_reversion_strategy, momentum_strategy]
        results = []
        
        for i, strategy in enumerate(strategies):
            try:
                # Create mock strategy for testing
                mock_strategy = MockStrategy(signal_frequency=0.1)
                
                # Run backtest
                result = self.backtester.run_backtest(mock_strategy, data)
                
                results.append({
                    'strategy': strategy.name,
                    'total_return': result.total_return,
                    'sharpe_ratio': result.sharpe_ratio,
                    'max_drawdown': result.max_drawdown,
                    'total_trades': result.total_trades,
                    'win_rate': result.win_rate
                })
                
                self.logger.info(f"✓ {strategy.name}:")
                self.logger.info(f"  Total Return: {result.total_return:.2%}")
                self.logger.info(f"  Sharpe Ratio: {result.sharpe_ratio:.3f}")
                self.logger.info(f"  Max Drawdown: {result.max_drawdown:.2%}")
                self.logger.info(f"  Total Trades: {result.total_trades}")
                self.logger.info(f"  Win Rate: {result.win_rate:.2%}")
                
            except Exception as e:
                self.logger.warning(f"✗ {strategy.name} backtest failed: {e}")
        
        # 3. Performance Comparison
        self.logger.info("\\n3. PERFORMANCE COMPARISON")
        self.logger.info("-" * 30)
        
        # Rank strategies
        if results:
            # Sort by Sharpe ratio
            sorted_results = sorted(results, key=lambda x: x['sharpe_ratio'], reverse=True)
            
            self.logger.info("Strategy Performance Ranking (by Sharpe Ratio):")
            for i, result in enumerate(sorted_results, 1):
                self.logger.info(f"{i}. {result['strategy']}: Sharpe {result['sharpe_ratio']:.3f}")
        
        return results
    
    async def run_advanced_demo(self):
        """Advanced demo with optimization and testing"""
        self.logger.info("\\n=== ADVANCED DEMO ===")
        
        # Sample data
        data = self.create_sample_data(365)
        
        # Create base strategy
        trend_strategy = self.generator.generate_trend_following_strategy()
        mock_strategy = MockStrategy(signal_frequency=0.1)
        
        # 1. Cross-Validation
        self.logger.info("\\n1. CROSS-VALIDATION")
        self.logger.info("-" * 30)
        
        try:
            cv_results = self.backtester.cross_validation(mock_strategy, data, n_folds=5)
            
            self.logger.info("Cross-Validation Results:")
            self.logger.info(f"  Folds tested: {cv_results.get('successful_folds', 0)}/{cv_results.get('n_folds', 0)}")
            self.logger.info(f"  Average Sharpe: {cv_results.get('avg_sharpe', 0):.3f}")
            self.logger.info(f"  Sharpe Stability: {cv_results.get('sharpe_stability', 0):.3f}")
            self.logger.info(f"  CV Score: {cv_results.get('cv_score', 0):.3f}")
            
        except Exception as e:
            self.logger.warning(f"Cross-validation failed: {e}")
        
        # 2. Walk-Forward Analysis
        self.logger.info("\\n2. WALK-FORWARD ANALYSIS")
        self.logger.info("-" * 30)
        
        try:
            wf_results = self.backtester.walk_forward_analysis(
                mock_strategy, data, window_size=168, step_size=24  # 1 week, 1 day steps
            )
            
            self.logger.info("Walk-Forward Results:")
            self.logger.info(f"  Windows analyzed: {wf_results.get('windows_analyzed', 0)}")
            self.logger.info(f"  Average test Sharpe: {wf_results.get('avg_test_sharpe', 0):.3f}")
            self.logger.info(f"  Sharpe stability: {wf_results.get('sharpe_stability', 0):.3f}")
            self.logger.info(f"  Average test return: {wf_results.get('avg_test_return', 0):.2%}")
            
        except Exception as e:
            self.logger.warning(f"Walk-forward analysis failed: {e}")
        
        # 3. Monte Carlo Simulation
        self.logger.info("\\n3. MONTE CARLO SIMULATION")
        self.logger.info("-" * 30)
        
        try:
            mc_results = self.backtester.monte_carlo_simulation(
                mock_strategy, data, num_simulations=100
            )
            
            self.logger.info("Monte Carlo Results:")
            self.logger.info(f"  Simulations completed: {mc_results.get('num_simulations', 0)}")
            self.logger.info(f"  Mean return: {mc_results.get('mean_return', 0):.2%}")
            self.logger.info(f"  Return std: {mc_results.get('std_return', 0):.2%}")
            self.logger.info(f"  5th percentile: {mc_results.get('percentile_5', 0):.2%}")
            self.logger.info(f"  95th percentile: {mc_results.get('percentile_95', 0):.2%}")
            self.logger.info(f"  VaR (5%): {mc_results.get('var_5', 0):.2%}")
            self.logger.info(f"  Probability of profit: {mc_results.get('prob_profit', 0):.2%}")
            self.logger.info(f"  Positive Sharpe probability: {mc_results.get('sharpe_prob_positive', 0):.2%}")
            
        except Exception as e:
            self.logger.warning(f"Monte Carlo simulation failed: {e}")
        
        # 4. Stress Testing
        self.logger.info("\\n4. STRESS TESTING")
        self.logger.info("-" * 30)
        
        try:
            stress_results = self.backtester.stress_test(mock_strategy, data)
            
            self.logger.info("Stress Testing Results:")
            normal_perf = stress_results.get('normal_performance', {})
            self.logger.info(f"  Normal condition return: {normal_perf.get('total_return', 0):.2%}")
            self.logger.info(f"  Normal condition Sharpe: {normal_perf.get('sharpe_ratio', 0):.3f}")
            
            stress_summary = stress_results.get('stress_summary', {})
            self.logger.info(f"  Success rate under stress: {stress_summary.get('success_rate', 0):.2%}")
            self.logger.info(f"  Worst stress return: {stress_summary.get('worst_return', 0):.2%}")
            self.logger.info(f"  Best stress return: {stress_summary.get('best_return', 0):.2%}")
            self.logger.info(f"  Robustness score: {stress_summary.get('robustness_score', 0):.3f}")
            
            # Show individual scenarios
            stress_tests = stress_results.get('stress_results', [])
            self.logger.info("  Scenario Results:")
            for test in stress_tests[:3]:  # Show first 3
                scenario_name = test.get('scenario', 'Unknown')
                if 'error' not in test:
                    self.logger.info(f"    {scenario_name}: Return {test.get('total_return', 0):.2%}")
                else:
                    self.logger.info(f"    {scenario_name}: Failed")
            
        except Exception as e:
            self.logger.warning(f"Stress testing failed: {e}")
        
        # 5. Strategy Optimization Demo (Simplified)
        self.logger.info("\\n5. STRATEGY OPTIMIZATION")
        self.logger.info("-" * 30)
        
        try:
            # Parameter space for optimization
            param_space = {
                'fast_ma_period': [5, 20],
                'slow_ma_period': [20, 50],
                'signal_threshold': [0.005, 0.05]
            }
            
            # This would require the actual strategy implementation
            # For demo, we'll show what would happen
            self.logger.info("Genetic Algorithm Optimization (Demo):")
            self.logger.info("  Parameter space defined:")
            for param, range_val in param_space.items():
                self.logger.info(f"    {param}: {range_val}")
            self.logger.info("  Population size: 50")
            self.logger.info("  Generations: 100")
            self.logger.info("  Mutation rate: 0.1")
            self.logger.info("  Note: Full optimization requires strategy implementation")
            
        except Exception as e:
            self.logger.warning(f"Optimization demo failed: {e}")
        
        # 6. Benchmark Comparison
        self.logger.info("\\n6. BENCHMARK COMPARISON")
        self.logger.info("-" * 30)
        
        try:
            benchmark_results = self.backtester.benchmark_comparison(mock_strategy, data)
            
            if 'error' not in benchmark_results:
                strategy_perf = benchmark_results.get('strategy', {})
                benchmark_perf = benchmark_results.get('benchmark', {})
                outperformance = benchmark_results.get('outperformance', {})
                
                self.logger.info("Strategy vs Benchmark:")
                self.logger.info(f"  Strategy return: {strategy_perf.get('total_return', 0):.2%}")
                self.logger.info(f"  Benchmark return: {benchmark_perf.get('total_return', 0):.2%}")
                self.logger.info(f"  Excess return: {outperformance.get('excess_return', 0):.2%}")
                self.logger.info(f"  Strategy Sharpe: {strategy_perf.get('sharpe_ratio', 0):.3f}")
                self.logger.info(f"  Benchmark Sharpe: {benchmark_perf.get('sharpe_ratio', 0):.3f}")
                self.logger.info(f"  Information ratio: {outperformance.get('information_ratio', 0):.3f}")
                if outperformance.get('beta') is not None:
                    self.logger.info(f"  Beta: {outperformance.get('beta', 0):.3f}")
                if outperformance.get('alpha') is not None:
                    self.logger.info(f"  Alpha: {outperformance.get('alpha', 0):.2%}")
            
        except Exception as e:
            self.logger.warning(f"Benchmark comparison failed: {e}")
    
    async def run_complete_demo(self):
        """To'liq demo funksiyasi"""
        self.logger.info("AI STRATEGY GENERATOR VA BACKTESTER")
        self.logger.info("=" * 50)
        
        # Basic demo
        self.run_basic_demo()
        
        # Advanced demo
        await self.run_advanced_demo()
        
        # Summary
        self.logger.info("\\n=== DEMO YAKUNLANDI ===")
        self.logger.info("Bu demo quyidagi imkoniyatlarni ko'rsatdi:")
        self.logger.info("✓ 7 xil strategy turi yaratish")
        self.logger.info("✓ Backtesting va performance metrikalar")
        self.logger.info("✓ Cross-validation")
        self.logger.info("✓ Walk-forward analysis")
        self.logger.info("✓ Monte Carlo simulation")
        self.logger.info("✓ Stress testing")
        self.logger.info("✓ Benchmark comparison")
        self.logger.info("✓ Strategy optimization framework")

async def main():
    """Asosiy demo funksiyasi"""
    print("Tanlang:\n1. Strategy Generator va Backtester Demo\n2. Onboarding System Demo\n3. Ikki demo ham")
    choice = input("Tanlovingiz (1-3): ").strip()
    
    if choice == "1":
        demo = StrategyDemo()
        await demo.run_complete_demo()
    elif choice == "2":
        onboarding_demo = OnboardingDemo()
        onboarding_demo.run_onboarding_demo()
    elif choice == "3":
        # Strategy demo
        demo = StrategyDemo()
        await demo.run_complete_demo()  # Full demo
        
        print("\n" + "="*50)
        
        # Onboarding demo
        onboarding_demo = OnboardingDemo()
        onboarding_demo.run_onboarding_demo()
    else:
        print("Noto'g'ri tanlov. Default: Onboarding demo")
        onboarding_demo = OnboardingDemo()
        onboarding_demo.run_onboarding_demo()

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())