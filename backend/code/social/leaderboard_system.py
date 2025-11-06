"""
Leaderboard System - Traderlar reytingi va performance metrikalar
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class RankCategory(Enum):
    """Reyting kategoriyalari"""
    OVERALL = "overall"  # Umumiy
    DAILY = "daily"  # Kunlik
    WEEKLY = "weekly"  # Haftalik
    MONTHLY = "monthly"  # Oylik
    QUARTERLY = "quarterly"  # Kvartalik
    YEARLY = "yearly"  # Yillik


class TraderRank(Enum):
    """Trader rank based on overall performance"""
    BRIZILGAN = "brizilgan"  # Bronze
    ORTACHA = "ortacha"     # Silver
    YAXSHI = "yaxshi"         # Gold
    ALO = "alo"             # Platinum
    USTUN = "ustun"           # Diamond
    LEGEND = "legend"         # Legendary


class TraderTier(Enum):
    """Trader darajalari"""
    BRONZE = "bronze"
    SILVER = "silver" 
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"


class TrustTier(Enum):
    """Trust verification levels"""
    NEWBIE = "newbie"
    TRUSTED = "trusted"
    VERIFIED = "verified"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class PerformanceScore:
    """Performance hisoblash ballari"""
    total_pnl: float = 0.0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    consistency: float = 0.0  # 0-100
    risk_management: float = 0.0  # 0-100
    
    # Vaznlar
    WEIGHTS = {
        'total_pnl': 0.25,
        'win_rate': 0.15,
        'sharpe_ratio': 0.20,
        'profit_factor': 0.15,
        'max_drawdown': 0.10,
        'consistency': 0.10,
        'risk_management': 0.05,
    }
    
    def calculate_score(self) -> float:
        """
        Umumiy scoreni hisoblash (0-100)
        
        Returns:
            Hisoblangan ball
        """
        # PnL normalizatsiya (0-100)
        pnl_score = min(100, max(0, (self.total_pnl / 1000) * 10))
        
        # Win rate allaqachon 0-100
        win_rate_score = self.win_rate
        
        # Sharpe ratio normalizatsiya (0-5 -> 0-100)
        sharpe_score = min(100, max(0, (self.sharpe_ratio / 5) * 100))
        
        # Profit factor normalizatsiya (0-3 -> 0-100)
        pf_score = min(100, max(0, (self.profit_factor / 3) * 100))
        
        # Max drawdown (kam yaxshi, 0-100)
        dd_score = max(0, 100 - abs(self.max_drawdown))
        
        # Weighted score
        score = (
            pnl_score * self.WEIGHTS['total_pnl'] +
            win_rate_score * self.WEIGHTS['win_rate'] +
            sharpe_score * self.WEIGHTS['sharpe_ratio'] +
            pf_score * self.WEIGHTS['profit_factor'] +
            dd_score * self.WEIGHTS['max_drawdown'] +
            self.consistency * self.WEIGHTS['consistency'] +
            self.risk_management * self.WEIGHTS['risk_management']
        )
        
        return round(score, 2)
    
    def to_dict(self) -> Dict:
        return {
            'total_pnl': self.total_pnl,
            'win_rate': self.win_rate,
            'sharpe_ratio': self.sharpe_ratio,
            'profit_factor': self.profit_factor,
            'max_drawdown': self.max_drawdown,
            'consistency': self.consistency,
            'risk_management': self.risk_management,
            'overall_score': self.calculate_score(),
        }


@dataclass
class TraderPerformance:
    """Trader performance data"""
    trader_id: str
    username: str
    rank: int = 0
    previous_rank: int = 0
    rank_enum: TraderRank = TraderRank.BRIZILGAN
    tier: TraderTier = TraderTier.BRONZE
    trust_tier: TrustTier = TrustTier.NEWBIE
    category: RankCategory = RankCategory.OVERALL
    score: PerformanceScore = field(default_factory=PerformanceScore)
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_volume: float = 0.0
    followers: int = 0
    verified: bool = False
    badges: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    join_date: datetime = field(default_factory=datetime.now)
    reputation_score: float = 0.0
    
    def get_rank_change(self) -> int:
        """Reyting o'zgarishi"""
        return self.previous_rank - self.rank if self.previous_rank > 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            'trader_id': self.trader_id,
            'username': self.username,
            'rank': self.rank,
            'previous_rank': self.previous_rank,
            'rank_change': self.get_rank_change(),
            'rank_enum': self.rank_enum.value,
            'tier': self.tier.value,
            'trust_tier': self.trust_tier.value,
            'category': self.category.value,
            'score': self.score.to_dict(),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            'total_volume': self.total_volume,
            'followers': self.followers,
            'verified': self.verified,
            'badges': self.badges,
            'achievements': self.achievements,
            'last_updated': self.last_updated.isoformat(),
            'join_date': self.join_date.isoformat(),
            'reputation_score': self.reputation_score,
        }


