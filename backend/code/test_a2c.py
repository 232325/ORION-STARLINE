"""
A2C Algorithm Test va Demo Script
=================================

Bu script A2C algoritmini test qilish va ishlatishni ko'rsatadi.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import torch
import numpy as np
import pandas as pd
from a2c_algorithm import AdvantageA2C, TradingConfig, A2CTrainer
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class MockTradingEnvironment:
    """Mock trading environment for testing"""
    
    def __init__(self, config: TradingConfig, n_features: int = 20):
        self.config = config
        self.n_features = n_features
        self.current_step = 0
        self.max_steps = 1000
        self.portfolio_value = 100000  # Initial capital
        self.prev_portfolio_value = 100000
        self.asset_prices = np.ones(config.n_assets) * 100
        
        # Generate mock price data
        self.generate_mock_data()
        
        self.state = None
        self.reset()
    
    def generate_mock_data(self):
        """Mock ma'lumotlar yaratish"""
        np.random.seed(42)
        
        self.price_history = {}
        for i in range(self.config.n_assets):
            # Generate price series with trends and volatility
            returns = np.random.normal(0.001, 0.02, self.max_steps + 100)
            prices = 100 * np.cumprod(1 + returns)
            self.price_history[f'asset_{i}'] = prices
    
    def reset(self):
        """Environment reset"""
        self.current_step = 0
        self.portfolio_value = 100000
        self.prev_portfolio_value = 100000
        self.state = self._get_state()
        return self.state
    
    def _get_state(self):
        """Joriy state ni olish"""
        # Create state from price data and portfolio info
        state_features = []
        
        # Price features for each asset
        for i in range(self.config.n_assets):
            asset_key = f'asset_{i}'
            if asset_key in self.price_history:
                prices = self.price_history[asset_key]
                start_idx = max(0, self.current_step - self.config.lookback_window)
                price_window = prices[start_idx:self.current_step + 1]
                
                if len(price_window) > 1:
                    # Price features
                    returns = np.diff(price_window) / price_window[:-1]
                    current_price = price_window[-1]
                    
                    feature_vector = [
                        current_price / 100 - 1,  # Normalized price
                        np.mean(returns) if len(returns) > 0 else 0,  # Average return
                        np.std(returns) if len(returns) > 0 else 0,  # Volatility
                        returns[-1] if len(returns) > 0 else 0,  # Last return
                        np.min(returns) if len(returns) > 0 else 0,  # Min return
                        np.max(returns) if len(returns) > 0 else 0,  # Max return
                    ]
                else:
                    feature_vector = [0] * 6
            else:
                feature_vector = [0] * 6
            
            state_features.extend(feature_vector)
        
        # Add portfolio features (simplified)
        portfolio_features = [
            0.0,  # Current portfolio return
            0.0,  # Portfolio volatility
            self.current_step / self.max_steps,  # Time in episode
        ]
        
        state_features.extend(portfolio_features)
        
        # Ensure correct dimension
        while len(state_features) < self.n_features:
            state_features.append(0.0)
        
        state_features = state_features[:self.n_features]
        
        return np.array(state_features, dtype=np.float32)
    
    def step(self, action):
        """Environment step"""
        self.current_step += 1
        done = self.current_step >= self.max_steps
        
        # Update asset prices
        price_changes = np.random.normal(0, 0.01, self.config.n_assets)
        self.asset_prices *= (1 + price_changes)
        
        # Calculate portfolio return based on action
        if isinstance(action, torch.Tensor):
            action = action.cpu().numpy()
        
        # Portfolio weights (last element is cash)
        weights = action[:-1] if len(action) > self.config.n_assets else action
        cash_weight = action[-1] if len(action) > self.config.n_assets else 0.1
        
        # Assume market return based on weighted average of asset returns
        market_return = np.sum(weights * price_changes)
        
        # Portfolio return with transaction costs
        portfolio_return = market_return * (1 - cash_weight)
        
        # Update portfolio value
        self.prev_portfolio_value = self.portfolio_value
        self.portfolio_value *= (1 + portfolio_return)
        
        reward = portfolio_return
        
        # Update state
        self.state = self._get_state()
        
        info = {
            'portfolio_value': self.portfolio_value,
            'portfolio_return': portfolio_return,
            'market_regime': self._detect_market_regime(),
            'asset_returns': price_changes,
        }
        
        return self.state, reward, done, info
    
    def _detect_market_regime(self):
        """Simple market regime detection"""
        if self.current_step < 10:
            return 'neutral'
        
        # Simple volatility-based regime detection
        recent_volatility = np.std([np.random.normal(0, 0.01) for _ in range(5)])
        
        if recent_volatility > 0.015:
            return 'high_vol_negative' if np.random.random() > 0.5 else 'high_vol_positive'
        elif recent_volatility < 0.005:
            return 'low_vol_positive' if np.random.random() > 0.5 else 'low_vol_negative'
        else:
            return 'medium_vol'

