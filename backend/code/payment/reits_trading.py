"""
REITs Trading System
Real Estate Investment Trusts savdo tizimi

Xususiyatlar:
- REIT kategoriyalari (10 ta kategoriya)
- Dividend tracking va yield analysis
- Property type diversification
- Portfolio management
- Market data va analysis
- Dividend processing
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
from enum import Enum
from dataclasses import dataclass, field
import random
import logging
from decimal import Decimal
import json

# Logger konfiguratsiyasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class REITCategory(Enum):
    """REIT kategoriyalari"""
    RESIDENTIAL = "residential"  # Turar-joy
    COMMERCIAL = "commercial"    # Tijoriy
    INDUSTRIAL = "industrial"    # Sanoat
    RETAIL = "retail"            # Chakana savdo
    OFFICE = "office"            # Ofis binolari
    HEALTHCARE = "healthcare"    # Sog'liqni saqlash
    HOTEL = "hotel"              # Mehmonxonalar
    DATA_CENTER = "data_center"  # Data centers
    STORAGE = "storage"          # Storage facilities
    DIVERSIFIED = "diversified"  # Aralash


class REITType(Enum):
    """REIT turlari"""
    EQUITY = "equity"              # Mulkka egalik qiluvchi
    MORTGAGE = "mortgage"          # Mortgage lending
    HYBRID = "hybrid"              # Equity + Mortgage


@dataclass
class DividendInfo:
    """Dividend ma'lumotlari"""
    amount: Decimal
    frequency: str  # monthly, quarterly, annual
    yield_rate: Decimal
    payout_ratio: Decimal
    last_payment_date: datetime
    next_payment_date: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": str(self.amount),
            "frequency": self.frequency,
            "yield_rate": str(self.yield_rate),
            "payout_ratio": str(self.payout_ratio),
            "last_payment_date": self.last_payment_date.isoformat(),
            "next_payment_date": self.next_payment_date.isoformat()
        }


@dataclass
class REIT:
    """REIT (Real Estate Investment Trust)"""
    id: str
    name: str
    ticker: str
    category: REITCategory
    reit_type: REITType
    price: Decimal
    market_cap: Decimal
    dividend_info: DividendInfo
    description: str
    properties_count: int
    geographic_focus: List[str]
    ffo_per_share: Decimal  # Funds From Operations
    nav_per_share: Decimal  # Net Asset Value
    occupancy_rate: Decimal
    debt_to_equity: Decimal
    year_founded: int
    
    def get_price_to_nav_ratio(self) -> Decimal:
        """Price/NAV ratio"""
        return self.price / self.nav_per_share if self.nav_per_share > 0 else Decimal("0")
    
    def get_ffo_yield(self) -> Decimal:
        """FFO yield"""
        return (self.ffo_per_share / self.price * Decimal("100")) if self.price > 0 else Decimal("0")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "ticker": self.ticker,
            "category": self.category.value,
            "reit_type": self.reit_type.value,
            "price": str(self.price),
            "market_cap": str(self.market_cap),
            "dividend_info": self.dividend_info.to_dict(),
            "description": self.description,
            "properties_count": self.properties_count,
            "geographic_focus": self.geographic_focus,
            "ffo_per_share": str(self.ffo_per_share),
            "nav_per_share": str(self.nav_per_share),
            "price_to_nav_ratio": str(self.get_price_to_nav_ratio()),
            "ffo_yield": str(self.get_ffo_yield()),
            "occupancy_rate": str(self.occupancy_rate),
            "debt_to_equity": str(self.debt_to_equity),
            "year_founded": self.year_founded
        }