@dataclass
class Achievement:
    """Yutuq"""
    achievement_id: str
    name: str
    description: str
    icon: str
    category: str  # trading, consistency, volume, social
    condition: str  # Qanday qilib olish mumkin
    rarity: str = "common"  # common, rare, epic, legendary
    points: int = 10
    
    def to_dict(self) -> Dict:
        return {
            'achievement_id': self.achievement_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'condition': self.condition,
            'rarity': self.rarity,
            'points': self.points,
        }


class LeaderboardSystem:
    """
    Leaderboard System - Traderlarni reytinglash va
    performance metrikalarini kuzatish
    """
    
    def __init__(self):
        self.rankings: Dict[RankCategory, List[TraderPerformance]] = {
            category: [] for category in RankCategory
        }
        self.traders: Dict[str, TraderPerformance] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.trader_achievements: Dict[str, List[str]] = {}  # trader_id -> achievement_ids
        
        # Predefined achievements
        self._initialize_achievements()
    
    def _initialize_achievements(self):
        """Standart yutuqlarni initsializatsiya qilish"""
        achievements = [
            # Trading achievements
            Achievement(
                "first_trade",
                "Birinchi Trade",
                "Birinchi tradeingizni amalga oshiring",
                "🎯",
                "trading",
                "1 ta trade qiling",
                "common",
                10
            ),
            Achievement(
                "profitable_week",
                "Foydali Hafta",
                "Bir hafta davomida foyda keltiring",
                "📈",
                "trading",
                "Haftalik PnL > 0",
                "rare",
                50
            ),
            Achievement(
                "10_wins_streak",
                "10 Muvaffaqiyat Ketma-ket",
                "Ketma-ket 10 ta daromadli trade",
                "🔥",
                "trading",
                "10 winning streak",
                "epic",
                100
            ),
            Achievement(
                "100_trades",
                "Yuzta Trade",
                "100 ta trade amalga oshiring",
                "💯",
                "volume",
                "Total trades >= 100",
                "rare",
                75
            ),
            Achievement(
                "1000_trades",
                "Ming Trade",
                "1000 ta trade amalga oshiring",
                "🏆",
                "volume",
                "Total trades >= 1000",
                "legendary",
                500
            ),
            # Consistency achievements
            Achievement(
                "consistent_trader",
                "Izchil Trader",
                "30 kun davomida har kuni trade qiling",
                "📅",
                "consistency",
                "30 kun ketma-ket trading",
                "epic",
                200
            ),
            Achievement(
                "sharp_trader",
                "Sharp Trader",
                "Sharpe ratio > 2.0 ga erishing",
                "⚡",
                "consistency",
                "Sharpe ratio > 2.0",
                "epic",
                150
            ),
            # Social achievements
            Achievement(
                "top_10",
                "Top 10",
                "Leaderboardda top 10 ga kiring",
                "🥇",
                "social",
                "Rank <= 10",
                "legendary",
                300
            ),
            Achievement(
                "100_followers",
                "Popular Trader",
                "100 ta follower to'plang",
                "👥",
                "social",
                "Followers >= 100",
                "rare",
                100
            ),
        ]
        
        for ach in achievements:
            self.achievements[ach.achievement_id] = ach
    
    async def update_trader_rank(
        self,
        trader_id: str,
        username: str,
        performance_data: Dict[str, Any],
        category: RankCategory = RankCategory.OVERALL
    ) -> TraderPerformance:
        """
        Trader reytingini yangilash
        
        Args:
            trader_id: Trader ID
            username: Trader nomi
            performance_data: Performance ma'lumotlari
            category: Reyting kategoriyasi
            
        Returns:
            Yangilangan TraderRank
        """
        try:
            # Performance score yaratish
            score = PerformanceScore(
                total_pnl=performance_data.get('total_pnl', 0.0),
                win_rate=performance_data.get('win_rate', 0.0),
                sharpe_ratio=performance_data.get('sharpe_ratio', 0.0),
                profit_factor=performance_data.get('profit_factor', 0.0),
                max_drawdown=performance_data.get('max_drawdown', 0.0),
                consistency=performance_data.get('consistency', 0.0),
                risk_management=performance_data.get('risk_management', 0.0),
            )
            
            # Mavjud rank topish yoki yangi yaratish
            if trader_id in self.traders:
                trader_rank = self.traders[trader_id]
                trader_rank.previous_rank = trader_rank.rank
                trader_rank.score = score
            else:
                trader_rank = TraderPerformance(
                    trader_id=trader_id,
                    username=username,
                    score=score,
                    category=category
                )
            
            # Trade statistikasini yangilash
            trader_rank.total_trades = performance_data.get('total_trades', 0)
            trader_rank.winning_trades = performance_data.get('winning_trades', 0)
            trader_rank.losing_trades = performance_data.get('losing_trades', 0)
            trader_rank.total_volume = performance_data.get('total_volume', 0.0)
            trader_rank.followers = performance_data.get('followers', 0)
            trader_rank.verified = performance_data.get('verified', False)
            trader_rank.last_updated = datetime.now()
            
            # Tier aniqlash
            trader_rank.tier = self._determine_tier(trader_rank.total_trades)
            
            # Saqlash
            self.traders[trader_id] = trader_rank
            
            # Rankingni yangilash
            await self._update_rankings(category)
            
            # Yutuqlarni tekshirish
            await self._check_achievements(trader_id, trader_rank)
            
            logger.info(
                f"Trader reytingi yangilandi: {username} "
                f"Score: {score.calculate_score():.2f}"
            )
            return trader_rank
            
        except Exception as e:
            logger.error(f"Trader reytingini yangilashda xatolik: {e}")
            raise
    
    def _determine_tier(self, total_trades: int) -> TraderTier:
        """
        Traderning darajasini aniqlash
        
        Args:
            total_trades: Umumiy tradelar soni
            
        Returns:
            TraderTier
        """
        if total_trades < 10:
            return TraderTier.BRONZE
        elif total_trades < 50:
            return TraderTier.SILVER
        elif total_trades < 200:
            return TraderTier.GOLD
        elif total_trades < 500:
            return TraderTier.PLATINUM
        elif total_trades < 1000:
            return TraderTier.DIAMOND
        else:
            return TraderTier.LEGENDARY
    
    async def _update_rankings(self, category: RankCategory):
        """
        Reyting ro'yxatini yangilash
        
        Args:
            category: Kategoriya
        """
        # Shu kategoriya bo'yicha barcha traderlar
        traders = [
            t for t in self.traders.values()
            if t.category == category
        ]
        
        # Score bo'yicha saralash
        traders.sort(key=lambda x: x.score.calculate_score(), reverse=True)
        
        # Rank raqamlarini belgilash
        for i, trader in enumerate(traders, 1):
            trader.rank = i
        
        # Saqlash
        self.rankings[category] = traders
    
    async def get_leaderboard(
        self,
        category: RankCategory = RankCategory.OVERALL,
        limit: int = 100,
        tier: Optional[TraderTier] = None
    ) -> List[TraderPerformance]:
        """
        Leaderboard ro'yxatini olish
        
        Args:
            category: Kategoriya
            limit: Maksimal soni
            tier: Tier filtri
            
        Returns:
            Trader ranklari ro'yxati
        """
        rankings = self.rankings.get(category, [])
        
        # Tier filtri
        if tier:
            rankings = [r for r in rankings if r.tier == tier]
        
        return rankings[:limit]
    
    async def get_trader_rank(
        self,
        trader_id: str,
        category: RankCategory = RankCategory.OVERALL
    ) -> Optional[TraderPerformance]:
        """
        Bitta traderning reytingini olish
        
        Args:
            trader_id: Trader ID
            category: Kategoriya
            
        Returns:
            TraderRank yoki None
        """
        trader = self.traders.get(trader_id)
        
        if trader and trader.category == category:
            return trader
        
        return None
    
    async def get_rank_by_position(
        self,
        position: int,
        category: RankCategory = RankCategory.OVERALL
    ) -> Optional[TraderPerformance]:
        """
        Pozitsiya bo'yicha trader reytingini olish
        
        Args:
            position: Pozitsiya (1-top)
            category: Kategoriya
            
        Returns:
            TraderRank yoki None
        """
        rankings = self.rankings.get(category, [])
        
        if 0 < position <= len(rankings):
            return rankings[position - 1]
        
        return None
    
    async def get_nearby_ranks(
        self,
        trader_id: str,
        category: RankCategory = RankCategory.OVERALL,
        range_size: int = 5
    ) -> List[TraderPerformance]:
        """
        Trader atrofidagi ranklarni olish
        
        Args:
            trader_id: Trader ID
            category: Kategoriya
            range_size: Har bir tomonda nechta rank
            
        Returns:
            Atrofdagi ranklarning ro'yxati
        """
        trader = await self.get_trader_rank(trader_id, category)
        if not trader:
            return []
        
        rankings = self.rankings.get(category, [])
        
        # Index topish
        try:
            index = rankings.index(trader)
        except ValueError:
            return []
        
        # Range hisoblash
        start = max(0, index - range_size)
        end = min(len(rankings), index + range_size + 1)
        
        return rankings[start:end]
    
    async def _check_achievements(
        self,
        trader_id: str,
        trader_rank: TraderPerformance
    ):
        """
        Trader yutuqlarini tekshirish
        
        Args:
            trader_id: Trader ID
            trader_rank: Trader reytingi
        """
        try:
            if trader_id not in self.trader_achievements:
                self.trader_achievements[trader_id] = []
            
            current_achievements = self.trader_achievements[trader_id]
            new_achievements = []
            
            # Har bir yutuqni tekshirish
            for ach_id, achievement in self.achievements.items():
                # Allaqachon olingan yutuqlarni o'tkazib yuborish
                if ach_id in current_achievements:
                    continue
                
                # Shart tekshirish
                earned = False
                
                if ach_id == "first_trade" and trader_rank.total_trades >= 1:
                    earned = True
                elif ach_id == "100_trades" and trader_rank.total_trades >= 100:
                    earned = True
                elif ach_id == "1000_trades" and trader_rank.total_trades >= 1000:
                    earned = True
                elif ach_id == "sharp_trader" and trader_rank.score.sharpe_ratio > 2.0:
                    earned = True
                elif ach_id == "top_10" and trader_rank.rank <= 10:
                    earned = True
                elif ach_id == "100_followers" and trader_rank.followers >= 100:
                    earned = True
                
                if earned:
                    new_achievements.append(ach_id)
                    current_achievements.append(ach_id)
                    trader_rank.achievements.append(achievement.name)
                    
                    logger.info(
                        f"Yangi yutuq: {trader_rank.username} -> {achievement.name}"
                    )
            
            # Badge larni yangilash (tier asosida)
            self._update_badges(trader_rank)
            
        except Exception as e:
            logger.error(f"Yutuqlarni tekshirishda xatolik: {e}")
    
    def _update_badges(self, trader_rank: TraderPerformance):
        """
        Trader badgelarini yangilash
        
        Args:
            trader_rank: Trader reytingi
        """
        badges = []
        
        # Tier badge
        badges.append(f"tier_{trader_rank.tier.value}")
        
        # Top rank badges
        if trader_rank.rank == 1:
            badges.append("rank_1st")
        elif trader_rank.rank <= 3:
            badges.append("rank_top3")
        elif trader_rank.rank <= 10:
            badges.append("rank_top10")
        elif trader_rank.rank <= 100:
            badges.append("rank_top100")
        
        # Win rate badges
        win_rate = (trader_rank.winning_trades / trader_rank.total_trades * 100) if trader_rank.total_trades > 0 else 0
        if win_rate >= 80:
            badges.append("winrate_80plus")
        elif win_rate >= 70:
            badges.append("winrate_70plus")
        
        # Verified badge
        if trader_rank.verified:
            badges.append("verified")
        
        trader_rank.badges = badges
    
    async def get_statistics(
        self,
        category: RankCategory = RankCategory.OVERALL
    ) -> Dict[str, Any]:
        """
        Leaderboard statistikasini olish
        
        Args:
            category: Kategoriya
            
        Returns:
            Statistika ma'lumotlari
        """
        rankings = self.rankings.get(category, [])
        
        if not rankings:
            return {
                'total_traders': 0,
                'avg_score': 0.0,
                'top_score': 0.0,
            }
        
        scores = [r.score.calculate_score() for r in rankings]
        
        # Tier bo'yicha taqsimlash
        tier_distribution = {}
        for tier in TraderTier:
            count = sum(1 for r in rankings if r.tier == tier)
            tier_distribution[tier.value] = count
        
        return {
            'total_traders': len(rankings),
            'avg_score': sum(scores) / len(scores),
            'top_score': max(scores),
            'min_score': min(scores),
            'tier_distribution': tier_distribution,
            'total_trades': sum(r.total_trades for r in rankings),
            'total_volume': sum(r.total_volume for r in rankings),
        }
    
    async def get_rising_stars(
        self,
        category: RankCategory = RankCategory.OVERALL,
        limit: int = 10
    ) -> List[TraderPerformance]:
        """
        Eng ko'p ko'tarilgan traderlar (rising stars)
        
        Args:
            category: Kategoriya
            limit: Maksimal soni
            
        Returns:
            Rising stars ro'yxati
        """
        rankings = self.rankings.get(category, [])
        
        # Rank o'zgarishi bo'yicha saralash
        rising = [
            r for r in rankings
            if r.get_rank_change() > 0
        ]
        rising.sort(key=lambda x: x.get_rank_change(), reverse=True)
        
        return rising[:limit]
    
    async def get_achievements_list(self) -> List[Achievement]:
        """
        Barcha yutuqlar ro'yxati
        
        Returns:
            Achievements ro'yxati
        """
        return list(self.achievements.values())
    
    async def get_trader_achievements(
        self,
        trader_id: str
    ) -> List[Achievement]:
        """
        Trader yutuqlari
        
        Args:
            trader_id: Trader ID
            
        Returns:
            Trader olgan yutuqlar
        """
        if trader_id not in self.trader_achievements:
            return []
        
        achievement_ids = self.trader_achievements[trader_id]
        
        return [
            self.achievements[ach_id]
            for ach_id in achievement_ids
            if ach_id in self.achievements
        ]
    
    async def compare_traders(
        self,
        trader1_id: str,
        trader2_id: str,
        category: RankCategory = RankCategory.OVERALL
    ) -> Dict[str, Any]:
        """
        Ikki traderni solishtirish
        
        Args:
            trader1_id: Birinchi trader ID
            trader2_id: Ikkinchi trader ID
            category: Kategoriya
            
        Returns:
            Solishtirish natijalari
        """
        trader1 = await self.get_trader_rank(trader1_id, category)
        trader2 = await self.get_trader_rank(trader2_id, category)
        
        if not trader1 or not trader2:
            return {}
        
        return {
            'trader1': trader1.to_dict(),
            'trader2': trader2.to_dict(),
            'comparison': {
                'rank_difference': trader1.rank - trader2.rank,
                'score_difference': trader1.score.calculate_score() - trader2.score.calculate_score(),
                'pnl_difference': trader1.score.total_pnl - trader2.score.total_pnl,
                'win_rate_difference': trader1.score.win_rate - trader2.score.win_rate,
                'trades_difference': trader1.total_trades - trader2.total_trades,
            }
        }

    async def get_achievements(
        self,
        trader_id: str,
        include_progress: bool = False
    ) -> Dict[str, Any]:
        """
        Trader achievements va progress ma'lumotlari
        
        Args:
            trader_id: Trader ID
            include_progress: Progress ma'lumotlarini ham qo'shish
            
        Returns:
            Achievement ma'lumotlari
        """
        trader = self.traders.get(trader_id)
        if not trader:
            return {
                'trader_id': trader_id,
                'achievements': [],
                'total_points': 0,
                'progress': []
            }
        
        # Olingan yutuqlar
        earned_achievements = await self.get_trader_achievements(trader_id)
        
        # Jami ochkolar
        total_points = sum(ach.points for ach in earned_achievements)
        
        result = {
            'trader_id': trader_id,
            'username': trader.username,
            'achievements': [ach.to_dict() for ach in earned_achievements],
            'total_achievements': len(earned_achievements),
            'total_points': total_points,
            'last_updated': trader.last_updated.isoformat()
        }
        
        # Progress ma'lumotlarini qo'shish
        if include_progress:
            result['progress'] = await self._get_achievement_progress(trader_id)
        
        return result

    async def _get_achievement_progress(
        self,
        trader_id: str
    ) -> List[Dict[str, Any]]:
        """Achievement progress ma'lumotlari"""
        trader = self.traders.get(trader_id)
        if not trader:
            return []
        
        progress = []
        
        # Har bir achievement uchun progress
        for ach_id, achievement in self.achievements.items():
            if ach_id in self.trader_achievements.get(trader_id, []):
                # Allaqachon olingan
                progress.append({
                    'achievement_id': ach_id,
                    'name': achievement.name,
                    'progress': 100,
                    'completed': True,
                    'completed_at': trader.last_updated.isoformat()
                })
            else:
                # Hali olinmagan - progress hisoblash
                completion_percent = self._calculate_achievement_progress(trader, achievement)
                progress.append({
                    'achievement_id': ach_id,
                    'name': achievement.name,
                    'progress': completion_percent,
                    'completed': completion_percent >= 100,
                    'condition': achievement.condition
                })
        
        return progress

    def _calculate_achievement_progress(
        self,
        trader: TraderRank,
        achievement: Achievement
    ) -> float:
        """Achievement progress hisoblash"""
        ach_id = achievement.achievement_id
        
        if ach_id == "first_trade":
            return min(100, (trader.total_trades / 1) * 100)
        elif ach_id == "100_trades":
            return min(100, (trader.total_trades / 100) * 100)
        elif ach_id == "1000_trades":
            return min(100, (trader.total_trades / 1000) * 100)
        elif ach_id == "sharp_trader":
            return min(100, (trader.score.sharpe_ratio / 2.0) * 100)
        elif ach_id == "top_10":
            if trader.rank <= 10:
                return 100
            elif trader.rank <= 50:
                return 50
            else:
                return 10
        elif ach_id == "100_followers":
            return min(100, (trader.followers / 100) * 100)
        elif ach_id == "consistent_trader":
            # 30 kun ketma-ket trading (simplified)
            return min(100, (trader.total_trades / 30) * 100)
        elif ach_id == "profitable_week":
            # Haftalik foyda > 0 (simplified)
            return 100 if trader.score.total_pnl > 0 else 0
        elif ach_id == "10_wins_streak":
            # 10 ta ketma-ket foydali trade
            win_rate = (trader.winning_trades / trader.total_trades * 100) if trader.total_trades > 0 else 0
            return min(100, win_rate * 10)
        
        return 0.0

    async def get_monthly_leaders(
        self,
        month: int = None,
        year: int = None,
        limit: int = 20
    ) -> List[TraderPerformance]:
        """Monthly leaders (simplified implementation)"""
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year
        
        # For now return top overall performers
        # In real implementation would filter by actual monthly trading
        return await self.get_leaderboard(RankCategory.MONTHLY, limit)

    async def get_risk_adjusted_returns(
        self,
        trader_id: str
    ) -> Optional[Dict[str, float]]:
        """Risk-adjusted returns for a trader"""
        trader = self.traders.get(trader_id)
        if not trader:
            return None
        
        return {
            'sharpe_ratio': trader.score.sharpe_ratio,
            'sortino_ratio': trader.score.sharpe_ratio * 0.9,  # Simplified
            'max_drawdown': trader.score.max_drawdown,
            'calmar_ratio': (trader.score.total_pnl / abs(trader.score.max_drawdown)) if trader.score.max_drawdown < 0 else 0,
            'risk_score': 100 - abs(trader.score.max_drawdown),  # Simplified risk score
        }

    async def get_top_performers(
        self,
        category: RankCategory = RankCategory.OVERALL,
        metric: str = "overall_score",
        limit: int = 50
    ) -> List[TraderPerformance]:
        """Get top performers by specific metric"""
        leaderboard = await self.get_leaderboard(category, limit * 2)
        
        if metric == "profit":
            leaderboard.sort(key=lambda x: x.score.total_pnl, reverse=True)
        elif metric == "win_rate":
            leaderboard.sort(key=lambda x: x.score.win_rate, reverse=True)
        elif metric == "trades":
            leaderboard.sort(key=lambda x: x.total_trades, reverse=True)
        elif metric == "volume":
            leaderboard.sort(key=lambda x: x.total_volume, reverse=True)
        elif metric == "followers":
            leaderboard.sort(key=lambda x: x.followers, reverse=True)
        elif metric == "consistency":
            leaderboard.sort(key=lambda x: x.score.consistency, reverse=True)
        # else use overall_score (default)
        
        return leaderboard[:limit]

    async def get_trader_stats(
        self,
        trader_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive trader statistics"""
        trader = await self.get_trader_rank(trader_id)
        if not trader:
            return None
        
        # Get category rankings
        category_rankings = {}
        for category in RankCategory:
            rank = await self.get_trader_rank(trader_id, category)
            if rank:
                category_rankings[category.value] = {
                    'rank': rank.rank,
                    'score': rank.score.calculate_score(),
                    'tier': rank.tier.value
                }
        
        # Achievement progress
        achievement_progress = await self._get_achievement_progress(trader_id)
        
        # Risk metrics
        risk_metrics = await self.get_risk_adjusted_returns(trader_id)
        
        return {
            'trader_info': trader.to_dict(),
            'category_rankings': category_rankings,
            'achievement_progress': achievement_progress,
            'risk_metrics': risk_metrics,
            'social_stats': {
                'followers': trader.followers,
                'verified': trader.verified,
                'badges': trader.badges,
            },
            'performance_trends': {
                'rank_change': trader.get_rank_change(),
                'recent_performance': trader.score.calculate_score(),
            }
        }

    async def add_social_follow(
        self,
        follower_id: str,
        followed_id: str
    ) -> bool:
        """Add social follow relationship"""
        if follower_id == followed_id:
            return False
        
        # Simplified social logic
        follower = self.traders.get(follower_id)
        followed = self.traders.get(followed_id)
        
        if follower and followed:
            followed.followers += 1
            follower.last_updated = datetime.now()
            return True
        
        return False

    async def update_trader_performance(
        self,
        trader_id: str,
        trade_result: Dict[str, Any]
    ) -> None:
        """Update trader performance from trade results"""
        if trader_id not in self.traders:
            return
        
        trader = self.traders[trader_id]
        
        # Update basic metrics
        trader.total_trades += 1
        
        if trade_result.get('profit', 0) > 0:
            trader.winning_trades += 1
        else:
            trader.losing_trades += 1
        
        # Update performance score
        trader.score.total_pnl += trade_result.get('profit', 0)
        
        win_rate = (trader.winning_trades / trader.total_trades) * 100
        trader.score.win_rate = win_rate
        
        # Update volume
        trader.total_volume += trade_result.get('volume', 0)
        
        # Re-rank trader
        await self.update_trader_rank(
            trader_id,
            trader.username,
            {
                'total_pnl': trader.score.total_pnl,
                'win_rate': win_rate,
                'sharpe_ratio': trader.score.sharpe_ratio,
                'profit_factor': trader.score.profit_factor,
                'max_drawdown': trader.score.max_drawdown,
                'consistency': trader.score.consistency,
                'risk_management': trader.score.risk_management,
                'total_trades': trader.total_trades,
                'winning_trades': trader.winning_trades,
                'losing_trades': trader.losing_trades,
                'total_volume': trader.total_volume,
                'followers': trader.followers,
                'verified': trader.verified,
            },
            trader.category
        )

    async def export_leaderboard_data(
        self,
        category: RankCategory = RankCategory.OVERALL,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export leaderboard data for analysis"""
        leaderboard = await self.get_leaderboard(category)
        statistics = await self.get_statistics(category)
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'category': category.value,
            'leaderboard': [trader.to_dict() for trader in leaderboard],
            'statistics': statistics,
            'achievements_count': len(self.achievements),
            'total_traders': len(self.traders)
        }
        
        if format.lower() == "json":
            return export_data
        else:
            # Other formats can be added here
            return export_data

    def get_comparative_analytics(
        self,
        trader_id: str
    ) -> Dict[str, Any]:
        """Get comparative analytics for a trader"""
        if trader_id not in self.traders:
            return {}
        
        trader = self.traders[trader_id]
        leaderboard = self.rankings.get(RankCategory.OVERALL, [])
        
        # Find trader position
        try:
            position = leaderboard.index(trader)
            percentile = ((len(leaderboard) - position) / len(leaderboard)) * 100
        except ValueError:
            position = None
            percentile = 0
        
        return {
            'trader_info': {
                'trader_id': trader_id,
                'username': trader.username,
                'rank': trader.rank,
                'tier': trader.tier.value,
                'score': trader.score.calculate_score(),
            },
            'position': position + 1 if position is not None else None,
            'percentile': percentile,
            'total_traders': len(leaderboard),
            'rankings_summary': {
                'category': trader.category.value,
                'rank_change': trader.get_rank_change(),
                'tier': trader.tier.value,
            },
            'performance_summary': trader.score.to_dict(),
            'social_summary': {
                'followers': trader.followers,
                'badges_count': len(trader.badges),
                'achievements_count': len(trader.achievements),
                'verified': trader.verified,
            }
        }

    # Demo usage
    async def demo(self):
        """Demo function to showcase the leaderboard system"""
        print("=== Leaderboard System Demo ===\n")
        
        # Add sample traders
        sample_traders = [
            ("trader_001", "Ali"),
            ("trader_002", "Bobur"), 
            ("trader_003", "Zara"),
            ("trader_004", "Otabek"),
            ("trader_005", "Madina"),
        ]
        
        for trader_id, username in sample_traders:
            # Simulate trading data
            import random
            performance_data = {
                'total_pnl': random.uniform(-1000, 5000),
                'win_rate': random.uniform(40, 90),
                'sharpe_ratio': random.uniform(0.5, 3.0),
                'profit_factor': random.uniform(0.8, 2.5),
                'max_drawdown': random.uniform(-10, -2),
                'consistency': random.uniform(60, 95),
                'risk_management': random.uniform(70, 100),
                'total_trades': random.randint(10, 500),
                'winning_trades': random.randint(5, 200),
                'losing_trades': random.randint(5, 200),
                'total_volume': random.uniform(10000, 100000),
                'followers': random.randint(0, 500),
                'verified': random.choice([True, False])
            }
            
            await self.update_trader_rank(trader_id, username, performance_data)
        
        # Get leaderboard
        print("🏆 Overall Leaderboard:")
        leaderboard = await self.get_leaderboard(limit=5)
        for i, trader in enumerate(leaderboard, 1):
            print(f"{i}. {trader.username} - Rank: {trader.rank_enum.value} - Score: {trader.score.calculate_score():.2f} - PnL: ${trader.score.total_pnl:.2f}")
        
        # Get rising stars
        print("\n⭐ Rising Stars:")
        rising = await self.get_rising_stars(limit=3)
        for trader in rising:
            print(f"📈 {trader.username} - Rank change: +{trader.get_rank_change()} - Tier: {trader.tier.value}")
        
        # Get achievements
        print("\n🎯 Achievements:")
        achievements = await self.get_achievements_list()
        for ach in achievements[:5]:
            print(f"{ach.icon} {ach.name} - {ach.points} points ({ach.rarity})")
        
        # Get trader stats
        print("\n📊 Trader Stats:")
        stats = await self.get_trader_stats("trader_002")
        if stats:
            print(f"Trader: {stats['trader_info']['username']}")
            print(f"Rank: {stats['trader_info']['rank']} ({stats['trader_info']['rank_enum']})")
            score_val = stats['trader_info']['score'] 
            if isinstance(score_val, dict) and 'overall_score' in score_val:
                print(f"Score: {score_val['overall_score']:.2f}")
            elif isinstance(score_val, (int, float)):
                print(f"Score: {score_val:.2f}")
            else:
                print(f"Score: {score_val}")
            print(f"Tier: {stats['trader_info']['tier']}")
            print(f"Trust: {stats['trader_info'].get('trust_tier', 'newbie')}")
            print(f"Achievements: {len(stats['trader_info'].get('achievements', []))}")
            print(f"Followers: {stats['trader_info']['followers']}")
        
        print("\n=== Demo Complete ===")

# Run demo if executed directly
if __name__ == "__main__":
    import asyncio
    
    async def main():
        lb = LeaderboardSystem()
        await lb.demo()
    
    asyncio.run(main())
