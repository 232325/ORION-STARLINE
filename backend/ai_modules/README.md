# AI Strategy Generator + Backtester + Onboarding System

Bu paket AI-driven strategy generation, comprehensive backtesting va foydalanuvchi onboarding tizimini ta'minlaydi.

## 📋 Tavsif

Bu paket quyidagi uchta asosiy tizimni o'z ichiga oladi:

1. **AI Strategy Generator** - AI-driven strategy generation
2. **Backtester** - Comprehensive backtesting system  
3. **Onboarding Engine** - Global foydalanuvchilar uchun onboarding tizimi
4. **Agent Controller** - AI agent management system

AI Strategy Generator va Backtester Orion Starline AI Trading tizimi uchun yaratilgan ilg'or strategiya yaratish va test qilish tizimidir. Onboarding Engine esa foydalanuvchilarni platformga bosqichma-bosqich tanishtirish uchun mo'ljallangan.

## 🎯 Asosiy imkoniyatlar

### 🤖 Strategy Generation
- **Trend Following** - Trenddagi harakatlarni kuzatish
- **Mean Reversion** - O'rtacha qiymatga qaytish strategiyalari
- **Momentum** - Impuls asosli strategiyalar
- **Statistical Arbitrage** - Statistika asosli arbitraj
- **Grid Trading** - To'ri (grid) savdo
- **Martingale** - Martingale varianti
- **Custom Hybrid** - Aralash strategiyalar

### 🔬 Advanced Testing
- **Genetic Algorithm Optimization** - Genetik algoritm optimizatsiyasi
- **Walk-Forward Analysis** - Oldinga yurish tahlili
- **Monte Carlo Simulation** - Monte Carlo simulatsiya
- **Stress Testing** - Stress test
- **Cross-Validation** - Cross-validation
- **Benchmark Comparison** - Benchmark bilan taqqoslash

### 👥 Onboarding Engine (YANGI!)
- **Welcome Tour** - Platform introduction
- **Demo Trading** - $100,000 virtual balance
- **Skill Assessment** - Automatic level determination
- **AI Assistant** - Interactive help system
- **Personalization** - Customized recommendations
- **Gamification** - Badges, levels, achievements
- **Multi-language** - Uzbek/English support
- **Progress Tracking** - 8-step onboarding process

### 📊 Performance Analysis
- **Historical Data Analysis** - Tarixiy ma'lumotlar tahlili
- **Multiple Timeframes** - Ko'p vaqt doiralari
- **Commission/Slippage Simulation** - Komissiya/sirpanish simulatsiyasi
- **Risk Metrics** - Risk metrikalar
- **Drawdown Analysis** - Tushib ketish tahlili
- **Win/Loss Ratios** - Yutish/yo'qotish nisbatlari
- **Sharpe/Sortino Ratios** - Risk-adjusted returns
- **Calmar Ratio** - Calmar nisbati

## 🚀 Tez boshlanish

### 1. Asosiy foydalanish

```python
import asyncio
from ai_modules import StrategyGenerator, Backtester

# Initialize
generator = StrategyGenerator()
backtester = Backtester()

# Create sample data (for demo)
import pandas as pd
import numpy as np

# Sample market data
dates = pd.date_range('2023-01-01', periods=1000, freq='1h')
np.random.seed(42)

price_changes = np.random.normal(0, 0.001, 1000)
prices = 1.1000 + np.cumsum(price_changes)

data = pd.DataFrame({
    'open': prices + np.random.normal(0, 0.0005, 1000),
    'high': prices + np.abs(np.random.normal(0, 0.001, 1000)),
    'low': prices - np.abs(np.random.normal(0, 0.001, 1000)),
    'close': prices,
    'volume': np.random.lognormal(10, 1, 1000)
}, index=dates)
```

### 2. Strategy yaratish

```python
# Trend following strategy
trend_strategy = generator.generate_trend_following_strategy(
    fast_period=12, slow_period=26
)

# Mean reversion strategy
mean_reversion_strategy = generator.generate_mean_reversion_strategy(
    rsi_period=14, overbought=70, oversold=30
)

# Momentum strategy
momentum_strategy = generator.generate_momentum_strategy(
    momentum_period=10, rsi_period=14
)

# Grid trading strategy
grid_strategy = generator.generate_grid_trading_strategy(
    grid_levels=10, price_range=(0.95, 1.05)
)

# Hybrid strategy
hybrid_strategy = generator.generate_hybrid_strategy(
    components=['trend', 'reversion', 'momentum']
)

print(f"Created {len([trend_strategy, mean_reversion_strategy, momentum_strategy])} strategies")
```

### 3. Strategy backtesting

```python
# Create a simple strategy class
class SimpleStrategy:
    def get_signal(self, data, current_row):
        if len(data) < 20:
            return 0
        
        # Simple moving average crossover
        short_ma = data['close'].tail(10).mean()
        long_ma = data['close'].tail(20).mean()
        
        if short_ma > long_ma:
            return 1  # Buy
        elif short_ma < long_ma:
            return -1  # Sell
        return 0

# Run backtest
strategy = SimpleStrategy()
result = backtester.run_backtest(strategy, data)

print(f"Total Return: {result.total_return:.2%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.3f}")
print(f"Max Drawdown: {result.max_drawdown:.2%}")
print(f"Total Trades: {result.total_trades}")
print(f"Win Rate: {result.win_rate:.2%}")
```

## 📖 Batafsil qo'llanma

### Strategy Types (Strategy Turlari)

#### 1. Trend Following Strategy
```python
trend_strategy = generator.generate_trend_following_strategy(
    fast_period=12,      # Tez MA davri
    slow_period=26       # Sekin MA davri
)

# Parameters
{
    "fast_ma_period": 12,
    "slow_ma_period": 26, 
    "signal_threshold": 0.02,
    "stop_loss_pct": 0.02,
    "take_profit_pct": 0.04
}
```

