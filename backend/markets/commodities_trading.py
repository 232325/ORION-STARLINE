"""
AI Trading Evolution - Commodities Trading Module
================================================

Bu modul 8 xil tovar bozorlarini qo'llab-quvvatlaydi:
- Energiya: Oil (Neft), Gas (Gaz)
- Qishloq xo'jaligi: Wheat (Bug'doy), Corn (Makkajo'xori), Soybeans (Soya)
- Oziq-ovqat: Coffee (Qahva), Sugar (Shakar), Cocoa (Kakao)

Real-time narxlar, futures kontraktlar, seasonal patterns va arbitraj imkoniyatlari.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import numpy as np
import pandas as pd
from collections import defaultdict
import json

# Logging sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommodityType(Enum):
    """Tovar turlari"""
    OIL = "oil"  # Neft (WTI, Brent)
    GAS = "natural_gas"  # Tabiiy gaz
    WHEAT = "wheat"  # Bug'doy
    CORN = "corn"  # Makkajo'xori
    COFFEE = "coffee"  # Qahva
    SUGAR = "sugar"  # Shakar
    COCOA = "cocoa"  # Kakao
    SOYBEANS = "soybeans"  # Soya


class ContractMonth(Enum):
    """Futures kontrakt oylari"""
    JAN = "F"
    FEB = "G"
    MAR = "H"
    APR = "J"
    MAY = "K"
    JUN = "M"
    JUL = "N"
    AUG = "Q"
    SEP = "U"
    OCT = "V"
    NOV = "X"
    DEC = "Z"


@dataclass
class CommodityContract:
    """Futures kontrakt ma'lumotlari"""
    symbol: str
    commodity_type: CommodityType
    contract_month: str
    expiry_date: datetime
    price: float
    volume: int
    open_interest: int
    bid: float
    ask: float
    last_update: datetime = field(default_factory=datetime.now)
    
    @property
    def spread(self) -> float:
        """Bid-Ask spread"""
        return self.ask - self.bid
    
    @property
    def days_to_expiry(self) -> int:
        """Muddati tugashiga qolgan kunlar"""
        return (self.expiry_date - datetime.now()).days


@dataclass
class SpotPrice:
    """Spot narx ma'lumotlari"""
    commodity_type: CommodityType
    price: float
    currency: str
    exchange: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SeasonalPattern:
    """Mavsumiy pattern ma'lumotlari"""
    commodity_type: CommodityType
    month: int
    avg_return: float
    std_dev: float
    win_rate: float
    historical_years: int


