"""
Order Book Management System
===========================

High-performance order book implementation optimized for microsecond-level latency
"""

import time
import bisect
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import threading

@dataclass
class Order:
    """Individual order structure"""
    order_id: str
    symbol: str
    side: str  # 'BUY' or 'SELL'
    price: float
    quantity: int
    timestamp: float
    trader_id: str
    priority: int = 0  # Higher priority = better execution order
    
    def __lt__(self, other):
        """For sorting orders - price-time priority"""
        if self.side == 'BUY':
            # For buy orders: higher price first, then earlier timestamp
            if self.price != other.price:
                return self.price > other.price
            return self.timestamp < other.timestamp
        else:
            # For sell orders: lower price first, then earlier timestamp
            if self.price != other.price:
                return self.price < other.price
            return self.timestamp < other.timestamp
    
@dataclass
class OrderBookLevel:
    """Single price level in the order book"""
    price: float
    total_quantity: int
    order_count: int

class OrderBook:
    """
    High-Performance Order Book
    
    Optimized for microsecond-level latency operations
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.logger = logging.getLogger(f"OrderBook.{symbol}")
        
        # Order storage - sorted lists for price-time priority
        self.buy_orders: List[Order] = []
        self.sell_orders: List[Order] = []
        
        # Order tracking
        self.active_orders: Dict[str, Order] = {}
        self.order_levels: Dict[float, List[Order]] = defaultdict(list)
        
        # Market statistics
        self.last_trade_price: Optional[float] = None
        self.last_trade_time: float = 0.0
        self.volume_24h: float = 0.0
        self.spread_bps: float = 0.0
        
        # Performance tracking
        self.update_count = 0
        self.last_update_time = time.perf_counter()
        
        # Thread safety
        self.lock = threading.RLock()
        
    def add_order(self, order: Order) -> bool:
        """Add order to the book with O(log n) complexity"""
        with self.lock:
            try:
                self.active_orders[order.order_id] = order
                
                if order.side == 'BUY':
                    bisect.insort(self.buy_orders, order)
                else:
                    bisect.insort(self.sell_orders, order)
                
                self.order_levels[order.price].append(order)
                self.update_count += 1
                
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to add order {order.order_id}: {e}")
                return False
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel existing order"""
        with self.lock:
            if order_id not in self.active_orders:
                return False
                
            order = self.active_orders[order_id]
            
            try:
                # Remove from active orders
                del self.active_orders[order_id]
                
                # Remove from price level
                price_level_orders = self.order_levels[order.price]
                if order in price_level_orders:
                    price_level_orders.remove(order)
                
                # Remove from sorted list
                if order.side == 'BUY':
                    if order in self.buy_orders:
                        self.buy_orders.remove(order)
                else:
                    if order in self.sell_orders:
                        self.sell_orders.remove(order)
                
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to cancel order {order_id}: {e}")
                return False
    
    def modify_order(self, order_id: str, new_quantity: int, new_price: float) -> bool:
        """Modify existing order"""
        with self.lock:
            if order_id not in self.active_orders:
                return False
            
            old_order = self.active_orders[order_id]
            
            # Cancel old order
            self.cancel_order(order_id)
            
            # Create new order with same ID but updated parameters
            new_order = Order(
                order_id=order_id,
                symbol=old_order.symbol,
                side=old_order.side,
                price=new_price,
                quantity=new_quantity,
                timestamp=time.time(),
                trader_id=old_order.trader_id,
                priority=old_order.priority
            )
            
            # Add new order
            return self.add_order(new_order)
    
    def get_best_bid(self) -> Optional[float]:
        """Get best bid price (highest buy price)"""
        with self.lock:
            return self.buy_orders[0].price if self.buy_orders else None
    
    def get_best_ask(self) -> Optional[float]:
        """Get best ask price (lowest sell price)"""
        with self.lock:
            return self.sell_orders[0].price if self.sell_orders else None
    
    def get_spread(self) -> Optional[float]:
        """Get bid-ask spread in basis points"""
        with self.lock:
            best_bid = self.get_best_bid()
            best_ask = self.get_best_ask()
            
            if best_bid is None or best_ask is None:
                return None
            
            spread = ((best_ask - best_bid) / ((best_bid + best_ask) / 2)) * 10000
            self.spread_bps = spread
            return spread
    
    def get_market_depth(self, levels: int = 5) -> Dict[str, List[OrderBookLevel]]:
        """Get market depth for specified number of levels"""
        with self.lock:
            depth = {'bids': [], 'asks': []}
            
            # Get bid levels (highest prices first)
            bid_prices = sorted(set(order.price for order in self.buy_orders), reverse=True)
            for price in bid_prices[:levels]:
                orders_at_price = [o for o in self.buy_orders if o.price == price]
                total_qty = sum(o.quantity for o in orders_at_price)
                depth['bids'].append(OrderBookLevel(price, total_qty, len(orders_at_price)))
            
            # Get ask levels (lowest prices first)
            ask_prices = sorted(set(order.price for order in self.sell_orders))
            for price in ask_prices[:levels]:
                orders_at_price = [o for o in self.sell_orders if o.price == price]
                total_qty = sum(o.quantity for o in orders_at_price)
                depth['asks'].append(OrderBookLevel(price, total_qty, len(orders_at_price)))
            
            return depth
    
    def match_order(self, order: Order) -> List[Dict]:
        """Match incoming order against existing orders"""
        with self.lock:
            matches = []
            
            if order.side == 'BUY':
                # Match against sell orders
                matches = self._match_against_sells(order)
            else:
                # Match against buy orders
                matches = self._match_against_buys(order)
            
            # Update trade statistics
            if matches:
                avg_price = sum(m['price'] * m['quantity'] for m in matches) / sum(m['quantity'] for m in matches)
                self.last_trade_price = avg_price
                self.last_trade_time = time.time()
                self.volume_24h += sum(m['quantity'] for m in matches)
            
            return matches
    
    def _match_against_sells(self, buy_order: Order) -> List[Dict]:
        """Match buy order against sell orders"""
        matches = []
        remaining_qty = buy_order.quantity
        
        # Match against best sell orders
        while remaining_qty > 0 and self.sell_orders and self.sell_orders[0].price <= buy_order.price:
            sell_order = self.sell_orders[0]
            match_qty = min(remaining_qty, sell_order.quantity)
            
            if match_qty > 0:
                matches.append({
                    'buy_order': buy_order.order_id,
                    'sell_order': sell_order.order_id,
                    'price': sell_order.price,
                    'quantity': match_qty,
                    'timestamp': time.time()
                })
                
                # Update orders
                remaining_qty -= match_qty
                sell_order.quantity -= match_qty
                
                if sell_order.quantity == 0:
                    self.cancel_order(sell_order.order_id)
                else:
                    # Re-sort the list since quantity changed
                    self.buy_orders.remove(sell_order)
                    self.sell_orders.remove(sell_order)
                    bisect.insort(self.sell_orders, sell_order)
        
        return matches
    
    def _match_against_buys(self, sell_order: Order) -> List[Dict]:
        """Match sell order against buy orders"""
        matches = []
        remaining_qty = sell_order.quantity
        
        # Match against best buy orders
        while remaining_qty > 0 and self.buy_orders and self.buy_orders[0].price >= sell_order.price:
            buy_order = self.buy_orders[0]
            match_qty = min(remaining_qty, buy_order.quantity)
            
            if match_qty > 0:
                matches.append({
                    'buy_order': buy_order.order_id,
                    'sell_order': sell_order.order_id,
                    'price': buy_order.price,
                    'quantity': match_qty,
                    'timestamp': time.time()
                })
                
                # Update orders
                remaining_qty -= match_qty
                buy_order.quantity -= match_qty
                
                if buy_order.quantity == 0:
                    self.cancel_order(buy_order.order_id)
                else:
                    # Re-sort the list since quantity changed
                    self.buy_orders.remove(buy_order)
                    self.sell_orders.remove(buy_order)
                    bisect.insort(self.buy_orders, buy_order)
        
        return matches
    
    def get_liquidity_metrics(self) -> Dict[str, float]:
        """Calculate liquidity metrics"""
        with self.lock:
            metrics = {}
            
            # Calculate order book imbalance
            bid_volume = sum(order.quantity for order in self.buy_orders)
            ask_volume = sum(order.quantity for order in self.sell_orders)
            total_volume = bid_volume + ask_volume
            
            if total_volume > 0:
                metrics['imbalance'] = (bid_volume - ask_volume) / total_volume
                metrics['bid_volume'] = bid_volume
                metrics['ask_volume'] = ask_volume
                metrics['total_volume'] = total_volume
            else:
                metrics['imbalance'] = 0
                metrics['bid_volume'] = 0
                metrics['ask_volume'] = 0
                metrics['total_volume'] = 0
            
            # Calculate effective spread
            if self.sell_orders and self.buy_orders:
                mid_price = (self.sell_orders[0].price + self.buy_orders[0].price) / 2
                metrics['effective_spread'] = ((self.sell_orders[0].price - self.buy_orders[0].price) / mid_price) * 10000
            else:
                metrics['effective_spread'] = 0
            
            # Calculate market impact estimates
            if bid_volume > 0 and ask_volume > 0:
                # VWAP calculations
                bid_vwap = sum(o.price * o.quantity for o in self.buy_orders) / bid_volume
                ask_vwap = sum(o.price * o.quantity for o in self.sell_orders) / ask_volume
                metrics['bid_vwap'] = bid_vwap
                metrics['ask_vwap'] = ask_vwap
            
            return metrics
    
    def update_from_feed(self, market_data: Optional[Dict]) -> bool:
        """Update order book from market data feed"""
        if not market_data:
            return False
        
        with self.lock:
            try:
                # Update based on market data
                # This is a simplified implementation - in real HFT, 
                # this would integrate with exchange feeds
                pass
                
                self.update_count += 1
                self.last_update_time = time.perf_counter()
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update from feed: {e}")
                return False
    
    def get_book_stats(self) -> Dict[str, Any]:
        """Get order book statistics"""
        with self.lock:
            return {
                'symbol': self.symbol,
                'bid_levels': len(self.buy_orders),
                'ask_levels': len(self.sell_orders),
                'best_bid': self.get_best_bid(),
                'best_ask': self.get_best_ask(),
                'spread_bps': self.spread_bps,
                'last_trade_price': self.last_trade_price,
                'volume_24h': self.volume_24h,
                'update_count': self.update_count,
                'last_update_time': self.last_update_time,
                'liquidity_metrics': self.get_liquidity_metrics()
            }
    
    def snapshot(self) -> Dict[str, Any]:
        """Get complete order book snapshot"""
        with self.lock:
            return {
                'symbol': self.symbol,
                'timestamp': time.time(),
                'bids': [(order.price, order.quantity) for order in self.buy_orders[:20]],
                'asks': [(order.price, order.quantity) for order in self.sell_orders[:20]],
                'best_bid': self.get_best_bid(),
                'best_ask': self.get_best_ask(),
                'spread_bps': self.spread_bps,
                'statistics': self.get_book_stats()
            }