#!/usr/bin/env python3
"""
Payment Gateway - Foydalanish Misollari
"""

import asyncio
from decimal import Decimal
from payment_gateway import (
    PaymentGateway, 
    SubscriptionPlan, 
    PaymentMethod, 
    InvoiceStatus, 
    PaymentStatus
)


async def example_basic_usage():
    """Oddiy foydalanish misoli"""
    
    print("🚀 Payment Gateway - Oddiy Foydalanish")
    print("=" * 50)
    
    # 1. Gateway yaratish
    gateway = PaymentGateway()
    
    # 2. Foydalanuvchi uchun subscription yaratish
    subscription = await gateway.create_subscription(
        user_id="user_001",
        plan=SubscriptionPlan.BASIC,
        trial_days=7  # 7 kunlik sinov
    )
    
    print(f"✅ Subscription yaratildi: {subscription.id}")
    print(f"   Plan: {subscription.plan.value}")
    print(f"   Status: {subscription.status}")
    print(f"   Trial muddati: {subscription.trial_end}")
    
    # 3. Invoice olish
    invoices = await gateway.get_user_invoices("user_001")
    invoice = invoices[0]
    
    print(f"\n📄 Invoice: {invoice.id}")
    print(f"   Summa: ${invoice.amount}")
    print(f"   Holat: {invoice.status.value}")
    print(f"   To'lov muddati: {invoice.due_date.strftime('%Y-%m-%d')}")
    
    # 4. Payment processing
    payment = await gateway.process_payment(
        invoice_id=invoice.id,
        payment_method=PaymentMethod.CARD
    )
    
    print(f"\n💳 Payment: {payment.id}")
    print(f"   Holat: {payment.status.value}")
    print(f"   Usul: {payment.method.value}")
    
    # 5. Plan upgrade qilish
    upgraded = await gateway.upgrade_subscription(
        subscription_id=subscription.id,
        new_plan=SubscriptionPlan.PROFESSIONAL
    )
    
    print(f"\n⬆️ Plan upgrade qilindi: {upgraded.plan.value}")
    print(f"   Yangi narx: ${upgraded.amount}")


async def example_advanced_usage():
    """Murakkab foydalanish misoli"""
    
    print("\n\n🎯 Payment Gateway - Murakkab Foydalanish")
    print("=" * 50)
    
    gateway = PaymentGateway()
    
    # 1. Barcha planlarni ko'rish
    plans = await gateway.get_all_plans()
    print("\n📋 Barcha planlar:")
    for plan in plans:
        print(f"   {plan['name']}: ${plan['price']}/oy")
        print(f"      Max strategies: {plan['features']['max_strategies']}")
        print(f"      API calls: {plan['features']['max_api_calls']}")
        print()
    
    # 2. Bir nechta foydalanuvchi yaratish
    users = ["user_100", "user_200", "user_300"]
    for i, user_id in enumerate(users):
        plan = list(SubscriptionPlan)[i+1]  # FREE dan tashqari
        sub = await gateway.create_subscription(
            user_id=user_id,
            plan=plan,
            trial_days=14
        )
        print(f"👤 {user_id} -> {plan.value} plan")
    
    # 3. Billing history
    billing = await gateway.get_billing_history("user_100")
    print(f"\n📊 Billing history (user_100):")
    print(f"   Jami invoice: {billing['total_invoices']}")
    print(f"   Jami to'lov: {billing['total_payments']}")
    print(f"   Jami to'langan: ${billing['total_paid']}")
    print(f"   Qarzdorlik: ${billing['outstanding_balance']}")
    
    # 4. Refund misoli
    user_invoices = await gateway.get_user_invoices("user_100")
    if user_invoices:
        invoice = user_invoices[0]
        
        # Payment yaratish
        payment = await gateway.process_payment(
            invoice_id=invoice.id,
            payment_method=PaymentMethod.STRIPE
        )
        
        # Refund qilish
        refund = await gateway.refund_payment(
            payment_id=payment.id,
            amount=Decimal("10.00"),  # Qisman refund
            reason="Service not satisfied"
        )
        
        print(f"\n🔄 Refund qilindi:")
        print(f"   Refund ID: {refund['refund_id']}")
        print(f"   Summa: ${refund['amount']}")
        print(f"   Sabab: {refund['reason']}")
    
    # 5. Statistics
    stats = gateway.get_statistics()
    print(f"\n📈 Gateway statistikasi:")
    print(f"   Jami subscription: {stats['total_subscriptions']}")
    print(f"   Aktiv subscription: {stats['active_subscriptions']}")
    print(f"   Jami daromad: ${stats['total_revenue']}")
    print(f"   Muvaffaqiyatli payment: {stats['successful_payments']}")
    print(f"   Xato payment: {stats['failed_payments']}")
    print(f"   Plan tarqalishi: {stats['plan_distribution']}")
    print(f"   Muddati o'tgan invoice: {stats['overdue_invoices']}")


async def main():
    """Asosiy funksiya"""
    await example_basic_usage()
    await example_advanced_usage()


if __name__ == "__main__":
    asyncio.run(main())