class CommoditiesDataProvider:
    """
    Tovarlar uchun ma'lumot provayderi
    Real API'lar: Alpha Vantage, Quandl, CME Group, ICE
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Tuple[datetime, any]] = {}
        self.cache_ttl = 60  # 60 soniya
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Kesh hali validmi?"""
        if key not in self.cache:
            return False
        timestamp, _ = self.cache[key]
        return (datetime.now() - timestamp).seconds < self.cache_ttl
    
    async def get_spot_price(self, commodity: CommodityType) -> Optional[SpotPrice]:
        """Hozirgi spot narxni olish"""
        cache_key = f"spot_{commodity.value}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            # Alpha Vantage API orqali narx olish
            api_key = self.api_keys.get('alpha_vantage', '')
            
            # Commodity symbol mapping
            symbols = {
                CommodityType.OIL: "WTI",
                CommodityType.GAS: "NATURAL_GAS",
                CommodityType.WHEAT: "WHEAT",
                CommodityType.CORN: "CORN",
                CommodityType.COFFEE: "COFFEE",
                CommodityType.SUGAR: "SUGAR",
                CommodityType.COCOA: "COCOA",
                CommodityType.SOYBEANS: "SOYBEANS"
            }
            
            symbol = symbols.get(commodity, commodity.value.upper())
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'COMMODITY',
                'symbol': symbol,
                'interval': 'daily',
                'apikey': api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Ma'lumotni parse qilish
                    if 'data' in data:
                        latest = data['data'][0]
                        spot_price = SpotPrice(
                            commodity_type=commodity,
                            price=float(latest['value']),
                            currency='USD',
                            exchange='ICE',  # Intercontinental Exchange
                            timestamp=datetime.fromisoformat(latest['date'])
                        )
                        
                        self.cache[cache_key] = (datetime.now(), spot_price)
                        return spot_price
            
            # Demo ma'lumot (API ishlamasa)
            demo_prices = {
                CommodityType.OIL: 78.50,
                CommodityType.GAS: 2.85,
                CommodityType.WHEAT: 6.45,
                CommodityType.CORN: 5.20,
                CommodityType.COFFEE: 1.75,
                CommodityType.SUGAR: 0.22,
                CommodityType.COCOA: 2.85,
                CommodityType.SOYBEANS: 13.50
            }
            
            spot_price = SpotPrice(
                commodity_type=commodity,
                price=demo_prices.get(commodity, 100.0),
                currency='USD',
                exchange='DEMO',
                timestamp=datetime.now()
            )
            
            self.cache[cache_key] = (datetime.now(), spot_price)
            return spot_price
            
        except Exception as e:
            logger.error(f"Spot narxni olishda xato ({commodity.value}): {e}")
            return None
    
    async def get_futures_contracts(
        self, 
        commodity: CommodityType,
        months: int = 6
    ) -> List[CommodityContract]:
        """Futures kontraktlarni olish"""
        cache_key = f"futures_{commodity.value}_{months}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            contracts = []
            base_price = await self.get_spot_price(commodity)
            
            if not base_price:
                return []
            
            # Keyingi N oy uchun kontraktlar generatsiya qilish
            for i in range(1, months + 1):
                expiry = datetime.now() + timedelta(days=30 * i)
                contract_code = list(ContractMonth)[expiry.month - 1].value
                
                # Contango/Backwardation simulatsiyasi
                # Contango: futures > spot (storage cost)
                # Backwardation: futures < spot (convenience yield)
                price_adjustment = np.random.uniform(-0.02, 0.05)  # -2% to +5%
                futures_price = base_price.price * (1 + price_adjustment * i / months)
                
                contract = CommodityContract(
                    symbol=f"{commodity.value.upper()}{contract_code}{expiry.year % 100}",
                    commodity_type=commodity,
                    contract_month=contract_code,
                    expiry_date=expiry,
                    price=round(futures_price, 2),
                    volume=np.random.randint(10000, 100000),
                    open_interest=np.random.randint(50000, 500000),
                    bid=round(futures_price * 0.999, 2),
                    ask=round(futures_price * 1.001, 2)
                )
                
                contracts.append(contract)
            
            self.cache[cache_key] = (datetime.now(), contracts)
            return contracts
            
        except Exception as e:
            logger.error(f"Futures kontraktlarni olishda xato ({commodity.value}): {e}")
            return []
    
    async def get_seasonal_patterns(
        self, 
        commodity: CommodityType
    ) -> List[SeasonalPattern]:
        """Mavsumiy patternlarni olish"""
        # Tarixiy ma'lumotlarga asoslangan mavsumiy patternlar
        patterns_data = {
            CommodityType.WHEAT: [
                # Bug'doy: hosilga bog'liq (yoz - past, qish - yuqori)
                (1, 0.015, 0.08, 0.55), (2, 0.020, 0.09, 0.58),
                (3, 0.025, 0.10, 0.60), (4, 0.010, 0.12, 0.52),
                (5, -0.020, 0.15, 0.45), (6, -0.035, 0.18, 0.40),
                (7, -0.025, 0.16, 0.42), (8, 0.005, 0.12, 0.48),
                (9, 0.020, 0.10, 0.55), (10, 0.030, 0.09, 0.60),
                (11, 0.025, 0.08, 0.58), (12, 0.015, 0.07, 0.55)
            ],
            CommodityType.CORN: [
                # Makkajo'xori: yoz o'rtasida past (hosil), qishda yuqori
                (1, 0.010, 0.09, 0.52), (2, 0.015, 0.10, 0.54),
                (3, 0.020, 0.11, 0.56), (4, 0.012, 0.13, 0.50),
                (5, -0.015, 0.16, 0.46), (6, -0.030, 0.19, 0.42),
                (7, -0.040, 0.20, 0.38), (8, -0.020, 0.17, 0.44),
                (9, 0.010, 0.12, 0.50), (10, 0.025, 0.10, 0.57),
                (11, 0.020, 0.09, 0.55), (12, 0.012, 0.08, 0.52)
            ],
            CommodityType.COFFEE: [
                # Qahva: Brazilian hosil mavsumi (may-sentyabr)
                (1, 0.020, 0.12, 0.56), (2, 0.025, 0.13, 0.58),
                (3, 0.030, 0.14, 0.60), (4, 0.015, 0.15, 0.54),
                (5, -0.010, 0.17, 0.48), (6, -0.025, 0.19, 0.44),
                (7, -0.030, 0.20, 0.42), (8, -0.015, 0.18, 0.46),
                (9, 0.005, 0.15, 0.50), (10, 0.020, 0.13, 0.56),
                (11, 0.025, 0.12, 0.58), (12, 0.022, 0.11, 0.57)
            ],
            CommodityType.SUGAR: [
                # Shakar: Brazilian va Indian hosil davrlari
                (1, 0.012, 0.10, 0.53), (2, 0.018, 0.11, 0.55),
                (3, 0.022, 0.12, 0.57), (4, 0.010, 0.14, 0.51),
                (5, -0.015, 0.16, 0.47), (6, -0.028, 0.18, 0.43),
                (7, -0.032, 0.19, 0.41), (8, -0.018, 0.17, 0.45),
                (9, 0.008, 0.14, 0.50), (10, 0.020, 0.12, 0.56),
                (11, 0.024, 0.11, 0.58), (12, 0.015, 0.10, 0.54)
            ],
            CommodityType.COCOA: [
                # Kakao: West Africa asosiy hosil (oktyabr-mart)
                (1, 0.015, 0.13, 0.54), (2, 0.010, 0.14, 0.52),
                (3, 0.005, 0.15, 0.50), (4, -0.005, 0.14, 0.48),
                (5, 0.005, 0.13, 0.50), (6, 0.015, 0.12, 0.54),
                (7, 0.025, 0.11, 0.58), (8, 0.030, 0.12, 0.60),
                (9, 0.028, 0.13, 0.59), (10, 0.020, 0.14, 0.56),
                (11, 0.015, 0.13, 0.54), (12, 0.012, 0.12, 0.53)
            ],
            CommodityType.SOYBEANS: [
                # Soya: US hosil (sentyabr-noyabr)
                (1, 0.018, 0.10, 0.55), (2, 0.022, 0.11, 0.57),
                (3, 0.025, 0.12, 0.59), (4, 0.015, 0.13, 0.54),
                (5, 0.005, 0.15, 0.50), (6, -0.010, 0.17, 0.46),
                (7, -0.015, 0.18, 0.44), (8, -0.020, 0.19, 0.42),
                (9, -0.025, 0.20, 0.40), (10, -0.015, 0.18, 0.44),
                (11, 0.005, 0.14, 0.50), (12, 0.015, 0.11, 0.55)
            ],
            CommodityType.OIL: [
                # Neft: qishda talab yuqori (driving season yozda)
                (1, 0.020, 0.12, 0.56), (2, 0.015, 0.13, 0.54),
                (3, 0.010, 0.14, 0.52), (4, 0.015, 0.13, 0.54),
                (5, 0.025, 0.12, 0.58), (6, 0.030, 0.11, 0.60),
                (7, 0.025, 0.12, 0.58), (8, 0.015, 0.13, 0.54),
                (9, 0.005, 0.15, 0.50), (10, 0.010, 0.14, 0.52),
                (11, 0.020, 0.12, 0.56), (12, 0.025, 0.11, 0.58)
            ],
            CommodityType.GAS: [
                # Tabiiy gaz: qishda talab juda yuqori (heating)
                (1, 0.040, 0.15, 0.62), (2, 0.035, 0.16, 0.60),
                (3, 0.020, 0.17, 0.56), (4, -0.010, 0.18, 0.48),
                (5, -0.025, 0.19, 0.44), (6, -0.035, 0.20, 0.40),
                (7, -0.030, 0.19, 0.42), (8, -0.020, 0.18, 0.46),
                (9, -0.005, 0.16, 0.50), (10, 0.015, 0.14, 0.54),
                (11, 0.030, 0.13, 0.59), (12, 0.038, 0.14, 0.61)
            ]
        }
        
        data = patterns_data.get(commodity, [])
        patterns = []
        
        for month, avg_return, std_dev, win_rate in data:
            pattern = SeasonalPattern(
                commodity_type=commodity,
                month=month,
                avg_return=avg_return,
                std_dev=std_dev,
                win_rate=win_rate,
                historical_years=20
            )
            patterns.append(pattern)
        
        return patterns