#### 2. Mean Reversion Strategy
```python
mean_reversion_strategy = generator.generate_mean_reversion_strategy(
    rsi_period=14,       # RSI hisoblash davri
    overbought=70,       # Overbought daraja
    oversold=30          # Oversold daraja
)

# Parameters
{
    "rsi_period": 14,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "bb_period": 20,
    "bb_std": 2.0,
    "stop_loss_pct": 0.015,
    "take_profit_pct": 0.03
}
```

#### 3. Momentum Strategy
```python
momentum_strategy = generator.generate_momentum_strategy(
    momentum_period=10,  # Momentum davri
    rsi_period=14        # RSI davri
)

# Parameters
{
    "momentum_period": 10,
    "rsi_period": 14,
    "rsi_threshold": 50,
    "volume_threshold": 1.5,
    "stop_loss_pct": 0.025,
    "take_profit_pct": 0.05
}
```

#### 4. Statistical Arbitrage Strategy
```python
stat_arb_strategy = generator.generate_statistical_arbitrage_strategy(
    lookback_period=50,     # Orqaga qarab olish davri
    z_score_threshold=2.0   # Z-score kirish darajasi
)

# Parameters
{
    "lookback_period": 50,
    "z_score_entry": 2.0,
    "z_score_exit": 0.5,
    "correlation_threshold": 0.8,
    "half_life_mean_reversion": 5,
    "stop_loss_pct": 0.02
}
```

#### 5. Grid Trading Strategy
```python
grid_strategy = generator.generate_grid_trading_strategy(
    grid_levels=10,               # Grid darajalar soni
    price_range=(0.95, 1.05)      # Narx diapazoni
)

# Parameters
{
    "grid_levels": 10,
    "price_range_low": 0.95,
    "price_range_high": 1.05,
    "grid_spacing": 0.01,
    "rebalance_threshold": 0.01,
    "position_size_pct": 0.1
}
```

#### 6. Martingale Strategy
```python
martingale_strategy = generator.generate_martingale_strategy(
    base_position=0.1,    # Baza pozitsiya hajmi
    multiplier=2.0,       # Ko'paytiruvchi
    max_levels=5          # Maksimal darajalar
)

# Parameters
{
    "base_position_size": 0.1,
    "multiplier": 2.0,
    "max_levels": 5,
    "stop_loss_limit": 0.2,
    "profit_target": 0.05,
    "time_limit_hours": 24
}
```

#### 7. Custom Hybrid Strategy
```python
hybrid_strategy = generator.generate_hybrid_strategy(
    components=['trend', 'reversion', 'momentum']  # Komponentlar
)

# Parameters
{
    "components": ['trend', 'reversion', 'momentum'],
    "weight_trend": 0.3,
    "weight_reversion": 0.3,
    "weight_momentum": 0.4,
    "voting_threshold": 0.6,
    "stop_loss_pct": 0.02,
    "take_profit_pct": 0.04
}
```

### Backtesting (Backtesting)

#### Basic Backtest
```python
# Custom strategy
class MyStrategy:
    def __init__(self):
        self.name = "My Custom Strategy"
    
    def get_signal(self, data, current_row):
        # Your trading logic
        if len(data) < 20:
            return 0
        
        # Example: Simple crossover
        ma_fast = data['close'].tail(5).mean()
        ma_slow = data['close'].tail(20).mean()
        
        if ma_fast > ma_slow * 1.001:  # 0.1% filter
            return 1
        elif ma_fast < ma_slow * 0.999:
            return -1
        return 0

# Configuration
config = BacktestConfig(
    initial_capital=10000.0,
    commission=0.0001,    # 1 pip
    slippage=0.00005,     # 0.5 pip
    spread=0.0002,        # 2 pips
    risk_per_trade=0.02,  # 2% risk
    max_drawdown_limit=0.1  # 10% max DD
)

# Run backtest
backtester = Backtester(config)
strategy = MyStrategy()
result = backtester.run_backtest(strategy, data)

# Performance metrics
print(f"Total Return: {result.total_return:.2%}")
print(f"Annual Return: {result.annual_return:.2%}")
print(f"Volatility: {result.volatility:.2%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.3f}")
print(f"Sortino Ratio: {result.sortino_ratio:.3f}")
print(f"Calmar Ratio: {result.calmar_ratio:.3f}")

# Risk metrics
print(f"Max Drawdown: {result.max_drawdown:.2%}")
print(f"Max DD Duration: {result.max_drawdown_duration} days")
print(f"VaR (95%): {result.var_95:.2%}")
print(f"CVaR (95%): {result.cvar_95:.2%}")

# Trade statistics
print(f"Total Trades: {result.total_trades}")
print(f"Winning Trades: {result.winning_trades}")
print(f"Losing Trades: {result.losing_trades}")
print(f"Win Rate: {result.win_rate:.2%}")
print(f"Average Win: {result.avg_win:.2f}")
print(f"Average Loss: {result.avg_loss:.2f}")
print(f"Profit Factor: {result.profit_factor:.2f}")
print(f"Largest Win: {result.largest_win:.2f}")
print(f"Largest Loss: {result.largest_loss:.2f}")
```

### Advanced Testing

#### Cross-Validation
```python
# K-fold cross validation
cv_results = backtester.cross_validation(strategy, data, n_folds=5)

print("Cross-Validation Results:")
print(f"  Folds tested: {cv_results.get('successful_folds', 0)}/{cv_results.get('n_folds', 0)}")
print(f"  Average Sharpe: {cv_results.get('avg_sharpe', 0):.3f}")
print(f"  Sharpe Stability: {cv_results.get('sharpe_stability', 0):.3f}")
print(f"  CV Score: {cv_results.get('cv_score', 0):.3f}")

# Detailed results
for fold_result in cv_results.get('fold_results', []):
    fold = fold_result['fold']
    success = fold_result['success']
    if success:
        perf = fold_result['test_performance']
        print(f"  Fold {fold}: Return {perf.get('total_return', 0):.2%}, Sharpe {perf.get('sharpe_ratio', 0):.3f}")
    else:
        print(f"  Fold {fold}: Failed")
```

