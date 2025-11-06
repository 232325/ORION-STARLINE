#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orion Starline Localization System
==================================

Advanced localization system with cultural adaptation, locale detection,
and region-specific formatting for professional applications.

Author: Orion Starline Team
Version: 1.0.0
Created: 2025-11-05
"""

import os
import json
import locale
import re
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import logging
from pathlib import Path
import requests
from urllib.parse import urlparse
import time
from threading import Lock
import json
import subprocess
import platform


class LocaleFormat(Enum):
    """Locale formatting options"""
    STANDARD = "standard"
    SHORT = "short"
    LONG = "long"
    FULL = "full"
    RELATIVE = "relative"


class TimeZoneStrategy(Enum):
    """Time zone handling strategies"""
    UTC = "utc"
    LOCAL = "local"
    USER_PREFERENCE = "user_preference"
    GEOGRAPHIC = "geographic"


class NumberSystem(Enum):
    """Number system types"""
    DECIMAL = "decimal"
    ARABIC_INDIC = "arabic_indic"
    EASTERN_ARABIC = "eastern_arabic"
    BENGALI = "bengali"
    THAI = "thai"
    KHMER = "khmer"


class CalendarSystem(Enum):
    """Calendar system types"""
    GREGORIAN = "gregorian"
    HIJRI = "hijri"
    HEBREW = "hebrew"
    BUDDHIST = "buddhist"
    PERSIAN = "persian"
    INDIAN = "indian"


@dataclass
class LocaleInfo:
    """Locale information dataclass"""
    locale_code: str
    language_code: str
    country_code: str
    region_name: str
    currency: str
    currency_symbol: str
    decimal_separator: str
    thousands_separator: str
    date_format: str
    time_format: str
    first_day_of_week: int  # 0=Monday, 6=Sunday
    timezone: str
    number_system: NumberSystem
    calendar_system: CalendarSystem
    reading_direction: str = "ltr"
    paper_size: str = "A4"
    measurement_system: str = "metric"
    phone_format: str = ""
    postal_code_format: str = ""
    address_format: str = ""


@dataclass
class CulturalPreferences:
    """Cultural preferences and adaptations"""
    region: str
    date_preferences: Dict[str, Any]
    number_preferences: Dict[str, Any]
    currency_preferences: Dict[str, Any]
    color_preferences: Dict[str, str]
    cultural_taboos: List[str]
    preferred_greetings: Dict[str, str]
    business_culture: Dict[str, Any]
    holiday_calendar: List[str]
    food_preferences: Dict[str, List[str]]
    communication_style: str
    decision_making_style: str
    time_orientation: str  # past, present, future
    context_level: str  # high_context, low_context
    power_distance: str  # high, low, medium
    uncertainty_avoidance: str  # high, low, medium


@dataclass
class AddressFormat:
    """Address format specification"""
    format_string: str
    field_order: List[str]
    required_fields: List[str]
    postal_code_required: bool
    country_specific: bool
    example: str


@dataclass
class NameFormat:
    """Name format specification"""
    given_name_first: bool
    family_name_first: bool
    middle_name_position: str
    honorific_required: bool
    formality_level: str
    cultural_notes: List[str]


class LocalizationManager:
    """
    Advanced Localization Management System
    
    Features:
    - Automatic locale detection
    - Cultural adaptation
    - Region-specific formatting
    - Timezone handling
    - Currency conversion
    - Address formatting
    - Name formatting
    - Holiday calendars
    - Business culture integration
    """
    
    def __init__(self, base_path: str = "i18n"):
        """
        Initialize localization manager
        
        Args:
            base_path: Base path for localization files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Core data
        self.locale_cache: Dict[str, LocaleInfo] = {}
        self.cultural_preferences: Dict[str, CulturalPreferences] = {}
        self.address_formats: Dict[str, AddressFormat] = {}
        self.name_formats: Dict[str, NameFormat] = {}
        
        # Current state
        self.current_locale: Optional[str] = None
        self.current_timezone: Optional[str] = None
        self.timezone_strategy: TimeZoneStrategy = TimeZoneStrategy.UTC
        
        # Configuration
        self.cache_enabled: bool = True
        self.auto_detect_enabled: bool = True
        self.geolocation_enabled: bool = True
        
        # Performance tracking
        self.detection_times: List[float] = []
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        
        # Concurrency
        self._lock = Lock()
        
        # Load data
        self._load_locale_data()
        self._load_cultural_preferences()
        self._load_format_specifications()
        
        # Auto-detect
        if self.auto_detect_enabled:
            self._auto_detect_locale()
    
    def _load_locale_data(self) -> None:
        """Load locale data from file or create default"""
        locale_file = self.base_path / "locales.json"
        
        if not locale_file.exists():
            self._create_default_locale_data()
        
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                locale_data = json.load(f)
            
            for locale_code, data in locale_data.items():
                # Convert string enum values back to enum objects
                if 'number_system' in data:
                    data['number_system'] = NumberSystem(data['number_system'])
                if 'calendar_system' in data:
                    data['calendar_system'] = CalendarSystem(data['calendar_system'])
                # Direction is already a string in the JSON, no conversion needed
                
                self.locale_cache[locale_code] = LocaleInfo(
                    locale_code=locale_code,
                    **data
                )
                
        except Exception as e:
            self.logger.error(f"Error loading locale data: {e}")
            self._create_default_locale_data()
    
    def _create_default_locale_data(self) -> None:
        """Create default locale data for major regions"""
        default_locales = {
            "uz-UZ": {
                "language_code": "uz",
                "country_code": "UZ",
                "region_name": "Uzbekistan",
                "currency": "UZS",
                "currency_symbol": "so'm",
                "decimal_separator": ",",
                "thousands_separator": " ",
                "date_format": "DD.MM.YYYY",
                "time_format": "HH:mm",
                "first_day_of_week": 1,
                "timezone": "Asia/Samarkand",
                "number_system": NumberSystem.DECIMAL.value,
                "calendar_system": CalendarSystem.GREGORIAN.value,
                "phone_format": "+998 XX XXX XX XX",
                "postal_code_format": "XXXXXX",
                "address_format": "{city}, {street}, {house}",
                "reading_direction": "ltr",
                "paper_size": "A4",
                "measurement_system": "metric"
            },
            "en-US": {
                "language_code": "en",
                "country_code": "US",
                "region_name": "United States",
                "currency": "USD",
                "currency_symbol": "$",
                "decimal_separator": ".",
                "thousands_separator": ",",
                "date_format": "MM/DD/YYYY",
                "time_format": "h:mm a",
                "first_day_of_week": 0,
                "timezone": "America/New_York",
                "number_system": NumberSystem.DECIMAL.value,
                "calendar_system": CalendarSystem.GREGORIAN.value,
                "phone_format": "(XXX) XXX-XXXX",
                "postal_code_format": "XXXXX",
                "address_format": "{street}\n{city}, {state} {zip}",
                "reading_direction": "ltr",
                "paper_size": "Letter",
                "measurement_system": "imperial"
            },
            "en-GB": {
                "language_code": "en",
                "country_code": "GB",
                "region_name": "United Kingdom",
                "currency": "GBP",
                "currency_symbol": "£",
                "decimal_separator": ".",
                "thousands_separator": ",",
                "date_format": "DD/MM/YYYY",
                "time_format": "HH:mm",
                "first_day_of_week": 1,
                "timezone": "Europe/London",
                "number_system": NumberSystem.DECIMAL.value,
                "calendar_system": CalendarSystem.GREGORIAN.value,
                "phone_format": "XXXX XXX XXX",
                "postal_code_format": "XXXX XXX",
                "address_format": "{street}\n{city}\n{postcode}",
                "reading_direction": "ltr",
                "paper_size": "A4",
                "measurement_system": "metric"
            },
            "ar-SA": {
                "language_code": "ar",
                "country_code": "SA",
                "region_name": "Saudi Arabia",
                "currency": "SAR",
                "currency_symbol": "ر.س",
                "decimal_separator": ".",
                "thousands_separator": ",",
                "date_format": "DD/MM/YYYY",
                "time_format": "HH:mm",
                "first_day_of_week": 6,
                "timezone": "Asia/Riyadh",
                "number_system": NumberSystem.ARABIC_INDIC.value,
                "calendar_system": CalendarSystem.HIJRI.value,
                "phone_format": "+966 XX XXX XXXX",
                "postal_code_format": "XXXXX",
                "address_format": "{street}\n{city} {zip}",
                "reading_direction": "rtl",
                "paper_size": "A4",
                "measurement_system": "metric"
            },
            "zh-CN": {
                "language_code": "zh",
                "country_code": "CN",
                "region_name": "China",
                "currency": "CNY",
                "currency_symbol": "¥",
                "decimal_separator": ".",
                "thousands_separator": ",",
                "date_format": "YYYY-MM-DD",
                "time_format": "HH:mm:ss",
                "first_day_of_week": 1,
                "timezone": "Asia/Shanghai",
                "number_system": NumberSystem.EASTERN_ARABIC.value,
                "calendar_system": CalendarSystem.GREGORIAN.value,
                "phone_format": "+86 XXX XXXX XXXX",
                "postal_code_format": "XXXXXX",
                "address_format": "{province} {city} {district}\n{street} {house}",
                "reading_direction": "ltr",
                "paper_size": "A4",
                "measurement_system": "metric"
            },
            "ja-JP": {
                "language_code": "ja",
                "country_code": "JP",
                "region_name": "Japan",
                "currency": "JPY",
                "currency_symbol": "¥",
                "decimal_separator": ".",
                "thousands_separator": ",",
                "date_format": "YYYY/MM/DD",
                "time_format": "H:mm",
                "first_day_of_week": 0,
                "timezone": "Asia/Tokyo",
                "number_system": NumberSystem.DECIMAL.value,
                "calendar_system": CalendarSystem.GREGORIAN.value,
                "phone_format": "090-XXXX-XXXX",
                "postal_code_format": "XXX-XXXX",
                "address_format": "〒{zip}\n{prefecture}{city}\n{street} {house}",
                "reading_direction": "ltr",
                "paper_size": "A4",
                "measurement_system": "metric"
            }
        }
        
        # Save to file
        locale_file = self.base_path / "locales.json"
        with open(locale_file, 'w', encoding='utf-8') as f:
            json.dump(default_locales, f, indent=2, ensure_ascii=False)
        
        # Load into cache
        for locale_code, data in default_locales.items():
            self.locale_cache[locale_code] = LocaleInfo(
                locale_code=locale_code,
                **data
            )
    
    def _load_cultural_preferences(self) -> None:
        """Load cultural preferences data"""
        cultural_file = self.base_path / "cultural_preferences.json"
        
        if not cultural_file.exists():
            self._create_default_cultural_preferences()
        
        try:
            with open(cultural_file, 'r', encoding='utf-8') as f:
                cultural_data = json.load(f)
            
            for region, data in cultural_data.items():
                self.cultural_preferences[region] = CulturalPreferences(**data)
                
        except Exception as e:
            self.logger.error(f"Error loading cultural preferences: {e}")
            self._create_default_cultural_preferences()
    
    def _create_default_cultural_preferences(self) -> None:
        """Create default cultural preferences"""
        default_cultural = {
            "uz-UZ": {
                "region": "Uzbekistan",
                "date_preferences": {
                    "format": "DD.MM.YYYY",
                    "first_day": "monday",
                    "weekend": ["saturday", "sunday"]
                },
                "number_preferences": {
                    "decimal_separator": ",",
                    "thousands_separator": " ",
                    "preferred_numbers": [3, 7, 13]
                },
                "currency_preferences": {
                    "format": "{amount} {currency}",
                    "position": "after",
                    "currency_display": "symbol"
                },
                "color_preferences": {
                    "green": "blessing, Islam, good fortune",
                    "blue": "peace, sky, water",
                    "red": "danger, passion, power",
                    "white": "purity, peace, cleanliness"
                },
                "cultural_taboos": [
                    "eating with left hand",
                    "stepping on thresholds",
                    "pointing with one finger"
                ],
                "preferred_greetings": {
                    "formal": "Assalomu alaykum",
                    "informal": "Salom",
                    "business": "Assalomu alaykum, hurmatli"
                },
                "business_culture": {
                    "hierarchy": "high",
                    "decision_making": "consultative",
                    "communication": "indirect",
                    "relationship_building": "important"
                },
                "holiday_calendar": [
                    "new_year", "womens_day", "navruz", "victory_day",
                    "independence_day", "teacher_day", "constitution_day",
                    "eid_al_fitr", "eid_al_adha"
                ],
                "food_preferences": {
                    "staple": ["rice", "bread", "meat"],
                    "preferred_spices": ["cumin", "coriander", "paprika"],
                    "dietary_restrictions": ["halal"]
                },
                "communication_style": "polite_formal",
                "decision_making_style": "consensus",
                "time_orientation": "past_focused",
                "context_level": "high_context",
                "power_distance": "high",
                "uncertainty_avoidance": "medium"
            },
            "en-US": {
                "region": "United States",
                "date_preferences": {
                    "format": "MM/DD/YYYY",
                    "first_day": "sunday",
                    "weekend": ["saturday", "sunday"]
                },
                "number_preferences": {
                    "decimal_separator": ".",
                    "thousands_separator": ",",
                    "preferred_numbers": [3, 7]
                },
                "currency_preferences": {
                    "format": "{currency}{amount}",
                    "position": "before",
                    "currency_display": "symbol"
                },
                "color_preferences": {
                    "red": "danger, love, passion",
                    "blue": "trust, loyalty, stability",
                    "green": "money, nature, growth",
                    "white": "purity, cleanliness"
                },
                "cultural_taboos": [
                    "asking about salary",
                    "pointing with middle finger"
                ],
                "preferred_greetings": {
                    "formal": "Good day",
                    "informal": "Hi",
                    "business": "Good morning/afternoon"
                },
                "business_culture": {
                    "hierarchy": "low",
                    "decision_making": "individual",
                    "communication": "direct",
                    "relationship_building": "task_focused"
                },
                "holiday_calendar": [
                    "new_year", "mlk_day", "valentines_day", "presidents_day",
                    "memorial_day", "independence_day", "labor_day", "thanksgiving",
                    "christmas"
                ],
                "food_preferences": {
                    "staple": ["bread", "meat", "potatoes"],
                    "preferred_spices": ["salt", "pepper", "garlic"],
                    "dietary_restrictions": ["varies"]
                },
                "communication_style": "direct",
                "decision_making_style": "individual",
                "time_orientation": "future_focused",
                "context_level": "low_context",
                "power_distance": "low",
                "uncertainty_avoidance": "low"
            }
        }
        
        with open(self.base_path / "cultural_preferences.json", 'w', encoding='utf-8') as f:
            json.dump(default_cultural, f, indent=2, ensure_ascii=False)
        
        for region, data in default_cultural.items():
            self.cultural_preferences[region] = CulturalPreferences(**data)
    
    def _load_format_specifications(self) -> None:
        """Load address and name format specifications"""
        formats_file = self.base_path / "format_specifications.json"
        
        if not formats_file.exists():
            self._create_default_format_specifications()
        
        try:
            with open(formats_file, 'r', encoding='utf-8') as f:
                format_data = json.load(f)
            
            # Address formats
            for region, data in format_data.get("addresses", {}).items():
                self.address_formats[region] = AddressFormat(**data)
            
            # Name formats
            for region, data in format_data.get("names", {}).items():
                self.name_formats[region] = NameFormat(**data)
                
        except Exception as e:
            self.logger.error(f"Error loading format specifications: {e}")
            self._create_default_format_specifications()
    
    def _create_default_format_specifications(self) -> None:
        """Create default format specifications"""
        default_formats = {
            "addresses": {
                "uz-UZ": {
                    "format_string": "{street}, {house}\n{city}, {region}\n{postal_code}",
                    "field_order": ["salutation", "first_name", "last_name", "organization", "street", "house", "apartment", "city", "region", "postal_code", "country"],
                    "required_fields": ["street", "city", "country"],
                    "postal_code_required": True,
                    "country_specific": True,
                    "example": "Tashkent sh., Amir Temur ko'chasi, 1-uy\nTashkent, 100000\nO'zbekiston"
                },
                "en-US": {
                    "format_string": "{salutation} {first_name} {last_name}\n{organization}\n{street}\n{city}, {state} {zip}",
                    "field_order": ["salutation", "first_name", "last_name", "organization", "street", "apartment", "city", "state", "zip", "country"],
                    "required_fields": ["street", "city", "state", "zip"],
                    "postal_code_required": True,
                    "country_specific": True,
                    "example": "John Smith\n123 Main St\nAnytown, CA 90210\nUSA"
                }
            },
            "names": {
                "uz-UZ": {
                    "given_name_first": True,
                    "family_name_first": False,
                    "middle_name_position": "after_given",
                    "honorific_required": True,
                    "formality_level": "formal",
                    "cultural_notes": ["Use patronymic as middle name", "Respect titles and honorifics"]
                },
                "en-US": {
                    "given_name_first": True,
                    "family_name_first": False,
                    "middle_name_position": "after_given",
                    "honorific_required": False,
                    "formality_level": "casual",
                    "cultural_notes": ["Middle names are common", "Use nicknames informally"]
                }
            }
        }
        
        with open(self.base_path / "format_specifications.json", 'w', encoding='utf-8') as f:
            json.dump(default_formats, f, indent=2, ensure_ascii=False)
        
        # Load into cache
        for region, data in default_formats["addresses"].items():
            self.address_formats[region] = AddressFormat(**data)
        
        for region, data in default_formats["names"].items():
            self.name_formats[region] = NameFormat(**data)
    
    def _auto_detect_locale(self) -> None:
        """Auto-detect user locale"""
        start_time = time.time()
        
        try:
            # Try system locale
            system_locale = self._detect_system_locale()
            if system_locale:
                self.set_locale(system_locale)
                self.detection_times.append(time.time() - start_time)
                return
            
            # Try browser headers (would need web framework integration)
            # browser_locale = self._detect_browser_locale()
            # if browser_locale:
            #     self.set_locale(browser_locale)
            #     self.detection_times.append(time.time() - start_time)
            #     return
            
            # Try geolocation (if enabled)
            if self.geolocation_enabled:
                geo_locale = self._detect_geolocation()
                if geo_locale:
                    self.set_locale(geo_locale)
                    self.detection_times.append(time.time() - start_time)
                    return
            
            # Fallback to default
            self.set_locale("en-US")
            
        except Exception as e:
            self.logger.error(f"Error auto-detecting locale: {e}")
            self.set_locale("en-US")
    
    def _detect_system_locale(self) -> Optional[str]:
        """Detect system locale"""
        try:
            # Try using locale module
            current_locale = locale.getdefaultlocale()[0]
            if current_locale:
                # Convert to our format (e.g., en_US -> en-US)
                locale_code = current_locale.replace('_', '-')
                # Check if the locale is supported
                if locale_code in self.locale_cache:
                    return locale_code
        except:
            pass
        
        try:
            # Try using environment variables
            for env_var in ['LANG', 'LC_ALL', 'LC_CTYPE']:
                env_value = os.environ.get(env_var)
                if env_value:
                    locale_code = env_value.split('.')[0].replace('_', '-')
                    if locale_code in self.locale_cache:
                        return locale_code
        except:
            pass
        
        return None
    
    def _detect_geolocation(self) -> Optional[str]:
        """Detect location using geolocation services"""
        try:
            # This would typically use a geolocation service
            # For demonstration, we'll use a simple approach
            
            # Get public IP (you might want to use a service for this)
            # response = requests.get('https://httpbin.org/ip', timeout=5)
            # if response.status_code == 200:
            #     ip_info = response.json()
            #     # Would then lookup IP to country mapping
            #     # For now, return a default
            
            # Simple country code detection based on system info
            country_code = self._get_system_country_code()
            if country_code:
                # Combine with language (could be improved)
                language_code = "en"  # Default
                return f"{language_code}-{country_code}"
        except:
            pass
        
        return None
    
    def _get_system_country_code(self) -> Optional[str]:
        """Get country code from system information"""
        try:
            # This is a simplified implementation
            # In production, you'd want more robust detection
            
            # Check system time zone for clues
            import tzlocal
            local_timezone = str(tzlocal.get_localzone())
            
            timezone_mapping = {
                "America/New_York": "US",
                "America/Los_Angeles": "US",
                "Europe/London": "GB",
                "Europe/Paris": "FR",
                "Europe/Berlin": "DE",
                "Asia/Tokyo": "JP",
                "Asia/Shanghai": "CN",
                "Asia/Samarkand": "UZ",
                "Asia/Tashkent": "UZ",
                "Asia/Riyadh": "SA",
                "Asia/Dubai": "AE"
            }
            
            return timezone_mapping.get(local_timezone)
        except:
            pass
        
        return None
    
    def set_locale(self, locale_code: str) -> bool:
        """
        Set current locale
        
        Args:
            locale_code: Locale code (e.g., 'en-US', 'uz-UZ')
        
        Returns:
            bool: Success status
        """
        if locale_code not in self.locale_cache:
            self.logger.warning(f"Locale {locale_code} not supported")
            return False
        
        self.current_locale = locale_code
        locale_info = self.locale_cache[locale_code]
        
        # Set timezone based on strategy
        if self.timezone_strategy == TimeZoneStrategy.LOCAL:
            self.current_timezone = locale_info.timezone
        elif self.timezone_strategy == TimeZoneStrategy.USER_PREFERENCE:
            # Would check user preferences
            self.current_timezone = locale_info.timezone
        
        self.logger.info(f"Locale set to {locale_code}")
        return True
    
    def get_locale(self) -> Optional[str]:
        """Get current locale"""
        return self.current_locale
    
    def get_locale_info(self, locale_code: Optional[str] = None) -> Optional[LocaleInfo]:
        """
        Get locale information
        
        Args:
            locale_code: Locale code, uses current locale if None
        
        Returns:
            LocaleInfo or None
        """
        loc_code = locale_code or self.current_locale
        return self.locale_cache.get(loc_code)
    
    def format_number(self, number: Union[int, float], locale_code: Optional[str] = None, 
                     use_grouping: bool = True) -> str:
        """
        Format number according to locale
        
        Args:
            number: Number to format
            locale_code: Locale code
            use_grouping: Whether to use grouping separators
        
        Returns:
            Formatted number string
        """
        locale_info = self.get_locale_info(locale_code)
        if not locale_info:
            return str(number)
        
        # Handle different number systems
        if locale_info.number_system == NumberSystem.ARABIC_INDIC.value:
            return self._format_arabic_indic(number, use_grouping)
        elif locale_info.number_system == NumberSystem.EASTERN_ARABIC.value:
            return self._format_eastern_arabic(number, use_grouping)
        else:
            return self._format_decimal(number, locale_info, use_grouping)
    
    def _format_decimal(self, number: Union[int, float], locale_info: LocaleInfo, 
                       use_grouping: bool) -> str:
        """Format decimal number"""
        # Convert to string with appropriate separators
        if isinstance(number, int):
            formatted = str(number)
        else:
            formatted = f"{number:.2f}"  # Default to 2 decimal places
        
        # Split integer and decimal parts
        if '.' in formatted:
            integer_part, decimal_part = formatted.split('.')
            decimal_sep = locale_info.decimal_separator
            if not use_grouping:
                return f"{integer_part}{decimal_sep}{decimal_part}"
            
            # Add thousands separator
            thousands_sep = locale_info.thousands_separator
            integer_part = self._add_thousands_separator(integer_part, thousands_sep)
            return f"{integer_part}{decimal_sep}{decimal_part}"
        else:
            if not use_grouping:
                return formatted
            
            thousands_sep = locale_info.thousands_separator
            return self._add_thousands_separator(formatted, thousands_sep)
    
    def _add_thousands_separator(self, number_str: str, separator: str) -> str:
        """Add thousands separator to number string"""
        if len(number_str) <= 3:
            return number_str
        
        result = ""
        for i, digit in enumerate(reversed(number_str)):
            if i > 0 and i % 3 == 0:
                result = separator + result
            result = digit + result
        
        return result
    
    def _format_arabic_indic(self, number: Union[int, float], use_grouping: bool) -> str:
        """Format number in Arabic-Indic numeral system"""
        # Arabic-Indic numerals: ٠١٢٣٤٥٦٧٨٩
        arabic_indic_digits = '٠١٢٣٤٥٦٧٨٩'
        english_digits = '0123456789'
        
        # Convert number to string
        number_str = str(number)
        
        # Translate digits
        translated = ''.join(arabic_indic_digits[int(d)] if d.isdigit() else d 
                           for d in number_str)
        
        return translated
    
    def _format_eastern_arabic(self, number: Union[int, float], use_grouping: bool) -> str:
        """Format number in Eastern Arabic numeral system"""
        # Eastern Arabic numerals: ۰۱۲۳۴۵۶۷۸۹
        eastern_arabic_digits = '۰۱۲۳۴۵۶۷۸۹'
        english_digits = '0123456789'
        
        # Convert number to string
        number_str = str(number)
        
        # Translate digits
        translated = ''.join(eastern_arabic_digits[int(d)] if d.isdigit() else d 
                           for d in number_str)
        
        return translated
    
    def format_currency(self, amount: Union[int, float], currency: Optional[str] = None,
                       locale_code: Optional[str] = None, format_type: str = "symbol") -> str:
        """
        Format currency according to locale
        
        Args:
            amount: Amount to format
            currency: Currency code
            locale_code: Locale code
            format_type: Format type ('symbol', 'code', 'name')
        
        Returns:
            Formatted currency string
        """
        locale_info = self.get_locale_info(locale_code)
        if not locale_info:
            return f"{amount} {currency}"
        
        currency = currency or locale_info.currency
        formatted_amount = self.format_number(amount, locale_code)
        
        cultural_pref = self.cultural_preferences.get(locale_code)
        if cultural_pref:
            format_template = cultural_pref.currency_preferences.get("format", "{amount} {currency}")
            position = cultural_pref.currency_preferences.get("position", "after")
            display = cultural_pref.currency_preferences.get("currency_display", "symbol")
            
            if position == "before":
                return format_template.format(amount=formatted_amount, currency=currency)
            else:
                return format_template.format(amount=formatted_amount, currency=currency)
        
        # Default formatting
        if format_type == "symbol" and currency in ["USD", "EUR", "GBP", "JPY", "CNY"]:
            symbols = {
                "USD": "$",
                "EUR": "€",
                "GBP": "£",
                "JPY": "¥",
                "CNY": "¥"
            }
            currency_symbol = symbols.get(currency, currency)
            return f"{currency_symbol}{formatted_amount}"
        else:
            return f"{formatted_amount} {currency}"
    
    def format_date(self, date_obj: datetime, format_type: LocaleFormat = LocaleFormat.STANDARD,
                   locale_code: Optional[str] = None, relative: bool = False) -> str:
        """
        Format date according to locale
        
        Args:
            date_obj: Date object to format
            format_type: Date format type
            locale_code: Locale code
            relative: Whether to use relative formatting
        
        Returns:
            Formatted date string
        """
        locale_info = self.get_locale_info(locale_code)
        if not locale_info:
            return date_obj.strftime("%Y-%m-%d")
        
        if relative:
            return self._format_relative_date(date_obj, locale_info)
        
        date_format = locale_info.date_format
        
        # Replace format tokens
        date_format = date_format.replace("YYYY", "%Y")
        date_format = date_format.replace("MM", "%m")
        date_format = date_format.replace("DD", "%d")
        
        if format_type == LocaleFormat.SHORT:
            date_format = date_format.replace("YYYY", "%y")
        
        return date_obj.strftime(date_format)
    
    def _format_relative_date(self, date_obj: datetime, locale_info: LocaleInfo) -> str:
        """Format date relatively"""
        now = datetime.now()
        diff = now - date_obj
        
        if diff.days == 0:
            if diff.seconds < 60:
                return "hozir"
            elif diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} daqiqa oldin"
            else:
                hours = diff.seconds // 3600
                return f"{hours} soat oldin"
        elif diff.days == 1:
            return "kecha"
        elif diff.days < 7:
            return f"{diff.days} kun oldin"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} hafta oldin"
        elif diff.days < 365:
            months = diff.days // 30
            return f"{months} oy oldin"
        else:
            years = diff.days // 365
            return f"{years} yil oldin"
    
    def format_time(self, time_obj: datetime, format_type: LocaleFormat = LocaleFormat.STANDARD,
                   locale_code: Optional[str] = None, show_seconds: bool = False) -> str:
        """
        Format time according to locale
        
        Args:
            time_obj: Time object to format
            format_type: Time format type
            locale_code: Locale code
            show_seconds: Whether to include seconds
        
        Returns:
            Formatted time string
        """
        locale_info = self.get_locale_info(locale_code)
        if not locale_info:
            return time_obj.strftime("%H:%M")
        
        time_format = locale_info.time_format
        
        # Handle 12-hour vs 24-hour format
        if "a" in time_format.lower() or "am/pm" in time_format.lower():
            # 12-hour format
            time_str = time_obj.strftime("%I:%M")
            if show_seconds:
                time_str = time_obj.strftime("%I:%M:%S")
            
            # Add AM/PM
            am_pm = time_obj.strftime("%p").lower()
            if locale_code and "uz" in locale_code.lower():
                # Uzbek format
                am_pm = "AM" if am_pm == "am" else "PM"
            else:
                # English format
                am_pm = am_pm.upper()
            
            return f"{time_str} {am_pm}"
        else:
            # 24-hour format
            if show_seconds:
                return time_obj.strftime("%H:%M:%S")
            else:
                return time_obj.strftime("%H:%M")
    
    def format_address(self, address_data: Dict[str, str], 
                      locale_code: Optional[str] = None) -> str:
        """
        Format address according to locale
        
        Args:
            address_data: Address data dictionary
            locale_code: Locale code
        
        Returns:
            Formatted address string
        """
        locale_code = locale_code or self.current_locale
        if not locale_code or locale_code not in self.address_formats:
            return str(address_data)
        
        address_format = self.address_formats[locale_code]
        format_string = address_format.format_string
        
        # Replace placeholders with actual data
        formatted_address = format_string
        for field, value in address_data.items():
            placeholder = "{" + field + "}"
            formatted_address = formatted_address.replace(placeholder, str(value))
        
        return formatted_address
    
    def format_name(self, name_data: Dict[str, str], 
                   locale_code: Optional[str] = None, format_type: str = "full") -> str:
        """
        Format name according to locale
        
        Args:
            name_data: Name data dictionary
            locale_code: Locale code
            format_type: Format type ('full', 'given', 'family')
        
        Returns:
            Formatted name string
        """
        locale_code = locale_code or self.current_locale
        if not locale_code or locale_code not in self.name_formats:
            # Fallback to simple formatting
            if format_type == "full":
                return f"{name_data.get('first_name', '')} {name_data.get('last_name', '')}"
            elif format_type == "given":
                return name_data.get('first_name', '')
            else:
                return name_data.get('last_name', '')
        
        name_format = self.name_formats[locale_code]
        
        if format_type == "full":
            if name_format.given_name_first:
                parts = []
                if name_data.get('salutation'):
                    parts.append(name_data['salutation'])
                if name_data.get('first_name'):
                    parts.append(name_data['first_name'])
                if name_data.get('middle_name') and name_format.middle_name_position == "after_given":
                    parts.append(name_data['middle_name'])
                if name_data.get('last_name'):
                    parts.append(name_data['last_name'])
                return " ".join(parts)
            else:
                # Family name first
                parts = []
                if name_data.get('salutation'):
                    parts.append(name_data['salutation'])
                if name_data.get('last_name'):
                    parts.append(name_data['last_name'])
                if name_data.get('first_name'):
                    parts.append(name_data['first_name'])
                return " ".join(parts)
        
        elif format_type == "given":
            return name_data.get('first_name', '')
        else:  # family
            return name_data.get('last_name', '')
    
    def get_cultural_adaptations(self, content: str, content_type: str = "general",
                               locale_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get cultural adaptations for content
        
        Args:
            content: Content to adapt
            content_type: Type of content ('general', 'ui', 'marketing', 'legal')
            locale_code: Locale code
        
        Returns:
            Dictionary of cultural adaptations
        """
        locale_code = locale_code or self.current_locale
        if not locale_code or locale_code not in self.cultural_preferences:
            return {}
        
        cultural_pref = self.cultural_preferences[locale_code]
        adaptations = {
            "communication_style": cultural_pref.communication_style,
            "tone_adjustments": self._get_tone_adjustments(content, cultural_pref),
            "cultural_elements": self._get_cultural_elements(content, cultural_pref),
            "visual_suggestions": self._get_visual_suggestions(content, cultural_pref),
            "avoidance_list": cultural_pref.cultural_taboos
        }
        
        return adaptations
    
    def _get_tone_adjustments(self, content: str, cultural_pref: CulturalPreferences) -> Dict[str, Any]:
        """Get tone adjustments based on cultural preferences"""
        adjustments = {
            "formality_level": cultural_pref.business_culture.get("hierarchy", "medium"),
            "directness": cultural_pref.business_culture.get("communication", "medium"),
            "context_requirement": cultural_pref.context_level
        }
        
        return adjustments
    
    def _get_cultural_elements(self, content: str, cultural_pref: CulturalPreferences) -> List[str]:
        """Get cultural elements to include"""
        elements = []
        
        # Add relevant holidays if content is time-sensitive
        current_month = datetime.now().month
        relevant_holidays = [
            holiday for holiday in cultural_pref.holiday_calendar
            if self._is_holiday_relevant(holiday, current_month)
        ]
        
        elements.extend(relevant_holidays)
        
        return elements
    
    def _get_visual_suggestions(self, content: str, cultural_pref: CulturalPreferences) -> List[str]:
        """Get visual design suggestions"""
        suggestions = []
        
        # Color preferences
        suggestions.extend([
            f"Use {color} for positive messaging" 
            for color in cultural_pref.color_preferences.keys()
            if "good" in cultural_pref.color_preferences[color] or 
               "blessing" in cultural_pref.color_preferences[color]
        ])
        
        # Avoid problematic colors
        problematic_colors = [
            color for color, meaning in cultural_pref.color_preferences.items()
            if "death" in meaning or "danger" in meaning or "taboo" in meaning
        ]
        
        if problematic_colors:
            suggestions.append(f"Avoid using {', '.join(problematic_colors)} in this context")
        
        return suggestions
    
    def _is_holiday_relevant(self, holiday: str, current_month: int) -> bool:
        """Check if holiday is relevant for current month"""
        # Simplified implementation - would need proper holiday calendar data
        month_mapping = {
            "new_year": [1],
            "womens_day": [3],
            "navruz": [3],
            "victory_day": [5],
            "independence_day": [9],
            "teacher_day": [10],
            "constitution_day": [12]
        }
        
        return holiday in month_mapping and current_month in month_mapping[holiday]
    
    def get_phone_format(self, phone_number: str, locale_code: Optional[str] = None) -> str:
        """
        Format phone number according to locale
        
        Args:
            phone_number: Phone number to format
            locale_code: Locale code
        
        Returns:
            Formatted phone number
        """
        locale_info = self.get_locale_info(locale_code)
        if not locale_info or not locale_info.phone_format:
            return phone_number
        
        # Simple formatting - would need more sophisticated parsing in production
        digits_only = re.sub(r'[^\d]', '', phone_number)
        
        format_template = locale_info.phone_format
        formatted_number = ""
        digit_index = 0
        
        for char in format_template:
            if char == 'X':
                if digit_index < len(digits_only):
                    formatted_number += digits_only[digit_index]
                    digit_index += 1
            else:
                formatted_number += char
        
        # Add remaining digits
        if digit_index < len(digits_only):
            formatted_number += digits_only[digit_index:]
        
        return formatted_number
    
    def get_measurement_conversion(self, value: float, from_system: str, to_system: str,
                                  measurement_type: str) -> float:
        """
        Convert between measurement systems
        
        Args:
            value: Value to convert
            from_system: Source measurement system
            to_system: Target measurement system
            measurement_type: Type of measurement ('length', 'weight', 'temperature', 'volume')
        
        Returns:
            Converted value
        """
        conversions = {
            "length": {
                "metric_to_imperial": {
                    "m_to_ft": 3.28084,
                    "cm_to_in": 0.393701,
                    "km_to_mi": 0.621371
                },
                "imperial_to_metric": {
                    "ft_to_m": 0.3048,
                    "in_to_cm": 2.54,
                    "mi_to_km": 1.60934
                }
            },
            "weight": {
                "metric_to_imperial": {
                    "kg_to_lb": 2.20462
                },
                "imperial_to_metric": {
                    "lb_to_kg": 0.453592
                }
            },
            "temperature": {
                "metric_to_imperial": {
                    "c_to_f": lambda x: x * 9/5 + 32
                },
                "imperial_to_metric": {
                    "f_to_c": lambda x: (x - 32) * 5/9
                }
            }
        }
        
        if measurement_type not in conversions:
            return value
        
        conversion_direction = f"{from_system}_to_{to_system}"
        if conversion_direction in conversions[measurement_type]:
            conversion = conversions[measurement_type][conversion_direction]
            
            if callable(conversion):
                return conversion(value)
            else:
                return value * conversion
        
        return value
    
    def get_available_locales(self) -> List[Dict[str, Any]]:
        """
        Get list of available locales
        
        Returns:
            List of locale dictionaries
        """
        locales = []
        for locale_code, locale_info in self.locale_cache.items():
            locales.append({
                "code": locale_code,
                "language": locale_info.language_code,
                "country": locale_info.country_code,
                "region": locale_info.region_name,
                "timezone": locale_info.timezone,
                "currency": locale_info.currency,
                "reading_direction": locale_info.reading_direction
            })
        
        return sorted(locales, key=lambda x: x["region"])
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get localization statistics
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_locales": len(self.locale_cache),
            "supported_countries": len(set(info.country_code for info in self.locale_cache.values())),
            "supported_languages": len(set(info.language_code for info in self.locale_cache.values())),
            "rtl_locales": len([info for info in self.locale_cache.values() if info.reading_direction == "rtl"]),
            "current_locale": self.current_locale,
            "current_timezone": self.current_timezone,
            "timezone_strategy": self.timezone_strategy.value,
            "cache_stats": {
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "detection_times": self.detection_times[-10:]  # Last 10
            }
        }
        
        return stats


# Example usage
if __name__ == "__main__":
    # Initialize localization manager
    lm = LocalizationManager()
    
    # Auto-detect and set locale
    print("Auto-detected locale:", lm.get_locale())
    
    # Format numbers
    print("Formatted number:", lm.format_number(1234567.89))
    print("Currency:", lm.format_currency(1234.56))
    
    # Format dates and times
    from datetime import datetime
    now = datetime.now()
    print("Date:", lm.format_date(now))
    print("Time:", lm.format_time(now))
    
    # Format address
    address_data = {
        "street": "Main Street",
        "house": "123",
        "city": "Tashkent",
        "region": "Tashkent Region",
        "postal_code": "100000",
        "country": "O'zbekiston"
    }
    print("Address:", lm.format_address(address_data))
    
    # Format name
    name_data = {
        "salutation": "Mr.",
        "first_name": "Aziz",
        "last_name": "Karimov"
    }
    print("Name:", lm.format_name(name_data))
    
    # Get cultural adaptations
    adaptations = lm.get_cultural_adaptations("Welcome to our service!")
    print("Cultural adaptations:", adaptations)
    
    # Measurement conversion
    converted = lm.get_measurement_conversion(25, "celsius", "fahrenheit", "temperature")
    print("25°C to Fahrenheit:", converted)
    
    # Get statistics
    stats = lm.get_statistics()
    print("Statistics:", stats)