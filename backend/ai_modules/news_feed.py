"""
Real-time Yangiliklar va Sentiment Integratsiyasi Moduli
Real-time News and Sentiment Integration Module

Iqtisodiy yangiliklar, sentiment analizi va social media ma'lumotlarini integratsiya qilish
"""

import asyncio
import json
import time
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
import aiohttp
import aiofiles

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """Yangilik elementi"""
    id: str
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    symbols: List[str]
    sentiment_score: float
    importance: float
    category: str
    language: str = "en"
    views: int = 0
    shares: int = 0


@dataclass
class SocialMediaPost:
    """Ijtimoiy tarmoq posti"""
    id: str
    platform: str
    content: str
    author: str
    timestamp: datetime
    symbols: List[str]
    sentiment_score: float
    engagement: int
    reach: int
    language: str = "en"
    verified: bool = False


@dataclass
class EconomicEvent:
    """Iqtisodiy voqea"""
    id: str
    title: str
    description: str
    date: datetime
    impact_level: str  # 'HIGH', 'MEDIUM', 'LOW'
    currency: str
    country: str
    category: str
    forecast: Optional[str] = None
    previous: Optional[str] = None
    actual: Optional[str] = None
    importance: float = 0.0


@dataclass
class SentimentMetrics:
    """Sentiment metrikalari"""
    symbol: str
    overall_score: float
    news_sentiment: float
    social_sentiment: float
    technical_sentiment: float
    sentiment_trend: str
    confidence: float
    volume: int
    timestamp: datetime


class NewsProvider(ABC):
    """Yangilik provider base class"""
    
    @abstractmethod
    async def fetch_news(self, symbols: List[str] = None, limit: int = 50) -> List[NewsItem]:
        pass
    
    @abstractmethod
    async def fetch_economic_calendar(self) -> List[EconomicEvent]:
        pass


class SocialMediaProvider(ABC):
    """Ijtimoiy tarmoq provider base class"""
    
    @abstractmethod
    async def fetch_posts(self, symbols: List[str] = None, limit: int = 100) -> List[SocialMediaPost]:
        pass
    
    @abstractmethod
    async def search_mentions(self, query: str) -> List[SocialMediaPost]:
        pass


class NewsAPISource(NewsProvider):
    """NewsAPI.org integratsiyasi"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.headers = {
            'X-API-Key': api_key,
            'User-Agent': 'Orion-Starline/1.0'
        }
    
    async def fetch_news(self, symbols: List[str] = None, limit: int = 50) -> List[NewsItem]:
        try:
            async with aiohttp.ClientSession() as session:
                # Build query from symbols
                query = " OR ".join([f'"{symbol}"' for symbol in symbols]) if symbols else "finance OR market OR stock"
                
                params = {
                    'q': query,
                    'sortBy': 'publishedAt',
                    'pageSize': min(limit, 100),
                    'language': 'en',
                    'category': 'business'
                }
                
                async with session.get(f"{self.base_url}/everything", 
                                     headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_news_items(data.get('articles', []))
                    else:
                        logger.error(f"NewsAPI error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching NewsAPI: {str(e)}")
            return []
    
    def _parse_news_items(self, articles: List[Dict]) -> List[NewsItem]:
        """Yangilik elementlarini pars qilish"""
        news_items = []
        
        for article in articles:
            try:
                # Extract symbols from title and content
                symbols = self._extract_symbols(article.get('title', '') + ' ' + article.get('description', ''))
                
                news_item = NewsItem(
                    id=article.get('url', ''),
                    title=article.get('title', ''),
                    content=article.get('description', ''),
                    url=article.get('url', ''),
                    source=article.get('source', {}).get('name', 'Unknown'),
                    published_at=datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')),
                    symbols=symbols,
                    sentiment_score=0.0,  # Will be calculated later
                    importance=1.0,  # Default importance
                    category='general'
                )
                news_items.append(news_item)
            except Exception as e:
                logger.error(f"Error parsing article: {str(e)}")
        
        return news_items
    
    def _extract_symbols(self, text: str) -> List[str]:
        """Matndan trading symbol'larni ajratib olish"""
        # Common stock symbols pattern
        symbol_pattern = r'\b[A-Z]{1,5}\b'
        potential_symbols = re.findall(symbol_pattern, text.upper())
        
        # Filter common words that are not symbols
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'WITH', 'FROM', 'THIS', 'THAT', 'HAVE', 'WILL', 'BE', 'WAS', 'HAS', 'HAD', 'ARE', 'IS', 'DO', 'DID', 'CAN', 'MAY', 'MIGHT', 'COULD', 'WOULD', 'SHOULD', 'MUST', 'SHALL'}
        
        symbols = [symbol for symbol in potential_symbols if symbol not in common_words and len(symbol) >= 2]
        return list(set(symbols))[:5]  # Return unique symbols, max 5
    
    async def fetch_economic_calendar(self) -> List[EconomicEvent]:
        # NewsAPI doesn't have economic calendar
        # This is a placeholder
        return []


