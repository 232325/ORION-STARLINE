"""
Order Flow Analysis System
Level 2 market data, order book depth, liquidity analysis
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from collections import deque, defaultdict
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OrderBookLevel:
    """Order book bitta level ma'lumoti"""
    price: Decimal
    volume: Decimal
    order_count: int
    timestamp: datetime


@dataclass
class OrderBookDepth:
    """Order book chuqurligi"""
    symbol: str
    timestamp: datetime
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    best_bid: Decimal
    best_ask: Decimal
    spread: Decimal
    spread_percent: Decimal
    mid_price: Decimal


@dataclass
class LiquidityMetrics:
    """Likvidlik metrikalari"""
    symbol: str
    timestamp: datetime
    
    # Spread metrics
    spread_bps: Decimal  # Basis points
    effective_spread: Decimal
    
    # Depth metrics
    bid_depth_1pct: Decimal  # Volume within 1% of best bid
    ask_depth_1pct: Decimal
    total_depth_1pct: Decimal
    
    bid_depth_5pct: Decimal
    ask_depth_5pct: Decimal
    total_depth_5pct: Decimal
    
    # Order book imbalance
    imbalance_ratio: Decimal  # (bid_vol - ask_vol) / (bid_vol + ask_vol)
    
    # Market pressure
    buy_pressure: Decimal  # 0-100
    sell_pressure: Decimal
    
    # Liquidity score
    liquidity_score: Decimal  # 0-100


@dataclass
class OrderFlowSignal:
    """Order flow signal"""
    signal_type: str  # 'bullish', 'bearish', 'neutral'
    strength: Decimal  # 0-100
    confidence: Decimal  # 0-100
    indicators: Dict
    description: str
    timestamp: datetime


@dataclass
class VolumeProfile:
    """Volume profile tahlili"""
    symbol: str
    timestamp: datetime
    price_levels: Dict[Decimal, Decimal]  # price -> volume
    value_area_high: Decimal
    value_area_low: Decimal
    point_of_control: Decimal  # Eng ko'p volume bo'lgan price
    volume_distribution: Dict[str, Decimal]


