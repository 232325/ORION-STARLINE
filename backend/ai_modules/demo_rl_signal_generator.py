"""
Demo: AI Signal Generator RL-based
==================================

Bu demo AI Signal Generator RL-based modulini sinab ko'rsatadi.
Multiple RL algoritmlar (DQN, PPO, A2C, DDPG, TD3) yordamida trading signallarini yaratish.

Author: Orion Starline AI Team
Versiya: 1.0.0
Sana: 2025-11-04
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import torch
import logging
from datetime import datetime, timedelta

# Import AI Signal Generator
from ai_modules.ai_signal_generator import (
    AISignalGenerator,
    FeatureEngineer,
    MarketRegimeDetector,
    DQNAgent,
    PPOAgent,
    A2CAgent,
    DDPGAgent,
    TD3Agent
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_market_data(days: int = 365) -> pd.DataFrame:
    """Namuna bozor ma'lumotlarini yaratish"""
    logger.info(f"Sample market data yaratilmoqda: {days} kun")
    
    # Sana diapazoni
    start_date = datetime.now() - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=datetime.now(), freq='D')
    n = len(dates)
    
    # Realistic price data generation
    np.random.seed(42)
    
    # Trend component
    trend = np.linspace(0, 0.5, n)  # 50% growth over period
    
    # Cyclical component (market cycles)
    cycle = 0.1 * np.sin(2 * np.pi * np.arange(n) / 252)  # Annual cycle
    
    # Random walk component
    random_walk = np.cumsum(np.random.normal(0, 0.02, n))
    
    # Combine components
    returns = trend + cycle + random_walk
    
    # Generate OHLCV data
    base_price = 100
    prices = base_price * np.cumprod(1 + returns)
    
    # Create realistic OHLCV
    daily_volatility = np.random.uniform(0.01, 0.03, n)
    
    high_noise = np.random.uniform(0, 0.02, n)
    low_noise = np.random.uniform(0, 0.02, n)
    open_noise = np.random.uniform(-0.01, 0.01, n)
    volume_base = 1000000
    volume_noise = np.random.lognormal(0, 0.5, n)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices * (1 + open_noise),
        'high': prices * (1 + high_noise + daily_volatility),
        'low': prices * (1 - low_noise - daily_volatility),
        'close': prices,
        'volume': volume_base * volume_noise
    })
    
    # Ensure OHLC relationships are correct
    data['high'] = np.maximum.reduce([data['open'], data['high'], data['close']])
    data['low'] = np.minimum.reduce([data['open'], data['low'], data['close']])
    
    logger.info(f"Market data yaratildi: {len(data)} qator, narx diapazoni: {data['close'].min():.2f} - {data['close'].max():.2f}")
    
    return data

def test_feature_engineering():
    """Feature Engineering test"""
    logger.info("🔧 Feature Engineering test boshlanmoqda...")
    
    # Create sample data
    data = create_sample_market_data(100)
    
    # Initialize feature engineer
    feature_engineer = FeatureEngineer()
    
    # Create features
    features = feature_engineer.create_features(data)
    
    # Remove NaN values
    features = features.dropna()
    
    logger.info(f"Feature yaratish tugallandi: {len(features.columns)} feature")
    logger.info(f"Feature namunalari: {list(features.columns[:10])}")
    
    # Calculate feature importance
    if 'close' in data.columns:
        target = data['close'].pct_change().shift(-1).loc[features.index]
        importance = feature_engineer.get_feature_importance(target, features)
        logger.info(f"Top 5 muhim featurelar: {list(importance.keys())[:5]}")
    
    # Normalize features
    features_normalized = feature_engineer.normalize_features(features, fit=True)
    
    logger.info("✅ Feature Engineering test muvaffaqiyatli")
    return features, features_normalized

def test_market_regime_detector():
    """Market Regime Detection test"""
    logger.info("📊 Market Regime Detection test boshlanmoqda...")
    
    # Create sample data
    data = create_sample_market_data(200)
    
    # Initialize regime detector
    regime_detector = MarketRegimeDetector()
    
    # Detect regimes
    regimes = regime_detector.detect_regime(data)
    
    regime_names = {
        0: 'trending_bull',
        1: 'trending_bear', 
        2: 'sideways',
        3: 'high_volatility',
        4: 'low_volatility'
    }
    
    # Count regime distribution
    regime_counts = {}
    for code, name in regime_names.items():
        count = (regimes == code).sum()
        regime_counts[name] = count
    
    logger.info(f"Regime taqsimoti: {regime_counts}")
    logger.info(f"Joriy regime: {regime_names.get(regimes.iloc[-1], 'unknown')}")
    
    logger.info("✅ Market Regime Detection test muvaffaqiyatli")
    return regimes

