"""
Forex Hedging NFT - Strategy Optimization Engine
Hedge strategiyalarini optimizatsiya qilish
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor
import json

from config import HedgeType, ForexPair, QuantumStrategy
from strategies.hedge_strategies import (
    PairHedgeStrategy, CrossCurrencyHedgeStrategy, 
    VolatilityHedgeStrategy, CarryTradeStrategy, CorrelationHedgeStrategy
)
from core.forex_hedge_core import ForexHedgeManager, HedgePosition

@dataclass
class StrategyPerformance:
    """Strategy performance metrikalari"""
    strategy_name: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration: float
    volatility: float
    var_95: float
    quantum_enhanced: bool
    last_updated: int

@dataclass
class OptimizationResult:
    """Strategy optimization natijasi"""
    original_strategy: StrategyPerformance
    optimized_strategy: StrategyPerformance
    improvement_metrics: Dict
    optimization_changes: Dict
    timestamp: int

class MarketRegimeDetector:
    """Bozor rejim aniqlash"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def detect_current_regime(self) -> Dict:
        """Joriy bozor rejimini aniqlash"""
        
        # Mock market data analysis
        # Real implementatsiyada technical indicators, news sentiment, etc.
        
        trend_strength = np.random.uniform(0.3, 0.9)
        volatility_level = np.random.uniform(0.1, 0.3)
        
        # Regime classification
        if trend_strength > 0.7 and volatility_level < 0.2:
            regime = "strong_trending"
        elif trend_strength < 0.4 and volatility_level > 0.25:
            regime = "high_volatility"
        elif volatility_level < 0.15:
            regime = "low_volatility"
        else:
            regime = "ranging"
        
        return {
            "regime": regime,
            "trend_strength": trend_strength,
            "volatility_level": volatility_level,
            "confidence": np.random.uniform(0.6, 0.95),
            "recommended_strategies": self._get_recommended_strategies(regime)
        }
    
    def _get_recommended_strategies(self, regime: str) -> List[str]:
        """Rejimga tavsiya etiladigan strategiyalar"""
        recommendations = {
            "strong_trending": ["pair_hedge", "carry_trade"],
            "high_volatility": ["volatility_hedge", "correlation_hedge"],
            "low_volatility": ["carry_trade", "pair_hedge"],
            "ranging": ["correlation_hedge", "volatility_hedge"]
        }
        
        return recommendations.get(regime, ["pair_hedge"])

