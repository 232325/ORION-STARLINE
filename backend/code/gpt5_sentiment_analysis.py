"""
GPT-5 Sentiment Analysis System
Bu tizim OpenAI GPT-5 API yordamida bozor sentimentini tahlil qiladi
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
import aiohttp
import websockets
from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks
from pydantic import BaseModel
import uvicorn

# Konfiguratsiya
from config import *

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === ENUMS VA CONSTANTS ===

class AssetClass(Enum):
    """Aktiv turi"""
    STOCK = "stock"
    FOREX = "forex"
    METALS = "metals"

class SentimentType(Enum):
    """Sentiment turi"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class DataSource(Enum):
    """Ma'lumot manbai"""
    NEWS = "news"
    TWITTER = "twitter"
    REDDIT = "reddit"
    EARNINGS = "earnings"
    ANALYST_REPORT = "analyst_report"

# === MODELS ===

@dataclass
class SentimentScore:
    """Sentiment hisoblari"""
    bullish_probability: float  # 0-1
    bearish_probability: float  # 0-1
    confidence: float  # 0-1
    sentiment_type: SentimentType
    overall_score: float  # -1 (bearish) to 1 (bullish)
    
    def to_dict(self) -> Dict:
        return {
            'bullish_probability': self.bullish_probability,
            'bearish_probability': self.bearish_probability,
            'confidence': self.confidence,
            'sentiment_type': self.sentiment_type.value,
            'overall_score': self.overall_score
        }

@dataclass
class MarketData:
    """Bozor ma'lumotlari"""
    symbol: str
    asset_class: AssetClass
    timestamp: datetime
    price: float
    volume: int
    news_count: int
    sentiment_data: Optional[SentimentScore] = None
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'asset_class': self.asset_class.value,
            'timestamp': self.timestamp.isoformat(),
            'price': self.price,
            'volume': self.volume,
            'news_count': self.news_count,
            'sentiment_data': self.sentiment_data.to_dict() if self.sentiment_data else None
        }

@dataclass
class NewsItem:
    """Yangilik elementi"""
    id: str
    title: str
    content: str
    source: str
    url: str
    timestamp: datetime
    symbols: List[str]
    source_type: DataSource
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'url': self.url,
            'timestamp': self.timestamp.isoformat(),
            'symbols': self.symbols,
            'source_type': self.source_type.value
        }

@dataclass
class SentimentAnalysisResult:
    """Sentiment tahlil natijasi"""
    news_id: str
    symbol: str
    sentiment: SentimentScore
    key_factors: List[str]
    confidence_breakdown: Dict[str, float]
    processing_time: float
    
    def to_dict(self) -> Dict:
        return {
            'news_id': self.news_id,
            'symbol': self.symbol,
            'sentiment': self.sentiment.to_dict(),
            'key_factors': self.key_factors,
            'confidence_breakdown': self.confidence_breakdown,
            'processing_time': self.processing_time
        }

# === GPT-5 API INTEGRATION ===

