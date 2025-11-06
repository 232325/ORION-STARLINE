"""
Kengaytirilgan AI Xususiyatlari - Orion Starline AI Tizimi
ChatGPT va Gemini integratsiyasi, real-time AI savollar va boshqa ilg'or xususiyatlar
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import openai
from google.generativeai import GenerativeModel, configure
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Conv1D, MaxPooling1D
import redis
import websockets
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModelType(Enum):
    """AI modellari turlari"""
    CHATGPT = "chatgpt"
    GEMINI = "gemini"
    CUSTOM_LSTM = "custom_lstm"
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    MARKET_PREDICTOR = "market_predictor"

class QueryPriority(Enum):
    """So'rov prioritetlari"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class AIQuery:
    """AI so'rovi"""
    id: str
    query: str
    priority: QueryPriority
    model_type: AIModelType
    timestamp: datetime
    context: Dict[str, Any]
    user_id: Optional[str] = None
    response_cache_key: Optional[str] = None

@dataclass
class AIResponse:
    """AI javobi"""
    query_id: str
    response: str
    confidence: float
    model_used: AIModelType
    timestamp: datetime
    processing_time: float
    tokens_used: int
    metadata: Dict[str, Any]

@dataclass
class MarketSignal:
    """Bozor signali"""
    symbol: str
    signal_type: str  # buy, sell, hold
    confidence: float
    price: float
    timestamp: datetime
    model_predictions: Dict[str, float]
    technical_indicators: Dict[str, float]

class ChatGPTIntegration:
    """ChatGPT API integratsiyasi"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history = {}
        self.rate_limiter = RateLimiter(requests_per_minute=60)
        
    async def generate_response(
        self, 
        query: str, 
        context: Dict[str, Any] = None,
        user_id: str = None
    ) -> AIResponse:
        """ChatGPT dan javob olish"""
        
        start_time = datetime.now()
        
        try:
            # Rate limiting
            await self.rate_limiter.acquire()
            
            # Konversatsiya tarixini olish
            messages = self._build_messages(query, context, user_id)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            ai_response = AIResponse(
                query_id=f"chatgpt_{datetime.now().timestamp()}",
                response=response.choices[0].message.content,
                confidence=0.9,  # ChatGPT yuqori ishonchlilik
                model_used=AIModelType.CHATGPT,
                timestamp=datetime.now(),
                processing_time=processing_time,
                tokens_used=response.usage.total_tokens,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model": self.model
                }
            )
            
            # Konversatsiya tarixini saqlash
            if user_id:
                self._save_conversation_history(user_id, query, response.choices[0].message.content)
                
            return ai_response
            
        except Exception as e:
            logger.error(f"ChatGPT xatosi: {str(e)}")
            raise
    
    def _build_messages(self, query: str, context: Dict[str, Any], user_id: str) -> List[Dict]:
        """Xabarlarni tuzish"""
        messages = [
            {
                "role": "system",
                "content": "Siz Orion Starline AI tizimining yordamchisiz. Siz bozorlar, savdo va investitsiyalar haqida professional maslahat berishingiz kerak."
            }
        ]
        
        # Konversatsiya tarixini qo'shish
        if user_id and user_id in self.conversation_history:
            messages.extend(self.conversation_history[user_id][-10:])  # Oxirgi 10 xabar
        
        # Kontekstni qo'shish
        if context:
            context_msg = {
                "role": "system",
                "content": f"Kontekst ma'lumotlar: {json.dumps(context, indent=2)}"
            }
            messages.append(context_msg)
        
        # Joriy so'rov
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def _save_conversation_history(self, user_id: str, query: str, response: str):
        """Konversatsiya tarixini saqlash"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
            
        self.conversation_history[user_id].extend([
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ])
        
        # Faqat oxirgi 50 xabarni saqlash
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]

