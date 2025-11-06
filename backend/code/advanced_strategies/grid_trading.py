"""
Grid Trading Strategy - Dynamic Grid Adjustment & Multi-Timeframe
===================================================================

Grid trading strategiyasi - narx ma'lum diapazon ichida harakat qilganda
avtomatik ravishda buy va sell orderlar joylashtiradigan strategiya.

Asosiy xususiyatlar:
- Dynamic grid level adjustment
- Multi-timeframe grid analysis
- Volatility-based grid spacing
- Profit target optimization
- Risk management integration
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GridLevel:
    """Grid darajasi"""
    price: float
    order_type: str  # 'buy' or 'sell'
    quantity: float
    status: str = 'pending'  # 'pending', 'filled', 'cancelled'
    order_id: Optional[str] = None
    filled_at: Optional[datetime] = None


@dataclass
class GridConfig:
    """Grid trading konfiguratsiyasi"""
    symbol: str
    base_price: float  # Boshlang'ich narx
    price_range_lower: float  # Pastki narx chegarasi
    price_range_upper: float  # Yuqori narx chegarasi
    grid_levels: int  # Grid darajalari soni
    order_amount: float  # Har bir order miqdori
    take_profit_per_grid: float  # Har bir grid uchun foyda (%)
    
    # Dynamic parameters
    use_dynamic_spacing: bool = True
    volatility_multiplier: float = 1.0
    rebalance_interval: int = 3600  # Seconds


class GridTradingStrategy:
    """
    Grid Trading Strategy Implementation
    
    Grid trading - narx ma'lum diapazonida grid (to'r) hosil qilib,
    narx grid darajalarini kesib o'tganda avtomatik savdo qilish.
    """
    
    def __init__(self, config: GridConfig):
        self.config = config
        self.grid_levels: List[GridLevel] = []
        self.active_orders: Dict[str, GridLevel] = {}
        self.completed_trades: List[Dict] = []
        self.total_profit = 0.0
        
        # Performance metrics
        self.metrics = {
            'total_trades': 0,
            'profitable_trades': 0,
            'total_buy_volume': 0.0,
            'total_sell_volume': 0.0,
            'largest_profit': 0.0,
            'largest_loss': 0.0
        }
        
        # Initialize grid
        self._initialize_grid()
        
        logger.info(f"Grid Trading Strategy initialized for {config.symbol}")
        logger.info(f"Grid levels: {config.grid_levels}, Range: ${config.price_range_lower:.2f} - ${config.price_range_upper:.2f}")
    
    def _calculate_volatility(self, price_history: List[float], period: int = 20) -> float:
        """
        Volatility hisoblash (Standard Deviation)
        
        Args:
            price_history: Narxlar tarixi
            period: Hisoblash davri
            
        Returns:
            Volatility qiymati
        """
        if len(price_history) < period:
            return 0.0
        
        recent_prices = price_history[-period:]
        returns = np.diff(recent_prices) / recent_prices[:-1]
        volatility = np.std(returns) * 100  # Percentage
        
        return volatility
    
    def _calculate_grid_spacing(
        self,
        price_range: float,
        grid_levels: int,
        volatility: Optional[float] = None
    ) -> List[float]:
        """
        Grid spacing hisoblash
        
        Args:
            price_range: Narx diapazoni
            grid_levels: Grid darajalari soni
            volatility: Volatility (agar dynamic spacing ishlatilsa)
            
        Returns:
            Grid spacings ro'yxati
        """
        if not self.config.use_dynamic_spacing or volatility is None:
            # Uniform spacing
            spacing = price_range / (grid_levels - 1)
            return [spacing] * (grid_levels - 1)
        
        # Dynamic spacing based on volatility
        # Higher volatility = wider spacing
        base_spacing = price_range / (grid_levels - 1)
        
        spacings = []
        for i in range(grid_levels - 1):
            # Adjust spacing based on position and volatility
            # Center grids are tighter, outer grids are wider
            position_factor = 1.0 - abs((i - grid_levels/2) / (grid_levels/2)) * 0.3
            volatility_factor = 1.0 + (volatility / 10.0) * self.config.volatility_multiplier
            
            adjusted_spacing = base_spacing * position_factor * volatility_factor
            spacings.append(adjusted_spacing)
        
        # Normalize to fit the range
        total_spacing = sum(spacings)
        spacings = [s * (price_range / total_spacing) for s in spacings]
        
        return spacings
    
    def _initialize_grid(self, volatility: Optional[float] = None):
        """
        Grid darajalarini yaratish
        
        Args:
            volatility: Volatility (agar dynamic spacing kerak bo'lsa)
        """
        self.grid_levels.clear()
        
        price_range = self.config.price_range_upper - self.config.price_range_lower
        
        # Calculate spacing
        spacings = self._calculate_grid_spacing(
            price_range,
            self.config.grid_levels,
            volatility
        )
        
        # Generate grid levels
        current_price = self.config.price_range_lower
        
        for i in range(self.config.grid_levels):
            # Determine order type
            if current_price < self.config.base_price:
                order_type = 'buy'
            else:
                order_type = 'sell'
            
            grid_level = GridLevel(
                price=current_price,
                order_type=order_type,
                quantity=self.config.order_amount
            )
            
            self.grid_levels.append(grid_level)
            
            # Move to next level
            if i < len(spacings):
                current_price += spacings[i]
        
        logger.info(f"Grid initialized with {len(self.grid_levels)} levels")
    
    def rebalance_grid(
        self,
        current_price: float,
        price_history: List[float]
    ):
        """
        Gridni qayta muvozanatlash
        
        Args:
            current_price: Joriy narx
            price_history: Narxlar tarixi
        """
        # Calculate new volatility
        volatility = self._calculate_volatility(price_history)
        
        # Adjust base price to current price
        self.config.base_price = current_price
        
        # Recalculate range based on volatility
        range_adjustment = volatility * 0.1  # 10% of volatility
        range_size = self.config.price_range_upper - self.config.price_range_lower
        
        self.config.price_range_lower = current_price - range_size / 2 * (1 + range_adjustment)
        self.config.price_range_upper = current_price + range_size / 2 * (1 + range_adjustment)
        
        # Cancel pending orders
        for level in self.grid_levels:
            if level.status == 'pending':
                level.status = 'cancelled'
        
        # Reinitialize grid
        self._initialize_grid(volatility)
        
        logger.info(f"Grid rebalanced at price ${current_price:.2f}")
        logger.info(f"New range: ${self.config.price_range_lower:.2f} - ${self.config.price_range_upper:.2f}")
    
    def place_grid_orders(self) -> List[Dict]:
        """
        Barcha grid orderlarni joylashtirish
        
        Returns:
            Joylashtirilgan orderlar ro'yxati
        """
        placed_orders = []
        
        for level in self.grid_levels:
            if level.status == 'pending':
                # Simulate order placement
                order = {
                    'symbol': self.config.symbol,
                    'type': level.order_type,
                    'price': level.price,
                    'quantity': level.quantity,
                    'order_id': f"GRID_{len(placed_orders)}_{int(datetime.now().timestamp())}",
                    'timestamp': datetime.now()
                }
                
                level.order_id = order['order_id']
                self.active_orders[order['order_id']] = level
                
                placed_orders.append(order)
        
        logger.info(f"Placed {len(placed_orders)} grid orders")
        return placed_orders
    
    def check_filled_orders(
        self,
        current_price: float,
        filled_orders: List[str]
    ) -> List[Dict]:
        """
        To'ldirilgan orderlarni tekshirish
        
        Args:
            current_price: Joriy narx
            filled_orders: To'ldirilgan order ID'lar
            
        Returns:
            Yangi joylashtirilishi kerak bo'lgan orderlar
        """
        new_orders = []
        
        for order_id in filled_orders:
            if order_id in self.active_orders:
                level = self.active_orders[order_id]
                level.status = 'filled'
                level.filled_at = datetime.now()
                
                # Calculate profit/loss
                if level.order_type == 'buy':
                    # Buy filled, place sell order
                    sell_price = level.price * (1 + self.config.take_profit_per_grid / 100)
                    
                    new_order = {
                        'symbol': self.config.symbol,
                        'type': 'sell',
                        'price': sell_price,
                        'quantity': level.quantity,
                        'order_id': f"GRID_SELL_{int(datetime.now().timestamp())}",
                        'timestamp': datetime.now(),
                        'paired_with': order_id
                    }
                    
                    new_orders.append(new_order)
                    self.metrics['total_buy_volume'] += level.quantity
                    
                else:  # sell
                    # Sell filled, place buy order
                    buy_price = level.price * (1 - self.config.take_profit_per_grid / 100)
                    
                    new_order = {
                        'symbol': self.config.symbol,
                        'type': 'buy',
                        'price': buy_price,
                        'quantity': level.quantity,
                        'order_id': f"GRID_BUY_{int(datetime.now().timestamp())}",
                        'timestamp': datetime.now(),
                        'paired_with': order_id
                    }
                    
                    new_orders.append(new_order)
                    self.metrics['total_sell_volume'] += level.quantity
                    
                    # Calculate profit for this trade
                    profit = level.quantity * level.price * (self.config.take_profit_per_grid / 100)
                    self.total_profit += profit
                    
                    self.metrics['total_trades'] += 1
                    self.metrics['profitable_trades'] += 1
                    
                    if profit > self.metrics['largest_profit']:
                        self.metrics['largest_profit'] = profit
                
                # Record completed trade
                self.completed_trades.append({
                    'order_id': order_id,
                    'type': level.order_type,
                    'price': level.price,
                    'quantity': level.quantity,
                    'filled_at': level.filled_at
                })
                
                # Remove from active orders
                del self.active_orders[order_id]
        
        return new_orders
    
    def adjust_for_trend(
        self,
        price_history: List[float],
        lookback: int = 50
    ):
        """
        Trend asosida grid sozlash
        
        Args:
            price_history: Narxlar tarixi
            lookback: Trend aniqlash davri
        """
        if len(price_history) < lookback:
            return
        
        recent_prices = price_history[-lookback:]
        
        # Calculate trend (linear regression slope)
        x = np.arange(len(recent_prices))
        slope, intercept = np.polyfit(x, recent_prices, 1)
        
        # Trend strength
        trend_pct = (slope / recent_prices[0]) * 100 * lookback
        
        logger.info(f"Detected trend: {trend_pct:.2f}%")
        
        # Adjust grid based on trend
        if abs(trend_pct) > 5:  # Strong trend
            if trend_pct > 0:  # Uptrend
                # Shift grid upward
                shift_amount = self.config.base_price * 0.02  # 2% shift
                self.config.price_range_lower += shift_amount
                self.config.price_range_upper += shift_amount
                logger.info("Grid shifted upward due to uptrend")
                
            else:  # Downtrend
                # Shift grid downward
                shift_amount = self.config.base_price * 0.02
                self.config.price_range_lower -= shift_amount
                self.config.price_range_upper -= shift_amount
                logger.info("Grid shifted downward due to downtrend")
            
            # Reinitialize grid with new range
            self._initialize_grid()
    
    def get_grid_status(self) -> Dict:
        """Grid holati haqida ma'lumot"""
        pending_count = sum(1 for level in self.grid_levels if level.status == 'pending')
        filled_count = sum(1 for level in self.grid_levels if level.status == 'filled')
        
        return {
            'total_levels': len(self.grid_levels),
            'pending_orders': pending_count,
            'filled_orders': filled_count,
            'active_orders': len(self.active_orders),
            'total_profit': self.total_profit,
            'completed_trades': len(self.completed_trades),
            'metrics': self.metrics
        }
    
    def optimize_grid_spacing(
        self,
        price_history: List[float],
        trade_history: List[Dict]
    ) -> Dict:
        """
        Grid spacing optimizatsiya (backtesting asosida)
        
        Args:
            price_history: Narxlar tarixi
            trade_history: Savdo tarixi
            
        Returns:
            Optimal parametrlar
        """
        # Test different grid configurations
        test_configs = []
        
        for grid_count in [5, 10, 15, 20]:
            for profit_pct in [0.5, 1.0, 1.5, 2.0]:
                test_config = GridConfig(
                    symbol=self.config.symbol,
                    base_price=self.config.base_price,
                    price_range_lower=self.config.price_range_lower,
                    price_range_upper=self.config.price_range_upper,
                    grid_levels=grid_count,
                    order_amount=self.config.order_amount,
                    take_profit_per_grid=profit_pct
                )
                
                # Simulate performance
                profit = self._simulate_grid_performance(
                    test_config,
                    price_history
                )
                
                test_configs.append({
                    'grid_levels': grid_count,
                    'take_profit_pct': profit_pct,
                    'simulated_profit': profit
                })
        
        # Find best configuration
        best_config = max(test_configs, key=lambda x: x['simulated_profit'])
        
        logger.info(f"Optimal grid configuration found:")
        logger.info(f"  Grid levels: {best_config['grid_levels']}")
        logger.info(f"  Take profit: {best_config['take_profit_pct']}%")
        logger.info(f"  Expected profit: ${best_config['simulated_profit']:.2f}")
        
        return best_config
    
    def _simulate_grid_performance(
        self,
        config: GridConfig,
        price_history: List[float]
    ) -> float:
        """
        Grid performance simulatsiya qilish
        
        Args:
            config: Test konfiguratsiyasi
            price_history: Narxlar tarixi
            
        Returns:
            Jami foyda
        """
        # Simple simulation
        grid_spacing = (config.price_range_upper - config.price_range_lower) / config.grid_levels
        grid_prices = [
            config.price_range_lower + i * grid_spacing
            for i in range(config.grid_levels)
        ]
        
        total_profit = 0.0
        positions = {}
        
        for price in price_history:
            # Check if price crosses any grid level
            for grid_price in grid_prices:
                if abs(price - grid_price) < grid_spacing * 0.1:  # Close enough
                    # Toggle position
                    if grid_price not in positions:
                        # Buy
                        positions[grid_price] = {
                            'entry_price': grid_price,
                            'quantity': config.order_amount
                        }
                    else:
                        # Sell
                        position = positions[grid_price]
                        profit = (price - position['entry_price']) * position['quantity']
                        total_profit += profit
                        del positions[grid_price]
        
        return total_profit


# Multi-timeframe Grid Strategy
class MultiTimeframeGridStrategy:
    """
    Multiple timeframe grid strategiyasi
    
    Turli vaqt oralig'ida (1h, 4h, 1d) grid strategiyalarni boshqaradi
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.timeframe_strategies: Dict[str, GridTradingStrategy] = {}
        self.timeframe_weights = {
            '1h': 0.5,
            '4h': 0.3,
            '1d': 0.2
        }
    
    def add_timeframe(
        self,
        timeframe: str,
        config: GridConfig,
        weight: float = 1.0
    ):
        """
        Yangi timeframe qo'shish
        
        Args:
            timeframe: Vaqt oralig'i ('1h', '4h', '1d')
            config: Grid konfiguratsiyasi
            weight: Strategiya og'irligi
        """
        strategy = GridTradingStrategy(config)
        self.timeframe_strategies[timeframe] = strategy
        self.timeframe_weights[timeframe] = weight
        
        logger.info(f"Added {timeframe} grid strategy with weight {weight}")
    
    def get_aggregated_signal(
        self,
        current_price: float
    ) -> Dict:
        """
        Barcha timeframe signallarini birlashtirib olish
        
        Args:
            current_price: Joriy narx
            
        Returns:
            Aggregated signal
        """
        total_weight = sum(self.timeframe_weights.values())
        weighted_signal = 0.0
        
        signals = {}
        
        for timeframe, strategy in self.timeframe_strategies.items():
            # Determine signal based on current price vs grid
            grid_status = strategy.get_grid_status()
            
            # Simple signal: buy if below mid-grid, sell if above
            mid_price = (strategy.config.price_range_lower + strategy.config.price_range_upper) / 2
            
            if current_price < mid_price:
                signal = 1.0  # Buy signal
            elif current_price > mid_price:
                signal = -1.0  # Sell signal
            else:
                signal = 0.0  # Neutral
            
            weight = self.timeframe_weights[timeframe]
            weighted_signal += signal * weight
            
            signals[timeframe] = {
                'signal': signal,
                'weight': weight,
                'grid_status': grid_status
            }
        
        aggregated_signal = weighted_signal / total_weight
        
        return {
            'aggregated_signal': aggregated_signal,
            'individual_signals': signals,
            'recommendation': 'BUY' if aggregated_signal > 0.3 else ('SELL' if aggregated_signal < -0.3 else 'HOLD')
        }


# Example usage
def main():
    """Test grid trading strategy"""
    
    # Configuration
    config = GridConfig(
        symbol='BTC/USDT',
        base_price=45000,
        price_range_lower=43000,
        price_range_upper=47000,
        grid_levels=10,
        order_amount=0.01,  # 0.01 BTC
        take_profit_per_grid=1.0,  # 1% per grid
        use_dynamic_spacing=True,
        volatility_multiplier=1.5
    )
    
    # Initialize strategy
    strategy = GridTradingStrategy(config)
    
    # Place grid orders
    orders = strategy.place_grid_orders()
    print(f"\n✅ Placed {len(orders)} grid orders")
    
    # Simulate price movements
    import random
    price_history = [45000]
    
    for i in range(100):
        # Random price movement
        change = random.uniform(-200, 200)
        new_price = price_history[-1] + change
        price_history.append(new_price)
        
        # Check for filled orders (simulate)
        filled = []
        for order_id, level in strategy.active_orders.items():
            if level.order_type == 'buy' and new_price <= level.price:
                filled.append(order_id)
            elif level.order_type == 'sell' and new_price >= level.price:
                filled.append(order_id)
        
        # Process filled orders
        if filled:
            new_orders = strategy.check_filled_orders(new_price, filled)
            print(f"📊 Price: ${new_price:.2f}, Filled: {len(filled)}, New orders: {len(new_orders)}")
    
    # Show results
    status = strategy.get_grid_status()
    print("\n" + "="*60)
    print("GRID TRADING RESULTS")
    print("="*60)
    print(f"Total profit: ${status['total_profit']:.2f}")
    print(f"Completed trades: {status['completed_trades']}")
    print(f"Total trades: {status['metrics']['total_trades']}")
    print(f"Profitable trades: {status['metrics']['profitable_trades']}")
    print(f"Largest profit: ${status['metrics']['largest_profit']:.2f}")
    print("="*60)


if __name__ == '__main__':
    main()
