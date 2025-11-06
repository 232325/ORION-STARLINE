"""
UI Customizer Module
===================

Ushbu modul treyderlarning shaxsiyatiga mos UI sozlashlarini boshqaradi
va dinamik tarzda interfeysni moslashtiradi.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import logging
from trading_personality import TradingPersonalityType, PersonalityProfile

class ColorTheme(Enum):
    """Rang temalari"""
    DARK = "dark"
    LIGHT = "light"
    HIGH_CONTRAST = "high_contrast"
    COLORFUL = "colorful"
    MINIMAL = "minimal"

class LayoutDensity(Enum):
    """Interfeys zichligi"""
    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"

class ChartStyle(Enum):
    """Grafik uslublari"""
    CANDLESTICK = "candlestick"
    HEIKIN_ASHI = "heikin_ashi"
    LINE = "line"
    MOUNTAIN = "mountain"
    OHLC = "ohlc"

@dataclass
class UISettings:
    """UI sozlamalar profili"""
    trader_id: str
    theme: ColorTheme
    layout_density: LayoutDensity
    primary_color: str
    secondary_color: str
    background_color: str
    text_color: str
    chart_style: ChartStyle
    timeframes: List[str]
    widget_layout: Dict[str, Any]
    font_size: str
    animation_speed: str
    alert_settings: Dict[str, Any]
    navigation_style: str
    mobile_optimized: bool
    accessibility_features: List[str]

class UICustomizer:
    """
    UI Customization Engine
    ======================
    
    Personality Profile asosida UI sozlashlarini boshqaradi
    """
    
    def __init__(self, data_dir: str = "/workspace/orion-starline/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # UI Settings saqlash
        self.ui_settings_path = self.data_dir / "ui_settings.json"
        self.ui_settings = self._load_ui_settings()
        
        # Theme konfiguratsiyalari
        self.themes = self._load_theme_configs()
        
        # Layout templates
        self.layout_templates = self._load_layout_templates()
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def _load_ui_settings(self) -> Dict[str, UISettings]:
        """Mavjud UI sozlamalarni yuklash"""
        if self.ui_settings_path.exists():
            try:
                with open(self.ui_settings_path, 'r') as f:
                    data = json.load(f)
                    settings = {}
                    for trader_id, settings_data in data.items():
                        settings[trader_id] = UISettings(
                            trader_id=trader_id,
                            theme=ColorTheme(settings_data['theme']),
                            layout_density=LayoutDensity(settings_data['layout_density']),
                            primary_color=settings_data['primary_color'],
                            secondary_color=settings_data['secondary_color'],
                            background_color=settings_data['background_color'],
                            text_color=settings_data['text_color'],
                            chart_style=ChartStyle(settings_data['chart_style']),
                            timeframes=settings_data['timeframes'],
                            widget_layout=settings_data['widget_layout'],
                            font_size=settings_data['font_size'],
                            animation_speed=settings_data['animation_speed'],
                            alert_settings=settings_data['alert_settings'],
                            navigation_style=settings_data['navigation_style'],
                            mobile_optimized=settings_data['mobile_optimized'],
                            accessibility_features=settings_data['accessibility_features']
                        )
                    return settings
            except Exception as e:
                self.logger.error(f"UI sozlamalarni yuklashda xato: {e}")
        return {}
    
    def _load_theme_configs(self) -> Dict[str, Dict]:
        """Rang temalari konfiguratsiyasi"""
        return {
            "scalper": {
                "theme": ColorTheme.DARK,
                "colors": {
                    "primary": "#FF4444",     # Qizil
                    "secondary": "#00CC88",   # Yashil
                    "background": "#0A0A0A",  # Qora
                    "surface": "#1A1A1A",     # Kulrang-qora
                    "text": "#FFFFFF",        # Oq
                    "text_secondary": "#CCCCCC", # Kulrang
                    "profit": "#00FF88",      # Yashil
                    "loss": "#FF4444",        # Qizil
                    "warning": "#FFA500",     # Tilla
                    "info": "#0088FF"         # Ko'k
                },
                "layout": LayoutDensity.COMPACT,
                "font_size": "small",
                "animation": "fast"
            },
            
            "day_trader": {
                "theme": ColorTheme.DARK,
                "colors": {
                    "primary": "#4ECDC4",     # Turquoise
                    "secondary": "#45B7D1",   # Ko'k
                    "background": "#1A202C",  # Qo'yilma ko'k
                    "surface": "#2D3748",     # Kulrang-ko'k
                    "text": "#F7FAFC",        # Oq-kulrang
                    "text_secondary": "#CBD5E0", # O'rta kulrang
                    "profit": "#48BB78",      # Yashil
                    "loss": "#F56565",        # Qizil
                    "warning": "#ED8936",     # To'q sariq
                    "info": "#4299E1"         # Ko'k
                },
                "layout": LayoutDensity.COMFORTABLE,
                "font_size": "medium",
                "animation": "normal"
            },
            
            "swing_trader": {
                "theme": ColorTheme.LIGHT,
                "colors": {
                    "primary": "#805AD5",     # Binafsha
                    "secondary": "#F56565",   # Qizil
                    "background": "#F7FAFC",  # Oq-kulrang
                    "surface": "#FFFFFF",     # Oq
                    "text": "#1A202C",        # Qora
                    "text_secondary": "#4A5568", # Kulrang
                    "profit": "#38A169",      # Yashil
                    "loss": "#E53E3E",        # Qizil
                    "warning": "#DD6B20",     # To'q sariq
                    "info": "#3182CE"         # Ko'k
                },
                "layout": LayoutDensity.COMFORTABLE,
                "font_size": "medium",
                "animation": "normal"
            },
            
            "position_trader": {
                "theme": ColorTheme.LIGHT,
                "colors": {
                    "primary": "#6B46C1",     # Binafsha
                    "secondary": "#9F7AEA",   # Och binafsha
                    "background": "#FFFBF7",  # Krem rang
                    "surface": "#FFFFFF",     # Oq
                    "text": "#2D3748",        # Qo'yilma
                    "text_secondary": "#4A5568", # Kulrang
                    "profit": "#2F855A",      # Yashil
                    "loss": "#C53030",        # Qizil
                    "warning": "#D69E2E",     # Tilla
                    "info": "#2B6CB0"         # Ko'k
                },
                "layout": LayoutDensity.SPACIOUS,
                "font_size": "large",
                "animation": "slow"
            },
            
            "algorithmic_trader": {
                "theme": ColorTheme.HIGH_CONTRAST,
                "colors": {
                    "primary": "#00FFFF",     # Cyan
                    "secondary": "#FF00FF",   # Magenta
                    "background": "#000000",  # To'liq qora
                    "surface": "#111111",     # Qizg'ish qora
                    "text": "#FFFFFF",        # Oq
                    "text_secondary": "#CCCCCC", # Kulrang
                    "profit": "#00FF00",      # Yashil
                    "loss": "#FF0000",        # Qizil
                    "warning": "#FFFF00",     # Sarguzasht
                    "info": "#0088FF"         # Ko'k
                },
                "layout": LayoutDensity.COMPACT,
                "font_size": "small",
                "animation": "none"
            },
            
            "value_investor": {
                "theme": ColorTheme.MINIMAL,
                "colors": {
                    "primary": "#2D3748",     # Qo'yilma
                    "secondary": "#4A5568",   # Kulrang
                    "background": "#F7FAFC",  # Oq-kulrang
                    "surface": "#FFFFFF",     # Oq
                    "text": "#1A202C",        # Qora
                    "text_secondary": "#4A5568", # Kulrang
                    "profit": "#2F855A",      # Yashil
                    "loss": "#E53E3E",        # Qizil
                    "warning": "#D69E2E",     # Tilla
                    "info": "#3182CE"         # Ko'k
                },
                "layout": LayoutDensity.SPACIOUS,
                "font_size": "medium",
                "animation": "minimal"
            },
            
            "growth_investor": {
                "theme": ColorTheme.COLORFUL,
                "colors": {
                    "primary": "#9F7AEA",     # Binafsha
                    "secondary": "#ED8936",   # To'q sariq
                    "background": "#F7FAFC",  # Oq-kulrang
                    "surface": "#FFFFFF",     # Oq
                    "text": "#2D3748",        # Qo'yilma
                    "text_secondary": "#4A5568", # Kulrang
                    "profit": "#38A169",      # Yashil
                    "loss": "#E53E3E",        # Qizil
                    "warning": "#D69E2E",     # Tilla
                    "info": "#3182CE"         # Ko'k
                },
                "layout": LayoutDensity.COMFORTABLE,
                "font_size": "medium",
                "animation": "normal"
            },
            
            "conservative": {
                "theme": ColorTheme.LIGHT,
                "colors": {
                    "primary": "#2B6CB0",     # Ko'k
                    "secondary": "#38A169",   # Yashil
                    "background": "#F9FAFB",  # Oq-kulrang
                    "surface": "#FFFFFF",     # Oq
                    "text": "#1F2937",        # Qo'yilma
                    "text_secondary": "#6B7280", # Kulrang
                    "profit": "#059669",      # Yashil
                    "loss": "#DC2626",        # Qizil
                    "warning": "#D97706",     # To'q sariq
                    "info": "#2563EB"         # Ko'k
                },
                "layout": LayoutDensity.SPACIOUS,
                "font_size": "large",
                "animation": "slow"
            },
            
            "aggressive": {
                "theme": ColorTheme.HIGH_CONTRAST,
                "colors": {
                    "primary": "#FF0000",     # Qizil
                    "secondary": "#FFFF00",   # Sarguzasht
                    "background": "#000000",  # Qora
                    "surface": "#1A1A1A",     # Qizg'ish qora
                    "text": "#FFFFFF",        # Oq
                    "text_secondary": "#FFA500", # Tilla
                    "profit": "#00FF00",      # Yashil
                    "loss": "#FF0000",        # Qizil
                    "warning": "#FFFF00",     # Sarguzasht
                    "info": "#00FFFF"         # Cyan
                },
                "layout": LayoutDensity.COMPACT,
                "font_size": "medium",
                "animation": "fast"
            }
        }
    
    def _load_layout_templates(self) -> Dict[str, Dict]:
        """Layout shablonlari"""
        return {
            "scalper_dashboard": {
                "type": "grid",
                "columns": 3,
                "rows": 2,
                "widgets": [
                    {
                        "id": "order_book",
                        "type": "orderbook",
                        "position": {"x": 0, "y": 0, "w": 2, "h": 1},
                        "priority": "high"
                    },
                    {
                        "id": "time_sales",
                        "type": "timesales",
                        "position": {"x": 2, "y": 0, "w": 1, "h": 1},
                        "priority": "high"
                    },
                    {
                        "id": "chart_1m",
                        "type": "chart",
                        "position": {"x": 0, "y": 1, "w": 1, "h": 1},
                        "priority": "high"
                    },
                    {
                        "id": "chart_5m",
                        "type": "chart", 
                        "position": {"x": 1, "y": 1, "w": 1, "h": 1},
                        "priority": "medium"
                    },
                    {
                        "id": "positions",
                        "type": "positions",
                        "position": {"x": 2, "y": 1, "w": 1, "h": 1},
                        "priority": "high"
                    }
                ],
                "settings": {
                    "auto_refresh": True,
                    "refresh_interval": 500,  # milliseconds
                    "show_animations": True,
                    "compact_mode": True
                }
            },
            
            "day_trader_dashboard": {
                "type": "flexible",
                "columns": 4,
                "rows": 3,
                "widgets": [
                    {
                        "id": "main_chart",
                        "type": "chart",
                        "position": {"x": 0, "y": 0, "w": 3, "h": 2},
                        "priority": "high"
                    },
                    {
                        "id": "watchlist",
                        "type": "watchlist",
                        "position": {"x": 3, "y": 0, "w": 1, "h": 1},
                        "priority": "high"
                    },
                    {
                        "id": "portfolio",
                        "type": "portfolio",
                        "position": {"x": 3, "y": 1, "w": 1, "h": 1},
                        "priority": "medium"
                    },
                    {
                        "id": "news",
                        "type": "news",
                        "position": {"x": 0, "y": 2, "w": 2, "h": 1},
                        "priority": "medium"
                    },
                    {
                        "id": "economic_calendar",
                        "type": "calendar",
                        "position": {"x": 2, "y": 2, "w": 1, "h": 1},
                        "priority": "low"
                    },
                    {
                        "id": "sentiment",
                        "type": "sentiment",
                        "position": {"x": 3, "y": 2, "w": 1, "h": 1},
                        "priority": "low"
                    }
                ],
                "settings": {
                    "auto_refresh": True,
                    "refresh_interval": 1000,
                    "show_animations": True,
                    "compact_mode": False
                }
            },
            
            "swing_trader_dashboard": {
                "type": "sidebar",
                "main_area": {
                    "type": "chart",
                    "position": {"x": 0, "y": 0, "w": 3, "h": 2}
                },
                "sidebar": {
                    "position": {"x": 3, "y": 0, "w": 1, "h": 2},
                    "widgets": [
                        {
                            "id": "analysis_tools",
                            "type": "analysis",
                            "priority": "high"
                        },
                        {
                            "id": "news",
                            "type": "news",
                            "priority": "medium"
                        },
                        {
                            "id": "economic_indicators",
                            "type": "indicators",
                            "priority": "medium"
                        }
                    ]
                },
                "bottom": {
                    "type": "portfolio",
                    "position": {"x": 0, "y": 2, "w": 4, "h": 1}
                },
                "settings": {
                    "auto_refresh": True,
                    "refresh_interval": 5000,
                    "show_animations": False,
                    "compact_mode": False
                }
            },
            
            "position_trader_dashboard": {
                "type": "presentation",
                "main_focus": "charts",
                "widgets": [
                    {
                        "id": "long_term_chart",
                        "type": "chart",
                        "position": {"x": 0, "y": 0, "w": 4, "h": 2},
                        "timeframe": "daily",
                        "priority": "high"
                    },
                    {
                        "id": "fundamental_data",
                        "type": "fundamental",
                        "position": {"x": 0, "y": 2, "w": 2, "h": 1},
                        "priority": "high"
                    },
                    {
                        "id": "news_analysis",
                        "type": "news",
                        "position": {"x": 2, "y": 2, "w": 2, "h": 1},
                        "priority": "medium"
                    }
                ],
                "settings": {
                    "auto_refresh": True,
                    "refresh_interval": 30000,
                    "show_animations": False,
                    "compact_mode": False,
                    "focus_mode": True
                }
            }
        }
    
    def _save_ui_settings(self):
        """UI sozlamalarni saqlash"""
        try:
            settings_data = {}
            for trader_id, settings in self.ui_settings.items():
                settings_data[trader_id] = {
                    'theme': settings.theme.value,
                    'layout_density': settings.layout_density.value,
                    'primary_color': settings.primary_color,
                    'secondary_color': settings.secondary_color,
                    'background_color': settings.background_color,
                    'text_color': settings.text_color,
                    'chart_style': settings.chart_style.value,
                    'timeframes': settings.timeframes,
                    'widget_layout': settings.widget_layout,
                    'font_size': settings.font_size,
                    'animation_speed': settings.animation_speed,
                    'alert_settings': settings.alert_settings,
                    'navigation_style': settings.navigation_style,
                    'mobile_optimized': settings.mobile_optimized,
                    'accessibility_features': settings.accessibility_features
                }
            
            with open(self.ui_settings_path, 'w') as f:
                json.dump(settings_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"UI sozlamalarni saqlashda xato: {e}")
    
    def create_ui_settings(self, profile: PersonalityProfile) -> UISettings:
        """
        Personality Profile asosida UI sozlamalar yaratish
        """
        try:
            # Theme tanlash
            theme_config = self.themes.get(profile.personality_type.value, self.themes["day_trader"])
            colors = theme_config["colors"]
            
            # Layout shabloni
            layout_template = self._select_layout_template(profile)
            
            # Widget layout
            widget_layout = self._generate_widget_layout(profile, layout_template)
            
            # Alert settings
            alert_settings = self._generate_alert_settings(profile)
            
            # Timeframes
            timeframes = self._generate_timeframes(profile)
            
            # Accessibility features
            accessibility = self._generate_accessibility_features(profile)
            
            settings = UISettings(
                trader_id=profile.trader_id,
                theme=theme_config["theme"],
                layout_density=theme_config["layout"],
                primary_color=colors["primary"],
                secondary_color=colors["secondary"],
                background_color=colors["background"],
                text_color=colors["text"],
                chart_style=ChartStyle.CANDLESTICK,  # Default
                timeframes=timeframes,
                widget_layout=widget_layout,
                font_size=theme_config["font_size"],
                animation_speed=theme_config["animation"],
                alert_settings=alert_settings,
                navigation_style=self._determine_navigation_style(profile),
                mobile_optimized=True,
                accessibility_features=accessibility
            )
            
            # Saqlash
            self.ui_settings[profile.trader_id] = settings
            self._save_ui_settings()
            
            self.logger.info(f"UI sozlamalar yaratildi: {profile.trader_id}")
            return settings
            
        except Exception as e:
            self.logger.error(f"UI sozlamalar yaratishda xato: {e}")
            raise
    
    def _select_layout_template(self, profile: PersonalityProfile) -> Dict:
        """Layout shablonini tanlash"""
        template_mapping = {
            TradingPersonalityType.SCALPER: "scalper_dashboard",
            TradingPersonalityType.DAY_TRADER: "day_trader_dashboard",
            TradingPersonalityType.SWING_TRADER: "swing_trader_dashboard",
            TradingPersonalityType.POSITION_TRADER: "position_trader_dashboard",
        }
        
        template_name = template_mapping.get(profile.personality_type, "day_trader_dashboard")
        return self.layout_templates[template_name]
    
    def _generate_widget_layout(self, profile: PersonalityProfile, layout_template: Dict) -> Dict:
        """Widget layout generatsiyasi"""
        # Base layout
        layout = layout_template.copy()
        
        # Personality ga mos sozlamalar
        if profile.personality_type == TradingPersonalityType.SCALPER:
            # Yuqori chastotali - ko'proq real-time widgets
            layout["settings"]["refresh_interval"] = 250
            layout["settings"]["enable_live_data"] = True
            layout["settings"]["compact_mode"] = True
        
        elif profile.personality_type == TradingPersonalityType.POSITION_TRADER:
            # Uzun muddat - ko'proq tahlil widgets
            layout["settings"]["refresh_interval"] = 60000
            layout["settings"]["show_historical"] = True
            layout["settings"]["enable_research"] = True
        
        # Decision speed asosida
        if profile.decision_speed == "fast":
            layout["settings"]["quick_actions"] = True
            layout["settings"]["hotkeys_enabled"] = True
        else:
            layout["settings"]["detailed_info"] = True
            layout["settings"]["explanations_enabled"] = True
        
        return layout
    
    def _generate_alert_settings(self, profile: PersonalityProfile) -> Dict[str, Any]:
        """Alert sozlamalari"""
        settings = {
            "enabled": True,
            "sound": True,
            "visual": True,
            "email": False,
            "push": False
        }
        
        # Frequency asosida
        if profile.trading_frequency > 20:  # Scalper
            settings["frequency"] = "high"
            settings["cooldown"] = 5  # sekundlar
        elif profile.trading_frequency > 2:  # Day trader
            settings["frequency"] = "medium"
            settings["cooldown"] = 30
        else:  # Position trader
            settings["frequency"] = "low"
            settings["cooldown"] = 300
        
        # Alert turlari
        if profile.personality_type == TradingPersonalityType.SCALPER:
            settings["types"] = ["price", "volume", "order_fill", "profit_target"]
        elif profile.personality_type == TradingPersonalityType.DAY_TRADER:
            settings["types"] = ["price", "news", "technical_signals", "breakouts"]
        elif profile.personality_type == TradingPersonalityType.POSITION_TRADER:
            settings["types"] = ["earnings", "fundamental", "long_term_trend"]
        else:
            settings["types"] = ["price", "important_news"]
        
        # Emotional stability asosida
        if profile.emotional_score < 0.5:  # Past stability
            settings["reduce_stress"] = True
            settings["positive_tone"] = True
            settings[" calmer_alerts"] = True
        
        return settings
    
    def _generate_timeframes(self, profile: PersonalityProfile) -> List[str]:
        """Timeframe tavsiyalari"""
        timeframe_map = {
            TradingPersonalityType.SCALPER: ["1s", "5s", "15s", "1m", "5m"],
            TradingPersonalityType.DAY_TRADER: ["1m", "5m", "15m", "1h", "4h"],
            TradingPersonalityType.SWING_TRADER: ["15m", "1h", "4h", "1d", "1w"],
            TradingPersonalityType.POSITION_TRADER: ["1h", "4h", "1d", "1w", "1M"],
            TradingPersonalityType.ALGORITHMIC_TRADER: ["1s", "5s", "1m", "5m", "15m"],
            TradingPersonalityType.VALUE_INVESTOR: ["1d", "1w", "1M", "3M", "1Y"],
            TradingPersonalityType.GROWTH_INVESTOR: ["1h", "4h", "1d", "1w", "1M"],
            TradingPersonalityType.CONSERVATIVE: ["1d", "1w", "1M", "3M", "1Y"],
            TradingPersonalityType.AGGRESSIVE: ["1m", "5m", "15m", "1h", "4h"]
        }
        
        return timeframe_map.get(profile.personality_type, ["1m", "5m", "1h", "1d"])
    
    def _generate_accessibility_features(self, profile: PersonalityProfile) -> List[str]:
        """Accessibility xususiyatlari"""
        features = []
        
        # Font size
        if profile.personality_type == TradingPersonalityType.POSITION_TRADER:
            features.extend(["large_fonts", "high_contrast"])
        elif profile.personality_type == TradingPersonalityType.SCALPER:
            features.append("small_fonts_efficiency")
        
        # Color adjustments
        if profile.risk_tolerance.value in ["very_low", "low"]:
            features.append("colorblind_friendly")
        
        # Keyboard navigation
        if profile.decision_speed == "fast":
            features.append("full_keyboard_navigation")
            features.append("hotkeys")
        
        # Screen reader support
        features.append("aria_labels")
        features.append("screen_reader_friendly")
        
        return features
    
    def _determine_navigation_style(self, profile: PersonalityProfile) -> str:
        """Navigation uslubi"""
        if profile.decision_speed == "fast":
            return "quick"
        elif profile.learning_style == "visual":
            return "icon_based"
        elif profile.emotional_score < 0.5:
            return "detailed_explanations"
        else:
            return "balanced"
    
    def update_ui_settings(self, trader_id: str, updates: Dict[str, Any]) -> UISettings:
        """Mavjud UI sozlamalarni yangilash"""
        if trader_id not in self.ui_settings:
            raise ValueError(f"Treyder topilmadi: {trader_id}")
        
        settings = self.ui_settings[trader_id]
        
        # Yangilash
        for key, value in updates.items():
            if hasattr(settings, key):
                if key == "theme" and isinstance(value, str):
                    setattr(settings, key, ColorTheme(value))
                elif key == "layout_density" and isinstance(value, str):
                    setattr(settings, key, LayoutDensity(value))
                elif key == "chart_style" and isinstance(value, str):
                    setattr(settings, key, ChartStyle(value))
                else:
                    setattr(settings, key, value)
        
        # Saqlash
        self._save_ui_settings()
        
        return settings
    
    def get_ui_settings(self, trader_id: str) -> Optional[UISettings]:
        """Treyder UI sozlamalarini olish"""
        return self.ui_settings.get(trader_id)
    
    def apply_theme_to_css(self, settings: UISettings) -> str:
        """CSS uchun theme qo'llash"""
        css_variables = f"""
        :root {{
            --primary-color: {settings.primary_color};
            --secondary-color: {settings.secondary_color};
            --background-color: {settings.background_color};
            --text-color: {settings.text_color};
            --font-size: {settings.font_size};
            --animation-speed: {settings.animation_speed};
        }}
        
        .trading-app {{
            background-color: var(--background-color);
            color: var(--text-color);
            font-size: {settings.font_size};
        }}
        
        .button-primary {{
            background-color: var(--primary-color);
            color: white;
        }}
        
        .profit {{
            color: var(--primary-color);
        }}
        
        .loss {{
            color: #ff4444;
        }}
        
        .widget {{
            padding: {1 if settings.layout_density == LayoutDensity.COMPACT else 2}rem;
            margin: {0.5 if settings.layout_density == LayoutDensity.COMPACT else 1}rem;
        }}
        """
        return css_variables
    
    def generate_responsive_config(self, settings: UISettings) -> Dict[str, Any]:
        """Responsive konfiguratsiya"""
        return {
            "breakpoints": {
                "mobile": "320px",
                "tablet": "768px", 
                "desktop": "1024px",
                "wide": "1440px"
            },
            "layouts": {
                "mobile": self._create_mobile_layout(settings),
                "tablet": self._create_tablet_layout(settings),
                "desktop": self._create_desktop_layout(settings)
            },
            "adaptations": {
                "hide_sidebar_on_mobile": True,
                "collapse_widgets_on_mobile": True,
                "simplify_navigation_mobile": settings.mobile_optimized,
                "reduce_widgets_tablet": settings.layout_density == LayoutDensity.SPACIOUS
            }
        }
    
    def _create_mobile_layout(self, settings: UISettings) -> Dict:
        """Mobile layout"""
        return {
            "type": "stack",
            "widgets": [
                {"id": "chart", "priority": 1, "collapsible": False},
                {"id": "positions", "priority": 2, "collapsible": True},
                {"id": "watchlist", "priority": 3, "collapsible": True},
                {"id": "news", "priority": 4, "collapsible": True}
            ],
            "navigation": "bottom_tabs"
        }
    
    def _create_tablet_layout(self, settings: UISettings) -> Dict:
        """Tablet layout"""
        return {
            "type": "grid",
            "columns": 2,
            "widgets": [
                {"id": "chart", "position": {"x": 0, "y": 0, "w": 2, "h": 2}, "priority": 1},
                {"id": "positions", "position": {"x": 0, "y": 2, "w": 1, "h": 1}, "priority": 2},
                {"id": "watchlist", "position": {"x": 1, "y": 2, "w": 1, "h": 1}, "priority": 3}
            ],
            "navigation": "side_drawer"
        }
    
    def _create_desktop_layout(self, settings: UISettings) -> Dict:
        """Desktop layout"""
        return settings.widget_layout
    
    def export_ui_config(self, trader_id: str, format: str = "json") -> str:
        """UI konfiguratsiyasini export qilish"""
        if trader_id not in self.ui_settings:
            raise ValueError(f"Treyder topilmadi: {trader_id}")
        
        settings = self.ui_settings[trader_id]
        
        if format == "json":
            config = {
                "trader_id": trader_id,
                "theme": settings.theme.value,
                "colors": {
                    "primary": settings.primary_color,
                    "secondary": settings.secondary_color,
                    "background": settings.background_color,
                    "text": settings.text_color
                },
                "layout": {
                    "density": settings.layout_density.value,
                    "widget_layout": settings.widget_layout
                },
                "chart": {
                    "style": settings.chart_style.value,
                    "timeframes": settings.timeframes
                },
                "accessibility": settings.accessibility_features,
                "responsive": self.generate_responsive_config(settings)
            }
            return json.dumps(config, indent=2)
        
        elif format == "css":
            return self.apply_theme_to_css(settings)
        
        else:
            raise ValueError(f"Qo'llab-quvvatlanmagan format: {format}")

# Test
if __name__ == "__main__":
    # Test
    from trading_personality import create_sample_profile, TradingPersonalityType
    
    customizer = UICustomizer()
    
    # Test profile
    profile = create_sample_profile("test_trader_001", "scalper")
    
    # UI settings yaratish
    settings = customizer.create_ui_settings(profile)
    print(f"UI Theme: {settings.theme.value}")
    print(f"Primary Color: {settings.primary_color}")
    print(f"Layout: {settings.layout_density.value}")
    
    # CSS generatsiya
    css = customizer.apply_theme_to_css(settings)
    print(f"\nGenerated CSS:\n{css[:200]}...")
    
    # Responsive config
    responsive = customizer.generate_responsive_config(settings)
    print(f"\nResponsive breakpoints: {len(responsive['breakpoints'])}")