#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Assistant Usage Examples
Advanced GPT Assistant tizimini qanday ishlatish namunalari

Bu fayl AI assistant tizimining asosiy funksiyalarini
namoyish qiladi va amaliy foydalanish ko'rsatkichlarini beradi.

Author: Orion Starline AI Team
Date: 2025-11-05
Version: 2.0.0
"""

import asyncio
import os
from datetime import datetime

# Demo uchun mock setup
from unittest.mock import Mock, patch

class MockOpenAIClient:
    def __init__(self):
        self.chat = MockChat()
        
class MockChat:
    def __init__(self):
        self.completions = MockCompletions()
        
class MockCompletions:
    def create(self, **kwargs):
        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = "Demo javob: Bu mock API dan kelayotgan javobdir. Real API keys bilan ishlaydi."
        response.usage = Mock()
        response.usage.total_tokens = 150
        return response

class MockGeminiModel:
    def generate_content(self, prompt, **kwargs):
        response = Mock()
        response.text = "Demo javob: Bu Gemini mock dan kelayotgan javobdir. OpenAI bilan birga ishlaydi."
        return response

# Setup mocks
with patch('advanced_gpt_assistant.OpenAI', return_value=MockOpenAIClient()), \
     patch('advanced_gpt_assistant.genai', return_value=Mock()), \
     patch('advanced_gpt_assistant.genai.GenerativeModel', return_value=MockGeminiModel()), \
     patch('advanced_gpt_assistant.tiktoken', return_value=Mock()):
    
    from advanced_gpt_assistant import (
        create_ai_assistant,
        TaskType,
        ModelType
    )


async def demo_basic_chat():
    """Asosiy chat demo"""
    print("\n" + "="*50)
    print("🗣️  ASOSIY CHAT DEMO")
    print("="*50)
    
    # AI Assistant yaratish
    assistant = create_ai_assistant(
        openai_key="demo-openai-key",
        gemini_key="demo-gemini-key",
        enable_trading_optimization=True
    )
    
    # Oddiy suhbat
    response = await assistant.chat("Salom! Men trading haqida so'rashni xohlayman.")
    
    print(f"❓ Savol: Men trading haqida so'rashni xohlayman.")
    print(f"🤖 Javob: {response.content}")
    print(f"📊 Model: {response.model_used}")
    print(f"⏱️ Vaqt: {response.response_time:.2f} soniya")
    print(f"💰 Narx: ${response.cost:.4f}")
    print(f"⭐ Sifat: {response.quality_score:.2f}")


async def demo_trading_analysis():
    """Trading analizi demo"""
    print("\n" + "="*50)
    print("📈 TRADING ANALIZI DEMO")
    print("="*50)
    
    assistant = create_ai_assistant(
        openai_key="demo-openai-key",
        gemini_key="demo-gemini-key",
        enable_trading_optimization=True
    )
    
    # Bozor ma'lumotlari
    market_data = {
        "symbol": "BTCUSDT",
        "current_price": 45000,
        "volume": 2500000,
        "rsi": 65,
        "macd": 150,
        "bb_upper": 46000,
        "bb_lower": 44000
    }
    
    # Trading optimizator bilan tahlil
    if hasattr(assistant, 'trading_optimizer'):
        response = await assistant.trading_optimizer.enhanced_trading_analysis(
            TaskType.TECHNICAL_ANALYSIS,
            market_data,
            "Bitcoin uchun qisqa muddatli savdo strategiyasini taklif qiling."
        )
        
        print(f"💹 Crypto: {market_data['symbol']}")
        print(f"💰 Narx: ${market_data['current_price']:,}")
        print(f"📊 RSI: {market_data['rsi']}")
        print(f"📈 Javob: {response.content}")
        print(f"🔧 Model: {response.model_used}")


async def demo_model_selection_strategies():
    """Model tanlash strategiyalari demo"""
    print("\n" + "="*50)
    print("🎯 MODEL TANLASH STRATEGIYALARI DEMO")
    print("="*50)
    
    assistant = create_ai_assistant(
        openai_key="demo-openai-key",
        gemini_key="demo-gemini-key"
    )
    
    # Turli strategiyalar
    strategies = ["cost_optimized", "quality_focused", "speed_optimized", "trading_specialized"]
    
    for strategy in strategies:
        print(f"\n📋 {strategy.upper()} strategiyasi:")
        
        # Model tanlash
        selected_model = assistant._select_best_model(
            TaskType.TRADING_ANALYSIS,
            strategy
        )
        
        print(f"   ✅ Tanlangan model: {selected_model.value}")
        print(f"   🏭 Provayder: {assistant.MODEL_CONFIGS[selected_model].provider}")
        print(f"   💰 Token narxi: ${assistant.MODEL_CONFIGS[selected_model].cost_per_token:.6f}")


async def demo_conversation():
    """Multi-turn conversation demo"""
    print("\n" + "="*50)
    print("💬 MULTI-TURN CONVERSATION DEMO")
    print("="*50)
    
    assistant = create_ai_assistant(
        openai_key="demo-openai-key",
        gemini_key="demo-gemini-key"
    )
    
    conversation_id = "demo_user_001"
    
    # 1-msg
    response1 = await assistant.chat(
        "Men yangi trader man. Portfoliomda 1000$ bor.",
        conversation_id=conversation_id
    )
    print(f"👤 User: Men yangi trader man. Portfoliomda 1000$ bor.")
    print(f"🤖 Assistant: {response1.content[:100]}...")
    
    # 2-msg (context saqlanadi)
    response2 = await assistant.chat(
        "Qanday strategiya taklif qilasiz?",
        conversation_id=conversation_id
    )
    print(f"\n👤 User: Qanday strategiya taklif qilasiz?")
    print(f"🤖 Assistant: {response2.content[:100]}...")


async def demo_cache_performance():
    """Cache performance demo"""
    print("\n" + "="*50)
    print("⚡ CACHE PERFORMANCE DEMO")
    print("="*50)
    
    assistant = create_ai_assistant(
        openai_key="demo-openai-key",
        gemini_key="demo-gemini-key"
    )
    
    test_prompt = "Python dasturlashda list comprehension nima?"
    
    # 1-so'rov (cache miss)
    print("🔄 1-so'rov (cache miss):")
    import time
    start_time = time.time()
    response1 = await assistant.chat(test_prompt, use_cache=True)
    first_time = time.time() - start_time
    print(f"   ⏱️ Vaqt: {first_time:.3f}s")
    print(f"   📦 Cache hit: {response1.cached}")
    
    # 2-so'rov (cache hit)
    print("\n🚀 2-so'rov (cache hit):")
    start_time = time.time()
    response2 = await assistant.chat(test_prompt, use_cache=True)
    second_time = time.time() - start_time
    print(f"   ⏱️ Vaqt: {second_time:.3f}s")
    print(f"   📦 Cache hit: {response2.cached}")
    
    # Performance improvement
    if first_time > 0:
        improvement = ((first_time - second_time) / first_time) * 100
        print(f"   📈 Tezlashtirish: {improvement:.1f}%")


async def demo_cost_optimization():
    """Cost optimization demo"""
    print("\n" + "="*50)
    print("💰 COST OPTIMIZATION DEMO")
    print("="*50)
    
    assistant = create_ai_assistant(
        openai_key="demo-openai-key",
        gemini_key="demo-gemini-key"
    )
    
    # Xarajat optimizatsiya tavsiyalari
    budget = 0.05  # $0.05
    recommendations = assistant.optimize_for_cost(budget)
    
    print(f"💵 Budget limit: ${budget:.4f}")
    print(f"🏆 Optimal modellar:")
    for model in recommendations["optimal_models"]:
        print(f"   • {model}")
    
    print(f"\n📊 Barcha tavsiyalar:")
    for rec in recommendations["recommendations"]:
        print(f"   {rec['model']}: {rec['recommendation']} (efficiency: {rec['cost_efficiency']:.2f})")


async def demo_performance_metrics():
    """Performance metrics demo"""
    print("\n" + "="*50)
    print("📊 PERFORMANCE METRICS DEMO")
    print("="*50)
    
    assistant = create_ai_assistant(
        openai_key="demo-openai-key",
        gemini_key="demo-gemini-key"
    )
    
    # Bir nechta so'rov qilish
    test_prompts = [
        "Bitcoin haqida qisqacha ma'lumot bering",
        "Python dasturlash o'rganish uchun resurslar",
        "Trading strategiyalari haqida",
        "Risk management nima?",
        "AI texnologiyalar rivoji"
    ]
    
    print("🔄 Test so'rovlari yuborilmoqda...")
    for i, prompt in enumerate(test_prompts, 1):
        response = await assistant.chat(prompt)
        print(f"   {i}. {prompt[:30]}... - {response.model_used}")
    
    # Metrikalarni ko'rsatish
    metrics = assistant.get_performance_metrics()
    
    print(f"\n📈 Jami so'rovlar: {metrics['total_requests']}")
    print(f"💬 Faol suhbatlar: {metrics['active_conversations']}")
    
    if 'cache' in metrics:
        cache_stats = metrics['cache']
        print(f"💾 Cache yozuvlari: {cache_stats['total_entries']}")
        print(f"🎯 Cache hit ratio: {cache_stats['hit_ratio']:.2%}")


async def demo_api_status():
    """API status demo"""
    print("\n" + "="*50)
    print("🔌 API STATUS DEMO")
    print("="*50)
    
    assistant = create_ai_assistant(
        openai_key="demo-openai-key",
        gemini_key="demo-gemini-key"
    )
    
    status = assistant.get_api_status()
    
    print("🌐 API Status:")
    for provider, info in status.items():
        connected = "✅" if info['connected'] else "❌"
        print(f"   {connected} {provider.upper()}: Connected = {info['connected']}")


async def main():
    """Barcha demolar"""
    print("🚀 ADVANCED GPT ASSISTANT - FOYDALANISH NAMUNALARI")
    print("=" * 60)
    print(f"Boshlanish vaqti: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Barcha demolar
        await demo_basic_chat()
        await demo_trading_analysis()
        await demo_model_selection_strategies()
        await demo_conversation()
        await demo_cache_performance()
        await demo_cost_optimization()
        await demo_performance_metrics()
        await demo_api_status()
        
        print("\n" + "="*60)
        print("🎉 BARCHA DEMOLAR MUVAFFAQIYATLI TUGADI!")
        print("="*60)
        print("\n📚 Qo'shimcha ma'lumotlar uchun:")
        print("   • ADVANCED_GPT_ASSISTANT_README.md - Batafsil qo'llanma")
        print("   • advanced_gpt_demo.py - To'liq demo script")
        print("   • ai_assistant_mock_test.py - Test script")
        
        print("\n⚙️ Sozlash:")
        print("   • API keys environment variables ga o'rnating")
        print("   • requirements.txt dan dependencies o'rnating")
        print("   • Real API test uchun: python advanced_gpt_demo.py --demo")
        
    except Exception as e:
        print(f"\n❌ Demo xatolik: {e}")


if __name__ == "__main__":
    asyncio.run(main())