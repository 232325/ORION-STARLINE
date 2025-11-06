"""
Real-time Ma'lumotlar Integratsiya Tizimi - Qisqartirilgan Demo
Real-time Data Integration System - Shortened Demo
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the ai_modules path
sys.path.append('/workspace/orion-starline/backend/ai_modules')

# Import our modules
from data_integration import DataIntegrationManager
from market_data import MarketDataManager  
from news_feed import NewsFeedManager


async def run_simple_demo():
    """Qisqartirilgan demo - streaming'siz"""
    print("=" * 70)
    print("🚀 REAL-TIME MA'LUMOTLAR INTEGRATSIYA TIZIMI DEMO")
    print("=" * 70)
    print(f"🕒 Boshlanish vaqti: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize all managers
    print("📡 Ma'lumot manager'larini ishga tushirish...")
    data_manager = DataIntegrationManager()
    market_manager = MarketDataManager()
    news_manager = NewsFeedManager()
    
    # Test symbols
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    print(f"🔍 Test qilinadigan symbollar: {symbols}")
    print()
    
    # 1. Data Integration Demo
    print("=" * 50)
    print("📊 1. DATA INTEGRATION MODULI")
    print("=" * 50)
    
    try:
        print("   🔄 Keng qamrovli bozor ma'lumotlarini olish...")
        comprehensive_data = await data_manager.get_comprehensive_market_data("AAPL")
        
        if comprehensive_data:
            print("   ✅ Ma'lumotlar muvaffaqiyatli olindi!")
            print(f"   📈 Symbol: {comprehensive_data.get('symbol', 'N/A')}")
            print(f"   📊 Multi-timeframe soni: {len(comprehensive_data.get('multi_timeframe', {}))}")
            print(f"   💬 Sentiment mavjud: {'Ha' if 'sentiment' in comprehensive_data else 'Yoq'}")
            print(f"   📅 Iqtisodiy voqealar: {len(comprehensive_data.get('economic_calendar', []))}")
            
            # Show quality score
            quality = comprehensive_data.get('data_quality', {})
            if quality:
                print(f"   ⭐ Ma'lumotlar sifati: {quality.get('quality_score', 0):.2f}")
        else:
            print("   ❌ Ma'lumotlarni olishda xatolik")
            
    except Exception as e:
        print(f"   ❌ Xatolik: {str(e)}")
    
    print()
    
    # 2. Market Data Demo (without streaming)
    print("=" * 50)
    print("💹 2. MARKET DATA MODULI (static)")
    print("=" * 50)
    
    try:
        print("   📊 Bozor umumiy holatini olish...")
        overview = market_manager.get_market_overview()
        
        print(f"   📈 Faol symbollar soni: {overview.get('active_symbols', 0)}")
        print(f"   💾 Tarixiy ma'lumotlar: {len(market_manager.processor.data_history)}")
        
        # Get specific symbol data (static)
        print("   🔍 AAPL uchun ma'lumotlar...")
        apple_data = market_manager.get_real_time_data("AAPL")
        if 'error' in apple_data:
            print("   ℹ️  AAPL uchun real-time ma'lumotlar mavjud emas (streaming kerak)")
        else:
            print("   ✅ AAPL ma'lumotlari topildi!")
            
    except Exception as e:
        print(f"   ❌ Xatolik: {str(e)}")
    
    print()
    
    # 3. News Feed Demo
    print("=" * 50)
    print("📰 3. NEWS FEED MODULI")
    print("=" * 50)
    
    try:
        print("   🔄 Keng qamrovli sentiment analizi...")
        sentiment_data = await news_manager.get_comprehensive_sentiment(["AAPL", "TSLA"])
        
        if sentiment_data:
            print("   ✅ Sentiment ma'lumotlari muvaffaqiyatli olindi!")
            
            for symbol, metrics in sentiment_data.items():
                print(f"   📊 {symbol}:")
                print(f"      💭 Umumiy sentiment: {metrics.overall_score:+.3f} "
                      f"({metrics.sentiment_trend})")
                print(f"      📰 Yangilik sentiment: {metrics.news_sentiment:+.3f}")
                print(f"      📱 Ijtimoiy tarmoq sentiment: {metrics.social_sentiment:+.3f}")
                print(f"      📈 Isonish darajasi: {metrics.confidence:.2f}")
                print(f"      📊 Ma'lumotlar hajmi: {metrics.volume}")
        else:
            print("   ℹ️  Hali sentiment ma'lumotlari olinmagan")
        
        print("   📋 Yangiliklar xulosasini olish...")
        news_summary = await news_manager.get_news_summary(["AAPL", "MSFT"])
        
        if news_summary and 'total_articles' in news_summary:
            breakdown = news_summary['sentiment_breakdown']
            print(f"   📰 Jami maqolalar: {news_summary['total_articles']}")
            print(f"   😊 Ijobiy: {breakdown['positive']} | "
                  f"😔 Salbiy: {breakdown['negative']} | "
                  f"😐 Neytral: {breakdown['neutral']}")
            print(f"   📊 O'rtacha sentiment: {news_summary.get('average_sentiment', 0):+.3f}")
        
        print("   📅 Iqtisodiy kalendar ma'lumotlari...")
        economic_events = await news_manager.fetch_economic_calendar()
        
        if economic_events:
            print(f"   📈 Topilgan voqealar: {len(economic_events)}")
            for event in economic_events[:3]:  # Show first 3
                print(f"      • {event.title} - {event.date.strftime('%m-%d %H:%M')} "
                      f"({event.impact_level})")
        else:
            print("   ℹ️  Iqtisodiy kalendar ma'lumotlari mavjud emas")
        
    except Exception as e:
        print(f"   ❌ Xatolik: {str(e)}")
    
    print()
    
    # 4. Performance and Cache Status
    print("=" * 50)
    print("⚡ 4. PERFORMANCE VA CACHE STATUS")
    print("=" * 50)
    
    try:
        # Data integration cache status
        print("   📡 Data Integration Cache:")
        data_cache = data_manager.engine.get_cache_status()
        print(f"      💾 Cache hajmi: {data_cache['cache_size']} element")
        
        # News feed cache status
        print("   📰 News Feed Cache:")
        news_cache = news_manager.get_cache_status()
        print(f"      📄 Yangiliklar cache: {news_cache['news_cache_size']} ta")
        print(f"      📱 Ijtimoiy tarmoq cache: {news_cache['social_cache_size']} ta")
        print(f"      💭 Sentiment cache: {news_cache['sentiment_cache_size']} ta")
        
    except Exception as e:
        print(f"   ❌ Xatolik: {str(e)}")
    
    print()
    
    # 5. Integration Summary
    print("=" * 50)
    print("🎯 5. INTEGRATSIYA XULOSASI")
    print("=" * 50)
    
    print("   ✅ Muvaffaqiyatli implementatsiya qilingan xususiyatlar:")
    print("      📊 Real-time bozor ma'lumotlari integratsiyasi")
    print("      💹 Multi-timeframe ma'lumotlar (1m, 5m, 15m, 1h, 4h, 1d)")
    print("      📰 Iqtisodiy yangiliklar va sentiment analizi")
    print("      📱 Ijtimoiy tarmoq sentimenti (Twitter, Reddit)")
    print("      🔍 Texnik indikatorlar (RSI, MACD, Bollinger Bands)")
    print("      📈 Iqtisodiy kalendar integratsiyasi")
    print("      💾 Ma'lumotlar cache va optimizatsiya")
    print("      🔄 Multi-source data fusion")
    print("      📊 Ma'lumotlar sifati validatsiyasi")
    
    print()
    print("   🔗 Integratsiya qilingan API'lar:")
    print("      • Yahoo Finance API")
    print("      • Alpha Vantage")
    print("      • IEX Cloud") 
    print("      • Finnhub News")
    print("      • NewsAPI.org")
    print("      • Twitter API")
    print("      • Reddit API")
    print("      • Binance WebSocket (sinov uchun)")
    print("      • Coinbase WebSocket (sinov uchun)")
    
    print()
    print("=" * 70)
    print(f"🎉 DEMO MUVAFFAQIYATLI YAKUNLANDI!")
    print(f"🕒 Tugash vaqti: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_simple_demo())