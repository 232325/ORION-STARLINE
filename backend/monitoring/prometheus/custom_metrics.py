#!/usr/bin/env python3
"""
Prometheus Metrics Integration
Custom business va technical metriklarni Prometheus formatida eksport qilish
"""

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
import json
from collections import defaultdict

@dataclass
class PrometheusMetric:
    """Prometheus metric definition"""
    name: str
    type: str  # counter, gauge, histogram, summary
    description: str
    value: float
    labels: Dict[str, str]
    timestamp: float
    
    def to_prometheus_line(self) -> str:
        """Prometheus formatiga konversiya"""
        labels_str = ""
        if self.labels:
            label_pairs = [f'{k}="{v}"' for k, v in self.labels.items()]
            labels_str = "{" + ",".join(label_pairs) + "}"
        
        return f"{self.name}{labels_str} {self.value} {int(self.timestamp * 1000)}"

class CustomMetricsCollector:
    """Custom business va technical metriklarni to'plash"""
    
    def __init__(self):
        self.metrics: Dict[str, PrometheusMetric] = {}
        self.metrics_lock = threading.Lock()
        self.business_metrics = BusinessMetrics()
        self.technical_metrics = TechnicalMetrics()
        
    def record_business_metric(self, metric_name: str, value: float, 
                             labels: Optional[Dict[str, str]] = None,
                             metric_type: str = "gauge"):
        """Business metric ni qayd etish"""
        labels = labels or {}
        metric = PrometheusMetric(
            name=metric_name,
            type=metric_type,
            description=f"Business metric: {metric_name}",
            value=value,
            labels=labels,
            timestamp=time.time()
        )
        
        with self.metrics_lock:
            self.metrics[metric_name] = metric
        
        # Technical metrics ham yangilash
        self.technical_metrics.update_metric_count()
        
    def record_technical_metric(self, metric_name: str, value: float,
                              labels: Optional[Dict[str, str]] = None,
                              metric_type: str = "gauge"):
        """Technical metric ni qayd etish"""
        labels = labels or {}
        metric = PrometheusMetric(
            name=f"tech_{metric_name}",
            type=metric_type,
            description=f"Technical metric: {metric_name}",
            value=value,
            labels=labels,
            timestamp=time.time()
        )
        
        with self.metrics_lock:
            self.metrics[f"tech_{metric_name}"] = metric
    
    def get_all_metrics(self) -> List[PrometheusMetric]:
        """Barcha metriklarni olish"""
        with self.metrics_lock:
            return list(self.metrics.values())
    
    def export_prometheus_format(self) -> str:
        """Prometheus formatida eksport qilish"""
        lines = []
        
        # Help lines
        for metric in self.get_all_metrics():
            lines.append(f"# HELP {metric.name} {metric.description}")
            lines.append(f"# TYPE {metric.name} {metric.type}")
            lines.append(metric.to_prometheus_line())
        
        return "\n".join(lines) + "\n"