class FinnhubNewsProvider(NewsProvider):
    """Finnhub yangiliklar provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"
        self.headers = {}
    
    async def fetch_news(self, symbols: List[str] = None, limit: int = 50) -> List[NewsItem]:
        try:
            news_items = []
            async with aiohttp.ClientSession() as session:
                if symbols:
                    # Get news for each symbol
                    for symbol in symbols[:5]:  # Limit to 5 symbols
                        params = {
                            'symbol': symbol,
                            'token': self.api_key,
                            'category': 'general',
                            'minId': 0
                        }
                        
                        async with session.get(f"{self.base_url}/news", 
                                             params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                for article in data[:10]:  # Limit per symbol
                                    news_item = NewsItem(
                                        id=str(article.get('id', '')),
                                        title=article.get('headline', ''),
                                        content=article.get('summary', ''),
                                        url=article.get('url', ''),
                                        source=article.get('source', 'Finnhub'),
                                        published_at=datetime.fromtimestamp(article.get('datetime', 0)),
                                        symbols=[symbol],
                                        sentiment_score=0.0,
                                        importance=1.0,
                                        category='general'
                                    )
                                    news_items.append(news_item)
                else:
                    # General market news
                    params = {
                        'category': 'general',
                        'token': self.api_key
                    }
                    
                    async with session.get(f"{self.base_url}/news", 
                                         params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            for article in data[:limit]:
                                symbols = self._extract_symbols(article.get('headline', '') + ' ' + article.get('summary', ''))
                                news_item = NewsItem(
                                    id=str(article.get('id', '')),
                                    title=article.get('headline', ''),
                                    content=article.get('summary', ''),
                                    url=article.get('url', ''),
                                    source=article.get('source', 'Finnhub'),
                                    published_at=datetime.fromtimestamp(article.get('datetime', 0)),
                                    symbols=symbols,
                                    sentiment_score=0.0,
                                    importance=1.0,
                                    category='general'
                                )
                                news_items.append(news_item)
            
            return news_items
        except Exception as e:
            logger.error(f"Error fetching Finnhub news: {str(e)}")
            return []
    
    def _extract_symbols(self, text: str) -> List[str]:
        # Simple symbol extraction for Finnhub
        symbol_pattern = r'\b[A-Z]{1,5}\b'
        symbols = re.findall(symbol_pattern, text.upper())
        return [s for s in symbols if len(s) >= 2][:3]
    
    async def fetch_economic_calendar(self) -> List[EconomicEvent]:
        try:
            events = []
            async with aiohttp.ClientSession() as session:
                params = {
                    'token': self.api_key
                }
                
                # Get economic calendar
                from_time = int(time.time())
                to_time = from_time + 7 * 24 * 3600  # Next 7 days
                
                async with session.get(f"{self.base_url}/calendar/economic", 
                                     params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        for event in data.get('economicEvents', []):
                            economic_event = EconomicEvent(
                                id=str(event.get('id', '')),
                                title=event.get('title', ''),
                                description=event.get('description', ''),
                                date=datetime.fromtimestamp(event.get('time', 0)),
                                impact_level=event.get('impact', 'MEDIUM'),
                                currency=event.get('country', 'USD'),
                                country=event.get('country', 'US'),
                                category=event.get('source', 'economic'),
                                forecast=event.get('forecast'),
                                previous=event.get('actual'),
                                importance=0.8 if event.get('impact') == 'HIGH' else 0.5
                            )
                            events.append(economic_event)
            
            return events
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {str(e)}")
            return []


class TwitterProvider(SocialMediaProvider):
    """Twitter API integratsiyasi"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    async def fetch_posts(self, symbols: List[str] = None, limit: int = 100) -> List[SocialMediaPost]:
        # This is a simplified version - in production, you'd use proper OAuth
        try:
            posts = []
            
            # Simulate Twitter data for demo
            for i in range(limit):
                if symbols:
                    symbol = np.random.choice(symbols)
                else:
                    symbol = "AAPL"
                
                post = SocialMediaPost(
                    id=f"tweet_{i}",
                    platform="twitter",
                    content=f"${symbol} is looking good today! Great earnings potential.",
                    author=f"trader_{i}",
                    timestamp=datetime.now() - timedelta(minutes=i*5),
                    symbols=[symbol],
                    sentiment_score=np.random.uniform(-1, 1),
                    engagement=np.random.randint(1, 1000),
                    reach=np.random.randint(100, 10000),
                    verified=np.random.choice([True, False])
                )
                posts.append(post)
            
            return posts
        except Exception as e:
            logger.error(f"Error fetching Twitter data: {str(e)}")
            return []
    
    async def search_mentions(self, query: str) -> List[SocialMediaPost]:
        # Simulate search results
        return await self.fetch_posts(limit=20)