def test_individual_agents():
    """Individual RL agent test"""
    logger.info("🤖 Individual RL Agent test boshlanmoqda...")
    
    # Configuration
    state_dim = 50
    action_dim = 3
    
    agent_configs = {
        'dqn': {
            'epsilon': 1.0,
            'epsilon_decay': 0.995,
            'epsilon_min': 0.01,
            'update_target_every': 100
        },
        'ppo': {
            'gamma': 0.99,
            'gae_lambda': 0.95,
            'clip_ratio': 0.2,
            'value_coef': 0.5,
            'entropy_coef': 0.01
        },
        'a2c': {
            'gamma': 0.99
        },
        'ddpg': {
            'tau': 0.005,
            'gamma': 0.99
        },
        'td3': {
            'tau': 0.005,
            'gamma': 0.99,
            'policy_delay': 2,
            'target_noise': 0.2,
            'noise_clip': 0.5
        }
    }
    
    # Test each agent
    agents = {}
    for agent_name, config in agent_configs.items():
        try:
            if agent_name == 'dqn':
                agent = DQNAgent(state_dim, action_dim, config)
            elif agent_name == 'ppo':
                agent = PPOAgent(state_dim, action_dim, config)
            elif agent_name == 'a2c':
                agent = A2CAgent(state_dim, action_dim, config)
            elif agent_name == 'ddpg':
                agent = DDPGAgent(state_dim, 1, config)  # Continuous action
            elif agent_name == 'td3':
                agent = TD3Agent(state_dim, 1, config)   # Continuous action
            
            agents[agent_name] = agent
            
            # Test action selection
            state = np.random.random(state_dim)
            
            if agent_name in ['dqn', 'ppo', 'a2c']:
                action = agent.act(state, training=False)
                logger.info(f"{agent_name}: Action = {action}")
            else:
                action = agent.act(state, training=False)
                logger.info(f"{agent_name}: Action = {action[:3]}...")  # Show first 3 values
            
        except Exception as e:
            logger.error(f"{agent_name} agent testida xato: {e}")
    
    logger.info(f"✅ {len(agents)} ta agent muvaffaqiyatli test qilindi")
    return agents

def test_ai_signal_generator():
    """AI Signal Generator comprehensive test"""
    logger.info("🎯 AI Signal Generator comprehensive test boshlanmoqda...")
    
    # Configuration
    config = {
        'model_ensemble': True,
        'agents': {
            'dqn': {
                'weight': 0.2,
                'epsilon': 1.0,
                'epsilon_decay': 0.995,
                'epsilon_min': 0.01,
                'update_target_every': 100
            },
            'ppo': {
                'weight': 0.2,
                'gamma': 0.99,
                'gae_lambda': 0.95,
                'clip_ratio': 0.2,
                'value_coef': 0.5,
                'entropy_coef': 0.01
            },
            'a2c': {
                'weight': 0.2,
                'gamma': 0.99
            },
            'ddpg': {
                'weight': 0.2,
                'tau': 0.005,
                'gamma': 0.99
            },
            'td3': {
                'weight': 0.2,
                'tau': 0.005,
                'gamma': 0.99,
                'policy_delay': 2,
                'target_noise': 0.2,
                'noise_clip': 0.5
            }
        },
        'training_episodes': 10  # Small for demo
    }
    
    # Create signal generator
    signal_generator = AISignalGenerator(config)
    
    # Generate sample data
    data = create_sample_market_data(200)
    logger.info(f"Sample data yaratildi: {len(data)} kunlik ma'lumot")
    
    # Generate signals
    signals = signal_generator.generate_signals(data, mode='training')
    
    logger.info("📈 Generated signals:")
    logger.info(f"  Signal: {signals['signal']}")
    logger.info(f"  Strength: {signals['strength']:.4f}")
    logger.info(f"  Confidence: {signals['confidence']:.4f}")
    logger.info(f"  Agent votes: {signals['votes']}")
    
    # Get performance metrics
    metrics = signal_generator.get_performance_metrics()
    
    logger.info("📊 Performance metrics:")
    for key, value in metrics.items():
        logger.info(f"  {key}: {value}")
    
    # Save models
    model_dir = '/tmp/ai_signal_models'
    signal_generator.save_models(model_dir)
    logger.info(f"Modellar saqlandi: {model_dir}")
    
    logger.info("✅ AI Signal Generator test muvaffaqiyatli")
    return signal_generator, signals, metrics

