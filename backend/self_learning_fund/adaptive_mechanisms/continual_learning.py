"""
Continual Learning Frameworks for Self-Learning Trading Fund

Ushbu modul uzluksiz o'rganish mexanizmlarini ta'minlaydi,
ya'ni eski bilimlarni yo'qotmasdan yangi ma'lumotlarni o'rganish.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score
import logging
import json
import pickle
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import asyncio
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')


class ContinualLearningStrategy(ABC):
    """Uzluksiz o'rganish strategiyalari uchun abstrakt baza sinfi"""
    
    @abstractmethod
    def before_update(self, model: nn.Module, old_data: Any) -> None:
        """Model yangilanishidan oldin chaqiriladi"""
        pass
    
    @abstractmethod
    def after_update(self, model: nn.Module, new_data: Any) -> None:
        """Model yangilanishidan keyin chaqiriladi"""
        pass
    
    @abstractmethod
    def get_regularization_term(self) -> torch.Tensor:
        """Regulyarizatsiya atrofini qaytaradi"""
        pass


class EWCStrategy(ContinualLearningStrategy):
    """Elastic Weight Consolidation strategiyasi"""
    
    def __init__(self, model: nn.Module, lambda_ewc: float = 1000.0):
        self.model = model
        self.lambda_ewc = lambda_ewc
        self.fisher_information = {}
        self.optimal_params = {}
        self.logger = logging.getLogger(__name__)
        
    def before_update(self, model: nn.Module, old_data: Any) -> None:
        """Fisher ma'lumotlarini hisoblaydi"""
        model.eval()
        
        # Optimal parametrlarni saqlaydi
        for name, param in model.named_parameters():
            if param.requires_grad:
                self.optimal_params[name] = param.data.clone()
        
        # Fisher ma'lumotlarini hisoblash
        self.fisher_information = {}
        
        for name, param in model.named_parameters():
            if param.requires_grad:
                fisher = torch.zeros_like(param)
                
                # Agar ma'lumot mavjud bo'lsa Fisher ni hisoblaydi
                if old_data is not None:
                    for data, target in old_data:
                        model.zero_grad()
                        output = model(data)
                        loss = nn.functional.cross_entropy(output, target)
                        loss.backward()
                        
                        # Fisher ma'lumotini hisoblaydi
                        fisher += param.grad.data ** 2
                
                fisher /= len(old_data) if old_data else 1
                self.fisher_information[name] = fisher
                
        self.logger.info("EWC: Fisher ma'lumotlari hisoblandi")
    
    def after_update(self, model: nn.Module, new_data: Any) -> None:
        """Yangilanish tugagandan so'ng chaqiriladi"""
        self.logger.info("EWC: Model yangilandi")
    
    def get_regularization_term(self) -> torch.Tensor:
        """EWC regulyarizatsiya atrofini hisoblaydi"""
        regularization_loss = 0.0
        
        for name, param in self.model.named_parameters():
            if param.requires_grad and name in self.fisher_information:
                fisher = self.fisher_information[name]
                optimal_param = self.optimal_params[name]
                regularization_loss += (fisher * (param - optimal_param) ** 2).sum()
                
        return self.lambda_ewc * regularization_loss