#### Walk-Forward Analysis
```python
# Time series cross-validation
wf_results = backtester.walk_forward_analysis(
    strategy, 
    data, 
    window_size=168,    # 1 hafta (24*7)
    step_size=24        # 1 kun (24 soat)
)

print("Walk-Forward Results:")
print(f"  Windows analyzed: {wf_results.get('windows_analyzed', 0)}")
print(f"  Average test Sharpe: {wf_results.get('avg_test_sharpe', 0):.3f}")
print(f"  Sharpe stability: {wf_results.get('sharpe_stability', 0):.3f}")
print(f"  Average test return: {wf_results.get('avg_test_return', 0):.2%}")

# Stability assessment
sharpe_stability = wf_results.get('sharpe_stability', 0)
if sharpe_stability > 0.8:
    print("  ✓ High stability")
elif sharpe_stability > 0.5:
    print("  ~ Moderate stability")
else:
    print("  ✗ Low stability")
```

#### Monte Carlo Simulation
```python
# Monte Carlo risk assessment
mc_results = backtester.monte_carlo_simulation(
    strategy, 
    data, 
    num_simulations=1000
)

print("Monte Carlo Results:")
print(f"  Simulations completed: {mc_results.get('num_simulations', 0)}")
print(f"  Mean return: {mc_results.get('mean_return', 0):.2%}")
print(f"  Return std: {mc_results.get('std_return', 0):.2%}")
print(f"  5th percentile: {mc_results.get('percentile_5', 0):.2%}")
print(f"  95th percentile: {mc_results.get('percentile_95', 0):.2%}")
print(f"  VaR (5%): {mc_results.get('var_5', 0):.2%}")
print(f"  Probability of profit: {mc_results.get('prob_profit', 0):.2%}")
print(f"  Positive Sharpe probability: {mc_results.get('sharpe_prob_positive', 0):.2%}")

# Risk assessment
prob_profit = mc_results.get('prob_profit', 0)
if prob_profit > 0.7:
    print("  ✓ High probability of success")
elif prob_profit > 0.5:
    print("  ~ Moderate probability of success")
else:
    print("  ✗ Low probability of success")
```

#### Stress Testing
```python
# Stress testing under extreme conditions
stress_results = backtester.stress_test(strategy, data)

print("Stress Testing Results:")
normal_perf = stress_results.get('normal_performance', {})
print(f"  Normal condition return: {normal_perf.get('total_return', 0):.2%}")
print(f"  Normal condition Sharpe: {normal_perf.get('sharpe_ratio', 0):.3f}")

stress_summary = stress_results.get('stress_summary', {})
print(f"  Success rate under stress: {stress_summary.get('success_rate', 0):.2%}")
print(f"  Worst stress return: {stress_summary.get('worst_return', 0):.2%}")
print(f"  Best stress return: {stress_summary.get('best_return', 0):.2%}")
print(f"  Robustness score: {stress_summary.get('robustness_score', 0):.3f}")

# Individual scenarios
stress_tests = stress_results.get('stress_results', [])
print("  Scenario Details:")
for test in stress_tests:
    scenario_name = test.get('scenario', 'Unknown')
    if 'error' not in test:
        return_val = test.get('total_return', 0)
        sharpe_val = test.get('sharpe_ratio', 0)
        print(f"    {scenario_name}: Return {return_val:.2%}, Sharpe {sharpe_val:.3f}")
    else:
        print(f"    {scenario_name}: Failed - {test.get('error', 'Unknown')}")
```

#### Benchmark Comparison
```python
# Compare against buy-and-hold or custom benchmark
benchmark_results = backtester.benchmark_comparison(strategy, data)

if 'error' not in benchmark_results:
    strategy_perf = benchmark_results.get('strategy', {})
    benchmark_perf = benchmark_results.get('benchmark', {})
    outperformance = benchmark_results.get('outperformance', {})
    
    print("Strategy vs Benchmark Comparison:")
    print(f"  Strategy return: {strategy_perf.get('total_return', 0):.2%}")
    print(f"  Benchmark return: {benchmark_perf.get('total_return', 0):.2%}")
    print(f"  Excess return: {outperformance.get('excess_return', 0):.2%}")
    
    print(f"  Strategy Sharpe: {strategy_perf.get('sharpe_ratio', 0):.3f}")
    print(f"  Benchmark Sharpe: {benchmark_perf.get('sharpe_ratio', 0):.3f}")
    print(f"  Information ratio: {outperformance.get('information_ratio', 0):.3f}")
    
    if outperformance.get('beta') is not None:
        print(f"  Beta: {outperformance.get('beta', 0):.3f}")
    if outperformance.get('alpha') is not None:
        print(f"  Alpha: {outperformance.get('alpha', 0):.2%}")
    
    # Outperformance assessment
    excess_return = outperformance.get('excess_return', 0)
    if excess_return > 0.05:
        print("  ✓ Significantly outperforms benchmark")
    elif excess_return > 0:
        print("  ~ Slightly outperforms benchmark")
    elif excess_return > -0.05:
        print("  ~ Similar to benchmark")
    else:
        print("  ✗ Underperforms benchmark")
```

### Strategy Optimization

