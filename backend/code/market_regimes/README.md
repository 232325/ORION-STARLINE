# Market Regime Detection va Cross-Asset Correlation Learning

Ushbu loyiha market rejimlarini aniqlash va cross-asset correlation tahlil qilish uchun qurilgan kompleks tizimdir. Tizim real-time market regime detection, correlation learning, va adaptive trading strategiesni o'z ichiga oladi.

## 🏗️ Tizim Arxitekturasi

### Asosiy Komponentlar

1. **Regime Detection Module** (`regime_detection.py`)
   - Trending market detection
   - Ranging market identification  
   - High/Low volatility regime detection
   - Crisis regime identification
   - Hidden Markov Models (HMM) integration

2. **Cross-Asset Correlation Learning** (`correlation_learning.py`)
   - Dynamic correlation modeling
   - Correlation regime detection
   - Cross-asset factor models
   - Correlation clustering
   - Correlation forecasting

3. **Adaptive Strategies** (`adaptive_strategies.py`)
   - Regime-adaptive trading strategies
   - Dynamic risk management
   - Adaptive position sizing
   - Multi-regime portfolio construction

4. **Implementation Framework** (`implementation_framework.py`)
   - Real-time regime detection
   - Regime-based strategy switching
   - Performance attribution by regime
   - Regime-aware backtesting
   - Dynamic strategy selection

5. **Configuration System** (`config.py`)
   - Predefined regime preferences
   - Strategy configurations
   - Risk management settings
   - Asset universe definitions

## 🚀 O'rnatish va Ishga Tushirish

### Talablar

```python
# Kerek kutubxonalar
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
scipy>=1.7.0
matplotlib>=3.4.0
seaborn>=0.11.0
```

### Asosiy Foydalanish

```python
from market_regimes import MarketRegimeSystemDemo

# Demo yaratish
demo = MarketRegimeSystemDemo("default")

# To'li tahlil o'tkazish
results = demo.run_complete_demo(
    n_days=1000,      # Kunlar soni
    n_assets=10,      # Assetlar soni
    save_results=True # Natijalarni saqlash
)
```

### Konfiguratsiya Tiplari

```python
# Konservativ konfiguratsiya (kam risk)
demo_conservative = MarketRegimeSystemDemo("conservative")

# Agresif konfiguratsiya (yuqori return)
demo_aggressive = MarketRegimeSystemDemo("aggressive")

# Default konfiguratsiya
demo_default = MarketRegimeSystemDemo("default")
```

## 📊 Market Regime Detection

### Rejim Tiplari

Tizim quyidagi market rejimlarini aniqlaydi:

1. **Trending Market**: Trend-following strategiyalar uchun optimal
2. **Ranging Market**: Mean-reversion strategiyalar uchun optimal
3. **High Volatility**: Kamaytirilgan pozitsiya o'lchamlari kerak
4. **Low Volatility**: Ko'proq leverage va katta pozitsiyalar mumkin
5. **Crisis**: Defensive strategiyalar va risk kamaytirish

### HMM Regime Detection

```python
from market_regimes import HiddenMarkovRegimeDetector

# HMM model yaratish
hmm_detector = HiddenMarkovRegimeDetector(n_regimes=3)

# Model o'rgatish
hmm_detector.fit(market_data)

# Rejimlarni bashorat qilish
predicted_regimes = hmm_detector.predict_regimes(market_data)

# Ehtimolliklarni olish
regime_probabilities = hmm_detector.get_regime_probabilities(market_data)
```

### Regime Indicators

```python
# Trend detection
trend_signals = detector.detect_trending_market(prices)

# Volatility regime
vol_regimes = detector.detect_volatility_regime(returns)

# Crisis detection
crisis_signals = detector.detect_crisis_regime(returns)

# Joriy rejimni olish
current_regime = detector.get_current_regime(prices)
```

## 📈 Cross-Asset Correlation Learning

### Dynamic Correlation Modeling

```python
from market_regimes import DynamicCorrelationModel

# Dynamic correlation model
dyn_corr = DynamicCorrelationModel(window_size=60)

# Rolling correlation matrix
rolling_corr = dyn_corr.rolling_correlation_matrix(returns)

# Correlation stability analysis
stability_analysis = dyn_corr.correlation_stability_analysis(rolling_corr)
```

