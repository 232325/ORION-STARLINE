# 🚀 AI Trading Evolution - SDK Documentation

> **Multi-Language Client Libraries** - Python, JavaScript/TypeScript, Java, Go, C#, PHP

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/ai-trading-evolution)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-14+-green.svg)](https://nodejs.org/)
[![Java](https://img.shields.io/badge/java-11+-red.svg)](https://www.oracle.com/java/)
[![Go](https://img.shields.io/badge/go-1.16+-cyan.svg)](https://golang.org/)

---

## 📋 Mundarija

1. [Kirish](#kirish)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [API Reference](#api-reference)
5. [WebSocket](#websocket)
6. [Examples](#examples)
7. [Testing](#testing)

---

## Kirish

AI Trading Evolution SDK - bu barcha dasturlash tillarida ishlaydigan official client library. Quyidagi tillarda SDK mavjud:

| Til | SDK Fayl | Status |
|-----|----------|--------|
| **Python** | `python/ai_trading_sdk.py` | ✅ Ready |
| **JavaScript/TypeScript** | `javascript/ai-trading-sdk.ts` | ✅ Ready |
| **Java** | `java/TradingClient.java` | ✅ Ready |
| **Go** | `go/trading_client.go` | ✅ Ready |
| **C#** | `csharp/TradingClient.cs` | ✅ Ready |
| **PHP** | `php/TradingClient.php` | ✅ Ready |

---

## Installation

### Python

```bash
# Pip orqali
pip install ai-trading-sdk

# O'rnatilgan SDK'dan
cp python/ai_trading_sdk.py your_project/
pip install aiohttp websockets
```

### JavaScript/TypeScript

```bash
# NPM orqali
npm install ai-trading-sdk

# Yarn orqali
yarn add ai-trading-sdk

# O'rnatilgan SDK'dan
cp javascript/ai-trading-sdk.ts your_project/
```

### Java

```xml
<!-- Maven -->
<dependency>
    <groupId>com.trading.ai</groupId>
    <artifactId>trading-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

```java
// O'rnatilgan SDK'dan
// Copy java/TradingClient.java to your project
// Add dependencies: jackson-databind, java.net.http
```

### Go

```bash
# Go modules
go get github.com/your-org/trading-sdk

# O'rnatilgan SDK'dan
cp go/trading_client.go your_project/
```

### C#

```bash
# NuGet
dotnet add package AITrading.SDK

# O'rnatilgan SDK'dan
# Copy csharp/TradingClient.cs to your project
```

### PHP

```bash
# Composer
composer require ai-trading/sdk

# O'rnatilgan SDK'dan
# Copy php/TradingClient.php to your project
```

---

## Quick Start

### Python

```python
import asyncio
from ai_trading_sdk import TradingClient

async def main():
    async with TradingClient(base_url="http://localhost:8000") as client:
        # Market data
        data = await client.market.get_data("BTC/USDT")
        print(data)
        
        # Execute strategy
        signal = await client.strategy.execute("grid", "BTC/USDT")
        print(f"Signal: {signal.signal}")

asyncio.run(main())
```

### JavaScript/TypeScript

```javascript
import { TradingClient } from 'ai-trading-sdk';

const client = new TradingClient({
  baseUrl: 'http://localhost:8000'
});

// Market data
const data = await client.market.getData('BTC/USDT');
console.log(data);

// Execute strategy
const signal = await client.strategy.execute('grid', 'BTC/USDT');
console.log(signal.signal);
```

### Java

```java
import com.trading.ai.sdk.TradingClient;

TradingClient client = new TradingClient("http://localhost:8000");

// Market data
var data = client.market.getData("BTC/USDT");
System.out.println(data);

// Execute strategy
var signal = client.strategy.execute("grid", "BTC/USDT");
System.out.println(signal.signal);
```

### Go

```go
import "trading"

client := trading.NewClient("http://localhost:8000", "")

// Market data
data, _ := client.Market.GetData("BTC/USDT", nil)
fmt.Println(data)

// Execute strategy
signal, _ := client.Strategy.Execute("grid", "BTC/USDT", nil)
fmt.Println(signal.Signal)
```

### C#

```csharp
using AITrading.SDK;

var client = new TradingClient("http://localhost:8000");

// Market data
var data = await client.Market.GetDataAsync("BTC/USDT");
Console.WriteLine(data);

// Execute strategy
var signal = await client.Strategy.ExecuteAsync("grid", "BTC/USDT");
Console.WriteLine(signal.Signal);
```

### PHP

```php
<?php
use AITrading\SDK\TradingClient;

$client = new TradingClient('http://localhost:8000');

// Market data
$data = $client->market->getData('BTC/USDT');
print_r($data);

// Execute strategy
$signal = $client->strategy->execute('grid', 'BTC/USDT');
echo "Signal: {$signal['signal']}\n";
```

---

## API Reference

### Client Initialization

**Python:**
```python
client = TradingClient(
    base_url="http://localhost:8000",
    api_key="your-api-key",
    timeout=30
)
```

**JavaScript:**
```javascript
const client = new TradingClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key',
  timeout: 30000
});
```

**Java:**
```java
TradingClient client = new TradingClient(
    "http://localhost:8000",
    "your-api-key"
);
```

**Go:**
```go
client := trading.NewClient(
    "http://localhost:8000",
    "your-api-key"
)
```

**C#:**
```csharp
var client = new TradingClient(
    "http://localhost:8000",
    "your-api-key"
);
```

**PHP:**
```php
$client = new TradingClient(
    'http://localhost:8000',
    'your-api-key'
);
```

---

### Market API

#### `get_data(symbol, options)`

Get market data for a symbol.

**Parameters:**
- `symbol` (string): Trading pair (e.g., "BTC/USDT")
- `market_type` (string, optional): "crypto", "forex", "stocks", "commodities" (default: "crypto")
- `timeframe` (string, optional): "1m", "5m", "15m", "1h", "4h", "1d" (default: "1h")
- `limit` (int, optional): Number of candles (default: 100)

**Returns:** Market data object

**Example:**

```python
# Python
data = await client.market.get_data("BTC/USDT", market_type="crypto", timeframe="1h", limit=100)
```

```javascript
// JavaScript
const data = await client.market.getData('BTC/USDT', {
  market_type: 'crypto',
  timeframe: '1h',
  limit: 100
});
```

#### `list_symbols(market_type)`

Get list of available symbols.

**Parameters:**
- `market_type` (string): "crypto", "forex", "stocks", "commodities"

**Returns:** Symbols list

---

### Strategy API

#### `execute(strategy_name, symbol, options)`

Execute trading strategy.

**Parameters:**
- `strategy_name` (string): Strategy name ("arbitrage", "grid", "dca", "futures", "mean_reversion", "momentum")
- `symbol` (string): Trading pair
- `timeframe` (string, optional): Timeframe (default: "1h")
- `parameters` (object, optional): Strategy parameters

**Returns:** Strategy response with signal

**Example:**

```python
# Python
signal = await client.strategy.execute(
    "grid",
    "BTC/USDT",
    timeframe="1h",
    parameters={"grid_levels": 10, "price_range": 0.05}
)
```

```javascript
// JavaScript
const signal = await client.strategy.execute('grid', 'BTC/USDT', {
  timeframe: '1h',
  parameters: { grid_levels: 10, price_range: 0.05 }
});
```

**Response:**
```json
{
  "strategy_name": "grid",
  "symbol": "BTC/USDT",
  "signal": "BUY",
  "confidence": 0.85,
  "price": 45000.0,
  "entry_price": 44950.0,
  "stop_loss": 44000.0,
  "take_profit": 46000.0,
  "timestamp": "2025-11-04T01:19:32Z",
  "metadata": {}
}
```

#### `list()`

Get list of available strategies.

---

### Analytics API

#### `analyze(analysis_type, symbol, parameters)`

Run analytics.

**Parameters:**
- `analysis_type` (string): "sentiment", "whale_tracking", "risk_scoring", "portfolio"
- `symbol` (string, optional): Trading pair
- `parameters` (object, optional): Analysis parameters

**Returns:** Analysis results

**Example:**

```python
# Python
sentiment = await client.analytics.sentiment("BTC/USDT")
```

```javascript
// JavaScript
const sentiment = await client.analytics.sentiment('BTC/USDT');
```

#### Convenience Methods

- `sentiment(symbol)` - Get sentiment analysis
- `risk_scoring(symbol)` - Get risk assessment
- `list_types()` - Get analytics types

---

## WebSocket

Real-time data streaming via WebSocket.

### Python Example

```python
import asyncio
from ai_trading_sdk import TradingClient

async def main():
    client = TradingClient()
    ws = client.websocket()
    
    # Connect
    await ws.connect()
    
    # Subscribe to market data
    await ws.subscribe("market:BTC/USDT")
    
    # Receive messages
    while True:
        message = await ws.receive()
        print(message)

asyncio.run(main())
```

### JavaScript Example

```javascript
const client = new TradingClient();
const ws = client.websocket();

// Connect
await ws.connect();

// Subscribe with handler
await ws.subscribe('market:BTC/USDT', (message) => {
  console.log('Market update:', message);
});

// Subscribe to multiple channels
await ws.subscribe('signals:grid');
await ws.subscribe('portfolio:user123');
```

### Supported Channels

| Channel | Tavsif | Format |
|---------|---------|--------|
| `market:{symbol}` | Real-time market data | `market:BTC/USDT` |
| `signals:{strategy}` | Trading signals | `signals:grid` |
| `portfolio:{user_id}` | Portfolio updates | `portfolio:user123` |

### Actions

| Action | Tavsif |
|--------|---------|
| `subscribe` | Channel'ga obuna |
| `unsubscribe` | Obunani bekor qilish |
| `ping` | Connection test |
| `get_stats` | Connection stats |

---

## Examples

To'liq misollar: [USAGE_EXAMPLES.md](examples/USAGE_EXAMPLES.md)

### Common Use Cases

#### 1. Multiple Symbols Monitoring

```python
# Python
import asyncio

symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
tasks = [client.market.get_data(symbol) for symbol in symbols]
results = await asyncio.gather(*tasks)
```

```javascript
// JavaScript
const symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'];
const promises = symbols.map(symbol => client.market.getData(symbol));
const results = await Promise.all(promises);
```

#### 2. Strategy with Parameters

```python
# Python - Grid Trading
signal = await client.strategy.execute(
    "grid",
    "BTC/USDT",
    parameters={
        "grid_levels": 10,
        "price_range": 0.05,
        "upper_price": 50000,
        "lower_price": 40000
    }
)
```

#### 3. Sentiment + Risk Analysis

```python
# Python
sentiment = await client.analytics.sentiment("BTC/USDT")
risk = await client.analytics.risk_scoring("BTC/USDT")

if sentiment.result['sentiment'] == 'bullish' and risk.result['risk_level'] == 'low':
    print("Good time to buy!")
```

---

## Testing

### Postman Collection

Import Postman collection: `AI_Trading_Evolution.postman_collection.json`

**Setup:**
1. Import collection to Postman
2. Set `BASE_URL` variable: `http://localhost:8000`
3. Set `API_KEY` variable (if needed)
4. Run collection tests

### Unit Tests

**Python:**
```bash
pytest tests/
```

**JavaScript:**
```bash
npm test
```

**Java:**
```bash
mvn test
```

**Go:**
```bash
go test ./...
```

**C#:**
```bash
dotnet test
```

**PHP:**
```bash
./vendor/bin/phpunit
```

---

## Error Handling

### Python

```python
from ai_trading_sdk import APIError

try:
    data = await client.market.get_data("INVALID/PAIR")
except APIError as e:
    print(f"API Error {e.status_code}: {e}")
except Exception as e:
    print(f"Unknown error: {e}")
```

### JavaScript

```javascript
import { APIError } from 'ai-trading-sdk';

try {
  const data = await client.market.getData('INVALID/PAIR');
} catch (error) {
  if (error instanceof APIError) {
    console.error(`API Error ${error.statusCode}: ${error.message}`);
  } else {
    console.error('Unknown error:', error);
  }
}
```

---

## Advanced Features

### Rate Limiting

```python
# Python
import asyncio

async def rate_limited_requests():
    symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
    
    for symbol in symbols:
        data = await client.market.get_data(symbol)
        print(data)
        await asyncio.sleep(0.1)  # Rate limit: 10 req/sec
```

### Connection Pooling

```python
# Python - Reuse client connection
async with TradingClient() as client:
    # All requests use same connection pool
    data1 = await client.market.get_data("BTC/USDT")
    data2 = await client.market.get_data("ETH/USDT")
```

### Retry Logic

```javascript
// JavaScript
async function retry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    }
  }
}

const data = await retry(() => client.market.getData('BTC/USDT'));
```

---

## Support

- 📚 **Full Documentation**: [PRODUCTION_README.md](../PRODUCTION_README.md)
- 📧 **Email**: support@yourdomain.com
- 💬 **Telegram**: @yourtelegram
- 🐛 **Issues**: https://github.com/yourusername/ai-trading-evolution/issues

---

## License

Proprietary - Barcha huquqlar himoyalangan.

---

**Built with ❤️ by MiniMax Agent**  
**Version**: 1.0.0  
**Last Updated**: 2025-11-04