#### Genetic Algorithm Optimization
```python
# Parameter space for optimization
param_space = {
    'fast_ma_period': [5, 20],
    'slow_ma_period': [20, 50], 
    'signal_threshold': [0.005, 0.05],
    'stop_loss_pct': [0.01, 0.05]
}

# Auto optimization
optimized_strategy = await generator.auto_optimize_parameters(
    strategy_type=StrategyType.TREND_FOLLOWING.value,
    data=data,
    param_space=param_space,
    backtester=backtester
)

print(f"Optimized strategy: {optimized_strategy.name}")
print("Optimized parameters:")
for key, value in optimized_strategy.parameters.items():
    print(f"  {key}: {value}")
```

#### Cross-Validation with Optimization
```python
# Cross-validate optimized strategy
cv_results = generator.cross_validate_strategy(
    optimized_strategy, backtester, data, n_folds=5
)

print("Optimized Strategy Cross-Validation:")
print(f"  CV Score: {cv_results.get('cv_score', 0):.3f}")
print(f"  Stability: {'High' if cv_results.get('cv_score', 0) > 0.5 else 'Low'}")
```

### Performance Reports

#### Generate Comprehensive Report
```python
# Generate detailed performance report
report = backtester.generate_performance_report(result, "strategy_report.txt")
print(report)

# Or save to file
report = backtester.generate_performance_report(result, "/path/to/report.txt")
```

#### Custom Performance Analysis
```python
# Custom analysis
def analyze_strategy_performance(result):
    # Performance scoring
    performance_score = 0
    
    # Return component (40% weight)
    if result.total_return > 0.1:
        performance_score += 40
    elif result.total_return > 0.05:
        performance_score += 30
    elif result.total_return > 0:
        performance_score += 20
    
    # Risk component (30% weight) 
    if result.max_drawdown < 0.05:
        performance_score += 30
    elif result.max_drawdown < 0.1:
        performance_score += 20
    elif result.max_drawdown < 0.15:
        performance_score += 10
    
    # Sharpe component (20% weight)
    if result.sharpe_ratio > 1.5:
        performance_score += 20
    elif result.sharpe_ratio > 1.0:
        performance_score += 15
    elif result.sharpe_ratio > 0.5:
        performance_score += 10
    
    # Consistency component (10% weight)
    if result.win_rate > 0.6:
        performance_score += 10
    elif result.win_rate > 0.5:
        performance_score += 7
    elif result.win_rate > 0.4:
        performance_score += 5
    
    return performance_score

# Analyze strategy
score = analyze_strategy_performance(result)
print(f"Strategy Performance Score: {score}/100")

if score >= 80:
    print("  ✓ Excellent strategy")
elif score >= 60:
    print("  ~ Good strategy") 
elif score >= 40:
    print("  ~ Fair strategy")
else:
    print("  ✗ Poor strategy")
```

## 🛠️ Konfiguratsiya

### Backtest Configuration
```python
# Conservative configuration
conservative_config = BacktestConfig(
    initial_capital=100000.0,    # $100k capital
    commission=0.0001,           # 1 pip commission
    slippage=0.00005,            # 0.5 pip slippage
    spread=0.0002,               # 2 pips spread
    max_position_size=0.5,       # Max 50% position
    risk_per_trade=0.01,         # 1% risk per trade
    max_drawdown_limit=0.05,     # 5% max drawdown
    risk_free_rate=0.02          # 2% risk-free rate
)

# Aggressive configuration
aggressive_config = BacktestConfig(
    initial_capital=10000.0,     # $10k capital
    commission=0.0002,           # 2 pips commission
    slippage=0.0001,             # 1 pip slippage
    spread=0.0003,               # 3 pips spread
    max_position_size=1.0,       # Max 100% position
    risk_per_trade=0.05,         # 5% risk per trade
    max_drawdown_limit=0.2,      # 20% max drawdown
    risk_free_rate=0.02          # 2% risk-free rate
)
```

### Strategy Parameter Ranges
```python
# Trend following parameter ranges
trend_param_space = {
    'fast_ma_period': [5, 20],
    'slow_ma_period': [20, 60],
    'signal_threshold': [0.001, 0.05],
    'stop_loss_pct': [0.01, 0.1],
    'take_profit_pct': [0.02, 0.2]
}

# Mean reversion parameter ranges
mean_reversion_param_space = {
    'rsi_period': [10, 30],
    'rsi_overbought': [65, 80],
    'rsi_oversold': [20, 35],
    'bb_period': [15, 30],
    'bb_std': [1.5, 2.5],
    'stop_loss_pct': [0.01, 0.05],
    'take_profit_pct': [0.02, 0.1]
}

# Momentum parameter ranges  
momentum_param_space = {
    'momentum_period': [5, 20],
    'rsi_period': [10, 25],
    'rsi_threshold': [45, 55],
    'volume_threshold': [1.2, 2.0],
    'stop_loss_pct': [0.02, 0.1],
    'take_profit_pct': [0.03, 0.15]
}
```

## 📊 Performance Metrics

### Risk-Adjusted Returns
- **Sharpe Ratio**: (Return - Risk Free Rate) / Volatility
- **Sortino Ratio**: (Return - Risk Free Rate) / Downside Deviation
- **Calmar Ratio**: Annual Return / Maximum Drawdown
- **Information Ratio**: Excess Return / Tracking Error

### Risk Metrics
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Value at Risk (VaR)**: Maximum expected loss at confidence level
- **Conditional VaR (CVaR)**: Expected loss beyond VaR threshold
- **Beta**: Sensitivity to market movements
- **Alpha**: Risk-adjusted excess return

### Trade Statistics
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Average Win/Loss**: Mean profit/loss per trade
- **Largest Win/Loss**: Maximum profit/loss in single trade
- **Trade Frequency**: Trades per time period

## 🧪 Testing

### Demo ishga tushirish
```bash
cd /workspace/orion-starline/backend/ai_modules
python3 demo.py
```

