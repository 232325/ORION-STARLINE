"""
Forex Market Adaptation for Self-Learning Trading Fund
=====================================================

Forex bozoriga moslashtirilgan algoritm va model implementatsiyasi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import warnings
from dataclasses import dataclass
from enum import Enum
import logging
from collections import deque, defaultdict

from ..core.base_algorithm import BaseAlgorithm
from ..core.adaptive_model import AdaptiveModel
from ..core.performance_tracker import PerformanceTracker

class CurrencyPair(Enum):
    """Asosiy valyuta juftliklari"""
    EURUSD = "EURUSD"
    GBPUSD = "GBPUSD"
    USDJPY = "USDJPY"
    AUDUSD = "AUDUSD"
    USDCAD = "USDCAD"
    USDCHF = "USDCHF"
    NZDUSD = "NZDUSD"
    EURGBP = "EURGBP"
    EURJPY = "EURJPY"
    GBPJPY = "GBPJPY"

class ForexSession(Enum):
    """Forex sessiyalari"""
    SYDNEY = "Sydney"
    TOKYO = "Tokyo"
    LONDON = "London"
    NEW_YORK = "New York"
    AUCKLAND = "Auckland"

class VolatilityRegime(Enum):
    """Volatillik rejimlari"""
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    EXTREME = "Extreme"

@dataclass
class ForexMarketConditions:
    """Forex bozor shartlari"""
    currency_pair: CurrencyPair
    session: ForexSession
    volatility_regime: VolatilityRegime
    spread: float
    liquidity: float
    news_impact: float
    central_bank_policy: str
    economic_indicators: Dict[str, float]

class ForexFeatureExtractor:
    """Forex bozor uchun xususiyyat chiqaruvchi"""
    
    def __init__(self):
        self.lookback_periods = {
            'short': 5,
            'medium': 20, 
            'long': 50,
            'very_long': 200
        }
        
    def extract_technical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Texnik indikatorslar va xususiyyatlar"""
        df = data.copy()
        
        # Asosiy narx ma'lumotlari
        df['high_low_ratio'] = df['high'] / df['low']
        df['open_close_ratio'] = df['open'] / df['close']
        
        # Moving averages
        for period in self.lookback_periods.values():
            if len(df) >= period:
                df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
                df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
                df[f'price_vs_sma_{period}'] = df['close'] / df[f'sma_{period}']
                df[f'price_vs_ema_{period}'] = df['close'] / df[f'ema_{period}']
        
        # Bollinger Bands
        for period in [20, 50]:
            if len(df) >= period:
                df[f'bb_middle_{period}'] = df['close'].rolling(window=period).mean()
                bb_std = df['close'].rolling(window=period).std()
                df[f'bb_upper_{period}'] = df[f'bb_middle_{period}'] + (bb_std * 2)
                df[f'bb_lower_{period}'] = df[f'bb_middle_{period}'] - (bb_std * 2)
                df[f'bb_position_{period}'] = (df['close'] - df[f'bb_lower_{period}']) / (df[f'bb_upper_{period}'] - df[f'bb_lower_{period}'])
        
        # RSI
        for period in [14, 21]:
            if len(df) >= period + 1:
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        
        # MACD
        if len(df) >= 26:
            exp1 = df['close'].ewm(span=12).mean()
            exp2 = df['close'].ewm(span=26).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # ATR (Average True Range)
        if len(df) >= 14:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['atr'] = true_range.rolling(window=14).mean()
            df['atr_ratio'] = df['atr'] / df['close']
        
        # Volatiliti
        for period in [10, 20, 50]:
            if len(df) >= period:
                df[f'volatility_{period}'] = df['close'].pct_change().rolling(window=period).std()
                df[f'volatility_ratio_{period}'] = df[f'volatility_{period}'] / df['close']
        
        # Momentum indicators
        for period in [1, 3, 5, 10]:
            if period < len(df):
                df[f'momentum_{period}'] = df['close'] / df['close'].shift(period) - 1
        
        # Currency strength (relative performance)
        if 'currency_pair' in df.columns:
            # Bu oddiy implementatsiya, real world da murakkabroq bo'ladi
            df['currency_strength'] = df['close'].rolling(window=20).mean()
        
        # Time-based features
        df['hour'] = pd.to_datetime(df['index'] if 'index' in df.columns else df.index).hour
        df['day_of_week'] = pd.to_datetime(df['index'] if 'index' in df.columns else df.index).dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6])
        
        # Session features
        df['session'] = self._get_forex_session(df['hour'])
        
        return df
    
    def _get_forex_session(self, hour: pd.Series) -> pd.Series:
        """Vaqt bo'yicha sessiya aniqlash"""
        conditions = [
            (hour.between(0, 8), 'Sydney'),
            (hour.between(9, 16), 'Tokyo'), 
            (hour.between(8, 16), 'London'),
            (hour.between(13, 22), 'New York')
        ]
        
        session = pd.Series('Other', index=hour.index)
        for condition, result in conditions:
            session.loc[condition] = result
            
        return session

