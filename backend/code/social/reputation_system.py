"""
Reputation System - Reviewlar, verified traders, va trust score
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ReviewStatus(Enum):
    """Review holatlari"""
    PENDING = "pending"  # Kutilayotgan
    PUBLISHED = "published"  # E'lon qilingan
    FLAGGED = "flagged"  # Belgilangan
    HIDDEN = "hidden"  # Yashirin
    DELETED = "deleted"  # O'chirilgan


class ReviewType(Enum):
    """Review turlari"""
    PRODUCT = "product"  # Mahsulot review
    SERVICE = "service"  # Xizmat review
    USER = "user"  # Foydalanuvchi review
    TRANSACTION = "transaction"  # Transaction review
    COMPLETION = "completion"  # Bajarilish review
    QUALITY = "quality"  # Sifat review
    TIMELINESS = "timeliness"  # Vaqt review
    COMMUNICATION = "communication"  # Muloqot review
    OVERALL = "overall"  # Umumiy review
    TRADER = "trader"  # Trader review
    STRATEGY = "strategy"  # Strategiya review
    SIGNAL_PROVIDER = "signal_provider"  # Signal provider review
    COPY_LEADER = "copy_leader"  # Copy trading leader review


class VerificationLevel(Enum):
    """Tasdiqlash darajalari"""
    UNVERIFIED = 0  # Tasdiqlanmagan
    BASIC = 1  # Asosiy
    MEDIUM = 2  # O'rta
    HIGH = 3  # Yuqori
    PREMIUM = 4  # Premium
    VERIFIED = 5  # To'liq tasdiqlangan
    EMAIL = 1  # Email tasdiqlangan
    PHONE = 2  # Telefon tasdiqlangan
    ID_DOCUMENT = 3  # Hujjat tasdiqlangan
    FULL = 5  # Barcha verifikatsiyalar


class TrustTier(Enum):
    """Ishonch darajalari"""
    NEW = "new"  # Yangi foydalanuvchi (0-25)
    BASIC = "basic"  # Asosiy (25-50)
    TRUSTED = "trusted"  # Ishonchli (50-70)
    PREMIUM = "premium"  # Premium (70-85)
    VIP = "vip"  # VIP (85-90)
    ELITE = "elite"  # Elite (90-95)
    LEGEND = "legend"  # Legenda (95-100)
    BANNED = "banned"  # Taqiqlangan
    UNTRUSTED = "untrusted"  # Ishonchsiz (0-20)
    LOW = "low"  # Past (20-40)
    MEDIUM = "medium"  # O'rta (40-60)
    HIGH = "high"  # Yuqori (60-80)
    VERY_HIGH = "very_high"  # juda yuqori (80-100)


@dataclass
class Review:
    """Review (sharh)"""
    review_id: str
    reviewer_id: str
    reviewer_name: str
    target_id: str  # Review qilinayotgan user/strategy/signal ID
    target_type: ReviewType
    rating: int  # 1-5
    title: str = ""
    content: str = ""
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    verified: bool = False  # Verified purchase/interaction
    helpful_count: int = 0
    not_helpful_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'review_id': self.review_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer_name,
            'target_id': self.target_id,
            'target_type': self.target_type.value,
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'pros': self.pros,
            'cons': self.cons,
            'verified': self.verified,
            'helpful_count': self.helpful_count,
            'not_helpful_count': self.not_helpful_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def helpfulness_ratio(self) -> float:
        """Foydalilik nisbati"""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0.0
        return (self.helpful_count / total) * 100


@dataclass
class TrustScore:
    """Ishonch balli"""
    user_id: str
    username: str
    
    # Score components (0-100 har biri)
    trading_history_score: float = 0.0  # Trading tarix
    verification_score: float = 0.0  # Tasdiqlash
    community_score: float = 0.0  # Jamoa baxosi
    consistency_score: float = 0.0  # Izchillik
    transparency_score: float = 0.0  # Shaffoflik
    
    # Overall
    overall_score: float = 0.0
    trust_tier: TrustTier = TrustTier.UNTRUSTED
    
    # Metadata
    total_reviews_received: int = 0
    avg_review_rating: float = 0.0
    verification_level: VerificationLevel = VerificationLevel.UNVERIFIED
    account_age_days: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Badges
    badges: List[str] = field(default_factory=list)
    
    def calculate_overall_score(self) -> float:
        """
        Umumiy trust scoreni hisoblash
        
        Returns:
            Overall score (0-100)
        """
        weights = {
            'trading_history': 0.30,
            'verification': 0.20,
            'community': 0.25,
            'consistency': 0.15,
            'transparency': 0.10,
        }
        
        score = (
            self.trading_history_score * weights['trading_history'] +
            self.verification_score * weights['verification'] +
            self.community_score * weights['community'] +
            self.consistency_score * weights['consistency'] +
            self.transparency_score * weights['transparency']
        )
        
        self.overall_score = round(score, 2)
        self._update_trust_tier()
        
        return self.overall_score
    
    def _update_trust_tier(self):
        """Trust tier ni yangilash"""
        score = self.overall_score
        
        if score < 20:
            self.trust_tier = TrustTier.UNTRUSTED
        elif score < 40:
            self.trust_tier = TrustTier.LOW
        elif score < 60:
            self.trust_tier = TrustTier.MEDIUM
        elif score < 80:
            self.trust_tier = TrustTier.HIGH
        else:
            self.trust_tier = TrustTier.VERY_HIGH
    
    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'username': self.username,
            'trading_history_score': self.trading_history_score,
            'verification_score': self.verification_score,
            'community_score': self.community_score,
            'consistency_score': self.consistency_score,
            'transparency_score': self.transparency_score,
            'overall_score': self.overall_score,
            'trust_tier': self.trust_tier.value,
            'total_reviews_received': self.total_reviews_received,
            'avg_review_rating': self.avg_review_rating,
            'verification_level': self.verification_level.value,
            'account_age_days': self.account_age_days,
            'last_updated': self.last_updated.isoformat(),
            'badges': self.badges,
        }


@dataclass
class VerificationRequest:
    """Tasdiqlash so'rovi"""
    request_id: str
    user_id: str
    verification_type: VerificationLevel
    status: str = "pending"  # pending, approved, rejected
    submitted_at: datetime = field(default_factory=datetime.now)
    reviewed_at: Optional[datetime] = None
    reviewer_notes: str = ""
    documents: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'verification_type': self.verification_type.value,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat(),
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewer_notes': self.reviewer_notes,
            'documents': self.documents,
        }


