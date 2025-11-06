# News Impact Assessment va Economic Calendar Integration Tizimi

Bu tizim bozor voqealari va iqtisodiy ma'lumotlarning bozorlarga ta'sirini tahlil qilish, bashorat qilish va riskni boshqarish uchun yaratilgan keng qamrovli AI-powered tizimdir.

## 🚀 Asosiy Funksiyalar

### 1. Economic Calendar Integration
- **FRED API Integration**: Federal Reserve Economic Data API orqali iqtisodiy ko'rsatkichlarni olish
- **Central Bank Announcements**: Fed, ECB, BOJ va boshqa markaziy banklarning yig'ilishlari va qarorlari
- **Earnings Calendar**: Korporativ daromadlar va moliyaviy natijalar
- **Market-Moving Events**: Bozor harakatiga ta'sir etuvchi voqealarni kuzatish

### 2. GPT-5 Powered News Analysis
- **Smart Classification**: Yangiliklarni avtomatik ravishda impact darajasiga ajratish
- **Impact Magnitude Estimation**: Ta'sir kuchini miqdoriy baholash
- **Asset Impact Mapping**: Qaysi aktiv sinflariga ta'sir qilishini aniqlash
- **Time-to-Impact Prediction**: Ta'sir vaqti va muddatini bashorat qilish
- **Recovery Analysis**: Bozor tiklanish vaqti tahmini

### 3. Event Categories
| Kategoriya | Tavsif | Misollar |
|------------|--------|----------|
| **Black Swan** | Kutilmagan katta voqealar | Urush, pandemiya, moliyaviy inqiroz |
| **High Impact** | Yuqori ta'sirli voqealar | Fed yig'ilishlari, GDP, CPI, earnings |
| **Medium Impact** | O'rta ta'sirli voqealar | PMI, retail sales, housing |
| **Low Impact** | Past ta'sirli ko'rsatkichlar | Haftalik ma'lumotlar, texnik ko'rsatkichlar |

### 4. Multi-Asset Impact Mapping
- **Stocks**: Earnings impact, sector-specific events
- **Forex**: Central bank policy, economic data
- **Metals**: Inflation data, industrial demand news
- **Crypto**: Risk sentiment, regulatory news
- **Bonds**: Interest rate decisions, inflation data

### 5. Prediction Models
- **Volatility Spike Prediction**: Volatilika o'sishini bashorat qilish
- **Price Movement Magnitude**: Narx harakati kattaligi
- **Direction Prediction**: Harakat yo'nalishi (bullish/bearish)
- **Recovery Pattern Analysis**: Tiklanish namunalarini tahlil qilish
- **Event Clustering**: O'xshash voqealarni guruhlash

## 📊 Asosiy Class-lar

### `NewsImpactAssessmentSystem`
Asosiy tizim koordinatori - barcha funksiyalarni birlashtiradi.

### `FREDApiIntegration`
Federal Reserve Economic Data API integration.

### `GPT5NewsClassifier`
GPT-5 powered yangiliklar klassifikatori.

### `ImpactAnalysisEngine`
Asosiy tahlil motori - bozor reaksiyasini bashorat qilish.

## 🛠️ O'rnatish va Sozlash

### 1. API Kalitlarni Sozlash
```python
# FRED API kaliti olish: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY = "your_fred_api_key_here"

# OpenAI API kaliti (GPT-5 uchun)
OPENAI_API_KEY = "your_openai_api_key_here"
```

### 2. Tizimni Ishga Tushirish
```python
import asyncio
from news_impact_assessment import NewsImpactAssessmentSystem

async def main():
    system = NewsImpactAssessmentSystem(
        fred_api_key=FRED_API_KEY,
        gpt5_api_key=OPENAI_API_KEY
    )
    
    # Joriy bozor narxlari
    current_prices = {
        'SPY': 445.50,
        'QQQ': 380.25,
        'GLD': 195.80,
        'EURUSD': 1.0850,
        'USDJPY': 149.50,
        'VIX': 18.5,
        'market_vol': 0.025
    }
    
    # To'liq tahlilni ishga tushirish
    report = await system.run_full_assessment(current_prices)
    return report

# Demo
report = asyncio.run(main())
```

## 📈 Asosiy Funksiyalar

### Economic Calendar Olish
```python
# Iqtisodiy calendar olish
events = await system.engine.get_economic_calendar()

# Yuqori ta'sirli voqealarni filtrlash
high_impact = [e for e in events if e.impact_level == ImpactLevel.HIGH]
```