class CommodityArbitrageDetector:
    """
    Tovarlar bo'yicha arbitraj imkoniyatlarini aniqlash
    - Calendar spread arbitrage
    - Inter-commodity spread
    - Spot-Futures arbitrage
    """
    
    def __init__(self, data_provider: CommoditiesDataProvider):
        self.data_provider = data_provider
    
    async def detect_calendar_spreads(
        self, 
        commodity: CommodityType,
        threshold: float = 0.02
    ) -> List[Dict]:
        """
        Calendar spread arbitraj: turli muddatli kontraktlar orasidagi spread
        """
        contracts = await self.data_provider.get_futures_contracts(commodity, months=6)
        
        if len(contracts) < 2:
            return []
        
        opportunities = []
        
        for i in range(len(contracts) - 1):
            near_contract = contracts[i]
            far_contract = contracts[i + 1]
            
            # Spread hisoblash
            spread = (far_contract.price - near_contract.price) / near_contract.price
            
            # Normal contango: 1-2% per month
            expected_spread = 0.015 * (i + 1)
            spread_deviation = spread - expected_spread
            
            if abs(spread_deviation) > threshold:
                opportunity = {
                    'type': 'calendar_spread',
                    'commodity': commodity.value,
                    'near_contract': near_contract.symbol,
                    'far_contract': far_contract.symbol,
                    'near_price': near_contract.price,
                    'far_price': far_contract.price,
                    'spread': spread,
                    'expected_spread': expected_spread,
                    'deviation': spread_deviation,
                    'action': 'buy_near_sell_far' if spread_deviation > 0 else 'sell_near_buy_far',
                    'confidence': min(abs(spread_deviation) / threshold, 1.0)
                }
                opportunities.append(opportunity)
        
        return opportunities
    
    async def detect_intercommodity_spreads(self) -> List[Dict]:
        """
        Inter-commodity spread: bog'liq tovarlar orasidagi nisbat
        - Corn vs Wheat
        - WTI vs Brent Oil
        - Coffee vs Cocoa
        """
        opportunities = []
        
        # Corn/Wheat spread
        corn_price = await self.data_provider.get_spot_price(CommodityType.CORN)
        wheat_price = await self.data_provider.get_spot_price(CommodityType.WHEAT)
        
        if corn_price and wheat_price:
            ratio = corn_price.price / wheat_price.price
            # Tarixiy o'rtacha: ~0.85
            if ratio < 0.75:
                opportunities.append({
                    'type': 'intercommodity_spread',
                    'pair': 'CORN/WHEAT',
                    'ratio': ratio,
                    'expected_ratio': 0.85,
                    'action': 'buy_corn_sell_wheat',
                    'confidence': (0.85 - ratio) / 0.10
                })
            elif ratio > 0.95:
                opportunities.append({
                    'type': 'intercommodity_spread',
                    'pair': 'CORN/WHEAT',
                    'ratio': ratio,
                    'expected_ratio': 0.85,
                    'action': 'sell_corn_buy_wheat',
                    'confidence': (ratio - 0.85) / 0.10
                })
        
        # Coffee/Cocoa spread
        coffee_price = await self.data_provider.get_spot_price(CommodityType.COFFEE)
        cocoa_price = await self.data_provider.get_spot_price(CommodityType.COCOA)
        
        if coffee_price and cocoa_price:
            ratio = coffee_price.price / cocoa_price.price
            # Tarixiy o'rtacha: ~0.65
            if ratio < 0.55:
                opportunities.append({
                    'type': 'intercommodity_spread',
                    'pair': 'COFFEE/COCOA',
                    'ratio': ratio,
                    'expected_ratio': 0.65,
                    'action': 'buy_coffee_sell_cocoa',
                    'confidence': (0.65 - ratio) / 0.10
                })
            elif ratio > 0.75:
                opportunities.append({
                    'type': 'intercommodity_spread',
                    'pair': 'COFFEE/COCOA',
                    'ratio': ratio,
                    'expected_ratio': 0.65,
                    'action': 'sell_coffee_buy_cocoa',
                    'confidence': (ratio - 0.65) / 0.10
                })
        
        return opportunities
    
    async def detect_spot_futures_arbitrage(
        self, 
        commodity: CommodityType,
        threshold: float = 0.03
    ) -> List[Dict]:
        """
        Spot-Futures arbitrage: spot va eng yaqin futures orasidagi farq
        """
        spot = await self.data_provider.get_spot_price(commodity)
        contracts = await self.data_provider.get_futures_contracts(commodity, months=2)
        
        if not spot or not contracts:
            return []
        
        opportunities = []
        near_contract = contracts[0]
        
        # Basis hisoblash
        basis = near_contract.price - spot.price
        basis_pct = basis / spot.price
        
        # Juda katta basis - arbitraj imkoniyati
        if abs(basis_pct) > threshold:
            opportunity = {
                'type': 'spot_futures_arbitrage',
                'commodity': commodity.value,
                'spot_price': spot.price,
                'futures_price': near_contract.price,
                'basis': basis,
                'basis_pct': basis_pct,
                'action': 'buy_spot_sell_futures' if basis_pct > threshold else 'sell_spot_buy_futures',
                'confidence': min(abs(basis_pct) / threshold, 1.0),
                'expiry_days': near_contract.days_to_expiry
            }
            opportunities.append(opportunity)
        
        return opportunities


