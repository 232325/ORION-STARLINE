"""
Multi-Currency Wallet System
Ko'p valyutali hamyon tizimi

Xususiyatlar:
- Multiple currency wallets (USD, EUR, GBP, Crypto)
- Currency conversion va exchange
- Balance tracking
- Transaction history
- Multi-currency portfolio management
- Real-time exchange rates
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class CurrencyType(Enum):
    """Valyuta turlari"""
    FIAT = "fiat"
    CRYPTO = "crypto"


class Currency(Enum):
    """Qo'llab-quvvatlanadigan valyutalar (18+ ta)"""
    
    # Fiat valyutalar
    USD = ("US Dollar", CurrencyType.FIAT, "$", "Amerika Qo'shma Shtatlari")
    EUR = ("Euro", CurrencyType.FIAT, "€", "Yevropa Ittifoqi")
    UZS = ("Uzbekistan Som", CurrencyType.FIAT, "so'm", "O'zbekiston")
    RUB = ("Russian Ruble", CurrencyType.FIAT, "₽", "Rossiya")
    GBP = ("British Pound", CurrencyType.FIAT, "£", "Britaniya")
    CNY = ("Chinese Yuan", CurrencyType.FIAT, "¥", "Xitoy")
    JPY = ("Japanese Yen", CurrencyType.FIAT, "¥", "Yaponiya")
    KRW = ("Korean Won", CurrencyType.FIAT, "₩", "Janubiy Koreya")
    TRY = ("Turkish Lira", CurrencyType.FIAT, "₺", "Turkiya")
    INR = ("Indian Rupee", CurrencyType.FIAT, "₹", "Hindiston")
    KZT = ("Kazakhstani Tenge", CurrencyType.FIAT, "₸", "Qozog'iston")
    CHF = ("Swiss Franc", CurrencyType.FIAT, "CHF", "Shveysariya")
    CAD = ("Canadian Dollar", CurrencyType.FIAT, "C$", "Kanada")
    AUD = ("Australian Dollar", CurrencyType.FIAT, "A$", "Avstraliya")
    NZD = ("New Zealand Dollar", CurrencyType.FIAT, "NZ$", "Yangi Zelandiya")
    
    # Kripto valyutalar
    BTC = ("Bitcoin", CurrencyType.CRYPTO, "₿", "Decentralized")
    ETH = ("Ethereum", CurrencyType.CRYPTO, "Ξ", "Decentralized")
    USDT = ("Tether", CurrencyType.CRYPTO, "₮", "Stablecoin")
    USDC = ("USD Coin", CurrencyType.CRYPTO, "USDC", "Stablecoin")
    BNB = ("Binance Coin", CurrencyType.CRYPTO, "BNB", "Binance")
    XRP = ("XRP", CurrencyType.CRYPTO, "XRP", "Ripple")
    ADA = ("Cardano", CurrencyType.CRYPTO, "ADA", "Cardano")
    DOGE = ("Dogecoin", CurrencyType.CRYPTO, "DOGE", "Meme coin")
    SOL = ("Solana", CurrencyType.CRYPTO, "SOL", "High-speed")
    MATIC = ("Polygon", CurrencyType.CRYPTO, "MATIC", "Layer 2")
    AVAX = ("Avalanche", CurrencyType.CRYPTO, "AVAX", "Smart contracts")
    DOT = ("Polkadot", CurrencyType.CRYPTO, "DOT", "Multi-chain")
    
    def __init__(self, name: str, currency_type: CurrencyType, symbol: str, country: str):
        self.full_name = name
        self.type = currency_type
        self.symbol = symbol
        self.country = country
        
    @property
    def code(self) -> str:
        """Currency kodini olish (masalan, USD, EUR)"""
        return self.name
        
    @property
    def value(self) -> str:
        """Enum value - currency code"""
        return self.name
        
    @classmethod
    def get_by_type(cls, currency_type: CurrencyType) -> List['Currency']:
        """Ma'lum turdagi valyutalarni olish"""
        return [currency for currency in cls if currency.type == currency_type]
        
    @property
    def is_fiat(self) -> bool:
        """Fiat valyuta ekanligini tekshirish"""
        return self.type == CurrencyType.FIAT
        
    @property
    def is_crypto(self) -> bool:
        """Kripto valyuta ekanligini tekshirish"""
        return self.type == CurrencyType.CRYPTO


