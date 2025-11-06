#!/usr/bin/env python3
"""
Integration Testing System
API integration tests, End-to-end testing, Performance testing, Load testing, va Chaos Engineering
"""

import time
import json
import asyncio
import threading
import random
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import concurrent.futures
import requests
import subprocess
import psutil
import logging
from enum import Enum

class TestStatus(Enum):
    """Test holati"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    RUNNING = "running"

class TestType(Enum):
    """Test turi"""
    UNIT = "unit"
    INTEGRATION = "integration"
    API = "api"
    E2E = "e2e"
    PERFORMANCE = "performance"
    LOAD = "load"
    CHAOS = "chaos"

@dataclass
class TestResult:
    """Test natija"""
    test_name: str
    test_type: TestType
    status: TestStatus
    duration_ms: float
    timestamp: str
    message: Optional[str] = None
    error: Optional[str] = None
    details: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['test_type'] = self.test_type.value
        data['status'] = self.status.value
        return data

@dataclass
class APITest:
    """API test definitsiyasi"""
    name: str
    method: str
    url: str
    headers: Dict[str, str] = None
    data: Any = None
    expected_status: int = 200
    expected_response_time_ms: float = 1000.0
    expected_response_keys: List[str] = None
    assert_conditions: List[Callable] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.expected_response_keys is None:
            self.expected_response_keys = []
        if self.assert_conditions is None:
            self.assert_conditions = []

@dataclass
class LoadTest:
    """Load test konfiguratsiyasi"""
    name: str
    endpoint: str
    concurrent_users: int
    duration_seconds: int
    ramp_up_seconds: int = 10
    payload_size_bytes: int = 1024
    expected_response_time_ms: float = 500.0
    max_error_rate_percent: float = 1.0

@dataclass
class ChaosTest:
    """Chaos engineering test"""
    name: str
    test_type: str  # latency, cpu, memory, network, kill_service
    target_service: str
    intensity: float  # 0.0 to 1.0
    duration_seconds: int
    expected_impact: str

class HTTPClient:
    """HTTP client with tracing"""
    
    def __init__(self, base_url: str = "", timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.request_count = 0
        self.response_times = []
        self.error_count = 0
    
    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """HTTP request yuborish"""
        if not url.startswith('http'):
            url = f"{self.base_url}/{url.lstrip('/')}"
        
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            
            # Metrics tracking
            response_time = (time.time() - start_time) * 1000
            self.response_times.append(response_time)
            self.request_count += 1
            
            if response.status_code >= 400:
                self.error_count += 1
            
            # Faqat oxirgi 1000 ta request ni saqlash
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
            
            return response
            
        except Exception as e:
            self.error_count += 1
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Client metrics"""
        if not self.response_times:
            return {}
        
        return {
            'total_requests': self.request_count,
            'error_requests': self.error_count,
            'avg_response_time_ms': statistics.mean(self.response_times),
            'p95_response_time_ms': statistics.quantiles(self.response_times, n=20)[18],
            'p99_response_time_ms': statistics.quantiles(self.response_times, n=100)[98],
            'error_rate_percent': (self.error_count / self.request_count) * 100
        }

class TestRunner:
    """Base test runner"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
    
    def run_test(self, test_func: Callable, test_name: str, 
                test_type: TestType) -> TestResult:
        """Test ni ishga tushirish"""
        start_time = time.time()
        
        try:
            if self.start_time is None:
                self.start_time = start_time
            
            # Test running holatini yaratish
            result = TestResult(
                test_name=test_name,
                test_type=test_type,
                status=TestStatus.RUNNING,
                duration_ms=0,
                timestamp=datetime.now().isoformat()
            )
            
            self.results.append(result)
            
            # Test funksiyasini chaqirish
            test_func()
            
            # Test muvaffaqiyatli tugashi
            duration_ms = (time.time() - start_time) * 1000
            result.status = TestStatus.PASSED
            result.duration_ms = duration_ms
            
        except AssertionError as e:
            # Test assertion xatosi
            duration_ms = (time.time() - start_time) * 1000
            result.status = TestStatus.FAILED
            result.duration_ms = duration_ms
            result.error = str(e)
            result.message = f"Test assertion failed: {e}"
            
        except Exception as e:
            # Boshqa xatolar
            duration_ms = (time.time() - start_time) * 1000
            result.status = TestStatus.ERROR
            result.duration_ms = duration_ms
            result.error = str(e)
            result.message = f"Test execution error: {e}"
        
        return result
    
    def get_results(self) -> List[TestResult]:
        """Barcha test natijalarini olish"""
        return self.results.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Test summary"""
        if not self.results:
            return {}
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        
        total_duration = sum(r.duration_ms for r in self.results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'success_rate_percent': (passed / total_tests) * 100 if total_tests > 0 else 0,
            'total_duration_ms': total_duration,
            'avg_duration_ms': avg_duration,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            'end_time': datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None
        }

