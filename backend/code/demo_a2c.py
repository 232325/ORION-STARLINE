"""
A2C Algorithm Demo Script
========================

Bu script A2C algoritmining asosiy foydalanish namunalarini ko'rsatadi.
"""

from a2c_algorithm import AdvantageA2C, TradingConfig, A2CTrainer
from a2c_config import get_config, PREDEFINED_CONFIGS
import torch
import numpy as np

def demo_basic_usage():
    """Asosiy foydalanish namunosi"""
    print("🚀 A2C Algorithm Asosiy Demo")
    print("=" * 40)
    
    # 1. Konfiguratsiya yaratish
    config = TradingConfig(
        n_assets=10,
        learning_rate=0.0001,
        gamma=0.99,
        max_position=0.25
    )
    
    # 2. Agent yaratish
    agent = AdvantageA2C(config, input_dim=20)
    print(f"✅ Agent yaratildi!")
    print(f"📊 Model parametrlar soni: {sum(p.numel() for p in agent.network.parameters()):,}")
    
    # 3. Sample state yaratish
    batch_size = 2
    seq_len = 60
    input_dim = 20
    
    sample_state = torch.randn(batch_size, seq_len, input_dim)
    print(f"📥 Sample state shape: {sample_state.shape}")
    
    # 4. Forward pass test
    (weights, cash_probs), values = agent.network(sample_state)
    print(f"💼 Portfolio weights shape: {weights.shape}")
    print(f"💵 Cash probabilities shape: {cash_probs.shape}")
    print(f"📈 State values shape: {values.shape}")
    
    # 5. Action selection test
    single_state = sample_state[0:1]
    action, value, log_prob = agent.select_action(single_state, training=True)
    
    print(f"🎯 Selected action shape: {action.shape}")
    print(f"💰 Portfolio weights: {action[:-1].detach().numpy()}")
    print(f"💵 Cash allocation: {action[-1].item():.4f}")
    print(f"🔢 State value: {value.item():.4f}")
    
    return agent

def demo_configurations():
    """Turli konfiguratsiyalar namunosi"""
    print("\n⚙️  Konfiguratsiyalar Demo")
    print("=" * 40)
    
    # Turli strategiya konfiguratsiyalari
    strategies = ['conservative', 'aggressive', 'balanced', 'scalping']
    
    for strategy in strategies:
        config = get_config(strategy)
        print(f"\n📋 {strategy.upper()} Strategy:")
        print(f"   Assets: {config.n_assets}")
        print(f"   Max Position: {config.max_position:.3f}")
        print(f"   Learning Rate: {config.learning_rate}")
        print(f"   Gamma: {config.gamma}")
        print(f"   Hidden Size: {config.hidden_size}")

def demo_training_simple():
    """Qisqa training demo"""
    print("\n🏋️  Training Demo")
    print("=" * 40)
    
    # Konfiguratsiya
    config = get_config('balanced')
    config.learning_rate = 0.001  # Tezroq o'rganish uchun
    
    # Agent yaratish
    agent = AdvantageA2C(config, input_dim=20)
    
    # Simple mock environment
    class SimpleEnv:
        def __init__(self):
            self.state = np.random.randn(20).astype(np.float32)
            self.step_count = 0
            
        def reset(self):
            self.state = np.random.randn(20).astype(np.float32)
            self.step_count = 0
            return self.state
            
        def step(self, action):
            self.step_count += 1
            reward = np.random.normal(0.01, 0.02)  # Random return
            done = self.step_count >= 10
            info = {'market_regime': 'neutral'}
            self.state = np.random.randn(20).astype(np.float32)
            return self.state, reward, done, info
    
    env = SimpleEnv()
    
    # Qisqa training loop
    print("Training qadamlarini boshlaymiz...")
    
    for episode in range(5):
        state = env.reset()
        total_reward = 0
        
        for step in range(10):
            # State ni format qilish (LSTM uchun)
            state_tensor = torch.FloatTensor(state).unsqueeze(0).unsqueeze(0).to(agent.device)
            
            # Action selection
            action, value, log_prob = agent.select_action(state_tensor, training=True)
            
            # Environment step
            next_state, reward, done, info = env.step(action.detach().cpu().numpy())
            
            # Experience yaratish
            experience = type('Experience', (), {
                'state': state_tensor.squeeze(0),
                'action': action.squeeze(0),
                'reward': reward,
                'next_state': torch.FloatTensor(next_state).unsqueeze(0).unsqueeze(0).to(agent.device),
                'done': done,
                'log_prob': log_prob.squeeze(0),
                'value': value.squeeze(0)
            })()
            
            # Network update (bir experience bilan)
            if step == 0:
                prev_experience = experience
            
            if step > 0:
                update_stats = agent.update_network([prev_experience, experience])
                print(f"   Episode {episode}, Step {step}: "
                      f"Loss={update_stats.get('total_loss', 0):.4f}")
                prev_experience = experience
            
            state = next_state
            total_reward += reward
            
            if done:
                break
        
        print(f"✅ Episode {episode}: Total Reward = {total_reward:.4f}")
    
    print("\n🎉 Training demo tugadi!")

