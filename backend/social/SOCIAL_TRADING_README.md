# Social Trading va AI Automation - To'liq Dokumentatsiya

## Umumiy Ma'lumot

BOSQICH 10: Social Trading va AI Automation moduli AI Trading Evolution platformasiga ijtimoiy savdo va sun'iy intellekt avtomatlashtirish imkoniyatlarini qo'shadi.

### Modullar

1. **Copy Trading Engine** - Leader traderlarni kuzatish va avtomatik ko'chirish
2. **Signal Sharing Platform** - Trading signallarini e'lon qilish va obuna bo'lish
3. **Leaderboard System** - Traderlar reytingi va yutuqlar tizimi
4. **AutoML Pipeline** - Avtomatik model training va optimization
5. **Strategy Marketplace** - Trading strategiyalarini sotish/sotib olish
6. **Reputation System** - Ishonch balli va tasdiqlash tizimi

---

## 1. Copy Trading Engine

### Asosiy Xususiyatlar

- **Leader Tracking**: Muvaffaqiyatli traderlarni kuzatish
- **Automatic Position Mirroring**: Tradelarni avtomatik ko'chirish
- **Multiple Copy Modes**: Turli xil ko'chirish rejimlari
- **Risk Management**: Risk boshqaruvi va limitlar
- **Performance Monitoring**: Real-time performance kuzatish

### Copy Modes

```python
class CopyMode(Enum):
    PROPORTIONAL = "proportional"  # Proporsional
    FIXED_AMOUNT = "fixed_amount"  # Belgilangan summa
    PERCENTAGE = "percentage"  # Portfolio foizi
    MIRROR = "mirror"  # To'liq ko'chirish (1:1)
```

### API Endpoints

#### Leader qo'shish
```http
POST /api/v1/copy-trading/leaders
Content-Type: application/json

{
  "leader_id": "leader_001",
  "username": "ProTrader",
  "total_trades": 500,
  "win_rate": 72.5,
  "total_pnl": 15000.0,
  "sharpe_ratio": 2.1,
  "min_copy_amount": 500.0,
  "verified": true
}
```

#### Top leaderlar
```http
GET /api/v1/copy-trading/leaders/top?limit=10&sort_by=win_rate&min_trades=50
```

**Response:**
```json
[
  {
    "leader_id": "leader_001",
    "username": "ProTrader",
    "total_followers": 150,
    "total_trades": 500,
    "win_rate": 72.5,
    "total_pnl": 15000.0,
    "sharpe_ratio": 2.1,
    "max_drawdown": 8.5,
    "risk_level": "moderate",
    "verified": true,
    "commission_rate": 10.0
  }
]
```

#### Copy tradingni boshlash
```http
POST /api/v1/copy-trading/start
Content-Type: application/json

{
  "follower_id": "user_123",
  "leader_id": "leader_001",
  "settings": {
    "mode": "proportional",
    "allocation_amount": 1000.0,
    "max_position_size": 100.0,
    "copy_sl_tp": true,
    "max_open_positions": 5
  }
}
```

#### Follower statistikasi
```http
GET /api/v1/copy-trading/statistics/user_123
```

**Response:**
```json
{
  "total_trades": 25,
  "open_positions": 3,
  "closed_positions": 22,
  "total_pnl": 450.75,
  "win_rate": 68.18,
  "winning_trades": 15,
  "losing_trades": 7,
  "avg_pnl": 20.49
}
```

---

## 2. Signal Sharing Platform

### Asosiy Xususiyatlar

- **Signal Publishing**: Signallarni e'lon qilish
- **Provider Subscription**: Providerlarga obuna bo'lish
- **Auto-Trading**: Signallarni avtomatik bajarish
- **Signal Filtering**: Moslashtirilgan filtrlar
- **Performance Tracking**: Provider performance kuzatish

### Signal Types

```python
class SignalType(Enum):
    ENTRY = "entry"  # Kirish
    EXIT = "exit"  # Chiqish
    ALERT = "alert"  # Ogohlantirish
    ANALYSIS = "analysis"  # Tahlil
    NEWS = "news"  # Yangiliklar
```

### API Endpoints

#### Provider ro'yxatdan o'tkazish
```http
POST /api/v1/signals/providers/register
Content-Type: application/json

{
  "provider_id": "provider_001",
  "name": "CryptoSignals Pro",
  "description": "Professional crypto trading signals",
  "specialization": ["crypto", "forex"],
  "subscription_fee": 99.0,
  "verified": true
}
```

