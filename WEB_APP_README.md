# 🚀 Orion Starline - Full-Stack Trading Platform

To'liq full-stack web ilovasi React frontend o'rniga Python-based Streamlit interface va Supabase backend bilan.

## 📋 Funktsiyalar

### ✨ Asosiy Imkoniyatlar
- **🔐 Foydalanuvchi Autentifikatsiyasi** - Supabase Auth bilan xavfsiz login
- **📊 Real-time Dashboard** - Live ma'lumotlar va interaktiv grafiklar  
- **💹 Trading Interface** - Buy/Sell orderlar, real-time narxlar
- **💼 Portfolio Management** - Portfel boshqaruvi va performance
- **🔗 Wallet Integration** - Cryptocurrency wallet ulash
- **📈 Analytics Dashboard** - Q avançado analytics va risk management
- **📱 Responsive Design** - Barcha qurilmalarda ishlaydi
- **⚡ Real-time Data** - WebSocket orqali live ma'lumotlar
- **🛡️ Production Ready** - Error handling va logging

### 🎯 Imkoniyatlar
- **AI Trading Assistant** - GPT bilan savol javoblash
- **Portfolio Analytics** - Performance va risk metriklari
- **Market Predictions** - Texnik tahlil signallari
- **Risk Management** - Avtomatik risk baholash
- **Multi-Asset Support** - Crypto, Stock, Forex
- **Social Trading** - Copy trading va leaderboard
- **Voice Commands** - Ovozli buyruqlar (koshib)

## 🏗️ Arxitektura

```
Orion-Starline/
├── frontend/
│   └── web_app.py           # Streamlit frontend interface
├── backend/
│   └── web_app_backend.py   # FastAPI backend server
├── requirements.txt         # Python dependencies
├── .env.template           # Environment variables template
└── README.md              # This file
```

## 🚀 Tez boshlanish

### 1. Muhitni sozlash

```bash
# Reponi klon qilish
git clone https://github.com/your-username/orion-starline.git
cd orion-starline

# Virtual environment yaratish
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Dependencies o'rnatish
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
# .env faylini yaratish
cp .env.template .env

# Faylni tahrirlash va kerakli qiymatlarni kiritish
nano .env
```

### 3. Supabase Sozlash

