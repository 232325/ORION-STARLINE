"""
AI Trading Evolution - Bonds & Treasury Module
==============================================

Government bonds va corporate bonds savdosi:
- US Treasury bonds (T-Bills, T-Notes, T-Bonds)
- Corporate bonds (Investment grade, High yield)
- Yield curve analysis
- Credit spread analysis
- Duration va convexity
- Bond arbitrage strategies
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BondType(Enum):
    """Bond turlari"""
    T_BILL = "treasury_bill"  # < 1 yil
    T_NOTE = "treasury_note"  # 2-10 yil
    T_BOND = "treasury_bond"  # 20-30 yil
    CORPORATE_IG = "corporate_investment_grade"  # BBB+ va yuqori
    CORPORATE_HY = "corporate_high_yield"  # BB+ va past (Junk bonds)
    MUNICIPAL = "municipal"  # Tax-free
    TIPS = "treasury_inflation_protected"  # Inflation-protected


class CreditRating(Enum):
    """Kredit reytingi"""
    AAA = ("AAA", 1)
    AA = ("AA", 2)
    A = ("A", 3)
    BBB = ("BBB", 4)  # Investment grade minimum
    BB = ("BB", 5)  # High yield start
    B = ("B", 6)
    CCC = ("CCC", 7)
    CC = ("CC", 8)
    C = ("C", 9)
    D = ("D", 10)  # Default
    
    def __init__(self, label: str, risk_level: int):
        self.label = label
        self.risk_level = risk_level
    
    @property
    def is_investment_grade(self) -> bool:
        return self.risk_level <= 4


@dataclass
class BondQuote:
    """Bond narx ma'lumotlari"""
    isin: str  # International Securities Identification Number
    bond_type: BondType
    issuer: str
    coupon_rate: float  # Yillik foiz
    maturity_date: datetime
    face_value: float  # Par value (odatda 1000)
    price: float  # Market price (% of par)
    yield_to_maturity: float  # YTM
    duration: float  # Macaulay duration
    credit_rating: CreditRating
    bid: float
    ask: float
    volume: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def spread(self) -> float:
        """Bid-Ask spread"""
        return self.ask - self.bid
    
    @property
    def years_to_maturity(self) -> float:
        """Muddati tugashiga qolgan yillar"""
        days = (self.maturity_date - datetime.now()).days
        return days / 365.25
    
    @property
    def current_yield(self) -> float:
        """Joriy yield (coupon / price)"""
        market_price = self.face_value * (self.price / 100)
        annual_coupon = self.face_value * (self.coupon_rate / 100)
        return (annual_coupon / market_price) * 100 if market_price > 0 else 0
    
    @property
    def accrued_interest(self) -> float:
        """To'plangan foiz"""
        # Simplification: 30 kunlik accrual
        annual_coupon = self.face_value * (self.coupon_rate / 100)
        daily_interest = annual_coupon / 365
        return daily_interest * 30  # 1 oylik


@dataclass
class YieldCurvePoint:
    """Yield curve nuqtasi"""
    maturity_years: float
    yield_rate: float
    bond_type: BondType
    timestamp: datetime = field(default_factory=datetime.now)


