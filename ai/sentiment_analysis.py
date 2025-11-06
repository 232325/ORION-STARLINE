"""
Sentiment Analysis va Market Prediction Models - Orion Starline
Bozor sentiment tahlili, bashorat qilish va risk baholash tizimlari
"""

import asyncio
import numpy as np
import pandas as pd
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import xgboost as xgb
import lightgbm as lgb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Embedding, GlobalMaxPooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# Import AI NLP module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_nlp import (
    AdvancedNLP, SentimentAnalyzer, Preprocessor,
    SentimentType, SentimentResult
)

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """Bozor rejimlari"""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"

class SentimentSource(Enum):
    """Sentiment manbalari"""
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    REDDIT = "reddit"
    TWITTER = "twitter"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    FORUM = "forum"

class PredictionHorizon(Enum):
    """Bashorat vaqti"""
    INTRADAY = "intraday"    # 1-4 hours
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-6 months

@dataclass
class MarketData:
    """Bozor ma'lumotlari"""
    symbol: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    market_cap: Optional[float] = None
    circulating_supply: Optional[float] = None

@dataclass
class SentimentDataPoint:
    """Sentiment data nuqtasi"""
    timestamp: datetime
    source: SentimentSource
    text: str
    sentiment_score: float
    sentiment_label: SentimentType
    confidence: float
    engagement: Optional[int] = None  # likes, shares, etc.
    author_reputation: Optional[float] = None

@dataclass
class MarketPrediction:
    """Bozor bashorati"""
    symbol: str
    prediction_time: datetime
    horizon: PredictionHorizon
    predicted_direction: str  # up, down, sideways
    confidence: float
    price_target: float
    probability: Dict[str, float]  # probability of each outcome
    features_importance: Dict[str, float]
    model_info: Dict[str, Any]

@dataclass
class RiskMetrics:
    """Risk metrikalari"""
    volatility: float
    var_95: float  # Value at Risk 95%
    expected_shortfall: float
    max_drawdown: float
    sharpe_ratio: float
    correlation_risk: float
    sentiment_risk: float
    liquidity_risk: float

class MarketDataCollector:
    """Bozor ma'lumotlarini to'plash"""
    
    def __init__(self):
        self.data_cache = {}
        self.supported_symbols = [
            'BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD',
            'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN'
        ]
    
    async def collect_market_data(
        self, 
        symbol: str, 
        period: str = "1mo", 
        interval: str = "1d"
    ) -> List[MarketData]:
        """Bozor ma'lumotlarini yCollect"""
        
        try:
            # Yahoo Finance dan ma'lumot olish
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            market_data = []
            for index, row in hist.iterrows():
                data_point = MarketData(
                    symbol=symbol,
                    timestamp=index.to_pydatetime(),
                    open_price=float(row['Open']),
                    high_price=float(row['High']),
                    low_price=float(row['Low']),
                    close_price=float(row['Close']),
                    volume=float(row['Volume'])
                )
                market_data.append(data_point)
            
            logger.info(f"{symbol} bo'yicha {len(market_data)} ta ma'lumot nuqtasi olindi")
            return market_data
            
        except Exception as e:
            logger.error(f"Bozor ma'lumotlari olishda xato {symbol}: {str(e)}")
            return []
    
    async def collect_real_time_data(self, symbol: str) -> Optional[MarketData]:
        """Real-time ma'lumot olish"""
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Real-time ma'lumotlar
            market_data = MarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                open_price=float(info.get('open', 0)),
                high_price=float(info.get('dayHigh', 0)),
                low_price=float(info.get('dayLow', 0)),
                close_price=float(info.get('currentPrice', 0)),
                volume=float(info.get('volume', 0)),
                market_cap=float(info.get('marketCap', 0)),
                circulating_supply=float(info.get('circulatingSupply', 0))
            )
            
            return market_data
            
        except Exception as e:
            logger.error(f"Real-time ma'lumot olishda xato {symbol}: {str(e)}")
            return None

