"""
AI Agent Controller - Orion Starline AI Trading System
======================================================

Asosiy AI agentlarni boshqaruvchi tizim. Bu modul observe()->decide()->act() siklini
amalga oshiradi va barcha AI agentlarini muvofiqlashtiradi.

Features:
- Event-driven architecture
- Agent state management
- Cross-agent communication
- Autonomous decision making
- Performance monitoring
- Health checks & failover
- Load balancing & scaling
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import threading
import queue
import uuid
from collections import defaultdict, deque
import weakref


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent status enumeration"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    FAILOVER = "failover"


class EventType(Enum):
    """Event types for event-driven architecture"""
    MARKET_DATA_UPDATE = "market_data_update"
    RISK_ALERT = "risk_alert"
    SIGNAL_GENERATED = "signal_generated"
    DECISION_REQUEST = "decision_request"
    HEALTH_CHECK = "health_check"
    PERFORMANCE_UPDATE = "performance_update"
    AGENT_STATUS_CHANGE = "agent_status_change"
    CROSS_AGENT_COMMUNICATION = "cross_agent_communication"
    SYSTEM_ERROR = "system_error"


@dataclass
class AgentState:
    """Agent state management"""
    agent_id: str
    status: AgentStatus
    last_activity: datetime
    performance_score: float
    load_factor: float
    error_count: int
    success_count: int
    memory_usage: float
    cpu_usage: float
    response_time_avg: float
    health_check_interval: int = 30
    last_health_check: Optional[datetime] = None


@dataclass
class Event:
    """Event data structure"""
    event_id: str
    event_type: EventType
    source_agent: str
    target_agent: Optional[str]
    timestamp: datetime
    data: Dict[str, Any]
    priority: int = 5  # 1-10 scale, 10 being highest
    retry_count: int = 0
    max_retries: int = 3


class EventBus:
    """Event-driven communication bus"""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_queue = queue.PriorityQueue()
        self.processing = False
        self._lock = threading.Lock()
        
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to event type"""
        with self._lock:
            self.subscribers[event_type].append(callback)
            
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from event type"""
        with self._lock:
            if callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)
                
    def publish(self, event: Event):
        """Publish event to subscribers"""
        # Add negative priority for proper queue ordering with unique counter
        import time
        unique_id = time.time_ns()  # nanosecond timestamp for uniqueness
        self.event_queue.put((-event.priority, unique_id, event))
        
    def start_processing(self):
        """Start event processing"""
        if not self.processing:
            self.processing = True
            threading.Thread(target=self._process_events, daemon=True).start()
            
    def _process_events(self):
        """Process events from queue"""
        while self.processing:
            try:
                priority, unique_id, event = self.event_queue.get(timeout=1)
                self._handle_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                
    def _handle_event(self, event: Event):
        """Handle individual event"""
        try:
            for callback in self.subscribers[event.event_type]:
                callback(event)
        except Exception as e:
            logger.error(f"Error handling event {event.event_id}: {e}")


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.state = AgentState(
            agent_id=agent_id,
            status=AgentStatus.INACTIVE,
            last_activity=datetime.now(),
            performance_score=0.0,
            load_factor=0.0,
            error_count=0,
            success_count=0,
            memory_usage=0.0,
            cpu_usage=0.0,
            response_time_avg=0.0
        )
        self.event_bus = None
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        self._message_handlers: Dict[EventType, Callable] = {}
        self._observers: List[Callable] = []
        
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for communication"""
        self.event_bus = event_bus
        event_bus.subscribe(EventType.CROSS_AGENT_COMMUNICATION, self._handle_message)
        
    def register_observer(self, observer: Callable):
        """Register observer for state changes"""
        self._observers.append(observer)
        
    @abstractmethod
    async def observe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Observe phase of ODA cycle - gather data"""
        pass
        
    @abstractmethod
    async def decide(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Decide phase of ODA cycle - make decisions"""
        pass
        
    @abstractmethod
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Act phase of ODA cycle - execute actions"""
        pass
        
    async def process_cycle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete ODA cycle"""
        start_time = time.time()
        
        try:
            self.state.status = AgentStatus.BUSY
            self._notify_observers()
            
            # Observe phase
            observation = await self.observe(input_data)
            
            # Decide phase
            decision = await self.decide(observation)
            
            # Act phase
            result = await self.act(decision)
            
            # Update performance metrics
            self._update_success_metrics(time.time() - start_time)
            
            self.state.status = AgentStatus.ACTIVE
            self._notify_observers()
            
            return result
            
        except Exception as e:
            self._update_error_metrics(str(e))
            self.state.status = AgentStatus.ERROR
            self._notify_observers()
            raise
            
    def _update_success_metrics(self, response_time: float):
        """Update success metrics"""
        self.state.success_count += 1
        self.state.last_activity = datetime.now()
        
        # Update average response time
        if self.state.response_time_avg == 0:
            self.state.response_time_avg = response_time
        else:
            self.state.response_time_avg = (self.state.response_time_avg + response_time) / 2
            
        # Update performance score
        self.state.performance_score = min(100, (self.state.success_count / 
                                               (self.state.success_count + self.state.error_count)) * 100)
        
    def _update_error_metrics(self, error_msg: str):
        """Update error metrics"""
        self.state.error_count += 1
        self.state.last_activity = datetime.now()
        self.logger.error(f"Agent {self.agent_id} error: {error_msg}")
        
    def _notify_observers(self):
        """Notify observers of state changes"""
        for observer in self._observers:
            try:
                observer(self.state)
            except Exception as e:
                self.logger.error(f"Error notifying observer: {e}")
                
    def _handle_message(self, event: Event):
        """Handle incoming messages"""
        if event.target_agent == self.agent_id:
            handler = self._message_handlers.get(event.event_type)
            if handler:
                handler(event)
                
    def send_message(self, target_agent: str, event_type: EventType, data: Dict[str, Any], priority: int = 5):
        """Send message to another agent"""
        if self.event_bus:
            event = Event(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                source_agent=self.agent_id,
                target_agent=target_agent,
                timestamp=datetime.now(),
                data=data,
                priority=priority
            )
            self.event_bus.publish(event)
            
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        current_time = datetime.now()
        
        # Check if agent is responsive
        time_since_activity = (current_time - self.state.last_activity).total_seconds()
        
        health_data = {
            "agent_id": self.agent_id,
            "status": self.state.status.value,
            "last_activity": self.state.last_activity.isoformat(),
            "time_since_activity": time_since_activity,
            "performance_score": self.state.performance_score,
            "load_factor": self.state.load_factor,
            "error_rate": self.state.error_count / max(1, self.state.success_count + self.state.error_count),
            "response_time_avg": self.state.response_time_avg,
            "health_status": "healthy" if time_since_activity < 60 else "stale"
        }
        
        self.state.last_health_check = current_time
        return health_data
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        return {
            "agent_id": self.agent_id,
            "status": self.state.status.value,
            "performance_score": self.state.performance_score,
            "success_count": self.state.success_count,
            "error_count": self.state.error_count,
            "success_rate": self.state.success_count / max(1, self.state.success_count + self.state.error_count),
            "average_response_time": self.state.response_time_avg,
            "load_factor": self.state.load_factor,
            "last_activity": self.state.last_activity.isoformat(),
            "memory_usage": self.state.memory_usage,
            "cpu_usage": self.state.cpu_usage
        }


