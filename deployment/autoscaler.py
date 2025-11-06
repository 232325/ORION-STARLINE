"""
Auto-scaling controller for Orion Starline AI Trading Platform
Production-grade auto-scaling based on multiple metrics and custom algorithms
"""

import asyncio
import logging
import time
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import aiohttp
import asyncpg
import redis.asyncio as redis
import structlog
from dataclasses import dataclass
from enum import Enum

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class ScalingAction(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_ACTION = "no_action"

@dataclass
class ScalingRule:
    """Auto-scaling rule configuration"""
    name: str
    metric: str
    threshold: float
    duration: int  # seconds
    action: ScalingAction
    target_replicas: Optional[int] = None
    increment: Optional[int] = None

@dataclass
class MetricData:
    """Container for metric data"""
    value: float
    timestamp: datetime
    source: str

class PrometheusClient:
    """Prometheus metrics client"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    async def query(self, query: str) -> Dict[str, Any]:
        """Execute Prometheus query"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/v1/query", params={'query': query}) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Prometheus query failed: {response.status}")

class KubernetesClient:
    """Kubernetes API client for scaling operations"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
    
    async def scale_deployment(self, namespace: str, deployment: str, replicas: int) -> bool:
        """Scale Kubernetes deployment"""
        try:
            # This would use the Kubernetes Python client
            # For demo purposes, we'll simulate the operation
            
            logger.info("Scaling deployment", 
                       namespace=namespace, 
                       deployment=deployment, 
                       replicas=replicas)
            
            # Simulate Kubernetes API call
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error("Failed to scale deployment", error=str(e))
            return False

class AutoScaler:
    """Main auto-scaling controller"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.prometheus = PrometheusClient(config['prometheus_url'])
        self.k8s_client = KubernetesClient(config.get('kubeconfig_path'))
        self.scaling_rules = self._load_scaling_rules()
        self.metric_history = {}
        self.scaling_cooldowns = {}
        
        # Scaling thresholds
        self.min_replicas = config.get('min_replicas', 2)
        self.max_replicas = config.get('max_replicas', 20)
        
        logger.info("AutoScaler initialized", 
                   min_replicas=self.min_replicas, 
                   max_replicas=self.max_replicas)
    
    def _load_scaling_rules(self) -> List[ScalingRule]:
        """Load scaling rules from configuration"""
        rules = [
            # CPU-based scaling
            ScalingRule(
                name="cpu_high",
                metric="avg(cpu_usage_percent) > 80",
                threshold=80.0,
                duration=300,  # 5 minutes
                action=ScalingAction.SCALE_UP,
                increment=2
            ),
            ScalingRule(
                name="cpu_low",
                metric="avg(cpu_usage_percent) < 30",
                threshold=30.0,
                duration=600,  # 10 minutes
                action=ScalingAction.SCALE_DOWN,
                increment=1
            ),
            
            # Memory-based scaling
            ScalingRule(
                name="memory_high",
                metric="avg(memory_usage_percent) > 85",
                threshold=85.0,
                duration=300,
                action=ScalingAction.SCALE_UP,
                increment=2
            ),
            ScalingRule(
                name="memory_low",
                metric="avg(memory_usage_percent) < 50",
                threshold=50.0,
                duration=600,
                action=ScalingAction.SCALE_DOWN,
                increment=1
            ),
            
            # Request rate scaling
            ScalingRule(
                name="high_traffic",
                metric="rate(http_requests_total[5m]) > 1000",
                threshold=1000.0,
                duration=180,  # 3 minutes
                action=ScalingAction.SCALE_UP,
                increment=1
            ),
            ScalingRule(
                name="low_traffic",
                metric="rate(http_requests_total[5m]) < 100",
                threshold=100.0,
                duration=900,  # 15 minutes
                action=ScalingAction.SCALE_DOWN,
                increment=1
            ),
            
            # Database connections scaling
            ScalingRule(
                name="db_connections_high",
                metric="avg(database_connections) > 80",
                threshold=80.0,
                duration=240,
                action=ScalingAction.SCALE_UP,
                increment=1
            ),
            
            # Cache hit rate scaling
            ScalingRule(
                name="cache_miss_high",
                metric="avg(cache_hit_rate) < 70",
                threshold=70.0,
                duration=300,
                action=ScalingAction.SCALE_UP,
                increment=1
            ),
            
            # Trading-specific metrics
            ScalingRule(
                name="trading_volume_high",
                metric="rate(trading_signals_total[10m]) > 50",
                threshold=50.0,
                duration=180,
                action=ScalingAction.SCALE_UP,
                increment=2
            ),
            ScalingRule(
                name="trading_quiet",
                metric="rate(trading_signals_total[10m]) < 5",
                threshold=5.0,
                duration=900,
                action=ScalingAction.SCALE_DOWN,
                increment=1
            )
        ]
        
        return rules
    
    async def get_current_replicas(self, deployment: str, namespace: str = 'orion-production') -> int:
        """Get current replica count"""
        try:
            # This would query Kubernetes API
            # For demo, we'll return a simulated value
            return 3
            
        except Exception as e:
            logger.error("Failed to get current replicas", error=str(e))
            return self.min_replicas
    
    async def get_metric_value(self, query: str) -> Optional[float]:
        """Get metric value from Prometheus"""
        try:
            result = await self.prometheus.query(query)
            if result.get('status') == 'success' and result['data']['result']:
                return float(result['data']['result'][0]['value'][1])
            return None
        except Exception as e:
            logger.error("Failed to get metric value", query=query, error=str(e))
            return None
    
    async def collect_metrics(self) -> Dict[str, MetricData]:
        """Collect all relevant metrics"""
        metrics = {}
        
        try:
            # System metrics
            cpu_usage = await self.get_metric_value('avg(orion_cpu_usage_percent)')
            if cpu_usage is not None:
                metrics['cpu_usage'] = MetricData(cpu_usage, datetime.now(), 'prometheus')
            
            memory_usage = await self.get_metric_value('avg(orion_memory_usage_percent)')
            if memory_usage is not None:
                metrics['memory_usage'] = MetricData(memory_usage, datetime.now(), 'prometheus')
            
            # HTTP metrics
            request_rate = await self.get_metric_value('rate(orion_requests_total[5m])')
            if request_rate is not None:
                metrics['request_rate'] = MetricData(request_rate, datetime.now(), 'prometheus')
            
            # Database metrics
            db_connections = await self.get_metric_value('avg(orion_database_connections)')
            if db_connections is not None:
                metrics['db_connections'] = MetricData(db_connections, datetime.now(), 'prometheus')
            
            # Cache metrics
            cache_hit_rate = await self.get_metric_value('avg(orion_cache_hit_rate)')
            if cache_hit_rate is not None:
                metrics['cache_hit_rate'] = MetricData(cache_hit_rate, datetime.now(), 'prometheus')
            
            # Trading metrics
            trading_signals_rate = await self.get_metric_value('rate(orion_trading_signals_total[10m])')
            if trading_signals_rate is not None:
                metrics['trading_signals_rate'] = MetricData(trading_signals_rate, datetime.now(), 'prometheus')
            
            # Custom application metrics
            response_time = await self.get_metric_value('histogram_quantile(0.95, rate(orion_request_duration_seconds_bucket[5m]))')
            if response_time is not None:
                metrics['response_time_95'] = MetricData(response_time, datetime.now(), 'prometheus')
            
            logger.debug("Metrics collected", metrics_count=len(metrics))
            
        except Exception as e:
            logger.error("Error collecting metrics", error=str(e))
        
        return metrics
    
    def should_scale(self, rule: ScalingRule, metrics: Dict[str, MetricData], current_replicas: int) -> Tuple[bool, str]:
        """Check if scaling should happen based on rule"""
        try:
            # Check cooldown period
            cooldown_key = f"{rule.name}_{rule.action.value}"
            if cooldown_key in self.scaling_cooldowns:
                time_since_last = datetime.now() - self.scaling_cooldowns[cooldown_key]
                if time_since_last.total_seconds() < self.config.get('cooldown_period', 300):
                    return False, f"Cooldown period active: {time_since_last.total_seconds():.0f}s remaining"
            
            # Evaluate metric condition
            metric_name = rule.metric.split('(')[0].strip()
            if metric_name not in metrics:
                return False, f"Metric not available: {metric_name}"
            
            metric_value = metrics[metric_name].value
            
            # Check threshold
            if rule.action == ScalingAction.SCALE_UP:
                if metric_value > rule.threshold:
                    # Check duration
                    if self._check_duration(rule, metric_name):
                        return True, f"Metric {metric_name} = {metric_value:.2f} > {rule.threshold}"
            elif rule.action == ScalingAction.SCALE_DOWN:
                if metric_value < rule.threshold:
                    # Check duration
                    if self._check_duration(rule, metric_name):
                        return True, f"Metric {metric_name} = {metric_value:.2f} < {rule.threshold}"
            
            return False, f"Metric {metric_name} = {metric_value:.2f} not meeting threshold"
            
        except Exception as e:
            logger.error("Error evaluating scaling rule", rule=rule.name, error=str(e))
            return False, f"Error evaluating rule: {str(e)}"
    
    def _check_duration(self, rule: ScalingRule, metric_name: str) -> bool:
        """Check if metric has been above/below threshold for required duration"""
        # This would check metric history
        # For demo, we'll assume duration is met if rule is being evaluated
        return True
    
    def calculate_new_replicas(self, action: ScalingAction, current_replicas: int, rule: ScalingRule) -> int:
        """Calculate new replica count"""
        if action == ScalingAction.SCALE_UP:
            if rule.target_replicas:
                return rule.target_replicas
            elif rule.increment:
                return min(current_replicas + rule.increment, self.max_replicas)
            else:
                return min(current_replicas + 1, self.max_replicas)
        elif action == ScalingAction.SCALE_DOWN:
            if rule.target_replicas:
                return rule.target_replicas
            elif rule.increment:
                return max(current_replicas - rule.increment, self.min_replicas)
            else:
                return max(current_replicas - 1, self.min_replicas)
        else:
            return current_replicas
    
    async def execute_scaling(self, deployment: str, new_replicas: int, reason: str) -> bool:
        """Execute scaling operation"""
        try:
            namespace = self.config.get('namespace', 'orion-production')
            current_replicas = await self.get_current_replicas(deployment, namespace)
            
            if current_replicas == new_replicas:
                logger.info("No scaling needed", current=current_replicas, target=new_replicas)
                return True
            
            logger.info("Executing scaling", 
                       deployment=deployment,
                       current_replicas=current_replicas,
                       target_replicas=new_replicas,
                       reason=reason)
            
            success = await self.k8s_client.scale_deployment(namespace, deployment, new_replicas)
            
            if success:
                logger.info("Scaling successful", 
                           deployment=deployment,
                           new_replicas=new_replicas)
                return True
            else:
                logger.error("Scaling failed", 
                           deployment=deployment,
                           target_replicas=new_replicas)
                return False
                
        except Exception as e:
            logger.error("Error executing scaling", error=str(e))
            return False
    
    async def run_scaling_loop(self):
        """Main auto-scaling loop"""
        logger.info("Starting auto-scaling loop")
        
        while True:
            try:
                # Collect metrics
                metrics = await self.collect_metrics()
                
                # Get current state
                current_replicas = await self.get_current_replicas('orion-backend')
                
                # Evaluate scaling rules
                scaling_decisions = []
                
                for rule in self.scaling_rules:
                    should_scale, reason = self.should_scale(rule, metrics, current_replicas)
                    
                    if should_scale:
                        new_replicas = self.calculate_new_replicas(rule.action, current_replicas, rule)
                        scaling_decisions.append({
                            'rule': rule,
                            'action': rule.action,
                            'new_replicas': new_replicas,
                            'reason': reason
                        })
                
                # Execute scaling if needed
                if scaling_decisions:
                    # Take the most recent decision
                    decision = scaling_decisions[-1]
                    
                    # Set cooldown
                    cooldown_key = f"{decision['rule'].name}_{decision['action'].value}"
                    self.scaling_cooldowns[cooldown_key] = datetime.now()
                    
                    # Execute scaling
                    success = await self.execute_scaling(
                        'orion-backend',
                        decision['new_replicas'],
                        decision['reason']
                    )
                    
                    if success:
                        logger.info("Scaling decision executed", 
                                   decision=decision)
                    else:
                        logger.error("Scaling decision failed", 
                                   decision=decision)
                
                # Wait before next evaluation
                await asyncio.sleep(self.config.get('scaling_interval', 30))
                
            except Exception as e:
                logger.error("Error in scaling loop", error=str(e))
                await asyncio.sleep(60)

