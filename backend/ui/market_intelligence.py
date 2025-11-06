"""
Market Intelligence Backend
===========================

Comprehensive market analysis va intelligence tools.
Heatmaps, correlation matrices, market scanner, sentiment analysis.

Features:
- Market heatmaps (get_market_heatmap)
- Correlation analysis (calculate_correlation_matrix)
- Market scanner (scan_market)
- Market sentiment analysis (get_market_sentiment)
- Market overview (get_market_overview)
- Sector rotation analysis (get_sector_rotation)
- Volume profile (get_volume_profile)
- Order flow imbalance (get_order_flow_imbalance)
- Market depth analysis (get_market_depth_analysis)
- Momentum indicators (get_momentum_indicators)
- Risk metrics (get_risk_metrics)
- Top movers (get_top_movers)
- Advanced analytics (get_advanced_analytics)

Classes:
- MarketSector: Market sector enum (CRYPTO, STOCKS, FOREX, COMMODITIES, BONDS)
- ScannerCondition: Scanner condition enum (PRICE_ABOVE, PRICE_BELOW, VOLUME_SPIKE, etc.)
- MarketData: Market data for a symbol
- CorrelationMatrix: Correlation matrix result
- ScannerResult: Market scanner result
- MarketIntelligence: Main market intelligence system
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from enum import Enum


class MarketSector(Enum):
    """Market sector enum"""
    CRYPTO = "crypto"
    STOCKS = "stocks"
    FOREX = "forex"
    COMMODITIES = "commodities"
    BONDS = "bonds"


class ScannerCondition(Enum):
    """Scanner condition enum"""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    VOLUME_SPIKE = "volume_spike"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"
    BREAKOUT = "breakout"
    SUPPORT_BOUNCE = "support_bounce"
    RESISTANCE_REJECT = "resistance_reject"


@dataclass
class MarketData:
    """Market data for a symbol"""
    symbol: str
    sector: MarketSector
    price: float
    change_24h: float
    change_7d: float
    change_30d: float
    volume_24h: float
    volume_avg: float
    market_cap: float
    
    # Technical indicators
    rsi: float
    macd: float
    ma_20: float
    ma_50: float
    ma_200: float
    
    # Volatility
    atr: float
    bollinger_upper: float
    bollinger_lower: float
    
    last_update: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'sector': self.sector.value,
            'price': self.price,
            'change_24h': self.change_24h,
            'change_7d': self.change_7d,
            'change_30d': self.change_30d,
            'volume_24h': self.volume_24h,
            'volume_avg': self.volume_avg,
            'market_cap': self.market_cap,
            'rsi': self.rsi,
            'macd': self.macd,
            'ma_20': self.ma_20,
            'ma_50': self.ma_50,
            'ma_200': self.ma_200,
            'atr': self.atr,
            'bollinger_upper': self.bollinger_upper,
            'bollinger_lower': self.bollinger_lower,
            'last_update': self.last_update.isoformat()
        }


@dataclass
class CorrelationMatrix:
    """Correlation matrix"""
    symbols: List[str]
    matrix: List[List[float]]
    period: str
    calculated_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbols': self.symbols,
            'matrix': self.matrix,
            'period': self.period,
            'calculated_at': self.calculated_at.isoformat()
        }


@dataclass
class ScannerResult:
    """Market scanner result"""
    symbol: str
    conditions_met: List[str]
    price: float
    volume: float
    indicators: Dict[str, float]
    score: float
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'conditions_met': self.conditions_met,
            'price': self.price,
            'volume': self.volume,
            'indicators': self.indicators,
            'score': self.score,
            'timestamp': self.timestamp.isoformat()
        }


class MarketIntelligence:
    """
    Market Intelligence System
    
    Provides market analysis tools including heatmaps,
    correlation matrices, and market scanning.
    """
    
    def __init__(self):
        self.market_data: Dict[str, MarketData] = {}
        self.price_history: Dict[str, List[Dict]] = {}
        
        # Initialize sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize sample market data"""
        symbols = [
            ('BTC/USDT', MarketSector.CRYPTO),
            ('ETH/USDT', MarketSector.CRYPTO),
            ('SOL/USDT', MarketSector.CRYPTO),
            ('AAPL', MarketSector.STOCKS),
            ('GOOGL', MarketSector.STOCKS),
            ('MSFT', MarketSector.STOCKS),
            ('EUR/USD', MarketSector.FOREX),
            ('GBP/USD', MarketSector.FOREX),
            ('GOLD', MarketSector.COMMODITIES),
            ('OIL', MarketSector.COMMODITIES)
        ]
        
        for symbol, sector in symbols:
            price = np.random.uniform(50, 50000)
            
            self.market_data[symbol] = MarketData(
                symbol=symbol,
                sector=sector,
                price=price,
                change_24h=np.random.uniform(-0.1, 0.1),
                change_7d=np.random.uniform(-0.2, 0.2),
                change_30d=np.random.uniform(-0.3, 0.3),
                volume_24h=np.random.uniform(1e6, 1e9),
                volume_avg=np.random.uniform(1e6, 1e9),
                market_cap=np.random.uniform(1e8, 1e12),
                rsi=np.random.uniform(20, 80),
                macd=np.random.uniform(-10, 10),
                ma_20=price * np.random.uniform(0.95, 1.05),
                ma_50=price * np.random.uniform(0.90, 1.10),
                ma_200=price * np.random.uniform(0.80, 1.20),
                atr=price * np.random.uniform(0.01, 0.05),
                bollinger_upper=price * 1.02,
                bollinger_lower=price * 0.98,
                last_update=datetime.now()
            )
            
            # Generate price history
            self.price_history[symbol] = []
            for i in range(100):
                date = datetime.now() - timedelta(days=100-i)
                self.price_history[symbol].append({
                    'date': date.isoformat(),
                    'price': price * (1 + np.random.normal(0, 0.02))
                })
    
    async def get_market_heatmap(
        self,
        sector: Optional[MarketSector] = None,
        metric: str = "change_24h"
    ) -> Dict[str, Any]:
        """
        Generate market heatmap
        
        Args:
            sector: Filter by sector
            metric: Metric to display (change_24h, volume_24h, etc.)
            
        Returns:
            Heatmap data
        """
        data = list(self.market_data.values())
        
        if sector:
            data = [d for d in data if d.sector == sector]
        
        heatmap_data = []
        
        for item in data:
            value = getattr(item, metric, 0)
            
            heatmap_data.append({
                'symbol': item.symbol,
                'sector': item.sector.value,
                'value': value,
                'price': item.price,
                'volume': item.volume_24h,
                'market_cap': item.market_cap
            })
        
        # Sort by absolute value
        heatmap_data.sort(key=lambda x: abs(x['value']), reverse=True)
        
        return {
            'metric': metric,
            'sector': sector.value if sector else 'all',
            'data': heatmap_data,
            'generated_at': datetime.now().isoformat()
        }
    
    async def calculate_correlation_matrix(
        self,
        symbols: Optional[List[str]] = None,
        period: str = "30d"
    ) -> CorrelationMatrix:
        """
        Calculate correlation matrix between symbols
        
        Args:
            symbols: List of symbols to correlate
            period: Time period for correlation
            
        Returns:
            CorrelationMatrix
        """
        if symbols is None:
            symbols = list(self.market_data.keys())
        
        # Filter valid symbols
        symbols = [s for s in symbols if s in self.price_history]
        
        if len(symbols) < 2:
            raise ValueError("Need at least 2 symbols for correlation")
        
        # Calculate period in days
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        else:
            days = 30
        
        # Get price data
        price_data = {}
        for symbol in symbols:
            history = self.price_history.get(symbol, [])
            prices = [h['price'] for h in history[-days:]]
            
            if len(prices) >= days:
                price_data[symbol] = prices
        
        # Calculate returns
        returns_data = {}
        for symbol, prices in price_data.items():
            returns = [
                (prices[i] - prices[i-1]) / prices[i-1]
                for i in range(1, len(prices))
            ]
            returns_data[symbol] = returns
        
        # Build correlation matrix
        symbols_list = list(returns_data.keys())
        n = len(symbols_list)
        
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    returns_i = returns_data[symbols_list[i]]
                    returns_j = returns_data[symbols_list[j]]
                    
                    # Pearson correlation
                    correlation = np.corrcoef(returns_i, returns_j)[0, 1]
                    matrix[i][j] = correlation
        
        return CorrelationMatrix(
            symbols=symbols_list,
            matrix=matrix,
            period=period,
            calculated_at=datetime.now()
        )
    
    async def scan_market(
        self,
        conditions: List[ScannerCondition],
        sector: Optional[MarketSector] = None,
        min_volume: Optional[float] = None
    ) -> List[ScannerResult]:
        """
        Scan market for opportunities
        
        Args:
            conditions: Scanner conditions to check
            sector: Filter by sector
            min_volume: Minimum volume filter
            
        Returns:
            List of scanner results
        """
        data = list(self.market_data.values())
        
        if sector:
            data = [d for d in data if d.sector == sector]
        
        if min_volume:
            data = [d for d in data if d.volume_24h >= min_volume]
        
        results = []
        
        for item in data:
            conditions_met = []
            score = 0
            
            for condition in conditions:
                if self._check_condition(item, condition):
                    conditions_met.append(condition.value)
                    score += 1
            
            if conditions_met:
                result = ScannerResult(
                    symbol=item.symbol,
                    conditions_met=conditions_met,
                    price=item.price,
                    volume=item.volume_24h,
                    indicators={
                        'rsi': item.rsi,
                        'macd': item.macd,
                        'change_24h': item.change_24h
                    },
                    score=score / len(conditions),
                    timestamp=datetime.now()
                )
                results.append(result)
        
        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results
    
    def _check_condition(
        self,
        data: MarketData,
        condition: ScannerCondition
    ) -> bool:
        """Check if market data meets scanner condition"""
        if condition == ScannerCondition.RSI_OVERBOUGHT:
            return data.rsi > 70
        
        elif condition == ScannerCondition.RSI_OVERSOLD:
            return data.rsi < 30
        
        elif condition == ScannerCondition.VOLUME_SPIKE:
            return data.volume_24h > data.volume_avg * 2
        
        elif condition == ScannerCondition.BREAKOUT:
            return data.price > data.ma_50 and data.price > data.bollinger_upper
        
        elif condition == ScannerCondition.SUPPORT_BOUNCE:
            return data.price < data.ma_20 and data.rsi < 40
        
        elif condition == ScannerCondition.RESISTANCE_REJECT:
            return data.price > data.ma_50 and data.rsi > 65
        
        elif condition == ScannerCondition.PRICE_ABOVE:
            return data.price > data.ma_200
        
        elif condition == ScannerCondition.PRICE_BELOW:
            return data.price < data.ma_200
        
        return False
    
    async def get_sector_rotation(self) -> Dict[str, Any]:
        """
        Analyze sector rotation
        
        Returns:
            Sector rotation analysis
        """
        sectors = {}
        
        for data in self.market_data.values():
            sector = data.sector.value
            
            if sector not in sectors:
                sectors[sector] = {
                    'avg_change_24h': [],
                    'avg_change_7d': [],
                    'total_volume': 0,
                    'count': 0
                }
            
            sectors[sector]['avg_change_24h'].append(data.change_24h)
            sectors[sector]['avg_change_7d'].append(data.change_7d)
            sectors[sector]['total_volume'] += data.volume_24h
            sectors[sector]['count'] += 1
        
        rotation_data = []
        
        for sector, metrics in sectors.items():
            rotation_data.append({
                'sector': sector,
                'avg_change_24h': np.mean(metrics['avg_change_24h']),
                'avg_change_7d': np.mean(metrics['avg_change_7d']),
                'momentum': np.mean(metrics['avg_change_7d']) - np.mean(metrics['avg_change_24h']),
                'total_volume': metrics['total_volume'],
                'num_symbols': metrics['count']
            })
        
        # Sort by momentum
        rotation_data.sort(key=lambda x: x['momentum'], reverse=True)
        
        return {
            'sectors': rotation_data,
            'top_sector': rotation_data[0]['sector'] if rotation_data else None,
            'bottom_sector': rotation_data[-1]['sector'] if rotation_data else None,
            'calculated_at': datetime.now().isoformat()
        }
    
    async def get_volume_profile(
        self,
        symbol: str,
        period: str = "24h"
    ) -> Dict[str, Any]:
        """
        Get volume profile for a symbol
        
        Args:
            symbol: Trading symbol
            period: Time period
            
        Returns:
            Volume profile data
        """
        if symbol not in self.price_history:
            return {'error': 'Symbol not found'}
        
        # Get price history
        history = self.price_history[symbol]
        
        if period == "24h":
            history = history[-24:]
        elif period == "7d":
            history = history[-168:]
        elif period == "30d":
            history = history[-720:]
        
        prices = [h['price'] for h in history]
        
        # Calculate price levels
        price_min = min(prices)
        price_max = max(prices)
        
        # Create price bins
        num_bins = 20
        bin_size = (price_max - price_min) / num_bins
        
        bins = []
        for i in range(num_bins):
            price_level = price_min + i * bin_size
            
            # Count volume at this price level
            volume = sum(
                np.random.uniform(1000, 10000)  # Simulated volume
                for p in prices
                if price_level <= p < price_level + bin_size
            )
            
            bins.append({
                'price_level': price_level,
                'volume': volume,
                'percentage': 0  # Will calculate after
            })
        
        # Calculate percentages
        total_volume = sum(b['volume'] for b in bins)
        for bin_data in bins:
            bin_data['percentage'] = bin_data['volume'] / total_volume if total_volume > 0 else 0
        
        # Find POC (Point of Control) - highest volume level
        poc = max(bins, key=lambda b: b['volume'])
        
        return {
            'symbol': symbol,
            'period': period,
            'bins': bins,
            'poc': poc['price_level'],
            'value_area_high': price_max * 0.85,
            'value_area_low': price_min * 1.15,
            'generated_at': datetime.now().isoformat()
        }
    
    async def get_order_flow_imbalance(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Calculate order flow imbalance
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Order flow imbalance data
        """
        # Simulate order flow data
        buy_volume = np.random.uniform(1e6, 1e7)
        sell_volume = np.random.uniform(1e6, 1e7)
        
        total_volume = buy_volume + sell_volume
        imbalance = (buy_volume - sell_volume) / total_volume
        
        # Simulate large orders
        large_orders = []
        for i in range(5):
            large_orders.append({
                'side': np.random.choice(['buy', 'sell']),
                'size': np.random.uniform(1e5, 1e6),
                'price': np.random.uniform(45000, 55000),
                'timestamp': (datetime.now() - timedelta(minutes=np.random.randint(1, 60))).isoformat()
            })
        
        return {
            'symbol': symbol,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'imbalance': imbalance,
            'imbalance_percent': imbalance * 100,
            'delta': buy_volume - sell_volume,
            'large_orders': large_orders,
            'calculated_at': datetime.now().isoformat()
        }
    
    async def get_top_movers(
        self,
        period: str = "24h",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get top movers (gainers and losers)
        
        Args:
            period: Time period
            limit: Number of results
            
        Returns:
            Top movers data
        """
        data = list(self.market_data.values())
        
        # Select metric based on period
        if period == "24h":
            metric = 'change_24h'
        elif period == "7d":
            metric = 'change_7d'
        elif period == "30d":
            metric = 'change_30d'
        else:
            metric = 'change_24h'
        
        # Sort by change
        data.sort(key=lambda d: getattr(d, metric), reverse=True)
        
        gainers = [
            {
                'symbol': d.symbol,
                'change': getattr(d, metric),
                'price': d.price,
                'volume': d.volume_24h
            }
            for d in data[:limit]
        ]
        
        losers = [
            {
                'symbol': d.symbol,
                'change': getattr(d, metric),
                'price': d.price,
                'volume': d.volume_24h
            }
            for d in data[-limit:]
        ]
        
        return {
            'period': period,
            'gainers': gainers,
            'losers': losers,
            'generated_at': datetime.now().isoformat()
        }
    
    async def get_market_sentiment(self) -> Dict[str, Any]:
        """Get detailed market sentiment analysis"""
        data = list(self.market_data.values())
        
        # Calculate sentiment indicators
        total_symbols = len(data)
        
        # Price action sentiment
        gainers_24h = sum(1 for d in data if d.change_24h > 0)
        losers_24h = total_symbols - gainers_24h
        
        # Technical sentiment (RSI based)
        oversold_count = sum(1 for d in data if d.rsi < 30)
        overbought_count = sum(1 for d in data if d.rsi > 70)
        
        # Volume sentiment
        high_volume_count = sum(1 for d in data if d.volume_24h > d.volume_avg * 1.5)
        
        # Fear & Greed Index components
        price_momentum = np.mean([d.change_24h for d in data])
        volume_momentum = np.mean([d.volume_24h / d.volume_avg for d in data])
        volatility = np.mean([d.atr / d.price for d in data])
        
        # Calculate composite sentiment score (0-100)
        fear_greed_components = {
            'price_momentum': max(0, min(100, 50 + price_momentum * 500)),
            'volume_momentum': max(0, min(100, 50 + (volume_momentum - 1) * 100)),
            'volatility': max(0, min(100, 50 - volatility * 2000)),
            'oversold_bullish': max(0, min(100, 50 + (oversold_count / total_symbols - 0.3) * 200)),
            'overbought_bearish': max(0, min(100, 50 + (overbought_count / total_symbols - 0.3) * 200))
        }
        
        fear_greed_index = np.mean(list(fear_greed_components.values()))
        
        # Sentiment classification
        if fear_greed_index >= 75:
            sentiment_label = "Extreme Greed"
            action = "Consider taking profits"
        elif fear_greed_index >= 55:
            sentiment_label = "Greed"
            action = "Stay cautious"
        elif fear_greed_index >= 45:
            sentiment_label = "Neutral"
            action = "Hold current position"
        elif fear_greed_index >= 25:
            sentiment_label = "Fear"
            action = "Consider buying opportunities"
        else:
            sentiment_label = "Extreme Fear"
            action = "Strong buying opportunity"
        
        # Sector sentiment breakdown
        sector_sentiment = {}
        for sector in MarketSector:
            sector_data = [d for d in data if d.sector == sector]
            if sector_data:
                sector_avg_change = np.mean([d.change_24h for d in sector_data])
                sector_sentiment[sector.value] = {
                    'change_24h': sector_avg_change,
                    'sentiment': 'bullish' if sector_avg_change > 0 else 'bearish',
                    'count': len(sector_data)
                }
        
        return {
            'fear_greed_index': round(fear_greed_index, 2),
            'sentiment_label': sentiment_label,
            'action': action,
            'components': fear_greed_components,
            'overview': {
                'gainers_24h': gainers_24h,
                'losers_24h': losers_24h,
                'advance_decline_ratio': gainers_24h / losers_24h if losers_24h > 0 else float('inf'),
                'high_volume_count': high_volume_count,
                'oversold_count': oversold_count,
                'overbought_count': overbought_count
            },
            'sector_sentiment': sector_sentiment,
            'volatility_index': np.mean([d.atr / d.price * 100 for d in data]),
            'analyzed_at': datetime.now().isoformat()
        }
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive market overview"""
        total_symbols = len(self.market_data)
        
        gainers = sum(1 for d in self.market_data.values() if d.change_24h > 0)
        losers = total_symbols - gainers
        
        avg_change = np.mean([d.change_24h for d in self.market_data.values()])
        total_volume = sum(d.volume_24h for d in self.market_data.values())
        
        # Advanced metrics
        median_change = np.median([d.change_24h for d in self.market_data.values()])
        volatility = np.std([d.change_24h for d in self.market_data.values()])
        avg_volume = np.mean([d.volume_24h for d in self.market_data.values()])
        
        # Market breadth (percentage of stocks above key moving averages)
        above_ma20 = sum(1 for d in self.market_data.values() if d.price > d.ma_20) / total_symbols
        above_ma50 = sum(1 for d in self.market_data.values() if d.price > d.ma_50) / total_symbols
        above_ma200 = sum(1 for d in self.market_data.values() if d.price > d.ma_200) / total_symbols
        
        # Market sentiment
        if avg_change > 0.02:
            sentiment = "bullish"
        elif avg_change < -0.02:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        # VIX-style volatility index
        vix_like = volatility * 100
        
        return {
            'total_symbols': total_symbols,
            'gainers': gainers,
            'losers': losers,
            'avg_change_24h': avg_change,
            'median_change_24h': median_change,
            'volatility': volatility,
            'total_volume_24h': total_volume,
            'avg_volume': avg_volume,
            'sentiment': sentiment,
            'fear_greed_index': np.random.randint(0, 100),
            'volatility_index': vix_like,
            'market_breadth': {
                'above_ma20_pct': above_ma20,
                'above_ma50_pct': above_ma50,
                'above_ma200_pct': above_ma200
            },
            'sector_summary': await self.get_sector_rotation(),
            'updated_at': datetime.now().isoformat()
        }
    
    async def get_market_depth_analysis(self) -> Dict[str, Any]:
        """Get market depth and liquidity analysis"""
        data = list(self.market_data.values())
        
        # Liquidity metrics
        liquid_symbols = [d for d in data if d.volume_24h > np.mean([x.volume_24h for x in data])]
        illiquid_symbols = [d for d in data if d.volume_24h <= np.mean([x.volume_24h for x in data])]
        
        # Bid-ask spread simulation
        spread_data = []
        for item in data:
            # Simulate bid-ask spread based on volume
            spread_bps = max(0.5, min(50, 100 / (item.volume_24h / 1e6)))  # Larger volume = tighter spreads
            spread_data.append({
                'symbol': item.symbol,
                'spread_bps': spread_bps,
                'liquidity_score': min(100, (item.volume_24h / 1e6) * 10)
            })
        
        # Market depth by sector
        sector_depth = {}
        for sector in MarketSector:
            sector_symbols = [d for d in data if d.sector == sector]
            if sector_symbols:
                sector_depth[sector.value] = {
                    'total_volume': sum(d.volume_24h for d in sector_symbols),
                    'avg_volume': np.mean([d.volume_24h for d in sector_symbols]),
                    'symbols_count': len(sector_symbols),
                    'liquidity_score': np.mean([d.volume_24h for d in sector_symbols]) / 1e6
                }
        
        # Calculate total volume
        total_volume = sum(d.volume_24h for d in data)
        
        # Dark pool activity simulation
        dark_pool_volume = total_volume * np.random.uniform(0.3, 0.6)  # 30-60% of total volume
        
        return {
            'liquidity_analysis': {
                'liquid_symbols_count': len(liquid_symbols),
                'illiquid_symbols_count': len(illiquid_symbols),
                'avg_liquidity_score': np.mean([s['liquidity_score'] for s in spread_data])
            },
            'bid_ask_spreads': spread_data[:10],  # Top 10 symbols by spread
            'sector_depth': sector_depth,
            'dark_pool': {
                'estimated_volume': dark_pool_volume,
                'dark_pool_ratio': dark_pool_volume / total_volume
            },
            'liquidity_concentration': {
                'top_10_pct_volume': sum(sorted([d.volume_24h for d in data], reverse=True)[:int(len(data) * 0.1)]) / total_volume * 100
            },
            'analyzed_at': datetime.now().isoformat()
        }
    
    async def get_momentum_indicators(self) -> Dict[str, Any]:
        """Get market momentum indicators"""
        data = list(self.market_data.values())
        
        # RSI momentum
        rsi_data = [d.rsi for d in data]
        rsi_overbought = sum(1 for r in rsi_data if r > 70)
        rsi_oversold = sum(1 for r in rsi_data if r < 30)
        
        # MACD momentum
        macd_data = [d.macd for d in data]
        macd_bullish = sum(1 for m in macd_data if m > 0)
        macd_bearish = sum(1 for m in macd_data if m < 0)
        
        # Moving average momentum
        ma20_above = sum(1 for d in data if d.price > d.ma_20)
        ma50_above = sum(1 for d in data if d.price > d.ma_50)
        ma200_above = sum(1 for d in data if d.price > d.ma_200)
        
        # Price momentum (average price changes)
        momentum_1d = np.mean([d.change_24h for d in data])
        momentum_7d = np.mean([d.change_7d for d in data])
        momentum_30d = np.mean([d.change_30d for d in data])
        
        # Volume momentum
        volume_spike_symbols = sum(1 for d in data if d.volume_24h > d.volume_avg * 2)
        
        # Composite momentum score
        momentum_components = {
            'rsi_momentum': (rsi_oversold - rsi_overbought) / len(rsi_data),
            'macd_momentum': (macd_bullish - macd_bearish) / len(macd_data),
            'ma_momentum': (ma20_above - (len(data) - ma20_above)) / len(data),
            'price_momentum': momentum_1d,
            'volume_momentum': volume_spike_symbols / len(data)
        }
        
        composite_momentum = np.mean(list(momentum_components.values())) * 100
        
        return {
            'rsi_analysis': {
                'overbought_count': rsi_overbought,
                'oversold_count': rsi_oversold,
                'neutral_count': len(rsi_data) - rsi_overbought - rsi_oversold,
                'avg_rsi': np.mean(rsi_data)
            },
            'macd_analysis': {
                'bullish_count': macd_bullish,
                'bearish_count': macd_bearish,
                'avg_macd': np.mean(macd_data)
            },
            'ma_momentum': {
                'above_ma20_pct': ma20_above / len(data),
                'above_ma50_pct': ma50_above / len(data),
                'above_ma200_pct': ma200_above / len(data)
            },
            'price_momentum': {
                '1d': momentum_1d,
                '7d': momentum_7d,
                '30d': momentum_30d
            },
            'volume_momentum': {
                'spike_symbols': volume_spike_symbols,
                'spike_percentage': volume_spike_symbols / len(data)
            },
            'composite_momentum': {
                'score': composite_momentum,
                'components': momentum_components,
                'interpretation': 'Strong Bullish' if composite_momentum > 0.5 else 
                               'Bullish' if composite_momentum > 0.2 else
                               'Neutral' if composite_momentum > -0.2 else
                               'Bearish' if composite_momentum > -0.5 else 'Strong Bearish'
            },
            'analyzed_at': datetime.now().isoformat()
        }
    
    async def get_risk_metrics(self) -> Dict[str, Any]:
        """Get market risk analysis"""
        data = list(self.market_data.values())
        
        # Volatility metrics
        volatilities = [d.atr / d.price for d in data]
        avg_volatility = np.mean(volatilities)
        volatility_percentile = np.percentile(volatilities, [25, 50, 75, 90, 95])
        
        # Price dispersion
        returns = [d.change_24h for d in data]
        price_correlation = np.corrcoef(returns, [d.volume_24h for d in data])[0, 1] if len(data) > 1 else 0
        
        # Sector concentration risk
        sector_counts = {}
        total_market_cap = sum(d.market_cap for d in data)
        
        for sector in MarketSector:
            sector_market_cap = sum(d.market_cap for d in data if d.sector == sector)
            sector_counts[sector.value] = sector_market_cap / total_market_cap if total_market_cap > 0 else 0
        
        # Value at Risk (VaR) simulation
        returns_sorted = sorted(returns)
        var_95 = returns_sorted[int(len(returns_sorted) * 0.05)]
        var_99 = returns_sorted[int(len(returns_sorted) * 0.01)]
        
        # Maximum Drawdown simulation
        max_dd = min(returns)  # Worst single-day loss
        
        # Risk-adjusted returns
        risk_free_rate = 0.02 / 252  # Assuming 2% annual risk-free rate
        sharpe_ratios = [(r - risk_free_rate) / (abs(r) + 0.01) for r in returns]  # Adjusted volatility
        
        return {
            'volatility_analysis': {
                'avg_volatility': avg_volatility,
                'volatility_percentiles': {
                    'p25': volatility_percentile[0],
                    'p50': volatility_percentile[1],
                    'p75': volatility_percentile[2],
                    'p90': volatility_percentile[3],
                    'p95': volatility_percentile[4]
                }
            },
            'correlation_analysis': {
                'price_volume_correlation': price_correlation,
                'avg_correlation': np.mean([abs(d.macd) for d in data])
            },
            'sector_concentration': sector_counts,
            'value_at_risk': {
                'var_95': var_95,
                'var_99': var_99,
                'max_drawdown': max_dd
            },
            'risk_adjusted_metrics': {
                'avg_sharpe_ratio': np.mean(sharpe_ratios),
                'positive_sharpe_count': sum(1 for s in sharpe_ratios if s > 0),
                'high_risk_symbols': sum(1 for d in data if d.atr / d.price > avg_volatility * 2)
            },
            'risk_score': {
                'overall_risk': min(100, avg_volatility * 2000),
                'volatility_risk': avg_volatility * 1000,
                'concentration_risk': max(sector_counts.values()) * 100 if sector_counts else 0,
                'correlation_risk': abs(price_correlation) * 50
            },
            'analyzed_at': datetime.now().isoformat()
        }
    
    async def get_advanced_analytics(self) -> Dict[str, Any]:
        """Get comprehensive advanced analytics"""
        return {
            'market_depth': await self.get_market_depth_analysis(),
            'momentum_indicators': await self.get_momentum_indicators(),
            'risk_metrics': await self.get_risk_metrics(),
            'market_sentiment': await self.get_market_sentiment(),
            'sector_rotation': await self.get_sector_rotation(),
            'top_movers': await self.get_top_movers(),
            'generated_at': datetime.now().isoformat()
        }


# Global instance
market_intelligence = MarketIntelligence()


async def test_market_intelligence():
    """Test market intelligence"""
    mi = MarketIntelligence()
    
    print("=== MARKET INTELLIGENCE MODULE TEST ===\n")
    
    # Market heatmap
    print("1. MARKET HEATMAP:")
    heatmap = await mi.get_market_heatmap(metric="change_24h")
    for item in heatmap['data'][:5]:
        print(f"  {item['symbol']}: {item['value']:.2%} ({item['sector']})")
    
    # Market sentiment
    print("\n2. MARKET SENTIMENT:")
    sentiment = await mi.get_market_sentiment()
    print(f"  Fear & Greed Index: {sentiment['fear_greed_index']}")
    print(f"  Sentiment: {sentiment['sentiment_label']}")
    print(f"  Action: {sentiment['action']}")
    print(f"  Gainers/Losers: {sentiment['overview']['gainers_24h']}/{sentiment['overview']['losers_24h']}")
    
    # Correlation matrix
    print("\n3. CORRELATION MATRIX:")
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    correlation = await mi.calculate_correlation_matrix(symbols)
    print(f"Symbols: {correlation.symbols}")
    for i, row in enumerate(correlation.matrix):
        print(f"  {symbols[i]}: {[f'{c:.2f}' for c in row]}")
    
    # Market scanner
    print("\n4. MARKET SCANNER:")
    conditions = [
        ScannerCondition.RSI_OVERSOLD,
        ScannerCondition.VOLUME_SPIKE
    ]
    results = await mi.scan_market(conditions)
    for result in results[:3]:
        print(f"  {result.symbol}: {result.conditions_met} (score: {result.score:.2f})")
    
    # Market overview
    print("\n5. MARKET OVERVIEW:")
    overview = await mi.get_market_overview()
    print(f"  Total Symbols: {overview['total_symbols']}")
    print(f"  Sentiment: {overview['sentiment']}")
    print(f"  Gainers/Losers: {overview['gainers']}/{overview['losers']}")
    print(f"  Avg Change: {overview['avg_change_24h']:.2%}")
    print(f"  Volatility Index: {overview['volatility_index']:.2f}")
    
    # Momentum indicators
    print("\n6. MOMENTUM INDICATORS:")
    momentum = await mi.get_momentum_indicators()
    print(f"  Composite Momentum: {momentum['composite_momentum']['score']:.2f}")
    print(f"  Interpretation: {momentum['composite_momentum']['interpretation']}")
    print(f"  Volume Spike Symbols: {momentum['volume_momentum']['spike_symbols']}")
    
    # Risk metrics
    print("\n7. RISK METRICS:")
    risk = await mi.get_risk_metrics()
    print(f"  Overall Risk Score: {risk['risk_score']['overall_risk']:.1f}")
    print(f"  VaR 95%: {risk['value_at_risk']['var_95']:.2%}")
    print(f"  Max Drawdown: {risk['value_at_risk']['max_drawdown']:.2%}")
    
    # Market depth
    print("\n8. MARKET DEPTH:")
    depth = await mi.get_market_depth_analysis()
    print(f"  Liquid Symbols: {depth['liquidity_analysis']['liquid_symbols_count']}")
    print(f"  Dark Pool Ratio: {depth['dark_pool']['dark_pool_ratio']:.1%}")
    
    # Advanced analytics
    print("\n9. ADVANCED ANALYTICS:")
    analytics = await mi.get_advanced_analytics()
    print(f"  Generated: {analytics['generated_at']}")
    print("  All analytics modules loaded successfully!")
    
    print("\n=== TEST COMPLETED ===")


if __name__ == "__main__":
    asyncio.run(test_market_intelligence())
