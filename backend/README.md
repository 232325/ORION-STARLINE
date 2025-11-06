# Multi-Asset Trading Signal Generator

## Ta'rif

Bu loyiha ko'p aktivli (multi-asset) trading signal generator tizimidir. Real-time ma'lumotlar qayta ishlash, texnik tahlil va machine learning integratsiyasi bilan ishlaydi.

## 🏗️ Tizim Komponentlari

### 🤖 Machine Learning (A2C Algorithm)
- **Actor-Critic Architecture**: Actor (strategiya) va Critic (qiymat funksiyasi) tarmoqlari
- **Advantage Function**: Generalized Advantage Estimation (GAE) ishlatiladi
- **Asynchronous Updates**: Tez va barqaror o'rganish
- **Entropy Regularization**: Exploration uchun entropy bonus
- **Portfolio Allocation**: Naktivli portfel vaznlarini optimal taqsimlash

### 📊 Trading Signal Generator
- **Real-time Signal Generation**: Har soniyada signal yaratish
- **Multi-Timeframe Analysis**: Turli vaqt oralig'larida tahlil
- **Technical Indicators**: 15+ texnik indikatorlar
- **Risk Management**: Stop-loss va take-profit hisoblash
- **Confidence Scoring**: Signal ishonchlilik baholash
- **Multi-Asset Support**: Aksialar, forex, metallar

## 📈 Trading Signal Generator

### Asosiy Xususiyatlar

#### 🏦 Aktiv Turlari
- **Aksialar**: AAPL, GOOGL, MSFT, TSLA, NVDA
- **Forex**: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD  
- **Metalllar**: Oltin (GC=F), Kumush (SI=F), Platina (PL=F), Palladiy (PA=F)

#### 📊 Texnik Indikatorlar
- **Moving Averages**: SMA, EMA, WMA (turli davrlar)
- **Momentum Indicators**: RSI, MACD, Stochastic Oscillator
- **Volatility Indicators**: Bollinger Bands, ATR
- **Volume Indicators**: Volume analysis, OBV
- **Custom Indicators**: Metall/Forex uchun maxsus indikatorlar

#### 🎯 Signal Turlari
- **STRONG_BUY**: 80%+ ishonchlilik
- **BUY**: 65-80% ishonchlilik  
- **HOLD**: 35-65% ishonchlilik
- **SELL**: 20-35% ishonchlilik
- **STRONG_SELL**: <20% ishonchlilik

#### 📈 Signal Komponentlari
- **Entry Price**: Kirish narxi
- **Stop Loss**: Zarar cheklash darajasi
- **Take Profit**: Foyda olish darajasi
- **Position Size**: Pozitsiya o'lchami
- **Confidence Score**: Signal ishonchlilik ko'rsatkichi
- **Reasoning**: Signal asoslari

### Tez Boshlash

```python
from trading_signal_generator import TradingSignalGenerator

# Generator yaratish
generator = TradingSignalGenerator()

# Bitta aktiv uchun signal olish
signal = generator.generate_signal("AAPL", timeframe="1h", account_balance=10000)

if signal:
    print(f"Signal: {signal.signal_type.value}")
    print(f"Confidence: {signal.confidence:.2f}")
    print(f"Entry Price: ${signal.entry_price:.2f}")
    print(f"Stop Loss: ${signal.stop_loss:.2f}")
    print(f"Take Profit: ${signal.take_profit:.2f}")
    print(f"Position Size: ${signal.position_size:.2f}")

# Ko'p aktivlar uchun signallar
signals = generator.generate_signals_for_all(account_balance=10000)

# Multi-timeframe analysis
mtf_signal = generator.generate_multi_timeframe_signal("TSLA")

# Real-time monitoring
generator.start_real_time_generation(["AAPL", "GOOGL", "EURUSD=X"])
signal_queue = generator.get_signal_queue()
signal_data = signal_queue.get()  # Real-time signal
```

### O'rnatish

```bash
# Kerakli kutubxonalar
pip install -r requirements.txt

# TA-Lib o'rnatish (muhim)
# Windows:
pip install TA-Lib

# macOS:
brew install ta-lib && pip install TA-Lib

# Linux:
sudo apt-get install ta-lib-dev && pip install TA-Lib
```

### Foydalanish Misollari

#### 1. Asosiy Signal Generatsiyasi
```python
# AAPL uchun 1 soatlik signal
signal = generator.generate_signal("AAPL", timeframe="1h", account_balance=15000)

print(f"Symbol: {signal.symbol}")
print(f"Signal: {signal.signal_type.value}")
print(f"Current Price: ${signal.current_price:.2f}")
print(f"Reasoning: {signal.reasoning}")

# Texnik indikatorlar
for indicator, value in signal.indicators.items():
    print(f"{indicator}: {value:.4f}")
```