def demo_risk_management():
    """Risk management demo"""
    print("\n🛡️  Risk Management Demo")
    print("=" * 40)
    
    from a2c_algorithm import RiskParity, MarketRegimeDetector
    
    # Risk Parity demo
    print("📊 Risk Parity hisoblash:")
    risk_parity = RiskParity(lookback_window=30)
    
    # Mock price data
    asset_names = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    for asset in asset_names:
        prices = 100 * (1 + np.random.normal(0.001, 0.02, 50)).cumprod()
        for price in prices:
            risk_parity.update_prices(asset, price)
    
    weights = risk_parity.calculate_weights(asset_names)
    print(f"   Risk Parity weights: {weights.detach().numpy()}")
    print(f"   Weights sum: {weights.sum().item():.4f}")
    
    # Market Regime Detection demo
    print("\n🌍 Market Regime Detection:")
    regime_detector = MarketRegimeDetector()
    
    # Turli market sharoitlar
    scenarios = {
        'High Volatility': np.random.normal(0, 0.05, 20),
        'Low Volatility': np.random.normal(0, 0.005, 20),
        'Stable Growth': np.random.normal(0.02, 0.01, 20)
    }
    
    for name, returns in scenarios.items():
        regime_detector.update(returns)
        regime = regime_detector.detect_regime()
        print(f"   {name}: {regime}")

def demo_model_save_load():
    """Model saqlash va yuklash demo"""
    print("\n💾 Model Save/Load Demo")
    print("=" * 40)
    
    # Agent yaratish
    config = get_config('balanced')
    agent = AdvantageA2C(config, input_dim=20)
    
    # Sample training stats
    agent.training_stats = {
        'actor_loss': [0.5, 0.3, 0.2],
        'critic_loss': [0.4, 0.25, 0.15],
        'total_loss': [0.9, 0.55, 0.35],
        'returns': [10.5, 12.3, 15.7]
    }
    
    # Model saqlash
    agent.save_model('/workspace/code/demo_model.pth')
    print("✅ Model saqlandi: demo_model.pth")
    
    # Yangi agent yaratish
    new_agent = AdvantageA2C(config, input_dim=20)
    
    # Model yuklash
    new_agent.load_model('/workspace/code/demo_model.pth')
    print("✅ Model yuklandi: demo_model.pth")
    
    # Statslarni tekshirish
    print(f"📈 Yuklangan training stats: {new_agent.training_stats}")
    
    print("💾 Model save/load demo tugadi!")

def main():
    """Demo asosiy funksiyasi"""
    print("🎯 A2C Algorithm To'liq Demo")
    print("=" * 50)
    
    try:
        # Asosiy foydalanish
        agent = demo_basic_usage()
        
        # Konfiguratsiyalar
        demo_configurations()
        
        # Training demo (qisqa)
        demo_training_simple()
        
        # Risk management
        demo_risk_management()
        
        # Model save/load
        demo_model_save_load()
        
        print("\n🎉 Barcha demo namunalar muvaffaqiyatli tugallandi!")
        print("\n📚 A2C Algorithm xususiyatlari:")
        print("✅ Actor-Critic Architecture")
        print("✅ Advantage Function (GAE)")
        print("✅ Multi-Asset Portfolio Allocation") 
        print("✅ Risk Parity & Market Regime Detection")
        print("✅ LSTM Sequence Modeling")
        print("✅ Reward Shaping for Trading")
        print("✅ Gradient Clipping & Entropy Regularization")
        print("✅ Model Save/Load functionality")
        
    except Exception as e:
        print(f"❌ Demo xatolik: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()