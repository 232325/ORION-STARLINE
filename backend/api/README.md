# AI Trading System - RESTful API

Quantum AI, HFT, DAO, NFT va Blockchain texnologiyalari bilan jihoblangan trading tizimi uchun to'liq RESTful API.

## 🎯 Asosiy Xususiyatlar

### 📡 Core API Endpoints
- **AI Signals** (`/api/v1/ai-signals`) - AI trading signals boshqaruvi
- **Quantum Analysis** (`/api/v1/quantum-analysis`) - Quantum analysis va simulation
- **Blockchain** (`/api/v1/blockchain`) - Blockchain operatsiyalari
- **DAO Governance** (`/api/v1/dao-governance`) - DAO boshqaruvi
- **HFT Engine** (`/api/v1/hft-engine`) - High-Frequency Trading
- **NFT Hedge Fund** (`/api/v1/nft-hedge`) - NFT hedge fund operatsiyalari  
- **Self-Learning** (`/api/v1/self-learning`) - Self-learning sistemlari

### ⚡ API Xususiyatlari
- ✅ **FastAPI Framework** - Ultra-fast async API
- ✅ **Async Endpoints** - High-performance concurrent requests
- ✅ **OpenAPI Documentation** - Auto-generated interactive docs
- ✅ **Pydantic Models** - Strong data validation
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **OAuth 2.0** - Google, GitHub, LinkedIn integration
- ✅ **WebSocket Real-time** - Live data streaming
- ✅ **File Operations** - Upload/download with validation
- ✅ **Bulk Operations** - Process multiple items efficiently
- ✅ **Smart Pagination** - Advanced filtering and sorting
- ✅ **Response Caching** - Redis + in-memory caching
- ✅ **Error Handling** - Comprehensive error management
- ✅ **Rate Limiting** - Request throttling and protection

### 🔐 Authentication & Security
- **JWT Token Authentication** - Stateless authentication
- **API Key Authentication** - Programmatic access
- **OAuth 2.0 Integration** - Google, GitHub, LinkedIn
- **Role-based Access Control** - Admin, Trader, Analyst, Viewer
- **Session Management** - Secure session handling

### 📊 Advanced Data Models
- **Request/Response Models** - Pydantic-based validation
- **Complex Validation** - Custom validators and constraints
- **Serialization/Deserialization** - Automatic data conversion
- **Type Safety** - Full type hints coverage
- **Schema Evolution** - Backward compatible model updates

## 🚀 Tez boshlash

### 1. Dependencies o'rnatish
```bash
cd /workspace/code/api
pip install -r requirements.txt
```

### 2. Environment sozlamalar
```bash
# .env.example ni .env ga ko'chiring va sozlang
cp .env.example .env
# .env faylini tahrirlang
```

### 3. Server'ni ishga tushirish
```bash
python run.py
# yoki
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Demo bilan test qilish
```bash
# Yangi terminal ochib
python demo.py
```

## 📚 API Documentation

Server ishga tushgandan so'ng:

| Resource | URL | Description |
|----------|-----|-------------|
| **Swagger UI** | http://localhost:8000/api/docs | Interactive API documentation |
| **ReDoc** | http://localhost:8000/api/redoc | Clean API reference |
| **OpenAPI JSON** | http://localhost:8000/api/openapi.json | OpenAPI specification |
| **Health Check** | http://localhost:8000/health | System health status |

## 🧪 Testing

### Barcha testlarni ishga tushirish
```bash
# Barcha testlarni bajarish
python tests/run_tests.py

# Ma'lum test nomi bo'yicha
python tests/run_tests.py --test ai_signals

# Batafsil chiqish bilan
python tests/run_tests.py --verbose

# Hisobot saqlash
python tests/run_tests.py --save test_report.json
```

### Test turlari
- **Unit Tests** - Individual component testing
- **Integration Tests** - API endpoint testing
- **Authentication Tests** - Security testing
- **Performance Tests** - Load and stress testing
- **WebSocket Tests** - Real-time connection testing

## 📱 API Usage Examples

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Token bilan ma'lumot olish
curl -X GET http://localhost:8000/api/v1/ai-signals \
  -H "Authorization: Bearer <your-token>"
```

### 3. AI Signals Management
```bash
# Signals ro'yxati
curl -X GET "http://localhost:8000/api/v1/ai-signals?symbol=BTC/USDT&page=1&size=10" \
  -H "Authorization: Bearer <token>"

# Yangi signal yaratish
curl -X POST http://localhost:8000/api/v1/ai-signals \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC/USDT",
    "signal_type": "buy",
    "confidence": 0.85,
    "price": 45000.00,
    "timeframe": "1h"
  }'
```

### 4. Bulk Operations
```bash
# Ko'plab signals yaratish
curl -X POST http://localhost:8000/api/v1/ai-signals/bulk \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC/USDT", "ETH/USDT"],
    "timeframes": ["1h", "4h"],
    "include_predictions": true
  }'
```

### 5. File Operations
```bash
# Fayl yuklash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@data.csv"

# Fayllar ro'yxati
curl -X GET http://localhost:8000/api/v1/files/list \
  -H "Authorization: Bearer <token>"
```

