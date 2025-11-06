#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced GPT Assistant Demo
AI Model Integration tizimi demo va test fayli

Ushbu fayl advanced_gpt_assistant.py da yaratilgan tizimni
test qilish va qo'llash uchun mo'ljallangan.

Author: Orion Starline AI Team
Date: 2025-11-05
Version: 2.0.0
"""

import asyncio
import json
import os
import sys
from datetime import datetime
import logging

# AI Assistant import
from advanced_gpt_assistant import (
    AdvancedGPTAssistant,
    create_ai_assistant,
    TaskType,
    ModelType,
    TradingModelOptimizer
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAssistantDemo:
    """AI Assistant demo class"""
    
    def __init__(self):
        self.assistant = None
        self.test_results = []
    
    def setup_assistant(self, openai_key=None, gemini_key=None):
        """AI Assistant ni sozlash"""
        try:
            self.assistant = create_ai_assistant(
                openai_key=openai_key,
                gemini_key=gemini_key,
                enable_trading_optimization=True
            )
            logger.info("AI Assistant muvaffaqiyatli yaratildi")
            return True
        except Exception as e:
            logger.error(f"AI Assistant yaratishda xatolik: {e}")
            return False
    
    async def test_basic_chat(self):
        """Asosiy chat test"""
        logger.info("=== Asosiy Chat Test ===")
        
        test_prompts = [
            "Salom! Men trading haqida so'rashni xohlayman.",
            "Python dasturlash tili haqida qisqacha ma'lumot bering.",
            "Bitcoin narxi hozir qanday va texnik tahlil qiling.",
            "Risk management strategiyalari nima?",
            "AI va machine learning o'rtasidagi farq nima?"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            try:
                logger.info(f"Test {i}: {prompt[:50]}...")
                
                response = await self.assistant.chat(
                    prompt=prompt,
                    strategy="cost_optimized"
                )
                
                if response.error:
                    logger.error(f"Xatolik: {response.error}")
                    self.test_results.append({
                        "test": f"basic_chat_{i}",
                        "status": "failed",
                        "error": response.error
                    })
                else:
                    logger.info(f"Javob: {response.content[:100]}...")
                    logger.info(f"Model: {response.model_used}")
                    logger.info(f"Sifat: {response.quality_score:.2f}")
                    logger.info(f"Narx: ${response.cost:.4f}")
                    
                    self.test_results.append({
                        "test": f"basic_chat_{i}",
                        "status": "success",
                        "model": response.model_used,
                        "quality": response.quality_score,
                        "cost": response.cost,
                        "cached": response.cached
                    })
                
            except Exception as e:
                logger.error(f"Test {i} xatolik: {e}")
                self.test_results.append({
                    "test": f"basic_chat_{i}",
                    "status": "error",
                    "error": str(e)
                })
    
    async def test_trading_analysis(self):
        """Trading analizi test"""
        logger.info("=== Trading Analysis Test ===")
        
        if not hasattr(self.assistant, 'trading_optimizer'):
            logger.warning("Trading optimizer topilmadi")
            return
        
        # Test market data
        market_data_samples = [
            {
                "symbol": "BTCUSDT",
                "current_price": 45000,
                "volume": 2500000,
                "rsi": 72,
                "macd": 150,
                "bb_upper": 46000,
                "bb_lower": 44000,
                "sma_20": 44500,
                "sma_50": 44200
            },
            {
                "symbol": "ETHUSDT",
                "current_price": 2800,
                "volume": 1800000,
                "rsi": 45,
                "macd": -25,
                "bb_upper": 2900,
                "bb_lower": 2700,
                "sma_20": 2750,
                "sma_50": 2720
            }
        ]
        
        for i, market_data in enumerate(market_data_samples, 1):
            try:
                logger.info(f"Trading Test {i}: {market_data['symbol']}")
                
                # Technical analysis
                response = await self.assistant.trading_optimizer.enhanced_trading_analysis(
                    TaskType.TECHNICAL_ANALYSIS,
                    market_data,
                    user_question="Bu coin uchun qisqa muddatli savdo strategiyasini taklif qiling."
                )
                
                if response.error:
                    logger.error(f"Trading xatolik: {response.error}")
                else:
                    logger.info(f"Trading Analysis: {response.content[:200]}...")
                    logger.info(f"Model: {response.model_used}")
                    logger.info(f"Sifat: {response.quality_score:.2f}")
                
            except Exception as e:
                logger.error(f"Trading test xatolik: {e}")
    
    async def test_model_comparison(self):
        """Model taqqoslash test"""
        logger.info("=== Model Comparison Test ===")
        
        test_prompt = "AI nima va u qanday ishlaydi? Qisqacha tushuntiring."
        
        try:
            # Single model test
            response = await self.assistant.chat(
                prompt=test_prompt,
                strategy="quality_focused"
            )
            
            logger.info(f"Single model javobi: {response.content[:100]}...")
            
            # Multiple model comparison (agar API keys mavjud bo'lsa)
            if self.assistant.openai_client and self.assistant.gemini_model:
                comparison_results = await self.assistant.multi_model_comparison(
                    test_prompt,
                    [ModelType.GPT4O, ModelType.GEMINI_PRO]
                )
                
                logger.info("=== Model Comparison Results ===")
                for model_type, model_response in comparison_results.items():
                    if not model_response.error:
                        logger.info(f"{model_type.value}: {model_response.content[:100]}...")
                    else:
                        logger.error(f"{model_type.value}: {model_response.error}")
            
        except Exception as e:
            logger.error(f"Model comparison xatolik: {e}")
    
    async def test_streaming(self):
        """Streaming response test"""
        logger.info("=== Streaming Test ===")
        
        try:
            response_generator = await self.assistant.chat(
                prompt="Havolangan matnni yozib bering: 'I love programming because it allows me to create solutions to complex problems.'",
                stream=True
            )
            
            logger.info("Streaming response:")
            async for response in response_generator:
                if response.content:
                    print(response.content, end="", flush=True)
            print()  # New line
            
        except Exception as e:
            logger.error(f"Streaming xatolik: {e}")
    
    async def test_cache_performance(self):
        """Cache performance test"""
        logger.info("=== Cache Performance Test ===")
        
        cache_test_prompt = "Python programlamasida list comprehension nima?"
        
        try:
            # First request (cache miss)
            start_time = datetime.now()
            response1 = await self.assistant.chat(cache_test_prompt, use_cache=True)
            first_time = (datetime.now() - start_time).total_seconds()
            
            # Second request (cache hit)
            start_time = datetime.now()
            response2 = await self.assistant.chat(cache_test_prompt, use_cache=True)
            second_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"First request time: {first_time:.2f}s")
            logger.info(f"Second request time: {second_time:.2f}s")
            logger.info(f"Cache hit: {response2.cached}")
            logger.info(f"Speed improvement: {((first_time - second_time) / first_time * 100):.1f}%")
            
        except Exception as e:
            logger.error(f"Cache test xatolik: {e}")
    
    async def test_error_handling(self):
        """Error handling test"""
        logger.info("=== Error Handling Test ===")
        
        try:
            # Test with invalid model (agar fallback ishlasa)
            response = await self.assistant.chat(
                "This is a test for error handling.",
                strategy="invalid_strategy"  # This will use default
            )
            
            logger.info(f"Error handling test: {response.model_used}")
            logger.info(f"Response quality: {response.quality_score:.2f}")
            
        except Exception as e:
            logger.info(f"Expected error handled: {e}")
    
    async def test_performance_metrics(self):
        """Performance metrics test"""
        logger.info("=== Performance Metrics Test ===")
        
        try:
            metrics = self.assistant.get_performance_metrics()
            
            logger.info("=== Performance Statistics ===")
            logger.info(f"Total requests: {metrics['total_requests']}")
            logger.info(f"Active conversations: {metrics['active_conversations']}")
            
            if 'models' in metrics:
                for model_name, stats in metrics['models'].items():
                    if stats['total_requests'] > 0:
                        logger.info(f"{model_name}:")
                        logger.info(f"  Average quality: {stats['avg_quality']:.2f}")
                        logger.info(f"  Average response time: {stats['avg_response_time']:.2f}s")
                        logger.info(f"  Average cost: ${stats['avg_cost']:.4f}")
                        logger.info(f"  Total requests: {stats['total_requests']}")
            
            if 'cache' in metrics:
                logger.info(f"Cache entries: {metrics['cache']['total_entries']}")
                logger.info(f"Cache hit ratio: {metrics['cache']['hit_ratio']:.2f}")
            
        except Exception as e:
            logger.error(f"Metrics test xatolik: {e}")
    
    async def test_cost_optimization(self):
        """Cost optimization test"""
        logger.info("=== Cost Optimization Test ===")
        
        try:
            recommendations = self.assistant.optimize_for_cost(budget_limit=0.05)  # $0.05 budget
            
            logger.info("=== Cost Optimization Recommendations ===")
            logger.info(f"Budget limit: ${recommendations['budget_limit']:.4f}")
            
            for rec in recommendations['recommendations']:
                logger.info(f"Model: {rec['model']}")
                logger.info(f"Cost efficiency: {rec['cost_efficiency']:.2f}")
                logger.info(f"Recommendation: {rec['recommendation']}")
                logger.info("---")
            
            logger.info(f"Optimal models: {recommendations['optimal_models']}")
            
        except Exception as e:
            logger.error(f"Cost optimization test xatolik: {e}")
    
    async def test_multi_turn_conversation(self):
        """Multi-turn conversation test"""
        logger.info("=== Multi-turn Conversation Test ===")
        
        conversation_id = "test_conversation_001"
        
        try:
            # First message
            response1 = await self.assistant.chat(
                "Men yangi trader man. Portfoliomda 1000$ bor.",
                conversation_id=conversation_id
            )
            logger.info(f"Response 1: {response1.content[:100]}...")
            
            # Second message (context maintained)
            response2 = await self.assistant.chat(
                "Endi qanday strategiya taklif qilasiz?",
                conversation_id=conversation_id
            )
            logger.info(f"Response 2: {response2.content[:100]}...")
            
            # Third message
            response3 = await self.assistant.chat(
            "Va bu strategiya uchun risk management qanday bo'ladi?",
                conversation_id=conversation_id
            )
            logger.info(f"Response 3: {response3.content[:100]}...")
            
        except Exception as e:
            logger.error(f"Multi-turn conversation test xatolik: {e}")
    
    def print_test_summary(self):
        """Test natijalarini ko'rsatish"""
        logger.info("=== Test Summary ===")
        
        successful_tests = sum(1 for result in self.test_results if result['status'] == 'success')
        failed_tests = sum(1 for result in self.test_results if result['status'] == 'failed')
        error_tests = sum(1 for result in self.test_results if result['status'] == 'error')
        
        logger.info(f"Successful tests: {successful_tests}")
        logger.info(f"Failed tests: {failed_tests}")
        logger.info(f"Error tests: {error_tests}")
        logger.info(f"Total tests: {len(self.test_results)}")
        
        # Save results to file
        with open('ai_assistant_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info("Test results saved to ai_assistant_test_results.json")
    
    async def run_all_tests(self):
        """Barcha testlarni ishga tushirish"""
        logger.info("AI Assistant Test Suite boshlanmoqda...")
        
        # Setup assistant
        if not self.setup_assistant():
            logger.error("AI Assistant setup failed")
            return
        
        # Run all tests
        await self.test_basic_chat()
        await self.test_trading_analysis()
        await self.test_model_comparison()
        await self.test_streaming()
        await self.test_cache_performance()
        await self.test_error_handling()
        await self.test_performance_metrics()
        await self.test_cost_optimization()
        await self.test_multi_turn_conversation()
        
        # Print summary
        self.print_test_summary()
        logger.info("Test Suite tugadi!")


async def demo_with_real_api():
    """Real API bilan demo"""
    logger.info("=== Real API Demo ===")
    
    # API keys olish
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not openai_key and not gemini_key:
        logger.warning("API keys topilmadi. Demo API keys bilan ishga tushiriladi.")
        # Demo uchun mock keys
        openai_key = "demo-openai-key"
        gemini_key = "demo-gemini-key"
    
    # Assistant yaratish
    assistant = create_ai_assistant(
        openai_key=openai_key,
        gemini_key=gemini_key,
        enable_trading_optimization=True
    )
    
    # Basic conversation
    logger.info("Basic chat demo:")
    response = await assistant.chat("Men yangi trader man. Bitcoin haqida nimani bilishim kerak?")
    print(f"Assistant: {response.content}")
    print(f"Model: {response.model_used}")
    print(f"Cost: ${response.cost:.4f}")
    
    # Trading analysis demo
    if hasattr(assistant, 'trading_optimizer'):
        logger.info("\nTrading analysis demo:")
        market_data = {
            "symbol": "BTCUSDT",
            "current_price": 45000,
            "volume": 2500000,
            "rsi": 65,
            "macd": 150
        }
        
        trading_response = await assistant.trading_optimizer.enhanced_trading_analysis(
            TaskType.TECHNICAL_ANALYSIS,
            market_data,
            "Bu coin uchun qisqa muddatli savdo strategiyasini taklif qiling."
        )
        print(f"Trading Assistant: {trading_response.content}")
    
    # Performance metrics
    logger.info("\nPerformance metrics:")
    metrics = assistant.get_performance_metrics()
    print(json.dumps(metrics, indent=2, default=str))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Assistant Demo")
    parser.add_argument("--demo", action="store_true", help="Run simple demo")
    parser.add_argument("--test", action="store_true", help="Run full test suite")
    parser.add_argument("--api-keys", nargs=2, metavar=("OPENAI_KEY", "GEMINI_KEY"), 
                       help="API keys for testing")
    
    args = parser.parse_args()
    
    if args.demo:
        asyncio.run(demo_with_real_api())
    elif args.test:
        demo = AIAssistantDemo()
        asyncio.run(demo.run_all_tests())
    else:
        # Default: simple demo
        asyncio.run(demo_with_real_api())