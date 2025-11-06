#!/usr/bin/env python3
"""
AI Trading System - API Demo Script
API endpointlarini namuna ko'rsatish
"""

import asyncio
import httpx
import json
from datetime import datetime
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

class APIDemo:
    """API demo klassi"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.auth_token = None
        self.demo_results = []
    
    async def log_step(self, step: str, success: bool = True, message: str = ""):
        """Qadamni loglash"""
        status = "✅" if success else "❌"
        result = f"{status} {step}"
        if message:
            result += f" - {message}"
        
        print(result)
        self.demo_results.append({
            "step": step,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def check_health(self):
        """Tizim sog'ligini tekshirish"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                await self.log_step(
                    "Tizim sog'ligi tekshirish", 
                    True, 
                    f"Status: {data.get('status')}"
                )
                return True
            else:
                await self.log_step(
                    "Tizim sog'ligi tekshirish", 
                    False, 
                    f"HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            await self.log_step(
                "Tizim sog'ligi tekshirish", 
                False, 
                f"Xato: {str(e)}"
            )
            return False
    
    async def authenticate(self):
        """Autentifikatsiya"""
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                await self.log_step(
                    "Login", 
                    True, 
                    f"Token olindi: {bool(self.auth_token)}"
                )
                return True
            else:
                await self.log_step(
                    "Login", 
                    False, 
                    f"HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            await self.log_step("Login", False, f"Xato: {str(e)}")
            return False
    
    async def get_ai_signals(self):
        """AI signals olish"""
        if not self.auth_token:
            await self.log_step("AI Signals", False, "Token yo'q")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/ai-signals",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                signals_count = len(data.get("signals", []))
                await self.log_step(
                    "AI Signals olish", 
                    True, 
                    f"Signals: {signals_count}"
                )
            else:
                await self.log_step(
                    "AI Signals olish", 
                    False, 
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            await self.log_step("AI Signals olish", False, f"Xato: {str(e)}")
    
    async def create_ai_signal(self):
        """Yangi AI signal yaratish"""
        if not self.auth_token:
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            signal_data = {
                "symbol": "BTC/USDT",
                "signal_type": "buy",
                "confidence": 0.85,
                "price": 45000.00,
                "timeframe": "1h"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/ai-signals",
                json=signal_data,
                headers=headers
            )
            
            if response.status_code == 201:
                data = response.json()
                signal_id = data.get("signal", {}).get("id", "Unknown")
                await self.log_step(
                    "AI Signal yaratish", 
                    True, 
                    f"Signal ID: {signal_id}"
                )
            else:
                await self.log_step(
                    "AI Signal yaratish", 
                    False, 
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            await self.log_step("AI Signal yaratish", False, f"Xato: {str(e)}")
    
    async def get_quantum_analysis(self):
        """Quantum analysis olish"""
        if not self.auth_token:
            await self.log_step("Quantum Analysis", False, "Token yo'q")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/quantum-analysis",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                analyses_count = len(data.get("analyses", []))
                await self.log_step(
                    "Quantum Analysis olish", 
                    True, 
                    f"Analyses: {analyses_count}"
                )
            else:
                await self.log_step(
                    "Quantum Analysis olish", 
                    False, 
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            await self.log_step("Quantum Analysis olish", False, f"Xato: {str(e)}")
    
    async def get_blockchain_info(self):
        """Blockchain ma'lumotlari"""
        if not self.auth_token:
            await self.log_step("Blockchain Info", False, "Token yo'q")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/blockchain/info",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                network = data.get("network", "Unknown")
                await self.log_step(
                    "Blockchain Info olish", 
                    True, 
                    f"Network: {network}"
                )
            else:
                await self.log_step(
                    "Blockchain Info olish", 
                    False, 
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            await self.log_step("Blockchain Info olish", False, f"Xato: {str(e)}")
    
    async def get_dao_overview(self):
        """DAO overview"""
        if not self.auth_token:
            await self.log_step("DAO Overview", False, "Token yo'q")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/dao-governance/governance/overview",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                proposals = data.get("dao_info", {}).get("total_proposals", 0)
                await self.log_step(
                    "DAO Overview olish", 
                    True, 
                    f"Proposals: {proposals}"
                )
            else:
                await self.log_step(
                    "DAO Overview olish", 
                    False, 
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            await self.log_step("DAO Overview olish", False, f"Xato: {str(e)}")
    
    async def get_hft_metrics(self):
        """HFT metrikalar"""
        if not self.auth_token:
            await self.log_step("HFT Metrics", False, "Token yo'q")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(
                f"{self.base_url}/api/v1/hft-engine/metrics/real-time",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                running = data.get("hft_status", {}).get("is_running", False)
                await self.log_step(
                    "HFT Metrics olish", 
                    True, 
                    f"Running: {running}"
                )
            else:
                await self.log_step(
                    "HFT Metrics olish", 
                    False, 
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            await self.log_step("HFT Metrics olish", False, f"Xato: {str(e)}")
    
    async def test_websocket(self):
        """WebSocket test"""
        try:
            # Create WebSocket connection
            async with self.client.stream(
                "GET", 
                f"{self.base_url.replace('http', 'ws')}/api/v1/websocket/trading"
            ) as response:
                if response.status_code == 101:  # Switching Protocols
                    await self.log_step("WebSocket ulanish", True, "Muvaffaqiyatli")
                else:
                    await self.log_step(
                        "WebSocket ulanish", 
                        False, 
                        f"HTTP {response.status_code}"
                    )
        except Exception as e:
            await self.log_step("WebSocket ulanish", False, f"Xato: {str(e)}")
    
    async def run_demo(self):
        """Demo dasturini ishga tushirish"""
        print("🚀 AI Trading System API Demo")
        print("=" * 50)
        print(f"🌐 Server: {self.base_url}")
        print("-" * 50)
        
        # Check if server is running
        server_available = await self.check_health()
        if not server_available:
            print("\n⚠️  Server ishga tushgan emas! Iltimos, avval server'ni ishga tushiring:")
            print("   python run.py")
            return
        
        # Run demo steps
        await self.authenticate()
        await self.get_ai_signals()
        await self.create_ai_signal()
        await self.get_quantum_analysis()
        await self.get_blockchain_info()
        await self.get_dao_overview()
        await self.get_hft_metrics()
        await self.test_websocket()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Demo natijalari:")
        successful = sum(1 for result in self.demo_results if result["success"])
        total = len(self.demo_results)
        
        print(f"✅ Muvaffaqiyatli: {successful}/{total}")
        print(f"❌ Muvaffaqiyatsiz: {total - successful}/{total}")
        
        if successful == total:
            print("🎉 Demo muvaffaqiyatli yakunlandi!")
        else:
            print("⚠️  Ba'zi qadamlar bajarilmadi.")
        
        print(f"📝 Batafsil ma'lumot: {total} qadam bajarildi")
    
    async def cleanup(self):
        """Tozalash"""
        await self.client.aclose()

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Trading System API Demo")
    parser.add_argument("--url", "-u", default="http://localhost:8000", help="Server URL")
    
    args = parser.parse_args()
    
    demo = APIDemo(args.url)
    try:
        await demo.run_demo()
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    print("🧪 AI Trading System API Demo")
    print("Bu script API endpointlarini test qilish uchun")
    print("⚠️  Avval server'ni ishga tushiring: python run.py")
    print()
    
    asyncio.run(main())