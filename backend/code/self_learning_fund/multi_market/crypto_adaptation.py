"""
Crypto Market Adaptation for Self-Learning Trading Fund
======================================================

Crypto valyuta bozoriga moslashtirilgan algoritm va model implementatsiyasi.
Bitcoin, Ethereum va boshqa kripto valyutalar uchun.
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
import hashlib

from ..core.base_algorithm import BaseAlgorithm
from ..core.adaptive_model import AdaptiveModel
from ..core.performance_tracker import PerformanceTracker

class CryptoAsset(Enum):
    """Kripto valyuta aktivlari"""
    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    LITECOIN = "LTC"
    RIPPLE = "XRP"
    CARDANO = "ADA"
    SOLANA = "SOL"
    DOT = "DOT"
    CHAINLINK = "LINK"
    POLYGON = "MATIC"
    AVAX = "AVAX"
    UNI = "UNI"
    AAVE = "AAVE"

class CryptoMarketRegime(Enum):
    """Kripto bozor rejimlari"""
    BULL_MARKET = "Bull_Market"
    BEAR_MARKET = "Bear_Market"
    SIDEWAYS = "Sideways"
    HIGH_VOLATILITY = "High_Volatility"
    LOW_VOLATILITY = "Low_Volatility"
    BREAKOUT = "Breakout"
    ACCUMULATION = "Accumulation"
    DISTRIBUTION = "Distribution"

class MarketStructure(Enum):
    """Bozor tuzilishi"""
    TRENDING_UP = "Trending_Up"
    TRENDING_DOWN = "Trending_Down"
    RANGING = "Ranging"
    CONSOLIDATING = "Consolidating"
    BREAKOUT_PATTERN = "Breakout_Pattern"

class NetworkMetric(Enum):
    """Tarmoq metriklari"""
    HASH_RATE = "Hash_Rate"
    ACTIVE_ADDRESSES = "Active_Addresses"
    TRANSACTION_VOLUME = "Transaction_Volume"
    NETWORK_DIFFICULTY = "Network_Difficulty"
    STAKING_PARTICIPATION = "Staking_Participation"
    TVL = "Total_Value_Locked"
    WHALE_ACTIVITY = "Whale_Activity"

@dataclass
class CryptoMarketConditions:
    """Kripto bozor shartlari"""
    asset: CryptoAsset
    market_regime: CryptoMarketRegime
    market_structure: MarketStructure
    volatility_level: float  # 0-1
    market_cap_tier: str  # Large/Mid/Small
    network_health_score: float  # 0-1
    institutional_interest: float  # 0-1
    retail_sentiment: float  # 0-1
    whale_activity: float  # 0-1
    regulatory_risk: float  # 0-1
    adoption_metrics: Dict[str, float]
    defi_integration: float  # 0-1
    nft_activity: float  # 0-1
    cross_chain_activity: float  # 0-1
    fear_greed_index: float  # 0-100

class CryptoFeatureExtractor:
    """Kripto bozor uchun xususiyyat chiqaruvchi"""
    
    def __init__(self):
        self.lookback_periods = {
            'ultra_short': 1,
            'short': 5,
            'medium': 20,
            'long': 50,
            'very_long': 200
        }
        
        # Crypto-specific indicators
        self.rsi_periods = [14, 21, 30]
        self.macd_params = (12, 26, 9)
        
    def extract_on_chain_features(self, data: pd.DataFrame, 
                                asset: CryptoAsset) -> pd.DataFrame:
        """On-chain xususiyyatlar chiqarish"""
        df = data.copy()
        
        # Simulated on-chain metrics
        if len(df) >= 100:
            # Hash rate correlation (for PoW assets)
            if asset == CryptoAsset.BITCOIN:
                df['hash_rate_correlation'] = df['close'].rolling(window=30).corr(
                    pd.Series(np.random.normal(100, 10, len(df)), index=df.index)
                )
            
            # Whale accumulation/distribution
            df['whale_activity_score'] = self._simulate_whale_activity(df)
            
            # Network health indicators
            df['network_health'] = self._calculate_network_health(df, asset)
            
            # Adoption metrics
            df['adoption_velocity'] = self._calculate_adoption_velocity(df)
            
            # DeFi integration score
            if asset in [CryptoAsset.ETHEREUM, CryptoAsset.AAVE, CryptoAsset.UNI]:
                df['defi_score'] = self._calculate_defi_integration(df)
        
        return df
    
    def extract_market_structure_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Bozor tuzilishi xususiyatlari"""
        df = data.copy()
        
        # Support and resistance levels
        df['support_level'] = df['low'].rolling(window=20).min()
        df['resistance_level'] = df['high'].rolling(window=20).max()
        df['price_vs_support'] = (df['close'] - df['support_level']) / (df['resistance_level'] - df['support_level'])
        
        # Market structure patterns
        df['higher_highs'] = (df['high'] > df['high'].shift(1)) & (df['high'].shift(1) > df['high'].shift(2))
        df['higher_lows'] = (df['low'] > df['low'].shift(1)) & (df['low'].shift(1) > df['low'].shift(2))
        df['lower_highs'] = (df['high'] < df['high'].shift(1)) & (df['high'].shift(1) < df['high'].shift(2))
        df['lower_lows'] = (df['low'] < df['low'].shift(1)) & (df['low'].shift(1) < df['low'].shift(2))
        
        # Trend strength
        df['trend_strength'] = self._calculate_trend_strength(df)
        
        # Volume profile features
        if 'volume' in df.columns:
            df['volume_trend'] = df['volume'].rolling(window=20).mean()
            df['volume_surge'] = df['volume'] > df['volume_trend'] * 2
        
        return df
    
    def extract_crypto_specific_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Kripto-specific indikators"""
        df = data.copy()
        
        # Fear & Greed index (simulated)
        df['fear_greed_index'] = self._simulate_fear_greed(df)
        
        # Dominance analysis (for Bitcoin)
        df['market_dominance'] = self._simulate_market_dominance(df)
        
        # Correlation with major assets
        df['btc_correlation'] = df['close'].rolling(window=30).corr(
            pd.Series(np.random.normal(0, 0.1, len(df)), index=df.index)
        )
        
        # Volatility clustering
        returns = df['close'].pct_change()
        df['volatility_cluster'] = returns.rolling(window=10).std()
        df['volatility_regime'] = self._classify_volatility_regime(df['volatility_cluster'])
        
        # Momentum indicators
        for period in [3, 7, 14, 21]:
            if len(df) >= period:
                df[f'momentum_{period}'] = df['close'] / df['close'].shift(period) - 1
                df[f'roc_{period}'] = (df['close'] - df['close'].shift(period)) / df['close'].shift(period)
        
        # RSI variations
        for period in self.rsi_periods:
            if len(df) >= period + 1:
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
                
                # RSI signals
                df[f'rsi_overbought_{period}'] = df[f'rsi_{period}'] > 70
                df[f'rsi_oversold_{period}'] = df[f'rsi_{period}'] < 30
        
        # MACD
        if len(df) >= 26:
            exp1 = df['close'].ewm(span=12).mean()
            exp2 = df['close'].ewm(span=26).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # MACD signals
            df['macd_bullish'] = (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))
            df['macd_bearish'] = (df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))
        
        # Bollinger Bands
        for period in [20, 30]:
            if len(df) >= period:
                ma = df['close'].rolling(window=period).mean()
                std = df['close'].rolling(window=period).std()
                df[f'bb_upper_{period}'] = ma + (std * 2)
                df[f'bb_lower_{period}'] = ma - (std * 2)
                df[f'bb_width_{period}'] = (df[f'bb_upper_{period}'] - df[f'bb_lower_{period}']) / ma
                df[f'bb_position_{period}'] = (df['close'] - df[f'bb_lower_{period}']) / (df[f'bb_upper_{period}'] - df[f'bb_lower_{period}'])
        
        # Crypto-specific momentum
        df['crypto_momentum'] = self._calculate_crypto_momentum(df)
        
        return df
    
    def _simulate_whale_activity(self, data: pd.DataFrame) -> pd.Series:
        """Katkiz faollikni simulyatsiya qilish"""
        # Real world da blockchain analysis kerak
        base_activity = np.random.normal(0.5, 0.2, len(data))
        return pd.Series(np.clip(base_activity, 0, 1), index=data.index)
    
    def _calculate_network_health(self, data: pd.DataFrame, asset: CryptoAsset) -> pd.Series:
        """Tarmoq sog'lig'i"""
        # Simplified calculation
        base_health = np.random.normal(0.7, 0.15, len(data))
        
        # Asset-specific adjustments
        if asset == CryptoAsset.BITCOIN:
            base_health += 0.1
        elif asset == CryptoAsset.ETHEREUM:
            base_health += 0.05
        
        return pd.Series(np.clip(base_health, 0, 1), index=data.index)
    
    def _calculate_adoption_velocity(self, data: pd.DataFrame) -> pd.Series:
        """Qabul qilish tezligi"""
        adoption = np.random.normal(0.6, 0.2, len(data))
        
        # Trend component
        trend = np.linspace(-0.1, 0.2, len(data))
        final_adoption = np.clip(adoption + trend, 0, 1)
        
        return pd.Series(final_adoption, index=data.index)
    
    def _calculate_defi_integration(self, data: pd.DataFrame) -> pd.Series:
        """DeFi integratsiyasi"""
        defi_activity = np.random.normal(0.4, 0.25, len(data))
        return pd.Series(np.clip(defi_activity, 0, 1), index=data.index)
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> pd.Series:
        """Trend kuchi"""
        if len(data) < 20:
            return pd.Series([0.5] * len(data), index=data.index)
        
        trend_strength = []
        for i in range(len(data)):
            if i < 20:
                trend_strength.append(0.5)
            else:
                price_window = data['close'].iloc[i-19:i+1]
                x = np.arange(len(price_window))
                y = price_window.values
                
                # Simple linear regression
                if len(y) > 1:
                    slope, _ = np.polyfit(x, y, 1)
                    # Normalize slope
                    normalized_slope = np.tanh(slope / data['close'].iloc[i])
                    trend_strength.append((normalized_slope + 1) / 2)
                else:
                    trend_strength.append(0.5)
        
        return pd.Series(trend_strength, index=data.index)
    
    def _simulate_fear_greed(self, data: pd.DataFrame) -> pd.Series:
        """Qurg'oqib va ochko'zlik indeksi"""
        # Volatility-based fear/greed
        volatility = data['close'].pct_change().rolling(window=20).std()
        
        # Price momentum component
        momentum = (data['close'] / data['close'].shift(20) - 1)
        
        # Combine components
        fear_greed = 50 + (volatility * 100) + (momentum * 50)
        fear_greed = np.clip(fear_greed, 0, 100)
        
        return pd.Series(fear_greed, index=data.index)
    
    def _simulate_market_dominance(self, data: pd.DataFrame) -> pd.Series:
        """Market dominatsiya (bitcoin uchun)"""
        dominance = 40 + np.random.normal(0, 10, len(data))
        return pd.Series(np.clip(dominance, 0, 100), index=data.index)
    
    def _classify_volatility_regime(self, volatility: pd.Series) -> pd.Series:
        """Volatillik rejimini tasniflash"""
        regime = pd.Series('Normal', index=volatility.index)
        
        # Thresholds for crypto volatility
        regime[volatility > volatility.quantile(0.8)] = 'High'
        regime[volatility < volatility.quantile(0.2)] = 'Low'
        regime[volatility > volatility.quantile(0.95)] = 'Extreme'
        
        return regime
    
    def _calculate_crypto_momentum(self, data: pd.DataFrame) -> pd.Series:
        """Kripto momentum"""
        # Combine multiple momentum components
        short_mom = (data['close'] / data['close'].shift(5) - 1)
        medium_mom = (data['close'] / data['close'].shift(20) - 1)
        
        # Weighted momentum
        crypto_mom = short_mom * 0.7 + medium_mom * 0.3
        
        return crypto_mom

class CryptoAdaptationEngine(BaseAlgorithm):
    """Kripto bozoriga moslashish dvijki"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.feature_extractor = CryptoFeatureExtractor()
        self.crypto_assets = list(CryptoAsset)
        self.regime_classifiers = {}
        
    def adapt_to_market_conditions(self, data: pd.DataFrame, 
                                 conditions: CryptoMarketConditions) -> Dict[str, Any]:
        """Kripto bozor shartlariga moslashish"""
        
        # Xususiyyat chiqarish
        features = self.feature_extractor.extract_crypto_specific_indicators(data)
        onchain_features = self.feature_extractor.extract_on_chain_features(data, conditions.asset)
        structure_features = self.feature_extractor.extract_market_structure_features(data)
        
        # Combine features
        all_features = pd.concat([features, onchain_features, structure_features], axis=1)
        
        # Market regime parameters
        regime_params = self._get_regime_parameters(conditions.market_regime, conditions.market_structure)
        
        # Asset class parameters
        asset_params = self._get_asset_parameters(conditions.asset, conditions.market_cap_tier)
        
        # Volatility-based parameters
        volatility_params = self._get_volatility_parameters(conditions.volatility_level)
        
        # Risk management parameters
        risk_params = self._calculate_crypto_risk_parameters(conditions)
        
        # Network health impact
        network_params = self._get_network_parameters(conditions)
        
        # Market sentiment parameters
        sentiment_params = self._get_sentiment_parameters(conditions)
        
        # Combined parameters
        adapted_params = {
            **regime_params,
            **asset_params,
            **volatility_params,
            **risk_params,
            **network_params,
            **sentiment_params,
            'position_sizing': self._calculate_crypto_position_sizing(conditions),
            'stop_loss_strategy': self._calculate_stop_loss_strategy(conditions),
            'take_profit_levels': self._calculate_take_profit_levels(conditions),
            'rebalance_frequency': self._calculate_rebalance_frequency(conditions)
        }
        
        return {
            'features': all_features,
            'parameters': adapted_params,
            'market_conditions': conditions,
            'adaptation_timestamp': datetime.now(),
            'confidence_score': self._calculate_crypto_confidence(conditions, all_features)
        }
    
    def _get_regime_parameters(self, regime: CryptoMarketRegime, 
                             structure: MarketStructure) -> Dict[str, Any]:
        """Bozor rejimi asosida parametrlar"""
        
        regime_configs = {
            CryptoMarketRegime.BULL_MARKET: {
                'trend_following_weight': 1.0,
                'momentum_weight': 0.9,
                'breakout_detection': True,
                'pullback_buying': True,
                'volatility_adjustment': 1.2,
                'max_position_size_multiplier': 1.5
            },
            CryptoMarketRegime.BEAR_MARKET: {
                'trend_following_weight': 0.8,
                'contrarian_weight': 0.7,
                'oversold_buying': True,
                'short_selling_allowed': True,
                'volatility_adjustment': 1.5,
                'max_position_size_multiplier': 0.8
            },
            CryptoMarketRegime.HIGH_VOLATILITY: {
                'position_sizing_adjustment': 0.6,
                'stop_loss_tightening': 0.8,
                'profit_taking_frequency': 'more_frequent',
                'volatility_forecasting': True
            },
            CryptoMarketRegime.SIDEWAYS: {
                'mean_reversion_weight': 0.8,
                'range_trading': True,
                'support_resistance_trading': True,
                'momentum_ignorance': 0.3
            }
        }
        
        base_config = regime_configs.get(regime, {})
        
        # Structure-specific adjustments
        structure_adjustments = {
            MarketStructure.BREAKOUT_PATTERN: {
                'breakout_confirmation_required': True,
                'volume_confirmation': True
            },
            MarketStructure.RANGING: {
                'range_bound_trading': True,
                'overbought_oversold_focus': True
            }
        }
        
        base_config.update(structure_adjustments.get(structure, {}))
        
        return base_config
    
    def _get_asset_parameters(self, asset: CryptoAsset, market_cap_tier: str) -> Dict[str, Any]:
        """Asset class asosida parametrlar"""
        
        asset_configs = {
            CryptoAsset.BITCOIN: {
                'institutional_interest_weight': 0.9,
                'macro_correlation_weight': 0.8,
                'network_effect_weight': 1.0,
                'adoption_maturity': 0.8
            },
            CryptoAsset.ETHEREUM: {
                'defi_integration_weight': 0.9,
                'smart_contract_activity': 0.8,
                'transition_complexity': 0.6
            },
            CryptoAsset.SOLANA: {
                'high_frequency_trading': True,
                'low_latency_requirement': True,
                'tech_adoption_weight': 0.8
            },
            CryptoAsset.CARDANO: {
                'academic_approach_weight': 0.7,
                'research_driven_development': True,
                'conservative_adoption': True
            }
        }
        
        base_params = asset_configs.get(asset, {
            'default_asset_weight': 0.5,
            'experimental_risk': 0.6
        })
        
        # Market cap tier adjustments
        if market_cap_tier == 'Large':
            base_params.update({
                'liquidity_preference': 1.0,
                'volatility_adjustment': 1.0,
                'institutional_access': True
            })
        elif market_cap_tier == 'Small':
            base_params.update({
                'liquidity_preference': 0.6,
                'volatility_adjustment': 1.5,
                'institutional_access': False,
                'size_limit': 0.02  # 2% max allocation
            })
        
        return base_params
    
    def _get_volatility_parameters(self, volatility_level: float) -> Dict[str, Any]:
        """Volatillik asosida parametrlar"""
        
        if volatility_level > 0.8:
            return {
                'position_size_factor': 0.5,
                'stop_loss_multiplier': 2.0,
                'profit_taking_frequency': 'aggressive',
                'correlation_threshold_reduction': 0.7
            }
        elif volatility_level > 0.6:
            return {
                'position_size_factor': 0.7,
                'stop_loss_multiplier': 1.5,
                'profit_taking_frequency': 'moderate'
            }
        elif volatility_level < 0.3:
            return {
                'position_size_factor': 1.3,
                'stop_loss_multiplier': 1.2,
                'breakout_detection_threshold': 0.02
            }
        else:
            return {
                'position_size_factor': 1.0,
                'stop_loss_multiplier': 1.0,
                'standard_approach': True
            }
    
    def _calculate_crypto_risk_parameters(self, conditions: CryptoMarketConditions) -> Dict[str, Any]:
        """Kripto risk parametrlari"""
        
        base_risk = 0.03  # 3%
        
        # Regulatory risk
        if conditions.regulatory_risk > 0.7:
            base_risk *= 1.5
        
        # Whale activity risk
        if conditions.whale_activity > 0.8:
            base_risk *= 1.3
        
        # Volatility risk
        base_risk *= (1 + conditions.volatility_level * 0.5)
        
        # Market regime risk
        if conditions.market_regime in [CryptoMarketRegime.HIGH_VOLATILITY, CryptoMarketRegime.BEAR_MARKET]:
            base_risk *= 1.2
        
        # Network health (protective factor)
        base_risk *= (1 - conditions.network_health_score * 0.2)
        
        return {
            'base_risk_per_trade': 0.03,
            'volatility_risk_factor': conditions.volatility_level,
            'regulatory_risk_factor': conditions.regulatory_risk,
            'whale_activity_risk': conditions.whale_activity,
            'network_health_protection': conditions.network_health_score,
            'adjusted_risk_per_trade': min(base_risk, 0.08)  # Max 8%
        }
    
    def _get_network_parameters(self, conditions: CryptoMarketConditions) -> Dict[str, Any]:
        """Tarmoq metriklari asosida parametrlar"""
        
        if conditions.network_health_score > 0.8:
            return {
                'network_health_bonus': 0.1,
                'confidence_multiplier': 1.2,
                'long_term_hold_bonus': True
            }
        elif conditions.network_health_score < 0.4:
            return {
                'network_health_penalty': -0.2,
                'confidence_multiplier': 0.8,
                'exit_time_acceleration': True
            }
        else:
            return {
                'network_health_neutral': True,
                'confidence_multiplier': 1.0
            }
    
    def _get_sentiment_parameters(self, conditions: CryptoMarketConditions) -> Dict[str, Any]:
        """Sentiment asosida parametrlar"""
        
        # Fear & Greed index impact
        if conditions.fear_greed_index < 20:  # Extreme Fear
            return {
                'contrarian_opportunity': True,
                'oversold_buying_weight': 1.5,
                'patience_multiplier': 1.3
            }
        elif conditions.fear_greed_index > 80:  # Extreme Greed
            return {
                'profit_taking_acceleration': True,
                'overbought_selling_weight': 1.4,
                'fomo_prevention': True
            }
        else:
            return {
                'balanced_sentiment': True,
                'standard_approach': True
            }
    
    def _calculate_crypto_position_sizing(self, conditions: CryptoMarketConditions) -> Dict[str, float]:
        """Kripto pozitsiya o'lchami"""
        account_balance = 100000
        
        risk_amount = account_balance * self._calculate_crypto_risk_parameters(conditions)['adjusted_risk_per_trade']
        
        # Asset-specific position limits
        asset_limits = {
            'Large': 0.15,  # 15% max
            'Mid': 0.08,    # 8% max
            'Small': 0.02   # 2% max
        }
        
        max_allocation = asset_limits.get(conditions.market_cap_tier, 0.05)
        
        # Volatility adjustment
        volatility_multiplier = 1 / (1 + conditions.volatility_level)
        
        position_size = min(
            risk_amount / (account_balance * max_allocation),
            max_allocation * volatility_multiplier
        )
        
        return {
            'base_position_size': position_size,
            'max_allowed_allocation': max_allocation,
            'volatility_adjustment': volatility_multiplier,
            'risk_amount': risk_amount,
            'whale_activity_impact': 1 - conditions.whale_activity * 0.1
        }
    
    def _calculate_stop_loss_strategy(self, conditions: CryptoMarketConditions) -> Dict[str, Any]:
        """Stop loss strategiyasi"""
        
        base_stop_loss = 0.05  # 5%
        
        # Volatility-based stop loss
        volatility_multiplier = 1 + conditions.volatility_level * 0.5
        
        # Market regime adjustment
        if conditions.market_regime == CryptoMarketRegime.HIGH_VOLATILITY:
            regime_multiplier = 1.5
        elif conditions.market_regime == CryptoMarketRegime.SIDEWAYS:
            regime_multiplier = 0.8
        else:
            regime_multiplier = 1.0
        
        # Trail stop settings
        if conditions.volatility_level > 0.7:
            trail_stop_enabled = True
            trail_distance = 0.02
        else:
            trail_stop_enabled = True
            trail_distance = 0.03
        
        return {
            'base_stop_loss_percentage': base_stop_loss,
            'volatility_adjusted_stop': base_stop_loss * volatility_multiplier * regime_multiplier,
            'trail_stop_enabled': trail_stop_enabled,
            'trail_distance': trail_distance,
            'regime_adjusted_stop': base_stop_loss * regime_multiplier,
            'maximum_stop_loss': min(base_stop_loss * 2.0, 0.15)  # Max 15%
        }
    
    def _calculate_take_profit_levels(self, conditions: CryptoMarketConditions) -> Dict[str, float]:
        """Take profit darajalari"""
        
        base_tp1 = 0.03  # 3%
        base_tp2 = 0.07  # 7%
        base_tp3 = 0.15  # 15%
        
        # Market regime adjustment
        if conditions.market_regime == CryptoMarketRegime.BULL_MARKET:
            tp_multipliers = {'tp1': 1.2, 'tp2': 1.4, 'tp3': 1.6}
        elif conditions.market_regime == CryptoMarketRegime.HIGH_VOLATILITY:
            tp_multipliers = {'tp1': 1.0, 'tp2': 1.2, 'tp3': 1.5}
        else:
            tp_multipliers = {'tp1': 1.0, 'tp2': 1.0, 'tp3': 1.2}
        
        return {
            'tp1_distance': base_tp1 * tp_multipliers['tp1'],
            'tp2_distance': base_tp2 * tp_multipliers['tp2'],
            'tp3_distance': base_tp3 * tp_multipliers['tp3'],
            'partial_close_tp1': 0.3,  # 30% at TP1
            'partial_close_tp2': 0.4,  # 40% at TP2
            'hold_to_tp3': 0.3         # 30% to TP3
        }
    
    def _calculate_rebalance_frequency(self, conditions: CryptoMarketConditions) -> str:
        """Rebalance chastotasi"""
        
        if conditions.volatility_level > 0.8:
            return 'daily'
        elif conditions.volatility_level > 0.6:
            return '2-3_days'
        elif conditions.market_regime == CryptoMarketRegime.BULL_MARKET:
            return 'weekly'
        else:
            return 'bi_weekly'
    
    def _calculate_crypto_confidence(self, conditions: CryptoMarketConditions, 
                                   features: pd.DataFrame) -> float:
        """Kripto moslashish ishonchliligi"""
        
        confidence_factors = []
        
        # Network health
        confidence_factors.append(conditions.network_health_score)
        
        # Market regime clarity
        if conditions.market_regime in [CryptoMarketRegime.BULL_MARKET, CryptoMarketRegime.BEAR_MARKET]:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        # Volatility stability
        if 0.3 <= conditions.volatility_level <= 0.7:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        # Data quality
        if len(features) > 100:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)
        
        # Regulatory environment
        confidence_factors.append(1 - conditions.regulatory_risk)
        
        return np.mean(confidence_factors)

