"""
Advanced Charts Backend
========================

TradingView integration va advanced charting.
Technical indicators, drawing tools, chart patterns.

Features:
- TradingView widget integration
- Technical indicators
- Chart patterns detection
- Drawing tools support
- Multi-timeframe analysis
- Custom indicators
- Support & Resistance analysis
- Volume analysis
- Comprehensive technical analysis
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from enum import Enum
import math
from collections import defaultdict


class ChartType(Enum):
    """Chart type enum"""
    CANDLESTICK = "candlestick"
    LINE = "line"
    AREA = "area"
    HEIKIN_ASHI = "heikin_ashi"
    RENKO = "renko"


class Timeframe(Enum):
    """Timeframe enum"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"


class IndicatorType(Enum):
    """Technical indicator type enum"""
    SMA = "sma"
    EMA = "ema"
    RSI = "rsi"
    MACD = "macd"
    BOLLINGER_BANDS = "bollinger_bands"
    ATR = "atr"
    STOCHASTIC = "stochastic"
    ADX = "adx"
    ICHIMOKU = "ichimoku"
    FIBONACCI = "fibonacci"
    WILLIAM_R = "williams_r"
    CCI = "cci"
    OBV = "obv"
    VWAP = "vwap"


class PatternType(Enum):
    """Chart pattern type enum"""
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    INVERSE_HEAD_AND_SHOULDERS = "inverse_head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIANGLE = "triangle"
    WEDGE = "wedge"
    FLAG = "flag"
    PENNANT = "pennant"
    CUP_AND_HANDLE = "cup_and_handle"
    TRIANGLE_ASCENDING = "triangle_ascending"
    TRIANGLE_DESCENDING = "triangle_descending"
    RECTANGLE = "rectangle"


@dataclass
class OHLCV:
    """OHLCV candlestick data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }


@dataclass
class Indicator:
    """Technical indicator"""
    name: str
    type: IndicatorType
    parameters: Dict[str, Any]
    values: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'type': self.type.value,
            'parameters': self.parameters,
            'values': self.values
        }


@dataclass
class ChartPattern:
    """Detected chart pattern"""
    pattern_id: str
    pattern_type: PatternType
    symbol: str
    timeframe: Timeframe
    
    # Pattern coordinates
    start_date: datetime
    end_date: datetime
    key_points: List[Dict[str, Any]]
    
    # Confidence and target
    confidence: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    
    detected_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type.value,
            'symbol': self.symbol,
            'timeframe': self.timeframe.value,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'key_points': self.key_points,
            'confidence': self.confidence,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'detected_at': self.detected_at.isoformat()
        }


@dataclass
class SupportResistanceLevel:
    """Support and Resistance level"""
    level_type: str  # "support" or "resistance"
    price: float
    strength: float
    touch_count: int
    last_touched: datetime
    is_major: bool
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'level_type': self.level_type,
            'price': self.price,
            'strength': self.strength,
            'touch_count': self.touch_count,
            'last_touched': self.last_touched.isoformat(),
            'is_major': self.is_major
        }


@dataclass
class VolumeAnalysis:
    """Volume analysis data"""
    symbol: str
    timeframe: Timeframe
    
    # Volume statistics
    average_volume: float
    current_volume: float
    volume_ratio: float
    volume_trend: str
    
    # Volume patterns
    high_volume_dates: List[datetime]
    low_volume_dates: List[datetime]
    volume_spikes: List[Dict[str, Any]]
    
    # On Balance Volume
    obv_values: List[Dict[str, Any]]
    
    # VWAP
    vwap_value: Optional[float]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe.value,
            'average_volume': self.average_volume,
            'current_volume': self.current_volume,
            'volume_ratio': self.volume_ratio,
            'volume_trend': self.volume_trend,
            'high_volume_dates': [d.isoformat() for d in self.high_volume_dates],
            'low_volume_dates': [d.isoformat() for d in self.low_volume_dates],
            'volume_spikes': self.volume_spikes,
            'obv_values': self.obv_values,
            'vwap_value': self.vwap_value
        }


@dataclass
class TradingViewWidget:
    """TradingView widget configuration"""
    symbol: str
    interval: str
    theme: str = "dark"
    style: str = "1"  # 1=candlestick
    width: str = "100%"
    height: str = "600"
    locale: str = "en"
    toolbar_bg: str = "#f1f3f6"
    enable_publishing: bool = False
    allow_symbol_change: bool = True
    studies: List[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to widget configuration"""
        return {
            'symbol': self.symbol,
            'interval': self.interval,
            'theme': self.theme,
            'style': self.style,
            'width': self.width,
            'height': self.height,
            'locale': self.locale,
            'toolbar_bg': self.toolbar_bg,
            'enable_publishing': self.enable_publishing,
            'allow_symbol_change': self.allow_symbol_change,
            'studies': self.studies or []
        }