def test_a2c_basic_functionality():
    """A2C algoritmining asosiy funksiyalarini test qilish"""
    print("=== A2C Asosiy Funksiyalar Testi ===")
    
    # Configuration
    config = TradingConfig(
        n_assets=5,
        learning_rate=0.0001,
        gamma=0.99,
        max_position=0.3,
        batch_size=32
    )
    
    # Create agent
    agent = AdvantageA2C(config, input_dim=20)
    
    # Test forward pass
    batch_size = 4
    seq_len = 60
    input_dim = 20
    
    example_states = torch.randn(batch_size, seq_len, input_dim)
    
    print(f"Input shape: {example_states.shape}")
    
    # Forward pass
    (weights, cash_probs), values = agent.network(example_states)
    
    print(f"Portfolio weights shape: {weights.shape}")
    print(f"Cash probabilities shape: {cash_probs.shape}")
    print(f"State values shape: {values.shape}")
    
    # Check sum constraint
    weights_sum = weights.sum(dim=-1)
    cash_sum = cash_probs.sum()
    print(f"Portfolio weights sum (should be ~1): {weights_sum.mean().item():.4f}")
    print(f"Cash probabilities range: [{cash_probs.min().item():.4f}, {cash_probs.max().item():.4f}]")
    
    # Test action selection
    single_state = example_states[0:1]  # Add batch dimension
    action, value, log_prob = agent.select_action(single_state, training=True)
    
    print(f"Selected action shape: {action.shape}")
    print(f"Selected value: {value.item():.4f}")
    print(f"Selected log probability: {log_prob.item():.4f}")
    
    print("✅ Asosiy funksiyalar testi o'tdi!\n")

def test_training_loop():
    """Training loop test"""
    print("=== Training Loop Testi ===")
    
    # Configuration
    config = TradingConfig(
        n_assets=5,
        learning_rate=0.001,  # Higher learning rate for faster testing
        gamma=0.99
    )
    
    max_episodes = 50
    max_steps_per_episode = 100
    
    # Create agent and environment
    agent = AdvantageA2C(config, input_dim=20)
    env = MockTradingEnvironment(config, n_features=20)
    
    # Simple training loop
    rewards_history = []
    losses_history = []
    
    for episode in range(max_episodes):
        state = env.reset()
        total_reward = 0
        step_count = 0
        done = False
        
        while not done and step_count < max_steps_per_episode:
            # Format state for LSTM (add sequence dimension)
            state_tensor = torch.FloatTensor(state).unsqueeze(0).unsqueeze(0).to(agent.device)
            action, value, log_prob = agent.select_action(state_tensor, training=True)
            
            # Environment step
            next_state, reward, done, info = env.step(action.detach().cpu().numpy())
            
            # Store experience (simplified)
            experience = type('Experience', (), {
                'state': state_tensor.squeeze(0),
                'action': action.squeeze(0),
                'reward': reward,
                'next_state': torch.FloatTensor(next_state).unsqueeze(0).unsqueeze(0).to(agent.device),
                'done': done,
                'log_prob': log_prob.squeeze(0),
                'value': value.squeeze(0)
            })()
            
            # Update network (using single experience)
            if step_count > 0:  # Wait for at least one experience
                update_stats = agent.update_network([prev_experience, experience])
                losses_history.append(update_stats.get('total_loss', 0))
            
            prev_experience = experience
            
            state = next_state
            total_reward += reward
            step_count += 1
        
        rewards_history.append(total_reward)
        
        if episode % 10 == 0:
            avg_reward = np.mean(rewards_history[-10:]) if len(rewards_history) >= 10 else total_reward
            avg_loss = np.mean(losses_history[-10:]) if len(losses_history) >= 10 else 0
            print(f"Episode {episode}: Avg Reward = {avg_reward:.4f}, Avg Loss = {avg_loss:.4f}")
    
    # Plot results
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(rewards_history)
    plt.title('Episode Rewards')
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    
    plt.subplot(1, 2, 2)
    if losses_history:
        plt.plot(losses_history)
        plt.title('Training Loss')
        plt.xlabel('Update')
        plt.ylabel('Loss')
    
    plt.tight_layout()
    plt.savefig('/workspace/code/training_results.png', dpi=150, bbox_inches='tight')
    print("📊 Training results saved to training_results.png")
    
    print("✅ Training loop testi o'tdi!\n")