class GPT5API:
    """GPT-5 API bilan ishlash"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
        self.rate_limit = 60  # requests per minute
        self.request_times = deque(maxlen=self.rate_limit)
        self.cache = {}  # Response caching
        self.cost_tracker = 0.0
        
    def _check_rate_limit(self):
        """Rate limiting tekshirish"""
        now = time.time()
        # Eski so'rovlarni o'chirish
        while self.request_times and now - self.request_times[0] > 60:
            self.request_times.popleft()
            
        if len(self.request_times) >= self.rate_limit:
            sleep_time = 60 - (now - self.request_times[0]) + 1
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                
        self.request_times.append(now)
    
    def _cache_key(self, text: str) -> str:
        """Cache kaliti yaratish"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _get_cached_response(self, text: str) -> Optional[Dict]:
        """Cache'dan javob olish"""
        cache_key = self._cache_key(text)
        return self.cache.get(cache_key)
    
    def _store_cached_response(self, text: str, response: Dict):
        """Javobni cache'da saqlash"""
        cache_key = self._cache_key(text)
        if len(self.cache) > 1000:  # Cache limit
            # Eng eski elementni o'chirish
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[cache_key] = response
    
    async def analyze_sentiment(self, text: str, symbol: str) -> SentimentAnalysisResult:
        """Matn sentimentini tahlil qilish"""
        start_time = time.time()
        
        # Cache tekshirish
        cached = self._get_cached_response(text)
        if cached:
            logger.info(f"Cache hit for text: {symbol}")
            processing_time = time.time() - start_time
            return SentimentAnalysisResult(
                news_id=cached['news_id'],
                symbol=symbol,
                sentiment=SentimentScore(
                    bullish_probability=cached['sentiment']['bullish_probability'],
                    bearish_probability=cached['sentiment']['bearish_probability'],
                    confidence=cached['sentiment']['confidence'],
                    sentiment_type=SentimentType(cached['sentiment']['sentiment_type']),
                    overall_score=cached['sentiment']['overall_score']
                ),
                key_factors=cached['key_factors'],
                confidence_breakdown=cached['confidence_breakdown'],
                processing_time=processing_time
            )
        
        # Rate limit tekshirish
        self._check_rate_limit()
        
        prompt = f"""
        Bozor sentimentini tahlil qiling. 
        
        Aktiv: {symbol}
        Matn: {text}
        
        Quyidagi JSON formatda javob bering:
        {{
            "bullish_probability": 0.0,
            "bearish_probability": 0.0,
            "confidence": 0.0,
            "sentiment_type": "bullish|bearish|neutral",
            "overall_score": 0.0,
            "key_factors": ["faktor1", "faktor2"],
            "confidence_breakdown": {{
                "technical": 0.0,
                "fundamental": 0.0,
                "news_impact": 0.0,
                "market_sentiment": 0.0
            }}
        }}
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "gpt-5",
                    "messages": [
                        {"role": "system", "content": "Siz bozor sentimentini tahlil qilish bo'yicha ekspertsiz."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                }
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(f"{self.base_url}/chat/completions", 
                                      headers=headers, 
                                      json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"API xatosi: {response.status}")
                    
                    result = await response.json()
                    
                    # Narx kuzatuvi (approximate)
                    estimated_cost = len(text) * 0.0001  # Token asosida
                    self.cost_tracker += estimated_cost
                    
                    # JSON parsing
                    content = result['choices'][0]['message']['content']
                    try:
                        analysis_data = json.loads(content)
                    except json.JSONDecodeError:
                        # Fallback parsing
                        analysis_data = self._extract_json_from_text(content)
                    
                    # Cache saqlash
                    cached_data = {
                        'news_id': f"cached_{symbol}_{self._cache_key(text)}",
                        'sentiment': analysis_data,
                        'key_factors': analysis_data.get('key_factors', []),
                        'confidence_breakdown': analysis_data.get('confidence_breakdown', {})
                    }
                    self._store_cached_response(text, cached_data)
                    
                    processing_time = time.time() - start_time
                    
                    return SentimentAnalysisResult(
                        news_id=f"analyzed_{symbol}_{int(time.time())}",
                        symbol=symbol,
                        sentiment=SentimentScore(
                            bullish_probability=analysis_data['bullish_probability'],
                            bearish_probability=analysis_data['bearish_probability'],
                            confidence=analysis_data['confidence'],
                            sentiment_type=SentimentType(analysis_data['sentiment_type']),
                            overall_score=analysis_data['overall_score']
                        ),
                        key_factors=analysis_data.get('key_factors', []),
                        confidence_breakdown=analysis_data.get('confidence_breakdown', {}),
                        processing_time=processing_time
                    )
                    
        except Exception as e:
            logger.error(f"Sentiment analysis xatosi: {e}")
            # Fallback javob
            processing_time = time.time() - start_time
            return SentimentAnalysisResult(
                news_id=f"error_{symbol}_{int(time.time())}",
                symbol=symbol,
                sentiment=SentimentScore(
                    bullish_probability=0.5,
                    bearish_probability=0.5,
                    confidence=0.0,
                    sentiment_type=SentimentType.NEUTRAL,
                    overall_score=0.0
                ),
                key_factors=["Xato sababli tahlil qilinmadi"],
                confidence_breakdown={},
                processing_time=processing_time
            )
    
    def _extract_json_from_text(self, text: str) -> Dict:
        """Text'dan JSON extraction"""
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback
        return {
            "bullish_probability": 0.5,
            "bearish_probability": 0.5,
            "confidence": 0.0,
            "sentiment_type": "neutral",
            "overall_score": 0.0,
            "key_factors": [],
            "confidence_breakdown": {}
        }

