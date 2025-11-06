"""
Portfolio Manager

Portfolio rebalancing va management
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np

@dataclass
class PortfolioPosition:
    """Portfolio position"""
    symbol: str
    quantity: float
    market_value: float
    cost_basis: float
    unrealized_pnl: float
    weight: float
    sector: str
    risk_contribution: float

@dataclass
class RebalanceDecision:
    """Rebalancing decision"""
    action: str  # "buy", "sell", "hold"
    symbol: str
    current_weight: float
    target_weight: float
    quantity_change: float
    reason: str
    risk_impact: float
    expected_improvement: float

class PortfolioManager:
    """
    Portfolio Management Agent
    
    - Automated portfolio rebalancing
    - Asset allocation optimization
    - Risk management
    - Performance tracking
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Portfolio parameters
        self.target_volatility = config.get("target_volatility", 0.15)
        self.rebalance_threshold = config.get("rebalance_threshold", 0.05)  # 5%
        self.max_position_weight = config.get("max_position_weight", 0.20)  # 20%
        self.min_position_weight = config.get("min_position_weight", 0.02)  # 2%
        
        # Asset allocation targets
        self.allocation_targets = {
            "equities": 0.60,
            "bonds": 0.25,
            "commodities": 0.10,
            "cash": 0.05
        }
        
        # Current portfolio state
        self.portfolio_state = {
            "total_value": 100000.0,
            "positions": [],
            "cash": 5000.0,
            "leverage": 1.0,
            "last_rebalance": None,
            "rebalance_count": 0
        }
        
        # Portfolio history
        self.portfolio_history = []
        
        # Risk management
        self.risk_limits = {
            "max_volatility": 0.25,
            "max_drawdown": 0.15,
            "max_leverage": 2.0,
            "min_diversification": 0.3
        }
        
        self.is_running = False
    
    def start(self):
        """Portfolio manager ni ishga tushirish"""
        if self.is_running:
            self.logger.warning("Portfolio manager allaqachon ishlayapti")
            return
        
        self.is_running = True
        self.logger.info("Portfolio manager started")
    
    def stop(self):
        """Portfolio manager ni to'xtatish"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info("Portfolio manager stopped")
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Portfolio hozirgi holatini olish"""
        return self.portfolio_state.copy()
    
    async def rebalance_portfolio(self, decision: Dict) -> Dict[str, Any]:
        """
        Portfolio rebalancing
        """
        if not self.is_running:
            raise RuntimeError("Portfolio manager is not running")
        
        try:
            self.logger.info("Portfolio rebalancing started")
            
            # 1. Current portfolio analysis
            current_analysis = await self._analyze_current_portfolio()
            
            # 2. Target allocation calculation
            target_allocation = await self._calculate_target_allocation(decision)
            
            # 3. Rebalancing opportunities
            rebalance_opportunities = await self._identify_rebalancing_opportunities(
                current_analysis, target_allocation
            )
            
            # 4. Risk assessment
            risk_assessment = await self._assess_rebalance_risk(
                current_analysis, rebalance_opportunities
            )
            
            # 5. Generate rebalancing decisions
            rebalance_decisions = await self._generate_rebalancing_decisions(
                current_analysis, target_allocation, rebalance_opportunities, risk_assessment
            )
            
            # 6. Execution plan
            execution_plan = await self._create_rebalance_execution_plan(rebalance_decisions)
            
            # 7. Portfolio update simulation
            updated_portfolio = await self._simulate_portfolio_update(rebalance_decisions)
            
            # 8. Rebalancing result
            rebalance_result = {
                "timestamp": datetime.now(),
                "rebalance_id": f"rebal_{datetime.now().isoformat()}",
                "trigger_reason": decision.get("reason", "scheduled_rebalance"),
                "current_analysis": current_analysis,
                "target_allocation": target_allocation,
                "rebalance_opportunities": rebalance_opportunities,
                "risk_assessment": risk_assessment,
                "decisions": [asdict(d) for d in rebalance_decisions],
                "execution_plan": execution_plan,
                "expected_improvement": self._calculate_expected_improvement(current_analysis, updated_portfolio),
                "updated_portfolio": updated_portfolio
            }
            
            # Update portfolio state
            self.portfolio_state.update(updated_portfolio)
            self.portfolio_state["last_rebalance"] = datetime.now()
            self.portfolio_state["rebalance_count"] += 1
            
            # History ga qo'shish
            self.portfolio_history.append(rebalance_result)
            
            self.logger.info(f"Portfolio rebalancing completed: {len(rebalance_decisions)} decisions")
            return rebalance_result
            
        except Exception as e:
            self.logger.error(f"Portfolio rebalancing xatosi: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now(),
                "decisions": []
            }
    
    async def _analyze_current_portfolio(self) -> Dict[str, Any]:
        """Portfolio hozirgi tahlili"""
        positions = self.portfolio_state.get("positions", [])
        total_value = self.portfolio_state.get("total_value", 0)
        cash = self.portfolio_state.get("cash", 0)
        
        analysis = {
            "timestamp": datetime.now(),
            "total_value": total_value,
            "cash_position": cash,
            "invested_amount": total_value - cash,
            "cash_weight": cash / total_value if total_value > 0 else 0,
            "positions": [],
            "sector_allocation": {},
            "geographic_allocation": {},
            "risk_metrics": {},
            "performance_metrics": {}
        }
        
        # Position analysis
        for pos in positions:
            weight = pos.get("market_value", 0) / total_value if total_value > 0 else 0
            pnl = pos.get("unrealized_pnl", 0)
            
            position_analysis = {
                "symbol": pos.get("symbol"),
                "weight": weight,
                "market_value": pos.get("market_value"),
                "pnl": pnl,
                "return": pnl / pos.get("cost_basis", 1) if pos.get("cost_basis", 0) > 0 else 0,
                "sector": pos.get("sector", "Unknown"),
                "risk_contribution": pos.get("risk_contribution", 0)
            }
            analysis["positions"].append(position_analysis)
            
            # Sector allocation
            sector = pos.get("sector", "Unknown")
            if sector not in analysis["sector_allocation"]:
                analysis["sector_allocation"][sector] = 0
            analysis["sector_allocation"][sector] += weight
        
        # Calculate portfolio metrics
        weights = [p.get("weight", 0) for p in analysis["positions"]]
        analysis["diversification_ratio"] = 1 - sum(w**2 for w in weights)
        
        # Risk metrics
        total_risk_contribution = sum(p.get("risk_contribution", 0) for p in analysis["positions"])
        analysis["risk_metrics"] = {
            "total_risk_contribution": total_risk_contribution,
            "concentration_risk": max(weights) if weights else 0,
            "sector_concentration": max(analysis["sector_allocation"].values()) if analysis["sector_allocation"] else 0
        }
        
        return analysis
    
    async def _calculate_target_allocation(self, decision: Dict) -> Dict[str, Any]:
        """Target allocation hisoblash"""
        # Base allocation from configuration
        targets = self.allocation_targets.copy()
        
        # Adjust based on market conditions
        market_conditions = decision.get("market_analysis", {})
        
        # Volatility adjustment
        volatility = market_conditions.get("volatility_level", "normal")
        if volatility == "high":
            # Increase defensive allocation
            targets["bonds"] += 0.05
            targets["equities"] -= 0.03
            targets["commodities"] -= 0.02
        elif volatility == "low":
            # Increase growth allocation
            targets["equities"] += 0.03
            targets["bonds"] -= 0.02
            targets["commodities"] += 0.01
        
        # Trend adjustment
        trend = market_conditions.get("trend_direction", "sideways")
        if trend == "uptrend":
            targets["equities"] += 0.02
            targets["cash"] -= 0.02
        elif trend == "downtrend":
            targets["bonds"] += 0.03
            targets["cash"] += 0.02
            targets["equities"] -= 0.05
        
        # Normalize targets to sum to 1
        target_sum = sum(targets.values())
        if target_sum != 1.0:
            factor = 1.0 / target_sum
            targets = {k: v * factor for k, v in targets.items()}
        
        return {
            "targets": targets,
            "asset_classes": ["equities", "bonds", "commodities", "cash"],
            "rebalancing_horizon": "monthly",
            "tolerance_bands": {
                "equities": 0.05,
                "bonds": 0.03,
                "commodities": 0.02,
                "cash": 0.02
            }
        }
    
    async def _identify_rebalancing_opportunities(self, current_analysis: Dict, 
                                                target_allocation: Dict) -> List[Dict]:
        """Rebalancing imkoniyatlarini aniqlash"""
        opportunities = []
        current_sectors = current_analysis.get("sector_allocation", {})
        target_sectors = target_allocation.get("targets", {})
        tolerance_bands = target_allocation.get("tolerance_bands", {})
        
        for asset_class, target_weight in target_sectors.items():
            current_weight = current_sectors.get(asset_class, 0)
            tolerance = tolerance_bands.get(asset_class, self.rebalance_threshold)
            
            deviation = current_weight - target_weight
            
            if abs(deviation) > tolerance:
                opportunity = {
                    "asset_class": asset_class,
                    "current_weight": current_weight,
                    "target_weight": target_weight,
                    "deviation": deviation,
                    "deviation_percent": abs(deviation) / target_weight if target_weight > 0 else 0,
                    "action": "buy" if deviation < 0 else "sell",
                    "priority": abs(deviation) / tolerance,  # Higher deviation = higher priority
                    "reason": f"Allocation deviation: {deviation:.3f}"
                }
                opportunities.append(opportunity)
        
        # Sort by priority
        opportunities.sort(key=lambda x: x["priority"], reverse=True)
        
        return opportunities
    
    async def _assess_rebalance_risk(self, current_analysis: Dict, 
                                   opportunities: List[Dict]) -> Dict[str, float]:
        """Rebalancing risk assessment"""
        risk_scores = {}
        
        # Transaction cost risk
        num_trades = len(opportunities)
        transaction_cost_risk = min(num_trades / 10, 1.0)  # Max risk at 10+ trades
        risk_scores["transaction_cost_risk"] = transaction_cost_risk
        
        # Market timing risk
        # This is simplified - real implementation would consider market volatility
        market_conditions = current_analysis.get("market_conditions", {})
        timing_risk = 0.3 if market_conditions.get("volatility_level") == "high" else 0.1
        risk_scores["market_timing_risk"] = timing_risk
        
        # Liquidity risk
        # Assume cash position available for rebalancing
        cash_needed = sum(abs(op.get("deviation", 0)) * current_analysis.get("total_value", 0) 
                         for op in opportunities if op.get("action") == "buy")
        cash_available = current_analysis.get("cash_position", 0)
        liquidity_risk = 0.0 if cash_needed <= cash_available else (cash_needed - cash_available) / cash_needed
        risk_scores["liquidity_risk"] = min(liquidity_risk, 1.0)
        
        # Concentration risk
        current_concentration = current_analysis.get("risk_metrics", {}).get("concentration_risk", 0)
        rebalance_concentration_risk = abs(sum(op.get("deviation", 0) for op in opportunities))
        concentration_risk = max(current_concentration, rebalance_concentration_risk)
        risk_scores["concentration_risk"] = concentration_risk
        
        # Overall rebalancing risk
        risk_scores["overall_risk"] = np.mean(list(risk_scores.values()))
        
        return risk_scores
    
    async def _generate_rebalancing_decisions(self, current_analysis: Dict, 
                                            target_allocation: Dict, opportunities: List[Dict],
                                            risk_assessment: Dict) -> List[RebalanceDecision]:
        """Rebalancing decisions yaratish"""
        decisions = []
        
        for opportunity in opportunities:
            # Skip if overall risk is too high
            if risk_assessment.get("overall_risk", 0) > 0.8:
                continue
            
            # Calculate quantity change
            total_value = current_analysis.get("total_value", 0)
            current_weight = opportunity.get("current_weight", 0)
            target_weight = opportunity.get("target_weight", 0)
            weight_change = target_weight - current_weight
            
            if abs(weight_change) < 0.001:  # Skip very small changes
                continue
            
            quantity_change = weight_change * total_value
            
            # Get representative asset for asset class
            representative_asset = self._get_representative_asset(opportunity.get("asset_class"))
            if not representative_asset:
                continue
            
            decision = RebalanceDecision(
                action=opportunity.get("action", "hold"),
                symbol=representative_asset,
                current_weight=current_weight,
                target_weight=target_weight,
                quantity_change=quantity_change,
                reason=opportunity.get("reason", ""),
                risk_impact=risk_assessment.get("overall_risk", 0) * abs(weight_change),
                expected_improvement=self._estimate_rebalance_improvement(
                    opportunity, risk_assessment
                )
            )
            
            decisions.append(decision)
        
        # Sort by expected improvement
        decisions.sort(key=lambda x: x.expected_improvement, reverse=True)
        
        # Limit number of decisions
        max_decisions = 5
        return decisions[:max_decisions]
    
    def _get_representative_asset(self, asset_class: str) -> Optional[str]:
        """Asset class uchun representative asset"""
        mapping = {
            "equities": "SPY",  # S&P 500 ETF
            "bonds": "TLT",     # Long-term Treasury ETF
            "commodities": "GLD",  # Gold ETF
            "cash": "CASH"      # Cash position
        }
        return mapping.get(asset_class)
    
    def _estimate_rebalance_improvement(self, opportunity: Dict, risk_assessment: Dict) -> float:
        """Rebalancing improvement estimation"""
        # Base improvement from better allocation
        base_improvement = opportunity.get("priority", 0) * 0.02  # 2% max improvement
        
        # Risk-adjusted improvement
        risk_factor = 1.0 - risk_assessment.get("overall_risk", 0)
        
        # Timing factor (prefer rebalancing in favorable conditions)
        timing_factor = 0.9  # Assume slightly favorable timing
        
        estimated_improvement = base_improvement * risk_factor * timing_factor
        
        return estimated_improvement
    
    async def _create_rebalance_execution_plan(self, decisions: List[RebalanceDecision]) -> Dict[str, Any]:
        """Execution plan yaratish"""
        plan = {
            "execution_order": [],
            "total_trades": len(decisions),
            "estimated_cost": 0.0,
            "execution_duration": 0,
            "risk_impact": 0.0
        }
        
        # Sort decisions by action (sells first to fund buys)
        buy_decisions = [d for d in decisions if d.action == "buy"]
        sell_decisions = [d for d in decisions if d.action == "sell"]
        
        ordered_decisions = sell_decisions + buy_decisions
        
        for i, decision in enumerate(ordered_decisions):
            execution_item = {
                "step": i + 1,
                "action": decision.action,
                "symbol": decision.symbol,
                "quantity_change": decision.quantity_change,
                "target_weight": decision.target_weight,
                "estimated_cost": abs(decision.quantity_change) * 0.001,  # 0.1% transaction cost
                "risk_impact": decision.risk_impact,
                "priority": len(ordered_decisions) - i  # Earlier trades have higher priority
            }
            plan["execution_order"].append(execution_item)
        
        # Plan metrics
        plan["estimated_cost"] = sum(item["estimated_cost"] for item in plan["execution_order"])
        plan["execution_duration"] = len(decisions) * 30  # 30 seconds per trade
        plan["net_quantity_change"] = sum(d.quantity_change for d in decisions)
        plan["total_risk_impact"] = np.mean([d.risk_impact for d in decisions])
        
        return plan
    
    async def _simulate_portfolio_update(self, decisions: List[RebalanceDecision]) -> Dict[str, Any]:
        """Portfolio update simulatsiyasi"""
        updated_state = self.portfolio_state.copy()
        
        # Apply decisions to portfolio
        for decision in decisions:
            symbol = decision.symbol
            quantity_change = decision.quantity_change
            
            # Find existing position or create new one
            existing_position = None
            for pos in updated_state["positions"]:
                if pos.get("symbol") == symbol:
                    existing_position = pos
                    break
            
            if existing_position:
                # Update existing position
                existing_position["quantity"] += quantity_change
                existing_position["market_value"] = existing_position["quantity"] * 1.0  # Mock price
                existing_position["unrealized_pnl"] = existing_position["market_value"] - existing_position["cost_basis"]
            else:
                # Create new position
                new_position = {
                    "symbol": symbol,
                    "quantity": quantity_change,
                    "market_value": quantity_change * 1.0,  # Mock price
                    "cost_basis": quantity_change * 1.0,
                    "unrealized_pnl": 0.0,
                    "weight": 0.0,
                    "sector": "ETF",
                    "risk_contribution": 0.0
                }
                updated_state["positions"].append(new_position)
        
        # Recalculate weights and metrics
        total_value = updated_state["total_value"]
        for pos in updated_state["positions"]:
            pos["weight"] = pos["market_value"] / total_value if total_value > 0 else 0
        
        # Remove positions with zero quantity
        updated_state["positions"] = [
            pos for pos in updated_state["positions"] 
            if pos.get("quantity", 0) != 0
        ]
        
        return updated_state
    
    def _calculate_expected_improvement(self, current_analysis: Dict, updated_portfolio: Dict) -> float:
        """Expected improvement calculation"""
        # Simplified improvement calculation
        current_diversification = current_analysis.get("diversification_ratio", 0.5)
        
        # Calculate new diversification ratio
        positions = updated_portfolio.get("positions", [])
        weights = [pos.get("weight", 0) for pos in positions]
        new_diversification = 1 - sum(w**2 for w in weights)
        
        # Improvement from better diversification
        diversification_improvement = max(0, new_diversification - current_diversification)
        
        # Risk-adjusted improvement
        risk_improvement = diversification_improvement * 0.5
        
        return risk_improvement
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Portfolio summary olish"""
        positions = self.portfolio_state.get("positions", [])
        
        if not positions:
            return {
                "total_value": self.portfolio_state.get("total_value", 0),
                "cash": self.portfolio_state.get("cash", 0),
                "positions": [],
                "message": "Portfolio is empty"
            }
        
        # Portfolio metrics
        total_value = self.portfolio_state.get("total_value", 0)
        cash = self.portfolio_state.get("cash", 0)
        
        # Performance metrics
        total_pnl = sum(pos.get("unrealized_pnl", 0) for pos in positions)
        total_cost_basis = sum(pos.get("cost_basis", 0) for pos in positions)
        portfolio_return = total_pnl / total_cost_basis if total_cost_basis > 0 else 0
        
        # Risk metrics
        weights = [pos.get("weight", 0) for pos in positions]
        concentration_risk = max(weights) if weights else 0
        diversification_ratio = 1 - sum(w**2 for w in weights)
        
        # Sector analysis
        sector_allocation = defaultdict(float)
        for pos in positions:
            sector = pos.get("sector", "Unknown")
            sector_allocation[sector] += pos.get("weight", 0)
        
        return {
            "timestamp": datetime.now(),
            "total_value": total_value,
            "cash_position": cash,
            "invested_value": total_value - cash,
            "positions_count": len(positions),
            "performance": {
                "total_pnl": total_pnl,
                "portfolio_return": portfolio_return,
                "unrealized_pnl": total_pnl
            },
            "risk_metrics": {
                "concentration_risk": concentration_risk,
                "diversification_ratio": diversification_ratio,
                "position_count": len(positions)
            },
            "sector_allocation": dict(sector_allocation),
            "top_positions": sorted(
                positions, 
                key=lambda x: x.get("weight", 0), 
                reverse=True
            )[:5],
            "rebalance_info": {
                "last_rebalance": self.portfolio_state.get("last_rebalance"),
                "rebalance_count": self.portfolio_state.get("rebalance_count", 0)
            }
        }
    
    def optimize_portfolio_weights(self, current_weights: Dict[str, float], 
                                 target_weights: Dict[str, float]) -> Dict[str, float]:
        """Portfolio weights optimizatsiyasi"""
        optimized_weights = current_weights.copy()
        
        # Simple optimization: move towards targets with constraints
        max_change = 0.05  # Maximum 5% change per asset
        
        for asset, target in target_weights.items():
            current = current_weights.get(asset, 0)
            change = target - current
            
            # Apply change limits
            if abs(change) > max_change:
                change = max_change if change > 0 else -max_change
            
            optimized_weights[asset] = max(0, current + change)
        
        # Normalize to ensure weights sum to 1
        total_weight = sum(optimized_weights.values())
        if total_weight != 1.0:
            factor = 1.0 / total_weight
            optimized_weights = {k: v * factor for k, v in optimized_weights.items()}
        
        return optimized_weights