#!/usr/bin/env python3
"""
Test script for Market Regime Detection System
"""

import sys
import os
sys.path.append('/workspace/code')

# Test individual modules
def test_regime_detection():
    """Test regime detection module"""
    print("Testing Regime Detection Module...")
    
    import numpy as np
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Generate test data
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    prices = pd.DataFrame(
        np.random.randn(100, 3).cumsum(axis=0) + 100,
        index=dates,
        columns=['AAPL', 'MSFT', 'GOOGL']
    )
    
    # Test regime detection
    exec(open('/workspace/code/market_regimes/regime_detection.py').read())
    
    detector = RegimeDetector()
    regimes = detector.detect_all_regimes(prices)
    current_regime = detector.get_current_regime(prices)
    
    print(f"✓ Current regime detected: {current_regime}")
    print(f"✓ Regime detection completed successfully")
    return True

def test_correlation_learning():
    """Test correlation learning module"""
    print("Testing Correlation Learning Module...")
    
    import numpy as np
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Generate test data
    dates = pd.date_range('2020-01-01', periods=200, freq='D')
    returns = pd.DataFrame(
        np.random.randn(200, 4),
        index=dates,
        columns=['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    )
    
    # Test correlation learning
    exec(open('/workspace/code/market_regimes/correlation_learning.py').read())
    
    dyn_corr = DynamicCorrelationModel(window_size=60)
    rolling_corr = dyn_corr.rolling_correlation_matrix(returns)
    
    print(f"✓ Rolling correlations calculated: {len(rolling_corr)} time periods")
    print(f"✓ Correlation learning completed successfully")
    return True

def test_adaptive_strategies():
    """Test adaptive strategies module"""
    print("Testing Adaptive Strategies Module...")
    
    import numpy as np
    import pandas as pd
    
    # Test strategies
    exec(open('/workspace/code/market_regimes/adaptive_strategies.py').read())
    
    trend_strategy = TrendFollowingStrategy()
    risk_manager = DynamicRiskManager()
    
    print(f"✓ Strategies created: {trend_strategy.name}")
    print(f"✓ Risk manager initialized")
    print(f"✓ Adaptive strategies completed successfully")
    return True

def test_configuration():
    """Test configuration module"""
    print("Testing Configuration Module...")
    
    exec(open('/workspace/code/market_regimes/config.py').read())
    
    config = get_default_config()
    trend_prefs = RegimePreferences.get_trend_following_preferences()
    equity_assets = AssetUniverse.get_equity_universe()
    
    print(f"✓ Default config created")
    print(f"✓ Trend preferences: {len(trend_prefs)} regimes")
    print(f"✓ Equity universe: {len(equity_assets)} assets")
    print(f"✓ Configuration completed successfully")
    return True

def test_integration():
    """Test system integration"""
    print("Testing System Integration...")
    
    # Test imports
    exec(open('/workspace/code/market_regimes/implementation_framework.py').read())
    
    print(f"✓ Implementation framework imported")
    print(f"✓ System integration completed successfully")
    return True

def main():
    """Main test function"""
    print("=" * 60)
    print("MARKET REGIME DETECTION SYSTEM - MODULE TEST")
    print("=" * 60)
    
    tests = [
        ("Regime Detection", test_regime_detection),
        ("Correlation Learning", test_correlation_learning),
        ("Adaptive Strategies", test_adaptive_strategies),
        ("Configuration", test_configuration),
        ("System Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)