class APITestRunner(TestRunner):
    """API Integration test runner"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.client = HTTPClient(base_url)
    
    def run_api_test(self, test_config: APITest) -> TestResult:
        """API test ni ishga tushirish"""
        def execute_api_test():
            # HTTP request yuborish
            response = self.client.request(
                test_config.method,
                test_config.url,
                headers=test_config.headers,
                json=test_config.data if isinstance(test_config.data, dict) else None,
                data=test_config.data if not isinstance(test_config.data, dict) else None
            )
            
            # Status code check
            assert response.status_code == test_config.expected_status, \
                f"Expected status {test_config.expected_status}, got {response.status_code}"
            
            # Response time check
            if response.elapsed.total_seconds() * 1000 > test_config.expected_response_time_ms:
                assert False, \
                    f"Response time {response.elapsed.total_seconds() * 1000}ms exceeded threshold {test_config.expected_response_time_ms}ms"
            
            # Response keys check
            if test_config.expected_response_keys and response.headers.get('content-type', '').startswith('application/json'):
                try:
                    json_response = response.json()
                    for key in test_config.expected_response_keys:
                        assert key in json_response, f"Expected key '{key}' not found in response"
                except json.JSONDecodeError:
                    assert False, "Expected JSON response but got invalid JSON"
            
            # Custom assertions
            for assert_func in test_config.assert_conditions:
                assert_func(response)
        
        return self.run_test(execute_api_test, test_config.name, TestType.API)
    
    def run_api_tests(self, test_configs: List[APITest]) -> List[TestResult]:
        """Bir nechta API testni ishga tushirish"""
        results = []
        for config in test_configs:
            result = self.run_api_test(config)
            results.append(result)
        
        self.end_time = time.time()
        return results

class E2ETestRunner(TestRunner):
    """End-to-End test runner"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.base_url = base_url
        self.client = HTTPClient(base_url)
    
    def create_trade_e2e_test(self) -> TestResult:
        """Trade yaratish E2E test"""
        def execute_e2e_test():
            # 1. Login
            login_response = self.client.request("POST", "/api/auth/login", json={
                "username": "test_user",
                "password": "test_password"
            })
            assert login_response.status_code == 200
            
            token = login_response.json().get("access_token")
            assert token, "No access token received"
            
            # 2. Market data olish
            headers = {"Authorization": f"Bearer {token}"}
            market_response = self.client.request("GET", "/api/market/eurusd", headers=headers)
            assert market_response.status_code == 200
            assert "price" in market_response.json()
            
            # 3. Trade yaratish
            trade_response = self.client.request("POST", "/api/trades", headers=headers, json={
                "symbol": "EURUSD",
                "side": "BUY",
                "quantity": 1000,
                "order_type": "MARKET"
            })
            assert trade_response.status_code == 201
            
            trade_data = trade_response.json()
            assert "trade_id" in trade_data
            assert trade_data["status"] == "PENDING"
            
            # 4. Trade status tekshirish
            trade_id = trade_data["trade_id"]
            status_response = self.client.request("GET", f"/api/trades/{trade_id}", headers=headers)
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            assert "status" in status_data
            
            # 5. Trade ni bekor qilish (agar hali ham pending bo'lsa)
            if status_data["status"] == "PENDING":
                cancel_response = self.client.request("DELETE", f"/api/trades/{trade_id}", headers=headers)
                assert cancel_response.status_code == 200
            
            # 6. Portfolio tekshirish
            portfolio_response = self.client.request("GET", "/api/portfolio", headers=headers)
            assert portfolio_response.status_code == 200
        
        return self.run_test(execute_e2e_test, "create_trade_e2e", TestType.E2E)