### Unit Tests
```python
import pytest
from ai_modules import StrategyGenerator, Backtester

def test_strategy_generation():
    generator = StrategyGenerator()
    strategy = generator.generate_trend_following_strategy()
    assert strategy.name is not None
    assert strategy.strategy_type == "trend_following"
    assert len(strategy.parameters) > 0

def test_backtester_initialization():
    backtester = Backtester()
    assert backtester.config is not None
    assert backtester.config.initial_capital > 0
```

### Integration Tests
```python
import asyncio
from ai_modules import StrategyGenerator, Backtester

async def test_full_strategy_lifecycle():
    # Generate strategy
    generator = StrategyGenerator()
    strategy = generator.generate_trend_following_strategy()
    
    # Create test data
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range('2023-01-01', periods=100, freq='1h')
    prices = 1.1000 + np.cumsum(np.random.normal(0, 0.001, 100))
    
    data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.001,
        'low': prices * 0.999,
        'close': prices,
        'volume': np.random.lognormal(10, 1, 100)
    }, index=dates)
    
    # Backtest
    backtester = Backtester()
    result = backtester.run_backtest(strategy, data)
    
    assert result is not None
    assert hasattr(result, 'total_return')
    assert hasattr(result, 'sharpe_ratio')
    assert hasattr(result, 'max_drawdown')
```

## 🔧 Advanced Features

### Custom Strategy Development
```python
class AdvancedStrategy:
    def __init__(self):
        self.name = "Advanced Multi-Factor Strategy"
        self.lookback_period = 50
        self.rsi_period = 14
        self.ma_period = 20
        self.volume_threshold = 1.5
        
    def get_signal(self, data, current_row):
        if len(data) < self.lookback_period:
            return 0
        
        current_idx = len(data) - 1
        
        # Multiple factors
        factors = []
        
        # 1. RSI momentum
        rsi = self._calculate_rsi(data['close'], self.rsi_period)
        if current_idx >= self.rsi_period:
            rsi_current = rsi.iloc[-1]
            rsi_prev = rsi.iloc[-2]
            factors.append(1 if rsi_current > rsi_prev else -1)
        
        # 2. Moving average trend
        ma = data['close'].rolling(self.ma_period).mean()
        if current_idx >= self.ma_period:
            price_current = data['close'].iloc[-1]
            ma_current = ma.iloc[-1]
            factors.append(1 if price_current > ma_current else -1)
        
        # 3. Volume confirmation
        volume_avg = data['volume'].rolling(20).mean()
        if current_idx >= 20:
            volume_current = data['volume'].iloc[-1]
            volume_avg_current = volume_avg.iloc[-1]
            volume_factor = volume_current / volume_avg_current
            factors.append(1 if volume_factor > self.volume_threshold else 0)
        
        # 4. Volatility regime
        returns = data['close'].pct_change().dropna()
        volatility = returns.rolling(20).std()
        if current_idx >= 20:
            vol_current = volatility.iloc[-1]
            vol_avg = volatility.iloc[-20:].mean()
            vol_factor = vol_current / vol_avg
            factors.append(1 if vol_factor < 1.2 else -1)
        
        # Aggregate signals
        if not factors:
            return 0
            
        signal_strength = sum(factors) / len(factors)
        
        if signal_strength > 0.6:
            return 1  # Strong buy
        elif signal_strength > 0.2:
            return 1  # Weak buy
        elif signal_strength < -0.6:
            return -1  # Strong sell
        elif signal_strength < -0.2:
            return -1  # Weak sell
        return 0  # No signal
    
    def _calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

# Test advanced strategy
advanced_strategy = AdvancedStrategy()
result = backtester.run_backtest(advanced_strategy, data)

print(f"Advanced Strategy Results:")
print(f"Total Return: {result.total_return:.2%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.3f}")
print(f"Max Drawdown: {result.max_drawdown:.2%}")
print(f"Win Rate: {result.win_rate:.2%}")
```

### Multi-Timeframe Analysis
```python
def analyze_multiple_timeframes(data, strategy):
    # Different timeframes
    timeframes = {
        '1h': data,
        '4h': data.resample('4h').agg({
            'open': 'first',
            'high': 'max', 
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }),
        '1d': data.resample('1d').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min', 
            'close': 'last',
            'volume': 'sum'
        })
    }
    
    results = {}
    
    for tf_name, tf_data in timeframes.items():
        if len(tf_data) > 50:  # Minimum data requirement
            try:
                result = backtester.run_backtest(strategy, tf_data)
                results[tf_name] = {
                    'total_return': result.total_return,
                    'sharpe_ratio': result.sharpe_ratio,
                    'max_drawdown': result.max_drawdown,
                    'total_trades': result.total_trades
                }
            except Exception as e:
                results[tf_name] = {'error': str(e)}
    
    return results

# Multi-timeframe analysis
mtf_results = analyze_multiple_timeframes(data, strategy)

print("Multi-Timeframe Analysis:")
for tf, result in mtf_results.items():
    if 'error' not in result:
        print(f"{tf}: Return {result['total_return']:.2%}, Sharpe {result['sharpe_ratio']:.3f}")
    else:
        print(f"{tf}: {result['error']}")
```