class LwFStrategy(ContinualLearningStrategy):
    """Learning without Forgetting strategiyasi"""
    
    def __init__(self, model: nn.Module, temperature: float = 2.0, alpha: float = 0.5):
        self.model = model
        self.temperature = temperature
        self.alpha = alpha
        self.old_model = None
        self.logger = logging.getLogger(__name__)
        
    def before_update(self, model: nn.Module, old_data: Any) -> None:
        """Eski model nusxasini saqlaydi"""
        self.old_model = type(model)(**model.init_kwargs if hasattr(model, 'init_kwargs') else {})
        self.old_model.load_state_dict(model.state_dict())
        self.old_model.eval()
        self.logger.info("LwF: Eski model saqlandi")
    
    def after_update(self, model: nn.Module, new_data: Any) -> None:
        """Yangilanish tugagandan so'ng chaqiriladi"""
        self.logger.info("LwF: Model yangilandi")
    
    def get_regularization_term(self) -> torch.Tensor:
        """LwF regulyarizatsiya atrofini hisoblayti"""
        if self.old_model is None:
            return torch.tensor(0.0)
            
        # Eski model va yangi model o'rtasidagi farqni hisoblaydi
        knowledge_distillation_loss = 0.0
        
        for old_param, new_param in zip(self.old_model.parameters(), self.model.parameters()):
            # Soft target distillyatsiya
            old_output = F.softmax(old_param / self.temperature, dim=1)
            new_output = F.softmax(new_param / self.temperature, dim=1)
            
            kl_div = F.kl_div(new_output.log(), old_output, reduction='batchmean')
            knowledge_distillation_loss += kl_div
            
        return self.alpha * knowledge_distillation_loss


class GEMStrategy(ContinualLearningStrategy):
    """Gradient Episodic Memory strategiyasi"""
    
    def __init__(self, model: nn.Module, memory_strength: float = 0.5):
        self.model = model
        self.memory_strength = memory_strength
        self.memory_data = []
        self.memory_params = []
        self.logger = logging.getLogger(__name__)
        
    def before_update(self, model: nn.Module, old_data: Any) -> None:
        """Episodic xotirani yangilaydi"""
        if old_data and len(self.memory_data) > 0:
            # Eng muhim namunalarni xotiraga qo'shadi
            self.memory_data.append(old_data)
            
            # Xotiradagi ma'lumotlar sonini cheklaydi
            max_memory_size = 1000
            if len(self.memory_data) > max_memory_size:
                self.memory_data = self.memory_data[-max_memory_size:]
                
        self.logger.info("GEM: Episodic xotira yangilandi")
    
    def after_update(self, model: nn.Module, new_data: Any) -> None:
        """Yangilanish tugagandan so'ng chaqiriladi"""
        # Gradientsni cheklab qo'yish
        self._project_gradient()
        self.logger.info("GEM: Gradient proyeksiya bajarildi")
    
    def _project_gradient(self) -> None:
        """Gradientlarni xotiradagi ma'lumotlar bilan mos ravishda cheklab qo'yadi"""
        if len(self.memory_params) == 0:
            return
            
        # Memory parametrlarini saqlab qolish
        for name, param in self.model.named_parameters():
            if param.requires_grad and param.grad is not None:
                # Boshqa vazifalar uchun zararli gradientlarni cheklab qo'yadi
                param.grad.data = torch.clamp(param.grad.data, min=-self.memory_strength)
    
    def get_regularization_term(self) -> torch.Tensor:
        """GEM regulyarizatsiya atrofini qaytaradi"""
        return torch.tensor(0.0)  # GEM asosan gradient cheklash ishlatadi


