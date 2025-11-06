# Crypto & Commodities Integration Module - Dokumentatsiya

## Umumiy ma'lumot

`crypto_commodities.py` moduli cryptocurrency va commodity bozorlari uchun keng qamrovli integration tizimini ta'minlaydi. Bu modul barcha asosiy kriptovalyuta va kommoditi bozorlarini qamrab oladi.

## Asosiy funksiyalar

### 1. Cryptocurrency Trading
- **100+ Kriptovalyuta qo'llab-quvvatlash**: BTC, ETH, LTC, BCH, XRP, ADA, LINK, XLM, DOT, BNB, SOL, DOGE, va boshqalar
- **Ko'p birja integratsiyasi**: Binance, Coinbase, Kraken, Huobi
- **Real-time narx ma'lumotlari**: Live price feeds, 24/7 monitoring
- **Trading operatsiyalari**: BUY/SELL, limit orders

### 2. Real-time Price Monitoring
- **WebSocket ulanishlar**: Birjalar bilan real-time aloqalar
- **24/7 monitoring**: To'xtovsiz narx kuzatish
- **Price caching**: Tez kirish uchun narx cache
- **Performance optimization**: 50+ crypto parallel monitoring

### 3. Commodities Analysis
- **Asosiy kommoditilar**: Oltin, Kumush, Platina, Neft, Paxta, Kofe, Shakar
- **Yahoo Finance integratsiyasi**: Narx ma'lumotlari olish
- **Historical data**: O'tmish narxlar tahlili
- **Market correlation**: Kommoditi o'rtasidagi korrelyatsiya

### 4. Technical Analysis
- **Texnik indikatorlar**: RSI, MACD, Bollinger Bands, Stochastic, ADX
- **Moving averages**: SMA, EMA (12, 26, 50, 200 davrlar)
- **Volume indicators**: OBV, Volume SMA
- **Signal generation**: BUY/SELL/HOLD signallar generatsiyasi
- **Price prediction**: ML model bilan narx bashoratlari

### 5. Portfolio Management
- **Mixed portfolios**: Krypto va kommoditi aralash portfoliylar
- **Transaction tracking**: Barcha tranzaksiyalar ro'yxati
- **Performance metrics**: ROI, P&L, risk metrikalar
- **SQLite database**: Mahalliy ma'lumotlar bazasi

### 6. Price Alerts
- **Narx alertlari**: Above/Below/Crossing alertlar
- **Percentage alerts**: 24h o'zgarish uchun alertlar
- **Real-time notifications**: WebSocket callback funksiyalar
- **Multiple conditions**: Murakkab alert shartlari

### 7. News Integration
- **Crypto news**: Kripto yangiliklar olish
- **Commodity news**: Kommoditi yangiliklari
- **Sentiment analysis**: Matn sentiment tahlili
- **News impact**: Narxga ta'sir baholash

### 8. Arbitrage Detection
- **Cross-exchange arbitrage**: Turli birja orasidagi farq
- **Price difference detection**: Narx farqlarini aniqlash
- **Profit calculation**: Foyda hisoblash
- **Risk assessment**: Arbitrage risk baholash

## API Foydalanish

### Asosiy Manager class yaratish
```python
from ai_modules.crypto_commodities import CryptoCommoditiesManager

manager = CryptoCommoditiesManager()
```

### Real-time Monitoring boshlash
```python
# Real-time monitoring ishga tushirish
await manager.start_real_time_monitoring()
```

### Texnik tahlil olish
```python
# Texnik indikatorlar va signallar
analysis = manager.get_technical_analysis('BTC/USDT')
print(f"Signals: {analysis['signals']}")
print(f"RSI: {analysis['indicators']['rsi']}")
```

### Price Alert qo'shish
```python
# Narx alert qo'shish
alert_id = manager.add_price_alert(
    asset_type='crypto',
    symbol='BTC/USDT', 
    alert_type='price_above',
    value=50000,
    user_id='user123'
)
```

### Portfolio boshqaruv
```python
# Tranzaksiya qo'shish
manager.portfolio_manager.add_transaction(
    user_id='user123',
    symbol='BTC/USDT',
    transaction_type='BUY',
    quantity=0.1,
    price=45000
)

# Portfolio ko'rish
portfolio = manager.get_portfolio_performance('user123')
print(f"Total Value: ${portfolio['total_value']}")
```

### News ma'lumotlari
```python
# Yangiliklar qisqa ma'lumoti
news_summary = manager.get_news_summary()
print(f"Crypto sentiment: {news_summary['crypto_news']['sentiment_distribution']}")
```

### Arbitrage imkoniyatlari
```python
# Arbitrage imkoniyatlari topish
arbitrage_opps = manager.get_arbitrage_opportunities()
for opp in arbitrage_opps:
    print(f"Profit: {opp['profit_margin']:.2f}%")
```

### Supported Assets
```python
# Qo'llab-quvvatlanadigan aktivlar
assets = manager.get_supported_assets()
print(f"Cryptos: {assets['cryptocurrencies']}")
print(f"Commodities: {assets['commodities']}")
```

## Asosiy Klasslar

### CryptoCommoditiesDataProvider
Ma'lumot provayderi - barcha birja API'larini birlashtiradi

### RealTimePriceMonitor
Real-time narx monitoring tizimi - WebSocket ulanishlari va alertlar