### Strategy Ensemble
```python
class StrategyEnsemble:
    def __init__(self, strategies, weights=None):
        self.strategies = strategies
        self.weights = weights or [1.0] * len(strategies)
        self.weights = [w / sum(self.weights) for w in self.weights]  # Normalize
    
    def get_signal(self, data, current_row):
        signals = []
        confidences = []
        
        for i, strategy in enumerate(self.strategies):
            try:
                signal = strategy.get_signal(data, current_row)
                signals.append(signal)
                confidences.append(self.weights[i])
            except:
                signals.append(0)
                confidences.append(0)
        
        # Weighted voting
        weighted_signal = sum(s * c for s, c in zip(signals, confidences))
        
        # Decision threshold
        if weighted_signal > 0.3:
            return 1
        elif weighted_signal < -0.3:
            return -1
        return 0

# Create ensemble
ensemble_strategies = [
    SimpleStrategy(),
    # Add more strategies here
]

ensemble = StrategyEnsemble(ensemble_strategies, weights=[0.4, 0.3, 0.3])
ensemble_result = backtester.run_backtest(ensemble, data)

print(f"Ensemble Strategy Results:")
print(f"Total Return: {ensemble_result.total_return:.2%}")
print(f"Sharpe Ratio: {ensemble_result.sharpe_ratio:.3f}")
print(f"Max Drawdown: {ensemble_result.max_drawdown:.2%}")
```

## 🚨 Error Handling & Best Practices

### Common Issues
```python
# Handle insufficient data
def safe_get_signal(self, data, current_row):
    if len(data) < 50:  # Minimum data requirement
        return 0
    
    try:
        # Your signal logic here
        signal = self._calculate_signal(data, current_row)
        
        # Validate signal
        if signal not in [-1, 0, 1]:
            return 0
            
        return signal
        
    except Exception as e:
        logging.warning(f"Signal calculation error: {e}")
        return 0

# Handle extreme market conditions
def handle_market_stress(self, data, signal):
    # Check for market stress indicators
    volatility = data['close'].pct_change().rolling(20).std().iloc[-1]
    
    if volatility > data['close'].pct_change().rolling(100).std().iloc[-1] * 2:
        # Reduce position size during high volatility
        signal = signal * 0.5
        
    return signal
```

### Performance Optimization
```python
import functools

# Cache computations
class OptimizedStrategy:
    def __init__(self):
        self.ma_cache = {}
        self.rsi_cache = {}
    
    @functools.lru_cache(maxsize=1000)
    def _calculate_ma(self, prices_tuple, period):
        prices = list(prices_tuple)
        return np.mean(prices[-period:])
    
    def get_signal(self, data, current_row):
        prices_tuple = tuple(data['close'].values)
        
        # Use cached moving average
        ma_fast = self._calculate_ma(prices_tuple, 10)
        ma_slow = self._calculate_ma(prices_tuple, 20)
        
        if ma_fast > ma_slow:
            return 1
        elif ma_fast < ma_slow:
            return -1
        return 0
```

## 📈 Performance Analysis Tools

### Strategy Comparison
```python
def compare_strategies(strategies, data, benchmark_data=None):
    results = {}
    
    for name, strategy in strategies.items():
        try:
            result = backtester.run_backtest(strategy, data)
            results[name] = {
                'return': result.total_return,
                'sharpe': result.sharpe_ratio,
                'drawdown': result.max_drawdown,
                'trades': result.total_trades,
                'win_rate': result.win_rate,
                'profit_factor': result.profit_factor
            }
        except Exception as e:
            results[name] = {'error': str(e)}
    
    # Add benchmark if provided
    if benchmark_data is not None:
        try:
            benchmark_result = backtester.run_backtest(strategies['benchmark'], benchmark_data)
            results['benchmark'] = {
                'return': benchmark_result.total_return,
                'sharpe': benchmark_result.sharpe_ratio,
                'drawdown': benchmark_result.max_drawdown
            }
        except:
            pass
    
    return results

# Compare multiple strategies
strategy_dict = {
    'Trend_Following': trend_strategy,
    'Mean_Reversion': mean_reversion_strategy,
    'Momentum': momentum_strategy
}

comparison_results = compare_strategies(strategy_dict, data)

print("Strategy Comparison Results:")
for name, metrics in comparison_results.items():
    if 'error' not in metrics:
        print(f"{name}: Return {metrics['return']:.2%}, Sharpe {metrics['sharpe']:.3f}")
    else:
        print(f"{name}: {metrics['error']}")
```

### Risk-Reward Analysis
```python
def analyze_risk_reward(result):
    analysis = {
        'risk_adjusted_return': result.total_return / (result.max_drawdown + 0.001),
        'return_per_trade': result.total_return / max(result.total_trades, 1),
        'volatility_adjusted_return': result.total_return / (result.volatility + 0.001),
        'sharpe_consistency': result.sharpe_ratio / (1 + abs(result.skewness)),
        'downside_protection': 1 - result.cvar_95,
        'upside_potential': result.total_return - result.cvar_95
    }
    
    return analysis

# Risk-reward analysis
rr_analysis = analyze_risk_reward(result)

print("Risk-Reward Analysis:")
for metric, value in rr_analysis.items():
    print(f"  {metric}: {value:.3f}")
```

## 🔍 Monitoring & Alerting

### Real-time Performance Monitoring
```python
class PerformanceMonitor:
    def __init__(self, backtester, alert_thresholds):
        self.backtester = backtester
        self.thresholds = alert_thresholds
        self.alert_history = []
    
    def check_performance(self, strategy, data):
        try:
            result = self.backtester.run_backtest(strategy, data)
            alerts = []
            
            # Check thresholds
            if result.sharpe_ratio < self.thresholds.get('min_sharpe', 0.5):
                alerts.append(f"Low Sharpe ratio: {result.sharpe_ratio:.3f}")
            
            if result.max_drawdown > self.thresholds.get('max_drawdown', 0.15):
                alerts.append(f"High drawdown: {result.max_drawdown:.2%}")
            
            if result.win_rate < self.thresholds.get('min_win_rate', 0.4):
                alerts.append(f"Low win rate: {result.win_rate:.2%}")
            
            # Store alerts
            self.alert_history.extend(alerts)
            
            return {
                'result': result,
                'alerts': alerts,
                'performance_score': self._calculate_score(result)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_score(self, result):
        score = 0
        
        # Return component
        if result.total_return > 0.2:
            score += 30
        elif result.total_return > 0.1:
            score += 20
        elif result.total_return > 0:
            score += 10
        
        # Risk component
        if result.max_drawdown < 0.05:
            score += 25
        elif result.max_drawdown < 0.1:
            score += 15
        elif result.max_drawdown < 0.15:
            score += 5
        
        # Efficiency component
        if result.sharpe_ratio > 1.0:
            score += 25
        elif result.sharpe_ratio > 0.5:
            score += 15
        elif result.sharpe_ratio > 0:
            score += 5
        
        # Consistency component
        if result.win_rate > 0.6:
            score += 20
        elif result.win_rate > 0.5:
            score += 10
        
        return score

# Set up monitoring
monitor = PerformanceMonitor(backtester, {
    'min_sharpe': 0.5,
    'max_drawdown': 0.15,
    'min_win_rate': 0.4
})

# Monitor strategy
monitoring_result = monitor.check_performance(strategy, data)

print(f"Performance Score: {monitoring_result['performance_score']}/100")
if monitoring_result['alerts']:
    print("Alerts:")
    for alert in monitoring_result['alerts']:
        print(f"  ⚠️ {alert}")
```

