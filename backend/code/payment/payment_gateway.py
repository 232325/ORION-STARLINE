"""
Payment Gateway - Stripe Integration
To'lov tizimi, subscription management, billing

Xususiyatlar:
- Stripe to'lov integratsiyasi
- Subscription planlar va billing
- Invoice yaratish va payment tracking
- Refund va chargeback management
- Payment method management
- Recurring payments va dunning
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class SubscriptionPlan(Enum):
    """Subscription plan turlari"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ULTIMATE = "ultimate"


class PaymentMethod(Enum):
    """To'lov usullari"""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class InvoiceStatus(Enum):
    """Invoice holatlari"""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class PaymentStatus(Enum):
    """To'lov holatlari"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


@dataclass
class PlanFeatures:
    """Plan xususiyatlari"""
    max_strategies: int
    max_api_calls: int
    advanced_analytics: bool
    priority_support: bool
    custom_integrations: bool
    backtesting_hours: int
    concurrent_trades: int
    data_retention_days: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_strategies": self.max_strategies,
            "max_api_calls": self.max_api_calls,
            "advanced_analytics": self.advanced_analytics,
            "priority_support": self.priority_support,
            "custom_integrations": self.custom_integrations,
            "backtesting_hours": self.backtesting_hours,
            "concurrent_trades": self.concurrent_trades,
            "data_retention_days": self.data_retention_days
        }


@dataclass
class Subscription:
    """Foydalanuvchi subscription"""
    id: str
    user_id: str
    plan: SubscriptionPlan
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    features: PlanFeatures
    amount: Decimal
    currency: str = "USD"
    stripe_subscription_id: Optional[str] = None
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    
    def is_active(self) -> bool:
        """Subscription aktiv ekanligini tekshirish"""
        return (
            self.status == "active" and
            datetime.now() < self.current_period_end
        )
    
    def days_remaining(self) -> int:
        """Qolgan kunlar soni"""
        if not self.is_active():
            return 0
        delta = self.current_period_end - datetime.now()
        return max(0, delta.days)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan": self.plan.value,
            "status": self.status,
            "current_period_start": self.current_period_start.isoformat(),
            "current_period_end": self.current_period_end.isoformat(),
            "cancel_at_period_end": self.cancel_at_period_end,
            "features": self.features.to_dict(),
            "amount": str(self.amount),
            "currency": self.currency,
            "days_remaining": self.days_remaining(),
            "stripe_subscription_id": self.stripe_subscription_id
        }


@dataclass
class Invoice:
    """To'lov invoice"""
    id: str
    user_id: str
    subscription_id: str
    amount: Decimal
    currency: str
    status: InvoiceStatus
    created_at: datetime
    due_date: datetime
    paid_at: Optional[datetime] = None
    items: List[Dict[str, Any]] = field(default_factory=list)
    stripe_invoice_id: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    
    def is_overdue(self) -> bool:
        """Invoice muddati o'tgan mi"""
        return (
            self.status == InvoiceStatus.OPEN and
            datetime.now() > self.due_date
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subscription_id": self.subscription_id,
            "amount": str(self.amount),
            "currency": self.currency,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "due_date": self.due_date.isoformat(),
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "items": self.items,
            "is_overdue": self.is_overdue(),
            "stripe_invoice_id": self.stripe_invoice_id,
            "payment_method": self.payment_method.value if self.payment_method else None
        }


@dataclass
class Payment:
    """To'lov tranzaksiyasi"""
    id: str
    user_id: str
    invoice_id: str
    amount: Decimal
    currency: str
    method: PaymentMethod
    status: PaymentStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    stripe_payment_id: Optional[str] = None
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "invoice_id": self.invoice_id,
            "amount": str(self.amount),
            "currency": self.currency,
            "method": self.method.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "stripe_payment_id": self.stripe_payment_id,
            "failure_reason": self.failure_reason,
            "metadata": self.metadata
        }


