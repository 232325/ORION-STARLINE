"""
Advanced Reinforcement Learning Models for Trading
===================================================

Bu modul ilg'or RL algoritmlarini o'z ichiga oladi:
- SAC (Soft Actor-Critic) - Off-policy, continuous action space
- TD3 (Twin Delayed DDPG) - Improved DDPG with double Q-learning
- Rainbow DQN - DQN ning barcha yaxshilanishlari
- Dreamer - Model-based RL with world models

Author: AI Trading Evolution
Date: 2025-11-04
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Normal
from collections import deque, namedtuple
from typing import Dict, List, Tuple, Optional, Any
import random
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class RLConfig:
    """RL model konfiguratsiyasi"""
    state_dim: int = 50
    action_dim: int = 3  # Buy, Sell, Hold
    hidden_dim: int = 256
    learning_rate: float = 3e-4
    gamma: float = 0.99  # Discount factor
    tau: float = 0.005  # Soft update coefficient
    buffer_size: int = 1_000_000
    batch_size: int = 256
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


Transition = namedtuple('Transition', 
                        ['state', 'action', 'reward', 'next_state', 'done'])


# ============================================================================
# Replay Buffer
# ============================================================================

class PrioritizedReplayBuffer:
    """Prioritized Experience Replay Buffer (Rainbow DQN komponenti)"""
    
    def __init__(self, capacity: int, alpha: float = 0.6):
        self.capacity = capacity
        self.alpha = alpha
        self.buffer = []
        self.priorities = np.zeros(capacity, dtype=np.float32)
        self.position = 0
        
    def push(self, transition: Transition):
        """Yangi tajriba qo'shish"""
        max_priority = self.priorities.max() if self.buffer else 1.0
        
        if len(self.buffer) < self.capacity:
            self.buffer.append(transition)
        else:
            self.buffer[self.position] = transition
            
        self.priorities[self.position] = max_priority
        self.position = (self.position + 1) % self.capacity
        
    def sample(self, batch_size: int, beta: float = 0.4) -> Tuple[List, np.ndarray, np.ndarray]:
        """Prioritetga asoslangan sample olish"""
        if len(self.buffer) == self.capacity:
            priorities = self.priorities
        else:
            priorities = self.priorities[:len(self.buffer)]
            
        # Probability calculation
        probs = priorities ** self.alpha
        probs /= probs.sum()
        
        # Sample indices
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        samples = [self.buffer[idx] for idx in indices]
        
        # Importance sampling weights
        total = len(self.buffer)
        weights = (total * probs[indices]) ** (-beta)
        weights /= weights.max()
        
        return samples, indices, weights
        
    def update_priorities(self, indices: np.ndarray, priorities: np.ndarray):
        """Prioritetlarni yangilash"""
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority
            
    def __len__(self):
        return len(self.buffer)


# ============================================================================
# SAC (Soft Actor-Critic) Implementation
# ============================================================================

class SACGaussianPolicy(nn.Module):
    """SAC uchun Gaussian policy network"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        
        self.mean = nn.Linear(hidden_dim, action_dim)
        self.log_std = nn.Linear(hidden_dim, action_dim)
        
        self.action_scale = 1.0
        self.action_bias = 0.0
        
    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        
        mean = self.mean(x)
        log_std = self.log_std(x)
        log_std = torch.clamp(log_std, min=-20, max=2)
        
        return mean, log_std
        
    def sample(self, state):
        """Action sample olish"""
        mean, log_std = self.forward(state)
        std = log_std.exp()
        normal = Normal(mean, std)
        
        # Reparameterization trick
        x_t = normal.rsample()
        action = torch.tanh(x_t)
        
        # Log probability calculation
        log_prob = normal.log_prob(x_t)
        log_prob -= torch.log(1 - action.pow(2) + 1e-6)
        log_prob = log_prob.sum(1, keepdim=True)
        
        # Scale action
        action = action * self.action_scale + self.action_bias
        mean = torch.tanh(mean) * self.action_scale + self.action_bias
        
        return action, log_prob, mean


class SACQNetwork(nn.Module):
    """SAC uchun Q-network (Critic)"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        
        # Q1 network
        self.q1_fc1 = nn.Linear(state_dim + action_dim, hidden_dim)
        self.q1_fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.q1_out = nn.Linear(hidden_dim, 1)
        
        # Q2 network
        self.q2_fc1 = nn.Linear(state_dim + action_dim, hidden_dim)
        self.q2_fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.q2_out = nn.Linear(hidden_dim, 1)
        
    def forward(self, state, action):
        x = torch.cat([state, action], dim=1)
        
        # Q1
        q1 = F.relu(self.q1_fc1(x))
        q1 = F.relu(self.q1_fc2(q1))
        q1 = self.q1_out(q1)
        
        # Q2
        q2 = F.relu(self.q2_fc1(x))
        q2 = F.relu(self.q2_fc2(q2))
        q2 = self.q2_out(q2)
        
        return q1, q2


