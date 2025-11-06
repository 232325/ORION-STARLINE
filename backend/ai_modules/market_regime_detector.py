"""
Market Regime Detection System
Bozor rejimini aniqlash tizimi
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import warnings
from datetime import datetime, timedelta
import logging

# Optional sklearn import
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("sklearn not available, ML features will be disabled")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """Bozor rejim turlari"""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market" 
    SIDEWAYS_MARKET = "sideways_market"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT_MARKET = "breakout_market"
    REVERSAL_MARKET = "reversal_market"
    CONSOLIDATION = "consolidation"

@dataclass
class RegimeConfig:
    """Rejim aniqlash konfiguratsiyasi"""
    trend_threshold: float = 0.02
    volatility_threshold: float = 0.02
    volume_threshold: float = 1.5
    support_resistance_distance: float = 0.01
    ma_short_period: int = 10
    ma_long_period: int = 50
    rsi_overbought: float = 70
    rsi_oversold: float = 30
    bollinger_period: int = 20
    bollinger_std: float = 2.0

@dataclass
class MarketRegimeResult:
    """Rejim aniqlash natijasi"""
    regime: MarketRegime
    confidence: float
    indicators: Dict[str, float]
    signal_strength: float
    persistence_score: float
    timestamp: datetime

class MarketRegimeDetector:
    """Bozor rejimini aniqlash tizimi"""
    
    def __init__(self, config: RegimeConfig = None):
        self.config = config or RegimeConfig()
        self.regime_history = []
        self.ml_model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.is_trained = False
        
    def detect_regime(self, data: pd.DataFrame, timeframe: str = '1D') -> MarketRegimeResult:
        """
        Asosiy rejim aniqlash funksiyasi
        
        Args:
            data: OHLCV ma'lumotlari
            timeframe: Vaqt doirasi
            
        Returns:
            MarketRegimeResult: Aniqlangan rejim
        """
        try:
            indicators = self._calculate_all_indicators(data)
            regime_scores = self._calculate_regime_scores(indicators)
            primary_regime = self._determine_primary_regime(regime_scores)
            confidence = self._calculate_confidence(regime_scores, indicators)
            persistence = self._calculate_persistence()
            
            result = MarketRegimeResult(
                regime=primary_regime,
                confidence=confidence,
                indicators=indicators,
                signal_strength=regime_scores[primary_regime.value],
                persistence_score=persistence,
                timestamp=datetime.now()
            )
            
            # Tarixni saqlash
            self.regime_history.append(result)
            if len(self.regime_history) > 1000:
                self.regime_history = self.regime_history[-1000:]
                
            return result
            
        except Exception as e:
            logger.error(f"Rejim aniqlashda xatolik: {e}")
            return MarketRegimeResult(
                regime=MarketRegime.SIDEWAYS_MARKET,
                confidence=0.0,
                indicators={},
                signal_strength=0.0,
                persistence_score=0.0,
                timestamp=datetime.now()
            )
    
    def _calculate_all_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Barcha texnik indikatori hisoblash"""
        indicators = {}
        
        try:
            close = data['close'].values
            high = data['high'].values
            low = data['low'].values
            volume = data['volume'].values
            
            # Trend indikatori
            indicators['sma_10'] = self._sma(close, self.config.ma_short_period)
            indicators['sma_50'] = self._sma(close, self.config.ma_long_period)
            indicators['ema_12'] = self._ema(close, 12)
            indicators['ema_26'] = self._ema(close, 26)
            
            # MACD
            macd_line, macd_signal, macd_hist = self._macd(close)
            indicators['macd'] = macd_line
            indicators['macd_signal'] = macd_signal
            indicators['macd_hist'] = macd_hist
            
            # ADX and DI
            indicators['adx'] = self._adx(high, low, close, 14)
            indicators['plus_di'] = self._plus_di(high, low, close, 14)
            indicators['minus_di'] = self._minus_di(high, low, close, 14)
            
            # Momentum indikatori
            indicators['rsi'] = self._rsi(close, 14)
            stoch_k, stoch_d = self._stochastic(high, low, close)
            indicators['stoch_k'] = stoch_k
            indicators['stoch_d'] = stoch_d
            indicators['williams_r'] = self._williams_r(high, low, close, 14)
            indicators['momentum'] = self._momentum(close, 10)
            indicators['roc'] = self._roc(close, 10)
            
            # Volatility indikatori
            indicators['atr'] = self._atr(high, low, close, 14)
            bb_upper, bb_middle, bb_lower = self._bollinger_bands(close, 20, 2.0)
            indicators['bollinger_upper'] = bb_upper
            indicators['bollinger_middle'] = bb_middle
            indicators['bollinger_lower'] = bb_lower
            indicators['bollinger_width'] = bb_upper - bb_lower
            indicators['volatility'] = np.std(close[-20:]) / np.mean(close[-20:]) if len(close) >= 20 else 0.02
            
            # Volume indikatori
            indicators['obv'] = self._obv(close, volume)
            indicators['ad'] = self._ad(high, low, close, volume)
            indicators['volume_sma'] = self._sma(volume.astype(float), 20)
            indicators['volume_ratio'] = volume[-1] / indicators['volume_sma'] if indicators['volume_sma'] > 0 else 0
            
            # Support/Resistance
            sr_levels = self._calculate_support_resistance(data)
            indicators['support_level'] = sr_levels['support']
            indicators['resistance_level'] = sr_levels['resistance']
            if sr_levels['resistance'] > sr_levels['support']:
                indicators['price_position'] = (close[-1] - sr_levels['support']) / (sr_levels['resistance'] - sr_levels['support'])
            else:
                indicators['price_position'] = 0.5
            
            # Market breadth (agar multiple instruments bo'lsa)
            if 'symbols' in data.columns:
                indicators['market_breadth'] = self._calculate_market_breadth(data)
            else:
                indicators['market_breadth'] = 0.5
            
            # Seasonality (odatda yil va oy uchun)
            indicators['seasonal_factor'] = self._calculate_seasonality()
            
        except Exception as e:
            logger.error(f"Indikator hisoblashda xatolik: {e}")
            
        return indicators
    
    # Technical Indicator Functions
    def _sma(self, data: np.ndarray, period: int) -> float:
        """Simple Moving Average"""
        if len(data) < period:
            return data[-1] if len(data) > 0 else 0.0
        return np.mean(data[-period:])
    
    def _ema(self, data: np.ndarray, period: int) -> float:
        """Exponential Moving Average"""
        if len(data) < period:
            return data[-1] if len(data) > 0 else 0.0
        alpha = 2.0 / (period + 1)
        ema = data[0]
        for price in data[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema
    
    def _macd(self, data: np.ndarray) -> Tuple[float, float, float]:
        """MACD indicator"""
        if len(data) < 26:
            return 0.0, 0.0, 0.0
        ema_12 = self._ema(data, 12)
        ema_26 = self._ema(data, 26)
        macd_line = ema_12 - ema_26
        
        # Signal line (simplified)
        signal_line = macd_line * 0.9  # Simplified
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def _rsi(self, data: np.ndarray, period: int) -> float:
        """Relative Strength Index"""
        if len(data) < period + 1:
            return 50.0
        
        deltas = np.diff(data)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _stochastic(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Tuple[float, float]:
        """Stochastic oscillator"""
        if len(close) < 14:
            return 50.0, 50.0
        
        period = 14
        lowest_low = np.min(low[-period:])
        highest_high = np.max(high[-period:])
        
        if highest_high == lowest_low:
            return 50.0, 50.0
        
        k_percent = 100 * (close[-1] - lowest_low) / (highest_high - lowest_low)
        
        # %D line (simplified)
        d_percent = k_percent * 0.9  # Simplified
        
        return k_percent, d_percent
    
    def _williams_r(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> float:
        """Williams %R indicator"""
        if len(close) < period:
            return -50.0
        
        highest_high = np.max(high[-period:])
        lowest_low = np.min(low[-period:])
        
        if highest_high == lowest_low:
            return -50.0
        
        williams_r = -100 * (highest_high - close[-1]) / (highest_high - lowest_low)
        return williams_r
    
    def _momentum(self, data: np.ndarray, period: int) -> float:
        """Momentum indicator"""
        if len(data) < period + 1:
            return 0.0
        return data[-1] - data[-(period + 1)]
    
    def _roc(self, data: np.ndarray, period: int) -> float:
        """Rate of Change indicator"""
        if len(data) < period + 1:
            return 0.0
        return ((data[-1] - data[-(period + 1)]) / data[-(period + 1)]) * 100
    
    def _atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> float:
        """Average True Range"""
        if len(close) < 2:
            return 0.0
        
        # True range calculation
        high_low = high[1:] - low[1:]  # Skip first element
        high_close = np.abs(high[1:] - close[:-1])  # Align arrays
        low_close = np.abs(low[:-1] - close[:-1])   # Align arrays
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        
        if len(true_range) < period:
            return np.mean(true_range) if len(true_range) > 0 else 0.0
        
        return np.mean(true_range[-period:])
    
    def _bollinger_bands(self, data: np.ndarray, period: int, std_dev: float) -> Tuple[float, float, float]:
        """Bollinger Bands"""
        if len(data) < period:
            last_price = data[-1] if len(data) > 0 else 0.0
            return last_price, last_price, last_price
        
        sma = np.mean(data[-period:])
        std = np.std(data[-period:])
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    def _obv(self, close: np.ndarray, volume: np.ndarray) -> float:
        """On Balance Volume"""
        if len(close) < 2:
            return volume[-1] if len(volume) > 0 else 0.0
        
        obv = 0.0
        for i in range(1, len(close)):
            if close[i] > close[i-1]:
                obv += volume[i]
            elif close[i] < close[i-1]:
                obv -= volume[i]
        
        return obv
    
    def _ad(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray) -> float:
        """Accumulation/Distribution Line"""
        if len(close) < 1:
            return 0.0
        
        ad_line = 0.0
        for i in range(len(close)):
            if i == 0:
                continue
            
            clv = ((close[i] - low[i]) - (high[i] - close[i])) / (high[i] - low[i]) if high[i] != low[i] else 0
            ad_line += clv * volume[i]
        
        return ad_line
    
    def _adx(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> float:
        """Average Directional Index (simplified)"""
        if len(close) < period + 1:
            return 25.0
        
        # Simplified ADX calculation
        up_moves = []
        down_moves = []
        
        for i in range(1, len(close)):
            up_move = high[i] - high[i-1] if high[i] > high[i-1] else 0
            down_move = low[i-1] - low[i] if low[i] < low[i-1] else 0
            up_moves.append(up_move)
            down_moves.append(down_move)
        
        if len(up_moves) < period:
            return 25.0
        
        avg_up = np.mean(up_moves[-period:])
        avg_down = np.mean(down_moves[-period:])
        
        if avg_down == 0:
            return 50.0
        
        di_plus = 100 * avg_up / (avg_up + avg_down)
        di_minus = 100 * avg_down / (avg_up + avg_down)
        
        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
        
        # Simplified ADX
        adx = np.mean([dx] * period)  # In real implementation, this would be smoothed
        return adx
    
    def _plus_di(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> float:
        """Plus Directional Indicator"""
        # Simplified implementation
        if len(close) < period + 1:
            return 25.0
        
        up_moves = []
        for i in range(1, min(len(close), period + 1)):
            up_move = high[i] - high[i-1] if high[i] > high[i-1] else 0
            up_moves.append(up_move)
        
        avg_up = np.mean(up_moves) if up_moves else 0
        true_range = self._atr(high, low, close, period)
        
        if true_range == 0:
            return 25.0
        
        return 100 * avg_up / true_range
    
    def _minus_di(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int) -> float:
        """Minus Directional Indicator"""
        # Simplified implementation
        if len(close) < period + 1:
            return 25.0
        
        down_moves = []
        for i in range(1, min(len(close), period + 1)):
            down_move = low[i-1] - low[i] if low[i] < low[i-1] else 0
            down_moves.append(down_move)
        
        avg_down = np.mean(down_moves) if down_moves else 0
        true_range = self._atr(high, low, close, period)
        
        if true_range == 0:
            return 25.0
        
        return 100 * avg_down / true_range
    
    def _calculate_regime_scores(self, indicators: Dict[str, float]) -> Dict[str, float]:
        """Har bir rejim uchun ball hisoblash"""
        scores = {}
        
        # Bull Market
        bull_score = 0
        if indicators.get('sma_10', 0) > indicators.get('sma_50', 0):
            bull_score += 0.3
        if indicators.get('macd', 0) > indicators.get('macd_signal', 0):
            bull_score += 0.3
        if indicators.get('rsi', 50) > 50:
            bull_score += 0.2
        if indicators.get('adx', 0) > 25:
            bull_score += 0.2
        scores[MarketRegime.BULL_MARKET.value] = min(bull_score, 1.0)
        
        # Bear Market
        bear_score = 0
        if indicators.get('sma_10', 0) < indicators.get('sma_50', 0):
            bear_score += 0.3
        if indicators.get('macd', 0) < indicators.get('macd_signal', 0):
            bear_score += 0.3
        if indicators.get('rsi', 50) < 50:
            bear_score += 0.2
        if indicators.get('plus_di', 0) < indicators.get('minus_di', 0):
            bear_score += 0.2
        scores[MarketRegime.BEAR_MARKET.value] = min(bear_score, 1.0)
        
        # Sideways Market
        sideways_score = 0
        if indicators.get('adx', 0) < 25:
            sideways_score += 0.4
        if 30 < indicators.get('rsi', 50) < 70:
            sideways_score += 0.3
        if abs(indicators.get('sma_10', 0) - indicators.get('sma_50', 0)) / indicators.get('sma_50', 1) < 0.02:
            sideways_score += 0.3
        scores[MarketRegime.SIDEWAYS_MARKET.value] = min(sideways_score, 1.0)
        
        # High Volatility
        high_vol_score = 0
        if indicators.get('volatility', 0) > self.config.volatility_threshold * 2:
            high_vol_score += 0.4
        if indicators.get('atr', 0) > self.config.volatility_threshold:
            high_vol_score += 0.3
        if indicators.get('bollinger_width', 0) > self.config.bollinger_std * 1.5:
            high_vol_score += 0.3
        scores[MarketRegime.HIGH_VOLATILITY.value] = min(high_vol_score, 1.0)
        
        # Low Volatility
        low_vol_score = 0
        if indicators.get('volatility', 0) < self.config.volatility_threshold * 0.5:
            low_vol_score += 0.5
        if indicators.get('atr', 0) < self.config.volatility_threshold * 0.5:
            low_vol_score += 0.3
        if indicators.get('adx', 0) < 20:
            low_vol_score += 0.2
        scores[MarketRegime.LOW_VOLATILITY.value] = min(low_vol_score, 1.0)
        
        # Breakout Market
        breakout_score = 0
        current_price = indicators.get('price_position', 0.5)
        if current_price > 0.8:  # Yaqinlikni resistance
            breakout_score += 0.4
        if indicators.get('volume_ratio', 0) > self.config.volume_threshold:
            breakout_score += 0.3
        if indicators.get('rsi', 50) > 65:
            breakout_score += 0.3
        scores[MarketRegime.BREAKOUT_MARKET.value] = min(breakout_score, 1.0)
        
        # Reversal Market
        reversal_score = 0
        if indicators.get('williams_r', -50) < -80:  # Oversold
            reversal_score += 0.4
        if indicators.get('rsi', 50) < 30:
            reversal_score += 0.3
        if indicators.get('stoch_k', 50) < 20:
            reversal_score += 0.3
        scores[MarketRegime.REVERSAL_MARKET.value] = min(reversal_score, 1.0)
        
        # Consolidation
        consolidation_score = 0
        bb_width = indicators.get('bollinger_upper', 0) - indicators.get('bollinger_lower', 0)
        if bb_width < self.config.bollinger_std * 0.5:
            consolidation_score += 0.5
        if indicators.get('adx', 0) < 20:
            consolidation_score += 0.3
        if indicators.get('volume_ratio', 1) < 0.8:
            consolidation_score += 0.2
        scores[MarketRegime.CONSOLIDATION.value] = min(consolidation_score, 1.0)
        
        return scores
    
    def _determine_primary_regime(self, scores: Dict[str, float]) -> MarketRegime:
        """Asosiy rejimni aniqlash"""
        # Eng yuqori ballni olgan rejim
        primary_regime = max(scores, key=scores.get)
        return MarketRegime(primary_regime)
    
    def _calculate_confidence(self, scores: Dict[str, float], indicators: Dict[str, float]) -> float:
        """Ishonchlilik darajasini hisoblash"""
        # Eng yuqqi va ikkinchi o'rinlar orasidagi farq
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) < 2:
            return 0.0
        
        score_diff = sorted_scores[0] - sorted_scores[1]
        base_confidence = min(score_diff * 2, 1.0)  # Farqni 2 ga ko'paytirish
        
        # Indikatorlarning konsistensiyasini tekshirish
        consistency_bonus = 0.0
        if indicators.get('adx', 0) > 30:  # Kuchli trend
            consistency_bonus += 0.1
        if indicators.get('volume_ratio', 1) > 1.2:  # Yuqori hajm
            consistency_bonus += 0.1
            
        return min(base_confidence + consistency_bonus, 1.0)
    
    def _calculate_persistence(self) -> float:
        """Rejim barqarorligini hisoblash"""
        if len(self.regime_history) < 5:
            return 0.0
            
        # Oxirgi 5 rejimni tekshirish
        recent_regimes = [r.regime for r in self.regime_history[-5:]]
        most_common = max(set(recent_regimes), key=recent_regimes.count)
        persistence = recent_regimes.count(most_common) / 5.0
        
        return persistence
    
    def _calculate_support_resistance(self, data: pd.DataFrame) -> Dict[str, float]:
        """Support va Resistance darajalarini hisoblash"""
        try:
            # Moving average support/resistance
            sma_20 = data['close'].rolling(window=20).mean()
            support = sma_20.iloc[-1]
            resistance = data['high'].rolling(window=20).max().iloc[-1]
            
            # Bollinger Bands asosida
            bb_upper, bb_middle, bb_lower = talib.BBANDS(data['close'].values, timeperiod=20)
            bb_support = bb_lower[-1]
            bb_resistance = bb_upper[-1]
            
            return {
                'support': (support + bb_support) / 2,
                'resistance': (resistance + bb_resistance) / 2
            }
        except:
            return {'support': data['close'].min(), 'resistance': data['close'].max()}
    
    def _calculate_market_breadth(self, data: pd.DataFrame) -> float:
        """Market breadth hisoblash (ko'p instrumentlar uchun)"""
        # Bu funksiya multiple symbols mavjud bo'lganda ishlatiladi
        return 0.5  # Default value
    
    def _calculate_seasonality(self) -> float:
        """Mavsumiy omil hisoblash"""
        now = datetime.now()
        month = now.month
        
        # Oddiy seasonality (yil uchun)
        seasonal_factors = {
            1: 0.9, 2: 0.95, 3: 1.0, 4: 1.05, 5: 1.1, 6: 1.05,
            7: 1.0, 8: 0.95, 9: 1.0, 10: 1.05, 11: 1.1, 12: 1.05
        }
        
        return seasonal_factors.get(month, 1.0)
    
    def detect_regimes_multi_timeframe(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, MarketRegimeResult]:
        """Ko'p vaqt doiralari bo'yicha rejim aniqlash"""
        results = {}
        
        for timeframe, data in data_dict.items():
            try:
                results[timeframe] = self.detect_regime(data, timeframe)
            except Exception as e:
                logger.error(f"{timeframe} vaqt doirasi uchun xatolik: {e}")
                
        return results
    
    def get_regime_transitions(self, days: int = 30) -> List[Dict[str, Any]]:
        """Rejim o'zgarishlarini olish"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_history = [r for r in self.regime_history if r.timestamp >= cutoff_date]
        
        transitions = []
        for i in range(1, len(recent_history)):
            if recent_history[i].regime != recent_history[i-1].regime:
                transitions.append({
                    'from': recent_history[i-1].regime,
                    'to': recent_history[i].regime,
                    'timestamp': recent_history[i].timestamp,
                    'confidence': recent_history[i].confidence
                })
                
        return transitions
    
    def train_ml_model(self, historical_data: List[pd.DataFrame], historical_regimes: List[MarketRegime]):
        """Machine Learning modelini o'qitish"""
        if not SKLEARN_AVAILABLE:
            logger.warning("sklearn not available, ML training disabled")
            return False
            
        try:
            if len(historical_data) != len(historical_regimes):
                raise ValueError("Ma'lumotlar va rejimlar soni mos kelmaydi")
            
            # Features extraction
            X = []
            y = []
            
            for data, regime in zip(historical_data, historical_regimes):
                indicators = self._calculate_all_indicators(data)
                feature_values = list(indicators.values())
                
                # NaN qiymatlarni tozalash
                feature_values = [v if not np.isnan(v) and np.isfinite(v) else 0.0 for v in feature_values]
                
                if len(feature_values) > 0:
                    X.append(feature_values)
                    y.append(regime.value)
            
            if len(X) == 0:
                logger.warning("Model uchun yetarli ma'lumot yo'q")
                return False
            
            # Scaling
            X_scaled = self.scaler.fit_transform(X)
            
            # Model training
            self.ml_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.ml_model.fit(X_scaled, y)
            self.is_trained = True
            
            logger.info("ML model muvaffaqiyatli o'qitildi")
            return True
            
        except Exception as e:
            logger.error(f"Model o'qitishda xatolik: {e}")
            return False
    
    def predict_regime_ml(self, data: pd.DataFrame) -> Optional[MarketRegimeResult]:
        """ML model orqali rejim bashorat qilish"""
        if not SKLEARN_AVAILABLE or not self.is_trained or self.ml_model is None:
            return None
            
        try:
            indicators = self._calculate_all_indicators(data)
            feature_values = list(indicators.values())
            feature_values = [v if not np.isnan(v) and np.isfinite(v) else 0.0 for v in feature_values]
            
            if len(feature_values) == 0:
                return None
                
            # Scaling
            X_scaled = self.scaler.transform([feature_values])
            
            # Prediction
            prediction = self.ml_model.predict(X_scaled)[0]
            probability = self.ml_model.predict_proba(X_scaled)[0].max()
            
            return MarketRegimeResult(
                regime=MarketRegime(prediction),
                confidence=probability,
                indicators=indicators,
                signal_strength=probability,
                persistence_score=0.0,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"ML bashoratda xatolik: {e}")
            return None

    def get_regime_statistics(self) -> Dict[str, Any]:
        """Rejim statistikalarini olish"""
        if not self.regime_history:
            return {}
            
        regime_counts = {}
        total_count = len(self.regime_history)
        
        for result in self.regime_history:
            regime = result.regime.value
            regime_counts[regime] = regime_counts.get(regime, 0) + 1
        
        # Foiz hisoblash
        regime_percentages = {regime: (count / total_count) * 100 
                            for regime, count in regime_counts.items()}
        
        # O'rtacha ishonchlilik
        avg_confidence = np.mean([r.confidence for r in self.regime_history])
        
        # O'rtacha barqarorlik
        avg_persistence = np.mean([r.persistence_score for r in self.regime_history])
        
        return {
            'total_observations': total_count,
            'regime_counts': regime_counts,
            'regime_percentages': regime_percentages,
            'average_confidence': avg_confidence,
            'average_persistence': avg_persistence,
            'current_regime': self.regime_history[-1].regime.value if self.regime_history else None,
            'current_confidence': self.regime_history[-1].confidence if self.regime_history else 0.0
        }

# Utility functions
def create_sample_data(days: int = 100) -> pd.DataFrame:
    """Namuna ma'lumot yaratish"""
    np.random.seed(42)
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days, freq='D')
    
    # Random walk with trend
    returns = np.random.normal(0.001, 0.02, days)
    prices = 100 * np.exp(np.cumsum(returns))
    
    # OHLCV data creation
    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices * (1 + np.random.normal(0, 0.005, days)),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.01, days))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.01, days))),
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, days)
    })
    
    return data

# Test function
def test_market_regime_detector():
    """Detector funksiyasini test qilish"""
    print("Market Regime Detector test qilish...")
    
    # Test data
    data = create_sample_data(100)
    
    # Detector yaratish
    detector = MarketRegimeDetector()
    
    # Rejim aniqlash
    result = detector.detect_regime(data)
    
    print(f"Aniqlangan rejim: {result.regime.value}")
    print(f"Ishonchlilik: {result.confidence:.2f}")
    print(f"Signal kuchi: {result.signal_strength:.2f}")
    print(f"Barqarorlik: {result.persistence_score:.2f}")
    
    # Statistikalar
    stats = detector.get_regime_statistics()
    print(f"Statistika: {stats}")
    
    return result

if __name__ == "__main__":
    test_market_regime_detector()