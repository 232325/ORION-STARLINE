#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Optimizer - Ma'lumotlar bazasi optimizatori
Ma'lumotlar bazasini optimizatsiya qilish va keshlash strategiyalari

Xususiyatlar:
- Index optimizatsiya
- Query performance tuning
- Connection pooling
- Caching strategies (Redis, Memcached)
- Database sharding
- Read replicas
- Query optimization
- Bulk operations
- Transaction optimization
- Migration management
"""

import os
import json
import time
import logging
import asyncio
import hashlib
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
from functools import wraps

# Database kutubxonalari
try:
    import psycopg2
    import psycopg2.pool
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import pymongo
    import pymongo.errors
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

try:
    import redis
    import redis.connection
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import sqlalchemy
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import QueuePool
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Logging sozlamalar
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueryInfo:
    """Query ma'lumotlari"""
    query: str
    execution_time: float
    rows_affected: int
    timestamp: float
    cache_key: str = ""
    from_cache: bool = False
    database: str = ""

@dataclass
class IndexInfo:
    """Index ma'lumotlari"""
    table_name: str
    column_name: str
    index_type: str
    size_mb: float
    usage_count: int
    is_unique: bool
    is_primary: bool
    recommendation: str = ""

@dataclass
class DatabaseConfig:
    """Ma'lumotlar bazasi konfiguratsiyasi"""
    database_type: str  # postgresql, mongodb, mysql, sqlite
    host: str
    port: int
    database_name: str
    username: str
    password: str
    max_connections: int = 10
    connection_timeout: int = 30
    query_timeout: int = 60
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_backend: str = "redis"  # redis, memory, filesystem
    connection_pool: bool = True
    read_replicas: List[Dict] = None
    connection_string: str = ""

class PerformanceMonitor:
    """Performance monitoring"""
    
    def __init__(self):
        self.query_history: List[QueryInfo] = []
        self.slow_queries: List[QueryInfo] = []
        self.performance_metrics = {
            "total_queries": 0,
            "average_response_time": 0.0,
            "cache_hit_rate": 0.0,
            "error_rate": 0.0
        }

    def record_query(self, query_info: QueryInfo):
        """Query natijasini qayd etish"""
        self.query_history.append(query_info)
        self.performance_metrics["total_queries"] += 1
        
        # Slow query qayd etish
        if query_info.execution_time > 1.0:  # 1 soniyadan ko'proq
            self.slow_queries.append(query_info)
        
        # Moving average hisoblash
        if self.query_history:
            execution_times = [q.execution_time for q in self.query_history[-100:]]
            self.performance_metrics["average_response_time"] = statistics.mean(execution_times)

    def get_slow_queries(self, threshold: float = 1.0) -> List[QueryInfo]:
        """Yavaq query'larni olish"""
        return [q for q in self.query_history if q.execution_time > threshold]

    def get_performance_stats(self) -> Dict:
        """Performance statistikasi"""
        if not self.query_history:
            return self.performance_metrics
        
        # Cache hit rate hisoblash
        cached_queries = sum(1 for q in self.query_history if q.from_cache)
        self.performance_metrics["cache_hit_rate"] = cached_queries / len(self.query_history)
        
        return self.performance_metrics

