# Advanced GPT Assistant - AI Model Integration Tizimi

## Kirish

**Advanced GPT Assistant** - bu OpenAI GPT-4 va Google Gemini API integratsiyasi bilan yaratilgan ilg'or AI model integration tizimi. Bu tizim trading, ma'lumotlar tahlili, va umumiy suhbat uchun optimizatsiya qilingan aqlli model tanlash va fallback mexanizmlarini ta'minlaydi.

### Asosiy imkoniyatlar

🤖 **Ko'plab Model Qarshilovi**
- OpenAI GPT-4, GPT-4 Turbo, GPT-4o, GPT-4o-mini
- Google Gemini Pro, Gemini Pro Vision, Gemini Flash
- Har bir model uchun maxsus konfiguratsiya

🎯 **Aqlli Model Tanlash**
- Vazifa turiga qarab avtomatik model tanlash
- Xarajatlar bo'yicha optimizatsiya
- Sifat va tezlik balanslash
- Trading uchun maxsus algoritmlar

⚡ **Performance Optimizatsiya**
- Response caching (qayta so'rovlarni tezlashtirish)
- Rate limiting va throttling
- Smart retry logic
- Fallback mechanisms

💰 **Xarajat Optimizatsiya**
- Model narxlarini hisobga olib tanlash
- Cost per request tracking
- Budget limit qo'llab-quvvatlash
- A/B testing support

🔄 **Kengaytirilgan Funksiyalar**
- Multi-turn conversation support
- Streaming responses
- Function calling (OpenAI)
- Real-time API status monitoring
- Context window management

## O'rnatish va Sozlash

### 1. Dependencies o'rnatish

```bash
cd /workspace/orion-starline/backend/ai_modules/
pip install -r requirements.txt
```

### 2. API Keys sozlash

```bash
# Environment variables
export OPENAI_API_KEY="your-openai-api-key"
export GEMINI_API_KEY="your-google-api-key"

# .env fayl yaratish
echo "OPENAI_API_KEY=your-openai-api-key" > .env
echo "GEMINI_API_KEY=your-google-api-key" >> .env
```

### 3. Oddiy ishlatish

```python
from advanced_gpt_assistant import create_ai_assistant
import asyncio

# Assistant yaratish
assistant = create_ai_assistant(
    openai_key="your-openai-key",
    gemini_key="your-gemini-key",
    enable_trading_optimization=True
)

# Chat so'rovi
async def main():
    response = await assistant.chat("Bitcoin narxi hozir qanday?")
    print(response.content)
    print(f"Model: {response.model_used}")
    print(f"Cost: ${response.cost:.4f}")

asyncio.run(main())
```

## Asosiy Foydalanish

### 1. Oddiy Chat

```python
# Qisqa chat
response = await assistant.chat("Men trading haqida so'rashni xohlayman.")
print(response.content)

# Conversation ID bilan (multi-turn)
response1 = await assistant.chat("Salom!", conversation_id="user123")
response2 = await assistant.chat("Qandaysiz?", conversation_id="user123")
```

### 2. Strategy-Based Selection

```python
# Xarajat bo'yicha optimizatsiya
response = await assistant.chat(
    "Nimadir so'rang",
    strategy="cost_optimized"
)

# Sifat bo'yicha optimizatsiya
response = await assistant.chat(
    "Nimadir so'rang",
    strategy="quality_focused"
)

# Tezlik bo'yicha optimizatsiya
response = await assistant.chat(
    "Nimadir so'rang",
    strategy="speed_optimized"
)

# Trading uchun maxsus
response = await assistant.chat(
    "Bitcoin texnik tahlil qiling",
    strategy="trading_specialized"
)
```

### 3. Trading Analysis

```python
# Trading uchun maxsus optimizatsiya
market_data = {
    "symbol": "BTCUSDT",
    "current_price": 45000,
    "volume": 2500000,
    "rsi": 65,
    "macd": 150
}

# Technical analysis
if hasattr(assistant, 'trading_optimizer'):
    response = await assistant.trading_optimizer.enhanced_trading_analysis(
        TaskType.TECHNICAL_ANALYSIS,
        market_data,
        "Qanday strategiya taklif qilasiz?"
    )

# General trading chat
response = await assistant.trading_analysis(
    market_data=market_data,
    question="Bu coin uchun qisqa muddatli outlook qanday?"
)
```

### 4. Streaming Responses

```python
# Real-time streaming
async for response in await assistant.chat(
    "Uzun matn yozib bering",
    stream=True
):
    if response.content:
        print(response.content, end="", flush=True)
```

### 5. Model Comparison

```python
# Bir nechta modelni taqqoslash
from advanced_gpt_assistant import ModelType

results = await assistant.multi_model_comparison(
    "AI nima va qanday ishlaydi?",
    models=[ModelType.GPT4O, ModelType.GEMINI_PRO]
)

for model_type, response in results.items():
    print(f"{model_type.value}: {response.content}")
```

## Performance Monitoring

### 1. Metrikalar olish

```python
# Performance statistikasi
metrics = assistant.get_performance_metrics()
print(f"Total requests: {metrics['total_requests']}")
print(f"Cache hit ratio: {metrics['cache']['hit_ratio']}")

# Model-specific stats
for model_name, stats in metrics['models'].items():
    if stats['total_requests'] > 0:
        print(f"{model_name} - Quality: {stats['avg_quality']:.2f}")
```

### 2. Cost Optimization

```python
# Xarajat optimizatsiya tavsiyalari
recommendations = assistant.optimize_for_cost(budget_limit=0.10)
print("Recommended models:", recommendations['optimal_models'])

for rec in recommendations['recommendations']:
    print(f"Model: {rec['model']}")
    print(f"Cost efficiency: {rec['cost_efficiency']:.2f}")
```

### 3. API Status

```python
# API status tekshirish
status = assistant.get_api_status()
print("OpenAI connected:", status['openai']['connected'])
print("Gemini connected:", status['gemini']['connected'])
```

## Cache Management

```python
# Cache statistikasi
cache_stats = assistant.cache.get_stats()
print(f"Cache entries: {cache_stats['total_entries']}")
print(f"Hit ratio: {cache_stats['hit_ratio']:.2f}")

# Cache ni tozalash
assistant.clear_cache()
```

## Configuration

### Model Konfiguratsiyasi

Har bir model quyidagi parametrlar bilan boshqariladi:

- **max_tokens**: Maksimum token soni
- **cost_per_token**: Token narxi
- **rate_limit**: Daqiqadagi so'rov limiti
- **quality_score**: Sifat ko'rsatkichi
- **supported_tasks**: Qo'llab-quvvatlanuvchi vazifalar

### Custom Model Qo'shish

```python
from advanced_gpt_assistant import ModelType, ModelConfig

# Yangi model qo'shish
new_model = ModelConfig(
    name=ModelType.CUSTOM_MODEL,
    provider="openai",
    max_tokens=4096,
    cost_per_token=0.00001,
    # ... boshqa parametrlar
)

assistant.MODEL_CONFIGS[ModelType.CUSTOM_MODEL] = new_model
```

## Error Handling

```python
try:
    response = await assistant.chat("So'rov")
    if response.error:
        print(f"Error: {response.error}")
    else:
        print(f"Success: {response.content}")
except Exception as e:
    print(f"Exception: {e}")
```

## Test va Demo

### Demo ishga tushirish

```bash
# Oddiy demo
python advanced_gpt_demo.py --demo

# API keys bilan
python advanced_gpt_demo.py --demo --api-keys YOUR_OPENAI_KEY YOUR_GEMINI_KEY

# To'liq test suite
python advanced_gpt_demo.py --test
```

### Test Natijalari

Test tugagandan so'ng natijalar `ai_assistant_test_results.json` fayliga saqlanadi.

## Monitoring va Logging

### Log Level O'rnatish

```python
import logging
logging.basicConfig(level=logging.INFO)

# Faqat error loglari
logging.basicConfig(level=logging.ERROR)
```

### Log Fayllari

- `ai_assistant.log`: Asosiy loglar
- Performance metrics real-time monitoring

## Best Practices

### 1. API Key Xavfsizligi

```python
# .env fayl ishlatish
from dotenv import load_dotenv
load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
```

### 2. Rate Limiting Hisobga Olish

```python
# Ko'p so'rovlar uchun
responses = []
for prompt in prompts:
    response = await assistant.chat(prompt)
    responses.append(response)
    # API rate limit hisobga olib kutish
    await asyncio.sleep(1)
```

### 3. Cache Optimization

```python
# Takrorlanuvchi so'rovlar uchun cache yoqish
response = await assistant.chat(
    "Doimiy savol",
    use_cache=True  # Default True
)
```

### 4. Trading Analysis Optimization

```python
# Trading vazifalar uchun maxsus optimizer
if hasattr(assistant, 'trading_optimizer'):
    response = await assistant.trading_optimizer.enhanced_trading_analysis(
        TaskType.TECHNICAL_ANALYSIS,
        market_data,
        user_question
    )
```

## Muammolarni Hal Qilish

### 1. API Connection Errors

```python
# Connection test
status = assistant.get_api_status()
if not status['openai']['connected']:
    print("OpenAI API connection failed")
if not status['gemini']['connected']:
    print("Gemini API connection failed")
```

### 2. Rate Limit Errors

```python
# Automatic fallback
response = await assistant.chat("So'rov")
# Agar rate limit bo'lsa, avtomatik fallback ishlaydi
```

### 3. High Costs

```python
# Cost monitoring
metrics = assistant.get_performance_metrics()
total_cost = sum(stats['avg_cost'] * stats['total_requests'] 
                for stats in metrics['models'].values())
print(f"Total cost: ${total_cost:.4f}")
```

## Kengaytirish

### 1. Custom Task Types

```python
from advanced_gpt_assistant import TaskType

# Yangi vazifa turi
TaskType.CUSTOM_ANALYSIS = "custom_analysis"
```

### 2. Model Selection Strategy

```python
# Custom strategy
def custom_strategy(self, task_type, context):
    # Custom logic
    return [ModelType.GPT4O]

assistant.model_strategies["custom"] = custom_strategy
```

### 3. Performance Hooks

```python
# Response processing
def custom_evaluator(response):
    # Custom quality assessment
    return response.quality_score + 1.0

assistant.evaluator.evaluate_response = custom_evaluator
```

## Support va Contribution

Agar muammo yoki taklif bo'lsa:

1. Issue yarating GitHub'da
2. Log fayllarini qo'shing
3. Test cases bering
4. Reproducible code snippet yuboring

## License

Bu project MIT license ostida tarqatiladi.

---

**Orion Starline AI Team** | 2025-11-05 | Version 2.0.0