# 📖 Orion Starline API Documentation

Bu hujjat Orion Starline API ning barcha endpoint-lari, authentication, va ishlatish usullarini qamrab oladi.

## 📋 Mundarija

- [Authentication](#authentication)
- [Base URL](#base-url)
- [Trading Endpoints](#trading-endpoints)
- [Portfolio Management](#portfolio-management)
- [AI Assistant](#ai-assistant)
- [Market Data](#market-data)
- [User Management](#user-management)
- [Error Codes](#error-codes)
- [Rate Limiting](#rate-limiting)

## 🔐 Authentication

API ga kirish uchun JWT token ishlatamiz:

```http
Authorization: Bearer <your-jwt-token>
```

### Token olish
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

## 🏠 Base URL

**Development**: `http://localhost:8000`  
**Production**: `https://api.orionstarline.com`

## 💰 Trading Endpoints

### Get Trading Positions
```http
GET /api/v1/positions
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "pos_001",
      "symbol": "BTCUSDT",
      "side": "LONG",
      "size": 0.5,
      "entry_price": 45000.0,
      "current_price": 46500.0,
      "pnl": 750.0,
      "pnl_percentage": 3.33,
      "stop_loss": 44000.0,
      "take_profit": 47000.0,
      "created_at": "2025-01-01T10:00:00Z"
    }
  ]
}
```

### Create Position
```http
POST /api/v1/positions
Authorization: Bearer <token>
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "side": "LONG",
  "size": 0.1,
  "stop_loss": 44000.0,
  "take_profit": 47000.0,
  "leverage": 2.0
}
```

### Close Position
```http
DELETE /api/v1/positions/{position_id}
Authorization: Bearer <token>
```

### Get Trading Signals
```http
GET /api/v1/signals
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "signal_001",
      "symbol": "BTCUSDT",
      "action": "BUY",
      "confidence": 0.85,
      "entry_price": 46000.0,
      "stop_loss": 45000.0,
      "take_profit": 47500.0,
      "reason": "RSI oversold, volume spike",
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ]
}
```

### Execute Signal
```http
POST /api/v1/signals/{signal_id}/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "size": 0.2,
  "leverage": 3.0
}
```

## 📊 Portfolio Management

### Get Portfolio
```http
GET /api/v1/portfolio
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_balance": 10000.0,
    "available_balance": 8500.0,
    "margin_balance": 1500.0,
    "pnl": 250.0,
    "pnl_percentage": 2.5,
    "positions": [
      {
        "symbol": "BTCUSDT",
        "size": 0.5,
        "value": 2250.0,
        "pnl": 125.0
      }
    ],
    "allocation": {
      "BTC": 40.0,
      "ETH": 30.0,
      "USDT": 20.0,
      "OTHERS": 10.0
    }
  }
}
```

### Rebalance Portfolio
```http
POST /api/v1/portfolio/rebalance
Authorization: Bearer <token>
Content-Type: application/json

{
  "target_allocation": {
    "BTC": 35.0,
    "ETH": 35.0,
    "USDT": 20.0,
    "OTHERS": 10.0
  },
  "threshold": 2.0
}
```

### Get Performance Metrics
```http
GET /api/v1/portfolio/performance
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_return": 15.5,
    "annualized_return": 12.3,
    "sharpe_ratio": 1.8,
    "max_drawdown": -8.2,
    "volatility": 12.5,
    "win_rate": 68.5,
    "profit_factor": 1.45,
    "total_trades": 156,
    "winning_trades": 107,
    "losing_trades": 49
  }
}
```

## 🤖 AI Assistant

### Send Message
```http
POST /api/v1/ai/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "BTC narxi qanday o'zgarishga duch keladi?",
  "session_id": "session_123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "AI tahlilim asosida, BTC/USDT birjasida. Hozirda...",
    "confidence": 0.85,
    "session_id": "session_123",
    "model_used": "gpt-trading-assistant-v2"
  }
}
```

### Get Chat History
```http
GET /api/v1/ai/chat/history
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "Savol",
      "timestamp": "2025-01-01T10:00:00Z"
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "Javob",
      "timestamp": "2025-01-01T10:00:01Z",
      "confidence": 0.85
    }
  ]
}
```

## 📈 Market Data

### Get Ticker
```http
GET /api/v1/market/ticker/{symbol}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "BTCUSDT",
    "price": 46000.00,
    "change_24h": 1250.00,
    "change_percent_24h": 2.79,
    "high_24h": 47500.00,
    "low_24h": 45000.00,
    "volume_24h": 12345.67,
    "market_cap": 890000000000.00,
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

### Get Market Data
```http
GET /api/v1/market/candles/{symbol}
Authorization: Bearer <token>
Query Parameters:
- interval: 1m, 5m, 15m, 1h, 4h, 1d
- limit: 1-1000
- start_time: ISO datetime
- end_time: ISO datetime
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2025-01-01T12:00:00Z",
      "open": 45500.00,
      "high": 46000.00,
      "low": 45000.00,
      "close": 45800.00,
      "volume": 1234.56
    }
  ]
}
```

### Get Market Analysis
```http
GET /api/v1/market/analysis/{symbol}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "BTCUSDT",
    "sentiment": "bullish",
    "rsi": 65.5,
    "macd": {
      "signal": "bullish",
      "histogram": 125.0
    },
    "support_levels": [44000, 43500, 43000],
    "resistance_levels": [47000, 47500, 48000],
    "trend": "uptrend",
    "analysis_timestamp": "2025-01-01T12:00:00Z"
  }
}
```

## 👤 User Management

### Get User Profile
```http
GET /api/v1/user/profile
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "avatar": "https://example.com/avatar.jpg",
    "subscription_tier": "premium",
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2025-01-01T12:00:00Z"
  }
}
```

### Update Profile
```http
PUT /api/v1/user/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Yangi Ism",
  "avatar": "https://example.com/new-avatar.jpg"
}
```

### Change Password
```http
POST /api/v1/user/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "eski_parol",
  "new_password": "yangi_parol"
}
```

### Get API Keys
```http
GET /api/v1/user/api-keys
Authorization: Bearer <token>
```

### Create API Key
```http
POST /api/v1/user/api-keys
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Trading Bot",
  "permissions": ["read", "trade"],
  "expires_at": "2025-12-31T23:59:59Z"
}
```

## ❌ Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| 400 | Bad Request | Noto'g'ri request format |
| 401 | Unauthorized | Authentication kerak |
| 403 | Forbidden | Ruxsat yo'q |
| 404 | Not Found | Resource topilmadi |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Error | Server xatoligi |
| 503 | Service Unavailable | Service vaqtincha ishlamayapti |

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "symbol",
      "issue": "Symbol not found"
    }
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## 🕐 Rate Limiting

**Free Tier**: 100 requests/minute  
**Premium Tier**: 1000 requests/minute  
**Enterprise**: 10000 requests/minute

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1704105600
```