class BusinessMetrics:
    """Business domain metriqlari"""
    
    def __init__(self):
        self.trading_metrics = TradingMetrics()
        self.user_metrics = UserMetrics()
        self.financial_metrics = FinancialMetrics()
        self.risk_metrics = RiskMetrics()
        
        # Metric collections
        self.metric_counts = defaultdict(int)
        self.time_series_data = defaultdict(list)
    
    def record_trade_execution(self, symbol: str, side: str, quantity: float, 
                             price: float, latency_ms: float):
        """Trade execution qayd etish"""
        self.trading_metrics.record_trade(symbol, side, quantity, price)
        
        # Technical metrics ham
        self.record_technical_business("trade_execution_latency", latency_ms, 
                                     {"symbol": symbol, "side": side})
        self.record_technical_business("trade_executed", 1, 
                                     {"symbol": symbol, "side": side})
    
    def record_trade_volume(self, symbol: str, volume: float):
        """Trade volume qayd etish"""
        self.trading_metrics.record_volume(symbol, volume)
    
    def record_user_action(self, action: str, user_id: str, 
                          success: bool, response_time_ms: float):
        """User action qayd etish"""
        self.user_metrics.record_action(action, user_id, success)
        
        self.record_technical_business("user_action_latency", response_time_ms,
                                     {"action": action, "user_id": user_id, "success": str(success)})
    
    def record_pnl(self, symbol: str, pnl: float):
        """PnL qayd etish"""
        self.financial_metrics.record_pnl(symbol, pnl)
    
    def record_risk_alert(self, alert_type: str, severity: str, 
                         risk_score: float):
        """Risk alert qayd etish"""
        self.risk_metrics.record_alert(alert_type, severity, risk_score)
        
        self.record_technical_business("risk_alert", 1,
                                     {"type": alert_type, "severity": severity})
    
    def record_technical_business(self, metric_name: str, value: float, 
                                labels: Dict[str, str]):
        """Technical business metrics"""
        self.metric_counts[metric_name] += 1
        
        # Time series data saqlash
        timestamp = time.time()
        self.time_series_data[metric_name].append({
            'timestamp': timestamp,
            'value': value,
            'labels': labels
        })
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Business metrics summary"""
        return {
            'trading': self.trading_metrics.get_summary(),
            'users': self.user_metrics.get_summary(),
            'financial': self.financial_metrics.get_summary(),
            'risk': self.risk_metrics.get_summary(),
            'time_series_stats': self._get_time_series_stats()
        }
    
    def _get_time_series_stats(self) -> Dict[str, Any]:
        """Time series statistics"""
        stats = {}
        for metric_name, data_points in self.time_series_data.items():
            if len(data_points) > 0:
                values = [dp['value'] for dp in data_points]
                stats[metric_name] = {
                    'count': len(values),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'latest': values[-1] if values else 0
                }
        return stats

class TechnicalMetrics:
    """Technical system metriqlari"""
    
    def __init__(self):
        self.performance_metrics = {}
        self.system_metrics = {}
        self.application_metrics = {}
        
        self.metric_counters = defaultdict(int)
        self.metric_timers = defaultdict(list)
    
    def update_metric_count(self):
        """Metric count ni yangilash"""
        self.metric_counters['total_metrics_collected'] += 1
    
    def record_response_time(self, endpoint: str, method: str, 
                           response_time_ms: float, status_code: int):
        """Response time qayd etish"""
        key = f"response_time_{endpoint}_{method}"
        self.metric_timers[key].append(response_time_ms)
        
        # Faqat oxirgi 1000 ta vaqtni saqlash
        if len(self.metric_timers[key]) > 1000:
            self.metric_timers[key] = self.metric_timers[key][-1000:]
        
        # Error status kodlarini alohida qayd etish
        if status_code >= 400:
            self.metric_counters[f"errors_{endpoint}'] += 1
    
    def record_database_query(self, query_type: str, table: str, 
                            execution_time_ms: float, rows_affected: int):
        """Database query qayd etish"""
        self.metric_timers[f"db_query_{query_type}_{table}"].append(execution_time_ms)
        self.metric_counters[f"db_queries_{query_type}"] += 1
        
        if len(self.metric_timers[f"db_query_{query_type}_{table}"]) > 1000:
            self.metric_timers[f"db_query_{query_type}_{table}"] = \
                self.metric_timers[f"db_query_{query_type}_{table}"][-1000:]
    
    def record_memory_usage(self, component: str, memory_mb: float):
        """Memory usage qayd etish"""
        self.performance_metrics[f'memory_{component}'] = memory_mb
    
    def record_cpu_usage(self, component: str, cpu_percent: float):
        """CPU usage qayd etish"""
        self.performance_metrics[f'cpu_{component}'] = cpu_percent
    
    def get_technical_summary(self) -> Dict[str, Any]:
        """Technical metrics summary"""
        response_time_stats = {}
        for key, times in self.metric_timers.items():
            if times:
                response_time_stats[key] = {
                    'count': len(times),
                    'avg_ms': sum(times) / len(times),
                    'p95_ms': self._calculate_percentile(times, 95),
                    'p99_ms': self._calculate_percentile(times, 99),
                    'min_ms': min(times),
                    'max_ms': max(times)
                }
        
        return {
            'counters': dict(self.metric_counters),
            'performance': dict(self.performance_metrics),
            'response_times': response_time_stats,
            'total_metrics_collected': self.metric_counters['total_metrics_collected']
        }
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Percentile hisoblash"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

class TradingMetrics:
    """Trading-specific metriqlari"""
    
    def __init__(self):
        self.trades = []
        self.volumes = defaultdict(float)
        self.symbols = set()
    
    def record_trade(self, symbol: str, side: str, quantity: float, price: float):
        """Trade qayd etish"""
        trade = {
            'timestamp': time.time(),
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'value': quantity * price
        }
        self.trades.append(trade)
        self.symbols.add(symbol)
        
        # Faqat oxirgi 1000 ta trade ni saqlash
        if len(self.trades) > 1000:
            self.trades = self.trades[-1000:]
    
    def record_volume(self, symbol: str, volume: float):
        """Volume qayd etish"""
        self.volumes[symbol] += volume
    
    def get_summary(self) -> Dict[str, Any]:
        """Trading summary"""
        if not self.trades:
            return {'trades_count': 0}
        
        recent_trades = [t for t in self.trades 
                        if time.time() - t['timestamp'] < 3600]  # Oxirgi soat
        
        total_volume = sum(volume for volume in self.volumes.values())
        total_trades = len(self.trades)
        
        side_counts = defaultdict(int)
        symbol_counts = defaultdict(int)
        
        for trade in self.trades:
            side_counts[trade['side']] += 1
            symbol_counts[trade['symbol']] += 1
        
        return {
            'trades_count': total_trades,
            'recent_trades_1h': len(recent_trades),
            'total_volume': total_volume,
            'unique_symbols': len(self.symbols),
            'side_distribution': dict(side_counts),
            'top_symbols': dict(sorted(symbol_counts.items(), 
                                     key=lambda x: x[1], reverse=True)[:10])
        }

class UserMetrics:
    """User engagement va activity metriqlari"""
    
    def __init__(self):
        self.user_actions = []
        self.user_sessions = defaultdict(list)
        self.active_users = set()
    
    def record_action(self, action: str, user_id: str, success: bool):
        """User action qayd etish"""
        action_record = {
            'timestamp': time.time(),
            'action': action,
            'user_id': user_id,
            'success': success
        }
        self.user_actions.append(action_record)
        self.active_users.add(user_id)
        
        # Faqat oxirgi 1000 ta action ni saqlash
        if len(self.user_actions) > 1000:
            self.user_actions = self.user_actions[-1000:]
        
        # User session tracking
        self.user_sessions[user_id].append(action_record)
        if len(self.user_sessions[user_id]) > 100:
            self.user_sessions[user_id] = self.user_sessions[user_id][-100:]
    
    def get_summary(self) -> Dict[str, Any]:
        """User metrics summary"""
        if not self.user_actions:
            return {'actions_count': 0}
        
        recent_actions = [a for a in self.user_actions 
                         if time.time() - a['timestamp'] < 3600]
        
        action_counts = defaultdict(int)
        success_rate = 0
        if recent_actions:
            successful_actions = sum(1 for a in recent_actions if a['success'])
            success_rate = (successful_actions / len(recent_actions)) * 100
        
        for action in recent_actions:
            action_counts[action['action']] += 1
        
        return {
            'actions_count': len(self.user_actions),
            'recent_actions_1h': len(recent_actions),
            'active_users_count': len(self.active_users),
            'success_rate_percent': success_rate,
            'action_distribution': dict(action_counts)
        }

class FinancialMetrics:
    """Financial va P&L metriqlari"""
    
    def __init__(self):
        self.pnl_records = []
        self.running_pnl = 0.0
        self.symbol_pnl = defaultdict(float)
    
    def record_pnl(self, symbol: str, pnl: float):
        """PnL qayd etish"""
        pnl_record = {
            'timestamp': time.time(),
            'symbol': symbol,
            'pnl': pnl
        }
        self.pnl_records.append(pnl_record)
        self.running_pnl += pnl
        self.symbol_pnl[symbol] += pnl
        
        # Faqat oxirgi 1000 ta PnL record ni saqlash
        if len(self.pnl_records) > 1000:
            self.pnl_records = self.pnl_records[-1000:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Financial summary"""
        if not self.pnl_records:
            return {'total_pnl': 0.0}
        
        return {
            'total_pnl': self.running_pnl,
            'pnl_records_count': len(self.pnl_records),
            'symbols_performance': dict(self.symbol_pnl),
            'recent_pnl': self.pnl_records[-10:] if len(self.pnl_records) >= 10 else self.pnl_records
        }