### TechnicalAnalyzer
Texnik tahlil - indikatorlar, signallar va bashoratlar

### PortfolioManager
Portfolio boshqaruv - tranzaksiyalar va performance tracking

### NewsAnalyzer
Yangiliklar tahlili - sentiment analysis va impact assessment

### ArbitrageDetector
Arbitrage detection - narx farqlari va foyda hisoblash

### CryptoCommoditiesManager
Asosiy boshqaruvchi class - barcha funksiyalarni jamlaydi

## Database Schema

### Portfolios jadvali
```sql
CREATE TABLE portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    crypto_symbol TEXT,
    commodity_symbol TEXT,
    quantity REAL,
    avg_price REAL,
    current_price REAL,
    pnl REAL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transactions jadvali
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    type TEXT NOT NULL,
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration

### Environment Variables
```bash
# API Keys (optional)
BINANCE_API_KEY=your_binance_key
COINBASE_API_KEY=your_coinbase_key
KRAKEN_API_KEY=your_kraken_key

# Database
DATABASE_PATH=crypto_portfolio.db
```

### Supported Cryptocurrencies
```python
supported_cryptos = [
    'BTC/USDT', 'ETH/USDT', 'LTC/USDT', 'BCH/USDT', 'XRP/USDT',
    'ADA/USDT', 'LINK/USDT', 'XLM/USDT', 'DOT/USDT', 'BNB/USDT',
    # ... 100+ more
]
```

### Supported Commodities
```python
commodity_sources = {
    'gold': 'XAUUSD=X',
    'silver': 'XAGUSD=X', 
    'platinum': 'XPTUSD=X',
    'oil': 'CL=F',
    'cotton': 'CT=F',
    'coffee': 'KC=F',
    'sugar': 'SB=F'
}
```

## Performance

### Monitoring Capacity
- **Real-time crypto**: 50 ta parallel narx tracking
- **Commodity updates**: 30 soniya interval
- **Alert processing**: 1 soniya response
- **Database queries**: Sub-second responses

### Scalability
- **Multi-user support**: Cheksiz user count
- **Concurrent operations**: Async/await support
- **Memory optimization**: Efficient caching
- **Rate limiting**: API limits respecter

## Risk Management

### Volatility Controls
- **Position limits**: Maksimal pozitsiya hajmi
- **Stop-loss detection**: Avtomatik stop-loss
- **Risk metrics**: VaR, Sharpe ratio
- **Exposure tracking**: Asset exposure monitoring

### Error Handling
- **Network timeouts**: Connection error handling
- **API rate limits**: Request throttling
- **Data validation**: Input validation
- **Logging**: Comprehensive error logging

## Integration Examples

### WebSocket Real-time Updates
```python
# Custom callback funksiyasi
async def custom_alert_callback(alert, asset):
    print(f"🚨 Alert: {asset.name} reached {alert['value']}")
    
# Callback qo'shish
manager.price_monitor.callbacks.append(custom_alert_callback)
```

### Plotly Charts
```python
# Trading chart yaratish
chart_path = manager.generate_trading_chart('BTC/USDT')
print(f"Chart saved: {chart_path}")
```

### Machine Learning Integration
```python
# Price prediction features
features = np.array([[rsi, macd, bb_position, volume_ratio]])
predicted_price = manager.technical_analyzer.predict_price(features)
```

## Monitoring va Logging

### Log Levels
- **INFO**: Oddiy operatsiyalar
- **ERROR**: Xatolar va muammolar
- **WARNING**: Ogohlantirishlar

### Metrics
- **Response times**: API response vaqtlari
- **Success rates**: Muvaffaqiyat foizlari
- **Memory usage**: Xotira iste'moli
- **Database performance**: DB operatsiyalar

## Testing

### Demo Implementation
```python
# To'liq demo
python crypto_commodities.py
```

### Unit Testing
```python
# Individual komponentlarni test qilish
manager = CryptoCommoditiesManager()
await manager.demo_run()
```

## Security Considerations

### API Keys
- **Environment variables**: API kalitlar environment dan olish
- **Encryption**: Maxfiy ma'lumotlarni shifrlash
- **Rate limiting**: API so'rovlar sonini cheklash

### Data Security
- **User data**: User ma'lumotlarini himoyalash
- **Portfolio info**: Portfolio ma'lumotlarini shifrlash
- **Access controls**: User autentifikatsiya

## Future Enhancements

### Planned Features
- **DeFi integration**: DEX integration
- **Options trading**: Kripto options
- **Social sentiment**: Social media sentiment
- **Advanced ML**: Deep learning models
- **Mobile API**: Mobile application support

### Performance Improvements
- **Caching**: Redis integration
- **Database optimization**: PostgreSQL migration
- **Microservices**: Service architecture
- **Kubernetes**: Container orchestration

## Support va Maintenance

### Troubleshooting
1. **Connection errors**: Internet aloqasini tekshiring
2. **API limits**: Rate limiting tekshirildi
3. **Database issues**: SQLite faylni tekshiring
4. **Performance**: Memory va CPU usage

### Maintenance Tasks
- **Database backup**: Haftalik backup
- **Log rotation**: Kunlik log rotation
- **API updates**: Haftalik API checks
- **Performance monitoring**: Monthly performance reviews

---

**Modul versiyasi**: 2.0.0  
**Oxirgi yangilash**: 2025-11-05  
**Manba**: Orion Starline AI Trading System