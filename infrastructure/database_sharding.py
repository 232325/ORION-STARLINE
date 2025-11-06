"""
Orion Starline Database Sharding
================================

Bu fayl ma'lumotlar bazasi sharding (bo'lish) va 
horizontal scaling uchun strategiyalarni o'z ichiga oladi.
"""

import asyncio
import hashlib
import json
import logging
import random
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncpg
import asyncpg.pool
from contextlib import asynccontextmanager


class ShardingStrategy(Enum):
    """Sharding strategiyalari"""
    HASH_BASED = "hash_based"
    RANGE_BASED = "range_based"
    GEOGRAPHIC = "geographic"
    TIME_BASED = "time_based"
    CONSISTENT_HASHING = "consistent_hashing"
    COMPOSITE = "composite"


class ConsistencyLevel(Enum):
    """Konsistentlik darajalari"""
    EVENTUAL = "eventual"
    STRONG = "strong"
    BOUNDED_STALENESS = "bounded_staleness"
    LOCAL_QUORUM = "local_quorum"


@dataclass
class ShardConfig:
    """Shard konfiguratsiyasi"""
    shard_id: str
    host: str
    port: int
    database: str
    username: str
    password: str
    max_connections: int = 20
    weight: int = 1
    region: str = "us-east"
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ShardMetadata:
    """Shard metadata"""
    shard_id: str
    strategy: ShardingStrategy
    total_shards: int
    replica_count: int
    consistency_level: ConsistencyLevel
    created_at: datetime = field(default_factory=datetime.now)
    last_rebalanced: Optional[datetime] = None


@dataclass
class ShardKey:
    """Sharding kalit"""
    value: Any
    shard_id: str
    partition: Optional[int] = None
    timestamp: Optional[datetime] = None


class ConsistentHashRing:
    """Consistent Hashing ring"""
    
    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        
    def _hash(self, key: str) -> int:
        """Kalitni hash qilish"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node_id: str, weight: int = 1):
        """Node qo'shish"""
        for i in range(self.virtual_nodes * weight):
            virtual_key = f"{node_id}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node_id
            
        self.sorted_keys = sorted(self.ring.keys())
    
    def remove_node(self, node_id: str, weight: int = 1):
        """Node olib tashlash"""
        for i in range(self.virtual_nodes * weight):
            virtual_key = f"{node_id}:{i}"
            hash_value = self._hash(virtual_key)
            if hash_value in self.ring:
                del self.ring[hash_value]
                
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_node(self, key: str) -> str:
        """Kalit uchun node olish"""
        if not self.ring:
            raise ValueError("No nodes in ring")
            
        hash_value = self._hash(key)
        
        # Birinchi katta yoki teng qiymatni topish
        for ring_hash in self.sorted_keys:
            if hash_value <= ring_hash:
                return self.ring[ring_hash]
        
        # Agar topilmasa, birinchi node ni qaytarish
        return self.ring[self.sorted_keys[0]]


