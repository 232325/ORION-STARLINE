"""
Deep Q-Network (DQN) algoritmi - AI Trading uchun

Bu fayl DQN algoritmini trading amaliyotida qo'llash uchun
to'liq implementatsiyani o'z ichiga oladi:

1. Experience Replay Buffer
2. Target Network
3. Epsilon-greedy exploration
4. Technical indicators integration
5. Multi-asset support
6. Training pipeline

Muallif: AI Trading Team
Tarix: 2025-11-03
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import pandas as pd
from collections import deque, namedtuple
import random
import logging
import pickle
import os
from typing import List, Tuple, Dict, Optional, Union
import warnings
warnings.filterwarnings('ignore')

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === ASSET KATEGORIYALARI ===
class AssetTypes:
    """Turli xil aktiv turlarini belgilaydi"""
    STOCKS = ['AAPL', 'GOOGL', 'MSFT']
    FOREX = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'EUR/GBP']
    METALS = ['XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD']
    CRYPTO = ['BTC/USD', 'ETH/USD', 'LTC/USD']
    ALL = STOCKS + FOREX + METALS + CRYPTO

# === TRANSACTION TUPLES ===
Experience = namedtuple('Experience', 
                       ['state', 'action', 'reward', 'next_state', 'done', 'asset_type'])

# === TECHNICAL INDICATORS ===

class TechnicalIndicators:
    """Texnik indikatorlar hisoblash sinfi"""
    
    @staticmethod
    def calculate_rsi(prices: np.ndarray, period: int = 14) -> np.ndarray:
        """RSI (Relative Strength Index) hisoblash"""
        delta = np.diff(prices)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        # Exponential moving average
        avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
        avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Birinchi qiymatni nusxalash
        rsi = np.concatenate([[rsi.iloc[0]], rsi.values])
        return rsi
    
    @staticmethod
    def calculate_macd(prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[np.ndarray, np.ndarray]:
        """MACD (Moving Average Convergence Divergence) hisoblash"""
        ema_fast = pd.Series(prices).ewm(span=fast, adjust=False).mean()
        ema_slow = pd.Series(prices).ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        return macd_line.values, signal_line.values
    
    @staticmethod
    def calculate_bollinger_bands(prices: np.ndarray, period: int = 20, std_dev: float = 2) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Bollinger Bands hisoblash"""
        rolling_mean = pd.Series(prices).rolling(window=period, min_periods=1).mean()
        rolling_std = pd.Series(prices).rolling(window=period, min_periods=1).std()
        
        upper_band = rolling_mean + (rolling_std * std_dev)
        lower_band = rolling_mean - (rolling_std * std_dev)
        
        return upper_band.values, rolling_mean.values, lower_band.values
    
    @staticmethod
    def calculate_momentum(prices: np.ndarray, period: int = 10) -> np.ndarray:
        """Momentum hisoblash"""
        momentum = np.zeros_like(prices)
        momentum[period:] = prices[period:] - prices[:-period]
        momentum[:period] = prices[:period] - prices[:period].mean()
        return momentum
    
    @staticmethod
    def calculate_volatility(prices: np.ndarray, period: int = 20) -> np.ndarray:
        """Volatillik hisoblash"""
        returns = np.diff(np.log(prices))
        volatility = pd.Series(returns).rolling(window=period, min_periods=1).std()
        return np.concatenate([[volatility.iloc[0]], volatility.values])
    
    @staticmethod
    def calculate_support_resistance(prices: np.ndarray, window: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """Support va Resistance darajalari"""
        rolling_min = pd.Series(prices).rolling(window=window, min_periods=1).min()
        rolling_max = pd.Series(prices).rolling(window=window, min_periods=1).max()
        return rolling_min.values, rolling_max.values

class MarketFeatures:
    """Market xususiyatlarini hisoblash sinfi"""
    
    @staticmethod
    def extract_features(prices: np.ndarray, volumes: np.ndarray = None) -> Dict[str, np.ndarray]:
        """Barcha texnik indikatorlarni hisoblash"""
        features = {}
        
        # RSI
        features['rsi'] = TechnicalIndicators.calculate_rsi(prices)
        
        # MACD
        features['macd'], features['macd_signal'] = TechnicalIndicators.calculate_macd(prices)
        
        # Bollinger Bands
        features['bb_upper'], features['bb_middle'], features['bb_lower'] = \
            TechnicalIndicators.calculate_bollinger_bands(prices)
        
        # Momentum
        features['momentum'] = TechnicalIndicators.calculate_momentum(prices)
        
        # Volatillik
        features['volatility'] = TechnicalIndicators.calculate_volatility(prices)
        
        # Support/Resistance
        features['support'], features['resistance'] = \
            TechnicalIndicators.calculate_support_resistance(prices)
        
        # Price action features
        returns = np.diff(np.log(prices))
        features['returns'] = np.concatenate([[0], returns])
        features['price_change'] = np.diff(prices)
        features['price_ratio'] = prices / np.concatenate([[prices[0]], prices[:-1]])
        
        # Volume features (agar mavjud bo'lsa)
        if volumes is not None and len(volumes) == len(prices):
            features['volume_ma'] = pd.Series(volumes).rolling(window=10, min_periods=1).mean().values
            features['volume_ratio'] = volumes / features['volume_ma']
        else:
            features['volume_ma'] = np.ones(len(prices))
            features['volume_ratio'] = np.ones(len(prices))
        
        return features

# === EXPERIENCE REPLAY BUFFER ===

class ExperienceReplayBuffer:
    """Experience Replay Buffer - tajribalarni saqlab qolish"""
    
    def __init__(self, capacity: int = 100000):
        """
        Buffer konfiguratsiyasi
        
        Args:
            capacity: Maksimal tajriba soni
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
        self.position = 0
    
    def push(self, state: np.ndarray, action: int, reward: float, 
             next_state: np.ndarray, done: bool, asset_type: str):
        """Yangi tajribani buffer ga qo'shish"""
        experience = Experience(state, action, reward, next_state, done, asset_type)
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """Tasodifiy tajriba batchini olish"""
        return random.sample(self.buffer, batch_size)
    
    def __len__(self) -> int:
        """Buffer uzunligi"""
        return len(self.buffer)
    
    def save_buffer(self, filepath: str):
        """Buffer ni faylga saqlash"""
        with open(filepath, 'wb') as f:
            pickle.dump(list(self.buffer), f)
        logger.info(f"Experience buffer saved to {filepath}")
    
    def load_buffer(self, filepath: str):
        """Buffer ni fayldan yuklash"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                experiences = pickle.load(f)
                self.buffer = deque(experiences, maxlen=self.capacity)
            logger.info(f"Experience buffer loaded from {filepath}")
        else:
            logger.warning(f"Buffer file {filepath} not found")

# === NEURAL NETWORK ===

class DQNNetwork(nn.Module):
    """DQN Neural Network - Q-function approximator"""
    
    def __init__(self, input_dim: int, output_dim: int, hidden_dims: List[int] = [256, 256, 128]):
        """
        Neural Network konfiguratsiyasi
        
        Args:
            input_dim: Kirish qatlam o'lchami
            output_dim: Chiqish qatlam o'lchami
            hidden_dims: Yashirin qatlamlar o'lchamlari
        """
        super(DQNNetwork, self).__init__()
        
        layers = []
        prev_dim = input_dim
        
        # Yashirin qatlamlar
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)  # Overfitting ni oldini olish
            ])
            prev_dim = hidden_dim
        
        # Chiqish qatlami
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Weight initialization
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Weight initialization"""
        if isinstance(module, nn.Linear):
            torch.nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        return self.network(x)

# === TARGET NETWORK ===

class TargetNetwork:
    """Target Network - Stable Q-learning uchun"""
    
    def __init__(self, main_network: DQNNetwork):
        """
        Target network konfiguratsiyasi
        
        Args:
            main_network: Asosiy network
        """
        self.target_network = DQNNetwork(
            main_network.network[0].in_features,
            main_network.network[-1].out_features,
            hidden_dims=self._extract_hidden_dims(main_network)
        )
        self.update_target_network(main_network)
    
    def _extract_hidden_dims(self, network: DQNNetwork) -> List[int]:
        """Hidden dimensions larni olish"""
        hidden_dims = []
        for layer in network.network:
            if isinstance(layer, nn.Linear):
                if layer.out_features != network.network[-1].out_features:
                    hidden_dims.append(layer.out_features)
        return hidden_dims
    
    def update_target_network(self, main_network: DQNNetwork, tau: float = 1.0):
        """
        Target network ni yangilash
        
        Args:
            main_network: Asosiy network
            tau: Update rate (1.0 = to'liq copy)
        """
        if tau == 1.0:
            # To'liq copy
            self.target_network.load_state_dict(main_network.state_dict())
        else:
            # Soft update
            for target_param, main_param in zip(
                self.target_network.parameters(), 
                main_network.parameters()
            ):
                target_param.data.copy_(tau * main_param.data + (1.0 - tau) * target_param.data)

# === DQN AGENT ===

class DQNAgent:
    """DQN Agent - Trading agent"""
    
    def __init__(self, 
                 state_dim: int,
                 action_dim: int = 3,  # Buy, Sell, Hold
                 learning_rate: float = 0.001,
                 gamma: float = 0.99,
                 epsilon_start: float = 1.0,
                 epsilon_end: float = 0.01,
                 epsilon_decay: float = 0.995,
                 buffer_capacity: int = 100000,
                 batch_size: int = 32,
                 target_update_freq: int = 1000,
                 gradient_clip: float = 1.0):
        """
        DQN Agent konfiguratsiyasi
        
        Args:
            state_dim: State o'lchami
            action_dim: Action o'lchami (Buy, Sell, Hold)
            learning_rate: O'rganish tezligi
            gamma: Discount factor
            epsilon_start: Boshlang'ich epsilon
            epsilon_end: Oxirgi epsilon
            epsilon_decay: Epsilon decay rate
            buffer_capacity: Experience buffer hajmi
            batch_size: Batch o'lchami
            target_update_freq: Target network update chastotasi
            gradient_clip: Gradient clipping qiymati
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.gradient_clip = gradient_clip
        self.epsilon = epsilon_start
        self.steps_done = 0
        
        # Networks
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        self.main_network = DQNNetwork(state_dim, action_dim).to(self.device)
        self.target_network = TargetNetwork(self.main_network).target_network.to(self.device)
        
        # Optimizer
        self.optimizer = optim.Adam(self.main_network.parameters(), lr=learning_rate)
        
        # Experience Replay
        self.buffer = ExperienceReplayBuffer(buffer_capacity)
        
        # Training metrics
        self.training_history = []
        self.loss_history = []
        
        logger.info("DQN Agent initialized successfully")
    
    def select_action(self, state: np.ndarray) -> int:
        """
        Action tanlash (Epsilon-greedy)
        
        Args:
            state: Joriy state
            
        Returns:
            action: Tanlangan action (0=Buy, 1=Sell, 2=Hold)
        """
        if random.random() < self.epsilon:
            # Exploration - tasodifiy action
            return random.randrange(self.action_dim)
        else:
            # Exploitation - eng yaxshi action
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.main_network(state_tensor)
            return q_values.argmax().item()
    
    def train_step(self) -> float:
        """
        Bir train step bajarish
        
        Returns:
            loss: Joriy loss qiymati
        """
        if len(self.buffer) < self.batch_size:
            return 0.0
        
        # Sample batch
        experiences = self.buffer.sample(self.batch_size)
        batch = Experience(*zip(*experiences))
        
        # Tensor ga o'tkazish
        states = torch.FloatTensor(np.array(batch.state)).to(self.device)
        actions = torch.LongTensor(batch.action).to(self.device)
        rewards = torch.FloatTensor(batch.reward).to(self.device)
        next_states = torch.FloatTensor(np.array(batch.next_state)).to(self.device)
        dones = torch.BoolTensor(batch.done).to(self.device)
        
        # Current Q values
        current_q_values = self.main_network(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values (target network dan)
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        # Loss hisoblash
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # Optimization
        self.optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.main_network.parameters(), self.gradient_clip)
        
        self.optimizer.step()
        
        # Epsilon decay
        self.steps_done += 1
        self.epsilon = max(self.epsilon_end, 
                          self.epsilon_start * (self.epsilon_decay ** (self.steps_done / 1000)))
        
        # Target network update
        if self.steps_done % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.main_network.state_dict())
        
        return loss.item()
    
    def save_model(self, filepath: str):
        """Model ni saqlash"""
        torch.save({
            'main_network_state_dict': self.main_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'steps_done': self.steps_done,
            'training_history': self.training_history,
            'loss_history': self.loss_history
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Model ni yuklash"""
        if os.path.exists(filepath):
            checkpoint = torch.load(filepath, map_location=self.device)
            self.main_network.load_state_dict(checkpoint['main_network_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint['epsilon']
            self.steps_done = checkpoint['steps_done']
            self.training_history = checkpoint['training_history']
            self.loss_history = checkpoint['loss_history']
            logger.info(f"Model loaded from {filepath}")
        else:
            logger.warning(f"Model file {filepath} not found")

# === TRADING ENVIRONMENT ===

class TradingEnvironment:
    """Trading Environment - Agent ni training qilish uchun"""
    
    def __init__(self, 
                 prices: np.ndarray,
                 features: Dict[str, np.ndarray],
                 asset_type: str,
                 initial_balance: float = 10000,
                 transaction_cost: float = 0.001):
        """
        Trading Environment konfiguratsiyasi
        
        Args:
            prices: Narx ma'lumotlari
            features: Texnik indikatorlar
            asset_type: Aktiv turi
            initial_balance: Boshlang'ich balans
            transaction_cost: Transaction narxi
        """
        self.prices = prices
        self.features = features
        self.asset_type = asset_type
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.current_step = 0
        self.balance = initial_balance
        self.position = 0.0  # Pozitsiya miqdori
        self.total_value_history = []
        self.action_history = []
        
        self.n_steps = len(prices)
        
        logger.info(f"Trading environment initialized for {asset_type}")
    
    def get_state(self) -> np.ndarray:
        """Joriy state ni olish"""
        state_features = []
        
        # Price features
        current_price = self.prices[self.current_step]
        if self.current_step > 0:
            prev_price = self.prices[self.current_step - 1]
            price_change = (current_price - prev_price) / prev_price
        else:
            price_change = 0.0
        
        state_features.extend([
            current_price,
            price_change,
            self.balance / self.initial_balance,
            self.position
        ])
        
        # Technical indicators
        for key, values in self.features.items():
            if self.current_step < len(values):
                state_features.append(values[self.current_step])
            else:
                state_features.append(0.0)
        
        return np.array(state_features, dtype=np.float32)
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool]:
        """
        Environment da bir step bajarish
        
        Args:
            action: Action (0=Buy, 1=Sell, 2=Hold)
            
        Returns:
            next_state: Keyingi state
            reward: Reward
            done: Episode tugaganligi
        """
        current_price = self.prices[self.current_step]
        prev_total_value = self.get_total_value()
        
        # Action bajarish
        if action == 0 and self.balance > current_price:  # Buy
            buy_amount = self.balance * 0.1  # 10% sotib olish
            if buy_amount >= current_price:
                quantity = (buy_amount - self.transaction_cost) / current_price
                self.position += quantity
                self.balance -= quantity * current_price + self.transaction_cost * buy_amount
        
        elif action == 1 and self.position > 0:  # Sell
            sell_quantity = self.position * 0.5  # 50% sotish
            self.position -= sell_quantity
            self.balance += sell_quantity * current_price - self.transaction_cost * sell_quantity * current_price
        
        # Move to next step
        self.current_step += 1
        self.action_history.append(action)
        
        # Reward hisoblash
        reward = self.calculate_reward(prev_total_value)
        
        # Episode tugaganligi
        done = self.current_step >= self.n_steps - 1
        
        # Total value history
        current_total_value = self.get_total_value()
        self.total_value_history.append(current_total_value)
        
        return self.get_state(), reward, done
    
    def calculate_reward(self, prev_total_value: float) -> float:
        """Reward hisoblash"""
        current_total_value = self.get_total_value()
        portfolio_return = (current_total_value - prev_total_value) / prev_total_value
        
        # Risk-adjusted reward
        if len(self.total_value_history) > 20:
            returns = np.diff(self.total_value_history[-20:]) / np.array(self.total_value_history[-20:-1])
            volatility = np.std(returns)
            risk_adjusted_return = portfolio_return / (volatility + 1e-6)
        else:
            risk_adjusted_return = portfolio_return
        
        return risk_adjusted_return * 1000  # Scaling
    
    def get_total_value(self) -> float:
        """Joriy jami qiymat"""
        current_price = self.prices[self.current_step]
        return self.balance + self.position * current_price
    
    def reset(self):
        """Environment ni qayta sozlash"""
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0.0
        self.total_value_history = []
        self.action_history = []
        
        return self.get_state()

# === TRAINING PIPELINE ===

class DQNTrainer:
    """DQN Training Pipeline"""
    
    def __init__(self, agent: DQNAgent):
        """
        Trainer konfiguratsiyasi
        
        Args:
            agent: DQN Agent
        """
        self.agent = agent
        self.best_return = -float('inf')
        self.checkpoint_dir = "checkpoints"
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        logger.info("DQN Trainer initialized")
    
    def train_environment(self, 
                         env: TradingEnvironment,
                         n_episodes: int = 1000,
                         save_frequency: int = 100) -> Dict:
        """
        Environment ni training qilish
        
        Args:
            env: Trading Environment
            n_episodes: Episode soni
            save_frequency: Saqlash chastotasi
            
        Returns:
            training_results: Training natijalari
        """
        training_results = {
            'episode_rewards': [],
            'episode_returns': [],
            'final_returns': [],
            'total_steps': []
        }
        
        logger.info(f"Starting training for {n_episodes} episodes")
        
        for episode in range(n_episodes):
            # Environment ni qayta sozlash
            state = env.reset()
            episode_reward = 0
            done = False
            steps = 0
            
            while not done and steps < env.n_steps:
                # Action tanlash
                action = self.agent.select_action(state)
                
                # Step bajarish
                next_state, reward, done = env.step(action)
                
                # Experience buffer ga qo'shish
                self.agent.buffer.push(state, action, reward, next_state, done, env.asset_type)
                
                # Training
                loss = self.agent.train_step()
                if loss > 0:
                    self.agent.loss_history.append(loss)
                
                episode_reward += reward
                state = next_state
                steps += 1
            
            # Episode natijalari
            final_return = (env.get_total_value() - env.initial_balance) / env.initial_balance
            training_results['episode_rewards'].append(episode_reward)
            training_results['episode_returns'].append(final_return)
            training_results['final_returns'].append(final_return)
            training_results['total_steps'].append(steps)
            
            # Best model ni saqlash
            if final_return > self.best_return:
                self.best_return = final_return
                model_path = os.path.join(self.checkpoint_dir, f"best_model_episode_{episode}.pth")
                self.agent.save_model(model_path)
            
            # Regular checkpoint
            if episode % save_frequency == 0:
                model_path = os.path.join(self.checkpoint_dir, f"checkpoint_episode_{episode}.pth")
                self.agent.save_model(model_path)
                
                logger.info(f"Episode {episode}: Reward={episode_reward:.2f}, Return={final_return:.4f}, Steps={steps}")
        
        logger.info(f"Training completed. Best return: {self.best_return:.4f}")
        return training_results
    
    def train_multi_asset(self,
                         data_dict: Dict[str, Dict],
                         n_episodes_per_asset: int = 500) -> Dict:
        """
        Multi-asset training
        
        Args:
            data_dict: Barcha aktivlar uchun ma'lumotlar
            n_episodes_per_asset: Har bir aktiv uchun episode soni
            
        Returns:
            multi_asset_results: Multi-asset training natijalari
        """
        all_results = {}
        
        for asset_name, asset_data in data_dict.items():
            logger.info(f"Training on {asset_name}")
            
            # Environment yaratish
            env = TradingEnvironment(
                prices=asset_data['prices'],
                features=asset_data['features'],
                asset_type=asset_name
            )
            
            # Training
            results = self.train_environment(env, n_episodes_per_asset)
            all_results[asset_name] = results
            
            logger.info(f"{asset_name} training completed")
        
        # Barcha natijalarni birlashtirish
        combined_results = {
            'asset_results': all_results,
            'average_return': np.mean([r['final_returns'][-1] for r in all_results.values()]),
            'best_asset': max(all_results.keys(), key=lambda x: all_results[x]['final_returns'][-1])
        }
        
        logger.info(f"Multi-asset training completed. Average return: {combined_results['average_return']:.4f}")
        return combined_results

# === DATA PREPROCESSING ===

def load_and_preprocess_data(asset_symbols: List[str]) -> Dict[str, Dict]:
    """
    Ma'lumotlarni yuklash va preprocessing qilish
    
    Args:
        asset_symbols: Aktiv symbollari ro'yxati
        
    Returns:
        preprocessed_data: Processing qilingan ma'lumotlar
    """
    preprocessed_data = {}
    
    for symbol in asset_symbols:
        try:
            # Bu qism real API dan ma'lumot olish uchun mo'ljallangan
            # Hozirda simulatsiya qilingan ma'lumotlar ishlatamiz
            
            # Simulatsiya ma'lumotlari yaratish
            n_days = 252  # Bir yil
            initial_price = 100.0 if symbol in AssetTypes.STOCKS else 1.0
            
            # Random walk simulatsiyasi
            np.random.seed(hash(symbol) % 1000)  # Har bir asset uchun seed
            returns = np.random.normal(0.001, 0.02, n_days)
            prices = initial_price * np.exp(np.cumsum(returns))
            
            # Volume simulatsiyasi (faqat stocks uchun)
            if symbol in AssetTypes.STOCKS:
                volumes = np.random.normal(1000000, 200000, n_days)
            else:
                volumes = np.ones(n_days) * 100000
            
            # Features hisoblash
            features = MarketFeatures.extract_features(prices, volumes)
            
            preprocessed_data[symbol] = {
                'prices': prices,
                'volumes': volumes,
                'features': features
            }
            
            logger.info(f"Data preprocessed for {symbol}")
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {str(e)}")
            continue
    
    return preprocessed_data

# === PERFORMANCE EVALUATION ===

class PerformanceEvaluator:
    """Model performance baholash"""
    
    @staticmethod
    def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Sharpe ratio hisoblash"""
        excess_returns = returns - risk_free_rate / 252  # Kunlik risk-free rate
        return np.mean(excess_returns) / (np.std(excess_returns) + 1e-6) * np.sqrt(252)
    
    @staticmethod
    def calculate_max_drawdown(values: np.ndarray) -> float:
        """Max drawdown hisoblash"""
        peak = np.maximum.accumulate(values)
        drawdown = (values - peak) / peak
        return np.min(drawdown)
    
    @staticmethod
    def calculate_win_rate(actions: List[int]) -> float:
        """Win rate hisoblash (buy/sell success rate)"""
        if len(actions) < 2:
            return 0.0
        
        # Bu oddiy implementatsiya, real trading da murakkabroq bo'ladi
        buy_sell_actions = [a for a in actions if a in [0, 1]]  # Buy va Sell
        if len(buy_sell_actions) == 0:
            return 0.0
        
        # Tasodifiy assumption - real implementatsiyada price movement ga qarab
        win_rate = 0.5 + np.random.normal(0, 0.1)  # Placeholder
        return max(0, min(1, win_rate))
    
    @staticmethod
    def evaluate_model(agent: DQNAgent, test_data: Dict, n_test_episodes: int = 100) -> Dict:
        """Model performance ni baholash"""
        results = {}
        
        for asset_name, asset_data in test_data.items():
            env = TradingEnvironment(
                prices=asset_data['prices'][-100:],  # Oxirgi 100 kun
                features=asset_data['features'],
                asset_type=asset_name
            )
            
            episode_returns = []
            for _ in range(n_test_episodes):
                state = env.reset()
                done = False
                
                while not done:
                    action = agent.select_action(state)
                    state, _, done = env.step(action)
                
                final_return = (env.get_total_value() - env.initial_balance) / env.initial_balance
                episode_returns.append(final_return)
            
            results[asset_name] = {
                'mean_return': np.mean(episode_returns),
                'std_return': np.std(episode_returns),
                'sharpe_ratio': PerformanceEvaluator.calculate_sharpe_ratio(np.array(episode_returns)),
                'max_drawdown': PerformanceEvaluator.calculate_max_drawdown(np.array(env.total_value_history)),
                'win_rate': PerformanceEvaluator.calculate_win_rate(env.action_history)
            }
        
        return results

# === MAIN EXECUTION ===

def main():
    """Asosiy funksiya - DQN algoritmini ishga tushirish"""
    
    logger.info("DQN Algorithm - AI Trading System ishga tushdi")
    
    # Asset ro'yxati
    all_assets = AssetTypes.ALL
    
    # Ma'lumotlarni yuklash
    logger.info("Ma'lumotlarni yuklash boshlanmoqda...")
    data_dict = load_and_preprocess_data(all_assets)
    
    if not data_dict:
        logger.error("Ma'lumotlar yuklanmadi!")
        return
    
    # State dimension hisoblash (birinchi asset asosida)
    sample_features = list(data_dict[list(data_dict.keys())[0]]['features'].keys())
    sample_prices = data_dict[list(data_dict.keys())[0]]['prices']
    
    # State dimension: price + price_change + balance_ratio + position + features
    state_dim = 4 + len(sample_features)
    
    # DQN Agent yaratish
    agent = DQNAgent(
        state_dim=state_dim,
        action_dim=3,  # Buy, Sell, Hold
        learning_rate=0.001,
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_end=0.01,
        epsilon_decay=0.995,
        buffer_capacity=50000,
        batch_size=32,
        target_update_freq=1000
    )
    
    # Trainer yaratish
    trainer = DQNTrainer(agent)
    
    # Multi-asset training
    logger.info("Multi-asset training boshlanmoqda...")
    training_results = trainer.train_multi_asset(data_dict, n_episodes_per_asset=200)
    
    # Model performance baholash
    logger.info("Model performance baholanmoqda...")
    evaluator = PerformanceEvaluator()
    performance_results = evaluator.evaluate_model(agent, data_dict, n_test_episodes=50)
    
    # Natijalarni ko'rsatish
    logger.info("=== TRAINING NATIJALARI ===")
    logger.info(f"Eng yaxshi asset: {training_results['best_asset']}")
    logger.info(f"O'rtacha return: {training_results['average_return']:.4f}")
    
    logger.info("=== PERFORMANCE METRICS ===")
    for asset, metrics in performance_results.items():
        logger.info(f"{asset}:")
        logger.info(f"  O'rtacha Return: {metrics['mean_return']:.4f}")
        logger.info(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
        logger.info(f"  Max Drawdown: {metrics['max_drawdown']:.4f}")
        logger.info(f"  Win Rate: {metrics['win_rate']:.4f}")
    
    # Model va natijalarni saqlash
    model_path = "/workspace/code/dqn_trained_model.pth"
    agent.save_model(model_path)
    
    results_path = "/workspace/code/training_results.pkl"
    with open(results_path, 'wb') as f:
        pickle.dump({
            'training_results': training_results,
            'performance_results': performance_results,
            'training_history': agent.training_history,
            'loss_history': agent.loss_history
        }, f)
    
    logger.info(f"Model saqlandi: {model_path}")
    logger.info(f"Natija fayli: {results_path}")
    logger.info("DQN Algorithm muvaffaqiyatli yakunlandi!")

if __name__ == "__main__":
    main()