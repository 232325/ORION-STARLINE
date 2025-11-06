"""
Multi-Market Knowledge Transfer - Cross-market model sharing
Generic multi-market adapter va cross-market transfer mechanisms
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import warnings
from collections import deque, defaultdict
from abc import ABC, abstractmethod
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import json
warnings.filterwarnings('ignore')

# Import individual market adapters
from .stock_adaptation import (
    MarketConfig, MarketAdapter, StockMarketAdapter,
    ForexMarketAdapter, MetalMarketAdapter, CryptoMarketAdapter,
    CrossMarketKnowledgeTransfer, MarketDataPreprocessor, MarketRegimeDetector
)

@dataclass
class MultiMarketConfig:
    """Multi-market system configuration"""
    # Market definitions
    markets: List[str] = field(default_factory=lambda: ['stock', 'forex', 'metal', 'crypto'])
    primary_market: str = 'stock'
    
    # Cross-market settings
    enable_cross_market_transfer: bool = True
    similarity_threshold: float = 0.6
    transfer_learning_rate: float = 0.01
    
    # Ensemble settings
    enable_market_ensemble: bool = True
    ensemble_method: str = 'weighted_voting'  # 'weighted_voting', 'stacking', 'dynamic_selection'
    market_weights: Dict[str, float] = field(default_factory=lambda: {
        'stock': 0.4, 'forex': 0.3, 'metal': 0.2, 'crypto': 0.1
    })
    
    # Adaptation settings
    auto_adaptation: bool = True
    adaptation_frequency: int = 100
    performance_threshold: float = 0.05
    
    # Performance tracking
    track_market_performance: bool = True
    performance_window: int = 500
    
    # Risk management
    market_risk_weights: Dict[str, float] = field(default_factory=lambda: {
        'stock': 1.0, 'forex': 0.8, 'metal': 0.6, 'crypto': 1.5  # Higher risk for crypto
    })

class MarketEnsemble:
    """Multi-market ensemble system"""
    
    def __init__(self, config: MultiMarketConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MarketEnsemble")
        
        # Market adapters
        self.market_adapters = {}
        self.market_models = {}
        self.market_performance = {}
        
        # Ensemble management
        self.ensemble_weights = config.market_weights.copy()
        self.performance_history = deque(maxlen=config.performance_window)
        
        # Risk management
        self.risk_weights = config.market_risk_weights
        
        # State tracking
        self.is_trained = False
        self.last_update = None
        
    def register_market(self, market_type: str, model: BaseEstimator, 
                       market_data: Optional[pd.DataFrame] = None) -> None:
        """Register a market with its model"""
        
        # Create market adapter
        market_config = MarketConfig(market_type=market_type)
        adapter = create_market_adapter(market_type, market_config)
        
        # Adapt model to market if data provided
        if market_data is not None:
            adaptation_result = adapter.adapt_to_market(market_data, model)
            self.logger.info(f"Adapted {market_type} model: {adaptation_result}")
        
        # Store market information
        self.market_adapters[market_type] = adapter
        self.market_models[market_type] = model
        self.market_performance[market_type] = {
            'adaptation_count': 0,
            'success_rate': 0.0,
            'avg_performance': 0.0
        }
        
        self.logger.info(f"Registered market: {market_type}")
    
    def update_market_model(self, market_type: str, new_data: pd.DataFrame) -> Dict[str, Any]:
        """Update model for specific market"""
        
        if market_type not in self.market_adapters:
            raise ValueError(f"Market {market_type} not registered")
        
        adapter = self.market_adapters[market_type]
        model = self.market_models[market_type]
        
        # Perform adaptation
        adaptation_result = adapter.adapt_to_market(new_data, model)
        
        # Update performance tracking
        if adaptation_result['success']:
            self.market_performance[market_type]['adaptation_count'] += 1
            self.market_performance[market_type]['avg_performance'] = (
                self.market_performance[market_type]['avg_performance'] * 0.9 + 
                adaptation_result.get('performance_change', 0) * 0.1
            )
        
        # Update ensemble weights if dynamic weighting enabled
        if self.config.enable_market_ensemble and self.config.ensemble_method == 'weighted_voting':
            self._update_ensemble_weights()
        
        self.last_update = datetime.now()
        
        return adaptation_result
    
    def predict_ensemble(self, features: np.ndarray) -> Union[int, float, np.ndarray]:
        """Make ensemble prediction across all markets"""
        
        if not self.market_models:
            raise ValueError("No models registered for ensemble prediction")
        
        market_predictions = {}
        market_weights = {}
        
        # Get predictions from each market
        for market_type, model in self.market_models.items():
            try:
                if hasattr(model, 'predict_proba'):
                    prediction_proba = model.predict_proba(features.reshape(1, -1))[0]
                    prediction = np.argmax(prediction_proba)
                    confidence = np.max(prediction_proba)
                else:
                    prediction = model.predict(features.reshape(1, -1))[0]
                    confidence = 0.8  # Default confidence
                
                market_predictions[market_type] = prediction
                market_weights[market_type] = self.ensemble_weights.get(market_type, 1.0) * confidence
                
            except Exception as e:
                self.logger.warning(f"Prediction failed for {market_type}: {e}")
                continue
        
        if not market_predictions:
            raise ValueError("No successful predictions from any market")
        
        # Ensemble prediction
        if self.config.ensemble_method == 'weighted_voting':
            return self._weighted_voting(market_predictions, market_weights)
        elif self.config.ensemble_method == 'stacking':
            return self._stacking_ensemble(features, market_predictions)
        elif self.config.ensemble_method == 'dynamic_selection':
            return self._dynamic_selection(features, market_predictions)
        else:
            # Simple majority voting
            predictions_array = np.array(list(market_predictions.values()))
            return int(np.round(np.mean(predictions_array)))
    
    def _weighted_voting(self, predictions: Dict[str, Any], weights: Dict[str, float]) -> int:
        """Weighted voting ensemble"""
        
        if len(predictions) == 1:
            return list(predictions.values())[0]
        
        # Group predictions by value
        prediction_groups = defaultdict(float)
        total_weight = 0
        
        for market_type, prediction in predictions.items():
            weight = weights[market_type] * self.risk_weights.get(market_type, 1.0)
            prediction_groups[prediction] += weight
            total_weight += weight
        
        # Select prediction with highest weight
        best_prediction = max(prediction_groups.items(), key=lambda x: x[1])
        confidence = best_prediction[1] / total_weight
        
        self.logger.debug(f"Weighted voting: {prediction_groups}, confidence: {confidence:.3f}")
        
        return int(best_prediction[0])
    
    def _stacking_ensemble(self, features: np.ndarray, predictions: Dict[str, Any]) -> int:
        """Stacking ensemble (simplified)"""
        
        # For simplicity, use weighted average
        weighted_sum = 0
        total_weight = 0
        
        for market_type, prediction in predictions.items():
            weight = self.ensemble_weights.get(market_type, 1.0)
            weighted_sum += prediction * weight
            total_weight += weight
        
        ensemble_prediction = weighted_sum / total_weight if total_weight > 0 else 0
        
        return int(np.round(ensemble_prediction))
    
    def _dynamic_selection(self, features: np.ndarray, predictions: Dict[str, Any]) -> int:
        """Dynamic ensemble selection based on current conditions"""
        
        # Simple dynamic selection: choose prediction from best-performing recent market
        best_market = max(
            self.market_performance.items(),
            key=lambda x: x[1]['avg_performance']
        )[0]
        
        if best_market in predictions:
            return predictions[best_market]
        else:
            # Fallback to weighted voting
            weights = {market: self.market_performance[market]['avg_performance'] 
                      for market in predictions}
            return self._weighted_voting(predictions, weights)
    
    def _update_ensemble_weights(self) -> None:
        """Update ensemble weights based on recent performance"""
        
        total_performance = sum(
            self.market_performance[market]['avg_performance'] 
            for market in self.market_models.keys()
        )
        
        if total_performance > 0:
            for market_type in self.market_models.keys():
                performance = self.market_performance[market_type]['avg_performance']
                self.ensemble_weights[market_type] = performance / total_performance
        
        self.logger.debug(f"Updated ensemble weights: {self.ensemble_weights}")
    
    def evaluate_ensemble_performance(self, test_features: np.ndarray, 
                                    test_labels: np.ndarray) -> Dict[str, Any]:
        """Evaluate ensemble performance"""
        
        if not self.market_models:
            return {'error': 'No models registered'}
        
        # Get ensemble predictions
        ensemble_predictions = []
        for i in range(len(test_features)):
            try:
                pred = self.predict_ensemble(test_features[i])
                ensemble_predictions.append(pred)
            except Exception as e:
                self.logger.error(f"Ensemble prediction failed for sample {i}: {e}")
                ensemble_predictions.append(0)  # Default prediction
        
        ensemble_predictions = np.array(ensemble_predictions)
        
        # Calculate metrics
        if len(np.unique(test_labels)) <= 10:  # Classification
            accuracy = accuracy_score(test_labels, ensemble_predictions)
            
            # Individual market performance
            individual_performance = {}
            for market_type, model in self.market_models.items():
                try:
                    market_preds = model.predict(test_features)
                    market_acc = accuracy_score(test_labels, market_preds)
                    individual_performance[market_type] = market_acc
                except Exception as e:
                    individual_performance[market_type] = 0.0
        else:  # Regression
            mse = mean_squared_error(test_labels, ensemble_predictions)
            accuracy = 1.0 / (1.0 + mse)  # Convert to 0-1 scale
            
            individual_performance = {}
            for market_type, model in self.market_models.items():
                try:
                    market_preds = model.predict(test_features)
                    market_mse = mean_squared_error(test_labels, market_preds)
                    individual_performance[market_type] = 1.0 / (1.0 + market_mse)
                except Exception as e:
                    individual_performance[market_type] = 0.0
        
        # Performance history
        self.performance_history.append({
            'timestamp': datetime.now(),
            'ensemble_accuracy': accuracy,
            'individual_performance': individual_performance,
            'ensemble_weights': self.ensemble_weights.copy()
        })
        
        return {
            'ensemble_accuracy': accuracy,
            'individual_market_performance': individual_performance,
            'ensemble_weights': self.ensemble_weights,
            'performance_improvement': self._calculate_performance_improvement(individual_performance, accuracy)
        }
    
    def _calculate_performance_improvement(self, individual_performance: Dict[str, float], 
                                         ensemble_accuracy: float) -> float:
        """Calculate performance improvement from ensemble"""
        
        if not individual_performance:
            return 0.0
        
        best_individual = max(individual_performance.values())
        improvement = ensemble_accuracy - best_individual
        
        return improvement
    
    def get_ensemble_summary(self) -> Dict[str, Any]:
        """Get comprehensive ensemble summary"""
        
        return {
            'registered_markets': list(self.market_models.keys()),
            'ensemble_method': self.config.ensemble_method,
            'current_weights': self.ensemble_weights,
            'market_performance': self.market_performance,
            'recent_performance': list(self.performance_history)[-10:] if self.performance_history else [],
            'is_trained': self.is_trained,
            'last_update': self.last_update,
            'total_predictions': len(self.performance_history),
            'risk_weights': self.risk_weights
        }

class CrossMarketTransferManager:
    """Manager for cross-market knowledge transfer"""
    
    def __init__(self, config: MultiMarketConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.CrossMarketTransfer")
        
        # Transfer system
        self.transfer_system = create_cross_market_transfer_system()
        
        # Market relationships
        self.market_relationships = {}
        self.transfer_history = []
        self.successful_transfers = []
        
        # Model repository
        self.source_models = {}
        self.transferred_models = {}
        
    def register_source_model(self, market_type: str, model: BaseEstimator, 
                            model_metadata: Dict[str, Any] = None) -> None:
        """Register source model for transfer"""
        
        self.source_models[market_type] = {
            'model': model,
            'metadata': model_metadata or {},
            'registration_time': datetime.now()
        }
        
        self.logger.info(f"Registered source model for {market_type}")
    
    def transfer_model_to_market(self, source_market: str, target_market: str,
                               target_data: pd.DataFrame,
                               similarity_threshold: float = None) -> Dict[str, Any]:
        """Transfer model from source to target market"""
        
        if source_market not in self.source_models:
            raise ValueError(f"Source model for {source_market} not registered")
        
        if similarity_threshold is None:
            similarity_threshold = self.config.similarity_threshold
        
        source_model_info = self.source_models[source_market]
        source_model = source_model_info['model']
        
        # Perform cross-market transfer
        transfer_result = self.transfer_system.transfer_knowledge(
            source_market, target_market, source_model, target_data, similarity_threshold
        )
        
        # Record transfer
        transfer_record = {
            'timestamp': datetime.now(),
            'source_market': source_market,
            'target_market': target_market,
            'similarity': transfer_result.get('similarity', 0.0),
            'success': transfer_result.get('success', False),
            'performance': transfer_result.get('performance', 0.0),
            'transfer_strength': transfer_result.get('transfer_strength', 0.0)
        }
        
        self.transfer_history.append(transfer_record)
        
        if transfer_result.get('success', False):
            self.successful_transfers.append(transfer_record)
            self.transferred_models[f"{source_market}_to_{target_market}"] = {
                'source_market': source_market,
                'target_market': target_market,
                'model': transfer_result.get('model'),
                'transfer_info': transfer_result
            }
        
        self.logger.info(f"Transfer {source_market} -> {target_market}: "
                        f"{'Success' if transfer_result.get('success') else 'Failed'}")
        
        return transfer_result
    
    def suggest_best_source_market(self, target_market: str, 
                                 target_data: pd.DataFrame) -> Dict[str, Any]:
        """Suggest best source market for transfer"""
        
        if not self.source_models:
            return {'error': 'No source models registered'}
        
        similarities = {}
        
        for source_market in self.source_models.keys():
            # Calculate similarity (simplified)
            source_data = self.source_models[source_market].get('metadata', {}).get('sample_data')
            if source_data is not None:
                similarity = self.transfer_system.calculate_market_similarity(
                    source_market, target_market, source_data, target_data
                )
            else:
                # Default similarities based on domain knowledge
                similarity = self.transfer_system._get_domain_knowledge_similarity(
                    source_market, target_market
                )
            
            similarities[source_market] = similarity
        
        # Sort by similarity
        sorted_markets = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'target_market': target_market,
            'source_market_suggestions': sorted_markets,
            'best_source': sorted_markets[0][0] if sorted_markets else None,
            'best_similarity': sorted_markets[0][1] if sorted_markets else 0.0
        }
    
    def batch_transfer_to_markets(self, target_markets: List[str], 
                                market_data: Dict[str, pd.DataFrame],
                                max_similarity_threshold: float = None) -> Dict[str, Any]:
        """Perform batch transfers to multiple markets"""
        
        if max_similarity_threshold is None:
            max_similarity_threshold = self.config.similarity_threshold
        
        transfer_results = {}
        
        for target_market in target_markets:
            if target_market not in market_data:
                self.logger.warning(f"No data provided for target market: {target_market}")
                continue
            
            # Suggest best source
            suggestion = self.suggest_best_source_market(target_market, market_data[target_market])
            
            if suggestion['best_source'] and suggestion['best_similarity'] > max_similarity_threshold:
                # Perform transfer
                transfer_result = self.transfer_model_to_market(
                    suggestion['best_source'], target_market, market_data[target_market]
                )
                
                transfer_results[target_market] = {
                    'suggestion': suggestion,
                    'transfer_result': transfer_result
                }
            else:
                transfer_results[target_market] = {
                    'suggestion': suggestion,
                    'transfer_result': {'success': False, 'reason': 'Low similarity'}
                }
        
        return {
            'batch_transfer_summary': {
                'total_markets': len(target_markets),
                'successful_transfers': sum(1 for r in transfer_results.values() 
                                          if r['transfer_result'].get('success', False)),
                'average_similarity': np.mean([r['suggestion']['best_similarity'] 
                                             for r in transfer_results.values()])
            },
            'individual_results': transfer_results
        }
    
    def get_transfer_summary(self) -> Dict[str, Any]:
        """Get comprehensive transfer summary"""
        
        return {
            'transfer_system_summary': self.transfer_system.get_transfer_summary(),
            'registered_source_markets': list(self.source_models.keys()),
            'total_transfers': len(self.transfer_history),
            'successful_transfers': len(self.successful_transfers),
            'success_rate': len(self.successful_transfers) / len(self.transfer_history) if self.transfer_history else 0,
            'transferred_models_count': len(self.transferred_models),
            'recent_transfers': self.transfer_history[-10:] if self.transfer_history else []
        }

class MultiMarketSystem:
    """Complete multi-market adaptive system"""
    
    def __init__(self, config: MultiMarketConfig = None):
        self.config = config or MultiMarketConfig()
        self.logger = logging.getLogger(f"{__name__}.MultiMarketSystem")
        
        # Core components
        self.ensemble = MarketEnsemble(self.config)
        self.transfer_manager = CrossMarketTransferManager(self.config)
        
        # System state
        self.is_initialized = False
        self.system_status = {}
        
    def initialize_system(self, market_data: Dict[str, pd.DataFrame], 
                         models: Dict[str, BaseEstimator]) -> Dict[str, Any]:
        """Initialize the multi-market system"""
        
        self.logger.info("Initializing multi-market system...")
        
        # Register all markets
        for market_type, model in models.items():
            if market_type in market_data:
                self.ensemble.register_market(market_type, model, market_data[market_type])
                self.transfer_manager.register_source_model(
                    market_type, model, {'sample_data': market_data[market_type]}
                )
        
        self.is_initialized = True
        
        # System status
        self.system_status = {
            'initialization_time': datetime.now(),
            'registered_markets': list(models.keys()),
            'ensemble_summary': self.ensemble.get_ensemble_summary(),
            'transfer_summary': self.transfer_manager.get_transfer_summary()
        }
        
        self.logger.info(f"System initialized with {len(models)} markets")
        
        return self.system_status
    
    def predict(self, features: np.ndarray) -> Union[int, float, np.ndarray]:
        """Make multi-market prediction"""
        
        if not self.is_initialized:
            raise ValueError("System must be initialized before prediction")
        
        return self.ensemble.predict_ensemble(features)
    
    def adapt_to_market_conditions(self, market_updates: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Adapt system to new market conditions"""
        
        adaptation_results = {}
        
        for market_type, new_data in market_updates.items():
            if market_type in self.ensemble.market_models:
                # Update individual market
                update_result = self.ensemble.update_market_model(market_type, new_data)
                adaptation_results[market_type] = update_result
                
                # Check if cross-market transfer is beneficial
                if self.config.enable_cross_market_transfer:
                    transfer_result = self._evaluate_cross_market_transfer(market_type, new_data)
                    adaptation_results[f"{market_type}_transfer"] = transfer_result
        
        return {
            'adaptation_results': adaptation_results,
            'adaptation_time': datetime.now(),
            'total_adaptations': len(adaptation_results)
        }
    
    def _evaluate_cross_market_transfer(self, target_market: str, target_data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate if cross-market transfer would be beneficial"""
        
        # Suggest best source market
        suggestion = self.transfer_manager.suggest_best_source_market(target_market, target_data)
        
        if suggestion['best_source'] and suggestion['best_similarity'] > self.config.similarity_threshold:
            # Check current market performance
            current_performance = self.ensemble.market_performance.get(target_market, {})
            
            if current_performance.get('avg_performance', 0) < 0.7:  # Poor performance threshold
                # Perform transfer
                transfer_result = self.transfer_manager.transfer_model_to_market(
                    suggestion['best_source'], target_market, target_data
                )
                
                if transfer_result.get('success', False):
                    # Update ensemble with new model
                    new_model = transfer_result.get('model')
                    if new_model:
                        self.ensemble.market_models[target_market] = new_model
                        self.logger.info(f"Updated {target_market} model via cross-market transfer")
                
                return transfer_result
        
        return {'success': False, 'reason': 'Transfer not beneficial'}
    
    def get_system_performance(self, test_data: Optional[Dict[str, Tuple[np.ndarray, np.ndarray]]] = None) -> Dict[str, Any]:
        """Get comprehensive system performance"""
        
        performance_report = {
            'system_status': self.system_status,
            'ensemble_summary': self.ensemble.get_ensemble_summary(),
            'transfer_summary': self.transfer_manager.get_transfer_summary()
        }
        
        if test_data:
            # Evaluate on test data if provided
            test_results = {}
            
            for market_type, (test_features, test_labels) in test_data.items():
                if market_type in self.ensemble.market_models:
                    market_result = self.ensemble.evaluate_ensemble_performance(test_features, test_labels)
                    test_results[market_type] = market_result
            
            performance_report['test_performance'] = test_results
        
        return performance_report
    
    def save_system_state(self, filepath: str) -> None:
        """Save system state to file"""
        
        system_state = {
            'config': self.config.__dict__,
            'ensemble_weights': self.ensemble.ensemble_weights,
            'market_performance': self.ensemble.market_performance,
            'transfer_history': self.transfer_manager.transfer_history,
            'system_status': self.system_status,
            'is_initialized': self.is_initialized
        }
        
        with open(filepath, 'w') as f:
            json.dump(system_state, f, indent=2, default=str)
        
        self.logger.info(f"System state saved to {filepath}")
    
    def load_system_state(self, filepath: str) -> None:
        """Load system state from file"""
        
        with open(filepath, 'r') as f:
            system_state = json.load(f)
        
        # Restore state (simplified)
        self.ensemble.ensemble_weights = system_state.get('ensemble_weights', {})
        self.ensemble.market_performance = system_state.get('market_performance', {})
        self.transfer_manager.transfer_history = system_state.get('transfer_history', [])
        self.system_status = system_state.get('system_status', {})
        self.is_initialized = system_state.get('is_initialized', False)
        
        self.logger.info(f"System state loaded from {filepath}")

# Utility functions
def create_multi_market_system(config: Optional[MultiMarketConfig] = None) -> MultiMarketSystem:
    """Create multi-market adaptive system"""
    
    if config is None:
        config = MultiMarketConfig()
    
    return MultiMarketSystem(config)

def create_forex_adapter() -> ForexMarketAdapter:
    """Create forex market adapter"""
    config = MarketConfig(market_type='forex')
    return ForexMarketAdapter(config)

def create_metal_adapter() -> MetalMarketAdapter:
    """Create metal market adapter"""
    config = MarketConfig(market_type='metal')
    return MetalMarketAdapter(config)

def create_crypto_adapter() -> CryptoMarketAdapter:
    """Create crypto market adapter"""
    config = MarketConfig(market_type='crypto')
    return CryptoMarketAdapter(config)