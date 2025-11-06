# Smart Alert System - Keng Qamrovli Dokumentatsiya

## Kirish

Smart Alert System - bu Orion Starline platformasi uchun yaratilgan keng qamrovli ogohlantirish moduli bo'lib, investitsiya va treyderlarga real-time market ma'lumotlari, texnik indikatorlar va muhim voqealar haqida xabar berish imkonini beradi.

## Xususiyatlari

### 1. **Price Alerts** (Narx Ogohlantirishlari)
- Custom price level alerts
- Above/Below/Equal conditions
- Multiple symbol support
- Real-time price monitoring

### 2. **Multi-Channel Notifications** (Ko'p Kanalli Xabarlar)
- **SMS** (Twilio orqali)
- **Email** (SendGrid orqali)
- **Push Notifications** (Firebase orqali)
- **Telegram** (Bot orqali)
- Slack webhook support
- Custom webhook integration

### 3. **News-Based Alerts** (Yangiliklar Asosidagi Ogohlantirishlar)
- Breaking news detection
- Market-moving events
- Keyword-based filtering
- Sentiment analysis integration
- Real-time news monitoring

### 4. **Custom Watchlists** (Foydalanuvchi Watchlistlari)
- User-defined asset lists
- Group-based monitoring
- Bulk operations support
- Dynamic list updates

### 5. **Technical Indicator Alerts** (Texnik Indikator Ogohlantirishlari)
- **RSI** (Relative Strength Index) alerts
- **MACD** (Moving Average Convergence Divergence) alerts
- **Moving Averages** (MA20, MA50, MA200) alerts
- **Bollinger Bands** alerts
- **Support/Resistance** level alerts

### 6. **Volume Alerts** (Volume Ogohlantirishlari)
- Unusual trading volume detection
- Volume surge alerts
- Historical volume comparison
- Multiplier-based alerts

### 7. **Portfolio Alerts** (Portfolio Ogohlantirishlari)
- Portfolio value changes
- Percentage-based alerts
- Individual holding monitoring
- Performance threshold alerts

### 8. **Risk Alerts** (Risk Ogohlantirishlari)
- Risk threshold breaches
- Portfolio risk assessment
- Volatility alerts
- Stop-loss notifications

### 9. **Calendar Alerts** (Taqvim Ogohlantirishlari)
- Economic events monitoring
- Central bank announcements
- Earnings reports
- Custom event scheduling

### 10. **Alert History & Management** (Ogohlantirish Tarixi)
- Complete alert tracking
- Acknowledgment system
- Performance analytics
- Export capabilities

## Arxitektura

### Asosiy Komponentlar

```
SmartAlertSystem
├── Notification Providers
│   ├── TwilioProvider (SMS)
│   ├── SendGridProvider (Email)
│   ├── TelegramProvider
│   └── FirebaseProvider (Push)
├── Analyzers
│   ├── TechnicalAnalyzer
│   ├── NewsAnalyzer
│   ├── CalendarAnalyzer
│   └── PortfolioAnalyzer
├── Database Layer (SQLite)
├── Monitoring Engine
└── Alert Rules Engine
```

### Ma'lumotlar Bazasi Struktura

**alert_rules** jadval:
- id, name, alert_type, symbol, condition, threshold
- channel, is_active, created_at, expires_at
- metadata (JSON)

**alerts** jadval:
- id, rule_id, alert_type, symbol, message
- severity, channel, status, triggered_at
- acknowledged, metadata (JSON)

**watchlists** jadval:
- id, name, symbols, created_at, updated_at

## O'rnatish va Sozlash

### 1. Asosiy O'rnatish

```python
from ai_modules.smart_alerts import SmartAlertSystem

# Smart Alert System yaratish
alerts = SmartAlertSystem()
```

### 2. Konfiguratsiya

**alert_config.json** faylini yarating:

