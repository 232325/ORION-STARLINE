"""
News Impact Assessment System - Demo va Test

Bu fayl News Impact Assessment tizimini test qilish va demo qilish uchun ishlatiladi.
"""

import asyncio
import json
from datetime import datetime, timedelta
from news_impact_assessment import (
    NewsImpactAssessmentSystem,
    ImpactLevel,
    AssetClass,
    NewsItem,
    EconomicEvent
)

async def test_economic_calendar_integration():
    """Economic Calendar Integration funksiyasini test qilish"""
    print("🧪 Testing Economic Calendar Integration")
    print("-" * 40)
    
    # Initialize system
    system = NewsImpactAssessmentSystem(
        fred_api_key="demo_key",  # Replace with real key
        gpt5_api_key="demo_key"   # Replace with real key
    )
    
    # Get economic calendar
    events = await system.engine.get_economic_calendar()
    
    print(f"✅ Retrieved {len(events)} economic events")
    
    # Show upcoming high-impact events
    high_impact = [e for e in events if e.impact_level in [ImpactLevel.HIGH, ImpactLevel.BLACK_SWAN]]
    print(f"⚠️  High-impact events: {len(high_impact)}")
    
    for event in high_impact[:5]:
        print(f"  📅 {event.date.strftime('%Y-%m-%d')}: {event.title}")
        print(f"     Impact Level: {event.impact_level.value}")
        print(f"     Asset Impacts: {[(asset.value, impact) for asset, impact in event.asset_impact.items()]}")

async def test_news_classification():
    """GPT-5 News Classification funksiyasini test qilish"""
    print("\n🧪 Testing GPT-5 News Classification")
    print("-" * 40)
    
    # Create sample news items
    sample_news = [
        NewsItem(
            headline="Federal Reserve considers interest rate cut amid economic slowdown",
            content="Fed officials signal potential monetary policy changes as economic indicators weaken",
            timestamp=datetime.now(),
            source="Reuters",
            classification=ImpactLevel.LOW,
            affected_assets={},
            sentiment_score=0.0,
            impact_magnitude=0.0,
            time_to_impact=None,
            recovery_prediction=None
        ),
        NewsItem(
            headline="Unexpected geopolitical crisis triggers market volatility",
            content="Major geopolitical developments cause shock to financial markets",
            timestamp=datetime.now(),
            source="Bloomberg",
            classification=ImpactLevel.LOW,
            affected_assets={},
            sentiment_score=0.0,
            impact_magnitude=0.0,
            time_to_impact=None,
            recovery_prediction=None
        )
    ]
    
    system = NewsImpactAssessmentSystem()
    analyzed_news = await system.engine.analyze_news_impact(sample_news)
    
    print(f"✅ Analyzed {len(analyzed_news)} news items")
    
    for news in analyzed_news:
        print(f"📰 {news.headline[:60]}...")
        print(f"   Classification: {news.classification.value}")
        print(f"   Impact Magnitude: {news.impact_magnitude:.2f}")
        print(f"   Time to Impact: {news.time_to_impact} hours")
        print(f"   Recovery Time: {news.recovery_prediction} hours")
        print()

async def test_market_reaction_prediction():
    """Market Reaction Prediction funksiyasini test qilish"""
    print("🧪 Testing Market Reaction Prediction")
    print("-" * 40)
    
    # Create sample economic event
    event = EconomicEvent(
        title="FOMC Interest Rate Decision",
        date=datetime.now() + timedelta(days=1),
        impact_level=ImpactLevel.HIGH,
        description="Federal Reserve policy meeting",
        previous_value=5.25,
        forecast_value=5.00,
        actual_value=None,
        source="Federal Reserve",
        asset_impact={
            AssetClass.STOCKS: 0.8,
            AssetClass.FOREX: 0.9,
            AssetClass.METALS: 0.6,
            AssetClass.CRYPTO: 0.7,
            AssetClass.BONDS: 0.9
        },
        volatility_impact={
            'VIX': 0.8,
            'US500': 0.7,
            'EURUSD': 0.8,
            'XAUUSD': 0.6
        },
        recovery_time_estimate=48
    )
    
    current_prices = {
        'SPY': 445.50,
        'QQQ': 380.25,
        'GLD': 195.80,
        'EURUSD': 1.0850,
        'market_vol': 0.025
    }
    
    system = NewsImpactAssessmentSystem()
    reactions = system.engine.predict_market_reaction(event, current_prices)
    
    print(f"✅ Generated {len(reactions)} market reaction predictions")
    
    for reaction in reactions:
        direction_emoji = "📈" if reaction.direction == 'bullish' else "📉"
        print(f"📊 {reaction.asset_class.value}:")
        print(f"   Expected Move: {reaction.expected_move:.1%}")
        print(f"   Volatility Spike: {reaction.volatility_spike:.1f}%")
        print(f"   Direction: {reaction.direction} {direction_emoji}")
        print(f"   Confidence: {reaction.confidence:.1%}")
        print(f"   Time to Max Impact: {reaction.time_to_max_impact}h")
        print(f"   Recovery Time: {reaction.recovery_time}h")
        print()