class ProgressiveNeuralNetwork(nn.Module):
    """Progressive Neural Network - yangi vazifalar uchun yangi ustunlar qo'shadi"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int]):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.task_columns = nn.ModuleList()
        self.task_adapters = nn.ModuleList()
        self.num_tasks = 0
        
        # Birinchi vazifa uchun ustun yaratish
        self._add_task_column()
        
    def _add_task_column(self) -> None:
        """Yangi vazifa uchun ustun qo'shadi"""
        layers = []
        
        # Input layer
        layers.append(nn.Linear(self.input_dim, self.hidden_dims[0]))
        layers.append(nn.ReLU())
        
        # Hidden layers
        for i in range(1, len(self.hidden_dims)):
            layers.append(nn.Linear(self.hidden_dims[i-1], self.hidden_dims[i]))
            layers.append(nn.ReLU())
        
        # Output layer (so'ngra konfiguratsiya qilinadi)
        layers.append(nn.Linear(self.hidden_dims[-1], 1))
        
        # Yangi ustun yaratish
        self.task_columns.append(nn.Sequential(*layers))
        
        # Adapter yaratish
        if self.num_tasks > 0:
            adapter_layers = []
            for i in range(len(self.hidden_dims)):
                adapter_layers.append(nn.Linear(self.hidden_dims[i], self.hidden_dims[i]))
            self.task_adapters.append(nn.Sequential(*adapter_layers))
        
        self.num_tasks += 1
        
    def forward(self, x: torch.Tensor, task_id: int) -> torch.Tensor:
        """Forward pass"""
        if task_id >= len(self.task_columns):
            # Yangi vazifa uchun ustun yaratish
            for _ in range(task_id + 1 - len(self.task_columns)):
                self._add_task_column()
        
        # Hamma ustunlar orqali o'tkazish
        outputs = []
        for i in range(self.num_tasks):
            if i < len(self.task_columns):
                output = self.task_columns[i](x)
                outputs.append(output)
        
        # Adapterlar bilan kombinatsiya qilish
        if len(outputs) > 1 and len(self.task_adapters) == len(outputs):
            combined_output = torch.stack(outputs, dim=-1)
            adapter_input = torch.mean(combined_output, dim=-1)
            adapter_output = self.task_adapters[task_id](adapter_input)
            return adapter_output
        elif outputs:
            return outputs[task_id]
        else:
            return self.task_columns[0](x)


class ContinualLearningFramework:
    """Asosiy uzluksiz o'rganish framework"""
    
    def __init__(self, model: nn.Module, strategy: ContinualLearningStrategy):
        self.model = model
        self.strategy = strategy
        self.logger = logging.getLogger(__name__)
        self.training_history = []
        self.task_performance = {}
        self.current_task = 0
        
        # Optimizer va loss function
        self.optimizer = optim.Adam(model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=10
        )
        
    def train_on_task(self, train_loader: DataLoader, val_loader: DataLoader, 
                     epochs: int = 50, task_name: str = None) -> Dict[str, float]:
        """Muayyan vazifa uchun train qilish"""
        
        if task_name is None:
            task_name = f"task_{self.current_task}"
            
        self.logger.info(f"{task_name} vazifasi uchun train boshlanmoqda...")
        
        # Strategiyani tayyorlash
        self.strategy.before_update(self.model, None)
        
        best_val_loss = float('inf')
        patience_counter = 0
        early_stopping_patience = 15
        
        for epoch in range(epochs):
            # Train qilish
            train_loss = self._train_epoch(train_loader, epoch)
            
            # Validation
            val_loss = self._validate_epoch(val_loader)
            
            # Scheduler update
            self.scheduler.step(val_loss)
            
            # History qo'shish
            self.training_history.append({
                'epoch': epoch,
                'task': task_name,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'learning_rate': self.optimizer.param_groups[0]['lr']
            })
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1
                
            if patience_counter >= early_stopping_patience:
                self.logger.info(f"Early stopping: {epoch} epoch da to'xtadi")
                break
                
            if epoch % 10 == 0:
                self.logger.info(f"Epoch {epoch}: Train Loss = {train_loss:.4f}, Val Loss = {val_loss:.4f}")
        
        # Vazifa performance saqlash
        self.task_performance[task_name] = {
            'best_val_loss': best_val_loss,
            'final_train_loss': train_loss,
            'epochs_trained': epoch + 1,
            'final_learning_rate': self.optimizer.param_groups[0]['lr']
        }
        
        self.logger.info(f"{task_name} vazifasi tugallandi. Best Val Loss: {best_val_loss:.4f}")
        
        self.current_task += 1
        return self.task_performance[task_name]
    
    def _train_epoch(self, train_loader: DataLoader, epoch: int) -> float:
        """Bir epoch train qilish"""
        self.model.train()
        total_loss = 0.0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            self.optimizer.zero_grad()
            
            # Forward pass
            output = self.model(data)
            loss = self.criterion(output, target)
            
            # Regularization qo'shish
            regularization = self.strategy.get_regularization_term()
            if regularization is not None:
                total_loss_with_reg = loss + regularization
            else:
                total_loss_with_reg = loss
            
            # Backward pass
            total_loss_with_reg.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            
        return total_loss / len(train_loader)
    
    def _validate_epoch(self, val_loader: DataLoader) -> float:
        """Validation"""
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for data, target in val_loader:
                output = self.model(data)
                loss = self.criterion(output, target)
                total_loss += loss.item()
                
        return total_loss / len(val_loader)
    
    def evaluate_all_tasks(self, task_loaders: Dict[str, DataLoader]) -> Dict[str, float]:
        """Barcha vazifalar uchun evaluation"""
        results = {}
        
        for task_name, loader in task_loaders.items():
            task_loss = self._validate_epoch(loader)
            results[task_name] = task_loss
            
        return results
    
    def save_checkpoint(self, filepath: str) -> None:
        """Model checkpoint saqlash"""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'training_history': self.training_history,
            'task_performance': self.task_performance,
            'current_task': self.current_task,
            'strategy_state': getattr(self.strategy, 'fisher_information', {})
        }
        
        torch.save(checkpoint, filepath)
        self.logger.info(f"Checkpoint saqlandi: {filepath}")
    
    def load_checkpoint(self, filepath: str) -> None:
        """Model checkpoint yuklash"""
        checkpoint = torch.load(filepath)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.training_history = checkpoint.get('training_history', [])
        self.task_performance = checkpoint.get('task_performance', {})
        self.current_task = checkpoint.get('current_task', 0)
        
        # Strategiya state yuklash
        strategy_state = checkpoint.get('strategy_state', {})
        if hasattr(self.strategy, 'fisher_information'):
            self.strategy.fisher_information = strategy_state
            
        self.logger.info(f"Checkpoint yuklandi: {filepath}")


