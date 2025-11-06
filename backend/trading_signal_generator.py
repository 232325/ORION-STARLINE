"""
Multi-Asset Trading Signal Generator
Real-time trading signal system with technical analysis and ML integration
"""

import asyncio
import logging
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

# Technical Analysis Libraries
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("Warning: TA-Lib not available. Using fallback calculations.")

from scipy import stats
from sklearn.preprocessing import StandardScaler
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SignalType(Enum):
    """Trading signal types"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class AssetType(Enum):
    """Asset categories"""
    STOCK = "STOCK"
    FOREX = "FOREX"
    METAL = "METAL"

@dataclass
class TradingSignal:
    """Trading signal data structure"""
    symbol: str
    signal_type: SignalType
    confidence: float
    current_price: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    timeframe: str
    timestamp: datetime
    indicators: Dict[str, float]
    reasoning: str

@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class TechnicalIndicators:
    """Technical indicator calculations"""
    
    @staticmethod
    def sma(data: pd.Series, period: int = 20) -> pd.Series:
        """Simple Moving Average"""
        if TALIB_AVAILABLE:
            return pd.Series(talib.SMA(data.values, timeperiod=period), index=data.index)
        else:
            return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int = 20) -> pd.Series:
        """Exponential Moving Average"""
        if TALIB_AVAILABLE:
            return pd.Series(talib.EMA(data.values, timeperiod=period), index=data.index)
        else:
            return data.ewm(span=period).mean()
    
    @staticmethod
    def wma(data: pd.Series, period: int = 20) -> pd.Series:
        """Weighted Moving Average"""
        weights = np.arange(1, period + 1)
        return data.rolling(period).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        if TALIB_AVAILABLE:
            return pd.Series(talib.RSI(data.values, timeperiod=period), index=data.index)
        else:
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD indicator"""
        if TALIB_AVAILABLE:
            macd, macdsignal, macdhist = talib.MACD(data.values, fastperiod=fast, 
                                                   slowperiod=slow, signalperiod=signal)
            return {
                'macd': pd.Series(macd, index=data.index),
                'signal': pd.Series(macdsignal, index=data.index),
                'histogram': pd.Series(macdhist, index=data.index)
            }
        else:
            ema_fast = TechnicalIndicators.ema(data, fast)
            ema_slow = TechnicalIndicators.ema(data, slow)
            macd = ema_fast - ema_slow
            signal_line = TechnicalIndicators.ema(macd, signal)
            histogram = macd - signal_line
            return {
                'macd': macd,
                'signal': signal_line,
                'histogram': histogram
            }
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std: float = 2) -> Dict[str, pd.Series]:
        """Bollinger Bands"""
        if TALIB_AVAILABLE:
            upper, middle, lower = talib.BBANDS(data.values, timeperiod=period, nbdevup=std, nbdevdn=std)
            return {
                'upper': pd.Series(upper, index=data.index),
                'middle': pd.Series(middle, index=data.index),
                'lower': pd.Series(lower, index=data.index)
            }
        else:
            middle = TechnicalIndicators.sma(data, period)
            std_dev = data.rolling(window=period).std()
            upper = middle + (std_dev * std)
            lower = middle - (std_dev * std)
            return {
                'upper': upper,
                'middle': middle,
                'lower': lower
            }
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """Stochastic Oscillator"""
        if TALIB_AVAILABLE:
            slowk, slowd = talib.STOCH(high.values, low.values, close.values, 
                                     fastk_period=k_period, slowk_period=d_period, slowd_period=d_period)
            return {
                'k': pd.Series(slowk, index=close.index),
                'd': pd.Series(slowd, index=close.index)
            }
        else:
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            return {
                'k': k_percent,
                'd': d_percent
            }
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range"""
        if TALIB_AVAILABLE:
            atr_values = talib.ATR(high.values, low.values, close.values, timeperiod=period)
            return pd.Series(atr_values, index=close.index)
        else:
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            return true_range.rolling(window=period).mean()

class DataProvider:
    """Data provider for market data"""
    
    # Supported symbols with their asset types
    SUPPORTED_SYMBOLS = {
        # Stocks
        'AAPL': AssetType.STOCK,
        'GOOGL': AssetType.STOCK,
        'MSFT': AssetType.STOCK,
        'TSLA': AssetType.STOCK,
        'NVDA': AssetType.STOCK,
        
        # Forex
        'EURUSD=X': AssetType.FOREX,
        'GBPUSD=X': AssetType.FOREX,
        'USDJPY=X': AssetType.FOREX,
        'USDCHF=X': AssetType.FOREX,
        'AUDUSD=X': AssetType.FOREX,
        
        # Metals
        'GC=F': AssetType.METAL,    # Gold
        'SI=F': AssetType.METAL,    # Silver
        'PL=F': AssetType.METAL,    # Platinum
        'PA=F': AssetType.METAL,    # Palladium
    }
    
    @staticmethod
    def get_data(symbol: str, period: str = "1d", interval: str = "1m") -> pd.DataFrame:
        """Fetch market data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Standardize column names
            data.columns = [col.lower() for col in data.columns]
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_current_price(symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('regularMarketPrice', info.get('previousClose', 0))
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return 0

class SignalGenerator:
    """Main signal generation engine"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.data_provider = DataProvider()
        self.models = {}  # Loaded ML models
        self.risk_free_rate = 0.02  # 2% risk-free rate
        
    def load_models(self, model_paths: Dict[str, str]) -> None:
        """Load trained ML models"""
        for model_name, path in model_paths.items():
            try:
                self.models[model_name] = joblib.load(path)
                logger.info(f"Loaded model: {model_name}")
            except Exception as e:
                logger.error(f"Error loading model {model_name}: {e}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate all technical indicators for latest data point"""
        if data.empty or len(data) < 50:
            return {}
        
        close = data['close']
        high = data['high']
        low = data['low']
        volume = data.get('volume', pd.Series())
        
        indicators = {}
        
        try:
            # Moving Averages
            indicators['sma_20'] = self.indicators.sma(close, 20).iloc[-1]
            indicators['sma_50'] = self.indicators.sma(close, 50).iloc[-1]
            indicators['ema_12'] = self.indicators.ema(close, 12).iloc[-1]
            indicators['ema_26'] = self.indicators.ema(close, 26).iloc[-1]
            
            # RSI
            indicators['rsi'] = self.indicators.rsi(close, 14).iloc[-1]
            
            # MACD
            macd_data = self.indicators.macd(close)
            indicators['macd'] = macd_data['macd'].iloc[-1]
            indicators['macd_signal'] = macd_data['signal'].iloc[-1]
            indicators['macd_histogram'] = macd_data['histogram'].iloc[-1]
            
            # Bollinger Bands
            bb_data = self.indicators.bollinger_bands(close)
            indicators['bb_upper'] = bb_data['upper'].iloc[-1]
            indicators['bb_middle'] = bb_data['middle'].iloc[-1]
            indicators['bb_lower'] = bb_data['lower'].iloc[-1]
            
            # Stochastic
            stoch_data = self.indicators.stochastic(high, low, close)
            indicators['stoch_k'] = stoch_data['k'].iloc[-1]
            indicators['stoch_d'] = stoch_data['d'].iloc[-1]
            
            # ATR
            indicators['atr'] = self.indicators.atr(high, low, close).iloc[-1]
            
            # Price-based indicators
            current_price = close.iloc[-1]
            indicators['price_vs_sma20'] = (current_price - indicators['sma_20']) / indicators['sma_20'] * 100
            indicators['price_vs_sma50'] = (current_price - indicators['sma_50']) / indicators['sma_50'] * 100
            
            # Volume indicators if available
            if not volume.empty and len(volume) > 20:
                indicators['volume_sma'] = volume.rolling(20).mean().iloc[-1]
                indicators['volume_ratio'] = volume.iloc[-1] / indicators['volume_sma']
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
        
        return indicators
    
    def calculate_signal_strength(self, indicators: Dict[str, float]) -> float:
        """Calculate signal strength based on technical indicators"""
        if not indicators:
            return 0.5
        
        score = 0.0
        weight_sum = 0.0
        
        try:
            # RSI analysis
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi < 30:
                    score += 0.8  # Oversold - Bullish
                elif rsi > 70:
                    score -= 0.8  # Overbought - Bearish
                weight_sum += 1.0
            
            # MACD analysis
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd']
                macd_signal = indicators['macd_signal']
                if macd > macd_signal:
                    score += 0.6  # Bullish crossover
                else:
                    score -= 0.6  # Bearish crossover
                weight_sum += 1.0
            
            # Moving Average analysis
            if 'price_vs_sma20' in indicators and 'price_vs_sma50' in indicators:
                sma20_score = 0.4 if indicators['price_vs_sma20'] > 0 else -0.4
                sma50_score = 0.3 if indicators['price_vs_sma50'] > 0 else -0.3
                score += sma20_score + sma50_score
                weight_sum += 1.0
            
            # Stochastic analysis
            if 'stoch_k' in indicators and 'stoch_d' in indicators:
                stoch_k = indicators['stoch_k']
                stoch_d = indicators['stoch_d']
                if stoch_k < 20 and stoch_d < 20:
                    score += 0.7  # Oversold
                elif stoch_k > 80 and stoch_d > 80:
                    score -= 0.7  # Overbought
                weight_sum += 1.0
            
            # Bollinger Bands analysis
            if 'bb_upper' in indicators and 'bb_lower' in indicators:
                current_price = indicators.get('price', 0)
                bb_upper = indicators['bb_upper']
                bb_lower = indicators['bb_lower']
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
                if bb_position < 0.2:
                    score += 0.5  # Near lower band
                elif bb_position > 0.8:
                    score -= 0.5  # Near upper band
                weight_sum += 1.0
            
            # Normalize score
            if weight_sum > 0:
                normalized_score = (score / weight_sum + 1) / 2  # Convert to 0-1 range
            else:
                normalized_score = 0.5
            
            return max(0.0, min(1.0, normalized_score))
            
        except Exception as e:
            logger.error(f"Error calculating signal strength: {e}")
            return 0.5
    
    def determine_signal_type(self, strength: float) -> SignalType:
        """Determine signal type based on strength"""
        if strength >= 0.8:
            return SignalType.STRONG_BUY
        elif strength >= 0.65:
            return SignalType.BUY
        elif strength >= 0.35:
            return SignalType.HOLD
        elif strength >= 0.2:
            return SignalType.SELL
        else:
            return SignalType.STRONG_SELL
    
    def calculate_position_size(self, signal_type: SignalType, confidence: float, 
                              account_balance: float = 10000, risk_percent: float = 0.02) -> float:
        """Calculate position size based on risk management"""
        base_size = account_balance * risk_percent
        
        # Adjust based on signal type
        if signal_type == SignalType.STRONG_BUY or signal_type == SignalType.STRONG_SELL:
            multiplier = 1.5
        elif signal_type == SignalType.BUY or signal_type == SignalType.SELL:
            multiplier = 1.0
        else:
            multiplier = 0.5  # HOLD - smaller position
        
        # Adjust based on confidence
        confidence_multiplier = confidence
        
        return base_size * multiplier * confidence_multiplier
    
    def calculate_stop_loss_take_profit(self, entry_price: float, signal_type: SignalType, 
                                      atr: float, multiplier: float = 2.0) -> Tuple[float, float]:
        """Calculate stop loss and take profit levels"""
        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
            stop_loss = entry_price - (atr * multiplier)
            take_profit = entry_price + (atr * multiplier * 1.5)
        else:
            stop_loss = entry_price + (atr * multiplier)
            take_profit = entry_price - (atr * multiplier * 1.5)
        
        return stop_loss, take_profit
    
    def generate_reasoning(self, indicators: Dict[str, float], signal_type: SignalType) -> str:
        """Generate reasoning for the signal"""
        reasoning_parts = []
        
        try:
            # RSI analysis
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi < 30:
                    reasoning_parts.append(f"RSI at {rsi:.1f} indicates oversold conditions")
                elif rsi > 70:
                    reasoning_parts.append(f"RSI at {rsi:.1f} suggests overbought conditions")
            
            # MACD analysis
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd']
                macd_signal = indicators['macd_signal']
                if macd > macd_signal:
                    reasoning_parts.append("MACD bullish crossover detected")
                else:
                    reasoning_parts.append("MACD bearish crossover detected")
            
            # Moving Average analysis
            if 'price_vs_sma20' in indicators:
                price_vs_sma = indicators['price_vs_sma20']
                if price_vs_sma > 0:
                    reasoning_parts.append(f"Price trading {price_vs_sma:.1f}% above SMA20")
                else:
                    reasoning_parts.append(f"Price trading {abs(price_vs_sma):.1f}% below SMA20")
            
            # Stochastic analysis
            if 'stoch_k' in indicators:
                stoch_k = indicators['stoch_k']
                if stoch_k < 20:
                    reasoning_parts.append("Stochastic indicates oversold conditions")
                elif stoch_k > 80:
                    reasoning_parts.append("Stochastic suggests overbought conditions")
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            reasoning_parts.append("Technical analysis based on multiple indicators")
        
        if not reasoning_parts:
            reasoning_parts.append("Signal based on composite technical analysis")
        
        return ". ".join(reasoning_parts) + "."
    
    def generate_signal(self, symbol: str, timeframe: str = "1m", 
                       account_balance: float = 10000) -> Optional[TradingSignal]:
        """Generate trading signal for a symbol"""
        try:
            # Fetch data
            data = self.data_provider.get_data(symbol, period="5d", interval=timeframe)
            if data.empty:
                logger.warning(f"No data available for {symbol}")
                return None
            
            # Calculate indicators
            indicators = self.calculate_indicators(data)
            if not indicators:
                logger.warning(f"Could not calculate indicators for {symbol}")
                return None
            
            # Calculate signal strength
            strength = self.calculate_signal_strength(indicators)
            signal_type = self.determine_signal_type(strength)
            
            # Get current price
            current_price = data['close'].iloc[-1]
            
            # Generate entry price (use current price)
            entry_price = current_price
            
            # Calculate position size
            position_size = self.calculate_position_size(
                signal_type, strength, account_balance
            )
            
            # Calculate stop loss and take profit
            atr = indicators.get('atr', 0.01 * current_price)  # Fallback ATR
            stop_loss, take_profit = self.calculate_stop_loss_take_profit(
                entry_price, signal_type, atr
            )
            
            # Generate reasoning
            reasoning = self.generate_reasoning(indicators, signal_type)
            
            # Create signal
            signal = TradingSignal(
                symbol=symbol,
                signal_type=signal_type,
                confidence=strength,
                current_price=current_price,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                position_size=position_size,
                timeframe=timeframe,
                timestamp=datetime.now(),
                indicators=indicators,
                reasoning=reasoning
            )
            
            logger.info(f"Generated {signal_type.value} signal for {symbol} with confidence {strength:.2f}")
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None

class MultiTimeframeSignal:
    """Multi-timeframe signal analysis"""
    
    def __init__(self, signal_generator: SignalGenerator):
        self.signal_generator = signal_generator
        self.timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
    
    def analyze_multi_timeframe(self, symbol: str, 
                               account_balance: float = 10000) -> List[TradingSignal]:
        """Analyze symbol across multiple timeframes"""
        signals = []
        
        for timeframe in self.timeframes:
            signal = self.signal_generator.generate_signal(symbol, timeframe, account_balance)
            if signal:
                signals.append(signal)
        
        return signals
    
    def get_ensemble_signal(self, symbol: str, account_balance: float = 10000) -> Optional[TradingSignal]:
        """Generate ensemble signal from multiple timeframes"""
        signals = self.analyze_multi_timeframe(symbol, account_balance)
        
        if not signals:
            return None
        
        # Weight signals by timeframe (higher timeframes have more weight)
        timeframe_weights = {
            "1m": 0.5, "5m": 0.6, "15m": 0.7, "1h": 0.8, "4h": 0.9, "1d": 1.0
        }
        
        # Calculate weighted average confidence
        total_weight = 0
        weighted_confidence = 0
        signal_types = []
        
        for signal in signals:
            weight = timeframe_weights.get(signal.timeframe, 0.5)
            total_weight += weight
            weighted_confidence += signal.confidence * weight
            signal_types.append(signal.signal_type)
        
        if total_weight == 0:
            return None
        
        final_confidence = weighted_confidence / total_weight
        final_signal_type = self.signal_generator.determine_signal_type(final_confidence)
        
        # Use the highest timeframe signal as base
        base_signal = max(signals, key=lambda x: timeframe_weights.get(x.timeframe, 0.5))
        
        # Create ensemble signal
        ensemble_signal = TradingSignal(
            symbol=symbol,
            signal_type=final_signal_type,
            confidence=final_confidence,
            current_price=base_signal.current_price,
            entry_price=base_signal.entry_price,
            stop_loss=base_signal.stop_loss,
            take_profit=base_signal.take_profit,
            position_size=self.signal_generator.calculate_position_size(
                final_signal_type, final_confidence, account_balance
            ),
            timeframe="Ensemble",
            timestamp=datetime.now(),
            indicators=base_signal.indicators,
            reasoning=f"Ensemble signal from {len(signals)} timeframes. {base_signal.reasoning}"
        )
        
        return ensemble_signal

class TradingSignalGenerator:
    """Main trading signal generator system"""
    
    def __init__(self, model_paths: Dict[str, str] = None):
        self.signal_generator = SignalGenerator()
        self.multi_timeframe = MultiTimeframeSignal(self.signal_generator)
        
        if model_paths:
            self.signal_generator.load_models(model_paths)
        
        self.supported_symbols = DataProvider.SUPPORTED_SYMBOLS
        self.is_running = False
        self.signals_queue = queue.Queue()
        self.background_thread = None
    
    def get_supported_assets(self) -> Dict[str, AssetType]:
        """Get list of supported assets"""
        return self.supported_symbols
    
    def generate_signal(self, symbol: str, timeframe: str = "1h", 
                       account_balance: float = 10000) -> Optional[TradingSignal]:
        """Generate signal for a single symbol"""
        if symbol not in self.supported_symbols:
            logger.error(f"Unsupported symbol: {symbol}")
            return None
        
        return self.signal_generator.generate_signal(symbol, timeframe, account_balance)
    
    def generate_multi_timeframe_signal(self, symbol: str, 
                                      account_balance: float = 10000) -> Optional[TradingSignal]:
        """Generate multi-timeframe signal"""
        return self.multi_timeframe.get_ensemble_signal(symbol, account_balance)
    
    def generate_signals_for_all(self, account_balance: float = 10000) -> Dict[str, Optional[TradingSignal]]:
        """Generate signals for all supported assets"""
        results = {}
        
        for symbol in self.supported_symbols.keys():
            signal = self.generate_multi_timeframe_signal(symbol, account_balance)
            results[symbol] = signal
        
        return results
    
    def start_real_time_generation(self, symbols: List[str] = None, 
                                  interval: int = 60, account_balance: float = 10000):
        """Start real-time signal generation"""
        if self.is_running:
            logger.warning("Real-time generation already running")
            return
        
        self.is_running = True
        symbols = symbols or list(self.supported_symbols.keys())
        
        def generate_signals():
            while self.is_running:
                try:
                    for symbol in symbols:
                        if not self.is_running:
                            break
                        
                        signal = self.generate_multi_timeframe_signal(symbol, account_balance)
                        if signal:
                            self.signals_queue.put({
                                'symbol': symbol,
                                'signal': signal,
                                'timestamp': datetime.now()
                            })
                    
                    # Sleep for specified interval
                    for _ in range(interval):
                        if not self.is_running:
                            break
                        threading.Event().wait(1)
                        
                except Exception as e:
                    logger.error(f"Error in real-time generation: {e}")
        
        self.background_thread = threading.Thread(target=generate_signals)
        self.background_thread.daemon = True
        self.background_thread.start()
        
        logger.info(f"Started real-time signal generation for {len(symbols)} symbols")
    
    def stop_real_time_generation(self):
        """Stop real-time signal generation"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
        
        logger.info("Stopped real-time signal generation")
    
    def get_signal_queue(self) -> queue.Queue:
        """Get the signals queue for real-time consumption"""
        return self.signals_queue
    
    def export_signals(self, signals: Dict[str, Optional[TradingSignal]], 
                     filename: str = None) -> str:
        """Export signals to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"signals_{timestamp}.json"
        
        # Convert signals to JSON-serializable format
        export_data = {}
        for symbol, signal in signals.items():
            if signal:
                export_data[symbol] = {
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type.value,
                    'confidence': signal.confidence,
                    'current_price': signal.current_price,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'position_size': signal.position_size,
                    'timeframe': signal.timeframe,
                    'timestamp': signal.timestamp.isoformat(),
                    'indicators': signal.indicators,
                    'reasoning': signal.reasoning
                }
        
        # Save to file
        filepath = f"/workspace/code/{filename}"
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported signals to {filepath}")
        return filepath
    
    def validate_data_quality(self, symbol: str, timeframe: str = "1h") -> Dict[str, any]:
        """Validate data quality for a symbol"""
        try:
            data = self.data_provider.get_data(symbol, period="30d", interval=timeframe)
            
            if data.empty:
                return {'quality_score': 0, 'issues': ['No data available']}
            
            issues = []
            quality_score = 100
            
            # Check for missing values
            missing_values = data.isnull().sum().sum()
            if missing_values > 0:
                issues.append(f"{missing_values} missing values")
                quality_score -= missing_values * 5
            
            # Check for zero prices
            zero_prices = (data['close'] == 0).sum()
            if zero_prices > 0:
                issues.append(f"{zero_prices} zero prices")
                quality_score -= zero_prices * 10
            
            # Check for negative prices
            negative_prices = (data[['open', 'high', 'low', 'close']] < 0).sum().sum()
            if negative_prices > 0:
                issues.append(f"{negative_prices} negative prices")
                quality_score -= negative_prices * 20
            
            # Check for unrealistic price movements
            data['price_change'] = data['close'].pct_change().abs()
            high_movements = (data['price_change'] > 0.2).sum()  # >20% movement
            if high_movements > 0:
                issues.append(f"{high_movements} unrealistic price movements (>20%)")
                quality_score -= high_movements * 5
            
            # Check volume if available
            if 'volume' in data.columns:
                zero_volume = (data['volume'] == 0).sum()
                if zero_volume > len(data) * 0.5:  # More than 50% zero volume
                    issues.append("High percentage of zero volume")
                    quality_score -= 15
            
            return {
                'quality_score': max(0, quality_score),
                'issues': issues,
                'data_points': len(data),
                'date_range': {
                    'start': data.index[0].isoformat() if len(data) > 0 else None,
                    'end': data.index[-1].isoformat() if len(data) > 0 else None
                }
            }
            
        except Exception as e:
            return {'quality_score': 0, 'issues': [f"Error validating data: {e}"]}

# Example usage and testing
def main():
    """Main function for testing"""
    print("Multi-Asset Trading Signal Generator")
    print("=" * 50)
    
    # Initialize the generator
    generator = TradingSignalGenerator()
    
    # Get supported assets
    assets = generator.get_supported_assets()
    print(f"Supported assets: {len(assets)}")
    
    # Generate signals for all assets
    print("\nGenerating signals for all assets...")
    signals = generator.generate_signals_for_all()
    
    # Display results
    print("\nSignal Summary:")
    print("-" * 30)
    for symbol, signal in signals.items():
        if signal:
            print(f"{symbol}: {signal.signal_type.value} (Confidence: {signal.confidence:.2f})")
            print(f"  Current Price: ${signal.current_price:.2f}")
            print(f"  Entry Price: ${signal.entry_price:.2f}")
            print(f"  Stop Loss: ${signal.stop_loss:.2f}")
            print(f"  Take Profit: ${signal.take_profit:.2f}")
            print(f"  Reasoning: {signal.reasoning}")
            print()
    
    # Export signals
    export_file = generator.export_signals(signals)
    print(f"Signals exported to: {export_file}")
    
    # Test multi-timeframe analysis
    print("\nTesting multi-timeframe analysis for AAPL...")
    mtf_signal = generator.generate_multi_timeframe_signal("AAPL")
    if mtf_signal:
        print(f"Ensemble Signal: {mtf_signal.signal_type.value}")
        print(f"Confidence: {mtf_signal.confidence:.2f}")
    
    # Test data quality validation
    print("\nTesting data quality validation...")
    quality = generator.validate_data_quality("AAPL")
    print(f"Data Quality Score: {quality['quality_score']}/100")
    if quality['issues']:
        print("Issues found:")
        for issue in quality['issues']:
            print(f"  - {issue}")
    else:
        print("No issues found in data quality")

if __name__ == "__main__":
    main()