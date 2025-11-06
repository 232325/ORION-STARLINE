# UI Modules - Advanced Trading Dashboard
## AI Trading Evolution - BOSQICH 9

**Yaratilgan sana:** 2025-11-04  
**Versiya:** 1.0.0  
**Jami kod:** 4,227 qator

---

## 📋 Umumiy Ma'lumot

BOSQICH 9 trading tizimi uchun to'liq UI backend modullarini taqdim etadi:
- Advanced backtesting va optimizatsiya
- Real-time trading monitoring
- Market intelligence va scanning
- Performance analytics
- Trade journaling
- Advanced charting va technical analysis

Barcha modullar REST API orqali mavjud va `main.py` ga integratsiya qilingan.

---

## 🗂️ Modullar Tarkibi

### 1. Backtesting Dashboard (`backtesting_dashboard.py` - 704 qator)

**Imkoniyatlar:**
- Interaktiv backtesting UI
- Parametr optimizatsiyasi (Grid Search, Random Search, Bayesian, Genetic)
- Walk-forward testing
- Monte Carlo simulation
- Equity curve visualization
- Performance metrics kalkulatsiyasi

**Asosiy Klaslar:**
- `BacktestConfig` - Backtest konfiguratsiyasi
- `BacktestResult` - Backtest natijalari
- `OptimizationResult` - Optimizatsiya natijalari
- `BacktestingDashboard` - Asosiy dashboard klassi

**API Endpoints:**
```
POST /api/v1/backtesting/run - Backtest ishga tushirish
GET  /api/v1/backtesting/list - Barcha backtestlar ro'yxati
GET  /api/v1/backtesting/{id} - Backtest ma'lumotlari
```

**Misol:**
```python
from ui.backtesting_dashboard import backtesting_dashboard, BacktestConfig

config = BacktestConfig(
    strategy_name="MomentumStrategy",
    symbol="BTC/USDT",
    timeframe="1h",
    start_date=datetime.now() - timedelta(days=365),
    end_date=datetime.now(),
    initial_capital=10000.0,
    parameters={'period': 20, 'threshold': 0.02}
)

result = await backtesting_dashboard.run_backtest(config)
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
```

---

### 2. Live Trading Dashboard (`live_trading_dashboard.py` - 707 qator)

**Imkoniyatlar:**
- Real-time position monitoring
- Live PnL tracking
- Order book visualization
- Trade execution monitoring
- Portfolio allocation
- Real-time risk metrics

**Asosiy Klaslar:**
- `Position` - Trading position
- `Order` - Trading order
- `PortfolioSnapshot` - Portfolio holati
- `LiveTradingDashboard` - Real-time dashboard

**API Endpoints:**
```
GET  /api/v1/dashboard/portfolio - Portfolio holati
GET  /api/v1/dashboard/positions - Ochiq positionlar
POST /api/v1/dashboard/position/open - Position ochish
POST /api/v1/dashboard/position/{id}/close - Position yopish
```

**Misol:**
```python
from ui.live_trading_dashboard import live_dashboard, PositionSide

# Start dashboard
await live_dashboard.start()

# Open position
position = await live_dashboard.open_position(
    symbol="BTC/USDT",
    side=PositionSide.LONG,
    size=0.1,
    leverage=2.0,
    stop_loss=45000.0,
    take_profit=55000.0
)

# Get portfolio
snapshot = live_dashboard.get_portfolio_snapshot()
print(f"Total Value: ${snapshot.total_value:.2f}")
```

---

### 3. Market Intelligence (`market_intelligence.py` - 707 qator)

**Imkoniyatlar:**
- Market heatmaps
- Correlation analysis
- Market scanner
- Sector rotation
- Volume profile
- Order flow imbalance

**Asosiy Klaslar:**
- `MarketData` - Market ma'lumotlari
- `CorrelationMatrix` - Correlation matrix
- `ScannerResult` - Scanner natijasi
- `MarketIntelligence` - Market tahlil tizimi

**API Endpoints:**
```
GET  /api/v1/market/heatmap - Market heatmap
GET  /api/v1/market/correlation - Correlation matrix
POST /api/v1/market/scan - Market scanning
GET  /api/v1/market/overview - Market overview
```

