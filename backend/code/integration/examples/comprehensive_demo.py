"""
Module Integration Demo
======================

Barcha integration komponentlarini ko'rsatuvchi comprehensive demo.
"""

import asyncio
import logging
import numpy as np
import time
from typing import Dict, List, Any

# Integration imports
from integration import (
    IntegrationManager, ModuleInfo, ModuleStatus,
    ModelIntegration, SignalAggregator, PerformanceTracker,
    QuantumIntegration, QuantumAlgorithm, HybridMode,
    BlockchainIntegration, BlockchainType, NetworkType,
    SystemIntegration
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModuleIntegrationDemo:
    """Comprehensive Module Integration Demo"""
    
    def __init__(self):
        self.integration_manager = IntegrationManager()
        self.model_integration = ModelIntegration()
        self.signal_aggregator = SignalAggregator()
        self.performance_tracker = PerformanceTracker()
        self.quantum_integration = QuantumIntegration()
        self.blockchain_integration = BlockchainIntegration()
        self.system_integration = SystemIntegration()
        
        self.demo_results = {}
    
    async def initialize_all_components(self):
        """Barcha komponentlarni ishga tushirish"""
        logger.info("🚀 Module Integration Demo boshlanmoqda...")
        
        # Initialize core integration manager
        integration_ok = await self.integration_manager.initialize()
        logger.info(f"✅ Integration Manager: {'OK' if integration_ok else 'ERROR'}")
        
        # Initialize AI trading components
        model_ok = await self.model_integration.initialize()
        signal_ok = await self.signal_aggregator.initialize()
        performance_ok = await self.performance_tracker.initialize()
        logger.info(f"🤖 AI Trading: Model={model_ok}, Signal={signal_ok}, Performance={performance_ok}")
        
        # Initialize quantum integration
        quantum_ok = await self.quantum_integration.initialize()
        logger.info(f"⚛️  Quantum Integration: {'OK' if quantum_ok else 'ERROR'}")
        
        # Initialize blockchain integration
        blockchain_ok = await self.blockchain_integration.initialize()
        logger.info(f"⛓️  Blockchain Integration: {'OK' if blockchain_ok else 'ERROR'}")
        
        # Initialize system integration
        system_ok = await self.system_integration.initialize()
        logger.info(f"🔧 System Integration: {'OK' if system_ok else 'ERROR'}")
        
        return all([integration_ok, model_ok, signal_ok, performance_ok, 
                   quantum_ok, blockchain_ok, system_ok])
    
    async def register_demo_modules(self):
        """Demo modullarni ro'yxatga olish"""
        logger.info("📋 Demo modullar ro'yxatga olinmoqda...")
        
        # AI Trading Module
        ai_trading_module = ModuleInfo(
            name="ai_trading_module",
            version="1.0.0",
            module_type="ai_trading",
            capabilities=["signal_generation", "model_prediction", "performance_tracking"],
            dependencies=[],
            config={"models": ["dqn", "ppo", "a2c"], "update_frequency": 3600}
        )
        
        # Quantum Module
        quantum_module = ModuleInfo(
            name="quantum_module",
            version="1.0.0", 
            module_type="quantum_computing",
            capabilities=["quantum_optimization", "hybrid_computation", "quantum_advantage"],
            dependencies=[],
            config={"algorithms": ["vqe", "qaoa"], "qubits": 4, "shots": 1024}
        )
        
        # Blockchain Module
        blockchain_module = ModuleInfo(
            name="blockchain_module",
            version="1.0.0",
            module_type="blockchain",
            capabilities=["smart_contracts", "defi_operations", "cross_chain"],
            dependencies=[],
            config={"networks": ["ethereum", "bsc", "polygon"], "gas_optimization": True}
        )
        
        # System Module
        system_module = ModuleInfo(
            name="system_module", 
            version="1.0.0",
            module_type="system_integration",
            capabilities=["data_pipeline", "microservices", "event_streaming"],
            dependencies=[],
            config={"pipelines": ["trading_data", "risk_management"], "streaming_enabled": True}
        )
        
        # Register all modules
        modules = [ai_trading_module, quantum_module, blockchain_module, system_module]
        
        for module in modules:
            success = self.integration_manager.register_module(module)
            logger.info(f"📝 {module.name}: {'REGISTERED' if success else 'FAILED'}")
        
        return True
    
    async def demonstrate_ai_trading_integration(self):
        """AI Trading integration demonstratsiyasi"""
        logger.info("🤖 AI Trading Integration demo...")
        
        # Model predictions yaratish
        test_state = np.random.random(10)
        
        predictions = []
        model_names = ["dqn_default", "ppo_default", "a2c_default"]
        
        for model_name in model_names:
            try:
                prediction = await self.model_integration.predict(model_name, test_state)
                if prediction:
                    predictions.append(prediction)
                    logger.info(f"✅ {model_name}: Signal={prediction.prediction.get('signal_type', 'N/A')}, "
                              f"Confidence={prediction.confidence:.3f}")
            except Exception as e:
                logger.error(f"❌ {model_name}: {e}")
        
        # Signals aggregation
        if predictions:
            aggregated_result = await self.signal_aggregator.aggregate_signals(
                symbol="BTCUSD",
                model_predictions=predictions
            )
            
            if aggregated_result:
                logger.info(f"🎯 Ensemble Result: {aggregated_result.final_signal.name}, "
                          f"Confidence={aggregated_result.confidence:.3f}")
                
                # Performance tracking
                for prediction in predictions:
                    await self.performance_tracker.track_prediction(
                        prediction.model_name,
                        prediction,
                        actual_outcome={"confidence": aggregated_result.confidence}
                    )
                
                self.demo_results['ai_trading'] = {
                    'predictions': len(predictions),
                    'ensemble_signal': aggregated_result.final_signal.name,
                    'ensemble_confidence': aggregated_result.confidence,
                    'consensus_score': aggregated_result.consensus_score
                }
        
        return True
    
    async def demonstrate_quantum_integration(self):
        """Quantum integration demonstratsiyasi"""
        logger.info("⚛️  Quantum Integration demo...")
        
        # Problem data preparation
        problem_data = {
            'problem_matrix': np.random.random((16, 16)),
            'quantum_params': {'shots': 1024, 'optimization_iterations': 10},
            'max_iterations': 5,
            'convergence_threshold': 1e-6
        }
        
        # Hybrid computation run
        try:
            result = await self.quantum_integration.run_hybrid_computation(
                problem_data=problem_data,
                hybrid_mode=HybridMode.ITERATIVE
            )
            
            if result and 'error' not in result:
                logger.info(f"🔬 Quantum Computation: Mode={result.get('computation_mode', 'N/A')}")
                if 'quantum_result' in result:
                    quantum_res = result['quantum_result']
                    logger.info(f"📊 Quantum Result: {type(quantum_res)} data received")
                
                if 'hybrid_advantage' in result:
                    advantage = result['hybrid_advantage']
                    logger.info(f"🚀 Quantum Advantage: {advantage:.3f}")
                
                self.demo_results['quantum'] = {
                    'computation_mode': result.get('computation_mode', 'unknown'),
                    'hybrid_advantage': result.get('hybrid_advantage', 0.0),
                    'success': True
                }
            else:
                logger.error(f"❌ Quantum Computation Failed: {result.get('error', 'Unknown error')}")
                self.demo_results['quantum'] = {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            logger.error(f"❌ Quantum Integration Error: {e}")
            self.demo_results['quantum'] = {'success': False, 'error': str(e)}
        
        return True
    
    async def demonstrate_blockchain_integration(self):
        """Blockchain integration demonstratsiyasi"""
        logger.info("⛓️  Blockchain Integration demo...")
        
        # Demo wallet yaratish
        try:
            wallet_address = await self.blockchain_integration.create_wallet(
                blockchain=BlockchainType.ETHEREUM,
                network=NetworkType.MAINNET
            )
            
            if wallet_address:
                logger.info(f"👛 Wallet Created: {wallet_address}")
                
                # Balance check
                balance = await self.blockchain_integration.get_balance(wallet_address)
                logger.info(f"💰 Balance Check: {balance}")
                
                # Transaction simulation
                tx_hash = await self.blockchain_integration.send_transaction(
                    from_address=wallet_address,
                    to_address="0x1234567890123456789012345678901234567890",
                    value=0.1
                )
                
                if tx_hash:
                    logger.info(f"📤 Transaction Sent: {tx_hash}")
                    
                    # Transaction status check
                    await asyncio.sleep(1)  # Simulate processing time
                    tx_status = await self.blockchain_integration.get_transaction_status(tx_hash)
                    if tx_status:
                        logger.info(f"📊 Transaction Status: {tx_status.get('status', 'Unknown')}")
                
                # DeFi operations demo
                swap_operation = await self.blockchain_integration.swap_tokens(
                    token_in="ETH",
                    token_out="USDC", 
                    amount_in=0.1,
                    slippage=0.5
                )
                
                if swap_operation:
                    logger.info(f"💱 Token Swap: {swap_operation.amount_in} ETH -> {swap_operation.amount_out} USDC")
                
                self.demo_results['blockchain'] = {
                    'wallet_address': wallet_address,
                    'balance': balance,
                    'transaction_sent': tx_hash is not None,
                    'defi_operation': swap_operation is not None
                }
        
        except Exception as e:
            logger.error(f"❌ Blockchain Integration Error: {e}")
            self.demo_results['blockchain'] = {'success': False, 'error': str(e)}
        
        return True
    
    async def demonstrate_system_integration(self):
        """System integration demonstratsiyasi"""
        logger.info("🔧 System Integration demo...")
        
        try:
            # Get integration status
            integration_status = await self.system_integration.get_integration_status()
            logger.info(f"📊 System Status: {integration_status.get('overall_health', 'Unknown')}")
            
            # Publish integration message
            publish_success = await self.system_integration.publish_integration_message(
                topic="trading.signals",
                data={
                    "signal": "BUY",
                    "confidence": 0.85,
                    "source": "integration_demo"
                },
                source="demo_module"
            )
            
            if publish_success:
                logger.info("📨 Integration message published successfully")
            
            # Get comprehensive stats
            stats = self.system_integration.get_comprehensive_stats()
            logger.info(f"📈 System Stats: {len(stats)} component groups")
            
            self.demo_results['system'] = {
                'overall_health': integration_status.get('overall_health', 'unknown'),
                'message_published': publish_success,
                'components_count': stats.get('system_integration', {}).get('components_count', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ System Integration Error: {e}")
            self.demo_results['system'] = {'success': False, 'error': str(e)}
        
        return True
    
    async def demonstrate_cross_module_communication(self):
        """Cross-module communication demonstratsiyasi"""
        logger.info("🔄 Cross-Module Communication demo...")
        
        try:
            # AI Trading dan Quantum ga signal yuborish
            signal_data = {
                "signal": "BUY",
                "confidence": 0.82,
                "symbol": "BTCUSD",
                "timestamp": time.time()
            }
            
            # Broadcast xabar
            broadcast_success = await self.integration_manager.broadcast_message(
                source_module="ai_trading_module",
                message_type="trading_signal",
                data=signal_data,
                target_capability="quantum_optimization"
            )
            
            if broadcast_success:
                logger.info("📡 Trading signal broadcast qilindi")
            
            # Module status check
            modules_status = self.integration_manager.list_modules()
            healthy_modules = self.integration_manager.get_healthy_modules()
            
            logger.info(f"📋 Module Status: {len(modules_status)} registered, "
                       f"{len(healthy_modules)} healthy")
            
            self.demo_results['communication'] = {
                'broadcast_success': broadcast_success,
                'total_modules': len(modules_status),
                'healthy_modules': len(healthy_modules)
            }
            
        except Exception as e:
            logger.error(f"❌ Cross-Module Communication Error: {e}")
            self.demo_results['communication'] = {'success': False, 'error': str(e)}
        
        return True
    
    async def run_comprehensive_demo(self):
        """Comprehensive demo run"""
        logger.info("🚀 Comprehensive Module Integration Demo boshlanmoqda...")
        
        start_time = time.time()
        
        try:
            # Step 1: Initialize all components
            init_success = await self.initialize_all_components()
            if not init_success:
                logger.error("❌ Component initialization failed")
                return False
            
            # Step 2: Register demo modules
            await self.register_demo_modules()
            
            # Step 3: Demonstrate each integration
            await self.demonstrate_ai_trading_integration()
            await self.demonstrate_quantum_integration()  
            await self.demonstrate_blockchain_integration()
            await self.demonstrate_system_integration()
            await self.demonstrate_cross_module_communication()
            
            # Step 4: Generate final report
            execution_time = time.time() - start_time
            await self.generate_demo_report(execution_time)
            
            logger.info("✅ Comprehensive Demo muvaffaqiyatli tugallandi!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo execution error: {e}")
            return False
    
    async def generate_demo_report(self, execution_time: float):
        """Demo report yaratish"""
        logger.info("📊 Demo report tayyorlanmoqda...")
        
        # Overall statistics
        total_components = 7  # integration_manager + 6 major components
        successful_components = sum(
            1 for result in self.demo_results.values() 
            if result.get('success', True)  # Default to True if not specified
        )
        
        # Performance metrics
        performance_metrics = {
            'total_execution_time': execution_time,
            'components_success_rate': successful_components / total_components * 100,
            'integration_success': len(self.demo_results) > 0
        }
        
        # Component-specific results
        component_results = {}
        for component, result in self.demo_results.items():
            component_results[component] = {
                'success': result.get('success', True),
                'metrics': result
            }
        
        # Final report
        report = {
            'demo_summary': {
                'execution_time': execution_time,
                'total_components': total_components,
                'successful_components': successful_components,
                'success_rate': f"{successful_components / total_components * 100:.1f}%"
            },
            'performance_metrics': performance_metrics,
            'component_results': component_results,
            'recommendations': self.generate_recommendations(),
            'timestamp': time.time()
        }
        
        # Save report
        import json
        with open('/workspace/code/integration/demo_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        logger.info("📈 DEMO SUMMARY:")
        logger.info(f"   ⏱️  Execution Time: {execution_time:.2f} seconds")
        logger.info(f"   ✅ Success Rate: {successful_components}/{total_components} ({successful_components / total_components * 100:.1f}%)")
        logger.info(f"   🏥 Overall Health: {report['performance_metrics']['integration_success']}")
        
        for component, result in component_results.items():
            status = "✅" if result['success'] else "❌"
            logger.info(f"   {status} {component.replace('_', ' ').title()}")
        
        logger.info(f"📄 Full report saved to: demo_report.json")
    
    def generate_recommendations(self) -> List[str]:
        """Recommendations yaratish"""
        recommendations = []
        
        # AI Trading recommendations
        if 'ai_trading' in self.demo_results:
            result = self.demo_results['ai_trading']
            if result.get('ensemble_confidence', 0) > 0.7:
                recommendations.append("AI Trading models showing good consensus - ready for production")
            else:
                recommendations.append("Consider retraining AI models to improve prediction confidence")
        
        # Quantum recommendations
        if 'quantum' in self.demo_results:
            result = self.demo_results['quantum']
            if result.get('hybrid_advantage', 0) > 0.1:
                recommendations.append("Quantum integration showing promising results - consider expanding")
            else:
                recommendations.append("Optimize quantum algorithms for better quantum advantage")
        
        # Blockchain recommendations
        if 'blockchain' in self.demo_results:
            result = self.demo_results['blockchain']
            if result.get('defi_operation'):
                recommendations.append("DeFi operations working - can integrate more protocols")
            else:
                recommendations.append("Review DeFi integration and gas optimization settings")
        
        # System recommendations
        if 'system' in self.demo_results:
            result = self.demo_results['system']
            health = result.get('overall_health', 'unknown')
            if health in ['excellent', 'good']:
                recommendations.append("System integration health is good - ready for scaling")
            else:
                recommendations.append("Monitor system integration health and optimize performance")
        
        return recommendations

async def main():
    """Main demo function"""
    demo = ModuleIntegrationDemo()
    
    try:
        success = await demo.run_comprehensive_demo()
        
        if success:
            print("\n🎉 Module Integration Demo muvaffaqiyatli yakunlandi!")
            print("📁 Natijalarni ko'rish uchun demo_report.json faylini oching.")
        else:
            print("\n❌ Demo da xatolik yuz berdi.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Demo to'xtatildi.")
    except Exception as e:
        print(f"\n💥 Demo critical xatosi: {e}")

if __name__ == "__main__":
    asyncio.run(main())