class ShardManager:
    """Shard boshqaruvchisi"""
    
    def __init__(self):
        self.shards: Dict[str, ShardConfig] = {}
        self.shard_metadata: Optional[ShardMetadata] = None
        self.consistent_hash_ring = ConsistentHashRing()
        self.pools: Dict[str, asyncpg.pool.Pool] = {}
        self.logger = logging.getLogger(__name__)
        
        # Range-based sharding uchun
        self.range_mappings = {}
        
        # Time-based sharding uchun
        self.time_slices = {}
    
    def initialize_shards(self, metadata: ShardMetadata, shard_configs: List[ShardConfig]):
        """Shardlarni inicializatsiya qilish"""
        self.shard_metadata = metadata
        self.shards = {config.shard_id: config for config in shard_configs}
        
        # Consistent hash ring ni sozlashtirish
        for shard_config in shard_configs:
            self.consistent_hash_ring.add_node(shard_config.shard_id, shard_config.weight)
        
        self.logger.info(f"Initialized {len(shards)} shards with {metadata.strategy.value} strategy")
    
    def get_shard_id(self, key: Any) -> str:
        """Kalit uchun shard ID ni olish"""
        if not self.shard_metadata:
            raise ValueError("Shards not initialized")
        
        strategy = self.shard_metadata.strategy
        
        if strategy == ShardingStrategy.HASH_BASED:
            return self._hash_based_sharding(key)
        elif strategy == ShardingStrategy.CONSISTENT_HASHING:
            return self._consistent_hash_sharding(key)
        elif strategy == ShardingStrategy.RANGE_BASED:
            return self._range_based_sharding(key)
        elif strategy == ShardingStrategy.GEOGRAPHIC:
            return self._geographic_sharding(key)
        elif strategy == ShardingStrategy.TIME_BASED:
            return self._time_based_sharding(key)
        elif strategy == ShardingStrategy.COMPOSITE:
            return self._composite_sharding(key)
        else:
            raise ValueError(f"Unsupported sharding strategy: {strategy}")
    
    def _hash_based_sharding(self, key: Any) -> str:
        """Hash-based sharding"""
        key_str = str(key)
        hash_value = int(hashlib.md5(key_str.encode()).hexdigest(), 16)
        shard_index = hash_value % self.shard_metadata.total_shards
        shard_id = f"shard_{shard_index}"
        
        if shard_id not in self.shards:
            # Agar shard topilmasa, mavjud shardlardan birini tanlash
            shard_ids = list(self.shards.keys())
            return shard_ids[hash_value % len(shard_ids)]
        
        return shard_id
    
    def _consistent_hash_sharding(self, key: Any) -> str:
        """Consistent hashing sharding"""
        key_str = str(key)
        return self.consistent_hash_ring.get_node(key_str)
    
    def _range_based_sharding(self, key: Any) -> str:
        """Range-based sharding"""
        key_str = str(key)
        
        # Range mappings ni tekshirish
        for range_key, shard_id in self.range_mappings.items():
            if self._is_in_range(key_str, range_key):
                return shard_id
        
        # Default fallback - hash-based
        return self._hash_based_sharding(key)
    
    def _geographic_sharding(self, key: Any) -> str:
        """Geographic sharding"""
        # Kalitda region ma'lumoti bo'lishi kerak
        if isinstance(key, dict) and 'region' in key:
            region = key['region']
            for shard_id, shard_config in self.shards.items():
                if shard_config.region == region:
                    return shard_id
        
        # Region topilmasa, hash-based
        return self._hash_based_sharding(key)
    
    def _time_based_sharding(self, key: Any) -> str:
        """Time-based sharding"""
        if isinstance(key, dict) and 'timestamp' in key:
            timestamp = key['timestamp']
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            # Vaqtni shard nomiga aylantirish
            shard_time_key = timestamp.strftime("%Y_%m")  # Oylik shard
            shard_id = f"shard_{shard_time_key}"
            
            if shard_id not in self.shards:
                # Shard mavjud bo'lmasa, oxirgi shard ni qaytarish
                latest_shard = max(self.shards.keys())
                return latest_shard
            
            return shard_id
        
        # Timestamp bo'lmasa, hash-based
        return self._hash_based_sharding(key)
    
    def _composite_sharding(self, key: Any) -> str:
        """Composite sharding - bir nechta strategiyani birlashtirish"""
        if isinstance(key, dict):
            # Region va timestamp bo'yicha
            if 'region' in key and 'timestamp' in key:
                region = key['region']
                timestamp = key['timestamp']
                
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                
                # Composite key yaratish
                composite_key = f"{region}:{timestamp.strftime('%Y_%m')}"
                return self._hash_based_sharding(composite_key)
        
        # Fallback to hash-based
        return self._hash_based_sharding(key)
    
    def _is_in_range(self, value: str, range_spec: str) -> bool:
        """Qiymat range da ekanligini tekshirish"""
        # Range spec format: "start-end"
        try:
            start, end = range_spec.split('-')
            return start <= value <= end
        except ValueError:
            return False
    
    def set_range_mapping(self, range_spec: str, shard_id: str):
        """Range mapping sozlash"""
        self.range_mappings[range_spec] = shard_id
    
    def get_all_shard_ids(self) -> List[str]:
        """Barcha shard ID larni olish"""
        return list(self.shards.keys())
    
    def get_active_shards(self) -> List[str]:
        """Faol shardlarni olish"""
        return [shard_id for shard_id, config in self.shards.items() 
                if config.status == "active"]
    
    async def create_connection_pool(self, shard_id: str, pool_size: int = 10):
        """Shard uchun connection pool yaratish"""
        if shard_id not in self.shards:
            raise ValueError(f"Shard {shard_id} not found")
        
        config = self.shards[shard_id]
        
        # Connection string
        dsn = f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        
        # Pool yaratish
        pool = await asyncpg.create_pool(
            dsn,
            min_size=5,
            max_size=min(pool_size, config.max_connections)
        )
        
        self.pools[shard_id] = pool
        self.logger.info(f"Connection pool created for shard {shard_id}")
    
    async def get_pool(self, shard_id: str) -> asyncpg.pool.Pool:
        """Shard uchun pool olish"""
        if shard_id not in self.pools:
            await self.create_connection_pool(shard_id)
        return self.pools[shard_id]
    
    async def execute_query(self, shard_id: str, query: str, *args) -> List[Dict]:
        """Shard da query bajarish"""
        pool = await self.get_pool(shard_id)
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def execute_write(self, shard_id: str, query: str, *args) -> str:
        """Shard da write operation bajarish"""
        pool = await self.get_pool(shard_id)
        
        async with pool.acquire() as conn:
            result = await conn.execute(query, *args)
            return result
    
    async def close_all_pools(self):
        """Barcha pool larni yopish"""
        for pool in self.pools.values():
            await pool.close()
        self.pools.clear()


