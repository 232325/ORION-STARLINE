#!/usr/bin/env python3
"""
Advanced Forex Tools Moduli
===========================

Bu modul Forex bozorini tahlil qilish va savdo qarorlarini qabul qilish uchun 
murakkab vositalarni taqdim etadi.

Asosiy imkoniyatlar:
- Multi-currency analysis (50+ valyuta juftliklari)
- Economic calendar (Markaziy bank yig'ilishlari, iqtisodiy ko'rsatkichlar)
- Markaziy bank qarorlari kuzatish (Foiz stavkalari, siyosat e'lonlari)
- Korelyatsiya tahlili (Valyuta juftliklari korelyatsiyasi)
- Carry trade imkoniyatlari (Foiz stavkalari farqi)
- Valyuta kuch ko'rsatkichlari (Real-time valyuta kuch indeksi)
- Pivot point va S/R darajalar (Avtomatik hisoblash)
- Yangiliklar sentiment tahlili (Forex yangiliklar sentiment)
- Iqtisodiy ko'rsatkichlarni kuzatish (GDP, CPI, bandlik ma'lumotlari)

Dasturchi: Orion Starline Team
Sana: 2025-11-05
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Logging sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurrencyType(Enum):
    """Valyuta turlari"""
    MAJOR = "major"
    MINOR = "minor" 
    EXOTIC = "exotic"

class CentralBank(Enum):
    """Markaziy banklar"""
    FED = "federal_reserve"
    ECB = "european_central_bank"
    BOE = "bank_of_england"
    BOJ = "bank_of_japan"
    SNB = "swiss_national_bank"
    RBA = "reserve_bank_australia"
    BOC = "bank_of_canada"
    RBNZ = "reserve_bank_new_zealand"

@dataclass
class CurrencyPair:
    """Valyuta juftligi ma'lumotlari"""
    symbol: str
    base_currency: str
    quote_currency: str
    type: CurrencyType
    current_rate: float = 0.0
    daily_change: float = 0.0
    daily_change_pct: float = 0.0
    volume: float = 0.0
    last_update: datetime = None

@dataclass
class EconomicIndicator:
    """Iqtisodiy ko'rsatkich ma'lumotlari"""
    name: str
    country: str
    currency: str
    value: float
    previous_value: float
    forecast_value: float
    impact_level: str
    release_date: datetime
    actual_date: datetime = None
    is_forecast: bool = True

@dataclass
class CentralBankDecision:
    """Markaziy bank qarori ma'lumotlari"""
    bank: CentralBank
    decision_date: datetime
    interest_rate: float
    previous_rate: float
    change_pct: float
    policy_statement: str
    is_emergency: bool = False

@dataclass
class PivotPoint:
    """Pivot point ma'lumotlari"""
    symbol: str
    pivot: float
    support_1: float
    support_2: float
    support_3: float
    resistance_1: float
    resistance_2: float
    resistance_3: float
    current_price: float
    calculation_date: datetime

