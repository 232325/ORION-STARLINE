"""
Forex Integration Module
Valyuta savdosi uchun to'liq integratsiya moduli

Xususiyatlar:
- 21+ valyuta juftliklari qo'llab-quvvatlash
- Real-time narx ma'lumotlari (bid/ask)
- Tarixiy ma'lumotlar
- Valyuta aylantirish
- Savdo buyurtmalari
- Iqtisodiy kalendar
- P&L hisoblash
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
import random
import json
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class CurrencyPair(Enum):
    """Valyuta juftliklari (21+ juftlik)"""
    # Asosiy (Major) juftliklar - 7 ta
    EURUSD = "EUR/USD"
    GBPUSD = "GBP/USD"
    USDJPY = "USD/JPY"
    USDCHF = "USD/CHF"
    USDCAD = "USD/CAD"
    AUDUSD = "AUD/USD"
    NZDUSD = "NZD/USD"
    
    # O'zaro (Cross) juftliklar - 15 ta
    EURJPY = "EUR/JPY"
    EURGBP = "EUR/GBP"
    EURCHF = "EUR/CHF"
    EURCAD = "EUR/CAD"
    EURAUD = "EUR/AUD"
    EURNZD = "EUR/NZD"
    GBPJPY = "GBP/JPY"
    GBPCHF = "GBP/CHF"
    GBPCAD = "GBP/CAD"
    GBPAUD = "GBP/AUD"
    GBPNZD = "GBP/NZD"
    CADJPY = "CAD/JPY"
    CHFJPY = "CHF/JPY"
    AUDJPY = "AUD/JPY"
    AUDCHF = "AUD/CHF"
    
    # Egzotik (Exotic) juftliklar - 10+ ta
    AUDCAD = "AUD/CAD"
    AUDNZD = "AUD/NZD"
    NZDJPY = "NZD/JPY"
    NZDCHF = "NZD/CHF"
    NZDCAD = "NZD/CAD"
    NZDAUD = "NZD/AUD"
    USDCNH = "USD/CNH"
    USDTRY = "USD/TRY"
    USDZAR = "USD/ZAR"
    USDMXN = "USD/MXN"
    USDBRL = "USD/BRL"
    USDSEK = "USD/SEK"
    USDNOK = "USD/NOK"
    USDDKK = "USD/DKK"
    USDPLN = "USD/PLN"
    USDHUF = "USD/HUF"


class OrderType(Enum):
    """Buyurtma turlari"""
    MARKET = "Market"
    LIMIT = "Limit"
    STOP = "Stop"
    STOP_LIMIT = "Stop Limit"
    TAKE_PROFIT = "Take Profit"
    TRAILING_STOP = "Trailing Stop"


class TradeSide(Enum):
    """Savdo tomoni"""
    BUY = "Buy"
    SELL = "Sell"


class MarketSession(Enum):
    """Forex bozor sessiyalari"""
    SYDNEY = "Sydney"
    TOKYO = "Tokyo"
    LONDON = "London"
    NEW_YORK = "New York"


@dataclass
class Quote:
    """Valyuta narx ma'lumotlari"""
    pair: CurrencyPair
    bid: Decimal
    ask: Decimal
    spread: Decimal
    timestamp: datetime
    change_24h: Decimal
    change_percent_24h: Decimal
    high_24h: Decimal
    low_24h: Decimal
    volume: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary ga aylantirish"""
        return {
            'pair': self.pair.value,
            'bid': str(self.bid),
            'ask': str(self.ask),
            'spread': str(self.spread),
            'timestamp': self.timestamp.isoformat(),
            'change_24h': str(self.change_24h),
            'change_percent_24h': str(self.change_percent_24h),
            'high_24h': str(self.high_24h),
            'low_24h': str(self.low_24h),
            'volume': self.volume
        }


@dataclass
class Order:
    """Savdo buyurtmasi"""
    order_id: str
    pair: CurrencyPair
    side: TradeSide
    order_type: OrderType
    amount: Decimal  # Lot miqdori
    price: Decimal
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "Pending"
    filled_amount: Decimal = Decimal("0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary ga aylantirish"""
        return {
            'order_id': self.order_id,
            'pair': self.pair.value,
            'side': self.side.value,
            'order_type': self.order_type.value,
            'amount': str(self.amount),
            'price': str(self.price),
            'stop_loss': str(self.stop_loss) if self.stop_loss else None,
            'take_profit': str(self.take_profit) if self.take_profit else None,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'filled_amount': str(self.filled_amount)
        }