class QueryRouter:
    """Query Router - Query larni tegishli shard ga yo'naltirish"""
    
    def __init__(self, shard_manager: ShardManager):
        self.shard_manager = shard_manager
        self.logger = logging.getLogger(__name__)
    
    def extract_shard_key_from_query(self, query: str, parameters: Tuple) -> Optional[Any]:
        """Query dan shard key ni olish"""
        query_lower = query.lower()
        
        # SELECT querylar uchun WHERE condition dan shard key ni olish
        if query_lower.startswith('select'):
            # WHERE clause qidirish
            if 'where' in query_lower:
                # Oddiy shard key extraction (murakkabroq logic kerak bo'lishi mumkin)
                if parameters and len(parameters) > 0:
                    return parameters[0]  # Birinchi parameter ni shard key qilib olish
        
        # INSERT querylar uchun VALUES dan shard key ni olish
        elif query_lower.startswith('insert'):
            if parameters and len(parameters) > 0:
                return parameters[0]  # Birinchi field ni shard key qilib olish
        
        return None
    
    async def route_query(self, query: str, parameters: Tuple = ()) -> List[Dict]:
        """Query ni route qilish"""
        shard_key = self.extract_shard_key_from_query(query, parameters)
        
        if shard_key is None:
            # Agar shard key topilmasa, barcha shardlarda query bajarish
            # (read replicas va scattered queries uchun)
            results = []
            for shard_id in self.shard_manager.get_active_shards():
                try:
                    shard_results = await self.shard_manager.execute_query(shard_id, query, *parameters)
                    results.extend([{**result, '_shard_id': shard_id} for result in shard_results])
                except Exception as e:
                    self.logger.error(f"Query failed on shard {shard_id}: {e}")
            return results
        else:
            # Shard key mavjud - shu shard da query bajarish
            shard_id = self.shard_manager.get_shard_id(shard_key)
            
            try:
                results = await self.shard_manager.execute_query(shard_id, query, *parameters)
                return [{**result, '_shard_id': shard_id} for result in results]
            except Exception as e:
                self.logger.error(f"Query failed on shard {shard_id}: {e}")
                return []


