# Uchinchi Tomon Integratsiya Tizimi

Orion Starline Trading Platform uchun uchinchi tomon integratsiyalari moduli.

## Umumiy ko'rinish

Bu modul quyidagi uchinchi tomon xizmatlar bilan integratsiyani ta'minlaydi:

### Brokerlar
- **MetaTrader 4/5** - Real-time trading uchun
- **Interactive Brokers** - Professional trading uchun
- **Alpaca Markets** - API-based trading uchun
- **TD Ameritrade** - Boshqa brokerlar uchun kengaytma

### Trading Xizmatlar
- **TradingView** - Signal va alert integratsiyasi
- **Webhooks** - Custom webhook tizimi

### Kommunikatsiya
- **Slack** - Team notifications va alerts
- **Discord** - Community va bot integratsiyasi

## O'rnatish va Sozlash

### Kerakli dependencies
```bash
pip install aiohttp websockets asyncio
```

### Asosiy import
```python
from integrations import (
    create_integration_manager,
    quick_setup_mt5,
    quick_setup_tradingview,
    quick_setup_slack,
    IntegrationConfig,
    IntegrationType
)
```

## Tez boshlash

### 1. MetaTrader 5 Setup
```python
import asyncio
from integrations import quick_setup_mt5

async def setup_mt5():
    # MetaTrader 5 integration yaratish
    mt5_integration = await quick_setup_mt5(
        name="MT5_Broker1",
        server_url="localhost",
        port=443
    )
    
    # Connection
    success = await mt5_integration.connect()
    if success:
        print("MetaTrader 5 ga ulanish muvaffaqiyatli!")
        
        # Account ma'lumotlarini olish
        account = await mt5_integration.get_account_info()
        print(f"Account balance: {account.balance}")
        
        # Order joylashtirish
        await mt5_integration.place_order(
            symbol="EURUSD",
            order_type=MTOrderType.BUY,
            volume=0.1,
            price=1.0500,
            sl=1.0450,
            tp=1.0550
        )
    
    await mt5_integration.disconnect()

asyncio.run(setup_mt5())
```

### 2. Interactive Brokers Setup
```python
async def setup_ib():
    from integrations import quick_setup_interactive_brokers
    
    ib_integration = await quick_setup_interactive_brokers(
        name="IB_TWS",
        client_id=1,
        host="localhost",
        port=7497
    )
    
    success = await ib_integration.connect()
    if success:
        # Market data olish
        market_data = await ib_integration.get_market_data(["AAPL", "MSFT"])
        print("Market data:", market_data)
        
        # Order joylashtirish
        order_id = await ib_integration.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            order_type=OrderType.MARKET
        )
        print(f"Order ID: {order_id}")

asyncio.run(setup_ib())
```

### 3. TradingView Setup
```python
async def setup_tradingview():
    from integrations import quick_setup_tradingview, create_integration_manager
    
    # TradingView webhook integration
    tv_integration = await quick_setup_tradingview(
        name="TradingView_Signals",
        webhook_url="https://hooks.tradingview.com/hooks/your-webhook"
    )
    
    # Integration manager
    manager = await create_integration_manager()
    await manager.add_integration(tv_integration, tv_integration.config)
    
    # Connection
    await manager.connect_integration("TradingView_Signals")
    
    # Signal yuborish
    await tv_integration.send_trading_signal(
        symbol="EURUSD",
        action="buy",
        price=1.0850,
        quantity=0.1
    )

asyncio.run(setup_tradingview())
```

### 4. Slack Integration
```python
async def setup_slack():
    from integrations import quick_setup_slack
    
    slack_integration = await quick_setup_slack(
        name="Trading_Alerts",
        webhook_url="https://hooks.slack.com/services/your-webhook"
    )
    
    await slack_integration.connect()
    
    # Trading alert yuborish
    await slack_integration.send_trading_alert(
        symbol="BTCUSD",
        action="SELL",
        price=45000.0,
        confidence=85
    )
    
    # Oddiy xabar
    await slack_integration.send_message(
        "🚀 New trading opportunity detected!"
    )

asyncio.run(setup_slack())
```

