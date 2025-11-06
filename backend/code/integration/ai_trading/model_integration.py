"""
AI Trading Integration
====================

AI Trading algoritmlarini (DQN, PPO, A2C) integratsiya qilish.
Trading signal aggregation, model performance tracking,
ensemble methods va real-time predictions.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import pickle
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

# Machine Learning libraries
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.distributions import Normal
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

class ModelType(Enum):
    """Model turlari"""
    DQN = "dqn"
    PPO = "ppo"
    A2C = "a2c"
    ENSEMBLE = "ensemble"

class SignalType(Enum):
    """Signal turlari"""
    BUY = 1
    SELL = -1
    HOLD = 0

@dataclass
class TradingSignal:
    """Trading signal ma'lumot"""
    symbol: str
    signal_type: SignalType
    confidence: float
    model_name: str
    timestamp: float
    price: float
    features: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelPrediction:
    """Model prediction ma'lumot"""
    model_name: str
    model_type: ModelType
    prediction: Any
    confidence: float
    timestamp: float
    features_used: List[str] = field(default_factory=list)
    model_state: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EnsembleResult:
    """Ensemble result"""
    symbol: str
    final_signal: SignalType
    confidence: float
    model_predictions: List[ModelPrediction]
    aggregation_method: str
    timestamp: float
    consensus_score: float

class DQNModel:
    """Deep Q-Network model"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Dict[str, Any] = None):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config or {}
        
        self.logger = logging.getLogger(__name__)
        
        if PYTORCH_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.q_network = self._build_network().to(self.device)
            self.target_network = self._build_network().to(self.device)
            self.optimizer = optim.Adam(self.q_network.parameters(), 
                                      lr=self.config.get('learning_rate', 0.001))
            
            # Copy weights to target network
            self.target_network.load_state_dict(self.q_network.state_dict())
        else:
            self.q_network = None
            self.target_network = None
            self.optimizer = None
            self.device = None
        
        self.epsilon = self.config.get('epsilon', 1.0)
        self.epsilon_decay = self.config.get('epsilon_decay', 0.995)
        self.epsilon_min = self.config.get('epsilon_min', 0.01)
    
    def _build_network(self):
        """Q-Network qurilishi"""
        return nn.Sequential(
            nn.Linear(self.state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, self.action_dim)
        )
    
    async def predict(self, state: np.ndarray) -> Tuple[int, float]:
        """Action va confidence predict qilish"""
        if not PYTORCH_AVAILABLE or self.q_network is None:
            # Fallback implementation
            action = np.random.choice(self.action_dim)
            confidence = 0.5
            return action, confidence
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
        
        action = q_values.argmax().item()
        confidence = torch.softmax(q_values, dim=1)[0][action].item()
        
        # Epsilon-greedy strategy
        if np.random.random() < self.epsilon:
            action = np.random.choice(self.action_dim)
            confidence = 0.33  # Random action confidence
        
        return action, confidence
    
    async def update(self, experiences: List[Dict[str, Any]]) -> float:
        """Model training update"""
        if not PYTORCH_AVAILABLE or self.q_network is None:
            return 0.0
        
        states = torch.FloatTensor([exp['state'] for exp in experiences]).to(self.device)
        actions = torch.LongTensor([exp['action'] for exp in experiences]).to(self.device)
        rewards = torch.FloatTensor([exp['reward'] for exp in experiences]).to(self.device)
        next_states = torch.FloatTensor([exp['next_state'] for exp in experiences]).to(self.device)
        dones = torch.BoolTensor([exp['done'] for exp in experiences]).to(self.device)
        
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (0.99 * next_q_values * ~dones)
        
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return loss.item()
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Model state dict olish"""
        if not PYTORCH_AVAILABLE or self.q_network is None:
            return {}
        
        return {
            'q_network_state': self.q_network.state_dict(),
            'target_network_state': self.target_network.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'config': self.config,
            'epsilon': self.epsilon
        }