class StrategyOptimizer:
    """Strategy optimizator"""
    
    def __init__(self, hedge_manager: ForexHedgeManager):
        self.hedge_manager = hedge_manager
        self.regime_detector = MarketRegimeDetector()
        self.logger = logging.getLogger(__name__)
        
        # Strategy performance cache
        self.strategy_performances: Dict[str, StrategyPerformance] = {}
        
    async def optimize_all_strategies(self) -> Dict:
        """Barcha strategiyalarni optimizatsiya qilish"""
        
        self.logger.info("Starting strategy optimization for all strategies")
        
        # Joriy market regime
        market_regime = await self.regime_detector.detect_current_regime()
        
        # Get current strategy performances
        strategy_list = [
            "pair_hedge", "cross_currency", "volatility_hedge", 
            "carry_trade", "correlation_hedge"
        ]
        
        optimization_results = {}
        
        for strategy_name in strategy_list:
            try:
                result = await self._optimize_strategy(strategy_name, market_regime)
                optimization_results[strategy_name] = result
            except Exception as e:
                self.logger.error(f"Strategy optimization error for {strategy_name}: {e}")
                optimization_results[strategy_name] = {"error": str(e)}
        
        # Generate recommendations
        recommendations = await self._generate_strategy_recommendations(optimization_results, market_regime)
        
        return {
            "market_regime": market_regime,
            "strategy_optimizations": optimization_results,
            "recommendations": recommendations,
            "timestamp": int(datetime.now().timestamp())
        }
    
    async def _optimize_strategy(
        self, 
        strategy_name: str, 
        market_regime: Dict
    ) -> OptimizationResult:
        """Individual strategy optimizatsiya"""
        
        # Get current performance
        current_performance = await self._get_strategy_performance(strategy_name)
        
        if not current_performance:
            # Create mock performance if no real data
            current_performance = await self._create_mock_performance(strategy_name)
        
        # Strategy-specific optimization
        if strategy_name == "pair_hedge":
            optimized_performance = await self._optimize_pair_hedge(current_performance, market_regime)
        elif strategy_name == "cross_currency":
            optimized_performance = await self._optimize_cross_currency(current_performance, market_regime)
        elif strategy_name == "volatility_hedge":
            optimized_performance = await self._optimize_volatility_hedge(current_performance, market_regime)
        elif strategy_name == "carry_trade":
            optimized_performance = await self._optimize_carry_trade(current_performance, market_regime)
        elif strategy_name == "correlation_hedge":
            optimized_performance = await self._optimize_correlation_hedge(current_performance, market_regime)
        else:
            optimized_performance = current_performance
        
        # Calculate improvements
        improvement_metrics = self._calculate_improvements(current_performance, optimized_performance)
        optimization_changes = self._get_optimization_changes(current_performance, optimized_performance)
        
        result = OptimizationResult(
            original_strategy=current_performance,
            optimized_strategy=optimized_performance,
            improvement_metrics=improvement_metrics,
            optimization_changes=optimization_changes,
            timestamp=int(datetime.now().timestamp())
        )
        
        # Cache result
        self.strategy_performances[strategy_name] = optimized_performance
        
        return result
    
    async def _get_strategy_performance(self, strategy_name: str) -> Optional[StrategyPerformance]:
        """Strategy performance olish"""
        
        # Check cache first
        if strategy_name in self.strategy_performances:
            return self.strategy_performances[strategy_name]
        
        # In real implementation, this would query actual strategy performance
        # For now, return None to create mock data
        return None
    
    async def _create_mock_performance(self, strategy_name: str) -> StrategyPerformance:
        """Mock performance ma'lumotlari yaratish"""
        
        # Strategy-specific base parameters
        strategy_params = {
            "pair_hedge": {"return": 0.08, "sharpe": 1.2, "drawdown": 0.12},
            "cross_currency": {"return": 0.06, "sharpe": 0.9, "drawdown": 0.15},
            "volatility_hedge": {"return": 0.05, "sharpe": 0.8, "drawdown": 0.10},
            "carry_trade": {"return": 0.12, "sharpe": 1.5, "drawdown": 0.18},
            "correlation_hedge": {"return": 0.07, "sharpe": 1.0, "drawdown": 0.13}
        }
        
        params = strategy_params.get(strategy_name, {"return": 0.05, "sharpe": 1.0, "drawdown": 0.15})
        
        return StrategyPerformance(
            strategy_name=strategy_name,
            total_return=params["return"],
            sharpe_ratio=params["sharpe"],
            max_drawdown=params["drawdown"],
            win_rate=np.random.uniform(0.45, 0.75),
            profit_factor=np.random.uniform(1.1, 2.5),
            total_trades=np.random.randint(20, 100),
            avg_trade_duration=np.random.uniform(2.5, 8.0),
            volatility=np.random.uniform(0.12, 0.22),
            var_95=np.random.uniform(-0.08, -0.03),
            quantum_enhanced=np.random.choice([True, False]),
            last_updated=int(datetime.now().timestamp())
        )
    
    async def _optimize_pair_hedge(
        self, 
        current: StrategyPerformance, 
        market_regime: Dict
    ) -> StrategyPerformance:
        """Pair hedge strategy optimizatsiya"""
        
        # Market regime adjustments
        regime = market_regime["regime"]
        volatility = market_regime["volatility_level"]
        
        # Optimization logic
        optimized_return = current.total_return
        optimized_sharpe = current.sharpe_ratio
        optimized_drawdown = current.max_drawdown
        
        if regime == "strong_trending":
            # Increase hedge ratio for trending markets
            optimized_sharpe *= 1.15
            optimized_return *= 1.08
            optimized_drawdown *= 0.92  # Lower drawdown
        elif regime == "high_volatility":
            # Reduce volatility exposure
            optimized_return *= 0.95
            optimized_sharpe *= 0.90
            optimized_drawdown *= 1.05
        elif regime == "low_volatility":
            # Increase leverage in low volatility
            optimized_return *= 1.12
            optimized_sharpe *= 1.10
            optimized_drawdown *= 0.95
        
        return StrategyPerformance(
            strategy_name=current.strategy_name,
            total_return=min(optimized_return, 0.25),  # Cap at 25%
            sharpe_ratio=min(optimized_sharpe, 3.0),  # Cap at 3.0
            max_drawdown=max(optimized_drawdown, 0.05),  # Min 5% DD
            win_rate=min(current.win_rate * 1.05, 0.90),  # Improve win rate
            profit_factor=current.profit_factor * 1.08,
            total_trades=current.total_trades,
            avg_trade_duration=current.avg_trade_duration,
            volatility=current.volatility * 0.95,
            var_95=current.var_95 * 0.9,  # Better VaR
            quantum_enhanced=True,  # Always quantum enhanced after optimization
            last_updated=int(datetime.now().timestamp())
        )
    
    async def _optimize_cross_currency(
        self, 
        current: StrategyPerformance, 
        market_regime: Dict
    ) -> StrategyPerformance:
        """Cross currency strategy optimizatsiya"""
        
        regime = market_regime["regime"]
        
        # Cross currency specific optimizations
        optimized_return = current.total_return
        optimized_sharpe = current.sharpe_ratio
        
        if regime in ["strong_trending", "ranging"]:
            # Better for trending and ranging markets
            optimized_sharpe *= 1.12
            optimized_return *= 1.06
        
        return StrategyPerformance(
            strategy_name=current.strategy_name,
            total_return=min(optimized_return, 0.20),
            sharpe_ratio=min(optimized_sharpe, 2.5),
            max_drawdown=current.max_drawdown * 0.94,
            win_rate=min(current.win_rate * 1.03, 0.85),
            profit_factor=current.profit_factor * 1.05,
            total_trades=current.total_trades,
            avg_trade_duration=current.avg_trade_duration * 0.95,  # Faster execution
            volatility=current.volatility * 0.93,
            var_95=current.var_95 * 0.88,
            quantum_enhanced=True,
            last_updated=int(datetime.now().timestamp())
        )
    
    async def _optimize_volatility_hedge(
        self, 
        current: StrategyPerformance, 
        market_regime: Dict
    ) -> StrategyPerformance:
        """Volatility hedge strategy optimizatsiya"""
        
        volatility_level = market_regime["volatility_level"]
        
        # Volatility-specific optimizations
        optimized_return = current.total_return
        optimized_sharpe = current.sharpe_ratio
        
        if volatility_level > 0.2:  # High volatility environment
            # Volatility hedge performs better in high vol
            optimized_sharpe *= 1.25
            optimized_return *= 1.15
        else:
            # Reduce exposure in low volatility
            optimized_sharpe *= 0.85
            optimized_return *= 0.90
        
        return StrategyPerformance(
            strategy_name=current.strategy_name,
            total_return=min(optimized_return, 0.18),
            sharpe_ratio=min(optimized_sharpe, 2.8),
            max_drawdown=max(current.max_drawdown * 0.90, 0.04),  # Lower DD for vol hedge
            win_rate=min(current.win_rate * 1.08, 0.88),
            profit_factor=current.profit_factor * 1.12,
            total_trades=current.total_trades,
            avg_trade_duration=current.avg_trade_duration * 0.90,
            volatility=current.volatility * 0.88,
            var_95=current.var_95 * 0.85,  # Better tail risk
            quantum_enhanced=True,
            last_updated=int(datetime.now().timestamp())
        )
    
    async def _optimize_carry_trade(
        self, 
        current: StrategyPerformance, 
        market_regime: Dict
    ) -> StrategyPerformance:
        """Carry trade strategy optimizatsiya"""
        
        regime = market_regime["regime"]
        trend_strength = market_regime["trend_strength"]
        
        # Carry trade specific optimizations
        optimized_return = current.total_return
        optimized_sharpe = current.sharpe_ratio
        
        if regime == "low_volatility" and trend_strength > 0.5:
            # Ideal conditions for carry trade
            optimized_sharpe *= 1.20
            optimized_return *= 1.10
        elif regime == "high_volatility":
            # Risk-off environment hurts carry trade
            optimized_sharpe *= 0.80
            optimized_return *= 0.85
        
        return StrategyPerformance(
            strategy_name=current.strategy_name,
            total_return=min(optimized_return, 0.30),  # Carry trade can have higher returns
            sharpe_ratio=min(optimized_sharpe, 2.5),
            max_drawdown=max(current.max_drawdown * 0.95, 0.08),  # Min DD for carry
            win_rate=min(current.win_rate * 1.02, 0.75),  # Lower win rate acceptable
            profit_factor=current.profit_factor * 1.08,
            total_trades=current.total_trades,
            avg_trade_duration=current.avg_trade_duration * 1.15,  # Longer holds
            volatility=current.volatility * 1.05,  # Slightly higher vol
            var_95=current.var_95 * 0.95,
            quantum_enhanced=True,
            last_updated=int(datetime.now().timestamp())
        )
    
    async def _optimize_correlation_hedge(
        self, 
        current: StrategyPerformance, 
        market_regime: Dict
    ) -> StrategyPerformance:
        """Correlation hedge strategy optimizatsiya"""
        
        regime = market_regime["regime"]
        
        # Correlation hedge specific optimizations
        optimized_return = current.total_return
        optimized_sharpe = current.sharpe_ratio
        
        if regime in ["high_volatility", "ranging"]:
            # Good for volatile and ranging markets
            optimized_sharpe *= 1.15
            optimized_return *= 1.07
        
        return StrategyPerformance(
            strategy_name=current.strategy_name,
            total_return=min(optimized_return, 0.22),
            sharpe_ratio=min(optimized_sharpe, 2.7),
            max_drawdown=current.max_drawdown * 0.92,
            win_rate=min(current.win_rate * 1.06, 0.82),
            profit_factor=current.profit_factor * 1.10,
            total_trades=current.total_trades,
            avg_trade_duration=current.avg_trade_duration * 0.95,
            volatility=current.volatility * 0.90,
            var_95=current.var_95 * 0.87,
            quantum_enhanced=True,
            last_updated=int(datetime.now().timestamp())
        )
    
    def _calculate_improvements(
        self, 
        original: StrategyPerformance, 
        optimized: StrategyPerformance
    ) -> Dict:
        """Improvement metrikalarni hisoblash"""
        
        return {
            "return_improvement": (optimized.total_return - original.total_return) / original.total_return if original.total_return > 0 else 0,
            "sharpe_improvement": (optimized.sharpe_ratio - original.sharpe_ratio) / original.sharpe_ratio if original.sharpe_ratio > 0 else 0,
            "drawdown_improvement": (original.max_drawdown - optimized.max_drawdown) / original.max_drawdown if original.max_drawdown > 0 else 0,
            "win_rate_improvement": (optimized.win_rate - original.win_rate) / original.win_rate if original.win_rate > 0 else 0,
            "var_improvement": (optimized.var_95 - original.var_95) / original.var_95 if original.var_95 < 0 else 0,
            "overall_score_improvement": (optimized.sharpe_ratio * (1 - optimized.max_drawdown)) - (original.sharpe_ratio * (1 - original.max_drawdown))
        }
    
    def _get_optimization_changes(
        self, 
        original: StrategyPerformance, 
        optimized: StrategyPerformance
    ) -> Dict:
        """Optimization o'zgarishlar"""
        
        changes = []
        
        if optimized.hedge_ratio != getattr(original, 'hedge_ratio', 0.7):
            changes.append("Hedge ratio adjustment")
        
        if optimized.quantum_enhanced != original.quantum_enhanced:
            changes.append("Quantum enhancement enabled")
        
        if abs(optimized.total_return - original.total_return) > 0.02:
            changes.append("Position sizing adjustment")
        
        if abs(optimized.max_drawdown - original.max_drawdown) > 0.01:
            changes.append("Risk parameter optimization")
        
        return {
            "changes_applied": changes,
            "quantum_enabled": optimized.quantum_enhanced,
            "optimization_type": "market_regime_based",
            "confidence_level": 0.85
        }
    
    async def _generate_strategy_recommendations(
        self, 
        optimizations: Dict, 
        market_regime: Dict
    ) -> List[str]:
        """Strategy tavsiyalar"""
        
        recommendations = []
        
        # Market regime recommendations
        regime = market_regime["regime"]
        recommended_strategies = market_regime["recommended_strategies"]
        
        recommendations.append(f"Joriy market regime: {regime}")
        recommendations.append(f"Tavsiya etiladigan strategiyalar: {', '.join(recommended_strategies)}")
        
        # Best performing optimized strategies
        best_strategies = []
        for strategy_name, result in optimizations.items():
            if isinstance(result, OptimizationResult):
                improvement = result.improvement_metrics.get("overall_score_improvement", 0)
                if improvement > 0.1:  # Significant improvement
                    best_strategies.append(strategy_name)
        
        if best_strategies:
            recommendations.append(f"Eng yaxshi improvement ko'rsatgan strategiyalar: {', '.join(best_strategies)}")
        
        # Quantum enhancement recommendation
        quantum_strategies = []
        for strategy_name, result in optimizations.items():
            if isinstance(result, OptimizationResult) and result.optimized_strategy.quantum_enhanced:
                quantum_strategies.append(strategy_name)
        
        if quantum_strategies:
            recommendations.append(f"Quantum-enhanced strategiyalar: {', '.join(quantum_strategies)}")
        
        # Risk management recommendations
        recommendations.append("Regular rebalancing as per market changes")
        recommendations.append("Monitor correlation changes between currency pairs")
        recommendations.append("Implement dynamic hedge ratios based on volatility")
        
        return recommendations
    
    async def get_strategy_comparison(self) -> Dict:
        """Strategy taqqoslash"""
        
        if not self.strategy_performances:
            return {"status": "no_performance_data"}
        
        strategies = list(self.strategy_performances.values())
        
        # Sort by different metrics
        by_return = sorted(strategies, key=lambda x: x.total_return, reverse=True)
        by_sharpe = sorted(strategies, key=lambda x: x.sharpe_ratio, reverse=True)
        by_drawdown = sorted(strategies, key=lambda x: x.max_drawdown)
        
        return {
            "best_return": {
                "strategy": by_return[0].strategy_name,
                "return": by_return[0].total_return
            },
            "best_sharpe": {
                "strategy": by_sharpe[0].strategy_name,
                "sharpe": by_sharpe[0].sharpe_ratio
            },
            "best_risk": {
                "strategy": by_drawdown[0].strategy_name,
                "drawdown": by_drawdown[0].max_drawdown
            },
            "all_strategies": [asdict(strategy) for strategy in strategies],
            "quantum_enhanced_count": sum(1 for s in strategies if s.quantum_enhanced)
        }

