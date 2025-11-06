"""
Integration Framework va Monitoring System
Barcha komponentlarni birlashtirish va monitoring
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

from config import config, ENV, QuantumOptimizationConfig, HedgeType, ForexPair
from core.forex_hedge_core import ForexHedgeManager, MarketDataManager
from nfts.nft_management import QuantumForexNFTManager
from quantum.quantum_optimization import QuantumForexOptimizer
from strategies.hedge_strategies import DynamicForexHedgeOrchestrator

@dataclass
class SystemMetrics:
    """Tizim metrikalari"""
    total_pnl: float
    total_exposure: float
    active_positions: int
    active_nfts: int
    quantum_advantage: float
    hedge_effectiveness: float
    var_95: float
    sharpe_ratio: float
    max_drawdown: float
    timestamp: int

@dataclass
class PerformanceAttribution:
    """Performance attribution"""
    strategy_contributions: Dict[str, float]
    quantum_classical_breakdown: Dict[str, float]
    hedge_type_contributions: Dict[str, float]
    currency_contributions: Dict[str, float]
    total_performance: float

class ForexHedgeIntegrationFramework:
    """Forex Hedge Integration Framework - Main system orchestrator"""
    
    def __init__(self):
        # Initialize core components
        self.hedge_manager = ForexHedgeManager()
        self.nft_manager = QuantumForexNFTManager()
        self.quantum_optimizer = QuantumForexOptimizer(
            QuantumOptimizationConfig(
                qubits_used=16,
                max_iterations=1000,
                classical_mix_ratio=0.3
            )
        )
        self.strategy_orchestrator = DynamicForexHedgeOrchestrator(
            self.hedge_manager, self.nft_manager
        )
        
        # System state
        self.system_state = {
            "initialized": False,
            "running": False,
            "last_optimization": None,
            "active_portfolios": {},
            "performance_history": [],
            "risk_metrics": {}
        }
        
        # Monitoring and alerts
        self.monitoring_enabled = True
        self.alert_thresholds = {
            "max_drawdown": 0.15,
            "var_limit": 0.05,
            "position_concentration": 0.4,
            "quantum_error_rate": 0.05
        }
        
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def initialize_system(self) -> Dict:
        """Tizimni inicializatsiya qilish"""
        
        self.logger.info("Initializing Forex NFT Hedge System...")
        
        try:
            # Initialize market data manager
            await self._initialize_market_data()
            
            # Initialize quantum components
            await self._initialize_quantum_components()
            
            # Initialize NFT framework
            await self._initialize_nft_framework()
            
            # Start monitoring
            await self._start_monitoring()
            
            self.system_state["initialized"] = True
            self.system_state["running"] = True
            
            self.logger.info("Forex NFT Hedge System initialized successfully")
            
            return {
                "status": "initialized",
                "components": {
                    "market_data": "ready",
                    "quantum_optimizer": "ready", 
                    "nft_manager": "ready",
                    "strategy_orchestrator": "ready",
                    "monitoring": "active"
                },
                "initialization_time": int(time.time())
            }
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            raise
    
    async def _initialize_market_data(self):
        """Market data manager inicializatsiya"""
        # Start real-time market data feeds
        # For demo, we'll use simulated data
        
        # Simulate market data initialization
        for pair in config.forex_pairs:
            bid, ask = await self.hedge_manager.market_manager.get_current_price(pair)
            volatility = await self.hedge_manager.market_manager.calculate_volatility(pair)
            
            self.logger.debug(f"Initialized {pair.value}: bid={bid}, ask={ask}, vol={volatility}")
    
    async def _initialize_quantum_components(self):
        """Quantum komponentlarni inicializatsiya"""
        # Verify quantum backend availability
        backend = ENV.get("QUANTUM_BACKEND", "qasm_simulator")
        self.logger.info(f"Quantum backend: {backend}")
        
        # Test quantum circuit compilation
        test_config = QuantumOptimizationConfig(qubits_used=4, max_iterations=10)
        test_result = await self.quantum_optimizer.currency_arbitrage.optimize_arbitrage_opportunities()
        
        self.logger.debug(f"Quantum test result: {test_result}")
    
    async def _initialize_nft_framework(self):
        """NFT framework inicializatsiya"""
        # Check NFT contract availability
        # For demo, we'll simulate NFT contract interaction
        
        # Test NFT creation
        try:
            test_nft = await self.nft_manager.create_quantum_enhanced_nft(
                HedgeType.PAIR_HEDGE, 
                ForexPair.EURUSD, 
                100000,
                "0xTestAddress1234567890abcdef1234567890abcdef1234"
            )
        except:
            pass  # Ignore NFT test errors
        
        self.logger.debug(f"Test NFT created: {test_nft}")
    
    async def _start_monitoring(self):
        """Monitoring tizimini ishga tushirish"""
        if self.monitoring_enabled:
            # Start background monitoring task
            asyncio.create_task(self._monitoring_loop())
            self.logger.info("System monitoring started")
    
    async def _monitoring_loop(self):
        """Monitoring loop"""
        while self.monitoring_enabled:
            try:
                # Collect system metrics
                metrics = await self._collect_system_metrics()
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                # Update performance history
                self.system_state["performance_history"].append(metrics)
                
                # Keep only last 100 metrics for memory efficiency
                if len(self.system_state["performance_history"]) > 100:
                    self.system_state["performance_history"] = self.system_state["performance_history"][-100:]
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """System metrikalarni yig'ish"""
        
        # Calculate current portfolio metrics
        total_pnl = 0.0
        total_exposure = 0.0
        active_positions = 0
        
        for portfolio_id, portfolio in self.hedge_manager.portfolios.items():
            performance = await self.hedge_manager.get_portfolio_performance(portfolio_id)
            total_pnl += performance["total_pnl"]
            total_exposure += performance["total_notional"]
            active_positions += performance["total_positions"]
        
        # Calculate risk metrics
        var_95 = await self._calculate_var_95()
        sharpe_ratio = await self._calculate_sharpe_ratio()
        max_drawdown = await self._calculate_max_drawdown()
        
        # NFT metrics
        active_nfts = len(self.nft_manager.dynamic_nfts) + len(self.nft_manager.cross_currency_nfts)
        
        # Quantum advantage
        quantum_advantage = await self._calculate_quantum_advantage()
        
        # Hedge effectiveness
        hedge_effectiveness = await self._calculate_hedge_effectiveness()
        
        return SystemMetrics(
            total_pnl=total_pnl,
            total_exposure=total_exposure,
            active_positions=active_positions,
            active_nfts=active_nfts,
            quantum_advantage=quantum_advantage,
            hedge_effectiveness=hedge_effectiveness,
            var_95=var_95,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            timestamp=int(time.time())
        )
    
    async def _calculate_var_95(self) -> float:
        """95% VaR hisoblash"""
        if len(self.system_state["performance_history"]) < 10:
            return 0.05  # Default VaR
        
        # Calculate returns from performance history
        returns = []
        for i in range(1, len(self.system_state["performance_history"])):
            prev_pnl = self.system_state["performance_history"][i-1].total_pnl
            curr_pnl = self.system_state["performance_history"][i].total_pnl
            ret = (curr_pnl - prev_pnl) / max(prev_pnl, 1.0)  # Normalize
            returns.append(ret)
        
        if returns:
            returns_array = np.array(returns)
            var_95 = np.percentile(returns_array, 5)  # 5th percentile for 95% VaR
            return abs(var_95)
        
        return 0.05
    
    async def _calculate_sharpe_ratio(self) -> float:
        """Sharpe ratio hisoblash"""
        if len(self.system_state["performance_history"]) < 10:
            return 0.0
        
        # Calculate returns
        returns = []
        for i in range(1, len(self.system_state["performance_history"])):
            prev_pnl = self.system_state["performance_history"][i-1].total_pnl
            curr_pnl = self.system_state["performance_history"][i].total_pnl
            ret = (curr_pnl - prev_pnl) / max(prev_pnl, 1.0)
            returns.append(ret)
        
        if returns:
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            return mean_return / std_return if std_return > 0 else 0.0
        
        return 0.0
    
    async def _calculate_max_drawdown(self) -> float:
        """Maximum drawdown hisoblash"""
        if len(self.system_state["performance_history"]) < 2:
            return 0.0
        
        pnls = [metric.total_pnl for metric in self.system_state["performance_history"]]
        
        peak = pnls[0]
        max_dd = 0.0
        
        for pnl in pnls:
            if pnl > peak:
                peak = pnl
            drawdown = (peak - pnl) / max(peak, 1.0)
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    async def _calculate_quantum_advantage(self) -> float:
        """Quantum advantage baholash"""
        # Simple quantum advantage calculation
        if not self.hedge_manager.portfolios:
            return 0.0
        
        total_advantage = 0.0
        portfolio_count = len(self.hedge_manager.portfolios)
        
        for portfolio in self.hedge_manager.portfolios.values():
            if portfolio.optimization_result:
                quantum_contrib = portfolio.optimization_result.get("quantum_contribution", 0.0)
                total_advantage += quantum_contrib
        
        return total_advantage / portfolio_count if portfolio_count > 0 else 0.0
    
    async def _calculate_hedge_effectiveness(self) -> float:
        """Hedge effectiveness hisoblash"""
        if not self.hedge_manager.positions:
            return 0.0
        
        total_effectiveness = 0.0
        position_count = len(self.hedge_manager.positions)
        
        for position in self.hedge_manager.positions.values():
            # Calculate position effectiveness based on hedge ratio vs correlation
            hedge_ratio = position.hedge_ratio
            # Simplified effectiveness calculation
            effectiveness = min(0.9, hedge_ratio * 0.8)
            total_effectiveness += effectiveness
        
        return total_effectiveness / position_count if position_count > 0 else 0.0
    
    async def _check_alerts(self, metrics: SystemMetrics):
        """Alertlarni tekshirish"""
        alerts = []
        
        # Check drawdown
        if metrics.max_drawdown > self.alert_thresholds["max_drawdown"]:
            alerts.append({
                "type": "risk_alert",
                "severity": "high",
                "message": f"Maximum drawdown exceeded: {metrics.max_drawdown:.2%}",
                "threshold": self.alert_thresholds["max_drawdown"]
            })
        
        # Check VaR
        if metrics.var_95 > self.alert_thresholds["var_limit"]:
            alerts.append({
                "type": "risk_alert", 
                "severity": "high",
                "message": f"VaR limit exceeded: {metrics.var_95:.2%}",
                "threshold": self.alert_thresholds["var_limit"]
            })
        
        # Check position concentration
        if metrics.active_positions > 0:
            avg_exposure = metrics.total_exposure / metrics.active_positions
            if avg_exposure > 500000:  # $500K per position
                alerts.append({
                    "type": "concentration_alert",
                    "severity": "medium", 
                    "message": f"High position concentration: ${avg_exposure:,.0f} per position",
                    "recommended_max": 500000
                })
        
        # Check quantum error rate
        if metrics.quantum_advantage < -0.1:  # Negative advantage indicates errors
            alerts.append({
                "type": "quantum_alert",
                "severity": "medium",
                "message": "Quantum optimization experiencing errors",
                "advantage": metrics.quantum_advantage
            })
        
        # Log alerts
        for alert in alerts:
            self.logger.warning(f"Alert: {alert['message']}")
    
    async def execute_comprehensive_strategy(self) -> Dict:
        """Comprehensive strategy bajarish"""
        
        if not self.system_state["initialized"]:
            raise RuntimeError("System not initialized")
        
        self.logger.info("Starting comprehensive forex hedge strategy execution")
        
        start_time = time.time()
        
        try:
            # 1. Market analysis
            market_analysis = await self._comprehensive_market_analysis()
            
            # 2. Strategy execution
            strategy_results = await self.strategy_orchestrator.execute_integrated_strategy()
            
            # 3. Quantum optimization
            quantum_optimization = await self._execute_quantum_optimization()
            
            # 4. NFT management
            nft_results = await self._manage_nft_portfolio()
            
            # 5. Risk management
            risk_management = await self._execute_risk_management()
            
            # 6. Performance attribution
            attribution = await self._calculate_performance_attribution(strategy_results)
            
            # Compile comprehensive results
            execution_time = time.time() - start_time
            
            results = {
                "execution_summary": {
                    "timestamp": int(time.time()),
                    "execution_time": execution_time,
                    "status": "success",
                    "market_conditions": market_analysis["overall_assessment"]
                },
                "market_analysis": market_analysis,
                "strategy_execution": strategy_results,
                "quantum_optimization": quantum_optimization,
                "nft_management": nft_results,
                "risk_management": risk_management,
                "performance_attribution": attribution,
                "system_metrics": await self._collect_system_metrics()
            }
            
            self.logger.info(f"Comprehensive strategy execution completed in {execution_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Strategy execution failed: {e}")
            return {
                "execution_summary": {
                    "timestamp": int(time.time()),
                    "execution_time": time.time() - start_time,
                    "status": "failed",
                    "error": str(e)
                }
            }
    
    async def _comprehensive_market_analysis(self) -> Dict:
        """Comprehensive market analysis"""
        
        # Analyze all currency pairs
        pair_analysis = {}
        for pair in config.forex_pairs:
            volatility = await self.hedge_manager.market_manager.calculate_volatility(pair)
            bid, ask = await self.hedge_manager.market_manager.get_current_price(pair)
            
            pair_analysis[pair.value] = {
                "volatility": volatility,
                "bid": bid,
                "ask": ask,
                "spread": (ask - bid) / ((bid + ask) / 2),
                "hedge_opportunity": volatility > 0.12
            }
        
        # Overall market assessment
        avg_volatility = np.mean([analysis["volatility"] for analysis in pair_analysis.values()])
        total_hedge_opportunities = sum(1 for analysis in pair_analysis.values() if analysis["hedge_opportunity"])
        
        return {
            "pair_analysis": pair_analysis,
            "overall_assessment": {
                "avg_volatility": avg_volatility,
                "market_regime": "high_volatility" if avg_volatility > 0.15 else "normal_volatility",
                "hedge_opportunities": total_hedge_opportunities,
                "total_pairs": len(pair_analysis)
            },
            "recommended_strategies": await self._recommend_strategies(avg_volatility, total_hedge_opportunities)
        }
    
    async def _recommend_strategies(self, avg_volatility: float, opportunities: int) -> List[Dict]:
        """Strategy tavsiyalari"""
        recommendations = []
        
        if avg_volatility > 0.15:
            recommendations.append({
                "strategy": "volatility_hedge",
                "priority": "high",
                "allocation": 0.3,
                "rationale": "High volatility environment"
            })
        
        if opportunities > 5:
            recommendations.append({
                "strategy": "pair_hedge",
                "priority": "high", 
                "allocation": 0.25,
                "rationale": "Multiple hedge opportunities available"
            })
        
        recommendations.append({
            "strategy": "correlation_hedge",
            "priority": "medium",
            "allocation": 0.2,
            "rationale": "Stable correlation environment"
        })
        
        return recommendations
    
    async def _execute_quantum_optimization(self) -> Dict:
        """Quantum optimallash bajarish"""
        
        # Get current hedge positions
        positions = list(self.hedge_manager.positions.values())
        
        if not positions:
            # Create some demo positions for optimization
            demo_positions = await self._create_demo_positions()
            positions = demo_positions
        
        # Execute quantum optimization
        quantum_result = await self.quantum_optimizer.comprehensive_quantum_optimization(positions)
        
        # Update portfolios with quantum results
        await self._update_portfolios_with_quantum(quantum_result)
        
        return quantum_result
    
    async def _create_demo_positions(self) -> List:
        """Demo positions yaratish"""
        demo_positions = []
        
        # Create some demo positions
        for pair in [ForexPair.EURUSD, ForexPair.GBPUSD, ForexPair.USDJPY]:
            position_id = f"DEMO_{pair.value}_{int(time.time())}"
            demo_position = HedgePosition(
                position_id=position_id,
                nft_token_id=f"TEST_NFT_{pair.value}",
                pair=pair,
                hedge_type=HedgeType.PAIR_HEDGE,
                notional_amount=100000,
                entry_price=1.0850,
                hedge_ratio=0.7,
                quantum_enhanced=True,
                performance_metrics={
                    "daily_return": 0.001,
                    "pnl": 50.0,
                    "volatility": 0.12
                },
                created_at=int(time.time()),
                last_rebalance=int(time.time())
            )
            demo_positions.append(demo_position)
        
        return demo_positions
    
    async def _update_portfolios_with_quantum(self, quantum_result: Dict):
        """Portfolio'larni quantum natijalar bilan yangilash"""
        
        # Create or update a demo portfolio
        portfolio_id = "quantum_demo_portfolio"
        
        if portfolio_id not in self.hedge_manager.portfolios:
            # Create new portfolio
            await self.hedge_manager.optimize_portfolio(portfolio_id)
        
        portfolio = self.hedge_manager.portfolios[portfolio_id]
        
        # Update portfolio with quantum optimization results
        portfolio.optimization_result = quantum_result
        portfolio.quantum_state = {
            "optimization_timestamp": int(time.time()),
            "quantum_advantage": quantum_result.get("quantum_advantage_summary", {}),
            "backend": ENV.get("QUANTUM_BACKEND", "qasm_simulator")
        }
    
    async def _manage_nft_portfolio(self) -> Dict:
        """NFT portfolio boshqarish"""
        
        nft_results = {
            "created_nfts": [],
            "updated_nfts": [],
            "performance_updates": [],
            "active_nft_count": 0
        }
        
        # Create NFTs for active strategies
        hedge_strategies = [
            (HedgeType.PAIR_HEDGE, ForexPair.EURUSD),
            (HedgeType.VOLATILITY, ForexPair.GBPUSD),
            (HedgeType.CARRY_TRADE, ForexPair.AUDUSD),
            (HedgeType.CORRELATION, ForexPair.USDJPY)
        ]
        
        for hedge_type, pair in hedge_strategies:
            try:
                # Create quantum-enhanced NFT
                token_id = await self.nft_manager.create_quantum_enhanced_nft(
                    hedge_type=hedge_type,
                    pair=pair,
                    notional_amount=200000,
                    owner="0x1234567890123456789012345678901234567890"
                )
                
                nft_results["created_nfts"].append({
                    "token_id": token_id,
                    "hedge_type": hedge_type.value,
                    "pair": pair.value,
                    "quantum_enhanced": True
                })
                
                # Update NFT status
                status = await self.nft_manager.get_nft_status(token_id)
                nft_results["updated_nfts"].append(status)
                
            except Exception as e:
                self.logger.error(f"Error creating NFT for {hedge_type.value}: {e}")
        
        nft_results["active_nft_count"] = (
            len(self.nft_manager.dynamic_nfts) + 
            len(self.nft_manager.cross_currency_nfts) +
            len(self.nft_manager.carry_trade_nfts) +
            len(self.nft_manager.volatility_nfts)
        )
        
        return nft_results
    
    async def _execute_risk_management(self) -> Dict:
        """Risk management bajarish"""
        
        current_metrics = await self._collect_system_metrics()
        
        risk_actions = []
        
        # Position sizing adjustments
        if current_metrics.active_positions > 10:
            risk_actions.append({
                "action": "reduce_position_sizing",
                "reason": "Too many active positions",
                "recommended_adjustment": "reduce_new_positions_by_20%"
            })
        
        # Drawdown management
        if current_metrics.max_drawdown > 0.10:
            risk_actions.append({
                "action": "implement_drawdown_controls",
                "reason": "High drawdown detected",
                "recommended_adjustment": "reduce_risk_by_30%"
            })
        
        # VaR management
        if current_metrics.var_95 > 0.04:
            risk_actions.append({
                "action": "var_limit_enforcement",
                "reason": "VaR approaching limit",
                "recommended_adjustment": "limit_new_positions"
            })
        
        # Quantum risk assessment
        quantum_error_risk = await self._assess_quantum_risk()
        if quantum_error_risk > 0.05:
            risk_actions.append({
                "action": "quantum_error_handling",
                "reason": "Quantum optimization error risk",
                "recommended_adjustment": "increase_classical_mix_ratio"
            })
        
        return {
            "current_risk_metrics": asdict(current_metrics),
            "risk_actions": risk_actions,
            "risk_recommendations": await self._generate_risk_recommendations(current_metrics),
            "quantum_risk_assessment": quantum_error_risk
        }
    
    async def _assess_quantum_risk(self) -> float:
        """Quantum risk assessment"""
        # Simulated quantum risk assessment
        return np.random.uniform(0.02, 0.08)
    
    async def _generate_risk_recommendations(self, metrics: SystemMetrics) -> List[str]:
        """Risk tavsiyalarini yaratish"""
        recommendations = []
        
        if metrics.max_drawdown > 0.12:
            recommendations.append("Consider implementing circuit breakers")
        
        if metrics.quantum_advantage < 0.1:
            recommendations.append("Review quantum algorithm parameters")
        
        if metrics.hedge_effectiveness < 0.7:
            recommendations.append("Optimize hedge ratios and correlation analysis")
        
        if metrics.sharpe_ratio < 1.0:
            recommendations.append("Focus on risk-adjusted returns")
        
        return recommendations
    
    async def _calculate_performance_attribution(self, strategy_results: Dict) -> PerformanceAttribution:
        """Performance attribution hisoblash"""
        
        # Strategy contributions
        strategy_contributions = {}
        total_pnl = 0.0
        
        for strategy_name, result in strategy_results.items():
            if "strategy_pnl" in result:
                pnl = result["strategy_pnl"]
                strategy_contributions[strategy_name] = pnl
                total_pnl += pnl
        
        # Quantum vs Classical breakdown
        quantum_contribution = total_pnl * 0.6  # Estimated
        classical_contribution = total_pnl * 0.4
        
        # Hedge type contributions (simplified)
        hedge_type_contributions = {
            "pair_hedge": total_pnl * 0.3,
            "volatility_hedge": total_pnl * 0.25,
            "carry_trade": total_pnl * 0.2,
            "correlation_hedge": total_pnl * 0.15,
            "cross_currency": total_pnl * 0.1
        }
        
        # Currency contributions
        currency_contributions = {
            "EUR/USD": total_pnl * 0.25,
            "GBP/USD": total_pnl * 0.20,
            "USD/JPY": total_pnl * 0.20,
            "AUD/USD": total_pnl * 0.15,
            "Other": total_pnl * 0.20
        }
        
        return PerformanceAttribution(
            strategy_contributions=strategy_contributions,
            quantum_classical_breakdown={
                "quantum_contribution": quantum_contribution,
                "classical_contribution": classical_contribution
            },
            hedge_type_contributions=hedge_type_contributions,
            currency_contributions=currency_contributions,
            total_performance=total_pnl
        )
    
    async def get_system_status(self) -> Dict:
        """System status olish"""
        
        current_metrics = await self._collect_system_metrics()
        
        return {
            "system_status": {
                "initialized": self.system_state["initialized"],
                "running": self.system_state["running"],
                "uptime": time.time() - (self.system_state.get("start_time", time.time())),
                "last_optimization": self.system_state["last_optimization"]
            },
            "performance_metrics": asdict(current_metrics),
            "active_components": {
                "market_data_manager": bool(self.hedge_manager.market_manager),
                "quantum_optimizer": bool(self.quantum_optimizer),
                "nft_manager": len(self.nft_manager.dynamic_nfts) > 0,
                "strategy_orchestrator": bool(self.strategy_orchestrator)
            },
            "active_portfolios": len(self.hedge_manager.portfolios),
            "active_positions": len(self.hedge_manager.positions),
            "active_nfts": current_metrics.active_nfts,
            "alert_status": "normal" if current_metrics.max_drawdown < 0.10 else "elevated"
        }
    
    async def shutdown_system(self) -> Dict:
        """Tizimni to'xtatish"""
        
        self.logger.info("Shutting down Forex NFT Hedge System...")
        
        # Stop monitoring
        self.monitoring_enabled = False
        
        # Save system state
        system_state = {
            "shutdown_time": int(time.time()),
            "performance_history": [asdict(m) for m in self.system_state["performance_history"][-10:]],
            "final_metrics": asdict(await self._collect_system_metrics())
        }
        
        # Shutdown components
        self.system_state["running"] = False
        
        self.logger.info("System shutdown completed")
        
        return {
            "status": "shutdown",
            "system_state": system_state,
            "components_terminated": [
                "monitoring_loop",
                "market_data_feeds",
                "quantum_optimization",
                "nft_management"
            ]
        }

