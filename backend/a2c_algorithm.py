"""
Advantage Actor-Critic (A2C) Algorithm for Multi-Asset Trading
=============================================================

Bu modul A2C algoritmini multi-asset trading uchun implement qiladi.
Asosiy xususiyatlari:
- Actor-Critic architecture
- Advantage function
- Multi-asset portfolio allocation
- Risk management
- LSTM sequence modeling
- Reward shaping
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from collections import deque
import math
import logging
from dataclasses import dataclass
from torch.distributions import MultivariateNormal, Categorical
import warnings
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradingConfig:
    """A2C Trading konfiguratsiyasi"""
    n_assets: int = 10
    max_position: float = 0.2
    transaction_cost: float = 0.001
    slippage: float = 0.0005
    max_drawdown: float = 0.15
    risk_free_rate: float = 0.02
    lookback_window: int = 60
    hidden_size: int = 256
    lstm_layers: int = 2
    learning_rate: float = 0.0001
    gamma: float = 0.99
    beta_entropy: float = 0.01
    value_loss_coef: float = 0.5
    max_grad_norm: float = 0.5
    n_steps: int = 5
    n_workers: int = 1
    batch_size: int = 32

@dataclass
class Experience:
    """Transition experience structure"""
    state: torch.Tensor
    action: torch.Tensor
    reward: float
    next_state: torch.Tensor
    done: bool
    log_prob: torch.Tensor
    value: torch.Tensor

class RiskParity:
    """Risk Parity hisoblash klassi"""
    
    def __init__(self, lookback_window: int = 60):
        self.lookback_window = lookback_window
        self.price_history = {}
        
    def update_prices(self, asset_name: str, price: float):
        """Asset narx tarixini yangilash"""
        if asset_name not in self.price_history:
            self.price_history[asset_name] = deque(maxlen=self.lookback_window)
        self.price_history[asset_name].append(price)
    
    def calculate_weights(self, asset_names: List[str]) -> torch.Tensor:
        """Risk parity vaznlarini hisoblash"""
        if len(asset_names) == 0:
            return torch.tensor([])
        
        returns_data = []
        valid_assets = []
        
        for asset in asset_names:
            if asset in self.price_history and len(self.price_history[asset]) >= 2:
                prices = np.array(self.price_history[asset])
                if len(prices) > 1:
                    returns = np.diff(prices) / prices[:-1]
                    returns_data.append(returns)
                    valid_assets.append(asset)
        
        if len(returns_data) < 2:
            # Bir xil vaznlar
            n_assets = len(asset_names)
            weights = torch.ones(n_assets) / n_assets
        else:
            returns_matrix = np.array(returns_data).T
            if returns_matrix.shape[0] > 1:
                cov_matrix = np.cov(returns_matrix.T)
                n_assets = len(valid_assets)
                
                # Risk parity weights
                inv_vol = 1.0 / (np.diag(cov_matrix) + 1e-8)
                weights_raw = inv_vol / np.sum(inv_vol)
                
                # Barcha assetlar uchun vazn yaratish
                weights = torch.zeros(len(asset_names))
                for i, asset in enumerate(valid_assets):
                    asset_idx = asset_names.index(asset)
                    weights[asset_idx] = weights_raw[i]
        
        return weights

class MarketRegimeDetector:
    """Bozor rejimini aniqlash klassi"""
    
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.volatility_history = deque(maxlen=window_size)
        self.return_history = deque(maxlen=window_size)
        
    def update(self, returns: np.ndarray):
        """Volatiliti va returnlarni yangilash"""
        if len(returns) > 0:
            vol = np.std(returns)
            total_return = np.sum(returns)
            
            self.volatility_history.append(vol)
            self.return_history.append(total_return)
    
    def detect_regime(self) -> str:
        """Joriy bozor rejimini aniqlash"""
        if len(self.volatility_history) < self.window_size // 2:
            return "neutral"
        
        recent_vol = np.mean(list(self.volatility_history)[-5:])
        recent_return = np.mean(list(self.return_history)[-5:])
        
        if recent_vol > np.percentile(list(self.volatility_history), 75):
            if recent_return > 0:
                return "high_vol_positive"
            else:
                return "high_vol_negative"
        elif recent_vol < np.percentile(list(self.volatility_history), 25):
            if recent_return > 0:
                return "low_vol_positive"
            else:
                return "low_vol_negative"
        else:
            return "medium_vol"

class SharedFeatureExtractor(nn.Module):
    """Umumiy feature extractor"""
    
    def __init__(self, input_dim: int, hidden_size: int, lstm_layers: int = 2):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_size = hidden_size
        self.lstm_layers = lstm_layers
        
        # LSTM for sequence modeling
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_size,
            num_layers=lstm_layers,
            batch_first=True,
            dropout=0.1
        )
        
        # Feature processing layers
        self.dense1 = nn.Linear(hidden_size, hidden_size)
        self.dense2 = nn.Linear(hidden_size, hidden_size // 2)
        self.dropout = nn.Dropout(0.2)
        self.batch_norm1 = nn.BatchNorm1d(hidden_size)
        self.batch_norm2 = nn.BatchNorm1d(hidden_size // 2)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: [batch_size, seq_len, input_dim]
        
        Returns:
            [batch_size, hidden_size // 2]
        """
        batch_size, seq_len, _ = x.shape
        
        # LSTM processing
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Take the last hidden state
        last_hidden = lstm_out[:, -1, :]  # [batch_size, hidden_size]
        
        # Dense layers with batch normalization (handle single samples)
        x = self.dense1(last_hidden)
        if x.size(0) > 1:
            x = self.batch_norm1(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        x = self.dense2(x)
        if x.size(0) > 1:
            x = self.batch_norm2(x)
        x = F.relu(x)
        
        return x

class ActorHead(nn.Module):
    """Actor head - action probabilities"""
    
    def __init__(self, input_dim: int, n_assets: int, max_position: float):
        super().__init__()
        self.n_assets = n_assets
        self.max_position = max_position
        
        self.dense1 = nn.Linear(input_dim, input_dim // 2)
        self.dense2 = nn.Linear(input_dim // 2, input_dim // 4)
        self.dropout = nn.Dropout(0.2)
        
        # Portfolio weights output (normalized)
        self.weight_head = nn.Linear(input_dim // 4, n_assets)
        
        # Cash allocation (0 to 1)
        self.cash_head = nn.Linear(input_dim // 4, 1)
        
        # Batch normalization
        self.batch_norm1 = nn.BatchNorm1d(input_dim // 2)
        self.batch_norm2 = nn.BatchNorm1d(input_dim // 4)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: [batch_size, input_dim]
        
        Returns:
            weights: [batch_size, n_assets] - portfolio weights
            cash_allocation: [batch_size, 1] - cash allocation
        """
        # Dense layers with batch normalization (handle single samples)
        x = self.dense1(x)
        if x.size(0) > 1:
            x = self.batch_norm1(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        x = self.dense2(x)
        if x.size(0) > 1:
            x = self.batch_norm2(x)
        x = F.relu(x)
        
        # Output layers
        weights_logits = self.weight_head(x)  # [batch_size, n_assets]
        cash_logits = self.cash_head(x).squeeze(-1)  # [batch_size]
        
        # Convert to probabilities using softmax
        weights = F.softmax(weights_logits, dim=-1)
        cash_prob = torch.sigmoid(cash_logits)  # 0-1 cash allocation
        
        # Normalize weights considering cash allocation
        stock_allocation = (1 - cash_prob).unsqueeze(-1) * weights
        stock_allocation = stock_allocation / (stock_allocation.sum(-1, keepdim=True) + 1e-8)
        
        return stock_allocation, cash_prob

class CriticHead(nn.Module):
    """Critic head - state value estimates"""
    
    def __init__(self, input_dim: int):
        super().__init__()
        self.dense1 = nn.Linear(input_dim, input_dim // 2)
        self.dense2 = nn.Linear(input_dim // 2, input_dim // 4)
        self.value_head = nn.Linear(input_dim // 4, 1)
        
        self.dropout = nn.Dropout(0.2)
        self.batch_norm1 = nn.BatchNorm1d(input_dim // 2)
        self.batch_norm2 = nn.BatchNorm1d(input_dim // 4)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: [batch_size, input_dim]
        
        Returns:
            value: [batch_size, 1] - state value
        """
        # Dense layers with batch normalization (handle single samples)
        x = self.dense1(x)
        if x.size(0) > 1:
            x = self.batch_norm1(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        x = self.dense2(x)
        if x.size(0) > 1:
            x = self.batch_norm2(x)
        x = F.relu(x)
        
        value = self.value_head(x)
        
        return value

class A2CNetwork(nn.Module):
    """A2C Network - Actor-Critic Architecture"""
    
    def __init__(self, config: TradingConfig, input_dim: int):
        super().__init__()
        self.config = config
        self.input_dim = input_dim
        
        # Shared feature extractor
        self.feature_extractor = SharedFeatureExtractor(
            input_dim=input_dim,
            hidden_size=config.hidden_size,
            lstm_layers=config.lstm_layers
        )
        
        # Actor and Critic heads
        self.actor = ActorHead(
            input_dim=config.hidden_size // 2,
            n_assets=config.n_assets,
            max_position=config.max_position
        )
        
        self.critic = CriticHead(input_dim=config.hidden_size // 2)
        
    def forward(self, x: torch.Tensor) -> Tuple[Tuple[torch.Tensor, torch.Tensor], torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: [batch_size, seq_len, input_dim]
        
        Returns:
            (weights, cash_prob), value
        """
        # Extract features
        features = self.feature_extractor(x)
        
        # Actor and Critic
        weights, cash_prob = self.actor(features)
        value = self.critic(features)
        
        return (weights, cash_prob), value

class AdvantageA2C:
    """A2C Agent for Multi-Asset Trading"""
    
    def __init__(self, config: TradingConfig, input_dim: int):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Network
        self.network = A2CNetwork(config, input_dim).to(self.device)
        
        # Optimizer
        self.optimizer = optim.Adam(
            self.network.parameters(),
            lr=config.learning_rate,
            eps=1e-5
        )
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.StepLR(
            self.optimizer,
            step_size=1000,
            gamma=0.95
        )
        
        # Risk management
        self.risk_parity = RiskParity(config.lookback_window)
        self.regime_detector = MarketRegimeDetector()
        
        # Experience buffer
        self.experience_buffer = deque(maxlen=config.n_steps)
        
        # Training statistics
        self.training_stats = {
            'actor_loss': [],
            'critic_loss': [],
            'total_loss': [],
            'returns': [],
            'entropy': [],
            'advantages': []
        }
        
        logger.info("A2C Agent initialized successfully")
    
    def calculate_advantage(self, rewards: List[float], values: List[torch.Tensor], 
                          dones: List[bool], next_value: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Advantage function hisoblash (GAE)"""
        advantages = []
        advantage = 0
        
        # Reverse iteration for GAE
        for i in reversed(range(len(rewards))):
            if i == len(rewards) - 1:
                next_non_terminal = 1.0 - dones[i]
                next_val = next_value
            else:
                next_non_terminal = 1.0 - dones[i]
                next_val = values[i + 1]
            
            # Delta calculation
            delta = rewards[i] + self.config.gamma * next_val * next_non_terminal - values[i]
            
            # GAE advantage
            advantage = delta + self.config.gamma * self.config.gamma * next_non_terminal * advantage
            advantages.insert(0, advantage)
        
        advantages = torch.stack(advantages).to(self.device)
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Returns = advantages + values
        returns = advantages + torch.stack(values).squeeze(-1)
        
        return advantages.detach(), returns.detach()
    
    def calculate_reward(self, portfolio_return: float, action: torch.Tensor, 
                        prev_action: torch.Tensor, market_regime: str) -> float:
        """Reward shaping for financial markets"""
        base_reward = portfolio_return * 100  # Scale up for stability
        
        # Transaction cost penalty
        if prev_action is not None:
            action_diff = torch.abs(action - prev_action).sum()
            transaction_penalty = -action_diff * self.config.transaction_cost * 100
            base_reward += transaction_penalty
        
        # Risk penalty based on drawdown
        # (This would typically use actual portfolio value history)
        risk_penalty = 0
        
        # Market regime adjustment
        regime_multiplier = {
            'high_vol_positive': 1.2,
            'high_vol_negative': 0.8,
            'low_vol_positive': 1.1,
            'low_vol_negative': 0.9,
            'medium_vol': 1.0,
            'neutral': 1.0
        }.get(market_regime, 1.0)
        
        final_reward = base_reward * regime_multiplier - risk_penalty
        
        return final_reward
    
    def select_action(self, state: torch.Tensor, training: bool = True) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Action selection"""
        self.network.eval() if not training else self.network.train()
        
        with torch.no_grad() if not training else torch.enable_grad():
            (weights, cash_prob), value = self.network(state)
            
            # Sample action
            if training:
                # Add noise for exploration
                noise = torch.randn_like(weights) * 0.1
                weights = F.softmax(weights + noise, dim=-1)
                cash_prob = torch.sigmoid(torch.logit(cash_prob) + torch.randn_like(cash_prob) * 0.1)
            
            # Convert to actual allocations
            stock_weights = (1 - cash_prob.unsqueeze(-1)) * weights
            cash_weight = cash_prob.unsqueeze(-1)
            action = torch.cat([stock_weights, cash_weight], dim=-1)
            
            # Log probabilities
            log_probs = torch.log(weights + 1e-8).sum(-1) + torch.log(cash_prob + 1e-8)
            
            return action.squeeze(0), value.squeeze(0), log_probs.squeeze(0)
    
    def update_network(self, experiences: List[Experience]) -> Dict[str, float]:
        """Network update with gradient clipping"""
        if len(experiences) == 0:
            return {'loss': 0.0}
        
        states = torch.stack([exp.state for exp in experiences])
        actions = torch.stack([exp.action for exp in experiences])
        rewards = [exp.reward for exp in experiences]
        next_states = torch.stack([exp.next_state for exp in experiences])
        dones = [exp.done for exp in experiences]
        old_log_probs = torch.stack([exp.log_prob for exp in experiences])
        old_values = torch.stack([exp.value for exp in experiences])
        
        # Forward pass
        (weights, cash_probs), values = self.network(states)
        _, next_values = self.network(next_states)
        
        # Calculate advantages and returns
        advantages, returns = self.calculate_advantage(
            rewards, old_values, dones, next_values.squeeze(-1)
        )
        
        # Current log probabilities
        stock_weights = (1 - cash_probs.squeeze(-1)) * weights
        current_log_probs = torch.log(stock_weights + 1e-8).sum(-1) + \
                           torch.log(cash_probs.squeeze(-1) + 1e-8)
        
        # Policy loss (Actor loss)
        ratio = torch.exp(current_log_probs - old_log_probs)
        policy_loss = -torch.mean(torch.min(
            ratio * advantages,
            torch.clamp(ratio, 1 - 0.2, 1 + 0.2) * advantages
        ))
        
        # Value loss (Critic loss)
        value_loss = F.mse_loss(values.squeeze(-1), returns)
        
        # Entropy bonus
        entropy_bonus = -torch.mean(torch.sum(stock_weights * torch.log(stock_weights + 1e-8), dim=-1))
        
        # Total loss
        total_loss = (
            policy_loss + 
            self.config.value_loss_coef * value_loss - 
            self.config.beta_entropy * entropy_bonus
        )
        
        # Update network
        self.optimizer.zero_grad()
        total_loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.network.parameters(), self.config.max_grad_norm)
        
        self.optimizer.step()
        self.scheduler.step()
        
        # Update statistics
        self.training_stats['actor_loss'].append(policy_loss.item())
        self.training_stats['critic_loss'].append(value_loss.item())
        self.training_stats['total_loss'].append(total_loss.item())
        self.training_stats['entropy'].append(entropy_bonus.item())
        self.training_stats['advantages'].append(advantages.mean().item())
        
        return {
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'total_loss': total_loss.item(),
            'entropy': entropy_bonus.item(),
            'advantages_mean': advantages.mean().item()
        }
    
    def save_model(self, filepath: str):
        """Model saqlash"""
        checkpoint = {
            'network_state_dict': self.network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'config': self.config,
            'training_stats': self.training_stats
        }
        torch.save(checkpoint, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Model yuklash"""
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.network.load_state_dict(checkpoint['network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        if 'training_stats' in checkpoint:
            self.training_stats = checkpoint['training_stats']
        
        logger.info(f"Model loaded from {filepath}")

class A2CTrainer:
    """A2C Training manager"""
    
    def __init__(self, agent: AdvantageA2C):
        self.agent = agent
        self.episode_count = 0
        
    def train_episode(self, env, max_steps: int = 1000) -> Dict[str, float]:
        """Bitta episode training"""
        state = env.reset()
        total_reward = 0
        experiences = []
        prev_action = None
        
        for step in range(max_steps):
            # Select action
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            action, value, log_prob = self.agent.select_action(state_tensor, training=True)
            
            # Execute action in environment
            next_state, reward, done, info = env.step(action.cpu().numpy())
            
            # Calculate shaped reward
            market_regime = info.get('market_regime', 'neutral')
            shaped_reward = self.agent.calculate_reward(
                reward, action, prev_action, market_regime
            )
            
            # Store experience
            experience = Experience(
                state=state_tensor.squeeze(0),
                action=action.squeeze(0),
                reward=shaped_reward,
                next_state=torch.FloatTensor(next_state).to(self.device),
                done=done,
                log_prob=log_prob.squeeze(0),
                value=value.squeeze(0)
            )
            
            experiences.append(experience)
            total_reward += reward
            
            state = next_state
            prev_action = action.clone()
            
            if done or step == max_steps - 1:
                break
        
        # Update network
        if len(experiences) > 0:
            update_stats = self.agent.update_network(experiences)
            update_stats['episode_reward'] = total_reward
            update_stats['episode_length'] = len(experiences)
            
            self.agent.training_stats['returns'].append(total_reward)
            
            return update_stats
        
        return {'episode_reward': 0, 'episode_length': 0}
    
    def train(self, env, num_episodes: int, eval_env=None, save_interval: int = 100):
        """To'liq training process"""
        logger.info(f"Training started for {num_episodes} episodes")
        
        best_return = -float('inf')
        eval_returns = []
        
        for episode in range(num_episodes):
            # Train episode
            stats = self.train_episode(env)
            
            self.episode_count = episode + 1
            
            # Logging
            if episode % 10 == 0:
                logger.info(f"Episode {episode}: "
                          f"Reward={stats['episode_reward']:.2f}, "
                          f"Length={stats['episode_length']}, "
                          f"Policy Loss={stats['policy_loss']:.4f}, "
                          f"Value Loss={stats['value_loss']:.4f}")
            
            # Evaluation
            if eval_env is not None and episode % eval_interval == 0:
                eval_return = self.evaluate(eval_env)
                eval_returns.append(eval_return)
                logger.info(f"Episode {episode}: Eval Return={eval_return:.2f}")
                
                if eval_return > best_return:
                    best_return = eval_return
                    self.agent.save_model(f"best_model_episode_{episode}.pth")
            
            # Save checkpoint
            if episode % save_interval == 0:
                self.agent.save_model(f"checkpoint_episode_{episode}.pth")
        
        logger.info(f"Training completed. Best return: {best_return:.2f}")
        return eval_returns
    
    def evaluate(self, env, num_episodes: int = 10) -> float:
        """Evaluation"""
        returns = []
        
        for _ in range(num_episodes):
            state = env.reset()
            total_return = 0
            done = False
            
            while not done:
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                action, _, _ = self.agent.select_action(state_tensor, training=False)
                
                state, reward, done, _ = env.step(action.cpu().numpy())
                total_return += reward
            
            returns.append(total_return)
        
        return np.mean(returns)

# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = TradingConfig(
        n_assets=5,
        learning_rate=0.0001,
        gamma=0.99,
        max_position=0.3
    )
    
    # Create agent
    agent = AdvantageA2C(config, input_dim=20)  # 20 features per asset
    
    print("A2C Agent muvaffaqiyatli yaratildi!")
    print(f"Model parameters: {sum(p.numel() for p in agent.network.parameters()):,}")
    
    # Example state (batch_size=1, seq_len=60, features=20)
    example_state = torch.randn(1, 60, 20)
    
    # Test forward pass
    with torch.no_grad():
        (weights, cash), value = agent.network(example_state)
    
    print(f"Portfolio weights shape: {weights.shape}")
    print(f"Cash allocation shape: {cash.shape}")
    print(f"State value shape: {value.shape}")
    print(f"Portfolio weights sum: {weights.sum().item():.4f}")
    print(f"Cash allocation: {cash.item():.4f}")
    print(f"State value: {value.item():.4f}")