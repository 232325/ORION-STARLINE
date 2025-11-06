"""
Technical Indicators for Market Analysis
=======================================

Texnik va fundamental indicatorlar.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')


class TechnicalIndicators:
    """Texnik indicatorlar sinfi"""
    
    @staticmethod
    def calculate_sma(data: pd.Series, window: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=window).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, window: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=window).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, window: int = 20, 
                                num_std: float = 2) -> Dict[str, pd.Series]:
        """Bollinger Bands"""
        sma = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        
        return {
            'upper': sma + (std * num_std),
            'middle': sma,
            'lower': sma - (std * num_std),
            'width': (sma + (std * num_std)) - (sma - (std * num_std))
        }
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, 
                      signal: int = 9) -> Dict[str, pd.Series]:
        """MACD indicator"""
        ema_fast = TechnicalIndicators.calculate_ema(data, fast)
        ema_slow = TechnicalIndicators.calculate_ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, 
                     window: int = 14) -> pd.Series:
        """Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return true_range.rolling(window=window).mean()
    
    @staticmethod
    def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                           k_window: int = 14, d_window: int = 3) -> Dict[str, pd.Series]:
        """Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return {
            'k': k_percent,
            'd': d_percent
        }
    
    @staticmethod
    def calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series,
                           window: int = 14) -> pd.Series:
        """Williams %R"""
        highest_high = high.rolling(window=window).max()
        lowest_low = low.rolling(window=window).min()
        return -100 * ((highest_high - close) / (highest_high - lowest_low))
    
    @staticmethod
    def calculate_momentum(data: pd.Series, window: int = 10) -> pd.Series:
        """Momentum"""
        return data / data.shift(window) - 1
    
    @staticmethod
    def calculate_roc(data: pd.Series, window: int = 10) -> pd.Series:
        """Rate of Change"""
        return ((data - data.shift(window)) / data.shift(window)) * 100
    
    @staticmethod
    def calculate_vroc(high: pd.Series, low: pd.Series, close: pd.Series,
                      volume: pd.Series, window: int = 14) -> pd.Series:
        """Volume Rate of Change"""
        price_change = (high + low + close) / 3
        vroc = ((volume - volume.shift(window)) / volume.shift(window)) * 100
        return vroc
    
    @staticmethod
    def calculate_ad_line(high: pd.Series, low: pd.Series, close: pd.Series,
                         volume: pd.Series) -> pd.Series:
        """Accumulation/Distribution Line"""
        money_flow_multiplier = ((close - low) - (high - close)) / (high - low)
        money_flow_volume = money_flow_multiplier * volume
        return money_flow_volume.cumsum()
    
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """On-Balance Volume"""
        obv = np.where(close > close.shift(1), volume, 
              np.where(close < close.shift(1), -volume, 0))
        return pd.Series(obv, index=close.index).cumsum()
    
    @staticmethod
    def calculate_pivot_points(high: pd.Series, low: pd.Series, close: pd.Series) -> Dict[str, pd.Series]:
        """Pivot Points"""
        pivot = (high + low + close) / 3
        
        return {
            'pivot': pivot,
            'r1': 2 * pivot - low,
            'r2': pivot + (high - low),
            'r3': high + 2 * (pivot - low),
            's1': 2 * pivot - high,
            's2': pivot - (high - low),
            's3': low - 2 * (high - pivot)
        }


class MarketRegimeIndicators:
    """Bozor rezhim indikatorlari"""
    
    @staticmethod
    def calculate_trend_strength(data: pd.Series, window: int = 20) -> pd.Series:
        """Trend kuchini hisoblash"""
        returns = data.pct_change().dropna()
        
        # Linear regression slope
        def regression_slope(series):
            if len(series) < 2:
                return 0
            x = np.arange(len(series))
            slope, _, _, _, _ = stats.linregress(x, series)
            return slope
        
        slope = returns.rolling(window=window).apply(regression_slope)
        
        # R-squared for trend confidence
        def r_squared(series):
            if len(series) < 2:
                return 0
            x = np.arange(len(series))
            slope, intercept, r_value, _, _ = stats.linregress(x, series)
            return r_value ** 2
        
        r2 = returns.rolling(window=window).apply(r_squared)
        
        return pd.DataFrame({
            'slope': slope,
            'r_squared': r2,
            'trend_strength': slope * r2
        })
    
    @staticmethod
    def identify_trending_ranging(data: pd.Series, window: int = 20) -> pd.Series:
        """Trending va ranging bozorlarni aniqlash"""
        returns = data.pct_change().dropna()
        
        # ADX calculation
        high = data.rolling(window=2).max()
        low = data.rolling(window=2).min()
        tr = pd.concat([
            high - low,
            abs(high - data.shift(1)),
            abs(low - data.shift(1))
        ], axis=1).max(axis=1)
        
        dm_plus = np.where((high - high.shift(1)) > (low.shift(1) - low),
                          np.maximum(high - high.shift(1), 0), 0)
        dm_minus = np.where((low.shift(1) - low) > (high - high.shift(1)),
                           np.maximum(low.shift(1) - low, 0), 0)
        
        di_plus = 100 * (pd.Series(dm_plus, index=data.index).rolling(window=14).mean() /
                         tr.rolling(window=14).mean())
        di_minus = 100 * (pd.Series(dm_minus, index=data.index).rolling(window=14).mean() /
                         tr.rolling(window=14).mean())
        
        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
        adx = dx.rolling(window=14).mean()
        
        # Trend: ADX > 25, Ranging: ADX < 20
        regime = np.where(adx > 25, 1, np.where(adx < 20, -1, 0))
        return pd.Series(regime, index=data.index)
    
    @staticmethod
    def calculate_volatility_regime(volatility: pd.Series, window: int = 20) -> pd.Series:
        """Volatility rejimini aniqlash"""
        vol_percentile = volatility.rolling(window=window*2).rank(pct=True)
        
        # High vol: top 20%, Low vol: bottom 20%
        regime = np.where(vol_percentile > 0.8, 1,
                 np.where(vol_percentile < 0.2, -1, 0))
        
        return pd.Series(regime, index=volatility.index)
    
    @staticmethod
    def detect_liquidity_regime(volume: pd.Series, window: int = 20) -> pd.Series:
        """Liquidity rejimini aniqlash"""
        vol_zscore = (volume - volume.rolling(window=window).mean()) / volume.rolling(window=window).std()
        
        # High liquidity: z-score > 1, Low liquidity: z-score < -1
        regime = np.where(vol_zscore > 1, 1,
                 np.where(vol_zscore < -1, -1, 0))
        
        return pd.Series(regime, index=volume.index)
    
    @staticmethod
    def calculate_market_efficiency_ratio(data: pd.Series, window: int = 14) -> pd.Series:
        """Market efficiency ratio (Kaufman's Adaptive Moving Average basis)"""
        abs_change = abs(data - data.shift(window))
        volatility = data.diff().abs().rolling(window=window).sum()
        
        efficiency_ratio = abs_change / volatility
        return efficiency_ratio.fillna(0)


class VolumeAnalysis:
    """Volume tahlili"""
    
    @staticmethod
    def calculate_volume_profile(price_data: pd.Series, volume_data: pd.Series,
                               price_bins: int = 100) -> Dict[str, any]:
        """Volume profile hisoblash"""
        # Price range
        min_price = price_data.min()
        max_price = price_data.max()
        price_range = np.linspace(min_price, max_price, price_bins)
        
        # Volume at each price level
        volume_at_price = np.zeros(price_bins)
        
        for i in range(len(price_range) - 1):
            mask = (price_data >= price_range[i]) & (price_data < price_range[i+1])
            volume_at_price[i] = volume_data[mask].sum()
        
        # Find POC (Point of Control - highest volume price)
        poc_idx = np.argmax(volume_at_price)
        poc_price = price_range[poc_idx]
        poc_volume = volume_at_price[poc_idx]
        
        # Value area (70% of volume)
        total_volume = volume_at_price.sum()
        target_volume = total_volume * 0.7
        
        # Expand from POC until we reach 70% of volume
        value_area_volume = poc_volume
        value_area_range = [poc_price, poc_price]
        
        # Expand above and below POC
        above_poc = poc_idx
        below_poc = poc_idx - 1
        
        while value_area_volume < target_volume and (above_poc < price_bins - 1 or below_poc >= 0):
            above_volume = volume_at_price[above_poc] if above_poc < price_bins - 1 else 0
            below_volume = volume_at_price[below_poc] if below_poc >= 0 else 0
            
            if above_volume >= below_volume and above_poc < price_bins - 1:
                value_area_volume += above_volume
                value_area_range[1] = price_range[above_poc + 1]
                above_poc += 1
            elif below_poc >= 0:
                value_area_volume += below_volume
                value_area_range[0] = price_range[below_poc]
                below_poc -= 1
            else:
                break
        
        return {
            'poc_price': poc_price,
            'poc_volume': poc_volume,
            'value_area_high': value_area_range[1],
            'value_area_low': value_area_range[0],
            'price_range': price_range,
            'volume_distribution': volume_at_price,
            'total_volume': total_volume
        }
    
    @staticmethod
    def analyze_volume_trends(volume_data: pd.Series, window: int = 20) -> Dict[str, pd.Series]:
        """Volume trend tahlili"""
        volume_sma = volume_data.rolling(window=window).mean()
        volume_ratio = volume_data / volume_sma
        
        # Volume trend direction
        volume_trend = np.where(volume_ratio > 1.1, 1,
                       np.where(volume_ratio < 0.9, -1, 0))
        
        return {
            'volume_ratio': volume_ratio,
            'volume_trend': pd.Series(volume_trend, index=volume_data.index),
            'volume_sma': volume_sma
        }


class CorrelationAnalysis:
    """Korrelyatsiya tahlili"""
    
    @staticmethod
    def calculate_rolling_correlation(data1: pd.Series, data2: pd.Series, 
                                   window: int = 30) -> pd.Series:
        """Rolling correlation hisoblash"""
        return data1.rolling(window=window).corr(data2)
    
    @staticmethod
    def find_correlation_clusters(data_matrix: pd.DataFrame, 
                                threshold: float = 0.7) -> List[List[str]]:
        """Korrelyatsiya klasterlarini topish"""
        corr_matrix = data_matrix.corr()
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > threshold:
                    high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))
        
        # Group into clusters (simple implementation)
        clusters = []
        used_symbols = set()
        
        for pair in high_corr_pairs:
            symbol1, symbol2 = pair
            
            if symbol1 in used_symbols or symbol2 in used_symbols:
                continue
            
            # Create new cluster
            cluster = [symbol1, symbol2]
            used_symbols.update([symbol1, symbol2])
            
            # Add other highly correlated symbols
            for other_pair in high_corr_pairs:
                other1, other2 = other_pair
                
                if other1 in cluster and other2 not in used_symbols:
                    cluster.append(other2)
                    used_symbols.add(other2)
                elif other2 in cluster and other1 not in used_symbols:
                    cluster.append(other1)
                    used_symbols.add(other1)
            
            clusters.append(cluster)
        
        return clusters


