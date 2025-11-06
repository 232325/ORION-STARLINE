"""
Metal Market Adaptation for Self-Learning Trading Fund
====================================================

Metal bozoriga moslashtirilgan algoritm va model implementatsiyasi.
Oltin, kumush, platinum va boshqa qimmatbop metallar uchun.
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

class MetalType(Enum):
    """Metallar turlari"""
    GOLD = "GOLD"
    SILVER = "SILVER"
    PLATINUM = "PLATINUM"
    PALLADIUM = "PALLADIUM"
    COPPER = "COPPER"
    ALUMINUM = "ALUMINUM"
    NICKEL = "NICKEL"
    ZINC = "ZINC"

class MetalMarketSector(Enum):
    """Metal bozor sektorlari"""
    PRECIOUS_METALS = "Precious_Metals"
    INDUSTRIAL_METALS = "Industrial_Metals"
    BASE_METALS = "Base_Metals"
    ENERGY_RELATED = "Energy_Related"

class MarketEventType(Enum):
    """Bozor voqealari"""
    GEOPOLITICAL_TENSION = "Geopolitical_Tension"
    ECONOMIC_INDICATORS = "Economic_Indicators"
    CENTRAL_BANK_POLICY = "Central_Bank_Policy"
    INFLATION_DATA = "Inflation_Data"
    CURRENCY_MOVEMENTS = "Currency_Movements"
    INDUSTRIAL_DEMAND = "Industrial_Demand"
    TECHNICAL_BREAKOUT = "Technical_Breakout"
    NEWS_SENTIMENT = "News_Sentiment"

@dataclass
class MetalMarketConditions:
    """Metal bozor shartlari"""
    metal_type: MetalType
    sector: MetalMarketSector
    market_event: MarketEventType
    supply_demand_ratio: float
    inventory_levels: float
    mine_production: float
    central_bank_holdings: float
    inflation_hedge_demand: float
    industrial_demand: float
    jewelry_demand: float
    investment_demand: float
    geopolitical_risk: float
    usd_strength: float
    real_interest_rates: float
    economic_uncertainty: float

class MetalFeatureExtractor:
    """Metal bozor uchun xususiyyat chiqaruvchi"""
    
    def __init__(self):
        self.lookback_periods = {
            'short': 5,
            'medium': 20,
            'long': 50,
            'trend': 200
        }
        
    def extract_metal_specific_features(self, data: pd.DataFrame, 
                                      metal_type: MetalType) -> pd.DataFrame:
        """Metal specific xususiyyatlar"""
        df = data.copy()
        
        # Basic price features
        df['price_change'] = df['close'].pct_change()
        df['volatility'] = df['price_change'].rolling(window=20).std()
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
        
        # Metal-specific moving averages
        for period in self.lookback_periods.values():
            if len(df) >= period:
                df[f'ma_{period}'] = df['close'].rolling(window=period).mean()
                df[f'price_ma_ratio_{period}'] = df['close'] / df[f'ma_{period}']
        
        # Metal momentum indicators
        df['momentum_1d'] = df['close'] / df['close'].shift(1) - 1
        df['momentum_3d'] = df['close'] / df['close'].shift(3) - 1
        df['momentum_1w'] = df['close'] / df['close'].shift(7) - 1
        
        # Relative strength to other metals
        df['relative_strength'] = self._calculate_relative_strength(df, metal_type)
        
        # Dollar strength correlation
        df['dollar_correlation'] = self._calculate_dollar_correlation(df)
        
        # Inflation hedge features
        df['inflation_hedge_strength'] = self._calculate_inflation_hedge_signal(df)
        
        # Supply/demand signals
        df['supply_demand_signal'] = self._calculate_supply_demand_signal(df)
        
        # Geopolitical risk indicators
        df['geopolitical_risk_score'] = self._calculate_geopolitical_risk(df)
        
        return df
    
    def extract_economic_indicators(self, data: pd.DataFrame, 
                                  metal_type: MetalType) -> pd.DataFrame:
        """Iqtisodiy indikatorslar"""
        df = data.copy()
        
        # Real interest rates (simplified)
        if len(df) >= 252:  # 1 year
            df['real_interest_rate'] = df['close'].pct_change(252) / df['close']
        
        # Currency strength indicators
        df['usd_strength'] = self._estimate_usd_strength(df)
        
        # Inflation expectations
        df['inflation_expectations'] = self._calculate_inflation_expectations(df)
        
        # Industrial demand indicators
        df['industrial_demand_index'] = self._calculate_industrial_demand(df, metal_type)
        
        return df
    
    def _calculate_relative_strength(self, data: pd.DataFrame, metal_type: MetalType) -> pd.Series:
        """Boshqa metallarga nisbotan kuch"""
        # Real world da boshqa metal narxlari bilan korrelyatsiya
        base_strength = np.random.random(len(data)) * 0.1
        return pd.Series(base_strength, index=data.index)
    
    def _calculate_dollar_correlation(self, data: pd.DataFrame) -> pd.Series:
        """Dollar korrelyatsiyasi"""
        # USD index o'rniga simulatsiya
        return data['close'].pct_change().rolling(window=30).corr(
            pd.Series(np.random.randn(len(data)), index=data.index)
        )
    
    def _calculate_inflation_hedge_signal(self, data: pd.DataFrame) -> pd.Series:
        """Inflatsiyadan himoya signal"""
        price_changes = data['close'].pct_change(252)  # 1 year
        inflation_proxy = price_changes.rolling(window=50).mean()
        return inflation_proxy * 0.5  # Simplified calculation
    
    def _calculate_supply_demand_signal(self, data: pd.DataFrame) -> pd.Series:
        """Taklif va talab signal"""
        volume_trend = data['volume'].rolling(window=20).mean()
        price_trend = data['close'].pct_change(20)
        return (volume_trend * price_trend).rolling(window=10).mean()
    
    def _calculate_geopolitical_risk(self, data: pd.DataFrame) -> pd.Series:
        """Geopolitik risk indikatori"""
        # News sentiment o'rniga random signal
        return pd.Series(np.random.normal(0, 0.1, len(data)), index=data.index)
    
    def _estimate_usd_strength(self, data: pd.DataFrame) -> pd.Series:
        """Dollar kuchini taxmin qilish"""
        # Real world da USD index kerak
        return pd.Series(np.random.normal(100, 5, len(data)), index=data.index)
    
    def _calculate_inflation_expectations(self, data: pd.DataFrame) -> pd.Series:
        """Inflatsiya kutishlar"""
        return data['close'].pct_change(252).rolling(window=50).mean()
    
    def _calculate_industrial_demand(self, data: pd.DataFrame, metal_type: MetalType) -> pd.Series:
        """Sanoat talabi indikatori"""
        if metal_type in [MetalType.GOLD, MetalType.SILVER]:
            # Oltin va kumush - kamroq industrial
            base_demand = 0.3
        elif metal_type in [MetalType.COPPER, MetalType.ALUMINUM]:
            # Asosiy metallar - ko'proq industrial
            base_demand = 0.8
        else:
            base_demand = 0.6
            
        return pd.Series(base_demand + np.random.normal(0, 0.1, len(data)), index=data.index)

class MetalAdaptationEngine(BaseAlgorithm):
    """Metal bozoriga moslashish dvijki"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.feature_extractor = MetalFeatureExtractor()
        self.metal_types = list(MetalType)
        self.current_conditions = {}
        self.correlations = {}
        
    def adapt_to_market_conditions(self, data: pd.DataFrame, 
                                 conditions: MetalMarketConditions) -> Dict[str, Any]:
        """Metal bozor shartlariga moslashish"""
        
        # Xususiyyat chiqarish
        features = self.feature_extractor.extract_metal_specific_features(data, conditions.metal_type)
        economic_features = self.feature_extractor.extract_economic_indicators(data, conditions.metal_type)
        
        # Qo'shilgan xususiyyatlar
        features = pd.concat([features, economic_features], axis=1)
        
        # Sector-based parameters
        sector_params = self._get_sector_parameters(conditions.sector, conditions.metal_type)
        
        # Market event parameters
        event_params = self._get_event_parameters(conditions.market_event)
        
        # Supply/demand based parameters
        supply_demand_params = self._get_supply_demand_parameters(conditions)
        
        # Risk management parameters
        risk_params = self._calculate_risk_parameters(conditions)
        
        # Optimal parameters
        adapted_params = {
            **sector_params,
            **event_params,
            **supply_demand_params,
            **risk_params,
            'position_sizing': self._calculate_position_sizing(conditions),
            'stop_loss_distance': self._calculate_stop_loss(conditions),
            'take_profit_ratio': self._calculate_take_profit_ratio(conditions)
        }
        
        return {
            'features': features,
            'parameters': adapted_params,
            'market_conditions': conditions,
            'adaptation_timestamp': datetime.now(),
            'confidence_score': self._calculate_adaptation_confidence(conditions, features)
        }
    
    def _get_sector_parameters(self, sector: MetalMarketSector, metal_type: MetalType) -> Dict[str, Any]:
        """Sektor asosida parametrlar"""
        
        sector_configs = {
            MetalMarketSector.PRECIOUS_METALS: {
                'momentum_weight': 0.6,
                'trend_following_weight': 0.8,
                'inflation_hedge_weight': 0.9,
                'volatility_multiplier': 1.2,
                'correlation_threshold': 0.7,
                'optimal_hold_period': 30,
                'risk_multiplier': 0.8
            },
            MetalMarketSector.INDUSTRIAL_METALS: {
                'momentum_weight': 0.7,
                'trend_following_weight': 0.6,
                'industrial_demand_weight': 0.8,
                'volatility_multiplier': 1.0,
                'correlation_threshold': 0.6,
                'optimal_hold_period': 20,
                'risk_multiplier': 1.0
            },
            MetalMarketSector.BASE_METALS: {
                'momentum_weight': 0.8,
                'trend_following_weight': 0.5,
                'economic_sensitivity_weight': 0.9,
                'volatility_multiplier': 0.9,
                'correlation_threshold': 0.5,
                'optimal_hold_period': 15,
                'risk_multiplier': 1.1
            }
        }
        
        base_params = sector_configs.get(sector, sector_configs[MetalMarketSector.INDUSTRIAL_METALS])
        
        # Metal-specific adjustments
        if metal_type == MetalType.GOLD:
            base_params.update({
                'inflation_hedge_weight': 1.0,
                'geopolitical_risk_weight': 0.9,
                'safe_haven_demand': 0.8
            })
        elif metal_type == MetalType.SILVER:
            base_params.update({
                'industrial_demand_weight': 0.7,
                'technology_demand_weight': 0.6
            })
        
        return base_params
    
    def _get_event_parameters(self, market_event: MarketEventType) -> Dict[str, Any]:
        """Bozor voqeasi asosida parametrlar"""
        
        event_configs = {
            MarketEventType.GEOPOLITICAL_TENSION: {
                'safe_haven_weight': 1.0,
                'volatility_adjustment': 1.5,
                'risk_multiplier': 0.6,
                'trend_following': False
            },
            MarketEventType.ECONOMIC_INDICATORS: {
                'fundamentals_weight': 1.0,
                'correlation_sensitivity': 1.2,
                'event_impact_multiplier': 2.0
            },
            MarketEventType.CENTRAL_BANK_POLICY: {
                'monetary_policy_weight': 1.0,
                'interest_rate_sensitivity': 1.3,
                'currency_impact_weight': 0.9
            },
            MarketEventType.INFLATION_DATA: {
                'inflation_hedge_weight': 1.0,
                'real_interest_rate_sensitivity': 1.2,
                'hedge_demand_multiplier': 1.5
            },
            MarketEventType.INDUSTRIAL_DEMAND: {
                'demand_weight': 1.0,
                'industrial_demand_sensitivity': 1.4,
                'inventory_level_impact': 0.8
            }
        }
        
        return event_configs.get(market_event, {
            'default_weight': 1.0,
            'volatility_adjustment': 1.0,
            'risk_multiplier': 1.0
        })
    
    def _get_supply_demand_parameters(self, conditions: MetalMarketConditions) -> Dict[str, Any]:
        """Taklif va talab asosida parametrlar"""
        
        # Supply/Demand ratio asosida
        if conditions.supply_demand_ratio > 1.2:
            # Ko'proq taklif - bearish signal
            supply_params = {
                'bearish_bias': 0.7,
                'price_pressure': 'downward',
                'inventory_release_risk': 0.8
            }
        elif conditions.supply_demand_ratio < 0.8:
            # Kam taklif - bullish signal
            supply_params = {
                'bullish_bias': 0.8,
                'price_pressure': 'upward',
                'shortage_risk': 0.9
            }
        else:
            supply_params = {
                'neutral_bias': 0.5,
                'price_pressure': 'balanced',
                'market_balance': 0.7
            }
        
        # Inventory levels
        inventory_impact = conditions.inventory_levels * 0.1
        
        # Central bank holdings impact
        cb_holdings_impact = conditions.central_bank_holdings * 0.05
        
        return {
            **supply_params,
            'inventory_impact': inventory_impact,
            'cb_holdings_impact': cb_holdings_impact,
            'demand_factor': (conditions.industrial_demand + conditions.investment_demand) / 2,
            'supply_demand_balance': conditions.supply_demand_ratio
        }
    
    def _calculate_risk_parameters(self, conditions: MetalMarketConditions) -> Dict[str, Any]:
        """Risk parametrlari hisoblash"""
        
        # Asosiy risk factor
        base_risk = 0.02  # 2%
        
        # Volatillik ta'siri
        volatility_adjustment = 1.0
        if conditions.geopolitical_risk > 0.7:
            volatility_adjustment *= 1.5
        if conditions.economic_uncertainty > 0.6:
            volatility_adjustment *= 1.3
        
        # USD strength ta'siri
        if conditions.usd_strength > 1.1:
            volatility_adjustment *= 1.2
        
        # Real interest rates ta'siri
        if conditions.real_interest_rates > 0.05:
            volatility_adjustment *= 0.9
        elif conditions.real_interest_rates < 0:
            volatility_adjustment *= 1.1
        
        final_risk = base_risk * volatility_adjustment
        
        return {
            'base_risk': base_risk,
            'volatility_multiplier': volatility_adjustment,
            'geopolitical_risk_factor': conditions.geopolitical_risk,
            'economic_uncertainty_factor': conditions.economic_uncertainty,
            'usd_strength_impact': abs(conditions.usd_strength - 1.0),
            'final_risk': min(final_risk, 0.05)  # Max 5%
        }
    
    def _calculate_position_sizing(self, conditions: MetalMarketConditions) -> Dict[str, float]:
        """Pozitsiya o'lchami hisoblash"""
        account_balance = 100000  # Demo account
        
        risk_amount = account_balance * self._calculate_risk_parameters(conditions)['final_risk']
        
        # Volatillik asosida stop loss
        estimated_volatility = 0.02  # 2%
        stop_loss_distance = estimated_volatility * 2  # 2x volatillik
        
        position_size = risk_amount / stop_loss_distance
        
        return {
            'base_position_size': position_size,
            'max_position_size': position_size * 3,
            'risk_amount': risk_amount,
            'stop_loss_distance': stop_loss_distance,
            'sector_allocation': self._calculate_sector_allocation(conditions)
        }
    
    def _calculate_sector_allocation(self, conditions: MetalMarketConditions) -> Dict[str, float]:
        """Sektor bo'yicha taqsimot"""
        
        sector_weights = {
            MetalMarketSector.PRECIOUS_METALS: 0.4,
            MetalMarketSector.INDUSTRIAL_METALS: 0.4,
            MetalMarketSector.BASE_METALS: 0.2
        }
        
        # Adjust for market conditions
        if conditions.geopolitical_risk > 0.6:
            sector_weights[MetalMarketSector.PRECIOUS_METALS] *= 1.5
        
        if conditions.industrial_demand > 0.7:
            sector_weights[MetalMarketSector.INDUSTRIAL_METALS] *= 1.3
        
        # Normalize
        total_weight = sum(sector_weights.values())
        return {k: v/total_weight for k, v in sector_weights.items()}
    
    def _calculate_stop_loss(self, conditions: MetalMarketConditions) -> float:
        """Stop loss masofasi"""
        base_distance = 0.03  # 3%
        
        # Volatillik ta'siri
        if conditions.geopolitical_risk > 0.7:
            base_distance *= 1.5
        
        if conditions.economic_uncertainty > 0.6:
            base_distance *= 1.3
        
        return base_distance
    
    def _calculate_take_profit_ratio(self, conditions: MetalMarketConditions) -> float:
        """Take profit ratio"""
        base_ratio = 2.0
        
        # Bullish conditions
        if conditions.supply_demand_ratio < 0.8:
            base_ratio *= 1.2
        
        # Geopolitical tension
        if conditions.geopolitical_risk > 0.6:
            base_ratio *= 0.9  # More conservative
        
        return base_ratio
    
    def _calculate_adaptation_confidence(self, conditions: MetalMarketConditions, 
                                       features: pd.DataFrame) -> float:
        """Moslashish ishonchliligi"""
        
        confidence_factors = []
        
        # Supply/demand clarity
        if 0.7 <= conditions.supply_demand_ratio <= 1.3:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)
        
        # Inventory visibility
        if conditions.inventory_levels > 0:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        # Geopolitical stability
        confidence_factors.append(1.0 - conditions.geopolitical_risk)
        
        # Data quality
        if len(features) > 100:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)
        
        return np.mean(confidence_factors)

