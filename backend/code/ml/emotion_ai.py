"""
Emotion AI - Market Sentiment va Psychology Analysis
====================================================

Bu modul bozor psixologiyasi va hissiyotlarini tahlil qiladi:
- Fear & Greed Index - Bozor qo'rquv va ochko'zlik indeksi
- Trader Sentiment Analysis - Treyder kayfiyatini tahlil qilish
- Social Media Sentiment - Twitter, Reddit, Telegram sentiment
- News Sentiment - Yangiliklar tahlili
- Market Psychology Patterns - Psixologik pattern detection

Author: AI Trading Evolution
Date: 2025-11-04
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging
import requests
import json
from collections import defaultdict
import re
from textblob import TextBlob
import tweepy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Enums
# ============================================================================

class MarketEmotion(Enum):
    """Bozor hissiyotlari"""
    EXTREME_FEAR = "extreme_fear"
    FEAR = "fear"
    NEUTRAL = "neutral"
    GREED = "greed"
    EXTREME_GREED = "extreme_greed"


class SentimentType(Enum):
    """Sentiment turlari"""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


class PsychologyPattern(Enum):
    """Psixologik patternlar"""
    FOMO = "fear_of_missing_out"
    FUD = "fear_uncertainty_doubt"
    CAPITULATION = "capitulation"
    EUPHORIA = "euphoria"
    PANIC_SELLING = "panic_selling"
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class FearGreedMetrics:
    """Fear & Greed Index metrikalar"""
    overall_score: float  # 0-100
    volatility_score: float
    market_momentum_score: float
    social_media_score: float
    dominance_score: float
    trend_score: float
    emotion: MarketEmotion
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            'overall_score': self.overall_score,
            'volatility_score': self.volatility_score,
            'market_momentum_score': self.market_momentum_score,
            'social_media_score': self.social_media_score,
            'dominance_score': self.dominance_score,
            'trend_score': self.trend_score,
            'emotion': self.emotion.value,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class SentimentScore:
    """Sentiment score"""
    score: float  # -1 to 1
    sentiment_type: SentimentType
    confidence: float  # 0 to 1
    source: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            'score': self.score,
            'sentiment_type': self.sentiment_type.value,
            'confidence': self.confidence,
            'source': self.source,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class PsychologySignal:
    """Psixologik signal"""
    pattern: PsychologyPattern
    strength: float  # 0 to 1
    description: str
    indicators: Dict[str, float]
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            'pattern': self.pattern.value,
            'strength': self.strength,
            'description': self.description,
            'indicators': self.indicators,
            'timestamp': self.timestamp.isoformat()
        }


# ============================================================================
# Fear & Greed Index Calculator
# ============================================================================

class FearGreedIndex:
    """Crypto Fear & Greed Index calculator"""
    
    def __init__(self):
        self.history = []
        
    def calculate_volatility_score(self, prices: List[float], period: int = 30) -> float:
        """Volatility asosida score (0-100)"""
        if len(prices) < period:
            return 50.0
            
        returns = np.diff(prices[-period:]) / prices[-period:-1]
        volatility = np.std(returns) * np.sqrt(365)
        
        # Yuqori volatility = fear, past volatility = greed
        # 50% yillik volatility = extreme fear (0)
        # 10% yillik volatility = extreme greed (100)
        if volatility >= 0.5:
            score = 0.0
        elif volatility <= 0.1:
            score = 100.0
        else:
            # Linear interpolation
            score = 100 - ((volatility - 0.1) / 0.4) * 100
            
        return max(0, min(100, score))
        
    def calculate_momentum_score(self, prices: List[float], 
                                 volumes: List[float]) -> float:
        """Market momentum score (0-100)"""
        if len(prices) < 30:
            return 50.0
            
        # 30 kunlik momentum
        momentum_30d = (prices[-1] - prices[-30]) / prices[-30]
        
        # Volume-weighted momentum
        volume_change = (np.mean(volumes[-7:]) - np.mean(volumes[-30:-7])) / np.mean(volumes[-30:-7])
        
        # Combine
        combined_momentum = momentum_30d + 0.3 * volume_change
        
        # Convert to 0-100 scale
        # +50% momentum = extreme greed (100)
        # -50% momentum = extreme fear (0)
        if combined_momentum >= 0.5:
            score = 100.0
        elif combined_momentum <= -0.5:
            score = 0.0
        else:
            score = 50 + (combined_momentum / 0.5) * 50
            
        return max(0, min(100, score))
        
    def calculate_dominance_score(self, btc_dominance: float) -> float:
        """BTC dominance asosida score (0-100)"""
        # BTC dominance oshsa - fear (altcoinlardan chiqib ketishmoqda)
        # BTC dominance pasaysa - greed (altcoinlarga kirishmoqda)
        
        # Historical average: ~45%
        avg_dominance = 45.0
        
        if btc_dominance > avg_dominance:
            # Fear territory
            deviation = (btc_dominance - avg_dominance) / avg_dominance
            score = 50 - min(50, deviation * 100)
        else:
            # Greed territory
            deviation = (avg_dominance - btc_dominance) / avg_dominance
            score = 50 + min(50, deviation * 100)
            
        return max(0, min(100, score))
        
    def calculate_trend_score(self, prices: List[float]) -> float:
        """Trend strength score (0-100)"""
        if len(prices) < 90:
            return 50.0
            
        # Simple Moving Averages
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        sma_90 = np.mean(prices[-90:])
        
        current_price = prices[-1]
        
        # Bullish trend indicators
        bullish_score = 0
        
        # Price above SMAs
        if current_price > sma_20:
            bullish_score += 25
        if current_price > sma_50:
            bullish_score += 25
        if current_price > sma_90:
            bullish_score += 25
            
        # Golden cross
        if sma_20 > sma_50:
            bullish_score += 25
            
        return float(bullish_score)
        
    def calculate_social_media_score(self, sentiment_scores: List[float]) -> float:
        """Social media sentiment score (0-100)"""
        if not sentiment_scores:
            return 50.0
            
        # Sentiment: -1 to 1
        avg_sentiment = np.mean(sentiment_scores)
        
        # Convert to 0-100 scale
        score = 50 + avg_sentiment * 50
        
        return max(0, min(100, score))
        
    def calculate_index(self, 
                       prices: List[float],
                       volumes: List[float],
                       btc_dominance: float,
                       sentiment_scores: List[float]) -> FearGreedMetrics:
        """Fear & Greed Index hisoblash"""
        
        # Individual scores
        volatility_score = self.calculate_volatility_score(prices)
        momentum_score = self.calculate_momentum_score(prices, volumes)
        dominance_score = self.calculate_dominance_score(btc_dominance)
        trend_score = self.calculate_trend_score(prices)
        social_score = self.calculate_social_media_score(sentiment_scores)
        
        # Weighted average
        weights = {
            'volatility': 0.25,
            'momentum': 0.25,
            'dominance': 0.15,
            'trend': 0.20,
            'social': 0.15
        }
        
        overall_score = (
            volatility_score * weights['volatility'] +
            momentum_score * weights['momentum'] +
            dominance_score * weights['dominance'] +
            trend_score * weights['trend'] +
            social_score * weights['social']
        )
        
        # Determine emotion
        if overall_score <= 25:
            emotion = MarketEmotion.EXTREME_FEAR
        elif overall_score <= 45:
            emotion = MarketEmotion.FEAR
        elif overall_score <= 55:
            emotion = MarketEmotion.NEUTRAL
        elif overall_score <= 75:
            emotion = MarketEmotion.GREED
        else:
            emotion = MarketEmotion.EXTREME_GREED
            
        metrics = FearGreedMetrics(
            overall_score=overall_score,
            volatility_score=volatility_score,
            market_momentum_score=momentum_score,
            social_media_score=social_score,
            dominance_score=dominance_score,
            trend_score=trend_score,
            emotion=emotion,
            timestamp=datetime.now()
        )
        
        self.history.append(metrics)
        
        return metrics
        
    def get_historical_fear_greed(self, days: int = 30) -> List[FearGreedMetrics]:
        """Tarixiy Fear & Greed data"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [m for m in self.history if m.timestamp >= cutoff_date]
        
    def get_trend(self, days: int = 7) -> str:
        """Fear & Greed trend"""
        recent = self.get_historical_fear_greed(days)
        
        if len(recent) < 2:
            return "insufficient_data"
            
        first_score = recent[0].overall_score
        last_score = recent[-1].overall_score
        
        change = last_score - first_score
        
        if change > 10:
            return "increasing_greed"
        elif change < -10:
            return "increasing_fear"
        else:
            return "stable"


