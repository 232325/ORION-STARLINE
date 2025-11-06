"""
Quantum Superposition Portfolio - Tez Demo
Quantum algoritmlarni tez test qilish uchun
"""

import numpy as np
from quantum_superposition_theory import QuantumSuperpositionManager, QuantumState
from superposition_portfolio_models import SuperpositionPortfolio, create_sample_superposition_portfolio
from diversification_quantum_models import QuantumDiversification, demonstrate_diversification_models
from portfolio_management import demonstrate_portfolio_management

def quick_quantum_demo():
    """Tez quantum portfolio demo"""
    print("🌟 QUANTUM PORTFOLIO TEZ DEMO")
    print("=" * 40)
    
    # 1. Superposition demo
    print("\n📊 1. Superposition Test:")
    assets = {
        'AAPL': 0.25, 'GOOGL': 0.20, 'MSFT': 0.15, 'TSLA': 0.25, 'AMZN': 0.15
    }
    
    manager = QuantumSuperpositionManager(len(assets))
    manager.create_superposition(assets)
    
    print(f"• Assets: {len(assets)}")
    print(f"• Coherence: {manager.get_coherence_measure():.4f}")
    measurements = manager.measure_portfolio()
    print(f"• Measurements: {len(measurements)} states")
    
    # 2. Portfolio models demo
    print("\n🎯 2. Portfolio Models Test:")
    portfolio, multi_dim, coherent_trading = create_sample_superposition_portfolio()
    
    print(f"• Portfolio assets: {len(portfolio.assets)}")
    print(f"• Superposition states: {len(portfolio.superposition_weights)}")
    
    # 3. Diversification demo
    print("\n⚛️  3. Diversification Test:")
    diversifier = QuantumDiversification(assets)
    
    metrics = diversifier.diversification_metrics
    print(f"• Quantum entropy: {metrics.get('quantum_entropy', 0):.4f}")
    print(f"• Schmidt number: {metrics.get('schmidt_number', 1):.2f}")
    
    # 4. Portfolio management demo
    print("\n📈 4. Portfolio Management Test:")
    manager_dm, rebalancer, attributor = demonstrate_portfolio_management()
    
    print("✅ Barcha testlar muvaffaqiyatli tugallandi!")
    
    return {
        'superposition': manager,
        'portfolio': portfolio,
        'diversifier': diversifier,
        'manager': manager_dm
    }

if __name__ == "__main__":
    results = quick_quantum_demo()
    print(f"\n🎉 Demo muvaffaqiyatli yakunlandi!")
    print(f"Test qilingan komponentlar: {len(results)}")