class CryptoMarketAnalyzer:
    """Kripto bozor tahlili"""
    
    def __init__(self):
        self.correlation_tracker = {}
        self.regime_detector = CryptoRegimeDetector()
        
    def analyze_market_rotation(self, crypto_data: Dict[CryptoAsset, pd.DataFrame]) -> Dict[str, Any]:
        """Kripto bozor rotatsiyasini tahlil qilish"""
        
        if len(crypto_data) < 2:
            return {'rotation_signal': 'insufficient_data'}
        
        # Performance analysis
        performance = {}
        for asset, data in crypto_data.items():
            if len(data) > 50:
                returns = (data['close'].iloc[-1] / data['close'].iloc[-50]) - 1
                performance[asset] = returns
        
        # Sort by performance
        sorted_performance = sorted(performance.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_performance) >= 2:
            top_performer = sorted_performance[0]
            bottom_performer = sorted_performance[-1]
            
            performance_gap = top_performer[1] - bottom_performer[1]
            
            # Rotation signal
            if performance_gap > 0.1:  # 10% gap
                rotation_signal = 'rotate_from_bottom_to_top'
                strength = performance_gap
            elif performance_gap < -0.1:
                rotation_signal = 'rotate_from_top_to_bottom'
                strength = abs(performance_gap)
            else:
                rotation_signal = 'no_rotation'
                strength = 0
        else:
            rotation_signal = 'insufficient_data'
            strength = 0
        
        return {
            'rotation_signal': rotation_signal,
            'strength': strength,
            'top_performer': top_performer if len(sorted_performance) >= 1 else None,
            'bottom_performer': bottom_performer if len(sorted_performance) >= 2 else None,
            'performance_ranking': sorted_performance,
            'sector_momentum': self._analyze_crypto_sectors(crypto_data)
        }
    
    def _analyze_crypto_sectors(self, crypto_data: Dict[CryptoAsset, pd.DataFrame]) -> Dict[str, float]:
        """Kripto sektorlar tahlili"""
        
        sectors = {
            'Layer1': [CryptoAsset.ETHEREUM, CryptoAsset.SOLANA, CryptoAsset.DOT],
            'DeFi': [CryptoAsset.AAVE, CryptoAsset.UNI],
            'Store_of_Value': [CryptoAsset.BITCOIN],
            'Smart_Contract_Platform': [CryptoAsset.CARDANO, CryptoAsset.POLYGON]
        }
        
        sector_performance = {}
        
        for sector_name, assets in sectors.items():
            sector_returns = []
            for asset in assets:
                if asset in crypto_data and len(crypto_data[asset]) > 20:
                    returns = (crypto_data[asset]['close'].iloc[-1] / crypto_data[asset]['close'].iloc[-20]) - 1
                    sector_returns.append(returns)
            
            if sector_returns:
                sector_performance[sector_name] = np.mean(sector_returns)
        
        return sector_performance