class SentimentDataCollector:
    """Sentiment ma'lumotlarini to'plash"""
    
    def __init__(self):
        self.nlp_system = AdvancedNLP()
        self.sentiment_cache = {}
        
        # Mock data generators
        self.mock_templates = {
            SentimentSource.NEWS: [
                "Breaking: {symbol} reaches new ATH amid institutional adoption",
                "Regulatory clarity drives {symbol} price surge",
                "Major partnership announced for {symbol} ecosystem"
            ],
            SentimentSource.SOCIAL_MEDIA: [
                "{symbol} to the moon! 🚀 #bullish",
                "Just bought more {symbol}, this is the dip we needed",
                " {symbol} showing strength despite market uncertainty"
            ],
            SentimentSource.REDDIT: [
                "My analysis on {symbol} fundamentals suggests long term growth",
                "Technical analysis shows {symbol} breaking key resistance",
                "Risk assessment: {symbol} volatility remains high"
            ]
        }
    
    async def collect_sentiment_data(
        self,
        symbol: str,
        sources: List[SentimentSource],
        time_window: timedelta = timedelta(hours=24)
    ) -> List[SentimentDataPoint]:
        """Sentiment ma'lumotlarini to'plash"""
        
        end_time = datetime.now()
        start_time = end_time - time_window
        
        sentiment_data = []
        
        # Mock data generation (real implementationda API larni ishlatish mumkin)
        for source in sources:
            mock_data = await self._generate_mock_sentiment_data(
                symbol, source, start_time, end_time
            )
            sentiment_data.extend(mock_data)
        
        # Sort by timestamp
        sentiment_data.sort(key=lambda x: x.timestamp)
        
        logger.info(f"{len(sentiment_data)} ta sentiment data nuqtasi to'plandi")
        return sentiment_data
    
    async def _generate_mock_sentiment_data(
        self,
        symbol: str,
        source: SentimentSource,
        start_time: datetime,
        end_time: datetime
    ) -> List[SentimentDataPoint]:
        """Mock sentiment data yaratish"""
        
        sentiment_data = []
        time_delta = (end_time - start_time) / 20  # 20 ta nuqta
        
        for i in range(20):
            timestamp = start_time + time_delta * i
            
            # Random text generation
            import random
            templates = self.mock_templates.get(source, ["{symbol} news update"])
            template = random.choice(templates)
            text = template.format(symbol=symbol)
            
            # Random sentiment (real implementationda AI tahlil qiladi)
            sentiment_score = random.uniform(-1, 1)
            
            if sentiment_score > 0.3:
                sentiment_label = SentimentType.POSITIVE
            elif sentiment_score < -0.3:
                sentiment_label = SentimentType.NEGATIVE
            else:
                sentiment_label = SentimentType.NEUTRAL
            
            confidence = random.uniform(0.5, 1.0)
            engagement = random.randint(10, 1000)
            author_reputation = random.uniform(0.3, 1.0)
            
            data_point = SentimentDataPoint(
                timestamp=timestamp,
                source=source,
                text=text,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                confidence=confidence,
                engagement=engagement,
                author_reputation=author_reputation
            )
            
            sentiment_data.append(data_point)
        
        return sentiment_data

class TechnicalIndicator:
    """Texnik indikatorlar hisoblash"""
    
    @staticmethod
    def calculate_sma(prices: List[float], window: int) -> List[float]:
        """Simple Moving Average"""
        if len(prices) < window:
            return []
        
        sma = []
        for i in range(window - 1, len(prices)):
            avg = sum(prices[i-window+1:i+1]) / window
            sma.append(avg)
        
        return sma
    
    @staticmethod
    def calculate_ema(prices: List[float], window: int) -> List[float]:
        """Exponential Moving Average"""
        if len(prices) < window:
            return []
        
        ema = [prices[0]]  # First value
        multiplier = 2 / (window + 1)
        
        for i in range(1, len(prices)):
            ema_value = (prices[i] * multiplier) + (ema[-1] * (1 - multiplier))
            ema.append(ema_value)
        
        return ema
    
    @staticmethod
    def calculate_rsi(prices: List[float], window: int = 14) -> List[float]:
        """Relative Strength Index"""
        if len(prices) < window + 1:
            return []
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        # First RSI value
        avg_gain = sum(gains[:window]) / window
        avg_loss = sum(losses[:window]) / window
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = [100 - (100 / (1 + rs))]
        
        # Calculate remaining RSI values
        for i in range(window, len(gains)):
            avg_gain = ((avg_gain * (window - 1)) + gains[i]) / window
            avg_loss = ((avg_loss * (window - 1)) + losses[i]) / window
            
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi_value = 100 - (100 / (1 + rs))
            rsi.append(rsi_value)
        
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], window: int = 20, num_std: float = 2) -> Tuple[List[float], List[float], List[float]]:
        """Bollinger Bands"""
        if len(prices) < window:
            return [], [], []
        
        sma = TechnicalIndicator.calculate_sma(prices, window)
        upper_band = []
        lower_band = []
        
        for i in range(len(sma)):
            price_slice = prices[i:i+window]
            std = np.std(price_slice)
            
            upper_band.append(sma[i] + (std * num_std))
            lower_band.append(sma[i] - (std * num_std))
        
        return sma, upper_band, lower_band
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """MACD"""
        ema_fast = TechnicalIndicator.calculate_ema(prices, fast)
        ema_slow = TechnicalIndicator.calculate_ema(prices, slow)
        
        # Align the lengths
        min_length = min(len(ema_fast), len(ema_slow))
        ema_fast = ema_fast[-min_length:]
        ema_slow = ema_slow[-min_length:]
        
        macd_line = [ema_fast[i] - ema_slow[i] for i in range(min_length)]
        signal_line = TechnicalIndicator.calculate_ema(macd_line, signal)
        
        # Align lengths again
        min_length = min(len(macd_line), len(signal_line))
        macd_line = macd_line[-min_length:]
        signal_line = signal_line[-min_length:]
        
        histogram = [macd_line[i] - signal_line[i] for i in range(min_length)]
        
        return macd_line, signal_line, histogram

