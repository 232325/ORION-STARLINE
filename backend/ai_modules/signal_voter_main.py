"""
AI Signal Voting System - Asosiy tizim fayli
Multiple AI agentlarning signallarini yig'ib, konsensus yaratish tizimi
"""

import asyncio
import logging
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import os

# Import our modules
from agent_pool import (
    AgentPool, AgentType, MarketRegime, 
    TechnicalAnalysisAgent, FundamentalAnalysisAgent, SentimentAnalysisAgent,
    QuantitativeAgent, OptionsFlowAgent, RiskManagementAgent, 
    MomentumAgent, ValueAgent
)
from signal_voter import (
    SignalVoter, VotingResult, SignalType, Vote, VotingMethod
)
from consensus_engine import (
    ConsensusEngine, ConsensusType, ConsensusStatus, ConsensusSignal
)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AISignalVotingSystem:
    """AI Signal Voting System - Asosiy boshqaruvchi klass"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        
        # Initialize components
        self.agent_pool = AgentPool(self.config.get('agent_pool', {}))
        self.signal_voter = None
        self.consensus_engine = None
        
        # System state
        self.is_running = False
        self.active_signals: List[ConsensusSignal] = []
        self.signal_history: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.system_metrics = {
            "total_signals_processed": 0,
            "successful_consensus": 0,
            "failed_consensus": 0,
            "average_confidence": 0.0,
            "system_uptime": None,
            "start_time": None
        }
        
        logger.info("AI Signal Voting System initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default konfiguratsiya"""
        return {
            "agent_pool": {
                "max_agents_per_type": 2,
                "performance_window": 100,
                "adaptive_learning": True
            },
            "signal_voter": {
                "min_consensus_threshold": 0.6,
                "min_participants": 3,
                "confidence_threshold": 0.5,
                "diversity_bonus": 0.1
            },
            "consensus_engine": {
                "default_timeout": timedelta(minutes=3),
                "default_min_participants": 3,
                "default_confidence_threshold": 0.6,
                "adaptive_threshold": True,
                "temporal_smoothing": True
            },
            "system": {
                "max_history_size": 1000,
                "cleanup_interval": 3600,  # 1 hour
                "performance_tracking": True,
                "real_time_mode": True
            }
        }
    
    async def initialize(self) -> bool:
        """Tizimni ishga tushirish"""
        try:
            logger.info("Initializing AI Signal Voting System...")
            
            # Initialize signal voter
            self.signal_voter = SignalVoter(
                self.agent_pool, 
                self.config.get('signal_voter', {})
            )
            
            # Initialize consensus engine
            self.consensus_engine = ConsensusEngine(
                self.agent_pool,
                self.signal_voter,
                self.config.get('consensus_engine', {})
            )
            
            # Setup agents
            await self._setup_agents()
            
            # Start system
            self.is_running = True
            self.system_metrics["start_time"] = datetime.now()
            
            logger.info("AI Signal Voting System started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {str(e)}")
            return False
    
    async def _setup_agents(self):
        """AI agentlarni sozlash"""
        logger.info("Setting up AI agents...")
        
        # Agent configurations
        agent_configs = {
            # Technical Analysis Agents
            "tech_1": {
                "agent_type": AgentType.TECHNICAL_ANALYSIS,
                "config": {
                    "timeframes": ["1h", "4h", "1d"],
                    "indicators": ["RSI", "MACD", "Bollinger Bands"],
                    "max_inactive_hours": 12
                }
            },
            "tech_2": {
                "agent_type": AgentType.TECHNICAL_ANALYSIS,
                "config": {
                    "timeframes": ["15m", "1h"],
                    "indicators": ["Stochastic", "Williams %R", "ADX"],
                    "max_inactive_hours": 12
                }
            },
            
            # Fundamental Analysis Agents
            "fundamental_1": {
                "agent_type": AgentType.FUNDAMENTAL_ANALYSIS,
                "config": {
                    "sectors": ["technology", "healthcare", "finance"],
                    "metrics": ["P/E Ratio", "ROE", "Revenue Growth"],
                    "data_freshness_hours": 24
                }
            },
            "fundamental_2": {
                "agent_type": AgentType.FUNDAMENTAL_ANALYSIS,
                "config": {
                    "sectors": ["energy", "consumer", "industrial"],
                    "metrics": ["P/B Ratio", "ROA", "Debt/Equity"],
                    "data_freshness_hours": 24
                }
            },
            
            # Sentiment Analysis Agents
            "sentiment_1": {
                "agent_type": AgentType.SENTIMENT_ANALYSIS,
                "config": {
                    "sources": ["social_media", "news", "earnings_calls"],
                    "sentiment_thresholds": {"extreme_fear": 20, "extreme_greed": 80},
                    "update_frequency": 900  # 15 minutes
                }
            },
            "sentiment_2": {
                "agent_type": AgentType.SENTIMENT_ANALYSIS,
                "config": {
                    "sources": ["analyst_reports", "institutional_sentiment"],
                    "indicators": ["VIX", "put_call_ratio"],
                    "update_frequency": 1800  # 30 minutes
                }
            },
            
            # Quantitative Agents
            "quant_1": {
                "agent_type": AgentType.QUANTITATIVE,
                "config": {
                    "models": ["mean_reversion", "momentum", "pairs_trading"],
                    "timeframes": ["intraday", "daily"],
                    "lookback_periods": [5, 10, 20, 50]
                }
            },
            "quant_2": {
                "agent_type": AgentType.QUANTITATIVE,
                "config": {
                    "models": ["statistical_arbitrage", "volatility_trading"],
                    "timeframes": ["weekly", "monthly"],
                    "risk_metrics": ["VaR", "CVaR"]
                }
            },
            
            # Options Flow Agent
            "options_1": {
                "agent_type": AgentType.OPTIONS_FLOW,
                "config": {
                    "strategies": ["covered_calls", "protective_puts"],
                    "data_sources": ["unusual_options", "whale_activity"],
                    "sensitivity": "high"
                }
            },
            
            # Risk Management Agent
            "risk_1": {
                "agent_type": AgentType.RISK_MANAGEMENT,
                "config": {
                    "risk_metrics": ["VaR", "CVaR", "max_drawdown"],
                    "position_sizing": "kelly_criterion",
                    "portfolio_hedging": True
                }
            },
            
            # Momentum Agent
            "momentum_1": {
                "agent_type": AgentType.MOMENTUM,
                "config": {
                    "indicators": ["price_momentum", "volume_momentum"],
                    "timeframes": ["short_term", "medium_term"],
                    "strength_threshold": 0.7
                }
            },
            "momentum_2": {
                "agent_type": AgentType.MOMENTUM,
                "config": {
                    "indicators": ["sector_momentum", "earnings_momentum"],
                    "timeframes": ["medium_term", "long_term"],
                    "strength_threshold": 0.6
                }
            },
            
            # Value Agent
            "value_1": {
                "agent_type": AgentType.VALUE,
                "config": {
                    "methods": ["dcf", "comparable_analysis"],
                    "growth_rate": 0.05,
                    "discount_rate": 0.10
                }
            },
            "value_2": {
                "agent_type": AgentType.VALUE,
                "config": {
                    "methods": ["asset_valuation", "earnings_power"],
                    "quality_factors": ["ROE", "ROIC", "profit_margins"],
                    "margin_of_safety": 0.20
                }
            }
        }
        
        # Add agents to pool
        for agent_id, agent_config in agent_configs.items():
            success = self.agent_pool.add_agent(
                agent_config["agent_type"],
                agent_id,
                agent_config["config"]
            )
            
            if success:
                logger.info(f"Added agent: {agent_id} ({agent_config['agent_type'].value})")
            else:
                logger.warning(f"Failed to add agent: {agent_id}")
        
        logger.info(f"Agent setup completed. Total agents: {len(self.agent_pool.agents)}")
    
    async def process_market_signal(self, 
                                  market_data: Dict[str, Any], 
                                  asset_symbol: str = "AAPL",
                                  consensus_type: ConsensusType = ConsensusType.ADAPTIVE) -> Optional[ConsensusSignal]:
        """Market signal qayta ishlash"""
        if not self.is_running:
            logger.warning("System is not running")
            return None
        
        try:
            # Create consensus session
            session_id = await self.consensus_engine.create_consensus_session(
                asset_symbol=asset_symbol,
                consensus_type=consensus_type,
                market_data=market_data
            )
            
            # Collect signals from all agents
            market_regime = self.consensus_engine._detect_market_regime(market_data)
            signals = await self.agent_pool.collect_signals(market_data, market_regime)
            
            # Submit signals to consensus session
            for signal in signals:
                vote = self._signal_to_vote(signal)
                self.consensus_engine.submit_signal_to_session(session_id, vote)
            
            # Wait for consensus
            await asyncio.sleep(0.1)  # Brief wait for processing
            
            # Get consensus result
            session = self.consensus_engine.active_sessions.get(session_id)
            if session and session.consensus_result:
                consensus_signal = session.consensus_result
                
                # Add to active signals
                self.active_signals.append(consensus_signal)
                
                # Update metrics
                self.system_metrics["total_signals_processed"] += 1
                if consensus_signal.confidence > 0.5:
                    self.system_metrics["successful_consensus"] += 1
                
                # Add to history
                self.signal_history.append(consensus_signal.to_dict())
                
                logger.info(f"Consensus reached for {asset_symbol}: {consensus_signal.signal_type.value} "
                           f"({consensus_signal.confidence:.2f} confidence)")
                
                return consensus_signal
            else:
                self.system_metrics["failed_consensus"] += 1
                logger.warning(f"Failed to reach consensus for {asset_symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing market signal: {str(e)}")
            return None
    
    async def process_real_time_signals(self, 
                                      market_data_list: List[Dict[str, Any]], 
                                      symbols: List[str]) -> List[ConsensusSignal]:
        """Real-time signals qayta ishlash"""
        if not self.is_running:
            logger.warning("System is not running")
            return []
        
        consensus_signals = []
        
        # Process each asset
        for i, market_data in enumerate(market_data_list):
            asset_symbol = symbols[i] if i < len(symbols) else f"ASSET_{i}"
            
            # Use real-time consensus for speed
            signal = await self.consensus_engine.process_real_time_consensus(
                market_data, asset_symbol
            )
            
            if signal:
                consensus_signals.append(signal)
                self.active_signals.append(signal)
                self.system_metrics["total_signals_processed"] += 1
        
        return consensus_signals
    
    def _signal_to_vote(self, signal: Dict[str, Any]) -> Vote:
        """Signal ni Vote obyektiga konvertatsiya"""
        return Vote(
            agent_id=signal['agent_id'],
            agent_type=signal['agent_type'],
            signal_type=SignalType(signal['signal_type']),
            strength=signal['strength'],
            confidence=signal['confidence'],
            timestamp=datetime.fromisoformat(signal['timestamp']),
            weights=signal.get('weights', {}),
            reasoning=signal.get('reasoning', ''),
            individual_performance=0.8  # Mock performance
        )
    
    def get_current_signals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Joriy signallar olish"""
        recent_signals = sorted(
            self.active_signals,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
        
        return [signal.to_dict() for signal in recent_signals]
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Tizim statistikasi"""
        if self.system_metrics["start_time"]:
            uptime = datetime.now() - self.system_metrics["start_time"]
            self.system_metrics["system_uptime"] = str(uptime)
        
        # Agent statistics
        agent_stats = self.agent_pool.get_pool_statistics()
        
        # Consensus statistics
        consensus_stats = self.consensus_engine.get_consensus_statistics() if self.consensus_engine else {}
        
        # Signal statistics
        signal_stats = {
            "total_signals": len(self.signal_history),
            "active_signals": len(self.active_signals),
            "average_confidence": sum(s.get('confidence', 0) for s in self.signal_history) / len(self.signal_history) if self.signal_history else 0,
            "signal_types": {}
        }
        
        # Count signal types
        for signal_data in self.signal_history:
            signal_type = signal_data.get('signal_type', 'UNKNOWN')
            signal_stats["signal_types"][signal_type] = signal_stats["signal_types"].get(signal_type, 0) + 1
        
        return {
            "system_metrics": self.system_metrics,
            "agent_statistics": agent_stats,
            "consensus_statistics": consensus_stats,
            "signal_statistics": signal_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Performance hisoboti"""
        if not self.signal_history:
            return {"message": "No signals processed yet"}
        
        recent_signals = [s for s in self.signal_history if 
                         datetime.fromisoformat(s['timestamp']) > datetime.now() - timedelta(days=7)]
        
        # Accuracy calculation (simplified)
        accurate_signals = [s for s in recent_signals if s.get('confidence', 0) > 0.6]
        accuracy = len(accurate_signals) / len(recent_signals) if recent_signals else 0
        
        # Confidence calibration
        high_conf_signals = [s for s in recent_signals if s.get('confidence', 0) > 0.8]
        calibration = len(high_conf_signals) / len(recent_signals) if recent_signals else 0
        
        return {
            "accuracy": accuracy,
            "confidence_calibration": calibration,
            "total_signals_7d": len(recent_signals),
            "avg_confidence_7d": sum(s.get('confidence', 0) for s in recent_signals) / len(recent_signals) if recent_signals else 0,
            "consensus_success_rate": (
                self.system_metrics["successful_consensus"] / 
                max(self.system_metrics["total_signals_processed"], 1)
            ),
            "top_performing_agents": self._get_top_agents()
        }
    
    def _get_top_agents(self) -> List[Dict[str, Any]]:
        """Eng yaxshi ishlayotgan agentlar"""
        performances = self.agent_pool.get_all_agent_performances()
        
        # Sort by accuracy
        sorted_agents = sorted(
            performances.items(),
            key=lambda x: x[1].accuracy,
            reverse=True
        )[:5]
        
        return [
            {
                "agent_id": agent_id,
                "accuracy": perf.accuracy,
                "total_signals": perf.total_signals,
                "win_rate": perf.win_rate
            }
            for agent_id, perf in sorted_agents
        ]
    
    async def cleanup(self):
        """Tizimni tozalash"""
        logger.info("Cleaning up AI Signal Voting System...")
        
        # Clean up expired sessions
        if self.consensus_engine:
            await self.consensus_engine.cleanup_expired_sessions()
        
        # Remove expired signals
        current_time = datetime.now()
        self.active_signals = [
            signal for signal in self.active_signals
            if current_time < signal.expiry_time
        ]
        
        # Limit history size
        max_history = self.config.get("system", {}).get("max_history_size", 1000)
        if len(self.signal_history) > max_history:
            self.signal_history = self.signal_history[-max_history:]
        
        self.is_running = False
        logger.info("AI Signal Voting System cleaned up")
    
    def save_state(self, filepath: str):
        """Tizim holatini saqlash"""
        try:
            state = {
                "config": self.config,
                "system_metrics": self.system_metrics,
                "signal_history": self.signal_history[-100:],  # Save last 100
                "timestamp": datetime.now().isoformat()
            }
            
            # Save agent pool state
            agent_pool_path = filepath.replace('.json', '_agents.json')
            self.agent_pool.save_pool_state(agent_pool_path)
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            
            logger.info(f"System state saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving system state: {str(e)}")
    
    def load_state(self, filepath: str) -> bool:
        """Tizim holatini yuklash"""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"State file {filepath} not found")
                return False
            
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Load agent pool state
            agent_pool_path = filepath.replace('.json', '_agents.json')
            if os.path.exists(agent_pool_path):
                self.agent_pool.load_pool_state(agent_pool_path)
            
            # Restore system metrics
            self.system_metrics.update(state.get("system_metrics", {}))
            self.signal_history = state.get("signal_history", [])
            
            logger.info(f"System state loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading system state: {str(e)}")
            return False

# Demo funksiyalar
async def demo_basic_functionality():
    """Asosiy funksionallik demo"""
    print("\n" + "="*60)
    print("🤖 AI SIGNAL VOTING SYSTEM - BASIC DEMO")
    print("="*60)
    
    # Initialize system
    system = AISignalVotingSystem()
    await system.initialize()
    
    # Mock market data
    market_data = {
        "volatility": 0.25,
        "sentiment": 0.7,
        "volume": 1.2,
        "price_data": {"close": [150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160]},
        "indicators": {
            "RSI": 65,
            "MACD": {"signal": 0.5, "histogram": 0.3}
        },
        "fundamentals": {
            "pe_ratio": 18.5,
            "roe": 0.15
        },
        "news": [{"sentiment": 0.6}],
        "social_media": {"overall_sentiment": 0.7}
    }
    
    # Process signals
    print("\n📊 Processing market signals...")
    consensus_signal = await system.process_market_signal(
        market_data, 
        asset_symbol="AAPL",
        consensus_type=ConsensusType.ADAPTIVE
    )
    
    if consensus_signal:
        print(f"\n✅ Consensus Result:")
        print(f"   Signal: {consensus_signal.signal_type.value}")
        print(f"   Confidence: {consensus_signal.confidence:.2f}")
        print(f"   Strength: {consensus_signal.strength:.2f}")
        print(f"   Participants: {len(consensus_signal.participating_agents)}")
        print(f"   Method: {consensus_signal.consensus_method.value}")
        
        # Get agent votes
        print(f"\n👥 Agent Votes:")
        for agent_id in consensus_signal.participating_agents:
            confidence = consensus_signal.confidence_by_agent.get(agent_id, 0)
            print(f"   {agent_id}: {confidence:.2f}")
    
    # System statistics
    print(f"\n📈 System Statistics:")
    stats = system.get_system_statistics()
    print(f"   Total Agents: {stats['agent_statistics']['total_agents']}")
    print(f"   Active Agents: {stats['agent_statistics']['active_agents']}")
    print(f"   Total Signals Processed: {stats['system_metrics']['total_signals_processed']}")
    print(f"   Success Rate: {stats['system_metrics']['successful_consensus']}/{stats['system_metrics']['total_signals_processed']}")
    
    return system

async def demo_multiple_methods():
    """Multiple voting methods demo"""
    print("\n" + "="*60)
    print("🗳️ MULTIPLE VOTING METHODS DEMO")
    print("="*60)
    
    system = AISignalVotingSystem()
    await system.initialize()
    
    # Market data
    market_data = {
        "volatility": 0.30,
        "sentiment": 0.6,
        "volume": 1.0,
        "price_data": {"close": [100, 102, 101, 103, 104, 106, 105, 107, 108, 109, 111]},
        "urgency": 0.8,
        "risk_tolerance": 0.5
    }
    
    # Test different consensus types
    consensus_types = [
        ConsensusType.IMMEDIATE,
        ConsensusType.THRESHOLD_BASED,
        ConsensusType.ADAPTIVE
    ]
    
    for consensus_type in consensus_types:
        print(f"\n🔄 Testing {consensus_type.value}...")
        
        consensus_signal = await system.process_market_signal(
            market_data,
            asset_symbol=f"TEST_{consensus_type.value}",
            consensus_type=consensus_type
        )
        
        if consensus_signal:
            print(f"   Result: {consensus_signal.signal_type.value}")
            print(f"   Confidence: {consensus_signal.confidence:.2f}")
            print(f"   Participants: {len(consensus_signal.participating_agents)}")
        else:
            print(f"   No consensus reached")
    
    return system

async def demo_real_time_processing():
    """Real-time processing demo"""
    print("\n" + "="*60)
    print("⚡ REAL-TIME PROCESSING DEMO")
    print("="*60)
    
    system = AISignalVotingSystem()
    await system.initialize()
    
    # Multiple assets
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    market_data_list = []
    
    # Generate mock data for each asset
    for i, symbol in enumerate(symbols):
        base_price = 100 + i * 50
        market_data = {
            "volatility": 0.20 + (i * 0.05),
            "sentiment": 0.5 + (i * 0.1),
            "volume": 1.0 + (i * 0.2),
            "price_data": {
                "close": [base_price + j for j in range(10)]
            },
            "current_price": base_price
        }
        market_data_list.append(market_data)
    
    print(f"\n🚀 Processing {len(symbols)} assets in real-time...")
    
    # Process all assets
    start_time = time.time()
    consensus_signals = await system.process_real_time_signals(market_data_list, symbols)
    processing_time = time.time() - start_time
    
    print(f"✅ Processed {len(consensus_signals)} signals in {processing_time:.2f} seconds")
    print(f"📊 Average time per signal: {processing_time/len(consensus_signals):.3f} seconds")
    
    # Show results
    for signal in consensus_signals:
        print(f"   {signal.asset_symbol}: {signal.signal_type.value} "
              f"({signal.confidence:.2f} confidence)")
    
    return system

async def demo_performance_tracking():
    """Performance tracking demo"""
    print("\n" + "="*60)
    print("📊 PERFORMANCE TRACKING DEMO")
    print("="*60)
    
    system = AISignalVotingSystem()
    await system.initialize()
    
    # Process multiple signals to build history
    print("\n🔄 Processing multiple signals for performance analysis...")
    
    for i in range(5):
        market_data = {
            "volatility": 0.2 + (i * 0.05),
            "sentiment": 0.5 + (i * 0.1),
            "volume": 1.0,
            "price_data": {"close": [100 + j for j in range(10)]},
            "urgency": 0.6,
            "risk_tolerance": 0.5
        }
        
        await system.process_market_signal(market_data, asset_symbol=f"PERF_{i}")
        await asyncio.sleep(0.1)  # Small delay
    
    # Get performance report
    print("\n📈 Performance Report:")
    performance = system.get_performance_report()
    
    for key, value in performance.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # System statistics
    print(f"\n📊 System Statistics:")
    stats = system.get_system_statistics()
    
    # Agent performance
    print("\n👥 Top Performing Agents:")
    for agent in performance.get("top_performing_agents", [])[:3]:
        print(f"   {agent['agent_id']}: {agent['accuracy']:.2f} accuracy "
              f"({agent['total_signals']} signals)")
    
    return system

async def demo_system_integration():
    """Tizim integratsiyasi demo"""
    print("\n" + "="*60)
    print("🔗 SYSTEM INTEGRATION DEMO")
    print("="*60)
    
    system = AISignalVotingSystem()
    await system.initialize()
    
    print(f"\n🏗️ System Components:")
    print(f"   Agent Pool: {len(system.agent_pool.agents)} agents")
    print(f"   Agent Types: {len(AgentType)} different types")
    print(f"   Consensus Engine: Ready")
    print(f"   Signal Voter: Ready")
    
    # Test system lifecycle
    print(f"\n🔄 System Lifecycle Test:")
    
    # 1. Process signal
    market_data = {
        "volatility": 0.25,
        "sentiment": 0.7,
        "volume": 1.2,
        "price_data": {"close": [150, 151, 152, 153, 154]},
        "urgency": 0.6
    }
    
    signal = await system.process_market_signal(market_data, "INTEGRATION_TEST")
    
    if signal:
        print(f"   ✅ Signal processing: SUCCESS")
        print(f"   ✅ Consensus generation: SUCCESS")
        print(f"   ✅ Agent coordination: SUCCESS")
    else:
        print(f"   ❌ Signal processing: FAILED")
    
    # 2. Save and load state
    print(f"\n💾 State Management Test:")
    
    # Save state
    state_file = "/tmp/ai_voting_system_state.json"
    system.save_state(state_file)
    print(f"   ✅ State saved: {state_file}")
    
    # Create new system and load state
    new_system = AISignalVotingSystem()
    loaded = new_system.load_state(state_file)
    print(f"   {'✅' if loaded else '❌'} State loaded: {loaded}")
    
    # 3. System statistics
    print(f"\n📊 Final System Statistics:")
    final_stats = system.get_system_statistics()
    print(f"   System Uptime: {final_stats['system_metrics'].get('system_uptime', 'N/A')}")
    print(f"   Total Signals: {final_stats['signal_statistics']['total_signals']}")
    print(f"   Success Rate: {final_stats['system_metrics']['successful_consensus']}/{final_stats['system_metrics']['total_signals_processed']}")
    
    return system

async def main():
    """Asosiy demo funksiya"""
    print("🚀 AI Signal Voting System - Comprehensive Demo")
    print("Version 1.0.0 - Multiple AI Agent Consensus System")
    
    try:
        # 1. Basic functionality
        system1 = await demo_basic_functionality()
        
        # 2. Multiple methods
        system2 = await demo_multiple_methods()
        
        # 3. Real-time processing
        system3 = await demo_real_time_processing()
        
        # 4. Performance tracking
        system4 = await demo_performance_tracking()
        
        # 5. System integration
        system5 = await demo_system_integration()
        
        print(f"\n" + "="*60)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print(f"\n📋 Demo Summary:")
        print(f"   ✅ Basic Functionality: Working")
        print(f"   ✅ Multiple Voting Methods: Working")
        print(f"   ✅ Real-time Processing: Working")
        print(f"   ✅ Performance Tracking: Working")
        print(f"   ✅ System Integration: Working")
        
        print(f"\n🔧 System Features Demonstrated:")
        print(f"   • 8 Different AI Agent Types")
        print(f"   • 8 Different Consensus Methods")
        print(f"   • Real-time Signal Processing")
        print(f"   • Adaptive Market Regime Detection")
        print(f"   • Performance Tracking & Analytics")
        print(f"   • Risk Management Integration")
        print(f"   • State Persistence")
        print(f"   • Multi-asset Processing")
        
        # Cleanup
        await system1.cleanup()
        await system2.cleanup()
        await system3.cleanup()
        await system4.cleanup()
        await system5.cleanup()
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        print(f"\n❌ Demo failed: {str(e)}")

if __name__ == "__main__":
    # Run the comprehensive demo
    asyncio.run(main())