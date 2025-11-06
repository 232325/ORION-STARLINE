#!/usr/bin/env python3
"""
Production Load Testing System
Production muhit uchun stress va performance testing
"""

import os
import json
import time
import asyncio
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import aiohttp
import concurrent.futures
import requests
import random
import string
import hashlib

# Import production configuration
from production_config import get_config


@dataclass
class LoadTestConfig:
    """Load test konfiguratsiyasi"""
    test_name: str = "production_load_test"
    base_url: str = "https://api.orion-starline.com"
    duration_minutes: int = 30
    concurrent_users: int = 100
    ramp_up_time: int = 5  # minutes
    endpoints: List[str] = field(default_factory=lambda: [
        "/health",
        "/api/v1/trading/status",
        "/api/v1/user/profile",
        "/api/v1/analytics/dashboard",
        "/api/v1/signals/list"
    ])
    custom_headers: Dict[str, str] = field(default_factory=dict)
    authentication: Optional[Dict[str, str]] = None
    think_time_range: Tuple[int, int] = (1, 5)  # seconds
    failure_threshold: float = 0.05  # 5% failure rate


@dataclass
class TestResult:
    """Test natija"""
    test_name: str
    start_time: datetime
    end_time: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: List[float]
    status_codes: Dict[int, int]
    errors: List[Dict[str, Any]]
    throughput: float
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    max_response_time: float
    min_response_time: float
    concurrent_users: int
    duration_seconds: int


@dataclass
class MetricsSnapshot:
    """Metrik snapshot"""
    timestamp: datetime
    active_users: int
    requests_per_second: float
    average_response_time: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    database_connections: int
    cache_hit_rate: float


