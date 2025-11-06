"""
AI Trading Evolution - Multi-Market Correlation Analysis Module
===============================================================

Turli bozorlar orasidagi korrelyatsiya tahlili:
- Crypto vs Stocks
- Crypto vs Commodities  
- Stocks vs Bonds
- Cross-asset correlations
- Risk-on/Risk-off regimes
- Portfolio diversification optimization
- Macro factor analysis
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetClass(Enum):
    """Asset class turlari"""
    CRYPTO = "crypto"
    STOCKS = "stocks"
    COMMODITIES = "commodities"
    BONDS = "bonds"
    FOREX = "forex"
    ETF = "etf"


class MarketRegime(Enum):
    """Bozor rejimlari"""
    RISK_ON = "risk_on"  # Risk appetite yuqori
    RISK_OFF = "risk_off"  # Risk aversion yuqori
    NEUTRAL = "neutral"
    VOLATILITY_SPIKE = "volatility_spike"


@dataclass
class AssetPair:
    """Asset juftligi"""
    asset1: str
    asset1_class: AssetClass
    asset2: str
    asset2_class: AssetClass
    correlation: float  # -1 to 1
    rolling_correlation: List[float]  # Tarixiy
    p_value: float  # Statistical significance
    lookback_days: int
    
    @property
    def correlation_strength(self) -> str:
        """Korrelyatsiya kuchi"""
        abs_corr = abs(self.correlation)
        if abs_corr > 0.7:
            return "STRONG"
        elif abs_corr > 0.4:
            return "MODERATE"
        else:
            return "WEAK"
    
    @property
    def is_significant(self) -> bool:
        """Statistik ahamiyatli?"""
        return self.p_value < 0.05


@dataclass
class MarketRegimeAnalysis:
    """Bozor rejimi tahlili"""
    regime: MarketRegime
    confidence: float
    indicators: Dict[str, float]
    risk_assets_performance: float
    safe_haven_performance: float
    volatility_level: str  # LOW, MEDIUM, HIGH
    timestamp: datetime = field(default_factory=datetime.now)


class MultiMarketDataProvider:
    """
    Multi-market ma'lumot provayderi
    Barcha asset classlardan narxlarni olish
    """
    
    def __init__(self):
        self.cache: Dict[str, pd.DataFrame] = {}
    
    async def get_price_history(
        self,
        symbol: str,
        asset_class: AssetClass,
        days: int = 90
    ) -> Optional[pd.DataFrame]:
        """Narx tarixini olish"""
        cache_key = f"{symbol}_{asset_class.value}_{days}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Demo data generation
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            
            # Base prices
            base_prices = {
                # Crypto
                'BTC': 68500, 'ETH': 3450, 'SOL': 145,
                # Stocks
                'SPY': 450, 'QQQ': 380, 'AAPL': 178,
                # Commodities
                'GLD': 182, 'USO': 78, 'DBA': 22,
                # Bonds
                'TLT': 95, 'AGG': 101, 'HYG': 78,
                # Forex
                'DXY': 104  # Dollar Index
            }
            
            base_price = base_prices.get(symbol, 100)
            
            # Volatility based on asset class
            volatility_map = {
                AssetClass.CRYPTO: 0.04,
                AssetClass.STOCKS: 0.015,
                AssetClass.COMMODITIES: 0.02,
                AssetClass.BONDS: 0.008,
                AssetClass.FOREX: 0.005
            }
            
            vol = volatility_map.get(asset_class, 0.02)
            
            # Generate price series with specific correlation patterns
            returns = np.random.normal(0.0005, vol, days)
            
            # Add some trend
            if asset_class == AssetClass.CRYPTO:
                trend = np.linspace(-0.0002, 0.0002, days)
                returns += trend
            
            prices = base_price * np.cumprod(1 + returns)
            
            df = pd.DataFrame({
                'close': prices,
                'high': prices * 1.02,
                'low': prices * 0.98,
                'volume': np.random.randint(1000000, 10000000, days)
            }, index=dates)
            
            self.cache[cache_key] = df
            return df
            
        except Exception as e:
            logger.error(f"Narx tarixini olishda xato ({symbol}): {e}")
            return None


class CorrelationAnalyzer:
    """
    Korrelyatsiya tahlilchisi
    - Pearson correlation
    - Rolling correlation
    - Cross-asset correlation matrix
    """
    
    def __init__(self, data_provider: MultiMarketDataProvider):
        self.data_provider = data_provider
    
    async def calculate_correlation(
        self,
        asset1: str,
        asset1_class: AssetClass,
        asset2: str,
        asset2_class: AssetClass,
        lookback_days: int = 90
    ) -> Optional[AssetPair]:
        """Ikki asset orasidagi korrelyatsiyani hisoblash"""
        df1 = await self.data_provider.get_price_history(asset1, asset1_class, lookback_days)
        df2 = await self.data_provider.get_price_history(asset2, asset2_class, lookback_days)
        
        if df1 is None or df2 is None:
            return None
        
        # Align dates
        common_dates = df1.index.intersection(df2.index)
        
        if len(common_dates) < 30:
            return None
        
        prices1 = df1.loc[common_dates, 'close']
        prices2 = df2.loc[common_dates, 'close']
        
        # Returns
        returns1 = prices1.pct_change().dropna()
        returns2 = prices2.pct_change().dropna()
        
        # Pearson correlation
        correlation = returns1.corr(returns2)
        
        # Rolling correlation (30-day window)
        rolling_corr = returns1.rolling(window=30).corr(returns2).dropna()
        
        # P-value (simplified)
        from scipy import stats
        _, p_value = stats.pearsonr(returns1, returns2)
        
        pair = AssetPair(
            asset1=asset1,
            asset1_class=asset1_class,
            asset2=asset2,
            asset2_class=asset2_class,
            correlation=correlation,
            rolling_correlation=rolling_corr.tolist(),
            p_value=p_value,
            lookback_days=lookback_days
        )
        
        return pair
    
    async def build_correlation_matrix(
        self,
        assets: List[Tuple[str, AssetClass]],
        lookback_days: int = 90
    ) -> pd.DataFrame:
        """Barcha assetlar uchun correlation matrix"""
        symbols = [asset[0] for asset in assets]
        n = len(symbols)
        
        corr_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    corr_matrix[i, j] = 1.0
                else:
                    pair = await self.calculate_correlation(
                        symbols[i], assets[i][1],
                        symbols[j], assets[j][1],
                        lookback_days
                    )
                    
                    if pair:
                        corr_matrix[i, j] = pair.correlation
                        corr_matrix[j, i] = pair.correlation
        
        df = pd.DataFrame(corr_matrix, index=symbols, columns=symbols)
        return df
    
    async def find_diversification_pairs(
        self,
        assets: List[Tuple[str, AssetClass]],
        max_correlation: float = 0.3
    ) -> List[AssetPair]:
        """
        Diversifikatsiya uchun eng yaxshi juftliklarni topish
        Past korrelyatsiya = yaxshi diversifikatsiya
        """
        pairs = []
        
        for i in range(len(assets)):
            for j in range(i + 1, len(assets)):
                pair = await self.calculate_correlation(
                    assets[i][0], assets[i][1],
                    assets[j][0], assets[j][1]
                )
                
                if pair and abs(pair.correlation) <= max_correlation and pair.is_significant:
                    pairs.append(pair)
        
        # Sort by lowest absolute correlation
        pairs.sort(key=lambda x: abs(x.correlation))
        return pairs


class RegimeDetector:
    """
    Bozor rejimini aniqlash
    Risk-on vs Risk-off
    """
    
    def __init__(self, data_provider: MultiMarketDataProvider):
        self.data_provider = data_provider
    
    async def detect_current_regime(self) -> MarketRegimeAnalysis:
        """Hozirgi bozor rejimini aniqlash"""
        lookback = 30
        
        # Risk assets: SPY (stocks), BTC (crypto)
        spy = await self.data_provider.get_price_history('SPY', AssetClass.STOCKS, lookback)
        btc = await self.data_provider.get_price_history('BTC', AssetClass.CRYPTO, lookback)
        
        # Safe havens: TLT (bonds), GLD (gold)
        tlt = await self.data_provider.get_price_history('TLT', AssetClass.BONDS, lookback)
        gld = await self.data_provider.get_price_history('GLD', AssetClass.COMMODITIES, lookback)
        
        # Calculate returns
        spy_return = (spy['close'].iloc[-1] / spy['close'].iloc[0] - 1) * 100 if spy is not None else 0
        btc_return = (btc['close'].iloc[-1] / btc['close'].iloc[0] - 1) * 100 if btc is not None else 0
        tlt_return = (tlt['close'].iloc[-1] / tlt['close'].iloc[0] - 1) * 100 if tlt is not None else 0
        gld_return = (gld['close'].iloc[-1] / gld['close'].iloc[0] - 1) * 100 if gld is not None else 0
        
        risk_assets_perf = (spy_return + btc_return) / 2
        safe_haven_perf = (tlt_return + gld_return) / 2
        
        # Volatility (SPY as proxy)
        if spy is not None:
            returns = spy['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100  # Annualized
            
            if volatility > 30:
                vol_level = "HIGH"
            elif volatility > 15:
                vol_level = "MEDIUM"
            else:
                vol_level = "LOW"
        else:
            volatility = 15
            vol_level = "MEDIUM"
        
        # Regime determination
        indicators = {
            'risk_assets_return': risk_assets_perf,
            'safe_haven_return': safe_haven_perf,
            'volatility': volatility,
            'spread': risk_assets_perf - safe_haven_perf
        }
        
        # Decision logic
        if volatility > 30:
            regime = MarketRegime.VOLATILITY_SPIKE
            confidence = 0.85
        elif risk_assets_perf > 5 and risk_assets_perf > safe_haven_perf:
            regime = MarketRegime.RISK_ON
            confidence = min(risk_assets_perf / 10, 1.0)
        elif safe_haven_perf > 5 and safe_haven_perf > risk_assets_perf:
            regime = MarketRegime.RISK_OFF
            confidence = min(safe_haven_perf / 10, 1.0)
        else:
            regime = MarketRegime.NEUTRAL
            confidence = 0.60
        
        analysis = MarketRegimeAnalysis(
            regime=regime,
            confidence=confidence,
            indicators=indicators,
            risk_assets_performance=risk_assets_perf,
            safe_haven_performance=safe_haven_perf,
            volatility_level=vol_level
        )
        
        return analysis
    
    async def get_regime_based_allocation(self) -> Dict[str, float]:
        """Rejim asosida asset allocation"""
        regime_analysis = await self.detect_current_regime()
        
        if regime_analysis.regime == MarketRegime.RISK_ON:
            # Risk-on: ko'proq stocks va crypto
            allocation = {
                'stocks': 0.50,
                'crypto': 0.25,
                'commodities': 0.15,
                'bonds': 0.10
            }
        elif regime_analysis.regime == MarketRegime.RISK_OFF:
            # Risk-off: ko'proq bonds va gold
            allocation = {
                'bonds': 0.45,
                'commodities': 0.30,  # Gold
                'stocks': 0.15,
                'crypto': 0.10
            }
        elif regime_analysis.regime == MarketRegime.VOLATILITY_SPIKE:
            # High vol: cash va stable assets
            allocation = {
                'bonds': 0.50,
                'commodities': 0.25,
                'stocks': 0.15,
                'crypto': 0.10
            }
        else:  # NEUTRAL
            # Balanced
            allocation = {
                'stocks': 0.40,
                'bonds': 0.30,
                'commodities': 0.15,
                'crypto': 0.15
            }
        
        return allocation


class CrossAssetStrategy:
    """
    Cross-asset trading strategiyalari
    - Pairs trading across asset classes
    - Risk parity
    - Flight to quality
    """
    
    def __init__(
        self,
        data_provider: MultiMarketDataProvider,
        correlation_analyzer: CorrelationAnalyzer
    ):
        self.data_provider = data_provider
        self.correlation_analyzer = correlation_analyzer
    
    async def detect_cross_asset_divergence(
        self,
        lookback_days: int = 90
    ) -> List[Dict]:
        """
        Cross-asset divergence detection
        Odatda korrelyatsiya bo'lgan assetlar diverge qilsa - mean reversion imkoniyati
        """
        # Historically correlated pairs
        pairs_to_check = [
            ('SPY', AssetClass.STOCKS, 'BTC', AssetClass.CRYPTO),  # Risk-on assets
            ('GLD', AssetClass.COMMODITIES, 'TLT', AssetClass.BONDS),  # Safe havens
            ('USO', AssetClass.COMMODITIES, 'XLE', AssetClass.ETF),  # Energy
        ]
        
        divergences = []
        
        for asset1, class1, asset2, class2 in pairs_to_check:
            # Historical correlation
            pair = await self.correlation_analyzer.calculate_correlation(
                asset1, class1, asset2, class2, lookback_days
            )
            
            if not pair or pair.correlation < 0.5:
                continue
            
            # Recent performance
            df1 = await self.data_provider.get_price_history(asset1, class1, 30)
            df2 = await self.data_provider.get_price_history(asset2, class2, 30)
            
            if df1 is None or df2 is None:
                continue
            
            ret1 = (df1['close'].iloc[-1] / df1['close'].iloc[0] - 1) * 100
            ret2 = (df2['close'].iloc[-1] / df2['close'].iloc[0] - 1) * 100
            
            spread = ret1 - ret2
            
            # Large divergence?
            if abs(spread) > 10:  # 10% difference
                if spread > 10:
                    signal = f"SHORT {asset1}, LONG {asset2}"
                    reasoning = f"{asset1} outperformed, expect mean reversion"
                else:
                    signal = f"LONG {asset1}, SHORT {asset2}"
                    reasoning = f"{asset2} outperformed, expect mean reversion"
                
                divergences.append({
                    'pair': f"{asset1}/{asset2}",
                    'historical_correlation': pair.correlation,
                    'asset1_return': ret1,
                    'asset2_return': ret2,
                    'spread': spread,
                    'signal': signal,
                    'reasoning': reasoning,
                    'confidence': min(abs(spread) / 20, 1.0)
                })
        
        divergences.sort(key=lambda x: abs(x['spread']), reverse=True)
        return divergences


class MacroFactorAnalyzer:
    """
    Makro faktorlar tahlili
    - Dollar Index impact
    - Interest rates
    - Inflation
    - Fed policy
    """
    
    def __init__(self, data_provider: MultiMarketDataProvider):
        self.data_provider = data_provider
    
    async def analyze_dollar_impact(self) -> Dict:
        """Dollar indexning boshqa assetlarga ta'siri"""
        lookback = 90
        
        dxy = await self.data_provider.get_price_history('DXY', AssetClass.FOREX, lookback)
        btc = await self.data_provider.get_price_history('BTC', AssetClass.CRYPTO, lookback)
        gld = await self.data_provider.get_price_history('GLD', AssetClass.COMMODITIES, lookback)
        spy = await self.data_provider.get_price_history('SPY', AssetClass.STOCKS, lookback)
        
        if dxy is None:
            return {}
        
        dxy_return = (dxy['close'].iloc[-1] / dxy['close'].iloc[0] - 1) * 100
        
        correlations = {}
        
        for name, df in [('BTC', btc), ('Gold', gld), ('Stocks', spy)]:
            if df is not None:
                common_dates = dxy.index.intersection(df.index)
                dxy_rets = dxy.loc[common_dates, 'close'].pct_change().dropna()
                asset_rets = df.loc[common_dates, 'close'].pct_change().dropna()
                
                corr = dxy_rets.corr(asset_rets)
                correlations[name] = corr
        
        # Dollar strength interpretation
        if dxy_return > 3:
            dollar_trend = "STRONG"
            interpretation = "Kuchli dollar: risky assets pastga, gold pastga"
        elif dxy_return < -3:
            dollar_trend = "WEAK"
            interpretation = "Zaif dollar: risky assets yuqoriga, gold yuqoriga"
        else:
            dollar_trend = "NEUTRAL"
            interpretation = "Dollar neutral: aralash signal"
        
        return {
            'dollar_index_return': dxy_return,
            'dollar_trend': dollar_trend,
            'interpretation': interpretation,
            'correlations': correlations
        }