class BondsDataProvider:
    """
    Bonds uchun ma'lumot provayderi
    Real API'lar: FRED, Treasury Direct, Bloomberg, FINRA
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Tuple[datetime, any]] = {}
        self.cache_ttl = 300  # 5 minut (bonds kam o'zgaradi)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Kesh validligi"""
        if key not in self.cache:
            return False
        timestamp, _ = self.cache[key]
        return (datetime.now() - timestamp).seconds < self.cache_ttl
    
    async def get_treasury_yield_curve(self) -> List[YieldCurvePoint]:
        """US Treasury yield curve"""
        cache_key = "treasury_yield_curve"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            # FRED API orqali olish mumkin
            # https://fred.stlouisfed.org/
            
            # Demo data - normal yield curve (upward sloping)
            maturities = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
            
            # Base rates with slight upward curve
            base_rate = 4.5
            curve_points = []
            
            for maturity in maturities:
                # Yield increases with maturity (normal curve)
                # Add term premium: sqrt(maturity) * 0.5%
                term_premium = np.sqrt(maturity) * 0.5
                yield_rate = base_rate + term_premium + np.random.normal(0, 0.05)
                
                bond_type = BondType.T_BILL if maturity < 1 else \
                           BondType.T_NOTE if maturity <= 10 else \
                           BondType.T_BOND
                
                point = YieldCurvePoint(
                    maturity_years=maturity,
                    yield_rate=yield_rate,
                    bond_type=bond_type
                )
                curve_points.append(point)
            
            self.cache[cache_key] = (datetime.now(), curve_points)
            return curve_points
            
        except Exception as e:
            logger.error(f"Yield curve olishda xato: {e}")
            return []
    
    async def get_bond_quote(
        self, 
        isin: str,
        bond_type: BondType
    ) -> Optional[BondQuote]:
        """Bond quote olish"""
        cache_key = f"bond_{isin}"
        
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        
        try:
            # Demo bond data
            if bond_type == BondType.T_BILL:
                coupon = 0  # T-Bills - zero coupon
                maturity_months = np.random.randint(3, 12)
                credit_rating = CreditRating.AAA
                ytm = 4.5 + np.random.uniform(-0.2, 0.2)
            elif bond_type == BondType.T_NOTE:
                coupon = 4.0 + np.random.uniform(-0.5, 0.5)
                maturity_months = np.random.randint(24, 120)
                credit_rating = CreditRating.AAA
                ytm = 4.8 + np.random.uniform(-0.3, 0.3)
            elif bond_type == BondType.T_BOND:
                coupon = 4.5 + np.random.uniform(-0.5, 0.5)
                maturity_months = np.random.randint(240, 360)
                credit_rating = CreditRating.AAA
                ytm = 5.2 + np.random.uniform(-0.3, 0.3)
            elif bond_type == BondType.CORPORATE_IG:
                coupon = 5.5 + np.random.uniform(-1.0, 1.0)
                maturity_months = np.random.randint(24, 120)
                credit_rating = np.random.choice([CreditRating.AAA, CreditRating.AA, CreditRating.A, CreditRating.BBB])
                ytm = 6.0 + np.random.uniform(-0.5, 0.5)
            else:  # High Yield
                coupon = 8.0 + np.random.uniform(-2.0, 2.0)
                maturity_months = np.random.randint(12, 84)
                credit_rating = np.random.choice([CreditRating.BB, CreditRating.B, CreditRating.CCC])
                ytm = 9.5 + np.random.uniform(-1.0, 1.0)
            
            maturity_date = datetime.now() + timedelta(days=maturity_months * 30)
            years_to_maturity = maturity_months / 12
            
            # Price calculation (simplified)
            # Price inversely related to YTM
            if coupon > 0:
                # Premium/Discount based on coupon vs YTM
                price = 100 + (coupon - ytm) * years_to_maturity * 10
            else:
                # Zero coupon: discount
                price = 100 / ((1 + ytm/100) ** years_to_maturity)
            
            price = max(70, min(130, price))  # Clamp
            
            # Duration (simplified Macaulay)
            duration = years_to_maturity * 0.85
            
            quote = BondQuote(
                isin=isin,
                bond_type=bond_type,
                issuer="US Treasury" if bond_type in [BondType.T_BILL, BondType.T_NOTE, BondType.T_BOND] else "Corporate",
                coupon_rate=coupon,
                maturity_date=maturity_date,
                face_value=1000,
                price=price,
                yield_to_maturity=ytm,
                duration=duration,
                credit_rating=credit_rating,
                bid=price - 0.05,
                ask=price + 0.05,
                volume=np.random.randint(100, 10000)
            )
            
            self.cache[cache_key] = (datetime.now(), quote)
            return quote
            
        except Exception as e:
            logger.error(f"Bond quote olishda xato ({isin}): {e}")
            return None
    
    async def get_credit_spread(
        self,
        credit_rating: CreditRating,
        maturity_years: float
    ) -> float:
        """Kredit spreadi hisoblash (vs Treasury)"""
        # Treasury yield
        yield_curve = await self.get_treasury_yield_curve()
        
        # Closest maturity
        closest_point = min(yield_curve, key=lambda p: abs(p.maturity_years - maturity_years))
        treasury_yield = closest_point.yield_rate
        
        # Credit spread based on rating
        spread_map = {
            CreditRating.AAA: 0.3,
            CreditRating.AA: 0.5,
            CreditRating.A: 0.8,
            CreditRating.BBB: 1.5,
            CreditRating.BB: 3.0,
            CreditRating.B: 5.0,
            CreditRating.CCC: 8.0,
            CreditRating.CC: 12.0,
            CreditRating.C: 15.0,
            CreditRating.D: 20.0
        }
        
        base_spread = spread_map.get(credit_rating, 2.0)
        
        # Maturity premium (uzoqroq - ko'proq spread)
        maturity_premium = np.sqrt(maturity_years) * 0.2
        
        total_spread = base_spread + maturity_premium
        
        return total_spread