#### Signal e'lon qilish
```http
POST /api/v1/signals/publish
Content-Type: application/json

{
  "signal_id": "signal_001",
  "provider_id": "provider_001",
  "provider_name": "CryptoSignals Pro",
  "signal_type": "entry",
  "symbol": "BTC/USDT",
  "side": "buy",
  "entry_price": 45000.0,
  "stop_loss": 44000.0,
  "take_profit": 47000.0,
  "timeframe": "4h",
  "strength": "strong",
  "confidence": 85.0,
  "description": "Bullish breakout signal",
  "tags": ["breakout", "trend-following"]
}
```

#### Obuna bo'lish
```http
POST /api/v1/signals/subscribe
Content-Type: application/json

{
  "subscriber_id": "user_123",
  "provider_id": "provider_001",
  "settings": {
    "auto_trade": true,
    "min_confidence": 70.0,
    "symbols_filter": ["BTC/USDT", "ETH/USDT"],
    "max_risk": 0.05
  }
}
```

#### Signallar ro'yxati
```http
GET /api/v1/signals?provider_id=provider_001&active_only=true&limit=50
```

#### Top providerlar
```http
GET /api/v1/signals/providers/top?limit=10&sort_by=success_rate&min_signals=20
```

**Response:**
```json
[
  {
    "provider_id": "provider_001",
    "name": "CryptoSignals Pro",
    "total_signals": 150,
    "successful_signals": 108,
    "success_rate": 72.0,
    "total_subscribers": 450,
    "avg_profit": 2.5,
    "verified": true,
    "premium": true
  }
]
```

---

## 3. Leaderboard System

### Asosiy Xususiyatlar

- **Trader Rankings**: Turli kategoriyalar bo'yicha reytinglar
- **Performance Scoring**: Keng qamrovli performance baholash
- **Trader Tiers**: 7 ta trader darajasi
- **Achievements**: Yutuqlar tizimi
- **Badges**: Badge va mukofotlar

### Trader Tiers

```python
class TraderTier(Enum):
    ROOKIE = "rookie"        # 0-10 trade
    BEGINNER = "beginner"    # 10-50 trade
    INTERMEDIATE = "intermediate"  # 50-200 trade
    ADVANCED = "advanced"    # 200-500 trade
    EXPERT = "expert"        # 500-1000 trade
    MASTER = "master"        # 1000-5000 trade
    LEGEND = "legend"        # 5000+ trade
```

### Rank Categories

```python
class RankCategory(Enum):
    OVERALL = "overall"      # Umumiy
    DAILY = "daily"          # Kunlik
    WEEKLY = "weekly"        # Haftalik
    MONTHLY = "monthly"      # Oylik
    QUARTERLY = "quarterly"  # Kvartalik
    YEARLY = "yearly"        # Yillik
```

### API Endpoints

#### Trader reytingini yangilash
```http
POST /api/v1/leaderboard/update
Content-Type: application/json

{
  "trader_id": "user_123",
  "username": "ProTrader",
  "category": "overall",
  "performance_data": {
    "total_pnl": 12500.0,
    "win_rate": 68.5,
    "sharpe_ratio": 1.8,
    "profit_factor": 2.1,
    "max_drawdown": 15.0,
    "total_trades": 250,
    "winning_trades": 171,
    "losing_trades": 79,
    "total_volume": 150000.0,
    "consistency": 75.0,
    "risk_management": 80.0
  }
}
```

#### Leaderboard ro'yxati
```http
GET /api/v1/leaderboard?category=overall&limit=100&tier=advanced
```

**Response:**
```json
[
  {
    "trader_id": "user_123",
    "username": "ProTrader",
    "rank": 1,
    "previous_rank": 3,
    "rank_change": 2,
    "tier": "expert",
    "score": {
      "total_pnl": 12500.0,
      "win_rate": 68.5,
      "sharpe_ratio": 1.8,
      "overall_score": 82.5
    },
    "total_trades": 250,
    "win_rate": 68.4,
    "verified": true,
    "badges": ["tier_expert", "rank_1st", "winrate_70plus"]
  }
]
```

#### Rising stars
```http
GET /api/v1/leaderboard/rising-stars?category=weekly&limit=10
```

