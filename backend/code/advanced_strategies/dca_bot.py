"""
DCA (Dollar Cost Averaging) Bot - Smart Entry Timing & Adaptive DCA
====================================================================

DCA strategiyasi - ma'lum vaqt oralig'ida doimiy ravishda aktivni sotib olish.
Bu strategiya narx o'zgaruvchanligini kamaytiradi va o'rtacha kirish narxini optimallashtiradi.

Asosiy xususiyatlar:
- Fixed interval DCA
- Adaptive DCA (trend va volatility asosida)
- Smart entry timing (dip buying)
- Dynamic amount adjustment
- Portfolio rebalancing
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DCAConfig:
    """DCA bot konfiguratsiyasi"""
    symbol: str
    base_currency: str = 'USDT'
    
    # Fixed DCA parameters
    fixed_amount: float = 100.0  # Har safar sotib olinadigan miqdor
    interval_hours: int = 24  # Sotib olish intervali (soat)
    
    # Adaptive DCA parameters
    use_adaptive: bool = True
    min_amount: float = 50.0
    max_amount: float = 200.0
    
    # Smart entry
    use_dip_buying: bool = True
    dip_threshold: float = -2.0  # Dip sifatida -2% drop
    
    # Portfolio management
    total_budget: float = 10000.0  # Jami budget
    max_position_size: float = 5000.0  # Maksimal pozitsiya hajmi


@dataclass
class DCAOrder:
    """DCA order ma'lumotlari"""
    timestamp: datetime
    price: float
    amount_base: float  # USDT miqdori
    amount_asset: float  # Sotib olingan asset miqdori
    order_type: str = 'fixed'  # 'fixed', 'adaptive', 'dip'
    executed: bool = False