# ============================================================================
# Sentiment Analysis Engine
# ============================================================================

class SentimentAnalyzer:
    """Text sentiment analysis"""
    
    def __init__(self):
        # Keywords for crypto sentiment
        self.positive_keywords = [
            'bull', 'bullish', 'moon', 'rocket', 'pump', 'gain', 'profit',
            'buy', 'long', 'hodl', 'accumulate', 'breakout', 'rally',
            'strong', 'support', 'bounce', 'reversal', 'uptrend'
        ]
        
        self.negative_keywords = [
            'bear', 'bearish', 'dump', 'crash', 'loss', 'sell', 'short',
            'panic', 'fear', 'resistance', 'breakdown', 'decline',
            'weak', 'drop', 'fall', 'correction', 'downtrend'
        ]
        
    def analyze_text(self, text: str) -> SentimentScore:
        """Text sentiment tahlil"""
        text_lower = text.lower()
        
        # TextBlob sentiment
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        # Keyword-based adjustment
        positive_count = sum(1 for kw in self.positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in self.negative_keywords if kw in text_lower)
        
        keyword_score = (positive_count - negative_count) / max(1, positive_count + negative_count)
        
        # Combine scores
        combined_score = 0.6 * polarity + 0.4 * keyword_score
        combined_score = max(-1, min(1, combined_score))
        
        # Confidence based on subjectivity
        confidence = 1 - subjectivity
        
        # Determine sentiment type
        if combined_score >= 0.5:
            sentiment_type = SentimentType.VERY_POSITIVE
        elif combined_score >= 0.1:
            sentiment_type = SentimentType.POSITIVE
        elif combined_score > -0.1:
            sentiment_type = SentimentType.NEUTRAL
        elif combined_score > -0.5:
            sentiment_type = SentimentType.NEGATIVE
        else:
            sentiment_type = SentimentType.VERY_NEGATIVE
            
        return SentimentScore(
            score=combined_score,
            sentiment_type=sentiment_type,
            confidence=confidence,
            source="text_analysis",
            timestamp=datetime.now()
        )
        
    def batch_analyze(self, texts: List[str]) -> List[SentimentScore]:
        """Bir nechta textni tahlil"""
        return [self.analyze_text(text) for text in texts]
        
    def get_aggregated_sentiment(self, scores: List[SentimentScore]) -> Dict[str, Any]:
        """Aggregated sentiment"""
        if not scores:
            return {
                'average_score': 0.0,
                'sentiment_distribution': {},
                'confidence': 0.0
            }
            
        avg_score = np.mean([s.score for s in scores])
        avg_confidence = np.mean([s.confidence for s in scores])
        
        # Distribution
        distribution = defaultdict(int)
        for score in scores:
            distribution[score.sentiment_type.name] += 1
            
        return {
            'average_score': avg_score,
            'sentiment_distribution': dict(distribution),
            'confidence': avg_confidence,
            'total_samples': len(scores)
        }


