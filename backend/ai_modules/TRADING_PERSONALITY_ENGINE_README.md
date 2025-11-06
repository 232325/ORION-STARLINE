# Trading Personality Engine

Ushbu loyiha treyderlarning shaxsiyatini aniqlash, UI ni moslashtirish va kengaytirilgan xulq-atvor tahlilini amalga oshirish uchun mo'ljallangan.

## 📁 Fayl Tuzilishi

```
ai_modules/
├── trading_personality.py           # Asosiy shaxsiyat aniqlash moduli
├── ui_customizer.py                 # UI moslashtirish moduli  
├── personality_analyzer.py          # Kengaytirilgan tahlil moduli
└── TRADING_PERSONALITY_ENGINE_COMPLETION_REPORT.md  # Hisobot
```

## 🚀 Tez Boshlanish

### 1. Personality Detection
```python
from trading_personality import TradingPersonalityEngine, TradingPersonalityType
import json

# Engine yaratish
engine = TradingPersonalityEngine()

# Savdo ma'lumotlari
trading_data = {
    "trader_id": "user_123",
    "trades": [
        {
            "entry_time": "2025-11-04T10:00:00",
            "exit_time": "2025-11-04T10:30:00", 
            "profit": 0.015,
            "strategy": "scalping"
        },
        {
            "entry_time": "2025-11-04T11:00:00",
            "exit_time": "2025-11-04T12:00:00",
            "profit": -0.01,
            "strategy": "scalping"
        }
    ],
    "days_active": 30,
    "win_rate": 0.65,
    "avg_profit_per_trade": 0.012,
    "max_drawdown": 0.12,
    "sharpe_ratio": 1.4
}

# Shaxsiyat aniqlash
profile = engine.detect_personality(trading_data)

print(f"Shaxsiyat: {profile.personality_type.value}")
print(f"Risk tolerance: {profile.risk_tolerance.value}")
print(f"Timeframe: {profile.timeframe_preference.value}")
```

### 2. UI Customization
```python
from ui_customizer import UICustomizer

# UI Customizer yaratish
customizer = UICustomizer()

# Personality ga mos UI sozlamalar
ui_settings = customizer.create_ui_settings(profile)

# Theme colors
print(f"Primary Color: {ui_settings.primary_color}")
print(f"Background: {ui_settings.background_color}")
print(f"Layout: {ui_settings.layout_density.value}")

# CSS generatsiya
css = customizer.apply_theme_to_css(ui_settings)
print(css)

# Responsive config
responsive = customizer.generate_responsive_config(ui_settings)
print(json.dumps(responsive, indent=2))
```

### 3. Advanced Analysis
```python
from personality_analyzer import PersonalityAnalyzer
from datetime import datetime, timedelta

# Advanced Analyzer
analyzer = PersonalityAnalyzer()

# Qo'shimcha ma'lumotlar
detailed_data = {
    "trades": [
        {
            "entry_time": "2025-11-04T10:00:00",
            "exit_time": "2025-11-04T10:30:00",
            "profit": 0.015,
            "position_size": 1000,
            "analysis_time": "2025-11-04T09:55:00",
            "execution_time": "2025-11-04T10:00:00"
        }
    ],
    "performance": {
        "win_rate": 0.65,
        "avg_profit": 0.012,
        "max_drawdown": 0.12
    }
}

behavioral_data = {
    "research_hours": 2.5,
    "tutorial_completion": 3,
    "strategy_reading": 5
}

social_data = {
    "behavior_type": "collaborator",
    "influence_score": 0.4,
    "collaboration_preference": 0.7,
    "network_size": 15
}

# Kengaytirilgan tahlil
advanced_profile = analyzer.analyze_advanced_personality(
    base_profile=profile,
    detailed_trading_data=detailed_data,
    behavioral_observations=behavioral_data,
    social_data=social_data
)

print(f"Konfidentsialik: {advanced_profile.confidence_score:.1%}")
print(f"Ijtimoiy xulq-atvor: {advanced_profile.social_profile.social_behavior.value}")
print(f"Emotional naqshlar: {len(advanced_profile.emotional_patterns)} ta")
```

## 📊 Personality Turlari

### 1. Scalper
- **Tavsif:** Qisqa muddatli, yuqori chastotali savdolar
- **Holding Time:** 1-15 daqiqa
- **Trades/day:** 20-200
- **Risk:** O'rta-Yuqori
- **Timeframes:** Seconds, Minutes
- **UI:** Compact, Dark theme
- **Assets:** Forex, Crypto, Futures

