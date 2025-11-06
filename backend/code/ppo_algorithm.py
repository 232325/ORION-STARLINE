"""
Proximal Policy Optimization (PPO) Algorithm Implementation
Trading uchun moslashtirilgan PPO algoritmi implementatsiyasi
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Normal
import numpy as np
import gymnasium as gym
from typing import Tuple, List, Dict, Optional, Any
import warnings
warnings.filterwarnings('ignore')


class ActorNetwork(nn.Module):
    """Actor Network - Policy uchun"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [256, 256]):
        super(ActorNetwork, self).__init__()
        
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(nn.Linear(state_dim, hidden_dims[0]))
        
        # Hidden layers with batch normalization and dropout
        for i in range(len(hidden_dims) - 1):
            self.layers.append(nn.Linear(hidden_dims[i], hidden_dims[i + 1]))
            self.layers.append(nn.BatchNorm1d(hidden_dims[i + 1]))
            self.layers.append(nn.Dropout(0.2))
        
        # Output layers for mean and log_std
        self.mean_layer = nn.Linear(hidden_dims[-1], action_dim)
        self.log_std_layer = nn.Linear(hidden_dims[-1], action_dim)
        
        self.initialize_weights()
    
    def initialize_weights(self):
        """Weight initialization"""
        for layer in self.layers:
            if isinstance(layer, nn.Linear):
                nn.init.orthogonal_(layer.weight, gain=np.sqrt(2))
                nn.init.zeros_(layer.bias)
        
        nn.init.orthogonal_(self.mean_layer.weight, gain=0.01)
        nn.init.zeros_(self.mean_layer.bias)
        nn.init.orthogonal_(self.log_std_layer.weight, gain=0.01)
        nn.init.zeros_(self.log_std_layer.bias)
    
    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        Args:
            state: Input state tensor
        Returns:
            mean, log_std: Policy parameters
        """
        x = state
        
        for layer in self.layers:
            x = F.relu(layer(x))
        
        mean = torch.tanh(self.mean_layer(x))
        log_std = self.log_std_layer(x)
        # Clamp log_std to prevent numerical instability
        log_std = torch.clamp(log_std, -20, 2)
        
        return mean, log_std


class CriticNetwork(nn.Module):
    """Critic Network - Value function uchun"""
    
    def __init__(self, state_dim: int, hidden_dims: List[int] = [256, 256]):
        super(CriticNetwork, self).__init__()
        
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(nn.Linear(state_dim, hidden_dims[0]))
        
        # Hidden layers with batch normalization and dropout
        for i in range(len(hidden_dims) - 1):
            self.layers.append(nn.Linear(hidden_dims[i], hidden_dims[i + 1]))
            self.layers.append(nn.BatchNorm1d(hidden_dims[i + 1]))
            self.layers.append(nn.Dropout(0.2))
        
        # Output layer
        self.value_layer = nn.Linear(hidden_dims[-1], 1)
        
        self.initialize_weights()
    
    def initialize_weights(self):
        """Weight initialization"""
        for layer in self.layers:
            if isinstance(layer, nn.Linear):
                nn.init.orthogonal_(layer.weight, gain=np.sqrt(2))
                nn.init.zeros_(layer.bias)
        
        nn.init.orthogonal_(self.value_layer.weight, gain=1.0)
        nn.init.zeros_(self.value_layer.bias)
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        Args:
            state: Input state tensor
        Returns:
            value: Estimated state value
        """
        x = state
        
        for layer in self.layers:
            x = F.relu(layer(x))
        
        value = self.value_layer(x)
        return value


