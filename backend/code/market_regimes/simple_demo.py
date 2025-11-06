#!/usr/bin/env python3
"""
Simple Demo - Market Regime Detection System
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')

def generate_sample_market_data(n_days: int = 500, n_assets: int = 5) -> pd.DataFrame:
    """Generate realistic market data for demo"""
    
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=n_days)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Asset symbols
    assets = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'][:n_assets]
    
    # Generate price data with regime changes
    returns_data = []
    prices_data = []
    
    current_prices = np.array([150.0 + i * 50.0 for i in range(n_assets)], dtype=float)
    
    for i, date in enumerate(dates):
        # Define regime periods
        if i < n_days * 0.3:  # Normal market
            drift, volatility = 0.0005, 0.015
        elif i < n_days * 0.5:  # Trending bull market
            drift, volatility = 0.001, 0.020
        elif i < n_days * 0.7:  # High volatility
            drift, volatility = -0.0002, 0.035
        elif i < n_days * 0.85:  # Range-bound
            drift, volatility = 0, 0.008
        else:  # Crisis period
            drift, volatility = -0.002, 0.045
            
        # Generate returns with regime characteristics
        daily_returns = np.random.normal(drift, volatility, n_assets)
        
        # Add regime patterns
        if i > n_days * 0.3 and i < n_days * 0.5:  # Trending
            daily_returns += np.linspace(0, 0.002, n_assets)
        elif i > n_days * 0.85:  # Crisis
            daily_returns *= 2
            daily_returns -= 0.01
            
        # Update prices
        current_prices *= (1 + daily_returns)
        
        returns_data.append(daily_returns)
        prices_data.append(current_prices.copy())
        
    # Create DataFrames
    returns_df = pd.DataFrame(returns_data, index=dates, columns=assets)
    prices_df = pd.DataFrame(prices_data, index=dates, columns=assets)
    
    return prices_df, returns_df

def detect_market_regimes_simple(prices: pd.Series) -> Dict:
    """Simple market regime detection"""
    
    returns = prices.pct_change().dropna()
    
    # Trend detection
    short_ma = prices.rolling(window=20).mean()
    long_ma = prices.rolling(window=50).mean()
    trend_signal = (short_ma > long_ma).fillna(False)
    
    # Volatility regime
    vol_20 = returns.rolling(window=20).std()
    vol_60 = returns.rolling(window=60).std()
    vol_ratio = vol_20 / vol_60
    high_vol = vol_ratio > 1.5
    low_vol = vol_ratio < 0.7
    
    # Crisis detection (severe drawdown)
    cumulative = (1 + returns).cumprod()
    drawdown = (cumulative / cumulative.cummax()) - 1
    crisis = drawdown < -0.15
    
    # Combine signals
    regimes = {
        'trend': trend_signal,
        'high_volatility': high_vol,
        'low_volatility': low_vol,
        'crisis': crisis,
        'drawdown': drawdown
    }
    
    return regimes

def analyze_correlations_simple(returns: pd.DataFrame) -> Dict:
    """Simple correlation analysis"""
    
    # Rolling correlation
    rolling_corr = returns.rolling(window=60).corr()
    
    # Average correlation
    avg_correlations = {}
    for i, asset1 in enumerate(returns.columns):
        for j, asset2 in enumerate(returns.columns[i+1:], i+1):
            # Get correlation time series for this pair
            corr_series = []
            for date in rolling_corr.index:
                try:
                    if not pd.isna(rolling_corr.loc[date, (asset1, asset2)]):
                        corr_series.append(rolling_corr.loc[date, (asset1, asset2)])
                except:
                    continue
            
            if corr_series:
                avg_correlations[f"{asset1}_{asset2}"] = {
                    'mean': np.mean(corr_series),
                    'std': np.std(corr_series),
                    'min': np.min(corr_series),
                    'max': np.max(corr_series),
                    'latest': corr_series[-1] if corr_series else 0
                }
    
    return {
        'average_correlations': avg_correlations,
        'overall_avg_correlation': np.mean([v['mean'] for v in avg_correlations.values()]) if avg_correlations else 0
    }

def simple_strategy_performance(prices: pd.DataFrame, regimes: Dict) -> Dict:
    """Simple strategy performance analysis"""
    
    returns = prices.pct_change().dropna()
    
    # Trend following strategy
    trend_signals = regimes['trend'].reindex(returns.index, fill_value=False)
    trend_returns = returns[trend_signals.shift(1).fillna(False)]
    
    # Mean reversion strategy (opposite of trend)
    mr_signals = ~regimes['trend'].reindex(returns.index, fill_value=False)
    mr_returns = returns[mr_signals.shift(1).fillna(False)]
    
    # Performance metrics
    def calc_metrics(returns_series):
        if len(returns_series) == 0:
            return {'total_return': 0.0, 'volatility': 0.0, 'sharpe': 0.0, 'max_drawdown': 0.0}
        
        # Convert to proper types
        total_return_series = (1 + returns_series).prod() - 1
        total_return = float(total_return_series.iloc[0]) if hasattr(total_return_series, 'iloc') else float(total_return_series)
        
        vol_series = returns_series.std()
        volatility = float(vol_series.iloc[0] * np.sqrt(252)) if hasattr(vol_series, 'iloc') else float(vol_series * np.sqrt(252))
        
        mean_series = returns_series.mean()
        mean_return = float(mean_series.iloc[0]) if hasattr(mean_series, 'iloc') else float(mean_series)
        
        sharpe = (mean_return * 252) / volatility if volatility > 0 else 0.0
        
        # Max drawdown
        cumulative = (1 + returns_series).cumprod()
        peak = cumulative.expanding().max()
        drawdown = (cumulative - peak) / peak
        min_drawdown = drawdown.min()
        if hasattr(min_drawdown, 'iloc'):
            max_drawdown = float(min_drawdown.iloc[0])
        else:
            max_drawdown = float(min_drawdown)
        
        return {
            'total_return': total_return,
            'volatility': volatility,
            'sharpe': sharpe,
            'max_drawdown': max_drawdown
        }
    
    return {
        'trend_following': calc_metrics(trend_returns),
        'mean_reversion': calc_metrics(mr_returns),
        'buy_hold': calc_metrics(returns)
    }

def generate_simple_report(market_data: pd.DataFrame, regimes: Dict, 
                          correlation_results: Dict, strategy_results: Dict) -> str:
    """Generate simple analysis report"""
    
    report = []
    report.append("=" * 60)
    report.append("MARKET REGIME DETECTION VA CROSS-ASSET CORRELATION LEARNING")
    report.append("SIMPLE ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Data Period: {len(market_data)} days")
    report.append(f"Assets: {', '.join(market_data.columns)}")
    report.append("")
    
    # Market Overview
    report.append("1. MARKET OVERVIEW")
    report.append("-" * 30)
    
    returns = market_data.pct_change().dropna()
    total_return = (market_data.iloc[-1] / market_data.iloc[0] - 1).mean()
    volatility = returns.std().mean() * np.sqrt(252)
    
    report.append(f"Average Total Return: {total_return:.2%}")
    report.append(f"Average Volatility: {volatility:.2%}")
    report.append("")
    
    # Regime Analysis
    report.append("2. REGIME ANALYSIS")
    report.append("-" * 30)
    
    # Count regime periods
    trend_periods = regimes['trend'].sum()
    high_vol_periods = regimes['high_volatility'].sum()
    low_vol_periods = regimes['low_volatility'].sum()
    crisis_periods = regimes['crisis'].sum()
    
    total_periods = len(regimes['trend'])
    
    report.append(f"Trending periods: {trend_periods} ({trend_periods/total_periods:.1%})")
    report.append(f"High volatility periods: {high_vol_periods} ({high_vol_periods/total_periods:.1%})")
    report.append(f"Low volatility periods: {low_vol_periods} ({low_vol_periods/total_periods:.1%})")
    report.append(f"Crisis periods: {crisis_periods} ({crisis_periods/total_periods:.1%})")
    
    # Max drawdown
    max_drawdown = regimes['drawdown'].min()
    report.append(f"Maximum Drawdown: {max_drawdown:.2%}")
    report.append("")
    
    # Correlation Analysis
    report.append("3. CROSS-ASSET CORRELATION ANALYSIS")
    report.append("-" * 30)
    
    avg_corr = correlation_results['overall_avg_correlation']
    report.append(f"Average Cross-Asset Correlation: {avg_corr:.3f}")
    
    if correlation_results['average_correlations']:
        report.append("\\nTop Correlations:")
        top_corrs = sorted(correlation_results['average_correlations'].items(), 
                          key=lambda x: abs(x[1]['mean']), reverse=True)[:3]
        
        for pair, stats in top_corrs:
            report.append(f"  {pair}: {stats['mean']:.3f} (range: {stats['min']:.3f} to {stats['max']:.3f})")
    
    report.append("")
    
    # Strategy Performance
    report.append("4. STRATEGY PERFORMANCE")
    report.append("-" * 30)
    
    for strategy, metrics in strategy_results.items():
        report.append(f"{strategy.replace('_', ' ').title()}:")
        report.append(f"  Total Return: {metrics['total_return']:.2%}")
        report.append(f"  Volatility: {metrics['volatility']:.2%}")
        report.append(f"  Sharpe Ratio: {metrics['sharpe']:.3f}")
        report.append(f"  Max Drawdown: {metrics['max_drawdown']:.2%}")
        report.append("")
    
    # Key Insights
    report.append("5. KEY INSIGHTS")
    report.append("-" * 30)
    
    # Market insights
    if crisis_periods > total_periods * 0.1:
        report.append("• Crisis periods detected - Consider defensive positioning")
    elif high_vol_periods > total_periods * 0.3:
        report.append("• High volatility environment - Reduce position sizes")
    elif trend_periods > total_periods * 0.4:
        report.append("• Trending market detected - Trend following may be effective")
    
    # Correlation insights
    if avg_corr > 0.7:
        report.append("• High correlation environment - Limited diversification benefits")
    elif avg_corr < 0.3:
        report.append("• Low correlation environment - Good diversification opportunities")
    
    # Strategy insights
    best_strategy = max(strategy_results.items(), key=lambda x: x[1]['sharpe'])
    report.append(f"• Best performing strategy: {best_strategy[0]} (Sharpe: {best_strategy[1]['sharpe']:.3f})")
    
    report.append("")
    report.append("=" * 60)
    
    return "\\n".join(report)

def create_simple_visualizations(market_data: pd.DataFrame, regimes: Dict):
    """Create simple visualizations"""
    
    try:
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Market Regime Analysis', fontsize=16)
        
        # Plot 1: Price evolution
        axes[0, 0].plot(market_data.index, market_data)
        axes[0, 0].set_title('Asset Prices Over Time')
        axes[0, 0].legend(market_data.columns, loc='upper left')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Regime timeline
        regime_colors = regimes['trend'].astype(int) + regimes['high_volatility'].astype(int) * 2
        # Set crisis regime to value 3
        regime_colors = regime_colors.copy().fillna(0)
        crisis_mask = regimes['crisis'].reindex(regime_colors.index, fill_value=False)
        regime_colors[crisis_mask] = 3
        regime_colors = regime_colors.astype(int)  # Ensure integers
        
        colors = ['blue', 'green', 'orange', 'red']
        regime_names = ['Normal', 'Trending', 'High Vol', 'Crisis']
        
        # Use y-axis position and color list
        y_pos = range(len(regime_colors))
        x_pos = regime_colors.index
        
        axes[0, 1].scatter(x_pos, y_pos, 
                          c=[colors[min(i, 3)] for i in regime_colors], alpha=0.6)
        axes[0, 1].set_title('Market Regime Timeline')
        axes[0, 1].set_ylabel('Regime')
        axes[0, 1].legend(regime_names, loc='upper left')
        
        # Plot 3: Volatility regime
        vol_20 = market_data.pct_change().rolling(20).std()
        axes[1, 0].plot(vol_20.index, vol_20)
        axes[1, 0].set_title('20-Day Rolling Volatility')
        axes[1, 0].set_ylabel('Volatility')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Drawdown
        cumulative_returns = (1 + market_data.pct_change()).cumprod()
        portfolio_value = cumulative_returns.mean(axis=1)
        peak = portfolio_value.expanding().max()
        drawdown = (portfolio_value - peak) / peak
        
        axes[1, 1].fill_between(drawdown.index, drawdown, 0, alpha=0.3, color='red')
        axes[1, 1].plot(drawdown.index, drawdown, color='darkred')
        axes[1, 1].set_title('Portfolio Drawdown')
        axes[1, 1].set_ylabel('Drawdown')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/workspace/code/market_regimes/simple_analysis.png', dpi=300, bbox_inches='tight')
        print("📊 Visualization saved to: /workspace/code/market_regimes/simple_analysis.png")
        plt.show()
        
    except ImportError:
        print("⚠️ Matplotlib not available for visualizations")

def main():
    """Main demo function"""
    
    print("=" * 60)
    print("MARKET REGIME DETECTION VA CROSS-ASSET CORRELATION LEARNING")
    print("SIMPLE SYSTEM DEMO")
    print("=" * 60)
    print("")
    
    # Step 1: Generate sample data
    print("1️⃣ Generating sample market data...")
    market_data, returns_data = generate_sample_market_data(n_days=500, n_assets=5)
    print(f"   ✓ Generated {len(market_data)} days of data for {len(market_data.columns)} assets")
    
    # Step 2: Regime detection
    print("\\n2️⃣ Detecting market regimes...")
    all_regimes = {}
    for asset in market_data.columns:
        regimes = detect_market_regimes_simple(market_data[asset])
        all_regimes[asset] = regimes
    
    # Combine regimes (majority vote)
    combined_regimes = {
        'trend': pd.DataFrame({asset: r['trend'] for asset, r in all_regimes.items()}).any(axis=1),
        'high_volatility': pd.DataFrame({asset: r['high_volatility'] for asset, r in all_regimes.items()}).any(axis=1),
        'low_volatility': pd.DataFrame({asset: r['low_volatility'] for asset, r in all_regimes.items()}).any(axis=1),
        'crisis': pd.DataFrame({asset: r['crisis'] for asset, r in all_regimes.items()}).any(axis=1),
        'drawdown': pd.DataFrame({asset: r['drawdown'] for asset, r in all_regimes.items()}).mean(axis=1)
    }
    
    print("   ✓ Market regimes detected across all assets")
    
    # Step 3: Correlation analysis
    print("\\n3️⃣ Analyzing cross-asset correlations...")
    correlation_results = analyze_correlations_simple(returns_data)
    print(f"   ✓ Analyzed correlations between {len(market_data.columns)} assets")
    
    # Step 4: Strategy analysis
    print("\\n4️⃣ Analyzing strategy performance...")
    strategy_results = simple_strategy_performance(market_data, combined_regimes)
    print("   ✓ Strategy performance analysis completed")
    
    # Step 5: Generate report
    print("\\n5️⃣ Generating analysis report...")
    report = generate_simple_report(market_data, combined_regimes, correlation_results, strategy_results)
    
    # Save report
    with open('/workspace/code/market_regimes/simple_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("   ✓ Report saved to: /workspace/code/market_regimes/simple_report.txt")
    
    # Step 6: Create visualizations
    print("\\n6️⃣ Creating visualizations...")
    create_simple_visualizations(market_data, combined_regimes)
    
    # Print summary
    print("\\n" + "=" * 60)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\\n📋 SUMMARY:")
    print(f"   • Market data: {len(market_data)} days, {len(market_data.columns)} assets")
    
    # Regime summary
    trend_pct = combined_regimes['trend'].mean()
    crisis_pct = combined_regimes['crisis'].mean()
    print(f"   • Trending periods: {trend_pct:.1%}")
    print(f"   • Crisis periods: {crisis_pct:.1%}")
    
    # Correlation summary
    avg_corr = correlation_results['overall_avg_correlation']
    print(f"   • Average correlation: {avg_corr:.3f}")
    
    # Strategy summary
    best_strategy = max(strategy_results.items(), key=lambda x: x[1]['sharpe'])
    print(f"   • Best strategy: {best_strategy[0]} (Sharpe: {best_strategy[1]['sharpe']:.3f})")
    
    print("\\n📁 OUTPUT FILES:")
    print("   • simple_report.txt - Comprehensive analysis report")
    print("   • simple_analysis.png - Visualization plots")
    
    print("\\n🔍 KEY INSIGHTS:")
    if crisis_pct > 0.1:
        print("   • Crisis conditions detected - Consider defensive strategies")
    if avg_corr > 0.7:
        print("   • High correlation environment - Limited diversification")
    if trend_pct > 0.4:
        print("   • Trending market - Trend following strategies may be effective")
    
    print("\\n" + "=" * 60)

if __name__ == "__main__":
    main()