class MetalMarketAnalyzer:
    """Metal bozor tahlili"""
    
    def __init__(self):
        self.price_correlations = {}
        self.supply_chain_tracker = {}
        self.economic_indicators = {}
        
    def analyze_metal_sector_rotation(self, metal_data: Dict[MetalType, pd.DataFrame]) -> Dict[str, Any]:
        """Metal sektor rotatsiyasini tahlil qilish"""
        
        if len(metal_data) < 2:
            return {'rotation_signal': 'insufficient_data'}
        
        # Har bir metal uchun performance
        performance = {}
        for metal_type, data in metal_data.items():
            if len(data) > 50:
                returns = (data['close'].iloc[-1] / data['close'].iloc[-50]) - 1
                performance[metal_type] = returns
        
        # Eng yaxshi va eng yomon
        sorted_performance = sorted(performance.items(), key=lambda x: x[1], reverse=True)
        
        best_metal = sorted_performance[0][0] if sorted_performance else None
        worst_metal = sorted_performance[-1][0] if sorted_performance else None
        
        # Rotation signal
        if best_metal and worst_metal:
            performance_gap = sorted_performance[0][1] - sorted_performance[-1][1]
            if performance_gap > 0.05:  # 5% gap
                rotation_signal = 'rotate_out_of_worst'
                strength = performance_gap
            elif performance_gap < -0.05:
                rotation_signal = 'rotate_out_of_best'
                strength = abs(performance_gap)
            else:
                rotation_signal = 'hold'
                strength = 0
        else:
            rotation_signal = 'insufficient_data'
            strength = 0
        
        return {
            'rotation_signal': rotation_signal,
            'strength': strength,
            'best_performer': best_metal,
            'worst_performer': worst_metal,
            'performance_ranking': sorted_performance,
            'sector_sentiment': self._calculate_sector_sentiment(performance)
        }
    
    def _calculate_sector_sentiment(self, performance: Dict[MetalType, float]) -> str:
        """Sektor kayfiyati"""
        if not performance:
            return 'neutral'
        
        avg_performance = np.mean(list(performance.values()))
        
        if avg_performance > 0.03:
            return 'bullish'
        elif avg_performance < -0.03:
            return 'bearish'
        else:
            return 'neutral'
    
    def analyze_supply_demand_dynamics(self, data: pd.DataFrame, 
                                     conditions: MetalMarketConditions) -> Dict[str, Any]:
        """Taklif va talab dinamikasini tahlil qilish"""
        
        # Volume trend analysis
        if 'volume' in data.columns:
            volume_trend = data['volume'].rolling(window=20).mean()
            recent_volume = data['volume'].iloc[-1]
            avg_volume = volume_trend.iloc[-1]
            
            volume_signal = 'increasing' if recent_volume > avg_volume * 1.2 else 'decreasing' if recent_volume < avg_volume * 0.8 else 'stable'
        else:
            volume_signal = 'no_data'
        
        # Price momentum
        price_changes = data['close'].pct_change(20)
        momentum = 'strong_up' if price_changes.iloc[-1] > 0.05 else 'strong_down' if price_changes.iloc[-1] < -0.05 else 'moderate'
        
        # Supply/demand pressure
        if conditions.supply_demand_ratio > 1.1:
            pressure = 'supply_pressure'
        elif conditions.supply_demand_ratio < 0.9:
            pressure = 'demand_pressure'
        else:
            pressure = 'balanced'
        
        return {
            'volume_signal': volume_signal,
            'momentum': momentum,
            'pressure': pressure,
            'inventory_impact': conditions.inventory_levels,
            'industrial_demand': conditions.industrial_demand,
            'investment_demand': conditions.investment_demand,
            'supply_demand_balance': conditions.supply_demand_ratio,
            'forward_looking_pressure': self._project_pressure(conditions)
        }
    
    def _project_pressure(self, conditions: MetalMarketConditions) -> str:
        """Kutilayotgan bosim"""
        
        # Simplified projection
        demand_growth = conditions.industrial_demand + conditions.investment_demand
        supply_growth = conditions.mine_production
        
        if demand_growth > supply_growth * 1.1:
            return 'increasing_demand_pressure'
        elif supply_growth > demand_growth * 1.1:
            return 'increasing_supply_pressure'
        else:
            return 'balanced_pressure'

