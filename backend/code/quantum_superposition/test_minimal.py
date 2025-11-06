"""
Minimal Quantum Portfolio Test
"""

print("🌟 Minimal Quantum Portfolio Test")
print("=" * 35)

try:
    # Import test
    from quantum_superposition_theory import QuantumState, QuantumSuperpositionManager
    print("✅ Quantum superposition theory import successful")
    
    from superposition_portfolio_models import SuperpositionPortfolio
    print("✅ Superposition portfolio models import successful")
    
    from diversification_quantum_models import QuantumDiversification
    print("✅ Diversification models import successful")
    
    from quantum_algorithms import QuantumOptimizer
    print("✅ Quantum algorithms import successful")
    
    from portfolio_management import DynamicPortfolioManager
    print("✅ Portfolio management import successful")
    
    # Simple test
    assets = {'AAPL': 0.25, 'GOOGL': 0.20, 'MSFT': 0.15, 'TSLA': 0.25, 'AMZN': 0.15}
    
    # Test quantum superposition
    manager = QuantumSuperpositionManager(len(assets))
    manager.create_superposition(assets)
    coherence = manager.get_coherence_measure()
    print(f"• Coherence measure: {coherence:.4f}")
    
    # Test portfolio
    portfolio = SuperpositionPortfolio(assets)
    print(f"• Portfolio assets: {len(portfolio.assets)}")
    
    # Test diversification
    diversifier = QuantumDiversification(assets)
    metrics = diversifier.diversification_metrics
    print(f"• Diversification metrics: {len(metrics)} metrics")
    
    print("\n🎉 Barcha testlar muvaffaqiyatli!")
    print("Quantum Superposition Portfolio tizimi tayyor!")
    
except Exception as e:
    print(f"❌ Xato: {e}")
    import traceback
    traceback.print_exc()