class MemoryReplayBuffer:
    """Ma'lumotlarni saqlab qolish va replay qilish uchun buffer"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer = []
        self.current_size = 0
        
    def add(self, data: Tuple[torch.Tensor, torch.Tensor]) -> None:
        """Ma'lumot qo'shish"""
        self.buffer.append(data)
        self.current_size += 1
        
        # Max size dan oshib ketganda eng eski ma'lumotni o'chirish
        if self.current_size > self.max_size:
            self.buffer.pop(0)
            self.current_size -= 1
    
    def sample(self, batch_size: int) -> List[Tuple[torch.Tensor, torch.Tensor]]:
        """Tasodifiy namunalar olish"""
        if len(self.buffer) == 0:
            return []
            
        indices = np.random.choice(len(self.buffer), 
                                 min(batch_size, len(self.buffer)), 
                                 replace=False)
        return [self.buffer[i] for i in indices]
    
    def get_all_data(self) -> List[Tuple[torch.Tensor, torch.Tensor]]:
        """Barcha ma'lumotlarni olish"""
        return self.buffer.copy()
    
    def clear(self) -> None:
        """Buffer ni tozalash"""
        self.buffer.clear()
        self.current_size = 0


class ContinualLearningManager:
    """Uzluksiz o'rganish uchun boshqaruvchi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Model yaratish
        self.model = self._create_model()
        
        # Strategiya tanlash
        strategy_name = config.get('strategy', 'ewc')
        self.strategy = self._create_strategy(strategy_name)
        
        # Framework yaratish
        self.framework = ContinualLearningFramework(self.model, self.strategy)
        
        # Memory buffer
        self.memory_buffer = MemoryReplayBuffer(
            max_size=config.get('memory_buffer_size', 5000)
        )
        
        # Training history va performance tracking
        self.training_stats = {
            'task_results': {},
            'overall_performance': {},
            'forgetting_metrics': {}
        }
        
    def _create_model(self) -> nn.Module:
        """Model yaratish"""
        input_dim = self.config.get('input_dim', 20)
        hidden_dims = self.config.get('hidden_dims', [64, 32, 16])
        
        model_type = self.config.get('model_type', 'pnn')
        
        if model_type == 'pnn':
            return ProgressiveNeuralNetwork(input_dim, hidden_dims)
        else:
            # Oddiy feedforward network
            layers = []
            prev_dim = input_dim
            
            for hidden_dim in hidden_dims:
                layers.append(nn.Linear(prev_dim, hidden_dim))
                layers.append(nn.ReLU())
                prev_dim = hidden_dim
            
            layers.append(nn.Linear(prev_dim, 1))
            
            return nn.Sequential(*layers)
    
    def _create_strategy(self, strategy_name: str) -> ContinualLearningStrategy:
        """Strategiya yaratish"""
        if strategy_name == 'ewc':
            return EWCStrategy(self.model, 
                             lambda_ewc=self.config.get('lambda_ewc', 1000.0))
        elif strategy_name == 'lwf':
            return LwFStrategy(self.model,
                             temperature=self.config.get('temperature', 2.0),
                             alpha=self.config.get('alpha', 0.5))
        elif strategy_name == 'gem':
            return GEMStrategy(self.model,
                             memory_strength=self.config.get('memory_strength', 0.5))
        else:
            # Default EWC
            return EWCStrategy(self.model)
    
    async def learn_from_stream(self, data_stream: List[Tuple[torch.Tensor, torch.Tensor]], 
                               task_labels: List[int]) -> Dict[str, Any]:
        """Ma'lumotlar oqimidan o'rganish"""
        self.logger.info("Stream data dan o'rganish boshlanmoqda...")
        
        # Ma'lumotlarni vazifalarga ajratish
        tasks_data = self._organize_data_by_tasks(data_stream, task_labels)
        
        results = {}
        
        for task_id, task_data in tasks_data.items():
            self.logger.info(f"Vazifa {task_id} o'qitilmoqda...")
            
            # Train/val split
            train_data, val_data = self._split_train_val(task_data)
            
            # DataLoader yaratish
            train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
            val_loader = DataLoader(val_data, batch_size=32, shuffle=False)
            
            # Train qilish
            task_result = self.framework.train_on_task(
                train_loader, val_loader,
                epochs=self.config.get('epochs_per_task', 50),
                task_name=f"stream_task_{task_id}"
            )
            
            results[f"task_{task_id}"] = task_result
            
            # Memory buffer ga ma'lumot qo'shish
            for data, target in train_data:
                self.memory_buffer.add((data, target))
        
        self.training_stats['task_results'].update(results)
        
        self.logger.info("Stream o'rganish tugallandi")
        return results
    
    def _organize_data_by_tasks(self, data_stream: List[Tuple[torch.Tensor, torch.Tensor]], 
                                task_labels: List[int]) -> Dict[int, List[Tuple[torch.Tensor, torch.Tensor]]]:
        """Ma'lumotlarni vazifalarga ajratish"""
        tasks_data = {}
        
        for (data, target), task_label in zip(data_stream, task_labels):
            if task_label not in tasks_data:
                tasks_data[task_label] = []
            tasks_data[task_label].append((data, target))
            
        return tasks_data
    
    def _split_train_val(self, task_data: List[Tuple[torch.Tensor, torch.Tensor]], 
                        train_ratio: float = 0.8) -> Tuple[List[Tuple[torch.Tensor, torch.Tensor]], 
                                                          List[Tuple[torch.Tensor, torch.Tensor]]]:
        """Train va validation ma'lumotlariga ajratish"""
        np.random.shuffle(task_data)
        split_idx = int(len(task_data) * train_ratio)
        
        train_data = task_data[:split_idx]
        val_data = task_data[split_idx:]
        
        return train_data, val_data
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Performance hisoboti"""
        report = {
            'training_statistics': self.training_stats,
            'model_architecture': str(self.model),
            'strategy_used': type(self.strategy).__name__,
            'memory_buffer_size': self.memory_buffer.current_size,
            'total_tasks_trained': self.framework.current_task,
            'checkpoint_info': {
                'training_history_length': len(self.framework.training_history),
                'tasks_performance': self.framework.task_performance
            }
        }
        
        return report
    
    def save_model(self, filepath: str) -> None:
        """Model va konfiguratsiyani saqlash"""
        self.framework.save_checkpoint(filepath)
        
        # Qo'shimcha konfiguratsiya saqlash
        config_filepath = filepath.replace('.pth', '_config.json')
        with open(config_filepath, 'w') as f:
            json.dump(self.config, f, indent=2)
            
        self.logger.info(f"Model saqlandi: {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Model va konfiguratsiyani yuklash"""
        self.framework.load_checkpoint(filepath)
        
        # Konfiguratsiya yuklash
        config_filepath = filepath.replace('.pth', '_config.json')
        try:
            with open(config_filepath, 'r') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
        except FileNotFoundError:
            self.logger.warning(f"Konfiguratsiya fayl topilmadi: {config_filepath}")
            
        self.logger.info(f"Model yuklandi: {filepath}")