### Correlation Regime Detection

```python
from market_regimes import CorrelationRegimeDetector

# Correlation regime detector
corr_detector = CorrelationRegimeDetector(n_regimes=3)

# Correlation rejimlarini aniqlash
correlation_regimes = corr_detector.detect_correlation_regimes(returns, window=60)
```

### Factor Model

```python
from market_regimes import CrossAssetFactorModel

# Factor model yaratish
factor_model = CrossAssetFactorModel(n_factors=5, method='pca')

# Model o'rgatish
factor_results = factor_model.fit_factor_model(returns)

# Factor forecast qilish
factor_forecasts = factor_model.forecast_factor_returns(recent_returns, horizon=5)
```

### Correlation Clustering

```python
from market_regimes import CorrelationClustering

# Clustering
clusterer = CorrelationClustering()
clustering_results = clusterer.cluster_assets_by_correlation(returns)

# Rejim-specific clustering
regime_clusters = clusterer.get_regime_specific_clusters(returns, regimes)
```

## 🎯 Adaptive Strategies

### Strategy Base Class

```python
from market_regimes import RegimeAdaptiveStrategy

class MyStrategy(RegimeAdaptiveStrategy):
    def __init__(self):
        regime_preferences = {
            "Trending": {'lookback': 30},
            "Ranging": {'lookback': 15}
        }
        super().__init__("MyStrategy", regime_preferences)
    
    def generate_signals(self, data, regime):
        # Strategy logic here
        signals = {}
        # ...
        return signals
    
    def calculate_position_size(self, signal, risk_budget, regime):
        # Position sizing logic here
        return position_size
```

### Built-in Strategies

#### Trend Following Strategy

```python
from market_regimes import TrendFollowingStrategy

trend_strategy = TrendFollowingStrategy(
    lookback_period=50,
    momentum_threshold=0.02
)

signals = trend_strategy.generate_signals(market_data, current_regime)
```

#### Mean Reversion Strategy

```python
from market_regimes import MeanReversionStrategy

mean_rev_strategy = MeanReversionStrategy(
    lookback_period=20,
    std_multiplier=2.0
)

signals = mean_rev_strategy.generate_signals(market_data, current_regime)
```

#### Volatility Targeting Strategy

```python
from market_regimes import VolatilityTargetingStrategy

vol_strategy = VolatilityTargetingStrategy(
    target_volatility=0.15,
    lookback_period=60
)

signals = vol_strategy.generate_signals(market_data, current_regime)
```

### Dynamic Risk Manager

```python
from market_regimes import DynamicRiskManager

risk_manager = DynamicRiskManager(
    max_portfolio_risk=0.02,
    var_confidence=0.95
)

# Position limits hisoblash
position_limits = risk_manager.calculate_position_limits(
    portfolio_value, correlation_matrix, current_regime
)

# Portfolio VaR hisoblash
portfolio_var = risk_manager.calculate_portfolio_var(returns, 0.95)

# Dynamic risk budgeting
risk_budget = risk_manager.dynamic_risk_budgeting(portfolio_returns, current_regime)
```

### Adaptive Portfolio Manager

```python
from market_regimes import AdaptivePortfolioManager

portfolio_manager = AdaptivePortfolioManager(
    strategies=[trend_strategy, mean_rev_strategy, vol_strategy],
    risk_manager=risk_manager
)

# Optimal strategy tanlash
optimal_strategy = portfolio_manager.select_optimal_strategy(
    market_data, current_regime, historical_performance
)

# Rejim weights allokatsiya
regime_weights = portfolio_manager.allocate_regime_weights(regime_history)
```

## 🔄 Real-Time Implementation

### Real-Time Regime Detector

```python
from market_regimes import RealTimeRegimeDetector

# Real-time detector
detector = RealTimeRegimeDetector(data_buffer_size=1000)

# Algorithm registrar
detector.register_detection_algorithm('trend_detection', trend_algorithm)
detector.register_detection_algorithm('volatility_detection', vol_algorithm)

# Real-time ma'lumot qo'shish
data_point = MarketDataPoint(
    timestamp=datetime.now(),
    symbol='AAPL',
    price=150.0,
    volume=1000000
)
detector.add_market_data(data_point)

# Rejim aniqlash
regime_signal = detector.detect_regime_realtime(symbols)

# Real-time loop ishga tushirish
detector.start_realtime_detection(symbols)
```