# ============================================================================
# Social Media Sentiment Tracker
# ============================================================================

class SocialMediaTracker:
    """Twitter, Reddit, Telegram sentiment tracker"""
    
    def __init__(self, twitter_api_key: Optional[str] = None):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.twitter_api_key = twitter_api_key
        self.sentiment_history = defaultdict(list)
        
    def track_twitter(self, keywords: List[str], count: int = 100) -> List[SentimentScore]:
        """Twitter sentiment tracking"""
        if not self.twitter_api_key:
            logger.warning("Twitter API key mavjud emas, simulated data qaytarilmoqda")
            return self._generate_simulated_twitter_sentiment(keywords, count)
            
        # Real Twitter API integration
        try:
            # Tweepy bilan Twitter API
            auth = tweepy.OAuthHandler(self.twitter_api_key, "")
            api = tweepy.API(auth)
            
            sentiments = []
            for keyword in keywords:
                tweets = api.search_tweets(q=keyword, count=count, lang='en')
                
                for tweet in tweets:
                    sentiment = self.sentiment_analyzer.analyze_text(tweet.text)
                    sentiment.source = f"twitter:{keyword}"
                    sentiments.append(sentiment)
                    
            return sentiments
            
        except Exception as e:
            logger.error(f"Twitter API error: {e}")
            return self._generate_simulated_twitter_sentiment(keywords, count)
            
    def _generate_simulated_twitter_sentiment(self, keywords: List[str], 
                                             count: int) -> List[SentimentScore]:
        """Simulated Twitter sentiment"""
        sentiments = []
        
        # Realistic tweet templates
        templates = [
            "{coin} is going to the moon! 🚀",
            "Just bought more {coin}, feeling bullish",
            "{coin} looks bearish, might sell soon",
            "Panic selling {coin} rn",
            "{coin} breaking resistance, buy signal!",
            "{coin} dump incoming, be careful",
            "Hodling {coin} strong 💎🙌",
            "{coin} chart looks terrible",
            "Accumulating {coin} at these prices",
            "{coin} to $100k soon"
        ]
        
        for keyword in keywords:
            for _ in range(count // len(keywords)):
                template = np.random.choice(templates)
                text = template.format(coin=keyword)
                
                sentiment = self.sentiment_analyzer.analyze_text(text)
                sentiment.source = f"twitter_simulated:{keyword}"
                sentiments.append(sentiment)
                
        return sentiments
        
    def track_reddit(self, subreddits: List[str], limit: int = 50) -> List[SentimentScore]:
        """Reddit sentiment tracking"""
        # Simulated Reddit data
        sentiments = []
        
        post_templates = [
            "Why {sub} is the best investment right now",
            "Should I sell my {sub} holdings?",
            "{sub} analysis - bullish patterns forming",
            "Warning: {sub} might crash soon",
            "Daily discussion - {sub} looking strong",
            "{sub} bearish divergence spotted",
            "Buying the dip on {sub}",
            "Time to exit {sub}?"
        ]
        
        for subreddit in subreddits:
            for _ in range(limit // len(subreddits)):
                template = np.random.choice(post_templates)
                text = template.format(sub=subreddit)
                
                sentiment = self.sentiment_analyzer.analyze_text(text)
                sentiment.source = f"reddit:{subreddit}"
                sentiments.append(sentiment)
                
        return sentiments
        
    def get_trending_sentiment(self, platform: str = "all") -> Dict[str, Any]:
        """Trending sentiment"""
        if platform == "all":
            all_sentiments = []
            for sentiments in self.sentiment_history.values():
                all_sentiments.extend(sentiments)
        else:
            all_sentiments = self.sentiment_history.get(platform, [])
            
        return self.sentiment_analyzer.get_aggregated_sentiment(all_sentiments)
        
    def store_sentiment(self, platform: str, sentiments: List[SentimentScore]):
        """Sentiment saqlash"""
        self.sentiment_history[platform].extend(sentiments)
        
        # Keep only recent 1000 entries per platform
        if len(self.sentiment_history[platform]) > 1000:
            self.sentiment_history[platform] = self.sentiment_history[platform][-1000:]


# ============================================================================
# News Sentiment Analyzer
# ============================================================================

class NewsSentimentAnalyzer:
    """News sentiment analysis"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.news_cache = []
        
    def fetch_crypto_news(self, keywords: List[str] = None) -> List[Dict]:
        """Crypto news fetch (simulated)"""
        if keywords is None:
            keywords = ['bitcoin', 'ethereum', 'crypto', 'blockchain']
            
        # Simulated news
        news_templates = [
            {
                'title': 'Bitcoin breaks $50,000 resistance level',
                'description': 'BTC surges past key resistance, analysts predict further gains',
                'sentiment_expected': 0.7
            },
            {
                'title': 'Major exchange suffers security breach',
                'description': 'Concerns rise as crypto platform reports vulnerability',
                'sentiment_expected': -0.6
            },
            {
                'title': 'Institutional adoption of crypto accelerates',
                'description': 'Major banks announce blockchain integration plans',
                'sentiment_expected': 0.8
            },
            {
                'title': 'Regulatory uncertainty impacts crypto markets',
                'description': 'New proposed regulations create selling pressure',
                'sentiment_expected': -0.5
            },
            {
                'title': 'DeFi TVL reaches all-time high',
                'description': 'Decentralized finance protocols see record inflows',
                'sentiment_expected': 0.6
            }
        ]
        
        news = []
        for _ in range(10):
            template = np.random.choice(news_templates)
            news.append({
                'title': template['title'],
                'description': template['description'],
                'timestamp': datetime.now() - timedelta(hours=np.random.randint(0, 24)),
                'source': 'crypto_news'
            })
            
        self.news_cache = news
        return news
        
    def analyze_news_sentiment(self, news_items: List[Dict]) -> List[SentimentScore]:
        """News sentiment tahlil"""
        sentiments = []
        
        for item in news_items:
            # Combine title and description
            text = f"{item['title']}. {item['description']}"
            
            sentiment = self.sentiment_analyzer.analyze_text(text)
            sentiment.source = item.get('source', 'news')
            sentiment.timestamp = item.get('timestamp', datetime.now())
            
            sentiments.append(sentiment)
            
        return sentiments
        
    def get_news_impact_score(self, hours: int = 24) -> float:
        """So'nggi N soatdagi news impact score (-1 to 1)"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_news = [n for n in self.news_cache if n['timestamp'] >= cutoff_time]
        
        if not recent_news:
            return 0.0
            
        sentiments = self.analyze_news_sentiment(recent_news)
        avg_score = np.mean([s.score for s in sentiments])
        
        return avg_score


# ============================================================================
# Market Psychology Pattern Detector
# ============================================================================

class PsychologyPatternDetector:
    """Market psychology pattern detection"""
    
    def __init__(self):
        self.pattern_history = []
        
    def detect_fomo(self, prices: List[float], volumes: List[float],
                   social_sentiment: float) -> Optional[PsychologySignal]:
        """FOMO (Fear Of Missing Out) detection"""
        if len(prices) < 30 or len(volumes) < 30:
            return None
            
        # Indicators
        price_increase = (prices[-1] - prices[-7]) / prices[-7]  # 7-day increase
        volume_surge = np.mean(volumes[-7:]) / np.mean(volumes[-30:-7])  # Volume spike
        
        # FOMO conditions:
        # 1. Sharp price increase (>15% in 7 days)
        # 2. Volume surge (>2x average)
        # 3. Very positive social sentiment (>0.5)
        
        strength = 0.0
        
        if price_increase > 0.15:
            strength += 0.4
        if volume_surge > 2.0:
            strength += 0.3
        if social_sentiment > 0.5:
            strength += 0.3
            
        if strength >= 0.6:
            return PsychologySignal(
                pattern=PsychologyPattern.FOMO,
                strength=strength,
                description="Strong FOMO detected - rapid price increase with high volume and positive sentiment",
                indicators={
                    'price_increase_7d': price_increase,
                    'volume_surge': volume_surge,
                    'social_sentiment': social_sentiment
                },
                timestamp=datetime.now()
            )
            
        return None
        
    def detect_fud(self, prices: List[float], news_sentiment: float,
                  social_sentiment: float) -> Optional[PsychologySignal]:
        """FUD (Fear, Uncertainty, Doubt) detection"""
        if len(prices) < 30:
            return None
            
        # Indicators
        price_decline = (prices[-1] - prices[-7]) / prices[-7]
        volatility = np.std(prices[-7:]) / np.mean(prices[-7:])
        
        # FUD conditions:
        # 1. Price decline (< -10%)
        # 2. High volatility (>5%)
        # 3. Negative news and social sentiment
        
        strength = 0.0
        
        if price_decline < -0.10:
            strength += 0.3
        if volatility > 0.05:
            strength += 0.2
        if news_sentiment < -0.3:
            strength += 0.25
        if social_sentiment < -0.3:
            strength += 0.25
            
        if strength >= 0.6:
            return PsychologySignal(
                pattern=PsychologyPattern.FUD,
                strength=strength,
                description="FUD detected - negative sentiment with price decline and volatility",
                indicators={
                    'price_decline_7d': price_decline,
                    'volatility': volatility,
                    'news_sentiment': news_sentiment,
                    'social_sentiment': social_sentiment
                },
                timestamp=datetime.now()
            )
            
        return None
        
    def detect_capitulation(self, prices: List[float], volumes: List[float],
                           fear_greed_score: float) -> Optional[PsychologySignal]:
        """Capitulation (taslim bo'lish) detection"""
        if len(prices) < 90 or len(volumes) < 90:
            return None
            
        # Indicators
        price_drop_30d = (prices[-1] - prices[-30]) / prices[-30]
        price_drop_90d = (prices[-1] - prices[-90]) / prices[-90]
        volume_spike = np.mean(volumes[-3:]) / np.mean(volumes[-30:-3])
        
        # Capitulation conditions:
        # 1. Severe price drop (>30% in 30 days, >50% in 90 days)
        # 2. Volume spike (panic selling)
        # 3. Extreme fear (<20)
        
        strength = 0.0
        
        if price_drop_30d < -0.30:
            strength += 0.3
        if price_drop_90d < -0.50:
            strength += 0.3
        if volume_spike > 2.5:
            strength += 0.2
        if fear_greed_score < 20:
            strength += 0.2
            
        if strength >= 0.7:
            return PsychologySignal(
                pattern=PsychologyPattern.CAPITULATION,
                strength=strength,
                description="Capitulation event - extreme selling pressure and fear",
                indicators={
                    'price_drop_30d': price_drop_30d,
                    'price_drop_90d': price_drop_90d,
                    'volume_spike': volume_spike,
                    'fear_greed_score': fear_greed_score
                },
                timestamp=datetime.now()
            )
            
        return None
        
    def detect_euphoria(self, prices: List[float], fear_greed_score: float,
                       social_sentiment: float) -> Optional[PsychologySignal]:
        """Euphoria (haddan tashqari xursandchilik) detection"""
        if len(prices) < 90:
            return None
            
        # Indicators
        price_increase_30d = (prices[-1] - prices[-30]) / prices[-30]
        price_increase_90d = (prices[-1] - prices[-90]) / prices[-90]
        
        # ATH proximity
        ath = max(prices)
        distance_from_ath = (ath - prices[-1]) / ath
        
        # Euphoria conditions:
        # 1. Large price increases
        # 2. Extreme greed (>80)
        # 3. Very positive social sentiment
        # 4. Near ATH
        
        strength = 0.0
        
        if price_increase_30d > 0.50:
            strength += 0.25
        if price_increase_90d > 1.0:
            strength += 0.25
        if fear_greed_score > 80:
            strength += 0.25
        if social_sentiment > 0.7:
            strength += 0.15
        if distance_from_ath < 0.05:
            strength += 0.10
            
        if strength >= 0.7:
            return PsychologySignal(
                pattern=PsychologyPattern.EUPHORIA,
                strength=strength,
                description="Market euphoria - extreme optimism and greed",
                indicators={
                    'price_increase_30d': price_increase_30d,
                    'price_increase_90d': price_increase_90d,
                    'fear_greed_score': fear_greed_score,
                    'social_sentiment': social_sentiment,
                    'distance_from_ath': distance_from_ath
                },
                timestamp=datetime.now()
            )
            
        return None
        
    def detect_all_patterns(self, prices: List[float], volumes: List[float],
                           fear_greed_score: float, news_sentiment: float,
                           social_sentiment: float) -> List[PsychologySignal]:
        """Barcha patternlarni detect qilish"""
        patterns = []
        
        # FOMO
        fomo = self.detect_fomo(prices, volumes, social_sentiment)
        if fomo:
            patterns.append(fomo)
            
        # FUD
        fud = self.detect_fud(prices, news_sentiment, social_sentiment)
        if fud:
            patterns.append(fud)
            
        # Capitulation
        capitulation = self.detect_capitulation(prices, volumes, fear_greed_score)
        if capitulation:
            patterns.append(capitulation)
            
        # Euphoria
        euphoria = self.detect_euphoria(prices, fear_greed_score, social_sentiment)
        if euphoria:
            patterns.append(euphoria)
            
        # Store in history
        self.pattern_history.extend(patterns)
        
        return patterns


# ============================================================================
# Integrated Emotion AI System
# ============================================================================

class EmotionAISystem:
    """Complete Emotion AI system"""
    
    def __init__(self, twitter_api_key: Optional[str] = None):
        self.fear_greed = FearGreedIndex()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.social_tracker = SocialMediaTracker(twitter_api_key)
        self.news_analyzer = NewsSentimentAnalyzer()
        self.psychology_detector = PsychologyPatternDetector()
        
    def analyze_market_emotion(self, 
                               prices: List[float],
                               volumes: List[float],
                               btc_dominance: float,
                               keywords: List[str] = None) -> Dict[str, Any]:
        """Complete market emotion analysis"""
        
        # Social media sentiment
        if keywords is None:
            keywords = ['bitcoin', 'btc', 'crypto']
            
        twitter_sentiments = self.social_tracker.track_twitter(keywords, count=100)
        reddit_sentiments = self.social_tracker.track_reddit(['cryptocurrency', 'bitcoin'], limit=50)
        
        all_social_sentiments = twitter_sentiments + reddit_sentiments
        social_agg = self.sentiment_analyzer.get_aggregated_sentiment(all_social_sentiments)
        
        # News sentiment
        news = self.news_analyzer.fetch_crypto_news(keywords)
        news_sentiments = self.news_analyzer.analyze_news_sentiment(news)
        news_agg = self.sentiment_analyzer.get_aggregated_sentiment(news_sentiments)
        
        # Fear & Greed Index
        sentiment_scores = [s.score for s in all_social_sentiments]
        fear_greed_metrics = self.fear_greed.calculate_index(
            prices, volumes, btc_dominance, sentiment_scores
        )
        
        # Psychology patterns
        patterns = self.psychology_detector.detect_all_patterns(
            prices, volumes,
            fear_greed_metrics.overall_score,
            news_agg['average_score'],
            social_agg['average_score']
        )
        
        return {
            'fear_greed_index': fear_greed_metrics.to_dict(),
            'social_sentiment': social_agg,
            'news_sentiment': news_agg,
            'psychology_patterns': [p.to_dict() for p in patterns],
            'trading_recommendation': self._generate_recommendation(
                fear_greed_metrics, social_agg, news_agg, patterns
            )
        }
        
    def _generate_recommendation(self, fear_greed: FearGreedMetrics,
                                social_agg: Dict, news_agg: Dict,
                                patterns: List[PsychologySignal]) -> str:
        """Trading recommendation generation"""
        
        # Extreme fear = buy opportunity
        if fear_greed.emotion == MarketEmotion.EXTREME_FEAR:
            return "BUY - Extreme fear presents buying opportunity (contrarian strategy)"
            
        # Extreme greed = sell signal
        if fear_greed.emotion == MarketEmotion.EXTREME_GREED:
            return "SELL - Extreme greed suggests market top (take profits)"
            
        # Capitulation = strong buy
        if any(p.pattern == PsychologyPattern.CAPITULATION for p in patterns):
            return "STRONG BUY - Capitulation event, market bottom likely near"
            
        # Euphoria = strong sell
        if any(p.pattern == PsychologyPattern.EUPHORIA for p in patterns):
            return "STRONG SELL - Euphoria detected, correction imminent"
            
        # FOMO = caution
        if any(p.pattern == PsychologyPattern.FOMO for p in patterns):
            return "HOLD/CAUTION - FOMO detected, avoid chasing pumps"
            
        # Neutral sentiment
        return "HOLD - Market sentiment neutral, wait for clearer signals"


if __name__ == "__main__":
    logger.info("Emotion AI moduli yuklandi!")
    logger.info("Fear & Greed Index, Sentiment Analysis, Psychology Patterns ready")