```json
{
  "twilio": {
    "account_sid": "your_twilio_account_sid",
    "auth_token": "your_twilio_auth_token",
    "from_number": "+1234567890",
    "to_number": "+0987654321"
  },
  "sendgrid": {
    "api_key": "your_sendgrid_api_key",
    "from_email": "alerts@yourcompany.com",
    "to_email": "user@example.com"
  },
  "telegram": {
    "bot_token": "your_telegram_bot_token",
    "chat_id": "your_chat_id"
  },
  "firebase": {
    "service_account_path": "path/to/service-account.json",
    "fcm_token": "your_fcm_token"
  },
  "news": {
    "news_api_key": "your_news_api_key"
  },
  "monitoring": {
    "interval": 60,
    "max_alerts_per_hour": 100
  }
}
```

## Foydalanish Namunalari

### 1. Price Alerts

```python
# BTC 45,000$ dan yuqori bo'lsa xabar
btc_alert = alerts.add_price_alert(
    symbol="BTC",
    condition="above",
    threshold=45000,
    channel="telegram",
    name="BTC 45K dan yuqori"
)

# AAPL 140$ dan past bo'lsa xabar
aapl_alert = alerts.add_price_alert(
    symbol="AAPL",
    condition="below",
    threshold=140,
    channel="email",
    name="AAPL 140$ dan past"
)
```

### 2. Technical Indicator Alerts

```python
# RSI overbought alert
rsi_alert = alerts.add_technical_alert(
    symbol="BTC",
    indicator="RSI",
    condition="rsi_overbought",
    threshold=70,
    channel="telegram"
)

# Moving average alert
ma_alert = alerts.add_technical_alert(
    symbol="ETH",
    indicator="MA20",
    condition="price_above_ma",
    threshold=0,
    channel="email"
)
```

### 3. Volume Alerts

```python
# Unusual volume alert
volume_alert = alerts.add_volume_alert(
    symbol="TSLA",
    volume_multiplier=2.5,
    channel="push",
    name="TSLA unusual volume"
)
```

### 4. News Alerts

```python
# News keyword alerts
news_alert = alerts.add_news_alert(
    keywords=["bitcoin", "fed", "crisis"],
    sentiment="negative",
    channel="telegram",
    name="Market crisis news"
)
```

### 5. Portfolio Alerts

```python
# Portfolio change alert
portfolio_alert = alerts.add_portfolio_alert(
    portfolio_name="My Portfolio",
    change_threshold=5.0,
    channel="email"
)
```

### 6. Risk Alerts

```python
# Risk threshold alert
risk_alert = alerts.add_risk_alert(
    symbol="BTC",
    risk_threshold=0.8,
    channel="push"
)
```

### 7. Calendar Alerts

```python
# Economic event alert
calendar_alert = alerts.add_calendar_alert(
    event_name="Fed Meeting",
    importance="high",
    channel="telegram"
)
```

## Watchlists Boshqaruvi

```python
# Watchlist yaratish
tech_watchlist = alerts.create_watchlist(
    name="Tech Stocks",
    symbols=["AAPL", "GOOGL", "MSFT", "NVDA"]
)

# Watchlist ga symbol qo'shish
alerts.add_to_watchlist(tech_watchlist, "AMZN")

# Barcha watchlist larni olish
watchlists = alerts.get_watchlists()
```

## Monitoring Boshqaruvi

```python
# Monitoring ni boshlash
alerts.start_monitoring()

# Monitoring ni to'xtatish
alerts.stop_monitoring()

# Faol qoidalarni olish
active_rules = alerts.get_active_rules()
```

## Alert Boshqaruvi

```python
# Qoidani to'xtatish
alerts.pause_rule(rule_id)

# Qoidani davom ettirish
alerts.resume_rule(rule_id)

# Qoidani o'chirish
alerts.delete_rule(rule_id)

# Ogohlantirish tarixi
history = alerts.get_alert_history(limit=100, symbol="BTC")
```

## Statistika va Analytics

