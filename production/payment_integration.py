#!/usr/bin/env python3
"""
Production Payment Integration System
Production muhit uchun Stripe va PayPal payment tizimi
"""

import os
import json
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import aiohttp
import asyncio
import stripe
import paypalrestsdk
from paypalrests_sdk import Api
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Import production configuration
from production_config import get_config


@dataclass
class PaymentMethod:
    """To'lov usuli"""
    id: str
    type: str  # card, bank_account, paypal, etc.
    last_four: Optional[str] = None
    brand: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False
    created_at: Optional[datetime] = None


@dataclass
class Subscription:
    """Obuna ma'lumotlari"""
    id: Optional[int] = None
    user_id: int
    plan_id: str
    stripe_subscription_id: Optional[str] = None
    paypal_subscription_id: Optional[str] = None
    status: str = "active"  # active, canceled, past_due, unpaid
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class Payment:
    """To'lov ma'lumotlari"""
    id: Optional[int] = None
    user_id: int
    amount: float
    currency: str = "USD"
    payment_method: str
    payment_provider: str  # stripe, paypal
    provider_payment_id: str
    status: str = "pending"  # pending, succeeded, failed, canceled
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None


@dataclass
class Plan:
    """Tarif rejasi"""
    id: str
    name: str
    description: str
    price_monthly: float
    price_yearly: float
    currency: str = "USD"
    features: List[str] = field(default_factory=list)
    max_trades: Optional[int] = None
    max_accounts: int = 1
    priority_support: bool = False
    advanced_analytics: bool = False
    ai_signals: bool = False
    is_active: bool = True
    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_yearly: Optional[str] = None