## 📊 Deployment & Production

### Strategy Deployment Checklist
```python
def deployment_checklist(strategy, data):
    """Pre-deployment validation"""
    checks = {
        'data_availability': len(data) > 100,
        'parameter_validation': _validate_parameters(strategy),
        'backtest_performance': _run_quick_backtest(strategy, data),
        'stress_test_results': _run_stress_test(strategy, data),
        'cross_validation': _run_cv_check(strategy, data)
    }
    
    # Overall readiness
    readiness_score = sum(1 for passed in checks.values() if passed)
    deployment_ready = readiness_score >= 4  # 80% threshold
    
    return {
        'deployment_ready': deployment_ready,
        'readiness_score': readiness_score,
        'total_checks': len(checks),
        'checks': checks
    }

def _validate_parameters(strategy):
    """Validate strategy parameters"""
    required_params = ['name', 'strategy_type', 'parameters']
    return all(hasattr(strategy, param) for param in required_params)

def _run_quick_backtest(strategy, data):
    """Quick performance check"""
    try:
        result = backtester.run_backtest(strategy, data.head(200))
        return result.total_return > -0.5  # Not catastrophic loss
    except:
        return False

def _run_stress_test(strategy, data):
    """Basic stress test"""
    try:
        stress_results = backtester.stress_test(strategy, data.head(200))
        return stress_results.get('stress_summary', {}).get('success_rate', 0) > 0.8
    except:
        return False

def _run_cv_check(strategy, data):
    """Cross-validation check"""
    try:
        cv_results = backtester.cross_validation(strategy, data.head(200), n_folds=3)
        return cv_results.get('cv_score', 0) > 0.3
    except:
        return False

# Run deployment check
deployment_check = deployment_checklist(strategy, data)

print(f"Deployment Readiness: {deployment_check['readiness_score']}/{deployment_check['total_checks']}")
if deployment_check['deployment_ready']:
    print("✅ Strategy is ready for deployment")
else:
    print("❌ Strategy needs improvement before deployment")
    
    print("Failed checks:")
    for check, passed in deployment_check['checks'].items():
        if not passed:
            print(f"  ✗ {check}")
```

## 📚 Resources & References

