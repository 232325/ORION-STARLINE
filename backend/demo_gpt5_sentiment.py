#!/usr/bin/env python3
"""
GPT-5 Sentiment Analysis Demonstration
Bu script GPT-5 sentiment analysis tizimini ishga tushirish va test qilish uchun
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpt5_sentiment_analysis import GPT5SentimentSystem, AssetClass, SentimentType

async def demo_basic_analysis():
    """Asosiy sentiment tahlili demo"""
    print("=== GPT-5 SENTIMENT ANALYSIS DEMO ===\n")
    
    # API key tekshirish
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY topilmadi!")
        print("Iltimos quyidagi buyruqni bajarib sozlang:")
        print("export OPENAI_API_KEY='sizning-api-kalit-ingiz'")
        return False
    
    # Tizimni yaratish
    print("🔄 Tizim ishga tushmoqda...")
    system = GPT5SentimentSystem(api_key)
    
    # Bitta aktiv uchun test
    print("\n📊 AAPL aktivini tahlil qilish...")
    aapl_data = await system.process_single_asset("AAPL", AssetClass.STOCK)
    
    if aapl_data and aapl_data.sentiment_data:
        print(f"✅ AAPL sentiment tahlili tugallandi:")
        print(f"   Sentiment turi: {aapl_data.sentiment_data.sentiment_type.value}")
        print(f"   Bullish ehtimoli: {aapl_data.sentiment_data.bullish_probability:.2f}")
        print(f"   Bearish ehtimoli: {aapl_data.sentiment_data.bearish_probability:.2f}")
        print(f"   Ishonchlilik: {aapl_data.sentiment_data.confidence:.2f}")
        print(f"   Umumiy hisob: {aapl_data.sentiment_data.overall_score:.2f}")
    else:
        print("❌ AAPL sentiment tahlili bajarilmadi")
        return False
    
    return True

async def demo_multi_asset_analysis():
    """Ko'p aktivlar sentiment tahlili demo"""
    print("\n=== KO'P AKTIVLAR TAHLILI ===\n")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False
    
    system = GPT5SentimentSystem(api_key)
    
    # Faqat bir nechta aktiv bilan test (API costni tejab saqlash uchun)
    test_symbols = ["AAPL", "TSLA", "EUR/USD"]
    test_classes = [AssetClass.STOCK, AssetClass.STOCK, AssetClass.FOREX]
    
    print(f"📈 {len(test_symbols)} ta aktivni parallel tahlil qilish...")
    
    # Parallel processing
    tasks = []
    for symbol, asset_class in zip(test_symbols, test_classes):
        task = system.process_single_asset(symbol, asset_class)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\n📊 NATIJALAR:")
    for i, (symbol, asset_class) in enumerate(zip(test_symbols, test_classes)):
        if isinstance(results[i], Exception):
            print(f"❌ {symbol}: Xato - {results[i]}")
            continue
            
        data = results[i]
        if data and data.sentiment_data:
            print(f"\n🔸 {symbol} ({asset_class.value}):")
            print(f"   Sentiment: {data.sentiment_data.sentiment_type.value}")
            print(f"   Bullish: {data.sentiment_data.bullish_probability:.2f}")
            print(f"   Bearish: {data.sentiment_data.bearish_probability:.2f}")
            print(f"   Confidence: {data.sentiment_data.confidence:.2f}")
            print(f"   News count: {data.news_count}")
    
    return True

async def demo_sentiment_history():
    """Sentiment tarixi demo"""
    print("\n=== SENTIMENT TARIXI ===\n")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False
    
    system = GPT5SentimentSystem(api_key)
    
    # AAPL uchun tarixiy ma'lumotlar
    print("📜 AAPL sentiment tarixini olish...")
    history = await system.get_live_sentiment("AAPL")
    
    if "error" in history:
        print(f"❌ {history['error']}")
        return False
    
    print("✅ AAPL sentiment ma'lumotlari:")
    if history.get("current_sentiment"):
        current = history["current_sentiment"]
        print(f"   Joriy sentiment: {current['sentiment_type']}")
        print(f"   Bullish: {current['bullish_probability']:.2f}")
        print(f"   Bearish: {current['bearish_probability']:.2f}")
    
    if history.get("momentum"):
        momentum = history["momentum"]
        print(f"   Momentum: {momentum.get('momentum', 0):.2f}")
        print(f"   Trend: {momentum.get('trend_direction', 'neutral')}")
    
    print(f"   Tarixiy yozuvlar soni: {history.get('history_count', 0)}")
    print(f"   Oxirgi yangilanish: {history.get('last_updated', 'N/A')}")
    
    return True

