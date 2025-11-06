"""
Market Analysis Package
======================

Comprehensive market impact analysis va market hours handling system.

Ushbu paket quyidagi asosiy modullarni o'z ichiga oladi:

1. **Market Impact Analysis:**
   - Price Impact Modeling
   - Liquidity Analysis  
   - Market Depth Assessment
   - Order Book Dynamics
   - Slippage Calculation

2. **Market Hours Management:**
   - Forex Session Management (Asian, European, American)
   - Session Overlap Optimization
   - News Event Timing
   - Central Bank Announcements
   - Economic Calendar Integration

3. **Metal Market Analysis:**
   - Market Opening/Closing Patterns
   - Volatility Clustering
   - Seasonal Patterns
   - Industrial Demand Cycles
   - Inventory Reporting Effects

4. **Market Regime Detection:**
   - Trending vs Ranging Markets
   - Volatility Regime Identification
   - Market Microstructure Changes
   - Liquidity Condition Analysis
   - Black Swan Event Detection

5. **Adaptive Strategies:**
   - Dynamic Strategy Selection
   - Market Condition Adaptation
   - Performance-based Switching
   - Risk-adjusted Execution
   - Smart Order Routing

## Asosiy Sinflar

### Market Impact
- `PriceImpactModel`: Price impact modeling
- `LiquidityAnalyzer`: Liquidity tahlil
- `MarketDepthAnalyzer`: Market depth assessment
- `OrderBookAnalyzer`: Order book dynamics
- `SlippageCalculator`: Slippage hisoblash

### Market Hours
- `ForexSessionManager`: Forex session management
- `SessionOverlapAnalyzer`: Session overlap tahlil
- `NewsEventAnalyzer`: Yangilik voqealar tahlil
- `CentralBankAnalyzer`: Markaziy bank tahlil
- `EconomicCalendarLoader`: Iqtisodiy calendar

### Metal Markets
- `MetalMarketAnalyzer`: Asosiy metal bozor tahlil
- `VolatilityPatternAnalyzer`: Volatilite pattern tahlil
- `SeasonalAnalyzer`: Seasonal pattern tahlil
- `DemandCycleAnalyzer`: Demand cycle tahlil
- `InventoryAnalyzer`: Inventory effect tahlil

### Regime Detection
- `MarketRegimeDetector`: Bozot rejim aniqlash
- `VolatilityRegimeAnalyzer`: Volatilite rejim tahlil

### Adaptive Strategies
- `AdaptiveStrategyManager`: Moslashuvchan strategiya boshqaruv

## Foydalanish

```python
from market_analysis import (
    PriceImpactModel, LiquidityAnalyzer, ForexSessionManager,
    MetalMarketAnalyzer, MarketRegimeDetector, AdaptiveStrategyManager
)

# Price impact tahlili
impact_model = PriceImpactModel()
impact_result = impact_model.calculate_total_impact(
    volume=1000000,
    avg_volume=5000000,
    volatility=0.02,
    time_of_day=14,
    order_book_depth=10000000,
    spread=0.0015
)

# Forex session tahlili
session_manager = ForexSessionManager()
current_session = session_manager.get_current_session()

# Metal bozor tahlili
metal_analyzer = MetalMarketAnalyzer()
metal_report = metal_analyzer.create_metal_market_report('XAUUSD', gold_data)

# Rejim aniqlash
regime_detector = MarketRegimeDetector()
current_regime = regime_detector.detect_trending_ranging_regime(price_data)

# Strategiya tanlash
strategy_manager = AdaptiveStrategyManager()
optimal_strategy = strategy_manager.select_optimal_strategy(
    market_regime='trending',
    liquidity_level='high_liquidity',
    volatility_level='normal_volatility'
)
```

## Talablar

- pandas
- numpy
- scipy
- scikit-learn
- pytz

## Litsenziya

MIT License
"""

__version__ = "1.0.0"
__author__ = "Market Analysis Team"

# Import main classes for easy access
from .market_impact.price_impact_model import PriceImpactModel
from .market_impact.liquidity_analysis import LiquidityAnalyzer
from .market_hours.forex_sessions import ForexSessionManager
from .metal_markets.opening_closing import MetalMarketAnalyzer
from .regime_detection.trending_ranging import MarketRegimeDetector
from .adaptive_strategies.strategy_selection import AdaptiveStrategyManager

__all__ = [
    'PriceImpactModel',
    'LiquidityAnalyzer', 
    'ForexSessionManager',
    'MetalMarketAnalyzer',
    'MarketRegimeDetector',
    'AdaptiveStrategyManager'
]