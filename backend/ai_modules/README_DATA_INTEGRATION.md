# Real-time Data Integration System
# Real-time Ma'lumotlar Integratsiya Tizimi

Bu tizim bir nechta manbalardan real-time bozor ma'lumotlarini, yangiliklarni, sentiment ma'lumotlarini va boshqa moliyaviy ma'lumotlarni birlashtirib, comprehensive ma'lumotlar bazasi yaratishga mo'ljallangan.

## 🏗️ Arxitektura

### Asosiy Komponentalar

1. **Data Integration Engine** (`data_integration.py`)
   - Multiple data source management
   - Real-time data streaming
   - Data validation and caching
   - Consensus calculation

2. **Market Data Processor** (`market_data.py`)
   - Real-time market data processing
   - Technical analysis indicators
   - WebSocket streaming (Binance, Coinbase)
   - Multi-timeframe data support

3. **News Feed Manager** (`news_feed.py`)
   - News aggregation and sentiment analysis
   - Social media sentiment tracking
   - Economic calendar integration
   - Content analysis and ranking

## 🚀 Asosiy Funksiyalar

### 1. Market Data Live Feed
```python
from data_integration import DataIntegrationManager

manager = DataIntegrationManager()

# Real-time narx ma'lumotlari
price_data = await manager.get_comprehensive_market_data("AAPL")
print(f"AAPL narxi: ${price_data['consensus']['price']['mean']}")
```

### 2. News Integration
```python
from news_feed import NewsFeedManager

news_manager = NewsFeedManager()

# Yangiliklar sentiment analizi
sentiment = await news_manager.get_comprehensive_sentiment(["AAPL", "GOOGL"])
for symbol, metrics in sentiment.items():
    print(f"{symbol}: {metrics.overall_score:.3f} sentiment")
```

### 3. Technical Analysis Data
```python
# RSI, MACD, Bollinger Bands
indicators = processor.calculate_technical_indicators("AAPL")
print(f"RSI: {indicators['rsi'].value}")
print(f"MACD Signal: {indicators['macd'].signal}")
```

### 4. Portfolio Data Access
```python
# Portfolio holati
portfolio = await integration.get_portfolio_data("user_123")
positions = portfolio.get('positions', [])
for position in positions:
    print(f"{position['symbol']}: {position['unrealized_pnl']}")
```

### 5. Risk Analytics Integration
```python
# Portfolio risk hisoblash
risk_metrics = await risk_analytics.calculate_portfolio_risk("user_123", positions)
print(f"VaR 95%: {risk_metrics['var_95']:.2f}")
print(f"Sharpe Ratio: {risk_metrics['sharpe_ratio_estimate']:.2f}")
```

### 6. Signal Generation Integration
```python
# AI signals
signals = await signal_generator.generate_signals("AAPL")
for signal_type, signal_list in signals['signals'].items():
    if signal_list:
        print(f"{signal_type}: {len(signal_list)} signals")
```

### 7. Multi-timeframe Data
```python
# Ko'p vaqt intervali
multi_tf = integration.get_multi_timeframe_data("AAPL")
for timeframe, data in multi_tf.items():
    print(f"{timeframe}: {data.get('close', 0)}")
```

### 8. Economic Calendar Integration
```python
# Iqtisodiy kalendar
events = await integration.get_economic_calendar()
for event in events:
    print(f"{event.title} - {event.date}")
```

### 9. Sentiment Analysis Data
```python
# Market sentiment
sentiment_data = await integration.get_sentiment_data("AAPL")
fear_greed = sentiment_data['fear_greed_index']
mood = sentiment_data['market_mood']
print(f"F&G Index: {fear_greed}, Market Mood: {mood}")
```

### 10. Social Media Sentiment Tracking
```python
# Ijtimoiy tarmoq ma'lumotlari
social_posts = await news_manager.fetch_social_sentiment(["AAPL"], limit=50)
for post in social_posts[:5]:
    print(f"Platform: {post.platform}, Sentiment: {post.sentiment_score:.2f}")
```

## 📊 Data Sources

### Market Data
- **Yahoo Finance API** - Real-time va historical ma'lumotlar
- **Alpha Vantage** - Technical indicators va ma'lumotlar
- **IEX Cloud** - Real-time market data
- **Polygon.io** - High-frequency ma'lumotlar
- **Finnhub** - Financial data va news

### News Sources
- **NewsAPI** - General financial news
- **Finnhub News** - Symbol-specific news
- **Reuters API** - Breaking financial news
- **Bloomberg API** - Market data va news