class TransactionType(Enum):
    """Tranzaksiya turlari"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    EXCHANGE = "exchange"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    REFUND = "refund"


class TransactionStatus(Enum):
    """Tranzaksiya holati"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass
class CurrencyBalance:
    """Valyuta balansi"""
    currency: Currency
    available: Decimal
    locked: Decimal = Decimal("0")
    
    def get_total(self) -> Decimal:
        """Umumiy balans"""
        return self.available + self.locked
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "currency": self.currency.value,
            "currency_name": self.currency.full_name,
            "symbol": self.currency.symbol,
            "type": self.currency.type.value,
            "available": str(self.available),
            "locked": str(self.locked),
            "total": str(self.get_total())
        }


@dataclass
class Transaction:
    """Tranzaksiya"""
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
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "wallet_id": self.wallet_id,
            "type": self.type.value,
            "currency": self.currency.value,
            "amount": str(self.amount),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "from_currency": self.from_currency.value if self.from_currency else None,
            "to_currency": self.to_currency.value if self.to_currency else None,
            "exchange_rate": str(self.exchange_rate) if self.exchange_rate else None,
            "fee": str(self.fee) if self.fee else None,
            "description": self.description,
            "metadata": self.metadata
        }


@dataclass
class Wallet:
    """Multi-currency wallet"""
    id: str
    user_id: str
    name: str
    balances: Dict[Currency, CurrencyBalance]
    created_at: datetime
    is_active: bool = True
    
    def get_balance(self, currency: Currency) -> CurrencyBalance:
        """Valyuta balansini olish"""
        if currency not in self.balances:
            self.balances[currency] = CurrencyBalance(
                currency=currency,
                available=Decimal("0"),
                locked=Decimal("0")
            )
        return self.balances[currency]
    
    def get_total_value_in_usd(self, exchange_rates: Dict[Currency, Decimal]) -> Decimal:
        """USD dagi umumiy qiymat"""
        total = Decimal("0")
        
        for currency, balance in self.balances.items():
            if currency == Currency.USD:
                total += balance.get_total()
            else:
                rate = exchange_rates.get(currency, Decimal("1"))
                total += balance.get_total() * rate
        
        return total
    
    def to_dict(self, exchange_rates: Optional[Dict[Currency, Decimal]] = None) -> Dict[str, Any]:
        balances_dict = {
            currency.value: balance.to_dict()
            for currency, balance in self.balances.items()
            if balance.get_total() > 0
        }
        
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "balances": balances_dict,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }
        
        if exchange_rates:
            result["total_value_usd"] = str(self.get_total_value_in_usd(exchange_rates))
        
        return result