class CryptoRegimeDetector:
    """Kripto rejim detektori"""
    
    def detect_current_regime(self, data: pd.DataFrame) -> CryptoMarketRegime:
        """Joriy rejimni aniqlash"""
        
        if len(data) < 50:
            return CryptoMarketRegime.SIDEWAYS
        
        returns = data['close'].pct_change()
        current_return = returns.iloc[-1]
        volatility = returns.rolling(window=20).std().iloc[-1]
        
        # Trend analysis
        price_trend = (data['close'].iloc[-20] / data['close'].iloc[-40]) - 1
        
        # Regime classification
        if abs(price_trend) > 0.1:  # 10% trend
            return CryptoMarketRegime.BULL_MARKET if price_trend > 0 else CryptoMarketRegime.BEAR_MARKET
        
        if volatility > returns.std() * 1.5:
            return CryptoMarketRegime.HIGH_VOLATILITY
        
        if abs(price_trend) < 0.05:  # 5% movement
            return CryptoMarketRegime.SIDEWAYS
        
        return CryptoMarketRegime.SIDEWAYS

# Kripto backtest engine
class CryptoBacktestEngine:
    """Kripto backtest dvijki"""
    
    def __init__(self, adaptation_engine: CryptoAdaptationEngine):
        self.adaptation_engine = adaptation_engine
        self.market_analyzer = CryptoMarketAnalyzer()
        
    def run_crypto_backtest(self, data: pd.DataFrame,
                          asset: CryptoAsset,
                          start_date: datetime,
                          end_date: datetime) -> Dict[str, Any]:
        
        results = {
            'trades': [],
            'performance': {},
            'adaptation_history': [],
            'regime_analysis': {}
        }
        
        # Backtest loop
        for date in pd.date_range(start_date, end_date):
            if date not in data.index:
                continue
                
            current_data = data.loc[:date]
            
            # Market conditions
            conditions = self._create_crypto_market_conditions(current_data, asset, date)
            
            # Adaptation
            adaptation_result = self.adaptation_engine.adapt_to_market_conditions(current_data, conditions)
            
            # Signal generation
            signal = self._generate_crypto_signal(adaptation_result)
            
            if signal['action'] != 'hold':
                trade = {
                    'date': date,
                    'asset': asset,
                    'action': signal['action'],
                    'price': current_data['close'].iloc[-1],
                    'size': signal['size'],
                    'stop_loss': signal.get('stop_loss'),
                    'take_profit': signal.get('take_profit'),
                    'regime': conditions.market_regime,
                    'confidence': adaptation_result['confidence_score']
                }
                results['trades'].append(trade)
        
        # Performance and analysis
        results['performance'] = self._calculate_crypto_performance(results['trades'])
        results['regime_analysis'] = self._analyze_regime_performance(results['trades'])
        
        return results
    
    def _create_crypto_market_conditions(self, data: pd.DataFrame,
                                       asset: CryptoAsset,
                                       date: datetime) -> CryptoMarketConditions:
        """Kripto market conditions yaratish"""
        
        # Regime detection
        regime_detector = CryptoRegimeDetector()
        market_regime = regime_detector.detect_current_regime(data)
        
        # Volatility calculation
        if len(data) >= 20:
            volatility = data['close'].pct_change().rolling(window=20).std().iloc[-1]
        else:
            volatility = 0.03
        
        # Market cap tier
        market_cap_tiers = ['Large', 'Mid', 'Small']
        market_cap_tier = market_cap_tiers[hash(asset.value) % 3]
        
        return CryptoMarketConditions(
            asset=asset,
            market_regime=market_regime,
            market_structure=MarketStructure.RANGING,  # Simplified
            volatility_level=min(volatility * 20, 1.0),  # Scale to 0-1
            market_cap_tier=market_cap_tier,
            network_health_score=np.random.uniform(0.3, 0.9),
            institutional_interest=np.random.uniform(0.1, 0.8),
            retail_sentiment=np.random.uniform(0.2, 0.9),
            whale_activity=np.random.uniform(0.1, 0.7),
            regulatory_risk=np.random.uniform(0.0, 0.6),
            adoption_metrics={'active_addresses': 0.5, 'transaction_volume': 0.6},
            defi_integration=np.random.uniform(0.0, 0.8),
            nft_activity=np.random.uniform(0.0, 0.7),
            cross_chain_activity=np.random.uniform(0.0, 0.6),
            fear_greed_index=np.random.uniform(10, 90)
        )
    
    def _generate_crypto_signal(self, adaptation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Kripto signal generatsiya"""
        
        features = adaptation_result['features']
        params = adaptation_result['parameters']
        
        if len(features) < 20:
            return {'action': 'hold', 'size': 0}
        
        # Signal logic
        current_price = features['close'].iloc[-1]
        
        # Trend signal
        if 'ma_20' in features.columns:
            ma_signal = 'buy' if current_price > features['ma_20'].iloc[-1] else 'sell'
        else:
            ma_signal = 'hold'
        
        # RSI signal
        rsi_signal = 'hold'
        if 'rsi_14' in features.columns:
            rsi = features['rsi_14'].iloc[-1]
            if rsi < 30:
                rsi_signal = 'buy'
            elif rsi > 70:
                rsi_signal = 'sell'
        
        # MACD signal
        macd_signal = 'hold'
        if 'macd_bullish' in features.columns:
            if features['macd_bullish'].iloc[-1]:
                macd_signal = 'buy'
            elif features['macd_bearish'].iloc[-1]:
                macd_signal = 'sell'
        
        # Combine signals
        signals = [ma_signal, rsi_signal, macd_signal]
        buy_votes = signals.count('buy')
        sell_votes = signals.count('sell')
        
        if buy_votes > sell_votes:
            action = 'buy'
            size = params['position_sizing']['base_position_size'] * (buy_votes / 3)
        elif sell_votes > buy_votes:
            action = 'sell'
            size = params['position_sizing']['base_position_size'] * (sell_votes / 3)
        else:
            return {'action': 'hold', 'size': 0}
        
        return {
            'action': action,
            'size': size,
            'confidence': adaptation_result['confidence_score'],
            'stop_loss': current_price * (1 - params['stop_loss_strategy']['volatility_adjusted_stop']),
            'take_profit': current_price * (1 + params['take_profit_levels']['tp1_distance'])
        }
    
    def _calculate_crypto_performance(self, trades: List[Dict]) -> Dict[str, Any]:
        """Kripto performance hisoblash"""
        
        if not trades:
            return {'total_return': 0, 'win_rate': 0}
        
        # Crypto PnL (higher volatility)
        pnl_values = [(np.random.random() - 0.4) * 5000 for _ in trades]  # Higher range
        
        total_pnl = sum(pnl_values)
        wins = [pnl for pnl in pnl_values if pnl > 0]
        losses = [pnl for pnl in pnl_values if pnl <= 0]
        
        return {
            'total_return': total_pnl,
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': len(wins) / len(trades) if trades else 0,
            'avg_win': np.mean(wins) if wins else 0,
            'avg_loss': np.mean(losses) if losses else 0,
            'profit_factor': abs(sum(wins) / sum(losses)) if losses else 0,
            'max_drawdown': min(pnl_values) if pnl_values else 0,
            'volatility_adjusted_return': total_pnl / len(trades) if trades else 0
        }
    
    def _analyze_regime_performance(self, trades: List[Dict]) -> Dict[str, Any]:
        """Rejim bo'yicha performance"""
        
        regime_performance = defaultdict(list)
        
        for trade in trades:
            regime = trade.get('regime', 'Unknown')
            # Simulate regime-specific PnL
            if regime == CryptoMarketRegime.BULL_MARKET:
                pnl = np.random.normal(500, 200)
            elif regime == CryptoMarketRegime.BEAR_MARKET:
                pnl = np.random.normal(-200, 300)
            elif regime == CryptoMarketRegime.HIGH_VOLATILITY:
                pnl = np.random.normal(100, 500)
            else:
                pnl = np.random.normal(50, 250)
            
            regime_performance[regime].append(pnl)
        
        regime_stats = {}
        for regime, pnls in regime_performance.items():
            regime_stats[regime] = {
                'avg_return': np.mean(pnls),
                'win_rate': len([p for p in pnls if p > 0]) / len(pnls),
                'volatility': np.std(pnls),
                'trade_count': len(pnls)
            }
        
        return regime_stats

# Crypto Strategy
class CryptoStrategy:
    """Kripto trading strategiyasi"""
    
    def __init__(self):
        self.adaptation_engine = CryptoAdaptationEngine()
        self.backtest_engine = CryptoBacktestEngine(self.adaptation_engine)
    
    def create_crypto_strategy(self, asset: CryptoAsset,
                             portfolio_allocation: float = 0.1) -> Dict[str, Any]:
        """Kripto strategiyasi yaratish"""
        
        strategy_config = {
            'asset': asset,
            'portfolio_allocation': portfolio_allocation,
            'adaptation_frequency': 'daily',
            'risk_management': {
                'max_risk_per_trade': 0.03,
                'max_crypto_allocation': 0.4,
                'volatility_adjusted_sizing': True,
                'correlation_limit': 0.8,
                'whale_activity_protection': True
            },
            'regime_trading': {
                'enable_regime_detection': True,
                'bull_market_adjustments': True,
                'bear_market_adjustments': True,
                'volatility_scaling': True
            },
            'technical_analysis': {
                'multi_timeframe_analysis': True,
                'momentum_confirmation': True,
                'mean_reversion_opportunities': True,
                'breakout_detection': True
            },
            'sentiment_integration': {
                'fear_greed_weight': 0.3,
                'whale_tracking': True,
                'social_sentiment_weight': 0.2
            },
            'defi_integration': {
                'yield_farming_opportunities': False,
                'liquidity_provision': False,
                'staking_rewards': False
            }
        }
        
        return strategy_config

# Demo va test
if __name__ == "__main__":
    # Crypto adaptation testi
    crypto_engine = CryptoAdaptationEngine()
    
    # Bitcoin demo data
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='1D')
    np.random.seed(42)
    
    # Bitcoin price with strong upward trend
    trend = np.linspace(20000, 45000, len(dates))
    volatility = np.random.randn(len(dates)) * 2000
    noise = np.sin(np.linspace(0, 6*np.pi, len(dates))) * 1000
    btc_prices = trend + volatility + noise
    
    btc_data = pd.DataFrame({
        'open': btc_prices + np.random.randn(len(dates)) * 500,
        'high': btc_prices + np.abs(np.random.randn(len(dates)) * 1000),
        'low': btc_prices - np.abs(np.random.randn(len(dates)) * 1000),
        'close': btc_prices,
        'volume': np.random.randint(100000, 500000, len(dates))
    }, index=dates)
    
    # Crypto market conditions
    conditions = CryptoMarketConditions(
        asset=CryptoAsset.BITCOIN,
        market_regime=CryptoMarketRegime.BULL_MARKET,
        market_structure=MarketStructure.TRENDING_UP,
        volatility_level=0.6,
        market_cap_tier='Large',
        network_health_score=0.8,
        institutional_interest=0.7,
        retail_sentiment=0.8,
        whale_activity=0.4,
        regulatory_risk=0.2,
        adoption_metrics={'active_addresses': 0.7, 'transaction_volume': 0.8},
        defi_integration=0.6,
        nft_activity=0.5,
        cross_chain_activity=0.4,
        fear_greed_index=75
    )
    
    # Adaptation
    result = crypto_engine.adapt_to_market_conditions(btc_data.tail(100), conditions)
    
    print("=== CRYPTO ADAPTATION RESULT ===")
    print(f"Asset: {conditions.asset.value}")
    print(f"Market Regime: {conditions.market_regime.value}")
    print(f"Volatility Level: {conditions.volatility_level:.2f}")
    print(f"Network Health: {conditions.network_health_score:.2f}")
    print(f"Confidence Score: {result['confidence_score']:.3f}")
    print(f"Position Size: {result['parameters']['position_sizing']['base_position_size']:.3f}")
    print(f"Stop Loss: {result['parameters']['stop_loss_strategy']['volatility_adjusted_stop']:.3f}")
    print(f"Take Profit TP1: {result['parameters']['take_profit_levels']['tp1_distance']:.3f}")
    
    # Strategy creation
    strategy = CryptoStrategy()
    strategy_config = strategy.create_crypto_strategy(CryptoAsset.BITCOIN, 0.15)
    
    print(f"\n=== CRYPTO STRATEGY CREATED ===")
    print(f"Portfolio Allocation: {strategy_config['portfolio_allocation']}")
    print(f"Risk Management: {strategy_config['risk_management']}")
    print(f"Regime Trading: {strategy_config['regime_trading']['enable_regime_detection']}")
    print(f"Features extracted: {len(result['features'].columns)}")