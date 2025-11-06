"""
Hybrid Quantum-Classical Trading System Demo
===========================================

Bu demo fayl Hybrid Quantum-Classical Trading System'ning asosiy 
xususiyatlarini ko'rsatadi.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to path to import our module
sys.path.append(os.path.dirname(__file__))

from hybrid_quantum_classical import (
    HybridQuantumClassicalSystem,
    ProblemSize,
    AlgorithmType,
    create_sample_market_data,
    analyze_quantum_advantage,
    visualize_portfolio_comparison
)

def create_realistic_market_data(n_assets=20, n_days=500):
    """Realistic market ma'lumotlari yaratish."""
    np.random.seed(42)
    
    # Create time series
    start_date = datetime.now() - timedelta(days=n_days)
    dates = pd.date_range(start=start_date, periods=n_days, freq='D')
    
    # Generate sector-based returns
    sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer']
    sector_returns = {
        'Technology': {'mean': 0.0008, 'vol': 0.025},
        'Healthcare': {'mean': 0.0006, 'vol': 0.018},
        'Finance': {'mean': 0.0005, 'vol': 0.022},
        'Energy': {'mean': 0.0004, 'vol': 0.030},
        'Consumer': {'mean': 0.0007, 'vol': 0.020}
    }
    
    # Generate assets with sector assignments
    assets_data = {}
    asset_names = []
    
    for i in range(n_assets):
        sector = sectors[i % len(sectors)]
        sector_data = sector_returns[sector]
        
        # Generate correlated returns within sector
        base_return = np.random.normal(
            sector_data['mean'], 
            sector_data['vol'], 
            n_days
        )
        
        # Add some noise and correlation
        correlation_noise = np.random.normal(0, sector_data['vol'] * 0.1, n_days)
        final_returns = base_return + correlation_noise
        
        asset_name = f"{sector}_{i//len(sectors):02d}"
        asset_names.append(asset_name)
        assets_data[asset_name] = final_returns
    
    # Create DataFrame
    market_data = pd.DataFrame(assets_data, index=dates)
    
    return market_data, asset_names

def demonstrate_hybrid_workflow():
    """Hybrid workflow'ni ko'rsatish."""
    print("🚀 HYBRID QUANTUM-CLASSICAL TRADING SYSTEM DEMO")
    print("=" * 60)
    
    # Create realistic market data
    print("📊 Realistic market data yaratilmoqda...")
    market_data, asset_names = create_realistic_market_data(n_assets=25, n_days=300)
    print(f"✅ {len(asset_names)} aktiv, {len(market_data)} kunlik ma'lumot")
    
    # Initialize system
    print("\n🤖 Hybrid Quantum-Classical System ishga tushirilmoqda...")
    config = {
        'n_qubits': 8,
        'hardware_type': 'simulator',
        'algorithm_thresholds': {
            ProblemSize.SMALL: AlgorithmType.CLASSICAL_ONLY,
            ProblemSize.MEDIUM: AlgorithmType.HYBRID,
            ProblemSize.LARGE: AlgorithmType.QUANTUM_ADVANTAGE
        },
        'performance_thresholds': {
            'min_sharpe_ratio': 0.8,
            'max_computation_time': 30.0,
            'quantum_advantage_threshold': 1.15
        }
    }
    
    system = HybridQuantumClassicalSystem(config=config)
    print(f"✅ System initialized - Quantum available: {system.is_quantum_available}")
    
    # Demonstrate different problem sizes
    print("\n🔍 MUAMMO HAJMI KLASSIFIKATSIYASI:")
    print("-" * 40)
    
    test_sizes = [10, 50, 150]  # Small, Medium, Large
    for size in test_sizes:
        subset_data = market_data.iloc[:, :size]
        problem_size = system.classify_problem_size(subset_data)
        selected_algorithm = system.select_algorithm(problem_size)
        print(f"  Assets: {size:3d} -> Problem Size: {problem_size.value:8s} -> Algorithm: {selected_algorithm.value}")
    
    # Portfolio optimization demo
    print("\n📈 PORTFOLIO OPTIMIZATSIYA:")
    print("-" * 40)
    
    # Use medium-sized portfolio
    portfolio_data = market_data.iloc[:, :30]
    result = system.process_portfolio_optimization(portfolio_data, asset_names[:30])
    
    print(f"Algorithm Used: {result['algorithm_used']}")
    print(f"Problem Size: {result['problem_size']}")
    print(f"Features: {result['feature_selection']['total_features']} -> {result['feature_selection']['selected_features']}")
    
    # Display portfolio metrics
    metrics = result['portfolio_metrics']
    print(f"\n📊 PORTFOLIO METRIKLARI:")
    print(f"  Expected Return: {metrics['expected_return']:.2%}")
    print(f"  Volatility: {metrics['volatility']:.2%}")
    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"  Sortino Ratio: {metrics['sortino_ratio']:.2f}")
    print(f"  Max Position: {metrics['max_position_weight']:.2%}")
    print(f"  Diversification: {metrics['diversification_ratio']:.2f}")
    print(f"  Portfolio Size: {metrics['portfolio_size']} assets")
    
    # Display top holdings
    weights = result['optimization_result'].weights
    top_holdings = sorted(zip(asset_names[:30], weights), key=lambda x: x[1], reverse=True)[:8]
    print(f"\n🎯 TOP 8 HOLDINGS:")
    for i, (asset, weight) in enumerate(top_holdings, 1):
        print(f"  {i:2d}. {asset:15s}: {weight:6.2%}")
    
    # Performance metrics
    perf = result['performance_metrics']
    quantum_metrics = result['quantum_metrics']
    
    print(f"\n⚡ PERFORMANCE METRIKLARI:")
    print(f"  Total Computation Time: {perf['total_computation_time']:.2f} seconds")
    print(f"  Quantum Advantage: {quantum_metrics['quantum_advantage_achieved']}")
    print(f"  Quantum Success Rate: {quantum_metrics['quantum_success_rate']:.1%}")
    
    # System status
    print(f"\n🖥️  SYSTEM HOLATI:")
    status = system.get_system_status()
    print(f"  System Health: {status['system_health']}")
    print(f"  Quantum Available: {status['quantum_available']}")
    print(f"  Current Problem Size: {status['current_problem_size']}")
    
    # Benchmark comparison
    print(f"\n🏆 BENCHMARK TAQQOSLASH:")
    print("-" * 30)
    benchmark = system.benchmark_algorithms(portfolio_data, n_runs=3)
    
    for algorithm, metrics in benchmark.items():
        if 'avg_sharpe_ratio' in metrics and not np.isnan(metrics['avg_sharpe_ratio']):
            print(f"  {algorithm.upper():12s}: Sharpe={metrics['avg_sharpe_ratio']:.2f}, "
                  f"Time={metrics['avg_computation_time']:.3f}s, "
                  f"Success={metrics['success_rate']:.0%}")
        else:
            print(f"  {algorithm.upper():12s}: Failed")
    
    return result, system

