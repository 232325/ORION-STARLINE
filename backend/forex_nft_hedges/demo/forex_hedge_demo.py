"""
Forex NFT Hedge System Demo
To'liq tizim demo va namoyish
"""

import asyncio
import json
import time
from typing import Dict, List
import logging
from datetime import datetime

from config import ForexPair, HedgeType, MarketRegime, QuantumStrategy, config
from core.forex_hedge_core import ForexHedgeManager
from nfts.nft_management import QuantumForexNFTManager
from quantum.quantum_optimization import QuantumForexOptimizer
from strategies.hedge_strategies import DynamicForexHedgeOrchestrator
from integration.forex_hedge_integration import ForexHedgeIntegrationFramework, PerformanceMonitor, SystemHealthMonitor

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ForexNHTHedgingDemo:
    """Forex NFT Hedging Demo - Asosiy demo klass"""
    
    def __init__(self):
        self.framework = None
        self.demo_results = {}
        self.logger = logging.getLogger(__name__)
    
    async def run_comprehensive_demo(self) -> Dict:
        """To'liq demo bajarish"""
        
        print("=" * 80)
        print("🌍 FOREX NFT HEDGING VA QUANTUM PORTFOLIO OPTIMIZATION DEMO")
        print("=" * 80)
        print()
        
        start_time = time.time()
        
        try:
            # 1. System initialization
            print("🚀 1. Tizimni inicializatsiya qilish...")
            await self._initialize_demo_system()
            
            # 2. Market data demonstration
            print("\n📊 2. Bozor ma'lumotlari namoyishi...")
            await self._demo_market_data()
            
            # 3. NFT creation and management
            print("\n🎨 3. NFT yaratish va boshqarish...")
            await self._demo_nft_management()
            
            # 4. Strategy execution
            print("\n⚡ 4. Strategiya bajarish...")
            await self._demo_strategy_execution()
            
            # 5. Quantum optimization
            print("\n🔮 5. Quantum optimallash...")
            await self._demo_quantum_optimization()
            
            # 6. Integration showcase
            print("\n🔗 6. Integration namoyishi...")
            await self._demo_integration_features()
            
            # 7. Performance monitoring
            print("\n📈 7. Performance monitoring...")
            await self._demo_performance_monitoring()
            
            # 8. System health check
            print("\n💚 8. Tizim sog'lig'i tekshirish...")
            await self._demo_system_health()
            
            # 9. Final comprehensive execution
            print("\n🎯 9. Comprehensive execution...")
            await self._demo_comprehensive_execution()
            
            # 10. Results summary
            demo_duration = time.time() - start_time
            await self._display_demo_summary(demo_duration)
            
            print("\n" + "=" * 80)
            print("✅ DEMO MUVAFFAQIYATLI YAKUNLANDI!")
            print("=" * 80)
            
            return self.demo_results
            
        except Exception as e:
            print(f"\n❌ Demo xatosi: {e}")
            self.logger.error(f"Demo failed: {e}")
            raise
    
    async def _initialize_demo_system(self):
        """Demo tizimini inicializatsiya qilish"""
        
        # Initialize integration framework
        self.framework = ForexHedgeIntegrationFramework()
        
        # Initialize system
        init_result = await self.framework.initialize_system()
        
        print(f"   ✅ Tizim initialized: {init_result['status']}")
        print(f"   📋 Components: {init_result['components']}")
        
        self.demo_results["initialization"] = init_result
    
    async def _demo_market_data(self):
        """Market data demo"""
        
        # Test market data collection
        market_data_results = {}
        
        for pair in [ForexPair.EURUSD, ForexPair.GBPUSD, ForexPair.USDJPY]:
            bid, ask = await self.framework.hedge_manager.market_manager.get_current_price(pair)
            volatility = await self.framework.hedge_manager.market_manager.calculate_volatility(pair)
            
            market_data_results[pair.value] = {
                "bid": bid,
                "ask": ask,
                "spread": ask - bid,
                "volatility": volatility,
                "hedge_opportunity": volatility > 0.12
            }
        
        print(f"   📊 Market Data for {len(market_data_results)} pairs:")
        for pair, data in market_data_results.items():
            print(f"      {pair}: bid={data['bid']:.4f}, ask={data['ask']:.4f}, vol={data['volatility']:.2%}")
        
        self.demo_results["market_data"] = market_data_results
    
    async def _demo_nft_management(self):
        """NFT management demo"""
        
        nft_creation_results = []
        
        # Create different types of NFTs
        hedge_types = [
            (HedgeType.PAIR_HEDGE, ForexPair.EURUSD),
            (HedgeType.VOLATILITY, ForexPair.GBPUSD),
            (HedgeType.CARRY_TRADE, ForexPair.AUDUSD),
            (HedgeType.CORRELATION, ForexPair.USDJPY),
            (HedgeType.CROSS_CURRENCY, ForexPair.EURJPY)
        ]
        
        for hedge_type, pair in hedge_types:
            try:
                token_id = await self.framework.nft_manager.create_quantum_enhanced_nft(
                    hedge_type=hedge_type,
                    pair=pair,
                    notional_amount=200000,
                    owner="0xDemoAddress1234567890abcdef1234567890abcdef1234"
                )
                
                status = await self.framework.nft_manager.get_nft_status(token_id)
                
                nft_creation_results.append({
                    "token_id": token_id,
                    "hedge_type": hedge_type.value,
                    "pair": pair.value,
                    "status": status,
                    "quantum_enhanced": True
                })
                
                print(f"   🎨 NFT yaratildi: {token_id} ({hedge_type.value} - {pair.value})")
                
            except Exception as e:
                print(f"   ❌ NFT yaratish xatosi ({hedge_type.value}): {e}")
        
        print(f"   ✅ Jami {len(nft_creation_results)} ta NFT yaratildi")
        
        self.demo_results["nft_management"] = {
            "created_nfts": nft_creation_results,
            "total_created": len(nft_creation_results)
        }
    
    async def _demo_strategy_execution(self):
        """Strategy execution demo"""
        
        # Execute different strategies
        strategy_results = {}
        
        # Pair hedge strategy
        print("   ⚡ Pair Hedge Strategy...")
        pair_result = await self._execute_single_strategy(HedgeType.PAIR_HEDGE, ForexPair.EURUSD)
        strategy_results["pair_hedge"] = pair_result
        
        # Volatility hedge strategy
        print("   ⚡ Volatility Hedge Strategy...")
        vol_result = await self._execute_single_strategy(HedgeType.VOLATILITY, ForexPair.GBPUSD)
        strategy_results["volatility_hedge"] = vol_result
        
        # Carry trade strategy
        print("   ⚡ Carry Trade Strategy...")
        carry_result = await self._execute_single_strategy(HedgeType.CARRY_TRADE, ForexPair.AUDUSD)
        strategy_results["carry_trade"] = carry_result
        
        # Cross currency strategy
        print("   ⚡ Cross Currency Strategy...")
        cross_result = await self._execute_single_strategy(HedgeType.CROSS_CURRENCY, ForexPair.EURJPY)
        strategy_results["cross_currency"] = cross_result
        
        print(f"   ✅ {len(strategy_results)} ta strategiya bajarildi")
        
        self.demo_results["strategy_execution"] = strategy_results
    
    async def _execute_single_strategy(self, hedge_type: HedgeType, pair: ForexPair) -> Dict:
        """Bitta strategiya bajarish"""
        
        try:
            # Create hedge strategy
            metadata, position = await self.framework.hedge_manager.create_hedge_strategy(
                hedge_type=hedge_type,
                pair=pair,
                notional_amount=150000,
                quantum_enhanced=True
            )
            
            result = {
                "success": True,
                "position_id": position.position_id,
                "nft_token_id": metadata.token_id,
                "hedge_ratio": position.hedge_ratio,
                "notional_amount": position.notional_amount,
                "quantum_enhanced": position.quantum_enhanced
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _demo_quantum_optimization(self):
        """Quantum optimization demo"""
        
        print("   🔮 Quantum optimization boshlanmoqda...")
        
        # Create demo positions for optimization
        demo_positions = await self.framework.quantum_optimizer.currency_arbitrage._classical_arbitrage_analysis()
        
        # Run quantum arbitrage optimization
        arbitrage_result = await self.framework.quantum_optimizer.currency_arbitrage.optimize_arbitrage_opportunities()
        
        # Run multi-currency portfolio optimization
        portfolio_result = await self.framework.quantum_optimizer.multi_currency.optimize_multi_currency_portfolio()
        
        # Run volatility modeling
        volatility_result = await self.framework.quantum_optimizer.volatility_modeling.quantum_volatility_modeling()
        
        quantum_results = {
            "arbitrage_optimization": arbitrage_result,
            "portfolio_optimization": portfolio_result,
            "volatility_modeling": volatility_result,
            "quantum_advantage_summary": arbitrage_result.get("quantum_advantage_summary", {})
        }
        
        print(f"   ✅ Quantum optimization yakunlandi")
        print(f"   📈 Quantum advantage: {quantum_results['quantum_advantage_summary']}")
        
        self.demo_results["quantum_optimization"] = quantum_results
    
    async def _demo_integration_features(self):
        """Integration features demo"""
        
        print("   🔗 Integration framework namoyishi...")
        
        # System status
        system_status = await self.framework.get_system_status()
        print(f"   📊 System status: {system_status['system_status']}")
        
        # Comprehensive market analysis
        market_analysis = await self.framework._comprehensive_market_analysis()
        print(f"   🌍 Market assessment: {market_analysis['overall_assessment']}")
        
        # NFT portfolio management
        nft_results = await self.framework._manage_nft_portfolio()
        print(f"   🎨 NFT management: {nft_results['active_nft_count']} active NFTs")
        
        # Risk management
        risk_results = await self.framework._execute_risk_management()
        print(f"   🛡️  Risk management: {len(risk_results['risk_actions'])} actions")
        
        integration_results = {
            "system_status": system_status,
            "market_analysis": market_analysis,
            "nft_results": nft_results,
            "risk_results": risk_results
        }
        
        self.demo_results["integration"] = integration_results
    
    async def _demo_performance_monitoring(self):
        """Performance monitoring demo"""
        
        print("   📈 Performance monitoring yoqildi...")
        
        # Initialize performance monitor
        monitor = PerformanceMonitor(self.framework)
        
        # Run immediate monitoring cycle
        metrics = await self.framework._collect_system_metrics()
        print(f"   📊 System metrics:")
        print(f"      Total PnL: ${metrics.total_pnl:,.2f}")
        print(f"      Active Positions: {metrics.active_positions}")
        print(f"      Active NFTs: {metrics.active_nfts}")
        print(f"      Quantum Advantage: {metrics.quantum_advantage:.2%}")
        print(f"      Hedge Effectiveness: {metrics.hedge_effectiveness:.2%}")
        print(f"      Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        print(f"      Max Drawdown: {metrics.max_drawdown:.2%}")
        print(f"      VaR (95%): {metrics.var_95:.2%}")
        
        # Performance attribution
        attribution = await self.framework._calculate_performance_attribution(self.demo_results.get("strategy_execution", {}))
        print(f"   🎯 Performance attribution:")
        print(f"      Total Performance: ${attribution.total_performance:,.2f}")
        print(f"      Quantum Contribution: ${attribution.quantum_classical_breakdown['quantum_contribution']:,.2f}")
        print(f"      Classical Contribution: ${attribution.quantum_classical_breakdown['classical_contribution']:,.2f}")
        
        monitoring_results = {
            "metrics": {
                "total_pnl": metrics.total_pnl,
                "active_positions": metrics.active_positions,
                "active_nfts": metrics.active_nfts,
                "quantum_advantage": metrics.quantum_advantage,
                "hedge_effectiveness": metrics.hedge_effectiveness,
                "sharpe_ratio": metrics.sharpe_ratio,
                "max_drawdown": metrics.max_drawdown,
                "var_95": metrics.var_95
            },
            "attribution": {
                "total_performance": attribution.total_performance,
                "quantum_contribution": attribution.quantum_classical_breakdown["quantum_contribution"],
                "classical_contribution": attribution.quantum_classical_breakdown["classical_contribution"]
            }
        }
        
        self.demo_results["performance_monitoring"] = monitoring_results
    
    async def _demo_system_health(self):
        """System health demo"""
        
        print("   💚 System health check...")
        
        health_monitor = SystemHealthMonitor(self.framework)
        health_results = await health_monitor.run_health_checks()
        
        print(f"   🌡️  Overall health: {health_results['overall_health']}")
        print(f"   🔧 Component health:")
        for component, status in health_results['component_health'].items():
            print(f"      {component}: {status}")
        
        if health_results['alerts']:
            print(f"   ⚠️  Alerts:")
            for alert in health_results['alerts']:
                print(f"      {alert}")
        else:
            print(f"   ✅ No alerts detected")
        
        self.demo_results["system_health"] = health_results
    
    async def _demo_comprehensive_execution(self):
        """Comprehensive execution demo"""
        
        print("   🎯 Comprehensive strategy execution...")
        
        # Execute the full integrated strategy
        comprehensive_results = await self.framework.execute_comprehensive_strategy()
        
        print(f"   ✅ Comprehensive execution completed")
        print(f"   📊 Execution summary:")
        print(f"      Status: {comprehensive_results['execution_summary']['status']}")
        print(f"      Execution time: {comprehensive_results['execution_summary']['execution_time']:.2f}s")
        print(f"      Market conditions: {comprehensive_results['execution_summary']['market_conditions']}")
        
        # Show key results
        if 'performance_attribution' in comprehensive_results:
            attribution = comprehensive_results['performance_attribution']
            print(f"   💰 Performance breakdown:")
            print(f"      Total performance: ${attribution.total_performance:,.2f}")
            print(f"      Strategy contributions: {attribution.strategy_contributions}")
        
        self.demo_results["comprehensive_execution"] = comprehensive_results
    
    async def _display_demo_summary(self, demo_duration: float):
        """Demo natijalarini ko'rsatish"""
        
        print("\n" + "=" * 80)
        print("📊 DEMO NATIJALARI")
        print("=" * 80)
        
        print(f"\n⏱️  Demo davomiyligi: {demo_duration:.2f} soniya")
        
        # System initialization
        init_result = self.demo_results.get("initialization", {})
        print(f"🚀 Tizim inicializatsiya: {'✅' if init_result.get('status') == 'initialized' else '❌'}")
        
        # Market data
        market_data = self.demo_results.get("market_data", {})
        print(f"📊 Bozor ma'lumotlari: {len(market_data)} juftlik")
        
        # NFT creation
        nft_data = self.demo_results.get("nft_management", {})
        print(f"🎨 NFT yaratish: {nft_data.get('total_created', 0)} ta NFT")
        
        # Strategy execution
        strategy_data = self.demo_results.get("strategy_execution", {})
        successful_strategies = len([s for s in strategy_data.values() if s.get("success")])
        print(f"⚡ Strategiya bajarish: {successful_strategies}/{len(strategy_data)} muvaffaqiyatli")
        
        # Quantum optimization
        quantum_data = self.demo_results.get("quantum_optimization", {})
        quantum_advantage = quantum_data.get("quantum_advantage_summary", {})
        print(f"🔮 Quantum advantage: {quantum_advantage}")
        
        # Performance metrics
        perf_data = self.demo_results.get("performance_monitoring", {})
        metrics = perf_data.get("metrics", {})
        print(f"📈 Performance metrics:")
        print(f"   💰 Total PnL: ${metrics.get('total_pnl', 0):,.2f}")
        print(f"   🎯 Active Positions: {metrics.get('active_positions', 0)}")
        print(f"   🎨 Active NFTs: {metrics.get('active_nfts', 0)}")
        print(f"   ⚡ Quantum Advantage: {metrics.get('quantum_advantage', 0):.2%}")
        print(f"   🛡️  Hedge Effectiveness: {metrics.get('hedge_effectiveness', 0):.2%}")
        print(f"   📊 Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        
        # System health
        health_data = self.demo_results.get("system_health", {})
        print(f"💚 Tizim sog'lig'i: {health_data.get('overall_health', 'unknown')}")
        
        # Comprehensive execution
        comp_data = self.demo_results.get("comprehensive_execution", {})
        comp_status = comp_data.get("execution_summary", {}).get("status", "unknown")
        print(f"🎯 Comprehensive execution: {comp_status}")
        
        # Summary statistics
        total_features = 9  # Number of demo sections
        successful_features = sum([
            init_result.get("status") == "initialized",
            len(market_data) > 0,
            nft_data.get("total_created", 0) > 0,
            successful_strategies > 0,
            bool(quantum_data),
            bool(perf_data),
            health_data.get("overall_health") != "unhealthy",
            comp_status == "success"
        ])
        
        success_rate = (successful_features / total_features) * 100
        print(f"\n📊 Umumiy muvaffaqiyat: {successful_features}/{total_features} ({success_rate:.1f}%)")
        
        # Key achievements
        print(f"\n🏆 Asosiy yutuqlar:")
        print(f"   ✅ {len(market_data)} ta valyuta juftlik uchun bozor ma'lumotlari")
        print(f"   ✅ {nft_data.get('total_created', 0)} ta quantum-enhanced NFT yaratildi")
        print(f"   ✅ {successful_strategies} ta hedge strategiyasi bajarildi")
        print(f"   ✅ Quantum optimallash aktivlashtirildi")
        print(f"   ✅ Performance monitoring yoqildi")
        print(f"   ✅ Tizim integratsiyasi amalga oshirildi")
        
        # Technical specifications
        print(f"\n🔧 Texnik xususiyatlar:")
        print(f"   🔮 Quantum qubits: 16 (simulated)")
        print(f"   🧮 Classical mix ratio: 30%")
        print(f"   ⚡ Max iterations: 1000")
        print(f"   📊 Real-time monitoring: enabled")
        print(f"   🎨 NFT tokenization: enabled")
        print(f"   🔗 Multi-asset integration: enabled")

async def main():
    """Asosiy demo funksiyasi"""
    
    print("Forex NFT Hedging va Quantum Portfolio Optimization")
    print("=" * 60)
    print("Demo tizimni barcha funksiyalarini namoyish etadi")
    print("=" * 60)
    
    try:
        # Demo yaratish va ishga tushirish
        demo = ForexNHTHedgingDemo()
        results = await demo.run_comprehensive_demo()
        
        # Natijalarni saqlash
        with open('/workspace/code/forex_nft_hedges/demo/demo_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Demo natijalari saqlandi: demo_results.json")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Demo xatosi: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(main())