class ReputationSystem:
    """
    Reputation System - Userlarning reputatsiyasini kuzatish,
    trust score hisoblash, va verification
    """
    
    def __init__(self):
        self.reviews: Dict[str, List[Review]] = {}  # target_id -> reviews
        self.trust_scores: Dict[str, TrustScore] = {}  # user_id -> trust score
        self.verifications: Dict[str, VerificationRequest] = {}
        self.user_verifications: Dict[str, VerificationLevel] = {}  # user_id -> level
        
    async def submit_review(self, review: Review) -> bool:
        """
        Review yuborish
        
        Args:
            review: Review
            
        Returns:
            bool: Muvaffaqiyatli yuborilgan bo'lsa True
        """
        try:
            target_id = review.target_id
            
            # Review saqlash
            if target_id not in self.reviews:
                self.reviews[target_id] = []
            
            # Duplikat tekshirish (bir user bir targetga faqat bir marta)
            existing = any(
                r.reviewer_id == review.reviewer_id
                for r in self.reviews[target_id]
            )
            
            if existing:
                logger.warning(
                    f"User allaqachon review qoldirgan: {review.reviewer_id} -> {target_id}"
                )
                return False
            
            self.reviews[target_id].append(review)
            
            # Target userning trust scoreni yangilash
            if review.target_type == ReviewType.TRADER:
                await self._update_community_score(target_id)
            
            logger.info(
                f"Review yuborildi: {review.rating}/5 for {target_id} "
                f"by {review.reviewer_name}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Review yuborishda xatolik: {e}")
            return False
    
    async def get_reviews(
        self,
        target_id: str,
        target_type: Optional[ReviewType] = None,
        min_rating: int = 0,
        verified_only: bool = False,
        limit: int = 50
    ) -> List[Review]:
        """
        Reviewlarni olish
        
        Args:
            target_id: Target ID
            target_type: Review turi filtri
            min_rating: Minimal reyting
            verified_only: Faqat verified reviewlar
            limit: Maksimal soni
            
        Returns:
            Reviewlar ro'yxati
        """
        reviews = self.reviews.get(target_id, [])
        
        # Filtrlar
        if target_type:
            reviews = [r for r in reviews if r.target_type == target_type]
        
        if min_rating > 0:
            reviews = [r for r in reviews if r.rating >= min_rating]
        
        if verified_only:
            reviews = [r for r in reviews if r.verified]
        
        # Foydalilik bo'yicha saralash
        reviews.sort(key=lambda x: x.helpful_count, reverse=True)
        
        return reviews[:limit]
    
    async def mark_review_helpful(
        self,
        review_id: str,
        helpful: bool = True
    ) -> bool:
        """
        Reviewni foydali/foydali emas deb belgilash
        
        Args:
            review_id: Review ID
            helpful: Foydali bo'lsa True
            
        Returns:
            bool: Muvaffaqiyatli bo'lsa True
        """
        try:
            # Reviewni topish
            for reviews_list in self.reviews.values():
                for review in reviews_list:
                    if review.review_id == review_id:
                        if helpful:
                            review.helpful_count += 1
                        else:
                            review.not_helpful_count += 1
                        return True
            
            logger.warning(f"Review topilmadi: {review_id}")
            return False
            
        except Exception as e:
            logger.error(f"Review belgilashda xatolik: {e}")
            return False
    
    async def calculate_trust_score(
        self,
        user_id: str,
        username: str,
        trading_data: Dict[str, Any]
    ) -> TrustScore:
        """
        User uchun trust score hisoblash
        
        Args:
            user_id: User ID
            username: Username
            trading_data: Trading ma'lumotlari
            
        Returns:
            TrustScore
        """
        try:
            # Mavjud score yoki yangi yaratish
            if user_id in self.trust_scores:
                trust_score = self.trust_scores[user_id]
            else:
                trust_score = TrustScore(user_id=user_id, username=username)
            
            # 1. Trading History Score
            trust_score.trading_history_score = self._calculate_trading_history_score(
                trading_data
            )
            
            # 2. Verification Score
            trust_score.verification_score = self._calculate_verification_score(user_id)
            verification_level = self.user_verifications.get(user_id, VerificationLevel.UNVERIFIED)
            trust_score.verification_level = verification_level
            
            # 3. Community Score
            trust_score.community_score = await self._calculate_community_score(user_id)
            
            # 4. Consistency Score
            trust_score.consistency_score = self._calculate_consistency_score(
                trading_data
            )
            
            # 5. Transparency Score
            trust_score.transparency_score = self._calculate_transparency_score(
                trading_data
            )
            
            # Account age
            if 'account_created' in trading_data:
                account_created = trading_data['account_created']
                if isinstance(account_created, datetime):
                    trust_score.account_age_days = (datetime.now() - account_created).days
            
            # Overall score hisoblash
            trust_score.calculate_overall_score()
            
            # Badgelarni yangilash
            self._update_badges(trust_score)
            
            # Saqlash
            trust_score.last_updated = datetime.now()
            self.trust_scores[user_id] = trust_score
            
            logger.info(
                f"Trust score hisoblandi: {username} -> {trust_score.overall_score:.2f} "
                f"({trust_score.trust_tier.value})"
            )
            
            return trust_score
            
        except Exception as e:
            logger.error(f"Trust score hisoblashda xatolik: {e}")
            # Default score qaytarish
            return TrustScore(user_id=user_id, username=username)
    
    def _calculate_trading_history_score(
        self,
        trading_data: Dict[str, Any]
    ) -> float:
        """Trading tarix skorini hisoblash"""
        score = 0.0
        
        # Total trades
        total_trades = trading_data.get('total_trades', 0)
        if total_trades >= 1000:
            score += 30
        elif total_trades >= 500:
            score += 25
        elif total_trades >= 100:
            score += 20
        elif total_trades >= 50:
            score += 15
        elif total_trades >= 10:
            score += 10
        
        # Win rate
        win_rate = trading_data.get('win_rate', 0.0)
        if win_rate >= 70:
            score += 30
        elif win_rate >= 60:
            score += 25
        elif win_rate >= 50:
            score += 20
        elif win_rate >= 40:
            score += 10
        
        # Profitability
        total_pnl = trading_data.get('total_pnl', 0.0)
        if total_pnl > 10000:
            score += 20
        elif total_pnl > 5000:
            score += 15
        elif total_pnl > 1000:
            score += 10
        elif total_pnl > 0:
            score += 5
        
        # Sharpe ratio
        sharpe = trading_data.get('sharpe_ratio', 0.0)
        if sharpe >= 2.0:
            score += 20
        elif sharpe >= 1.5:
            score += 15
        elif sharpe >= 1.0:
            score += 10
        elif sharpe >= 0.5:
            score += 5
        
        return min(100, score)
    
    def _calculate_verification_score(self, user_id: str) -> float:
        """Verification skorini hisoblash"""
        level = self.user_verifications.get(user_id, VerificationLevel.UNVERIFIED)
        
        scores = {
            VerificationLevel.UNVERIFIED: 0,
            VerificationLevel.BASIC: 20,
            VerificationLevel.EMAIL: 20,
            VerificationLevel.PHONE: 40,
            VerificationLevel.MEDIUM: 40,
            VerificationLevel.ID_DOCUMENT: 70,
            VerificationLevel.HIGH: 70,
            VerificationLevel.PREMIUM: 85,
            VerificationLevel.VERIFIED: 100,
            VerificationLevel.FULL: 100,
        }
        
        return scores.get(level, 0)
    
    async def _calculate_community_score(self, user_id: str) -> float:
        """Community skorini hisoblash"""
        score = 0.0
        
        # Reviewlar
        reviews = self.reviews.get(user_id, [])
        
        if reviews:
            # O'rtacha reyting
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            score += (avg_rating / 5) * 50  # Max 50 points
            
            # Review soni
            if len(reviews) >= 50:
                score += 25
            elif len(reviews) >= 20:
                score += 20
            elif len(reviews) >= 10:
                score += 15
            elif len(reviews) >= 5:
                score += 10
            
            # Verified reviewlar
            verified_count = sum(1 for r in reviews if r.verified)
            if verified_count >= 10:
                score += 25
            elif verified_count >= 5:
                score += 15
            elif verified_count >= 1:
                score += 10
        
        return min(100, score)
    
    async def _update_community_score(self, user_id: str):
        """Userning community scoreni yangilash"""
        if user_id not in self.trust_scores:
            return
        
        trust_score = self.trust_scores[user_id]
        
        # Reviewlarni olish
        reviews = self.reviews.get(user_id, [])
        
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            trust_score.total_reviews_received = len(reviews)
            trust_score.avg_review_rating = avg_rating
            
            # Community scoreni yangilash
            trust_score.community_score = await self._calculate_community_score(user_id)
            
            # Overall scoreni qayta hisoblash
            trust_score.calculate_overall_score()
    
    def _calculate_consistency_score(
        self,
        trading_data: Dict[str, Any]
    ) -> float:
        """Izchillik skorini hisoblash"""
        score = 0.0
        
        # Trading frequency (regularity)
        days_active = trading_data.get('days_active', 0)
        account_age_days = trading_data.get('account_age_days', 1)
        
        if account_age_days > 0:
            activity_ratio = (days_active / account_age_days) * 100
            
            if activity_ratio >= 80:
                score += 40
            elif activity_ratio >= 60:
                score += 30
            elif activity_ratio >= 40:
                score += 20
            elif activity_ratio >= 20:
                score += 10
        
        # Drawdown control
        max_drawdown = abs(trading_data.get('max_drawdown', 100))
        if max_drawdown <= 10:
            score += 30
        elif max_drawdown <= 20:
            score += 20
        elif max_drawdown <= 30:
            score += 10
        
        # Risk management
        avg_risk_per_trade = trading_data.get('avg_risk_per_trade', 100)
        if avg_risk_per_trade <= 1:
            score += 30
        elif avg_risk_per_trade <= 2:
            score += 20
        elif avg_risk_per_trade <= 5:
            score += 10
        
        return min(100, score)
    
    def _calculate_transparency_score(
        self,
        trading_data: Dict[str, Any]
    ) -> float:
        """Shaffoflik skorini hisoblash"""
        score = 0.0
        
        # Public profile
        if trading_data.get('public_profile', False):
            score += 25
        
        # Shared statistics
        if trading_data.get('shared_statistics', False):
            score += 25
        
        # Verified trades
        verified_trades_pct = trading_data.get('verified_trades_pct', 0.0)
        score += verified_trades_pct * 0.3  # Max 30 points
        
        # Active communication (reviews given)
        reviews_given = trading_data.get('reviews_given', 0)
        if reviews_given >= 20:
            score += 20
        elif reviews_given >= 10:
            score += 15
        elif reviews_given >= 5:
            score += 10
        elif reviews_given >= 1:
            score += 5
        
        return min(100, score)
    
    def _update_badges(self, trust_score: TrustScore):
        """Badgelarni yangilash"""
        badges = []
        
        # Trust tier badge
        badges.append(f"trust_{trust_score.trust_tier.value}")
        
        # Verification badge
        if trust_score.verification_level == VerificationLevel.VERIFIED:
            badges.append("fully_verified")
        elif trust_score.verification_level == VerificationLevel.ID_DOCUMENT:
            badges.append("id_verified")
        
        # Trading badges
        if trust_score.trading_history_score >= 80:
            badges.append("expert_trader")
        elif trust_score.trading_history_score >= 60:
            badges.append("experienced_trader")
        
        # Community badges
        if trust_score.total_reviews_received >= 50:
            badges.append("highly_reviewed")
        
        if trust_score.avg_review_rating >= 4.5:
            badges.append("top_rated")
        
        # Account age badges
        if trust_score.account_age_days >= 365:
            badges.append("veteran")
        elif trust_score.account_age_days >= 180:
            badges.append("established")
        
        trust_score.badges = badges
    
    async def submit_verification(
        self,
        user_id: str,
        verification_type: VerificationLevel,
        documents: List[str] = None
    ) -> VerificationRequest:
        """
        Verification so'rovini yuborish
        
        Args:
            user_id: User ID
            verification_type: Verification turi
            documents: Hujjatlar ro'yxati
            
        Returns:
            VerificationRequest
        """
        try:
            request_id = f"verify_{user_id}_{datetime.now().timestamp()}"
            
            request = VerificationRequest(
                request_id=request_id,
                user_id=user_id,
                verification_type=verification_type,
                documents=documents or []
            )
            
            self.verifications[request_id] = request
            
            logger.info(
                f"Verification so'rovi yuborildi: {user_id} -> {verification_type.value}"
            )
            
            return request
            
        except Exception as e:
            logger.error(f"Verification so'rovini yuborishda xatolik: {e}")
            raise
    
    async def approve_verification(
        self,
        request_id: str,
        reviewer_notes: str = ""
    ) -> bool:
        """
        Verification so'rovini tasdiqlash
        
        Args:
            request_id: So'rov ID
            reviewer_notes: Ko'rib chiquvchi eslatmalari
            
        Returns:
            bool: Muvaffaqiyatli bo'lsa True
        """
        try:
            if request_id not in self.verifications:
                logger.error(f"Verification so'rovi topilmadi: {request_id}")
                return False
            
            request = self.verifications[request_id]
            request.status = "approved"
            request.reviewed_at = datetime.now()
            request.reviewer_notes = reviewer_notes
            
            # User verification level ni yangilash
            self.user_verifications[request.user_id] = request.verification_type
            
            # Trust scoreni yangilash
            if request.user_id in self.trust_scores:
                trust_score = self.trust_scores[request.user_id]
                trust_score.verification_score = self._calculate_verification_score(
                    request.user_id
                )
                trust_score.verification_level = request.verification_type
                trust_score.calculate_overall_score()
                self._update_badges(trust_score)
            
            logger.info(f"Verification tasdiqlandi: {request.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Verification tasdiqlashda xatolik: {e}")
            return False
    
    async def get_trust_score(self, user_id: str) -> Optional[TrustScore]:
        """
        User trust scoreni olish
        
        Args:
            user_id: User ID
            
        Returns:
            TrustScore yoki None
        """
        return self.trust_scores.get(user_id)
    
    async def get_top_trusted_users(
        self,
        limit: int = 50,
        min_tier: TrustTier = TrustTier.MEDIUM
    ) -> List[TrustScore]:
        """
        Eng ishonchli userlar
        
        Args:
            limit: Maksimal soni
            min_tier: Minimal trust tier
            
        Returns:
            Trust scorelar ro'yxati
        """
        # Tier order
        tier_order = {
            TrustTier.UNTRUSTED: 0,
            TrustTier.LOW: 1,
            TrustTier.MEDIUM: 2,
            TrustTier.HIGH: 3,
            TrustTier.VERY_HIGH: 4,
        }
        
        min_tier_value = tier_order[min_tier]
        
        # Filtr va saralash
        trusted_users = [
            score for score in self.trust_scores.values()
            if tier_order[score.trust_tier] >= min_tier_value
        ]
        
        trusted_users.sort(key=lambda x: x.overall_score, reverse=True)
        
        return trusted_users[:limit]
    
    async def get_verification_status(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        User verification statusini olish
        
        Args:
            user_id: User ID
            
        Returns:
            Verification status
        """
        level = self.user_verifications.get(user_id, VerificationLevel.UNVERIFIED)
        
        # Pending requestlar
        pending_requests = [
            req for req in self.verifications.values()
            if req.user_id == user_id and req.status == "pending"
        ]
        
        return {
            'current_level': level.value,
            'pending_requests': len(pending_requests),
            'can_upgrade': level != VerificationLevel.VERIFIED,
        }
    
    async def compare_trust_scores(
        self,
        user1_id: str,
        user2_id: str
    ) -> Dict[str, Any]:
        """
        Ikki userning trust scoreni solishtirish
        
        Args:
            user1_id: Birinchi user ID
            user2_id: Ikkinchi user ID
            
        Returns:
            Solishtirish natijalari
        """
        score1 = self.trust_scores.get(user1_id)
        score2 = self.trust_scores.get(user2_id)
        
        if not score1 or not score2:
            return {}
        
        return {
            'user1': score1.to_dict(),
            'user2': score2.to_dict(),
            'comparison': {
                'overall_difference': score1.overall_score - score2.overall_score,
                'trading_history_difference': score1.trading_history_score - score2.trading_history_score,
                'verification_difference': score1.verification_score - score2.verification_score,
                'community_difference': score1.community_score - score2.community_score,
                'higher_score': user1_id if score1.overall_score > score2.overall_score else user2_id,
            }
        }
    
    async def get_reputation_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Reputatsiya analitikasi
        
        Args:
            user_id: User ID
            
        Returns:
            Reputatsiya analitikasi
        """
        trust_score = self.trust_scores.get(user_id)
        if not trust_score:
            return {}
        
        reviews = self.reviews.get(user_id, [])
        
        # Review statistikasi
        review_stats = {
            'total_reviews': len(reviews),
            'average_rating': trust_score.avg_review_rating,
            'rating_distribution': {},
            'monthly_reviews': {},
            'verified_percentage': 0,
        }
        
        if reviews:
            # Rating taqsimoti
            for i in range(1, 6):
                review_stats['rating_distribution'][i] = sum(1 for r in reviews if r.rating == i)
            
            # Tasdiqlangan reviewlar foizi
            verified_count = sum(1 for r in reviews if r.verified)
            review_stats['verified_percentage'] = (verified_count / len(reviews)) * 100
            
            # Oylik reviewlar
            current_month = datetime.now().replace(day=1)
            monthly_count = sum(
                1 for r in reviews 
                if r.created_at >= current_month
            )
            review_stats['monthly_reviews'] = monthly_count
        
        # Trust score breakdown
        score_breakdown = {
            'overall_score': trust_score.overall_score,
            'trading_history': trust_score.trading_history_score,
            'verification': trust_score.verification_score,
            'community': trust_score.community_score,
            'consistency': trust_score.consistency_score,
            'transparency': trust_score.transparency_score,
        }
        
        return {
            'user_id': user_id,
            'trust_tier': trust_score.trust_tier.value,
            'trust_score_breakdown': score_breakdown,
            'review_statistics': review_stats,
            'account_age_days': trust_score.account_age_days,
            'badges': trust_score.badges,
            'last_updated': trust_score.last_updated.isoformat(),
        }
    
    async def get_reputation_trends(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Reputatsiya trendlar
        
        Args:
            user_id: User ID
            days: Kunlar soni
            
        Returns:
            Trend ma'lumotlari
        """
        reviews = self.reviews.get(user_id, [])
        if not reviews:
            return {}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_reviews = [r for r in reviews if r.created_at >= cutoff_date]
        
        if not recent_reviews:
            return {}
        
        # Rating trend
        rating_trend = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            day_reviews = [r for r in recent_reviews if r.created_at.date() == date.date()]
            if day_reviews:
                avg_rating = sum(r.rating for r in day_reviews) / len(day_reviews)
                rating_trend.append({
                    'date': date.date().isoformat(),
                    'rating': avg_rating,
                    'count': len(day_reviews)
                })
        
        # Overall trend
        return {
            'period_days': days,
            'total_reviews_period': len(recent_reviews),
            'average_rating_period': sum(r.rating for r in recent_reviews) / len(recent_reviews),
            'rating_trend': rating_trend,
            'trend_direction': 'improving' if len(recent_reviews) > 0 else 'stable',
        }
    
    async def update_trust_tier(self, user_id: str) -> TrustTier:
        """
        Trust tier ni yangilash
        
        Args:
            user_id: User ID
            
        Returns:
            Yangi trust tier
        """
        trust_score = self.trust_scores.get(user_id)
        if not trust_score:
            return TrustTier.NEW
        
        old_tier = trust_score.trust_tier
        score = trust_score.overall_score
        
        # Enhanced tier logic
        if score >= 95:
            new_tier = TrustTier.LEGEND
        elif score >= 90:
            new_tier = TrustTier.ELITE
        elif score >= 85:
            new_tier = TrustTier.VIP
        elif score >= 70:
            new_tier = TrustTier.PREMIUM
        elif score >= 50:
            new_tier = TrustTier.TRUSTED
        elif score >= 25:
            new_tier = TrustTier.BASIC
        else:
            new_tier = TrustTier.NEW
        
        trust_score.trust_tier = new_tier
        
        logger.info(f"Trust tier updated for {user_id}: {old_tier.value} -> {new_tier.value}")
        
        return new_tier
    
    async def award_badge(self, user_id: str, badge_name: str) -> bool:
        """
        Badge berish
        
        Args:
            user_id: User ID
            badge_name: Badge nomi
            
        Returns:
            bool: Muvaffaqiyatli bo'lsa True
        """
        trust_score = self.trust_scores.get(user_id)
        if not trust_score:
            return False
        
        if badge_name not in trust_score.badges:
            trust_score.badges.append(badge_name)
            logger.info(f"Badge awarded: {badge_name} to {user_id}")
            return True
        
        return False
    
    async def remove_badge(self, user_id: str, badge_name: str) -> bool:
        """
        Badge olib tashlash
        
        Args:
            user_id: User ID
            badge_name: Badge nomi
            
        Returns:
            bool: Muvaffaqiyatli bo'lsa True
        """
        trust_score = self.trust_scores.get(user_id)
        if not trust_score:
            return False
        
        if badge_name in trust_score.badges:
            trust_score.badges.remove(badge_name)
            logger.info(f"Badge removed: {badge_name} from {user_id}")
            return True
        
        return False
    
    async def get_reputation_leaderboard(
        self,
        metric: str = 'overall_score',
        limit: int = 100,
        min_reviews: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Reputatsiya leaderboard
        
        Args:
            metric: Saralash metrikasi
            limit: Limit
            min_reviews: Minimal review soni
            
        Returns:
            Leaderboard ro'yxati
        """
        qualified_users = [
            score for score in self.trust_scores.values()
            if score.total_reviews_received >= min_reviews
        ]
        
        # Saralash
        if metric == 'overall_score':
            qualified_users.sort(key=lambda x: x.overall_score, reverse=True)
        elif metric == 'trading_history':
            qualified_users.sort(key=lambda x: x.trading_history_score, reverse=True)
        elif metric == 'community':
            qualified_users.sort(key=lambda x: x.community_score, reverse=True)
        elif metric == 'avg_review_rating':
            qualified_users.sort(key=lambda x: x.avg_review_rating, reverse=True)
        
        return [score.to_dict() for score in qualified_users[:limit]]
    
    async def moderate_review(
        self,
        review_id: str,
        action: str,
        moderator_id: str,
        reason: str = ""
    ) -> bool:
        """
        Review moderatsiyasi
        
        Args:
            review_id: Review ID
            action: Harakat (hide, flag, delete, approve)
            moderator_id: Moderator ID
            reason: Sabab
            
        Returns:
            bool: Muvaffaqiyatli bo'lsa True
        """
        try:
            # Reviewni topish
            for target_reviews in self.reviews.values():
                for review in target_reviews:
                    if review.review_id == review_id:
                        if action == 'hide':
                            review.content = "[Yashirilgan review]"
                            review.title = "[Yashirilgan]"
                            review.pros = []
                            review.cons = []
                        elif action == 'flag':
                            # Flag qilish
                            pass
                        elif action == 'delete':
                            target_reviews.remove(review)
                        elif action == 'approve':
                            review.verified = True
                        
                        logger.info(
                            f"Review moderated: {review_id} - {action} by {moderator_id}"
                        )
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Review moderatsiyasida xatolik: {e}")
            return False
    
    async def calculate_impact_score(self, user_id: str) -> float:
        """
        Ta'sir reytingini hisoblash
        
        Args:
            user_id: User ID
            
        Returns:
            Impact score (0-100)
        """
        trust_score = self.trust_scores.get(user_id)
        if not trust_score:
            return 0.0
        
        # Impact score komponentlari
        impact_factors = {
            'trust_level': (trust_score.overall_score / 100) * 30,
            'review_count': min(20, trust_score.total_reviews_received) * 2,
            'verification_level': (trust_score.verification_score / 100) * 25,
            'community_engagement': (trust_score.community_score / 100) * 25,
        }
        
        total_impact = sum(impact_factors.values())
        
        return min(100.0, total_impact)
    
    async def export_reputation_data(self, user_id: str) -> Dict[str, Any]:
        """
        Reputatsiya ma'lumotlarini eksport qilish
        
        Args:
            user_id: User ID
            
        Returns:
            Eksport ma'lumotlari
        """
        trust_score = self.trust_scores.get(user_id)
        reviews = self.reviews.get(user_id, [])
        
        return {
            'user_id': user_id,
            'export_timestamp': datetime.now().isoformat(),
            'trust_score': trust_score.to_dict() if trust_score else {},
            'reviews': [review.to_dict() for review in reviews],
            'verification_status': await self.get_verification_status(user_id),
            'analytics': await self.get_reputation_analytics(user_id),
            'trends': await self.get_reputation_trends(user_id),
        }
    
    async def get_reputation_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Reputatsiya xulosasi
        
        Args:
            user_id: User ID
            
        Returns:
            Reputatsiya xulosasi
        """
        trust_score = self.trust_scores.get(user_id)
        if not trust_score:
            return {
                'user_id': user_id,
                'trust_score': 0.0,
                'trust_tier': TrustTier.NEW.value,
                'verification_level': VerificationLevel.UNVERIFIED.value,
                'total_reviews': 0,
                'badges': []
            }
        
        return {
            'user_id': user_id,
            'trust_score': trust_score.overall_score,
            'trust_tier': trust_score.trust_tier.value,
            'verification_level': trust_score.verification_level.value,
            'total_reviews': trust_score.total_reviews_received,
            'positive_reviews': sum(1 for r in self.reviews.get(user_id, []) if r.rating >= 4),
            'neutral_reviews': sum(1 for r in self.reviews.get(user_id, []) if r.rating == 3),
            'negative_reviews': sum(1 for r in self.reviews.get(user_id, []) if r.rating <= 2),
            'average_rating': trust_score.avg_review_rating,
            'badges': trust_score.badges,
            'account_age_days': trust_score.account_age_days,
            'last_updated': trust_score.last_updated.isoformat(),
        }
    
    async def bulk_update_trust_scores(self) -> Dict[str, int]:
        """
        Barcha userlar uchun trust scorelarni yangilash
        
        Returns:
            Yangilangan userlar soni
        """
        updated_count = 0
        failed_count = 0
        
        for user_id in list(self.trust_scores.keys()):
            try:
                trust_score = self.trust_scores[user_id]
                trust_score.calculate_overall_score()
                await self.update_trust_tier(user_id)
                updated_count += 1
            except Exception as e:
                logger.error(f"Trust score update failed for {user_id}: {e}")
                failed_count += 1
        
        return {
            'updated': updated_count,
            'failed': failed_count,
            'total': len(self.trust_scores)
        }


# Utility Functions / Yordamchi Funksiyalar

def create_sample_reviews(system: ReputationSystem, count: int = 10) -> List[str]:
    """
    Namuna reviewlar yaratish
    
    Args:
        system: ReputationSystem instance
        count: Yaratiladigan reviewlar soni
        
    Returns:
        Yaratilgan review ID lar ro'yxati
    """
    import uuid
    
    sample_data = [
        {
            'reviewer_id': 'user1',
            'reviewer_name': 'Ali Karimov',
            'target_id': 'trader1',
            'target_type': ReviewType.TRADER,
            'rating': 5,
            'title': 'Ajoyib trader!',
            'content': 'Bu trader juda professional va natijalar ajoyib.',
            'pros': ['Professional', 'Natijalar yaxshi', 'Ishonchli'],
            'cons': ['Kamda-kam'],
            'verified': True
        },
        {
            'reviewer_id': 'user2',
            'reviewer_name': 'Gulbahor Saidova',
            'target_id': 'trader1',
            'target_type': ReviewType.TRADER,
            'rating': 4,
            'title': 'Yaxshi tajriba',
            'content': 'Umumiy olganda yaxshi, lekin ba\'zi borishlar борча бор.',
            'pros': ['Natijalar yaxshi', 'Muloqot yaxshi'],
            'cons': ['Ba\'zi хатоc бор'],
            'verified': True
        },
        {
            'reviewer_id': 'user3',
            'reviewer_name': 'Bobur Rahimov',
            'target_id': 'strategy1',
            'target_type': ReviewType.STRATEGY,
            'rating': 5,
            'title': 'Samarali strategiya',
            'content': 'Bu strategiya juda yaxshi ishlaydi va foyda olib keladi.',
            'pros': ['Samarali', 'Quyidagi natija', 'Oson tushunish'],
            'cons': ['Yo\'q'],
            'verified': False
        },
        {
            'reviewer_id': 'user4',
            'reviewer_name': 'Malika Azizova',
            'target_id': 'user5',
            'target_type': ReviewType.USER,
            'rating': 3,
            'title': 'O\'rtacha',
            'content': 'Hech qanday ajoyib emas, lekin yomon ham emas.',
            'pros': ['Hech qanday'],
            'cons': ['Aktiv emas', 'Javob bermaydi'],
            'verified': False
        },
        {
            'reviewer_id': 'user5',
            'reviewer_name': 'Jasur Normatov',
            'target_id': 'signal_provider1',
            'target_type': ReviewType.SIGNAL_PROVIDER,
            'rating': 4,
            'title': 'Signal provider',
            'content': 'Yaxshi signallar beradi va analizlar ajoyib.',
            'pros': ['Tez javob', 'Aniq analiz', 'Yordamchi'],
            'cons': ['Ba\'zi signallar noto\'g\'ri'],
            'verified': True
        }
    ]
    
    created_reviews = []
    
    # Create a new event loop for this function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def create_reviews_async():
        for i in range(min(count, len(sample_data))):
            data = sample_data[i % len(sample_data)]
            
            review = Review(
                review_id=f"review_{uuid.uuid4().hex[:8]}",
                **data
            )
            
            await system.submit_review(review)
            created_reviews.append(review.review_id)
    
    loop.run_until_complete(create_reviews_async())
    loop.close()
    
    return created_reviews


def create_sample_verifications(system: ReputationSystem) -> List[str]:
    """
    Namuna verifikatsiyalar yaratish
    
    Args:
        system: ReputationSystem instance
        
    Returns:
        Yaratilgan verification ID lar ro'yxati
    """
    import asyncio
    
    sample_users = [
        ('user1', VerificationLevel.FULL),
        ('user2', VerificationLevel.ID_DOCUMENT),
        ('user3', VerificationLevel.PHONE),
        ('trader1', VerificationLevel.FULL),
        ('signal_provider1', VerificationLevel.HIGH),
    ]
    
    created_verifications = []
    
    # Create a new event loop for this function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def create_verifications_async():
        for user_id, level in sample_users:
            request = await system.submit_verification(
                user_id=user_id,
                verification_type=level
            )
            
            # Tasdiqlash
            await system.approve_verification(
                request_id=request.request_id,
                reviewer_notes="Avtomatik tasdiqlangan"
            )
            
            created_verifications.append(request.request_id)
    
    loop.run_until_complete(create_verifications_async())
    loop.close()
    
    return created_verifications


def calculate_comprehensive_trust_score(
    trading_data: Dict[str, Any],
    community_data: Dict[str, Any],
    verification_data: Dict[str, Any]
) -> Dict[str, float]:
    """
    Keng qamrovli trust score hisoblash
    
    Args:
        trading_data: Trading ma'lumotlari
        community_data: Jamoa ma'lumotlari
        verification_data: Verifikatsiya ma'lumotlari
        
    Returns:
        Score breakdown
    """
    # Trading score
    win_rate = trading_data.get('win_rate', 0)
    total_trades = trading_data.get('total_trades', 0)
    profit_factor = trading_data.get('profit_factor', 0)
    
    trading_score = min(100, (
        (win_rate / 100) * 30 +
        min(30, total_trades / 10) +
        (profit_factor * 20)
    ))
    
    # Community score
    avg_rating = community_data.get('average_rating', 0)
    review_count = community_data.get('review_count', 0)
    helpful_votes = community_data.get('helpful_votes', 0)
    
    community_score = min(100, (
        (avg_rating / 5) * 40 +
        min(30, review_count / 5) +
        min(20, helpful_votes / 10)
    ))
    
    # Verification score
    verification_level = verification_data.get('level', VerificationLevel.UNVERIFIED)
    verification_score = verification_level.value * 20
    
    # Overall
    overall_score = (trading_score * 0.4 + community_score * 0.3 + verification_score * 0.3)
    
    return {
        'trading_score': round(trading_score, 2),
        'community_score': round(community_score, 2),
        'verification_score': round(verification_score, 2),
        'overall_score': round(overall_score, 2)
    }


def get_reputation_recommendations(user_id: str, trust_score: float, badges: List[str]) -> List[str]:
    """
    Reputatsiya takliflar
    
    Args:
        user_id: User ID
        trust_score: Trust score
        badges: Badge list
        
    Returns:
        Takliflar ro'yxati
    """
    recommendations = []
    
    if trust_score < 25:
        recommendations.append("Aktiv savdo qilish va ko'proq review qoldirish")
        recommendations.append("Email va telefon tasdiqlash")
    
    if trust_score < 50:
        recommendations.append("Professional profili to'ldirish")
        recommendations.append("Ko'proq foydalanuvchilar bilan muloqot qilish")
    
    if trust_score < 70:
        recommendations.append("Communityda aktiv ishtirok etish")
        recommendations.append("Foydali review va ko'rsatmalar berish")
    
    if trust_score < 85:
        recommendations.append("Yuqori sifatli kontent yaratish")
        recommendations.append("Verification level oshirish")
    
    if "trust_basic" not in badges and trust_score >= 25:
        recommendations.append("Trust Basic badge olish imkoniyati bor")
    
    if "verified_trader" not in badges and trust_score >= 70:
        recommendations.append("Verified Trader badge olish uchun arizalar yuborish")
    
    return recommendations


# Demo Usage / Namuna Foydalanish
if __name__ == "__main__":
    def demo():
        """Reputatsiya tizimi demo"""
        print("=== REPUTATSIYA TIZIMI DEMO ===\n")
        
        # Tizim yaratish
        reputation_system = ReputationSystem()
        
        # Namuna ma'lumotlar
        print("1. Namuna reviewlar yaratilmoqda...")
        created_reviews = create_sample_reviews(reputation_system, 5)
        print(f"   {len(created_reviews)} ta review yaratildi\n")
        
        print("2. Namuna verifikatsiyalar yaratilmoqda...")
        created_verifications = create_sample_verifications(reputation_system)
        print(f"   {len(created_verifications)} ta verifikatsiya yaratildi\n")
        
        # Trust score hisoblash
        print("3. Trust score hisoblash...")
        sample_trading_data = {
            'win_rate': 65,
            'total_trades': 150,
            'profit_factor': 1.8,
            'account_created': datetime.now() - timedelta(days=365),
            'public_profile': True,
            'shared_statistics': True,
            'verified_trades_pct': 80,
            'reviews_given': 10
        }
        
        # Sync wrapper for async trust score calculation
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        trust_score = loop.run_until_complete(
            reputation_system.calculate_trust_score(
                user_id="trader1",
                username="Professional Trader",
                trading_data=sample_trading_data
            )
        )
        
        loop.close()
        
        print(f"   Trust score: {trust_score.overall_score}")
        print(f"   Trust tier: {trust_score.trust_tier.value}")
        print(f"   Badges: {', '.join(trust_score.badges)}\n")
        
        # Reviewlarni olish
        print("4. Reviewlarni olish...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        reviews = loop.run_until_complete(
            reputation_system.get_reviews(
                target_id="trader1",
                verified_only=False,
                limit=10
            )
        )
        
        loop.close()
        print(f"   {len(reviews)} ta review topildi\n")
        
        # Reputatsiya analytics
        print("5. Reputatsiya analitikasi...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        analytics = loop.run_until_complete(
            reputation_system.get_reputation_analytics("trader1")
        )
        
        loop.close()
        
        if analytics:
            print(f"   Umumiy score: {analytics['trust_score_breakdown']['overall_score']}")
            print(f"   Jamoa score: {analytics['trust_score_breakdown']['community']}")
            print(f"   Tasdiqlash score: {analytics['trust_score_breakdown']['verification']}\n")
        
        # Leaderboard
        print("6. Leaderboard...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        leaderboard = loop.run_until_complete(
            reputation_system.get_reputation_leaderboard(
                metric='overall_score',
                limit=5,
                min_reviews=1
            )
        )
        
        loop.close()
        
        print(f"   {len(leaderboard)} ta foydalanuvchi topildi")
        for i, user in enumerate(leaderboard[:3], 1):
            print(f"   {i}. {user['username']}: {user['overall_score']} ({user['trust_tier']})")
        
        print("\n=== DEMO TUGADI ===")
    
    # Demo ishga tushirish
    demo()