class DCABot:
    """
    Dollar Cost Averaging Bot
    
    Avtomatik ravishda ma'lum vaqt oralig'ida asset sotib olish,
    trend va volatilityga qarab adaptive sozlamalar.
    """
    
    def __init__(self, config: DCAConfig):
        self.config = config
        self.orders: List[DCAOrder] = []
        self.portfolio = {
            'total_invested': 0.0,
            'total_asset': 0.0,
            'average_price': 0.0,
            'current_value': 0.0,
            'profit_loss': 0.0,
            'profit_loss_pct': 0.0
        }
        
        self.last_order_time: Optional[datetime] = None
        self.price_history: List[Tuple[datetime, float]] = []
        
        logger.info(f"DCA Bot initialized for {config.symbol}")
        logger.info(f"Budget: ${config.total_budget:.2f}, Fixed amount: ${config.fixed_amount:.2f}")
    
    def calculate_volatility(
        self,
        lookback_periods: int = 20
    ) -> float:
        """
        Volatility hisoblash
        
        Args:
            lookback_periods: Necha davr orqaga qarash
            
        Returns:
            Volatility (%)
        """
        if len(self.price_history) < lookback_periods:
            return 0.0
        
        recent_prices = [price for _, price in self.price_history[-lookback_periods:]]
        returns = np.diff(recent_prices) / recent_prices[:-1]
        volatility = np.std(returns) * 100
        
        return volatility
    
    def calculate_trend(
        self,
        lookback_periods: int = 50
    ) -> Tuple[float, str]:
        """
        Trend aniqlash
        
        Args:
            lookback_periods: Necha davr orqaga qarash
            
        Returns:
            (trend_strength, trend_direction)
        """
        if len(self.price_history) < lookback_periods:
            return 0.0, 'neutral'
        
        recent_prices = [price for _, price in self.price_history[-lookback_periods:]]
        
        # Linear regression
        x = np.arange(len(recent_prices))
        slope, intercept = np.polyfit(x, recent_prices, 1)
        
        # Trend strength as percentage
        trend_strength = (slope / recent_prices[0]) * 100 * len(recent_prices)
        
        # Determine direction
        if trend_strength > 2:
            direction = 'uptrend'
        elif trend_strength < -2:
            direction = 'downtrend'
        else:
            direction = 'neutral'
        
        return trend_strength, direction
    
    def detect_dip(
        self,
        current_price: float,
        lookback_periods: int = 10
    ) -> Tuple[bool, float]:
        """
        Dip (narx tushishi) aniqlash
        
        Args:
            current_price: Joriy narx
            lookback_periods: Necha davr orqaga qarash
            
        Returns:
            (is_dip, drop_percentage)
        """
        if len(self.price_history) < lookback_periods:
            return False, 0.0
        
        recent_prices = [price for _, price in self.price_history[-lookback_periods:]]
        max_recent_price = max(recent_prices)
        
        drop_pct = ((current_price - max_recent_price) / max_recent_price) * 100
        
        is_dip = drop_pct <= self.config.dip_threshold
        
        return is_dip, drop_pct
    
    def calculate_adaptive_amount(
        self,
        current_price: float,
        volatility: float,
        trend_strength: float
    ) -> float:
        """
        Adaptive DCA miqdorini hisoblash
        
        Args:
            current_price: Joriy narx
            volatility: Volatility (%)
            trend_strength: Trend kuchi (%)
            
        Returns:
            Sotib olish miqdori ($)
        """
        base_amount = self.config.fixed_amount
        
        # Adjust based on volatility
        # Higher volatility = buy more (opportunity)
        volatility_factor = 1.0 + (volatility / 20.0)  # +5% volatility = +25% amount
        
        # Adjust based on trend
        # Downtrend = buy more (accumulate at lower prices)
        # Uptrend = buy less (higher prices)
        if trend_strength < -2:  # Downtrend
            trend_factor = 1.0 + abs(trend_strength) / 20.0
        elif trend_strength > 2:  # Uptrend
            trend_factor = 1.0 - (trend_strength / 30.0)
        else:  # Neutral
            trend_factor = 1.0
        
        # Calculate adaptive amount
        adaptive_amount = base_amount * volatility_factor * trend_factor
        
        # Clamp to min/max
        adaptive_amount = max(
            self.config.min_amount,
            min(self.config.max_amount, adaptive_amount)
        )
        
        # Check budget constraints
        remaining_budget = self.config.total_budget - self.portfolio['total_invested']
        adaptive_amount = min(adaptive_amount, remaining_budget)
        
        # Check position size
        current_position_value = self.portfolio['total_asset'] * current_price
        if current_position_value >= self.config.max_position_size:
            adaptive_amount = 0.0
        
        return adaptive_amount
    
    def should_execute_dca(
        self,
        current_time: datetime
    ) -> bool:
        """
        DCA bajarilishi kerakligini tekshirish
        
        Args:
            current_time: Joriy vaqt
            
        Returns:
            True agar DCA bajarilishi kerak bo'lsa
        """
        if self.last_order_time is None:
            return True
        
        time_elapsed = current_time - self.last_order_time
        required_interval = timedelta(hours=self.config.interval_hours)
        
        return time_elapsed >= required_interval
    
    def execute_dca_order(
        self,
        current_price: float,
        current_time: datetime,
        order_type: str = 'fixed'
    ) -> Optional[DCAOrder]:
        """
        DCA order bajarish
        
        Args:
            current_price: Joriy narx
            current_time: Joriy vaqt
            order_type: Order turi ('fixed', 'adaptive', 'dip')
            
        Returns:
            Bajarilgan order yoki None
        """
        # Calculate amount based on type
        if order_type == 'adaptive':
            volatility = self.calculate_volatility()
            trend_strength, _ = self.calculate_trend()
            amount_usd = self.calculate_adaptive_amount(
                current_price, volatility, trend_strength
            )
        else:
            amount_usd = self.config.fixed_amount
            
            # Check budget
            remaining_budget = self.config.total_budget - self.portfolio['total_invested']
            amount_usd = min(amount_usd, remaining_budget)
        
        if amount_usd <= 0:
            logger.warning("Insufficient budget or max position size reached")
            return None
        
        # Calculate asset amount
        amount_asset = amount_usd / current_price
        
        # Create order
        order = DCAOrder(
            timestamp=current_time,
            price=current_price,
            amount_base=amount_usd,
            amount_asset=amount_asset,
            order_type=order_type,
            executed=True
        )
        
        # Update portfolio
        self.portfolio['total_invested'] += amount_usd
        self.portfolio['total_asset'] += amount_asset
        
        # Recalculate average price
        if self.portfolio['total_asset'] > 0:
            self.portfolio['average_price'] = (
                self.portfolio['total_invested'] / self.portfolio['total_asset']
            )
        
        # Add to orders
        self.orders.append(order)
        self.last_order_time = current_time
        
        logger.info(f"✅ DCA Order executed ({order_type})")
        logger.info(f"   Amount: ${amount_usd:.2f} @ ${current_price:.2f}")
        logger.info(f"   Asset acquired: {amount_asset:.6f}")
        logger.info(f"   New average price: ${self.portfolio['average_price']:.2f}")
        
        return order
    
    def update_portfolio_value(self, current_price: float):
        """
        Portfolio qiymatini yangilash
        
        Args:
            current_price: Joriy narx
        """
        self.portfolio['current_value'] = self.portfolio['total_asset'] * current_price
        self.portfolio['profit_loss'] = (
            self.portfolio['current_value'] - self.portfolio['total_invested']
        )
        
        if self.portfolio['total_invested'] > 0:
            self.portfolio['profit_loss_pct'] = (
                self.portfolio['profit_loss'] / self.portfolio['total_invested']
            ) * 100
    
    def process_price_update(
        self,
        current_price: float,
        current_time: datetime
    ) -> Optional[DCAOrder]:
        """
        Narx yangilanishini qayta ishlash va DCA qarorini qabul qilish
        
        Args:
            current_price: Joriy narx
            current_time: Joriy vaqt
            
        Returns:
            Bajarilgan order (agar mavjud bo'lsa)
        """
        # Add to price history
        self.price_history.append((current_time, current_price))
        
        # Update portfolio value
        self.update_portfolio_value(current_price)
        
        # Check for dip buying opportunity
        if self.config.use_dip_buying:
            is_dip, drop_pct = self.detect_dip(current_price)
            
            if is_dip:
                logger.info(f"🎯 Dip detected! Price dropped {drop_pct:.2f}%")
                return self.execute_dca_order(current_price, current_time, 'dip')
        
        # Check regular DCA schedule
        if self.should_execute_dca(current_time):
            if self.config.use_adaptive:
                return self.execute_dca_order(current_price, current_time, 'adaptive')
            else:
                return self.execute_dca_order(current_price, current_time, 'fixed')
        
        return None
    
    def rebalance_portfolio(
        self,
        target_allocation: Dict[str, float],
        current_prices: Dict[str, float]
    ) -> List[Dict]:
        """
        Portfolio rebalancing (multi-asset DCA uchun)
        
        Args:
            target_allocation: Target allocation {'BTC': 0.4, 'ETH': 0.3, 'USDT': 0.3}
            current_prices: Joriy narxlar {'BTC': 45000, 'ETH': 3000}
            
        Returns:
            Rebalancing orders
        """
        # Calculate current allocation
        total_value = sum(
            self.portfolio['total_asset'] * current_prices.get(self.config.symbol, 0)
            for symbol in target_allocation.keys()
        )
        
        rebalance_orders = []
        
        for symbol, target_pct in target_allocation.items():
            if symbol == self.config.base_currency:
                continue
            
            target_value = total_value * target_pct
            current_value = self.portfolio['total_asset'] * current_prices.get(symbol, 0)
            
            difference = target_value - current_value
            
            if abs(difference) > total_value * 0.05:  # 5% threshold
                if difference > 0:
                    # Buy
                    action = 'buy'
                    amount = difference
                else:
                    # Sell
                    action = 'sell'
                    amount = abs(difference)
                
                rebalance_orders.append({
                    'symbol': symbol,
                    'action': action,
                    'amount_usd': amount,
                    'current_allocation': current_value / total_value,
                    'target_allocation': target_pct
                })
        
        return rebalance_orders
    
    def get_performance_metrics(self) -> Dict:
        """Performance ko'rsatkichlarini olish"""
        total_orders = len(self.orders)
        
        if total_orders == 0:
            return {
                'total_orders': 0,
                'total_invested': 0,
                'total_asset': 0,
                'average_price': 0,
                'current_value': 0,
                'profit_loss': 0,
                'profit_loss_pct': 0
            }
        
        # Order types breakdown
        order_types = {'fixed': 0, 'adaptive': 0, 'dip': 0}
        for order in self.orders:
            order_types[order.order_type] += 1
        
        # Calculate additional metrics
        prices = [order.price for order in self.orders]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        return {
            'total_orders': total_orders,
            'order_types': order_types,
            'total_invested': self.portfolio['total_invested'],
            'total_asset': self.portfolio['total_asset'],
            'average_price': self.portfolio['average_price'],
            'current_value': self.portfolio['current_value'],
            'profit_loss': self.portfolio['profit_loss'],
            'profit_loss_pct': self.portfolio['profit_loss_pct'],
            'min_buy_price': min_price,
            'max_buy_price': max_price,
            'price_range_pct': ((max_price - min_price) / min_price * 100) if min_price > 0 else 0
        }


