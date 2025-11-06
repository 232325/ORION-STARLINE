"""
Central Bank Module
==================

Markaziy bank qarorlari va e'lonlari tahlili moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import pytz
from ..utils.time_utils import TimeUtils
import warnings
warnings.filterwarnings('ignore')


@dataclass
class CentralBankDecision:
    """Markaziy bank qarori"""
    bank_name: str
    decision_time: datetime
    decision_type: str  # 'rate_change', 'policy_statement', 'speech'
    actual_rate: Optional[float]
    previous_rate: Optional[float]
    forecasted_rate: Optional[float]
    rate_change_bps: float
    hawkish_dovish: str  # 'hawkish', 'dovish', 'neutral'
    market_impact: float
    surprise_factor: float


@dataclass
class CentralBankEvent:
    """Markaziy bank voqeasi"""
    bank_name: str
    event_type: str
    speaker: str
    scheduled_time: datetime
    importance: str  # 'high', 'medium', 'low'
    expected_topics: List[str]
    previous_statements: List[str]


class CentralBankAnalyzer:
    """Markaziy bank tahlil moduli"""
    
    def __init__(self):
        self.central_banks = {
            'Federal Reserve': {
                'name': 'Federal Reserve System',
                'currency': 'USD',
                'timezone': 'America/New_York',
                'meeting_schedule': '8 times per year',
                'rate_decision_time': '18:00 UTC',  # 13:00 EST
                'policy_framework': 'Dual Mandate',
                'recent_stance': 'hawkish',
                'key_officials': [
                    'Jerome Powell (Chair)',
                    'John Williams (Vice Chair)',
                    'Michelle Bowman',
                    'Philip Jefferson'
                ],
                'regular_speeches': [
                    'FOMC Press Conference',
                    'Congressional Testimony',
                    'Economic Symposium'
                ]
            },
            'ECB': {
                'name': 'European Central Bank',
                'currency': 'EUR',
                'timezone': 'Europe/Frankfurt',
                'meeting_schedule': '8 times per year',
                'rate_decision_time': '11:45 UTC',  # 12:45 CET
                'policy_framework': 'Price Stability',
                'recent_stance': 'dovish',
                'key_officials': [
                    'Christine Lagarde (President)',
                    'Luis de Guindos (Vice President)',
                    'Isabel Schnabel',
                    'Philip Lane'
                ],
                'regular_speeches': [
                    'Monetary Policy Statement',
                    'Press Conference',
                    'European Parliament Testimony'
                ]
            },
            'Bank of England': {
                'name': 'Bank of England',
                'currency': 'GBP',
                'timezone': 'Europe/London',
                'meeting_schedule': '8 times per year',
                'rate_decision_time': '11:00 UTC',  # 11:00 GMT
                'policy_framework': 'Inflation Targeting',
                'recent_stance': 'neutral',
                'key_officials': [
                    'Andrew Bailey (Governor)',
                    'Ben Broadbent (Deputy Governor)',
                    'Jon Cunliffe',
                    'Sir Jon Cunliffe'
                ],
                'regular_speeches': [
                    'Monetary Policy Decision',
                    'Inflation Report',
                    'Quarterly Press Conference'
                ]
            },
            'Bank of Japan': {
                'name': 'Bank of Japan',
                'currency': 'JPY',
                'timezone': 'Asia/Tokyo',
                'meeting_schedule': '8 times per year',
                'rate_decision_time': '03:00 UTC',  # 11:00 JST
                'policy_framework': 'Price Stability',
                'recent_stance': 'dovish',
                'key_officials': [
                    'Kazuo Ueda (Governor)',
                    'Shinichi Uchida (Deputy Governor)',
                    'Seiji Adachi',
                    'Yutaka Yamashita'
                ],
                'regular_speeches': [
                    'Monetary Policy Decision',
                    'Statement',
                    'Press Conference'
                ]
            },
            'SNB': {
                'name': 'Swiss National Bank',
                'currency': 'CHF',
                'timezone': 'Europe/Zurich',
                'meeting_schedule': '4 times per year',
                'rate_decision_time': '07:30 UTC',  # 08:30 CET
                'policy_framework': 'Price Stability',
                'recent_stance': 'dovish',
                'key_officials': [
                    'Thomas Jordan (Chairman)',
                    'Fritz Zurbruegg (Vice Chairman)',
                    'Andrea Maechler',
                    'Patrick M. Frost'
                ]
            },
            'Bank of Canada': {
                'name': 'Bank of Canada',
                'currency': 'CAD',
                'timezone': 'America/Toronto',
                'meeting_schedule': '8 times per year',
                'rate_decision_time': '14:00 UTC',  # 09:00 EST
                'policy_framework': 'Inflation Targeting',
                'recent_stance': 'neutral',
                'key_officials': [
                    'Tiff Macklem (Governor)',
                    'Carolyn A. Wilkins (Senior Deputy Governor)',
                    'Sharon Kozicki',
                    'Paul Beaudry'
                ]
            },
            'RBA': {
                'name': 'Reserve Bank of Australia',
                'currency': 'AUD',
                'timezone': 'Australia/Sydney',
                'meeting_schedule': '11 times per year',
                'rate_decision_time': '00:30 UTC',  # 10:30 AEST
                'policy_framework': 'Inflation Targeting',
                'recent_stance': 'neutral',
                'key_officials': [
                    'Philip Lowe (Governor)',
                    'Michele Bullock (Deputy Governor)',
                    'Luci Ellis',
                    'Bradley Jones'
                ]
            }
        }
        
        # Policy stance indicators
        self.policy_indicators = {
            'hawkish': {
                'keywords': [
                    'tightening', 'higher rates', 'restrictive policy', 'inflation concerns',
                    'wage pressures', 'strong economy', 'faster normalization'
                ],
                'market_reaction': 'positive',
                'typical_impact_bps': 50
            },
            'dovish': {
                'keywords': [
                    'accommodative', 'lower rates', 'stimulus', 'supportive policy',
                    'growth concerns', 'easing', 'flexibility'
                ],
                'market_reaction': 'negative',
                'typical_impact_bps': -30
            },
            'neutral': {
                'keywords': [
                    'data dependent', 'monitoring', 'balanced approach', 'current policy appropriate',
                    'gradual', 'dependent on outlook'
                ],
                'market_reaction': 'mixed',
                'typical_impact_bps': 10
            }
        }
    
    def get_upcoming_central_bank_events(self, days_ahead: int = 30) -> List[Dict]:
        """Kelgusi markaziy bank voqealarini olish"""
        current_time = TimeUtils.get_current_utc_time()
        end_time = current_time + timedelta(days=days_ahead)
        
        upcoming_events = []
        
        for bank_name, bank_info in self.central_banks.items():
            # Generate regular meeting schedule (simplified)
            meetings = self._generate_meeting_schedule(bank_name, bank_info, current_time, end_time)
            
            for meeting in meetings:
                upcoming_events.append({
                    'bank_name': bank_name,
                    'bank_currency': bank_info['currency'],
                    'event_type': 'rate_decision',
                    'scheduled_time': meeting,
                    'importance': 'high',
                    'expected_decision': True,
                    'rate_decision_time': bank_info['rate_decision_time']
                })
            
            # Add key speeches
            speeches = self._generate_speech_schedule(bank_name, bank_info, current_time, end_time)
            for speech in speeches:
                upcoming_events.append({
                    'bank_name': bank_name,
                    'bank_currency': bank_info['currency'],
                    'event_type': 'speech',
                    'scheduled_time': speech['time'],
                    'speaker': speech['speaker'],
                    'importance': speech['importance'],
                    'topic': speech['topic'],
                    'expected_decision': False
                })
        
        return upcoming_events
    
    def _generate_meeting_schedule(self, bank_name: str, bank_info: Dict, 
                                 start_time: datetime, end_time: datetime) -> List[datetime]:
        """Bank meeting schedule yaratish"""
        meetings = []
        
        # Meeting frequency (simplified scheduling)
        if bank_info['meeting_schedule'] == '8 times per year':
            # Approximately every 6 weeks
            meeting_interval = timedelta(days=42)
        elif bank_info['meeting_schedule'] == '4 times per year':
            # Every 3 months
            meeting_interval = timedelta(days=90)
        elif bank_info['meeting_schedule'] == '11 times per year':
            # Approximately every 4 weeks
            meeting_interval = timedelta(days=28)
        else:
            meeting_interval = timedelta(days=60)
        
        # Generate meetings
        current = start_time
        while current <= end_time:
            # Schedule for business day (adjust for weekends)
            if current.weekday() < 5:  # Monday to Friday
                meetings.append(current)
            current += meeting_interval
        
        return meetings
    
    def _generate_speech_schedule(self, bank_name: str, bank_info: Dict,
                                start_time: datetime, end_time: datetime) -> List[Dict]:
        """Bank speech schedule yaratish"""
        speeches = []
        
        # Generate regular speeches
        current = start_time
        speech_interval = timedelta(days=14)  # Every 2 weeks
        
        while current <= end_time:
            if current.weekday() < 5 and 'key_officials' in bank_info:
                for official in bank_info['key_officials'][:2]:  # Top 2 officials
                    if current.weekday() == 2:  # Wednesday speeches
                        speeches.append({
                            'time': current + timedelta(hours=9),  # 9 AM
                            'speaker': official,
                            'importance': 'medium',
                            'topic': 'monetary_policy_outlook'
                        })
                        break
            current += speech_interval
        
        return speeches
    
    def analyze_central_bank_communication(self, speech_text: str, 
                                         bank_name: str) -> Dict[str, any]:
        """Markaziy bank kommunikatsiyasini tahlil qilish"""
        bank_info = self.central_banks.get(bank_name, {})
        
        # Sentiment analysis
        sentiment_score = self._analyze_sentiment(speech_text)
        policy_stance = self._classify_policy_stance(speech_text)
        
        # Key themes analysis
        key_themes = self._extract_key_themes(speech_text)
        
        # Rate expectations
        rate_expectations = self._extract_rate_expectations(speech_text)
        
        # Market implications
        market_implications = self._assess_market_implications(
            policy_stance, key_themes, bank_info
        )
        
        return {
            'bank_name': bank_name,
            'sentiment_score': sentiment_score,  # -1 to 1 scale
            'policy_stance': policy_stance,
            'hawkish_dovish_score': self._calculate_hd_score(speech_text),
            'key_themes': key_themes,
            'rate_expectations': rate_expectations,
            'market_implications': market_implications,
            'surprise_potential': self._assess_surprise_potential(speech_text, bank_info),
            'communication_quality': self._assess_communication_quality(speech_text)
        }
    
    def _analyze_sentiment(self, text: str) -> float:
        """Sentiment tahlili (simplified)"""
        # Positive words
        positive_words = [
            'strong', 'robust', 'positive', 'growth', 'improving', 'better',
            'confident', 'optimistic', 'solid', 'healthy'
        ]
        
        # Negative words
        negative_words = [
            'weak', 'concerning', 'negative', 'declining', 'worse', 'worrying',
            'pessimistic', 'uncertain', 'challenging', 'risks'
        ]
        
        # Neutral/inflationary words
        neutral_words = [
            'stable', 'moderate', 'gradual', 'steady', 'balanced', 'measured'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        neutral_count = sum(1 for word in neutral_words if word in text_lower)
        
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words == 0:
            return 0
        
        sentiment = (positive_count - negative_count) / total_sentiment_words
        return max(-1, min(1, sentiment))  # Clamp to -1 to 1
    
    def _classify_policy_stance(self, text: str) -> str:
        """Policy stance klassifikatsiyasi"""
        text_lower = text.lower()
        
        hawkish_score = 0
        dovish_score = 0
        
        for stance, info in self.policy_indicators.items():
            if stance == 'hawkish':
                hawkish_score = sum(1 for keyword in info['keywords'] if keyword in text_lower)
            elif stance == 'dovish':
                dovish_score = sum(1 for keyword in info['keywords'] if keyword in text_lower)
        
        if hawkish_score > dovish_score and hawkish_score > 0:
            return 'hawkish'
        elif dovish_score > hawkish_score and dovish_score > 0:
            return 'dovish'
        else:
            return 'neutral'
    
    def _calculate_hd_score(self, text: str) -> float:
        """Hawkish-Dovish score hisoblash (-100 to 100)"""
        text_lower = text.lower()
        
        hawkish_indicators = [
            'tightening', 'higher', 'restrictive', 'concern', 'strength',
            'vigilant', 'appropriate to tighten', 'accelerate'
        ]
        
        dovish_indicators = [
            'easing', 'lower', 'accommodative', 'support', 'flexible',
            'patient', 'flexibility', 'remain accommodative'
        ]
        
        hawkish_count = sum(1 for word in hawkish_indicators if word in text_lower)
        dovish_count = sum(1 for word in dovish_indicators if word in text_lower)
        
        total_indicators = hawkish_count + dovish_count
        
        if total_indicators == 0:
            return 0
        
        hd_score = (hawkish_count - dovish_count) / total_indicators * 100
        return max(-100, min(100, hd_score))
    
    def _extract_key_themes(self, text: str) -> List[str]:
        """Asosiy mavzularni ajratib olish"""
        themes = []
        
        # Inflation themes
        inflation_keywords = ['inflation', 'price', 'cpi', 'pce', 'deflationary', 'disinflation']
        if any(keyword in text.lower() for keyword in inflation_keywords):
            themes.append('inflation_outlook')
        
        # Growth themes
        growth_keywords = ['growth', 'gdp', 'recession', 'expansion', 'economic activity']
        if any(keyword in text.lower() for keyword in growth_keywords):
            themes.append('growth_outlook')
        
        # Labor market themes
        labor_keywords = ['employment', 'unemployment', 'labor', 'jobs', 'wages', 'payroll']
        if any(keyword in text.lower() for keyword in labor_keywords):
            themes.append('labor_market')
        
        # Financial stability themes
        stability_keywords = ['stability', 'financial', 'credit', 'banking', 'systemic']
        if any(keyword in text.lower() for keyword in stability_keywords):
            themes.append('financial_stability')
        
        # International themes
        intl_keywords = ['international', 'global', 'trade', 'geopolitical', 'china']
        if any(keyword in text.lower() for keyword in intl_keywords):
            themes.append('international_developments')
        
        return themes
    
    def _extract_rate_expectations(self, text: str) -> Dict[str, any]:
        """Rate kutishlarini aniqlash"""
        expectations = {
            'explicit_guidance': False,
            'rate_path_mentioned': False,
            'hike_likelihood': 0.0,
            'cut_likelihood': 0.0,
            'hold_likelihood': 0.0
        }
        
        # Look for explicit rate guidance
        rate_keywords = ['rate', 'rates', 'interest', 'monetary policy']
        guidance_keywords = ['will', 'expect', 'plan', 'appropriate', 'likely']
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in rate_keywords):
            if any(guidance in text_lower for guidance in guidance_keywords):
                expectations['explicit_guidance'] = True
        
        # Rate direction indicators
        hike_indicators = ['increase', 'raise', 'hike', 'tighten', 'higher']
        cut_indicators = ['decrease', 'lower', 'cut', 'reduce', 'ease']
        
        hike_count = sum(1 for indicator in hike_indicators if indicator in text_lower)
        cut_count = sum(1 for indicator in cut_indicators if indicator in text_lower)
        
        total_direction = hike_count + cut_count
        
        if total_direction > 0:
            expectations['hike_likelihood'] = hike_count / total_direction
            expectations['cut_likelihood'] = cut_count / total_direction
            expectations['hold_likelihood'] = max(0, 1 - (hike_count + cut_count) / 10)
        else:
            expectations['hold_likelihood'] = 0.7  # Default to holding
        
        return expectations
    
    def _assess_market_implications(self, policy_stance: str, key_themes: List[str],
                                  bank_info: Dict) -> Dict[str, any]:
        """Bozor ta'sirini baholash"""
        implications = {
            'currency_impact': 'neutral',
            'volatility_expectation': 'medium',
            'trading_recommendation': 'neutral'
        }
        
        # Currency impact based on policy stance
        if policy_stance == 'hawkish':
            implications['currency_impact'] = 'stronger' if bank_info.get('currency') == 'USD' else 'positive'
            implications['volatility_expectation'] = 'high'
            implications['trading_recommendation'] = 'buy'
        elif policy_stance == 'dovish':
            implications['currency_impact'] = 'weaker' if bank_info.get('currency') == 'USD' else 'negative'
            implications['volatility_expectation'] = 'medium'
            implications['trading_recommendation'] = 'sell'
        
        # Theme-based implications
        if 'inflation_outlook' in key_themes:
            implications['volatility_expectation'] = 'high'
            implications['trading_recommendation'] = 'cautious'
        
        if 'financial_stability' in key_themes:
            implications['trading_recommendation'] = 'risk_off'
        
        return implications
    
    def _assess_surprise_potential(self, text: str, bank_info: Dict) -> str:
        """Kutilmaganlik potensialini baholash"""
        surprise_indicators = [
            'unexpected', 'unusual', 'deviation', 'significant change',
            'major shift', 'unprecedented', 'dramatic'
        ]
        
        text_lower = text.lower()
        
        surprise_count = sum(1 for indicator in surprise_indicators if indicator in text_lower)
        
        if surprise_count >= 2:
            return 'high'
        elif surprise_count == 1:
            return 'medium'
        else:
            return 'low'
    
    def _assess_communication_quality(self, text: str) -> str:
        """Kommunikatsiya sifatini baholash"""
        # Quality indicators
        clarity_indicators = [
            'clear', 'transparent', 'explicit', 'direct', 'unequivocal'
        ]
        
        vagueness_indicators = [
            'uncertain', 'unclear', 'confusing', 'ambiguous', 'vague'
        ]
        
        text_lower = text.lower()
        
        clarity_score = sum(1 for indicator in clarity_indicators if indicator in text_lower)
        vagueness_score = sum(1 for indicator in vagueness_indicators if indicator in text_lower)
        
        if clarity_score > vagueness_score and clarity_score >= 2:
            return 'high'
        elif vagueness_score > clarity_score and vagueness_score >= 2:
            return 'low'
        else:
            return 'medium'
    
    def predict_central_bank_reaction(self, upcoming_decision: Dict,
                                    market_data: pd.DataFrame) -> Dict[str, float]:
        """Markaziy bank reaksiyasini bashoratlash"""
        bank_info = self.central_banks.get(upcoming_decision['bank_name'], {})
        
        # Base probability
        base_probabilities = {
            'hike': 0.25,
            'cut': 0.15,
            'hold': 0.60
        }
        
        # Adjust based on economic conditions
        if not market_data.empty:
            # Market-based adjustments
            recent_performance = market_data['close'].tail(20).pct_change().mean()
            volatility = market_data['close'].pct_change().tail(20).std()
            
            # High volatility might favor holding
            if volatility > 0.02:
                base_probabilities['hold'] += 0.1
                base_probabilities['hike'] -= 0.05
                base_probabilities['cut'] -= 0.05
        
        # Policy stance adjustments
        recent_stance = bank_info.get('recent_stance', 'neutral')
        
        if recent_stance == 'hawkish':
            base_probabilities['hike'] += 0.15
            base_probabilities['cut'] -= 0.10
        elif recent_stance == 'dovish':
            base_probabilities['cut'] += 0.10
            base_probabilities['hike'] -= 0.10
        
        # Normalize probabilities
        total_prob = sum(base_probabilities.values())
        normalized_probs = {k: v / total_prob for k, v in base_probabilities.items()}
        
        # Expected rate change
        expected_change = (normalized_probs['hike'] * 25 +  # Typical 25 bps hike
                          normalized_probs['cut'] * -25 +    # Typical 25 bps cut
                          normalized_probs['hold'] * 0) / 25  # No change
        
        return {
            'probability_hike': normalized_probs['hike'],
            'probability_cut': normalized_probs['cut'],
            'probability_hold': normalized_probs['hold'],
            'expected_rate_change_bps': expected_change * 25,
            'market_impact_expectation': abs(expected_change) * 50,  # Estimated impact in bps
            'confidence_level': 0.75 if len(market_data) > 100 else 0.60
        }
    
    def create_central_bank_trading_strategy(self, upcoming_events: List[Dict],
                                           risk_tolerance: str = 'medium') -> Dict[str, any]:
        """Markaziy bank asosida trading strategiyasi"""
        strategy = {
            'trading_approach': '',
            'position_sizing': {},
            'timing': {},
            'risk_management': {},
            'currency_focus': [],
            'avoid_events': []
        }
        
        # Risk-based approach
        if risk_tolerance == 'low':
            strategy['trading_approach'] = 'avoid_cb_events'
            strategy['avoid_events'] = [event['bank_name'] for event in upcoming_events]
        elif risk_tolerance == 'high':
            strategy['trading_approach'] = 'cb_trading'
            strategy['currency_focus'] = [event['bank_currency'] for event in upcoming_events]
        else:
            strategy['trading_approach'] = 'selective_cb'
            strategy['currency_focus'] = ['USD', 'EUR']  # Focus on major currencies
        
        # Position sizing
        position_multipliers = {
            'low': 0.3, 'medium': 0.6, 'high': 1.0
        }
        
        strategy['position_sizing'] = {
            'base_multiplier': position_multipliers[risk_tolerance],
            'pre_event_reduction': 0.5,
            'post_event_wait_hours': 2 if risk_tolerance == 'low' else 1
        }
        
        # Timing strategy
        strategy['timing'] = {
            'pre_event': 'Close positions 1 hour before',
            'during_event': 'Monitor, no new positions',
            'post_event': 'Wait 30-60 minutes for clarity',
            'optimal_entry': 'After volatility settles'
        }
        
        # Risk management
        strategy['risk_management'] = {
            'stop_loss_multiplier': 2.0 if risk_tolerance == 'high' else 1.5,
            'max_risk_per_trade': 0.02,  # 2% of capital
            'correlation_limit': 0.3,    # Max currency correlation
            'news_avoid_minutes': 60 if risk_tolerance == 'low' else 30
        }
        
        return strategy
    
    def analyze_central_bank_divergence(self, events: List[Dict]) -> Dict[str, any]:
        """Markaziy bank divergensiyasini tahlil qilish"""
        # Group events by time windows
        divergence_windows = []
        
        current_time = TimeUtils.get_current_utc_time()
        for i, event in enumerate(events):
            # Find events within 24 hours
            window_events = [event]
            
            for j, other_event in enumerate(events):
                if i != j:
                    time_diff = abs((event['scheduled_time'] - other_event['scheduled_time']).total_seconds())
                    if time_diff <= 86400:  # 24 hours
                        window_events.append(other_event)
            
            if len(window_events) > 1:
                divergence_windows.append({
                    'events': window_events,
                    'time_range': f"{min(e['scheduled_time'] for e in window_events)} - {max(e['scheduled_time'] for e in window_events)}",
                    'banks_involved': list(set(e['bank_name'] for e in window_events)),
                    'currencies_involved': list(set(e.get('bank_currency', '') for e in window_events))
                })
        
        # Analyze divergence implications
        divergence_analysis = []
        
        for window in divergence_windows:
            banks = window['banks_involved']
            currencies = window['currencies_involved']
            
            # Policy divergence assessment
            policy_differences = self._assess_policy_divergence(banks)
            
            divergence_analysis.append({
                'time_window': window['time_range'],
                'central_banks': banks,
                'currencies': currencies,
                'policy_divergence': policy_differences,
                'trading_implications': self._get_divergence_implications(banks, currencies),
                'volatility_expectation': self._estimate_divergence_volatility(banks)
            })
        
        return {
            'divergence_periods': divergence_analysis,
            'high_impact_windows': len([d for d in divergence_analysis if d['policy_divergence']['level'] == 'high']),
            'recommended_approach': self._get_divergence_strategy_recommendation(divergence_analysis)
        }
    
    def _assess_policy_divergence(self, banks: List[str]) -> Dict[str, str]:
        """Policy divergence darajasini baholash"""
        stances = []
        for bank in banks:
            bank_info = self.central_banks.get(bank, {})
            stances.append(bank_info.get('recent_stance', 'neutral'))
        
        # Count stance diversity
        unique_stances = set(stances)
        
        if len(unique_stances) == 1:
            level = 'low'
            description = 'Similar policy stances'
        elif len(unique_stances) == 2:
            if ('hawkish' in unique_stances and 'dovish' in unique_stances):
                level = 'high'
                description = 'Significant divergence between hawkish and dovish stances'
            else:
                level = 'medium'
                description = 'Moderate policy differences'
        else:
            level = 'high'
            description = 'Mixed policy stances across banks'
        
        return {
            'level': level,
            'description': description,
            'stances_involved': stances,
            'trading_complexity': 'high' if level == 'high' else 'medium'
        }
    
    def _get_divergence_implications(self, banks: List[str], currencies: List[str]) -> List[str]:
        """Divergence trading implikatsiyalari"""
        implications = []
        
        # Cross-currency implications
        if 'USD' in currencies and 'EUR' in currencies:
            implications.append('EUR/USD likely to be highly volatile')
        
        if 'GBP' in currencies and 'EUR' in currencies:
            implications.append('EUR/GBP may see directional moves')
        
        # Policy-based implications
        bank_stances = [self.central_banks.get(bank, {}).get('recent_stance', 'neutral') for bank in banks]
        
        if 'hawkish' in bank_stances and 'dovish' in bank_stances:
            implications.append('Currency carry trade unwinding likely')
            implications.append('Risk-on/risk-off sentiment shifts expected')
        
        return implications
    
    def _estimate_divergence_volatility(self, banks: List[str]) -> str:
        """Divergence volatilite taxmini"""
        if len(banks) >= 3:
            return 'very_high'
        elif len(banks) == 2:
            bank1_stance = self.central_banks.get(banks[0], {}).get('recent_stance', 'neutral')
            bank2_stance = self.central_banks.get(banks[1], {}).get('recent_stance', 'neutral')
            
            if bank1_stance != bank2_stance and bank1_stance != 'neutral' and bank2_stance != 'neutral':
                return 'high'
            else:
                return 'medium'
        else:
            return 'low'
    
    def _get_divergence_strategy_recommendation(self, divergence_analysis: List[Dict]) -> str:
        """Divergence strategiyasi tavsiyasi"""
        high_divergence_count = len([d for d in divergence_analysis if d['policy_divergence']['level'] == 'high'])
        
        if high_divergence_count >= 2:
            return 'avoid_trading'  # Too much uncertainty
        elif high_divergence_count == 1:
            return 'reduce_exposure'  # High caution needed
        else:
            return 'selective_trading'  # Some opportunities available