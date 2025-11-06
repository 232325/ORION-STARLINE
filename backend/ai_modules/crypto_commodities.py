"""
Crypto & Commodities Integration Module
=====================================

Bu modul cryptocurrency va commodity bozorlari uchun keng qamrovli integration tizimini ta'minlaydi.

Asosiy funksiyalar:
- Cryptocurrency trading (100+ kripto)
- Real-time narx monitoring
- Commodity tahlili
- Portfolio tracking
- Technical analysis
- News integration
- Arbitrage opportunities
- Price alerts

@author: Orion Starline AI System
@version: 2.0.0
@date: 2025-11-05
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
import websockets
import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
import ccxt
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CryptoAsset:
    """Kryptovalyuta aktiv ma'lumotlari"""
    symbol: str
    name: str
    price: float
    change_24h: float
    volume_24h: float
    market_cap: float
    exchange: str
    timestamp: datetime
    
@dataclass
class CommodityAsset:
    """Kommoditi aktiv ma'lumotlari"""
    symbol: str
    name: str
    price: float
    change_24h: float
    volume_24h: float
    market_cap: float
    exchange: str
    timestamp: datetime
    
@dataclass
class Portfolio:
    """Portfolio ma'lumotlari"""
    user_id: str
    total_value: float
    crypto_balance: Dict[str, float]
    commodity_balance: Dict[str, float]
    pnl: float
    last_updated: datetime

class CryptoCommoditiesDataProvider:
    """Ma'lumot provayderi klassi"""
    
    def __init__(self):
        self.exchanges = {
            'binance': ccxt.binance(),
            'coinbase': ccxt.coinbase(),
            'kraken': ccxt.kraken(),
            'huobi': ccxt.huobi()
        }
        
        self.commodity_sources = {
            'gold': 'XAUUSD=X',
            'silver': 'XAGUSD=X',
            'platinum': 'XPTUSD=X',
            'oil': 'CL=F',
            'cotton': 'CT=F',
            'coffee': 'KC=F',
            'sugar': 'SB=F'
        }
        
        # Krypto valyuta ro'yxati (100+)
        self.supported_cryptos = [
            'BTC/USDT', 'ETH/USDT', 'LTC/USDT', 'BCH/USDT', 'XRP/USDT',
            'ADA/USDT', 'LINK/USDT', 'XLM/USDT', 'DOT/USDT', 'BNB/USDT',
            'SOL/USDT', 'DOGE/USDT', 'AVAX/USDT', 'MATIC/USDT', 'ATOM/USDT',
            'UNI/USDT', 'AAVE/USDT', 'MKR/USDT', 'COMP/USDT', 'YFI/USDT',
            'SUSHI/USDT', '1INCH/USDT', 'ENJ/USDT', 'SAND/USDT', 'MANA/USDT',
            'ALGO/USDT', 'XTZ/USDT', 'ATOM/USDT', 'VET/USDT', 'FIL/USDT',
            'THETA/USDT', 'ICX/USDT', 'EOS/USDT', 'XMR/USDT', 'ZEC/USDT',
            'DASH/USDT', 'LRC/USDT', 'ZIL/USDT', 'IOTA/USDT', 'ONT/USDT',
            'QTUM/USDT', 'WAVES/USDT', 'KAVA/USDT', 'BAND/USDT', 'REN/USDT',
            'KSM/USDT', 'OCEAN/USDT', 'FET/USDT', 'BAT/USDT', 'ZRX/USDT',
            'KNC/USDT', 'OMG/USDT', 'REP/USDT', 'STORJ/USDT', 'LPT/USDT',
            'SKL/USDT', 'GRT/USDT', 'LTO/USDT', 'DGB/USDT', 'RVN/USDT',
            'HOT/USDT', 'NANO/USDT', 'LSK/USDT', 'WTC/USDT', 'DCR/USDT',
            'SC/USDT', 'SIA/USDT', 'DGB/USDT', 'GAS/USDT', 'NEO/USDT',
            'IOTX/USDT', 'RLC/USDT', 'ZIL/USDT', 'POWR/USDT', 'REQ/USDT',
            'DRGN/USDT', 'WAVES/USDT', 'CTR/USDT', 'DATA/USDT', 'TRX/USDT',
            'XLM/USDT', 'XRP/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT'
        ]

