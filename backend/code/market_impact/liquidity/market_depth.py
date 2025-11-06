"""
Market Depth Analyzer

Bu modul market depth ni tahlil qilish uchun
specialized methods ta'minlaydi.

Market depth trading likvidligi va order book
dynamics ni tushunishda muhim rol o'ynaydi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from scipy import stats
from scipy.optimize import minimize_scalar


@dataclass
class DepthLevel:
    """Individual depth level"""
    price: float
    size: float
    side: str  # 'bid' or 'ask'


class MarketDepthAnalyzer:
    """
    Market Depth Analyzer
    
    Order book depth, liquidity profiling va market impact analysis
    """
    
    def __init__(self, min_size_threshold: float = 100.0):
        """
        Initialize analyzer
        
        Args:
            min_size_threshold: Minimum size to consider for depth analysis
        """
        self.min_size_threshold = min_size_threshold
        self.depth_history = []
        
    def analyze_current_depth(self, bid_levels: List[Tuple[float, float]],
                            ask_levels: List[Tuple[float, float]]) -> Dict[str, any]:
        """
        Current market depth analysis
        
        Args:
            bid_levels: List of (price, size) tuples for bids
            ask_levels: List of (price, size) tuples for asks
            
        Returns:
            Current depth analysis
        """
        # Filter levels by minimum size
        filtered_bids = [(p, s) for p, s in bid_levels if s >= self.min_size_threshold]
        filtered_asks = [(p, s) for p, s in ask_levels if s >= self.min_size_threshold]
        
        if not filtered_bids or not filtered_asks:
            return {'error': 'Insufficient depth data'}
            
        # Basic calculations
        best_bid = max(filtered_bids, key=lambda x: x[0])[0]
        best_ask = min(filtered_asks, key=lambda x: x[0])[0]
        
        total_bid_size = sum(size for _, size in filtered_bids)
        total_ask_size = sum(size for _, size in filtered_asks)
        total_depth = total_bid_size + total_ask_size
        
        # Calculate depth statistics
        bid_depth_stats = self._calculate_level_statistics(filtered_bids)
        ask_depth_stats = self._calculate_level_statistics(filtered_asks)
        
        # Market imbalance
        imbalance = (total_bid_size - total_ask_size) / (total_depth + 1e-6)
        
        # Price levels analysis
        bid_price_levels = [price for price, _ in filtered_bids]
        ask_price_levels = [price for price, _ in filtered_asks]
        
        price_spread = best_ask - best_bid
        
        return {
            'timestamp': datetime.now(),
            'best_bid': best_bid,
            'best_ask': best_ask,
            'spread': price_spread,
            'mid_price': (best_bid + best_ask) / 2,
            'total_bid_size': total_bid_size,
            'total_ask_size': total_ask_size,
            'total_depth': total_depth,
            'depth_imbalance': imbalance,
            'bid_levels_count': len(filtered_bids),
            'ask_levels_count': len(filtered_asks),
            'bid_depth_stats': bid_depth_stats,
            'ask_depth_stats': ask_depth_stats,
            'price_levels': {
                'bid_levels': bid_price_levels,
                'ask_levels': ask_price_levels
            },
            'liquidity_quality': self._calculate_liquidity_quality(filtered_bids, filtered_asks)
        }
        
    def _calculate_level_statistics(self, levels: List[Tuple[float, float]]) -> Dict[str, float]:
        """Calculate statistics for depth levels"""
        if not levels:
            return {}
            
        prices = [price for price, _ in levels]
        sizes = [size for _, size in levels]
        
        return {
            'mean_price': np.mean(prices),
            'median_price': np.median(prices),
            'std_price': np.std(prices),
            'min_price': np.min(prices),
            'max_price': np.max(prices),
            'mean_size': np.mean(sizes),
            'median_size': np.median(sizes),
            'std_size': np.std(sizes),
            'total_size': np.sum(sizes),
            'price_range': np.max(prices) - np.min(prices),
            'size_distribution_skew': stats.skew(sizes) if len(sizes) > 2 else 0
        }
        
    def _calculate_liquidity_quality(self, bid_levels: List[Tuple[float, float]],
                                   ask_levels: List[Tuple[float, float]]) -> float:
        """Calculate liquidity quality score (0-1)"""
        if not bid_levels or not ask_levels:
            return 0.0
            
        # Spread component (wider spread = lower quality)
        spread = min(ask_levels, key=lambda x: x[0])[0] - max(bid_levels, key=lambda x: x[0])[0]
        spread_score = max(0, 1 - spread / 0.1)  # Normalize by 10-cent spread
        
        # Depth uniformity component
        bid_sizes = [size for _, size in bid_levels]
        ask_sizes = [size for _, size in ask_levels]
        
        bid_uniformity = 1 - (np.std(bid_sizes) / (np.mean(bid_sizes) + 1e-6))
        ask_uniformity = 1 - (np.std(ask_sizes) / (np.mean(ask_sizes) + 1e-6))
        uniformity_score = (bid_uniformity + ask_uniformity) / 2
        
        # Level distribution component
        level_score = min(1, (len(bid_levels) + len(ask_levels)) / 20)  # Normalize by 20 levels
        
        # Combined quality score
        quality_score = (spread_score * 0.4 + uniformity_score * 0.3 + level_score * 0.3)
        
        return max(0, min(1, quality_score))
        
    def calculate_market_impact_curve(self, trade_sizes: List[float],
                                    bid_levels: List[Tuple[float, float]],
                                    ask_levels: List[Tuple[float, float]],
                                    side: str = 'buy') -> Dict[str, np.ndarray]:
        """
        Market impact curve hisoblash
        
        Args:
            trade_sizes: Trade sizes to analyze
            bid_levels: Current bid levels
            ask_levels: Current ask levels  
            side: 'buy' or 'sell'
            
        Returns:
            Impact curve data
        """
        # Sort levels
        if side.lower() == 'buy':
            # Buying consumes ask levels
            sorted_levels = sorted(ask_levels, key=lambda x: x[0])  # Lowest ask first
            reference_price = max(bid_levels, key=lambda x: x[0])[0] if bid_levels else 100.0
        else:
            # Selling consumes bid levels  
            sorted_levels = sorted(bid_levels, key=lambda x: x[0], reverse=True)  # Highest bid first
            reference_price = min(ask_levels, key=lambda x: x[0])[0] if ask_levels else 100.0
            
        # Calculate impact for each trade size
        impacts = []
        vwap_prices = []
        completion_sizes = []
        
        for size in trade_sizes:
            remaining_size = size
            total_cost = 0.0
            total_size_filled = 0.0
            
            # Consume levels
            for price, level_size in sorted_levels:
                if remaining_size <= 0:
                    break
                    
                fill_size = min(remaining_size, level_size)
                total_cost += fill_size * price
                total_size_filled += fill_size
                remaining_size -= fill_size
                
            # Calculate metrics
            if total_size_filled > 0:
                vwap = total_cost / total_size_filled
                impact = vwap - reference_price
                
                # Add slippage estimate for partial fills
                if remaining_size > 0:
                    if side.lower() == 'buy':
                        # Assume worst price for remaining
                        impact += remaining_size * 0.001  # 10bp penalty
                    else:
                        impact -= remaining_size * 0.001
                        
                impacts.append(impact)
                vwap_prices.append(vwap)
                completion_sizes.append(size - remaining_size)
            else:
                impacts.append(0.0)
                vwap_prices.append(reference_price)
                completion_sizes.append(0.0)
                
        return {
            'trade_sizes': np.array(trade_sizes),
            'impacts': np.array(impacts),
            'vwap_prices': np.array(vwap_prices),
            'completion_sizes': np.array(completion_sizes),
            'completion_rates': np.array(completion_sizes) / np.array(trade_sizes)
        }
        
    def analyze_depth_resilience(self, bid_levels: List[Tuple[float, float]],
                               ask_levels: List[Tuple[float, float]],
                               shock_sizes: List[float]) -> Dict[str, any]:
        """
        Order book resilience analysis
        
        Args:
            bid_levels: Bid levels
            ask_levels: Ask levels
            shock_sizes: Sizes of potential shocks to test
            
        Returns:
            Resilience analysis
        """
        resilience_results = {}
        
        # Calculate for both sides
        for side in ['buy', 'sell']:
            if side.lower() == 'buy':
                levels_to_analyze = ask_levels
                reference_price = max(bid_levels, key=lambda x: x[0])[0] if bid_levels else 100.0
            else:
                levels_to_analyze = bid_levels
                reference_price = min(ask_levels, key=lambda x: x[0])[0] if ask_levels else 100.0
                
            if not levels_to_analyze:
                continue
                
            # Calculate resilience metrics
            total_available = sum(size for _, size in levels_to_analyze)
            
            price_impact_50 = self._calculate_shock_impact(levels_to_analyze, total_available * 0.5, side)
            price_impact_90 = self._calculate_shock_impact(levels_to_analyze, total_available * 0.9, side)
            
            # Price levels consumed
            levels_consumed_50 = self._count_levels_consumed(levels_to_analyze, total_available * 0.5, side)
            levels_consumed_90 = self._count_levels_consumed(levels_to_analyze, total_available * 0.9, side)
            
            resilience_results[side] = {
                'total_available': total_available,
                'impact_50pct': price_impact_50,
                'impact_90pct': price_impact_90,
                'levels_consumed_50pct': levels_consumed_50,
                'levels_consumed_90pct': levels_consumed_90,
                'resilience_score': 1.0 - (price_impact_90 / (reference_price + 1e-6))
            }
            
        return resilience_results
        
    def _calculate_shock_impact(self, levels: List[Tuple[float, float]], 
                              shock_size: float, side: str) -> float:
        """Calculate price impact for a given shock size"""
        if not levels:
            return 0.0
            
        remaining_size = shock_size
        total_cost = 0.0
        total_filled = 0.0
        
        # Sort levels appropriately
        if side.lower() == 'buy':
            sorted_levels = sorted(levels, key=lambda x: x[0])  # Lowest ask first
        else:
            sorted_levels = sorted(levels, key=lambda x: x[0], reverse=True)  # Highest bid first
            
        for price, level_size in sorted_levels:
            if remaining_size <= 0:
                break
                
            fill_size = min(remaining_size, level_size)
            total_cost += fill_size * price
            total_filled += fill_size
            remaining_size -= fill_size
            
        if total_filled > 0:
            return total_cost / total_filled
        else:
            return 0.0
            
    def _count_levels_consumed(self, levels: List[Tuple[float, float]],
                             shock_size: float, side: str) -> int:
        """Count how many levels are consumed by shock"""
        if not levels:
            return 0
            
        remaining_size = shock_size
        levels_consumed = 0
        
        # Sort levels appropriately
        if side.lower() == 'buy':
            sorted_levels = sorted(levels, key=lambda x: x[0])
        else:
            sorted_levels = sorted(levels, key=lambda x: x[0], reverse=True)
            
        for price, level_size in sorted_levels:
            if remaining_size <= 0:
                break
                
            fill_size = min(remaining_size, level_size)
            remaining_size -= fill_size
            
            if fill_size > 0:
                levels_consumed += 1
                
        return levels_consumed
        
    def analyze_depth_evolution(self, depth_history: List[Dict[str, any]],
                              time_window: int = 50) -> Dict[str, any]:
        """
        Evolution of market depth over time
        
        Args:
            depth_history: Historical depth snapshots
            time_window: Time window for analysis
            
        Returns:
            Evolution analysis
        """
        if len(depth_history) < 2:
            return {'error': 'Insufficient data for evolution analysis'}
            
        # Take recent window
        recent_history = depth_history[-time_window:] if len(depth_history) > time_window else depth_history
        
        # Extract time series
        timestamps = [snapshot['timestamp'] for snapshot in recent_history]
        total_depths = [snapshot['total_depth'] for snapshot in recent_history]
        bid_sizes = [snapshot['total_bid_size'] for snapshot in recent_history]
        ask_sizes = [snapshot['total_ask_size'] for snapshot in recent_history]
        imbalances = [snapshot['depth_imbalance'] for snapshot in recent_history]
        
        # Trend analysis
        depth_trend = stats.linregress(range(len(total_depths)), total_depths)
        imbalance_trend = stats.linregress(range(len(imbalances)), imbalances)
        
        # Volatility analysis
        depth_volatility = np.std(total_depths)
        imbalance_volatility = np.std(imbalances)
        
        # Regime detection
        depth_mean = np.mean(total_depths)
        depth_std = np.std(total_depths)
        
        high_depth_periods = total_depths > (depth_mean + depth_std)
        low_depth_periods = total_depths < (depth_mean - depth_std)
        
        return {
            'time_window': len(recent_history),
            'depth_trend': {
                'slope': depth_trend.slope,
                'r_squared': depth_trend.rvalue ** 2,
                'is_trending': abs(depth_trend.slope) > depth_trend.stderr * 2
            },
            'imbalance_trend': {
                'slope': imbalance_trend.slope,
                'r_squared': imbalance_trend.rvalue ** 2,
                'is_trending': abs(imbalance_trend.slope) > imbalance_trend.stderr * 2
            },
            'volatility': {
                'depth_volatility': depth_volatility,
                'imbalance_volatility': imbalance_volatility,
                'depth_cv': depth_volatility / (depth_mean + 1e-6)
            },
            'regimes': {
                'high_depth_periods': {
                    'count': sum(high_depth_periods),
                    'percentage': sum(high_depth_periods) / len(high_depth_periods) * 100
                },
                'low_depth_periods': {
                    'count': sum(low_depth_periods),
                    'percentage': sum(low_depth_periods) / len(low_depth_periods) * 100
                },
                'normal_depth_periods': {
                    'count': len(total_depths) - sum(high_depth_periods) - sum(low_depth_periods),
                    'percentage': (len(total_depths) - sum(high_depth_periods) - sum(low_depth_periods)) / len(total_depths) * 100
                }
            },
            'stability_metrics': {
                'depth_stability': 1.0 / (1.0 + depth_volatility / (depth_mean + 1e-6)),
                'imbalance_stability': 1.0 - abs(np.mean(imbalances)),
                'overall_stability': min(1.0, (depth_volatility / (depth_mean + 1e-6)) * 0.5 + abs(np.mean(imbalances)) * 0.5)
            }
        }
        
    def calculate_optimal_order_sizing(self, target_impact: float,
                                     bid_levels: List[Tuple[float, float]],
                                     ask_levels: List[Tuple[float, float]],
                                     side: str = 'buy') -> Dict[str, float]:
        """
        Optimal order size hisoblash
        
        Args:
            target_impact: Target price impact
            bid_levels: Current bid levels
            ask_levels: Current ask levels
            side: 'buy' or 'sell'
            
        Returns:
            Optimal sizing results
        """
        # Test different sizes to find optimal
        max_size = min(10000, sum(size for _, size in (bid_levels + ask_levels)))
        test_sizes = np.linspace(100, max_size, 100)
        
        # Get impact curve
        impact_curve = self.calculate_market_impact_curve(test_sizes, bid_levels, ask_levels, side)
        
        # Find size that achieves target impact
        impacts = impact_curve['impacts']
        target_sign = 1 if side.lower() == 'buy' else -1
        adjusted_impacts = impacts * target_sign
        
        # Find closest match
        closest_idx = np.argmin(np.abs(adjusted_impacts - target_impact))
        optimal_size = test_sizes[closest_idx]
        achieved_impact = adjusted_impacts[closest_idx]
        
        # Alternative: optimize for cost-effectiveness
        cost_per_size = np.abs(adjusted_impacts) / test_sizes
        optimal_idx = np.argmin(cost_per_size)
        efficient_size = test_sizes[optimal_idx]
        
        return {
            'target_impact': target_impact,
            'optimal_size_for_target': optimal_size,
            'achieved_impact': achieved_impact,
            'impact_error': abs(achieved_impact - target_impact),
            'efficient_size': efficient_size,
            'efficient_size_impact': adjusted_impacts[optimal_idx],
            'efficiency_ratio': cost_per_size[optimal_idx],
            'recommendation': {
                'size': optimal_size,
                'justification': f'Achieves {achieved_impact:.4f} impact vs target {target_impact:.4f}'
            }
        }
        
    def generate_depth_report(self, depth_analysis: Dict[str, any]) -> str:
        """
        Generate market depth analysis report
        
        Args:
            depth_analysis: Depth analysis results
            
        Returns:
            Formatted report
        """
        report = []
        report.append("=== MARKET DEPTH ANALYSIS REPORT ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Current snapshot
        if 'best_bid' in depth_analysis:
            report.append("CURRENT DEPTH SNAPSHOT:")
            report.append(f"  Best Bid: {depth_analysis['best_bid']:.4f}")
            report.append(f"  Best Ask: {depth_analysis['best_ask']:.4f}")
            report.append(f"  Spread: {depth_analysis['spread']:.4f}")
            report.append(f"  Mid Price: {depth_analysis['mid_price']:.4f}")
            report.append(f"  Total Bid Size: {depth_analysis['total_bid_size']:,.0f}")
            report.append(f"  Total Ask Size: {depth_analysis['total_ask_size']:,.0f}")
            report.append(f"  Total Depth: {depth_analysis['total_depth']:,.0f}")
            report.append(f"  Depth Imbalance: {depth_analysis['depth_imbalance']:.4f}")
            report.append("")
            
        # Quality metrics
        if 'liquidity_quality' in depth_analysis:
            quality = depth_analysis['liquidity_quality']
            report.append("LIQUIDITY QUALITY:")
            report.append(f"  Quality Score: {quality:.3f} / 1.0")
            quality_rating = "Excellent" if quality > 0.8 else "Good" if quality > 0.6 else "Fair" if quality > 0.4 else "Poor"
            report.append(f"  Rating: {quality_rating}")
            report.append("")
            
        # Level statistics
        if 'bid_depth_stats' in depth_analysis:
            bid_stats = depth_analysis['bid_depth_stats']
            ask_stats = depth_analysis['ask_depth_stats']
            report.append("DEPTH LEVEL STATISTICS:")
            report.append("  BID SIDE:")
            report.append(f"    Levels: {depth_analysis['bid_levels_count']}")
            report.append(f"    Mean Size: {bid_stats.get('mean_size', 0):,.0f}")
            report.append(f"    Total Size: {bid_stats.get('total_size', 0):,.0f}")
            report.append("  ASK SIDE:")
            report.append(f"    Levels: {depth_analysis['ask_levels_count']}")
            report.append(f"    Mean Size: {ask_stats.get('mean_size', 0):,.0f}")
            report.append(f"    Total Size: {ask_stats.get('total_size', 0):,.0f}")
            report.append("")
            
        return "\n".join(report)
        
    def get_analyzer_statistics(self) -> Dict[str, any]:
        """
        Analyzer statistics
        
        Returns:
            Analyzer statistics
        """
        return {
            'min_size_threshold': self.min_size_threshold,
            'depth_history_size': len(self.depth_history),
            'last_analysis': datetime.now().isoformat()
        }