class SACAgent:
    """Soft Actor-Critic Agent"""
    
    def __init__(self, config: RLConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Networks
        self.policy = SACGaussianPolicy(
            config.state_dim, config.action_dim, config.hidden_dim
        ).to(self.device)
        
        self.critic = SACQNetwork(
            config.state_dim, config.action_dim, config.hidden_dim
        ).to(self.device)
        
        self.critic_target = SACQNetwork(
            config.state_dim, config.action_dim, config.hidden_dim
        ).to(self.device)
        self.critic_target.load_state_dict(self.critic.state_dict())
        
        # Optimizers
        self.policy_optimizer = optim.Adam(self.policy.parameters(), lr=config.learning_rate)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=config.learning_rate)
        
        # Automatic entropy tuning
        self.target_entropy = -config.action_dim
        self.log_alpha = torch.zeros(1, requires_grad=True, device=self.device)
        self.alpha_optimizer = optim.Adam([self.log_alpha], lr=config.learning_rate)
        
        # Replay buffer
        self.replay_buffer = deque(maxlen=config.buffer_size)
        
    def select_action(self, state: np.ndarray, evaluate: bool = False):
        """Action tanlash"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        if evaluate:
            _, _, action = self.policy.sample(state)
        else:
            action, _, _ = self.policy.sample(state)
            
        return action.detach().cpu().numpy()[0]
        
    def update(self, batch_size: int):
        """Agent parametrlarini yangilash"""
        if len(self.replay_buffer) < batch_size:
            return {}
            
        # Sample from buffer
        batch = random.sample(self.replay_buffer, batch_size)
        state, action, reward, next_state, done = zip(*batch)
        
        state = torch.FloatTensor(np.array(state)).to(self.device)
        action = torch.FloatTensor(np.array(action)).to(self.device)
        reward = torch.FloatTensor(reward).unsqueeze(1).to(self.device)
        next_state = torch.FloatTensor(np.array(next_state)).to(self.device)
        done = torch.FloatTensor(done).unsqueeze(1).to(self.device)
        
        # Update critic
        with torch.no_grad():
            next_action, next_log_prob, _ = self.policy.sample(next_state)
            q1_next, q2_next = self.critic_target(next_state, next_action)
            q_next = torch.min(q1_next, q2_next) - self.log_alpha.exp() * next_log_prob
            q_target = reward + (1 - done) * self.config.gamma * q_next
            
        q1, q2 = self.critic(state, action)
        critic_loss = F.mse_loss(q1, q_target) + F.mse_loss(q2, q_target)
        
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        # Update policy
        new_action, log_prob, _ = self.policy.sample(state)
        q1_new, q2_new = self.critic(state, new_action)
        q_new = torch.min(q1_new, q2_new)
        
        policy_loss = (self.log_alpha.exp() * log_prob - q_new).mean()
        
        self.policy_optimizer.zero_grad()
        policy_loss.backward()
        self.policy_optimizer.step()
        
        # Update temperature (alpha)
        alpha_loss = -(self.log_alpha * (log_prob + self.target_entropy).detach()).mean()
        
        self.alpha_optimizer.zero_grad()
        alpha_loss.backward()
        self.alpha_optimizer.step()
        
        # Soft update target network
        for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
            target_param.data.copy_(
                self.config.tau * param.data + (1 - self.config.tau) * target_param.data
            )
            
        return {
            'critic_loss': critic_loss.item(),
            'policy_loss': policy_loss.item(),
            'alpha_loss': alpha_loss.item(),
            'alpha': self.log_alpha.exp().item()
        }
        
    def store_transition(self, state, action, reward, next_state, done):
        """Tajriba saqlash"""
        self.replay_buffer.append((state, action, reward, next_state, done))


# ============================================================================
# TD3 (Twin Delayed DDPG) Implementation
# ============================================================================

class TD3Actor(nn.Module):
    """TD3 Actor network"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, action_dim)
        
    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        action = torch.tanh(self.fc3(x))
        return action