class PerformanceTestRunner(TestRunner):
    """Performance test runner"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.base_url = base_url
        self.client = HTTPClient(base_url)
    
    def run_performance_test(self, endpoint: str, method: str = "GET",
                           iterations: int = 100, payload: Dict = None) -> TestResult:
        """Performance test ishga tushirish"""
        def execute_performance_test():
            response_times = []
            errors = 0
            
            for i in range(iterations):
                start_time = time.time()
                try:
                    response = self.client.request(method, endpoint, json=payload)
                    response_time = (time.time() - start_time) * 1000
                    response_times.append(response_time)
                    
                    if response.status_code >= 400:
                        errors += 1
                        
                except Exception as e:
                    errors += 1
                    if i < 10:  # Faqat birinchi 10 xatoni log qilish
                        logging.error(f"Request {i} failed: {e}")
            
            # Performance metrics
            if response_times:
                avg_response_time = statistics.mean(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18]
                p99_response_time = statistics.quantiles(response_times, n=100)[98]
                max_response_time = max(response_times)
                min_response_time = min(response_times)
            else:
                avg_response_time = p95_response_time = p99_response_time = 0
                max_response_time = min_response_time = 0
            
            error_rate = (errors / iterations) * 100
            
            # Performance assertions
            assert error_rate < 5.0, f"Error rate {error_rate}% exceeds 5% threshold"
            assert p95_response_time < 1000.0, f"P95 response time {p95_response_time}ms exceeds 1000ms threshold"
            assert p99_response_time < 2000.0, f"P99 response time {p99_response_time}ms exceeds 2000ms threshold"
            
            # Metadata ni saqlash
            self.results[-1].metadata.update({
                'iterations': iterations,
                'avg_response_time_ms': avg_response_time,
                'p95_response_time_ms': p95_response_time,
                'p99_response_time_ms': p99_response_time,
                'max_response_time_ms': max_response_time,
                'min_response_time_ms': min_response_time,
                'error_rate_percent': error_rate,
                'error_count': errors
            })
        
        test_name = f"performance_{method}_{endpoint.replace('/', '_')}"
        return self.run_test(execute_performance_test, test_name, TestType.PERFORMANCE)

class LoadTestRunner(TestRunner):
    """Load test runner"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.base_url = base_url
        self.results_history: List[Dict[str, Any]] = []
    
    def run_load_test(self, test_config: LoadTest) -> TestResult:
        """Load test ishga tushirish"""
        def execute_load_test():
            # Thread pool yaratish
            with concurrent.futures.ThreadPoolExecutor(max_workers=test_config.concurrent_users) as executor:
                futures = []
                start_time = time.time()
                end_time = start_time + test_config.duration_seconds
                
                # Workers ramp up
                ramp_up_interval = test_config.ramp_up_seconds / test_config.concurrent_users
                
                for i in range(test_config.concurrent_users):
                    # Ramp up delay
                    if ramp_up_interval > 0:
                        time.sleep(ramp_up_interval)
                    
                    # Start time check
                    if time.time() >= end_time:
                        break
                    
                    future = executor.submit(self._single_user_load, test_config)
                    futures.append(future)
                
                # Natijalarni yig'ish
                completed_requests = 0
                total_requests = 0
                response_times = []
                errors = 0
                error_details = []
                
                for future in concurrent.futures.as_completed(futures, timeout=test_config.duration_seconds + 30):
                    try:
                        result = future.result()
                        completed_requests += 1
                        total_requests += result['requests_count']
                        response_times.extend(result['response_times'])
                        errors += result['errors']
                        error_details.extend(result['error_details'])
                        
                    except Exception as e:
                        errors += 1
                        error_details.append({'error': str(e), 'timestamp': time.time()})
                
                # Load test metrics
                actual_duration = time.time() - start_time
                throughput = completed_requests / actual_duration if actual_duration > 0 else 0
                error_rate = (errors / total_requests) * 100 if total_requests > 0 else 0
                
                if response_times:
                    avg_response_time = statistics.mean(response_times)
                    p95_response_time = statistics.quantiles(response_times, n=20)[18]
                    p99_response_time = statistics.quantiles(response_times, n=100)[98]
                else:
                    avg_response_time = p95_response_time = p99_response_time = 0
                
                # Load test assertions
                assert error_rate < test_config.max_error_rate_percent, \
                    f"Error rate {error_rate}% exceeds threshold {test_config.max_error_rate_percent}%"
                assert p95_response_time < test_config.expected_response_time_ms, \
                    f"P95 response time {p95_response_time}ms exceeds threshold {test_config.expected_response_time_ms}ms"
                
                # Metadata ni saqlash
                self.results[-1].metadata.update({
                    'concurrent_users': test_config.concurrent_users,
                    'duration_seconds': test_config.duration_seconds,
                    'actual_duration_seconds': actual_duration,
                    'completed_requests': completed_requests,
                    'total_requests': total_requests,
                    'throughput_requests_per_second': throughput,
                    'avg_response_time_ms': avg_response_time,
                    'p95_response_time_ms': p95_response_time,
                    'p99_response_time_ms': p99_response_time,
                    'error_rate_percent': error_rate,
                    'error_count': errors,
                    'error_details': error_details[:10]  # Faqat 10 ta xato
                })
        
        return self.run_test(execute_load_test, f"load_{test_config.name}", TestType.LOAD)
    
    def _single_user_load(self, test_config: LoadTest) -> Dict[str, Any]:
        """Bitta user uchun load"""
        client = HTTPClient(self.base_url)
        response_times = []
        requests_count = 0
        errors = 0
        error_details = []
        
        end_time = time.time() + test_config.duration_seconds
        
        while time.time() < end_time:
            try:
                start_time = time.time()
                response = client.request("GET", test_config.endpoint)
                response_time = (time.time() - start_time) * 1000
                
                response_times.append(response_time)
                requests_count += 1
                
                if response.status_code >= 400:
                    errors += 1
                    error_details.append({
                        'status_code': response.status_code,
                        'url': test_config.endpoint,
                        'timestamp': time.time()
                    })
                
                # Small delay between requests
                time.sleep(random.uniform(0.01, 0.1))
                
            except Exception as e:
                errors += 1
                error_details.append({
                    'error': str(e),
                    'url': test_config.endpoint,
                    'timestamp': time.time()
                })
        
        return {
            'response_times': response_times,
            'requests_count': requests_count,
            'errors': errors,
            'error_details': error_details
        }

