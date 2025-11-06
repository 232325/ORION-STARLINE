"""
Real-time Data Integration System - Complete Demo
Real-time Ma'lumotlar Integratsiya Tizimi - To'liq Demo

Bu demo barcha funksiyalarni ko'rsatadi:
- Real-time market data streaming
- News integration va sentiment analysis
- Technical analysis indicators
- Portfolio risk analytics
- AI signal generation
- Economic calendar integration
- Social media sentiment tracking
- Anomaly detection
- Performance optimization
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Import tizim komponentalari
from data_integration import (
    DataIntegrationManager, 
    RealTimeDataIntegration, 
    DataConfig,
    SignalGenerator,
    RiskAnalyticsIntegration,
    RateLimiter,
    AnomalyDetector,
    PerformanceOptimizer
)

from market_data import MarketDataManager, MultiTimeframeFetcher
from news_feed import NewsFeedManager

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveDataIntegrationDemo:
    """Real-time Data Integration tizimi to'liq demo"""
    
    def __init__(self):
        self.config = self._create_config()
        self.integration_manager = DataIntegrationManager()
        self.market_manager = MarketDataManager()
        self.news_manager = NewsFeedManager()
        self.fetcher = MultiTimeframeFetcher(self.market_manager)
        
        # Test symbols
        self.symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META"]
        self.user_id = "demo_user_123"
        
        print("🚀 Real-time Data Integration Tizimi Tushirilmoqda...")
        print("=" * 60)
    
    def _create_config(self) -> DataConfig:
        """Demo konfiguratsiyasini yaratish"""
        return DataConfig(
            # API keys (demo uchun)
            alpha_vantage_key="demo_alpha_key",
            finnhub_key="demo_finnhub_key", 
            polygon_key="demo_polygon_key",
            newsapi_key="demo_newsapi_key",
            twitter_bearer_token="demo_twitter_token",
            
            # Streaming sozlamalari
            update_interval=2,  # 2 soniya
            cache_timeout=300,  # 5 daqiqa
            max_workers=8,
            
            # Enabled sources
            enabled_sources=['yahoo', 'alpha_vantage', 'finnhub'],
            timeframes=['1m', '5m', '15m', '1h', '4h', '1d']
        )
    
    async def demo_market_data_integration(self):
        """1. Bozor ma'lumotlari integratsiyasi demo"""
        print("\n📈 1. BOZOR MA'LUMOTLARI INTEGRATSIYASI")
        print("-" * 50)
        
        try:
            # Single symbol comprehensive data
            symbol = "AAPL"
            print(f"\n🔍 {symbol} uchun keng qamrovli ma'lumotlar:")
            
            market_data = await self.integration_manager.get_comprehensive_market_data(symbol)
            
            if market_data:
                consensus = market_data.get('consensus', {})
                price_data = consensus.get('price', {})
                sentiment = market_data.get('sentiment', {})
                
                print(f"  • Narx: ${price_data.get('mean', 0):.2f}")
                print(f"  • O'zgarish: {market_data.get('change_percent', 0):.2f}%")
                print(f"  • Hajm: {market_data.get('volume', 0):,}")
                print(f"  • Ma'lumotlar sifati: {market_data.get('data_quality', {}).get('quality_score', 0):.2f}")
                print(f"  • Sentiment: {sentiment.get('market_mood', 'unknown')}")
            
            # Multi symbol comparison
            print(f"\n📊 Ko'p symbol taqqoslash:")
            for sym in self.symbols[:3]:
                data = await self.integration_manager.engine.integrate_market_data(sym)
                quality = data.get('quality_score', 0)
                print(f"  • {sym}: Sifat balli {quality:.2f}")
        
        except Exception as e:
            print(f"❌ Bozor ma'lumotlari xatosi: {e}")
    
    async def demo_real_time_streaming(self):
        """2. Real-time streaming demo"""
        print("\n⚡ 2. REAL-TIME STREAMING")
        print("-" * 50)
        
        try:
            # WebSocket streaming (demo uchun qisqa vaqt)
            print("🌐 Real-time streaming boshlammoqda...")
            streaming_symbols = ["BTCUSDT", "ETHUSDT"]
            
            # Streaming task yaratish
            streaming_task = asyncio.create_task(
                self.market_manager.start_streaming(streaming_symbols, ["binance"])
            )
            
            # 3 soniya kutish
            await asyncio.sleep(3)
            
            # Ma'lumotlarni olish
            for symbol in streaming_symbols:
                data = self.market_manager.get_real_time_data(symbol)
                if data and 'current' in data:
                    current = data['current']
                    print(f"  📊 {symbol}: ${current.get('close', 0):.2f}")
            
            # Streaming to'xtatish
            await self.market_manager.stop_streaming("binance")
            print("✅ Streaming to'xtatildi")
            
        except Exception as e:
            print(f"❌ Streaming xatosi: {e}")
    
    async def demo_technical_analysis(self):
        """3. Texnik tahlil demo"""
        print("\n📉 3. TEXNIK TAHLIL")
        print("-" * 50)
        
        try:
            for symbol in self.symbols[:3]:
                print(f"\n🔬 {symbol} texnik indikatorlari:")
                
                # Multi-timeframe data
                multi_tf = await self.fetcher.get_multi_timeframe_data(symbol)
                
                if 'timeframes' in multi_tf:
                    for tf, data in multi_tf['timeframes'].items():
                        indicators = data.get('indicators', {})
                        print(f"  {tf}:")
                        print(f"    RSI: {indicators.get('rsi', 0):.1f}")
                        print(f"    MACD: {indicators.get('macd', 0):.3f}")
                        print(f"    MA20: ${indicators.get('ma20', 0):.2f}")
        
        except Exception as e:
            print(f"❌ Texnik tahlil xatosi: {e}")
    
    async def demo_news_sentiment_analysis(self):
        """4. Yangilik va sentiment analizi demo"""
        print("\n📰 4. YANGILIK VA SENTIMENT ANALIZI")
        print("-" * 50)
        
        try:
            # Comprehensive sentiment analysis
            print("🔍 Sentiment tahlili...")
            sentiment_data = await self.news_manager.get_comprehensive_sentiment(self.symbols)
            
            for symbol, metrics in sentiment_data.items():
                print(f"\n📊 {symbol} Sentiment:")
                print(f"  • Umumiy sentiment: {metrics.overall_score:.3f} ({metrics.sentiment_trend})")
                print(f"  • Yangiliklar: {metrics.news_sentiment:.3f}")
                print(f"  • Ijtimoiy tarmoq: {metrics.social_sentiment:.3f}")
                print(f"  • Ishonchlilik: {metrics.confidence:.2f}")
                print(f"  • Ma'lumotlar soni: {metrics.volume}")
            
            # News summary
            print(f"\n📄 Yangiliklar xulosasi:")
            news_summary = await self.news_manager.get_news_summary(self.symbols)
            
            breakdown = news_summary.get('sentiment_breakdown', {})
            print(f"  • Jami maqolalar: {news_summary.get('total_articles', 0)}")
            print(f"  • Ijobiy: {breakdown.get('positive', 0)}")
            print(f"  • Salbiy: {breakdown.get('negative', 0)}")
            print(f"  • Neytral: {breakdown.get('neutral', 0)}")
            print(f"  • O'rtacha sentiment: {news_summary.get('average_sentiment', 0):.3f}")
            
        except Exception as e:
            print(f"❌ Sentiment tahlil xatosi: {e}")
    
    async def demo_portfolio_risk_analytics(self):
        """5. Portfolio risk analitikasi demo"""
        print("\n💼 5. PORTFOLIO RISK ANALITIKASI")
        print("-" * 50)
        
        try:
            # Mock portfolio positions
            positions = [
                {"symbol": "AAPL", "quantity": 100, "avg_price": 150.0},
                {"symbol": "GOOGL", "quantity": 50, "avg_price": 2800.0},
                {"symbol": "MSFT", "quantity": 75, "avg_price": 350.0},
                {"symbol": "TSLA", "quantity": 25, "avg_price": 800.0}
            ]
            
            print("📊 Portfolio metrikalari hisoblanmoqda...")
            
            # Risk analytics (from data_integration)
            integration = RealTimeDataIntegration(self.config)
            risk_analytics = RiskAnalyticsIntegration(integration.engine)
            
            risk_metrics = await risk_analytics.calculate_portfolio_risk(
                self.user_id, positions
            )
            
            if risk_metrics:
                print(f"\n📈 Portfolio Risk Metrikalari:")
                print(f"  • Jami qiymat: ${risk_metrics.get('total_value', 0):,.2f}")
                print(f"  • Umumiy risk: ${risk_metrics.get('total_risk', 0):,.2f}")
                print(f"  • Risk/Value nisbati: {risk_metrics.get('risk_value_ratio', 0):.3f}")
                print(f"  • Diversifikatsiya: {risk_metrics.get('diversification_score', 0):.2f}")
                print(f"  • VaR 95%: ${risk_metrics.get('var_95', 0):,.2f}")
                print(f"  • VaR 99%: ${risk_metrics.get('var_99', 0):,.2f}")
                print(f"  • Max Drawdown: ${risk_metrics.get('max_drawdown_estimate', 0):,.2f}")
                print(f"  • Sharpe Ratio: {risk_metrics.get('sharpe_ratio_estimate', 0):.2f}")
                
                # Position breakdown
                position_details = risk_metrics.get('position_details', [])
                print(f"\n📊 Pozitsiya tafsilotlari:")
                for pos in position_details:
                    print(f"  • {pos['symbol']}: ${pos['value']:,.2f} ({pos['weight']:.1%})")
            
            integration.cleanup()
            
        except Exception as e:
            print(f"❌ Risk analitikasi xatosi: {e}")
    
    async def demo_ai_signal_generation(self):
        """6. AI signal generatsiyasi demo"""
        print("\n🤖 6. AI SIGNAL GENERATSIYASI")
        print("-" * 50)
        
        try:
            integration = RealTimeDataIntegration(self.config)
            signal_generator = SignalGenerator(integration.engine)
            
            for symbol in self.symbols[:3]:
                print(f"\n🎯 {symbol} AI signallari:")
                
                signals = await signal_generator.generate_signals(symbol)
                
                if signals:
                    buy_signals = signals.get('signals', {}).get('buy', [])
                    sell_signals = signals.get('signals', {}).get('sell', [])
                    confidence = signals.get('confidence', 0)
                    
                    print(f"  • Ishonschlilik: {confidence:.2f}")
                    print(f"  • Sotib olish signallari: {len(buy_signals)}")
                    print(f"  • Sotish signallari: {len(sell_signals)}")
                    
                    if buy_signals:
                        print("  📈 Sotib olish signallari:")
                        for signal in buy_signals[:2]:
                            print(f"    - {signal.get('type', 'unknown')}: {signal.get('signal', 'unknown')}")
                    
                    if sell_signals:
                        print("  📉 Sotish signallari:")
                        for signal in sell_signals[:2]:
                            print(f"    - {signal.get('type', 'unknown')}: {signal.get('signal', 'unknown')}")
                    
                    reasons = signals.get('reasons', [])
                    if reasons:
                        print("  💡 Sabablar:")
                        for reason in reasons:
                            print(f"    - {reason}")
            
            integration.cleanup()
            
        except Exception as e:
            print(f"❌ Signal generatsiyasi xatosi: {e}")
    
    async def demo_economic_calendar(self):
        """7. Iqtisodiy kalendar demo"""
        print("\n📅 7. IQTISODIY KALENDAR")
        print("-" * 50)
        
        try:
            print("📊 Kelajakdagi muhim voqealar:")
            
            # Economic calendar data
            events = await self.integration_manager.engine.get_economic_calendar_data()
            
            for event in events[:5]:
                impact = event.get('impact', 'LOW')
                impact_emoji = "🔴" if impact == "HIGH" else "🟡" if impact == "MEDIUM" else "🟢"
                
                print(f"  {impact_emoji} {event.get('date', 'unknown')}: {event.get('event', 'unknown')}")
                print(f"     Davlat: {event.get('currency', 'unknown')}")
                print(f"     Daraja: {impact}")
                
                if event.get('forecast'):
                    print(f"     Prognoz: {event.get('forecast')}")
                if event.get('previous'):
                    print(f"     Avvalgi: {event.get('previous')}")
        
        except Exception as e:
            print(f"❌ Economic calendar xatosi: {e}")
    
    async def demo_social_media_tracking(self):
        """8. Ijtimoiy tarmoq tracking demo"""
        print("\n📱 8. IJTIMOIY TARMOQ TRACKING")
        print("-" * 50)
        
        try:
            print("🐦 Twitter va Reddit sentiment tracking...")
            
            # Social media posts
            social_posts = await self.news_manager.fetch_social_sentiment(
                ["AAPL", "TSLA"], limit=20
            )
            
            # Platform breakdown
            platform_stats = {}
            for post in social_posts:
                platform = post.platform
                if platform not in platform_stats:
                    platform_stats[platform] = {'count': 0, 'sentiment': []}
                
                platform_stats[platform]['count'] += 1
                platform_stats[platform]['sentiment'].append(post.sentiment_score)
            
            print(f"\n📊 Platform statistikasi:")
            for platform, stats in platform_stats.items():
                avg_sentiment = sum(stats['sentiment']) / len(stats['sentiment'])
                count = stats['count']
                
                sentiment_emoji = "📈" if avg_sentiment > 0.1 else "📉" if avg_sentiment < -0.1 else "➡️"
                print(f"  {sentiment_emoji} {platform.title()}: {count} posts, sentiment {avg_sentiment:.3f}")
            
            # High engagement posts
            high_engagement = [p for p in social_posts if p.engagement > 500]
            if high_engagement:
                print(f"\n🔥 Yuqori engagement postlar ({len(high_engagement)}):")
                for post in high_engagement[:3]:
                    print(f"  • {post.platform}: {post.content[:60]}...")
        
        except Exception as e:
            print(f"❌ Social media tracking xatosi: {e}")
    
    async def demo_anomaly_detection(self):
        """9. Anomaly detection demo"""
        print("\n🚨 9. ANOMALY DETECTION")
        print("-" * 50)
        
        try:
            # Mock historical data for demo
            import numpy as np
            from data_integration import AnomalyDetector
            
            detector = AnomalyDetector()
            
            # Generate some test data
            historical_prices = [100 + np.random.normal(0, 5) for _ in range(30)]
            current_price = 120  # Potential anomaly
            historical_volumes = [10000 + np.random.normal(0, 2000) for _ in range(30)]
            current_volume = 50000  # Volume spike
            
            print("🔍 Anomaly detection tahlili...")
            
            # Price anomaly
            price_anomaly = detector.detect_price_anomaly(current_price, historical_prices)
            if price_anomaly['is_anomaly']:
                print(f"  🚨 Narx anomalisi topildi!")
                print(f"    Z-score: {price_anomaly['z_score']:.2f}")
                print(f"    Jiddiylik: {price_anomaly['severity']:.2f}")
            else:
                print(f"  ✅ Narx normal")
            
            # Volume anomaly
            volume_anomaly = detector.detect_volume_anomaly(current_volume, historical_volumes)
            if volume_anomaly['is_anomaly']:
                print(f"  🚨 Hajm anomalisi topildi!")
                print(f"    O'zgarish: {volume_anomaly['volume_ratio']:.1f}x normal")
                print(f"    Jiddiylik: {volume_anomaly['severity']:.2f}")
            else:
                print(f"  ✅ Hajm normal")
        
        except Exception as e:
            print(f"❌ Anomaly detection xatosi: {e}")
    
    async def demo_performance_optimization(self):
        """10. Performance optimization demo"""
        print("\n⚡ 10. PERFORMANCE OPTIMIZATION")
        print("-" * 50)
        
        try:
            print("📊 Tizim performance metrikalari...")
            
            # System performance
            integration = RealTimeDataIntegration(self.config)
            health = await integration.health_check_advanced()
            
            if health:
                cache_efficiency = health.get('cache_efficiency', {})
                recommendations = health.get('optimization_recommendations', [])
                
                print(f"\n💾 Cache samaradorligi:")
                for cache_type, efficiency in cache_efficiency.items():
                    print(f"  • {cache_type}: {efficiency:.2%}")
                
                print(f"\n🔧 Optimizatsiya tavsiyalari:")
                if recommendations:
                    for rec in recommendations[:3]:
                        print(f"  • {rec}")
                else:
                    print("  ✅ Optimizatsiya talab qilinmaydi")
            
            integration.cleanup()
            
        except Exception as e:
            print(f"❌ Performance optimization xatosi: {e}")
    
    async def demo_comprehensive_dashboard(self):
        """11. Comprehensive dashboard demo"""
        print("\n📋 11. COMPREHENSIVE DASHBOARD")
        print("-" * 50)
        
        try:
            print("📊 Dashboard ma'lumotlari tayyorlanmoqda...")
            
            integration = RealTimeDataIntegration(self.config)
            
            # Comprehensive dashboard data
            dashboard_data = await integration.get_comprehensive_dashboard_data(self.symbols[:3])
            
            if dashboard_data:
                symbols = dashboard_data.get('symbols', {})
                market_overview = dashboard_data.get('market_overview', {})
                
                print(f"\n📈 Bozor umumiy holati:")
                print(f"  • Ishlab turgan symbollar: {len(symbols)}")
                print(f"  • O'rtacha narx: ${market_overview.get('average_price', 0):.2f}")
                print(f"  • Jami hajm: {market_overview.get('total_volume', 0):,}")
                
                positive = market_overview.get('positive_count', 0)
                negative = market_overview.get('negative_count', 0)
                neutral = market_overview.get('neutral_count', 0)
                
                print(f"  • Ijobiy: {positive}, Salbiy: {negative}, Neytral: {neutral}")
                
                # Top movers
                top_movers = dashboard_data.get('top_movers', {})
                gainers = top_movers.get('gainers', [])
                losers = top_movers.get('losers', [])
                
                if gainers:
                    print(f"\n📈 Eng ko'p ko'tarilganlar:")
                    for symbol, data in gainers[:3]:
                        change = data.get('change_percent', 0)
                        print(f"  • {symbol}: +{change:.2f}%")
                
                if losers:
                    print(f"\n📉 Eng ko'p tushganlar:")
                    for symbol, data in losers[:3]:
                        change = data.get('change_percent', 0)
                        print(f"  • {symbol}: {change:.2f}%")
            
            integration.cleanup()
            
        except Exception as e:
            print(f"❌ Dashboard xatosi: {e}")
    
    async def demo_cache_and_rate_limiting(self):
        """12. Cache va rate limiting demo"""
        print("\n🔄 12. CACHE VA RATE LIMITING")
        print-" * 50)
        
        try:
            from data_integration import RateLimiter
            
            rate_limiter = RateLimiter()
            
            print("⏱️ API rate limiting test:")
            
            # Test rate limiting
            for source in ['yahoo', 'alpha_vantage', 'finnhub']:
                can_request = rate_limiter.can_make_request(source)
                print(f"  • {source}: {'✅ Mumkin' if can_request else '❌ Cheklangan'}")
                
                if can_request:
                    rate_limiter.record_request(source)
                    print(f"    Request ro'yxatga olindi")
            
            # Cache testing
            integration = RealTimeDataIntegration(self.config)
            
            # First request (cache miss)
            start_time = time.time()
            data1 = await integration.get_real_time_price("AAPL")
            first_request_time = time.time() - start_time
            
            # Second request (cache hit)
            start_time = time.time()
            data2 = await integration.get_real_time_price("AAPL")
            second_request_time = time.time() - start_time
            
            print(f"\n💾 Cache performance:")
            print(f"  • Birinchi request: {first_request_time:.3f}s")
            print(f"  • Ikkinchi request: {second_request_time:.3f}s")
            print(f"  • Tezlashtirish: {(first_request_time / second_request_time):.1f}x")
            
            integration.cleanup()
            
        except Exception as e:
            print(f"❌ Cache va rate limiting xatosi: {e}")
    
    async def run_all_demos(self):
        """Barcha demo'larni ketma-ket ishga tushirish"""
        print("🚀 REAL-TIME DATA INTEGRATION TIZIMI - TO'LIQ DEMO")
        print("=" * 60)
        print(f"Boshlanish vaqti: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Test qilinadigan symbollar: {', '.join(self.symbols)}")
        
        start_time = time.time()
        
        # 1. Market Data Integration
        await self.demo_market_data_integration()
        await asyncio.sleep(1)
        
        # 2. Real-time Streaming
        await self.demo_real_time_streaming()
        await asyncio.sleep(2)
        
        # 3. Technical Analysis
        await self.demo_technical_analysis()
        await asyncio.sleep(1)
        
        # 4. News & Sentiment
        await self.demo_news_sentiment_analysis()
        await asyncio.sleep(1)
        
        # 5. Portfolio Risk
        await self.demo_portfolio_risk_analytics()
        await asyncio.sleep(1)
        
        # 6. AI Signal Generation
        await self.demo_ai_signal_generation()
        await asyncio.sleep(1)
        
        # 7. Economic Calendar
        await self.demo_economic_calendar()
        await asyncio.sleep(1)
        
        # 8. Social Media Tracking
        await self.demo_social_media_tracking()
        await asyncio.sleep(1)
        
        # 9. Anomaly Detection
        await self.demo_anomaly_detection()
        await asyncio.sleep(1)
        
        # 10. Performance Optimization
        await self.demo_performance_optimization()
        await asyncio.sleep(1)
        
        # 11. Comprehensive Dashboard
        await self.demo_comprehensive_dashboard()
        await asyncio.sleep(1)
        
        # 12. Cache & Rate Limiting
        await self.demo_cache_and_rate_limiting()
        
        # Demo summary
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"✅ DEMO TUGALLANDI!")
        print(f"Jami vaqt: {total_time:.1f} soniya")
        print(f"Tugash vaqti: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🎯 Asosiy natijalar:")
        print(f"  ✅ Real-time market data integration")
        print(f"  ✅ News va sentiment analysis")
        print(f"  ✅ Technical analysis indicators")
        print(f"  ✅ Portfolio risk analytics")
        print(f"  ✅ AI signal generation")
        print(f"  ✅ Economic calendar integration")
        print(f"  ✅ Social media tracking")
        print(f"  ✅ Anomaly detection")
        print(f"  ✅ Performance optimization")
        print(f"  ✅ Cache va rate limiting")
        print(f"  ✅ Multi-timeframe data support")
        print(f"  ✅ WebSocket streaming")
        
        print("\n📚 Qo'shimcha ma'lumotlar:")
        print(f"  📖 Batafsil hujjat: README_DATA_INTEGRATION.md")
        print(f"  🔧 Requirements: requirements_data_integration.txt")
        print(f"  🏗️ Source code: data_integration.py, market_data.py, news_feed.py")


