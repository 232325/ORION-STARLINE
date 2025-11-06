"""
Arbitrage Detection Module
Arbitrage imkoniyatlarini aniqlash moduli
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timezone, timedelta
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import itertools
from dataclasses import dataclass

from ..utils.data_models import MarketData, ArbitrageOpportunity, ArbitrageCalculation, ArbitrageType
from ..config.config import config, CURRENCY_PAIRS

logger = logging.getLogger(__name__)

@dataclass
class ArbitragePattern:
    """Arbitrage pattern definition"""
    pattern_type: ArbitrageType
    currency_sequence: List[str]
    required_pairs: List[str]
    profit_formula: str
    risk_level: float
    execution_complexity: int  # 1-5 scale

class ArbitrageDetector:
    """
    Arbitrage Detection Engine
    Arbitrage imkoniyatlarini aniqlash va tahlil qilish
    """
    
    def __init__(self, arbitrage_config):
        self.config = arbitrage_config
        self.detection_history = []
        self.opportunity_cache = {}
        self.pattern_matcher = ArbitragePatternMatcher()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Detection parameters
        self.min_profit_threshold = config.arbitrage_config.min_profit_threshold
        self.max_execution_time = config.arbitrage_config.max_execution_time
        self.risk_limit = config.arbitrage_config.risk_limit
        
        # Real-time detection settings
        self.detection_interval = 0.1  # 100ms
        self.max_opportunities_per_cycle = 20
        self.confidence_threshold = 0.7
        
        # Pattern definitions
        self._initialize_arbitrage_patterns()
        
        logger.info("Arbitrage Detector initialized")
    
    def _initialize_arbitrage_patterns(self):
        """Arbitrage pattern definitions"""
        self.arbitrage_patterns = [
            # Triangular arbitrage patterns
            ArbitragePattern(
                pattern_type=ArbitrageType.TRIANGULAR,
                currency_sequence=['EUR', 'USD', 'JPY'],
                required_pairs=['EURUSD', 'USDJPY', 'EURJPY'],
                profit_formula='EURUSD * USDJPY - EURJPY',
                risk_level=0.4,
                execution_complexity=3
            ),
            ArbitragePattern(
                pattern_type=ArbitrageType.TRIANGULAR,
                currency_sequence=['GBP', 'USD', 'CHF'],
                required_pairs=['GBPUSD', 'USDCHF', 'GBPCHF'],
                profit_formula='GBPUSD * USDCHF - GBPCHF',
                risk_level=0.5,
                execution_complexity=3
            ),
            ArbitragePattern(
                pattern_type=ArbitrageType.TRIANGULAR,
                currency_sequence=['AUD', 'USD', 'JPY'],
                required_pairs=['AUDUSD', 'USDJPY', 'AUDJPY'],
                profit_formula='AUDUSD * USDJPY - AUDJPY',
                risk_level=0.6,
                execution_complexity=3
            ),
            
            # Cross-currency patterns
            ArbitragePattern(
                pattern_type=ArbitrageType.CROSS_CURRENCY,
                currency_sequence=['EUR', 'GBP'],
                required_pairs=['EURGBP'],
                profit_formula='direct_rate - implied_rate',
                risk_level=0.3,
                execution_complexity=1
            ),
            ArbitragePattern(
                pattern_type=ArbitrageType.CROSS_CURRENCY,
                currency_sequence=['EUR', 'CHF'],
                required_pairs=['EURCHF'],
                profit_formula='direct_rate - implied_rate',
                risk_level=0.3,
                execution_complexity=1
            ),
            
            # Time-zone arbitrage patterns
            ArbitragePattern(
                pattern_type=ArbitrageType.TIME_ZONE,
                currency_sequence=['EUR', 'USD'],
                required_pairs=['EURUSD'],
                profit_formula='session_overlap_profit',
                risk_level=0.4,
                execution_complexity=2
            ),
            
            # Quantum correlation patterns
            ArbitragePattern(
                pattern_type=ArbitrageType.CORRELATION,
                currency_sequence=['EUR', 'USD', 'GBP', 'USD'],
                required_pairs=['EURUSD', 'GBPUSD'],
                profit_formula='correlation_divergence_profit',
                risk_level=0.6,
                execution_complexity=4
            ),
            ArbitragePattern(
                pattern_type=ArbitrageType.CORRELATION,
                currency_sequence=['AUD', 'USD', 'NZD', 'USD'],
                required_pairs=['AUDUSD', 'NZDUSD'],
                profit_formula='correlation_divergence_profit',
                risk_level=0.5,
                execution_complexity=4
            )
        ]
    
    def detect_opportunities(self, market_data: MarketData, quantum_features: Optional[Dict[str, Any]] = None) -> List[ArbitrageOpportunity]:
        """Real-time arbitrage opportunity detection"""
        try:
            start_time = datetime.now(timezone.utc)
            
            opportunities = []
            
            # 1. Pattern-based detection
            pattern_opportunities = self._detect_pattern_based_opportunities(market_data, quantum_features)
            opportunities.extend(pattern_opportunities)
            
            # 2. Statistical arbitrage detection
            statistical_opportunities = self._detect_statistical_arbitrage(market_data, quantum_features)
            opportunities.extend(statistical_opportunities)
            
            # 3. Quantum-enhanced detection
            if quantum_features:
                quantum_opportunities = self._detect_quantum_enhanced_opportunities(market_data, quantum_features)
                opportunities.extend(quantum_opportunities)
            
            # 4. Time-zone based detection
            timezone_opportunities = self._detect_timezone_opportunities(market_data)
            opportunities.extend(timezone_opportunities)
            
            # 5. Real-time opportunity filtering and ranking
            filtered_opportunities = self._filter_and_rank_opportunities(opportunities, market_data)
            
            # 6. Risk validation
            validated_opportunities = self._validate_opportunities(filtered_opportunities, market_data)
            
            # Cache results
            self._cache_detection_results(start_time, validated_opportunities)
            
            logger.info(f"Detected {len(validated_opportunities)} arbitrage opportunities")
            return validated_opportunities[:self.max_opportunities_per_cycle]
            
        except Exception as e:
            logger.error(f"Arbitrage detection failed: {e}")
            return []
    
    def _detect_pattern_based_opportunities(self, market_data: MarketData, quantum_features: Optional[Dict[str, Any]] = None) -> List[ArbitrageOpportunity]:
        """Pattern-based arbitrage detection"""
        opportunities = []
        
        for pattern in self.arbitrage_patterns:
            pattern_opportunities = self._match_pattern(market_data, pattern, quantum_features)
            opportunities.extend(pattern_opportunities)
        
        return opportunities
    
    def _match_pattern(self, market_data: MarketData, pattern: ArbitragePattern, quantum_features: Optional[Dict[str, Any]] = None) -> List[ArbitrageOpportunity]:
        """Pattern matching for arbitrage opportunities"""
        opportunities = []
        
        try:
            # Check if all required pairs are available
            if not all(pair in market_data.prices for pair in pattern.required_pairs):
                return opportunities
            
            if pattern.pattern_type == ArbitrageType.TRIANGULAR:
                opportunities = self._detect_triangular_pattern(market_data, pattern, quantum_features)
            elif pattern.pattern_type == ArbitrageType.CROSS_CURRENCY:
                opportunities = self._detect_cross_currency_pattern(market_data, pattern, quantum_features)
            elif pattern.pattern_type == ArbitrageType.CORRELATION:
                opportunities = self._detect_correlation_pattern(market_data, pattern, quantum_features)
            elif pattern.pattern_type == ArbitrageType.TIME_ZONE:
                opportunities = self._detect_timezone_pattern(market_data, pattern, quantum_features)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Pattern matching failed for {pattern.pattern_type}: {e}")
            return []
    
    def _detect_triangular_pattern(self, market_data: MarketData, pattern: ArbitragePattern, quantum_features: Optional[Dict[str, Any]] = None) -> List[ArbitrageOpportunity]:
        """Triangular arbitrage pattern detection"""
        opportunities = []
        
        try:
            pair1, pair2, pair3 = pattern.required_pairs
            
            # Get rates
            rate1 = market_data.prices[pair1].mid_price
            rate2 = market_data.prices[pair2].mid_price
            rate3 = market_data.prices[pair3].mid_price
            
            # Calculate triangular arbitrage
            implied_rate = rate1 * rate2
            direct_rate = rate3
            
            # Calculate profit potential
            arbitrage_spread = abs(implied_rate - direct_rate)
            profit_potential_pct = (arbitrage_spread / direct_rate) * 100
            
            # Apply quantum enhancement if available
            quantum_multiplier = 1.0
            if quantum_features:
                correlation_strength = quantum_features.get('correlation_analysis', {}).get('entanglement_strength', 0)
                volatility_superposition = quantum_features.get('volatility_analysis', {}).get('superposition_coherence', 0)
                
                # Quantum enhancement factors
                quantum_multiplier += correlation_strength * 0.2
                quantum_multiplier += volatility_superposition * 0.15
            
            enhanced_profit_potential = profit_potential_pct * quantum_multiplier
            
            # Check minimum threshold
            if enhanced_profit_potential >= self.min_profit_threshold:
                # Risk assessment
                execution_risk = self._assess_triangular_execution_risk(market_data, pattern.required_pairs)
                market_risk = self._assess_triangular_market_risk(market_data, pattern.required_pairs)
                overall_risk = (execution_risk + market_risk) / 2.0
                
                # Time window estimation
                time_window = self._estimate_triangular_time_window(pattern.required_pairs, quantum_features)
                
                opportunity = ArbitrageOpportunity(
                    arbitrage_type=ArbitrageType.TRIANGULAR,
                    currencies=pattern.currency_sequence,
                    pairs=pattern.required_pairs,
                    rates={
                        'pair1_rate': rate1,
                        'pair2_rate': rate2,
                        'direct_rate': rate3,
                        'implied_rate': implied_rate
                    },
                    calculations=ArbitrageCalculation(
                        direct_rate=direct_rate,
                        cross_rate=implied_rate,
                        arbitrage_spread=arbitrage_spread,
                        profit_potential=enhanced_profit_potential,
                        risk_score=overall_risk,
                        time_sensitivity=self._calculate_time_sensitivity(quantum_features),
                        market_depth=self._calculate_market_depth(market_data, pattern.required_pairs)
                    ),
                    risk_level=overall_risk,
                    required_capital=100000,  # $100k default
                    execution_time_estimate=0.5,  # 500ms
                    time_window=time_window,
                    volatility_score=self._calculate_volatility_score(market_data, pattern.required_pairs)
                )
                
                opportunities.append(opportunity)
        
        except Exception as e:
            logger.error(f"Triangular pattern detection failed: {e}")
        
        return opportunities
    
    def _detect_cross_currency_pattern(self, market_data: MarketData, pattern: ArbitragePattern, quantum_features: Optional[Dict[str, Any]] = None) -> List[ArbitrageOpportunity]:
        """Cross-currency arbitrage pattern detection"""
        opportunities = []
        
        try:
            pair = pattern.required_pairs[0]
            
            if pair in market_data.prices:
                direct_rate = market_data.prices[pair].mid_price
                
                # Calculate implied rate through USD
                base_currency = pair[:3]
                quote_currency = pair[3:]
                
                implied_rate = self._calculate_implied_rate_through_usd(market_data, base_currency, quote_currency)
                
                if implied_rate:
                    arbitrage_spread = abs(direct_rate - implied_rate)
                    profit_potential_pct = (arbitrage_spread / direct_rate) * 100
                    
                    if profit_potential_pct >= self.min_profit_threshold:
                        opportunity = ArbitrageOpportunity(
                            arbitrage_type=ArbitrageType.CROSS_CURRENCY,
                            currencies=pattern.currency_sequence,
                            pairs=[pair],
                            rates={
                                'direct_rate': direct_rate,
                                'implied_rate': implied_rate,
                                'arbitrage_spread': arbitrage_spread
                            },
                            calculations=ArbitrageCalculation(
                                direct_rate=direct_rate,
                                cross_rate=implied_rate,
                                arbitrage_spread=arbitrage_spread,
                                profit_potential=profit_potential_pct,
                                risk_score=0.3,  # Lower risk for cross-currency
                                time_sensitivity=0.6,
                                market_depth=market_data.volume.get(pair, 1000000)
                            )
                        )
                        opportunities.append(opportunity)
        
        except Exception as e:
            logger.error(f"Cross-currency pattern detection failed: {e}")
        
        return opportunities
    
    def _detect_correlation_pattern(self, market_data: MarketData, pattern: ArbitragePattern, quantum_features: Optional[Dict[str, Any]] = None) -> List[ArbitrageOpportunity]:
        """Correlation-based arbitrage pattern detection"""
        opportunities = []
        
        try:
            if not quantum_features:
                return opportunities
            
            correlation_strength = quantum_features.get('correlation_analysis', {}).get('entanglement_strength', 0)
            
            if correlation_strength > 0.6:  # Strong correlation detected
                pairs = pattern.required_pairs
                
                if len(pairs) == 2:
                    pair1, pair2 = pairs
                    
                    if pair1 in market_data.prices and pair2 in market_data.prices:
                        rate1 = market_data.prices[pair1].mid_price
                        rate2 = market_data.prices[pair2].mid_price
                        
                        # Calculate correlation divergence
                        expected_rate_ratio = self._calculate_expected_rate_ratio(market_data, pair1, pair2)
                        actual_rate_ratio = rate1 / rate2
                        
                        divergence = abs(actual_rate_ratio - expected_rate_ratio) / expected_rate_ratio
                        profit_potential_pct = divergence * 100
                        
                        if profit_potential_pct >= self.min_profit_threshold:
                            opportunity = ArbitrageOpportunity(
                                arbitrage_type=ArbitrageType.CORRELATION,
                                currencies=pattern.currency_sequence,
                                pairs=[pair1, pair2],
                                rates={
                                    'pair1_rate': rate1,
                                    'pair2_rate': rate2,
                                    'expected_ratio': expected_rate_ratio,
                                    'actual_ratio': actual_rate_ratio
                                },
                                calculations=ArbitrageCalculation(
                                    direct_rate=rate1,
                                    cross_rate=rate2,
                                    arbitrage_spread=divergence,
                                    profit_potential=profit_potential_pct,
                                    risk_score=1.0 - correlation_strength,  # Lower risk with higher correlation
                                    time_sensitivity=0.8,
                                    market_depth=min(market_data.volume.get(pair1, 0), market_data.volume.get(pair2, 0))
                                )
                            )
                            opportunities.append(opportunity)
        
        except Exception as e:
            logger.error(f"Correlation pattern detection failed: {e}")
        
        return opportunities
    
    def _detect_timezone_pattern(self, market_data: MarketData, pattern: ArbitragePattern, quantum_features: Optional[Dict[str, Any]] = None) -> List[ArbitrageOpportunity]:
        """Time-zone arbitrage pattern detection"""
        opportunities = []
        
        try:
            current_session = self._detect_market_session()
            session_overlaps = self._get_active_session_overlaps(current_session)
            
            for overlap in session_overlaps:
                if overlap['duration'] > 0:  # Active overlap
                    profit_potential = overlap.get('profit_potential', 0.001)
                    
                    if profit_potential >= self.min_profit_threshold:
                        opportunity = ArbitrageOpportunity(
                            arbitrage_type=ArbitrageType.TIME_ZONE,
                            currencies=pattern.currency_sequence,
                            pairs=overlap['pairs'],
                            rates=overlap['rates'],
                            calculations=ArbitrageCalculation(
                                direct_rate=1.0,  # Placeholder
                                cross_rate=1.001,
                                arbitrage_spread=profit_potential,
                                profit_potential=profit_potential * 100,
                                risk_score=0.4,
                                time_sensitivity=0.9,  # Very time-sensitive
                                market_depth=1000000  # Assumed high liquidity
                            ),
                            time_window=overlap['duration'],
                            required_capital=50000  # Lower capital requirement for timezone arbitrage
                        )
                        opportunities.append(opportunity)
        
        except Exception as e:
            logger.error(f"Timezone pattern detection failed: {e}")
        
        return opportunities
    
    def _detect_statistical_arbitrage(self, market_data: MarketData, quantum_features: Optional[Dict[str, Any]] = None) -> List[ArbitrageOpportunity]:
        """Statistical arbitrage detection"""
        opportunities = []
        
        try:
            # Z-score based opportunities
            z_score_opportunities = self._detect_z_score_opportunities(market_data)
            opportunities.extend(z_score_opportunities)
            
            # Mean reversion opportunities
            mean_reversion_opportunities = self._detect_mean_reversion_opportunities(market_data)
            opportunities.extend(mean_reversion_opportunities)
            
            # Volatility arbitrage opportunities
            volatility_opportunities = self._detect_volatility_arbitrage_opportunities(market_data, quantum_features)
            opportunities.extend(volatility_opportunities)
            
        except Exception as e:
            logger.error(f"Statistical arbitrage detection failed: {e}")
        
        return opportunities
    
    def _detect_z_score_opportunities(self, market_data: MarketData) -> List[ArbitrageOpportunity]:
        """Z-score based arbitrage detection"""
        opportunities = []
        
        # Calculate price deviations from recent mean
        for pair, price in market_data.prices.items():
            # Simulate z-score calculation (would use historical data in practice)
            volatility = market_data.volatility.get(pair, 0.01)
            
            # Simple z-score based on volatility
            z_score = abs(np.random.normal(0, 1))  # Random for demo
            
            if z_score > 2.0:  # Significant deviation
                profit_potential = z_score * 0.001  # Convert to profit percentage
                
                if profit_potential >= self.min_profit_threshold:
                    opportunity = ArbitrageOpportunity(
                        arbitrage_type=ArbitrageType.CORRELATION,  # Use existing enum
                        currencies=[pair[:3], pair[3:]],
                        pairs=[pair],
                        rates={'current_rate': price.mid_price, 'z_score': z_score},
                        calculations=ArbitrageCalculation(
                            direct_rate=price.mid_price,
                            cross_rate=price.mid_price,
                            arbitrage_spread=z_score * 0.001,
                            profit_potential=profit_potential * 100,
                            risk_score=0.6,  # Medium-high risk for statistical arbitrage
                            time_sensitivity=0.7,
                            market_depth=market_data.volume.get(pair, 1000000)
                        )
                    )
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_mean_reversion_opportunities(self, market_data: MarketData) -> List[ArbitrageOpportunity]:
        """Mean reversion arbitrage detection"""
        opportunities = []
        
        # Detect prices significantly deviated from expected levels
        for pair, price in market_data.prices.items():
            # Simulate mean reversion signal
            deviation = np.random.normal(0, 0.002)  # Random deviation
            
            if abs(deviation) > 0.001:  # Significant deviation
                profit_potential = abs(deviation) * 50  # Scale to percentage
                
                if profit_potential >= self.min_profit_threshold:
                    opportunity = ArbitrageOpportunity(
                        arbitrage_type=ArbitrageType.CORRELATION,
                        currencies=[pair[:3], pair[3:]],
                        pairs=[pair],
                        rates={'current_rate': price.mid_price, 'deviation': deviation},
                        calculations=ArbitrageCalculation(
                            direct_rate=price.mid_price,
                            cross_rate=price.mid_price * (1 + deviation),
                            arbitrage_spread=abs(deviation),
                            profit_potential=profit_potential,
                            risk_score=0.5,
                            time_sensitivity=0.6,
                            market_depth=market_data.volume.get(pair, 1000000)
                        )
                    )
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_volatility_arbitrage_opportunities(self, market_data: MarketData, quantum_features: Optional[Dict[str, Any]] = None) -> List[ArbitrageOpportunity]:
        """Volatility arbitrage opportunities"""
        opportunities = []
        
        volatility_superposition = 0
        if quantum_features:
            volatility_superposition = quantum_features.get('volatility_analysis', {}).get('superposition_coherence', 0)
        
        # Detect volatility clustering opportunities
        for pair, volatility in market_data.volatility.items():
            if volatility > 0.02:  # High volatility
                # Volatility arbitrage profit potential
                profit_potential = volatility * 20  # Scale to percentage
                
                if profit_potential >= self.min_profit_threshold:
                    opportunity = ArbitrageOpportunity(
                        arbitrage_type=ArbitrageType.VOLATILITY,
                        currencies=[pair[:3], pair[3:]],
                        pairs=[pair],
                        rates={'current_volatility': volatility},
                        calculations=ArbitrageCalculation(
                            direct_rate=market_data.prices[pair].mid_price,
                            cross_rate=market_data.prices[pair].mid_price,
                            arbitrage_spread=volatility,
                            profit_potential=profit_potential,
                            risk_score=volatility * 10,  # Higher volatility = higher risk
                            time_sensitivity=0.8,
                            market_depth=market_data.volume.get(pair, 1000000)
                        ),
                        volatility_score=volatility
                    )
                    
                    # Apply quantum volatility superposition enhancement
                    if quantum_features:
                        quantum_factor = 1 + volatility_superposition * 0.3
                        opportunity.calculations.profit_potential *= quantum_factor
                    
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_quantum_enhanced_opportunities(self, market_data: MarketData, quantum_features: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Quantum-enhanced arbitrage opportunities"""
        opportunities = []
        
        try:
            # Quantum coherence opportunities
            coherence_opportunities = self._detect_quantum_coherence_opportunities(market_data, quantum_features)
            opportunities.extend(coherence_opportunities)
            
            # Quantum entanglement opportunities
            entanglement_opportunities = self._detect_quantum_entanglement_opportunities(market_data, quantum_features)
            opportunities.extend(entanglement_opportunities)
            
            # Quantum state opportunities
            quantum_state_opportunities = self._detect_quantum_state_opportunities(market_data, quantum_features)
            opportunities.extend(quantum_state_opportunities)
            
        except Exception as e:
            logger.error(f"Quantum-enhanced detection failed: {e}")
        
        return opportunities
    
    def _detect_quantum_coherence_opportunities(self, market_data: MarketData, quantum_features: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Quantum coherence-based opportunities"""
        opportunities = []
        
        coherence_score = quantum_features.get('quantum_coherence', {}).get('reliability_score', 0)
        
        if coherence_score > 0.8:  # High coherence
            # Coherent market conditions favor certain strategies
            for pair, price in market_data.prices.items():
                # Coherence-enhanced mean reversion
                if price.effective_spread_pct < 0.05:  # Tight spreads
                    profit_potential = coherence_score * 0.002 * 100
                    
                    if profit_potential >= self.min_profit_threshold:
                        opportunity = ArbitrageOpportunity(
                            arbitrage_type=ArbitrageType.CORRELATION,
                            currencies=[pair[:3], pair[3:]],
                            pairs=[pair],
                            rates={'coherence_enhanced_rate': price.mid_price},
                            calculations=ArbitrageCalculation(
                                direct_rate=price.mid_price,
                                cross_rate=price.mid_price,
                                arbitrage_spread=0.0001,
                                profit_potential=profit_potential,
                                risk_score=1.0 - coherence_score * 0.5,  # Lower risk with higher coherence
                                time_sensitivity=coherence_score,
                                market_depth=market_data.volume.get(pair, 1000000)
                            )
                        )
                        opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_quantum_entanglement_opportunities(self, market_data: MarketData, quantum_features: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Quantum entanglement-based opportunities"""
        opportunities = []
        
        correlation_entanglement = quantum_features.get('correlation_analysis', {}).get('entanglement_strength', 0)
        momentum_entanglement = quantum_features.get('momentum_analysis', {}).get('entanglement_strength', 0)
        
        if correlation_entanglement > 0.7:  # Strong correlation entanglement
            # Find correlated pairs for quantum correlation arbitrage
            correlated_pairs = self._find_correlated_pairs(market_data, 0.8)
            
            for pair1, pair2, correlation in correlated_pairs:
                profit_potential = correlation_entanglement * momentum_entanglement * 0.005 * 100
                
                if profit_potential >= self.min_profit_threshold:
                    opportunity = ArbitrageOpportunity(
                        arbitrage_type=ArbitrageType.CORRELATION,
                        currencies=[pair1[:3], pair1[3:], pair2[:3], pair2[3:]],
                        pairs=[pair1, pair2],
                        rates={
                            'pair1_rate': market_data.prices[pair1].mid_price,
                            'pair2_rate': market_data.prices[pair2].mid_price,
                            'quantum_correlation': correlation
                        },
                        calculations=ArbitrageCalculation(
                            direct_rate=market_data.prices[pair1].mid_price,
                            cross_rate=market_data.prices[pair2].mid_price,
                            arbitrage_spread=abs(market_data.prices[pair1].mid_price - market_data.prices[pair2].mid_price),
                            profit_potential=profit_potential,
                            risk_score=1.0 - correlation_entanglement,
                            time_sensitivity=momentum_entanglement,
                            market_depth=min(market_data.volume.get(pair1, 0), market_data.volume.get(pair2, 0))
                        )
                    )
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_quantum_state_opportunities(self, market_data: MarketData, quantum_features: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Quantum state-based opportunities"""
        opportunities = []
        
        market_quantum_state = quantum_features.get('market_quantum_state', {})
        
        if market_quantum_state:
            # Analyze quantum state coherence across currency pairs
            for pair, state_data in market_quantum_state.items():
                coherence = state_data.get('coherence', 0)
                amplitude = state_data.get('amplitude', 0)
                
                if coherence > 0.8 and amplitude > 0.1:
                    # High coherence + significant amplitude indicates strong signal
                    profit_potential = coherence * amplitude * 0.003 * 100
                    
                    if profit_potential >= self.min_profit_threshold:
                        opportunity = ArbitrageOpportunity(
                            arbitrage_type=ArbitrageType.CORRELATION,
                            currencies=[pair[:3], pair[3:]],
                            pairs=[pair],
                            rates={
                                'quantum_state_rate': market_data.prices[pair].mid_price,
                                'quantum_coherence': coherence,
                                'quantum_amplitude': amplitude
                            },
                            calculations=ArbitrageCalculation(
                                direct_rate=market_data.prices[pair].mid_price,
                                cross_rate=market_data.prices[pair].mid_price,
                                arbitrage_spread=amplitude * 0.001,
                                profit_potential=profit_potential,
                                risk_score=1.0 - coherence,
                                time_sensitivity=coherence,
                                market_depth=market_data.volume.get(pair, 1000000)
                            )
                        )
                        opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_timezone_opportunities(self, market_data: MarketData) -> List[ArbitrageOpportunity]:
        """Time-zone specific opportunities"""
        opportunities = []
        
        try:
            current_utc = datetime.now(timezone.utc)
            current_hour = current_utc.hour
            
            # Market session overlaps
            if self._is_london_newyork_overlap(current_hour):
                opportunities.extend(self._detect_london_ny_overlap_opportunities(market_data))
            
            if self._is_tokyo_london_overlap(current_hour):
                opportunities.extend(self._detect_tokyo_london_overlap_opportunities(market_data))
            
            if self._is_asia_us_overlap(current_hour):
                opportunities.extend(self._detect_asia_us_overlap_opportunities(market_data))
            
        except Exception as e:
            logger.error(f"Timezone opportunity detection failed: {e}")
        
        return opportunities
    
    def _is_london_newyork_overlap(self, hour: int) -> bool:
        """London-New York session overlap"""
        return 13 <= hour <= 17  # 13:00-17:00 UTC
    
    def _is_tokyo_london_overlap(self, hour: int) -> bool:
        """Tokyo-London session overlap"""
        return 8 <= hour <= 9  # 08:00-09:00 UTC
    
    def _is_asia_us_overlap(self, hour: int) -> bool:
        """Asia-US session overlap"""
        return 21 <= hour or hour <= 1  # 21:00-01:00 UTC
    
    def _detect_london_ny_overlap_opportunities(self, market_data: MarketData) -> List[ArbitrageOpportunity]:
        """London-New York overlap opportunities"""
        opportunities = []
        
        # High liquidity opportunities during overlap
        major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF']
        
        for pair in major_pairs:
            if pair in market_data.prices:
                # Overlap period: higher profit potential
                profit_potential = 0.0015  # 0.15%
                
                opportunity = ArbitrageOpportunity(
                    arbitrage_type=ArbitrageType.TIME_ZONE,
                    currencies=[pair[:3], pair[3:]],
                    pairs=[pair],
                    rates={'overlap_rate': market_data.prices[pair].mid_price},
                    calculations=ArbitrageCalculation(
                        direct_rate=market_data.prices[pair].mid_price,
                        cross_rate=market_data.prices[pair].mid_price,
                        arbitrage_spread=profit_potential,
                        profit_potential=profit_potential * 100,
                        risk_score=0.3,  # Lower risk during overlap
                        time_sensitivity=0.8,
                        market_depth=market_data.volume.get(pair, 2000000)  # Higher during overlap
                    ),
                    time_window=14400  # 4 hours overlap
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_tokyo_london_overlap_opportunities(self, market_data: MarketData) -> List[ArbitrageOpportunity]:
        """Tokyo-London overlap opportunities"""
        opportunities = []
        
        # JPY and cross pairs more active
        jpy_pairs = ['USDJPY', 'EURJPY', 'GBPJPY']
        
        for pair in jpy_pairs:
            if pair in market_data.prices:
                profit_potential = 0.001  # 0.1%
                
                opportunity = ArbitrageOpportunity(
                    arbitrage_type=ArbitrageType.TIME_ZONE,
                    currencies=[pair[:3], pair[3:]],
                    pairs=[pair],
                    rates={'overlap_rate': market_data.prices[pair].mid_price},
                    calculations=ArbitrageCalculation(
                        direct_rate=market_data.prices[pair].mid_price,
                        cross_rate=market_data.prices[pair].mid_price,
                        arbitrage_spread=profit_potential,
                        profit_potential=profit_potential * 100,
                        risk_score=0.4,
                        time_sensitivity=0.7,
                        market_depth=market_data.volume.get(pair, 1500000)
                    ),
                    time_window=3600  # 1 hour overlap
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_asia_us_overlap_opportunities(self, market_data: MarketData) -> List[ArbitrageOpportunity]:
        """Asia-US overlap opportunities"""
        opportunities = []
        
        # AUD, NZD, and JPY pairs
        asia_us_pairs = ['AUDUSD', 'NZDUSD', 'USDJPY']
        
        for pair in asia_us_pairs:
            if pair in market_data.prices:
                profit_potential = 0.0008  # 0.08%
                
                opportunity = ArbitrageOpportunity(
                    arbitrage_type=ArbitrageType.TIME_ZONE,
                    currencies=[pair[:3], pair[3:]],
                    pairs=[pair],
                    rates={'overlap_rate': market_data.prices[pair].mid_price},
                    calculations=ArbitrageCalculation(
                        direct_rate=market_data.prices[pair].mid_price,
                        cross_rate=market_data.prices[pair].mid_price,
                        arbitrage_spread=profit_potential,
                        profit_potential=profit_potential * 100,
                        risk_score=0.5,
                        time_sensitivity=0.6,
                        market_depth=market_data.volume.get(pair, 1200000)
                    ),
                    time_window=18000  # 5 hours overlap (21:00-01:00)
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def _filter_and_rank_opportunities(self, opportunities: List[ArbitrageOpportunity], market_data: MarketData) -> List[ArbitrageOpportunity]:
        """Filter and rank opportunities"""
        try:
            # Filter by minimum profit threshold
            filtered = [op for op in opportunities if op.calculations and op.calculations.profit_potential >= self.min_profit_threshold]
            
            # Filter by risk limit
            filtered = [op for op in filtered if op.risk_level <= self.risk_limit]
            
            # Calculate composite scores
            scored_opportunities = []
            for op in filtered:
                score = self._calculate_opportunity_score(op, market_data)
                op.composite_score = score
                scored_opportunities.append(op)
            
            # Sort by score
            scored_opportunities.sort(key=lambda x: getattr(x, 'composite_score', 0), reverse=True)
            
            return scored_opportunities
            
        except Exception as e:
            logger.error(f"Opportunity filtering and ranking failed: {e}")
            return opportunities
    
    def _calculate_opportunity_score(self, opportunity: ArbitrageOpportunity, market_data: MarketData) -> float:
        """Calculate composite opportunity score"""
        if not opportunity.calculations:
            return 0.0
        
        score = 0.0
        
        # Profit potential (40% weight)
        profit_score = opportunity.calculations.profit_potential * 40
        score += profit_score
        
        # Risk-adjusted return (30% weight)
        if opportunity.calculations.risk_score > 0:
            risk_adjusted_return = opportunity.calculations.profit_potential / opportunity.calculations.risk_score
            risk_score = risk_adjusted_return * 30
            score += risk_score
        
        # Time sensitivity bonus (15% weight)
        time_score = opportunity.calculations.time_sensitivity * 15
        score += time_score
        
        # Market depth bonus (15% weight)
        depth_score = min(1.0, opportunity.calculations.market_depth / 1000000) * 15
        score += depth_score
        
        return score
    
    def _validate_opportunities(self, opportunities: List[ArbitrageOpportunity], market_data: MarketData) -> List[ArbitrageOpportunity]:
        """Validate opportunities"""
        validated = []
        
        for opportunity in opportunities:
            if self._validate_single_opportunity(opportunity, market_data):
                validated.append(opportunity)
        
        return validated
    
    def _validate_single_opportunity(self, opportunity: ArbitrageOpportunity, market_data: MarketData) -> bool:
        """Validate single opportunity"""
        try:
            # Check if all required pairs exist
            for pair in opportunity.pairs:
                if pair not in market_data.prices:
                    return False
            
            # Check rate validity
            for pair in opportunity.pairs:
                price = market_data.prices[pair]
                if price.bid <= 0 or price.ask <= 0 or price.ask <= price.bid:
                    return False
            
            # Check calculations validity
            if opportunity.calculations:
                if (opportunity.calculations.profit_potential <= 0 or 
                    opportunity.calculations.risk_score < 0 or 
                    opportunity.calculations.risk_score > 1):
                    return False
            
            # Check time constraints
            if opportunity.execution_time_estimate > self.max_execution_time:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Opportunity validation failed: {e}")
            return False
    
    def _cache_detection_results(self, timestamp: datetime, opportunities: List[ArbitrageOpportunity]):
        """Cache detection results"""
        with self._lock:
            self.detection_history.append({
                'timestamp': timestamp,
                'opportunity_count': len(opportunities),
                'opportunities': opportunities
            })
            
            # Keep only recent history
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
            self.detection_history = [
                entry for entry in self.detection_history 
                if entry['timestamp'] > cutoff
            ]
    
    def _detect_market_session(self) -> str:
        """Detect current market session"""
        current_utc = datetime.now(timezone.utc)
        current_hour = current_utc.hour
        
        if 21 <= current_hour or current_hour < 6:
            return 'Sydney'
        elif 0 <= current_hour < 9:
            return 'Tokyo'
        elif 8 <= current_hour < 17:
            return 'London'
        elif 13 <= current_hour < 22:
            return 'New_York'
        else:
            return 'Weekend'
    
    def _get_active_session_overlaps(self, current_session: str) -> List[Dict[str, Any]]:
        """Get active session overlaps"""
        overlaps = []
        current_hour = datetime.now(timezone.utc).hour
        
        # London-New York overlap
        if 13 <= current_hour <= 17:
            overlaps.append({
                'name': 'London-New York',
                'pairs': ['EURUSD', 'GBPUSD', 'USDJPY'],
                'profit_potential': 0.0015,
                'duration': (17 - current_hour) * 3600  # Remaining seconds
            })
        
        # Tokyo-London overlap
        if 8 <= current_hour <= 9:
            overlaps.append({
                'name': 'Tokyo-London',
                'pairs': ['USDJPY', 'EURJPY'],
                'profit_potential': 0.001,
                'duration': (9 - current_hour) * 3600
            })
        
        return overlaps
    
    def _calculate_implied_rate_through_usd(self, market_data: MarketData, base: str, quote: str) -> Optional[float]:
        """Calculate implied rate through USD"""
        try:
            base_usd = f"{base}USD"
            usd_quote = f"USD{quote}"
            
            if base_usd in market_data.prices and usd_quote in market_data.prices:
                base_rate = market_data.prices[base_usd].mid_price
                quote_rate = market_data.prices[usd_quote].mid_price
                return base_rate * quote_rate
            
            # Try reverse
            quote_usd = f"{quote}USD"
            usd_base = f"USD{base}"
            
            if quote_usd in market_data.prices and usd_base in market_data.prices:
                quote_rate = market_data.prices[quote_usd].mid_price
                base_rate = market_data.prices[usd_base].mid_price
                return 1.0 / (quote_rate * base_rate)
            
            return None
            
        except Exception as e:
            logger.error(f"Implied rate calculation failed: {e}")
            return None
    
    def _calculate_expected_rate_ratio(self, market_data: MarketData, pair1: str, pair2: str) -> float:
        """Calculate expected rate ratio between two pairs"""
        # For correlated pairs, calculate historical ratio
        # This is simplified - would use actual historical data in practice
        
        if pair1 in market_data.prices and pair2 in market_data.prices:
            rate1 = market_data.prices[pair1].mid_price
            rate2 = market_data.prices[pair2].mid_price
            return rate1 / rate2
        
        return 1.0
    
    def _find_correlated_pairs(self, market_data: MarketData, min_correlation: float) -> List[Tuple[str, str, float]]:
        """Find correlated pairs"""
        pairs = list(market_data.prices.keys())
        correlated = []
        
        for i, pair1 in enumerate(pairs):
            for j, pair2 in enumerate(pairs[i+1:], i+1):
                correlation = self._calculate_pairs_correlation(market_data, pair1, pair2)
                if correlation > min_correlation:
                    correlated.append((pair1, pair2, correlation))
        
        return correlated
    
    def _calculate_pairs_correlation(self, market_data: MarketData, pair1: str, pair2: str) -> float:
        """Calculate correlation between two pairs"""
        # Simplified correlation calculation
        try:
            # Check for shared currencies
            curr1_set = {pair1[:3], pair1[3:]}
            curr2_set = {pair2[:3], pair2[3:]}
            shared = len(curr1_set.intersection(curr2_set))
            
            # Base correlation on shared currencies
            if shared == 2:  # Same pair
                return 1.0
            elif shared == 1:  # Common currency
                return 0.7
            else:  # No shared currencies
                # Check for economic correlation
                major_currencies = {'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD'}
                if (any(curr in curr1_set for curr in major_currencies) and 
                    any(curr in curr2_set for curr in major_currencies)):
                    return 0.5
                else:
                    return 0.2
            
        except Exception:
            return 0.0
    
    def _assess_triangular_execution_risk(self, market_data: MarketData, pairs: List[str]) -> float:
        """Assess triangular execution risk"""
        risk_score = 0.0
        
        # Execution complexity
        risk_score += len(pairs) * 0.2
        
        # Spread-based risk
        for pair in pairs:
            if pair in market_data.prices:
                spread_pct = market_data.prices[pair].effective_spread_pct
                risk_score += spread_pct * 2
        
        return min(1.0, risk_score)
    
    def _assess_triangular_market_risk(self, market_data: MarketData, pairs: List[str]) -> float:
        """Assess triangular market risk"""
        risk_score = 0.0
        
        # Volatility risk
        for pair in pairs:
            if pair in market_data.volatility:
                volatility = market_data.volatility[pair]
                risk_score += volatility * 5
        
        # Liquidity risk
        for pair in pairs:
            if pair in market_data.volume:
                volume = market_data.volume.get(pair, 0)
                if volume < 500000:
                    risk_score += 0.3
        
        return min(1.0, risk_score)
    
    def _estimate_triangular_time_window(self, pairs: List[str], quantum_features: Optional[Dict[str, Any]] = None) -> float:
        """Estimate triangular arbitrage time window"""
        base_time = len(pairs) * 0.2  # 200ms per leg
        
        if quantum_features:
            coherence = quantum_features.get('quantum_coherence', {}).get('reliability_score', 0.8)
            base_time *= (2.0 - coherence)  # Higher coherence = faster execution
        
        return base_time
    
    def _calculate_time_sensitivity(self, quantum_features: Optional[Dict[str, Any]] = None) -> float:
        """Calculate time sensitivity score"""
        base_sensitivity = 0.6
        
        if quantum_features:
            momentum = quantum_features.get('momentum_analysis', {}).get('entanglement_strength', 0)
            coherence = quantum_features.get('quantum_coherence', {}).get('reliability_score', 0.8)
            
            base_sensitivity += momentum * 0.3
            base_sensitivity *= coherence
        
        return min(1.0, base_sensitivity)
    
    def _calculate_market_depth(self, market_data: MarketData, pairs: List[str]) -> float:
        """Calculate market depth"""
        depths = []
        
        for pair in pairs:
            volume = market_data.volume.get(pair, 1000000)
            depths.append(volume)
        
        return min(depths) if depths else 1000000
    
    def _calculate_volatility_score(self, market_data: MarketData, pairs: List[str]) -> float:
        """Calculate volatility score"""
        volatilities = []
        
        for pair in pairs:
            vol = market_data.volatility.get(pair, 0.01)
            volatilities.append(vol)
        
        return np.mean(volatilities) if volatilities else 0.01


class ArbitragePatternMatcher:
    """Pattern matching utilities"""
    
    def __init__(self):
        self.compiled_patterns = {}
    
    def match_pattern(self, market_data: MarketData, pattern: ArbitragePattern) -> bool:
        """Check if pattern matches current market conditions"""
        # Simplified pattern matching
        return all(pair in market_data.prices for pair in pattern.required_pairs)