class Rebalancer:
    """Database Rebalancer - Shard load ni qayta taqsimlash"""
    
    def __init__(self, shard_manager: ShardManager):
        self.shard_manager = shard_manager
        self.logger = logging.getLogger(__name__)
    
    def get_shard_load_stats(self) -> Dict[str, Dict]:
        """Shard load statistikasini olish"""
        stats = {}
        
        for shard_id in self.shard_manager.get_all_shard_ids():
            stats[shard_id] = {
                'connections': 0,  # Connection count
                'queries_per_second': 0.0,
                'average_response_time': 0.0,
                'storage_used': 0.0,
                'storage_limit': 1000.0  # GB
            }
        
        return stats
    
    def is_rebalancing_needed(self, threshold: float = 0.8) -> bool:
        """Rebalancing kerakligini tekshirish"""
        stats = self.get_shard_load_stats()
        
        # Storage usage bo'yicha tekshirish
        max_usage = max(stats[shard]['storage_used'] / stats[shard]['storage_limit'] 
                       for shard in stats)
        
        if max_usage > threshold:
            return True
        
        # Load imbalance tekshirish
        loads = [stats[shard]['queries_per_second'] for shard in stats]
        if len(loads) > 1:
            load_std = statistics.stdev(loads)
            load_mean = statistics.mean(loads)
            if load_mean > 0 and (load_std / load_mean) > 0.5:  # 50% coefficient of variation
                return True
        
        return False
    
    async def rebalance_shards(self) -> bool:
        """Shardlarni qayta taqsimlash"""
        try:
            self.logger.info("Starting shard rebalancing...")
            
            # Rebalancing strategy tanlash
            stats = self.get_shard_load_stats()
            
            # Og'irliklarni qayta hisoblash
            total_load = sum(stats[shard]['queries_per_second'] for shard in stats)
            
            for shard_id in stats:
                current_load = stats[shard_id]['queries_per_second']
                new_weight = max(1, int(current_load * 10 / total_load * len(stats)))
                
                # Weight ni yangilash
                if shard_id in self.shard_manager.shards:
                    self.shard_manager.shards[shard_id].weight = new_weight
                    # Consistent hash ring ni yangilash
                    self.shard_manager.consistent_hash_ring.remove_node(shard_id)
                    self.shard_manager.consistent_hash_ring.add_node(shard_id, new_weight)
            
            # Metadata ni yangilash
            if self.shard_manager.shard_metadata:
                self.shard_manager.shard_metadata.last_rebalanced = datetime.now()
            
            self.logger.info("Shard rebalancing completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Rebalancing failed: {e}")
            return False


class DataMigrator:
    """Data Migrator - Shardlar o'rtasida ma'lumotlarni ko'chirish"""
    
    def __init__(self, shard_manager: ShardManager, query_router: QueryRouter):
        self.shard_manager = shard_manager
        self.query_router = query_router
        self.logger = logging.getLogger(__name__)
    
    async def migrate_data(self, source_shard: str, target_shard: str, 
                         table: str, where_clause: str = "") -> bool:
        """Ma'lumotlarni shard o'rtasida ko'chirish"""
        try:
            # Read from source shard
            select_query = f"SELECT * FROM {table}"
            if where_clause:
                select_query += f" WHERE {where_clause}"
            
            source_results = await self.shard_manager.execute_query(source_shard, select_query)
            
            if not source_results:
                self.logger.info(f"No data to migrate from {source_shard} to {target_shard}")
                return True
            
            # Write to target shard
            for result in source_results:
                # INSERT query yaratish
                columns = list(result.keys())
                values = list(result.values())
                placeholders = ', '.join([f'${i+1}' for i in range(len(values))])
                columns_str = ', '.join(columns)
                
                insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                
                await self.shard_manager.execute_write(target_shard, insert_query, *values)
            
            # Delete from source shard (optional)
            if where_clause:
                delete_query = f"DELETE FROM {table} WHERE {where_clause}"
                await self.shard_manager.execute_write(source_shard, delete_query)
            
            self.logger.info(f"Migrated {len(source_results)} records from {source_shard} to {target_shard}")
            return True
            
        except Exception as e:
            self.logger.error(f"Data migration failed: {e}")
            return False
    
    async def bulk_migrate_shard(self, shard_id: str, migration_rules: Dict[str, Any]) -> bool:
        """Butun shard ni migration qilish"""
        try:
            target_shard = migration_rules.get('target_shard')
            tables = migration_rules.get('tables', [])
            
            for table in tables:
                where_clause = migration_rules.get('where_clause', "")
                success = await self.migrate_data(shard_id, target_shard, table, where_clause)
                
                if not success:
                    self.logger.error(f"Migration failed for table {table}")
                    return False
            
            # Source shard ni o'chirish
            if shard_id in self.shard_manager.shards:
                self.shard_manager.shards[shard_id].status = "migrated"
            
            self.logger.info(f"Shard {shard_id} migration completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Shard migration failed: {e}")
            return False