# === DATA SOURCES ===

class NewsDataSource:
    """Yangiliklar manbasi"""
    
    def __init__(self):
        self.rss_feeds = {
            'bloomberg': 'https://feeds.bloomberg.com/markets',
            'reuters': 'https://feeds.reuters.com/reuters/businessNews',
            'cnbc': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/'
        }
        
    async def fetch_news(self, symbols: List[str]) -> List[NewsItem]:
        """Yangiliklarni olish"""
        news_items = []
        
        # Simulated news fetching - haqiqiy implementatsiyada RSS API'lar ishlatiladi
        for i, symbol in enumerate(symbols):
            # Mock news data
            news_item = NewsItem(
                id=f"news_{symbol}_{i}",
                title=f"{symbol} uchun muhim yangiliklar",
                content=f"{symbol} aktiviga tegishli bozor yangiliklari va tahlillar",
                source="Mock News Source",
                url=f"https://example.com/news/{symbol}/{i}",
                timestamp=datetime.now() - timedelta(minutes=i*30),
                symbols=[symbol],
                source_type=DataSource.NEWS
            )
            news_items.append(news_item)
            
        return news_items

class SocialMediaDataSource:
    """Ijtimoiy tarmoq ma'lumotlari"""
    
    def __init__(self):
        self.twitter_api_base = "https://api.twitter.com/2"
        self.reddit_api_base = "https://www.reddit.com/r/wallstreetbets"
    
    async def fetch_social_sentiment(self, symbols: List[str]) -> List[NewsItem]:
        """Ijtimoiy tarmoqlardan ma'lumot olish"""
        social_items = []
        
        for symbol in symbols:
            # Mock social media data
            news_item = NewsItem(
                id=f"social_{symbol}",
                title=f"{symbol} - Ijtimoiy tarmoq sentimenti",
                content=f"{symbol} aktiviga tegishli ijtimoiy tarmoq munosabatlari",
                source="Twitter/Reddit",
                url=f"https://twitter.com/search/{symbol}",
                timestamp=datetime.now(),
                symbols=[symbol],
                source_type=DataSource.TWITTER
            )
            social_items.append(news_item)
            
        return social_items

class EarningsDataSource:
    """Daromadlar hisobotlari manbasi"""
    
    async def fetch_earnings_data(self, symbols: List[str]) -> List[NewsItem]:
        """Daromadlar ma'lumotlari"""
        earnings_items = []
        
        for symbol in symbols:
            # Mock earnings data
            news_item = NewsItem(
                id=f"earnings_{symbol}",
                title=f"{symbol} - Choraklik hisobot",
                content=f"{symbol} kompaniyasining choraklik natijalari va rahbariyat izohi",
                source="Earnings Call",
                url=f"https://investor.relations/{symbol}/earnings",
                timestamp=datetime.now() - timedelta(days=7),
                symbols=[symbol],
                source_type=DataSource.EARNINGS
            )
            earnings_items.append(news_item)
            
        return earnings_items

# === SENTIMENT AGGREGATOR ===

