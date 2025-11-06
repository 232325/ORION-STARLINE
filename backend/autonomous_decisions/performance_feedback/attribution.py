"""
Performance Attribution Analysis

Strategy performance attribution va optimization
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict

@dataclass
class AttributionResult:
    """Performance attribution result"""
    timestamp: datetime
    strategy_attribution: Dict[str, float]
    factor_attribution: Dict[str, float]
    asset_attribution: Dict[str, float]
    residual: float
    total_performance: float

@dataclass
class OptimizationResult:
    """Strategy optimization result"""
    improvements: Dict[str, Any]
    new_weights: Dict[str, float]
    expected_performance: float
    risk_metrics: Dict[str, float]
    confidence: float

class PerformanceAttribution:
    """
    Performance Attribution Analysis
    
    - Strategy performance attribution
    - Factor-based attribution
    - Performance optimization
    - Feedback signal generation
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Attribution models (placeholder for future implementation)
        # self.models = {
        #     "brinson": self._brinson_attribution,
        #     "factor": self._factor_attribution,
        #     "carino": self._carino_attribution
        # }
        
        # Performance factors
        self.factors = {
            "market": {"weight": 0.4, "description": "Market exposure"},
            "style": {"weight": 0.3, "description": "Style factors"},
            "selection": {"weight": 0.2, "description": "Security selection"},
            "interaction": {"weight": 0.1, "description": "Interaction effects"}
        }
        
        # Strategy definitions
        self.strategies = {
            "momentum": {
                "lookback": 20,
                "holding": 5,
                "max_positions": 10
            },
            "mean_reversion": {
                "lookback": 10,
                "holding": 3,
                "max_positions": 8
            },
            "trend_following": {
                "lookback": 50,
                "holding": 20,
                "max_positions": 5
            },
            "arbitrage": {
                "lookback": 5,
                "holding": 1,
                "max_positions": 15
            }
        }
        
        # Optimization parameters
        self.optimization_params = {
            "risk_aversion": 1.0,
            "max_iterations": 100,
            "convergence_threshold": 1e-6
        }
        
        # Attribution history
        self.attribution_history = []
    
    async def analyze_performance(self, performance_data: Dict) -> Dict[str, Any]:
        """
        Performance attribution analysis
        """
        try:
            # Attribution computation
            attribution = await self._compute_attribution(performance_data)
            
            # Factor analysis
            factor_analysis = await self._analyze_factors(performance_data)
            
            # Strategy contribution
            strategy_contrib = await self._analyze_strategy_contribution(performance_data)
            
            # Risk-adjusted attribution
            risk_adj_attribution = await self._compute_risk_adjusted_attribution(
                attribution, performance_data
            )
            
            result = {
                "timestamp": datetime.now(),
                "attribution": asdict(attribution),
                "factor_analysis": factor_analysis,
                "strategy_contribution": strategy_contrib,
                "risk_adjusted": asdict(risk_adj_attribution),
                "insights": await self._generate_insights(attribution, factor_analysis)
            }
            
            # History ga qo'shish
            self.attribution_history.append(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Performance attribution xatosi: {str(e)}")
            return {"error": str(e)}
    
    async def _compute_attribution(self, performance_data: Dict) -> AttributionResult:
        """Attribution computation"""
        # Mock data for demonstration
        portfolio_return = performance_data.get("metrics", {}).get("daily_return", 0.0)
        benchmark_return = 0.001  # 0.1% daily
        
        # Strategy attribution
        strategy_attribution = {
            "momentum": portfolio_return * 0.3,
            "mean_reversion": portfolio_return * 0.25,
            "trend_following": portfolio_return * 0.2,
            "arbitrage": portfolio_return * 0.15,
            "cash": portfolio_return * 0.1
        }
        
        # Factor attribution
        factor_attribution = {
            "market": portfolio_return * 0.4,
            "value": portfolio_return * 0.2,
            "momentum_factor": portfolio_return * 0.15,
            "quality": portfolio_return * 0.1,
            "low_volatility": portfolio_return * 0.08,
            "size": portfolio_return * 0.07
        }
        
        # Asset attribution
        positions = performance_data.get("positions", [])
        asset_attribution = {}
        for pos in positions:
            symbol = pos.get("symbol", "UNKNOWN")
            pnl = pos.get("pnl", 0)
            contribution = pnl / 100000.0  # Portfolio value normalization
            asset_attribution[symbol] = contribution
        
        # Calculate residual
        total_attribution = (
            sum(strategy_attribution.values()) +
            sum(factor_attribution.values()) +
            sum(asset_attribution.values())
        ) / 3  # Average of different approaches
        residual = portfolio_return - total_attribution
        
        return AttributionResult(
            timestamp=datetime.now(),
            strategy_attribution=strategy_attribution,
            factor_attribution=factor_attribution,
            asset_attribution=asset_attribution,
            residual=residual,
            total_performance=portfolio_return
        )
    
    async def _analyze_factors(self, performance_data: Dict) -> Dict[str, Any]:
        """Factor-based analysis"""
        # Factor returns
        factor_returns = {
            "market": 0.008,
            "value": 0.003,
            "momentum": 0.012,
            "quality": 0.005,
            "size": -0.002,
            "volatility": 0.004
        }
        
        # Factor exposures (simplified)
        exposures = {
            "market": 0.95,
            "value": 0.2,
            "momentum": 0.6,
            "quality": 0.3,
            "size": -0.1,
            "volatility": 0.4
        }
        
        # Factor contributions
        contributions = {}
        for factor, exposure in exposures.items():
            factor_return = factor_returns.get(factor, 0.0)
            contributions[factor] = exposure * factor_return
        
        # Factor analysis metrics
        factor_analysis = {
            "factor_returns": factor_returns,
            "exposures": exposures,
            "contributions": contributions,
            "factor_performance": self._calculate_factor_performance(contributions),
            "factor_loadings": self._calculate_factor_loadings(contributions, factor_returns)
        }
        
        return factor_analysis
    
    async def _analyze_strategy_contribution(self, performance_data: Dict) -> Dict[str, Any]:
        """Strategy contribution analysis"""
        # Strategy metrics
        strategies = {
            "momentum": {
                "return": 0.015,
                "volatility": 0.18,
                "sharpe": 0.83,
                "max_drawdown": 0.08,
                "weight": 0.3
            },
            "mean_reversion": {
                "return": 0.012,
                "volatility": 0.15,
                "sharpe": 0.80,
                "max_drawdown": 0.06,
                "weight": 0.25
            },
            "trend_following": {
                "return": 0.018,
                "volatility": 0.22,
                "sharpe": 0.82,
                "max_drawdown": 0.12,
                "weight": 0.2
            },
            "arbitrage": {
                "return": 0.008,
                "volatility": 0.08,
                "sharpe": 1.00,
                "max_drawdown": 0.03,
                "weight": 0.15
            }
        }
        
        # Contribution calculations
        contribution_analysis = {}
        for strategy, metrics in strategies.items():
            contribution_analysis[strategy] = {
                "absolute_contribution": metrics["return"] * metrics["weight"],
                "risk_adjusted_contribution": (metrics["return"] / metrics["volatility"]) * metrics["weight"],
                "efficiency": metrics["sharpe"] * metrics["weight"],
                "risk_contribution": metrics["volatility"] * metrics["weight"] * 0.5  # Simplified
            }
        
        # Overall strategy metrics
        total_return = sum(m["return"] * m["weight"] for m in strategies.values())
        total_vol = np.sqrt(sum((m["volatility"] * m["weight"])**2 for m in strategies.values()))
        
        strategy_summary = {
            "individual_strategies": contribution_analysis,
            "portfolio_metrics": {
                "total_return": total_return,
                "total_volatility": total_vol,
                "overall_sharpe": total_return / total_vol if total_vol > 0 else 0,
                "diversification_ratio": self._calculate_diversification_ratio(strategies)
            },
            "strategy_rankings": self._rank_strategies(strategies)
        }
        
        return strategy_summary
    
    async def _compute_risk_adjusted_attribution(self, attribution: AttributionResult, 
                                               performance_data: Dict) -> Dict[str, Any]:
        """Risk-adjusted attribution computation"""
        # Risk metrics
        volatility = performance_data.get("metrics", {}).get("volatility", 0.15)
        var_1d = performance_data.get("metrics", {}).get("var_1d", 0.02)
        
        # Risk-adjusted contributions
        risk_adj_attribution = {}
        
        # Strategy risk-adjusted attribution
        for strategy, contribution in attribution.strategy_attribution.items():
            risk_adj_contribution = contribution / max(volatility, 0.01)  # Sharpe-like ratio
            risk_adj_attribution[f"{strategy}_risk_adj"] = risk_adj_contribution
        
        # Factor risk-adjusted attribution
        for factor, contribution in attribution.factor_attribution.items():
            risk_adj_contribution = contribution / max(volatility, 0.01)
            risk_adj_attribution[f"{factor}_risk_adj"] = risk_adj_contribution
        
        # VaR-adjusted attribution
        var_adj_contribution = attribution.total_performance / max(var_1d, 0.001)
        risk_adj_attribution["var_adjusted_total"] = var_adj_contribution
        
        return {
            "risk_adjusted_attribution": risk_adj_attribution,
            "volatility_adjustment": volatility,
            "var_adjustment": var_1d,
            "risk_metrics": {
                "volatility_risk": volatility,
                "var_risk": var_1d,
                "tail_risk": self._calculate_tail_risk(performance_data)
            }
        }
    
    def _calculate_factor_performance(self, contributions: Dict[str, float]) -> Dict[str, float]:
        """Factor performance calculation"""
        return {factor: contrib for factor, contrib in contributions.items()}
    
    def _calculate_factor_loadings(self, contributions: Dict[str, float], 
                                  factor_returns: Dict[str, float]) -> Dict[str, float]:
        """Factor loadings calculation"""
        loadings = {}
        for factor in contributions:
            if factor in factor_returns and factor_returns[factor] != 0:
                loading = contributions[factor] / factor_returns[factor]
                loadings[factor] = loading
            else:
                loadings[factor] = 0.0
        
        return loadings
    
    def _calculate_diversification_ratio(self, strategies: Dict) -> float:
        """Diversification ratio calculation"""
        # Simplified diversification ratio
        weights = [m["weight"] for m in strategies.values()]
        vols = [m["volatility"] for m in strategies.values()]
        
        # Weighted average volatility
        weighted_vol = sum(w * v for w, v in zip(weights, vols))
        
        # Individual portfolio volatility (simplified)
        portfolio_vol = sum(vols) / len(vols)
        
        diversification_ratio = weighted_vol / portfolio_vol if portfolio_vol > 0 else 1.0
        return diversification_ratio
    
    def _rank_strategies(self, strategies: Dict) -> List[Dict]:
        """Strategy ranking"""
        rankings = []
        
        for strategy, metrics in strategies.items():
            # Composite score (Sharpe + Return/Risk)
            score = metrics["sharpe"] * 0.6 + (metrics["return"] / metrics["max_drawdown"]) * 0.4
            
            rankings.append({
                "strategy": strategy,
                "score": score,
                "sharpe": metrics["sharpe"],
                "return": metrics["return"],
                "drawdown": metrics["max_drawdown"]
            })
        
        # Sort by score (descending)
        rankings.sort(key=lambda x: x["score"], reverse=True)
        return rankings
    
    def _calculate_tail_risk(self, performance_data: Dict) -> float:
        """Tail risk calculation"""
        # Simplified tail risk (skewness of returns)
        # Real implementation would calculate proper tail risk measures
        returns = [0.01, -0.02, 0.015, -0.005, 0.02, -0.01, 0.008, -0.003]
        
        if len(returns) > 2:
            negative_returns = [r for r in returns if r < 0]
            positive_returns = [r for r in returns if r > 0]
            
            avg_negative = np.mean(negative_returns) if negative_returns else 0
            avg_positive = np.mean(positive_returns) if positive_returns else 0
            
            tail_risk = abs(avg_negative) / avg_positive if avg_positive > 0 else 1.0
            return tail_risk
        
        return 0.0
    
    async def _generate_insights(self, attribution: AttributionResult, 
                               factor_analysis: Dict) -> List[str]:
        """Insights generation"""
        insights = []
        
        # Strategy insights
        best_strategy = max(attribution.strategy_attribution.items(), key=lambda x: x[1])
        worst_strategy = min(attribution.strategy_attribution.items(), key=lambda x: x[1])
        
        if best_strategy[1] > 0.005:
            insights.append(f"{best_strategy[0]} strategy eng yaxshi ishlayapti ({best_strategy[1]:.3%})")
        
        if worst_strategy[1] < -0.002:
            insights.append(f"{worst_strategy[0]} strategy optimizatsiya kerak ({worst_strategy[1]:.3%})")
        
        # Factor insights
        best_factor = max(attribution.factor_attribution.items(), key=lambda x: x[1])
        insights.append(f"{best_factor[0]} factor eng katta ta'sir ko'rsatyapti ({best_factor[1]:.3%})")
        
        # Performance quality
        total_positive_contributions = sum(v for v in attribution.strategy_attribution.values() if v > 0)
        if total_positive_contributions > 0.01:
            insights.append("Strategiyalarning ko'pchiligi ijobiy hissa qo'shmoqda")
        
        return insights
    
    async def optimize_strategies(self) -> OptimizationResult:
        """
        Strategy optimization
        """
        try:
            # Current performance analysis
            if not self.attribution_history:
                return OptimizationResult(
                    improvements={},
                    new_weights={},
                    expected_performance=0.0,
                    risk_metrics={},
                    confidence=0.0
                )
            
            latest_attribution = self.attribution_history[-1]
            
            # Optimization based on recent performance
            improvements = await self._generate_improvements(latest_attribution)
            
            # New weights calculation
            new_weights = await self._calculate_new_weights(latest_attribution, improvements)
            
            # Expected performance
            expected_performance = self._estimate_expected_performance(new_weights, improvements)
            
            # Risk metrics
            risk_metrics = self._calculate_optimization_risk_metrics(new_weights, improvements)
            
            # Confidence score
            confidence = self._calculate_optimization_confidence(improvements, latest_attribution)
            
            return OptimizationResult(
                improvements=improvements,
                new_weights=new_weights,
                expected_performance=expected_performance,
                risk_metrics=risk_metrics,
                confidence=confidence
            )
            
        except Exception as e:
            self.logger.error(f"Strategy optimization xatosi: {str(e)}")
            return OptimizationResult({}, {}, 0.0, {}, 0.0)
    
    async def _generate_improvements(self, attribution: Dict) -> Dict[str, Any]:
        """Improvement suggestions"""
        improvements = {}
        
        # Strategy-based improvements
        strategy_contrib = attribution.get("strategy_contribution", {}).get("individual_strategies", {})
        
        for strategy, contrib_data in strategy_contrib.items():
            efficiency = contrib_data.get("efficiency", 0)
            
            if efficiency < 0.5:
                # Low efficiency strategy
                improvements[strategy] = {
                    "action": "reduce_weight",
                    "current_efficiency": efficiency,
                    "target_efficiency": 0.7,
                    "reason": "Low efficiency"
                }
            elif efficiency > 1.0:
                # High efficiency strategy
                improvements[strategy] = {
                    "action": "increase_weight",
                    "current_efficiency": efficiency,
                    "target_efficiency": efficiency * 1.1,
                    "reason": "High efficiency"
                }
        
        return improvements
    
    async def _calculate_new_weights(self, attribution: Dict, improvements: Dict) -> Dict[str, float]:
        """New weights calculation"""
        # Current weights (simplified)
        current_weights = {
            "momentum": 0.3,
            "mean_reversion": 0.25,
            "trend_following": 0.2,
            "arbitrage": 0.15,
            "cash": 0.1
        }
        
        new_weights = current_weights.copy()
        total_adjustment = 0
        
        # Apply improvements
        for strategy, improvement in improvements.items():
            if strategy in current_weights:
                current_weight = current_weights[strategy]
                
                if improvement["action"] == "reduce_weight":
                    adjustment = -0.05  # 5% reduction
                elif improvement["action"] == "increase_weight":
                    adjustment = 0.05  # 5% increase
                else:
                    adjustment = 0
                
                new_weights[strategy] = max(0.01, current_weight + adjustment)
                total_adjustment += adjustment
        
        # Normalize weights to sum to 1
        weight_sum = sum(new_weights.values())
        if weight_sum != 1.0:
            factor = 1.0 / weight_sum
            for strategy in new_weights:
                new_weights[strategy] *= factor
        
        return new_weights
    
    def _estimate_expected_performance(self, weights: Dict[str, float], 
                                     improvements: Dict) -> float:
        """Expected performance estimation"""
        # Base expected returns
        expected_returns = {
            "momentum": 0.015,
            "mean_reversion": 0.012,
            "trend_following": 0.018,
            "arbitrage": 0.008,
            "cash": 0.002
        }
        
        # Calculate weighted expected return
        expected_performance = sum(
            weights.get(strategy, 0) * expected_return 
            for strategy, expected_return in expected_returns.items()
        )
        
        # Apply improvement boost
        if improvements:
            improvement_boost = len(improvements) * 0.002  # 0.2% per improvement
            expected_performance += improvement_boost
        
        return expected_performance
    
    def _calculate_optimization_risk_metrics(self, weights: Dict[str, float], 
                                           improvements: Dict) -> Dict[str, float]:
        """Risk metrics for optimization"""
        # Simplified risk calculations
        strategy_vols = {
            "momentum": 0.18,
            "mean_reversion": 0.15,
            "trend_following": 0.22,
            "arbitrage": 0.08,
            "cash": 0.01
        }
        
        # Portfolio volatility
        portfolio_vol = np.sqrt(sum(
            (weights.get(strategy, 0) * vol)**2 
            for strategy, vol in strategy_vols.items()
        ))
        
        # Risk metrics
        risk_metrics = {
            "portfolio_volatility": portfolio_vol,
            "expected_var": portfolio_vol * 1.65,  # 95% VaR approximation
            "max_drawdown_estimate": portfolio_vol * 2.0,  # Conservative estimate
            "concentration_risk": self._calculate_concentration_risk(weights)
        }
        
        return risk_metrics
    
    def _calculate_concentration_risk(self, weights: Dict[str, float]) -> float:
        """Concentration risk calculation"""
        # Herfindahl index
        herfindahl = sum(w**2 for w in weights.values())
        return herfindahl
    
    def _calculate_optimization_confidence(self, improvements: Dict, 
                                         attribution: Dict) -> float:
        """Optimization confidence calculation"""
        confidence = 0.5  # Base confidence
        
        # More improvements = higher confidence (but with diminishing returns)
        num_improvements = len(improvements)
        if num_improvements > 0:
            confidence += min(num_improvements * 0.1, 0.3)
        
        # Recent performance quality
        performance_score = attribution.get("risk_adjusted", {}).get("total_performance", 0)
        if performance_score > 0:
            confidence += 0.1
        elif performance_score < -0.01:
            confidence -= 0.2
        
        # Attribution quality (residual should be small)
        attribution_quality = 1.0 - abs(attribution.get("attribution", {}).get("residual", 0)) * 10
        confidence += attribution_quality * 0.1
        
        return max(0.0, min(1.0, confidence))