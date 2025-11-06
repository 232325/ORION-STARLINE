"""
Liquidity Analysis System

Bu modul comprehensive liquidity analysis ta'minlaydi
va barcha liquidity-related componentlarni birlashtiradi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import warnings

from ..liquidity import (
    LiquidityAnalyzer, BidAskSpreadAnalyzer,
    MarketDepthAnalyzer, OrderBookDynamics,
    LiquidityCostEstimator
)


@dataclass
class LiquidityReport:
    """Comprehensive liquidity report"""
    timestamp: datetime
    overall_liquidity_score: float
    bid_ask_spread: Dict[str, float]
    market_depth: Dict[str, float]
    order_book_metrics: Dict[str, float]
    liquidity_cost: Dict[str, float]
    alerts: List[str]
    recommendations: List[str]


@dataclass
class LiquidityMonitoring:
    """Real-time liquidity monitoring"""
    current_conditions: Dict[str, Any]
    changes_detected: List[str]
    alert_level: str  # 'low', 'medium', 'high'
    recommended_actions: List[str]


class LiquidityAnalysisSystem:
    """
    Comprehensive Liquidity Analysis System
    
    Barcha liquidity analysis komponentlarini birlashtirib
    unified monitoring va analysis ta'minlaydi.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize liquidity analysis system
        
        Args:
            config: System configuration
        """
        self.config = config or {}
        
        # Initialize component analyzers
        self.liquidity_analyzer = LiquidityAnalyzer(
            lookback_window=self.config.get('lookback_window', 100)
        )
        
        self.spread_analyzer = BidAskSpreadAnalyzer(
            data_window=self.config.get('spread_window', 1000)
        )
        
        self.depth_analyzer = MarketDepthAnalyzer(
            min_size_threshold=self.config.get('min_size_threshold', 100.0)
        )
        
        # Internal state
        self.monitoring_data = []
        self.alert_thresholds = self._initialize_alert_thresholds()
        self.liquidity_history = []
        
    def _initialize_alert_thresholds(self) -> Dict[str, float]:
        """Initialize alert thresholds"""
        return {
            'spread_widening': 0.001,  # 10 basis points
            'volume_spike': 2.0,       # 200% of average
            'depth_deterioration': 0.5, # 50% of normal depth
            'liquidity_score_low': 30.0, # Below 30% score
            'volatility_spike': 0.05   # 5% volatility
        }
        
    def analyze_liquidity_comprehensive(self, market_data: pd.DataFrame,
                                      order_book_data: pd.DataFrame) -> LiquidityReport:
        """
        Comprehensive liquidity analysis
        
        Args:
            market_data: Market price/volume data
            order_book_data: Order book level data
            
        Returns:
            Comprehensive liquidity report
        """
        # Basic liquidity analysis
        basic_analysis = self.liquidity_analyzer.analyze_market_liquidity(
            market_data, order_book_data)
            
        # Spread analysis
        spread_analysis = self._analyze_spread_detailed(order_book_data)
        
        # Depth analysis
        depth_analysis = self._analyze_depth_detailed(order_book_data)
        
        # Order book dynamics
        dynamics_analysis = self._analyze_order_book_dynamics(order_book_data)
        
        # Calculate overall liquidity score
        overall_score = self._calculate_overall_liquidity_score(
            basic_analysis, spread_analysis, depth_analysis)
            
        # Generate alerts
        alerts = self._generate_liquidity_alerts(
            basic_analysis, spread_analysis, depth_analysis)
            
        # Generate recommendations
        recommendations = self._generate_liquidity_recommendations(
            basic_analysis, spread_analysis, depth_analysis, alerts)
            
        # Estimate liquidity costs
        liquidity_costs = self._estimate_liquidity_costs(
            market_data, spread_analysis, depth_analysis)
            
        return LiquidityReport(
            timestamp=datetime.now(),
            overall_liquidity_score=overall_score,
            bid_ask_spread=spread_analysis,
            market_depth=depth_analysis,
            order_book_metrics=dynamics_analysis,
            liquidity_cost=liquidity_costs,
            alerts=alerts,
            recommendations=recommendations
        )
        
    def _analyze_spread_detailed(self, order_book_data: pd.DataFrame) -> Dict[str, float]:
        """Detailed spread analysis"""
        if len(order_book_data) == 0:
            return {}
            
        # Extract spread data
        spreads = []
        for _, row in order_book_data.iterrows():
            if 'bid' in row and 'ask' in row:
                spread = row['ask'] - row['bid']
                spreads.append(spread)
                
        if not spreads:
            return {}
            
        spreads = np.array(spreads)
        
        # Detailed statistics
        return {
            'mean_spread': np.mean(spreads),
            'median_spread': np.median(spreads),
            'spread_volatility': np.std(spreads),
            'spread_skewness': float(pd.Series(spreads).skew()),
            'spread_percentile_10': np.percentile(spreads, 10),
            'spread_percentile_90': np.percentile(spreads, 90),
            'spread_regime_changes': self._detect_spread_regime_changes(spreads)
        }
        
    def _analyze_depth_detailed(self, order_book_data: pd.DataFrame) -> Dict[str, float]:
        """Detailed depth analysis"""
        if len(order_book_data) == 0:
            return {}
            
        # Analyze each snapshot for depth
        total_depths = []
        bid_depths = []
        ask_depths = []
        
        for _, row in order_book_data.iterrows():
            # Parse bid/ask levels
            total_depth, b_depth, a_depth = self._parse_order_book_levels(row)
            total_depths.append(total_depth)
            bid_depths.append(b_depth)
            ask_depths.append(a_depth)
            
        if not total_depths:
            return {}
            
        return {
            'mean_total_depth': np.mean(total_depths),
            'depth_volatility': np.std(total_depths),
            'mean_bid_depth': np.mean(bid_depths),
            'mean_ask_depth': np.mean(ask_depths),
            'depth_imbalance_mean': np.mean(np.array(bid_depths) - np.array(ask_depths)),
            'depth_trend': self._calculate_depth_trend(total_depths),
            'liquidity_concentration': self._calculate_liquidity_concentration(order_book_data)
        }
        
    def _parse_order_book_levels(self, row: pd.Series) -> Tuple[float, float, float]:
        """Parse order book levels from row"""
        # This would parse the actual order book format
        # For now, return placeholder values
        bid_size = row.get('bid_size', 1000)
        ask_size = row.get('ask_size', 1000)
        return bid_size + ask_size, bid_size, ask_size
        
    def _calculate_overall_liquidity_score(self, basic_analysis: Dict,
                                         spread_analysis: Dict,
                                         depth_analysis: Dict) -> float:
        """Calculate overall liquidity score"""
        score = 50.0  # Base score
        
        # Spread component (30% weight)
        mean_spread = spread_analysis.get('mean_spread', 0.01)
        spread_score = max(0, 30 - mean_spread * 10000)  # Normalize to basis points
        score += spread_score * 0.3
        
        # Depth component (40% weight)
        mean_depth = depth_analysis.get('mean_total_depth', 100000)
        depth_score = min(20, mean_depth / 50000)  # Scale based on typical depth
        score += depth_score * 0.4
        
        # Volume component (20% weight)
        if 'liquidity_score' in basic_analysis:
            volume_score = basic_analysis['liquidity_score'] * 0.2
            score += volume_score * 0.2
            
        # Stability component (10% weight)
        spread_vol = spread_analysis.get('spread_volatility', 0)
        depth_vol = depth_analysis.get('depth_volatility', 0)
        stability_score = 10 * (1 - min(1, (spread_vol + depth_vol) / 0.1))
        score += stability_score * 0.1
        
        return max(0, min(100, score))
        
    def _detect_spread_regime_changes(self, spreads: np.ndarray) -> int:
        """Detect spread regime changes"""
        if len(spreads) < 20:
            return 0
            
        # Simple regime change detection
        mean_spread = np.mean(spreads)
        std_spread = np.std(spreads)
        
        threshold_changes = 0
        for i in range(1, len(spreads)):
            prev_deviation = abs(spreads[i-1] - mean_spread) / std_spread
            curr_deviation = abs(spreads[i] - mean_spread) / std_spread
            
            # Count significant regime changes
            if abs(prev_deviation - curr_deviation) > 1.0:
                threshold_changes += 1
                
        return threshold_changes
        
    def _calculate_depth_trend(self, depths: List[float]) -> float:
        """Calculate depth trend"""
        if len(depths) < 2:
            return 0.0
            
        x = np.arange(len(depths))
        slope = np.polyfit(x, depths, 1)[0]
        return slope
        
    def _calculate_liquidity_concentration(self, order_book_data: pd.DataFrame) -> float:
        """Calculate liquidity concentration"""
        if len(order_book_data) == 0:
            return 0.0
            
        # Calculate how concentrated liquidity is (lower = more concentrated)
        # This would analyze the distribution of sizes across price levels
        # Simplified version
        return 0.5  # Placeholder
        
    def _analyze_order_book_dynamics(self, order_book_data: pd.DataFrame) -> Dict[str, float]:
        """Analyze order book dynamics"""
        if len(order_book_data) < 2:
            return {}
            
        dynamics_metrics = {}
        
        # Price level dynamics
        if 'mid_price' in order_book_data.columns:
            price_changes = order_book_data['mid_price'].pct_change()
            dynamics_metrics['price_volatility'] = price_changes.std()
            dynamics_metrics['price_trend'] = price_changes.mean()
            
        # Volume dynamics
        if 'volume' in order_book_data.columns:
            volume_changes = order_book_data['volume'].pct_change()
            dynamics_metrics['volume_volatility'] = volume_changes.std()
            dynamics_metrics['volume_trend'] = volume_changes.mean()
            
        # Imbalance dynamics
        if 'bid_size' in order_book_data.columns and 'ask_size' in order_book_data.columns:
            imbalances = (order_book_data['bid_size'] - order_book_data['ask_size']) / (order_book_data['bid_size'] + order_book_data['ask_size'] + 1e-6)
            dynamics_metrics['imbalance_volatility'] = imbalances.std()
            dynamics_metrics['imbalance_mean'] = imbalances.mean()
            
        return dynamics_metrics
        
    def _generate_liquidity_alerts(self, basic_analysis: Dict,
                                 spread_analysis: Dict,
                                 depth_analysis: Dict) -> List[str]:
        """Generate liquidity alerts"""
        alerts = []
        
        # Spread alerts
        mean_spread = spread_analysis.get('mean_spread', 0)
        if mean_spread > self.alert_thresholds['spread_widening']:
            alerts.append(f"WIDENING_SPREAD: Mean spread {mean_spread:.4f} exceeds threshold")
            
        # Volume alerts
        if 'liquidity_score' in basic_analysis:
            score = basic_analysis['liquidity_score']
            if score < self.alert_thresholds['liquidity_score_low']:
                alerts.append(f"LOW_LIQUIDITY_SCORE: Score {score:.1f} below threshold")
                
        # Depth alerts
        mean_depth = depth_analysis.get('mean_total_depth', 0)
        if mean_depth < 50000:  # Arbitrary threshold
            alerts.append(f"LOW_MARKET_DEPTH: Mean depth {mean_depth:,.0f} below threshold")
            
        # Volatility alerts
        spread_vol = spread_analysis.get('spread_volatility', 0)
        if spread_vol > self.alert_thresholds['volatility_spike']:
            alerts.append(f"HIGH_SPREAD_VOLATILITY: Volatility {spread_vol:.4f} exceeds threshold")
            
        return alerts
        
    def _generate_liquidity_recommendations(self, basic_analysis: Dict,
                                          spread_analysis: Dict,
                                          depth_analysis: Dict,
                                          alerts: List[str]) -> List[str]:
        """Generate liquidity recommendations"""
        recommendations = []
        
        # Spread-based recommendations
        mean_spread = spread_analysis.get('mean_spread', 0)
        if mean_spread > 0.002:  # 20 basis points
            recommendations.append("Consider using limit orders instead of market orders")
            recommendations.append("Split large orders to reduce market impact")
            
        # Depth-based recommendations
        mean_depth = depth_analysis.get('mean_total_depth', 0)
        if mean_depth < 100000:
            recommendations.append("Market shows limited depth - use conservative position sizing")
            recommendations.append("Consider trading during higher volume periods")
            
        # Score-based recommendations
        if 'liquidity_score' in basic_analysis:
            score = basic_analysis['liquidity_score']
            if score < 50:
                recommendations.append("Overall liquidity conditions are poor - consider waiting")
                recommendations.append("Use iceberg orders to minimize market impact")
                
        # Alert-based recommendations
        for alert in alerts:
            if "WIDENING_SPREAD" in alert:
                recommendations.append("Spread widening detected - avoid aggressive trading")
            elif "LOW_MARKET_DEPTH" in alert:
                recommendations.append("Low depth indicates limited liquidity - trade conservatively")
                
        return list(set(recommendations))  # Remove duplicates
        
    def _estimate_liquidity_costs(self, market_data: pd.DataFrame,
                                spread_analysis: Dict,
                                depth_analysis: Dict) -> Dict[str, float]:
        """Estimate liquidity costs"""
        # Base spread cost
        mean_spread = spread_analysis.get('mean_spread', 0.001)
        
        # Impact cost based on depth
        mean_depth = depth_analysis.get('mean_total_depth', 100000)
        
        # Cost estimates for different trade sizes
        trade_sizes = [1000, 5000, 10000, 50000]
        cost_estimates = {}
        
        for size in trade_sizes:
            # Spread cost (constant)
            spread_cost = mean_spread * size
            
            # Impact cost (increases with size and decreases with depth)
            impact_cost = (size / mean_depth) ** 1.5 * 0.001 * size
            
            total_cost = spread_cost + impact_cost
            
            cost_estimates[f'trade_{size}'] = {
                'spread_cost': spread_cost,
                'impact_cost': impact_cost,
                'total_cost': total_cost,
                'cost_bps': (total_cost / size) * 10000
            }
            
        return {
            'mean_spread': mean_spread,
            'trade_cost_estimates': cost_estimates,
            'cost_quality_score': self._calculate_cost_quality_score(mean_spread, mean_depth)
        }
        
    def _calculate_cost_quality_score(self, spread: float, depth: float) -> float:
        """Calculate cost quality score"""
        # Lower spread and higher depth = better score
        spread_score = max(0, 1 - spread / 0.01)  # Normalize by 100bp
        depth_score = min(1, depth / 200000)      # Normalize by 200k depth
        
        return (spread_score * 0.6 + depth_score * 0.4) * 100
        
    def monitor_liquidity_realtime(self, current_market_data: Dict[str, Any]) -> LiquidityMonitoring:
        """
        Real-time liquidity monitoring
        
        Args:
            current_market_data: Current market data snapshot
            
        Returns:
            Real-time monitoring results
        """
        # Store current data
        self.monitoring_data.append({
            'timestamp': datetime.now(),
            'data': current_market_data
        })
        
        # Keep only recent data
        max_history = 100
        if len(self.monitoring_data) > max_history:
            self.monitoring_data = self.monitoring_data[-max_history:]
            
        # Detect changes
        changes_detected = self._detect_liquidity_changes()
        
        # Determine alert level
        alert_level = self._determine_alert_level(changes_detected)
        
        # Generate recommended actions
        recommended_actions = self._generate_realtime_actions(changes_detected)
        
        return LiquidityMonitoring(
            current_conditions=current_market_data,
            changes_detected=changes_detected,
            alert_level=alert_level,
            recommended_actions=recommended_actions
        )
        
    def _detect_liquidity_changes(self) -> List[str]:
        """Detect changes in liquidity conditions"""
        if len(self.monitoring_data) < 2:
            return []
            
        changes = []
        
        # Compare current with previous
        current = self.monitoring_data[-1]['data']
        previous = self.monitoring_data[-2]['data']
        
        # Spread change
        if 'spread' in current and 'spread' in previous:
            spread_change = (current['spread'] - previous['spread']) / previous['spread']
            if abs(spread_change) > 0.2:  # 20% change
                changes.append("SPREAD_CHANGE")
                
        # Volume change
        if 'volume' in current and 'volume' in previous:
            volume_change = (current['volume'] - previous['volume']) / previous['volume']
            if volume_change > 1.0:  # 100% increase
                changes.append("VOLUME_SPIKE")
            elif volume_change < -0.5:  # 50% decrease
                changes.append("VOLUME_DROP")
                
        # Price change
        if 'price' in current and 'price' in previous:
            price_change = abs(current['price'] - previous['price']) / previous['price']
            if price_change > 0.02:  # 2% price move
                changes.append("PRICE_MOVE")
                
        return changes
        
    def _determine_alert_level(self, changes_detected: List[str]) -> str:
        """Determine alert level based on changes"""
        if not changes_detected:
            return 'low'
            
        high_impact_changes = ['PRICE_MOVE', 'VOLUME_DROP']
        medium_impact_changes = ['SPREAD_CHANGE']
        low_impact_changes = ['VOLUME_SPIKE']
        
        for change in changes_detected:
            if change in high_impact_changes:
                return 'high'
            elif change in medium_impact_changes:
                if 'high' not in changes_detected:  # Don't downgrade if high already detected
                    return 'medium'
                    
        return 'low'
        
    def _generate_realtime_actions(self, changes_detected: List[str]) -> List[str]:
        """Generate real-time action recommendations"""
        actions = []
        
        for change in changes_detected:
            if change == "SPREAD_CHANGE":
                actions.append("Monitor market conditions closely")
                actions.append("Consider adjusting order placement strategy")
            elif change == "VOLUME_SPIKE":
                actions.append("Increased trading opportunity")
                actions.append("Consider accelerating execution")
            elif change == "VOLUME_DROP":
                actions.append("Reduced liquidity - use caution")
                actions.append("Consider pausing large orders")
            elif change == "PRICE_MOVE":
                actions.append("Price movement detected - reassess strategy")
                actions.append("Review position sizing")
                
        return actions
        
    def compare_liquidity_periods(self, period1_data: Dict[str, pd.DataFrame],
                                period2_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Compare liquidity conditions across two periods
        
        Args:
            period1_data: First period data {'market_data': df, 'order_book': df}
            period2_data: Second period data
            
        Returns:
            Period comparison results
        """
        # Analyze both periods
        report1 = self.analyze_liquidity_comprehensive(
            period1_data.get('market_data', pd.DataFrame()),
            period1_data.get('order_book', pd.DataFrame())
        )
        
        report2 = self.analyze_liquidity_comprehensive(
            period2_data.get('market_data', pd.DataFrame()),
            period2_data.get('order_book', pd.DataFrame())
        )
        
        # Compare metrics
        comparison = {
            'period1_report': report1,
            'period2_report': report2,
            'differences': {},
            'improvement_areas': [],
            'deterioration_areas': []
        }
        
        # Overall score comparison
        score_diff = report2.overall_liquidity_score - report1.overall_liquidity_score
        comparison['overall_score_change'] = score_diff
        
        # Detailed comparisons
        metrics_to_compare = [
            'overall_liquidity_score',
            'bid_ask_spread',
            'market_depth',
            'liquidity_cost'
        ]
        
        for metric in metrics_to_compare:
            if hasattr(report1, metric) and hasattr(report2, metric):
                val1 = getattr(report1, metric)
                val2 = getattr(report2, metric)
                
                if isinstance(val1, dict) and isinstance(val2, dict):
                    comparison['differences'][metric] = {}
                    for submetric in val1:
                        if submetric in val2:
                            if isinstance(val1[submetric], (int, float)) and isinstance(val2[submetric], (int, float)):
                                diff = val2[submetric] - val1[submetric]
                                comparison['differences'][metric][submetric] = diff
                                
                                # Identify improvement/deterioration
                                if diff > 0:  # Improvement (lower is better for spreads and costs)
                                    if 'spread' in metric.lower() or 'cost' in metric.lower():
                                        comparison['deterioration_areas'].append(f"{metric}.{submetric}")
                                    else:
                                        comparison['improvement_areas'].append(f"{metric}.{submetric}")
                                elif diff < 0:
                                    if 'spread' in metric.lower() or 'cost' in metric.lower():
                                        comparison['improvement_areas'].append(f"{metric}.{submetric}")
                                    else:
                                        comparison['deterioration_areas'].append(f"{metric}.{submetric}")
                else:
                    comparison['differences'][metric] = val2 - val1
        
        return comparison
        
    def generate_liquidity_forecast(self, historical_data: pd.DataFrame,
                                  forecast_horizon: int = 10) -> Dict[str, Any]:
        """
        Liquidity conditions forecast
        
        Args:
            historical_data: Historical liquidity data
            forecast_horizon: Number of periods to forecast
            
        Returns:
            Liquidity forecast results
        """
        if len(historical_data) < 50:
            return {'error': 'Insufficient data for forecasting'}
            
        # Extract time series
        spreads = historical_data.get('spread', pd.Series())
        volumes = historical_data.get('volume', pd.Series())
        
        if spreads.empty or volumes.empty:
            return {'error': 'Missing required data columns'}
            
        # Simple forecasting using moving averages
        forecast_data = {}
        
        # Spread forecast
        spread_ma = spreads.rolling(window=10).mean()
        spread_trend = spread_ma.diff().mean()
        
        spread_forecast = []
        for i in range(forecast_horizon):
            next_spread = spread_ma.iloc[-1] + spread_trend * (i + 1)
            spread_forecast.append(max(0, next_spread))  # Ensure non-negative
            
        forecast_data['spread'] = {
            'forecast': spread_forecast,
            'confidence': min(0.9, len(historical_data) / 1000)  # Higher confidence with more data
        }
        
        # Volume forecast
        volume_ma = volumes.rolling(window=10).mean()
        volume_trend = volume_ma.diff().mean()
        
        volume_forecast = []
        for i in range(forecast_horizon):
            next_volume = volume_ma.iloc[-1] + volume_trend * (i + 1)
            volume_forecast.append(max(0, next_volume))
            
        forecast_data['volume'] = {
            'forecast': volume_forecast,
            'confidence': min(0.9, len(historical_data) / 1000)
        }
        
        # Liquidity score forecast (simplified)
        score_forecast = []
        for i in range(forecast_horizon):
            # Assume correlation with volume and inverse correlation with spread
            volume_factor = volume_forecast[i] / volumes.mean()
            spread_factor = spreads.mean() / spread_forecast[i] if spread_forecast[i] > 0 else 1
            
            predicted_score = 50 * volume_factor * spread_factor
            score_forecast.append(max(0, min(100, predicted_score)))
            
        forecast_data['liquidity_score'] = {
            'forecast': score_forecast,
            'confidence': 0.7  # Lower confidence for derived metric
        }
        
        return {
            'forecast_horizon': forecast_horizon,
            'forecast_data': forecast_data,
            'forecast_timestamp': datetime.now(),
            'model_summary': 'Simple moving average trend extrapolation'
        }
        
    def generate_system_report(self) -> str:
        """
        Generate comprehensive liquidity system report
        
        Returns:
            Formatted system report
        """
        report = []
        report.append("=== LIQUIDITY ANALYSIS SYSTEM REPORT ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # System status
        report.append("SYSTEM STATUS:")
        report.append(f"  Component Analyzers: {len(self.liquidity_analyzer,)} initialized")
        report.append(f"  Monitoring Data Points: {len(self.monitoring_data)}")
        report.append(f"  Alert Thresholds: {len(self.alert_thresholds)} configured")
        report.append("")
        
        # Recent monitoring
        if self.monitoring_data:
            latest = self.monitoring_data[-1]
            report.append("LATEST MONITORING:")
            report.append(f"  Timestamp: {latest['timestamp'].strftime('%H:%M:%S')}")
            report.append(f"  Data Available: {list(latest['data'].keys())}")
            report.append("")
            
        # Alert thresholds
        report.append("ALERT THRESHOLDS:")
        for threshold, value in self.alert_thresholds.items():
            report.append(f"  {threshold}: {value}")
        report.append("")
        
        # Component status
        report.append("COMPONENT STATUS:")
        report.append(f"  Liquidity Analyzer: Active")
        report.append(f"  Spread Analyzer: Active")
        report.append(f"  Depth Analyzer: Active")
        report.append("")
        
        return "\n".join(report)
        
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'monitoring_data_points': len(self.monitoring_data),
            'alert_thresholds': self.alert_thresholds,
            'components_initialized': 3,  # All main components
            'system_status': 'operational',
            'last_monitoring': self.monitoring_data[-1]['timestamp'].isoformat() if self.monitoring_data else None
        }