def create_synthetic_task_data(input_dim: int, num_samples: int = 1000, 
                              num_features: int = 10, noise_level: float = 0.1) -> Tuple[List[Tuple[torch.Tensor, torch.Tensor]], List[int]]:
    """Sinov uchun ma'lumot yaratish"""
    
    data = []
    task_labels = []
    
    for task_id in range(num_features):
        # Har bir vazifa uchun turli pattern yaratish
        X = torch.randn(num_samples, input_dim)
        
        # Turli vazifalar uchun turli target pattern
        if task_id % 3 == 0:
            # Linear pattern
            weights = torch.randn(input_dim, 1)
            y = X @ weights + noise_level * torch.randn(num_samples, 1)
        elif task_id % 3 == 1:
            # Polynomial pattern
            X_squared = X ** 2
            weights = torch.randn(input_dim, 1)
            y = X @ weights + 0.1 * X_squared @ weights + noise_level * torch.randn(num_samples, 1)
        else:
            # Sinusoidal pattern
            weights = torch.randn(input_dim, 1)
            y = torch.sin(X @ weights) + noise_level * torch.randn(num_samples, 1)
        
        # Data va label ni saqlash
        for i in range(num_samples):
            data.append((X[i:i+1], y[i:i+1]))
            task_labels.append(task_id)
    
    return data, task_labels


