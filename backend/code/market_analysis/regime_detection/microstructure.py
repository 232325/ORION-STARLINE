"""
Market Microstructure Module
===========================

Market microstructure changes.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


class MicrostructureAnalyzer:
    """Microstructure tahlil moduli"""
    
    def __init__(self):
        self.liquidity_thresholds = {
            'bid_ask_spread': 0.001,  # 0.1% as hold threshold
            'order_imbalance': 0.3,   # 30% imbalance threshold
            'depth_ratio': 0.5        # Minimum bid/ask depth ratio
        }
    
    def analyze_microstructure_changes(self, data, order_book_data=None):
        """Microstructure o'zgarish tahlil"""
        if 'close' not in data.columns and len(data.columns) == 4:
            data.columns = ['open', 'high', 'low', 'close']
        
        # Price impact analysis
        returns = data['close'].pct_change().dropna()
        volume = data['volume'] if 'volume' in data.columns else pd.Series(1, index=data.index)
        
        # Price impact coefficient
        price_impact = self._calculate_price_impact(returns, volume)
        
        # Volatility clustering
        volatility_clusters = self._detect_volatility_clusters(returns)
        
        # Order flow analysis
        if order_book_data is not None:
            order_flow_metrics = self._analyze_order_flow(order_book_data)
        else:
            order_flow_metrics = {'status': 'no_order_book_data'}
        
        return {
            'price_impact_coefficient': price_impact,
            'volatility_clusters': volatility_clusters,
            'order_flow_metrics': order_flow_metrics,
            'microstructure_regime': self._classify_microstructure_regime(price_impact, volatility_clusters),
            'market_efficiency_score': self._calculate_efficiency_score(returns)
        }
    
    def detect_liquidity_shocks(self, order_book_data):
        """Liquidity shock aniqlash"""
        if not order_book_data:
            return {'shock_detected': False, 'reason': 'no_data'}
        
        current_spread = order_book_data.get('spread', 0)
        average_spread = order_book_data.get('avg_spread', 0)
        
        # Spread-based shock detection
        spread_shock = current_spread > average_spread * 2 if average_spread > 0 else False
        
        # Depth-based shock detection
        current_bid_depth = order_book_data.get('bid_depth', 0)
        current_ask_depth = order_book_data.get('ask_depth', 0)
        avg_depth = (current_bid_depth + current_ask_depth) / 2
        
        depth_shock = current_bid_depth < avg_depth * 0.3 or current_ask_depth < avg_depth * 0.3
        
        shock_detected = spread_shock or depth_shock
        
        return {
            'shock_detected': shock_detected,
            'spread_shock': spread_shock,
            'depth_shock': depth_shock,
            'shock_severity': 'high' if shock_detected else 'normal',
            'recovery_time_estimate': '30-60 min' if shock_detected else 'N/A'
        }
    
    def calculate_microstructure_metrics(self, data, tick_size=0.0001):
        """Microstructure metrikalarni hisoblash"""
        if 'close' not in data.columns and len(data.columns) == 4:
            data.columns = ['open', 'high', 'low', 'close']
        
        # Quote-to-quote analysis
        price_changes = data['close'].diff().dropna()
        tick_volumes = data['volume'] if 'volume' in data.columns else pd.Series(1, index=data.index)
        
        # Effective spread estimation
        effective_spread = self._estimate_effective_spread(price_changes)
        
        # Price improvement
        price_improvement = self._calculate_price_improvement(data)
        
        # Market impact measure
        market_impact = self._calculate_market_impact(data)
        
        return {
            'effective_spread': effective_spread,
            'price_improvement': price_improvement,
            'market_impact': market_impact,
            'price_impact_ratio': market_impact / effective_spread if effective_spread > 0 else 0,
            'trade_frequency': len(price_changes[abs(price_changes) >= tick_size]) / len(price_changes)
        }
    
    def analyze_tick_data_patterns(self, tick_data):
        """Tick data namunalar tahlili"""
        # Tick-by-tick analysis
        if 'price' not in tick_data.columns:
            tick_data['price'] = tick_data.iloc[:, 0]  # Assuming first column is price
        
        price_directions = np.sign(tick_data['price'].diff())
        direction_persistence = self._calculate_persistence(price_directions)
        
        return {
            'direction_persistence': direction_persistence,
            'tick_frequency': len(tick_data) / (tick_data.index[-1] - tick_data.index[0]).total_seconds(),
            'price_change_distribution': {
                'up_moves': len(price_directions[price_directions > 0]),
                'down_moves': len(price_directions[price_directions < 0]),
                'no_change': len(price_directions[price_directions == 0])
            }
        }
    
    def _calculate_price_impact(self, returns, volume):
        """Price impact koeffitsientini hisoblash"""
        if len(returns) < 10 or len(volume) < 10:
            return 0
        
        # Simple regression: returns vs volume
        correlation = returns.rolling(window=20).corr(volume.rolling(window=20))
        return correlation.dropna().mean()
    
    def _detect_volatility_clusters(self, returns):
        """Volatility klasterlanishini aniqlash"""
        squared_returns = returns ** 2
        high_vol_threshold = squared_returns.quantile(0.8)
        
        clusters = []
        in_cluster = False
        cluster_start = None
        
        for i, ret_sq in enumerate(squared_returns):
            if ret_sq > high_vol_threshold and not in_cluster:
                cluster_start = i
                in_cluster = True
            elif ret_sq <= high_vol_threshold and in_cluster:
                clusters.append({
                    'start': cluster_start,
                    'end': i - 1,
                    'duration': i - cluster_start,
                    'avg_volatility': squared_returns[cluster_start:i].mean()
                })
                in_cluster = False
        
        return {
            'clusters': clusters,
            'total_clusters': len(clusters),
            'avg_cluster_duration': np.mean([c['duration'] for c in clusters]) if clusters else 0
        }
    
    def _analyze_order_flow(self, order_book_data):
        """Order flow tahlil"""
        bid_volume = order_book_data.get('bid_volume', 0)
        ask_volume = order_book_data.get('ask_volume', 0)
        total_volume = bid_volume + ask_volume
        
        if total_volume == 0:
            return {'imbalance': 0, 'imbalance_severity': 'unknown'}
        
        imbalance = (bid_volume - ask_volume) / total_volume
        severity = 'high' if abs(imbalance) > 0.5 else 'moderate' if abs(imbalance) > 0.3 else 'normal'
        
        return {
            'imbalance': imbalance,
            'imbalance_severity': severity,
            'bid_dominance': bid_volume > ask_volume,
            'total_market_depth': total_volume
        }
    
    def _classify_microstructure_regime(self, price_impact, volatility_clusters):
        """Microstructure rejimini tasniflash"""
        high_impact = abs(price_impact) > 0.1
        high_volatility = volatility_clusters['total_clusters'] > 5
        
        if high_impact and high_volatility:
            return 'stressed'
        elif high_impact or high_volatility:
            return 'transitional'
        else:
            return 'normal'
    
    def _calculate_efficiency_score(self, returns):
        """Market samaradorligi ballini hisoblash"""
        # Simple efficiency measure: mean reversion tendency
        if len(returns) < 20:
            return 0.5
        
        # First-order autocorrelation
        autocorr = returns.autocorr()
        
        # Convert to efficiency score (0-1, higher = more efficient)
        efficiency = 1 - abs(autocorr) if not np.isnan(autocorr) else 0.5
        
        return max(0, min(1, efficiency))
    
    def _estimate_effective_spread(self, price_changes):
        """Effective spread bahosini hisoblash"""
        abs_changes = abs(price_changes)
        # Estimate as 2x average absolute price change
        return 2 * abs_changes.mean()
    
    def _calculate_price_improvement(self, data):
        """Price improvement hisoblash"""
        if 'high' not in data.columns or 'low' not in data.columns:
            return 0
        
        # Average true range as proxy for price improvement
        high_low_spread = data['high'] - data['low']
        return high_low_spread.mean()
    
    def _calculate_market_impact(self, data):
        """Market impact hisoblash"""
        if 'volume' not in data.columns:
            return 0
        
        # Simple volume-weighted price change
        returns = data['close'].pct_change().dropna()
        volume = data['volume'].iloc[1:]  # Align with returns
        
        if len(returns) != len(volume):
            return 0
        
        weighted_impact = (abs(returns) * volume).sum() / volume.sum()
        return weighted_impact
    
    def _calculate_persistence(self, directions):
        """Persistence hisoblash"""
        if len(directions) < 2:
            return 0
        
        # Count consecutive same directions
        consecutive_changes = 0
        max_consecutive = 0
        current_direction = None
        
        for direction in directions:
            if direction != 0:  # Ignore zero changes
                if current_direction == direction:
                    consecutive_changes += 1
                else:
                    max_consecutive = max(max_consecutive, consecutive_changes)
                    consecutive_changes = 1
                    current_direction = direction
        
        max_consecutive = max(max_consecutive, consecutive_changes)
        return max_consecutive / len(directions[directions != 0]) if len(directions[directions != 0]) > 0 else 0