class AdvancedForexTools:
    """Advanced Forex Tools asosiy klassi"""
    
    def __init__(self, api_key: str = None):
        """Advanced Forex Tools ni ishga tushirish"""
        self.api_key = api_key
        self.session = None
        self.currency_pairs = {}
        self.central_banks = {}
        self.economic_calendar = {}
        self.correlation_matrix = None
        
        # Asosiy valyuta juftliklari
        self._initialize_currency_pairs()
        
        # Markaziy banklar ma'lumotlari
        self._initialize_central_banks()

    def _initialize_currency_pairs(self):
        """Valyuta juftliklarini ishga tushirish"""
        # Major pairs
        majors = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", 
            "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "EURCHF",
            "GBPJPY", "GBPCHF", "AUDJPY", "CADJPY", "CHFJPY"
        ]
        
        # Minor pairs  
        minors = [
            "EURAUD", "EURCAD", "EURNZD", "EURSGD", "EURZAR",
            "GBPAUD", "GBPCAD", "GBPNZD", "GBPSGD", "GBPSAR",
            "AUDCAD", "AUDCHF", "AUDNZD", "AUDCHF", "CADCHF",
            "NZDCAD", "NZDCHF", "NZDJPY", "NZDSGD", "SGDJPY"
        ]
        
        # Exotic pairs
        exotics = [
            "USDTRY", "USDZAR", "USDHKD", "USDSGD", "USDSEK",
            "USDNOK", "USDTHB", "USDMXN", "USDBRL", "USDRUB",
            "USDCZK", "USDDKK", "USDHUF", "USDPLN", "USDISK",
            "EURTRY", "EURZAR", "EURSGD", "GBPSAR", "GBPHKD",
            "GBPRUB", "GBPMXN", "GBPSEK", "GBPNOK", "AUDHKD"
        ]
        
        all_pairs = majors + minors + exotics
        
        for pair in majors:
            self.currency_pairs[pair] = CurrencyPair(
                symbol=pair,
                base_currency=pair[:3],
                quote_currency=pair[3:],
                type=CurrencyType.MAJOR
            )
            
        for pair in minors:
            self.currency_pairs[pair] = CurrencyPair(
                symbol=pair,
                base_currency=pair[:3], 
                quote_currency=pair[3:],
                type=CurrencyType.MINOR
            )
            
        for pair in exotics:
            self.currency_pairs[pair] = CurrencyPair(
                symbol=pair,
                base_currency=pair[:3],
                quote_currency=pair[3:], 
                type=CurrencyType.EXOTIC
            )
    
    def _initialize_central_banks(self):
        """Markaziy banklar ma'lumotlarini ishga tushirish"""
        self.central_banks = {
            CentralBank.FED: {
                "name": "Federal Reserve",
                "currency": "USD",
                "country": "USA",
                "base_rate": 5.25,
                "next_meeting": datetime(2025, 12, 11),
                "decision_frequency": "8 times per year"
            },
            CentralBank.ECB: {
                "name": "European Central Bank", 
                "currency": "EUR",
                "country": "Eurozone",
                "base_rate": 4.25,
                "next_meeting": datetime(2025, 12, 12),
                "decision_frequency": "6-8 times per year"
            },
            CentralBank.BOE: {
                "name": "Bank of England",
                "currency": "GBP", 
                "country": "UK",
                "base_rate": 5.00,
                "next_meeting": datetime(2025, 12, 18),
                "decision_frequency": "8 times per year"
            },
            CentralBank.BOJ: {
                "name": "Bank of Japan",
                "currency": "JPY",
                "country": "Japan", 
                "base_rate": 0.10,
                "next_meeting": datetime(2025, 12, 19),
                "decision_frequency": "8 times per year"
            },
            CentralBank.SNB: {
                "name": "Swiss National Bank",
                "currency": "CHF",
                "country": "Switzerland",
                "base_rate": 1.00,
                "next_meeting": datetime(2025, 12, 11),
                "decision_frequency": "4 times per year"
            },
            CentralBank.RBA: {
                "name": "Reserve Bank of Australia",
                "currency": "AUD",
                "country": "Australia",
                "base_rate": 4.35,
                "next_meeting": datetime(2025, 12, 3),
                "decision_frequency": "11 times per year"
            },
            CentralBank.BOC: {
                "name": "Bank of Canada",
                "currency": "CAD",
                "country": "Canada", 
                "base_rate": 3.75,
                "next_meeting": datetime(2025, 12, 10),
                "decision_frequency": "8 times per year"
            },
            CentralBank.RBNZ: {
                "name": "Reserve Bank of New Zealand",
                "currency": "NZD",
                "country": "New Zealand",
                "base_rate": 5.25,
                "next_meeting": datetime(2025, 11, 27),
                "decision_frequency": "8 times per year"
            }
        }

    async def get_real_time_rates(self, symbols: List[str] = None) -> Dict[str, CurrencyPair]:
        """Real-time valyuta kurslarini olish
        
        Args:
            symbols: Tanlangan valyuta juftliklari ro'yxati (None bo'lsa barchasini)
            
        Returns:
            Valyuta juftliklari va ularning ma'lumotlari
        """
        if symbols is None:
            symbols = list(self.currency_pairs.keys())
            
        try:
            # Simulatsiya qilingan real-time data (haqiqiy API'da aiohttp orqali fetch)
            rates = {}
            
            for symbol in symbols:
                if symbol in self.currency_pairs:
                    # Real-world scenario uchun API chaqiruvi:
                    # url = f"https://api.fxmarketapi.com/live?apikey={self.api_key}&currency={symbol}"
                    # async with self.session.get(url) as response:
                    #     data = await response.json()
                    
                    # Simulatsiya
                    np.random.seed(hash(symbol) % 2**32)
                    base_rate = 1.0 + (hash(symbol) % 100) / 1000
                    
                    pair = self.currency_pairs[symbol]
                    pair.current_rate = base_rate + np.random.normal(0, 0.001)
                    pair.daily_change = np.random.normal(0, 0.01)
                    pair.daily_change_pct = (pair.daily_change / pair.current_rate) * 100
                    pair.volume = np.random.uniform(10000, 1000000)
                    pair.last_update = datetime.now()
                    
                    rates[symbol] = pair
                    
            logger.info(f"Real-time kurslar yangilandi: {len(rates)} juftlik")
            return rates
            
        except Exception as e:
            logger.error(f"Real-time kurslarni olishda xato: {e}")
            return {}

    def calculate_pivot_points(self, high: float, low: float, close: float, 
                             open_price: float = None) -> PivotPoint:
        """Pivot point va Support/Resistance darajalarini hisoblash
        
        Args:
            high: Maksimum narx
            low: Minimum narx  
            close: Yopilish narxi
            open_price: Ochilish narxi (optional)
            
        Returns:
            PivotPoint obyekti
        """
        try:
            # Standard pivot point hisoblash
            if open_price:
                pivot = (high + low + close + open_price) / 4
            else:
                pivot = (high + low + close) / 3
            
            # Support va Resistance darajalar
            support_1 = 2 * pivot - high
            resistance_1 = 2 * pivot - low
            
            support_2 = pivot - (high - low)
            resistance_2 = pivot + (high - low)
            
            support_3 = low - 2 * (high - pivot)
            resistance_3 = high + 2 * (pivot - low)
            
            current_price = close
            
            return PivotPoint(
                symbol="SIMULATED",
                pivot=pivot,
                support_1=support_1,
                support_2=support_2, 
                support_3=support_3,
                resistance_1=resistance_1,
                resistance_2=resistance_2,
                resistance_3=resistance_3,
                current_price=current_price,
                calculation_date=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Pivot point hisoblashda xato: {e}")
            return None

    def calculate_correlation_matrix(self, periods: int = 252) -> pd.DataFrame:
        """Valyuta juftliklari orasidagi korelyatsiyani hisoblash
        
        Args:
            periods: Tahlil qilish davrlari soni
            
        Returns:
            Korelyatsiya matritsasi
        """
        try:
            # Simulatsiya qilingan historical data
            symbols = list(self.currency_pairs.keys())[:20]  # Birinchi 20 ta
            
            # Real scenario uchun historical data fetch
            # data = await self.fetch_historical_data(symbols, periods)
            
            # Simulatsiya uchun random data
            np.random.seed(42)
            data = pd.DataFrame({
                symbol: np.random.randn(periods).cumsum() 
                for symbol in symbols
            })
            
            # Returns hisoblash
            returns = data.pct_change().dropna()
            
            # Korelyatsiya matritsasi
            correlation_matrix = returns.corr()
            self.correlation_matrix = correlation_matrix
            
            logger.info(f"Korelyatsiya matritsasi hisoblandi: {correlation_matrix.shape}")
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"Korelyatsiya hisoblashda xato: {e}")
            return pd.DataFrame()

    def analyze_currency_strength(self) -> Dict[str, float]:
        """Valyuta kuch ko'rsatkichini tahlil qilish
        
        Returns:
            Valyuta kuch ko'rsatkichlari
        """
        try:
            # Simulatsiya qilingan currency strength
            currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD']
            
            strength_index = {}
            
            for currency in currencies:
                # Real calculation would involve multiple pairs containing this currency
                # For simulation, we'll use a weighted random approach
                np.random.seed(hash(currency) % 2**32)
                
                # Base strength calculation using correlated pairs
                strength = 100 + np.random.normal(0, 10)
                strength_index[currency] = max(0, min(200, strength))
            
            # Normalize to show relative strength
            mean_strength = np.mean(list(strength_index.values()))
            for currency in strength_index:
                strength_index[currency] = (strength_index[currency] / mean_strength) * 100
            
            logger.info(f"Valyuta kuch ko'rsatkichlari hisoblash: {len(strength_index)} valyuta")
            return strength_index
            
        except Exception as e:
            logger.error(f"Valyuta kuch tahlilida xato: {e}")
            return {}

    def find_carry_trade_opportunities(self) -> List[Dict[str, Any]]:
        """Carry trade imkoniyatlarini topish
        
        Returns:
            Carry trade imkoniyatlari ro'yxati
        """
        try:
            opportunities = []
            
            # Foiz stavkalarini olish
            rates = {
                'USD': 5.25, 'EUR': 4.25, 'GBP': 5.00, 'JPY': 0.10,
                'CHF': 1.00, 'AUD': 4.35, 'CAD': 3.75, 'NZD': 5.25
            }
            
            for symbol, pair in self.currency_pairs.items():
                if pair.type == CurrencyType.MAJOR:
                    base_rate = rates.get(pair.base_currency, 0)
                    quote_rate = rates.get(pair.quote_currency, 0)
                    
                    carry_rate = base_rate - quote_rate
                    
                    if abs(carry_rate) > 0.5:  # Minimal carry trade criteria
                        direction = "Long" if carry_rate > 0 else "Short"
                        
                        opportunities.append({
                            'symbol': symbol,
                            'carry_rate': carry_rate,
                            'direction': direction,
                            'base_currency': pair.base_currency,
                            'quote_currency': pair.quote_currency,
                            'base_rate': base_rate,
                            'quote_rate': quote_rate,
                            'attractiveness': abs(carry_rate),
                            'risk_level': 'Medium' if abs(carry_rate) < 2 else 'High'
                        })
            
            # Eng yaxshi imkoniyatlarni saralash
            opportunities.sort(key=lambda x: x['attractiveness'], reverse=True)
            
            logger.info(f"Carry trade imkoniyatlari topildi: {len(opportunities)}")
            return opportunities[:10]  # Eng yaxshi 10 tasini qaytarish
            
        except Exception as e:
            logger.error(f"Carry trade tahlilida xato: {e}")
            return []

    def get_economic_calendar(self, days_ahead: int = 30) -> List[EconomicIndicator]:
        """Iqtisodiy kalendarni olish
        
        Args:
            days_ahead: Necha kun oldin ko'rish
            
        Returns:
            Iqtisodiy ko'rsatkichlar ro'yxati
        """
        try:
            indicators = []
            
            # Simulatsiya qilingan economic calendar
            economic_events = [
                {
                    'name': 'Non Farm Payrolls',
                    'country': 'USA', 
                    'currency': 'USD',
                    'impact': 'High',
                    'frequency': 'Monthly'
                },
                {
                    'name': 'CPI',
                    'country': 'Eurozone',
                    'currency': 'EUR', 
                    'impact': 'High',
                    'frequency': 'Monthly'
                },
                {
                    'name': 'GDP',
                    'country': 'UK',
                    'currency': 'GBP',
                    'impact': 'High', 
                    'frequency': 'Quarterly'
                },
                {
                    'name': 'Core CPI',
                    'country': 'Japan',
                    'currency': 'JPY',
                    'impact': 'Medium',
                    'frequency': 'Monthly'
                },
                {
                    'name': 'Retail Sales',
                    'country': 'Australia',
                    'currency': 'AUD',
                    'impact': 'Medium',
                    'frequency': 'Monthly'
                }
            ]
            
            for event in economic_events:
                for i in range(3):  # Har bir event uchun 3 ta keyingi release
                    release_date = datetime.now() + timedelta(days=i*7 + np.random.randint(0, 7))
                    
                    indicator = EconomicIndicator(
                        name=event['name'],
                        country=event['country'],
                        currency=event['currency'],
                        value=np.random.uniform(-2, 5),
                        previous_value=np.random.uniform(-2, 5),
                        forecast_value=np.random.uniform(-1, 4),
                        impact_level=event['impact'],
                        release_date=release_date
                    )
                    
                    indicators.append(indicator)
            
            logger.info(f"Iqtisodiy kalendar yuklandi: {len(indicators)} voqea")
            return indicators[:20]  # Eng yaqin 20 ta voqeani qaytarish
            
        except Exception as e:
            logger.error(f"Iqtisodiy kalendar olishda xato: {e}")
            return []

    def get_central_bank_decisions(self) -> List[CentralBankDecision]:
        """Markaziy bank qarorlarini olish
        
        Returns:
            Markaziy bank qarorlari ro'yxati
        """
        try:
            decisions = []
            
            for bank_enum, bank_info in self.central_banks.items():
                # Simulatsiya qilingan qaror
                current_rate = bank_info['base_rate']
                previous_rate = current_rate + np.random.uniform(-0.5, 0.5)
                change = current_rate - previous_rate
                
                decision = CentralBankDecision(
                    bank=bank_enum,
                    decision_date=bank_info['next_meeting'],
                    interest_rate=current_rate,
                    previous_rate=previous_rate,
                    change_pct=(change / previous_rate) * 100 if previous_rate != 0 else 0,
                    policy_statement=f"Monetary policy decision by {bank_info['name']}",
                    is_emergency=False
                )
                
                decisions.append(decision)
            
            logger.info(f"Markaziy bank qarorlari: {len(decisions)} bank")
            return decisions
            
        except Exception as e:
            logger.error(f"Markaziy bank qarorlarida xato: {e}")
            return []

    def analyze_news_sentiment(self, news_text: str = None) -> Dict[str, float]:
        """Yangiliklar sentimentini tahlil qilish
        
        Args:
            news_text: Tahlil qilish uchun yangiliklar matni
            
        Returns:
            Sentiment tahlili natijasi
        """
        try:
            # Simulatsiya qilingan sentiment analysis
            if news_text is None:
                news_text = "Global economic outlook remains positive with strong dollar performance"
            
            # Real implementation would use NLP libraries like VADER, TextBlob, or transformers
            sentiments = {
                'overall_sentiment': np.random.uniform(-1, 1),
                'dollar_sentiment': np.random.uniform(-1, 1),
                'euro_sentiment': np.random.uniform(-1, 1),
                'pound_sentiment': np.random.uniform(-1, 1),
                'yen_sentiment': np.random.uniform(-1, 1),
                'confidence': np.random.uniform(0.5, 1.0),
                'volatility_impact': np.random.uniform(0, 1),
                'trading_signal': np.random.choice(['Buy', 'Sell', 'Hold'])
            }
            
            logger.info("News sentiment analysis completed")
            return sentiments
            
        except Exception as e:
            logger.error(f"News sentiment tahlilida xato: {e}")
            return {}

    def calculate_technical_indicators(self, prices: List[float], 
                                     indicators: List[str] = None) -> Dict[str, float]:
        """Texnik indikatorlarni hisoblash
        
        Args:
            prices: Narxlar ro'yxati
            indicators: Hisoblash kerak bo'lgan indikatorlar
            
        Returns:
            Texnik indikatorlar qiymatlari
        """
        try:
            if indicators is None:
                indicators = ['sma_20', 'sma_50', 'ema_12', 'rsi_14', 'macd', 'bollinger']
            
            if len(prices) < 50:
                logger.warning("Texnik indikatorlar uchun yetarli ma'lumot yo'q")
                return {}
            
            price_series = pd.Series(prices)
            results = {}
            
            # Simple Moving Average
            if 'sma_20' in indicators:
                results['sma_20'] = price_series.rolling(20).mean().iloc[-1]
            if 'sma_50' in indicators:
                results['sma_50'] = price_series.rolling(50).mean().iloc[-1]
            
            # Exponential Moving Average
            if 'ema_12' in indicators:
                results['ema_12'] = price_series.ewm(span=12).mean().iloc[-1]
            
            # RSI
            if 'rsi_14' in indicators:
                delta = price_series.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                results['rsi_14'] = 100 - (100 / (1 + rs)).iloc[-1]
            
            # MACD
            if 'macd' in indicators:
                ema_12 = price_series.ewm(span=12).mean()
                ema_26 = price_series.ewm(span=26).mean()
                macd = ema_12 - ema_26
                signal = macd.ewm(span=9).mean()
                results['macd'] = macd.iloc[-1]
                results['macd_signal'] = signal.iloc[-1]
                results['macd_histogram'] = (macd - signal).iloc[-1]
            
            # Bollinger Bands
            if 'bollinger' in indicators:
                sma_20 = price_series.rolling(20).mean()
                std_20 = price_series.rolling(20).std()
                results['bollinger_upper'] = (sma_20 + 2 * std_20).iloc[-1]
                results['bollinger_middle'] = sma_20.iloc[-1]
                results['bollinger_lower'] = (sma_20 - 2 * std_20).iloc[-1]
            
            logger.info(f"Texnik indikatorlar hisoblash: {len(results)} indicator")
            return results
            
        except Exception as e:
            logger.error(f"Texnik indikator hisoblashda xato: {e}")
            return {}

    def multi_currency_analysis(self) -> Dict[str, Any]:
        """Barcha valyutalar bo'yicha umumiy tahlil
        
        Returns:
            Ko'p valyutali tahlil natijasi
        """
        try:
            # Parallel tahlillar
            currency_strength = self.analyze_currency_strength()
            carry_opportunities = self.find_carry_trade_opportunities()
            correlation_matrix = self.calculate_correlation_matrix()
            
            # Economic calendar integration
            economic_events = self.get_economic_calendar()
            central_decisions = self.get_central_bank_decisions()
            
            # High impact events filtering
            high_impact_events = [
                event for event in economic_events 
                if event.impact_level == 'High'
            ]
            
            # Currency ranking by strength
            strength_ranking = sorted(
                currency_strength.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Correlation insights
            high_correlations = []
            if correlation_matrix is not None and not correlation_matrix.empty:
                for i in range(len(correlation_matrix.columns)):
                    for j in range(i+1, len(correlation_matrix.columns)):
                        corr_value = correlation_matrix.iloc[i, j]
                        if abs(corr_value) > 0.7:
                            high_correlations.append({
                                'pair1': correlation_matrix.columns[i],
                                'pair2': correlation_matrix.columns[j],
                                'correlation': corr_value
                            })
            
            analysis_result = {
                'timestamp': datetime.now(),
                'currency_strength': {
                    'rankings': strength_ranking,
                    'strongest': strength_ranking[0] if strength_ranking else None,
                    'weakest': strength_ranking[-1] if strength_ranking else None
                },
                'carry_trade_opportunities': carry_opportunities[:5],
                'economic_outlook': {
                    'high_impact_events': len(high_impact_events),
                    'central_bank_decisions': len(central_decisions),
                    'next_major_event': min([e.release_date for e in high_impact_events], default=None)
                },
                'correlation_insights': {
                    'high_correlations': high_correlations,
                    'diversification_score': len(high_correlations) / 10
                },
                'market_sentiment': self.analyze_news_sentiment(),
                'recommended_trades': self._generate_recommendations(
                    currency_strength, carry_opportunities, high_impact_events
                )
            }
            
            logger.info("Multi-currency analysis completed")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Multi-currency analysisda xato: {e}")
            return {}

    def _generate_recommendations(self, currency_strength: Dict[str, float],
                                carry_opportunities: List[Dict],
                                high_impact_events: List[EconomicIndicator]) -> List[Dict]:
        """Tavsiyalar yaratish
        
        Args:
            currency_strength: Valyuta kuch ko'rsatkichlari
            carry_opportunities: Carry trade imkoniyatlari
            high_impact_events: Yuqori ta'sir voqealari
            
        Returns:
            Tavsiyalar ro'yxati
        """
        try:
            recommendations = []
            
            # Strength-based recommendations
            if currency_strength:
                strongest = max(currency_strength.items(), key=lambda x: x[1])
                weakest = min(currency_strength.items(), key=lambda x: x[1])
                
                recommendations.append({
                    'type': 'Currency Strength',
                    'action': f'Long {strongest[0]} / Short {weakest[0]}',
                    'confidence': 'Medium',
                    'rationale': f'{strongest[0]} showing strength, {weakest[0]} showing weakness',
                    'timeframe': '1-2 weeks'
                })
            
            # Carry trade recommendations
            if carry_opportunities:
                best_carry = carry_opportunities[0]
                recommendations.append({
                    'type': 'Carry Trade',
                    'action': f'{best_carry["direction"]} {best_carry["symbol"]}',
                    'confidence': 'High' if best_carry['risk_level'] == 'Medium' else 'Medium',
                    'rationale': f'Positive carry rate of {best_carry["carry_rate"]:.2f}%',
                    'timeframe': '1-3 months'
                })
            
            # Event-based recommendations
            if high_impact_events:
                next_event = min(high_impact_events, key=lambda x: x.release_date)
                recommendations.append({
                    'type': 'Event-Driven',
                    'action': f'Position sizing adjustment for {next_event.currency}',
                    'confidence': 'Medium',
                    'rationale': f'Upcoming {next_event.name} release',
                    'timeframe': '1-2 days'
                })
            
            logger.info(f"Recommendations generated: {len(recommendations)}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendations generationda xato: {e}")
            return []

    async def close_session(self):
        """HTTP sessionni yopish"""
        if self.session:
            await self.session.close()
            logger.info("HTTP session closed")

    def export_analysis_report(self, analysis_data: Dict[str, Any], 
                             filename: str = None) -> str:
        """Tahlil hisobotini eksport qilish
        
        Args:
            analysis_data: Tahlil ma'lumotlari
            filename: Fayl nomi (optional)
            
        Returns:
            Fayl yo'li
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"forex_analysis_{timestamp}.json"
            
            # Add metadata
            report = {
                'metadata': {
                    'generated_at': datetime.now(),
                    'tool_version': '1.0.0',
                    'analysis_period': 'Current',
                    'currency_pairs_analyzed': len(self.currency_pairs)
                },
                'analysis': analysis_data
            }
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(f"Analysis report exported: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Report exportda xato: {e}")
            return ""

# Utility funksiyalar
def create_forex_session(api_key: str = None) -> AdvancedForexTools:
    """Forex session yaratish uchun utility funksiya
    
    Args:
        api_key: API kaliti
        
    Returns:
        AdvancedForexTools instance
    """
    return AdvancedForexTools(api_key)

async def quick_analysis(symbols: List[str] = None) -> Dict[str, Any]:
    """Tezkor tahlil funksiyasi
    
    Args:
        symbols: Tahlil qilish uchun valyuta juftliklari
        
    Returns:
        Tahlil natijasi
    """
    forex_tool = AdvancedForexTools()
    
    try:
        # Get real-time rates
        rates = await forex_tool.get_real_time_rates(symbols)
        
        # Quick analysis
        currency_strength = forex_tool.analyze_currency_strength()
        carry_opps = forex_tool.find_carry_trade_opportunities()
        
        return {
            'rates': {k: v.current_rate for k, v in rates.items()},
            'strength': currency_strength,
            'carry_trades': carry_opps,
            'timestamp': datetime.now()
        }
        
    finally:
        await forex_tool.close_session()

# Test funksiyasi
async def test_advanced_forex():
    """Advanced Forex Tools ni test qilish"""
    print("🔍 Advanced Forex Tools Test")
    print("=" * 50)
    
    # Forex tools instance yaratish
    forex = AdvancedForexTools()
    
    try:
        # 1. Real-time rates
        print("\n📊 Real-time Rates:")
        rates = await forex.get_real_time_rates(['EURUSD', 'GBPUSD', 'USDJPY'])
        for symbol, data in rates.items():
            print(f"  {symbol}: {data.current_rate:.5f} ({data.daily_change_pct:+.2f}%)")
        
        # 2. Currency strength
        print("\n💪 Currency Strength:")
        strength = forex.analyze_currency_strength()
        for currency, value in list(strength.items())[:5]:
            print(f"  {currency}: {value:.2f}")
        
        # 3. Carry trade opportunities
        print("\n💰 Carry Trade Opportunities:")
        carry_ops = forex.find_carry_trade_opportunities()
        for op in carry_ops[:3]:
            print(f"  {op['symbol']}: {op['direction']} (Carry: {op['carry_rate']:.2f}%)")
        
        # 4. Economic calendar
        print("\n📅 Economic Calendar:")
        calendar = forex.get_economic_calendar()
        for event in calendar[:3]:
            print(f"  {event.name} ({event.currency}): {event.release_date.strftime('%Y-%m-%d')}")
        
        # 5. Multi-currency analysis
        print("\n🔬 Multi-currency Analysis:")
        analysis = forex.multi_currency_analysis()
        print(f"  Strongest: {analysis['currency_strength']['strongest']}")
        print(f"  Carry Trades: {len(analysis['carry_trade_opportunities'])}")
        print(f"  High Impact Events: {analysis['economic_outlook']['high_impact_events']}")
        
        # 6. Technical indicators
        print("\n📈 Technical Indicators:")
        # Simulatsiya narxlari
        prices = [1.0500 + i * 0.001 + np.random.normal(0, 0.001) for i in range(100)]
        indicators = forex.calculate_technical_indicators(prices)
        for indicator, value in indicators.items():
            if isinstance(value, float):
                print(f"  {indicator}: {value:.5f}")
        
        print("\n✅ Advanced Forex Tools test completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        
    finally:
        await forex.close_session()

if __name__ == "__main__":
    # Test qo'llash
    asyncio.run(test_advanced_forex())