#### 2. Ko'p Vaqt Oralig'i Tahlili
```python
# Ensemble signal - ko'p vaqt oralig'i tahlili
mtf_signal = generator.generate_multi_timeframe_signal("EURUSD=X")

print(f"Timeframe: {mtf_signal.timeframe}")
print(f"Ensemble Signal: {mtf_signal.signal_type.value}")
print(f"Confidence: {mtf_signal.confidence:.2f}")
```

#### 3. Real-time Monitoring
```python
# Real-time monitoring boshlash
symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "EURUSD=X", "GC=F"]
generator.start_real_time_generation(symbols=symbols, interval=60)

# Signallarni olish
signal_queue = generator.get_signal_queue()
while True:
    signal_data = signal_queue.get()  # Blocking call
    signal = signal_data['signal']
    timestamp = signal_data['timestamp']
    
    print(f"[{timestamp}] {signal.symbol}: {signal.signal_type.value}")
    
# To'xtatish
generator.stop_real_time_generation()
```

#### 4. Ma'lumot Sifati Validatsiyasi
```python
# Ma'lumotlar sifati tekshirish
quality = generator.validate_data_quality("AAPL", timeframe="1h")

print(f"Quality Score: {quality['quality_score']}/100")
if quality['issues']:
    for issue in quality['issues']:
        print(f"Issue: {issue}")
```

#### 5. Export va Hisobot
```python
# Signallarni faylga eksport qilish
signals = generator.generate_signals_for_all(account_balance=25000)
export_file = generator.export_signals(signals, "daily_signals.json")

print(f"Signals exported to: {export_file}")

# JSON formatda ko'rish
with open(export_file, 'r') as f:
    data = json.load(f)
    
for symbol, signal_data in data.items():
    print(f"{symbol}: {signal_data['signal_type']} (Conf: {signal_data['confidence']:.2f})")
```

## Asosiy Xususiyatlar

### 🤖 Core Algorithm
- **Actor-Critic Architecture**: Actor (strategiya) va Critic (qiymat funksiyasi) tarmoqlari
- **Advantage Function**: Generalized Advantage Estimation (GAE) ishlatiladi
- **Asynchronous Updates**: Tez va barqaror o'rganish
- **Entropy Regularization**: Exploration uchun entropy bonus

### 📊 Multi-Asset Trading
- **Portfolio Allocation**: Naktivli portfel vaznlarini optimal taqsimlash
- **Cross-Asset Correlation**: Aktivlar o'rtasidagi bog'liqlikni hisobga olish
- **Risk Parity**: Riskni teng taqsimlash
- **Market Regime Detection**: Bozorni rejimlarini aniqlash

### 🎯 Training Optimizations
- **Advantage Normalization**: Training barqarorligi
- **Gradient Clipping**: Exploding gradient oldini olish
- **Learning Rate Scheduling**: Adaptive o'rganish tezligi
- **Experience Buffer**: Ma'lumotlarni saqlash

### 🏗️ Architecture
- **Shared Feature Extractor**: LSTM bilan jihozlangan umumiy feature extractor
- **Actor Head**: Action probabilities (portfolio weights + cash allocation)
- **Critic Head**: State value estimates
- **LSTM Integration**: Ketma-ket ma'lumotlarni model qilish

### 💰 Reward Shaping
- **Risk-Adjusted Returns**: Riskni hisobga olgan daromadlar
- **Transaction Cost Penalties**:.transaction cost jarimalari
- **Slippage Consideration**: Slippage ni hisobga olish
- **Maximum Drawdown Constraints**: Maksimal drawdown cheklovlari

## O'rnatish va Foydalanish

### Asosiy Foydalanish

```python
from a2c_algorithm import AdvantageA2C, TradingConfig
import torch

# Konfiguratsiya yaratish
config = TradingConfig(
    n_assets=10,
    learning_rate=0.0001,
    gamma=0.99,
    max_position=0.25
)

# Agent yaratish
agent = AdvantageA2C(config, input_dim=20)

# Training
trainer = A2CTrainer(agent)
stats = trainer.train_episode(environment)
```

### Turli Strategiyalar

```python
from a2c_config import get_config, PREDEFINED_CONFIGS

# Konservativ strategiya
config = get_config('conservative')

# Agressiv strategiya  
config = get_config('aggressive')

# Balansli strategiya
config = get_config('balanced')

# Scalping strategiya
config = get_config('scalping')
```

### Custom Konfiguratsiya

```python
from a2c_algorithm import TradingConfig

config = TradingConfig(
    n_assets=15,
    max_position=0.2,
    transaction_cost=0.0008,
    slippage=0.0003,
    learning_rate=0.00005,
    gamma=0.995,
    max_drawdown=0.1,
    lookback_window=80,
    hidden_size=384,
    lstm_layers=3
)
```

