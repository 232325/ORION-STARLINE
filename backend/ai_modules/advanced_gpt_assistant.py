#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI GPT-4 & Google Gemini API Integration
AI Model Integration Tizimi

Asosiy imkoniyatlar:
- OpenAI GPT-4 API integratsiyasi
- Google Gemini API integratsiyasi
- Ko'plab model qo'llab-quvvatlashi
- Aqlli model tanlash
- Fallback mexanizmi
- Xarajatlarni optimizatsiya qilish
- Response caching
- Rate limiting va throttling
- Error handling va retry logic

Author: Orion Starline AI Team
Date: 2025-11-05
Version: 2.0.0
"""

import asyncio
import hashlib
import json
import logging
import time
import os
import sqlite3
from typing import Dict, List, Optional, Any, Union, Tuple, Generator, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import aiohttp
import openai
import google.generativeai as genai
from openai import OpenAI
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import tiktoken

# Logging konfiguratsiyasi
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Modellarning turlari"""
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    GEMINI_FLASH = "gemini-1.5-flash"
    GEMINI_FLASH_LATEST = "gemini-1.5-flash-8b"


class TaskType(Enum):
    """Vazifa turlari"""
    TRADING_ANALYSIS = "trading_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    NEWS_ANALYSIS = "news_analysis"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    RISK_ASSESSMENT = "risk_assessment"
    GENERAL_CHAT = "general_chat"
    CODE_GENERATION = "code_generation"
    DATA_ANALYSIS = "data_analysis"
    IMAGE_ANALYSIS = "image_analysis"
    STRATEGY_CREATION = "strategy_creation"
    BACKTESTING = "backtesting"
    MARKET_PREDICTION = "market_prediction"


class ModelPerformance(Enum):
    """Model bajarilish ko'rsatkichlari"""
    EXCELLENT = 5
    GOOD = 4
    AVERAGE = 3
    BELOW_AVERAGE = 2
    POOR = 1


@dataclass
class ModelConfig:
    """Model konfiguratsiyasi"""
    name: ModelType
    provider: str
    max_tokens: int
    context_window: int
    cost_per_token: float
    cost_per_request: float
    rate_limit: int  # requests per minute
    response_time_target: float  # seconds
    quality_score: float
    supported_tasks: List[TaskType]
    streaming_support: bool
    function_calling_support: bool
    vision_support: bool
    latency_estimate: float  # milliseconds


@dataclass
class ModelResponse:
    """Model javobi"""
    content: str
    model_used: str
    tokens_used: int
    cost: float
    response_time: float
    quality_score: float
    timestamp: datetime
    task_type: TaskType
    cached: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheEntry:
    """Cache yozuvi"""
    response: ModelResponse
    timestamp: datetime
    hash_key: str
    hits: int = 1


class RateLimiter:
    """Rate Limiter"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = threading.Lock()
    
    def can_make_request(self) -> bool:
        """Yangi so'rov yaratish mumkinmi?"""
        with self.lock:
            current_time = time.time()
            # Eski so'rovlarni olib tashlash
            while self.requests and self.requests[0] < current_time - self.time_window:
                self.requests.popleft()
            
            return len(self.requests) < self.max_requests
    
    def add_request(self):
        """So'rov qo'shish"""
        with self.lock:
            current_time = time.time()
            self.requests.append(current_time)
    
    def wait_time(self) -> float:
        """Kutilish vaqti"""
        with self.lock:
            current_time = time.time()
            if not self.requests:
                return 0
            
            oldest_request = min(self.requests)
            wait_time = (oldest_request + self.time_window) - current_time
            return max(0, wait_time)


class ResponseCache:
    """Response Caching tizimi"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.ttl = ttl  # seconds
        self.lock = threading.Lock()
    
    def _get_cache_key(self, prompt: str, model: str, task_type: TaskType) -> str:
        """Cache kalitini yaratish"""
        content = f"{prompt}_{model}_{task_type.value}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, task_type: TaskType) -> Optional[ModelResponse]:
        """Cache dan javob olish"""
        key = self._get_cache_key(prompt, model, task_type)
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                # TTL tekshirish
                if (datetime.now() - entry.timestamp).total_seconds() < self.ttl:
                    entry.hits += 1
                    return entry.response
                else:
                    # Expired entry
                    del self.cache[key]
        return None
    
    def set(self, response: ModelResponse, prompt: str, model: str, task_type: TaskType):
        """Cache ga javob qo'shish"""
        key = self._get_cache_key(prompt, model, task_type)
        with self.lock:
            # Cache size limit check
            if len(self.cache) >= self.max_size:
                # Least used entry ni o'chirish
                oldest_key = min(self.cache.keys(), 
                               key=lambda k: (self.cache[k].hits, self.cache[k].timestamp))
                del self.cache[oldest_key]
            
            self.cache[key] = CacheEntry(
                response=response,
                timestamp=datetime.now(),
                hash_key=key
            )
    
    def clear(self):
        """Cache ni tozalash"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Cache statistikasi"""
        with self.lock:
            total_hits = sum(entry.hits for entry in self.cache.values())
            return {
                "total_entries": len(self.cache),
                "total_hits": total_hits,
                "hit_ratio": total_hits / max(len(self.cache), 1)
            }


