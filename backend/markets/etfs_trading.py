"""
AI Trading Evolution - ETFs Trading Module
==========================================

Exchange-Traded Funds (ETFs) savdosi:
- Index tracking ETFs (S&P 500, NASDAQ, Russell 2000)
- Sector ETFs (Technology, Healthcare, Energy, etc.)
- Commodity ETFs (Gold, Oil, Agriculture)
- Bond ETFs
- International ETFs
- Thematic ETFs (AI, Clean Energy, Cybersecurity)
- ETF arbitrage (vs underlying basket)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import numpy as np
import pandas as pd
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETFCategory(Enum):
    """ETF toifalari"""
    INDEX = "index"  # S&P 500, NASDAQ, etc.
    SECTOR = "sector"  # Technology, Healthcare, etc.
    COMMODITY = "commodity"  # Gold, Oil, etc.
    BOND = "bond"  # Government, Corporate bonds
    INTERNATIONAL = "international"  # Emerging markets, Europe, Asia
    THEMATIC = "thematic"  # AI, Clean Energy, Blockchain
    LEVERAGED = "leveraged"  # 2x, 3x leveraged
    INVERSE = "inverse"  # Short ETFs


class SectorType(Enum):
    """Sektor turlari"""
    TECHNOLOGY = "XLK"
    HEALTHCARE = "XLV"
    FINANCIAL = "XLF"
    ENERGY = "XLE"
    CONSUMER_DISCRETIONARY = "XLY"
    CONSUMER_STAPLES = "XLP"
    INDUSTRIALS = "XLI"
    MATERIALS = "XLB"
    UTILITIES = "XLU"
    REAL_ESTATE = "XLRE"
    COMMUNICATION = "XLC"


@dataclass
class ETFQuote:
    """ETF narx ma'lumotlari"""
    ticker: str
    name: str
    category: ETFCategory
    price: float
    nav: float  # Net Asset Value
    volume: int
    aum: float  # Assets Under Management (USD)
    expense_ratio: float  # Yillik xarajat (%)
    dividend_yield: float  # Dividend (%)
    bid: float
    ask: float
    day_high: float
    day_low: float
    open_price: float
    prev_close: float
    inception_date: datetime
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def premium_discount(self) -> float:
        """Premium/Discount to NAV (%)"""
        return ((self.price - self.nav) / self.nav) * 100 if self.nav > 0 else 0
    
    @property
    def spread_pct(self) -> float:
        """Bid-Ask spread (%)"""
        return ((self.ask - self.bid) / self.price) * 100 if self.price > 0 else 0
    
    @property
    def day_change_pct(self) -> float:
        """Kunlik o'zgarish (%)"""
        return ((self.price - self.prev_close) / self.prev_close) * 100 if self.prev_close > 0 else 0


@dataclass
class ETFHolding:
    """ETF tarkibidagi aktiv"""
    ticker: str
    name: str
    weight: float  # Foizda (%)
    shares: int
    market_value: float


@dataclass
class ETFPerformance:
    """ETF performance metriklar"""
    ticker: str
    return_1d: float
    return_1w: float
    return_1m: float
    return_3m: float
    return_ytd: float
    return_1y: float
    volatility: float  # Annualized
    sharpe_ratio: float
    max_drawdown: float
    beta: float  # vs benchmark
    tracking_error: float


