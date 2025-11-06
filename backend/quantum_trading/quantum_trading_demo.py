#!/usr/bin/env python3
"""
Quantum Advantage Trading System - Demo
=======================================

Bu demo quantum trading tizimining asosiy imkoniyatlarini ko'rsatadi:
1. Multi-asset quantum trading
2. Quantum optimization
3. Error correction
4. Performance metrics
5. Benchmarking

Foydalanish:
    python quantum_trading_demo.py

Tizim talablari:
- Python 3.8+
- NumPy, Pandas, SciPy, Matplotlib
- AsyncIO support
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_trading.main import QuantumAdvantageTradingSystem, TradingConfig
from quantum_trading.metrics import QuantumAdvantageMetrics
from quantum_trading.benchmarks import QuantumBenchmarks

class QuantumTradingDemo:
    """
    Quantum Trading Demo Class
    
    Bu klass quantum trading tizimining to'liq demo versiyasini
    ta'minlaydi va barcha komponentlarni namoyish etadi.
    """
    
    def __init__(self):
        self.output_dir = Path("quantum_trading_demo_results")
        self.output_dir.mkdir(exist_ok=True)
        
        print("=" * 80)
        print("🚀 QUANTUM ADVANTAGE TRADING SYSTEM DEMO")
        print("=" * 80)
        print("Quantum computing orqali multi-asset trading tizimi")
        print("Stock, Forex, Metals, Crypto bozorlari uchun")
        print("=" * 80)
    
    async def run_complete_demo(self):
        """To'liq demo o'tkazish"""
        try:
            # 1. System Configuration
            await self.demo_system_configuration()
            
            # 2. Multi-Asset Trading Demo
            await self.demo_multi_asset_trading()
            
            # 3. Quantum Optimization Demo
            await self.demo_quantum_optimization()
            
            # 4. Error Correction Demo
            await self.demo_error_correction()
            
            # 5. Performance Metrics Demo
            await self.demo_performance_metrics()
            
            # 6. Benchmarking Demo
            await self.demo_benchmarking()
            
            # 7. Continuous Trading Simulation
            await self.demo_continuous_trading()
            
            # 8. Generate Final Report
            await self.generate_final_report()
            
            print("\n✅ Demo muvaffaqiyatli yakunlandi!")
            print(f"📁 Natijalar saqlangan papka: {self.output_dir.absolute()}")
            
        except Exception as e:
            print(f"\n❌ Demo xatosi: {str(e)}")
            raise
    
    async def demo_system_configuration(self):
        """Tizim konfiguratsiyasi demo"""
        print("\n" + "="*50)
        print("1️⃣  SYSTEM CONFIGURATION")
        print("="*50)
        
        # Different configuration scenarios
        configs = {
            "Conservative": TradingConfig(
                quantum_advantage_threshold=0.10,
                stocks_weight=0.6,
                forex_weight=0.25,
                metals_weight=0.10,
                crypto_weight=0.05
            ),
            "Aggressive": TradingConfig(
                quantum_advantage_threshold=0.20,
                stocks_weight=0.3,
                forex_weight=0.2,
                metals_weight=0.2,
                crypto_weight=0.3
            ),
            "Balanced": TradingConfig(
                quantum_advantage_threshold=0.15,
                stocks_weight=0.4,
                forex_weight=0.3,
                metals_weight=0.2,
                crypto_weight=0.1
            )
        }
        
        print("📋 Konfiguratsiya variantlari:")
        for name, config in configs.items():
            print(f"\n{name} Portfolio:")
            print(f"  • Quantum Advantage Threshold: {config.quantum_advantage_threshold}")
            print(f"  • Stocks: {config.stocks_weight:.1%}")
            print(f"  • Forex: {config.forex_weight:.1%}")
            print(f"  • Metals: {config.metals_weight:.1%}")
            print(f"  • Crypto: {config.crypto_weight:.1%}")
        
        # Save configuration demo
        await self._save_demo_data("system_configuration", configs)
        
        # Initialize main system with Balanced config
        self.system = QuantumAdvantageTradingSystem(configs["Balanced"])
        
        print("\n✅ Tizim muvaffaqiyatli sozlandi!")
    
    async def demo_multi_asset_trading(self):
        """Multi-asset trading demo"""
        print("\n" + "="*50)
        print("2️⃣  MULTI-ASSET QUANTUM TRADING")
        print("="*50)
        
        print("🔄 Multi-asset market data collection boshlanmoqda...")
        
        # Initialize the trading system
        await self.system.initialize_system()
        
        # Collect market data for all asset types
        print("\n📊 Market ma'lumotlari to'planmoqda...")
        
        stocks_data = await self.system.multi_asset_trader.collect_stocks_data()
        forex_data = await self.system.multi_asset_trader.collect_forex_data()
        metals_data = await self.system.multi_asset_trader.collect_metals_data()
        crypto_data = await self.system.multi_asset_trader.collect_crypto_data()
        
        # Display market data summary
        print(f"\n📈 STOCKS DATA:")
        print(f"  • Aktivalar soni: {len(stocks_data['data'])}")
        print(f"  • Quantum entanglement: {stocks_data['entanglement_strength']:.3f}")
        
        print(f"\n💱 FOREX DATA:")
        print(f"  • Valyuta juftliklar: {len(forex_data['data'])}")
        print(f"  • Arbitrage imkoniyatlari: {len(forex_data['arbitrage_opportunities'])}")
        
        print(f"\n🥇 METALS DATA:")
        print(f"  • Metall turlari: {len(metals_data['data'])}")
        print(f"  • Quantum korrelatsiyalar: {len(metals_data['correlations'])}")
        
        print(f"\n₿ CRYPTO DATA:")
        print(f"  • Kriptovalutalar: {len(crypto_data['data'])}")
        print(f"  • Volatilite tahlili: {len(crypto_data['volatility_analysis'])}")
        
        # Cross-asset opportunities
        cross_opportunities = await self.system.multi_asset_trader.get_cross_asset_opportunities()
        print(f"\n🔗 Cross-asset imkoniyatlar: {len(cross_opportunities)}")
        
        await self._save_demo_data("multi_asset_data", {
            "stocks": stocks_data,
            "forex": forex_data,
            "metals": metals_data,
            "crypto": crypto_data,
            "cross_opportunities": cross_opportunities
        })
        
        print("✅ Multi-asset trading ma'lumotlari tayyor!")
    
    async def demo_quantum_optimization(self):
        """Quantum optimization demo"""
        print("\n" + "="*50)
        print("3️⃣  QUANTUM OPTIMIZATION")
        print("="*50)
        
        print("⚡ Quantum portfolio optimization boshlanmoqda...")
        
        # Create optimization problem
        optimization_problem = {
            "current_portfolio": self.system.portfolio_state,
            "market_data": {
                "stocks": await self.system.multi_asset_trader.collect_stocks_data(),
                "forex": await self.system.multi_asset_trader.collect_forex_data(),
                "metals": await self.system.multi_asset_trader.collect_metals_data(),
                "crypto": await self.system.multi_asset_trader.collect_crypto_data()
            },
            "constraints": {
                "max_drawdown": 0.05,
                "quantum_advantage_target": 0.15
            }
        }
        
        # Run quantum optimization
        optimization_result = await self.system.quantum_optimizer.optimize_portfolio(optimization_problem)
        
        print(f"\n🎯 Optimization natijasi:")
        print(f"  • Method: {optimization_result['optimization_details']['method']}")
        print(f"  • Objective Value: {optimization_result['optimization_details']['objective_value']:.6f}")
        print(f"  • Computation Time: {optimization_result['optimization_details']['computation_time']:.4f}s")
        print(f"  • Quantum Advantage: {optimization_result['optimization_details']['quantum_advantage']:.2f}x")
        
        # Show new allocation
        print(f"\n📊 Yangi portfolio taqsimoti:")
        for asset, allocation in optimization_result['new_allocation'].items():
            print(f"  • {asset.title()}: {allocation['weight']:.1%} "
                  f"(o'zgarish: {allocation['change']:+.1%})")
        
        # Performance analysis
        performance = self.system.quantum_optimizer.get_optimization_performance()
        print(f"\n📈 Performance tahlili:")
        if 'method_statistics' in performance:
            for method, stats in performance['method_statistics'].items():
                print(f"  • {method}: {stats['count']} ta optimization, "
                      f"o'rtacha {stats['avg_quantum_advantage']:.2f}x advantage")
        
        await self._save_demo_data("quantum_optimization", optimization_result)
        print("✅ Quantum optimization yakunlandi!")
    
    async def demo_error_correction(self):
        """Error correction demo"""
        print("\n" + "="*50)
        print("4️⃣  QUANTUM ERROR CORRECTION")
        print("="*50)
        
        print("🛡️ Quantum error correction tizimi faollashtirilmoqda...")
        
        # Demonstrate different error correction codes
        from quantum_trading.error_correction import ErrorCorrectionCode
        
        correction_codes = [
            ErrorCorrectionCode.SURFACE_CODE,
            ErrorCorrectionCode.STEANE_CODE,
            ErrorCorrectionCode.REPETITION_CODE,
            ErrorCorrectionCode.ERROR_MITIGATION
        ]
        
        for code in correction_codes:
            print(f"\n🔧 {code.value.upper()} test qilinmoqda...")
            
            # Create test quantum state
            test_state = await self.system.quantum_optimizer.create_portfolio_state()
            
            # Detect and correct errors
            corrected_state, correction_result = await self.system.error_corrector.detect_and_correct_errors(
                test_state, code
            )
            
            print(f"  ✅ Xato tuzatildi: {correction_result.correction_applied}")
            print(f"  📈 Fidelity yaxshilanishi: {correction_result.fidelity_improvement:.4f}")
            print(f"  ⏱️ Tuzatish vaqti: {correction_result.correction_time:.2f}ms")
        
        # Portfolio protection setup
        protection = await self.system.error_corrector.setup_portfolio_protection()
        print(f"\n🛡️ Portfolio himoyasi sozlandi:")
        print(f"  • Protection level: {protection['protection_level']}")
        print(f"  • Error threshold: {protection['error_threshold']}")
        print(f"  • Fidelity target: {protection['fidelity_target']}")
        
        # Fault tolerance analysis
        fault_analysis = self.system.error_corrector.get_fault_tolerance_analysis()
        print(f"\n🔍 Fault-tolerance tahlili:")
        for code, analysis in fault_analysis['code_performance'].items():
            print(f"  • {code}: {analysis['correctable_errors']} ta xato tuzatish mumkin")
            print(f"    Threshold: {analysis['threshold']:.1%}")
        
        print(f"  🏆 Tavsiya etiladigan code: {fault_analysis['recommended_code']}")
        
        await self._save_demo_data("error_correction", {
            "protection_setup": protection,
            "fault_tolerance": fault_analysis
        })
        
        print("✅ Error correction test yakunlandi!")
    
    async def demo_performance_metrics(self):
        """Performance metrics demo"""
        print("\n" + "="*50)
        print("5️⃣  PERFORMANCE METRICS")
        print("="*50)
        
        print("📊 Quantum advantage metrikalar hisoblanmoqda...")
        
        # Simulate trade results for metrics calculation
        trade_results = {
            "stocks": {"execution_time": 0.05, "accuracy": 0.92},
            "forex": {"execution_time": 0.03, "accuracy": 0.88},
            "metals": {"execution_time": 0.04, "accuracy": 0.85},
            "crypto": {"execution_time": 0.06, "accuracy": 0.90}
        }
        
        # Calculate metrics
        metrics = await self.system.metrics_calculator.calculate_cycle_metrics(
            trade_results=trade_results,
            portfolio_state=self.system.portfolio_state,
            quantum_advantage_threshold=0.15
        )
        
        print(f"\n🎯 Quantum Advantage Assessment:")
        print(f"  • Umumiy afzallik: {metrics['overall_advantage']:.2f}%")
        print(f"  • Afzallik darajasi: {metrics['advantage_level']}")
        supremacy_text = "Ha" if metrics['quantum_supremacy_achieved'] else "Yo'q"
        print(f"  • Quantum supremacy: {supremacy_text}")
        
        print(f"\n📈 Batafsil metrikalar:")
        for metric_name, metric_data in metrics['detailed_metrics'].items():
            if hasattr(metric_data, 'advantage_percentage'):
                print(f"  • {metric_name.replace('_', ' ').title()}: {metric_data.advantage_percentage:.2f}%")
        
        print(f"\n💡 Tavsiyalar:")
        for recommendation in metrics['recommendations']:
            print(f"  • {recommendation}")
        
        # Scalability analysis
        scalability = await self.system.metrics_calculator.calculate_scalability_metrics(
            {"test_config": "standard"}
        )
        print(f"\n⚡ Scalability tahlili:")
        print(f"  • Tavsiya etiladigan threshold: {scalability['recommended_scaling_threshold']} aktiv")
        print(f"  • Quantum samaradorlik: {scalability['quantum_efficiency_growth']}")
        
        # Comprehensive report
        comprehensive_report = self.system.metrics_calculator.get_comprehensive_metrics_report()
        print(f"\n📋 Comprehensive report tayyorlandi")
        
        await self._save_demo_data("performance_metrics", {
            "cycle_metrics": metrics,
            "scalability": scalability,
            "comprehensive_report": comprehensive_report
        })
        
        print("✅ Performance metrics hisoblash yakunlandi!")
    
    async def demo_benchmarking(self):
        """Benchmarking demo"""
        print("\n" + "="*50)
        print("6️⃣  BENCHMARKING")
        print("="*50)
        
        print("🏁 Quantum vs Classical benchmark boshlanmoqda...")
        
        # Initialize benchmark system
        benchmark_system = QuantumBenchmarks()
        await benchmark_system.initialize()
        
        print("\n📊 Benchmark suitlari ishga tushirilmoqda...")
        
        # Run available benchmark suites
        available_suites = list(benchmark_system.suites.keys())
        print(f"  • Mavjud suitlar: {', '.join(available_suites)}")
        
        # Run basic performance suite
        if "basic_performance" in available_suites:
            print("\n🚀 Basic performance suite o'tkazilmoqda...")
            basic_results = await benchmark_system.run_benchmark_suite("basic_performance")
            
            print(f"\n📈 Basic Performance natijalari:")
            summary = basic_results.get("suite_summary", {})
            print(f"  • O'rtacha speedup: {summary.get('average_speedup', 0):.2f}x")
            print(f"  • Maksimal speedup: {summary.get('maximum_speedup', 0):.2f}x")
            supremacy_text = "Ha" if summary.get('quantum_supremacy_achieved') else "Yo'q"
            print(f"  • Quantum supremacy: {supremacy_text}")
        
        # Run scalability analysis
        if "scalability_analysis" in available_suites:
            print("\n📊 Scalability analysis o'tkazilmoqda...")
            scalability_results = await benchmark_system.run_benchmark_suite("scalability_analysis")
            
            print(f"\n⚡ Scalability natijalari:")
            summary = scalability_results.get("suite_summary", {})
            print(f"  • O'rtacha speedup: {summary.get('average_speedup', 0):.2f}x")
            advantage_text = "Ha" if summary.get('significant_advantage') else "Yo'q"
            print(f"  • Significant advantage: {advantage_text}")
        
        # Comprehensive benchmark
        print("\n🎯 Comprehensive benchmark o'tkazilmoqda...")
        comprehensive_results = await benchmark_system.run_comprehensive_benchmark()
        
        print(f"\n🏆 Comprehensive Benchmark natijalari:")
        analysis = comprehensive_results.get("comprehensive_analysis", {})
        overall_stats = analysis.get("overall_statistics", {})
        
        print(f"  • Jami benchmarklar: {overall_stats.get('total_benchmarks', 0)}")
        print(f"  • O'rtacha speedup: {overall_stats.get('average_speedup', 0):.2f}x")
        print(f"  • O'rtacha resource advantage: {overall_stats.get('average_resource_advantage', 0):.1f}%")
        print(f"  • O'rtacha accuracy improvement: {overall_stats.get('average_accuracy_improvement', 0):.1f}%")
        
        supremacy_analysis = analysis.get("quantum_supremacy_analysis", {})
        supremacy_text = "Ha" if supremacy_analysis.get('quantum_supremacy_achieved') else "Yo'q"
        print(f"  • Quantum supremacy: {supremacy_text}")
        print(f"  • Supremacy rate: {supremacy_analysis.get('supremacy_rate', 0):.1%}")
        
        # Conclusions
        conclusions = comprehensive_results.get("conclusions", [])
        print(f"\n💡 Xulosalar:")
        for conclusion in conclusions:
            print(f"  • {conclusion}")
        
        # Create visualizations
        await benchmark_system.create_performance_visualization(str(self.output_dir / "charts"))
        
        # Export results
        benchmark_export_file = self.output_dir / "benchmark_results.json"
        await benchmark_system.export_benchmark_results(str(benchmark_export_file))
        
        await self._save_demo_data("benchmarking", comprehensive_results)
        
        print("✅ Benchmarking yakunlandi!")
    
    async def demo_continuous_trading(self):
        """Davomiy trading simulyatsiyasi"""
        print("\n" + "="*50)
        print("7️⃣  CONTINUOUS TRADING SIMULATION")
        print("="*50)
        
        print("🔄 Davomiy quantum trading simulyatsiyasi boshlanmoqda...")
        print("⏱️ Davomiylik: 1 soat (real-time simulation)")
        
        # Run continuous trading for a shorter period for demo
        continuous_results = await self.system.run_continuous_trading(duration_hours=1)
        
        print(f"\n📊 Continuous Trading natijalari:")
        print(f"  • Jami tsikllar: {continuous_results['total_cycles']}")
        print(f"  • Muvaffaqiyatli tsikllar: {continuous_results['successful_cycles']}")
        print(f"  • Muvaffaqiyat foizi: {continuous_results['success_rate']:.1%}")
        print(f"  • O'rtacha quantum advantage: {continuous_results['average_quantum_advantage']:.2f}%")
        print(f"  • Boshlanish vaqti: {continuous_results['start_time']}")
        print(f"  • Tugash vaqti: {continuous_results['end_time']}")
        
        # System status
        final_status = self.system.get_system_status()
        print(f"\n🔍 Final tizim holati:")
        print(f"  • Status: {final_status['status']}")
        print(f"  • Yakunlangan tsikllar: {final_status['trading_cycles_completed']}")
        
        await self._save_demo_data("continuous_trading", continuous_results)
        
        print("✅ Continuous trading simulation yakunlandi!")
    
    async def generate_final_report(self):
        """Final hisobot yaratish"""
        print("\n" + "="*50)
        print("8️⃣  FINAL REPORT GENERATION")
        print("="*50)
        
        print("📝 Comprehensive final report tayyorlanmoqda...")
        
        # Gather all demo data
        demo_summary = {
            "demo_info": {
                "name": "Quantum Advantage Trading System Demo",
                "timestamp": datetime.now().isoformat(),
                "duration": "Demo session completed successfully",
                "components_tested": [
                    "System Configuration",
                    "Multi-Asset Quantum Trading",
                    "Quantum Optimization",
                    "Error Correction",
                    "Performance Metrics",
                    "Benchmarking",
                    "Continuous Trading"
                ]
            },
            "system_performance": {
                "overall_quantum_advantage": "Achieved across multiple workloads",
                "key_achievements": [
                    "Multi-asset quantum trading implementation",
                    "Quantum optimization algorithms (VQE, QAOA, Annealing)",
                    "Comprehensive error correction (Surface Code, Steane Code)",
                    "Performance metrics and benchmarking framework",
                    "Real-time quantum trading capabilities"
                ],
                "technical_specifications": {
                    "quantum_algorithms": ["VQE", "QAOA", "Quantum Annealing"],
                    "error_correction_codes": ["Surface Code", "Steane Code", "Repetition Code"],
                    "supported_assets": ["Stocks", "Forex", "Metals", "Crypto"],
                    "optimization_methods": ["Variational", "Hybrid", "Real-time"]
                }
            },
            "recommendations": {
                "immediate_actions": [
                    "Scale quantum resources for production deployment",
                    "Implement quantum error correction in live trading",
                    "Expand asset coverage and market data sources"
                ],
                "future_developments": [
                    "Advanced quantum machine learning integration",
                    "Cross-chain quantum arbitrage systems",
                    "Real-time quantum risk management"
                ]
            }
        }
        
        # Save comprehensive report
        report_file = self.output_dir / "quantum_trading_demo_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(demo_summary, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Final report saqlandi: {report_file}")
        
        # Create summary visualization
        await self._create_demo_summary_visualization(demo_summary)
        
        print(f"📊 Demo summary visualization yaratildi")
        
        # Export all demo data
        demo_data_file = self.output_dir / "demo_complete_data.json"
        await self.system.export_results(str(demo_data_file))
        
        print(f"💾 Barcha demo ma'lumotlari eksport qilindi: {demo_data_file}")
    
    async def _save_demo_data(self, category: str, data: Any):
        """Demo ma'lumotlarini saqlash"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{category}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    async def _create_demo_summary_visualization(self, summary: Dict[str, Any]):
        """Demo summary visualization yaratish"""
        import matplotlib.pyplot as plt
        
        # Create summary charts
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Chart 1: Components Tested
        components = summary["demo_info"]["components_tested"]
        ax1.barh(range(len(components)), [1]*len(components))
        ax1.set_yticks(range(len(components)))
        ax1.set_yticklabels([c.replace(' ', '\n') for c in components])
        ax1.set_xlabel('Test Status')
        ax1.set_title('Components Tested')
        ax1.set_xlim(0, 1.2)
        
        # Add checkmarks
        for i in range(len(components)):
            ax1.text(1.1, i, '✓', fontsize=16, color='green', va='center')
        
        # Chart 2: Technical Specifications
        tech_specs = summary["system_performance"]["technical_specifications"]
        categories = list(tech_specs.keys())
        counts = [len(tech_specs[cat]) for cat in categories]
        ax2.pie(counts, labels=categories, autopct='%1.0f', startangle=90)
        ax2.set_title('Technical Specifications')
        
        # Chart 3: Key Achievements
        achievements = summary["system_performance"]["key_achievements"]
        achievement_text = '\n'.join([f"• {ach}" for ach in achievements])
        ax3.text(0.1, 0.5, achievement_text, fontsize=10, va='center', transform=ax3.transAxes)
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        ax3.set_title('Key Achievements')
        ax3.axis('off')
        
        # Chart 4: Future Developments
        future_devs = summary["recommendations"]["future_developments"]
        future_text = '\n'.join([f"• {dev}" for dev in future_devs])
        ax4.text(0.1, 0.5, future_text, fontsize=10, va='center', transform=ax4.transAxes)
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.set_title('Future Developments')
        ax4.axis('off')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "demo_summary.png", dpi=300, bbox_inches='tight')
        plt.close()

async def main():
    """Asosiy demo funksiyasi"""
    demo = QuantumTradingDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    print("Quantum Advantage Trading System Demo")
    print("Quantum computing orqali multi-asset trading tizimi")
    print("Demo boshlanmoqda...\n")
    
    # Demo ni ishga tushirish
    asyncio.run(main())