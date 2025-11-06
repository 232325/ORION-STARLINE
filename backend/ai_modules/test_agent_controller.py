#!/usr/bin/env python3
"""
AI Agent Controller - Test Script
=================================

Bu skript agent_controller.py modulini test qilish uchun
yasashgan bo'lib, barcha asosiy funksionalliklarni tekshiradi.

Foydalanish:
```bash
cd /workspace/orion-starline/backend/ai_modules
python test_agent_controller.py
```
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# AI modules papkasini path ga qo'shish
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Modul importlarini test qilish"""
    print("🧪 Test 1: Modul importlari")
    print("-" * 40)
    
    try:
        from agent_controller import (
            AgentController, GPTAgent, RiskAgent, SignalAgent,
            EventBus, AgentRegistry, LoadBalancer, FailoverManager,
            AgentStatus, EventType, AgentState, Event
        )
        print("✅ Barcha importlar muvaffaqiyatli")
        return True
    except ImportError as e:
        print(f"❌ Import xatosi: {e}")
        return False

def test_basic_functionality():
    """Asosiy funksionallikni test qilish"""
    print("\n🧪 Test 2: Asosiy funksionallik")
    print("-" * 40)
    
    try:
        from agent_controller import AgentController, AgentStatus
        
        # Controller yaratish
        controller = AgentController()
        print("✅ Controller yaratildi")
        
        # Agent configurations
        configs = {
            "gpt_agent": {"model_name": "gpt-4"},
            "risk_agent": {"max_risk_tolerance": 0.10},
            "signal_agent": {"min_signal_strength": 0.7}
        }
        
        # Agentlarni initialize qilish
        controller.initialize_agents(configs)
        print(f"✅ {len(controller.agents)} ta agent initialized")
        
        # Barcha agentlarni tekshirish
        registered_agents = controller.registry.get_all_agents()
        assert len(registered_agents) == 3
        print("✅ 3 ta agent ro'yxatga olindi")
        
        # Agent types tekshirish
        agent_types = ["gpt_assistant", "risk_analytics", "signal_generator"]
        for agent_type in agent_types:
            assert agent_type in registered_agents
            print(f"✅ {agent_type} agent topildi")
            
        return True
        
    except Exception as e:
        print(f"❌ Asosiy funksionallik xatosi: {e}")
        return False

async def test_oda_cycle():
    """ODA siklini test qilish"""
    print("\n🧪 Test 3: ODA Sikli")
    print("-" * 40)
    
    try:
        from agent_controller import AgentController
        
        # Controller setup
        controller = AgentController()
        controller.initialize_agents()
        controller.start()
        print("✅ Controller started")
        
        # Test data
        market_data = {
            "symbol": "EURUSD",
            "price": 1.2356,
            "volume": 1000000,
            "rsi": 65.4,
            "timestamp": datetime.now().isoformat()
        }
        
        # Har bir agent uchun ODA cycle test
        test_results = {}
        
        for agent_type in ["gpt", "risk", "signal"]:
            try:
                # Get agent directly and call async method
                agent_id_mapping = {
                    "gpt": "gpt_assistant",
                    "risk": "risk_analytics", 
                    "signal": "signal_generator"
                }
                agent_id = agent_id_mapping.get(agent_type, f"{agent_type}_agent")
                agent = controller.registry.get_agent(agent_id)
                
                if agent:
                    result = await agent.process_cycle(market_data)
                    test_results[agent_type] = result
                    print(f"✅ {agent_type} agent ODA cycle muvaffaqiyatli")
                    
                    # Result validation
                    assert isinstance(result, dict)
                    assert len(result) > 0
                else:
                    test_results[agent_type] = {"error": "Agent not found"}
                    print(f"❌ {agent_type} agent topilmadi")
                
            except Exception as e:
                print(f"❌ {agent_type} agent ODA cycle xatosi: {e}")
                test_results[agent_type] = {"error": str(e)}
                
        # System status
        status = controller.get_system_status()
        assert status["controller_status"] == "running"
        assert status["total_agents"] == 3
        print("✅ System status to'g'ri")
        
        # Cleanup
        controller.stop()
        print("✅ Controller stopped")
        
        return test_results
        
    except Exception as e:
        print(f"❌ ODA cycle test xatosi: {e}")
        return False