class YieldCurveAnalyzer:
    """
    Yield curve tahlili
    - Shape analysis (normal, inverted, flat, humped)
    - Steepness
    - Trading strategies
    """
    
    def __init__(self, data_provider: BondsDataProvider):
        self.data_provider = data_provider
    
    async def analyze_curve_shape(self) -> Dict[str, any]:
        """Yield curve shaklini tahlil qilish"""
        curve = await self.data_provider.get_treasury_yield_curve()
        
        if len(curve) < 3:
            return {}
        
        # Key points
        short_term = next((p for p in curve if p.maturity_years <= 1), curve[0])
        medium_term = next((p for p in curve if 5 <= p.maturity_years <= 7), curve[len(curve)//2])
        long_term = next((p for p in curve if p.maturity_years >= 20), curve[-1])
        
        # Calculate slopes
        short_medium_slope = medium_term.yield_rate - short_term.yield_rate
        medium_long_slope = long_term.yield_rate - medium_term.yield_rate
        overall_slope = long_term.yield_rate - short_term.yield_rate
        
        # Determine shape
        if overall_slope > 1.0:
            shape = "STEEP_NORMAL"
            interpretation = "Kuchli iqtisodiy o'sish kutilmoqda"
        elif 0.2 < overall_slope <= 1.0:
            shape = "NORMAL"
            interpretation = "O'rtacha iqtisodiy o'sish"
        elif -0.2 <= overall_slope <= 0.2:
            shape = "FLAT"
            interpretation = "Noaniqlik, o'tish davri"
        elif overall_slope < -0.2:
            shape = "INVERTED"
            interpretation = "⚠️ Retsessiya signali!"
        else:
            shape = "UNKNOWN"
            interpretation = "Noma'lum holat"
        
        # Humped check
        is_humped = medium_term.yield_rate > short_term.yield_rate and \
                   medium_term.yield_rate > long_term.yield_rate
        
        if is_humped:
            shape = "HUMPED"
            interpretation = "O'rta muddatda yuqori foizlar"
        
        return {
            'shape': shape,
            'interpretation': interpretation,
            'short_rate': short_term.yield_rate,
            'medium_rate': medium_term.yield_rate,
            'long_rate': long_term.yield_rate,
            'overall_slope': overall_slope,
            'short_medium_slope': short_medium_slope,
            'medium_long_slope': medium_long_slope,
            'is_humped': is_humped
        }
    
    async def detect_curve_trading_opportunities(self) -> List[Dict]:
        """Yield curve arbitraj imkoniyatlari"""
        analysis = await self.analyze_curve_shape()
        opportunities = []
        
        if not analysis:
            return []
        
        shape = analysis['shape']
        
        # Steep curve: Barbell strategy
        if shape == "STEEP_NORMAL":
            opportunities.append({
                'strategy': 'BARBELL',
                'description': 'Qisqa va uzoq muddatli bondlar, o\'rta muddatni chetlab o\'tish',
                'rationale': 'Steep curve da barbell yuqori return beradi',
                'action': 'Buy short-term + long-term bonds, avoid medium-term',
                'confidence': 0.75
            })
        
        # Flat curve: Bullet strategy
        elif shape == "FLAT":
            opportunities.append({
                'strategy': 'BULLET',
                'description': 'O\'rta muddatli bondlarga fokus',
                'rationale': 'Flat curve da medium maturity optimal',
                'action': 'Concentrate in medium-term bonds (5-7 years)',
                'confidence': 0.70
            })
        
        # Inverted curve: Go short duration
        elif shape == "INVERTED":
            opportunities.append({
                'strategy': 'SHORT_DURATION',
                'description': 'Qisqa muddatli bondlar, foiz tushishi kutilmoqda',
                'rationale': 'Inverted curve - retsessiya va foiz pasayishi signali',
                'action': 'Buy short-term bonds, sell long-term',
                'confidence': 0.85
            })
        
        # Steepening/Flattening trades
        slope = analysis['overall_slope']
        
        if slope > 1.5:
            opportunities.append({
                'strategy': 'CURVE_FLATTENING',
                'description': 'Curve tekislanishini kutish',
                'rationale': 'Juda tik curve odatda tekislanadi',
                'action': 'Long short-term bonds, Short long-term bonds',
                'confidence': 0.65
            })
        elif 0 < slope < 0.3:
            opportunities.append({
                'strategy': 'CURVE_STEEPENING',
                'description': 'Curve tiklashishini kutish',
                'rationale': 'Flat curve odatda tiklashadi',
                'action': 'Short short-term bonds, Long long-term bonds',
                'confidence': 0.60
            })
        
        return opportunities


class CorporateBondAnalyzer:
    """
    Corporate bonds tahlili
    - Credit spread analysis
    - Default probability
    - Relative value
    """
    
    def __init__(self, data_provider: BondsDataProvider):
        self.data_provider = data_provider
    
    async def analyze_credit_spread(
        self,
        bond: BondQuote
    ) -> Dict[str, any]:
        """Kredit spreadini tahlil qilish"""
        # Treasury comparable yield
        maturity = bond.years_to_maturity
        expected_spread = await self.data_provider.get_credit_spread(
            bond.credit_rating, 
            maturity
        )
        
        # Yield curve dan treasury yield
        yield_curve = await self.data_provider.get_treasury_yield_curve()
        closest_point = min(yield_curve, key=lambda p: abs(p.maturity_years - maturity))
        treasury_yield = closest_point.yield_rate
        
        # Actual spread
        actual_spread = bond.yield_to_maturity - treasury_yield
        
        # Z-score (historical average dan qancha farq)
        spread_deviation = actual_spread - expected_spread
        spread_std = expected_spread * 0.2  # Assumed 20% std
        z_score = spread_deviation / spread_std if spread_std > 0 else 0
        
        # Interpretation
        if z_score > 2:
            signal = "WIDE"
            action = "BUY"
            interpretation = "Spread haddan tashqari keng - xarid imkoniyati"
        elif z_score < -2:
            signal = "TIGHT"
            action = "SELL"
            interpretation = "Spread haddan tashqari tor - sotuv imkoniyati"
        else:
            signal = "FAIR"
            action = "HOLD"
            interpretation = "Spread normal darajada"
        
        return {
            'bond': bond.isin,
            'issuer': bond.issuer,
            'credit_rating': bond.credit_rating.label,
            'treasury_yield': treasury_yield,
            'bond_yield': bond.yield_to_maturity,
            'actual_spread': actual_spread,
            'expected_spread': expected_spread,
            'spread_deviation': spread_deviation,
            'z_score': z_score,
            'signal': signal,
            'action': action,
            'interpretation': interpretation,
            'confidence': min(abs(z_score) / 3.0, 1.0)
        }
    
    async def estimate_default_probability(
        self,
        bond: BondQuote
    ) -> float:
        """Default ehtimolini hisoblash (Merton model simplification)"""
        # Credit spread-based estimate
        maturity = bond.years_to_maturity
        
        # Yield curve
        yield_curve = await self.data_provider.get_treasury_yield_curve()
        closest = min(yield_curve, key=lambda p: abs(p.maturity_years - maturity))
        treasury_yield = closest.yield_rate
        
        # Spread
        spread = bond.yield_to_maturity - treasury_yield
        
        # Default probability approximation
        # spread ≈ default_prob * loss_given_default
        # Assuming 40% recovery rate (60% loss given default)
        loss_given_default = 0.60
        
        default_prob = (spread / 100) / loss_given_default
        default_prob = max(0, min(default_prob, 1.0))  # Clamp 0-1
        
        return default_prob
    
    async def find_relative_value(
        self,
        bonds: List[BondQuote]
    ) -> List[Dict]:
        """Relative value - qaysi bond undervalued/overvalued"""
        results = []
        
        for bond in bonds:
            analysis = await self.analyze_credit_spread(bond)
            default_prob = await self.estimate_default_probability(bond)
            
            # Value score: high yield + tight spread + low default prob = good value
            yield_score = bond.yield_to_maturity / 10  # Normalize
            spread_score = 1 - abs(analysis['z_score']) / 3  # Normalized
            credit_score = 1 - default_prob
            
            value_score = (yield_score * 0.4 + spread_score * 0.3 + credit_score * 0.3)
            
            results.append({
                'bond': bond.isin,
                'issuer': bond.issuer,
                'rating': bond.credit_rating.label,
                'yield': bond.yield_to_maturity,
                'price': bond.price,
                'maturity_years': bond.years_to_maturity,
                'spread_analysis': analysis,
                'default_probability': default_prob,
                'value_score': value_score,
                'recommendation': 'BUY' if value_score > 0.7 else 'SELL' if value_score < 0.4 else 'HOLD'
            })
        
        # Sort by value score
        results.sort(key=lambda x: x['value_score'], reverse=True)
        return results


class BondArbitrageStrategy:
    """
    Bond arbitrage strategiyalari
    - Cash-futures arbitrage
    - On-the-run / Off-the-run arbitrage
    - Butterfly spreads
    """
    
    def __init__(self, data_provider: BondsDataProvider):
        self.data_provider = data_provider
    
    async def detect_butterfly_opportunities(self) -> List[Dict]:
        """
        Butterfly spread: short + long vs medium
        Profit from curve shape changes
        """
        curve = await self.data_provider.get_treasury_yield_curve()
        
        if len(curve) < 5:
            return []
        
        opportunities = []
        
        # Try different butterfly combinations
        # Short: 2yr, Medium: 5yr, Long: 10yr
        short = next((p for p in curve if abs(p.maturity_years - 2) < 0.5), None)
        medium = next((p for p in curve if abs(p.maturity_years - 5) < 0.5), None)
        long = next((p for p in curve if abs(p.maturity_years - 10) < 0.5), None)
        
        if short and medium and long:
            # Butterfly spread calculation
            butterfly = medium.yield_rate - (short.yield_rate + long.yield_rate) / 2
            
            # Positive butterfly: medium higher than average (humped)
            # Negative butterfly: medium lower than average (steep/flat)
            
            if abs(butterfly) > 0.15:  # Significant deviation
                if butterfly > 0.15:
                    opportunity = {
                        'type': 'BUTTERFLY',
                        'combination': '2s-5s-10s',
                        'butterfly_value': butterfly,
                        'action': 'SELL_BUTTERFLY',
                        'description': 'Short 5yr, Long 2yr + 10yr',
                        'rationale': 'Curve humped, bet on normalization',
                        'confidence': min(abs(butterfly) / 0.3, 1.0)
                    }
                else:
                    opportunity = {
                        'type': 'BUTTERFLY',
                        'combination': '2s-5s-10s',
                        'butterfly_value': butterfly,
                        'action': 'BUY_BUTTERFLY',
                        'description': 'Long 5yr, Short 2yr + 10yr',
                        'rationale': 'Curve too flat/steep, bet on humping',
                        'confidence': min(abs(butterfly) / 0.3, 1.0)
                    }
                
                opportunities.append(opportunity)
        
        return opportunities


class BondPortfolioManager:
    """
    Bond portfolio boshqaruvi
    - Duration matching
    - Immunization
    - Ladder strategy
    """
    
    def __init__(
        self,
        data_provider: BondsDataProvider,
        total_capital: float = 1000000
    ):
        self.data_provider = data_provider
        self.total_capital = total_capital
        self.holdings: List[Dict] = []
    
    def calculate_portfolio_duration(self) -> float:
        """Portfolio duratsiyasini hisoblash"""
        if not self.holdings:
            return 0.0
        
        total_value = sum(h['value'] for h in self.holdings)
        
        if total_value == 0:
            return 0.0
        
        weighted_duration = sum(
            h['duration'] * h['value'] / total_value 
            for h in self.holdings
        )
        
        return weighted_duration
    
    def calculate_portfolio_yield(self) -> float:
        """Portfolio yieldini hisoblash"""
        if not self.holdings:
            return 0.0
        
        total_value = sum(h['value'] for h in self.holdings)
        
        if total_value == 0:
            return 0.0
        
        weighted_yield = sum(
            h['yield'] * h['value'] / total_value 
            for h in self.holdings
        )
        
        return weighted_yield
    
    async def build_ladder_portfolio(
        self,
        bond_type: BondType,
        num_rungs: int = 5
    ) -> List[Dict]:
        """
        Ladder strategiyasi: turli muddatli bondlarni teng taqsimlash
        Muntazam cash flow va reinvestment risk kamayishi
        """
        allocation_per_rung = self.total_capital / num_rungs
        
        ladder = []
        
        for i in range(1, num_rungs + 1):
            # Generate bond for each maturity
            isin = f"US{bond_type.value.upper()}{i}Y"
            bond = await self.data_provider.get_bond_quote(isin, bond_type)
            
            if bond:
                quantity = int(allocation_per_rung / (bond.face_value * bond.price / 100))
                value = quantity * bond.face_value * (bond.price / 100)
                
                rung = {
                    'maturity_year': i,
                    'bond': bond.isin,
                    'quantity': quantity,
                    'value': value,
                    'yield': bond.yield_to_maturity,
                    'duration': bond.duration
                }
                
                ladder.append(rung)
        
        return ladder
    
    def get_portfolio_metrics(self) -> Dict:
        """Portfolio metrikalarini olish"""
        return {
            'total_value': sum(h['value'] for h in self.holdings),
            'num_holdings': len(self.holdings),
            'avg_duration': self.calculate_portfolio_duration(),
            'portfolio_yield': self.calculate_portfolio_yield(),
            'capital_deployed': sum(h['value'] for h in self.holdings) / self.total_capital
        }


async def main():
    """Test funksiyasi"""
    api_keys = {
        'fred': 'YOUR_API_KEY'
    }
    
    async with BondsDataProvider(api_keys) as provider:
        print("=" * 80)
        print("AI TRADING EVOLUTION - BONDS & TREASURY MODULE")
        print("=" * 80)
        print()
        
        # 1. Yield Curve
        print("📈 US TREASURY YIELD CURVE:")
        print("-" * 80)
        curve = await provider.get_treasury_yield_curve()
        
        for point in curve:
            maturity_str = f"{point.maturity_years:.2f}Y" if point.maturity_years >= 1 else f"{int(point.maturity_years*12)}M"
            print(f"{maturity_str:8} {point.yield_rate:6.2f}%")
        print()
        
        # 2. Yield Curve Analysis
        print("🔍 YIELD CURVE TAHLILI:")
        print("-" * 80)
        analyzer = YieldCurveAnalyzer(provider)
        curve_analysis = await analyzer.analyze_curve_shape()
        
        print(f"Shakl: {curve_analysis['shape']}")
        print(f"Talqin: {curve_analysis['interpretation']}")
        print(f"Short: {curve_analysis['short_rate']:.2f}%")
        print(f"Medium: {curve_analysis['medium_rate']:.2f}%")
        print(f"Long: {curve_analysis['long_rate']:.2f}%")
        print(f"Slope: {curve_analysis['overall_slope']:.2f}%")
        print()
        
        # 3. Yield Curve Trading
        print("💡 YIELD CURVE TRADING STRATEGIYALARI:")
        print("-" * 80)
        opportunities = await analyzer.detect_curve_trading_opportunities()
        
        for opp in opportunities:
            print(f"Strategy: {opp['strategy']}")
            print(f"  {opp['description']}")
            print(f"  Rationale: {opp['rationale']}")
            print(f"  Action: {opp['action']}")
            print(f"  Confidence: {opp['confidence']:.1%}")
            print()
        
        # 4. Corporate Bonds
        print("🏢 CORPORATE BONDS TAHLILI:")
        print("-" * 80)
        
        # Generate sample corporate bonds
        corp_bonds = []
        for i in range(3):
            isin = f"CORP{i+1}"
            bond = await provider.get_bond_quote(
                isin, 
                BondType.CORPORATE_IG if i < 2 else BondType.CORPORATE_HY
            )
            if bond:
                corp_bonds.append(bond)
        
        corp_analyzer = CorporateBondAnalyzer(provider)
        relative_values = await corp_analyzer.find_relative_value(corp_bonds)
        
        for i, rv in enumerate(relative_values, 1):
            print(f"{i}. {rv['issuer']} - {rv['rating']}")
            print(f"   Yield: {rv['yield']:.2f}%, Price: {rv['price']:.2f}")
            print(f"   Default Prob: {rv['default_probability']:.1%}")
            print(f"   Value Score: {rv['value_score']:.2f}")
            print(f"   Recommendation: {rv['recommendation']}")
            print()
        
        # 5. Portfolio Management
        print("💼 BOND PORTFOLIO - LADDER STRATEGIYASI:")
        print("-" * 80)
        portfolio = BondPortfolioManager(provider, total_capital=1000000)
        
        ladder = await portfolio.build_ladder_portfolio(BondType.T_NOTE, num_rungs=5)
        
        for rung in ladder:
            print(f"{rung['maturity_year']}Y: ${rung['value']:,.0f}  "
                  f"Yield: {rung['yield']:.2f}%  "
                  f"Duration: {rung['duration']:.1f}")
        
        print()
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