# Test va misol
if __name__ == "__main__":
    # Logging sozlash
    logging.basicConfig(level=logging.INFO)
    
    # Konfiguratsiya
    config = {
        'model_type': 'pnn',
        'input_dim': 10,
        'hidden_dims': [64, 32, 16],
        'strategy': 'ewc',
        'lambda_ewc': 1000.0,
        'epochs_per_task': 30,
        'memory_buffer_size': 2000
    }
    
    # Manager yaratish
    manager = ContinualLearningManager(config)
    
    # Sinov ma'lumotlari yaratish
    print("Sinov ma'lumotlari yaratilmoqda...")
    data_stream, task_labels = create_synthetic_task_data(
        input_dim=10, 
        num_samples=500, 
        num_features=5
    )
    
    # O'rganish
    print("Uzluksiz o'rganish boshlanmoqda...")
    results = asyncio.run(manager.learn_from_stream(data_stream, task_labels))
    
    # Performance hisoboti
    print("\n=== PERFORMANCE HISOBOTI ===")
    report = manager.get_performance_report()
    for key, value in report.items():
        if isinstance(value, (int, float, str)):
            print(f"{key}: {value}")
        elif isinstance(value, dict):
            print(f"{key}: {len(value)} items")
    
    # Model saqlash
    print("\nModel saqlanmoqda...")
    manager.save_model('continual_learning_model.pth')
    
    print("Sinov tugallandi!")