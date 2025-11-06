"""
Social Copy Trading Engine
==========================

Bu modul ijtimoiy copy trading tizimini amalga oshiradi, u yerda
taqqoslash uchun traderlar (liderlar) va ulardan copy qiluvchi foydalanuvchilar (followers) ishlaydi.
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from decimal import Decimal
import uuid
import logging


class LeaderProfile(Enum):
    """Lider trader profillari"""
    BEGINNER = "boshlang'ich"  # 0-6 oylik tajriba
    INTERMEDIATE = "o'rta"     # 6-24 oylik tajriba  
    ADVANCED = "advans"        # 2-5 yillik tajriba
    EXPERT = "expert"          # 5+ yillik tajriba
    LEGEND = "legenda"         # 10+ yillik + yuqori daromad
    SOCIAL_STAR = "ijtimoiy_yulduz"  # Katta followers soni


class CopyMode(Enum):
    """Copy qilish rejimlari"""
    AUTO = "avtomatik"         # Avtomatik copy qilish
    MANUAL = "qo'lda"          # Qo'lda tasdiqlash
    SIGNAL_ONLY = "signal"     # Faqat signallar
    PERCENTAGE = "foiz"        # Foiz asosida
    FIXED_AMOUNT = "miqdor"    # Qo'zg'aluvchi miqdor


@dataclass
class CopySettings:
    """Copy qilish sozlamalari"""
    copy_mode: CopyMode = CopyMode.AUTO
    max_drawdown_percent: float = 10.0  # Maksimal drawdown %
    min_leader_profit: float = 0.0      # Minimal leader daromadi
    auto_stop_loss: bool = True         # Avtomatik stop loss
    risk_management: bool = True        # Risk boshqaruvi
    copy_percentage: float = 100.0      # Copy qilish foizi
    max_position_size: Decimal = Decimal('1000')  # Maksimal pozitsiya hajmi
    min_balance: Decimal = Decimal('100')  # Minimal balans
    stop_copying_on_loss: bool = False   # Zarar bo'lganda to'xtatish


@dataclass  
class LeaderStats:
    """Lider trader statistikasi"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_profit: Decimal = Decimal('0')
    total_loss: Decimal = Decimal('0')
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    profit_factor: float = 0.0
    avg_trade_duration: float = 0.0  # daqiqalarda
    followers_count: int = 0
    total_followed_capital: Decimal = Decimal('0')
    monthly_returns: List[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Leader:
    """Lider trader ma'lumotlari"""
    user_id: str
    username: str
    profile: LeaderProfile
    balance: Decimal = Decimal('0')
    equity: Decimal = Decimal('0')
    stats: LeaderStats = field(default_factory=LeaderStats)
    is_active: bool = True
    verified: bool = False
    bio: str = ""
    avatar_url: str = ""
    social_stats: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class Follower:
    """Follower (copy qiluvchi) ma'lumotlari"""
    user_id: str
    username: str
    balance: Decimal = Decimal('0')
    equity: Decimal = Decimal('0')
    settings: CopySettings = field(default_factory=CopySettings)
    followed_leaders: Dict[str, CopySettings] = field(default_factory=dict)  # leader_id -> settings
    total_copy_invested: Decimal = Decimal('0')
    total_copy_profit: Decimal = Decimal('0')
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class CopyTrade:
    """Copy qilingan savdo"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    follower_id: str = ""
    leader_id: str = ""
    leader_trade_id: str = ""  # Asl trader savdo ID si
    symbol: str = ""
    action: str = ""  # BUY/SELL
    amount: Decimal = Decimal('0')
    price: Decimal = Decimal('0')
    entry_time: datetime = field(default_factory=datetime.now)
    exit_time: Optional[datetime] = None
    exit_price: Optional[Decimal] = None
    pnl: Decimal = Decimal('0')  # Profit/Loss
    commission: Decimal = Decimal('0')
    status: str = "open"  # open/closed/cancelled
    copy_percentage: float = 100.0
    notes: str = ""


class CopyTradingEngine:
    """Asosiy Copy Trading Engine"""
    
    def __init__(self):
        self.leaders: Dict[str, Leader] = {}
        self.followers: Dict[str, Follower] = {}
        self.copy_trades: Dict[str, CopyTrade] = {}
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        
    def add_leader(self, 
                  user_id: str, 
                  username: str, 
                  profile: LeaderProfile,
                  balance: Decimal,
                  bio: str = "",
                  avatar_url: str = "",
                  verified: bool = False) -> bool:
        """
        Yangi lider trader qo'shish
        
        Args:
            user_id: Foydalanuvchi ID si
            username: Foydalanuvchi nomi
            profile: Lider profili
            balance: Balans
            bio: Biografiya
            avatar_url: Avatar rasmi
            verified: Tasdiqlanganlik holati
            
        Returns:
            bool: Muvaffaqiyatli qo'shilganligi
        """
        try:
            if user_id in self.leaders:
                self.logger.warning(f"Lider {user_id} allaqachon mavjud")
                return False
                
            leader = Leader(
                user_id=user_id,
                username=username,
                profile=profile,
                balance=balance,
                bio=bio,
                avatar_url=avatar_url,
                verified=verified
            )
            
            self.leaders[user_id] = leader
            self.logger.info(f"Lider qo'shildi: {username} ({profile.value})")
            return True
            
        except Exception as e:
            self.logger.error(f"Lider qo'shishda xato: {e}")
            return False
    
    def get_top_leaders(self, 
                       limit: int = 10,
                       sort_by: str = "sharpe_ratio",
                       min_followers: int = 0,
                       profile_filter: Optional[LeaderProfile] = None) -> List[Tuple[str, Leader, Dict[str, Any]]]:
        """
        Top liderlarni olish
        
        Args:
            limit: Limit soni
            sort_by: Saralash mezoni (sharpe_ratio, win_rate, total_profit, followers_count)
            min_followers: Minimal follower soni
            profile_filter: Profil filtrasi
            
        Returns:
            List[Tuple[str, Leader, Dict]]: [(leader_id, leader, metrics)]
        """
        try:
            leaders_list = []
            
            for leader_id, leader in self.leaders.items():
                if not leader.is_active:
                    continue
                    
                if min_followers > 0 and leader.stats.followers_count < min_followers:
                    continue
                    
                if profile_filter and leader.profile != profile_filter:
                    continue
                
                # Metrikalarni hisoblash
                metrics = self._calculate_leader_metrics(leader)
                
                leaders_list.append((leader_id, leader, metrics))
            
            # Saralash
            if sort_by == "sharpe_ratio":
                leaders_list.sort(key=lambda x: x[2]['sharpe_ratio'], reverse=True)
            elif sort_by == "win_rate":
                leaders_list.sort(key=lambda x: x[2]['win_rate'], reverse=True)
            elif sort_by == "total_profit":
                leaders_list.sort(key=lambda x: x[2]['total_profit'], reverse=True)
            elif sort_by == "followers_count":
                leaders_list.sort(key=lambda x: x[2]['followers_count'], reverse=True)
            else:
                leaders_list.sort(key=lambda x: x[2]['sharpe_ratio'], reverse=True)
            
            return leaders_list[:limit]
            
        except Exception as e:
            self.logger.error(f"Top liderlarni olishda xato: {e}")
            return []
    
    def start_copying(self, 
                     follower_id: str,
                     leader_id: str,
                     settings: CopySettings) -> bool:
        """
        Liderdan copy qilishni boshlash
        
        Args:
            follower_id: Follower ID si
            leader_id: Lider ID si  
            settings: Copy sozlamalari
            
        Returns:
            bool: Muvaffaqiyatli boshlanganligi
        """
        try:
            if follower_id not in self.followers:
                self.logger.error(f"Follower {follower_id} topilmadi")
                return False
                
            if leader_id not in self.leaders:
                self.logger.error(f"Lider {leader_id} topilmadi")
                return False
            
            follower = self.followers[follower_id]
            leader = self.leaders[leader_id]
            
            # Balansni tekshirish
            if follower.balance < settings.min_balance:
                self.logger.error(f"Follower balansi yetarli emas")
                return False
            
            # Leader aktivligini tekshirish
            if not leader.is_active:
                self.logger.error("Lider faol emas")
                return False
            
            # Copy qilishni qo'shish
            follower.followed_leaders[leader_id] = settings
            leader.stats.followers_count += 1
            leader.stats.total_followed_capital += follower.balance * (settings.copy_percentage / 100)
            
            # Activity time update
            follower.last_activity = datetime.now()
            leader.last_activity = datetime.now()
            
            self.logger.info(f"Follower {follower_id} lider {leader_id} dan copy qilishni boshladi")
            return True
            
        except Exception as e:
            self.logger.error(f"Copy qilishni boshlashda xato: {e}")
            return False
    
    def stop_copying(self, follower_id: str, leader_id: str = None) -> bool:
        """
        Copy qilishni to'xtatish
        
        Args:
            follower_id: Follower ID si
            leader_id: Lider ID si (None bo'lsa, barcha liderlardan to'xtatish)
            
        Returns:
            bool: Muvaffaqiyatli to'xtatilganligi
        """
        try:
            if follower_id not in self.followers:
                return False
            
            follower = self.followers[follower_id]
            
            if leader_id:
                # Ma'lum liderdan to'xtatish
                if leader_id not in follower.followed_leaders:
                    self.logger.error(f"Copy qilish mavjud emas: {leader_id}")
                    return False
                
                del follower.followed_leaders[leader_id]
                
                # Leader stats update
                if leader_id in self.leaders:
                    leader = self.leaders[leader_id]
                    leader.stats.followers_count = max(0, leader.stats.followers_count - 1)
                
                self.logger.info(f"Follower {follower_id} lider {leader_id} dan copy qilishni to'xtatdi")
            
            else:
                # Barcha liderlardan to'xtatish
                for l_id in list(follower.followed_leaders.keys()):
                    if l_id in self.leaders:
                        leader = self.leaders[l_id]
                        leader.stats.followers_count = max(0, leader.stats.followers_count - 1)
                
                follower.followed_leaders.clear()
                self.logger.info(f"Follower {follower_id} barcha liderlardan copy qilishni to'xtatdi")
            
            follower.last_activity = datetime.now()
            return True
            
        except Exception as e:
            self.logger.error(f"Copy qilishni to'xtatishda xato: {e}")
            return False
    
    def get_follower_statistics(self, follower_id: str) -> Dict[str, Any]:
        """
        Follower statistikasini olish
        
        Args:
            follower_id: Follower ID si
            
        Returns:
            Dict: Follower statistikasi
        """
        try:
            if follower_id not in self.followers:
                return {}
            
            follower = self.followers[follower_id]
            
            # Copy qilingan savdolarni olish
            follower_trades = [
                trade for trade in self.copy_trades.values()
                if trade.follower_id == follower_id
            ]
            
            # Statistikani hisoblash
            total_trades = len(follower_trades)
            closed_trades = [t for t in follower_trades if t.status == "closed"]
            winning_trades = [t for t in closed_trades if t.pnl > 0]
            losing_trades = [t for t in closed_trades if t.pnl < 0]
            
            total_pnl = sum(t.pnl for t in closed_trades)
            total_commission = sum(t.commission for t in follower_trades)
            
            win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
            
            # Followed leaders details
            followed_leaders_detail = []
            for leader_id, settings in follower.followed_leaders.items():
                if leader_id in self.leaders:
                    leader = self.leaders[leader_id]
                    # Lider uchun copy qilingan savdolarni olish
                    leader_copy_trades = [t for t in follower_trades if t.leader_id == leader_id]
                    leader_pnl = sum(t.pnl for t in leader_copy_trades)
                    
                    followed_leaders_detail.append({
                        'leader_id': leader_id,
                        'leader_name': leader.username,
                        'leader_profile': leader.profile.value,
                        'copy_settings': {
                            'mode': settings.copy_mode.value,
                            'percentage': settings.copy_percentage,
                            'max_drawdown': settings.max_drawdown_percent,
                            'auto_stop_loss': settings.auto_stop_loss
                        },
                        'total_trades': len(leader_copy_trades),
                        'pnl': float(leader_pnl),
                        'start_date': min(t.entry_time for t in leader_copy_trades) if leader_copy_trades else None
                    })
            
            stats = {
                'follower_id': follower_id,
                'username': follower.username,
                'total_balance': float(follower.balance),
                'total_equity': float(follower.equity),
                'total_invested': float(follower.total_copy_invested),
                'total_profit': float(follower.total_copy_profit),
                'followed_leaders_count': len(follower.followed_leaders),
                'followed_leaders': followed_leaders_detail,
                'total_trades': total_trades,
                'closed_trades': len(closed_trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'total_pnl': float(total_pnl),
                'total_commission': float(total_commission),
                'net_profit': float(total_pnl - total_commission),
                'is_active': follower.is_active,
                'last_activity': follower.last_activity.isoformat(),
                'created_at': follower.created_at.isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Follower statistikasini olishda xato: {e}")
            return {}
    
    def get_copy_history(self, 
                        user_id: str = None,
                        leader_id: str = None,
                        follower_id: str = None,
                        days: int = 30,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        Copy savdo tarixini olish
        
        Args:
            user_id: Foydalanuvchi ID si (leader yoki follower)
            leader_id: Lider ID si
            follower_id: Follower ID si
            days: Kun soni (default 30)
            limit: Limit soni
            
        Returns:
            List[Dict]: Copy savdo tarixi
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filtrlash
            filtered_trades = []
            for trade in self.copy_trades.values():
                if trade.entry_time < cutoff_date:
                    continue
                
                # User filter
                if user_id:
                    if trade.leader_id != user_id and trade.follower_id != user_id:
                        continue
                
                # Leader filter
                if leader_id and trade.leader_id != leader_id:
                    continue
                    
                # Follower filter  
                if follower_id and trade.follower_id != follower_id:
                    continue
                
                filtered_trades.append(trade)
            
            # Vaqt bo'yicha saralash (oxirgi birinchi)
            filtered_trades.sort(key=lambda x: x.entry_time, reverse=True)
            
            # Limit qo'llash
            result_trades = filtered_trades[:limit]
            
            # Natijalarni formatlash
            history = []
            for trade in result_trades:
                leader_info = self.leaders.get(trade.leader_id)
                follower_info = self.followers.get(trade.follower_id)
                
                trade_info = {
                    'id': trade.id,
                    'follower_id': trade.follower_id,
                    'follower_name': follower_info.username if follower_info else 'Noma\'lum',
                    'leader_id': trade.leader_id,
                    'leader_name': leader_info.username if leader_info else 'Noma\'lum',
                    'leader_trade_id': trade.leader_trade_id,
                    'symbol': trade.symbol,
                    'action': trade.action,
                    'amount': float(trade.amount),
                    'entry_price': float(trade.price),
                    'entry_time': trade.entry_time.isoformat(),
                    'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                    'exit_price': float(trade.exit_price) if trade.exit_price else None,
                    'pnl': float(trade.pnl),
                    'commission': float(trade.commission),
                    'status': trade.status,
                    'copy_percentage': trade.copy_percentage,
                    'profit_loss_percent': float((trade.pnl / trade.amount) * 100) if trade.amount > 0 else 0,
                    'duration_minutes': (
                        (trade.exit_time - trade.entry_time).total_seconds() / 60
                        if trade.exit_time else None
                    ),
                    'notes': trade.notes
                }
                
                history.append(trade_info)
            
            return history
            
        except Exception as e:
            self.logger.error(f"Copy tarixini olishda xato: {e}")
            return []
    
    def execute_copy_trade(self,
                          leader_trade: Dict[str, Any],
                          leader_id: str) -> List[str]:
        """
        Lider savdosini copy qilish
        
        Args:
            leader_trade: Lider savdo ma'lumotlari
            leader_id: Lider ID si
            
        Returns:
            List[str]: Yaratilgan copy trade IDlari
        """
        try:
            if leader_id not in self.leaders:
                return []
            
            leader = self.leaders[leader_id]
            created_trade_ids = []
            
            # Barcha followerlarni tekshirish
            for follower_id, settings in self.followers.items():
                if leader_id not in follower.followed_leaders:
                    continue
                
                follower = self.followers[follower_id]
                copy_settings = follower.followed_leaders[leader_id]
                
                # Sozlamalarni tekshirish
                if not self._validate_copy_conditions(follower, leader, copy_settings, leader_trade):
                    continue
                
                # Copy trade yaratish
                copy_trade = self._create_copy_trade(follower_id, leader_id, leader_trade, copy_settings)
                
                if copy_trade:
                    self.copy_trades[copy_trade.id] = copy_trade
                    created_trade_ids.append(copy_trade.id)
                    
                    self.logger.info(
                        f"Copy trade yaratildi: {copy_trade.id} "
                        f"(leader: {leader_id} -> follower: {follower_id})"
                    )
            
            return created_trade_ids
            
        except Exception as e:
            self.logger.error(f"Copy trade bajarishda xato: {e}")
            return []
    
    def update_leader_performance(self, leader_id: str, performance_data: Dict[str, Any]) -> bool:
        """
        Lider performance ma'lumotlarini yangilash
        
        Args:
            leader_id: Lider ID si
            performance_data: Performance ma'lumotlari
            
        Returns:
            bool: Yangilash muvaffaqiyatligi
        """
        try:
            if leader_id not in self.leaders:
                return False
            
            leader = self.leaders[leader_id]
            
            # Stats ma'lumotlarini yangilash
            if 'total_trades' in performance_data:
                leader.stats.total_trades = performance_data['total_trades']
            if 'winning_trades' in performance_data:
                leader.stats.winning_trades = performance_data['winning_trades']
            if 'total_profit' in performance_data:
                leader.stats.total_profit = Decimal(str(performance_data['total_profit']))
            if 'win_rate' in performance_data:
                leader.stats.win_rate = performance_data['win_rate']
            
            leader.last_activity = datetime.now()
            return True
            
        except Exception as e:
            self.logger.error(f"Lider performance yangilashda xato: {e}")
            return False
    
    def get_leader_statistics(self, leader_id: str) -> Dict[str, Any]:
        """
        Lider statistikasini olish
        
        Args:
            leader_id: Lider ID si
            
        Returns:
            Dict: Lider statistikasi
        """
        try:
            if leader_id not in self.leaders:
                return {}
            
            leader = self.leaders[leader_id]
            
            # Lider savdolarini olish
            leader_trades = [
                trade for trade in self.copy_trades.values()
                if trade.leader_id == leader_id
            ]
            
            # Copy qilingan savdolarni olish
            copied_trades = leader_trades  # Copy trade larda leader_id mavjud
            
            # Followers statistikasi
            followers_list = [
                follower for follower in self.followers.values()
                if leader_id in follower.followed_leaders
            ]
            
            total_followed_capital = sum(
                follower.balance * (settings.copy_percentage / 100)
                for follower in followers_list
                for settings in [follower.followed_leaders[leader_id]]
            )
            
            stats = {
                'leader_id': leader_id,
                'username': leader.username,
                'profile': leader.profile.value,
                'balance': float(leader.balance),
                'equity': float(leader.equity),
                'verified': leader.verified,
                'is_active': leader.is_active,
                'stats': {
                    'total_trades': leader.stats.total_trades,
                    'winning_trades': leader.stats.winning_trades,
                    'losing_trades': leader.stats.losing_trades,
                    'win_rate': leader.stats.win_rate,
                    'total_profit': float(leader.stats.total_profit),
                    'max_drawdown': leader.stats.max_drawdown,
                    'sharpe_ratio': leader.stats.sharpe_ratio,
                    'profit_factor': leader.stats.profit_factor,
                    'avg_trade_duration': leader.stats.avg_trade_duration
                },
                'followers': {
                    'total_count': len(followers_list),
                    'total_followed_capital': float(total_followed_capital),
                    'active_followers': len([f for f in followers_list if f.is_active])
                },
                'copy_performance': {
                    'total_copy_trades': len(copied_trades),
                    'successful_copies': len([t for t in copied_trades if t.pnl > 0]),
                    'copy_success_rate': len([t for t in copied_trades if t.pnl > 0]) / len(copied_trades) * 100 if copied_trades else 0,
                    'total_copy_pnl': float(sum(t.pnl for t in copied_trades))
                },
                'created_at': leader.created_at.isoformat(),
                'last_activity': leader.last_activity.isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Lider statistikasini olishda xato: {e}")
            return {}
    
    # Helper methods
    
    def _calculate_leader_metrics(self, leader: Leader) -> Dict[str, Any]:
        """Lider uchun metrikalarni hisoblash"""
        try:
            # Leader trades
            leader_trades = [
                trade for trade in self.copy_trades.values()
                if trade.leader_id == leader.user_id
            ]
            
            closed_trades = [t for t in leader_trades if t.status == "closed"]
            
            if not closed_trades:
                return {
                    'win_rate': 0,
                    'total_profit': 0,
                    'sharpe_ratio': 0,
                    'followers_count': 0,
                    'total_return': 0
                }
            
            # Win rate
            winning_trades = [t for t in closed_trades if t.pnl > 0]
            win_rate = len(winning_trades) / len(closed_trades) * 100
            
            # Total profit
            total_profit = sum(t.pnl for t in closed_trades)
            
            # Sharpe ratio (simplified)
            returns = [float(t.pnl) for t in closed_trades]
            if len(returns) > 1:
                avg_return = sum(returns) / len(returns)
                variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
                std_return = variance ** 0.5
                sharpe_ratio = avg_return / std_return if std_return > 0 else 0
            else:
                sharpe_ratio = 0
            
            # Total return
            total_return = float(total_profit / leader.balance) * 100 if leader.balance > 0 else 0
            
            return {
                'win_rate': win_rate,
                'total_profit': float(total_profit),
                'sharpe_ratio': sharpe_ratio,
                'followers_count': leader.stats.followers_count,
                'total_return': total_return
            }
            
        except Exception as e:
            self.logger.error(f"Metrikalarni hisoblashda xato: {e}")
            return {}
    
    def _validate_copy_conditions(self, 
                                 follower: Follower, 
                                 leader: Leader, 
                                 settings: CopySettings, 
                                 leader_trade: Dict[str, Any]) -> bool:
        """Copy qilish shartlarini tekshirish"""
        try:
            # Leader aktivligini tekshirish
            if not leader.is_active:
                return False
            
            # Follower balansini tekshirish
            trade_amount = Decimal(str(leader_trade.get('amount', 0)))
            copy_amount = trade_amount * (settings.copy_percentage / 100)
            
            if copy_amount > follower.balance:
                return False
            
            # Max position size check
            if copy_amount > settings.max_position_size:
                return False
            
            # Risk management checks
            if settings.risk_management:
                # Leader drawdown check
                if leader.stats.max_drawdown > settings.max_drawdown_percent:
                    return False
                
                # Min profit check
                if hasattr(leader.stats, 'total_profit') and leader.stats.total_profit < settings.min_leader_profit:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Copy shartlarini tekshirishda xato: {e}")
            return False
    
    def _create_copy_trade(self, 
                          follower_id: str, 
                          leader_id: str, 
                          leader_trade: Dict[str, Any], 
                          settings: CopySettings) -> Optional[CopyTrade]:
        """Copy trade yaratish"""
        try:
            # Leader trade ma'lumotlaridan copy trade yaratish
            trade_amount = Decimal(str(leader_trade.get('amount', 0)))
            trade_price = Decimal(str(leader_trade.get('price', 0)))
            
            copy_amount = trade_amount * (settings.copy_percentage / 100)
            copy_price = trade_price
            
            # Commission hisoblash (masalan 0.1%)
            commission = copy_amount * Decimal('0.001')
            
            copy_trade = CopyTrade(
                follower_id=follower_id,
                leader_id=leader_id,
                leader_trade_id=leader_trade.get('id', ''),
                symbol=leader_trade.get('symbol', ''),
                action=leader_trade.get('action', ''),
                amount=copy_amount,
                price=copy_price,
                commission=commission,
                copy_percentage=settings.copy_percentage,
                entry_time=datetime.now()
            )
            
            return copy_trade
            
        except Exception as e:
            self.logger.error(f"Copy trade yaratishda xato: {e}")
            return None
    
    def add_follower(self, 
                    user_id: str, 
                    username: str, 
                    balance: Decimal) -> bool:
        """
        Yangi follower qo'shish
        
        Args:
            user_id: Foydalanuvchi ID si
            username: Foydalanuvchi nomi  
            balance: Balans
            
        Returns:
            bool: Muvaffaqiyatli qo'shilganligi
        """
        try:
            if user_id in self.followers:
                self.logger.warning(f"Follower {user_id} allaqachon mavjud")
                return False
            
            follower = Follower(
                user_id=user_id,
                username=username,
                balance=balance
            )
            
            self.followers[user_id] = follower
            self.logger.info(f"Follower qo'shildi: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Follower qo'shishda xato: {e}")
            return False
    
    def update_follower_balance(self, follower_id: str, new_balance: Decimal) -> bool:
        """
        Follower balansini yangilash
        
        Args:
            follower_id: Follower ID si
            new_balance: Yangi balans
            
        Returns:
            bool: Yangilash muvaffaqiyatligi
        """
        try:
            if follower_id not in self.followers:
                return False
            
            self.followers[follower_id].balance = new_balance
            self.followers[follower_id].last_activity = datetime.now()
            return True
            
        except Exception as e:
            self.logger.error(f"Follower balansini yangilashda xato: {e}")
            return False
    
    def close_copy_trade(self, trade_id: str, exit_price: Decimal) -> bool:
        """
        Copy trade ni yopish
        
        Args:
            trade_id: Trade ID si
            exit_price: Chiqish narxi
            
        Returns:
            bool: Yopish muvaffaqiyatligi
        """
        try:
            if trade_id not in self.copy_trades:
                return False
            
            trade = self.copy_trades[trade_id]
            
            if trade.status != "open":
                return False
            
            # PnL hisoblash
            if trade.action == "BUY":
                trade.pnl = (exit_price - trade.price) * trade.amount
            else:  # SELL
                trade.pnl = (trade.price - exit_price) * trade.amount
            
            trade.exit_price = exit_price
            trade.exit_time = datetime.now()
            trade.status = "closed"
            
            # Follower ma'lumotlarini yangilash
            if trade.follower_id in self.followers:
                follower = self.followers[trade.follower_id]
                follower.equity += trade.pnl - trade.commission
                follower.total_copy_profit += trade.pnl
            
            self.logger.info(f"Copy trade yopildi: {trade_id}, PnL: {trade.pnl}")
            return True
            
        except Exception as e:
            self.logger.error(f"Copy trade ni yopishda xato: {e}")
            return False
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """
        Platform umumiy statistikasi
        
        Returns:
            Dict: Platform statistikasi
        """
        try:
            active_leaders = len([l for l in self.leaders.values() if l.is_active])
            active_followers = len([f for f in self.followers.values() if f.is_active])
            
            total_copy_trades = len(self.copy_trades)
            closed_copy_trades = len([t for t in self.copy_trades.values() if t.status == "closed"])
            winning_copy_trades = len([t for t in self.copy_trades.values() if t.status == "closed" and t.pnl > 0])
            
            total_platform_volume = sum(t.amount for t in self.copy_trades.values())
            total_platform_pnl = sum(t.pnl for t in self.copy_trades.values())
            
            avg_win_rate = (winning_copy_trades / closed_copy_trades * 100) if closed_copy_trades > 0 else 0
            
            # Top performing leaders
            top_leaders = self.get_top_leaders(limit=5, sort_by="total_profit")
            
            stats = {
                'leaders': {
                    'total': len(self.leaders),
                    'active': active_leaders,
                    'verified': len([l for l in self.leaders.values() if l.verified])
                },
                'followers': {
                    'total': len(self.followers),
                    'active': active_followers,
                    'copying': len([f for f in self.followers.values() if len(f.followed_leaders) > 0])
                },
                'trades': {
                    'total': total_copy_trades,
                    'closed': closed_copy_trades,
                    'winning': winning_copy_trades,
                    'win_rate': avg_win_rate
                },
                'volume': {
                    'total_copy_volume': float(total_platform_volume),
                    'total_pnl': float(total_platform_pnl)
                },
                'top_leaders': [
                    {
                        'leader_id': leader_id,
                        'username': leader.username,
                        'profile': leader.profile.value,
                        'followers': metrics['followers_count'],
                        'total_profit': metrics['total_profit']
                    }
                    for leader_id, leader, metrics in top_leaders
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Platform statistikasini olishda xato: {e}")
            return {}


# Utility functions

def create_demo_engine() -> CopyTradingEngine:
    """Demo maqsadida engine yaratish va test ma'lumotlarni qo'shish"""
    engine = CopyTradingEngine()
    
    # Demo liderlar qo'shish
    demo_leaders = [
        {
            'user_id': 'leader_001',
            'username': ' Trader_Alex',
            'profile': LeaderProfile.EXPERT,
            'balance': Decimal('10000'),
            'bio': '5+ yillik tajribaga ega professional trader',
            'verified': True
        },
        {
            'user_id': 'leader_002',
            'username': 'CryptoQueen_Maria',
            'profile': LeaderProfile.SOCIAL_STAR,
            'balance': Decimal('25000'),
            'bio': 'Kripto trading bo\'yicha ijtimoiy media eksperti',
            'verified': True
        },
        {
            'user_id': 'leader_003',
            'username': 'ForexKing_John',
            'profile': LeaderProfile.ADVANCED,
            'balance': Decimal('15000'),
            'bio': 'Forex bo\'yicha tajribali trader',
            'verified': False
        }
    ]
    
    for leader_data in demo_leaders:
        engine.add_leader(**leader_data)
    
    # Demo followerlar qo'shish
    demo_followers = [
        {
            'user_id': 'follower_001',
            'username': 'Newbie_Sarah',
            'balance': Decimal('1000')
        },
        {
            'user_id': 'follower_002',
            'username': 'Investor_Bob',
            'balance': Decimal('5000')
        }
    ]
    
    for follower_data in demo_followers:
        engine.add_follower(**follower_data)
    
    # Demo copy qilish qo'shish
    engine.start_copying('follower_001', 'leader_001', CopySettings(copy_percentage=50.0))
    engine.start_copying('follower_002', 'leader_002', CopySettings(copy_percentage=75.0))
    
    return engine


if __name__ == "__main__":
    # Demo ishga tushirish
    logging.basicConfig(level=logging.INFO)
    
    engine = create_demo_engine()
    
    # Top liderlarni ko'rsatish
    top_leaders = engine.get_top_leaders(limit=3)
    print("\n=== TOP LIDERLAR ===")
    for i, (leader_id, leader, metrics) in enumerate(top_leaders, 1):
        print(f"{i}. {leader.username} ({leader.profile.value})")
        print(f"   Followers: {metrics['followers_count']}")
        print(f"   Win Rate: {metrics['win_rate']:.1f}%")
        print(f"   Total Profit: ${metrics['total_profit']:.2f}")
        print()
    
    # Platform statistikasi
    platform_stats = engine.get_platform_statistics()
    print("=== PLATFORM STATISTIKASI ===")
    print(f"Liderlar: {platform_stats['leaders']['active']}/{platform_stats['leaders']['total']}")
    print(f"Followerlar: {platform_stats['followers']['active']}/{platform_stats['followers']['total']}")
    print(f"Win Rate: {platform_stats['trades']['win_rate']:.1f}%")