class OrderFlowAnalyzer:
    """Order flow va market microstructure tahlili"""
    
    def __init__(
        self,
        depth_update_interval_ms: int = 100,
        history_size: int = 1000
    ):
        self.depth_update_interval = timedelta(milliseconds=depth_update_interval_ms)
        self.history_size = history_size
        
        # Data storage
        self.orderbook_snapshots: Dict[str, Deque[OrderBookDepth]] = defaultdict(
            lambda: deque(maxlen=history_size)
        )
        self.trade_flow: Dict[str, Deque[Tuple[datetime, Decimal, Decimal, str]]] = defaultdict(
            lambda: deque(maxlen=history_size)
        )
        self.liquidity_history: Dict[str, Deque[LiquidityMetrics]] = defaultdict(
            lambda: deque(maxlen=history_size)
        )
        
        # Aggregated metrics
        self.volume_profiles: Dict[str, VolumeProfile] = {}
        self.cumulative_delta: Dict[str, Decimal] = defaultdict(lambda: Decimal('0'))
    
    async def analyze_orderbook(
        self,
        symbol: str,
        bids: List[Tuple[Decimal, Decimal]],  # (price, volume)
        asks: List[Tuple[Decimal, Decimal]]
    ) -> OrderBookDepth:
        """Order book tahlili"""
        try:
            if not bids or not asks:
                logger.warning(f"Empty orderbook for {symbol}")
                return None
            
            timestamp = datetime.now()
            
            # Sort orders
            bids_sorted = sorted(bids, key=lambda x: x[0], reverse=True)
            asks_sorted = sorted(asks, key=lambda x: x[0])
            
            # Best bid/ask
            best_bid = bids_sorted[0][0]
            best_ask = asks_sorted[0][0]
            
            # Spread
            spread = best_ask - best_bid
            mid_price = (best_bid + best_ask) / Decimal('2')
            spread_percent = (spread / mid_price) * Decimal('100')
            
            # Convert to OrderBookLevel
            bid_levels = [
                OrderBookLevel(
                    price=price,
                    volume=volume,
                    order_count=1,  # Would need real data
                    timestamp=timestamp
                )
                for price, volume in bids_sorted
            ]
            
            ask_levels = [
                OrderBookLevel(
                    price=price,
                    volume=volume,
                    order_count=1,
                    timestamp=timestamp
                )
                for price, volume in asks_sorted
            ]
            
            depth = OrderBookDepth(
                symbol=symbol,
                timestamp=timestamp,
                bids=bid_levels,
                asks=ask_levels,
                best_bid=best_bid,
                best_ask=best_ask,
                spread=spread,
                spread_percent=spread_percent,
                mid_price=mid_price
            )
            
            # Store snapshot
            self.orderbook_snapshots[symbol].append(depth)
            
            logger.info(f"Analyzed orderbook for {symbol}: spread={spread_percent:.3f}%")
            return depth
            
        except Exception as e:
            logger.error(f"Error analyzing orderbook: {e}")
            return None
    
    async def calculate_liquidity_metrics(
        self,
        symbol: str,
        depth: OrderBookDepth
    ) -> LiquidityMetrics:
        """Likvidlik metrikalarini hisoblash"""
        try:
            # Spread in basis points
            spread_bps = (depth.spread / depth.mid_price) * Decimal('10000')
            
            # Calculate depth at different levels
            bid_depth_1pct = self._calculate_depth(
                depth.bids,
                depth.best_bid,
                Decimal('0.01'),
                'bid'
            )
            ask_depth_1pct = self._calculate_depth(
                depth.asks,
                depth.best_ask,
                Decimal('0.01'),
                'ask'
            )
            total_depth_1pct = bid_depth_1pct + ask_depth_1pct
            
            bid_depth_5pct = self._calculate_depth(
                depth.bids,
                depth.best_bid,
                Decimal('0.05'),
                'bid'
            )
            ask_depth_5pct = self._calculate_depth(
                depth.asks,
                depth.best_ask,
                Decimal('0.05'),
                'ask'
            )
            total_depth_5pct = bid_depth_5pct + ask_depth_5pct
            
            # Order book imbalance
            imbalance_ratio = Decimal('0')
            total_volume = bid_depth_1pct + ask_depth_1pct
            if total_volume > 0:
                imbalance_ratio = (
                    (bid_depth_1pct - ask_depth_1pct) / total_volume
                )
            
            # Market pressure (0-100)
            buy_pressure = Decimal('50') + (imbalance_ratio * Decimal('50'))
            sell_pressure = Decimal('100') - buy_pressure
            
            # Liquidity score (0-100)
            liquidity_score = await self._calculate_liquidity_score(
                spread_bps,
                total_depth_1pct,
                total_depth_5pct
            )
            
            # Effective spread (would need trade data)
            effective_spread = spread_bps
            
            metrics = LiquidityMetrics(
                symbol=symbol,
                timestamp=datetime.now(),
                spread_bps=spread_bps,
                effective_spread=effective_spread,
                bid_depth_1pct=bid_depth_1pct,
                ask_depth_1pct=ask_depth_1pct,
                total_depth_1pct=total_depth_1pct,
                bid_depth_5pct=bid_depth_5pct,
                ask_depth_5pct=ask_depth_5pct,
                total_depth_5pct=total_depth_5pct,
                imbalance_ratio=imbalance_ratio,
                buy_pressure=buy_pressure,
                sell_pressure=sell_pressure,
                liquidity_score=liquidity_score
            )
            
            # Store metrics
            self.liquidity_history[symbol].append(metrics)
            
            logger.info(
                f"Liquidity metrics for {symbol}: "
                f"score={liquidity_score:.1f}, imbalance={imbalance_ratio:.3f}"
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating liquidity metrics: {e}")
            return None
    
    def _calculate_depth(
        self,
        levels: List[OrderBookLevel],
        best_price: Decimal,
        threshold_pct: Decimal,
        side: str
    ) -> Decimal:
        """Ma'lum bir price range ichidagi depth hisoblash"""
        try:
            total_volume = Decimal('0')
            
            for level in levels:
                # Calculate distance from best price
                if side == 'bid':
                    distance_pct = (best_price - level.price) / best_price
                else:  # ask
                    distance_pct = (level.price - best_price) / best_price
                
                if distance_pct <= threshold_pct:
                    total_volume += level.volume
                else:
                    break  # Levels are sorted
            
            return total_volume
            
        except Exception as e:
            logger.error(f"Error calculating depth: {e}")
            return Decimal('0')
    
    async def _calculate_liquidity_score(
        self,
        spread_bps: Decimal,
        depth_1pct: Decimal,
        depth_5pct: Decimal
    ) -> Decimal:
        """Liquidity score hisoblash (0-100)"""
        try:
            score = Decimal('0')
            
            # Spread component (0-40 points)
            # Tight spread = high score
            if spread_bps <= 10:
                spread_score = Decimal('40')
            elif spread_bps <= 50:
                spread_score = Decimal('40') - (spread_bps - Decimal('10')) / Decimal('40') * Decimal('20')
            elif spread_bps <= 100:
                spread_score = Decimal('20') - (spread_bps - Decimal('50')) / Decimal('50') * Decimal('20')
            else:
                spread_score = Decimal('0')
            
            score += spread_score
            
            # Depth component (0-60 points)
            # High depth = high score
            # Assuming good depth is 100+ BTC equivalent
            depth_score = min(float(depth_1pct) / 100 * 30, 30)
            score += Decimal(str(depth_score))
            
            depth_5pct_score = min(float(depth_5pct) / 500 * 30, 30)
            score += Decimal(str(depth_5pct_score))
            
            return min(score, Decimal('100'))
            
        except Exception as e:
            logger.error(f"Error calculating liquidity score: {e}")
            return Decimal('50')
    
    async def process_trade(
        self,
        symbol: str,
        price: Decimal,
        volume: Decimal,
        side: str,
        timestamp: Optional[datetime] = None
    ):
        """Trade'ni qayd etish va cumulative delta yangilash"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Record trade
            self.trade_flow[symbol].append((timestamp, price, volume, side))
            
            # Update cumulative delta
            if side == 'buy':
                self.cumulative_delta[symbol] += volume
            else:
                self.cumulative_delta[symbol] -= volume
            
        except Exception as e:
            logger.error(f"Error processing trade: {e}")
    
    async def calculate_volume_profile(
        self,
        symbol: str,
        time_window_minutes: int = 60
    ) -> Optional[VolumeProfile]:
        """Volume profile hisoblash"""
        try:
            since = datetime.now() - timedelta(minutes=time_window_minutes)
            
            # Get trades in window
            trades = [
                (ts, price, volume, side)
                for ts, price, volume, side in self.trade_flow[symbol]
                if ts >= since
            ]
            
            if not trades:
                return None
            
            # Group by price levels (round to nearest price tick)
            price_tick = Decimal('10')  # Example: round to nearest $10
            
            price_levels = defaultdict(lambda: Decimal('0'))
            for _, price, volume, _ in trades:
                rounded_price = (price // price_tick) * price_tick
                price_levels[rounded_price] += volume
            
            # Find point of control (highest volume price)
            poc = max(price_levels.items(), key=lambda x: x[1])[0]
            
            # Calculate value area (70% of volume)
            total_volume = sum(price_levels.values())
            value_area_volume = total_volume * Decimal('0.7')
            
            # Sort by volume
            sorted_levels = sorted(
                price_levels.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Find value area range
            cumulative_vol = Decimal('0')
            value_area_prices = []
            
            for price, volume in sorted_levels:
                if cumulative_vol >= value_area_volume:
                    break
                cumulative_vol += volume
                value_area_prices.append(price)
            
            vah = max(value_area_prices) if value_area_prices else poc
            val = min(value_area_prices) if value_area_prices else poc
            
            # Volume distribution by side
            buy_volume = sum(
                volume for _, _, volume, side in trades if side == 'buy'
            )
            sell_volume = sum(
                volume for _, _, volume, side in trades if side == 'sell'
            )
            
            profile = VolumeProfile(
                symbol=symbol,
                timestamp=datetime.now(),
                price_levels=dict(price_levels),
                value_area_high=vah,
                value_area_low=val,
                point_of_control=poc,
                volume_distribution={
                    'buy': buy_volume,
                    'sell': sell_volume,
                    'total': total_volume,
                    'buy_percent': (buy_volume / total_volume * Decimal('100')) if total_volume > 0 else Decimal('0')
                }
            )
            
            # Store profile
            self.volume_profiles[symbol] = profile
            
            logger.info(
                f"Volume profile for {symbol}: "
                f"POC=${poc:.2f}, VA=${val:.2f}-${vah:.2f}"
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error calculating volume profile: {e}")
            return None
    
    async def generate_order_flow_signals(
        self,
        symbol: str
    ) -> List[OrderFlowSignal]:
        """Order flow asosida trading signallar yaratish"""
        try:
            signals = []
            
            # Get latest metrics
            if not self.liquidity_history[symbol]:
                return signals
            
            latest_liquidity = self.liquidity_history[symbol][-1]
            
            # Signal 1: Order book imbalance
            if abs(latest_liquidity.imbalance_ratio) > Decimal('0.3'):
                signal_type = 'bullish' if latest_liquidity.imbalance_ratio > 0 else 'bearish'
                strength = min(abs(float(latest_liquidity.imbalance_ratio)) * 200, 100)
                
                signals.append(OrderFlowSignal(
                    signal_type=signal_type,
                    strength=Decimal(str(strength)),
                    confidence=Decimal('70'),
                    indicators={
                        'imbalance_ratio': float(latest_liquidity.imbalance_ratio),
                        'buy_pressure': float(latest_liquidity.buy_pressure),
                        'sell_pressure': float(latest_liquidity.sell_pressure)
                    },
                    description=f"Strong {'buy' if signal_type == 'bullish' else 'sell'} pressure from order book imbalance",
                    timestamp=datetime.now()
                ))
            
            # Signal 2: Cumulative delta
            cumul_delta = self.cumulative_delta[symbol]
            if abs(cumul_delta) > Decimal('10'):  # Threshold
                signal_type = 'bullish' if cumul_delta > 0 else 'bearish'
                strength = min(abs(float(cumul_delta)) * 5, 100)
                
                signals.append(OrderFlowSignal(
                    signal_type=signal_type,
                    strength=Decimal(str(strength)),
                    confidence=Decimal('75'),
                    indicators={
                        'cumulative_delta': float(cumul_delta)
                    },
                    description=f"Cumulative delta shows {'buying' if signal_type == 'bullish' else 'selling'} dominance",
                    timestamp=datetime.now()
                ))
            
            # Signal 3: Liquidity absorption
            if len(self.liquidity_history[symbol]) >= 10:
                recent = list(self.liquidity_history[symbol])[-10:]
                
                depth_trend = [float(m.total_depth_1pct) for m in recent]
                if len(depth_trend) > 1:
                    avg_depth = statistics.mean(depth_trend)
                    current_depth = depth_trend[-1]
                    
                    if current_depth < avg_depth * 0.5:  # 50% drop in liquidity
                        # Liquidity being absorbed
                        signals.append(OrderFlowSignal(
                            signal_type='neutral',
                            strength=Decimal('60'),
                            confidence=Decimal('65'),
                            indicators={
                                'depth_drop_percent': ((avg_depth - current_depth) / avg_depth) * 100,
                                'current_depth': current_depth,
                                'avg_depth': avg_depth
                            },
                            description="Significant liquidity absorption detected",
                            timestamp=datetime.now()
                        ))
            
            # Signal 4: Volume profile analysis
            if symbol in self.volume_profiles:
                profile = self.volume_profiles[symbol]
                buy_pct = profile.volume_distribution.get('buy_percent', Decimal('50'))
                
                if buy_pct > Decimal('65'):
                    signals.append(OrderFlowSignal(
                        signal_type='bullish',
                        strength=Decimal('70'),
                        confidence=Decimal('70'),
                        indicators={
                            'buy_percent': float(buy_pct),
                            'poc': float(profile.point_of_control)
                        },
                        description=f"Strong buying volume ({buy_pct:.1f}%) detected",
                        timestamp=datetime.now()
                    ))
                elif buy_pct < Decimal('35'):
                    signals.append(OrderFlowSignal(
                        signal_type='bearish',
                        strength=Decimal('70'),
                        confidence=Decimal('70'),
                        indicators={
                            'buy_percent': float(buy_pct),
                            'poc': float(profile.point_of_control)
                        },
                        description=f"Strong selling volume ({100 - float(buy_pct):.1f}%) detected",
                        timestamp=datetime.now()
                    ))
            
            logger.info(f"Generated {len(signals)} order flow signals for {symbol}")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating order flow signals: {e}")
            return []
    
    async def get_market_depth_chart_data(
        self,
        symbol: str,
        depth_levels: int = 20
    ) -> Dict:
        """Market depth chart uchun ma'lumot"""
        try:
            if not self.orderbook_snapshots[symbol]:
                return {}
            
            latest = self.orderbook_snapshots[symbol][-1]
            
            # Get top N levels
            bids = latest.bids[:depth_levels]
            asks = latest.asks[:depth_levels]
            
            # Calculate cumulative volume
            bid_cumulative = []
            ask_cumulative = []
            
            cumul_vol = Decimal('0')
            for level in reversed(bids):
                cumul_vol += level.volume
                bid_cumulative.append({
                    'price': float(level.price),
                    'volume': float(cumul_vol)
                })
            
            cumul_vol = Decimal('0')
            for level in asks:
                cumul_vol += level.volume
                ask_cumulative.append({
                    'price': float(level.price),
                    'volume': float(cumul_vol)
                })
            
            return {
                'symbol': symbol,
                'timestamp': latest.timestamp.isoformat(),
                'bids': bid_cumulative,
                'asks': ask_cumulative,
                'spread': float(latest.spread),
                'mid_price': float(latest.mid_price)
            }
            
        except Exception as e:
            logger.error(f"Error getting market depth chart data: {e}")
            return {}
    
    async def get_orderflow_summary(self, symbol: str) -> Dict:
        """Order flow xulosa"""
        try:
            summary = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'liquidity': {},
                'volume_profile': {},
                'signals': [],
                'cumulative_delta': float(self.cumulative_delta.get(symbol, Decimal('0')))
            }
            
            # Latest liquidity
            if self.liquidity_history[symbol]:
                latest = self.liquidity_history[symbol][-1]
                summary['liquidity'] = {
                    'score': float(latest.liquidity_score),
                    'spread_bps': float(latest.spread_bps),
                    'imbalance': float(latest.imbalance_ratio),
                    'buy_pressure': float(latest.buy_pressure),
                    'sell_pressure': float(latest.sell_pressure)
                }
            
            # Volume profile
            if symbol in self.volume_profiles:
                profile = self.volume_profiles[symbol]
                summary['volume_profile'] = {
                    'poc': float(profile.point_of_control),
                    'value_area_high': float(profile.value_area_high),
                    'value_area_low': float(profile.value_area_low),
                    'buy_percent': float(profile.volume_distribution.get('buy_percent', 0))
                }
            
            # Signals
            signals = await self.generate_order_flow_signals(symbol)
            summary['signals'] = [
                {
                    'type': s.signal_type,
                    'strength': float(s.strength),
                    'confidence': float(s.confidence),
                    'description': s.description
                }
                for s in signals
            ]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting orderflow summary: {e}")
            return {}