### 6. WebSocket Connection
```javascript
// JavaScript WebSocket ulanish
const ws = new WebSocket('ws://localhost:8000/api/v1/websocket/trading');

ws.onopen = function() {
    console.log('WebSocket connected');
    ws.send(JSON.stringify({action: 'subscribe', channel: 'trading'}));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

## 👥 Test Foydalanuvchilari

Tizimda test uchun quyidagi foydalanuvchilar mavjud:

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | Admin | Full access |
| `trader` | `trader123` | Trader | Read, Write |
| `analyst` | `analyst123` | Analyst | Read, Write |
| `viewer` | `viewer123` | Viewer | Read only |

## ⚙️ Environment Variables

`.env` faylida quyidagi o'zgaruvchilarni sozlang:

### Asosiy Sozlamalar
```bash
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production
DATABASE_URL=sqlite:///./ai_trading.db
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

### OAuth Configuration
```bash
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
```

### External APIs
```bash
OPENAI_API_KEY=your-openai-api-key
BINANCE_API_KEY=your-binance-key
BINANCE_API_SECRET=your-binance-secret
COINBASE_API_KEY=your-coinbase-key
COINBASE_API_SECRET=your-coinbase-secret
```

## 🏗️ Project Structure

```
api/
├── main.py                     # Main FastAPI application
├── run.py                      # Server runner script
├── demo.py                     # API demo script
├── requirements.txt            # Dependencies list
├── .env.example               # Environment template
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration management
├── models/
│   ├── __init__.py
│   └── schemas.py             # Pydantic data models
├── auth/
│   ├── __init__.py
│   ├── auth_handler.py        # JWT authentication
│   └── oauth_handler.py       # OAuth 2.0 handlers
├── endpoints/
│   ├── __init__.py
│   ├── ai_signals.py          # AI signals endpoints
│   ├── quantum_analysis.py    # Quantum analysis endpoints
│   ├── blockchain.py          # Blockchain endpoints
│   ├── dao_governance.py      # DAO governance endpoints
│   ├── hft_engine.py          # HFT engine endpoints
│   ├── nft_hedge.py           # NFT hedge endpoints
│   └── self_learning.py       # Self-learning endpoints
├── websocket/
│   ├── __init__.py
│   └── manager.py             # WebSocket connection manager
├── utils/
│   ├── __init__.py
│   ├── cache.py               # Redis + memory caching
│   ├── pagination.py          # Advanced pagination utilities
│   ├── error_handler.py       # Global error handling
│   └── file_operations.py     # File upload/processing
├── middleware/
│   ├── __init__.py
│   └── [middleware files]     # Custom middleware
├── tests/
│   ├── __init__.py
│   ├── test_components.py     # Unit tests
│   ├── test_api_integration.py # Integration tests
│   └── run_tests.py           # Test runner script
└── uploads/                   # File upload directory
```

## 📈 Performance & Monitoring

### Performance Features
- ⚡ **Ultra-low latency HFT operations** - Microsecond-level responses
- 🔄 **Real-time WebSocket connections** - Live data streaming
- 💾 **Intelligent caching** - Multi-layer caching strategy
- 📈 **Scalable architecture** - Horizontal scaling support
- 🛡️ **Comprehensive error handling** - Graceful failure recovery

### Monitoring Endpoints
- **Health Checks**: `/health` - System health status
- **System Status**: `/api/v1/system/status` - Detailed system metrics
- **Performance Metrics** - Available in all API responses
- **Error Tracking** - Unique error IDs for debugging

### Caching Strategy
- **Redis Cache** - Distributed caching for production
- **In-Memory Cache** - Fast local caching
- **Smart Invalidation** - Pattern-based cache clearing
- **Cache Warmup** - Preload frequently accessed data

## 🔒 Security Features

### Authentication & Authorization
- **JWT Token Authentication** - Stateless secure authentication
- **Role-based Access Control** - Granular permission system
- **OAuth 2.0 Integration** - Third-party authentication
- **API Key Authentication** - Programmatic access tokens

### Security Measures
- **Input Validation** - Pydantic-based request validation
- **Rate Limiting** - Request throttling protection
- **CORS Protection** - Cross-origin request security
- **SQL Injection Prevention** - ORM-based database queries
- **XSS Protection** - Output encoding and sanitization
- **Request/Response Logging** - Security audit trail

## 🛠️ Development Tools

### Code Quality
- **Black** - Code formatting
- **Flake8** - Linting and style checking
- **MyPy** - Static type checking
- **Isort** - Import sorting

### Testing Framework
- **Pytest** - Comprehensive testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage reporting
- **pytest-mock** - Mocking utilities

### Documentation
- **OpenAPI/Swagger** - Interactive API docs
- **ReDoc** - Clean API reference
- **Type Hints** - Inline documentation
- **Docstrings** - Detailed function documentation

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Run** tests (`python tests/run_tests.py`)
6. **Commit** your changes (`git commit -m 'Add amazing feature'`)
7. **Push** to the branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive docstrings
- Include tests for new features
- Maintain >90% test coverage

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Support & Contact

- **API Documentation**: http://localhost:8000/api/docs
- **Issues**: GitHub Issues
- **Email**: api@aitrading.com
- **Discord**: [Join our community](https://discord.gg/aitrading)

## 🎉 Features Showcase

### Real-time Trading Data
- Live price feeds via WebSocket
- Instant signal updates
- Market data streaming

### Quantum Computing Integration
- Quantum state simulation
- Superposition analysis
- Quantum advantage calculations

### Blockchain Operations
- Multi-chain support
- Smart contract interaction
- DeFi protocol integration

### Advanced Analytics
- AI-powered market analysis
- Risk assessment models
- Performance metrics

### Professional Trading Tools
- HFT-optimized APIs
- Low-latency execution
- Advanced order management