#!/usr/bin/env python3
"""
AI Trading System - API Test Script
API endpoint'larini test qilish skripti
"""

import asyncio
import httpx
import json
from datetime import datetime
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.auth_token = None
        self.test_results = []
    
    async def log_test(self, test_name: str, success: bool, message: str = ""):
        """Test natijasini loglash"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"
        
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_health_check(self):
        """Health check test"""
        try:
            response = await self.client.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                await self.log_test("Health Check", True, f"Status: {data.get('status')}")
            else:
                await self.log_test("Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            await self.log_test("Health Check", False, str(e))
    
    async def test_authentication(self):
        """Authentication test"""
        try:
            # Test login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = await self.client.post(
                f"{API_BASE_URL}/api/v1/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                await self.log_test("Authentication", True, f"Token received: {bool(self.auth_token)}")
            else:
                await self.log_test("Authentication", False, f"Status: {response.status_code}")
        except Exception as e:
            await self.log_test("Authentication", False, str(e))
    
    async def test_ai_signals(self):
        """AI Signals test"""
        if not self.auth_token:
            await self.log_test("AI Signals", False, "No auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{API_BASE_URL}/api/v1/ai-signals",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                signals_count = len(data.get("signals", []))
                await self.log_test("AI Signals", True, f"Signals: {signals_count}")
            else:
                await self.log_test("AI Signals", False, f"Status: {response.status_code}")
        except Exception as e:
            await self.log_test("AI Signals", False, str(e))
    
    async def test_quantum_analysis(self):
        """Quantum Analysis test"""
        if not self.auth_token:
            await self.log_test("Quantum Analysis", False, "No auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{API_BASE_URL}/api/v1/quantum-analysis",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                analyses_count = len(data.get("analyses", []))
                await self.log_test("Quantum Analysis", True, f"Analyses: {analyses_count}")
            else:
                await self.log_test("Quantum Analysis", False, f"Status: {response.status_code}")
        except Exception as e:
            await self.log_test("Quantum Analysis", False, str(e))
    
    async def test_blockchain(self):
        """Blockchain test"""
        if not self.auth_token:
            await self.log_test("Blockchain", False, "No auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{API_BASE_URL}/api/v1/blockchain/info",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                network = data.get("network", "Unknown")
                await self.log_test("Blockchain", True, f"Network: {network}")
            else:
                await self.log_test("Blockchain", False, f"Status: {response.status_code}")
        except Exception as e:
            await self.log_test("Blockchain", False, str(e))
    
    async def test_dao_governance(self):
        """DAO Governance test"""
        if not self.auth_token:
            await self.log_test("DAO Governance", False, "No auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{API_BASE_URL}/api/v1/dao-governance/governance/overview",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                proposals_count = data.get("dao_info", {}).get("total_proposals", 0)
                await self.log_test("DAO Governance", True, f"Proposals: {proposals_count}")
            else:
                await self.log_test("DAO Governance", False, f"Status: {response.status_code}")
        except Exception as e:
            await self.log_test("DAO Governance", False, str(e))
    
    async def test_hft_engine(self):
        """HFT Engine test"""
        if not self.auth_token:
            await self.log_test("HFT Engine", False, "No auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{API_BASE_URL}/api/v1/hft-engine/metrics/real-time",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("hft_status", {}).get("is_running", False)
                await self.log_test("HFT Engine", True, f"Running: {status}")
            else:
                await self.log_test("HFT Engine", False, f"Status: {response.status_code}")
        except Exception as e:
            await self.log_test("HFT Engine", False, str(e))
    
    async def test_nft_hedge(self):
        """NFT Hedge test"""
        if not self.auth_token:
            await self.log_test("NFT Hedge", False, "No auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{API_BASE_URL}/api/v1/nft-hedge/collections",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                collections_count = len(data.get("collections", []))
                await self.log_test("NFT Hedge", True, f"Collections: {collections_count}")
            else:
                await self.log_test("NFT Hedge", False, f"Status: {response.status_code}")
        except Exception as e:
            await self.log_test("NFT Hedge", False, str(e))
    
    async def test_self_learning(self):
        """Self Learning test"""
        if not self.auth_token:
            await self.log_test("Self Learning", False, "No auth token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{API_BASE_URL}/api/v1/self-learning/models",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                models_count = data.get("total", 0)
                await self.log_test("Self Learning", True, f"Models: {models_count}")
            else:
                await self.log_test("Self Learning", False, f"Status: {response.status_code}")
        except Exception as e:
            await self.log_test("Self Learning", False, str(e))
    
    async def run_all_tests(self):
        """Barcha testlarni bajarish"""
        print("🧪 AI Trading System API Test")
        print("=" * 50)
        
        tests = [
            self.test_health_check,
            self.test_authentication,
            self.test_ai_signals,
            self.test_quantum_analysis,
            self.test_blockchain,
            self.test_dao_governance,
            self.test_hft_engine,
            self.test_nft_hedge,
            self.test_self_learning
        ]
        
        for test in tests:
            await test()
            await asyncio.sleep(0.1)  # Small delay between tests
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("🎉 Barcha testlar muvaffaqiyatli o'tdi!")
        else:
            print("⚠️  Ba'zi testlar xato berdi.")
        
        print(f"📝 To'liq natija: {len(self.test_results)} test bajarildi")
    
    async def cleanup(self):
        """Cleanup"""
        await self.client.aclose()

async def main():
    """Main function"""
    tester = APITester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    print("🚀 AI Trading System API test ishga tushmoqda...")
    print(f"🌐 Target URL: {API_BASE_URL}")
    print("-" * 50)
    
    asyncio.run(main())