#### Yutuqlar ro'yxati
```http
GET /api/v1/leaderboard/achievements
```

**Response:**
```json
[
  {
    "achievement_id": "first_trade",
    "name": "Birinchi Trade",
    "description": "Birinchi tradeingizni amalga oshiring",
    "icon": "🎯",
    "category": "trading",
    "condition": "1 ta trade qiling",
    "rarity": "common",
    "points": 10
  }
]
```

---

## 4. AutoML Pipeline

### Asosiy Xususiyatlar

- **Automatic Model Selection**: Eng yaxshi modelni avtomatik tanlash
- **Hyperparameter Optimization**: Parameter tuning
- **Multiple Algorithms**: Random Forest, XGBoost, LightGBM, LSTM, va boshqalar
- **Optimization Methods**: Grid Search, Random Search, Bayesian Optimization
- **Feature Importance**: Muhim featurelarni aniqlash

### Model Types

```python
class ModelType(Enum):
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"
    GRU = "gru"
    TRANSFORMER = "transformer"
```

### API Endpoints

#### Avtomatik training
```http
POST /api/v1/automl/train
Content-Type: application/json

{
  "data": {
    "features": [...],
    "labels": [...]
  },
  "task_type": "classification",
  "max_trials": 20
}
```

**Response:**
```json
[
  {
    "run_id": "run_1699876543.123",
    "model_config": {
      "model_type": "xgboost",
      "task_type": "classification"
    },
    "train_score": 0.92,
    "val_score": 0.88,
    "training_time": 45.2,
    "best_hyperparameters": {
      "n_estimators": 200,
      "learning_rate": 0.05,
      "max_depth": 7
    }
  }
]
```

#### Eng yaxshi model
```http
GET /api/v1/automl/best-model?task_name=classification_best
```

#### Feature importance
```http
GET /api/v1/automl/feature-importance/run_1699876543.123?top_n=10
```

#### Recommendations
```http
GET /api/v1/automl/recommendations?task_type=classification&dataset_size=5000&features_count=20
```

**Response:**
```json
{
  "recommended_models": ["xgboost", "lightgbm", "random_forest"],
  "optimization_method": "random_search",
  "max_trials": 20,
  "notes": ["Kichik dataset uchun oddiy modellar tavsiya etiladi"]
}
```

---

## 5. Strategy Marketplace

### Asosiy Xususiyatlar

- **Strategy Listing**: Strategiyalarni ro'yxatlash
- **Multiple Pricing Models**: Turli narxlash modellari
- **Rating System**: Reyting va review tizimi
- **Seller Profiles**: Sotuvchi profillari
- **Purchase Management**: Sotib olishlarni boshqarish

### Pricing Models

```python
class PricingModel(Enum):
    FREE = "free"
    ONE_TIME = "one_time"            # Bir martalik
    SUBSCRIPTION = "subscription"    # Oylik obuna
    REVENUE_SHARE = "revenue_share"  # Foyda ulashish
    PERFORMANCE_BASED = "performance_based"
```

### API Endpoints

#### Sotuvchi ro'yxatdan o'tkazish
```http
POST /api/v1/marketplace/sellers/register
Content-Type: application/json

{
  "seller_id": "seller_001",
  "username": "StrategyMaster",
  "verified": true
}
```

#### Strategiya yuborish
```http
POST /api/v1/marketplace/strategies/submit
Content-Type: application/json

{
  "strategy_id": "strat_001",
  "seller_id": "seller_001",
  "seller_name": "StrategyMaster",
  "name": "Advanced Grid Trading",
  "description": "Highly profitable grid trading strategy",
  "category": "grid_trading",
  "pricing_model": "one_time",
  "price": 299.0,
  "win_rate": 75.0,
  "sharpe_ratio": 2.3,
  "supported_markets": ["crypto", "forex"],
  "min_capital": 1000.0,
  "risk_level": "medium",
  "tags": ["grid", "automated", "tested"]
}
```

#### Strategiyalar ro'yxati
```http
GET /api/v1/marketplace/strategies?category=grid_trading&min_rating=4.0&sort_by=rating&limit=20
```

**Response:**
```json
[
  {
    "strategy_id": "strat_001",
    "seller_name": "StrategyMaster",
    "name": "Advanced Grid Trading",
    "category": "grid_trading",
    "pricing_model": "one_time",
    "price": 299.0,
    "win_rate": 75.0,
    "avg_profit": 3.2,
    "sharpe_ratio": 2.3,
    "avg_rating": 4.7,
    "total_sales": 150,
    "verified": true,
    "featured": true
  }
]
```