1. [Supabase](https://supabase.com) da project yarating
2. Authentication ni yoqib oling
3. Database tables yarating:
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trades table
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    quantity DECIMAL NOT NULL,
    price DECIMAL NOT NULL,
    total_value DECIMAL NOT NULL,
    status TEXT DEFAULT 'executed',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Positions table
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    symbol TEXT NOT NULL,
    quantity DECIMAL NOT NULL,
    average_price DECIMAL NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market data table
CREATE TABLE market_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    price DECIMAL NOT NULL,
    change_24h DECIMAL,
    volume BIGINT,
    market_cap BIGINT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Ilovani ishga tushirish

#### Backend Server (FastAPI)
```bash
cd backend
python web_app_backend.py
# yoki
uvicorn web_app_backend:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend (Streamlit)
```bash
cd frontend
streamlit run web_app.py
```

## 📚 API Documentation

### Authentication Endpoints
```
POST /auth/register    # Foydalanuvchi ro'yxatdan o'tishi
POST /auth/login       # Login qilish
GET  /health          # API salomatlik tekshiruvi
```

### Trading Endpoints
```
POST /trading/order   # Order bajarish
GET  /portfolio/{user_id}  # Portfolioni olish
GET  /analytics/risk/{user_id}  # Risk metriklari
```

### Market Data Endpoints
```
GET /market/data/{symbol}    # Market ma'lumotlari
GET /signals/trading         # Trading signallari
GET /admin/stats            # Tizim statistikasi
```

### WebSocket Endpoints
```
WS /ws/market   # Real-time market data
```

## 🎨 Foydalanish Qo'llanmasi

### 1. Tizimga kirish
1. Streamlit ilovani oching
2. "Login" sahifasiga o'ting
3. Email va parolni kiriting
4. "Login" tugmasini bosing

### 2. Dashboard
- **Portfolio Value**: Joriy portfel qiymati
- **Daily P&L**: Kunlik foyda/zarar
- **Active Positions**: Ochiq pozitsiyalar soni
- **Win Rate**: G'olib bo'lgan savdolar foizi
- **Real-time Market Data**: Live narxlar jadvali

### 3. Trading
1. **Symbol tanlang** - BTC/USD, ETH/USD, AAPL, GOOGL
2. **Side tanlang** - Buy yoki Sell
3. **Quantity** - Savdo miqdorini kiriting
4. **Order Type** - Market, Limit, Stop
5. **Execute Order** - Buyrug'ni bajarish

### 4. Portfolio Management
- **Current Positions** - Joriy pozitsiyalar ro'yxati
- **Performance Metrics** - Performance ko'rsatkichlari
- **Risk Assessment** - Risk baholash
- **Allocation Charts** - Taqsimot grafiklari

### 5. Wallet Integration
1. "Wallet" sahifasiga o'ting
2. Wallet address ni kiriting
3. "Connect Wallet" tugmasini bosing
4. Balans va transaction tarixini ko'ring

### 6. Analytics
- **Performance Charts** - Performance grafiklari
- **Trading Volume** - Savdo hajmi
- **Risk Allocation** - Risk taqsimoti
- **Market Sentiment** - Bozor kayfiyati

## 🔧 Sozlash

### Environment Variables
```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT Security
JWT_SECRET_KEY=your-secret-key

# API Keys
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
NEWS_API_KEY=your-news-api-key

# External Services
OPENAI_API_KEY=your-openai-key
TELEGRAM_BOT_TOKEN=your-telegram-token
```

### Configuration
```python
# Trading Settings
MAX_ORDER_SIZE = 10000  # USD
MAX_DAILY_TRADES = 100
RISK_LIMIT_PERCENTAGE = 15

# Risk Management
MAX_POSITION_SIZE = 10000
MAX_DAILY_LOSS = 5000
MAX_LEVERAGE = 3.0
MAX_DRAWDOWN = 0.15
```

## 🛠️ Development

### Code Structure
```
frontend/web_app.py        # Streamlit main app
├── SupabaseClient         # Database integration
├── TradingEngine         # Order execution
├── RealTimeDataFeed      # Live data
├── WalletManager         # Crypto wallet
└── AnalyticsDashboard    # Charts & analysis

backend/web_app_backend.py  # FastAPI server
├── DatabaseManager       # Database operations
├── AuthenticationManager # JWT auth
├── TradingEngine         # Core trading logic
├── RiskManager          # Risk calculations
└── WebSocketManager     # Real-time updates
```

### Customization
1. **UI Theme** - `web_app.py` dagi CSS stillarini o'zgartiring
2. **Trading Rules** - `TradingEngine` class ni modify qiling
3. **Market Data** - `DatabaseManager.get_market_data()` ni o'zgartiring
4. **Risk Logic** - `RiskManager` methods ni customize qiling

### Adding New Features
```python
# Yangi sahifa qo'shish
def new_feature_page():
    st.title("🆕 Yangi Imkoniyat")
    # Your feature implementation

# Navigation ga qo'shish
if st.session_state.page == "New Feature":
    new_feature_page()
```

## 🔒 Xavfsizlik

### Authentication
- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control
- Session management

### API Security
- CORS configuration
- Rate limiting
- Input validation
- SQL injection protection

### Data Protection
- Environment variables for sensitive data
- Database connection security
- Audit logging
- Error handling without data exposure

## 📊 Monitoring

### Health Checks
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs  
tail -f logs/frontend.log
```

### Metrics
- API response times
- Database connection status
- WebSocket connections count
- Error rates

## 🧪 Testing

### Unit Tests
```bash
# Backend tests
pytest backend/tests/

# Frontend tests
pytest frontend/tests/
```

### Integration Tests
```bash
# Full pipeline test
python -m pytest tests/integration/
```

### Load Testing
```bash
# API load test
ab -n 1000 -c 10 http://localhost:8000/health
```

## 🚀 Deployment

### Docker (Tavsiya etiladi)
```bash
# Build images
docker build -t orion-frontend ./frontend
docker build -t orion-backend ./backend

# Run containers
docker-compose up -d
```

### Manual Deployment
```bash
# Backend
gunicorn backend.web_app_backend:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
streamlit run frontend/web_app.py --server.port=8501 --server.address=0.0.0.0
```

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Security scan completed

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check Supabase credentials
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY

# Test connection
python -c "from supabase import create_client; create_client('$SUPABASE_URL', '$SUPABASE_ANON_KEY')"
```

**WebSocket Connection Failed**
```bash
# Check firewall settings
sudo ufw status

# Test WebSocket manually
wscat -c ws://localhost:8000/ws/market
```

**Module Not Found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"
```

**Port Already in Use**
```bash
# Find process using port
lsof -i :8000
lsof -i :8501

# Kill process
kill -9 <PID>
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run with verbose output
streamlit run frontend/web_app.py --logger.level debug
```

## 📞 Yordam

Agar muammo yuz bersa:

1. **Log fayllarini tekshiring** - `logs/` papkasida
2. **API health ni tekshiring** - `GET /health` endpoint
3. **Database connection** - Supabase dashboard da tekshiring
4. **Environment variables** - `.env` faylni tekshiring

**Issues boshqarish:**
- GitHub Issues oching
- Error logs ni qo'shing
- Steps to reproduce ni yozing

---

## 🏆 Xususiyatlari

### ✅ Amalga oshirilgan
- ✅ User Authentication
- ✅ Real-time Dashboard  
- ✅ Trading Interface
- ✅ Portfolio Management
- ✅ Wallet Integration
- ✅ Analytics Dashboard
- ✅ Responsive Design
- ✅ Error Handling
- ✅ Production Ready
- ✅ WebSocket Real-time Data

### 🔄 Kelgusida
- 📱 Mobile App (React Native)
- 🤖 Advanced AI Trading Bots
- 📊 More Chart Types
- 🔔 Push Notifications
- 📈 Social Trading Features
- 🌐 Multi-language Support

---

**Orion Starline** - Professional Trading Platform ✨