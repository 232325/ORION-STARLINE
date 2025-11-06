# AI Trading Evolution - SDK Usage Examples
# ==========================================
# Multi-language usage examples
# Author: MiniMax Agent
# Version: 1.0.0
# Date: 2025-11-04

## Python Examples

### 1. Basic Usage (Async)
```python
import asyncio
from ai_trading_sdk import TradingClient

async def main():
    # Create client
    async with TradingClient(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    ) as client:
        
        # Get market data
        data = await client.market.get_data("BTC/USDT")
        print(f"Market data: {data}")
        
        # Execute strategy
        signal = await client.strategy.execute("grid", "BTC/USDT")
        print(f"Signal: {signal.signal}, Confidence: {signal.confidence}")
        
        # Run analytics
        sentiment = await client.analytics.sentiment("BTC/USDT")
        print(f"Sentiment: {sentiment.result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Synchronous Usage
```python
from ai_trading_sdk import SyncTradingClient

# Create client
with SyncTradingClient(base_url="http://localhost:8000") as client:
    
    # Get market data
    data = client.market.get_data("BTC/USDT", market_type="crypto", timeframe="1h")
    print(data)
    
    # Execute strategy with parameters
    signal = client.strategy.execute(
        "grid",
        "BTC/USDT",
        timeframe="1h",
        parameters={"grid_levels": 10, "price_range": 0.05}
    )
    print(f"Entry Price: {signal['entry_price']}")
```

### 3. WebSocket Real-time Streaming
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
    
    # Subscribe to trading signals
    await ws.subscribe("signals:grid")
    
    # Receive messages
    while True:
        message = await ws.receive()
        print(f"Received: {message}")
        
        if message['type'] == 'market_data':
            print(f"Price: {message['data']['price']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Batch Operations
```python
import asyncio
from ai_trading_sdk import TradingClient

async def main():
    async with TradingClient() as client:
        
        # Multiple symbols concurrently
        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
        
        tasks = [
            client.market.get_data(symbol)
            for symbol in symbols
        ]
        
        results = await asyncio.gather(*tasks)
        
        for symbol, data in zip(symbols, results):
            print(f"{symbol}: {data}")

asyncio.run(main())
```

---

## JavaScript/TypeScript Examples

### 1. Basic Usage
```javascript
import { TradingClient } from 'ai-trading-sdk';

const client = new TradingClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Get market data
const data = await client.market.getData('BTC/USDT', {
  market_type: 'crypto',
  timeframe: '1h'
});
console.log('Market data:', data);

// Execute strategy
const signal = await client.strategy.execute('grid', 'BTC/USDT', {
  timeframe: '1h',
  parameters: { grid_levels: 10 }
});
console.log('Signal:', signal.signal);

// Run analytics
const sentiment = await client.analytics.sentiment('BTC/USDT');
console.log('Sentiment:', sentiment.result);
```

### 2. TypeScript with Types
```typescript
import { TradingClient, StrategyResponse } from 'ai-trading-sdk';

const client = new TradingClient({
  baseUrl: 'http://localhost:8000',
  apiKey: process.env.API_KEY
});

// Typed response
const signal: StrategyResponse = await client.strategy.execute('grid', 'BTC/USDT');

if (signal.signal === 'BUY') {
  console.log(`Buy at ${signal.entry_price}`);
  console.log(`Stop loss: ${signal.stop_loss}`);
  console.log(`Take profit: ${signal.take_profit}`);
}
```

### 3. WebSocket Real-time
```javascript
const client = new TradingClient();
const ws = client.websocket();

// Connect
await ws.connect();

// Subscribe with handler
await ws.subscribe('market:BTC/USDT', (message) => {
  console.log('Market update:', message.data);
});

// Subscribe to multiple channels
await ws.subscribe('signals:grid');
await ws.subscribe('portfolio:user123');

// Register global handler
ws.on('trading_signal', (message) => {
  console.log('New signal:', message.data);
});
```

### 4. Error Handling
```javascript
import { TradingClient, APIError } from 'ai-trading-sdk';

const client = new TradingClient();

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

## Java Examples

### 1. Basic Usage
```java
import com.trading.ai.sdk.TradingClient;
import com.trading.ai.sdk.StrategyResponse;

public class Example {
    public static void main(String[] args) {
        TradingClient client = new TradingClient(
            "http://localhost:8000",
            "your-api-key"
        );
        
        try {
            // Get market data
            var data = client.market.getData("BTC/USDT", "crypto", "1h", 100);
            System.out.println("Market data: " + data);
            
            // Execute strategy
            Map<String, Object> params = new HashMap<>();
            params.put("grid_levels", 10);
            
            StrategyResponse signal = client.strategy.execute(
                "grid",
                "BTC/USDT",
                "1h",
                params
            );
            
            System.out.println("Signal: " + signal.signal);
            System.out.println("Confidence: " + signal.confidence);
            
            // Run analytics
            var sentiment = client.analytics.sentiment("BTC/USDT");
            System.out.println("Sentiment: " + sentiment);
            
        } catch (APIException e) {
            System.err.println("API Error: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}
```

### 2. Spring Boot Integration
```java
import org.springframework.stereotype.Service;
import com.trading.ai.sdk.TradingClient;

@Service
public class TradingService {
    private final TradingClient client;
    
    public TradingService() {
        this.client = new TradingClient("http://localhost:8000");
    }
    
    public String executeStrategy(String strategy, String symbol) {
        try {
            var signal = client.strategy.execute(strategy, symbol);
            return signal.signal;
        } catch (Exception e) {
            throw new RuntimeException("Strategy execution failed", e);
        }
    }
}
```

---

## Go Examples

