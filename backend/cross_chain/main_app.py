"""
Cross-Chain Asset Management Main Application
Ko'p zanjirli asset boshqaruv asosiy dasturi
"""

import asyncio
import json
import time
from typing import Dict, List, Optional
from dataclasses import asdict
import logging

# Import all modules
from config import *
from bridge_contracts import (
    CrossChainBridge, EthereumBSCBridge, EthereumPolygonBridge, 
    MultiHopBridge, AtomicSwapBridge, BridgeTransaction
)
from multi_sig_validation import (
    MultiSigValidator, MultiSigTransaction, ActionType, 
    SignatureStatus, EmergencyProtocol
)
from oracle_verification import (
    OracleManager, OraclePrice, PriceStatus, 
    initialize_oracle_system, get_asset_price
)
from asset_management import (
    CrossChainAssetManager, Portfolio, RebalanceTrigger
)
from relay_network import (
    CrossChainRelayNetwork, RelayMessage, MessageType,
    initialize_relay_network, relay_cross_chain_message
)

class CrossChainManager:
    """Asosiy cross-chain asset manager"""
    
    def __init__(self):
        self.bridge_system = {}
        self.multi_sig_validator = None
        self.oracle_manager = None
        self.asset_manager = None
        self.relay_network = None
        self.emergency_protocol = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # System status
        self.is_initialized = False
        self.paused = False
        self.emergency_mode = False
        
        print("🚀 Cross-Chain Manager yaratildi")
    
    async def initialize(self, private_key: str):
        """Tizimni ishga tushirish"""
        
        try:
            print("🔄 Cross-Chain Asset Management tizimi ishga tushirilmoqda...")
            
            # 1. Multi-Signature Validator
            self.multi_sig_validator = MultiSigValidator(
                threshold=SECURITY_CONFIG.multi_sig_threshold,
                timeout_hours=24
            )
            print("✅ Multi-Signature Validator")
            
            # 2. Oracle System
            await initialize_oracle_system()
            self.oracle_manager = OracleManager()
            await self.oracle_manager.initialize_oracles()
            print("✅ Oracle Verification System")
            
            # 3. Asset Manager
            self.asset_manager = CrossChainAssetManager()
            print("✅ Asset Management System")
            
            # 4. Relay Network
            await initialize_relay_network()
            self.relay_network = relay_network
            print("✅ Cross-Chain Relay Network")
            
            # 5. Bridge Systems
            await self._initialize_bridges(private_key)
            print("✅ Bridge Systems")
            
            # 6. Emergency Protocol
            self.emergency_protocol = EmergencyProtocol(self.multi_sig_validator)
            print("✅ Emergency Protocol")
            
            # 7. Health Check
            health_status = await self.health_check()
            if health_status["overall_status"] != "healthy":
                self.logger.warning(f"Tizim holati: {health_status['overall_status']}")
            
            self.is_initialized = True
            print("🎉 Cross-Chain Asset Management tizimi muvaffaqiyatli ishga tushdi!")
            
            return True
            
        except Exception as e:
            print(f"❌ Tizimni ishga tushirishda xatolik: {e}")
            return False
    
    async def _initialize_bridges(self, private_key: str):
        """Bridge tizimlarini ishga tushirish"""
        
        # Ethereum-BSC Bridge
        self.bridge_system["ethereum_bsc"] = EthereumBSCBridge(private_key)
        await self.bridge_system["ethereum_bsc"].initialize_both()
        
        # Ethereum-Polygon Bridge
        self.bridge_system["ethereum_polygon"] = EthereumPolygonBridge(private_key)
        await self.bridge_system["ethereum_polygon"].initialize_both()
        
        # Multi-Hop Bridge
        self.bridge_system["multi_hop"] = MultiHopBridge({
            "ethereum": CrossChainBridge("ethereum", private_key),
            "bsc": CrossChainBridge("bsc", private_key),
            "polygon": CrossChainBridge("polygon", private_key),
            "arbitrum": CrossChainBridge("arbitrum", private_key),
            "optimism": CrossChainBridge("optimism", private_key)
        })
        
        # Atomic Swap Bridge
        self.bridge_system["atomic_swap"] = AtomicSwapBridge()
    
    async def bridge_assets(
        self,
        source_chain: str,
        target_chain: str,
        token_address: str,
        amount: int,
        recipient: str,
        bridge_type: str = "standard"
    ) -> Dict:
        """Assetlarni bridge qilish"""
        
        if not self.is_initialized:
            raise ValueError("Tizim ishga tushirilmagan")
        
        if self.paused or self.emergency_mode:
            raise ValueError("Tizim to'xtatilgan yoki favqulodda rejimda")
        
        try:
            # Amount validation
            if amount < 10**15:  # Minimum 0.001 ETH
                raise ValueError("Miqdor juda kichik")
            
            # Multi-sig tranzaksiya yaratish
            bridge_data = {
                "source_chain": source_chain,
                "target_chain": target_chain,
                "token_address": token_address,
                "amount": amount,
                "recipient": recipient,
                "bridge_type": bridge_type
            }
            
            tx_id = await self.multi_sig_validator.initiate_transaction(
                action_type=ActionType.BRIDGE_INITIATE,
                initiator=self._get_current_user(),
                parameters=bridge_data,
                private_key="user_private_key"
            )
            
            # Bridge yaratish
            bridge_key = f"{source_chain}_{target_chain}"
            
            if bridge_key not in self.bridge_system:
                raise ValueError(f"Ushbu ko'prik mavjud emas: {bridge_key}")
            
            bridge = self.bridge_system[bridge_key]
            
            # Bridge operation
            if hasattr(bridge, 'bridge_eth_to_bsc'):
                # Direct bridge
                if bridge_key == "ethereum_bsc":
                    transaction = await bridge.bridge_eth_to_bsc(amount, recipient)
                elif bridge_key == "ethereum_polygon":
                    transaction = await bridge.bridge_eth_to_polygon(amount, recipient)
            else:
                # General bridge
                transaction = await bridge.bridge_tokens(
                    token_address=token_address,
                    amount=amount,
                    recipient=recipient,
                    target_chain_id=self._get_chain_id(target_chain)
                )
            
            # Transaction status monitoring
            await self._monitor_transaction(transaction.tx_hash)
            
            result = {
                "success": True,
                "transaction_id": transaction.tx_hash,
                "source_chain": source_chain,
                "target_chain": target_chain,
                "amount": amount,
                "recipient": recipient,
                "multi_sig_tx_id": tx_id,
                "status": "pending",
                "estimated_completion": int(time.time()) + 1800  # 30 minutes
            }
            
            print(f"🌉 Bridge boshlandi: {transaction.tx_hash}")
            return result
            
        except Exception as e:
            self.logger.error(f"Bridge qilishda xatolik: {e}")
            return {
                "success": False,
                "error": str(e),
                "transaction_id": None
            }
    
    async def _monitor_transaction(self, tx_hash: str):
        """Tranzaksiyani kuzatib borish"""
        
        # Background monitoring
        asyncio.create_task(self._monitor_transaction_background(tx_hash))
    
    async def _monitor_transaction_background(self, tx_hash: str):
        """Background tranzaksiya monitoring"""
        
        max_attempts = 60  # 10 minutes
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Get status from bridge system
                # In real implementation, this would check actual transaction status
                
                await asyncio.sleep(10)  # Check every 10 seconds
                attempt += 1
                
            except Exception as e:
                self.logger.error(f"Tranzaksiya monitoring xatolik: {e}")
                break
    
    async def create_portfolio(
        self,
        user_id: str,
        initial_allocations: Dict[str, Dict[str, float]]
    ) -> Dict:
        """Portfolio yaratish"""
        
        if not self.is_initialized:
            raise ValueError("Tizim ishga tushirilmagan")
        
        try:
            portfolio = await self.asset_manager.create_portfolio(
                owner=user_id,
                initial_assets=initial_allocations
            )
            
            result = {
                "success": True,
                "portfolio_id": user_id,
                "total_value_usd": portfolio.total_value_usd,
                "assets_count": len(portfolio.assets),
                "chains": list(portfolio.chains.keys()),
                "created_at": int(time.time())
            }
            
            print(f"📊 Portfolio yaratildi: {user_id}")
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def rebalance_portfolio(
        self,
        user_id: str,
        target_allocation: Dict[str, float],
        rebalance_trigger: str = "manual"
    ) -> Dict:
        """Portfolio rebalancing"""
        
        if not self.is_initialized:
            raise ValueError("Tizim ishga tushirilmagan")
        
        try:
            trigger_enum = RebalanceTrigger.THRESHOLD_BREACH
            if rebalance_trigger == "time_based":
                trigger_enum = RebalanceTrigger.TIME_BASED
            elif rebalance_trigger == "volatility":
                trigger_enum = RebalanceTrigger.VOLATILITY_HIGH
            
            result = await self.asset_manager.rebalance_portfolio(
                owner=user_id,
                target_allocation=target_allocation,
                trigger=trigger_enum
            )
            
            print(f"🔄 Portfolio rebalanced: {user_id}")
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def optimize_yield_farming(
        self,
        user_id: str,
        risk_tolerance: float = 0.5
    ) -> Dict:
        """Yield farming optimizatsiyasi"""
        
        if not self.is_initialized:
            raise ValueError("Tizim ishga tushirilmagan")
        
        try:
            result = await self.asset_manager.optimize_yield_farming(
                owner=user_id,
                risk_tolerance=risk_tolerance
            )
            
            print(f"🎯 Yield farming optimizatsiyasi: {user_id}")
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def add_liquidity(
        self,
        user_id: str,
        pool_id: str,
        amount_a: float,
        amount_b: float,
        chain: str
    ) -> Dict:
        """Likvidlik qo'shish"""
        
        if not self.is_initialized:
            raise ValueError("Tizim ishga tushirilmagan")
        
        try:
            result = await self.asset_manager.add_liquidity(
                owner=user_id,
                pool_id=pool_id,
                amount_a=amount_a,
                amount_b=amount_b,
                chain=chain
            )
            
            print(f"💧 Likvidlik qo'shildi: {pool_id}")
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_portfolio_analytics(self, user_id: str) -> Dict:
        """Portfolio tahlili"""
        
        if not self.is_initialized:
            raise ValueError("Tizim ishga tushirilmagan")
        
        try:
            analytics = self.asset_manager.get_portfolio_analytics(user_id)
            return {"success": True, "data": analytics}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_asset_prices(self, symbols: List[str]) -> Dict:
        """Asset narxlarini olish"""
        
        if not self.is_initialized:
            raise ValueError("Tizim ishga tushirilmagan")
        
        try:
            prices = {}
            
            for symbol in symbols:
                price = await get_asset_price(symbol)
                if price:
                    prices[symbol] = {
                        "price_usd": price,
                        "timestamp": int(time.time())
                    }
            
            return {"success": True, "prices": prices}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def verify_cross_chain_state(
        self,
        source_chain: int,
        target_chain: int,
        contract_address: str
    ) -> Dict:
        """Cross-chain state verification"""
        
        if not self.is_initialized:
            raise ValueError("Tizim ishga tushirilmagan")
        
        try:
            expected_state = {"locked_amount": 0, "minted_amount": 0}
            
            is_valid = await self.oracle_manager.verify_cross_chain_state(
                source_chain=source_chain,
                target_chain=target_chain,
                contract_address=contract_address,
                expected_state=expected_state
            )
            
            return {
                "success": True,
                "is_valid": is_valid,
                "source_chain": source_chain,
                "target_chain": target_chain,
                "contract_address": contract_address,
                "verified_at": int(time.time())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def emergency_pause(self, reason: str) -> Dict:
        """Favqulodda to'xtatish"""
        
        if not self.is_initialized:
            raise ValueError("Tizim ishga tushirilmagan")
        
        try:
            # Emergency pause tranzaksiyasi
            tx_id = await self.emergency_protocol.initiate_emergency_pause(reason)
            
            # Tizimni to'xtatish
            self.emergency_mode = True
            self.paused = True
            
            # Barcha zanjirlar uchun xabar yuborish
            await self.relay_network.notify_emergency_pause(reason, "system_admin")
            
            result = {
                "success": True,
                "paused": True,
                "reason": reason,
                "pause_transaction_id": tx_id,
                "paused_at": int(time.time())
            }
            
            print(f"🚨 Favqulodda to'xtatish: {reason}")
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def unpause_system(self) -> Dict:
        """Tizimni qayta ishga tushirish"""
        
        if not self.is_initialized:
            raise ValueError("Tizim ishga tushirilmagan")
        
        try:
            # Multi-sig unpause tranzaksiyasi
            tx_id = await self.multi_sig_validator.initiate_transaction(
                action_type=ActionType.UNPAUSE_SYSTEM,
                initiator=self._get_current_user(),
                parameters={"reason": "manual_unpause"},
                private_key="user_private_key"
            )
            
            # Tizimni qayta ishga tushirish
            self.emergency_mode = False
            self.paused = False
            
            result = {
                "success": True,
                "unpaused": True,
                "unpause_transaction_id": tx_id,
                "unpaused_at": int(time.time())
            }
            
            print("▶️ Tizim qayta ishga tushirildi")
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict:
        """Tizim sog'lig'ini tekshirish"""
        
        health_status = {
            "overall_status": "healthy",
            "timestamp": int(time.time()),
            "components": {},
            "issues": []
        }
        
        try:
            # Multi-sig validator check
            if self.multi_sig_validator:
                validator_stats = self.multi_sig_validator.get_system_stats()
                health_status["components"]["multi_sig"] = {
                    "status": "healthy",
                    "active_validators": validator_stats["active_validators"],
                    "pending_transactions": validator_stats["pending_transactions"]
                }
            else:
                health_status["issues"].append("Multi-sig validator ishga tushmagan")
            
            # Oracle check
            if self.oracle_manager:
                oracle_stats = self.oracle_manager.get_oracle_stats()
                health_status["components"]["oracle"] = {
                    "status": "healthy",
                    "active_feeds": oracle_stats["active_feeds"],
                    "oracle_types": oracle_stats["oracle_types"]
                }
            else:
                health_status["issues"].append("Oracle manager ishga tushmagan")
            
            # Asset manager check
            if self.asset_manager:
                health_status["components"]["asset_manager"] = {
                    "status": "healthy",
                    "portfolios": len(self.asset_manager.portfolios),
                    "pools": len(self.asset_manager.liquidity_pools)
                }
            else:
                health_status["issues"].append("Asset manager ishga tushmagan")
            
            # Relay network check
            if self.relay_network:
                relay_stats = self.relay_network.get_network_stats()
                relay_health = await self.relay_network.health_check()
                
                health_status["components"]["relay_network"] = {
                    "status": relay_health["overall_status"],
                    "active_nodes": relay_stats["active_nodes"],
                    "success_rate": relay_stats["success_rate"]
                }
                
                if relay_health["overall_status"] != "healthy":
                    health_status["issues"].extend(relay_health["issues"])
            else:
                health_status["issues"].append("Relay network ishga tushmagan")
            
            # Bridge systems check
            bridge_count = len(self.bridge_system) if self.bridge_system else 0
            health_status["components"]["bridges"] = {
                "status": "healthy" if bridge_count > 0 else "warning",
                "active_bridges": bridge_count
            }
            
            # System status
            if self.paused:
                health_status["components"]["system"] = {"status": "paused"}
                health_status["overall_status"] = "paused"
            elif self.emergency_mode:
                health_status["components"]["system"] = {"status": "emergency"}
                health_status["overall_status"] = "emergency"
            else:
                health_status["components"]["system"] = {"status": "active"}
            
            # Overall status determination
            if len(health_status["issues"]) == 0:
                health_status["overall_status"] = "healthy"
            elif len(health_status["issues"]) <= 2:
                health_status["overall_status"] = "warning"
            else:
                health_status["overall_status"] = "critical"
            
            return health_status
            
        except Exception as e:
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": int(time.time())
            }
    
    def get_system_stats(self) -> Dict:
        """Tizim statistikasi"""
        
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        stats = {
            "system_status": "active" if not self.paused else "paused",
            "emergency_mode": self.emergency_mode,
            "timestamp": int(time.time())
        }
        
        # Component statistics
        if self.multi_sig_validator:
            stats["multi_sig"] = self.multi_sig_validator.get_system_stats()
        
        if self.oracle_manager:
            stats["oracle"] = self.oracle_manager.get_oracle_stats()
        
        if self.asset_manager:
            stats["assets"] = {
                "portfolios": len(self.asset_manager.portfolios),
                "pools": len(self.asset_manager.liquidity_pools),
                "strategies": len(self.asset_manager.yield_opportunities)
            }
        
        if self.relay_network:
            stats["relay"] = self.relay_network.get_network_stats()
        
        return stats
    
    def _get_current_user(self) -> str:
        """Hozirgi foydalanuvchi (demo)"""
        return "0x742d35Cc6a12F8C71EdBD49E1a5d3f76E32C2c7d"
    
    def _get_chain_id(self, chain_name: str) -> int:
        """Chain name'dan chain ID olish"""
        chain_ids = {
            "ethereum": 1,
            "bsc": 56,
            "polygon": 137,
            "arbitrum": 42161,
            "optimism": 10
        }
        return chain_ids.get(chain_name, 1)