### Yangiliklarni Tahlil Qilish
```python
# Yangiliklarni GPT-5 bilan tahlil qilish
analyzed_news = await system.engine.analyze_news_impact(news_items)

for news in analyzed_news:
    print(f"Classification: {news.classification.value}")
    print(f"Impact: {news.impact_magnitude:.2f}")
    print(f"Affected Assets: {news.affected_assets}")
```

### Bozor Reaksiyasini Bashorat Qilish
```python
# Voqea uchun bozor reaksiyasini bashorat qilish
reactions = system.engine.predict_market_reaction(event, current_prices)

for reaction in reactions:
    print(f"{reaction.asset_class.value}: {reaction.volatility_spike:.1f}% spike")
    print(f"Direction: {reaction.direction} (confidence: {reaction.confidence:.1%})")
```

### Risk Assessment
```python
# Tizim riskini baholash
risk_assessment = system.engine._assess_systemic_risk(events)
print(f"Risk Level: {risk_assessment['risk_level']}")
print(f"Recommendation: {risk_assessment['recommendation']}")
```

### Asset Allocation Recommendations
```python
# Aktivlar taqsimoti tavsiyalarini olish
allocations = system.engine._generate_allocation_recommendations(events)
for asset, allocation in allocations.items():
    print(f"{asset}: {allocation:.1%}")
```

## 🎯 Qo'llanma

### 1. Daily Workflow
```python
# Har kuni bajariladigan amallar
async def daily_routine():
    system = NewsImpactAssessmentSystem(API_KEYS)
    
    # 1. Joriy bozor narxlarini olish
    current_prices = get_current_market_prices()
    
    # 2. Iqtisodiy calendar yangilanish
    events = await system.engine.get_economic_calendar()
    
    # 3. Real-time alertlar
    alerts = await system.get_real_time_alerts()
    
    # 4. Risk assessment
    report = await system.run_full_assessment(current_prices)
    
    return report, alerts
```

### 2. Event-Driven Alerts
```python
# Voqea asosidagi ogohlantirishlar
async def monitor_events():
    while True:
        alerts = await system.get_real_time_alerts()
        for alert in alerts:
            if alert['level'] == 'HIGH':
                send_notification(alert)
        await asyncio.sleep(300)  # 5 daqiqa
```

### 3. Portfolio Risk Management
```python
# Portfel riskini boshqarish
async def manage_portfolio_risk():
    events = await system.engine.get_economic_calendar()
    risk = system.engine._assess_systemic_risk(events)
    
    if risk['risk_level'] == 'HIGH':
        # Pozitsiyalarni kamaytirish
        reduce_position_sizes(0.7)  # 30% kamaytirish
        increase_cash_allocation(0.4)  # 40% naqd pul
    elif risk['risk_level'] == 'MEDIUM':
        # Hedging strategiyalar
        add_hedge_positions()
```

## 📊 Output Format

### Economic Event Structure
```python
@dataclass
class EconomicEvent:
    title: str                    # Voqea nomi
    date: datetime               # Sana
    impact_level: ImpactLevel    # Ta'sir darajasi
    description: str             # Tavsif
    asset_impact: Dict[AssetClass, float]  # Aktiv ta'siri
    volatility_impact: Dict[str, float]    # Volatilika ta'siri
    recovery_time_estimate: int  # Tiklanish vaqti (soat)
```

### News Analysis Output
```python
@dataclass  
class NewsItem:
    headline: str              # Sarlavha
    classification: ImpactLevel # Klassifikatsiya
    impact_magnitude: float    # Ta'sir kuchi
    affected_assets: Dict[str, float]  # Ta'sirlangan aktivlar
    time_to_impact: int        # Ta'sir vaqti
    recovery_prediction: int   # Tiklanish bashorati
```

## 🔧 Demo va Test

### Demo Ishga Tushirish
```bash
# To'liq demo
python news_impact_demo.py

# Individual testlar
python -c "
import asyncio
from news_impact_demo import test_economic_calendar_integration
asyncio.run(test_economic_calendar_integration())
"
```

