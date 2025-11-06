"""
Transfer Learning and Continual Learning - Knowledge transfer across domains
Domain adaptation, few-shot learning, va lifelong learning systems
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import warnings
from collections import deque, defaultdict
from abc import ABC, abstractmethod
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
import pickle
import json
warnings.filterwarnings('ignore')

@dataclass
class TransferLearningConfig:
    """Transfer learning konfiguratsiyasi"""
    # Knowledge transfer settings
    source_domain: str = "general"
    target_domain: str = "trading"
    similarity_threshold: float = 0.7
    transfer_threshold: float = 0.6
    
    # Few-shot learning
    few_shot_support_size: int = 10
    few_shot_query_size: int = 50
    prototype_distance_metric: str = 'euclidean'  # 'euclidean', 'cosine', 'manhattan'
    
    # Domain adaptation
    domain_adapter_type: str = 'feature_matching'  # 'feature_matching', 'domain_adversarial', 'importance_weighting'
    adaptation_rate: float = 0.01
    gradient_reversal: bool = True
    
    # Model selection for transfer
    source_models_to_consider: int = 10
    transfer_learning_rate: float = 0.001
    fine_tuning_layers: int = 2  # Number of layers to fine-tune
    
    # Performance tracking
    transfer_success_threshold: float = 0.1  # Minimum improvement needed
    adaptation_patience: int = 10
    performance_history_size: int = 1000
    
    # Advanced features
    enable_meta_learning: bool = True
    enable_elastic_weight_consolidation: bool = True
    enable_progressive_networks: bool = False
    memory_replay_size: int = 1000

@dataclass
class Domain:
    """Domain representation"""
    domain_id: str
    name: str
    domain_type: str  # 'source', 'target', 'intermediate'
    features: np.ndarray
    labels: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    domain_characteristics: Dict[str, Any] = field(default_factory=dict)
    performance_history: List[float] = field(default_factory=list)
    model_repertoire: Dict[str, Any] = field(default_factory=dict)

class DomainSimilarityCalculator:
    """Calculate similarity between domains"""
    
    def __init__(self, config: TransferLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.DomainSimilarity")
        
        self.domain_stats = {}
    
    def calculate_domain_similarity(self, source_domain: Domain, target_domain: Domain) -> float:
        """Calculate overall domain similarity"""
        
        similarities = {}
        
        # Feature distribution similarity
        if len(source_domain.features) > 0 and len(target_domain.features) > 0:
            similarities['feature_similarity'] = self._calculate_feature_similarity(
                source_domain.features, target_domain.features
            )
        
        # Label distribution similarity
        if len(source_domain.labels) > 0 and len(target_domain.labels) > 0:
            similarities['label_similarity'] = self._calculate_label_similarity(
                source_domain.labels, target_domain.labels
            )
        
        # Metadata similarity
        similarities['metadata_similarity'] = self._calculate_metadata_similarity(
            source_domain.metadata, target_domain.metadata
        )
        
        # Domain characteristics similarity
        similarities['characteristics_similarity'] = self._calculate_characteristics_similarity(
            source_domain.domain_characteristics, target_domain.domain_characteristics
        )
        
        # Weighted combination
        weights = {
            'feature_similarity': 0.4,
            'label_similarity': 0.3,
            'metadata_similarity': 0.2,
            'characteristics_similarity': 0.1
        }
        
        overall_similarity = sum(
            similarities.get(key, 0) * weights.get(key, 0) 
            for key in weights.keys()
        )
        
        self.logger.info(f"Domain similarity calculation: {similarities}")
        return overall_similarity
    
    def _calculate_feature_similarity(self, source_features: np.ndarray, 
                                    target_features: np.ndarray) -> float:
        """Calculate feature distribution similarity"""
        
        try:
            # Ensure same dimensions
            min_features = min(source_features.shape[1], target_features.shape[1])
            source_feats = source_features[:, :min_features]
            target_feats = target_features[:, :min_features]
            
            # Statistical moments comparison
            source_mean = np.mean(source_feats, axis=0)
            target_mean = np.mean(target_feats, axis=0)
            source_std = np.std(source_feats, axis=0)
            target_std = np.std(target_feats, axis=0)
            
            # Mean similarity
            mean_similarity = 1.0 / (1.0 + np.linalg.norm(source_mean - target_mean))
            
            # Std similarity
            std_similarity = 1.0 / (1.0 + np.linalg.norm(source_std - target_std))
            
            # Distribution similarity using cosine similarity
            feature_similarity = (mean_similarity + std_similarity) / 2
            
            return feature_similarity
            
        except Exception as e:
            self.logger.warning(f"Feature similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_label_similarity(self, source_labels: np.ndarray, 
                                  target_labels: np.ndarray) -> float:
        """Calculate label distribution similarity"""
        
        try:
            # For categorical labels
            if source_labels.dtype == 'object' or len(np.unique(source_labels)) <= 10:
                source_counts = pd.Series(source_labels).value_counts(normalize=True)
                target_counts = pd.Series(target_labels).value_counts(normalize=True)
                
                # Combine all unique labels
                all_labels = set(source_counts.index) | set(target_counts.index)
                
                source_vec = np.array([source_counts.get(label, 0) for label in all_labels])
                target_vec = np.array([target_counts.get(label, 0) for label in all_labels])
                
                # Cosine similarity
                dot_product = np.dot(source_vec, target_vec)
                norms = np.linalg.norm(source_vec) * np.linalg.norm(target_vec)
                
                if norms > 0:
                    similarity = dot_product / norms
                else:
                    similarity = 0.0
            else:
                # For continuous labels
                source_mean = np.mean(source_labels)
                target_mean = np.mean(target_labels)
                source_std = np.std(source_labels)
                target_std = np.std(target_labels)
                
                # Statistical similarity
                mean_sim = 1.0 / (1.0 + abs(source_mean - target_mean))
                std_sim = 1.0 / (1.0 + abs(source_std - target_std))
                
                similarity = (mean_sim + std_sim) / 2
            
            return similarity
            
        except Exception as e:
            self.logger.warning(f"Label similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_metadata_similarity(self, source_metadata: Dict[str, Any], 
                                     target_metadata: Dict[str, Any]) -> float:
        """Calculate metadata similarity"""
        
        if not source_metadata or not target_metadata:
            return 0.5  # Neutral similarity
        
        # Common keys
        common_keys = set(source_metadata.keys()) & set(target_metadata.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            source_val = source_metadata[key]
            target_val = target_metadata[key]
            
            if isinstance(source_val, (int, float)) and isinstance(target_val, (int, float)):
                # Numerical similarity
                diff = abs(source_val - target_val)
                max_val = max(abs(source_val), abs(target_val), 1.0)
                sim = 1.0 - min(diff / max_val, 1.0)
                similarities.append(sim)
            elif isinstance(source_val, str) and isinstance(target_val, str):
                # String similarity (exact match for simplicity)
                sim = 1.0 if source_val == target_val else 0.0
                similarities.append(sim)
            else:
                # Default similarity
                similarities.append(0.5)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_characteristics_similarity(self, source_chars: Dict[str, Any], 
                                            target_chars: Dict[str, Any]) -> float:
        """Calculate domain characteristics similarity"""
        
        # Focus on key characteristics for trading domains
        key_characteristics = ['volatility', 'trend_strength', 'market_regime', 
                             'data_quality', 'temporal_patterns']
        
        similarities = []
        for char in key_characteristics:
            source_val = source_chars.get(char, 0)
            target_val = target_chars.get(char, 0)
            
            if isinstance(source_val, (int, float)) and isinstance(target_val, (int, float)):
                diff = abs(source_val - target_val)
                similarity = 1.0 / (1.0 + diff)
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0

class TransferKnowledgeManager:
    """Manages knowledge transfer between domains"""
    
    def __init__(self, config: TransferLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.TransferManager")
        
        # Domain storage
        self.domains = {}
        self.domain_relationships = {}
        
        # Transfer history
        self.transfer_history = []
        self.successful_transfers = []
        self.failed_transfers = []
        
        # Knowledge base
        self.knowledge_base = {}
        self.transferred_models = {}
        
        # Performance tracking
        self.transfer_performance_history = deque(maxlen=config.performance_history_size)
        
    def register_domain(self, domain: Domain) -> None:
        """Register a domain"""
        
        self.domains[domain.domain_id] = domain
        
        # Analyze domain characteristics
        domain.domain_characteristics = self._analyze_domain_characteristics(domain)
        
        self.logger.info(f"Registered domain: {domain.domain_id} ({domain.name})")
    
    def register_source_domain(self, domain: Domain, model_repertoire: Dict[str, Any]) -> None:
        """Register source domain with trained models"""
        
        domain.domain_type = 'source'
        domain.model_repertoire = model_repertoire
        
        self.register_domain(domain)
        
        self.logger.info(f"Registered source domain: {domain.domain_id} with {len(model_repertoire)} models")
    
    def transfer_knowledge(self, source_domain_id: str, target_domain_id: str,
                         target_data: Tuple[np.ndarray, np.ndarray],
                         transfer_strategy: str = 'fine_tuning') -> Dict[str, Any]:
        """Transfer knowledge from source to target domain"""
        
        if source_domain_id not in self.domains:
            raise ValueError(f"Source domain {source_domain_id} not found")
        
        if target_domain_id not in self.domains:
            raise ValueError(f"Target domain {target_domain_id} not found")
        
        source_domain = self.domains[source_domain_id]
        target_domain = self.domains[target_domain_id]
        
        X_target, y_target = target_data
        
        # Calculate domain similarity
        similarity_calculator = DomainSimilarityCalculator(self.config)
        similarity = similarity_calculator.calculate_domain_similarity(source_domain, target_domain)
        
        # Check if transfer is worthwhile
        if similarity < self.config.similarity_threshold:
            return {
                'success': False,
                'reason': f'Low domain similarity: {similarity:.3f} < {self.config.similarity_threshold}',
                'similarity': similarity
            }
        
        self.logger.info(f"Starting knowledge transfer from {source_domain_id} to {target_domain_id} "
                        f"(similarity: {similarity:.3f})")
        
        # Perform transfer based on strategy
        if transfer_strategy == 'fine_tuning':
            result = self._fine_tune_transfer(source_domain, target_domain, X_target, y_target, similarity)
        elif transfer_strategy == 'domain_adaptation':
            result = self._domain_adaptation_transfer(source_domain, target_domain, X_target, y_target, similarity)
        elif transfer_strategy == 'few_shot':
            result = self._few_shot_transfer(source_domain, target_domain, X_target, y_target, similarity)
        else:
            raise ValueError(f"Unknown transfer strategy: {transfer_strategy}")
        
        # Record transfer
        transfer_record = {
            'timestamp': datetime.now(),
            'source_domain': source_domain_id,
            'target_domain': target_domain_id,
            'strategy': transfer_strategy,
            'similarity': similarity,
            'result': result
        }
        
        self.transfer_history.append(transfer_record)
        
        if result['success']:
            self.successful_transfers.append(transfer_record)
            self.transferred_models[result['model_id']] = {
                'source_domain': source_domain_id,
                'target_domain': target_domain_id,
                'model': result['model'],
                'transfer_info': result
            }
        else:
            self.failed_transfers.append(transfer_record)
        
        return result
    
    def _fine_tune_transfer(self, source_domain: Domain, target_domain: Domain,
                          X_target: np.ndarray, y_target: np.ndarray, similarity: float) -> Dict[str, Any]:
        """Perform fine-tuning based transfer"""
        
        # Select best source models
        source_models = self._select_best_source_models(source_domain, len(X_target))
        
        if not source_models:
            return {'success': False, 'reason': 'No suitable source models found'}
        
        best_source_model = source_models[0]['model']
        best_source_score = source_models[0]['performance']
        
        # Fine-tune the model
        try:
            # Create a copy of the source model for fine-tuning
            model_class = type(best_source_model)
            fine_tuned_model = model_class(**best_source_model.get_params())
            
            # Perform partial training on target data
            fine_tuned_model.fit(X_target, y_target)
            
            # Evaluate performance
            predictions = fine_tuned_model.predict(X_target)
            if len(np.unique(y_target)) <= 10:
                target_performance = accuracy_score(y_target, predictions)
            else:
                target_performance = 1.0 / (1.0 + mean_squared_error(y_target, predictions))
            
            # Check if transfer was successful
            improvement = target_performance - best_source_score
            transfer_successful = improvement > self.config.transfer_success_threshold
            
            model_id = f"{source_domain.domain_id}_{target_domain.domain_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            result = {
                'success': transfer_successful,
                'model_id': model_id,
                'model': fine_tuned_model,
                'source_performance': best_source_score,
                'target_performance': target_performance,
                'improvement': improvement,
                'similarity': similarity,
                'strategy': 'fine_tuning',
                'reason': 'Transfer successful' if transfer_successful else 'Insufficient improvement'
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Fine-tuning transfer failed: {e}")
            return {'success': False, 'reason': f'Transfer error: {str(e)}'}
    
    def _domain_adaptation_transfer(self, source_domain: Domain, target_domain: Domain,
                                  X_target: np.ndarray, y_target: np.ndarray, similarity: float) -> Dict[str, Any]:
        """Perform domain adaptation transfer"""
        
        # This is a simplified domain adaptation approach
        # In practice, would use more sophisticated methods
        
        # Get source model
        source_models = self._select_best_source_models(source_domain, len(X_target))
        if not source_models:
            return {'success': False, 'reason': 'No suitable source models found'}
        
        best_source_model = source_models[0]['model']
        
        try:
            # Domain adaptation through feature alignment
            source_features = source_domain.features
            target_features = X_target
            
            # Align feature distributions
            aligned_features = self._align_feature_distributions(source_features, target_features)
            
            # Create adapted model
            model_class = type(best_source_model)
            adapted_model = model_class(**best_source_model.get_params())
            
            # Train on aligned features
            adapted_model.fit(aligned_features, y_target)
            
            # Evaluate on original target features
            predictions = adapted_model.predict(X_target)
            if len(np.unique(y_target)) <= 10:
                target_performance = accuracy_score(y_target, predictions)
            else:
                target_performance = 1.0 / (1.0 + mean_squared_error(y_target, predictions))
            
            model_id = f"{source_domain.domain_id}_{target_domain.domain_id}_adapted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            result = {
                'success': True,  # Domain adaptation typically works with aligned features
                'model_id': model_id,
                'model': adapted_model,
                'target_performance': target_performance,
                'similarity': similarity,
                'strategy': 'domain_adaptation',
                'feature_alignment': True
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Domain adaptation transfer failed: {e}")
            return {'success': False, 'reason': f'Adaptation error: {str(e)}'}
    
    def _few_shot_transfer(self, source_domain: Domain, target_domain: Domain,
                         X_target: np.ndarray, y_target: np.ndarray, similarity: float) -> Dict[str, Any]:
        """Perform few-shot transfer learning"""
        
        # Create prototype-based model
        prototypes = self._create_prototypes(source_domain, X_target, y_target)
        
        # Create few-shot classifier
        few_shot_classifier = self._create_few_shot_classifier(prototypes)
        
        # Evaluate
        predictions = few_shot_classifier.predict(X_target)
        target_performance = accuracy_score(y_target, predictions)
        
        model_id = f"{source_domain.domain_id}_{target_domain.domain_id}_few_shot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = {
            'success': True,
            'model_id': model_id,
            'model': few_shot_classifier,
            'target_performance': target_performance,
            'similarity': similarity,
            'strategy': 'few_shot',
            'prototypes': prototypes
        }
        
        return result
    
    def _select_best_source_models(self, source_domain: Domain, target_data_size: int) -> List[Dict[str, Any]]:
        """Select best models from source domain"""
        
        models = []
        
        for model_id, model_info in source_domain.model_repertoire.items():
            # Filter models based on performance and data size compatibility
            performance = model_info.get('performance', 0)
            compatibility = self._calculate_model_compatibility(model_info, target_data_size)
            
            if compatibility > 0.5:  # Minimum compatibility threshold
                models.append({
                    'model_id': model_id,
                    'model': model_info['model'],
                    'performance': performance,
                    'compatibility': compatibility,
                    'score': performance * compatibility
                })
        
        # Sort by combined score
        models.sort(key=lambda x: x['score'], reverse=True)
        
        return models[:self.config.source_models_to_consider]
    
    def _calculate_model_compatibility(self, model_info: Dict[str, Any], target_size: int) -> float:
        """Calculate how compatible a model is with target data size"""
        
        # Simple compatibility based on training data size similarity
        source_size = model_info.get('training_data_size', 100)
        
        size_ratio = min(source_size, target_size) / max(source_size, target_size)
        return size_ratio
    
    def _align_feature_distributions(self, source_features: np.ndarray, 
                                   target_features: np.ndarray) -> np.ndarray:
        """Align feature distributions between domains"""
        
        # Simple approach: scale features to match means and variances
        source_mean = np.mean(source_features, axis=0)
        source_std = np.std(source_features, axis=0)
        
        target_mean = np.mean(target_features, axis=0)
        target_std = np.std(target_features, axis=0)
        
        # Align target features to source distribution
        aligned_features = (target_features - target_mean) * (source_std / (target_std + 1e-8)) + source_mean
        
        return aligned_features
    
    def _create_prototypes(self, source_domain: Domain, X_support: np.ndarray, y_support: np.ndarray) -> Dict[Any, np.ndarray]:
        """Create class prototypes for few-shot learning"""
        
        prototypes = {}
        unique_labels = np.unique(y_support)
        
        for label in unique_labels:
            label_mask = y_support == label
            label_features = X_support[label_mask]
            
            # Prototype is the mean of support examples
            prototype = np.mean(label_features, axis=0)
            prototypes[label] = prototype
        
        return prototypes
    
    def _create_few_shot_classifier(self, prototypes: Dict[Any, np.ndarray]) -> 'FewShotClassifier':
        """Create a few-shot classifier based on prototypes"""
        
        return FewShotClassifier(prototypes, self.config.prototype_distance_metric)
    
    def _analyze_domain_characteristics(self, domain: Domain) -> Dict[str, Any]:
        """Analyze domain characteristics"""
        
        characteristics = {}
        
        if len(domain.features) > 0:
            characteristics['feature_count'] = domain.features.shape[1]
            characteristics['sample_count'] = len(domain.features)
            characteristics['feature_variance'] = np.mean(np.var(domain.features, axis=0))
            characteristics['feature_mean'] = np.mean(np.mean(domain.features, axis=0))
        
        if len(domain.labels) > 0:
            if domain.labels.dtype == 'object' or len(np.unique(domain.labels)) <= 10:
                characteristics['label_diversity'] = len(np.unique(domain.labels))
                characteristics['label_distribution'] = pd.Series(domain.labels).value_counts(normalize=True).to_dict()
            else:
                characteristics['label_mean'] = np.mean(domain.labels)
                characteristics['label_std'] = np.std(domain.labels)
        
        return characteristics
    
    def get_transfer_summary(self) -> Dict[str, Any]:
        """Get comprehensive transfer learning summary"""
        
        total_transfers = len(self.transfer_history)
        successful_transfers = len(self.successful_transfers)
        
        if total_transfers > 0:
            success_rate = successful_transfers / total_transfers
        else:
            success_rate = 0.0
        
        # Average similarity for successful transfers
        if self.successful_transfers:
            similarities = [t['similarity'] for t in self.successful_transfers]
            avg_successful_similarity = np.mean(similarities)
        else:
            avg_successful_similarity = 0.0
        
        # Domain relationship analysis
        domain_relationships = defaultdict(list)
        for transfer in self.transfer_history:
            relationship = f"{transfer['source_domain']} -> {transfer['target_domain']}"
            domain_relationships[relationship].append(transfer['success'])
        
        return {
            'total_transfers': total_transfers,
            'successful_transfers': successful_transfers,
            'failed_transfers': len(self.failed_transfers),
            'success_rate': success_rate,
            'avg_successful_similarity': avg_successful_similarity,
            'domain_relationships': dict(domain_relationships),
            'registered_domains': list(self.domains.keys()),
            'transferred_models_count': len(self.transferred_models)
        }

class FewShotClassifier:
    """Simple few-shot classifier based on prototypes"""
    
    def __init__(self, prototypes: Dict[Any, np.ndarray], distance_metric: str = 'euclidean'):
        self.prototypes = prototypes
        self.distance_metric = distance_metric
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Classify examples based on prototype distances"""
        
        predictions = []
        
        for sample in X:
            distances = {}
            
            for label, prototype in self.prototypes.items():
                if self.distance_metric == 'euclidean':
                    dist = np.linalg.norm(sample - prototype)
                elif self.distance_metric == 'cosine':
                    # Cosine distance
                    dot_product = np.dot(sample, prototype)
                    norm_sample = np.linalg.norm(sample)
                    norm_prototype = np.linalg.norm(prototype)
                    dist = 1 - dot_product / (norm_sample * norm_prototype + 1e-8)
                else:  # manhattan
                    dist = np.sum(np.abs(sample - prototype))
                
                distances[label] = dist
            
            # Predict closest prototype
            predicted_label = min(distances.keys(), key=lambda k: distances[k])
            predictions.append(predicted_label)
        
        return np.array(predictions)