class SentimentAggregator:
    """Sentiment agregatori va tahlilchi"""
    
    def __init__(self):
        self.moving_window = 24  # Soat
        self.weight_factors = {
            DataSource.NEWS: 0.4,
            DataSource.TWITTER: 0.2,
            DataSource.REDDIT: 0.1,
            DataSource.EARNINGS: 0.2,
            DataSource.ANALYST_REPORT: 0.1
        }
        
    def calculate_market_sentiment(self, sentiments: List[SentimentScore]) -> SentimentScore:
        """Bozor sentimentini hisoblash"""
        if not sentiments:
            return SentimentScore(
                bullish_probability=0.5,
                bearish_probability=0.5,
                confidence=0.0,
                sentiment_type=SentimentType.NEUTRAL,
                overall_score=0.0
            )
        
        weighted_bullish = 0.0
        weighted_bearish = 0.0
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for sentiment in sentiments:
            weight = 1.0  # Barobar og'irlik
            weighted_bullish += sentiment.bullish_probability * weight
            weighted_bearish += sentiment.bearish_probability * weight
            weighted_confidence += sentiment.confidence * weight
            total_weight += weight
            
        if total_weight > 0:
            avg_bullish = weighted_bullish / total_weight
            avg_bearish = weighted_bearish / total_weight
            avg_confidence = weighted_confidence / total_weight
        else:
            avg_bullish = avg_bearish = avg_confidence = 0.5
            
        # Overall score hisoblash
        overall_score = avg_bullish - avg_bearish
        
        # Sentiment type belgilash
        if overall_score > 0.1:
            sentiment_type = SentimentType.BULLISH
        elif overall_score < -0.1:
            sentiment_type = SentimentType.BEARISH
        else:
            sentiment_type = SentimentType.NEUTRAL
            
        return SentimentScore(
            bullish_probability=avg_bullish,
            bearish_probability=avg_bearish,
            confidence=avg_confidence,
            sentiment_type=sentiment_type,
            overall_score=overall_score
        )
    
    def _get_source_weight(self, analysis: SentimentAnalysisResult) -> float:
        """Manba og'irlik ko'rsatkichini olish"""
        # Bu yerda news_id dan source_type aniqlanadi
        # Hozircha barobar og'irlik
        return 1.0
    
    def detect_sentiment_momentum(self, sentiment_history: List[SentimentScore]) -> Dict[str, float]:
        """Sentiment momentum aniqlash"""
        if len(sentiment_history) < 2:
            return {"momentum": 0.0, "acceleration": 0.0}
        
        recent_scores = [s.overall_score for s in sentiment_history[-5:]]
        
        # Moving average
        current_ma = sum(recent_scores) / len(recent_scores)
        previous_ma = sum(sentiment_history[-10:-5]) / min(5, len(sentiment_history[-10:-5]))
        
        momentum = current_ma - previous_ma
        
        # Acceleration (ikkinchi hosila)
        if len(recent_scores) >= 3:
            acceleration = (recent_scores[-1] - 2*recent_scores[-2] + recent_scores[-3])
        else:
            acceleration = 0.0
            
        return {
            "momentum": momentum,
            "acceleration": acceleration,
            "trend_direction": "bullish" if momentum > 0 else "bearish" if momentum < 0 else "neutral"
        }
    
    def detect_contrarian_signals(self, analyses: List[Any], 
                                market_price_change: float, 
                                sentiment_score: SentimentScore) -> Dict[str, Any]:
        """Kontrarian signallarni aniqlash"""
        signals = []
        
        # Yuqori bozor sentimenti, lekin narx pasayishi
        if sentiment_score.sentiment_type == SentimentType.BULLISH and market_price_change < 0:
            signals.append("Yuqori bullish sentiment narx pasayishida - potential contrarian sell signal")
            
        # Past sentiment lekin narx o'sishi
        if sentiment_score.sentiment_type == SentimentType.BEARISH and market_price_change > 0:
            signals.append("Past bearish sentiment narx o'sishida - potential contrarian buy signal")
            
        # Aşırı extreme sentiment
        if sentiment_score.bullish_probability > 0.8 or sentiment_score.bearish_probability > 0.8:
            confidence_level = max(sentiment_score.bullish_probability, sentiment_score.bearish_probability)
            signals.append(f"Aşırı extreme sentiment ({confidence_level:.2f}) - potential reversal signal")
            
        return {
            "contrarian_signals": signals,
            "signal_strength": len(signals),
            "recommendation": self._get_contrarian_recommendation(signals)
        }
    
    def _get_contrarian_recommendation(self, signals: List[str]) -> str:
        """Kontrarian tavsiya berish"""
        if not signals:
            return "No contrarian signals detected"
            
        bullish_signals = [s for s in signals if "buy" in s.lower()]
        bearish_signals = [s for s in signals if "sell" in s.lower()]
        
        if bullish_signals:
            return "Consider contrarian sell position"
        elif bearish_signals:
            return "Consider contrarian buy position"
        else:
            return "Mixed contrarian signals - wait for clearer direction"