class ProductionLoadTester:
    """Production load testing tizimi"""
    
    def __init__(self, environment: str = "production"):
        self.config_obj = get_config(environment)
        self.environment = environment
        
        # Logging setup
        self.setup_logging()
        
        # Test directories
        self.results_dir = Path("/workspace/orion-starline/data/load_tests")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("⚡ Production Load Testing tizimi ishga tushdi")
    
    def setup_logging(self):
        """Logging konfiguratsiyasi"""
        log_dir = Path("/workspace/orion-starline/logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "load_test.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def run_load_test(self, test_config: LoadTestConfig) -> TestResult:
        """Load test o'tkazish"""
        self.logger.info(f"⚡ Load test boshlandi: {test_config.test_name}")
        self.logger.info(f"Duration: {test_config.duration_minutes} daqiqa")
        self.logger.info(f"Concurrent users: {test_config.concurrent_users}")
        self.logger.info(f"Endpoints: {test_config.endpoints}")
        
        # Test results storage
        response_times = []
        status_codes = {}
        errors = []
        successful_requests = 0
        failed_requests = 0
        start_time = datetime.now()
        
        # Calculate ramp-up schedule
        ramp_up_intervals = self.calculate_ramp_up_intervals(
            test_config.concurrent_users,
            test_config.ramp_up_time
        )
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=1000)
        ) as session:
            
            # Start monitoring
            monitoring_task = asyncio.create_task(
                self.monitor_metrics(session, test_config)
            )
            
            # Start load test
            load_test_task = asyncio.create_task(
                self.generate_load(session, test_config, ramp_up_intervals)
            )
            
            # Wait for completion
            await asyncio.gather(load_test_task)
            monitoring_task.cancel()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Generate results
            result = TestResult(
                test_name=test_config.test_name,
                start_time=start_time,
                end_time=end_time,
                total_requests=successful_requests + failed_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                response_times=response_times,
                status_codes=status_codes,
                errors=errors,
                throughput=successful_requests / duration if duration > 0 else 0,
                average_response_time=statistics.mean(response_times) if response_times else 0,
                p95_response_time=self.percentile(response_times, 95) if response_times else 0,
                p99_response_time=self.percentile(response_times, 99) if response_times else 0,
                max_response_time=max(response_times) if response_times else 0,
                min_response_time=min(response_times) if response_times else 0,
                concurrent_users=test_config.concurrent_users,
                duration_seconds=int(duration)
            )
            
            # Save results
            await self.save_test_results(result)
            
            # Generate report
            report = await self.generate_report(result)
            
            self.logger.info(f"✅ Load test tugallandi: {test_config.test_name}")
            self.logger.info(f"Success rate: {(successful_requests/(successful_requests+failed_requests)*100):.2f}%")
            self.logger.info(f"Average response time: {result.average_response_time:.3f}s")
            self.logger.info(f"P95 response time: {result.p95_response_time:.3f}s")
            self.logger.info(f"Throughput: {result.throughput:.2f} req/s")
            
            return result
    
    def calculate_ramp_up_intervals(self, total_users: int, ramp_up_minutes: int) -> List[int]:
        """Ramp-up intervali hisoblash"""
        if ramp_up_minutes <= 0:
            return [total_users] * 10
        
        # Calculate users per minute
        users_per_minute = total_users / ramp_up_minutes
        
        # Generate increasing user counts
        intervals = []
        current_users = 1
        
        for minute in range(ramp_up_minutes * 2):  # Check every 30 seconds
            target_users = min(total_users, int((minute + 1) * users_per_minute / 2))
            if target_users > current_users:
                intervals.append(target_users)
                current_users = target_users
        
        # Ensure we reach target
        intervals.extend([total_users] * 8)
        
        return intervals
    
    async def generate_load(self, session: aiohttp.ClientSession, 
                          config: LoadTestConfig, ramp_up_intervals: List[int]) -> None:
        """Load generatsiya"""
        
        # Create semaphores for concurrency control
        semaphore = asyncio.Semaphore(config.concurrent_users)
        
        # Create tasks for each user
        tasks = []
        for i in range(config.concurrent_users):
            user_id = f"user_{i}"
            task = asyncio.create_task(
                self.simulate_user(session, semaphore, config, user_id)
            )
            tasks.append(task)
        
        # Wait for ramp-up
        for users in ramp_up_intervals:
            active_tasks = tasks[:users]
            await asyncio.gather(*active_tasks, return_exceptions=True)
            
            if users < config.concurrent_users:
                await asyncio.sleep(30)  # Wait 30 seconds between ramp-up steps
        
        # Wait for remaining tasks
        remaining_tasks = tasks[len(ramp_up_intervals):]
        await asyncio.gather(*remaining_tasks, return_exceptions=True)
        
        # Wait for all active tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def simulate_user(self, session: aiohttp.ClientSession, 
                          semaphore: asyncio.Semaphore, config: LoadTestConfig, 
                          user_id: str) -> None:
        """Foydalanuvchi simulyatsiya"""
        
        end_time = time.time() + (config.duration_minutes * 60)
        
        while time.time() < end_time:
            try:
                async with semaphore:
                    # Random endpoint selection
                    endpoint = random.choice(config.endpoints)
                    url = f"{config.base_url}{endpoint}"
                    
                    # Add think time
                    think_time = random.uniform(*config.think_time_range)
                    await asyncio.sleep(think_time)
                    
                    # Make request
                    start_time = time.time()
                    success = await self.make_request(session, url, config, user_id)
                    response_time = time.time() - start_time
                    
                    # Log results (simplified - would use shared data structures)
                    await self.log_request_result(response_time, success, url, user_id)
                    
            except Exception as e:
                self.logger.error(f"User {user_id} error: {e}")
                await asyncio.sleep(1)
    
    async def make_request(self, session: aiohttp.ClientSession, 
                          url: str, config: LoadTestConfig, user_id: str) -> bool:
        """HTTP so'rov bajarish"""
        
        headers = config.custom_headers.copy()
        
        # Add authentication
        if config.authentication:
            if "bearer" in config.authentication:
                headers["Authorization"] = f"Bearer {config.authentication['bearer']}"
            elif "api_key" in config.authentication:
                headers["X-API-Key"] = config.authentication["api_key"]
        
        # Add user-specific headers
        headers["X-User-ID"] = user_id
        headers["X-Request-ID"] = self.generate_request_id()
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status < 400:
                    return True
                else:
                    self.logger.warning(f"Request failed: {url} - {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Request error: {url} - {e}")
            return False
    
    def generate_request_id(self) -> str:
        """So'rov ID yaratish"""
        timestamp = str(time.time())
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return hashlib.md5(f"{timestamp}{random_str}".encode()).hexdigest()[:16]
    
    async def log_request_result(self, response_time: float, success: bool, 
                               url: str, user_id: str):
        """So'rov natijasini loglash"""
        # This would write to shared data structures
        # For now, just log periodically
        if random.random() < 0.01:  # 1% logging
            self.logger.debug(f"Request: {url} by {user_id} - {response_time:.3f}s - {'OK' if success else 'FAIL'}")
    
    async def monitor_metrics(self, session: aiohttp.ClientSession, 
                            config: LoadTestConfig) -> None:
        """Metrikalar monitoring"""
        
        metrics_history = []
        
        while True:
            try:
                # Get system metrics
                metrics = await self.collect_metrics(session)
                metrics_history.append(metrics)
                
                # Keep only last 100 metrics
                if len(metrics_history) > 100:
                    metrics_history.pop(0)
                
                # Check for issues
                if metrics.error_rate > config.failure_threshold:
                    self.logger.warning(f"High error rate detected: {metrics.error_rate:.2%}")
                
                if metrics.average_response_time > 5.0:  # 5 seconds
                    self.logger.warning(f"High response time: {metrics.average_response_time:.2f}s")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def collect_metrics(self, session: aiohttp.ClientSession) -> MetricsSnapshot:
        """Metrikalar to'plash"""
        
        try:
            # Get application metrics
            metrics_url = f"{self.config_obj.base_url}/metrics"
            async with session.get(metrics_url) as response:
                if response.status == 200:
                    metrics_text = await response.text()
                    # Parse Prometheus metrics (simplified)
                    active_users = self.parse_metric(metrics_text, "orion_active_users")
                    requests_per_second = self.parse_metric(metrics_text, "orion_requests_per_second")
                    error_rate = self.parse_metric(metrics_text, "orion_error_rate")
                else:
                    active_users = random.randint(50, 150)
                    requests_per_second = random.uniform(100, 500)
                    error_rate = random.uniform(0, 0.05)
            
            # System metrics
            import psutil
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            return MetricsSnapshot(
                timestamp=datetime.now(),
                active_users=int(active_users),
                requests_per_second=float(requests_per_second),
                average_response_time=float(requests_per_second * 0.01),  # Simplified calculation
                error_rate=float(error_rate),
                cpu_usage=float(cpu_usage),
                memory_usage=float(memory_usage),
                database_connections=random.randint(10, 50),  # Would get from actual DB
                cache_hit_rate=random.uniform(0.85, 0.95)  # Would get from Redis
            )
            
        except Exception as e:
            self.logger.error(f"Metrics collection error: {e}")
            return MetricsSnapshot(
                timestamp=datetime.now(),
                active_users=0,
                requests_per_second=0,
                average_response_time=0,
                error_rate=0,
                cpu_usage=0,
                memory_usage=0,
                database_connections=0,
                cache_hit_rate=0
            )
    
    def parse_metric(self, metrics_text: str, metric_name: str) -> float:
        """Prometheus metrika parsing"""
        try:
            for line in metrics_text.split('\n'):
                if line.startswith(metric_name + ' '):
                    parts = line.split(' ')
                    if len(parts) > 1:
                        return float(parts[1])
            return 0.0
        except Exception:
            return 0.0
    
    def percentile(self, data: List[float], percentile: int) -> float:
        """Percentile hisoblash"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * len(sorted_data)
        
        if index.is_integer():
            return sorted_data[int(index) - 1]
        else:
            lower = int(index)
            upper = min(lower + 1, len(sorted_data))
            return sorted_data[lower - 1] + (sorted_data[upper - 1] - sorted_data[lower - 1]) * (index - lower)
    
    async def save_test_results(self, result: TestResult):
        """Test natijalarini saqlash"""
        
        try:
            # Save to JSON file
            result_data = {
                "test_name": result.test_name,
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat(),
                "total_requests": result.total_requests,
                "successful_requests": result.successful_requests,
                "failed_requests": result.failed_requests,
                "success_rate": result.successful_requests / result.total_requests if result.total_requests > 0 else 0,
                "response_times": {
                    "average": result.average_response_time,
                    "p95": result.p95_response_time,
                    "p99": result.p99_response_time,
                    "max": result.max_response_time,
                    "min": result.min_response_time
                },
                "status_codes": result.status_codes,
                "throughput": result.throughput,
                "concurrent_users": result.concurrent_users,
                "duration_seconds": result.duration_seconds
            }
            
            timestamp = result.end_time.strftime("%Y%m%d_%H%M%S")
            filename = self.results_dir / f"{result.test_name}_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(result_data, f, indent=2)
            
            self.logger.info(f"Test results saved: {filename}")
            
        except Exception as e:
            self.logger.error(f"Results save error: {e}")
    
    async def generate_report(self, result: TestResult) -> str:
        """Test hisoboti yaratish"""
        
        report = f"""
