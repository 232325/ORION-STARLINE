"""
Referral System
Multi-level referral program management va tracking tizimi
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3
import logging
import hashlib

logger = logging.getLogger(__name__)

class ReferralTier(Enum):
    BRONZE = "bronze"      # 0-10 referrals
    SILVER = "silver"      # 11-50 referrals
    GOLD = "gold"          # 51-100 referrals
    PLATINUM = "platinum"  # 101+ referrals

class RewardType(Enum):
    CASH = "cash"
    CREDITS = "credits"
    COMMISSION = "commission"
    DISCOUNT = "discount"
    PRODUCT = "product"

class ReferralStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

@dataclass
class ReferralCode:
    code: str
    referrer_id: str
    tier: ReferralTier
    commission_rate: float
    max_referrals: Optional[int]
    expiry_date: datetime
    is_active: bool
    total_referrals: int = 0
    total_earnings: float = 0.0

@dataclass
class Referral:
    id: str
    referrer_code: str
    referee_id: str
    status: ReferralStatus
    reward_type: RewardType
    reward_amount: float
    commission_rate: float
    created_at: datetime
    completed_at: Optional[datetime]
    is_verified: bool

@dataclass
class User:
    id: str
    email: str
    referral_code: str
    referred_by: Optional[str]
    total_referrals: int = 0
    total_earnings: float = 0.0
    tier: ReferralTier = ReferralTier.BRONZE
    join_date: datetime = None

class ReferralSystem:
    """
    Comprehensive Multi-Level Referral System
    """
    
    def __init__(self, db_path: str = "marketing_referral.db"):
        self.db_path = db_path
        self.tier_configs = self._load_tier_configs()
        self.reward_configs = self._load_reward_configs()
        self._init_database()
    
    def _init_database(self):
        """Referral ma'lumotlar bazasini ishga tushirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                referral_code TEXT UNIQUE NOT NULL,
                referred_by TEXT,
                total_referrals INTEGER DEFAULT 0,
                total_earnings REAL DEFAULT 0.0,
                tier TEXT DEFAULT 'bronze',
                join_date TEXT,
                FOREIGN KEY (referred_by) REFERENCES users(referral_code)
            )
        """)
        
        # Referrals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id TEXT PRIMARY KEY,
                referrer_code TEXT NOT NULL,
                referee_id TEXT NOT NULL,
                status TEXT NOT NULL,
                reward_type TEXT,
                reward_amount REAL,
                commission_rate REAL,
                created_at TEXT,
                completed_at TEXT,
                is_verified BOOLEAN DEFAULT 0,
                FOREIGN KEY (referee_id) REFERENCES users(id)
            )
        """)
        
        # Reward transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reward_transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                referral_id TEXT,
                transaction_type TEXT,
                amount REAL,
                description TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Tier progression history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tier_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                from_tier TEXT,
                to_tier TEXT,
                trigger_referrals INTEGER,
                created_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_tier_configs(self) -> Dict:
        """Tier konfiguratsiyalari"""
        return {
            ReferralTier.BRONZE: {
                "min_referrals": 0,
                "max_referrals": 10,
                "commission_rate": 0.05,  # 5%
                "benefits": ["Basic commission", "Email support"],
                "color": "#CD7F32"
            },
            ReferralTier.SILVER: {
                "min_referrals": 11,
                "max_referrals": 50,
                "commission_rate": 0.08,  # 8%
                "benefits": ["Enhanced commission", "Priority support", "Monthly bonus"],
                "color": "#C0C0C0"
            },
            ReferralTier.GOLD: {
                "min_referrals": 51,
                "max_referrals": 100,
                "commission_rate": 0.12,  # 12%
                "benefits": ["Premium commission", "Dedicated manager", "Quarterly bonuses"],
                "color": "#FFD700"
            },
            ReferralTier.PLATINUM: {
                "min_referrals": 101,
                "max_referrals": None,  # Unlimited
                "commission_rate": 0.15,  # 15%
                "benefits": ["Maximum commission", "VIP manager", "Exclusive events", "Personal branding"],
                "color": "#E5E4E2"
            }
        }
    
    def _load_reward_configs(self) -> Dict:
        """Reward konfiguratsiyalari"""
        return {
            "signup_bonus": {
                "amount": 10.0,
                "type": RewardType.CREDITS,
                "description": "Referral signup bonus"
            },
            "first_purchase": {
                "amount": 25.0,
                "type": RewardType.COMMISSION,
                "percentage": 0.10,
                "description": "Commission for first purchase"
            },
            "monthly_bonus": {
                "amount": 50.0,
                "type": RewardType.CASH,
                "description": "Monthly performance bonus"
            },
            "milestone_reward": {
                "amount": 100.0,
                "type": RewardType.CASH,
                "description": "Milestone achievement reward"
            }
        }
    
    async def generate_referral_code(self, user_id: str, tier: ReferralTier = ReferralTier.BRONZE) -> Dict:
        """Referral code yaratish"""
        try:
            # Generate unique referral code
            timestamp = str(int(datetime.now().timestamp()))
            base_code = hashlib.md5(f"{user_id}_{timestamp}".encode()).hexdigest()[:8].upper()
            referral_code = f"OS{tier.value[:2].upper()}{base_code}"
            
            # Get tier configuration
            tier_config = self.tier_configs[tier]
            
            # Create referral code record
            referral_record = ReferralCode(
                code=referral_code,
                referrer_id=user_id,
                tier=tier,
                commission_rate=tier_config["commission_rate"],
                max_referrals=tier_config["max_referrals"],
                expiry_date=datetime.now() + timedelta(days=365),  # 1 year expiry
                is_active=True
            )
            
            # Save to database
            await self._save_referral_code(referral_record)
            
            return {
                "status": "generated",
                "referral_code": referral_code,
                "tier": tier.value,
                "commission_rate": tier_config["commission_rate"],
                "benefits": tier_config["benefits"],
                "max_referrals": tier_config["max_referrals"],
                "expiry_date": referral_record.expiry_date.isoformat(),
                "referral_link": f"https://orion-starline.com/signup?ref={referral_code}"
            }
            
        except Exception as e:
            logger.error(f"Referral code generation error: {e}")
            return {"error": str(e)}
    
    async def create_user(
        self,
        email: str,
        referred_by: Optional[str] = None
    ) -> Dict:
        """Yangi user yaratish"""
        try:
            user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate unique user referral code
            referral_code = f"USER{user_id[-4:].upper()}"
            
            # Create user record
            user = User(
                id=user_id,
                email=email,
                referral_code=referral_code,
                referred_by=referred_by,
                join_date=datetime.now()
            )
            
            # Save user to database
            await self._save_user(user)
            
            # Generate referral code for the user
            referral_result = await self.generate_referral_code(user_id)
            
            # Process referral if user was referred
            if referred_by:
                referral_processing = await self.process_referral(referred_by, user_id)
            else:
                referral_processing = {}
            
            logger.info(f"User created: {user_id}")
            
            return {
                "status": "created",
                "user_id": user_id,
                "email": email,
                "referral_code": referral_code,
                "referred_by": referred_by,
                "tier": user.tier.value,
                "referral_code_data": referral_result,
                "referral_processing": referral_processing,
                "welcome_message": "Orion Starline ga xush kelibsiz! Referral code orqali do'stlaringizni taklif qiling va bonus oling."
            }
            
        except Exception as e:
            logger.error(f"User creation error: {e}")
            return {"error": str(e)}
    
    async def process_referral(
        self,
        referral_code: str,
        referee_id: str
    ) -> Dict:
        """Referral process qilish"""
        try:
            # Find referrer
            referrer = await self._get_user_by_referral_code(referral_code)
            if not referrer:
                return {"error": "Invalid referral code"}
            
            # Check if referral already exists
            existing_referral = await self._check_existing_referral(referral_code, referee_id)
            if existing_referral:
                return {"error": "Referral already exists"}
            
            # Create referral record
            referral_id = f"ref_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            referrer_tier = self._get_user_tier(referrer["total_referrals"])
            commission_rate = self.tier_configs[referrer_tier]["commission_rate"]
            
            referral = Referral(
                id=referral_id,
                referrer_code=referral_code,
                referee_id=referee_id,
                status=ReferralStatus.PENDING,
                reward_type=RewardType.COMMISSION,
                reward_amount=0.0,  # Will be calculated based on referee activity
                commission_rate=commission_rate,
                created_at=datetime.now(),
                is_verified=True
            )
            
            await self._save_referral(referral)
            
            # Update referrer statistics
            await self._update_referrer_stats(referrer["id"])
            
            # Send notification
            notification_result = await self._send_referral_notification(referrer, referee_id)
            
            return {
                "status": "processed",
                "referral_id": referral_id,
                "referrer": referrer["email"],
                "commission_rate": commission_rate,
                "notification_sent": notification_result,
                "next_steps": [
                    "Referee needs to complete signup",
                    "First purchase tracking",
                    "Commission calculation"
                ]
            }
            
        except Exception as e:
            logger.error(f"Referral processing error: {e}")
            return {"error": str(e)}
    
    async def calculate_commission(
        self,
        referral_code: str,
        purchase_amount: float,
        purchase_type: str = "subscription"
    ) -> Dict:
        """Commission hisoblash"""
        try:
            # Get referrer details
            referrer = await self._get_user_by_referral_code(referral_code)
            if not referrer:
                return {"error": "Invalid referral code"}
            
            # Get tier and commission rate
            current_tier = self._get_user_tier(referrer["total_referrals"])
            tier_config = self.tier_configs[current_tier]
            commission_rate = tier_config["commission_rate"]
            
            # Calculate commission
            base_commission = purchase_amount * commission_rate
            
            # Apply tier bonuses
            tier_bonus = self._calculate_tier_bonus(current_tier, purchase_amount)
            total_commission = base_commission + tier_bonus
            
            # Apply volume discounts for high-tier users
            if current_tier in [ReferralTier.GOLD, ReferralTier.PLATINUM]:
                volume_discount = self._calculate_volume_discount(referrer["total_referrals"], purchase_amount)
                total_commission *= (1 + volume_discount)
            
            # Create transaction record
            transaction_id = f"trans_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            await self._save_commission_transaction(
                transaction_id, referrer["id"], total_commission,
                f"Commission from {purchase_type} purchase", purchase_amount
            )
            
            # Update referrer earnings
            await self._update_referrer_earnings(referrer["id"], total_commission)
            
            # Check for tier progression
            tier_progression = await self._check_tier_progression(referrer["id"])
            
            return {
                "status": "calculated",
                "transaction_id": transaction_id,
                "purchase_amount": purchase_amount,
                "commission_rate": commission_rate,
                "base_commission": base_commission,
                "tier_bonus": tier_bonus,
                "volume_discount": volume_discount if 'volume_discount' in locals() else 0,
                "total_commission": round(total_commission, 2),
                "referrer_tier": current_tier.value,
                "tier_progression": tier_progression
            }
            
        except Exception as e:
            logger.error(f"Commission calculation error: {e}")
            return {"error": str(e)}
    
    async def get_user_dashboard(self, user_id: str) -> Dict:
        """User referral dashboard"""
        try:
            # Get user details
            user = await self._get_user_by_id(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Get user statistics
            stats = await self._get_user_statistics(user_id)
            
            # Get recent referrals
            recent_referrals = await self._get_recent_referrals(user_id, limit=10)
            
            # Get tier progression history
            tier_history = await self._get_tier_history(user_id)
            
            # Get current tier benefits
            current_tier = self._get_user_tier(user["total_referrals"])
            tier_benefits = self.tier_configs[current_tier]["benefits"]
            
            # Calculate next tier requirements
            next_tier = self._get_next_tier(current_tier)
            next_tier_requirements = self._get_tier_requirements(next_tier) if next_tier else None
            
            # Generate referral link
            referral_link = f"https://orion-starline.com/signup?ref={user['referral_code']}"
            
            return {
                "user_id": user_id,
                "email": user["email"],
                "current_tier": current_tier.value,
                "tier_color": self.tier_configs[current_tier]["color"],
                "statistics": stats,
                "recent_referrals": recent_referrals,
                "tier_history": tier_history,
                "current_benefits": tier_benefits,
                "next_tier_requirements": next_tier_requirements,
                "referral_link": referral_link,
                "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={referral_link}",
                "share_options": {
                    "email": f"Menga Orion Starline da qo'shiling! Referral link: {referral_link}",
                    "social_media": f"🚀 AI Trading platform Orion Starline! Men orqali ro'yxatdan o'ting: {referral_link}",
                    "whatsapp": f"Orion Starline AI Trading platform! Referral link: {referral_link}"
                },
                "leaderboard_position": await self._get_leaderboard_position(user_id)
            }
            
        except Exception as e:
            logger.error(f"User dashboard error: {e}")
            return {"error": str(e)}
    
    async def create_campaign(
        self,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        reward_multiplier: float = 1.0,
        special_tiers: Dict = None
    ) -> Dict:
        """Special referral campaign yaratish"""
        try:
            campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            campaign = {
                "id": campaign_id,
                "name": name,
                "description": description,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "reward_multiplier": reward_multiplier,
                "special_tiers": special_tiers or {},
                "status": "active",
                "participants": 0,
                "total_referrals": 0,
                "total_rewards_distributed": 0.0,
                "created_at": datetime.now().isoformat()
            }
            
            await self._save_campaign(campaign)
            
            # Apply campaign benefits to eligible users
            eligible_users = await self._get_eligible_campaign_users(campaign)
            for user in eligible_users:
                await self._apply_campaign_benefits(user["id"], campaign_id)
            
            logger.info(f"Referral campaign created: {campaign_id}")
            
            return {
                "status": "created",
                "campaign_id": campaign_id,
                "campaign_name": name,
                "duration_days": (end_date - start_date).days,
                "reward_multiplier": reward_multiplier,
                "eligible_participants": len(eligible_users),
                "expected_impact": {
                    "referral_increase": f"{int(reward_multiplier * 100 - 100)}%",
                    "engagement_boost": f"{int(reward_multiplier * 50)}%"
                }
            }
            
        except Exception as e:
            logger.error(f"Campaign creation error: {e}")
            return {"error": str(e)}
    
    async def get_referral_analytics(
        self,
        date_range: Tuple[datetime, datetime] = None
    ) -> Dict:
        """Referral system analytics"""
        try:
            if not date_range:
                date_range = (datetime.now() - timedelta(days=30), datetime.now())
            
            # Get system-wide statistics
            stats = await self._get_system_statistics(date_range)
            
            # Get tier distribution
            tier_distribution = await self._get_tier_distribution()
            
            # Get top performers
            top_performers = await self._get_top_performers(limit=10)
            
            # Get conversion funnel
            conversion_funnel = await self._get_conversion_funnel(date_range)
            
            # Get geographic distribution
            geo_distribution = await self._get_geographic_distribution(date_range)
            
            # Calculate ROI
            roi_analysis = await self._calculate_referral_roi(date_range)
            
            return {
                "report_period": {
                    "start": date_range[0].isoformat(),
                    "end": date_range[1].isoformat()
                },
                "system_statistics": stats,
                "tier_distribution": tier_distribution,
                "top_performers": top_performers,
                "conversion_funnel": conversion_funnel,
                "geographic_insights": geo_distribution,
                "roi_analysis": roi_analysis,
                "recommendations": [
                    "Bronze tier users uchun qo'shimcha incentive berish",
                    "Geographic expansion uchun localized referral programs",
                    "Tier progression speed ni oshirish uchun milestone rewards",
                    "Viral referral mechanics qo'shish"
                ]
            }
            
        except Exception as e:
            logger.error(f"Referral analytics error: {e}")
            return {"error": str(e)}
    
    async def optimize_referral_program(self) -> Dict:
        """Referral program optimization"""
        try:
            # Analyze current performance
            performance_analysis = await self._analyze_current_performance()
            
            # Identify optimization opportunities
            optimization_opportunities = await self._identify_optimization_opportunities()
            
            # Generate A/B testing recommendations
            ab_test_recommendations = await self._generate_ab_test_recommendations()
            
            # Calculate potential improvements
            improvement_projections = await self._calculate_improvement_projections()
            
            return {
                "current_performance": performance_analysis,
                "optimization_opportunities": optimization_opportunities,
                "ab_test_recommendations": ab_test_recommendations,
                "improvement_projections": improvement_projections,
                "implementation_roadmap": {
                    "immediate": ["Tier benefits optimization", "Referral link presentation"],
                    "short_term": ["Gamification elements", "Social sharing integration"],
                    "long_term": ["Multi-tier rewards", "Partnership programs"]
                },
                "expected_outcomes": {
                    "referral_rate_increase": "25-40%",
                    "tier_progression_speed": "30% faster",
                    "user_lifetime_value": "20% improvement"
                }
            }
            
        except Exception as e:
            logger.error(f"Referral optimization error: {e}")
            return {"error": str(e)}
    
    # Helper methods
    def _get_user_tier(self, total_referrals: int) -> ReferralTier:
        """Get user tier based on referral count"""
        if total_referrals >= 101:
            return ReferralTier.PLATINUM
        elif total_referrals >= 51:
            return ReferralTier.GOLD
        elif total_referrals >= 11:
            return ReferralTier.SILVER
        else:
            return ReferralTier.BRONZE
    
    def _get_next_tier(self, current_tier: ReferralTier) -> Optional[ReferralTier]:
        """Get next tier for current tier"""
        tier_progression = {
            ReferralTier.BRONZE: ReferralTier.SILVER,
            ReferralTier.SILVER: ReferralTier.GOLD,
            ReferralTier.GOLD: ReferralTier.PLATINUM,
            ReferralTier.PLATINUM: None
        }
        return tier_progression.get(current_tier)
    
    def _get_tier_requirements(self, tier: ReferralTier) -> Dict:
        """Get requirements for tier progression"""
        config = self.tier_configs[tier]
        return {
            "min_referrals": config["min_referrals"],
            "commission_rate": config["commission_rate"],
            "benefits": config["benefits"]
        }
    
    def _calculate_tier_bonus(self, tier: ReferralTier, purchase_amount: float) -> float:
        """Calculate tier-based bonus"""
        bonus_rates = {
            ReferralTier.BRONZE: 0.0,
            ReferralTier.SILVER: 0.01,  # 1% bonus
            ReferralTier.GOLD: 0.02,    # 2% bonus
            ReferralTier.PLATINUM: 0.03  # 3% bonus
        }
        return purchase_amount * bonus_rates.get(tier, 0.0)
    
    def _calculate_volume_discount(self, total_referrals: int, purchase_amount: float) -> float:
        """Calculate volume discount for high-tier users"""
        if total_referrals >= 200:
            return 0.05  # 5% additional
        elif total_referrals >= 100:
            return 0.03  # 3% additional
        elif total_referrals >= 50:
            return 0.02  # 2% additional
        return 0.0
    
    async def _save_user(self, user: User):
        """Save user to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (id, email, referral_code, referred_by, total_referrals, total_earnings, tier, join_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user.id, user.email, user.referral_code, user.referred_by,
            user.total_referrals, user.total_earnings, user.tier.value,
            user.join_date.isoformat() if user.join_date else None
        ))
        
        conn.commit()
        conn.close()
    
    async def _save_referral(self, referral: Referral):
        """Save referral to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO referrals 
            (id, referrer_code, referee_id, status, reward_type, reward_amount, 
             commission_rate, created_at, completed_at, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            referral.id, referral.referrer_code, referral.referee_id,
            referral.status.value, referral.reward_type.value,
            referral.reward_amount, referral.commission_rate,
            referral.created_at.isoformat(),
            referral.completed_at.isoformat() if referral.completed_at else None,
            referral.is_verified
        ))
        
        conn.commit()
        conn.close()
    
    async def _save_referral_code(self, code: ReferralCode):
        """Save referral code to database"""
        # For this example, we'll store in users table
        # In a real system, you'd have a separate referral_codes table
        pass
    
    async def _get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "email": user[1],
                "referral_code": user[2],
                "referred_by": user[3],
                "total_referrals": user[4],
                "total_earnings": user[5],
                "tier": user[6]
            }
        return None
    
    async def _get_user_by_referral_code(self, referral_code: str) -> Optional[Dict]:
        """Get user by referral code"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE referral_code = ?", (referral_code,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "email": user[1],
                "referral_code": user[2],
                "referred_by": user[3],
                "total_referrals": user[4],
                "total_earnings": user[5],
                "tier": user[6]
            }
        return None
    
    async def _check_existing_referral(self, referral_code: str, referee_id: str) -> bool:
        """Check if referral already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM referrals 
            WHERE referrer_code = ? AND referee_id = ?
        """, (referral_code, referee_id))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    async def _update_referrer_stats(self, referrer_id: str):
        """Update referrer statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total referrals for this user
        cursor.execute("""
            SELECT COUNT(*) FROM referrals 
            WHERE referrer_code = (SELECT referral_code FROM users WHERE id = ?)
        """, (referrer_id,))
        
        total_referrals = cursor.fetchone()[0]
        
        # Update user stats
        cursor.execute("""
            UPDATE users 
            SET total_referrals = ? 
            WHERE id = ?
        """, (total_referrals, referrer_id))
        
        conn.commit()
        conn.close()
    
    async def _get_user_statistics(self, user_id: str) -> Dict:
        """Get user referral statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total referrals
        cursor.execute("""
            SELECT COUNT(*) FROM referrals 
            WHERE referrer_code = (SELECT referral_code FROM users WHERE id = ?)
        """, (user_id,))
        total_referrals = cursor.fetchone()[0]
        
        # Completed referrals
        cursor.execute("""
            SELECT COUNT(*) FROM referrals 
            WHERE referrer_code = (SELECT referral_code FROM users WHERE id = ?)
            AND status = 'completed'
        """, (user_id,))
        completed_referrals = cursor.fetchone()[0]
        
        # Total earnings
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM reward_transactions 
            WHERE user_id = ? AND transaction_type = 'commission'
        """, (user_id,))
        total_earnings = cursor.fetchone()[0]
        
        # This month referrals
        this_month = datetime.now().replace(day=1)
        cursor.execute("""
            SELECT COUNT(*) FROM referrals 
            WHERE referrer_code = (SELECT referral_code FROM users WHERE id = ?)
            AND created_at >= ?
        """, (user_id, this_month.isoformat()))
        this_month_referrals = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_referrals": total_referrals,
            "completed_referrals": completed_referrals,
            "conversion_rate": (completed_referrals / total_referrals * 100) if total_referrals > 0 else 0,
            "total_earnings": total_earnings,
            "this_month_referrals": this_month_referrals,
            "average_earnings_per_referral": (total_earnings / total_referrals) if total_referrals > 0 else 0
        }
    
    async def _send_referral_notification(self, referrer: Dict, referee_id: str) -> bool:
        """Send referral notification"""
        # In a real system, this would send email/SMS/notification
        logger.info(f"Referral notification sent to {referrer['email']}")
        return True
    
    async def _save_commission_transaction(
        self,
        transaction_id: str,
        user_id: str,
        amount: float,
        description: str,
        purchase_amount: float
    ):
        """Save commission transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reward_transactions 
            (id, user_id, transaction_type, amount, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            transaction_id, user_id, "commission", amount,
            description, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def _update_referrer_earnings(self, referrer_id: str, commission: float):
        """Update referrer total earnings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET total_earnings = total_earnings + ?
            WHERE id = ?
        """, (commission, referrer_id))
        
        conn.commit()
        conn.close()
    
    async def _check_tier_progression(self, user_id: str) -> Dict:
        """Check if user qualifies for tier progression"""
        user = await self._get_user_by_id(user_id)
        if not user:
            return {}
        
        current_tier = self._get_user_tier(user["total_referrals"])
        next_tier = self._get_next_tier(current_tier)
        
        if next_tier:
            next_tier_reqs = self._get_tier_requirements(next_tier)
            referrals_needed = max(0, next_tier_reqs["min_referrals"] - user["total_referrals"])
            
            if referrals_needed == 0:
                # Upgrade tier
                await self._upgrade_user_tier(user_id, current_tier, next_tier)
                return {
                    "upgraded": True,
                    "from_tier": current_tier.value,
                    "to_tier": next_tier.value,
                    "benefits_unlocked": next_tier_reqs["benefits"]
                }
        
        return {"upgraded": False}
    
    async def _upgrade_user_tier(self, user_id: str, from_tier: ReferralTier, to_tier: ReferralTier):
        """Upgrade user tier"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update user tier
        cursor.execute("""
            UPDATE users SET tier = ? WHERE id = ?
        """, (to_tier.value, user_id))
        
        # Record tier history
        tier_history_id = f"tier_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cursor.execute("""
            INSERT INTO tier_history 
            (id, user_id, from_tier, to_tier, trigger_referrals, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tier_history_id, user_id, from_tier.value, to_tier.value,
            user_id, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def _save_campaign(self, campaign: Dict):
        """Save campaign to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referral_campaigns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                reward_multiplier REAL,
                special_tiers TEXT,
                status TEXT,
                participants INTEGER,
                total_referrals INTEGER,
                total_rewards_distributed REAL,
                created_at TEXT
            )
        """)
        
        cursor.execute("""
            INSERT OR REPLACE INTO referral_campaigns 
            (id, name, description, start_date, end_date, reward_multiplier, 
             special_tiers, status, participants, total_referrals, total_rewards_distributed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign["id"], campaign["name"], campaign["description"],
            campaign["start_date"], campaign["end_date"], campaign["reward_multiplier"],
            json.dumps(campaign["special_tiers"]), campaign["status"],
            campaign["participants"], campaign["total_referrals"],
            campaign["total_rewards_distributed"], campaign["created_at"]
        ))
        
        conn.commit()
        conn.close()
    
    async def _get_recent_referrals(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent referrals for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.*, u.email as referee_email 
            FROM referrals r
            JOIN users u ON r.referee_id = u.id
            WHERE r.referrer_code = (SELECT referral_code FROM users WHERE id = ?)
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        referrals = cursor.fetchall()
        conn.close()
        
        return [
            {
                "referee_email": ref[8],  # referee_email
                "status": ref[3],        # status
                "commission_rate": ref[6],
                "created_at": ref[7]
            }
            for ref in referrals
        ]
    
    async def _get_tier_history(self, user_id: str) -> List[Dict]:
        """Get tier progression history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tier_history 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
        
        history = cursor.fetchall()
        conn.close()
        
        return [
            {
                "from_tier": record[2],
                "to_tier": record[3],
                "trigger_referrals": record[4],
                "created_at": record[5]
            }
            for record in history
        ]
    
    async def _get_leaderboard_position(self, user_id: str) -> Dict:
        """Get user's position on leaderboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user's referral count
        cursor.execute("""
            SELECT total_referrals FROM users WHERE id = ?
        """, (user_id,))
        user_referrals = cursor.fetchone()
        
        if not user_referrals:
            return {"position": None, "total_users": 0}
        
        # Count how many users have more referrals
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE total_referrals > ?
        """, (user_referrals[0],))
        users_with_more = cursor.fetchone()[0]
        
        # Get total active users
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE total_referrals > 0
        """, ())
        total_users = cursor.fetchone()[0]
        
        position = users_with_more + 1 if total_users > 0 else None
        
        conn.close()
        
        return {
            "position": position,
            "total_users": total_users,
            "percentile": ((total_users - position + 1) / total_users * 100) if position else 0
        }
    
    # Placeholder methods for analytics (would need real implementation)
    async def _get_system_statistics(self, date_range: Tuple[datetime, datetime]) -> Dict:
        return {"total_referrals": 1250, "total_commission_paid": 45000.0}
    
    async def _get_tier_distribution(self) -> Dict:
        return {"bronze": 45, "silver": 25, "gold": 15, "platinum": 5}
    
    async def _get_top_performers(self, limit: int) -> List[Dict]:
        return [{"rank": 1, "email": "user1@example.com", "referrals": 150, "earnings": 2500.0}]
    
    async def _get_conversion_funnel(self, date_range: Tuple[datetime, datetime]) -> Dict:
        return {"signups": 1000, "verified": 800, "active": 600, "referring": 200}
    
    async def _get_geographic_distribution(self, date_range: Tuple[datetime, datetime]) -> Dict:
        return {"Uzbekistan": 70, "Kazakhstan": 15, "Kyrgyzstan": 10, "Other": 5}
    
    async def _calculate_referral_roi(self, date_range: Tuple[datetime, datetime]) -> Dict:
        return {"total_investment": 10000, "total_revenue": 45000, "roi": 350}
    
    async def _analyze_current_performance(self) -> Dict:
        return {"conversion_rate": 4.2, "avg_referrals_per_user": 3.5}
    
    async def _identify_optimization_opportunities(self) -> List[str]:
        return ["Bronze tier activation", "Referral link presentation", "Onboarding flow"]
    
    async def _generate_ab_test_recommendations(self) -> List[Dict]:
        return [{"test": "Referral link format", "hypothesis": "Visual links perform better"}]
    
    async def _calculate_improvement_projections(self) -> Dict:
        return {"referral_rate_increase": 25, "tier_progression_speed": 30}
    
    async def _get_eligible_campaign_users(self, campaign: Dict) -> List[Dict]:
        return []  # Simplified for demo