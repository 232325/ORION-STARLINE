"""
Sentiment Analysis Engine - Twitter, Reddit, News API Integration
===================================================================

Bozor kayfiyatini tahlil qilish uchun sentiment analysis engine.
Social media, news va boshqa manbalardan ma'lumot to'plash va tahlil qilish.

Asosiy xususiyatlar:
- Twitter sentiment analysis
- Reddit sentiment tracking
- News sentiment extraction
- Fear & Greed index calculation
- Multi-source aggregation
- Real-time sentiment monitoring
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import Counter
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SentimentData:
    """Sentiment ma'lumotlari"""
    source: str  # 'twitter', 'reddit', 'news'
    timestamp: datetime
    text: str
    sentiment_score: float  # -1 (very negative) to +1 (very positive)
    confidence: float  # 0-1
    mentions: int  # Number of mentions/engagement
    keywords: List[str]


@dataclass
class AggregatedSentiment:
    """Aggregated sentiment"""
    timestamp: datetime
    overall_score: float  # -100 to +100
    sources: Dict[str, float]  # {'twitter': 0.5, 'reddit': 0.3, 'news': 0.7}
    volume: int  # Total mentions
    trending_keywords: List[Tuple[str, int]]
    fear_greed_index: float  # 0-100


class SentimentAnalysisEngine:
    """
    Sentiment Analysis Engine
    
    Multi-source sentiment tahlili va aggregation
    """
    
    def __init__(self):
        self.sentiment_history: List[SentimentData] = []
        self.aggregated_history: List[AggregatedSentiment] = []
        
        # Sentiment keywords (simplified - real implementation would use ML models)
        self.positive_keywords = [
            'bullish', 'moon', 'pump', 'buy', 'long', 'breakout', 'rally',
            'growth', 'profit', 'gains', 'rocket', 'green', 'up', 'surge',
            'strong', 'momentum', 'positive', 'optimistic', 'confident'
        ]
        
        self.negative_keywords = [
            'bearish', 'dump', 'sell', 'short', 'crash', 'drop', 'fall',
            'loss', 'decline', 'weak', 'red', 'down', 'plunge', 'fear',
            'negative', 'pessimistic', 'concern', 'risk', 'warning'
        ]
        
        logger.info("Sentiment Analysis Engine initialized")
    
    def analyze_text_sentiment(
        self,
        text: str
    ) -> Tuple[float, float]:
        """
        Matnni tahlil qilib sentiment score berish
        
        Args:
            text: Tahlil qilinadigan matn
            
        Returns:
            (sentiment_score, confidence)
        """
        text_lower = text.lower()
        
        # Count positive and negative keywords
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        total_keywords = positive_count + negative_count
        
        if total_keywords == 0:
            return 0.0, 0.0  # Neutral, no confidence
        
        # Calculate sentiment score
        sentiment_score = (positive_count - negative_count) / total_keywords
        
        # Confidence based on keyword density
        word_count = len(text_lower.split())
        keyword_density = total_keywords / max(word_count, 1)
        confidence = min(keyword_density * 2, 1.0)  # Cap at 1.0
        
        return sentiment_score, confidence
    
    def extract_keywords(
        self,
        text: str,
        top_n: int = 5
    ) -> List[str]:
        """
        Matndan asosiy keywords ekstraktatsiya qilish
        
        Args:
            text: Matn
            top_n: Top N keywords
            
        Returns:
            Keywords ro'yxati
        """
        # Remove special characters and split
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common words (simplified stopwords)
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'in', 'of', 'for', 'on'}
        words = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Count frequencies
        word_freq = Counter(words)
        
        # Get top N
        top_keywords = [word for word, _ in word_freq.most_common(top_n)]
        
        return top_keywords
    
    def analyze_twitter_data(
        self,
        tweets: List[Dict],
        symbol: str = 'BTC'
    ) -> List[SentimentData]:
        """
        Twitter ma'lumotlarini tahlil qilish
        
        Args:
            tweets: Twitter tweets list
                [{'text': '...', 'timestamp': ..., 'likes': ..., 'retweets': ...}]
            symbol: Asset symboli
            
        Returns:
            Sentiment data ro'yxati
        """
        sentiment_data = []
        
        for tweet in tweets:
            text = tweet.get('text', '')
            
            # Analyze sentiment
            score, confidence = self.analyze_text_sentiment(text)
            
            # Extract keywords
            keywords = self.extract_keywords(text)
            
            # Calculate engagement (mentions)
            likes = tweet.get('likes', 0)
            retweets = tweet.get('retweets', 0)
            mentions = likes + retweets * 2  # Retweets weighted higher
            
            data = SentimentData(
                source='twitter',
                timestamp=tweet.get('timestamp', datetime.now()),
                text=text,
                sentiment_score=score,
                confidence=confidence,
                mentions=mentions,
                keywords=keywords
            )
            
            sentiment_data.append(data)
            self.sentiment_history.append(data)
        
        logger.info(f"Analyzed {len(tweets)} tweets for {symbol}")
        return sentiment_data
    
    def analyze_reddit_data(
        self,
        posts: List[Dict],
        symbol: str = 'BTC'
    ) -> List[SentimentData]:
        """
        Reddit ma'lumotlarini tahlil qilish
        
        Args:
            posts: Reddit posts list
                [{'title': '...', 'text': '...', 'timestamp': ..., 'score': ..., 'comments': ...}]
            symbol: Asset symboli
            
        Returns:
            Sentiment data ro'yxati
        """
        sentiment_data = []
        
        for post in posts:
            title = post.get('title', '')
            text = post.get('text', '')
            combined_text = f"{title} {text}"
            
            # Analyze sentiment
            score, confidence = self.analyze_text_sentiment(combined_text)
            
            # Extract keywords
            keywords = self.extract_keywords(combined_text)
            
            # Calculate engagement
            upvotes = post.get('score', 0)
            comments = post.get('comments', 0)
            mentions = upvotes + comments * 3  # Comments weighted higher
            
            data = SentimentData(
                source='reddit',
                timestamp=post.get('timestamp', datetime.now()),
                text=combined_text[:200],  # Truncate
                sentiment_score=score,
                confidence=confidence,
                mentions=mentions,
                keywords=keywords
            )
            
            sentiment_data.append(data)
            self.sentiment_history.append(data)
        
        logger.info(f"Analyzed {len(posts)} Reddit posts for {symbol}")
        return sentiment_data
    
    def analyze_news_data(
        self,
        articles: List[Dict],
        symbol: str = 'BTC'
    ) -> List[SentimentData]:
        """
        News ma'lumotlarini tahlil qilish
        
        Args:
            articles: News articles list
                [{'title': '...', 'content': '...', 'timestamp': ..., 'source': '...'}]
            symbol: Asset symboli
            
        Returns:
            Sentiment data ro'yxati
        """
        sentiment_data = []
        
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', '')
            combined_text = f"{title} {content}"
            
            # Analyze sentiment
            score, confidence = self.analyze_text_sentiment(combined_text)
            
            # Extract keywords
            keywords = self.extract_keywords(combined_text)
            
            # News articles have inherent authority
            mentions = 100  # Base authority score
            
            data = SentimentData(
                source='news',
                timestamp=article.get('timestamp', datetime.now()),
                text=combined_text[:200],
                sentiment_score=score,
                confidence=confidence,
                mentions=mentions,
                keywords=keywords
            )
            
            sentiment_data.append(data)
            self.sentiment_history.append(data)
        
        logger.info(f"Analyzed {len(articles)} news articles for {symbol}")
        return sentiment_data
    
    def aggregate_sentiment(
        self,
        lookback_hours: int = 24,
        source_weights: Optional[Dict[str, float]] = None
    ) -> AggregatedSentiment:
        """
        Sentiment aggregation (barcha manbalar)
        
        Args:
            lookback_hours: Necha soat orqaga qarash
            source_weights: Source og'irliklari {'twitter': 0.3, 'reddit': 0.3, 'news': 0.4}
            
        Returns:
            Aggregated sentiment
        """
        if source_weights is None:
            source_weights = {
                'twitter': 0.3,
                'reddit': 0.3,
                'news': 0.4
            }
        
        # Filter recent data
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        recent_data = [
            d for d in self.sentiment_history
            if d.timestamp >= cutoff_time
        ]
        
        if not recent_data:
            return AggregatedSentiment(
                timestamp=datetime.now(),
                overall_score=0.0,
                sources={},
                volume=0,
                trending_keywords=[],
                fear_greed_index=50.0
            )
        
        # Aggregate by source
        source_sentiments = {}
        total_volume = 0
        all_keywords = []
        
        for source in ['twitter', 'reddit', 'news']:
            source_data = [d for d in recent_data if d.source == source]
            
            if source_data:
                # Weighted average by mentions and confidence
                weights = [d.mentions * d.confidence for d in source_data]
                scores = [d.sentiment_score for d in source_data]
                
                if sum(weights) > 0:
                    weighted_avg = np.average(scores, weights=weights)
                    source_sentiments[source] = weighted_avg
                
                # Collect volume and keywords
                total_volume += sum(d.mentions for d in source_data)
                for d in source_data:
                    all_keywords.extend(d.keywords)
        
        # Calculate overall sentiment
        overall_score = 0.0
        for source, score in source_sentiments.items():
            weight = source_weights.get(source, 0.33)
            overall_score += score * weight
        
        # Scale to -100 to +100
        overall_score *= 100
        
        # Trending keywords
        keyword_freq = Counter(all_keywords)
        trending_keywords = keyword_freq.most_common(10)
        
        # Calculate Fear & Greed Index
        fear_greed = self.calculate_fear_greed_index(
            overall_score, total_volume, len(recent_data)
        )
        
        aggregated = AggregatedSentiment(
            timestamp=datetime.now(),
            overall_score=overall_score,
            sources=source_sentiments,
            volume=total_volume,
            trending_keywords=trending_keywords,
            fear_greed_index=fear_greed
        )
        
        self.aggregated_history.append(aggregated)
        
        logger.info(f"📊 Aggregated Sentiment:")
        logger.info(f"   Overall Score: {overall_score:.2f}")
        logger.info(f"   Volume: {total_volume}")
        logger.info(f"   Fear & Greed: {fear_greed:.1f}")
        
        return aggregated
    
    def calculate_fear_greed_index(
        self,
        sentiment_score: float,
        volume: int,
        data_points: int
    ) -> float:
        """
        Fear & Greed Index hisoblash
        
        Args:
            sentiment_score: Sentiment score (-100 to +100)
            volume: Total mentions volume
            data_points: Number of data points
            
        Returns:
            Fear & Greed Index (0-100)
            0-25: Extreme Fear
            25-45: Fear
            45-55: Neutral
            55-75: Greed
            75-100: Extreme Greed
        """
        # Base on sentiment (50% weight)
        sentiment_component = (sentiment_score + 100) / 2  # Scale to 0-100
        
        # Volume component (30% weight)
        # Higher volume = higher confidence in sentiment
        avg_volume = volume / max(data_points, 1)
        volume_component = min(avg_volume / 100, 1.0) * 100
        
        # Volatility component (20% weight)
        # Higher data points = more stable
        volatility_component = min(data_points / 100, 1.0) * 100
        
        # Weighted combination
        fear_greed = (
            sentiment_component * 0.5 +
            volume_component * 0.3 +
            volatility_component * 0.2
        )
        
        return fear_greed
    
    def get_sentiment_trend(
        self,
        hours: int = 24
    ) -> Dict:
        """
        Sentiment trend tahlili
        
        Args:
            hours: Necha soat trend tahlil qilish
            
        Returns:
            Trend ma'lumotlari
        """
        if len(self.aggregated_history) < 2:
            return {
                'trend': 'neutral',
                'change': 0.0,
                'velocity': 0.0
            }
        
        # Get recent aggregated data
        recent = [a for a in self.aggregated_history[-hours:]]
        
        if len(recent) < 2:
            return {
                'trend': 'neutral',
                'change': 0.0,
                'velocity': 0.0
            }
        
        # Calculate trend
        scores = [a.overall_score for a in recent]
        
        # Linear regression for trend
        x = np.arange(len(scores))
        slope, intercept = np.polyfit(x, scores, 1)
        
        # Determine trend direction
        if slope > 2:
            trend = 'bullish'
        elif slope < -2:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        # Change from start to end
        change = scores[-1] - scores[0]
        
        # Velocity (rate of change)
        velocity = slope
        
        return {
            'trend': trend,
            'change': change,
            'velocity': velocity,
            'current_score': scores[-1],
            'previous_score': scores[0]
        }
    
    def get_sentiment_alerts(
        self,
        threshold: float = 30.0
    ) -> List[Dict]:
        """
        Sentiment alerts (extreme sentiment detection)
        
        Args:
            threshold: Alert threshold
            
        Returns:
            Alerts ro'yxati
        """
        alerts = []
        
        if not self.aggregated_history:
            return alerts
        
        latest = self.aggregated_history[-1]
        
        # Extreme positive sentiment
        if latest.overall_score > threshold:
            alerts.append({
                'type': 'extreme_greed',
                'severity': 'high',
                'message': f"Extreme positive sentiment detected: {latest.overall_score:.1f}",
                'recommendation': 'Consider taking profits or reducing exposure',
                'fear_greed_index': latest.fear_greed_index
            })
        
        # Extreme negative sentiment
        elif latest.overall_score < -threshold:
            alerts.append({
                'type': 'extreme_fear',
                'severity': 'high',
                'message': f"Extreme negative sentiment detected: {latest.overall_score:.1f}",
                'recommendation': 'Potential buying opportunity (contrarian)',
                'fear_greed_index': latest.fear_greed_index
            })
        
        # Rapid sentiment change
        if len(self.aggregated_history) >= 2:
            prev = self.aggregated_history[-2]
            change = latest.overall_score - prev.overall_score
            
            if abs(change) > 20:
                alerts.append({
                    'type': 'rapid_sentiment_shift',
                    'severity': 'medium',
                    'message': f"Rapid sentiment change: {change:+.1f} in last period",
                    'recommendation': 'Monitor closely for market volatility',
                    'change': change
                })
        
        return alerts


