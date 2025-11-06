"""
Strategy Marketplace - Trading strategiyalarni sotish/sotib olish platformasi
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Strategiya turlari"""
    MANUAL = "manual"
    AUTOMATED = "automated"
    HYBRID = "hybrid"
    COPY_TRADING = "copy_trading"
    ALGO_TRADING = "algo_trading"
    QUANTITATIVE = "quantitative"
    AI_POWERED = "ai_powered"
    SCALPING = "scalping"
    SWING_TRADING = "swing_trading"
    POSITION_TRADING = "position_trading"


class StrategyCategory(Enum):
    """Strategiya kategoriyalari"""
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    ARBITRAGE = "arbitrage"
    GRID_TRADING = "grid_trading"
    DCA = "dollar_cost_averaging"
    NEWS_TRADING = "news_trading"
    CRYPTO = "crypto"
    FOREX = "forex"
    STOCKS = "stocks"
    COMMODITIES = "commodities"
    METALS = "metals"
    INDEX_TRADING = "index_trading"
    OPTIONS_TRADING = "options_trading"
    FUTURES_TRADING = "futures_trading"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    RISK_MANAGEMENT = "risk_management"
    MARKET_MAKING = "market_making"
    HIGH_FREQUENCY = "high_frequency"
    SOCIAL_TRADING = "social_trading"
    AI_ML = "ai_ml"
    OTHER = "other"


class PricingModel(Enum):
    """Narxlash modellari"""
    FREE = "free"
    ONE_TIME_PAYMENT = "one_time_payment"
    SUBSCRIPTION_MONTHLY = "subscription_monthly"
    SUBSCRIPTION_YEARLY = "subscription_yearly"
    PERFORMANCE_FEE = "performance_fee"
    REVENUE_SHARE = "revenue_share"
    TIERED_PRICING = "tiered_pricing"
    FREEMIUM = "freemium"
    PROMOTIONAL = "promotional"
    CROWDFUNDED = "crowdfunded"
    # Eski nomlar (orqaga moslik uchun)
    ONE_TIME = "one_time"  # Bir martalik to'lov
    SUBSCRIPTION = "subscription"  # Oylik obuna


class StrategyStatus(Enum):
    """Strategiya statusi"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class Strategy:
    """Trading strategiyasi"""
    strategy_id: str
    seller_id: str
    seller_name: str
    name: str
    description: str
    strategy_type: StrategyType
    category: StrategyCategory
    pricing_model: PricingModel
    price: float = 0.0  # USD
    revenue_share_pct: float = 0.0  # Revenue share foizi
    
    # Performance
    backtesting_results: Dict[str, Any] = field(default_factory=dict)
    live_performance: Dict[str, Any] = field(default_factory=dict)
    win_rate: float = 0.0
    avg_profit: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    total_returns: float = 0.0
    profit_factor: float = 0.0
    volatility: float = 0.0
    
    # Metadata
    supported_markets: List[str] = field(default_factory=list)  # Crypto, Forex, Stocks
    supported_symbols: List[str] = field(default_factory=list)
    min_capital: float = 1000.0
    risk_level: str = "medium"  # low, medium, high
    timeframe: str = "1h"
    
    # Ma'lumotlar
    strategy_code: str = ""
    documentation: str = ""
    setup_instructions: str = ""
    risk_disclaimer: str = ""
    
    # Ko'rinish va tarqatish
    image_url: str = ""
    demo_video_url: str = ""
    live_performance_url: str = ""
    
    # Qo'shimcha narxlash ma'lumotlari
    monthly_price: float = None
    yearly_price: float = None
    performance_fee_percent: float = None
    minimum_trade_amount: float = None
    maximum_trade_amount: float = None
    
    # Requirements
    requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Stats
    total_sales: int = 0
    total_revenue: float = 0.0
    active_users: int = 0
    avg_rating: float = 0.0
    total_ratings: int = 0
    views_count: int = 0
    purchases_count: int = 0
    subscribers_count: int = 0
    popularity_score: float = 0.0
    
    # Status
    status: StrategyStatus = StrategyStatus.DRAFT
    verified: bool = False
    featured: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    approved_date: Optional[datetime] = None
    
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'strategy_id': self.strategy_id,
            'seller_id': self.seller_id,
            'seller_name': self.seller_name,
            'name': self.name,
            'description': self.description,
            'strategy_type': self.strategy_type.value,
            'category': self.category.value,
            'pricing_model': self.pricing_model.value,
            'price': self.price,
            'revenue_share_pct': self.revenue_share_pct,
            'backtesting_results': self.backtesting_results,
            'live_performance': self.live_performance,
            'win_rate': self.win_rate,
            'avg_profit': self.avg_profit,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'total_returns': self.total_returns,
            'profit_factor': self.profit_factor,
            'volatility': self.volatility,
            'supported_markets': self.supported_markets,
            'supported_symbols': self.supported_symbols,
            'min_capital': self.min_capital,
            'risk_level': self.risk_level,
            'timeframe': self.timeframe,
            'strategy_code': self.strategy_code,
            'documentation': self.documentation,
            'setup_instructions': self.setup_instructions,
            'risk_disclaimer': self.risk_disclaimer,
            'image_url': self.image_url,
            'demo_video_url': self.demo_video_url,
            'live_performance_url': self.live_performance_url,
            'monthly_price': self.monthly_price,
            'yearly_price': self.yearly_price,
            'performance_fee_percent': self.performance_fee_percent,
            'minimum_trade_amount': self.minimum_trade_amount,
            'maximum_trade_amount': self.maximum_trade_amount,
            'requirements': self.requirements,
            'total_sales': self.total_sales,
            'total_revenue': self.total_revenue,
            'active_users': self.active_users,
            'avg_rating': self.avg_rating,
            'total_ratings': self.total_ratings,
            'views_count': self.views_count,
            'purchases_count': self.purchases_count,
            'subscribers_count': self.subscribers_count,
            'popularity_score': self.popularity_score,
            'status': self.status.value,
            'verified': self.verified,
            'featured': self.featured,
            'created_at': self.created_at.isoformat(),
            'approved_date': self.approved_date.isoformat() if self.approved_date else None,
            'updated_at': self.updated_at.isoformat(),
            'tags': self.tags,
        }
    
    def increment_views(self):
        """Ko'rish sonini oshirish"""
        self.views_count += 1
        self.update_popularity_score()
    
    def increment_purchases(self):
        """Xaridlar sonini oshirish"""
        self.purchases_count += 1
        self.update_popularity_score()
    
    def update_popularity_score(self):
        """Ommalashish ballini yangilash"""
        base_score = self.views_count * 0.1 + self.purchases_count * 2 + self.subscribers_count * 3
        rating_bonus = self.avg_rating * 5
        review_bonus = self.total_ratings * 0.5
        performance_bonus = self.total_returns * 0.1 + self.sharpe_ratio * 2
        self.popularity_score = base_score + rating_bonus + review_bonus + performance_bonus


