"""
Predictive Market Movement Models
==================================

Bu modul bozor harakatini bashorat qilish uchun zamonaviy deep learning modellarini o'z ichiga oladi:
- LSTM (Long Short-Term Memory) - Time series prediction
- GRU (Gated Recurrent Unit) - Lighter alternative to LSTM
- Transformer - Attention-based sequence modeling
- Temporal Fusion Transformer - Multi-horizon forecasting
- Hybrid Models - Combining multiple architectures

Author: AI Trading Evolution
Date: 2025-11-04
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from sklearn.preprocessing import StandardScaler
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class ModelConfig:
    """Model konfiguratsiya"""
    input_dim: int = 10  # Feature count
    hidden_dim: int = 128
    num_layers: int = 3
    output_dim: int = 1  # Price prediction
    dropout: float = 0.2
    learning_rate: float = 1e-3
    batch_size: int = 64
    sequence_length: int = 60  # 60 timesteps
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


@dataclass
class PredictionResult:
    """Bashorat natijasi"""
    predicted_price: float
    confidence: float
    prediction_horizon: int  # steps ahead
    timestamp: datetime
    model_type: str
    
    def to_dict(self) -> Dict:
        return {
            'predicted_price': self.predicted_price,
            'confidence': self.confidence,
            'prediction_horizon': self.prediction_horizon,
            'timestamp': self.timestamp.isoformat(),
            'model_type': self.model_type
        }


# ============================================================================
# Dataset
# ============================================================================

class TimeSeriesDataset(Dataset):
    """Time series dataset for training"""
    
    def __init__(self, data: np.ndarray, sequence_length: int = 60, 
                 target_horizon: int = 1):
        """
        Args:
            data: Shape (timesteps, features)
            sequence_length: Input sequence length
            target_horizon: Prediction horizon (steps ahead)
        """
        self.data = torch.FloatTensor(data)
        self.sequence_length = sequence_length
        self.target_horizon = target_horizon
        
    def __len__(self):
        return len(self.data) - self.sequence_length - self.target_horizon + 1
        
    def __getitem__(self, idx):
        # Input: sequence_length timesteps
        x = self.data[idx:idx + self.sequence_length]
        
        # Target: price at target_horizon ahead
        y = self.data[idx + self.sequence_length + self.target_horizon - 1, 0]  # Assuming price is first feature
        
        return x, y


# ============================================================================
# LSTM Model
# ============================================================================

class LSTMPredictor(nn.Module):
    """LSTM-based price predictor"""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        
        self.config = config
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim,
            num_layers=config.num_layers,
            dropout=config.dropout if config.num_layers > 1 else 0,
            batch_first=True
        )
        
        # Fully connected layers
        self.fc = nn.Sequential(
            nn.Linear(config.hidden_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim // 2, config.output_dim)
        )
        
    def forward(self, x):
        """
        Args:
            x: Shape (batch, sequence_length, input_dim)
        Returns:
            predictions: Shape (batch, output_dim)
        """
        # LSTM forward
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Use last hidden state
        last_hidden = lstm_out[:, -1, :]
        
        # FC layers
        predictions = self.fc(last_hidden)
        
        return predictions
        
    def predict_sequence(self, x, steps: int = 10):
        """Multi-step prediction"""
        self.eval()
        predictions = []
        
        current_seq = x.clone()
        
        with torch.no_grad():
            for _ in range(steps):
                # Predict next step
                pred = self.forward(current_seq)
                predictions.append(pred)
                
                # Update sequence (shift left and append prediction)
                new_step = current_seq[:, -1, :].clone()
                new_step[:, 0] = pred.squeeze()  # Update price feature
                
                current_seq = torch.cat([current_seq[:, 1:, :], new_step.unsqueeze(1)], dim=1)
                
        return torch.cat(predictions, dim=0)


# ============================================================================
# GRU Model
# ============================================================================

class GRUPredictor(nn.Module):
    """GRU-based price predictor (lighter than LSTM)"""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        
        self.config = config
        
        # GRU layers
        self.gru = nn.GRU(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim,
            num_layers=config.num_layers,
            dropout=config.dropout if config.num_layers > 1 else 0,
            batch_first=True
        )
        
        # Attention layer
        self.attention = nn.MultiheadAttention(
            embed_dim=config.hidden_dim,
            num_heads=4,
            dropout=config.dropout,
            batch_first=True
        )
        
        # FC layers
        self.fc = nn.Sequential(
            nn.Linear(config.hidden_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim // 2, config.output_dim)
        )
        
    def forward(self, x):
        # GRU forward
        gru_out, hidden = self.gru(x)
        
        # Self-attention
        attn_out, _ = self.attention(gru_out, gru_out, gru_out)
        
        # Use last output
        last_out = attn_out[:, -1, :]
        
        # FC layers
        predictions = self.fc(last_out)
        
        return predictions


# ============================================================================
# Transformer Model
# ============================================================================

class PositionalEncoding(nn.Module):
    """Positional encoding for Transformer"""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        """
        Args:
            x: Shape (batch, seq_len, d_model)
        """
        return x + self.pe[:, :x.size(1), :]


class TransformerPredictor(nn.Module):
    """Transformer-based price predictor"""
    
    def __init__(self, config: ModelConfig, num_heads: int = 8, num_encoder_layers: int = 6):
        super().__init__()
        
        self.config = config
        
        # Input projection
        self.input_projection = nn.Linear(config.input_dim, config.hidden_dim)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(config.hidden_dim)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.hidden_dim,
            nhead=num_heads,
            dim_feedforward=config.hidden_dim * 4,
            dropout=config.dropout,
            batch_first=True
        )
        
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_encoder_layers
        )
        
        # Output projection
        self.output_projection = nn.Sequential(
            nn.Linear(config.hidden_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim // 2, config.output_dim)
        )
        
    def forward(self, x):
        """
        Args:
            x: Shape (batch, sequence_length, input_dim)
        """
        # Input projection
        x = self.input_projection(x)
        
        # Positional encoding
        x = self.pos_encoder(x)
        
        # Transformer encoding
        transformer_out = self.transformer_encoder(x)
        
        # Use last output for prediction
        last_out = transformer_out[:, -1, :]
        
        # Output projection
        predictions = self.output_projection(last_out)
        
        return predictions


# ============================================================================
# Temporal Fusion Transformer
# ============================================================================

class TemporalFusionTransformer(nn.Module):
    """Advanced multi-horizon forecasting with TFT"""
    
    def __init__(self, config: ModelConfig, num_heads: int = 4):
        super().__init__()
        
        self.config = config
        
        # Variable selection network
        self.variable_selection = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dim),
            nn.ReLU(),
            nn.Linear(config.hidden_dim, config.input_dim),
            nn.Softmax(dim=-1)
        )
        
        # LSTM encoder for historical data
        self.lstm_encoder = nn.LSTM(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim,
            num_layers=2,
            batch_first=True
        )
        
        # Temporal self-attention
        self.temporal_attention = nn.MultiheadAttention(
            embed_dim=config.hidden_dim,
            num_heads=num_heads,
            dropout=config.dropout,
            batch_first=True
        )
        
        # Static enrichment
        self.static_enrichment = nn.Sequential(
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.ReLU()
        )
        
        # Gating mechanism
        self.gating = nn.Sequential(
            nn.Linear(config.hidden_dim * 2, config.hidden_dim),
            nn.Sigmoid()
        )
        
        # Output layer with quantile forecasting
        self.quantile_output = nn.ModuleDict({
            'q10': nn.Linear(config.hidden_dim, config.output_dim),
            'q50': nn.Linear(config.hidden_dim, config.output_dim),
            'q90': nn.Linear(config.hidden_dim, config.output_dim)
        })
        
    def forward(self, x):
        batch_size = x.size(0)
        
        # Variable selection
        weights = self.variable_selection(x)
        x_selected = x * weights
        
        # LSTM encoding
        lstm_out, (hidden, cell) = self.lstm_encoder(x_selected)
        
        # Temporal attention
        attn_out, attn_weights = self.temporal_attention(lstm_out, lstm_out, lstm_out)
        
        # Static context (use last hidden state)
        static_context = hidden[-1]
        static_enriched = self.static_enrichment(static_context)
        
        # Combine with gating
        combined = torch.cat([attn_out[:, -1, :], static_enriched], dim=-1)
        gate = self.gating(combined)
        
        gated_output = gate * attn_out[:, -1, :]
        
        # Multi-quantile predictions
        predictions = {
            'q10': self.quantile_output['q10'](gated_output),
            'q50': self.quantile_output['q50'](gated_output),
            'q90': self.quantile_output['q90'](gated_output)
        }
        
        return predictions, attn_weights


# ============================================================================
# Hybrid Model (LSTM + Transformer)
# ============================================================================

class HybridPredictor(nn.Module):
    """Hybrid model combining LSTM and Transformer"""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        
        self.config = config
        
        # LSTM branch
        self.lstm = nn.LSTM(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim,
            num_layers=2,
            batch_first=True
        )
        
        # Transformer branch
        self.input_projection = nn.Linear(config.input_dim, config.hidden_dim)
        self.pos_encoder = PositionalEncoding(config.hidden_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.hidden_dim,
            nhead=4,
            dim_feedforward=config.hidden_dim * 2,
            dropout=config.dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(config.hidden_dim * 2, config.hidden_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout)
        )
        
        # Output layer
        self.output = nn.Linear(config.hidden_dim, config.output_dim)
        
    def forward(self, x):
        # LSTM branch
        lstm_out, _ = self.lstm(x)
        lstm_features = lstm_out[:, -1, :]
        
        # Transformer branch
        x_proj = self.input_projection(x)
        x_pos = self.pos_encoder(x_proj)
        transformer_out = self.transformer(x_pos)
        transformer_features = transformer_out[:, -1, :]
        
        # Fuse features
        combined = torch.cat([lstm_features, transformer_features], dim=-1)
        fused = self.fusion(combined)
        
        # Final prediction
        predictions = self.output(fused)
        
        return predictions


# ============================================================================
# Model Trainer
# ============================================================================

class PredictiveModelTrainer:
    """Training pipeline for predictive models"""
    
    def __init__(self, model: nn.Module, config: ModelConfig):
        self.model = model
        self.config = config
        self.device = torch.device(config.device)
        self.model.to(self.device)
        
        # Optimizer
        self.optimizer = optim.AdamW(model.parameters(), lr=config.learning_rate)
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=5
        )
        
        # Loss function
        self.criterion = nn.MSELoss()
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        self.model.train()
        epoch_loss = 0.0
        
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(self.device)
            batch_y = batch_y.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            
            if isinstance(self.model, TemporalFusionTransformer):
                predictions, _ = self.model(batch_x)
                loss = self.criterion(predictions['q50'].squeeze(), batch_y)
            else:
                predictions = self.model(batch_x)
                loss = self.criterion(predictions.squeeze(), batch_y)
            
            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            epoch_loss += loss.item()
            
        return epoch_loss / len(train_loader)
        
    def validate(self, val_loader: DataLoader) -> float:
        """Validation"""
        self.model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                if isinstance(self.model, TemporalFusionTransformer):
                    predictions, _ = self.model(batch_x)
                    loss = self.criterion(predictions['q50'].squeeze(), batch_y)
                else:
                    predictions = self.model(batch_x)
                    loss = self.criterion(predictions.squeeze(), batch_y)
                
                val_loss += loss.item()
                
        return val_loss / len(val_loader)
        
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
             epochs: int = 100, early_stopping_patience: int = 10):
        """Complete training loop"""
        best_val_loss = float('inf')
        patience_counter = 0
        
        logger.info(f"Training {self.model.__class__.__name__} for {epochs} epochs")
        
        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                torch.save(self.model.state_dict(), f'best_{self.model.__class__.__name__}.pth')
            else:
                patience_counter += 1
                
            if patience_counter >= early_stopping_patience:
                logger.info(f"Early stopping at epoch {epoch}")
                break
                
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
                
        logger.info(f"Training complete. Best validation loss: {best_val_loss:.6f}")
        
        # Load best model
        self.model.load_state_dict(torch.load(f'best_{self.model.__class__.__name__}.pth'))
        
        return {
            'best_val_loss': best_val_loss,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses
        }


# ============================================================================
# Prediction System
# ============================================================================

class PredictionSystem:
    """Complete prediction system with multiple models"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Initialize models
        self.models = {
            'LSTM': LSTMPredictor(config).to(self.device),
            'GRU': GRUPredictor(config).to(self.device),
            'Transformer': TransformerPredictor(config).to(self.device),
            'TFT': TemporalFusionTransformer(config).to(self.device),
            'Hybrid': HybridPredictor(config).to(self.device)
        }
        
        # Scaler for normalization
        self.scaler = StandardScaler()
        
    def prepare_data(self, df: pd.DataFrame, 
                    feature_columns: List[str],
                    train_ratio: float = 0.8) -> Tuple[DataLoader, DataLoader]:
        """Prepare data for training"""
        
        # Extract features
        data = df[feature_columns].values
        
        # Normalize
        data_normalized = self.scaler.fit_transform(data)
        
        # Split train/val
        train_size = int(len(data_normalized) * train_ratio)
        train_data = data_normalized[:train_size]
        val_data = data_normalized[train_size:]
        
        # Create datasets
        train_dataset = TimeSeriesDataset(train_data, self.config.sequence_length)
        val_dataset = TimeSeriesDataset(val_data, self.config.sequence_length)
        
        # Create dataloaders
        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size, shuffle=False)
        
        return train_loader, val_loader
        
    def train_all_models(self, train_loader: DataLoader, val_loader: DataLoader,
                        epochs: int = 100):
        """Train all models"""
        results = {}
        
        for model_name, model in self.models.items():
            logger.info(f"\n{'='*50}")
            logger.info(f"Training {model_name}")
            logger.info(f"{'='*50}")
            
            trainer = PredictiveModelTrainer(model, self.config)
            result = trainer.train(train_loader, val_loader, epochs=epochs)
            results[model_name] = result
            
        return results
        
    def predict(self, recent_data: np.ndarray, model_name: str = 'Hybrid',
               steps: int = 1) -> PredictionResult:
        """Make prediction with specified model"""
        
        # Normalize input
        recent_normalized = self.scaler.transform(recent_data)
        
        # Prepare input tensor
        x = torch.FloatTensor(recent_normalized[-self.config.sequence_length:]).unsqueeze(0).to(self.device)
        
        # Get model
        model = self.models[model_name]
        model.eval()
        
        with torch.no_grad():
            if isinstance(model, TemporalFusionTransformer):
                predictions, attention_weights = model(x)
                pred_value = predictions['q50'].item()
                
                # Confidence based on quantile range
                q_range = predictions['q90'].item() - predictions['q10'].item()
                confidence = 1.0 / (1.0 + q_range)
            else:
                predictions = model(x)
                pred_value = predictions.item()
                confidence = 0.8  # Default confidence
                
        # Denormalize prediction
        dummy = np.zeros((1, recent_data.shape[1]))
        dummy[0, 0] = pred_value
        pred_denormalized = self.scaler.inverse_transform(dummy)[0, 0]
        
        return PredictionResult(
            predicted_price=pred_denormalized,
            confidence=confidence,
            prediction_horizon=steps,
            timestamp=datetime.now(),
            model_type=model_name
        )
        
    def ensemble_predict(self, recent_data: np.ndarray, 
                        model_weights: Optional[Dict[str, float]] = None) -> PredictionResult:
        """Ensemble prediction from multiple models"""
        
        if model_weights is None:
            # Equal weights
            model_weights = {name: 1.0 / len(self.models) for name in self.models.keys()}
            
        predictions = []
        confidences = []
        
        for model_name, weight in model_weights.items():
            pred = self.predict(recent_data, model_name)
            predictions.append(pred.predicted_price * weight)
            confidences.append(pred.confidence * weight)
            
        ensemble_price = sum(predictions)
        ensemble_confidence = sum(confidences)
        
        return PredictionResult(
            predicted_price=ensemble_price,
            confidence=ensemble_confidence,
            prediction_horizon=1,
            timestamp=datetime.now(),
            model_type='Ensemble'
        )


# ============================================================================
# Feature Engineering
# ============================================================================

class FeatureEngineer:
    """Feature engineering for time series prediction"""
    
    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators as features"""
        df = df.copy()
        
        # Price-based features
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Moving averages
        for period in [7, 14, 30]:
            df[f'sma_{period}'] = df['close'].rolling(period).mean()
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
            
        # Volatility
        df['volatility_7d'] = df['returns'].rolling(7).std()
        df['volatility_30d'] = df['returns'].rolling(30).std()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + 2 * bb_std
        df['bb_lower'] = df['bb_middle'] - 2 * bb_std
        
        # Volume features
        if 'volume' in df.columns:
            df['volume_sma_7'] = df['volume'].rolling(7).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma_7']
            
        return df.dropna()


if __name__ == "__main__":
    logger.info("Predictive Models moduli yuklandi!")
    logger.info("Mavjud modellar: LSTM, GRU, Transformer, TFT, Hybrid")
    logger.info("Multi-horizon forecasting va ensemble predictions qo'llab-quvvatlanadi")