### 5. Discord Integration
```python
async def setup_discord():
    from integrations import quick_setup_discord
    
    discord_integration = await quick_setup_discord(
        name="Trading_Bot",
        webhook_url="https://discord.com/api/webhooks/your-webhook"
    )
    
    await discord_integration.connect()
    
    # Embed xabar yuborish
    await discord_integration.send_embed(
        title="Trading Alert",
        description="New BUY signal detected",
        color=0x00ff00,
        fields=[
            {"name": "Symbol", "value": "EURUSD", "inline": True},
            {"name": "Price", "value": "1.0850", "inline": True},
            {"name": "Confidence", "value": "85%", "inline": True}
        ]
    )

asyncio.run(setup_discord())
```

### 6. Multi-Integration Manager
```python
async def setup_multi_integration():
    from integrations import create_integration_manager
    
    # Integration manager yaratish
    manager = await create_integration_manager()
    
    # Konfiguratsiyalar
    configs = [
        # MetaTrader
        IntegrationConfig(
            integration_type=IntegrationType.METATRADER,
            name="MT5_Broker1",
            enabled=True,
            server_url="localhost",
            port=443
        ),
        
        # Interactive Brokers
        IntegrationConfig(
            integration_type=IntegrationType.INTERACTIVE_BROKERS,
            name="IB_Gateway",
            enabled=True,
            metadata={"broker_type": "interactive_brokers"}
        ),
        
        # Slack
        IntegrationConfig(
            integration_type=IntegrationType.SLACK,
            name="Slack_Alerts",
            enabled=True,
            metadata={"webhook_url": "your-slack-webhook"}
        ),
        
        # TradingView
        IntegrationConfig(
            integration_type=IntegrationType.TRADINGVIEW,
            name="TradingView_Signals",
            enabled=True,
            metadata={"webhook_url": "your-tv-webhook"}
        )
    ]
    
    # Integratsiyalarni qo'shish
    from integrations import (
        create_metatrader_integration,
        create_broker_integration,
        create_slack_integration,
        create_tradingview_integration
    )
    
    integrations = [
        create_metatrader_integration(configs[0]),
        create_broker_integration(configs[1]),
        create_slack_integration(configs[2]),
        create_tradingview_integration(configs[3])
    ]
    
    for integration in integrations:
        await manager.add_integration(integration, integration.config)
    
    # Barchasini ulash
    await manager.connect_all()
    
    # Test ma'lumot yuborish
    test_data = {
        "event": "test_signal",
        "symbol": "EURUSD",
        "action": "buy",
        "timestamp": datetime.now().isoformat()
    }
    
    # Barcha integratsiyalarga yuborish
    results = await manager.broadcast_to_all(test_data)
    print("Broadcast results:", results)
    
    # Status monitoring
    status = await manager.get_integration_status()
    print("Integration status:", status)

asyncio.run(setup_multi_integration())
```

## Webhook Tizimi

### Custom Webhook Endpoint Qo'shish
```python
from integrations.webhook_system import WebhookEndpoint, WebhookManager

async def setup_custom_webhook():
    manager = ThirdPartyIntegrationManager()
    
    # Custom endpoint
    endpoint = WebhookEndpoint(
        url="https://your-custom-webhook.com/endpoint",
        method="POST",
        headers={"Authorization": "Bearer your-token"},
        timeout=30,
        retry_attempts=3,
        rate_limit=100
    )
    
    webhook_system = WebhookSystemIntegration(config)
    webhook_system.add_webhook_endpoint("custom_api", endpoint)
    
    await webhook_system.connect()
    
    # Ma'lumot yuborish
    success = await webhook_system.send_broadcast({
        "type": "custom_event",
        "data": {"message": "Custom webhook test"}
    })

asyncio.run(setup_custom_webhook())
```

