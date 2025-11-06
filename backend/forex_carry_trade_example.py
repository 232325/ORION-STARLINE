"""
Forex Carry Trade va Metal Price Correlation Tizimi - Foydalanish Misoli
======================================================================

Bu fayl asosiy tizimni qanday ishlatishni ko'rsatadi.
"""

from forex_carry_trade import (
    ForexCarryTradeAnalyzer,
    MetalPriceCorrelationAnalyzer, 
    DynamicCorrelationAnalyzer,
    PredictiveCorrelationModels,
    MultifactorModel,
    ForexCarryTradeSystem,
    generate_sample_data
)

def example_usage():
    """
    Tizimdan foydalanish misoli
    """
    print("FOREX CARRY TRADE TAHLIL MISOLI")
    print("=" * 40)
    
    # 1. Sample ma'lumotlarni yaratish
    print("1. Sample ma'lumotlar yaratilmoqda...")
    sample_data = generate_sample_data(500)  # 500 kunlik ma'lumot
    
    # 2. Carry Trade Analyzer misoli
    print("\n2. Carry Trade Analyzer:")
    carry_analyzer = ForexCarryTradeAnalyzer()
    
    # Foiz stavkalarini yuklash
    carry_analyzer.load_interest_rates(sample_data['interest_rates'])
    
    # Valyuta juftliklari tahlili
    pairs = ['USD/JPY', 'EUR/USD', 'GBP/USD', 'USD/CHF']
    opportunities = carry_analyzer.identify_opportunities(pairs)
    
    print(f"Topilgan imkoniyatlar: {len(opportunities)}")
    for opp in opportunities[:3]:
        print(f"  {opp['pair']}: Return {opp['annual_return_pct']:.2f}%, Sharpe {opp['sharpe_ratio']:.3f}")
    
    # 3. Metal Price Correlation Analyzer misoli
    print("\n3. Metal Price Correlation Analyzer:")
    metal_analyzer = MetalPriceCorrelationAnalyzer()
    
    # Metal narxlarini yuklash
    metal_analyzer.load_metal_prices(sample_data['metal_prices'])
    metal_analyzer.load_economic_data(sample_data['economic_data'])
    
    # Korrelatsiya tahlili
    cross_corr = metal_analyzer.cross_metal_correlation(period=120)
    print(f"Korrelatsiya matritsasi hajmi: {cross_corr.shape}")
    
    # Dollar kuchi korrelatsiyasi
    dollar_corr = metal_analyzer.dollar_strength_correlation()
    print("Dollar bilan korrelatsiya:")
    for metal, corr in dollar_corr.items():
        print(f"  {metal}: {corr:.3f}")
    
    # 4. Dynamic Correlation Analyzer misoli
    print("\n4. Dynamic Correlation Analyzer:")
    dynamic_analyzer = DynamicCorrelationAnalyzer()
    
    # Rolik korrelatsiya tahlili
    rolling_corr = dynamic_analyzer.rolling_correlation_analysis(
        sample_data['metal_prices'].tail(300)
    )
    print(f"Rolik korrelatsiya oyna hajmlari: {list(rolling_corr.keys())}")
    
    # 5. Predictive Models misoli
    print("\n5. Predictive Models:")
    predictive = PredictiveCorrelationModels()
    
    # Korrelatsiya bashorati
    forecast_result = predictive.correlation_forecasting(
        sample_data['metal_prices'].tail(400), 
        method='rf'
    )
    
    if 'error' not in forecast_result:
        print(f"Bashorat model R²: {forecast_result['test_r2']:.3f}")
    
    # Farqlanish aniqlash
    divergences = predictive.divergence_detection(
        sample_data['metal_prices'].tail(200)
    )
    print(f"Topilgan farqlanishlar: {len(divergences)}")
    
    # 6. Multi-factor Model misoli
    print("\n6. Multi-factor Model:")
    multifactor = MultifactorModel()
    
    # Turli omillarni qo'shish
    multifactor.add_economic_factors(sample_data['economic_data'])
    multifactor.add_supply_demand_factors(sample_data['supply_demand_data'])
    multifactor.add_market_factors(sample_data['market_data'])
    multifactor.add_sentiment_factors(sample_data['sentiment_data'])
    multifactor.add_technical_factors(sample_data['technical_data'])
    
    # Faktor tahlili
    factor_result = multifactor.factor_analysis(method='pca')
    
    if 'error' not in factor_result:
        print(f"Asosiy komponentlar soni: {factor_result['loadings'].shape[1]}")
        print(f"Birinchi komponentning explained variance: {factor_result['explained_variance'][0]:.3f}")
    
    # 7. To'liq tizim misoli
    print("\n7. To'liq Tizim:")
    system = ForexCarryTradeSystem()
    
    # Tizim konfiguratsiyasi
    config = {
        'metal_prices': sample_data['metal_prices'],
        'economic_data': sample_data['economic_data'],
        'interest_rates': sample_data['interest_rates'],
        'supply_demand_data': sample_data['supply_demand_data'],
        'market_data': sample_data['market_data'],
        'sentiment_data': sample_data['sentiment_data'],
        'technical_data': sample_data['technical_data']
    }
    
    # Tizimni ishga tushirish
    system.initialize_system(config)
    
    # To'liq tahlil
    results = system.run_comprehensive_analysis()
    
    # Treyding signallari
    signals = system.generate_trading_signals(results)
    
    # Dashboard ma'lumotlari
    dashboard = system.create_dashboard_data(results)
    
    print("Barcha tahlillar muvaffaqiyatli tugallandi!")
    print(f"Korrelatsiya rejimlari: {len(results.get('dynamic_correlations', {}).get('regime_detection', {}).unique())}")
    
    return {
        'carry_analyzer': carry_analyzer,
        'metal_analyzer': metal_analyzer,
        'dynamic_analyzer': dynamic_analyzer,
        'predictive': predictive,
        'multifactor': multifactor,
        'system': system,
        'results': results,
        'signals': signals,
        'dashboard': dashboard
    }