# === DATABASE ===

class SentimentDatabase:
    """Sentiment ma'lumotlar bazasi"""
    
    def __init__(self, db_path: str = "sentiment_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Ma'lumotlar bazasini yaratish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sentiment results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sentiment_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id TEXT UNIQUE,
                symbol TEXT,
                timestamp DATETIME,
                bullish_probability REAL,
                bearish_probability REAL,
                confidence REAL,
                sentiment_type TEXT,
                overall_score REAL,
                key_factors TEXT,
                confidence_breakdown TEXT,
                processing_time REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Market data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                asset_class TEXT,
                timestamp DATETIME,
                price REAL,
                volume INTEGER,
                news_count INTEGER,
                overall_sentiment REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # News items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_items (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                source TEXT,
                url TEXT,
                timestamp DATETIME,
                symbols TEXT,
                source_type TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_sentiment_result(self, result: SentimentAnalysisResult):
        """Sentiment natijasini saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sentiment_results 
            (news_id, symbol, timestamp, bullish_probability, bearish_probability, 
             confidence, sentiment_type, overall_score, key_factors, confidence_breakdown, processing_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.news_id,
            result.symbol,
            datetime.now(),
            result.sentiment.bullish_probability,
            result.sentiment.bearish_probability,
            result.sentiment.confidence,
            result.sentiment.sentiment_type.value,
            result.sentiment.overall_score,
            json.dumps(result.key_factors),
            json.dumps(result.confidence_breakdown),
            result.processing_time
        ))
        
        conn.commit()
        conn.close()
    
    def save_market_data(self, data: MarketData):
        """Bozor ma'lumotlarini saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO market_data 
            (symbol, asset_class, timestamp, price, volume, news_count, overall_sentiment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.symbol,
            data.asset_class.value,
            data.timestamp,
            data.price,
            data.volume,
            data.news_count,
            data.sentiment_data.overall_score if data.sentiment_data else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_sentiment_history(self, symbol: str, days: int = 7) -> List[Dict]:
        """Sentiment tarixini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sentiment_results 
            WHERE symbol = ? AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp DESC
        """.format(days), (symbol,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results

# === MAIN SENTIMENT ANALYSIS SYSTEM ===

class GPT5SentimentSystem:
    """Asosiy GPT-5 sentiment tahlil tizimi"""
    
    def __init__(self, openai_api_key: str):
        self.gpt5_api = GPT5API(openai_api_key)
        self.news_source = NewsDataSource()
        self.social_source = SocialMediaDataSource()
        self.earnings_source = EarningsDataSource()
        self.aggregator = SentimentAggregator()
        self.database = SentimentDatabase()
        
        # Asset configurations
        self.stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
        self.forex_pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF"]
        self.metals = ["XAU/USD", "XAG/USD", "XPT/USD", "XPD/USD"]
        
        self.all_assets = {
            AssetClass.STOCK: self.stocks,
            AssetClass.FOREX: self.forex_pairs,
            AssetClass.METALS: self.metals
        }
        
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def process_all_assets(self) -> Dict[str, MarketData]:
        """Barcha aktivlar uchun sentiment tahlili"""
        results = {}
        
        # Parallel processing
        tasks = []
        for asset_class, symbols in self.all_assets.items():
            for symbol in symbols:
                task = self.process_single_asset(symbol, asset_class)
                tasks.append(task)
        
        # Execute all tasks
        asset_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, (asset_class, symbol) in enumerate([(ac, s) for ac, symbols in self.all_assets.items() for s in symbols]):
            if isinstance(asset_results[i], Exception):
                logger.error(f"Error processing {symbol}: {asset_results[i]}")
                continue
                
            results[symbol] = asset_results[i]
            
        return results
    
    async def process_single_asset(self, symbol: str, asset_class: AssetClass) -> MarketData:
        """Bitta aktiv uchun to'liq sentiment tahlili"""
        logger.info(f"Processing {symbol} ({asset_class.value})")
        
        # Ma'lumot manbalarini parallel olish
        news_task = self.news_source.fetch_news([symbol])
        social_task = self.social_source.fetch_social_sentiment([symbol])
        earnings_task = self.earnings_source.fetch_earnings_data([symbol])
        
        news_items, social_items, earnings_items = await asyncio.gather(
            news_task, social_task, earnings_task
        )
        
        # Barcha ma'lumotlarni birlashtirish
        all_items = news_items + social_items + earnings_items
        
        # Sentiment tahlilini parallel bajarish
        sentiment_tasks = []
        for item in all_items:
            task = self.gpt5_api.analyze_sentiment(item.content, symbol)
            sentiment_tasks.append(task)
        
        # Tahlil natijalarini kutish
        sentiment_results = await asyncio.gather(*sentiment_tasks)
        
        # Natijalarni saqlash
        for result in sentiment_results:
            self.database.save_sentiment_result(result)
        
        # Umumiy sentiment hisoblash
        aggregated_sentiment = self.aggregator.calculate_market_sentiment(sentiment_results)
        
        # Kontrarian signallar
        mock_price_change = 0.0  # Haqiqiy narx ma'lumotlari uchun
        contrarian_signals = self.aggregator.detect_contrarian_signals(
            sentiment_results, mock_price_change, aggregated_sentiment
        )
        
        # Bozor ma'lumotlarini yaratish
        market_data = MarketData(
            symbol=symbol,
            asset_class=asset_class,
            timestamp=datetime.now(),
            price=100.0 + (hash(symbol) % 100),  # Mock price
            volume=1000000 + (hash(symbol) % 100000),  # Mock volume
            news_count=len(all_items),
            sentiment_data=aggregated_sentiment
        )
        
        # Ma'lumotlar bazasiga saqlash
        self.database.save_market_data(market_data)
        
        logger.info(f"Completed processing {symbol}: {aggregated_sentiment.sentiment_type.value} "
                   f"(confidence: {aggregated_sentiment.confidence:.2f})")
        
        return market_data
    
    async def get_live_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Real-time sentiment ma'lumotlari"""
        # So'nggi sentiment tarixi
        history = self.database.get_sentiment_history(symbol, days=1)
        
        if not history:
            return {"error": "Ma'lumotlar topilmadi"}
        
        # Sentiment obyektlariga aylantirish
        sentiment_history = []
        for record in history[-10:]:  # Oxirgi 10 ta yozuv
            sentiment = SentimentScore(
                bullish_probability=record['bullish_probability'],
                bearish_probability=record['bearish_probability'],
                confidence=record['confidence'],
                sentiment_type=SentimentType(record['sentiment_type']),
                overall_score=record['overall_score']
            )
            sentiment_history.append(sentiment)
        
        # Momentum tahlili
        momentum_data = self.aggregator.detect_sentiment_momentum(sentiment_history)
        
        # Joriy sentiment
        current_sentiment = sentiment_history[0] if sentiment_history else None
        
        return {
            "symbol": symbol,
            "current_sentiment": current_sentiment.to_dict() if current_sentiment else None,
            "momentum": momentum_data,
            "history_count": len(history),
            "last_updated": datetime.now().isoformat()
        }

# === FASTAPI ENDPOINTS ===

class SentimentRequest(BaseModel):
    """Sentiment so'rovi modeli"""
    symbols: List[str]
    asset_classes: Optional[List[str]] = None

class SentimentResponse(BaseModel):
    """Sentiment javob modeli"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

# FastAPI app
app = FastAPI(title="GPT-5 Sentiment Analysis API", version="1.0.0")

# Global system instance
sentiment_system = None

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    global sentiment_system
    # OpenAI API key environment variable dan olinadi
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable topilmadi")
        return
    
    sentiment_system = GPT5SentimentSystem(api_key)
    logger.info("GPT-5 Sentiment System started")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "GPT-5 Sentiment Analysis API is running"}

@app.get("/health")
async def health_check():
    """Tizim sog'lig'i tekshiruvi"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """Sentiment tahlili"""
    if not sentiment_system:
        raise HTTPException(status_code=503, detail="Sentiment tizimi ishlamayapti")
    
    try:
        # Barcha aktivlar uchun tahlil
        results = await sentiment_system.process_all_assets()
        
        response_data = {}
        for symbol, data in results.items():
            response_data[symbol] = data.to_dict()
        
        return SentimentResponse(
            success=True,
            data=response_data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Sentiment analysis xatosi: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sentiment/{symbol}")
async def get_symbol_sentiment(symbol: str):
    """Bitta aktiv uchun sentiment"""
    if not sentiment_system:
        raise HTTPException(status_code=503, detail="Sentiment tizimi ishlamayapti")
    
    try:
        sentiment_data = await sentiment_system.get_live_sentiment(symbol)
        return SentimentResponse(
            success=True,
            data=sentiment_data,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Symbol sentiment xatosi: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/symbols")
async def get_available_symbols():
    """Mavjud aktivlar ro'yxati"""
    if not sentiment_system:
        raise HTTPException(status_code=503, detail="Sentiment tizimi ishlamayapti")
    
    return {
        "stocks": sentiment_system.stocks,
        "forex": sentiment_system.forex_pairs,
        "metals": sentiment_system.metals,
        "total_symbols": len(sentiment_system.stocks) + len(sentiment_system.forex_pairs) + len(sentiment_system.metals)
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws/sentiment")
async def websocket_sentiment(websocket: WebSocket):
    """WebSocket sentiment yangilanishlari"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Sentiment ma'lumotlarini yuborish
            if sentiment_system:
                # Barcha aktivlar uchun so'nggi ma'lumotlar
                results = await sentiment_system.process_all_assets()
                
                for symbol, data in results.items():
                    sentiment_message = {
                        "type": "sentiment_update",
                        "symbol": symbol,
                        "data": data.to_dict(),
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(sentiment_message))
            
            # 30 soniya kutish
            await asyncio.sleep(30)
            
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket xatosi: {e}")

# === USAGE EXAMPLES ===

async def main():
    """Test va demonstratsiya"""
    import os
    
    # Environment variable dan API key olish
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Iltimos OPENAI_API_KEY environment variable ni sozlang")
        return
    
    # Tizimni ishga tushirish
    system = GPT5SentimentSystem(api_key)
    
    # Barcha aktivlar uchun tahlil
    print("GPT-5 Sentiment Analysis boshlanmoqda...")
    results = await system.process_all_assets()
    
    print("\n=== NATIJALAR ===")
    for symbol, data in results.items():
        if data.sentiment_data:
            print(f"{symbol} ({data.asset_class.value}):")
            print(f"  Sentiment: {data.sentiment_data.sentiment_type.value}")
            print(f"  Bullish: {data.sentiment_data.bullish_probability:.2f}")
            print(f"  Bearish: {data.sentiment_data.bearish_probability:.2f}")
            print(f"  Confidence: {data.sentiment_data.confidence:.2f}")
            print(f"  Overall Score: {data.sentiment_data.overall_score:.2f}")
            print()
    
    # So'nggi sentiment tarixi
    print("\n=== AAPL SENTIMENT TARIXI ===")
    aapl_sentiment = await system.get_live_sentiment("AAPL")
    print(json.dumps(aapl_sentiment, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    # Test uchun main() chaqirish
    # asyncio.run(main())