class ModelEvaluator:
    """Model baholovchi tizim"""
    
    def __init__(self):
        self.quality_scores = defaultdict(list)
        self.response_times = defaultdict(list)
        self.costs = defaultdict(list)
        self.task_performance = defaultdict(lambda: defaultdict(list))
    
    def evaluate_response(self, response: ModelResponse, expected_quality: float = 4.0) -> float:
        """Javobni baholash"""
        # Baza scoring factors
        base_score = 5.0
        
        # Response time penalty
        if response.response_time > response.metadata.get('time_target', 2.0):
            base_score -= 1.0
        
        # Cost efficiency penalty
        if response.cost > 0.1:  # $0.1 dan ortiq xarajat
            base_score -= 0.5
        
        # Content quality checks
        content = response.content.lower()
        
        # Qo'shimcha javoblar uchun bonus
        if len(content) > 100:
            base_score += 0.5
        
        # Structured content uchun bonus
        if any(marker in content for marker in ['\n', '1.', '2.', '-', '•']):
            base_score += 0.5
        
        # Error indicators uchun penalty
        error_indicators = ['error', 'sorry', 'cannot', 'unable', 'failed']
        if any(indicator in content for indicator in error_indicators):
            base_score -= 2.0
        
        # Task-specific scoring
        if response.task_type in [TaskType.TRADING_ANALYSIS, TaskType.TECHNICAL_ANALYSIS]:
            # Trading analysis uchun maxsus criteria
            trading_indicators = ['trend', 'support', 'resistance', 'volatility', 'rsi', 'macd']
            if any(indicator in content for indicator in trading_indicators):
                base_score += 1.0
        
        return max(0, min(5, base_score))
    
    def record_performance(self, model_name: str, response: ModelResponse):
        """Bajarilish ko'rsatkichlarini yozib olish"""
        quality_score = self.evaluate_response(response)
        
        self.quality_scores[model_name].append(quality_score)
        self.response_times[model_name].append(response.response_time)
        self.costs[model_name].append(response.cost)
        self.task_performance[model_name][response.task_type.value].append(quality_score)
    
    def get_model_stats(self, model_name: str) -> Dict[str, float]:
        """Model statistikasi"""
        quality_scores = self.quality_scores[model_name]
        response_times = self.response_times[model_name]
        costs = self.costs[model_name]
        
        return {
            "avg_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "avg_cost": sum(costs) / len(costs) if costs else 0,
            "total_requests": len(quality_scores)
        }