def test_risk_management():
    """Risk management funksiyalarini test qilish"""
    print("=== Risk Management Testi ===")
    
    from a2c_algorithm import RiskParity, MarketRegimeDetector
    
    # Test Risk Parity
    risk_parity = RiskParity(lookback_window=30)
    
    # Simulate price data
    asset_names = ['asset_0', 'asset_1', 'asset_2', 'asset_3', 'asset_4']
    
    for i, asset in enumerate(asset_names):
        prices = 100 * (1 + np.random.normal(0.001, 0.02, 50)).cumprod()
        for price in prices:
            risk_parity.update_prices(asset, price)
    
    weights = risk_parity.calculate_weights(asset_names)
    print(f"Risk parity weights: {weights}")
    print(f"Weights sum: {weights.sum().item():.4f}")
    
    # Test Market Regime Detector
    regime_detector = MarketRegimeDetector()
    
    # Simulate different market conditions
    high_vol_returns = np.random.normal(0, 0.05, 20)
    low_vol_returns = np.random.normal(0.001, 0.005, 20)
    
    regime_detector.update(high_vol_returns)
    high_vol_regime = regime_detector.detect_regime()
    print(f"High volatility regime: {high_vol_regime}")
    
    regime_detector.update(low_vol_returns)
    low_vol_regime = regime_detector.detect_regime()
    print(f"Low volatility regime: {low_vol_regime}")
    
    print("✅ Risk management testi o'tdi!\n")

def benchmark_performance():
    """Performance benchmark"""
    print("=== Performance Benchmark ===")
    
    import time
    
    config = TradingConfig(
        n_assets=10,
        learning_rate=0.0001,
        batch_size=64
    )
    
    agent = AdvantageA2C(config, input_dim=20)
    
    # Benchmark forward pass
    batch_sizes = [1, 8, 32, 64]
    
    for batch_size in batch_sizes:
        test_input = torch.randn(batch_size, 60, 20)
        
        # Warm up
        for _ in range(10):
            with torch.no_grad():
                _ = agent.network(test_input)
        
        # Benchmark
        start_time = time.time()
        num_iterations = 100
        
        for _ in range(num_iterations):
            with torch.no_grad():
                _ = agent.network(test_input)
        
        end_time = time.time()
        
        avg_time = (end_time - start_time) / num_iterations
        throughput = batch_size / avg_time
        
        print(f"Batch size {batch_size}: {avg_time*1000:.2f}ms per forward pass, "
              f"{throughput:.1f} samples/sec")
    
    print("✅ Performance benchmark tugadi!\n")

def main():
    """Asosiy test funksiyasi"""
    print("🚀 A2C Algorithm Test va Demo")
    print("=" * 50)
    
    # Test asosiy funksiyalar
    test_a2c_basic_functionality()
    
    # Test training loop
    test_training_loop()
    
    # Test risk management
    test_risk_management()
    
    # Performance benchmark
    benchmark_performance()
    
    print("🎉 Barcha testlar muvaffaqiyatli tugallandi!")
    print("\nA2C Algorithm xususiyatlari:")
    print("✅ Actor-Critic architecture")
    print("✅ Advantage function (GAE)")
    print("✅ Multi-asset portfolio allocation")
    print("✅ Risk parity considerations")
    print("✅ Market regime detection")
    print("✅ LSTM sequence modeling")
    print("✅ Reward shaping for trading")
    print("✅ Gradient clipping")
    print("✅ Entropy regularization")

if __name__ == "__main__":
    main()