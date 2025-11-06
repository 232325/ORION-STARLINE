#!/usr/bin/env python3
"""
GPT-5 Sentiment Analysis Test Script
Tizimni test qilish va validatsiya qilish
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Import test"""
    print("🔍 Import test...")
    
    try:
        from gpt5_sentiment_analysis import (
            GPT5SentimentSystem, 
            SentimentScore, 
            MarketData, 
            AssetClass, 
            SentimentType,
            DataSource
        )
        print("✅ Barcha import'lar muvaffaqiyatli")
        return True
    except ImportError as e:
        print(f"❌ Import xatosi: {e}")
        return False

def test_config():
    """Configuration test"""
    print("\n⚙️ Configuration test...")
    
    try:
        from config import SENTIMENT_CONFIG
        required_keys = [
            'openai_api_key', 'gpt5_model', 'rate_limit', 
            'batch_size', 'stocks', 'forex_pairs', 'metals'
        ]
        
        for key in required_keys:
            if key not in SENTIMENT_CONFIG:
                print(f"❌ Kalit topilmadi: {key}")
                return False
        
        print("✅ Konfiguratsiya to'g'ri")
        return True
        
    except Exception as e:
        print(f"❌ Configuration xatosi: {e}")
        return False

def test_api_key():
    """API key test"""
    print("\n🔑 API key test...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY topilmadi - demo test davom etadi")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ API key formati noto'g'ri (sk- bilan boshlanishi kerak)")
        return False
    
    print("✅ API key to'g'ri formatda")
    return True

def test_data_structures():
    """Data structures test"""
    print("\n📊 Data structures test...")
    
    try:
        from gpt5_sentiment_analysis import SentimentScore, SentimentType
        
        # SentimentScore test
        sentiment = SentimentScore(
            bullish_probability=0.7,
            bearish_probability=0.3,
            confidence=0.8,
            sentiment_type=SentimentType.BULLISH,
            overall_score=0.4
        )
        
        assert sentiment.bullish_probability == 0.7
        assert sentiment.sentiment_type == SentimentType.BULLISH
        assert sentiment.to_dict()['sentiment_type'] == 'bullish'
        
        print("✅ Data structures ishlaydi")
        return True
        
    except Exception as e:
        print(f"❌ Data structures xatosi: {e}")
        return False

async def test_system_creation():
    """System creation test"""
    print("\n🏗️ System creation test...")
    
    try:
        api_key = "dummy_key_for_test"
        from gpt5_sentiment_analysis import GPT5SentimentSystem
        
        system = GPT5SentimentSystem(api_key)
        
        # Asset checks
        assert len(system.stocks) == 5
        assert len(system.forex_pairs) == 4
        assert len(system.metals) == 4
        assert "AAPL" in system.stocks
        assert "EUR/USD" in system.forex_pairs
        assert "XAU/USD" in system.metals
        
        print("✅ System yaratish muvaffaqiyatli")
        return True
        
    except Exception as e:
        print(f"❌ System creation xatosi: {e}")
        return False

async def test_mock_analysis():
    """Mock analysis test (API key'siz)"""
    print("\n🧪 Mock analysis test...")
    
    try:
        from gpt5_sentiment_analysis import SentimentAggregator, SentimentScore, SentimentType
        
        aggregator = SentimentAggregator()
        
        # Mock sentiment data
        mock_sentiments = [
            SentimentScore(0.7, 0.3, 0.8, SentimentType.BULLISH, 0.4),
            SentimentScore(0.6, 0.4, 0.7, SentimentType.BULLISH, 0.2),
            SentimentScore(0.4, 0.6, 0.6, SentimentType.BEARISH, -0.2)
        ]
        
        # Aggregate test
        result = aggregator.calculate_market_sentiment(mock_sentiments)
        
        assert 0 <= result.bullish_probability <= 1
        assert 0 <= result.bearish_probability <= 1
        assert 0 <= result.confidence <= 1
        assert -1 <= result.overall_score <= 1
        
        print("✅ Mock analysis ishlaydi")
        return True
        
    except Exception as e:
        print(f"❌ Mock analysis xatosi: {e}")
        return False

async def test_contrarian_signals():
    """Contrarian signals test"""
    print("\n⚖️ Contrarian signals test...")
    
    try:
        from gpt5_sentiment_analysis import SentimentAggregator, SentimentScore, SentimentType
        
        aggregator = SentimentAggregator()
        
        # Extreme bullish sentiment with negative price
        extreme_bullish = SentimentScore(0.9, 0.1, 0.8, SentimentType.BULLISH, 0.8)
        signals = aggregator.detect_contrarian_signals([], -0.1, extreme_bullish)
        
        assert len(signals['contrarian_signals']) > 0
        assert 'contrarian' in signals['recommendation'].lower()
        
        print("✅ Kontrarian signallar ishlaydi")
        return True
        
    except Exception as e:
        print(f"❌ Contrarian signals xatosi: {e}")
        return False