**Misol:**
```python
from ui.market_intelligence import market_intelligence, ScannerCondition

# Market heatmap
heatmap = await market_intelligence.get_market_heatmap(metric="change_24h")

# Correlation
correlation = await market_intelligence.calculate_correlation_matrix(
    ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
)

# Scan market
results = await market_intelligence.scan_market([
    ScannerCondition.RSI_OVERSOLD,
    ScannerCondition.VOLUME_SPIKE
])
```

---

### 4. Performance Analytics (`performance_analytics.py` - 676 qator)

**Imkoniyatlar:**
- Sharpe ratio calculation
- Sortino ratio
- Maximum drawdown analysis
- Calmar ratio
- Win/loss analysis
- Risk-adjusted returns

**Asosiy Klaslar:**
- `TradeRecord` - Trade yozuvi
- `PerformanceMetrics` - Performance metrikalari
- `DrawdownAnalysis` - Drawdown tahlili
- `PerformanceAnalytics` - Performance tahlil tizimi

**API Endpoints:**
```
GET /api/v1/analytics/performance - Performance metrics
GET /api/v1/analytics/drawdown - Drawdown analysis
GET /api/v1/analytics/equity-curve - Equity curve
```

**Misol:**
```python
from ui.performance_analytics import performance_analytics

# Calculate metrics
metrics = await performance_analytics.calculate_performance_metrics()
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
print(f"Max Drawdown: {metrics.max_drawdown:.2%}")

# Drawdown analysis
dd = await performance_analytics.analyze_drawdown()
print(f"Max DD Duration: {dd.max_drawdown_duration} days")
```

---

### 5. Trade Journal (`trade_journal.py` - 675 qator)

**Imkoniyatlar:**
- Trade logging with notes
- Tags and categories
- Advanced filtering
- Search functionality
- Trade review system
- Pattern recognition

**Asosiy Klaslar:**
- `JournalEntry` - Trade journal yozuvi
- `JournalStats` - Journal statistikasi
- `TradeJournal` - Trade journal tizimi

**API Endpoints:**
```
GET /api/v1/journal/entries - Journal yozuvlari
GET /api/v1/journal/{id} - Journal yozuvi
GET /api/v1/journal/statistics - Journal statistika
```

**Misol:**
```python
from ui.trade_journal import trade_journal, TradeSetup

# Search entries
entries = await trade_journal.search_entries(
    symbol="BTC/USDT",
    setup=TradeSetup.BREAKOUT,
    limit=10
)

# Get statistics
stats = await trade_journal.get_statistics()
print(f"Win Rate by Setup: {stats.setup_distribution}")

# Get insights
insights = await trade_journal.get_insights()
```

---

### 6. Advanced Charts (`advanced_charts.py` - 758 qator)

**Imkoniyatlar:**
- TradingView widget integration
- Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR)
- Chart patterns detection
- Drawing tools support
- Multi-timeframe analysis

**Asosiy Klaslar:**
- `OHLCV` - Candlestick data
- `Indicator` - Technical indicator
- `ChartPattern` - Chart pattern
- `AdvancedCharts` - Charting tizimi

**API Endpoints:**
```
GET /api/v1/charts/data - OHLCV data
GET /api/v1/charts/indicator - Technical indicator
GET /api/v1/charts/patterns - Pattern detection
GET /api/v1/charts/mtf-analysis - Multi-timeframe analysis
```

**Misol:**
```python
from ui.advanced_charts import advanced_charts, Timeframe, IndicatorType

# Get chart data
candles = await advanced_charts.get_chart_data(
    "BTC/USDT", 
    Timeframe.H1, 
    limit=100
)

# Calculate RSI
rsi = await advanced_charts.calculate_indicator(
    "BTC/USDT",
    Timeframe.H1,
    IndicatorType.RSI,
    {'period': 14}
)

# Detect patterns
patterns = await advanced_charts.detect_patterns("BTC/USDT", Timeframe.H1)
```

---

## 🚀 Ishga Tushirish

### 1. Modullarni Import Qilish

```python
from ui.backtesting_dashboard import backtesting_dashboard
from ui.live_trading_dashboard import live_dashboard
from ui.market_intelligence import market_intelligence
from ui.performance_analytics import performance_analytics
from ui.trade_journal import trade_journal
from ui.advanced_charts import advanced_charts
```