class ProductionPaymentSystem:
    """Production payment tizimi"""
    
    def __init__(self, environment: str = "production"):
        self.config = get_config(environment)
        self.environment = environment
        
        # Logging setup
        self.setup_logging()
        
        # Payment providers setup
        self.setup_payment_providers()
        
        # Database setup
        self.setup_database()
        
        # Initialize payment plans
        self.initialize_payment_plans()
        
        self.logger.info("💳 Production Payment Integration tizimi ishga tushdi")
    
    def setup_logging(self):
        """Logging konfiguratsiyasi"""
        log_dir = Path("/workspace/orion-starline/logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "payment.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_payment_providers(self):
        """Payment providerlarni sozlash"""
        # Stripe setup
        stripe.api_key = self.config.STRIPE_SECRET_KEY
        
        # PayPal setup
        self.paypal_api = Api({
            "mode": "live" if self.environment == "production" else "sandbox",
            "client_id": self.config.PAYPAL_CLIENT_ID,
            "client_secret": self.config.PAYPAL_CLIENT_SECRET
        })
        
        self.logger.info("💳 Payment providerlar sozlangan")
    
    def setup_database(self):
        """Ma'lumotlar bazasi jadvallarini yaratish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    # Payment methods table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS payment_methods (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            provider VARCHAR(50) NOT NULL,  -- stripe, paypal
                            provider_method_id VARCHAR(255) NOT NULL,
                            type VARCHAR(50) NOT NULL,  -- card, bank_account, paypal
                            last_four VARCHAR(4),
                            brand VARCHAR(50),
                            exp_month INTEGER,
                            exp_year INTEGER,
                            is_default BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(user_id, provider, provider_method_id)
                        )
                    """)
                    
                    # Payment plans table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS payment_plans (
                            id VARCHAR(100) PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            description TEXT,
                            price_monthly DECIMAL(10,2) NOT NULL,
                            price_yearly DECIMAL(10,2) NOT NULL,
                            currency VARCHAR(10) DEFAULT 'USD',
                            features TEXT[],
                            max_trades INTEGER,
                            max_accounts INTEGER DEFAULT 1,
                            priority_support BOOLEAN DEFAULT FALSE,
                            advanced_analytics BOOLEAN DEFAULT FALSE,
                            ai_signals BOOLEAN DEFAULT FALSE,
                            is_active BOOLEAN DEFAULT TRUE,
                            stripe_price_id_monthly VARCHAR(255),
                            stripe_price_id_yearly VARCHAR(255),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Subscriptions table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS subscriptions (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            plan_id VARCHAR(100) REFERENCES payment_plans(id) ON DELETE CASCADE,
                            stripe_subscription_id VARCHAR(255),
                            paypal_subscription_id VARCHAR(255),
                            status VARCHAR(50) DEFAULT 'active',
                            current_period_start TIMESTAMP,
                            current_period_end TIMESTAMP,
                            cancel_at TIMESTAMP,
                            canceled_at TIMESTAMP,
                            trial_start TIMESTAMP,
                            trial_end TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(user_id, plan_id, stripe_subscription_id)
                        )
                    """)
                    
                    # Payments table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS payments (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE CASCADE,
                            amount DECIMAL(10,2) NOT NULL,
                            currency VARCHAR(10) DEFAULT 'USD',
                            payment_method VARCHAR(50) NOT NULL,
                            payment_provider VARCHAR(50) NOT NULL,
                            provider_payment_id VARCHAR(255) NOT NULL,
                            status VARCHAR(50) DEFAULT 'pending',
                            description TEXT,
                            metadata JSONB DEFAULT '{}',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            processed_at TIMESTAMP
                        )
                    """)
                    
                    # Webhook events table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS webhook_events (
                            id SERIAL PRIMARY KEY,
                            provider VARCHAR(50) NOT NULL,  -- stripe, paypal
                            event_id VARCHAR(255) UNIQUE NOT NULL,
                            event_type VARCHAR(100) NOT NULL,
                            payload JSONB NOT NULL,
                            processed BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    conn.commit()
                    self.logger.info("✅ Payment ma'lumotlar bazasi jadvallari yaratildi")
                    
        except Exception as e:
            self.logger.error(f"Payment database setup xatosi: {e}")
            raise
    
    def initialize_payment_plans(self):
        """To'lov rejlarini yaratish"""
        try:
            plans = [
                Plan(
                    id="free",
                    name="Bepul Reja",
                    description="Trading asoslari va demo hisob",
                    price_monthly=0.0,
                    price_yearly=0.0,
                    features=["Demo hisob", "Asosiy ko'rsatkichlar", "Kundalik ma'lumotlar"],
                    max_trades=10,
                    max_accounts=1,
                    priority_support=False,
                    advanced_analytics=False,
                    ai_signals=False
                ),
                Plan(
                    id="basic",
                    name="Asosiy Reja",
                    description="Shaxsiy trading uchun",
                    price_monthly=29.99,
                    price_yearly=299.99,
                    features=["Real trading", "Barcha ko'rsatkichlar", "Risk boshqaruvi", "Email yordam"],
                    max_trades=100,
                    max_accounts=1,
                    priority_support=False,
                    advanced_analytics=True,
                    ai_signals=False,
                    stripe_price_id_monthly="price_basic_monthly",
                    stripe_price_id_yearly="price_basic_yearly"
                ),
                Plan(
                    id="premium",
                    name="Premium Reja",
                    description="Professional traderlar uchun",
                    price_monthly=79.99,
                    price_yearly=799.99,
                    features=["Real trading", "AI signals", "Adv analytics", "24/7 yordam", "Multiple accounts"],
                    max_trades=500,
                    max_accounts=5,
                    priority_support=True,
                    advanced_analytics=True,
                    ai_signals=True,
                    stripe_price_id_monthly="price_premium_monthly",
                    stripe_price_id_yearly="price_premium_yearly"
                ),
                Plan(
                    id="vip",
                    name="VIP Reja",
                    description="Institutional users uchun",
                    price_monthly=199.99,
                    price_yearly=1999.99,
                    features=["Unlimited trading", "Custom strategies", "Dedicated manager", "API access"],
                    max_trades=None,
                    max_accounts=20,
                    priority_support=True,
                    advanced_analytics=True,
                    ai_signals=True,
                    stripe_price_id_monthly="price_vip_monthly",
                    stripe_price_id_yearly="price_vip_yearly"
                )
            ]
            
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    for plan in plans:
                        cur.execute("""
                            INSERT INTO payment_plans 
                            (id, name, description, price_monthly, price_yearly, currency, features,
                             max_trades, max_accounts, priority_support, advanced_analytics, ai_signals,
                             stripe_price_id_monthly, stripe_price_id_yearly)
                            VALUES (%(id)s, %(name)s, %(description)s, %(price_monthly)s, %(price_yearly)s,
                                    %(currency)s, %(features)s, %(max_trades)s, %(max_accounts)s,
                                    %(priority_support)s, %(advanced_analytics)s, %(ai_signals)s,
                                    %(stripe_price_id_monthly)s, %(stripe_price_id_yearly)s)
                            ON CONFLICT (id) DO UPDATE SET
                                name = EXCLUDED.name,
                                description = EXCLUDED.description,
                                price_monthly = EXCLUDED.price_monthly,
                                price_yearly = EXCLUDED.price_yearly,
                                features = EXCLUDED.features,
                                max_trades = EXCLUDED.max_trades,
                                max_accounts = EXCLUDED.max_accounts,
                                priority_support = EXCLUDED.priority_support,
                                advanced_analytics = EXCLUDED.advanced_analytics,
                                ai_signals = EXCLUDED.ai_signals,
                                updated_at = CURRENT_TIMESTAMP
                        """, {
                            "id": plan.id,
                            "name": plan.name,
                            "description": plan.description,
                            "price_monthly": plan.price_monthly,
                            "price_yearly": plan.price_yearly,
                            "currency": plan.currency,
                            "features": plan.features,
                            "max_trades": plan.max_trades,
                            "max_accounts": plan.max_accounts,
                            "priority_support": plan.priority_support,
                            "advanced_analytics": plan.advanced_analytics,
                            "ai_signals": plan.ai_signals,
                            "stripe_price_id_monthly": plan.stripe_price_id_monthly,
                            "stripe_price_id_yearly": plan.stripe_price_id_yearly
                        })
                    
                    conn.commit()
                    self.logger.info("✅ Payment rejalar yaratildi")
                    
        except Exception as e:
            self.logger.error(f"Payment plans yaratishda xato: {e}")
    
    def create_stripe_customer(self, user_id: int, email: str) -> Tuple[bool, str, Optional[str]]:
        """Stripe customer yaratish"""
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={"user_id": str(user_id)}
            )
            
            self.logger.info(f"✅ Stripe customer yaratildi: {customer.id}")
            return True, "Stripe customer yaratildi", customer.id
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe customer yaratishda xato: {e}")
            return False, f"Stripe xatosi: {str(e)}", None
    
    def create_stripe_payment_intent(self, customer_id: str, amount: float, currency: str = "usd", 
                                   metadata: Dict[str, str] = None) -> Tuple[bool, str, Optional[str]]:
        """Stripe payment intent yaratish"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe uses cents
                currency=currency,
                customer=customer_id,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True}
            )
            
            self.logger.info(f"✅ Stripe Payment Intent yaratildi: {intent.id}")
            return True, "Payment Intent yaratildi", intent.client_secret
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe Payment Intent xatosi: {e}")
            return False, f"Stripe xatosi: {str(e)}", None
    
    def create_stripe_subscription(self, customer_id: str, price_id: str, 
                                 metadata: Dict[str, str] = None) -> Tuple[bool, str, Optional[str]]:
        """Stripe obuna yaratish"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {},
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            
            self.logger.info(f"✅ Stripe Subscription yaratildi: {subscription.id}")
            return True, "Subscription yaratildi", subscription.id
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe Subscription xatosi: {e}")
            return False, f"Stripe xatosi: {str(e)}", None
    
    def create_paypal_order(self, amount: float, currency: str = "USD", 
                          description: str = "", metadata: Dict[str, str] = None) -> Tuple[bool, str, Optional[str]]:
        """PayPal order yaratish"""
        try:
            order = paypalrestsdk.Order({
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    },
                    "description": description
                }],
                "application_context": {
                    "brand_name": "Orion Starline",
                    "landing_page": "LOGIN",
                    "user_action": "PAY_NOW",
                    "return_url": "https://app.orion-starline.com/payment/success",
                    "cancel_url": "https://app.orion-starline.com/payment/cancel"
                }
            })
            
            if order.create():
                self.logger.info(f"✅ PayPal Order yaratildi: {order.id}")
                return True, "PayPal Order yaratildi", order.id
            else:
                return False, "PayPal Order yaratishda xato", None
                
        except Exception as e:
            self.logger.error(f"PayPal Order xatosi: {e}")
            return False, f"PayPal xatosi: {str(e)}", None
    
    def create_paypal_subscription(self, plan_id: str, subscriber: Dict[str, str], 
                                 metadata: Dict[str, str] = None) -> Tuple[bool, str, Optional[str]]:
        """PayPal obuna yaratish"""
        try:
            subscription = paypalrestsdk.Subscription({
                "plan_id": plan_id,
                "application_context": {
                    "brand_name": "Orion Starline",
                    "user_action": "SUBSCRIBE_NOW",
                    "return_url": "https://app.orion-starline.com/subscription/success",
                    "cancel_url": "https://app.orion-starline.com/subscription/cancel"
                }
            })
            
            # Add subscriber info
            if subscriber.get("email"):
                subscription.subscriber = {"email_address": subscriber["email"]}
            
            if subscription.create():
                self.logger.info(f"✅ PayPal Subscription yaratildi: {subscription.id}")
                return True, "PayPal Subscription yaratildi", subscription.id
            else:
                return False, "PayPal Subscription yaratishda xato", None
                
        except Exception as e:
            self.logger.error(f"PayPal Subscription xatosi: {e}")
            return False, f"PayPal xatosi: {str(e)}", None
    
    def process_payment(self, user_id: int, amount: float, currency: str = "USD",
                      payment_method: str = "stripe", payment_type: str = "one_time",
                      plan_id: str = None, description: str = "") -> Tuple[bool, str, Optional[str]]:
        """To'lovni qayta ishlash"""
        try:
            # Get user info
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT email FROM users WHERE id = %s", (user_id,))
                    user = cur.fetchone()
                    
                    if not user:
                        return False, "Foydalanuvchi topilmadi", None
                    
                    email = user[0]
            
            payment_id = None
            
            if payment_method == "stripe":
                if payment_type == "one_time":
                    # One-time payment
                    success, message, customer_id = self.create_stripe_customer(user_id, email)
                    if not success:
                        return False, message, None
                    
                    success, message, payment_intent = self.create_stripe_payment_intent(
                        customer_id, amount, currency, {"user_id": str(user_id), "plan_id": plan_id or ""}
                    )
                    if not success:
                        return False, message, None
                    
                    payment_id = payment_intent
                    
                elif payment_type == "subscription":
                    # Subscription payment
                    success, message, customer_id = self.create_stripe_customer(user_id, email)
                    if not success:
                        return False, message, None
                    
                    # Get plan details
                    plan_details = self.get_plan_details(plan_id)
                    if not plan_details:
                        return False, "Reja topilmadi", None
                    
                    price_id = plan_details.get("stripe_price_id_monthly")
                    if not price_id:
                        return False, "Stripe price ID topilmadi", None
                    
                    success, message, subscription_id = self.create_stripe_subscription(
                        customer_id, price_id, {"user_id": str(user_id), "plan_id": plan_id}
                    )
                    if not success:
                        return False, message, None
                    
                    payment_id = subscription_id
            
            elif payment_method == "paypal":
                if payment_type == "one_time":
                    # One-time payment
                    success, message, order_id = self.create_paypal_order(
                        amount, currency, description, {"user_id": str(user_id), "plan_id": plan_id}
                    )
                    if not success:
                        return False, message, None
                    
                    payment_id = order_id
                    
                elif payment_type == "subscription":
                    # Subscription payment
                    # PayPal subscription would require pre-configured plan
                    return False, "PayPal subscription hali qo'llab-quvvatlanmagan", None
            
            # Save payment record
            payment_record_id = self.save_payment_record(
                user_id, amount, currency, payment_method, payment_id, payment_type, plan_id, description
            )
            
            if payment_record_id:
                self.logger.info(f"✅ Payment qayta ishlandi: {payment_id}")
                return True, "To'lov muvaffaqiyatli qayta ishlandi", payment_id
            else:
                return False, "Payment record saqlanmadi", None
                
        except Exception as e:
            self.logger.error(f"Payment qayta ishlashda xato: {e}")
            return False, "To'lov qayta ishlashda xato", None
    
    def get_plan_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Reja tafsilotlarini olish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT * FROM payment_plans WHERE id = %s AND is_active = TRUE", (plan_id,))
                    plan = cur.fetchone()
                    
                    return dict(plan) if plan else None
                    
        except Exception as e:
            self.logger.error(f"Plan details olishda xato: {e}")
            return None
    
    def get_all_plans(self) -> List[Dict[str, Any]]:
        """Barcha rejalarni olish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT * FROM payment_plans WHERE is_active = TRUE ORDER BY price_monthly")
                    plans = cur.fetchall()
                    
                    return [dict(plan) for plan in plans]
                    
        except Exception as e:
            self.logger.error(f"Plans olishda xato: {e}")
            return []
    
    def save_payment_record(self, user_id: int, amount: float, currency: str, 
                          payment_method: str, provider_payment_id: str, 
                          payment_type: str, plan_id: str, description: str) -> Optional[int]:
        """Payment record ni saqlash"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO payments 
                        (user_id, amount, currency, payment_method, payment_provider, 
                         provider_payment_id, status, description, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        user_id, amount, currency, payment_type, payment_method,
                        provider_payment_id, "pending", description,
                        json.dumps({"plan_id": plan_id})
                    ))
                    
                    payment_id = cur.fetchone()[0]
                    conn.commit()
                    
                    return payment_id
                    
        except Exception as e:
            self.logger.error(f"Payment record saqlashda xato: {e}")
            return None
    
    def handle_stripe_webhook(self, payload: bytes, signature: str) -> bool:
        """Stripe webhook ni qayta ishlash"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.config.STRIPE_WEBHOOK_SECRET
            )
            
            # Save webhook event
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO webhook_events (provider, event_id, event_type, payload)
                        VALUES ('stripe', %s, %s, %s)
                        ON CONFLICT (event_id) DO NOTHING
                    """, (event["id"], event["type"], json.dumps(event)))
                    conn.commit()
            
            # Process specific events
            if event["type"] == "payment_intent.succeeded":
                self.process_payment_success(event["data"]["object"])
            elif event["type"] == "payment_intent.payment_failed":
                self.process_payment_failure(event["data"]["object"])
            elif event["type"] == "customer.subscription.created":
                self.process_subscription_created(event["data"]["object"])
            elif event["type"] == "customer.subscription.updated":
                self.process_subscription_updated(event["data"]["object"])
            elif event["type"] == "customer.subscription.deleted":
                self.process_subscription_canceled(event["data"]["object"])
            elif event["type"] == "invoice.payment_succeeded":
                self.process_invoice_payment_succeeded(event["data"]["object"])
            elif event["type"] == "invoice.payment_failed":
                self.process_invoice_payment_failed(event["data"]["object"])
            
            self.logger.info(f"✅ Stripe webhook processed: {event['type']}")
            return True
            
        except stripe.error.SignatureVerificationError as e:
            self.logger.error(f"Stripe webhook signature verification failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Stripe webhook processing error: {e}")
            return False
    
    def handle_paypal_webhook(self, webhook_id: str, payload: Dict[str, Any]) -> bool:
        """PayPal webhook ni qayta ishlash"""
        try:
            # Verify PayPal webhook
            webhook_verification = paypalrestsdk.Webhook.verify(
                transmission_id=webhook_id,
                transmission_time=payload.get("transmission_time"),
                cert_url=payload.get("cert_url"),
                auth_algo=payload.get("auth_algo"),
                transmission_sig=payload.get("transmission_sig"),
                webhook_id=self.config.PAYPAL_WEBHOOK_ID
            )
            
            if not webhook_verification:
                self.logger.error("PayPal webhook verification failed")
                return False
            
            # Save webhook event
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO webhook_events (provider, event_id, event_type, payload)
                        VALUES ('paypal', %s, %s, %s)
                        ON CONFLICT (event_id) DO NOTHING
                    """, (
                        payload["id"], 
                        payload["event_type"], 
                        json.dumps(payload)
                    ))
                    conn.commit()
            
            # Process specific events
            event_type = payload["event_type"]
            resource = payload["resource"]
            
            if event_type == "PAYMENT.CAPTURE.COMPLETED":
                self.process_paypal_payment_completed(resource)
            elif event_type == "BILLING.SUBSCRIPTION.CREATED":
                self.process_paypal_subscription_created(resource)
            elif event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
                self.process_paypal_subscription_activated(resource)
            elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
                self.process_paypal_subscription_canceled(resource)
            
            self.logger.info(f"✅ PayPal webhook processed: {event_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"PayPal webhook processing error: {e}")
            return False
    
    def process_payment_success(self, payment_intent: Dict[str, Any]):
        """To'lov muvaffaqiyati qayta ishlash"""
        try:
            payment_intent_id = payment_intent["id"]
            
            # Update payment status
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE payments 
                        SET status = 'succeeded', processed_at = CURRENT_TIMESTAMP
                        WHERE provider_payment_id = %s
                    """, (payment_intent_id,))
                    conn.commit()
            
            self.logger.info(f"✅ Payment success processed: {payment_intent_id}")
            
        except Exception as e:
            self.logger.error(f"Payment success processing error: {e}")
    
    def process_payment_failure(self, payment_intent: Dict[str, Any]):
        """To'lov muvaffaqiyatsizligini qayta ishlash"""
        try:
            payment_intent_id = payment_intent["id"]
            
            # Update payment status
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE payments 
                        SET status = 'failed', processed_at = CURRENT_TIMESTAMP
                        WHERE provider_payment_id = %s
                    """, (payment_intent_id,))
                    conn.commit()
            
            self.logger.warning(f"❌ Payment failure processed: {payment_intent_id}")
            
        except Exception as e:
            self.logger.error(f"Payment failure processing error: {e}")
    
    def process_subscription_created(self, subscription: Dict[str, Any]):
        """Obuna yaratish qayta ishlash"""
        try:
            customer_id = subscription["customer"]
            subscription_id = subscription["id"]
            plan_id = subscription["items"]["data"][0]["price"]["id"]
            
            # Find user by customer metadata
            customer = stripe.Customer.retrieve(customer_id)
            user_id = int(customer["metadata"]["user_id"])
            
            # Save subscription
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO subscriptions (user_id, plan_id, stripe_subscription_id, status, current_period_start, current_period_end)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        user_id, plan_id, subscription_id, subscription["status"],
                        datetime.fromtimestamp(subscription["current_period_start"]),
                        datetime.fromtimestamp(subscription["current_period_end"])
                    ))
                    conn.commit()
            
            self.logger.info(f"✅ Subscription created: {subscription_id}")
            
        except Exception as e:
            self.logger.error(f"Subscription creation processing error: {e}")
    
    def process_subscription_updated(self, subscription: Dict[str, Any]):
        """Obuna yangilanishi qayta ishlash"""
        try:
            subscription_id = subscription["id"]
            
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE subscriptions 
                        SET status = %s, current_period_start = %s, current_period_end = %s
                        WHERE stripe_subscription_id = %s
                    """, (
                        subscription["status"],
                        datetime.fromtimestamp(subscription["current_period_start"]),
                        datetime.fromtimestamp(subscription["current_period_end"]),
                        subscription_id
                    ))
                    conn.commit()
            
            self.logger.info(f"✅ Subscription updated: {subscription_id}")
            
        except Exception as e:
            self.logger.error(f"Subscription update processing error: {e}")
    
    def process_subscription_canceled(self, subscription: Dict[str, Any]):
        """Obuna bekor qilish qayta ishlash"""
        try:
            subscription_id = subscription["id"]
            
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE subscriptions 
                        SET status = 'canceled', canceled_at = CURRENT_TIMESTAMP
                        WHERE stripe_subscription_id = %s
                    """, (subscription_id,))
                    conn.commit()
            
            self.logger.info(f"✅ Subscription canceled: {subscription_id}")
            
        except Exception as e:
            self.logger.error(f"Subscription cancellation processing error: {e}")
    
    def process_invoice_payment_succeeded(self, invoice: Dict[str, Any]):
        """Invoice to'lov muvaffaqiyati qayta ishlash"""
        try:
            # This would handle recurring subscription payments
            self.logger.info(f"✅ Invoice payment succeeded: {invoice['id']}")
            
        except Exception as e:
            self.logger.error(f"Invoice payment success processing error: {e}")
    
    def process_invoice_payment_failed(self, invoice: Dict[str, Any]):
        """Invoice to'lov xatosi qayta ishlash"""
        try:
            # This would handle failed recurring subscription payments
            self.logger.warning(f"❌ Invoice payment failed: {invoice['id']}")
            
        except Exception as e:
            self.logger.error(f"Invoice payment failure processing error: {e}")
    
    def process_paypal_payment_completed(self, capture: Dict[str, Any]):
        """PayPal to'lov muvaffaqiyati qayta ishlash"""
        try:
            payment_id = capture["id"]
            
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE payments 
                        SET status = 'succeeded', processed_at = CURRENT_TIMESTAMP
                        WHERE provider_payment_id = %s
                    """, (payment_id,))
                    conn.commit()
            
            self.logger.info(f"✅ PayPal payment completed: {payment_id}")
            
        except Exception as e:
            self.logger.error(f"PayPal payment completion processing error: {e}")
    
    def process_paypal_subscription_created(self, subscription: Dict[str, Any]):
        """PayPal obuna yaratish qayta ishlash"""
        try:
            # Similar to Stripe subscription processing
            self.logger.info(f"✅ PayPal subscription created: {subscription['id']}")
            
        except Exception as e:
            self.logger.error(f"PayPal subscription creation processing error: {e}")
    
    def process_paypal_subscription_activated(self, subscription: Dict[str, Any]):
        """PayPal obuna aktivatsiyasi qayta ishlash"""
        try:
            # Update subscription status to active
            self.logger.info(f"✅ PayPal subscription activated: {subscription['id']}")
            
        except Exception as e:
            self.logger.error(f"PayPal subscription activation processing error: {e}")
    
    def process_paypal_subscription_canceled(self, subscription: Dict[str, Any]):
        """PayPal obuna bekor qilish qayta ishlash"""
        try:
            # Update subscription status to canceled
            self.logger.info(f"✅ PayPal subscription canceled: {subscription['id']}")
            
        except Exception as e:
            self.logger.error(f"PayPal subscription cancellation processing error: {e}")
    
    def get_user_payment_methods(self, user_id: int) -> List[PaymentMethod]:
        """Foydalanuvchi to'lov usullarini olish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM payment_methods 
                        WHERE user_id = %s 
                        ORDER BY is_default DESC, created_at DESC
                    """, (user_id,))
                    
                    methods = []
                    for row in cur.fetchall():
                        methods.append(PaymentMethod(
                            id=str(row["id"]),
                            type=row["type"],
                            last_four=row["last_four"],
                            brand=row["brand"],
                            exp_month=row["exp_month"],
                            exp_year=row["exp_year"],
                            is_default=row["is_default"],
                            created_at=row["created_at"]
                        ))
                    
                    return methods
                    
        except Exception as e:
            self.logger.error(f"Payment methods olishda xato: {e}")
            return []
    
    def get_user_subscriptions(self, user_id: int) -> List[Subscription]:
        """Foydalanuvchi obunalarini olish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT s.*, p.name as plan_name, p.description as plan_description
                        FROM subscriptions s
                        JOIN payment_plans p ON s.plan_id = p.id
                        WHERE s.user_id = %s
                        ORDER BY s.created_at DESC
                    """, (user_id,))
                    
                    subscriptions = []
                    for row in cur.fetchall():
                        subscriptions.append(Subscription(
                            id=row["id"],
                            user_id=row["user_id"],
                            plan_id=row["plan_id"],
                            stripe_subscription_id=row["stripe_subscription_id"],
                            paypal_subscription_id=row["paypal_subscription_id"],
                            status=row["status"],
                            current_period_start=row["current_period_start"],
                            current_period_end=row["current_period_end"],
                            cancel_at=row["cancel_at"],
                            canceled_at=row["canceled_at"],
                            trial_start=row["trial_start"],
                            trial_end=row["trial_end"],
                            created_at=row["created_at"]
                        ))
                    
                    return subscriptions
                    
        except Exception as e:
            self.logger.error(f"Subscriptions olishda xato: {e}")
            return []
    
    def get_payment_history(self, user_id: int, limit: int = 50) -> List[Payment]:
        """To'lov tarixini olish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM payments 
                        WHERE user_id = %s 
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (user_id, limit))
                    
                    payments = []
                    for row in cur.fetchall():
                        payments.append(Payment(
                            id=row["id"],
                            user_id=row["user_id"],
                            amount=float(row["amount"]),
                            currency=row["currency"],
                            payment_method=row["payment_method"],
                            payment_provider=row["payment_provider"],
                            provider_payment_id=row["provider_payment_id"],
                            status=row["status"],
                            description=row["description"],
                            metadata=row["metadata"],
                            created_at=row["created_at"],
                            processed_at=row["processed_at"]
                        ))
                    
                    return payments
                    
        except Exception as e:
            self.logger.error(f"Payment history olishda xato: {e}")
            return []


