# Pro Backtesting Engine Documentation

## Kirish

Pro Backtesting Engine - bu professional darajadagi backtesting tizimi bo'lib, ilg'or trading strategiyaliarini sinash va tahlil qilish uchun mo'ljallangan. Bu tizim bir vaqtning o'zida bir nechta strategiyani sinash, parametrlarni optimallashtirish, Monte Carlo simulyatsiyasi, walk-forward tahlil va boshqa ilg'or funksiyalarni qo'llab-quvvatlaydi.

## Asosiy xususiyatlar

### 1. Advanced Strategy Testing
- Bir vaqtning o'zida bir nechta strategiyani sinash
- Parallel va sequential ishlash qo'llab-quvvatlash
- Har bir strategiya uchun alohida konfiguratsiya

### 2. Historical Data Analysis
- 10+ yil ma'lumotlarni qo'llab-quvvatlash
- Turli vaqt freymlarida ishlash (1m, 5m, 1h, 1d)
- Ma'lumotlarni avtomatik tozalash va tayyorlash

### 3. Performance Optimization
- Grid Search, Genetic Algorithm, Random Search
- Parametrlarni avtomatik optimallashtirish
- Turli maqsad funksiyalari (Sharpe ratio, Sortino ratio, etc.)

### 4. Monte Carlo Simulation
- Block, Random, Circular bootstrap metodlari
- Risk scenario testlash
- Confidence interval hisoblash
- VaR va CVaR analizi

### 5. Walk-Forward Analysis
- Out-of-sample testlash
- Model stability va robustness baholash
- Progressive optimization

### 6. Multi-timeframe Testing
- 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M vaqt freymlari
- Cross-timeframe signal analysis
- Timeframe correlation

### 7. Transaction Cost Modeling
- Commission modellari (fixed, percentage, tiered, volume-weighted)
- Slippage modellari (constant, proportional, market impact, sqrt impact)
- Market depth hisobga olish

### 8. Portfolio Backtesting
- Multi-asset portfolio testing
- Dynamic rebalancing
- Portfolio-level risk metrics

### 9. Risk-adjusted Metrics
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Maximum Drawdown
- Win Rate, Profit Factor

### 10. Optimization Algorithms
- Genetic Algorithm
- Grid Search
- Random Search
- Bayesian Optimization (o'shaqda qo'shiladi)

## O'rnatish va Sozlanish

### Kerakli kutubxonalar

```python
pip install numpy pandas scipy scikit-learn plotly joblib deap
```

### Asosiy ishga tushirish

```python
from pro_backtesting import (
    ProBacktestingEngine, StrategyConfig, 
    TimeFrame, OptimizationMethod
)

# Engine yaratish
engine = ProBacktestingEngine(
    data_manager=None,  # O'z ma'lumot managerizni ulash mumkin
    max_workers=4,      # Worker proces soni
    cache_enabled=True, # Natija cache qilish
    benchmark_data=None # Benchmark ma'lumotlari
)
```

## Ishlatish misollari

### 1. Oddiy Backtest

```python
import pandas as pd
from pro_backtesting import StrategyConfig, ProBacktestingEngine

# Ma'lumotlarni yuklash
data = pd.read_csv('price_data.csv', index_col=0, parse_dates=True)

# Strategiya konfiguratsiyasi
strategy_config = StrategyConfig(
    name="Moving Average Crossover",
    strategy_function=ProBacktestingEngine.moving_average_strategy,
    parameters={
        'short_window': 20,
        'long_window': 50
    },
    initial_capital=100000.0,
    commission=0.001,
    slippage=0.0005
)

# Backtest ishga tushirish
engine = ProBacktestingEngine()
result = engine.run_backtest(strategy_config, data)

# Natija ko'rish
print(f"Total Return: {result.total_return:.2%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Max Drawdown: {result.max_drawdown:.2%}")
```

### 2. Bir Nechta Strategiya

