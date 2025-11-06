"""
AI Trading Evolution - API Test Suite
====================================
Production API endpoints testing

Author: MiniMax Agent
Version: 1.0.0
Date: 2025-11-04
"""

import asyncio
import httpx
import json
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class APITester:
    """API endpoint'larni test qilish"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    async def test_endpoint(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        expected_status: int = 200
    ) -> Dict[str, Any]:
        """Bitta endpoint'ni test qilish"""
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                success = response.status_code == expected_status
                
                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status_code,
                    "expected_status": expected_status,
                    "success": success,
                    "response_time": response.elapsed.total_seconds(),
                    "data": response.json() if response.status_code < 500 else None
                }
                
                self.results.append(result)
                return result
                
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "expected_status": expected_status,
                "success": False,
                "error": str(e)
            }
            self.results.append(result)
            return result
    
    def print_results(self):
        """Natijalarni chiroyli formatda chiqarish"""
        
        # Table yaratish
        table = Table(title="API Test Natijalari", show_header=True, header_style="bold magenta")
        table.add_column("Endpoint", style="cyan")
        table.add_column("Method", style="yellow")
        table.add_column("Status", justify="center")
        table.add_column("Time (s)", justify="right", style="green")
        table.add_column("Result", justify="center")
        
        for result in self.results:
            status = f"{result['status_code']}"
            time_str = f"{result.get('response_time', 0):.3f}"
            success_icon = "✅" if result['success'] else "❌"
            
            table.add_row(
                result['endpoint'],
                result['method'],
                status,
                time_str,
                success_icon
            )
        
        console.print(table)
        
        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total - passed
        
        summary = f"""
        Total Tests: {total}
        Passed: {passed} ✅
        Failed: {failed} ❌
        Success Rate: {(passed/total*100):.1f}%
        """
        
        console.print(Panel(summary, title="Summary", border_style="green"))


async def main():
    """Asosiy test funksiyasi"""
    
    console.print(Panel.fit(
        "🧪 AI Trading Evolution API Test Suite",
        border_style="blue"
    ))
    
    tester = APITester()
    
    # Test 1: Root endpoint
    console.print("\n[bold cyan]Test 1: Root Endpoint[/bold cyan]")
    await tester.test_endpoint("GET", "/")
    
    # Test 2: Health check
    console.print("[bold cyan]Test 2: Health Check[/bold cyan]")
    await tester.test_endpoint("GET", "/health")
    
    # Test 3: Metrics
    console.print("[bold cyan]Test 3: Metrics[/bold cyan]")
    await tester.test_endpoint("GET", "/metrics")
    
    # Test 4: Strategy list
    console.print("[bold cyan]Test 4: Strategy List[/bold cyan]")
    await tester.test_endpoint("GET", "/api/v1/strategy/list")
    
    # Test 5: Strategy execution
    console.print("[bold cyan]Test 5: Strategy Execution[/bold cyan]")
    strategy_data = {
        "strategy_name": "grid",
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "parameters": {
            "grid_levels": 10,
            "price_range": 0.05
        }
    }
    await tester.test_endpoint("POST", "/api/v1/strategy/execute", strategy_data)
    
    # Test 6: Market symbols
    console.print("[bold cyan]Test 6: Market Symbols[/bold cyan]")
    await tester.test_endpoint("GET", "/api/v1/market/symbols?market_type=crypto")
    
    # Test 7: Market data
    console.print("[bold cyan]Test 7: Market Data[/bold cyan]")
    market_data = {
        "symbol": "BTC/USDT",
        "market_type": "crypto",
        "timeframe": "1h",
        "limit": 100
    }
    await tester.test_endpoint("POST", "/api/v1/market/data", market_data)
    
    # Test 8: Analytics types
    console.print("[bold cyan]Test 8: Analytics Types[/bold cyan]")
    await tester.test_endpoint("GET", "/api/v1/analytics/types")
    
    # Test 9: Analytics execution
    console.print("[bold cyan]Test 9: Analytics Execution[/bold cyan]")
    analytics_data = {
        "analysis_type": "sentiment",
        "symbol": "BTC/USDT",
        "parameters": {}
    }
    await tester.test_endpoint("POST", "/api/v1/analytics/analyze", analytics_data)
    
    # Test 10: API Documentation
    console.print("[bold cyan]Test 10: API Documentation[/bold cyan]")
    await tester.test_endpoint("GET", "/docs")
    
    # Natijalarni ko'rsatish
    console.print("\n")
    tester.print_results()
    
    # Detaylarni saqlash
    with open("test_results.json", "w") as f:
        json.dump(tester.results, f, indent=2)
    
    console.print("\n[green]✅ Test natijalari test_results.json faylida saqlandi[/green]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Test to'xtatildi[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Xatolik: {e}[/red]")
