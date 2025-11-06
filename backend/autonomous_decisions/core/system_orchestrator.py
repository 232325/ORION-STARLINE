"""
Autonomous Decision System Orchestrator

Bu modul butun tizimning asosiy qismi bo'lib,
Performance Feedback Loops va Autonomous Decision Making
komponentlarini boshqaradi.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

from ..performance_feedback.monitoring import PerformanceMonitor
from ..performance_feedback.attribution import PerformanceAttribution
from ..decision_making.trading_agent import TradingAgent
from ..decision_making.portfolio_manager import PortfolioManager
from ..governance.dao_integration import DAOGovernance
from .config_manager import ConfigManager
from .data_aggregator import DataAggregator
from .event_system import EventSystem

@dataclass
class SystemState:
    """Tizimning holati"""
    is_active: bool = False
    performance_score: float = 0.0
    total_trades: int = 0
    successful_trades: int = 0
    governance_pending: List[Dict] = None
    last_update: Optional[datetime] = None
    
    def __post_init__(self):
        if self.governance_pending is None:
            self.governance_pending = []
        if self.last_update is None:
            self.last_update = datetime.now()

class AutonomousDecisionSystem:
    """
    Asosiy tizim orchestrator
    
    Barcha komponentlarni muvofiqlashtiradi va
    real-time decision making ta'minlaydi
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.logger = self._setup_logging()
        self.config = ConfigManager(config)
        self.state = SystemState()
        
        # Boshqa komponentlarni initialize qilish
        self.data_aggregator = DataAggregator(self.config)
        self.event_system = EventSystem()
        
        # Performance feedback komponentlari
        self.performance_monitor = PerformanceMonitor(self.config)
        self.performance_attribution = PerformanceAttribution(self.config)
        
        # Decision making komponentlari
        self.trading_agent = TradingAgent(self.config)
        self.portfolio_manager = PortfolioManager(self.config)
        
        # Governance komponentlari
        self.dao_governance = DAOGovernance(self.config)
        
        # System monitoring
        self._initialize_monitoring()
        
        self.logger.info("AutonomousDecisionSystem initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Logging sozlash"""
        logger = logging.getLogger("autonomous_decisions")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_monitoring(self):
        """Tizim monitoringini boshlash"""
        self.event_system.subscribe("performance_update", self._handle_performance_update)
        self.event_system.subscribe("trade_executed", self._handle_trade_executed)
        self.event_system.subscribe("governance_vote", self._handle_governance_vote)
        
    def start(self):
        """Tizimni ishga tushirish"""
        if self.state.is_active:
            self.logger.warning("Tizim allaqachon ishga tushgan")
            return
        
        self.logger.info("AutonomousDecisionSystem starting...")
        
        # Barcha komponentlarni aktiv qilish
        self.performance_monitor.start()
        self.trading_agent.start()
        self.portfolio_manager.start()
        self.dao_governance.start()
        
        self.state.is_active = True
        self.state.last_update = datetime.now()
        
        self.logger.info("AutonomousDecisionSystem started successfully")
    
    def stop(self):
        """Tizimni to'xtatish"""
        if not self.state.is_active:
            self.logger.warning("Tizim allaqachon to'xtatilgan")
            return
        
        self.logger.info("AutonomousDecisionSystem stopping...")
        
        # Barcha komponentlarni to'xtatish
        self.performance_monitor.stop()
        self.trading_agent.stop()
        self.portfolio_manager.stop()
        self.dao_governance.stop()
        
        self.state.is_active = False
        self.state.last_update = datetime.now()
        
        self.logger.info("AutonomousDecisionSystem stopped")
    
    async def make_decision(self, market_data: Dict) -> Dict[str, Any]:
        """
        Asosiy decision making metod
        
        Market data asosida avtonom qaror qabul qiladi
        """
        if not self.state.is_active:
            raise RuntimeError("Tizim aktiv emas")
        
        try:
            # 1. Performance feedback olish
            performance_data = await self.performance_monitor.get_current_performance()
            
            # 2. Performance attribution analysis
            attribution = await self.performance_attribution.analyze_performance(performance_data)
            
            # 3. Portfolio holatini tekshirish
            portfolio_state = await self.portfolio_manager.get_current_state()
            
            # 4. Decision making
            decision = await self.trading_agent.make_decision(
                market_data=market_data,
                performance_data=performance_data,
                attribution=attribution,
                portfolio_state=portfolio_state
            )
            
            # 5. Governance approval kerakmi?
            if self._requires_governance_approval(decision):
                approval_result = await self._request_governance_approval(decision)
                decision["governance_approved"] = approval_result["approved"]
                decision["governance_vote_id"] = approval_result["vote_id"]
            
            # 6. Qarorni execute qilish
            if decision.get("execute", False):
                execution_result = await self._execute_decision(decision)
                decision["execution_result"] = execution_result
            
            self.state.last_update = datetime.now()
            return decision
            
        except Exception as e:
            self.logger.error(f"Decision making xatosi: {str(e)}")
            raise
    
    def _requires_governance_approval(self, decision: Dict) -> bool:
        """Governance approval kerakligini aniqlash"""
        large_trade_threshold = self.config.get("large_trade_threshold", 0.1)
        strategy_change_threshold = self.config.get("strategy_change_threshold", 0.05)
        
        # Katta trade yoki strategy o'zgarishi
        if decision.get("action_type") == "large_trade":
            return decision.get("trade_size", 0) > large_trade_threshold
        elif decision.get("action_type") == "strategy_change":
            return decision.get("confidence", 0) < strategy_change_threshold
        
        return False
    
    async def _request_governance_approval(self, decision: Dict) -> Dict:
        """Governance approval so'rash"""
        proposal = {
            "type": "trading_decision",
            "description": decision.get("description", ""),
            "parameters": decision,
            "requested_by": "autonomous_system",
            "timestamp": datetime.now().isoformat()
        }
        
        vote_id = await self.dao_governance.create_proposal(proposal)
        self.state.governance_pending.append({
            "vote_id": vote_id,
            "decision": decision,
            "created": datetime.now()
        })
        
        return {"approved": False, "vote_id": vote_id}
    
    async def _execute_decision(self, decision: Dict) -> Dict:
        """Qarorni execute qilish"""
        try:
            if decision.get("action_type") == "trade":
                result = await self.trading_agent.execute_trade(decision)
            elif decision.get("action_type") == "rebalance":
                result = await self.portfolio_manager.rebalance_portfolio(decision)
            elif decision.get("action_type") == "strategy_change":
                result = await self.trading_agent.change_strategy(decision)
            else:
                raise ValueError(f"Noma'lum action_type: {decision.get('action_type')}")
            
            # Execution event yuborish
            self.event_system.publish("decision_executed", {
                "decision": decision,
                "result": result,
                "timestamp": datetime.now()
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Decision execution xatosi: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _handle_performance_update(self, event_data: Dict):
        """Performance update event handler"""
        try:
            # Performance score ni yangilash
            self.state.performance_score = event_data.get("score", 0.0)
            
            # Agar performance pas bo'lsa, strategy optimizatsiyasi
            if self.state.performance_score < 0.7:  # Threshold
                self.logger.warning("Performance pas, optimizatsiya kerak")
                asyncio.create_task(self._optimize_strategies())
                
        except Exception as e:
            self.logger.error(f"Performance update handler xatosi: {str(e)}")
    
    def _handle_trade_executed(self, event_data: Dict):
        """Trade executed event handler"""
        try:
            self.state.total_trades += 1
            if event_data.get("success", False):
                self.state.successful_trades += 1
            
            # Trade statistics yangilash
            self.logger.info(f"Trade executed: {event_data}")
            
        except Exception as e:
            self.logger.error(f"Trade executed handler xatosi: {str(e)}")
    
    def _handle_governance_vote(self, event_data: Dict):
        """Governance vote event handler"""
        try:
            vote_id = event_data.get("vote_id")
            
            # Pending vote larni topish va yangilash
            for pending in self.state.governance_pending:
                if pending["vote_id"] == vote_id:
                    if event_data.get("approved", False):
                        # Vote qabul qilindi, qarorni execute qilish
                        asyncio.create_task(self._execute_pending_decision(pending["decision"]))
                    self.state.governance_pending.remove(pending)
                    break
                    
        except Exception as e:
            self.logger.error(f"Governance vote handler xatosi: {str(e)}")
    
    async def _optimize_strategies(self):
        """Strategy optimizatsiya"""
        try:
            self.logger.info("Strategy optimizatsiya boshlandi...")
            
            # Performance attribution asosida optimizatsiya
            optimization_result = await self.performance_attribution.optimize_strategies()
            
            if optimization_result.get("improvements"):
                await self.trading_agent.update_strategies(optimization_result["improvements"])
                self.logger.info("Strategy optimizatsiya tugallandi")
            
        except Exception as e:
            self.logger.error(f"Strategy optimizatsiya xatosi: {str(e)}")
    
    async def _execute_pending_decision(self, decision: Dict):
        """Pending qarorni execute qilish"""
        try:
            result = await self._execute_decision(decision)
            self.logger.info(f"Pending decision executed: {result}")
        except Exception as e:
            self.logger.error(f"Pending decision execution xatosi: {str(e)}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Tizim holatini olish"""
        return {
            "state": asdict(self.state),
            "config": self.config.get_all(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Performance summary olish"""
        return self.performance_monitor.get_summary()
    
    async def export_data(self, format_type: str = "json") -> str:
        """Ma'lumotlarni eksport qilish"""
        data = {
            "system_status": self.get_system_status(),
            "performance_summary": self.get_performance_summary(),
            "governance_pending": self.state.governance_pending
        }
        
        if format_type.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Qo'llab-quvvatlanmagan format: {format_type}")