class RiskMetrics:
    """Risk metriqlari va ogohlantirishlar"""
    
    def __init__(self):
        self.risk_alerts = []
        self.risk_scores = []
        self.alert_types = defaultdict(int)
    
    def record_alert(self, alert_type: str, severity: str, risk_score: float):
        """Risk alert qayd etish"""
        alert = {
            'timestamp': time.time(),
            'alert_type': alert_type,
            'severity': severity,
            'risk_score': risk_score
        }
        self.risk_alerts.append(alert)
        self.risk_scores.append(risk_score)
        self.alert_types[alert_type] += 1
        
        # Faqat oxirgi 1000 ta alert ni saqlash
        if len(self.risk_alerts) > 1000:
            self.risk_alerts = self.risk_alerts[-1000:]
            self.risk_scores = self.risk_scores[-1000:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Risk summary"""
        if not self.risk_alerts:
            return {'alerts_count': 0}
        
        recent_alerts = [a for a in self.risk_alerts 
                        if time.time() - a['timestamp'] < 3600]
        
        severity_counts = defaultdict(int)
        for alert in recent_alerts:
            severity_counts[alert['severity']] += 1
        
        return {
            'alerts_count': len(self.risk_alerts),
            'recent_alerts_1h': len(recent_alerts),
            'severity_distribution': dict(severity_counts),
            'alert_types': dict(self.alert_types),
            'avg_risk_score': sum(self.risk_scores) / len(self.risk_scores) if self.risk_scores else 0,
            'max_risk_score': max(self.risk_scores) if self.risk_scores else 0
        }

class PrometheusExporter:
    """Prometheus metrics exporter"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.custom_collector = CustomMetricsCollector()
        self.exporter_thread = None
        self.running = False
        
    def start(self):
        """Exporter ni ishga tushirish"""
        if self.running:
            return
        
        self.running = True
        self.exporter_thread = threading.Thread(target=self._run_exporter, daemon=True)
        self.exporter_thread.start()
        logging.info(f"Prometheus exporter port {self.port} da ishga tushdi")
    
    def stop(self):
        """Exporter ni to'xtatish"""
        self.running = False
        if self.exporter_thread:
            self.exporter_thread.join(timeout=5)
        logging.info("Prometheus exporter to'xtatildi")
    
    def _run_exporter(self):
        """Exporter loop"""
        # Bu oddiy HTTP server bo'lishi kerak
        # Hozircha logging qilaylik
        while self.running:
            try:
                # Prometheus metrics export
                metrics_data = self.custom_collector.export_prometheus_format()
                
                # Bu yerda real HTTP server bo'lishi kerak
                # logger.info(f"Exporting {len(self.custom_collector.get_all_metrics())} metrics")
                
                time.sleep(10)  # 10 soniyada export qilish
                
            except Exception as e:
                logging.error(f"Exporter error: {e}")
                time.sleep(5)
    
    def export_current_metrics(self) -> str:
        """Joriy metriklarni export qilish"""
        return self.custom_collector.export_prometheus_format()
    
    def get_custom_metrics(self) -> CustomMetricsCollector:
        """Custom metrics collector olish"""
        return self.custom_collector

class AlertConfiguration:
    """Ogohlantirish konfiguratsiyasi"""
    
    def __init__(self):
        self.alert_rules = {}
        self.notification_channels = {}
        self.alert_templates = {}
        
    def add_alert_rule(self, name: str, condition: str, threshold: float,
                      duration: str, severity: str, labels: Dict[str, str] = None):
        """Alert rule qo'shish"""
        self.alert_rules[name] = {
            'condition': condition,
            'threshold': threshold,
            'duration': duration,
            'severity': severity,
            'labels': labels or {},
            'created_at': datetime.now().isoformat()
        }
    
    def add_notification_channel(self, name: str, channel_type: str, 
                               config: Dict[str, Any]):
        """Notification channel qo'shish"""
        self.notification_channels[name] = {
            'type': channel_type,
            'config': config,
            'created_at': datetime.now().isoformat()
        }
    
    def generate_prometheus_rules(self) -> str:
        """Prometheus alert rules generatsiya qilish"""
        rules_lines = ["groups:"]
        rules_lines.append("- name: application_alerts")
        rules_lines.append("  rules:")
        
        for name, rule in self.alert_rules.items():
            rule_text = f"""
  - alert: {name}
    expr: {rule['condition']} > {rule['threshold']}
    for: {rule['duration']}
    labels:
      severity: {rule['severity']}"""
            
            # Labels qo'shish
            for key, value in rule['labels'].items():
                rule_text += f"\n      {key}: {value}"
            
            rule_text += f"""
    annotations:
      summary: "{name} alert triggered"
      description: "{name} metric has exceeded threshold {rule['threshold']}" """
            
            rules_lines.append(rule_text)
        
        return "\n".join(rules_lines)

# Example usage va test
if __name__ == "__main__":
    # Test Prometheus exporter
    exporter = PrometheusExporter()
    
    try:
        # Exporter ni ishga tushirish
        exporter.start()
        
        # Test metriqlari qo'shish
        custom_metrics = exporter.get_custom_metrics()
        
        # Business metrics
        custom_metrics.record_business_metric("trading_volume", 125000.50, 
                                            {"symbol": "EURUSD", "type": "forex"})
        custom_metrics.record_business_metric("user_active_sessions", 45, 
                                            {"region": "US"})
        
        # Technical metrics
        custom_metrics.record_technical_metric("response_time_ms", 150.5, 
                                            {"endpoint": "/api/trades"})
        custom_metrics.record_technical_metric("db_query_time_ms", 25.3, 
                                            {"table": "trades", "type": "select"})
        
        # Metrics export qilish
        metrics_output = exporter.export_current_metrics()
        print("=== PROMETHEUS METRICS ===")
        print(metrics_output)
        
        # Business summary
        business_summary = custom_metrics.business_metrics.get_business_summary()
        print("\n=== BUSINESS SUMMARY ===")
        print(json.dumps(business_summary, indent=2, default=str))
        
        # Alert rules
        alert_config = AlertConfiguration()
        alert_config.add_alert_rule(
            name="HighResponseTime",
            condition="response_time",
            threshold=500.0,
            duration="5m",
            severity="warning",
            labels={"component": "api", "tier": "frontend"}
        )
        
        prometheus_rules = alert_config.generate_prometheus_rules()
        print("\n=== PROMETHEUS ALERT RULES ===")
        print(prometheus_rules)
        
        # 10 soniya kutish
        time.sleep(10)
        
    finally:
        exporter.stop()