# Demo functions
async def demo_cross_chain_management():
    """Cross-chain management demo"""
    
    print("🎬 Cross-Chain Asset Management Demo boshlanmoqda...")
    
    # Manager yaratish
    manager = CrossChainManager()
    
    # Private key (demo uchun)
    private_key = "demo_private_key_123456789"
    
    # Tizimni ishga tushirish
    print("\n1️⃣ Tizimni ishga tushirish...")
    init_success = await manager.initialize(private_key)
    
    if not init_success:
        print("❌ Tizimni ishga tushirishda xatolik")
        return
    
    # Portfolio yaratish
    print("\n2️⃣ Portfolio yaratish...")
    portfolio_data = {
        "ETH": {"ethereum": 1.0, "bsc": 0.5},
        "USDC": {"ethereum": 2000, "polygon": 1000},
        "USDT": {"bsc": 1500}
    }
    
    portfolio_result = await manager.create_portfolio("user123", portfolio_data)
    print(f"Portfolio yaratish: {portfolio_result}")
    
    # Asset narxlarini olish
    print("\n3️⃣ Asset narxlarini olish...")
    prices_result = await manager.get_asset_prices(["ETH", "USDC", "USDT", "WBTC"])
    print(f"Narxlar: {prices_result}")
    
    # Portfolio analytics
    print("\n4️⃣ Portfolio tahlili...")
    analytics_result = await manager.get_portfolio_analytics("user123")
    print(f"Analytics: {analytics_result}")
    
    # Yield farming optimizatsiya
    print("\n5️⃣ Yield farming optimizatsiya...")
    yield_result = await manager.optimize_yield_farming("user123", risk_tolerance=0.6)
    print(f"Yield farming: {yield_result}")
    
    # Bridge test
    print("\n6️⃣ Bridge test...")
    bridge_result = await manager.bridge_assets(
        source_chain="ethereum",
        target_chain="bsc",
        token_address="0x0000000000000000000000000000000000000000",  # ETH
        amount=10**17,  # 0.1 ETH
        recipient="0x742d35Cc6a12F8C71EdBD49E1a5d3f76E32C2c7d"
    )
    print(f"Bridge: {bridge_result}")
    
    # Tizim sog'lig'i
    print("\n7️⃣ Tizim sog'ligi...")
    health_result = await manager.health_check()
    print(f"Health: {health_result}")
    
    # Tizim statistikasi
    print("\n8️⃣ Tizim statistikasi...")
    system_stats = manager.get_system_stats()
    print(f"Stats: {system_stats}")
    
    print("\n✅ Demo tugallandi!")

if __name__ == "__main__":
    asyncio.run(demo_cross_chain_management())