class PortfolioDiversifier:
    """
    Portfolio diversifikatsiya optimizatori
    - Minimum correlation portfolio
    - Risk parity
    - Max Sharpe with diversification constraint
    """
    
    def __init__(
        self,
        data_provider: MultiMarketDataProvider,
        correlation_analyzer: CorrelationAnalyzer
    ):
        self.data_provider = data_provider
        self.correlation_analyzer = correlation_analyzer
    
    async def build_diversified_portfolio(
        self,
        assets: List[Tuple[str, AssetClass]],
        target_assets: int = 5
    ) -> Dict[str, float]:
        """
        Eng yaxshi diversifikatsiya qilgan portfolio
        Minimum o'rtacha korrelyatsiya
        """
        # Calculate all pairwise correlations
        n = len(assets)
        corr_matrix = await self.correlation_analyzer.build_correlation_matrix(assets)
        
        # Greedy selection: start with highest return asset, add least correlated
        selected_indices = []
        
        # Start with first asset
        selected_indices.append(0)
        
        while len(selected_indices) < min(target_assets, n):
            min_avg_corr = float('inf')
            best_idx = -1
            
            for i in range(n):
                if i in selected_indices:
                    continue
                
                # Average correlation with selected assets
                avg_corr = np.mean([abs(corr_matrix.iloc[i, j]) for j in selected_indices])
                
                if avg_corr < min_avg_corr:
                    min_avg_corr = avg_corr
                    best_idx = i
            
            if best_idx != -1:
                selected_indices.append(best_idx)
        
        # Equal weight for selected assets
        selected_symbols = [assets[i][0] for i in selected_indices]
        weight = 1.0 / len(selected_symbols)
        
        portfolio = {symbol: weight for symbol in selected_symbols}
        
        return portfolio
    
    async def calculate_portfolio_metrics(
        self,
        portfolio: Dict[str, float],
        asset_classes: Dict[str, AssetClass]
    ) -> Dict:
        """Portfolio metrikalarini hisoblash"""
        # Get returns
        returns_data = []
        
        for symbol, weight in portfolio.items():
            asset_class = asset_classes.get(symbol, AssetClass.STOCKS)
            df = await self.data_provider.get_price_history(symbol, asset_class, 90)
            
            if df is not None:
                returns = df['close'].pct_change().dropna()
                weighted_returns = returns * weight
                returns_data.append(weighted_returns)
        
        if not returns_data:
            return {}
        
        # Portfolio returns
        portfolio_returns = pd.concat(returns_data, axis=1).sum(axis=1)
        
        # Metrics
        total_return = (1 + portfolio_returns).prod() - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe = (portfolio_returns.mean() * 252) / (volatility) if volatility > 0 else 0
        max_drawdown = (portfolio_returns.cumsum().cummax() - portfolio_returns.cumsum()).max()
        
        return {
            'total_return': total_return * 100,
            'annual_volatility': volatility * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown * 100
        }