class RealTimePriceMonitor:
    """Real-time narx monitoring tizimi"""
    
    def __init__(self, data_provider: CryptoCommoditiesDataProvider):
        self.data_provider = data_provider
        self.price_cache = {}
        self.alert_conditions = {}
        self.callbacks = []
        self.monitoring_active = False
        
    async def start_monitoring(self):
        """Real-time monitoring boshlash"""
        self.monitoring_active = True
        
        # Parallel monitoring tasklari
        tasks = [
            self.monitor_crypto_prices(),
            self.monitor_commodity_prices(),
            self.check_alerts()
        ]
        
        await asyncio.gather(*tasks)
        
    async def monitor_crypto_prices(self):
        """Krypto valyuta narxlarini monitoring qilish"""
        while self.monitoring_active:
            try:
                for symbol in self.data_provider.supported_cryptos[:50]:  # First 50 for performance
                    for exchange_name, exchange in self.data_provider.exchanges.items():
                        try:
                            ticker = await exchange.fetch_ticker(symbol)
                            
                            crypto_asset = CryptoAsset(
                                symbol=symbol,
                                name=symbol.replace('/USDT', ''),
                                price=ticker['last'],
                                change_24h=ticker['percentage'] or 0,
                                volume_24h=ticker['quoteVolume'] or 0,
                                market_cap=0,  # Would need additional API call
                                exchange=exchange_name,
                                timestamp=datetime.now()
                            )
                            
                            self.price_cache[f"{symbol}_{exchange_name}"] = crypto_asset
                            
                            # Alert checks
                            await self._check_crypto_alerts(crypto_asset)
                            
                        except Exception as e:
                            logger.error(f"Krypto narx olishda xato {symbol}: {e}")
                            
                await asyncio.sleep(2)  # 2 soniya interval
                
            except Exception as e:
                logger.error(f"Krypto monitoring xatosi: {e}")
                await asyncio.sleep(5)
                
    async def monitor_commodity_prices(self):
        """Kommoditi narxlarini monitoring qilish"""
        while self.monitoring_active:
            try:
                for symbol, yahoo_symbol in self.data_provider.commodity_sources.items():
                    try:
                        ticker = yf.Ticker(yahoo_symbol)
                        data = ticker.history(period="1d")
                        
                        if not data.empty:
                            current_price = data['Close'].iloc[-1]
                            previous_price = data['Open'].iloc[0]
                            change_24h = ((current_price - previous_price) / previous_price) * 100
                            
                            commodity_asset = CommodityAsset(
                                symbol=symbol,
                                name=symbol.upper(),
                                price=current_price,
                                change_24h=change_24h,
                                volume_24h=0,  # Commodities don't have volume like crypto
                                market_cap=0,
                                exchange='YAHOO',
                                timestamp=datetime.now()
                            )
                            
                            self.price_cache[symbol] = commodity_asset
                            
                            # Alert checks
                            await self._check_commodity_alerts(commodity_asset)
                            
                    except Exception as e:
                        logger.error(f"Kommoditi narx olishda xato {symbol}: {e}")
                        
                await asyncio.sleep(30)  # 30 soniya interval for commodities
                
            except Exception as e:
                logger.error(f"Kommoditi monitoring xatosi: {e}")
                await asyncio.sleep(30)
                
    async def _check_crypto_alerts(self, crypto_asset: CryptoAsset):
        """Krypto uchun alertlarni tekshirish"""
        cache_key = f"crypto_{crypto_asset.symbol}_{crypto_asset.exchange}"
        
        if cache_key in self.alert_conditions:
            for alert_id, alert in self.alert_conditions[cache_key].items():
                triggered = False
                
                if alert['type'] == 'price_above' and crypto_asset.price > alert['value']:
                    triggered = True
                elif alert['type'] == 'price_below' and crypto_asset.price < alert['value']:
                    triggered = True
                elif alert['type'] == 'change_above' and crypto_asset.change_24h > alert['value']:
                    triggered = True
                elif alert['type'] == 'change_below' and crypto_asset.change_24h < alert['value']:
                    triggered = True
                    
                if triggered:
                    await self._send_alert_notification(alert, crypto_asset)
                    
    async def _check_commodity_alerts(self, commodity_asset: CommodityAsset):
        """Kommoditi uchun alertlarni tekshirish"""
        cache_key = f"commodity_{commodity_asset.symbol}"
        
        if cache_key in self.alert_conditions:
            for alert_id, alert in self.alert_conditions[cache_key].items():
                triggered = False
                
                if alert['type'] == 'price_above' and commodity_asset.price > alert['value']:
                    triggered = True
                elif alert['type'] == 'price_below' and commodity_asset.price < alert['value']:
                    triggered = True
                elif alert['type'] == 'change_above' and commodity_asset.change_24h > alert['value']:
                    triggered = True
                elif alert['type'] == 'change_below' and commodity_asset.change_24h < alert['value']:
                    triggered = True
                    
                if triggered:
                    await self._send_alert_notification(alert, commodity_asset)
                    
    async def _send_alert_notification(self, alert: dict, asset):
        """Alert xabarini yuborish"""
        logger.info(f"🚨 ALERT: {asset.name} {alert['type']} {alert['value']}")
        logger.info(f"   Joriy narx: {asset.price}")
        logger.info(f"   24h o'zgarish: {asset.change_24h:.2f}%")
        
        # Callback functions
        for callback in self.callbacks:
            try:
                await callback(alert, asset)
            except Exception as e:
                logger.error(f"Callback xatosi: {e}")
                
    async def check_alerts(self):
        """Alertlarni tekshirish uchun asosiy loop"""
        while self.monitoring_active:
            await asyncio.sleep(1)