def add_all_indicators(df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
    """Barcha indikatorlarni DataFrame ga qo'shish"""
    df = df.copy()
    
    # Ensure we have OHLCV data
    required_cols = ['open', 'high', 'low', 'close']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"OHLC data required. Available columns: {list(df.columns)}")
    
    # Basic indicators
    indicators = {}
    
    # Moving averages
    for period in [5, 10, 20, 50, 100, 200]:
        indicators[f'sma_{period}'] = TechnicalIndicators.calculate_sma(df['close'], period)
        indicators[f'ema_{period}'] = TechnicalIndicators.calculate_ema(df['close'], period)
    
    # RSI
    indicators['rsi_14'] = TechnicalIndicators.calculate_rsi(df['close'])
    
    # Bollinger Bands
    bb = TechnicalIndicators.calculate_bollinger_bands(df['close'])
    indicators.update({f'bb_{k}': v for k, v in bb.items()})
    
    # MACD
    macd = TechnicalIndicators.calculate_macd(df['close'])
    indicators.update({f'macd_{k}': v for k, v in macd.items()})
    
    # ATR
    indicators['atr_14'] = TechnicalIndicators.calculate_atr(df['high'], df['low'], df['close'])
    
    # Stochastic
    if 'high' in df.columns and 'low' in df.columns:
        stoch = TechnicalIndicators.calculate_stochastic(df['high'], df['low'], df['close'])
        indicators.update({f'stoch_{k}': v for k, v in stoch.items()})
        
        indicators['williams_r'] = TechnicalIndicators.calculate_williams_r(df['high'], df['low'], df['close'])
    
    # Momentum indicators
    indicators['momentum_10'] = TechnicalIndicators.calculate_momentum(df['close'])
    indicators['roc_10'] = TechnicalIndicators.calculate_roc(df['close'])
    
    # Volume indicators (if volume data available)
    if 'volume' in df.columns:
        indicators['obv'] = TechnicalIndicators.calculate_obv(df['close'], df['volume'])
        indicators['ad_line'] = TechnicalIndicators.calculate_ad_line(df['high'], df['low'], df['close'], df['volume'])
        
        vol_analysis = VolumeAnalysis.analyze_volume_trends(df['volume'])
        indicators.update({f'vol_{k}': v for k, v in vol_analysis.items()})
    
    # Market regime indicators
    regime_data = MarketRegimeIndicators.calculate_trend_strength(df['close'])
    indicators['trend_strength'] = regime_data['trend_strength']
    indicators['trend_slope'] = regime_data['slope']
    
    indicators['market_regime'] = MarketRegimeIndicators.identify_trending_ranging(df['close'])
    
    # Volatility regime
    volatility = df['close'].pct_change().rolling(window=20).std()
    indicators['volatility_regime'] = MarketRegimeIndicators.calculate_volatility_regime(volatility)
    
    # Liquidity regime (if volume available)
    if 'volume' in df.columns:
        indicators['liquidity_regime'] = MarketRegimeIndicators.detect_liquidity_regime(df['volume'])
    
    # Market efficiency
    indicators['efficiency_ratio'] = MarketRegimeIndicators.calculate_market_efficiency_ratio(df['close'])
    
    # Pivot points
    if 'high' in df.columns and 'low' in df.columns:
        pivots = TechnicalIndicators.calculate_pivot_points(df['high'], df['low'], df['close'])
        indicators.update({f'pivot_{k}': v for k, v in pivots.items()})
    
    # Add all indicators to DataFrame
    for name, series in indicators.items():
        df[name] = series
    
    # Add symbol identifier
    if symbol:
        df['symbol'] = symbol
    
    return df