## Fayl Struktura

```
code/
├── trading_signal_generator.py  # Asosiy signal generator tizimi
├── config.py                    # Umumiy konfiguratsiya
├── example_usage.py             # Foydalanish misollari
├── requirements.txt             # Kutubxona talablari
├── a2c_algorithm.py            # A2C ML algoritmi
├── a2c_config.py               # A2C konfiguratsiya parametrlari
├── dqn_algorithm.py            # DQN algoritmi
├── ppo_algorithm.py            # PPO algoritmi
├── test_a2c.py                 # A2C test skripti
├── test_dqn.py                 # DQN test skripti
└── README.md                   # Bu fayl
```

## Algoritm Komponentlari

### 1. SharedFeatureExtractor

LSTM asosidagi feature extractor - ketma-ket ma'lumotlarni qayta ishlaydi:

```python
class SharedFeatureExtractor(nn.Module):
    def __init__(self, input_dim, hidden_size, lstm_layers=2):
        self.lstm = nn.LSTM(input_dim, hidden_size, lstm_layers)
        self.dense1 = nn.Linear(hidden_size, hidden_size)
        self.dense2 = nn.Linear(hidden_size, hidden_size // 2)
```

### 2. Actor Head

Portfolio vaznlarini va cash allocation ni hisoblaydi:

```python
class ActorHead(nn.Module):
    def forward(self, x):
        weights_logits = self.weight_head(x)  # Portfolio weights
        cash_logits = self.cash_head(x)       # Cash allocation
        
        weights = F.softmax(weights_logits, dim=-1)
        cash_prob = torch.sigmoid(cash_logits)
        
        return weights, cash_prob
```

### 3. Critic Head

State value ni baholaydi:

```python
class CriticHead(nn.Module):
    def forward(self, x):
        x = F.relu(self.dense1(x))
        x = F.relu(self.dense2(x))
        value = self.value_head(x)
        return value
```

### 4. Risk Management

Risk parity va market regime detection:

```python
class RiskParity:
    def calculate_weights(self, asset_names):
        # Risk parity weights hisoblash
        returns_matrix = self.get_returns_matrix()
        cov_matrix = np.cov(returns_matrix.T)
        inv_vol = 1.0 / (np.diag(cov_matrix) + 1e-8)
        return inv_vol / np.sum(inv_vol)

class MarketRegimeDetector:
    def detect_regime(self):
        # High/Low volatility, Positive/Negative return regimes
        recent_vol = np.mean(list(self.volatility_history)[-5:])
        recent_return = np.mean(list(self.return_history)[-5:])
        # Return appropriate regime
```

### 5. Advantage Calculation

Generalized Advantage Estimation (GAE):

```python
def calculate_advantage(self, rewards, values, dones, next_value):
    advantages = []
    advantage = 0
    
    for i in reversed(range(len(rewards))):
        next_non_terminal = 1.0 - dones[i]
        next_val = next_value if i == len(rewards) - 1 else values[i + 1]
        
        delta = rewards[i] + self.config.gamma * next_val * next_non_terminal - values[i]
        advantage = delta + self.config.gamma * self.config.gamma * next_non_terminal * advantage
        advantages.insert(0, advantage)
    
    advantages = torch.stack(advantages)
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
    
    return advantages.detach(), (advantages + torch.stack(values)).detach()
```

### 6. Reward Shaping

Trading uchun mo'ljallangan reward shaping:

```python
def calculate_reward(self, portfolio_return, action, prev_action, market_regime):
    base_reward = portfolio_return * 100
    
    # Transaction cost penalty
    if prev_action is not None:
        action_diff = torch.abs(action - prev_action).sum()
        transaction_penalty = -action_diff * self.config.transaction_cost * 100
        base_reward += transaction_penalty
    
    # Market regime adjustment
    regime_multiplier = {
        'high_vol_positive': 1.2,
        'high_vol_negative': 0.8,
        'low_vol_positive': 1.1,
        'low_vol_negative': 0.9
    }.get(market_regime, 1.0)
    
    return base_reward * regime_multiplier
```

## Training Process

### 1. Experience Collection

```python
def train_episode(self, env, max_steps=1000):
    state = env.reset()
    total_reward = 0
    experiences = []
    
    for step in range(max_steps):
        # Action selection
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        action, value, log_prob = self.select_action(state_tensor, training=True)
        
        # Environment step
        next_state, reward, done, info = env.step(action.cpu().numpy())
        
        # Experience storage
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
```

### 2. Network Update