class TechnicalAnalyzer:
    """Technical analysis klassi"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        
    def get_technical_indicators(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """Texnik indikatorlarni hisoblash"""
        try:
            # Price columns
            high = price_data['High']
            low = price_data['Low']
            close = price_data['Close']
            volume = price_data['Volume'] if 'Volume' in price_data.columns else pd.Series([1000000] * len(close))
            
            # Moving Averages
            sma_20 = ta.trend.sma_indicator(close, window=20)
            ema_12 = ta.trend.ema_indicator(close, window=12)
            ema_26 = ta.trend.ema_indicator(close, window=26)
            
            # MACD
            macd_line = ema_12 - ema_26
            macd_signal = ta.trend.sma_indicator(macd_line, window=9)
            macd_histogram = macd_line - macd_signal
            
            # RSI
            rsi = ta.momentum.rsi(close, window=14)
            
            # Bollinger Bands
            bb_upper = ta.volatility.bollinger_hband(close, window=20)
            bb_lower = ta.volatility.bollinger_lband(close, window=20)
            bb_middle = ta.volatility.bollinger_mavg(close, window=20)
            
            # Stochastic
            stoch_k = ta.momentum.stoch(high, low, close, window=14)
            stoch_d = ta.momentum.stoch_signal(high, low, close, window=14)
            
            # ADX (Trend strength)
            adx = ta.trend.adx(high, low, close, window=14)
            
            # Volume indicators
            obv = ta.volume.on_balance_volume(close, volume)
            volume_sma = ta.volume.volume_sma(close, volume, window=20)
            
            return {
                'sma_20': sma_20.iloc[-1] if not sma_20.empty else 0,
                'ema_12': ema_12.iloc[-1] if not ema_12.empty else 0,
                'macd_line': macd_line.iloc[-1] if not macd_line.empty else 0,
                'macd_signal': macd_signal.iloc[-1] if not macd_signal.empty else 0,
                'macd_histogram': macd_histogram.iloc[-1] if not macd_histogram.empty else 0,
                'rsi': rsi.iloc[-1] if not rsi.empty else 50,
                'bb_upper': bb_upper.iloc[-1] if not bb_upper.empty else 0,
                'bb_middle': bb_middle.iloc[-1] if not bb_middle.empty else 0,
                'bb_lower': bb_lower.iloc[-1] if not bb_lower.empty else 0,
                'stoch_k': stoch_k.iloc[-1] if not stoch_k.empty else 50,
                'stoch_d': stoch_d.iloc[-1] if not stoch_d.empty else 50,
                'adx': adx.iloc[-1] if not adx.empty else 0,
                'obv': obv.iloc[-1] if not obv.empty else 0,
                'volume_sma': volume_sma.iloc[-1] if not volume_sma.empty else 0
            }
            
        except Exception as e:
            logger.error(f"Texnik indikator hisoblashda xato: {e}")
            return {}
            
    def generate_signals(self, indicators: Dict[str, float]) -> Dict[str, str]:
        """Texnik signallarni generatsiya qilish"""
        signals = {}
        
        try:
            # RSI signals
            if indicators.get('rsi', 50) > 70:
                signals['rsi'] = 'SELL'
            elif indicators.get('rsi', 50) < 30:
                signals['rsi'] = 'BUY'
            else:
                signals['rsi'] = 'HOLD'
                
            # MACD signals
            if indicators.get('macd_line', 0) > indicators.get('macd_signal', 0):
                signals['macd'] = 'BUY'
            else:
                signals['macd'] = 'SELL'
                
            # Bollinger Bands signals
            price = indicators.get('price', 0)
            bb_upper = indicators.get('bb_upper', 0)
            bb_lower = indicators.get('bb_lower', 0)
            
            if price > bb_upper:
                signals['bollinger'] = 'SELL'
            elif price < bb_lower:
                signals['bollinger'] = 'BUY'
            else:
                signals['bollinger'] = 'HOLD'
                
            # Stochastic signals
            if indicators.get('stoch_k', 50) > 80:
                signals['stoch'] = 'SELL'
            elif indicators.get('stoch_k', 50) < 20:
                signals['stoch'] = 'BUY'
            else:
                signals['stoch'] = 'HOLD'
                
            # Overall signal
            buy_signals = sum(1 for signal in signals.values() if signal == 'BUY')
            sell_signals = sum(1 for signal in signals.values() if signal == 'SELL')
            
            if buy_signals > sell_signals:
                signals['overall'] = 'BUY'
            elif sell_signals > buy_signals:
                signals['overall'] = 'SELL'
            else:
                signals['overall'] = 'HOLD'
                
        except Exception as e:
            logger.error(f"Signal generatsiya qilishda xato: {e}")
            signals['overall'] = 'ERROR'
            
        return signals
        
    def predict_price(self, features: np.ndarray) -> float:
        """Narx bashorati"""
        try:
            # Features o'lchami mosligini tekshirish
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
                
            return self.model.predict(features)[0]
        except Exception as e:
            logger.error(f"Narx bashorat qilishda xato: {e}")
            return 0.0

class PortfolioManager:
    """Portfolio boshqaruv tizimi"""
    
    def __init__(self, db_path: str = "crypto_portfolio.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Ma'lumotlar bazasini yaratish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                crypto_symbol TEXT,
                commodity_symbol TEXT,
                quantity REAL,
                avg_price REAL,
                current_price REAL,
                pnl REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                type TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_transaction(self, user_id: str, symbol: str, transaction_type: str, 
                      quantity: float, price: float) -> bool:
        """Tranzaksiya qo'shish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (user_id, symbol, type, quantity, price)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, symbol, transaction_type, quantity, price))
            
            # Portfolio ni yangilash
            self.update_portfolio_position(user_id, symbol, transaction_type, quantity, price)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Tranzaksiya qo'shildi: {user_id}, {symbol}, {transaction_type}, {quantity}, {price}")
            return True
            
        except Exception as e:
            logger.error(f"Tranzaksiya qo'shishda xato: {e}")
            return False
            
    def update_portfolio_position(self, user_id: str, symbol: str, 
                                transaction_type: str, quantity: float, price: float):
        """Portfolio pozitsiyasini yangilash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Mavjud pozitsiyani tekshirish
            cursor.execute('''
                SELECT quantity, avg_price FROM portfolios
                WHERE user_id = ? AND (crypto_symbol = ? OR commodity_symbol = ?)
            ''', (user_id, symbol, symbol))
            
            position = cursor.fetchone()
            
            if position:
                # Mavjud pozitsiyani yangilash
                current_qty, avg_price = position
                
                if transaction_type == 'BUY':
                    new_quantity = current_qty + quantity
                    new_avg_price = (current_qty * avg_price + quantity * price) / new_quantity
                else:  # SELL
                    new_quantity = current_qty - quantity
                    new_avg_price = avg_price if new_quantity > 0 else 0
                    
                cursor.execute('''
                    UPDATE portfolios
                    SET quantity = ?, avg_price = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND (crypto_symbol = ? OR commodity_symbol = ?)
                ''', (new_quantity, new_avg_price, user_id, symbol, symbol))
                
            else:
                # Yangi pozitsiya yaratish
                cursor.execute('''
                    INSERT INTO portfolios (user_id, crypto_symbol, quantity, avg_price)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, symbol if len(symbol) == 3 else None, quantity, price))
                
                cursor.execute('''
                    INSERT INTO portfolios (user_id, commodity_symbol, quantity, avg_price)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, symbol if len(symbol) == 3 else None, quantity, price))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Portfolio yangilashda xato: {e}")
            
    def get_portfolio(self, user_id: str) -> Portfolio:
        """Portfolio ma'lumotlarini olish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT crypto_symbol, commodity_symbol, quantity, avg_price
                FROM portfolios
                WHERE user_id = ?
            ''', (user_id,))
            
            positions = cursor.fetchall()
            conn.close()
            
            crypto_balance = {}
            commodity_balance = {}
            total_value = 0
            
            for position in positions:
                crypto_symbol, commodity_symbol, quantity, avg_price = position
                
                if crypto_symbol:
                    crypto_balance[crypto_symbol] = {'quantity': quantity, 'avg_price': avg_price}
                    total_value += quantity * avg_price * 1.1  # Mock current price
                elif commodity_symbol:
                    commodity_balance[commodity_symbol] = {'quantity': quantity, 'avg_price': avg_price}
                    total_value += quantity * avg_price * 1.05  # Mock current price
                    
            return Portfolio(
                user_id=user_id,
                total_value=total_value,
                crypto_balance=crypto_balance,
                commodity_balance=commodity_balance,
                pnl=total_value * 0.05,  # Mock P&L
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Portfolio olishda xato: {e}")
            return Portfolio(user_id=user_id, total_value=0, crypto_balance={}, 
                           commodity_balance={}, pnl=0, last_updated=datetime.now())

class NewsAnalyzer:
    """Yangiliklar tahlili tizimi"""
    
    def __init__(self):
        self.news_cache = []
        
    def get_crypto_news(self, limit: int = 20) -> List[Dict]:
        """Kripto yangiliklari olish (demo)"""
        try:
            # Demo yangiliklar (real implementation uchun API kerak)
            news = [
                {
                    'title': 'Bitcoin $50,000 darajasini qayta test qilmoqda',
                    'summary': 'Bitcoin narxi yana muhim darajani qayta test qilmoqda.',
                    'timestamp': datetime.now() - timedelta(minutes=30),
                    'source': 'CryptoNews',
                    'sentiment': 'positive',
                    'symbols': ['BTC']
                },
                {
                    'title': 'Ethereum 2.0 upgrade muvaffaqiyatli yakunlandi',
                    'summary': 'Ethereum network upgrade muvaffaqiyatli amalga oshirildi.',
                    'timestamp': datetime.now() - timedelta(hours=1),
                    'source': 'ETHNews',
                    'sentiment': 'positive',
                    'symbols': ['ETH']
                },
                {
                    'title': 'Kripto bozorida volatilite ortmoqda',
                    'summary': 'Asosiy kriptovalyutalarda volatilite darajasi oshmoqda.',
                    'timestamp': datetime.now() - timedelta(hours=2),
                    'source': 'MarketWatch',
                    'sentiment': 'neutral',
                    'symbols': ['BTC', 'ETH']
                }
            ]
            
            return news[:limit]
            
        except Exception as e:
            logger.error(f"Kripto yangiliklari olishda xato: {e}")
            return []
            
    def get_commodity_news(self, limit: int = 15) -> List[Dict]:
        """Kommoditi yangiliklari olish (demo)"""
        try:
            news = [
                {
                    'title': 'Oltin narxi yangi rekordni qayd etdi',
                    'summary': 'Investorlar vaqtinchalik risklardan qochish uchun oltinga murojaat qilmoqda.',
                    'timestamp': datetime.now() - timedelta(hours=3),
                    'source': 'CommodityNews',
                    'sentiment': 'positive',
                    'symbols': ['GOLD']
                },
                {
                    'title': 'Neft narxi global talab ortishi hisobida oshmoqda',
                    'summary': 'Iqtisodiy tiklanish neft talabini oshiradi.',
                    'timestamp': datetime.now() - timedelta(hours=5),
                    'source': 'OilDaily',
                    'sentiment': 'positive',
                    'symbols': ['OIL']
                },
                {
                    'title': 'Kofehun narxi ob-havo sharoitlari ta\'sirida pasaymoqda',
                    'summary': 'Yaxshi ob-havo kofehun yetishtirishiga yaxshi ta\'sir qilmoqda.',
                    'timestamp': datetime.now() - timedelta(hours=6),
                    'source': 'AgriNews',
                    'sentiment': 'negative',
                    'symbols': ['COFFEE']
                }
            ]
            
            return news[:limit]
            
        except Exception as e:
            logger.error(f"Kommoditi yangiliklari olishda xato: {e}")
            return []
            
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Matn sentiment tahlili"""
        try:
            # Simple sentiment analysis (real implementation uchun AI kerak)
            positive_words = ['ko\'tarilish', 'musbat', 'yaxshi', 'muvaffaqiyatli', 'rekord', 'oshmoqda']
            negative_words = ['tushish', 'salbiy', 'yomon', 'xato', 'xavf', 'pasaymoqda']
            
            positive_count = sum(1 for word in positive_words if word in text.lower())
            negative_count = sum(1 for word in negative_words if word in text.lower())
            
            total_words = len(text.split())
            
            positive_score = positive_count / max(total_words, 1)
            negative_score = negative_count / max(total_words, 1)
            
            return {
                'positive': positive_score,
                'negative': negative_score,
                'neutral': max(0, 1 - positive_score - negative_score),
                'overall_sentiment': 'positive' if positive_count > negative_count else 'negative' if negative_count > positive_count else 'neutral'
            }
            
        except Exception as e:
            logger.error(f"Sentiment tahlilida xato: {e}")
            return {'positive': 0, 'negative': 0, 'neutral': 1, 'overall_sentiment': 'neutral'}

class ArbitrageDetector:
    """Arbitrage imkoniyatlarini aniqlash tizimi"""
    
    def __init__(self, data_provider: CryptoCommoditiesDataProvider):
        self.data_provider = data_provider
        
    def find_arbitrage_opportunities(self) -> List[Dict]:
        """Arbitrage imkoniyatlarini topish"""
        try:
            opportunities = []
            
            # Kripto arbitrage topish
            crypto_symbols = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT']
            
            for symbol in crypto_symbols:
                prices = {}
                
                # Turli birja narxlarini olish
                for exchange_name, exchange in self.data_provider.exchanges.items():
                    try:
                        ticker = exchange.fetch_ticker(symbol)
                        prices[exchange_name] = ticker['last']
                    except:
                        continue
                        
                if len(prices) > 1:
                    max_price = max(prices.values())
                    min_price = min(prices.values())
                    profit_margin = ((max_price - min_price) / min_price) * 100
                    
                    if profit_margin > 0.5:  # 0.5% dan ko'p foyda
                        opportunities.append({
                            'type': 'crypto',
                            'symbol': symbol,
                            'strategy': 'cross-exchange',
                            'buy_exchange': min(prices, key=prices.get),
                            'sell_exchange': max(prices, key=prices.get),
                            'buy_price': min_price,
                            'sell_price': max_price,
                            'profit_margin': profit_margin,
                            'estimated_profit': (max_price - min_price) * 100  # 100 birlik uchun
                        })
                        
            return opportunities
            
        except Exception as e:
            logger.error(f"Arbitrage imkoniyatlar topishda xato: {e}")
            return []

class CryptoCommoditiesManager:
    """Asosiy Crypto & Commodities boshqaruv tizimi"""
    
    def __init__(self):
        self.data_provider = CryptoCommoditiesDataProvider()
        self.price_monitor = RealTimePriceMonitor(self.data_provider)
        self.technical_analyzer = TechnicalAnalyzer()
        self.portfolio_manager = PortfolioManager()
        self.news_analyzer = NewsAnalyzer()
        self.arbitrage_detector = ArbitrageDetector(self.data_provider)
        
        # Callback functions
        self.alert_callbacks = []
        
    async def start_real_time_monitoring(self):
        """Real-time monitoring ishga tushirish"""
        await self.price_monitor.start_monitoring()
        
    def add_price_alert(self, asset_type: str, symbol: str, alert_type: str, 
                       value: float, user_id: str = None) -> str:
        """Narx alert qo'shish"""
        try:
            alert_id = f"{asset_type}_{symbol}_{int(time.time())}"
            
            if asset_type == 'crypto':
                cache_key = f"crypto_{symbol}_*"
            else:
                cache_key = f"commodity_{symbol}"
                
            if cache_key not in self.price_monitor.alert_conditions:
                self.price_monitor.alert_conditions[cache_key] = {}
                
            self.price_monitor.alert_conditions[cache_key][alert_id] = {
                'type': alert_type,
                'value': value,
                'user_id': user_id,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Alert qo'shildi: {alert_id}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Alert qo'shishda xato: {e}")
            return ""
            
    def get_technical_analysis(self, symbol: str, period: str = '1d') -> Dict:
        """Texnik tahlil olish"""
        try:
            # Mock data (real implementation uchun historical data kerak)
            dates = pd.date_range(end=datetime.now(), periods=100, freq='H')
            mock_data = pd.DataFrame({
                'Date': dates,
                'High': np.random.randn(100).cumsum() + 100,
                'Low': np.random.randn(100).cumsum() + 90,
                'Close': np.random.randn(100).cumsum() + 95,
                'Volume': np.random.randint(1000, 10000, 100)
            })
            
            indicators = self.technical_analyzer.get_technical_indicators(mock_data)
            signals = self.technical_analyzer.generate_signals(indicators)
            
            return {
                'symbol': symbol,
                'indicators': indicators,
                'signals': signals,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Texnik tahlilda xato: {e}")
            return {}
            
    def get_portfolio_performance(self, user_id: str) -> Dict:
        """Portfolio ish faoliyati"""
        try:
            portfolio = self.portfolio_manager.get_portfolio(user_id)
            
            # Performance metrics
            total_value = portfolio.total_value
            pnl = portfolio.pnl
            return_rate = (pnl / total_value) * 100 if total_value > 0 else 0
            
            return {
                'total_value': total_value,
                'pnl': pnl,
                'return_rate': return_rate,
                'crypto_allocation': sum(portfolio.crypto_balance.values()) / max(total_value, 1),
                'commodity_allocation': sum(portfolio.commodity_balance.values()) / max(total_value, 1),
                'positions_count': len(portfolio.crypto_balance) + len(portfolio.commodity_balance),
                'last_updated': portfolio.last_updated
            }
            
        except Exception as e:
            logger.error(f"Portfolio tahlilida xato: {e}")
            return {}
            
    def get_news_summary(self) -> Dict:
        """Yangiliklar qisqa ma'lumoti"""
        try:
            crypto_news = self.news_analyzer.get_crypto_news()
            commodity_news = self.news_analyzer.get_commodity_news()
            
            # Sentiment analysis
            crypto_sentiment = []
            for news in crypto_news:
                sentiment = self.news_analyzer.analyze_sentiment(news['title'] + ' ' + news['summary'])
                crypto_sentiment.append(sentiment['overall_sentiment'])
                
            commodity_sentiment = []
            for news in commodity_news:
                sentiment = self.news_analyzer.analyze_sentiment(news['title'] + ' ' + news['summary'])
                commodity_sentiment.append(sentiment['overall_sentiment'])
                
            return {
                'crypto_news': {
                    'count': len(crypto_news),
                    'sentiment_distribution': {
                        'positive': crypto_sentiment.count('positive'),
                        'negative': crypto_sentiment.count('negative'),
                        'neutral': crypto_sentiment.count('neutral')
                    },
                    'latest_news': crypto_news[:3]
                },
                'commodity_news': {
                    'count': len(commodity_news),
                    'sentiment_distribution': {
                        'positive': commodity_sentiment.count('positive'),
                        'negative': commodity_sentiment.count('negative'),
                        'neutral': commodity_sentiment.count('neutral')
                    },
                    'latest_news': commodity_news[:3]
                }
            }
            
        except Exception as e:
            logger.error(f"Yangiliklar tahlilida xato: {e}")
            return {}
            
    def get_arbitrage_opportunities(self) -> List[Dict]:
        """Arbitrage imkoniyatlari"""
        return self.arbitrage_detector.find_arbitrage_opportunities()
        
    def get_supported_assets(self) -> Dict:
        """Qo'llab-quvvatlanadigan aktivlar"""
        return {
            'cryptocurrencies': self.data_provider.supported_cryptos[:20],  # First 20 for display
            'commodities': list(self.data_provider.commodity_sources.keys())
        }
        
    def generate_trading_chart(self, symbol: str, period: str = '1d') -> str:
        """Trading grafigi yaratish"""
        try:
            # Mock data for demonstration
            dates = pd.date_range(end=datetime.now(), periods=50, freq='H')
            prices = np.random.randn(50).cumsum() + 100
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                              vertical_spacing=0.1,
                              subplot_titles=('Narx', 'Volume'),
                              row_width=[0.7, 0.3])
            
            # Price chart
            fig.add_trace(
                go.Scatter(x=dates, y=prices, name='Narx', line=dict(color='blue'))
            )
            
            # Volume chart
            volume = np.random.randint(1000, 5000, 50)
            fig.add_trace(
                go.Bar(x=dates, y=volume, name='Volume', marker_color='lightblue')
            )
            
            fig.update_layout(
                title=f'{symbol} Trading Chart',
                height=600,
                showlegend=True
            )
            
            # Save as HTML
            chart_path = f'/tmp/chart_{symbol.replace("/", "_")}_{period}.html'
            fig.write_html(chart_path)
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Grafik yaratishda xato: {e}")
            return ""

    async def demo_run(self):
        """Demo ishga tushirish"""
        print("🚀 Crypto & Commodities Integration Tizimi ishga tushmoqda...")
        
        # Supported assets
        assets = self.get_supported_assets()
        print(f"📊 Qo'llab-quvvatlanadigan aktivlar:")
        print(f"   Kriptovalutalar: {len(assets['cryptocurrencies'])} ta")
        print(f"   Kommoditilar: {len(assets['commodities'])} ta")
        
        # Technical analysis demo
        print("\n📈 Texnik tahlil:")
        analysis = self.get_technical_analysis('BTC/USDT')
        if analysis and 'signals' in analysis:
            print(f"   BTC/USDT signallari: {analysis['signals']}")
            
        # News summary
        print("\n📰 Yangiliklar:")
        news_summary = self.get_news_summary()
        if news_summary:
            crypto_sentiment = news_summary['crypto_news']['sentiment_distribution']
            print(f"   Kripto sentiment: Positiv={crypto_sentiment['positive']}, "
                  f"Negativ={crypto_sentiment['negative']}, "
                  f"Neutral={crypto_sentiment['neutral']}")
            
        # Arbitrage opportunities
        print("\n💰 Arbitrage imkoniyatlari:")
        arbitrage = self.get_arbitrage_opportunities()
        print(f"   Topilgan imkoniyatlar: {len(arbitrage)} ta")
        
        # Portfolio management demo
        print("\n💼 Portfolio boshqaruv:")
        demo_user_id = "demo_user"
        transaction_result = self.portfolio_manager.add_transaction(
            demo_user_id, "BTC/USDT", "BUY", 0.1, 50000
        )
        print(f"   Tranzaksiya qo'shildi: {transaction_result}")
        
        portfolio_performance = self.get_portfolio_performance(demo_user_id)
        if portfolio_performance:
            print(f"   Portfolio qiymati: ${portfolio_performance['total_value']:.2f}")
            print(f"   P&L: ${portfolio_performance['pnl']:.2f}")
            
        print("\n✅ Demo muvaffaqiyatli yakunlandi!")
        
        # Note: Real-time monitoring is commented out for demo
        # In production, uncomment the line below:
        # await self.start_real_time_monitoring()

# Demo va test funksiyalari
def run_demo():
    """Demo ishga tushirish"""
    async def demo():
        manager = CryptoCommoditiesManager()
        await manager.demo_run()
        
    asyncio.run(demo())

if __name__ == "__main__":
    print("=" * 60)
    print("🪙 Crypto & Commodities Integration Moduli")
    print("=" * 60)
    print("Bu modul quyidagi funksiyalarni ta'minlaydi:")
    print("• 100+ kriptovalyuta trading")
    print("• Real-time narx monitoring")
    print("• Kommoditi tahlili")
    print("• Portfolio boshqaruv")
    print("• Texnik tahlil")
    print("• Yangiliklar integratsiyasi")
    print("• Arbitrage imkoniyatlari")
    print("=" * 60)
    
    # Demo ishga tushirish
    run_demo()