@dataclass
class REITPosition:
    """REIT pozitsiyasi"""
    id: str
    reit_id: str
    reit_ticker: str
    shares: Decimal
    avg_entry_price: Decimal
    current_price: Decimal
    opened_at: datetime
    total_dividends_received: Decimal = Decimal("0")
    
    def get_market_value(self) -> Decimal:
        """Joriy bozor qiymati"""
        return self.shares * self.current_price
    
    def get_cost_basis(self) -> Decimal:
        """Dastlabki investitsiya"""
        return self.shares * self.avg_entry_price
    
    def get_unrealized_pnl(self) -> Decimal:
        """Unrealized PnL"""
        return self.get_market_value() - self.get_cost_basis()
    
    def get_total_return(self) -> Decimal:
        """Total return (capital gains + dividends)"""
        return self.get_unrealized_pnl() + self.total_dividends_received
    
    def get_return_percentage(self) -> Decimal:
        """Return foizi"""
        cost = self.get_cost_basis()
        return (self.get_total_return() / cost * Decimal("100")) if cost > 0 else Decimal("0")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "reit_id": self.reit_id,
            "reit_ticker": self.reit_ticker,
            "shares": str(self.shares),
            "avg_entry_price": str(self.avg_entry_price),
            "current_price": str(self.current_price),
            "market_value": str(self.get_market_value()),
            "cost_basis": str(self.get_cost_basis()),
            "unrealized_pnl": str(self.get_unrealized_pnl()),
            "total_dividends_received": str(self.total_dividends_received),
            "total_return": str(self.get_total_return()),
            "return_percentage": str(self.get_return_percentage()),
            "opened_at": self.opened_at.isoformat()
        }


@dataclass
class DividendPayment:
    """Dividend to'lovi"""
    id: str
    position_id: str
    reit_ticker: str
    amount_per_share: Decimal
    shares: Decimal
    total_amount: Decimal
    payment_date: datetime
    ex_dividend_date: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "position_id": self.position_id,
            "reit_ticker": self.reit_ticker,
            "amount_per_share": str(self.amount_per_share),
            "shares": str(self.shares),
            "total_amount": str(self.total_amount),
            "payment_date": self.payment_date.isoformat(),
            "ex_dividend_date": self.ex_dividend_date.isoformat()
        }