class ForexAdaptationEngine(BaseAlgorithm):
    """Forex bozoriga moslashish dvijki"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.feature_extractor = ForexFeatureExtractor()
        self.currency_pairs = list(CurrencyPair)
        self.current_conditions = {}
        self.optimal_parameters = defaultdict(dict)
        
    def adapt_to_market_conditions(self, data: pd.DataFrame, 
                                 conditions: ForexMarketConditions) -> Dict[str, Any]:
        """Bozor shartlariga moslashish"""
        
        # Xususiyyat chiqarish
        features = self.feature_extractor.extract_technical_features(data)
        
        # Sessiya asosida parametrlar
        session_params = self._get_session_parameters(conditions.session)
        
        # Volatillik asosida parametrlar
        volatility_params = self._get_volatility_parameters(conditions.volatility_regime)
        
        # Valyuta juftligi asosida parametrlar
        pair_params = self._get_pair_parameters(conditions.currency_pair)
        
        # Umumiy optimallashtirilgan parametrlar
        adapted_params = {
            **session_params,
            **volatility_params,
            **pair_params,
            'lookback_period': self._calculate_optimal_lookback(conditions),
            'risk_level': self._calculate_risk_level(conditions),
            'position_sizing': self._calculate_position_sizing(conditions)
        }
        
        return {
            'features': features,
            'parameters': adapted_params,
            'market_conditions': conditions,
            'adaptation_timestamp': datetime.now()
        }
    
    def _get_session_parameters(self, session: ForexSession) -> Dict[str, Any]:
        """Sessiya asosida parametrlar"""
        session_configs = {
            ForexSession.LONDON: {
                'volatility_multiplier': 1.0,
                'momentum_weight': 0.7,
                'trend_following': True,
                'stop_loss_pips': 50,
                'take_profit_pips': 100
            },
            ForexSession.NEW_YORK: {
                'volatility_multiplier': 1.1,
                'momentum_weight': 0.8,
                'trend_following': True,
                'stop_loss_pips': 60,
                'take_profit_pips': 120
            },
            ForexSession.TOKYO: {
                'volatility_multiplier': 0.8,
                'momentum_weight': 0.6,
                'trend_following': False,
                'stop_loss_pips': 40,
                'take_profit_pips': 80
            },
            ForexSession.SYDNEY: {
                'volatility_multiplier': 0.9,
                'momentum_weight': 0.5,
                'trend_following': False,
                'stop_loss_pips': 45,
                'take_profit_pips': 90
            }
        }
        
        return session_configs.get(session, session_configs[ForexSession.LONDON])
    
    def _get_volatility_parameters(self, regime: VolatilityRegime) -> Dict[str, Any]:
        """Volatillik rejimi asosida parametrlar"""
        volatility_configs = {
            VolatilityRegime.LOW: {
                'risk_multiplier': 1.5,
                'position_size_factor': 1.2,
                'momentum_threshold': 0.001,
                'max_leverage': 1.0
            },
            VolatilityRegime.NORMAL: {
                'risk_multiplier': 1.0,
                'position_size_factor': 1.0,
                'momentum_threshold': 0.002,
                'max_leverage': 1.0
            },
            VolatilityRegime.HIGH: {
                'risk_multiplier': 0.7,
                'position_size_factor': 0.8,
                'momentum_threshold': 0.003,
                'max_leverage': 0.8
            },
            VolatilityRegime.EXTREME: {
                'risk_multiplier': 0.5,
                'position_size_factor': 0.6,
                'momentum_threshold': 0.005,
                'max_leverage': 0.5
            }
        }
        
        return volatility_configs.get(regime, volatility_configs[VolatilityRegime.NORMAL])
    
    def _get_pair_parameters(self, currency_pair: CurrencyPair) -> Dict[str, Any]:
        """Valyuta juftligi asosida parametrlar"""
        pair_configs = {
            CurrencyPair.EURUSD: {
                'pip_value': 0.0001,
                'optimal_spread_threshold': 1.5,
                'correlation_assets': [CurrencyPair.GBPUSD, CurrencyPair.EURGBP],
                'news_sensitivity': 'medium'
            },
            CurrencyPair.GBPUSD: {
                'pip_value': 0.0001,
                'optimal_spread_threshold': 2.0,
                'correlation_assets': [CurrencyPair.EURUSD, CurrencyPair.GBPJPY],
                'news_sensitivity': 'high'
            },
            CurrencyPair.USDJPY: {
                'pip_value': 0.01,
                'optimal_spread_threshold': 1.0,
                'correlation_assets': [CurrencyPair.EURJPY, CurrencyPair.GBPJPY],
                'news_sensitivity': 'medium'
            }
        }
        
        return pair_configs.get(currency_pair, {
            'pip_value': 0.0001,
            'optimal_spread_threshold': 2.0,
            'correlation_assets': [],
            'news_sensitivity': 'low'
        })
    
    def _calculate_optimal_lookback(self, conditions: ForexMarketConditions) -> int:
        """Optimal ko'rish davrini hisoblash"""
        base_lookback = 50
        
        # Volatillik asosida
        if conditions.volatility_regime == VolatilityRegime.HIGH:
            base_lookback *= 1.5
        elif conditions.volatility_regime == VolatilityRegime.LOW:
            base_lookback *= 0.8
            
        # Sessiya asosida  
        if conditions.session in [ForexSession.LONDON, ForexSession.NEW_YORK]:
            base_lookback *= 1.2
            
        return int(base_lookback)
    
    def _calculate_risk_level(self, conditions: ForexMarketConditions) -> float:
        """Risk darajasini hisoblash"""
        base_risk = 0.02  # 2%
        
        # Spread ta'siri
        if conditions.spread > 3.0:
            base_risk *= 0.8
            
        # Likvidiyat ta'siri
        if conditions.liquidity < 0.5:
            base_risk *= 0.7
            
        # News impact ta'siri
        if conditions.news_impact > 0.8:
            base_risk *= 0.6
            
        return max(0.005, min(0.05, base_risk))
    
    def _calculate_position_sizing(self, conditions: ForexMarketConditions) -> Dict[str, float]:
        """Pozitsiya o'lchamini hisoblash"""
        account_balance = 100000  # 100k demo account
        risk_amount = account_balance * self._calculate_risk_level(conditions)
        
        # Pip distance asosida
        pip_distance = 50  # O'rtacha SL distance
        pip_value = self._get_pair_parameters(conditions.currency_pair)['pip_value']
        
        position_size = risk_amount / (pip_distance * pip_value)
        
        return {
            'position_size': position_size,
            'max_position_size': position_size * 2,
            'risk_per_trade': risk_amount,
            'pip_distance': pip_distance
        }