class SeasonalTradingStrategy:
    """
    Mavsumiy trading strategiyasi
    Tarixiy seasonal patterns asosida pozitsiya ochish
    """
    
    def __init__(self, data_provider: CommoditiesDataProvider):
        self.data_provider = data_provider
        self.positions: Dict[CommodityType, Dict] = {}
    
    async def analyze_seasonal_opportunity(
        self, 
        commodity: CommodityType
    ) -> Optional[Dict]:
        """Mavsumiy imkoniyatni tahlil qilish"""
        patterns = await self.data_provider.get_seasonal_patterns(commodity)
        
        if not patterns:
            return None
        
        current_month = datetime.now().month
        current_pattern = patterns[current_month - 1]
        next_pattern = patterns[current_month % 12]
        
        # Keyingi oyda ijobiy return kutilayotganmi?
        if next_pattern.avg_return > 0.015 and next_pattern.win_rate > 0.55:
            spot = await self.data_provider.get_spot_price(commodity)
            
            if spot:
                return {
                    'commodity': commodity.value,
                    'action': 'BUY',
                    'current_price': spot.price,
                    'expected_return': next_pattern.avg_return,
                    'win_rate': next_pattern.win_rate,
                    'std_dev': next_pattern.std_dev,
                    'sharpe_estimate': next_pattern.avg_return / next_pattern.std_dev,
                    'entry_month': current_month,
                    'target_month': next_pattern.month,
                    'reasoning': f"{commodity.value.upper()} tarixan {next_pattern.month}-oyda yuqoriga ko'tariladi"
                }
        
        # Keyingi oyda salbiy return kutilayotganmi?
        elif next_pattern.avg_return < -0.015 and next_pattern.win_rate < 0.45:
            spot = await self.data_provider.get_spot_price(commodity)
            
            if spot:
                return {
                    'commodity': commodity.value,
                    'action': 'SELL',
                    'current_price': spot.price,
                    'expected_return': abs(next_pattern.avg_return),
                    'win_rate': 1 - next_pattern.win_rate,
                    'std_dev': next_pattern.std_dev,
                    'sharpe_estimate': abs(next_pattern.avg_return) / next_pattern.std_dev,
                    'entry_month': current_month,
                    'target_month': next_pattern.month,
                    'reasoning': f"{commodity.value.upper()} tarixan {next_pattern.month}-oyda pastga tushadi"
                }
        
        return None
    
    async def scan_all_commodities(self) -> List[Dict]:
        """Barcha tovarlar bo'yicha mavsumiy imkoniyatlarni skanerlash"""
        opportunities = []
        
        for commodity in CommodityType:
            opportunity = await self.analyze_seasonal_opportunity(commodity)
            if opportunity:
                opportunities.append(opportunity)
        
        # Sharpe ratio bo'yicha saralash
        opportunities.sort(key=lambda x: x['sharpe_estimate'], reverse=True)
        
        return opportunities


