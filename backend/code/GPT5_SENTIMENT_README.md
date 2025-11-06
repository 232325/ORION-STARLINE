# GPT-5 Sentiment Analysis System

Bu loyiha OpenAI GPT-5 API yordamida bozor sentimentini tahlil qiluvchi to'liq tizimdir. Sistema ko'p aktiv turlari (aksialar, forex, metallar) uchun real-time sentiment tahlili bajaradi.

## 🎯 Xususiyatlar

### GPT-5 API Integration
- ✅ OpenAI GPT-5 API to'liq integratsiyasi
- ✅ Rate limiting va xato boshqaruvi
- ✅ Async API chaqiruvlari batch processing uchun
- ✅ Narx optimizatsiyasi strategiyalari
- ✅ Response caching tizimi

### Market Sentiment Analysis
- ✅ Yangilik maqolalar sentiment extraction
- ✅ Ijtimoiy tarmoq sentiment (Twitter, Reddit)
- ✅ Earnings call sentiment tahlili
- ✅ Analyst report sentiment
- ✅ Umumiy bozor sentiment hisoblari

### Multi-Asset Sentiment
- **📈 Aksiyalar:** AAPL, GOOGL, MSFT, TSLA, NVDA
- **💱 Forex:** EUR/USD, GBP/USD, USD/JPY, USD/CHF
- **🥇 Metallar:** XAU/USD, XAG/USD, XPT/USD, XPD/USD
- Asset-specific sentiment ko'rsatkichlari

### Sentiment Features
- ✅ Bullish/Bearish ehtimollik
- ✅ Ishonchlilik hisoblari (0-1)
- ✅ Time-series sentiment trendlari
- ✅ Sentiment momentum ko'rsatkichlari
- ✅ Kontrarian sentiment signallar

### Technical Integration
- ✅ FastAPI endpoint sentiment API uchun
- ✅ Real-time news feed processing
- ✅ Sentiment ma'lumotlar bazasi saqlash
- ✅ WebSocket live yangilanishlar uchun
- ✅ Dashboard visualization

## 🚀 Tez boshlash

### 1. O'rnatish

```bash
# Dependencies o'rnating
pip install -r requirements.txt

# Environment variable sozlang
export OPENAI_API_KEY='sizning-openai-api-kalit-ingiz'
```

### 2. Demo ishga tushirish

```bash
# Demo script
python demo_gpt5_sentiment.py

# API server
python gpt5_sentiment_analysis.py
```

### 3. API test qilish

```bash
# Tizim holati
curl http://localhost:8000/health

# Sentiment tahlili
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "TSLA"]}'

# Bitta aktiv sentimenti
curl http://localhost:8000/sentiment/AAPL

# Mavjud aktivlar
curl http://localhost:8000/symbols
```

## 📊 API Documentation

### Endpoints

| Endpoint | Method | Tavsif |
|----------|--------|--------|
| `/` | GET | Root endpoint |
| `/health` | GET | Tizim sog'lig'i tekshiruvi |
| `/analyze` | POST | Sentiment tahlili |
| `/sentiment/{symbol}` | GET | Bitta aktiv sentimenti |
| `/symbols` | GET | Mavjud aktivlar ro'yxati |
| `/ws/sentiment` | WebSocket | Real-time yangilanishlar |

### Response Format

```json
{
  "success": true,
  "data": {
    "AAPL": {
      "symbol": "AAPL",
      "asset_class": "stock",
      "timestamp": "2025-11-03T03:56:33",
      "price": 150.25,
      "volume": 1000000,
      "news_count": 15,
      "sentiment_data": {
        "bullish_probability": 0.75,
        "bearish_probability": 0.25,
        "confidence": 0.85,
        "sentiment_type": "bullish",
        "overall_score": 0.50
      }
    }
  },
  "timestamp": "2025-11-03T03:56:33"
}
```

## 🔧 Konfiguratsiya

### config.py

```python
SENTIMENT_CONFIG = {
    'openai_api_key': 'YOUR_OPENAI_API_KEY',
    'gpt5_model': 'gpt-5',
    'rate_limit': 60,  # requests per minute
    'max_tokens': 500,
    'temperature': 0.3,
    'enable_cache': True,
    'max_cache_size': 1000,
    'batch_size': 10,
    'max_workers': 10
}
```

### Asset Symbols

```python
stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
forex_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF']
metals = ['XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD']
```

## 📈 Sentiment Metrikalar