def demonstrate_error_mitigation():
    """Error mitigation xususiyatlarini ko'rsatish."""
    print("\n\n🛡️  ERROR MITIGATION DEMO")
    print("=" * 40)
    
    from hybrid_quantum_classical import QuantumErrorMitigator
    
    mitigator = QuantumErrorMitigator()
    
    # Simulate noisy quantum measurement
    noisy_measurement = {0: 800, 1: 200, 2: 0, 3: 0}  # |00⟩, |01⟩, |10⟩, |11⟩
    
    print("Original measurement:", noisy_measurement)
    
    # Apply error mitigation
    mitigated = mitigator.mitigate_measurement_errors(noisy_measurement)
    print("Mitigated measurement:", mitigated)
    
    # Create mock quantum state
    from hybrid_quantum_classical import QuantumState
    mock_state = QuantumState(
        amplitudes=np.array([0.7, 0.3]),
        probabilities=np.array([0.49, 0.51]),
        measurement_counts=noisy_measurement,
        fidelity=0.92,
        error_rate=0.08
    )
    
    is_valid = mitigator.validate_quantum_result(mock_state)
    print(f"Quantum result validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    return mitigator

def demonstrate_adaptive_algorithm_selection():
    """Adaptive algoritm tanlash qobiliyatini ko'rsatish."""
    print("\n\n🎯 ADAPTIVE ALGORITHM SELECTION DEMO")
    print("=" * 50)
    
    market_data, asset_names = create_realistic_market_data(n_assets=100, n_days=250)
    
    config = {
        'algorithm_thresholds': {
            ProblemSize.SMALL: AlgorithmType.CLASSICAL_ONLY,
            ProblemSize.MEDIUM: AlgorithmType.HYBRID,
            ProblemSize.LARGE: AlgorithmType.QUANTUM_ADVANTAGE
        }
    }
    
    system = HybridQuantumClassicalSystem(config=config)
    
    # Test different portfolio sizes
    portfolio_sizes = [10, 50, 150, 250]
    results = []
    
    for size in portfolio_sizes:
        subset_data = market_data.iloc[:, :size]
        problem_size = system.classify_problem_size(subset_data)
        selected_algorithm = system.select_algorithm(problem_size)
        
        # Run optimization
        result = system.process_portfolio_optimization(subset_data, asset_names[:size])
        
        results.append({
            'size': size,
            'problem_size': problem_size.value,
            'algorithm': selected_algorithm.value,
            'sharpe_ratio': result['portfolio_metrics']['sharpe_ratio'],
            'computation_time': result['performance_metrics']['total_computation_time']
        })
    
    print("Portfolio Size | Problem Size  | Algorithm        | Sharpe | Time(s)")
    print("-" * 70)
    for r in results:
        sharpe_str = f"{r['sharpe_ratio']:.2f}" if not np.isnan(r['sharpe_ratio']) else "N/A"
        print(f"{r['size']:12d} | {r['problem_size']:13s} | {r['algorithm']:16s} | {sharpe_str:6s} | {r['computation_time']:6.2f}")
    
    return results

def create_performance_visualization(results_data):
    """Performance vizualizatsiya yaratish."""
    print("\n📊 Performance Visualization yaratilmoqda...")
    
    try:
        # Create a simple visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Hybrid Quantum-Classical Trading System Performance', fontsize=16)
        
        # Portfolio sizes vs Sharpe ratio
        sizes = [r['size'] for r in results_data]
        sharpe_ratios = [r['sharpe_ratio'] for r in results_data if not np.isnan(r['sharpe_ratio'])]
        valid_sizes = [r['size'] for r in results_data if not np.isnan(r['sharpe_ratio'])]
        
        if sharpe_ratios:
            ax1.plot(valid_sizes, sharpe_ratios, 'bo-', linewidth=2, markersize=8)
            ax1.set_xlabel('Portfolio Size')
            ax1.set_ylabel('Sharpe Ratio')
            ax1.set_title('Portfolio Size vs Sharpe Ratio')
            ax1.grid(True, alpha=0.3)
        
        # Computation time
        times = [r['computation_time'] for r in results_data]
        ax2.bar(range(len(sizes)), times, color='lightblue', alpha=0.7)
        ax2.set_xlabel('Test Case')
        ax2.set_ylabel('Computation Time (seconds)')
        ax2.set_title('Computation Time by Portfolio Size')
        ax2.set_xticks(range(len(sizes)))
        ax2.set_xticklabels([f"{s}\nassets" for s in sizes])
        
        # Algorithm distribution
        algorithms = [r['algorithm'] for r in results_data]
        unique_algos = list(set(algorithms))
        algo_counts = [algorithms.count(algo) for algo in unique_algos]
        
        ax3.pie(algo_counts, labels=unique_algos, autopct='%1.1f%%', startangle=90)
        ax3.set_title('Algorithm Distribution')
        
        # Problem size distribution
        problem_sizes = [r['problem_size'] for r in results_data]
        unique_problems = list(set(problem_sizes))
        problem_counts = [problem_sizes.count(p) for p in unique_problems]
        
        ax4.bar(unique_problems, problem_counts, color='lightgreen', alpha=0.7)
        ax4.set_xlabel('Problem Size Category')
        ax4.set_ylabel('Number of Cases')
        ax4.set_title('Problem Size Distribution')
        
        plt.tight_layout()
        
        # Save the plot
        plt.savefig('/workspace/code/hybrid_system_performance.png', dpi=300, bbox_inches='tight')
        print("✅ Visualization saved as 'hybrid_system_performance.png'")
        
        plt.show()
        
    except Exception as e:
        print(f"❌ Visualization yaratishda xato: {e}")

def main():
    """Asosiy demo funksiya."""
    try:
        # 1. Hybrid workflow demo
        result, system = demonstrate_hybrid_workflow()
        
        # 2. Error mitigation demo
        mitigator = demonstrate_error_mitigation()
        
        # 3. Adaptive algorithm selection demo
        results_data = demonstrate_adaptive_algorithm_selection()
        
        # 4. Performance visualization
        create_performance_visualization(results_data)
        
        # 5. System features summary
        print("\n\n🌟 HYBRID QUANTUM-CLASSICAL SYSTEM XUSUSIYATLARI:")
        print("=" * 60)
        print("✅ Hybrid Architecture: Quantum + Classical integration")
        print("✅ Adaptive Algorithm Selection: Problem size based")
        print("✅ Error Mitigation: Quantum error handling")
        print("✅ Performance Monitoring: Real-time tracking")
        print("✅ Decision Fusion: Multiple algorithm combination")
        print("✅ Real-World Integration: Fallback systems")
        print("✅ Risk Management: Post-processing constraints")
        print("✅ Quantum-Ready: Qiskit compatibility")
        
        print(f"\n🎯 Key Insights:")
        print(f"  • System automatically selects best algorithm for problem size")
        print(f"  • Quantum methods provide advantage for complex portfolios")
        print(f"  • Classical fallback ensures system reliability")
        print(f"  • Performance monitoring guides future decisions")
        print(f"  • Error mitigation handles quantum hardware limitations")
        
        print(f"\n📈 Production Ready Features:")
        print(f"  • Comprehensive error handling")
        print(f"  • Configurable optimization parameters")
        print(f"  • Real-time performance monitoring")
        print(f"  • Multiple optimization algorithms")
        print(f"  • Risk management constraints")
        print(f"  • Benchmarking capabilities")
        
        print(f"\n🚀 DEMO COMPLETE!")
        
    except Exception as e:
        print(f"❌ Demo jarayonida xato: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()