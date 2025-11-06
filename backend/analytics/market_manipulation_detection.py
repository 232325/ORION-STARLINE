"""
Market Manipulation Detection System
Wash trading, pump & dump, spoofing detection
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict, deque
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TradeEvent:
    """Bitta trade event"""
    timestamp: datetime
    symbol: str
    price: Decimal
    volume: Decimal
    side: str  # 'buy' or 'sell'
    trade_id: str
    buyer_id: Optional[str] = None
    seller_id: Optional[str] = None


@dataclass
class OrderBookSnapshot:
    """Order book snapshot"""
    timestamp: datetime
    symbol: str
    bids: List[Tuple[Decimal, Decimal]]  # (price, volume)
    asks: List[Tuple[Decimal, Decimal]]
    bid_volume: Decimal
    ask_volume: Decimal
    spread: Decimal


@dataclass
class ManipulationAlert:
    """Manipulation alert"""
    alert_type: str  # 'wash_trade', 'pump_dump', 'spoofing', 'layering'
    symbol: str
    timestamp: datetime
    severity: str  # 'low', 'medium', 'high', 'critical'
    confidence: Decimal  # 0-100
    evidence: Dict
    description: str


@dataclass
class SuspiciousPattern:
    """Shubhali pattern ma'lumotlari"""
    pattern_type: str
    symbol: str
    detected_at: datetime
    duration_minutes: int
    indicators: Dict
    risk_score: Decimal


