"""
Classical Postprocessing Module
Quantum natijalarni qayta ishlash
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone, timedelta
import logging
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

from ..utils.data_models import MarketData, QuantumFeatures, ArbitrageOpportunity, ArbitrageCalculation
from ..config.config import config, CURRENCY_PAIRS

logger = logging.getLogger(__name__)

class ClassicalPostprocessor:
    """
    Classical Postprocessing Engine
    Quantum natijalarni qayta ishlash
    """
    
    def __init__(self, arbitrage_config):
        self.config = arbitrage_config
        self.processing_history = []
        self.opportunity_cache = {}
        self.performance_tracker = {}
        self.risk_calculator = RiskCalculator()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Processing parameters
        self.correlation_threshold = 0.3
        self.volatility_threshold = 0.02
        self.momentum_threshold = 0.01
        
        # Optimization settings
        self.max_opportunities = 50
        self.min_confidence_score = 0.6
        
        logger.info("Classical Postprocessor initialized")
    
    def process_quantum_results(self, market_data: MarketData, quantum_features: QuantumFeatures) -> Dict[str, Any]:
        """Quantum results processing"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Postprocessing pipeline
            results = {}
            
            # 1. Quantum feature interpretation
            interpreted_features = self._interpret_quantum_features(quantum_features)
            results['features'] = interpreted_features
            
            # 2. Arbitrage opportunity generation
            opportunities = self._generate_arbitrage_opportunities(market_data, interpreted_features)
            results['opportunities'] = opportunities
            
            # 3. Risk assessment
            risk_assessments = self._assess_arbitrage_risk(opportunities, market_data)
            results['risk_assessments'] = risk_assessments
            
            # 4. Optimization
            optimized_opportunities = self._optimize_opportunities(opportunities, risk_assessments)
            results['optimized_opportunities'] = optimized_opportunities
            
            # 5. Performance metrics
            metrics = self._calculate_processing_metrics(start_time, len(opportunities), len(optimized_opportunities))
            results['metrics'] = metrics
            
            # Cache results
            self._cache_results(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Quantum results processing failed: {e}")
            return {'error': str(e), 'opportunities': []}
    
    def _interpret_quantum_features(self, quantum_features: QuantumFeatures) -> Dict[str, Any]:
        """Quantum features interpretation"""
        try:
            interpretation = {
                'correlation_analysis': {
                    'entanglement_strength': quantum_features.correlation_entanglement,
                    'interpretation': self._interpret_correlation_entanglement(quantum_features.correlation_entanglement),
                    'confidence': self._calculate_confidence_score('correlation', quantum_features.correlation_entanglement)
                },
                'volatility_analysis': {
                    'superposition_coherence': quantum_features.volatility_superposition,
                    'interpretation': self._interpret_volatility_superposition(quantum_features.volatility_superposition),
                    'confidence': self._calculate_confidence_score('volatility', quantum_features.volatility_superposition)
                },
                'momentum_analysis': {
                    'entanglement_strength': quantum_features.momentum_entanglement,
                    'interpretation': self._interpret_momentum_entanglement(quantum_features.momentum_entanglement),
                    'confidence': self._calculate_confidence_score('momentum', quantum_features.momentum_entanglement)
                },
                'quantum_coherence': {
                    'coherence_time': quantum_features.coherence_time,
                    'error_rate': quantum_features.error_rate,
                    'reliability_score': self._calculate_reliability_score(quantum_features)
                },
                'market_quantum_state': self._interpret_market_quantum_state(quantum_features.market_quantum_state)
            }
            
            return interpretation
            
        except Exception as e:
            logger.error(f"Quantum features interpretation failed: {e}")
            return {}
    
    def _interpret_correlation_entanglement(self, entanglement: float) -> str:
        """Correlation entanglement interpretation"""
        if entanglement > 0.8:
            return "Strong market correlations detected - high potential for correlation arbitrage"
        elif entanglement > 0.6:
            return "Moderate market correlations - good opportunity for correlation trades"
        elif entanglement > 0.4:
            return "Weak correlations present - limited arbitrage potential"
        else:
            return "Minimal market correlations - poor arbitrage conditions"
    
    def _interpret_volatility_superposition(self, superposition: float) -> str:
        """Volatility superposition interpretation"""
        if superposition > 0.8:
            return "High volatility superposition - increased profit potential with higher risk"
        elif superposition > 0.6:
            return "Moderate volatility superposition - balanced risk-reward opportunities"
        elif superposition > 0.4:
            return "Low volatility superposition - stable but limited profit potential"
        else:
            return "Minimal volatility superposition - very stable market conditions"
    
    def _interpret_momentum_entanglement(self, momentum: float) -> str:
        """Momentum entanglement interpretation"""
        if momentum > 0.8:
            return "Strong momentum entanglement - clear directional movement expected"
        elif momentum > 0.6:
            return "Moderate momentum entanglement - directional bias present"
        elif momentum > 0.4:
            return "Weak momentum entanglement - uncertain direction"
        else:
            return "No clear momentum - ranging market conditions"
    
    def _interpret_market_quantum_state(self, quantum_state: Dict[str, float]) -> Dict[str, Any]:
        """Market quantum state interpretation"""
        interpretation = {
            'market_coherence': 0.0,
            'price_stability': 0.0,
            'trend_strength': 0.0,
            'recommendations': []
        }
        
        if not quantum_state:
            return interpretation
        
        # Calculate aggregate metrics
        amplitudes = [state['amplitude'] for state in quantum_state.values() if 'amplitude' in state]
        phases = [state['phase'] for state in quantum_state.values() if 'phase' in state]
        coherences = [state['coherence'] for state in quantum_state.values() if 'coherence' in state]
        
        if amplitudes:
            interpretation['market_coherence'] = np.mean(amplitudes)
        
        if phases:
            # Phase coherence indicates price stability
            phase_variance = np.var(phases)
            interpretation['price_stability'] = 1.0 / (1.0 + phase_variance)
        
        if coherences:
            interpretation['trend_strength'] = np.mean(coherences)
        
        # Generate recommendations
        if interpretation['market_coherence'] > 0.7:
            interpretation['recommendations'].append("High market coherence detected - stable trading conditions")
        
        if interpretation['price_stability'] > 0.8:
            interpretation['recommendations'].append("Price stability high - consider mean reversion strategies")
        
        if interpretation['trend_strength'] > 0.7:
            interpretation['recommendations'].append("Strong trends detected - momentum strategies favored")
        
        return interpretation
    
    def _calculate_confidence_score(self, analysis_type: str, value: float) -> float:
        """Confidence score calculation"""
        # Base confidence on quantum coherence
        base_confidence = 0.8
        
        # Adjust based on value strength
        value_factor = min(1.0, abs(value) * 1.5)
        
        confidence = base_confidence * value_factor
        
        # Type-specific adjustments
        if analysis_type == 'correlation':
            confidence *= 0.9  # Correlations can be noisy
        elif analysis_type == 'volatility':
            confidence *= 0.95  # Volatility measurements are more reliable
        elif analysis_type == 'momentum':
            confidence *= 0.85  # Momentum can be volatile
        
        return min(1.0, confidence)
    
    def _calculate_reliability_score(self, quantum_features: QuantumFeatures) -> float:
        """Quantum reliability score"""
        # Base reliability
        reliability = 1.0
        
        # Reduce reliability based on error rate
        reliability *= (1.0 - quantum_features.error_rate)
        
        # Reduce reliability based on coherence time (longer = more reliable)
        coherence_factor = min(1.0, quantum_features.coherence_time / 100.0)
        reliability *= coherence_factor
        
        # Reduce reliability based on low entanglement
        avg_entanglement = (
            quantum_features.correlation_entanglement + 
            quantum_features.momentum_entanglement
        ) / 2.0
        
        entanglement_factor = avg_entanglement
        reliability *= entanglement_factor
        
        return max(0.1, min(1.0, reliability))
    
    def _generate_arbitrage_opportunities(self, market_data: MarketData, quantum_features: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Arbitrage opportunity generation"""
        opportunities = []
        
        try:
            # 1. Triangular arbitrage opportunities
            triangular_ops = self._detect_triangular_arbitrage(market_data, quantum_features)
            opportunities.extend(triangular_ops)
            
            # 2. Cross-currency arbitrage
            cross_currency_ops = self._detect_cross_currency_arbitrage(market_data, quantum_features)
            opportunities.extend(cross_currency_ops)
            
            # 3. Quantum correlation arbitrage
            correlation_ops = self._detect_quantum_correlation_arbitrage(market_data, quantum_features)
            opportunities.extend(correlation_ops)
            
            # 4. Time-zone arbitrage
            timezone_ops = self._detect_timezone_arbitrage(market_data, quantum_features)
            opportunities.extend(timezone_ops)
            
            # 5. Volatility arbitrage
            volatility_ops = self._detect_volatility_arbitrage(market_data, quantum_features)
            opportunities.extend(volatility_ops)
            
            logger.info(f"Generated {len(opportunities)} arbitrage opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Arbitrage opportunity generation failed: {e}")
            return []
    
    def _detect_triangular_arbitrage(self, market_data: MarketData, quantum_features: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Triangular arbitrage detection"""
        opportunities = []
        
        # Common triangular patterns
        triangles = [
            ['EURUSD', 'USDJPY', 'EURJPY'],
            ['GBPUSD', 'USDCHF', 'GBPCHF'],
            ['AUDUSD', 'USDJPY', 'AUDJPY'],
            ['NZDUSD', 'USDCAD', 'NZDCAD']
        ]
        
        for triangle in triangles:
            if all(pair in market_data.prices for pair in triangle):
                profit_potential = self._calculate_triangular_profit(market_data, triangle, quantum_features)
                
                if profit_potential > self.config.min_profit_threshold:
                    opportunity = ArbitrageOpportunity(
                        arbitrage_type=ArbitrageType.TRIANGULAR,
                        currencies=self._extract_currencies_from_pairs(triangle),
                        pairs=triangle,
                        rates={pair: market_data.prices[pair].mid_price for pair in triangle},
                        calculations=profit_potential,
                        max_profit=profit_potential.profit_potential * 100000,  # Assume $100k capital
                        execution_time_estimate=0.5
                    )
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _calculate_triangular_profit(self, market_data: MarketData, triangle: List[str], quantum_features: Dict[str, Any]) -> Optional[ArbitrageCalculation]:
        """Triangular arbitrage profit calculation"""
        try:
            # Get rates
            rate1 = market_data.prices[triangle[0]].mid_price  # EUR/USD
            rate2 = market_data.prices[triangle[1]].mid_price  # USD/JPY
            rate3 = market_data.prices[triangle[2]].mid_price  # EUR/JPY
            
            # Calculate implied rate through triangle
            implied_rate = rate1 * rate2
            direct_rate = rate3
            
            # Calculate arbitrage spread
            arbitrage_spread = abs(implied_rate - direct_rate)
            profit_potential = (arbitrage_spread / direct_rate) * 100  # Percentage
            
            # Risk assessment
            volatility_factor = self._assess_triangular_risk(market_data, triangle)
            risk_score = volatility_factor * (1.0 - quantum_features.get('reliability_score', 0.8))
            
            # Time sensitivity (quantum coherence affects timing)
            time_sensitivity = quantum_features.get('quantum_coherence', {}).get('reliability_score', 0.8)
            time_window = time_sensitivity * 10  # Max 10 seconds
            
            # Market depth estimation
            liquidity_scores = [market_data.volume.get(pair, 1000000) for pair in triangle]
            market_depth = min(liquidity_scores)
            
            return ArbitrageCalculation(
                direct_rate=direct_rate,
                cross_rate=implied_rate,
                arbitrage_spread=arbitrage_spread,
                profit_potential=profit_potential,
                risk_score=risk_score,
                time_sensitivity=time_sensitivity,
                market_depth=market_depth
            )
            
        except Exception as e:
            logger.error(f"Triangular profit calculation failed: {e}")
            return None
    
    def _detect_cross_currency_arbitrage(self, market_data: MarketData, quantum_features: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Cross-currency arbitrage detection"""
        opportunities = []
        
        # Cross-currency pairs analysis
        cross_pairs = ['EURGBP', 'EURJPY', 'GBPCHF', 'AUDCAD', 'AUDJPY']
        
        for pair in cross_pairs:
            if pair in market_data.prices:
                cross_rate = market_data.prices[pair].mid_price
                
                # Calculate implied rate through USD
                implied_rate = self._calculate_implied_cross_rate(market_data, pair)
                
                if implied_rate:
                    profit_potential = abs(cross_rate - implied_rate) / implied_rate * 100
                    
                    if profit_potential > self.config.min_profit_threshold:
                        opportunity = ArbitrageOpportunity(
                            arbitrage_type=ArbitrageType.CROSS_CURRENCY,
                            currencies=CURRENCY_PAIRS.get(pair, {'base': pair[:3], 'quote': pair[3:]}),
                            pairs=[pair],
                            rates={'direct': cross_rate, 'implied': implied_rate},
                            calculations=ArbitrageCalculation(
                                direct_rate=cross_rate,
                                cross_rate=implied_rate,
                                arbitrage_spread=abs(cross_rate - implied_rate),
                                profit_potential=profit_potential,
                                risk_score=0.3  # Medium risk for cross-currency
                            )
                        )
                        opportunities.append(opportunity)
        
        return opportunities
    
    def _calculate_implied_cross_rate(self, market_data: MarketData, cross_pair: str) -> Optional[float]:
        """Implied cross rate calculation"""
        try:
            base = cross_pair[:3]
            quote = cross_pair[3:]
            
            # Try USD-based calculation
            if f"{base}USD" in market_data.prices and f"USD{quote}" in market_data.prices:
                base_usd = market_data.prices[f"{base}USD"].mid_price
                usd_quote = market_data.prices[f"USD{quote}"].mid_price
                return base_usd * usd_quote
            
            # Try reverse calculation
            elif f"{quote}USD" in market_data.prices and f"USD{base}" in market_data.prices:
                quote_usd = market_data.prices[f"{quote}USD"].mid_price
                usd_base = market_data.prices[f"USD{base}"].mid_price
                return 1.0 / (quote_usd * usd_base)
            
            return None
            
        except Exception as e:
            logger.error(f"Implied cross rate calculation failed: {e}")
            return None
    
    def _detect_quantum_correlation_arbitrage(self, market_data: MarketData, quantum_features: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Quantum correlation-based arbitrage"""
        opportunities = []
        
        correlation_strength = quantum_features.get('correlation_analysis', {}).get('entanglement_strength', 0)
        
        if correlation_strength > 0.7:
            # High correlation entanglement detected
            correlated_pairs = self._find_correlated_pairs(market_data, correlation_strength)
            
            for pair1, pair2, correlation in correlated_pairs:
                # Calculate correlation-based profit potential
                profit_potential = correlation * 0.5  # Max 0.5% profit potential
                
                if profit_potential > self.config.min_profit_threshold:
                    opportunity = ArbitrageOpportunity(
                        arbitrage_type=ArbitrageType.CORRELATION,
                        currencies=[pair1[:3], pair1[3:], pair2[:3], pair2[3:]],
                        pairs=[pair1, pair2],
                        rates={pair1: market_data.prices[pair1].mid_price,
                              pair2: market_data.prices[pair2].mid_price},
                        calculations=ArbitrageCalculation(
                            direct_rate=market_data.prices[pair1].mid_price,
                            cross_rate=market_data.prices[pair2].mid_price,
                            arbitrage_spread=abs(market_data.prices[pair1].mid_price - market_data.prices[pair2].mid_price),
                            profit_potential=profit_potential,
                            risk_score=1.0 - correlation  # High correlation = lower risk
                        )
                    )
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _find_correlated_pairs(self, market_data: MarketData, min_correlation: float) -> List[Tuple[str, str, float]]:
        """Find correlated currency pairs"""
        correlated_pairs = []
        pairs = list(market_data.prices.keys())
        
        for i, pair1 in enumerate(pairs):
            for j, pair2 in enumerate(pairs[i+1:], i+1):
                correlation = self._calculate_pairs_correlation(market_data, pair1, pair2)
                if correlation > min_correlation:
                    correlated_pairs.append((pair1, pair2, correlation))
        
        return correlated_pairs
    
    def _calculate_pairs_correlation(self, market_data: MarketData, pair1: str, pair2: str) -> float:
        """Calculate correlation between two pairs"""
        try:
            # Check for shared currencies
            curr1_set = {pair1[:3], pair1[3:]}
            curr2_set = {pair2[:3], pair2[3:]}
            shared_currencies = curr1_set.intersection(curr2_set)
            
            if not shared_currencies:
                return 0.0
            
            # Base correlation for shared currencies
            base_correlation = 0.3
            
            # Volatility correlation
            vol1 = market_data.volatility.get(pair1, 0.01)
            vol2 = market_data.volatility.get(pair2, 0.01)
            
            if vol1 > 0 and vol2 > 0:
                vol_similarity = 1.0 - abs(vol1 - vol2) / max(vol1, vol2)
                base_correlation += vol_similarity * 0.4
            
            # Spread correlation
            spread1 = market_data.prices[pair1].effective_spread_pct
            spread2 = market_data.prices[pair2].effective_spread_pct
            
            if spread1 > 0 and spread2 > 0:
                spread_similarity = 1.0 - abs(spread1 - spread2) / max(spread1, spread2)
                base_correlation += spread_similarity * 0.3
            
            return min(1.0, base_correlation)
            
        except Exception as e:
            logger.error(f"Pair correlation calculation failed: {e}")
            return 0.0
    
    def _detect_timezone_arbitrage(self, market_data: MarketData, quantum_features: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Time-zone arbitrage detection"""
        opportunities = []
        
        # Current market session analysis
        current_session = self._detect_market_session()
        
        # Time-zone arbitrage opportunities based on market overlaps
        session_overlaps = self._calculate_session_overlaps(current_session)
        
        for overlap in session_overlaps:
            if overlap['profit_potential'] > self.config.min_profit_threshold:
                opportunity = ArbitrageOpportunity(
                    arbitrage_type=ArbitrageType.TIME_ZONE,
                    currencies=overlap['currencies'],
                    pairs=overlap['pairs'],
                    rates=overlap['rates'],
                    calculations=ArbitrageCalculation(
                        direct_rate=overlap['direct_rate'],
                        cross_rate=overlap['cross_rate'],
                        arbitrage_spread=overlap['spread'],
                        profit_potential=overlap['profit_potential'],
                        risk_score=0.4,  # Medium risk for timezone arbitrage
                        time_sensitivity=0.9  # Very time-sensitive
                    ),
                    time_window=overlap['time_window']
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_market_session(self) -> str:
        """Detect current market session"""
        current_hour = datetime.now(timezone.utc).hour
        
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
    
    def _calculate_session_overlaps(self, current_session: str) -> List[Dict[str, Any]]:
        """Calculate session overlap opportunities"""
        overlaps = []
        
        # Session overlap windows (UTC hours)
        session_windows = {
            'London_Asia': {'start': 8, 'end': 9, 'pairs': ['EURUSD', 'GBPUSD', 'USDJPY']},
            'London_New_York': {'start': 13, 'end': 17, 'pairs': ['EURUSD', 'GBPUSD', 'USDCHF']},
            'New_York_Asia': {'start': 21, 'end': 22, 'pairs': ['USDCAD', 'AUDUSD', 'NZDUSD']}
        }
        
        current_hour = datetime.now(timezone.utc).hour
        
        for session_name, window in session_windows.items():
            if window['start'] <= current_hour < window['end']:
                # Calculate profit potential for this overlap
                profit_potential = 0.002  # 0.2% average overlap profit
                
                overlaps.append({
                    'session': session_name,
                    'profit_potential': profit_potential,
                    'currencies': ['USD', 'EUR', 'GBP', 'JPY', 'CHF'],
                    'pairs': window['pairs'],
                    'direct_rate': 1.0,  # Placeholder
                    'cross_rate': 1.002,
                    'spread': 0.002,
                    'time_window': 3600  # 1 hour overlap window
                })
        
        return overlaps
    
    def _detect_volatility_arbitrage(self, market_data: MarketData, quantum_features: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Volatility arbitrage detection"""
        opportunities = []
        
        volatility_superposition = quantum_features.get('volatility_analysis', {}).get('superposition_coherence', 0)
        
        if volatility_superposition > 0.6:
            # High volatility superposition detected
            volatile_pairs = self._find_volatile_pairs(market_data, 0.02)  # 2% volatility threshold
            
            for pair, volatility in volatile_pairs:
                # Calculate volatility-based profit potential
                profit_potential = volatility * 10  # Scale volatility to profit potential
                
                if profit_potential > self.config.min_profit_threshold:
                    opportunity = ArbitrageOpportunity(
                        arbitrage_type=ArbitrageType.VOLATILITY,
                        currencies=[pair[:3], pair[3:]],
                        pairs=[pair],
                        rates={'current': market_data.prices[pair].mid_price},
                        calculations=ArbitrageCalculation(
                            direct_rate=market_data.prices[pair].mid_price,
                            cross_rate=market_data.prices[pair].mid_price,
                            arbitrage_spread=volatility * 0.1,
                            profit_potential=profit_potential,
                            risk_score=volatility  # High volatility = high risk
                        ),
                        volatility_score=volatility
                    )
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _find_volatile_pairs(self, market_data: MarketData, min_volatility: float) -> List[Tuple[str, float]]:
        """Find highly volatile pairs"""
        volatile_pairs = []
        
        for pair, volatility in market_data.volatility.items():
            if volatility > min_volatility:
                volatile_pairs.append((pair, volatility))
        
        # Sort by volatility (highest first)
        volatile_pairs.sort(key=lambda x: x[1], reverse=True)
        
        return volatile_pairs[:10]  # Top 10 most volatile pairs
    
    def _assess_triangular_risk(self, market_data: MarketData, triangle: List[str]) -> float:
        """Triangular arbitrage risk assessment"""
        risk_score = 0.0
        
        # Execution risk
        for pair in triangle:
            spread = market_data.prices[pair].effective_spread_pct
            if spread > 0.1:  # High spread
                risk_score += 0.3
        
        # Liquidity risk
        for pair in triangle:
            volume = market_data.volume.get(pair, 0)
            if volume < 100000:  # Low liquidity
                risk_score += 0.4
        
        # Volatility risk
        for pair in triangle:
            volatility = market_data.volatility.get(pair, 0)
            risk_score += volatility * 2
        
        return min(1.0, risk_score)
    
    def _extract_currencies_from_pairs(self, pairs: List[str]) -> List[str]:
        """Extract unique currencies from pairs"""
        currencies = set()
        for pair in pairs:
            currencies.add(pair[:3])
            currencies.add(pair[3:])
        return list(currencies)
    
    def _assess_arbitrage_risk(self, opportunities: List[ArbitrageOpportunity], market_data: MarketData) -> List[Dict[str, Any]]:
        """Risk assessment for arbitrage opportunities"""
        risk_assessments = []
        
        for opportunity in opportunities:
            risk_assessment = self.risk_calculator.assess_opportunity_risk(opportunity, market_data)
            risk_assessments.append({
                'opportunity_id': opportunity.id,
                'risk_assessment': risk_assessment
            })
        
        return risk_assessments
    
    def _optimize_opportunities(self, opportunities: List[ArbitrageOpportunity], risk_assessments: List[Dict[str, Any]]) -> List[ArbitrageOpportunity]:
        """Opportunity optimization"""
        try:
            # Combine opportunities with risk assessments
            enhanced_opportunities = []
            
            for i, opportunity in enumerate(opportunities):
                if i < len(risk_assessments):
                    risk_assessment = risk_assessments[i]['risk_assessment']
                    
                    # Apply quantum-enhanced scoring
                    quantum_score = self._calculate_quantum_score(opportunity, risk_assessment)
                    
                    # Add quantum score to opportunity
                    opportunity.quantum_features = opportunity.quantum_features or {}
                    opportunity.quantum_features['quantum_score'] = quantum_score
                    opportunity.quantum_features['confidence'] = risk_assessment['confidence_score']
                    
                    enhanced_opportunities.append(opportunity)
            
            # Sort by quantum score and risk-adjusted return
            enhanced_opportunities.sort(
                key=lambda op: self._get_opportunity_score(op),
                reverse=True
            )
            
            # Keep top opportunities
            optimized = enhanced_opportunities[:self.max_opportunities]
            
            logger.info(f"Optimized to {len(optimized)} opportunities")
            return optimized
            
        except Exception as e:
            logger.error(f"Opportunity optimization failed: {e}")
            return opportunities
    
    def _calculate_quantum_score(self, opportunity: ArbitrageOpportunity, risk_assessment: Dict[str, Any]) -> float:
        """Quantum score calculation"""
        # Base score from profit potential
        base_score = opportunity.get_expected_return() * 100
        
        # Quantum enhancement factor
        quantum_enhancement = 1.0
        
        if hasattr(opportunity, 'quantum_features') and opportunity.quantum_features:
            correlation_entanglement = opportunity.quantum_features.get('correlation_entanglement', 0)
            volatility_superposition = opportunity.quantum_features.get('volatility_superposition', 0)
            momentum_entanglement = opportunity.quantum_features.get('momentum_entanglement', 0)
            
            # Quantum enhancement based on entanglement
            quantum_enhancement += correlation_entanglement * 0.2
            quantum_enhancement += volatility_superposition * 0.15
            quantum_enhancement += momentum_entanglement * 0.1
        
        # Risk adjustment
        risk_factor = 1.0 - risk_assessment.get('overall_risk_score', 0.5)
        
        # Final quantum score
        quantum_score = base_score * quantum_enhancement * risk_factor
        
        return quantum_score
    
    def _get_opportunity_score(self, opportunity: ArbitrageOpportunity) -> float:
        """Get opportunity score for ranking"""
        if not opportunity.calculations:
            return 0.0
        
        quantum_score = 0.0
        if hasattr(opportunity, 'quantum_features') and opportunity.quantum_features:
            quantum_score = opportunity.quantum_features.get('quantum_score', 0.0)
        
        # Combine quantum score with classical metrics
        return quantum_score + opportunity.calculations.profit_potential
    
    def _calculate_processing_metrics(self, start_time: datetime, opportunities_count: int, optimized_count: int) -> Dict[str, Any]:
        """Processing metrics calculation"""
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return {
            'processing_time': processing_time,
            'total_opportunities_generated': opportunities_count,
            'optimized_opportunities': optimized_count,
            'optimization_ratio': optimized_count / max(opportunities_count, 1),
            'quantum_enhancement_applied': True,
            'risk_assessment_coverage': 100.0
        }
    
    def _cache_results(self, results: Dict[str, Any]):
        """Cache processing results"""
        with self._lock:
            self.processing_history.append({
                'timestamp': datetime.now(timezone.utc),
                'results': results
            })
            
            # Keep only recent history
            cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
            self.processing_history = [
                entry for entry in self.processing_history 
                if entry['timestamp'] > cutoff
            ]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Performance metrics"""
        with self._lock:
            if not self.processing_history:
                return {}
            
            recent_entries = self.processing_history[-10:]  # Last 10 entries
            
            avg_processing_time = np.mean([entry['results']['metrics']['processing_time'] for entry in recent_entries])
            avg_opportunities = np.mean([entry['results']['metrics']['total_opportunities_generated'] for entry in recent_entries])
            avg_optimization_ratio = np.mean([entry['results']['metrics']['optimization_ratio'] for entry in recent_entries])
            
            return {
                'avg_processing_time': avg_processing_time,
                'avg_opportunities_per_cycle': avg_opportunities,
                'avg_optimization_ratio': avg_optimization_ratio,
                'total_cycles': len(self.processing_history)
            }


class RiskCalculator:
    """Risk assessment calculator"""
    
    def assess_opportunity_risk(self, opportunity: ArbitrageOpportunity, market_data: MarketData) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        try:
            risk_factors = []
            
            # Market risk
            market_risk = self._assess_market_risk(opportunity, market_data)
            if market_risk > 0.5:
                risk_factors.append("High market volatility")
            
            # Liquidity risk
            liquidity_risk = self._assess_liquidity_risk(opportunity, market_data)
            if liquidity_risk > 0.6:
                risk_factors.append("Low market liquidity")
            
            # Operational risk
            operational_risk = self._assess_operational_risk(opportunity)
            if operational_risk > 0.7:
                risk_factors.append("Complex execution required")
            
            # Quantum risk (uncertainty in quantum measurements)
            quantum_risk = self._assess_quantum_risk(opportunity)
            if quantum_risk > 0.3:
                risk_factors.append("Quantum measurement uncertainty")
            
            # Overall risk score
            overall_risk = (market_risk + liquidity_risk + operational_risk + quantum_risk) / 4.0
            
            # Confidence score (inverse of risk)
            confidence_score = 1.0 - overall_risk
            
            return {
                'overall_risk_score': overall_risk,
                'market_risk': market_risk,
                'liquidity_risk': liquidity_risk,
                'operational_risk': operational_risk,
                'quantum_risk': quantum_risk,
                'risk_factors': risk_factors,
                'confidence_score': confidence_score,
                'risk_category': self._categorize_risk(overall_risk)
            }
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {
                'overall_risk_score': 0.8,  # High risk on error
                'confidence_score': 0.2,
                'error': str(e)
            }
    
    def _assess_market_risk(self, opportunity: ArbitrageOpportunity, market_data: MarketData) -> float:
        """Market risk assessment"""
        risk_score = 0.0
        
        # Volatility-based risk
        for pair in opportunity.pairs:
            if pair in market_data.volatility:
                volatility = market_data.volatility[pair]
                risk_score += volatility * 2  # High volatility = high risk
        
        # Spread-based risk
        for pair in opportunity.pairs:
            if pair in market_data.prices:
                spread_pct = market_data.prices[pair].effective_spread_pct
                if spread_pct > 0.1:  # High spread
                    risk_score += 0.3
        
        return min(1.0, risk_score / len(opportunity.pairs))
    
    def _assess_liquidity_risk(self, opportunity: ArbitrageOpportunity, market_data: MarketData) -> float:
        """Liquidity risk assessment"""
        min_liquidity = float('inf')
        
        for pair in opportunity.pairs:
            if pair in market_data.volume:
                volume = market_data.volume[pair]
                min_liquidity = min(min_liquidity, volume)
        
        if min_liquidity == float('inf'):
            return 0.5  # Unknown liquidity
        
        # Lower liquidity = higher risk
        if min_liquidity < 100000:
            return 0.8
        elif min_liquidity < 500000:
            return 0.6
        elif min_liquidity < 1000000:
            return 0.4
        else:
            return 0.2
    
    def _assess_operational_risk(self, opportunity: ArbitrageOpportunity) -> float:
        """Operational risk assessment"""
        risk_score = 0.0
        
        # Execution complexity
        if opportunity.arbitrage_type == ArbitrageType.TRIANGULAR:
            risk_score += 0.3  # Complex execution
        elif opportunity.arbitrage_type == ArbitrageType.CROSS_CURRENCY:
            risk_score += 0.2
        else:
            risk_score += 0.1
        
        # Number of pairs (more pairs = higher risk)
        risk_score += len(opportunity.pairs) * 0.1
        
        # Time sensitivity
        if opportunity.time_window < 5:
            risk_score += 0.4  # Very time-sensitive
        elif opportunity.time_window < 30:
            risk_score += 0.2
        
        return min(1.0, risk_score)
    
    def _assess_quantum_risk(self, opportunity: ArbitrageOpportunity) -> float:
        """Quantum risk assessment (measurement uncertainty)"""
        if not hasattr(opportunity, 'quantum_features') or not opportunity.quantum_features:
            return 0.5  # Unknown quantum state
        
        # Base quantum risk
        quantum_risk = 0.3
        
        # Adjust based on quantum scores
        quantum_score = opportunity.quantum_features.get('quantum_score', 0)
        if quantum_score < 0.5:
            quantum_risk += 0.2
        
        # Adjust based on entanglement strength
        correlation_entanglement = opportunity.quantum_features.get('correlation_entanglement', 0)
        if correlation_entanglement < 0.5:
            quantum_risk += 0.2
        
        return min(1.0, quantum_risk)
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Risk category"""
        if risk_score <= 0.3:
            return "LOW"
        elif risk_score <= 0.6:
            return "MEDIUM"
        elif risk_score <= 0.8:
            return "HIGH"
        else:
            return "CRITICAL"