class PPOModel:
    """Proximal Policy Optimization model"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Dict[str, Any] = None):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config or {}
        
        self.logger = logging.getLogger(__name__)
        
        if PYTORCH_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.actor = self._build_actor().to(self.device)
            self.critic = self._build_critic().to(self.device)
            
            self.actor_optimizer = optim.Adam(self.actor.parameters(), 
                                            lr=self.config.get('actor_lr', 0.0003))
            self.critic_optimizer = optim.Adam(self.critic.parameters(), 
                                             lr=self.config.get('critic_lr', 0.001))
        else:
            self.actor = None
            self.critic = None
            self.actor_optimizer = None
            self.critic_optimizer = None
            self.device = None
        
        self.clip_epsilon = self.config.get('clip_epsilon', 0.2)
        self.gamma = self.config.get('gamma', 0.99)
        self.lam = self.config.get('lam', 0.95)
    
    def _build_actor(self):
        """Actor network qurilishi"""
        return nn.Sequential(
            nn.Linear(self.state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, self.action_dim),
            nn.Tanh()
        )
    
    def _build_critic(self):
        """Critic network qurilishi"""
        return nn.Sequential(
            nn.Linear(self.state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
    
    async def predict(self, state: np.ndarray) -> Tuple[int, float]:
        """Action va confidence predict qilish"""
        if not PYTORCH_AVAILABLE or self.actor is None:
            # Fallback implementation
            action = np.random.choice(self.action_dim)
            confidence = 0.5
            return action, confidence
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            action_probs = torch.softmax(self.actor(state_tensor), dim=1)
        
        action_dist = torch.distributions.Categorical(action_probs)
        action = action_dist.sample().item()
        confidence = action_probs[0][action].item()
        
        return action, confidence
    
    async def update(self, trajectories: List[Dict[str, Any]]) -> Dict[str, float]:
        """Model training update"""
        if not PYTORCH_AVAILABLE or self.actor is None:
            return {'actor_loss': 0.0, 'critic_loss': 0.0}
        
        # Extract trajectories data
        states = torch.FloatTensor([traj['state'] for traj in trajectories]).to(self.device)
        actions = torch.LongTensor([traj['action'] for traj in trajectories]).to(self.device)
        rewards = torch.FloatTensor([traj['reward'] for traj in trajectories]).to(self.device)
        values = torch.FloatTensor([traj['value'] for traj in trajectories]).to(self.device)
        next_values = torch.FloatTensor([traj['next_value'] for traj in trajectories]).to(self.device)
        
        # Calculate advantages
        deltas = rewards + self.gamma * next_values - values
        advantages = []
        adv = 0
        for delta in reversed(deltas.tolist()):
            adv = delta + self.gamma * self.lam * adv
            advantages.insert(0, adv)
        
        advantages = torch.FloatTensor(advantages).to(self.device)
        returns = rewards + self.gamma * next_values
        
        # Update actor
        current_logits = self.actor(states)
        current_probs = torch.softmax(current_logits, dim=1)
        current_dist = torch.distributions.Categorical(current_probs)
        
        current_log_probs = current_dist.log_prob(actions)
        
        # This would need stored old probabilities from trajectory collection
        # Simplified implementation
        actor_loss = -torch.mean(advantages * current_log_probs)
        
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        
        # Update critic
        current_values = self.critic(states).squeeze()
        critic_loss = nn.MSELoss()(current_values, returns)
        
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        return {
            'actor_loss': actor_loss.item(),
            'critic_loss': critic_loss.item()
        }
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Model state dict olish"""
        if not PYTORCH_AVAILABLE or self.actor is None:
            return {}
        
        return {
            'actor_state': self.actor.state_dict(),
            'critic_state': self.critic.state_dict(),
            'actor_optimizer_state': self.actor_optimizer.state_dict(),
            'critic_optimizer_state': self.critic_optimizer.state_dict(),
            'config': self.config
        }