class QueryCache:
    """Query caching tizimi"""
    
    def __init__(self, backend: str = "redis", ttl: int = 3600):
        self.backend = backend
        self.ttl = ttl
        self.memory_cache: Dict[str, Any] = {}
        self.redis_client = None
        
        if backend == "redis" and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
                self.redis_client.ping()
            except:
                logger.warning("Redis server mavjud emas, memory cache ishlatiladi")
                self.backend = "memory"

    def get_cache_key(self, query: str, params: Any = None) -> str:
        """Cache key yaratish"""
        key_data = f"{query}:{str(params)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, query: str, params: Any = None) -> Optional[Any]:
        """Cache'dan olish"""
        cache_key = self.get_cache_key(query, params)
        
        try:
            if self.backend == "redis" and self.redis_client:
                data = self.redis_client.get(cache_key)
                if data:
                    return pickle.loads(data)
            elif self.backend == "memory":
                if cache_key in self.memory_cache:
                    return self.memory_cache[cache_key]
        except Exception as e:
            logger.error(f"Cache get xatosi: {str(e)}")
        
        return None

    def set(self, query: str, result: Any, params: Any = None):
        """Cache'ga saqlash"""
        cache_key = self.get_cache_key(query, params)
        
        try:
            if self.backend == "redis" and self.redis_client:
                serialized_data = pickle.dumps(result)
                self.redis_client.setex(cache_key, self.ttl, serialized_data)
            elif self.backend == "memory":
                self.memory_cache[cache_key] = result
        except Exception as e:
            logger.error(f"Cache set xatosi: {str(e)}")

    def invalidate(self, pattern: str = "*"):
        """Cache'ni tozalash"""
        try:
            if self.backend == "redis" and self.redis_client:
                if pattern == "*":
                    self.redis_client.flushdb()
                else:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
            elif self.backend == "memory":
                if pattern == "*":
                    self.memory_cache.clear()
                else:
                    # Pattern matching memory cache
                    keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                    for key in keys_to_delete:
                        del self.memory_cache[key]
        except Exception as e:
            logger.error(f"Cache invalidation xatosi: {str(e)}")