### Regime-Aware Backtester

```python
from market_regimes import RegimeAwareBacktester

backtester = RegimeAwareBacktester(initial_capital=100000)

# Strategy functions
strategy_functions = {
    'Trending': trending_strategy,
    'Ranging': mean_reversion_strategy,
    'Crisis': defensive_strategy
}

# Backtest o'tkazish
results = backtester.run_backtest(
    market_data, regime_data, strategy_functions
)
```

### System Integration

```python
from market_regimes import SystemIntegration

# Tizim yaratish
system = SystemIntegration()

# Strategiyalarni ro'yxatdan o'tkazish
strategies = {
    'Trending': trending_strategy_func,
    'Ranging': mean_reversion_strategy_func
}
system.register_strategies(strategies)

# Ma'lumot feed sozlamas
system.setup_market_data_feed("simulated")

# Tizimni ishga tushirish
system.start_system()

# Tizim statusini olish
status = system.get_system_status()
```

## ⚙️ Konfiguratsiya

### Asosiy Konfiguratsiya

```python
from market_regimes.config import get_default_config

config = get_default_config()

# Konfiguratsiya parametrlari
print(config.regime_detection.lookback_window)
print(config.strategy.max_portfolio_risk)
print(config.risk.max_drawdown_limit)
```

### Predefined Preferences

```python
from market_regimes.config import RegimePreferences

# Trend following preferences
trend_prefs = RegimePreferences.get_trend_following_preferences()

# Mean reversion preferences  
mean_rev_prefs = RegimePreferences.get_mean_reversion_preferences()

# Volatility targeting preferences
vol_prefs = RegimePreferences.get_volatility_targeting_preferences()
```

### Asset Universe

```python
from market_regimes.config import AssetUniverse

# Equity assets
equity_assets = AssetUniverse.get_equity_universe()

# Multi-asset universe
multi_asset = AssetUniverse.get_multi_asset_universe()

# Sector ETFs
sector_etfs = AssetUniverse.get_sector_etfs()
```

### Performance Benchmarks

```python
from market_regimes.config import PerformanceBenchmarks

benchmarks = PerformanceBenchmarks.get_benchmarks()

# Trending market benchmarks
trending_benchmarks = benchmarks["Trending"]
```

## 📋 Demo va Namuna

### Quick Start Demo

```python
# Tez demo
python demo.py
```

### Custom Demo

```python
from market_regimes import MarketRegimeSystemDemo

# O'z konfiguratsiyangiz bilan demo
demo = MarketRegimeSystemDemo("conservative")

# 2 yillik ma'lumotlar bilan tahlil
results = demo.run_complete_demo(
    n_days=500,
    n_assets=15,
    save_results=True
)

# Natijalarni ko'rish
print(results['report'])
```

### Namuna Kodlar

#### Asosiy Regime Detection

```python
import pandas as pd
import numpy as np
from market_regimes import RegimeDetector

# Sample data
dates = pd.date_range('2020-01-01', periods=1000, freq='D')
prices = pd.DataFrame(
    np.random.randn(1000, 3).cumsum(axis=0) + 100,
    index=dates,
    columns=['AAPL', 'MSFT', 'GOOGL']
)

# Regime detection
detector = RegimeDetector()
regimes = detector.detect_all_regimes(prices)
current_regime = detector.get_current_regime(prices)

print(f"Current regime: {current_regime}")
```

#### Cross-Asset Correlation

```python
from market_regimes import DynamicCorrelationModel

# Dynamic correlation
dyn_corr = DynamicCorrelationModel(window_size=60)
rolling_corr = dyn_corr.rolling_correlation_matrix(returns)

# Stability analysis
stability = dyn_corr.correlation_stability_analysis(rolling_corr)
```

#### Strategy Backtesting

```python
from market_regimes import RegimeAwareBacktester

backtester = RegimeAwareBacktester(initial_capital=100000)

# Simple strategy functions
def trending_strategy(market_state):
    return {'AAPL': {'action': 'BUY', 'quantity': 100}}

# Run backtest
results = backtester.run_backtest(
    market_data, regime_data, {'Trending': trending_strategy}
)

print(f"Total return: {results['performance_metrics']['total_return']:.2%}")
```