```python
def update_network(self, experiences):
    states = torch.stack([exp.state for exp in experiences])
    actions = torch.stack([exp.action for exp in experiences])
    
    # Forward pass
    (weights, cash_probs), values = self.network(states)
    
    # Calculate advantages
    advantages, returns = self.calculate_advantage(rewards, values, dones, next_value)
    
    # Policy loss
    ratio = torch.exp(current_log_probs - old_log_probs)
    policy_loss = -torch.mean(torch.min(
        ratio * advantages,
        torch.clamp(ratio, 1 - 0.2, 1 + 0.2) * advantages
    ))
    
    # Value loss
    value_loss = F.mse_loss(values.squeeze(-1), returns)
    
    # Total loss
    total_loss = (
        policy_loss + 
        self.config.value_loss_coef * value_loss - 
        self.config.beta_entropy * entropy_bonus
    )
    
    # Gradient clipping
    torch.nn.utils.clip_grad_norm_(self.network.parameters(), self.config.max_grad_norm)
```

## Test va Validatsiya

```bash
# Test skriptini ishga tushirish
python test_a2c.py
```

Test quyidagilarni tekshiradi:
- ✅ Forward pass to'g'riligi
- ✅ Action selection
- ✅ Network update
- ✅ Risk management
- ✅ Performance benchmark

## Konfiguratsiya Variants

### Conservative Strategy
```python
config = ConservativeConfig(
    max_position=0.15,  # Kam risk
    learning_rate=0.00005,
    gamma=0.995
)
```

### Aggressive Strategy
```python
config = AggressiveConfig(
    max_position=0.35,  # Yuqori risk
    learning_rate=0.0003,
    gamma=0.98
)
```

### Scalping Strategy
```python
config = ScalpingConfig(
    lookback_window=15,  # Qisqa vaqt oynasi
    learning_rate=0.0005,
    gamma=0.92
)
```

## Performance Optimizatsiya

### Hardware Requirements
- **GPU**: NVIDIA CUDA compatible GPU (tavsiya etiladi)
- **RAM**: Kamida 8GB
- **CPU**: Multi-core processor

### Training Optimizations
```python
# Gradient accumulation
accumulation_steps = 4
effective_batch_size = config.batch_size * accumulation_steps

# Mixed precision training
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

# Multiple workers
config.n_workers = torch.get_num_threads()
```

### Memory Management
```python
# Experience replay buffer size
experience_buffer = deque(maxlen=config.n_steps * config.n_workers)

# Model checkpointing
torch.save({
    'network_state_dict': self.network.state_dict(),
    'optimizer_state_dict': self.optimizer.state_dict(),
    'training_stats': self.training_stats
}, filepath)
```

## Monitoring va Logging

### Training Metrics
- **Episode Reward**: Har bir episode uchun jami reward
- **Policy Loss**: Actor (policy) loss qiymati
- **Value Loss**: Critic (value) loss qiymati
- **Entropy**: Exploration darajasi
- **Advantages Mean**: Advantage qiymatlari o'rtachasi

### Visualization
```python
import matplotlib.pyplot as plt

def plot_training_stats(agent):
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.plot(agent.training_stats['returns'])
    plt.title('Episode Returns')
    
    plt.subplot(1, 3, 2)
    plt.plot(agent.training_stats['total_loss'])
    plt.title('Total Loss')
    
    plt.subplot(1, 3, 3)
    plt.plot(agent.training_stats['advantages'])
    plt.title('Advantages')
    
    plt.tight_layout()
    plt.show()
```

## Production Deployment

### Model Saving/Loading
```python
# Model saqlash
agent.save_model('production_model.pth')

# Model yuklash
agent.load_model('production_model.pth')
agent.eval()  # Inference mode
```

### Inference
```python
def predict_portfolio(self, market_data):
    with torch.no_grad():
        state = self.preprocess_state(market_data)
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        (weights, cash_prob), value = self.network(state_tensor)
        
        return {
            'portfolio_weights': weights.cpu().numpy(),
            'cash_allocation': cash_prob.cpu().numpy(),
            'confidence': torch.sigmoid(value).cpu().numpy()
        }
```

## Risk Disclaimer

⚠️ **Muhim eslatma**: Bu algoritm educational va research maqsadlar uchun yaratilgan. Real trading qilishdan oldin:

1. **Backtesting**: Tarixiy ma'lumotlar bilan keng qamrovli test qiling
2. **Paper Trading**: Real mablag'lar ishlatmasdan amalda sinab ko'ring  
3. **Risk Management**: Qat'iy risk management qoidalarini belgilang
4. **Professional Consultation**: Professional trader yoki financial advisor bilan maslahatlashing

## Lisenziya

Bu loyiha MIT License ostida tarqatiladi.

## Aloqa va Yordam

Qo'shimcha savollar va yordam uchun:
- GitHub Issues oching
- Email: support@example.com
- Documentation: [link]

---

**So'nggi yangilanish**: 2025-11-03
**Versiya**: 1.0.0