```python
# Alert statistikasi
stats = alerts.get_alert_statistics()
print(f"Total alerts: {stats['total_alerts']}")
print(f"Today alerts: {stats['today_alerts']}")
print(f"Active rules: {stats['active_rules']}")
print(f"Type distribution: {stats['type_distribution']}")

# Performance metrikalar
performance = alerts.get_performance_metrics()
print(f"Alert frequency: {performance['alert_frequency_per_rule']}")
print(f"System uptime: {performance['system_uptime']}")
```

## Notification Provider Configuration

### Twilio (SMS)
```python
config = {
    "twilio": {
        "account_sid": "ACxxxxxxxx",
        "auth_token": "xxxxxxxx",
        "from_number": "+1234567890",
        "to_number": "+0987654321"
    }
}
alerts.update_config(config)
```

### SendGrid (Email)
```python
config = {
    "sendgrid": {
        "api_key": "SG.xxxxxxxx",
        "from_email": "alerts@company.com",
        "to_email": "user@email.com"
    }
}
alerts.update_config(config)
```

### Telegram Bot
```python
config = {
    "telegram": {
        "bot_token": "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ",
        "chat_id": "123456789"
    }
}
alerts.update_config(config)
```

### Firebase (Push Notifications)
```python
config = {
    "firebase": {
        "service_account_path": "path/to/service-account.json",
        "fcm_token": "dGVzdF9mbV90b2tlbg"
    }
}
alerts.update_config(config)
```

## Real-time Monitoring

### System Ishlashi

1. **Rule Engine**: Barcha qoidalar avtomatik ravishda tekshiriladi
2. **Condition Checking**: Har bir qoida uchun shartlar tekshiriladi
3. **Alert Triggering**: Shartlar bajarilsa, ogohlantirish yaratiladi
4. **Notification**: Xabar tegishli kanallarga yuboriladi
5. **History Tracking**: Barcha ogohlantirishlar tarixga saqlanadi

### Performance Optimization

- **Async Operations**: Xabar yuborish async
- **Threading**: Monitoring alohida thread da ishlaydi
- **Database Optimization**: Indexlangan sorgular
- **Caching**: Tez-tez ishlatiladigan ma'lumotlar cache

## Xavfsizlik va Compliance

### Data Protection
- Ma'lumotlar SQLite database da shifrlangan
- API kalitlar environment variables da saqlanadi
- Xavfli ma'lumotlar log qilinmaydi

### Rate Limiting
- Soatiga maksimal ogohlantirish soni
- Duplicate alert prevention
- Provider-specific rate limits

### Error Handling
- Graceful degradation
- Automatic retry mechanisms
- Comprehensive logging

## Integration Examples

### Trading Platform Integration
```python
# Trading platform dan ma'lumot olish
async def get_market_data(symbol):
    # API dan real-time ma'lumot olish
    return {
        "price": current_price,
        "volume": current_volume,
        "timestamp": datetime.now()
    }

# Custom condition function
def custom_price_condition(symbol, threshold):
    # Custom logic here
    return current_price > threshold

# Integration
alerts.add_custom_alert(
    symbol="BTC",
    condition_func=custom_price_condition,
    channel="telegram"
)
```

### Portfolio Management Integration
```python
# Portfolio monitoring
def monitor_portfolio():
    portfolio_value = portfolio_analyzer.calculate_portfolio_value(holdings)
    
    # Check all portfolio alerts
    for rule_id, rule in alerts.alert_rules.items():
        if rule.alert_type == AlertType.PORTFOLIO:
            # Check portfolio change
            change_pct = calculate_change_percentage(portfolio_value)
            
            if abs(change_pct) > rule.threshold:
                alert = create_portfolio_alert(rule, change_pct)
                alerts._trigger_alert(alert)

# Auto-monitoring
schedule.every(5).minutes.do(monitor_portfolio)
```

## Troubleshooting

### Common Issues

**1. Notification Provider Errors**
```python
# Provider status check
if 'telegram' not in alerts.notification_providers:
    print("Telegram provider not configured")

# Configuration update
alerts.update_config({"telegram": {"bot_token": "new_token"}})
```