class GeminiIntegration:
    """Gemini API integratsiyasi"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        configure(api_key=api_key)
        self.model = GenerativeModel(model_name)
        self.conversation_history = {}
        
    async def generate_response(
        self, 
        query: str, 
        context: Dict[str, Any] = None,
        user_id: str = None
    ) -> AIResponse:
        """Gemini dan javob olish"""
        
        start_time = datetime.now()
        
        try:
            # Kontekstni sozlash
            prompt = self._build_prompt(query, context, user_id)
            
            response = self.model.generate_content(prompt)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            ai_response = AIResponse(
                query_id=f"gemini_{datetime.now().timestamp()}",
                response=response.text,
                confidence=0.85,  # Gemini yuqori ishonchlilik
                model_used=AIModelType.GEMINI,
                timestamp=datetime.now(),
                processing_time=processing_time,
                tokens_used=len(response.text.split()) * 1.3,  # Taxminiy token soni
                metadata={
                    "model_name": "gemini-pro",
                    "safety_ratings": str(response.prompt_feedback)
                }
            )
            
            # Konversatsiya tarixini saqlash
            if user_id:
                self._save_conversation_history(user_id, query, response.text)
                
            return ai_response
            
        except Exception as e:
            logger.error(f"Gemini xatosi: {str(e)}")
            raise
    
    def _build_prompt(self, query: str, context: Dict[str, Any], user_id: str) -> str:
        """Promptni tuzish"""
        prompt_parts = [
            "Siz Orion Starline AI tizimining professional maslahatchisisiz.",
            "Siz bozorlar, savdo strategiyalari va risklarni boshqarish haqida ekspert maslahat berishingiz kerak."
        ]
        
        # Konversatsiya tarixini qo'shish
        if user_id and user_id in self.conversation_history:
            prompt_parts.append("Avvalgi suhbatlar:")
            for conv in self.conversation_history[user_id][-5:]:
                prompt_parts.append(f"Foydalanuvchi: {conv['query']}")
                prompt_parts.append(f"Javob: {conv['response']}")
        
        # Kontekst ma'lumotlarini qo'shish
        if context:
            prompt_parts.append("Joriy bozor holati:")
            prompt_parts.append(json.dumps(context, indent=2, ensure_ascii=False))
        
        prompt_parts.append(f"Hozirgi savol: {query}")
        prompt_parts.append("Iltimos, professional va aniq javob bering:")
        
        return "\n".join(prompt_parts)
    
    def _save_conversation_history(self, user_id: str, query: str, response: str):
        """Konversatsiya tarixini saqlash"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
            
        self.conversation_history[user_id].append({
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Faqat oxirgi 20 suhbatni saqlash
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]

class RealTimeAIProcessor:
    """Real-time AI qayta ishlash tizimi"""
    
    def __init__(self, chatgpt_api_key: str, gemini_api_key: str):
        self.chatgpt = ChatGPTIntegration(chatgpt_api_key)
        self.gemini = GeminiIntegration(gemini_api_key)
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.query_queue = asyncio.Queue()
        self.response_cache = {}
        self.active_connections = set()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # WebSocket server
        self.websocket_server = None
        
    async def start_websocket_server(self, host: str = "localhost", port: int = 8765):
        """WebSocket serverini ishga tushirish"""
        logger.info(f"WebSocket serveri ishga tushirilmoqda: {host}:{port}")
        
        async def handle_client(websocket, path):
            """Mijoz bilan ishlash"""
            self.active_connections.add(websocket)
            logger.info(f"Yangi ulanish: {websocket.remote_address}")
            
            try:
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self.process_websocket_message(websocket, data)
                    except json.JSONDecodeError:
                        await websocket.send(json.dumps({"error": "Invalid JSON"}))
                        
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"Ulanish yopildi: {websocket.remote_address}")
            finally:
                self.active_connections.discard(websocket)
        
        self.websocket_server = await websockets.serve(handle_client, host, port)
        logger.info("WebSocket serveri tayyor!")
        
    async def process_websocket_message(self, websocket, data: Dict):
        """WebSocket xabarini qayta ishlash"""
        try:
            query_type = data.get("type")
            
            if query_type == "ai_query":
                await self.handle_ai_query(websocket, data)
            elif query_type == "market_analysis":
                await self.handle_market_analysis(websocket, data)
            elif query_type == "strategy_recommendation":
                await self.handle_strategy_recommendation(websocket, data)
            else:
                await websocket.send(json.dumps({"error": "Unknown query type"}))
                
        except Exception as e:
            logger.error(f"WebSocket xabar qayta ishlash xatosi: {str(e)}")
            await websocket.send(json.dumps({"error": str(e)}))
    
    async def handle_ai_query(self, websocket, data: Dict):
        """AI so'rovni qayta ishlash"""
        query = data.get("query")
        model_preference = data.get("model", "auto")
        user_id = data.get("user_id")
        
        if not query:
            await websocket.send(json.dumps({"error": "Query is required"}))
            return
        
        # So'rovni yaratish
        ai_query = AIQuery(
            id=f"ws_{datetime.now().timestamp()}",
            query=query,
            priority=QueryPriority.NORMAL,
            model_type=self._select_model(model_preference),
            timestamp=datetime.now(),
            context=data.get("context", {}),
            user_id=user_id
        )
        
        # Javobni olish
        response = await self.process_query(ai_query)
        
        # Javobni yuborish
        await websocket.send(json.dumps({
            "type": "ai_response",
            "query_id": ai_query.id,
            "response": response.response,
            "confidence": response.confidence,
            "model_used": response.model_used.value,
            "processing_time": response.processing_time,
            "timestamp": response.timestamp.isoformat()
        }))
    
    async def handle_market_analysis(self, websocket, data: Dict):
        """Bozor tahlilini qayta ishlash"""
        symbols = data.get("symbols", [])
        analysis_type = data.get("analysis_type", "comprehensive")
        
        # Bozor tahlini olish
        analysis = await self.perform_market_analysis(symbols, analysis_type)
        
        await websocket.send(json.dumps({
            "type": "market_analysis_result",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }))
    
    async def handle_strategy_recommendation(self, websocket, data: Dict):
        """Strategiya tavsiyalarini qayta ishlash"""
        portfolio = data.get("portfolio", {})
        risk_level = data.get("risk_level", "medium")
        market_conditions = data.get("market_conditions", {})
        
        recommendations = await self.generate_strategy_recommendations(
            portfolio, risk_level, market_conditions
        )
        
        await websocket.send(json.dumps({
            "type": "strategy_recommendations",
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }))
    
    def _select_model(self, preference: str) -> AIModelType:
        """Model tanlash"""
        if preference == "chatgpt":
            return AIModelType.CHATGPT
        elif preference == "gemini":
            return AIModelType.GEMINI
        else:
            # Avtomatik tanlash - so'rov turiga qarab
            return AIModelType.CHATGPT
    
    async def process_query(self, ai_query: AIQuery) -> AIResponse:
        """So'rovni qayta ishlash"""
        
        # Cache tekshirish
        cache_key = f"ai_response_{hash(ai_query.query)}_{ai_query.model_type.value}"
        cached_response = self.redis_client.get(cache_key)
        
        if cached_response:
            cached_data = json.loads(cached_response)
            return AIResponse(**cached_data)
        
        # Model bo'yicha javob olish
        if ai_query.model_type == AIModelType.CHATGPT:
            response = await self.chatgpt.generate_response(
                ai_query.query, ai_query.context, ai_query.user_id
            )
        elif ai_query.model_type == AIModelType.GEMINI:
            response = await self.gemini.generate_response(
                ai_query.query, ai_query.context, ai_query.user_id
            )
        else:
            raise ValueError(f"Unknown model type: {ai_query.model_type}")
        
        # Cache ga saqlash (24 soat)
        self.redis_client.setex(
            cache_key, 
            86400, 
            json.dumps(asdict(response), default=str)
        )
        
        return response
    
    async def perform_market_analysis(self, symbols: List[str], analysis_type: str) -> Dict[str, Any]:
        """Bozor tahlilini bajarish"""
        
        analysis_results = {}
        
        # Har bir symbol uchun tahlin qilish
        for symbol in symbols:
            # Texnik tahlin
            technical_analysis = await self._perform_technical_analysis(symbol)
            
            # Sentiment tahlin
            sentiment_analysis = await self._perform_sentiment_analysis(symbol)
            
            # Modellashtirish
            prediction = await self._perform_market_prediction(symbol)
            
            analysis_results[symbol] = {
                "technical_analysis": technical_analysis,
                "sentiment_analysis": sentiment_analysis,
                "prediction": prediction,
                "overall_signal": self._calculate_overall_signal(
                    technical_analysis, sentiment_analysis, prediction
                )
            }
        
        return analysis_results
    
    async def _perform_technical_analysis(self, symbol: str) -> Dict[str, Any]:
        """Texnik tahlin"""
        # Bu yerda texnik indikatorlarni hisoblash
        # Hozircha mock data qaytaramiz
        return {
            "rsi": 65.4,
            "macd": 0.023,
            "bollinger_position": "middle",
            "support_level": 45000,
            "resistance_level": 48000,
            "trend": "bullish",
            "volume_trend": "increasing"
        }
    
    async def _perform_sentiment_analysis(self, symbol: str) -> Dict[str, Any]:
        """Sentiment tahlin"""
        # Bu yerda sentiment tahlin qilish
        return {
            "news_sentiment": 0.65,
            "social_sentiment": 0.72,
            "overall_sentiment": 0.68,
            "sentiment_trend": "improving",
            "fear_greed_index": 72
        }
    
    async def _perform_market_prediction(self, symbol: str) -> Dict[str, Any]:
        """Bozor bashorat qilish"""
        # Bu yerda ML modeli bilan bashorat qilish
        return {
            "price_prediction_1h": 46500,
            "price_prediction_4h": 47200,
            "price_prediction_24h": 48100,
            "confidence": 0.78,
            "volatility_prediction": 0.045,
            "trend_prediction": "up"
        }
    
    def _calculate_overall_signal(self, technical: Dict, sentiment: Dict, prediction: Dict) -> str:
        """Umumiy signalni hisoblash"""
        signals = []
        
        # Texnik signal
        if technical.get("trend") == "bullish":
            signals.append(1)
        elif technical.get("trend") == "bearish":
            signals.append(-1)
        else:
            signals.append(0)
        
        # Sentiment signal
        sentiment_score = sentiment.get("overall_sentiment", 0.5)
        if sentiment_score > 0.6:
            signals.append(1)
        elif sentiment_score < 0.4:
            signals.append(-1)
        else:
            signals.append(0)
        
        # Bashorat signal
        if prediction.get("trend_prediction") == "up":
            signals.append(1)
        elif prediction.get("trend_prediction") == "down":
            signals.append(-1)
        else:
            signals.append(0)
        
        # O'rtacha hisoblash
        avg_signal = sum(signals) / len(signals)
        
        if avg_signal > 0.5:
            return "buy"
        elif avg_signal < -0.5:
            return "sell"
        else:
            return "hold"
    
    async def generate_strategy_recommendations(
        self, 
        portfolio: Dict, 
        risk_level: str, 
        market_conditions: Dict
    ) -> Dict[str, Any]:
        """Strategiya tavsiyalarini yaratish"""
        
        recommendations = {
            "allocation_strategy": {},
            "risk_management": {},
            "entry_points": [],
            "exit_points": [],
            "rebalancing_suggestions": []
        }
        
        # Portfoyl strategiyalari
        if risk_level == "low":
            recommendations["allocation_strategy"] = {
                "conservative": 70,
                "moderate": 20,
                "aggressive": 10
            }
        elif risk_level == "medium":
            recommendations["allocation_strategy"] = {
                "conservative": 40,
                "moderate": 40,
                "aggressive": 20
            }
        else:  # high
            recommendations["allocation_strategy"] = {
                "conservative": 20,
                "moderate": 30,
                "aggressive": 50
            }
        
        # Risk boshqaruvi
        recommendations["risk_management"] = {
            "max_position_size": 0.10,  # 10%
            "stop_loss_percentage": 0.05,  # 5%
            "take_profit_ratio": 2.0,  # 1:2
            "correlation_threshold": 0.7
        }
        
        return recommendations