### Social Media
- **Twitter API** - Real-time tweets va sentiment
- **Reddit API** - Investment community discussions
- **StockTwits** - Social trading sentiment

### Economic Data
- **FRED API** - Federal Reserve Economic Data
- **Yahoo Finance Economic Calendar** - Economic events
- **TradingView Economic Calendar** - Market-moving events

## 🔧 Sozlash va Ishga Tushirish

### 1. Dependencies O'rnatish
```bash
pip install -r requirements_data_integration.txt
```

### 2. Environment Variables
```bash
# .env fayl yarating
ALPHA_VANTAGE_KEY=your_api_key_here
FINNHUB_KEY=your_finnhub_key
POLYGON_KEY=your_polygon_key
NEWSAPI_KEY=your_newsapi_key
TWITTER_BEARER_TOKEN=your_twitter_token
```

### 3. Asosiy Foydalanish
```python
import asyncio
from data_integration import RealTimeDataIntegration, DataConfig

async def main():
    config = DataConfig(
        alpha_vantage_key="your_key",
        finnhub_key="your_key",
        enabled_sources=['yahoo', 'alpha_vantage', 'finnhub']
    )
    
    integration = RealTimeDataIntegration(config)
    
    # Ma'lumotlarni olish
    data = await integration.get_real_time_price("AAPL")
    print(data)
    
    # Portfolio ma'lumotlari
    portfolio = await integration.get_portfolio_data("user_123")
    
    # Risk metrikalari
    risk = await integration.get_risk_metrics("user_123")
    
    integration.cleanup()

asyncio.run(main())
```

## ⚡ Real-time Streaming

### WebSocket Streaming
```python
# Streaming boshlash
manager = MarketDataManager()
await manager.start_streaming(["BTCUSDT", "ETHUSDT"], ["binance", "coinbase"])

# Ma'lumotlarni olish
while True:
    data = manager.get_real_time_data("BTCUSDT")
    print(f"Price: ${data['current']['close']}")
    await asyncio.sleep(1)
```

### Real-time Signal Processing
```python
# AI signal monitoring
async def monitor_signals():
    while True:
        signals = await signal_generator.generate_signals("AAPL")
        if signals['confidence'] > 0.7:
            print(f"Strong signal detected: {signals['reasons']}")
        await asyncio.sleep(30)
```

## 🛡️ Xavfsizlik va Rate Limiting

### API Rate Limiting
```python
# Rate limit tekshirish
if rate_limiter.can_make_request('alpha_vantage'):
    data = await alpha_vantage.get_market_data("AAPL")
    rate_limiter.record_request('alpha_vantage')
```

### Data Validation
```python
# Ma'lumotlar sifati tekshiruvi
quality_check = await integration.engine.validate_data_quality("AAPL", "1m")
if quality_check['valid']:
    print(f"Data quality: {quality_check['quality_score']:.2f}")
```

## 📈 Performance Optimization

### Caching
```python
# Cache samaradorligi
cache_stats = integration.cache.get_cache_stats()
print(f"Hit rate: {cache_stats['hit_rate']:.2%}")
```

### Performance Monitoring
```python
# Tizim performance
health = await integration.health_check_advanced()
print(f"Optimization recommendations: {health['optimization_recommendations']}")
```

## 🔍 Anomaly Detection

### Market Anomalies
```python
# Narx anomalisini aniqlash
anomaly = anomaly_detector.detect_price_anomaly(current_price, historical_prices)
if anomaly['is_anomaly']:
    print(f"Anomaly detected! Z-score: {anomaly['z_score']:.2f}")

# Hajm anomalisini aniqlash
volume_anomaly = anomaly_detector.detect_volume_anomaly(current_volume, historical_volumes)
if volume_anomaly['is_anomaly']:
    print(f"Volume spike detected! {volume_anomaly['volume_ratio']:.1f}x normal")
```

## 📊 Risk Analytics

### Portfolio Risk
```python
positions = [
    {"symbol": "AAPL", "quantity": 100, "avg_price": 150.0},
    {"symbol": "GOOGL", "quantity": 50, "avg_price": 2800.0}
]

risk_metrics = await risk_analytics.calculate_portfolio_risk("user_123", positions)
print(f"Portfolio VaR 95%: ${risk_metrics['var_95']:.2f}")
print(f"Diversification Score: {risk_metrics['diversification_score']:.2f}")
```