### 2. Day Trader  
- **Tavsif:** Kun ichi pozitsiyalar, o'rta muddat
- **Holding Time:** 1-8 soat
- **Trades/day:** 2-20
- **Risk:** O'rta-Yuqori
- **Timeframes:** Minutes, Hours
- **UI:** Comfortable, Dark theme
- **Assets:** Stocks, Options, Crypto

### 3. Swing Trader
- **Tavsif:** Ko'p kunlik pozitsiyalar
- **Holding Time:** 1 kun - 1 hafta
- **Trades/week:** 1-10
- **Risk:** Past-O'rta-Yuqori
- **Timeframes:** Hours, Days
- **UI:** Comfortable, Light theme
- **Assets:** Stocks, Commodities, Indices

### 4. Position Trader
- **Tavsif:** Uzun muddatli pozitsiyalar
- **Holding Time:** 1 hafta - 6 oy
- **Trades/month:** 1-10
- **Risk:** Past-O'rta
- **Timeframes:** Days, Weeks, Months
- **UI:** Spacious, Light theme
- **Assets:** Stocks, Bonds, Real Estate

### 5. Algorithmic Trader
- **Tavsif:** Tizimli, algoritmik savdolar
- **Holding Time:** 1 daqiqa - 1 kun
- **Trades/day:** 1-1000
- **Risk:** O'rta-Yuqori
- **Timeframes:** Seconds, Minutes, Hours
- **UI:** High Contrast, Compact
- **Assets:** Barchasi

### 6. Value Investor
- **Tavsif:** Asosiy tahlilga asoslangan qiymatli sarmoyasi
- **Holding Time:** 6 oy - 5 yil
- **Trades/year:** 2-20
- **Risk:** Past
- **Timeframes:** Weeks, Months
- **UI:** Minimal, Spacious
- **Assets:** Stocks, Bonds, Real Estate

### 7. Growth Investor
- **Tavsif:** Momentum va o'sish potentsiali bo'yicha
- **Holding Time:** 6 oy - 1 yil
- **Trades/year:** 4-30
- **Risk:** O'rta-Yuqori
- **Timeframes:** Days, Weeks
- **UI:** Colorful, Comfortable
- **Assets:** Growth Stocks, Tech, Emerging Markets

### 8. Contrarian
- **Tavsif:** Qarshi sentiment bo'yicha savdolar
- **Holding Time:** 1 hafta - 1 oy
- **Trades/month:** 2-15
- **Risk:** O'rta-Yuqori
- **Timeframes:** Days, Weeks
- **UI:** Medium density
- **Assets:** Barchasi

### 9. Conservative
- **Tavsif:** Past risk, barqaror daromad
- **Holding Time:** 6 oy - 10 yil
- **Trades/year:** 1-8
- **Risk:** Past
- **Timeframes:** Weeks, Months
- **UI:** Spacious, Light theme
- **Assets:** Bonds, Dividend Stocks, REITs

### 10. Aggressive
- **Tavsif:** Yuqori risk, yuqori daromad
- **Holding Time:** 1 soat - 1 hafta
- **Trades/day:** 5-50
- **Risk:** Yuqori
- **Timeframes:** Minutes, Hours, Days
- **UI:** High Contrast, Compact
- **Assets:** Crypto, Options, Forex, Small Cap

## 🔧 Advanced Features

### Behavioral Pattern Recognition
```python
# Emotional patterns
patterns = analyzer._analyze_emotional_patterns(profile, trading_data)
for pattern in patterns:
    print(f"Pattern: {pattern.pattern_type}")
    print(f"Confidence: {pattern.confidence:.1%}")
    print(f"Context: {pattern.context}")

# Decision patterns  
decision_patterns = analyzer._analyze_decision_patterns(profile, trading_data)
for pattern in decision_patterns:
    print(f"Decision Type: {pattern.pattern_type}")
    print(f"Speed: {pattern.intensity:.1f}")
```

### Social Profile Analysis
```python
# Ijtimoiy profil
social_profile = advanced_profile.social_profile
print(f"Social Behavior: {social_profile.social_behavior.value}")
print(f"Influence Score: {social_profile.influence_score:.1%}")
print(f"Collaboration: {social_profile.collaboration_preference:.1%}")
print(f"Network Size: {social_profile.network_size} people")
```

