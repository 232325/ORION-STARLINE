# Orion Starline Onboarding Tizimi

Global foydalanuvchilar uchun AI-powered onboarding tizimi. Bu tizim foydalanuvchilarni Orion Starline trading platformasiga bosqichma-bosqich tanishtirish uchun mo'ljallangan.

## Asosiy Imkoniyatlar

### 1. Foydalanuvchi Profili
- UUID-based user ID
- Ko'p tilli qo'llab-quvvatlash (Uzbek/English)
- Skill level assessment
- Progress tracking

### 2. Skill Assessment
- 3 ta asosiy savol
- Automatic skill level determination (Beginner/Intermediate/Advanced)
- Personalized experience delivery

### 3. Welcome Tour
- Platform introduction
- Step-by-step guidance
- Progress visualization
- Multi-language content

### 4. Demo Trading
- **$100,000 virtual balance**
- Real-time mock price feeds
- Major currency pairs (EURUSD, GBPUSD, USDJPY, XAUUSD, XAGUSD, BTCUSD)
- Live P&L tracking
- Performance analytics
- Risk-free learning environment

### 5. AI Assistant
- Context-aware responses
- Multi-language interaction
- Real-time help and guidance
- Trading education

### 6. Personalization
- Skill-based strategy recommendations
- Market selection suggestions
- Risk level customization
- Learning path adaptation

### 7. Progress Tracking
- 8-step onboarding process
- Percentage completion
- Step management
- Completion badges

### 8. Gamification
- User levels (Level 1-4)
- Achievement badges
- Point system
- Progress milestones

## Onboarding Qadamlari

1. **Registration & Profile Setup**
   - User creation
   - Language preference
   - Initial profile setup

2. **Skill Assessment**
   - Experience evaluation
   - Market knowledge test
   - Risk tolerance assessment

3. **Welcome Tour**
   - Platform introduction
   - Feature overview
   - Navigation guide

4. **Demo Trading Session**
   - Virtual balance allocation
   - Trading practice
   - Performance monitoring

5. **AI Assistant Introduction**
   - Assistant capabilities
   - Interactive help
   - First questions

6. **Personal Recommendations**
   - Strategy suggestions
   - Market recommendations
   - Learning paths

7. **Community Introduction**
   - Social features
   - Leaderboards
   - Mentorship programs

8. **Live Trading Preparation**
   - Account verification
   - Risk management setup
   - First live trade guidance

## Texnik Detallar

### Data Models

#### UserProfile
```python
@dataclass
class UserProfile:
    user_id: str
    name: str
    email: str
    preferred_language: Language
    skill_level: UserLevel
    interests: List[str]
    onboarding_completed: bool
    current_step: OnboardingStep
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
```

#### DemoTradingSession
```python
@dataclass
class DemoTradingSession:
    user_id: str
    virtual_balance: float
    positions: List[MockPosition]
    performance_metrics: Dict[str, float]
    start_time: datetime
    last_updated: datetime
```

#### MockPosition
```python
@dataclass
class MockPosition:
    id: str
    symbol: str
    side: str  # "long" or "short"
    entry_price: float
    current_price: float
    quantity: float
    timestamp: datetime
    pnl: float
```

### Asosiy Funksiyalar

```python
# User management
create_user_profile(name, email, preferred_language)
get_onboarding_status(user_id)

# Assessment
conduct_skill_assessment(user_id, answers)

# Demo trading
start_demo_trading(user_id)
execute_demo_trade(user_id, symbol, side, quantity)
update_demo_positions(user_id)
close_demo_position(user_id, position_id)

# AI Assistant
get_ai_assistant_response(user_id, message)

# Personalization
get_personalized_recommendations(user_id)

# Progress management
complete_onboarding_step(user_id, step)
get_gamification_data(user_id)

# Market data
get_mock_market_data()
```

## Market Data

Mock market data quyidagi instrumentlarni qamrab oladi:

- **Forex**: EURUSD, GBPUSD, USDJPY
- **Metals**: XAUUSD (Gold), XAGUSD (Silver)
- **Crypto**: BTCUSD (Bitcoin)

Har bir instrument uchun:
- Real-time price simulation
- Price change tracking
- Market sentiment analysis
- Trending instruments identification

## Multi-Language Support

### Uzbek Content
- Platform introduction
- Assessment questions
- AI responses
- Trading education

### English Content
- Full feature set
- Professional terminology
- International standards
- Global accessibility

## Performance Metrics

Demo trading session uchun quyidagi metrikalar kuzatiladi:

- Total trades executed
- Winning/losing trade ratio
- Win rate percentage
- Total P&L
- Maximum drawdown
- Session duration
- Balance changes

## Gamification System

### User Levels
- **Level 1**: 0-25% progress
- **Level 2**: 26-50% progress  
- **Level 3**: 51-75% progress
- **Level 4**: 76-100% progress

### Badges
- "First Steps" - Registration complete
- "Halfway There" - 50% progress
- "Almost Ready" - 75% progress
- "Onboarding Complete" - 100% progress
- "Active Trader" - 5+ demo trades
- "Winning Streak" - 60%+ win rate

### Points System
- 10 points per progress percentage
- Bonus points for achievements
- Level-based progression

## Security va Data Protection

- UUID-based user identification
- No sensitive data storage
- Session-based data management
- Privacy-focused design

## Foydalanish

```python
from onboarding_engine import OnboardingEngine, Language

# Engine yaratish
engine = OnboardingEngine()

# Foydalanuvchi yaratish
user = engine.create_user_profile(
    "Aziz Ahmed", 
    "aziz@example.com", 
    Language.UZBEK
)

# Demo trading boshlash
demo_session = engine.start_demo_trading(user.user_id)

# Trade bajarish
trade_result = engine.execute_demo_trade(
    user.user_id, "EURUSD", "long", 1000
)

# AI Assistant
ai_response = engine.get_ai_assistant_response(
    user.user_id, "Demo trading yordam kerak"
)
```

## Demo Foydalanish

Onboarding tizimini test qilish uchun:

```bash
cd /workspace/orion-starline/backend/ai_modules
python onboarding_engine.py
```

Yoki comprehensive demo:

```bash
python demo.py
```

Va tanlang: `2` (Onboarding System Demo)

## Integration

Bu onboarding engine quyidagi tizimlar bilan integratsiya qilinishi mumkin:

- Supabase database
- WebSocket real-time updates
- Frontend React components
- Authentication systems
- Payment gateways
- Trading APIs

## Keyingi Rivojlantirishlar

1. **Database Integration**
   - User data persistence
   - Session history
   - Analytics tracking

2. **Real-time Features**
   - WebSocket integration
   - Live notifications
   - Progress updates

3. **Advanced Personalization**
   - ML-based recommendations
   - Behavioral analysis
   - Adaptive learning paths

4. **Social Features**
   - Community integration
   - Leaderboards
   - Peer learning

5. **Mobile App Support**
   - React Native integration
   - Mobile-specific UI
   - Push notifications

## Muallif

**Orion Starline Development Team**  
AI-Powered Trading Platform  
2025

---

*Bu onboarding tizimi Orion Starline trading platformining bir qismi bo'lib, global foydalanuvchilar uchun optimallashtirilgan.*