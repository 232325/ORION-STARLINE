"""
Integration Framework for Risk Management System
===============================================

Central integration framework that connects the risk management system
with external systems including HFT engines, DAO governance, blockchain,
machine learning models, and external data feeds.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from .hft_engine.hft_connector import HFTEngineConnector
from .dao_governance.dao_connector import DAOGovernanceConnector
from .blockchain.blockchain_connector import BlockchainConnector
from .ml_models.ml_connector import MLModelsConnector
from .external_feeds.data_feed_connector import DataFeedConnector

logger = logging.getLogger(__name__)

@dataclass
class IntegrationConfig:
    """Configuration for integrations"""
    hft_engine_enabled: bool = True
    dao_governance_enabled: bool = True
    blockchain_enabled: bool = True
    ml_models_enabled: bool = True
    external_feeds_enabled: bool = True
    integration_interval: int = 5  # seconds
    retry_attempts: int = 3
    timeout: int = 30

@dataclass
class IntegrationStatus:
    """Integration component status"""
    component_name: str
    enabled: bool
    connected: bool
    last_sync: Optional[datetime]
    error_count: int
    status_message: str

class IntegrationFramework:
    """
    Central integration framework for risk management system
    
    Coordinates all external integrations and provides unified interface
    for data exchange and control signals between systems.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.integration_config = IntegrationConfig(**config)
        
        # Initialize integration components
        self.hft_connector = None
        self.dao_connector = None
        self.blockchain_connector = None
        self.ml_connector = None
        self.data_feed_connector = None
        
        # Integration status tracking
        self.integration_statuses: Dict[str, IntegrationStatus] = {}
        
        # Data synchronization
        self.sync_queue = asyncio.Queue()
        self.command_queue = asyncio.Queue()
        
        # Background tasks
        self.integration_tasks = []
        self.running = False
        
        logger.info("Integration Framework initialized")
    
    async def initialize(self):
        """Initialize all integration components"""
        try:
            logger.info("Initializing Integration Framework...")
            
            # Initialize HFT Engine Connector
            if self.integration_config.hft_engine_enabled:
                self.hft_connector = HFTEngineConnector(
                    self.config.get('hft_engine_config', {})
                )
                await self.hft_connector.initialize()
                self._update_integration_status('hft_engine', True, True, None, "HFT Engine connected")
            
            # Initialize DAO Governance Connector
            if self.integration_config.dao_governance_enabled:
                self.dao_connector = DAOGovernanceConnector(
                    self.config.get('dao_governance_config', {})
                )
                await self.dao_connector.initialize()
                self._update_integration_status('dao_governance', True, True, None, "DAO Governance connected")
            
            # Initialize Blockchain Connector
            if self.integration_config.blockchain_enabled:
                self.blockchain_connector = BlockchainConnector(
                    self.config.get('blockchain_config', {})
                )
                await self.blockchain_connector.initialize()
                self._update_integration_status('blockchain', True, True, None, "Blockchain connected")
            
            # Initialize ML Models Connector
            if self.integration_config.ml_models_enabled:
                self.ml_connector = MLModelsConnector(
                    self.config.get('ml_models_config', {})
                )
                await self.ml_connector.initialize()
                self._update_integration_status('ml_models', True, True, None, "ML Models connected")
            
            # Initialize Data Feed Connector
            if self.integration_config.external_feeds_enabled:
                self.data_feed_connector = DataFeedConnector(
                    self.config.get('external_feeds_config', {})
                )
                await self.data_feed_connector.initialize()
                self._update_integration_status('external_feeds', True, True, None, "External Feeds connected")
            
            # Start background integration tasks
            await self._start_integration_tasks()
            
            logger.info("Integration Framework initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Integration Framework: {e}")
            raise
    
    async def start(self):
        """Start integration framework"""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting Integration Framework...")
        
        # Start synchronization loops
        asyncio.create_task(self._data_synchronization_loop())
        asyncio.create_task(self._command_processing_loop())
        
        # Start health monitoring
        asyncio.create_task(self._health_monitoring_loop())
    
    async def stop(self):
        """Stop integration framework"""
        self.running = False
        
        # Stop all integration components
        if self.hft_connector:
            await self.hft_connector.stop()
        if self.dao_connector:
            await self.dao_connector.stop()
        if self.blockchain_connector:
            await self.blockchain_connector.stop()
        if self.ml_connector:
            await self.ml_connector.stop()
        if self.data_feed_connector:
            await self.data_feed_connector.stop()
        
        # Cancel background tasks
        for task in self.integration_tasks:
            task.cancel()
        
        logger.info("Integration Framework stopped")
    
    async def send_risk_control_signal(self, signal_type: str, 
                                     signal_data: Dict[str, Any]) -> bool:
        """Send risk control signal to integrated systems"""
        try:
            # Queue the command for processing
            await self.command_queue.put({
                'type': 'risk_control_signal',
                'signal_type': signal_type,
                'data': signal_data,
                'timestamp': datetime.now()
            })
            
            logger.info(f"Queued risk control signal: {signal_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error queuing risk control signal: {e}")
            return False
    
    async def request_hft_position_adjustment(self, symbol: str, 
                                            target_position: float,
                                            reason: str = "risk_management") -> bool:
        """Request HFT engine to adjust position"""
        try:
            if not self.hft_connector:
                logger.warning("HFT Engine connector not available")
                return False
            
            return await self.hft_connector.adjust_position(
                symbol, target_position, reason
            )
            
        except Exception as e:
            logger.error(f"Error requesting HFT position adjustment: {e}")
            return False
    
    async def request_emergency_position_close(self, symbol: str, 
                                             reason: str = "risk_limit_breach") -> bool:
        """Request emergency position closure"""
        try:
            # Send to all relevant systems
            tasks = []
            
            # HFT Engine
            if self.hft_connector:
                tasks.append(
                    self.hft_connector.close_position(symbol, reason)
                )
            
            # DAO Governance (for transparency)
            if self.dao_connector:
                tasks.append(
                    self.dao_connector.record_emergency_action(symbol, "close_position", reason)
                )
            
            # Blockchain (for audit trail)
            if self.blockchain_connector:
                tasks.append(
                    self.blockchain_connector.record_action("position_close", {
                        'symbol': symbol,
                        'reason': reason,
                        'timestamp': datetime.now().isoformat()
                    })
                )
            
            # Execute all requests
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum(1 for result in results if result is True)
            logger.info(f"Emergency position close completed: {success_count}/{len(tasks)} successful")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error requesting emergency position close: {e}")
            return False
    
    async def get_external_risk_data(self) -> Dict[str, Any]:
        """Get risk data from external sources"""
        try:
            external_data = {}
            
            # ML Models risk predictions
            if self.ml_connector:
                try:
                    ml_predictions = await self.ml_connector.get_risk_predictions()
                    external_data['ml_predictions'] = ml_predictions
                except Exception as e:
                    logger.error(f"Error getting ML predictions: {e}")
            
            # Blockchain risk data
            if self.blockchain_connector:
                try:
                    blockchain_risk = await self.blockchain_connector.get_blockchain_risk_data()
                    external_data['blockchain_risk'] = blockchain_risk
                except Exception as e:
                    logger.error(f"Error getting blockchain risk data: {e}")
            
            # DAO governance decisions
            if self.dao_connector:
                try:
                    dao_decisions = await self.dao_connector.get_recent_decisions()
                    external_data['dao_decisions'] = dao_decisions
                except Exception as e:
                    logger.error(f"Error getting DAO decisions: {e}")
            
            # External market data feeds
            if self.data_feed_connector:
                try:
                    market_data = await self.data_feed_connector.get_latest_data()
                    external_data['external_market_data'] = market_data
                except Exception as e:
                    logger.error(f"Error getting external market data: {e}")
            
            return external_data
            
        except Exception as e:
            logger.error(f"Error getting external risk data: {e}")
            return {}
    
    async def submit_governance_proposal(self, proposal_data: Dict[str, Any]) -> bool:
        """Submit governance proposal through DAO connector"""
        try:
            if not self.dao_connector:
                logger.warning("DAO Governance connector not available")
                return False
            
            return await self.dao_connector.submit_proposal(proposal_data)
            
        except Exception as e:
            logger.error(f"Error submitting governance proposal: {e}")
            return False
    
    async def record_blockchain_audit_event(self, event_type: str, 
                                          event_data: Dict[str, Any]) -> bool:
        """Record audit event on blockchain"""
        try:
            if not self.blockchain_connector:
                logger.warning("Blockchain connector not available")
                return False
            
            return await self.blockchain_connector.record_event(event_type, event_data)
            
        except Exception as e:
            logger.error(f"Error recording blockchain audit event: {e}")
            return False
    
    # Background Integration Tasks
    
    async def _start_integration_tasks(self):
        """Start background integration tasks"""
        if self.hft_connector:
            self.integration_tasks.append(
                asyncio.create_task(self.hft_connector.monitor_connection())
            )
        
        if self.dao_connector:
            self.integration_tasks.append(
                asyncio.create_task(self.dao_connector.monitor_governance())
            )
        
        if self.blockchain_connector:
            self.integration_tasks.append(
                asyncio.create_task(self.blockchain_connector.monitor_blockchain())
            )
        
        if self.ml_connector:
            self.integration_tasks.append(
                asyncio.create_task(self.ml_connector.monitor_models())
            )
        
        if self.data_feed_connector:
            self.integration_tasks.append(
                asyncio.create_task(self.data_feed_connector.monitor_feeds())
            )
        
        logger.info(f"Started {len(self.integration_tasks)} integration tasks")
    
    async def _data_synchronization_loop(self):
        """Background data synchronization loop"""
        while self.running:
            try:
                await asyncio.sleep(self.integration_config.integration_interval)
                
                # Sync position data with HFT engine
                if self.hft_connector:
                    await self._sync_position_data()
                
                # Sync market data with external feeds
                if self.data_feed_connector:
                    await self._sync_market_data()
                
                # Sync ML model updates
                if self.ml_connector:
                    await self._sync_ml_models()
                
            except Exception as e:
                logger.error(f"Error in data synchronization loop: {e}")
                await asyncio.sleep(10)
    
    async def _command_processing_loop(self):
        """Background command processing loop"""
        while self.running:
            try:
                # Process queued commands
                while not self.command_queue.empty():
                    command = await self.command_queue.get()
                    await self._process_command(command)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in command processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""
        while self.running:
            try:
                await self._check_integration_health()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(60)
    
    # Helper Methods
    
    def _update_integration_status(self, component_name: str, enabled: bool, 
                                 connected: bool, last_sync: Optional[datetime],
                                 status_message: str):
        """Update integration status"""
        self.integration_statuses[component_name] = IntegrationStatus(
            component_name=component_name,
            enabled=enabled,
            connected=connected,
            last_sync=last_sync,
            error_count=0,
            status_message=status_message
        )
    
    async def _sync_position_data(self):
        """Synchronize position data with HFT engine"""
        try:
            # This would sync current positions with HFT engine
            logger.debug("Syncing position data with HFT engine")
            
        except Exception as e:
            logger.error(f"Error syncing position data: {e}")
    
    async def _sync_market_data(self):
        """Synchronize market data from external feeds"""
        try:
            # This would get latest market data from external feeds
            logger.debug("Syncing market data from external feeds")
            
        except Exception as e:
            logger.error(f"Error syncing market data: {e}")
    
    async def _sync_ml_models(self):
        """Synchronize ML model updates"""
        try:
            # This would check for ML model updates
            logger.debug("Syncing ML model updates")
            
        except Exception as e:
            logger.error(f"Error syncing ML models: {e}")
    
    async def _process_command(self, command: Dict[str, Any]):
        """Process queued command"""
        try:
            command_type = command.get('type')
            
            if command_type == 'risk_control_signal':
                signal_type = command.get('signal_type')
                signal_data = command.get('data', {})
                
                # Process risk control signal
                await self._process_risk_control_signal(signal_type, signal_data)
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
    
    async def _process_risk_control_signal(self, signal_type: str, signal_data: Dict[str, Any]):
        """Process risk control signal"""
        try:
            if signal_type == 'position_adjustment':
                symbol = signal_data.get('symbol')
                target_position = signal_data.get('target_position')
                
                if symbol and target_position is not None:
                    await self.request_hft_position_adjustment(symbol, target_position)
            
            elif signal_type == 'emergency_close':
                symbol = signal_data.get('symbol')
                
                if symbol:
                    await self.request_emergency_position_close(symbol)
            
        except Exception as e:
            logger.error(f"Error processing risk control signal: {e}")
    
    async def _check_integration_health(self):
        """Check health of all integration components"""
        try:
            health_status = {}
            
            # Check HFT Engine
            if self.hft_connector:
                health_status['hft_engine'] = await self.hft_connector.health_check()
            
            # Check DAO Governance
            if self.dao_connector:
                health_status['dao_governance'] = await self.dao_connector.health_check()
            
            # Check Blockchain
            if self.blockchain_connector:
                health_status['blockchain'] = await self.blockchain_connector.health_check()
            
            # Check ML Models
            if self.ml_connector:
                health_status['ml_models'] = await self.ml_connector.health_check()
            
            # Check External Feeds
            if self.data_feed_connector:
                health_status['external_feeds'] = await self.data_feed_connector.health_check()
            
            # Log health summary
            healthy_count = sum(1 for status in health_status.values() if status.get('healthy', False))
            total_count = len(health_status)
            
            logger.info(f"Integration health check: {healthy_count}/{total_count} components healthy")
            
        except Exception as e:
            logger.error(f"Error checking integration health: {e}")
    
    # Utility Methods
    
    async def get_integration_summary(self) -> Dict[str, Any]:
        """Get integration framework summary"""
        return {
            'timestamp': datetime.now(),
            'framework_running': self.running,
            'configured_integrations': {
                'hft_engine': self.integration_config.hft_engine_enabled,
                'dao_governance': self.integration_config.dao_governance_enabled,
                'blockchain': self.integration_config.blockchain_enabled,
                'ml_models': self.integration_config.ml_models_enabled,
                'external_feeds': self.integration_config.external_feeds_enabled
            },
            'integration_statuses': {
                name: {
                    'enabled': status.enabled,
                    'connected': status.connected,
                    'last_sync': status.last_sync.isoformat() if status.last_sync else None,
                    'error_count': status.error_count,
                    'status_message': status.status_message
                }
                for name, status in self.integration_statuses.items()
            },
            'queue_sizes': {
                'sync_queue': self.sync_queue.qsize(),
                'command_queue': self.command_queue.qsize()
            }
        }
    
    async def export_integration_data(self, format_type: str = 'json') -> str:
        """Export integration data and logs"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'integration_summary': await self.get_integration_summary(),
            'recent_commands': [],  # Would include recent command history
            'recent_sync_events': [],  # Would include recent sync events
            'error_log': []  # Would include recent errors
        }
        
        if format_type.lower() == 'json':
            import json
            return json.dumps(export_data, indent=2, default=str)
        else:
            return str(export_data)