```python
# Strategiya konfiguratsiyalari
ma_strategy = StrategyConfig(
    name="MA Strategy",
    strategy_function=ProBacktestingEngine.moving_average_strategy,
    parameters={'short_window': 20, 'long_window': 50}
)

rsi_strategy = StrategyConfig(
    name="RSI Strategy",
    strategy_function=ProBacktestingEngine.rsi_strategy,
    parameters={'rsi_period': 14, 'oversold': 30, 'overbought': 70}
)

momentum_strategy = StrategyConfig(
    name="Momentum Strategy",
    strategy_function=ProBacktestingEngine.momentum_strategy,
    parameters={'lookback_period': 20}
)

strategies = [ma_strategy, rsi_strategy, momentum_strategy]

# Bir vaqtning o'zida ishlash
results = engine.run_multiple_strategies(
    strategies, data, parallel=True
)

# Natijalarni ko'rish
for result in results:
    print(f"{result.strategy_name}: {result.total_return:.2%}")
```

### 3. Parameter Optimization

```python
# Parametr diapazonlari
parameter_ranges = {
    'short_window': [10, 15, 20, 25, 30],
    'long_window': [40, 45, 50, 55, 60],
    'rsi_period': [10, 14, 18, 22]
}

# Grid Search optimizatsiya
best_params, best_result = engine.optimize_strategy_parameters(
    strategy_config=rsi_strategy,
    data=data,
    parameter_ranges=parameter_ranges,
    optimization_method=OptimizationMethod.GRID_SEARCH,
    objective='sharpe_ratio'
)

print(f"Best parameters: {best_params}")
print(f"Best Sharpe ratio: {best_result.sharpe_ratio:.2f}")
```

### 4. Genetic Algorithm Optimization

```python
# Genetic Algorithm bilan optimizatsiya
best_params, best_result = engine.optimize_strategy_parameters(
    strategy_config=ma_strategy,
    data=data,
    parameter_ranges={
        'short_window': (5, 30),    # Integer range
        'long_window': (30, 100),   # Integer range
        'threshold': (0.01, 0.1)    # Float range
    },
    optimization_method=OptimizationMethod.GENETIC,
    max_iterations=50,
    objective='calmar_ratio'
)
```

### 5. Monte Carlo Simulation

```python
# Risk analizi uchun Monte Carlo
mc_result = engine.run_monte_carlo_simulation(
    strategy_config=ma_strategy,
    data=data,
    num_simulations=1000,
    bootstrap_method='block',
    confidence_level=0.95
)

print(f"Probability of loss: {mc_result.probability_of_loss:.2%}")
print(f"VaR (95%): {mc_result.var_95:.2%}")
print(f"CVaR (95%): {mc_result.cvar_95:.2%}")
print(f"Best case: {mc_result.best_case:.2%}")
print(f"Worst case: {mc_result.worst_case:.2%}")
```

### 6. Walk-Forward Analysis

```python
# Out-of-sample testlash
wf_result = engine.run_walk_forward_analysis(
    strategy_config=ma_strategy,
    data=data,
    in_sample_period=252,      # 1 yil
    out_of_sample_period=63,   # 3 oy
    step_size=21               # Har hafta
)

print(f"Stability score: {wf_result.stability_score:.2f}")
print(f"Robustness score: {wf_result.robustness_score:.2f}")

# Har bir period uchuna natijalar
for i, (period, result, oos_result) in enumerate(
    zip(wf_result.periods, wf_result.results, wf_result.out_of_sample_results)
):
    print(f"Period {i+1}: {period[0]} - {period[1]}")
    if result:
        print(f"  In-sample: {result.total_return:.2%}")
    if oos_result:
        print(f"  Out-of-sample: {oos_result.total_return:.2%}")
```

### 7. Multi-timeframe Analysis

```python
# Turli vaqt freymlarida testlash
data_dict = {
    TimeFrame.D1: daily_data,
    TimeFrame.H4: hourly_4h_data,
    TimeFrame.H1: hourly_1h_data
}

tf_results = engine.run_multi_timeframe_analysis(
    strategy_configs=[ma_strategy, rsi_strategy],
    data_dict=data_dict,
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2023, 12, 31)
)

# Natija ko'rish
for timeframe, result in tf_results.items():
    print(f"{timeframe}: Return {result.total_return:.2%}, "
          f"Sharpe {result.sharpe_ratio:.2f}")
```

### 8. Portfolio Backtesting