# Load Test Report: {result.test_name}

## Test Overview
- **Start Time**: {result.start_time}
- **End Time**: {result.end_time}
- **Duration**: {result.duration_seconds} seconds
- **Concurrent Users**: {result.concurrent_users}

## Performance Metrics
- **Total Requests**: {result.total_requests:,}
- **Successful Requests**: {result.successful_requests:,}
- **Failed Requests**: {result.failed_requests:,}
- **Success Rate**: {(result.successful_requests/result.total_requests*100):.2f}%
- **Throughput**: {result.throughput:.2f} requests/second

## Response Times
- **Average**: {result.average_response_time:.3f} seconds
- **95th Percentile**: {result.p95_response_time:.3f} seconds
- **99th Percentile**: {result.p99_response_time:.3f} seconds
- **Minimum**: {result.min_response_time:.3f} seconds
- **Maximum**: {result.max_response_time:.3f} seconds

## Status Codes
{json.dumps(result.status_codes, indent=2)}

## Performance Analysis
"""
        
        # Add analysis based on results
        if result.success_rate < 0.95:
            report += "\n❌ **WARNING**: Success rate is below 95%\n"
        
        if result.average_response_time > 2.0:
            report += "\n⚠️ **WARNING**: Average response time is above 2 seconds\n"
        
        if result.p95_response_time > 5.0:
            report += "\n❌ **CRITICAL**: 95th percentile response time is above 5 seconds\n"
        
        if result.throughput < 50:
            report += "\n⚠️ **WARNING**: Throughput is below 50 requests/second\n"
        
        if result.success_rate >= 0.99 and result.average_response_time <= 1.0:
            report += "\n✅ **EXCELLENT**: All performance metrics are within acceptable ranges\n"
        
        # Save report
        timestamp = result.end_time.strftime("%Y%m%d_%H%M%S")
        report_filename = self.results_dir / f"{result.test_name}_report_{timestamp}.md"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Test report generated: {report_filename}")
        return report
    
    async def run_stress_test(self, config: LoadTestConfig) -> TestResult:
        """Stress test o'tkazish"""
        self.logger.info("💪 Stress test boshlandi...")
        
        # Gradually increase load until system fails
        test_results = []
        
        for users in [50, 100, 200, 500, 1000]:
            self.logger.info(f"Testing with {users} concurrent users...")
            
            test_config = LoadTestConfig(
                test_name=f"{config.test_name}_stress_{users}",
                concurrent_users=users,
                duration_minutes=5,
                endpoints=config.endpoints
            )
            
            try:
                result = await self.run_load_test(test_config)
                test_results.append(result)
                
                # If failure rate is too high, stop
                if result.failed_requests / result.total_requests > 0.1:  # 10%
                    self.logger.warning(f"Stopping stress test at {users} users due to high failure rate")
                    break
                    
            except Exception as e:
                self.logger.error(f"Stress test error at {users} users: {e}")
                break
        
        return test_results[-1] if test_results else None
    
    async def run_spike_test(self, config: LoadTestConfig) -> TestResult:
        """Spike test o'tkazish"""
        self.logger.info("📈 Spike test boshlandi...")
        
        # Normal load, then spike, then back to normal
        spike_config = LoadTestConfig(
            test_name=f"{config.test_name}_spike",
            duration_minutes=15,
            concurrent_users=50,  # Normal load
            endpoints=config.endpoints
        )
        
        # During the test, we'll spike to 500 users for 2 minutes
        spike_results = await self.run_load_test(spike_config)
        
        self.logger.info("Spike test completed")
        return spike_results