class ReplayBuffer:
    """Experience Replay Buffer"""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = []
        self.position = 0
    
    def push(self, state, action, reward, next_state, done, log_prob):
        """Add experience to buffer"""
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        
        self.buffer[self.position] = (state, action, reward, next_state, done, log_prob)
        self.position = (self.position + 1) % self.capacity
    
    def sample(self, batch_size: int):
        """Sample batch of experiences"""
        batch = np.random.choice(len(self.buffer), batch_size, replace=False)
        states = torch.FloatTensor([self.buffer[i][0] for i in batch])
        actions = torch.FloatTensor([self.buffer[i][1] for i in batch])
        rewards = torch.FloatTensor([self.buffer[i][2] for i in batch])
        next_states = torch.FloatTensor([self.buffer[i][3] for i in batch])
        dones = torch.FloatTensor([self.buffer[i][4] for i in batch])
        log_probs = torch.FloatTensor([self.buffer[i][5] for i in batch])
        
        return states, actions, rewards, next_states, dones, log_probs
    
    def get_all(self):
        """Get all experiences"""
        if len(self.buffer) == 0:
            return None
        
        states = torch.FloatTensor([self.buffer[i][0] for i in range(len(self.buffer))])
        actions = torch.FloatTensor([self.buffer[i][1] for i in range(len(self.buffer))])
        rewards = torch.FloatTensor([self.buffer[i][2] for i in range(len(self.buffer))])
        next_states = torch.FloatTensor([self.buffer[i][3] for i in range(len(self.buffer))])
        dones = torch.FloatTensor([self.buffer[i][4] for i in range(len(self.buffer))])
        log_probs = torch.FloatTensor([self.buffer[i][5] for i in range(len(self.buffer))])
        
        return states, actions, rewards, next_states, dones, log_probs
    
    def __len__(self):
        return len(self.buffer)