async def main():
    """Test function"""
    analyzer = OrderFlowAnalyzer()
    
    # Sample orderbook
    bids = [
        (Decimal('50000'), Decimal('1.5')),
        (Decimal('49990'), Decimal('2.0')),
        (Decimal('49980'), Decimal('1.8'))
    ]
    
    asks = [
        (Decimal('50010'), Decimal('1.2')),
        (Decimal('50020'), Decimal('2.5')),
        (Decimal('50030'), Decimal('1.9'))
    ]
    
    # Analyze orderbook
    depth = await analyzer.analyze_orderbook('BTC/USDT', bids, asks)
    
    if depth:
        print(f"Spread: {depth.spread_percent:.3f}%")
        print(f"Mid Price: ${depth.mid_price:.2f}")
    
    # Calculate liquidity
    metrics = await analyzer.calculate_liquidity_metrics('BTC/USDT', depth)
    
    if metrics:
        print(f"\nLiquidity Score: {metrics.liquidity_score:.1f}/100")
        print(f"Order Book Imbalance: {metrics.imbalance_ratio:.3f}")
        print(f"Buy Pressure: {metrics.buy_pressure:.1f}%")
    
    # Process some trades
    await analyzer.process_trade('BTC/USDT', Decimal('50010'), Decimal('0.5'), 'buy')
    await analyzer.process_trade('BTC/USDT', Decimal('50015'), Decimal('1.2'), 'buy')
    await analyzer.process_trade('BTC/USDT', Decimal('50005'), Decimal('0.8'), 'sell')
    
    # Generate signals
    signals = await analyzer.generate_order_flow_signals('BTC/USDT')
    print(f"\nGenerated {len(signals)} signals:")
    for signal in signals:
        print(f"- {signal.signal_type}: {signal.description} (strength: {signal.strength:.1f})")


if __name__ == '__main__':
    asyncio.run(main())
