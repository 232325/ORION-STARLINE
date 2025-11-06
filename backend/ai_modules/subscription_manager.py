"""
Subscription Manager - Obuna boshqaruv tizimi

Signal marketplace uchun obuna boshqaruv, to'lov ishlov va pricing
tizimini ta'minlaydi. Multiple pricing tiers, free trials, enterprise
packages va loyalty programni qo'llab-quvvatlaydi.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np
import pandas as pd
from decimal import Decimal
import hashlib
import jwt
import stripe
import paypal
from pathlib import Path

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentProvider(Enum):
    """To'lov provayderlari"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    CRYPTO = "crypto"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO_WALLET = "crypto_wallet"

class SubscriptionStatus(Enum):
    """Obuna holatlari"""
    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    REFUNDED = "refunded"

class PlanType(Enum):
    """Reja turlari"""
    FREE = "free"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"
    ENTERPRISE = "enterprise"

class DiscountType(Enum):
    """Chegirma turlari"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    BUY_X_GET_Y = "buy_x_get_y"

class ReferralStatus(Enum):
    """Referral holatlari"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"

@dataclass
class PricingPlan:
    """Pricing reja"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    plan_type: PlanType = PlanType.MONTHLY
    price: float = 0.0
    currency: str = "USD"
    duration_days: int = 30
    max_signals: int = 5
    max_commodities: int = 3
    features: List[str] = field(default_factory=list)
    api_access: bool = False
    priority_support: bool = False
    custom_strategies: bool = False
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    trial_days: int = 0
    max_users: int = 1  # Enterprise uchun

@dataclass
class Subscription:
    """Obuna ma'lumotlari"""
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    plan_id: str = ""
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    payment_provider: PaymentProvider = PaymentProvider.STRIPE
    external_subscription_id: str = ""  # Stripe, PayPal ID
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    auto_renew: bool = True
    next_billing_date: Optional[datetime] = None
    amount: float = 0.0
    currency: str = "USD"
    discount_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    usage_stats: Dict[str, Any] = field(default_factory=dict)
    payment_history: List[Dict[str, Any]] = field(default_factory=list)
    cancellation_reason: Optional[str] = None
    refund_amount: float = 0.0

@dataclass
class DiscountCode:
    """Chegirma kodi"""
    code_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    code: str = ""
    discount_type: DiscountType = DiscountType.PERCENTAGE
    value: float = 0.0  # percentage yoki fixed amount
    min_amount: float = 0.0
    max_discount: Optional[float] = None
    usage_limit: int = 1
    used_count: int = 0
    is_active: bool = True
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    applicable_plans: List[str] = field(default_factory=list)
    created_by: str = ""
    description: str = ""
    max_uses_per_user: int = 1

@dataclass
class ReferralProgram:
    """Referral dasturi"""
    referral_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    referrer_id: str = ""
    referee_id: str = ""
    referral_code: str = ""
    status: ReferralStatus = ReferralStatus.PENDING
    reward_type: str = "percentage"  # percentage, fixed_amount, free_months
    reward_value: float = 0.0
    currency: str = "USD"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    reward_claimed: bool = False
    reward_claimed_at: Optional[datetime] = None

