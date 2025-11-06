#!/usr/bin/env python3
"""
Quantum AI Algorithms - Quick Demo Script
==========================================

Bu script Quantum AI Trading tizimining asosiy imkoniyatlarini ko'rsatadi.

Foydalanish:
    python quantum_demo.py

Talablar:
    - quantum_ai_algorithms.py
    - numpy, pandas, scipy, scikit-learn, matplotlib
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Import Quantum AI Components
from quantum_ai_algorithms import (
    HybridQuantumClassicalTrader,
    TradingStrategy,
    ImplementationTimeline,
    QuantumImplementationRoadmap,
    create_quantum_trading_demo,
    QAOAAlgorithm,
    VQEAlgorithm,
    QuantumMonteCarlo
)

def main():
    """Quantum AI Trading tizimi demo."""
    
    print("🧬 QUANTUM AI ALGORITHMS TRADING DEMO")
    print("=" * 60)
    print("Quantum computing va AI'ni birlashtirgan trading tizimi")
    print("=" * 60)
    
    # 1. System Configuration
    print("\n1️⃣ SISTEM KONFIGURATSIYASI")
    print("-" * 40)
    
    config = {
        'hardware_type': 'simulator',
        'quantum_algorithms': {
            'qaoa': {'enabled': True, 'n_qubits': 6},
            'vqe': {'enabled': True, 'n_qubits': 6},
            'quantum_mc': {'enabled': True, 'n_qubits': 4}
        },
        'trading_strategies': {
            'portfolio_optimization': {'enabled': True, 'weight': 0.4},
            'risk_parity': {'enabled': True, 'weight': 0.3},
            'arbitrage_detection': {'enabled': True, 'weight': 0.2},
            'volatility_prediction': {'enabled': True, 'weight': 0.1}
        }
    }
    
    trader = HybridQuantumClassicalTrader(config)
    print("✅ Hybrid Quantum-Classical Trader initialized")
    print(f"📊 Quantum algorithms configured: {list(config['quantum_algorithms'].keys())}")
    print(f"💼 Trading strategies: {list(config['trading_strategies'].keys())}")
    
    # 2. Sample Market Data
    print("\n2️⃣ NAMUNA BOZOR MA'LUMOTLARI")
    print("-" * 40)
    
    # Generate synthetic market data
    np.random.seed(42)
    n_days = 100
    n_assets = 8
    
    # Create correlated returns
    correlation = np.random.uniform(0.1, 0.6, (n_assets, n_assets))
    correlation = (correlation + correlation.T) / 2
    np.fill_diagonal(correlation, 1.0)
    
    # Ensure positive definite matrix
    eigenvals, eigenvecs = np.linalg.eigh(correlation)
    eigenvals = np.maximum(eigenvals, 0.1)  # Ensure positive
    correlation = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
    
    # Generate returns
    daily_returns = np.random.normal(0.0008, 0.025, (n_days, n_assets))
    L = np.linalg.cholesky(correlation)
    correlated_returns = np.dot(daily_returns, L.T)
    
    market_data = pd.DataFrame(correlated_returns, 
                              columns=[f'Asset_{i:02d}' for i in range(n_assets)])
    
    print(f"📈 Generated {n_days} days of data for {n_assets} assets")
    print(f"📊 Data shape: {market_data.shape}")
    print(f"📈 Average daily return: {market_data.mean().mean():.3%}")
    print(f"📊 Average volatility: {market_data.std().mean():.3%}")
    
    # 3. Portfolio Optimization Demo
    print("\n3️⃣ PORTFOLIO OPTIMIZATSIYA")
    print("-" * 40)
    
    try:
        portfolio_result = trader.process_trading_request(
            market_data, 
            TradingStrategy.PORTFOLIO_OPTIMIZATION,
            {'risk_free_rate': 0.02}
        )
        
        print("✅ Portfolio optimization completed")
        print(f"💰 Expected Return: {portfolio_result['expected_return']:.2%}")
        print(f"📊 Volatility: {portfolio_result['volatility']:.2%}")
        print(f"⚡ Sharpe Ratio: {portfolio_result['sharpe_ratio']:.2f}")
        print(f"🧬 Quantum Advantage: {portfolio_result['quantum_advantage']}")
        print(f"🔧 Algorithm Used: {portfolio_result['algorithm_used']}")
        
        # Show top holdings
        weights = portfolio_result['weights']
        top_5_indices = np.argsort(weights)[-5:]
        print("\n🎯 Top 5 Holdings:")
        for i in reversed(top_5_indices):
            print(f"   Asset_{i:02d}: {weights[i]:.2%}")
            
    except Exception as e:
        print(f"❌ Portfolio optimization failed: {e}")
    
    # 4. Risk Parity Demo
    print("\n4️⃣ RISK PARITY OPTIMIZATSIYA")
    print("-" * 40)
    
    try:
        risk_parity_result = trader.process_trading_request(
            market_data, 
            TradingStrategy.RISK_PARITY
        )
        
        print("✅ Risk parity optimization completed")
        print(f"💰 Expected Return: {risk_parity_result['expected_return']:.2%}")
        print(f"📊 Volatility: {risk_parity_result['volatility']:.2%}")
        print(f"⚡ Sharpe Ratio: {risk_parity_result['sharpe_ratio']:.2f}")
        print(f"🧬 Quantum Advantage: {risk_parity_result['quantum_advantage']}")
        
        # Show risk contributions (should be equal)
        weights = risk_parity_result['weights']
        print("\n⚖️ Risk Contributions (should be equal):")
        for i, weight in enumerate(weights[:5]):
            print(f"   Asset_{i:02d}: {weight:.2%}")
            
    except Exception as e:
        print(f"❌ Risk parity optimization failed: {e}")
    
    # 5. Arbitrage Detection Demo
    print("\n5️⃣ ARBITRAJ TOPILISHI")
    print("-" * 40)
    
    try:
        arbitrage_result = trader.process_trading_request(
            market_data, 
            TradingStrategy.ARBITRAGE_DETECTION
        )
        
        print("✅ Arbitrage detection completed")
        print(f"🔍 Total Opportunities: {arbitrage_result.get('total_opportunities', 0)}")
        print(f"💎 Max Profit Margin: {arbitrage_result.get('max_profit_margin', 0):.2%}")
        print(f"🧬 Quantum Advantage: {arbitrage_result['quantum_advantage']}")
        
        # Show opportunities if any
        opportunities = arbitrage_result.get('arbitrage_opportunities', [])
        if opportunities:
            print("\n💰 Top Arbitrage Opportunities:")
            for i, opp in enumerate(opportunities[:3]):
                print(f"   {i+1}. Cycle: {' → '.join(opp['cycle'])}")
                print(f"      Profit: {opp['profit_margin']:.2%}")
                print(f"      Risk: {opp['risk_score']:.2f}")
        else:
            print("\n❌ No profitable arbitrage opportunities found")
            
    except Exception as e:
        print(f"❌ Arbitrage detection failed: {e}")
    
    # 6. Volatility Prediction Demo
    print("\n6️⃣ VOLATILITASH Bashorati")
    print("-" * 40)
    
    try:
        volatility_result = trader.process_trading_request(
            market_data, 
            TradingStrategy.VOLATILITY_PREDICTION
        )
        
        print("✅ Volatility prediction completed")
        
        forecast = volatility_result.get('volatility_forecast', {})
        print(f"📊 Current Volatility: {forecast.get('current_volatility', 0):.2%}")
        print(f"🔮 Forecast Volatility: {forecast.get('forecast_volatility', 0):.2%}")
        print(f"📈 Confidence Score: {forecast.get('confidence_score', 0):.1%}")
        print(f"🧬 Quantum Advantage: {volatility_result['quantum_advantage']}")
        
        # Show confidence interval
        ci_lower = forecast.get('volatility_ci_lower', 0)
        ci_upper = forecast.get('volatility_ci_upper', 0)
        print(f"📊 95% CI: [{ci_lower:.2%}, {ci_upper:.2%}]")
        
    except Exception as e:
        print(f"❌ Volatility prediction failed: {e}")
    
    # 7. Individual Quantum Algorithms Demo
    print("\n7️⃣ ALGORITMLAR NIJOYIDA TEST")
    print("-" * 40)
    
    # QAOA Algorithm
    print("🔬 QAOA Algorithm Test:")
    try:
        qaoa = QAOAAlgorithm(n_qubits=4, p_layers=1)
        problem_data = np.random.normal(0, 1, (4, 4))
        circuit = qaoa.build_circuit(problem_data)
        quantum_state = qaoa.execute(circuit, shots=512)
        solution = qaoa.extract_solution(quantum_state)
        
        print(f"   ✅ QAOA executed successfully")
        print(f"   🎯 Solution shape: {solution.shape}")
        print(f"   🔬 Fidelity: {quantum_state.fidelity:.2f}")
        
    except Exception as e:
        print(f"   ❌ QAOA failed: {e}")
    
    # VQE Algorithm
    print("\n🔬 VQE Algorithm Test:")
    try:
        vqe = VQEAlgorithm(n_qubits=4, ansatz_depth=2)
        problem_data = np.random.normal(0, 1, (4, 4))
        circuit = vqe.build_circuit(problem_data)
        quantum_state = vqe.execute(circuit, shots=512)
        solution = vqe.extract_solution(quantum_state)
        
        print(f"   ✅ VQE executed successfully")
        print(f"   🎯 Solution shape: {solution.shape}")
        print(f"   🔬 Fidelity: {quantum_state.fidelity:.2f}")
        
    except Exception as e:
        print(f"   ❌ VQE failed: {e}")
    
    # Quantum Monte Carlo
    print("\n🔬 Quantum Monte Carlo Test:")
    try:
        qmc = QuantumMonteCarlo(n_qubits=4, n_samples=512)
        risk_data = np.random.normal(0, 0.1, (4, 100))
        circuit = qmc.build_circuit(risk_data)
        quantum_state = qmc.execute(circuit, shots=512)
        risk_metrics = qmc.extract_solution(quantum_state)
        
        print(f"   ✅ Quantum MC executed successfully")
        print(f"   📊 Risk metrics: {risk_metrics}")
        print(f"   🔬 Fidelity: {quantum_state.fidelity:.2f}")
        
    except Exception as e:
        print(f"   ❌ Quantum MC failed: {e}")
    
    # 8. Implementation Roadmap
    print("\n8️⃣ IMPLEMENTATSIYA REJASI")
    print("-" * 40)
    
    roadmap = QuantumImplementationRoadmap()
    
    # Near-term plan
    current_capabilities = {
        'quantum_experience': 'beginner',
        'budget': 'medium',
        'team_size': 10,
        'existing_infrastructure': 'cloud'
    }
    
    near_term_plan = roadmap.get_implementation_plan(
        ImplementationTimeline.NEAR_TERM, current_capabilities
    )
    
    print(f"🗓️ Timeline: {near_term_plan['timeline']}")
    print(f"🎯 Focus: {near_term_plan['focus']}")
    print(f"💰 Investment: {near_term_plan['technology_requirements']['investment']}")
    
    print("\n📋 Key Initiatives:")
    for i, initiative in enumerate(near_term_plan['key_initiatives'][:3], 1):
        print(f"   {i}. {initiative['name']}")
        print(f"      📅 Timeline: {initiative['timeline']}")
        print(f"      💡 ROI: {initiative['expected_roi']}")
    
    # 9. System Status
    print("\n9️⃣ SISTEM HOLATI")
    print("-" * 40)
    
    status = trader.get_system_status()
    
    print(f"🟢 System Health: {status['system_health']}")
    print(f"🧬 Quantum Available: {status['quantum_available']}")
    print(f"⚡ Quantum Usage Rate: {status['quantum_usage_rate']:.1%}")
    print(f"⏱️ Avg Computation Time: {status['avg_computation_time']:.3f}s")
    print(f"📊 Total Requests: {status['total_requests_processed']}")
    
    # Hardware status
    hw_status = status['hardware_status']
    print(f"🔧 Hardware Status:")
    print(f"   Qiskit: {'✅' if hw_status['qiskit_available'] else '❌'}")
    print(f"   PennyLane: {'✅' if hw_status['pennylane_available'] else '❌'}")
    print(f"   Cirq: {'✅' if hw_status['cirq_available'] else '❌'}")
    
    # 10. Quick Performance Summary
    print("\n🔟 PERFORMANS XULOSASI")
    print("-" * 40)
    
    if portfolio_result and 'weights' in portfolio_result:
        print("📊 Portfolio Performance:")
        print(f"   Expected Return: {portfolio_result['expected_return']:.2%}")
        print(f"   Volatility: {portfolio_result['volatility']:.2%}")
        print(f"   Sharpe Ratio: {portfolio_result['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {portfolio_result.get('max_drawdown', 0):.2%}")
    
    print("\n🧬 Quantum Advantage Summary:")
    quantum_strategies = sum(1 for result in [portfolio_result, risk_parity_result, 
                                           arbitrage_result, volatility_result] 
                           if result and result.get('quantum_advantage', False))
    total_strategies = sum(1 for result in [portfolio_result, risk_parity_result, 
                                          arbitrage_result, volatility_result] 
                         if result is not None)
    
    if total_strategies > 0:
        advantage_rate = quantum_strategies / total_strategies
        print(f"   ✅ Quantum Advantage Rate: {advantage_rate:.1%}")
        print(f"   🎯 Strategies with Quantum Advantage: {quantum_strategies}/{total_strategies}")
    else:
        print("   ❌ No strategies executed successfully")
    
    print("\n🎉 QUANTUM AI ALGORITHMS DEMO COMPLETED!")
    print("=" * 60)
    print("Batafsil ma'lumot: quantum_ai_algorithms_README.md")
    print("Quantum Advantage: Research va development bosqichida")
    print("Production: Qo'shimcha testing va validation kerak")
    print("=" * 60)

if __name__ == "__main__":
    main()