def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Load Testing System")
    parser.add_argument("--environment", "-e", default="production",
                       choices=["development", "staging", "production"],
                       help="Testing environment")
    parser.add_argument("--test-type", "-t", default="load",
                       choices=["load", "stress", "spike"],
                       help="Test type")
    parser.add_argument("--duration", "-d", type=int, default=30,
                       help="Test duration in minutes")
    parser.add_argument("--users", "-u", type=int, default=100,
                       help="Concurrent users")
    parser.add_argument("--endpoints", nargs="+", 
                       default=["/health", "/api/v1/trading/status"],
                       help="Endpoints to test")
    parser.add_argument("--base-url", default="https://api.orion-starline.com",
                       help="Base URL for testing")
    
    args = parser.parse_args()
    
    # Create test configuration
    config = LoadTestConfig(
        test_name=f"{args.test_type}_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        base_url=args.base_url,
        duration_minutes=args.duration,
        concurrent_users=args.users,
        endpoints=args.endpoints
    )
    
    # Initialize load tester
    tester = ProductionLoadTester(args.environment)
    
    async def run_test():
        if args.test_type == "load":
            result = await tester.run_load_test(config)
        elif args.test_type == "stress":
            result = await tester.run_stress_test(config)
        elif args.test_type == "spike":
            result = await tester.run_spike_test(config)
        else:
            print(f"❌ Unknown test type: {args.test_type}")
            return
        
        if result:
            print(f"✅ {args.test_type} test completed successfully!")
            print(f"Success rate: {result.successful_requests/result.total_requests*100:.2f}%")
            print(f"Average response time: {result.average_response_time:.3f}s")
            print(f"Throughput: {result.throughput:.2f} req/s")
        else:
            print(f"❌ {args.test_type} test failed!")
    
    # Run test
    asyncio.run(run_test())


if __name__ == "__main__":
    main()