class AdvancedGPTAssistant:
    """AI Model Integration Tizimi"""
    
    # Model konfiguratsiyalari
    MODEL_CONFIGS = {
        ModelType.GPT4: ModelConfig(
            name=ModelType.GPT4,
            provider="openai",
            max_tokens=8192,
            context_window=8192,
            cost_per_token=0.00003,
            cost_per_request=0.03,
            rate_limit=3500,
            response_time_target=2.0,
            quality_score=4.5,
            supported_tasks=[TaskType.GENERAL_CHAT, TaskType.TRADING_ANALYSIS, 
                           TaskType.TECHNICAL_ANALYSIS, TaskType.CODE_GENERATION],
            streaming_support=True,
            function_calling_support=True,
            vision_support=False,
            latency_estimate=1200
        ),
        ModelType.GPT4_TURBO: ModelConfig(
            name=ModelType.GPT4_TURBO,
            provider="openai",
            max_tokens=4096,
            context_window=128000,
            cost_per_token=0.00001,
            cost_per_request=0.01,
            rate_limit=5000,
            response_time_target=1.5,
            quality_score=4.3,
            supported_tasks=[TaskType.GENERAL_CHAT, TaskType.TRADING_ANALYSIS, 
                           TaskType.TECHNICAL_ANALYSIS, TaskType.NEWS_ANALYSIS],
            streaming_support=True,
            function_calling_support=True,
            vision_support=False,
            latency_estimate=1000
        ),
        ModelType.GPT4O: ModelConfig(
            name=ModelType.GPT4O,
            provider="openai",
            max_tokens=4096,
            context_window=128000,
            cost_per_token=0.0000025,
            cost_per_request=0.0025,
            rate_limit=10000,
            response_time_target=1.0,
            quality_score=4.2,
            supported_tasks=[TaskType.GENERAL_CHAT, TaskType.TRADING_ANALYSIS, 
                           TaskType.TECHNICAL_ANALYSIS, TaskType.IMAGE_ANALYSIS],
            streaming_support=True,
            function_calling_support=True,
            vision_support=True,
            latency_estimate=800
        ),
        ModelType.GEMINI_PRO: ModelConfig(
            name=ModelType.GEMINI_PRO,
            provider="google",
            max_tokens=8192,
            context_window=32000,
            cost_per_token=0.00000125,
            cost_per_request=0.002,
            rate_limit=15,
            response_time_target=1.5,
            quality_score=4.0,
            supported_tasks=[TaskType.GENERAL_CHAT, TaskType.TRADING_ANALYSIS, 
                           TaskType.DATA_ANALYSIS, TaskType.NEWS_ANALYSIS],
            streaming_support=True,
            function_calling_support=False,
            vision_support=False,
            latency_estimate=1000
        ),
        ModelType.GEMINI_PRO_VISION: ModelConfig(
            name=ModelType.GEMINI_PRO_VISION,
            provider="google",
            max_tokens=8192,
            context_window=32000,
            cost_per_token=0.0000025,
            cost_per_request=0.005,
            rate_limit=15,
            response_time_target=2.0,
            quality_score=4.1,
            supported_tasks=[TaskType.IMAGE_ANALYSIS, TaskType.GENERAL_CHAT, 
                           TaskType.DATA_ANALYSIS],
            streaming_support=True,
            function_calling_support=False,
            vision_support=True,
            latency_estimate=1500
        )
    }
    
    def __init__(self, 
                 openai_api_key: str = None,
                 gemini_api_key: str = None,
                 cache_size: int = 1000,
                 cache_ttl: int = 3600,
                 enable_ab_testing: bool = False):
        """
        AI Assistant ni ishga tushirish
        
        Args:
            openai_api_key: OpenAI API kaliti
            gemini_api_key: Google Gemini API kaliti
            cache_size: Cache hajmi
            cache_ttl: Cache TTL (seconds)
            enable_ab_testing: A/B testing yoqish/o'chirish
        """
        self.openai_client = None
        self.gemini_model = None
        self.conversations = {}  # Multi-turn conversation support
        self.enable_ab_testing = enable_ab_testing
        
        # Initsializatsiya
        self._initialize_clients(openai_api_key, gemini_api_key)
        
        # Cache va rate limiting
        self.cache = ResponseCache(cache_size, cache_ttl)
        self.rate_limiters = {}
        for model_type in self.MODEL_CONFIGS:
            config = self.MODEL_CONFIGS[model_type]
            self.rate_limiters[model_type] = RateLimiter(
                config.rate_limit, 60  # 1 daqiqa window
            )
        
        # Performance tracking
        self.evaluator = ModelEvaluator()
        self.performance_metrics = defaultdict(int)
        
        # Model selection strategies
        self.model_strategies = {
            "cost_optimized": self._cost_optimized_selection,
            "quality_focused": self._quality_focused_selection,
            "speed_optimized": self._speed_optimized_selection,
            "trading_specialized": self._trading_specialized_selection
        }
        
        logger.info("Advanced GPT Assistant initialized successfully")
    
    def _initialize_clients(self, openai_api_key: str, gemini_api_key: str):
        """API clientlarni sozlash"""
        try:
            if openai_api_key:
                os.environ['OPENAI_API_KEY'] = openai_api_key
                self.openai_client = OpenAI()
                logger.info("OpenAI client initialized")
            
            if gemini_api_key:
                os.environ['GEMINI_API_KEY'] = gemini_api_key
                genai.configure(api_key=gemini_api_key)
                # Gemini model ni sozlash
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                }
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("Google Gemini client initialized")
                
        except Exception as e:
            logger.error(f"Error initializing clients: {e}")
            raise
    
    def _cost_optimized_selection(self, task_type: TaskType, context: Dict[str, Any]) -> List[ModelType]:
        """Xarajatlar bo'yicha optimizatsiya qilingan tanlash"""
        # Eng arzon model dan boshlash
        cost_ranking = sorted(
            self.MODEL_CONFIGS.items(),
            key=lambda x: x[1].cost_per_token
        )
        
        suitable_models = []
        for model_type, config in cost_ranking:
            if task_type in config.supported_tasks:
                suitable_models.append(model_type)
        
        return suitable_models[:3]  # Top 3 models
    
    def _quality_focused_selection(self, task_type: TaskType, context: Dict[str, Any]) -> List[ModelType]:
        """Sifat bo'yicha optimizatsiya qilingan tanlash"""
        # Eng sifatli model dan boshlash
        quality_ranking = sorted(
            self.MODEL_CONFIGS.items(),
            key=lambda x: x[1].quality_score,
            reverse=True
        )
        
        suitable_models = []
        for model_type, config in quality_ranking:
            if task_type in config.supported_tasks:
                suitable_models.append(model_type)
        
        return suitable_models[:3]
    
    def _speed_optimized_selection(self, task_type: TaskType, context: Dict[str, Any]) -> List[ModelType]:
        """Tezlik bo'yicha optimizatsiya qilingan tanlash"""
        # Eng tez model dan boshlash
        speed_ranking = sorted(
            self.MODEL_CONFIGS.items(),
            key=lambda x: x[1].latency_estimate
        )
        
        suitable_models = []
        for model_type, config in speed_ranking:
            if task_type in config.supported_tasks:
                suitable_models.append(model_type)
        
        return suitable_models[:3]
    
    def _trading_specialized_selection(self, task_type: TaskType, context: Dict[str, Any]) -> List[ModelType]:
        """Trading uchun maxsus tanlash"""
        trading_models = [ModelType.GPT4, ModelType.GPT4_TURBO, ModelType.GPT4O]
        
        if task_type in [TaskType.TECHNICAL_ANALYSIS, TaskType.TRADING_ANALYSIS]:
            return trading_models
        elif task_type == TaskType.MARKET_PREDICTION:
            return [ModelType.GPT4, ModelType.GPT4_TURBO]
        elif task_type == TaskType.IMAGE_ANALYSIS:
            return [ModelType.GPT4O, ModelType.GEMINI_PRO_VISION]
        else:
            return trading_models
    
    def _detect_task_type(self, prompt: str, context: Dict[str, Any] = None) -> TaskType:
        """Vazifa turini aniqlash"""
        prompt_lower = prompt.lower()
        
        # Trading-related keywords
        trading_keywords = ['trade', 'stock', 'market', 'price', 'buy', 'sell', 'portfolio', 'invest']
        technical_keywords = ['chart', 'pattern', 'rsi', 'macd', 'indicator', 'support', 'resistance']
        news_keywords = ['news', 'article', 'announcement', 'report', 'event']
        image_keywords = ['image', 'picture', 'chart', 'graph', 'visual', 'screenshot']
        code_keywords = ['code', 'script', 'function', 'python', 'program', 'algorithm']
        
        # Task type detection
        if any(keyword in prompt_lower for keyword in image_keywords):
            return TaskType.IMAGE_ANALYSIS
        elif any(keyword in prompt_lower for keyword in technical_keywords):
            return TaskType.TECHNICAL_ANALYSIS
        elif any(keyword in prompt_lower for keyword in news_keywords):
            return TaskType.NEWS_ANALYSIS
        elif any(keyword in prompt_lower for keyword in trading_keywords):
            return TaskType.TRADING_ANALYSIS
        elif any(keyword in prompt_lower for keyword in code_keywords):
            return TaskType.CODE_GENERATION
        else:
            return TaskType.GENERAL_CHAT
    
    def _select_best_model(self, 
                          task_type: TaskType, 
                          strategy: str = "cost_optimized",
                          context: Dict[str, Any] = None) -> ModelType:
        """Eng yaxshi modelni tanlash"""
        if context is None:
            context = {}
        
        # Model selection strategy
        strategy_func = self.model_strategies.get(strategy, self._cost_optimized_selection)
        candidate_models = strategy_func(task_type, context)
        
        # Fallback model
        if not candidate_models:
            candidate_models = [ModelType.GPT4O, ModelType.GEMINI_PRO]
        
        # Performance-based selection
        best_model = candidate_models[0]
        best_score = 0
        
        for model_type in candidate_models:
            if model_type in self.MODEL_CONFIGS:
                config = self.MODEL_CONFIGS[model_type]
                # Get recent performance metrics
                model_stats = self.evaluator.get_model_stats(model_type.value)
                
                # Calculate composite score
                quality_score = model_stats.get('avg_quality', config.quality_score)
                speed_score = config.quality_score * (1 - (model_stats.get('avg_response_time', 0) / config.response_time_target))
                cost_score = config.quality_score * (1 - min(config.cost_per_token * 10000, 0.5))
                
                total_score = (quality_score * 0.5 + speed_score * 0.3 + cost_score * 0.2)
                
                if total_score > best_score:
                    best_score = total_score
                    best_model = model_type
        
        return best_model
    
    def _make_openai_request(self, 
                            model: str, 
                            messages: List[Dict], 
                            stream: bool = False,
                            functions: List[Dict] = None) -> Union[ModelResponse, Generator]:
        """OpenAI API ga so'rov yuborish"""
        start_time = time.time()
        
        try:
            # Function calling support
            if functions:
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    functions=functions,
                    stream=stream,
                    max_tokens=2000,
                    temperature=0.7
                )
            else:
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=stream,
                    max_tokens=2000,
                    temperature=0.7
                )
            
            if stream:
                return self._handle_openai_streaming_response(response, model, start_time)
            else:
                content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                cost = tokens_used * self.MODEL_CONFIGS[ModelType(model)].cost_per_token
                response_time = time.time() - start_time
                
                return ModelResponse(
                    content=content,
                    model_used=model,
                    tokens_used=tokens_used,
                    cost=cost,
                    response_time=response_time,
                    quality_score=0,  # Will be set by evaluator
                    timestamp=datetime.now(),
                    task_type=TaskType.GENERAL_CHAT
                )
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ModelResponse(
                content="",
                model_used=model,
                tokens_used=0,
                cost=0,
                response_time=time.time() - start_time,
                quality_score=0,
                timestamp=datetime.now(),
                task_type=TaskType.GENERAL_CHAT,
                error=str(e)
            )
    
    def _make_gemini_request(self, 
                           model: str, 
                           prompt: str, 
                           stream: bool = False,
                           context: Dict[str, Any] = None) -> Union[ModelResponse, Generator]:
        """Google Gemini API ga so'rov yuborish"""
        start_time = time.time()
        
        try:
            if stream:
                response = self.gemini_model.generate_content(prompt, stream=True)
                return self._handle_gemini_streaming_response(response, model, start_time)
            else:
                response = self.gemini_model.generate_content(prompt)
                content = response.text
                
                # Token estimation for Gemini (approximate)
                tokens_used = len(prompt.split()) * 1.3  # Rough estimation
                cost = tokens_used * self.MODEL_CONFIGS[ModelType(model)].cost_per_token
                response_time = time.time() - start_time
                
                return ModelResponse(
                    content=content,
                    model_used=model,
                    tokens_used=int(tokens_used),
                    cost=cost,
                    response_time=response_time,
                    quality_score=0,  # Will be set by evaluator
                    timestamp=datetime.now(),
                    task_type=TaskType.GENERAL_CHAT
                )
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return ModelResponse(
                content="",
                model_used=model,
                tokens_used=0,
                cost=0,
                response_time=time.time() - start_time,
                quality_score=0,
                timestamp=datetime.now(),
                task_type=TaskType.GENERAL_CHAT,
                error=str(e)
            )
    
    def _handle_openai_streaming_response(self, response, model: str, start_time: float) -> Generator:
        """OpenAI streaming response handler"""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                response_time = time.time() - start_time
                yield ModelResponse(
                    content=content,
                    model_used=model,
                    tokens_used=0,  # Will be calculated at the end
                    cost=0,  # Will be calculated at the end
                    response_time=response_time,
                    quality_score=0,
                    timestamp=datetime.now(),
                    task_type=TaskType.GENERAL_CHAT,
                    metadata={"streaming": True}
                )
    
    def _handle_gemini_streaming_response(self, response, model: str, start_time: float) -> Generator:
        """Gemini streaming response handler"""
        for chunk in response:
            if chunk.text:
                content = chunk.text
                response_time = time.time() - start_time
                yield ModelResponse(
                    content=content,
                    model_used=model,
                    tokens_used=0,
                    cost=0,
                    response_time=response_time,
                    quality_score=0,
                    timestamp=datetime.now(),
                    task_type=TaskType.GENERAL_CHAT,
                    metadata={"streaming": True}
                )
    
    def _check_rate_limit(self, model_type: ModelType) -> bool:
        """Rate limit tekshirish"""
        if model_type not in self.rate_limiters:
            return True
        
        return self.rate_limiters[model_type].can_make_request()
    
    def _wait_for_rate_limit(self, model_type: ModelType, max_wait: int = 30):
        """Rate limit kutish"""
        if model_type in self.rate_limiters:
            wait_time = self.rate_limiters[model_type].wait_time()
            if wait_time > 0 and wait_time <= max_wait:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
    
    def _apply_fallback(self, primary_model: ModelType, error: str) -> ModelType:
        """Fallback mechanism"""
        logger.warning(f"Primary model {primary_model} failed: {error}")
        
        # Provider-based fallback
        primary_config = self.MODEL_CONFIGS[primary_model]
        
        if primary_config.provider == "openai":
            # OpenAI dan Gemini ga
            if self.gemini_model:
                return ModelType.GEMINI_PRO
        else:
            # Gemini dan OpenAI ga
            if self.openai_client:
                return ModelType.GPT4O
        
        # Model-based fallback
        fallbacks = {
            ModelType.GPT4: ModelType.GPT4_TURBO,
            ModelType.GPT4_TURBO: ModelType.GPT4O,
            ModelType.GPT4O: ModelType.GEMINI_PRO,
            ModelType.GEMINI_PRO: ModelType.GEMINI_FLASH,
            ModelType.GEMINI_PRO_VISION: ModelType.GEMINI_PRO
        }
        
        return fallbacks.get(primary_model, ModelType.GPT4O)
    
    async def chat(self, 
                   prompt: str, 
                   conversation_id: str = None,
                   strategy: str = "cost_optimized",
                   use_cache: bool = True,
                   stream: bool = False,
                   max_retries: int = 3,
                   context: Dict[str, Any] = None) -> Union[ModelResponse, Generator]:
        """
        Asosiy chat funksiyasi
        
        Args:
            prompt: Foydalanuvchi so'rovi
            conversation_id: Suxbat ID si
            strategy: Model tanlash strategiyasi
            use_cache: Cache ishlatish
            stream: Streaming response
            max_retries: Retry soni
            context: Qo'shimcha kontekst
        
        Returns:
            ModelResponse yoki Generator (streaming uchun)
        """
        start_time = time.time()
        retries = 0
        
        try:
            # Task type detection
            task_type = self._detect_task_type(prompt, context)
            
            # Multi-turn conversation
            if conversation_id:
                if conversation_id not in self.conversations:
                    self.conversations[conversation_id] = []
                messages = self.conversations[conversation_id]
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]
            
            # Cache check
            if use_cache and not stream:
                cached_response = self.cache.get(prompt, "", task_type)
                if cached_response:
                    logger.info("Cache hit")
                    cached_response.cached = True
                    return cached_response
            
            # Model selection
            model_type = self._select_best_model(task_type, strategy, context)
            model_config = self.MODEL_CONFIGS[model_type]
            
            # Rate limit check
            if not self._check_rate_limit(model_type):
                self._wait_for_rate_limit(model_type)
                if not self._check_rate_limit(model_type):
                    # Fallback to different model
                    model_type = self._apply_fallback(model_type, "Rate limit exceeded")
                    model_config = self.MODEL_CONFIGS[model_type]
            
            # API request with retry logic
            while retries <= max_retries:
                try:
                    # OpenAI request
                    if model_config.provider == "openai":
                        response = self._make_openai_request(
                            model=model_type.value,
                            messages=messages,
                            stream=stream
                        )
                    # Gemini request
                    else:
                        response = self._make_gemini_request(
                            model=model_type.value,
                            prompt=prompt,
                            stream=stream,
                            context=context
                        )
                    
                    # Quality evaluation
                    if not stream:
                        response.quality_score = self.evaluator.evaluate_response(response, 4.0)
                        response.task_type = task_type
                        
                        # Performance recording
                        self.evaluator.record_performance(model_type.value, response)
                        
                        # Cache storage
                        if use_cache and not response.error:
                            self.cache.set(response, prompt, model_type.value, task_type)
                        
                        # Rate limiter update
                        if model_type in self.rate_limiters:
                            self.rate_limiters[model_type].add_request()
                        
                        # Update conversation history
                        if conversation_id:
                            messages.append({"role": "assistant", "content": response.content})
                            self.conversations[conversation_id] = messages[-10:]  # Keep last 10 messages
                        
                        logger.info(f"Response generated: {model_type.value}, Quality: {response.quality_score:.2f}, Cost: ${response.cost:.4f}")
                        return response
                    else:
                        return response
                
                except Exception as e:
                    retries += 1
                    error_msg = str(e)
                    
                    if retries <= max_retries:
                        logger.warning(f"Request failed (attempt {retries}/{max_retries}): {error_msg}")
                        time.sleep(2 ** retries)  # Exponential backoff
                        
                        # Try fallback model
                        fallback_model = self._apply_fallback(model_type, error_msg)
                        if fallback_model != model_type:
                            model_type = fallback_model
                            model_config = self.MODEL_CONFIGS[model_type]
                    else:
                        logger.error(f"Max retries exceeded: {error_msg}")
                        return ModelResponse(
                            content="Uzr, so'rovingizni qayta ishlashda xatolik yuz berdi.",
                            model_used=model_type.value,
                            tokens_used=0,
                            cost=0,
                            response_time=time.time() - start_time,
                            quality_score=0,
                            timestamp=datetime.now(),
                            task_type=task_type,
                            error=error_msg
                        )
        
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return ModelResponse(
                content="Kutilmagan xatolik yuz berdi.",
                model_used="unknown",
                tokens_used=0,
                cost=0,
                response_time=time.time() - start_time,
                quality_score=0,
                timestamp=datetime.now(),
                task_type=TaskType.GENERAL_CHAT,
                error=str(e)
            )
    
    async def trading_analysis(self, 
                             market_data: Dict[str, Any],
                             question: str = None,
                             model_preference: str = None) -> ModelResponse:
        """
        Trading analysis uchun maxsus funksiya
        
        Args:
            market_data: Bozor ma'lumotlari
            question: Aniq savol
            model_preference: Tanlangan model
        
        Returns:
            Trading analysis result
        """
        # Trading-specific prompt engineering
        prompt = f"""
        Trading Analysis Request:
        
        Current Market Data: {json.dumps(market_data, indent=2)}
        
        Question: {question or "Provide comprehensive trading analysis"}
        
        Please provide:
        1. Technical Analysis (trends, support/resistance levels)
        2. Market Sentiment
        3. Risk Assessment
        4. Trading Recommendations
        5. Entry/Exit Points
        
        Focus on actionable insights and quantitative metrics.
        """
        
        # Use trading-specialized model selection
        return await self.chat(
            prompt=prompt,
            strategy="trading_specialized",
            context={"market_data": market_data, "analysis_type": "trading"}
        )
    
    async def multi_model_comparison(self, 
                                   prompt: str,
                                   models: List[ModelType] = None) -> Dict[ModelType, ModelResponse]:
        """
        Bir nechta modelni taqqoslash
        
        Args:
            prompt: Savol
            models: Taqqoslanadigan modellar
        
        Returns:
            Barcha modellarning javoblari
        """
        if models is None:
            models = [ModelType.GPT4O, ModelType.GEMINI_PRO]
        
        results = {}
        
        # Parallel requests
        tasks = []
        for model_type in models:
            task = self._single_model_request(prompt, model_type)
            tasks.append((model_type, task))
        
        # Execute all requests
        for model_type, task in tasks:
            try:
                result = await task
                results[model_type] = result
            except Exception as e:
                logger.error(f"Model {model_type} failed: {e}")
                results[model_type] = ModelResponse(
                    content="",
                    model_used=model_type.value,
                    tokens_used=0,
                    cost=0,
                    response_time=0,
                    quality_score=0,
                    timestamp=datetime.now(),
                    task_type=TaskType.GENERAL_CHAT,
                    error=str(e)
                )
        
        return results
    
    async def _single_model_request(self, prompt: str, model_type: ModelType) -> ModelResponse:
        """Bitta model ga so'rov yuborish"""
        model_config = self.MODEL_CONFIGS[model_type]
        
        if model_config.provider == "openai":
            messages = [{"role": "user", "content": prompt}]
            return self._make_openai_request(model_type.value, messages)
        else:
            return self._make_gemini_request(model_type.value, prompt)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Performance metrikalarini olish"""
        model_stats = {}
        for model_type in self.MODEL_CONFIGS:
            stats = self.evaluator.get_model_stats(model_type.value)
            model_stats[model_type.value] = stats
        
        cache_stats = self.cache.get_stats()
        
        return {
            "models": model_stats,
            "cache": cache_stats,
            "total_requests": sum(stats["total_requests"] for stats in model_stats.values()),
            "active_conversations": len(self.conversations),
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_cache(self):
        """Cache ni tozalash"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def reset_conversations(self):
        """Conversations ni tozalash"""
        self.conversations.clear()
        logger.info("Conversations reset")
    
    def switch_model_strategy(self, strategy: str):
        """Model selection strategy ni o'zgartirish"""
        if strategy in self.model_strategies:
            self.current_strategy = strategy
            logger.info(f"Strategy switched to: {strategy}")
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def get_api_status(self) -> Dict[str, Any]:
        """API status tekshirish"""
        status = {
            "openai": {
                "connected": self.openai_client is not None,
                "rate_limited": False,
                "last_check": datetime.now().isoformat()
            },
            "gemini": {
                "connected": self.gemini_model is not None,
                "rate_limited": False,
                "last_check": datetime.now().isoformat()
            }
        }
        
        # Rate limit status
        for model_type, rate_limiter in self.rate_limiters.items():
            config = self.MODEL_CONFIGS[model_type]
            provider_status = status[config.provider]
            provider_status["rate_limited"] = not rate_limiter.can_make_request()
        
        return status
    
    def optimize_for_cost(self, budget_limit: float) -> Dict[str, Any]:
        """Xarajatlar bo'yicha optimizatsiya"""
        recommendations = []
        
        for model_type, config in self.MODEL_CONFIGS.items():
            stats = self.evaluator.get_model_stats(model_type.value)
            
            if stats["total_requests"] > 0:
                cost_efficiency = stats["avg_quality"] / max(stats["avg_cost"], 0.001)
                recommendations.append({
                    "model": model_type.value,
                    "cost_efficiency": cost_efficiency,
                    "avg_cost": stats["avg_cost"],
                    "avg_quality": stats["avg_quality"],
                    "recommendation": "use" if cost_efficiency > 3.0 else "avoid"
                })
        
        recommendations.sort(key=lambda x: x["cost_efficiency"], reverse=True)
        
        return {
            "budget_limit": budget_limit,
            "recommendations": recommendations,
            "optimal_models": [r["model"] for r in recommendations[:3] if r["recommendation"] == "use"]
        }