class TD3Critic(nn.Module):
    """TD3 Critic network (Twin Q-networks)"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        
        # Q1
        self.q1_fc1 = nn.Linear(state_dim + action_dim, hidden_dim)
        self.q1_fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.q1_out = nn.Linear(hidden_dim, 1)
        
        # Q2
        self.q2_fc1 = nn.Linear(state_dim + action_dim, hidden_dim)
        self.q2_fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.q2_out = nn.Linear(hidden_dim, 1)
        
    def forward(self, state, action):
        x = torch.cat([state, action], dim=1)
        
        q1 = F.relu(self.q1_fc1(x))
        q1 = F.relu(self.q1_fc2(q1))
        q1 = self.q1_out(q1)
        
        q2 = F.relu(self.q2_fc1(x))
        q2 = F.relu(self.q2_fc2(q2))
        q2 = self.q2_out(q2)
        
        return q1, q2
        
    def q1_forward(self, state, action):
        x = torch.cat([state, action], dim=1)
        q1 = F.relu(self.q1_fc1(x))
        q1 = F.relu(self.q1_fc2(q1))
        return self.q1_out(q1)


class TD3Agent:
    """Twin Delayed DDPG Agent"""
    
    def __init__(self, config: RLConfig, policy_delay: int = 2, policy_noise: float = 0.2):
        self.config = config
        self.device = torch.device(config.device)
        self.policy_delay = policy_delay
        self.policy_noise = policy_noise
        self.total_iterations = 0
        
        # Networks
        self.actor = TD3Actor(config.state_dim, config.action_dim, config.hidden_dim).to(self.device)
        self.actor_target = TD3Actor(config.state_dim, config.action_dim, config.hidden_dim).to(self.device)
        self.actor_target.load_state_dict(self.actor.state_dict())
        
        self.critic = TD3Critic(config.state_dim, config.action_dim, config.hidden_dim).to(self.device)
        self.critic_target = TD3Critic(config.state_dim, config.action_dim, config.hidden_dim).to(self.device)
        self.critic_target.load_state_dict(self.critic.state_dict())
        
        # Optimizers
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=config.learning_rate)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=config.learning_rate)
        
        # Replay buffer
        self.replay_buffer = deque(maxlen=config.buffer_size)
        
    def select_action(self, state: np.ndarray, noise: float = 0.1):
        """Action tanlash"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        action = self.actor(state).detach().cpu().numpy()[0]
        
        if noise > 0:
            action += np.random.normal(0, noise, size=action.shape)
            action = np.clip(action, -1, 1)
            
        return action
        
    def update(self, batch_size: int):
        """Agent parametrlarini yangilash"""
        if len(self.replay_buffer) < batch_size:
            return {}
            
        self.total_iterations += 1
        
        # Sample batch
        batch = random.sample(self.replay_buffer, batch_size)
        state, action, reward, next_state, done = zip(*batch)
        
        state = torch.FloatTensor(np.array(state)).to(self.device)
        action = torch.FloatTensor(np.array(action)).to(self.device)
        reward = torch.FloatTensor(reward).unsqueeze(1).to(self.device)
        next_state = torch.FloatTensor(np.array(next_state)).to(self.device)
        done = torch.FloatTensor(done).unsqueeze(1).to(self.device)
        
        # Update critic
        with torch.no_grad():
            # Target policy smoothing
            noise = (torch.randn_like(action) * self.policy_noise).clamp(-0.5, 0.5)
            next_action = (self.actor_target(next_state) + noise).clamp(-1, 1)
            
            # Compute target Q
            q1_target, q2_target = self.critic_target(next_state, next_action)
            q_target = reward + (1 - done) * self.config.gamma * torch.min(q1_target, q2_target)
            
        q1, q2 = self.critic(state, action)
        critic_loss = F.mse_loss(q1, q_target) + F.mse_loss(q2, q_target)
        
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        # Delayed policy update
        policy_loss = None
        if self.total_iterations % self.policy_delay == 0:
            # Update actor
            actor_loss = -self.critic.q1_forward(state, self.actor(state)).mean()
            
            self.actor_optimizer.zero_grad()
            actor_loss.backward()
            self.actor_optimizer.step()
            
            policy_loss = actor_loss.item()
            
            # Soft update targets
            for param, target_param in zip(self.actor.parameters(), self.actor_target.parameters()):
                target_param.data.copy_(
                    self.config.tau * param.data + (1 - self.config.tau) * target_param.data
                )
                
            for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
                target_param.data.copy_(
                    self.config.tau * param.data + (1 - self.config.tau) * target_param.data
                )
                
        return {
            'critic_loss': critic_loss.item(),
            'policy_loss': policy_loss if policy_loss else 0.0
        }
        
    def store_transition(self, state, action, reward, next_state, done):
        """Tajriba saqlash"""
        self.replay_buffer.append((state, action, reward, next_state, done))


