"""
Performance Optimization Engine - Demo Script
============================================

Bu demo performance optimization modulining asosiy 
funksiyalarini ko'rsatadi.
"""

import asyncio
import logging
import time
import random
from ai_modules.performance_optimization import (
    PerformanceOptimizer,
    OptimizationLevel,
    CacheManager,
    MemoryCache,
    CacheStrategy,
    LoadBalancer,
    LoadBalancedNode,
    LoadBalanceStrategy,
    ModelManager,
    ModelType,
    ResourceMonitor,
    CostTracker,
    AsyncProcessor,
    AutoScaler,
    performance_monitor,
    cache_result,
    rate_limiter
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockModelProvider:
    """Mock model provider for demo"""
    
    def __init__(self, name: str, base_cost: float, base_latency: float):
        self.name = name
        self.base_cost = base_cost
        self.base_latency = base_latency
    
    async def process_request(self, prompt: str, **kwargs) -> str:
        # Simulatsiya qilingan API chaqiruv
        latency = self.base_latency * (1 + random.uniform(0, 0.5))
        await asyncio.sleep(latency)
        
        return f"Response from {self.name} for: {prompt[:50]}..."
    
    def get_cost(self, token_count: int) -> float:
        cost_per_token = self.base_cost / 1000
        return token_count * cost_per_token

async def demo_cache_manager():
    """Cache manager demo"""
    logger.info("=== CACHE MANAGER DEMO ===")
    
    # Memory cache yaratish
    memory_cache = MemoryCache(
        max_size=100,
        strategy=CacheStrategy.LRU
    )
    
    cache_manager = CacheManager(memory_cache=memory_cache)
    
    # Qimmat funksiya
    async def expensive_computation(x: int, y: int) -> int:
        await asyncio.sleep(0.5)  # 500ms simulatsiya
        return x * x + y * y
    
    # Cache'siz - birinchi chaqiruv
    logger.info("Cache'siz calculation...")
    start = time.time()
    result1 = await expensive_computation(10, 20)
    time1 = time.time() - start
    logger.info(f"Natija: {result1}, Vaqt: {time1:.3f}s")
    
    # Cache bilan - ikkinchi chaqiruv
    logger.info("Cache bilan calculation...")
    start = time.time()
    result2 = await cache_manager.get_cached_result(
        "expensive_calc_10_20",
        lambda: expensive_computation(10, 20)
    )
    time2 = time.time() - start
    logger.info(f"Natija: {result2}, Vaqt: {time2:.3f}s")
    
    # Cache statistikalari
    stats = cache_manager.get_cache_stats()
    logger.info(f"Cache Hit Rate: {stats['hit_rate']:.2%}")
    logger.info(f"Cache Size: {stats['size']}/{stats['max_size']}")

async def demo_load_balancer():
    """Load balancer demo"""
    logger.info("\\n=== LOAD BALANCER DEMO ===")
    
    # Load balancer yaratish
    load_balancer = LoadBalancer(
        strategy=LoadBalanceStrategy.FASTEST_RESPONSE
    )
    
    # Tugunlarni qo'shish
    nodes = [
        LoadBalancedNode("node1", "192.168.1.10", 8000, weight=2.0),
        LoadBalancedNode("node2", "192.168.1.11", 8000, weight=1.0),
        LoadBalancedNode("node3", "192.168.1.12", 8000, weight=1.5)
    ]
    
    for node in nodes:
        load_balancer.add_node(node)
        logger.info(f"Added node: {node.node_id}")
    
    # Eng yaxshi tugunni tanlash
    for i in range(5):
        best_node = await load_balancer.select_best_node()
        if best_node:
            # Simulatsiya qilingan response time
            response_time = random.uniform(0.1, 0.5)
            load_balancer.update_node_load(best_node.node_id, response_time)
            
            logger.info(f"Selected node: {best_node.node_id} "
                       f"(Response time: {response_time:.3f}s)")
    
    # Load balancer statistikalari
    stats = load_balancer.get_stats()
    logger.info(f"Total nodes: {stats['total_nodes']}")
    logger.info(f"Healthy nodes: {stats['healthy_nodes']}")

async def demo_model_manager():
    """Model manager demo"""
    logger.info("\\n=== MODEL MANAGER DEMO ===")
    
    # Model manager
    model_manager = ModelManager()
    
    # Mock model provider'lar
    providers = [
        MockModelProvider("GPT-4", base_cost=0.03, base_latency=0.8),
        MockModelProvider("Claude-3", base_cost=0.015, base_latency=0.6),
        MockModelProvider("GPT-3.5", base_cost=0.002, base_latency=0.4)
    ]
    
    # Modellarni ro'yxatga olish
    model_ids = ["gpt-4", "claude-3", "gpt-3.5"]
    model_types = [ModelType.OPENAI_GPT, ModelType.ANTHROPIC_CLAUDE, ModelType.OPENAI_GPT]
    
    for model_id, provider, model_type in zip(model_ids, providers, model_types):
        model_manager.register_model(model_id, provider, model_type)
        logger.info(f"Registered model: {model_id}")
    
    # Optimal model tanlash
    optimal_model = await model_manager.select_optimal_model(
        task_type="text_generation",
        cost_budget=0.05,
        latency_requirement=1.0
    )
    
    if optimal_model:
        logger.info(f"Optimal model: {optimal_model}")
    
    # Modellar bilan ishlash
    for model_id in model_ids:
        provider = providers[model_ids.index(model_id)]
        
        start = time.time()
        response = await provider.process_request("Bu test savoli")
        response_time = time.time() - start
        
        # Performance yozib olish
        await model_manager.record_performance(
            model_id=model_id,
            response_time=response_time,
            accuracy=random.uniform(0.85, 0.99),
            cost=provider.get_cost(len(response))
        )
        
        logger.info(f"Model {model_id}: {response_time:.3f}s, "
                   f"${provider.get_cost(len(response)):.4f}")
    
    # Model taqqoslash
    comparison = model_manager.get_model_comparison()
    logger.info("\\nModel Performance Comparison:")
    for model_id, perf in comparison.items():
        logger.info(f"{model_id}:")
        logger.info(f"  Response Time: {perf['response_time']:.3f}s")
        logger.info(f"  Accuracy: {perf['accuracy']:.2%}")
        logger.info(f"  Cost per request: ${perf['cost_per_request']:.4f}")

async def demo_resource_monitor():
    """Resource monitor demo"""
    logger.info("\\n=== RESOURCE MONITOR DEMO ===")
    
    # Resource monitor
    monitor = ResourceMonitor(monitoring_interval=2.0)
    
    # Monitoring boshlash
    monitor.start_monitoring()
    
    # Hozirgi resurs foydalanish
    current_usage = monitor.get_current_usage()
    logger.info(f"Current CPU: {current_usage.cpu_percent:.1f}%")
    logger.info(f"Current Memory: {current_usage.memory_percent:.1f}%")
    logger.info(f"Disk Usage: {current_usage.disk_usage:.1f}%")
    
    # Bir necha sample olish
    for i in range(3):
        await asyncio.sleep(2)
        usage = monitor.get_current_usage()
        logger.info(f"Sample {i+1}: CPU {usage.cpu_percent:.1f}%, "
                   f"Memory {usage.memory_percent:.1f}%")
    
    # 10 soniyaklik statistikalar
    stats = monitor.get_resource_stats(10)
    if "error" not in stats:
        logger.info(f"10s CPU Average: {stats['cpu']['avg']:.1f}%")
        logger.info(f"10s Memory Average: {stats['memory']['avg']:.1f}%")
    
    # Monitoring to'xtatish
    monitor.stop_monitoring()

async def demo_cost_tracker():
    """Cost tracker demo"""
    logger.info("\\n=== COST TRACKER DEMO ===")
    
    # Cost tracker
    cost_tracker = CostTracker()
    
    # Budgetlar belgilash
    cost_tracker.set_budgets(daily=100.0, monthly=2000.0)
    
    # API chaqiruvlar simulatsiyasi
    models = ["gpt-4", "claude-3", "gpt-3.5"]
    
    for i in range(10):
        model_id = random.choice(models)
        tokens = random.randint(500, 2000)
        
        if model_id == "gpt-4":
            cost = tokens * 0.03 / 1000
        elif model_id == "claude-3":
            cost = tokens * 0.015 / 1000
        else:  # gpt-3.5
            cost = tokens * 0.002 / 1000
        
        cost_tracker.record_api_call(
            model_id=model_id,
            tokens=tokens,
            cost=cost,
            response_time=random.uniform(0.3, 1.0)
        )
        
        logger.info(f"API call {i+1}: {model_id}, {tokens} tokens, ${cost:.4f}")
    
    # 24 soatlik xarajat tahlili
    analysis = cost_tracker.get_cost_analysis(24)
    logger.info("\\n24-hour Cost Analysis:")
    logger.info(f"Total cost: ${analysis['total_cost']:.2f}")
    logger.info(f"Total calls: {analysis['total_calls']}")
    logger.info(f"Average per call: ${analysis['avg_cost_per_call']:.4f}")
    
    # Model breakdown
    logger.info("\\nCost by Model:")
    for model, cost in analysis['model_breakdown'].items():
        logger.info(f"  {model}: ${cost:.2f}")
    
    # Optimizatsiya takiflari
    suggestions = cost_tracker.get_optimization_suggestions()
    if suggestions:
        logger.info("\\nOptimization Suggestions:")
        for suggestion in suggestions:
            logger.info(f"  - {suggestion}")

async def demo_async_processor():
    """Async processor demo"""
    logger.info("\\n=== ASYNC PROCESSOR DEMO ===")
    
    # Async processor
    async_processor = AsyncProcessor(
        max_workers=5,
        batch_size=10
    )
    
    # Test funksiyasi
    async def process_item(item: int) -> int:
        await asyncio.sleep(0.1)  # 100ms simulatsiya
        return item * item + random.randint(1, 10)
    
    # Batch processing
    logger.info("Batch processing 50 items...")
    items = list(range(1, 51))
    start = time.time()
    results = await async_processor.process_batch(items, process_item)
    batch_time = time.time() - start
    
    logger.info(f"Processed {len(results)} items in {batch_time:.3f}s")
    logger.info(f"Average per item: {batch_time/len(results):.4f}s")
    
    # Streaming processing demo
    logger.info("\\nStreaming processing...")
    
    async def data_stream():
        for i in range(20):
            await asyncio.sleep(0.05)
            yield i
    
    async def process_stream_item(item: int) -> str:
        await asyncio.sleep(0.05)
        return f"Processed: {item} -> {item * 2}"
    
    start = time.time()
    stream_count = 0
    async for result in async_processor.process_streaming(
        data_stream(), 
        process_stream_item
    ):
        stream_count += 1
        if stream_count <= 5:  # Faqat birinchi 5 ta natijani ko'rsatish
            logger.info(f"  {result}")
    
    stream_time = time.time() - start
    logger.info(f"Stream processed {stream_count} items in {stream_time:.3f}s")
    
    # Processing statistikalari
    stats = async_processor.get_processing_stats()
    logger.info(f"Success rate: {stats['success_rate']:.2%}")
    logger.info(f"Processed: {stats['processed']}")
    logger.info(f"Failed: {stats['failed']}")

async def demo_decorators():
    """Decorator funksiyalar demo"""
    logger.info("\\n=== DECORATORS DEMO ===")
    
    # Cache manager yaratish
    memory_cache = MemoryCache()
    cache_manager = CacheManager(memory_cache=memory_cache)
    
    @performance_monitor
    async def monitored_function(x: int, y: int) -> int:
        await asyncio.sleep(0.3)
        return x + y
    
    @cache_result(cache_manager, ttl=60)
    async def cached_function(x: int) -> int:
        await asyncio.sleep(0.5)
        return x ** 2
    
    @rate_limiter(max_calls=3, time_window=10)
    async def limited_function() -> str:
        await asyncio.sleep(0.1)
        return "Function called"
    
    # Performance monitor demo
    logger.info("Performance monitor demo:")
    for i in range(3):
        start = time.time()
        result = await monitored_function(5, 10)
        duration = time.time() - start
        logger.info(f"  Call {i+1}: {result} in {duration:.3f}s")
    
    # Cache decorator demo
    logger.info("\\nCache decorator demo:")
    for i in range(3):
        start = time.time()
        result = await cached_function(7)
        duration = time.time() - start
        logger.info(f"  Call {i+1}: {result} in {duration:.3f}s")
    
    # Rate limiter demo
    logger.info("\\nRate limiter demo:")
    for i in range(5):
        start = time.time()
        try:
            result = await limited_function()
            duration = time.time() - start
            logger.info(f"  Call {i+1}: {result} in {duration:.3f}s")
        except Exception as e:
            logger.info(f"  Call {i+1}: Rate limited - {e}")

async def demo_performance_optimizer():
    """To'liq performance optimizer demo"""
    logger.info("\\n=== PERFORMANCE OPTIMIZER DEMO ===")
    
    # Performance optimizer yaratish
    optimizer = PerformanceOptimizer(
        optimization_level=OptimizationLevel.MODERATE
    )
    
    # System optimizatsiyasini boshlash
    logger.info("Starting system optimization...")
    results = await optimizer.optimize_system()
    
    logger.info(f"Optimization status: {results.get('status', 'unknown')}")
    
    # Performance dashboard
    logger.info("\\nPerformance Dashboard:")
    dashboard = optimizer.get_performance_dashboard()
    
    # Cache stats
    cache_stats = dashboard.get('cache_stats', {})
    logger.info(f"Cache Hit Rate: {cache_stats.get('hit_rate', 0):.2%}")
    
    # Load balancer stats
    lb_stats = dashboard.get('load_balancer_stats', {})
    logger.info(f"Total Nodes: {lb_stats.get('total_nodes', 0)}")
    
    # Resource stats
    resource_stats = dashboard.get('resource_stats', {})
    if 'cpu' in resource_stats:
        logger.info(f"Average CPU: {resource_stats['cpu']['avg']:.1f}%")
    if 'memory' in resource_stats:
        logger.info(f"Average Memory: {resource_stats['memory']['avg']:.1f}%")
    
    # Cost analysis
    cost_analysis = dashboard.get('cost_analysis', {})
    if 'total_cost' in cost_analysis:
        logger.info(f"Total Cost: ${cost_analysis['total_cost']:.2f}")
    
    # Optimizatsiya takiflari
    recommendations = optimizer.get_optimization_recommendations()
    if recommendations:
        logger.info("\\nOptimization Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"  {i}. {rec}")
    
    # Optimizer to'xtatish
    await optimizer.stop()

async def main():
    """Asosiy demo funksiyasi"""
    logger.info("🚀 Performance Optimization Engine Demo")
    logger.info("=" * 50)
    
    try:
        # Barcha demo'larni ketma-ket ishga tushirish
        await demo_cache_manager()
        await demo_load_balancer()
        await demo_model_manager()
        await demo_resource_monitor()
        await demo_cost_tracker()
        await demo_async_processor()
        await demo_decorators()
        await demo_performance_optimizer()
        
        logger.info("\\n✅ Demo barcha qismlari muvaffaqiyatli tugallandi!")
        
    except Exception as e:
        logger.error(f"❌ Demo xatosi: {e}")
        raise

if __name__ == "__main__":
    # Demo'ni ishga tushirish
    asyncio.run(main())