class SentimentProcessor:
    """Sentiment qayta ishlash"""
    
    def __init__(self):
        self.nlp_system = AdvancedNLP()
        
    async def aggregate_sentiment(
        self, 
        sentiment_data: List[SentimentDataPoint],
        weighting_scheme: str = "reputation_engagement"
    ) -> Dict[str, Any]:
        """Sentiment ni jamlash"""
        
        if not sentiment_data:
            return {
                'overall_sentiment': 0.0,
                'sentiment_distribution': {s.value: 0 for s in SentimentType},
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'volume': 0,
                'weighted_sentiment': 0.0
            }
        
        # Sentiment distribution
        sentiment_counts = {s.value: 0 for s in SentimentType}
        weighted_scores = []
        total_weight = 0
        
        for data_point in sentiment_data:
            sentiment_counts[data_point.sentiment_label.value] += 1
            
            # Weight calculation
            if weighting_scheme == "reputation_engagement":
                weight = (data_point.confidence * 
                         (data_point.author_reputation or 0.5) * 
                         np.log((data_point.engagement or 1) + 1))
            elif weighting_scheme == "time_decay":
                # Recent posts have higher weight
                hours_ago = (datetime.now() - data_point.timestamp).total_seconds() / 3600
                weight = data_point.confidence * np.exp(-hours_ago / 24)  # Decay over 24 hours
            else:  # equal_weight
                weight = data_point.confidence
            
            weighted_scores.append(data_point.sentiment_score * weight)
            total_weight += weight
        
        # Overall metrics
        overall_sentiment = np.mean([dp.sentiment_score for dp in sentiment_data])
        weighted_sentiment = sum(weighted_scores) / total_weight if total_weight > 0 else 0
        confidence = np.mean([dp.confidence for dp in sentiment_data])
        volume = len(sentiment_data)
        
        return {
            'overall_sentiment': overall_sentiment,
            'weighted_sentiment': weighted_sentiment,
            'sentiment_distribution': sentiment_counts,
            'confidence': confidence,
            'volume': volume,
            'sentiment_score': weighted_sentiment,
            'source_breakdown': self._analyze_by_source(sentiment_data)
        }
    
    def _analyze_by_source(self, sentiment_data: List[SentimentDataPoint]) -> Dict[str, Any]:
        """Manba bo'yicha tahlil"""
        
        source_analysis = {}
        
        for source in SentimentSource:
            source_data = [dp for dp in sentiment_data if dp.source == source]
            
            if source_data:
                avg_sentiment = np.mean([dp.sentiment_score for dp in source_data])
                avg_confidence = np.mean([dp.confidence for dp in source_data])
                volume = len(source_data)
                
                source_analysis[source.value] = {
                    'average_sentiment': avg_sentiment,
                    'average_confidence': avg_confidence,
                    'volume': volume,
                    'sentiment_distribution': self._get_sentiment_distribution(source_data)
                }
        
        return source_analysis
    
    def _get_sentiment_distribution(self, data_points: List[SentimentDataPoint]) -> Dict[str, int]:
        """Sentiment distribution"""
        distribution = {s.value: 0 for s in SentimentType}
        for dp in data_points:
            distribution[dp.sentiment_label.value] += 1
        return distribution

class MarketRegimeDetector:
    """Bozor rejimi aniqlovchi"""
    
    @staticmethod
    async def detect_regime(market_data: List[MarketData], sentiment_data: Dict[str, Any]) -> MarketRegime:
        """Bozor rejimini aniqlash"""
        
        if len(market_data) < 20:
            return MarketRegime.SIDEWAYS
        
        prices = [data.close_price for data in market_data]
        
        # Calculate metrics
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        
        # Trend analysis
        sma_20 = TechnicalIndicator.calculate_sma(prices, 20)
        sma_50 = TechnicalIndicator.calculate_sma(prices, 50)
        
        current_price = prices[-1]
        sma_20_current = sma_20[-1] if sma_20 else current_price
        sma_50_current = sma_50[-1] if sma_50 else current_price
        
        # Sentiment analysis
        sentiment_score = sentiment_data.get('weighted_sentiment', 0)
        
        # Regime detection logic
        if sentiment_score > 0.5 and current_price > sma_20_current > sma_50_current:
            return MarketRegime.BULL_MARKET
        elif sentiment_score < -0.5 and current_price < sma_20_current < sma_50_current:
            return MarketRegime.BEAR_MARKET
        elif volatility > 0.5:
            return MarketRegime.HIGH_VOLATILITY
        elif volatility < 0.2:
            return MarketRegime.LOW_VOLATILITY
        else:
            return MarketRegime.SIDEWAYS