class OrionStarlineShardingSystem:
    """Orion Starline Sharding System"""
    
    def __init__(self):
        self.shard_manager = ShardManager()
        self.query_router = QueryRouter(self.shard_manager)
        self.rebalancer = Rebalancer(self.shard_manager)
        self.data_migrator = DataMigrator(self.shard_manager, self.query_router)
        self.logger = logging.getLogger(__name__)
    
    async def initialize_system(self):
        """Sharding sistemini inicializatsiya qilish"""
        # Shard metadata
        metadata = ShardMetadata(
            shard_id="main",
            strategy=ShardingStrategy.CONSISTENT_HASHING,
            total_shards=6,
            replica_count=2,
            consistency_level=ConsistencyLevel.EVENTUAL
        )
        
        # Shard konfiguratsiyasi
        shard_configs = [
            ShardConfig("shard_0", "db-node-1", 5432, "orion_shard_0", "orion_user", "password"),
            ShardConfig("shard_1", "db-node-2", 5432, "orion_shard_1", "orion_user", "password"),
            ShardConfig("shard_2", "db-node-3", 5432, "orion_shard_2", "orion_user", "password"),
            ShardConfig("shard_3", "db-node-4", 5432, "orion_shard_3", "orion_user", "password"),
            ShardConfig("shard_4", "db-node-5", 5432, "orion_shard_4", "orion_user", "password"),
            ShardConfig("shard_5", "db-node-6", 5432, "orion_shard_5", "orion_user", "password"),
        ]
        
        # Shardlarni inicializatsiya qilish
        self.shard_manager.initialize_shards(metadata, shard_configs)
        
        # Range mappings (masalan, user_id bo'yicha)
        self.shard_manager.set_range_mapping("0-166666", "shard_0")
        self.shard_manager.set_range_mapping("166667-333333", "shard_1")
        self.shard_manager.set_range_mapping("333334-499999", "shard_2")
        self.shard_manager.set_range_mapping("500000-666666", "shard_3")
        self.shard_manager.set_range_mapping("666667-833333", "shard_4")
        self.shard_manager.set_range_mapping("833334-999999", "shard_5")
        
        self.logger.info("Orion Starline Sharding System initialized")
    
    async def execute_user_query(self, user_id: str, query: str) -> List[Dict]:
        """Foydalanuvchi query si"""
        # User ID bo'yicha shard ni aniqlash
        shard_id = self.shard_manager.get_shard_id(user_id)
        
        # Query ni shu shard da bajarish
        return await self.shard_manager.execute_query(shard_id, query, user_id)
    
    async def execute_trading_query(self, trading_data: Dict[str, Any], query: str) -> List[Dict]:
        """Trading query si"""
        # Trading data bo'yicha shard ni aniqlash
        shard_id = self.shard_manager.get_shard_id(trading_data)
        
        # Query ni shu shard da bajarish
        return await self.shard_manager.execute_query(shard_id, query, *list(trading_data.values()))
    
    async def cross_shard_analytics(self, query_template: str, shard_ids: List[str] = None) -> List[Dict]:
        """Cross-shard analytics"""
        if shard_ids is None:
            shard_ids = self.shard_manager.get_active_shards()
        
        # Barcha shardlarda query bajarish
        all_results = []
        for shard_id in shard_ids:
            try:
                results = await self.shard_manager.execute_query(shard_id, query_template)
                all_results.extend([{**result, '_shard_id': shard_id} for result in results])
            except Exception as e:
                self.logger.error(f"Analytics query failed on shard {shard_id}: {e}")
        
        return all_results
    
    async def health_check(self) -> Dict[str, Any]:
        """Sharding sistemi holati"""
        stats = self.rebalancer.get_shard_load_stats()
        active_shards = self.shard_manager.get_active_shards()
        
        return {
            "total_shards": len(self.shard_manager.shards),
            "active_shards": len(active_shards),
            "shard_stats": stats,
            "strategy": self.shard_manager.shard_metadata.strategy.value if self.shard_manager.shard_metadata else "unknown",
            "needs_rebalancing": self.rebalancer.is_rebalancing_needed(),
            "last_rebalanced": self.shard_manager.shard_metadata.last_rebalanced.isoformat() 
                               if self.shard_manager.shard_metadata and self.shard_manager.shard_metadata.last_rebalanced 
                               else None
        }