async def demo_contrarian_signals():
    """Kontrarian signallar demo"""
    print("\n=== KONTRARIAN SIGNALLAR ===\n")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False
    
    system = GPT5SentimentSystem(api_key)
    aggregator = system.aggregator
    
    # Mock sentiment data for demo
    from gpt5_sentiment_analysis import SentimentScore
    
    extreme_bullish = SentimentScore(
        bullish_probability=0.9,
        bearish_probability=0.1,
        confidence=0.8,
        sentiment_type=SentimentType.BULLISH,
        overall_score=0.8
    )
    
    extreme_bearish = SentimentScore(
        bullish_probability=0.1,
        bearish_probability=0.9,
        confidence=0.8,
        sentiment_type=SentimentType.BEARISH,
        overall_score=-0.8
    )
    
    neutral_sentiment = SentimentScore(
        bullish_probability=0.5,
        bearish_probary=0.5,
        confidence=0.3,
        sentiment_type=SentimentType.NEUTRAL,
        overall_score=0.0
    )
    
    print("🔍 Kontrarian signallar tahlili:")
    
    # Positive price movement with bearish sentiment
    signals = aggregator.detect_contrarian_signals([], -0.1, extreme_bearish)
    print(f"\n📉 Narx pasayish + Bullish sentiment:")
    for signal in signals['contrarian_signals']:
        print(f"   ⚠️  {signal}")
    
    # Negative price movement with bullish sentiment
    signals = aggregator.detect_contrarian_signals([], 0.1, extreme_bullish)
    print(f"\n📈 Narx o'sish + Bearish sentiment:")
    for signal in signals['contrarian_signals']:
        print(f"   ⚠️  {signal}")
    
    return True

async def demo_api_endpoints():
    """API endpoint'lar demo"""
    print("\n=== API ENDPOINTS ===\n")
    
    # FastAPI server ni alohida faylda ishlatish kerak
    print("🌐 API endpoint'lar:")
    print("   GET  / - Tizim holati")
    print("   GET  /health - Sog'liq tekshiruvi") 
    print("   POST /analyze - Sentiment tahlili")
    print("   GET  /sentiment/{symbol} - Bitta aktiv sentimenti")
    print("   GET  /symbols - Mavjud aktivlar ro'yxati")
    print("   WS   /ws/sentiment - Real-time yangilanishlar")
    print("\n📝 FastAPI serverni ishga tushirish uchun:")
    print("   python gpt5_sentiment_analysis.py")
    print("   yoki uvicorn gpt5_sentiment_analysis:app --reload --host 0.0.0.0 --port 8000")

def print_system_info():
    """Tizim haqida ma'lumot"""
    print("\n=== TIZIM HAQIDA MA'LUMOT ===\n")
    
    print("🎯 XUSUSIYATLAR:")
    print("   ✅ GPT-5 API integratsiyasi")
    print("   ✅ Ko'p aktiv turlari (aksialar, forex, metallar)")
    print("   ✅ Turli ma'lumot manbalari (yangiliklar, ijtimoiy tarmoqlar)")
    print("   ✅ Real-time sentiment tahlili")
    print("   ✅ Sentiment tarixi va momentum")
    print("   ✅ Kontrarian signal aniqlash")
    print("   ✅ FastAPI REST API")
    print("   ✅ WebSocket real-time yangilanishlar")
    print("   ✅ SQLite ma'lumotlar bazasi")
    print("   ✅ Response caching")
    print("   ✅ Rate limiting va xato boshqaruvi")
    
    print("\n💰 AKTIV TURLARI:")
    print("   📈 Aksiyalar: AAPL, GOOGL, MSFT, TSLA, NVDA")
    print("   💱 Forex: EUR/USD, GBP/USD, USD/JPY, USD/CHF")
    print("   🥇 Metallar: XAU/USD, XAG/USD, XPT/USD, XPD/USD")
    
    print("\n📊 SENTIMENT METRIKALAR:")
    print("   🟢 Bullish/Bearish ehtimolliklari")
    print("   📊 Ishonchlilik hisoblari")
    print("   📈 Sentiment momentum")
    print("   ⚖️  Kontrarian signallar")
    print("   🎯 Umumiy sentiment hisobi")
    
    print("\n🔧 SOZLASH:")
    print("   1. OpenAI API key ni sozlang: export OPENAI_API_KEY='sizning-kalit'")
    print("   2. Dependencies o'rnating: pip install -r requirements.txt")
    print("   3. API server ishga tushiring: python gpt5_sentiment_analysis.py")
    print("   4. Demo script ishga tushiring: python demo_gpt5_sentiment.py")

async def main():
    """Asosiy demo funksiyasi"""
    print(f"🚀 GPT-5 Sentiment Analysis Demo")
    print(f"⏰ Sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 OpenAI API: {'✅ Sozlangan' if os.getenv('OPENAI_API_KEY') else '❌ Sozlanmagan'}")
    
    # Tizim haqida ma'lumot
    print_system_info()
    
    # Demo'larni ketma-ket bajarish
    demos = [
        ("Asosiy tahlil", demo_basic_analysis),
        ("Ko'p aktivlar tahlili", demo_multi_asset_analysis),
        ("Sentiment tarixi", demo_sentiment_history),
        ("Kontrarian signallar", demo_contrarian_signals),
        ("API endpoint'lar", demo_api_endpoints)
    ]
    
    for name, demo_func in demos:
        print(f"\n{'='*50}")
        print(f"🔄 {name} boshlanmoqda...")
        
        try:
            result = await demo_func()
            if result:
                print(f"✅ {name} muvaffaqiyatli tugallandi")
            else:
                print(f"⚠️  {name} bajarilmadi (API key yoki boshqa xato)")
        except Exception as e:
            print(f"❌ {name} xatosi: {e}")
    
    print(f"\n{'='*50}")
    print("🎉 Demo tugallandi!")
    print("\n📖 Batafsil ma'lumot uchun:")
    print("   • README.md faylini o'qang")
    print("   • API documentation: /docs endpoint")
    print("   • Example usage: python gpt5_sentiment_analysis.py")

if __name__ == "__main__":
    # Event loop va demo
    asyncio.run(main())