class MarketPredictionModel:
    """Bozor bashorat modeli"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
        # Model konfiguratsiyalari
        self.model_configs = {
            'sentiment_lstm': {
                'model_type': 'lstm',
                'sequence_length': 30,
                'features': ['sentiment_score', 'volume', 'volatility', 'rsi', 'macd']
            },
            'ensemble_rf': {
                'model_type': 'random_forest',
                'n_estimators': 100,
                'max_depth': 10
            },
            'xgboost_sentiment': {
                'model_type': 'xgboost',
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1
            }
        }
    
    async def prepare_features(
        self,
        market_data: List[MarketData],
        sentiment_data: Dict[str, Any],
        technical_indicators: Dict[str, List[float]]
    ) -> np.ndarray:
        """Features tayyorlash"""
        
        features = []
        
        for i, market_point in enumerate(market_data):
            feature_vector = []
            
            # Price features
            if i > 0:
                price_return = (market_point.close_price - market_data[i-1].close_price) / market_data[i-1].close_price
            else:
                price_return = 0
            
            feature_vector.extend([
                price_return,
                market_point.volume,
                market_point.high_price - market_point.low_price,  # Range
            ])
            
            # Sentiment features
            feature_vector.extend([
                sentiment_data.get('weighted_sentiment', 0),
                sentiment_data.get('confidence', 0),
                sentiment_data.get('volume', 0)
            ])
            
            # Technical indicators
            if 'rsi' in technical_indicators and i < len(technical_indicators['rsi']):
                feature_vector.append(technical_indicators['rsi'][i])
            else:
                feature_vector.append(50)  # Default RSI
            
            if 'macd' in technical_indicators and i < len(technical_indicators['macd']):
                feature_vector.append(technical_indicators['macd'][i])
            else:
                feature_vector.append(0)  # Default MACD
            
            features.append(feature_vector)
        
        return np.array(features)
    
    async def create_labels(
        self, 
        market_data: List[MarketData], 
        prediction_horizon: PredictionHorizon
    ) -> np.ndarray:
        """Labels yaratish (price direction prediction)"""
        
        labels = []
        horizon_days = {
            PredictionHorizon.INTRADAY: 1,
            PredictionHorizon.SHORT_TERM: 5,
            PredictionHorizon.MEDIUM_TERM: 20,
            PredictionHorizon.LONG_TERM: 60
        }
        
        days_ahead = horizon_days[prediction_horizon]
        
        for i in range(len(market_data) - days_ahead):
            current_price = market_data[i].close_price
            future_price = market_data[i + days_ahead].close_price
            
            price_change = (future_price - current_price) / current_price
            
            # Label encoding: 0=down, 1=sideways, 2=up
            if price_change > 0.02:  # 2% threshold for significant move up
                labels.append(2)
            elif price_change < -0.02:  # 2% threshold for significant move down
                labels.append(0)
            else:
                labels.append(1)  # Sideways
        
        return np.array(labels)
    
    async def train_sentiment_lstm(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        model_name: str = "sentiment_lstm"
    ):
        """LSTM model o'qitish"""
        
        try:
            # Reshape for LSTM (samples, timesteps, features)
            sequence_length = self.model_configs[model_name]['sequence_length']
            X_lstm = []
            y_lstm = []
            
            for i in range(sequence_length, len(features)):
                X_lstm.append(features[i-sequence_length:i])
                y_lstm.append(labels[i])
            
            X_lstm = np.array(X_lstm)
            y_lstm = np.array(y_lstm)
            
            # Model yaratish
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(sequence_length, features.shape[1])),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(3, activation='softmax')  # 3 classes: down, sideways, up
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), 
                         loss='sparse_categorical_crossentropy', 
                         metrics=['accuracy'])
            
            # Training
            early_stopping = EarlyStopping(patience=10, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(factor=0.2, patience=5, min_lr=0.0001)
            
            history = model.fit(
                X_lstm, y_lstm,
                batch_size=32,
                epochs=100,
                validation_split=0.2,
                callbacks=[early_stopping, reduce_lr],
                verbose=0
            )
            
            # Model saqlash
            self.models[model_name] = model
            
            logger.info(f"LSTM model muvaffaqiyatli o'qitildi: {model_name}")
            
        except Exception as e:
            logger.error(f"LSTM model o'qitishda xato: {str(e)}")
    
    async def train_ensemble_rf(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        model_name: str = "ensemble_rf"
    ):
        """Random Forest ensemble o'qitish"""
        
        try:
            config = self.model_configs[model_name]
            
            # RF model
            rf_model = RandomForestClassifier(
                n_estimators=config['n_estimators'],
                max_depth=config['max_depth'],
                random_state=42
            )
            
            # Training
            rf_model.fit(features, labels)
            
            # Feature importance
            feature_names = [
                'price_return', 'volume', 'price_range', 'sentiment_score',
                'sentiment_confidence', 'sentiment_volume', 'rsi', 'macd'
            ]
            
            importance_dict = dict(zip(feature_names, rf_model.feature_importances_))
            
            self.models[model_name] = rf_model
            self.feature_importance[model_name] = importance_dict
            
            logger.info(f"Random Forest model muvaffaqiyatli o'qitildi: {model_name}")
            
        except Exception as e:
            logger.error(f"Random Forest model o'qitishda xato: {str(e)}")
    
    async def predict(
        self,
        model_name: str,
        features: np.ndarray
    ) -> Dict[str, Any]:
        """Bashorat qilish"""
        
        if model_name not in self.models:
            raise ValueError(f"Model topilmadi: {model_name}")
        
        model = self.models[model_name]
        
        try:
            if self.model_configs[model_name]['model_type'] == 'lstm':
                # LSTM prediction
                sequence_length = self.model_configs[model_name]['sequence_length']
                if len(features) >= sequence_length:
                    # Use last sequence_length features
                    input_sequence = features[-sequence_length:].reshape(1, sequence_length, -1)
                    prediction = model.predict(input_sequence, verbose=0)[0]
                    
                    predicted_class = np.argmax(prediction)
                    confidence = np.max(prediction)
                    
                    probabilities = {
                        'down': float(prediction[0]),
                        'sideways': float(prediction[1]),
                        'up': float(prediction[2])
                    }
                else:
                    raise ValueError("Insufficient sequence length for LSTM prediction")
                    
            else:
                # Other models prediction
                prediction = model.predict(features[-1].reshape(1, -1))[0]
                
                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(features[-1].reshape(1, -1))[0]
                    probabilities = {
                        'down': float(probabilities[0]),
                        'sideways': float(probabilities[1]) if len(probabilities) > 1 else 0.0,
                        'up': float(probabilities[2]) if len(probabilities) > 2 else 0.0
                    }
                    confidence = max(probabilities.values())
                else:
                    confidence = 1.0
                    probabilities = {
                        'down': 0.33,
                        'sideways': 0.33,
                        'up': 0.33
                    }
                
                predicted_class = prediction
            
            # Direction mapping
            direction_map = {0: 'down', 1: 'sideways', 2: 'up'}
            predicted_direction = direction_map.get(predicted_class, 'unknown')
            
            return {
                'predicted_direction': predicted_direction,
                'confidence': float(confidence),
                'probabilities': probabilities,
                'model_info': {
                    'model_name': model_name,
                    'model_type': self.model_configs[model_name]['model_type'],
                    'prediction_time': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction xatosi {model_name}: {str(e)}")
            raise

class RiskAnalyzer:
    """Risk tahlil qiluvchi"""
    
    @staticmethod
    async def calculate_risk_metrics(
        market_data: List[MarketData],
        predictions: List[MarketPrediction],
        sentiment_data: Dict[str, Any]
    ) -> RiskMetrics:
        """Risk metrikalarini hisoblash"""
        
        if not market_data:
            return RiskMetrics(
                volatility=0.0, var_95=0.0, expected_shortfall=0.0,
                max_drawdown=0.0, sharpe_ratio=0.0, correlation_risk=0.0,
                sentiment_risk=0.0, liquidity_risk=0.0
            )
        
        prices = [data.close_price for data in market_data]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # Volatility
        volatility = np.std(returns) * np.sqrt(252)  # Annualized
        
        # Value at Risk (95%)
        var_95 = np.percentile(returns, 5) * prices[-1]  # 5th percentile
        
        # Expected Shortfall
        var_threshold = np.percentile(returns, 5)
        tail_returns = [r for r in returns if r <= var_threshold]
        expected_shortfall = np.mean(tail_returns) * prices[-1] if tail_returns else 0
        
        # Maximum Drawdown
        cumulative_returns = np.cumprod([1 + r for r in returns])
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = np.min(drawdown)
        
        # Sharpe Ratio (assuming risk-free rate = 2%)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        excess_returns = [r - risk_free_rate for r in returns]
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) > 0 else 0
        
        # Correlation Risk (simplified)
        correlation_risk = 0.0  # Would need multiple assets for real calculation
        
        # Sentiment Risk
        sentiment_volatility = sentiment_data.get('confidence', 0) * abs(sentiment_data.get('weighted_sentiment', 0))
        sentiment_risk = 1 - sentiment_volatility  # Higher risk when sentiment is uncertain
        
        # Liquidity Risk (simplified)
        avg_volume = np.mean([data.volume for data in market_data])
        current_volume = market_data[-1].volume if market_data else 0
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        liquidity_risk = max(0, 1 - volume_ratio)  # Higher risk when volume is low
        
        return RiskMetrics(
            volatility=volatility,
            var_95=abs(var_95),
            expected_shortfall=abs(expected_shortfall),
            max_drawdown=abs(max_drawdown),
            sharpe_ratio=sharpe_ratio,
            correlation_risk=correlation_risk,
            sentiment_risk=sentiment_risk,
            liquidity_risk=liquidity_risk
        )

class SentimentMarketPredictor:
    """Sentiment-based Market Prediction tizimi"""
    
    def __init__(self):
        self.market_data_collector = MarketDataCollector()
        self.sentiment_data_collector = SentimentDataCollector()
        self.technical_indicator = TechnicalIndicator()
        self.sentiment_processor = SentimentProcessor()
        self.regime_detector = MarketRegimeDetector()
        self.prediction_model = MarketPredictionModel()
        self.risk_analyzer = RiskAnalyzer()
        
        # Cache
        self.data_cache = {}
        self.model_cache = {}
    
    async def comprehensive_market_analysis(
        self,
        symbol: str,
        prediction_horizon: PredictionHorizon = PredictionHorizon.SHORT_TERM,
        sources: List[SentimentSource] = None
    ) -> Dict[str, Any]:
        """Keng qamrovli bozor tahlili"""
        
        try:
            # Default sources
            if sources is None:
                sources = [SentimentSource.NEWS, SentimentSource.SOCIAL_MEDIA, SentimentSource.REDDIT]
            
            # Parallel data collection
            market_task = self.market_data_collector.collect_market_data(symbol, period="3mo")
            sentiment_task = self.sentiment_data_collector.collect_sentiment_data(
                symbol, sources, timedelta(hours=48)
            )
            
            market_data, sentiment_raw_data = await asyncio.gather(market_task, sentiment_task)
            
            if not market_data:
                raise ValueError(f"{symbol} bo'yicha bozor ma'lumotlari topilmadi")
            
            logger.info(f"{symbol} uchun ma'lumotlar to'plandi: {len(market_data)} ta market data, {len(sentiment_raw_data)} ta sentiment data")
            
            # Sentiment processing
            sentiment_data = await self.sentiment_processor.aggregate_sentiment(sentiment_raw_data)
            
            # Technical analysis
            prices = [data.close_price for data in market_data]
            volumes = [data.volume for data in market_data]
            
            technical_indicators = {
                'sma_20': self.technical_indicator.calculate_sma(prices, 20),
                'sma_50': self.technical_indicator.calculate_sma(prices, 50),
                'ema_12': self.technical_indicator.calculate_ema(prices, 12),
                'ema_26': self.technical_indicator.calculate_ema(prices, 26),
                'rsi': self.technical_indicator.calculate_rsi(prices, 14),
                'macd': self.technical_indicator.calculate_macd(prices, 12, 26, 9)[0],
                'bollinger_upper': self.technical_indicator.calculate_bollinger_bands(prices, 20)[1],
                'bollinger_lower': self.technical_indicator.calculate_bollinger_bands(prices, 20)[2]
            }
            
            # Market regime detection
            market_regime = await self.regime_detector.detect_regime(market_data, sentiment_data)
            
            # Features preparation
            features = await self.prediction_model.prepare_features(market_data, sentiment_data, technical_indicators)
            
            # Labels preparation
            labels = await self.prediction_model.create_labels(market_data, prediction_horizon)
            
            # Model training (if sufficient data)
            if len(features) > 50 and len(labels) > 50:
                # Train models
                await self.prediction_model.train_sentiment_lstm(features, labels)
                await self.prediction_model.train_ensemble_rf(features, labels)
                
                # Generate predictions
                predictions = {}
                
                # LSTM prediction
                try:
                    lstm_prediction = await self.prediction_model.predict('sentiment_lstm', features)
                    predictions['lstm'] = lstm_prediction
                except Exception as e:
                    logger.error(f"LSTM prediction xatosi: {str(e)}")
                
                # Random Forest prediction
                try:
                    rf_prediction = await self.prediction_model.predict('ensemble_rf', features)
                    predictions['random_forest'] = rf_prediction
                except Exception as e:
                    logger.error(f"Random Forest prediction xatosi: {str(e)}")
                
                # Ensemble prediction
                ensemble_prediction = self._create_ensemble_prediction(predictions)
            else:
                ensemble_prediction = {
                    'predicted_direction': 'sideways',
                    'confidence': 0.3,
                    'probabilities': {'down': 0.33, 'sideways': 0.34, 'up': 0.33},
                    'model_info': {'error': 'Insufficient training data'}
                }
            
            # Risk analysis
            risk_metrics = await self.risk_analyzer.calculate_risk_metrics(market_data, [], sentiment_data)
            
            # Compile comprehensive analysis
            analysis_result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'prediction_horizon': prediction_horizon.value,
                'market_data': {
                    'current_price': prices[-1] if prices else 0,
                    'price_change_24h': ((prices[-1] - prices[-2]) / prices[-2] * 100) if len(prices) > 1 else 0,
                    'volume': volumes[-1] if volumes else 0,
                    'volatility_30d': np.std(returns[-30:]) * np.sqrt(252) if len(prices) > 30 else 0
                },
                'sentiment_analysis': sentiment_data,
                'market_regime': market_regime.value,
                'technical_indicators': {
                    'rsi': technical_indicators['rsi'][-1] if technical_indicators['rsi'] else 50,
                    'macd': technical_indicators['macd'][-1] if technical_indicators['macd'] else 0,
                    'sma_20': technical_indicators['sma_20'][-1] if technical_indicators['sma_20'] else prices[-1] if prices else 0,
                    'sma_50': technical_indicators['sma_50'][-1] if technical_indicators['sma_50'] else prices[-1] if prices else 0
                },
                'predictions': ensemble_prediction,
                'risk_metrics': asdict(risk_metrics),
                'model_performance': {
                    'data_points': len(market_data),
                    'training_samples': len(features),
                    'prediction_confidence': ensemble_prediction.get('confidence', 0)
                }
            }
            
            logger.info(f"{symbol} uchun keng qamrovli tahlil yakunlandi")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Comprehensive market analysis xatosi {symbol}: {str(e)}")
            raise
    
    def _create_ensemble_prediction(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Ensemble prediction yaratish"""
        
        if not predictions:
            return {
                'predicted_direction': 'sideways',
                'confidence': 0.33,
                'probabilities': {'down': 0.33, 'sideways': 0.34, 'up': 0.33}
            }
        
        # Weight by confidence
        total_weight = 0
        weighted_probabilities = {'down': 0, 'sideways': 0, 'up': 0}
        
        for model_name, prediction in predictions.items():
            confidence = prediction.get('confidence', 0)
            probabilities = prediction.get('probabilities', {})
            weight = confidence
            
            for direction in ['down', 'sideways', 'up']:
                weighted_probabilities[direction] += probabilities.get(direction, 0) * weight
            
            total_weight += weight
        
        # Normalize
        if total_weight > 0:
            for direction in weighted_probabilities:
                weighted_probabilities[direction] /= total_weight
        
        # Final prediction
        final_direction = max(weighted_probabilities, key=weighted_probabilities.get)
        final_confidence = weighted_probabilities[final_direction]
        
        return {
            'predicted_direction': final_direction,
            'confidence': final_confidence,
            'probabilities': weighted_probabilities,
            'model_info': {
                'ensemble_method': 'confidence_weighted',
                'models_used': list(predictions.keys()),
                'prediction_time': datetime.now().isoformat()
            }
        }
    
    async def generate_trading_signals(
        self,
        symbol: str,
        risk_tolerance: str = "medium"
    ) -> Dict[str, Any]:
        """Trading signallarini yaratish"""
        
        try:
            # Comprehensive analysis
            analysis = await self.comprehensive_market_analysis(symbol)
            
            # Signal generation logic
            prediction = analysis.get('predictions', {})
            sentiment = analysis.get('sentiment_analysis', {})
            technical = analysis.get('technical_indicators', {})
            risk_metrics = analysis.get('risk_metrics', {})
            
            # Signal strength calculation
            signal_strength = 0
            
            # Prediction contribution
            prediction_confidence = prediction.get('confidence', 0)
            if prediction.get('predicted_direction') == 'up':
                signal_strength += prediction_confidence * 0.4
            elif prediction.get('predicted_direction') == 'down':
                signal_strength -= prediction_confidence * 0.4
            
            # Sentiment contribution
            sentiment_score = sentiment.get('weighted_sentiment', 0)
            sentiment_confidence = sentiment.get('confidence', 0)
            signal_strength += sentiment_score * sentiment_confidence * 0.3
            
            # Technical contribution
            rsi = technical.get('rsi', 50)
            if rsi < 30:  # Oversold - bullish signal
                signal_strength += 0.2
            elif rsi > 70:  # Overbought - bearish signal
                signal_strength -= 0.2
            
            macd = technical.get('macd', 0)
            if macd > 0:  # Positive MACD
                signal_strength += 0.1
            else:
                signal_strength -= 0.1
            
            # Risk adjustment
            risk_multiplier = 1.0
            if risk_tolerance == "low":
                risk_multiplier = 0.5
            elif risk_tolerance == "high":
                risk_multiplier = 1.5
            
            adjusted_signal_strength = signal_strength * risk_multiplier
            
            # Signal classification
            if adjusted_signal_strength > 0.6:
                signal = "STRONG_BUY"
            elif adjusted_signal_strength > 0.3:
                signal = "BUY"
            elif adjusted_signal_strength < -0.6:
                signal = "STRONG_SELL"
            elif adjusted_signal_strength < -0.3:
                signal = "SELL"
            else:
                signal = "HOLD"
            
            # Position sizing recommendation
            risk_score = risk_metrics.get('volatility', 0) * risk_metrics.get('sentiment_risk', 0)
            if risk_tolerance == "low":
                position_size = max(0.1, 0.5 - risk_score)
            elif risk_tolerance == "high":
                position_size = min(1.0, 0.3 + risk_score)
            else:
                position_size = max(0.1, 0.3 - risk_score * 0.5)
            
            return {
                'symbol': symbol,
                'signal': signal,
                'signal_strength': adjusted_signal_strength,
                'confidence': prediction_confidence,
                'position_size': position_size,
                'stop_loss_pct': risk_metrics.get('var_95', 0.05),
                'take_profit_pct': risk_metrics.get('expected_shortfall', 0.1),
                'analysis_summary': {
                    'prediction': prediction.get('predicted_direction', 'unknown'),
                    'sentiment': sentiment.get('weighted_sentiment', 0),
                    'market_regime': analysis.get('market_regime', 'unknown'),
                    'risk_level': 'high' if risk_metrics.get('volatility', 0) > 0.5 else 'medium'
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trading signals generation xatosi {symbol}: {str(e)}")
            raise

# Demo va test funksiyalari
async def demo_sentiment_market_predictor():
    """Sentiment Market Predictor demo"""
    
    print("📊 Sentiment Analysis & Market Prediction Demo")
    print("=" * 60)
    
    # Tizimni yaratish
    predictor = SentimentMarketPredictor()
    
    # Test symbols
    test_symbols = ['BTC-USD', 'ETH-USD']
    
    for symbol in test_symbols:
        print(f"\n🔍 {symbol} Analysis:")
        print("-" * 30)
        
        try:
            # Comprehensive analysis
            analysis = await predictor.comprehensive_market_analysis(
                symbol, 
                PredictionHorizon.SHORT_TERM,
                [SentimentSource.NEWS, SentimentSource.SOCIAL_MEDIA]
            )
            
            # Results display
            print(f"Current Price: ${analysis['market_data']['current_price']:,.2f}")
            print(f"24h Change: {analysis['market_data']['price_change_24h']:+.2f}%")
            print(f"Market Regime: {analysis['market_regime']}")
            
            # Sentiment
            sentiment = analysis['sentiment_analysis']
            print(f"Sentiment: {sentiment.get('weighted_sentiment', 0):.3f}")
            print(f"Sentiment Confidence: {sentiment.get('confidence', 0):.3f}")
            
            # Prediction
            prediction = analysis['predictions']
            print(f"Prediction: {prediction.get('predicted_direction', 'unknown').upper()}")
            print(f"Confidence: {prediction.get('confidence', 0):.3f}")
            
            # Technical indicators
            technical = analysis['technical_indicators']
            print(f"RSI: {technical.get('rsi', 0):.1f}")
            print(f"MACD: {technical.get('macd', 0):.4f}")
            
            # Risk metrics
            risk = analysis['risk_metrics']
            print(f"Volatility: {risk.get('volatility', 0):.3f}")
            print(f"VaR (95%): {risk.get('var_95', 0):.3f}")
            
        except Exception as e:
            print(f"❌ {symbol} analysis xatosi: {str(e)}")
    
    print(f"\n🎯 Trading Signals Generation:")
    print("-" * 30)
    
    # Trading signals
    for symbol in test_symbols:
        try:
            signals = await predictor.generate_trading_signals(symbol, risk_tolerance="medium")
            
            print(f"\n{symbol}:")
            print(f"  Signal: {signals['signal']}")
            print(f"  Position Size: {signals['position_size']:.1%}")
            print(f"  Stop Loss: {signals['stop_loss_pct']:.1%}")
            print(f"  Take Profit: {signals['take_profit_pct']:.1%}")
            
        except Exception as e:
            print(f"❌ Trading signals xatosi {symbol}: {str(e)}")
    
    print("\n✅ Demo yakunlandi!")

if __name__ == "__main__":
    # Demo ishga tushirish
    asyncio.run(demo_sentiment_market_predictor())