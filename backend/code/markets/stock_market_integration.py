"""
AI Trading Evolution - Stock Market Integration Module
======================================================

NASDAQ va NYSE aksiyalar bozorlariga integratsiya:
- Real-time stock quotes
- Market depth (Level 2 data)
- Technical indicators
- Fundamental analysis
- Sector rotation strategies
- Pairs trading
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
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Exchange(Enum):
    """Birja turlari"""
    NASDAQ = "NASDAQ"
    NYSE = "NYSE"
    AMEX = "AMEX"


class Sector(Enum):
    """Sektor turlari"""
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCIAL = "Financial Services"
    CONSUMER_CYCLICAL = "Consumer Cyclical"
    INDUSTRIALS = "Industrials"
    ENERGY = "Energy"
    UTILITIES = "Utilities"
    REAL_ESTATE = "Real Estate"
    MATERIALS = "Basic Materials"
    CONSUMER_DEFENSIVE = "Consumer Defensive"
    COMMUNICATION = "Communication Services"


@dataclass
class StockQuote:
    """Aksiya narx ma'lumotlari"""
    symbol: str
    exchange: Exchange
    price: float
    bid: float
    ask: float
    volume: int
    market_cap: float
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    day_high: float
    day_low: float
    open_price: float
    prev_close: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def spread(self) -> float:
        """Bid-Ask spread"""
        return self.ask - self.bid
    
    @property
    def spread_pct(self) -> float:
        """Spread foizda"""
        return (self.spread / self.price) * 100 if self.price > 0 else 0
    
    @property
    def day_change(self) -> float:
        """Kunlik o'zgarish"""
        return self.price - self.prev_close
    
    @property
    def day_change_pct(self) -> float:
        """Kunlik o'zgarish foizda"""
        return (self.day_change / self.prev_close) * 100 if self.prev_close > 0 else 0


@dataclass
class StockProfile:
    """Kompaniya profili"""
    symbol: str
    name: str
    sector: Sector
    industry: str
    exchange: Exchange
    market_cap: float
    employees: int
    description: str
    website: str
    ceo: str
    founded_year: Optional[int] = None


@dataclass
class FinancialMetrics:
    """Moliyaviy ko'rsatkichlar"""
    symbol: str
    revenue: float
    revenue_growth: float
    net_income: float
    profit_margin: float
    operating_margin: float
    roe: float  # Return on Equity
    roa: float  # Return on Assets
    debt_to_equity: float
    current_ratio: float
    free_cash_flow: float
    earnings_per_share: float
    book_value_per_share: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TechnicalIndicators:
    """Texnik indikatorlar"""
    symbol: str
    sma_20: float  # Simple Moving Average
    sma_50: float
    sma_200: float
    ema_12: float  # Exponential Moving Average
    ema_26: float
    rsi: float  # Relative Strength Index
    macd: float  # MACD
    macd_signal: float
    bollinger_upper: float
    bollinger_lower: float
    atr: float  # Average True Range
    adx: float  # Average Directional Index
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_oversold(self) -> bool:
        """RSI asosida oversold"""
        return self.rsi < 30
    
    @property
    def is_overbought(self) -> bool:
        """RSI asosida overbought"""
        return self.rsi > 70
    
    @property
    def trend_strength(self) -> str:
        """ADX asosida trend kuchi"""
        if self.adx > 50:
            return "very_strong"
        elif self.adx > 25:
            return "strong"
        else:
            return "weak"


