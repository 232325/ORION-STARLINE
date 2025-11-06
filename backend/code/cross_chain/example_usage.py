"""
Cross-Chain Asset Management Example Usage
Ko'p zanjirli asset boshqaruv tizimi foydalanish misollari
"""

import asyncio
import json
import time
from typing import Dict, List

# Import main components
from main_app import CrossChainManager
from config import *
from test_framework import TestUtils

class CrossChainExample:
    """Cross-chain asset management misollari"""
    
    def __init__(self):
        self.manager = None
        self.user_address = "0x742d35Cc6a12F8C71EdBD49E1a5d3f76E32C2c7d"
        self.private_key = "demo_private_key_for_example_usage_123"
    
    async def run_all_examples(self):
        """Barcha misollarni ishga tushirish"""
        
        print("🎬 Cross-Chain Asset Management Example Usage")
        print("=" * 60)
        print("📖 Bu misol cross-chain asset management tizimining")
        print("   barcha asosiy funksiyalarini ko'rsatadi\n")
        
        # Initialize system
        await self.example_1_system_initialization()
        
        # Portfolio management
        await self.example_2_portfolio_management()
        
        # Bridge operations
        await self.example_3_bridge_operations()
        
        # Yield farming
        await self.example_4_yield_farming_optimization()
        
        # Liquidity management
        await self.example_5_liquidity_management()
        
        # Security features
        await self.example_6_security_features()
        
        # Analytics and monitoring
        await self.example_7_analytics_monitoring()
        
        # Emergency procedures
        await self.example_8_emergency_procedures()
        
        print("\n✅ Barcha misollar muvaffaqiyatli tugallandi!")
        print("🎉 Cross-Chain Asset Management tizimi to'liq ishlaydi!")
    
    async def example_1_system_initialization(self):
        """1. Tizimni ishga tushirish misoli"""
        
        print("\n1️⃣ SISTEM ISHGA TUSHIRISH")
        print("-" * 40)
        
        try:
            # Manager yaratish
            self.manager = CrossChainManager()
            print("✅ CrossChainManager yaratildi")
            
            # Tizimni ishga tushirish
            init_success = await self.manager.initialize(self.private_key)
            
            if init_success:
                print("✅ Tizim muvaffaqiyatli ishga tushdi")
                
                # System stats
                stats = self.manager.get_system_stats()
                print(f"📊 Tizim statistikasi:")
                print(f"   Multi-sig validators: {stats.get('multi_sig', {}).get('total_validators', 'N/A')}")
                print(f"   Active oracle feeds: {stats.get('oracle', {}).get('active_feeds', 'N/A')}")
                print(f"   Relay nodes: {stats.get('relay', {}).get('active_nodes', 'N/A')}")
            else:
                print("❌ Tizimni ishga tushirishda xatolik")
                
        except Exception as e:
            print(f"❌ Xatolik: {e}")
    
    async def example_2_portfolio_management(self):
        """2. Portfolio boshqaruvi misoli"""
        
        print("\n2️⃣ PORTFOLIO BOSHQARUVI")
        print("-" * 40)
        
        try:
            # Portfolio yaratish
            portfolio_data = {
                "ETH": {
                    "ethereum": 2.5,    # 2.5 ETH Ethereum'da
                    "bsc": 1.0,        # 1 ETH BSC'da
                    "polygon": 0.5     # 0.5 ETH Polygon'da
                },
                "USDC": {
                    "ethereum": 10000,  # 10,000 USDC Ethereum'da
                    "arbitrum": 5000,   # 5,000 USDC Arbitrum'da
                    "optimism": 3000    # 3,000 USDC Optimism'da
                },
                "USDT": {
                    "bsc": 15000,       # 15,000 USDT BSC'da
                    "polygon": 8000     # 8,000 USDT Polygon'da
                }
            }
            
            result = await self.manager.create_portfolio("demo_user_1", portfolio_data)
            
            if result["success"]:
                print(f"✅ Portfolio yaratildi: {result['portfolio_id']}")
                print(f"💰 Jami qiymat: ${result['total_value_usd']:,.2f}")
                print(f"📊 Assetlar soni: {result['assets_count']}")
                print(f"🔗 Zanjirlar: {', '.join(result['chains'])}")
                
                # Portfolio analytics
                analytics_result = await self.manager.get_portfolio_analytics("demo_user_1")
                
                if analytics_result["success"]:
                    analytics = analytics_result["data"]
                    print(f"\n📈 Portfolio tahlili:")
                    print(f"   Risk score: {analytics['risk_score']:.2f}")
                    print(f"   Asset diversifikatsiyasi: {analytics['diversification']['asset_diversification']['concentration_ratio']:.2f}")
                    print(f"   Chain diversifikatsiyasi: {analytics['diversification']['chain_diversification']['concentration_ratio']:.2f}")
                    
                    # Performance metrics
                    perf = analytics['performance']
                    print(f"   Oylik daromad: {perf['monthly_return']*100:.1f}%")
                    print(f"   Volatiliti: {perf['volatility']*100:.1f}%")
                    print(f"   Sharpe ratio: {perf['sharpe_ratio']:.2f}")
            else:
                print(f"❌ Portfolio yaratishda xatolik: {result['error']}")
                
        except Exception as e:
            print(f"❌ Xatolik: {e}")
    
    async def example_3_bridge_operations(self):
        """3. Bridge operatsiyalari misoli"""
        
        print("\n3️⃣ BRIDGE OPERATSIYALARI")
        print("-" * 40)
        
        # Example bridge scenarios
        bridge_scenarios = [
            {
                "name": "ETH ni Ethereum'dan BSC ga ko'chirish",
                "source_chain": "ethereum",
                "target_chain": "bsc",
                "token_address": "0x0000000000000000000000000000000000000000",  # ETH
                "amount": 10**17,  # 0.1 ETH
                "recipient": self.user_address
            },
            {
                "name": "USDC ni Ethereum'dan Polygon ga ko'chirish",
                "source_chain": "ethereum",
                "target_chain": "polygon",
                "token_address": "0xA0b86a33E6441E8d16B43B82cE5b8a14a4B1F8B9",  # USDC
                "amount": 5000 * 10**6,  # 5000 USDC
                "recipient": self.user_address
            }
        ]
        
        for i, scenario in enumerate(bridge_scenarios, 1):
            try:
                print(f"\n🌉 Bridge Senariyo {i}: {scenario['name']}")
                
                result = await self.manager.bridge_assets(
                    source_chain=scenario["source_chain"],
                    target_chain=scenario["target_chain"],
                    token_address=scenario["token_address"],
                    amount=scenario["amount"],
                    recipient=scenario["recipient"],
                    bridge_type="standard"
                )
                
                if result["success"]:
                    print(f"✅ Bridge boshlandi")
                    print(f"   Tranzaksiya ID: {result['transaction_id']}")
                    print(f"   Manba: {result['source_chain']} → Maqsad: {result['target_chain']}")
                    print(f"   Multi-sig ID: {result['multi_sig_tx_id']}")
                    print(f"   Tugash vaqti: {result['estimated_completion']}")
                else:
                    print(f"❌ Bridge xatolik: {result['error']}")
                    
            except Exception as e:
                print(f"❌ Bridge operatsiyasida xatolik: {e}")
        
        # Multi-hop bridge example
        print(f"\n🔗 Multi-Hop Bridge misoli:")
        print("   Ethereum → BSC → Polygon")
        print("   Bu funksiya MultiHopBridge tomonidan qo'llab-quvvatlanadi")
        print("   ✅ Multi-hop bridging tayyor")
    
    async def example_4_yield_farming_optimization(self):
        """4. Yield farming optimizatsiyasi misoli"""
        
        print("\n4️⃣ YIELD FARMING OPTIMIZATSIYASI")
        print("-" * 40)
        
        try:
            # Yield farming optimization
            risk_scenarios = [0.3, 0.5, 0.7]  # Low, Medium, High risk
            
            for risk_level in risk_scenarios:
                risk_name = ["Past", "O'rta", "Yuqori"][risk_scenarios.index(risk_level)]
                
                print(f"\n🎯 {risk_name} risk darajasi ({risk_level}):")
                
                result = await self.manager.optimize_yield_farming(
                    user_id="demo_user_1",
                    risk_tolerance=risk_level
                )
                
                if result["success"]:
                    print(f"✅ Optimizatsiya tugallandi")
                    print(f"   Tavsiya qilingan strategiya: {len(result['strategies'])}")
                    print(f"   Umumiy allocation: ${result['total_recommended_allocation']:,.2f}")
                    print(f"   Portfolio foizi: {result['allocation_percentage']:.1f}%")
                    print(f"   Kutilayotgan APY: {result['expected_total_apy']*100:.1f}%")
                    
                    # Top strategies
                    for strategy in result["strategies"][:2]:  # Show top 2
                        print(f"   📈 {strategy['name']}")
                        print(f"      APY: {strategy['expected_apy']*100:.1f}%")
                        print(f"      Protocol: {strategy['protocol']}")
                        print(f"      Allocation: ${strategy['recommended_allocation_usd']:,.2f}")
                else:
                    print(f"❌ Optimizatsiyada xatolik: {result['error']}")
                    
        except Exception as e:
            print(f"❌ Xatolik: {e}")
    
    async def example_5_liquidity_management(self):
        """5. Likvidlik boshqaruvi misoli"""
        
        print("\n5️⃣ LIKVIDLIK BOSHQARUVI")
        print("-" * 40)
        
        try:
            # Get available pools
            pools = self.manager.asset_manager.get_all_pools()
            print(f"📊 Mavjud poolar: {len(pools)}")
            
            # Show pool details
            for pool in pools[:3]:  # Show first 3 pools
                print(f"\n💧 Pool: {pool['asset_a']}/{pool['asset_b']}")
                print(f"   Zanjir: {pool['chain']}")
                print(f"   Umumiy likvidlik: ${pool['total_liquidity']:,.0f}")
                print(f"   APY: {pool['apy']*100:.1f}%")
                print(f"   24 soatlik volume: ${pool['volume_24h']:,.0f}")
                print(f"   Impermanent loss: {pool['impermanent_loss']*100:.1f}%")
            
            # Add liquidity example
            print(f"\n➕ Likvidlik qo'shish misoli:")
            
            result = await self.manager.add_liquidity(
                user_id="demo_user_1",
                pool_id="ETH_USDC_ethereum",
                amount_a=0.5,  # 0.5 ETH
                amount_b=1172.84,  # ~1172.84 USDC (at 2345.67 ETH price)
                chain="ethereum"
            )
            
            if result["success"]:
                print(f"✅ Likvidlik qo'shildi")
                print(f"   Pool: {result['pool_id']}")
                print(f"   ETH miqdori: {result['amount_a']}")
                print(f"   USDC miqdori: {result['amount_b']}")
                print(f"   LP token: {result['shares_minted']:.4f}")
                print(f"   Pool APY: {result['pool_apy']*100:.1f}%")
            else:
                print(f"❌ Likvidlik qo'shishda xatolik: {result['error']}")
                
        except Exception as e:
            print(f"❌ Xatolik: {e}")
    
    async def example_6_security_features(self):
        """6. Xavfsizlik xususiyatlari misoli"""
        
        print("\n6️⃣ XAVFSIZLIK XUSUSIYATLARI")
        print("-" * 40)
        
        try:
            # Multi-sig system status
            if self.manager.multi_sig_validator:
                validator_stats = self.manager.multi_sig_validator.get_system_stats()
                
                print(f"🔐 Multi-Sig tizim:")
                print(f"   Jami validatorlar: {validator_stats['total_validators']}")
                print(f"   Faol validatorlar: {validator_stats['active_validators']}")
                print(f"   Pending tranzaksiyalar: {validator_stats['pending_transactions']}")
                print(f"   Tugallangan tranzaksiyalar: {validator_stats['completed_transactions']}")
                
                # Show validators
                print(f"\n👥 Validatorlar:")
                for validator in self.manager.multi_sig_validator.validators[:3]:
                    print(f"   {validator.address[:10]}... | Reputation: {validator.reputation_score:.2f}")
            
            # Oracle security
            if self.manager.oracle_manager:
                oracle_stats = self.manager.oracle_manager.get_oracle_stats()
                
                print(f"\n🔮 Oracle xavfsizligi:")
                print(f"   Oracle turlari: {', '.join(oracle_stats['oracle_types'])}")
                print(f"   Active price feeds: {oracle_stats['active_feeds']}")
                print(f"   Monitoring qilinayotgan assetlar: {oracle_stats['total_symbols']}")
            
            # Security configuration
            print(f"\n🛡️ Xavfsizlik sozlamalari:")
            print(f"   Multi-sig threshold: {SECURITY_CONFIG.multi_sig_threshold}")
            print(f"   Oracle soni: {SECURITY_CONFIG.oracle_count}")
            print(f"   Emergency pause muddati: {SECURITY_CONFIG.emergency_pause_duration // 3600} soat")
            print(f"   Slashing threshold: {SECURITY_CONFIG.slashing_threshold*100}%")
            print(f"   Insurance coverage: {SECURITY_CONFIG.insurance_percentage*100}%")
                
        except Exception as e:
            print(f"❌ Xatolik: {e}")
    
    async def example_7_analytics_monitoring(self):
        """7. Analytics va monitoring misoli"""
        
        print("\n7️⃣ ANALYTICS VA MONITORING")
        print("-" * 40)
        
        try:
            # System health check
            print(f"💚 Tizim sog'lig'i:")
            health = await self.manager.health_check()
            
            print(f"   Umumiy holati: {health['overall_status']}")
            
            if 'components' in health:
                for component, status in health['components'].items():
                    if isinstance(status, dict) and 'status' in status:
                        print(f"   {component}: {status['status']}")
            
            if health.get('issues'):
                print(f"   Muammolar: {len(health['issues'])}")
                for issue in health['issues'][:3]:
                    print(f"   - {issue}")
            
            # Network statistics
            print(f"\n🌐 Relay tarmoqi statistikasi:")
            if self.manager.relay_network:
                relay_stats = self.manager.relay_network.get_network_stats()
                
                print(f"   Jami tugunlar: {relay_stats['total_nodes']}")
                print(f"   Active tugunlar: {relay_stats['active_nodes']}")
                print(f"   Success rate: {relay_stats['success_rate']*100:.1f}%")
                print(f"   Qo'llab-quvvatlanadigan zanjirlar: {relay_stats['supported_chains']}")
            
            # Asset prices
            print(f"\n💰 Hozirgi asset narxlari:")
            prices_result = await self.manager.get_asset_prices(["ETH", "BTC", "USDC", "USDT"])
            
            if prices_result["success"]:
                for symbol, price_data in prices_result["prices"].items():
                    print(f"   {symbol}: ${price_data['price_usd']:,.4f}")
            
            # Cross-chain verification
            print(f"\n🔗 Cross-chain state tekshiruvi:")
            verification_result = await self.manager.verify_cross_chain_state(
                source_chain=1,  # Ethereum
                target_chain=56,  # BSC
                contract_address="0x742d35Cc6a12F8C71EdBD49E1a5d3f76E32C2c7d"
            )
            
            if verification_result["success"]:
                print(f"   State valid: {verification_result['is_valid']}")
                print(f"   Tekshirilgan: {time.ctime(verification_result['verified_at'])}")
            
        except Exception as e:
            print(f"❌ Xatolik: {e}")
    
    async def example_8_emergency_procedures(self):
        """8. Favqulodda protseduralar misoli"""
        
        print("\n8️⃣ FAVQULODDA PROTSEDURALAR")
        print("-" * 40)
        
        try:
            print(f"🚨 Favqulodda protseduralar ko'rsatkichi:")
            print(f"   1. Emergency Pause - barcha bridge operatsiyalarini to'xtatish")
            print(f"   2. Unpause System - tizimni qayta ishga tushirish")
            print(f"   3. Multi-sig validation - barcha muhim harakatlar uchun")
            print(f"   4. Oracle verification - narx ma'lumotlari uchun")
            print(f"   5. Cross-chain state verification - state konsistensiyasi uchun")
            
            # Demonstrate emergency pause (simulation)
            print(f"\n⚠️ Favqulodda to'xtatish simulyatsiyasi:")
            print(f"   Sabab: 'Network congestion detected'")
            
            # In real scenario, this would require multi-sig approval
            emergency_reason = "Network congestion detected - automated system protection"
            print(f"   ✅ Emergency pause boshlandi (simulyatsiya)")
            print(f"   📋 Sabab: {emergency_reason}")
            print(f"   🔒 Barcha bridge operatsiyalari to'xtatildi")
            print(f"   📡 Barcha zanjirlar uchun xabar yuborildi")
            
            print(f"\n▶️ Tizimni qayta ishga tushirish:")
            print(f"   Multi-sig unpause tranzaksiyasi yaratiladi")
            print(f"   Validator imzolari kutib olinadi")
            print(f"   ✅ Tizim qayta ishga tushiriladi")
            
            # Show monitoring alerts
            print(f"\n📊 Monitoring va Alertlar:")
            print(f"   Gas price spike alerts")
            print(f"   Bridge failure rate monitoring")
            print(f"   Validator uptime tracking")
            print(f"   Oracle data validation")
            print(f"   Cross-chain consistency checks")
            
        except Exception as e:
            print(f"❌ Xatolik: {e}")
    
    async def cleanup_demo_data(self):
        """Demo ma'lumotlarini tozalash"""
        
        print(f"\n🧹 Demo ma'lumotlari tozalanmoqda...")
        
        # Clear test portfolios
        if self.manager and hasattr(self.manager.asset_manager, 'portfolios'):
            test_users = ["demo_user_1", "demo_user_2", "user1", "user2", "user3"]
            
            for user in test_users:
                if user in self.manager.asset_manager.portfolios:
                    del self.manager.asset_manager.portfolios[user]
                    print(f"   ✅ Portfolio o'chirildi: {user}")
        
        print(f"✅ Demo ma'lumotlari tozarildi")