# Example usage
def main():
    """Test sentiment analysis engine"""
    
    print("="*60)
    print("SENTIMENT ANALYSIS ENGINE TEST")
    print("="*60)
    
    # Initialize engine
    engine = SentimentAnalysisEngine()
    
    # Mock Twitter data
    tweets = [
        {
            'text': "Bitcoin is so bullish! Going to the moon! 🚀 #BTC #crypto",
            'timestamp': datetime.now(),
            'likes': 150,
            'retweets': 45
        },
        {
            'text': "BTC looking weak. Expecting a dump soon. Bearish setup.",
            'timestamp': datetime.now(),
            'likes': 80,
            'retweets': 20
        },
        {
            'text': "Strong breakout for Bitcoin! Momentum is positive.",
            'timestamp': datetime.now(),
            'likes': 200,
            'retweets': 60
        }
    ]
    
    # Analyze Twitter
    twitter_sentiment = engine.analyze_twitter_data(tweets, 'BTC')
    
    # Mock Reddit data
    reddit_posts = [
        {
            'title': "Bitcoin rally continues!",
            'text': "The bullish momentum is strong. Great time to buy.",
            'timestamp': datetime.now(),
            'score': 350,
            'comments': 42
        }
    ]
    
    # Analyze Reddit
    reddit_sentiment = engine.analyze_reddit_data(reddit_posts, 'BTC')
    
    # Mock News data
    news_articles = [
        {
            'title': "Bitcoin hits new high",
            'content': "Positive market sentiment drives Bitcoin growth.",
            'timestamp': datetime.now(),
            'source': 'CoinDesk'
        }
    ]
    
    # Analyze News
    news_sentiment = engine.analyze_news_data(news_articles, 'BTC')
    
    # Aggregate sentiment
    aggregated = engine.aggregate_sentiment(lookback_hours=24)
    
    print(f"\n📊 Aggregated Sentiment Results:")
    print(f"Overall Score: {aggregated.overall_score:.2f}")
    print(f"Fear & Greed Index: {aggregated.fear_greed_index:.1f}")
    print(f"Total Volume: {aggregated.volume}")
    print(f"\nSource Breakdown:")
    for source, score in aggregated.sources.items():
        print(f"  {source}: {score:.2f}")
    
    print(f"\nTrending Keywords:")
    for keyword, freq in aggregated.trending_keywords[:5]:
        print(f"  {keyword}: {freq}")
    
    # Get alerts
    alerts = engine.get_sentiment_alerts(threshold=30)
    if alerts:
        print(f"\n⚠️ Sentiment Alerts:")
        for alert in alerts:
            print(f"  {alert['type']}: {alert['message']}")
            print(f"    Recommendation: {alert['recommendation']}")


if __name__ == '__main__':
    main()
