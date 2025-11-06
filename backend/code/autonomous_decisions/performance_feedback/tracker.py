"""
Strategy Performance Tracker

Individual strategy performance tracking va monitoring
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import numpy as np

@dataclass
class StrategyPerformance:
    """Individual strategy performance"""
    strategy_name: str
    timestamp: datetime
    return_value: float
    cumulative_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trades_count: int
    avg_trade_return: float
    profit_factor: float

@dataclass
class StrategyMetrics:
    """Strategy metrics summary"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    average_trade: float
    best_trade: float
    worst_trade: float
    avg_winning_trade: float
    avg_losing_trade: float

class StrategyTracker:
    """
    Strategy Performance Tracking
    
    - Individual strategy monitoring
    - Performance comparison
    - Strategy ranking
    - Performance correlation analysis
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Strategy definitions
        self.strategies = {
            "momentum": self._track_momentum_strategy,
            "mean_reversion": self._track_mean_reversion_strategy,
            "trend_following": self._track_trend_following_strategy,
            "arbitrage": self._track_arbitrage_strategy,
            "market_making": self._track_market_making_strategy
        }
        
        # Performance storage
        self.strategy_performance = defaultdict(lambda: deque(maxlen=1000))
        self.strategy_trades = defaultdict(list)
        
        # Tracking parameters
        self.update_interval = config.get("strategy_update_interval", 300)  # 5 minutes
        self.max_history = config.get("max_strategy_history", 10000)
        
        # Performance benchmarks
        self.benchmarks = {
            "market_return": 0.08,  # 8% annual
            "risk_free": 0.02,      # 2% risk-free rate
            "target_sharpe": 1.5,   # Target Sharpe ratio
            "target_return": 0.15   # 15% annual target
        }
        
        # Risk thresholds
        self.risk_thresholds = {
            "max_drawdown": 0.10,     # 10% max drawdown
            "min_sharpe": 0.5,        # Minimum Sharpe ratio
            "min_win_rate": 0.40,     # 40% minimum win rate
            "min_trades": 10          # Minimum trades for evaluation
        }
    
    def start_tracking(self, strategy_name: str):
        """Strategy tracking ni boshlash"""
        if strategy_name not in self.strategies:
            raise ValueError(f"Noma'lum strategy: {strategy_name}")
        
        self.logger.info(f"Strategy tracking started: {strategy_name}")
    
    def stop_tracking(self, strategy_name: str):
        """Strategy tracking ni to'xtatish"""
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
        self.logger.info(f"Strategy tracking stopped: {strategy_name}")
    
    async def track_performance(self, strategy_name: str, performance_data: Dict):
        """Strategy performance tracking"""
        try:
            if strategy_name not in self.strategies:
                return
            
            # Performance data processing
            strategy_perf = await self._process_strategy_performance(strategy_name, performance_data)
            
            # Store performance data
            self.strategy_performance[strategy_name].append(strategy_perf)
            
            # Update trades data
            if "trades" in performance_data:
                self.strategy_trades[strategy_name].extend(performance_data["trades"])
            
            # Generate alerts if needed
            await self._check_performance_alerts(strategy_name, strategy_perf)
            
        except Exception as e:
            self.logger.error(f"Strategy performance tracking xatosi ({strategy_name}): {str(e)}")
    
    async def _process_strategy_performance(self, strategy_name: str, 
                                          performance_data: Dict) -> StrategyPerformance:
        """Strategy performance data processing"""
        # Calculate strategy metrics
        current_return = performance_data.get("return", 0.0)
        cumulative_return = self._calculate_cumulative_return(strategy_name, current_return)
        
        # Get strategy trades
        trades = performance_data.get("trades", [])
        trade_count = len(trades)
        win_rate = self._calculate_win_rate(trades)
        avg_trade_return = self._calculate_avg_trade_return(trades)
        profit_factor = self._calculate_profit_factor(trades)
        
        # Calculate risk metrics
        volatility = self._calculate_strategy_volatility(strategy_name)
        sharpe_ratio = self._calculate_sharpe_ratio(strategy_name)
        max_drawdown = self._calculate_strategy_drawdown(strategy_name)
        
        return StrategyPerformance(
            strategy_name=strategy_name,
            timestamp=datetime.now(),
            return_value=current_return,
            cumulative_return=cumulative_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            trades_count=trade_count,
            avg_trade_return=avg_trade_return,
            profit_factor=profit_factor
        )
    
    def _calculate_cumulative_return(self, strategy_name: str, current_return: float) -> float:
        """Cumulative return hisoblash"""
        if not self.strategy_performance[strategy_name]:
            return current_return
        
        last_perf = self.strategy_performance[strategy_name][-1]
        return last_perf.cumulative_return + current_return
    
    def _calculate_win_rate(self, trades: List[Dict]) -> float:
        """Win rate hisoblash"""
        if not trades:
            return 0.0
        
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        return len(winning_trades) / len(trades)
    
    def _calculate_avg_trade_return(self, trades: List[Dict]) -> float:
        """Average trade return hisoblash"""
        if not trades:
            return 0.0
        
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        return total_pnl / len(trades)
    
    def _calculate_profit_factor(self, trades: List[Dict]) -> float:
        """Profit factor hisoblash"""
        if not trades:
            return 0.0
        
        gross_profit = sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) > 0)
        gross_loss = abs(sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) < 0))
        
        return gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    def _calculate_strategy_volatility(self, strategy_name: str) -> float:
        """Strategy volatility hisoblash"""
        performance_history = list(self.strategy_performance[strategy_name])
        
        if len(performance_history) < 2:
            return 0.0
        
        returns = [perf.return_value for perf in performance_history[-50:]]  # Last 50 points
        return np.std(returns) * np.sqrt(252)  # Annualized volatility
    
    def _calculate_sharpe_ratio(self, strategy_name: str) -> float:
        """Sharpe ratio hisoblash"""
        performance_history = list(self.strategy_performance[strategy_name])
        
        if len(performance_history) < 2:
            return 0.0
        
        returns = [perf.return_value for perf in performance_history[-50:]]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        excess_return = avg_return - (self.benchmarks["risk_free"] / 252)
        return excess_return / std_return * np.sqrt(252)
    
    def _calculate_strategy_drawdown(self, strategy_name: str) -> float:
        """Strategy drawdown hisoblash"""
        performance_history = list(self.strategy_performance[strategy_name])
        
        if not performance_history:
            return 0.0
        
        # Track peak and current values
        peak = 0.0
        max_drawdown = 0.0
        
        cumulative_returns = [perf.cumulative_return for perf in performance_history]
        for ret in cumulative_returns:
            peak = max(peak, ret)
            drawdown = (peak - ret) / (1 + peak) if peak != -1 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    async def _check_performance_alerts(self, strategy_name: str, 
                                      performance: StrategyPerformance):
        """Performance alerts check"""
        alerts = []
        
        # Drawdown alert
        if performance.max_drawdown > self.risk_thresholds["max_drawdown"]:
            alerts.append(f"CRITICAL: {strategy_name} drawdown {performance.max_drawdown:.2%}")
        
        # Sharpe ratio alert
        if performance.sharpe_ratio < self.risk_thresholds["min_sharpe"]:
            alerts.append(f"WARNING: {strategy_name} Sharpe ratio {performance.sharpe_ratio:.2f}")
        
        # Win rate alert
        if (performance.trades_count >= self.risk_thresholds["min_trades"] and 
            performance.win_rate < self.risk_thresholds["min_win_rate"]):
            alerts.append(f"WARNING: {strategy_name} win rate {performance.win_rate:.2%}")
        
        # High volatility alert
        if performance.volatility > 0.25:  # 25% annual volatility threshold
            alerts.append(f"INFO: {strategy_name} high volatility {performance.volatility:.2%}")
        
        # Alert logging
        for alert in alerts:
            if "CRITICAL" in alert:
                self.logger.critical(alert)
            elif "WARNING" in alert:
                self.logger.warning(alert)
            else:
                self.logger.info(alert)
    
    def get_strategy_performance(self, strategy_name: str, 
                               days: int = 30) -> Optional[Dict[str, Any]]:
        """Strategy performance olish"""
        if strategy_name not in self.strategy_performance:
            return None
        
        cutoff_time = datetime.now() - timedelta(days=days)
        performance_history = [
            perf for perf in self.strategy_performance[strategy_name]
            if perf.timestamp >= cutoff_time
        ]
        
        if not performance_history:
            return {"message": "Performance data not available"}
        
        # Calculate summary metrics
        latest = performance_history[-1]
        metrics = StrategyMetrics(
            total_return=latest.cumulative_return,
            annualized_return=latest.cumulative_return * (365 / days) if days > 0 else 0,
            volatility=latest.volatility,
            sharpe_ratio=latest.sharpe_ratio,
            sortino_ratio=self._calculate_sortino_ratio(performance_history),
            max_drawdown=latest.max_drawdown,
            calmar_ratio=latest.cumulative_return / latest.max_drawdown if latest.max_drawdown > 0 else 0,
            win_rate=latest.win_rate,
            profit_factor=latest.profit_factor,
            average_trade=latest.avg_trade_return,
            best_trade=self._calculate_best_trade(strategy_name),
            worst_trade=self._calculate_worst_trade(strategy_name),
            avg_winning_trade=self._calculate_avg_winning_trade(strategy_name),
            avg_losing_trade=self._calculate_avg_losing_trade(strategy_name)
        )
        
        return {
            "strategy_name": strategy_name,
            "time_period_days": days,
            "metrics": asdict(metrics),
            "recent_performance": [
                asdict(perf) for perf in performance_history[-10:]  # Last 10 records
            ],
            "trade_statistics": self._get_trade_statistics(strategy_name)
        }
    
    def _calculate_sortino_ratio(self, performance_history: List[StrategyPerformance]) -> float:
        """Sortino ratio hisoblash"""
        if len(performance_history) < 2:
            return 0.0
        
        returns = [perf.return_value for perf in performance_history]
        avg_return = np.mean(returns)
        
        # Downside deviation
        downside_returns = [r for r in returns if r < 0]
        if not downside_returns:
            return float('inf')
        
        downside_std = np.std(downside_returns)
        excess_return = avg_return - (self.benchmarks["risk_free"] / 252)
        
        return excess_return / downside_std * np.sqrt(252) if downside_std > 0 else 0
    
    def _calculate_best_trade(self, strategy_name: str) -> float:
        """Best trade return"""
        trades = self.strategy_trades[strategy_name]
        if not trades:
            return 0.0
        
        return max(t.get("pnl", 0) for t in trades)
    
    def _calculate_worst_trade(self, strategy_name: str) -> float:
        """Worst trade return"""
        trades = self.strategy_trades[strategy_name]
        if not trades:
            return 0.0
        
        return min(t.get("pnl", 0) for t in trades)
    
    def _calculate_avg_winning_trade(self, strategy_name: str) -> float:
        """Average winning trade"""
        trades = self.strategy_trades[strategy_name]
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        
        if not winning_trades:
            return 0.0
        
        return np.mean([t.get("pnl", 0) for t in winning_trades])
    
    def _calculate_avg_losing_trade(self, strategy_name: str) -> float:
        """Average losing trade"""
        trades = self.strategy_trades[strategy_name]
        losing_trades = [t for t in trades if t.get("pnl", 0) < 0]
        
        if not losing_trades:
            return 0.0
        
        return np.mean([t.get("pnl", 0) for t in losing_trades])
    
    def _get_trade_statistics(self, strategy_name: str) -> Dict[str, Any]:
        """Trade statistics"""
        trades = self.strategy_trades[strategy_name]
        
        if not trades:
            return {"message": "No trades available"}
        
        pnl_values = [t.get("pnl", 0) for t in trades]
        
        return {
            "total_trades": len(trades),
            "winning_trades": len([p for p in pnl_values if p > 0]),
            "losing_trades": len([p for p in pnl_values if p < 0]),
            "breakeven_trades": len([p for p in pnl_values if p == 0]),
            "total_pnl": sum(pnl_values),
            "largest_win": max(pnl_values),
            "largest_loss": min(pnl_values),
            "average_win": np.mean([p for p in pnl_values if p > 0]) if any(p > 0 for p in pnl_values) else 0,
            "average_loss": np.mean([p for p in pnl_values if p < 0]) if any(p < 0 for p in pnl_values) else 0,
            "avg_trade_duration": self._calculate_avg_trade_duration(trades)
        }
    
    def _calculate_avg_trade_duration(self, trades: List[Dict]) -> float:
        """Average trade duration"""
        # Simplified calculation
        durations = []
        for trade in trades:
            entry_time = trade.get("entry_time")
            exit_time = trade.get("exit_time")
            if entry_time and exit_time:
                duration = (exit_time - entry_time).total_seconds() / 3600  # hours
                durations.append(duration)
        
        return np.mean(durations) if durations else 0.0
    
    def compare_strategies(self, strategy_names: List[str], days: int = 30) -> Dict[str, Any]:
        """Strategy comparison"""
        comparison_data = {}
        
        for strategy_name in strategy_names:
            perf_data = self.get_strategy_performance(strategy_name, days)
            if perf_data and "metrics" in perf_data:
                comparison_data[strategy_name] = perf_data["metrics"]
        
        if not comparison_data:
            return {"message": "No comparison data available"}
        
        # Calculate rankings
        rankings = self._rank_strategies(comparison_data)
        
        # Calculate correlations
        correlations = self._calculate_strategy_correlations(strategy_names)
        
        # Portfolio diversification analysis
        diversification = self._analyze_diversification(comparison_data)
        
        return {
            "comparison_period_days": days,
            "strategy_metrics": comparison_data,
            "rankings": rankings,
            "correlations": correlations,
            "diversification_analysis": diversification,
            "recommendations": self._generate_comparison_recommendations(comparison_data, rankings)
        }
    
    def _rank_strategies(self, strategy_metrics: Dict) -> List[Dict]:
        """Strategy ranking"""
        # Multi-criteria ranking
        rankings = []
        
        for strategy_name, metrics in strategy_metrics.items():
            # Composite score calculation
            return_score = min(metrics.get("total_return", 0) / 0.2, 1.0) * 0.3  # Return weight
            sharpe_score = min(metrics.get("sharpe_ratio", 0) / 2.0, 1.0) * 0.25  # Sharpe weight
            drawdown_score = max(0, 1 - metrics.get("max_drawdown", 0) / 0.15) * 0.2  # Drawdown weight
            win_rate_score = metrics.get("win_rate", 0) * 0.15  # Win rate weight
            profit_factor_score = min(metrics.get("profit_factor", 0) / 2.0, 1.0) * 0.1  # Profit factor weight
            
            composite_score = return_score + sharpe_score + drawdown_score + win_rate_score + profit_factor_score
            
            rankings.append({
                "strategy": strategy_name,
                "composite_score": composite_score,
                "return_score": return_score,
                "risk_score": drawdown_score,
                "efficiency_score": sharpe_score,
                "consistency_score": win_rate_score
            })
        
        # Sort by composite score
        rankings.sort(key=lambda x: x["composite_score"], reverse=True)
        return rankings
    
    def _calculate_strategy_correlations(self, strategy_names: List[str]) -> Dict[str, Dict[str, float]]:
        """Strategy correlation calculation"""
        correlations = {}
        
        # Get returns for each strategy
        strategy_returns = {}
        for strategy_name in strategy_names:
            if strategy_name in self.strategy_performance:
                returns = [perf.return_value for perf in list(self.strategy_performance[strategy_name])[-50:]]
                if len(returns) > 1:
                    strategy_returns[strategy_name] = returns
        
        # Calculate pairwise correlations
        strategies = list(strategy_returns.keys())
        for i, strategy1 in enumerate(strategies):
            correlations[strategy1] = {}
            for j, strategy2 in enumerate(strategies):
                if i != j and strategy2 in strategy_returns[strategy1]:
                    correlation = np.corrcoef(
                        strategy_returns[strategy1], 
                        strategy_returns[strategy2]
                    )[0, 1]
                    correlations[strategy1][strategy2] = correlation
        
        return correlations
    
    def _analyze_diversification(self, strategy_metrics: Dict) -> Dict[str, Any]:
        """Portfolio diversification analysis"""
        # Calculate average correlation
        correlations = self._calculate_strategy_correlations(list(strategy_metrics.keys()))
        
        if not correlations:
            return {"diversification_ratio": 0.0}
        
        # Calculate average absolute correlation
        total_correlation = 0
        correlation_count = 0
        
        for strategy1, other_correlations in correlations.items():
            for correlation in other_correlations.values():
                if not np.isnan(correlation):
                    total_correlation += abs(correlation)
                    correlation_count += 1
        
        avg_correlation = total_correlation / correlation_count if correlation_count > 0 else 0
        
        # Diversification ratio (1 - avg_correlation)
        diversification_ratio = 1 - avg_correlation
        
        return {
            "diversification_ratio": diversification_ratio,
            "average_correlation": avg_correlation,
            "correlation_matrix": correlations,
            "diversification_quality": "high" if diversification_ratio > 0.7 else 
                                     "medium" if diversification_ratio > 0.4 else "low"
        }
    
    def _generate_comparison_recommendations(self, strategy_metrics: Dict, 
                                           rankings: List[Dict]) -> List[str]:
        """Comparison-based recommendations"""
        recommendations = []
        
        if not rankings:
            return ["Ma'lumot yetarli emas"]
        
        best_strategy = rankings[0]["strategy"]
        worst_strategy = rankings[-1]["strategy"]
        
        # Performance recommendations
        best_metrics = strategy_metrics[best_strategy]
        worst_metrics = strategy_metrics[worst_strategy]
        
        if best_metrics.get("total_return", 0) > 0.1:
            recommendations.append(f"{best_strategy} strategiyasi yuqori return ko'rsatyapti")
        
        if worst_metrics.get("max_drawdown", 0) > 0.15:
            recommendations.append(f"{worst_strategy} strategiyasi yuqori risk bor")
        
        # Diversification recommendations
        if len(rankings) > 1:
            recommendations.append("Ko'p strategiya diversifikatsiyani yaxshilaydi")
        
        # Risk management recommendations
        high_risk_strategies = [
            s for s, m in strategy_metrics.items() 
            if m.get("max_drawdown", 0) > 0.1
        ]
        
        if high_risk_strategies:
            recommendations.append(f"Yuqori riskli strategiyalar: {', '.join(high_risk_strategies)}")
        
        return recommendations
    
    # Strategy-specific tracking methods
    async def _track_momentum_strategy(self, data: Dict) -> Dict:
        """Momentum strategy tracking"""
        return {
            "lookback_period": 20,
            "signal_strength": 0.75,
            "current_positions": 3
        }
    
    async def _track_mean_reversion_strategy(self, data: Dict) -> Dict:
        """Mean reversion strategy tracking"""
        return {
            "reversion_threshold": 2.0,
            "current_positions": 2,
            "signal_strength": 0.60
        }
    
    async def _track_trend_following_strategy(self, data: Dict) -> Dict:
        """Trend following strategy tracking"""
        return {
            "trend_strength": 0.80,
            "current_positions": 1,
            "trend_direction": "bullish"
        }
    
    async def _track_arbitrage_strategy(self, data: Dict) -> Dict:
        """Arbitrage strategy tracking"""
        return {
            "spread_opportunities": 5,
            "execution_rate": 0.85,
            "current_positions": 4
        }
    
    async def _track_market_making_strategy(self, data: Dict) -> Dict:
        """Market making strategy tracking"""
        return {
            "bid_ask_spread": 0.001,
            "inventory_risk": 0.15,
            "active_quotes": 10
        }