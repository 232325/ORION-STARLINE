"""
AI Signal Generator RL-based
Reinforcement Learning asosida signal generator

Muallif: Orion Starline AI Team
Versiya: 1.0.0
Sana: 2025-11-04
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Normal
from collections import deque, namedtuple
import gymnasium as gym
from gymnasium import spaces
import warnings
warnings.filterwarnings('ignore')

# Technical indicators
import talib
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
import asyncio
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import pickle
import os

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SIGNAL_TYPES = ['BUY', 'SELL', 'HOLD']
TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d']
MAX_FEATURES = 128
MEMORY_SIZE = 10000
BATCH_SIZE = 64
LEARNING_RATE = 0.001

# Experience Replay Buffer
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

class ReplayBuffer:
    """Experience Replay Buffer for off-policy algorithms"""
    
    def __init__(self, capacity: int = MEMORY_SIZE):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """Sample random batch from buffer"""
        return random.sample(self.buffer, batch_size)
    
    def __len__(self):
        return len(self.buffer)

# Base Agent Class
class BaseRLAgent:
    """Base Reinforcement Learning Agent"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Dict):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Performance tracking
        self.total_reward = 0
        self.episode_count = 0
        self.episode_rewards = []
        
    def act(self, state: np.ndarray, training: bool = True) -> int:
        """Choose action based on current state"""
        raise NotImplementedError
        
    def remember(self, state, action, reward, next_state, done):
        """Store experience in memory"""
        raise NotImplementedError
        
    def learn(self):
        """Update agent parameters"""
        raise NotImplementedError
        
    def save_model(self, path: str):
        """Save model weights"""
        raise NotImplementedError
        
    def load_model(self, path: str):
        """Load model weights"""
        raise NotImplementedError

