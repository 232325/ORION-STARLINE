#!/usr/bin/env python3
"""
Orion Starline Infrastructure Integration Demo
==============================================

Bu script barcha infrastructure komponentlarini 
birgalikda ishlatishni ko'rsatadi.
"""

import asyncio
import time
import random
from datetime import datetime
import json

# Infrastructure komponentlarini import qilish
from microservices import get_global_orchestrator, ServiceFactory
from cache_system import get_global_cache_manager
from load_balancer import get_global_load_balancer
from database_sharding import get_global_sharding_system
from kubernetes_config import OrionStarlineK8sGenerator


class InfrastructureDemo:
    """Infrastructure integratsiya demo"""
    
    def __init__(self):
        self.orchestrator = None
        self.cache_manager = None
        self.load_balancer = None
        self.sharding_system = None
        self.k8s_generator = None
        
    async def initialize_all(self):
        """Barcha komponentlarni inicializatsiya qilish"""
        print("🚀 Infrastructure komponentlarini inicializatsiya qilish...")
        
        # Microservices Orchestrator
        print("  📦 Microservices Orchestrator...")
        self.orchestrator = get_global_orchestrator()
        
        # Cache Manager
        print("  💾 Cache Manager...")
        self.cache_manager = get_global_cache_manager()
        
        # Load Balancer
        print("  ⚖️ Load Balancer...")
        self.load_balancer = get_global_load_balancer()
        await self.load_balancer.start()
        
        # Database Sharding
        print("  🗄️ Database Sharding System...")
        self.sharding_system = get_global_sharding_system()
        await self.sharding_system.initialize_system()
        
        # Kubernetes Generator
        print("  ☸️ Kubernetes Configuration Generator...")
        self.k8s_generator = OrionStarlineK8sGenerator()
        
        print("✅ Barcha komponentlar tayyor!\n")
    
    async def deploy_infrastructure(self):
        """Infrastructure ni joylashtirish"""
        print("🏗️ Infrastructure joylashtirish...")
        
        # Microservices joylashtirish
        auth_config = ServiceFactory.create_auth_service()
        auth_instances = ["auth-1", "auth-2", "auth-3"]
        await self.orchestrator.deploy_service(auth_config, auth_instances)
        
        trading_config = ServiceFactory.create_trading_service()
        trading_instances = ["trading-1", "trading-2", "trading-3", "trading-4", "trading-5"]
        await self.orchestrator.deploy_service(trading_config, trading_instances)
        
        md_config = ServiceFactory.create_market_data_service()
        md_instances = ["md-1", "md-2"]
        await self.orchestrator.deploy_service(md_config, md_instances)
        
        print("  ✅ Microservices deployed")
        
        # Kubernetes manifests yaratish
        k8s_manifest = self.k8s_generator.generate_full_k8s_manifest()
        with open("kubernetes-manifest.yaml", "w") as f:
            f.write(k8s_manifest)
        
        print("  ✅ Kubernetes manifests yaratildi")
        print("✅ Infrastructure joylashtirish tugallandi!\n")
    
    async def simulate_traffic(self):
        """Traffic ni simulatsiya qilish"""
        print("🌊 Traffic simulatsiyasi...")
        
        # Test requests
        test_requests = [
            {
                "client_ip": f"192.168.1.{random.randint(1, 255)}",
                "method": "GET",
                "path": "/api/auth/profile",
                "headers": {"User-Agent": "TradingApp/1.0"}
            },
            {
                "client_ip": f"192.168.1.{random.randint(1, 255)}",
                "method": "GET", 
                "path": "/api/trading/positions",
                "headers": {"User-Agent": "TradingApp/1.0"}
            },
            {
                "client_ip": f"192.168.1.{random.randint(1, 255)}",
                "method": "GET",
                "path": "/api/market-data/EURUSD",
                "headers": {"User-Agent": "TradingApp/1.0"}
            }
        ]
        
        # Requestlarni yuborish
        for i, request_data in enumerate(test_requests, 1):
            print(f"  📤 Request {i}: {request_data['path']}")
            
            # Load balancer orqali
            start_time = time.time()
            result = await self.load_balancer.handle_request(request_data)
            lb_time = time.time() - start_time
            
            print(f"    Load Balancer: {result['server_id']} ({lb_time:.3f}s)")
            
            # Cache dan olish sinovi
            cache_key = f"demo:{request_data['path']}"
            cached_result = await self.cache_manager.cache.get(cache_key)
            
            if cached_result:
                print(f"    Cache: HIT ({len(str(cached_result))} bytes)")
            else:
                # Cache ga saqlash
                mock_data = {"data": f"Response for {request_data['path']}", "timestamp": datetime.now().isoformat()}
                await self.cache_manager.cache.set(cache_key, mock_data, ttl=300)
                print(f"    Cache: MISS → Saved to cache")
            
            print()
    
    async def database_operations(self):
        """Database operatsiyalari"""
        print("🗄️ Database operatsiyalari...")
        
        # User-based operations
        user_id = f"user_{random.randint(100000, 999999)}"
        shard_id = self.sharding_system.shard_manager.get_shard_id(user_id)
        print(f"  👤 User {user_id} → Shard: {shard_id}")
        
        # Trading data operations
        trading_data = {
            "user_id": user_id,
            "symbol": "EURUSD",
            "region": "eu-west",
            "timestamp": datetime.now()
        }
        trading_shard = self.sharding_system.shard_manager.get_shard_id(trading_data)
        print(f"  📊 Trading data → Shard: {trading_shard}")
        
        # Sharding health check
        health = await self.sharding_system.health_check()
        print(f"  📈 Database Health:")
        print(f"    Total shards: {health['total_shards']}")
        print(f"    Active shards: {health['active_shards']}")
        print(f"    Strategy: {health['strategy']}")
        print(f"    Needs rebalancing: {health['needs_rebalancing']}")
        
        # Cache integration
        cache_key = f"user:{user_id}:profile"
        cached_profile = await self.cache_manager.cache.get(cache_key, "user_cache")
        
        if not cached_profile:
            mock_profile = {
                "user_id": user_id,
                "name": "Demo User",
                "balance": 10000.0,
                "shard_id": shard_id,
                "cached_at": datetime.now().isoformat()
            }
            await self.cache_manager.cache.set(cache_key, mock_profile, ttl=1800, cache_name="user_cache")
            print(f"  💾 Profile cached in user_cache")
        else:
            print(f"  💾 Profile found in cache")
        
        print()
    
    async def scaling_simulation(self):
        """Scaling simulatsiyasi"""
        print("📈 Scaling simulatsiyasi...")
        
        # Auth service scale test
        print("  🔄 Auth Service scaling...")
        await self.orchestrator.scale_service("auth-service", 7)
        
        auth_status = await self.orchestrator.get_service_status("auth-service")
        print(f"    Target replicas: {auth_status['target_replicas']}")
        print(f"    Current replicas: {auth_status['current_replicas']}")
        print(f"    Health: {auth_status['overall_health']}")
        
        # Trading service load test
        print("  🔄 Trading Service load test...")
        
        # 20 ta parallel request
        tasks = []
        for i in range(20):
            request_data = {
                "client_ip": f"10.0.0.{i}",
                "method": "GET",
                "path": "/api/trading/market-status",
                "headers": {"User-Agent": f"LoadTest/{i}"}
            }
            task = self.load_balancer.handle_request(request_data)
            tasks.append(task)
        
        # Parallel execution
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful_requests = sum(1 for r in results if not isinstance(r, Exception))
        print(f"    Parallel requests: 20")
        print(f"    Successful: {successful_requests}")
        print(f"    Total time: {total_time:.2f}s")
        print(f"    Requests/sec: {20/total_time:.1f}")
        
        print()
    
    async def monitoring_dashboard(self):
        """Monitoring dashboard"""
        print("📊 Monitoring Dashboard")
        print("=" * 50)
        
        # Load Balancer stats
        lb_stats = self.load_balancer.load_balancer.get_stats()
        print("⚖️ Load Balancer:")
        print(f"  Total requests: {lb_stats['global_stats']['total_requests']}")
        print(f"  Success rate: {lb_stats['global_stats']['successful_requests']}/{lb_stats['global_stats']['total_requests']}")
        print(f"  Avg response time: {lb_stats['global_stats']['average_response_time']:.3f}s")
        print(f"  Available servers: {lb_stats['available_servers']}/{lb_stats['total_servers']}")
        
        # Cache metrics
        cache_metrics = await self.cache_manager.get_cache_metrics()
        print("\n💾 Cache System:")
        for cache_name, stats in cache_metrics.items():
            print(f"  {cache_name}:")
            print(f"    Hit rate: {stats['hit_rate']:.1%}")
            print(f"    Current size: {stats['current_size']}")
            print(f"    Hits/Misses: {stats['hits']}/{stats['misses']}")
        
        # Microservices status
        print("\n📦 Microservices:")
        for service_name in ["auth-service", "trading-service", "market-data-service"]:
            status = await self.orchestrator.get_service_status(service_name)
            print(f"  {service_name}:")
            print(f"    Replicas: {status['current_replicas']}/{status['target_replicas']}")
            print(f"    Health: {status['overall_health']}")
        
        # Database health
        db_health = await self.sharding_system.health_check()
        print("\n🗄️ Database Sharding:")
        print(f"  Strategy: {db_health['strategy']}")
        print(f"  Active shards: {db_health['active_shards']}/{db_health['total_shards']}")
        print(f"  Rebalancing needed: {db_health['needs_rebalancing']}")
        
        print()
    
    async def run_complete_demo(self):
        """To'liq demo"""
        print("🎯 Orion Starline Infrastructure Integration Demo")
        print("=" * 60)
        print()
        
        # 1. Initialization
        await self.initialize_all()
        
        # 2. Deployment
        await self.deploy_infrastructure()
        
        # 3. Traffic simulation
        await self.simulate_traffic()
        
        # 4. Database operations
        await self.database_operations()
        
        # 5. Scaling test
        await self.scaling_simulation()
        
        # 6. Monitoring
        await self.monitoring_dashboard()
        
        print("🎉 Demo tugallandi!")
        print("\n📋 Xulosa:")
        print("✅ Microservices orchestrator ishlaydi")
        print("✅ Load balancer traffic ni taqsimlaydi") 
        print("✅ Cache sistemi performance oshiradi")
        print("✅ Database sharding horizontal scaling ta'minlaydi")
        print("✅ Kubernetes konfiguratsiyasi yaratildi")
        print("✅ Monitoring va metrics ishlaydi")


async def main():
    """Asosiy demo funktsiya"""
    demo = InfrastructureDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    print("🚀 Orion Starline Infrastructure Demo boshlanmoqda...")
    asyncio.run(main())