## 📰 Sentiment Analysis

### News Sentiment
```python
# Yangiliklar sentiment analizi
news_summary = await news_manager.get_news_summary(["AAPL"])
print(f"Positive articles: {news_summary['sentiment_breakdown']['positive']}")
print(f"Average sentiment: {news_summary['average_sentiment']:.3f}")
```

### Social Media Sentiment
```python
# Social media tracking
social_data = await news_manager.fetch_social_sentiment(["AAPL"], limit=100)
twitter_sentiment = np.mean([p.sentiment_score for p in social_data if p.platform == 'twitter'])
reddit_sentiment = np.mean([p.sentiment_score for p in social_data if p.platform == 'reddit'])
print(f"Twitter sentiment: {twitter_sentiment:.3f}")
print(f"Reddit sentiment: {reddit_sentiment:.3f}")
```

## 🌍 Economic Calendar

### Upcoming Events
```python
# Iqtisodiy voqealar
events = await integration.get_economic_calendar()
high_impact_events = [e for e in events if e.impact_level == "HIGH"]
for event in high_impact_events:
    print(f"{event.date}: {event.title} ({event.currency})")
```

## 🔄 Multi-timeframe Analysis

### Comprehensive Analysis
```python
# Ko'p timeframe tahlil
multi_tf_data = await integration.get_enhanced_market_data("AAPL", "1h")
for timeframe, data in multi_tf_data.get('multi_timeframe', {}).items():
    print(f"{timeframe} price: ${data.get('consensus', {}).get('price', {}).get('mean', 0):.2f}")
```

## 📱 API Endpoints (FastAPI)

```python
from fastapi import FastAPI
from data_integration import RealTimeDataIntegration

app = FastAPI()
integration = RealTimeDataIntegration(DataConfig())

@app.get("/api/market/{symbol}")
async def get_market_data(symbol: str):
    return await integration.get_enhanced_market_data(symbol)

@app.get("/api/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    return await integration.get_sentiment_data(symbol)

@app.get("/api/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    return await integration.get_portfolio_data(user_id)

@app.get("/api/risk/{user_id}")
async def get_risk_metrics(user_id: str):
    return await integration.get_risk_metrics(user_id)
```

## 📋 Testing

### Unit Tests
```bash
# Testlarni ishga tushirish
pytest tests/test_data_integration.py -v
```

### Integration Tests
```python
# Ma'lumotlar integratsiyasini test qilish
async def test_integration():
    manager = DataIntegrationManager()
    data = await manager.get_comprehensive_market_data("AAPL")
    assert data is not None
    assert 'consensus' in data
```

## 📊 Monitoring va Logging

### Performance Monitoring
```python
# Tizim monitoring
health = await integration.health_check_advanced()
print(f"System status: {health['status']}")
print(f"Cache hit rate: {health['cache_efficiency']}")
```

### Logging Setup
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

## 🛠️ Troubleshooting

### Common Issues

1. **API Rate Limiting**
   ```python
   # Rate limit xatosi bo'lsa
   if "rate limit" in str(error):
       await asyncio.sleep(60)  # 1 daqiqa kutish
   ```

2. **Connection Timeouts**
   ```python
   # Timeout handling
   try:
       data = await asyncio.wait_for(get_data(), timeout=10)
   except asyncio.TimeoutError:
       data = get_cached_data()
   ```

3. **Data Quality Issues**
   ```python
   # Ma'lumotlar sifati tekshiruvi
   quality = await integration.engine.validate_data_quality(symbol, timeframe)
   if quality['quality_score'] < 0.5:
       # Alternate source dan ma'lumot olish
   ```

## 📈 Future Enhancements

1. **Machine Learning Integration**
   - Advanced signal generation
   - Pattern recognition
   - Predictive analytics

2. **Real-time Alerts**
   - Price alerts
   - Sentiment alerts
   - Risk alerts

3. **Advanced Analytics**
   - Correlation analysis
   - Portfolio optimization
   - Backtesting integration

4. **Mobile Support**
   - Push notifications
   - Mobile app integration

## 📄 License

Bu loyiha MIT license ostida tarqatiladi.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

Qo'shimcha savollar uchun:
- Email: support@orion-starline.com
- Documentation: https://docs.orion-starline.com
- GitHub Issues: https://github.com/orion-starline/issues

---

**Oxirgi yangilanish:** 2025-11-05
**Versiya:** 1.0.0
**Muallif:** Orion-Starline Development Team