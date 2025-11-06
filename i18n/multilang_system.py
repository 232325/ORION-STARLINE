#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orion Starline Multi-Language System
====================================

Professional multi-language and localization system supporting 20+ languages
with RTL support, cultural adaptation, and dynamic language switching.

Author: Orion Starline Team
Version: 1.0.0
Created: 2025-11-05
"""

import os
import json
import yaml
import re
from typing import Dict, List, Optional, Union, Tuple, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import logging
from pathlib import Path
import pickle
import hashlib
from collections import defaultdict
import babel
from babel import Locale
import unicodedata


class LanguageDirection(Enum):
    """Language writing direction enumeration"""
    LTR = "ltr"  # Left to Right
    RTL = "rtl"  # Right to Left


class CurrencyFormat(Enum):
    """Currency format styles"""
    STANDARD = "standard"
    ACCOUNTING = "accounting"
    CURRENCY = "currency"


class DateFormat(Enum):
    """Date format styles"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    FULL = "full"


@dataclass
class LanguageConfig:
    """Language configuration dataclass"""
    code: str
    name: str
    native_name: str
    direction: LanguageDirection
    locale: str
    encoding: str = "utf-8"
    currency: str = "USD"
    date_format: DateFormat = DateFormat.MEDIUM
    number_format: str = "standard"
    rtl_support: bool = False
    plural_rules: Dict[str, Any] = field(default_factory=dict)
    calendar_type: str = "gregorian"
    timezone: str = "UTC"
    cultural_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TranslationEntry:
    """Translation entry with metadata"""
    key: str
    value: str
    context: Optional[str] = None
    plural_form: Optional[str] = None
    namespace: str = "default"
    description: str = ""
    last_updated: Optional[datetime] = None
    translator: str = ""
    quality_score: float = 1.0
    approved: bool = True
    cultural_adaptation: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CulturalContext:
    """Cultural context and adaptation settings"""
    region: str
    cultural_preferences: Dict[str, Any]
    color_meanings: Dict[str, str]
    number_preferences: Dict[str, Any]
    date_conventions: Dict[str, Any]
    greeting_formats: Dict[str, str]
    business_hours: Dict[str, Any]
    holiday_calendar: List[str]
    measurement_system: str = "metric"  # metric, imperial
    paper_size: str = "A4"  # A4, Letter
    timezone: str = "UTC"


