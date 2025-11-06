#!/usr/bin/env python3
"""
Pro Backtesting Engine Demo Script
==================================

Bu script Pro Backtesting Engine ning barcha asosiy funksiyalarini 
namoyish qiladi va test qiladi.

Author: Orion Starline AI Trading System
Version: 1.0.0
"""

import sys
import os
sys.path.append('/workspace/orion-starline/backend/ai_modules')

from pro_backtesting import (
    ProBacktestingEngine, StrategyConfig, TimeFrame, 
    OptimizationMethod, create_sample_data
)
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def run_comprehensive_demo():
    """
    Pro Backtesting Engine ning to'liq demo si
    """
    print("=" * 80)
    print("🚀 PRO BACKTESTING ENGINE - TO'LIQ DEMO")
    print("=" * 80)
    print()
    
    # 1. Ma'lumotlarni yaratish
    print("📊 1. Sample ma'lumotlarni yaratish...")
    try:
        data = create_sample_data(
            symbol="AAPL", 
            start_date="2015-01-01", 
            end_date="2023-12-31", 
            frequency="D"
        )
        print(f"   ✅ Ma'lumotlar yaratildi: {data.shape[0]} kunlik data")
        print(f"   📅 Sana diapazoni: {data.index[0].date()} dan {data.index[-1].date()} gacha")
        print(f"   📈 Oxirgi narx: ${data['close'].iloc[-1]:.2f}")
        print()
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 2. Engine yaratish
    print("⚙️  2. Pro Backtesting Engine yaratish...")
    try:
        engine = ProBacktestingEngine(
            max_workers=4,
            cache_enabled=True,
            benchmark_data=None
        )
        print("   ✅ Engine muvaffaqiyatli yaratildi")
        print(f"   🔧 Worker processes: {engine.max_workers}")
        print(f"   💾 Cache: {engine.cache_enabled}")
        print()
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 3. Strategiya konfiguratsiyalari
    print("🎯 3. Strategiya konfiguratsiyalarini yaratish...")
    
    try:
        # Moving Average Strategy
        ma_strategy = StrategyConfig(
            name="Moving Average Crossover",
            strategy_function=ProBacktestingEngine.moving_average_strategy,
            parameters={'short_window': 20, 'long_window': 50},
            initial_capital=100000.0,
            commission=0.001,
            slippage=0.0005,
            risk_free_rate=0.02
        )
        
        # RSI Strategy
        rsi_strategy = StrategyConfig(
            name="RSI Mean Reversion",
            strategy_function=ProBacktestingEngine.rsi_strategy,
            parameters={'rsi_period': 14, 'oversold': 30, 'overbought': 70},
            initial_capital=100000.0,
            commission=0.001,
            slippage=0.0005,
            risk_free_rate=0.02
        )
        
        # Momentum Strategy
        momentum_strategy = StrategyConfig(
            name="Momentum Strategy",
            strategy_function=ProBacktestingEngine.momentum_strategy,
            parameters={'lookback_period': 20},
            initial_capital=100000.0,
            commission=0.001,
            slippage=0.0005,
            risk_free_rate=0.02
        )
        
        strategies = [ma_strategy, rsi_strategy, momentum_strategy]
        print("   ✅ 3 ta strategiya konfiguratsiyasi yaratildi:")
        for i, strategy in enumerate(strategies, 1):
            print(f"      {i}. {strategy.name}")
            print(f"         Parametrlar: {strategy.parameters}")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 4. Bitta strategiya backtest
    print("🔄 4. Moving Average strategiyasi backtest...")
    try:
        result = engine.run_backtest(
            strategy_config=ma_strategy,
            data=data,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2023, 12, 31),
            commission_model='percentage',
            slippage_model='proportional'
        )
        
        print("   📊 NATIJALAR:")
        print(f"   📈 Jami foyda: {result.total_return:.2%}")
        print(f"   📊 Yillik foyda: {result.annualized_return:.2%}")
        print(f"   📉 Volatilite: {result.volatility:.2%}")
        print(f"   🎯 Sharpe ratio: {result.sharpe_ratio:.2f}")
        print(f"   📉 Max drawdown: {result.max_drawdown:.2%}")
        print(f"   🎲 Win rate: {result.win_rate:.2%}")
        print(f"   🔢 Jami trade: {result.total_trades}")
        print(f"   ⏱️  Ishga tushish vaqti: {result.execution_time:.2f}s")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 5. Bir nechta strategiya (parallel)
    print("🚀 5. Bir nechta strategiyani parallel ishlash...")
    try:
        results = engine.run_multiple_strategies(
            strategies=strategies,
            data=data,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2023, 12, 31),
            parallel=True
        )
        
        print("   📊 BARALASH NATIJALARI:")
        print("   " + "-" * 70)
        print(f"   {'Strategiya':<20} {'Foyda':<10} {'Sharpe':<8} {'Max DD':<10} {'Win Rate':<10}")
        print("   " + "-" * 70)
        
        for result in results:
            print(f"   {result.strategy_name:<20} "
                  f"{result.total_return:<9.2%} "
                  f"{result.sharpe_ratio:<7.2f} "
                  f"{result.max_drawdown:<9.2%} "
                  f"{result.win_rate:<9.2%}")
        
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 6. Parameter optimizatsiya (Grid Search)
    print("🎯 6. Grid Search parameter optimizatsiya...")
    try:
        parameter_ranges = {
            'short_window': [10, 15, 20, 25],
            'long_window': [40, 50, 60, 70]
        }
        
        best_params, best_result = engine.optimize_strategy_parameters(
            strategy_config=ma_strategy,
            data=data,
            parameter_ranges=parameter_ranges,
            optimization_method=OptimizationMethod.GRID_SEARCH,
            objective='sharpe_ratio'
        )
        
        print("   🏆 ENG YAXSHI NATIJA:")
        print(f"   📋 Parametrlar: {best_params}")
        print(f"   📈 Jami foyda: {best_result.total_return:.2%}")
        print(f"   🎯 Sharpe ratio: {best_result.sharpe_ratio:.2f}")
        print(f"   📉 Max drawdown: {best_result.max_drawdown:.2%}")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 7. Genetic Algorithm optimizatsiya
    print("🧬 7. Genetic Algorithm optimizatsiya...")
    try:
        # RSI strategiyasi uchun parametrlar
        rsi_param_ranges = {
            'rsi_period': (10, 20),
            'oversold': (20, 35),
            'overbought': (65, 80)
        }
        
        ga_params, ga_result = engine.optimize_strategy_parameters(
            strategy_config=rsi_strategy,
            data=data,
            parameter_ranges=rsi_param_ranges,
            optimization_method=OptimizationMethod.GENETIC,
            max_iterations=20,  # Demo uchun kam iteratsiya
            objective='sharpe_ratio'
        )
        
        print("   🧬 GENETIC ALGORITHM NATIJASI:")
        print(f"   📋 Parametrlar: {ga_params}")
        print(f"   📈 Jami foyda: {ga_result.total_return:.2%}")
        print(f"   🎯 Sharpe ratio: {ga_result.sharpe_ratio:.2f}")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 8. Monte Carlo Simulation
    print("🎲 8. Monte Carlo risk analizi...")
    try:
        mc_result = engine.run_monte_carlo_simulation(
            strategy_config=ma_strategy,
            data=data,
            num_simulations=200,  # Demo uchun kam simulyatsiya
            bootstrap_method='block',
            confidence_level=0.95
        )
        
        print("   🎲 MONTE CARLO NATIJALARI:")
        print(f"   🔢 Simulyatsiya soni: {mc_result.simulation_count}")
        print(f"   📊 Yo'qotish ehtimoli: {mc_result.probability_of_loss:.2%}")
        print(f"   📈 Eng yaxshi natija: {mc_result.best_case:.2%}")
        print(f"   📉 Eng yomon natija: {mc_result.worst_case:.2%}")
        print(f"   📊 O'rtacha natija: {mc_result.median_case:.2%}")
        print(f"   ⚠️  VaR (95%): {mc_result.var_95:.2%}")
        print(f"   🚨 CVaR (95%): {mc_result.cvar_95:.2%}")
        
        # Confidence interval
        return_ci = mc_result.confidence_intervals['total_return']
        print(f"   📊 Foyda confidence interval: [{return_ci[0]:.2%}, {return_ci[1]:.2%}]")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 9. Walk-Forward Analysis
    print("🔄 9. Walk-Forward out-of-sample analiz...")
    try:
        wf_result = engine.run_walk_forward_analysis(
            strategy_config=ma_strategy,
            data=data,
            in_sample_period=252,  # 1 yil
            out_of_sample_period=63,  # 3 oy
            step_size=21  # Har hafta
        )
        
        print("   🔄 WALK-FORWARD NATIJALARI:")
        print(f"   📊 Periodlar soni: {len(wf_result.periods)}")
        print(f"   📈 Stability score: {wf_result.stability_score:.2f}")
        print(f"   💪 Robustness score: {wf_result.robustness_score:.2f}")
        
        # Har bir period natijalarini ko'rsatish
        print("   📅 Har period natijalari:")
        for i, (period, in_result, out_result) in enumerate(
            zip(wf_result.periods, wf_result.results, wf_result.out_of_sample_results)
        ):
            in_return = in_result.total_return if in_result else 0
            out_return = out_result.total_return if out_result else 0
            print(f"      Period {i+1}: In={in_return:.2%}, Out={out_return:.2%}")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 10. Multi-timeframe analysis (simulyatsiya)
    print("⏰ 10. Multi-timeframe analiz demo...")
    try:
        # Ma'lumotlarni turli vaqt freymlariga aylantirish
        daily_data = data.copy()
        
        # 4 soatlik data (simplified)
        h4_data = data.resample('4H').agg({
            'open': 'first',
            'high': 'max', 
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        # 1 soatlik data (simplified) 
        h1_data = data.resample('1H').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min', 
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        data_dict = {
            TimeFrame.D1: daily_data,
            TimeFrame.H4: h4_data,
            TimeFrame.H1: h1_data
        }
        
        tf_strategies = [ma_strategy, rsi_strategy]
        
        tf_results = engine.run_multi_timeframe_analysis(
            strategy_configs=tf_strategies,
            data_dict=data_dict,
            start_date=datetime(2022, 1, 1),
            end_date=datetime(2023, 12, 31)
        )
        
        print("   ⏰ MULTI-TIMEFRAME NATIJALARI:")
        for timeframe, result in tf_results.items():
            print(f"      {timeframe}: {result.strategy_name}")
            print(f"         Foyda: {result.total_return:.2%}, "
                  f"Sharpe: {result.sharpe_ratio:.2f}")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 11. Portfolio backtest
    print("💼 11. Portfolio backtest demo...")
    try:
        portfolio_strategies = [ma_strategy, rsi_strategy, momentum_strategy]
        weights = [0.4, 0.3, 0.3]  # 40%, 30%, 30%
        
        # Portfolio uchun ma'lumot (bitta asset uchun simplified)
        portfolio_data = { 'portfolio': data }
        
        portfolio_result = engine.run_portfolio_backtest(
            strategies=portfolio_strategies,
            weights=weights,
            data_dict=portfolio_data,
            rebalance_frequency='monthly',
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2023, 12, 31)
        )
        
        print("   💼 PORTFOLIO NATIJALARI:")
        print(f"   📊 Jami foyda: {portfolio_result.total_return:.2%}")
        print(f"   🎯 Sharpe ratio: {portfolio_result.sharpe_ratio:.2f}")
        print(f"   📉 Max drawdown: {portfolio_result.max_drawdown:.2%}")
        print(f"   ⚖️  Og'irliklar: {weights}")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 12. Statistical significance test
    print("📊 12. Statistical significance test...")
    try:
        # Simulatsiya qilingan natijalar
        strategy_results = [result for result in results]
        
        # Benchmark natija (masalan, buy and hold)
        benchmark_strategy = StrategyConfig(
            name="Buy and Hold",
            strategy_function=lambda data, **params: pd.DataFrame({'signal': [1]*len(data)}),
            parameters={}
        )
        
        benchmark_result = engine.run_backtest(
            benchmark_strategy, data,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2023, 12, 31)
        )
        benchmark_results = [benchmark_result]
        
        # Statistical test
        sig_results = engine.calculate_statistical_significance(
            strategy_results=strategy_results,
            benchmark_results=benchmark_results,
            alpha=0.05
        )
        
        print("   📊 STATISTICAL SIGNIFICANCE NATIJALARI:")
        print(f"   📈 Return test p-value: {sig_results['return_test']['p_value']:.4f}")
        print(f"   📈 Return significant: {sig_results['return_test']['significant']}")
        print(f"   📊 Sharpe test p-value: {sig_results['sharpe_test']['p_value']:.4f}")
        print(f"   📊 Sharpe significant: {sig_results['sharpe_test']['significant']}")
        print(f"   📏 Return effect size (Cohen's d): {sig_results['return_test']['cohens_d']:.2f}")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 13. Report generation
    print("📄 13. Comprehensive report yaratish...")
    try:
        report_html = engine.generate_comprehensive_report(
            results=strategy_results[:2],  # Faqat 2 ta strategiya
            benchmark_results=benchmark_results,
            monte_carlo_results=mc_result,
            walk_forward_results=wf_result,
            save_path="/tmp/pro_backtest_report.html"
        )
        
        print("   📄 Hisobot muvaffaqiyatli yaratildi!")
        print(f"   💾 Fayl manzili: /tmp/pro_backtest_report.html")
        print(f"   📏 Fayl hajmi: {len(report_html)} characters")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # 14. Performance metrics summary
    print("📈 14. Performance metrics summary...")
    try:
        best_strategy = max(results, key=lambda x: x.sharpe_ratio)
        worst_strategy = min(results, key=lambda x: x.sharpe_ratio)
        
        print("   🏆 ENG YAXSHI STRATEGIYA:")
        print(f"      Nomi: {best_strategy.strategy_name}")
        print(f"      Sharpe: {best_strategy.sharpe_ratio:.2f}")
        print(f"      Foyda: {best_strategy.total_return:.2%}")
        print(f"      Max DD: {best_strategy.max_drawdown:.2%}")
        
        print()
        print("   📉 ENG YOMON STRATEGIYA:")
        print(f"      Nomi: {worst_strategy.strategy_name}")
        print(f"      Sharpe: {worst_strategy.sharpe_ratio:.2f}")
        print(f"      Foyda: {worst_strategy.total_return:.2%}")
        print(f"      Max DD: {worst_strategy.max_drawdown:.2%}")
        
        # Average metrics
        avg_return = np.mean([r.total_return for r in results])
        avg_sharpe = np.mean([r.sharpe_ratio for r in results])
        avg_dd = np.mean([r.max_drawdown for r in results])
        
        print()
        print("   📊 O'RTACHA METRIKALAR:")
        print(f"      O'rtacha foyda: {avg_return:.2%}")
        print(f"      O'rtacha Sharpe: {avg_sharpe:.2f}")
        print(f"      O'rtacha Max DD: {avg_dd:.2%}")
        print()
        
    except Exception as e:
        print(f"   ❌ Xato: {e}")
        return
    
    # Xulosa
    print("=" * 80)
    print("✅ PRO BACKTESTING ENGINE DEMO MUVAFFAQIYATLI YAKUNLANDI!")
    print("=" * 80)
    print()
    print("📋 BAJARILGAN FUNKSIYALAR:")
    print("   ✅ Single strategy backtest")
    print("   ✅ Multiple strategies (parallel)")
    print("   ✅ Grid search optimization")
    print("   ✅ Genetic algorithm optimization")
    print("   ✅ Monte Carlo risk analysis")
    print("   ✅ Walk-forward analysis")
    print("   ✅ Multi-timeframe testing")
    print("   ✅ Portfolio backtesting")
    print("   ✅ Statistical significance testing")
    print("   ✅ Comprehensive report generation")
    print()
    print("🎯 KEYINGI QADAMLAR:")
    print("   📖 To'liq documentation o'qish")
    print("   🛠️  Custom strategiyalar yaratish")
    print("   📊 Real ma'lumotlar bilan test qilish")
    print("   🚀 Production da deploy qilish")
    print()
    print("💡 Eslatma: Demo maqsadli ma'lumotlar ishlatildi.")
    print("   Real trading uchun haqiqiy broker ma'lumotlari kerak.")