# ============================================================================
# Rainbow DQN Implementation
# ============================================================================

class NoisyLinear(nn.Module):
    """Noisy Networks for Exploration"""
    
    def __init__(self, in_features: int, out_features: int, sigma_init: float = 0.5):
        super().__init__()
        
        self.in_features = in_features
        self.out_features = out_features
        self.sigma_init = sigma_init
        
        # Learnable parameters
        self.weight_mu = nn.Parameter(torch.FloatTensor(out_features, in_features))
        self.weight_sigma = nn.Parameter(torch.FloatTensor(out_features, in_features))
        self.bias_mu = nn.Parameter(torch.FloatTensor(out_features))
        self.bias_sigma = nn.Parameter(torch.FloatTensor(out_features))
        
        # Noise buffers
        self.register_buffer('weight_epsilon', torch.FloatTensor(out_features, in_features))
        self.register_buffer('bias_epsilon', torch.FloatTensor(out_features))
        
        self.reset_parameters()
        self.reset_noise()
        
    def reset_parameters(self):
        mu_range = 1 / np.sqrt(self.in_features)
        self.weight_mu.data.uniform_(-mu_range, mu_range)
        self.bias_mu.data.uniform_(-mu_range, mu_range)
        
        self.weight_sigma.data.fill_(self.sigma_init / np.sqrt(self.in_features))
        self.bias_sigma.data.fill_(self.sigma_init / np.sqrt(self.out_features))
        
    def reset_noise(self):
        epsilon_in = self._scale_noise(self.in_features)
        epsilon_out = self._scale_noise(self.out_features)
        
        self.weight_epsilon.copy_(epsilon_out.ger(epsilon_in))
        self.bias_epsilon.copy_(epsilon_out)
        
    def _scale_noise(self, size):
        x = torch.randn(size)
        return x.sign().mul(x.abs().sqrt())
        
    def forward(self, x):
        if self.training:
            weight = self.weight_mu + self.weight_sigma * self.weight_epsilon
            bias = self.bias_mu + self.bias_sigma * self.bias_epsilon
        else:
            weight = self.weight_mu
            bias = self.bias_mu
            
        return F.linear(x, weight, bias)