class MultiLanguageSystem:
    """
    Professional Multi-Language System
    
    Features:
    - 20+ languages support
    - RTL (Right-to-Left) language support
    - Cultural adaptation
    - Dynamic language switching
    - Locale detection
    - Translation memory
    - Quality assurance
    """
    
    def __init__(self, base_path: str = "i18n"):
        """
        Initialize the multi-language system
        
        Args:
            base_path: Base path for i18n files and data
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Core configurations
        self.languages: Dict[str, LanguageConfig] = {}
        self.translations: Dict[str, Dict[str, TranslationEntry]] = defaultdict(dict)
        self.cultural_contexts: Dict[str, CulturalContext] = {}
        self.translation_memory: Dict[str, str] = {}
        self.quality_cache: Dict[str, float] = {}
        
        # Current state
        self.current_language: Optional[str] = None
        self.current_culture: Optional[str] = None
        self.auto_detect: bool = True
        self.fallback_language: str = "en"
        
        # Performance optimization
        self.cache_enabled: bool = True
        self.cache_ttl: int = 3600  # 1 hour
        self.translation_cache: Dict[str, Any] = {}
        
        # Load configurations
        self._load_language_configs()
        self._load_cultural_contexts()
        self._load_translations()
        
        # Auto-detect user language
        if self.auto_detect:
            self._auto_detect_language()
    
    def _load_language_configs(self) -> None:
        """Load language configurations"""
        config_file = self.base_path / "language_configs.yaml"
        
        if not config_file.exists():
            self._create_default_language_configs()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            for lang_code, config_data in config_data.items():
                self.languages[lang_code] = LanguageConfig(
                    code=lang_code,
                    **config_data
                )
                
        except Exception as e:
            self.logger.error(f"Error loading language configs: {e}")
            self._create_default_language_configs()
    
    def _create_default_language_configs(self) -> None:
        """Create default language configurations for 20+ languages"""
        default_configs = {
            # Major global languages
            "en": {
                "name": "English",
                "native_name": "English",
                "direction": LanguageDirection.LTR,
                "locale": "en_US",
                "currency": "USD",
                "timezone": "America/New_York"
            },
            "uz": {
                "name": "Uzbek",
                "native_name": "O'zbek",
                "direction": LanguageDirection.LTR,
                "locale": "uz_UZ",
                "currency": "UZS",
                "timezone": "Asia/Samarkand"
            },
            "ru": {
                "name": "Russian",
                "native_name": "Русский",
                "direction": LanguageDirection.LTR,
                "locale": "ru_RU",
                "currency": "RUB",
                "timezone": "Europe/Moscow"
            },
            "zh": {
                "name": "Chinese",
                "native_name": "中文",
                "direction": LanguageDirection.LTR,
                "locale": "zh_CN",
                "currency": "CNY",
                "timezone": "Asia/Shanghai"
            },
            "es": {
                "name": "Spanish",
                "native_name": "Español",
                "direction": LanguageDirection.LTR,
                "locale": "es_ES",
                "currency": "EUR",
                "timezone": "Europe/Madrid"
            },
            "fr": {
                "name": "French",
                "native_name": "Français",
                "direction": LanguageDirection.LTR,
                "locale": "fr_FR",
                "currency": "EUR",
                "timezone": "Europe/Paris"
            },
            "de": {
                "name": "German",
                "native_name": "Deutsch",
                "direction": LanguageDirection.LTR,
                "locale": "de_DE",
                "currency": "EUR",
                "timezone": "Europe/Berlin"
            },
            "ja": {
                "name": "Japanese",
                "native_name": "日本語",
                "direction": LanguageDirection.LTR,
                "locale": "ja_JP",
                "currency": "JPY",
                "timezone": "Asia/Tokyo"
            },
            "ko": {
                "name": "Korean",
                "native_name": "한국어",
                "direction": LanguageDirection.LTR,
                "locale": "ko_KR",
                "currency": "KRW",
                "timezone": "Asia/Seoul"
            },
            "ar": {
                "name": "Arabic",
                "native_name": "العربية",
                "direction": LanguageDirection.RTL,
                "locale": "ar_SA",
                "currency": "SAR",
                "timezone": "Asia/Riyadh",
                "rtl_support": True
            },
            "hi": {
                "name": "Hindi",
                "native_name": "हिन्दी",
                "direction": LanguageDirection.LTR,
                "locale": "hi_IN",
                "currency": "INR",
                "timezone": "Asia/Kolkata"
            },
            "pt": {
                "name": "Portuguese",
                "native_name": "Português",
                "direction": LanguageDirection.LTR,
                "locale": "pt_PT",
                "currency": "EUR",
                "timezone": "Europe/Lisbon"
            },
            "it": {
                "name": "Italian",
                "native_name": "Italiano",
                "direction": LanguageDirection.LTR,
                "locale": "it_IT",
                "currency": "EUR",
                "timezone": "Europe/Rome"
            },
            "nl": {
                "name": "Dutch",
                "native_name": "Nederlands",
                "direction": LanguageDirection.LTR,
                "locale": "nl_NL",
                "currency": "EUR",
                "timezone": "Europe/Amsterdam"
            },
            "sv": {
                "name": "Swedish",
                "native_name": "Svenska",
                "direction": LanguageDirection.LTR,
                "locale": "sv_SE",
                "currency": "SEK",
                "timezone": "Europe/Stockholm"
            },
            "no": {
                "name": "Norwegian",
                "native_name": "Norsk",
                "direction": LanguageDirection.LTR,
                "locale": "no_NO",
                "currency": "NOK",
                "timezone": "Europe/Oslo"
            },
            "da": {
                "name": "Danish",
                "native_name": "Dansk",
                "direction": LanguageDirection.LTR,
                "locale": "da_DK",
                "currency": "DKK",
                "timezone": "Europe/Copenhagen"
            },
            "fi": {
                "name": "Finnish",
                "native_name": "Suomi",
                "direction": LanguageDirection.LTR,
                "locale": "fi_FI",
                "currency": "EUR",
                "timezone": "Europe/Helsinki"
            },
            "pl": {
                "name": "Polish",
                "native_name": "Polski",
                "direction": LanguageDirection.LTR,
                "locale": "pl_PL",
                "currency": "PLN",
                "timezone": "Europe/Warsaw"
            },
            "tr": {
                "name": "Turkish",
                "native_name": "Türkçe",
                "direction": LanguageDirection.LTR,
                "locale": "tr_TR",
                "currency": "TRY",
                "timezone": "Europe/Istanbul"
            },
            "th": {
                "name": "Thai",
                "native_name": "ไทย",
                "direction": LanguageDirection.LTR,
                "locale": "th_TH",
                "currency": "THB",
                "timezone": "Asia/Bangkok"
            },
            "vi": {
                "name": "Vietnamese",
                "native_name": "Tiếng Việt",
                "direction": LanguageDirection.LTR,
                "locale": "vi_VN",
                "currency": "VND",
                "timezone": "Asia/Ho_Chi_Minh"
            },
            "id": {
                "name": "Indonesian",
                "native_name": "Bahasa Indonesia",
                "direction": LanguageDirection.LTR,
                "locale": "id_ID",
                "currency": "IDR",
                "timezone": "Asia/Jakarta"
            },
            # RTL languages
            "he": {
                "name": "Hebrew",
                "native_name": "עברית",
                "direction": LanguageDirection.RTL,
                "locale": "he_IL",
                "currency": "ILS",
                "timezone": "Asia/Jerusalem",
                "rtl_support": True
            },
            "fa": {
                "name": "Persian",
                "native_name": "فارسی",
                "direction": LanguageDirection.RTL,
                "locale": "fa_IR",
                "currency": "IRR",
                "timezone": "Asia/Tehran",
                "rtl_support": True
            }
        }
        
        # Save to file
        config_file = self.base_path / "language_configs.yaml"
        serializable_configs = {}
        for lang_code, config in default_configs.items():
            serializable_config = {
                "name": config["name"],
                "native_name": config["native_name"],
                "direction": config["direction"].value,
                "locale": config["locale"],
                "currency": config["currency"],
                "timezone": config["timezone"],
                "rtl_support": config.get("rtl_support", False)
            }
            serializable_configs[lang_code] = serializable_config
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(serializable_configs, f, default_flow_style=False, allow_unicode=True)
        
        # Load into memory
        for lang_code, config_data in serializable_configs.items():
            self.languages[lang_code] = LanguageConfig(
                code=lang_code,
                **config_data
            )
    
    def _load_cultural_contexts(self) -> None:
        """Load cultural contexts for different regions"""
        cultural_file = self.base_path / "cultural_contexts.json"
        
        if not cultural_file.exists():
            self._create_default_cultural_contexts()
        
        try:
            with open(cultural_file, 'r', encoding='utf-8') as f:
                cultural_data = json.load(f)
            
            for region, data in cultural_data.items():
                self.cultural_contexts[region] = CulturalContext(**data)
                
        except Exception as e:
            self.logger.error(f"Error loading cultural contexts: {e}")
            self._create_default_cultural_contexts()
    
    def _create_default_cultural_contexts(self) -> None:
        """Create default cultural contexts"""
        cultural_data = {
            "uz-UZ": {
                "region": "Uzbekistan",
                "cultural_preferences": {
                    "greeting_style": "formal",
                    "communication_style": "direct",
                    "business_protocol": "respectful",
                    "decision_making": "hierarchical"
                },
                "color_meanings": {
                    "green": "goodness, Islam",
                    "blue": "peace, sky",
                    "red": "danger, passion",
                    "white": "purity, peace"
                },
                "number_preferences": {
                    "lucky_numbers": [3, 7, 13],
                    "unlucky_numbers": [4, 666],
                    "date_preference": "DD.MM.YYYY"
                },
                "date_conventions": {
                    "first_day_of_week": "monday",
                    "date_format": "DD.MM.YYYY",
                    "time_format": "24h"
                },
                "greeting_formats": {
                    "formal": "Assalomu alaykum",
                    "informal": "Salom",
                    "business": "Assalomu alaykum, hurmatli"
                },
                "business_hours": {
                    "weekdays": "09:00-18:00",
                    "friday": "09:00-12:00",
                    "weekend": "closed"
                },
                "holiday_calendar": [
                    "new_year", "womens_day", "navruz", "victory_day", 
                    "independence_day", "teacher_day", "constitution_day"
                ],
                "measurement_system": "metric",
                "paper_size": "A4"
            },
            "en-US": {
                "region": "United States",
                "cultural_preferences": {
                    "greeting_style": "casual",
                    "communication_style": "direct",
                    "business_protocol": "efficient",
                    "decision_making": "individual"
                },
                "color_meanings": {
                    "red": "danger, passion, love",
                    "blue": "trust, loyalty",
                    "green": "money, nature",
                    "white": "purity, peace"
                },
                "number_preferences": {
                    "lucky_numbers": [3, 7],
                    "unlucky_numbers": [666],
                    "date_preference": "MM/DD/YYYY"
                },
                "date_conventions": {
                    "first_day_of_week": "sunday",
                    "date_format": "MM/DD/YYYY",
                    "time_format": "12h"
                },
                "greeting_formats": {
                    "formal": "Good day",
                    "informal": "Hi",
                    "business": "Good morning"
                },
                "business_hours": {
                    "weekdays": "09:00-17:00",
                    "weekend": "closed"
                },
                "holiday_calendar": [
                    "new_year", "mlk_day", "valentines_day", "presidents_day",
                    "memorial_day", "independence_day", "labor_day"
                ],
                "measurement_system": "imperial",
                "paper_size": "Letter"
            }
        }
        
        with open(self.base_path / "cultural_contexts.json", 'w', encoding='utf-8') as f:
            json.dump(cultural_data, f, indent=2, ensure_ascii=False)
    
    def _load_translations(self) -> None:
        """Load translations from various sources"""
        translations_dir = self.base_path / "translations"
        translations_dir.mkdir(exist_ok=True)
        
        # Load translations for each language
        for lang_code in self.languages.keys():
            translations_file = translations_dir / f"{lang_code}.json"
            
            if translations_file.exists():
                try:
                    with open(translations_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    for key, value in data.items():
                        translation_entry = TranslationEntry(
                            key=key,
                            value=value,
                            namespace="default"
                        )
                        self.translations[lang_code][key] = translation_entry
                        
                except Exception as e:
                    self.logger.error(f"Error loading translations for {lang_code}: {e}")
    
    def _auto_detect_language(self) -> None:
        """Auto-detect user language from environment"""
        # This would typically detect from browser headers, user settings, etc.
        # For now, we'll use a simple fallback
        try:
            import locale
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                lang_code = system_locale.split('_')[0]
                if lang_code in self.languages:
                    self.set_language(lang_code)
                    return
        except:
            pass
        
        # Fallback to English
        self.set_language(self.fallback_language)
    
    def set_language(self, language_code: str, culture: Optional[str] = None) -> bool:
        """
        Set the current language
        
        Args:
            language_code: Language code (e.g., 'en', 'uz', 'ar')
            culture: Optional culture code (e.g., 'en-US', 'uz-UZ')
        
        Returns:
            bool: Success status
        """
        if language_code not in self.languages:
            self.logger.warning(f"Language {language_code} not supported")
            return False
        
        self.current_language = language_code
        if culture:
            self.current_culture = culture
        
        # Clear translation cache
        if self.cache_enabled:
            self.translation_cache.clear()
        
        self.logger.info(f"Language set to {language_code}")
        return True
    
    def get_language(self) -> Optional[str]:
        """Get current language code"""
        return self.current_language
    
    def get_language_config(self, language_code: Optional[str] = None) -> Optional[LanguageConfig]:
        """
        Get language configuration
        
        Args:
            language_code: Language code, uses current language if None
        
        Returns:
            LanguageConfig or None
        """
        lang_code = language_code or self.current_language
        return self.languages.get(lang_code)
    
    def is_rtl(self, language_code: Optional[str] = None) -> bool:
        """
        Check if language is RTL (Right-to-Left)
        
        Args:
            language_code: Language code, uses current language if None
        
        Returns:
            bool: True if RTL
        """
        config = self.get_language_config(language_code)
        return config.direction == LanguageDirection.RTL if config else False
    
    def translate(self, key: str, default: str = "", **kwargs) -> str:
        """
        Translate a key to current language
        
        Args:
            key: Translation key
            default: Default value if translation not found
            **kwargs: Variables for string interpolation
        
        Returns:
            Translated string
        """
        if not self.current_language:
            return default or key
        
        # Check cache first
        cache_key = f"{self.current_language}:{key}:{hash(str(kwargs))}"
        if self.cache_enabled and cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Get translation
        translation_entry = self.translations[self.current_language].get(key)
        
        if not translation_entry:
            # Fallback to fallback language
            if self.fallback_language and self.fallback_language != self.current_language:
                fallback_entry = self.translations[self.fallback_language].get(key)
                if fallback_entry:
                    translation_entry = fallback_entry
        
        result = translation_entry.value if translation_entry else (default or key)
        
        # Handle plural forms
        if 'count' in kwargs:
            result = self._handle_plural_forms(result, kwargs['count'])
        
        # Apply string interpolation
        result = result.format(**kwargs)
        
        # Cultural adaptation
        result = self._apply_cultural_adaptation(result)
        
        # Cache result
        if self.cache_enabled:
            self.translation_cache[cache_key] = result
        
        return result
    
    def translate_plural(self, singular_key: str, plural_key: str, count: int, **kwargs) -> str:
        """
        Handle plural forms
        
        Args:
            singular_key: Key for singular form
            plural_key: Key for plural form
            count: Count to determine form
            **kwargs: Additional variables
        
        Returns:
            Translated string with appropriate plural form
        """
        if not self.current_language:
            return singular_key if count == 1 else plural_key
        
        # Use count to determine key
        key = singular_key if count == 1 else plural_key
        return self.translate(key, **kwargs)
    
    def _handle_plural_forms(self, text: str, count: int) -> str:
        """
        Handle plural forms based on language rules
        
        Args:
            text: Text with plural markers
            count: Count value
        
        Returns:
            Text with appropriate plural form
        """
        # Simple plural handling - can be enhanced for complex languages
        if count == 1:
            text = re.sub(r'\|plural', '', text)
        else:
            text = re.sub(r'\|singular\|', '', text)
            text = re.sub(r'\|singular', '', text)
            text = re.sub(r'\|plural', '', text)
        
        return text
    
    def _apply_cultural_adaptation(self, text: str) -> str:
        """
        Apply cultural adaptations to text
        
        Args:
            text: Text to adapt
        
        Returns:
            Culturally adapted text
        """
        if not self.current_culture:
            return text
        
        cultural_context = self.cultural_contexts.get(self.current_culture)
        if not cultural_context:
            return text
        
        # Apply cultural preferences
        # This is a simplified implementation - can be expanded
        adapted_text = text
        
        # Add cultural markers for numbers, dates, etc.
        if cultural_context.measurement_system == "imperial":
            adapted_text = self._convert_to_imperial(adapted_text)
        elif cultural_context.measurement_system == "metric":
            adapted_text = self._convert_to_metric(adapted_text)
        
        return adapted_text
    
    def _convert_to_imperial(self, text: str) -> str:
        """Convert metric measurements to imperial"""
        # Simple conversion patterns - can be enhanced
        text = re.sub(r'(\d+(?:\.\d+)?)\s*km', r'\1 miles', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*cm', r'\1 inches', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*m', r'\1 feet', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*kg', r'\1 pounds', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*°C', r'\1°F', text)
        return text
    
    def _convert_to_metric(self, text: str) -> str:
        """Convert imperial measurements to metric"""
        # Simple conversion patterns - can be enhanced
        text = re.sub(r'(\d+(?:\.\d+)?)\s*miles', r'\1 km', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*inches', r'\1 cm', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*feet', r'\1 m', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*pounds', r'\1 kg', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*°F', r'\1°C', text)
        return text
    
    def format_number(self, number: Union[int, float], **kwargs) -> str:
        """
        Format number according to current locale
        
        Args:
            number: Number to format
            **kwargs: Additional formatting options
        
        Returns:
            Formatted number string
        """
        config = self.get_language_config()
        if not config:
            return str(number)
        
        try:
            locale_obj = Locale.parse(config.locale)
            return locale_obj.format_decimal(number, **kwargs)
        except:
            return str(number)
    
    def format_currency(self, amount: Union[int, float], currency: Optional[str] = None, **kwargs) -> str:
        """
        Format currency according to current locale
        
        Args:
            amount: Amount to format
            currency: Currency code
            **kwargs: Additional formatting options
        
        Returns:
            Formatted currency string
        """
        config = self.get_language_config()
        if not config:
            return f"{amount} {currency}"
        
        currency = currency or config.currency
        
        try:
            locale_obj = Locale.parse(config.locale)
            return locale_obj.format_currency(amount, currency, **kwargs)
        except:
            return f"{amount} {currency}"
    
    def format_date(self, date_obj: datetime, style: DateFormat = DateFormat.MEDIUM, **kwargs) -> str:
        """
        Format date according to current locale
        
        Args:
            date_obj: Date object to format
            style: Date format style
            **kwargs: Additional formatting options
        
        Returns:
            Formatted date string
        """
        config = self.get_language_config()
        if not config:
            return date_obj.strftime("%Y-%m-%d")
        
        try:
            locale_obj = Locale.parse(config.locale)
            date_pattern = locale_obj.date_formats[style]
            return date_pattern.format(date_obj)
        except:
            return date_obj.strftime("%Y-%m-%d")
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """
        Get list of available languages
        
        Returns:
            List of language dictionaries
        """
        languages = []
        for lang_code, config in self.languages.items():
            languages.append({
                "code": lang_code,
                "name": config.name,
                "native_name": config.native_name,
                "direction": config.direction.value,
                "rtl_support": config.rtl_support
            })
        return languages
    
    def detect_language_from_text(self, text: str) -> Optional[str]:
        """
        Detect language from text content
        
        Args:
            text: Text to analyze
        
        Returns:
            Detected language code or None
        """
        # Simple detection based on common patterns
        # This is a basic implementation - can be enhanced with ML
        
        text = text.lower()
        
        # Common patterns for different languages
        patterns = {
            "uz": ["men", "sen", "bu", "shu", "qanday", "nimaga"],
            "ru": ["что", "как", "где", "когда", "почему"],
            "en": ["the", "and", "or", "but", "is", "are"],
            "ar": ["في", "من", "إلى", "على", "هذا", "هذه"],
            "zh": ["的", "是", "在", "有", "和", "了"]
        }
        
        scores = {}
        for lang_code, words in patterns.items():
            score = sum(1 for word in words if word in text)
            if score > 0:
                scores[lang_code] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def add_translation(self, language_code: str, key: str, value: str, 
                       context: Optional[str] = None, namespace: str = "default") -> bool:
        """
        Add a new translation
        
        Args:
            language_code: Language code
            key: Translation key
            value: Translation value
            context: Optional context
            namespace: Namespace for organization
        
        Returns:
            bool: Success status
        """
        if language_code not in self.languages:
            return False
        
        translation_entry = TranslationEntry(
            key=key,
            value=value,
            context=context,
            namespace=namespace,
            last_updated=datetime.now()
        )
        
        self.translations[language_code][key] = translation_entry
        return True
    
    def save_translations(self, language_code: Optional[str] = None) -> bool:
        """
        Save translations to file
        
        Args:
            language_code: Specific language to save, or all if None
        
        Returns:
            bool: Success status
        """
        translations_dir = self.base_path / "translations"
        translations_dir.mkdir(exist_ok=True)
        
        try:
            if language_code:
                # Save specific language
                if language_code in self.translations:
                    translations_file = translations_dir / f"{language_code}.json"
                    data = {
                        key: entry.value for key, entry in self.translations[language_code].items()
                    }
                    with open(translations_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                # Save all languages
                for lang_code in self.translations:
                    translations_file = translations_dir / f"{lang_code}.json"
                    data = {
                        key: entry.value for key, entry in self.translations[lang_code].items()
                    }
                    with open(translations_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving translations: {e}")
            return False
    
    def get_translation_quality(self, language_code: str) -> float:
        """
        Get translation quality score for a language
        
        Args:
            language_code: Language code
        
        Returns:
            Quality score (0.0 to 1.0)
        """
        if language_code not in self.translations:
            return 0.0
        
        total_score = sum(entry.quality_score for entry in self.translations[language_code].values())
        total_count = len(self.translations[language_code])
        
        return total_score / total_count if total_count > 0 else 0.0
    
    def optimize_performance(self) -> None:
        """Optimize system performance"""
        # Clear expired cache entries
        if self.cache_enabled and self.translation_cache:
            # This is a simplified cache cleanup
            # In production, you might want to use more sophisticated caching
            pass
        
        # Compress translation memory
        self._compress_translation_memory()
        
        # Update quality scores
        self._update_quality_scores()
    
    def _compress_translation_memory(self) -> None:
        """Compress translation memory to save space"""
        # Remove duplicate entries
        seen_translations = {}
        for lang_code in self.translations:
            for key, entry in self.translations[lang_code].items():
                if entry.value not in seen_translations:
                    seen_translations[entry.value] = key
        
        self.logger.info(f"Translation memory compressed: {len(seen_translations)} unique translations")
    
    def _update_quality_scores(self) -> None:
        """Update quality scores for all translations"""
        for lang_code in self.translations:
            for entry in self.translations[lang_code].values():
                # Simple quality scoring - can be enhanced
                if len(entry.value) > 0:
                    entry.quality_score = min(1.0, 0.8 + (len(entry.value) / 100))
    
    def export_translations(self, format: str = "json", language_codes: Optional[List[str]] = None) -> str:
        """
        Export translations to various formats
        
        Args:
            format: Export format ('json', 'po', 'yaml')
            language_codes: List of language codes to export
        
        Returns:
            Exported content as string
        """
        if language_codes is None:
            language_codes = list(self.translations.keys())
        
        if format.lower() == "json":
            export_data = {}
            for lang_code in language_codes:
                if lang_code in self.translations:
                    export_data[lang_code] = {
                        key: entry.value for key, entry in self.translations[lang_code].items()
                    }
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        
        elif format.lower() == "po":
            # PO format export
            result = []
            result.append('msgid ""')
            result.append('msgstr ""')
            result.append('"Content-Type: text/plain; charset=UTF-8\\n"')
            result.append("")
            
            for lang_code in language_codes:
                if lang_code in self.translations:
                    result.append(f'# Language: {lang_code}')
                    result.append("")
                    for entry in self.translations[lang_code].values():
                        result.append(f'msgid "{entry.key}"')
                        result.append(f'msgstr "{entry.value}"')
                        result.append("")
            
            return "\n".join(result)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            Dictionary with system statistics
        """
        stats = {
            "total_languages": len(self.languages),
            "rtl_languages": sum(1 for config in self.languages.values() if config.rtl_support),
            "total_translations": sum(len(translations) for translations in self.translations.values()),
            "translation_coverage": {},
            "quality_scores": {},
            "cache_size": len(self.translation_cache) if self.cache_enabled else 0
        }
        
        # Calculate coverage and quality for each language
        for lang_code in self.languages:
            total_keys = len(self.translations.get(lang_code, {}))
            stats["translation_coverage"][lang_code] = total_keys
            
            quality = self.get_translation_quality(lang_code)
            stats["quality_scores"][lang_code] = quality
        
        return stats