class PPOAgent:
    """Proximal Policy Optimization Agent"""
    
    def __init__(self, 
                 state_dim: int,
                 action_dim: int,
                 learning_rate_actor: float = 3e-4,
                 learning_rate_critic: float = 1e-3,
                 clipping_epsilon: float = 0.2,
                 gamma: float = 0.99,
                 gae_lambda: float = 0.95,
                 value_coef: float = 0.5,
                 entropy_coef: float = 0.01,
                 value_clip: float = 0.2,
                 max_grad_norm: float = 0.5,
                 buffer_size: int = 10000,
                 batch_size: int = 64,
                 epochs: int = 10):
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.clipping_epsilon = clipping_epsilon
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.value_clip = value_clip
        self.max_grad_norm = max_grad_norm
        self.batch_size = batch_size
        self.epochs = epochs
        
        # Neural Networks
        self.actor = ActorNetwork(state_dim, action_dim)
        self.critic = CriticNetwork(state_dim)
        
        # Optimizers with adaptive learning rate scheduling
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=learning_rate_actor)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=learning_rate_critic)
        
        # Learning rate schedulers
        self.actor_scheduler = optim.lr_scheduler.StepLR(self.actor_optimizer, step_size=100, gamma=0.95)
        self.critic_scheduler = optim.lr_scheduler.StepLR(self.critic_optimizer, step_size=100, gamma=0.95)
        
        # Replay buffer
        self.buffer = ReplayBuffer(buffer_size)
        
        # Training statistics
        self.training_stats = {
            'actor_loss': [],
            'critic_loss': [],
            'entropy': [],
            'kl_divergence': [],
            'value_loss': []
        }
        
        # Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.actor.to(self.device)
        self.critic.to(self.device)
    
    def select_action(self, state: np.ndarray, deterministic: bool = False) -> Tuple[np.ndarray, float]:
        """
        Select action using current policy
        Args:
            state: Environment state
            deterministic: Whether to use deterministic policy
        Returns:
            action: Selected action
            log_prob: Log probability of action
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            mean, log_std = self.actor(state_tensor)
            
            if deterministic:
                action = mean
            else:
                std = log_std.exp()
                dist = Normal(mean, std)
                action = dist.sample()
            
            log_prob = dist.log_prob(action).sum(dim=-1)
        
        action_np = action.cpu().numpy().squeeze()
        log_prob_np = log_prob.cpu().numpy().item()
        
        return action_np, log_prob_np
    
    def compute_gae(self, rewards: List[float], values: List[float], 
                    next_value: float, dones: List[bool]) -> Tuple[List[float], List[float]]:
        """
        Compute Generalized Advantage Estimation (GAE)
        Args:
            rewards: Episode rewards
            values: State values
            next_value: Next state value
            dones: Episode termination flags
        Returns:
            advantages: Computed advantages
            returns: Computed returns
        """
        advantages = []
        returns = []
        
        # Add next value to the end
        values = values + [next_value]
        
        # Compute GAE
        gae = 0
        for i in reversed(range(len(rewards))):
            if i == len(rewards) - 1:
                next_non_terminal = 1.0 - dones[-1]
                next_values = next_value
            else:
                next_non_terminal = 1.0 - dones[i]
                next_values = values[i + 1]
            
            delta = rewards[i] + self.gamma * next_non_terminal * next_values - values[i]
            gae = delta + self.gamma * self.gae_lambda * next_non_terminal * gae
            advantages.insert(0, gae)
            returns.insert(0, gae + values[i])
        
        return advantages, returns
    
    def update_policy(self):
        """Update policy using PPO algorithm"""
        if len(self.buffer) == 0:
            return
        
        # Get all experiences
        data = self.buffer.get_all()
        if data is None:
            return
        
        states, actions, rewards, next_states, dones, old_log_probs = data
        
        # Move to device
        states = states.to(self.device)
        actions = actions.to(self.device)
        old_log_probs = old_log_probs.to(self.device)
        
        # Compute values for all states
        with torch.no_grad():
            values = self.critic(states).squeeze()
            next_values = self.critic(next_states).squeeze()
        
        # Compute advantages and returns
        rewards = rewards.cpu().numpy().tolist()
        values = values.cpu().numpy().tolist()
        next_values = next_values.cpu().numpy().tolist()
        dones = dones.cpu().numpy().tolist()
        
        advantages, returns = self.compute_gae(rewards, values, next_values[-1], dones)
        
        # Convert to tensors
        advantages = torch.FloatTensor(advantages).to(self.device)
        returns = torch.FloatTensor(returns).to(self.device)
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Update policy for multiple epochs
        for epoch in range(self.epochs):
            # Shuffle indices
            indices = torch.randperm(len(states))
            
            for start_idx in range(0, len(states), self.batch_size):
                end_idx = start_idx + self.batch_size
                batch_indices = indices[start_idx:end_idx]
                
                batch_states = states[batch_indices]
                batch_actions = actions[batch_indices]
                batch_old_log_probs = old_log_probs[batch_indices]
                batch_advantages = advantages[batch_indices]
                batch_returns = returns[batch_indices]
                
                # Forward pass
                mean, log_std = self.actor(batch_states)
                std = log_std.exp()
                dist = Normal(mean, std)
                
                new_log_probs = dist.log_prob(batch_actions).sum(dim=-1)
                entropy = dist.entropy().sum(dim=-1)
                
                # Compute ratio
                ratio = torch.exp(new_log_probs - batch_old_log_probs)
                
                # PPO clipped objective
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1 - self.clipping_epsilon, 1 + self.clipping_epsilon) * batch_advantages
                actor_loss = -torch.min(surr1, surr2).mean()
                
                # Entropy bonus
                actor_loss -= self.entropy_coef * entropy.mean()
                
                # Value function loss
                values_pred = self.critic(batch_states).squeeze()
                value_loss = F.mse_loss(values_pred, batch_returns)
                
                # Value function clipping
                if self.value_clip > 0:
                    values_old = values_pred.detach()
                    values_clipped = values_old + torch.clamp(
                        values_pred - values_old, -self.value_clip, self.value_clip
                    )
                    value_loss_clipped = F.mse_loss(values_clipped, batch_returns)
                    value_loss = torch.max(value_loss, value_loss_clipped)
                
                # Total loss
                total_loss = actor_loss + self.value_coef * value_loss
                
                # Update networks
                self.actor_optimizer.zero_grad()
                self.critic_optimizer.zero_grad()
                
                total_loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)
                torch.nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm)
                
                self.actor_optimizer.step()
                self.critic_optimizer.step()
                
                # Record statistics
                with torch.no_grad():
                    kl_div = (new_log_probs - batch_old_log_probs).mean()
                
                self.training_stats['actor_loss'].append(actor_loss.item())
                self.training_stats['critic_loss'].append(value_loss.item())
                self.training_stats['entropy'].append(entropy.mean().item())
                self.training_stats['kl_divergence'].append(kl_div.item())
                self.training_stats['value_loss'].append(value_loss.item())
    
    def save_model(self, filepath: str):
        """Save model weights"""
        torch.save({
            'actor_state_dict': self.actor.state_dict(),
            'critic_state_dict': self.critic.state_dict(),
            'actor_optimizer_state_dict': self.actor_optimizer.state_dict(),
            'critic_optimizer_state_dict': self.critic_optimizer.state_dict(),
            'training_stats': self.training_stats
        }, filepath)
    
    def load_model(self, filepath: str):
        """Load model weights"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.actor.load_state_dict(checkpoint['actor_state_dict'])
        self.critic.load_state_dict(checkpoint['critic_state_dict'])
        self.actor_optimizer.load_state_dict(checkpoint['actor_optimizer_state_dict'])
        self.critic_optimizer.load_state_dict(checkpoint['critic_optimizer_state_dict'])
        self.training_stats = checkpoint.get('training_stats', self.training_stats)