# Deep Q-Network (DQN) Agent
class DQNAgent(BaseRLAgent):
    """Deep Q-Network Agent for discrete action spaces"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Dict):
        super().__init__(state_dim, action_dim, config)
        
        # Neural networks
        self.q_network = DQNNetwork(state_dim, action_dim).to(self.device)
        self.target_network = DQNNetwork(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=LEARNING_RATE)
        
        # Memory
        self.memory = ReplayBuffer(MEMORY_SIZE)
        self.epsilon = config.get('epsilon', 1.0)
        self.epsilon_decay = config.get('epsilon_decay', 0.995)
        self.epsilon_min = config.get('epsilon_min', 0.01)
        
        # Update target network
        self.update_target_every = config.get('update_target_every', 100)
        self.steps = 0
        
    def act(self, state: np.ndarray, training: bool = True) -> int:
        """Choose action using epsilon-greedy policy"""
        if training and np.random.random() <= self.epsilon:
            return np.random.randint(self.action_dim)
            
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        q_values = self.q_network(state)
        return q_values.argmax().item()
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)
    
    def learn(self):
        """Update Q-network using experience replay"""
        if len(self.memory) < BATCH_SIZE:
            return
            
        experiences = self.memory.sample(BATCH_SIZE)
        states, actions, rewards, next_states, dones = zip(*experiences)
        
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values from target network
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (0.99 * next_q_values * (1 - dones))
        
        # Loss
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update target network
        self.steps += 1
        if self.steps % self.update_target_every == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Update epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save_model(self, path: str):
        """Save model weights"""
        torch.save({
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, path)
    
    def load_model(self, path: str):
        """Load model weights"""
        checkpoint = torch.load(path, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint['epsilon']

class DQNNetwork(nn.Module):
    """Deep Q-Network Architecture"""
    
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )
    
    def forward(self, x):
        return self.network(x)

# Proximal Policy Optimization (PPO) Agent
class PPOAgent(BaseRLAgent):
    """Proximal Policy Optimization Agent"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Dict):
        super().__init__(state_dim, action_dim, config)
        
        # Neural networks
        self.actor = ActorNetwork(state_dim, action_dim).to(self.device)
        self.critic = CriticNetwork(state_dim).to(self.device)
        
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=LEARNING_RATE)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=LEARNING_RATE)
        
        # PPO parameters
        self.gamma = config.get('gamma', 0.99)
        self.gae_lambda = config.get('gae_lambda', 0.95)
        self.clip_ratio = config.get('clip_ratio', 0.2)
        self.value_coef = config.get('value_coef', 0.5)
        self.entropy_coef = config.get('entropy_coef', 0.01)
        
        # Storage for trajectories
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        
    def act(self, state: np.ndarray, training: bool = True) -> Tuple[int, float]:
        """Choose action and return action with log probability"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        action_probs = F.softmax(self.actor(state), dim=-1)
        dist = torch.distributions.Categorical(action_probs)
        
        if training:
            action = dist.sample()
        else:
            action = action_probs.argmax()
            
        log_prob = dist.log_prob(action)
        value = self.critic(state)
        
        return action.item(), log_prob.item(), value.item()
    
    def remember(self, state, action, reward, value, log_prob):
        """Store transition data"""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
    
    def learn(self):
        """Update actor and critic networks"""
        if len(self.states) == 0:
            return
            
        # Convert to tensors
        states = torch.FloatTensor(np.array(self.states)).to(self.device)
        actions = torch.LongTensor(self.actions).to(self.device)
        rewards = torch.FloatTensor(self.rewards).to(self.device)
        values = torch.FloatTensor(self.values).to(self.device)
        old_log_probs = torch.FloatTensor(self.log_probs).to(self.device)
        
        # Calculate advantages using GAE
        advantages = self._compute_gae(rewards, values)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Update actor
        new_action_probs = F.softmax(self.actor(states), dim=-1)
        dist = torch.distributions.Categorical(new_action_probs)
        new_log_probs = dist.log_prob(actions)
        
        ratio = torch.exp(new_log_probs - old_log_probs)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio) * advantages
        
        actor_loss = -torch.min(surr1, surr2).mean()
        entropy_loss = -dist.entropy().mean()
        
        total_actor_loss = actor_loss + self.entropy_coef * entropy_loss
        
        self.actor_optimizer.zero_grad()
        total_actor_loss.backward()
        self.actor_optimizer.step()
        
        # Update critic
        returns = rewards + self.gamma * torch.cat([values[1:], torch.zeros(1).to(self.device)])
        returns = returns[:-1]  # Remove last value
        
        value_loss = F.mse_loss(values[:-1], returns.detach())
        
        self.critic_optimizer.zero_grad()
        value_loss.backward()
        self.critic_optimizer.step()
        
        # Clear storage
        self._clear_storage()
    
    def _compute_gae(self, rewards: torch.Tensor, values: torch.Tensor) -> torch.Tensor:
        """Compute Generalized Advantage Estimation"""
        advantages = []
        gae = 0
        
        for t in reversed(range(len(rewards) - 1)):
            delta = rewards[t] + self.gamma * values[t + 1] - values[t]
            gae = delta + self.gamma * self.gae_lambda * gae
            advantages.insert(0, gae)
        
        return torch.FloatTensor(advantages)
    
    def _clear_storage(self):
        """Clear trajectory storage"""
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.values.clear()
        self.log_probs.clear()

class ActorNetwork(nn.Module):
    """Actor Network for PPO"""
    
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, action_dim)
        )
    
    def forward(self, x):
        return self.network(x)

class CriticNetwork(nn.Module):
    """Critic Network for PPO"""
    
    def __init__(self, state_dim: int):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 1)
        )
    
    def forward(self, x):
        return self.network(x)

# Advantage Actor-Critic (A2C) Agent
class A2CAgent(BaseRLAgent):
    """Advantage Actor-Critic Agent"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Dict):
        super().__init__(state_dim, action_dim, config)
        
        # Neural networks
        self.actor = ActorNetwork(state_dim, action_dim).to(self.device)
        self.critic = CriticNetwork(state_dim).to(self.device)
        
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=LEARNING_RATE)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=LEARNING_RATE)
        
        # A2C parameters
        self.gamma = config.get('gamma', 0.99)
        
    def act(self, state: np.ndarray, training: bool = True) -> Tuple[int, float]:
        """Choose action and return action with log probability"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        action_probs = F.softmax(self.actor(state), dim=-1)
        dist = torch.distributions.Categorical(action_probs)
        
        if training:
            action = dist.sample()
        else:
            action = action_probs.argmax()
            
        log_prob = dist.log_prob(action)
        value = self.critic(state)
        
        return action.item(), log_prob.item(), value.item()
    
    def remember(self, state, action, reward, value, log_prob):
        """Store transition data"""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
    
    def learn(self):
        """Update actor and critic networks"""
        if len(self.states) == 0:
            return
            
        # Convert to tensors
        states = torch.FloatTensor(np.array(self.states)).to(self.device)
        actions = torch.LongTensor(self.actions).to(self.device)
        rewards = torch.FloatTensor(self.rewards).to(self.device)
        values = torch.FloatTensor(self.values).to(self.device)
        old_log_probs = torch.FloatTensor(self.log_probs).to(self.device)
        
        # Calculate returns
        returns = []
        R = 0
        for reward in reversed(rewards):
            R = reward + self.gamma * R
            returns.insert(0, R)
        returns = torch.FloatTensor(returns).to(self.device)
        
        # Calculate advantages
        advantages = returns - values
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Update actor
        new_action_probs = F.softmax(self.actor(states), dim=-1)
        dist = torch.distributions.Categorical(new_action_probs)
        new_log_probs = dist.log_prob(actions)
        
        actor_loss = -(new_log_probs * advantages.detach()).mean()
        entropy_loss = -dist.entropy().mean()
        
        total_actor_loss = actor_loss + 0.01 * entropy_loss
        
        self.actor_optimizer.zero_grad()
        total_actor_loss.backward()
        self.actor_optimizer.step()
        
        # Update critic
        value_loss = F.mse_loss(values, returns)
        
        self.critic_optimizer.zero_grad()
        value_loss.backward()
        self.critic_optimizer.step()
        
        # Clear storage
        self._clear_storage()
    
    def _clear_storage(self):
        """Clear trajectory storage"""
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.values.clear()
        self.log_probs.clear()

# Feature Engineering Module
class FeatureEngineer:
    """Advanced feature engineering for financial time series"""
    
    def __init__(self):
        self.scalers = {}
        self.feature_importance = {}
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive features from price data"""
        features = df.copy()
        
        # Price-based features
        features['returns'] = df['close'].pct_change()
        features['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        features['high_low_ratio'] = df['high'] / df['low']
        features['close_open_ratio'] = df['close'] / df['open']
        
        # Technical indicators
        self._add_technical_indicators(features)
        
        # Multi-timeframe analysis
        self._add_multi_timeframe_features(features)
        
        # Pattern recognition features
        self._add_pattern_features(features)
        
        # Volume analysis
        self._add_volume_features(features)
        
        # Volatility features
        self._add_volatility_features(features)
        
        # Market sentiment features
        self._add_sentiment_features(features)
        
        # Support/resistance features
        self._add_support_resistance_features(features)
        
        # Trend features
        self._add_trend_features(features)
        
        # Statistical features
        self._add_statistical_features(features)
        
        return features
    
    def _add_technical_indicators(self, df: pd.DataFrame):
        """Add technical indicators"""
        # Moving averages
        df['sma_5'] = talib.SMA(df['close'], timeperiod=5)
        df['sma_10'] = talib.SMA(df['close'], timeperiod=10)
        df['sma_20'] = talib.SMA(df['close'], timeperiod=20)
        df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
        
        df['ema_5'] = talib.EMA(df['close'], timeperiod=5)
        df['ema_10'] = talib.EMA(df['close'], timeperiod=10)
        df['ema_20'] = talib.EMA(df['close'], timeperiod=20)
        
        # RSI
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        df['rsi_fast'] = talib.RSI(df['close'], timeperiod=5)
        df['rsi_slow'] = talib.RSI(df['close'], timeperiod=21)
        
        # MACD
        macd, macd_signal, macd_hist = talib.MACD(df['close'])
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_histogram'] = macd_hist
        
        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(df['close'])
        df['bb_upper'] = upper
        df['bb_middle'] = middle
        df['bb_lower'] = lower
        df['bb_width'] = (upper - lower) / middle
        df['bb_position'] = (df['close'] - lower) / (upper - lower)
        
        # Stochastic
        slowk, slowd = talib.STOCH(df['high'], df['low'], df['close'])
        df['stoch_k'] = slowk
        df['stoch_d'] = slowd
        
        # Williams %R
        df['williams_r'] = talib.WILLR(df['high'], df['low'], df['close'])
        
        # CCI
        df['cci'] = talib.CCI(df['high'], df['low'], df['close'])
        
        # ADX
        df['adx'] = talib.ADX(df['high'], df['low'], df['close'])
        df['adx_pos'] = talib.PLUS_DI(df['high'], df['low'], df['close'])
        df['adx_neg'] = talib.MINUS_DI(df['high'], df['low'], df['close'])
    
    def _add_multi_timeframe_features(self, df: pd.DataFrame):
        """Add multi-timeframe analysis features"""
        for tf in ['5m', '15m', '1h', '4h', '1d']:
            # This would require resampling in real implementation
            # For now, creating placeholder features
            df[f'sma_{tf}'] = df['close'].rolling(window=20).mean()
            df[f'rsi_{tf}'] = df['rsi']  # Placeholder
    
    def _add_pattern_features(self, df: pd.DataFrame):
        """Add pattern recognition features"""
        # Candlestick patterns
        df['doji'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
        df['hammer'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])
        df['shooting_star'] = talib.CDLSHOOTINGSTAR(df['open'], df['high'], df['low'], df['close'])
        df['engulfing'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
        df['harami'] = talib.CDLHARAMI(df['open'], df['high'], df['low'], df['close'])
        
        # Gap analysis
        df['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
    
    def _add_volume_features(self, df: pd.DataFrame):
        """Add volume analysis features"""
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        df['price_volume'] = df['close'] * df['volume']
        df['volume_price_trend'] = talib.VPT(df['close'], df['volume'])
        df['obv'] = talib.OBV(df['close'], df['volume'])
    
    def _add_volatility_features(self, df: pd.DataFrame):
        """Add volatility features"""
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        df['volatility_5'] = df['returns'].rolling(window=5).std()
        df['volatility_20'] = df['returns'].rolling(window=20).std()
        df['garman_klass'] = (np.log(df['high'] / df['low']) ** 2) / 2 - (2 * np.log(2) - 1) * (np.log(df['close'] / df['open']) ** 2)
    
    def _add_sentiment_features(self, df: pd.DataFrame):
        """Add market sentiment features"""
        # Fear & Greed index proxy
        df['fear_greed'] = (df['rsi'] - 50) / 50  # Normalized RSI
        df['sentiment_score'] = np.where(df['rsi'] > 70, -1, 
                                       np.where(df['rsi'] < 30, 1, 0))
        
        # Momentum sentiment
        df['momentum'] = df['close'] / df['close'].shift(10) - 1
        df['momentum_sentiment'] = np.where(df['momentum'] > 0.02, 1,
                                          np.where(df['momentum'] < -0.02, -1, 0))
    
    def _add_support_resistance_features(self, df: pd.DataFrame):
        """Add support and resistance detection features"""
        # Pivot points
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        df['r1'] = 2 * df['pivot'] - df['low']
        df['s1'] = 2 * df['pivot'] - df['high']
        df['r2'] = df['pivot'] + (df['high'] - df['low'])
        df['s2'] = df['pivot'] - (df['high'] - df['low'])
        
        # Nearest support/resistance levels
        df['nearest_resistance'] = np.where(df['close'] < df['r1'], df['r1'], df['r2'])
        df['nearest_support'] = np.where(df['close'] > df['s1'], df['s1'], df['s2'])
        
        # Distance to support/resistance
        df['resistance_distance'] = (df['nearest_resistance'] - df['close']) / df['close']
        df['support_distance'] = (df['close'] - df['nearest_support']) / df['close']
    
    def _add_trend_features(self, df: pd.DataFrame):
        """Add trend identification features"""
        # Linear regression slope
        df['trend_5'] = df['close'].rolling(window=5).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        df['trend_20'] = df['close'].rolling(window=20).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        
        # Trend strength
        df['adx_trend_strength'] = np.where(df['adx'] > 25, 
                                          np.where(df['adx_pos'] > df['adx_neg'], 1, -1), 0)
        
        # Parabolic SAR
        df['sar'] = talib.SAR(df['high'], df['low'])
        df['sar_signal'] = np.where(df['close'] > df['sar'], 1, -1)
    
    def _add_statistical_features(self, df: pd.DataFrame):
        """Add statistical features"""
        # Rolling correlations
        df['price_volume_corr'] = df['close'].rolling(window=20).corr(df['volume'])
        df['high_low_corr'] = df['high'].rolling(window=20).corr(df['low'])
        
        # Distribution features
        df['skewness'] = df['returns'].rolling(window=20).skew()
        df['kurtosis'] = df['returns'].rolling(window=20).kurtosis()
        
        # Z-score features
        df['price_zscore'] = (df['close'] - df['close'].rolling(window=20).mean()) / df['close'].rolling(window=20).std()
        df['volume_zscore'] = (df['volume'] - df['volume'].rolling(window=20).mean()) / df['volume'].rolling(window=20).std()
    
    def normalize_features(self, features: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Normalize features using scalers"""
        normalized = features.copy()
        feature_columns = [col for col in features.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        for col in feature_columns:
            if fit:
                self.scalers[col] = MinMaxScaler()
                normalized[col] = self.scalers[col].fit_transform(features[[col]])
            else:
                if col in self.scalers:
                    normalized[col] = self.scalers[col].transform(features[[col]])
                else:
                    normalized[col] = features[col]
        
        return normalized
    
    def get_feature_importance(self, target: pd.Series, features: pd.DataFrame) -> Dict:
        """Calculate feature importance using Random Forest"""
        feature_columns = [col for col in features.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        if len(feature_columns) > 0:
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(features[feature_columns], target)
            
            importance = dict(zip(feature_columns, rf.feature_importances_))
            self.feature_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
            
        return self.feature_importance

# Market Regime Detection
class MarketRegimeDetector:
    """Detect different market regimes"""
    
    def __init__(self):
        self.regimes = {
            'trending_bull': 0,
            'trending_bear': 1,
            'sideways': 2,
            'high_volatility': 3,
            'low_volatility': 4
        }
        
    def detect_regime(self, df: pd.DataFrame) -> pd.Series:
        """Detect current market regime"""
        returns = df['close'].pct_change()
        volatility = returns.rolling(window=20).std()
        
        # Trend detection using linear regression
        trend_20 = df['close'].rolling(window=20).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0]
        )
        
        # Regime classification
        regimes = []
        
        for i in range(len(df)):
            if i < 20:
                regimes.append(self.regimes['sideways'])
                continue
                
            vol = volatility.iloc[i]
            trend = trend_20.iloc[i]
            
            # High volatility regime
            if vol > volatility.quantile(0.8):
                regime = self.regimes['high_volatility']
            # Low volatility regime
            elif vol < volatility.quantile(0.2):
                regime = self.regimes['low_volatility']
            # Trending regimes
            elif trend > 0.001:
                regime = self.regimes['trending_bull']
            elif trend < -0.001:
                regime = self.regimes['trending_bear']
            else:
                regime = self.regimes['sideways']
                
            regimes.append(regime)
        
        return pd.Series(regimes, index=df.index)

# Signal Generation Environment
class TradingEnvironment(gym.Env):
    """Custom trading environment for RL training"""
    
    def __init__(self, data: pd.DataFrame, features: pd.DataFrame, window_size: int = 50):
        super().__init__()
        
        self.data = data
        self.features = features
        self.window_size = window_size
        self.current_step = window_size
        self.max_steps = len(data) - window_size - 1
        
        # Action space: 0=HOLD, 1=BUY, 2=SELL
        self.action_space = spaces.Discrete(3)
        
        # Observation space
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(window_size * len(features.columns),), dtype=np.float32
        )
        
        # Trading state
        self.position = 0  # 0=no position, 1=long, -1=short
        self.entry_price = 0
        self.cash = 10000
        self.portfolio_value = 10000
        self.trade_history = []
        
    def reset(self):
        """Reset environment"""
        self.current_step = self.window_size
        self.position = 0
        self.entry_price = 0
        self.cash = 10000
        self.portfolio_value = 10000
        self.trade_history = []
        
        return self._get_observation()
    
    def step(self, action: int):
        """Execute one step in environment"""
        self.current_step += 1
        
        if self.current_step >= self.max_steps:
            return self._get_observation(), 0, True, {}
        
        current_price = self.data['close'].iloc[self.current_step]
        
        # Execute action
        reward = self._execute_action(action, current_price)
        
        # Calculate portfolio value
        self.portfolio_value = self._calculate_portfolio_value(current_price)
        
        # Check if done
        done = self.current_step >= self.max_steps - 1
        
        info = {
            'portfolio_value': self.portfolio_value,
            'position': self.position,
            'cash': self.cash
        }
        
        return self._get_observation(), reward, done, info
    
    def _execute_action(self, action: int, price: float) -> float:
        """Execute trading action"""
        reward = 0
        
        if action == 1:  # BUY
            if self.position <= 0:  # Open long position
                if self.position == -1:  # Close short first
                    pnl = self.entry_price - price
                    self.cash += pnl
                    reward += pnl
                
                # Open long
                self.position = 1
                self.entry_price = price
                
        elif action == 2:  # SELL
            if self.position >= 0:  # Open short position
                if self.position == 1:  # Close long first
                    pnl = price - self.entry_price
                    self.cash += pnl
                    reward += pnl
                
                # Open short
                self.position = -1
                self.entry_price = price
                
        elif action == 0:  # HOLD
            if self.position != 0:
                # Calculate unrealized P&L
                if self.position == 1:  # Long
                    pnl = price - self.entry_price
                else:  # Short
                    pnl = self.entry_price - price
                reward += pnl * 0.01  # Small reward for holding profitable position
        
        return reward
    
    def _calculate_portfolio_value(self, current_price: float) -> float:
        """Calculate total portfolio value"""
        if self.position == 0:
            return self.cash
        elif self.position == 1:  # Long
            return self.cash + (current_price - self.entry_price)
        else:  # Short
            return self.cash + (self.entry_price - current_price)
    
    def _get_observation(self):
        """Get current observation"""
        start_idx = self.current_step - self.window_size
        end_idx = self.current_step
        
        # Get features for window
        window_features = self.features.iloc[start_idx:end_idx].values.flatten()
        
        # Add trading state
        state_info = [
            self.position,
            self.entry_price / 100,  # Normalize
            self.cash / 10000,  # Normalize
            self.portfolio_value / 10000  # Normalize
        ]
        
        observation = np.concatenate([window_features, state_info])
        
        return observation.astype(np.float32)

# Main AI Signal Generator
class AISignalGenerator:
    """Main AI Signal Generator using Multiple RL Algorithms"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.feature_engineer = FeatureEngineer()
        self.regime_detector = MarketRegimeDetector()
        
        # Initialize agents
        self.agents = {}
        self.agent_weights = {}
        self.model_ensemble = config.get('model_ensemble', True)
        
        # Performance tracking
        self.performance_history = []
        self.confidence_scores = []
        self.signal_filters = []
        
        # Market regime awareness
        self.current_regime = 0
        self.regime_history = []
        
        logger.info("AI Signal Generator initialized")
    
    def initialize_agents(self, state_dim: int, action_dim: int):
        """Initialize multiple RL agents"""
        agent_configs = self.config.get('agents', {})
        
        # DQN Agent
        if 'dqn' in agent_configs:
            self.agents['dqn'] = DQNAgent(state_dim, action_dim, agent_configs['dqn'])
            self.agent_weights['dqn'] = agent_configs['dqn'].get('weight', 0.2)
        
        # PPO Agent
        if 'ppo' in agent_configs:
            self.agents['ppo'] = PPOAgent(state_dim, action_dim, agent_configs['ppo'])
            self.agent_weights['ppo'] = agent_configs['ppo'].get('weight', 0.2)
        
        # A2C Agent
        if 'a2c' in agent_configs:
            self.agents['a2c'] = A2CAgent(state_dim, action_dim, agent_configs['a2c'])
            self.agent_weights['a2c'] = agent_configs['a2c'].get('weight', 0.2)
        
        # DDPG Agent
        if 'ddpg' in agent_configs:
            self.agents['ddpg'] = DDPGAgent(state_dim, action_dim, agent_configs['ddpg'])
            self.agent_weights['ddpg'] = agent_configs['ddpg'].get('weight', 0.2)
        
        # TD3 Agent
        if 'td3' in agent_configs:
            self.agents['td3'] = TD3Agent(state_dim, action_dim, agent_configs['td3'])
            self.agent_weights['td3'] = agent_configs['td3'].get('weight', 0.2)
        
        logger.info(f"Initialized {len(self.agents)} agents: {list(self.agents.keys())}")
    
    def prepare_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Prepare data for training"""
        # Create features
        features = self.feature_engineer.create_features(data)
        
        # Remove rows with NaN values
        features = features.dropna()
        
        # Detect market regime
        features['regime'] = self.regime_detector.detect_regime(features)
        
        # Normalize features
        features_normalized = self.feature_engineer.normalize_features(features, fit=True)
        
        return data.loc[features.index], features_normalized
    
    def generate_signals(self, data: pd.DataFrame, mode: str = 'inference') -> Dict:
        """Generate trading signals using ensemble of RL models"""
        # Prepare data
        processed_data, features = self.prepare_data(data)
        
        # Detect current market regime
        current_regime = features['regime'].iloc[-1]
        self.current_regime = current_regime
        
        if mode == 'training':
            # Initialize agents if not already done
            if not self.agents:
                state_dim = len(features.columns) * 50 + 4  # Features + trading state
                action_dim = 3  # BUY, SELL, HOLD
                self.initialize_agents(state_dim, action_dim)
            
            # Create environment for training
            env = TradingEnvironment(processed_data, features)
            
            # Train each agent
            for agent_name, agent in self.agents.items():
                logger.info(f"Training {agent_name} agent...")
                self._train_agent(agent, env, agent_name)
        
        # Generate signals
        signals = self._generate_ensemble_signals(features)
        
        # Add confidence scores
        signals['confidence'] = self._calculate_confidence(signals)
        
        # Apply signal filters
        signals = self._apply_signal_filters(signals, features)
        
        # Track performance
        self.performance_history.append({
            'timestamp': datetime.now(),
            'signals': signals,
            'regime': current_regime,
            'confidence': signals['confidence']
        })
        
        return signals
    
    def _generate_ensemble_signals(self, features: pd.DataFrame) -> Dict:
        """Generate signals using ensemble of agents"""
        current_state = self._get_current_state(features)
        agent_predictions = {}
        weighted_votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        
        # Get predictions from each agent
        for agent_name, agent in self.agents.items():
            try:
                if agent_name in ['dqn', 'ppo', 'a2c']:
                    action = agent.act(current_state, training=False)
                    
                # Convert action to signal
                if action == 0:
                    signal = 'HOLD'
                elif action == 1:
                    signal = 'BUY'
                else:
                    signal = 'SELL'
                
                agent_predictions[agent_name] = signal
                weight = self.agent_weights.get(agent_name, 0.2)
                weighted_votes[signal] += weight
                
            except Exception as e:
                logger.warning(f"Error getting prediction from {agent_name}: {e}")
                continue
        
        # Determine final signal
        final_signal = max(weighted_votes, key=weighted_votes.get)
        signal_strength = weighted_votes[final_signal]
        
        return {
            'signal': final_signal,
            'strength': signal_strength,
            'agent_predictions': agent_predictions,
            'votes': weighted_votes,
            'timestamp': datetime.now()
        }
    
    def _get_current_state(self, features: pd.DataFrame) -> np.ndarray:
        """Get current state for inference"""
        window_size = 50
        start_idx = max(0, len(features) - window_size)
        end_idx = len(features)
        
        # Get features for window
        window_features = features.iloc[start_idx:end_idx].values.flatten()
        
        # Add current trading state (assumed neutral for inference)
        state_info = [0, 0, 0.5, 0.5]  # position, entry_price, cash, portfolio_value
        current_state = np.concatenate([window_features, state_info])
        
        return current_state.astype(np.float32)
    
    def _calculate_confidence(self, signals: Dict) -> float:
        """Calculate confidence score for signals"""
        votes = signals['votes']
        total_votes = sum(votes.values())
        
        if total_votes == 0:
            return 0.0
        
        # Calculate agreement between agents
        max_vote = max(votes.values())
        confidence = max_vote / total_votes
        
        # Adjust for market regime
        regime_confidence = 1.0
        if self.current_regime in [3, 4]:  # High/Low volatility regimes
            regime_confidence = 0.8  # Reduce confidence in volatile regimes
        
        return min(confidence * regime_confidence, 1.0)
    
    def _apply_signal_filters(self, signals: Dict, features: pd.DataFrame) -> Dict:
        """Apply signal filters to improve quality"""
        filtered_signals = signals.copy()
        
        # Volume filter
        volume_sma = features['volume'].rolling(window=20).mean().iloc[-1]
        current_volume = features['volume'].iloc[-1]
        volume_ratio = current_volume / volume_sma if volume_sma > 0 else 1
        
        # Volatility filter
        current_rsi = features['rsi'].iloc[-1] if not pd.isna(features['rsi'].iloc[-1]) else 50
        volatility_filter = 1.0
        
        if current_rsi > 80 or current_rsi < 20:  # Extreme RSI
            volatility_filter = 0.7
        
        # Regime filter
        regime_filter = 1.0
        if self.current_regime == 3:  # High volatility
            if filtered_signals['signal'] == 'HOLD':
                regime_filter = 1.2  # Increase hold signal strength
            else:
                regime_filter = 0.8  # Reduce trading signal strength
        
        # Apply filters
        filtered_signals['strength'] *= volatility_filter * regime_filter
        
        # Adjust signal based on volume
        if volume_ratio < 0.5:  # Low volume
            if filtered_signals['signal'] != 'HOLD':
                filtered_signals['strength'] *= 0.6
        
        # Ensure strength is within bounds
        filtered_signals['strength'] = max(0, min(1, filtered_signals['strength']))
        
        return filtered_signals
    
    def _train_agent(self, agent, env, agent_name: str):
        """Train individual agent"""
        episodes = self.config.get('training_episodes', 1000)
        
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            done = False
            
            while not done:
                if agent_name in ['dqn', 'ppo', 'a2c']:
                    if agent_name == 'dqn':
                        action = agent.act(state)
                        next_state, reward, done, _ = env.step(action)
                        agent.remember(state, action, reward, next_state, done)
                    else:
                        action, log_prob, value = agent.act(state)
                        next_state, reward, done, _ = env.step(action)
                        agent.remember(state, action, reward, value, log_prob)
                
                state = next_state
                total_reward += reward
            
            if agent_name != 'dqn':
                agent.learn()
            
            if episode % 100 == 0:
                logger.info(f"{agent_name} - Episode {episode}, Total Reward: {total_reward:.2f}")
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        if not self.performance_history:
            return {}
        
        recent_signals = self.performance_history[-100:]  # Last 100 signals
        
        # Calculate metrics
        total_signals = len(recent_signals)
        buy_signals = sum(1 for s in recent_signals if s['signals']['signal'] == 'BUY')
        sell_signals = sum(1 for s in recent_signals if s['signals']['signal'] == 'SELL')
        hold_signals = sum(1 for s in recent_signals if s['signals']['signal'] == 'HOLD')
        
        avg_confidence = np.mean([s['confidence'] for s in recent_signals])
        
        return {
            'total_signals': total_signals,
            'buy_ratio': buy_signals / total_signals if total_signals > 0 else 0,
            'sell_ratio': sell_signals / total_signals if total_signals > 0 else 0,
            'hold_ratio': hold_signals / total_signals if total_signals > 0 else 0,
            'average_confidence': avg_confidence,
            'current_regime': self.current_regime,
            'regime_distribution': self._get_regime_distribution()
        }
    
    def _get_regime_distribution(self) -> Dict:
        """Get distribution of market regimes"""
        if not self.regime_history:
            return {}
        
        regimes, counts = np.unique(self.regime_history, return_counts=True)
        total = len(self.regime_history)
        
        regime_names = ['trending_bull', 'trending_bear', 'sideways', 'high_volatility', 'low_volatility']
        
        return {
            regime_names[r]: count / total 
            for r, count in zip(regimes, counts) 
            if r < len(regime_names)
        }
    
    def save_models(self, path: str):
        """Save all trained models"""
        os.makedirs(path, exist_ok=True)
        
        for agent_name, agent in self.agents.items():
            model_path = os.path.join(path, f"{agent_name}_model.pth")
            agent.save_model(model_path)
        
        # Save feature scalers
        scaler_path = os.path.join(path, "feature_scalers.pkl")
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.feature_engineer.scalers, f)
        
        logger.info(f"Models saved to {path}")
    
    def load_models(self, path: str):
        """Load all trained models"""
        for agent_name, agent in self.agents.items():
            model_path = os.path.join(path, f"{agent_name}_model.pth")
            if os.path.exists(model_path):
                agent.load_model(model_path)
        
        # Load feature scalers
        scaler_path = os.path.join(path, "feature_scalers.pkl")
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.feature_engineer.scalers = pickle.load(f)
        
        logger.info(f"Models loaded from {path}")

# DDPG Agent (for continuous actions)
class DDPGAgent(BaseRLAgent):
    """Deep Deterministic Policy Gradient Agent"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Dict):
        super().__init__(state_dim, action_dim, config)
        
        # Neural networks
        self.actor = ActorNetwork(state_dim, action_dim).to(self.device)
        self.critic = CriticNetwork(state_dim + action_dim).to(self.device)
        
        self.target_actor = ActorNetwork(state_dim, action_dim).to(self.device)
        self.target_critic = CriticNetwork(state_dim + action_dim).to(self.device)
        
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=LEARNING_RATE)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=LEARNING_RATE)
        
        # Memory
        self.memory = ReplayBuffer(MEMORY_SIZE)
        
        # DDPG parameters
        self.tau = config.get('tau', 0.005)
        self.gamma = config.get('gamma', 0.99)
        
        # Update target networks
        self._update_target_networks(initial=True)
    
    def act(self, state: np.ndarray, training: bool = True) -> np.ndarray:
        """Choose continuous action"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        action = self.actor(state)
        if training:
            action += torch.randn_like(action) * 0.1  # Add noise
        
        return action.cpu().detach().numpy().flatten()
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)
    
    def learn(self):
        """Update actor and critic networks"""
        if len(self.memory) < BATCH_SIZE:
            return
            
        experiences = self.memory.sample(BATCH_SIZE)
        states, actions, rewards, next_states, dones = zip(*experiences)
        
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.FloatTensor(np.array(actions)).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Update critic
        next_actions = self.target_actor(next_states)
        next_q_values = self.target_critic(torch.cat([next_states, next_actions], dim=1)).squeeze()
        target_q_values = rewards + (self.gamma * next_q_values * (1 - dones))
        
        current_q_values = self.critic(torch.cat([states, actions], dim=1)).squeeze()
        critic_loss = F.mse_loss(current_q_values, target_q_values.detach())
        
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        # Update actor
        current_actions = self.actor(states)
        actor_loss = -self.critic(torch.cat([states, current_actions], dim=1)).mean()
        
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        
        # Update target networks
        self._update_target_networks()
    
    def _update_target_networks(self, initial: bool = False):
        """Update target networks with soft update"""
        if initial:
            self.target_actor.load_state_dict(self.actor.state_dict())
            self.target_critic.load_state_dict(self.critic.state_dict())
        else:
            for target, main in zip(self.target_actor.parameters(), self.actor.parameters()):
                target.data.copy_(self.tau * main.data + (1 - self.tau) * target.data)
            
            for target, main in zip(self.target_critic.parameters(), self.critic.parameters()):
                target.data.copy_(self.tau * main.data + (1 - self.tau) * target.data)
    
    def save_model(self, path: str):
        """Save model weights"""
        torch.save({
            'actor': self.actor.state_dict(),
            'critic': self.critic.state_dict(),
            'target_actor': self.target_actor.state_dict(),
            'target_critic': self.target_critic.state_dict(),
            'actor_optimizer': self.actor_optimizer.state_dict(),
            'critic_optimizer': self.critic_optimizer.state_dict()
        }, path)
    
    def load_model(self, path: str):
        """Load model weights"""
        checkpoint = torch.load(path, map_location=self.device)
        self.actor.load_state_dict(checkpoint['actor'])
        self.critic.load_state_dict(checkpoint['critic'])
        self.target_actor.load_state_dict(checkpoint['target_actor'])
        self.target_critic.load_state_dict(checkpoint['target_critic'])
        self.actor_optimizer.load_state_dict(checkpoint['actor_optimizer'])
        self.critic_optimizer.load_state_dict(checkpoint['critic_optimizer'])

# TD3 Agent (Twin Delayed DDPG)
class TD3Agent(DDPGAgent):
    """Twin Delayed DDPG Agent"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Dict):
        super().__init__(state_dim, action_dim, config)
        
        # Additional critic network
        self.critic2 = CriticNetwork(state_dim + action_dim).to(self.device)
        self.target_critic2 = CriticNetwork(state_dim + action_dim).to(self.device)
        self.critic2_optimizer = optim.Adam(self.critic2.parameters(), lr=LEARNING_RATE)
        
        # TD3 parameters
        self.policy_delay = config.get('policy_delay', 2)
        self.target_noise = config.get('target_noise', 0.2)
        self.noise_clip = config.get('noise_clip', 0.5)
        self.update_count = 0
        
        # Update target networks
        self._update_target_networks(initial=True)
    
    def learn(self):
        """Update networks using TD3 algorithm"""
        if len(self.memory) < BATCH_SIZE:
            return
            
        experiences = self.memory.sample(BATCH_SIZE)
        states, actions, rewards, next_states, dones = zip(*experiences)
        
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.FloatTensor(np.array(actions)).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Update critics
        next_actions = self.target_actor(next_states)
        next_actions = next_actions + torch.clamp(
            torch.randn_like(next_actions) * self.target_noise, 
            -self.noise_clip, self.noise_clip
        )
        next_actions = torch.clamp(next_actions, -1, 1)
        
        # Twin Q-values
        next_q_values1 = self.target_critic(torch.cat([next_states, next_actions], dim=1)).squeeze()
        next_q_values2 = self.target_critic2(torch.cat([next_states, next_actions], dim=1)).squeeze()
        next_q_values = torch.min(next_q_values1, next_q_values2)
        
        target_q_values = rewards + (self.gamma * next_q_values * (1 - dones))
        
        # Current Q-values
        current_q_values1 = self.critic(torch.cat([states, actions], dim=1)).squeeze()
        current_q_values2 = self.critic2(torch.cat([states, actions], dim=1)).squeeze()
        
        critic_loss1 = F.mse_loss(current_q_values1, target_q_values.detach())
        critic_loss2 = F.mse_loss(current_q_values2, target_q_values.detach())
        
        # Update critics
        self.critic_optimizer.zero_grad()
        critic_loss1.backward()
        self.critic_optimizer.step()
        
        self.critic2_optimizer.zero_grad()
        critic_loss2.backward()
        self.critic2_optimizer.step()
        
        # Delayed policy update
        self.update_count += 1
        if self.update_count % self.policy_delay == 0:
            # Update actor
            current_actions = self.actor(states)
            actor_loss = -self.critic(torch.cat([states, current_actions], dim=1)).mean()
            
            self.actor_optimizer.zero_grad()
            actor_loss.backward()
            self.actor_optimizer.step()
            
            # Update target networks
            self._update_target_networks()
    
    def _update_target_networks(self, initial: bool = False):
        """Update target networks"""
        if initial:
            self.target_critic2.load_state_dict(self.critic2.state_dict())
        else:
            for target, main in zip(self.target_critic2.parameters(), self.critic2.parameters()):
                target.data.copy_(self.tau * main.data + (1 - self.tau) * target.data)
        
        super()._update_target_networks(initial)
    
    def save_model(self, path: str):
        """Save model weights"""
        torch.save({
            'actor': self.actor.state_dict(),
            'critic': self.critic.state_dict(),
            'critic2': self.critic2.state_dict(),
            'target_actor': self.target_actor.state_dict(),
            'target_critic': self.target_critic.state_dict(),
            'target_critic2': self.target_critic2.state_dict(),
            'actor_optimizer': self.actor_optimizer.state_dict(),
            'critic_optimizer': self.critic_optimizer.state_dict(),
            'critic2_optimizer': self.critic2_optimizer.state_dict()
        }, path)
    
    def load_model(self, path: str):
        """Load model weights"""
        checkpoint = torch.load(path, map_location=self.device)
        self.actor.load_state_dict(checkpoint['actor'])
        self.critic.load_state_dict(checkpoint['critic'])
        self.critic2.load_state_dict(checkpoint['critic2'])
        self.target_actor.load_state_dict(checkpoint['target_actor'])
        self.target_critic.load_state_dict(checkpoint['target_critic'])
        self.target_critic2.load_state_dict(checkpoint['target_critic2'])
        self.actor_optimizer.load_state_dict(checkpoint['actor_optimizer'])
        self.critic_optimizer.load_state_dict(checkpoint['critic_optimizer'])
        self.critic2_optimizer.load_state_dict(checkpoint['critic2_optimizer'])

# Example usage and testing
def create_sample_data() -> pd.DataFrame:
    """Create sample financial data for testing"""
    np.random.seed(42)
    
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='1H')
    n = len(dates)
    
    # Generate realistic price data
    returns = np.random.normal(0.001, 0.02, n)
    prices = 100 * np.cumprod(1 + returns)
    
    # Generate OHLCV data
    high_noise = np.random.uniform(0, 0.01, n)
    low_noise = np.random.uniform(0, 0.01, n)
    volume_noise = np.random.lognormal(10, 0.5, n)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * (1 + high_noise),
        'low': prices * (1 - low_noise),
        'close': prices,
        'volume': volume_noise
    })
    
    return data

def main():
    """Main function to demonstrate AI Signal Generator"""
    logger.info("AI Signal Generator demo boshlanmoqda...")
    
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
        'training_episodes': 100
    }
    
    # Create signal generator
    signal_generator = AISignalGenerator(config)
    
    # Generate sample data
    data = create_sample_data()
    logger.info(f"Sample data yaratildi: {len(data)} qator")
    
    # Generate signals
    signals = signal_generator.generate_signals(data, mode='training')
    logger.info(f"Signallar yaratildi: {signals}")
    
    # Get performance metrics
    metrics = signal_generator.get_performance_metrics()
    logger.info(f"Performance metrics: {metrics}")
    
    # Save models
    signal_generator.save_models('/workspace/orion-starline/backend/ai_modules/models')
    logger.info("Modellar saqlandi")
    
    return signal_generator, signals, metrics

if __name__ == "__main__":
    # Set random seeds for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Run demo
    generator, signals, metrics = main()
    print("AI Signal Generator muvaffaqiyatli ishga tushdi!")
    print(f"Yaratilgan signal: {signals}")
    print(f"Performance metrics: {metrics}")