class AdvancedCharts:
    """
    Advanced Charts System
    
    Provides TradingView integration, technical indicators,
    chart pattern detection, support/resistance analysis,
    and comprehensive volume analysis.
    """
    
    def __init__(self):
        self.price_data: Dict[str, Dict[Timeframe, List[OHLCV]]] = {}
        self.indicators: Dict[str, List[Indicator]] = {}
        self.detected_patterns: List[ChartPattern] = []
        
        # Initialize sample data
        self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate sample price data"""
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT']
        
        for symbol in symbols:
            self.price_data[symbol] = {}
            
            # Generate data for different timeframes
            for timeframe in [Timeframe.M5, Timeframe.H1, Timeframe.D1]:
                candles = []
                
                # Base price varies by symbol
                base_prices = {
                    'BTC/USDT': 45000,
                    'ETH/USDT': 3000,
                    'SOL/USDT': 100,
                    'ADA/USDT': 0.5,
                    'DOT/USDT': 7
                }
                current_price = base_prices.get(symbol, 100)
                
                # Number of candles based on timeframe
                if timeframe == Timeframe.M5:
                    num_candles = 288  # 24 hours
                    delta = timedelta(minutes=5)
                elif timeframe == Timeframe.H1:
                    num_candles = 168  # 1 week
                    delta = timedelta(hours=1)
                else:
                    num_candles = 365  # 1 year
                    delta = timedelta(days=1)
                
                current_time = datetime.now() - (delta * num_candles)
                volatility = 0.01 if symbol == 'BTC/USDT' else 0.02
                
                for i in range(num_candles):
                    open_price = current_price
                    
                    # More realistic price movement with trends
                    trend_factor = 1 + np.random.normal(0, volatility)
                    
                    # Add occasional breakouts
                    if np.random.random() < 0.05:  # 5% chance of significant move
                        trend_factor *= 1.1 if np.random.random() > 0.5 else 0.9
                    
                    close_price = open_price * trend_factor
                    
                    high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, volatility/2)))
                    low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, volatility/2)))
                    
                    # Volume varies with price movement
                    volume_multiplier = 1 + abs(trend_factor - 1) * 10
                    base_volume = 1e6 if 'BTC' in symbol else 5e6
                    volume = base_volume * volume_multiplier * np.random.uniform(0.5, 2.0)
                    
                    candle = OHLCV(
                        timestamp=current_time,
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        close=close_price,
                        volume=volume
                    )
                    
                    candles.append(candle)
                    
                    current_price = close_price
                    current_time += delta
                
                self.price_data[symbol][timeframe] = candles
    
    async def get_chart_data(
        self,
        symbol: str,
        timeframe: Timeframe,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[OHLCV]:
        """
        Get chart data (OHLCV)
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            start_date: Start date filter
            end_date: End date filter
            limit: Number of candles limit
            
        Returns:
            List of OHLCV candles
        """
        if symbol not in self.price_data:
            return []
        
        if timeframe not in self.price_data[symbol]:
            return []
        
        candles = self.price_data[symbol][timeframe]
        
        # Apply date filters
        if start_date:
            candles = [c for c in candles if c.timestamp >= start_date]
        
        if end_date:
            candles = [c for c in candles if c.timestamp <= end_date]
        
        # Apply limit
        if limit:
            candles = candles[-limit:]
        
        return candles
    
    async def calculate_indicator(
        self,
        symbol: str,
        timeframe: Timeframe,
        indicator_type: IndicatorType,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Indicator:
        """
        Calculate technical indicator
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            indicator_type: Type of indicator
            parameters: Indicator parameters
            
        Returns:
            Calculated indicator
        """
        candles = await self.get_chart_data(symbol, timeframe)
        
        if not candles:
            raise ValueError(f"No data for {symbol} {timeframe.value}")
        
        closes = [c.close for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        volumes = [c.volume for c in candles]
        
        parameters = parameters or {}
        indicator_values = []
        
        if indicator_type == IndicatorType.SMA:
            period = parameters.get('period', 20)
            values = self._calculate_sma(closes, period)
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'value': values[i]
                }
                for i in range(len(values))
            ]
        
        elif indicator_type == IndicatorType.EMA:
            period = parameters.get('period', 20)
            values = self._calculate_ema(closes, period)
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'value': values[i]
                }
                for i in range(len(values))
            ]
        
        elif indicator_type == IndicatorType.RSI:
            period = parameters.get('period', 14)
            values = self._calculate_rsi(closes, period)
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'value': values[i]
                }
                for i in range(len(values))
            ]
        
        elif indicator_type == IndicatorType.MACD:
            fast = parameters.get('fast_period', 12)
            slow = parameters.get('slow_period', 26)
            signal = parameters.get('signal_period', 9)
            
            macd_line, signal_line, histogram = self._calculate_macd(
                closes, fast, slow, signal
            )
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'macd': macd_line[i],
                    'signal': signal_line[i],
                    'histogram': histogram[i]
                }
                for i in range(len(macd_line))
            ]
        
        elif indicator_type == IndicatorType.BOLLINGER_BANDS:
            period = parameters.get('period', 20)
            std_dev = parameters.get('std_dev', 2)
            
            middle, upper, lower = self._calculate_bollinger_bands(
                closes, period, std_dev
            )
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'middle': middle[i],
                    'upper': upper[i],
                    'lower': lower[i]
                }
                for i in range(len(middle))
            ]
        
        elif indicator_type == IndicatorType.ATR:
            period = parameters.get('period', 14)
            values = self._calculate_atr(highs, lows, closes, period)
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'value': values[i]
                }
                for i in range(len(values))
            ]
        
        elif indicator_type == IndicatorType.STOCHASTIC:
            k_period = parameters.get('k_period', 14)
            d_period = parameters.get('d_period', 3)
            k_values, d_values = self._calculate_stochastic(highs, lows, closes, k_period, d_period)
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'k': k_values[i],
                    'd': d_values[i]
                }
                for i in range(len(k_values))
            ]
        
        elif indicator_type == IndicatorType.WILLIAM_R:
            period = parameters.get('period', 14)
            values = self._calculate_williams_r(highs, lows, closes, period)
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'value': values[i]
                }
                for i in range(len(values))
            ]
        
        elif indicator_type == IndicatorType.CCI:
            period = parameters.get('period', 20)
            values = self._calculate_cci(highs, lows, closes, period)
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'value': values[i]
                }
                for i in range(len(values))
            ]
        
        elif indicator_type == IndicatorType.OBV:
            values = self._calculate_obv(closes, volumes)
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'value': values[i]
                }
                for i in range(len(values))
            ]
        
        elif indicator_type == IndicatorType.VWAP:
            values = self._calculate_vwap(closes, volumes)
            indicator_values = [
                {
                    'timestamp': candles[i].timestamp.isoformat(),
                    'value': values[i]
                }
                for i in range(len(values))
            ]
        
        else:
            raise ValueError(f"Unsupported indicator type: {indicator_type}")
        
        indicator = Indicator(
            name=f"{indicator_type.value}_{symbol}_{timeframe.value}",
            type=indicator_type,
            parameters=parameters,
            values=indicator_values
        )
        
        return indicator
    
    def _calculate_sma(self, data: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        sma = []
        for i in range(len(data)):
            if i < period - 1:
                sma.append(None)
            else:
                sma.append(np.mean(data[i-period+1:i+1]))
        return sma
    
    def _calculate_ema(self, data: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        multiplier = 2 / (period + 1)
        ema = [data[0]]
        
        for i in range(1, len(data)):
            ema.append((data[i] - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    def _calculate_rsi(self, data: List[float], period: int) -> List[float]:
        """Calculate Relative Strength Index"""
        deltas = [data[i] - data[i-1] for i in range(1, len(data))]
        
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        rsi = [None] * period
        
        for i in range(period, len(data)):
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
            
            if i < len(gains):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        return rsi
    
    def _calculate_macd(
        self,
        data: List[float],
        fast: int,
        slow: int,
        signal: int
    ) -> Tuple[List[float], List[float], List[float]]:
        """Calculate MACD"""
        ema_fast = self._calculate_ema(data, fast)
        ema_slow = self._calculate_ema(data, slow)
        
        macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
        signal_line = self._calculate_ema(macd_line, signal)
        histogram = [m - s for m, s in zip(macd_line, signal_line)]
        
        return macd_line, signal_line, histogram
    
    def _calculate_bollinger_bands(
        self,
        data: List[float],
        period: int,
        std_dev: float
    ) -> Tuple[List[float], List[float], List[float]]:
        """Calculate Bollinger Bands"""
        middle = self._calculate_sma(data, period)
        
        upper = []
        lower = []
        
        for i in range(len(data)):
            if i < period - 1:
                upper.append(None)
                lower.append(None)
            else:
                std = np.std(data[i-period+1:i+1])
                upper.append(middle[i] + std_dev * std)
                lower.append(middle[i] - std_dev * std)
        
        return middle, upper, lower
    
    def _calculate_atr(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int
    ) -> List[float]:
        """Calculate Average True Range"""
        tr = [highs[0] - lows[0]]
        
        for i in range(1, len(closes)):
            tr.append(max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            ))
        
        atr = [None] * (period - 1)
        atr.append(np.mean(tr[:period]))
        
        for i in range(period, len(tr)):
            atr.append((atr[-1] * (period - 1) + tr[i]) / period)
        
        return atr
    
    def _calculate_stochastic(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        k_period: int,
        d_period: int
    ) -> Tuple[List[float], List[float]]:
        """Calculate Stochastic Oscillator"""
        k_values = []
        
        for i in range(len(closes)):
            if i < k_period - 1:
                k_values.append(None)
            else:
                highest_high = max(highs[i-k_period+1:i+1])
                lowest_low = min(lows[i-k_period+1:i+1])
                
                if highest_high != lowest_low:
                    k = ((closes[i] - lowest_low) / (highest_high - lowest_low)) * 100
                else:
                    k = 50
                
                k_values.append(k)
        
        # Calculate %D (moving average of %K)
        d_values = self._calculate_sma(k_values, d_period)
        
        return k_values, d_values
    
    def _calculate_williams_r(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int
    ) -> List[float]:
        """Calculate Williams %R"""
        williams_r = []
        
        for i in range(len(closes)):
            if i < period - 1:
                williams_r.append(None)
            else:
                highest_high = max(highs[i-period+1:i+1])
                lowest_low = min(lows[i-period+1:i+1])
                
                if highest_high != lowest_low:
                    wr = ((highest_high - closes[i]) / (highest_high - lowest_low)) * -100
                else:
                    wr = -50
                
                williams_r.append(wr)
        
        return williams_r
    
    def _calculate_cci(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int
    ) -> List[float]:
        """Calculate Commodity Channel Index"""
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        sma_tp = self._calculate_sma(typical_prices, period)
        
        cci_values = []
        
        for i in range(len(typical_prices)):
            if i < period - 1:
                cci_values.append(None)
            else:
                mean_deviation = np.mean([
                    abs(tp - sma_tp[i])
                    for tp in typical_prices[i-period+1:i+1]
                ])
                
                if mean_deviation != 0:
                    cci = (typical_prices[i] - sma_tp[i]) / (0.015 * mean_deviation)
                else:
                    cci = 0
                
                cci_values.append(cci)
        
        return cci_values
    
    def _calculate_obv(self, closes: List[float], volumes: List[float]) -> List[float]:
        """Calculate On Balance Volume"""
        obv = [volumes[0]]
        
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif closes[i] < closes[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])
        
        return obv
    
    def _calculate_vwap(self, closes: List[float], volumes: List[float]) -> List[float]:
        """Calculate Volume Weighted Average Price"""
        vwap_values = []
        cumulative_volume = 0
        cumulative_pv = 0
        
        for i in range(len(closes)):
            cumulative_volume += volumes[i]
            cumulative_pv += closes[i] * volumes[i]
            
            if cumulative_volume > 0:
                vwap = cumulative_pv / cumulative_volume
            else:
                vwap = closes[i]
            
            vwap_values.append(vwap)
        
        return vwap_values
    
    async def detect_patterns(
        self,
        symbol: str,
        timeframe: Timeframe,
        sensitivity: float = 0.02
    ) -> List[ChartPattern]:
        """
        Detect chart patterns
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            sensitivity: Pattern detection sensitivity
            
        Returns:
            List of detected patterns
        """
        candles = await self.get_chart_data(symbol, timeframe, limit=100)
        
        if len(candles) < 50:
            return []
        
        detected = []
        closes = [c.close for c in candles]
        
        # Detect multiple pattern types
        
        # Double Top/Bottom patterns
        patterns = await self._detect_double_patterns(candles, sensitivity)
        detected.extend(patterns)
        
        # Triangle patterns
        patterns = await self._detect_triangle_patterns(candles)
        detected.extend(patterns)
        
        # Head and Shoulders patterns
        patterns = await self._detect_head_shoulders_patterns(candles, sensitivity)
        detected.extend(patterns)
        
        self.detected_patterns.extend(detected)
        
        return detected
    
    async def _detect_double_patterns(
        self,
        candles: List[OHLCV],
        sensitivity: float
    ) -> List[ChartPattern]:
        """Detect double top and double bottom patterns"""
        patterns = []
        closes = [c.close for c in candles]
        
        # Find peaks and troughs
        peaks = self._find_peaks(closes, distance=5)
        troughs = self._find_troughs(closes, distance=5)
        
        # Double Top detection
        for i in range(len(peaks) - 1):
            for j in range(i + 1, len(peaks)):
                peak1, peak2 = peaks[i], peaks[j]
                price1, price2 = closes[peak1], closes[peak2]
                
                # Check if peaks are similar
                if abs(price1 - price2) / price1 < sensitivity:
                    # Check if there's a significant valley between peaks
                    valley_range = closes[peak1:peak2+1]
                    valley_price = min(valley_range)
                    
                    if valley_price < min(price1, price2) * (1 - sensitivity):
                        pattern = ChartPattern(
                            pattern_id=f"double_top_{len(patterns)+1}",
                            pattern_type=PatternType.DOUBLE_TOP,
                            symbol="",
                            timeframe=Timeframe.H1,  # Will be set by caller
                            start_date=candles[peak1].timestamp,
                            end_date=candles[peak2].timestamp,
                            key_points=[
                                {'timestamp': candles[peak1].timestamp.isoformat(), 'price': price1, 'type': 'peak'},
                                {'timestamp': candles[peak2].timestamp.isoformat(), 'price': price2, 'type': 'peak'}
                            ],
                            confidence=0.8,
                            target_price=min(price1, price2) * (1 - sensitivity * 2),
                            stop_loss=max(price1, price2) * (1 + sensitivity),
                            detected_at=datetime.now()
                        )
                        patterns.append(pattern)
                        break
        
        # Double Bottom detection
        for i in range(len(troughs) - 1):
            for j in range(i + 1, len(troughs)):
                trough1, trough2 = troughs[i], troughs[j]
                price1, price2 = closes[trough1], closes[trough2]
                
                # Check if troughs are similar
                if abs(price1 - price2) / price1 < sensitivity:
                    # Check if there's a significant peak between troughs
                    peak_range = closes[trough1:trough2+1]
                    peak_price = max(peak_range)
                    
                    if peak_price > max(price1, price2) * (1 + sensitivity):
                        pattern = ChartPattern(
                            pattern_id=f"double_bottom_{len(patterns)+1}",
                            pattern_type=PatternType.DOUBLE_BOTTOM,
                            symbol="",
                            timeframe=Timeframe.H1,
                            start_date=candles[trough1].timestamp,
                            end_date=candles[trough2].timestamp,
                            key_points=[
                                {'timestamp': candles[trough1].timestamp.isoformat(), 'price': price1, 'type': 'trough'},
                                {'timestamp': candles[trough2].timestamp.isoformat(), 'price': price2, 'type': 'trough'}
                            ],
                            confidence=0.8,
                            target_price=max(price1, price2) * (1 + sensitivity * 2),
                            stop_loss=min(price1, price2) * (1 - sensitivity),
                            detected_at=datetime.now()
                        )
                        patterns.append(pattern)
                        break
        
        return patterns
    
    async def _detect_triangle_patterns(
        self,
        candles: List[OHLCV]
    ) -> List[ChartPattern]:
        """Detect triangle patterns"""
        patterns = []
        
        if len(candles) < 20:
            return patterns
        
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        
        # Simple triangle detection based on trend lines
        recent_highs = highs[-20:]
        recent_lows = lows[-20:]
        
        # Calculate trend lines
        high_slope = self._calculate_trend_slope(range(len(recent_highs)), recent_highs)
        low_slope = self._calculate_trend_slope(range(len(recent_lows)), recent_lows)
        
        # Ascending triangle (flat resistance, rising support)
        if abs(high_slope) < 0.1 and low_slope > 0.1:
            pattern = ChartPattern(
                pattern_id=f"triangle_asc_{len(patterns)+1}",
                pattern_type=PatternType.TRIANGLE_ASCENDING,
                symbol="",
                timeframe=Timeframe.H1,
                start_date=candles[-20].timestamp,
                end_date=candles[-1].timestamp,
                key_points=[
                    {'type': 'resistance', 'slope': high_slope},
                    {'type': 'support', 'slope': low_slope}
                ],
                confidence=0.7,
                target_price=max(highs[-20:]),
                stop_loss=min(lows[-20:]),
                detected_at=datetime.now()
            )
            patterns.append(pattern)
        
        # Descending triangle (falling resistance, flat support)
        elif high_slope < -0.1 and abs(low_slope) < 0.1:
            pattern = ChartPattern(
                pattern_id=f"triangle_desc_{len(patterns)+1}",
                pattern_type=PatternType.TRIANGLE_DESCENDING,
                symbol="",
                timeframe=Timeframe.H1,
                start_date=candles[-20].timestamp,
                end_date=candles[-1].timestamp,
                key_points=[
                    {'type': 'resistance', 'slope': high_slope},
                    {'type': 'support', 'slope': low_slope}
                ],
                confidence=0.7,
                target_price=min(lows[-20:]),
                stop_loss=max(highs[-20:]),
                detected_at=datetime.now()
            )
            patterns.append(pattern)
        
        return patterns
    
    async def _detect_head_shoulders_patterns(
        self,
        candles: List[OHLCV],
        sensitivity: float
    ) -> List[ChartPattern]:
        """Detect head and shoulders patterns"""
        patterns = []
        
        if len(candles) < 30:
            return patterns
        
        highs = [c.high for c in candles]
        
        # Find local maxima
        peaks = self._find_peaks(highs, distance=3)
        
        # Look for head and shoulders pattern
        if len(peaks) >= 3:
            for i in range(len(peaks) - 2):
                left_shoulder = peaks[i]
                head = peaks[i + 1]
                right_shoulder = peaks[i + 2]
                
                ls_price = highs[left_shoulder]
                head_price = highs[head]
                rs_price = highs[right_shoulder]
                
                # Check if head is higher than shoulders
                if (head_price > ls_price * (1 + sensitivity) and 
                    head_price > rs_price * (1 + sensitivity)):
                    
                    # Check if shoulders are similar
                    if abs(ls_price - rs_price) / ls_price < sensitivity * 2:
                        pattern = ChartPattern(
                            pattern_id=f"hns_{len(patterns)+1}",
                            pattern_type=PatternType.HEAD_AND_SHOULDERS,
                            symbol="",
                            timeframe=Timeframe.H1,
                            start_date=candles[left_shoulder].timestamp,
                            end_date=candles[right_shoulder].timestamp,
                            key_points=[
                                {'timestamp': candles[left_shoulder].timestamp.isoformat(), 'price': ls_price, 'type': 'left_shoulder'},
                                {'timestamp': candles[head].timestamp.isoformat(), 'price': head_price, 'type': 'head'},
                                {'timestamp': candles[right_shoulder].timestamp.isoformat(), 'price': rs_price, 'type': 'right_shoulder'}
                            ],
                            confidence=0.75,
                            target_price=min([ls_price, rs_price]) * (1 - sensitivity),
                            stop_loss=head_price * (1 + sensitivity),
                            detected_at=datetime.now()
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def _calculate_trend_slope(self, x: range, y: List[float]) -> float:
        """Calculate trend line slope"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        # Simple linear regression
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def _find_peaks(self, data: List[float], distance: int = 10) -> List[int]:
        """Find peaks in data"""
        peaks = []
        for i in range(distance, len(data) - distance):
            if all(data[i] > data[i-j] for j in range(1, distance+1)) and \
               all(data[i] > data[i+j] for j in range(1, distance+1)):
                peaks.append(i)
        return peaks
    
    def _find_troughs(self, data: List[float], distance: int = 10) -> List[int]:
        """Find troughs in data"""
        troughs = []
        for i in range(distance, len(data) - distance):
            if all(data[i] < data[i-j] for j in range(1, distance+1)) and \
               all(data[i] < data[i+j] for j in range(1, distance+1)):
                troughs.append(i)
        return troughs
    
    async def get_support_resistance(
        self,
        symbol: str,
        timeframe: Timeframe,
        lookback_period: int = 50
    ) -> List[SupportResistanceLevel]:
        """
        Calculate support and resistance levels
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            lookback_period: Number of candles to analyze
            
        Returns:
            List of support and resistance levels
        """
        candles = await self.get_chart_data(symbol, timeframe, limit=lookback_period)
        
        if len(candles) < 20:
            return []
        
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        
        # Find potential support and resistance levels
        resistance_levels = self._find_price_levels(highs)
        support_levels = self._find_price_levels(lows)
        
        # Calculate strength for each level
        resistance_with_strength = []
        for price in resistance_levels:
            strength = self._calculate_level_strength(highs, price)
            resistance_with_strength.append(SupportResistanceLevel(
                level_type="resistance",
                price=price,
                strength=strength['strength'],
                touch_count=strength['touch_count'],
                last_touched=strength['last_touched'],
                is_major=strength['strength'] > 0.7
            ))
        
        support_with_strength = []
        for price in support_levels:
            strength = self._calculate_level_strength(lows, price)
            support_with_strength.append(SupportResistanceLevel(
                level_type="support",
                price=price,
                strength=strength['strength'],
                touch_count=strength['touch_count'],
                last_touched=strength['last_touched'],
                is_major=strength['strength'] > 0.7
            ))
        
        # Sort by strength and return top levels
        all_levels = resistance_with_strength + support_with_strength
        all_levels.sort(key=lambda x: x.strength, reverse=True)
        
        # Return top 10 levels
        return all_levels[:10]
    
    def _find_price_levels(self, prices: List[float], tolerance: float = 0.002) -> List[float]:
        """Find significant price levels"""
        levels = []
        
        # Find local maxima/minima
        peaks = self._find_peaks(prices, distance=5) if max(prices) == max(prices[:len(prices)//2]) else []
        troughs = self._find_troughs(prices, distance=5)
        
        # Collect potential levels
        potential_levels = []
        
        for peak in peaks:
            potential_levels.append(prices[peak])
        
        for trough in troughs:
            potential_levels.append(prices[trough])
        
        # Group similar levels
        grouped_levels = []
        for level in potential_levels:
            # Check if level is close to existing group
            found_group = False
            for group in grouped_levels:
                if abs(level - group['price']) / group['price'] < tolerance:
                    group['prices'].append(level)
                    found_group = True
                    break
            
            if not found_group:
                grouped_levels.append({
                    'price': level,
                    'prices': [level]
                })
        
        # Calculate average for each group
        for group in grouped_levels:
            group['price'] = np.mean(group['prices'])
            group['count'] = len(group['prices'])
        
        # Sort by count and return
        grouped_levels.sort(key=lambda x: x['count'], reverse=True)
        
        return [level['price'] for level in grouped_levels]
    
    def _calculate_level_strength(self, prices: List[float], level: float) -> Dict[str, Any]:
        """Calculate strength of a support/resistance level"""
        touches = 0
        last_touch = None
        
        tolerance = level * 0.002  # 0.2% tolerance
        
        for i, price in enumerate(prices):
            if abs(price - level) <= tolerance:
                touches += 1
                last_touch = i
        
        # Calculate strength based on touches and recency
        if touches == 0:
            strength = 0
        else:
            # More touches = higher strength
            # More recent touches = higher strength
            recency_factor = 1 - (last_touch / len(prices))
            strength = min(1.0, (touches * 0.2) + (recency_factor * 0.3))
        
        return {
            'strength': strength,
            'touch_count': touches,
            'last_touched': candles[len(prices) - last_touch - 1].timestamp if last_touch is not None else None
        }
    
    async def get_volume_analysis(
        self,
        symbol: str,
        timeframe: Timeframe,
        lookback_period: int = 100
    ) -> VolumeAnalysis:
        """
        Analyze volume patterns
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            lookback_period: Number of candles to analyze
            
        Returns:
            Volume analysis data
        """
        candles = await self.get_chart_data(symbol, timeframe, limit=lookback_period)
        
        if len(candles) < 20:
            raise ValueError("Insufficient data for volume analysis")
        
        volumes = [c.volume for c in candles]
        prices = [c.close for c in candles]
        
        # Calculate volume statistics
        avg_volume = np.mean(volumes)
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Determine volume trend
        recent_avg = np.mean(volumes[-10:])
        if current_volume > recent_avg * 1.2:
            volume_trend = "increasing"
        elif current_volume < recent_avg * 0.8:
            volume_trend = "decreasing"
        else:
            volume_trend = "stable"
        
        # Find high and low volume dates
        volume_threshold_high = np.percentile(volumes, 80)
        volume_threshold_low = np.percentile(volumes, 20)
        
        high_volume_dates = [candles[i].timestamp for i, v in enumerate(volumes) if v > volume_threshold_high]
        low_volume_dates = [candles[i].timestamp for i, v in enumerate(volumes) if v < volume_threshold_low]
        
        # Find volume spikes (significant price movement with volume)
        volume_spikes = []
        for i in range(1, len(candles)):
            price_change = abs(candles[i].close - candles[i-1].close) / candles[i-1].close
            volume_increase = volumes[i] / avg_volume
            
            if price_change > 0.05 and volume_increase > 2:  # 5% price move with 2x average volume
                volume_spikes.append({
                    'timestamp': candles[i].timestamp.isoformat(),
                    'price_change': price_change,
                    'volume_ratio': volume_increase,
                    'type': 'breakout' if candles[i].close > candles[i-1].close else 'breakdown'
                })
        
        # Calculate OBV
        obv_values = self._calculate_obv(prices, volumes)
        obv_data = [
            {
                'timestamp': candles[i].timestamp.isoformat(),
                'value': obv_values[i]
            }
            for i in range(len(obv_values))
        ]
        
        # Calculate VWAP
        vwap_value = self._calculate_vwap(prices, volumes)[-1]
        
        return VolumeAnalysis(
            symbol=symbol,
            timeframe=timeframe,
            average_volume=avg_volume,
            current_volume=current_volume,
            volume_ratio=volume_ratio,
            volume_trend=volume_trend,
            high_volume_dates=high_volume_dates,
            low_volume_dates=low_volume_dates,
            volume_spikes=volume_spikes,
            obv_values=obv_data,
            vwap_value=vwap_value
        )
    
    async def get_tradingview_widget(
        self,
        symbol: str,
        interval: str = "D",
        studies: Optional[List[str]] = None
    ) -> TradingViewWidget:
        """
        Get TradingView widget configuration
        
        Args:
            symbol: Trading symbol
            interval: Chart interval
            studies: List of study IDs to include
            
        Returns:
            TradingView widget configuration
        """
        widget = TradingViewWidget(
            symbol=symbol,
            interval=interval,
            studies=studies or [
                'RSI@tv-basicstudies',
                'MACD@tv-basicstudies',
                'BB@tv-basicstudies'
            ]
        )
        
        return widget
    
    async def get_multi_timeframe_analysis(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive multi-timeframe analysis
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Multi-timeframe analysis with consensus
        """
        timeframes = [Timeframe.M15, Timeframe.H1, Timeframe.H4, Timeframe.D1]
        
        analysis = {}
        
        for tf in timeframes:
            try:
                candles = await self.get_chart_data(symbol, tf, limit=100)
                
                if not candles:
                    continue
                
                closes = [c.close for c in candles]
                
                # Calculate multiple indicators
                sma_20 = self._calculate_sma(closes, 20)
                sma_50 = self._calculate_sma(closes, 50)
                sma_200 = self._calculate_sma(closes, 200)
                
                rsi = self._calculate_rsi(closes, 14)
                
                current_price = closes[-1]
                sma_20_current = sma_20[-1] if sma_20[-1] else current_price
                sma_50_current = sma_50[-1] if sma_50[-1] else current_price
                sma_200_current = sma_200[-1] if sma_200[-1] else current_price
                rsi_current = rsi[-1] if rsi[-1] else 50
                
                # Determine trend
                if current_price > sma_20_current > sma_50_current > sma_200_current:
                    trend = "strong_uptrend"
                elif current_price > sma_20_current > sma_50_current:
                    trend = "uptrend"
                elif current_price < sma_20_current < sma_50_current < sma_200_current:
                    trend = "strong_downtrend"
                elif current_price < sma_20_current < sma_50_current:
                    trend = "downtrend"
                else:
                    trend = "sideways"
                
                # Determine momentum
                if rsi_current > 70:
                    momentum = "overbought"
                elif rsi_current < 30:
                    momentum = "oversold"
                elif rsi_current > 50:
                    momentum = "bullish"
                elif rsi_current < 50:
                    momentum = "bearish"
                else:
                    momentum = "neutral"
                
                # Calculate volatility
                price_changes = [abs(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, min(20, len(closes)))]
                volatility = np.mean(price_changes) * 100
                
                # Generate signal
                if trend in ["strong_uptrend", "uptrend"] and momentum in ["bullish", "neutral"] and rsi_current < 70:
                    signal = "bullish"
                elif trend in ["strong_downtrend", "downtrend"] and momentum in ["bearish", "neutral"] and rsi_current > 30:
                    signal = "bearish"
                else:
                    signal = "neutral"
                
                analysis[tf.value] = {
                    'trend': trend,
                    'momentum': momentum,
                    'current_price': current_price,
                    'sma_20': sma_20_current,
                    'sma_50': sma_50_current,
                    'sma_200': sma_200_current,
                    'rsi': rsi_current,
                    'volatility': volatility,
                    'signal': signal,
                    'confidence': self._calculate_signal_confidence(trend, momentum, rsi_current)
                }
                
            except Exception as e:
                print(f"Error analyzing {symbol} on {tf.value}: {e}")
                continue
        
        # Calculate overall consensus
        if analysis:
            signals = [a['signal'] for a in analysis.values()]
            bullish = signals.count('bullish')
            bearish = signals.count('bearish')
            
            if bullish > bearish:
                consensus = 'bullish'
                confidence = bullish / len(signals)
            elif bearish > bullish:
                consensus = 'bearish'
                confidence = bearish / len(signals)
            else:
                consensus = 'neutral'
                confidence = 0.5
            
            # Weighted consensus (higher timeframes have more weight)
            timeframe_weights = {
                '15m': 0.1,
                '1h': 0.2,
                '4h': 0.3,
                '1d': 0.4
            }
            
            weighted_score = 0
            total_weight = 0
            
            for tf, data in analysis.items():
                weight = timeframe_weights.get(tf, 0.1)
                if data['signal'] == 'bullish':
                    weighted_score += weight
                elif data['signal'] == 'bearish':
                    weighted_score -= weight
                total_weight += weight
            
            if total_weight > 0:
                weighted_consensus = 'bullish' if weighted_score > 0 else 'bearish' if weighted_score < 0 else 'neutral'
            else:
                weighted_consensus = consensus
        else:
            consensus = 'neutral'
            weighted_consensus = 'neutral'
            confidence = 0.5
        
        return {
            'symbol': symbol,
            'timeframes': analysis,
            'consensus': consensus,
            'weighted_consensus': weighted_consensus,
            'confidence': confidence,
            'analyzed_at': datetime.now().isoformat(),
            'summary': {
                'strongest_timeframe': max(analysis.items(), key=lambda x: x[1]['confidence'])[0] if analysis else None,
                'most_volatile_timeframe': max(analysis.items(), key=lambda x: x[1]['volatility'])[0] if analysis else None,
                'overall_trend': max(set([a['trend'] for a in analysis.values()]), key=[a['trend'] for a in analysis.values()].count) if analysis else 'unknown'
            }
        }
    
    def _calculate_signal_confidence(self, trend: str, momentum: str, rsi: float) -> float:
        """Calculate confidence score for a signal"""
        confidence = 0.5  # Base confidence
        
        # Trend factor
        if 'uptrend' in trend:
            confidence += 0.2
        elif 'downtrend' in trend:
            confidence -= 0.2
        
        # Momentum factor
        if momentum == 'bullish':
            confidence += 0.15
        elif momentum == 'bearish':
            confidence -= 0.15
        elif momentum in ['overbought', 'oversold']:
            confidence -= 0.1
        
        # RSI factor
        if 30 < rsi < 70:  # Normal range
            confidence += 0.1
        elif rsi > 80 or rsi < 20:  # Extreme
            confidence -= 0.2
        elif rsi > 70 or rsi < 30:  # Near extreme
            confidence -= 0.1
        
        return max(0, min(1, confidence))


# Global instance
advanced_charts = AdvancedCharts()


async def test_advanced_charts():
    """Test advanced charts functionality"""
    charts = AdvancedCharts()
    
    symbol = "BTC/USDT"
    timeframe = Timeframe.H1
    
    print("=== Advanced Charts Test ===")
    
    # 1. Get chart data
    candles = await charts.get_chart_data(symbol, timeframe, limit=50)
    print(f"\n1. Chart Data:")
    print(f"   Candles: {len(candles)}")
    print(f"   Last close: ${candles[-1].close:.2f}")
    print(f"   Volume: {candles[-1].volume:,.0f}")
    
    # 2. Calculate indicators
    print(f"\n2. Technical Indicators:")
    rsi = await charts.calculate_indicator(symbol, timeframe, IndicatorType.RSI)
    print(f"   RSI: {rsi.values[-1]['value']:.2f}")
    
    macd = await charts.calculate_indicator(symbol, timeframe, IndicatorType.MACD)
    print(f"   MACD: {macd.values[-1]['macd']:.4f}")
    
    bb = await charts.calculate_indicator(symbol, timeframe, IndicatorType.BOLLINGER_BANDS)
    print(f"   BB Upper: ${bb.values[-1]['upper']:.2f}")
    print(f"   BB Lower: ${bb.values[-1]['lower']:.2f}")
    
    # 3. Volume analysis
    print(f"\n3. Volume Analysis:")
    volume_analysis = await charts.get_volume_analysis(symbol, timeframe)
    print(f"   Average Volume: {volume_analysis.average_volume:,.0f}")
    print(f"   Current Volume: {volume_analysis.current_volume:,.0f}")
    print(f"   Volume Ratio: {volume_analysis.volume_ratio:.2f}x")
    print(f"   Volume Trend: {volume_analysis.volume_trend}")
    print(f"   VWAP: ${volume_analysis.vwap_value:.2f}")
    print(f"   Volume Spikes: {len(volume_analysis.volume_spikes)}")
    
    # 4. Support/Resistance
    print(f"\n4. Support & Resistance:")
    sr_levels = await charts.get_support_resistance(symbol, timeframe)
    print(f"   Levels found: {len(sr_levels)}")
    for i, level in enumerate(sr_levels[:5]):
        print(f"   {level.level_type.title()}: ${level.price:.2f} (strength: {level.strength:.2f})")
    
    # 5. Detect patterns
    print(f"\n5. Chart Patterns:")
    patterns = await charts.detect_patterns(symbol, timeframe)
    print(f"   Patterns detected: {len(patterns)}")
    for pattern in patterns:
        print(f"   {pattern.pattern_type.value}: confidence {pattern.confidence:.2f}")
    
    # 6. Multi-timeframe analysis
    print(f"\n6. Multi-Timeframe Analysis:")
    mtf = await charts.get_multi_timeframe_analysis(symbol)
    print(f"   Consensus: {mtf['consensus']}")
    print(f"   Weighted Consensus: {mtf['weighted_consensus']}")
    print(f"   Confidence: {mtf['confidence']:.2f}")
    print(f"   Strongest Timeframe: {mtf['summary']['strongest_timeframe']}")
    
    print(f"\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_advanced_charts())