async def test_event_clustering():
    """Event Clustering funksiyasini test qilish"""
    print("🧪 Testing Event Clustering")
    print("-" * 40)
    
    # Create sample events with similar patterns
    events = [
        EconomicEvent(
            title="FOMC Meeting - Interest Rate Decision",
            date=datetime.now() + timedelta(days=7),
            impact_level=ImpactLevel.HIGH,
            description="Fed policy meeting",
            previous_value=None,
            forecast_value=None,
            actual_value=None,
            source="Federal Reserve",
            asset_impact={},
            volatility_impact={},
            recovery_time_estimate=48
        ),
        EconomicEvent(
            title="FOMC Meeting Minutes Release",
            date=datetime.now() + timedelta(days=14),
            impact_level=ImpactLevel.HIGH,
            description="Fed meeting minutes",
            previous_value=None,
            forecast_value=None,
            actual_value=None,
            source="Federal Reserve",
            asset_impact={},
            volatility_impact={},
            recovery_time_estimate=24
        ),
        EconomicEvent(
            title="CPI Inflation Report",
            date=datetime.now() + timedelta(days=10),
            impact_level=ImpactLevel.HIGH,
            description="Consumer Price Index",
            previous_value=None,
            forecast_value=None,
            actual_value=None,
            source="Bureau of Labor Statistics",
            asset_impact={},
            volatility_impact={},
            recovery_time_estimate=36
        )
    ]
    
    system = NewsImpactAssessmentSystem()
    clusters = system.engine.cluster_similar_events(events)
    
    print(f"✅ Identified {len(clusters)} event clusters")
    
    for cluster_name, cluster_events in clusters.items():
        print(f"🔍 {cluster_name}: {len(cluster_events)} events")
        for event in cluster_events:
            print(f"   - {event.date.strftime('%Y-%m-%d')}: {event.title}")

async def test_risk_assessment():
    """Systemic Risk Assessment funksiyasini test qilish"""
    print("\n🧪 Testing Risk Assessment")
    print("-" * 40)
    
    # Create mix of high and low impact events
    events = [
        EconomicEvent(
            title="FOMC Meeting",
            date=datetime.now() + timedelta(days=1),
            impact_level=ImpactLevel.HIGH,
            description="High impact",
            previous_value=None,
            forecast_value=None,
            actual_value=None,
            source="Fed",
            asset_impact={},
            volatility_impact={},
            recovery_time_estimate=48
        ),
        EconomicEvent(
            title="GDP Release",
            date=datetime.now() + timedelta(days=3),
            impact_level=ImpactLevel.HIGH,
            description="High impact",
            previous_value=None,
            forecast_value=None,
            actual_value=None,
            source="BEA",
            asset_impact={},
            volatility_impact={},
            recovery_time_estimate=36
        ),
        EconomicEvent(
            title="Retail Sales",
            date=datetime.now() + timedelta(days=5),
            impact_level=ImpactLevel.MEDIUM,
            description="Medium impact",
            previous_value=None,
            forecast_value=None,
            actual_value=None,
            source="Census Bureau",
            asset_impact={},
            volatility_impact={},
            recovery_time_estimate=24
        )
    ]
    
    system = NewsImpactAssessmentSystem()
    risk_assessment = system.engine._assess_systemic_risk(events)
    
    print("🚨 Systemic Risk Assessment:")
    print(f"   Risk Level: {risk_assessment['risk_level']}")
    print(f"   High Impact Events: {risk_assessment['high_impact_count']}")
    print(f"   Total Impact Score: {risk_assessment['total_impact_score']:.2f}")
    print(f"   Recommendation: {risk_assessment['recommendation']}")

async def test_allocation_recommendations():
    """Asset Allocation Recommendations funksiyasini test qilish"""
    print("\n🧪 Testing Allocation Recommendations")
    print("-" * 40)
    
    # Create events that should trigger allocation changes
    events = [
        EconomicEvent(
            title="CPI Inflation Report",
            date=datetime.now() + timedelta(days=1),
            impact_level=ImpactLevel.HIGH,
            description="Inflation data",
            previous_value=None,
            forecast_value=None,
            actual_value=None,
            source="BLS",
            asset_impact={},
            volatility_impact={},
            recovery_time_estimate=36
        ),
        EconomicEvent(
            title="Employment Situation Report",
            date=datetime.now() + timedelta(days=7),
            impact_level=ImpactLevel.HIGH,
            description="Jobs data",
            previous_value=None,
            forecast_value=None,
            actual_value=None,
            source="BLS",
            asset_impact={},
            volatility_impact={},
            recovery_time_estimate=48
        )
    ]
    
    system = NewsImpactAssessmentSystem()
    allocations = system.engine._generate_allocation_recommendations(events)
    
    print("💼 Recommended Asset Allocation:")
    for asset, allocation in allocations.items():
        print(f"   {asset.upper()}: {allocation:.1%}")
    
    print("\n📊 Allocation Changes from Base:")
    base = {'stocks': 0.40, 'bonds': 0.30, 'metals': 0.15, 'forex': 0.10, 'crypto': 0.05}
    for asset, current in allocations.items():
        base_allocation = base.get(asset, 0)
        change = current - base_allocation
        if abs(change) > 0.01:  # Only show significant changes
            direction = "📈" if change > 0 else "📉"
            print(f"   {asset.upper()}: {change:+.1%} {direction}")