def test_database():
    """Database test"""
    print("\n💾 Database test...")
    
    try:
        import tempfile
        from gpt5_sentiment_analysis import SentimentDatabase
        
        # Temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = SentimentDatabase(db_path)
        
        # Test data insertion
        test_data = {
            'symbol': 'TEST',
            'asset_class': 'stock',
            'timestamp': datetime.now(),
            'price': 100.0,
            'volume': 1000,
            'news_count': 5,
            'overall_sentiment': 0.5
        }
        
        # Mock market data for test
        from gpt5_sentiment_analysis import MarketData, AssetClass, SentimentScore
        market_data = MarketData(
            symbol='TEST',
            asset_class=AssetClass.STOCK,
            timestamp=datetime.now(),
            price=100.0,
            volume=1000,
            news_count=5,
            sentiment_data=SentimentScore(0.6, 0.4, 0.7, SentimentType.BULLISH, 0.2)
        )
        
        db.save_market_data(market_data)
        
        # Test data retrieval
        history = db.get_sentiment_history('TEST', days=1)
        
        # Clean up
        os.unlink(db_path)
        
        print("✅ Database ishlaydi")
        return True
        
    except Exception as e:
        print(f"❌ Database xatosi: {e}")
        return False

async def test_websocket_imports():
    """WebSocket imports test"""
    print("\n🔌 WebSocket imports test...")
    
    try:
        import websockets
        import uvicorn
        from fastapi import FastAPI
        print("✅ WebSocket dependencies mavjud")
        return True
    except ImportError as e:
        print(f"⚠️  WebSocket dependency yo'q: {e}")
        return False

async def run_comprehensive_test():
    """Barcha testlarni bajarish"""
    print("🚀 GPT-5 Sentiment Analysis Comprehensive Test")
    print(f"⏰ Sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    tests = [
        ("Import test", test_imports),
        ("Configuration test", test_config),
        ("API key test", test_api_key),
        ("Data structures test", test_data_structures),
        ("System creation test", test_system_creation),
        ("Mock analysis test", test_mock_analysis),
        ("Contrarian signals test", test_contrarian_signals),
        ("Database test", test_database),
        ("WebSocket imports test", test_websocket_imports)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"🧪 {name}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results.append((name, result))
            
            if result:
                print(f"✅ {name} - PASS")
            else:
                print(f"⚠️  {name} - WARNING")
                
        except Exception as e:
            print(f"❌ {name} - FAIL: {e}")
            results.append((name, False))
    
    # Test natijalari
    print("\n" + "="*60)
    print("📊 TEST NATIJALARI:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status:8} | {name}")
        if result:
            passed += 1
    
    print(f"\n📈 Statistika: {passed}/{total} test o'tdi ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 Barcha testlar muvaffaqiyatli! Tizim ishga tayyor.")
        print("\n💡 Keyingi qadamlar:")
        print("   1. OPENAI_API_KEY environment variable ni sozlang")
        print("   2. python demo_gpt5_sentiment.py ishga tushiring")
        print("   3. python gpt5_sentiment_analysis.py API server uchun")
        
    elif passed >= total * 0.7:  # 70% yoki ko'proq
        print("\n✅ Ko'p testlar o'tdi. Minor issues mavjud.")
        print("\n⚠️  Diqqat:")
        if not test_api_key():
            print("   • OPENAI_API_KEY sozlang")
        if not test_websocket_imports():
            print("   • WebSocket dependencies o'rnating: pip install websockets uvicorn")
            
    else:
        print("\n❌ Ko'p testlar o'tmadi. Critical issues mavjud.")
        print("\n🔧 Muammolarni hal qiling va qaytadan urinib ko'ring.")
    
    return passed == total

async def main():
    """Main test function"""
    success = await run_comprehensive_test()
    
    # Demo ko'rsatish
    if success:
        print(f"\n{'='*60}")
        print("🎯 DEMO START")
        print("Demo faylini ishga tushirish uchun:")
        print("   python demo_gpt5_sentiment.py")
        print("\nAPI serverni ishga tushirish uchun:")
        print("   python gpt5_sentiment_analysis.py")
    
    return success

if __name__ == "__main__":
    # Tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)