# Trading-specific model fine-tuning
class TradingModelOptimizer:
    """Trading uchun model optimizatori"""
    
    def __init__(self, assistant: AdvancedGPTAssistant):
        self.assistant = assistant
        self.trading_templates = self._load_trading_templates()
    
    def _load_trading_templates(self) -> Dict[TaskType, str]:
        """Trading shablonlarini yuklash"""
        return {
            TaskType.TECHNICAL_ANALYSIS: """
            Sen professional trading analyst ekansan. Quyidagi ma'lumotlarni tahlil qil:
            
            Market Data: {market_data}
            
            Talab qilingan tahlil:
            1. Trend tahlili (bullish/bearish)
            2. Support va Resistance darajalari
            3. Volume tahlili
            4. Technical indicators (RSI, MACD, Bollinger Bands)
            5. Short-term va long-term outlook
            6. Entry va Exit pointlar
            7. Risk/Reward ratio
            
            Quantitative metrics bilan javob bering.
            """,
            
            TaskType.TRADING_ANALYSIS: """
            Comprehensive Trading Analysis:
            
            Current Portfolio: {portfolio_data}
            Market Conditions: {market_conditions}
            Economic Indicators: {economic_indicators}
            
            Provide:
            1. Portfolio risk assessment
            2. Market outlook (1D, 1W, 1M)
            3. Asset allocation recommendations
            4. Risk management strategies
            5. Market opportunities
            6. Performance predictions
            """,
            
            TaskType.MARKET_PREDICTION: """
            Market Prediction Request:
            
            Historical Data: {historical_data}
            Current Sentiment: {sentiment_data}
            Economic Events: {events}
            
            Predict:
            1. Price direction (next 24h, 1W)
            2. Volatility expectations
            3. Key support/resistance levels
            4. Market catalysts
            5. Risk factors
            6. Probability scores
            
            Use quantitative analysis and data-driven insights.
            """
        }
    
    def create_trading_prompt(self, 
                            task_type: TaskType, 
                            data: Dict[str, Any]) -> str:
        """Trading prompt yaratish"""
        template = self.trading_templates.get(task_type, "")
        
        if template:
            return template.format(**data)
        else:
            return f"Trading analysis for: {data}"
    
    async def enhanced_trading_analysis(self, 
                                      task_type: TaskType,
                                      data: Dict[str, Any],
                                      user_question: str = None) -> ModelResponse:
        """Kuchaytirilgan trading analizi"""
        prompt = self.create_trading_prompt(task_type, data)
        
        if user_question:
            prompt += f"\n\nSpecific Question: {user_question}"
        
        # Trading-specific context
        context = {
            "analysis_type": "trading",
            "task_type": task_type.value,
            "data_sources": list(data.keys()),
            "trading_timeframe": "real_time"
        }
        
        return await self.assistant.chat(
            prompt=prompt,
            strategy="trading_specialized",
            context=context
        )