class ManipulationDetector:
    """Bozor manipulatsiyasini aniqlash tizimi"""
    
    def __init__(
        self,
        wash_trade_threshold: Decimal = Decimal('0.7'),  # Similarity threshold
        pump_threshold_percent: Decimal = Decimal('10'),  # 10% price increase
        volume_spike_multiplier: Decimal = Decimal('5'),  # 5x average volume
        alert_cooldown_minutes: int = 30
    ):
        self.wash_trade_threshold = wash_trade_threshold
        self.pump_threshold = pump_threshold_percent
        self.volume_spike_multiplier = volume_spike_multiplier
        self.alert_cooldown = timedelta(minutes=alert_cooldown_minutes)
        
        self.trade_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.orderbook_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.recent_alerts: Dict[str, datetime] = {}
        
        # Account tracking for wash trading
        self.account_trades: Dict[str, List[TradeEvent]] = defaultdict(list)
        
        # Volume tracking
        self.volume_history: Dict[str, List[Tuple[datetime, Decimal]]] = defaultdict(list)
    
    async def analyze_trades(
        self,
        symbol: str,
        trades: List[TradeEvent]
    ) -> List[ManipulationAlert]:
        """Trade'larni tahlil qilish va manipulatsiya aniqlash"""
        try:
            alerts = []
            
            # Add to history
            for trade in trades:
                self.trade_history[symbol].append(trade)
                
                # Track by account
                if trade.buyer_id:
                    self.account_trades[trade.buyer_id].append(trade)
                if trade.seller_id:
                    self.account_trades[trade.seller_id].append(trade)
            
            # Detect wash trading
            wash_alerts = await self._detect_wash_trading(symbol)
            alerts.extend(wash_alerts)
            
            # Detect pump and dump
            pump_alerts = await self._detect_pump_dump(symbol)
            alerts.extend(pump_alerts)
            
            # Detect volume manipulation
            volume_alerts = await self._detect_volume_manipulation(symbol)
            alerts.extend(volume_alerts)
            
            # Detect coordinated trading
            coord_alerts = await self._detect_coordinated_trading(symbol)
            alerts.extend(coord_alerts)
            
            # Filter by cooldown
            alerts = self._filter_cooldown_alerts(alerts)
            
            logger.info(f"Detected {len(alerts)} manipulation alerts for {symbol}")
            return alerts
            
        except Exception as e:
            logger.error(f"Error analyzing trades: {e}")
            return []
    
    async def _detect_wash_trading(self, symbol: str) -> List[ManipulationAlert]:
        """Wash trading aniqlash (self-trading)"""
        try:
            alerts = []
            recent_trades = list(self.trade_history[symbol])[-100:]  # Last 100 trades
            
            if len(recent_trades) < 10:
                return alerts
            
            # Group trades by account pairs
            trade_pairs = defaultdict(list)
            
            for trade in recent_trades:
                if not trade.buyer_id or not trade.seller_id:
                    continue
                
                # Create canonical pair (sorted to avoid duplicates)
                pair = tuple(sorted([trade.buyer_id, trade.seller_id]))
                trade_pairs[pair].append(trade)
            
            # Analyze each pair
            for pair, pair_trades in trade_pairs.items():
                if len(pair_trades) < 5:  # Need multiple trades
                    continue
                
                # Check if accounts are trading back and forth
                buyer_seller_swaps = 0
                for i in range(1, len(pair_trades)):
                    prev = pair_trades[i-1]
                    curr = pair_trades[i]
                    
                    # Check if buyer/seller roles swap
                    if prev.buyer_id == curr.seller_id and prev.seller_id == curr.buyer_id:
                        buyer_seller_swaps += 1
                
                swap_ratio = buyer_seller_swaps / len(pair_trades)
                
                if swap_ratio >= float(self.wash_trade_threshold):
                    # Potential wash trading
                    total_volume = sum(t.volume for t in pair_trades)
                    
                    # Calculate confidence
                    confidence = min(swap_ratio * 100, 100)
                    
                    alert = ManipulationAlert(
                        alert_type='wash_trade',
                        symbol=symbol,
                        timestamp=datetime.now(),
                        severity='high' if confidence >= 80 else 'medium',
                        confidence=Decimal(str(confidence)),
                        evidence={
                            'account_pair': pair,
                            'trade_count': len(pair_trades),
                            'swap_ratio': swap_ratio,
                            'total_volume': float(total_volume),
                            'time_window': '1h'
                        },
                        description=f"Suspected wash trading between accounts {pair[0][:8]}... and {pair[1][:8]}..."
                    )
                    
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error detecting wash trading: {e}")
            return []
    
    async def _detect_pump_dump(self, symbol: str) -> List[ManipulationAlert]:
        """Pump and dump sxemasini aniqlash"""
        try:
            alerts = []
            recent_trades = list(self.trade_history[symbol])[-200:]
            
            if len(recent_trades) < 50:
                return alerts
            
            # Calculate rolling price and volume
            window_size = 20
            
            for i in range(window_size, len(recent_trades) - window_size):
                # Previous window
                prev_window = recent_trades[i-window_size:i]
                # Current window
                curr_window = recent_trades[i:i+window_size]
                # Next window (for dump detection)
                next_window = recent_trades[i+window_size:i+2*window_size] if i+2*window_size <= len(recent_trades) else []
                
                # Calculate metrics
                prev_avg_price = sum(t.price for t in prev_window) / len(prev_window)
                curr_avg_price = sum(t.price for t in curr_window) / len(curr_window)
                
                prev_avg_volume = sum(t.volume for t in prev_window) / len(prev_window)
                curr_avg_volume = sum(t.volume for t in curr_window) / len(curr_window)
                
                # Price increase
                price_increase = ((curr_avg_price - prev_avg_price) / prev_avg_price) * Decimal('100')
                
                # Volume spike
                volume_ratio = curr_avg_volume / prev_avg_volume if prev_avg_volume > 0 else Decimal('1')
                
                # Check for pump conditions
                is_pump = (
                    price_increase >= self.pump_threshold and
                    volume_ratio >= self.volume_spike_multiplier
                )
                
                if is_pump:
                    # Check for dump (price drop after pump)
                    is_dump = False
                    if next_window:
                        next_avg_price = sum(t.price for t in next_window) / len(next_window)
                        price_drop = ((curr_avg_price - next_avg_price) / curr_avg_price) * Decimal('100')
                        
                        if price_drop >= self.pump_threshold / 2:
                            is_dump = True
                    
                    # Calculate confidence
                    confidence = min(
                        (float(price_increase) / 20) * 50 +  # Price component
                        (min(float(volume_ratio) / 10, 1.0)) * 50,  # Volume component
                        100
                    )
                    
                    alert = ManipulationAlert(
                        alert_type='pump_dump' if is_dump else 'pump',
                        symbol=symbol,
                        timestamp=curr_window[0].timestamp,
                        severity='critical' if is_dump else 'high',
                        confidence=Decimal(str(confidence)),
                        evidence={
                            'price_increase_percent': float(price_increase),
                            'volume_ratio': float(volume_ratio),
                            'is_dump_detected': is_dump,
                            'window_size': window_size,
                            'avg_price_before': float(prev_avg_price),
                            'avg_price_during': float(curr_avg_price)
                        },
                        description=f"Suspected {'pump & dump' if is_dump else 'pump'} scheme: {price_increase:.1f}% price increase with {volume_ratio:.1f}x volume spike"
                    )
                    
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error detecting pump and dump: {e}")
            return []
    
    async def _detect_volume_manipulation(self, symbol: str) -> List[ManipulationAlert]:
        """Volume manipulatsiyasini aniqlash"""
        try:
            alerts = []
            recent_trades = list(self.trade_history[symbol])[-100:]
            
            if len(recent_trades) < 30:
                return alerts
            
            # Calculate baseline volume
            volumes = [float(t.volume) for t in recent_trades[:-10]]
            if not volumes:
                return alerts
            
            avg_volume = statistics.mean(volumes)
            std_volume = statistics.stdev(volumes) if len(volumes) > 1 else 0
            
            # Check recent spikes
            recent_10 = recent_trades[-10:]
            for trade in recent_10:
                if float(trade.volume) > avg_volume + 3 * std_volume:
                    # Significant volume spike
                    
                    # Check if price barely moved (suspicious)
                    price_window = [t.price for t in recent_trades[-20:]]
                    price_volatility = (
                        max(price_window) - min(price_window)
                    ) / statistics.mean([float(p) for p in price_window])
                    
                    if price_volatility < Decimal('0.01'):  # < 1% volatility
                        confidence = min(
                            (float(trade.volume) / avg_volume) * 20,
                            100
                        )
                        
                        alert = ManipulationAlert(
                            alert_type='volume_manipulation',
                            symbol=symbol,
                            timestamp=trade.timestamp,
                            severity='medium',
                            confidence=Decimal(str(confidence)),
                            evidence={
                                'trade_volume': float(trade.volume),
                                'avg_volume': avg_volume,
                                'volume_ratio': float(trade.volume) / avg_volume,
                                'price_volatility': float(price_volatility),
                                'price': float(trade.price)
                            },
                            description=f"Suspicious volume spike ({float(trade.volume)/avg_volume:.1f}x) with minimal price movement"
                        )
                        
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error detecting volume manipulation: {e}")
            return []
    
    async def _detect_coordinated_trading(self, symbol: str) -> List[ManipulationAlert]:
        """Koordinatsiyalangan trading aniqlash"""
        try:
            alerts = []
            recent_trades = list(self.trade_history[symbol])[-100:]
            
            if len(recent_trades) < 20:
                return alerts
            
            # Group trades by time windows (5 minute windows)
            time_windows = defaultdict(list)
            
            for trade in recent_trades:
                window_key = trade.timestamp.replace(
                    minute=(trade.timestamp.minute // 5) * 5,
                    second=0,
                    microsecond=0
                )
                time_windows[window_key].append(trade)
            
            # Analyze each window
            for window_time, window_trades in time_windows.items():
                if len(window_trades) < 10:
                    continue
                
                # Check if all trades are in same direction
                buy_count = sum(1 for t in window_trades if t.side == 'buy')
                sell_count = len(window_trades) - buy_count
                
                directional_ratio = max(buy_count, sell_count) / len(window_trades)
                
                # Check if trades are evenly spaced (bot-like)
                timestamps = [t.timestamp for t in window_trades]
                time_diffs = [
                    (timestamps[i+1] - timestamps[i]).total_seconds()
                    for i in range(len(timestamps) - 1)
                ]
                
                if time_diffs:
                    avg_diff = statistics.mean(time_diffs)
                    std_diff = statistics.stdev(time_diffs) if len(time_diffs) > 1 else 0
                    
                    # Regular spacing indicates automation
                    regularity_score = 1 - (std_diff / avg_diff) if avg_diff > 0 else 0
                    
                    if directional_ratio >= 0.9 and regularity_score >= 0.8:
                        # Highly coordinated
                        confidence = min(
                            directional_ratio * 50 + regularity_score * 50,
                            100
                        )
                        
                        alert = ManipulationAlert(
                            alert_type='coordinated_trading',
                            symbol=symbol,
                            timestamp=window_time,
                            severity='high',
                            confidence=Decimal(str(confidence)),
                            evidence={
                                'trade_count': len(window_trades),
                                'directional_ratio': directional_ratio,
                                'regularity_score': regularity_score,
                                'avg_interval_seconds': avg_diff,
                                'dominant_side': 'buy' if buy_count > sell_count else 'sell'
                            },
                            description=f"Suspected coordinated trading: {len(window_trades)} {('buy' if buy_count > sell_count else 'sell')} orders in regular intervals"
                        )
                        
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error detecting coordinated trading: {e}")
            return []
    
    async def analyze_orderbook(
        self,
        symbol: str,
        orderbook: OrderBookSnapshot
    ) -> List[ManipulationAlert]:
        """Order book tahlili (spoofing, layering)"""
        try:
            alerts = []
            
            # Add to history
            self.orderbook_history[symbol].append(orderbook)
            
            # Detect spoofing
            spoof_alerts = await self._detect_spoofing(symbol, orderbook)
            alerts.extend(spoof_alerts)
            
            # Detect layering
            layer_alerts = await self._detect_layering(symbol, orderbook)
            alerts.extend(layer_alerts)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error analyzing orderbook: {e}")
            return []
    
    async def _detect_spoofing(
        self,
        symbol: str,
        orderbook: OrderBookSnapshot
    ) -> List[ManipulationAlert]:
        """Spoofing aniqlash (fake large orders)"""
        try:
            alerts = []
            
            # Get previous orderbook
            history = list(self.orderbook_history[symbol])
            if len(history) < 2:
                return alerts
            
            prev_orderbook = history[-2]
            
            # Calculate average order size
            all_orders = orderbook.bids + orderbook.asks
            if not all_orders:
                return alerts
            
            avg_order_size = sum(vol for _, vol in all_orders) / len(all_orders)
            
            # Check for abnormally large orders
            for price, volume in orderbook.bids + orderbook.asks:
                if volume > avg_order_size * 10:  # 10x average
                    # Check if this order was quickly cancelled
                    # (by comparing with previous snapshot)
                    
                    was_in_prev = any(
                        abs(p - price) < Decimal('0.01') and v > volume * Decimal('0.9')
                        for p, v in (prev_orderbook.bids + prev_orderbook.asks)
                    )
                    
                    # If large order appeared and disappeared quickly
                    if not was_in_prev:
                        confidence = min(
                            (float(volume) / float(avg_order_size)) * 10,
                            100
                        )
                        
                        alert = ManipulationAlert(
                            alert_type='spoofing',
                            symbol=symbol,
                            timestamp=orderbook.timestamp,
                            severity='high',
                            confidence=Decimal(str(confidence)),
                            evidence={
                                'order_price': float(price),
                                'order_volume': float(volume),
                                'avg_order_volume': float(avg_order_size),
                                'volume_ratio': float(volume / avg_order_size)
                            },
                            description=f"Suspected spoofing: Large order ({volume:.2f}) placed and quickly removed"
                        )
                        
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error detecting spoofing: {e}")
            return []
    
    async def _detect_layering(
        self,
        symbol: str,
        orderbook: OrderBookSnapshot
    ) -> List[ManipulationAlert]:
        """Layering aniqlash (multiple fake orders)"""
        try:
            alerts = []
            
            # Check for multiple large orders at similar price levels
            bid_clusters = self._find_order_clusters(orderbook.bids)
            ask_clusters = self._find_order_clusters(orderbook.asks)
            
            for cluster in bid_clusters + ask_clusters:
                if len(cluster) >= 5:  # 5+ orders in cluster
                    total_volume = sum(vol for _, vol in cluster)
                    avg_volume = total_volume / len(cluster)
                    
                    # Check if volumes are suspiciously similar
                    volumes = [float(vol) for _, vol in cluster]
                    vol_std = statistics.stdev(volumes) if len(volumes) > 1 else 0
                    vol_mean = statistics.mean(volumes)
                    
                    coefficient_of_variation = vol_std / vol_mean if vol_mean > 0 else 0
                    
                    # Low variation = likely automated
                    if coefficient_of_variation < 0.2:
                        confidence = min(
                            len(cluster) * 10 + (1 - coefficient_of_variation) * 50,
                            100
                        )
                        
                        alert = ManipulationAlert(
                            alert_type='layering',
                            symbol=symbol,
                            timestamp=orderbook.timestamp,
                            severity='medium',
                            confidence=Decimal(str(confidence)),
                            evidence={
                                'order_count': len(cluster),
                                'total_volume': float(total_volume),
                                'avg_volume': avg_volume,
                                'volume_variation': coefficient_of_variation,
                                'price_range': (
                                    float(min(p for p, _ in cluster)),
                                    float(max(p for p, _ in cluster))
                                )
                            },
                            description=f"Suspected layering: {len(cluster)} similar orders in tight price range"
                        )
                        
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error detecting layering: {e}")
            return []
    
    def _find_order_clusters(
        self,
        orders: List[Tuple[Decimal, Decimal]],
        price_tolerance: Decimal = Decimal('0.01')  # 1% price range
    ) -> List[List[Tuple[Decimal, Decimal]]]:
        """Order'larni clusterlarga ajratish"""
        try:
            if not orders:
                return []
            
            sorted_orders = sorted(orders, key=lambda x: x[0])
            clusters = []
            current_cluster = [sorted_orders[0]]
            
            for i in range(1, len(sorted_orders)):
                prev_price = current_cluster[-1][0]
                curr_price = sorted_orders[i][0]
                
                # Check if within tolerance
                if abs(curr_price - prev_price) / prev_price <= price_tolerance:
                    current_cluster.append(sorted_orders[i])
                else:
                    if len(current_cluster) >= 3:
                        clusters.append(current_cluster)
                    current_cluster = [sorted_orders[i]]
            
            if len(current_cluster) >= 3:
                clusters.append(current_cluster)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error finding order clusters: {e}")
            return []
    
    def _filter_cooldown_alerts(
        self,
        alerts: List[ManipulationAlert]
    ) -> List[ManipulationAlert]:
        """Alert cooldown filter qilish"""
        filtered = []
        
        for alert in alerts:
            key = f"{alert.symbol}:{alert.alert_type}"
            
            if key in self.recent_alerts:
                last_alert = self.recent_alerts[key]
                if datetime.now() - last_alert < self.alert_cooldown:
                    continue
            
            filtered.append(alert)
            self.recent_alerts[key] = datetime.now()
        
        return filtered
    
    async def get_manipulation_report(
        self,
        symbol: Optional[str] = None,
        hours: int = 24
    ) -> Dict:
        """Manipulatsiya hisoboti"""
        try:
            # This would aggregate all detected alerts
            # and provide summary statistics
            
            report = {
                'period_hours': hours,
                'total_alerts': 0,
                'alerts_by_type': {},
                'alerts_by_severity': {},
                'most_manipulated_symbols': [],
                'summary': ''
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating manipulation report: {e}")
            return {}


async def main():
    """Test function"""
    detector = ManipulationDetector()
    
    # Sample trades
    trades = [
        TradeEvent(
            timestamp=datetime.now(),
            symbol='BTC/USDT',
            price=Decimal('50000'),
            volume=Decimal('1.5'),
            side='buy',
            trade_id='1',
            buyer_id='user1',
            seller_id='user2'
        ),
        TradeEvent(
            timestamp=datetime.now() + timedelta(seconds=10),
            symbol='BTC/USDT',
            price=Decimal('50010'),
            volume=Decimal('1.5'),
            side='sell',
            trade_id='2',
            buyer_id='user2',
            seller_id='user1'
        )
    ]
    
    alerts = await detector.analyze_trades('BTC/USDT', trades)
    
    print(f"Detected {len(alerts)} alerts:")
    for alert in alerts:
        print(f"- {alert.alert_type}: {alert.description} (confidence: {alert.confidence}%)")


if __name__ == '__main__':
    asyncio.run(main())