## 📡 WebSocket API

### Connection
```javascript
const ws = new WebSocket('wss://api.orionstarline.com/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
  }));
};
```

### Subscribe to Market Data
```javascript
// Subscribe to ticker updates
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'ticker',
  symbol: 'BTCUSDT'
}));

// Subscribe to position updates
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'positions'
}));
```

### Message Format
```json
{
  "type": "ticker",
  "data": {
    "symbol": "BTCUSDT",
    "price": 46000.00,
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

## 📚 SDK Examples

### JavaScript/TypeScript
```typescript
import { OrionStarlineClient } from '@orionstarline/sdk';

const client = new OrionStarlineClient({
  apiKey: 'your-api-key',
  environment: 'production' // 'development' or 'production'
});

// Get positions
const positions = await client.positions.list();

// Create signal
const signal = await client.signals.create({
  symbol: 'BTCUSDT',
  action: 'BUY',
  size: 0.1
});
```

### Python
```python
from orion_starline import OrionStarlineClient

client = OrionStarlineClient(
    api_key='your-api-key',
    environment='production'
)

# Get portfolio
portfolio = client.portfolio.get()

# Get market data
ticker = client.market.get_ticker('BTCUSDT')
```

### cURL Examples
```bash
# Get positions
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     https://api.orionstarline.com/api/v1/positions

# Create position
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"symbol":"BTCUSDT","side":"LONG","size":0.1}' \
     https://api.orionstarline.com/api/v1/positions
```

## 📞 Support

- **Email**: api-support@orionstarline.com
- **Discord**: [Orion Starline API](https://discord.gg/orionstarline)
- **GitHub**: [Issues](https://github.com/your-username/orion-starline/issues)

---

**API versiyasi**: v2.0  
**Oxirgi yangilash**: 2025-01-01