```python
# Portfolio strategiyasi
portfolio_strategies = [
    StrategyConfig("MA Portfolio", ma_strategy, parameters={...}),
    StrategyConfig("RSI Portfolio", rsi_strategy, parameters={...}),
    StrategyConfig("Momentum Portfolio", momentum_strategy, parameters={...})
]

# Portfolio og'irliklari (yig'indisi 1.0 bo'lishi kerak)
weights = [0.4, 0.3, 0.3]

# Ma'lumotlar
data_dict = {
    'asset1': asset1_data,
    'asset2': asset2_data,
    'asset3': asset3_data
}

# Portfolio backtest
portfolio_result = engine.run_portfolio_backtest(
    strategies=portfolio_strategies,
    weights=weights,
    data_dict=data_dict,
    rebalance_frequency='monthly',
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2023, 12, 31)
)

print(f"Portfolio Return: {portfolio_result.total_return:.2%}")
print(f"Portfolio Sharpe: {portfolio_result.sharpe_ratio:.2f}")
```

### 9. Statistical Significance Testing

```python
# Strategiya natijalari
strategy_results = [result1, result2, result3]  # BacktestResult obyektlari

# Benchmark natijalari
benchmark_results = [benchmark_result1, benchmark_result2]  # Benchmark natijalari

# Statistical significance test
sig_results = engine.calculate_statistical_significance(
    strategy_results=strategy_results,
    benchmark_results=benchmark_results,
    alpha=0.05
)

print(f"Return test p-value: {sig_results['return_test']['p_value']:.4f}")
print(f"Sharpe test p-value: {sig_results['sharpe_test']['p_value']:.4f}")
print(f"Return effect size (Cohen's d): {sig_results['return_test']['cohens_d']:.2f}")
```

### 10. Comprehensive Report Generation

```python
# To'liq hisobot yaratish
html_report = engine.generate_comprehensive_report(
    results=strategy_results,
    benchmark_results=benchmark_results,
    monte_carlo_results=mc_result,
    walk_forward_results=wf_result,
    save_path="/path/to/backtest_report.html"
)

print(f"Report saved to: /path/to/backtest_report.html")
```

## Custom Strategiya Yaratish

O'z strategiyangizni yaratish uchun quyidagi formatni ishlatish kerak:

```python
def my_custom_strategy(data: pd.DataFrame, **params) -> pd.DataFrame:
    """
    Custom trading strategy
    
    Args:
        data: OHLCV ma'lumotlari
        **params: Strategiya parametrlari
    
    Returns:
        DataFrame with 'signal' column (1: buy, -1: sell, 0: hold)
    """
    signals = data.copy()
    
    # Sizning strategiya logikasi
    
    # Masalan: Bollinger Bands strategy
    window = params.get('window', 20)
    num_std = params.get('num_std', 2)
    
    # Moving average hisoblash
    signals['ma'] = data['close'].rolling(window=window).mean()
    
    # Standard deviation hisoblash
    signals['std'] = data['close'].rolling(window=window).std()
    
    # Bollinger Bands
    signals['upper'] = signals['ma'] + (signals['std'] * num_std)
    signals['lower'] = signals['ma'] - (signals['std'] * num_std)
    
    # Signallarni yaratish
    signals['signal'] = 0
    signals.loc[data['close'] > signals['upper'], 'signal'] = -1  # Sell
    signals.loc[data['close'] < signals['lower'], 'signal'] = 1   # Buy
    
    return signals[['signal']]

# Strategiya konfiguratsiyasi
custom_strategy = StrategyConfig(
    name="Bollinger Bands",
    strategy_function=my_custom_strategy,
    parameters={
        'window': 20,
        'num_std': 2
    },
    initial_capital=100000,
    commission=0.001,
    slippage=0.0005
)
```

## Cost Model Configurations

### Commission Models

```python
# Percentage commission (default)
commission_model = 'percentage'  # 0.1% har bir trade uchun

# Fixed commission
commission_model = 'fixed'  # Har bir trade uchun $1

# Tiered commission
commission_model = 'tiered'  # Volume asosida

# Volume weighted commission
commission_model = 'volume_weighted'  # Volume asosida kamaytirish
```

### Slippage Models

```python
# Proportional slippage (default)
slippage_model = 'proportional'  # Position size va volatility ga bog'liq

# Constant slippage
slippage_model = 'constant'  # Har doim bir xil

# Market impact slippage
slippage_model = 'market_impact'  # Market depth hisobga oladi

# Square root impact
slippage_model = 'sqrt_impact'  # Square root law
```

