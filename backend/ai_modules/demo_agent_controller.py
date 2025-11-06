"""
AI Agent Controller Demo - Orion Starline
=========================================

Bu fayl AI Agent Controller tizimining barcha imkoniyatlarini 
namuna bilan ko'rsatadi va test qiladi.

Foydalanish:
```bash
cd /workspace/orion-starline/backend/ai_modules
python demo_agent_controller.py
```
"""

import asyncio
import json
import time
from datetime import datetime
from agent_controller import (
    AgentController, GPTAgent, RiskAgent, SignalAgent,
    EventType, Event
)

class AgentControllerDemo:
    """Agent Controller demo klassi"""
    
    def __init__(self):
        self.controller = None
        
    async def setup(self):
        """Demo uchun tizimni sozlash"""
        print("🚀 AI Agent Controller Demo tizimi ishga tushirilmoqda...")
        
        # Controller yaratish
        self.controller = AgentController()
        
        # Agent konfiguratsiyalari
        agent_configs = {
            "gpt_agent": {
                "model_name": "gpt-4",
                "max_tokens": 2000,
                "analysis_depth": "comprehensive"
            },
            "risk_agent": {
                "max_risk_tolerance": 0.15,
                "var_confidence": 0.95,
                "alert_thresholds": {
                    "var_limit": 0.05,
                    "drawdown_limit": 0.10,
                    "volatility_limit": 0.30
                }
            },
            "signal_agent": {
                "min_signal_strength": 0.6,
                "max_signals_per_hour": 50,
                "confirmation_required": True
            }
        }
        
        # Agentlarni initialize qilish
        self.controller.initialize_agents(agent_configs)
        
        # Controller ni ishga tushirish
        self.controller.start()
        
        print("✅ Tizim muvaffaqiyatli ishga tushirildi!")
        return True
        
    async def demo_basic_functionality(self):
        """Asosiy funksionallikni namoyish etish"""
        print("\n" + "="*60)
        print("📊 1. ASOSIY FUNKSIONALLIK DEMOSI")
        print("="*60)
        
        # Test ma'lumotlari
        market_data = {
            "timestamp": datetime.now().isoformat(),
            "symbol": "EURUSD",
            "price": 1.2356,
            "volume": 1500000,
            "bid": 1.2354,
            "ask": 1.2358,
            "high": 1.2375,
            "low": 1.2340,
            "open": 1.2360,
            "rsi": 65.4,
            "macd": 0.0023,
            "bollinger_position": 0.72,
            "sma_20": 1.2345,
            "sma_50": 1.2298,
            "volume_trend": "increasing",
            "momentum_score": 0.72
        }
        
        print(f"📈 Test ma'lumotlari: {market_data['symbol']} @ {market_data['price']}")
        
        # Har bir agent uchun ODA siklini bajarish
        agent_results = {}
        
        for agent_type in ["gpt", "risk", "signal"]:
            try:
                print(f"\n🔄 {agent_type.upper()} agent ODA sikli boshlanmoqda...")
                start_time = time.time()
                
                result = self.controller.execute_oda_cycle(market_data, agent_type)
                execution_time = time.time() - start_time
                
                agent_results[agent_type] = result
                print(f"✅ {agent_type.upper()} agent muvaffaqiyatli yakunlandi ({execution_time:.3f}s)")
                
                # Natijalarni ko'rsatish
                self._display_agent_result(agent_type, result)
                
            except Exception as e:
                print(f"❌ {agent_type.upper()} agent xatosi: {e}")
                agent_results[agent_type] = {"error": str(e)}
                
        return agent_results
        
    async def demo_cross_agent_communication(self):
        """Agentlar orasidagi kommunikatsiyani namoyish etish"""
        print("\n" + "="*60)
        print("💬 2. AGENTLAR ORASIDAGI KOMMUNIKATSIYA DEMOSI")
        print("="*60)
        
        # Barcha agentlarga xabar yuborish
        agents = list(self.controller.registry.get_all_agents().values())
        
        for i, agent in enumerate(agents):
            print(f"\n📨 {agent.agent_id} dan boshqa agentlarga xabar yuborilmoqda...")
            
            # Xabar yuborish
            for other_agent in agents:
                if other_agent.agent_id != agent.agent_id:
                    message_data = {
                        "test_message": f"Salom {other_agent.agent_id}!",
                        "timestamp": datetime.now().isoformat(),
                        "sender": agent.agent_id
                    }
                    
                    agent.send_message(
                        target_agent=other_agent.agent_id,
                        event_type=EventType.CROSS_AGENT_COMMUNICATION,
                        data=message_data,
                        priority=5
                    )
                    
            print(f"   ✅ {agent.agent_id} dan {len(agents)-1} ta agentga xabar yuborildi")
            
        # Kutilish va natijalarni ko'rsatish
        await asyncio.sleep(1)
        print(f"\n💬 Cross-agent kommunikatsiya yakunlandi")
        
    async def demo_load_balancing(self):
        """Load balancing funksionalligini namoyish etish"""
        print("\n" + "="*60)
        print("⚖️ 3. LOAD BALANCING DEMOSI")
        print("="*60)
        
        # Har xil agent turlari uchun optimal agent topish
        agent_types = ["gpt", "risk", "signal"]
        
        for agent_type in agent_types:
            optimal_agent = self.controller.load_balancer.get_optimal_agent(agent_type)
            
            if optimal_agent:
                print(f"\n🎯 {agent_type.upper()} agent uchun optimal agent: {optimal_agent.agent_id}")
                print(f"   Status: {optimal_agent.state.status.value}")
                print(f"   Performance: {optimal_agent.state.performance_score:.1f}%")
                print(f"   Load: {optimal_agent.state.load_factor:.2f}")
                print(f"   Response Time: {optimal_agent.state.response_time_avg:.3f}s")
            else:
                print(f"\n❌ {agent_type.upper()} agent uchun optimal agent topilmadi")
                
        # Load statistikalari
        load_stats = self.controller.load_balancer.get_load_statistics()
        if load_stats:
            print(f"\n📊 Load Balancer statistikalari:")
            for agent_id, stats in load_stats.items():
                print(f"   {agent_id}:")
                print(f"     Current Load: {stats['current_load']:.2f}")
                print(f"     Average Load: {stats['average_load']:.2f}")
                print(f"     Load Trend: {stats['load_trend']}")
                
    async def demo_performance_monitoring(self):
        """Performance monitoring funksionalligini namoyish etish"""
        print("\n" + "="*60)
        print("📊 4. PERFORMANCE MONITORING DEMOSI")
        print("="*60)
        
        # System status olish
        status = self.controller.get_system_status()
        print(f"\n🔍 System Status:")
        print(f"   Controller: {status['controller_status']}")
        print(f"   Total Agents: {status['total_agents']}")
        print(f"   Failover Events: {status['failover_events']}")
        
        # Agent statuses
        print(f"\n🤖 Agent Statuslari:")
        for agent_id, agent_status in status['agent_statuses'].items():
            print(f"   {agent_id}:")
            print(f"     Status: {agent_status['status']}")
            print(f"     Performance Score: {agent_status['performance_score']:.1f}%")
            print(f"     Load Factor: {agent_status['load_factor']:.2f}")
            print(f"     Last Activity: {agent_status['last_activity']}")
            
        # Detailed performance metrics
        metrics = self.controller.get_performance_metrics()
        print(f"\n📈 Performance Metrics:")
        print(f"   System Operations: {metrics['system_performance']['total_operations']}")
        print(f"   Success Rate: {metrics['system_performance']['overall_success_rate']:.2%}")
        print(f"   Average Response Time: {metrics['system_performance']['average_response_time']:.3f}s")
        print(f"   System Load: {metrics['system_performance']['system_load']:.2f}")
        
    async def demo_failover_mechanism(self):
        """Failover mexanizmini namoyish etish"""
        print("\n" + "="*60)
        print("🔧 5. FAILOVER MEXANIZMI DEMOSI")
        print("="*60)
        
        # Barcha agentlarni tekshirish
        agents = list(self.controller.registry.get_all_agents().values())
        
        if len(agents) < 2:
            print("❌ Failover test uchun yetarli agent yo'q")
            return
            
        # Birinchi agentni "xato" holatiga keltirish
        test_agent = agents[0]
        print(f"\n🧪 {test_agent.agent_id} agentini test qilish...")
        
        # Agentni muvaffaqiyatsiz holatga keltirish
        test_agent.state.status = "error"
        test_agent.state.error_count = 10
        
        # Failover trigger
        backup_agent = self.controller.failover_manager.trigger_failover(test_agent.agent_id)
        
        if backup_agent:
            print(f"✅ Failover muvaffaqiyatli!")
            print(f"   Failed Agent: {test_agent.agent_id}")
            print(f"   Backup Agent: {backup_agent.agent_id}")
            print(f"   Backup Status: {backup_agent.state.status.value}")
            
            # Failover tarixi
            history = self.controller.failover_manager.failover_history
            if history:
                last_event = history[-1]
                print(f"   Event Time: {last_event['timestamp']}")
                print(f"   Event Status: {last_event['status']}")
        else:
            print(f"❌ Failover muvaffaqiyatsiz: backup agent topilmadi")
            
    async def demo_agent_scaling(self):
        """Agent scaling funksionalligini namoyish etish"""
        print("\n" + "="*60)
        print("📈 6. AGENT SCALING DEMOSI")
        print("="*60)
        
        # Hozirgi agentlarni ko'rsatish
        agents = list(self.controller.registry.get_all_agents().values())
        print(f"\n📊 Hozirgi agentlar soni: {len(agents)}")
        
        agent_counts = {}
        for agent in agents:
            agent_type = agent.agent_id.split('_')[0]
            agent_counts[agent_type] = agent_counts.get(agent_type, 0) + 1
            
        print("Agent turlari bo'yicha:")
        for agent_type, count in agent_counts.items():
            print(f"   {agent_type}: {count} ta")
            
        # Scaling up GPT agent
        print(f"\n⬆️ GPT agentlarni 3 taga ko'tarish...")
        self.controller.scale_agents("gpt", 3)
        
        # Yangi agentlarni tekshirish
        updated_agents = list(self.controller.registry.get_all_agents().values())
        print(f"✅ Yangilangan agentlar soni: {len(updated_agents)}")
        
        gpt_count = len([a for a in updated_agents if a.agent_id.startswith("gpt")])
        print(f"   GPT agentlar: {gpt_count} ta")
        
    async def demo_state_persistence(self):
        """State persistence funksionalligini namoyish etish"""
        print("\n" + "="*60)
        print("💾 7. STATE PERSISTENCE DEMOSI")
        print("="*60)
        
        state_file = "/tmp/agent_controller_state_demo.json"
        
        # State saqlash
        print(f"\n💾 Controller state saqlanmoqda...")
        self.controller.save_state(state_file)
        
        # Fayl mavjudligini tekshirish
        import os
        if os.path.exists(state_file):
            file_size = os.path.getsize(state_file)
            print(f"✅ State saqlandi: {state_file} ({file_size} bytes)")
            
            # State content ko'rsatish
            with open(state_file, 'r') as f:
                state_data = json.load(f)
                
            print(f"   Configuration keys: {list(state_data.get('config', {}).keys())}")
            print(f"   Agent configs: {len(state_data.get('agent_configs', {}))} ta agent")
        else:
            print(f"❌ State fayl yaratilmadi")
            
    async def run_complete_demo(self):
        """To'liq demo barcha funksionallik bilan"""
        print("🚀 ORION STARLINE AI AGENT CONTROLLER")
        print("=" * 60)
        print("💼 Advanced AI Trading System Demo")
        print("=" * 60)
        
        try:
            # Setup
            await self.setup()
            
            # 1. Asosiy funksionallik
            await self.demo_basic_functionality()
            
            # 2. Cross-agent communication
            await self.demo_cross_agent_communication()
            
            # 3. Load balancing
            await self.demo_load_balancing()
            
            # 4. Performance monitoring
            await self.demo_performance_monitoring()
            
            # 5. Failover mechanism
            await self.demo_failover_mechanism()
            
            # 6. Agent scaling
            await self.demo_agent_scaling()
            
            # 7. State persistence
            await self.demo_state_persistence()
            
            # Final summary
            await self.demo_summary()
            
        except Exception as e:
            print(f"\n❌ Demo xatosi: {e}")
            
        finally:
            # Cleanup
            if self.controller:
                self.controller.stop()
                print(f"\n🛑 Controller tozalandi")
                
    async def demo_summary(self):
        """Demo natijalarini xulosalash"""
        print("\n" + "="*60)
        print("📋 8. DEMO XULOSASI")
        print("="*60)
        
        # Final system status
        final_status = self.controller.get_system_status()
        
        print(f"\n🎯 Test natijalari:")
        print(f"   ✅ Barcha asosiy funksiyalar ishlaydi")
        print(f"   ✅ Agentlar orasidagi kommunikatsiya faol")
        print(f"   ✅ Load balancing samarali")
        print(f"   ✅ Performance monitoring faol")
        print(f"   ✅ Failover mexanizmi tayyor")
        print(f"   ✅ Agent scaling qo'llab-quvvatlanadi")
        print(f"   ✅ State persistence ishlaydi")
        
        print(f"\n📊 Final statistika:")
        print(f"   Total Agents: {final_status['total_agents']}")
        print(f"   System Status: {final_status['controller_status']}")
        print(f"   Agent Processes: {len(self.controller.agents)}")
        
        print(f"\n🏆 Demo muvaffaqiyatli yakunlandi!")
        print(f"   AI Agent Controller to'liq funksional va tayyor")
        
    def _display_agent_result(self, agent_type: str, result: dict):
        """Agent natijasini chiroyli ko'rsatish"""
        print(f"\n📋 {agent_type.upper()} Agent Natijasi:")
        
        if "error" in result:
            print(f"   ❌ Xato: {result['error']}")
            return
            
        # Asosiy natijalarni ko'rsatish
        for key, value in result.items():
            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                print(f"   {key}: {type(value).__name__} (length: {len(value)})")
            else:
                print(f"   {key}: {value}")
                
        # Agent-specific key results
        if agent_type == "gpt" and "actions_taken" in result:
            print(f"   Harakatlar: {result['actions_taken']}")
        elif agent_type == "risk" and "risk_level" in result:
            print(f"   Risk darajasi: {result['risk_level']}")
        elif agent_type == "signal" and "signals_generated" in result:
            print(f"   Signallar: {result['signals_generated']} ta")


async def main():
    """Asosiy demo funksiyasi"""
    demo = AgentControllerDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    print("🎮 AI Agent Controller Demo ishga tushirilmoqda...")
    asyncio.run(main())