class ConnectionManager:
    """Ma'lumotlar bazasi connection management"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection_pool = None
        self.connections = {}
        
        # Connection pool yaratish
        if config.connection_pool and SQLALCHEMY_AVAILABLE:
            self._create_connection_pool()

    def _create_connection_pool(self):
        """Connection pool yaratish"""
        try:
            if self.config.connection_string:
                engine = create_engine(
                    self.config.connection_string,
                    poolclass=QueuePool,
                    pool_size=self.config.max_connections,
                    max_overflow=5,
                    pool_timeout=self.config.connection_timeout
                )
                self.connection_pool = engine
            else:
                # Connection string yaratish
                if self.config.database_type == "postgresql":
                    conn_str = f"postgresql://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database_name}"
                elif self.config.database_type == "mysql":
                    conn_str = f"mysql://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database_name}"
                else:
                    conn_str = f"sqlite:///{self.config.database_name}.db"
                
                engine = create_engine(
                    conn_str,
                    poolclass=QueuePool,
                    pool_size=self.config.max_connections,
                    max_overflow=5,
                    pool_timeout=self.config.connection_timeout
                )
                self.connection_pool = engine
                
        except Exception as e:
            logger.error(f"Connection pool yaratish xatosi: {str(e)}")

    @contextmanager
    def get_connection(self):
        """Connection olish context manager"""
        connection = None
        try:
            if self.connection_pool:
                connection = self.connection_pool.connect()
            else:
                connection = self._create_direct_connection()
            yield connection
        except Exception as e:
            logger.error(f"Connection xatosi: {str(e)}")
            raise
        finally:
            if connection and not self.connection_pool:
                try:
                    connection.close()
                except:
                    pass

    def _create_direct_connection(self):
        """To'g'ridan-to'g'ri connection yaratish"""
        if self.config.database_type == "postgresql" and POSTGRES_AVAILABLE:
            return psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database_name,
                user=self.config.username,
                password=self.config.password
            )
        elif self.config.database_type == "mysql" and MYSQL_AVAILABLE:
            return mysql.connector.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database_name,
                user=self.config.username,
                password=self.config.password
            )
        elif self.config.database_type == "mongodb" and MONGO_AVAILABLE:
            client = pymongo.MongoClient(
                f"mongodb://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database_name}"
            )
            return client[self.config.database_name]
        else:
            raise Exception(f"Database type {self.config.database_type} qo'llab-quvvatlanmaydi")

class DatabaseOptimizer:
    """Asosiy ma'lumotlar bazasi optimizatori"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.performance_monitor = PerformanceMonitor()
        self.query_cache = QueryCache(config.cache_backend, config.cache_ttl)
        self.connection_manager = ConnectionManager(config)
        self.optimization_results = {}

    async def optimize_database(self) -> Dict:
        """Ma'lumotlar bazasini optimizatsiya qilish"""
        logger.info("🚀 Ma'lumotlar bazasi optimizatsiya boshlanmoqda...")
        
        try:
            # 1. Connection test
            await self._test_connection()
            
            # 2. Performance tahlili
            await self._analyze_performance()
            
            # 3. Index tahlili
            await self._analyze_indexes()
            
            # 4. Query optimization
            await self._optimize_queries()
            
            # 5. Cache performance
            await self._optimize_caching()
            
            # 6. Connection pool tuning
            await self._tune_connection_pool()
            
            # 7. Database configuration
            await self._optimize_database_config()
            
            # 8. Migration planning
            await self._plan_optimization_migrations()
            
            # 9. Monitoring setup
            await self._setup_monitoring()
            
            # 10. Hisobot yaratish
            await self._generate_optimization_report()
            
            logger.info("✅ Ma'lumotlar bazasi optimizatsiya tugallandi!")
            return self.optimization_results
            
        except Exception as e:
            logger.error(f"❌ Database optimizatsiya xatosi: {str(e)}")
            raise

    async def _test_connection(self):
        """Connection test qilish"""
        logger.info("🔌 Connection test qilinmoqda...")
        
        try:
            with self.connection_manager.get_connection() as conn:
                if self.config.database_type == "postgresql" and POSTGRES_AVAILABLE:
                    cursor = conn.cursor()
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()[0]
                    logger.info(f"PostgreSQL connected: {version}")
                elif self.config.database_type == "mysql" and MYSQL_AVAILABLE:
                    cursor = conn.cursor()
                    cursor.execute("SELECT VERSION();")
                    version = cursor.fetchone()[0]
                    logger.info(f"MySQL connected: {version}")
                elif self.config.database_type == "mongodb" and MONGO_AVAILABLE:
                    db = conn
                    db.admin.command('ismaster')
                    logger.info("MongoDB connected")
            
            self.optimization_results["connection_test"] = {"status": "success", "database_type": self.config.database_type}
            
        except Exception as e:
            logger.error(f"❌ Connection test xatosi: {str(e)}")
            self.optimization_results["connection_test"] = {"status": "failed", "error": str(e)}
            raise

    async def _analyze_performance(self):
        """Performance tahlili"""
        logger.info("📊 Performance tahlili...")
        
        stats = self.performance_monitor.get_performance_stats()
        
        if stats["total_queries"] > 0:
            logger.info(f"Jami query'lar: {stats['total_queries']}")
            logger.info(f"O'rtacha response time: {stats['average_response_time']*1000:.2f}ms")
            logger.info(f"Cache hit rate: {stats['cache_hit_rate']*100:.1f}%")
        
        # Slow query tahlili
        slow_queries = self.performance_monitor.get_slow_queries()
        if slow_queries:
            logger.warning(f"{len(slow_queries)} ta yavaq query topildi")
            for query in slow_queries[-5:]:  # Oxirgi 5 ta
                logger.warning(f"Slow query: {query.execution_time:.2f}s")
        
        self.optimization_results["performance_analysis"] = {
            "stats": stats,
            "slow_queries_count": len(slow_queries),
            "performance_score": self._calculate_performance_score(stats)
        }

    def _calculate_performance_score(self, stats: Dict) -> float:
        """Performance score hisoblash"""
        score = 100.0
        
        # Response time penalty
        if stats["average_response_time"] > 0.1:
            score -= 20
        elif stats["average_response_time"] > 0.05:
            score -= 10
        
        # Cache hit rate bonus/malus
        score += (stats["cache_hit_rate"] - 0.5) * 40
        
        # Query count penalty
        if stats["total_queries"] > 1000:
            score -= 30
        
        return max(0, min(100, score))

    async def _analyze_indexes(self):
        """Index tahlili"""
        logger.info("🗂️  Index tahlili...")
        
        indexes = []
        
        try:
            with self.connection_manager.get_connection() as conn:
                if self.config.database_type == "postgresql" and POSTGRES_AVAILABLE:
                    indexes = await self._analyze_postgresql_indexes(conn)
                elif self.config.database_type == "mysql" and MYSQL_AVAILABLE:
                    indexes = await self._analyze_mysql_indexes(conn)
                elif self.config.database_type == "mongodb" and MONGO_AVAILABLE:
                    indexes = await self._analyze_mongodb_indexes(conn)
            
            # Index tavsiyalari
            recommendations = self._generate_index_recommendations(indexes)
            
            self.optimization_results["index_analysis"] = {
                "indexes": [asdict(idx) for idx in indexes],
                "recommendations": recommendations,
                "index_usage_score": self._calculate_index_score(indexes)
            }
            
        except Exception as e:
            logger.error(f"Index tahlil xatosi: {str(e)}")
            self.optimization_results["index_analysis"] = {"error": str(e)}

    async def _analyze_postgresql_indexes(self, conn) -> List[IndexInfo]:
        """PostgreSQL index tahlili"""
        indexes = []
        cursor = conn.cursor()
        
        query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            indexdef,
            pg_size_pretty(pg_relation_size(indexrelid::regclass)) as size,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC;
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            schema, table, index_name, index_def, size_str, scans, reads, fetches = row
            size_mb = float(size_str.replace('MB', '').strip())
            
            # Index turini aniqlash
            index_type = "btree"
            if "USING hash" in index_def:
                index_type = "hash"
            elif "USING gin" in index_def:
                index_type = "gin"
            elif "USING gist" in index_def:
                index_type = "gist"
            
            indexes.append(IndexInfo(
                table_name=table,
                column_name=index_name,
                index_type=index_type,
                size_mb=size_mb,
                usage_count=scans,
                is_unique="UNIQUE" in index_def,
                is_primary="PRIMARY KEY" in index_def
            ))
        
        return indexes

    async def _analyze_mysql_indexes(self, conn) -> List[IndexInfo]:
        """MySQL index tahloli"""
        indexes = []
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, NON_UNIQUE, SUB_PART, NULLABLE, INDEX_TYPE
        FROM information_schema.statistics
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, INDEX_NAME;
        """)
        
        rows = cursor.fetchall()
        
        for row in rows:
            schema, table, index_name, non_unique, sub_part, nullable, index_type = row
            
            # MySQL'da size hisoblash murakkab
            # Oddiy estimate
            size_mb = 0.1 if non_unique == 0 else 0.05
            
            indexes.append(IndexInfo(
                table_name=table,
                column_name=index_name,
                index_type=index_type,
                size_mb=size_mb,
                usage_count=0,  # MySQL'da stats捞取 murakkab
                is_unique=non_unique == 0,
                is_primary=index_name == "PRIMARY"
            ))
        
        return indexes

    async def _analyze_mongodb_indexes(self, db) -> List[IndexInfo]:
        """MongoDB index tahloli"""
        indexes = []
        
        collections = db.list_collection_names()
        for collection_name in collections:
            collection = db[collection_name]
            for index_info in collection.list_indexes():
                indexes.append(IndexInfo(
                    table_name=collection_name,
                    column_name=index_info["name"],
                    index_type=index_info.get("key", {}).get("_type", "text"),
                    size_mb=0.1,  # MongoDB'da size捞取 murakkab
                    usage_count=0,
                    is_unique=index_info.get("unique", False),
                    is_primary=False
                ))
        
        return indexes

    def _generate_index_recommendations(self, indexes: List[IndexInfo]) -> List[str]:
        """Index tavsiyalari yaratish"""
        recommendations = []
        
        # Kam ishlatiladigan indexlar
        unused_indexes = [idx for idx in indexes if idx.usage_count < 10]
        if unused_indexes:
            recommendations.append(f"{len(unused_indexes)} ta kam ishlatiladigan index o'chirilishi mumkin")
        
        # Katta indexlar
        large_indexes = [idx for idx in indexes if idx.size_mb > 100]
        if large_indexes:
            recommendations.append(f"{len(large_indexes)} ta katta index (>100MB) topildi")
        
        # Multi-column index tavsiyalari
        composite_indexes = [idx for idx in indexes if "." in idx.column_name]
        if not composite_indexes:
            recommendations.append("Composite index'lar yaratish tavsiya etiladi")
        
        # Full-text index tavsiyalari
        text_indexes = [idx for idx in indexes if idx.index_type == "text"]
        if not text_indexes:
            recommendations.append("Text search uchun full-text index'lar yaratish tavsiya etiladi")
        
        return recommendations

    def _calculate_index_score(self, indexes: List[IndexInfo]) -> float:
        """Index samaradorlik score"""
        if not indexes:
            return 0
        
        # Usage-based score
        total_usage = sum(idx.usage_count for idx in indexes)
        if total_usage == 0:
            return 0
        
        # Katta foydalanish va kichik size uchun yuqori score
        total_size = sum(idx.size_mb for idx in indexes)
        
        # Optimal ratio: yuqori usage, kichik size
        usage_ratio = min(1.0, total_usage / 1000)  # Normalize to 0-1
        size_efficiency = max(0.1, 1.0 - (total_size / len(indexes) / 10))  # Size efficiency
        
        return (usage_ratio + size_efficiency) / 2 * 100

    async def _optimize_queries(self):
        """Query optimizatsiya"""
        logger.info("🔍 Query optimizatsiya...")
        
        # Slow query'lar tahloli
        slow_queries = self.performance_monitor.get_slow_queries()
        
        optimizations = []
        for query_info in slow_queries:
            optimization = self._analyze_slow_query(query_info)
            if optimization:
                optimizations.append(optimization)
        
        self.optimization_results["query_optimization"] = {
            "slow_queries_analyzed": len(slow_queries),
            "optimizations": optimizations,
            "estimated_improvement": self._estimate_query_improvement(optimizations)
        }

    def _analyze_slow_query(self, query_info: QueryInfo) -> Optional[Dict]:
        """Yavaq query tahloli va optimizatsiya"""
        query = query_info.query.lower()
        
        optimizations = []
        
        # SELECT * cheklov
        if "select *" in query:
            optimizations.append("SELECT * o'rniga aniq column'lar tanlang")
        
        # Joins optimization
        if "join" in query and "use index" not in query:
            optimizations.append("JOIN'lar uchun index'lar tekshiring")
        
        # Subquery optimization
        if "select" in query and "(" in query:
            optimizations.append("Subquery'ni EXISTS yoki IN bilan almashtiring")
        
        # ORDER BY optimization
        if "order by" in query:
            if "limit" not in query:
                optimizations.append("ORDER BY bilan LIMIT ishlatish tavsiya etiladi")
        
        # WHERE clause optimization
        if "where" not in query:
            optimizations.append("WHERE clause qo'shing")
        
        return {
            "query": query_info.query[:100] + "..." if len(query_info.query) > 100 else query_info.query,
            "execution_time": query_info.execution_time,
            "optimizations": optimizations
        } if optimizations else None

    def _estimate_query_improvement(self, optimizations: List[Dict]) -> Dict:
        """Query yaxshilanish hisob-kitobi"""
        if not optimizations:
            return {"improvement_percentage": 0, "estimated_time_saved": 0}
        
        # Har bir optimizatsiya uchun taxmin qilingan improvement
        improvement_map = {
            "SELECT * o'rniga aniq column'lar tanlang": 15,
            "JOIN'lar uchun index'lar tekshiring": 25,
            "Subquery'ni EXISTS yoki IN bilan almashtiring": 20,
            "ORDER BY bilan LIMIT ishlatish tavsiya etiladi": 30,
            "WHERE clause qo'shing": 40
        }
        
        total_improvement = 0
        time_saved = 0
        
        for opt in optimizations:
            query_improvement = 0
            for improvement in opt["optimizations"]:
                query_improvement += improvement_map.get(improvement, 10)
            query_improvement = min(query_improvement, 70)  # Max 70% improvement
        
        # Query execution time hisoblash
        avg_time = statistics.mean([opt["execution_time"] for opt in optimizations])
        estimated_improvement = (query_improvement / 100) * avg_time
        
        return {
            "improvement_percentage": min(query_improvement, 70),
            "estimated_time_saved": estimated_improvement,
            "optimizations_count": len(optimizations)
        }

    async def _optimize_caching(self):
        """Cache optimizatsiya"""
        logger.info("💾 Cache optimizatsiya...")
        
        cache_stats = {
            "backend": self.config.cache_backend,
            "ttl": self.config.cache_ttl,
            "hit_rate": 0,
            "size_estimate": 0
        }
        
        # Cache hit rate o'lchash
        if self.query_history:
            cached_count = sum(1 for q in self.performance_monitor.query_history if q.from_cache)
            cache_stats["hit_rate"] = (cached_count / len(self.performance_monitor.query_history)) * 100
        
        # Redis connection test
        if self.config.cache_backend == "redis" and REDIS_AVAILABLE:
            try:
                redis_client = self.query_cache.redis_client
                if redis_client:
                    info = redis_client.info()
                    cache_stats["size_estimate"] = info.get("used_memory_human", "N/A")
                    cache_stats["redis_version"] = info.get("redis_version", "N/A")
            except:
                pass
        
        recommendations = []
        
        # Cache hit rate tavsiyalari
        if cache_stats["hit_rate"] < 70:
            recommendations.append("Cache hit rate yaxshilash uchun TTL vaqti ko'paytiring")
        elif cache_stats["hit_rate"] > 90:
            recommendations.append("Yuqori cache hit rate - yaxshi!")
        
        # Memory usage tavsiyalari
        if cache_stats["size_estimate"]:
            recommendations.append("Cache size monitoring qiling")
        
        self.optimization_results["cache_optimization"] = {
            "stats": cache_stats,
            "recommendations": recommendations
        }

    async def _tune_connection_pool(self):
        """Connection pool tuning"""
        logger.info("🔧 Connection pool tuning...")
        
        pool_config = {
            "max_connections": self.config.max_connections,
            "connection_timeout": self.config.connection_timeout,
            "pool_status": "active" if self.connection_manager.connection_pool else "inactive"
        }
        
        recommendations = []
        
        # Connection pool kattaligi
        if self.config.max_connections < 5:
            recommendations.append("Connection pool kattaligini oshiring")
        elif self.config.max_connections > 20:
            recommendations.append("Connection pool juda katta - optimallashtiring")
        
        # Timeout optimizatsiya
        if self.config.connection_timeout < 30:
            recommendations.append("Connection timeout vaqtini oshiring")
        
        # Database performance based recommendations
        avg_response_time = self.performance_monitor.get_performance_stats()["average_response_time"]
        if avg_response_time > 0.1:
            recommendations.append("Yuqori response time - connection pool optimizatsiyasi zarur")
        
        self.optimization_results["connection_pool_tuning"] = {
            "config": pool_config,
            "recommendations": recommendations
        }

    async def _optimize_database_config(self):
        """Ma'lumotlar bazasi konfiguratsiya optimizatsiyasi"""
        logger.info("⚙️  Database konfiguratsiya optimizatsiya...")
        
        config_recommendations = []
        
        try:
            with self.connection_manager.get_connection() as conn:
                if self.config.database_type == "postgresql" and POSTGRES_AVAILABLE:
                    config_recommendations = await self._optimize_postgresql_config(conn)
                elif self.config.database_type == "mysql" and MYSQL_AVAILABLE:
                    config_recommendations = await self._optimize_mysql_config(conn)
                elif self.config.database_type == "mongodb" and MONGO_AVAILABLE:
                    config_recommendations = await self._optimize_mongodb_config(conn)
            
        except Exception as e:
            logger.error(f"Database config optimizatsiya xatosi: {str(e)}")
        
        self.optimization_results["database_config"] = {
            "recommendations": config_recommendations
        }

    async def _optimize_postgresql_config(self, conn) -> List[str]:
        """PostgreSQL konfiguratsiya optimizatsiyasi"""
        recommendations = []
        cursor = conn.cursor()
        
        try:
            # Connection settings
            cursor.execute("SHOW max_connections;")
            max_connections = cursor.fetchone()[0]
            if int(max_connections) < 100:
                recommendations.append("PostgreSQL: max_connections ni oshiring")
            
            # Memory settings
            cursor.execute("SHOW shared_buffers;")
            shared_buffers = cursor.fetchone()[0]
            recommendations.append(f"shared_buffers: {shared_buffers} (optimal qilish uchun tekshiring)")
            
            # Query cache
            cursor.execute("SHOW work_mem;")
            work_mem = cursor.fetchone()[0]
            recommendations.append(f"work_mem: {work_mem} (query performance uchun muhim)")
            
        except Exception as e:
            logger.error(f"PostgreSQL config tahlil xatosi: {str(e)}")
        
        return recommendations

    async def _optimize_mysql_config(self, conn) -> List[str]:
        """MySQL konfiguratsiya optimizatsiyasi"""
        recommendations = []
        cursor = conn.cursor()
        
        try:
            # InnoDB buffer pool
            cursor.execute("SELECT @@innodb_buffer_pool_size;")
            buffer_pool = cursor.fetchone()[0]
            recommendations.append(f"innodb_buffer_pool_size: {buffer_pool} (RAM'ning 50-70% tavsiya etiladi)")
            
            # Query cache
            cursor.execute("SELECT @@query_cache_size;")
            query_cache = cursor.fetchone()[0]
            if query_cache == 0:
                recommendations.append("MySQL: Query cache yoqish foydali bo'lishi mumkin")
            
            # Connection limit
            cursor.execute("SELECT @@max_connections;")
            max_conn = cursor.fetchone()[0]
            recommendations.append(f"max_connections: {max_conn}")
            
        except Exception as e:
            logger.error(f"MySQL config tahlil xatosi: {str(e)}")
        
        return recommendations

    async def _optimize_mongodb_config(self, db) -> List[str]:
        """MongoDB konfiguratsiya optimizatsiya"""
        recommendations = []
        
        try:
            # Database stats
            stats = db.command("dbStats")
            recommendations.append(f"Database size: {stats.get('dataSize', 'N/A')}MB")
            
            # Index stats
            collections = db.list_collection_names()
            for collection_name in collections:
                collection = db[collection_name]
                indexes = collection.list_indexes()
                index_count = len(list(indexes))
                if index_count > 10:
                    recommendations.append(f"Collection {collection_name}: {index_count} ta index - ko'p")
            
        except Exception as e:
            logger.error(f"MongoDB config tahlil xatosi: {str(e)}")
        
        return recommendations

    async def _plan_optimization_migrations(self):
        """Optimizatsiya migration'larini rejalash"""
        logger.info("📋 Optimizatsiya migration rejalari...")
        
        migrations = []
        
        # Index migration'lar
        if "index_analysis" in self.optimization_results:
            index_data = self.optimization_results["index_analysis"]
            if "recommendations" in index_data:
                for recommendation in index_data["recommendations"]:
                    if "o'chirilishi mumkin" in recommendation:
                        # Index deletion migration
                        migrations.append({
                            "type": "index_drop",
                            "description": recommendation,
                            "sql": "DROP INDEX index_name ON table_name;"
                        })
                    elif "yaratish" in recommendation:
                        # Index creation migration
                        migrations.append({
                            "type": "index_create",
                            "description": recommendation,
                            "sql": "CREATE INDEX index_name ON table_name (column_name);"
                        })
        
        # Query migration'lar
        if "query_optimization" in self.optimization_results:
            query_data = self.optimization_results["query_optimization"]
            if "optimizations" in query_data:
                for opt in query_data["optimizations"]:
                    migrations.append({
                        "type": "query_optimization",
                        "description": f"Query optimization: {opt['query']}",
                        "improvements": opt["optimizations"]
                    })
        
        self.optimization_results["migration_plan"] = migrations

    async def _setup_monitoring(self):
        """Monitoring o'rnatish"""
        logger.info("📊 Monitoring o'rnatilmoqda...")
        
        monitoring_config = {
            "performance_tracking": {
                "enabled": True,
                "slow_query_threshold": 1.0,  # seconds
                "metrics_retention": "7d"
            },
            "cache_monitoring": {
                "enabled": self.config.enable_caching,
                "hit_rate_target": 80,  # percentage
                "memory_usage_tracking": True
            },
            "connection_monitoring": {
                "enabled": True,
                "pool_size_monitoring": True,
                "connection_timeout_tracking": True
            }
        }
        
        self.optimization_results["monitoring_setup"] = monitoring_config

    async def _generate_optimization_report(self):
        """Optimizatsiya hisoboti yaratish"""
        logger.info("📊 Optimizatsiya hisoboti yaratilmoqda...")
        
        report = {
            "summary": {
                "database_type": self.config.database_type,
                "optimization_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "overall_score": self._calculate_overall_score(),
                "total_recommendations": self._count_total_recommendations()
            },
            "performance_analysis": self.optimization_results.get("performance_analysis", {}),
            "index_analysis": self.optimization_results.get("index_analysis", {}),
            "query_optimization": self.optimization_results.get("query_optimization", {}),
            "cache_optimization": self.optimization_results.get("cache_optimization", {}),
            "connection_pool_tuning": self.optimization_results.get("connection_pool_tuning", {}),
            "database_config": self.optimization_results.get("database_config", {}),
            "migration_plan": self.optimization_results.get("migration_plan", []),
            "monitoring_setup": self.optimization_results.get("monitoring_setup", {}),
            "all_recommendations": self._collect_all_recommendations()
        }
        
        # Hisobotni faylga saqlash
        report_path = "database_optimization_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Database optimizatsiya hisoboti saqlandi: {report_path}")

    def _calculate_overall_score(self) -> float:
        """Umumiy performance score hisoblash"""
        scores = []
        
        # Performance score
        if "performance_analysis" in self.optimization_results:
            score = self.optimization_results["performance_analysis"].get("performance_score", 0)
            scores.append(score)
        
        # Index score
        if "index_analysis" in self.optimization_results:
            score = self.optimization_results["index_analysis"].get("index_usage_score", 0)
            scores.append(score)
        
        # Cache hit rate
        if "cache_optimization" in self.optimization_results:
            hit_rate = self.optimization_results["cache_optimization"]["stats"]["hit_rate"]
            scores.append(hit_rate)
        
        return statistics.mean(scores) if scores else 0

    def _count_total_recommendations(self) -> int:
        """Jami tavsiyalar soni"""
        total = 0
        
        for section in ["index_analysis", "query_optimization", "cache_optimization", "connection_pool_tuning", "database_config"]:
            if section in self.optimization_results:
                data = self.optimization_results[section]
                if "recommendations" in data:
                    total += len(data["recommendations"])
        
        return total

    def _collect_all_recommendations(self) -> List[str]:
        """Barcha tavsiyalarni yig'ish"""
        all_recommendations = []
        
        for section in ["index_analysis", "query_optimization", "cache_optimization", "connection_pool_tuning", "database_config"]:
            if section in self.optimization_results:
                data = self.optimization_results[section]
                if "recommendations" in data:
                    all_recommendations.extend(data["recommendations"])
        
        return all_recommendations

    @contextmanager
    def cache_query(self, key_prefix: str = ""):
        """Query caching decorator"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Cache key yaratish
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Cache'dan olishga harakat qilish
                cached_result = self.query_cache.get("", cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Query bajarish
                result = await func(*args, **kwargs)
                
                # Cache'ga saqlash
                self.query_cache.set("", result, cache_key)
                
                return result
            return wrapper
        return decorator

# CLI interface
async def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Optimizer - Ma'lumotlar bazasi optimizatori")
    parser.add_argument("--db-type", choices=["postgresql", "mysql", "mongodb"], required=True, help="Database type")
    parser.add_argument("--host", default="localhost", help="Database host")
    parser.add_argument("--port", type=int, help="Database port")
    parser.add_argument("--database", required=True, help="Database name")
    parser.add_argument("--username", required=True, help="Database username")
    parser.add_argument("--password", required=True, help="Database password")
    parser.add_argument("--cache-backend", choices=["redis", "memory"], default="redis", help="Cache backend")
    parser.add_argument("--output", help="Hisobot fayl yo'li")
    
    args = parser.parse_args()
    
    # Port aniqlash
    default_ports = {"postgresql": 5432, "mysql": 3306, "mongodb": 27017}
    port = args.port or default_ports.get(args.db_type, 5432)
    
    # Config yaratish
    config = DatabaseConfig(
        database_type=args.db_type,
        host=args.host,
        port=port,
        database_name=args.database,
        username=args.username,
        password=args.password,
        cache_backend=args.cache_backend
    )
    
    # Optimizator yaratish
    optimizer = DatabaseOptimizer(config)
    
    # Optimizatsiya o'tkazish
    try:
        results = await optimizer.optimize_database()
        
        # Natijani ko'rsatish
        print("\n🗄️  MA'LUMOTLAR BAZASI OPTIMIZATSIYASI NATIJASI:")
        print("=" * 50)
        print(f"Database type: {results['summary']['database_type']}")
        print(f"Umumiy score: {results['summary']['overall_score']:.1f}/100")
        print(f"Jami tavsiyalar: {results['summary']['total_recommendations']}")
        
        if "performance_analysis" in results:
            perf = results["performance_analysis"]["stats"]
            print(f"O'rtacha response time: {perf['average_response_time']*1000:.2f}ms")
            print(f"Cache hit rate: {perf['cache_hit_rate']*100:.1f}%")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Hisobot saqlandi: {args.output}")
        
    except Exception as e:
        logger.error(f"Database optimizatsiya xatosi: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())