"""
Journal Analytics - Advanced performance analysis and reporting
Comprehensive analytics for trading journal data
"""

import json
import sqlite3
import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from trading_journal import TradingJournal, TradeEntry, PerformanceMetrics, EmotionalState, MarketCondition
from ai_feedback_loop import AIFeedbackLoop, AIInsight

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalyticsReport:
    """Analytics report ma'lumotlari"""
    report_id: str
    title: str
    period_start: datetime.datetime
    period_end: datetime.datetime
    total_trades: int
    performance_summary: Dict[str, Any]
    detailed_analysis: Dict[str, Any]
    charts_data: Dict[str, str]  # Chart paths
    recommendations: List[str]
    created_at: datetime.datetime
    report_type: str  # daily, weekly, monthly, yearly

@dataclass
class ComparativeAnalysis:
    """Taqqoslash tahlili"""
    metric_name: str
    current_value: float
    previous_value: float
    change_absolute: float
    change_percentage: float
    trend: str  # improving, declining, stable
    significance: float  # p-value

class JournalAnalytics:
    """Trading journal analytics tizimi"""
    
    def __init__(self, journal: TradingJournal):
        self.journal = journal
        self.feedback_loop = AIFeedbackLoop(journal)
        self.db_path = journal.db_path
        
    def generate_comprehensive_report(self, start_date: datetime.datetime, 
                                    end_date: datetime.datetime,
                                    report_type: str = "period") -> AnalyticsReport:
        """Keng qamrovli report yaratish"""
        
        trades = self.journal.get_trades_by_date_range(start_date, end_date)
        
        if not trades:
            return None
        
        report_id = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Asosiy metrikalar
        performance_summary = self._generate_performance_summary(trades)
        
        # Batafsil tahlil
        detailed_analysis = {
            "performance_trends": self._analyze_performance_trends(trades),
            "pattern_analysis": self._deep_pattern_analysis(trades),
            "risk_analysis": self._comprehensive_risk_analysis(trades),
            "behavioral_analysis": self._behavioral_analysis(trades),
            "market_timing_analysis": self._market_timing_analysis(trades),
            "strategy_comparison": self._strategy_comparison(trades),
            "emotional_correlation": self._emotional_correlation_analysis(trades),
            "statistical_analysis": self._statistical_analysis(trades)
        }
        
        # Charts yaratish
        charts_data = self._generate_analytics_charts(trades, report_id)
        
        # Tavsiyalar
        recommendations = self._generate_comprehensive_recommendations(trades, detailed_analysis)
        
        report = AnalyticsReport(
            report_id=report_id,
            title=f"Trading Analytics Report - {report_type.title()}",
            period_start=start_date,
            period_end=end_date,
            total_trades=len(trades),
            performance_summary=performance_summary,
            detailed_analysis=detailed_analysis,
            charts_data=charts_data,
            recommendations=recommendations,
            created_at=datetime.datetime.now(),
            report_type=report_type
        )
        
        return report
    
    def perform_comparative_analysis(self, period1_start: datetime.datetime,
                                   period1_end: datetime.datetime,
                                   period2_start: datetime.datetime,
                                   period2_end: datetime.datetime) -> Dict[str, ComparativeAnalysis]:
        """Ikki davr orasida taqqoslash tahlili"""
        
        trades1 = self.journal.get_trades_by_date_range(period1_start, period1_end)
        trades2 = self.journal.get_trades_by_date_range(period2_start, period2_end)
        
        if not trades1 or not trades2:
            return {}
        
        metrics1 = self.journal.calculate_performance_metrics(trades1)
        metrics2 = self.journal.calculate_performance_metrics(trades2)
        
        comparisons = {
            "win_rate": self._compare_metrics("Win Rate", metrics1.win_rate, metrics2.win_rate),
            "total_pnl": self._compare_metrics("Total P&L", metrics1.total_pnl, metrics2.total_pnl),
            "profit_factor": self._compare_metrics("Profit Factor", metrics1.profit_factor, metrics2.profit_factor),
            "sharpe_ratio": self._compare_metrics("Sharpe Ratio", metrics1.sharpe_ratio, metrics2.sharpe_ratio),
            "max_drawdown": self._compare_metrics("Max Drawdown", metrics1.max_drawdown, metrics2.max_drawdown),
            "total_trades": self._compare_metrics("Total Trades", metrics1.total_trades, metrics2.total_trades),
            "average_win": self._compare_metrics("Average Win", metrics1.average_win, metrics2.average_win),
            "average_loss": self._compare_metrics("Average Loss", metrics1.average_loss, metrics2.average_loss)
        }
        
        return comparisons
    
    def detect_performance_anomalies(self, trades: List[TradeEntry] = None) -> Dict[str, Any]:
        """Performance anomalylarini aniqlash"""
        if trades is None:
            trades = self.journal.get_all_trades()
        
        if len(trades) < 10:
            return {"error": "Insufficient data for anomaly detection"}
        
        anomalies = {
            "large_losses": [],
            "unusual_winning_streaks": [],
            "performance_deterioration": [],
            "risk_breaches": [],
            "emotional_patterns": []
        }
        
        # Large losses detection
        pnl_values = [t.pnl for t in trades]
        mean_pnl = np.mean(pnl_values)
        std_pnl = np.std(pnl_values)
        threshold = mean_pnl - 2 * std_pnl
        
        for trade in trades:
            if trade.pnl < threshold:
                anomalies["large_losses"].append({
                    "trade_id": trade.id,
                    "symbol": trade.symbol,
                    "pnl": trade.pnl,
                    "deviation": (trade.pnl - mean_pnl) / std_pnl,
                    "date": trade.entry_time.isoformat()
                })
        
        # Winning streaks detection
        sorted_trades = sorted(trades, key=lambda x: x.entry_time)
        current_streak = 0
        max_streak = 0
        
        for trade in sorted_trades:
            if trade.pnl > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                if current_streak >= 5:  # 5+ consecutive wins
                    anomalies["unusual_winning_streaks"].append({
                        "streak_length": current_streak,
                        "end_date": trade.entry_time.isoformat()
                    })
                current_streak = 0
        
        # Performance deterioration
        if len(trades) >= 20:
            first_half = trades[:len(trades)//2]
            second_half = trades[len(trades)//2:]
            
            first_half_pnl = np.mean([t.pnl for t in first_half])
            second_half_pnl = np.mean([t.pnl for t in second_half])
            
            if second_half_pnl < first_half_pnl * 0.7:  # 30% decline
                anomalies["performance_deterioration"].append({
                    "first_half_avg_pnl": first_half_pnl,
                    "second_half_avg_pnl": second_half_pnl,
                    "decline_percentage": ((first_half_pnl - second_half_pnl) / abs(first_half_pnl)) * 100
                })
        
        # Risk breaches
        for trade in trades:
            if trade.risk_reward_ratio < 0.5 and trade.pnl < 0:
                anomalies["risk_breaches"].append({
                    "trade_id": trade.id,
                    "risk_reward_ratio": trade.risk_reward_ratio,
                    "pnl": trade.pnl,
                    "emotional_state": trade.emotional_state.value
                })
        
        return anomalies
    
    def perform_seasonal_analysis(self, years: int = 2) -> Dict[str, Any]:
        """Mavsimiy tahlil"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=365 * years)
        
        trades = self.journal.get_trades_by_date_range(start_date, end_date)
        
        if not trades:
            return {"error": "No trades found for seasonal analysis"}
        
        # Monthly analysis
        monthly_performance = defaultdict(lambda: {"pnl": 0, "trades": 0, "wins": 0})
        # Weekly analysis
        weekly_performance = defaultdict(lambda: {"pnl": 0, "trades": 0, "wins": 0})
        # Quarterly analysis
        quarterly_performance = defaultdict(lambda: {"pnl": 0, "trades": 0, "wins": 0})
        
        for trade in trades:
            month = trade.entry_time.month
            week = trade.entry_time.isocalendar()[1]
            quarter = (trade.entry_time.month - 1) // 3 + 1
            
            monthly_performance[month]["pnl"] += trade.pnl
            monthly_performance[month]["trades"] += 1
            if trade.pnl > 0:
                monthly_performance[month]["wins"] += 1
            
            weekly_performance[week]["pnl"] += trade.pnl
            weekly_performance[week]["trades"] += 1
            if trade.pnl > 0:
                weekly_performance[week]["wins"] += 1
            
            quarterly_performance[f"Q{quarter}"]["pnl"] += trade.pnl
            quarterly_performance[f"Q{quarter}"]["trades"] += 1
            if trade.pnl > 0:
                quarterly_performance[f"Q{quarter}"]["wins"] += 1
        
        # Calculate metrics
        for data in [monthly_performance, weekly_performance, quarterly_performance]:
            for period, stats in data.items():
                if stats["trades"] > 0:
                    stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
                    stats["avg_pnl"] = stats["pnl"] / stats["trades"]
        
        return {
            "analysis_period_years": years,
            "monthly_performance": dict(monthly_performance),
            "weekly_performance": dict(weekly_performance),
            "quarterly_performance": dict(quarterly_performance),
            "best_months": self._get_top_periods(monthly_performance, 3),
            "best_weeks": self._get_top_periods(weekly_performance, 10),
            "best_quarters": self._get_top_periods(quarterly_performance, 4)
        }
    
    def clustering_analysis(self, trades: List[TradeEntry] = None, n_clusters: int = 3) -> Dict[str, Any]:
        """Trade clustering tahlili"""
        if trades is None:
            trades = self.journal.get_all_trades()
        
        if len(trades) < n_clusters:
            return {"error": "Insufficient data for clustering"}
        
        # Feature extraction
        features = []
        trade_info = []
        
        for trade in trades:
            # Numeric features
            feature_vector = [
                trade.pnl,
                trade.pnl_percentage,
                trade.confidence_level,
                trade.risk_reward_ratio,
                trade.entry_time.hour,
                trade.entry_time.weekday(),
                trade.entry_time.month
            ]
            features.append(feature_vector)
            trade_info.append({
                "id": trade.id,
                "symbol": trade.symbol,
                "strategy": trade.strategy,
                "emotional_state": trade.emotional_state.value,
                "market_condition": trade.market_condition.value
            })
        
        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(features_scaled)
        
        # Analyze clusters
        clusters = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            clusters[f"Cluster_{label}"].append(trade_info[i])
        
        # Cluster characteristics
        cluster_analysis = {}
        for i, (cluster_name, trades_in_cluster) in enumerate(clusters.items()):
            cluster_features = features_scaled[cluster_labels == i]
            cluster_analysis[cluster_name] = {
                "size": len(trades_in_cluster),
                "characteristics": {
                    "avg_pnl": np.mean([trade.pnl for j, trade in enumerate(trades) if cluster_labels[j] == i]),
                    "avg_confidence": np.mean([trade.confidence_level for j, trade in enumerate(trades) if cluster_labels[j] == i]),
                    "dominant_emotion": Counter([trade["emotional_state"] for trade in trades_in_cluster]).most_common(1)[0][0],
                    "dominant_strategy": Counter([trade["strategy"] for trade in trades_in_cluster]).most_common(1)[0][0],
                    "dominant_symbol": Counter([trade["symbol"] for trade in trades_in_cluster]).most_common(1)[0][0]
                }
            }
        
        return {
            "n_clusters": n_clusters,
            "cluster_analysis": cluster_analysis,
            "trades_by_cluster": {k: len(v) for k, v in clusters.items()},
            "cluster_centers": kmeans.cluster_centers_.tolist()
        }
    
    def generate_visual_dashboard(self, trades: List[TradeEntry] = None) -> Dict[str, str]:
        """Visual dashboard yaratish"""
        if trades is None:
            trades = self.journal.get_all_trades()
        
        if not trades:
            return {"error": "No trades found for visualization"}
        
        chart_paths = {}
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # 1. P&L over time
            plt.figure(figsize=(12, 6))
            dates = [t.entry_time for t in sorted(trades, key=lambda x: x.entry_time)]
            pnls = [t.pnl for t in sorted(trades, key=lambda x: x.entry_time)]
            cumulative_pnl = np.cumsum(pnls)
            
            plt.plot(dates, cumulative_pnl, linewidth=2, color='blue')
            plt.title('Cumulative P&L Over Time')
            plt.xlabel('Date')
            plt.ylabel('Cumulative P&L ($)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            chart_paths["cumulative_pnl"] = f"charts/cumulative_pnl_{timestamp}.png"
            plt.savefig(chart_paths["cumulative_pnl"], dpi=300, bbox_inches='tight')
            plt.close()
            
            # 2. Win rate by strategy
            strategy_stats = self.feedback_loop._analyze_strategy_patterns(trades)
            if strategy_stats:
                strategies = list(strategy_stats.keys())
                win_rates = [strategy_stats[s]["win_rate"] for s in strategies]
                
                plt.figure(figsize=(10, 6))
                bars = plt.bar(strategies, win_rates, color='skyblue', edgecolor='navy')
                plt.title('Win Rate by Strategy')
                plt.xlabel('Strategy')
                plt.ylabel('Win Rate (%)')
                plt.xticks(rotation=45)
                
                # Add value labels on bars
                for bar, rate in zip(bars, win_rates):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                            f'{rate:.1f}%', ha='center', va='bottom')
                
                plt.tight_layout()
                chart_paths["win_rate_by_strategy"] = f"charts/win_rate_strategy_{timestamp}.png"
                plt.savefig(chart_paths["win_rate_by_strategy"], dpi=300, bbox_inches='tight')
                plt.close()
            
            # 3. Emotional state performance
            emotional_stats = self.feedback_loop._analyze_emotional_performance(trades)
            if emotional_stats:
                emotions = list(emotional_stats.keys())
                avg_pnls = [emotional_stats[e]["avg_pnl"] for e in emotions]
                
                plt.figure(figsize=(10, 6))
                colors = ['green' if pnl > 0 else 'red' for pnl in avg_pnls]
                bars = plt.bar(emotions, avg_pnls, color=colors, alpha=0.7)
                plt.title('Average P&L by Emotional State')
                plt.xlabel('Emotional State')
                plt.ylabel('Average P&L ($)')
                plt.xticks(rotation=45)
                
                # Add value labels
                for bar, pnl in zip(bars, avg_pnls):
                    plt.text(bar.get_x() + bar.get_width()/2, 
                            bar.get_height() + (1 if pnl > 0 else -3), 
                            f'{pnl:.1f}', ha='center', va='bottom' if pnl > 0 else 'top')
                
                plt.tight_layout()
                chart_paths["emotional_performance"] = f"charts/emotional_perf_{timestamp}.png"
                plt.savefig(chart_paths["emotional_performance"], dpi=300, bbox_inches='tight')
                plt.close()
            
            # 4. Risk-Reward distribution
            risk_rewards = [t.risk_reward_ratio for t in trades]
            plt.figure(figsize=(10, 6))
            plt.hist(risk_rewards, bins=20, color='lightblue', edgecolor='black', alpha=0.7)
            plt.title('Risk-Reward Ratio Distribution')
            plt.xlabel('Risk-Reward Ratio')
            plt.ylabel('Frequency')
            plt.axvline(np.mean(risk_rewards), color='red', linestyle='--', label=f'Mean: {np.mean(risk_rewards):.2f}')
            plt.legend()
            plt.tight_layout()
            chart_paths["risk_reward_distribution"] = f"charts/risk_reward_{timestamp}.png"
            plt.savefig(chart_paths["risk_reward_distribution"], dpi=300, bbox_inches='tight')
            plt.close()
            
            # 5. Performance by time of day
            hourly_perf = defaultdict(lambda: {"pnl": 0, "trades": 0})
            for trade in trades:
                hour = trade.entry_time.hour
                hourly_perf[hour]["pnl"] += trade.pnl
                hourly_perf[hour]["trades"] += 1
            
            hours = list(range(24))
            avg_pnls = [hourly_perf[h]["pnl"]/hourly_perf[h]["trades"] if hourly_perf[h]["trades"] > 0 else 0 for h in hours]
            
            plt.figure(figsize=(12, 6))
            plt.bar(hours, avg_pnls, color='orange', alpha=0.7)
            plt.title('Average P&L by Hour of Day')
            plt.xlabel('Hour of Day')
            plt.ylabel('Average P&L ($)')
            plt.xticks(range(0, 24, 2))
            plt.tight_layout()
            chart_paths["hourly_performance"] = f"charts/hourly_perf_{timestamp}.png"
            plt.savefig(chart_paths["hourly_performance"], dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
        
        return chart_paths
    
    def predict_future_performance(self, trades: List[TradeEntry] = None) -> Dict[str, Any]:
        """Kelgusi performance ni bashorat qilish"""
        if trades is None:
            trades = self.journal.get_all_trades()
        
        if len(trades) < 20:
            return {"error": "Insufficient data for prediction"}
        
        # Recent performance trend
        recent_trades = sorted(trades, key=lambda x: x.entry_time)[-20:]
        recent_pnls = [t.pnl for t in recent_trades]
        
        # Simple linear trend
        if len(recent_pnls) >= 2:
            x = np.arange(len(recent_pnls))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, recent_pnls)
            
            # Next 5 trades prediction
            next_x = np.arange(len(recent_pnls), len(recent_pnls) + 5)
            predicted_pnls = slope * next_x + intercept
            
            # Confidence intervals
            prediction_std = std_err * np.sqrt(1 + 1/len(recent_pnls))
            confidence_interval = 1.96 * prediction_std  # 95% confidence
            
        else:
            slope = 0
            predicted_pnls = [np.mean(recent_pnls)] * 5
            confidence_interval = np.std(recent_pnls)
        
        # Performance indicators
        current_win_rate = len([t for t in recent_trades if t.pnl > 0]) / len(recent_trades) * 100
        avg_recent_pnl = np.mean(recent_pnls)
        volatility = np.std(recent_pnls)
        
        # Trend assessment
        if slope > 5:
            trend = "improving"
        elif slope < -5:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "predicted_next_5_pnls": predicted_pnls.tolist(),
            "trend_slope": slope,
            "trend_direction": trend,
            "confidence_interval": confidence_interval,
            "r_squared": r_value**2 if len(recent_pnls) >= 2 else 0,
            "current_performance": {
                "recent_win_rate": current_win_rate,
                "avg_recent_pnl": avg_recent_pnl,
                "volatility": volatility
            },
            "recommendations": self._generate_prediction_recommendations(slope, trend, current_win_rate)
        }
    
    def _generate_performance_summary(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Performance summary yaratish"""
        metrics = self.journal.calculate_performance_metrics(trades)
        
        return {
            "total_trades": metrics.total_trades,
            "win_rate": f"{metrics.win_rate:.1f}%",
            "total_pnl": f"${metrics.total_pnl:.2f}",
            "profit_factor": f"{metrics.profit_factor:.2f}",
            "sharpe_ratio": f"{metrics.sharpe_ratio:.2f}",
            "max_drawdown": f"${metrics.max_drawdown:.2f}",
            "largest_win": f"${metrics.largest_win:.2f}",
            "largest_loss": f"${metrics.largest_loss:.2f}",
            "avg_win": f"${metrics.average_win:.2f}",
            "avg_loss": f"${metrics.average_loss:.2f}"
        }
    
    def _analyze_performance_trends(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Performance trendlari tahlili"""
        sorted_trades = sorted(trades, key=lambda x: x.entry_time)
        
        # Rolling metrics
        window_size = min(10, len(sorted_trades) // 3)
        if window_size < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        rolling_metrics = []
        for i in range(window_size, len(sorted_trades) + 1):
            window_trades = sorted_trades[i-window_size:i]
            metrics = self.journal.calculate_performance_metrics(window_trades)
            rolling_metrics.append({
                "period_end": window_trades[-1].entry_time,
                "win_rate": metrics.win_rate,
                "total_pnl": metrics.total_pnl,
                "profit_factor": metrics.profit_factor
            })
        
        return {
            "rolling_metrics": rolling_metrics,
            "trend_direction": "improving" if len(rolling_metrics) > 1 and 
                             rolling_metrics[-1]["win_rate"] > rolling_metrics[0]["win_rate"] else "declining"
        }
    
    def _deep_pattern_analysis(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Chuqur pattern tahlili"""
        return {
            "emotional_patterns": self.feedback_loop._analyze_emotional_bias(trades),
            "temporal_patterns": self.feedback_loop._analyze_time_patterns(trades),
            "strategy_patterns": self.feedback_loop._analyze_strategy_patterns(trades),
            "market_condition_patterns": self.feedback_loop._analyze_market_condition_patterns(trades)
        }
    
    def _comprehensive_risk_analysis(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Keng qamrovli risk tahlili"""
        risk_metrics = {
            "avg_risk_reward": np.mean([t.risk_reward_ratio for t in trades]),
            "risk_adjusted_return": self._calculate_risk_adjusted_return(trades),
            "var_95": self._calculate_value_at_risk(trades, 0.05),
            "max_consecutive_losses": self._calculate_max_consecutive_losses(trades),
            "recovery_factor": self._calculate_recovery_factor(trades)
        }
        
        return risk_metrics
    
    def _behavioral_analysis(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Xulq-atvor tahlili"""
        return {
            "confidence_vs_performance": self._analyze_confidence_performance_correlation(trades),
            "emotional_stability": self._analyze_emotional_stability(trades),
            "decision_consistency": self._analyze_decision_consistency(trades)
        }
    
    def _market_timing_analysis(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Market timing tahlili"""
        return self.feedback_loop.analyze_market_timing(trades)
    
    def _strategy_comparison(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Strategy taqqoslash"""
        strategy_performance = self.feedback_loop._analyze_strategy_patterns(trades)
        
        # Strategy ranking
        ranked_strategies = sorted(strategy_performance.items(), 
                                 key=lambda x: x[1]["avg_pnl"], reverse=True)
        
        return {
            "strategy_rankings": [{"strategy": s, "avg_pnl": data["avg_pnl"], "win_rate": data["win_rate"]} 
                                for s, data in ranked_strategies],
            "best_strategy": ranked_strategies[0] if ranked_strategies else None,
            "strategy_diversity": len(strategy_performance)
        }
    
    def _emotional_correlation_analysis(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Emotsional korelyatsiya tahlili"""
        emotional_performance = self.feedback_loop._analyze_emotional_performance(trades)
        
        # Correlation between emotional states and performance
        correlations = {}
        for emotion, stats in emotional_performance.items():
            if stats["trades"] > 0:
                correlations[emotion] = {
                    "win_rate": stats["win_rate"],
                    "avg_pnl": stats["avg_pnl"],
                    "consistency": 1 - (abs(stats["avg_pnl"]) / (abs(stats["avg_pnl"]) + 100))  # Simplified consistency score
                }
        
        return correlations
    
    def _statistical_analysis(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Statistik tahlil"""
        pnl_values = [t.pnl for t in trades]
        
        return {
            "mean": np.mean(pnl_values),
            "median": np.median(pnl_values),
            "std": np.std(pnl_values),
            "skewness": stats.skew(pnl_values),
            "kurtosis": stats.kurtosis(pnl_values),
            "sharpe_ratio": np.mean(pnl_values) / np.std(pnl_values) if np.std(pnl_values) > 0 else 0,
            "percentile_95": np.percentile(pnl_values, 95),
            "percentile_5": np.percentile(pnl_values, 5)
        }
    
    def _generate_analytics_charts(self, trades: List[TradeEntry], report_id: str) -> Dict[str, str]:
        """Analytics charts yaratish"""
        return self.generate_visual_dashboard(trades)
    
    def _generate_comprehensive_recommendations(self, trades: List[TradeEntry], 
                                              analysis: Dict[str, Any]) -> List[str]:
        """Keng qamrovli tavsiyalar"""
        recommendations = []
        
        # Performance based recommendations
        if "performance_trends" in analysis:
            trend_data = analysis["performance_trends"]
            if "trend_direction" in trend_data and trend_data["trend_direction"] == "declining":
                recommendations.append("Performance pasaymoqda - strategy qayta ko'rib chiqish kerak")
        
        # Risk based recommendations
        if "risk_analysis" in analysis:
            risk_data = analysis["risk_analysis"]
            if risk_data.get("avg_risk_reward", 0) < 1.5:
                recommendations.append("Risk-reward ratio yaxshilash kerak - kamida 1:2")
        
        # Strategy based recommendations
        if "strategy_comparison" in analysis:
            strategy_data = analysis["strategy_comparison"]
            if strategy_data.get("strategy_diversity", 0) > 3:
                recommendations.append("Ko'p strategy ishlatilayapti - eng yaxshisini tanlash kerak")
        
        return recommendations
    
    def _compare_metrics(self, name: str, current: float, previous: float) -> ComparativeAnalysis:
        """Metrikalarni taqqoslash"""
        change_absolute = current - previous
        change_percentage = (change_absolute / abs(previous)) * 100 if previous != 0 else 0
        
        if change_percentage > 5:
            trend = "improving"
        elif change_percentage < -5:
            trend = "declining"
        else:
            trend = "stable"
        
        return ComparativeAnalysis(
            metric_name=name,
            current_value=current,
            previous_value=previous,
            change_absolute=change_absolute,
            change_percentage=change_percentage,
            trend=trend,
            significance=0.5  # Placeholder - would need statistical test
        )
    
    def _get_top_periods(self, performance_dict: Dict, n: int) -> List[Dict]:
        """Eng yaxshi davrlarni olish"""
        sorted_periods = sorted(performance_dict.items(), 
                              key=lambda x: x[1]["avg_pnl"] if x[1]["trades"] > 0 else -999, 
                              reverse=True)
        
        return [{"period": period, **data} for period, data in sorted_periods[:n] if data["trades"] > 0]
    
    def _calculate_risk_adjusted_return(self, trades: List[TradeEntry]) -> float:
        """Risk-adjusted return hisoblash"""
        if not trades:
            return 0.0
        
        total_return = sum(t.pnl for t in trades)
        volatility = np.std([t.pnl for t in trades])
        
        return total_return / volatility if volatility > 0 else 0
    
    def _calculate_value_at_risk(self, trades: List[TradeEntry], confidence: float) -> float:
        """Value at Risk hisoblash"""
        if not trades:
            return 0.0
        
        pnl_values = [t.pnl for t in trades]
        return np.percentile(pnl_values, confidence * 100)
    
    def _calculate_max_consecutive_losses(self, trades: List[TradeEntry]) -> int:
        """Maksimal ketma-ket yo'qotishlar soni"""
        if not trades:
            return 0
        
        sorted_trades = sorted(trades, key=lambda x: x.entry_time)
        max_consecutive = 0
        current_consecutive = 0
        
        for trade in sorted_trades:
            if trade.pnl < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_recovery_factor(self, trades: List[TradeEntry]) -> float:
        """Recovery factor hisoblash"""
        if not trades:
            return 0.0
        
        metrics = self.journal.calculate_performance_metrics(trades)
        return metrics.total_pnl / metrics.max_drawdown if metrics.max_drawdown > 0 else 0
    
    def _analyze_confidence_performance_correlation(self, trades: List[TradeEntry]) -> Dict[str, float]:
        """Ishonch va performance korelyatsiyasi"""
        if len(trades) < 2:
            return {"correlation": 0, "insights": []}
        
        confidence_levels = [t.confidence_level for t in trades]
        pnl_values = [t.pnl for t in trades]
        
        correlation = np.corrcoef(confidence_levels, pnl_values)[0, 1]
        
        return {
            "correlation": correlation,
            "insights": [
                "Ishonch darajasi performance ga ta'sir qiladi" if abs(correlation) > 0.3 else 
                "Ishonch darajasi performance ga sezilarli ta'sir qilmaydi"
            ]
        }
    
    def _analyze_emotional_stability(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Emotsional barqarorlik tahlili"""
        if not trades:
            return {"stability_score": 0, "variety": 0}
        
        emotional_states = [t.emotional_state.value for t in trades]
        emotional_variety = len(set(emotional_states))
        emotional_consistency = 1 - (emotional_variety / len(emotional_states))
        
        return {
            "stability_score": emotional_consistency * 100,
            "variety": emotional_variety,
            "dominant_emotion": Counter(emotional_states).most_common(1)[0][0] if emotional_states else None
        }
    
    def _analyze_decision_consistency(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Qaror qabul qilish barqarorligi"""
        if not trades:
            return {"consistency_score": 0}
        
        # Strategy consistency
        strategies = [t.strategy for t in trades]
        strategy_consistency = len(set(strategies)) / len(strategies)
        
        # Risk management consistency
        risk_rewards = [t.risk_reward_ratio for t in trades]
        risk_consistency = 1 - (np.std(risk_rewards) / np.mean(risk_rewards)) if np.mean(risk_rewards) > 0 else 0
        
        return {
            "strategy_consistency": strategy_consistency,
            "risk_consistency": max(0, risk_consistency),
            "overall_consistency": (strategy_consistency + max(0, risk_consistency)) / 2
        }
    
    def _generate_prediction_recommendations(self, slope: float, trend: str, win_rate: float) -> List[str]:
        """Bashorat tavsiyalari"""
        recommendations = []
        
        if trend == "improving":
            recommendations.append("Performance yaxshilanayapti - hozirgi strategiyani davom ettiring")
        elif trend == "declining":
            recommendations.append("Performance pasaymoqda - strategy o'zgartirish kerak")
        
        if win_rate < 50:
            recommendations.append("Win rate past - risk management qoidalarini qayta ko'rib chiqish")
        elif win_rate > 70:
            recommendations.append("Yuqori win rate - position size ni oshirish mumkin")
        
        return recommendations