class RateLimiter:
    """Rate limiting tizimi"""
    
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    async def acquire(self):
        """Rate limit nazorat qilish"""
        now = datetime.now()
        
        # 1 daqiqa oldingi so'rovlarni o'chirish
        self.requests = [req_time for req_time in self.requests 
                        if (now - req_time).total_seconds() < 60]
        
        # Limit tekshirish
        if len(self.requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.requests[0]).total_seconds()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        # Joriy so'rovni qo'shish
        self.requests.append(now)

class AdvancedAIFeatures:
    """Kengaytirilgan AI xususiyatlari asosiy klassi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.chatgpt_integration = None
        self.gemini_integration = None
        self.realtime_processor = None
        self.market_predictor = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Komponentlarni ishga tushirish"""
        
        # ChatGPT integratsiyasi
        if "chatgpt_api_key" in self.config:
            self.chatgpt_integration = ChatGPTIntegration(self.config["chatgpt_api_key"])
        
        # Gemini integratsiyasi
        if "gemini_api_key" in self.config:
            self.gemini_integration = GeminiIntegration(self.config["gemini_api_key"])
        
        # Real-time processor
        if self.chatgpt_integration and self.gemini_integration:
            self.realtime_processor = RealTimeAIProcessor(
                self.config["chatgpt_api_key"],
                self.config["gemini_api_key"]
            )
        
        # Market predictor
        self.market_predictor = MarketPredictor()
    
    async def start_realtime_ai(self, host: str = "localhost", port: int = 8765):
        """Real-time AI tizimini ishga tushirish"""
        if self.realtime_processor:
            await self.realtime_processor.start_websocket_server(host, port)
            logger.info(f"Real-time AI tizimi ishga tushdi: {host}:{port}")
        else:
            raise ValueError("Real-time processor inicializatsiya qilinmagan")
    
    async def process_ai_query(
        self, 
        query: str, 
        model_preference: str = "auto",
        user_id: str = None,
        context: Dict[str, Any] = None
    ) -> AIResponse:
        """AI so'rovni qayta ishlash"""
        
        # Model tanlash
        if model_preference == "chatgpt":
            model_type = AIModelType.CHATGPT
        elif model_preference == "gemini":
            model_type = AIModelType.GEMINI
        else:
            model_type = AIModelType.CHATGPT  # Default
        
        # So'rov yaratish
        ai_query = AIQuery(
            id=f"adv_ai_{datetime.now().timestamp()}",
            query=query,
            priority=QueryPriority.NORMAL,
            model_type=model_type,
            timestamp=datetime.now(),
            context=context or {},
            user_id=user_id
        )
        
        # Qayta ishlash
        if model_type == AIModelType.CHATGPT and self.chatgpt_integration:
            return await self.chatgpt_integration.generate_response(query, context, user_id)
        elif model_type == AIModelType.GEMINI and self.gemini_integration:
            return await self.gemini_integration.generate_response(query, context, user_id)
        else:
            raise ValueError("Mos AI integratsiyasi topilmadi")
    
    async def generate_market_signals(self, symbols: List[str]) -> List[MarketSignal]:
        """Bozor signallari yaratish"""
        signals = []
        
        for symbol in symbols:
            # Texnik tahlin
            technical_data = await self._get_technical_data(symbol)
            
            # Sentiment tahlin
            sentiment_data = await self._get_sentiment_data(symbol)
            
            # Bashorat
            prediction = await self.market_predictor.predict(symbol, technical_data)
            
            # Signal yaratish
            signal = MarketSignal(
                symbol=symbol,
                signal_type=prediction["signal"],
                confidence=prediction["confidence"],
                price=technical_data["current_price"],
                timestamp=datetime.now(),
                model_predictions=prediction["predictions"],
                technical_indicators=technical_data["indicators"]
            )
            
            signals.append(signal)
        
        return signals
    
    async def _get_technical_data(self, symbol: str) -> Dict[str, Any]:
        """Texnik ma'lumotlarni olish"""
        # Mock data - real implementationda API dan olinadi
        return {
            "current_price": 46500.0,
            "indicators": {
                "rsi": 65.4,
                "macd": 0.023,
                "bollinger_upper": 48000,
                "bollinger_lower": 45000,
                "sma_20": 46200,
                "sma_50": 45800
            }
        }
    
    async def _get_sentiment_data(self, symbol: str) -> Dict[str, Any]:
        """Sentiment ma'lumotlarini olish"""
        # Mock data - real implementationda sentiment API dan olinadi
        return {
            "news_sentiment": 0.65,
            "social_sentiment": 0.72,
            "overall_score": 0.68,
            "volume_change": 0.15
        }