@dataclass
class Trade:
    """Yakunlangan savdo"""
    trade_id: str
    order: Order
    open_price: Decimal
    close_price: Optional[Decimal] = None
    open_time: datetime = field(default_factory=datetime.now)
    close_time: Optional[datetime] = None
    profit_loss: Optional[Decimal] = None
    commission: Decimal = Decimal("0")
    swap: Decimal = Decimal("0")
    status: str = "Open"
    
    def calculate_pnl(self, current_price: Decimal) -> Decimal:
        """P&L hisoblash"""
        if self.status != "Open":
            return self.profit_loss or Decimal("0")
        
        if self.order.side == TradeSide.BUY:
            pnl = (current_price - self.open_price) * self.order.amount * Decimal("100000")
        else:
            pnl = (self.open_price - current_price) * self.order.amount * Decimal("100000")
        
        return pnl - self.commission - self.swap
    
    def close_trade(self, close_price: Decimal) -> None:
        """Savdoni yopish"""
        self.close_price = close_price
        self.close_time = datetime.now()
        self.profit_loss = self.calculate_pnl(close_price)
        self.status = "Closed"
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary ga aylantirish"""
        return {
            'trade_id': self.trade_id,
            'pair': self.order.pair.value,
            'side': self.order.side.value,
            'amount': str(self.order.amount),
            'open_price': str(self.open_price),
            'close_price': str(self.close_price) if self.close_price else None,
            'open_time': self.open_time.isoformat(),
            'close_time': self.close_time.isoformat() if self.close_time else None,
            'profit_loss': str(self.profit_loss) if self.profit_loss else None,
            'commission': str(self.commission),
            'swap': str(self.swap),
            'status': self.status
        }


@dataclass
class EconomicEvent:
    """Iqtisodiy voqea"""
    event_id: str
    title: str
    country: str
    currency: str
    impact: str  # High, Medium, Low
    time: datetime
    actual: Optional[str] = None
    forecast: Optional[str] = None
    previous: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary ga aylantirish"""
        return {
            'event_id': self.event_id,
            'title': self.title,
            'country': self.country,
            'currency': self.currency,
            'impact': self.impact,
            'time': self.time.isoformat(),
            'actual': self.actual,
            'forecast': self.forecast,
            'previous': self.previous,
            'description': self.description
        }