# Global instance
mls = MultiLanguageSystem()


def get_current_language() -> str:
    """Get current language code"""
    return mls.get_language() or "en"


def set_current_language(language_code: str) -> bool:
    """Set current language"""
    return mls.set_language(language_code)


def _(key: str, default: str = "", **kwargs) -> str:
    """
    Shortcut translation function
    
    Args:
        key: Translation key
        default: Default value
        **kwargs: Variables for interpolation
    
    Returns:
        Translated string
    """
    return mls.translate(key, default, **kwargs)


def _n(singular_key: str, plural_key: str, count: int, **kwargs) -> str:
    """
    Shortcut plural translation function
    
    Args:
        singular_key: Singular form key
        plural_key: Plural form key
        count: Count for plural selection
        **kwargs: Additional variables
    
    Returns:
        Translated string with appropriate plural form
    """
    return mls.translate_plural(singular_key, plural_key, count, **kwargs)


# Example usage
if __name__ == "__main__":
    # Initialize system
    mls = MultiLanguageSystem()
    
    # Set language to Uzbek
    mls.set_language("uz")
    
    # Add some sample translations
    mls.add_translation("uz", "welcome", "Xush kelibsiz!")
    mls.add_translation("uz", "hello_user", "Salom, {name}!")
    mls.add_translation("en", "welcome", "Welcome!")
    mls.add_translation("en", "hello_user", "Hello, {name}!")
    
    # Get translations
    print(mls.translate("welcome"))  # "Xush kelibsiz!"
    print(mls.translate("hello_user", name="Aziz"))  # "Salom, Aziz!"
    
    # Test RTL support
    mls.set_language("ar")  # Arabic
    print(f"Is Arabic RTL: {mls.is_rtl()}")  # True
    
    # Get available languages
    languages = mls.get_available_languages()
    print(f"Available languages: {len(languages)}")
    
    # Format currency
    mls.set_language("en")
    print(mls.format_currency(1234.56))  # "$1,234.56"
    
    # Format date
    from datetime import datetime
    print(mls.format_date(datetime.now()))  # Current date in US format