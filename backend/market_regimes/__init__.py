"""
Market Regime Detection va Cross-Asset Correlation Learning Package

Professional-grade market regime detection va correlation analysis tizimi.
"""

# Import main classes
from .regime_detection import RegimeDetector, HiddenMarkovRegimeDetector, RegimeAnalyzer
from .correlation_learning import (
    DynamicCorrelationModel, CorrelationRegimeDetector, 
    CrossAssetFactorModel, CorrelationClustering
)
from .adaptive_strategies import (
    TrendFollowingStrategy, MeanReversionStrategy, VolatilityTargetingStrategy,
    DynamicRiskManager, AdaptivePortfolioManager
)
from .implementation_framework import (
    RealTimeRegimeDetector, RegimeAwareBacktester, SystemIntegration,
    MarketDataPoint, RegimeSignal, TradingSignal
)
from .config import (
    SystemConfig, RegimePreferences, AssetUniverse, PerformanceBenchmarks,
    get_default_config, get_conservative_config, get_aggressive_config
)

# Version information
__version__ = "1.0.0"
__author__ = "Market Regime Detection Team"
__email__ = "support@marketregimes.com"
__description__ = "Market Regime Detection va Cross-Asset Correlation Learning System"

# Package metadata
__all__ = [
    # Regime Detection
    'RegimeDetector',
    'HiddenMarkovRegimeDetector', 
    'RegimeAnalyzer',
    
    # Correlation Learning
    'DynamicCorrelationModel',
    'CorrelationRegimeDetector',
    'CrossAssetFactorModel',
    'CorrelationClustering',
    
    # Adaptive Strategies
    'TrendFollowingStrategy',
    'MeanReversionStrategy',
    'VolatilityTargetingStrategy',
    'DynamicRiskManager',
    'AdaptivePortfolioManager',
    
    # Implementation Framework
    'RealTimeRegimeDetector',
    'RegimeAwareBacktester',
    'SystemIntegration',
    'MarketDataPoint',
    'RegimeSignal',
    'TradingSignal',
    
    # Configuration
    'SystemConfig',
    'RegimePreferences',
    'AssetUniverse',
    'PerformanceBenchmarks',
    'get_default_config',
    'get_conservative_config',
    'get_aggressive_config'
]

# Package constants
REGIME_TYPES = [
    'Trending', 'Ranging', 'High Volatility', 'Low Volatility', 
    'Crisis', 'Normal', 'Mixed/Neutral'
]

CORRELATION_METHODS = ['pca', 'factor_analysis']

STRATEGY_TYPES = [
    'trend_following', 'mean_reversion', 'momentum',
    'volatility_targeting', 'risk_parity', 'dynamic_hedging'
]

RISK_METRICS = [
    'portfolio_volatility', 'max_drawdown', 'var_95', 
    'expected_shortfall', 'sharpe_ratio', 'sortino_ratio'
]

def get_package_info():
    """Package haqida ma'lumot olish"""
    return {
        'name': __name__,
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'available_regimes': REGIME_TYPES,
        'correlation_methods': CORRELATION_METHODS,
        'strategy_types': STRATEGY_TYPES
    }

def check_dependencies():
    """Kerakli kutubxonalar tekshirish"""
    required_packages = {
        'numpy': 'numpy',
        'pandas': 'pandas', 
        'scikit-learn': 'sklearn',
        'scipy': 'scipy',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn'
    }
    
    missing_packages = []
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        missing_str = ', '.join(missing_packages)
        raise ImportError(f"Quyidagi paketlar o'rnatilmagan: {missing_str}")
    
    return True

def quick_demo():
    """Tizim tez namuna ko'rsatish"""
    try:
        check_dependencies()
        
        from .demo import MarketRegimeSystemDemo
        
        print("Market Regime Detection System - Tez Demo")
        print("=" * 50)
        
        # Demo yaratish
        demo = MarketRegimeSystemDemo("default")
        
        # Qisqa demo (100 kun, 5 asset)
        print("Qisqa demo ishga tushmoqda...")
        results = demo.run_complete_demo(
            n_days=100,
            n_assets=5,
            save_results=False  # Tez test uchun
        )
        
        print("✓ Demo muvaffaqiyatli tugallandi!")
        print(f"Joriy rejim: {results['regime_results']['current_regime']}")
        
        if 'backtest_results' in results['strategy_results']:
            total_return = results['strategy_results']['backtest_results']['performance_metrics'].get('total_return', 0)
            print(f"Backtest natija: {total_return:.2%}")
        
        return True
        
    except Exception as e:
        print(f"Demo xatosi: {e}")
        return False

# Package initialization
try:
    check_dependencies()
    print(f"Market Regime Detection package v{__version__} muvaffaqiyatli yuklandi")
except ImportError as e:
    print(f"Ogohlantirish: {e}")
    print("Ishga tushish uchun kerakli paketlarni o'rnating: pip install numpy pandas scikit-learn scipy matplotlib seaborn")

# Utility functions
def create_sample_config():
    """Sample konfiguratsiya yaratish"""
    config = get_default_config()
    config.regime_detection.lookback_window = 252
    config.strategy.max_portfolio_risk = 0.02
    config.backtest.initial_capital = 100000
    return config

def validate_market_data(data):
    """Market data validation"""
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Market data must be a pandas DataFrame")
    
    if data.empty:
        raise ValueError("Market data cannot be empty")
    
    if not pd.api.types.is_numeric_dtype(data.select_dtypes(include=[np.number]).iloc[:, 0]):
        raise ValueError("Market data must contain numeric values")
    
    return True

# Quick setup guide
SETUP_GUIDE = """
Market Regime Detection Setup Guide:

1. Install required packages:
   pip install numpy pandas scikit-learn scipy matplotlib seaborn

2. Quick test:
   from market_regimes import quick_demo
   quick_demo()

3. Full demo:
   from market_regimes import MarketRegimeSystemDemo
   demo = MarketRegimeSystemDemo("default")
   results = demo.run_complete_demo()

4. Basic usage:
   from market_regimes import RegimeDetector
   detector = RegimeDetector()
   regimes = detector.detect_all_regimes(price_data)

For more examples, see demo.py and README.md
"""

print(SETUP_GUIDE)