## Performance Metrics

Backtest natijalarida quyidagi metrikalar hisoblanadi:

### Return Metrics
- **Total Return**: Jami foyda (%)
- **Annualized Return**: Yillik foyda (%)
- **Compound Annual Growth Rate (CAGR)**: Murakkab yillik o'sish sur'ati

### Risk Metrics
- **Volatility**: Yillik volatilite (%)
- **Maximum Drawdown**: Maksimal drawdown (%)
- **Value at Risk (VaR)**: Risk qiymati
- **Conditional VaR (CVaR)**: Shartli risk qiymati

### Risk-Adjusted Metrics
- **Sharpe Ratio**: Risk-adjusted foyda
- **Sortino Ratio**: Downside risk asosida
- **Calmar Ratio**: Drawdown asosida

### Trade Analysis
- **Win Rate**: G'alaba foizi (%)
- **Profit Factor**: Foyda factor
- **Total Trades**: Jami trade soni
- **Average Win/Loss**: O'rtacha g'alaba/mag'lubiyat

## Caching va Performance

Engine caching qo'llab-quvvatlaydi:

```python
# Engine yaratishda cache yoqish
engine = ProBacktestingEngine(cache_enabled=True)

# Cache clearing
engine.cache.clear()
engine.results_cache.clear()
```

## Parallel Processing

```python
# Ko'p processor yadrolari ishlatish
engine = ProBacktestingEngine(max_workers=8)

# Bir nechta strategiyani parallel ishlash
results = engine.run_multiple_strategies(
    strategies=strategies, 
    data=data, 
    parallel=True
)
```

## Error Handling va Logging

```python
import logging

# Logging sozlash
logging.basicConfig(level=logging.INFO)

# Engine yaratish
engine = ProBacktestingEngine()

# Backtest ishga tushirish
try:
    result = engine.run_backtest(strategy_config, data)
except Exception as e:
    print(f"Backtest xatosi: {e}")
    # Error handling logika
```

## Best Practices

### 1. Data Quality
```python
# Ma'lumotlarni tekshirish
def validate_data(data: pd.DataFrame) -> bool:
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    
    if not all(col in data.columns for col in required_columns):
        print("Kerakli ustunlar topilmadi")
        return False
    
    if data.isnull().any().any():
        print("Null qiymatlar mavjud")
        return False
    
    if (data['high'] < data['low']).any():
        print("High < Low qiymatlar")
        return False
    
    return True

# Tekshirish
if validate_data(data):
    print("Ma'lumotlar toza")
else:
    print("Ma'lumotlarni tozalash kerak")
```

### 2. Walk-Forward Validation
```python
# Har doim walk-forward analiz ishlatish
wf_result = engine.run_walk_forward_analysis(
    strategy_config, data,
    in_sample_period=252,  # 1 yil
    out_of_sample_period=63,  # 3 oy
    step_size=21
)

# Robustness check
if wf_result.robustness_score < 0.7:
    print("⚠️ Strategiya robustness past")
```

### 3. Monte Carlo Validation
```python
# Monte Carlo bilan risk baholash
mc_result = engine.run_monte_carlo_simulation(
    strategy_config, data, num_simulations=1000
)

# Risk check
if mc_result.probability_of_loss > 0.3:
    print("⚠️ Strategiya yo'qotish ehtimoli yuqori")
```

### 4. Parameter Stability
```python
# Parameter grid search ishlatish
param_ranges = {
    'short_window': [10, 15, 20, 25, 30],
    'long_window': [40, 45, 50, 55, 60]
}

best_params, best_result = engine.optimize_strategy_parameters(
    strategy_config, data, param_ranges
)

# Eng yaxshi va eng yomon natijalarni solishtirish
# Agar juda katta farq bo'lsa, overfitting bor
```

### 5. Statistical Significance
```python
# Benchmark bilan solishtirish
benchmark_results = [...]  # Benchmark strategiya natijalari
sig_results = engine.calculate_statistical_significance(
    strategy_results, benchmark_results
)

if not sig_results['return_test']['significant']:
    print("⚠️ Strategiya benchmark dan sezilarli yaxshiroq emas")
```