class GPTAgent(BaseAgent):
    """GPT Assistant Agent - natural language processing and decision support"""
    
    def __init__(self, agent_id: str = "gpt_assistant", config: Optional[Dict] = None):
        default_config = {
            "model_name": "gpt-4",
            "max_tokens": 2000,
            "temperature": 0.7,
            "context_length": 8000,
            "analysis_depth": "comprehensive"
        }
        if config:
            default_config.update(config)
        super().__init__(agent_id, default_config)
        
        # Register message handlers
        self._message_handlers[EventType.DECISION_REQUEST] = self._handle_decision_request
        self._message_handlers[EventType.MARKET_DATA_UPDATE] = self._handle_market_data
        self._message_handlers[EventType.SIGNAL_GENERATED] = self._handle_signal
        
    async def observe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Observe market data and generate insights"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        observations = {
            "market_sentiment": self._analyze_sentiment(data),
            "trend_analysis": self._analyze_trends(data),
            "risk_assessment": self._assess_risks(data),
            "opportunity_identification": self._identify_opportunities(data),
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"GPT Agent observed {len(data)} data points")
        return observations
        
    async def decide(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Make intelligent decisions based on observations"""
        await asyncio.sleep(0.15)  # Simulate decision processing
        
        decision_factors = {
            "confidence_level": self._calculate_confidence(observation),
            "recommended_actions": self._generate_recommendations(observation),
            "risk_level": observation.get("risk_assessment", {}).get("overall_risk", 50),
            "market_timing": self._evaluate_timing(observation),
            "decision_rationale": self._generate_rationale(observation)
        }
        
        decision = {
            "decision_type": "market_analysis",
            "factors": decision_factors,
            "urgency": self._assess_urgency(observation),
            "timestamp": datetime.now().isoformat()
        }
        
        return decision
        
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute actions based on decisions"""
        await asyncio.sleep(0.05)  # Simulate action execution
        
        actions_taken = []
        
        # Send analysis results
        if decision.get("factors", {}).get("recommended_actions"):
            self.send_message(
                target_agent="controller",
                event_type=EventType.PERFORMANCE_UPDATE,
                data={
                    "action": "recommendation_generated",
                    "recommendations": decision["factors"]["recommended_actions"],
                    "confidence": decision["factors"]["confidence_level"]
                }
            )
            actions_taken.append("recommendation_sent")
            
        # Notify other agents
        if decision.get("urgency") > 7:
            self.send_message(
                target_agent="risk_agent",
                event_type=EventType.DECISION_REQUEST,
                data={"urgency": decision["urgency"], "context": decision},
                priority=8
            )
            actions_taken.append("high_priority_alert")
            
        return {
            "actions_taken": actions_taken,
            "decision_implemented": True,
            "impact_assessment": self._assess_impact(decision),
            "timestamp": datetime.now().isoformat()
        }
        
    def _analyze_sentiment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market sentiment from data"""
        # Simulate sentiment analysis
        return {
            "overall_sentiment": "neutral",
            "confidence": 0.75,
            "fear_greed_index": 52,
            "news_sentiment": 0.65,
            "social_sentiment": 0.58
        }
        
    def _analyze_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market trends"""
        return {
            "short_term_trend": "upward",
            "medium_term_trend": "sideways",
            "long_term_trend": "upward",
            "trend_strength": 0.72,
            "reversal_probability": 0.25
        }
        
    def _assess_risks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market risks"""
        return {
            "volatility_risk": 0.35,
            "liquidity_risk": 0.20,
            "market_risk": 0.45,
            "overall_risk": 0.35
        }
        
    def _identify_opportunities(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify trading opportunities"""
        return [
            {"type": "momentum", "strength": 0.8, "timeframe": "1h"},
            {"type": "mean_reversion", "strength": 0.6, "timeframe": "4h"},
            {"type": "breakout", "strength": 0.7, "timeframe": "1d"}
        ]
        
    def _calculate_confidence(self, observation: Dict[str, Any]) -> float:
        """Calculate decision confidence"""
        return min(1.0, observation.get("market_sentiment", {}).get("confidence", 0.5) + 0.2)
        
    def _generate_recommendations(self, observation: Dict[str, Any]) -> List[str]:
        """Generate trading recommendations"""
        return [
            "Consider long positions on strong momentum stocks",
            "Monitor volatility for entry opportunities",
            "Set stop losses at 2% below entry"
        ]
        
    def _evaluate_timing(self, observation: Dict[str, Any]) -> str:
        """Evaluate market timing"""
        return "favorable" if observation.get("trend_analysis", {}).get("trend_strength", 0) > 0.6 else "neutral"
        
    def _generate_rationale(self, observation: Dict[str, Any]) -> str:
        """Generate decision rationale"""
        return "Based on strong upward trend and positive sentiment, market conditions favor long positions."
        
    def _assess_urgency(self, observation: Dict[str, Any]) -> int:
        """Assess urgency of actions (1-10)"""
        return 6 if observation.get("trend_analysis", {}).get("trend_strength", 0) > 0.7 else 4
        
    def _assess_impact(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Assess impact of decision"""
        return {
            "expected_return": "5-8%",
            "risk_level": "medium",
            "time_horizon": "1-3 days"
        }
        
    def _handle_decision_request(self, event: Event):
        """Handle decision request from other agents"""
        self.logger.info(f"Received decision request from {event.source_agent}")
        # Process request asynchronously
        threading.Thread(target=self._process_decision_request, args=(event,), daemon=True).start()
        
    def _handle_market_data(self, event: Event):
        """Handle market data updates"""
        self.logger.info(f"Received market data from {event.source_agent}")
        # Process market data
        threading.Thread(target=self._process_market_data, args=(event,), daemon=True).start()
        
    def _handle_signal(self, event: Event):
        """Handle signal generation"""
        self.logger.info(f"Received signal from {event.source_agent}")
        # Analyze signal
        threading.Thread(target=self._process_signal, args=(event,), daemon=True).start()
        
    def _process_decision_request(self, event: Event):
        """Process decision request"""
        # Simulate decision processing
        time.sleep(0.5)
        result = {
            "decision": "proceed",
            "confidence": 0.8,
            "reasoning": "Market conditions favorable"
        }
        self.send_message(event.source_agent, EventType.PERFORMANCE_UPDATE, result)
        
    def _process_market_data(self, event: Event):
        """Process market data"""
        # Simulate analysis
        time.sleep(0.2)
        
    def _process_signal(self, event: Event):
        """Process signal"""
        # Simulate signal analysis
        time.sleep(0.1)


class RiskAgent(BaseAgent):
    """Risk Analytics Agent - risk assessment and management"""
    
    def __init__(self, agent_id: str = "risk_analytics", config: Optional[Dict] = None):
        default_config = {
            "max_risk_tolerance": 0.15,
            "var_confidence": 0.95,
            "stress_test_frequency": 3600,  # seconds
            "monitoring_interval": 30,  # seconds
            "alert_thresholds": {
                "var_limit": 0.05,
                "drawdown_limit": 0.10,
                "volatility_limit": 0.30
            }
        }
        if config:
            default_config.update(config)
        super().__init__(agent_id, default_config)
        
        # Register message handlers
        self._message_handlers[EventType.MARKET_DATA_UPDATE] = self._handle_market_update
        self._message_handlers[EventType.SIGNAL_GENERATED] = self._handle_signal
        self._message_handlers[EventType.DECISION_REQUEST] = self._handle_decision_request
        
    async def observe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Observe risk factors and market conditions"""
        await asyncio.sleep(0.08)
        
        observations = {
            "portfolio_risk": self._calculate_portfolio_risk(data),
            "var_analysis": self._calculate_var(data),
            "stress_test_results": self._perform_stress_test(data),
            "correlation_analysis": self._analyze_correlations(data),
            "liquidity_assessment": self._assess_liquidity(data),
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Risk Agent completed risk assessment")
        return observations
        
    async def decide(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Make risk-based decisions"""
        await asyncio.sleep(0.12)
        
        risk_score = observation.get("portfolio_risk", {}).get("score", 0)
        var_limit = self.config["alert_thresholds"]["var_limit"]
        drawdown_limit = self.config["alert_thresholds"]["drawdown_limit"]
        
        decision = {
            "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low",
            "actions_required": [],
            "risk_alerts": [],
            "position_adjustments": []
        }
        
        if risk_score > 0.8:
            decision["actions_required"].append("reduce_positions")
            decision["risk_alerts"].append("critical_risk_level")
        elif risk_score > 0.6:
            decision["actions_required"].append("monitor_closely")
            decision["risk_alerts"].append("elevated_risk")
            
        if observation.get("var_analysis", {}).get("current_var", 0) > var_limit:
            decision["position_adjustments"].append("reduce_var_exposure")
            
        return decision
        
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute risk management actions"""
        await asyncio.sleep(0.06)
        
        actions_taken = []
        
        if decision.get("risk_alerts"):
            # Send risk alerts
            for alert in decision["risk_alerts"]:
                self.send_message(
                    target_agent="controller",
                    event_type=EventType.RISK_ALERT,
                    data={
                        "alert_type": alert,
                        "risk_score": decision.get("risk_level"),
                        "timestamp": datetime.now().isoformat()
                    },
                    priority=9 if "critical" in alert else 7
                )
                actions_taken.append(f"alert_sent_{alert}")
                
        if decision.get("position_adjustments"):
            for adjustment in decision["position_adjustments"]:
                self.send_message(
                    target_agent="signal_agent",
                    event_type=EventType.SIGNAL_GENERATED,
                    data={
                        "action": adjustment,
                        "priority": 8,
                        "reason": "risk_management"
                    }
                )
                actions_taken.append(f"adjustment_initiated_{adjustment}")
                
        return {
            "actions_taken": actions_taken,
            "risk_mitigated": len(decision.get("actions_required", [])) > 0,
            "timestamp": datetime.now().isoformat()
        }
        
    def _calculate_portfolio_risk(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall portfolio risk"""
        # Simulate risk calculation
        return {
            "score": 0.35,
            "components": {
                "market_risk": 0.40,
                "credit_risk": 0.20,
                "liquidity_risk": 0.25,
                "operational_risk": 0.15
            }
        }
        
    def _calculate_var(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Value at Risk"""
        return {
            "current_var": 0.03,
            "95_percent_var": 0.045,
            "99_percent_var": 0.065,
            "breached_limits": False
        }
        
    def _perform_stress_test(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform stress testing"""
        return {
            "market_crash_scenario": {"loss": 0.12, "recovery_time": "6 months"},
            "volatility_spike": {"loss": 0.08, "recovery_time": "2 months"},
            "liquidity_crisis": {"loss": 0.15, "recovery_time": "1 year"}
        }
        
    def _analyze_correlations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze asset correlations"""
        return {
            "average_correlation": 0.45,
            "high_correlation_pairs": ["EURUSD-GBPUSD", "GOLD-SILVER"],
            "diversification_score": 0.72
        }
        
    def _assess_liquidity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess liquidity conditions"""
        return {
            "market_liquidity": "adequate",
            "bid_ask_spreads": 0.0015,
            "slippage_risk": "low"
        }
        
    def _handle_market_update(self, event: Event):
        """Handle market data update"""
        self.logger.info(f"Received market update from {event.source_agent}")
        threading.Thread(target=self._process_market_update, args=(event,), daemon=True).start()
        
    def _handle_signal(self, event: Event):
        """Handle signal generation"""
        self.logger.info(f"Received signal from {event.source_agent}")
        threading.Thread(target=self._process_signal, args=(event,), daemon=True).start()
        
    def _handle_decision_request(self, event: Event):
        """Handle decision request"""
        self.logger.info(f"Received decision request from {event.source_agent}")
        threading.Thread(target=self._process_decision_request, args=(event,), daemon=True).start()
        
    def _process_market_update(self, event: Event):
        """Process market update"""
        time.sleep(0.3)
        
    def _process_signal(self, event: Event):
        """Process signal"""
        time.sleep(0.2)
        
    def _process_decision_request(self, event: Event):
        """Process decision request"""
        time.sleep(0.4)


class SignalAgent(BaseAgent):
    """Signal Generator Agent - trading signal generation and execution"""
    
    def __init__(self, agent_id: str = "signal_generator", config: Optional[Dict] = None):
        default_config = {
            "min_signal_strength": 0.6,
            "max_signals_per_hour": 50,
            "signal_timeout": 300,  # seconds
            "backtesting_period": 30,  # days
            "confirmation_required": True
        }
        if config:
            default_config.update(config)
        super().__init__(agent_id, default_config)
        
        # Register message handlers
        self._message_handlers[EventType.DECISION_REQUEST] = self._handle_decision_request
        self._message_handlers[EventType.RISK_ALERT] = self._handle_risk_alert
        self._message_handlers[EventType.MARKET_DATA_UPDATE] = self._handle_market_update
        
        self.signal_queue = deque()
        self.last_signal_time = None
        
    async def observe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Observe market patterns and generate signals"""
        await asyncio.sleep(0.1)
        
        observations = {
            "technical_indicators": self._analyze_technical_indicators(data),
            "pattern_recognition": self._recognize_patterns(data),
            "volume_analysis": self._analyze_volume(data),
            "momentum_assessment": self._assess_momentum(data),
            "signal_candidates": self._generate_signal_candidates(data),
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Signal Agent identified {len(observations.get('signal_candidates', []))} candidates")
        return observations
        
    async def decide(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on signal generation and filtering"""
        await asyncio.sleep(0.08)
        
        candidates = observation.get("signal_candidates", [])
        filtered_signals = []
        
        for candidate in candidates:
            if self._validate_signal(candidate):
                signal_strength = self._calculate_signal_strength(candidate, observation)
                if signal_strength >= self.config["min_signal_strength"]:
                    filtered_signals.append({
                        **candidate,
                        "strength": signal_strength,
                        "confidence": self._calculate_confidence(candidate, observation)
                    })
                    
        decision = {
            "signals_to_generate": filtered_signals,
            "signal_count": len(filtered_signals),
            "recommendations": self._generate_recommendations(filtered_signals),
            "filtering_applied": len(candidates) - len(filtered_signals)
        }
        
        return decision
        
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute signal generation and notification"""
        await asyncio.sleep(0.05)
        
        actions_taken = []
        signals_generated = []
        
        for signal in decision.get("signals_to_generate", []):
            # Add to signal queue
            self.signal_queue.append(signal)
            signals_generated.append(signal)
            
            # Notify controller
            self.send_message(
                target_agent="controller",
                event_type=EventType.SIGNAL_GENERATED,
                data={
                    "signal": signal,
                    "timestamp": datetime.now().isoformat()
                },
                priority=7 if signal.get("strength", 0) > 0.8 else 5
            )
            actions_taken.append("signal_generated")
            
        # Clean old signals
        self._clean_old_signals()
        
        return {
            "signals_generated": len(signals_generated),
            "actions_taken": actions_taken,
            "queue_size": len(self.signal_queue),
            "timestamp": datetime.now().isoformat()
        }
        
    def _analyze_technical_indicators(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical indicators"""
        return {
            "rsi": 65.4,
            "macd": 0.0023,
            "bollinger_position": 0.72,
            "moving_averages": {
                "sma_20": 1.2345,
                "sma_50": 1.2298,
                "ema_12": 1.2356
            }
        }
        
    def _recognize_patterns(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recognize chart patterns"""
        return [
            {"pattern": "double_top", "confidence": 0.75, "reliability": 0.68},
            {"pattern": "ascending_triangle", "confidence": 0.82, "reliability": 0.73}
        ]
        
    def _analyze_volume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze volume patterns"""
        return {
            "volume_trend": "increasing",
            "volume_ratio": 1.35,
            "accumulation_distribution": 0.68
        }
        
    def _assess_momentum(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market momentum"""
        return {
            "momentum_score": 0.72,
            "acceleration": "positive",
            "velocity": 0.65
        }
        
    def _generate_signal_candidates(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate signal candidates"""
        return [
            {
                "type": "buy",
                "symbol": "EURUSD",
                "entry_price": 1.2356,
                "stop_loss": 1.2298,
                "take_profit": 1.2456,
                "timeframe": "1h"
            },
            {
                "type": "sell",
                "symbol": "GOLD",
                "entry_price": 2034.5,
                "stop_loss": 2045.2,
                "take_profit": 2015.8,
                "timeframe": "4h"
            }
        ]
        
    def _validate_signal(self, signal: Dict[str, Any]) -> bool:
        """Validate signal quality"""
        required_fields = ["type", "symbol", "entry_price", "stop_loss", "take_profit"]
        return all(field in signal for field in required_fields)
        
    def _calculate_signal_strength(self, signal: Dict[str, Any], observation: Dict[str, Any]) -> float:
        """Calculate signal strength (0-1)"""
        # Simulate strength calculation
        base_strength = 0.7
        technical_boost = observation.get("technical_indicators", {}).get("rsi", 50) / 100
        pattern_boost = max([p.get("confidence", 0) for p in observation.get("pattern_recognition", [])], default=0)
        volume_boost = observation.get("volume_analysis", {}).get("volume_ratio", 1.0) / 2
        
        strength = (base_strength + technical_boost + pattern_boost + volume_boost) / 4
        return min(1.0, strength)
        
    def _calculate_confidence(self, signal: Dict[str, Any], observation: Dict[str, Any]) -> float:
        """Calculate signal confidence (0-1)"""
        # Simulate confidence calculation
        return 0.75
        
    def _generate_recommendations(self, signals: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for signals"""
        recommendations = []
        
        if len(signals) == 0:
            return ["No high-quality signals found. Continue monitoring."]
            
        recommendations.append(f"Generated {len(signals)} quality signals")
        
        for signal in signals:
            if signal.get("strength", 0) > 0.8:
                recommendations.append(f"High confidence {signal['type']} signal for {signal['symbol']}")
                
        return recommendations
        
    def _clean_old_signals(self):
        """Clean signals older than timeout"""
        current_time = time.time()
        timeout = self.config["signal_timeout"]
        
        while self.signal_queue and (current_time - self.signal_queue[0].get("timestamp", 0)) > timeout:
            self.signal_queue.popleft()
            
    def _handle_decision_request(self, event: Event):
        """Handle decision request"""
        self.logger.info(f"Received decision request from {event.source_agent}")
        threading.Thread(target=self._process_decision_request, args=(event,), daemon=True).start()
        
    def _handle_risk_alert(self, event: Event):
        """Handle risk alert"""
        self.logger.info(f"Received risk alert from {event.source_agent}")
        threading.Thread(target=self._process_risk_alert, args=(event,), daemon=True).start()
        
    def _handle_market_update(self, event: Event):
        """Handle market update"""
        self.logger.info(f"Received market update from {event.source_agent}")
        threading.Thread(target=self._process_market_update, args=(event,), daemon=True).start()
        
    def _process_decision_request(self, event: Event):
        """Process decision request"""
        time.sleep(0.3)
        
    def _process_risk_alert(self, event: Event):
        """Process risk alert"""
        time.sleep(0.2)
        
    def _process_market_update(self, event: Event):
        """Process market update"""
        time.sleep(0.1)


class AgentRegistry:
    """Agent registry for managing agent instances"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_configs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent"""
        with self._lock:
            self.agents[agent.agent_id] = agent
            self.agent_configs[agent.agent_id] = agent.config
            logger.info(f"Registered agent: {agent.agent_id}")
            
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        with self._lock:
            if agent_id in self.agents:
                del self.agents[agent_id]
                del self.agent_configs[agent_id]
                logger.info(f"Unregistered agent: {agent_id}")
                
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
        
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """Get all registered agents"""
        return self.agents.copy()
        
    def get_agents_by_status(self, status: AgentStatus) -> List[BaseAgent]:
        """Get agents by status"""
        return [agent for agent in self.agents.values() if agent.state.status == status]
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of all agents"""
        summary = {}
        for agent_id, agent in self.agents.items():
            summary[agent_id] = agent.get_performance_metrics()
        return summary


class LoadBalancer:
    """Load balancer for distributing work across agents"""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.load_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
    def get_optimal_agent(self, agent_type: str = None) -> Optional[BaseAgent]:
        """Get optimal agent based on load and performance"""
        available_agents = []
        
        for agent in self.registry.get_all_agents().values():
            if agent.state.status == AgentStatus.ACTIVE and agent.state.load_factor < 0.8:
                if agent_type is None or agent_type in agent.agent_id:
                    available_agents.append(agent)
                    
        if not available_agents:
            return None
            
        # Score agents based on multiple factors
        best_agent = None
        best_score = -1
        
        for agent in available_agents:
            score = self._calculate_agent_score(agent)
            if score > best_score:
                best_score = score
                best_agent = agent
                
        return best_agent
        
    def _calculate_agent_score(self, agent: BaseAgent) -> float:
        """Calculate agent score for load balancing"""
        # Performance score (0-1)
        performance = agent.state.performance_score / 100
        
        # Inverse of load (0-1, higher = less load)
        load_inverse = 1 - agent.state.load_factor
        
        # Inverse of error rate (0-1)
        error_rate = agent.state.error_count / max(1, agent.state.success_count + agent.state.error_count)
        error_inverse = 1 - error_rate
        
        # Response time factor (0-1, lower response time = higher score)
        response_factor = 1 / (1 + agent.state.response_time_avg)
        
        # Weighted score
        score = (performance * 0.3 + load_inverse * 0.3 + error_inverse * 0.2 + response_factor * 0.2)
        
        # Record load history
        self.load_history[agent.agent_id].append(agent.state.load_factor)
        
        return score
        
    def get_load_statistics(self) -> Dict[str, Any]:
        """Get load statistics for all agents"""
        stats = {}
        for agent_id, history in self.load_history.items():
            if history:
                stats[agent_id] = {
                    "current_load": history[-1],
                    "average_load": sum(history) / len(history),
                    "load_trend": "increasing" if len(history) > 1 and history[-1] > history[-2] else "stable"
                }
        return stats


class FailoverManager:
    """Failover manager for handling agent failures"""
    
    def __init__(self, registry: AgentRegistry, event_bus: EventBus):
        self.registry = registry
        self.event_bus = event_bus
        self.failover_history: List[Dict[str, Any]] = []
        self.monitoring_active = False
        
    def start_monitoring(self):
        """Start monitoring agents for failures"""
        if not self.monitoring_active:
            self.monitoring_active = True
            threading.Thread(target=self._monitor_agents, daemon=True).start()
            logger.info("Failover monitoring started")
            
    def stop_monitoring(self):
        """Stop monitoring agents"""
        self.monitoring_active = False
        logger.info("Failover monitoring stopped")
        
    def trigger_failover(self, failed_agent_id: str) -> Optional[BaseAgent]:
        """Trigger failover for a failed agent"""
        failed_agent = self.registry.get_agent(failed_agent_id)
        if not failed_agent:
            return None
            
        logger.warning(f"Triggering failover for agent: {failed_agent_id}")
        
        # Find backup agent
        backup_agent = self._find_backup_agent(failed_agent_id)
        
        if backup_agent:
            # Transfer state and responsibilities
            self._transfer_responsibilities(failed_agent, backup_agent)
            
            # Log failover event
            self.failover_history.append({
                "timestamp": datetime.now().isoformat(),
                "failed_agent": failed_agent_id,
                "backup_agent": backup_agent.agent_id,
                "status": "success"
            })
            
            # Notify all agents
            event = Event(
                event_id=str(uuid.uuid4()),
                event_type=EventType.AGENT_STATUS_CHANGE,
                source_agent="failover_manager",
                target_agent=None,
                timestamp=datetime.now(),
                data={
                    "agent_id": failed_agent_id,
                    "new_status": "failover",
                    "backup_agent": backup_agent.agent_id
                }
            )
            self.event_bus.publish(event)
            
            return backup_agent
        else:
            logger.error(f"No backup agent found for {failed_agent_id}")
            return None
            
    def _monitor_agents(self):
        """Monitor agents for failures"""
        while self.monitoring_active:
            try:
                for agent in self.registry.get_all_agents().values():
                    if agent.state.status == AgentStatus.ERROR:
                        # Check if agent is truly failed
                        time_since_error = (datetime.now() - agent.state.last_activity).total_seconds()
                        if time_since_error > 60:  # 1 minute threshold
                            self.trigger_failover(agent.agent_id)
                            
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in agent monitoring: {e}")
                
    def _find_backup_agent(self, failed_agent_id: str) -> Optional[BaseAgent]:
        """Find backup agent for failed agent"""
        # Simple backup strategy - any active agent of same type
        for agent in self.registry.get_all_agents().values():
            if (agent.state.status == AgentStatus.ACTIVE and 
                agent.agent_id != failed_agent_id and
                failed_agent_id.split('_')[0] in agent.agent_id):
                return agent
        return None
        
    def _transfer_responsibilities(self, failed_agent: BaseAgent, backup_agent: BaseAgent):
        """Transfer responsibilities from failed to backup agent"""
        # Update backup agent status
        backup_agent.state.status = AgentStatus.BUSY
        
        # In a real implementation, this would transfer state, queues, etc.
        logger.info(f"Transferred responsibilities from {failed_agent.agent_id} to {backup_agent.agent_id}")


class AgentController:
    """Main AI Agent Controller - orchestrates all agents"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.event_bus = EventBus()
        self.registry = AgentRegistry()
        self.load_balancer = LoadBalancer(self.registry)
        self.failover_manager = FailoverManager(self.registry, self.event_bus)
        
        self.agents: List[BaseAgent] = []
        self.is_running = False
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Performance monitoring
        self.monitoring_active = False
        
    def _setup_event_handlers(self):
        """Setup event handlers for controller"""
        self.event_bus.subscribe(EventType.AGENT_STATUS_CHANGE, self._handle_status_change)
        self.event_bus.subscribe(EventType.PERFORMANCE_UPDATE, self._handle_performance_update)
        self.event_bus.subscribe(EventType.RISK_ALERT, self._handle_risk_alert)
        self.event_bus.subscribe(EventType.SIGNAL_GENERATED, self._handle_signal_generated)
        self.event_bus.subscribe(EventType.HEALTH_CHECK, self._handle_health_check)
        
    def initialize_agents(self, agent_configs: Optional[Dict[str, Dict]] = None):
        """Initialize agents with configurations"""
        configs = agent_configs or {}
        
        # Initialize GPT Agent
        gpt_config = configs.get("gpt_agent", {})
        gpt_agent = GPTAgent(config=gpt_config)
        self._register_agent(gpt_agent)
        
        # Initialize Risk Agent
        risk_config = configs.get("risk_agent", {})
        risk_agent = RiskAgent(config=risk_config)
        self._register_agent(risk_agent)
        
        # Initialize Signal Agent
        signal_config = configs.get("signal_agent", {})
        signal_agent = SignalAgent(config=signal_config)
        self._register_agent(signal_agent)
        
        logger.info(f"Initialized {len(self.agents)} agents")
        
    def _register_agent(self, agent: BaseAgent):
        """Register agent and setup dependencies"""
        agent.set_event_bus(self.event_bus)
        agent.register_observer(self._on_agent_state_change)
        
        self.registry.register_agent(agent)
        self.agents.append(agent)
        
        # Set agent to ACTIVE status by default
        agent.state.status = AgentStatus.ACTIVE
        
        # Add to performance history
        self.performance_history[agent.agent_id] = deque(maxlen=1000)
        
    def start(self):
        """Start the agent controller"""
        if self.is_running:
            logger.warning("Controller already running")
            return
            
        self.is_running = True
        self.event_bus.start_processing()
        self.failover_manager.start_monitoring()
        self._start_performance_monitoring()
        
        logger.info("AI Agent Controller started successfully")
        
    def stop(self):
        """Stop the agent controller"""
        if not self.is_running:
            return
            
        self.is_running = False
        self.failover_manager.stop_monitoring()
        self.monitoring_active = False
        
        # Stop all agents
        for agent in self.agents:
            agent.state.status = AgentStatus.INACTIVE
            
        logger.info("AI Agent Controller stopped")
        
    def execute_oda_cycle(self, data: Dict[str, Any], agent_type: str = None) -> Dict[str, Any]:
        """Execute complete ODA (Observe-Decide-Act) cycle"""
        if not self.is_running:
            raise RuntimeError("Controller not running")
            
        # Get optimal agent
        if agent_type:
            # Map agent types to actual agent IDs
            agent_id_mapping = {
                "gpt": "gpt_assistant",
                "risk": "risk_analytics", 
                "signal": "signal_generator"
            }
            agent_id = agent_id_mapping.get(agent_type, f"{agent_type}_agent")
            agent = self.registry.get_agent(agent_id)
        else:
            agent = self.load_balancer.get_optimal_agent()
            
        if not agent:
            raise RuntimeError("No available agent found")
            
        # Execute cycle - handle async properly
        try:
            # Create new event loop for this operation
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, create a new task
                    result = loop.create_task(agent.process_cycle(data))
                    # Run in a separate thread to avoid blocking
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, agent.process_cycle(data))
                        result = future.result()
                else:
                    result = loop.run_until_complete(agent.process_cycle(data))
            except RuntimeError:
                # No event loop, create one
                result = asyncio.run(agent.process_cycle(data))
                
            self._record_performance(agent.agent_id, True, agent.state.response_time_avg)
            return result
        except Exception as e:
            self._record_performance(agent.agent_id, False, agent.state.response_time_avg)
            raise
            
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        agent_statuses = {}
        for agent in self.agents:
            agent_statuses[agent.agent_id] = {
                "status": agent.state.status.value,
                "last_activity": agent.state.last_activity.isoformat(),
                "performance_score": agent.state.performance_score,
                "load_factor": agent.state.load_factor
            }
            
        return {
            "controller_status": "running" if self.is_running else "stopped",
            "total_agents": len(self.agents),
            "agent_statuses": agent_statuses,
            "load_statistics": self.load_balancer.get_load_statistics(),
            "failover_events": len(self.failover_manager.failover_history),
            "timestamp": datetime.now().isoformat()
        }
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        metrics = {
            "controller_uptime": time.time() - (self.start_time if hasattr(self, 'start_time') else time.time()),
            "agent_metrics": {},
            "system_performance": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Get individual agent metrics
        for agent in self.agents:
            metrics["agent_metrics"][agent.agent_id] = agent.get_performance_metrics()
            
        # Calculate system-wide metrics
        total_operations = sum(agent.state.success_count + agent.state.error_count for agent in self.agents)
        total_successes = sum(agent.state.success_count for agent in self.agents)
        
        metrics["system_performance"] = {
            "total_operations": total_operations,
            "overall_success_rate": total_successes / max(1, total_operations),
            "average_response_time": sum(agent.state.response_time_avg for agent in self.agents) / max(1, len(self.agents)),
            "system_load": sum(agent.state.load_factor for agent in self.agents) / max(1, len(self.agents))
        }
        
        return metrics
        
    def scale_agents(self, agent_type: str, target_count: int):
        """Scale agents up or down"""
        current_count = len([agent for agent in self.agents if agent_type in agent.agent_id])
        
        if target_count > current_count:
            # Scale up
            for i in range(target_count - current_count):
                if agent_type == "gpt":
                    new_agent = GPTAgent(f"{agent_type}_agent_{i+2}")
                elif agent_type == "risk":
                    new_agent = RiskAgent(f"{agent_type}_agent_{i+2}")
                elif agent_type == "signal":
                    new_agent = SignalAgent(f"{agent_type}_agent_{i+2}")
                else:
                    continue
                    
                self._register_agent(new_agent)
                logger.info(f"Scaled up {agent_type} agents to {target_count}")
                
        elif target_count < current_count:
            # Scale down - remove excess agents
            agents_to_remove = []
            for agent in self.agents:
                if agent_type in agent.agent_id and f"{agent_type}_agent" not in agent.agent_id:
                    agents_to_remove.append(agent)
                    
            for agent in agents_to_remove[:current_count - target_count]:
                self.agents.remove(agent)
                self.registry.unregister_agent(agent.agent_id)
                logger.info(f"Scaled down {agent_type} agents to {target_count}")
                
    def _start_performance_monitoring(self):
        """Start performance monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.start_time = time.time()
            threading.Thread(target=self._monitor_performance, daemon=True).start()
            
    def _monitor_performance(self):
        """Monitor system performance"""
        while self.monitoring_active:
            try:
                # Collect performance data
                for agent in self.agents:
                    metrics = agent.get_performance_metrics()
                    self.performance_history[agent.agent_id].append({
                        "timestamp": time.time(),
                        "performance_score": metrics["performance_score"],
                        "response_time": metrics["average_response_time"],
                        "load_factor": metrics["load_factor"]
                    })
                    
                # Check for performance degradation
                self._check_performance_thresholds()
                
                time.sleep(30)  # Monitor every 30 seconds
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                
    def _check_performance_thresholds(self):
        """Check for performance threshold violations"""
        for agent in self.agents:
            if agent.state.performance_score < 50:  # Performance threshold
                logger.warning(f"Low performance detected for agent {agent.agent_id}: {agent.state.performance_score}")
                
            if agent.state.load_factor > 0.9:  # Load threshold
                logger.warning(f"High load detected for agent {agent.agent_id}: {agent.state.load_factor}")
                
    def _record_performance(self, agent_id: str, success: bool, response_time: float):
        """Record performance metrics"""
        if agent_id in self.performance_history:
            self.performance_history[agent_id].append({
                "timestamp": time.time(),
                "success": success,
                "response_time": response_time
            })
            
    def _on_agent_state_change(self, new_state: AgentState):
        """Handle agent state changes"""
        # Log state changes
        logger.debug(f"Agent {new_state.agent_id} state changed to {new_state.status.value}")
        
        # Check for failure conditions
        if new_state.status == AgentStatus.ERROR and new_state.error_count > 5:
            logger.error(f"Agent {new_state.agent_id} has too many errors, triggering failover")
            self.failover_manager.trigger_failover(new_state.agent_id)
            
    def _handle_status_change(self, event: Event):
        """Handle agent status change events"""
        logger.info(f"Status change event: {event.data}")
        
    def _handle_performance_update(self, event: Event):
        """Handle performance update events"""
        logger.debug(f"Performance update: {event.data}")
        
    def _handle_risk_alert(self, event: Event):
        """Handle risk alert events"""
        logger.warning(f"Risk alert received: {event.data}")
        
    def _handle_signal_generated(self, event: Event):
        """Handle signal generation events"""
        logger.info(f"Signal generated: {event.data}")
        
    def _handle_health_check(self, event: Event):
        """Handle health check events"""
        # Perform health checks on all agents
        health_data = {}
        for agent in self.agents:
            health_data[agent.agent_id] = agent.health_check()
            
        # Send health report
        health_event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.HEALTH_CHECK,
            source_agent="controller",
            target_agent=None,
            timestamp=datetime.now(),
            data=health_data
        )
        self.event_bus.publish(health_event)
        
    def save_state(self, filepath: str):
        """Save controller state to file"""
        state_data = {
            "config": self.config,
            "agent_configs": self.registry.agent_configs,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state_data, f, indent=2, default=str)
            
        logger.info(f"Controller state saved to {filepath}")
        
    def load_state(self, filepath: str):
        """Load controller state from file"""
        try:
            with open(filepath, 'r') as f:
                state_data = json.load(f)
                
            self.config = state_data.get("config", {})
            self.registry.agent_configs = state_data.get("agent_configs", {})
            
            logger.info(f"Controller state loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading state: {e}")


# Demo and testing functions
async def demo_controller():
    """Demonstrate the AI Agent Controller functionality"""
    print("🚀 AI Agent Controller Demo")
    print("=" * 50)
    
    # Initialize controller
    controller = AgentController()
    
    # Configure agents
    agent_configs = {
        "gpt_agent": {
            "analysis_depth": "comprehensive",
            "max_tokens": 2000
        },
        "risk_agent": {
            "max_risk_tolerance": 0.10,
            "alert_thresholds": {
                "var_limit": 0.03,
                "drawdown_limit": 0.08
            }
        },
        "signal_agent": {
            "min_signal_strength": 0.7,
            "max_signals_per_hour": 30
        }
    }
    
    # Initialize agents
    controller.initialize_agents(agent_configs)
    
    # Start controller
    controller.start()
    print("✅ Controller started")
    
    # Simulate market data
    market_data = {
        "timestamp": datetime.now().isoformat(),
        "symbol": "EURUSD",
        "price": 1.2356,
        "volume": 1000000,
        "bid": 1.2354,
        "ask": 1.2358,
        "high": 1.2375,
        "low": 1.2340,
        "rsi": 65.4,
        "macd": 0.0023
    }
    
    print(f"\n📊 Market Data: {market_data['symbol']} @ {market_data['price']}")
    
    # Execute ODA cycles for each agent type
    for agent_type in ["gpt", "risk", "signal"]:
        try:
            print(f"\n🔄 Executing {agent_type} agent cycle...")
            result = controller.execute_oda_cycle(market_data, agent_type)
            print(f"✅ {agent_type} agent completed successfully")
            print(f"   Result keys: {list(result.keys())}")
        except Exception as e:
            print(f"❌ {agent_type} agent error: {e}")
            
    # Get system status
    print(f"\n📈 System Status:")
    status = controller.get_system_status()
    print(f"   Controller: {status['controller_status']}")
    print(f"   Total agents: {status['total_agents']}")
    for agent_id, agent_status in status['agent_statuses'].items():
        print(f"   {agent_id}: {agent_status['status']} (score: {agent_status['performance_score']:.1f})")
        
    # Get performance metrics
    print(f"\n📊 Performance Metrics:")
    metrics = controller.get_performance_metrics()
    print(f"   System operations: {metrics['system_performance']['total_operations']}")
    print(f"   Overall success rate: {metrics['system_performance']['overall_success_rate']:.2%}")
    print(f"   Average response time: {metrics['system_performance']['average_response_time']:.3f}s")
    
    # Test cross-agent communication
    print(f"\n💬 Testing cross-agent communication...")
    for agent in controller.agents:
        if hasattr(agent, 'send_message'):
            agent.send_message(
                target_agent="controller",
                event_type=EventType.CROSS_AGENT_COMMUNICATION,
                data={"test": "communication", "source": agent.agent_id}
            )
            
    # Test failover
    print(f"\n🔧 Testing failover mechanism...")
    if len(controller.agents) > 1:
        failed_agent = controller.agents[0]
        backup = controller.failover_manager.trigger_failover(failed_agent.agent_id)
        if backup:
            print(f"   ✅ Failover successful: {failed_agent.agent_id} -> {backup.agent_id}")
        else:
            print(f"   ❌ Failover failed: no backup found")
            
    # Test load balancing
    print(f"\n⚖️  Testing load balancing...")
    optimal_agent = controller.load_balancer.get_optimal_agent()
    if optimal_agent:
        print(f"   ✅ Load balancer selected: {optimal_agent.agent_id}")
    else:
        print(f"   ❌ Load balancer failed: no optimal agent found")
        
    # Save state
    state_file = "/tmp/agent_controller_state.json"
    controller.save_state(state_file)
    print(f"\n💾 State saved to: {state_file}")
    
    # Stop controller
    controller.stop()
    print(f"\n🛑 Controller stopped")
    
    print(f"\n🎉 Demo completed successfully!")
    return controller


if __name__ == "__main__":
    # Run demo
    controller = asyncio.run(demo_controller())
    
    print(f"\n📋 Controller Summary:")
    print(f"   Agents registered: {len(controller.registry.get_all_agents())}")
    print(f"   Failover events: {len(controller.failover_manager.failover_history)}")
    print(f"   Performance records: {sum(len(history) for history in controller.performance_history.values())}")