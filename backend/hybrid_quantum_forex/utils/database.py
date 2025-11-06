"""
Database Utilities Module
Ma'lumotlar bazasi moduli
"""
import sqlite3
import json
import os
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
import logging
import threading

from ..config.config import config

logger = logging.getLogger(__name__)

def setup_database():
    """Database setup va initialization"""
    try:
        # Create directory if it doesn't exist
        db_dir = os.path.dirname(config.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        conn = sqlite3.connect(config.db_path)
        cursor = conn.cursor()
        
        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                uptime REAL,
                total_opportunities INTEGER,
                executed_trades INTEGER,
                successful_trades INTEGER,
                failed_trades INTEGER,
                total_profit REAL,
                total_loss REAL,
                avg_latency REAL,
                error_rate REAL,
                quantum_fidelity REAL,
                system_utilization REAL,
                current_positions TEXT,
                unrealized_pnl REAL,
                available_capital REAL
            )
        ''')
        
        # Market data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                pair TEXT NOT NULL,
                bid REAL NOT NULL,
                ask REAL NOT NULL,
                volume REAL,
                volatility REAL,
                session TEXT,
                source TEXT
            )
        ''')
        
        # Arbitrage opportunities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                arbitrage_type TEXT NOT NULL,
                currencies TEXT,
                pairs TEXT,
                rates TEXT,
                profit_potential REAL,
                risk_score REAL,
                time_sensitivity REAL,
                execution_time_estimate REAL,
                quantum_features TEXT,
                status TEXT DEFAULT 'detected',
                executed BOOLEAN DEFAULT FALSE,
                execution_result TEXT
            )
        ''')
        
        # Trade executions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id TEXT,
                timestamp TEXT NOT NULL,
                success BOOLEAN,
                profit REAL,
                loss REAL,
                execution_time REAL,
                slippage REAL,
                trades TEXT,
                total_cost REAL,
                net_profit REAL,
                market_impact REAL,
                FOREIGN KEY (opportunity_id) REFERENCES arbitrage_opportunities (id)
            )
        ''')
        
        # Quantum computation results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quantum_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                circuit_id TEXT,
                result_data TEXT,
                quantum_state TEXT,
                measurement_results TEXT,
                coherence_metrics TEXT,
                processing_time REAL,
                error_correction_applied BOOLEAN,
                market_data_hash TEXT
            )
        ''')
        
        # Risk assessments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                opportunity_id TEXT,
                overall_risk_score REAL,
                market_risk REAL,
                liquidity_risk REAL,
                operational_risk REAL,
                quantum_risk REAL,
                risk_factors TEXT,
                mitigation_strategies TEXT,
                recommendations TEXT,
                FOREIGN KEY (opportunity_id) REFERENCES arbitrage_opportunities (id)
            )
        ''')
        
        # Performance analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                period_start TEXT,
                period_end TEXT,
                total_opportunities INTEGER,
                executed_trades INTEGER,
                total_profit REAL,
                total_loss REAL,
                success_rate REAL,
                avg_profit_per_trade REAL,
                max_drawdown REAL,
                sharpe_ratio REAL,
                quantum_advantage_score REAL,
                system_health_score REAL
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_data_pair ON market_data (pair)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_opportunities_timestamp ON arbitrage_opportunities (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_opportunities_status ON arbitrage_opportunities (status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_timestamp ON trade_executions (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quantum_timestamp ON quantum_results (timestamp)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database setup completed: {config.db_path}")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

class DatabaseManager:
    """Database management class"""
    
    def __init__(self):
        self.db_path = config.db_path
        self._lock = threading.Lock()
        
        # Ensure database is set up
        if not os.path.exists(self.db_path):
            setup_database()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()
                
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                
                conn.close()
                return results
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(query, params)
                affected_rows = cursor.rowcount
                
                conn.commit()
                conn.close()
                
                return affected_rows
                
        except Exception as e:
            logger.error(f"Update execution failed: {e}")
            return 0
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute batch INSERT/UPDATE/DELETE"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.executemany(query, params_list)
                affected_rows = cursor.rowcount
                
                conn.commit()
                conn.close()
                
                return affected_rows
                
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            return 0
    
    def insert_market_data(self, timestamp: datetime, pair: str, bid: float, ask: float, 
                          volume: float = None, volatility: float = None, 
                          session: str = None, source: str = None) -> bool:
        """Insert market data"""
        try:
            query = '''
                INSERT INTO market_data (timestamp, pair, bid, ask, volume, volatility, session, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (timestamp.isoformat(), pair, bid, ask, volume, volatility, session, source)
            return self.execute_update(query, params) > 0
            
        except Exception as e:
            logger.error(f"Failed to insert market data: {e}")
            return False
    
    def get_latest_market_data(self, pair: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get latest market data"""
        try:
            if pair:
                query = '''
                    SELECT * FROM market_data 
                    WHERE pair = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                '''
                params = (pair, limit)
            else:
                query = '''
                    SELECT * FROM market_data 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                '''
                params = (limit,)
            
            return self.execute_query(query, params)
            
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return []
    
    def insert_arbitrage_opportunity(self, opportunity) -> bool:
        """Insert arbitrage opportunity"""
        try:
            query = '''
                INSERT OR REPLACE INTO arbitrage_opportunities 
                (id, timestamp, arbitrage_type, currencies, pairs, rates, profit_potential, 
                 risk_score, time_sensitivity, execution_time_estimate, quantum_features, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                opportunity.id,
                opportunity.timestamp.isoformat(),
                opportunity.arbitrage_type.value,
                json.dumps(opportunity.currencies),
                json.dumps(opportunity.pairs),
                json.dumps(opportunity.rates) if opportunity.rates else None,
                opportunity.calculations.profit_potential if opportunity.calculations else None,
                opportunity.risk_level,
                opportunity.calculations.time_sensitivity if opportunity.calculations else None,
                opportunity.execution_time_estimate,
                json.dumps(opportunity.__dict__),
                'detected'
            )
            return self.execute_update(query, params) > 0
            
        except Exception as e:
            logger.error(f"Failed to insert arbitrage opportunity: {e}")
            return False
    
    def update_opportunity_status(self, opportunity_id: str, status: str, execution_result: str = None) -> bool:
        """Update opportunity status"""
        try:
            if execution_result:
                query = '''
                    UPDATE arbitrage_opportunities 
                    SET status = ?, executed = TRUE, execution_result = ?
                    WHERE id = ?
                '''
                params = (status, execution_result, opportunity_id)
            else:
                query = '''
                    UPDATE arbitrage_opportunities 
                    SET status = ?
                    WHERE id = ?
                '''
                params = (status, opportunity_id)
            
            return self.execute_update(query, params) > 0
            
        except Exception as e:
            logger.error(f"Failed to update opportunity status: {e}")
            return False
    
    def get_opportunities_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get opportunities by status"""
        try:
            query = '''
                SELECT * FROM arbitrage_opportunities 
                WHERE status = ? 
                ORDER BY timestamp DESC
            '''
            return self.execute_query(query, (status,))
            
        except Exception as e:
            logger.error(f"Failed to get opportunities by status: {e}")
            return []
    
    def insert_trade_execution(self, execution) -> bool:
        """Insert trade execution"""
        try:
            query = '''
                INSERT INTO trade_executions 
                (opportunity_id, timestamp, success, profit, loss, execution_time, slippage, 
                 trades, total_cost, net_profit, market_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                execution.opportunity_id,
                datetime.now(timezone.utc).isoformat(),
                execution.success,
                execution.profit,
                execution.loss,
                execution.execution_time,
                execution.slippage,
                json.dumps(execution.trades),
                execution.total_cost,
                execution.net_profit,
                execution.market_impact
            )
            return self.execute_update(query, params) > 0
            
        except Exception as e:
            logger.error(f"Failed to insert trade execution: {e}")
            return False
    
    def insert_quantum_result(self, timestamp: datetime, circuit_id: str, result_data: Dict[str, Any], 
                             quantum_state: Any, measurement_results: Dict[str, Any],
                             coherence_metrics: Dict[str, Any], processing_time: float,
                             error_correction_applied: bool, market_data_hash: str = None) -> bool:
        """Insert quantum computation result"""
        try:
            query = '''
                INSERT INTO quantum_results 
                (timestamp, circuit_id, result_data, quantum_state, measurement_results, 
                 coherence_metrics, processing_time, error_correction_applied, market_data_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                timestamp.isoformat(),
                circuit_id,
                json.dumps(result_data),
                json.dumps(quantum_state.tolist()) if hasattr(quantum_state, 'tolist') else str(quantum_state),
                json.dumps(measurement_results),
                json.dumps(coherence_metrics),
                processing_time,
                error_correction_applied,
                market_data_hash
            )
            return self.execute_update(query, params) > 0
            
        except Exception as e:
            logger.error(f"Failed to insert quantum result: {e}")
            return False
    
    def get_quantum_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get quantum computation results"""
        try:
            query = '''
                SELECT * FROM quantum_results 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            return self.execute_query(query, (limit,))
            
        except Exception as e:
            logger.error(f"Failed to get quantum results: {e}")
            return []
    
    def insert_system_metrics(self, metrics) -> bool:
        """Insert system metrics"""
        try:
            query = '''
                INSERT INTO system_metrics 
                (timestamp, uptime, total_opportunities, executed_trades, successful_trades, 
                 failed_trades, total_profit, total_loss, avg_latency, error_rate, 
                 quantum_fidelity, system_utilization, current_positions, unrealized_pnl, available_capital)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                datetime.now(timezone.utc).isoformat(),
                metrics.uptime,
                metrics.total_opportunities,
                metrics.executed_trades,
                metrics.successful_trades,
                metrics.failed_trades,
                metrics.total_profit,
                metrics.total_loss,
                metrics.total_latency,
                metrics.error_rate,
                metrics.quantum_fidelity,
                metrics.system_utilization,
                json.dumps(metrics.current_positions),
                metrics.unrealized_pnl,
                metrics.available_capital
            )
            return self.execute_update(query, params) > 0
            
        except Exception as e:
            logger.error(f"Failed to insert system metrics: {e}")
            return False
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified hours"""
        try:
            start_time = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
            
            # Get total opportunities and executions
            query = '''
                SELECT 
                    COUNT(*) as total_opportunities,
                    SUM(CASE WHEN status = 'executed' THEN 1 ELSE 0 END) as executed_opportunities,
                    SUM(CASE WHEN executed = TRUE THEN 1 ELSE 0 END) as executed_trades
                FROM arbitrage_opportunities 
                WHERE timestamp >= ?
            '''
            opportunities_result = self.execute_query(query, (start_time,))
            
            # Get execution results
            exec_query = '''
                SELECT 
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) as successful_executions,
                    SUM(net_profit) as total_net_profit,
                    AVG(execution_time) as avg_execution_time
                FROM trade_executions 
                WHERE timestamp >= ?
            '''
            executions_result = self.execute_query(exec_query, (start_time,))
            
            # Get system metrics
            metrics_query = '''
                SELECT 
                    AVG(quantum_fidelity) as avg_quantum_fidelity,
                    AVG(system_utilization) as avg_system_utilization,
                    AVG(error_rate) as avg_error_rate
                FROM system_metrics 
                WHERE timestamp >= ?
            '''
            metrics_result = self.execute_query(metrics_query, (start_time,))
            
            # Combine results
            summary = {
                'period_hours': hours,
                'start_time': start_time,
                'end_time': datetime.now(timezone.utc).isoformat(),
                'opportunities': opportunities_result[0] if opportunities_result else {},
                'executions': executions_result[0] if executions_result else {},
                'system_performance': metrics_result[0] if metrics_result else {}
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """Cleanup old data from database"""
        try:
            cutoff_time = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            # Delete old market data
            query = 'DELETE FROM market_data WHERE timestamp < ?'
            deleted_market = self.execute_update(query, (cutoff_time,))
            
            # Delete old quantum results
            query = 'DELETE FROM quantum_results WHERE timestamp < ?'
            deleted_quantum = self.execute_update(query, (cutoff_time,))
            
            # Delete old system metrics (keep longer for analytics)
            metrics_cutoff = (datetime.now(timezone.utc) - timedelta(days=days * 2)).isoformat()
            query = 'DELETE FROM system_metrics WHERE timestamp < ?'
            deleted_metrics = self.execute_update(query, (cutoff_time,))
            
            # Vacuum database to reclaim space
            self.execute_update('VACUUM', ())
            
            logger.info(f"Cleanup completed - Deleted {deleted_market} market data, {deleted_quantum} quantum results, {deleted_metrics} metrics records")
            
        except Exception as e:
            logger.error(f"Database cleanup failed: {e}")
    
    def export_data(self, table_name: str, start_time: datetime = None, end_time: datetime = None) -> str:
        """Export data to CSV file"""
        try:
            # Build query
            if start_time and end_time:
                query = f'''
                    SELECT * FROM {table_name} 
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp
                '''
                params = (start_time.isoformat(), end_time.isoformat())
            else:
                query = f'SELECT * FROM {table_name} ORDER BY timestamp'
                params = ()
            
            # Get data
            data = self.execute_query(query, params)
            
            if not data:
                return ""
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Export to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{table_name}_export_{timestamp}.csv"
            df.to_csv(filename, index=False)
            
            logger.info(f"Data exported to {filename} - {len(data)} records")
            return filename
            
        except Exception as e:
            logger.error(f"Data export failed: {e}")
            return ""
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {}
            
            # Get table info
            tables = [
                'system_metrics', 'market_data', 'arbitrage_opportunities',
                'trade_executions', 'quantum_results', 'risk_assessments',
                'performance_analytics'
            ]
            
            for table in tables:
                query = f'SELECT COUNT(*) as count FROM {table}'
                result = self.execute_query(query)
                stats[table] = result[0]['count'] if result else 0
            
            # Get database size
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size = page_count * page_size
            conn.close()
            
            stats['database_size_mb'] = db_size / (1024 * 1024)
            stats['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

# Global database manager instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get global database manager instance"""
    return db_manager