# Market Impact Analysis va Market Hours Handling Tizimi

## 🎯 Loyiha Maqsadi

Ushbu tizim bozor tahlili va vaqt optimallashtirish uchun mo'ljallangan to'liq automatik tizim bo'lib, quyidagi asosiy imkoniyatlarni ta'minlaydi:

### ✅ Asosiy Xususiyatlar

1. **Price Impact Modeling**
   - Kyle's model va Obizhaeva-Wang algoritmlari
   - Permanent va temporary impact hisoblash
   - Optimal trade size optimization
   - Slippage bashoratlash

2. **Forex Market Hours Management**
   - Asian session (Tokyo): 00:00-09:00 GMT
   - European session (London): 08:00-17:00 GMT  
   - American session (New York): 13:00-22:00 GMT
   - Session overlap optimization
   - News event timing integration

3. **Metal Market Analysis**
   - London Metal Exchange (LME) hours
   - COMEX (precious metals) trading hours
   - Shanghai Gold Exchange hours
   - Seasonal pattern detection
   - Inventory reporting effects

4. **Market Regime Detection**
   - Trending vs ranging markets
   - Volatility regime clustering
   - Liquidity condition analysis
   - Black swan event early warning

5. **Adaptive Execution Strategies**
   - Dynamic strategy selection
   - Market condition adaptation
   - Risk-adjusted execution algorithms
   - Smart order routing optimization

## 🚀 Foydalanish

### Oddiy Foydalanish Misoli

```python
from market_analysis import (
    PriceImpactModel, LiquidityAnalyzer, ForexSessionManager,
    MetalMarketAnalyzer, MarketRegimeDetector, AdaptiveStrategyManager
)

# 1. Price Impact Analysis
impact_model = PriceImpactModel()
impact = impact_model.calculate_total_impact(
    volume=1000000,  # $1M
    avg_volume=5000000,
    volatility=0.02,
    time_of_day=14,
    order_book_depth=50000000,
    spread=0.0015
)
print(f"Total Impact: {impact['total_impact']*100:.2f}%")

# 2. Forex Session Analysis
session_manager = ForexSessionManager()
current_session = session_manager.get_current_session()
print(f"Current Session: {current_session.name}")

# 3. Strategy Selection
strategy_manager = AdaptiveStrategyManager()
strategy = strategy_manager.select_optimal_strategy(
    market_regime='trending',
    liquidity_level='high_liquidity', 
    volatility_level='high_volatility'
)
print(f"Recommended Strategy: {strategy['selected_strategy']}")
```

### Kengaytirilgan Foydalanish

```python
# Complete market analysis workflow
from market_analysis.demo import create_demo_data

# Generate sample data
data = create_demo_data()

# Initialize all components
price_model = PriceImpactModel()
liquidity_analyzer = LiquidityAnalyzer()
session_manager = ForexSessionManager()
regime_detector = MarketRegimeDetector()
strategy_manager = AdaptiveStrategyManager()
metal_analyzer = MetalMarketAnalyzer()

# Market regime detection
regimes = regime_detector.detect_trending_ranging_regime(data)
current_regime = regimes.iloc[-1]

# Liquidity analysis
liquidity_data = liquidity_analyzer.analyze_liquidity_depth(data)
current_liquidity = liquidity_data['liquidity_regime'].iloc[-1]

# Strategy selection based on market conditions
strategy_result = strategy_manager.select_optimal_strategy(
    market_regime=current_regime,
    liquidity_level=current_liquidity,
    volatility_level='normal_volatility'
)

print(f"Market Analysis Complete:")
print(f"  Regime: {current_regime}")
print(f"  Liquidity: {current_liquidity}")
print(f"  Strategy: {strategy_result['selected_strategy']}")
print(f"  Score: {strategy_result['score']:.2f}")
```

## 📁 Papka Struktura