class TradingEnvironment:
    """Custom Trading Environment for PPO"""
    
    def __init__(self, initial_balance: float = 10000, 
                 transaction_cost: float = 0.001,
                 max_position: float = 100):
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.max_position = max_position
        
        self.reset()
    
    def reset(self):
        """Reset environment"""
        self.balance = self.initial_balance
        self.position = 0.0
        self.portfolio_value = self.initial_balance
        self.trade_history = []
        self.max_drawdown = 0.0
        self.peak_value = self.initial_balance
        
        return self._get_state()
    
    def _get_state(self) -> np.ndarray:
        """Get current state"""
        # Normalize features
        balance_norm = self.balance / self.initial_balance
        position_norm = self.position / self.max_position
        portfolio_norm = self.portfolio_value / self.initial_balance
        drawdown_norm = self.max_drawdown
        
        # Market features (simulate with random values for demo)
        market_price = 100.0  # Simplified
        price_change = np.random.normal(0, 0.02)
        market_momentum = np.random.normal(0, 0.01)
        market_volatility = np.random.normal(0.02, 0.01)
        
        state = np.array([
            balance_norm,
            position_norm,
            portfolio_norm,
            drawdown_norm,
            market_price / 200.0,  # Normalized price
            price_change,
            market_momentum,
            market_volatility
        ])
        
        return state
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute action
        Args:
            action: [position_size, risk_level]
        Returns:
            state, reward, done, info
        """
        # Parse action
        position_size = np.clip(action[0], -1, 1) * self.max_position
        risk_level = np.clip(action[1], 0, 1)
        
        # Simulate market price change
        base_change = np.random.normal(0, 0.02)
        volatility = 0.02 + risk_level * 0.02
        price_change = base_change * (1 + np.random.normal(0, volatility))
        
        # Calculate portfolio value
        old_value = self.portfolio_value
        old_position = self.position
        
        # Update position
        position_diff = position_size - self.position
        transaction_cost = abs(position_diff) * self.transaction_cost
        
        # Update balance
        self.balance -= position_diff + transaction_cost
        
        # Update position
        self.position = position_size
        
        # Calculate new portfolio value
        self.portfolio_value = self.balance + self.position
        
        # Calculate reward
        portfolio_return = (self.portfolio_value - old_value) / old_value
        base_reward = portfolio_return * 100  # Scale reward
        
        # Risk-adjusted reward
        sharpe_ratio = self._calculate_sharpe_ratio()
        risk_adjusted_reward = base_reward * (1 + risk_level * 0.5)
        
        # Drawdown penalty
        if self.portfolio_value > self.peak_value:
            self.peak_value = self.portfolio_value
        
        current_drawdown = (self.peak_value - self.portfolio_value) / self.peak_value
        self.max_drawdown = max(self.max_drawdown, current_drawdown)
        
        drawdown_penalty = -current_drawdown * 10 if current_drawdown > 0.1 else 0
        
        # Total reward
        reward = risk_adjusted_reward + drawdown_penalty
        
        # Record trade
        self.trade_history.append({
            'position': self.position,
            'portfolio_value': self.portfolio_value,
            'return': portfolio_return,
            'drawdown': current_drawdown
        })
        
        # Check termination
        done = (self.portfolio_value < self.initial_balance * 0.5) or (len(self.trade_history) > 1000)
        
        info = {
            'portfolio_value': self.portfolio_value,
            'return': portfolio_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'position': self.position
        }
        
        return self._get_state(), reward, done, info
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio of returns"""
        if len(self.trade_history) < 10:
            return 0.0
        
        returns = [trade['return'] for trade in self.trade_history[-10:]]
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        return mean_return / std_return * np.sqrt(252)  # Annualized