# Global sharding system instance
_global_sharding_system: Optional[OrionStarlineShardingSystem] = None

def get_global_sharding_system() -> OrionStarlineShardingSystem:
    """Global sharding system olish"""
    global _global_sharding_system
    if _global_sharding_system is None:
        _global_sharding_system = OrionStarlineShardingSystem()
    return _global_sharding_system


if __name__ == "__main__":
    async def demo():
        """Demo - Database Sharding sistemi"""
        print("🚀 Orion Starline Database Sharding")
        print("=" * 50)
        
        # Sharding sistemini yaratish
        sharding_system = get_global_sharding_system()
        await sharding_system.initialize_system()
        
        # User query test
        print("👤 User Query Test:")
        user_id = "user_123456"
        user_query = "SELECT * FROM users WHERE user_id = $1"
        
        try:
            # Note: Bu yerda real database connection yo'q, shuning uchun simulyatsiya
            shard_id = sharding_system.shard_manager.get_shard_id(user_id)
            print(f"User {user_id} mapped to shard: {shard_id}")
            print(f"Query: {user_query}")
            print("✅ Query routed successfully")
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        # Trading query test
        print("\n📊 Trading Query Test:")
        trading_data = {
            "user_id": "user_789",
            "symbol": "EURUSD",
            "region": "eu-west",
            "timestamp": datetime.now()
        }
        
        trading_query = "SELECT * FROM trades WHERE user_id = $1 AND symbol = $2"
        shard_id = sharding_system.shard_manager.get_shard_id(trading_data)
        print(f"Trading data mapped to shard: {shard_id}")
        print(f"Query: {trading_query}")
        
        # Sharding strategiyalarini test qilish
        print("\n🔄 Sharding Strategies Test:")
        test_keys = [
            ("hash_key", "test_hash_123"),
            ("user_id", "user_456789"),
            ("geographic", {"region": "us-east", "user_id": "user_123"}),
            ("time_based", {"timestamp": datetime.now(), "user_id": "user_999"})
        ]
        
        strategies_to_test = [
            ShardingStrategy.HASH_BASED,
            ShardingStrategy.CONSISTENT_HASHING,
            ShardingStrategy.RANGE_BASED,
            ShardingStrategy.GEOGRAPHIC,
            ShardingStrategy.TIME_BASED
        ]
        
        for strategy in strategies_to_test:
            print(f"\nStrategy: {strategy.value}")
            sharding_system.shard_manager.shard_metadata.strategy = strategy
            
            for test_type, test_key in test_keys:
                try:
                    shard_id = sharding_system.shard_manager.get_shard_id(test_key)
                    print(f"  {test_type}: {shard_id}")
                except Exception as e:
                    print(f"  {test_type}: Error - {e}")
        
        # Rebalancing test
        print("\n⚖️ Rebalancing Test:")
        needs_rebalancing = sharding_system.rebalancer.is_rebalancing_needed()
        print(f"Needs rebalancing: {needs_rebalancing}")
        
        if needs_rebalancing:
            success = await sharding_system.rebalancer.rebalance_shards()
            print(f"Rebalancing result: {'✅' if success else '❌'}")
        
        # Health check
        print("\n🏥 Health Check:")
        health = await sharding_system.health_check()
        print(f"Total shards: {health['total_shards']}")
        print(f"Active shards: {health['active_shards']}")
        print(f"Strategy: {health['strategy']}")
        print(f"Needs rebalancing: {health['needs_rebalancing']}")
        print(f"Last rebalanced: {health['last_rebalanced'] or 'Never'}")
        
        # Cross-shard analytics demo
        print("\n📈 Cross-Shard Analytics Demo:")
        analytics_query = "SELECT COUNT(*) as user_count FROM users"
        # Bu yerda real query bajarilmaydi, faqat simulatsiya
        print(f"Analytics query: {analytics_query}")
        print("Query would run on all active shards and aggregate results")
        
        print("\n🎉 Demo tugallandi!")
        print("💾 Database Sharding sistemi tayyor!")
    
    asyncio.run(demo())