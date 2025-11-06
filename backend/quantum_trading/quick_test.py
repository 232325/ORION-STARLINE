#!/usr/bin/env python3
"""
Quantum Advantage Trading System - Quick Test
===========================================

Bu test quantum trading tizimining asosiy komponentlarini
tezkor tarzda test qilish uchun mo'ljallangan.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_trading.main import QuantumAdvantageTradingSystem, TradingConfig

async def quick_test():
    """Teza test"""
    print("🚀 Quantum Advantage Trading System - Tez Test")
    print("=" * 50)
    
    # Test 1: System initialization
    print("1️⃣ Tizimni initsializatsiya qilish...")
    config = TradingConfig(
        quantum_advantage_threshold=0.15,
        stocks_weight=0.4,
        forex_weight=0.3,
        metals_weight=0.2,
        crypto_weight=0.1
    )
    
    system = QuantumAdvantageTradingSystem(config)
    await system.initialize_system()
    print("✅ Tizim muvaffaqiyatli initsializatsiya qilindi!")
    
    # Test 2: Market data collection
    print("\n2️⃣ Market ma'lumotlari to'plash...")
    stocks_data = await system.multi_asset_trader.collect_stocks_data()
    print(f"✅ Stocks ma'lumotlari: {len(stocks_data['data'])} ta aktiv")
    
    forex_data = await system.multi_asset_trader.collect_forex_data()
    print(f"✅ Forex ma'lumotlari: {len(forex_data['data'])} ta juftlik")
    
    # Test 3: Quantum optimization
    print("\n3️⃣ Quantum optimizatsiya...")
    optimization_problem = {
        "current_portfolio": system.portfolio_state,
        "market_data": {"stocks": stocks_data, "forex": forex_data},
        "constraints": {"max_drawdown": 0.05}
    }
    
    result = await system.quantum_optimizer.optimize_portfolio(optimization_problem)
    print(f"✅ Quantum advantage: {result['optimization_details']['quantum_advantage']:.1f}x")
    
    # Test 4: Error correction
    print("\n4️⃣ Error correction...")
    from quantum_trading.error_correction import ErrorCorrectionCode
    test_state = await system.quantum_optimizer.create_portfolio_state()
    corrected_state, correction_result = await system.error_corrector.detect_and_correct_errors(
        test_state, ErrorCorrectionCode.SURFACE_CODE
    )
    print(f"✅ Error correction: {correction_result.correction_applied}")
    
    # Test 5: Trading cycle
    print("\n5️⃣ Trading tsikli...")
    cycle_result = await system.execute_quantum_trading_cycle()
    print(f"✅ Trading tsikli: {cycle_result['status']}")
    print(f"   Quantum advantage: {cycle_result['quantum_advantage']['overall_advantage']:.2f}%")
    
    print("\n🎉 Barcha testlar muvaffaqiyatli yakunlandi!")
    print("📊 Quantum trading tizimi to'liq ishlayapti!")
    
    return system

async def main():
    """Asosiy funksiya"""
    try:
        system = await quick_test()
        
        # Save results
        output_dir = Path("test_results")
        output_dir.mkdir(exist_ok=True)
        
        await system.export_results(str(output_dir / "quick_test_results.json"))
        
        print(f"\n📁 Natijalar saqlandi: {output_dir}")
        
    except Exception as e:
        print(f"\n❌ Test xatosi: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Quantum Trading System - Quick Test")
    print("Test boshlanmoqda...\n")
    
    success = asyncio.run(main())
    
    if success:
        print("\n✅ Barcha testlar muvaffaqiyatli!")
    else:
        print("\n❌ Ba'zi testlar xato berdi!")
    
    sys.exit(0 if success else 1)