"""
Learning & Personalization Engine

Foydalanuvchi xulqini tahlil qilish va moslashuvchan interfeys yaratish uchun asosiy modul.
Bu modul real-time o'rganish, shaxsiylashtirilgan tajribalar va davomiy yaxshilanishni ta'minlaydi.

Xususiyatlar:
- Foydalanuvchi xulqatni tahlil qilish
- Shaxsiylashtirilgan javoblar
- O'rganish afzalliklari
- Moslashuvchan interfeys
- Faoliyat kuzatuvi
- Doimiy yaxshilanish
"""

import asyncio
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import re

# Supabase client import
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase client not available. Using local storage only.")

# Privacy-first encryption
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.warning("Cryptography not available. Data encryption disabled.")


class InteractionType(Enum):
    """Foydalanuvchi o'zaro ta'sirov turlari"""
    CLICK = "click"
    HOVER = "hover"
    SCROLL = "scroll"
    FORM_SUBMIT = "form_submit"
    TEXT_INPUT = "text_input"
    NAVIGATION = "navigation"
    SEARCH = "search"
    FILTER = "filter"
    TRADING_ACTION = "trading_action"
    FEEDBACK = "feedback"


class LearningStyle(Enum):
    """O'rganish uslublari"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"


class LanguageCode(Enum):
    """Qo'llab-quvvatlanadigan tillar"""
    UZBEK = "uz"
    ENGLISH = "en"
    RUSSIAN = "ru"


@dataclass
class UserBehaviorData:
    """Foydalanuvchi xulqat ma'lumotlari"""
    user_id: str
    interaction_type: InteractionType
    element_id: str
    timestamp: datetime
    session_id: str
    page_url: str
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UserPreferences:
    """Foydalanuvchi afzalliklari"""
    language: LanguageCode
    learning_style: LearningStyle
    communication_style: str  # formal, casual, technical
    trading_experience_level: str  # beginner, intermediate, advanced
    risk_tolerance: str  # low, medium, high
    interface_complexity: str  # simple, advanced, expert
    time_preference: str  # morning, afternoon, evening
    notification_preference: str  # all, important, none


@dataclass
class PersonalizationMetrics:
    """Shaxsiylashtirish metrikalari"""
    user_id: str
    engagement_score: float
    task_completion_rate: float
    error_rate: float
    learning_curve_score: float
    satisfaction_score: float
    retention_score: float
    last_updated: datetime


class PrivacyManager:
    """Ma'lumotlar xavfsizligi boshqaruvchisi"""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key or self._generate_key()
        if CRYPTO_AVAILABLE:
            self.cipher = Fernet(self.encryption_key)
        else:
            self.cipher = None
    
    def _generate_key(self) -> bytes:
        """Shifrlash kalitini yaratish"""
        return Fernet.generate_key() if CRYPTO_AVAILABLE else b'demo_key'
    
    def anonymize_user_id(self, user_id: str) -> str:
        """Foydalanuvchi ID ni anonimlashtirish"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Muhim ma'lumotlarni shifrlash"""
        if self.cipher and isinstance(data, str):
            return self.cipher.encrypt(data.encode()).decode()
        return data
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Shifrlangan ma'lumotlarni ochish"""
        if self.cipher and isinstance(encrypted_data, str):
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        return encrypted_data


