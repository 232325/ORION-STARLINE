"""
News Impact Assessment va Economic Calendar Integration tizimi
GPT-5 powered news classification va multi-asset impact analysis

Asosiy funksiyalar:
- Economic Calendar Integration (FRED API)
- News Impact Analysis
- Event Categories (High/Medium/Low/Black Swan)
- Multi-Asset Impact Mapping
- Prediction Models
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImpactLevel(Enum):
    """Event impact level categories"""
    BLACK_SWAN = "black_swan"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AssetClass(Enum):
    """Supported asset classes"""
    STOCKS = "stocks"
    FOREX = "forex"
    METALS = "metals"
    CRYPTO = "crypto"
    BONDS = "bonds"

@dataclass
class EconomicEvent:
    """Economic event data structure"""
    title: str
    date: datetime
    impact_level: ImpactLevel
    description: str
    previous_value: Optional[float]
    forecast_value: Optional[float]
    actual_value: Optional[float]
    source: str
    asset_impact: Dict[AssetClass, float]  # Impact magnitude per asset class
    volatility_impact: Dict[str, float]  # Expected volatility change
    recovery_time_estimate: Optional[int]  # Hours to recover
    
@dataclass
class NewsItem:
    """News item with impact analysis"""
    headline: str
    content: str
    timestamp: datetime
    source: str
    classification: ImpactLevel
    affected_assets: Dict[str, float]
    sentiment_score: float
    impact_magnitude: float
    time_to_impact: Optional[int]
    recovery_prediction: Optional[int]

@dataclass
class MarketReaction:
    """Predicted market reaction to events"""
    asset_class: AssetClass
    expected_move: float
    volatility_spike: float
    direction: str
    confidence: float
    time_to_max_impact: int
    recovery_time: int

class FREDApiIntegration:
    """FRED API integration for economic data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        
    async def get_indicators(self, series_ids: List[str]) -> Dict[str, Dict]:
        """Get economic indicators from FRED"""
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for series_id in series_ids:
                try:
                    url = f"{self.base_url}/series/observations"
                    params = {
                        'series_id': series_id,
                        'api_key': self.api_key,
                        'file_type': 'json',
                        'limit': 1
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            results[series_id] = data
                        else:
                            logger.warning(f"FRED API error for {series_id}: {response.status}")
                            
                except Exception as e:
                    logger.error(f"Error fetching {series_id}: {e}")
                    
        return results
    
    async def get_release_dates(self, release_ids: List[str]) -> List[Dict]:
        """Get economic release calendar"""
        calendar_events = []
        
        async with aiohttp.ClientSession() as session:
            for release_id in release_ids:
                try:
                    # Get releases for next 30 days
                    end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                    start_date = datetime.now().strftime('%Y-%m-%d')
                    
                    url = f"{self.base_url}/release/dates"
                    params = {
                        'release_id': release_id,
                        'api_key': self.api_key,
                        'file_type': 'json',
                        'limit': 100,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            calendar_events.extend(data.get('release_dates', []))
                            
                except Exception as e:
                    logger.error(f"Error fetching release {release_id}: {e}")
                    
        return calendar_events

class GPT5NewsClassifier:
    """GPT-5 powered news classification system"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.classification_prompts = self._initialize_prompts()
        
    def _initialize_prompts(self) -> Dict[str, str]:
        """Initialize classification prompts"""
        return {
            "impact_classification": """
            Classify this news item's market impact level:
            
            High Impact Events:
            - Federal Reserve meetings and policy decisions
            - GDP reports (quarterly, annual)
            - CPI and PCE inflation data
            - Employment reports (NFP, unemployment rate)
            - Corporate earnings from major companies
            
            Medium Impact Events:
            - PMI reports (manufacturing, services)
            - Retail sales data
            - Housing market reports
            - Consumer confidence
            - Industrial production
            
            Low Impact Events:
            - Minor economic indicators
            - Routine weekly data
            - Technical readings
            
            Black Swan Events:
            - Unexpected major political events
            - Natural disasters affecting markets
            - Pandemic declarations
            - Major geopolitical conflicts
            - Financial system crises
            
            News: {news_text}
            """,
            
            "asset_impact": """
            Analyze which asset classes will be most affected by this news:
            
            For each asset class, provide impact magnitude (-1 to 1):
            - stocks: Stock market impact
            - forex: Currency markets impact  
            - metals: Gold, silver, industrial metals impact
            - crypto: Cryptocurrency impact
            - bonds: Bond market impact
            
            Consider:
            - Direct vs indirect effects
            - Sector-specific impacts
            - Regional market differences
            - Time sensitivity
            
            News: {news_text}
            """,
            
            "volatility_prediction": """
            Predict market volatility changes from this news:
            
            Consider:
            - Historical volatility of similar events
            - Market's prior expectations
            - News shock factor
            - Duration of impact
            
            Provide:
            - Expected volatility spike (0-100%)
            - Time to maximum impact (hours)
            - Recovery time estimate (hours)
            - Direction bias probability
            
            News: {news_text}
            """
        }
    
    async def classify_news(self, news_item: NewsItem) -> NewsItem:
        """Classify news using GPT-5"""
        try:
            # Simulate GPT-5 API call (in real implementation, use OpenAI API)
            classification = await self._simulate_gpt5_classification(news_item)
            
            # Update news item with classification
            news_item.classification = classification['impact_level']
            news_item.affected_assets = classification['asset_impacts']
            news_item.impact_magnitude = classification['impact_magnitude']
            news_item.time_to_impact = classification['time_to_impact']
            news_item.recovery_prediction = classification['recovery_time']
            
        except Exception as e:
            logger.error(f"Error in news classification: {e}")
            # Fallback classification based on keywords
            news_item = self._fallback_classification(news_item)
            
        return news_item
    
    async def _simulate_gpt5_classification(self, news_item: NewsItem) -> Dict:
        """Simulate GPT-5 classification (replace with actual OpenAI API)"""
        # This is a simulation - replace with actual GPT-5 API call
        await asyncio.sleep(0.1)  # Simulate API delay
        
        text = f"{news_item.headline} {news_item.content}"
        
        # Simple keyword-based classification (replace with GPT-5 logic)
        if any(keyword in text.lower() for keyword in ['fed', 'federal reserve', 'interest rate', 'gdp', 'inflation']):
            impact_level = ImpactLevel.HIGH
            impact_magnitude = 0.8
        elif any(keyword in text.lower() for keyword in ['earnings', 'revenue', 'profit']):
            impact_level = ImpactLevel.HIGH
            impact_magnitude = 0.7
        elif any(keyword in text.lower() for keyword in ['pmi', 'retail', 'housing', 'consumer confidence']):
            impact_level = ImpactLevel.MEDIUM
            impact_magnitude = 0.5
        elif any(keyword in text.lower() for keyword in ['unexpected', 'crisis', 'war', 'pandemic']):
            impact_level = ImpactLevel.BLACK_SWAN
            impact_magnitude = 0.9
        else:
            impact_level = ImpactLevel.LOW
            impact_magnitude = 0.3
        
        # Asset impact mapping
        asset_impacts = {
            'stocks': impact_magnitude * 0.9 if impact_level in [ImpactLevel.HIGH, ImpactLevel.BLACK_SWAN] else impact_magnitude * 0.6,
            'forex': impact_magnitude * 0.8 if 'fed' in text.lower() or 'interest' in text.lower() else impact_magnitude * 0.5,
            'metals': impact_magnitude * 0.7 if 'inflation' in text.lower() else impact_magnitude * 0.4,
            'crypto': impact_magnitude * 0.6,
            'bonds': impact_magnitude * 0.8 if 'fed' in text.lower() or 'inflation' in text.lower() else impact_magnitude * 0.5
        }
        
        return {
            'impact_level': impact_level,
            'asset_impacts': asset_impacts,
            'impact_magnitude': impact_magnitude,
            'time_to_impact': max(1, int(impact_magnitude * 6)),  # 1-6 hours
            'recovery_time': max(6, int(impact_magnitude * 48))  # 6-48 hours
        }
    
    def _fallback_classification(self, news_item: NewsItem) -> NewsItem:
        """Fallback classification using keyword matching"""
        text = f"{news_item.headline} {news_item.content}".lower()
        
        if any(keyword in text for keyword in ['fed', 'federal reserve', 'crisis', 'war']):
            news_item.classification = ImpactLevel.BLACK_SWAN
            news_item.impact_magnitude = 0.9
        elif any(keyword in text for keyword in ['gdp', 'inflation', 'earnings', 'nfp']):
            news_item.classification = ImpactLevel.HIGH
            news_item.impact_magnitude = 0.8
        elif any(keyword in text for keyword in ['pmi', 'retail', 'housing']):
            news_item.classification = ImpactLevel.MEDIUM
            news_item.impact_magnitude = 0.5
        else:
            news_item.classification = ImpactLevel.LOW
            news_item.impact_magnitude = 0.3
        
        # Default asset impacts
        news_item.affected_assets = {
            'stocks': news_item.impact_magnitude * 0.8,
            'forex': news_item.impact_magnitude * 0.7,
            'metals': news_item.impact_magnitude * 0.6,
            'crypto': news_item.impact_magnitude * 0.5,
            'bonds': news_item.impact_magnitude * 0.7
        }
        
        news_item.time_to_impact = max(1, int(news_item.impact_magnitude * 6))
        news_item.recovery_prediction = max(6, int(news_item.impact_magnitude * 48))
        
        return news_item

class ImpactAnalysisEngine:
    """Main impact analysis engine"""
    
    def __init__(self, fred_api_key: str, gpt5_api_key: str):
        self.fred_api = FREDApiIntegration(fred_api_key)
        self.gpt5_classifier = GPT5NewsClassifier(gpt5_api_key)
        self.event_cache = {}
        self.correlation_matrix = self._initialize_correlations()
        
    def _initialize_correlations(self) -> pd.DataFrame:
        """Initialize cross-asset correlation matrix"""
        assets = ['SPY', 'QQQ', 'GLD', 'SLV', 'EURUSD', 'USDJPY', 'BTCUSD', 'TLT']
        correlation_data = np.random.uniform(-0.8, 0.8, (len(assets), len(assets)))
        
        # Make correlation matrix symmetric and set diagonal to 1
        correlation_data = (correlation_data + correlation_data.T) / 2
        np.fill_diagonal(correlation_data, 1.0)
        
        return pd.DataFrame(correlation_data, index=assets, columns=assets)
    
    async def get_economic_calendar(self) -> List[EconomicEvent]:
        """Get economic calendar with event classifications"""
        try:
            # Key economic indicators to monitor
            series_ids = [
                'CPIAUCSL',     # Consumer Price Index
                'GDP',          # Gross Domestic Product  
                'UNRATE',       # Unemployment Rate
                'INDPRO',       # Industrial Production
                'PAYEMS',       # Nonfarm Payrolls
                'FEDFUNDS'      # Federal Funds Rate
            ]
            
            release_ids = [
                '500',          # Consumer Price Index
                '193',          # Employment Situation
                '238',          # Gross Domestic Product
                '194',          # Retail Sales
                '53',           # Manufacturing PMI
                '207'           # Consumer Confidence
            ]
            
            # Get indicators and calendar data
            indicators = await self.fred_api.get_indicators(series_ids)
            calendar = await self.fred_api.get_release_dates(release_ids)
            
            events = []
            
            # Process calendar events
            for event_data in calendar:
                event = await self._process_economic_event(event_data)
                if event:
                    events.append(event)
            
            # Add manually defined high-impact events
            events.extend(self._get_recurring_high_impact_events())
            
            return sorted(events, key=lambda x: x.date)
            
        except Exception as e:
            logger.error(f"Error getting economic calendar: {e}")
            return []
    
    async def _process_economic_event(self, event_data: Dict) -> Optional[EconomicEvent]:
        """Process individual economic event"""
        try:
            title = event_data.get('release_name', '')
            event_date = datetime.strptime(event_data.get('date', ''), '%Y-%m-%d')
            
            # Classify event impact based on release type
            impact_level = self._classify_event_impact(title)
            
            # Calculate asset impacts
            asset_impact = self._calculate_asset_impacts(impact_level, title)
            
            event = EconomicEvent(
                title=title,
                date=event_date,
                impact_level=impact_level,
                description=f"Scheduled release: {title}",
                previous_value=None,
                forecast_value=None,
                actual_value=None,
                source="FRED",
                asset_impact=asset_impact,
                volatility_impact=self._estimate_volatility_impact(impact_level),
                recovery_time_estimate=self._estimate_recovery_time(impact_level)
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error processing economic event: {e}")
            return None
    
    def _classify_event_impact(self, event_title: str) -> ImpactLevel:
        """Classify event impact level"""
        title_lower = event_title.lower()
        
        if any(keyword in title_lower for keyword in ['federal funds', 'gdp', 'consumer price', 'employment situation']):
            return ImpactLevel.HIGH
        elif any(keyword in title_lower for keyword in ['retail sales', 'industrial production', 'consumer confidence']):
            return ImpactLevel.MEDIUM
        elif any(keyword in title_lower for keyword in ['manufacturing', 'services']):
            return ImpactLevel.LOW
        else:
            return ImpactLevel.LOW
    
    def _calculate_asset_impacts(self, impact_level: ImpactLevel, event_title: str) -> Dict[AssetClass, float]:
        """Calculate expected asset class impacts"""
        base_impacts = {
            ImpactLevel.BLACK_SWAN: {
                AssetClass.STOCKS: 0.9,
                AssetClass.FOREX: 0.8,
                AssetClass.METALS: 0.7,
                AssetClass.CRYPTO: 0.8,
                AssetClass.BONDS: 0.9
            },
            ImpactLevel.HIGH: {
                AssetClass.STOCKS: 0.7,
                AssetClass.FOREX: 0.6,
                AssetClass.METALS: 0.5,
                AssetClass.CRYPTO: 0.6,
                AssetClass.BONDS: 0.7
            },
            ImpactLevel.MEDIUM: {
                AssetClass.STOCKS: 0.5,
                AssetClass.FOREX: 0.4,
                AssetClass.METALS: 0.4,
                AssetClass.CRYPTO: 0.4,
                AssetClass.BONDS: 0.5
            },
            ImpactLevel.LOW: {
                AssetClass.STOCKS: 0.2,
                AssetClass.FOREX: 0.2,
                AssetClass.METALS: 0.2,
                AssetClass.CRYPTO: 0.2,
                AssetClass.BONDS: 0.2
            }
        }
        
        impacts = base_impacts[impact_level].copy()
        
        # Adjust for specific event types
        title_lower = event_title.lower()
        if 'inflation' in title_lower or 'cpi' in title_lower:
            impacts[AssetClass.METALS] *= 1.2  # Inflation hedge
            impacts[AssetClass.BONDS] *= 1.3   # Interest rate sensitive
            
        if 'employment' in title_lower or 'unemployment' in title_lower:
            impacts[AssetClass.STOCKS] *= 1.2  # Growth indicator
            
        return impacts
    
    def _estimate_volatility_impact(self, impact_level: ImpactLevel) -> Dict[str, float]:
        """Estimate volatility impact by asset"""
        return {
            'VIX': 0.8 if impact_level == ImpactLevel.BLACK_SWAN else 0.6 if impact_level == ImpactLevel.HIGH else 0.4,
            'US500': 0.7 if impact_level == ImpactLevel.BLACK_SWAN else 0.5 if impact_level == ImpactLevel.HIGH else 0.3,
            'EURUSD': 0.6 if impact_level == ImpactLevel.BLACK_SWAN else 0.4 if impact_level == ImpactLevel.HIGH else 0.2,
            'XAUUSD': 0.5 if impact_level == ImpactLevel.BLACK_SWAN else 0.4 if impact_level == ImpactLevel.HIGH else 0.2
        }
    
    def _estimate_recovery_time(self, impact_level: ImpactLevel) -> int:
        """Estimate recovery time in hours"""
        recovery_times = {
            ImpactLevel.BLACK_SWAN: 72,   # 3 days
            ImpactLevel.HIGH: 48,         # 2 days
            ImpactLevel.MEDIUM: 24,       # 1 day
            ImpactLevel.LOW: 12           # 12 hours
        }
        return recovery_times[impact_level]
    
    def _get_recurring_high_impact_events(self) -> List[EconomicEvent]:
        """Get recurring high-impact events (FOMC meetings, earnings, etc.)"""
        now = datetime.now()
        events = []
        
        # FOMC meetings (8 per year, roughly every 6 weeks)
        fomc_dates = [
            now.replace(month=1, day=30, hour=14, minute=0),
            now.replace(month=3, day=20, hour=14, minute=0),
            now.replace(month=5, day=1, hour=14, minute=0),
            now.replace(month=6, day=12, hour=14, minute=0),
            now.replace(month=7, day=31, hour=14, minute=0),
            now.replace(month=9, day=18, hour=14, minute=0),
            now.replace(month=11, day=6, hour=14, minute=0),
            now.replace(month=12, day=18, hour=14, minute=0)
        ]
        
        for date in fomc_dates:
            if date > now:
                events.append(EconomicEvent(
                    title="FOMC Meeting - Federal Open Market Committee",
                    date=date,
                    impact_level=ImpactLevel.HIGH,
                    description="Federal Reserve policy meeting and interest rate decision",
                    previous_value=None,
                    forecast_value=None,
                    actual_value=None,
                    source="Federal Reserve",
                    asset_impact={
                        AssetClass.STOCKS: 0.8,
                        AssetClass.FOREX: 0.9,
                        AssetClass.METALS: 0.6,
                        AssetClass.CRYPTO: 0.7,
                        AssetClass.BONDS: 0.9
                    },
                    volatility_impact={
                        'VIX': 0.8,
                        'US500': 0.7,
                        'EURUSD': 0.8,
                        'XAUUSD': 0.6
                    },
                    recovery_time_estimate=48
                ))
        
        return events
    
    async def analyze_news_impact(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Analyze news items for market impact"""
        analyzed_news = []
        
        # Process news items concurrently
        tasks = [self.gpt5_classifier.classify_news(news) for news in news_items]
        analyzed_news = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        return [news for news in analyzed_news if isinstance(news, NewsItem)]
    
    def predict_market_reaction(self, event: EconomicEvent, 
                              current_prices: Dict[str, float]) -> List[MarketReaction]:
        """Predict market reaction to economic events"""
        reactions = []
        
        for asset_class, impact_magnitude in event.asset_impact.items():
            # Get correlation factor for this asset class
            correlation_factor = self._get_correlation_factor(asset_class)
            
            # Calculate expected move
            expected_move = impact_magnitude * current_prices.get('market_vol', 0.02) * correlation_factor
            
            # Estimate volatility spike
            volatility_spike = impact_magnitude * 100  # Percentage
            
            # Determine direction (simplified)
            direction = "bullish" if impact_magnitude > 0.5 else "bearish"
            
            # Calculate confidence based on impact level
            confidence = min(0.95, 0.6 + (impact_magnitude * 0.4))
            
            # Time estimates
            time_to_max = max(1, int(impact_magnitude * 6))  # 1-6 hours
            recovery_time = max(6, int(impact_magnitude * 48))  # 6-48 hours
            
            reaction = MarketReaction(
                asset_class=asset_class,
                expected_move=expected_move,
                volatility_spike=volatility_spike,
                direction=direction,
                confidence=confidence,
                time_to_max_impact=time_to_max,
                recovery_time=recovery_time
            )
            
            reactions.append(reaction)
        
        return reactions
    
    def _get_correlation_factor(self, asset_class: AssetClass) -> float:
        """Get correlation factor for asset class"""
        correlation_factors = {
            AssetClass.STOCKS: 1.0,
            AssetClass.FOREX: 0.8,
            AssetClass.METALS: 0.6,
            AssetClass.CRYPTO: 0.7,
            AssetClass.BONDS: 0.9
        }
        return correlation_factors[asset_class]
    
    def cluster_similar_events(self, events: List[EconomicEvent]) -> Dict[str, List[EconomicEvent]]:
        """Cluster similar events for pattern analysis"""
        clusters = {}
        
        for event in events:
            # Create cluster key based on impact level and type
            cluster_key = f"{event.impact_level.value}_{event.title[:20].lower()}"
            
            if cluster_key not in clusters:
                clusters[cluster_key] = []
            
            clusters[cluster_key].append(event)
        
        # Keep only clusters with multiple events
        return {k: v for k, v in clusters.items() if len(v) > 1}
    
    def generate_impact_report(self, events: List[EconomicEvent], 
                             news_items: List[NewsItem]) -> Dict[str, Any]:
        """Generate comprehensive impact assessment report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_events': len(events),
                'high_impact_events': len([e for e in events if e.impact_level == ImpactLevel.HIGH]),
                'black_swan_events': len([e for e in events if e.impact_level == ImpactLevel.BLACK_SWAN]),
                'news_items_analyzed': len(news_items)
            },
            'upcoming_events': [
                {
                    'title': e.title,
                    'date': e.date.isoformat(),
                    'impact_level': e.impact_level.value,
                    'expected_impact': {asset.value: impact for asset, impact in e.asset_impact.items()}
                }
                for e in events if e.date > datetime.now()
            ],
            'news_analysis': [
                {
                    'headline': n.headline,
                    'classification': n.classification.value,
                    'impact_magnitude': n.impact_magnitude,
                    'affected_assets': n.affected_assets
                }
                for n in news_items
            ],
            'risk_assessment': self._assess_systemic_risk(events),
            'asset_allocation_recommendations': self._generate_allocation_recommendations(events)
        }
        
        return report
    
    def _assess_systemic_risk(self, events: List[EconomicEvent]) -> Dict[str, Any]:
        """Assess overall systemic risk from upcoming events"""
        high_impact_count = len([e for e in events if e.impact_level in [ImpactLevel.HIGH, ImpactLevel.BLACK_SWAN]])
        total_impact_score = sum(e.impact_magnitude for e in events if hasattr(e, 'impact_magnitude'))
        
        if high_impact_count >= 3 or total_impact_score >= 2.5:
            risk_level = "HIGH"
        elif high_impact_count >= 1 or total_impact_score >= 1.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            'risk_level': risk_level,
            'high_impact_count': high_impact_count,
            'total_impact_score': total_impact_score,
            'recommendation': self._get_risk_recommendation(risk_level)
        }
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get risk management recommendation"""
        recommendations = {
            "HIGH": "Reduce position sizes, increase cash allocation, prepare for high volatility",
            "MEDIUM": "Monitor positions closely, consider hedging strategies",
            "LOW": "Normal trading operations, maintain current positions"
        }
        return recommendations[risk_level]
    
    def _generate_allocation_recommendations(self, events: List[EconomicEvent]) -> Dict[str, float]:
        """Generate asset allocation recommendations based on upcoming events"""
        base_allocation = {
            'stocks': 0.40,
            'bonds': 0.30,
            'metals': 0.15,
            'forex': 0.10,
            'crypto': 0.05
        }
        
        # Adjust based on high-impact events
        high_impact_events = [e for e in events if e.impact_level == ImpactLevel.HIGH]
        
        if any('inflation' in e.title.lower() or 'fed' in e.title.lower() for e in high_impact_events):
            # Inflation/fed events favor bonds and metals
            base_allocation['bonds'] = min(0.45, base_allocation['bonds'] + 0.10)
            base_allocation['metals'] = min(0.25, base_allocation['metals'] + 0.05)
            base_allocation['stocks'] = max(0.30, base_allocation['stocks'] - 0.10)
            base_allocation['crypto'] = max(0.02, base_allocation['crypto'] - 0.02)
        
        if any('employment' in e.title.lower() or 'gdp' in e.title.lower() for e in high_impact_events):
            # Growth events favor stocks
            base_allocation['stocks'] = min(0.50, base_allocation['stocks'] + 0.08)
            base_allocation['bonds'] = max(0.25, base_allocation['bonds'] - 0.05)
            base_allocation['metals'] = max(0.12, base_allocation['metals'] - 0.02)
        
        # Normalize allocations
        total = sum(base_allocation.values())
        base_allocation = {k: v/total for k, v in base_allocation.items()}
        
        return base_allocation

class NewsImpactAssessmentSystem:
    """Main system orchestrator"""
    
    def __init__(self, fred_api_key: str = "", gpt5_api_key: str = ""):
        self.engine = ImpactAnalysisEngine(fred_api_key, gpt5_api_key)
        self.news_sources = [
            'reuters', 'bloomberg', 'cnbc', 'marketwatch', 
            'yahoo_finance', 'investing', 'tradingview'
        ]
        
    async def run_full_assessment(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Run complete news impact assessment"""
        logger.info("Starting full news impact assessment...")
        
        try:
            # 1. Get economic calendar
            economic_events = await self.engine.get_economic_calendar()
            logger.info(f"Retrieved {len(economic_events)} economic events")
            
            # 2. Simulate news feed (in real implementation, fetch from news APIs)
            news_items = await self._simulate_news_feed()
            logger.info(f"Processing {len(news_items)} news items")
            
            # 3. Analyze news impact
            analyzed_news = await self.engine.analyze_news_impact(news_items)
            
            # 4. Predict market reactions
            market_reactions = []
            for event in economic_events[:5]:  # Top 5 upcoming events
                reactions = self.engine.predict_market_reaction(event, current_prices)
                market_reactions.extend(reactions)
            
            # 5. Generate comprehensive report
            report = self.engine.generate_impact_report(economic_events, analyzed_news)
            
            # 6. Add market reactions to report
            report['market_reactions'] = [
                {
                    'asset_class': r.asset_class.value,
                    'expected_move': r.expected_move,
                    'volatility_spike': r.volatility_spike,
                    'direction': r.direction,
                    'confidence': r.confidence
                }
                for r in market_reactions
            ]
            
            # 7. Event clustering analysis
            clusters = self.engine.cluster_similar_events(economic_events)
            report['event_patterns'] = {
                'total_clusters': len(clusters),
                'largest_cluster': max(len(v) for v in clusters.values()) if clusters else 0,
                'cluster_details': {k: len(v) for k, v in clusters.items()}
            }
            
            logger.info("News impact assessment completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error in full assessment: {e}")
            return {'error': str(e)}
    
    async def _simulate_news_feed(self) -> List[NewsItem]:
        """Simulate news feed (replace with actual news API integration)"""
        sample_news = [
            {
                'headline': 'Federal Reserve signals potential rate cuts in next meeting',
                'content': 'Fed officials indicate cautious approach to monetary policy amid economic uncertainties.',
                'source': 'Reuters',
                'timestamp': datetime.now() - timedelta(hours=1)
            },
            {
                'headline': 'Gold prices surge on inflation concerns',
                'content': 'Gold reaches new highs as investors seek inflation hedge.',
                'source': 'Bloomberg',
                'timestamp': datetime.now() - timedelta(hours=2)
            },
            {
                'headline': 'Tech earnings beat expectations, NASDAQ rallies',
                'content': 'Major tech companies report strong quarterly results.',
                'source': 'CNBC',
                'timestamp': datetime.now() - timedelta(hours=3)
            }
        ]
        
        news_items = []
        for item in sample_news:
            news = NewsItem(
                headline=item['headline'],
                content=item['content'],
                timestamp=item['timestamp'],
                source=item['source'],
                classification=ImpactLevel.LOW,  # Will be updated by classifier
                affected_assets={},              # Will be updated by classifier
                sentiment_score=0.0,             # Will be calculated by classifier
                impact_magnitude=0.0,            # Will be calculated by classifier
                time_to_impact=None,             # Will be calculated by classifier
                recovery_prediction=None         # Will be calculated by classifier
            )
            news_items.append(news)
        
        return news_items
    
    async def get_real_time_alerts(self) -> List[Dict[str, Any]]:
        """Get real-time impact alerts"""
        try:
            # In real implementation, this would monitor news feeds and economic data
            # For demo purposes, return simulated alerts
            
            alerts = []
            
            # High priority alert simulation
            if datetime.now().hour in [8, 14]:  # US market open/Fed time
                alerts.append({
                    'level': 'HIGH',
                    'message': 'Federal Reserve communication detected - Monitor rate-sensitive assets',
                    'timestamp': datetime.now().isoformat(),
                    'assets': ['TLT', 'GLD', 'USDJPY']
                })
            
            # Medium priority alert simulation  
            if datetime.now().weekday() < 5:  # Weekday
                alerts.append({
                    'level': 'MEDIUM',
                    'message': 'High-impact economic data releases scheduled this week',
                    'timestamp': datetime.now().isoformat(),
                    'assets': ['SPY', 'QQQ', 'EURUSD']
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating real-time alerts: {e}")
            return []

# Demo usage and testing
async def demo_news_impact_system():
    """Demo the news impact assessment system"""
    print("🚀 News Impact Assessment System Demo")
    print("=" * 50)
    
    # Initialize system (replace API keys with real ones for production)
    system = NewsImpactAssessmentSystem(
        fred_api_key="your_fred_api_key_here",
        gpt5_api_key="your_openai_api_key_here"
    )
    
    # Sample current market prices
    current_prices = {
        'SPY': 445.50,
        'QQQ': 380.25,
        'GLD': 195.80,
        'EURUSD': 1.0850,
        'USDJPY': 149.50,
        'VIX': 18.5,
        'market_vol': 0.025  # 2.5% daily volatility
    }
    
    print("\n📊 Current Market Data:")
    for asset, price in current_prices.items():
        print(f"  {asset}: {price}")
    
    print("\n🔍 Running Full Impact Assessment...")
    
    # Run comprehensive assessment
    report = await system.run_full_assessment(current_prices)
    
    if 'error' not in report:
        print("\n📈 Impact Assessment Results:")
        print(f"  Total Events: {report['summary']['total_events']}")
        print(f"  High Impact Events: {report['summary']['high_impact_events']}")
        print(f"  Black Swan Events: {report['summary']['black_swan_events']}")
        print(f"  News Items Analyzed: {report['summary']['news_items_analyzed']}")
        
        print("\n⚠️  Risk Assessment:")
        risk = report['risk_assessment']
        print(f"  Risk Level: {risk['risk_level']}")
        print(f"  High Impact Count: {risk['high_impact_count']}")
        print(f"  Total Impact Score: {risk['total_impact_score']:.2f}")
        print(f"  Recommendation: {risk['recommendation']}")
        
        print("\n💼 Asset Allocation Recommendations:")
        for asset, allocation in report['asset_allocation_recommendations'].items():
            print(f"  {asset.upper()}: {allocation:.1%}")
        
        print("\n📅 Top Upcoming Events:")
        for event in report['upcoming_events'][:3]:
            print(f"  {event['date'][:10]}: {event['title']} ({event['impact_level']})")
        
        print("\n📰 News Analysis Summary:")
        for news in report['news_analysis'][:3]:
            print(f"  {news['classification']}: {news['headline'][:50]}...")
        
        print("\n🎯 Market Reaction Predictions:")
        for reaction in report['market_reactions'][:5]:
            direction_emoji = "📈" if reaction['direction'] == 'bullish' else "📉"
            print(f"  {reaction['asset_class']}: {reaction['volatility_spike']:.1f}% volatility spike {direction_emoji}")
        
        print("\n🔄 Event Clustering Analysis:")
        patterns = report['event_patterns']
        print(f"  Total Clusters: {patterns['total_clusters']}")
        print(f"  Largest Cluster Size: {patterns['largest_cluster']}")
        
    else:
        print(f"❌ Error in assessment: {report['error']}")
    
    print("\n🚨 Real-time Alerts:")
    alerts = await system.get_real_time_alerts()
    for alert in alerts:
        print(f"  [{alert['level']}] {alert['message']}")
        print(f"    Affected Assets: {', '.join(alert['assets'])}")
    
    print("\n✅ News Impact Assessment Demo Complete!")

if __name__ == "__main__":
    asyncio.run(demo_news_impact_system())