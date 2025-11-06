"""
Performance Optimization Module

Ushbu modul cycle-adjusted performance metrics, long-term performance tracking,
continuous improvement loops va benchmarking uchun mo'ljallangan.

Imkoniyatlar:
- Cycle-adjusted performance metrics
- Long-term performance tracking
- Adaptation effectiveness measurement
- Continuous improvement loops
- Performance benchmarking
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import warnings
from scipy import stats
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings('ignore')

class PerformanceOptimizer:
    """
    Economic Cycle-Based Performance Optimization Class
    """
    
    def __init__(self, 
                 benchmark_data: Optional[pd.DataFrame] = None,
                 performance_horizon: int = 36):
        """
        Performance Optimizer initialize qilish
        
        Args:
            benchmark_data: Benchmark performance ma'lumotlari
            performance_horizon: Performance hisoblash uchun horizon (oylar)
        """
        
        self.benchmark_data = benchmark_data
        self.performance_horizon = performance_horizon
        
        # Performance tracking
        self.performance_history = []
        self.cycle_performance = {}
        self.adaptation_effectiveness = {}
        
        # Optimization parameters
        self.optimization_config = {
            'cycle_adjustment_enabled': True,
            'risk_adjusted_metrics': True,
            'long_term_tracking': True,
            'continuous_improvement': True
        }
        
        # Performance benchmarks
        self.performance_benchmarks = {
            'sharpe_ratio_threshold': 1.0,
            'max_drawdown_threshold': -0.20,
            'volatility_threshold': 0.25,
            'return_threshold': 0.12
        }
        
        # Cycle-specific performance tracking
        self.cycle_specific_metrics = {
            'expansion': {'count': 0, 'total_return': 0, 'avg_sharpe': 0},
            'contraction': {'count': 0, 'total_return': 0, 'avg_sharpe': 0},
            'transition': {'count': 0, 'total_return': 0, 'avg_sharpe': 0}
        }
    
    def optimize_performance(self, 
                           performance_data: pd.DataFrame,
                           economic_cycles: Dict[str, Any],
                           adaptation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Performance optimization
        
        Args:
            performance_data: Portfolio performance ma'lumotlari
            economic_cycles: Iqtisodiy sikl ma'lumotlari
            adaptation_data: Adaptation ma'lumotlari (optional)
            
        Returns:
            dict: Optimization results
        """
        
        try:
            # 1. Cycle-Adjusted Performance Analysis
            cycle_adjusted_performance = self._analyze_cycle_adjusted_performance(
                performance_data, economic_cycles
            )
            
            # 2. Long-term Performance Tracking
            long_term_performance = self._track_long_term_performance(
                performance_data, economic_cycles
            )
            
            # 3. Adaptation Effectiveness Measurement
            adaptation_effectiveness = self._measure_adaptation_effectiveness(
                adaptation_data, economic_cycles, performance_data
            )
            
            # 4. Performance Benchmarking
            performance_benchmarking = self._perform_performance_benchmarking(
                cycle_adjusted_performance, long_term_performance
            )
            
            # 5. Continuous Improvement Analysis
            improvement_analysis = self._analyze_continuous_improvement(
                long_term_performance, adaptation_effectiveness
            )
            
            # 6. Performance Optimization Recommendations
            optimization_recommendations = self._generate_optimization_recommendations(
                cycle_adjusted_performance, long_term_performance, 
                adaptation_effectiveness, performance_benchmarking
            )
            
            optimization_results = {
                'timestamp': pd.Timestamp.now(),
                'cycle_adjusted_performance': cycle_adjusted_performance,
                'long_term_performance': long_term_performance,
                'adaptation_effectiveness': adaptation_effectiveness,
                'performance_benchmarking': performance_benchmarking,
                'improvement_analysis': improvement_analysis,
                'optimization_recommendations': optimization_recommendations,
                'performance_scorecard': self._create_performance_scorecard(
                    cycle_adjusted_performance, performance_benchmarking
                ),
                'optimization_summary': self._create_optimization_summary(
                    optimization_recommendations, improvement_analysis
                )
            }
            
            # Update tracking records
            self._update_performance_tracking(optimization_results)
            
            return optimization_results
            
        except Exception as e:
            return {'error': f'Performance optimization failed: {str(e)}'}
    
    def _analyze_cycle_adjusted_performance(self, 
                                          performance_data: pd.DataFrame,
                                          economic_cycles: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cycle-adjusted performance analysis
        """
        
        if performance_data.empty:
            return {'error': 'No performance data available'}
        
        cycle_adjustments = {}
        
        # Extract cycle information
        if 'primary_cycle_analysis' in economic_cycles:
            cycle_data = economic_cycles['primary_cycle_analysis']
            current_phase = cycle_data.get('current_phase', 'unknown')
        else:
            current_phase = 'unknown'
        
        # Calculate performance by economic cycle
        for column in performance_data.select_dtypes(include=[np.number]).columns:
            returns = performance_data[column].pct_change().dropna()
            
            # Basic performance metrics
            total_return = (performance_data[column].iloc[-1] / performance_data[column].iloc[0] - 1) if len(performance_data) > 1 and performance_data[column].iloc[0] != 0 else 0
            annual_return = ((performance_data[column].iloc[-1] / performance_data[column].iloc[0]) ** (12 / len(performance_data)) - 1) if len(performance_data) > 1 else 0
            volatility = returns.std() * np.sqrt(12)
            sharpe_ratio = annual_return / volatility if volatility > 0 else 0
            
            # Cycle adjustment factor
            cycle_adjustment_factor = self._calculate_cycle_adjustment_factor(current_phase)
            
            # Cycle-adjusted metrics
            cycle_adjusted_return = annual_return * cycle_adjustment_factor
            cycle_adjusted_sharpe = sharpe_ratio * cycle_adjustment_factor
            
            # Risk metrics
            cumulative_returns = (1 + returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            cycle_adjustments[column] = {
                'raw_performance': {
                    'total_return': total_return,
                    'annual_return': annual_return,
                    'volatility': volatility,
                    'sharpe_ratio': sharpe_ratio
                },
                'cycle_adjustment_factor': cycle_adjustment_factor,
                'cycle_adjusted_performance': {
                    'cycle_adjusted_return': cycle_adjusted_return,
                    'cycle_adjusted_sharpe': cycle_adjusted_sharpe,
                    'current_cycle_phase': current_phase
                },
                'risk_metrics': {
                    'max_drawdown': max_drawdown,
                    'volatility_risk': 'high' if volatility > 0.3 else 'medium' if volatility > 0.2 else 'low',
                    'drawdown_risk': 'high' if max_drawdown < -0.3 else 'medium' if max_drawdown < -0.15 else 'low'
                },
                'performance_rating': self._rate_cycle_adjusted_performance(cycle_adjusted_return, cycle_adjusted_sharpe, max_drawdown)
            }
        
        return {
            'cycle_adjustments': cycle_adjustments,
            'cycle_specific_performance': self._analyze_cycle_specific_performance(cycle_adjustments),
            'overall_cycle_adjustment': self._calculate_overall_cycle_adjustment(cycle_adjustments),
            'cycle_performance_summary': self._create_cycle_performance_summary(cycle_adjustments)
        }
    
    def _calculate_cycle_adjustment_factor(self, cycle_phase: str) -> float:
        """
        Calculate cycle adjustment factor
        """
        
        # Historical cycle performance factors (simplified)
        cycle_factors = {
            'expansion': 1.2,    # 20% boost during expansion
            'peak': 0.9,         # 10% reduction at peak
            'contraction': 0.7,  # 30% reduction during contraction  
            'trough': 1.1,       # 10% boost at trough
            'transition': 1.0,   # No adjustment during transition
            'unknown': 1.0       # Default no adjustment
        }
        
        return cycle_factors.get(cycle_phase, 1.0)
    
    def _rate_cycle_adjusted_performance(self, adj_return: float, adj_sharpe: float, max_dd: float) -> str:
        """
        Rate cycle-adjusted performance
        """
        
        if adj_sharpe > 1.5 and adj_return > 0.15 and max_dd > -0.15:
            return 'excellent'
        elif adj_sharpe > 1.0 and adj_return > 0.10 and max_dd > -0.25:
            return 'good'
        elif adj_sharpe > 0.5 and adj_return > 0.05 and max_dd > -0.35:
            return 'fair'
        elif adj_sharpe > 0 and max_dd > -0.50:
            return 'poor'
        else:
            return 'very_poor'
    
    def _analyze_cycle_specific_performance(self, cycle_adjustments: Dict) -> Dict[str, Any]:
        """
        Analyze performance specific to different cycles
        """
        
        cycle_performance = {}
        
        for asset, metrics in cycle_adjustments.items():
            current_phase = metrics['cycle_adjusted_performance']['current_cycle_phase']
            cycle_adj_return = metrics['cycle_adjusted_performance']['cycle_adjusted_return']
            cycle_adj_sharpe = metrics['cycle_adjusted_performance']['cycle_adjusted_sharpe']
            
            if current_phase not in cycle_performance:
                cycle_performance[current_phase] = []
            
            cycle_performance[current_phase].append({
                'asset': asset,
                'adjusted_return': cycle_adj_return,
                'adjusted_sharpe': cycle_adj_sharpe
            })
        
        # Calculate averages by cycle
        cycle_averages = {}
        for cycle, performances in cycle_performance.items():
            returns = [p['adjusted_return'] for p in performances]
            sharpes = [p['adjusted_sharpe'] for p in performances]
            
            cycle_averages[cycle] = {
                'average_return': np.mean(returns),
                'average_sharpe': np.mean(sharpes),
                'asset_count': len(performances),
                'best_performing_asset': max(performances, key=lambda x: x['adjusted_sharpe'])['asset']
            }
        
        return cycle_averages
    
    def _calculate_overall_cycle_adjustment(self, cycle_adjustments: Dict) -> Dict[str, Any]:
        """
        Calculate overall cycle adjustment impact
        """
        
        if not cycle_adjustments:
            return {'error': 'No cycle adjustments to calculate'}
        
        raw_returns = []
        adj_returns = []
        raw_sharpes = []
        adj_sharpes = []
        
        for metrics in cycle_adjustments.values():
            raw_returns.append(metrics['raw_performance']['annual_return'])
            adj_returns.append(metrics['cycle_adjusted_performance']['cycle_adjusted_return'])
            raw_sharpes.append(metrics['raw_performance']['sharpe_ratio'])
            adj_sharpes.append(metrics['cycle_adjusted_performance']['cycle_adjusted_sharpe'])
        
        return {
            'raw_performance_avg': {
                'average_return': np.mean(raw_returns),
                'average_sharpe': np.mean(raw_sharpes)
            },
            'adjusted_performance_avg': {
                'average_return': np.mean(adj_returns),
                'average_sharpe': np.mean(adj_sharpes)
            },
            'adjustment_impact': {
                'return_impact': np.mean(adj_returns) - np.mean(raw_returns),
                'sharpe_impact': np.mean(adj_sharpes) - np.mean(raw_sharpes)
            },
            'adjustment_effectiveness': 'positive' if np.mean(adj_sharpes) > np.mean(raw_sharpes) else 'negative'
        }
    
    def _create_cycle_performance_summary(self, cycle_adjustments: Dict) -> Dict[str, Any]:
        """
        Create cycle performance summary
        """
        
        if not cycle_adjustments:
            return {'summary': 'No performance data available'}
        
        performance_ratings = [metrics['performance_rating'] for metrics in cycle_adjustments.values()]
        
        rating_counts = {}
        for rating in performance_ratings:
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        # Calculate weighted performance score
        rating_scores = {
            'excellent': 5, 'good': 4, 'fair': 3, 'poor': 2, 'very_poor': 1
        }
        
        weighted_score = sum(
            rating_counts[rating] * rating_scores[rating] 
            for rating in rating_counts.keys()
        ) / len(performance_ratings)
        
        return {
            'performance_distribution': rating_counts,
            'weighted_performance_score': weighted_score,
            'overall_performance_grade': (
                'A' if weighted_score >= 4.5 else
                'B' if weighted_score >= 3.5 else
                'C' if weighted_score >= 2.5 else
                'D' if weighted_score >= 1.5 else
                'F'
            ),
            'improvement_areas': self._identify_improvement_areas(rating_counts)
        }
    
    def _identify_improvement_areas(self, rating_counts: Dict[str, int]) -> List[str]:
        """
        Identify areas for improvement
        """
        
        improvement_areas = []
        
        poor_ratings = rating_counts.get('poor', 0) + rating_counts.get('very_poor', 0)
        total_ratings = sum(rating_counts.values())
        
        if poor_ratings / total_ratings > 0.3:
            improvement_areas.append('significant_performance_issues')
        
        if rating_counts.get('excellent', 0) == 0:
            improvement_areas.append('lack_of_excellent_performance')
        
        if rating_counts.get('fair', 0) > rating_counts.get('good', 0):
            improvement_areas.append('performance_consistency')
        
        return improvement_areas
    
    def _track_long_term_performance(self, 
                                   performance_data: pd.DataFrame,
                                   economic_cycles: Dict[str, Any]) -> Dict[str, Any]:
        """
        Long-term performance tracking
        """
        
        if performance_data.empty:
            return {'error': 'No performance data available'}
        
        long_term_metrics = {}
        
        # Define time periods for analysis
        time_periods = {
            '1_year': 12,
            '2_years': 24,
            '3_years': 36,
            'ytd': 'ytd'
        }
        
        for column in performance_data.select_dtypes(include=[np.number]).columns:
            returns = performance_data[column].pct_change().dropna()
            
            # Calculate returns for different periods
            period_returns = {}
            
            for period_name, period_length in time_periods.items():
                if period_length == 'ytd':
                    # Year-to-date calculation
                    current_year = performance_data.index[-1].year if hasattr(performance_data.index, 'year') else 2023
                    ytd_data = performance_data[performance_data.index.year == current_year] if hasattr(performance_data.index, 'year') else performance_data.tail(12)
                    if len(ytd_data) > 1 and ytd_data[column].iloc[0] != 0:
                        period_returns[period_name] = (ytd_data[column].iloc[-1] / ytd_data[column].iloc[0] - 1)
                    else:
                        period_returns[period_name] = 0
                else:
                    if len(performance_data) >= period_length and performance_data[column].iloc[-period_length] != 0:
                        period_returns[period_name] = (
                            performance_data[column].iloc[-1] / performance_data[column].iloc[-period_length] - 1
                        )
                    else:
                        period_returns[period_name] = 0
            
            # Rolling performance metrics
            rolling_metrics = self._calculate_rolling_metrics(returns)
            
            # Performance consistency analysis
            consistency_analysis = self._analyze_performance_consistency(returns)
            
            long_term_metrics[column] = {
                'period_returns': period_returns,
                'rolling_performance': rolling_metrics,
                'consistency_analysis': consistency_analysis,
                'long_term_rating': self._rate_long_term_performance(period_returns, rolling_metrics)
            }
        
        return {
            'long_term_metrics': long_term_metrics,
            'portfolio_long_term_summary': self._create_portfolio_long_term_summary(long_term_metrics),
            'performance_consistency': self._assess_portfolio_consistency(long_term_metrics),
            'long_term_trends': self._analyze_long_term_trends(long_term_metrics)
        }
    
    def _calculate_rolling_metrics(self, returns: pd.Series, window: int = 12) -> Dict[str, Any]:
        """
        Calculate rolling performance metrics
        """
        
        if len(returns) < window:
            return {'error': 'Insufficient data for rolling metrics'}
        
        rolling_returns = returns.rolling(window).sum() * 12  # Annualized
        rolling_volatility = returns.rolling(window).std() * np.sqrt(12)
        rolling_sharpe = rolling_returns / rolling_volatility
        
        return {
            'rolling_returns': {
                'mean': rolling_returns.mean(),
                'std': rolling_returns.std(),
                'current': rolling_returns.iloc[-1],
                'min': rolling_returns.min(),
                'max': rolling_returns.max()
            },
            'rolling_volatility': {
                'mean': rolling_volatility.mean(),
                'current': rolling_volatility.iloc[-1],
                'trend': 'increasing' if rolling_volatility.tail(6).mean() > rolling_volatility.head(6).mean() else 'decreasing'
            },
            'rolling_sharpe': {
                'mean': rolling_sharpe.mean(),
                'current': rolling_sharpe.iloc[-1],
                'consistency': 1 - (rolling_sharpe.std() / (rolling_sharpe.mean() + 0.01))
            }
        }
    
    def _analyze_performance_consistency(self, returns: pd.Series) -> Dict[str, Any]:
        """
        Analyze performance consistency
        """
        
        if len(returns) < 24:
            return {'error': 'Insufficient data for consistency analysis'}
        
        # Calculate rolling correlations
        rolling_correlations = []
        
        for i in range(12, len(returns)):
            current_window = returns.iloc[i-12:i]
            previous_window = returns.iloc[i-24:i-12]
            
            if len(current_window) > 0 and len(previous_window) > 0:
                correlation = current_window.corr(previous_window)
                if not np.isnan(correlation):
                    rolling_correlations.append(correlation)
        
        # Consistency metrics
        positive_months = (returns > 0).sum()
        total_months = len(returns)
        win_rate = positive_months / total_months
        
        # Volatility of returns
        return_volatility = returns.std()
        
        # Drawdown frequency
        cumulative = (1 + returns).cumprod()
        drawdowns = []
        
        peak = cumulative.iloc[0]
        for value in cumulative:
            if value > peak:
                peak = value
            drawdowns.append((value - peak) / peak)
        
        drawdown_frequency = len([dd for dd in drawdowns if dd < -0.05]) / len(drawdowns)
        
        return {
            'win_rate': win_rate,
            'return_volatility': return_volatility,
            'drawdown_frequency': drawdown_frequency,
            'rolling_correlation_avg': np.mean(rolling_correlations) if rolling_correlations else 0,
            'consistency_score': self._calculate_consistency_score(win_rate, return_volatility, drawdown_frequency),
            'consistency_rating': self._rate_consistency(win_rate, return_volatility, drawdown_frequency)
        }
    
    def _calculate_consistency_score(self, win_rate: float, volatility: float, drawdown_freq: float) -> float:
        """
        Calculate consistency score
        """
        
        # Higher win rate is better, lower volatility is better, lower drawdown frequency is better
        consistency_score = (
            win_rate * 0.4 +
            (1 - min(volatility / 0.5, 1)) * 0.3 +  # Normalize volatility
            (1 - min(drawdown_freq / 0.5, 1)) * 0.3   # Normalize drawdown frequency
        )
        
        return consistency_score
    
    def _rate_consistency(self, win_rate: float, volatility: float, drawdown_freq: float) -> str:
        """
        Rate performance consistency
        """
        
        if win_rate > 0.7 and volatility < 0.15 and drawdown_freq < 0.1:
            return 'excellent'
        elif win_rate > 0.6 and volatility < 0.25 and drawdown_freq < 0.2:
            return 'good'
        elif win_rate > 0.5 and volatility < 0.35 and drawdown_freq < 0.3:
            return 'fair'
        else:
            return 'poor'
    
    def _rate_long_term_performance(self, period_returns: Dict[str, float], rolling_metrics: Dict[str, Any]) -> str:
        """
        Rate long-term performance
        """
        
        # Weight recent performance more heavily
        recent_return = period_returns.get('1_year', 0)
        long_term_return = period_returns.get('3_years', 0) if '3_years' in period_returns else period_returns.get('2_years', 0)
        current_sharpe = rolling_metrics.get('rolling_sharpe', {}).get('current', 0)
        
        # Overall score calculation
        if 'error' in rolling_metrics:
            return 'insufficient_data'
        
        score_components = [
            recent_return * 0.4,  # 40% weight to recent performance
            long_term_return * 0.3,  # 30% weight to long-term performance
            current_sharpe * 0.3   # 30% weight to current risk-adjusted performance
        ]
        
        overall_score = sum(score_components)
        
        if overall_score > 0.15:
            return 'excellent'
        elif overall_score > 0.10:
            return 'good'
        elif overall_score > 0.05:
            return 'fair'
        elif overall_score > 0:
            return 'poor'
        else:
            return 'very_poor'
    
    def _create_portfolio_long_term_summary(self, long_term_metrics: Dict) -> Dict[str, Any]:
        """
        Create portfolio long-term summary
        """
        
        if not long_term_metrics:
            return {'summary': 'No long-term metrics available'}
        
        # Aggregate metrics across all assets
        all_1y_returns = []
        all_3y_returns = []
        all_current_sharpes = []
        all_consistency_scores = []
        
        for metrics in long_term_metrics.values():
            if 'period_returns' in metrics:
                if '1_year' in metrics['period_returns']:
                    all_1y_returns.append(metrics['period_returns']['1_year'])
                if '3_years' in metrics['period_returns']:
                    all_3y_returns.append(metrics['period_returns']['3_years'])
                elif '2_years' in metrics['period_returns']:
                    all_3y_returns.append(metrics['period_returns']['2_years'])
            
            if 'rolling_performance' in metrics and 'rolling_sharpe' in metrics['rolling_performance']:
                all_current_sharpes.append(metrics['rolling_performance']['rolling_sharpe']['current'])
            
            if 'consistency_analysis' in metrics and 'consistency_score' in metrics['consistency_analysis']:
                all_consistency_scores.append(metrics['consistency_analysis']['consistency_score'])
        
        return {
            'portfolio_1y_return': np.mean(all_1y_returns) if all_1y_returns else 0,
            'portfolio_3y_return': np.mean(all_3y_returns) if all_3y_returns else 0,
            'portfolio_current_sharpe': np.mean(all_current_sharpes) if all_current_sharpes else 0,
            'portfolio_consistency_score': np.mean(all_consistency_scores) if all_consistency_scores else 0,
            'best_performing_asset': max(long_term_metrics.keys(), 
                                       key=lambda x: long_term_metrics[x].get('period_returns', {}).get('1_year', 0)) if long_term_metrics else 'unknown',
            'portfolio_diversification_benefit': self._calculate_diversification_benefit(long_term_metrics)
        }
    
    def _calculate_diversification_benefit(self, long_term_metrics: Dict) -> float:
        """
        Calculate diversification benefit
        """
        
        if len(long_term_metrics) < 2:
            return 0
        
        # Calculate average correlation between assets
        returns_data = {}
        
        for asset, metrics in long_term_metrics.items():
            if 'period_returns' in metrics and '1_year' in metrics['period_returns']:
                # Simplified - use period returns as proxy for correlation calculation
                returns_data[asset] = metrics['period_returns']['1_year']
        
        if len(returns_data) < 2:
            return 0
        
        # Simple diversification benefit based on return dispersion
        returns = list(returns_data.values())
        return_dispersion = np.std(returns) / (np.mean(returns) + 0.01)
        
        # Higher dispersion suggests better diversification potential
        return min(return_dispersion, 1.0)
    
    def _assess_portfolio_consistency(self, long_term_metrics: Dict) -> Dict[str, Any]:
        """
        Assess overall portfolio consistency
        """
        
        if not long_term_metrics:
            return {'assessment': 'No data available'}
        
        consistency_scores = []
        
        for metrics in long_term_metrics.values():
            if 'consistency_analysis' in metrics:
                consistency_scores.append(metrics['consistency_analysis'].get('consistency_score', 0))
        
        if not consistency_scores:
            return {'assessment': 'No consistency data available'}
        
        avg_consistency = np.mean(consistency_scores)
        
        return {
            'portfolio_consistency_score': avg_consistency,
            'consistency_rating': (
                'excellent' if avg_consistency > 0.8 else
                'good' if avg_consistency > 0.6 else
                'fair' if avg_consistency > 0.4 else
                'poor'
            ),
            'consistency_spread': np.std(consistency_scores),
            'most_consistent_asset': max(long_term_metrics.keys(),
                                       key=lambda x: long_term_metrics[x].get('consistency_analysis', {}).get('consistency_score', 0)) if long_term_metrics else 'unknown'
        }
    
    def _analyze_long_term_trends(self, long_term_metrics: Dict) -> Dict[str, Any]:
        """
        Analyze long-term performance trends
        """
        
        if not long_term_metrics:
            return {'trends': 'No trend data available'}
        
        trend_analysis = {}
        
        for asset, metrics in long_term_metrics.items():
            period_returns = metrics.get('period_returns', {})
            
            # Trend direction analysis
            returns_1y = period_returns.get('1_year', 0)
            returns_3y = period_returns.get('3_years', 0) if '3_years' in period_returns else period_returns.get('2_years', 0)
            
            if returns_3y > 0 and returns_1y > 0:
                if returns_1y > returns_3y:
                    trend = 'accelerating'
                elif returns_1y < returns_3y * 0.8:
                    trend = 'decelerating'
                else:
                    trend = 'stable'
            elif returns_3y > 0:
                trend = 'recent_improvement'
            elif returns_1y > 0:
                trend = 'maintaining_gains'
            else:
                trend = 'declining'
            
            trend_analysis[asset] = {
                'trend_direction': trend,
                'performance_improvement': returns_1y - returns_3y if returns_3y != 0 else returns_1y,
                'trend_strength': abs(returns_1y - returns_3y) if returns_3y != 0 else abs(returns_1y)
            }
        
        return {
            'asset_trends': trend_analysis,
            'portfolio_trend_summary': self._summarize_portfolio_trends(trend_analysis)
        }
    
    def _summarize_portfolio_trends(self, trend_analysis: Dict) -> Dict[str, Any]:
        """
        Summarize overall portfolio trends
        """
        
        if not trend_analysis:
            return {'summary': 'No trend data available'}
        
        trend_counts = {}
        improving_assets = 0
        declining_assets = 0
        
        for trend_info in trend_analysis.values():
            trend = trend_info['trend_direction']
            trend_counts[trend] = trend_counts.get(trend, 0) + 1
            
            if trend in ['accelerating', 'recent_improvement']:
                improving_assets += 1
            elif trend in ['decelerating', 'declining']:
                declining_assets += 1
        
        total_assets = len(trend_analysis)
        
        return {
            'trend_distribution': trend_counts,
            'improving_assets_ratio': improving_assets / total_assets,
            'declining_assets_ratio': declining_assets / total_assets,
            'portfolio_trend_sentiment': (
                'positive' if improving_assets > declining_assets else
                'negative' if declining_assets > improving_assets else
                'neutral'
            )
        }
    
    def _measure_adaptation_effectiveness(self, 
                                        adaptation_data: Optional[Dict[str, Any]],
                                        economic_cycles: Dict[str, Any],
                                        performance_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Measure adaptation effectiveness
        """
        
        if adaptation_data is None or 'error' in adaptation_data:
            return {'error': 'No adaptation data available for effectiveness measurement'}
        
        effectiveness_metrics = {}
        
        # Extract adaptation results
        adaptation_results = adaptation_data.get('adaptation_engine_results', {})
        if 'error' in adaptation_results:
            return {'error': 'Invalid adaptation results'}
        
        # Measure timing effectiveness
        timing_effectiveness = self._measure_adaptation_timing(adaptation_results, economic_cycles)
        
        # Measure implementation effectiveness
        implementation_effectiveness = self._measure_implementation_effectiveness(
            adaptation_results, performance_data
        )
        
        # Measure performance impact
        performance_impact = self._measure_adaptation_performance_impact(
            adaptation_data, performance_data
        )
        
        # Calculate overall effectiveness
        overall_effectiveness = self._calculate_overall_adaptation_effectiveness(
            timing_effectiveness, implementation_effectiveness, performance_impact
        )
        
        effectiveness_metrics = {
            'timing_effectiveness': timing_effectiveness,
            'implementation_effectiveness': implementation_effectiveness,
            'performance_impact': performance_impact,
            'overall_effectiveness': overall_effectiveness,
            'adaptation_recommendations': self._generate_adaptation_recommendations(overall_effectiveness),
            'adaptation_learning': self._extract_adaptation_learning(adaptation_data)
        }
        
        return effectiveness_metrics
    
    def _measure_adaptation_timing(self, adaptation_results: Dict, economic_cycles: Dict) -> Dict[str, Any]:
        """
        Measure adaptation timing effectiveness
        """
        
        if 'cycle_detection' not in adaptation_results:
            return {'timing_rating': 'unknown', 'reason': 'No cycle detection data'}
        
        cycle_detection = adaptation_results['cycle_detection']
        
        # Assess how quickly adaptations were implemented relative to cycle changes
        timing_scores = []
        
        for cycle_type, cycle_info in cycle_detection.items():
            if 'cycle' in cycle_info:
                cycle_phase = cycle_info['cycle']
                
                # Score based on cycle phase timing
                if cycle_phase in ['expansion', 'contraction']:  # Active phases
                    timing_score = 0.8  # Good timing for active phases
                elif cycle_phase in ['peak', 'trough']:  # Transition points
                    timing_score = 0.6  # Acceptable timing for transitions
                else:
                    timing_score = 0.5  # Neutral timing
                
                timing_scores.append(timing_score)
        
        if not timing_scores:
            return {'timing_rating': 'unknown', 'reason': 'No cycle timing data'}
        
        avg_timing_score = np.mean(timing_scores)
        
        return {
            'timing_score': avg_timing_score,
            'timing_rating': (
                'excellent' if avg_timing_score > 0.8 else
                'good' if avg_timing_score > 0.6 else
                'fair' if avg_timing_score > 0.4 else
                'poor'
            ),
            'timing_factors': {
                'cycle_responsiveness': avg_timing_score,
                'adaptation_speed': 'medium'  # Would need more detailed timing data
            }
        }
    
    def _measure_implementation_effectiveness(self, adaptation_results: Dict, performance_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Measure adaptation implementation effectiveness
        """
        
        if 'implementation_priority' not in adaptation_results:
            return {'implementation_rating': 'unknown', 'reason': 'No implementation priority data'}
        
        implementation_priority = adaptation_results['implementation_priority']
        
        # Count implemented vs recommended actions
        total_recommended = sum(len(actions) for actions in implementation_priority.values())
        
        # Simple implementation score based on recommendation completeness
        implementation_score = min(total_recommended / 5, 1.0)  # Assume max 5 recommended actions
        
        return {
            'implementation_score': implementation_score,
            'implementation_rating': (
                'excellent' if implementation_score > 0.8 else
                'good' if implementation_score > 0.6 else
                'fair' if implementation_score > 0.4 else
                'poor'
            ),
            'implementation_details': {
                'total_recommended_actions': total_recommended,
                'priority_distribution': {k: len(v) for k, v in implementation_priority.items()}
            }
        }
    
    def _measure_adaptation_performance_impact(self, 
                                             adaptation_data: Dict[str, Any],
                                             performance_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Measure adaptation performance impact
        """
        
        if performance_data.empty:
            return {'performance_impact': 'unknown', 'reason': 'No performance data available'}
        
        # This is a simplified measurement - in practice would need pre/post adaptation comparison
        adaptation_results = adaptation_data.get('adaptation_engine_results', {})
        
        # Estimate performance impact based on adaptation strength
        estimated_impact = 0
        
        if 'optimized_adaptations' in adaptation_results:
            optimized = adaptation_results['optimized_adaptations']
            
            # Simple impact estimation based on number of optimizations
            optimization_count = 0
            
            if 'parameters' in optimized:
                optimization_count += len(optimized['parameters'])
            if 'positions' in optimized:
                optimization_count += len(optimized['positions'])
            
            # Estimate positive impact from optimizations
            estimated_impact = min(optimization_count * 0.01, 0.05)  # Max 5% estimated impact
        
        return {
            'estimated_performance_impact': estimated_impact,
            'impact_rating': (
                'positive' if estimated_impact > 0.02 else
                'neutral' if estimated_impact > -0.01 else
                'negative'
            ),
            'impact_confidence': 'low'  # Would need more detailed analysis for high confidence
        }
    
    def _calculate_overall_adaptation_effectiveness(self, 
                                                  timing_effectiveness: Dict,
                                                  implementation_effectiveness: Dict,
                                                  performance_impact: Dict) -> Dict[str, Any]:
        """
        Calculate overall adaptation effectiveness
        """
        
        # Extract scores
        timing_score = timing_effectiveness.get('timing_score', 0)
        implementation_score = implementation_effectiveness.get('implementation_score', 0)
        
        # Performance impact scoring
        estimated_impact = performance_impact.get('estimated_performance_impact', 0)
        impact_score = max(0, min(estimated_impact * 20, 1.0))  # Scale impact to [0,1]
        
        # Weighted overall effectiveness
        weights = {
            'timing': 0.3,
            'implementation': 0.4,
            'performance': 0.3
        }
        
        overall_score = (
            timing_score * weights['timing'] +
            implementation_score * weights['implementation'] +
            impact_score * weights['performance']
        )
        
        return {
            'overall_effectiveness_score': overall_score,
            'effectiveness_rating': (
                'excellent' if overall_score > 0.8 else
                'good' if overall_score > 0.6 else
                'fair' if overall_score > 0.4 else
                'poor'
            ),
            'component_scores': {
                'timing_effectiveness': timing_score,
                'implementation_effectiveness': implementation_score,
                'performance_impact_score': impact_score
            },
            'improvement_areas': self._identify_adaptation_improvement_areas(
                timing_score, implementation_score, impact_score
            )
        }
    
    def _identify_adaptation_improvement_areas(self, timing_score: float, implementation_score: float, impact_score: float) -> List[str]:
        """
        Identify areas for adaptation improvement
        """
        
        improvement_areas = []
        
        if timing_score < 0.6:
            improvement_areas.append('adaptation_timing')
        
        if implementation_score < 0.6:
            improvement_areas.append('implementation_completeness')
        
        if impact_score < 0.4:
            improvement_areas.append('adaptation_impact')
        
        return improvement_areas
    
    def _generate_adaptation_recommendations(self, overall_effectiveness: Dict) -> List[str]:
        """
        Generate adaptation improvement recommendations
        """
        
        recommendations = []
        component_scores = overall_effectiveness.get('component_scores', {})
        improvement_areas = overall_effectiveness.get('improvement_areas', [])
        
        for area in improvement_areas:
            if area == 'adaptation_timing':
                recommendations.append('Improve cycle detection and response timing')
            elif area == 'implementation_completeness':
                recommendations.append('Ensure complete implementation of recommended adaptations')
            elif area == 'adaptation_impact':
                recommendations.append('Focus on high-impact adaptations that can improve performance')
        
        # General recommendations based on overall rating
        overall_rating = overall_effectiveness.get('effectiveness_rating', 'unknown')
        
        if overall_rating in ['poor', 'fair']:
            recommendations.append('Review and strengthen the adaptation framework')
            recommendations.append('Increase monitoring frequency of economic indicators')
        
        return recommendations
    
    def _extract_adaptation_learning(self, adaptation_data: Dict) -> Dict[str, Any]:
        """
        Extract learning insights from adaptation process
        """
        
        learning_insights = {
            'successful_adaptations': [],
            'challenging_adaptations': [],
            'adaptation_patterns': {},
            'learning_recommendations': []
        }
        
        adaptation_results = adaptation_data.get('adaptation_engine_results', {})
        
        # Analyze implementation priority for patterns
        if 'implementation_priority' in adaptation_results:
            priority_data = adaptation_results['implementation_priority']
            
            high_priority_count = len(priority_data.get('high_priority', []))
            medium_priority_count = len(priority_data.get('medium_priority', []))
            
            learning_insights['adaptation_patterns'] = {
                'high_priority_adaptations': high_priority_count,
                'medium_priority_adaptations': medium_priority_count,
                'adaptation_complexity': 'high' if (high_priority_count + medium_priority_count) > 5 else 'moderate'
            }
        
        return learning_insights
    
    def _perform_performance_benchmarking(self, 
                                        cycle_adjusted_performance: Dict,
                                        long_term_performance: Dict) -> Dict[str, Any]:
        """
        Performance benchmarking against benchmarks
        """
        
        benchmarking_results = {
            'benchmark_comparison': {},
            'relative_performance': {},
            'benchmark_gaps': {},
            'benchmark_recommendations': []
        }
        
        # Benchmark comparison
        if self.benchmark_data is None:
            benchmarking_results['benchmark_comparison'] = {
                'status': 'no_benchmark_data_available',
                'recommendation': 'Obtain benchmark data for meaningful comparison'
            }
            return benchmarking_results
        
        # Compare performance against benchmarks
        benchmark_comparison = self._compare_against_benchmark(
            cycle_adjusted_performance, long_term_performance
        )
        
        benchmarking_results['benchmark_comparison'] = benchmark_comparison
        
        # Relative performance analysis
        relative_performance = self._analyze_relative_performance(benchmark_comparison)
        benchmarking_results['relative_performance'] = relative_performance
        
        # Identify benchmark gaps
        benchmark_gaps = self._identify_benchmark_gaps(benchmark_comparison)
        benchmarking_results['benchmark_gaps'] = benchmark_gaps
        
        # Generate recommendations
        benchmarking_results['benchmark_recommendations'] = self._generate_benchmarking_recommendations(
            benchmark_comparison, relative_performance
        )
        
        return benchmarking_results
    
    def _compare_against_benchmark(self, 
                                 cycle_adjusted_performance: Dict,
                                 long_term_performance: Dict) -> Dict[str, Any]:
        """
        Compare performance against benchmark
        """
        
        if self.benchmark_data.empty:
            return {'error': 'No benchmark data available'}
        
        comparison_results = {}
        
        # Extract portfolio metrics (simplified - taking first asset as proxy)
        cycle_adjustments = cycle_adjusted_performance.get('cycle_adjustments', {})
        long_term_metrics = long_term_performance.get('long_term_metrics', {})
        
        if not cycle_adjustments or not long_term_metrics:
            return {'error': 'Insufficient portfolio performance data'}
        
        # Take first asset for comparison
        first_asset = list(cycle_adjustments.keys())[0]
        
        portfolio_adj_sharpe = cycle_adjustments[first_asset]['cycle_adjusted_performance']['cycle_adjusted_sharpe']
        portfolio_1y_return = long_term_metrics[first_asset].get('period_returns', {}).get('1_year', 0)
        
        # Compare with benchmark (simplified - assuming single benchmark series)
        benchmark_column = self.benchmark_data.select_dtypes(include=[np.number]).columns[0]
        benchmark_returns = self.benchmark_data[benchmark_column].pct_change().dropna()
        
        benchmark_annual_return = benchmark_returns.mean() * 12
        benchmark_volatility = benchmark_returns.std() * np.sqrt(12)
        benchmark_sharpe = benchmark_annual_return / benchmark_volatility if benchmark_volatility > 0 else 0
        
        comparison_results = {
            'sharpe_ratio_comparison': {
                'portfolio': portfolio_adj_sharpe,
                'benchmark': benchmark_sharpe,
                'outperformance': portfolio_adj_sharpe - benchmark_sharpe
            },
            'return_comparison': {
                'portfolio_1y': portfolio_1y_return,
                'benchmark_1y': benchmark_annual_return,
                'return_outperformance': portfolio_1y_return - benchmark_annual_return
            },
            'risk_comparison': {
                'portfolio_volatility': cycle_adjustments[first_asset]['raw_performance']['volatility'],
                'benchmark_volatility': benchmark_volatility,
                'risk_difference': cycle_adjustments[first_asset]['raw_performance']['volatility'] - benchmark_volatility
            }
        }
        
        return comparison_results
    
    def _analyze_relative_performance(self, benchmark_comparison: Dict) -> Dict[str, Any]:
        """
        Analyze relative performance vs benchmark
        """
        
        if 'error' in benchmark_comparison:
            return {'relative_performance': 'unknown'}
        
        sharpe_comp = benchmark_comparison.get('sharpe_ratio_comparison', {})
        return_comp = benchmark_comparison.get('return_comparison', {})
        
        sharpe_outperformance = sharpe_comp.get('outperformance', 0)
        return_outperformance = return_comp.get('return_outperformance', 0)
        
        # Overall relative performance rating
        if sharpe_outperformance > 0.2 and return_outperformance > 0.02:
            relative_rating = 'outperforming'
        elif sharpe_outperformance > 0 and return_outperformance > 0:
            relative_rating = 'slightly_outperforming'
        elif sharpe_outperformance < -0.2 and return_outperformance < -0.02:
            relative_rating = 'underperforming'
        elif sharpe_outperformance < 0 and return_outperformance < 0:
            relative_rating = 'slightly_underperforming'
        else:
            relative_rating = 'in_line'
        
        return {
            'relative_performance_rating': relative_rating,
            'performance_leadership': (
                'clear_leader' if sharpe_outperformance > 0.3 else
                'modest_leader' if sharpe_outperformance > 0.1 else
                'in_line' if abs(sharpe_outperformance) <= 0.1 else
                'modest_laggard' if sharpe_outperformance > -0.3 else
                'clear_laggard'
            ),
            'outperformance_consistency': self._assess_outperformance_consistency(benchmark_comparison)
        }
    
    def _assess_outperformance_consistency(self, benchmark_comparison: Dict) -> str:
        """
        Assess consistency of outperformance
        """
        
        sharpe_comp = benchmark_comparison.get('sharpe_ratio_comparison', {})
        return_comp = benchmark_comparison.get('return_comparison', {})
        
        sharpe_outperf = sharpe_comp.get('outperformance', 0)
        return_outperf = return_comp.get('return_outperformance', 0)
        
        # Simple consistency assessment
        if sharpe_outperf > 0 and return_outperf > 0:
            return 'consistent_outperformance'
        elif sharpe_outperf < 0 and return_outperf < 0:
            return 'consistent_underperformance'
        elif (sharpe_outperf > 0 and return_outperf < 0) or (sharpe_outperf < 0 and return_outperf > 0):
            return 'mixed_performance'
        else:
            return 'inconsistent'
    
    def _identify_benchmark_gaps(self, benchmark_comparison: Dict) -> Dict[str, Any]:
        """
        Identify gaps vs benchmark
        """
        
        if 'error' in benchmark_comparison:
            return {'gaps': 'Cannot identify gaps without benchmark comparison'}
        
        gaps = {}
        
        sharpe_comp = benchmark_comparison.get('sharpe_ratio_comparison', {})
        return_comp = benchmark_comparison.get('return_comparison', {})
        risk_comp = benchmark_comparison.get('risk_comparison', {})
        
        sharpe_gap = sharpe_comp.get('outperformance', 0)
        return_gap = return_comp.get('return_outperformance', 0)
        risk_gap = risk_comp.get('risk_difference', 0)
        
        # Identify specific gaps
        if sharpe_gap < -0.1:
            gaps['sharpe_ratio_gap'] = 'significant_underperformance'
        elif sharpe_gap < 0:
            gaps['sharpe_ratio_gap'] = 'minor_underperformance'
        
        if return_gap < -0.02:
            gaps['return_gap'] = 'significant_return_gap'
        elif return_gap < 0:
            gaps['return_gap'] = 'minor_return_gap'
        
        if risk_gap > 0.05:
            gaps['risk_gap'] = 'excessive_risk_taking'
        elif risk_gap < -0.05:
            gaps['risk_gap'] = 'underexposure_to_risk'
        
        return {
            'identified_gaps': gaps,
            'gap_severity': (
                'critical' if len(gaps) >= 2 else
                'moderate' if len(gaps) == 1 else
                'minimal'
            )
        }
    
    def _generate_benchmarking_recommendations(self, 
                                             benchmark_comparison: Dict,
                                             relative_performance: Dict) -> List[str]:
        """
        Generate benchmarking-based recommendations
        """
        
        recommendations = []
        
        if 'error' in benchmark_comparison:
            recommendations.append('Obtain benchmark data for performance comparison')
            return recommendations
        
        sharpe_comp = benchmark_comparison.get('sharpe_ratio_comparison', {})
        return_comp = benchmark_comparison.get('return_comparison', {})
        
        sharpe_gap = sharpe_comp.get('outperformance', 0)
        return_gap = return_comp.get('return_outperformance', 0)
        
        # Performance gap recommendations
        if sharpe_gap < -0.1:
            recommendations.append('Improve risk-adjusted returns to match benchmark')
        
        if return_gap < -0.02:
            recommendations.append('Focus on return enhancement strategies')
        
        # Relative performance recommendations
        relative_rating = relative_performance.get('relative_performance_rating', 'unknown')
        
        if relative_rating in ['underperforming', 'slightly_underperforming']:
            recommendations.append('Review portfolio allocation and strategy implementation')
            recommendations.append('Consider benchmark-relative performance targets')
        
        if relative_rating == 'outperforming':
            recommendations.append('Maintain current strategy while managing tail risks')
        
        return recommendations
    
    def _analyze_continuous_improvement(self, 
                                      long_term_performance: Dict,
                                      adaptation_effectiveness: Dict) -> Dict[str, Any]:
        """
        Analyze continuous improvement opportunities
        """
        
        improvement_analysis = {
            'performance_trends': {},
            'adaptation_learning': {},
            'improvement_opportunities': [],
            'improvement_roadmap': {}
        }
        
        # Analyze performance trends for improvement
        if 'performance_trends' in long_term_performance:
            trend_summary = long_term_performance['performance_trends']
            
            improvement_analysis['performance_trends'] = {
                'trend_analysis': trend_summary,
                'improvement_potential': self._assess_improvement_potential(trend_summary)
            }
        
        # Analyze adaptation learning
        if 'adaptation_learning' in adaptation_effectiveness:
            adaptation_learning = adaptation_effectiveness.get('adaptation_learning', {})
            
            improvement_analysis['adaptation_learning'] = {
                'learning_insights': adaptation_learning,
                'learning_effectiveness': self._assess_learning_effectiveness(adaptation_learning)
            }
        
        # Identify improvement opportunities
        improvement_opportunities = self._identify_improvement_opportunities(
            long_term_performance, adaptation_effectiveness
        )
        improvement_analysis['improvement_opportunities'] = improvement_opportunities
        
        # Create improvement roadmap
        improvement_analysis['improvement_roadmap'] = self._create_improvement_roadmap(
            improvement_opportunities
        )
        
        return improvement_analysis
    
    def _assess_improvement_potential(self, trend_summary: Dict) -> str:
        """
        Assess improvement potential based on trends
        """
        
        improving_ratio = trend_summary.get('improving_assets_ratio', 0)
        declining_ratio = trend_summary.get('declining_assets_ratio', 0)
        
        if improving_ratio > 0.6:
            return 'high_potential'
        elif improving_ratio > 0.4:
            return 'moderate_potential'
        elif declining_ratio > 0.4:
            return 'urgent_improvement_needed'
        else:
            return 'maintain_current_approach'
    
    def _assess_learning_effectiveness(self, adaptation_learning: Dict) -> str:
        """
        Assess effectiveness of learning from adaptations
        """
        
        patterns = adaptation_learning.get('adaptation_patterns', {})
        
        if not patterns:
            return 'unknown'
        
        complexity = patterns.get('adaptation_complexity', 'moderate')
        
        if complexity == 'high':
            return 'learning_from_complex_situations'
        elif complexity == 'moderate':
            return 'moderate_learning_opportunities'
        else:
            return 'limited_learning_scope'
    
    def _identify_improvement_opportunities(self, 
                                          long_term_performance: Dict,
                                          adaptation_effectiveness: Dict) -> List[Dict]:
        """
        Identify specific improvement opportunities
        """
        
        opportunities = []
        
        # Performance-based opportunities
        if 'portfolio_long_term_summary' in long_term_performance:
            portfolio_summary = long_term_performance['portfolio_long_term_summary']
            
            current_sharpe = portfolio_summary.get('portfolio_current_sharpe', 0)
            if current_sharpe < 1.0:
                opportunities.append({
                    'area': 'risk_adjusted_returns',
                    'opportunity': 'improve_sharpe_ratio',
                    'priority': 'high' if current_sharpe < 0.5 else 'medium',
                    'target_improvement': 'increase_sharpe_by_0.3'
                })
        
        # Consistency-based opportunities
        if 'performance_consistency' in long_term_performance:
            consistency = long_term_performance['performance_consistency']
            consistency_score = consistency.get('portfolio_consistency_score', 0)
            
            if consistency_score < 0.6:
                opportunities.append({
                    'area': 'performance_consistency',
                    'opportunity': 'reduce_performance_volatility',
                    'priority': 'medium',
                    'target_improvement': 'increase_consistency_by_0.2'
                })
        
        # Adaptation-based opportunities
        if 'overall_effectiveness' in adaptation_effectiveness:
            effectiveness = adaptation_effectiveness['overall_effectiveness']
            effectiveness_rating = effectiveness.get('effectiveness_rating', 'unknown')
            
            if effectiveness_rating in ['poor', 'fair']:
                opportunities.append({
                    'area': 'adaptation_effectiveness',
                    'opportunity': 'improve_adaptation_process',
                    'priority': 'high',
                    'target_improvement': 'achieve_good_effectiveness_rating'
                })
        
        return opportunities
    
    def _create_improvement_roadmap(self, opportunities: List[Dict]) -> Dict[str, List]:
        """
        Create improvement roadmap
        """
        
        roadmap = {
            'immediate_actions': [],
            'short_term_goals': [],
            'long_term_objectives': []
        }
        
        for opportunity in opportunities:
            area = opportunity['area']
            priority = opportunity['priority']
            
            if priority == 'high':
                roadmap['immediate_actions'].append({
                    'action': opportunity['opportunity'],
                    'area': area,
                    'timeline': '1-3 months'
                })
            elif priority == 'medium':
                roadmap['short_term_goals'].append({
                    'goal': opportunity['opportunity'],
                    'area': area,
                    'timeline': '3-6 months'
                })
            else:
                roadmap['long_term_objectives'].append({
                    'objective': opportunity['opportunity'],
                    'area': area,
                    'timeline': '6-12 months'
                })
        
        return roadmap
    
    def _generate_optimization_recommendations(self, 
                                             cycle_adjusted_performance: Dict,
                                             long_term_performance: Dict,
                                             adaptation_effectiveness: Dict,
                                             performance_benchmarking: Dict) -> Dict[str, List]:
        """
        Generate optimization recommendations
        """
        
        recommendations = {
            'strategic_optimizations': [],
            'tactical_optimizations': [],
            'risk_optimizations': [],
            'performance_optimizations': []
        }
        
        # Strategic optimizations based on cycle analysis
        if 'cycle_specific_performance' in cycle_adjusted_performance:
            cycle_perf = cycle_adjusted_performance['cycle_specific_performance']
            
            # Identify underperforming cycle phases
            underperforming_cycles = []
            for cycle, metrics in cycle_perf.items():
                if metrics['average_sharpe'] < 0.5:
                    underperforming_cycles.append(cycle)
            
            if underperforming_cycles:
                recommendations['strategic_optimizations'].append({
                    'optimization': 'cycle_phase_specific_strategies',
                    'target_cycles': underperforming_cycles,
                    'description': 'Develop specialized strategies for underperforming cycle phases'
                })
        
        # Tactical optimizations based on long-term performance
        if 'portfolio_long_term_summary' in long_term_performance:
            portfolio_summary = long_term_performance['portfolio_long_term_summary']
            current_sharpe = portfolio_summary.get('portfolio_current_sharpe', 0)
            
            if current_sharpe < 1.0:
                recommendations['tactical_optimizations'].append({
                    'optimization': 'risk_return_optimization',
                    'current_sharpe': current_sharpe,
                    'target_sharpe': 1.0,
                    'methods': ['position_sizing_optimization', 'volatility_management']
                })
        
        # Risk optimizations
        if 'risk_dashboard' in performance_benchmarking.get('benchmark_comparison', {}):
            risk_comparison = performance_benchmarking['benchmark_comparison'].get('risk_comparison', {})
            risk_difference = risk_comparison.get('risk_difference', 0)
            
            if risk_difference > 0.05:
                recommendations['risk_optimizations'].append({
                    'optimization': 'risk_management_enhancement',
                    'excess_risk': risk_difference,
                    'methods': ['volatility_targeting', 'drawdown_controls']
                })
        
        # Performance optimizations
        if 'relative_performance' in performance_benchmarking:
            relative_perf = performance_benchmarking['relative_performance']
            relative_rating = relative_perf.get('relative_performance_rating', 'unknown')
            
            if relative_rating in ['underperforming', 'slightly_underperforming']:
                recommendations['performance_optimizations'].append({
                    'optimization': 'benchmark_relative_optimization',
                    'current_rating': relative_rating,
                    'target_rating': 'slightly_outperforming',
                    'methods': ['enhanced_security_selection', 'timing_optimization']
                })
        
        return recommendations
    
    def _create_performance_scorecard(self, 
                                    cycle_adjusted_performance: Dict,
                                    performance_benchmarking: Dict) -> Dict[str, Any]:
        """
        Create comprehensive performance scorecard
        """
        
        scorecard = {
            'overall_score': 0,
            'component_scores': {},
            'grade_breakdown': {},
            'score_history': []
        }
        
        # Component scores
        if 'overall_cycle_adjustment' in cycle_adjusted_performance:
            cycle_adj = cycle_adjusted_performance['overall_cycle_adjustment']
            adjustment_effectiveness = cycle_adj.get('adjustment_effectiveness', 'neutral')
            
            scorecard['component_scores']['cycle_adjustment'] = (
                90 if adjustment_effectiveness == 'positive' else
                70 if adjustment_effectiveness == 'neutral' else
                50
            )
        
        # Long-term performance score
        if 'portfolio_long_term_summary' in cycle_adjusted_performance.get('long_term_performance', {}):
            long_term = cycle_adjusted_performance['long_term_performance']['portfolio_long_term_summary']
            current_sharpe = long_term.get('portfolio_current_sharpe', 0)
            
            scorecard['component_scores']['long_term_performance'] = min(current_sharpe * 100, 100)
        
        # Benchmarking score
        if 'relative_performance' in performance_benchmarking:
            relative_perf = performance_benchmarking['relative_performance']
            relative_rating = relative_perf.get('relative_performance_rating', 'unknown')
            
            rating_scores = {
                'outperforming': 90, 'slightly_outperforming': 80,
                'in_line': 70, 'slightly_underperforming': 60, 'underperforming': 40
            }
            
            scorecard['component_scores']['benchmarking'] = rating_scores.get(relative_rating, 50)
        
        # Calculate overall score
        if scorecard['component_scores']:
            scorecard['overall_score'] = np.mean(list(scorecard['component_scores'].values()))
        
        # Grade breakdown
        scorecard['grade_breakdown'] = {
            'cycle_adjustment_grade': self._score_to_grade(scorecard['component_scores'].get('cycle_adjustment', 0)),
            'long_term_grade': self._score_to_grade(scorecard['component_scores'].get('long_term_performance', 0)),
            'benchmarking_grade': self._score_to_grade(scorecard['component_scores'].get('benchmarking', 0)),
            'overall_grade': self._score_to_grade(scorecard['overall_score'])
        }
        
        return scorecard
    
    def _score_to_grade(self, score: float) -> str:
        """
        Convert numerical score to letter grade
        """
        
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _create_optimization_summary(self, 
                                   optimization_recommendations: Dict[str, List],
                                   improvement_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create optimization summary
        """
        
        summary = {
            'key_recommendations': [],
            'optimization_priority': [],
            'expected_benefits': {},
            'implementation_timeline': {}
        }
        
        # Key recommendations
        for category, recs in optimization_recommendations.items():
            for rec in recs:
                summary['key_recommendations'].append({
                    'category': category,
                    'recommendation': rec.get('optimization', rec.get('opportunity', 'Unknown')),
                    'priority': rec.get('priority', 'medium')
                })
        
        # Optimization priority
        all_priorities = []
        for category, recs in optimization_recommendations.items():
            for rec in recs:
                priority = rec.get('priority', 'medium')
                all_priorities.append((priority, rec.get('optimization', rec.get('opportunity', ''))))
        
        # Sort by priority
        high_priority = [(p, r) for p, r in all_priorities if p == 'high']
        medium_priority = [(p, r) for p, r in all_priorities if p == 'medium']
        
        summary['optimization_priority'] = {
            'high_priority_count': len(high_priority),
            'medium_priority_count': len(medium_priority),
            'total_recommendations': len(all_priorities)
        }
        
        # Expected benefits (simplified)
        summary['expected_benefits'] = {
            'performance_improvement_potential': 'medium',
            'risk_reduction_potential': 'medium',
            'consistency_improvement_potential': 'high'
        }
        
        # Implementation timeline
        if 'improvement_roadmap' in improvement_analysis:
            roadmap = improvement_analysis['improvement_roadmap']
            
            summary['implementation_timeline'] = {
                'immediate_actions': len(roadmap.get('immediate_actions', [])),
                'short_term_goals': len(roadmap.get('short_term_goals', [])),
                'long_term_objectives': len(roadmap.get('long_term_objectives', []))
            }
        
        return summary
    
    def _update_performance_tracking(self, optimization_results: Dict[str, Any]):
        """
        Update performance tracking records
        """
        
        # Add to performance history
        tracking_record = {
            'timestamp': optimization_results['timestamp'],
            'overall_performance_score': optimization_results['performance_scorecard'].get('overall_score', 0),
            'cycle_adjustment_effectiveness': optimization_results['cycle_adjusted_performance'].get('overall_cycle_adjustment', {}).get('adjustment_effectiveness', 'unknown'),
            'benchmarking_status': optimization_results.get('performance_benchmarking', {}).get('relative_performance', {}).get('relative_performance_rating', 'unknown'),
            'optimization_recommendations_count': sum(
                len(recs) for recs in optimization_results['optimization_recommendations'].values()
            )
        }
        
        self.performance_history.append(tracking_record)
        
        # Update cycle-specific tracking
        if 'cycle_adjusted_performance' in optimization_results:
            cycle_performance = optimization_results['cycle_adjusted_performance']
            
            if 'cycle_specific_performance' in cycle_performance:
                cycle_perf = cycle_performance['cycle_specific_performance']
                
                for cycle, metrics in cycle_perf.items():
                    if cycle in self.cycle_specific_metrics:
                        self.cycle_specific_metrics[cycle]['count'] += 1
                        self.cycle_specific_metrics[cycle]['total_return'] += metrics.get('average_return', 0)
                        self.cycle_specific_metrics[cycle]['avg_sharpe'] += metrics.get('average_sharpe', 0)
    
    def get_performance_status(self) -> Dict[str, Any]:
        """
        Get current performance optimization status
        """
        
        return {
            'performance_history_count': len(self.performance_history),
            'cycle_specific_tracking': self.cycle_specific_metrics,
            'last_optimization': (
                self.performance_history[-1] 
                if self.performance_history else None
            ),
            'optimization_config': self.optimization_config,
            'performance_benchmarks': self.performance_benchmarks,
            'benchmark_data_available': self.benchmark_data is not None
        }