## Event Handling

### Callback funksiyalar
```python
async def on_quote_update(quote):
    print(f"Price update: {quote.symbol} @ {quote.bid}")

async def on_order_update(order):
    print(f"Order update: {order.order_id} - {order.status}")

async def on_tradingview_signal(event):
    print(f"TV Signal: {event.data['symbol']} {event.data['action']}")

async def setup_callbacks():
    # MetaTrader callbacks
    mt5_integration.add_quote_callback(on_quote_update)
    mt5_integration.add_order_callback(on_order_update)
    
    # TradingView callbacks
    tv_integration.add_signal_callback(on_tradingview_signal)
    
    # Slack callbacks
    slack_integration.add_message_callback(lambda event: print("Slack message received"))

asyncio.run(setup_callbacks())
```

## Error Handling va Monitoring

### Health Check
```python
async def monitor_integrations():
    from integrations import create_integration_manager
    
    manager = await create_integration_manager()
    
    # Ma'lum integratsiyalarni ulash
    # ... setup code ...
    
    # Har 30 soniyada health check
    while True:
        health_status = await manager.get_integration_status()
        
        for name, status in health_status.items():
            if status["status"] == "error":
                print(f"⚠️  Integration error: {name}")
                # Auto-reconnect qilish
                await manager.connect_integration(name)
        
        await asyncio.sleep(30)

asyncio.run(monitor_integrations())
```

### Retry va Failover
```python
async def robust_connection():
    integration = await quick_setup_mt5("MT5_Robust")
    
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            success = await integration.connect()
            if success:
                print("Connected successfully!")
                break
            else:
                raise ConnectionError("Connection failed")
        
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("Max retries reached. Connection failed.")
                raise

asyncio.run(robust_connection())
```

## Configuration Management

### Konfiguratsiyani saqlash
```python
async def save_load_config():
    manager = await create_integration_manager()
    
    # Integratsiyalarni qo'shish
    # ... setup code ...
    
    # Konfiguratsiyani saqlash
    await manager.save_configs("integration_configs.json")
    
    # Yangi session
    new_manager = await create_integration_manager()
    
    # Konfiguratsiyani yuklash
    await new_manager.load_configs("integration_configs.json")

asyncio.run(save_load_config())
```

### Environment Variables bilan
```python
import os
from integrations import IntegrationConfig

def create_config_from_env():
    return IntegrationConfig(
        integration_type=IntegrationType.METATRADER,
        name=os.getenv("MT5_NAME", "MT5_Default"),
        server_url=os.getenv("MT5_HOST", "localhost"),
        port=int(os.getenv("MT5_PORT", "443")),
        enabled=os.getenv("MT5_ENABLED", "true").lower() == "true"
    )
```

## Security

### API Key Management
```python
from integrations.webhook_system import WebhookSecurity

# Xavfsizlik konfiguratsiyasi
security = WebhookSecurity(
    api_key="your-api-key",
    secret_key="your-secret-key",
    signature_header="X-Custom-Signature",
    verify_tolerance=300
)

webhook_manager = WebhookManager()
webhook_manager.set_security_config(security)
```

### Signature Verification
```python
async def verify_incoming_webhook(payload: str, signature: str, timestamp: str):
    webhook_system = create_webhook_system_integration(config)
    
    is_valid = await webhook_system.verify_webhook_signature(
        payload, signature, timestamp
    )
    
    return is_valid
```

## Performance Optimization

### Connection Pooling
```python
async def setup_connection_pool():
    # Reuse connections across integrations
    session = aiohttp.ClientSession()
    
    # Use session with multiple integrations
    # ... integration setup ...
    
    await session.close()
```

### Rate Limiting
```python
# Webhook endpoint larda rate limit o'rnatish
endpoint = WebhookEndpoint(
    url="https://api.example.com/webhook",
    rate_limit=50,  # 50 requests per minute
    retry_attempts=3
)
```

