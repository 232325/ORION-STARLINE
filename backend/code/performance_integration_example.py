"""
Performance Optimization Tizimi Integration Miso
==============================================

Bu fayl mavjud trading tizimiga Performance Optimization
tizimini qanday integratsiya qilishni ko'rsatadi.

Foydalanish:
- PerformanceOptimizer class ni import qiling
- O'z trading strategy laringiz bilan integratsiya qiling
- Real-time monitoring va optimization ni boshlang
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from performance_optimization import (
    PerformanceOptimizer, 
    MetricType, 
    MarketRegime,
    plot_performance_metrics
)
import numpy as np
import pandas as pd
import asyncio
from datetime import datetime, timedelta

class IntegratedTradingSystem:
    """Performance optimization bilan integratsiya qilingan trading tizimi"""
    
    def __init__(self):
        self.optimizer = PerformanceOptimizer()
        self.current_strategy = "default_strategy"
        self.portfolio_value = 100000  # $100k starting capital
        
    async def run_trading_strategy(self, price_data: pd.DataFrame):
        """Trading strategiyasini performance monitoring bilan birga ishga tushirish"""
        
        print("🚀 Integrated Trading System boshlanmoqda...")
        
        # Performance optimization ni boshlash
        self.optimizer.start_optimization()
        
        try:
            # Real-time trading loop
            for i, (timestamp, row) in enumerate(price_data.iterrows()):
                
                # Trading signal generatsiya (mock)
                signal = self._generate_trading_signal(row)
                
                # Trade execution
                trade_result = await self._execute_trade(signal, row)
                
                # Performance monitoring
                await self._monitor_performance(trade_result, timestamp)
                
                # Adaptive optimization
                if i % 100 == 0:  # Har 100 trade da
                    await self._adaptive_optimization()
                
                # A/B testing for different strategies
                if i % 50 == 0:  # Har 50 trade da
                    await self._ab_test_strategy_comparison()
                
                # Log progress
                if i % 20 == 0:
                    self._log_progress(i, len(price_data))
                
                # Small delay to simulate real trading
                await asyncio.sleep(0.01)
            
            # Final performance report
            await self._generate_final_report()
            
        finally:
            self.optimizer.stop_optimization()
    
    def _generate_trading_signal(self, market_data) -> dict:
        """Trading signal generatsiya (mock)"""
        # Simple moving average crossover strategy
        np.random.seed(int(market_data.name.timestamp()) if hasattr(market_data.name, 'timestamp') else 42)
        
        return {
            'action': np.random.choice(['BUY', 'SELL', 'HOLD']),
            'confidence': np.random.uniform(0.6, 0.9),
            'entry_price': market_data.get('close', 100) + np.random.normal(0, 1),
            'stop_loss': market_data.get('close', 100) * 0.98,
            'take_profit': market_data.get('close', 100) * 1.02,
            'timestamp': datetime.now()
        }
    
    async def _execute_trade(self, signal: dict, market_data) -> dict:
        """Trade execution with performance tracking"""
        start_time = datetime.now()
        
        # Simulate trade execution latency
        await asyncio.sleep(np.random.uniform(0.05, 0.15))
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Mock trade result
        result = {
            'signal': signal,
            'executed': np.random.random() > 0.1,  # 90% success rate
            'execution_latency_ms': execution_time,
            'price_filled': signal['entry_price'] + np.random.normal(0, 0.1),
            'pnl': np.random.normal(0, 100),  # Random P&L
            'timestamp': datetime.now()
        }
        
        # Update portfolio value
        if result['executed']:
            self.portfolio_value += result['pnl']
        
        return result
    
    async def _monitor_performance(self, trade_result: dict, timestamp):
        """Real-time performance monitoring"""
        try:
            # Trading metrics
            portfolio_returns = pd.Series([trade_result['pnl'] / self.portfolio_value])
            equity_curve = pd.Series([self.portfolio_value])
            
            # Analyze performance
            trading_metrics = self.optimizer.analyze_trading_performance(
                portfolio_returns, equity_curve=equity_curve
            )
            
            # AI performance (mock predictions)
            if trade_result['executed']:
                y_true = np.array([1 if trade_result['pnl'] > 0 else 0])
                y_pred = np.array([1 if trade_result['signal']['confidence'] > 0.7 else 0])
                
                ai_metrics = self.optimizer.analyze_ai_performance(
                    y_true, y_pred, trade_result['execution_latency_ms']
                )
            
            # System performance
            system_metrics = self.optimizer.analyze_system_performance()
            
            # Cost tracking
            current_costs = {
                'api_cost_per_day': 25.0 + np.random.normal(0, 2),
                'quantum_cost_per_hour': 15.0 + np.random.normal(0, 1)
            }
            cost_metrics = self.optimizer.analyze_cost_performance(current_costs)
            
        except Exception as e:
            print(f"Performance monitoring xatolik: {e}")
    
    async def _adaptive_optimization(self):
        """Adaptive parameter optimization"""
        try:
            # Register optimization strategies
            strategies = {
                'conservative': {'risk_level': 0.02, 'position_size': 0.1},
                'aggressive': {'risk_level': 0.05, 'position_size': 0.2},
                'balanced': {'risk_level': 0.03, 'position_size': 0.15}
            }
            
            for strategy_name, params in strategies.items():
                self.optimizer.adaptive_optimizer.register_strategy(
                    strategy_name, 
                    lambda p: self._optimize_strategy(p),
                    params
                )
            
            # Market regime detection
            # (In real implementation, use actual market data)
            mock_price_data = pd.Series(np.random.random(20) * 100)
            mock_volatility = pd.Series(np.random.random(20) * 0.02)
            
            regime = self.optimizer.adaptive_optimizer.detect_market_regime(
                mock_price_data, mock_volatility
            )
            
            # Optimize based on current performance
            performance_data = {'current_strategy': [0.05, 0.03, 0.07, 0.04, 0.06]}
            best_strategy = self.optimizer.adaptive_optimizer.select_best_strategy(
                performance_data
            )
            
            if best_strategy and best_strategy != self.current_strategy:
                print(f"📈 Strategy switching: {self.current_strategy} -> {best_strategy}")
                self.current_strategy = best_strategy
                
        except Exception as e:
            print(f"Adaptive optimization xatolik: {e}")
    
    async def _ab_test_strategy_comparison(self):
        """A/B testing for strategy comparison"""
        try:
            # Create A/B test for different entry strategies
            test_name = f"entry_strategy_{int(datetime.now().timestamp())}"
            
            exp_id = self.optimizer.ab_testing.create_experiment(
                test_name,
                ["momentum_entry", "reversal_entry"],
                {"momentum_entry": 0.5, "reversal_entry": 0.5}
            )
            
            # Simulate outcomes based on strategy performance
            for variant in ["momentum_entry", "reversal_entry"]:
                for i in range(10):
                    user_id = f"sim_user_{i}"
                    outcome = np.random.normal(0.08 if variant == "momentum_entry" else 0.06, 0.02)
                    self.optimizer.ab_testing.record_outcome(exp_id, variant, user_id, outcome, "return")
            
            # Analyze results
            results = self.optimizer.ab_testing.analyze_results(exp_id, "return")
            if 'statistical_test' in results and results['statistical_test']['significant']:
                winner = results['statistical_test']['better_variant']
                print(f"🏆 A/B Test Winner: {winner}")
                
        except Exception as e:
            print(f"A/B testing xatolik: {e}")
    
    def _optimize_strategy(self, parameters: dict) -> float:
        """Strategy optimization function"""
        # Mock optimization - return performance score
        return np.random.uniform(0.02, 0.08)
    
    def _log_progress(self, current: int, total: int):
        """Progress logging"""
        progress = (current / total) * 100
        print(f"📊 Progress: {progress:.1f}% ({current}/{total}) | Portfolio: ${self.portfolio_value:,.2f}")
    
    async def _generate_final_report(self):
        """Final performance report generation"""
        print("\n📋 Final Performance Report Generation...")
        
        report = self.optimizer.create_performance_report(24)
        
        print(f"\n📈 Performance Summary:")
        print(f"   - Portfolio Value: ${self.portfolio_value:,.2f}")
        print(f"   - Total Return: {((self.portfolio_value - 100000) / 100000) * 100:.2f}%")
        
        print(f"\n🎯 Performance Status:")
        for metric, status in report['status'].items():
            print(f"   - {metric.upper()}: {status.upper()}")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report.get('recommendations', []), 1):
            print(f"   {i}. {rec}")
        
        # Generate performance visualization
        plot_performance_metrics(self.optimizer.monitor, "integrated_performance_metrics.png")
        print(f"\n📊 Performance chart saved: integrated_performance_metrics.png")

async def demo_integrated_system():
    """Integrated trading system demo"""
    print("🎯 Integrated Trading System with Performance Optimization Demo")
    print("=" * 70)
    
    # Generate mock market data
    dates = pd.date_range(start='2024-01-01', end='2024-11-03', freq='H')
    n_periods = min(500, len(dates))  # Limit for demo
    
    price_data = pd.DataFrame({
        'timestamp': dates[:n_periods],
        'open': np.random.random(n_periods) * 100 + 50,
        'high': np.random.random(n_periods) * 100 + 50,
        'low': np.random.random(n_periods) * 100 + 50,
        'close': np.random.random(n_periods) * 100 + 50,
        'volume': np.random.randint(1000, 10000, n_periods)
    })
    price_data.set_index('timestamp', inplace=True)
    
    # Initialize and run integrated system
    trading_system = IntegratedTradingSystem()
    
    try:
        await trading_system.run_trading_strategy(price_data)
        print("\n✅ Integrated trading system demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo xatolik: {e}")

# Standalone usage examples
def example_basic_usage():
    """Asosiy foydalanish misoli"""
    print("📚 Basic Usage Example")
    print("-" * 30)
    
    # Initialize optimizer
    optimizer = PerformanceOptimizer()
    
    # Start monitoring
    optimizer.start_optimization()
    
    try:
        # Simulate trading data
        np.random.seed(42)
        returns = pd.Series(np.random.normal(0.001, 0.02, 252))
        
        # Analyze performance
        trading_metrics = optimizer.analyze_trading_performance(returns)
        print(f"Sharpe Ratio: {trading_metrics.sharpe_ratio:.3f}")
        
        # AI performance
        y_true = np.random.choice([0, 1], 100)
        y_pred = np.random.choice([0, 1], 100)
        ai_metrics = optimizer.analyze_ai_performance(y_true, y_pred)
        print(f"AI Accuracy: {ai_metrics.prediction_accuracy:.3f}")
        
        # System performance
        system_metrics = optimizer.analyze_system_performance()
        print(f"System Latency: {system_metrics.latency_ms:.1f}ms")
        
        # Generate report
        report = optimizer.create_performance_report()
        print(f"Report generated with {len(report.get('recommendations', []))} recommendations")
        
    finally:
        optimizer.stop_optimization()

def example_ab_testing():
    """A/B testing misoli"""
    print("\n🧪 A/B Testing Example")
    print("-" * 30)
    
    optimizer = PerformanceOptimizer()
    
    # Create experiment
    exp_id = optimizer.ab_testing.create_experiment(
        "pricing_strategy",
        ["premium", "standard"],
        {"premium": 0.3, "standard": 0.7}
    )
    
    # Simulate user assignments and outcomes
    for i in range(100):
        user_id = f"user_{i}"
        variant = optimizer.ab_testing.assign_variant(exp_id, user_id)
        
        # Simulate different conversion rates
        conversion_rate = 0.15 if variant == "premium" else 0.12
        outcome = 1 if np.random.random() < conversion_rate else 0
        revenue = np.random.uniform(50, 200) if outcome else 0
        
        optimizer.ab_testing.record_outcome(exp_id, variant, user_id, outcome, "conversion")
        optimizer.ab_testing.record_outcome(exp_id, variant, user_id, revenue, "revenue")
    
    # Analyze results
    conversion_results = optimizer.ab_testing.analyze_results(exp_id, "conversion")
    revenue_results = optimizer.ab_testing.analyze_results(exp_id, "revenue")
    
    print(f"Conversion Results: {conversion_results}")
    print(f"Revenue Results: {revenue_results}")

def example_adaptive_optimization():
    """Adaptive optimization misoli"""
    print("\n🔄 Adaptive Optimization Example")
    print("-" * 40)
    
    optimizer = PerformanceOptimizer()
    adaptive = optimizer.adaptive_optimizer
    
    # Register strategies
    strategies = {
        "mean_reversion": lambda params: np.random.normal(0.05, 0.02),
        "momentum": lambda params: np.random.normal(0.03, 0.03),
        "pairs_trading": lambda params: np.random.normal(0.04, 0.015)
    }
    
    for name, func in strategies.items():
        adaptive.register_strategy(name, func, {"lookback": 20, "threshold": 2.0})
    
    # Simulate performance over time
    performance_history = {}
    for strategy in strategies:
        performance_history[strategy] = [np.random.normal(0.04, 0.02) for _ in range(50)]
    
    # Select best strategy
    best_strategy = adaptive.select_best_strategy(performance_history)
    print(f"Best Strategy: {best_strategy}")
    
    # Optimize parameters
    optimized_params = adaptive.optimize_parameters(best_strategy, performance_history[best_strategy])
    print(f"Optimized Parameters: {optimized_params}")

if __name__ == "__main__":
    # Setup logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Performance Optimization Integration Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_ab_testing()
    example_adaptive_optimization()
    
    # Run integrated demo
    print("\n🎯 Running Integrated System Demo...")
    asyncio.run(demo_integrated_system())