"""
Portfolio Optimizer Demo
========================

Bu fayl Portfolio Optimizer tizimini qanday ishlatishni ko'rsatadi.
"""

from portfolio_optimizer import PortfolioOptimizer, AssetAllocator, create_sample_assets_data
import numpy as np
import pandas as pd

def demo_basic_optimization():
    """Asosiy optimizatsiya demo."""
    print("=== ASOSIY PORTFOLIO OPTIMIZATSIYA ===")
    
    # Optimizatorni ishga tushirish
    optimizer = PortfolioOptimizer(risk_free_rate=0.03)
    
    # Namuna ma'lumotlar
    assets_data = create_sample_assets_data()
    
    # Quantum optimization
    print("\n1. Quantum-Inspired Optimization:")
    result_quantum = optimizer.optimize_portfolio(assets_data, method='quantum')
    
    report_quantum = optimizer.generate_portfolio_report(result_quantum)
    print(report_quantum)
    
    # Modern Portfolio Theory - Maximum Sharpe
    print("\n2. Maximum Sharpe Ratio Optimization:")
    result_sharpe = optimizer.optimize_portfolio(assets_data, method='mpt_max_sharpe')
    print(f"Kutilayotgan daromad: {result_sharpe['metrics']['expected_return']:.2%}")
    print(f"Volatilite: {result_sharpe['metrics']['volatility']:.2%}")
    print(f"Sharpe ratio: {result_sharpe['metrics']['sharpe_ratio']:.2f}")

def demo_multi_asset_allocation():
    """Ko'p aktivli allocation demo."""
    print("\n=== KO'P AKTIVLI ALLOCATION ===")
    
    allocator = AssetAllocator()
    assets_data = create_sample_assets_data()
    
    # Ko'p aktivli portfolio optimizatsiya
    multi_asset_portfolio = allocator.optimize_multi_asset_portfolio(assets_data)
    
    print("\nAsset class bo'yicha allocation:")
    for asset, weight in multi_asset_portfolio.items():
        if weight > 0.01:  # Faqat sezilarli allocation
            print(f"{asset}: {weight:.2%}")

def demo_risk_analysis():
    """Risk tahlili demo."""
    print("\n=== RISK TAHLILI ===")
    
    from portfolio_optimizer import RiskMetrics
    
    # Risk metrics kalkulyatori
    risk_calc = RiskMetrics(confidence_level=0.95)
    
    # Simulatsiya qilingan returns (real hayotda historical data ishlatiladi)
    np.random.seed(42)
    returns = np.random.normal(0.08, 0.15, 252)  # Bir yillik daily returns
    
    print("\nRisk metrikalar:")
    print(f"Value at Risk (95%): {risk_calc.calculate_var(returns):.2%}")
    print(f"Conditional VaR (95%): {risk_calc.calculate_cvar(returns):.2%}")
    print(f"Maximum Drawdown: {risk_calc.calculate_max_drawdown(pd.Series(returns)):.2%}")
    print(f"Sharpe Ratio: {risk_calc.calculate_sharpe_ratio(pd.Series(returns)):.2f}")
    print(f"Sortino Ratio: {risk_calc.calculate_sortino_ratio(pd.Series(returns)):.2f}")

def demo_constraints():
    """Constraintlar bilan optimizatsiya demo."""
    print("\n=== CONSTRAINTLAR BILAN OPTIMIZATSIYA ===")
    
    optimizer = PortfolioOptimizer(risk_free_rate=0.03)
    
    # Max constraintlar
    custom_constraints = {
        'max_weight': 0.30,  # Maksimal bitta pozitsiya 30%
        'min_weight': 0.05,  # Minimal pozitsiya 5%
        'target_return': 0.10,  # Target return 10%
        'sector_limits': {
            'technology': 0.25,  # Tech sektor maksimal 25%
            'healthcare': 0.20,  # Healthcare maksimal 20%
        }
    }
    
    assets_data = create_sample_assets_data()
    
    result = optimizer.optimize_portfolio(
        assets_data, 
        method='quantum',
        constraints=custom_constraints
    )
    
    print("\nConstrain olgan portfolio:")
    weights = result['weights']
    for i, weight in enumerate(weights):
        if weight > 0.01:
            asset_name = list(assets_data.keys())[i]
            print(f"{asset_name}: {weight:.2%}")
    
    print(f"\nKutilayotgan daromad: {result['metrics']['expected_return']:.2%}")
    print(f"Volatilite: {result['metrics']['volatility']:.2%}")

def demo_backtest():
    """Backtest demo."""
    print("\n=== BACKTEST DEMO ===")
    
    optimizer = PortfolioOptimizer(risk_free_rate=0.03)
    assets_data = create_sample_assets_data()
    
    # Optimizatsiya
    result = optimizer.optimize_portfolio(assets_data, method='quantum')
    weights = result['weights']
    
    # Tarixiy ma'lumotlar simulyatsiyasi (real hayotda API dan olinadi)
    np.random.seed(42)
    n_days = 1000
    n_assets = len(assets_data)
    
    # Correlation matrix yaratish
    correlation_matrix = np.eye(n_assets) * 0.3 + 0.7 * np.ones((n_assets, n_assets))
    np.fill_diagonal(correlation_matrix, 1)
    
    # Random returns yaratish
    returns_data = np.random.multivariate_normal(
        mean=np.zeros(n_assets),
        cov=correlation_matrix * 0.01,  # 1% daily volatility
        size=n_days
    )
    
    # Backtest
    backtest_results = optimizer.backtest_portfolio(
        pd.DataFrame(returns_data), weights
    )
    
    print("\nBacktest natijalari:")
    for metric, value in backtest_results.items():
        if 'return' in metric:
            print(f"{metric}: {value:.2%}")
        else:
            print(f"{metric}: {value:.3f}")

def main():
    """Asosiy demo funksiya."""
    print("Portfolio Optimizer Demo")
    print("=" * 50)
    
    # Barcha demo funksiyalarni ishga tushirish
    demo_basic_optimization()
    demo_multi_asset_allocation()
    demo_risk_analysis()
    demo_constraints()
    demo_backtest()
    
    print("\n=== DEMO TUGALLANDI ===")
    print("\nQo'llanma:")
    print("1. Portfolio Optimizer turli optimizatsiya usullarini qo'llab-quvvatlaydi")
    print("2. Quantum-inspired algorithms samaraliroq natija berishi mumkin")
    print("3. Constraintlar yordamida risk va allocation nazorat qilish mumkin")
    print("4. Backtest yordamida historical performance ko'rish mumkin")

if __name__ == "__main__":
    main()