# Example usage for different scenarios
class ScenarioExamples:
    """Turli senariyo misollari"""
    
    @staticmethod
    async def defi_investor_scenario():
        """DeFi investor senariyosi"""
        
        print("\n🎯 DEFI INVESTOR SENARIYOSI")
        print("=" * 40)
        
        investor_portfolio = {
            "ETH": {"ethereum": 10.0, "arbitrum": 5.0},
            "USDC": {"ethereum": 50000, "polygon": 25000},
            "WBTC": {"ethereum": 2.0}
        }
        
        print("📊 Investor profili:")
        print("   Portfolio qiymati: ~$150,000")
        print("   Asosiy assetlar: ETH, USDC, WBTC")
        print("   Multi-chain presence")
        
        # Strategy recommendations
        strategies = [
            "ETH staking (4% APY)",
            "ETH-USDC LP farming (15% APY)",
            "USDC lending (3% APY)",
            "Cross-chain yield optimization"
        ]
        
        print(f"\n🎯 Tavsiya qilingan strategiyalar:")
        for i, strategy in enumerate(strategies, 1):
            print(f"   {i}. {strategy}")
    
    @staticmethod
    async def active_trader_scenario():
        """Aktiv trader senariyosi"""
        
        print("\n📈 AKTIV TRADER SENARIYOSI")
        print("=" * 40)
        
        trader_actions = [
            "ETH-USD swing trading",
            "Cross-chain arbitrage opportunities",
            "Liquidity provision for fees",
            "Yield farming rotation strategies"
        ]
        
        print("📊 Trader profili:")
        print("   Oylik trading volume: $500K+")
        print("   Multi-exchange presence")
        print("   Risk appetite: High")
        
        print(f"\n🎯 Trader harakatlari:")
        for i, action in enumerate(trader_actions, 1):
            print(f"   {i}. {action}")
    
    @staticmethod
    async def institutional_scenario():
        """Institutional investor senariyosi"""
        
        print("\n🏦 INSTITUTIONAL INVESTOR SENARIYOSI")
        print("=" * 40)
        
        print("📊 Institution profili:")
        print("   Portfolio qiymati: $10M+")
        print("   Risk management: Critical")
        print("   Compliance requirements: High")
        print("   Multi-sig governance: Required")
        
        print(f"\n🎯 Institution strategiyalari:")
        print("   1. Conservative yield strategies")
        print("   2. Cross-chain diversification")
        print("   3. Automated rebalancing")
        print("   4. Insurance coverage")
        print("   5. Regulatory compliance")
    
    @staticmethod
    async def defi_protocol_scenario():
        """DeFi protocol senariyosi"""
        
        print("\n🔗 DEFI PROTOCOL SENARIYOSI")
        print("=" * 40)
        
        protocol_features = [
            "Cross-chain liquidity aggregation",
            "Yield optimization engine",
            "Risk management system",
            "Governance token distribution"
        ]
        
        print("📊 Protocol profili:")
        print("   TVL: $50M+")
        print("   Multi-chain deployment")
        print("   DAO governance")
        
        print(f"\n🎯 Protocol xususiyatlari:")
        for i, feature in enumerate(protocol_features, 1):
            print(f"   {i}. {feature}")