### Similar Traders Matching
```python
# O'xshash treyderlarni topish
similar_traders = analyzer.find_similar_traders(advanced_profile, top_k=5)
for trader_id, similarity in similar_traders:
    print(f"Similar trader: {trader_id} (Similarity: {similarity:.1%})")
```

### Learning Opportunities
```python
# O'rganish imkoniyatlari
opportunities = analyzer.suggest_learning_opportunities(advanced_profile)
for opp in opportunities:
    print(f"Topic: {opp['topic']}")
    print(f"Type: {opp['type']}")
    print(f"Priority: {opp['priority']}")
    print(f"Time: {opp['estimated_time']}")
```

## 🎨 UI Customization Examples

### Theme Generation
```python
# Scalper uchun dark theme
scalper_profile = create_sample_profile("scalper_001", "scalper")
ui_settings = customizer.create_ui_settings(scalper_profile)

print(f"Theme: {ui_settings.theme.value}")
print(f"Primary: {ui_settings.primary_color}")  # #FF4444
print(f"Background: {ui_settings.background_color}")  # #0A0A0A

# CSS variables
css = customizer.apply_theme_to_css(ui_settings)
print(css[:300])
```

### Widget Layout
```python
# Widget layout olish
layout = ui_settings.widget_layout
print(f"Layout type: {layout['type']}")
print(f"Columns: {layout['columns']}")
print(f"Refresh rate: {layout['settings']['refresh_interval']}ms")

# Widgetlar
for widget in layout['widgets']:
    print(f"- {widget['id']}: {widget['type']}")
```

### Responsive Design
```python
# Responsive config
responsive = customizer.generate_responsive_config(ui_settings)
print(f"Breakpoints: {list(responsive['breakpoints'].keys())}")
print(f"Adaptations: {responsive['adaptations']}")

# Mobile layout
mobile_layout = responsive['layouts']['mobile']
print(f"Mobile type: {mobile_layout['type']}")
print(f"Navigation: {mobile_layout['navigation']}")
```

## 📈 Performance Tracking

### Goal Setting
```python
# Progress tracking
tracking = engine.get_progress_tracking(profile)
print("Key Metrics:", tracking['key_metrics'])
print("Weekly Goals:", tracking['milestone_goals']['weekly'])
print("Monthly Goals:", tracking['milestone_goals']['monthly'])
```

### Adaptive Personalization
```python
# Adaptiv yangilash
new_trading_data = {
    "trades": [
        {
            "entry_time": "2025-11-04T15:00:00",
            "exit_time": "2025-11-04T15:20:00",
            "profit": 0.02
        }
    ],
    "performance": {
        "win_rate": 0.7,
        "avg_profit": 0.015,
        "max_drawdown": 0.1
    }
}

updated_profile = engine.adaptive_personalization(profile, new_trading_data)
print(f"Updated personality: {updated_profile.personality_type.value}")
print(f"New win rate: {updated_profile.win_rate:.1%}")
```

## 🤝 Mentor Matching

```python
# Available mentors
mentors = [create_sample_profile(f"mentor_{i}", "day_trader") for i in range(5)]

# Best match
mentor_match = engine.suggest_mentor_match(profile, mentors)
if mentor_match:
    print(f"Best mentor: {mentor_match.trader_id}")
    print(f"Mentor type: {mentor_match.personality_type.value}")
    print(f"Mentor win rate: {mentor_match.win_rate:.1%}")
    print(f"Sharpe ratio: {mentor_match.sharpe_ratio}")
```

## 📊 Strategy Recommendations

```python
# Tavsiya qilingan strategiyalar
strategies = engine.get_recommended_strategies(profile)
for strategy in strategies:
    print(f"Strategy: {strategy['name']}")
    print(f"Description: {strategy['description']}")
    print(f"Timeframe: {strategy['timeframe']}")
    print(f"Risk per trade: {strategy['risk_per_trade']:.1%}")
    print(f"Take profit: {strategy['take_profit']:.1%}")
    print()
```

## 🔍 Export va Data Management

### UI Config Export
```python
# JSON format
json_config = customizer.export_ui_config("user_123", "json")
print(json_config[:200])

# CSS format  
css_config = customizer.export_ui_config("user_123", "css")
print(css_config[:200])
```