#### Strategiya sotib olish
```http
POST /api/v1/marketplace/purchase
Content-Type: application/json

{
  "strategy_id": "strat_001",
  "buyer_id": "user_123",
  "payment_info": {
    "method": "card",
    "amount": 299.0
  }
}
```

#### Reyting qo'shish
```http
POST /api/v1/marketplace/ratings/add
Content-Type: application/json

{
  "rating_id": "rating_001",
  "strategy_id": "strat_001",
  "buyer_id": "user_123",
  "buyer_name": "TradingPro",
  "rating": 5,
  "review": "Ajoyib strategiya! Juda yaxshi natijalar",
  "performance_met": true,
  "ease_of_use": 5,
  "support_quality": 5
}
```

---

## 6. Reputation System

### Asosiy Xususiyatlar

- **Trust Score Calculation**: 5 komponentli trust score
- **Review System**: Reviewlar va reytinglar
- **Verification Levels**: 4 darajali tasdiqlash
- **Trust Tiers**: 5 darajali ishonch darajasi
- **Badges System**: Avtomatik badge tizimi

### Trust Score Components

1. **Trading History Score** (30%): Trading tajriba va natijalar
2. **Verification Score** (20%): Tasdiqlash darajasi
3. **Community Score** (25%): Jamoa baholari
4. **Consistency Score** (15%): Izchillik
5. **Transparency Score** (10%): Shaffoflik

### Verification Levels

```python
class VerificationLevel(Enum):
    NONE = "none"
    EMAIL = "email"
    PHONE = "phone"
    ID_DOCUMENT = "id_document"
    FULL = "full"
```

### Trust Tiers

```python
class TrustTier(Enum):
    UNTRUSTED = "untrusted"    # 0-20
    LOW = "low"                # 20-40
    MEDIUM = "medium"          # 40-60
    HIGH = "high"              # 60-80
    VERY_HIGH = "very_high"    # 80-100
```

### API Endpoints

#### Review yuborish
```http
POST /api/v1/reputation/reviews/submit
Content-Type: application/json

{
  "review_id": "review_001",
  "reviewer_id": "user_123",
  "reviewer_name": "TradingPro",
  "target_id": "user_456",
  "target_type": "trader",
  "rating": 5,
  "title": "Ajoyib trader",
  "content": "Professional va ishonchli trader",
  "pros": ["Professional", "Responsive", "Good results"],
  "cons": [],
  "verified": true
}
```

#### Trust score hisoblash
```http
POST /api/v1/reputation/trust-score/calculate
Content-Type: application/json

{
  "user_id": "user_123",
  "username": "ProTrader",
  "trading_data": {
    "total_trades": 500,
    "win_rate": 72.0,
    "total_pnl": 15000.0,
    "sharpe_ratio": 2.1,
    "days_active": 250,
    "account_age_days": 365,
    "max_drawdown": 10.0,
    "public_profile": true,
    "shared_statistics": true,
    "verified_trades_pct": 95.0,
    "reviews_given": 25
  }
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "username": "ProTrader",
  "trading_history_score": 85.0,
  "verification_score": 100.0,
  "community_score": 78.5,
  "consistency_score": 82.0,
  "transparency_score": 90.0,
  "overall_score": 85.65,
  "trust_tier": "very_high",
  "total_reviews_received": 45,
  "avg_review_rating": 4.6,
  "verification_level": "full",
  "badges": [
    "trust_very_high",
    "fully_verified",
    "expert_trader",
    "highly_reviewed",
    "top_rated",
    "veteran"
  ]
}
```

#### Verification so'rovi yuborish
```http
POST /api/v1/reputation/verification/submit
Content-Type: application/json

{
  "user_id": "user_123",
  "verification_type": "id_document",
  "documents": ["id_front.jpg", "id_back.jpg"]
}
```

#### Eng ishonchli userlar
```http
GET /api/v1/reputation/top-trusted?limit=50&min_tier=high
```

---

## Foydalanish Misollari

### 1. Copy Trading Boshlash