class ForexIntegration:
    """Forex integratsiya sinfi"""
    
    def __init__(self, account_id: str = "FX_ACCOUNT_001"):
        """
        Args:
            account_id: Hisob raqami
        """
        self.account_id = account_id
        self.active_orders: Dict[str, Order] = {}
        self.active_trades: Dict[str, Trade] = {}
        self.completed_trades: Dict[str, Trade] = {}
        self.order_counter = 1
        self.trade_counter = 1
        
        # Asosiy narxlar (base rates) - simulyatsiya
        self.base_rates = {
            # Major pairs
            CurrencyPair.EURUSD: Decimal("1.0845"),
            CurrencyPair.GBPUSD: Decimal("1.2567"),
            CurrencyPair.USDJPY: Decimal("149.82"),
            CurrencyPair.USDCHF: Decimal("0.8756"),
            CurrencyPair.USDCAD: Decimal("1.3678"),
            CurrencyPair.AUDUSD: Decimal("0.6587"),
            CurrencyPair.NZDUSD: Decimal("0.6123"),
            
            # Cross pairs
            CurrencyPair.EURJPY: Decimal("162.45"),
            CurrencyPair.EURGBP: Decimal("0.8634"),
            CurrencyPair.EURCHF: Decimal("0.9501"),
            CurrencyPair.EURCAD: Decimal("1.4842"),
            CurrencyPair.EURAUD: Decimal("1.6453"),
            CurrencyPair.EURNZD: Decimal("1.7698"),
            CurrencyPair.GBPJPY: Decimal("188.23"),
            CurrencyPair.GBPCHF: Decimal("1.1002"),
            CurrencyPair.GBPCAD: Decimal("1.7198"),
            CurrencyPair.GBPAUD: Decimal("2.0834"),
            CurrencyPair.GBPNZD: Decimal("2.2167"),
            CurrencyPair.CADJPY: Decimal("109.45"),
            CurrencyPair.CHFJPY: Decimal("171.12"),
            CurrencyPair.AUDJPY: Decimal("98.67"),
            CurrencyPair.AUDCHF: Decimal("0.5768"),
            CurrencyPair.AUDCAD: Decimal("0.9012"),
            CurrencyPair.AUDNZD: Decimal("1.0765"),
            CurrencyPair.NZDJPY: Decimal("91.78"),
            CurrencyPair.NZDCHF: Decimal("0.5365"),
            CurrencyPair.NZDCAD: Decimal("0.8376"),
            CurrencyPair.NZDAUD: Decimal("0.9291"),
            
            # Exotic pairs
            CurrencyPair.USDCNH: Decimal("7.2567"),
            CurrencyPair.USDTRY: Decimal("30.45"),
            CurrencyPair.USDZAR: Decimal("18.67"),
            CurrencyPair.USDMXN: Decimal("17.82"),
            CurrencyPair.USDBRL: Decimal("5.12"),
            CurrencyPair.USDSEK: Decimal("10.78"),
            CurrencyPair.USDNOK: Decimal("10.89"),
            CurrencyPair.USDDKK: Decimal("7.2345"),
            CurrencyPair.USDPLN: Decimal("4.1567"),
            CurrencyPair.USDHUF: Decimal("362.45")
        }
        
        logger.info(f"ForexIntegration initialized for account: {account_id}")
    
    def get_quote(self, pair: CurrencyPair) -> Quote:
        """
        Valyuta juftligi uchun real vaqt narx ma'lumotlari
        
        Args:
            pair: Valyuta juftligi
            
        Returns:
            Quote: Narx ma'lumotlari
        """
        base_price = self.base_rates.get(pair, Decimal("1.0000"))
        
        # Simulyatsiya: kichik narx o'zgarishlari (±0.5%)
        price_change = Decimal(str(random.uniform(-0.005, 0.005)))
        current_price = base_price * (Decimal("1") + price_change)
        
        # Spread hisoblash (pip asosida)
        if "JPY" in pair.value:
            spread_pips = Decimal(str(random.uniform(5, 20))) * Decimal("0.01")
        else:
            spread_pips = Decimal(str(random.uniform(0.5, 3.0))) * Decimal("0.0001")
        
        bid_price = current_price - spread_pips / Decimal("2")
        ask_price = current_price + spread_pips / Decimal("2")
        
        # 24 soatlik o'zgarish
        change_24h = current_price - base_price
        change_percent_24h = (change_24h / base_price) * Decimal("100")
        
        # 24 soatlik high/low
        high_24h = current_price * Decimal(str(1 + random.uniform(0, 0.01)))
        low_24h = current_price * Decimal(str(1 - random.uniform(0, 0.01)))
        
        # Volume (simulyatsiya)
        volume = random.randint(50000, 500000)
        
        return Quote(
            pair=pair,
            bid=round(bid_price, 5),
            ask=round(ask_price, 5),
            spread=round(spread_pips, 5),
            timestamp=datetime.now(),
            change_24h=round(change_24h, 5),
            change_percent_24h=round(change_percent_24h, 3),
            high_24h=round(high_24h, 5),
            low_24h=round(low_24h, 5),
            volume=volume
        )
    
    def get_historical_data(
        self, 
        pair: CurrencyPair, 
        timeframe: str = "1d",
        periods: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Valyuta juftligi uchun tarixiy ma'lumotlar
        
        Args:
            pair: Valyuta juftligi
            timeframe: Vaqt davri ("1m", "5m", "15m", "1h", "4h", "1d")
            periods: Davrlar soni
            
        Returns:
            List[Dict]: Tarixiy OHLCV ma'lumotlari
        """
        base_price = self.base_rates.get(pair, Decimal("1.0000"))
        historical_data = []
        
        # Timeframe转换
        timeframe_minutes = {
            "1m": 1, "5m": 5, "15m": 15, "30m": 30,
            "1h": 60, "4h": 240, "1d": 1440
        }.get(timeframe, 1440)
        
        current_time = datetime.now()
        
        for i in range(periods):
            timestamp = current_time - timedelta(minutes=timeframe_minutes * (periods - i))
            
            # Trend va tebranish bilan narx generatsiyasi
            trend_factor = Decimal(str(1 + random.uniform(-0.001, 0.001) * i * 0.1))
            volatility = Decimal(str(random.uniform(0.98, 1.02)))
            open_price = base_price * trend_factor * volatility
            
            # High/Low hisoblash
            price_range = open_price * Decimal(str(random.uniform(0.005, 0.025)))
            high = open_price + price_range
            low = open_price - price_range
            
            # Close price
            close_variance = Decimal(str(random.uniform(-0.5, 0.5))) * price_range
            close_price = open_price + close_variance
            
            # Volume
            volume = random.randint(100000, 1000000)
            
            historical_data.append({
                'timestamp': timestamp.isoformat(),
                'open': str(round(open_price, 5)),
                'high': str(round(high, 5)),
                'low': str(round(low, 5)),
                'close': str(round(close_price, 5)),
                'volume': volume,
                'timeframe': timeframe
            })
        
        return historical_data
    
    def convert_currency(
        self, 
        amount: Union[float, Decimal], 
        from_currency: str, 
        to_currency: str
    ) -> Dict[str, Any]:
        """
        Valyutani boshqa valyutaga aylantirish
        
        Args:
            amount: Miqdor
            from_currency: Manba valyuta (masalan, 'USD')
            to_currency: Maqsad valyuta (masalan, 'EUR')
            
        Returns:
            Dict: Aylantirish natijasi
        """
        amount = Decimal(str(amount))
        
        # To'g'ridan-to'g'ri juftlikni qidirish
        pair = self._find_currency_pair(from_currency, to_currency)
        
        if pair:
            # To'g'ridan-to'g'ri aylantirish
            quote = self.get_quote(pair)
            rate = quote.bid if from_currency == pair.value.split('/')[0] else Decimal("1") / quote.bid
            converted_amount = amount * rate
            
            return {
                'from_currency': from_currency,
                'to_currency': to_currency,
                'original_amount': str(amount),
                'converted_amount': str(round(converted_amount, 2)),
                'exchange_rate': str(round(rate, 6)),
                'timestamp': datetime.now().isoformat(),
                'pair': pair.value,
                'method': 'direct'
            }
        else:
            # Cross-rate orqali aylantirish (USD orqali)
            return self._cross_rate_conversion(amount, from_currency, to_currency)
    
    def _find_currency_pair(self, currency1: str, currency2: str) -> Optional[CurrencyPair]:
        """Valyuta juftligini topish"""
        pair_str = f"{currency1}/{currency2}"
        reverse_str = f"{currency2}/{currency1}"
        
        for pair in CurrencyPair:
            if pair.value == pair_str or pair.value == reverse_str:
                return pair
        return None
    
    def _cross_rate_conversion(
        self, 
        amount: Decimal, 
        from_currency: str, 
        to_currency: str
    ) -> Dict[str, Any]:
        """Cross-rate orqali aylantirish (USD orqali)"""
        # from_currency -> USD
        usd_pair_from = self._find_currency_pair(from_currency, "USD")
        if not usd_pair_from:
            raise ValueError(f"Valyuta juftligi topilmadi: {from_currency}/USD")
        
        quote_from = self.get_quote(usd_pair_from)
        if from_currency == "USD":
            usd_amount = amount
            from_rate = Decimal("1")
        elif from_currency == usd_pair_from.value.split('/')[0]:
            # currency/USD
            usd_amount = amount * quote_from.bid
            from_rate = quote_from.bid
        else:
            # USD/currency
            usd_amount = amount / quote_from.bid
            from_rate = Decimal("1") / quote_from.bid
        
        # USD -> to_currency
        usd_pair_to = self._find_currency_pair("USD", to_currency)
        if not usd_pair_to:
            raise ValueError(f"Valyuta juftligi topilmadi: USD/{to_currency}")
        
        quote_to = self.get_quote(usd_pair_to)
        if to_currency == "USD":
            final_amount = usd_amount
            to_rate = Decimal("1")
        elif to_currency == usd_pair_to.value.split('/')[1]:
            # USD/currency
            final_amount = usd_amount / quote_to.bid
            to_rate = Decimal("1") / quote_to.bid
        else:
            # currency/USD
            final_amount = usd_amount * quote_to.bid
            to_rate = quote_to.bid
        
        cross_rate = from_rate * to_rate
        
        return {
            'from_currency': from_currency,
            'to_currency': to_currency,
            'original_amount': str(amount),
            'converted_amount': str(round(final_amount, 2)),
            'exchange_rate': str(round(cross_rate, 6)),
            'timestamp': datetime.now().isoformat(),
            'pair': f"{from_currency}/{to_currency}",
            'method': 'cross_rate_via_USD',
            'usd_intermediate': str(round(usd_amount, 2))
        }
    
    def place_order(
        self,
        pair: CurrencyPair,
        side: TradeSide,
        order_type: OrderType,
        amount: Union[float, Decimal],
        price: Optional[Union[float, Decimal]] = None,
        stop_loss: Optional[Union[float, Decimal]] = None,
        take_profit: Optional[Union[float, Decimal]] = None
    ) -> Order:
        """
        Yangi savdo buyurtmasi joylashtirish
        
        Args:
            pair: Valyuta juftligi
            side: Sotib olish yoki sotish
            order_type: Buyurtma turi
            amount: Lot miqdori
            price: Narx (limit buyurtma uchun)
            stop_loss: Zarar to'xtatish
            take_profit: Foyda olish
            
        Returns:
            Order: Buyurtma obyekti
        """
        amount = Decimal(str(amount))
        
        if price:
            price = Decimal(str(price))
        if stop_loss:
            stop_loss = Decimal(str(stop_loss))
        if take_profit:
            take_profit = Decimal(str(take_profit))
        
        quote = self.get_quote(pair)
        
        # Narxni aniqlash
        if price is None:
            if order_type == OrderType.MARKET:
                price = quote.ask if side == TradeSide.BUY else quote.bid
            else:
                raise ValueError(f"{order_type.value} buyurtma uchun narx ko'rsatish kerak")
        
        # Buyurtma ID generatsiyasi
        order_id = f"ORD_{self.account_id}_{self.order_counter:06d}"
        self.order_counter += 1
        
        order = Order(
            order_id=order_id,
            pair=pair,
            side=side,
            order_type=order_type,
            amount=amount,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            timestamp=datetime.now(),
            status="Placed"
        )
        
        self.active_orders[order_id] = order
        
        # Market buyurtma bo'lsa, darhol bajarish
        if order_type == OrderType.MARKET:
            self._execute_order(order)
        
        logger.info(f"Buyurtma joylashtirildi: {order_id} - {pair.value} {side.value} {amount} lots @ {price}")
        
        return order
    
    def _execute_order(self, order: Order) -> Trade:
        """Buyurtmani bajarish"""
        # Savdo ID generatsiyasi
        trade_id = f"TRD_{self.account_id}_{self.trade_counter:06d}"
        self.trade_counter += 1
        
        # Komissiya (2$ per lot)
        commission = order.amount * Decimal("2")
        
        trade = Trade(
            trade_id=trade_id,
            order=order,
            open_price=order.price,
            open_time=datetime.now(),
            commission=commission,
            status="Open"
        )
        
        self.active_trades[trade_id] = trade
        order.status = "Executed"
        order.filled_amount = order.amount
        
        logger.info(f"Buyurtma bajarildi: {trade_id} - Foyda/zarar: ${trade.calculate_pnl(self.get_quote(order.pair).mid_price)}")
        
        return trade
    
    def close_trade(self, trade_id: str, price: Optional[Union[float, Decimal]] = None) -> Trade:
        """
        Savdoni yopish
        
        Args:
            trade_id: Savdo ID
            price: Yopish narxi (None bo'lsa, market narxdan)
            
        Returns:
            Trade: Yakunlangan savdo
        """
        if trade_id not in self.active_trades:
            raise ValueError(f"Savdo topilmadi: {trade_id}")
        
        trade = self.active_trades[trade_id]
        
        if trade.status == "Closed":
            raise ValueError("Savdo allaqachon yopilgan")
        
        # Narxni aniqlash
        if price is None:
            quote = self.get_quote(trade.order.pair)
            if trade.order.side == TradeSide.BUY:
                price = quote.bid  # Sotish narxi
            else:
                price = quote.ask  # Sotib olish narxi
        else:
            price = Decimal(str(price))
        
        # Swap hisoblash (kechasi saqlash uchun)
        hours_held = (datetime.now() - trade.open_time).total_seconds() / 3600
        swap = Decimal(str(hours_held / 24 * 1.5))  # 1.5$ per lot per day
        
        trade.swap = swap
        trade.close_trade(price)
        
        # Aktiv savdolardan yakunlanganlarga ko'chirish
        del self.active_trades[trade_id]
        self.completed_trades[trade_id] = trade
        
        logger.info(f"Savdo yopildi: {trade_id} - Final P&L: ${trade.profit_loss}")
        
        return trade
    
    def get_economic_calendar(self, days_ahead: int = 7) -> List[EconomicEvent]:
        """
        Iqtisodiy voqealar kalendarini olish
        
        Args:
            days_ahead: Qancha kun oldindan ko'rish
            
        Returns:
            List[EconomicEvent]: Iqtisodiy voqealar ro'yxati
        """
        events = []
        
        # Namuna iqtisodiy voqealar
        economic_events = [
            # Yuqori ta'sir
            {"title": "FED foiz stavkasi qarori", "country": "US", "currency": "USD", "impact": "High"},
            {"title": "ECB asosiy foiz stavkasi", "country": "EU", "currency": "EUR", "impact": "High"},
            {"title": "Bank of England foiz stavkasi", "country": "UK", "currency": "GBP", "impact": "High"},
            {"title": "Bank of Japan foiz stavkasi", "country": "Japan", "currency": "JPY", "impact": "High"},
            {"title": "Non-Farm Payrolls", "country": "US", "currency": "USD", "impact": "High"},
            {"title": "Ishsizlik darajasi", "country": "US", "currency": "USD", "impact": "High"},
            {"title": "GDP (YaIM) yakuniy", "country": "US", "currency": "USD", "impact": "High"},
            {"title": "Bank of Canada foiz stavkasi", "country": "Canada", "currency": "CAD", "impact": "High"},
            {"title": "RBA foiz stavkasi", "country": "Australia", "currency": "AUD", "impact": "High"},
            {"title": "RBNZ foiz stavkasi", "country": "New Zealand", "currency": "NZD", "impact": "High"},
            
            # O'rta ta'sir
            {"title": "CPI (iste'mol narxlari indeksi)", "country": "US", "currency": "USD", "impact": "Medium"},
            {"title": "PPI (ishlab chiqaruvchi narxlari indeksi)", "country": "US", "currency": "USD", "impact": "Medium"},
            {"title": "GDP (YaIM) boshlang'ich", "country": "EU", "currency": "EUR", "impact": "Medium"},
            {"title": "Ishsizlik darajasi", "country": "EU", "currency": "EUR", "impact": "Medium"},
            {"title": "Manufacturing PMI", "country": "US", "currency": "USD", "impact": "Medium"},
            {"title": "Services PMI", "country": "US", "currency": "USD", "impact": "Medium"},
            {"title": "Rochester tovarlar aylanmasi", "country": "UK", "currency": "GBP", "impact": "Medium"},
            {"title": "Ish bilan bandlik o'zgarishi", "country": "Australia", "currency": "AUD", "impact": "Medium"},
            {"title": "KPI (kalitli narxlar indeksi)", "country": "Japan", "currency": "JPY", "impact": "Medium"},
            {"title": "Tovarlar savdosi balansi", "country": "Canada", "currency": "CAD", "impact": "Medium"},
            
            # Past ta'sir
            {"title": "Retail Sales", "country": "US", "currency": "USD", "impact": "Low"},
            {"title": "Consumer Confidence", "country": "US", "currency": "USD", "impact": "Low"},
            {"title": "Factory Orders", "country": "US", "currency": "USD", "impact": "Low"},
            {"title": "Trade Balance", "country": "UK", "currency": "GBP", "impact": "Low"},
            {"title": "Public Sector Net Borrowing", "country": "UK", "currency": "GBP", "impact": "Low"},
            {"title": "Industrial Production", "country": "EU", "currency": "EUR", "impact": "Low"},
            {"title": "Construction Output", "country": "EU", "currency": "EUR", "impact": "Low"},
            {"title": "Retail Sales", "country": "Japan", "currency": "JPY", "impact": "Low"},
            {"title": "Machine Orders", "country": "Japan", "currency": "JPY", "impact": "Low"},
            {"title": "New Housing Sales", "country": "Canada", "currency": "CAD", "impact": "Low"}
        ]
        
        event_id_counter = 1000
        
        for day_offset in range(days_ahead):
            date = datetime.now() + timedelta(days=day_offset)
            
            # Har kuni 3-8 ta voqeani random tanlash
            num_events = random.randint(3, 8)
            day_events = random.sample(economic_events, min(num_events, len(economic_events)))
            
            for event_template in day_events:
                # Voqea vaqti (ish vaqti ichida)
                hour = random.choice([8, 9, 10, 11, 12, 13, 14, 15, 16])
                minute = random.choice([0, 15, 30, 45])
                
                event_time = datetime.combine(
                    date.date(),
                    datetime.min.time().replace(hour=hour, minute=minute)
                )
                
                event = EconomicEvent(
                    event_id=f"EVT_{event_id_counter}",
                    title=event_template['title'],
                    country=event_template['country'],
                    currency=event_template['currency'],
                    impact=event_template['impact'],
                    time=event_time,
                    forecast=f"{random.uniform(0.1, 5.0):.1f}%",
                    previous=f"{random.uniform(0.1, 5.0):.1f}%",
                    description=f"{event_template['currency']} valutasiga ta'sir qiluvchi iqtisodiy voqea"
                )
                
                events.append(event)
                event_id_counter += 1
        
        # Vaqt bo'yicha tartiblash
        events.sort(key=lambda x: x.time)
        
        logger.info(f"Iqtisodiy kalendar yangilandi: {len(events)} ta voqea")
        
        return events
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Hisob xulosasini olish
        
        Returns:
            Dict: Hisob ma'lumotlari
        """
        total_pnl = Decimal("0")
        total_commission = Decimal("0")
        total_swap = Decimal("0")
        
        # Aktiv savdolardan P&L
        for trade in self.active_trades.values():
            if trade.status == "Open":
                current_quote = self.get_quote(trade.order.pair)
                current_pnl = trade.calculate_pnl(current_quote.mid_price)
                total_pnl += current_pnl
                total_commission += trade.commission
                total_swap += trade.swap
        
        # Yakunlangan savdolardan P&L
        completed_pnl = Decimal("0")
        for trade in self.completed_trades.values():
            if trade.profit_loss:
                completed_pnl += trade.profit_loss
                total_commission += trade.commission
                total_swap += trade.swap
        
        # Asosiy balans (simulyatsiya)
        initial_balance = Decimal("10000.00")
        balance = initial_balance + completed_pnl
        equity = balance + total_pnl
        
        return {
            'account_id': self.account_id,
            'balance': str(round(balance, 2)),
            'equity': str(round(equity, 2)),
            'margin': "0.00",  # Hozircha leverage ishlatmaymiz
            'free_margin': str(round(equity, 2)),
            'open_trades_pnl': str(round(total_pnl, 2)),
            'total_pnl': str(round(completed_pnl, 2)),
            'total_commission': str(round(total_commission, 2)),
            'total_swap': str(round(total_swap, 2)),
            'open_trades_count': len(self.active_trades),
            'pending_orders_count': len(self.active_orders),
            'currency': 'USD',
            'leverage': '1:100',
            'margin_level': "0.00"
        }
    
    def get_open_trades(self) -> List[Dict[str, Any]]:
        """
        Ochiq savdolarni olish
        
        Returns:
            List[Dict]: Ochiq savdolar ro'yxati
        """
        open_trades = []
        
        for trade in self.active_trades.values():
            if trade.status == "Open":
                quote = self.get_quote(trade.order.pair)
                current_pnl = trade.calculate_pnl(quote.mid_price)
                
                open_trades.append({
                    'trade_id': trade.trade_id,
                    'pair': trade.order.pair.value,
                    'side': trade.order.side.value,
                    'amount': str(trade.order.amount),
                    'open_price': str(trade.open_price),
                    'current_price': str(quote.mid_price),
                    'pnl': str(round(current_pnl, 2)),
                    'open_time': trade.open_time.isoformat(),
                    'stop_loss': str(trade.order.stop_loss) if trade.order.stop_loss else None,
                    'take_profit': str(trade.order.take_profit) if trade.order.take_profit else None,
                    'commission': str(trade.commission),
                    'swap': str(trade.swap)
                })
        
        # P&L bo'yicha tartiblash
        open_trades.sort(key=lambda x: float(x['pnl']), reverse=True)
        
        return open_trades
    
    def get_supported_pairs(self) -> List[str]:
        """
        Qo'llab-quvvatlanadigan valyuta juftliklari
        
        Returns:
            List[str]: Valyuta juftliklari ro'yxati
        """
        pairs = [pair.value for pair in CurrencyPair]
        
        # Kategoriyalar bo'yicha guruhlash
        return {
            'total_count': len(pairs),
            'major_pairs': [p.value for p in CurrencyPair if p in [
                CurrencyPair.EURUSD, CurrencyPair.GBPUSD, CurrencyPair.USDJPY,
                CurrencyPair.USDCHF, CurrencyPair.USDCAD, CurrencyPair.AUDUSD,
                CurrencyPair.NZDUSD
            ]],
            'cross_pairs': [p.value for p in CurrencyPair if p not in [
                CurrencyPair.EURUSD, CurrencyPair.GBPUSD, CurrencyPair.USDJPY,
                CurrencyPair.USDCHF, CurrencyPair.USDCAD, CurrencyPair.AUDUSD,
                CurrencyPair.NZDUSD
            ] and not any(exotic in p.value for exotic in ['CNH', 'TRY', 'ZAR', 'MXN', 'BRL', 'SEK', 'NOK', 'DKK', 'PLN', 'HUF'])],
            'exotic_pairs': [p.value for p in CurrencyPair if any(exotic in p.value for exotic in ['CNH', 'TRY', 'ZAR', 'MXN', 'BRL', 'SEK', 'NOK', 'DKK', 'PLN', 'HUF'])],
            'all_pairs': pairs
        }
    
    def get_market_overview(self) -> Dict[str, Any]:
        """
        Bozor umumiy ko'rinishi
        
        Returns:
            Dict: Bozor ma'lumotlari
        """
        overview = {
            'timestamp': datetime.now().isoformat(),
            'market_session': self._get_current_session(),
            'total_pairs': len(CurrencyPair),
            'quotes': {},
            'top_movers': [],
            'market_sentiment': 'neutral'
        }
        
        # Asosiy juftliklar narxlarini olish
        major_pairs = [
            CurrencyPair.EURUSD, CurrencyPair.GBPUSD, CurrencyPair.USDJPY,
            CurrencyPair.USDCHF, CurrencyPair.USDCAD, CurrencyPair.AUDUSD,
            CurrencyPair.NZDUSD
        ]
        
        quote_data = []
        for pair in major_pairs:
            quote = self.get_quote(pair)
            quote_dict = quote.to_dict()
            overview['quotes'][pair.value] = quote_dict
            
            quote_data.append({
                'pair': pair.value,
                'change_percent': float(quote.change_percent_24h),
                'volume': quote.volume
            })
        
        # Eng ko'p harakat qilayotganlar
        quote_data.sort(key=lambda x: abs(x['change_percent']), reverse=True)
        overview['top_movers'] = quote_data[:5]
        
        # Bozor kayfiyati
        positive_movers = sum(1 for q in quote_data if q['change_percent'] > 0)
        negative_movers = sum(1 for q in quote_data if q['change_percent'] < 0)
        
        if positive_movers > negative_movers:
            overview['market_sentiment'] = 'bullish'
        elif negative_movers > positive_movers:
            overview['market_sentiment'] = 'bearish'
        
        return overview
    
    def _get_current_session(self) -> Dict[str, Any]:
        """Joriy bozor sessiyasini aniqlash"""
        now = datetime.now()
        utc_hour = now.hour
        
        # Forex sessiyalari (UTC)
        sessions = {
            'Sydney': {'open': 22, 'close': 6},
            'Tokyo': {'open': 0, 'close': 9},
            'London': {'open': 8, 'close': 17},
            'New_York': {'open': 13, 'close': 22}
        }
        
        current_sessions = []
        
        for session_name, times in sessions.items():
            if times['open'] > times['close']:  # Kechqurun boshlab, ertaga tugaydigan sessiya
                if utc_hour >= times['open'] or utc_hour < times['close']:
                    current_sessions.append(session_name)
            else:  # Bir kun ichida
                if times['open'] <= utc_hour < times['close']:
                    current_sessions.append(session_name)
        
        return {
            'current_sessions': current_sessions,
            'next_session': self._get_next_session(utc_hour),
            'utc_time': now.isoformat()
        }
    
    def _get_next_session(self, current_hour: int) -> str:
        """Keyingi sessiyani aniqlash"""
        session_times = [
            ('Sydney', 22), ('Tokyo', 0), ('London', 8), ('New_York', 13)
        ]
        
        for session, start_hour in session_times:
            if current_hour < start_hour:
                return session
        
        # Ertaga birinchi sessiya
        return 'Sydney'
    
    def calculate_pip_value(
        self,
        pair: CurrencyPair,
        lot_size: Union[float, Decimal],
        account_currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Pip qiymatini hisoblash
        
        Args:
            pair: Valyuta juftligi
            lot_size: Lot hajmi
            account_currency: Hisob valyutasi
            
        Returns:
            Dict: Pip ma'lumotlari
        """
        lot_size = Decimal(str(lot_size))
        
        # Standard lot = 100,000 units
        contract_size = lot_size * Decimal("100000")
        
        # Pip o'lchami
        is_jpy_pair = "JPY" in pair.value
        pip_size = Decimal("0.01") if is_jpy_pair else Decimal("0.0001")
        
        # Pip qiymati quote valyutada
        pip_value_quote = contract_size * pip_size
        
        # Account valyutaga aylantirish
        quote_currency = pair.value.split("/")[1]
        
        if quote_currency == account_currency:
            pip_value_account = pip_value_quote
        else:
            # Conversion kerak
            try:
                conversion = self.convert_currency(
                    float(pip_value_quote),
                    quote_currency,
                    account_currency
                )
                pip_value_account = Decimal(conversion['converted_amount'])
            except:
                pip_value_account = pip_value_quote  # Fallback
        
        return {
            'pair': pair.value,
            'lot_size': str(lot_size),
            'contract_size': str(contract_size),
            'pip_size': str(pip_size),
            'pip_value_quote_currency': str(pip_value_quote),
            'pip_value_account_currency': str(pip_value_account),
            'quote_currency': quote_currency,
            'account_currency': account_currency
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Savdo statistikasi"""
        all_trades = list(self.active_trades.values()) + list(self.completed_trades.values())
        
        if not all_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': '0%',
                'total_pnl': '0.00',
                'average_win': '0.00',
                'average_loss': '0.00',
                'largest_win': '0.00',
                'largest_loss': '0.00'
            }
        
        closed_trades = [t for t in self.completed_trades.values() if t.profit_loss is not None]
        
        if not closed_trades:
            return {'message': 'Yakunlangan savdolar yo\'q'}
        
        # Statistika hisoblash
        winning_trades = [t for t in closed_trades if t.profit_loss > 0]
        losing_trades = [t for t in closed_trades if t.profit_loss < 0]
        
        total_pnl = sum(t.profit_loss for t in closed_trades)
        win_rate = (len(winning_trades) / len(closed_trades)) * 100 if closed_trades else 0
        
        average_win = sum(t.profit_loss for t in winning_trades) / len(winning_trades) if winning_trades else 0
        average_loss = sum(t.profit_loss for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        largest_win = max((t.profit_loss for t in closed_trades), default=0)
        largest_loss = min((t.profit_loss for t in closed_trades), default=0)
        
        return {
            'total_trades': len(all_trades),
            'open_trades': len(self.active_trades),
            'closed_trades': len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': f"{win_rate:.2f}%",
            'total_pnl': str(round(total_pnl, 2)),
            'average_win': str(round(average_win, 2)),
            'average_loss': str(round(average_loss, 2)),
            'largest_win': str(round(largest_win, 2)),
            'largest_loss': str(round(largest_loss, 2)),
            'total_commission': str(round(sum(t.commission for t in all_trades), 2)),
            'total_swap': str(round(sum(t.swap for t in all_trades), 2))
        }


# Test va foydalanish misollari
if __name__ == "__main__":
    # Forex integratsiya obyektini yaratish
    forex = ForexIntegration(account_id="DEMO_001")
    
    print("=" * 60)
    print("FOREX INTEGRATION TEST")
    print("=" * 60)
    
    # 1. Mavjud valyuta juftliklari
    print("\n1. MAVJUD VALYUTA JUFTLIKLARI:")
    pairs_info = forex.get_supported_pairs()
    print(f"Jami: {pairs_info['total_count']} juftlik")
    print(f"Major: {len(pairs_info['major_pairs'])} ta")
    print(f"Cross: {len(pairs_info['cross_pairs'])} ta") 
    print(f"Exotic: {len(pairs_info['exotic_pairs'])} ta")
    
    print("\nMajor juftliklar:")
    for pair in pairs_info['major_pairs']:
        print(f"  • {pair}")
    
    # 2. Narx ma'lumotlari
    print("\n2. NARX MA'LUMOTLARI:")
    major_pairs = [CurrencyPair.EURUSD, CurrencyPair.GBPUSD, CurrencyPair.USDJPY]
    
    for pair in major_pairs:
        quote = forex.get_quote(pair)
        print(f"{quote.pair.value}:")
        print(f"  Bid: {quote.bid} | Ask: {quote.ask} | Spread: {quote.spread}")
        print(f"  24h o'zgarish: {quote.change_percent_24h}% | Volume: {quote.volume:,}")
    
    # 3. Tarixiy ma'lumotlar
    print("\n3. TARIXIY MA'LUMOTLAR (EUR/USD, oxirgi 5 kun):")
    historical = forex.get_historical_data(CurrencyPair.EURUSD, "1d", 5)
    for day in historical:
        print(f"{day['timestamp'][:10]}: O={day['open']}, H={day['high']}, L={day['low']}, C={day['close']}")
    
    # 4. Valyuta aylantirish
    print("\n4. VALYUTA AYLANTIRISH:")
    conversions = [
        ("USD", "EUR", 1000),
        ("GBP", "JPY", 500),
        ("AUD", "USD", 2000),
        ("CHF", "CAD", 800)
    ]
    
    for from_curr, to_curr, amount in conversions:
        conversion = forex.convert_currency(amount, from_curr, to_curr)
        print(f"{amount} {from_curr} = {conversion['converted_amount']} {to_curr}")
        print(f"  Kurs: {conversion['exchange_rate']} | Method: {conversion['method']}")
    
    # 5. Savdo buyurtmasi
    print("\n5. SAVDO BUYURTMASI:")
    order = forex.place_order(
        pair=CurrencyPair.EURUSD,
        side=TradeSide.BUY,
        order_type=OrderType.MARKET,
        amount=1.0  # 1 lot
    )
    print(f"Buyurtma ID: {order.order_id}")
    print(f"Narx: {order.price} | Status: {order.status}")
    
    # 6. Ochiq savdolar
    print("\n6. OCHIQ SAVDOLAR:")
    open_trades = forex.get_open_trades()
    for trade in open_trades:
        print(f"ID: {trade['trade_id']}")
        print(f"  {trade['pair']} {trade['side']} {trade['amount']} lots")
        print(f"  Open: {trade['open_price']} | Current: {trade['current_price']}")
        print(f"  P&L: ${trade['pnl']} | Commission: ${trade['commission']}")
    
    # 7. Hisob xulosasi
    print("\n7. HISOB XULOSASI:")
    account = forex.get_account_summary()
    print(f"Balans: ${account['balance']} | Equity: ${account['equity']}")
    print(f"Ochiq savdolar P&L: ${account['open_trades_pnl']}")
    print(f"Umumiy komissiya: ${account['total_commission']}")
    print(f"Ochiq savdolar: {account['open_trades_count']} ta")
    
    # 8. Iqtisodiy kalendar
    print("\n8. IQTISODIY KALENDAR (keyingi 3 kun):")
    events = forex.get_economic_calendar(3)
    for event in events[:8]:  # Faqat 8 ta voqea
        print(f"{event.time.strftime('%m-%d %H:%M')} - {event.title}")
        print(f"  {event.country} ({event.currency}) | Impact: {event.impact}")
    
    # 9. Bozor ko'rinishi
    print("\n9. BOZOR UMUMIY KO'RINISH:")
    overview = forex.get_market_overview()
    print(f"Sessiya: {', '.join(overview['market_session']['current_sessions'])}")
    print(f"Kayfiyat: {overview['market_sentiment']}")
    print("Top movers:")
    for mover in overview['top_movers']:
        print(f"  {mover['pair']}: {mover['change_percent']:.2f}%")
    
    # 10. Pip qiymati hisoblash
    print("\n10. PIP QIYMATI:")
    pip_info = forex.calculate_pip_value(CurrencyPair.EURUSD, 1.0)
    print(f"{pip_info['pair']} - 1 lot:")
    print(f"  Pip size: {pip_info['pip_size']}")
    print(f"  Pip value: {pip_info['pip_value_account_currency']} {pip_info['account_currency']}")
    
    # 11. Statistika
    print("\n11. SAVDO STATISTIKASI:")
    stats = forex.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("TEST YAKUNLANDI")
    print("=" * 60)