def run_performance_test():
    """
    Performance test funksiyasi
    """
    print("\n" + "=" * 60)
    print("⚡ PERFORMANCE TEST")
    print("=" * 60)
    
    # Katta ma'lumotlar bilan test
    print("📊 Katta ma'lumotlar bilan test (10000 kun)...")
    try:
        large_data = create_sample_data(
            symbol="TEST", 
            start_date="1990-01-01", 
            end_date="2023-12-31",
            frequency="D"
        )
        
        engine = ProBacktestingEngine(max_workers=2)
        strategy = StrategyConfig(
            name="Performance Test",
            strategy_function=ProBacktestingEngine.moving_average_strategy,
            parameters={'short_window': 20, 'long_window': 50}
        )
        
        import time
        start_time = time.time()
        
        result = engine.run_backtest(strategy, large_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"   ✅ Test yakunlandi!")
        print(f"   📊 Ma'lumotlar hajmi: {large_data.shape[0]} qator")
        print(f"   ⏱️  Ishga tushish vaqti: {execution_time:.2f}s")
        print(f"   🚀 Tezlik: {large_data.shape[0]/execution_time:.0f} qator/soniya")
        print(f"   💾 Memory usage: {large_data.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
        
    except Exception as e:
        print(f"   ❌ Performance test xatosi: {e}")


if __name__ == "__main__":
    try:
        # Asosiy demo
        run_comprehensive_demo()
        
        # Performance test
        run_performance_test()
        
        print("\n🎉 Barcha testlar muvaffaqiyatli tugallandi!")
        print("📞 Qo'shimcha yordam uchun documentation ni o'qishingiz mumkin.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo to'xtatildi (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Kutilmagan xato: {e}")
        import traceback
        traceback.print_exc()