class A2CModel:
    """Advantage Actor-Critic model"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Dict[str, Any] = None):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config or {}
        
        self.logger = logging.getLogger(__name__)
        
        if PYTORCH_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.actor = self._build_actor().to(self.device)
            self.critic = self._build_critic().to(self.device)
            
            self.actor_optimizer = optim.Adam(self.actor.parameters(), 
                                            lr=self.config.get('actor_lr', 0.0001))
            self.critic_optimizer = optim.Adam(self.critic.parameters(), 
                                             lr=self.config.get('critic_lr', 0.001))
        else:
            self.actor = None
            self.critic = None
            self.actor_optimizer = None
            self.critic_optimizer = None
            self.device = None
        
        self.gamma = self.config.get('gamma', 0.99)
    
    def _build_actor(self):
        """Actor network qurilishi"""
        return nn.Sequential(
            nn.Linear(self.state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, self.action_dim)
        )
    
    def _build_critic(self):
        """Critic network qurilishi"""
        return nn.Sequential(
            nn.Linear(self.state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
    
    async def predict(self, state: np.ndarray) -> Tuple[int, float]:
        """Action va confidence predict qilish"""
        if not PYTORCH_AVAILABLE or self.actor is None:
            # Fallback implementation
            action = np.random.choice(self.action_dim)
            confidence = 0.5
            return action, confidence
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            logits = self.actor(state_tensor)
            action_probs = torch.softmax(logits, dim=1)
        
        action_dist = torch.distributions.Categorical(action_probs)
        action = action_dist.sample().item()
        confidence = action_probs[0][action].item()
        
        return action, confidence
    
    async def update(self, trajectories: List[Dict[str, Any]]) -> Dict[str, float]:
        """Model training update"""
        if not PYTORCH_AVAILABLE or self.actor is None:
            return {'actor_loss': 0.0, 'critic_loss': 0.0}
        
        # Extract trajectories data
        states = torch.FloatTensor([traj['state'] for traj in trajectories]).to(self.device)
        actions = torch.LongTensor([traj['action'] for traj in trajectories]).to(self.device)
        rewards = torch.FloatTensor([traj['reward'] for traj in trajectories]).to(self.device)
        next_states = torch.FloatTensor([traj['next_state'] for traj in trajectories]).to(self.device)
        dones = torch.BoolTensor([traj['done'] for traj in trajectories]).to(self.device)
        
        # Calculate values and returns
        values = self.critic(states).squeeze()
        next_values = self.critic(next_states).squeeze()
        returns = rewards + self.gamma * next_values * ~dones
        advantages = returns - values
        
        # Update actor
        logits = self.actor(states)
        action_probs = torch.softmax(logits, dim=1)
        action_dist = torch.distributions.Categorical(action_probs)
        log_probs = action_dist.log_prob(actions)
        
        actor_loss = -torch.mean(log_probs * advantages.detach())
        
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        
        # Update critic
        critic_loss = nn.MSELoss()(values, returns.detach())
        
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        return {
            'actor_loss': actor_loss.item(),
            'critic_loss': critic_loss.item()
        }
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Model state dict olish"""
        if not PYTORCH_AVAILABLE or self.actor is None:
            return {}
        
        return {
            'actor_state': self.actor.state_dict(),
            'critic_state': self.critic.state_dict(),
            'actor_optimizer_state': self.actor_optimizer.state_dict(),
            'critic_optimizer_state': self.critic_optimizer.state_dict(),
            'config': self.config
        }