## 📊 Performance Metrics

### Risk Metrics

- **VaR (Value at Risk)**: Portfel yo'qotish ehtimoli
- **Expected Shortfall**: VaR dan ortiq yo'qotishlar o'rtacha qiymati
- **Maximum Drawdown**: Eng katta pasayish
- **Sharpe Ratio**: Risk-adjusted return
- **Sortino Ratio**: Negative deviation-adjusted return

### Regime Performance

- **Total Return by Regime**: Har bir rejim uchun umumiy return
- **Sharpe Ratio by Regime**: Rejim-specific Sharpe ratios
- **Win Rate by Regime**: Rejim-specific g'oliblik foizi
- **Volatility by Regime**: Rejim-specific volatility

### Strategy Performance

- **Strategy Attribution**: Har bir strategiya hissasi
- **Regime-Adaptive Performance**: Rejimga moslashgan natijalar
- **Risk-Adjusted Returns**: Risk-adjusted strategy returns

## 🛠️ Advanced Features

### Custom Indicators

```python
def custom_trend_indicator(prices, window=20):
    # Custom trend calculation
    slope = calculate_slope(prices, window)
    return slope > threshold

# Register custom indicator
detector.register_detection_algorithm('custom_trend', custom_trend_indicator)
```

### Factor Model Customization

```python
# Custom factor extraction
factor_model = CrossAssetFactorModel(
    n_factors=10,
    method='factor_analysis'  # or 'pca'
)
```

### Risk Scenario Testing

```python
from market_regimes.config import RiskManagementConfig

# Stress test scenarios
risk_config = RiskManagementConfig(
    stress_test_scenarios=[
        {
            'name': 'Market Crash',
            'market_shock': -0.20,
            'volatility_multiplier': 3.0
        }
    ]
)
```

## 🔧 Troubleshooting

### Tez-tez uchraydigan muammolar

1. **Import Error**: `scipy` kutubxonasini o'rnating
   ```bash
   pip install scipy
   ```

2. **Memory Issues**: Katta datasetlar bilan ishlashda
   ```python
   detector = RegimeDetector(lookback_window=100)  # Kamaytiring
   ```

3. **Data Quality**: Yo'q ma'lumotlar uchun
   ```python
   prices = prices.dropna()  # NaN larni olib tashlang
   ```

### Performance Optimization

1. **Parallel Processing**
   ```python
   config.parallel_processing = True
   config.max_workers = 4
   ```

2. **Caching Results**
   ```python
   config.cache_results = True
   ```

3. **Data Buffer Size**
   ```python
   detector = RealTimeRegimeDetector(data_buffer_size=500)
   ```

## 📁 Fayl Strukturasi

```
market_regimes/
├── __init__.py              # Package initialization
├── regime_detection.py      # Market regime detection
├── correlation_learning.py  # Cross-asset correlation
├── adaptive_strategies.py   # Regime-adaptive strategies
├── implementation_framework.py  # Real-time system
├── config.py               # Configuration system
├── demo.py                 # Comprehensive demo
└── README.md               # This file
```

## 📈 Natijalar

Demo natijalar `output/` papkasida saqlanadi:

- `comprehensive_report.txt`: Executive summary
- `detailed_results.json`: To'li tahlil natijalari
- `market_regime_analysis.png`: Asosiy tahlil grafiklari
- `correlation_analysis.png`: Correlation tahlil grafiklari

## 🤝 Hissa Qo'shish

1. Fork qiling
2. Feature branch yarating (`git checkout -b feature/yanghi-xususiyat`)
3. O'zgarishlaringizni commit qiling (`git commit -am 'Yanghi xususiyat qo'shish'`)
4. Branch ni push qiling (`git push origin feature/yanghi-xususiyat`)
5. Pull Request yuboring

## 📄 Litsenziya

Ushbu loyiha MIT litsenziyasi ostida tarqatiladi.

## 🆘 Yordam

Savollar uchun:
- Issue yarating GitHub da
- Documentation ni o'qib chiqing
- Demo fayllarni ko'ring

---

**Market Regime Detection va Cross-Asset Correlation Learning tizimi** - Quantitative Finance uchun professional-grade yechim.