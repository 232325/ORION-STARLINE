#!/usr/bin/env python3
"""
Payment Gateway Test
To'lov tizimi test qilish
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


async def test_payment_gateway():
    """Payment gateway ni test qilish"""
    
    print("🚀 Payment Gateway Test")
    print("=" * 50)
    
    # Gateway yaratish
    gateway = PaymentGateway()
    
    # 1. Barcha planlarni ko'rish
    print("\n📋 Available Plans:")
    plans = await gateway.get_all_plans()
    for plan in plans:
        print(f"  • {plan['name']}: ${plan['price']}/{plan['billing_period']}")
    
    # 2. Foydalanuvchi subscription yaratish
    print("\n👤 Creating user subscription...")
    user_id = "user_123"
    subscription = await gateway.create_subscription(
        user_id=user_id,
        plan=SubscriptionPlan.PROFESSIONAL,
        trial_days=14
    )
    print(f"  ✅ Subscription created: {subscription.id}")
    print(f"     Plan: {subscription.plan.value}")
    print(f"     Status: {subscription.status}")
    print(f"     Amount: ${subscription.amount}")
    print(f"     Days remaining: {subscription.days_remaining()}")
    
    # 3. Invoice ma'lumotlarini ko'rish
    print("\n📄 Invoice Information:")
    invoices = await gateway.get_user_invoices(user_id)
    if invoices:
        invoice = invoices[0]
        print(f"  • Invoice ID: {invoice.id}")
        print(f"  • Amount: ${invoice.amount}")
        print(f"  • Status: {invoice.status.value}")
        print(f"  • Due date: {invoice.due_date.strftime('%Y-%m-%d')}")
    
    # 4. Payment processing
    print("\n💳 Processing Payment...")
    if invoices:
        payment = await gateway.process_payment(
            invoice_id=invoices[0].id,
            payment_method=PaymentMethod.CARD
        )
        print(f"  ✅ Payment processed: {payment.id}")
        print(f"     Status: {payment.status.value}")
        print(f"     Method: {payment.method.value}")
    
    # 5. Billing history
    print("\n📊 Billing History:")
    history = await gateway.get_billing_history(user_id)
    print(f"  • Total invoices: {history['total_invoices']}")
    print(f"  • Total payments: {history['total_payments']}")
    print(f"  • Total paid: ${history['total_paid']}")
    print(f"  • Outstanding: ${history['outstanding_balance']}")
    
    # 6. Plan upgrade
    print("\n⬆️  Upgrading Plan...")
    upgraded = await gateway.upgrade_subscription(
        subscription_id=subscription.id,
        new_plan=SubscriptionPlan.ENTERPRISE
    )
    print(f"  ✅ Plan upgraded: {upgraded.plan.value}")
    print(f"  • New amount: ${upgraded.amount}")
    
    # 7. Statistics
    print("\n📈 Gateway Statistics:")
    stats = gateway.get_statistics()
    print(f"  • Total subscriptions: {stats['total_subscriptions']}")
    print(f"  • Active subscriptions: {stats['active_subscriptions']}")
    print(f"  • Total revenue: ${stats['total_revenue']}")
    print(f"  • Successful payments: {stats['successful_payments']}")
    print(f"  • Plan distribution: {stats['plan_distribution']}")
    
    print("\n✅ Payment Gateway test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_payment_gateway())