def train_ppo_agent(episodes: int = 1000, max_steps: int = 1000):
    """Train PPO agent for trading"""
    
    # Initialize environment and agent
    env = TradingEnvironment()
    agent = PPOAgent(
        state_dim=8,
        action_dim=2,
        learning_rate_actor=3e-4,
        learning_rate_critic=1e-3,
        clipping_epsilon=0.2,
        gamma=0.99,
        gae_lambda=0.95,
        batch_size=64,
        epochs=10
    )
    
    # Training loop
    episode_rewards = []
    best_reward = float('-inf')
    
    print("PPO Training boshlash...")
    print("=" * 50)
    
    for episode in range(episodes):
        state = env.reset()
        episode_reward = 0
        
        for step in range(max_steps):
            # Select action
            action, log_prob = agent.select_action(state)
            
            # Execute action
            next_state, reward, done, info = env.step(action)
            
            # Store experience
            agent.buffer.push(state, action, reward, next_state, done, log_prob)
            
            state = next_state
            episode_reward += reward
            
            # Update policy periodically
            if len(agent.buffer) >= agent.batch_size * 4:
                agent.update_policy()
            
            if done:
                break
        
        episode_rewards.append(episode_reward)
        
        # Print progress
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            print(f"Episode {episode + 1:4d} | Reward: {episode_reward:8.2f} | "
                  f"Avg(10): {avg_reward:8.2f} | Max: {max(episode_rewards):8.2f}")
            
            # Save best model
            if avg_reward > best_reward:
                best_reward = avg_reward
                agent.save_model(f"code/best_ppo_model.pth")
                print(f"     Yangi eng yaxshi model saqlandi! Reward: {best_reward:.2f}")
        
        # Update learning rate
        agent.actor_scheduler.step()
        agent.critic_scheduler.step()
    
    # Final training stats
    print("\n" + "=" * 50)
    print("Training tugallandi!")
    print(f"Jami episode: {episodes}")
    print(f"Eng yaxshi reward: {max(episode_rewards):.2f}")
    print(f"O'rtacha reward: {np.mean(episode_rewards):.2f}")
    print(f"Oxirgi 100 episodning o'rtacha reward: {np.mean(episode_rewards[-100:]):.2f}")
    
    return agent, episode_rewards


def evaluate_agent(agent: PPOAgent, episodes: int = 10):
    """Evaluate trained agent"""
    env = TradingEnvironment()
    
    evaluation_rewards = []
    portfolio_values = []
    sharpe_ratios = []
    max_drawdowns = []
    
    print("\nAgent evaluation...")
    print("=" * 30)
    
    for episode in range(episodes):
        state = env.reset()
        episode_reward = 0
        
        for step in range(1000):
            # Use deterministic policy for evaluation
            action, _ = agent.select_action(state, deterministic=True)
            state, reward, done, info = env.step(action)
            episode_reward += reward
            
            if done:
                break
        
        evaluation_rewards.append(episode_reward)
        portfolio_values.append(info['portfolio_value'])
        sharpe_ratios.append(info['sharpe_ratio'])
        max_drawdowns.append(info['max_drawdown'])
        
        print(f"Episode {episode + 1:2d} | Reward: {episode_reward:8.2f} | "
              f"Portfolio: ${info['portfolio_value']:8.2f} | "
              f"Sharpe: {info['sharpe_ratio']:6.2f}")
    
    print("\n" + "=" * 30)
    print("Evaluation natijalari:")
    print(f"O'rtacha reward: {np.mean(evaluation_rewards):.2f}")
    print(f"O'rtacha portfolio qiymati: ${np.mean(portfolio_values):.2f}")
    print(f"O'rtacha Sharpe ratio: {np.mean(sharpe_ratios):.2f}")
    print(f"O'rtacha max drawdown: {np.mean(max_drawdowns):.2f}")


if __name__ == "__main__":
    # Training
    trained_agent, rewards = train_ppo_agent(episodes=500)
    
    # Evaluation
    evaluate_agent(trained_agent, episodes=5)
    
    # Save final model
    trained_agent.save_model("code/final_ppo_model.pth")
    print("\nModel saqlandi: code/final_ppo_model.pth")