def test_event_system():
    """Event tizimini test qilish"""
    print("\n🧪 Test 4: Event Tizimi")
    print("-" * 40)
    
    try:
        from agent_controller import EventBus, Event, EventType
        
        # Event bus yaratish
        event_bus = EventBus()
        print("✅ Event bus yaratildi")
        
        # Test event
        test_event = Event(
            event_id="test_001",
            event_type=EventType.MARKET_DATA_UPDATE,
            source_agent="test_agent",
            target_agent="target_agent",
            timestamp=datetime.now(),
            data={"price": 1.2356, "symbol": "EURUSD"}
        )
        
        # Event subscriber
        received_events = []
        
        def event_handler(event):
            received_events.append(event)
            
        # Event subscribe
        event_bus.subscribe(EventType.MARKET_DATA_UPDATE, event_handler)
        print("✅ Event handler registered")
        
        # Event publish
        event_bus.publish(test_event)
        print("✅ Event published")
        
        # Event processing
        event_bus.start_processing()
        print("✅ Event processing started")
        
        # Kutilish
        import time
        time.sleep(0.1)
        
        # Check results
        assert len(received_events) > 0
        print(f"✅ {len(received_events)} event received")
        
        return True
        
    except Exception as e:
        print(f"❌ Event system test xatosi: {e}")
        return False

def test_load_balancing():
    """Load balancing ni test qilish"""
    print("\n🧪 Test 5: Load Balancing")
    print("-" * 40)
    
    try:
        from agent_controller import AgentController, LoadBalancer
        
        controller = AgentController()
        controller.initialize_agents()
        controller.start()
        
        load_balancer = controller.load_balancer
        print("✅ Load balancer yaratildi")
        
        # Optimal agent topish
        optimal_agent = load_balancer.get_optimal_agent("gpt")
        if optimal_agent:
            print(f"✅ Optimal agent: {optimal_agent.agent_id}")
        else:
            print("⚠️ Optimal agent topilmadi")
            
        # Load statistikalari
        load_stats = load_balancer.get_load_statistics()
        print(f"✅ Load statistikalari: {len(load_stats)} agent")
        
        controller.stop()
        return True
        
    except Exception as e:
        print(f"❌ Load balancing test xatosi: {e}")
        return False

def test_failover():
    """Failover ni test qilish"""
    print("\n🧪 Test 6: Failover Mechanism")
    print("-" * 40)
    
    try:
        from agent_controller import AgentController, AgentStatus
        
        controller = AgentController()
        controller.initialize_agents()
        controller.start()
        
        # Agentlardan birini fail qilish
        agents = list(controller.registry.get_all_agents().values())
        if len(agents) > 1:
            test_agent = agents[0]
            test_agent.state.status = AgentStatus.ERROR
            test_agent.state.error_count = 10
            print(f"✅ {test_agent.agent_id} agent fail qilindi")
            
            # Failover trigger
            backup_agent = controller.failover_manager.trigger_failover(test_agent.agent_id)
            
            if backup_agent:
                print(f"✅ Failover muvaffaqiyatli: {backup_agent.agent_id}")
            else:
                print("⚠️ Backup agent topilmadi")
                
        controller.stop()
        return True
        
    except Exception as e:
        print(f"❌ Failover test xatosi: {e}")
        return False

