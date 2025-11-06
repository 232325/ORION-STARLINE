"""
Meta-Learning for Trading Strategies
=====================================

Bu modul meta-learning algoritmlarini o'z ichiga oladi:
- MAML (Model-Agnostic Meta-Learning) - Fast adaptation to new markets
- Reptile - Simple meta-learning algorithm
- Few-Shot Learning - Learn from limited examples
- Task Adaptation - Adapt to different market conditions
- Transfer Learning - Transfer knowledge across assets

Author: AI Trading Evolution
Date: 2025-11-04
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from collections import OrderedDict
import copy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class MetaLearningConfig:
    """Meta-learning konfiguratsiya"""
    input_dim: int = 50
    hidden_dim: int = 128
    output_dim: int = 3  # Buy, Sell, Hold
    num_inner_steps: int = 5  # Inner loop gradient steps
    inner_lr: float = 0.01  # Inner loop learning rate
    meta_lr: float = 0.001  # Meta learning rate
    num_tasks: int = 10  # Number of tasks for meta-training
    k_shot: int = 5  # K-shot learning
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


# ============================================================================
# Base Trading Model
# ============================================================================

class TradingModel(nn.Module):
    """Base trading model for meta-learning"""
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
    def forward(self, x):
        return self.network(x)
        
    def clone(self):
        """Create a deep copy of the model"""
        clone = TradingModel(
            self.network[0].in_features,
            self.network[0].out_features,
            self.network[-1].out_features
        )
        clone.load_state_dict(self.state_dict())
        return clone


# ============================================================================
# MAML (Model-Agnostic Meta-Learning)
# ============================================================================

class MAML:
    """MAML algorithm for trading strategy adaptation"""
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Meta-model
        self.model = TradingModel(
            config.input_dim,
            config.hidden_dim,
            config.output_dim
        ).to(self.device)
        
        # Meta-optimizer
        self.meta_optimizer = optim.Adam(self.model.parameters(), lr=config.meta_lr)
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        
    def inner_loop(self, model: TradingModel, support_x: torch.Tensor, 
                  support_y: torch.Tensor) -> TradingModel:
        """Inner loop: adapt model to specific task"""
        
        # Clone model for task-specific adaptation
        adapted_model = model.clone().to(self.device)
        
        # Inner loop optimizer
        inner_optimizer = optim.SGD(adapted_model.parameters(), lr=self.config.inner_lr)
        
        # Gradient steps on support set
        for _ in range(self.config.num_inner_steps):
            inner_optimizer.zero_grad()
            
            predictions = adapted_model(support_x)
            loss = self.criterion(predictions, support_y)
            
            loss.backward()
            inner_optimizer.step()
            
        return adapted_model
        
    def meta_train_step(self, tasks: List[Tuple[torch.Tensor, torch.Tensor, 
                                                torch.Tensor, torch.Tensor]]) -> Dict:
        """Meta-training step"""
        
        meta_loss = 0.0
        
        for support_x, support_y, query_x, query_y in tasks:
            support_x = support_x.to(self.device)
            support_y = support_y.to(self.device)
            query_x = query_x.to(self.device)
            query_y = query_y.to(self.device)
            
            # Inner loop adaptation
            adapted_model = self.inner_loop(self.model, support_x, support_y)
            
            # Evaluate on query set
            query_predictions = adapted_model(query_x)
            query_loss = self.criterion(query_predictions, query_y)
            
            meta_loss += query_loss
            
        # Meta-update
        meta_loss = meta_loss / len(tasks)
        
        self.meta_optimizer.zero_grad()
        meta_loss.backward()
        self.meta_optimizer.step()
        
        return {'meta_loss': meta_loss.item()}
        
    def adapt(self, support_x: np.ndarray, support_y: np.ndarray, 
             num_steps: Optional[int] = None) -> TradingModel:
        """Adapt to new task"""
        
        if num_steps is None:
            num_steps = self.config.num_inner_steps
            
        support_x = torch.FloatTensor(support_x).to(self.device)
        support_y = torch.LongTensor(support_y).to(self.device)
        
        adapted_model = self.inner_loop(self.model, support_x, support_y)
        
        return adapted_model
        
    def predict(self, x: np.ndarray, adapted_model: Optional[TradingModel] = None) -> np.ndarray:
        """Make predictions"""
        
        model = adapted_model if adapted_model is not None else self.model
        model.eval()
        
        x = torch.FloatTensor(x).to(self.device)
        
        with torch.no_grad():
            predictions = model(x)
            predictions = F.softmax(predictions, dim=-1)
            
        return predictions.cpu().numpy()


# ============================================================================
# Reptile Algorithm
# ============================================================================

class Reptile:
    """Reptile meta-learning algorithm"""
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Meta-model
        self.model = TradingModel(
            config.input_dim,
            config.hidden_dim,
            config.output_dim
        ).to(self.device)
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        
    def train_on_task(self, model: TradingModel, task_x: torch.Tensor, 
                     task_y: torch.Tensor, num_steps: int) -> TradingModel:
        """Train model on a single task"""
        
        # Clone model
        task_model = model.clone().to(self.device)
        
        # Optimizer for this task
        optimizer = optim.SGD(task_model.parameters(), lr=self.config.inner_lr)
        
        # Training steps
        for _ in range(num_steps):
            optimizer.zero_grad()
            
            predictions = task_model(task_x)
            loss = self.criterion(predictions, task_y)
            
            loss.backward()
            optimizer.step()
            
        return task_model
        
    def meta_train_step(self, tasks: List[Tuple[torch.Tensor, torch.Tensor]],
                       epsilon: float = 1.0) -> Dict:
        """Reptile meta-training step"""
        
        # Store initial parameters
        initial_params = [p.clone() for p in self.model.parameters()]
        
        task_models = []
        
        # Train on each task
        for task_x, task_y in tasks:
            task_x = task_x.to(self.device)
            task_y = task_y.to(self.device)
            
            task_model = self.train_on_task(self.model, task_x, task_y, 
                                           self.config.num_inner_steps)
            task_models.append(task_model)
            
        # Compute average task parameters
        avg_params = []
        for i, param in enumerate(self.model.parameters()):
            task_params = [list(m.parameters())[i] for m in task_models]
            avg_param = torch.stack(task_params).mean(dim=0)
            avg_params.append(avg_param)
            
        # Reptile update: move towards average of task parameters
        for param, avg_param in zip(self.model.parameters(), avg_params):
            param.data = param.data + epsilon * (avg_param - param.data)
            
        # Calculate meta-loss (for monitoring)
        meta_loss = sum([(p1 - p2).pow(2).sum() for p1, p2 in 
                        zip(initial_params, list(self.model.parameters()))])
        
        return {'meta_loss': meta_loss.item()}
        
    def adapt(self, task_x: np.ndarray, task_y: np.ndarray,
             num_steps: Optional[int] = None) -> TradingModel:
        """Adapt to new task"""
        
        if num_steps is None:
            num_steps = self.config.num_inner_steps
            
        task_x = torch.FloatTensor(task_x).to(self.device)
        task_y = torch.LongTensor(task_y).to(self.device)
        
        adapted_model = self.train_on_task(self.model, task_x, task_y, num_steps)
        
        return adapted_model


# ============================================================================
# Few-Shot Learning for Market Adaptation
# ============================================================================

class PrototypicalNetwork(nn.Module):
    """Prototypical Networks for few-shot learning"""
    
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
    def forward(self, x):
        """Encode input to embedding space"""
        return self.encoder(x)
        
    def compute_prototypes(self, support_embeddings: torch.Tensor, 
                          support_labels: torch.Tensor, num_classes: int) -> torch.Tensor:
        """Compute class prototypes"""
        
        prototypes = []
        for c in range(num_classes):
            # Get embeddings for this class
            class_mask = (support_labels == c)
            class_embeddings = support_embeddings[class_mask]
            
            # Compute prototype (mean embedding)
            prototype = class_embeddings.mean(dim=0)
            prototypes.append(prototype)
            
        return torch.stack(prototypes)
        
    def predict(self, query_embeddings: torch.Tensor, 
               prototypes: torch.Tensor) -> torch.Tensor:
        """Predict using prototypes"""
        
        # Compute distances to prototypes
        distances = torch.cdist(query_embeddings, prototypes)
        
        # Convert to probabilities (negative distance)
        logits = -distances
        probabilities = F.softmax(logits, dim=-1)
        
        return probabilities


class FewShotLearner:
    """Few-shot learning system for trading"""
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        self.model = PrototypicalNetwork(
            config.input_dim,
            config.hidden_dim
        ).to(self.device)
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=config.meta_lr)
        self.criterion = nn.CrossEntropyLoss()
        
    def train_episode(self, support_x: torch.Tensor, support_y: torch.Tensor,
                     query_x: torch.Tensor, query_y: torch.Tensor) -> Dict:
        """Train on one episode"""
        
        support_x = support_x.to(self.device)
        support_y = support_y.to(self.device)
        query_x = query_x.to(self.device)
        query_y = query_y.to(self.device)
        
        # Encode
        support_embeddings = self.model(support_x)
        query_embeddings = self.model(query_x)
        
        # Compute prototypes
        num_classes = len(torch.unique(support_y))
        prototypes = self.model.compute_prototypes(support_embeddings, support_y, num_classes)
        
        # Predict
        predictions = self.model.predict(query_embeddings, prototypes)
        
        # Loss
        loss = self.criterion(predictions, query_y)
        
        # Update
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Accuracy
        pred_labels = predictions.argmax(dim=-1)
        accuracy = (pred_labels == query_y).float().mean()
        
        return {
            'loss': loss.item(),
            'accuracy': accuracy.item()
        }
        
    def adapt_and_predict(self, support_x: np.ndarray, support_y: np.ndarray,
                         query_x: np.ndarray) -> np.ndarray:
        """Adapt to new task and predict"""
        
        self.model.eval()
        
        support_x = torch.FloatTensor(support_x).to(self.device)
        support_y = torch.LongTensor(support_y).to(self.device)
        query_x = torch.FloatTensor(query_x).to(self.device)
        
        with torch.no_grad():
            # Encode
            support_embeddings = self.model(support_x)
            query_embeddings = self.model(query_x)
            
            # Compute prototypes
            num_classes = len(torch.unique(support_y))
            prototypes = self.model.compute_prototypes(support_embeddings, support_y, num_classes)
            
            # Predict
            predictions = self.model.predict(query_embeddings, prototypes)
            
        return predictions.cpu().numpy()


# ============================================================================
# Transfer Learning
# ============================================================================

class TransferLearner:
    """Transfer learning across different assets/markets"""
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Source domain model
        self.source_model = TradingModel(
            config.input_dim,
            config.hidden_dim,
            config.output_dim
        ).to(self.device)
        
        self.optimizer = optim.Adam(self.source_model.parameters(), lr=config.meta_lr)
        self.criterion = nn.CrossEntropyLoss()
        
    def train_source(self, source_data: List[Tuple[torch.Tensor, torch.Tensor]], 
                    epochs: int = 100) -> Dict:
        """Train on source domain"""
        
        logger.info(f"Training on source domain for {epochs} epochs")
        
        history = {'losses': [], 'accuracies': []}
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            epoch_acc = 0.0
            
            for x, y in source_data:
                x = x.to(self.device)
                y = y.to(self.device)
                
                self.optimizer.zero_grad()
                
                predictions = self.source_model(x)
                loss = self.criterion(predictions, y)
                
                loss.backward()
                self.optimizer.step()
                
                epoch_loss += loss.item()
                
                pred_labels = predictions.argmax(dim=-1)
                epoch_acc += (pred_labels == y).float().mean().item()
                
            avg_loss = epoch_loss / len(source_data)
            avg_acc = epoch_acc / len(source_data)
            
            history['losses'].append(avg_loss)
            history['accuracies'].append(avg_acc)
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}, Acc: {avg_acc:.4f}")
                
        return history
        
    def transfer_to_target(self, target_data: List[Tuple[torch.Tensor, torch.Tensor]],
                          freeze_features: bool = True,
                          fine_tune_epochs: int = 20) -> TradingModel:
        """Transfer to target domain"""
        
        # Create target model with source weights
        target_model = TradingModel(
            self.config.input_dim,
            self.config.hidden_dim,
            self.config.output_dim
        ).to(self.device)
        
        target_model.load_state_dict(self.source_model.state_dict())
        
        if freeze_features:
            # Freeze all layers except the last one
            for param in target_model.network[:-1].parameters():
                param.requires_grad = False
                
        # Fine-tune on target domain
        logger.info(f"Fine-tuning on target domain for {fine_tune_epochs} epochs")
        
        optimizer = optim.Adam(
            filter(lambda p: p.requires_grad, target_model.parameters()),
            lr=self.config.inner_lr
        )
        
        for epoch in range(fine_tune_epochs):
            epoch_loss = 0.0
            
            for x, y in target_data:
                x = x.to(self.device)
                y = y.to(self.device)
                
                optimizer.zero_grad()
                
                predictions = target_model(x)
                loss = self.criterion(predictions, y)
                
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                
            if (epoch + 1) % 5 == 0:
                logger.info(f"Fine-tune Epoch {epoch+1}/{fine_tune_epochs} - Loss: {epoch_loss/len(target_data):.4f}")
                
        return target_model
        
    def domain_adaptation(self, source_data: List[Tuple[torch.Tensor, torch.Tensor]],
                         target_data: List[Tuple[torch.Tensor, torch.Tensor]],
                         adaptation_epochs: int = 50) -> TradingModel:
        """Domain adaptation using adversarial training"""
        
        # Create domain discriminator
        discriminator = nn.Sequential(
            nn.Linear(self.config.hidden_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        ).to(self.device)
        
        # Optimizers
        model_optimizer = optim.Adam(self.source_model.parameters(), lr=self.config.meta_lr)
        disc_optimizer = optim.Adam(discriminator.parameters(), lr=self.config.meta_lr)
        
        logger.info(f"Domain adaptation for {adaptation_epochs} epochs")
        
        for epoch in range(adaptation_epochs):
            # Sample batches
            source_x, source_y = source_data[epoch % len(source_data)]
            target_x, target_y = target_data[epoch % len(target_data)]
            
            source_x = source_x.to(self.device)
            target_x = target_x.to(self.device)
            source_y = source_y.to(self.device)
            
            # Extract features
            source_features = self.source_model.network[:-1](source_x)
            target_features = self.source_model.network[:-1](target_x)
            
            # Train discriminator
            disc_optimizer.zero_grad()
            
            source_domain = discriminator(source_features.detach())
            target_domain = discriminator(target_features.detach())
            
            disc_loss = (
                F.binary_cross_entropy(source_domain, torch.ones_like(source_domain)) +
                F.binary_cross_entropy(target_domain, torch.zeros_like(target_domain))
            )
            
            disc_loss.backward()
            disc_optimizer.step()
            
            # Train model (task loss + domain confusion)
            model_optimizer.zero_grad()
            
            # Task loss
            source_predictions = self.source_model(source_x)
            task_loss = self.criterion(source_predictions, source_y)
            
            # Domain confusion loss
            target_features = self.source_model.network[:-1](target_x)
            target_domain = discriminator(target_features)
            domain_loss = F.binary_cross_entropy(target_domain, torch.ones_like(target_domain))
            
            total_loss = task_loss + 0.1 * domain_loss
            
            total_loss.backward()
            model_optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{adaptation_epochs} - "
                          f"Task Loss: {task_loss.item():.4f}, "
                          f"Domain Loss: {domain_loss.item():.4f}")
                
        return self.source_model


# ============================================================================
# Meta-Learning Task Generator
# ============================================================================

class TaskGenerator:
    """Generate tasks for meta-learning"""
    
    @staticmethod
    def generate_market_tasks(historical_data: Dict[str, np.ndarray],
                             k_shot: int = 5,
                             query_size: int = 20) -> List:
        """Generate tasks from different market periods"""
        
        tasks = []
        
        for asset, data in historical_data.items():
            # Split data into episodes
            episode_length = k_shot + query_size
            num_episodes = len(data) // episode_length
            
            for ep in range(num_episodes):
                start_idx = ep * episode_length
                end_idx = start_idx + episode_length
                
                episode_data = data[start_idx:end_idx]
                
                # Support set (first k_shot samples)
                support_x = episode_data[:k_shot, :-1]  # Features
                support_y = episode_data[:k_shot, -1].astype(int)  # Labels
                
                # Query set (remaining samples)
                query_x = episode_data[k_shot:, :-1]
                query_y = episode_data[k_shot:, -1].astype(int)
                
                tasks.append((
                    torch.FloatTensor(support_x),
                    torch.LongTensor(support_y),
                    torch.FloatTensor(query_x),
                    torch.LongTensor(query_y)
                ))
                
        return tasks


if __name__ == "__main__":
    logger.info("Meta-Learning moduli yuklandi!")
    logger.info("MAML, Reptile, Few-Shot Learning, Transfer Learning tayyor")
    logger.info("Yangi bozorlarga tez moslashuv imkoniyati")
