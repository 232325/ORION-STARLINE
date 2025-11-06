"""
Liquidity Analyzer

Bu modul market likvidligini comprehensive tahlil qilish uchun
asosiy interfeys vazifasini bajaradi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class LiquidityMetrics:
    """Liquidity metrics data class"""
    bid_ask_spread: float
    market_depth: float
    order_book_imbalance: float
    volume_profile: Dict[str, float]
    liquidity_cost: float
    timestamp: datetime


class LiquidityAnalyzer:
    """
    Asosiy Liquidity Analyzer class
    
    Bu class market likvidligini tahlil qilish uchun barcha asosiy
    metodlarni ta'minlaydi va turli liquidity metrics hisoblaydi.
    """
    
    def __init__(self, lookback_window: int = 100):
        """
        Initialize analyzer
        
        Args:
            lookback_window: Historical data window size
        """
        self.lookback_window = lookback_window
        self.cache = {}
        
    def analyze_market_liquidity(self, market_data: pd.DataFrame,
                               order_book_data: pd.DataFrame) -> Dict[str, any]:
        """
        Comprehensive market liquidity analysis
        
        Args:
            market_data: Historical market data
            order_book_data: Order book snapshots
            
        Returns:
            Comprehensive liquidity analysis results
        """
        results = {}
        
        # Basic metrics
        results['timestamp'] = datetime.now()
        
        # Bid-ask spread analysis
        if 'bid' in order_book_data.columns and 'ask' in order_book_data.columns:
            bid_ask_data = order_book_data[['bid', 'ask', 'volume']].copy()
            spread_results = self._analyze_bid_ask_spread(bid_ask_data)
            results['bid_ask_spread'] = spread_results
        else:
            results['bid_ask_spread'] = {'error': 'Missing bid/ask data'}
            
        # Market depth analysis
        if 'bids' in order_book_data.columns and 'asks' in order_book_data.columns:
            depth_results = self._analyze_market_depth(order_book_data)
            results['market_depth'] = depth_results
        else:
            results['market_depth'] = {'error': 'Missing depth data'}
            
        # Order book dynamics
        if len(order_book_data) > 1:
            dynamics_results = self._analyze_order_book_dynamics(order_book_data)
            results['order_book_dynamics'] = dynamics_results
        else:
            results['order_book_dynamics'] = {'error': 'Insufficient data'}
            
        # Volume profile analysis
        if 'volume' in market_data.columns:
            volume_results = self._analyze_volume_profile(market_data)
            results['volume_profile'] = volume_results
        else:
            results['volume_profile'] = {'error': 'Missing volume data'}
            
        # Overall liquidity score
        results['liquidity_score'] = self._calculate_liquidity_score(results)
        
        return results
        
    def _analyze_bid_ask_spread(self, bid_ask_data: pd.DataFrame) -> Dict[str, float]:
        """Bid-ask spread analysis"""
        spread = bid_ask_data['ask'] - bid_ask_data['bid']
        mid_price = (bid_ask_data['ask'] + bid_ask_data['bid']) / 2
        
        return {
            'mean_spread': spread.mean(),
            'median_spread': spread.median(),
            'spread_volatility': spread.std(),
            'relative_spread': (spread / mid_price).mean(),
            'spread_percentile_25': spread.quantile(0.25),
            'spread_percentile_75': spread.quantile(0.75)
        }
        
    def _analyze_market_depth(self, order_book_data: pd.DataFrame) -> Dict[str, float]:
        """Market depth analysis"""
        # Assume order_book_data contains aggregated bid/ask sizes
        total_bid_size = 0
        total_ask_size = 0
        
        if 'bids' in order_book_data.columns and 'asks' in order_book_data.columns:
            for _, row in order_book_data.iterrows():
                bid_sizes = row.get('bids', [])
                ask_sizes = row.get('asks', [])
                
                if isinstance(bid_sizes, list):
                    total_bid_size += sum(bid_sizes) if len(bid_sizes) > 0 else 0
                if isinstance(ask_sizes, list):
                    total_ask_size += sum(ask_sizes) if len(ask_sizes) > 0 else 0
        
        # Calculate depth metrics
        total_depth = total_bid_size + total_ask_size
        imbalance = (total_bid_size - total_ask_size) / (total_depth + 1e-6)
        
        return {
            'total_bid_depth': total_bid_size,
            'total_ask_depth': total_ask_size,
            'total_depth': total_depth,
            'depth_imbalance': imbalance,
            'bid_depth_ratio': total_bid_size / (total_depth + 1e-6),
            'ask_depth_ratio': total_ask_size / (total_depth + 1e-6)
        }
        
    def _analyze_order_book_dynamics(self, order_book_data: pd.DataFrame) -> Dict[str, float]:
        """Order book dynamics analysis"""
        if len(order_book_data) < 2:
            return {'error': 'Insufficient data for dynamics analysis'}
            
        # Calculate changes in order book
        dynamics = {}
        
        # Spread dynamics
        if 'bid' in order_book_data.columns and 'ask' in order_book_data.columns:
            spreads = order_book_data['ask'] - order_book_data['bid']
            dynamics['spread_volatility'] = spreads.pct_change().std()
            dynamics['spread_mean_reversion'] = spreads.diff().mean()
            
        # Volume dynamics  
        if 'volume' in order_book_data.columns:
            volume_changes = order_book_data['volume'].pct_change()
            dynamics['volume_volatility'] = volume_changes.std()
            dynamics['volume_trend'] = volume_changes.mean()
            
        return dynamics
        
    def _analyze_volume_profile(self, market_data: pd.DataFrame) -> Dict[str, float]:
        """Volume profile analysis"""
        if 'volume' not in market_data.columns:
            return {'error': 'No volume data available'}
            
        volumes = market_data['volume']
        
        return {
            'mean_volume': volumes.mean(),
            'median_volume': volumes.median(),
            'volume_volatility': volumes.std(),
            'volume_percentile_25': volumes.quantile(0.25),
            'volume_percentile_75': volumes.quantile(0.75),
            'volume_skewness': volumes.skew(),
            'volume_kurtosis': volumes.kurtosis()
        }
        
    def _calculate_liquidity_score(self, results: Dict[str, any]) -> float:
        """Overall liquidity score calculation (0-100)"""
        score = 50.0  # Base score
        
        # Spread impact (lower spread = higher score)
        if 'bid_ask_spread' in results and 'relative_spread' in results['bid_ask_spread']:
            rel_spread = results['bid_ask_spread']['relative_spread']
            spread_score = max(0, 30 - rel_spread * 1000)  # Scale factor
            score += spread_score
            
        # Depth impact
        if 'market_depth' in results and 'total_depth' in results['market_depth']:
            depth = results['market_depth']['total_depth']
            depth_score = min(20, depth / 10000)  # Scale factor
            score += depth_score
            
        return max(0, min(100, score))
        
    def calculate_liquidity_cost(self, trade_size: float, 
                               time_horizon: float = 1.0,
                               market_conditions: Dict[str, float] = None) -> Dict[str, float]:
        """
        Trading cost estimation based on liquidity
        
        Args:
            trade_size: Trade size
            time_horizon: Trading time horizon (hours)
            market_conditions: Current market conditions
            
        Returns:
            Liquidity cost breakdown
        """
        if market_conditions is None:
            market_conditions = {
                'spread': 0.01,
                'depth': 100000,
                'volatility': 0.02
            }
            
        # Spread cost (constant)
        spread_cost = market_conditions['spread'] * trade_size
        
        # Impact cost (grows with trade size)
        depth = market_conditions['depth']
        impact_cost = (trade_size / depth) ** 1.5 * 0.001 * trade_size
        
        # Time-based cost (longer horizon = lower impact)
        time_cost = impact_cost * (1.0 / np.sqrt(time_horizon))
        
        # Volatility adjustment
        vol_adj = 1.0 + market_conditions.get('volatility', 0.02) * 10
        
        total_cost = (spread_cost + time_cost) * vol_adj
        
        return {
            'spread_cost': spread_cost,
            'impact_cost': impact_cost,
            'time_cost': time_cost,
            'volatility_adjustment': vol_adj - 1.0,
            'total_cost': total_cost,
            'cost_per_share': total_cost / trade_size if trade_size > 0 else 0,
            'cost_bps': (total_cost / trade_size) * 10000 if trade_size > 0 else 0
        }
        
    def monitor_liquidity_changes(self, order_book_history: pd.DataFrame,
                                monitoring_window: int = 10) -> Dict[str, any]:
        """
        Real-time liquidity change monitoring
        
        Args:
            order_book_history: Historical order book data
            monitoring_window: Window size for changes
            
        Returns:
            Liquidity change metrics
        """
        if len(order_book_history) < monitoring_window:
            return {'error': 'Insufficient data for monitoring'}
            
        recent_data = order_book_history.tail(monitoring_window)
        
        # Calculate changes
        changes = {}
        
        # Spread changes
        if 'bid' in recent_data.columns and 'ask' in recent_data.columns:
            recent_spreads = recent_data['ask'] - recent_data['bid']
            changes['spread_change'] = recent_spreads.diff().mean()
            changes['spread_trend'] = recent_spreads.pct_change().mean()
            
        # Volume changes
        if 'volume' in recent_data.columns:
            recent_volumes = recent_data['volume']
            changes['volume_change'] = recent_volumes.diff().mean()
            changes['volume_trend'] = recent_volumes.pct_change().mean()
            
        # Liquidity alerts
        alerts = self._generate_liquidity_alerts(changes)
        
        return {
            'changes': changes,
            'alerts': alerts,
            'monitoring_timestamp': datetime.now()
        }
        
    def _generate_liquidity_alerts(self, changes: Dict[str, float]) -> List[str]:
        """Generate liquidity alerts"""
        alerts = []
        
        # Spread widening alert
        if changes.get('spread_change', 0) > 0.001:
            alerts.append("BID-ASK_SPREAD_WIDENING")
            
        # Volume spike alert
        if changes.get('volume_change', 0) > 0.5:  # 50% volume increase
            alerts.append("VOLUME_SPIKE")
            
        # Liquidity deterioration
        if changes.get('spread_trend', 0) > 0.1:
            alerts.append("LIQUIDITY_DETERIORATION")
            
        return alerts
        
    def compare_liquidity_sessions(self, session1_data: pd.DataFrame,
                                 session2_data: pd.DataFrame) -> Dict[str, any]:
        """
        Two trading sessions ni liquidity bo'yicha taqqoslash
        
        Args:
            session1_data: Session 1 data
            session2_data: Session 2 data
            
        Returns:
            Liquidity comparison results
        """
        session1_analysis = self.analyze_market_liquidity(
            session1_data.get('market_data', pd.DataFrame()),
            session1_data.get('order_book', pd.DataFrame())
        )
        
        session2_analysis = self.analyze_market_liquidity(
            session2_data.get('market_data', pd.DataFrame()),
            session2_data.get('order_book', pd.DataFrame())
        )
        
        comparison = {
            'session1_analysis': session1_analysis,
            'session2_analysis': session2_analysis,
            'differences': {}
        }
        
        # Compare key metrics
        metrics_to_compare = [
            'liquidity_score',
            'bid_ask_spread',
            'market_depth'
        ]
        
        for metric in metrics_to_compare:
            if metric in session1_analysis and metric in session2_analysis:
                if isinstance(session1_analysis[metric], dict):
                    # Deep comparison for dict metrics
                    comparison['differences'][metric] = {}
                    for submetric in session1_analysis[metric]:
                        if submetric in session2_analysis[metric]:
                            val1 = session1_analysis[metric][submetric]
                            val2 = session2_analysis[metric][submetric]
                            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                                comparison['differences'][metric][submetric] = val2 - val1
                else:
                    # Simple comparison for scalar metrics
                    comparison['differences'][metric] = (
                        session2_analysis[metric] - session1_analysis[metric]
                    )
                    
        return comparison
        
    def generate_liquidity_report(self, analysis_results: Dict[str, any]) -> str:
        """
        Liquidity analysis results dan comprehensive report yaratish
        
        Args:
            analysis_results: Liquidity analysis results
            
        Returns:
            Formatted liquidity report
        """
        report = []
        report.append("=== LIQUIDITY ANALYSIS REPORT ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall score
        if 'liquidity_score' in analysis_results:
            score = analysis_results['liquidity_score']
            report.append(f"Overall Liquidity Score: {score:.2f}/100")
            report.append("")
            
        # Bid-ask spread
        if 'bid_ask_spread' in analysis_results:
            spread_data = analysis_results['bid_ask_spread']
            report.append("BID-ASK SPREAD ANALYSIS:")
            report.append(f"  Mean Spread: {spread_data.get('mean_spread', 0):.4f}")
            report.append(f"  Median Spread: {spread_data.get('median_spread', 0):.4f}")
            report.append(f"  Relative Spread: {spread_data.get('relative_spread', 0):.4f}")
            report.append("")
            
        # Market depth
        if 'market_depth' in analysis_results:
            depth_data = analysis_results['market_depth']
            report.append("MARKET DEPTH ANALYSIS:")
            report.append(f"  Total Depth: {depth_data.get('total_depth', 0):.0f}")
            report.append(f"  Bid Depth: {depth_data.get('total_bid_depth', 0):.0f}")
            report.append(f"  Ask Depth: {depth_data.get('total_ask_depth', 0):.0f}")
            report.append(f"  Depth Imbalance: {depth_data.get('depth_imbalance', 0):.4f}")
            report.append("")
            
        # Volume profile
        if 'volume_profile' in analysis_results:
            vol_data = analysis_results['volume_profile']
            report.append("VOLUME PROFILE:")
            report.append(f"  Mean Volume: {vol_data.get('mean_volume', 0):.0f}")
            report.append(f"  Volume Volatility: {vol_data.get('volume_volatility', 0):.0f}")
            report.append("")
            
        # Alerts
        if 'order_book_dynamics' in analysis_results and 'alerts' in analysis_results.get('order_book_dynamics', {}):
            alerts = analysis_results['order_book_dynamics']['alerts']
            if alerts:
                report.append("LIQUIDITY ALERTS:")
                for alert in alerts:
                    report.append(f"  - {alert}")
                    
        return "\n".join(report)
        
    def get_liquidity_statistics(self) -> Dict[str, float]:
        """
        Analyzer statistics
        
        Returns:
            Analyzer statistics
        """
        return {
            'lookback_window': self.lookback_window,
            'cache_size': len(self.cache),
            'analysis_count': len(self.cache)
        }