class MultiCurrencyWallet:
    """
    Multi-Currency Wallet System
    
    Ko'p valyutali hamyon tizimi bilan ishlash
    """
    
    def __init__(self):
        self.wallets: Dict[str, Wallet] = {}
        self.transactions: Dict[str, Transaction] = {}
        
        # Exchange rates (to USD)
        self.exchange_rates: Dict[Currency, Decimal] = {
            # Fiat currencies
            Currency.USD: Decimal("1.0000"),
            Currency.EUR: Decimal("1.0950"),
            Currency.UZS: Decimal("0.000078"),  # 1 UZS = 0.000078 USD
            Currency.RUB: Decimal("0.0135"),
            Currency.GBP: Decimal("1.2650"),
            Currency.CNY: Decimal("0.1390"),
            Currency.JPY: Decimal("0.0067"),
            Currency.KRW: Decimal("0.00067"),
            Currency.TRY: Decimal("0.059"),
            Currency.INR: Decimal("0.0120"),
            Currency.KZT: Decimal("0.0023"),
            Currency.CHF: Decimal("1.1430"),
            Currency.CAD: Decimal("0.7395"),
            Currency.AUD: Decimal("0.6580"),
            Currency.NZD: Decimal("0.6120"),
            # Crypto currencies
            Currency.BTC: Decimal("43500.00"),
            Currency.ETH: Decimal("2280.00"),
            Currency.USDT: Decimal("1.0000"),
            Currency.USDC: Decimal("1.0000"),
            Currency.BNB: Decimal("315.00"),
            Currency.SOL: Decimal("102.00"),
            Currency.XRP: Decimal("0.5850"),
            Currency.ADA: Decimal("0.5120"),
            Currency.DOGE: Decimal("0.075"),
            Currency.MATIC: Decimal("0.85"),
            Currency.AVAX: Decimal("35.50"),
            Currency.DOT: Decimal("6.75")
        }
        
        logger.info("MultiCurrencyWallet initialized")
    
    async def create_wallet(
        self,
        user_id: str,
        name: str,
        initial_balances: Optional[Dict[Currency, Decimal]] = None
    ) -> Wallet:
        """
        Yangi wallet yaratish
        
        Args:
            user_id: Foydalanuvchi ID
            name: Wallet nomi
            initial_balances: Boshlang'ich balanslar
        
        Returns:
            Yaratilgan wallet
        """
        import uuid
        
        balances = {}
        if initial_balances:
            for currency, amount in initial_balances.items():
                balances[currency] = CurrencyBalance(
                    currency=currency,
                    available=amount
                )
        
        wallet = Wallet(
            id=f"wallet_{uuid.uuid4().hex[:16]}",
            user_id=user_id,
            name=name,
            balances=balances,
            created_at=datetime.now()
        )
        
        self.wallets[wallet.id] = wallet
        
        logger.info(f"Wallet created: {wallet.id} for user {user_id}")
        
        return wallet
    
    async def deposit(
        self,
        wallet_id: str,
        currency: Currency,
        amount: Decimal,
        description: Optional[str] = None
    ) -> Transaction:
        """
        Depozit qo'shish
        
        Args:
            wallet_id: Wallet ID
            currency: Valyuta
            amount: Summa
            description: Tavsif
        
        Returns:
            Transaction obyekti
        """
        import uuid
        
        if wallet_id not in self.wallets:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        wallet = self.wallets[wallet_id]
        
        # Create transaction
        transaction = Transaction(
            id=f"txn_{uuid.uuid4().hex[:16]}",
            wallet_id=wallet_id,
            type=TransactionType.DEPOSIT,
            currency=currency,
            amount=amount,
            status=TransactionStatus.PROCESSING,
            created_at=datetime.now(),
            description=description
        )
        
        # Update balance
        balance = wallet.get_balance(currency)
        balance.available += amount
        
        # Complete transaction
        transaction.status = TransactionStatus.COMPLETED
        transaction.completed_at = datetime.now()
        
        self.transactions[transaction.id] = transaction
        
        logger.info(f"Deposit: {wallet_id} - {amount} {currency.value}")
        
        return transaction
    
    async def withdraw(
        self,
        wallet_id: str,
        currency: Currency,
        amount: Decimal,
        description: Optional[str] = None
    ) -> Transaction:
        """
        Pul yechish
        
        Args:
            wallet_id: Wallet ID
            currency: Valyuta
            amount: Summa
            description: Tavsif
        
        Returns:
            Transaction obyekti
        """
        import uuid
        
        if wallet_id not in self.wallets:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        wallet = self.wallets[wallet_id]
        balance = wallet.get_balance(currency)
        
        if balance.available < amount:
            raise ValueError(f"Insufficient balance: {balance.available} < {amount}")
        
        # Create transaction
        transaction = Transaction(
            id=f"txn_{uuid.uuid4().hex[:16]}",
            wallet_id=wallet_id,
            type=TransactionType.WITHDRAWAL,
            currency=currency,
            amount=amount,
            status=TransactionStatus.PROCESSING,
            created_at=datetime.now(),
            description=description
        )
        
        # Update balance
        balance.available -= amount
        
        # Complete transaction
        transaction.status = TransactionStatus.COMPLETED
        transaction.completed_at = datetime.now()
        
        self.transactions[transaction.id] = transaction
        
        logger.info(f"Withdrawal: {wallet_id} - {amount} {currency.value}")
        
        return transaction
    
    async def exchange_currency(
        self,
        wallet_id: str,
        from_currency: Currency,
        to_currency: Currency,
        amount: Decimal,
        fee_percentage: Decimal = Decimal("0.001")
    ) -> Transaction:
        """
        Valyuta almashish (asosiy metod)
        
        Args:
            wallet_id: Wallet ID
            from_currency: Manba valyuta
            to_currency: Maqsad valyuta
            amount: Summa (from_currency da)
            fee_percentage: Fee foizi (default: 0.1%)
        
        Returns:
            Transaction obyekti
        """
        return await self.exchange(wallet_id, from_currency, to_currency, amount, fee_percentage)
    
    async def exchange(
        self,
        wallet_id: str,
        from_currency: Currency,
        to_currency: Currency,
        amount: Decimal,
        fee_percentage: Decimal = Decimal("0.001")
    ) -> Transaction:
        """
        Valyuta almashish
        
        Args:
            wallet_id: Wallet ID
            from_currency: Manba valyuta
            to_currency: Maqsad valyuta
            amount: Summa (from_currency da)
            fee_percentage: Fee foizi (default: 0.1%)
        
        Returns:
            Transaction obyekti
        """
        import uuid
        
        if wallet_id not in self.wallets:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        wallet = self.wallets[wallet_id]
        from_balance = wallet.get_balance(from_currency)
        
        if from_balance.available < amount:
            raise ValueError(f"Insufficient balance: {from_balance.available} < {amount}")
        
        # Calculate exchange
        from_rate = self.exchange_rates[from_currency]
        to_rate = self.exchange_rates[to_currency]
        
        # Convert to USD, then to target currency
        usd_value = amount * from_rate
        to_amount = usd_value / to_rate
        
        # Apply fee
        fee = to_amount * fee_percentage
        final_amount = to_amount - fee
        
        # Exchange rate
        exchange_rate = final_amount / amount
        
        # Create transaction
        transaction = Transaction(
            id=f"txn_{uuid.uuid4().hex[:16]}",
            wallet_id=wallet_id,
            type=TransactionType.EXCHANGE,
            currency=from_currency,
            amount=amount,
            status=TransactionStatus.PROCESSING,
            created_at=datetime.now(),
            from_currency=from_currency,
            to_currency=to_currency,
            exchange_rate=exchange_rate,
            fee=fee,
            description=f"Exchange {amount} {from_currency.value} to {final_amount} {to_currency.value}",
            metadata={
                "from_amount": str(amount),
                "to_amount": str(final_amount),
                "fee_amount": str(fee)
            }
        )
        
        # Update balances
        from_balance.available -= amount
        
        to_balance = wallet.get_balance(to_currency)
        to_balance.available += final_amount
        
        # Complete transaction
        transaction.status = TransactionStatus.COMPLETED
        transaction.completed_at = datetime.now()
        
        self.transactions[transaction.id] = transaction
        
        logger.info(f"Exchange: {wallet_id} - {amount} {from_currency.value} -> {final_amount} {to_currency.value}")
        
        return transaction
    
    async def transfer_between_wallets(
        self,
        from_wallet_id: str,
        to_wallet_id: str,
        currency: Currency,
        amount: Decimal,
        description: Optional[str] = None
    ) -> Transaction:
        """
        Wallet o'rtasida transfer (asosiy metod)
        
        Args:
            from_wallet_id: Manba wallet
            to_wallet_id: Maqsad wallet
            currency: Valyuta
            amount: Summa
            description: Tavsif
        
        Returns:
            Transaction obyekti
        """
        return await self.transfer(from_wallet_id, to_wallet_id, currency, amount, description)
    
    async def transfer(
        self,
        from_wallet_id: str,
        to_wallet_id: str,
        currency: Currency,
        amount: Decimal,
        description: Optional[str] = None
    ) -> Transaction:
        """
        Wallet o'rtasida transfer
        
        Args:
            from_wallet_id: Manba wallet
            to_wallet_id: Maqsad wallet
            currency: Valyuta
            amount: Summa
            description: Tavsif
        
        Returns:
            Transaction obyekti
        """
        import uuid
        
        if from_wallet_id not in self.wallets:
            raise ValueError(f"From wallet not found: {from_wallet_id}")
        
        if to_wallet_id not in self.wallets:
            raise ValueError(f"To wallet not found: {to_wallet_id}")
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        from_wallet = self.wallets[from_wallet_id]
        to_wallet = self.wallets[to_wallet_id]
        
        from_balance = from_wallet.get_balance(currency)
        
        if from_balance.available < amount:
            raise ValueError(f"Insufficient balance: {from_balance.available} < {amount}")
        
        # Create transaction
        transaction = Transaction(
            id=f"txn_{uuid.uuid4().hex[:16]}",
            wallet_id=from_wallet_id,
            type=TransactionType.TRANSFER,
            currency=currency,
            amount=amount,
            status=TransactionStatus.PROCESSING,
            created_at=datetime.now(),
            description=description,
            metadata={
                "to_wallet_id": to_wallet_id
            }
        )
        
        # Update balances
        from_balance.available -= amount
        
        to_balance = to_wallet.get_balance(currency)
        to_balance.available += amount
        
        # Complete transaction
        transaction.status = TransactionStatus.COMPLETED
        transaction.completed_at = datetime.now()
        
        self.transactions[transaction.id] = transaction
        
        logger.info(f"Transfer: {from_wallet_id} -> {to_wallet_id} - {amount} {currency.value}")
        
        return transaction
    
    async def get_wallet(self, wallet_id: str) -> Optional[Wallet]:
        """Wallet ma'lumotlarini olish"""
        return self.wallets.get(wallet_id)
    
    async def get_user_wallets(self, user_id: str) -> List[Wallet]:
        """Foydalanuvchi walletlarini olish"""
        return [
            wallet for wallet in self.wallets.values()
            if wallet.user_id == user_id and wallet.is_active
        ]
    
    async def get_balance(
        self,
        wallet_id: str,
        currency: Currency
    ) -> CurrencyBalance:
        """Wallet balansini olish"""
        if wallet_id not in self.wallets:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        wallet = self.wallets[wallet_id]
        return wallet.get_balance(currency)
    
    async def get_all_balances(self, wallet_id: str) -> Dict[str, Dict[str, Any]]:
        """Barcha valyuta balanslarini olish"""
        if wallet_id not in self.wallets:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        wallet = self.wallets[wallet_id]
        
        return {
            currency.value: balance.to_dict()
            for currency, balance in wallet.balances.items()
            if balance.get_total() > 0
        }
    
    async def get_transaction_history(
        self,
        wallet_id: str,
        transaction_type: Optional[TransactionType] = None,
        currency: Optional[Currency] = None,
        limit: int = 100
    ) -> List[Transaction]:
        """
        Tranzaksiya tarixini olish
        
        Args:
            wallet_id: Wallet ID
            transaction_type: Filter by type
            currency: Filter by currency
            limit: Limit
        
        Returns:
            Tranzaksiyalar ro'yxati
        """
        transactions = [
            txn for txn in self.transactions.values()
            if txn.wallet_id == wallet_id
        ]
        
        if transaction_type:
            transactions = [t for t in transactions if t.type == transaction_type]
        
        if currency:
            transactions = [t for t in transactions if t.currency == currency]
        
        # Sort by created_at descending
        transactions.sort(key=lambda x: x.created_at, reverse=True)
        
        return transactions[:limit]
    
    async def get_exchange_rate(
        self,
        from_currency: Currency,
        to_currency: Currency
    ) -> Dict[str, Any]:
        """
        Exchange rate olish
        
        Args:
            from_currency: Manba valyuta
            to_currency: Maqsad valyuta
        
        Returns:
            Exchange rate ma'lumotlari
        """
        from_rate = self.exchange_rates[from_currency]
        to_rate = self.exchange_rates[to_currency]
        
        # Convert via USD
        usd_value = Decimal("1") * from_rate
        rate = usd_value / to_rate
        
        return {
            "from_currency": from_currency.value,
            "to_currency": to_currency.value,
            "rate": str(rate),
            "inverse_rate": str(Decimal("1") / rate),
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_all_exchange_rates(
        self,
        base_currency: Currency = Currency.USD
    ) -> Dict[str, str]:
        """Barcha exchange ratelarni olish"""
        base_rate = self.exchange_rates[base_currency]
        
        rates = {}
        for currency, rate in self.exchange_rates.items():
            if currency != base_currency:
                # Convert via USD
                converted_rate = rate / base_rate
                rates[currency.value] = str(converted_rate)
        
        return rates
    
    async def get_portfolio_summary(self, user_id: str) -> Dict[str, Any]:
        """Foydalanuvchi portfolio xulosasi"""
        wallets = await self.get_user_wallets(user_id)
        
        if not wallets:
            return {
                "user_id": user_id,
                "total_wallets": 0,
                "total_value_usd": "0",
                "balances_by_currency": {},
                "fiat_total": "0",
                "crypto_total": "0",
                "distribution": {}
            }
        
        # Aggregate all balances
        total_by_currency: Dict[Currency, Decimal] = {}
        
        for wallet in wallets:
            for currency, balance in wallet.balances.items():
                if currency not in total_by_currency:
                    total_by_currency[currency] = Decimal("0")
                total_by_currency[currency] += balance.get_total()
        
        # Calculate total value in USD
        total_value_usd = Decimal("0")
        fiat_total = Decimal("0")
        crypto_total = Decimal("0")
        
        for currency, amount in total_by_currency.items():
            rate = self.exchange_rates[currency]
            value_usd = amount * rate
            total_value_usd += value_usd
            
            if currency.type == CurrencyType.FIAT:
                fiat_total += value_usd
            else:
                crypto_total += value_usd
        
        # Format balances va hisoblash
        balances_by_currency = {}
        distribution = {}
        
        for currency, amount in total_by_currency.items():
            if amount > 0:
                value_usd = amount * self.exchange_rates[currency]
                balances_by_currency[currency.value] = {
                    "currency_name": currency.full_name,
                    "symbol": currency.symbol,
                    "type": currency.type.value,
                    "amount": str(amount),
                    "value_usd": str(value_usd)
                }
                
                # Foiz hisoblash
                percentage = (value_usd / total_value_usd * 100) if total_value_usd > 0 else 0
                distribution[currency.value] = {
                    "percentage": float(percentage),
                    "value_usd": str(value_usd)
                }
        
        return {
            "user_id": user_id,
            "total_wallets": len(wallets),
            "total_value_usd": str(total_value_usd),
            "fiat_total": str(fiat_total),
            "crypto_total": str(crypto_total),
            "balances_by_currency": balances_by_currency,
            "distribution": distribution,
            "wallet_ids": [w.id for w in wallets]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Multi-currency wallet statistikasi"""
        total_transactions = len(self.transactions)
        
        # Transaction by type
        txn_by_type = {}
        for txn in self.transactions.values():
            txn_type = txn.type.value
            txn_by_type[txn_type] = txn_by_type.get(txn_type, 0) + 1
        
        # Total volume in USD
        total_volume = Decimal("0")
        for txn in self.transactions.values():
            if txn.status == TransactionStatus.COMPLETED:
                rate = self.exchange_rates.get(txn.currency, Decimal("1"))
                total_volume += txn.amount * rate
        
        # Currency statistics
        fiat_currencies = len([c for c in Currency if c.is_fiat])
        crypto_currencies = len([c for c in Currency if c.is_crypto])
        
        return {
            "total_wallets": len(self.wallets),
            "total_transactions": total_transactions,
            "completed_transactions": sum(
                1 for t in self.transactions.values()
                if t.status == TransactionStatus.COMPLETED
            ),
            "total_volume_usd": str(total_volume),
            "transactions_by_type": txn_by_type,
            "supported_currencies": len(Currency),
            "fiat_currencies": fiat_currencies,
            "crypto_currencies": crypto_currencies,
            "currency_breakdown": {
                "fiat": [c.value for c in Currency.get_by_type(CurrencyType.FIAT)],
                "crypto": [c.value for c in Currency.get_by_type(CurrencyType.CRYPTO)]
            }
        }
    
    def get_supported_currencies_by_type(self) -> Dict[str, List[str]]:
        """Valyuta turlari bo'yicha guruhlash"""
        return {
            "fiat": [currency.value for currency in Currency.get_by_type(CurrencyType.FIAT)],
            "crypto": [currency.value for currency in Currency.get_by_type(CurrencyType.CRYPTO)]
        }
    
    def get_currency_info(self, currency_code: str) -> Optional[Dict[str, Any]]:
        """Ma'lum valyuta haqida ma'lumot olish"""
        try:
            currency = Currency[currency_code.upper()]
            return {
                "code": currency.code,
                "name": currency.full_name,
                "type": currency.type.value,
                "symbol": currency.symbol,
                "country": currency.country,
                "is_fiat": currency.is_fiat,
                "is_crypto": currency.is_crypto,
                "usd_rate": str(self.exchange_rates[currency])
            }
        except KeyError:
            return None
    
    def get_all_currencies_info(self) -> List[Dict[str, Any]]:
        """Barcha valyutalar haqida ma'lumot"""
        return [
            {
                "code": currency.code,
                "name": currency.full_name,
                "type": currency.type.value,
                "symbol": currency.symbol,
                "country": currency.country,
                "is_fiat": currency.is_fiat,
                "is_crypto": currency.is_crypto,
                "usd_rate": str(self.exchange_rates[currency])
            }
            for currency in Currency
        ]