### Additional Documentation
- [Technical Analysis Library Documentation](https://talib.org/)
- [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/)
- [NumPy Reference](https://numpy.org/doc/)
- [Statistical Arbitrage Methods](https://www.quantifiedstrategies.com/)

### Research Papers
- Factor-Based Investment Strategies
- Machine Learning in Finance
- Risk Management in Algorithmic Trading
- Portfolio Optimization Theory

### Online Courses
- Quantitative Finance
- Algorithmic Trading
- Risk Management
- Financial Engineering

## 🤝 Contributing

### Development Setup
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m pytest`
4. Start development: `python demo.py`

### Code Standards
- PEP 8 compliance
- Type hints
- Documentation strings
- Test coverage > 80%

### Pull Request Process
1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Update documentation
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 👥 Authors

- **Orion Starline AI Team** - *Initial work* - AI Strategy Generator + Backtester

## 🆘 Support

### Common Issues
- **Strategy not generating signals**: Check data requirements
- **Poor backtest performance**: Validate parameters and signal logic
- **High memory usage**: Optimize data processing
- **Slow execution**: Use vectorized operations

### Getting Help
- Check documentation
- Review demo examples
- Run diagnostic tools
- Contact support team

## 🔄 Changelog

### v1.0.0 (2025-11-04)
- Initial release
- Core strategy generation functionality
- Comprehensive backtesting system
- Performance analytics
- Advanced testing methods
- Strategy optimization tools
- Risk management features
- Cross-validation and walk-forward analysis
- Monte Carlo simulation
- Stress testing framework
- Benchmark comparison tools

---

**Orion Starline AI Trading System** - AI Strategy Generator + Backtester v1.0.0

# 🚨 Xavfsizlik va Muvofiqliq Tizimi

## Kirish

Bu tizim Orion Starline AI tizimi uchun to'liq xavfsizlik va muvofiqlik choralarini ta'minlaydi.

## Asosiy Xususiyatlar

### 1. Kontent Filtrlash (Content Filtering)

```python
from safety_compliance import SafetyCompliance, ContentType

# Tizimni ishga tushirish
safety_system = SafetyCompliance()

# Foydalanuvchi kiritishini tekshirish
result = safety_system.validate_user_input(
    user_input="Salom, bu test kontenti",
    content_type=ContentType.GENERAL,
    user_id="user123",
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0"
)

print(result)
```

### 2. Moliyaviy Maslahat Muvofiqligi

```python
# Moliyaviy maslahat validatsiyasi
financial_advice = """
Bu investitsiya haqida maslahat. 
Investitsiya risk bilan bog'liq va kafolat yo'q.
Professional maslahat olish tavsiya etiladi.
"""

result = safety_system.validate_financial_advice(
    advice_content=financial_advice,
    user_id="user123",
    jurisdiction="kyiv"  # O'zbekiston
)

print(result)
```

### 3. GDPR/CCPA Muvofiqligi

```python
# Foydalanuvchi ma'lumotlarini eksport qilish
export_result = safety_system.handle_user_data_request(
    user_id="user123",
    request_type="export",
    data_types=["profile", "activity", "preferences"]
)

# Ma'lumotlarni o'chirish (Right to be Forgotten)
deletion_result = safety_system.handle_user_data_request(
    user_id="user123", 
    request_type="deletion",
    data_types=["activity", "preferences"]
)
```

### 4. Audit Logging

```python
# Foydalanuvchi audit tarixi
audit_summary = safety_system.get_audit_summary(
    user_id="user123",
    days=30
)

print(audit_summary)
```

### 5. Rate Limiting

```python
# Rate limit tekshirish
is_limited = safety_system.rate_limiter.is_rate_limited(
    identifier="user123",
    endpoint="api"  # default, auth, api, bulk
)

# Qolgan so'rovlar soni
remaining = safety_system.rate_limiter.get_remaining_requests(
    identifier="user123",
    endpoint="api"
)
```

### 6. Real-time Monitoring

```python
# Monitoring yoqish
safety_system.enable_threat_detection()

# Ogohlantirish email manzili
safety_system.realtime_monitor.set_alert_email("admin@orion-starline.com")
```

## Barcha Modullar

1. **ContentFilter** - Kontent filtrlash
2. **FinancialCompliance** - Moliyaviy muvofiqlik  
3. **DataProtection** - Ma'lumotlar himoyasi (GDPR/CCPA)
4. **AuditLogger** - Audit logging
5. **ComplianceReporter** - Muvofiqliq hisobotlari
6. **RateLimiter** - API so'rovlar cheklovlari
7. **RealTimeMonitor** - Real-time monitoring
8. **SafetyCompliance** - Asosiy boshqaruv klassi

Batafsil ma'lumot uchun `safety_compliance.py` faylini ko'ring.

---

## 🤝 Social Trading Platform

### Kirish

Social Trading Platform moduli ijtimoiy savdo platformasi uchun to'liq funksionallikni ta'minlaydi. Bu modul foydalanuvchilarga muvaffaqiyatli treyderlarni kuzatish, signallarni almashish va ijtimoiy savdo qilish imkonini beradi.

### Asosiy Imkoniyatlar

#### 1. Copy Trading
```python
from social_trading import SocialTradingPlatform, UserRole

platform = SocialTradingPlatform()

# Copy trading boshlash
copy_result = platform.start_copy_trading(
    follower_id="follower_user_id",
    trader_id="trader_user_id", 
    amount=1000.0,
    copy_percentage=100.0
)
```

#### 2. Signal Almashish
```python
from social_trading import SignalType, SignalPrivacy

# Signal yaratish
signal_result = platform.create_signal(
    trader_id="trader_user_id",
    symbol="EURUSD",
    signal_type=SignalType.BUY,
    price=1.0950,
    stop_loss=1.0900,
    take_profit=1.1000,
    privacy=SignalPrivacy.PUBLIC,
    confidence=0.85
)
```

#### 3. Reyting Tizimi
```python
# Treyderga reyting berish
rating_result = platform.rate_trader(
    user_id="rater_user_id",
    trader_id="trader_user_id",
    rating=4.5,
    comment="Juda yaxshi treyder!"
)
```

#### 4. Performance Kuzatish
```python
# Performance ma'lumotlarini olish
performance = platform.track_performance("user_id")
print(f"Win rate: {performance['performance']['win_rate']:.1f}%")
```

#### 5. Leaderboard
```python
# Top performers olish
leaderboard = platform.get_top_performers(period="month", limit=10)
for performer in leaderboard["performers"]:
    print(f"#{performer['rank']}: {performer['username']}")
```

### Demo Foydalanish

```python
# To'liq demo
python social_trading.py
```

Bu demo quyidagi funksiyalarni ko'rsatadi:
- Foydalanuvchi ro'yxatdan o'tkazish
- Treyder tasdiqlash
- Signal yaratish
- Copy trading
- Obuna tizimi
- Reyting berish
- Performance kuzatish
- Ijtimoiy funksiyalar

### Asosiy Modullar

1. **User Management** - Foydalanuvchi boshqaruvi
2. **Signal System** - Trading signallar
3. **Copy Trading** - Copy trading tizimi
4. **Performance Tracking** - Performance kuzatuvi
5. **Rating System** - Reyting tizimi
6. **Social Features** - Ijtimoiy xususiyatlar
7. **Verification** - Tasdiqlash tizimi
8. **Commission Management** - Komissiya boshqaruvi
9. **Notifications** - Bildirishnomalar

### Ma'lumotlar Bazasini Strukturasi

- **users** - Foydalanuvchi ma'lumotlari
- **trader_profiles** - Treyder profillari  
- **trading_signals** - Trading signallar
- **copy_trades** - Copy trading ma'lumotlari
- **followers** - Obunachilar
- **comments** - Izohlar
- **likes** - Likes
- **notifications** - Bildirishnomalar
- **performance_metrics** - Performance metrikalar

### Platform Statistikalari

```python
# Platform umumiy statistikalari
stats = platform.get_platform_stats()
print(f"Jami foydalanuvchilar: {stats['stats']['total_users']}")
print(f"Aktiv copy trade: {stats['stats']['active_copy_trades']}")
```

Batafsil ma'lumot uchun `social_trading.py` faylini ko'ring.