# Multi-Asset DCA Strategy
class MultiAssetDCABot:
    """
    Multiple asset DCA strategiyasi
    
    Bir nechta aktivlar bo'yicha DCA strategiyasini boshqaradi
    """
    
    def __init__(
        self,
        total_budget: float,
        asset_allocation: Dict[str, float]
    ):
        """
        Args:
            total_budget: Jami budget
            asset_allocation: Asset allocation {'BTC': 0.4, 'ETH': 0.3, 'BNB': 0.3}
        """
        self.total_budget = total_budget
        self.asset_allocation = asset_allocation
        self.bots: Dict[str, DCABot] = {}
        
        # Create DCA bot for each asset
        for symbol, allocation_pct in asset_allocation.items():
            asset_budget = total_budget * allocation_pct
            
            config = DCAConfig(
                symbol=symbol,
                fixed_amount=asset_budget / 100,  # 100 orders over time
                interval_hours=24,
                use_adaptive=True,
                total_budget=asset_budget,
                max_position_size=asset_budget * 0.8
            )
            
            self.bots[symbol] = DCABot(config)
        
        logger.info(f"Multi-Asset DCA Bot initialized with {len(self.bots)} assets")
    
    def process_market_update(
        self,
        prices: Dict[str, float],
        timestamp: datetime
    ) -> Dict[str, Optional[DCAOrder]]:
        """
        Bozor yangilanishini qayta ishlash
        
        Args:
            prices: Narxlar {'BTC': 45000, 'ETH': 3000}
            timestamp: Vaqt
            
        Returns:
            Bajarilgan orderlar
        """
        executed_orders = {}
        
        for symbol, bot in self.bots.items():
            if symbol in prices:
                order = bot.process_price_update(prices[symbol], timestamp)
                if order:
                    executed_orders[symbol] = order
        
        return executed_orders
    
    def get_total_portfolio_value(
        self,
        current_prices: Dict[str, float]
    ) -> Dict:
        """Jami portfolio qiymatini hisoblash"""
        total_invested = 0.0
        total_value = 0.0
        
        asset_values = {}
        
        for symbol, bot in self.bots.items():
            if symbol in current_prices:
                bot.update_portfolio_value(current_prices[symbol])
                
                total_invested += bot.portfolio['total_invested']
                total_value += bot.portfolio['current_value']
                
                asset_values[symbol] = {
                    'invested': bot.portfolio['total_invested'],
                    'current_value': bot.portfolio['current_value'],
                    'profit_loss': bot.portfolio['profit_loss'],
                    'profit_loss_pct': bot.portfolio['profit_loss_pct']
                }
        
        total_profit_loss = total_value - total_invested
        total_profit_loss_pct = (
            (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        )
        
        return {
            'total_invested': total_invested,
            'total_value': total_value,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_pct': total_profit_loss_pct,
            'assets': asset_values
        }


# Example usage
def main():
    """Test DCA bot"""
    import random
    
    # Configuration
    config = DCAConfig(
        symbol='BTC/USDT',
        fixed_amount=100,
        interval_hours=24,
        use_adaptive=True,
        use_dip_buying=True,
        total_budget=10000,
        max_position_size=5000
    )
    
    # Initialize bot
    bot = DCABot(config)
    
    # Simulate price movements over 100 days
    base_price = 45000
    current_time = datetime.now()
    
    for day in range(100):
        # Random price movement
        price_change = random.uniform(-1000, 1000)
        current_price = max(base_price + price_change, 30000)  # Floor at 30k
        base_price = current_price
        
        # Process update
        order = bot.process_price_update(current_price, current_time)
        
        if order:
            print(f"Day {day}: Order executed @ ${current_price:.2f}")
        
        # Move to next day
        current_time += timedelta(days=1)
    
    # Final update
    bot.update_portfolio_value(current_price)
    
    # Show results
    metrics = bot.get_performance_metrics()
    print("\n" + "="*60)
    print("DCA BOT PERFORMANCE")
    print("="*60)
    print(f"Total orders: {metrics['total_orders']}")
    print(f"  Fixed: {metrics['order_types']['fixed']}")
    print(f"  Adaptive: {metrics['order_types']['adaptive']}")
    print(f"  Dip: {metrics['order_types']['dip']}")
    print(f"\nTotal invested: ${metrics['total_invested']:.2f}")
    print(f"Current value: ${metrics['current_value']:.2f}")
    print(f"Average price: ${metrics['average_price']:.2f}")
    print(f"Current price: ${current_price:.2f}")
    print(f"\nProfit/Loss: ${metrics['profit_loss']:.2f} ({metrics['profit_loss_pct']:.2f}%)")
    print(f"Price range: ${metrics['min_buy_price']:.2f} - ${metrics['max_buy_price']:.2f}")
    print("="*60)


if __name__ == '__main__':
    main()