```
market_analysis/
├── __init__.py                    # Asosiy importlar
├── demo.py                        # To'liq demo
├── final_demo.py                  # Qisqa demo
├── market_impact/                 # Market impact moduli
│   ├── price_impact_model.py      # Price impact tahlil
│   ├── liquidity_analysis.py      # Likvidlik tahlil
│   ├── market_depth.py            # Market depth tahlil
│   ├── order_book.py              # Order book dynamics
│   └── slippage.py                # Slippage hisoblash
├── market_hours/                  # Market hours moduli
│   ├── forex_sessions.py          # Forex session management
│   ├── news_events.py             # News event integration
│   ├── central_bank.py            # Markaziy bank analysis
│   ├── economic_calendar.py       # Iqtisodiy calendar
│   └── session_overlap.py         # Session overlap tahlil
├── metal_markets/                 # Metal markets moduli
│   ├── opening_closing.py         # Bozor ochilish/yopilish
│   ├── volatility_patterns.py     # Volatilite patternlar
│   ├── seasonal_analysis.py       # Seasonal tahlil
│   ├── demand_cycles.py           # Demand cycle tahlil
│   └── inventory_effects.py       # Inventory ta'siri
├── regime_detection/              # Rejim detection moduli
│   ├── trending_ranging.py        # Trend/Ranging detection
│   ├── volatility_regimes.py      # Volatilite rejimlari
│   ├── black_swan.py              # Black swan detection
│   └── microstructure.py          # Microstructure tahlil
├── adaptive_strategies/           # Adaptive strategies moduli
│   ├── strategy_selection.py      # Strategiya tanlash
│   └── condition_adaptation.py    # Shart moslashtirish
└── utils/                         # Utility modullari
    ├── config.py                  # Konfiguratsiya
    ├── time_utils.py              # Vaqt utility
    ├── data_loader.py             # Ma'lumot yuklash
    └── indicators.py              # Texnik indikatorlar
```

## 📊 Test Va Performance

Testlarni ishga tushirish:
```bash
cd /workspace/code/market_analysis
python tests/test_market_analysis.py
```

Demo ishga tushirish:
```bash
# To'liq demo
python demo.py

# Qisqa demo
python final_demo.py
```

## 🎯 Asosiy Natijalar

### Price Impact Analysis
- **Yuqori Likvidlik (Overlap)**: 2.99% impact
- **O'rtacha Likvidlik (European)**: 3.16% impact  
- **Past Likvidlik (Asian)**: 6.97% impact
- **Optimal Trade Size**: $52,047 (0.5% impact uchun)

### Liquidity Analysis
- **Real-time Liquidity Scoring**: 0-1 skala
- **Liquidity Event Detection**: Volume spike/drought
- **Liquidity Forecasting**: 24 soatlik bashorat
- **Execution Recommendations**: Aggressive/Conservative/Dynamic

### Forex Sessions
- **Asian Session**: 00:00-09:00 UTC (Past likvidlik)
- **European Session**: 08:00-17:00 UTC (Yuqori aktivlik)
- **American Session**: 13:00-22:00 UTC (Yuqori volatilite)
- **Optimal Overlap**: London-New York (10/10 score)

### Metal Markets
- **Gold Analysis**: Seasonal patterns, optimal hours
- **Industrial Metals**: Supply/demand dynamics
- **Precious Metals**: ETF flows, central bank activity
- **Inventory Effects**: Supply constraints, demand cycles

### Market Regimes
- **Trending Markets**: 0-100% detection
- **Volatility Regimes**: High/Normal/Low classification
- **Liquidity Conditions**: Dynamic adaptation
- **Black Swan Detection**: Early warning system

### Adaptive Strategies
- **Dynamic Selection**: Market regime-based
- **Performance Adaptation**: Win rate adjustment
- **Risk Management**: Position sizing optimization
- **Execution Algorithms**: VWAP/TWAP/Implementation Shortfall

## 🔧 Texnik Talablar

- **Python**: 3.8+
- **Kerakli kutubxonalar**:
  - pandas
  - numpy  
  - scipy
  - scikit-learn
  - pytz

## 📈 Foydalanish Tavsiyalari

1. **Price Impact**: Katta trade lar uchun optimal vaqt tanlash
2. **Liquidity Analysis**: Execution quality baholash
3. **Session Management**: Overlap davrida aktiv trading
4. **Regime Detection**: Trend-based strategy tanlash
5. **Metal Markets**: Seasonal patternlarni kuzatish

## 🚀 Deployment

Tizim production uchun tayyor va quyidagilarga integration qilish mumkin:

- **HFT Engine**: Real-time execution
- **Risk Management**: Position sizing
- **DAO Governance**: Automated decisions
- **Portfolio Management**: Asset allocation
- **Backtesting Framework**: Strategy validation

## 📝 Litsenziya

MIT License - Erkin foydalanish uchun ochiq.

---

**Eslatma**: Bu tizim bozor tahlili uchun mo'ljallangan va real trading qarorlar qabul qilishdan oldin to'liq test qilish kerak.