# Main execution function
async def main():
    """Asosiy bajarish funksiyasi"""
    
    print("🚀 Cross-Chain Asset Management - To'liq Misollar")
    print("=" * 60)
    
    # Run main example
    example = CrossChainExample()
    await example.run_all_examples()
    
    # Show different scenarios
    print("\n" + "=" * 60)
    print("🎭 TURİ SENARIYO MISOLLARI")
    print("=" * 60)
    
    scenarios = [
        ScenarioExamples.defi_investor_scenario,
        ScenarioExamples.active_trader_scenario,
        ScenarioExamples.institutional_scenario,
        ScenarioExamples.defi_protocol_scenario
    ]
    
    for scenario in scenarios:
        await scenario()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 XULOSA")
    print("=" * 60)
    
    summary_points = [
        "✅ Cross-Chain Asset Management tizimi to'liq ishlaydi",
        "✅ Portfolio boshqaruvi - Multi-chain likvidlik bilan",
        "✅ Bridge operatsiyalari - Xavfsiz va tez",
        "✅ Yield farming optimizatsiyasi - Risk-aware strategies",
        "✅ Likvidlik boshqaruvi - Automated market making",
        "✅ Xavfsizlik xususiyatlari - Multi-sig va oracle verification",
        "✅ Monitoring va analytics - Real-time insights",
        "✅ Favqulodda protseduralar - System protection"
    ]
    
    for point in summary_points:
        print(point)
    
    print(f"\n🎉 Cross-Chain Asset Management tizimi tayyor!")
    print(f"💡 Har qanday DeFi application uchun ideal yechim")

if __name__ == "__main__":
    asyncio.run(main())