class REITsTrading:
    """
    REITs Trading System
    
    Real Estate Investment Trusts trading va analysis
    """
    
    def __init__(self):
        self.reits: Dict[str, REIT] = {}
        self.positions: Dict[str, REITPosition] = {}
        self.dividend_payments: List[DividendPayment] = []
        
        # Initialize sample REITs
        self._initialize_sample_reits()
        
        logger.info("REITsTrading initialized")
    
    def _initialize_sample_reits(self):
        """Sample REIT ma'lumotlarini yaratish"""
        sample_reits = [
            {
                "name": "American Tower Corporation",
                "ticker": "AMT",
                "category": REITCategory.DATA_CENTER,
                "reit_type": REITType.EQUITY,
                "price": Decimal("195.50"),
                "market_cap": Decimal("90000000000"),
                "description": "Wireless communication infrastructure REIT",
                "properties_count": 220000,
                "geographic_focus": ["USA", "Brazil", "India", "Mexico"],
                "ffo_per_share": Decimal("10.25"),
                "nav_per_share": Decimal("180.00"),
                "occupancy_rate": Decimal("98.5"),
                "debt_to_equity": Decimal("1.85"),
                "year_founded": 1995,
                "dividend_yield": Decimal("2.8")
            },
            {
                "name": "Prologis Inc",
                "ticker": "PLD",
                "category": REITCategory.INDUSTRIAL,
                "reit_type": REITType.EQUITY,
                "price": Decimal("125.80"),
                "market_cap": Decimal("110000000000"),
                "description": "Industrial logistics real estate",
                "properties_count": 4700,
                "geographic_focus": ["USA", "Europe", "Asia"],
                "ffo_per_share": Decimal("5.15"),
                "nav_per_share": Decimal("115.00"),
                "occupancy_rate": Decimal("97.8"),
                "debt_to_equity": Decimal("0.65"),
                "year_founded": 1983,
                "dividend_yield": Decimal("2.5")
            },
            {
                "name": "Equity Residential",
                "ticker": "EQR",
                "category": REITCategory.RESIDENTIAL,
                "reit_type": REITType.EQUITY,
                "price": Decimal("68.90"),
                "market_cap": Decimal("26000000000"),
                "description": "Apartment communities",
                "properties_count": 305,
                "geographic_focus": ["USA"],
                "ffo_per_share": Decimal("3.45"),
                "nav_per_share": Decimal("72.00"),
                "occupancy_rate": Decimal("95.7"),
                "debt_to_equity": Decimal("0.52"),
                "year_founded": 1969,
                "dividend_yield": Decimal("3.5")
            },
            {
                "name": "Simon Property Group",
                "ticker": "SPG",
                "category": REITCategory.RETAIL,
                "reit_type": REITType.EQUITY,
                "price": Decimal("145.20"),
                "market_cap": Decimal("48000000000"),
                "description": "Retail shopping mall operator",
                "properties_count": 204,
                "geographic_focus": ["USA", "Asia", "Europe"],
                "ffo_per_share": Decimal("11.80"),
                "nav_per_share": Decimal("155.00"),
                "occupancy_rate": Decimal("94.5"),
                "debt_to_equity": Decimal("1.25"),
                "year_founded": 1993,
                "dividend_yield": Decimal("5.2")
            },
            {
                "name": "Welltower Inc",
                "ticker": "WELL",
                "category": REITCategory.HEALTHCARE,
                "reit_type": REITType.EQUITY,
                "price": Decimal("92.30"),
                "market_cap": Decimal("44000000000"),
                "description": "Healthcare infrastructure",
                "properties_count": 1400,
                "geographic_focus": ["USA", "Canada", "UK"],
                "ffo_per_share": Decimal("3.85"),
                "nav_per_share": Decimal("88.00"),
                "occupancy_rate": Decimal("91.2"),
                "debt_to_equity": Decimal("0.78"),
                "year_founded": 1970,
                "dividend_yield": Decimal("3.1")
            },
            {
                "name": "Boston Properties",
                "ticker": "BXP",
                "category": REITCategory.OFFICE,
                "reit_type": REITType.EQUITY,
                "price": Decimal("78.50"),
                "market_cap": Decimal("12000000000"),
                "description": "Class A office properties",
                "properties_count": 196,
                "geographic_focus": ["USA"],
                "ffo_per_share": Decimal("6.95"),
                "nav_per_share": Decimal("95.00"),
                "occupancy_rate": Decimal("89.3"),
                "debt_to_equity": Decimal("0.88"),
                "year_founded": 1970,
                "dividend_yield": Decimal("4.8")
            }
        ]
        
        for data in sample_reits:
            import uuid
            
            # Create dividend info
            dividend_amount = data["price"] * data["dividend_yield"] / Decimal("100") / Decimal("4")
            
            dividend_info = DividendInfo(
                amount=dividend_amount,
                frequency="quarterly",
                yield_rate=data["dividend_yield"],
                payout_ratio=Decimal("75.0"),
                last_payment_date=datetime.now() - timedelta(days=30),
                next_payment_date=datetime.now() + timedelta(days=60)
            )
            
            reit = REIT(
                id=f"reit_{uuid.uuid4().hex[:12]}",
                name=data["name"],
                ticker=data["ticker"],
                category=data["category"],
                reit_type=data["reit_type"],
                price=data["price"],
                market_cap=data["market_cap"],
                dividend_info=dividend_info,
                description=data["description"],
                properties_count=data["properties_count"],
                geographic_focus=data["geographic_focus"],
                ffo_per_share=data["ffo_per_share"],
                nav_per_share=data["nav_per_share"],
                occupancy_rate=data["occupancy_rate"],
                debt_to_equity=data["debt_to_equity"],
                year_founded=data["year_founded"]
            )
            
            self.reits[reit.id] = reit
    
    async def get_all_reits(
        self,
        category: Optional[REITCategory] = None,
        min_yield: Optional[Decimal] = None
    ) -> List[REIT]:
        """
        Barcha REITlarni olish
        
        Args:
            category: Filter by category
            min_yield: Minimum dividend yield
        
        Returns:
            REITlar ro'yxati
        """
        reits = list(self.reits.values())
        
        # Filter by category
        if category:
            reits = [r for r in reits if r.category == category]
        
        # Filter by minimum yield
        if min_yield:
            reits = [r for r in reits if r.dividend_info.yield_rate >= min_yield]
        
        # Sort by market cap descending
        reits.sort(key=lambda x: x.market_cap, reverse=True)
        
        return reits
    
    async def get_reit_by_ticker(self, ticker: str) -> Optional[REIT]:
        """Ticker bo'yicha REIT topish"""
        for reit in self.reits.values():
            if reit.ticker == ticker:
                return reit
        return None
    
    async def buy_reit(
        self,
        reit_id: str,
        shares: Decimal,
        price: Optional[Decimal] = None
    ) -> REITPosition:
        """
        REIT sotib olish
        
        Args:
            reit_id: REIT ID
            shares: Shares soni
            price: Narx (None = current price)
        
        Returns:
            Yaratilgan pozitsiya
        """
        import uuid
        
        if reit_id not in self.reits:
            raise ValueError(f"REIT not found: {reit_id}")
        
        reit = self.reits[reit_id]
        entry_price = price if price else reit.price
        
        position = REITPosition(
            id=f"pos_{uuid.uuid4().hex[:16]}",
            reit_id=reit_id,
            reit_ticker=reit.ticker,
            shares=shares,
            avg_entry_price=entry_price,
            current_price=reit.price,
            opened_at=datetime.now()
        )
        
        self.positions[position.id] = position
        
        logger.info(f"REIT position opened: {position.id} - {reit.ticker} {shares} shares @ {entry_price}")
        
        return position
    
    async def sell_reit(
        self,
        position_id: str,
        shares: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        REIT sotish
        
        Args:
            position_id: Pozitsiya ID
            shares: Sotish uchun shares (None = all)
        
        Returns:
            Savdo ma'lumotlari
        """
        if position_id not in self.positions:
            raise ValueError(f"Position not found: {position_id}")
        
        position = self.positions[position_id]
        reit = self.reits[position.reit_id]
        
        sell_shares = shares if shares else position.shares
        
        if sell_shares > position.shares:
            raise ValueError(f"Not enough shares to sell")
        
        # Calculate PnL
        sell_price = reit.price
        cost_basis = sell_shares * position.avg_entry_price
        proceeds = sell_shares * sell_price
        pnl = proceeds - cost_basis
        
        # Update or remove position
        if sell_shares == position.shares:
            # Full sale - remove position
            del self.positions[position_id]
        else:
            # Partial sale - update shares
            position.shares -= sell_shares
        
        sale_data = {
            "position_id": position_id,
            "reit_ticker": reit.ticker,
            "shares_sold": str(sell_shares),
            "sell_price": str(sell_price),
            "cost_basis": str(cost_basis),
            "proceeds": str(proceeds),
            "pnl": str(pnl),
            "sold_at": datetime.now().isoformat()
        }
        
        logger.info(f"REIT sold: {position_id} - {reit.ticker} {sell_shares} shares @ {sell_price} - PnL: {pnl}")
        
        return sale_data
    
    async def get_positions(self) -> List[REITPosition]:
        """Barcha pozitsiyalarni olish"""
        # Update current prices
        for position in self.positions.values():
            if position.reit_id in self.reits:
                reit = self.reits[position.reit_id]
                position.current_price = reit.price
        
        return list(self.positions.values())
    
    async def process_dividends(self) -> List[DividendPayment]:
        """
        Dividendlarni qayta ishlash
        
        Barcha pozitsiyalar uchun dividend to'lovlarini simulyatsiya qilish
        """
        new_payments = []
        
        for position in self.positions.values():
            reit = self.reits[position.reit_id]
            
            # Check if dividend is due (simplified)
            days_since_last = (datetime.now() - reit.dividend_info.last_payment_date).days
            
            if days_since_last >= 30:  # Monthly or quarterly dividend
                import uuid
                
                payment = DividendPayment(
                    id=f"div_{uuid.uuid4().hex[:16]}",
                    position_id=position.id,
                    reit_ticker=reit.ticker,
                    amount_per_share=reit.dividend_info.amount,
                    shares=position.shares,
                    total_amount=reit.dividend_info.amount * position.shares,
                    payment_date=datetime.now(),
                    ex_dividend_date=datetime.now() - timedelta(days=2)
                )
                
                # Add to position's total dividends
                position.total_dividends_received += payment.total_amount
                
                new_payments.append(payment)
                self.dividend_payments.append(payment)
                
                # Update last payment date
                reit.dividend_info.last_payment_date = datetime.now()
                reit.dividend_info.next_payment_date = datetime.now() + timedelta(days=30)
        
        logger.info(f"Processed {len(new_payments)} dividend payments")
        
        return new_payments
    
    async def get_dividend_history(
        self,
        position_id: Optional[str] = None,
        limit: int = 50
    ) -> List[DividendPayment]:
        """Dividend to'lovlari tarixini olish"""
        payments = self.dividend_payments
        
        if position_id:
            payments = [p for p in payments if p.position_id == position_id]
        
        # Sort by payment date descending
        payments.sort(key=lambda x: x.payment_date, reverse=True)
        
        return payments[:limit]
    
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Portfolio xulosasi"""
        positions = await self.get_positions()
        
        if not positions:
            return {
                "total_positions": 0,
                "total_market_value": "0",
                "total_cost_basis": "0",
                "total_unrealized_pnl": "0",
                "total_dividends": "0",
                "total_return": "0",
                "return_percentage": "0"
            }
        
        total_market_value = sum(p.get_market_value() for p in positions)
        total_cost_basis = sum(p.get_cost_basis() for p in positions)
        total_unrealized_pnl = sum(p.get_unrealized_pnl() for p in positions)
        total_dividends = sum(p.total_dividends_received for p in positions)
        total_return = total_unrealized_pnl + total_dividends
        
        return_pct = (total_return / total_cost_basis * Decimal("100")) if total_cost_basis > 0 else Decimal("0")
        
        # Category breakdown
        category_breakdown = {}
        for position in positions:
            reit = self.reits[position.reit_id]
            cat = reit.category.value
            
            if cat not in category_breakdown:
                category_breakdown[cat] = {
                    "positions": 0,
                    "market_value": Decimal("0")
                }
            
            category_breakdown[cat]["positions"] += 1
            category_breakdown[cat]["market_value"] += position.get_market_value()
        
        # Convert to serializable format
        for cat in category_breakdown:
            category_breakdown[cat]["market_value"] = str(category_breakdown[cat]["market_value"])
        
        return {
            "total_positions": len(positions),
            "total_market_value": str(total_market_value),
            "total_cost_basis": str(total_cost_basis),
            "total_unrealized_pnl": str(total_unrealized_pnl),
            "total_dividends": str(total_dividends),
            "total_return": str(total_return),
            "return_percentage": str(return_pct),
            "category_breakdown": category_breakdown,
            "avg_dividend_yield": str(
                sum(self.reits[p.reit_id].dividend_info.yield_rate for p in positions) / len(positions)
            )
        }
    
    async def get_top_reits_by_yield(self, limit: int = 10) -> List[REIT]:
        """Eng yuqori dividend yield bilan REITlar"""
        reits = list(self.reits.values())
        reits.sort(key=lambda x: x.dividend_info.yield_rate, reverse=True)
        return reits[:limit]
    
    async def get_top_reits_by_performance(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Eng yaxshi performance ko'rsatgan REITlar"""
        reits_performance = []
        
        for reit in self.reits.values():
            # Simulate YTD performance
            ytd_return = Decimal(str(random.uniform(-10, 25)))
            
            reits_performance.append({
                "reit": reit.to_dict(),
                "ytd_return": str(ytd_return),
                "total_return_with_dividends": str(ytd_return + reit.dividend_info.yield_rate)
            })
        
        # Sort by total return
        reits_performance.sort(
            key=lambda x: Decimal(x["total_return_with_dividends"]),
            reverse=True
        )
        
        return reits_performance[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """REITs trading statistikasi"""
        total_dividends_paid = sum(
            p.total_amount for p in self.dividend_payments
        )
        
        return {
            "total_reits": len(self.reits),
            "active_positions": len(self.positions),
            "total_dividend_payments": len(self.dividend_payments),
            "total_dividends_paid": str(total_dividends_paid),
            "categories": [cat.value for cat in REITCategory],
            "reit_types": [rt.value for rt in REITType]
        }
    
    # ========== SYNC VERSIONS FOR EASY USAGE ==========
    
    def get_all_reits_sync(
        self,
        category: Optional[REITCategory] = None,
        min_yield: Optional[Decimal] = None
    ) -> List[REIT]:
        """
        Barcha REITlarni olish (sync version)
        
        Args:
            category: Filter by category
            min_yield: Minimum dividend yield
        
        Returns:
            REITlar ro'yxati
        """
        reits = list(self.reits.values())
        
        # Filter by category
        if category:
            reits = [r for r in reits if r.category == category]
        
        # Filter by minimum yield
        if min_yield:
            reits = [r for r in reits if r.dividend_info.yield_rate >= min_yield]
        
        # Sort by market cap descending
        reits.sort(key=lambda x: x.market_cap, reverse=True)
        
        return reits
    
    def buy_reit_sync(
        self,
        reit_id: str,
        shares: Decimal,
        price: Optional[Decimal] = None
    ) -> REITPosition:
        """
        REIT sotib olish (sync version)
        
        Args:
            reit_id: REIT ID
            shares: Shares soni
            price: Narx (None = current price)
        
        Returns:
            Yaratilgan pozitsiya
        """
        import uuid
        
        if reit_id not in self.reits:
            raise ValueError(f"REIT topilmadi: {reit_id}")
        
        reit = self.reits[reit_id]
        entry_price = price if price else reit.price
        
        position = REITPosition(
            id=f"pos_{uuid.uuid4().hex[:16]}",
            reit_id=reit_id,
            reit_ticker=reit.ticker,
            shares=shares,
            avg_entry_price=entry_price,
            current_price=reit.price,
            opened_at=datetime.now()
        )
        
        self.positions[position.id] = position
        
        logger.info(f"REIT pozitsiya ochildi: {position.id} - {reit.ticker} {shares} dona @ ${entry_price}")
        
        return position
    
    def sell_reit_sync(
        self,
        position_id: str,
        shares: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        REIT sotish (sync version)
        
        Args:
            position_id: Pozitsiya ID
            shares: Sotish uchun shares (None = all)
        
        Returns:
            Savdo ma'lumotlari
        """
        if position_id not in self.positions:
            raise ValueError(f"Pozitsiya topilmadi: {position_id}")
        
        position = self.positions[position_id]
        reit = self.reits[position.reit_id]
        
        sell_shares = shares if shares else position.shares
        
        if sell_shares > position.shares:
            raise ValueError(f"Sotish uchun yetarli aksiya yo'q")
        
        # Calculate PnL
        sell_price = reit.price
        cost_basis = sell_shares * position.avg_entry_price
        proceeds = sell_shares * sell_price
        pnl = proceeds - cost_basis
        
        # Update or remove position
        if sell_shares == position.shares:
            # Full sale - remove position
            del self.positions[position_id]
        else:
            # Partial sale - update shares
            position.shares -= sell_shares
        
        sale_data = {
            "position_id": position_id,
            "reit_ticker": reit.ticker,
            "shares_sold": str(sell_shares),
            "sell_price": str(sell_price),
            "cost_basis": str(cost_basis),
            "proceeds": str(proceeds),
            "pnl": str(pnl),
            "sold_at": datetime.now().isoformat()
        }
        
        logger.info(f"REIT sotildi: {position_id} - {reit.ticker} {sell_shares} dona @ ${sell_price} - PnL: ${pnl}")
        
        return sale_data
    
    def process_dividends_sync(self) -> List[DividendPayment]:
        """
        Dividendlarni qayta ishlash (sync version)
        
        Barcha pozitsiyalar uchun dividend to'lovlarini simulyatsiya qilish
        """
        new_payments = []
        
        for position in self.positions.values():
            reit = self.reits[position.reit_id]
            
            # Check if dividend is due (simplified)
            days_since_last = (datetime.now() - reit.dividend_info.last_payment_date).days
            
            if days_since_last >= 30:  # Monthly or quarterly dividend
                import uuid
                
                payment = DividendPayment(
                    id=f"div_{uuid.uuid4().hex[:16]}",
                    position_id=position.id,
                    reit_ticker=reit.ticker,
                    amount_per_share=reit.dividend_info.amount,
                    shares=position.shares,
                    total_amount=reit.dividend_info.amount * position.shares,
                    payment_date=datetime.now(),
                    ex_dividend_date=datetime.now() - timedelta(days=2)
                )
                
                # Add to position's total dividends
                position.total_dividends_received += payment.total_amount
                
                new_payments.append(payment)
                self.dividend_payments.append(payment)
                
                # Update last payment date
                reit.dividend_info.last_payment_date = datetime.now()
                reit.dividend_info.next_payment_date = datetime.now() + timedelta(days=30)
        
        logger.info(f"Dividend to'lovlari qayta ishlandi: {len(new_payments)} ta")
        
        return new_payments
    
    def get_dividend_history_sync(
        self,
        position_id: Optional[str] = None,
        limit: int = 50
    ) -> List[DividendPayment]:
        """
        Dividend to'lovlari tarixini olish (sync version)
        """
        payments = self.dividend_payments
        
        if position_id:
            payments = [p for p in payments if p.position_id == position_id]
        
        # Sort by payment date descending
        payments.sort(key=lambda x: x.payment_date, reverse=True)
        
        return payments[:limit]
    
    def get_portfolio_summary_sync(self) -> Dict[str, Any]:
        """
        Portfolio xulosasi (sync version)
        """
        positions = list(self.positions.values())
        
        # Update current prices
        for position in positions:
            if position.reit_id in self.reits:
                reit = self.reits[position.reit_id]
                position.current_price = reit.price
        
        if not positions:
            return {
                "total_positions": 0,
                "total_market_value": "0.00",
                "total_cost_basis": "0.00",
                "total_unrealized_pnl": "0.00",
                "total_dividends": "0.00",
                "total_return": "0.00",
                "return_percentage": "0.00",
                "dividend_yield": "0.00"
            }
        
        total_market_value = sum(p.get_market_value() for p in positions)
        total_cost_basis = sum(p.get_cost_basis() for p in positions)
        total_unrealized_pnl = sum(p.get_unrealized_pnl() for p in positions)
        total_dividends = sum(p.total_dividends_received for p in positions)
        total_return = total_unrealized_pnl + total_dividends
        
        return_pct = (total_return / total_cost_basis * Decimal("100")) if total_cost_basis > 0 else Decimal("0")
        
        # Category breakdown
        category_breakdown = {}
        for position in positions:
            reit = self.reits[position.reit_id]
            cat = reit.category.value
            
            if cat not in category_breakdown:
                category_breakdown[cat] = {
                    "positions": 0,
                    "market_value": Decimal("0")
                }
            
            category_breakdown[cat]["positions"] += 1
            category_breakdown[cat]["market_value"] += position.get_market_value()
        
        # Convert to serializable format
        for cat in category_breakdown:
            category_breakdown[cat]["market_value"] = str(category_breakdown[cat]["market_value"])
        
        return {
            "total_positions": len(positions),
            "total_market_value": str(round(total_market_value, 2)),
            "total_cost_basis": str(round(total_cost_basis, 2)),
            "total_unrealized_pnl": str(round(total_unrealized_pnl, 2)),
            "total_dividends": str(round(total_dividends, 2)),
            "total_return": str(round(total_return, 2)),
            "return_percentage": str(round(return_pct, 2)),
            "category_breakdown": category_breakdown,
            "avg_dividend_yield": str(
                round(sum(self.reits[p.reit_id].dividend_info.yield_rate for p in positions) / len(positions), 2)
            )
        }


def demo_reits_trading():
    """REITs trading demo"""
    print("=" * 60)
    print("REITs TRADING SYSTEM DEMO")
    print("Real Estate Investment Trusts savdo tizimi")
    print("=" * 60)
    
    # Tizimni boshlash
    reits_system = REITsTrading()
    
    # Bozor ma'lumotlarini ko'rsatish
    print("\n📊 1. Bozor statistikasi:")
    stats = reits_system.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Barcha REITlarni ko'rsatish
    print("\n🏢 2. Mavjud REITlar:")
    all_reits = reits_system.get_all_reits_sync()
    print(f"   Jami: {len(all_reits)} ta REIT")
    
    for i, reit in enumerate(all_reits, 1):
        print(f"   {i}. {reit.ticker} - {reit.name}")
        print(f"      Kategoriya: {reit.category.value}")
        print(f"      Narx: ${reit.price}, Market Cap: ${float(reit.market_cap)/1e9:.1f}B")
        print(f"      Dividend Yield: {reit.dividend_info.yield_rate}%")
        print()
    
    # Eng yaxshi dividend yield
    print("\n💰 3. Eng yuqori dividend yield (3 ta):")
    all_reits_with_yield = sorted(all_reits, key=lambda x: x.dividend_info.yield_rate, reverse=True)
    for reit in all_reits_with_yield[:3]:
        print(f"   {reit.ticker} - {reit.dividend_info.yield_rate}% ({reit.name})")
    
    # Portfolio yaratish
    print("\n💼 4. REIT savdolari:")
    # AMT sotib olish
    amt_reit = next((r for r in all_reits if r.ticker == "AMT"), None)
    if amt_reit:
        position1 = reits_system.buy_reit_sync(amt_reit.id, Decimal("100"))
        print(f"   ✅ AMT sotib olindi: 100 dona @ ${amt_reit.price}")
    else:
        print("   ⚠️ AMT REIT topilmadi")
    
    # PLD sotib olish
    pld_reit = next((r for r in all_reits if r.ticker == "PLD"), None)
    if pld_reit:
        position2 = reits_system.buy_reit_sync(pld_reit.id, Decimal("75"))
        print(f"   ✅ PLD sotib olindi: 75 dona @ ${pld_reit.price}")
    else:
        print("   ⚠️ PLD REIT topilmadi")
    
    # EQR sotib olish
    eqr_reit = next((r for r in all_reits if r.ticker == "EQR"), None)
    if eqr_reit:
        position3 = reits_system.buy_reit_sync(eqr_reit.id, Decimal("200"))
        print(f"   ✅ EQR sotib olindi: 200 dona @ ${eqr_reit.price}")
    else:
        print("   ⚠️ EQR REIT topilmadi")
    
    # Portfolio xulosasi
    print("\n📈 5. Portfolio xulosasi:")
    portfolio = reits_system.get_portfolio_summary_sync()
    print(f"   Jami pozitsiyalar: {portfolio['total_positions']}")
    print(f"   Bozor qiymati: ${portfolio['total_market_value']}")
    print(f"   Dastlabki sarmoya: ${portfolio['total_cost_basis']}")
    print(f"   Unrealized P&L: ${portfolio['total_unrealized_pnl']}")
    print(f"   Dividend daromadi: ${portfolio['total_dividends']}")
    print(f"   Jami return: ${portfolio['total_return']} ({portfolio['return_percentage']}%)")
    print(f"   O'rtacha dividend yield: {portfolio['avg_dividend_yield']}%")
    
    # Kategoriya bo'yicha taqsimot
    print("\n📊 6. Kategoriya bo'yicha taqsimot:")
    for category, data in portfolio['category_breakdown'].items():
        print(f"   {category}: {data['positions']} ta pozitsiya, ${data['market_value']}")
    
    # Dividend qayta ishlash
    print("\n💵 7. Dividend qayta ishlash:")
    new_dividends = reits_system.process_dividends_sync()
    print(f"   Qayta ishlandi: {len(new_dividends)} ta dividend")
    
    for payment in new_dividends:
        print(f"   {payment.reit_ticker}: {payment.shares} dona * ${payment.amount_per_share} = ${payment.total_amount}")
    
    # Dividend tarixi
    print("\n📋 8. Dividend tarixi:")
    dividend_history = reits_system.get_dividend_history_sync()
    if dividend_history:
        for payment in dividend_history[:3]:  # Faqat 3 ta
            print(f"   {payment.reit_ticker}: ${payment.total_amount} ({payment.payment_date.strftime('%Y-%m-%d')})")
    else:
        print("   Hozircha dividend tarixi yo'q")
    
    # Yangi portfolio xulosasi (dividendlar bilan)
    print("\n📊 9. Yangilangan portfolio (dividendlar bilan):")
    updated_portfolio = reits_system.get_portfolio_summary_sync()
    print(f"   Jami return: ${updated_portfolio['total_return']} ({updated_portfolio['return_percentage']}%)")
    
    print("\n✅ Demo yakunlandi!")
    print("=" * 60)


if __name__ == "__main__":
    demo_reits_trading()