def test_state_management():
    """State management ni test qilish"""
    print("\n🧪 Test 7: State Management")
    print("-" * 40)
    
    try:
        from agent_controller import AgentController
        
        controller = AgentController()
        controller.initialize_agents()
        controller.start()
        
        # State save
        state_file = "/tmp/test_agent_state.json"
        controller.save_state(state_file)
        print("✅ State saqlandi")
        
        # Fayl mavjudligini tekshirish
        if os.path.exists(state_file):
            file_size = os.path.getsize(state_file)
            print(f"✅ State fayl: {file_size} bytes")
            
            # State content
            with open(state_file, 'r') as f:
                state_data = json.load(f)
                
            assert "config" in state_data
            assert "agent_configs" in state_data
            print("✅ State content to'g'ri")
            
            # Faylni o'chirish
            os.remove(state_file)
            print("✅ Test state fayl o'chirildi")
        else:
            print("❌ State fayl yaratilmadi")
            
        controller.stop()
        return True
        
    except Exception as e:
        print(f"❌ State management test xatosi: {e}")
        return False

def test_performance_monitoring():
    """Performance monitoring ni test qilish"""
    print("\n🧪 Test 8: Performance Monitoring")
    print("-" * 40)
    
    try:
        from agent_controller import AgentController
        
        controller = AgentController()
        controller.initialize_agents()
        controller.start()
        
        # System status
        status = controller.get_system_status()
        assert "controller_status" in status
        assert "total_agents" in status
        assert "agent_statuses" in status
        print("✅ System status olindi")
        
        # Performance metrics
        metrics = controller.get_performance_metrics()
        assert "agent_metrics" in metrics
        assert "system_performance" in metrics
        print("✅ Performance metrics olindi")
        
        # Individual agent metrics
        for agent in controller.agents:
            agent_metrics = agent.get_performance_metrics()
            assert "agent_id" in agent_metrics
            assert "performance_score" in agent_metrics
            print(f"✅ {agent.agent_id} metrics olindi")
            
        controller.stop()
        return True
        
    except Exception as e:
        print(f"❌ Performance monitoring test xatosi: {e}")
        return False

def run_all_tests():
    """Barcha testlarni bajarish"""
    print("🚀 AI AGENT CONTROLLER - TEST SUITE")
    print("=" * 50)
    print("Orion Starline AI Trading System")
    print("=" * 50)
    
    test_results = {}
    
    # Test sequence
    tests = [
        ("Modul Importlari", test_imports),
        ("Asosiy Funksionallik", test_basic_functionality),
        ("Event Tizimi", test_event_system),
        ("Load Balancing", test_load_balancing),
        ("Failover Mechanism", test_failover),
        ("State Management", test_state_management),
        ("Performance Monitoring", test_performance_monitoring),
    ]
    
    # Add async test separately
    async def run_async_tests():
        results = {}
        results["ODA Sikli"] = await test_oda_cycle()
        return results
    
    # Run sync tests
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name} testi boshlanmoqda...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = test_func()
            else:
                result = test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"❌ Test xatosi: {e}")
            test_results[test_name] = False
    
    # Run async tests
    try:
        async_results = asyncio.run(run_async_tests())
        test_results.update(async_results)
    except Exception as e:
        print(f"❌ Async test xatosi: {e}")
        test_results["ODA Sikli"] = False
    
    # Test results summary
    print("\n" + "=" * 50)
    print("📊 TEST NATIJALARI XULOSASI")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results.items():
        if result is True:
            print(f"✅ {test_name}: O'TDI")
            passed += 1
        elif result is False:
            print(f"❌ {test_name}: XATO")
            failed += 1
        else:
            print(f"⚠️  {test_name}: Qisman")
            failed += 1
    
    print(f"\n📈 Jami: {len(test_results)} ta test")
    print(f"✅ O'tgan: {passed} ta")
    print(f"❌ Xato: {failed} ta")
    
    if failed == 0:
        print(f"\n🎉 BARCHA TESTLAR MUvaffaQiyatLI!")
        print(f"AI Agent Controller tizimi to'liq ishlaydi")
    else:
        print(f"\n⚠️  BA'ZI TESTLARda XATOLAR BOR")
        print(f"Iltimos, xatolarni tekshiring")
    
    return test_results

if __name__ == "__main__":
    # Barcha testlarni ishga tushirish
    results = run_all_tests()
    
    # Exit code
    failed_count = sum(1 for result in results.values() if not result)
    if failed_count == 0:
        exit(0)  # Success
    else:
        exit(1)  # Failure