class SubscriptionManager:
    """Obuna boshqaruv tizimi"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Payment providers
        self.stripe_client = None
        self.paypal_client = None
        self._initialize_payment_providers()
        
        # Data storage
        self.pricing_plans: Dict[str, PricingPlan] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.discount_codes: Dict[str, DiscountCode] = {}
        self.referral_programs: Dict[str, ReferralProgram] = {}
        self.payment_history: List[Dict[str, Any]] = []
        
        # Business logic
        self.commission_rate = 0.05  # 5%
        self.default_currency = "USD"
        self.auto_billing_enabled = True
        self.refund_policy_days = 30
        
        # Analytics
        self.analytics = {
            "total_revenue": 0.0,
            "monthly_recurring_revenue": 0.0,
            "churn_rate": 0.0,
            "average_revenue_per_user": 0.0,
            "conversion_rate": 0.0
        }
        
        self._initialize_default_plans()
        self._initialize_default_discounts()
    
    def _initialize_payment_providers(self):
        """To'lov provayderlarini boshlash"""
        try:
            # Stripe initialization
            stripe_api_key = self.config.get("stripe_api_key")
            if stripe_api_key:
                self.stripe_client = stripe
                self.stripe_client.api_key = stripe_api_key
            
            # PayPal initialization
            paypal_client_id = self.config.get("paypal_client_id")
            paypal_client_secret = self.config.get("paypal_client_secret")
            if paypal_client_id and paypal_client_secret:
                self.paypal_client = paypal
                # PayPal setup would go here
            
            logger.info("To'lov provayderlari tayyorlandi")
            
        except Exception as e:
            logger.error(f"To'lov provayderlari xatosi: {e}")
    
    def _initialize_default_plans(self):
        """Standart pricing rejalarni yaratish"""
        default_plans = [
            {
                "name": "Free Plan",
                "description": "Basic access to limited signals",
                "plan_type": PlanType.FREE,
                "price": 0.0,
                "max_signals": 3,
                "max_commodities": 1,
                "features": ["basic_signals", "limited_analytics"],
                "trial_days": 0
            },
            {
                "name": "Basic Plan",
                "description": "Starter package for new traders",
                "plan_type": PlanType.MONTHLY,
                "price": 29.99,
                "duration_days": 30,
                "max_signals": 10,
                "max_commodities": 3,
                "features": ["basic_signals", "analytics", "alerts", "email_support"],
                "trial_days": 7
            },
            {
                "name": "Premium Plan",
                "description": "Professional trading signals",
                "plan_type": PlanType.MONTHLY,
                "price": 99.99,
                "duration_days": 30,
                "max_signals": 50,
                "max_commodities": 10,
                "features": ["all_signals", "advanced_analytics", "alerts", "api_access", "priority_support"],
                "trial_days": 14
            },
            {
                "name": "Elite Plan",
                "description": "Advanced trading for professionals",
                "plan_type": PlanType.MONTHLY,
                "price": 299.99,
                "duration_days": 30,
                "max_signals": 200,
                "max_commodities": 50,
                "features": ["all_signals", "elite_analytics", "alerts", "api_access", "custom_strategies", "priority_support"],
                "trial_days": 14
            },
            {
                "name": "VIP Plan",
                "description": "Ultimate trading experience",
                "plan_type": PlanType.MONTHLY,
                "price": 999.99,
                "duration_days": 30,
                "max_signals": -1,  # Unlimited
                "max_commodities": -1,
                "features": ["all_signals", "vip_analytics", "alerts", "api_access", "custom_strategies", "priority_support", "personal_manager"],
                "trial_days": 30
            },
            {
                "name": "Enterprise Plan",
                "description": "Custom solutions for organizations",
                "plan_type": PlanType.ENTERPRISE,
                "price": 0.0,  # Custom pricing
                "duration_days": 365,
                "max_signals": -1,
                "max_commodities": -1,
                "max_users": 100,
                "features": ["all_signals", "enterprise_analytics", "api_access", "custom_strategies", "dedicated_support", "training"],
                "trial_days": 30
            }
        ]
        
        for plan_data in default_plans:
            plan = PricingPlan(**plan_data)
            self.pricing_plans[plan.plan_id] = plan
        
        logger.info(f"{len(default_plans)} ta standart reja yaratildi")
    
    def _initialize_default_discounts(self):
        """Standart chegirma kodlarini yaratish"""
        now = datetime.now()
        
        default_discounts = [
            {
                "code": "WELCOME20",
                "discount_type": DiscountType.PERCENTAGE,
                "value": 20.0,
                "min_amount": 50.0,
                "usage_limit": 1000,
                "valid_until": now + timedelta(days=90),
                "description": "20% discount for new users"
            },
            {
                "code": "SAVE50",
                "discount_type": DiscountType.FIXED_AMOUNT,
                "value": 50.0,
                "min_amount": 100.0,
                "usage_limit": 500,
                "valid_until": now + timedelta(days=60),
                "description": "$50 off orders over $100"
            },
            {
                "code": "YEARLY25",
                "discount_type": DiscountType.PERCENTAGE,
                "value": 25.0,
                "applicable_plans": [p.plan_id for p in self.pricing_plans.values() if p.plan_type in [PlanType.MONTHLY, PlanType.QUARTERLY, PlanType.YEARLY]],
                "usage_limit": 200,
                "valid_until": now + timedelta(days=365),
                "description": "25% off yearly subscriptions"
            }
        ]
        
        for discount_data in default_discounts:
            discount = DiscountCode(**discount_data)
            self.discount_codes[discount.code] = discount
        
        logger.info(f"{len(default_discounts)} ta chegirma kodi yaratildi")
    
    async def create_subscription(self,
                                user_id: str,
                                plan_id: str,
                                payment_provider: PaymentProvider = PaymentProvider.STRIPE,
                                discount_code: Optional[str] = None,
                                **kwargs) -> str:
        """
        Yangi obuna yaratish
        
        Args:
            user_id: Foydalanuvchi ID
            plan_id: Reja ID
            payment_provider: To'lov provayder
            discount_code: Chegirma kodi
        
        Returns:
            subscription_id: Obuna ID
        """
        try:
            # Reja tekshiruvi
            if plan_id not in self.pricing_plans:
                raise ValueError("Reja topilmadi")
            
            plan = self.pricing_plans[plan_id]
            
            # Narx hisoblash
            base_price = plan.price
            discount = 0.0
            
            if discount_code:
                discount = await self._calculate_discount(discount_code, base_price, user_id)
            
            final_price = base_price - discount
            
            # Payment processing
            payment_result = await self._process_payment(
                amount=final_price,
                currency=plan.currency,
                provider=payment_provider,
                user_id=user_id,
                **kwargs
            )
            
            if not payment_result["success"]:
                raise ValueError(f"To'lov muvaffaqiyatsiz: {payment_result['error']}")
            
            # Obuna yaratish
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                payment_provider=payment_provider,
                external_subscription_id=payment_result.get("subscription_id", ""),
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=plan.duration_days),
                trial_end_date=datetime.now() + timedelta(days=plan.trial_days) if plan.trial_days > 0 else None,
                auto_renew=kwargs.get("auto_renew", True),
                next_billing_date=datetime.now() + timedelta(days=plan.duration_days),
                amount=final_price,
                currency=plan.currency,
                discount_code=discount_code
            )
            
            # Muddati tekshirish
            if plan.trial_days > 0:
                subscription.status = SubscriptionStatus.TRIAL
            
            # Saqlash
            self.subscriptions[subscription.subscription_id] = subscription
            
            # Analytics
            await self._update_analytics("subscription_created", final_price)
            
            logger.info(f"Obuna yaratildi: {subscription.subscription_id} - ${final_price}")
            return subscription.subscription_id
            
        except Exception as e:
            logger.error(f"Obuna yaratish xatosi: {e}")
            raise
    
    async def cancel_subscription(self,
                                subscription_id: str,
                                reason: str = "",
                                immediate: bool = False) -> bool:
        """
        Obunani bekor qilish
        
        Args:
            subscription_id: Obuna ID
            reason: Bekor qilish sababi
            immediate: Darhol bekor qilish
        
        Returns:
            bool: Muvaffaqiyat holati
        """
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            
            # External providerda ham bekor qilish
            if subscription.external_subscription_id:
                await self._cancel_external_subscription(subscription)
            
            if immediate:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.end_date = datetime.now()
            else:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.cancellation_reason = reason
                # Current period oxirida bekor qilish
            
            subscription.updated_at = datetime.now()
            
            # Analytics
            await self._update_analytics("subscription_canceled")
            
            logger.info(f"Obuna bekor qilindi: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Obuna bekor qilish xatosi: {e}")
            return False
    
    async def renew_subscription(self, subscription_id: str) -> bool:
        """
        Obunani yangilash
        
        Args:
            subscription_id: Obuna ID
        
        Returns:
            bool: Muvaffaqiyat holati
        """
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            plan = self.pricing_plans[subscription.plan_id]
            
            # Payment processing
            payment_result = await self._process_payment(
                amount=plan.price,
                currency=plan.currency,
                provider=subscription.payment_provider,
                user_id=subscription.user_id,
                description=f"Renewal for {plan.name}"
            )
            
            if not payment_result["success"]:
                subscription.status = SubscriptionStatus.PAST_DUE
                return False
            
            # Obuna yangilash
            subscription.start_date = datetime.now()
            subscription.end_date = datetime.now() + timedelta(days=plan.duration_days)
            subscription.next_billing_date = datetime.now() + timedelta(days=plan.duration_days)
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.updated_at = datetime.now()
            
            # Analytics
            await self._update_analytics("subscription_renewed", plan.price)
            
            logger.info(f"Obuna yangilandi: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Obuna yangilash xatosi: {e}")
            return False
    
    async def process_refund(self,
                           subscription_id: str,
                           amount: Optional[float] = None,
                           reason: str = "") -> bool:
        """
        Qaytarish (refund) so'rovi
        
        Args:
            subscription_id: Obuna ID
            amount: Qaytariladigan summa
            reason: Sabab
        
        Returns:
            bool: Muvaffaqiyat holati
        """
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            
            # Refund amount hisoblash
            if amount is None:
                amount = subscription.amount
            
            # Refund processing
            refund_result = await self._process_refund(
                external_subscription_id=subscription.external_subscription_id,
                amount=amount,
                provider=subscription.payment_provider
            )
            
            if not refund_result["success"]:
                return False
            
            # Obuna holatini yangilash
            subscription.status = SubscriptionStatus.REFUNDED
            subscription.refund_amount = amount
            subscription.updated_at = datetime.now()
            
            # Payment history
            subscription.payment_history.append({
                "type": "refund",
                "amount": amount,
                "reason": reason,
                "timestamp": datetime.now()
            })
            
            # Analytics
            await self._update_analytics("refund_processed", -amount)
            
            logger.info(f"Refund qaytarildi: {subscription_id} - ${amount}")
            return True
            
        except Exception as e:
            logger.error(f"Refund xatosi: {e}")
            return False
    
    async def get_subscription_details(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Obuna tafsilotlarini olish
        
        Args:
            subscription_id: Obuna ID
        
        Returns:
            Dict: Obuna ma'lumotlari
        """
        try:
            if subscription_id not in self.subscriptions:
                return None
            
            subscription = self.subscriptions[subscription_id]
            plan = self.pricing_plans[subscription.plan_id]
            
            # Usage statistics
            usage_stats = await self._calculate_usage_stats(subscription.user_id, subscription.plan_id)
            
            return {
                "subscription_id": subscription.subscription_id,
                "user_id": subscription.user_id,
                "plan": {
                    "plan_id": plan.plan_id,
                    "name": plan.name,
                    "plan_type": plan.plan_type.value,
                    "price": plan.price,
                    "currency": plan.currency
                },
                "status": subscription.status.value,
                "start_date": subscription.start_date.isoformat(),
                "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
                "trial_end_date": subscription.trial_end_date.isoformat() if subscription.trial_end_date else None,
                "auto_renew": subscription.auto_renew,
                "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
                "amount": subscription.amount,
                "currency": subscription.currency,
                "discount_code": subscription.discount_code,
                "payment_provider": subscription.payment_provider.value,
                "usage_stats": usage_stats,
                "days_remaining": (subscription.end_date - datetime.now()).days if subscription.end_date else 0,
                "is_trial": subscription.status == SubscriptionStatus.TRIAL
            }
            
        except Exception as e:
            logger.error(f"Obuna tafsilotlari xatosi: {e}")
            return None
    
    async def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Foydalanuvchi obunalarini olish
        
        Args:
            user_id: Foydalanuvchi ID
        
        Returns:
            List: Obuna ro'yxati
        """
        try:
            user_subscriptions = []
            
            for subscription in self.subscriptions.values():
                if subscription.user_id == user_id:
                    details = await self.get_subscription_details(subscription.subscription_id)
                    if details:
                        user_subscriptions.append(details)
            
            # Active obunalar birinchi
            user_subscriptions.sort(key=lambda x: (x["status"] == "active", x["end_date"]), reverse=True)
            
            return user_subscriptions
            
        except Exception as e:
            logger.error(f"Foydalanuvchi obunalari xatosi: {e}")
            return []
    
    async def validate_discount_code(self,
                                   code: str,
                                   user_id: str,
                                   amount: float) -> Dict[str, Any]:
        """
        Chegirma kodini tekshirish
        
        Args:
            code: Chegirma kodi
            user_id: Foydalanuvchi ID
            amount: Summa
        
        Returns:
            Dict: Tekshiruv natijasi
        """
        try:
            if code not in self.discount_codes:
                return {"valid": False, "error": "Kod topilmadi"}
            
            discount = self.discount_codes[code]
            
            # Aktivligi
            if not discount.is_active:
                return {"valid": False, "error": "Kod faol emas"}
            
            # Muddati
            if discount.valid_until and datetime.now() > discount.valid_until:
                return {"valid": False, "error": "Kodning muddati tugagan"}
            
            # Minimal summa
            if amount < discount.min_amount:
                return {"valid": False, "error": f"Minimal summa ${discount.min_amount}"}
            
            # Foydalanish limiti
            if discount.used_count >= discount.usage_limit:
                return {"valid": False, "error": "Kod foydalanish limitiga yetgan"}
            
            # Foydalanuvchi foydalanishi
            # (user discount usage tracking would go here)
            
            # Chegirma hisoblash
            discount_amount = await self._calculate_discount_amount(code, amount)
            
            return {
                "valid": True,
                "discount_amount": discount_amount,
                "final_amount": amount - discount_amount,
                "discount_details": {
                    "code": code,
                    "type": discount.discount_type.value,
                    "value": discount.value
                }
            }
            
        except Exception as e:
            logger.error(f"Chegirma kodi tekshiruvi xatosi: {e}")
            return {"valid": False, "error": "Tekshiruv xatosi"}
    
    async def create_referral(self, referrer_id: str, referee_id: str) -> str:
        """
        Referral dasturi yaratish
        
        Args:
            referrer_id: Taklif qiluvchi ID
            referee_id: Taklif qilingan ID
        
        Returns:
            referral_id: Referral ID
        """
        try:
            # Referral kod yaratish
            referral_code = f"REF{referrer_id[:6].upper()}{int(time.time())}"
            
            referral = ReferralProgram(
                referrer_id=referrer_id,
                referee_id=referee_id,
                referral_code=referral_code,
                reward_type="percentage",
                reward_value=20.0  # 20% reward
            )
            
            self.referral_programs[referral.referral_id] = referral
            
            logger.info(f"Referral yaratildi: {referral.referral_id}")
            return referral.referral_id
            
        except Exception as e:
            logger.error(f"Referral yaratish xatosi: {e}")
            raise
    
    async def get_pricing_plans(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Pricing rejalarni olish
        
        Args:
            include_inactive: Faol bo'lmagan rejalami ham
        
        Returns:
            List: Reja ro'yxati
        """
        try:
            plans = []
            
            for plan in self.pricing_plans.values():
                if not include_inactive and not plan.is_active:
                    continue
                
                plan_dict = {
                    "plan_id": plan.plan_id,
                    "name": plan.name,
                    "description": plan.description,
                    "plan_type": plan.plan_type.value,
                    "price": plan.price,
                    "currency": plan.currency,
                    "duration_days": plan.duration_days,
                    "max_signals": plan.max_signals,
                    "max_commodities": plan.max_commodities,
                    "features": plan.features,
                    "api_access": plan.api_access,
                    "priority_support": plan.priority_support,
                    "custom_strategies": plan.custom_strategies,
                    "trial_days": plan.trial_days,
                    "max_users": plan.max_users,
                    "is_popular": plan.name in ["Premium Plan", "Elite Plan"]
                }
                plans.append(plan_dict)
            
            # Price bo'yicha saralash
            plans.sort(key=lambda x: x["price"])
            
            return plans
            
        except Exception as e:
            logger.error(f"Pricing rejalar xatosi: {e}")
            return []
    
    async def get_subscription_analytics(self) -> Dict[str, Any]:
        """
        Obuna analytics
        
        Returns:
            Dict: Analytics ma'lumotlari
        """
        try:
            # Basic stats
            total_subscriptions = len(self.subscriptions)
            active_subscriptions = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.ACTIVE])
            trial_subscriptions = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.TRIAL])
            
            # Revenue calculations
            total_revenue = sum(s.amount for s in self.subscriptions.values() if s.status != SubscriptionStatus.REFUNDED)
            monthly_revenue = sum(s.amount for s in self.subscriptions.values() 
                                if s.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
            
            # Plan distribution
            plan_distribution = {}
            for subscription in self.subscriptions.values():
                plan = self.pricing_plans[subscription.plan_id]
                plan_name = plan.name
                plan_distribution[plan_name] = plan_distribution.get(plan_name, 0) + 1
            
            # Churn rate
            canceled_subscriptions = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.CANCELED])
            churn_rate = (canceled_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0
            
            # ARPU
            arpu = (total_revenue / len(set(s.user_id for s in self.subscriptions.values()))) if self.subscriptions else 0
            
            return {
                "total_subscriptions": total_subscriptions,
                "active_subscriptions": active_subscriptions,
                "trial_subscriptions": trial_subscriptions,
                "total_revenue": total_revenue,
                "monthly_recurring_revenue": monthly_revenue,
                "average_revenue_per_user": arpu,
                "churn_rate": churn_rate,
                "plan_distribution": plan_distribution,
                "top_plans": sorted(plan_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
            }
            
        except Exception as e:
            logger.error(f"Analytics xatosi: {e}")
            return {}
    
    async def _process_payment(self,
                             amount: float,
                             currency: str,
                             provider: PaymentProvider,
                             user_id: str,
                             **kwargs) -> Dict[str, Any]:
        """To'lovni qayta ishlash"""
        try:
            if provider == PaymentProvider.STRIPE:
                return await self._process_stripe_payment(amount, currency, user_id, **kwargs)
            elif provider == PaymentProvider.PAYPAL:
                return await self._process_paypal_payment(amount, currency, user_id, **kwargs)
            else:
                return {"success": False, "error": "Unsupported payment provider"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_stripe_payment(self,
                                    amount: float,
                                    currency: str,
                                    user_id: str,
                                    **kwargs) -> Dict[str, Any]:
        """Stripe to'lov qayta ishlash"""
        try:
            if not self.stripe_client:
                # Demo mode
                return {
                    "success": True,
                    "subscription_id": f"sub_demo_{uuid.uuid4().hex[:8]}",
                    "amount": amount,
                    "currency": currency
                }
            
            # Real Stripe implementation would go here
            # For now, return success for demo
            
            return {
                "success": True,
                "subscription_id": f"sub_{uuid.uuid4().hex[:8]}",
                "amount": amount,
                "currency": currency
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_paypal_payment(self,
                                    amount: float,
                                    currency: str,
                                    user_id: str,
                                    **kwargs) -> Dict[str, Any]:
        """PayPal to'lov qayta ishlash"""
        try:
            # PayPal implementation
            return {
                "success": True,
                "subscription_id": f"paypal_{uuid.uuid4().hex[:8]}",
                "amount": amount,
                "currency": currency
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_discount(self, code: str, amount: float, user_id: str) -> float:
        """Chegirma hisoblash"""
        if code not in self.discount_codes:
            return 0.0
        
        discount = self.discount_codes[code]
        return await self._calculate_discount_amount(code, amount)
    
    async def _calculate_discount_amount(self, code: str, amount: float) -> float:
        """Chegirma summasini hisoblash"""
        if code not in self.discount_codes:
            return 0.0
        
        discount = self.discount_codes[code]
        
        if discount.discount_type == DiscountType.PERCENTAGE:
            discount_amount = amount * (discount.value / 100)
        elif discount.discount_type == DiscountType.FIXED_AMOUNT:
            discount_amount = discount.value
        else:
            discount_amount = 0.0
        
        # Max discount cap
        if discount.max_discount:
            discount_amount = min(discount_amount, discount.max_discount)
        
        return min(discount_amount, amount)  # Cannot exceed original amount
    
    async def _calculate_usage_stats(self, user_id: str, plan_id: str) -> Dict[str, Any]:
        """Foydalanish statistikasi"""
        plan = self.pricing_plans[plan_id]
        
        return {
            "signals_used": 0,  # Would be calculated from actual usage
            "commodities_used": 0,
            "api_calls": 0,
            "support_tickets": 0,
            "limit_utilization": {
                "signals": 0,  # (used / max) * 100
                "commodities": 0,
                "api_calls": 0
            }
        }
    
    async def _update_analytics(self, event_type: str, amount: float = 0.0):
        """Analytics yangilash"""
        try:
            if event_type == "subscription_created":
                self.analytics["total_revenue"] += amount
            elif event_type == "subscription_renewed":
                self.analytics["monthly_recurring_revenue"] += amount
            elif event_type == "refund_processed":
                self.analytics["total_revenue"] += amount  # Negative amount
            
        except Exception as e:
            logger.error(f"Analytics yangilash xatosi: {e}")
    
    async def _cancel_external_subscription(self, subscription: Subscription):
        """External providerda obunani bekor qilish"""
        # Implementation for canceling with Stripe, PayPal, etc.
        pass
    
    async def _process_refund(self, external_subscription_id: str, amount: float, provider: PaymentProvider) -> Dict[str, Any]:
        """Refund qayta ishlash"""
        # Implementation for processing refunds
        return {"success": True, "refund_id": f"refund_{uuid.uuid4().hex[:8]}"}

# Demo va test
async def demo_subscription_manager():
    """Subscription manager demo"""
    print("=== Subscription Manager Demo ===\n")
    
    # Manager yaratish
    config = {
        "stripe_api_key": "demo_key",
        "paypal_client_id": "demo_client",
        "paypal_client_secret": "demo_secret"
    }
    manager = SubscriptionManager(config)
    
    # Pricing rejalar
    print("=== Pricing Rejalar ===")
    plans = await manager.get_pricing_plans()
    for plan in plans:
        print(f"- {plan['name']}: ${plan['price']}/{plan['plan_type']}")
        if plan['is_popular']:
            print("  ⭐ Ommabop reja")
    
    # Chegirma kodi tekshirish
    print("\n=== Chegirma Kodi Tekshirish ===")
    test_code = "WELCOME20"
    validation = await manager.validate_discount_code(test_code, "user123", 100.0)
    if validation["valid"]:
        print(f"Kod {test_code}: ${validation['discount_amount']} chegirma")
        print(f"Oxirgi summa: ${validation['final_amount']}")
    else:
        print(f"Kod xatosi: {validation['error']}")
    
    # Obuna yaratish demo
    print("\n=== Obuna Yaratish ===")
    try:
        # Eng mashhur reja
        premium_plan = next(p for p in plans if p['name'] == 'Premium Plan')
        
        subscription_id = await manager.create_subscription(
            user_id="user_123",
            plan_id=premium_plan['plan_id'],
            payment_provider=PaymentProvider.STRIPE,
            discount_code="WELCOME20"
        )
        print(f"Obuna yaratildi: {subscription_id}")
        
        # Obuna tafsilotlari
        details = await manager.get_subscription_details(subscription_id)
        if details:
            print(f"Reja: {details['plan']['name']}")
            print(f"Narx: ${details['amount']} {details['currency']}")
            print(f"Holat: {details['status']}")
            print(f"Muddati: {details['days_remaining']} kun")
        
    except Exception as e:
        print(f"Obuna xatosi: {e}")
    
    # Analytics
    print("\n=== Subscription Analytics ===")
    analytics = await manager.get_subscription_analytics()
    print(f"Jami obunalar: {analytics['total_subscriptions']}")
    print(f"Aktiv obunalar: {analytics['active_subscriptions']}")
    print(f"Proba obunalari: {analytics['trial_subscriptions']}")
    print(f"Jami daromad: ${analytics['total_revenue']:.2f}")
    print(f"Oylik daromad: ${analytics['monthly_recurring_revenue']:.2f}")
    print(f"ARPU: ${analytics['average_revenue_per_user']:.2f}")
    print(f"Churn rate: {analytics['churn_rate']:.2f}%")
    
    # Rejalar taqsimoti
    print("\nReja taqsimoti:")
    for plan_name, count in analytics['plan_distribution'].items():
        print(f"- {plan_name}: {count} ta obuna")
    
    print("\n=== Subscription Manager Demo Tugadi ===")

if __name__ == "__main__":
    asyncio.run(demo_subscription_manager())