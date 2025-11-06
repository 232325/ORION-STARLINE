"""
Trading Agent

Autonomous trading decisions qabul qilish
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np

@dataclass
class TradingDecision:
    """Trading decision structure"""
    action_type: str  # "buy", "sell", "hold", "rebalance"
    symbol: str
    quantity: float
    price: float
    confidence: float
    strategy: str
    reasoning: str
    risk_score: float
    expected_return: float
    timestamp: datetime

@dataclass
class TradeExecution:
    """Trade execution result"""
    decision_id: str
    status: str  # "executed", "rejected", "partial"
    executed_quantity: float
    executed_price: float
    commission: float
    pnl: float
    timestamp: datetime

class TradingAgent:
    """
    Autonomous Trading Decision Agent
    
    - Automated trading decisions
    - Multi-strategy decision making
    - Risk-adjusted position sizing
    - Real-time decision execution
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Trading parameters
        self.base_position_size = config.get("base_position_size", 10000.0)
        self.max_position_size = config.get("max_position_size", 100000.0)
        self.min_confidence = config.get("min_confidence", 0.7)
        self.max_risk_per_trade = config.get("max_risk_per_trade", 0.02)  # 2% of portfolio
        
        # Decision tracking
        self.decision_history = []
        self.execution_history = []
        self.active_positions = {}
        
        # Strategy definitions
        self.trading_strategies = {
            "momentum": self._momentum_strategy,
            "mean_reversion": self._mean_reversion_strategy,
            "trend_following": self._trend_following_strategy,
            "arbitrage": self._arbitrage_strategy,
            "breakout": self._breakout_strategy,
            "contrarian": self._contrarian_strategy
        }
        
        # Market data cache
        self.market_data_cache = {}
        self.last_market_update = None
        
        # Execution settings
        self.execution_mode = config.get("execution_mode", "limit")  # limit, market, stop
        self.execution_delay = config.get("execution_delay", 0)  # seconds
        self.is_running = False
    
    def start(self):
        """Trading agent ni ishga tushirish"""
        if self.is_running:
            self.logger.warning("Trading agent allaqachon ishlayapti")
            return
        
        self.is_running = True
        self.logger.info("Trading agent started")
    
    def stop(self):
        """Trading agent ni to'xtatish"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info("Trading agent stopped")
    
    async def make_decision(self, market_data: Dict, performance_data: Dict, 
                          attribution: Dict, portfolio_state: Dict) -> Dict[str, Any]:
        """
        Asosiy decision making metod
        """
        if not self.is_running:
            raise RuntimeError("Trading agent is not running")
        
        try:
            self.logger.info("Trading decision making started")
            
            # 1. Market analysis
            market_analysis = await self._analyze_market_conditions(market_data)
            
            # 2. Strategy signals
            strategy_signals = await self._generate_strategy_signals(market_data)
            
            # 3. Risk assessment
            risk_assessment = await self._assess_trading_risk(portfolio_state, market_analysis)
            
            # 4. Portfolio alignment
            portfolio_analysis = await self._analyze_portfolio_alignment(portfolio_state, strategy_signals)
            
            # 5. Decision generation
            decisions = await self._generate_trading_decisions(
                strategy_signals, risk_assessment, portfolio_analysis
            )
            
            # 6. Decision filtering va prioritization
            filtered_decisions = await self._filter_and_prioritize_decisions(decisions, risk_assessment)
            
            # 7. Final decision assembly
            decision_package = {
                "timestamp": datetime.now(),
                "decisions": [asdict(d) for d in filtered_decisions],
                "market_analysis": market_analysis,
                "strategy_signals": strategy_signals,
                "risk_assessment": risk_assessment,
                "portfolio_analysis": portfolio_analysis,
                "confidence_score": self._calculate_decision_confidence(filtered_decisions),
                "execution_plan": await self._create_execution_plan(filtered_decisions)
            }
            
            # History ga qo'shish
            self.decision_history.append(decision_package)
            
            self.logger.info(f"Generated {len(filtered_decisions)} trading decisions")
            return decision_package
            
        except Exception as e:
            self.logger.error(f"Trading decision making xatosi: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now(),
                "decisions": []
            }
    
    async def _analyze_market_conditions(self, market_data: Dict) -> Dict[str, Any]:
        """Market sharoitlarini tahlil qilish"""
        analysis = {
            "timestamp": datetime.now(),
            "overall_sentiment": "neutral",
            "volatility_level": "normal",
            "trend_direction": "sideways",
            "liquidity_conditions": "adequate",
            "correlation_clusters": {},
            "risk_factors": []
        }
        
        # Market sentiment analysis
        if "sentiment_score" in market_data:
            sentiment = market_data["sentiment_score"]
            if sentiment > 0.7:
                analysis["overall_sentiment"] = "bullish"
            elif sentiment < 0.3:
                analysis["overall_sentiment"] = "bearish"
        
        # Volatility analysis
        volatility_data = market_data.get("volatility", {})
        if volatility_data:
            avg_volatility = np.mean(list(volatility_data.values()))
            if avg_volatility > 0.025:
                analysis["volatility_level"] = "high"
            elif avg_volatility < 0.01:
                analysis["volatility_level"] = "low"
        
        # Trend analysis
        trends = market_data.get("trends", {})
        if trends:
            trend_counts = defaultdict(int)
            for trend in trends.values():
                trend_counts[trend] += 1
            
            if trend_counts.get("bullish", 0) > len(trends) * 0.6:
                analysis["trend_direction"] = "uptrend"
            elif trend_counts.get("bearish", 0) > len(trends) * 0.6:
                analysis["trend_direction"] = "downtrend"
        
        # Liquidity analysis
        volumes = market_data.get("volumes", {})
        if volumes:
            avg_volume = np.mean(list(volumes.values()))
            if avg_volume < 500:  # Low volume threshold
                analysis["liquidity_conditions"] = "poor"
            elif avg_volume > 2000:  # High volume threshold
                analysis["liquidity_conditions"] = "excellent"
        
        return analysis
    
    async def _generate_strategy_signals(self, market_data: Dict) -> Dict[str, List[Dict]]:
        """Strategy signallarini yaratish"""
        strategy_signals = {}
        
        for strategy_name, strategy_func in self.trading_strategies.items():
            try:
                signals = await strategy_func(market_data)
                if signals:
                    strategy_signals[strategy_name] = signals
            except Exception as e:
                self.logger.error(f"Strategy signal generation xatosi ({strategy_name}): {str(e)}")
        
        return strategy_signals
    
    async def _assess_trading_risk(self, portfolio_state: Dict, market_analysis: Dict) -> Dict[str, float]:
        """Trading risk assessment"""
        risk_scores = {}
        
        # Portfolio risk
        current_risk = portfolio_state.get("risk_metrics", {}).get("portfolio_var", 0.02)
        risk_scores["portfolio_risk"] = current_risk
        
        # Market risk
        market_risk_factor = {
            "high": 0.3,
            "normal": 0.15,
            "low": 0.05
        }.get(market_analysis.get("volatility_level", "normal"), 0.15)
        risk_scores["market_risk"] = market_risk_factor
        
        # Liquidity risk
        liquidity_risk_factor = {
            "poor": 0.2,
            "adequate": 0.1,
            "excellent": 0.05
        }.get(market_analysis.get("liquidity_conditions", "adequate"), 0.1)
        risk_scores["liquidity_risk"] = liquidity_risk_factor
        
        # Correlation risk
        correlation_risk = market_analysis.get("correlation_clusters", {}).get("concentration", 0.1)
        risk_scores["correlation_risk"] = correlation_risk
        
        # Overall risk score
        risk_scores["overall_risk"] = np.mean(list(risk_scores.values()))
        
        return risk_scores
    
    async def _analyze_portfolio_alignment(self, portfolio_state: Dict, strategy_signals: Dict) -> Dict[str, Any]:
        """Portfolio alignment analysis"""
        analysis = {
            "alignment_score": 0.5,
            "overweight_assets": [],
            "underweight_assets": [],
            "concentration_risk": 0.0,
            "sector_exposure": {},
            "geographic_exposure": {}
        }
        
        positions = portfolio_state.get("positions", [])
        if not positions:
            return analysis
        
        # Calculate weights
        total_value = sum(pos.get("value", 0) for pos in positions)
        
        for pos in positions:
            symbol = pos.get("symbol", "UNKNOWN")
            value = pos.get("value", 0)
            weight = value / total_value if total_value > 0 else 0
            
            # Check for concentration
            if weight > 0.2:  # 20% threshold
                analysis["overweight_assets"].append(symbol)
            elif weight < 0.05:  # 5% threshold
                analysis["underweight_assets"].append(symbol)
        
        # Concentration risk
        weights = [pos.get("value", 0) / total_value if total_value > 0 else 0 for pos in positions]
        herfindahl_index = sum(w**2 for w in weights)
        analysis["concentration_risk"] = herfindahl_index
        
        # Strategy alignment
        strategy_alignment = 0
        num_strategies_with_signals = len(strategy_signals)
        if num_strategies_with_signals > 0:
            strategy_alignment = min(num_strategies_with_signals / 3, 1.0)  # Max at 3 active strategies
        
        analysis["alignment_score"] = (1 - herfindahl_index) * strategy_alignment
        
        return analysis
    
    async def _generate_trading_decisions(self, strategy_signals: Dict, risk_assessment: Dict, 
                                        portfolio_analysis: Dict) -> List[TradingDecision]:
        """Trading decisions yaratish"""
        decisions = []
        
        # Process each strategy's signals
        for strategy_name, signals in strategy_signals.items():
            for signal in signals:
                try:
                    decision = await self._create_decision_from_signal(
                        signal, strategy_name, risk_assessment, portfolio_analysis
                    )
                    if decision:
                        decisions.append(decision)
                except Exception as e:
                    self.logger.error(f"Decision creation xatosi ({strategy_name}): {str(e)}")
        
        return decisions
    
    async def _create_decision_from_signal(self, signal: Dict, strategy_name: str, 
                                         risk_assessment: Dict, portfolio_analysis: Dict) -> Optional[TradingDecision]:
        """Signal dan decision yaratish"""
        # Signal validation
        confidence = signal.get("confidence", 0.0)
        if confidence < self.min_confidence:
            return None
        
        # Risk check
        if risk_assessment.get("overall_risk", 0) > 0.8:
            return None
        
        # Position sizing
        position_size = self._calculate_position_size(signal, risk_assessment)
        if position_size <= 0:
            return None
        
        # Price estimation
        current_price = signal.get("current_price", 1.0)
        
        decision = TradingDecision(
            action_type=signal.get("action", "hold"),
            symbol=signal.get("symbol", "UNKNOWN"),
            quantity=position_size / current_price,  # Calculate quantity from size
            price=current_price,
            confidence=confidence,
            strategy=strategy_name,
            reasoning=signal.get("reasoning", ""),
            risk_score=risk_assessment.get("overall_risk", 0.0),
            expected_return=signal.get("expected_return", 0.0),
            timestamp=datetime.now()
        )
        
        return decision
    
    def _calculate_position_size(self, signal: Dict, risk_assessment: Dict) -> float:
        """Position size hisoblash"""
        base_size = self.base_position_size
        
        # Confidence adjustment
        confidence = signal.get("confidence", 0.5)
        confidence_multiplier = 0.5 + (confidence * 1.5)  # 0.5x to 2x range
        
        # Risk adjustment
        risk_factor = max(0.1, 1.0 - risk_assessment.get("overall_risk", 0.0))
        
        # Expected return adjustment
        expected_return = signal.get("expected_return", 0.0)
        return_multiplier = 0.5 + (max(0, expected_return) * 20)  # Boost for positive returns
        
        # Strategy-specific adjustments
        strategy = signal.get("strategy", "default")
        strategy_multiplier = {
            "momentum": 1.2,
            "trend_following": 1.1,
            "mean_reversion": 0.8,
            "arbitrage": 1.5,
            "breakout": 1.0,
            "contrarian": 0.9
        }.get(strategy, 1.0)
        
        # Calculate final position size
        position_size = (base_size * confidence_multiplier * risk_factor * 
                        return_multiplier * strategy_multiplier)
        
        # Apply limits
        position_size = max(
            position_size * 0.1,  # Minimum size (10% of calculated)
            min(position_size, self.max_position_size)
        )
        
        return position_size
    
    async def _filter_and_prioritize_decisions(self, decisions: List[TradingDecision], 
                                             risk_assessment: Dict) -> List[TradingDecision]:
        """Decision larni filtrlash va priority qilish"""
        if not decisions:
            return []
        
        # Risk-based filtering
        filtered_decisions = []
        for decision in decisions:
            if decision.risk_score > 0.9:  # Skip very high risk decisions
                continue
            if decision.confidence < 0.5:  # Skip low confidence decisions
                continue
            filtered_decisions.append(decision)
        
        # Risk-adjusted scoring
        for decision in filtered_decisions:
            decision.score = (
                decision.confidence * 0.4 +
                decision.expected_return * 0.3 +
                (1 - decision.risk_score) * 0.3
            )
        
        # Sort by score
        filtered_decisions.sort(key=lambda x: x.score, reverse=True)
        
        # Apply execution limits
        max_decisions_per_cycle = 3
        return filtered_decisions[:max_decisions_per_cycle]
    
    def _calculate_decision_confidence(self, decisions: List[TradingDecision]) -> float:
        """Decision confidence hisoblash"""
        if not decisions:
            return 0.0
        
        # Average confidence with quality weighting
        total_confidence = sum(d.confidence * d.score for d in decisions)
        total_weight = sum(d.score for d in decisions)
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    async def _create_execution_plan(self, decisions: List[TradingDecision]) -> Dict[str, Any]:
        """Execution plan yaratish"""
        plan = {
            "execution_order": [],
            "estimated_duration": 0,
            "risk_impact": 0.0,
            "commission_estimate": 0.0
        }
        
        for i, decision in enumerate(decisions):
            execution_item = {
                "decision_id": f"dec_{i}_{decision.timestamp.isoformat()}",
                "action": decision.action_type,
                "symbol": decision.symbol,
                "quantity": decision.quantity,
                "price": decision.price,
                "execution_mode": self.execution_mode,
                "delay": self.execution_delay * i,  # Staggered execution
                "estimated_commission": decision.quantity * decision.price * 0.001  # 0.1% commission
            }
            plan["execution_order"].append(execution_item)
        
        # Plan metrics
        plan["estimated_duration"] = len(decisions) * max(self.execution_delay, 1)
        plan["total_quantity"] = sum(d.quantity for d in decisions)
        plan["estimated_commission"] = sum(item["estimated_commission"] for item in plan["execution_order"])
        plan["risk_impact"] = np.mean([d.risk_score for d in decisions])
        
        return plan
    
    # Strategy implementations
    async def _momentum_strategy(self, market_data: Dict) -> List[Dict]:
        """Momentum strategy"""
        signals = []
        trends = market_data.get("trends", {})
        
        for symbol, trend in trends.items():
            if trend == "bullish":
                signals.append({
                    "symbol": symbol,
                    "action": "buy",
                    "confidence": 0.8,
                    "expected_return": 0.05,
                    "current_price": market_data.get("prices", {}).get(symbol, 1.0),
                    "reasoning": "Bullish momentum detected",
                    "strategy": "momentum"
                })
            elif trend == "bearish":
                signals.append({
                    "symbol": symbol,
                    "action": "sell",
                    "confidence": 0.75,
                    "expected_return": 0.04,
                    "current_price": market_data.get("prices", {}).get(symbol, 1.0),
                    "reasoning": "Bearish momentum detected",
                    "strategy": "momentum"
                })
        
        return signals
    
    async def _mean_reversion_strategy(self, market_data: Dict) -> List[Dict]:
        """Mean reversion strategy"""
        signals = []
        # Simplified mean reversion based on volatility
        volatility = market_data.get("volatility", {})
        
        for symbol, vol in volatility.items():
            if vol > 0.02:  # High volatility suggests mean reversion opportunity
                signals.append({
                    "symbol": symbol,
                    "action": "buy",  # Buy oversold, simplified
                    "confidence": 0.7,
                    "expected_return": 0.03,
                    "current_price": market_data.get("prices", {}).get(symbol, 1.0),
                    "reasoning": f"High volatility ({vol:.3f}) suggests mean reversion",
                    "strategy": "mean_reversion"
                })
        
        return signals
    
    async def _trend_following_strategy(self, market_data: Dict) -> List[Dict]:
        """Trend following strategy"""
        signals = []
        trends = market_data.get("trends", {})
        
        for symbol, trend in trends.items():
            if trend in ["bullish", "bearish"]:
                action = "buy" if trend == "bullish" else "sell"
                signals.append({
                    "symbol": symbol,
                    "action": action,
                    "confidence": 0.75,
                    "expected_return": 0.06,
                    "current_price": market_data.get("prices", {}).get(symbol, 1.0),
                    "reasoning": f"Following {trend} trend",
                    "strategy": "trend_following"
                })
        
        return signals
    
    async def _arbitrage_strategy(self, market_data: Dict) -> List[Dict]:
        """Arbitrage strategy"""
        signals = []
        # Simplified arbitrage based on price discrepancies
        prices = market_data.get("prices", {})
        
        # Mock arbitrage opportunity
        if "EURUSD" in prices and "GBPUSD" in prices:
            signals.append({
                "symbol": "EURGBP",  # Cross pair
                "action": "buy",
                "confidence": 0.9,
                "expected_return": 0.02,
                "current_price": prices["EURUSD"] / prices["GBPUSD"],
                "reasoning": "Cross-currency arbitrage opportunity",
                "strategy": "arbitrage"
            })
        
        return signals
    
    async def _breakout_strategy(self, market_data: Dict) -> List[Dict]:
        """Breakout strategy"""
        signals = []
        # Simplified breakout detection
        volatility = market_data.get("volatility", {})
        
        for symbol, vol in volatility.items():
            if vol < 0.01:  # Low volatility before breakout
                signals.append({
                    "symbol": symbol,
                    "action": "buy",
                    "confidence": 0.65,
                    "expected_return": 0.04,
                    "current_price": market_data.get("prices", {}).get(symbol, 1.0),
                    "reasoning": "Potential breakout from low volatility",
                    "strategy": "breakout"
                })
        
        return signals
    
    async def _contrarian_strategy(self, market_data: Dict) -> List[Dict]:
        """Contrarian strategy"""
        signals = []
        sentiment = market_data.get("sentiment_score", 0.5)
        
        if sentiment > 0.8:  # Euphoria - contrarian sell
            for symbol in market_data.get("trends", {}):
                signals.append({
                    "symbol": symbol,
                    "action": "sell",
                    "confidence": 0.6,
                    "expected_return": 0.03,
                    "current_price": market_data.get("prices", {}).get(symbol, 1.0),
                    "reasoning": "Contrarian: market euphoria",
                    "strategy": "contrarian"
                })
        elif sentiment < 0.2:  # Fear - contrarian buy
            for symbol in market_data.get("trends", {}):
                signals.append({
                    "symbol": symbol,
                    "action": "buy",
                    "confidence": 0.65,
                    "expected_return": 0.04,
                    "current_price": market_data.get("prices", {}).get(symbol, 1.0),
                    "reasoning": "Contrarian: market fear",
                    "strategy": "contrarian"
                })
        
        return signals
    
    async def execute_trade(self, decision: Dict) -> Dict[str, Any]:
        """Trade execution"""
        try:
            self.logger.info(f"Executing trade: {decision}")
            
            # Simulate trade execution
            execution_result = {
                "decision_id": f"exec_{datetime.now().isoformat()}",
                "status": "executed",
                "executed_quantity": decision.get("quantity", 0),
                "executed_price": decision.get("price", 0),
                "commission": decision.get("quantity", 0) * decision.get("price", 0) * 0.001,
                "pnl": decision.get("expected_return", 0) * decision.get("quantity", 0) * decision.get("price", 0),
                "timestamp": datetime.now()
            }
            
            # Store execution
            self.execution_history.append(execution_result)
            
            # Update active positions
            symbol = decision.get("symbol")
            action = decision.get("action_type")
            quantity = decision.get("quantity", 0)
            
            if symbol not in self.active_positions:
                self.active_positions[symbol] = 0
            
            if action == "buy":
                self.active_positions[symbol] += quantity
            elif action == "sell":
                self.active_positions[symbol] -= quantity
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Trade execution xatosi: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def change_strategy(self, decision: Dict) -> Dict[str, Any]:
        """Strategy o'zgartirish"""
        try:
            current_strategy = decision.get("current_strategy")
            new_strategy = decision.get("new_strategy")
            
            if new_strategy not in self.trading_strategies:
                raise ValueError(f"Invalid strategy: {new_strategy}")
            
            self.logger.info(f"Changing strategy from {current_strategy} to {new_strategy}")
            
            # Update strategy configuration
            result = {
                "change_id": f"strat_change_{datetime.now().isoformat()}",
                "from_strategy": current_strategy,
                "to_strategy": new_strategy,
                "reason": decision.get("reasoning", ""),
                "confidence": decision.get("confidence", 0.5),
                "timestamp": datetime.now()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Strategy change xatosi: {str(e)}")
            return {"error": str(e)}
    
    def get_active_positions(self) -> Dict[str, float]:
        """Active positions olish"""
        return self.active_positions.copy()
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """Decision statistics"""
        if not self.decision_history:
            return {"message": "No decisions available"}
        
        recent_decisions = list(self.decision_history)[-10:]  # Last 10 decisions
        
        total_decisions = len(self.decision_history)
        action_counts = defaultdict(int)
        avg_confidence = []
        
        for decision in recent_decisions:
            for d in decision.get("decisions", []):
                action_counts[d.get("action_type", "unknown")] += 1
                avg_confidence.append(d.get("confidence", 0))
        
        return {
            "total_decisions": total_decisions,
            "recent_decisions_count": len(recent_decisions),
            "action_distribution": dict(action_counts),
            "average_confidence": np.mean(avg_confidence) if avg_confidence else 0,
            "success_rate": self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Success rate calculation"""
        if not self.execution_history:
            return 0.0
        
        successful_executions = len([
            e for e in self.execution_history 
            if e.get("status") == "executed" and e.get("pnl", 0) > 0
        ])
        
        return successful_executions / len(self.execution_history)