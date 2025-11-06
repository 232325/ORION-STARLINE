# Multi-Currency Wallet Tizimi

Bu loyiha ko'p-valyutali hamyon tizimini amalga oshiradi, 18+ ta valyutani (fiat va kripto) qo'llab-quvvatlaydi.

## Asosiy Xususiyatlar

### 🔧 Enums
- **CurrencyType**: Fiat va Kripto valyuta turlari
- **Currency**: 27 ta valyuta (15 fiat + 12 kripto)
- **TransactionType**: Tranzaksiya turlari
- **TransactionStatus**: Tranzaksiya holatlari

### 💰 Valyutalar Ro'yxati

#### Fiat Valyutalar (15 ta)
- USD (US Dollar) - $
- EUR (Euro) - €
- UZS (Uzbekistan Som) - so'm
- RUB (Russian Ruble) - ₽
- GBP (British Pound) - £
- CNY (Chinese Yuan) - ¥
- JPY (Japanese Yen) - ¥
- KRW (Korean Won) - ₩
- TRY (Turkish Lira) - ₺
- INR (Indian Rupee) - ₹
- KZT (Kazakhstani Tenge) - ₸
- CHF (Swiss Franc) - CHF
- CAD (Canadian Dollar) - C$
- AUD (Australian Dollar) - A$
- NZD (New Zealand Dollar) - NZ$

#### Kripto Valyutalar (12 ta)
- BTC (Bitcoin) - ₿
- ETH (Ethereum) - Ξ
- USDT (Tether) - ₮
- USDC (USD Coin) - USDC
- BNB (Binance Coin) - BNB
- XRP (XRP) - XRP
- ADA (Cardano) - ADA
- DOGE (Dogecoin) - DOGE
- SOL (Solana) - SOL
- MATIC (Polygon) - MATIC
- AVAX (Avalanche) - AVAX
- DOT (Polkadot) - DOT

### 🔄 Asosiy Metodlar

#### 1. `create_wallet()`
```python
wallet = await wallet_system.create_wallet(
    user_id="user_001",
    name="Mening Hamyonim",
    initial_balances={
        Currency.USD: Decimal("1000.00"),
        Currency.BTC: Decimal("0.01")
    }
)
```

#### 2. `deposit()`
```python
transaction = await wallet_system.deposit(
    wallet_id=wallet.id,
    currency=Currency.EUR,
    amount=Decimal("500.00"),
    description="Maosh kirim"
)
```

#### 3. `withdraw()`
```python
transaction = await wallet_system.withdraw(
    wallet_id=wallet.id,
    currency=Currency.USD,
    amount=Decimal("200.00"),
    description="Xarid"
)
```

#### 4. `exchange_currency()` (valyuta almashtirish)
```python
transaction = await wallet_system.exchange_currency(
    wallet_id=wallet.id,
    from_currency=Currency.USD,
    to_currency=Currency.EUR,
    amount=Decimal("200.00"),
    fee_percentage=Decimal("0.001")  # 0.1% komissiya
)
```

#### 5. `transfer_between_wallets()` (wallet o'rtasida transfer)
```python
transaction = await wallet_system.transfer_between_wallets(
    from_wallet_id=wallet1.id,
    to_wallet_id=wallet2.id,
    currency=Currency.UZS,
    amount=Decimal("1000000.00"),
    description="Do'stga yordam"
)
```

#### 6. `get_portfolio_summary()` (portfel xulosasi)
```python
summary = await wallet_system.get_portfolio_summary("user_001")

# Natija:
{
    "user_id": "user_001",
    "total_value_usd": "3163.50",
    "fiat_total": "1858.50",
    "crypto_total": "1305.00",
    "balances_by_currency": {
        "USD": {
            "currency_name": "US Dollar",
            "symbol": "$",
            "amount": "800.00",
            "value_usd": "800.00"
        },
        "BTC": {
            "currency_name": "Bitcoin",
            "symbol": "₿",
            "amount": "0.03",
            "value_usd": "1305.00"
        }
    },
    "distribution": {
        "USD": {
            "percentage": 25.3,
            "value_usd": "800.00"
        },
        "BTC": {
            "percentage": 41.3,
            "value_usd": "1305.00"
        }
    }
}
```

### 🔍 Qo'shimcha Metodlar

#### Valyuta Ma'lumotlari
```python
# Ma'lum valyuta haqida
currency_info = wallet_system.get_currency_info('USD')

# Barcha valyutalar ro'yxati
all_currencies = wallet_system.get_supported_currencies_by_type()

# Barcha valyutalar ma'lumotlari
currencies_details = wallet_system.get_all_currencies_info()
```

