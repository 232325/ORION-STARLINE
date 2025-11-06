"""
Order Book Analysis Module
=========================

Order book tahlil moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from collections import defaultdict, deque
import heapq
import warnings
warnings.filterwarnings('ignore')


@dataclass
class OrderBookEntry:
    """Order book entry"""
    price: float
    volume: float
    timestamp: pd.Timestamp
    order_id: str


@dataclass
class OrderBookLevel:
    """Order book level (aggregated)"""
    price: float
    total_volume: float
    order_count: int
    timestamp: pd.Timestamp


class OrderBookAnalyzer:
    """Order book tahlil moduli"""
    
    def __init__(self, max_levels: int = 20):
        self.max_levels = max_levels
        self.order_book_history = deque(maxlen=1000)
        
    def create_order_book_snapshot(self, mid_price: float, spread_bps: float,
                                 volume_profile: Dict[str, List[float]]) -> Dict[str, any]:
        """
        Order book snapshot yaratish (simulation based)
        
        Args:
            mid_price: Joriy narx
            spread_bps: Spread basis points da
            volume_profile: {'bid_volumes': [...], 'ask_volumes': [...], 
                           'bid_prices': [...], 'ask_prices': [...]}
        """
        spread = spread_bps * 0.0001 * mid_price
        
        # Generate price levels
        bid_prices = []
        ask_prices = []
        
        # Bid side (prices below mid)
        for i in range(1, self.max_levels + 1):
            bid_price = mid_price - (i * spread / self.max_levels)
            bid_prices.append(bid_price)
        
        # Ask side (prices above mid)  
        for i in range(1, self.max_levels + 1):
            ask_price = mid_price + (i * spread / self.max_levels)
            ask_prices.append(ask_price)
        
        # Create order book structure
        order_book = {
            'timestamp': pd.Timestamp.now(),
            'mid_price': mid_price,
            'spread': spread,
            'spread_bps': spread_bps,
            'bids': [],
            'asks': [],
            'order_book_imbalance': 0,
            'order_concentration': 0,
            'market_pressure': 0
        }
        
        # Populate bid side
        bid_volumes = volume_profile.get('bid_volumes', [100000] * self.max_levels)
        bid_volumes = bid_volumes[:self.max_levels]  # Ensure correct length
        
        total_bid_volume = sum(bid_volumes)
        for i, (price, volume) in enumerate(zip(bid_prices, bid_volumes)):
            order_book['bids'].append({
                'price': price,
                'volume': volume,
                'level': i + 1,
                'cumulative_volume': sum(bid_volumes[:i+1])
            })
        
        # Populate ask side
        ask_volumes = volume_profile.get('ask_volumes', [100000] * self.max_levels)
        ask_volumes = ask_volumes[:self.max_levels]  # Ensure correct length
        
        total_ask_volume = sum(ask_volumes)
        for i, (price, volume) in enumerate(zip(ask_prices, ask_volumes)):
            order_book['asks'].append({
                'price': price,
                'volume': volume,
                'level': i + 1,
                'cumulative_volume': sum(ask_volumes[:i+1])
            })
        
        # Calculate derived metrics
        order_book['order_book_imbalance'] = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
        order_book['order_concentration'] = self._calculate_concentration(bid_volumes + ask_volumes)
        order_book['market_pressure'] = self._calculate_market_pressure(order_book)
        
        return order_book
    
    def _calculate_concentration(self, volumes: List[float]) -> float:
        """Order concentration hisoblash (Herfindahl-Hirschman Index)"""
        total_volume = sum(volumes)
        if total_volume == 0:
            return 0
        
        # Normalize volumes
        normalized_volumes = [v / total_volume for v in volumes]
        
        # HHI (0-1 scale, higher = more concentrated)
        hhi = sum(v**2 for v in normalized_volumes)
        return hhi
    
    def _calculate_market_pressure(self, order_book: Dict[str, any]) -> float:
        """Market pressure hisoblash"""
        # Compare bid/ask volume at different levels
        
        # Volume at best levels
        best_bid_volume = order_book['bids'][0]['volume'] if order_book['bids'] else 0
        best_ask_volume = order_book['asks'][0]['volume'] if order_book['asks'] else 0
        
        # Volume at 5 levels deep
        depth_5_bid = sum(level['volume'] for level in order_book['bids'][:5])
        depth_5_ask = sum(level['volume'] for level in order_book['asks'][:5])
        
        # Market pressure score (-1 to 1)
        if depth_5_bid + depth_5_ask > 0:
            pressure = (depth_5_bid - depth_5_ask) / (depth_5_bid + depth_5_ask)
        else:
            pressure = 0
        
        return pressure
    
    def analyze_order_book_snapshots(self, snapshots: List[Dict]) -> pd.DataFrame:
        """Order book snapshotlarini tahlil qilish"""
        if not snapshots:
            return pd.DataFrame()
        
        # Convert to structured data
        analysis_data = []
        
        for snapshot in snapshots:
            # Basic metrics
            spread = snapshot.get('spread', 0)
            spread_bps = snapshot.get('spread_bps', 0)
            imbalance = snapshot.get('order_book_imbalance', 0)
            concentration = snapshot.get('order_concentration', 0)
            pressure = snapshot.get('market_pressure', 0)
            
            # Depth metrics
            bid_depth = sum(level['cumulative_volume'] for level in snapshot.get('bids', []))
            ask_depth = sum(level['cumulative_volume'] for level in snapshot.get('asks', []))
            total_depth = bid_depth + ask_depth
            
            # Price levels metrics
            best_bid = snapshot['bids'][0]['price'] if snapshot.get('bids') else 0
            best_ask = snapshot['asks'][0]['price'] if snapshot.get('asks') else 0
            
            # Volume distribution
            bid_volumes = [level['volume'] for level in snapshot.get('bids', [])]
            ask_volumes = [level['volume'] for level in snapshot.get('asks', [])]
            
            # Advanced metrics
            volume_weighted_spread = self._calculate_vws(snapshot)
            effective_spread = self._calculate_effective_spread(snapshot)
            
            analysis_data.append({
                'timestamp': snapshot.get('timestamp', pd.Timestamp.now()),
                'spread': spread,
                'spread_bps': spread_bps,
                'order_book_imbalance': imbalance,
                'order_concentration': concentration,
                'market_pressure': pressure,
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'total_depth': total_depth,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'mid_price': (best_bid + best_ask) / 2,
                'effective_spread': effective_spread,
                'volume_weighted_spread': volume_weighted_spread,
                'bid_volume_first5': sum(bid_volumes[:5]),
                'ask_volume_first5': sum(ask_volumes[:5]),
                'avg_bid_volume': np.mean(bid_volumes) if bid_volumes else 0,
                'avg_ask_volume': np.mean(ask_volumes) if ask_volumes else 0
            })
        
        df = pd.DataFrame(analysis_data)
        df.set_index('timestamp', inplace=True)
        
        # Add derived metrics
        df['depth_ratio'] = df['bid_depth'] / df['ask_depth']
        df['spread_volatility'] = df['spread_bps'].rolling(20).std()
        df['imbalance_volatility'] = df['order_book_imbalance'].rolling(20).std()
        
        return df
    
    def _calculate_vws(self, snapshot: Dict) -> float:
        """Volume-weighted spread hisoblash"""
        bid_levels = snapshot.get('bids', [])
        ask_levels = snapshot.get('asks', [])
        
        if not bid_levels or not ask_levels:
            return 0
        
        # Calculate VW spread using top 5 levels
        total_weighted_price = 0
        total_weight = 0
        
        # Bid contribution (negative)
        for level in bid_levels[:5]:
            weight = level['volume']
            total_weighted_price -= weight * level['price']
            total_weight += weight
        
        # Ask contribution (positive)
        for level in ask_levels[:5]:
            weight = level['volume']
            total_weighted_price += weight * level['price']
            total_weight += weight
        
        if total_weight > 0:
            return total_weighted_price / total_weight
        else:
            return 0
    
    def _calculate_effective_spread(self, snapshot: Dict) -> float:
        """Effective spread hisoblash"""
        bid_levels = snapshot.get('bids', [])
        ask_levels = snapshot.get('asks', [])
        
        if not bid_levels or not ask_levels:
            return 0
        
        # Mid price
        mid = (bid_levels[0]['price'] + ask_levels[0]['price']) / 2
        
        # Volume at mid
        bid_mid_volume = bid_levels[0]['volume']
        ask_mid_volume = ask_levels[0]['volume']
        
        # Effective spread weighted by volume
        if bid_mid_volume + ask_mid_volume > 0:
            effective_spread = (
                (ask_levels[0]['price'] - mid) * bid_mid_volume +
                (mid - bid_levels[0]['price']) * ask_mid_volume
            ) / (bid_mid_volume + ask_mid_volume)
        else:
            effective_spread = (ask_levels[0]['price'] - bid_levels[0]['price']) / 2
        
        return effective_spread
    
    def detect_order_book_patterns(self, data: pd.DataFrame) -> Dict[str, List[pd.Timestamp]]:
        """Order book patternlarini aniqlash"""
        patterns = {}
        
        if data.empty:
            return patterns
        
        # 1. Spread widening/narrowing patterns
        spread_ma = data['spread_bps'].rolling(10).mean()
        spread_std = data['spread_bps'].rolling(10).std()
        
        # Spread widening
        widening_threshold = spread_ma + 1.5 * spread_std
        patterns['spread_widening'] = data[data['spread_bps'] > widening_threshold].index.tolist()
        
        # Spread narrowing
        narrowing_threshold = spread_ma - 1.5 * spread_std
        patterns['spread_narrowing'] = data[data['spread_bps'] < narrowing_threshold].index.tolist()
        
        # 2. Order book imbalance patterns
        imbalance_ma = data['order_book_imbalance'].rolling(10).mean()
        
        # Heavy bid imbalance
        patterns['bid_pressure'] = data[data['order_book_imbalance'] > 0.3].index.tolist()
        
        # Heavy ask imbalance
        patterns['ask_pressure'] = data[data['order_book_imbalance'] < -0.3].index.tolist()
        
        # 3. Concentration patterns (rearrangement)
        concentration_ma = data['order_concentration'].rolling(10).mean()
        patterns['high_concentration'] = data[data['order_concentration'] > concentration_ma * 1.2].index.tolist()
        patterns['low_concentration'] = data[data['order_concentration'] < concentration_ma * 0.8].index.tolist()
        
        # 4. Depth patterns
        depth_ma = data['total_depth'].rolling(20).mean()
        patterns['deep_market'] = data[data['total_depth'] > depth_ma * 1.5].index.tolist()
        patterns['shallow_market'] = data[data['total_depth'] < depth_ma * 0.5].index.tolist()
        
        # 5. Sudden changes (volume or price shocks)
        volume_change = data['total_depth'].pct_change().abs()
        price_change = data['mid_price'].pct_change().abs()
        
        patterns['volume_shock'] = data[volume_change > 0.5].index.tolist()
        patterns['price_shock'] = data[price_change > 0.01].index.tolist()
        
        return patterns
    
    def simulate_market_impact(self, trade_volume: float, trade_side: str,
                             order_book: Dict) -> Dict[str, float]:
        """Trade uchun market impact simulatsiyasi"""
        if trade_side.lower() not in ['buy', 'sell']:
            raise ValueError("Trade side must be 'buy' or 'sell'")
        
        # Determine which side to consume
        levels = order_book['asks'] if trade_side.lower() == 'buy' else order_book['bids']
        
        remaining_volume = trade_volume
        total_cost = 0
        total_volume_consumed = 0
        price_levels_consumed = 0
        
        for level in levels:
            if remaining_volume <= 0:
                break
            
            volume_to_consume = min(remaining_volume, level['volume'])
            cost = volume_to_consume * level['price']
            
            total_cost += cost
            total_volume_consumed += volume_to_consume
            remaining_volume -= volume_to_consume
            price_levels_consumed += 1
        
        # Calculate metrics
        avg_execution_price = total_cost / total_volume_consumed if total_volume_consumed > 0 else 0
        
        mid_price = (order_book.get('best_bid', 0) + order_book.get('best_ask', 0)) / 2
        
        if trade_side.lower() == 'buy':
            price_impact = avg_execution_price - mid_price
        else:
            price_impact = mid_price - avg_execution_price
        
        # Impact as percentage
        price_impact_pct = (price_impact / mid_price) * 100 if mid_price > 0 else 0
        price_impact_bps = price_impact_pct * 100  # basis points
        
        return {
            'trade_volume': trade_volume,
            'volume_executed': total_volume_consumed,
            'volume_remaining': remaining_volume,
            'price_levels_consumed': price_levels_consumed,
            'avg_execution_price': avg_execution_price,
            'mid_price': mid_price,
            'price_impact': price_impact,
            'price_impact_pct': price_impact_pct,
            'price_impact_bps': price_impact_bps,
            'execution_completeness': total_volume_consumed / trade_volume * 100,
            'slippage_cost': total_volume_consumed * price_impact
        }
    
    def optimize_slicing_strategy(self, total_volume: float, max_impact_bps: float,
                                order_book: Dict, num_slices: int = 5) -> Dict[str, any]:
        """Trade slicing strategiyasini optimallash"""
        
        # Calculate optimal slice sizes
        strategies = []
        
        for slices in range(1, num_slices + 1):
            slice_volume = total_volume / slices
            
            # Simulate impact for this slice size
            buy_impact = self.simulate_market_impact(slice_volume, 'buy', order_book)
            sell_impact = self.simulate_market_impact(slice_volume, 'sell', order_book)
            
            # Average impact (worst case)
            avg_impact = max(buy_impact['price_impact_bps'], sell_impact['price_impact_bps'])
            
            strategies.append({
                'num_slices': slices,
                'slice_volume': slice_volume,
                'buy_impact_bps': buy_impact['price_impact_bps'],
                'sell_impact_bps': sell_impact['price_impact_bps'],
                'avg_impact_bps': avg_impact,
                'exceeds_limit': avg_impact > max_impact_bps,
                'execution_time_factor': slices,  # More slices = longer execution
                'market_impact_cost': slice_volume * avg_impact * 0.0001
            })
        
        # Find optimal strategy
        feasible_strategies = [s for s in strategies if not s['exceeds_limit']]
        
        if feasible_strategies:
            # Choose strategy with best balance of impact and time
            best_strategy = min(feasible_strategies, 
                              key=lambda x: x['avg_impact_bps'] * x['execution_time_factor'])
        else:
            # Choose least bad strategy
            best_strategy = min(strategies, key=lambda x: x['avg_impact_bps'])
        
        return {
            'total_volume': total_volume,
            'max_impact_bps': max_impact_bps,
            'strategies': strategies,
            'recommended_strategy': best_strategy,
            'implementation_plan': self._create_implementation_plan(best_strategy, order_book)
        }
    
    def _create_implementation_plan(self, strategy: Dict, order_book: Dict) -> List[Dict]:
        """Implementation plan yaratish"""
        plan = []
        slice_volume = strategy['slice_volume']
        num_slices = strategy['num_slices']
        
        for i in range(num_slices):
            # Simulate market conditions for each slice
            # (In reality, this would consider time-based changes)
            
            buy_impact = self.simulate_market_impact(slice_volume, 'buy', order_book)
            sell_impact = self.simulate_market_impact(slice_volume, 'sell', order_book)
            
            plan.append({
                'slice_number': i + 1,
                'volume': slice_volume,
                'buy_impact_bps': buy_impact['price_impact_bps'],
                'sell_impact_bps': sell_impact['price_impact_bps'],
                'execution_timing': f'Slice {i + 1} of {num_slices}',
                'risk_factors': [
                    'Market conditions may change',
                    'Volume may become less available',
                    'Competition from other traders'
                ]
            })
        
        return plan
    
    def analyze_liquidity_distribution(self, order_book: Dict) -> Dict[str, float]:
        """Liquidity taqsimlanishini tahlil qilish"""
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])
        
        if not bids and not asks:
            return {}
        
        # Calculate distribution metrics
        all_bid_volumes = [level['volume'] for level in bids]
        all_ask_volumes = [level['volume'] for level in asks]
        
        total_bid_volume = sum(all_bid_volumes)
        total_ask_volume = sum(all_ask_volumes)
        
        # Liquidity distribution by distance from mid
        mid_price = order_book.get('mid_price', 0)
        
        # Calculate weighted average distance from mid
        bid_weighted_distance = 0
        ask_weighted_distance = 0
        
        for level in bids:
            if total_bid_volume > 0:
                distance = (mid_price - level['price']) / mid_price
                weight = level['volume'] / total_bid_volume
                bid_weighted_distance += distance * weight
        
        for level in asks:
            if total_ask_volume > 0:
                distance = (level['price'] - mid_price) / mid_price
                weight = level['volume'] / total_ask_volume
                ask_weighted_distance += distance * weight
        
        # Top-of-book concentration
        top_levels_volume = 0
        if bids:
            top_levels_volume += bids[0]['volume']
        if asks:
            top_levels_volume += asks[0]['volume']
        
        total_volume = total_bid_volume + total_ask_volume
        top_concentration = top_levels_volume / total_volume if total_volume > 0 else 0
        
        return {
            'total_bid_volume': total_bid_volume,
            'total_ask_volume': total_ask_volume,
            'bid_ask_ratio': total_bid_volume / total_ask_volume if total_ask_volume > 0 else 0,
            'weighted_bid_distance': bid_weighted_distance,
            'weighted_ask_distance': ask_weighted_distance,
            'top_levels_concentration': top_concentration,
            'liquidity_skew': (bid_weighted_distance - ask_weighted_distance),
            'effective_spread_volumes': self._calculate_effective_spread_volumes(bids, asks),
            'liquidity_availability_score': self._calculate_liquidity_score(bids, asks)
        }
    
    def _calculate_effective_spread_volumes(self, bids: List[Dict], asks: List[Dict]) -> Dict[str, float]:
        """Volume-adjusted effective spread hisoblash"""
        if not bids or not asks:
            return {'effective_spread_volume': 0}
        
        # Volume-weighted spread
        bid_price_volume = sum(level['price'] * level['volume'] for level in bids[:3])
        ask_price_volume = sum(level['price'] * level['volume'] for level in asks[:3])
        bid_volume_total = sum(level['volume'] for level in bids[:3])
        ask_volume_total = sum(level['volume'] for level in asks[:3])
        
        if bid_volume_total > 0 and ask_volume_total > 0:
            avg_bid = bid_price_volume / bid_volume_total
            avg_ask = ask_price_volume / ask_volume_total
            effective_spread_volume = avg_ask - avg_bid
        else:
            effective_spread_volume = asks[0]['price'] - bids[0]['price']
        
        return {'effective_spread_volume': effective_spread_volume}
    
    def _calculate_liquidity_score(self, bids: List[Dict], asks: List[Dict]) -> float:
        """Liquidity score hisoblash (0-1 scale)"""
        if not bids or not asks:
            return 0
        
        # Factors: total volume, distribution, proximity to mid
        total_volume = sum(level['volume'] for level in bids + asks)
        
        # Normalize total volume (assuming 1M is excellent)
        volume_score = min(1.0, total_volume / 1000000)
        
        # Distribution score (more levels = better liquidity)
        distribution_score = min(1.0, len(bids + asks) / 20)  # 20 levels is good
        
        # Proximity score (closer to mid = better)
        mid_price = (bids[0]['price'] + asks[0]['price']) / 2
        
        avg_distance_bid = sum((mid_price - level['price']) / mid_price for level in bids[:5]) / min(5, len(bids))
        avg_distance_ask = sum((level['price'] - mid_price) / mid_price for level in asks[:5]) / min(5, len(asks))
        proximity_score = 1 - min(1.0, (avg_distance_bid + avg_distance_ask) / 2)
        
        # Combined score
        liquidity_score = (volume_score * 0.4 + 
                         distribution_score * 0.3 + 
                         proximity_score * 0.3)
        
        return liquidity_score
    
    def forecast_order_book_changes(self, recent_snapshots: List[Dict],
                                  horizon_minutes: int = 5) -> Dict[str, any]:
        """Order book o'zgarishlarini bashoratlash"""
        if len(recent_snapshots) < 3:
            return {'status': 'insufficient_data'}
        
        # Analyze trends
        spreads = [snap.get('spread_bps', 0) for snap in recent_snapshots]
        imbalances = [snap.get('order_book_imbalance', 0) for snap in recent_snapshots]
        depths = [snap.get('total_depth', 0) for snap in recent_snapshots]
        
        # Simple trend analysis
        spread_trend = np.polyfit(range(len(spreads)), spreads, 1)[0] if len(spreads) > 1 else 0
        imbalance_trend = np.polyfit(range(len(imbalances)), imbalances, 1)[0] if len(imbalances) > 1 else 0
        depth_trend = np.polyfit(range(len(depths)), depths, 1)[0] if len(depths) > 1 else 0
        
        # Volatility analysis
        spread_volatility = np.std(spreads)
        imbalance_volatility = np.std(imbalances)
        
        # Forecast ranges (simple extrapolation)
        latest_spread = spreads[-1]
        latest_imbalance = imbalances[-1]
        latest_depth = depths[-1]
        
        forecast = {
            'time_horizon_minutes': horizon_minutes,
            'spread_forecast': {
                'current': latest_spread,
                'trend': 'widening' if spread_trend > spread_volatility * 0.1 else 'narrowing' if spread_trend < -spread_volatility * 0.1 else 'stable',
                'predicted_range': [
                    max(0, latest_spread + spread_trend * horizon_minutes - spread_volatility),
                    latest_spread + spread_trend * horizon_minutes + spread_volatility
                ]
            },
            'imbalance_forecast': {
                'current': latest_imbalance,
                'trend': 'increasing' if imbalance_trend > imbalance_volatility * 0.1 else 'decreasing' if imbalance_trend < -imbalance_volatility * 0.1 else 'stable',
                'predicted_range': [
                    latest_imbalance + imbalance_trend * horizon_minutes - imbalance_volatility,
                    latest_imbalance + imbalance_trend * horizon_minutes + imbalance_volatility
                ]
            },
            'depth_forecast': {
                'current': latest_depth,
                'trend': 'increasing' if depth_trend > 0 else 'decreasing',
                'predicted_range': [
                    max(0, latest_depth + depth_trend * horizon_minutes - np.std(depths)),
                    latest_depth + depth_trend * horizon_minutes + np.std(depths)
                ]
            },
            'confidence': {
                'spread_confidence': 0.8 if len(spreads) > 10 else 0.5,
                'imbalance_confidence': 0.6 if len(imbalances) > 10 else 0.3,
                'depth_confidence': 0.7 if len(depths) > 10 else 0.4
            },
            'risk_factors': [
                'News events may cause sudden changes',
                'Large orders can rapidly deplete liquidity',
                'Market makers may adjust quotes',
                'Other participants may have conflicting views'
            ]
        }
        
        return forecast