"""
Smart Alert System - Keng qamrovli Smart Alert moduli

Ushbu modul quyidagi xususiyatlarni o'z ichiga oladi:
1. Price alerts (Custom price level alerts)
2. Multi-channel notifications (SMS, Email, Push, Telegram)
3. News-based alerts (Breaking news, market-moving events)
4. Custom watchlists (User-defined asset lists)
5. Technical indicator alerts (RSI, MACD, moving averages)
6. Volume alerts (Unusual trading volume)
7. Portfolio alerts (Portfolio value changes)
8. Risk alerts (Risk threshold breaches)
9. Calendar alerts (Economic events)
10. Alert history (Alert tracking and management)

Multiple notification providers (Twilio, SendGrid, Firebase)
Alert scheduling and automation
Custom alert rules engine
Real-time monitoring
Alert performance tracking

Foydalanish:
from ai_modules.smart_alerts import SmartAlertSystem

alerts = SmartAlertSystem()
alerts.add_price_alert("BTC", "above", 50000)
alerts.start_monitoring()
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
import sqlite3
import schedule
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import websocket
import uuid
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

# Optional imports
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


class AlertType(Enum):
    """Ogohlantirish turlari"""
    PRICE = "price"
    NEWS = "news"
    TECHNICAL = "technical"
    VOLUME = "volume"
    PORTFOLIO = "portfolio"
    RISK = "risk"
    CALENDAR = "calendar"
    CUSTOM = "custom"


class NotificationChannel(Enum):
    """Xabar yuborish kanallari"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    TELEGRAM = "telegram"
    SLACK = "slack"
    WEBHOOK = "webhook"


class AlertStatus(Enum):
    """Ogohlantirish holatlari"""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    PAUSED = "paused"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class AlertRule:
    """Ogohlantirish qoidalari"""
    id: str
    name: str
    alert_type: AlertType
    symbol: str
    condition: str
    threshold: float
    channel: NotificationChannel
    is_active: bool = True
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Alert:
    """Ogohlantirish ob'ekti"""
    id: str
    rule_id: str
    alert_type: AlertType
    symbol: str
    message: str
    severity: str
    channel: NotificationChannel
    status: AlertStatus
    triggered_at: datetime
    acknowledged: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class NotificationProvider:
    """Xabar yuborish provayderlarining asosiy klasi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def send(self, alert: Alert, message: str) -> bool:
        """Xabar yuborish"""
        raise NotImplementedError


class TwilioProvider(NotificationProvider):
    """Twilio SMS provayderi"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        if config.get('account_sid') and config.get('auth_token'):
            try:
                from twilio.rest import Client
                self.client = Client(config['account_sid'], config['auth_token'])
            except ImportError:
                self.logger.warning("Twilio kutubxonasi topilmadi")
    
    async def send(self, alert: Alert, message: str) -> bool:
        """SMS yuborish"""
        if not self.client:
            self.logger.error("Twilio client sozlanmagan")
            return False
        
        try:
            from_number = self.config.get('from_number')
            to_number = self.config.get('to_number')
            
            if not from_number or not to_number:
                self.logger.error("Twilio raqamlar sozlanmagan")
                return False
            
            message_instance = self.client.messages.create(
                body=f"[Smart Alert] {message}",
                from_=from_number,
                to=to_number
            )
            
            self.logger.info(f"SMS yuborildi: {message_instance.sid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Twilio SMS xatoligi: {e}")
            return False


class SendGridProvider(NotificationProvider):
    """SendGrid Email provayderi"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.from_email = config.get('from_email')
        self.to_email = config.get('to_email')
    
    async def send(self, alert: Alert, message: str) -> bool:
        """Email yuborish"""
        if not self.api_key:
            self.logger.error("SendGrid API key sozlanmagan")
            return False
        
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
            
            mail = Mail(
                from_email=self.from_email,
                to_emails=self.to_email,
                subject=f"Smart Alert - {alert.symbol}",
                html_content=f"""
                <h2>Smart Alert</h2>
                <p><strong>Symbol:</strong> {alert.symbol}</p>
                <p><strong>Turi:</strong> {alert.alert_type.value}</p>
                <p><strong>Xabar:</strong> {message}</p>
                <p><strong>Vaqt:</strong> {alert.triggered_at}</p>
                """
            )
            
            response = sg.send(mail)
            
            if response.status_code == 202:
                self.logger.info("Email yuborildi")
                return True
            else:
                self.logger.error(f"Email yuborish xatoligi: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"SendGrid xatoligi: {e}")
            return False


class TelegramProvider(NotificationProvider):
    """Telegram Bot provayderi"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bot_token = config.get('bot_token')
        self.chat_id = config.get('chat_id')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
    
    async def send(self, alert: Alert, message: str) -> bool:
        """Telegram xabar yuborish"""
        if not self.base_url or not self.chat_id:
            self.logger.error("Telegram sozlanmagan")
            return False
        
        try:
            telegram_message = f"""
🚨 Smart Alert 🚨

📊 Symbol: {alert.symbol}
🔔 Turi: {alert.alert_type.value}
📝 Xabar: {message}
⏰ Vaqt: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
⚡ Daraja: {alert.severity}
            """
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": telegram_message,
                    "parse_mode": "HTML"
                }
            )
            
            if response.status_code == 200:
                self.logger.info("Telegram xabar yuborildi")
                return True
            else:
                self.logger.error(f"Telegram xatoligi: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Telegram xatoligi: {e}")
            return False