### Personality Insights Export
```python
# Summary format
insights = analyzer.export_personality_insights(advanced_profile, "summary")
print(insights)

# JSON format
json_insights = analyzer.export_personality_insights(advanced_profile, "json")
print(json.dumps(json.loads(json_insights)['social_profile'], indent=2))
```

## 🛠️ Configuration

### Data Directory
```python
# Default data directory
data_dir = "/workspace/orion-starline/data"
engine = TradingPersonalityEngine(data_dir=data_dir)
```

### Custom Personality Types
```python
# Yangi personality turini qo'shish
TradingPersonalityType.MY_CUSTOM = "my_custom"
```

## ⚙️ Error Handling

```python
try:
    # Personality detection
    profile = engine.detect_personality(trading_data)
    print("Success!")
except ValueError as e:
    print(f"Input error: {e}")
except Exception as e:
    print(f"System error: {e}")
```

## 🚀 Production Usage

### Web API Integration
```python
# Flask example
from flask import Flask, request, jsonify

app = Flask(__name__)
engine = TradingPersonalityEngine()

@app.route('/api/personality/detect', methods=['POST'])
def detect_personality():
    data = request.json
    profile = engine.detect_personality(data)
    return jsonify(profile.to_dict())

@app.route('/api/ui/customize/<trader_id>', methods=['GET'])
def get_ui_settings(trader_id):
    settings = customizer.get_ui_settings(trader_id)
    if settings:
        return jsonify(settings.__dict__)
    return jsonify({"error": "Settings not found"}), 404
```

### Database Integration
```python
# SQLAlchemy example (suggested)
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TraderProfile(Base):
    __tablename__ = 'trader_profiles'
    
    trader_id = Column(String, primary_key=True)
    personality_type = Column(String)
    risk_tolerance = Column(String)
    confidence_score = Column(Float)
    created_at = Column(DateTime)
```

## 🔐 Security va Privacy

- **Data Encryption:** Ma'lumotlar encrypted saqlanadi
- **Access Control:** Role-based permissions
- **Privacy First:** Minimal data collection
- **GDPR Ready:** Data deletion support

## 📚 API Reference

### TradingPersonalityEngine
- `detect_personality(trading_data, behavioral_data=None)` → PersonalityProfile
- `get_personality_config(personality_type)` → Dict
- `get_recommended_strategies(profile)` → List[Dict]
- `get_ui_customization(profile)` → Dict
- `analyze_personality_match(profile1, profile2)` → float
- `suggest_mentor_match(profile, available_mentors)` → PersonalityProfile
- `adaptive_personalization(profile, new_data)` → PersonalityProfile

### UICustomizer  
- `create_ui_settings(profile)` → UISettings
- `update_ui_settings(trader_id, updates)` → UISettings
- `get_ui_settings(trader_id)` → UISettings
- `apply_theme_to_css(settings)` → str
- `generate_responsive_config(settings)` → Dict
- `export_ui_config(trader_id, format="json")` → str

### PersonalityAnalyzer
- `analyze_advanced_personality(base_profile, detailed_data, behavioral_obs=None, social_data=None)` → AdvancedPersonality
- `find_similar_traders(target_profile, top_k=5)` → List[Tuple[str, float]]
- `suggest_learning_opportunities(profile)` → List[Dict]
- `adaptive_learning_recommendation(profile, recent_performance)` → Dict
- `export_personality_insights(profile, format="json")` → str

## 🎉 Test Data

```python
# Test uchun sample data
sample_data = {
    "trader_id": "test_user",
    "trades": [
        {
            "entry_time": "2025-11-04T10:00:00",
            "exit_time": "2025-11-04T10:30:00",
            "profit": 0.015,
            "strategy": "scalping"
        }
    ],
    "days_active": 30,
    "win_rate": 0.65,
    "avg_profit_per_trade": 0.012,
    "max_drawdown": 0.12,
    "sharpe_ratio": 1.4
}
```

## 🐛 Troubleshooting

### Common Issues:
1. **ImportError:** sklearn topilmadi → `pip install scikit-learn`
2. **FileNotFoundError:** Data directory yaratilmagan → Automated creation
3. **TypeError:** Personality type not found → Check enum values
4. **JSON Error:** Malformed data → Check input format

### Debug Mode:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch  
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Email:** support@trading-personality.com
- **Documentation:** https://docs.trading-personality.com
- **Discord:** https://discord.gg/trading-personality

---

**Trading Personality Engine** - Treyding tajribangizni shaxsiylashtiring! 🚀