```python
import requests

# Leader topish
response = requests.get(
    "http://localhost:8000/api/v1/copy-trading/leaders/top",
    params={"limit": 10, "sort_by": "sharpe_ratio", "min_trades": 100}
)
leaders = response.json()

# Eng yaxshi leaderni tanlash
best_leader = leaders[0]

# Copy tradingni boshlash
response = requests.post(
    "http://localhost:8000/api/v1/copy-trading/start",
    json={
        "follower_id": "user_123",
        "leader_id": best_leader["leader_id"],
        "settings": {
            "mode": "proportional",
            "allocation_amount": 5000.0,
            "max_position_size": 500.0,
            "copy_sl_tp": True,
            "max_open_positions": 3
        }
    }
)
```

### 2. Signal Platformasidan Foydalanish

```python
# Top providerni topish
response = requests.get(
    "http://localhost:8000/api/v1/signals/providers/top",
    params={"limit": 5, "sort_by": "success_rate"}
)
providers = response.json()

# Providerga obuna bo'lish
response = requests.post(
    "http://localhost:8000/api/v1/signals/subscribe",
    json={
        "subscriber_id": "user_123",
        "provider_id": providers[0]["provider_id"],
        "settings": {
            "auto_trade": True,
            "min_confidence": 75.0,
            "symbols_filter": ["BTC/USDT", "ETH/USDT"]
        }
    }
)

# Signallarni kuzatish
response = requests.get(
    "http://localhost:8000/api/v1/signals/subscriber/user_123",
    params={"limit": 20}
)
signals = response.json()
```

### 3. Leaderboardda O'rningizni Tekshirish

```python
# O'z reytingingizni tekshirish
response = requests.get(
    "http://localhost:8000/api/v1/leaderboard/trader/user_123",
    params={"category": "overall"}
)
my_rank = response.json()

print(f"Rank: {my_rank['rank']}")
print(f"Tier: {my_rank['tier']}")
print(f"Score: {my_rank['score']['overall_score']}")

# Atrofdagi traderlar
response = requests.get(
    "http://localhost:8000/api/v1/leaderboard/nearby/user_123",
    params={"category": "overall", "range_size": 5}
)
nearby = response.json()

# Yutuqlaringiz
response = requests.get(
    "http://localhost:8000/api/v1/leaderboard/achievements/user_123"
)
achievements = response.json()
```

---

## Konfiguratsiya

### Environment Variables

```bash
# API Server
PORT=8000
HOST=0.0.0.0
WORKERS=4

# Platform Settings
PLATFORM_FEE_PCT=20.0  # Marketplace komissiyasi
```

---

## Xatoliklarni Bartaraf Qilish

### Copy Trading Issues

**Problem**: Leader tradelari ko'chirilmayapti
**Yechim**:
1. Copy settings enabled ekanligini tekshiring
2. Symbol filter sozlamalarini ko'rib chiqing
3. Max open positions limitini tekshiring

### Signal Platform Issues

**Problem**: Signallar kelmayapti
**Yechim**:
1. Obuna active ekanligini tekshiring
2. Min confidence va strength filtrlarini pastroq qilish
3. Notification enabled ekanligini tasdiqlash

### AutoML Issues

**Problem**: Training juda sekin
**Yechim**:
1. max_trials sonini kamaytiring
2. Optimization method ni random_search ga o'zgartiring
3. Dataset hajmini kichikroq qiling

---

## Statistika

### BOSQICH 10 Natijalari

- **Umumiy kod qatorlari**: ~4,500 qator
- **Modullar**: 6 ta
- **API endpointlar**: 60+
- **Funksiyalar**: 150+
- **Klasslar**: 25+

### Fayl Tuzilishi

```
code/
├── social/
│   ├── __init__.py                (31 qator)
│   ├── copy_trading_engine.py     (665 qator)
│   ├── signal_platform.py         (745 qator)
│   ├── leaderboard_system.py      (747 qator)
│   ├── automl_pipeline.py         (765 qator)
│   ├── strategy_marketplace.py    (756 qator)
│   └── reputation_system.py       (828 qator)
└── main.py                        (yangilangan, 400+ qator qo'shildi)
```

---

## Keyingi Qadamlar

BOSQICH 11 da qo'shiladi:
- Forex Market Integration
- REITs Trading
- Payment Gateway (Stripe)
- Multi-Currency Support
- Tax Reporting
- Webhook Integrations

---

**Muallif**: MiniMax Agent  
**Sana**: 2025-11-04  
**Versiya**: 1.0.0
