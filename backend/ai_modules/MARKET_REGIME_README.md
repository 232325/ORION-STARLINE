# Bozor Rejimini Aniqlash Tizimi (Market Regime Detection System)

Bu tizim bozor rejimlarini aniqlaydi vaunga mos strategiyalarni tanlaydi.

## Asosiy xususiyatlar

### 🎯 Bozor rejim turlari
- **Bull Market** - Ko'tarilish trendi
- **Bear Market** - Pasayish trendi
- **Sideways Market** - Yon yo'nalish
- **High Volatility** - Yuqori o'zgaruvchanlik
- **Low Volatility** - Past o'zgaruvchanlik
- **Breakout Market** - Daraxt chiqish
- **Reversal Market** - Teskarilanish
- **Consolidation** - Konsolidatsiya

### 📊 Texnik indikatori
- **Trend indikatori**: SMA, EMA, MACD, ADX
- **Momentum indikatori**: RSI, Stochastic, Williams %R, Momentum, ROC
- **Volatility indikatori**: ATR, Bollinger Bands
- **Volume indikatori**: OBV, AD, Volume ratio
- **Support/Resistance**: Dinamik support/resistance darajalar

### 🎮 Strategiya turlari
- **Trend Following** - Trendni kuzatish
- **Mean Reversion** - O'rtacha qiymatga qaytish
- **Momentum** - Impuls strategiya
- **Breakout** - Daraxt chiqish
- **Scalping** - Tez savdo
- **Swing Trading** - Swing savdo
- **Risk Parity** - Risk pariteti
- **Dollar Cost Averaging** - O'rtacha xarid
- **Volatility Arbitrage** - Volatilite arbitraji

## Ishlatish

### 1. Bozor rejimini aniqlash

```python
from market_regime_detector import MarketRegimeDetector, RegimeConfig
import pandas as pd

# Ma'lumotlarni tayyorlash
data = pd.DataFrame({
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...],
    'volume': [...]
})

# Detektorni yaratish
detector = MarketRegimeDetector()

# Rejim aniqlash
result = detector.detect_regime(data)
print(f"Rejim: {result.regime.value}")
print(f"Ishonchlilik: {result.confidence:.2f}")
print(f"Indikatorlar: {result.indicators}")
```

### 2. Strategiya tanlash

```python
from strategy_switcher import StrategySwitcher

# Switcherni yaratish
switcher = StrategySwitcher()

# Eng yaxshi strategiyani tanlash
strategy = switcher.select_strategy(data)

if strategy:
    print(f"Tanlangan strategiya: {strategy.name}")
    
    # Trade signallarini yaratish
    signals = switcher.generate_trade_signals(strategy, data)
    for signal in signals:
        print(f"Signal: {signal['side']} {signal['symbol']} @ {signal['price']}")
```

### 3. Pozitsiya hajmini hisoblash

```python
# Pozitsiya hajmini hisoblash
account_value = 10000  # $10,000
position_size = switcher.calculate_position_size(strategy, data, account_value)
print(f"Pozitsiya hajmi: {position_size:.1%}")
```

### 4. Portfolio boshqaruv

```python
# Pozitsiyalarni yangilash
current_prices = {'BTCUSDT': 45000, 'ETHUSDT': 3000}
switcher.update_positions(current_prices)

# Portfolio metrikalari
metrics = switcher.calculate_portfolio_metrics()
print(f"Jami qiymat: ${metrics['total_value']:,.2f}")
print(f"jami PnL: ${metrics['total_pnl']:+.2f} ({metrics['total_pnl_pct']:+.2%})")
```

## Demo ishga tushirish

```bash
cd /workspace/orion-starline/backend/ai_modules
python market_regime_demo.py
```

## Natijalar

Demo ishga tushganda quyidagi ma'lumotlarni ko'rishingiz mumkin:

1. **Rejim aniqlash**: Har hafta uchun bozor rejimi
2. **Strategiya tanlash**: Rejimga mos strategiya
3. **Risk boshqaruv**: Pozitsiya hajmi va risk hisoblash
4. **Portfolio boshqaruv**: Aktiv pozitsiyalar va PnL
5. **Kengaytirilgan xususiyatlar**: Multi-timeframe tahlil, ML bashorat

## Konfiguratsiya

```python
from market_regime_detector import RegimeConfig

# Maxsus konfiguratsiya
config = RegimeConfig(
    trend_threshold=0.02,      # Trend uchun threshold
    volatility_threshold=0.02, # Volatilite uchun threshold
    volume_threshold=1.5,      # Volume uchun threshold
    ma_short_period=10,        # Qisqa MA periodi
    ma_long_period=50,         # Uzun MA periodi
    rsi_overbought=70,         # RSI overbought
    rsi_oversold=30,           # RSI oversold
    bollinger_period=20,       # Bollinger period
    bollinger_std=2.0          # Bollinger standard dev
)

detector = MarketRegimeDetector(config)
```

## Xususiyatlar

### 🧠 Machine Learning
- Random Forest modeli
- Historical ma'lumotlar bilan o'qitish
- Bashorat qilish funksiyasi
- **Eslatma**: sklearn kutubxonasi talab qilinadi

### 📈 Multi-timeframe tahlil
- 1h, 4h, 1d vaqt doiralari
- Har bir vaqt doirasi uchun alohida rejim
- Cross-timeframe tasdiqlash

### 🎯 Rejim o'zgarishlari kuzatuvi
- Real-time rejim o'zgarishlari
- O'tish statistikalari
- Persistence hisoblash

### 📊 Performance analytics
- Sharpe ratio
- Max drawdown
- Win rate
- Profit factor
- VaR 95%

## Xatolarni hal qilish

1. **sklearn mavjud emas**: ML xususiyatlari o'chiriladi, lekin asosiy funksiyalar ishlaydi
2. **Ma'lumotlar yetarli emas**: Minimal 20 ta qator kerak
3. **NaN qiymatlar**: Avtomatik tozalanadi

## Loyiha struktura

```
/workspace/orion-starline/backend/ai_modules/
├── market_regime_detector.py    # Asosiy rejim detektori
├── strategy_switcher.py         # Strategiya almashtirish
├── market_regime_demo.py        # Demo script
└── README.md                    # Ushbu fayl
```

## Keyingi qadamlar

1. **Real-time ma'lumotlar** integratsiyasi
2. **API integratsiyasi** (Binance, etc.)
3. **Web dashboard** yaratish
4. **Backtesting** funksiyasi
5. **Alert tizimi**

## Hissa qo'shish

1. Fork qiling
2. Feature branch yarating
3. O'zgarishlaringizni commit qiling
4. Pull request yarating

## Litsenziya

MIT License