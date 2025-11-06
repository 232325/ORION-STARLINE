#!/usr/bin/env python3
"""Teat qisqa test tuzatilgan xatolarni tekshirish uchun"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pro_backtesting import *
import pandas as pd
import numpy as np

def test_basic_functionality():
    """Asosiy funksiyalarni test qilish"""
    print("🧪 Asosiy funksiyalar test...")
    
    # Sample data yaratish
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    np.random.seed(42)
    data = pd.DataFrame({
        'Open': np.random.randn(100).cumsum() + 100,
        'High': np.random.randn(100).cumsum() + 102,
        'Low': np.random.randn(100).cumsum() + 98,
        'Close': np.random.randn(100).cumsum() + 100,
        'Volume': np.random.randint(1000000, 5000000, 100)
    }, index=dates)
    data['Close'] = data['Close'].clip(lower=1)
    
    print(f"✅ Ma'lumotlar yaratildi: {data.shape}")
    
    # Engine yaratish
    engine = ProBacktestingEngine(max_workers=2)
    print("✅ Engine yaratildi")
    
    # Strategiya konfiguratsiya
    strategy_config = StrategyConfig(
        name="Test Strategy",
        parameters={'short_window': 10, 'long_window': 20},
        timeframe=TimeFrame.DAILY,
        commission=0.001,
        slippage=0.0005
    )
    
    print("✅ Strategiya konfiguratsiya yaratildi")
    
    # Backtest run
    result = engine.run_backtest(strategy_config, data)
    print(f"✅ Backtest tugallandi: Total Return {result.total_return:.2%}")
    
    # Commission va slippage test
    print("✅ Commission va slippage test...")
    test_order = {'side': 'BUY', 'size': 100}
    current_price = 100
    volatility = 0.02
    
    # Test default cost models
    commission = engine.commission_models['percentage'](100, 100)
    slippage = engine.slippage_models['proportional'](100, 100, 0.02)
    print(f"✅ Commission: {commission:.4f}, Slippage: {slippage:.4f}")
    
    print("\n🎉 Barcha asosiy testlar muvaffaqiyatli!")
    return True

if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"❌ Xato: {e}")
        import traceback
        traceback.print_exc()