def custom_data_example():
    """
    O'z ma'lumotlaringiz bilan ishlash misoli
    """
    print("\n" + "="*50)
    print("O'Z MA'LUMOTLAR BILAN ISHLASH MISOLI")
    print("="*50)
    
    # Create your own data structure
    import pandas as pd
    import numpy as np
    
    # Sample metal prices (o'zingizning ma'lumotlaringizni kiriting)
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    your_metal_prices = pd.DataFrame({
        'GOLD': np.random.randn(len(dates)).cumsum() * 10 + 1800,
        'SILVER': np.random.randn(len(dates)).cumsum() * 0.5 + 25,
        'COPPER': np.random.randn(len(dates)).cumsum() * 0.1 + 4.0
    }, index=dates)
    
    # Your interest rates (o'zingizning foiz stavkalaringiz)
    your_interest_rates = {
        'USD': {'rate': 5.25, 'last_update': '2024-01-15'},
        'EUR': {'rate': 4.00, 'last_update': '2024-01-15'},
        'JPY': {'rate': -0.10, 'last_update': '2024-01-15'},
        'GBP': {'rate': 5.25, 'last_update': '2024-01-15'}
    }
    
    # Your economic data
    your_economic_data = pd.DataFrame({
        'USD_INDEX': np.random.randn(len(dates)).cumsum() * 2 + 100,
        'GDP_GROWTH': np.random.normal(2.0, 0.5, len(dates)),
        'INFLATION': np.random.normal(2.5, 0.3, len(dates))
    }, index=dates)
    
    # Create analyzer with your data
    analyzer = ForexCarryTradeSystem()
    
    config = {
        'metal_prices': your_metal_prices,
        'economic_data': your_economic_data,
        'interest_rates': your_interest_rates
    }
    
    analyzer.initialize_system(config)
    
    # Run analysis
    results = analyzer.run_comprehensive_analysis()
    
    print("O'z ma'lumotlaringiz bilan tahlil tugallandi!")
    
    return results


if __name__ == "__main__":
    # Asosiy misol
    results = example_usage()
    
    # O'z ma'lumotlar bilan ishlash
    custom_results = custom_data_example()
    
    print("\n" + "="*50)
    print("BARCHA MISOLLAR MUVAFFAQIYATLI TUGALLANDI!")
    print("="*50)