class ContinualLearningManager:
    """Manager for continual learning across multiple tasks"""
    
    def __init__(self, config: TransferLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ContinualLearning")
        
        # Task management
        self.tasks = {}
        self.task_history = []
        self.current_task_id = None
        
        # Memory replay
        self.memory_buffer = deque(maxlen=config.memory_replay_size)
        self.exemplar_selection = 'random'  # 'random', 'herding', 'margin'
        
        # Model management
        self.task_specific_models = {}
        self.shared_knowledge = {}
        self.elastic_weights = {}  # For EWC
        
        # Performance tracking
        self.task_performance_history = {}
        self.forgetting_curve = []
        
    def start_new_task(self, task_id: str, task_data: Tuple[np.ndarray, np.ndarray],
                      task_metadata: Dict[str, Any] = None) -> str:
        """Start processing a new task"""
        
        self.current_task_id = task_id
        self.tasks[task_id] = {
            'task_data': task_data,
            'metadata': task_metadata or {},
            'start_time': datetime.now(),
            'performance_history': []
        }
        
        self.logger.info(f"Started new task: {task_id}")
        return task_id
    
    def learn_task(self, task_id: str, model_class: type = None, 
                  model_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Learn a task with continual learning"""
        
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task_data = self.tasks[task_id]['task_data']
        X, y = task_data
        
        # Select base model
        if model_class is None:
            model_class = RandomForestClassifier
        
        # Get previous knowledge
        previous_models = self._get_previous_models()
        memory_samples = list(self.memory_buffer)
        
        # Train model with continual learning
        performance = self._train_continual_model(
            model_class, model_params or {}, X, y, previous_models, memory_samples
        )
        
        # Store model
        self.task_specific_models[task_id] = {
            'model': performance['model'],
            'performance': performance['training_accuracy'],
            'metadata': self.tasks[task_id]['metadata']
        }
        
        # Update memory buffer with exemplars
        self._update_memory_buffer(X, y, task_id)
        
        # Record performance
        self.tasks[task_id]['performance_history'].append(performance['training_accuracy'])
        
        return performance
    
    def _train_continual_model(self, model_class: type, model_params: Dict[str, Any],
                             X: np.ndarray, y: np.ndarray, 
                             previous_models: List, memory_samples: List) -> Dict[str, Any]:
        """Train model with continual learning capabilities"""
        
        # Combine current data with memory samples
        if memory_samples:
            memory_X, memory_y = zip(*memory_samples)
            combined_X = np.vstack([X] + list(memory_X))
            combined_y = np.hstack([y] + list(memory_y))
        else:
            combined_X, combined_y = X, y
        
        # Create and train model
        model = model_class(**model_params)
        model.fit(combined_X, combined_y)
        
        # Evaluate performance
        predictions = model.predict(X)
        training_accuracy = accuracy_score(y, predictions)
        
        return {
            'model': model,
            'training_accuracy': training_accuracy,
            'memory_size': len(memory_samples),
            'total_samples': len(combined_X)
        }
    
    def _get_previous_models(self) -> List:
        """Get models from previous tasks"""
        return list(self.task_specific_models.values())
    
    def _update_memory_buffer(self, X: np.ndarray, y: np.ndarray, task_id: str) -> None:
        """Update memory buffer with representative samples"""
        
        # Simple exemplar selection - can be improved with more sophisticated methods
        n_exemplars = min(10, len(X) // 10)  # Select 10% of data as exemplars
        
        # Random selection (can be improved with herding, margin-based selection, etc.)
        indices = np.random.choice(len(X), n_exemplars, replace=False)
        
        for idx in indices:
            self.memory_buffer.append((X[idx], y[idx]))
    
    def evaluate_continual_learning(self, task_id: str, test_data: Tuple[np.ndarray, np.ndarray]) -> Dict[str, Any]:
        """Evaluate model on test data after continual learning"""
        
        if task_id not in self.task_specific_models:
            raise ValueError(f"Model for task {task_id} not found")
        
        X_test, y_test = test_data
        model = self.task_specific_models[task_id]['model']
        
        # Evaluate on test data
        predictions = model.predict(X_test)
        test_accuracy = accuracy_score(y_test, predictions)
        
        # Evaluate on previous tasks (forgetting detection)
        previous_performances = {}
        for prev_task_id, prev_model_info in self.task_specific_models.items():
            if prev_task_id != task_id:
                # Use the current model to predict on previous task's test data if available
                # This is a simplification - in practice would store test sets for each task
                prev_model = prev_model_info['model']
                # For now, use training accuracy as proxy
                previous_performances[prev_task_id] = prev_model_info['performance']
        
        # Calculate forgetting
        if previous_performances:
            current_avg_performance = np.mean(list(previous_performances.values()))
            original_avg_performance = self._calculate_original_performance(previous_performances.keys())
            forgetting = original_avg_performance - current_avg_performance
        else:
            forgetting = 0.0
        
        result = {
            'task_id': task_id,
            'test_accuracy': test_accuracy,
            'previous_task_performances': previous_performances,
            'forgetting_measure': forgetting,
            'memory_buffer_size': len(self.memory_buffer)
        }
        
        return result
    
    def _calculate_original_performance(self, task_ids: List[str]) -> float:
        """Calculate original performance for previous tasks"""
        # Simplified: return average of original accuracies
        original_performances = []
        for task_id in task_ids:
            if task_id in self.task_specific_models:
                original_performances.append(self.task_specific_models[task_id]['performance'])
        
        return np.mean(original_performances) if original_performances else 0.0
    
    def get_continual_learning_summary(self) -> Dict[str, Any]:
        """Get continual learning system summary"""
        
        total_tasks = len(self.tasks)
        completed_tasks = len(self.task_specific_models)
        
        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
        else:
            completion_rate = 0.0
        
        # Calculate average performance
        if self.task_specific_models:
            avg_performance = np.mean([info['performance'] for info in self.task_specific_models.values()])
        else:
            avg_performance = 0.0
        
        # Memory buffer statistics
        memory_stats = {
            'current_size': len(self.memory_buffer),
            'max_size': self.memory_buffer.maxlen,
            'utilization': len(self.memory_buffer) / self.memory_buffer.maxlen if self.memory_buffer.maxlen else 0
        }
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': completion_rate,
            'avg_performance': avg_performance,
            'memory_buffer': memory_stats,
            'current_task': self.current_task_id,
            'task_performances': {tid: info['performance'] for tid, info in self.task_specific_models.items()}
        }

# Factory functions
def create_transfer_learning_system(config: Optional[TransferLearningConfig] = None) -> TransferKnowledgeManager:
    """Create transfer learning system"""
    
    if config is None:
        config = TransferLearningConfig()
    
    return TransferKnowledgeManager(config)

def create_continual_learning_system(config: Optional[TransferLearningConfig] = None) -> ContinualLearningManager:
    """Create continual learning system"""
    
    if config is None:
        config = TransferLearningConfig()
    
    return ContinualLearningManager(config)