### 2. API Server Ishga Tushirish

```bash
# Development
python main.py

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. API Documentation

FastAPI avtomatik API dokumentatsiya yaratadi:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📊 Performance Metrikalari

### Backtesting Metrics
- **Total Return** - Umumiy daromad
- **Sharpe Ratio** - Risk-adjusted return
- **Sortino Ratio** - Downside risk-adjusted return
- **Calmar Ratio** - Return / Max Drawdown
- **Max Drawdown** - Eng katta pasayish
- **Win Rate** - Muvaffaqiyatli tradelar foizi
- **Profit Factor** - Daromad / Zarar

### Live Trading Metrics
- **Total PnL** - Umumiy foyda/zarar
- **Daily PnL** - Kunlik foyda/zarar
- **Portfolio Value** - Portfolio qiymati
- **Margin Ratio** - Margin nisbati
- **Exposure** - Long/Short exposure

### Risk Metrics
- **VaR (Value at Risk)** - 95% va 99% darajada
- **CVaR (Conditional VaR)** - Tail risk
- **Volatility** - Narx o'zgaruvchanligi
- **Beta** - Market bilan korrelyatsiya

---

## 🔧 Konfiguratsiya

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost/trading

# Redis Cache (optional)
REDIS_URL=redis://localhost:6379

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

---

## 📈 Statistika

| Modul | Qatorlar | Klasslar | Funksiyalar |
|-------|----------|----------|-------------|
| Backtesting Dashboard | 704 | 5 | 12 |
| Live Trading Dashboard | 707 | 5 | 15 |
| Market Intelligence | 707 | 5 | 10 |
| Performance Analytics | 676 | 4 | 8 |
| Trade Journal | 675 | 4 | 11 |
| Advanced Charts | 758 | 6 | 14 |
| **JAMI** | **4,227** | **29** | **70** |

---

## 🧪 Testing

Har bir modul o'z test funksiyalariga ega:

```bash
# Test individual modules
python ui/backtesting_dashboard.py
python ui/live_trading_dashboard.py
python ui/market_intelligence.py
python ui/performance_analytics.py
python ui/trade_journal.py
python ui/advanced_charts.py

# Test API
pytest tests/test_ui_api.py
```

---

## 🔒 Security

- API key autentifikatsiya
- Rate limiting
- Input validation
- SQL injection himoyasi
- XSS himoyasi
- CORS sozlamalari

---

## 📝 API Examples

### Backtesting

```bash
# Run backtest
curl -X POST http://localhost:8000/api/v1/backtesting/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_name": "MomentumStrategy",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-12-31T23:59:59",
    "initial_capital": 10000,
    "parameters": {"period": 20, "threshold": 0.02}
  }'
```

### Live Dashboard

```bash
# Get portfolio
curl http://localhost:8000/api/v1/dashboard/portfolio

# Open position
curl -X POST http://localhost:8000/api/v1/dashboard/position/open \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC/USDT",
    "side": "long",
    "size": 0.1,
    "leverage": 2.0,
    "stop_loss": 45000.0,
    "take_profit": 55000.0
  }'
```

### Market Intelligence

```bash
# Get heatmap
curl "http://localhost:8000/api/v1/market/heatmap?metric=change_24h"

# Scan market
curl -X POST http://localhost:8000/api/v1/market/scan \
  -H "Content-Type: application/json" \
  -d '{"conditions": ["rsi_oversold", "volume_spike"]}'
```

---

## 🎯 Keyingi Qadamlar

### BOSQICH 10: Social Trading
- Copy trading engine
- Signal sharing platform
- Leaderboard system
- AutoML pipeline

### BOSQICH 11: Payment & Markets
- Stripe integration
- Forex market
- REITs trading
- Tax reporting

---

## 👨‍💻 Muallif

**MiniMax Agent**  
AI Trading Evolution - BOSQICH 9  
Sana: 2025-11-04

---

## 📄 License

Proprietary - AI Trading Evolution Platform

---

## 🤝 Support

Support uchun:
- Email: support@aitradingevolution.com
- Telegram: @ai_trading_support
- Discord: AI Trading Evolution

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-04  
**Status:** ✅ Production Ready