class StockDataProvider:
    """
    Aksiyalar uchun ma'lumot provayderi
    Real API'lar: Alpha Vantage, Polygon.io, IEX Cloud, Yahoo Finance
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Tuple[datetime, any]] = {}
        self.cache_ttl = 60  # 60 soniya
        
        # Top stocks by sector
        self.popular_stocks = {
            Sector.TECHNOLOGY: ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA'],
            Sector.HEALTHCARE: ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK'],
            Sector.FINANCIAL: ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C'],
            Sector.CONSUMER_CYCLICAL: ['AMZN', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT'],
            Sector.ENERGY: ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC'],
            Sector.INDUSTRIALS: ['BA', 'CAT', 'UPS', 'HON', 'GE', 'MMM']
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Kesh validligi tekshirish"""
        if key not in self.cache:
            return False
        timestamp, _ = self.cache[key]
        return (datetime.now() - timestamp).seconds < self.cache_ttl
    
    async def get_quote(self, symbol: str) -> Optional[StockQuote]:
        """Real-time quote olish"""
        cache_key = f"quote_{symbol}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            # Alpha Vantage Global Quote API
            api_key = self.api_keys.get('alpha_vantage', '')
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'Global Quote' in data:
                        quote_data = data['Global Quote']
                        
                        quote = StockQuote(
                            symbol=symbol,
                            exchange=Exchange.NASDAQ,  # Default
                            price=float(quote_data.get('05. price', 0)),
                            bid=float(quote_data.get('05. price', 0)) * 0.999,
                            ask=float(quote_data.get('05. price', 0)) * 1.001,
                            volume=int(quote_data.get('06. volume', 0)),
                            market_cap=0,  # Alohida API kerak
                            pe_ratio=None,
                            dividend_yield=None,
                            day_high=float(quote_data.get('03. high', 0)),
                            day_low=float(quote_data.get('04. low', 0)),
                            open_price=float(quote_data.get('02. open', 0)),
                            prev_close=float(quote_data.get('08. previous close', 0))
                        )
                        
                        self.cache[cache_key] = (datetime.now(), quote)
                        return quote
            
            # Demo data (API ishlamasa)
            demo_prices = {
                'AAPL': 178.50, 'MSFT': 380.20, 'GOOGL': 142.30, 'AMZN': 155.80,
                'NVDA': 495.30, 'TSLA': 248.50, 'META': 485.20, 'JPM': 172.40,
                'JNJ': 155.90, 'V': 265.30, 'WMT': 168.70, 'PG': 155.40
            }
            
            base_price = demo_prices.get(symbol, 100.0)
            
            quote = StockQuote(
                symbol=symbol,
                exchange=Exchange.NASDAQ,
                price=base_price,
                bid=base_price * 0.999,
                ask=base_price * 1.001,
                volume=np.random.randint(5000000, 50000000),
                market_cap=base_price * 1e9,
                pe_ratio=np.random.uniform(15, 35),
                dividend_yield=np.random.uniform(0, 3),
                day_high=base_price * 1.02,
                day_low=base_price * 0.98,
                open_price=base_price * 0.995,
                prev_close=base_price * 0.998
            )
            
            self.cache[cache_key] = (datetime.now(), quote)
            return quote
            
        except Exception as e:
            logger.error(f"Quote olishda xato ({symbol}): {e}")
            return None
    
    async def get_historical_data(
        self, 
        symbol: str,
        days: int = 30
    ) -> Optional[pd.DataFrame]:
        """Tarixiy ma'lumotlar"""
        cache_key = f"history_{symbol}_{days}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            # Alpha Vantage Daily API
            api_key = self.api_keys.get('alpha_vantage', '')
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': 'compact',
                'apikey': api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'Time Series (Daily)' in data:
                        time_series = data['Time Series (Daily)']
                        
                        df = pd.DataFrame.from_dict(time_series, orient='index')
                        df.index = pd.to_datetime(df.index)
                        df = df.sort_index()
                        
                        # Column nomlarini tozalash
                        df.columns = ['open', 'high', 'low', 'close', 'volume']
                        df = df.astype(float)
                        
                        # Oxirgi N kunni olish
                        df = df.tail(days)
                        
                        self.cache[cache_key] = (datetime.now(), df)
                        return df
            
            # Demo data generation
            quote = await self.get_quote(symbol)
            if not quote:
                return None
            
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            base_price = quote.price
            
            # Random walk simulatsiyasi
            returns = np.random.normal(0.001, 0.02, days)
            prices = base_price * np.cumprod(1 + returns)
            
            df = pd.DataFrame({
                'open': prices * np.random.uniform(0.99, 1.01, days),
                'high': prices * np.random.uniform(1.00, 1.03, days),
                'low': prices * np.random.uniform(0.97, 1.00, days),
                'close': prices,
                'volume': np.random.randint(5000000, 50000000, days)
            }, index=dates)
            
            self.cache[cache_key] = (datetime.now(), df)
            return df
            
        except Exception as e:
            logger.error(f"Tarixiy ma'lumot olishda xato ({symbol}): {e}")
            return None
    
    async def get_technical_indicators(self, symbol: str) -> Optional[TechnicalIndicators]:
        """Texnik indikatorlarni hisoblash"""
        df = await self.get_historical_data(symbol, days=200)
        
        if df is None or len(df) < 50:
            return None
        
        try:
            close = df['close']
            high = df['high']
            low = df['low']
            
            # Simple Moving Averages
            sma_20 = close.rolling(window=20).mean().iloc[-1]
            sma_50 = close.rolling(window=50).mean().iloc[-1]
            sma_200 = close.rolling(window=200).mean().iloc[-1] if len(df) >= 200 else sma_50
            
            # Exponential Moving Averages
            ema_12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
            ema_26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
            
            # RSI (Relative Strength Index)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi = rsi.iloc[-1]
            
            # MACD
            macd = ema_12 - ema_26
            macd_signal = close.ewm(span=9, adjust=False).mean().iloc[-1]
            
            # Bollinger Bands
            bb_middle = close.rolling(window=20).mean()
            bb_std = close.rolling(window=20).std()
            bollinger_upper = (bb_middle + 2 * bb_std).iloc[-1]
            bollinger_lower = (bb_middle - 2 * bb_std).iloc[-1]
            
            # ATR (Average True Range)
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]
            
            # ADX (Average Directional Index) - Simplified
            adx = 25.0  # Default average
            
            indicators = TechnicalIndicators(
                symbol=symbol,
                sma_20=sma_20,
                sma_50=sma_50,
                sma_200=sma_200,
                ema_12=ema_12,
                ema_26=ema_26,
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                bollinger_upper=bollinger_upper,
                bollinger_lower=bollinger_lower,
                atr=atr,
                adx=adx
            )
            
            return indicators
            
        except Exception as e:
            logger.error(f"Texnik indikatorlarni hisoblashda xato ({symbol}): {e}")
            return None
    
    async def get_fundamental_metrics(self, symbol: str) -> Optional[FinancialMetrics]:
        """Fundamental tahlil ko'rsatkichlari"""
        cache_key = f"fundamentals_{symbol}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            # Demo fundamental data
            demo_data = {
                'AAPL': (394_328_000_000, 0.078, 96_995_000_000, 0.245, 0.305, 1.502, 0.272, 1.95, 0.98, 111_443_000_000, 6.16, 3.85),
                'MSFT': (211_915_000_000, 0.072, 72_361_000_000, 0.342, 0.427, 0.433, 0.188, 0.32, 2.52, 65_149_000_000, 9.65, 23.84),
                'GOOGL': (282_836_000_000, 0.089, 59_972_000_000, 0.212, 0.287, 0.269, 0.145, 0.09, 2.97, 69_495_000_000, 5.61, 19.32),
            }
            
            if symbol in demo_data:
                data = demo_data[symbol]
                metrics = FinancialMetrics(
                    symbol=symbol,
                    revenue=data[0],
                    revenue_growth=data[1],
                    net_income=data[2],
                    profit_margin=data[3],
                    operating_margin=data[4],
                    roe=data[5],
                    roa=data[6],
                    debt_to_equity=data[7],
                    current_ratio=data[8],
                    free_cash_flow=data[9],
                    earnings_per_share=data[10],
                    book_value_per_share=data[11]
                )
            else:
                # Generic demo data
                metrics = FinancialMetrics(
                    symbol=symbol,
                    revenue=np.random.uniform(50e9, 500e9),
                    revenue_growth=np.random.uniform(0.05, 0.15),
                    net_income=np.random.uniform(10e9, 100e9),
                    profit_margin=np.random.uniform(0.10, 0.30),
                    operating_margin=np.random.uniform(0.15, 0.35),
                    roe=np.random.uniform(0.10, 0.50),
                    roa=np.random.uniform(0.05, 0.20),
                    debt_to_equity=np.random.uniform(0.20, 2.00),
                    current_ratio=np.random.uniform(1.00, 3.00),
                    free_cash_flow=np.random.uniform(5e9, 50e9),
                    earnings_per_share=np.random.uniform(3.0, 15.0),
                    book_value_per_share=np.random.uniform(10.0, 50.0)
                )
            
            self.cache[cache_key] = (datetime.now(), metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Fundamental metrikalarni olishda xato ({symbol}): {e}")
            return None
    
    def get_stocks_by_sector(self, sector: Sector) -> List[str]:
        """Sektor bo'yicha aksiyalar ro'yxati"""
        return self.popular_stocks.get(sector, [])


class StockScreener:
    """
    Aksiyalarni filterlash va saralash
    - Technical screening
    - Fundamental screening
    - Combined scoring
    """
    
    def __init__(self, data_provider: StockDataProvider):
        self.data_provider = data_provider
    
    async def screen_technical(
        self,
        symbols: List[str],
        criteria: Dict[str, any]
    ) -> List[Tuple[str, float]]:
        """Texnik kriterialar bo'yicha filterlash"""
        results = []
        
        for symbol in symbols:
            indicators = await self.data_provider.get_technical_indicators(symbol)
            
            if not indicators:
                continue
            
            score = 0.0
            max_score = 0.0
            
            # RSI check
            if 'rsi_min' in criteria and 'rsi_max' in criteria:
                max_score += 1.0
                if criteria['rsi_min'] <= indicators.rsi <= criteria['rsi_max']:
                    score += 1.0
            
            # Trend check (price vs MA)
            if 'above_sma_50' in criteria:
                max_score += 1.0
                quote = await self.data_provider.get_quote(symbol)
                if quote and criteria['above_sma_50'] == (quote.price > indicators.sma_50):
                    score += 1.0
            
            # MACD check
            if 'macd_bullish' in criteria:
                max_score += 1.0
                if criteria['macd_bullish'] == (indicators.macd > indicators.macd_signal):
                    score += 1.0
            
            # Trend strength
            if 'min_trend_strength' in criteria:
                max_score += 1.0
                if indicators.trend_strength in ['strong', 'very_strong']:
                    score += 1.0
            
            if max_score > 0:
                normalized_score = score / max_score
                results.append((symbol, normalized_score))
        
        # Score bo'yicha saralash
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    async def screen_fundamental(
        self,
        symbols: List[str],
        criteria: Dict[str, any]
    ) -> List[Tuple[str, float]]:
        """Fundamental kriterialar bo'yicha filterlash"""
        results = []
        
        for symbol in symbols:
            metrics = await self.data_provider.get_fundamental_metrics(symbol)
            
            if not metrics:
                continue
            
            score = 0.0
            max_score = 0.0
            
            # Revenue growth
            if 'min_revenue_growth' in criteria:
                max_score += 1.0
                if metrics.revenue_growth >= criteria['min_revenue_growth']:
                    score += 1.0
            
            # Profit margin
            if 'min_profit_margin' in criteria:
                max_score += 1.0
                if metrics.profit_margin >= criteria['min_profit_margin']:
                    score += 1.0
            
            # ROE
            if 'min_roe' in criteria:
                max_score += 1.0
                if metrics.roe >= criteria['min_roe']:
                    score += 1.0
            
            # Debt to Equity
            if 'max_debt_to_equity' in criteria:
                max_score += 1.0
                if metrics.debt_to_equity <= criteria['max_debt_to_equity']:
                    score += 1.0
            
            if max_score > 0:
                normalized_score = score / max_score
                results.append((symbol, normalized_score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    async def combined_screen(
        self,
        symbols: List[str],
        technical_weight: float = 0.6,
        fundamental_weight: float = 0.4
    ) -> List[Tuple[str, float]]:
        """Texnik va fundamental birlashtirgan screening"""
        # Default criteria
        technical_criteria = {
            'rsi_min': 40,
            'rsi_max': 60,
            'above_sma_50': True,
            'macd_bullish': True
        }
        
        fundamental_criteria = {
            'min_revenue_growth': 0.05,
            'min_profit_margin': 0.10,
            'min_roe': 0.10,
            'max_debt_to_equity': 2.0
        }
        
        tech_results = await self.screen_technical(symbols, technical_criteria)
        fund_results = await self.screen_fundamental(symbols, fundamental_criteria)
        
        # Combine scores
        tech_dict = dict(tech_results)
        fund_dict = dict(fund_results)
        
        combined = []
        all_symbols = set(tech_dict.keys()) | set(fund_dict.keys())
        
        for symbol in all_symbols:
            tech_score = tech_dict.get(symbol, 0)
            fund_score = fund_dict.get(symbol, 0)
            
            combined_score = (tech_score * technical_weight + 
                            fund_score * fundamental_weight)
            
            combined.append((symbol, combined_score))
        
        combined.sort(key=lambda x: x[1], reverse=True)
        return combined


class PairsTradingStrategy:
    """
    Pairs Trading strategiyasi
    Korrelyatsiyasi yuqori 2 ta aksiyani tanlash va spread tradingini amalga oshirish
    """
    
    def __init__(self, data_provider: StockDataProvider):
        self.data_provider = data_provider
        self.pairs: List[Tuple[str, str]] = []
    
    async def find_cointegrated_pairs(
        self,
        symbols: List[str],
        lookback_days: int = 90
    ) -> List[Tuple[str, str, float]]:
        """Cointegrated pairs topish"""
        pairs_with_score = []
        
        # Barcha juftliklarni tekshirish
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                symbol1, symbol2 = symbols[i], symbols[j]
                
                # Tarixiy ma'lumotlarni olish
                df1 = await self.data_provider.get_historical_data(symbol1, days=lookback_days)
                df2 = await self.data_provider.get_historical_data(symbol2, days=lookback_days)
                
                if df1 is None or df2 is None:
                    continue
                
                # Umumiy sanalarni topish
                common_dates = df1.index.intersection(df2.index)
                if len(common_dates) < 60:
                    continue
                
                prices1 = df1.loc[common_dates, 'close']
                prices2 = df2.loc[common_dates, 'close']
                
                # Korrelyatsiya hisoblash
                correlation = prices1.corr(prices2)
                
                if correlation > 0.75:  # Yuqori korrelyatsiya
                    # Spread hisoblash (normalized)
                    ratio = prices1 / prices2
                    spread = ratio - ratio.mean()
                    spread_std = spread.std()
                    
                    # Z-score
                    z_score = abs(spread.iloc[-1] / spread_std) if spread_std > 0 else 0
                    
                    # Score: yuqori correlation + yuqori z-score = yaxshi imkoniyat
                    score = correlation * z_score
                    
                    pairs_with_score.append((symbol1, symbol2, score))
        
        pairs_with_score.sort(key=lambda x: x[2], reverse=True)
        return pairs_with_score[:10]  # Top 10
    
    async def analyze_pair_opportunity(
        self,
        symbol1: str,
        symbol2: str,
        lookback_days: int = 90
    ) -> Optional[Dict]:
        """Juftlik uchun trading imkoniyatini tahlil qilish"""
        df1 = await self.data_provider.get_historical_data(symbol1, days=lookback_days)
        df2 = await self.data_provider.get_historical_data(symbol2, days=lookback_days)
        
        if df1 is None or df2 is None:
            return None
        
        common_dates = df1.index.intersection(df2.index)
        prices1 = df1.loc[common_dates, 'close']
        prices2 = df2.loc[common_dates, 'close']
        
        # Ratio va spread
        ratio = prices1 / prices2
        spread = ratio - ratio.mean()
        spread_std = spread.std()
        current_spread = spread.iloc[-1]
        z_score = current_spread / spread_std if spread_std > 0 else 0
        
        # Trading signal
        signal = None
        if z_score > 2.0:
            signal = 'SHORT_SPREAD'  # Short symbol1, Long symbol2
            action = f"SHORT {symbol1}, LONG {symbol2}"
        elif z_score < -2.0:
            signal = 'LONG_SPREAD'  # Long symbol1, Short symbol2
            action = f"LONG {symbol1}, SHORT {symbol2}"
        
        if signal:
            return {
                'symbol1': symbol1,
                'symbol2': symbol2,
                'signal': signal,
                'action': action,
                'z_score': z_score,
                'current_ratio': ratio.iloc[-1],
                'mean_ratio': ratio.mean(),
                'spread_std': spread_std,
                'correlation': prices1.corr(prices2),
                'confidence': min(abs(z_score) / 3.0, 1.0)
            }
        
        return None


class SectorRotationStrategy:
    """
    Sector Rotation strategiyasi
    Eng yaxshi performance ko'rsatayotgan sektorlarga invest qilish
    """
    
    def __init__(self, data_provider: StockDataProvider):
        self.data_provider = data_provider
    
    async def calculate_sector_performance(
        self,
        lookback_days: int = 30
    ) -> Dict[Sector, float]:
        """Sektor bo'yicha performance hisoblash"""
        sector_returns = {}
        
        for sector in Sector:
            symbols = self.data_provider.get_stocks_by_sector(sector)
            
            if not symbols:
                continue
            
            returns = []
            
            for symbol in symbols:
                df = await self.data_provider.get_historical_data(symbol, days=lookback_days)
                
                if df is not None and len(df) >= 2:
                    start_price = df['close'].iloc[0]
                    end_price = df['close'].iloc[-1]
                    ret = (end_price - start_price) / start_price
                    returns.append(ret)
            
            if returns:
                avg_return = np.mean(returns)
                sector_returns[sector] = avg_return
        
        return sector_returns
    
    async def get_rotation_signals(self) -> List[Dict]:
        """Rotation signallarini olish"""
        # 30 kunlik va 90 kunlik performance
        short_term = await self.calculate_sector_performance(lookback_days=30)
        long_term = await self.calculate_sector_performance(lookback_days=90)
        
        signals = []
        
        for sector in Sector:
            if sector in short_term and sector in long_term:
                st_return = short_term[sector]
                lt_return = long_term[sector]
                
                # Momentum: qisqa muddatda yaxshi, uzoq muddatda ham yaxshi
                if st_return > 0.05 and lt_return > 0.10:
                    signals.append({
                        'sector': sector.value,
                        'action': 'OVERWEIGHT',
                        'short_term_return': st_return,
                        'long_term_return': lt_return,
                        'momentum_score': (st_return + lt_return) / 2
                    })
                # Reversal: qisqa muddatda yomon, uzoq muddatda yaxshi
                elif st_return < -0.03 and lt_return > 0.05:
                    signals.append({
                        'sector': sector.value,
                        'action': 'CONSIDER_BUY',
                        'short_term_return': st_return,
                        'long_term_return': lt_return,
                        'reversal_score': lt_return - st_return
                    })
        
        return signals


async def main():
    """Test funksiyasi"""
    api_keys = {
        'alpha_vantage': 'YOUR_API_KEY',
        'polygon': 'YOUR_API_KEY'
    }
    
    async with StockDataProvider(api_keys) as provider:
        print("=" * 80)
        print("AI TRADING EVOLUTION - STOCK MARKET INTEGRATION")
        print("=" * 80)
        print()
        
        # 1. Real-time quotes
        print("📊 REAL-TIME QUOTES:")
        print("-" * 80)
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        
        for symbol in test_symbols:
            quote = await provider.get_quote(symbol)
            if quote:
                print(f"{symbol:6} ${quote.price:8.2f}  "
                      f"Change: {quote.day_change_pct:+6.2f}%  "
                      f"Vol: {quote.volume:,}")
        print()
        
        # 2. Technical indicators
        print("📈 TEXNIK INDIKATORLAR (AAPL):")
        print("-" * 80)
        indicators = await provider.get_technical_indicators('AAPL')
        if indicators:
            print(f"SMA 20:  ${indicators.sma_20:.2f}")
            print(f"SMA 50:  ${indicators.sma_50:.2f}")
            print(f"SMA 200: ${indicators.sma_200:.2f}")
            print(f"RSI:     {indicators.rsi:.1f} ({'Oversold' if indicators.is_oversold else 'Overbought' if indicators.is_overbought else 'Neutral'})")
            print(f"MACD:    {indicators.macd:.2f}")
            print(f"Trend:   {indicators.trend_strength}")
        print()
        
        # 3. Stock screening
        print("🔍 STOCK SCREENING:")
        print("-" * 80)
        screener = StockScreener(provider)
        
        all_symbols = []
        for sector in [Sector.TECHNOLOGY, Sector.HEALTHCARE, Sector.FINANCIAL]:
            all_symbols.extend(provider.get_stocks_by_sector(sector))
        
        top_stocks = await screener.combined_screen(all_symbols)
        
        for i, (symbol, score) in enumerate(top_stocks[:5], 1):
            print(f"{i}. {symbol:6} Score: {score:.2f}")
        print()
        
        # 4. Pairs trading
        print("👥 PAIRS TRADING IMKONIYATLARI:")
        print("-" * 80)
        pairs_strategy = PairsTradingStrategy(provider)
        
        tech_symbols = provider.get_stocks_by_sector(Sector.TECHNOLOGY)
        pairs = await pairs_strategy.find_cointegrated_pairs(tech_symbols[:6], lookback_days=60)
        
        for i, (sym1, sym2, score) in enumerate(pairs[:3], 1):
            opportunity = await pairs_strategy.analyze_pair_opportunity(sym1, sym2)
            if opportunity:
                print(f"{i}. {opportunity['symbol1']} / {opportunity['symbol2']}")
                print(f"   Signal: {opportunity['signal']}")
                print(f"   Action: {opportunity['action']}")
                print(f"   Z-Score: {opportunity['z_score']:.2f}")
                print(f"   Correlation: {opportunity['correlation']:.2f}")
                print(f"   Confidence: {opportunity['confidence']:.1%}")
                print()
        
        # 5. Sector rotation
        print("🔄 SEKTOR ROTATION:")
        print("-" * 80)
        rotation_strategy = SectorRotationStrategy(provider)
        rotation_signals = await rotation_strategy.get_rotation_signals()
        
        for signal in rotation_signals[:3]:
            print(f"Sector: {signal['sector']}")
            print(f"  Action: {signal['action']}")
            print(f"  30D Return: {signal['short_term_return']:.1%}")
            print(f"  90D Return: {signal['long_term_return']:.1%}")
            print()
        
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