## Troubleshooting

### Tez-tez uchraydigan muammolar

1. **Memory Error**: Katta ma'lumotlar bilan ishlashda
   ```python
   # Ma'lumotlarni qismlarga ajratish
   data_chunks = [data[i:i+1000] for i in range(0, len(data), 1000)]
   ```

2. **Slow Performance**: Parallel processing yoqish
   ```python
   engine = ProBacktestingEngine(max_workers=8, cache_enabled=True)
   ```

3. **Data Quality Issues**: Ma'lumotlarni tozalash
   ```python
   # NaN qiymatlarni tozalash
   data = data.dropna()
   
   # Outlier larni olib tashlash
   data = data[(data['volume'] > 0) & (data['close'] > 0)]
   ```

4. **Overfitting**: Walk-forward va out-of-sample testlash
   ```python
   # Har doim out-of-sample test qilish
   train_data = data[:'2020-12-31']
   test_data = data['2021-01-01':]
   
   # Train data da optimizatsiya
   best_params, _ = engine.optimize_strategy_parameters(...)
   
   # Test data da validation
   test_config = StrategyConfig(..., parameters=best_params)
   test_result = engine.run_backtest(test_config, test_data)
   ```

## API Reference

### Asosiy Klasslar

#### `ProBacktestingEngine`
Asosiy backtesting engine klassi

**Methods:**
- `run_backtest()` - Bitta strategiya uchun backtest
- `run_multiple_strategies()` - Bir nechta strategiya
- `optimize_strategy_parameters()` - Parameter optimizatsiya
- `run_monte_carlo_simulation()` - Monte Carlo simulyatsiya
- `run_walk_forward_analysis()` - Walk-forward analiz
- `run_multi_timeframe_analysis()` - Multi-timeframe analiz
- `run_portfolio_backtest()` - Portfolio backtest
- `calculate_statistical_significance()` - Statistical significance
- `generate_comprehensive_report()` - Hisobot yaratish

#### `StrategyConfig`
Strategiya konfiguratsiya klassi

**Attributes:**
- `name` - Strategiya nomi
- `strategy_function` - Strategiya funksiyasi
- `parameters` - Strategiya parametrlari
- `timeframe` - Vaqt freymi
- `initial_capital` - Boshlang'ich kapital
- `commission` - Komissiya stavkasi
- `slippage` - Slippage stavkasi

#### `BacktestResult`
Backtest natija klassi

**Attributes:**
- `strategy_name` - Strategiya nomi
- `total_return` - Jami foyda
- `annualized_return` - Yillik foyda
- `volatility` - Volatilite
- `sharpe_ratio` - Sharpe ratio
- `sortino_ratio` - Sortino ratio
- `calmar_ratio` - Calmar ratio
- `max_drawdown` - Maksimal drawdown
- `win_rate` - G'alaba foizi
- `profit_factor` - Foyda factor
- `total_trades` - Jami trade soni
- `equity_curve` - Equity curve
- `trades` - Trade ro'yxati

## Konkluziya

Pro Backtesting Engine - bu professional darajadagi backtesting tizimi bo'lib, trading strategiyaliarini chuqur tahlil qilish va optimallashtirish u barcha kerakli vositalarni ta'minlaydi. Bu tizim orqali siz:

1. **Chuqur Strategy Analysis**: Har bir strategiyani detail tahlil qilishingiz mumkin
2. **Risk Management**: Monte Carlo va walk-forward analiz bilan risklarni baholashingiz mumkin
3. **Parameter Optimization**: Turli algoritmlar bilan eng yaxshi parametrlarni topishingiz mumkin
4. **Portfolio Management**: Bir nechta aktivli portfelni test qilishingiz mumkin
5. **Statistical Validation**: Statistical significance testlar bilan natijalarning ishonchliligini tekshirishingiz mumkin

Bu engine bilan siz professional darajadagi backtesting analizlari o'tkaza olasiz va trading qarorlarini ma'lumotlar asosida qabul qila olasiz.

---

**Eslatma**: Bu documentation Pro Backtesting Engine v1.0.0 uchun mo'ljallangan. Keyingi versiyalarda qo'shimcha funksiyalar va yaxshilanishlar bo'lishi mumkin.