### Test Senariolari
1. **Economic Calendar Integration**: FRED API orqali iqtisodiy ma'lumotlarni olish
2. **News Classification**: Yangiliklarni GPT-5 bilan klassifikatsiya qilish  
3. **Market Reaction Prediction**: Bozor reaksiyasini bashorat qilish
4. **Event Clustering**: O'xshash voqealarni guruhlash
5. **Risk Assessment**: Tizim riskini baholash
6. **Allocation Recommendations**: Aktivlar taqsimoti tavsiyalari
7. **Real-time Alerts**: Real-time ogohlantirishlar

## 📈 Integration Example

### Trading Platform Integration
```python
class TradingBot:
    def __init__(self):
        self.impact_system = NewsImpactAssessmentSystem(API_KEYS)
        
    async def before_market_open(self):
        # Market ochilishdan oldin risk assessment
        events = await self.impact_system.engine.get_economic_calendar()
        risk = self.impact_system.engine._assess_systemic_risk(events)
        
        if risk['risk_level'] == 'HIGH':
            self.reduce_risk_exposure()
            
    async def on_news_event(self, news_item):
        # Yangilik voqeasida avtomatik reaksion
        analyzed = await self.impact_system.engine.analyze_news_impact([news_item])
        if analyzed[0].impact_magnitude > 0.7:
            self.close_high_risk_positions()
```

### Risk Management Integration
```python
class RiskManager:
    def __init__(self):
        self.system = NewsImpactAssessmentSystem(API_KEYS)
        
    async def daily_risk_check(self):
        current_prices = get_portfolio_prices()
        report = await self.system.run_full_assessment(current_prices)
        
        # Portfolio rebalancing based on upcoming events
        if report['risk_assessment']['risk_level'] in ['HIGH', 'MEDIUM']:
            recommended_allocation = report['asset_allocation_recommendations']
            self.rebalance_portfolio(recommended_allocation)
```

## 🚨 Real-time Monitoring

### Alert System
```python
async def monitoring_loop():
    system = NewsImpactAssessmentSystem(API_KEYS)
    
    while True:
        # Real-time alertlarni tekshirish
        alerts = await system.get_real_time_alerts()
        
        for alert in alerts:
            if alert['level'] == 'HIGH':
                # Foydalanuvchiga xabar berish
                send_telegram_alert(alert)
                send_email_alert(alert)
                
        # 15 daqiqa kutib turish
        await asyncio.sleep(900)
```

## 📊 Performance Metrics

### Accuracy Tracking
- **Direction Prediction**: Bull/Bear prediction accuracy
- **Magnitude Estimation**: Price movement size accuracy  
- **Timing Accuracy**: Time-to-impact and recovery timing
- **Classification Accuracy**: Event impact level classification

### Model Improvement
- **Historical Backtesting**: Past voqealar natijalarini tahlil qilish
- **Continuous Learning**: Yangi ma'lumotlar asosida model yangilash
- **Cross-Asset Correlation**: Assetlar orasidagi korrelyatsiyani yangilash

## 🔮 Advanced Features

### Machine Learning Integration
```python
# XG Boost yoki LSTM modellari bilan integratsiya
from sklearn.ensemble import RandomForestRegressor

class MLPredictionEngine:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        
    async def train_on_historical_data(self, historical_events, market_outcomes):
        # Tarixiy ma'lumotlar asosida o'qitish
        features = self.extract_features(historical_events)
        self.model.fit(features, market_outcomes)
        
    async def predict_outcome(self, upcoming_event):
        features = self.extract_features([upcoming_event])
        prediction = self.model.predict(features)
        return prediction
```

### Multi-Source Data Integration
- **News APIs**: Reuters, Bloomberg, CNBC integration
- **Social Sentiment**: Twitter, Reddit sentiment analysis
- **Alternative Data**: Satellite data, credit card transactions
- **Market Microstructure**: Order book, volume analysis

## 🛡️ Security va Compliance

### API Security
- Rate limiting va authentication
- Encrypted API key storage
- Request/response logging

### Data Privacy
- PII data handling
- GDPR compliance
- Secure data transmission

### Risk Disclosure
- Model limitations clearly stated
- Historical performance tracking
- Regular model validation

## 📞 Support va Documentation

- **Technical Issues**: Bug reports va feature requests
- **API Integration**: Help with external API setup  
- **Model Training**: Custom model development
- **Performance Tuning**: System optimization
- **Regulatory Compliance**: Industry-specific requirements

---

**Tizim Version**: 1.0.0  
**Oxirgi yangilanish**: 2025-11-03  
**Muallif**: AI Trading Technologies Team  
**Litsenziya**: MIT License