@dataclass
class StrategyRating:
    """Strategiya reytingi"""
    rating_id: str
    strategy_id: str
    buyer_id: str
    buyer_name: str
    rating: int  # 1-5
    review: str = ""
    verified_purchase: bool = False
    performance_met: bool = True
    ease_of_use: int = 5  # 1-5
    support_quality: int = 5  # 1-5
    created_at: datetime = field(default_factory=datetime.now)
    helpful_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'rating_id': self.rating_id,
            'strategy_id': self.strategy_id,
            'buyer_id': self.buyer_id,
            'buyer_name': self.buyer_name,
            'rating': self.rating,
            'review': self.review,
            'verified_purchase': self.verified_purchase,
            'performance_met': self.performance_met,
            'ease_of_use': self.ease_of_use,
            'support_quality': self.support_quality,
            'created_at': self.created_at.isoformat(),
            'helpful_count': self.helpful_count,
        }


@dataclass
class Purchase:
    """Sotib olish"""
    purchase_id: str
    strategy_id: str
    buyer_id: str
    seller_id: str
    price_paid: float
    pricing_model: PricingModel
    purchase_date: datetime = field(default_factory=datetime.now)
    subscription_end: Optional[datetime] = None
    status: str = "active"  # active, cancelled, expired
    
    def to_dict(self) -> Dict:
        return {
            'purchase_id': self.purchase_id,
            'strategy_id': self.strategy_id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'price_paid': self.price_paid,
            'pricing_model': self.pricing_model.value,
            'purchase_date': self.purchase_date.isoformat(),
            'subscription_end': self.subscription_end.isoformat() if self.subscription_end else None,
            'status': self.status,
        }


@dataclass
class SellerProfile:
    """Sotuvchi profili"""
    seller_id: str
    username: str
    email: str
    full_name: str
    verification_status: bool = False
    rating: float = 0.0
    total_sales: int = 0
    total_earnings: float = 0.0
    join_date: datetime = field(default_factory=datetime.now)
    description: str = ""
    profile_image: str = ""
    social_links: Dict[str, str] = field(default_factory=dict)
    languages: List[str] = field(default_factory=list)
    specialties: List[str] = field(default_factory=list)
    
    # Qo'shimcha ma'lumotlar
    total_strategies: int = 0
    total_revenue: float = 0.0
    verified: bool = False
    joined_date: datetime = field(default_factory=datetime.now)
    payout_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'seller_id': self.seller_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'verification_status': self.verification_status,
            'rating': self.rating,
            'total_sales': self.total_sales,
            'total_earnings': self.total_earnings,
            'join_date': self.join_date.isoformat(),
            'description': self.description,
            'profile_image': self.profile_image,
            'social_links': self.social_links,
            'languages': self.languages,
            'specialties': self.specialties,
            'total_strategies': self.total_strategies,
            'total_revenue': self.total_revenue,
            'verified': self.verified,
            'joined_date': self.joined_date.isoformat(),
        }