class PaymentGateway:
    """
    Payment Gateway - Stripe Integration
    
    To'lov tizimi, subscription management, billing va invoice yaratish
    """
    
    def __init__(self, stripe_api_key: Optional[str] = None):
        """
        Args:
            stripe_api_key: Stripe API key (production)
        """
        self.stripe_api_key = stripe_api_key
        self.subscriptions: Dict[str, Subscription] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.payments: Dict[str, Payment] = {}
        
        # Plan pricing va features
        self.plan_configs = {
            SubscriptionPlan.FREE: {
                "price": Decimal("0"),
                "features": PlanFeatures(
                    max_strategies=3,
                    max_api_calls=1000,
                    advanced_analytics=False,
                    priority_support=False,
                    custom_integrations=False,
                    backtesting_hours=10,
                    concurrent_trades=5,
                    data_retention_days=30
                ),
                "name": "Free Plan",
                "description": "Boshlang'ich plan - cheklangan xususiyatlar"
            },
            SubscriptionPlan.BASIC: {
                "price": Decimal("29.99"),
                "features": PlanFeatures(
                    max_strategies=10,
                    max_api_calls=10000,
                    advanced_analytics=True,
                    priority_support=False,
                    custom_integrations=False,
                    backtesting_hours=50,
                    concurrent_trades=20,
                    data_retention_days=90
                ),
                "name": "Basic Plan",
                "description": "Yangi boshlovchilar uchun"
            },
            SubscriptionPlan.PROFESSIONAL: {
                "price": Decimal("99.99"),
                "features": PlanFeatures(
                    max_strategies=50,
                    max_api_calls=100000,
                    advanced_analytics=True,
                    priority_support=True,
                    custom_integrations=True,
                    backtesting_hours=200,
                    concurrent_trades=100,
                    data_retention_days=365
                ),
                "name": "Professional Plan",
                "description": "Professional treyderlar uchun"
            },
            SubscriptionPlan.ENTERPRISE: {
                "price": Decimal("299.99"),
                "features": PlanFeatures(
                    max_strategies=200,
                    max_api_calls=1000000,
                    advanced_analytics=True,
                    priority_support=True,
                    custom_integrations=True,
                    backtesting_hours=1000,
                    concurrent_trades=500,
                    data_retention_days=730
                ),
                "name": "Enterprise Plan",
                "description": "Korporativ mijozlar uchun"
            },
            SubscriptionPlan.ULTIMATE: {
                "price": Decimal("999.99"),
                "features": PlanFeatures(
                    max_strategies=-1,  # Unlimited
                    max_api_calls=-1,   # Unlimited
                    advanced_analytics=True,
                    priority_support=True,
                    custom_integrations=True,
                    backtesting_hours=-1,  # Unlimited
                    concurrent_trades=-1,  # Unlimited
                    data_retention_days=-1  # Unlimited
                ),
                "name": "Ultimate Plan",
                "description": "Cheksiz xususiyatlar"
            }
        }
        
        logger.info("PaymentGateway initialized")
    
    async def create_subscription(
        self,
        user_id: str,
        plan: SubscriptionPlan,
        payment_method: Optional[PaymentMethod] = None,
        trial_days: int = 0
    ) -> Subscription:
        """
        Yangi subscription yaratish
        
        Args:
            user_id: Foydalanuvchi ID
            plan: Subscription plan
            payment_method: To'lov usuli
            trial_days: Sinov davri (kunlar)
        
        Returns:
            Yaratilgan subscription
        """
        import uuid
        
        config = self.plan_configs[plan]
        
        now = datetime.now()
        trial_end = now + timedelta(days=trial_days) if trial_days > 0 else None
        period_start = trial_end if trial_end else now
        period_end = period_start + timedelta(days=30)  # Monthly billing
        
        subscription = Subscription(
            id=f"sub_{uuid.uuid4().hex[:16]}",
            user_id=user_id,
            plan=plan,
            status="active" if plan == SubscriptionPlan.FREE else "trialing" if trial_days > 0 else "active",
            current_period_start=period_start,
            current_period_end=period_end,
            cancel_at_period_end=False,
            features=config["features"],
            amount=config["price"],
            trial_end=trial_end
        )
        
        self.subscriptions[subscription.id] = subscription
        
        # FREE plan uchun invoice yaratilmaydi
        if plan != SubscriptionPlan.FREE:
            # Birinchi invoice yaratish
            await self._create_invoice(subscription)
        
        logger.info(f"Subscription created: {subscription.id} for user {user_id} - Plan: {plan.value}")
        
        return subscription
    
    async def _create_invoice(self, subscription: Subscription) -> Invoice:
        """
        Subscription uchun invoice yaratish
        
        Args:
            subscription: Subscription obyekti
        
        Returns:
            Yaratilgan invoice
        """
        import uuid
        
        now = datetime.now()
        
        invoice = Invoice(
            id=f"inv_{uuid.uuid4().hex[:16]}",
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            amount=subscription.amount,
            currency=subscription.currency,
            status=InvoiceStatus.OPEN if subscription.amount > 0 else InvoiceStatus.PAID,
            created_at=now,
            due_date=now + timedelta(days=7),
            items=[
                {
                    "description": f"{subscription.plan.value.title()} Plan - Monthly Subscription",
                    "amount": str(subscription.amount),
                    "quantity": 1
                }
            ]
        )
        
        self.invoices[invoice.id] = invoice
        
        logger.info(f"Invoice created: {invoice.id} for subscription {subscription.id}")
        
        return invoice
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Subscription:
        """
        Subscription bekor qilish
        
        Args:
            subscription_id: Subscription ID
            immediately: Darhol bekor qilish yoki davr oxirida
        
        Returns:
            Yangilangan subscription
        """
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription not found: {subscription_id}")
        
        subscription = self.subscriptions[subscription_id]
        
        if immediately:
            subscription.status = "canceled"
            subscription.canceled_at = datetime.now()
        else:
            subscription.cancel_at_period_end = True
        
        logger.info(f"Subscription canceled: {subscription_id} - Immediately: {immediately}")
        
        return subscription
    
    async def process_payment(
        self,
        invoice_id: str,
        payment_method: PaymentMethod,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Payment:
        """
        To'lovni qayta ishlash
        
        Args:
            invoice_id: Invoice ID
            payment_method: To'lov usuli
            metadata: Qo'shimcha ma'lumotlar
        
        Returns:
            Payment obyekti
        """
        import uuid
        
        if invoice_id not in self.invoices:
            raise ValueError(f"Invoice not found: {invoice_id}")
        
        invoice = self.invoices[invoice_id]
        
        # Payment yaratish
        payment = Payment(
            id=f"pay_{uuid.uuid4().hex[:16]}",
            user_id=invoice.user_id,
            invoice_id=invoice_id,
            amount=invoice.amount,
            currency=invoice.currency,
            method=payment_method,
            status=PaymentStatus.PROCESSING,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.payments[payment.id] = payment
        
        # Simulate payment processing
        try:
            # Bu yerda haqiqiy Stripe API call bo'ladi
            # stripe.PaymentIntent.create(...)
            
            # Success scenario
            payment.status = PaymentStatus.SUCCEEDED
            payment.completed_at = datetime.now()
            
            # Invoice ni to'langan deb belgilash
            invoice.status = InvoiceStatus.PAID
            invoice.paid_at = datetime.now()
            invoice.payment_method = payment_method
            
            logger.info(f"Payment processed successfully: {payment.id}")
            
        except Exception as e:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = str(e)
            logger.error(f"Payment failed: {payment.id} - {e}")
        
        return payment
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        To'lovni qaytarish (refund)
        
        Args:
            payment_id: Payment ID
            amount: Qaytariladigan summa (None = full refund)
            reason: Qaytarish sababi
        
        Returns:
            Refund ma'lumotlari
        """
        if payment_id not in self.payments:
            raise ValueError(f"Payment not found: {payment_id}")
        
        payment = self.payments[payment_id]
        
        if payment.status != PaymentStatus.SUCCEEDED:
            raise ValueError(f"Can only refund succeeded payments")
        
        refund_amount = amount if amount else payment.amount
        
        if refund_amount > payment.amount:
            raise ValueError(f"Refund amount exceeds payment amount")
        
        # Simulate refund processing
        payment.status = PaymentStatus.REFUNDED
        
        refund_data = {
            "refund_id": f"ref_{payment_id[:16]}",
            "payment_id": payment_id,
            "amount": str(refund_amount),
            "currency": payment.currency,
            "reason": reason,
            "status": "succeeded",
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Payment refunded: {payment_id} - Amount: {refund_amount}")
        
        return refund_data
    
    async def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Subscription ma'lumotlarini olish"""
        return self.subscriptions.get(subscription_id)
    
    async def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """Foydalanuvchi subscription-larini olish"""
        return [
            sub for sub in self.subscriptions.values()
            if sub.user_id == user_id
        ]
    
    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Invoice ma'lumotlarini olish"""
        return self.invoices.get(invoice_id)
    
    async def get_user_invoices(
        self,
        user_id: str,
        status: Optional[InvoiceStatus] = None
    ) -> List[Invoice]:
        """Foydalanuvchi invoice-larini olish"""
        invoices = [
            inv for inv in self.invoices.values()
            if inv.user_id == user_id
        ]
        
        if status:
            invoices = [inv for inv in invoices if inv.status == status]
        
        # Sort by created_at descending
        invoices.sort(key=lambda x: x.created_at, reverse=True)
        
        return invoices
    
    async def get_payment(self, payment_id: str) -> Optional[Payment]:
        """Payment ma'lumotlarini olish"""
        return self.payments.get(payment_id)
    
    async def get_user_payments(
        self,
        user_id: str,
        status: Optional[PaymentStatus] = None
    ) -> List[Payment]:
        """Foydalanuvchi to'lovlarini olish"""
        payments = [
            pay for pay in self.payments.values()
            if pay.user_id == user_id
        ]
        
        if status:
            payments = [pay for pay in payments if pay.status == status]
        
        # Sort by created_at descending
        payments.sort(key=lambda x: x.created_at, reverse=True)
        
        return payments
    
    async def upgrade_subscription(
        self,
        subscription_id: str,
        new_plan: SubscriptionPlan
    ) -> Subscription:
        """
        Subscription-ni yangilash (upgrade/downgrade)
        
        Args:
            subscription_id: Subscription ID
            new_plan: Yangi plan
        
        Returns:
            Yangilangan subscription
        """
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription not found: {subscription_id}")
        
        subscription = self.subscriptions[subscription_id]
        old_plan = subscription.plan
        
        # Plan config olish
        new_config = self.plan_configs[new_plan]
        
        # Update subscription
        subscription.plan = new_plan
        subscription.features = new_config["features"]
        subscription.amount = new_config["price"]
        
        # Agar upgrade bo'lsa, prorated invoice yaratish
        if new_config["price"] > self.plan_configs[old_plan]["price"]:
            await self._create_prorated_invoice(subscription, old_plan)
        
        logger.info(f"Subscription upgraded: {subscription_id} - {old_plan.value} -> {new_plan.value}")
        
        return subscription
    
    async def _create_prorated_invoice(
        self,
        subscription: Subscription,
        old_plan: SubscriptionPlan
    ) -> Invoice:
        """Prorated invoice yaratish (upgrade uchun)"""
        import uuid
        
        old_price = self.plan_configs[old_plan]["price"]
        new_price = subscription.amount
        
        # Qolgan kunlar uchun hisoblash
        days_remaining = subscription.days_remaining()
        days_total = 30
        
        prorated_amount = (new_price - old_price) * Decimal(days_remaining) / Decimal(days_total)
        
        invoice = Invoice(
            id=f"inv_{uuid.uuid4().hex[:16]}",
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            amount=prorated_amount,
            currency=subscription.currency,
            status=InvoiceStatus.OPEN,
            created_at=datetime.now(),
            due_date=datetime.now() + timedelta(days=1),  # Immediate payment
            items=[
                {
                    "description": f"Plan Upgrade: {old_plan.value} -> {subscription.plan.value} (Prorated)",
                    "amount": str(prorated_amount),
                    "quantity": 1,
                    "days_remaining": days_remaining
                }
            ]
        )
        
        self.invoices[invoice.id] = invoice
        
        return invoice
    
    async def get_plan_features(self, plan: SubscriptionPlan) -> Dict[str, Any]:
        """Plan xususiyatlarini olish"""
        config = self.plan_configs[plan]
        return {
            "plan": plan.value,
            "name": config["name"],
            "description": config["description"],
            "price": str(config["price"]),
            "currency": "USD",
            "billing_period": "monthly",
            "features": config["features"].to_dict()
        }
    
    async def get_all_plans(self) -> List[Dict[str, Any]]:
        """Barcha mavjud planlarni olish"""
        return [
            await self.get_plan_features(plan)
            for plan in SubscriptionPlan
        ]
    
    async def get_billing_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Foydalanuvchi billing tarixini olish
        
        Returns:
            Billing history with invoices va payments
        """
        invoices = await self.get_user_invoices(user_id)
        payments = await self.get_user_payments(user_id)
        
        return {
            "user_id": user_id,
            "invoices": [inv.to_dict() for inv in invoices[:limit]],
            "payments": [pay.to_dict() for pay in payments[:limit]],
            "total_invoices": len(invoices),
            "total_payments": len(payments),
            "total_paid": sum(
                pay.amount for pay in payments
                if pay.status == PaymentStatus.SUCCEEDED
            ),
            "outstanding_balance": sum(
                inv.amount for inv in invoices
                if inv.status == InvoiceStatus.OPEN
            )
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gateway statistikasini olish"""
        total_revenue = sum(
            pay.amount for pay in self.payments.values()
            if pay.status == PaymentStatus.SUCCEEDED
        )
        
        active_subscriptions = sum(
            1 for sub in self.subscriptions.values()
            if sub.is_active()
        )
        
        # Plan distribution
        plan_dist = {}
        for sub in self.subscriptions.values():
            if sub.is_active():
                plan_dist[sub.plan.value] = plan_dist.get(sub.plan.value, 0) + 1
        
        return {
            "total_subscriptions": len(self.subscriptions),
            "active_subscriptions": active_subscriptions,
            "total_invoices": len(self.invoices),
            "total_payments": len(self.payments),
            "total_revenue": str(total_revenue),
            "successful_payments": sum(
                1 for pay in self.payments.values()
                if pay.status == PaymentStatus.SUCCEEDED
            ),
            "failed_payments": sum(
                1 for pay in self.payments.values()
                if pay.status == PaymentStatus.FAILED
            ),
            "plan_distribution": plan_dist,
            "overdue_invoices": sum(
                1 for inv in self.invoices.values()
                if inv.is_overdue()
            )
        }