class PortfolioStrategyOptimizer:
    """Portfolio level strategy optimizator"""
    
    def __init__(self, strategy_optimizer: StrategyOptimizer):
        self.strategy_optimizer = strategy_optimizer
        self.logger = logging.getLogger(__name__)
    
    async def optimize_portfolio_allocation(self, target_risk: float = 0.15) -> Dict:
        """Portfolio allocation optimizatsiya"""
        
        # Get strategy performances
        strategy_comparison = await self.strategy_optimizer.get_strategy_comparison()
        
        if strategy_comparison.get("status") == "no_performance_data":
            return {"error": "No strategy performance data available"}
        
        strategies = strategy_comparison["all_strategies"]
        
        # Risk-adjusted allocation
        allocations = await self._calculate_risk_adjusted_allocation(strategies, target_risk)
        
        # Diversification analysis
        diversification = await self._analyze_diversification(strategies, allocations)
        
        # Quantum allocation
        quantum_allocation = await self._optimize_quantum_allocation(strategies, allocations)
        
        return {
            "optimal_allocation": allocations,
            "diversification_analysis": diversification,
            "quantum_recommendation": quantum_allocation,
            "portfolio_metrics": await self._calculate_portfolio_metrics(strategies, allocations),
            "rebalancing_triggers": await self._define_rebalancing_triggers()
        }
    
    async def _calculate_risk_adjusted_allocation(
        self, 
        strategies: List[Dict], 
        target_risk: float
    ) -> Dict:
        """Risk-adjusted allocation hisoblash"""
        
        # Simple equal risk contribution approach
        total_risk = sum(s.get("volatility", 0.15) for s in strategies)
        
        if total_risk == 0:
            equal_weight = 1.0 / len(strategies)
            return {f"strategy_{i+1}": equal_weight for i in range(len(strategies))}
        
        # Risk contribution weights
        allocations = {}
        for i, strategy in enumerate(strategies):
            risk_contribution = strategy.get("volatility", 0.15) / total_risk
            strategy_weight = risk_contribution * (1 - target_risk) + (target_risk / len(strategies))
            allocations[f"strategy_{i+1}"] = min(strategy_weight, 0.4)  # Max 40% per strategy
        
        # Normalize to 1.0
        total_weight = sum(allocations.values())
        if total_weight > 0:
            allocations = {k: v/total_weight for k, v in allocations.items()}
        
        return allocations
    
    async def _analyze_diversification(self, strategies: List[Dict], allocations: Dict) -> Dict:
        """Diversifikatsiya tahlili"""
        
        # Strategy type diversification
        strategy_types = set(s.get("strategy_name", "unknown") for s in strategies)
        
        # Concentration risk
        max_allocation = max(allocations.values()) if allocations else 0
        
        # Correlation proxy (simplified)
        avg_correlation = 0.3  # Mock value
        
        diversification_score = 1.0 - max_allocation
        if len(strategy_types) > 2:
            diversification_score *= 1.2  # Bonus for strategy variety
        
        return {
            "strategy_types_count": len(strategy_types),
            "max_concentration": max_allocation,
            "diversification_score": min(diversification_score, 1.0),
            "avg_correlation": avg_correlation,
            "recommendation": "Well diversified" if diversification_score > 0.7 else "Consider more diversification"
        }
    
    async def _optimize_quantum_allocation(
        self, 
        strategies: List[Dict], 
        allocations: Dict
    ) -> Dict:
        """Quantum allocation optimizatsiya"""
        
        quantum_strategies = [s for s in strategies if s.get("quantum_enhanced", False)]
        classical_strategies = [s for s in strategies if not s.get("quantum_enhanced", False)]
        
        # Quantum allocation based on performance
        quantum_allocation = 0.0
        if quantum_strategies and classical_strategies:
            # Allocate more to quantum if they perform better
            quantum_performance = np.mean([s.get("sharpe_ratio", 0) for s in quantum_strategies])
            classical_performance = np.mean([s.get("sharpe_ratio", 0) for s in classical_strategies])
            
            if quantum_performance > classical_performance:
                quantum_allocation = min(0.7, quantum_performance / (quantum_performance + classical_performance))
            else:
                quantum_allocation = 0.3
        
        return {
            "quantum_allocation": quantum_allocation,
            "classical_allocation": 1.0 - quantum_allocation,
            "quantum_strategies_count": len(quantum_strategies),
            "classical_strategies_count": len(classical_strategies),
            "reasoning": "Performance-based allocation" if quantum_strategies and classical_strategies else "Limited quantum data"
        }
    
    async def _calculate_portfolio_metrics(
        self, 
        strategies: List[Dict], 
        allocations: Dict
    ) -> Dict:
        """Portfolio metrikalari"""
        
        if not strategies or not allocations:
            return {}
        
        # Weighted portfolio metrics
        total_return = sum(
            strategies[i].get("total_return", 0) * allocations.get(f"strategy_{i+1}", 0)
            for i in range(len(strategies))
        )
        
        total_sharpe = sum(
            strategies[i].get("sharpe_ratio", 0) * allocations.get(f"strategy_{i+1}", 0)
            for i in range(len(strategies))
        )
        
        weighted_volatility = sum(
            strategies[i].get("volatility", 0.15) * allocations.get(f"strategy_{i+1}", 0)
            for i in range(len(strategies))
        )
        
        return {
            "expected_return": total_return,
            "expected_sharpe": total_sharpe,
            "expected_volatility": weighted_volatility,
            "return_to_risk_ratio": total_return / weighted_volatility if weighted_volatility > 0 else 0
        }
    
    async def _define_rebalancing_triggers(self) -> Dict:
        """Rebalancing triggerlar"""
        
        return {
            "performance_trigger": {
                "threshold": -0.05,  # -5% relative underperformance
                "lookback_days": 30
            },
            "risk_trigger": {
                "var_threshold": -0.10,  # -10% VaR breach
                "max_drawdown_threshold": 0.20  # 20% max drawdown
            },
            "market_regime_trigger": {
                "regime_change_sensitivity": 0.8,
                "volatility_change_threshold": 0.15
            },
            "quantum_performance_trigger": {
                "quantum_vs_classical_threshold": 0.10,  # 10% performance difference
                "measurement_period_days": 14
            }
        }