class ETFDataProvider:
    """
    ETFs uchun ma'lumot provayderi
    Real API'lar: Alpha Vantage, Polygon.io, ETF Database
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Tuple[datetime, any]] = {}
        self.cache_ttl = 60
        
        # Popular ETFs by category
        self.popular_etfs = {
            ETFCategory.INDEX: {
                'SPY': 'SPDR S&P 500 ETF',
                'QQQ': 'Invesco QQQ (NASDAQ-100)',
                'IWM': 'iShares Russell 2000',
                'DIA': 'SPDR Dow Jones Industrial Average'
            },
            ETFCategory.SECTOR: {
                'XLK': 'Technology Select Sector',
                'XLV': 'Health Care Select Sector',
                'XLF': 'Financial Select Sector',
                'XLE': 'Energy Select Sector',
                'XLY': 'Consumer Discretionary'
            },
            ETFCategory.COMMODITY: {
                'GLD': 'SPDR Gold Shares',
                'USO': 'United States Oil Fund',
                'SLV': 'iShares Silver Trust',
                'DBA': 'Invesco DB Agriculture'
            },
            ETFCategory.BOND: {
                'AGG': 'iShares Core U.S. Aggregate Bond',
                'TLT': 'iShares 20+ Year Treasury Bond',
                'LQD': 'iShares iBoxx Investment Grade Corporate',
                'HYG': 'iShares iBoxx High Yield Corporate'
            },
            ETFCategory.THEMATIC: {
                'ARKK': 'ARK Innovation ETF',
                'ICLN': 'iShares Global Clean Energy',
                'HACK': 'ETFMG Prime Cyber Security',
                'BOTZ': 'Global X Robotics & AI'
            }
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Kesh validligi"""
        if key not in self.cache:
            return False
        timestamp, _ = self.cache[key]
        return (datetime.now() - timestamp).seconds < self.cache_ttl
    
    async def get_etf_quote(self, ticker: str) -> Optional[ETFQuote]:
        """ETF quote olish"""
        cache_key = f"etf_quote_{ticker}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            # Determine category and name
            category = ETFCategory.INDEX
            name = ticker
            
            for cat, etfs in self.popular_etfs.items():
                if ticker in etfs:
                    category = cat
                    name = etfs[ticker]
                    break
            
            # Demo price data
            demo_prices = {
                'SPY': 450.25, 'QQQ': 380.50, 'IWM': 195.30, 'DIA': 350.75,
                'XLK': 185.40, 'XLV': 145.20, 'XLF': 38.90, 'XLE': 85.60,
                'GLD': 182.30, 'USO': 78.40, 'AGG': 101.20, 'TLT': 95.50,
                'ARKK': 48.20, 'ICLN': 22.50, 'HACK': 58.30
            }
            
            base_price = demo_prices.get(ticker, 100.0)
            nav = base_price * np.random.uniform(0.998, 1.002)  # Slight premium/discount
            
            quote = ETFQuote(
                ticker=ticker,
                name=name,
                category=category,
                price=base_price,
                nav=nav,
                volume=np.random.randint(5_000_000, 50_000_000),
                aum=np.random.uniform(5e9, 500e9),
                expense_ratio=np.random.uniform(0.03, 0.75),  # 0.03% - 0.75%
                dividend_yield=np.random.uniform(0, 3),
                bid=base_price * 0.9999,
                ask=base_price * 1.0001,
                day_high=base_price * 1.015,
                day_low=base_price * 0.985,
                open_price=base_price * 0.995,
                prev_close=base_price * np.random.uniform(0.990, 1.010),
                inception_date=datetime.now() - timedelta(days=np.random.randint(365, 7300))
            )
            
            self.cache[cache_key] = (datetime.now(), quote)
            return quote
            
        except Exception as e:
            logger.error(f"ETF quote olishda xato ({ticker}): {e}")
            return None
    
    async def get_etf_holdings(self, ticker: str, top_n: int = 10) -> List[ETFHolding]:
        """ETF tarkibini olish (top holdings)"""
        cache_key = f"etf_holdings_{ticker}_{top_n}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            # Demo holdings
            demo_holdings = {
                'SPY': [
                    ('AAPL', 'Apple Inc.', 7.1),
                    ('MSFT', 'Microsoft Corp.', 6.8),
                    ('AMZN', 'Amazon.com Inc.', 3.2),
                    ('NVDA', 'NVIDIA Corp.', 2.9),
                    ('GOOGL', 'Alphabet Inc.', 2.1),
                    ('META', 'Meta Platforms Inc.', 1.9),
                    ('TSLA', 'Tesla Inc.', 1.7),
                    ('BRK.B', 'Berkshire Hathaway', 1.6),
                    ('UNH', 'UnitedHealth Group', 1.3),
                    ('JNJ', 'Johnson & Johnson', 1.2)
                ],
                'QQQ': [
                    ('AAPL', 'Apple Inc.', 11.5),
                    ('MSFT', 'Microsoft Corp.', 10.2),
                    ('AMZN', 'Amazon.com Inc.', 6.1),
                    ('NVDA', 'NVIDIA Corp.', 5.8),
                    ('META', 'Meta Platforms Inc.', 4.9),
                    ('GOOGL', 'Alphabet Inc. Class A', 3.8),
                    ('GOOG', 'Alphabet Inc. Class C', 3.7),
                    ('TSLA', 'Tesla Inc.', 3.2),
                    ('AVGO', 'Broadcom Inc.', 2.5),
                    ('COST', 'Costco Wholesale', 2.1)
                ],
                'XLK': [
                    ('AAPL', 'Apple Inc.', 22.1),
                    ('MSFT', 'Microsoft Corp.', 21.3),
                    ('NVDA', 'NVIDIA Corp.', 9.2),
                    ('AVGO', 'Broadcom Inc.', 4.8),
                    ('CRM', 'Salesforce Inc.', 3.5),
                    ('ORCL', 'Oracle Corp.', 3.2),
                    ('CSCO', 'Cisco Systems', 2.9),
                    ('ACN', 'Accenture plc', 2.7),
                    ('AMD', 'Advanced Micro Devices', 2.4),
                    ('INTC', 'Intel Corp.', 2.1)
                ]
            }
            
            if ticker in demo_holdings:
                holdings_data = demo_holdings[ticker]
            else:
                # Generic holdings
                holdings_data = [
                    (f'HOLD{i}', f'Holding {i}', np.random.uniform(1, 10))
                    for i in range(1, top_n + 1)
                ]
            
            holdings = []
            for symbol, name, weight in holdings_data[:top_n]:
                holding = ETFHolding(
                    ticker=symbol,
                    name=name,
                    weight=weight,
                    shares=np.random.randint(1_000_000, 50_000_000),
                    market_value=np.random.uniform(1e9, 50e9)
                )
                holdings.append(holding)
            
            self.cache[cache_key] = (datetime.now(), holdings)
            return holdings
            
        except Exception as e:
            logger.error(f"ETF holdings olishda xato ({ticker}): {e}")
            return []
    
    async def get_etf_performance(self, ticker: str) -> Optional[ETFPerformance]:
        """ETF performance metrikalarini olish"""
        cache_key = f"etf_performance_{ticker}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            # Demo performance data
            performance = ETFPerformance(
                ticker=ticker,
                return_1d=np.random.uniform(-2, 2),
                return_1w=np.random.uniform(-3, 3),
                return_1m=np.random.uniform(-5, 5),
                return_3m=np.random.uniform(-8, 12),
                return_ytd=np.random.uniform(-10, 20),
                return_1y=np.random.uniform(-15, 30),
                volatility=np.random.uniform(10, 30),  # Annualized %
                sharpe_ratio=np.random.uniform(0.5, 2.0),
                max_drawdown=np.random.uniform(-30, -5),
                beta=np.random.uniform(0.8, 1.2),
                tracking_error=np.random.uniform(0.1, 1.0)
            )
            
            self.cache[cache_key] = (datetime.now(), performance)
            return performance
            
        except Exception as e:
            logger.error(f"ETF performance olishda xato ({ticker}): {e}")
            return None
    
    def get_etfs_by_category(self, category: ETFCategory) -> Dict[str, str]:
        """Kategoriya bo'yicha ETFlar"""
        return self.popular_etfs.get(category, {})