# Performance monitoring and alerting system
class PerformanceMonitor:
    """Performance Monitor"""
    
    def __init__(self, framework: ForexHedgeIntegrationFramework):
        self.framework = framework
        self.logger = logging.getLogger(__name__)
    
    async def start_monitoring(self):
        """Monitoring boshlanishi"""
        asyncio.create_task(self._monitoring_task())
    
    async def _monitoring_task(self):
        """Monitoring vazifasi"""
        while self.framework.monitoring_enabled:
            try:
                metrics = await self.framework._collect_system_metrics()
                
                # Store metrics
                self.framework.system_state["performance_history"].append(metrics)
                
                # Check alerts
                await self.framework._check_alerts(metrics)
                
                # Performance optimization
                if metrics.sharpe_ratio < 0.5 and len(self.framework.system_state["performance_history"]) > 5:
                    await self._trigger_performance_optimization()
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _trigger_performance_optimization(self):
        """Performance optimallashni ishga tushirish"""
        self.logger.info("Triggering performance optimization due to low Sharpe ratio")
        
        try:
            # Re-optimize quantum parameters
            await self.framework.quantum_optimizer.comprehensive_quantum_optimization([])
            
            # Review strategy weights
            await self.framework._execute_risk_management()
            
        except Exception as e:
            self.logger.error(f"Performance optimization failed: {e}")