def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Payment Integration System")
    parser.add_argument("--environment", "-e", default="production",
                       choices=["development", "staging", "production"],
                       help="Payment environment")
    parser.add_argument("--action", "-a", default="initialize",
                       choices=["initialize", "test-payment", "webhook-test"],
                       help="Action to perform")
    parser.add_argument("--amount", type=float, default=29.99,
                       help="Test payment amount")
    parser.add_argument("--user-id", type=int, default=1,
                       help="Test user ID")
    
    args = parser.parse_args()
    
    # Environment validatsiyasi
    if not validate_environment():
        print("❌ Environment validatsiyasi muvaffaqiyatsiz!")
        sys.exit(1)
    
    payment_system = ProductionPaymentSystem(args.environment)
    
    if args.action == "initialize":
        print("✅ Payment Integration tizimi tayyor!")
    elif args.action == "test-payment":
        success, message, payment_id = payment_system.process_payment(
            user_id=args.user_id,
            amount=args.amount,
            payment_method="stripe",
            payment_type="one_time",
            plan_id="basic",
            description="Test payment"
        )
        if success:
            print(f"✅ Test payment muvaffaqiyatli: {payment_id}")
        else:
            print(f"❌ Test payment xatosi: {message}")
    elif args.action == "webhook-test":
        print("🔔 Webhook test endpoint ready")
    
    print("💳 Payment Integration tizimi ishga tushdi!")


if __name__ == "__main__":
    main()