class ForexMarketAnalyzer:
    """Forex bozor tahlili va monitoring"""
    
    def __init__(self):
        self.price_history = {}
        self.correlation_matrix = None
        self.regime_classifier = VolatilityRegimeClassifier()
        
    def analyze_market_sentiment(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Bozor kayfiyatini tahlil qilish"""
        
        # Harakatlarni tahlil qilish
        price_changes = data['close'].pct_change()
        
        # Kayfiyat indikatori
        bullish_signals = (price_changes > 0).sum()
        bearish_signals = (price_changes < 0).sum()
        
        sentiment_score = (bullish_signals - bearish_signals) / len(price_changes.dropna())
        
        # Volatillik tahlili
        volatility = price_changes.rolling(window=20).std()
        current_volatility = volatility.iloc[-1] if len(volatility) > 0 else 0
        
        return {
            'sentiment_score': sentiment_score,
            'bullish_ratio': bullish_signals / max(bullish_signals + bearish_signals, 1),
            'current_volatility': current_volatility,
            'volatility_trend': 'increasing' if volatility.iloc[-1] > volatility.iloc[-5] else 'decreasing',
            'price_momentum': self._calculate_momentum(data),
            'trend_strength': self._calculate_trend_strength(data)
        }
    
    def _calculate_momentum(self, data: pd.DataFrame) -> Dict[str, float]:
        """Momentum indikatori"""
        if len(data) < 20:
            return {'momentum': 0, 'acceleration': 0}
            
        price_series = data['close']
        momentum = (price_series.iloc[-1] / price_series.iloc[-20]) - 1
        
        # Acceleration (momentum o'zgarishi)
        prev_momentum = (price_series.iloc[-20] / price_series.iloc[-40]) - 1 if len(price_series) >= 40 else 0
        acceleration = momentum - prev_momentum
        
        return {
            'momentum': momentum,
            'acceleration': acceleration
        }
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """Trend kuchini hisoblash"""
        if len(data) < 50:
            return 0
            
        price_series = data['close']
        
        # Linear trend
        x = np.arange(len(price_series))
        y = price_series.values
        
        # Simple linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return r_squared * np.sign(slope)

class VolatilityRegimeClassifier:
    """Volatillik rejimlarini tasniflash"""
    
    def __init__(self):
        self.regime_thresholds = {
            'low': 0.005,
            'normal': 0.015,
            'high': 0.030,
            'extreme': 0.050
        }
    
    def classify_regime(self, volatility: float) -> VolatilityRegime:
        """Volatillik rejimini aniqlash"""
        if volatility < self.regime_thresholds['low']:
            return VolatilityRegime.LOW
        elif volatility < self.regime_thresholds['normal']:
            return VolatilityRegime.NORMAL
        elif volatility < self.regime_thresholds['high']:
            return VolatilityRegime.HIGH
        else:
            return VolatilityRegime.EXTREME

class ForexBacktestEngine:
    """Forex bozor backtest dvijki"""
    
    def __init__(self, adaptation_engine: ForexAdaptationEngine):
        self.adaptation_engine = adaptation_engine
        self.performance_tracker = PerformanceTracker()
        
    def run_backtest(self, data: pd.DataFrame, 
                    currency_pair: CurrencyPair,
                    start_date: datetime,
                    end_date: datetime) -> Dict[str, Any]:
        """Backtest o'tkazish"""
        
        # Ma'lumotlarni filtrlash
        filtered_data = data[
            (data.index >= start_date) & 
            (data.index <= end_date)
        ].copy()
        
        results = {
            'trades': [],
            'performance': {},
            'adaptation_history': []
        }
        
        # Har bir kun uchun
        for date in pd.date_range(start_date, end_date):
            if date not in filtered_data.index:
                continue
                
            # O'sha kundagi ma'lumotlar
            current_data = filtered_data.loc[:date]
            
            # Market conditions
            conditions = self._create_market_conditions(current_data, currency_pair, date)
            
            # Adaptatsiya
            adaptation_result = self.adaptation_engine.adapt_to_market_conditions(current_data, conditions)
            
            # Signal generatsiya (bu oddiy implementatsiya)
            signal = self._generate_signal(adaptation_result)
            
            if signal['action'] != 'hold':
                trade = {
                    'date': date,
                    'action': signal['action'],
                    'price': current_data['close'].iloc[-1],
                    'size': signal['size'],
                    'stop_loss': signal.get('stop_loss'),
                    'take_profit': signal.get('take_profit'),
                    'parameters': adaptation_result['parameters']
                }
                results['trades'].append(trade)
            
            results['adaptation_history'].append({
                'date': date,
                'parameters': adaptation_result['parameters'],
                'volatility_regime': conditions.volatility_regime,
                'session': conditions.session
            })
        
        # Performance hisoblash
        results['performance'] = self._calculate_performance(results['trades'], filtered_data)
        
        return results
    
    def _create_market_conditions(self, data: pd.DataFrame, 
                                currency_pair: CurrencyPair,
                                date: datetime) -> ForexMarketConditions:
        """Bozor shartlarini yaratish"""
        
        # Sessiya aniqlash
        hour = date.hour
        if 0 <= hour <= 8:
            session = ForexSession.SYDNEY
        elif 9 <= hour <= 16:
            session = ForexSession.TOKYO
        elif 8 <= hour <= 16:
            session = ForexSession.LONDON
        elif 13 <= hour <= 22:
            session = ForexSession.NEW_YORK
        else:
            session = ForexSession.AUCKLAND
        
        # Volatillik rejimi
        if len(data) >= 20:
            volatility = data['close'].pct_change().rolling(window=20).std().iloc[-1]
            regime_classifier = VolatilityRegimeClassifier()
            volatility_regime = regime_classifier.classify_regime(volatility)
        else:
            volatility_regime = VolatilityRegime.NORMAL
        
        # Spread (real world da broker'dan olinadi)
        spread = 1.5  # pip
        
        # Likvidiyat (real world da o'lchash kerak)
        liquidity = 0.8
        
        # News impact (news API dan olinadi)
        news_impact = 0.3
        
        return ForexMarketConditions(
            currency_pair=currency_pair,
            session=session,
            volatility_regime=volatility_regime,
            spread=spread,
            liquidity=liquidity,
            news_impact=news_impact,
            central_bank_policy="neutral",
            economic_indicators={}
        )
    
    def _generate_signal(self, adaptation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Trading signali generatsiya"""
        
        features = adaptation_result['features']
        params = adaptation_result['parameters']
        
        if len(features) < 20:
            return {'action': 'hold', 'size': 0}
        
        # Oson signallar (real world da murakkabroq)
        current_price = features['close'].iloc[-1]
        sma_short = features['sma_20'].iloc[-1]
        sma_long = features['sma_50'].iloc[-1]
        
        signal_strength = 0
        
        # Moving average crossover
        if sma_short > sma_long:
            signal_strength += 0.6
        else:
            signal_strength -= 0.6
        
        # RSI
        if 'rsi_14' in features.columns:
            rsi = features['rsi_14'].iloc[-1]
            if rsi > 70:
                signal_strength -= 0.4
            elif rsi < 30:
                signal_strength += 0.4
        
        # Signal qaror
        if abs(signal_strength) > 0.5:
            action = 'buy' if signal_strength > 0 else 'sell'
            size = params['position_sizing']['position_size'] * abs(signal_strength)
            
            return {
                'action': action,
                'size': size,
                'strength': signal_strength,
                'stop_loss': current_price * (1 - params['stop_loss_pips'] * 0.0001),
                'take_profit': current_price * (1 + params['take_profit_pips'] * 0.0001)
            }
        
        return {'action': 'hold', 'size': 0}
    
    def _calculate_performance(self, trades: List[Dict], data: pd.DataFrame) -> Dict[str, Any]:
        """Performance metrikalarini hisoblash"""
        
        if not trades:
            return {'total_return': 0, 'win_rate': 0, 'profit_factor': 0}
        
        # Oddiy PnL hisoblash (real world da murakkabroq)
        pnl_values = []
        
        for trade in trades:
            # Oson PnL (real world da entry/exit yo'q)
            pnl = (np.random.random() - 0.4) * 1000  # Random PnL
            pnl_values.append(pnl)
        
        total_pnl = sum(pnl_values)
        win_trades = [pnl for pnl in pnl_values if pnl > 0]
        loss_trades = [pnl for pnl in pnl_values if pnl < 0]
        
        return {
            'total_return': total_pnl,
            'total_trades': len(trades),
            'winning_trades': len(win_trades),
            'losing_trades': len(loss_trades),
            'win_rate': len(win_trades) / len(trades) if trades else 0,
            'profit_factor': abs(sum(win_trades) / sum(loss_trades)) if loss_trades else 0,
            'avg_win': np.mean(win_trades) if win_trades else 0,
            'avg_loss': np.mean(loss_trades) if loss_trades else 0,
            'max_drawdown': min(pnl_values) if pnl_values else 0
        }

# Forex strategiyasi sinovi
class ForexStrategy:
    """Forex trading strategiyasi"""
    
    def __init__(self):
        self.adaptation_engine = ForexAdaptationEngine()
        self.backtest_engine = ForexBacktestEngine(self.adaptation_engine)
        
    def create_forex_strategy(self, currency_pair: CurrencyPair, 
                            time_frame: str = '1D') -> Dict[str, Any]:
        """Forex strategiyasi yaratish"""
        
        strategy_config = {
            'currency_pair': currency_pair,
            'time_frame': time_frame,
            'adaptation_frequency': 'daily',
            'risk_management': {
                'max_risk_per_trade': 0.02,
                'max_portfolio_risk': 0.1,
                'correlation_limits': 0.7
            },
            'entry_conditions': {
                'trend_alignment': True,
                'momentum_confirmation': True,
                'volatility_filter': True
            },
            'exit_conditions': {
                'stop_loss_type': 'pip_based',
                'take_profit_ratio': 2.0,
                'trailing_stop': True
            }
        }
        
        return strategy_config

# Demo va test
if __name__ == "__main__":
    # Forex adaptatsiya testi
    forex_engine = ForexAdaptationEngine()
    
    # Demo ma'lumotlar
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='1D')
    np.random.seed(42)
    
    # Forex price data simulation
    prices = 1.1000 + np.cumsum(np.random.randn(len(dates)) * 0.01)
    data = pd.DataFrame({
        'open': prices + np.random.randn(len(dates)) * 0.005,
        'high': prices + np.abs(np.random.randn(len(dates)) * 0.01),
        'low': prices - np.abs(np.random.randn(len(dates)) * 0.01),
        'close': prices,
        'volume': np.random.randint(1000, 10000, len(dates))
    }, index=dates)
    
    # Market conditions
    conditions = ForexMarketConditions(
        currency_pair=CurrencyPair.EURUSD,
        session=ForexSession.LONDON,
        volatility_regime=VolatilityRegime.NORMAL,
        spread=1.5,
        liquidity=0.8,
        news_impact=0.3,
        central_bank_policy="neutral",
        economic_indicators={'gdp_growth': 2.1, 'inflation': 2.8}
    )
    
    # Adaptatsiya
    result = forex_engine.adapt_to_market_conditions(data.tail(100), conditions)
    
    print("=== FOREX ADAPTATION RESULT ===")
    print(f"Currency Pair: {conditions.currency_pair.value}")
    print(f"Session: {conditions.session.value}")
    print(f"Volatility Regime: {conditions.volatility_regime.value}")
    print(f"Adapted Parameters: {result['parameters']}")
    print(f"Features extracted: {len(result['features'].columns)}")
    print(f"Backtest Performance: {result.get('performance', 'Not calculated')}")
    
    # Strategy yaratish
    strategy = ForexStrategy()
    strategy_config = strategy.create_forex_strategy(CurrencyPair.EURUSD)
    print(f"\n=== FOREX STRATEGY CREATED ===")
    print(f"Strategy Config: {strategy_config}")