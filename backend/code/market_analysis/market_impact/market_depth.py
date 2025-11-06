"""
Market Depth Analysis Module
===========================

Market depth tahlil moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from scipy import interpolate
import warnings
warnings.filterwarnings('ignore')


@dataclass
class OrderBookLevel:
    """Order book darajasi"""
    price: float
    volume: float
    cumulative_volume: float
    side: str  # 'bid' or 'ask'
    level: int


@dataclass
class MarketDepthSnapshot:
    """Market depth snapshot"""
    timestamp: pd.Timestamp
    best_bid: float
    best_ask: float
    spread: float
    mid_price: float
    bid_depth: float
    ask_depth: float
    total_depth: float
    order_book_imbalance: float
    price_impact_levels: Dict[float, float]


class MarketDepthAnalyzer:
    """Market depth tahlil moduli"""
    
    def __init__(self, max_levels: int = 20):
        self.max_levels = max_levels
        self.depth_cache = {}
    
    def simulate_order_book(self, current_price: float, volatility: float,
                          volume_profile: Dict[str, float]) -> List[OrderBookLevel]:
        """
        Real order book ma'lumotlari bo'lmaganda simulatsiya qilish
        """
        order_book = []
        spread_bps = 1  # 1 pip spread
        
        # Generate bid levels
        bid_volume = volume_profile.get('bid_base_volume', 100000)
        bid_decay = volume_profile.get('bid_decay_factor', 0.7)
        
        cumulative_bid_volume = 0
        for level in range(self.max_levels):
            level_bid_price = current_price - (level + 1) * spread_bps * 0.0001
            level_bid_volume = bid_volume * (bid_decay ** level)
            cumulative_bid_volume += level_bid_volume
            
            order_book.append(OrderBookLevel(
                price=level_bid_price,
                volume=level_bid_volume,
                cumulative_volume=cumulative_bid_volume,
                side='bid',
                level=level + 1
            ))
        
        # Generate ask levels
        ask_volume = volume_profile.get('ask_base_volume', 100000)
        ask_decay = volume_profile.get('ask_decay_factor', 0.7)
        
        cumulative_ask_volume = 0
        for level in range(self.max_levels):
            level_ask_price = current_price + (level + 1) * spread_bps * 0.0001
            level_ask_volume = ask_volume * (ask_decay ** level)
            cumulative_ask_volume += level_ask_volume
            
            order_book.append(OrderBookLevel(
                price=level_ask_price,
                volume=level_ask_volume,
                cumulative_volume=cumulative_ask_volume,
                side='ask',
                level=level + 1
            ))
        
        return order_book
    
    def analyze_market_depth(self, data: pd.DataFrame, 
                           volume_profile: Dict[str, float] = None) -> pd.DataFrame:
        """Market depth tahlil qilish"""
        if volume_profile is None:
            volume_profile = self._get_default_volume_profile(data)
        
        df = data.copy()
        
        # Create market depth snapshots for each timestamp
        depth_data = []
        
        for idx, row in df.iterrows():
            if isinstance(idx, pd.Timestamp):
                timestamp = idx
            else:
                timestamp = pd.Timestamp(idx)
            
            # Simulate order book
            order_book = self.simulate_order_book(
                current_price=row['close'],
                volatility=row.get('volatility', 0.02),
                volume_profile=volume_profile
            )
            
            # Calculate depth metrics
            best_bid = max([level.price for level in order_book if level.side == 'bid'])
            best_ask = min([level.price for level in order_book if level.side == 'ask'])
            spread = best_ask - best_bid
            mid_price = (best_bid + best_ask) / 2
            
            # Calculate depth
            bid_depth = sum([level.cumulative_volume for level in order_book if level.side == 'bid'])
            ask_depth = sum([level.cumulative_volume for level in order_book if level.side == 'ask'])
            total_depth = bid_depth + ask_depth
            
            # Order book imbalance
            order_book_imbalance = (bid_depth - ask_depth) / total_depth if total_depth > 0 else 0
            
            depth_data.append({
                'timestamp': timestamp,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': spread,
                'mid_price': mid_price,
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'total_depth': total_depth,
                'order_book_imbalance': order_book_imbalance
            })
        
        depth_df = pd.DataFrame(depth_data)
        depth_df.set_index('timestamp', inplace=True)
        
        # Merge with original data
        result = pd.concat([df, depth_df], axis=1)
        
        # Add derived metrics
        result['spread_bps'] = (result['spread'] / result['close']) * 10000
        result['depth_ratio'] = result['bid_depth'] / result['ask_depth']
        result['depth_concentration'] = self._calculate_depth_concentration(result)
        result['price_impact_threshold'] = self._calculate_price_impact_thresholds(result)
        
        return result
    
    def _get_default_volume_profile(self, data: pd.DataFrame) -> Dict[str, float]:
        """Standart volume profile olish"""
        avg_volume = data['volume'].mean()
        
        return {
            'bid_base_volume': avg_volume * 0.6,
            'ask_base_volume': avg_volume * 0.6,
            'bid_decay_factor': 0.75,
            'ask_decay_factor': 0.75
        }
    
    def _calculate_depth_concentration(self, data: pd.DataFrame) -> pd.Series:
        """Depth concentration hisoblash (top 5 levels vs total)"""
        # This would be more accurate with real order book data
        # For simulation, we'll use volume profile patterns
        
        concentration = pd.Series(index=data.index, dtype=float)
        
        # Simulate concentration based on volume characteristics
        volume_cv = data['volume'].rolling(20).std() / data['volume'].rolling(20).mean()
        volatility = data['close'].pct_change().rolling(20).std()
        
        # Higher volatility tends to spread volume across more levels
        # Lower volatility concentrates volume in top levels
        concentration = 1 - (volatility * 0.5 + volume_cv * 0.3)
        concentration = concentration.clip(0.3, 0.9)  # Reasonable bounds
        
        return concentration
    
    def _calculate_price_impact_thresholds(self, data: pd.DataFrame) -> pd.Series:
        """Price impact thresholdlarini hisoblash"""
        # Price at which different levels of impact occur
        # These are estimates based on market depth
        
        impact_thresholds = pd.Series(index=data.index, dtype=float)
        
        for idx, row in data.iterrows():
            # Estimate volume needed for 1 pip move
            current_price = row['close']
            total_depth = row.get('total_depth', 1000000)
            
            # Assuming 1 pip impact requires about 1% of total depth
            volume_for_1pip = total_depth * 0.01
            
            # Adjust based on spread
            spread_bps = row.get('spread_bps', 1.0)
            spread_adjustment = min(2.0, spread_bps / 1.0)  # Wider spreads = more impact
            
            impact_thresholds.loc[idx] = volume_for_1pip * spread_adjustment
        
        return impact_thresholds
    
    def calculate_price_impact_levels(self, order_book: List[OrderBookLevel],
                                    target_volume: float) -> Dict[str, float]:
        """Ma'lum volume uchun price impact darajalarini hisoblash"""
        # Separate bids and asks
        bids = [level for level in order_book if level.side == 'bid']
        asks = [level for level in order_book if level.side == 'ask']
        
        # Sort by price (descending for bids, ascending for asks)
        bids.sort(key=lambda x: x.price, reverse=True)
        asks.sort(key=lambda x: x.price)
        
        # Calculate impact levels for different volume percentages
        impact_levels = {
            'volume_taken': 0,
            'average_price': 0,
            'price_impact': 0,
            'impact_pips': 0
        }
        
        remaining_volume = target_volume
        total_volume_taken = 0
        weighted_price_sum = 0
        
        # Take from bid side
        for level in bids:
            if remaining_volume <= 0:
                break
            
            volume_to_take = min(remaining_volume, level.volume)
            weighted_price_sum += volume_to_take * level.price
            total_volume_taken += volume_to_take
            remaining_volume -= volume_to_take
        
        # Calculate metrics
        if total_volume_taken > 0:
            impact_levels['volume_taken'] = total_volume_taken
            impact_levels['average_price'] = weighted_price_sum / total_volume_taken
            
            # Estimate original price (mid of best bid/ask)
            original_price = (max([b.price for b in bids]) + 
                            min([a.price for a in asks])) / 2
            
            price_impact = impact_levels['average_price'] - original_price
            impact_levels['price_impact'] = price_impact
            impact_levels['impact_pips'] = price_impact / 0.0001  # Convert to pips
        
        return impact_levels
    
    def analyze_depth_profile(self, data: pd.DataFrame, window: int = 20) -> Dict[str, any]:
        """Depth profile tahlil qilish"""
        df = self.analyze_market_depth(data)
        
        # Calculate depth metrics
        metrics = {}
        
        # Average metrics
        metrics['avg_spread_bps'] = df['spread_bps'].mean()
        metrics['avg_bid_depth'] = df['bid_depth'].mean()
        metrics['avg_ask_depth'] = df['ask_depth'].mean()
        metrics['avg_total_depth'] = df['total_depth'].mean()
        metrics['avg_imbalance'] = df['order_book_imbalance'].mean()
        
        # Depth statistics
        metrics['spread_volatility'] = df['spread_bps'].std()
        metrics['depth_volatility'] = df['total_depth'].std()
        metrics['imbalance_volatility'] = df['order_book_imbalance'].std()
        
        # Depth trend analysis
        metrics['depth_trend'] = self._calculate_depth_trend(df['total_depth'], window)
        metrics['spread_trend'] = self._calculate_spread_trend(df['spread_bps'], window)
        
        # Depth clustering
        depth_clusters = self._cluster_depth_regimes(df['total_depth'])
        metrics['depth_clusters'] = depth_clusters
        
        # Price-depth correlation
        if 'close' in df.columns:
            price_depth_corr = df['close'].corr(df['total_depth'])
            metrics['price_depth_correlation'] = price_depth_corr
        
        # Session-based depth patterns
        if isinstance(df.index, pd.DatetimeIndex):
            session_depth = self._analyze_session_depth_patterns(df)
            metrics['session_patterns'] = session_depth
        
        return metrics
    
    def _calculate_depth_trend(self, depth: pd.Series, window: int) -> str:
        """Depth trend direction"""
        if len(depth) < window:
            return 'insufficient_data'
        
        recent_depth = depth.tail(window)
        slope = np.polyfit(range(len(recent_depth)), recent_depth.values, 1)[0]
        
        if slope > depth.std() * 0.1:
            return 'increasing'
        elif slope < -depth.std() * 0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_spread_trend(self, spread: pd.Series, window: int) -> str:
        """Spread trend direction"""
        if len(spread) < window:
            return 'insufficient_data'
        
        recent_spread = spread.tail(window)
        slope = np.polyfit(range(len(recent_spread)), recent_spread.values, 1)[0]
        
        if slope > spread.std() * 0.05:
            return 'widening'
        elif slope < -spread.std() * 0.05:
            return 'narrowing'
        else:
            return 'stable'
    
    def _cluster_depth_regimes(self, depth: pd.Series) -> Dict[str, any]:
        """Depth rejimlarini clustering"""
        from sklearn.cluster import KMeans
        
        if len(depth) < 50:
            return {'status': 'insufficient_data'}
        
        # Prepare data
        depth_values = depth.dropna().values.reshape(-1, 1)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(depth_values)
        
        # Analyze clusters
        unique_clusters = np.unique(clusters)
        cluster_stats = {}
        
        for cluster_id in unique_clusters:
            cluster_mask = clusters == cluster_id
            cluster_depths = depth.dropna()[cluster_mask]
            
            cluster_stats[f'regime_{cluster_id}'] = {
                'size': int(cluster_mask.sum()),
                'percentage': float(cluster_mask.sum() / len(clusters) * 100),
                'mean_depth': float(cluster_depths.mean()),
                'std_depth': float(cluster_depths.std()),
                'depth_range': [float(cluster_depths.min()), float(cluster_depths.max())]
            }
        
        return {
            'n_regimes': len(unique_clusters),
            'regime_statistics': cluster_stats,
            'regime_labels': clusters.tolist()
        }
    
    def _analyze_session_depth_patterns(self, data: pd.DataFrame) -> Dict[str, any]:
        """Session-based depth patternlari"""
        # Define sessions based on hour
        def get_session(hour):
            if 0 <= hour < 8:
                return 'Asian'
            elif 8 <= hour < 13:
                return 'Europe_Asia_Overlap'
            elif 13 <= hour < 17:
                return 'America_Europe_Overlap'
            elif 17 <= hour < 24:
                return 'American'
            else:
                return 'Unknown'
        
        data['session'] = data.index.hour.apply(get_session)
        
        # Calculate session statistics
        session_stats = data.groupby('session').agg({
            'total_depth': ['mean', 'std', 'min', 'max'],
            'spread_bps': ['mean', 'std'],
            'order_book_imbalance': ['mean', 'std']
        }).round(4)
        
        return {
            'session_statistics': session_stats.to_dict('index'),
            'deepest_session': session_stats[('total_depth', 'mean')].idxmax(),
            'shallowest_session': session_stats[('total_depth', 'mean')].idxmin(),
            'tightest_spread_session': session_stats[('spread_bps', 'mean')].idxmin(),
            'widest_spread_session': session_stats[('spread_bps', 'mean')].idxmax()
        }
    
    def forecast_depth_impact(self, trade_volume: float, data: pd.DataFrame,
                            price_levels: int = 10) -> Dict[str, float]:
        """Trade volume uchun depth impact bashoratlash"""
        df = self.analyze_market_depth(data)
        
        # Current market conditions
        current_total_depth = df['total_depth'].iloc[-1]
        current_spread = df['spread_bps'].iloc[-1]
        current_imbalance = df['order_book_imbalance'].iloc[-1]
        
        # Estimate impact
        volume_ratio = trade_volume / current_total_depth
        
        # Impact estimation models
        if volume_ratio <= 0.01:  # Small trade
            price_impact_bps = current_spread * 0.1 * volume_ratio * 100
        elif volume_ratio <= 0.05:  # Medium trade
            price_impact_bps = current_spread * 0.3 * (volume_ratio ** 0.8) * 100
        else:  # Large trade
            price_impact_bps = current_spread * 0.5 * (volume_ratio ** 0.6) * 100
        
        # Adjust for order book imbalance
        imbalance_adjustment = 1 + abs(current_imbalance) * 0.2
        price_impact_bps *= imbalance_adjustment
        
        # Calculate execution metrics
        estimated_levels_needed = int(volume_ratio * price_levels * 10)
        
        return {
            'trade_volume': trade_volume,
            'volume_ratio': volume_ratio,
            'estimated_price_impact_bps': price_impact_bps,
            'estimated_price_impact_pips': price_impact_bps / 1.0,  # 1 bps = 1 pip for major pairs
            'estimated_levels_needed': estimated_levels_needed,
            'execution_difficulty': 'easy' if volume_ratio <= 0.01 else 'moderate' if volume_ratio <= 0.05 else 'difficult',
            'market_impact_cost': trade_volume * price_impact_bps * 0.0001,
            'current_market_depth': current_total_depth,
            'current_spread_bps': current_spread,
            'imbalance_factor': imbalance_adjustment
        }
    
    def optimize_execution_strategy(self, total_volume: float, 
                                  max_impact: float, data: pd.DataFrame) -> Dict[str, any]:
        """Execution strategiyani optimallash"""
        df = self.analyze_market_depth(data)
        
        current_depth = df['total_depth'].iloc[-1]
        avg_depth = df['total_depth'].mean()
        
        # Strategy options
        strategies = []
        
        # 1. Aggressive execution (all at once)
        aggressive_volume = total_volume
        aggressive_impact = self.forecast_depth_impact(aggressive_volume, data)
        
        strategies.append({
            'name': 'aggressive',
            'description': 'Barcha volume ni birdan bajarish',
            'volume_per_trade': aggressive_volume,
            'num_trades': 1,
            'estimated_impact_bps': aggressive_impact['estimated_price_impact_bps'],
            'execution_time': 'immediate',
            'market_impact': aggressive_impact['market_impact_cost'],
            'recommended': aggressive_impact['estimated_price_impact_bps'] <= max_impact
        })
        
        # 2. Conservative execution (split across time)
        num_trades = min(10, max(2, int(total_volume / (current_depth * 0.02))))
        conservative_volume = total_volume / num_trades
        conservative_impact = self.forecast_depth_impact(conservative_volume, data)
        
        strategies.append({
            'name': 'conservative',
            'description': f'Volume ni {num_trades} qismga bo\'lib bajarish',
            'volume_per_trade': conservative_volume,
            'num_trades': num_trades,
            'estimated_impact_bps': conservative_impact['estimated_price_impact_bps'],
            'execution_time': 'extended',
            'market_impact': conservative_impact['market_impact_cost'] * num_trades,
            'recommended': conservative_impact['estimated_price_impact_bps'] <= max_impact
        })
        
        # 3. Dynamic execution (based on market conditions)
        dynamic_trades = []
        remaining_volume = total_volume
        
        while remaining_volume > 0:
            current_conditions = df.iloc[-1]
            
            # Calculate optimal trade size based on current conditions
            optimal_size = min(
                remaining_volume,
                current_depth * 0.01  # Never more than 1% of depth
            )
            
            if optimal_size < remaining_volume * 0.1:  # If too small, take larger chunk
                optimal_size = min(remaining_volume, current_depth * 0.02)
            
            impact = self.forecast_depth_impact(optimal_size, data)
            
            dynamic_trades.append({
                'volume': optimal_size,
                'estimated_impact_bps': impact['estimated_price_impact_bps'],
                'market_conditions': {
                    'depth': current_conditions['total_depth'],
                    'spread': current_conditions['spread_bps'],
                    'imbalance': current_conditions['order_book_imbalance']
                }
            })
            
            remaining_volume -= optimal_size
        
        total_dynamic_impact = sum([trade['estimated_impact_bps'] for trade in dynamic_trades])
        
        strategies.append({
            'name': 'dynamic',
            'description': 'Market shartlariga qarab dinamik execution',
            'volume_per_trade': 'variable',
            'num_trades': len(dynamic_trades),
            'estimated_impact_bps': total_dynamic_impact / len(dynamic_trades) if dynamic_trades else 0,
            'execution_time': 'adaptive',
            'market_impact': sum([self.forecast_depth_impact(trade['volume'], data)['market_impact_cost'] for trade in dynamic_trades]),
            'trade_breakdown': dynamic_trades,
            'recommended': total_dynamic_impact / len(dynamic_trades) <= max_impact if dynamic_trades else False
        })
        
        # Select best strategy
        recommended_strategies = [s for s in strategies if s['recommended']]
        best_strategy = None
        
        if recommended_strategies:
            # Choose strategy with lowest market impact
            best_strategy = min(recommended_strategies, key=lambda x: x['market_impact'])
        else:
            # Choose least bad option
            best_strategy = min(strategies, key=lambda x: x['estimated_impact_bps'])
        
        return {
            'total_volume': total_volume,
            'max_allowed_impact_bps': max_impact,
            'current_market_depth': current_depth,
            'strategies': strategies,
            'recommended_strategy': best_strategy['name'],
            'best_strategy_details': best_strategy,
            'implementation_recommendations': self._get_implementation_recommendations(best_strategy, data)
        }
    
    def _get_implementation_recommendations(self, strategy: Dict, data: pd.DataFrame) -> List[str]:
        """Implementation uchun tavsiyalar"""
        recommendations = []
        
        if strategy['name'] == 'aggressive':
            recommendations.extend([
                "Yuqori likvidlik davrida bajarish (European/US overlap)",
                "Market order ishlatish",
                "Havola olish vaqti minimal"
            ])
        
        elif strategy['name'] == 'conservative':
            recommendations.extend([
                "Trade larni vaqt bo'yicha taqsimlash",
                "Limit order ishlatish",
                "Volume surilishini kuzatish"
            ])
        
        elif strategy['name'] == 'dynamic':
            recommendations.extend([
                "Real-time market shartlarni kuzatish",
                "Flexibel volume adjustment",
                "Automated execution logic"
            ])
        
        # General recommendations based on current market
        if 'spread_bps' in data.columns and data['spread_bps'].iloc[-1] > 2.0:
            recommendations.append("Keng spread: Ehtiyotkor execution")
        
        if 'order_book_imbalance' in data.columns:
            imbalance = data['order_book_imbalance'].iloc[-1]
            if abs(imbalance) > 0.3:
                recommendations.append("Order book imbalance: Trade direction ga e'tibor")
        
        return recommendations