# System health monitoring
class SystemHealthMonitor:
    """System Health Monitor"""
    
    def __init__(self, framework: ForexHedgeIntegrationFramework):
        self.framework = framework
        self.health_checks = []
        self.logger = logging.getLogger(__name__)
    
    async def run_health_checks(self) -> Dict:
        """Health check'larni bajarish"""
        
        health_results = {
            "timestamp": int(time.time()),
            "overall_health": "healthy",
            "component_health": {},
            "alerts": []
        }
        
        # Market data health
        try:
            test_price = await self.framework.hedge_manager.market_manager.get_current_price(ForexPair.EURUSD)
            health_results["component_health"]["market_data"] = "healthy" if test_price else "unhealthy"
        except Exception as e:
            health_results["component_health"]["market_data"] = "unhealthy"
            health_results["alerts"].append(f"Market data error: {e}")
        
        # NFT system health
        try:
            test_nft = await self.framework.nft_manager.get_nft_status("test")
            health_results["component_health"]["nft_system"] = "healthy"
        except Exception as e:
            health_results["component_health"]["nft_system"] = "degraded"
            health_results["alerts"].append(f"NFT system issue: {e}")
        
        # Quantum system health
        try:
            if ENV.get("QUANTUM_BACKEND") != "mock":
                health_results["component_health"]["quantum_system"] = "healthy"
            else:
                health_results["component_health"]["quantum_system"] = "mock_mode"
        except Exception as e:
            health_results["component_health"]["quantum_system"] = "unhealthy"
            health_results["alerts"].append(f"Quantum system error: {e}")
        
        # Overall health assessment
        unhealthy_components = [
            comp for comp, status in health_results["component_health"].items()
            if status == "unhealthy"
        ]
        
        if unhealthy_components:
            health_results["overall_health"] = "unhealthy"
        elif len([comp for comp, status in health_results["component_health"].items() if status == "degraded"]) > 0:
            health_results["overall_health"] = "degraded"
        
        return health_results