class RainbowDQN(nn.Module):
    """Rainbow DQN Network with Dueling Architecture and Distributional RL"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256,
                 n_atoms: int = 51, v_min: float = -10, v_max: float = 10):
        super().__init__()
        
        self.action_dim = action_dim
        self.n_atoms = n_atoms
        self.v_min = v_min
        self.v_max = v_max
        
        # Support for distributional RL
        self.register_buffer('support', torch.linspace(v_min, v_max, n_atoms))
        self.delta_z = (v_max - v_min) / (n_atoms - 1)
        
        # Feature extraction
        self.feature = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # Dueling architecture - Value stream
        self.value_stream = nn.Sequential(
            NoisyLinear(hidden_dim, hidden_dim),
            nn.ReLU(),
            NoisyLinear(hidden_dim, n_atoms)
        )
        
        # Dueling architecture - Advantage stream
        self.advantage_stream = nn.Sequential(
            NoisyLinear(hidden_dim, hidden_dim),
            nn.ReLU(),
            NoisyLinear(hidden_dim, action_dim * n_atoms)
        )
        
    def forward(self, state):
        batch_size = state.size(0)
        
        # Feature extraction
        features = self.feature(state)
        
        # Value and advantage
        value = self.value_stream(features).view(batch_size, 1, self.n_atoms)
        advantage = self.advantage_stream(features).view(batch_size, self.action_dim, self.n_atoms)
        
        # Combine using dueling architecture
        q_dist = value + advantage - advantage.mean(dim=1, keepdim=True)
        
        # Softmax for probability distribution
        q_dist = F.softmax(q_dist, dim=-1)
        
        return q_dist
        
    def reset_noise(self):
        """Reset noise in all noisy layers"""
        for module in self.modules():
            if isinstance(module, NoisyLinear):
                module.reset_noise()
                
    def get_q_values(self, state):
        """Get Q-values from distribution"""
        q_dist = self.forward(state)
        q_values = (q_dist * self.support).sum(dim=-1)
        return q_values


class RainbowDQNAgent:
    """Rainbow DQN Agent (combines DQN + Double DQN + Dueling + Noisy + Prioritized + Distributional)"""
    
    def __init__(self, config: RLConfig, n_step: int = 3):
        self.config = config
        self.device = torch.device(config.device)
        self.n_step = n_step
        
        # Networks
        self.dqn = RainbowDQN(config.state_dim, config.action_dim, config.hidden_dim).to(self.device)
        self.target_dqn = RainbowDQN(config.state_dim, config.action_dim, config.hidden_dim).to(self.device)
        self.target_dqn.load_state_dict(self.dqn.state_dict())
        
        # Optimizer
        self.optimizer = optim.Adam(self.dqn.parameters(), lr=config.learning_rate)
        
        # Prioritized replay buffer
        self.replay_buffer = PrioritizedReplayBuffer(config.buffer_size)
        
        # N-step buffer
        self.n_step_buffer = deque(maxlen=n_step)
        
        # Beta annealing for importance sampling
        self.beta = 0.4
        self.beta_increment = 0.001
        
    def select_action(self, state: np.ndarray):
        """Action tanlash (noisy networks orqali exploration)"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            q_values = self.dqn.get_q_values(state)
            action = q_values.argmax(dim=1).item()
            
        return action
        
    def update(self, batch_size: int):
        """Agent parametrlarini yangilash"""
        if len(self.replay_buffer) < batch_size:
            return {}
            
        # Sample with prioritization
        batch, indices, weights = self.replay_buffer.sample(batch_size, self.beta)
        self.beta = min(1.0, self.beta + self.beta_increment)
        
        state, action, reward, next_state, done = zip(*batch)
        
        state = torch.FloatTensor(np.array(state)).to(self.device)
        action = torch.LongTensor(action).unsqueeze(1).to(self.device)
        reward = torch.FloatTensor(reward).to(self.device)
        next_state = torch.FloatTensor(np.array(next_state)).to(self.device)
        done = torch.FloatTensor(done).to(self.device)
        weights = torch.FloatTensor(weights).to(self.device)
        
        # Current Q distribution
        q_dist = self.dqn(state)
        q_dist = q_dist.gather(1, action.unsqueeze(-1).expand(-1, -1, q_dist.size(-1))).squeeze(1)
        
        # Double DQN: use online network to select action
        with torch.no_grad():
            next_actions = self.dqn.get_q_values(next_state).argmax(dim=1, keepdim=True)
            
            # Get target distribution
            next_q_dist = self.target_dqn(next_state)
            next_q_dist = next_q_dist.gather(1, next_actions.unsqueeze(-1).expand(-1, -1, next_q_dist.size(-1))).squeeze(1)
            
            # Compute projected distribution
            support = self.dqn.support
            delta_z = self.dqn.delta_z
            
            # Tz = r + gamma * z (projection)
            Tz = reward.unsqueeze(-1) + (1 - done.unsqueeze(-1)) * self.config.gamma * support.unsqueeze(0)
            Tz = Tz.clamp(self.dqn.v_min, self.dqn.v_max)
            
            # Compute projection onto support
            b = (Tz - self.dqn.v_min) / delta_z
            l = b.floor().long()
            u = b.ceil().long()
            
            # Distribute probability
            m = torch.zeros_like(next_q_dist)
            offset = torch.linspace(0, (batch_size - 1) * q_dist.size(-1), batch_size).long().unsqueeze(1).expand(batch_size, q_dist.size(-1)).to(self.device)
            
            m.view(-1).index_add_(0, (l + offset).view(-1), (next_q_dist * (u.float() - b)).view(-1))
            m.view(-1).index_add_(0, (u + offset).view(-1), (next_q_dist * (b - l.float())).view(-1))
            
        # Compute loss
        loss = -(m * q_dist.clamp(min=1e-5, max=1 - 1e-5).log()).sum(-1)
        loss = (loss * weights).mean()
        
        # Update network
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.dqn.parameters(), 10)
        self.optimizer.step()
        
        # Update priorities
        td_errors = loss.detach().cpu().numpy()
        self.replay_buffer.update_priorities(indices, td_errors + 1e-6)
        
        # Reset noise
        self.dqn.reset_noise()
        self.target_dqn.reset_noise()
        
        return {'loss': loss.item()}
        
    def store_transition(self, state, action, reward, next_state, done):
        """N-step transition saqlash"""
        self.n_step_buffer.append((state, action, reward, next_state, done))
        
        if len(self.n_step_buffer) == self.n_step:
            # Compute n-step return
            n_step_state = self.n_step_buffer[0][0]
            n_step_action = self.n_step_buffer[0][1]
            n_step_reward = sum([self.config.gamma ** i * t[2] for i, t in enumerate(self.n_step_buffer)])
            n_step_next_state = self.n_step_buffer[-1][3]
            n_step_done = self.n_step_buffer[-1][4]
            
            transition = Transition(n_step_state, n_step_action, n_step_reward, 
                                   n_step_next_state, n_step_done)
            self.replay_buffer.push(transition)
            
    def update_target(self):
        """Target network yangilash"""
        self.target_dqn.load_state_dict(self.dqn.state_dict())


