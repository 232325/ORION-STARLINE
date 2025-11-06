"""
Risk Data Manager
================

Centralized data management for risk management system.
Handles data collection, storage, validation, and access for all risk components.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
import sqlite3
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class MarketDataPoint:
    """Market data point structure"""
    symbol: str
    timestamp: datetime
    price: float
    volume: float
    bid: float = 0.0
    ask: float = 0.0
    spread: float = 0.0
    volatility: float = 0.0
    data_source: str = "unknown"

@dataclass
class RiskDataConfig:
    """Configuration for risk data management"""
    database_path: str = "risk_data.db"
    data_retention_days: int = 365
    real_time_buffer_size: int = 1000
    data_validation_enabled: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24

class RiskDataManager:
    """
    Centralized data management for risk system
    
    Responsibilities:
    - Market data collection and storage
    - Position data management
    - Risk metrics storage
    - Data validation and cleaning
    - Historical data access
    - Data export and reporting
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_config = RiskDataConfig(**config)
        
        # Database connection
        self.db_connection = None
        self.real_time_buffer = {}
        
        # Data storage
        self.market_data_cache = {}
        self.position_data_cache = {}
        self.risk_metrics_cache = {}
        
        # Data statistics
        self.data_stats = {
            'market_data_points': 0,
            'position_updates': 0,
            'risk_calculations': 0,
            'last_update': None
        }
        
        logger.info("Risk Data Manager initialized")
    
    async def initialize(self):
        """Initialize data manager and database connections"""
        try:
            logger.info("Initializing Risk Data Manager...")
            
            # Initialize database
            await self._initialize_database()
            
            # Setup data validation
            if self.data_config.data_validation_enabled:
                await self._setup_data_validation()
            
            # Start background tasks
            asyncio.create_task(self._data_cleanup_loop())
            asyncio.create_task(self._backup_loop())
            
            logger.info("Risk Data Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Risk Data Manager: {e}")
            raise
    
    async def _initialize_database(self):
        """Initialize SQLite database for data storage"""
        try:
            self.db_connection = sqlite3.connect(self.data_config.database_path, check_same_thread=False)
            
            # Create tables
            await self._create_tables()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _create_tables(self):
        """Create database tables"""
        cursor = self.db_connection.cursor()
        
        # Market data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL DEFAULT 0,
                bid REAL DEFAULT 0,
                ask REAL DEFAULT 0,
                spread REAL DEFAULT 0,
                volatility REAL DEFAULT 0,
                data_source TEXT DEFAULT 'unknown',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Position data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                quantity REAL NOT NULL,
                avg_cost REAL NOT NULL,
                current_price REAL NOT NULL,
                market_value REAL NOT NULL,
                unrealized_pnl REAL DEFAULT 0,
                realized_pnl REAL DEFAULT 0,
                asset_class TEXT DEFAULT 'unknown',
                position_limit REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Risk metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                portfolio_value REAL NOT NULL,
                var_1d_95 REAL DEFAULT 0,
                var_1d_99 REAL DEFAULT 0,
                expected_shortfall REAL DEFAULT 0,
                portfolio_volatility REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                correlation_risk REAL DEFAULT 0,
                liquidity_risk REAL DEFAULT 0,
                stress_test_results TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Compliance violations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                current_value REAL NOT NULL,
                threshold_value REAL NOT NULL,
                description TEXT,
                resolved INTEGER DEFAULT 0,
                resolved_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Risk alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                acknowledged INTEGER DEFAULT 0,
                acknowledged_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.db_connection.commit()
        logger.info("Database tables created successfully")
    
    async def _setup_data_validation(self):
        """Setup data validation rules"""
        # This would setup data validation rules
        # For now, just log that validation is enabled
        logger.info("Data validation enabled")
    
    # Market Data Management
    
    async def store_market_data(self, data_point: MarketDataPoint):
        """Store market data point"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO market_data 
                (symbol, timestamp, price, volume, bid, ask, spread, volatility, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data_point.symbol,
                data_point.timestamp.isoformat(),
                data_point.price,
                data_point.volume,
                data_point.bid,
                data_point.ask,
                data_point.spread,
                data_point.volatility,
                data_point.data_source
            ))
            
            self.db_connection.commit()
            
            # Update cache
            if data_point.symbol not in self.market_data_cache:
                self.market_data_cache[data_point.symbol] = []
            
            self.market_data_cache[data_point.symbol].append(data_point)
            
            # Limit cache size
            if len(self.market_data_cache[data_point.symbol]) > self.data_config.real_time_buffer_size:
                self.market_data_cache[data_point.symbol].pop(0)
            
            self.data_stats['market_data_points'] += 1
            self.data_stats['last_update'] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error storing market data: {e}")
    
    async def get_current_market_data(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Get current market data for specified symbols"""
        try:
            cursor = self.db_connection.cursor()
            
            if symbols:
                placeholders = ','.join(['?' for _ in symbols])
                query = f'''
                    SELECT symbol, price, volume, bid, ask, spread, volatility, timestamp
                    FROM market_data 
                    WHERE symbol IN ({placeholders})
                    ORDER BY timestamp DESC
                '''
                cursor.execute(query, symbols)
            else:
                query = '''
                    SELECT symbol, price, volume, bid, ask, spread, volatility, timestamp
                    FROM market_data 
                    ORDER BY timestamp DESC
                '''
                cursor.execute(query)
            
            rows = cursor.fetchall()
            
            market_data = {}
            for row in rows:
                symbol = row[0]
                if symbol not in market_data:  # Take the most recent
                    market_data[symbol] = {
                        'current_price': row[1],
                        'volume': row[2],
                        'bid': row[3],
                        'ask': row[4],
                        'spread': row[5],
                        'volatility': row[6],
                        'timestamp': row[7]
                    }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error retrieving market data: {e}")
            return {}
    
    async def get_market_history(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical market data for a symbol"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, price, volume, bid, ask, spread, volatility
                FROM market_data
                WHERE symbol = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            ''', (symbol, cutoff_date.isoformat()))
            
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    'timestamp': row[0],
                    'price': row[1],
                    'volume': row[2],
                    'bid': row[3],
                    'ask': row[4],
                    'spread': row[5],
                    'volatility': row[6]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error retrieving market history for {symbol}: {e}")
            return []
    
    # Position Data Management
    
    async def store_position_data(self, symbol: str, position_data: Dict[str, Any]):
        """Store position data"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO position_data
                (symbol, timestamp, quantity, avg_cost, current_price, market_value,
                 unrealized_pnl, realized_pnl, asset_class, position_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                position_data.get('timestamp', datetime.now()).isoformat(),
                position_data.get('quantity', 0),
                position_data.get('avg_cost', 0),
                position_data.get('current_price', 0),
                position_data.get('market_value', 0),
                position_data.get('unrealized_pnl', 0),
                position_data.get('realized_pnl', 0),
                position_data.get('asset_class', 'unknown'),
                position_data.get('position_limit', 0)
            ))
            
            self.db_connection.commit()
            
            # Update cache
            self.position_data_cache[symbol] = position_data
            self.data_stats['position_updates'] += 1
            
        except Exception as e:
            logger.error(f"Error storing position data for {symbol}: {e}")
    
    async def get_position_history(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical position data for a symbol"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, quantity, avg_cost, current_price, market_value,
                       unrealized_pnl, realized_pnl, asset_class
                FROM position_data
                WHERE symbol = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            ''', (symbol, cutoff_date.isoformat()))
            
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    'timestamp': row[0],
                    'quantity': row[1],
                    'avg_cost': row[2],
                    'current_price': row[3],
                    'market_value': row[4],
                    'unrealized_pnl': row[5],
                    'realized_pnl': row[6],
                    'asset_class': row[7]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error retrieving position history for {symbol}: {e}")
            return []
    
    # Risk Metrics Management
    
    async def store_risk_metrics(self, risk_metrics: Dict[str, Any]):
        """Store risk metrics"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO risk_metrics
                (timestamp, portfolio_value, var_1d_95, var_1d_99, expected_shortfall,
                 portfolio_volatility, max_drawdown, correlation_risk, liquidity_risk,
                 stress_test_results)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                risk_metrics.get('timestamp', datetime.now()).isoformat(),
                risk_metrics.get('portfolio_value', 0),
                risk_metrics.get('var_1d_95', 0),
                risk_metrics.get('var_1d_99', 0),
                risk_metrics.get('expected_shortfall', 0),
                risk_metrics.get('portfolio_volatility', 0),
                risk_metrics.get('max_drawdown', 0),
                risk_metrics.get('correlation_risk', 0),
                risk_metrics.get('liquidity_risk', 0),
                json.dumps(risk_metrics.get('stress_test_results', {}))
            ))
            
            self.db_connection.commit()
            
            # Update cache
            self.risk_metrics_cache['latest'] = risk_metrics
            self.data_stats['risk_calculations'] += 1
            
        except Exception as e:
            logger.error(f"Error storing risk metrics: {e}")
    
    async def get_risk_metrics_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical risk metrics"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor = self.db_connection.cursor()
            cursor.execute('''
                SELECT timestamp, portfolio_value, var_1d_95, var_1d_99, expected_shortfall,
                       portfolio_volatility, max_drawdown, correlation_risk, liquidity_risk,
                       stress_test_results
                FROM risk_metrics
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            ''', (cutoff_date.isoformat(),))
            
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    'timestamp': row[0],
                    'portfolio_value': row[1],
                    'var_1d_95': row[2],
                    'var_1d_99': row[3],
                    'expected_shortfall': row[4],
                    'portfolio_volatility': row[5],
                    'max_drawdown': row[6],
                    'correlation_risk': row[7],
                    'liquidity_risk': row[8],
                    'stress_test_results': json.loads(row[9]) if row[9] else {}
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error retrieving risk metrics history: {e}")
            return []
    
    # Data Validation
    
    async def validate_market_data(self, data_point: MarketDataPoint) -> bool:
        """Validate market data point"""
        try:
            if not self.data_config.data_validation_enabled:
                return True
            
            # Basic validation checks
            if data_point.price <= 0:
                logger.warning(f"Invalid price for {data_point.symbol}: {data_point.price}")
                return False
            
            if data_point.bid > data_point.ask:
                logger.warning(f"Invalid bid-ask spread for {data_point.symbol}: "
                             f"bid={data_point.bid}, ask={data_point.ask}")
                return False
            
            if data_point.volume < 0:
                logger.warning(f"Invalid volume for {data_point.symbol}: {data_point.volume}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating market data: {e}")
            return False
    
    async def validate_position_data(self, position_data: Dict[str, Any]) -> bool:
        """Validate position data"""
        try:
            if not self.data_config.data_validation_enabled:
                return True
            
            required_fields = ['quantity', 'avg_cost', 'current_price', 'market_value']
            
            for field in required_fields:
                if field not in position_data:
                    logger.warning(f"Missing required field in position data: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating position data: {e}")
            return False
    
    # Data Export
    
    async def export_market_data(self, symbols: List[str] = None, 
                               start_date: datetime = None,
                               end_date: datetime = None,
                               format_type: str = 'csv') -> str:
        """Export market data"""
        try:
            cursor = self.db_connection.cursor()
            
            # Build query
            query = "SELECT * FROM market_data WHERE 1=1"
            params = []
            
            if symbols:
                placeholders = ','.join(['?' for _ in symbols])
                query += f" AND symbol IN ({placeholders})"
                params.extend(symbols)
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to DataFrame
            columns = [description[0] for description in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            
            if format_type.lower() == 'csv':
                return df.to_csv(index=False)
            elif format_type.lower() == 'json':
                return df.to_json(orient='records', date_format='iso')
            else:
                return df.to_string()
            
        except Exception as e:
            logger.error(f"Error exporting market data: {e}")
            return ""
    
    async def export_risk_data_summary(self) -> Dict[str, Any]:
        """Export risk data summary"""
        try:
            cursor = self.db_connection.cursor()
            
            # Get counts
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_data_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM position_data")
            position_data_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM risk_metrics")
            risk_metrics_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM compliance_violations")
            violations_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM risk_alerts")
            alerts_count = cursor.fetchone()[0]
            
            # Get date ranges
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM market_data")
            market_date_range = cursor.fetchone()
            
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM risk_metrics")
            metrics_date_range = cursor.fetchone()
            
            return {
                'export_timestamp': datetime.now().isoformat(),
                'data_summary': {
                    'market_data_points': market_data_count,
                    'position_data_points': position_data_count,
                    'risk_metrics_records': risk_metrics_count,
                    'compliance_violations': violations_count,
                    'risk_alerts': alerts_count
                },
                'date_ranges': {
                    'market_data': {
                        'start': market_date_range[0],
                        'end': market_date_range[1]
                    },
                    'risk_metrics': {
                        'start': metrics_date_range[0],
                        'end': metrics_date_range[1]
                    }
                },
                'data_statistics': self.data_stats.copy()
            }
            
        except Exception as e:
            logger.error(f"Error exporting risk data summary: {e}")
            return {}
    
    # Background Tasks
    
    async def _data_cleanup_loop(self):
        """Background data cleanup task"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                cutoff_date = datetime.now() - timedelta(days=self.data_config.data_retention_days)
                
                cursor = self.db_connection.cursor()
                
                # Clean old market data
                cursor.execute("DELETE FROM market_data WHERE timestamp < ?", (cutoff_date.isoformat(),))
                
                # Clean old position data
                cursor.execute("DELETE FROM position_data WHERE timestamp < ?", (cutoff_date.isoformat(),))
                
                self.db_connection.commit()
                
                logger.info("Data cleanup completed")
                
            except Exception as e:
                logger.error(f"Error in data cleanup loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _backup_loop(self):
        """Background backup task"""
        if not self.data_config.backup_enabled:
            return
        
        while True:
            try:
                await asyncio.sleep(self.data_config.backup_interval_hours * 3600)  # Convert to seconds
                
                await self._create_backup()
                
            except Exception as e:
                logger.error(f"Error in backup loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def _create_backup(self):
        """Create database backup"""
        try:
            backup_path = f"risk_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            # Simple file copy backup (in production, would use proper backup tools)
            import shutil
            shutil.copy2(self.data_config.database_path, backup_path)
            
            logger.info(f"Database backup created: {backup_path}")
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
    
    # Utility Methods
    
    async def get_data_statistics(self) -> Dict[str, Any]:
        """Get data management statistics"""
        return {
            'database_path': self.data_config.database_path,
            'retention_days': self.data_config.data_retention_days,
            'data_stats': self.data_stats.copy(),
            'cache_sizes': {
                'market_data': len(self.market_data_cache),
                'position_data': len(self.position_data_cache),
                'risk_metrics': len(self.risk_metrics_cache)
            },
            'last_update': self.data_stats.get('last_update')
        }
    
    async def close(self):
        """Close data manager and cleanup resources"""
        try:
            if self.db_connection:
                self.db_connection.close()
            
            logger.info("Risk Data Manager closed")
            
        except Exception as e:
            logger.error(f"Error closing Risk Data Manager: {e}")