class RedditProvider(SocialMediaProvider):
    """Reddit API integratsiyasi"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.base_url = "https://www.reddit.com"
        self.headers = {
            'User-Agent': user_agent
        }
    
    async def fetch_posts(self, symbols: List[str] = None, limit: int = 100) -> List[SocialMediaPost]:
        try:
            posts = []
            
            # Simulate Reddit data for demo
            subreddits = ['wallstreetbets', 'stocks', 'investing', 'securityanalysis']
            
            for i in range(limit):
                if symbols:
                    symbol = np.random.choice(symbols)
                else:
                    symbol = "AAPL"
                
                subreddit = np.random.choice(subreddits)
                
                post = SocialMediaPost(
                    id=f"reddit_{i}",
                    platform="reddit",
                    content=f"Just bought more ${symbol}! Bullish on this one. DD in comments.",
                    author=f"redditor_{i}",
                    timestamp=datetime.now() - timedelta(hours=i),
                    symbols=[symbol],
                    sentiment_score=np.random.uniform(-1, 1),
                    engagement=np.random.randint(1, 500),
                    reach=np.random.randint(50, 5000),
                    verified=False
                )
                posts.append(post)
            
            return posts
        except Exception as e:
            logger.error(f"Error fetching Reddit data: {str(e)}")
            return []
    
    async def search_mentions(self, query: str) -> List[SocialMediaPost]:
        return await self.fetch_posts(limit=20)


class SentimentAnalyzer:
    """Sentiment tahlilchi"""
    
    def __init__(self):
        # Simple sentiment keywords
        self.positive_words = {
            'bullish', 'up', 'rise', 'gain', 'profit', 'good', 'great', 'excellent', 
            'strong', 'buy', 'long', 'moon', 'pump', 'rally', 'growth', 'increase'
        }
        
        self.negative_words = {
            'bearish', 'down', 'fall', 'loss', 'bad', 'terrible', 'weak', 'sell',
            'short', 'dump', 'crash', 'decline', 'decrease', 'drop', 'fail', 'lose'
        }
        
        # Financial sentiment words
        self.financial_positive = {
            'earnings', 'revenue', 'dividend', 'guidance', 'beat', 'exceed',
            'outperform', 'upgrade', 'buy', 'overweight', 'target'
        }
        
        self.financial_negative = {
            'miss', 'underperform', 'downgrade', 'sell', 'underweight', 'target'
        }
    
    def analyze_text(self, text: str) -> float:
        """Matn uchun sentiment ballini hisoblash"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_score = 0
        negative_score = 0
        
        for word in words:
            if word in self.positive_words or word in self.financial_positive:
                positive_score += 1
            elif word in self.negative_words or word in self.financial_negative:
                negative_score += 1
        
        if positive_score + negative_score == 0:
            return 0.0
        
        # Normalize to -1 to 1 range
        total_words = positive_score + negative_score
        sentiment = (positive_score - negative_score) / total_words
        return max(-1.0, min(1.0, sentiment))
    
    def analyze_news_item(self, news_item: NewsItem) -> NewsItem:
        """Yangilik elementi uchun sentiment analizi"""
        # Combine title and content for analysis
        text = f"{news_item.title} {news_item.content}"
        sentiment_score = self.analyze_text(text)
        
        # Update importance based on sentiment and source
        importance = 1.0
        if abs(sentiment_score) > 0.5:  # Strong sentiment
            importance = 1.5
        if news_item.source in ['Reuters', 'Bloomberg', 'Financial Times']:
            importance *= 1.2  # High-quality sources
        
        news_item.sentiment_score = sentiment_score
        news_item.importance = min(importance, 2.0)  # Cap importance
        
        return news_item
    
    def analyze_social_post(self, post: SocialMediaPost) -> SocialMediaPost:
        """Ijtimoiy tarmoq posti uchun sentiment analizi"""
        sentiment_score = self.analyze_text(post.content)
        
        # Adjust sentiment based on engagement
        if post.engagement > 500:
            sentiment_score *= 1.1  # High engagement amplifies sentiment
        if post.verified:
            sentiment_score *= 1.05  # Verified accounts have slightly more weight
        
        post.sentiment_score = max(-1.0, min(1.0, sentiment_score))
        return post
    
    def calculate_symbol_sentiment(self, symbols: List[str], news_items: List[NewsItem], 
                                 social_posts: List[SocialMediaPost]) -> Dict[str, SentimentMetrics]:
        """Symbol bo'yicha sentiment metrikalari"""
        symbol_sentiments = {}
        
        for symbol in symbols:
            # Filter data for this symbol
            symbol_news = [item for item in news_items if symbol in item.symbols]
            symbol_posts = [post for post in social_posts if symbol in post.symbols]
            
            if not symbol_news and not symbol_posts:
                continue
            
            # Calculate sentiment scores
            news_sentiment = np.mean([item.sentiment_score for item in symbol_news]) if symbol_news else 0.0
            social_sentiment = np.mean([post.sentiment_score for post in symbol_posts]) if symbol_posts else 0.0
            
            # Simple technical sentiment (placeholder)
            technical_sentiment = 0.0  # Would calculate from price data
            
            # Overall sentiment (weighted average)
            overall_sentiment = (news_sentiment * 0.4 + social_sentiment * 0.4 + technical_sentiment * 0.2)
            
            # Determine trend
            if overall_sentiment > 0.2:
                trend = "POSITIVE"
            elif overall_sentiment < -0.2:
                trend = "NEGATIVE"
            else:
                trend = "NEUTRAL"
            
            # Calculate confidence based on data volume
            total_items = len(symbol_news) + len(symbol_posts)
            confidence = min(1.0, total_items / 20)  # Full confidence at 20+ items
            
            metrics = SentimentMetrics(
                symbol=symbol,
                overall_score=overall_sentiment,
                news_sentiment=news_sentiment,
                social_sentiment=social_sentiment,
                technical_sentiment=technical_sentiment,
                sentiment_trend=trend,
                confidence=confidence,
                volume=total_items,
                timestamp=datetime.now()
            )
            
            symbol_sentiments[symbol] = metrics
        
        return symbol_sentiments