async def run_quick_demo():
    """Tezkor demo (5 daqiqa ichida)"""
    print("⚡ TEZKOR DEMO - Real-time Data Integration Tizimi")
    print("=" * 60)
    
    demo = ComprehensiveDataIntegrationDemo()
    
    # Faqat asosiy funksiyalar
    await demo.demo_market_data_integration()
    await demo.demo_news_sentiment_analysis()
    await demo.demo_portfolio_risk_analytics()
    await demo.demo_ai_signal_generation()
    
    print("\n✅ Tezkor demo tugallandi!")


if __name__ == "__main__":
    import sys
    
    # Command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        print("Tezkor demo ishga tushirilmoqda...")
        asyncio.run(run_quick_demo())
    else:
        print("To'liq demo ishga tushirilmoqda...")
        print("Bu 10-15 daqiqa davom etishi mumkin.")
        print("Tezkor demo uchun: python demo_data_integration.py quick")
        
        try:
            # Timeout bilan demo
            asyncio.run(asyncio.wait_for(
                ComprehensiveDataIntegrationDemo().run_all_demos(),
                timeout=900  # 15 daqiqa timeout
            ))
        except asyncio.TimeoutError:
            print("\n❌ Demo timeout - maksimal vaqt tugadi (15 daqiqa)")
        except Exception as e:
            print(f"\n❌ Demo xatosi: {e}")