class StrategyMarketplace:
    """
    Strategy Marketplace - Trading strategiyalarni
    sotish va sotib olish platformasi
    """
    
    def __init__(self):
        self.strategies: Dict[str, Strategy] = {}
        self.ratings: Dict[str, List[StrategyRating]] = {}  # strategy_id -> ratings
        self.purchases: Dict[str, Purchase] = {}
        self.sellers: Dict[str, SellerProfile] = {}
        self.buyer_purchases: Dict[str, List[str]] = {}  # buyer_id -> purchase_ids
        
        # Platform fees
        self.platform_fee_pct = 20.0  # Platform komissiyasi (%)
    
    async def register_seller(self, seller_id: str, username: str, email: str, 
                            full_name: str, description: str = "", 
                            profile_image: str = "", social_links: Dict[str, str] = None,
                            languages: List[str] = None, specialties: List[str] = None) -> bool:
        """
        Sotuvchi ro'yxatdan o'tkazish
        
        Args:
            seller_id: Sotuvchi ID
            username: Foydalanuvchi nomi
            email: Email manzili
            full_name: To'liq ism
            description: Tavsif
            profile_image: Profil rasm URLi
            social_links: Ijtimoiy tarmoq havolalari
            languages: Tillar ro'yxati
            specialties: Ixtisosliklar ro'yxati
            
        Returns:
            bool: Muvaffaqiyatli ro'yxatdan o'tgan bo'lsa True
        """
        try:
            seller = SellerProfile(
                seller_id=seller_id,
                username=username,
                email=email,
                full_name=full_name,
                description=description,
                profile_image=profile_image,
                social_links=social_links or {},
                languages=languages or [],
                specialties=specialties or []
            )
            
            self.sellers[seller_id] = seller
            logger.info(f"Sotuvchi ro'yxatdan o'tdi: {seller.username}")
            return True
        except Exception as e:
            logger.error(f"Sotuvchi ro'yxatdan o'tkazishda xatolik: {e}")
            return False
    
    async def submit_strategy(
        self,
        strategy_id: str,
        seller_id: str,
        title: str,
        description: str,
        strategy_type: StrategyType,
        category: StrategyCategory,
        pricing_model: PricingModel,
        price: float,
        risk_level: str = "medium",
        strategy_code: str = "",
        documentation: str = "",
        requirements: Dict[str, Any] = None,
        tags: List[str] = None,
        supported_markets: List[str] = None,
        timeframe: str = "1h",
        setup_instructions: str = "",
        risk_disclaimer: str = "",
        image_url: str = "",
        demo_video_url: str = "",
        monthly_price: float = None,
        yearly_price: float = None,
        performance_fee_percent: float = None,
        minimum_trade_amount: float = None,
        maximum_trade_amount: float = None
    ) -> bool:
        """
        Strategiya yuborish (ko'rib chiqishga)
        
        Args:
            strategy_id: Strategiya ID
            seller_id: Sotuvchi ID
            title: Strategiya nomi
            description: Tavsif
            strategy_type: Strategiya turi
            category: Kategoriya
            pricing_model: Narxlash modeli
            price: Narx
            risk_level: Risk darajasi
            strategy_code: Strategiya kodi
            documentation: Hujjatlar
            requirements: Talablar
            tags: Teglar
            supported_markets: Qo'llab-quvvatlanadigan bozorlar
            timeframe: Vaqt intervali
            setup_instructions: O'rnatish ko'rsatmalari
            risk_disclaimer: Risk ogohlantirish
            image_url: Rasm URL
            demo_video_url: Demo video URL
            monthly_price: Oylik narx
            yearly_price: Yillik narx
            performance_fee_percent: Performance komissiya foizi
            minimum_trade_amount: Minimal trade miqdori
            maximum_trade_amount: Maksimal trade miqdori
            
        Returns:
            bool: Muvaffaqiyatli yuborilgan bo'lsa True
        """
        try:
            # Sotuvchi mavjudligini tekshirish
            if seller_id not in self.sellers:
                logger.error(f"Sotuvchi topilmadi: {seller_id}")
                return False
            
            # Sotuvchi tasdiqlanganligini tekshirish
            seller = self.sellers[seller_id]
            if not seller.verification_status and not seller.verified:
                logger.warning(f"Sotuvchi tasdiqlanmagan: {seller_id}, lekin davom etilmoqda")
                # Tasdiqlanmagan sotuvchilarga ham ruxsat beramiz demo uchun
            
            # Strategiya yaratish
            seller_name = seller.full_name or seller.username
            strategy = Strategy(
                strategy_id=strategy_id,
                seller_id=seller_id,
                seller_name=seller_name,
                name=title,
                description=description,
                strategy_type=strategy_type,
                category=category,
                pricing_model=pricing_model,
                price=price,
                risk_level=risk_level,
                strategy_code=strategy_code,
                documentation=documentation,
                requirements=requirements or {},
                tags=tags or [],
                supported_markets=supported_markets or [],
                timeframe=timeframe,
                setup_instructions=setup_instructions,
                risk_disclaimer=risk_disclaimer,
                image_url=image_url,
                demo_video_url=demo_video_url,
                monthly_price=monthly_price,
                yearly_price=yearly_price,
                performance_fee_percent=performance_fee_percent,
                minimum_trade_amount=minimum_trade_amount,
                maximum_trade_amount=maximum_trade_amount
            )
            
            # Statusni pending_review ga o'zgartirish
            strategy.status = StrategyStatus.PENDING_REVIEW
            strategy.updated_at = datetime.now()
            
            # Saqlash
            self.strategies[strategy_id] = strategy
            
            # Sotuvchi statistikasini yangilash
            seller.total_strategies += 1
            
            logger.info(f"Strategiya yuborildi: {strategy.name} by {strategy.seller_name}")
            return True
            
        except Exception as e:
            logger.error(f"Strategiya yuborishda xatolik: {e}")
            return False
    
    async def approve_strategy(
        self,
        strategy_id: str,
        admin_notes: str = ""
    ) -> bool:
        """
        Strategiyani tasdiqlash (admin)
        
        Args:
            strategy_id: Strategiya ID
            admin_notes: Admin eslatmalari
            
        Returns:
            bool: Muvaffaqiyatli tasdiqlangan bo'lsa True
        """
        try:
            if strategy_id not in self.strategies:
                logger.error(f"Strategiya topilmadi: {strategy_id}")
                return False
            
            strategy = self.strategies[strategy_id]
            strategy.status = StrategyStatus.ACTIVE
            strategy.updated_at = datetime.now()
            
            logger.info(f"Strategiya tasdiqlandi: {strategy.name}")
            return True
            
        except Exception as e:
            logger.error(f"Strategiya tasdiqlashda xatolik: {e}")
            return False
    
    async def purchase_strategy(
        self,
        strategy_id: str,
        buyer_id: str,
        payment_info: Dict[str, Any]
    ) -> Optional[Purchase]:
        """
        Strategiya sotib olish
        
        Args:
            strategy_id: Strategiya ID
            buyer_id: Xaridor ID
            payment_info: To'lov ma'lumotlari
            
        Returns:
            Purchase yoki None
        """
        try:
            # Strategiya mavjudligini tekshirish
            if strategy_id not in self.strategies:
                logger.error(f"Strategiya topilmadi: {strategy_id}")
                return None
            
            strategy = self.strategies[strategy_id]
            
            # Aktiv statusni tekshirish
            if strategy.status != StrategyStatus.ACTIVE:
                logger.error(f"Strategiya aktiv emas: {strategy_id}")
                return None
            
            # Allaqachon sotib olingan bo'lsa
            if buyer_id in self.buyer_purchases:
                for purchase_id in self.buyer_purchases[buyer_id]:
                    purchase = self.purchases.get(purchase_id)
                    if (purchase and
                        purchase.strategy_id == strategy_id and
                        purchase.status == "active"):
                        logger.warning(f"Strategiya allaqachon sotib olingan: {strategy_id}")
                        return None
            
            # Purchase yaratish
            purchase_id = f"purchase_{datetime.now().timestamp()}"
            
            # Subscription end date (agar subscription bo'lsa)
            subscription_end = None
            if strategy.pricing_model == PricingModel.SUBSCRIPTION:
                subscription_end = datetime.now() + timedelta(days=30)
            
            purchase = Purchase(
                purchase_id=purchase_id,
                strategy_id=strategy_id,
                buyer_id=buyer_id,
                seller_id=strategy.seller_id,
                price_paid=strategy.price,
                pricing_model=strategy.pricing_model,
                subscription_end=subscription_end
            )
            
            # Saqlash
            self.purchases[purchase_id] = purchase
            
            # Xaridor purchaselarini yangilash
            if buyer_id not in self.buyer_purchases:
                self.buyer_purchases[buyer_id] = []
            self.buyer_purchases[buyer_id].append(purchase_id)
            
            # Strategiya statistikasini yangilash
            strategy.total_sales += 1
            strategy.active_users += 1
            
            # Platform fee hisoblash
            platform_fee = strategy.price * (self.platform_fee_pct / 100)
            seller_revenue = strategy.price - platform_fee
            
            strategy.total_revenue += seller_revenue
            
            # Sotuvchi statistikasini yangilash
            if strategy.seller_id in self.sellers:
                seller = self.sellers[strategy.seller_id]
                seller.total_sales += 1
                seller.total_revenue += seller_revenue
            
            logger.info(
                f"Strategiya sotib olindi: {strategy.name} "
                f"Buyer: {buyer_id}, Price: ${strategy.price}"
            )
            
            return purchase
            
        except Exception as e:
            logger.error(f"Strategiya sotib olishda xatolik: {e}")
            return None
    
    async def add_rating(self, rating: StrategyRating) -> bool:
        """
        Strategiyaga reyting qo'shish
        
        Args:
            rating: Reyting
            
        Returns:
            bool: Muvaffaqiyatli qo'shilgan bo'lsa True
        """
        try:
            strategy_id = rating.strategy_id
            
            # Strategiya mavjudligini tekshirish
            if strategy_id not in self.strategies:
                logger.error(f"Strategiya topilmadi: {strategy_id}")
                return False
            
            # Xaridor sotib olganligini tekshirish
            purchased = False
            if rating.buyer_id in self.buyer_purchases:
                for purchase_id in self.buyer_purchases[rating.buyer_id]:
                    purchase = self.purchases.get(purchase_id)
                    if purchase and purchase.strategy_id == strategy_id:
                        purchased = True
                        rating.verified_purchase = True
                        break
            
            if not purchased:
                logger.warning(f"Xaridor strategiyani sotib olmagan: {rating.buyer_id}")
                # Baribir reyting qo'shishga ruxsat beramiz, lekin verified emas
            
            # Reytingni saqlash
            if strategy_id not in self.ratings:
                self.ratings[strategy_id] = []
            self.ratings[strategy_id].append(rating)
            
            # O'rtacha reytingni yangilash
            await self._update_avg_rating(strategy_id)
            
            logger.info(
                f"Reyting qo'shildi: {rating.rating}/5 for {strategy_id}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Reyting qo'shishda xatolik: {e}")
            return False
    
    async def _update_avg_rating(self, strategy_id: str):
        """Strategiyaning o'rtacha reytingini yangilash"""
        if strategy_id not in self.strategies:
            return
        
        strategy = self.strategies[strategy_id]
        ratings = self.ratings.get(strategy_id, [])
        
        if ratings:
            total_rating = sum(r.rating for r in ratings)
            strategy.avg_rating = total_rating / len(ratings)
            strategy.total_ratings = len(ratings)
            
            # Sotuvchi o'rtacha reytingini yangilash
            if strategy.seller_id in self.sellers:
                await self._update_seller_avg_rating(strategy.seller_id)
    
    async def _update_seller_avg_rating(self, seller_id: str):
        """Sotuvchining o'rtacha reytingini yangilash"""
        if seller_id not in self.sellers:
            return
        
        seller = self.sellers[seller_id]
        
        # Sotuvchining barcha strategiyalari
        seller_strategies = [
            s for s in self.strategies.values()
            if s.seller_id == seller_id
        ]
        
        if seller_strategies:
            total_rating = sum(s.avg_rating * s.total_ratings for s in seller_strategies)
            total_ratings = sum(s.total_ratings for s in seller_strategies)
            
            if total_ratings > 0:
                seller.avg_rating = total_rating / total_ratings
    
    async def get_strategies(
        self,
        category: Optional[StrategyCategory] = None,
        strategy_type: Optional[StrategyType] = None,
        pricing_model: Optional[PricingModel] = None,
        min_rating: float = 0.0,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        risk_level: Optional[str] = None,
        tags: List[str] = None,
        market: Optional[str] = None,
        query: Optional[str] = None,
        sort_by: str = "popularity",
        limit: int = 50,
        offset: int = 0
    ) -> List[Strategy]:
        """
        Strategiyalar ro'yxatini olish
        
        Args:
            category: Kategoriya filtri
            strategy_type: Strategiya turi filtri
            pricing_model: Narxlash modeli filtri
            min_rating: Minimal reyting
            max_price: Maksimal narx
            min_price: Minimal narx
            risk_level: Risk darajasi filtri
            tags: Teglar filtri
            market: Bozor filtri
            query: Qidiruv so'rovi
            sort_by: Saralash (popularity, rating, sales, price, date, returns)
            limit: Maksimal soni
            offset: Offset
            
        Returns:
            Strategiyalar ro'yxati
        """
        strategies = [
            s for s in self.strategies.values()
            if s.status == StrategyStatus.ACTIVE
        ]
        
        # Filtrlar
        if category:
            strategies = [s for s in strategies if s.category == category]
        
        if strategy_type:
            strategies = [s for s in strategies if s.strategy_type == strategy_type]
        
        if pricing_model:
            strategies = [s for s in strategies if s.pricing_model == pricing_model]
        
        if min_rating > 0:
            strategies = [s for s in strategies if s.avg_rating >= min_rating]
        
        if max_price is not None:
            strategies = [s for s in strategies if s.price <= max_price]
        
        if min_price is not None:
            strategies = [s for s in strategies if s.price >= min_price]
        
        if risk_level:
            strategies = [s for s in strategies if s.risk_level == risk_level]
        
        if tags:
            strategies = [s for s in strategies if all(tag in s.tags for tag in tags)]
        
        if market:
            strategies = [s for s in strategies if market in s.supported_markets]
        
        if query:
            query_lower = query.lower()
            strategies = [s for s in strategies 
                         if query_lower in s.name.lower() or 
                         query_lower in s.description.lower()]
        
        # Strategiyalarni ko'rish sonini oshirish (view count uchun)
        for strategy in strategies:
            strategy.increment_views()
        
        # Saralash
        if sort_by == "popularity":
            strategies.sort(key=lambda x: x.popularity_score, reverse=True)
        elif sort_by == "rating":
            strategies.sort(key=lambda x: x.avg_rating, reverse=True)
        elif sort_by == "sales":
            strategies.sort(key=lambda x: x.total_sales, reverse=True)
        elif sort_by == "price":
            strategies.sort(key=lambda x: x.price)
        elif sort_by == "date":
            strategies.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "returns":
            strategies.sort(key=lambda x: x.total_returns, reverse=True)
        elif sort_by == "risk":
            risk_order = {"low": 1, "medium": 2, "high": 3}
            strategies.sort(key=lambda x: risk_order.get(x.risk_level, 4))
        
        # Limit va offset qo'llash
        return strategies[offset:offset + limit]
    
    async def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """
        Bitta strategiyani olish
        
        Args:
            strategy_id: Strategiya ID
            
        Returns:
            Strategy yoki None
        """
        return self.strategies.get(strategy_id)
    
    async def get_strategy_ratings(
        self,
        strategy_id: str,
        limit: int = 50
    ) -> List[StrategyRating]:
        """
        Strategiya reytinglarini olish
        
        Args:
            strategy_id: Strategiya ID
            limit: Maksimal soni
            
        Returns:
            Reytinglar ro'yxati
        """
        ratings = self.ratings.get(strategy_id, [])
        # Vaqt bo'yicha teskari saralash
        ratings.sort(key=lambda x: x.created_at, reverse=True)
        return ratings[:limit]
    
    async def get_buyer_purchases(
        self,
        buyer_id: str
    ) -> List[Purchase]:
        """
        Xaridorning sotib olishlari
        
        Args:
            buyer_id: Xaridor ID
            
        Returns:
            Purchaselar ro'yxati
        """
        if buyer_id not in self.buyer_purchases:
            return []
        
        purchase_ids = self.buyer_purchases[buyer_id]
        purchases = [
            self.purchases[pid]
            for pid in purchase_ids
            if pid in self.purchases
        ]
        
        # Vaqt bo'yicha teskari saralash
        purchases.sort(key=lambda x: x.purchase_date, reverse=True)
        
        return purchases
    
    async def get_seller_strategies(
        self,
        seller_id: str
    ) -> List[Strategy]:
        """
        Sotuvchining strategiyalari
        
        Args:
            seller_id: Sotuvchi ID
            
        Returns:
            Strategiyalar ro'yxati
        """
        strategies = [
            s for s in self.strategies.values()
            if s.seller_id == seller_id
        ]
        
        # Vaqt bo'yicha teskari saralash
        strategies.sort(key=lambda x: x.created_at, reverse=True)
        
        return strategies
    
    async def get_top_sellers(
        self,
        limit: int = 10,
        sort_by: str = "revenue"
    ) -> List[SellerProfile]:
        """
        Top sotuvchilar
        
        Args:
            limit: Maksimal soni
            sort_by: Saralash (revenue, sales, rating)
            
        Returns:
            Sotuvchilar ro'yxati
        """
        sellers = list(self.sellers.values())
        
        # Saralash
        if sort_by == "revenue":
            sellers.sort(key=lambda x: x.total_revenue, reverse=True)
        elif sort_by == "sales":
            sellers.sort(key=lambda x: x.total_sales, reverse=True)
        elif sort_by == "rating":
            sellers.sort(key=lambda x: x.avg_rating, reverse=True)
        
        return sellers[:limit]
    
    async def search_strategies(
        self,
        query: str,
        search_in: List[str] = None
    ) -> List[Strategy]:
        """
        Strategiyalarni qidirish
        
        Args:
            query: Qidiruv so'zi
            search_in: Qaysi maydonlarda qidirish
            
        Returns:
            Topilgan strategiyalar
        """
        if search_in is None:
            search_in = ['name', 'description', 'tags']
        
        query_lower = query.lower()
        results = []
        
        for strategy in self.strategies.values():
            if strategy.status != StrategyStatus.ACTIVE:
                continue
            
            match = False
            
            if 'name' in search_in:
                if query_lower in strategy.name.lower():
                    match = True
            
            if 'description' in search_in:
                if query_lower in strategy.description.lower():
                    match = True
            
            if 'tags' in search_in:
                if any(query_lower in tag.lower() for tag in strategy.tags):
                    match = True
            
            if match:
                results.append(strategy)
        
        # Reytingga qarab saralash
        results.sort(key=lambda x: x.avg_rating, reverse=True)
        
        return results
    
    async def get_featured_strategies(
        self,
        limit: int = 10
    ) -> List[Strategy]:
        """
        Featured strategiyalar
        
        Args:
            limit: Maksimal soni
            
        Returns:
            Featured strategiyalar ro'yxati
        """
        strategies = [
            s for s in self.strategies.values()
            if s.featured and s.status == StrategyStatus.ACTIVE
        ]
        
        # Reytingga qarab saralash
        strategies.sort(key=lambda x: x.avg_rating, reverse=True)
        
        return strategies[:limit]
    
    async def get_marketplace_stats(self) -> Dict[str, Any]:
        """
        Marketplace statistikasi
        
        Returns:
            Keng qamrovli statistika ma'lumotlari
        """
        active_strategies = [s for s in self.strategies.values() if s.status == StrategyStatus.ACTIVE]
        pending_strategies = [s for s in self.strategies.values() if s.status == StrategyStatus.PENDING_REVIEW]
        total_strategies = len(self.strategies)
        
        # Asosiy statistikalar
        total_sales = sum(s.total_sales for s in active_strategies)
        total_revenue = sum(s.total_revenue for s in active_strategies)
        total_earnings = sum(seller.total_earnings for seller in self.sellers.values())
        total_views = sum(s.views_count for s in active_strategies)
        total_purchases = sum(s.purchases_count for s in active_strategies)
        total_subscribers = sum(s.subscribers_count for s in active_strategies)
        
        # Kategoriya bo'yicha taqsimlash
        category_distribution = {}
        for category in StrategyCategory:
            count = sum(1 for s in active_strategies if s.category == category)
            category_distribution[category.value] = count
        
        # Strategiya turi bo'yicha taqsimlash
        strategy_type_distribution = {}
        for strategy_type in StrategyType:
            count = sum(1 for s in active_strategies if s.strategy_type == strategy_type)
            strategy_type_distribution[strategy_type.value] = count
        
        # Narx oralig'i bo'yicha taqsimlash
        price_ranges = {
            '0-100': 0,
            '100-500': 0,
            '500-1000': 0,
            '1000-5000': 0,
            '5000+': 0
        }
        
        for strategy in active_strategies:
            price = strategy.price
            if price < 100:
                price_ranges['0-100'] += 1
            elif price < 500:
                price_ranges['100-500'] += 1
            elif price < 1000:
                price_ranges['500-1000'] += 1
            elif price < 5000:
                price_ranges['1000-5000'] += 1
            else:
                price_ranges['5000+'] += 1
        
        # Risk darajasi bo'yicha taqsimlash
        risk_stats = {"low": 0, "medium": 0, "high": 0}
        for strategy in active_strategies:
            risk_stats[strategy.risk_level] += 1
        
        # Eng yaxshi sotuvchilar
        top_sellers = sorted(self.sellers.values(), 
                           key=lambda x: x.total_revenue or x.total_earnings, 
                           reverse=True)[:10]
        
        # Eng mashhur strategiyalar
        top_strategies = sorted(active_strategies, 
                              key=lambda x: x.popularity_score, 
                              reverse=True)[:10]
        
        return {
            # Asosiy statistikalar
            'total_strategies': total_strategies,
            'approved_strategies': len(active_strategies),
            'pending_strategies': len(pending_strategies),
            'active_sellers': len(self.sellers),
            
            # Operatsion statistikalar
            'total_views': total_views,
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'total_subscribers': total_subscribers,
            'total_revenue': total_revenue,
            'total_earnings': total_earnings,
            
            # O'rtacha ko'rsatkichlar
            'average_strategy_price': sum(s.price for s in active_strategies) / len(active_strategies) if active_strategies else 0,
            'average_rating': sum(s.avg_rating for s in active_strategies) / len(active_strategies) if active_strategies else 0,
            'average_total_returns': sum(s.total_returns for s in active_strategies) / len(active_strategies) if active_strategies else 0,
            
            # Taqsimlash
            'category_distribution': category_distribution,
            'strategy_type_distribution': strategy_type_distribution,
            'price_ranges': price_ranges,
            'risk_stats': risk_stats,
            
            # Top ma'lumotlar
            'top_sellers': [
                {
                    'seller_id': seller.seller_id,
                    'username': seller.username,
                    'full_name': seller.full_name,
                    'rating': seller.rating,
                    'total_sales': seller.total_sales,
                    'total_revenue': seller.total_revenue or seller.total_earnings,
                    'verification_status': seller.verification_status or seller.verified,
                    'strategies_count': seller.total_strategies
                }
                for seller in top_sellers
            ],
            'top_strategies': [
                {
                    'strategy_id': s.strategy_id,
                    'name': s.name,
                    'seller_name': s.seller_name,
                    'category': s.category.value,
                    'price': s.price,
                    'average_rating': s.avg_rating,
                    'total_sales': s.total_sales,
                    'popularity_score': s.popularity_score,
                    'total_returns': s.total_returns
                }
                for s in top_strategies
            ],
            
            # Qo'shimcha
            'total_ratings': sum(s.total_ratings for s in active_strategies),
            'platform_fee_pct': self.platform_fee_pct,
        }
    
    async def verify_seller(self, seller_id: str, verified: bool = True) -> bool:
        """
        Sotuvchini tasdiqlash
        
        Args:
            seller_id: Sotuvchi ID
            verified: Tasdiqlash holati
            
        Returns:
            bool: Muvaffaqiyatli bo'lsa True
        """
        try:
            if seller_id not in self.sellers:
                return False
            
            seller = self.sellers[seller_id]
            seller.verification_status = verified
            seller.verified = verified  # Orqaga moslik uchun
            
            logger.info(f"Sotuvchi tasdiqlandi: {seller_id}")
            return True
            
        except Exception as e:
            logger.error(f"Sotuvchini tasdiqlashda xatolik: {e}")
            return False
    
    async def update_strategy_performance(
        self,
        strategy_id: str,
        returns: float,
        balance: float,
        trades_count: int,
        profit_loss: float,
        win_rate: float = None,
        sharpe_ratio: float = None,
        max_drawdown: float = None
    ) -> bool:
        """
        Strategiya ishga chiqarish ma'lumotlarini yangilash
        
        Args:
            strategy_id: Strategiya ID
            returns: Foyda foizi
            balance: Balans
            trades_count: Trade soni
            profit_loss: Foyda/zarar
            win_rate: Win rate
            sharpe_ratio: Sharpe ratio
            max_drawdown: Maksimal drawdown
            
        Returns:
            bool: Muvaffaqiyatli bo'lsa True
        """
        try:
            if strategy_id not in self.strategies:
                return False
            
            strategy = self.strategies[strategy_id]
            
            # Performance ma'lumotlarini yangilash
            strategy.total_returns = returns
            
            if win_rate is not None:
                strategy.win_rate = win_rate
            
            if sharpe_ratio is not None:
                strategy.sharpe_ratio = sharpe_ratio
            
            if max_drawdown is not None:
                strategy.max_drawdown = max_drawdown
            
            # Live performance ma'lumotlarini yangilash
            if not strategy.live_performance:
                strategy.live_performance = {}
            
            strategy.live_performance.update({
                'last_updated': datetime.now().isoformat(),
                'balance': balance,
                'recent_returns': returns,
                'trades_today': trades_count,
                'profit_loss_today': profit_loss
            })
            
            strategy.updated_at = datetime.now()
            
            # Populyar ballini yangilash
            strategy.update_popularity_score()
            
            logger.info(f"Strategiya performance yangilandi: {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Performance yangilashda xatolik: {e}")
            return False
    
    async def search_strategies(
        self,
        query: str,
        limit: int = 20
    ) -> List[Strategy]:
        """
        Strategiyalarni qidirish
        
        Args:
            query: Qidiruv so'zi
            limit: Maksimal natija soni
            
        Returns:
            Topilgan strategiyalar ro'yxati
        """
        if not query:
            return []
        
        query_lower = query.lower()
        results = []
        
        for strategy in self.strategies.values():
            if strategy.status != StrategyStatus.ACTIVE:
                continue
            
            # Qidiruv so'rovini tekshirish
            if (query_lower in strategy.name.lower() or 
                query_lower in strategy.description.lower() or
                any(query_lower in tag.lower() for tag in strategy.tags) or
                any(query_lower in market.lower() for market in strategy.supported_markets)):
                
                results.append(strategy)
                strategy.increment_views()
        
        # Moslik va ommalashishga qarab saralash
        results.sort(key=lambda x: (x.popularity_score, x.avg_rating), reverse=True)
        
        return results[:limit]
    
    async def get_strategy_by_id(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """
        ID bo'yicha strategiya olish
        
        Args:
            strategy_id: Strategiya ID
            
        Returns:
            Strategiya ma'lumotlari yoki None
        """
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            return None
        
        # Ko'rish sonini oshirish
        strategy.increment_views()
        
        seller = self.sellers.get(strategy.seller_id)
        
        return {
            'strategy': strategy.to_dict(),
            'seller': {
                'seller_id': seller.seller_id if seller else None,
                'username': seller.username if seller else None,
                'full_name': seller.full_name if seller else None,
                'rating': seller.rating if seller else 0,
                'verification_status': seller.verification_status if seller else False,
                'description': seller.description if seller else ''
            },
            'can_purchase': True,
            'similar_strategies': await self.get_strategies(
                category=strategy.category,
                limit=5,
                exclude_strategy_id=strategy_id
            )
        }
    
    async def get_user_purchases(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Foydalanuvchi xaridlari
        
        Args:
            user_id: Foydalanuvchi ID
            
        Returns:
            Xaridlar ro'yxati
        """
        if user_id not in self.buyer_purchases:
            return []
        
        purchase_ids = self.buyer_purchases[user_id]
        purchases_data = []
        
        for purchase_id in purchase_ids:
            if purchase_id in self.purchases:
                purchase = self.purchases[purchase_id]
                strategy = self.strategies.get(purchase.strategy_id)
                
                if strategy:
                    purchase_data = {
                        'purchase_id': purchase.purchase_id,
                        'strategy': strategy.to_dict(),
                        'purchase_date': purchase.purchase_date.isoformat(),
                        'price_paid': purchase.price_paid,
                        'pricing_model': purchase.pricing_model.value,
                        'subscription_end': purchase.subscription_end.isoformat() if purchase.subscription_end else None,
                        'status': purchase.status,
                        'seller_name': strategy.seller_name
                    }
                    purchases_data.append(purchase_data)
        
        # Vaqt bo'yicha teskari saralash
        purchases_data.sort(key=lambda x: x['purchase_date'], reverse=True)
        
        return purchases_data
    
    async def rate_strategy(
        self,
        strategy_id: str,
        buyer_id: str,
        rating: int,
        review: str = "",
        ease_of_use: int = 5,
        support_quality: int = 5
    ) -> bool:
        """
        Strategiyaga reyting berish
        
        Args:
            strategy_id: Strategiya ID
            buyer_id: Xaridor ID
            rating: Reyting (1-5)
            review: Sharh
            ease_of_use: Foydalanish qulayligi (1-5)
            support_quality: Qo'llab-quvvatlash sifati (1-5)
            
        Returns:
            bool: Muvaffaqiyatli bo'lsa True
        """
        try:
            # Validatsiya
            if rating < 1 or rating > 5:
                return False
            
            if strategy_id not in self.strategies:
                return False
            
            # Xarid qilinganligini tekshirish
            purchased = False
            if buyer_id in self.buyer_purchases:
                for purchase_id in self.buyer_purchases[buyer_id]:
                    purchase = self.purchases.get(purchase_id)
                    if purchase and purchase.strategy_id == strategy_id:
                        purchased = True
                        break
            
            if not purchased:
                logger.warning(f"Xaridor strategiyani sotib olmagan: {buyer_id}")
                return False
            
            # Reyting yaratish
            rating_obj = StrategyRating(
                rating_id=f"rating_{datetime.now().timestamp()}",
                strategy_id=strategy_id,
                buyer_id=buyer_id,
                buyer_name=f"User_{buyer_id[:8]}",  # Simple anonymization
                rating=rating,
                review=review,
                verified_purchase=True,
                ease_of_use=ease_of_use,
                support_quality=support_quality
            )
            
            # Reytingni qo'shish
            return await self.add_rating(rating_obj)
            
        except Exception as e:
            logger.error(f"Reyting berishda xatolik: {e}")
            return False


# Demo va test funksiyalari
async def demo_marketplace():
    """Marketplace demo"""
    print("🚀 Strategy Marketplace Demo")
    print("=" * 50)
    
    # Marketplace yaratish
    marketplace = StrategyMarketplace()
    
    # Sotuvchilarni ro'yxatdan o'tkazish
    print("\n📝 Sotuvchilarni ro'yxatdan o'tkazish...")
    seller1_id = "seller1"
    await marketplace.register_seller(
        seller_id=seller1_id,
        username="algo_trader_pro",
        email="trader@example.com",
        full_name="Alex Johnson",
        description="Professional algoritm trader with 10+ years experience",
        specialties=["Forex", "Crypto", "Quantitative Analysis"]
    )
    
    seller2_id = "seller2"
    await marketplace.register_seller(
        seller_id=seller2_id,
        username="forex_guru",
        email="guru@example.com", 
        full_name="Maria Rodriguez",
        description="Expert in forex trading strategies",
        specialties=["Forex", "Risk Management"]
    )
    
    # Sotuvchilarni tasdiqlash
    await marketplace.verify_seller(seller1_id)
    await marketplace.verify_seller(seller2_id)
    
    # Strategiyallar topshirish
    print("\n📈 Strategiyalar topshirish...")
    
    # Strategiya 1: Scalping
    strategy1_id = "strategy1"
    await marketplace.submit_strategy(
        strategy_id=strategy1_id,
        seller_id=seller1_id,
        title="High-Frequency Scalping Bot",
        description="Advanced scalping strategy with 95% win rate. Optimized for crypto markets.",
        strategy_type=StrategyType.SCALPING,
        category=StrategyCategory.HIGH_FREQUENCY,
        pricing_model=PricingModel.SUBSCRIPTION_MONTHLY,
        price=299.99,
        monthly_price=299.99,
        risk_level="high",
        supported_markets=["BTC", "ETH", "ADA"],
        tags=["scalping", "automated", "crypto", "high-frequency"],
        requirements={
            "min_deposit": 1000.00,
            "supported_brokers": ["Binance", "Coinbase"],
            "risk_tolerance": "high"
        }
    )
    
    # Strategiya 2: Trend Following
    strategy2_id = "strategy2"
    await marketplace.submit_strategy(
        strategy_id=strategy2_id,
        seller_id=seller2_id,
        title="TrendMaster Forex System",
        description="Proven trend following system for major forex pairs. 3+ years live track record.",
        strategy_type=StrategyType.MANUAL,
        category=StrategyCategory.TREND_FOLLOWING,
        pricing_model=PricingModel.ONE_TIME_PAYMENT,
        price=99.99,
        risk_level="medium",
        supported_markets=["EURUSD", "GBPUSD", "USDJPY"],
        tags=["forex", "trend-following", "manual", "proven"],
        requirements={
            "min_deposit": 500.00,
            "supported_brokers": ["MetaTrader4", "MetaTrader5"],
            "risk_tolerance": "medium"
        }
    )
    
    # Strategiyallarni tasdiqlash
    await marketplace.approve_strategy(strategy1_id)
    await marketplace.approve_strategy(strategy2_id)
    
    # Ishga chiqarish ma'lumotlari qo'shish
    print("\n📊 Ishga chiqarish ma'lumotlarini qo'shish...")
    await marketplace.update_strategy_performance(
        strategy1_id, returns=15.5, balance=11500, trades_count=8, profit_loss=1550,
        win_rate=0.92, sharpe_ratio=2.3, max_drawdown=0.08
    )
    
    await marketplace.update_strategy_performance(
        strategy2_id, returns=12.8, balance=11280, trades_count=3, profit_loss=1280,
        win_rate=0.87, sharpe_ratio=1.9, max_drawdown=0.12
    )
    
    # Foydalanuvchilarni ro'yxatdan o'tkazish (simulyatsiya)
    user_id = "user123"
    
    # Strategiyalarni sotib olish
    print("\n🛒 Strategiyalarni sotib olish...")
    purchase1_id = await marketplace.purchase_strategy(
        strategy1_id, user_id, {"payment_method": "card"}
    )
    
    purchase2_id = await marketplace.purchase_strategy(
        strategy2_id, user_id, {"payment_method": "paypal"}
    )
    
    # Reytinglar qo'shish
    print("\n⭐ Reytinglar qo'shish...")
    await marketplace.rate_strategy(
        strategy1_id, user_id, 5, "Excellent scalping bot! Great profits.",
        ease_of_use=5, support_quality=5
    )
    
    await marketplace.rate_strategy(
        strategy2_id, user_id, 4, "Good forex strategy, easy to follow.",
        ease_of_use=4, support_quality=4
    )
    
    # Qidiruv
    print("\n🔎 Qidiruv natijalari ('crypto' uchun):")
    search_results = await marketplace.search_strategies("crypto")
    for result in search_results:
        print(f"   - {result.name} (${result.price})")
    
    # Foydalanuvchi xaridlari
    print("\n👤 Foydalanuvchi xaridlari:")
    user_purchases = await marketplace.get_user_purchases(user_id)
    for purchase in user_purchases:
        print(f"   - {purchase['strategy']['name']} (${purchase['price_paid']})")
    
    # Strategiyalar ro'yxati
    print("\n📋 Barcha strategiyalar:")
    all_strategies = await marketplace.get_strategies(limit=10)
    for i, strategy in enumerate(all_strategies, 1):
        print(f"   {i}. {strategy.name}")
        print(f"      Narx: ${strategy.price}")
        print(f"      Reyting: {strategy.avg_rating:.2f}/5")
        print(f"      Xaridlar: {strategy.total_sales}")
        print()
    
    # Statistiklarni olish
    print("\n📈 Marketplace statistikalari:")
    stats = await marketplace.get_marketplace_stats()
    print(f"   Jami strategiyallar: {stats['total_strategies']}")
    print(f"   Tasdiqlangan strategiyallar: {stats['approved_strategies']}")
    print(f"   Faol sotuvchilar: {stats['active_sellers']}")
    print(f"   Jami ko'rishlar: {stats['total_views']}")
    print(f"   Jami xaridlar: {stats['total_sales']}")
    print(f"   Jami daromadlar: ${stats['total_revenue']:.2f}")
    print(f"   O'rtacha narx: ${stats['average_strategy_price']:.2f}")
    
    return marketplace


if __name__ == "__main__":
    # Async demo ishga tushirish
    import asyncio
    
    async def main():
        marketplace = await demo_marketplace()
        print("\n✅ Strategy Marketplace tizimi muvaffaqiyatli ishga tushdi!")
        print("\n📋 Asosiy imkoniyatlar:")
        print("   ✓ Sotuvchilarni ro'yxatdan o'tkazish va tasdiqlash")
        print("   ✓ Strategiyalarni topshirish va tasdiqlash")
        print("   ✓ Strategiyalarni sotib olish va obuna tizimi")
        print("   ✓ Reyting va sharh tizimi")
        print("   ✓ Keng qamrovli filtrlash va qidiruv")
        print("   ✓ Marketplace statistikalari")
        print("   ✓ Ishga chiqarish ma'lumotlari kuzatuvi")
        print("   ✓ Performance metrikalari hisoblash")
        print("   ✓ Risk boshqaruv va talablar")
        print("   ✓ Ko'p turli narx berish modellari")
        print("   ✓ Real-time strategiya monitoringi")
        print("   ✓ Ko'rish va sotuv statistikalari")
        print("   ✓ Sotuvchilar reyting tizimi")
        print("   ✓ Ommalashish algoritmi")
    
    # Demo ishga tushirish
    asyncio.run(main())
