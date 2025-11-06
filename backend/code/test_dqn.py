"""
DQN Algorithm test va demo fayli

Bu fayl DQN algoritmini test qilish va demo qilish uchun
mo'ljallangan.
"""

import sys
import os
sys.path.append('/workspace/code')

from dqn_algorithm import *
import numpy as np
import matplotlib.pyplot as plt

def test_dqn_components():
    """DQN algoritm komponentlarini test qilish"""
    
    print("=== DQN ALGORITHM TEST ===")
    print("1. Technical Indicators test...")
    
    # Sample data
    prices = np.random.randn(100).cumsum() + 100
    
    # RSI test
    rsi = TechnicalIndicators.calculate_rsi(prices)
    assert len(rsi) == len(prices), "RSI length error"
    assert 0 <= np.min(rsi) <= 100, "RSI range error"
    print("✓ RSI hisoblash ishlaydi")
    
    # MACD test
    macd, signal = TechnicalIndicators.calculate_macd(prices)
    assert len(macd) == len(prices), "MACD length error"
    print("✓ MACD hisoblash ishlaydi")
    
    # Bollinger Bands test
    bb_upper, bb_middle, bb_lower = TechnicalIndicators.calculate_bollinger_bands(prices)
    assert len(bb_upper) == len(prices), "Bollinger Bands length error"
    print("✓ Bollinger Bands hisoblash ishlaydi")
    
    # Features test
    features = MarketFeatures.extract_features(prices)
    assert len(features) > 5, "Features extraction error"
    print(f"✓ {len(features)} ta feature extraction qilindi")
    
    print("\n2. Experience Replay Buffer test...")
    
    # Buffer test
    buffer = ExperienceReplayBuffer(1000)
    buffer.push(prices[:10], 0, 1.0, prices[1:11], False, "TEST")
    buffer.push(prices[:10], 1, -0.5, prices[1:11], True, "TEST")
    
    batch = buffer.sample(2)
    assert len(batch) == 2, "Buffer sampling error"
    print("✓ Experience Replay Buffer ishlaydi")
    
    print("\n3. Neural Network test...")
    
    # Network test
    state_dim = 20
    action_dim = 3
    network = DQNNetwork(state_dim, action_dim)
    
    # Forward pass test
    test_input = torch.randn(5, state_dim)
    output = network(test_input)
    assert output.shape == (5, action_dim), "Network output shape error"
    print("✓ Neural Network ishlaydi")
    
    print("\n4. DQN Agent test...")
    
    # Agent test
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        buffer_capacity=100,
        batch_size=16
    )
    
    # Action selection test
    test_state = np.random.randn(state_dim)
    action = agent.select_action(test_state)
    assert 0 <= action < action_dim, "Action selection error"
    print("✓ DQN Agent action selection ishlaydi")
    
    print("\n5. Trading Environment test...")
    
    # Environment test
    env = TradingEnvironment(
        prices=prices,
        features=features,
        asset_type="TEST"
    )
    
    # Reset test
    initial_state = env.reset()
    actual_state_dim = len(initial_state)
    assert actual_state_dim > 0, "Environment state dimension error"
    print(f"✓ Trading Environment ishlaydi (State dim: {actual_state_dim})")
    
    print("\n=== BARCHA TESTLAR MUVAFFAQIYATLI ===")
    return True

def quick_demo():
    """DQN algoritmi uchun tez demo"""
    
    print("\n=== DQN ALGORITHM DEMO ===")
    
    # Sample data yaratish
    np.random.seed(42)
    prices = np.random.randn(200).cumsum() + 100
    
    # Features extraction
    features = MarketFeatures.extract_features(prices)
    
    # State dimension
    state_dim = 4 + len(features)  # price, change, balance, position + features
    
    # Agent yaratish
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=3,
        buffer_capacity=1000,
        batch_size=16,
        epsilon_start=0.5  # Tezroq convergence uchun
    )
    
    # Environment
    env = TradingEnvironment(
        prices=prices,
        features=features,
        asset_type="DEMO"
    )
    
    # Training (qisqa)
    n_episodes = 10
    episode_rewards = []
    
    print("Training boshlanmoqda...")
    
    for episode in range(n_episodes):
        state = env.reset()
        episode_reward = 0
        done = False
        
        while not done:
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)
            
            agent.buffer.push(state, action, reward, next_state, done, "DEMO")
            loss = agent.train_step()
            
            episode_reward += reward
            state = next_state
        
        episode_rewards.append(episode_reward)
        
        if episode % 10 == 0:
            final_return = (env.get_total_value() - env.initial_balance) / env.initial_balance
            print(f"Episode {episode}: Reward={episode_reward:.2f}, Return={final_return:.4f}")
    
    # Demo natijasi
    avg_reward = np.mean(episode_rewards)
    final_return = (env.get_total_value() - env.initial_balance) / env.initial_balance
    
    print(f"\n=== DEMO NATIJALARI ===")
    print(f"O'rtacha episode reward: {avg_reward:.2f}")
    print(f"Final portfolio return: {final_return:.4f}")
    print(f"Total steps: {len(agent.training_history)}")
    print(f"Epsilon: {agent.epsilon:.4f}")
    
    return True

def main():
    """Test va demo funksiyalari"""
    
    try:
        # Komponentlar testi
        test_dqn_components()
        
        # Tez demo
        quick_demo()
        
        print("\n=== BARCHA TESTLAR MUVAFFAQIYATLI YAKUNLANDI ===")
        print("DQN Algorithm to'liq ishlashga tayyor!")
        
    except Exception as e:
        print(f"Xato yuz berdi: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()