class NewsFeedManager:
    """Yangilik va sentiment boshqaruvchisi"""
    
    def __init__(self):
        self.news_providers = {}
        self.social_providers = {}
        self.sentiment_analyzer = SentimentAnalyzer()
        self.news_cache = {}
        self.social_cache = {}
        self.sentiment_cache = {}
        
        # Setup providers
        self._setup_providers()
    
    def _setup_providers(self):
        """Provider'larni sozlash"""
        # News providers
        self.news_providers['newsapi'] = NewsAPISource("demo_key")
        self.news_providers['finnhub'] = FinnhubNewsProvider("demo_key")
        
        # Social media providers
        self.social_providers['twitter'] = TwitterProvider(
            "demo_key", "demo_secret", "demo_token", "demo_secret"
        )
        self.social_providers['reddit'] = RedditProvider(
            "demo_client", "demo_secret", "Orion-Starline/1.0"
        )
    
    async def fetch_latest_news(self, symbols: List[str] = None, limit: int = 50) -> List[NewsItem]:
        """So'nggi yangiliklarni olish"""
        all_news = []
        
        # Fetch from all news providers
        tasks = []
        for name, provider in self.news_providers.items():
            task = asyncio.create_task(
                self._safe_provider_call(provider.fetch_news, symbols, limit)
            )
            tasks.append(task)
        
        # Collect results
        for task in tasks:
            try:
                news_items = await task
                for item in news_items:
                    # Analyze sentiment
                    item = self.sentiment_analyzer.analyze_news_item(item)
                all_news.extend(news_items)
            except Exception as e:
                logger.error(f"Error fetching news from provider: {str(e)}")
        
        # Sort by importance and timestamp
        all_news.sort(key=lambda x: (x.importance, x.published_at), reverse=True)
        
        # Cache the results
        cache_key = f"news_{'-'.join(symbols or [])}"
        self.news_cache[cache_key] = {
            'items': all_news,
            'timestamp': datetime.now()
        }
        
        return all_news[:limit]
    
    async def fetch_social_sentiment(self, symbols: List[str] = None, limit: int = 100) -> List[SocialMediaPost]:
        """Ijtimoiy tarmoq sentimentini olish"""
        all_posts = []
        
        # Fetch from all social providers
        tasks = []
        for name, provider in self.social_providers.items():
            task = asyncio.create_task(
                self._safe_provider_call(provider.fetch_posts, symbols, limit)
            )
            tasks.append(task)
        
        # Collect results
        for task in tasks:
            try:
                posts = await task
                for post in posts:
                    # Analyze sentiment
                    post = self.sentiment_analyzer.analyze_social_post(post)
                all_posts.extend(posts)
            except Exception as e:
                logger.error(f"Error fetching social data: {str(e)}")
        
        # Sort by engagement
        all_posts.sort(key=lambda x: x.engagement, reverse=True)
        
        # Cache the results
        cache_key = f"social_{'-'.join(symbols or [])}"
        self.social_cache[cache_key] = {
            'items': all_posts,
            'timestamp': datetime.now()
        }
        
        return all_posts[:limit]
    
    async def fetch_economic_calendar(self) -> List[EconomicEvent]:
        """Iqtisodiy kalendar ma'lumotlari"""
        all_events = []
        
        # Fetch from all providers that support economic calendar
        tasks = []
        for name, provider in self.news_providers.items():
            if hasattr(provider, 'fetch_economic_calendar'):
                task = asyncio.create_task(
                    self._safe_provider_call(provider.fetch_economic_calendar)
                )
                tasks.append(task)
        
        # Collect results
        for task in tasks:
            try:
                events = await task
                all_events.extend(events)
            except Exception as e:
                logger.error(f"Error fetching economic calendar: {str(e)}")
        
        # Sort by date
        all_events.sort(key=lambda x: x.date)
        
        return all_events
    
    async def get_comprehensive_sentiment(self, symbols: List[str]) -> Dict[str, SentimentMetrics]:
        """Keng qamrovli sentiment analizi"""
        # Fetch news and social data
        news_items = await self.fetch_latest_news(symbols, limit=100)
        social_posts = await self.fetch_social_sentiment(symbols, limit=200)
        
        # Calculate sentiment metrics for each symbol
        sentiment_metrics = self.sentiment_analyzer.calculate_symbol_sentiment(
            symbols, news_items, social_posts
        )
        
        # Cache the results
        cache_key = f"sentiment_{'-'.join(symbols)}"
        self.sentiment_cache[cache_key] = {
            'metrics': sentiment_metrics,
            'news_count': len(news_items),
            'social_count': len(social_posts),
            'timestamp': datetime.now()
        }
        
        return sentiment_metrics
    
    async def get_news_summary(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Yangiliklar xulosasi"""
        news_items = await self.fetch_latest_news(symbols, limit=20)
        
        if not news_items:
            return {'summary': 'No recent news found', 'articles': []}
        
        # Calculate summary statistics
        total_articles = len(news_items)
        positive_articles = len([n for n in news_items if n.sentiment_score > 0.1])
        negative_articles = len([n for n in news_items if n.sentiment_score < -0.1])
        neutral_articles = total_articles - positive_articles - negative_articles
        
        avg_sentiment = np.mean([n.sentiment_score for n in news_items])
        
        # Get top sources
        sources = {}
        for item in news_items:
            sources[item.source] = sources.get(item.source, 0) + 1
        
        top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]
        
        summary = {
            'total_articles': total_articles,
            'sentiment_breakdown': {
                'positive': positive_articles,
                'negative': negative_articles,
                'neutral': neutral_articles
            },
            'average_sentiment': avg_sentiment,
            'top_sources': top_sources,
            'recent_articles': [
                {
                    'title': item.title,
                    'source': item.source,
                    'sentiment': item.sentiment_score,
                    'published_at': item.published_at,
                    'url': item.url
                }
                for item in news_items[:10]
            ]
        }
        
        return summary
    
    async def _safe_provider_call(self, func, *args, **kwargs):
        """Xavfsiz provider chaqiruvi"""
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return await asyncio.to_thread(func, *args, **kwargs)
        except Exception as e:
            logger.error(f"Provider call error: {str(e)}")
            return [] if 'fetch' in str(func) else None
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Cache holatini olish"""
        return {
            'news_cache_size': len(self.news_cache),
            'social_cache_size': len(self.social_cache),
            'sentiment_cache_size': len(self.sentiment_cache),
            'news_cache': {
                k: {
                    'items_count': len(v['items']),
                    'timestamp': v['timestamp']
                }
                for k, v in self.news_cache.items()
            },
            'social_cache': {
                k: {
                    'items_count': len(v['items']),
                    'timestamp': v['timestamp']
                }
                for k, v in self.social_cache.items()
            }
        }


# Demo usage
async def demo_news_feed():
    """Yangilik feed demo"""
    print("=== Real-time Yangiliklar va Sentiment Demo ===")
    
    manager = NewsFeedManager()
    
    # Test symbols
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    
    print(f"\n=== {symbols} uchun sentiment analizi ===")
    sentiment_data = await manager.get_comprehensive_sentiment(symbols)
    for symbol, metrics in sentiment_data.items():
        print(f"{symbol}:")
        print(f"  Sentiment: {metrics.overall_score:.3f} ({metrics.sentiment_trend})")
        print(f"  News: {metrics.news_sentiment:.3f}, Social: {metrics.social_sentiment:.3f}")
        print(f"  Confidence: {metrics.confidence:.2f}, Volume: {metrics.volume}")
        print()
    
    print(f"\n=== Yangiliklar xulosasi ===")
    news_summary = await manager.get_news_summary(symbols)
    print(json.dumps(news_summary, indent=2, default=str))
    
    print(f"\n=== Iqtisodiy kalendar ===")
    economic_events = await manager.fetch_economic_calendar()
    for event in economic_events[:5]:
        print(f"{event.title} - {event.date} ({event.impact_level})")
    
    print(f"\n=== Cache holati ===")
    cache_status = manager.get_cache_status()
    print(json.dumps(cache_status, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(demo_news_feed())