## Testing

### Unit Tests
```python
import pytest
from integrations import create_integration_manager

@pytest.mark.asyncio
async def test_integration_manager():
    manager = await create_integration_manager()
    
    # Mock config
    config = IntegrationConfig(
        integration_type=IntegrationType.METATRADER,
        name="test_mt5",
        enabled=True
    )
    
    # Test adding integration
    integration = create_metatrader_integration(config)
    await manager.add_integration(integration, config)
    
    # Test connection (mock)
    # success = await manager.connect_integration("test_mt5")
    # assert success

@pytest.mark.asyncio
async def test_tradingview_integration():
    config = IntegrationConfig(
        integration_type=IntegrationType.TRADINGVIEW,
        name="test_tv",
        enabled=True,
        metadata={"webhook_url": "https://test.com/webhook"}
    )
    
    integration = create_tradingview_integration(config)
    
    # Test signal sending (mock)
    # success = await integration.send_trading_signal("EURUSD", "buy", 1.05)
    # assert success
```

### Integration Tests
```python
async def test_full_workflow():
    # Complete trading workflow test
    manager = await create_integration_manager()
    
    # Setup multiple integrations
    # ... setup code ...
    
    # Test signal flow: TradingView -> Broker -> Slack
    signal_data = {
        "symbol": "EURUSD",
        "action": "buy",
        "price": 1.0850,
        "quantity": 0.1
    }
    
    # Send to broker
    broker_result = await manager.send_to_integration("ib_broker", signal_data)
    assert broker_result
    
    # Notify Slack
    slack_result = await manager.send_to_integration("slack_alerts", {
        "text": f"Order placed: {signal_data['symbol']}"
    })
    assert slack_result
```

## Debugging

### Logging Configuration
```python
import logging

# Detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Integration specific logger
integration_logger = logging.getLogger("integrations.metatrader")
integration_logger.setLevel(logging.INFO)
```

### Error Tracking
```python
async def track_errors():
    try:
        integration = await quick_setup_mt5("debug_mt5")
        await integration.connect()
        
        # Simulate error
        await integration.place_order("INVALID_SYMBOL", MTOrderType.BUY, 0.1)
        
    except Exception as e:
        # Log error with context
        logger.error(f"Integration error: {e}", extra={
            "integration": "MT5",
            "action": "place_order",
            "symbol": "INVALID_SYMBOL"
        })
```

## Best Practices

1. **Error Handling**: Har doim try-catch bloklari ishlatish
2. **Resource Management**: Context manager ishlatish (`async with`)
3. **Rate Limiting**: API limitlarini hurmat qilish
4. **Security**: API key'larni muhit o'zgaruvchilarida saqlash
5. **Monitoring**: Health check'lar va alerting
6. **Testing**: Unit va integration testlar yozish
7. **Configuration**: Konfiguratsiyani alohida faylda saqlash
8. **Logging**: To'g'ri log level'lar ishlatish

## Troubleshooting

### Connection Issues
```python
# Connection timeout
if "timeout" in str(e):
    # Connection timeout oshirish
    config.timeout = 60

# Network errors
if "network" in str(e):
    # Retry with exponential backoff
    await asyncio.sleep(2 ** attempt)
```

### Authentication Errors
```python
# API key tekshirish
if "unauthorized" in str(e):
    print("API key yoki secret xato!")
    # Key'larni tekshirish
```

### Webhook Issues
```python
# Webhook delivery status
if response.status == 429:
    # Rate limit exceeded
    print("Rate limit aşildi, kutib turing...")
    await asyncio.sleep(60)
```

## Contributing

1. Yangi integratsiya qo'shish uchun `BrokerAdapter` yoki `ThirdPartyIntegration` dan inherit qiling
2. Test cases yozing
3. Documentation yangilang
4. Code review o'tkazish

## License

Orion Starline Team tomonidan ishlab chiqilgan.