async def test_real_time_alerts():
    """Real-time Alerts funksiyasini test qilish"""
    print("\n🧪 Testing Real-time Alerts")
    print("-" * 40)
    
    system = NewsImpactAssessmentSystem()
    alerts = await system.get_real_time_alerts()
    
    print(f"🚨 Generated {len(alerts)} real-time alerts:")
    
    for alert in alerts:
        level_emoji = "🔴" if alert['level'] == 'HIGH' else "🟡" if alert['level'] == 'MEDIUM' else "🟢"
        print(f"   {level_emoji} [{alert['level']}] {alert['message']}")
        print(f"      Affected Assets: {', '.join(alert['assets'])}")
        print(f"      Timestamp: {alert['timestamp']}")
        print()

async def run_comprehensive_demo():
    """To'liq tizimni demo qilish"""
    print("🚀 News Impact Assessment System - Comprehensive Demo")
    print("=" * 60)
    
    # Run all tests
    await test_economic_calendar_integration()
    await test_news_classification()
    await test_market_reaction_prediction()
    await test_event_clustering()
    await test_risk_assessment()
    await test_allocation_recommendations()
    await test_real_time_alerts()
    
    print("\n🎯 Full System Integration Test")
    print("-" * 40)
    
    # Initialize system with current market data
    current_prices = {
        'SPY': 445.50,
        'QQQ': 380.25,
        'GLD': 195.80,
        'EURUSD': 1.0850,
        'USDJPY': 149.50,
        'VIX': 18.5,
        'BTCUSD': 42500.00,
        'TLT': 95.20,
        'market_vol': 0.025
    }
    
    system = NewsImpactAssessmentSystem()
    
    # Run complete assessment
    print("Running full impact assessment...")
    report = await system.run_full_assessment(current_prices)
    
    if 'error' not in report:
        print("\n📊 Full Assessment Results:")
        print(f"✅ Assessment completed successfully")
        print(f"📈 Summary:")
        print(f"   - Total Economic Events: {report['summary']['total_events']}")
        print(f"   - High Impact Events: {report['summary']['high_impact_events']}")
        print(f"   - Black Swan Events: {report['summary']['black_swan_events']}")
        print(f"   - News Items Analyzed: {report['summary']['news_items_analyzed']}")
        
        print(f"\n⚠️  Risk Assessment:")
        risk = report['risk_assessment']
        print(f"   - Risk Level: {risk['risk_level']}")
        print(f"   - High Impact Count: {risk['high_impact_count']}")
        print(f"   - Total Impact Score: {risk['total_impact_score']:.2f}")
        print(f"   - Recommendation: {risk['recommendation']}")
        
        print(f"\n💼 Asset Allocation Recommendations:")
        for asset, allocation in report['asset_allocation_recommendations'].items():
            print(f"   - {asset.upper()}: {allocation:.1%}")
        
        print(f"\n📅 Upcoming High-Impact Events:")
        upcoming = [e for e in report['upcoming_events'] if e['impact_level'] in ['high', 'black_swan']]
        for event in upcoming[:5]:
            print(f"   - {event['date'][:10]}: {event['title']}")
        
        print(f"\n🎯 Market Reaction Predictions:")
        for reaction in report['market_reactions'][:3]:
            direction_emoji = "📈" if reaction['direction'] == 'bullish' else "📉"
            print(f"   - {reaction['asset_class'].upper()}: {reaction['volatility_spike']:.1f}% vol spike {direction_emoji}")
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/workspace/code/demo_impact_assessment_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Full report saved to: {filename}")
        
    else:
        print(f"❌ Assessment failed: {report['error']}")
    
    print("\n✅ Comprehensive Demo Complete!")

if __name__ == "__main__":
    # Run individual tests
    print("Choose test to run:")
    print("1. Economic Calendar Integration")
    print("2. News Classification")
    print("3. Market Reaction Prediction")
    print("4. Event Clustering")
    print("5. Risk Assessment")
    print("6. Allocation Recommendations")
    print("7. Real-time Alerts")
    print("8. Full System Demo")
    print("9. All Tests")
    
    # For demo purposes, run full demo
    asyncio.run(run_comprehensive_demo())