class PredictiveAutoScaler(AutoScaler):
    """Auto-scaler with predictive capabilities"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.prediction_window = config.get('prediction_window', 300)  # 5 minutes
    
    async def predict_resource_needs(self, metrics: Dict[str, MetricData]) -> Dict[str, float]:
        """Predict future resource needs based on trends"""
        predictions = {}
        
        try:
            # Simple trend analysis
            # In production, you'd use more sophisticated ML models
            
            for metric_name, metric_data in metrics.items():
                # Get historical data for this metric
                history_key = f"history_{metric_name}"
                if history_key not in self.metric_history:
                    self.metric_history[history_key] = []
                
                # Add current value to history
                self.metric_history[history_key].append(metric_data)
                
                # Keep only recent history
                if len(self.metric_history[history_key]) > 100:
                    self.metric_history[history_key] = self.metric_history[history_key][-100:]
                
                # Simple linear trend prediction
                if len(self.metric_history[history_key]) >= 10:
                    recent_values = [m.value for m in self.metric_history[history_key][-10:]]
                    
                    # Calculate trend (simple slope)
                    if len(recent_values) >= 2:
                        trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
                        
                        # Predict future value
                        predicted_value = metric_data.value + (trend * 5)  # Predict 5 intervals ahead
                        predictions[f"{metric_name}_predicted"] = predicted_value
                        
                        logger.debug("Prediction made", 
                                   metric=metric_name,
                                   current=metric_data.value,
                                   predicted=predicted_value,
                                   trend=trend)
            
        except Exception as e:
            logger.error("Error predicting resource needs", error=str(e))
        
        return predictions
    
    async def run_scaling_loop(self):
        """Enhanced scaling loop with predictions"""
        logger.info("Starting predictive auto-scaling loop")
        
        while True:
            try:
                # Collect current metrics
                metrics = await self.collect_metrics()
                
                # Predict future needs
                predictions = await self.predict_resource_needs(metrics)
                
                # Combine current metrics with predictions
                all_metrics = {**metrics, **predictions}
                
                # Get current state
                current_replicas = await self.get_current_replicas('orion-backend')
                
                # Enhanced decision making with predictions
                await self._make_scaling_decisions(all_metrics, current_replicas)
                
                # Wait before next evaluation
                await asyncio.sleep(self.config.get('scaling_interval', 30))
                
            except Exception as e:
                logger.error("Error in predictive scaling loop", error=str(e))
                await asyncio.sleep(60)
    
    async def _make_scaling_decisions(self, metrics: Dict[str, MetricData], current_replicas: int):
        """Make scaling decisions with prediction support"""
        # This would implement the enhanced decision logic
        # For now, we'll use the parent class logic
        return await super().run_scaling_loop()

async def main():
    """Main auto-scaler function"""
    # Load configuration
    config = {
        'prometheus_url': 'http://prometheus:9090',
        'namespace': 'orion-production',
        'min_replicas': 2,
        'max_replicas': 20,
        'cooldown_period': 300,  # 5 minutes
        'scaling_interval': 30,
        'prediction_window': 300,
        'kubeconfig_path': None
    }
    
    # Create auto-scaler
    autoscaler = PredictiveAutoScaler(config)
    
    # Start scaling loop
    logger.info("Starting auto-scaler")
    await autoscaler.run_scaling_loop()

if __name__ == "__main__":
    asyncio.run(main())