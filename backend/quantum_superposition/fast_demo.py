"""
Fast Quantum Superposition Portfolio Demo
=========================================
Tezlashtirilgan demo - quantum portfolio algoritmlarini tez ko'rsatish
"""

import numpy as np
import time
from typing import Dict, Any
from quantum_superposition_theory import QuantumSuperpositionManager
from superposition_portfolio_models import SuperpositionPortfolio

def quick_quantum_demo():
    """Tez quantum portfolio demo"""
    print("🌟 TEZ QUANTUM PORTFOLIO DEMO")
    print("=" * 50)
    
    # 1. Portfolio yaratish
    assets = {'AAPL': 0.25, 'GOOGL': 0.20, 'MSFT': 0.15, 'TSLA': 0.25, 'AMZN': 0.15}
    portfolio = SuperpositionPortfolio(assets)
    print(f"✅ Portfolio yaratildi: {len(assets)} assets")
    
    # 2. Quantum Superposition
    print("\n📊 QUANTUM SUPERPOSITION:")
    superposition_manager = QuantumSuperpositionManager(len(assets))
    superposition_manager.create_superposition(list(assets.keys()))
    
    # Measurement
    measurements = superposition_manager.measure_portfolio()
    coherence = superposition_manager.get_coherence_measure()
    interference = superposition_manager.calculate_interference()
    
    print(f"• Coherence: {coherence:.4f}")
    print(f"• Interference: {interference.real:.4f}")
    print(f"• Measurements: {len(measurements)} states")
    
    # 3. Tez optimizatsiya
    print("\n⚡ TEZ OPTIMIZATSIYA:")
    
    # Expected returns va covariance (sample data)
    expected_returns = np.array([0.1, 0.08, 0.12, 0.15, 0.06])
    covariance_matrix = np.eye(5) * 0.02
    
    # Simple optimization (classical approach)
    target_return = 0.12
    risk_free_rate = 0.02
    
    # Markowitz optimization (classical)
    from scipy.optimize import minimize
    
    def objective(weights):
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
        return -sharpe_ratio  # Minimize negative Sharpe
    
    # Constraints
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = [(0.05, 0.4) for _ in range(5)]  # Min 5%, Max 40%
    initial_weights = np.ones(5) / 5
    
    # Optimize
    start_time = time.time()
    result = minimize(objective, initial_weights, 
                     method='SLSQP', bounds=bounds, constraints=constraints)
    optimization_time = time.time() - start_time
    
    if result.success:
        optimal_weights = result.x
        optimal_return = np.dot(optimal_weights, expected_returns)
        optimal_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(covariance_matrix, optimal_weights)))
        optimal_sharpe = (optimal_return - risk_free_rate) / optimal_risk
        
        print(f"• Optimization time: {optimization_time:.3f}s")
        print(f"• Optimal Sharpe Ratio: {optimal_sharpe:.4f}")
        print(f"• Expected Return: {optimal_return:.4f}")
        print(f"• Portfolio Risk: {optimal_risk:.4f}")
        print(f"• Convergence: {'✅' if result.success else '❌'}")
        
    # 4. Quantum Feature Demonstration
    print("\n🔬 QUANTUM FEATURES:")
    
    # Quantum interference demo
    quantum_amplitudes = np.random.complex128(len(assets))
    quantum_amplitudes = quantum_amplitudes / np.linalg.norm(quantum_amplitudes)
    
    # Interference calculation
    interference_term = np.sum(quantum_amplitudes**2)
    coherence_measure = np.abs(quantum_amplitudes[0])**2
    
    print(f"• Quantum interference: {interference_term.real:.4f}")
    print(f"• Amplitude magnitude: {coherence_measure:.4f}")
    
    # 5. Portfolio Comparison
    print("\n📊 PERFORMANCE TAQQOSLASH:")
    print(f"• Classical Sharpe: {optimal_sharpe:.4f}")
    print(f"• Quantum Coherence: {coherence:.4f}")
    print(f"• Superposition States: {len(measurements)}")
    
    # 6. Summary
    print("\n🎯 DEMO NATIJALARI:")
    print("-" * 30)
    print(f"✅ Portfolio optimization: tugallandi")
    print(f"✅ Quantum superposition: {len(measurements)} states")
    print(f"✅ Coherence measurement: {coherence:.4f}")
    print(f"✅ Interference analysis: {interference_term.real:.4f}")
    print(f"✅ Optimization time: {optimization_time:.3f}s")
    
    print("\n" + "="*50)
    print("🎉 TEZ QUANTUM PORTFOLIO DEMO YAKUNLANDI!")
    print("="*50)
    
    return {
        'portfolio': portfolio,
        'optimal_weights': optimal_weights,
        'sharpe_ratio': optimal_sharpe,
        'coherence': coherence,
        'optimization_time': optimization_time
    }

if __name__ == "__main__":
    start_time = time.time()
    results = quick_quantum_demo()
    total_time = time.time() - start_time
    print(f"\n⏱️  Total demo time: {total_time:.2f} seconds")