async def main():
    """Test funksiyasi"""
    provider = MultiMarketDataProvider()
    correlation_analyzer = CorrelationAnalyzer(provider)
    
    print("=" * 80)
    print("AI TRADING EVOLUTION - MULTI-MARKET CORRELATION ANALYSIS")
    print("=" * 80)
    print()
    
    # 1. Correlation Matrix
    print("🔗 KORRELYATSIYA MATRIX:")
    print("-" * 80)
    
    assets = [
        ('BTC', AssetClass.CRYPTO),
        ('ETH', AssetClass.CRYPTO),
        ('SPY', AssetClass.STOCKS),
        ('GLD', AssetClass.COMMODITIES),
        ('TLT', AssetClass.BONDS)
    ]
    
    corr_matrix = await correlation_analyzer.build_correlation_matrix(assets)
    print(corr_matrix.round(2))
    print()
    
    # 2. Diversification Pairs
    print("🎯 DIVERSIFIKATSIYA UCHUN ENG YAXSHI JUFTLIKLAR:")
    print("-" * 80)
    
    div_pairs = await correlation_analyzer.find_diversification_pairs(assets, max_correlation=0.4)
    
    for i, pair in enumerate(div_pairs[:5], 1):
        print(f"{i}. {pair.asset1} / {pair.asset2}")
        print(f"   Correlation: {pair.correlation:.3f} ({pair.correlation_strength})")
        print(f"   P-value: {pair.p_value:.4f}")
        print()
    
    # 3. Market Regime
    print("📊 BOZOR REJIMI:")
    print("-" * 80)
    
    regime_detector = RegimeDetector(provider)
    regime = await regime_detector.detect_current_regime()
    
    print(f"Rejim: {regime.regime.value.upper()}")
    print(f"Confidence: {regime.confidence:.1%}")
    print(f"Volatility: {regime.volatility_level}")
    print(f"Risk Assets Return: {regime.risk_assets_performance:.1f}%")
    print(f"Safe Haven Return: {regime.safe_haven_performance:.1f}%")
    print()
    
    # Recommended allocation
    print("TAVSIYA ETILGAN ALLOCATION:")
    allocation = await regime_detector.get_regime_based_allocation()
    for asset_class, weight in allocation.items():
        print(f"  {asset_class.capitalize():15} {weight:.1%}")
    print()
    
    # 4. Cross-Asset Divergence
    print("⚡ CROSS-ASSET DIVERGENCE:")
    print("-" * 80)
    
    cross_asset = CrossAssetStrategy(provider, correlation_analyzer)
    divergences = await cross_asset.detect_cross_asset_divergence()
    
    for i, div in enumerate(divergences[:3], 1):
        print(f"{i}. {div['pair']}")
        print(f"   Historical Corr: {div['historical_correlation']:.2f}")
        print(f"   Recent Spread: {div['spread']:.1f}%")
        print(f"   Signal: {div['signal']}")
        print(f"   Reasoning: {div['reasoning']}")
        print()
    
    # 5. Dollar Impact
    print("💵 DOLLAR INDEX TA'SIRI:")
    print("-" * 80)
    
    macro = MacroFactorAnalyzer(provider)
    dollar_analysis = await macro.analyze_dollar_impact()
    
    if dollar_analysis:
        print(f"Dollar Return: {dollar_analysis['dollar_index_return']:.2f}%")
        print(f"Trend: {dollar_analysis['dollar_trend']}")
        print(f"Interpretation: {dollar_analysis['interpretation']}")
        print()
        print("Correlations with Dollar:")
        for asset, corr in dollar_analysis['correlations'].items():
            print(f"  {asset:10} {corr:+.3f}")
    print()
    
    # 6. Diversified Portfolio
    print("📈 DIVERSIFIKATSIYA QILINGAN PORTFOLIO:")
    print("-" * 80)
    
    diversifier = PortfolioDiversifier(provider, correlation_analyzer)
    
    all_assets = [
        ('BTC', AssetClass.CRYPTO),
        ('ETH', AssetClass.CRYPTO),
        ('SPY', AssetClass.STOCKS),
        ('QQQ', AssetClass.STOCKS),
        ('GLD', AssetClass.COMMODITIES),
        ('USO', AssetClass.COMMODITIES),
        ('TLT', AssetClass.BONDS),
        ('AGG', AssetClass.BONDS)
    ]
    
    portfolio = await diversifier.build_diversified_portfolio(all_assets, target_assets=5)
    
    print("Selected Assets:")
    for symbol, weight in portfolio.items():
        print(f"  {symbol:6} {weight:.1%}")
    print()
    
    # Portfolio metrics
    asset_classes_map = {symbol: asset_class for symbol, asset_class in all_assets}
    metrics = await diversifier.calculate_portfolio_metrics(portfolio, asset_classes_map)
    
    if metrics:
        print("Portfolio Metrics:")
        print(f"  Total Return: {metrics['total_return']:.1f}%")
        print(f"  Volatility: {metrics['annual_volatility']:.1f}%")
        print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown: {metrics['max_drawdown']:.1f}%")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