# Integration function
def create_ai_assistant(openai_key: str = None, 
                       gemini_key: str = None,
                       enable_trading_optimization: bool = True) -> AdvancedGPTAssistant:
    """
    AI Assistant yaratish
    
    Args:
        openai_key: OpenAI API kaliti
        gemini_key: Gemini API kaliti
        enable_trading_optimization: Trading optimizatsiyasini yoqish
    
    Returns:
        Configured AI Assistant
    """
    assistant = AdvancedGPTAssistant(
        openai_api_key=openai_key,
        gemini_api_key=gemini_key,
        enable_ab_testing=True
    )
    
    if enable_trading_optimization:
        assistant.trading_optimizer = TradingModelOptimizer(assistant)
    
    return assistant


# Usage examples
async def main():
    """Asosiy demo"""
    # API keys environment dan olish
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    # AI Assistant yaratish
    assistant = create_ai_assistant(openai_key, gemini_key)
    
    # Basic chat
    response = await assistant.chat(
        "Bitcoin narxi hozir qanday? Texnik tahlil qiling.",
        strategy="trading_specialized"
    )
    
    print(f"Model: {response.model_used}")
    print(f"Content: {response.content}")
    print(f"Quality: {response.quality_score}")
    print(f"Cost: ${response.cost:.4f}")
    
    # Trading analysis
    if hasattr(assistant, 'trading_optimizer'):
        market_data = {
            "symbol": "BTCUSDT",
            "current_price": 45000,
            "volume": 1000000,
            "rsi": 65,
            "macd": 0.5
        }
        
        trading_response = await assistant.trading_optimizer.enhanced_trading_analysis(
            TaskType.TECHNICAL_ANALYSIS,
            market_data
        )
        
        print(f"Trading Analysis: {trading_response.content}")
    
    # Performance metrics
    metrics = assistant.get_performance_metrics()
    print(f"Performance: {json.dumps(metrics, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())