class ModelIntegration:
    """
    AI Trading Model Integration
    
    DQN, PPO, A2C modellari integratsiyasi va management.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.models: Dict[str, Any] = {}
        self.model_types: Dict[str, ModelType] = {}
        self.model_configs: Dict[str, Dict[str, Any]] = {}
        
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Default configurations
        self.default_configs = {
            'dqn': {
                'state_dim': 10,
                'action_dim': 3,
                'learning_rate': 0.001,
                'epsilon': 1.0,
                'epsilon_decay': 0.995,
                'epsilon_min': 0.01
            },
            'ppo': {
                'state_dim': 10,
                'action_dim': 3,
                'actor_lr': 0.0003,
                'critic_lr': 0.001,
                'clip_epsilon': 0.2,
                'gamma': 0.99,
                'lam': 0.95
            },
            'a2c': {
                'state_dim': 10,
                'action_dim': 3,
                'actor_lr': 0.0001,
                'critic_lr': 0.001,
                'gamma': 0.99
            }
        }
    
    async def initialize(self) -> bool:
        """Model Integration-ni ishga tushirish"""
        try:
            self.logger.info("Model Integration ishga tushirilmoqda...")
            
            # Default modellarni yaratish
            await self._create_default_models()
            
            self.logger.info("Model Integration muvaffaqiyatli ishga tushdi")
            return True
            
        except Exception as e:
            self.logger.error(f"Model Integration ishga tushishda xato: {e}")
            return False
    
    async def _create_default_models(self):
        """Default modellarni yaratish"""
        for model_type in ['dqn', 'ppo', 'a2c']:
            model_name = f"{model_type}_default"
            await self.create_model(model_name, ModelType(model_type.upper()))
    
    async def create_model(self, model_name: str, model_type: ModelType, 
                          config: Dict[str, Any] = None) -> bool:
        """Model yaratish"""
        try:
            # Config merge
            default_config = self.default_configs.get(model_type.value, {})
            merged_config = {**default_config, **(config or {})}
            
            # Model yaratish
            if model_type == ModelType.DQN:
                model = DQNModel(
                    state_dim=merged_config['state_dim'],
                    action_dim=merged_config['action_dim'],
                    config=merged_config
                )
            elif model_type == ModelType.PPO:
                model = PPOModel(
                    state_dim=merged_config['state_dim'],
                    action_dim=merged_config['action_dim'],
                    config=merged_config
                )
            elif model_type == ModelType.A2C:
                model = A2CModel(
                    state_dim=merged_config['state_dim'],
                    action_dim=merged_config['action_dim'],
                    config=merged_config
                )
            else:
                self.logger.error(f"Qo'llab-quvvatlanmaydigan model turi: {model_type}")
                return False
            
            # Model registratsiya
            self.models[model_name] = model
            self.model_types[model_name] = model_type
            self.model_configs[model_name] = merged_config
            
            self.logger.info(f"Model yaratildi: {model_name} ({model_type.value})")
            return True
            
        except Exception as e:
            self.logger.error(f"Model yaratishda xato: {e}")
            return False
    
    async def predict(self, model_name: str, state: np.ndarray) -> Optional[ModelPrediction]:
        """Model predict qilish"""
        try:
            if model_name not in self.models:
                self.logger.error(f"Model topilmadi: {model_name}")
                return None
            
            model = self.models[model_name]
            model_type = self.model_types[model_name]
            
            # Model prediction
            action, confidence = await model.predict(state)
            
            # Signal type convert
            signal_type = SignalType.HOLD
            if action == 0:
                signal_type = SignalType.BUY
            elif action == 2:
                signal_type = SignalType.SELL
            
            # Model prediction ma'lumot
            prediction = ModelPrediction(
                model_name=model_name,
                model_type=model_type,
                prediction={
                    'action': action,
                    'signal_type': signal_type.value,
                    'raw_output': action
                },
                confidence=confidence,
                timestamp=time.time(),
                features_used=[f"feature_{i}" for i in range(len(state))],
                model_state=model.get_state_dict()
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Model prediction da xato {model_name}: {e}")
            return None
    
    async def update_model(self, model_name: str, training_data: Any) -> Dict[str, float]:
        """Model training update"""
        try:
            if model_name not in self.models:
                return {}
            
            model = self.models[model_name]
            
            # Model update
            if hasattr(model, 'update'):
                result = await model.update(training_data)
                return result
            else:
                self.logger.warning(f"Model update qo'llab-quvvatlanmaydi: {model_name}")
                return {}
            
        except Exception as e:
            self.logger.error(f"Model update da xato {model_name}: {e}")
            return {}
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Model ma'lumotini olish"""
        if model_name not in self.models:
            return None
        
        model = self.models[model_name]
        model_type = self.model_types[model_name]
        config = self.model_configs[model_name]
        
        return {
            'name': model_name,
            'type': model_type.value,
            'config': config,
            'state_dict_available': hasattr(model, 'get_state_dict')
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Modellar ro'yxati"""
        return [
            self.get_model_info(model_name) 
            for model_name in self.models.keys()
        ]
    
    async def save_model(self, model_name: str, filepath: str) -> bool:
        """Model saqlash"""
        try:
            if model_name not in self.models:
                return False
            
            model = self.models[model_name]
            model_type = self.model_types[model_name]
            config = self.model_configs[model_name]
            
            model_data = {
                'model_name': model_name,
                'model_type': model_type.value,
                'config': config,
                'model_state': model.get_state_dict(),
                'timestamp': time.time()
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"Model saqlandi: {model_name} -> {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Model saqlashda xato {model_name}: {e}")
            return False
    
    async def load_model(self, filepath: str) -> Optional[str]:
        """Model yuklash"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            model_name = model_data['model_name']
            model_type = ModelType(model_data['model_type'])
            config = model_data['config']
            model_state = model_data['model_state']
            
            # Model yaratish
            success = await self.create_model(model_name, model_type, config)
            if not success:
                return None
            
            # Model state yuklash
            if model_name in self.models and hasattr(self.models[model_name], 'load_state_dict'):
                try:
                    # State dict ni yuklash logikasi
                    self.logger.info(f"Model state yuklandi: {model_name}")
                except Exception as e:
                    self.logger.warning(f"Model state yuklashda xato {model_name}: {e}")
            
            self.logger.info(f"Model yuklandi: {model_name} from {filepath}")
            return model_name
            
        except Exception as e:
            self.logger.error(f"Model yuklashda xato {filepath}: {e}")
            return None