#### Balance Operatsiyalari
```python
# Ma'lum valyutadagi balans
balance = await wallet_system.get_balance(wallet_id, Currency.USD)

# Barcha balanslar
all_balances = await wallet_system.get_all_balances(wallet_id)

# Tranzaksiya tarixi
history = await wallet_system.get_transaction_history(wallet_id)
```

#### Exchange Rate
```python
# Kurs ma'lumotlari
rate_info = await wallet_system.get_exchange_rate(
    from_currency=Currency.USD,
    to_currency=Currency.EUR
)

# Barcha kurslar
all_rates = await wallet_system.get_all_exchange_rates(Currency.USD)
```

#### Statistika
```python
stats = wallet_system.get_statistics()
# Natija:
{
    "total_wallets": 2,
    "total_transactions": 4,
    "completed_transactions": 4,
    "total_volume_usd": "1695.50",
    "supported_currencies": 27,
    "fiat_currencies": 15,
    "crypto_currencies": 12
}
```

### 🏗️ Arxitektura

#### CurrencyBalance
```python
@dataclass
class CurrencyBalance:
    currency: Currency
    available: Decimal  # Mavjud mablag'
    locked: Decimal    # Bloklangan mablag'
    
    def get_total(self) -> Decimal:
        return self.available + self.locked
```

#### Transaction
```python
@dataclass
class Transaction:
    id: str
    wallet_id: str
    type: TransactionType
    currency: Currency
    amount: Decimal
    status: TransactionStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    from_currency: Optional[Currency] = None
    to_currency: Optional[Currency] = None
    exchange_rate: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    description: Optional[str] = None
```

#### Wallet
```python
@dataclass
class Wallet:
    id: str
    user_id: str
    name: str
    balances: Dict[Currency, CurrencyBalance]
    created_at: datetime
    is_active: bool = True
```

### 🎯 Foydalanish Misoli

```python
import asyncio
from decimal import Decimal
from multi_currency import MultiCurrencyWallet, Currency

async def main():
    # Tizimni yaratish
    wallet_system = MultiCurrencyWallet()
    
    # Wallet yaratish
    wallet = await wallet_system.create_wallet(
        user_id="user_001",
        name="Asosiy Hamyon"
    )
    
    # Mablag' qo'shish
    await wallet_system.deposit(wallet.id, Currency.USD, Decimal("1000"))
    
    # Valyuta almashtirish
    await wallet_system.exchange_currency(
        wallet.id, Currency.USD, Currency.EUR, Decimal("500")
    )
    
    # Portfel xulosasi
    summary = await wallet_system.get_portfolio_summary("user_001")
    print(f"Jami qiymat: ${summary['total_value_usd']}")
    
asyncio.run(main())
```

### 🚀 Test Qilish

```bash
cd /workspace/code/payment
python3 test_multi_currency.py
```

### ✨ Xususiyatlari

- ✅ 27 ta valyuta (15 fiat + 12 kripto)
- ✅ Valyuta almashtirish
- ✅ Wallet o'rtasida transfer
- ✅ Portfel boshqaruvi
- ✅ Tranzaksiya tarixi
- ✅ Exchange rate management
- ✅ Decimal hisoblash (aniq natijalar)
- ✅ Async/await API
- ✅ Comprehensive logging
- ✅ Currency type classification
- ✅ Detailed statistics

### 📊 Test Natija Misoli

```
============================================================
MULTI-CURRENCY WALLET TIZIMI - TEST
============================================================

1. VALYUTALAR HAQIDA MA'LUMOT
Fiat valyutalar (15 ta): USD, EUR, UZS, RUB, GBP, CNY, JPY, KRW, TRY, INR, KZT, CHF, CAD, AUD, NZD
Kripto valyutalar (12 ta): BTC, ETH, USDT, USDC, BNB, XRP, ADA, DOGE, SOL, MATIC, AVAX, DOT

8. PORTFEL XULOSASI
Jami qiymat (USD): $3163.50
Fiat valyutalar: $1858.50
Kripto valyutalar: $1305.00

Valyuta taqsimoti:
  USD: 25.3% ($800.00) - US Dollar
  UZS: 9.9% ($312.00) - Uzbekistan Som
  BTC: 41.3% ($1305.00) - Bitcoin
  EUR: 23.6% ($746.50) - Euro

11. SISTEM STATISTIKASI
Jami walletlar: 2
Jami tranzaksiyalar: 4
Tugallangan tranzaksiyalar: 4
Jami hajmi (USD): $1695.50
Qo'llab-quvvatlanadigan valyutalar: 27
  - Fiat: 15 ta
  - Kripto: 12 ta

============================================================
TEST MUFAQQIYATLI YAKUNLANDI! ✓
============================================================
```

---

**Muallif**: Task Agent  
** Sana**: 2025-11-04  
** Versiya**: 1.0  