# Metal backtest engine
class MetalBacktestEngine:
    """Metal backtest dvijki"""
    
    def __init__(self, adaptation_engine: MetalAdaptationEngine):
        self.adaptation_engine = adaptation_engine
        self.market_analyzer = MetalMarketAnalyzer()
        
    def run_metal_backtest(self, data: pd.DataFrame, 
                          metal_type: MetalType,
                          start_date: datetime,
                          end_date: datetime) -> Dict[str, Any]:
        
        results = {
            'trades': [],
            'performance': {},
            'adaptation_history': [],
            'sector_analysis': {}
        }
        
        # Backtest logic
        for date in pd.date_range(start_date, end_date):
            if date not in data.index:
                continue
                
            current_data = data.loc[:date]
            
            # Market conditions
            conditions = self._create_market_conditions(current_data, metal_type, date)
            
            # Adaptation
            adaptation_result = self.adaptation_engine.adapt_to_market_conditions(current_data, conditions)
            
            # Signal generation
            signal = self._generate_metal_signal(adaptation_result)
            
            if signal['action'] != 'hold':
                trade = {
                    'date': date,
                    'metal_type': metal_type,
                    'action': signal['action'],
                    'price': current_data['close'].iloc[-1],
                    'size': signal['size'],
                    'stop_loss': signal.get('stop_loss'),
                    'take_profit': signal.get('take_profit'),
                    'confidence': adaptation_result['confidence_score']
                }
                results['trades'].append(trade)
        
        # Performance metrics
        results['performance'] = self._calculate_metal_performance(results['trades'])
        results['sector_analysis'] = self.market_analyzer.analyze_metal_sector_rotation({metal_type: data})
        
        return results
    
    def _create_market_conditions(self, data: pd.DataFrame, 
                                metal_type: MetalType,
                                date: datetime) -> MetalMarketConditions:
        """Metal market conditions yaratish"""
        
        # Sector determination
        if metal_type in [MetalType.GOLD, MetalType.SILVER, MetalType.PLATINUM]:
            sector = MetalMarketSector.PRECIOUS_METALS
        elif metal_type in [MetalType.COPPER, MetalType.ALUMINUM]:
            sector = MetalMarketSector.INDUSTRIAL_METALS
        else:
            sector = MetalMarketSector.BASE_METALS
        
        # Supply/demand ratio
        supply_demand_ratio = np.random.uniform(0.8, 1.2)
        
        # Market event (simplified)
        event_types = list(MarketEventType)
        market_event = event_types[int(date.month % len(event_types))]
        
        return MetalMarketConditions(
            metal_type=metal_type,
            sector=sector,
            market_event=market_event,
            supply_demand_ratio=supply_demand_ratio,
            inventory_levels=np.random.uniform(0.5, 1.0),
            mine_production=np.random.uniform(0.9, 1.1),
            central_bank_holdings=np.random.uniform(0.1, 0.8),
            inflation_hedge_demand=np.random.uniform(0.2, 0.8),
            industrial_demand=np.random.uniform(0.3, 0.9),
            jewelry_demand=np.random.uniform(0.2, 0.7),
            investment_demand=np.random.uniform(0.1, 0.6),
            geopolitical_risk=np.random.uniform(0.0, 0.5),
            usd_strength=np.random.uniform(0.95, 1.05),
            real_interest_rates=np.random.uniform(-0.01, 0.05),
            economic_uncertainty=np.random.uniform(0.1, 0.6)
        )
    
    def _generate_metal_signal(self, adaptation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Metal signal generatsiya"""
        
        features = adaptation_result['features']
        params = adaptation_result['parameters']
        
        if len(features) < 20:
            return {'action': 'hold', 'size': 0}
        
        # Simple signal logic
        current_price = features['close'].iloc[-1]
        ma_trend = features['ma_50'].iloc[-1] if 'ma_50' in features.columns else current_price
        
        signal_strength = 0
        
        # Trend signal
        if current_price > ma_trend:
            signal_strength += 0.5
        else:
            signal_strength -= 0.5
        
        # Momentum confirmation
        if 'momentum_1w' in features.columns:
            if features['momentum_1w'].iloc[-1] > 0.02:
                signal_strength += 0.3
            elif features['momentum_1w'].iloc[-1] < -0.02:
                signal_strength -= 0.3
        
        if abs(signal_strength) > 0.4:
            action = 'buy' if signal_strength > 0 else 'sell'
            size = params['position_sizing']['base_position_size'] * abs(signal_strength)
            
            return {
                'action': action,
                'size': size,
                'confidence': adaptation_result['confidence_score'],
                'stop_loss': current_price * (1 - params['stop_loss_distance']),
                'take_profit': current_price * (1 + params['take_profit_ratio'] * params['stop_loss_distance'])
            }
        
        return {'action': 'hold', 'size': 0}
    
    def _calculate_metal_performance(self, trades: List[Dict]) -> Dict[str, Any]:
        """Metal performance hisoblash"""
        
        if not trades:
            return {'total_return': 0, 'win_rate': 0}
        
        # Simplified PnL
        pnl_values = [(np.random.random() - 0.45) * 2000 for _ in trades]
        
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
            'max_drawdown': min(pnl_values) if pnl_values else 0
        }

# Metal Strategy
class MetalStrategy:
    """Metal trading strategiyasi"""
    
    def __init__(self):
        self.adaptation_engine = MetalAdaptationEngine()
        self.backtest_engine = MetalBacktestEngine(self.adaptation_engine)
    
    def create_metal_strategy(self, metal_type: MetalType, 
                            portfolio_allocation: float = 0.1) -> Dict[str, Any]:
        """Metal strategiyasi yaratish"""
        
        strategy_config = {
            'metal_type': metal_type,
            'portfolio_allocation': portfolio_allocation,
            'adaptation_frequency': 'weekly',
            'risk_management': {
                'max_risk_per_trade': 0.03,
                'max_metal_allocation': 0.15,
                'sector_correlation_limit': 0.7,
                'stop_loss_volatility_adjustment': True
            },
            'sector_rotation': {
                'enable_rotation': True,
                'rebalance_frequency': 'monthly',
                'relative_strength_lookback': 60
            },
            'supply_demand_trading': {
                'enable_supply_demand_signals': True,
                'inventory_level_weight': 0.3,
                'industrial_demand_weight': 0.4
            },
            'hedging': {
                'enable_inflation_hedge': True,
                'geopolitical_hedge_weight': 0.2,
                'currency_hedge_weight': 0.1
            }
        }
        
        return strategy_config

# Demo va test
if __name__ == "__main__":
    # Metal adaptation testi
    metal_engine = MetalAdaptationEngine()
    
    # Demo gold data
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='1D')
    np.random.seed(42)
    
    # Gold price simulation (trend with volatility)
    trend = np.linspace(1800, 2000, len(dates))
    noise = np.random.randn(len(dates)) * 20
    gold_prices = trend + noise
    
    gold_data = pd.DataFrame({
        'open': gold_prices + np.random.randn(len(dates)) * 5,
        'high': gold_prices + np.abs(np.random.randn(len(dates)) * 10),
        'low': gold_prices - np.abs(np.random.randn(len(dates)) * 10),
        'close': gold_prices,
        'volume': np.random.randint(50000, 200000, len(dates))
    }, index=dates)
    
    # Market conditions
    conditions = MetalMarketConditions(
        metal_type=MetalType.GOLD,
        sector=MetalMarketSector.PRECIOUS_METALS,
        market_event=MarketEventType.INFLATION_DATA,
        supply_demand_ratio=0.9,
        inventory_levels=0.6,
        mine_production=1.0,
        central_bank_holdings=0.3,
        inflation_hedge_demand=0.8,
        industrial_demand=0.2,
        jewelry_demand=0.6,
        investment_demand=0.7,
        geopolitical_risk=0.4,
        usd_strength=1.02,
        real_interest_rates=0.02,
        economic_uncertainty=0.5
    )
    
    # Adaptation
    result = metal_engine.adapt_to_market_conditions(gold_data.tail(100), conditions)
    
    print("=== METAL ADAPTATION RESULT ===")
    print(f"Metal Type: {conditions.metal_type.value}")
    print(f"Sector: {conditions.sector.value}")
    print(f"Market Event: {conditions.market_event.value}")
    print(f"Confidence Score: {result['confidence_score']:.3f}")
    print(f"Position Size: {result['parameters']['position_sizing']['base_position_size']:.2f}")
    print(f"Risk Level: {result['parameters']['final_risk']:.4f}")
    print(f"Stop Loss Distance: {result['parameters']['stop_loss_distance']:.4f}")
    
    # Strategy creation
    strategy = MetalStrategy()
    strategy_config = strategy.create_metal_strategy(MetalType.GOLD, 0.12)
    
    print(f"\n=== METAL STRATEGY CREATED ===")
    print(f"Portfolio Allocation: {strategy_config['portfolio_allocation']}")
    print(f"Risk Management: {strategy_config['risk_management']}")
    print(f"Sector Rotation: {strategy_config['sector_rotation']['enable_rotation']}")