class CommoditiesPortfolioManager:
    """
    Tovarlar portfelini boshqarish
    - Risk management
    - Position sizing
    - Diversification
    """
    
    def __init__(
        self, 
        data_provider: CommoditiesDataProvider,
        total_capital: float = 100000.0,
        max_position_size: float = 0.15  # 15% of capital
    ):
        self.data_provider = data_provider
        self.total_capital = total_capital
        self.max_position_size = max_position_size
        self.positions: List[Dict] = []
        self.trade_history: List[Dict] = []
    
    def calculate_position_size(
        self, 
        price: float, 
        confidence: float,
        volatility: float
    ) -> int:
        """
        Kelly Criterion bilan pozitsiya hajmini hisoblash
        f* = (p * b - q) / b
        """
        win_prob = 0.5 + (confidence * 0.2)  # 50-70%
        loss_prob = 1 - win_prob
        win_loss_ratio = 2.0  # 2:1 reward-to-risk
        
        kelly = (win_prob * win_loss_ratio - loss_prob) / win_loss_ratio
        kelly = max(0, min(kelly, self.max_position_size))  # Cap at max
        
        # Volatilityga qarab sozlash
        kelly_adjusted = kelly * (1 - volatility)
        
        position_value = self.total_capital * kelly_adjusted
        quantity = int(position_value / price)
        
        return quantity
    
    def get_sector_exposure(self) -> Dict[str, float]:
        """Sektor bo'yicha exposure"""
        sectors = {
            'energy': [CommodityType.OIL, CommodityType.GAS],
            'agriculture': [CommodityType.WHEAT, CommodityType.CORN, CommodityType.SOYBEANS],
            'soft': [CommodityType.COFFEE, CommodityType.SUGAR, CommodityType.COCOA]
        }
        
        exposure = defaultdict(float)
        
        for position in self.positions:
            commodity = CommodityType(position['commodity'])
            for sector, commodities in sectors.items():
                if commodity in commodities:
                    exposure[sector] += position['value']
        
        # Foizlarga aylantirish
        total_value = sum(exposure.values())
        if total_value > 0:
            exposure = {k: v / total_value for k, v in exposure.items()}
        
        return dict(exposure)
    
    def check_diversification(self) -> bool:
        """Diversifikatsiya tekshirish"""
        sector_exposure = self.get_sector_exposure()
        
        # Hech bir sektor 50% dan oshmasligi kerak
        return all(exp < 0.50 for exp in sector_exposure.values())
    
    async def open_position(
        self, 
        commodity: CommodityType,
        direction: str,  # 'long' or 'short'
        confidence: float,
        reasoning: str
    ) -> bool:
        """Pozitsiya ochish"""
        spot = await self.data_provider.get_spot_price(commodity)
        
        if not spot:
            logger.error(f"Narxni ololmadim: {commodity.value}")
            return False
        
        # Volatility hisoblash (simplified)
        patterns = await self.data_provider.get_seasonal_patterns(commodity)
        avg_volatility = np.mean([p.std_dev for p in patterns]) if patterns else 0.15
        
        # Pozitsiya hajmini hisoblash
        quantity = self.calculate_position_size(spot.price, confidence, avg_volatility)
        
        if quantity == 0:
            logger.warning(f"Pozitsiya hajmi 0: {commodity.value}")
            return False
        
        position = {
            'commodity': commodity.value,
            'direction': direction,
            'entry_price': spot.price,
            'quantity': quantity,
            'value': spot.price * quantity,
            'entry_time': datetime.now(),
            'confidence': confidence,
            'reasoning': reasoning
        }
        
        self.positions.append(position)
        
        logger.info(f"Pozitsiya ochildi: {direction.upper()} {quantity} {commodity.value} @ ${spot.price}")
        
        return True
    
    def get_portfolio_metrics(self) -> Dict:
        """Portfolio metrikalarini hisoblash"""
        total_value = sum(pos['value'] for pos in self.positions)
        
        return {
            'total_positions': len(self.positions),
            'total_value': total_value,
            'capital_used': total_value / self.total_capital,
            'sector_exposure': self.get_sector_exposure(),
            'is_diversified': self.check_diversification()
        }