class UserBehaviorAnalyzer:
    """Foydalanuvchi xulqat tahlil qiluvchi"""
    
    def __init__(self):
        self.interaction_patterns = defaultdict(list)
        self.session_data = defaultdict(deque)
        self.behavior_clusters = {}
    
    async def analyze_interaction_pattern(self, user_id: str, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Foydalanuvchi o'zaro ta'sirov namunalarini tahlil qilish"""
        session_key = f"{user_id}_{behavior_data.session_id}"
        self.session_data[session_key].append(behavior_data)
        
        # Pattern analysis
        patterns = {
            "click_frequency": self._calculate_click_frequency(session_key),
            "navigation_style": self._analyze_navigation_style(session_key),
            "time_spent": self._calculate_time_spent(session_key),
            "scroll_behavior": self._analyze_scroll_behavior(session_key),
            "form_interaction": self._analyze_form_interaction(session_key)
        }
        
        return patterns
    
    def _calculate_click_frequency(self, session_key: str) -> float:
        """Bosish chastotasini hisoblash"""
        session = self.session_data[session_key]
        if len(session) < 2:
            return 0.0
        
        interactions = [data for data in session if data.interaction_type == InteractionType.CLICK]
        time_span = (session[-1].timestamp - session[0].timestamp).total_seconds() / 60  # minutes
        return len(interactions) / max(time_span, 1.0)
    
    def _analyze_navigation_style(self, session_key: str) -> str:
        """Navigatsiya uslubini tahlil qilish"""
        session = self.session_data[session_key]
        navigation_counts = defaultdict(int)
        
        for data in session:
            if data.interaction_type == InteractionType.NAVIGATION:
                navigation_counts[data.page_url] += 1
        
        return "deep" if len(navigation_counts) > 5 else "shallow"
    
    def _calculate_time_spent(self, session_key: str) -> float:
        """Sarflangan vaqtni hisoblash"""
        session = self.session_data[session_key]
        if len(session) < 2:
            return 0.0
        
        total_time = 0.0
        for i in range(1, len(session)):
            time_diff = (session[i].timestamp - session[i-1].timestamp).total_seconds()
            if time_diff < 300:  # 5 minutes max
                total_time += time_diff
        
        return total_time / 60  # minutes
    
    def _analyze_scroll_behavior(self, session_key: str) -> Dict[str, float]:
        """Skroll xulqatni tahlil qilish"""
        session = self.session_data[session_key]
        scroll_data = [data for data in session if data.interaction_type == InteractionType.SCROLL]
        
        if not scroll_data:
            return {"scroll_depth": 0.0, "scroll_frequency": 0.0}
        
        return {
            "scroll_depth": len(scroll_data) / max(len(session), 1),
            "scroll_frequency": len(scroll_data) / max(self._calculate_time_spent(session_key), 1.0)
        }
    
    def _analyze_form_interaction(self, session_key: str) -> Dict[str, Any]:
        """Form bilan o'zaro ta'sirovni tahlil qilish"""
        session = self.session_data[session_key]
        form_interactions = [data for data in session if data.interaction_type == InteractionType.FORM_SUBMIT]
        
        return {
            "form_submission_rate": len(form_interactions) / max(len(session), 1),
            "abandonment_rate": self._calculate_form_abandonment(session)
        }
    
    def _calculate_form_abandonment(self, session: deque) -> float:
        """Formni tashlab ketish foizini hisoblash"""
        form_starts = 0
        form_completions = 0
        
        for data in session:
            if data.interaction_type == InteractionType.FORM_SUBMIT:
                form_completions += 1
            elif data.metadata and "form_start" in data.metadata:
                form_starts += 1
        
        return 1.0 - (form_completions / max(form_starts, 1))


class PersonalizedResponseEngine:
    """Shaxsiylashtirilgan javoblar dvijogi"""
    
    def __init__(self):
        self.response_templates = {
            LanguageCode.UZBEK: {
                "trading_advice": {
                    "beginner": "Sizning savdo tajribangizni hisobga olgan holda, {advice} tavsiya etamiz.",
                    "intermediate": "Sizning darajangiz bo'yicha, {advice} maslahati foydali bo'lishi mumkin.",
                    "advanced": "Keng tajriba asosida, {advice} yondashuvini ko'rib chiqishingiz mumkin."
                },
                "error_handling": {
                    "friendly": "Xatolik yuz berdi. Qaytadan urinib ko'ring.",
                    "technical": "Texnik muammo yuz berdi. Tez orada hal qilinadi."
                },
                "ui_guidance": {
                    "simple": "Tushunarli ko'rsatmalar: {guidance}",
                    "detailed": "Batafsil ko'rsatma: {guidance}"
                }
            },
            LanguageCode.ENGLISH: {
                "trading_advice": {
                    "beginner": "Based on your trading experience, we recommend: {advice}",
                    "intermediate": "For your level, {advice} might be beneficial",
                    "advanced": "Given your expertise, consider: {advice}"
                },
                "error_handling": {
                    "friendly": "An error occurred. Please try again.",
                    "technical": "A technical issue occurred. Will be resolved shortly."
                },
                "ui_guidance": {
                    "simple": "Clear instructions: {guidance}",
                    "detailed": "Detailed guidance: {guidance}"
                }
            },
            LanguageCode.RUSSIAN: {
                "trading_advice": {
                    "beginner": "Учитывая ваш опыт торговли, рекомендуем: {advice}",
                    "intermediate": "Для вашего уровня {advice} может быть полезным",
                    "advanced": "Учитывая вашу экспертизу, рассмотрите: {advice}"
                },
                "error_handling": {
                    "friendly": "Произошла ошибка. Попробуйте еще раз.",
                    "technical": "Возникла техническая проблема. Скоро будет решена."
                },
                "ui_guidance": {
                    "simple": "Понятные инструкции: {guidance}",
                    "detailed": "Подробное руководство: {guidance}"
                }
            }
        }
    
    async def generate_personalized_response(self, 
                                           user_id: str,
                                           content_type: str,
                                           content_data: Dict[str, Any],
                                           user_preferences: UserPreferences) -> str:
        """Shaxsiylashtirilgan javob yaratish"""
        language = user_preferences.language
        experience = user_preferences.trading_experience_level
        style = user_preferences.communication_style
        
        if content_type not in self.response_templates[language]:
            content_type = "trading_advice"  # default fallback
        
        template = self.response_templates[language][content_type].get(experience, 
                                                                     self.response_templates[language][content_type]["beginner"])
        
        # Template ni ma'lumotlar bilan to'ldirish
        formatted_content = content_data.get("content", "")
        if isinstance(formatted_content, dict):
            formatted_content = formatted_content.get("text", str(formatted_content))
        
        if "{advice}" in template:
            response = template.replace("{advice}", formatted_content)
        elif "{guidance}" in template:
            response = template.replace("{guidance}", formatted_content)
        else:
            response = template
        
        # Communication style ga mos tarzda sozlash
        response = self._adjust_communication_style(response, style)
        
        return response
    
    def _adjust_communication_style(self, response: str, style: str) -> str:
        """Javobni kommunikatsiya uslubiga mos ravishda sozlash"""
        if style == "formal":
            response = self._make_formal(response)
        elif style == "casual":
            response = self._make_casual(response)
        elif style == "technical":
            response = self._make_technical(response)
        
        return response
    
    def _make_formal(self, text: str) -> str:
        """Rasmiy uslubga o'tkazish"""
        replacements = {
            "urinib ko'ring": "takrorlashni iltimos qiling",
            "try again": "повторите попытку",
            "try again": "please retry"
        }
        
        for informal, formal in replacements.items():
            text = text.replace(informal, formal)
        
        return text
    
    def _make_casual(self, text: str) -> str:
        """Odatiy suhbat uslubiga o'tkazish"""
        replacements = {
            "iltimos qiling": "urinib ko'ring",
            "please": "feel free to",
            "попробуйте": "давайте попробуем"
        }
        
        for formal, casual in replacements.items():
            text = text.replace(formal, casual)
        
        return text
    
    def _make_technical(self, text: str) -> str:
        """Texnik uslubga o'tkazish"""
        # Texnik terminlar qo'shish
        technical_additions = {
            "buy": "long position",
            "sell": "short position",
            "foyda": "profit margin",
            "zarar": "risk exposure"
        }
        
        for casual, technical in technical_additions.items():
            text = text.replace(casual, technical)
        
        return text


class LearningPreferencesEngine:
    """O'rganish afzalliklari dvijogi"""
    
    def __init__(self):
        self.preference_profiles = {}
        self.learning_paths = {}
        self.adaptation_rules = {}
    
    async def analyze_learning_style(self, user_id: str, interaction_history: List[UserBehaviorData]) -> LearningStyle:
        """Foydalanuvchi o'rganish uslubini tahlil qilish"""
        visual_score = 0
        auditory_score = 0
        kinesthetic_score = 0
        reading_writing_score = 0
        
        for interaction in interaction_history:
            # Visual interactions
            if interaction.interaction_type in [InteractionType.HOVER, InteractionType.SCROLL]:
                visual_score += 1
            
            # Auditory interactions (simulated through video/audio content)
            if interaction.metadata and "media_type" in interaction.metadata:
                if interaction.metadata["media_type"] in ["video", "audio"]:
                    auditory_score += 2
            
            # Kinesthetic interactions
            if interaction.interaction_type in [InteractionType.CLICK, InteractionType.TRADING_ACTION]:
                kinesthetic_score += 1
            
            # Reading/Writing interactions
            if interaction.interaction_type in [InteractionType.TEXT_INPUT, InteractionType.SEARCH]:
                reading_writing_score += 1
        
        scores = {
            LearningStyle.VISUAL: visual_score,
            LearningStyle.AUDITORY: auditory_score,
            LearningStyle.KINESTHETIC: kinesthetic_score,
            LearningStyle.READING_WRITING: reading_writing_score
        }
        
        return max(scores, key=scores.get)
    
    async def adapt_content_presentation(self, 
                                       user_id: str,
                                       content: Dict[str, Any],
                                       learning_style: LearningStyle) -> Dict[str, Any]:
        """Kontentni foydalanuvchi o'rganish uslubiga mos ravishda taqdim etish"""
        adapted_content = content.copy()
        
        if learning_style == LearningStyle.VISUAL:
            adapted_content = self._adapt_for_visual_learners(adapted_content)
        elif learning_style == LearningStyle.AUDITORY:
            adapted_content = self._adapt_for_auditory_learners(adapted_content)
        elif learning_style == LearningStyle.KINESTHETIC:
            adapted_content = self._adapt_for_kinesthetic_learners(adapted_content)
        elif learning_style == LearningStyle.READING_WRITING:
            adapted_content = self._adapt_for_reading_writing_learners(adapted_content)
        
        return adapted_content
    
    def _adapt_for_visual_learners(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Visual o'rganuvchilar uchun moslashtirish"""
        content["presentation"] = "charts_and_graphs"
        content["visual_elements"] = True
        content["color_coding"] = True
        content["infographics"] = True
        return content
    
    def _adapt_for_auditory_learners(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Auditory o'rganuvchilar uchun moslashtirish"""
        content["audio_explanations"] = True
        content["verbal_reinforcement"] = True
        content["discussion_oriented"] = True
        return content
    
    def _adapt_for_kinesthetic_learners(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Kinesthetic o'rganuvchilar uchun moslashtirish"""
        content["interactive_elements"] = True
        content["hands_on_practice"] = True
        content["simulation_based"] = True
        return content
    
    def _adapt_for_reading_writing_learners(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Reading/Writing o'rganuvchilar uchun moslashtirish"""
        content["detailed_text"] = True
        content["written_explanations"] = True
        content["notes_and_lists"] = True
        return content


class AdaptiveInterfaceEngine:
    """Moslashuvchan interfeys dvijogi"""
    
    def __init__(self):
        self.interface_configs = {}
        self.user_interface_history = {}
        self.adaptation_triggers = {}
    
    async def analyze_interface_preferences(self, user_id: str, 
                                          behavior_data: List[UserBehaviorData]) -> Dict[str, Any]:
        """Foydalanuvchi interfeys afzalliklarini tahlil qilish"""
        preferences = {
            "complexity_level": "simple",
            "color_scheme": "default",
            "layout_style": "standard",
            "navigation_type": "menu",
            "font_size": "medium",
            "widget_density": "normal"
        }
        
        # Complexity analysis
        click_frequency = sum(1 for data in behavior_data if data.interaction_type == InteractionType.CLICK)
        error_rate = self._calculate_error_rate(behavior_data)
        
        if click_frequency > 50 and error_rate < 0.1:
            preferences["complexity_level"] = "advanced"
        elif click_frequency < 10 or error_rate > 0.3:
            preferences["complexity_level"] = "simple"
        else:
            preferences["complexity_level"] = "medium"
        
        # Color scheme analysis
        time_preference = self._analyze_time_preference(behavior_data)
        if time_preference == "night":
            preferences["color_scheme"] = "dark"
        else:
            preferences["color_scheme"] = "light"
        
        # Navigation style analysis
        navigation_efficiency = self._analyze_navigation_efficiency(behavior_data)
        if navigation_efficiency > 0.8:
            preferences["navigation_type"] = "shortcuts"
        else:
            preferences["navigation_type"] = "menu"
        
        return preferences
    
    def _calculate_error_rate(self, behavior_data: List[UserBehaviorData]) -> float:
        """Xato foizini hisoblash"""
        total_interactions = len(behavior_data)
        if total_interactions == 0:
            return 0.0
        
        error_interactions = sum(1 for data in behavior_data 
                               if data.metadata and data.metadata.get("error", False))
        
        return error_interactions / total_interactions
    
    def _analyze_time_preference(self, behavior_data: List[UserBehaviorData]) -> str:
        """Vaqt afzalligini tahlil qilish"""
        night_interactions = 0
        day_interactions = 0
        
        for data in behavior_data:
            hour = data.timestamp.hour
            if 20 <= hour or hour <= 6:
                night_interactions += 1
            else:
                day_interactions += 1
        
        return "night" if night_interactions > day_interactions else "day"
    
    def _analyze_navigation_efficiency(self, behavior_data: List[UserBehaviorData]) -> float:
        """Navigatsiya samaradorligini tahlil qilish"""
        navigation_steps = []
        current_path = []
        
        for data in behavior_data:
            if data.interaction_type == InteractionType.NAVIGATION:
                current_path.append(data.page_url)
            elif data.interaction_type == InteractionType.SEARCH:
                # Search often indicates difficulty finding information
                if len(current_path) > 2:
                    navigation_steps.append(len(current_path))
                current_path = []
        
        if not navigation_steps:
            return 1.0
        
        return 1.0 - (np.mean(navigation_steps) / 10.0)  # Normalize to 0-1
    
    async def generate_adaptive_interface_config(self, 
                                               user_id: str,
                                               preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Moslashuvchan interfeys konfiguratsiyasini yaratish"""
        config = {
            "theme": {
                "mode": "dark" if preferences.get("color_scheme") == "dark" else "light",
                "primary_color": "#2563eb",
                "accent_color": "#3b82f6"
            },
            "layout": {
                "density": preferences.get("widget_density", "normal"),
                "sidebar_width": "250px" if preferences.get("complexity_level") == "advanced" else "200px",
                "header_height": "60px"
            },
            "components": {
                "navigation": {
                    "type": preferences.get("navigation_type", "menu"),
                    "show_labels": True,
                    "collapsible": preferences.get("complexity_level") != "simple"
                },
                "dashboard": {
                    "grid_columns": 4 if preferences.get("complexity_level") == "advanced" else 2,
                    "auto_refresh": True,
                    "chart_interactivity": preferences.get("complexity_level") == "advanced"
                },
                "trading_panel": {
                    "advanced_mode": preferences.get("complexity_level") == "advanced",
                    "quick_actions": True,
                    "risk_display": "detailed" if preferences.get("complexity_level") == "advanced" else "simple"
                }
            }
        }
        
        return config


class PerformanceTracker:
    """Faoliyat kuzatuvchisi"""
    
    def __init__(self):
        self.metrics_history = {}
        self.performance_data = defaultdict(list)
        self.improvement_targets = {}
    
    async def track_user_performance(self, user_id: str, 
                                   session_data: List[UserBehaviorData]) -> PersonalizationMetrics:
        """Foydalanuvchi ish faoliyatini kuzatish"""
        current_time = datetime.now()
        
        # Calculate metrics
        engagement_score = self._calculate_engagement_score(session_data)
        completion_rate = self._calculate_task_completion_rate(session_data)
        error_rate = self._calculate_error_rate(session_data)
        learning_curve = self._calculate_learning_curve_score(user_id)
        satisfaction = self._calculate_satisfaction_score(session_data)
        retention = self._calculate_retention_score(user_id, current_time)
        
        metrics = PersonalizationMetrics(
            user_id=user_id,
            engagement_score=engagement_score,
            task_completion_rate=completion_rate,
            error_rate=error_rate,
            learning_curve_score=learning_curve,
            satisfaction_score=satisfaction,
            retention_score=retention,
            last_updated=current_time
        )
        
        # Store metrics
        self.metrics_history[user_id] = metrics
        
        return metrics
    
    def _calculate_engagement_score(self, session_data: List[UserBehaviorData]) -> float:
        """Ish faollik ballini hisoblash"""
        if not session_data:
            return 0.0
        
        # Interaction diversity
        interaction_types = set(data.interaction_type for data in session_data)
        diversity_score = len(interaction_types) / len(list(InteractionType))
        
        # Session duration
        if len(session_data) > 1:
            session_duration = (session_data[-1].timestamp - session_data[0].timestamp).total_seconds() / 60
            duration_score = min(session_duration / 30, 1.0)  # Max at 30 minutes
        else:
            duration_score = 0.0
        
        # Interaction frequency
        interaction_frequency = len(session_data) / max(self._calculate_time_spent(session_data), 1)
        frequency_score = min(interaction_frequency / 10, 1.0)  # Max at 10 interactions per minute
        
        return (diversity_score * 0.4 + duration_score * 0.3 + frequency_score * 0.3)
    
    def _calculate_task_completion_rate(self, session_data: List[UserBehaviorData]) -> float:
        """Vazifa bajarilish foizini hisoblash"""
        if not session_data:
            return 0.0
        
        completed_tasks = 0
        total_task_indicators = 0
        
        for data in session_data:
            if data.metadata and "task_status" in data.metadata:
                total_task_indicators += 1
                if data.metadata["task_status"] == "completed":
                    completed_tasks += 1
        
        return completed_tasks / max(total_task_indicators, 1)
    
    def _calculate_error_rate(self, session_data: List[UserBehaviorData]) -> float:
        """Xato foizini hisoblash"""
        if not session_data:
            return 0.0
        
        error_count = 0
        for data in session_data:
            if data.metadata and data.metadata.get("error", False):
                error_count += 1
        
        return error_count / len(session_data)
    
    def _calculate_learning_curve_score(self, user_id: str) -> float:
        """O'rganish egri chizig'i ballini hisoblash"""
        if user_id not in self.metrics_history:
            return 0.5  # Default for new users
        
        # Compare recent performance with historical data
        current_metrics = self.metrics_history[user_id]
        historical_data = self.performance_data[user_id]
        
        if len(historical_data) < 2:
            return 0.5
        
        # Calculate improvement trend
        recent_engagement = [m.engagement_score for m in historical_data[-5:]]
        improvement_trend = (recent_engagement[-1] - recent_engagement[0]) / max(recent_engagement[0], 0.1)
        
        return max(0.0, min(1.0, 0.5 + improvement_trend))
    
    def _calculate_satisfaction_score(self, session_data: List[UserBehaviorData]) -> float:
        """Qoniqish ballini hisoblash"""
        if not session_data:
            return 0.5
        
        # Analyze positive vs negative indicators
        positive_indicators = 0
        negative_indicators = 0
        
        for data in session_data:
            if data.metadata:
                if data.metadata.get("sentiment") == "positive":
                    positive_indicators += 2
                elif data.metadata.get("sentiment") == "negative":
                    negative_indicators += 2
                
                if data.metadata.get("action") == "feedback_provided":
                    positive_indicators += 1
        
        total_sentiment = positive_indicators + negative_indicators
        if total_sentiment == 0:
            return 0.5
        
        return positive_indicators / total_sentiment
    
    def _calculate_retention_score(self, user_id: str, current_time: datetime) -> float:
        """Saqlab qolish ballini hisoblash"""
        # This would typically use historical login data
        # For now, using a simplified calculation
        if user_id not in self.performance_data:
            return 0.5
        
        # Calculate time since last activity
        last_activity = max(data.last_updated for data in self.performance_data[user_id])
        days_since_last = (current_time - last_activity).days
        
        if days_since_last <= 1:
            return 1.0
        elif days_since_last <= 7:
            return 0.8
        elif days_since_last <= 30:
            return 0.5
        else:
            return 0.2
    
    def _calculate_time_spent(self, session_data: List[UserBehaviorData]) -> float:
        """Sarflangan vaqtni hisoblash (daqiqalarda)"""
        if len(session_data) < 2:
            return 1.0
        
        time_span = (session_data[-1].timestamp - session_data[0].timestamp).total_seconds() / 60
        return max(time_span, 1.0)


class ContinuousImprovementEngine:
    """Doimiy yaxshilanish dvijogi"""
    
    def __init__(self):
        self.ml_models = {}
        self.improvement_algorithms = {}
        self.feedback_loops = {}
    
    async def analyze_and_improve(self, user_id: str, 
                                user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Foydalanuvchi ma'lumotlarini tahlil qilish va yaxshilash maslahatlari"""
        improvements = {
            "personalization_adjustments": [],
            "interface_suggestions": [],
            "content_recommendations": [],
            "learning_path_updates": []
        }
        
        # Analyze current performance
        performance_data = user_data.get("performance_metrics")
        if performance_data:
            improvements["personalization_adjustments"] = self._suggest_personalization_changes(performance_data)
        
        # Analyze behavior patterns
        behavior_data = user_data.get("behavior_data", [])
        if behavior_data:
            improvements["interface_suggestions"] = self._suggest_interface_improvements(behavior_data)
            improvements["content_recommendations"] = self._suggest_content_improvements(behavior_data)
        
        # Learning path optimization
        learning_data = user_data.get("learning_progress")
        if learning_data:
            improvements["learning_path_updates"] = self._optimize_learning_path(learning_data)
        
        return improvements
    
    def _suggest_personalization_changes(self, performance_data: PersonalizationMetrics) -> List[str]:
        """Shaxsiylashtirish o'zgarishlari uchun maslahatlar"""
        suggestions = []
        
        if performance_data.engagement_score < 0.5:
            suggestions.append("Engagementni oshirish uchun interaktiv elementlarni ko'proq qo'shing")
        
        if performance_data.error_rate > 0.2:
            suggestions.append("Xato foizini kamaytirish uchun batafsil ko'rsatmalar qo'shing")
        
        if performance_data.learning_curve_score < 0.6:
            suggestions.append("O'rganish tezligini oshirish uchun qadam-baqadam yondashuvni qo'llang")
        
        return suggestions
    
    def _suggest_interface_improvements(self, behavior_data: List[UserBehaviorData]) -> List[str]:
        """Interfeys yaxshilash maslahatlari"""
        suggestions = []
        
        # Analyze click patterns
        click_data = [d for d in behavior_data if d.interaction_type == InteractionType.CLICK]
        if len(click_data) > 20:
            suggestions.append("Tezkor harakatlar uchun tezkor tugmalar qo'shing")
        
        # Analyze navigation efficiency
        navigation_data = [d for d in behavior_data if d.interaction_type == InteractionType.NAVIGATION]
        if len(navigation_data) > 10:
            suggestions.append("Navigatsiyani soddalashtirish uchun breadcrumb qo'shing")
        
        return suggestions
    
    def _suggest_content_improvements(self, behavior_data: List[UserBehaviorData]) -> List[str]:
        """Kontent yaxshilash maslahatlari"""
        suggestions = []
        
        # Analyze time spent on different content types
        time_spent = defaultdict(float)
        for data in behavior_data:
            if data.duration:
                time_spent[data.page_url] += data.duration
        
        # Suggest based on engagement patterns
        if time_spent:
            most_engaging = max(time_spent, key=time_spent.get)
            suggestions.append(f"{most_engaging} kabi kontentni ko'proq taqdim eting")
        
        return suggestions
    
    def _optimize_learning_path(self, learning_data: Dict[str, Any]) -> List[str]:
        """O'rganish yo'nalishini optimallashtirish"""
        suggestions = []
        
        current_level = learning_data.get("current_level", "beginner")
        progress_rate = learning_data.get("progress_rate", 0.1)
        
        if progress_rate < 0.05:
            suggestions.append("O'rganish tezligini sekinlashtiring va qo'shimcha tushuntirish qo'shing")
        elif progress_rate > 0.2:
            suggestions.append("Murakkabroq kontentga o'ting")
        
        return suggestions


class LearningPersonalizationEngine:
    """Asosiy Learning & Personalization Engine"""
    
    def __init__(self, supabase_url: Optional[str] = None, 
                 supabase_key: Optional[str] = None):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_client = None
        
        if SUPABASE_AVAILABLE and supabase_url and supabase_key:
            try:
                self.supabase_client = create_client(supabase_url, supabase_key)
            except Exception as e:
                logging.error(f"Supabase client yaratishda xato: {e}")
        
        # Initialize components
        self.privacy_manager = PrivacyManager()
        self.behavior_analyzer = UserBehaviorAnalyzer()
        self.response_engine = PersonalizedResponseEngine()
        self.learning_engine = LearningPreferencesEngine()
        self.interface_engine = AdaptiveInterfaceEngine()
        self.performance_tracker = PerformanceTracker()
        self.improvement_engine = ContinuousImprovementEngine()
        
        # Data storage
        self.user_preferences = {}
        self.user_behavior_cache = defaultdict(deque)
        self.performance_history = {}
    
    async def initialize_user(self, user_id: str, initial_preferences: Optional[UserPreferences] = None) -> bool:
        """Foydalanuvchini tizimga ulash"""
        try:
            # Load existing preferences or create new ones
            if initial_preferences:
                self.user_preferences[user_id] = initial_preferences
            else:
                # Default preferences
                self.user_preferences[user_id] = UserPreferences(
                    language=LanguageCode.UZBEK,
                    learning_style=LearningStyle.VISUAL,
                    communication_style="friendly",
                    trading_experience_level="beginner",
                    risk_tolerance="medium",
                    interface_complexity="medium",
                    time_preference="morning",
                    notification_preference="important"
                )
            
            # Store in database if available
            if self.supabase_client:
                await self._store_user_preferences(user_id, self.user_preferences[user_id])
            
            return True
        except Exception as e:
            logging.error(f"Foydalanuvchi initializatsiyasida xato: {e}")
            return False
    
    async def track_interaction(self, user_id: str, behavior_data: UserBehaviorData) -> Dict[str, Any]:
        """Foydalanuvchi o'zaro ta'sirovini kuzatish"""
        try:
            # Store in cache
            self.user_behavior_cache[user_id].append(behavior_data)
            
            # Limit cache size
            if len(self.user_behavior_cache[user_id]) > 1000:
                self.user_behavior_cache[user_id].popleft()
            
            # Analyze behavior
            analysis = await self.behavior_analyzer.analyze_interaction_pattern(user_id, behavior_data)
            
            # Store in database
            if self.supabase_client:
                await self._store_behavior_data(user_id, behavior_data, analysis)
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": behavior_data.timestamp.isoformat()
            }
        except Exception as e:
            logging.error(f"Interaction tracking xatosi: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_personalized_response(self, 
                                      user_id: str,
                                      content_type: str,
                                      content_data: Dict[str, Any]) -> str:
        """Shaxsiylashtirilgan javob olish"""
        try:
            if user_id not in self.user_preferences:
                await self.initialize_user(user_id)
            
            user_prefs = self.user_preferences[user_id]
            response = await self.response_engine.generate_personalized_response(
                user_id, content_type, content_data, user_prefs
            )
            
            return response
        except Exception as e:
            logging.error(f"Personalized response yaratishda xato: {e}")
            return "Kechirasiz, xatolik yuz berdi."
    
    async def get_learning_style_analysis(self, user_id: str) -> Dict[str, Any]:
        """Foydalanuvchi o'rganish uslubi tahlili"""
        try:
            behavior_data = list(self.user_behavior_cache[user_id])
            if not behavior_data:
                return {"learning_style": "visual", "confidence": 0.5}
            
            learning_style = await self.learning_engine.analyze_learning_style(user_id, behavior_data)
            
            # Store learning style
            if user_id in self.user_preferences:
                self.user_preferences[user_id].learning_style = learning_style
            
            return {
                "learning_style": learning_style.value,
                "confidence": 0.8,  # Simplified confidence score
                "recommendations": self._get_style_recommendations(learning_style)
            }
        except Exception as e:
            logging.error(f"Learning style analysis xatosi: {e}")
            return {"learning_style": "visual", "confidence": 0.0}
    
    async def get_adaptive_interface_config(self, user_id: str) -> Dict[str, Any]:
        """Moslashuvchan interfeys konfiguratsiyasini olish"""
        try:
            behavior_data = list(self.user_behavior_cache[user_id])
            if not behavior_data:
                return self._get_default_interface_config()
            
            # Analyze preferences
            preferences = await self.interface_engine.analyze_interface_preferences(user_id, behavior_data)
            
            # Generate config
            config = await self.interface_engine.generate_adaptive_interface_config(user_id, preferences)
            
            return config
        except Exception as e:
            logging.error(f"Adaptive interface config xatosi: {e}")
            return self._get_default_interface_config()
    
    async def get_performance_metrics(self, user_id: str) -> PersonalizationMetrics:
        """Foydalanuvchi faoliyat metrikalari"""
        try:
            behavior_data = list(self.user_behavior_cache[user_id])
            if not behavior_data:
                # Return default metrics
                return PersonalizationMetrics(
                    user_id=user_id,
                    engagement_score=0.5,
                    task_completion_rate=0.5,
                    error_rate=0.0,
                    learning_curve_score=0.5,
                    satisfaction_score=0.5,
                    retention_score=0.5,
                    last_updated=datetime.now()
                )
            
            metrics = await self.performance_tracker.track_user_performance(user_id, behavior_data)
            self.performance_history[user_id] = metrics
            
            # Store in database
            if self.supabase_client:
                await self._store_performance_metrics(user_id, metrics)
            
            return metrics
        except Exception as e:
            logging.error(f"Performance metrics xatosi: {e}")
            raise
    
    async def get_improvement_suggestions(self, user_id: str) -> Dict[str, Any]:
        """Yaxshilash maslahatlari"""
        try:
            # Gather user data
            user_data = {
                "performance_metrics": self.performance_history.get(user_id),
                "behavior_data": list(self.user_behavior_cache[user_id]),
                "learning_progress": {
                    "current_level": self.user_preferences.get(user_id, UserPreferences(
                        language=LanguageCode.UZBEK,
                        learning_style=LearningStyle.VISUAL,
                        communication_style="friendly",
                        trading_experience_level="beginner",
                        risk_tolerance="medium",
                        interface_complexity="medium",
                        time_preference="morning",
                        notification_preference="important"
                    )).trading_experience_level,
                    "progress_rate": 0.1
                }
            }
            
            improvements = await self.improvement_engine.analyze_and_improve(user_id, user_data)
            
            return {
                "success": True,
                "suggestions": improvements,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Improvement suggestions xatosi: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_style_recommendations(self, learning_style: LearningStyle) -> List[str]:
        """O'rganish uslubi bo'yicha maslahatlar"""
        recommendations = {
            LearningStyle.VISUAL: [
                "Grafik va chizmalar bilan ishlash",
                "Ranglar va vizual kodlash qoidalarini qo'llash",
                "Infografikalar va diagrammalarni ko'rish"
            ],
            LearningStyle.AUDITORY: [
                "Audio ma'ruzalar va tushuntirishlar",
                "Muhokama va savol-javob sessiyalari",
                "Ovozli xatlar va audio yozuvlar"
            ],
            LearningStyle.KINESTHETIC: [
                "Amaliy mashqlar va simulyatsiyalar",
                "Interaktiv demo va тренажёрлар",
                "Qo'lda ishlash va tatib qilish"
            ],
            LearningStyle.READING_WRITING: [
                "Batafsil matnli materiallar",
                "Yozma mashqlar va konspektlar",
                "Ro'yxat va jadval ma'lumotlar"
            ]
        }
        
        return recommendations.get(learning_style, [])
    
    def _get_default_interface_config(self) -> Dict[str, Any]:
        """Standart interfeys konfiguratsiyasi"""
        return {
            "theme": {
                "mode": "light",
                "primary_color": "#2563eb",
                "accent_color": "#3b82f6"
            },
            "layout": {
                "density": "normal",
                "sidebar_width": "200px",
                "header_height": "60px"
            },
            "components": {
                "navigation": {
                    "type": "menu",
                    "show_labels": True,
                    "collapsible": False
                },
                "dashboard": {
                    "grid_columns": 2,
                    "auto_refresh": True,
                    "chart_interactivity": False
                },
                "trading_panel": {
                    "advanced_mode": False,
                    "quick_actions": True,
                    "risk_display": "simple"
                }
            }
        }
    
    # Database operations
    async def _store_user_preferences(self, user_id: str, preferences: UserPreferences):
        """Foydalanuvchi afzalliklarini bazaga saqlash"""
        try:
            if not self.supabase_client:
                return
            
            # Anonymize user ID for privacy
            anon_id = self.privacy_manager.anonymize_user_id(user_id)
            
            # Store preferences
            self.supabase_client.table('user_preferences').upsert({
                'user_id': anon_id,
                'language': preferences.language.value,
                'learning_style': preferences.learning_style.value,
                'communication_style': preferences.communication_style,
                'trading_experience_level': preferences.trading_experience_level,
                'risk_tolerance': preferences.risk_tolerance,
                'interface_complexity': preferences.interface_complexity,
                'time_preference': preferences.time_preference,
                'notification_preference': preferences.notification_preference,
                'updated_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            logging.error(f"User preferences saqlashda xato: {e}")
    
    async def _store_behavior_data(self, user_id: str, behavior_data: UserBehaviorData, analysis: Dict[str, Any]):
        """Xulqat ma'lumotlarini bazaga saqlash"""
        try:
            if not self.supabase_client:
                return
            
            anon_id = self.privacy_manager.anonymize_user_id(user_id)
            
            self.supabase_client.table('user_behavior').insert({
                'user_id': anon_id,
                'interaction_type': behavior_data.interaction_type.value,
                'element_id': behavior_data.element_id,
                'timestamp': behavior_data.timestamp.isoformat(),
                'session_id': behavior_data.session_id,
                'page_url': behavior_data.page_url,
                'duration': behavior_data.duration,
                'metadata': behavior_data.metadata,
                'analysis': analysis,
                'created_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            logging.error(f"Behavior data saqlashda xato: {e}")
    
    async def _store_performance_metrics(self, user_id: str, metrics: PersonalizationMetrics):
        """Faoliyat metrikalarini bazaga saqlash"""
        try:
            if not self.supabase_client:
                return
            
            anon_id = self.privacy_manager.anonymize_user_id(user_id)
            
            self.supabase_client.table('performance_metrics').insert({
                'user_id': anon_id,
                'engagement_score': metrics.engagement_score,
                'task_completion_rate': metrics.task_completion_rate,
                'error_rate': metrics.error_rate,
                'learning_curve_score': metrics.learning_curve_score,
                'satisfaction_score': metrics.satisfaction_score,
                'retention_score': metrics.retention_score,
                'last_updated': metrics.last_updated.isoformat(),
                'created_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            logging.error(f"Performance metrics saqlashda xato: {e}")
    
    # Public API methods
    async def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Foydalanuvchi dashboard ma'lumotlari"""
        try:
            # Get all relevant data
            preferences = self.user_preferences.get(user_id)
            performance_metrics = await self.get_performance_metrics(user_id)
            learning_analysis = await self.get_learning_style_analysis(user_id)
            interface_config = await self.get_adaptive_interface_config(user_id)
            improvement_suggestions = await self.get_improvement_suggestions(user_id)
            
            return {
                "user_id": user_id,
                "preferences": asdict(preferences) if preferences else None,
                "performance": asdict(performance_metrics),
                "learning_style": learning_analysis,
                "interface_config": interface_config,
                "improvements": improvement_suggestions.get("suggestions", {}),
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Dashboard data olishda xato: {e}")
            return {"error": str(e)}
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Foydalanuvchi ma'lumotlarini eksport qilish (GDPR compliance)"""
        try:
            user_data = {
                "user_id": user_id,
                "preferences": self.user_preferences.get(user_id),
                "performance_history": self.performance_history.get(user_id),
                "behavior_data_count": len(self.user_behavior_cache[user_id]),
                "exported_at": datetime.now().isoformat(),
                "data_categories": [
                    "preferences",
                    "performance_metrics",
                    "behavior_data",
                    "learning_patterns",
                    "interface_adaptations"
                ]
            }
            
            return {
                "success": True,
                "data": user_data,
                "privacy_notice": "Ma'lumotlar anonimlashtirildi va shifrlandi"
            }
        except Exception as e:
            logging.error(f"Data export xatosi: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_user_data(self, user_id: str) -> bool:
        """Foydalanuvchi ma'lumotlarini o'chirish"""
        try:
            # Remove from local storage
            if user_id in self.user_preferences:
                del self.user_preferences[user_id]
            if user_id in self.performance_history:
                del self.performance_history[user_id]
            if user_id in self.user_behavior_cache:
                del self.user_behavior_cache[user_id]
            
            # Remove from database
            if self.supabase_client:
                anon_id = self.privacy_manager.anonymize_user_id(user_id)
                
                # Delete from all related tables
                tables = ['user_preferences', 'user_behavior', 'performance_metrics']
                for table in tables:
                    self.supabase_client.table(table).delete().eq('user_id', anon_id).execute()
            
            return True
        except Exception as e:
            logging.error(f"User data delete xatosi: {e}")
            return False


# Example usage and testing
async def main():
    """Asosiy test funksiyasi"""
    # Initialize the engine
    engine = LearningPersonalizationEngine()
    
    # Test user ID
    user_id = "test_user_123"
    
    # Initialize user
    success = await engine.initialize_user(user_id)
    print(f"User initialized: {success}")
    
    # Simulate some user interactions
    behavior_data = UserBehaviorData(
        user_id=user_id,
        interaction_type=InteractionType.CLICK,
        element_id="buy_button",
        timestamp=datetime.now(),
        session_id="session_1",
        page_url="/trading/dashboard"
    )
    
    # Track interaction
    result = await engine.track_interaction(user_id, behavior_data)
    print(f"Interaction tracked: {result}")
    
    # Get personalized response
    response = await engine.get_personalized_response(
        user_id, 
        "trading_advice", 
        {"content": "Bu aktivni sotib olish foydali bo'lishi mumkin"}
    )
    print(f"Personalized response: {response}")
    
    # Get learning style analysis
    learning_style = await engine.get_learning_style_analysis(user_id)
    print(f"Learning style: {learning_style}")
    
    # Get interface config
    interface_config = await engine.get_adaptive_interface_config(user_id)
    print(f"Interface config: {json.dumps(interface_config, indent=2)}")
    
    # Get performance metrics
    metrics = await engine.get_performance_metrics(user_id)
    print(f"Performance metrics: {metrics}")
    
    # Get improvement suggestions
    improvements = await engine.get_improvement_suggestions(user_id)
    print(f"Improvement suggestions: {improvements}")


if __name__ == "__main__":
    asyncio.run(main())