class ETFScreener:
    """
    ETFlarni filterlash va saralash
    - Performance-based
    - Cost-efficiency
    - Liquidity
    """
    
    def __init__(self, data_provider: ETFDataProvider):
        self.data_provider = data_provider
    
    async def screen_by_performance(
        self,
        tickers: List[str],
        min_return_1y: float = 10.0,
        min_sharpe: float = 1.0
    ) -> List[Tuple[str, float]]:
        """Performance bo'yicha filterlash"""
        results = []
        
        for ticker in tickers:
            perf = await self.data_provider.get_etf_performance(ticker)
            
            if not perf:
                continue
            
            if perf.return_1y >= min_return_1y and perf.sharpe_ratio >= min_sharpe:
                score = perf.return_1y * perf.sharpe_ratio / 10
                results.append((ticker, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    async def screen_by_cost(
        self,
        tickers: List[str],
        max_expense_ratio: float = 0.20
    ) -> List[Tuple[str, float]]:
        """Xarajat nisbati bo'yicha filterlash"""
        results = []
        
        for ticker in tickers:
            quote = await self.data_provider.get_etf_quote(ticker)
            
            if not quote:
                continue
            
            if quote.expense_ratio <= max_expense_ratio:
                # Score: lower expense ratio = better
                score = (max_expense_ratio - quote.expense_ratio) / max_expense_ratio
                results.append((ticker, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    async def screen_by_liquidity(
        self,
        tickers: List[str],
        min_volume: int = 1_000_000,
        max_spread_pct: float = 0.10
    ) -> List[Tuple[str, float]]:
        """Likvidlik bo'yicha filterlash"""
        results = []
        
        for ticker in tickers:
            quote = await self.data_provider.get_etf_quote(ticker)
            
            if not quote:
                continue
            
            if quote.volume >= min_volume and quote.spread_pct <= max_spread_pct:
                # Score: higher volume + tighter spread = better
                volume_score = min(quote.volume / 10_000_000, 1.0)
                spread_score = 1 - (quote.spread_pct / max_spread_pct)
                score = (volume_score + spread_score) / 2
                results.append((ticker, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results


class ETFArbitrageDetector:
    """
    ETF arbitrage strategiyasi
    - Premium/Discount to NAV arbitrage
    - Pair trading with underlying index
    """
    
    def __init__(self, data_provider: ETFDataProvider):
        self.data_provider = data_provider
    
    async def detect_nav_arbitrage(
        self,
        tickers: List[str],
        threshold: float = 0.5  # 0.5% premium/discount
    ) -> List[Dict]:
        """
        Premium/Discount to NAV arbitrage
        Agar ETF NAV dan ancha yuqori/past - arbitraj imkoniyati
        """
        opportunities = []
        
        for ticker in tickers:
            quote = await self.data_provider.get_etf_quote(ticker)
            
            if not quote:
                continue
            
            premium_discount = quote.premium_discount
            
            if abs(premium_discount) > threshold:
                if premium_discount > threshold:
                    signal = 'PREMIUM'
                    action = 'SELL_ETF_BUY_BASKET'
                    description = f'{ticker} NAV dan {premium_discount:.2f}% yuqori'
                else:
                    signal = 'DISCOUNT'
                    action = 'BUY_ETF_SELL_BASKET'
                    description = f'{ticker} NAV dan {abs(premium_discount):.2f}% past'
                
                opportunities.append({
                    'ticker': ticker,
                    'name': quote.name,
                    'price': quote.price,
                    'nav': quote.nav,
                    'premium_discount': premium_discount,
                    'signal': signal,
                    'action': action,
                    'description': description,
                    'confidence': min(abs(premium_discount) / (threshold * 2), 1.0)
                })
        
        opportunities.sort(key=lambda x: abs(x['premium_discount']), reverse=True)
        return opportunities


class SectorRotationETFStrategy:
    """
    Sector Rotation strategiyasi ETFlar orqali
    Eng yaxshi sektorlarni tanlash va rotatsiya qilish
    """
    
    def __init__(self, data_provider: ETFDataProvider):
        self.data_provider = data_provider
    
    async def analyze_sector_momentum(self) -> List[Dict]:
        """Sektor momentum tahlili"""
        sector_etfs = self.data_provider.get_etfs_by_category(ETFCategory.SECTOR)
        
        results = []
        
        for ticker, name in sector_etfs.items():
            perf = await self.data_provider.get_etf_performance(ticker)
            quote = await self.data_provider.get_etf_quote(ticker)
            
            if not perf or not quote:
                continue
            
            # Momentum score: weighted average of returns
            momentum_score = (
                perf.return_1m * 0.3 +
                perf.return_3m * 0.4 +
                perf.return_ytd * 0.3
            )
            
            # Risk-adjusted momentum
            risk_adjusted_momentum = momentum_score / perf.volatility if perf.volatility > 0 else 0
            
            results.append({
                'ticker': ticker,
                'name': name,
                'momentum_score': momentum_score,
                'risk_adjusted_momentum': risk_adjusted_momentum,
                'return_1m': perf.return_1m,
                'return_3m': perf.return_3m,
                'return_ytd': perf.return_ytd,
                'volatility': perf.volatility,
                'sharpe_ratio': perf.sharpe_ratio
            })
        
        # Sort by risk-adjusted momentum
        results.sort(key=lambda x: x['risk_adjusted_momentum'], reverse=True)
        return results
    
    async def get_rotation_signals(self) -> List[Dict]:
        """Rotation signallarini olish"""
        momentum_analysis = await self.analyze_sector_momentum()
        
        if not momentum_analysis:
            return []
        
        signals = []
        
        # Top 3 - OVERWEIGHT
        for sector in momentum_analysis[:3]:
            signals.append({
                'ticker': sector['ticker'],
                'name': sector['name'],
                'action': 'OVERWEIGHT',
                'momentum_score': sector['momentum_score'],
                'risk_adjusted_momentum': sector['risk_adjusted_momentum'],
                'reasoning': f"Kuchli momentum ({sector['return_3m']:.1f}% 3M return)"
            })
        
        # Bottom 3 - UNDERWEIGHT
        for sector in momentum_analysis[-3:]:
            signals.append({
                'ticker': sector['ticker'],
                'name': sector['name'],
                'action': 'UNDERWEIGHT',
                'momentum_score': sector['momentum_score'],
                'risk_adjusted_momentum': sector['risk_adjusted_momentum'],
                'reasoning': f"Zaif momentum ({sector['return_3m']:.1f}% 3M return)"
            })
        
        return signals


class ThematicETFAnalyzer:
    """
    Thematic ETFlar tahlili
    AI, Clean Energy, Cybersecurity kabi tematik ETFlar
    """
    
    def __init__(self, data_provider: ETFDataProvider):
        self.data_provider = data_provider
    
    async def analyze_theme_performance(self) -> List[Dict]:
        """Tematik ETFlar performance"""
        thematic_etfs = self.data_provider.get_etfs_by_category(ETFCategory.THEMATIC)
        
        results = []
        
        for ticker, name in thematic_etfs.items():
            quote = await self.data_provider.get_etf_quote(ticker)
            perf = await self.data_provider.get_etf_performance(ticker)
            
            if not quote or not perf:
                continue
            
            results.append({
                'ticker': ticker,
                'name': name,
                'price': quote.price,
                'return_1y': perf.return_1y,
                'volatility': perf.volatility,
                'sharpe_ratio': perf.sharpe_ratio,
                'max_drawdown': perf.max_drawdown,
                'expense_ratio': quote.expense_ratio,
                'aum': quote.aum
            })
        
        results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
        return results


class ETFPortfolioOptimizer:
    """
    ETF portfolio optimallashtirish
    - Modern Portfolio Theory (MPT)
    - Risk parity
    - Equal weight
    """
    
    def __init__(self, data_provider: ETFDataProvider):
        self.data_provider = data_provider
    
    async def optimize_risk_parity(
        self,
        tickers: List[str]
    ) -> Dict[str, float]:
        """
        Risk Parity allocation
        Har bir ETFning risk contributioni teng bo'lishi
        """
        # Get volatilities
        volatilities = {}
        
        for ticker in tickers:
            perf = await self.data_provider.get_etf_performance(ticker)
            if perf:
                volatilities[ticker] = perf.volatility
        
        if not volatilities:
            return {}
        
        # Inverse volatility weighting
        inv_vol = {k: 1/v for k, v in volatilities.items()}
        total_inv_vol = sum(inv_vol.values())
        
        weights = {k: v/total_inv_vol for k, v in inv_vol.items()}
        
        return weights
    
    async def optimize_max_sharpe(
        self,
        tickers: List[str]
    ) -> Dict[str, float]:
        """
        Max Sharpe Ratio portfolio
        Sharpe ratio eng yuqori bo'lgan kombinatsiya
        """
        # Simplified: weight by Sharpe ratio
        sharpe_ratios = {}
        
        for ticker in tickers:
            perf = await self.data_provider.get_etf_performance(ticker)
            if perf and perf.sharpe_ratio > 0:
                sharpe_ratios[ticker] = perf.sharpe_ratio
        
        if not sharpe_ratios:
            return {}
        
        total_sharpe = sum(sharpe_ratios.values())
        weights = {k: v/total_sharpe for k, v in sharpe_ratios.items()}
        
        return weights
    
    def equal_weight(self, tickers: List[str]) -> Dict[str, float]:
        """Equal weight allocation"""
        weight = 1.0 / len(tickers)
        return {ticker: weight for ticker in tickers}


async def main():
    """Test funksiyasi"""
    api_keys = {
        'alpha_vantage': 'YOUR_API_KEY'
    }
    
    async with ETFDataProvider(api_keys) as provider:
        print("=" * 80)
        print("AI TRADING EVOLUTION - ETFs TRADING MODULE")
        print("=" * 80)
        print()
        
        # 1. Index ETFs
        print("📊 INDEX ETFs:")
        print("-" * 80)
        index_etfs = provider.get_etfs_by_category(ETFCategory.INDEX)
        
        for ticker, name in list(index_etfs.items())[:4]:
            quote = await provider.get_etf_quote(ticker)
            if quote:
                print(f"{ticker:6} {name:35} ${quote.price:7.2f}  "
                      f"Vol: {quote.volume:,}  "
                      f"Exp: {quote.expense_ratio:.2f}%")
        print()
        
        # 2. ETF Holdings
        print("🏢 ETF HOLDINGS (SPY - Top 5):")
        print("-" * 80)
        holdings = await provider.get_etf_holdings('SPY', top_n=5)
        
        for holding in holdings:
            print(f"{holding.ticker:6} {holding.name:25} {holding.weight:5.1f}%")
        print()
        
        # 3. Sector Rotation
        print("🔄 SEKTOR ROTATION STRATEGIYASI:")
        print("-" * 80)
        rotation_strategy = SectorRotationETFStrategy(provider)
        rotation_signals = await rotation_strategy.get_rotation_signals()
        
        for signal in rotation_signals[:5]:
            print(f"{signal['ticker']:6} {signal['action']:12} - {signal['reasoning']}")
        print()
        
        # 4. NAV Arbitrage
        print("💰 NAV ARBITRAGE IMKONIYATLARI:")
        print("-" * 80)
        arbitrage = ETFArbitrageDetector(provider)
        
        all_etfs = []
        for cat in [ETFCategory.INDEX, ETFCategory.SECTOR, ETFCategory.COMMODITY]:
            all_etfs.extend(list(provider.get_etfs_by_category(cat).keys())[:3])
        
        arb_opportunities = await arbitrage.detect_nav_arbitrage(all_etfs)
        
        for i, opp in enumerate(arb_opportunities[:3], 1):
            print(f"{i}. {opp['ticker']} - {opp['signal']}")
            print(f"   Price: ${opp['price']:.2f}, NAV: ${opp['nav']:.2f}")
            print(f"   Premium/Discount: {opp['premium_discount']:+.2f}%")
            print(f"   Action: {opp['action']}")
            print(f"   Confidence: {opp['confidence']:.1%}")
            print()
        
        # 5. Thematic ETFs
        print("🚀 TEMATIK ETFs PERFORMANCE:")
        print("-" * 80)
        thematic = ThematicETFAnalyzer(provider)
        theme_perf = await thematic.analyze_theme_performance()
        
        for i, theme in enumerate(theme_perf[:3], 1):
            print(f"{i}. {theme['ticker']} - {theme['name']}")
            print(f"   1Y Return: {theme['return_1y']:.1f}%")
            print(f"   Sharpe: {theme['sharpe_ratio']:.2f}")
            print(f"   Volatility: {theme['volatility']:.1f}%")
            print(f"   Max DD: {theme['max_drawdown']:.1f}%")
            print()
        
        # 6. Portfolio Optimization
        print("📈 PORTFOLIO OPTIMALLASHTIRISH:")
        print("-" * 80)
        optimizer = ETFPortfolioOptimizer(provider)
        
        portfolio_etfs = ['SPY', 'QQQ', 'IWM', 'GLD', 'AGG']
        
        print("Risk Parity Allocation:")
        risk_parity = await optimizer.optimize_risk_parity(portfolio_etfs)
        for ticker, weight in risk_parity.items():
            print(f"  {ticker:6} {weight:6.1%}")
        
        print()
        print("Max Sharpe Ratio Allocation:")
        max_sharpe = await optimizer.optimize_max_sharpe(portfolio_etfs)
        for ticker, weight in max_sharpe.items():
            print(f"  {ticker:6} {weight:6.1%}")
        
        print()
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