def test_backtesting_integration():
    """Backtesting integration test"""
    logger.info("🔄 Backtesting Integration test boshlanmoqda...")
    
    # Create sample data
    data = create_sample_market_data(100)
    
    # Simulate signal generation over time
    signal_history = []
    
    for i in range(50, len(data), 5):  # Every 5 days
        subset_data = data.iloc[:i]
        
        # Create signal generator
        config = {
            'model_ensemble': True,
            'agents': {
                'dqn': {'weight': 0.25, 'epsilon': 0.1},  # Less exploration
                'ppo': {'weight': 0.25, 'gamma': 0.99},
                'a2c': {'weight': 0.25, 'gamma': 0.99},
                'ddpg': {'weight': 0.25, 'tau': 0.005, 'gamma': 0.99}
            }
        }
        
        generator = AISignalGenerator(config)
        signals = generator.generate_signals(subset_data, mode='inference')
        
        signal_history.append({
            'timestamp': subset_data['timestamp'].iloc[-1],
            'close_price': subset_data['close'].iloc[-1],
            'signal': signals['signal'],
            'strength': signals['strength'],
            'confidence': signals['confidence']
        })
    
    logger.info(f"Backtest yaratildi: {len(signal_history)} ta signal")
    
    # Analyze signal performance
    buy_signals = [s for s in signal_history if s['signal'] == 'BUY']
    sell_signals = [s for s in signal_history if s['signal'] == 'SELL']
    hold_signals = [s for s in signal_history if s['signal'] == 'HOLD']
    
    logger.info(f"Signal taqsimoti:")
    logger.info(f"  BUY: {len(buy_signals)} ({len(buy_signals)/len(signal_history)*100:.1f}%)")
    logger.info(f"  SELL: {len(sell_signals)} ({len(sell_signals)/len(signal_history)*100:.1f}%)")
    logger.info(f"  HOLD: {len(hold_signals)} ({len(hold_signals)/len(signal_history)*100:.1f}%)")
    
    avg_confidence = np.mean([s['confidence'] for s in signal_history])
    logger.info(f"O'rtacha confidence: {avg_confidence:.4f}")
    
    logger.info("✅ Backtesting Integration test muvaffaqiyatli")
    return signal_history

def run_comprehensive_demo():
    """Comprehensive demo boshqaruvchi"""
    logger.info("🚀 AI Signal Generator RL-based - Comprehensive Demo boshlanmoqda")
    logger.info("=" * 80)
    
    try:
        # 1. Feature Engineering Test
        logger.info("\n1️⃣ FEATURE ENGINEERING TEST")
        features, normalized_features = test_feature_engineering()
        
        # 2. Market Regime Detection Test  
        logger.info("\n2️⃣ MARKET REGIME DETECTION TEST")
        regimes = test_market_regime_detector()
        
        # 3. Individual Agents Test
        logger.info("\n3️⃣ INDIVIDUAL AGENTS TEST")
        agents = test_individual_agents()
        
        # 4. AI Signal Generator Test
        logger.info("\n4️⃣ AI SIGNAL GENERATOR TEST")
        generator, signals, metrics = test_ai_signal_generator()
        
        # 5. Backtesting Integration Test
        logger.info("\n5️⃣ BACKTESTING INTEGRATION TEST")
        backtest_results = test_backtesting_integration()
        
        # Final summary
        logger.info("\n" + "=" * 80)
        logger.info("🎉 COMPREHENSIVE DEMO TUGALLANDI")
        logger.info("=" * 80)
        logger.info("✅ Barcha testlar muvaffaqiyatli o'tkazildi!")
        logger.info("📊 AI Signal Generator tayyor foydalanish uchun")
        logger.info(f"🤖 {len(agents)} ta RL agent ishga tushdi")
        logger.info(f"📈 Joriy signal: {signals['signal']} (confidence: {signals['confidence']:.2f})")
        logger.info(f"💾 Modellar saqlandi va yuklanishga tayyor")
        
        return {
            'features': features,
            'normalized_features': normalized_features,
            'regimes': regimes,
            'agents': agents,
            'generator': generator,
            'signals': signals,
            'metrics': metrics,
            'backtest_results': backtest_results
        }
        
    except Exception as e:
        logger.error(f"❌ Demo xatosi: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Demo-ni ishga tushirish
    results = run_comprehensive_demo()
    
    if results:
        print("\n" + "=" * 50)
        print("🎯 AI Signal Generator - Demo natijalari:")
        print("=" * 50)
        print(f"✅ Feature count: {len(results['features'].columns)}")
        print(f"🤖 Active agents: {len(results['agents'])}")
        print(f"📈 Current signal: {results['signals']['signal']}")
        print(f"📊 Average confidence: {results['metrics'].get('average_confidence', 'N/A')}")
        print(f"🔄 Backtest signals: {len(results['backtest_results'])}")
        print("=" * 50)
        print("Demo muvaffaqiyatli tugallandi! 🚀")
    else:
        print("❌ Demo xatosi yuz berdi")