class FirebaseProvider(NotificationProvider):
    """Firebase Push Notification provayderi"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not FIREBASE_AVAILABLE:
            self.logger.warning("Firebase kutubxonasi topilmadi")
            self.is_initialized = False
            return
        
        try:
            cred = credentials.Certificate(config.get('service_account_path'))
            firebase_admin.initialize_app(cred)
            self.is_initialized = True
        except Exception as e:
            self.logger.warning(f"Firebase init xatoligi: {e}")
            self.is_initialized = False
    
    async def send(self, alert: Alert, message: str) -> bool:
        """Push notification yuborish"""
        if not FIREBASE_AVAILABLE:
            self.logger.warning("Firebase kutubxonasi mavjud emas")
            return False
            
        if not self.is_initialized:
            self.logger.error("Firebase sozlanmagan")
            return False
        
        try:
            notification = messaging.Notification(
                title=f"Smart Alert - {alert.symbol}",
                body=message
            )
            
            message_data = {
                "alert_id": alert.id,
                "symbol": alert.symbol,
                "type": alert.alert_type.value,
                "message": message,
                "severity": alert.severity,
                "timestamp": alert.triggered_at.isoformat()
            }
            
            # Bu yerda FCM token olishi kerak
            fcm_token = self.config.get('fcm_token')
            
            if fcm_token:
                if not FIREBASE_AVAILABLE:
                    self.logger.error("Firebase kutubxonasi mavjud emas")
                    return False
                    
                message_instance = messaging.Message(
                    notification=notification,
                    data=message_data,
                    token=fcm_token
                )
                
                response = messaging.send(message_instance)
                self.logger.info(f"Push notification yuborildi: {response}")
                return True
            else:
                self.logger.error("FCM token topilmadi")
                return False
                
        except Exception as e:
            self.logger.error(f"Firebase xatoligi: {e}")
            return False


class TechnicalAnalyzer:
    """Texnik tahlilchi"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """RSI hisoblash"""
        if len(prices) < period + 1:
            return 50.0
        
        prices_array = np.array(prices)
        deltas = np.diff(prices_array)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """MACD hisoblash"""
        if len(prices) < slow:
            return {"macd": 0, "signal": 0, "histogram": 0}
        
        prices_array = np.array(prices)
        ema_fast = TechnicalAnalyzer._ema(prices_array, fast)
        ema_slow = TechnicalAnalyzer._ema(prices_array, slow)
        
        macd = ema_fast - ema_slow
        
        # Signal line
        if len(macd) >= signal:
            signal_line = TechnicalAnalyzer._ema(macd, signal)
        else:
            signal_line = np.zeros(len(macd))
        
        histogram = macd - signal_line
        
        return {
            "macd": float(macd[-1]) if len(macd) > 0 else 0,
            "signal": float(signal_line[-1]) if len(signal_line) > 0 else 0,
            "histogram": float(histogram[-1]) if len(histogram) > 0 else 0
        }
    
    @staticmethod
    def calculate_moving_average(prices: List[float], period: int) -> float:
        """Harakatli o'rtacha hisoblash"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return float(np.mean(prices[-period:]))
    
    @staticmethod
    def _ema(prices: np.ndarray, period: int) -> np.ndarray:
        """EMA hisoblash"""
        alpha = 2.0 / (period + 1.0)
        ema = np.zeros_like(prices)
        ema[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema[i] = alpha * prices[i] + (1 - alpha) * ema[i-1]
        
        return ema


class NewsAnalyzer:
    """Yangiliklar tahlilchisi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_key = config.get('news_api_key')
    
    def get_market_news(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """Yangiliklarni olish"""
        try:
            # Bu yerda yangiliklar API sini chaqirish mumkin
            # Hozircha mock data qaytaramiz
            return [
                {
                    "title": "Bitcoin reaches new all-time high",
                    "description": "BTC price surges above $50,000",
                    "url": "https://example.com/news/btc-high",
                    "published_at": datetime.now(),
                    "symbols": ["BTC"],
                    "sentiment": "positive",
                    "impact": "high"
                },
                {
                    "title": "Federal Reserve maintains interest rates",
                    "description": "Fed keeps rates unchanged",
                    "url": "https://example.com/news/fed-rates",
                    "published_at": datetime.now() - timedelta(hours=1),
                    "symbols": ["DXY", "SPY"],
                    "sentiment": "neutral",
                    "impact": "medium"
                }
            ]
        except Exception as e:
            self.logger.error(f"Yangiliklar olish xatoligi: {e}")
            return []


class CalendarAnalyzer:
    """Taqvim voqealari tahlilchisi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def get_economic_events(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Iqtisodiy voqealarni olish"""
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = datetime.now() + timedelta(days=7)
        
        # Mock data
        return [
            {
                "title": "US CPI Data Release",
                "description": "Consumer Price Index data",
                "event_time": start_date + timedelta(hours=8),
                "importance": "high",
                "expected_impact": "medium",
                "currency": "USD",
                "symbols": ["DXY", "SPY", "TNX"]
            },
            {
                "title": "ECB Interest Rate Decision",
                "description": "European Central Bank rate decision",
                "event_time": start_date + timedelta(days=2, hours=10),
                "importance": "high",
                "expected_impact": "high",
                "currency": "EUR",
                "symbols": ["EURUSD", "EURGBP", "VGX"]
            }
        ]


class PortfolioAnalyzer:
    """Portfolio tahlilchisi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def calculate_portfolio_value(self, holdings: Dict[str, float]) -> float:
        """Portfolio qiymatini hisoblash"""
        total_value = 0
        # Bu yerda real narxlarni olish kerak
        for symbol, quantity in holdings.items():
            # Mock price
            mock_price = 100.0 if "USD" in symbol else 50000.0
            total_value += quantity * mock_price
        return total_value
    
    def calculate_portfolio_change(self, current_value: float, previous_value: float) -> Dict[str, float]:
        """Portfolio o'zgarishlarini hisoblash"""
        if previous_value == 0:
            return {"absolute_change": current_value, "percentage_change": 0}
        
        absolute_change = current_value - previous_value
        percentage_change = (absolute_change / previous_value) * 100
        
        return {
            "absolute_change": absolute_change,
            "percentage_change": percentage_change
        }


class SmartAlertSystem:
    """Smart Alert System - Bosh sinf"""
    
    def __init__(self, config_path: str = "alert_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logger()
        
        # Ma'lumotlar bazasi
        self.db_path = "smart_alerts.db"
        self._init_database()
        
        # Xabar yuborish provayderlari
        self.notification_providers = self._init_notification_providers()
        
        # Tahlilchilar
        self.technical_analyzer = TechnicalAnalyzer()
        self.news_analyzer = NewsAnalyzer(self.config.get('news', {}))
        self.calendar_analyzer = CalendarAnalyzer(self.config.get('calendar', {}))
        self.portfolio_analyzer = PortfolioAnalyzer(self.config.get('portfolio', {}))
        
        # Monitoring
        self.alert_rules = {}
        self.active_alerts = []
        self.alert_history = []
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Watchlists
        self.watchlists = {}
        
        # Real-time data streams
        self.data_streams = {}
        
        self.logger.info("SmartAlertSystem boshlang'ich qilindi")
    
    def _load_config(self) -> Dict[str, Any]:
        """Konfiguratsiya faylini yuklash"""
        default_config = {
            "twilio": {
                "account_sid": "",
                "auth_token": "",
                "from_number": "",
                "to_number": ""
            },
            "sendgrid": {
                "api_key": "",
                "from_email": "",
                "to_email": ""
            },
            "telegram": {
                "bot_token": "",
                "chat_id": ""
            },
            "firebase": {
                "service_account_path": "",
                "fcm_token": ""
            },
            "news": {
                "news_api_key": ""
            },
            "monitoring": {
                "interval": 60,
                "max_alerts_per_hour": 100
            }
        }
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Default config bilan birlashtirish
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            self._save_config(default_config)
            return default_config
        except Exception as e:
            self.logger.error(f"Konfiguratsiya yuklash xatoligi: {e}")
            return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Konfiguratsiya faylini saqlash"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Konfiguratsiya saqlash xatoligi: {e}")
    
    def _setup_logger(self) -> logging.Logger:
        """Logger sozlamasi"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_database(self) -> None:
        """Ma'lumotlar bazasini boslang'ich qilish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Alert rules jadval
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alert_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    channel TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Alerts jadval
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    rule_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    status TEXT NOT NULL,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged BOOLEAN DEFAULT 0,
                    metadata TEXT,
                    FOREIGN KEY (rule_id) REFERENCES alert_rules (id)
                )
            ''')
            
            # Watchlists jadval
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlists (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    symbols TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Ma'lumotlar bazasi xatoligi: {e}")
    
    def _init_notification_providers(self) -> Dict[str, NotificationProvider]:
        """Xabar yuborish provayderlarini boslang'ich qilish"""
        providers = {}
        
        # Twilio
        if self.config.get('twilio', {}).get('account_sid'):
            providers['twilio'] = TwilioProvider(self.config['twilio'])
        
        # SendGrid
        if self.config.get('sendgrid', {}).get('api_key'):
            providers['sendgrid'] = SendGridProvider(self.config['sendgrid'])
        
        # Telegram
        if self.config.get('telegram', {}).get('bot_token'):
            providers['telegram'] = TelegramProvider(self.config['telegram'])
        
        # Firebase
        if self.config.get('firebase', {}).get('service_account_path'):
            providers['firebase'] = FirebaseProvider(self.config['firebase'])
        
        return providers
    
    # ===== PRICE ALERTS =====
    
    def add_price_alert(self, symbol: str, condition: str, threshold: float, 
                       channel: str = "email", name: str = None) -> str:
        """Narx ogohlantirish qo'shish"""
        rule_id = str(uuid.uuid4())
        
        rule = AlertRule(
            id=rule_id,
            name=name or f"{symbol} narx {condition} {threshold}",
            alert_type=AlertType.PRICE,
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            channel=NotificationChannel(channel.lower())
        )
        
        self.alert_rules[rule_id] = rule
        self._save_rule_to_db(rule)
        
        self.logger.info(f"Narx ogohlantirish qo'shildi: {rule.name}")
        return rule_id
    
    def add_technical_alert(self, symbol: str, indicator: str, condition: str, 
                          threshold: float, channel: str = "email", name: str = None) -> str:
        """Texnik indikator ogohlantirish qo'shish"""
        rule_id = str(uuid.uuid4())
        
        rule = AlertRule(
            id=rule_id,
            name=name or f"{symbol} {indicator} {condition} {threshold}",
            alert_type=AlertType.TECHNICAL,
            symbol=symbol,
            condition=f"{indicator}_{condition}",
            threshold=threshold,
            channel=NotificationChannel(channel.lower()),
            metadata={"indicator": indicator}
        )
        
        self.alert_rules[rule_id] = rule
        self._save_rule_to_db(rule)
        
        self.logger.info(f"Texnik ogohlantirish qo'shildi: {rule.name}")
        return rule_id
    
    def add_volume_alert(self, symbol: str, volume_multiplier: float, 
                        channel: str = "email", name: str = None) -> str:
        """Volume ogohlantirish qo'shish"""
        rule_id = str(uuid.uuid4())
        
        rule = AlertRule(
            id=rule_id,
            name=name or f"{symbol} unusual volume {volume_multiplier}x",
            alert_type=AlertType.VOLUME,
            symbol=symbol,
            condition="volume_above",
            threshold=volume_multiplier,
            channel=NotificationChannel(channel.lower())
        )
        
        self.alert_rules[rule_id] = rule
        self._save_rule_to_db(rule)
        
        self.logger.info(f"Volume ogohlantirish qo'shildi: {rule.name}")
        return rule_id
    
    def add_news_alert(self, keywords: List[str], sentiment: str = "any", 
                      channel: str = "telegram", name: str = None) -> str:
        """Yangiliklar ogohlantirish qo'shish"""
        rule_id = str(uuid.uuid4())
        
        rule = AlertRule(
            id=rule_id,
            name=name or f"News alert: {', '.join(keywords)}",
            alert_type=AlertType.NEWS,
            symbol="GLOBAL",
            condition="keywords",
            threshold=len(keywords),
            channel=NotificationChannel(channel.lower()),
            metadata={"keywords": keywords, "sentiment": sentiment}
        )
        
        self.alert_rules[rule_id] = rule
        self._save_rule_to_db(rule)
        
        self.logger.info(f"Yangiliklar ogohlantirish qo'shildi: {rule.name}")
        return rule_id
    
    def add_portfolio_alert(self, portfolio_name: str, change_threshold: float,
                           channel: str = "email", name: str = None) -> str:
        """Portfolio ogohlantirish qo'shish"""
        rule_id = str(uuid.uuid4())
        
        rule = AlertRule(
            id=rule_id,
            name=name or f"Portfolio {portfolio_name} change {change_threshold}%",
            alert_type=AlertType.PORTFOLIO,
            symbol=portfolio_name,
            condition="percentage_change",
            threshold=change_threshold,
            channel=NotificationChannel(channel.lower())
        )
        
        self.alert_rules[rule_id] = rule
        self._save_rule_to_db(rule)
        
        self.logger.info(f"Portfolio ogohlantirish qo'shildi: {rule.name}")
        return rule_id
    
    def add_risk_alert(self, symbol: str, risk_threshold: float,
                      channel: str = "email", name: str = None) -> str:
        """Risk ogohlantirish qo'shish"""
        rule_id = str(uuid.uuid4())
        
        rule = AlertRule(
            id=rule_id,
            name=name or f"{symbol} risk level {risk_threshold}",
            alert_type=AlertType.RISK,
            symbol=symbol,
            condition="risk_above",
            threshold=risk_threshold,
            channel=NotificationChannel(channel.lower())
        )
        
        self.alert_rules[rule_id] = rule
        self._save_rule_to_db(rule)
        
        self.logger.info(f"Risk ogohlantirish qo'shildi: {rule.name}")
        return rule_id
    
    def add_calendar_alert(self, event_name: str, importance: str = "medium",
                         channel: str = "telegram", name: str = None) -> str:
        """Taqvim ogohlantirish qo'shish"""
        rule_id = str(uuid.uuid4())
        
        rule = AlertRule(
            id=rule_id,
            name=name or f"Calendar: {event_name}",
            alert_type=AlertType.CALENDAR,
            symbol="CALENDAR",
            condition="event_upcoming",
            threshold=1.0,
            channel=NotificationChannel(channel.lower()),
            metadata={"event_name": event_name, "importance": importance}
        )
        
        self.alert_rules[rule_id] = rule
        self._save_rule_to_db(rule)
        
        self.logger.info(f"Taqvim ogohlantirish qo'shildi: {rule.name}")
        return rule_id
    
    # ===== WATCHLISTS =====
    
    def create_watchlist(self, name: str, symbols: List[str]) -> str:
        """Watchlist yaratish"""
        watchlist_id = str(uuid.uuid4())
        
        self.watchlists[watchlist_id] = {
            "id": watchlist_id,
            "name": name,
            "symbols": symbols,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Database ga saqlash
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO watchlists (id, name, symbols) VALUES (?, ?, ?)",
                (watchlist_id, name, json.dumps(symbols))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Watchlist saqlash xatoligi: {e}")
        
        self.logger.info(f"Watchlist yaratildi: {name}")
        return watchlist_id
    
    def add_to_watchlist(self, watchlist_id: str, symbol: str) -> bool:
        """Watchlist ga symbol qo'shish"""
        if watchlist_id not in self.watchlists:
            return False
        
        if symbol not in self.watchlists[watchlist_id]["symbols"]:
            self.watchlists[watchlist_id]["symbols"].append(symbol)
            self.watchlists[watchlist_id]["updated_at"] = datetime.now()
        
        return True
    
    def get_watchlists(self) -> List[Dict[str, Any]]:
        """Barcha watchlist larni olish"""
        return list(self.watchlists.values())
    
    # ===== NOTIFICATIONS =====
    
    async def send_notification(self, alert: Alert) -> bool:
        """Xabar yuborish"""
        try:
            provider_name = alert.channel.value
            if provider_name not in self.notification_providers:
                self.logger.error(f"Provider topilmadi: {provider_name}")
                return False
            
            provider = self.notification_providers[provider_name]
            success = await provider.send(alert, alert.message)
            
            if success:
                self.logger.info(f"Xabar yuborildi: {alert.id}")
            else:
                self.logger.error(f"Xabar yuborilmadi: {alert.id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Xabar yuborish xatoligi: {e}")
            return False
    
    # ===== MONITORING =====
    
    def start_monitoring(self) -> None:
        """Monitoring ni boshlash"""
        if self.monitoring_active:
            self.logger.warning("Monitoring allaqachon ishga tushgan")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Monitoring boshlandi")
    
    def stop_monitoring(self) -> None:
        """Monitoring ni to'xtatish"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        self.logger.info("Monitoring to'xtatildi")
    
    def _monitoring_loop(self) -> None:
        """Asosiy monitoring tsikli"""
        while self.monitoring_active:
            try:
                self._check_all_rules()
                time.sleep(self.config.get('monitoring', {}).get('interval', 60))
            except Exception as e:
                self.logger.error(f"Monitoring xatoligi: {e}")
                time.sleep(10)  # Xato bo'lsa 10 soniya kuting
    
    def _check_all_rules(self) -> None:
        """Barcha qoidalarni tekshirish"""
        for rule_id, rule in list(self.alert_rules.items()):
            if not rule.is_active:
                continue
            
            try:
                alert = self._check_rule(rule)
                if alert:
                    self._trigger_alert(alert)
            except Exception as e:
                self.logger.error(f"Rule tekshirish xatoligi {rule_id}: {e}")
    
    def _check_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Bitta qoidani tekshirish"""
        # Mock data - real vaziyatda API dan olish kerak
        current_price = self._get_mock_price(rule.symbol)
        
        triggered = False
        message = ""
        severity = "medium"
        
        if rule.alert_type == AlertType.PRICE:
            triggered, message, severity = self._check_price_rule(rule, current_price)
        
        elif rule.alert_type == AlertType.TECHNICAL:
            triggered, message, severity = self._check_technical_rule(rule, current_price)
        
        elif rule.alert_type == AlertType.VOLUME:
            current_volume = self._get_mock_volume(rule.symbol)
            triggered, message, severity = self._check_volume_rule(rule, current_volume)
        
        elif rule.alert_type == AlertType.NEWS:
            news_list = self.news_analyzer.get_market_news()
            triggered, message, severity = self._check_news_rule(rule, news_list)
        
        if triggered:
            alert = Alert(
                id=str(uuid.uuid4()),
                rule_id=rule.id,
                alert_type=rule.alert_type,
                symbol=rule.symbol,
                message=message,
                severity=severity,
                channel=rule.channel,
                status=AlertStatus.TRIGGERED,
                triggered_at=datetime.now()
            )
            return alert
        
        return None
    
    def _check_price_rule(self, rule: AlertRule, current_price: float) -> tuple:
        """Narx qoidasini tekshirish"""
        condition = rule.condition.lower()
        
        if condition == "above" and current_price > rule.threshold:
            return True, f"Narx {rule.threshold} dan yuqori: {current_price}", "high"
        elif condition == "below" and current_price < rule.threshold:
            return True, f"Narx {rule.threshold} dan past: {current_price}", "high"
        elif condition == "equal" and abs(current_price - rule.threshold) < 0.01:
            return True, f"Narx {rule.threshold} ga teng: {current_price}", "medium"
        
        return False, "", "low"
    
    def _check_technical_rule(self, rule: AlertRule, current_price: float) -> tuple:
        """Texnik indikator qoidasini tekshirish"""
        # Mock historical prices
        historical_prices = [current_price * (0.99 + i * 0.002) for i in range(50)]
        
        indicator = rule.metadata.get("indicator", "")
        
        if indicator.upper() == "RSI":
            rsi = self.technical_analyzer.calculate_rsi(historical_prices)
            if rule.condition == "rsi_oversold" and rsi < rule.threshold:
                return True, f"RSI {rule.threshold} dan past: {rsi:.2f}", "medium"
            elif rule.condition == "rsi_overbought" and rsi > rule.threshold:
                return True, f"RSI {rule.threshold} dan yuqori: {rsi:.2f}", "medium"
        
        elif indicator.upper() == "MA20":
            ma20 = self.technical_analyzer.calculate_moving_average(historical_prices, 20)
            if rule.condition == "price_above_ma" and current_price > ma20:
                return True, f"Narx MA20 dan yuqori: {current_price:.2f} vs {ma20:.2f}", "medium"
            elif rule.condition == "price_below_ma" and current_price < ma20:
                return True, f"Narx MA20 dan past: {current_price:.2f} vs {ma20:.2f}", "medium"
        
        return False, "", "low"
    
    def _check_volume_rule(self, rule: AlertRule, current_volume: int) -> tuple:
        """Volume qoidasini tekshirish"""
        # Mock average volume
        avg_volume = current_volume // 2
        
        if current_volume > avg_volume * rule.threshold:
            return True, f"Volume g'ayrioddiy yuqori: {current_volume} (avg: {avg_volume})", "medium"
        
        return False, "", "low"
    
    def _check_news_rule(self, rule: AlertRule, news_list: List[Dict]) -> tuple:
        """Yangiliklar qoidasini tekshirish"""
        keywords = rule.metadata.get("keywords", [])
        
        for news in news_list:
            title = news.get("title", "").lower()
            description = news.get("description", "").lower()
            
            matched_keywords = [kw for kw in keywords if kw.lower() in title or kw.lower() in description]
            
            if len(matched_keywords) >= rule.threshold:
                sentiment = rule.metadata.get("sentiment", "any")
                news_sentiment = news.get("sentiment", "neutral")
                
                if sentiment == "any" or sentiment == news_sentiment:
                    return True, f"Yangilik: {news.get('title', '')}", "high"
        
        return False, "", "low"
    
    def _trigger_alert(self, alert: Alert) -> None:
        """Ogohlantirishni triggerman"""
        # Alert history ga qo'shish
        self.alert_history.append(alert)
        
        # Database ga saqlash
        self._save_alert_to_db(alert)
        
        # Xabar yuborish
        if alert.channel.value in self.notification_providers:
            asyncio.create_task(self.send_notification(alert))
        
        self.logger.info(f"Ogohlantirish triggerman: {alert.message}")
    
    def _get_mock_price(self, symbol: str) -> float:
        """Mock narx olish (real vaziyatda API dan olish kerak)"""
        import random
        base_prices = {
            "BTC": 45000,
            "ETH": 3000,
            "AAPL": 150,
            "GOOGL": 2800,
            "MSFT": 350,
            "TSLA": 250,
            "AMZN": 3200,
            "NVDA": 500
        }
        
        base_price = base_prices.get(symbol, 100.0)
        # 1% dan 5% gacha tasodifiy o'zgarish
        change = random.uniform(-0.05, 0.05)
        return base_price * (1 + change)
    
    def _get_mock_volume(self, symbol: str) -> int:
        """Mock volume olish"""
        import random
        return random.randint(100000, 1000000)
    
    # ===== DATABASE OPERATIONS =====
    
    def _save_rule_to_db(self, rule: AlertRule) -> None:
        """Qoidani database ga saqlash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO alert_rules 
                   (id, name, alert_type, symbol, condition, threshold, 
                    channel, is_active, created_at, expires_at, metadata) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rule.id, rule.name, rule.alert_type.value, rule.symbol,
                    rule.condition, rule.threshold, rule.channel.value,
                    rule.is_active, rule.created_at, rule.expires_at,
                    json.dumps(rule.metadata)
                )
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Rule saqlash xatoligi: {e}")
    
    def _save_alert_to_db(self, alert: Alert) -> None:
        """Ogohlantirishni database ga saqlash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO alerts 
                   (id, rule_id, alert_type, symbol, message, severity, 
                    channel, status, triggered_at, acknowledged, metadata) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    alert.id, alert.rule_id, alert.alert_type.value, alert.symbol,
                    alert.message, alert.severity, alert.channel.value,
                    alert.status.value, alert.triggered_at, alert.acknowledged,
                    json.dumps(alert.metadata)
                )
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Alert saqlash xatoligi: {e}")
    
    # ===== ALERT MANAGEMENT =====
    
    def get_active_rules(self) -> List[AlertRule]:
        """Faol qoidalarni olish"""
        return [rule for rule in self.alert_rules.values() if rule.is_active]
    
    def pause_rule(self, rule_id: str) -> bool:
        """Qoidani to'xtatish"""
        if rule_id in self.alert_rules:
            self.alert_rules[rule_id].is_active = False
            self._save_rule_to_db(self.alert_rules[rule_id])
            self.logger.info(f"Rule to'xtatildi: {rule_id}")
            return True
        return False
    
    def resume_rule(self, rule_id: str) -> bool:
        """Qoidani davom ettirish"""
        if rule_id in self.alert_rules:
            self.alert_rules[rule_id].is_active = True
            self._save_rule_to_db(self.alert_rules[rule_id])
            self.logger.info(f"Rule davom ettirildi: {rule_id}")
            return True
        return False
    
    def delete_rule(self, rule_id: str) -> bool:
        """Qoidani o'chirish"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            
            # Database dan ham o'chirish
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM alert_rules WHERE id = ?", (rule_id,))
                conn.commit()
                conn.close()
            except Exception as e:
                self.logger.error(f"Rule o'chirish xatoligi: {e}")
            
            self.logger.info(f"Rule o'chirildi: {rule_id}")
            return True
        return False
    
    def get_alert_history(self, limit: int = 100, symbol: str = None) -> List[Alert]:
        """Ogohlantirish tarixini olish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute(
                    "SELECT * FROM alerts WHERE symbol = ? ORDER BY triggered_at DESC LIMIT ?",
                    (symbol, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM alerts ORDER BY triggered_at DESC LIMIT ?",
                    (limit,)
                )
            
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alert = Alert(
                    id=row[0],
                    rule_id=row[1],
                    alert_type=AlertType(row[2]),
                    symbol=row[3],
                    message=row[4],
                    severity=row[5],
                    channel=NotificationChannel(row[6]),
                    status=AlertStatus(row[7]),
                    triggered_at=datetime.fromisoformat(row[8]),
                    acknowledged=bool(row[9]),
                    metadata=json.loads(row[10]) if row[10] else {}
                )
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Alert history olish xatoligi: {e}")
            return []
    
    # ===== PERFORMANCE TRACKING =====
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Ogohlantirish statistikasi"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Umumiy statistika
            cursor.execute("SELECT COUNT(*) FROM alerts")
            total_alerts = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT rule_id) FROM alerts")
            triggered_rules = cursor.fetchone()[0]
            
            # Bugungi ogohlantirishlar
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM alerts WHERE DATE(triggered_at) = ?", (today,))
            today_alerts = cursor.fetchone()[0]
            
            # Alert type bo'yicha
            cursor.execute("""
                SELECT alert_type, COUNT(*) 
                FROM alerts 
                GROUP BY alert_type
            """)
            type_stats = dict(cursor.fetchall())
            
            # Channel bo'yicha
            cursor.execute("""
                SELECT channel, COUNT(*) 
                FROM alerts 
                GROUP BY channel
            """)
            channel_stats = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "total_alerts": total_alerts,
                "triggered_rules": triggered_rules,
                "today_alerts": today_alerts,
                "active_rules": len(self.get_active_rules()),
                "type_distribution": type_stats,
                "channel_distribution": channel_stats
            }
            
        except Exception as e:
            self.logger.error(f"Statistika olish xatoligi: {e}")
            return {}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Performance metrikalar"""
        stats = self.get_alert_statistics()
        
        # Performance koeffitsiyenti
        active_rules = stats.get("active_rules", 0)
        total_alerts = stats.get("total_alerts", 0)
        
        if active_rules > 0:
            alert_frequency = total_alerts / active_rules if active_rules > 0 else 0
        else:
            alert_frequency = 0
        
        return {
            "alert_frequency_per_rule": alert_frequency,
            "system_uptime": time.time(),
            "monitoring_active": self.monitoring_active,
            "total_rules": len(self.alert_rules),
            "total_providers": len(self.notification_providers)
        }
    
    # ===== CONFIGURATION =====
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Konfiguratsiyani yangilash"""
        self.config.update(new_config)
        self._save_config(self.config)
        
        # Notification provider larni qayta boslang'ich qilish
        self.notification_providers = self._init_notification_providers()
        
        self.logger.info("Konfiguratsiya yangilandi")
    
    def get_config(self) -> Dict[str, Any]:
        """Joriy konfiguratsiyani olish"""
        return self.config.copy()


# ===== DEMO VA TEST =====
def demo_smart_alerts():
    """Smart Alerts demo"""
    print("=" * 60)
    print("Smart Alert System Demo")
    print("=" * 60)
    
    # Smart Alert System yaratish
    alerts = SmartAlertSystem()
    
    # 1. Narx ogohlantirishlar
    print("\n1. Narx ogohlantirishlar qo'shish...")
    btc_alert = alerts.add_price_alert("BTC", "above", 45000, "telegram", "BTC 45K dan yuqori")
    aapl_alert = alerts.add_price_alert("AAPL", "below", 140, "email", "AAPL 140$ dan past")
    
    # 2. Texnik indikator ogohlantirishlar
    print("\n2. Texnik indikator ogohlantirishlar qo'shish...")
    btc_rsi = alerts.add_technical_alert("BTC", "RSI", "rsi_overbought", 70, "telegram", "BTC RSI overbought")
    eth_ma = alerts.add_technical_alert("ETH", "MA20", "price_above_ma", 0, "email", "ETH MA20 dan yuqori")
    
    # 3. Volume ogohlantirishlar
    print("\n3. Volume ogohlantirishlar qo'shish...")
    tsla_volume = alerts.add_volume_alert("TSLA", 2.5, "push", "TSLA unusual volume")
    
    # 4. Yangiliklar ogohlantirishlar
    print("\n4. Yangiliklar ogohlantirishlar qo'shish...")
    news_alert = alerts.add_news_alert(["bitcoin", "fed", "crisis"], "negative", "telegram")
    
    # 5. Portfolio ogohlantirishlar
    print("\n5. Portfolio ogohlantirishlar qo'shish...")
    portfolio_alert = alerts.add_portfolio_alert("My Portfolio", 5.0, "email")
    
    # 6. Risk ogohlantirishlar
    print("\n6. Risk ogohlantirishlar qo'shish...")
    risk_alert = alerts.add_risk_alert("BTC", 0.8, "push")
    
    # 7. Taqvim ogohlantirishlar
    print("\n7. Taqvim ogohlantirishlar q'o'shish...")
    calendar_alert = alerts.add_calendar_alert("Fed Meeting", "high", "telegram")
    
    # Watchlist yaratish
    print("\n8. Watchlist yaratish...")
    tech_watchlist = alerts.create_watchlist("Tech Stocks", ["AAPL", "GOOGL", "MSFT", "NVDA"])
    crypto_watchlist = alerts.create_watchlist("Crypto", ["BTC", "ETH", "ADA"])
    
    # Statistika
    print("\n9. Statistika...")
    stats = alerts.get_alert_statistics()
    print(f"Umumiy ogohlantirishlar: {stats.get('total_alerts', 0)}")
    print(f"Faol qoidalar: {stats.get('active_rules', 0)}")
    print(f"Today ogohlantirishlar: {stats.get('today_alerts', 0)}")
    
    print(f"Type distribution: {stats.get('type_distribution', {})}")
    print(f"Channel distribution: {stats.get('channel_distribution', {})}")
    
    # Performance metrikalar
    performance = alerts.get_performance_metrics()
    print(f"\nPerformance metrikalar: {performance}")
    
    # Monitoring boshlang'ich qilish (demo uchun)
    print("\n10. Monitoring boshlang'ich qilish...")
    alerts.start_monitoring()
    
    # 30 soniya kutish va monitoring ni to'xtatish
    print("Monitoring 30 soniya davom etadi...")
    time.sleep(30)
    alerts.stop_monitoring()
    
    print("\nDemo tugadi!")


if __name__ == "__main__":
    demo_smart_alerts()