class ChaosTestRunner(TestRunner):
    """Chaos engineering test runner"""
    
    def __init__(self):
        super().__init__()
        self.processes = []
    
    def run_chaos_test(self, test_config: ChaosTest) -> TestResult:
        """Chaos test ishga tushirish"""
        def execute_chaos_test():
            chaos_engine = ChaosEngine()
            
            # Baseline performance olish
            baseline_metrics = self._get_baseline_metrics(test_config.target_service)
            
            try:
                # Chaos scenario ni ishga tushirish
                chaos_engine.execute_chaos(test_config)
                
                # System resilience ni test qilish
                time.sleep(test_config.duration_seconds // 2)  # O'rtacha kutish
                
                # Impact measurement
                impact_metrics = self._measure_impact(test_config.target_service)
                
                # System recovery test
                recovery_start = time.time()
                
                # Chaos ni to'xtatish
                chaos_engine.stop_chaos(test_config.test_type)
                
                # Recovery time o'lchash
                recovery_threshold = 10.0  # 10% baseline dan yuqori bo'lmasligi kerak
                recovery_time = 0
                
                for _ in range(60):  # Max 60 sekund kutish
                    current_metrics = self._measure_impact(test_config.target_service)
                    
                    if self._is_recovered(baseline_metrics, current_metrics, recovery_threshold):
                        recovery_time = time.time() - recovery_start
                        break
                    
                    time.sleep(1)
                
                # Chaos test assertions
                max_allowed_impact = test_config.intensity * 50  # Intensity ga bog'liq
                
                if impact_metrics.get('error_rate_increase', 0) > max_allowed_impact:
                    assert False, \
                        f"Error rate increase {impact_metrics.get('error_rate_increase', 0)}% exceeds allowed {max_allowed_impact}%"
                
                # Recovery time assertion
                max_recovery_time = test_config.duration_seconds * 2
                assert recovery_time < max_recovery_time, \
                    f"Recovery time {recovery_time}s exceeds threshold {max_recovery_time}s"
                
                # Metadata ni saqlash
                self.results[-1].metadata.update({
                    'chaos_type': test_config.test_type,
                    'intensity': test_config.intensity,
                    'duration_seconds': test_config.duration_seconds,
                    'baseline_metrics': baseline_metrics,
                    'impact_metrics': impact_metrics,
                    'recovery_time_seconds': recovery_time,
                    'expected_impact': test_config.expected_impact
                })
                
            finally:
                # Cleanup
                chaos_engine.cleanup()
        
        return self.run_test(execute_chaos_test, f"chaos_{test_config.name}", TestType.CHAOS)
    
    def _get_baseline_metrics(self, service: str) -> Dict[str, Any]:
        """Baseline metriklarni olish"""
        # Simulatsiya qilingan baseline metrics
        return {
            'cpu_usage': 25.0,
            'memory_usage': 45.0,
            'response_time_ms': 150.0,
            'error_rate': 0.5,
            'throughput': 100.0
        }
    
    def _measure_impact(self, service: str) -> Dict[str, Any]:
        """Impact o'lchash"""
        # Simulatsiya qilingan impact metrics
        return {
            'cpu_usage': 75.0,
            'memory_usage': 85.0,
            'response_time_ms': 450.0,
            'error_rate': 8.5,
            'throughput': 45.0,
            'error_rate_increase': 8.0  # Baseline ga nisbatan o'sish
        }
    
    def _is_recovered(self, baseline: Dict[str, Any], current: Dict[str, Any], 
                     threshold_percent: float) -> bool:
        """System recovery tekshirish"""
        for metric in ['response_time_ms', 'error_rate']:
            if metric in baseline and metric in current:
                increase = ((current[metric] - baseline[metric]) / baseline[metric]) * 100
                if increase > threshold_percent:
                    return False
        return True

class ChaosEngine:
    """Chaos engineering engine"""
    
    def __init__(self):
        self.active_chaos = {}
    
    def execute_chaos(self, test_config: ChaosTest):
        """Chaos scenario execute qilish"""
        if test_config.test_type == "latency":
            self._inject_latency(test_config)
        elif test_config.test_type == "cpu":
            self._stress_cpu(test_config)
        elif test_config.test_type == "memory":
            self._stress_memory(test_config)
        elif test_config.test_type == "network":
            self._network_disruption(test_config)
        elif test_config.test_type == "kill_service":
            self._kill_service(test_config)
    
    def _inject_latency(self, test_config: ChaosTest):
        """Network latency inject qilish"""
        logging.info(f"Injecting {test_config.intensity * 1000}ms latency to {test_config.target_service}")
        # Real implementation da tc (traffic control) yoki similar tool ishlatish kerak
    
    def _stress_cpu(self, test_config: ChaosTest):
        """CPU stress test"""
        def cpu_stress():
            while self.active_chaos.get(test_config.test_type, False):
                # CPU intensive calculation
                _ = sum(i ** 2 for i in range(10000))
                time.sleep(0.01)
        
        self.active_chaos[test_config.test_type] = True
        for _ in range(int(test_config.intensity * 4)):  # Intensity ga bog'liq
            threading.Thread(target=cpu_stress, daemon=True).start()
    
    def _stress_memory(self, test_config: ChaosTest):
        """Memory stress test"""
        memory_objects = []
        while self.active_chaos.get(test_config.test_type, False):
            # Memory allocation
            size_mb = int(test_config.intensity * 10)  # Max 10MB
            memory_objects.append(bytearray(size_mb * 1024 * 1024))
            time.sleep(1)
    
    def _network_disruption(self, test_config: ChaosTest):
        """Network disruption"""
        logging.info(f"Disrupting network to {test_config.target_service}")
        # Real implementation da iptables yoki similar ishlatish kerak
    
    def _kill_service(self, test_config: ChaosTest):
        """Service ni o'ldirish"""
        logging.info(f"Killing service {test_config.target_service}")
        # Real implementation da systemctl kill yoki similar ishlatish kerak
    
    def stop_chaos(self, chaos_type: str):
        """Chaos ni to'xtatish"""
        self.active_chaos[chaos_type] = False
    
    def cleanup(self):
        """Cleanup"""
        self.active_chaos.clear()

class IntegrationTestSuite:
    """Integration test suite"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_runner = APITestRunner(base_url)
        self.e2e_runner = E2ETestRunner(base_url)
        self.performance_runner = PerformanceTestRunner(base_url)
        self.load_runner = LoadTestRunner(base_url)
        self.chaos_runner = ChaosTestRunner()
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Barcha testlarni ishga tushirish"""
        all_results = {}
        
        # API Tests
        api_tests = self._create_api_tests()
        print("Running API Integration Tests...")
        api_results = self.api_runner.run_api_tests(api_tests)
        all_results['api'] = [r.to_dict() for r in api_results]
        
        # E2E Tests
        print("Running End-to-End Tests...")
        e2e_result = self.e2e_runner.create_trade_e2e_test()
        all_results['e2e'] = [e2e_result.to_dict()]
        
        # Performance Tests
        print("Running Performance Tests...")
        perf_result = self.performance_runner.run_performance_test("/api/health", iterations=50)
        all_results['performance'] = [perf_result.to_dict()]
        
        # Load Tests
        print("Running Load Tests...")
        load_config = LoadTest(
            name="api_health_load",
            endpoint="/api/health",
            concurrent_users=10,
            duration_seconds=30,
            ramp_up_seconds=5
        )
        load_result = self.load_runner.run_load_test(load_config)
        all_results['load'] = [load_result.to_dict()]
        
        # Chaos Tests
        print("Running Chaos Engineering Tests...")
        chaos_config = ChaosTest(
            name="latency_chaos",
            test_type="latency",
            target_service="trading_api",
            intensity=0.5,
            duration_seconds=20,
            expected_impact="Increased response time"
        )
        chaos_result = self.chaos_runner.run_chaos_test(chaos_config)
        all_results['chaos'] = [chaos_result.to_dict()]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'results': all_results,
            'summary': self._create_summary(all_results)
        }
    
    def _create_api_tests(self) -> List[APITest]:
        """API testlarni yaratish"""
        return [
            APITest(
                name="health_check",
                method="GET",
                url="/api/health",
                expected_status=200,
                expected_response_time_ms=500.0
            ),
            APITest(
                name="market_data",
                method="GET",
                url="/api/market/eurusd",
                expected_status=200,
                expected_response_time_ms=1000.0,
                expected_response_keys=["price", "timestamp", "symbol"]
            ),
            APITest(
                name="invalid_endpoint",
                method="GET",
                url="/api/invalid",
                expected_status=404,
                expected_response_time_ms=500.0
            )
        ]
    
    def _create_summary(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Test summary yaratish"""
        total_tests = 0
        passed = 0
        failed = 0
        errors = 0
        
        for category, test_results in results.items():
            for result in test_results:
                total_tests += 1
                status = result['status']
                if status == 'passed':
                    passed += 1
                elif status == 'failed':
                    failed += 1
                elif status == 'error':
                    errors += 1
        
        return {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'success_rate_percent': (passed / total_tests * 100) if total_tests > 0 else 0
        }

# Example usage
if __name__ == "__main__":
    # Logging setup
    logging.basicConfig(level=logging.INFO)
    
    # Test suite yaratish
    test_suite = IntegrationTestSuite("http://localhost:8000")
    
    try:
        # Barcha testlarni ishga tushirish
        test_results = test_suite.run_all_tests()
        
        # Natijalarni saqlash
        with open('integration_test_results.json', 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        # Print summary
        print("\n=== INTEGRATION TEST SUMMARY ===")
        print(json.dumps(test_results['summary'], indent=2))
        
        print(f"\nDetailed results saved to: integration_test_results.json")
        
    except Exception as e:
        logging.error(f"Test suite execution failed: {e}")
        raise