class MarketPredictor:
    """Bozor bashorat qilish modeli"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self._initialize_model()
    
    def _initialize_model(self):
        """Model arxitekturasini yaratish"""
        self.model = Sequential([
            Conv1D(64, 3, activation='relu', input_shape=(50, 10)),
            MaxPooling1D(2),
            Dropout(0.2),
            Conv1D(32, 3, activation='relu'),
            MaxPooling1D(2),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(25),
            Dense(3, activation='softmax')  # buy, sell, hold
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
    
    async def predict(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Bashorat qilish"""
        if not self.is_trained:
            await self._train_model()
        
        # Features extraction
        features = self._extract_features(data)
        features_scaled = self.scaler.transform([features])
        
        # Prediction
        prediction = self.model.predict(features_scaled.reshape(1, 1, -1))
        
        # Result interpretation
        classes = ['sell', 'hold', 'buy']
        predicted_class = classes[np.argmax(prediction[0])]
        confidence = np.max(prediction[0])
        
        return {
            "signal": predicted_class,
            "confidence": float(confidence),
            "predictions": {
                "sell": float(prediction[0][0]),
                "hold": float(prediction[0][1]),
                "buy": float(prediction[0][2])
            }
        }
    
    def _extract_features(self, data: Dict[str, Any]) -> List[float]:
        """Xususiyatlarni ajratib olish"""
        indicators = data.get("indicators", {})
        
        features = [
            indicators.get("rsi", 50) / 100,  # Normalize
            indicators.get("macd", 0),
            (indicators.get("bollinger_upper", 47000) - indicators.get("bollinger_lower", 46000)) / 1000,
            indicators.get("sma_20", 46000) / 50000,  # Normalize
            indicators.get("sma_50", 46000) / 50000,
            data.get("current_price", 46000) / 50000,
            0.5,  # Mock volume indicator
            0.5,  # Mock momentum
            0.5,  # Mock volatility
            0.5   # Mock trend
        ]
        
        return features
    
    async def _train_model(self):
        """Modelni o'qitish"""
        logger.info("Market predictor modeli o'qitilmoqda...")
        
        # Mock training data
        X_train, y_train = self._generate_training_data()
        
        # Scaling
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Reshape for Conv1D
        X_train_reshaped = X_train_scaled.reshape(X_train_scaled.shape[0], 1, X_train_scaled.shape[1])
        
        # Training
        history = self.model.fit(
            X_train_reshaped, y_train,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        self.is_trained = True
        logger.info(f"Model o'qitildi. Accuracy: {history.history['accuracy'][-1]:.3f}")
    
    def _generate_training_data(self) -> Tuple[List[List[float]], List[List[int]]]:
        """Training data yaratish"""
        X_train = []
        y_train = []
        
        # 1000 ta mock sample yaratish
        for _ in range(1000):
            # Random features
            features = [
                np.random.random(),  # rsi
                np.random.normal(0, 0.1),  # macd
                np.random.random() * 2,  # bollinger
                np.random.random(),  # sma_20
                np.random.random(),  # sma_50
                np.random.random(),  # price
                np.random.random(),  # volume
                np.random.random(),  # momentum
                np.random.random(),  # volatility
                np.random.random()   # trend
            ]
            X_train.append(features)
            
            # Label (simple rule-based)
            signal_score = (
                features[0] * 0.3 +  # rsi
                features[1] * 0.2 +  # macd
                features[3] * 0.2 +  # sma_20
                features[9] * 0.3    # trend
            )
            
            if signal_score > 0.6:
                y_train.append([0, 0, 1])  # buy
            elif signal_score < 0.4:
                y_train.append([1, 0, 0])  # sell
            else:
                y_train.append([0, 1, 0])  # hold
        
        return X_train, y_train

# Konfiguratsiya va ishga tushirish
def create_advanced_ai_system(config_path: str = None) -> AdvancedAIFeatures:
    """Advanced AI tizimini yaratish"""
    
    # Default config
    default_config = {
        "chatgpt_api_key": "your_chatgpt_api_key",
        "gemini_api_key": "your_gemini_api_key",
        "redis_host": "localhost",
        "redis_port": 6379,
        "websocket_host": "localhost",
        "websocket_port": 8765
    }
    
    # Config file dan o'qish
    if config_path:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                default_config.update(config_data)
        except Exception as e:
            logger.warning(f"Config file o'qishda xato: {str(e)}")
    
    return AdvancedAIFeatures(default_config)

# Demo va test funksiyalari
async def demo_advanced_ai():
    """Advanced AI demo"""
    
    # AI tizimini yaratish
    ai_system = create_advanced_ai_system()
    
    print("🚀 Advanced AI Features Demo")
    print("=" * 50)
    
    # ChatGPT test
    print("\n📝 ChatGPT Integration Test:")
    try:
        response = await ai_system.process_ai_query(
            "Bitcoin narxi haqida tahlil qiling va kelajakdagi o'zgarishlar haqida прогноз bering.",
            model_preference="chatgpt"
        )
        print(f"Model: {response.model_used.value}")
        print(f"Javob: {response.response[:200]}...")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Processing time: {response.processing_time:.2f}s")
    except Exception as e:
        print(f"ChatGPT xatosi: {str(e)}")
    
    # Gemini test
    print("\n🧠 Gemini Integration Test:")
    try:
        response = await ai_system.process_ai_query(
            "Ethereum bozoridagi risklarni tahlil qiling va diversifikatsiya bo'yicha maslahat bering.",
            model_preference="gemini"
        )
        print(f"Model: {response.model_used.value}")
        print(f"Javob: {response.response[:200]}...")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Processing time: {response.processing_time:.2f}s")
    except Exception as e:
        print(f"Gemini xatosi: {str(e)}")
    
    # Market signals test
    print("\n📊 Market Signals Generation Test:")
    try:
        signals = await ai_system.generate_market_signals(["BTCUSDT", "ETHUSDT", "ADAUSDT"])
        for signal in signals:
            print(f"{signal.symbol}: {signal.signal_type} (confidence: {signal.confidence:.2f})")
    except Exception as e:
        print(f"Market signals xatosi: {str(e)}")
    
    # Real-time processor test
    print("\n⚡ Real-time AI Test:")
    print("WebSocket serveri 5 soniya davomida ishga tushiriladi...")
    try:
        await ai_system.start_realtime_ai()
        await asyncio.sleep(5)  # 5 soniya kutish
        if hasattr(ai_system.realtime_processor, 'websocket_server'):
            ai_system.realtime_processor.websocket_server.close()
            await ai_system.realtime_processor.websocket_server.wait_closed()
    except Exception as e:
        print(f"Real-time AI xatosi: {str(e)}")
    
    print("\n✅ Demo yakunlandi!")

if __name__ == "__main__":
    # Demo ishga tushirish
    asyncio.run(demo_advanced_ai())