### Bullish/Bearish Probabilities
- **Bullish:** 0.0 - 1.0 (yuqori qiymat = ko'proq ijobiy sentiment)
- **Bearish:** 0.0 - 1.0 (yuqori qiymat = ko'proq salbiy sentiment)

### Confidence Score
- **0.0 - 1.0:** Tahlil ishonchliligi darajasi
- **> 0.8:** Yuqori ishonchlilik
- **0.5 - 0.8:** O'rta ishonchlilik  
- **< 0.5:** Past ishonchlilik

### Overall Score
- **-1.0:** Aşırı bearish
- **0.0:** Neutral
- **+1.0:** Aşırı bullish

### Sentiment Momentum
- **Positive:** Bullish momentum o'sishda
- **Negative:** Bearish momentum kuchaymoqda
- **Zero:** Hech qanday trend yo'q

## 🎯 Kontrarian Signals

Sistema quyidagi kontrarian signallarni aniqlaydi:

1. **Yuqori bullish sentiment + Narx pasayishi**
   - Potentsial contrarian sell signal

2. **Past bearish sentiment + Narx o'sishi**
   - Potentsial contrarian buy signal

3. **Aşırı extreme sentiment (>0.8)**
   - Potentsial reversal signal

## 💾 Ma'lumotlar bazasi

Tizim SQLite ma'lumotlar bazasidan foydalanadi:

- `sentiment_results`: Tahlil natijalari
- `market_data`: Bozor ma'lumotlari
- `news_items`: Yangilik elementlari

### Tarixiy ma'lumotlarni olish

```python
from gpt5_sentiment_analysis import SentimentDatabase

db = SentimentDatabase()
history = db.get_sentiment_history("AAPL", days=7)
```

## 🌐 WebSocket Integration

Real-time sentiment yangilanishlari uchun WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/sentiment');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Sentiment update:', data);
};
```

## 📊 Dashboard Integration

React dashboard uchun misol:

```javascript
import React, { useState, useEffect } from 'react';

const SentimentDashboard = () => {
    const [sentimentData, setSentimentData] = useState({});
    
    useEffect(() => {
        fetch('/analyze')
            .then(response => response.json())
            .then(data => setSentimentData(data.data));
    }, []);
    
    return (
        <div>
            {Object.entries(sentimentData).map(([symbol, data]) => (
                <div key={symbol}>
                    <h3>{symbol}</h3>
                    <p>Sentiment: {data.sentiment_data?.sentiment_type}</p>
                    <p>Confidence: {data.sentiment_data?.confidence}</p>
                </div>
            ))}
        </div>
    );
};
```

## 🔧 Cost Optimization

### API Narx Tejash
- Response caching (1000 ta so'rovgacha)
- Batch processing (10 ta aktiv parallel)
- Rate limiting (60 so'rov/dakika)
- Minimal token usage (max_tokens: 500)

### Monitoring
- Narx kuzatuvi (`cost_tracker`)
- Xato loglash
- Performance metrikalar

## 🛠️ Development

### Loyiha tuzilishi

```
code/
├── gpt5_sentiment_analysis.py  # Asosiy tizim
├── demo_gpt5_sentiment.py     # Demo script
├── config.py                  # Konfiguratsiya
├── requirements.txt           # Dependencies
└── sentiment_data.db         # SQLite DB (auto-created)
```

### Yangi Feature Qo'shish

1. **Yangi ma'lumot manbasi:**
```python
class NewDataSource:
    async def fetch_data(self, symbols):
        # Implementation
        pass
```

2. **Custom sentiment aggregator:**
```python
class CustomSentimentAggregator(SentimentAggregator):
    def custom_analysis(self, data):
        # Custom logic
        pass
```

### Testing

```bash
# Unit tests
pytest tests/

# Demo test
python demo_gpt5_sentiment.py

# API test
curl -X GET http://localhost:8000/health
```

## 🔍 Troubleshooting

### Keng tarqalgan muammolar

1. **"API key topilmadi" xatosi**
   ```bash
   export OPENAI_API_KEY='sizning-kalit'
   ```

2. **"Rate limit exceeded" xatosi**
   - `rate_limit` ni kamaytiring yoki bekor qiling
   - Cache yoqilganligini tekshiring

3. **"Database error" xatosi**
   - `sentiment_data.db` fayl huquqlari
   - Disk joy yetarli ekanligini tekshiring

4. **"WebSocket connection failed"**
   - Port 8000 band emasligini tekshiring
   - Firewall sozlamalarini ko'ring

## 📚 Qo'shimcha Resurslar

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket Guide](https://websockets.readthedocs.io/)
- [SQLite Python Tutorial](https://docs.python.org/3/library/sqlite3.html)

## 🤝 Hissa Qo'shish

1. Fork qiling
2. Feature branch yarating (`git checkout -b feature/AmazingFeature`)
3. O'zgarishlaringizni commit qiling (`git commit -m 'Add AmazingFeature'`)
4. Branch ni push qiling (`git push origin feature/AmazingFeature`)
5. Pull Request oching

## 📄 Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## 📞 Yordam

Agar savollaringiz bo'lsa:
- [Issues yarating](https://github.com/your-repo/issues)
- [Documentation o'qib ko'ring](https://github.com/your-repo/wiki)
- [Demo script ishga tushiring](demo_gpt5_sentiment.py)

---

**Eslatma:** Bu loyiha demo maqsadlar uchun yaratilgan. Haqiqiy savdo qarorlar qabul qilishdan oldin professional maslahat oling.