### 1. Basic Usage
```go
package main

import (
    "fmt"
    "log"
    "trading"
)

func main() {
    // Create client
    client := trading.NewClient("http://localhost:8000", "your-api-key")
    
    // Get market data
    data, err := client.Market.GetData("BTC/USDT", nil)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Market data:", data)
    
    // Execute strategy
    signal, err := client.Strategy.Execute("grid", "BTC/USDT", &trading.StrategyRequest{
        Timeframe: "1h",
        Parameters: map[string]interface{}{
            "grid_levels": 10,
        },
    })
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Signal: %s, Confidence: %.2f\n", signal.Signal, signal.Confidence)
    
    // Run analytics
    sentiment, err := client.Analytics.Sentiment("BTC/USDT")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Sentiment:", sentiment.Result)
}
```

### 2. Goroutine Concurrency
```go
package main

import (
    "fmt"
    "sync"
    "trading"
)

func main() {
    client := trading.NewClient("http://localhost:8000", "")
    
    symbols := []string{"BTC/USDT", "ETH/USDT", "BNB/USDT"}
    var wg sync.WaitGroup
    
    for _, symbol := range symbols {
        wg.Add(1)
        go func(sym string) {
            defer wg.Done()
            
            data, err := client.Market.GetData(sym, nil)
            if err != nil {
                fmt.Println("Error:", err)
                return
            }
            fmt.Printf("%s: %v\n", sym, data)
        }(symbol)
    }
    
    wg.Wait()
}
```

---

## C# Examples

### 1. Basic Usage
```csharp
using AITrading.SDK;

var client = new TradingClient("http://localhost:8000", "your-api-key");

// Get market data
var data = await client.Market.GetDataAsync("BTC/USDT");
Console.WriteLine($"Market data: {data}");

// Execute strategy
var signal = await client.Strategy.ExecuteAsync("grid", "BTC/USDT");
Console.WriteLine($"Signal: {signal.Signal}, Confidence: {signal.Confidence}");

// Run analytics
var sentiment = await client.Analytics.SentimentAsync("BTC/USDT");
Console.WriteLine($"Sentiment: {sentiment.Result}");
```

### 2. ASP.NET Core Integration
```csharp
using Microsoft.AspNetCore.Mvc;
using AITrading.SDK;

[ApiController]
[Route("api/[controller]")]
public class TradingController : ControllerBase
{
    private readonly TradingClient _client;
    
    public TradingController()
    {
        _client = new TradingClient("http://localhost:8000");
    }
    
    [HttpGet("signal/{symbol}")]
    public async Task<IActionResult> GetSignal(string symbol)
    {
        try
        {
            var signal = await _client.Strategy.ExecuteAsync("grid", symbol);
            return Ok(signal);
        }
        catch (APIException ex)
        {
            return StatusCode(ex.StatusCode, ex.Message);
        }
    }
}
```

---

## PHP Examples

### 1. Basic Usage
```php
<?php
require_once 'vendor/autoload.php';

use AITrading\SDK\TradingClient;

$client = new TradingClient('http://localhost:8000', 'your-api-key');

// Get market data
$data = $client->market->getData('BTC/USDT', [
    'market_type' => 'crypto',
    'timeframe' => '1h'
]);
print_r($data);

// Execute strategy
$signal = $client->strategy->execute('grid', 'BTC/USDT', [
    'timeframe' => '1h',
    'parameters' => ['grid_levels' => 10]
]);
echo "Signal: {$signal['signal']}\n";

// Run analytics
$sentiment = $client->analytics->sentiment('BTC/USDT');
print_r($sentiment);
```

### 2. Laravel Integration
```php
<?php
namespace App\Services;

use AITrading\SDK\TradingClient;

class TradingService
{
    private $client;
    
    public function __construct()
    {
        $this->client = new TradingClient(
            config('trading.api_url'),
            config('trading.api_key')
        );
    }
    
    public function getSignal($symbol)
    {
        try {
            return $this->client->strategy->execute('grid', $symbol);
        } catch (\Exception $e) {
            \Log::error("Trading error: " . $e->getMessage());
            throw $e;
        }
    }
}
```

---

## Common Patterns

### Rate Limiting
```python
# Python
import asyncio
from ai_trading_sdk import TradingClient

async def rate_limited_requests():
    client = TradingClient()
    symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
    
    for symbol in symbols:
        data = await client.market.get_data(symbol)
        print(data)
        await asyncio.sleep(0.1)  # Rate limiting
```

### Retry Logic
```javascript
// JavaScript
async function executeWithRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}

const signal = await executeWithRetry(() => 
  client.strategy.execute('grid', 'BTC/USDT')
);
```

### Logging
```java
// Java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

Logger logger = LoggerFactory.getLogger(TradingExample.class);

try {
    var signal = client.strategy.execute("grid", "BTC/USDT");
    logger.info("Signal received: {}", signal.signal);
} catch (APIException e) {
    logger.error("API error: {}", e.getMessage());
}
```

---

## Testing Examples

### Python Unit Test
```python
import pytest
from ai_trading_sdk import TradingClient

@pytest.mark.asyncio
async def test_market_data():
    async with TradingClient() as client:
        data = await client.market.get_data("BTC/USDT")
        assert data['symbol'] == "BTC/USDT"
        assert 'data' in data
```

### JavaScript Jest Test
```javascript
import { TradingClient } from 'ai-trading-sdk';

describe('TradingClient', () => {
  it('should fetch market data', async () => {
    const client = new TradingClient();
    const data = await client.market.getData('BTC/USDT');
    expect(data.symbol).toBe('BTC/USDT');
  });
});
```

---

**More examples:** See `/examples` directory in each SDK folder.
