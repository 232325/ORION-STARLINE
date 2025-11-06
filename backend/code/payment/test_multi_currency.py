"""
Multi-Currency Wallet Tizimi - Test va Demo
"""

import asyncio
from decimal import Decimal
from multi_currency import (
    MultiCurrencyWallet, 
    Currency, 
    CurrencyType,
    TransactionType
)


async def test_multi_currency_wallet():
    """Multi-currency wallet tizimini test qilish"""
    print("=" * 60)
    print("MULTI-CURRENCY WALLET TIZIMI - TEST")
    print("=" * 60)
    
    # Tizimni yaratish
    wallet_system = MultiCurrencyWallet()
    
    print("\n1. VALYUTALAR HAQIDA MA'LUMOT")
    print("-" * 40)
    
    # Barcha valyutalar ro'yxati
    supported = wallet_system.get_supported_currencies_by_type()
    print(f"Fiat valyutalar ({len(supported['fiat'])} ta): {', '.join(supported['fiat'])}")
    print(f"Kripto valyutalar ({len(supported['crypto'])} ta): {', '.join(supported['crypto'])}")
    
    # Ma'lum valyuta haqida
    usd_info = wallet_system.get_currency_info('USD')
    print(f"\nUSD haqida: {usd_info}")
    
    # Wallet yaratish
    print("\n2. WALLET YARATISH")
    print("-" * 40)
    
    wallet = await wallet_system.create_wallet(
        user_id="user_001",
        name="Mening Hamyonim",
        initial_balances={
            Currency.USD: Decimal("1000.00"),
            Currency.UZS: Decimal("5000000.00"),
            Currency.BTC: Decimal("0.01")
        }
    )
    
    print(f"Wallet yaratildi: {wallet.id}")
    print(f"Foydalanuvchi: {wallet.user_id}")
    print(f"Nomi: {wallet.name}")
    
    # Boshlang'ich balanslar
    print("\n3. BOSHLANG'ICH BALANSLAR")
    print("-" * 40)
    
    balances = await wallet_system.get_all_balances(wallet.id)
    for currency, balance in balances.items():
        print(f"{currency}: {balance['total']} ({balance['symbol']}) - {balance['currency_name']}")
    
    # Depozit operatsiyasi
    print("\n4. DEPOZIT OPERATSIYASI")
    print("-" * 40)
    
    deposit_txn = await wallet_system.deposit(
        wallet_id=wallet.id,
        currency=Currency.EUR,
        amount=Decimal("500.00"),
        description="Maosh kirim"
    )
    
    print(f"Depozit tranzaksiya: {deposit_txn.id}")
    print(f"Miqdor: {deposit_txn.amount} {deposit_txn.currency.value}")
    print(f"Holati: {deposit_txn.status.value}")
    
    # Yana bir depozit
    deposit_txn2 = await wallet_system.deposit(
        wallet_id=wallet.id,
        currency=Currency.BTC,
        amount=Decimal("0.02"),
        description="Bitcoin xarid"
    )
    
    # Valyuta almashtirish
    print("\n5. VALYUTA ALMASHTIRISH (exchange_currency)")
    print("-" * 40)
    
    exchange_txn = await wallet_system.exchange_currency(
        wallet_id=wallet.id,
        from_currency=Currency.USD,
        to_currency=Currency.EUR,
        amount=Decimal("200.00"),
        fee_percentage=Decimal("0.005")
    )
    
    print(f"Almashtirish tranzaksiya: {exchange_txn.id}")
    print(f"Miqdor: {exchange_txn.amount} {exchange_txn.currency.value}")
    print(f"Maqsad: {exchange_txn.to_currency.value}")
    print(f"Komissiya: {exchange_txn.fee}")
    print(f"Kurs: {exchange_txn.exchange_rate}")
    
    # Transfer operatsiyasi
    print("\n6. WALLET O'RTASIDA TRANSFER (transfer_between_wallets)")
    print("-" * 40)
    
    # Ikkinchi wallet yaratish
    wallet2 = await wallet_system.create_wallet(
        user_id="user_002",
        name="John Doening Hamyoni",
        initial_balances={
            Currency.USD: Decimal("500.00")
        }
    )
    
    transfer_txn = await wallet_system.transfer_between_wallets(
        from_wallet_id=wallet.id,
        to_wallet_id=wallet2.id,
        currency=Currency.UZS,
        amount=Decimal("1000000.00"),
        description="Do'stga yordam"
    )
    
    print(f"Transfer tranzaksiya: {transfer_txn.id}")
    print(f"O'tkazilgan miqdor: {transfer_txn.amount} {transfer_txn.currency.value}")
    print(f"Manba wallet: {transfer_txn.wallet_id}")
    
    # Aktual balanslar
    print("\n7. AKTUAL BALANSLAR")
    print("-" * 40)
    
    print("Birinchi wallet:")
    balances1 = await wallet_system.get_all_balances(wallet.id)
    for currency, balance in balances1.items():
        print(f"  {currency}: {balance['total']} ({balance['symbol']})")
    
    print("\nIkkinchi wallet:")
    balances2 = await wallet_system.get_all_balances(wallet2.id)
    for currency, balance in balances2.items():
        print(f"  {currency}: {balance['total']} ({balance['symbol']})")
    
    # Portfel xulosasi
    print("\n8. PORTFEL XULOSASI (get_portfolio_summary)")
    print("-" * 40)
    
    portfolio = await wallet_system.get_portfolio_summary("user_001")
    print(f"Jami qiymat (USD): ${portfolio['total_value_usd']}")
    print(f"Fiat valyutalar: ${portfolio['fiat_total']}")
    print(f"Kripto valyutalar: ${portfolio['crypto_total']}")
    
    print("\nValyuta taqsimoti:")
    for currency, dist in portfolio['distribution'].items():
        currency_info = portfolio['balances_by_currency'][currency]
        print(f"  {currency}: {dist['percentage']:.1f}% (${dist['value_usd']}) - {currency_info['currency_name']}")
    
    # Tranzaksiya tarixi
    print("\n9. TRANZAKSIYA TARIXI")
    print("-" * 40)
    
    history = await wallet_system.get_transaction_history(
        wallet_id=wallet.id,
        limit=5
    )
    
    print(f"Umumiy tranzaksiyalar soni: {len(history)}")
    for txn in history:
        print(f"\nTranzaksiya ID: {txn.id}")
        print(f"  Tur: {txn.type.value}")
        print(f"  Valyuta: {txn.currency.value}")
        print(f"  Miqdor: {txn.amount}")
        print(f"  Vaqt: {txn.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if txn.description:
            print(f"  Tavsif: {txn.description}")
    
    # Exchange rate
    print("\n10. EXCHANGE RATE")
    print("-" * 40)
    
    rate_info = await wallet_system.get_exchange_rate(
        from_currency=Currency.USD,
        to_currency=Currency.EUR
    )
    
    print(f"1 USD = {rate_info['rate']} EUR")
    print(f"1 EUR = {rate_info['inverse_rate']} USD")
    
    # Sistem statistikasi
    print("\n11. SISTEM STATISTIKASI")
    print("-" * 40)
    
    stats = wallet_system.get_statistics()
    print(f"Jami walletlar: {stats['total_wallets']}")
    print(f"Jami tranzaksiyalar: {stats['total_transactions']}")
    print(f"Tugallangan tranzaksiyalar: {stats['completed_transactions']}")
    print(f"Jami hajmi (USD): ${stats['total_volume_usd']}")
    print(f"Qo'llab-quvvatlanadigan valyutalar: {stats['supported_currencies']}")
    print(f"  - Fiat: {stats['fiat_currencies']} ta")
    print(f"  - Kripto: {stats['crypto_currencies']} ta")
    
    print("\n" + "=" * 60)
    print("TEST MUFAQQIYATLI YAKUNLANDI! ✓")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_multi_currency_wallet())