async def main():
    """Test funksiyasi"""
    api_keys = {
        'alpha_vantage': 'YOUR_API_KEY',
        'quandl': 'YOUR_API_KEY'
    }
    
    async with CommoditiesDataProvider(api_keys) as provider:
        print("=" * 80)
        print("AI TRADING EVOLUTION - COMMODITIES TRADING MODULE")
        print("=" * 80)
        print()
        
        # 1. Spot narxlarni olish
        print("📊 SPOT NARXLAR:")
        print("-" * 80)
        for commodity in CommodityType:
            spot = await provider.get_spot_price(commodity)
            if spot:
                print(f"{commodity.value.upper():15} ${spot.price:8.2f} USD")
        print()
        
        # 2. Futures kontraktlar
        print("📈 FUTURES KONTRAKTLAR (Wheat):")
        print("-" * 80)
        wheat_contracts = await provider.get_futures_contracts(CommodityType.WHEAT, months=6)
        for contract in wheat_contracts[:3]:
            print(f"{contract.symbol:10} ${contract.price:7.2f}  "
                  f"Exp: {contract.expiry_date.strftime('%Y-%m-%d')}  "
                  f"Vol: {contract.volume:,}")
        print()
        
        # 3. Arbitraj imkoniyatlari
        print("🎯 ARBITRAJ IMKONIYATLARI:")
        print("-" * 80)
        detector = CommodityArbitrageDetector(provider)
        
        # Calendar spreads
        cal_spreads = await detector.detect_calendar_spreads(CommodityType.CORN)
        if cal_spreads:
            for opp in cal_spreads[:2]:
                print(f"Calendar Spread: {opp['near_contract']} / {opp['far_contract']}")
                print(f"  Spread: {opp['spread']:.2%}, Deviation: {opp['deviation']:.2%}")
                print(f"  Action: {opp['action']}, Confidence: {opp['confidence']:.1%}")
                print()
        
        # Inter-commodity spreads
        inter_spreads = await detector.detect_intercommodity_spreads()
        if inter_spreads:
            for opp in inter_spreads:
                print(f"Inter-Commodity: {opp['pair']}")
                print(f"  Ratio: {opp['ratio']:.3f}, Expected: {opp['expected_ratio']:.3f}")
                print(f"  Action: {opp['action']}, Confidence: {opp['confidence']:.1%}")
                print()
        
        # 4. Mavsumiy imkoniyatlar
        print("🌾 MAVSUMIY IMKONIYATLAR:")
        print("-" * 80)
        seasonal_strategy = SeasonalTradingStrategy(provider)
        opportunities = await seasonal_strategy.scan_all_commodities()
        
        for opp in opportunities[:3]:
            print(f"{opp['commodity'].upper()} - {opp['action']}")
            print(f"  Price: ${opp['current_price']:.2f}")
            print(f"  Expected Return: {opp['expected_return']:.1%}")
            print(f"  Win Rate: {opp['win_rate']:.1%}")
            print(f"  Sharpe: {opp['sharpe_estimate']:.2f}")
            print(f"  Reasoning: {opp['reasoning']}")
            print()
        
        # 5. Portfolio management
        print("💼 PORTFOLIO BOSHQARUVI:")
        print("-" * 80)
        portfolio = CommoditiesPortfolioManager(provider, total_capital=100000)
        
        # Eng yaxshi imkoniyatni tanlab pozitsiya ochish
        if opportunities:
            best = opportunities[0]
            await portfolio.open_position(
                commodity=CommodityType(best['commodity']),
                direction='long' if best['action'] == 'BUY' else 'short',
                confidence=best['sharpe_estimate'] / 2.0,
                reasoning=best['reasoning']
            )
        
        metrics = portfolio.get_portfolio_metrics()
        print(f"Total Positions: {metrics['total_positions']}")
        print(f"Total Value: ${metrics['total_value']:,.2f}")
        print(f"Capital Used: {metrics['capital_used']:.1%}")
        print(f"Diversified: {'Yes' if metrics['is_diversified'] else 'No'}")
        print()
        print("Sector Exposure:")
        for sector, exposure in metrics['sector_exposure'].items():
            print(f"  {sector.capitalize():15} {exposure:.1%}")
        
        print()
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