# ============================================================================
# Dreamer (Model-Based RL with World Models)
# ============================================================================

class WorldModel(nn.Module):
    """Dreamer World Model (RSSM - Recurrent State Space Model)"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256,
                 stochastic_dim: int = 32, deterministic_dim: int = 256):
        super().__init__()
        
        self.stochastic_dim = stochastic_dim
        self.deterministic_dim = deterministic_dim
        
        # Encoder: observation -> embedding
        self.encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Decoder: state -> observation
        self.decoder = nn.Sequential(
            nn.Linear(deterministic_dim + stochastic_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, state_dim)
        )
        
        # Recurrent model: (state, action) -> next deterministic state
        self.rnn = nn.GRUCell(stochastic_dim + action_dim, deterministic_dim)
        
        # Prior: deterministic state -> stochastic state distribution
        self.prior = nn.Sequential(
            nn.Linear(deterministic_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, stochastic_dim * 2)  # mean and std
        )
        
        # Posterior: (deterministic state, observation) -> stochastic state distribution
        self.posterior = nn.Sequential(
            nn.Linear(deterministic_dim + hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, stochastic_dim * 2)  # mean and std
        )
        
        # Reward predictor
        self.reward_model = nn.Sequential(
            nn.Linear(deterministic_dim + stochastic_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Continue predictor (for episode termination)
        self.continue_model = nn.Sequential(
            nn.Linear(deterministic_dim + stochastic_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
    def encode(self, observation):
        """Observation encode qilish"""
        return self.encoder(observation)
        
    def decode(self, state):
        """State dan observation qayta tiklash"""
        return self.decoder(state)
        
    def get_distribution(self, params):
        """Gaussian distribution olish"""
        mean, std = torch.chunk(params, 2, dim=-1)
        std = F.softplus(std) + 0.1
        return Normal(mean, std)
        
    def imagine_step(self, prev_state, prev_action, sample=True):
        """Imagination: bir qadamni tasavvur qilish"""
        prev_deterministic, prev_stochastic = prev_state
        
        # Recurrent step
        deterministic = self.rnn(
            torch.cat([prev_stochastic, prev_action], dim=-1),
            prev_deterministic
        )
        
        # Prior distribution
        prior_params = self.prior(deterministic)
        prior_dist = self.get_distribution(prior_params)
        
        if sample:
            stochastic = prior_dist.rsample()
        else:
            stochastic = prior_dist.mean
            
        return (deterministic, stochastic), prior_dist
        
    def observe_step(self, prev_state, prev_action, observation):
        """Observation step: posterior distribution"""
        prev_deterministic, prev_stochastic = prev_state
        
        # Recurrent step
        deterministic = self.rnn(
            torch.cat([prev_stochastic, prev_action], dim=-1),
            prev_deterministic
        )
        
        # Encode observation
        obs_embed = self.encode(observation)
        
        # Posterior distribution
        posterior_params = self.posterior(torch.cat([deterministic, obs_embed], dim=-1))
        posterior_dist = self.get_distribution(posterior_params)
        stochastic = posterior_dist.rsample()
        
        # Prior distribution (for KL divergence)
        prior_params = self.prior(deterministic)
        prior_dist = self.get_distribution(prior_params)
        
        return (deterministic, stochastic), posterior_dist, prior_dist
        
    def predict_reward(self, state):
        """Reward prediction"""
        deterministic, stochastic = state
        state_cat = torch.cat([deterministic, stochastic], dim=-1)
        return self.reward_model(state_cat)
        
    def predict_continue(self, state):
        """Episode davom etishi ehtimoli"""
        deterministic, stochastic = state
        state_cat = torch.cat([deterministic, stochastic], dim=-1)
        return self.continue_model(state_cat)


class DreamerAgent:
    """Dreamer Agent (Model-Based Reinforcement Learning)"""
    
    def __init__(self, config: RLConfig, horizon: int = 15):
        self.config = config
        self.device = torch.device(config.device)
        self.horizon = horizon
        
        # World model
        self.world_model = WorldModel(
            config.state_dim, config.action_dim, config.hidden_dim
        ).to(self.device)
        
        # Actor (policy)
        self.actor = nn.Sequential(
            nn.Linear(config.hidden_dim + 32, config.hidden_dim),
            nn.ReLU(),
            nn.Linear(config.hidden_dim, config.action_dim),
            nn.Tanh()
        ).to(self.device)
        
        # Critic (value function)
        self.critic = nn.Sequential(
            nn.Linear(config.hidden_dim + 32, config.hidden_dim),
            nn.ReLU(),
            nn.Linear(config.hidden_dim, 1)
        ).to(self.device)
        
        # Optimizers
        self.world_optimizer = optim.Adam(self.world_model.parameters(), lr=config.learning_rate)
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=config.learning_rate)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=config.learning_rate)
        
        # Replay buffer
        self.replay_buffer = deque(maxlen=config.buffer_size)
        
        # Current state
        self.current_state = None
        
    def select_action(self, observation: np.ndarray):
        """Action tanlash"""
        observation = torch.FloatTensor(observation).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            if self.current_state is None:
                # Initialize state
                batch_size = observation.size(0)
                deterministic = torch.zeros(batch_size, 256).to(self.device)
                stochastic = torch.zeros(batch_size, 32).to(self.device)
                self.current_state = (deterministic, stochastic)
                
            # Get action from policy
            state_cat = torch.cat(self.current_state, dim=-1)
            action = self.actor(state_cat)
            
        return action.cpu().numpy()[0]
        
    def imagine_trajectory(self, start_state, horizon: int):
        """Tasavvur qilingan trajectory yaratish"""
        states = []
        actions = []
        rewards = []
        
        state = start_state
        
        for _ in range(horizon):
            # Get action from policy
            state_cat = torch.cat(state, dim=-1)
            action = self.actor(state_cat)
            
            # Imagine next state
            next_state, _ = self.world_model.imagine_step(state, action, sample=True)
            
            # Predict reward
            reward = self.world_model.predict_reward(next_state)
            
            states.append(next_state)
            actions.append(action)
            rewards.append(reward)
            
            state = next_state
            
        return states, actions, rewards
        
    def update(self, batch_size: int):
        """Agent yangilash"""
        if len(self.replay_buffer) < batch_size:
            return {}
            
        # Sample batch
        batch = random.sample(self.replay_buffer, batch_size)
        observations, actions, rewards, next_observations, dones = zip(*batch)
        
        observations = torch.FloatTensor(np.array(observations)).to(self.device)
        actions = torch.FloatTensor(np.array(actions)).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_observations = torch.FloatTensor(np.array(next_observations)).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)
        
        # Update world model
        batch_size = observations.size(0)
        deterministic = torch.zeros(batch_size, 256).to(self.device)
        stochastic = torch.zeros(batch_size, 32).to(self.device)
        state = (deterministic, stochastic)
        
        # Observe step
        next_state, posterior_dist, prior_dist = self.world_model.observe_step(
            state, actions, next_observations
        )
        
        # Reconstruction loss
        reconstructed = self.world_model.decode(torch.cat(next_state, dim=-1))
        reconstruction_loss = F.mse_loss(reconstructed, next_observations)
        
        # KL divergence loss
        kl_loss = torch.distributions.kl_divergence(posterior_dist, prior_dist).mean()
        
        # Reward prediction loss
        predicted_reward = self.world_model.predict_reward(next_state)
        reward_loss = F.mse_loss(predicted_reward, rewards)
        
        # Total world model loss
        world_loss = reconstruction_loss + 0.1 * kl_loss + reward_loss
        
        self.world_optimizer.zero_grad()
        world_loss.backward()
        self.world_optimizer.step()
        
        # Update actor and critic using imagined trajectories
        with torch.no_grad():
            start_state = next_state
            
        imagined_states, imagined_actions, imagined_rewards = self.imagine_trajectory(
            start_state, self.horizon
        )
        
        # Compute returns
        returns = []
        ret = 0
        for reward in reversed(imagined_rewards):
            ret = reward + self.config.gamma * ret
            returns.insert(0, ret)
        returns = torch.cat(returns, dim=0)
        
        # Update critic
        values = []
        for state in imagined_states:
            state_cat = torch.cat(state, dim=-1)
            value = self.critic(state_cat)
            values.append(value)
        values = torch.cat(values, dim=0)
        
        critic_loss = F.mse_loss(values, returns.detach())
        
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        # Update actor
        actor_loss = -(returns - values.detach()).mean()
        
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        
        return {
            'world_loss': world_loss.item(),
            'reconstruction_loss': reconstruction_loss.item(),
            'kl_loss': kl_loss.item(),
            'reward_loss': reward_loss.item(),
            'critic_loss': critic_loss.item(),
            'actor_loss': actor_loss.item()
        }
        
    def store_transition(self, state, action, reward, next_state, done):
        """Tajriba saqlash"""
        self.replay_buffer.append((state, action, reward, next_state, done))
        
    def reset_state(self):
        """Stateni reset qilish"""
        self.current_state = None


# ============================================================================
# Training & Evaluation
# ============================================================================

class RLTrainer:
    """RL agentlarni training qilish"""
    
    def __init__(self, agent, agent_type: str = "SAC"):
        self.agent = agent
        self.agent_type = agent_type
        self.training_history = []
        
    def train_episode(self, env, max_steps: int = 1000):
        """Bir episode training"""
        state = env.reset()
        episode_reward = 0
        episode_losses = []
        
        for step in range(max_steps):
            # Select action
            if self.agent_type == "Rainbow":
                action = self.agent.select_action(state)
            else:
                action = self.agent.select_action(state)
                
            # Environment step
            next_state, reward, done, _ = env.step(action)
            
            # Store transition
            self.agent.store_transition(state, action, reward, next_state, done)
            
            # Update agent
            losses = self.agent.update(self.agent.config.batch_size)
            if losses:
                episode_losses.append(losses)
                
            episode_reward += reward
            state = next_state
            
            if done:
                break
                
        # Update target network (for DQN-based methods)
        if self.agent_type == "Rainbow" and len(episode_losses) > 0:
            if len(self.training_history) % 10 == 0:
                self.agent.update_target()
                
        avg_losses = {}
        if episode_losses:
            for key in episode_losses[0].keys():
                avg_losses[key] = np.mean([loss[key] for loss in episode_losses])
                
        return episode_reward, avg_losses
        
    def evaluate(self, env, num_episodes: int = 10):
        """Agent baholash"""
        total_rewards = []
        
        for _ in range(num_episodes):
            state = env.reset()
            episode_reward = 0
            done = False
            
            while not done:
                if self.agent_type in ["SAC", "TD3"]:
                    action = self.agent.select_action(state, noise=0)
                else:
                    action = self.agent.select_action(state)
                    
                state, reward, done, _ = env.step(action)
                episode_reward += reward
                
            total_rewards.append(episode_reward)
            
        return {
            'mean_reward': np.mean(total_rewards),
            'std_reward': np.std(total_rewards),
            'max_reward': np.max(total_rewards),
            'min_reward': np.min(total_rewards)
        }


if __name__ == "__main__":
    logger.info("Advanced RL Models moduli yuklandi!")
    logger.info("Mavjud agentlar: SAC, TD3, Rainbow DQN, Dreamer")
    logger.info("Har bir agent zamonaviy RL algoritmlarini qo'llaydi")