**2. Database Issues**
```python
# Database integrity check
def check_database():
    try:
        conn = sqlite3.connect(alerts.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM alert_rules")
        rules_count = cursor.fetchone()[0]
        conn.close()
        return rules_count > 0
    except Exception as e:
        print(f"Database error: {e}")
        return False
```

**3. Monitoring Issues**
```python
# Monitoring status
print(f"Monitoring active: {alerts.monitoring_active}")
print(f"Active rules: {len(alerts.get_active_rules())}")

# Restart monitoring
alerts.stop_monitoring()
time.sleep(5)
alerts.start_monitoring()
```

### Logging
```python
# Logger setup
import logging
logging.basicConfig(level=logging.INFO)

# Alert-specific logging
logger = logging.getLogger('SmartAlerts')
logger.info("Alert triggered: BTC price above 45000")
```

## Best Practices

### 1. Rule Management
- Unique rule names foydalaning
- Expiration dates belgilang
- Metadata da qo'shimcha ma'lumotlar saqlang

### 2. Performance
- Monitoring intervalni to'g'ri tanlang
- Maximum alert limits o'rnating
- Provider-specific rate limits e'tiborga oling

### 3. Security
- API kalitlarni environment variables da saqlang
- Sensitive data ni log qilmang
- Database access ni cheklang

### 4. Maintenance
- Alert history ni muntazam tozalang
- Database performance ni kuzating
- Provider status ni tekshiring

## API Reference

### AlertRule Class
```python
@dataclass
class AlertRule:
    id: str
    name: str
    alert_type: AlertType
    symbol: str
    condition: str
    threshold: float
    channel: NotificationChannel
    is_active: bool = True
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
```

### Alert Class
```python
@dataclass
class Alert:
    id: str
    rule_id: str
    alert_type: AlertType
    symbol: str
    message: str
    severity: str
    channel: NotificationChannel
    status: AlertStatus
    triggered_at: datetime
    acknowledged: bool = False
    metadata: Dict[str, Any] = None
```

### Main Methods
- `add_price_alert()` - Narx ogohlantirish qo'shish
- `add_technical_alert()` - Texnik indikator ogohlantirish qo'shish
- `add_volume_alert()` - Volume ogohlantirish qo'shish
- `add_news_alert()` - Yangiliklar ogohlantirish qo'shish
- `add_portfolio_alert()` - Portfolio ogohlantirish qo'shish
- `add_risk_alert()` - Risk ogohlantirish qo'shish
- `add_calendar_alert()` - Taqvim ogohlantirish qo'shish
- `create_watchlist()` - Watchlist yaratish
- `start_monitoring()` - Monitoring boshlash
- `stop_monitoring()` - Monitoring to'xtatish
- `get_alert_history()` - Ogohlantirish tarixi olish
- `get_alert_statistics()` - Statistika olish

## Demo va Test

```python
# Demo ishga tushirish
python smart_alerts.py

# Unit test
pytest test_smart_alerts.py

# Integration test
python integration_demo.py
```

## Conclusion

Smart Alert System - bu professional, keng qamrovli va skalabll ogohlantirish tizimi bo'lib, Orion Starline platformasining bir qismi sifatida ishlaydi. Sistema modular architecture ga ega bo'lib, yangi xususiyatlar qo'shish va mavjud funksiyalarni kengaytirish oson.

Ushbu modul orqali treyderlar va investorlar:
- Real-time market ma'lumotlarini olishlari
- Texnik tahlillar bo'yicha signal olishlari  
- Muhim yangiliklar va voqealar haqida xabar olishlari
- Portfolio holatini kuzatishlari
- Risk boshqaruvini yaxshilashlari mumkin.

**Asosiy afzalliklar:**
- ✅ Ko'p kanalli xabar yuborish
- ✅ Keng qamrovli alert turlari
- ✅ Real-time monitoring
- ✅ Professional ma'lumotlar bazasi
- ✅ Comprehensive analytics
- ✅ Scalable architecture
- ✅ Easy integration
- ✅ Security & compliance

---

*Ushbu dokumentatsiya Smart Alert System v1.0 uchun tayyorlangan.*