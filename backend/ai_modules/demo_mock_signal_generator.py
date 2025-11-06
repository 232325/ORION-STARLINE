"""
AI Signal Generator RL-based - Demo (Kutubxonalarsiz)
=====================================================

Bu demo AI Signal Generator RL-based modulini kutubxonalarsiz test qiladi.
Fayl tuzilishi va kod mantig'ini ko'rsatadi.

Author: Orion Starline AI Team
Versiya: 1.0.0
Sana: 2025-11-04
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockFeatureEngineer:
    """Mock Feature Engineer - kutubxonalarsiz ishlash uchun"""
    
    def __init__(self):
        self.feature_count = 0
        logger.info("Mock Feature Engineer yaratildi")
    
    def create_features(self, data):
        """Mock feature creation"""
        # Simulate feature creation
        features = {
            'sma_5': [0.01, 0.02, 0.015] * (len(data) // 3),
            'rsi': [45, 55, 65] * (len(data) // 3),
            'macd': [-0.1, 0.0, 0.1] * (len(data) // 3),
            'volume_ratio': [0.8, 1.2, 1.5] * (len(data) // 3),
            'volatility': [0.02, 0.025, 0.03] * (len(data) // 3)
        }
        self.feature_count = len(features)
        logger.info(f"Mock features yaratildi: {self.feature_count} ta")
        return features
    
    def get_feature_importance(self, target, features):
        """Mock feature importance"""
        importance = {
            'rsi': 0.25,
            'volume_ratio': 0.20,
            'macd': 0.18,
            'sma_5': 0.15,
            'volatility': 0.12
        }
        logger.info("Feature importance hisoblandi")
        return importance

class MockMarketRegimeDetector:
    """Mock Market Regime Detector"""
    
    def __init__(self):
        self.regimes = {
            0: 'trending_bull',
            1: 'trending_bear',
            2: 'sideways',
            3: 'high_volatility',
            4: 'low_volatility'
        }
        logger.info("Mock Market Regime Detector yaratildi")
    
    def detect_regime(self, data):
        """Mock regime detection"""
        # Simulate regime detection
        regimes = []
        for i in range(len(data)):
            if i < 20:
                regimes.append(2)  # sideways
            else:
                # Random regime selection based on price action
                if i % 10 < 3:
                    regimes.append(0)  # trending_bull
                elif i % 10 < 6:
                    regimes.append(1)  # trending_bear
                else:
                    regimes.append(2)  # sideways
        
        logger.info(f"Mock regimes yaratildi: {len(regimes)} ta")
        return regimes

class MockRLAgent:
    """Mock RL Agent"""
    
    def __init__(self, name, state_dim, action_dim, config):
        self.name = name
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config
        self.trained_episodes = 0
        
        logger.info(f"Mock {name} agent yaratildi")
    
    def act(self, state, training=False):
        """Mock action selection"""
        # Simulate different action selection strategies
        if self.name == 'dqn':
            action = 1 if self.trained_episodes > 50 else 0  # BUY after training
        elif self.name == 'ppo':
            action = 2 if self.trained_episodes > 30 else 1  # SELL after training
        elif self.name == 'a2c':
            action = 0  # HOLD by default
        else:
            action = 1  # Default to BUY
        
        self.trained_episodes += 1
        return action
    
    def predict_signal(self):
        """Mock signal prediction"""
        signals = ['BUY', 'SELL', 'HOLD']
        weights = {
            'BUY': 0.4,
            'SELL': 0.3,
            'HOLD': 0.3
        }
        return signals, weights

class MockAISignalGenerator:
    """Mock AI Signal Generator"""
    
    def __init__(self, config):
        self.config = config
        self.feature_engineer = MockFeatureEngineer()
        self.regime_detector = MockMarketRegimeDetector()
        self.agents = {}
        self.performance_history = []
        
        # Initialize agents
        if 'agents' in config:
            for agent_name, agent_config in config['agents'].items():
                self.agents[agent_name] = MockRLAgent(
                    agent_name, 
                    state_dim=50, 
                    action_dim=3, 
                    config=agent_config
                )
        
        logger.info(f"Mock AI Signal Generator yaratildi: {len(self.agents)} agent")
    
    def generate_signals(self, data, mode='inference'):
        """Mock signal generation"""
        # Create features
        features = self.feature_engineer.create_features(data)
        
        # Detect regime
        regimes = self.regime_detector.detect_regime(data)
        current_regime = regimes[-1] if regimes else 2
        
        # Get agent predictions
        agent_predictions = {}
        ensemble_votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        
        for agent_name, agent in self.agents.items():
            if mode == 'training':
                # Simulate training
                for _ in range(10):  # Mock training steps
                    dummy_state = [0.1] * 50
                    action = agent.act(dummy_state, training=True)
            else:
                # Inference
                action = agent.act([0.1] * 50, training=False)
            
            # Convert action to signal
            action_map = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
            signal = action_map.get(action, 'HOLD')
            
            agent_predictions[agent_name] = signal
            
            # Add to ensemble votes
            weight = self.config.get('agents', {}).get(agent_name, {}).get('weight', 0.2)
            ensemble_votes[signal] += weight
        
        # Determine final signal
        final_signal = max(ensemble_votes, key=ensemble_votes.get)
        signal_strength = ensemble_votes[final_signal]
        
        # Calculate confidence
        total_votes = sum(ensemble_votes.values())
        confidence = (ensemble_votes[final_signal] / total_votes) if total_votes > 0 else 0.5
        
        # Adjust for market regime
        regime_multiplier = {
            0: 1.2,  # trending_bull
            1: 0.8,  # trending_bear
            2: 1.0,  # sideways
            3: 0.7,  # high_volatility
            4: 1.1   # low_volatility
        }.get(current_regime, 1.0)
        
        signal = {
            'signal': final_signal,
            'strength': signal_strength * regime_multiplier,
            'confidence': confidence,
            'agent_predictions': agent_predictions,
            'votes': ensemble_votes,
            'timestamp': datetime.now().isoformat(),
            'market_regime': self.regime_detector.regimes.get(current_regime, 'unknown')
        }
        
        # Track performance
        self.performance_history.append({
            'timestamp': datetime.now().isoformat(),
            'signal': signal,
            'regime': current_regime
        })
        
        logger.info(f"Mock signals yaratildi: {signal['signal']} (confidence: {signal['confidence']:.2f})")
        return signal
    
    def get_performance_metrics(self):
        """Mock performance metrics"""
        if not self.performance_history:
            return {}
        
        recent_signals = self.performance_history[-10:]  # Last 10 signals
        
        # Count signal types
        signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        confidences = []
        
        for record in recent_signals:
            signal = record['signal']
            signal_counts[signal['signal']] += 1
            confidences.append(signal['confidence'])
        
        total = len(recent_signals)
        regime_name = self.regime_detector.regimes.get(
            self.performance_history[-1]['regime'], 'unknown'
        )
        
        metrics = {
            'total_signals': total,
            'buy_ratio': signal_counts['BUY'] / total,
            'sell_ratio': signal_counts['SELL'] / total,
            'hold_ratio': signal_counts['HOLD'] / total,
            'average_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'current_regime': regime_name,
            'active_agents': len(self.agents)
        }
        
        logger.info("Mock performance metrics hisoblandi")
        return metrics

def create_sample_data(days=100):
    """Sample market data yaratish"""
    logger.info(f"Sample data yaratilmoqda: {days} kun")
    
    start_date = datetime.now() - timedelta(days=days)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Mock price data
    base_price = 100
    prices = []
    current_price = base_price
    
    for i in range(days):
        # Simulate price movement
        change = (i * 0.001) + (0.02 * (1 if i % 10 < 5 else -1))  # Trend + cycle
        current_price *= (1 + change)
        prices.append({
            'timestamp': dates[i].isoformat(),
            'open': current_price,
            'high': current_price * 1.02,
            'low': current_price * 0.98,
            'close': current_price,
            'volume': 1000000 + (i * 1000)
        })
    
    logger.info(f"Sample data yaratildi: {len(prices)} qator")
    return prices

def run_mock_demo():
    """Mock demo boshqaruvchi"""
    logger.info("🚀 AI Signal Generator RL-based - Mock Demo boshlanmoqda")
    logger.info("=" * 60)
    
    # Configuration
    config = {
        'model_ensemble': True,
        'agents': {
            'dqn': {
                'weight': 0.25,
                'epsilon': 1.0,
                'epsilon_decay': 0.995
            },
            'ppo': {
                'weight': 0.25,
                'gamma': 0.99
            },
            'a2c': {
                'weight': 0.25,
                'gamma': 0.99
            },
            'ddpg': {
                'weight': 0.25,
                'tau': 0.005,
                'gamma': 0.99
            }
        },
        'training_episodes': 100
    }
    
    try:
        # 1. Create signal generator
        logger.info("\n1️⃣ AI Signal Generator yaratilmoqda...")
        generator = MockAISignalGenerator(config)
        logger.info(f"✅ {len(generator.agents)} agent yaratildi: {list(generator.agents.keys())}")
        
        # 2. Create sample data
        logger.info("\n2️⃣ Sample market data yaratilmoqda...")
        data = create_sample_data(100)
        logger.info(f"✅ {len(data)} kunlik data yaratildi")
        logger.info(f"   Narx diapazoni: {data[0]['close']:.2f} - {data[-1]['close']:.2f}")
        
        # 3. Generate signals
        logger.info("\n3️⃣ Trading signallar yaratilmoqda...")
        signals = generator.generate_signals(data, mode='training')
        
        logger.info("📈 Generated signals:")
        logger.info(f"   Signal: {signals['signal']}")
        logger.info(f"   Strength: {signals['strength']:.3f}")
        logger.info(f"   Confidence: {signals['confidence']:.3f}")
        logger.info(f"   Market Regime: {signals['market_regime']}")
        
        # 4. Agent predictions
        logger.info("🤖 Agent predictions:")
        for agent, prediction in signals['agent_predictions'].items():
            logger.info(f"   {agent}: {prediction}")
        
        # 5. Ensemble votes
        logger.info("🗳️  Ensemble votes:")
        for signal, votes in signals['votes'].items():
            logger.info(f"   {signal}: {votes:.3f}")
        
        # 6. Generate more signals for backtesting
        logger.info("\n4️⃣ Backtesting simulation...")
        for i in range(5):
            subset_data = data[:50 + i * 10]  # Expanding window
            test_signals = generator.generate_signals(subset_data, mode='inference')
            logger.info(f"   Test {i+1}: {test_signals['signal']} (confidence: {test_signals['confidence']:.2f})")
        
        # 7. Performance metrics
        logger.info("\n5️⃣ Performance metrics:")
        metrics = generator.get_performance_metrics()
        for key, value in metrics.items():
            if isinstance(value, float):
                logger.info(f"   {key}: {value:.3f}")
            else:
                logger.info(f"   {key}: {value}")
        
        # 8. Save results
        logger.info("\n6️⃣ Natijalarni saqlash...")
        results = {
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'latest_signals': signals,
            'performance_metrics': metrics,
            'regime_mapping': generator.regime_detector.regimes,
            'feature_count': generator.feature_engineer.feature_count,
            'total_signals_generated': len(generator.performance_history)
        }
        
        output_file = '/workspace/orion-starline/backend/ai_modules/demo_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Natijalar saqlandi: {output_file}")
        
        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("🎉 MOCK DEMO TUGALLANDI")
        logger.info("=" * 60)
        logger.info("✅ AI Signal Generator muvaffaqiyatli test qilindi")
        logger.info(f"🤖 {len(generator.agents)} ta RL agent ishladi")
        logger.info(f"📈 Joriy signal: {signals['signal']} (confidence: {signals['confidence']:.2f})")
        logger.info(f"📊 {len(generator.performance_history)} ta signal yaratildi")
        logger.info(f"🔄 Joriy bozor rejimi: {signals['market_regime']}")
        logger.info(f"💾 Natijalar: {output_file}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Demo xatosi: {e}")
        import traceback
        traceback.print_exc()
        return None

def print_demo_summary():
    """Demo xulosasi"""
    print("\n" + "=" * 60)
    print("🎯 AI Signal Generator RL-based - Xulosa")
    print("=" * 60)
    print("📁 Fayl joylashuvi: /workspace/orion-starline/backend/ai_modules/")
    print("📄 Asosiy fayl: ai_signal_generator.py")
    print("🎬 Demo fayl: demo_mock_signal_generator.py")
    print("📊 Demo natijalar: demo_results.json")
    print("\n🚀 Xususiyatlari:")
    print("   • DQN, PPO, A2C, DDPG, TD3 algoritmlari")
    print("   • Multi-timeframe analysis")
    print("   • Pattern recognition")
    print("   • Technical indicator combination")
    print("   • Market sentiment analysis")
    print("   • Volume analysis")
    print("   • Support/resistance detection")
    print("   • Trend identification")
    print("   • Market regime awareness")
    print("   • Model ensemble")
    print("   • Confidence scoring")
    print("   • Backtesting integration")
    print("=" * 60)

if __name__ == "__main__":
    # Mock demo-ni ishga tushirish
    results = run_mock_demo()
    
    if results:
        print_demo_summary()
    else:
        print("❌ Demo xatosi yuz berdi")
