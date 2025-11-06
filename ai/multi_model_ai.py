"""
Multi-Model AI Tizimi - Orion Starline
Turli AI modellari integratsiyasi, ensemble learning va model boshqaruvi
"""

import asyncio
import numpy as np
import pandas as pd
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import joblib
import pickle
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor,
    VotingClassifier, VotingRegressor,
    BaggingClassifier, BaggingRegressor,
    AdaBoostClassifier, AdaBoostRegressor
)
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.model_selection import (
    train_test_split, cross_val_score, GridSearchCV, 
    RandomizedSearchCV, TimeSeriesSplit
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    classification_report, confusion_matrix
)
from sklearn.feature_selection import SelectKBest, f_regression, f_classif
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, LSTM, GRU, Conv1D, MaxPooling1D, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam, RMSprop
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.regularizers import l1, l2, l1_l2
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier, CatBoostRegressor
import warnings
warnings.filterwarnings('ignore')

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """AI model turlari"""
    # Klassik ML modellari
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    CATBOOST = "catboost"
    SVM = "svm"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"
    KNN = "knn"
    DECISION_TREE = "decision_tree"
    NAIVE_BAYES = "naive_bayes"
    LINEAR_REGRESSION = "linear_regression"
    
    # Ensemble modellari
    VOTING_ENSEMBLE = "voting_ensemble"
    BAGGING = "bagging"
    BOOSTING = "boosting"
    STACKING = "stacking"
    
    # Deep Learning
    CNN = "cnn"
    GRU = "gru"
    TRANSFORMER = "transformer"

class TaskType(Enum):
    """Vazifa turlari"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    TIME_SERIES = "time_series"
    FORECASTING = "forecasting"
    CLUSTERING = "clustering"

class ModelStatus(Enum):
    """Model holati"""
    TRAINING = "training"
    TRAINING_COMPLETE = "training_complete"
    EVALUATING = "evaluating"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

@dataclass
class ModelConfig:
    """Model konfiguratsiyasi"""
    model_type: ModelType
    task_type: TaskType
    hyperparameters: Dict[str, Any]
    features: List[str]
    target: str
    validation_split: float = 0.2
    test_split: float = 0.1
    random_state: int = 42
    preprocessing: Dict[str, Any] = None

@dataclass
class ModelMetrics:
    """Model metrikalari"""
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mse: Optional[float] = None
    mae: Optional[float] = None
    r2_score: Optional[float] = None
    rmse: Optional[float] = None
    cross_val_score: Optional[float] = None
    training_time: float = 0.0
    inference_time: float = 0.0
    memory_usage: float = 0.0

@dataclass
class TrainedModel:
    """O'qitilgan model"""
    model_id: str
    model_type: ModelType
    task_type: TaskType
    model: Any
    scaler: Optional[Any] = None
    feature_selector: Optional[Any] = None
    metrics: ModelMetrics = None
    config: ModelConfig = None
    training_date: datetime = None
    status: ModelStatus = ModelStatus.TRAINING
    version: str = "1.0.0"
    description: str = ""

class ModelManager:
    """Model boshqaruvchi"""
    
    def __init__(self, storage_path: str = "./models"):
        self.storage_path = storage_path
        self.models: Dict[str, TrainedModel] = {}
        self.model_registry = {}
        
        # Storage papkasini yaratish
        import os
        os.makedirs(storage_path, exist_ok=True)
        
    async def save_model(self, model: TrainedModel) -> bool:
        """Model saqlash"""
        try:
            model_path = f"{self.storage_path}/{model.model_id}.pkl"
            
            # Model ma'lumotlarini saqlash
            model_data = {
                'model': model.model,
                'scaler': model.scaler,
                'feature_selector': model.feature_selector,
                'config': asdict(model.config),
                'metrics': asdict(model.metrics) if model.metrics else None,
                'training_date': model.training_date.isoformat() if model.training_date else None,
                'version': model.version,
                'description': model.description
            }
            
            # Faylga saqlash
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            # Registry ga qo'shish
            self.model_registry[model.model_id] = {
                'path': model_path,
                'type': model.model_type.value,
                'task_type': model.task_type.value,
                'version': model.version,
                'created': datetime.now().isoformat()
            }
            
            logger.info(f"Model saqlandi: {model.model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Model saqlashda xato: {str(e)}")
            return False
    
    async def load_model(self, model_id: str) -> Optional[TrainedModel]:
        """Model yuklash"""
        try:
            if model_id not in self.model_registry:
                logger.warning(f"Model topilmadi registry da: {model_id}")
                return None
            
            registry_info = self.model_registry[model_id]
            model_path = registry_info['path']
            
            # Faylni o'qish
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Model qayta tiklash
            trained_model = TrainedModel(
                model_id=model_id,
                model_type=ModelType(model_data['config']['model_type']),
                task_type=TaskType(model_data['config']['task_type']),
                model=model_data['model'],
                scaler=model_data.get('scaler'),
                feature_selector=model_data.get('feature_selector'),
                config=ModelConfig(**model_data['config']),
                training_date=datetime.fromisoformat(model_data['training_date']) if model_data['training_date'] else None,
                version=model_data['version'],
                description=model_data['description']
            )
            
            # Metrics qayta tiklash
            if model_data.get('metrics'):
                trained_model.metrics = ModelMetrics(**model_data['metrics'])
            
            trained_model.status = ModelStatus.ACTIVE
            
            logger.info(f"Model yuklandi: {model_id}")
            return trained_model
            
        except Exception as e:
            logger.error(f"Model yuklashda xato: {str(e)}")
            return None
    
    async def delete_model(self, model_id: str) -> bool:
        """Model o'chirish"""
        try:
            if model_id in self.model_registry:
                import os
                model_path = self.model_registry[model_id]['path']
                
                # Faylni o'chirish
                if os.path.exists(model_path):
                    os.remove(model_path)
                
                # Registry dan o'chirish
                del self.model_registry[model_id]
                if model_id in self.models:
                    del self.models[model_id]
                
                logger.info(f"Model o'chirildi: {model_id}")
                return True
            else:
                logger.warning(f"Model topilmadi: {model_id}")
                return False
                
        except Exception as e:
            logger.error(f"Model o'chirishda xato: {str(e)}")
            return False

class ModelFactory:
    """Model yaratuvchi fabrika"""
    
    @staticmethod
    def create_model(config: ModelConfig) -> Any:
        """Model yaratish"""
        
        if config.model_type == ModelType.RANDOM_FOREST:
            return RandomForestClassifier(**config.hyperparameters)
        
        elif config.model_type == ModelType.RANDOM_FOREST and config.task_type == TaskType.REGRESSION:
            return RandomForestRegressor(**config.hyperparameters)
        
        elif config.model_type == ModelType.GRADIENT_BOOSTING:
            if config.task_type == TaskType.CLASSIFICATION:
                return GradientBoostingClassifier(**config.hyperparameters)
            else:
                return GradientBoostingRegressor(**config.hyperparameters)
        
        elif config.model_type == ModelType.XGBOOST:
            if config.task_type == TaskType.CLASSIFICATION:
                return xgb.XGBClassifier(**config.hyperparameters)
            else:
                return xgb.XGBRegressor(**config.hyperparameters)
        
        elif config.model_type == ModelType.LIGHTGBM:
            if config.task_type == TaskType.CLASSIFICATION:
                return lgb.LGBMClassifier(**config.hyperparameters, verbose=-1)
            else:
                return lgb.LGBMRegressor(**config.hyperparameters, verbose=-1)
        
        elif config.model_type == ModelType.CATBOOST:
            if config.task_type == TaskType.CLASSIFICATION:
                return CatBoostClassifier(**config.hyperparameters, verbose=False)
            else:
                return CatBoostRegressor(**config.hyperparameters, verbose=False)
        
        elif config.model_type == ModelType.SVM:
            if config.task_type == TaskType.CLASSIFICATION:
                return SVC(**config.hyperparameters)
            else:
                return SVR(**config.hyperparameters)
        
        elif config.model_type == ModelType.KNN:
            if config.task_type == TaskType.CLASSIFICATION:
                return KNeighborsClassifier(**config.hyperparameters)
            else:
                return KNeighborsRegressor(**config.hyperparameters)
        
        elif config.model_type == ModelType.DECISION_TREE:
            if config.task_type == TaskType.CLASSIFICATION:
                return DecisionTreeClassifier(**config.hyperparameters)
            else:
                return DecisionTreeRegressor(**config.hyperparameters)
        
        elif config.model_type == ModelType.NAIVE_BAYES:
            return GaussianNB(**config.hyperparameters)
        
        elif config.model_type == ModelType.LINEAR_REGRESSION:
            if config.task_type == TaskType.CLASSIFICATION:
                return LogisticRegression(**config.hyperparameters)
            else:
                return LinearRegression(**config.hyperparameters)
        
        elif config.model_type == ModelType.LSTM:
            return ModelFactory._create_lstm_model(config)
        
        elif config.model_type == ModelType.NEURAL_NETWORK:
            return ModelFactory._create_neural_network(config)
        
        elif config.model_type == ModelType.VOTING_ENSEMBLE:
            return ModelFactory._create_voting_ensemble(config)
        
        else:
            raise ValueError(f"Qo'llab-quvvatlanmaydigan model turi: {config.model_type}")
    
    @staticmethod
    def _create_lstm_model(config: ModelConfig) -> Model:
        """LSTM model yaratish"""
        model = Sequential()
        
        # Hyperparameters
        units = config.hyperparameters.get('units', 50)
        layers = config.hyperparameters.get('layers', 2)
        dropout = config.hyperparameters.get('dropout', 0.2)
        learning_rate = config.hyperparameters.get('learning_rate', 0.001)
        
        # Input layer
        model.add(LSTM(units, return_sequences=layers > 1, input_shape=(None, len(config.features))))
        
        # Additional LSTM layers
        for i in range(1, layers):
            if i < layers - 1:
                model.add(LSTM(units, return_sequences=True))
            else:
                model.add(LSTM(units))
            model.add(Dropout(dropout))
        
        # Output layer
        if config.task_type == TaskType.CLASSIFICATION:
            model.add(Dense(1, activation='sigmoid'))
            model.compile(optimizer=Adam(learning_rate=learning_rate), 
                         loss='binary_crossentropy', metrics=['accuracy'])
        else:
            model.add(Dense(1))
            model.compile(optimizer=Adam(learning_rate=learning_rate), 
                         loss='mse', metrics=['mae'])
        
        return model
    
    @staticmethod
    def _create_neural_network(config: ModelConfig) -> Model:
        """Neural Network model yaratish"""
        model = Sequential()
        
        # Hyperparameters
        hidden_layers = config.hyperparameters.get('hidden_layers', [100, 50])
        dropout = config.hyperparameters.get('dropout', 0.3)
        learning_rate = config.hyperparameters.get('learning_rate', 0.001)
        activation = config.hyperparameters.get('activation', 'relu')
        
        # Input layer
        model.add(Dense(hidden_layers[0], activation=activation, input_shape=(len(config.features),)))
        
        # Hidden layers
        for units in hidden_layers[1:]:
            model.add(Dense(units, activation=activation))
            model.add(Dropout(dropout))
        
        # Output layer
        if config.task_type == TaskType.CLASSIFICATION:
            model.add(Dense(1, activation='sigmoid'))
            model.compile(optimizer=Adam(learning_rate=learning_rate), 
                         loss='binary_crossentropy', metrics=['accuracy'])
        else:
            model.add(Dense(1))
            model.compile(optimizer=Adam(learning_rate=learning_rate), 
                         loss='mse', metrics=['mae'])
        
        return model
    
    @staticmethod
    def _create_voting_ensemble(config: ModelConfig) -> Any:
        """Voting Ensemble yaratish"""
        estimators = []
        
        # Base models
        rf_params = config.hyperparameters.get('random_forest', {})
        gb_params = config.hyperparameters.get('gradient_boosting', {})
        
        if config.task_type == TaskType.CLASSIFICATION:
            estimators.append(('rf', RandomForestClassifier(**rf_params)))
            estimators.append(('gb', GradientBoostingClassifier(**gb_params)))
            return VotingClassifier(estimators=estimators, voting='soft')
        else:
            estimators.append(('rf', RandomForestRegressor(**rf_params)))
            estimators.append(('gb', GradientBoostingRegressor(**gb_params)))
            return VotingRegressor(estimators=estimators)

class ModelTrainer:
    """Model o'qituvchi"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.training_history = {}
    
    async def train_model(
        self,
        config: ModelConfig,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None,
        model_id: str = None
    ) -> TrainedModel:
        """Model o'qitish"""
        
        start_time = datetime.now()
        
        # Model ID yaratish
        if model_id is None:
            model_id = f"{config.model_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # TrainedModel obyektini yaratish
            trained_model = TrainedModel(
                model_id=model_id,
                model_type=config.model_type,
                task_type=config.task_type,
                model=None,  # Keyin to'ldiriladi
                config=config,
                training_date=start_time,
                status=ModelStatus.TRAINING
            )
            
            # Model yaratish
            model = ModelFactory.create_model(config)
            trained_model.model = model
            
            # Preprocessing
            scaler = None
            if config.preprocessing and config.preprocessing.get('scaler'):
                scaler_type = config.preprocessing['scaler']
                if scaler_type == 'standard':
                    scaler = StandardScaler()
                elif scaler_type == 'minmax':
                    scaler = MinMaxScaler()
                elif scaler_type == 'robust':
                    scaler = RobustScaler()
                
                if scaler:
                    X_train_scaled = scaler.fit_transform(X_train)
                    if X_val is not None:
                        X_val_scaled = scaler.transform(X_val)
                else:
                    X_train_scaled, X_val_scaled = X_train, X_val
            else:
                X_train_scaled, X_val_scaled = X_train, X_val
            
            # Feature selection
            feature_selector = None
            if config.preprocessing and config.preprocessing.get('feature_selection'):
                k_features = config.preprocessing['feature_selection'].get('k', 'all')
                if k_features != 'all':
                    if config.task_type == TaskType.CLASSIFICATION:
                        feature_selector = SelectKBest(f_classif, k=k_features)
                    else:
                        feature_selector = SelectKBest(f_regression, k=k_features)
                    
                    X_train_scaled = feature_selector.fit_transform(X_train_scaled, y_train)
                    if X_val is not None:
                        X_val_scaled = feature_selector.transform(X_val_scaled)
            
            # Scaler va feature selector ni saqlash
            trained_model.scaler = scaler
            trained_model.feature_selector = feature_selector
            
            # Training
            if config.model_type in [ModelType.LSTM, ModelType.NEURAL_NETWORK, ModelType.CNN]:
                await self._train_deep_learning_model(trained_model, X_train_scaled, y_train, X_val_scaled, y_val)
            else:
                await self._train_classical_model(trained_model, X_train_scaled, y_train, X_val_scaled, y_val)
            
            # Metrics hisoblash
            training_time = (datetime.now() - start_time).total_seconds()
            metrics = await self._evaluate_model(trained_model, X_train_scaled, y_train)
            metrics.training_time = training_time
            
            trained_model.metrics = metrics
            trained_model.status = ModelStatus.TRAINING_COMPLETE
            
            # Model ni saqlash
            await self.model_manager.save_model(trained_model)
            
            logger.info(f"Model muvaffaqiyatli o'qitildi: {model_id}")
            return trained_model
            
        except Exception as e:
            logger.error(f"Model o'qitishda xato: {str(e)}")
            trained_model.status = ModelStatus.ERROR
            raise
    
    async def _train_classical_model(
        self, 
        trained_model: TrainedModel, 
        X_train: np.ndarray, 
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ):
        """Klassik model o'qitish"""
        
        model = trained_model.model
        config = trained_model.config
        
        # Cross-validation
        if config.validation_split > 0:
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy' if config.task_type == TaskType.CLASSIFICATION else 'r2')
            logger.info(f"Cross-validation score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Training
        model.fit(X_train, y_train)
        
        # Validation metrics
        if X_val is not None and y_val is not None:
            val_predictions = model.predict(X_val)
            if config.task_type == TaskType.CLASSIFICATION:
                val_accuracy = accuracy_score(y_val, val_predictions)
                logger.info(f"Validation accuracy: {val_accuracy:.4f}")
            else:
                val_r2 = r2_score(y_val, val_predictions)
                logger.info(f"Validation R2 score: {val_r2:.4f}")
    
    async def _train_deep_learning_model(
        self, 
        trained_model: TrainedModel, 
        X_train: np.ndarray, 
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ):
        """Deep learning model o'qitish"""
        
        model = trained_model.model
        config = trained_model.config
        
        # Data reshape for deep learning
        if config.model_type == ModelType.LSTM:
            # LSTM uchun 3D shape kerak
            if len(X_train.shape) == 2:
                X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
                if X_val is not None:
                    X_val = X_val.reshape((X_val.shape[0], 1, X_val.shape[1]))
        
        # Callbacks
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(factor=0.2, patience=5, min_lr=0.0001)
        ]
        
        # Validation data
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        
        # Training
        history = model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=config.hyperparameters.get('epochs', 100),
            batch_size=config.hyperparameters.get('batch_size', 32),
            callbacks=callbacks,
            verbose=0
        )
        
        # History saqlash
        trained_model.training_history = history.history
    
    async def _evaluate_model(
        self, 
        trained_model: TrainedModel, 
        X_test: np.ndarray, 
        y_test: np.ndarray
    ) -> ModelMetrics:
        """Model baholash"""
        
        model = trained_model.model
        task_type = trained_model.task_type
        
        # Predictions
        start_inference = datetime.now()
        predictions = model.predict(X_test)
        inference_time = (datetime.now() - start_inference).total_seconds()
        
        metrics = ModelMetrics()
        
        if task_type == TaskType.CLASSIFICATION:
            # Classification metrics
            metrics.accuracy = accuracy_score(y_test, predictions)
            metrics.precision = precision_score(y_test, predictions, average='weighted')
            metrics.recall = recall_score(y_test, predictions, average='weighted')
            metrics.f1_score = f1_score(y_test, predictions, average='weighted')
        else:
            # Regression metrics
            metrics.mse = mean_squared_error(y_test, predictions)
            metrics.mae = mean_absolute_error(y_test, predictions)
            metrics.r2_score = r2_score(y_test, predictions)
            metrics.rmse = np.sqrt(metrics.mse)
        
        metrics.inference_time = inference_time
        
        return metrics

class ModelPredictor:
    """Model bashorat qiluvchi"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.loaded_models: Dict[str, TrainedModel] = {}
    
    async def predict(
        self, 
        model_id: str, 
        data: np.ndarray, 
        return_probability: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """Bashorat qilish"""
        
        # Model yuklash (agar yuklanmagan bo'lsa)
        if model_id not in self.loaded_models:
            model = await self.model_manager.load_model(model_id)
            if model is None:
                raise ValueError(f"Model topilmadi: {model_id}")
            self.loaded_models[model_id] = model
        
        trained_model = self.loaded_models[model_id]
        model = trained_model.model
        
        # Preprocessing
        processed_data = self._preprocess_data(data, trained_model)
        
        # Prediction
        if trained_model.model_type == ModelType.LSTM:
            if len(processed_data.shape) == 2:
                processed_data = processed_data.reshape((processed_data.shape[0], 1, processed_data.shape[1]))
        
        predictions = model.predict(processed_data, verbose=0)
        
        # Probability qaytarish (agar so'ralgan bo'lsa)
        if return_probability and trained_model.task_type == TaskType.CLASSIFICATION:
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(processed_data)
                return predictions, probabilities
            else:
                return predictions, None
        else:
            return predictions
    
    def _preprocess_data(self, data: np.ndarray, trained_model: TrainedModel) -> np.ndarray:
        """Data preprocessing"""
        
        processed_data = data.copy()
        
        # Scaling
        if trained_model.scaler:
            processed_data = trained_model.scaler.transform(processed_data)
        
        # Feature selection
        if trained_model.feature_selector:
            processed_data = trained_model.feature_selector.transform(processed_data)
        
        return processed_data
    
    async def ensemble_predict(
        self,
        model_ids: List[str],
        data: np.ndarray,
        method: str = "average"
    ) -> np.ndarray:
        """Ensemble bashorat qilish"""
        
        predictions = []
        
        # Har bir model uchun bashorat olish
        for model_id in model_ids:
            pred = await self.predict(model_id, data)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # Ensemble method
        if method == "average":
            ensemble_pred = np.mean(predictions, axis=0)
        elif method == "weighted":
            # Model og'irliklarini hisoblash
            weights = []
            for model_id in model_ids:
                if model_id in self.loaded_models:
                    weights.append(self.loaded_models[model_id].metrics.f1_score or 
                                  self.loaded_models[model_id].metrics.r2_score or 0.5)
                else:
                    weights.append(0.5)
            
            weights = np.array(weights)
            weights = weights / np.sum(weights)  # Normalization
            ensemble_pred = np.average(predictions, axis=0, weights=weights)
        else:
            raise ValueError(f"Qo'llab-quvvatlanmaydigan ensemble method: {method}")
        
        return ensemble_pred

class MultiModelAI:
    """Multi-Model AI asosiy klassi"""
    
    def __init__(self, storage_path: str = "./models"):
        self.model_manager = ModelManager(storage_path)
        self.model_trainer = ModelTrainer(self.model_manager)
        self.model_predictor = ModelPredictor(self.model_manager)
        
        # AutoML pipelines
        self.automl_pipeline = AutoMLPipeline(self.model_manager)
    
    async def train_multiple_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        task_type: TaskType,
        model_configs: List[ModelConfig] = None
    ) -> Dict[str, TrainedModel]:
        """Bir nechta model o'qitish"""
        
        # Default configs
        if model_configs is None:
            model_configs = self._get_default_configs(task_type)
        
        trained_models = {}
        
        for config in model_configs:
            try:
                logger.info(f"O'qitish boshlanmoqda: {config.model_type.value}")
                
                trained_model = await self.model_trainer.train_model(
                    config, X_train, y_train, X_test, y_test
                )
                
                trained_models[config.model_type.value] = trained_model
                logger.info(f"Muvaffaqiyatli tugallandi: {config.model_type.value}")
                
            except Exception as e:
                logger.error(f"Model o'qitishda xato {config.model_type.value}: {str(e)}")
        
        return trained_models
    
    def _get_default_configs(self, task_type: TaskType) -> List[ModelConfig]:
        """Default model konfiguratsiyalarini olish"""
        
        if task_type == TaskType.CLASSIFICATION:
            return [
                ModelConfig(
                    model_type=ModelType.RANDOM_FOREST,
                    task_type=TaskType.CLASSIFICATION,
                    hyperparameters={'n_estimators': 100, 'max_depth': 10, 'random_state': 42},
                    features=[],  # Will be set later
                    target="target"
                ),
                ModelConfig(
                    model_type=ModelType.GRADIENT_BOOSTING,
                    task_type=TaskType.CLASSIFICATION,
                    hyperparameters={'n_estimators': 100, 'learning_rate': 0.1, 'max_depth': 6},
                    features=[],
                    target="target"
                ),
                ModelConfig(
                    model_type=ModelType.XGBOOST,
                    task_type=TaskType.CLASSIFICATION,
                    hyperparameters={'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1},
                    features=[],
                    target="target"
                ),
                ModelConfig(
                    model_type=ModelType.VOTING_ENSEMBLE,
                    task_type=TaskType.CLASSIFICATION,
                    hyperparameters={
                        'random_forest': {'n_estimators': 50},
                        'gradient_boosting': {'n_estimators': 50}
                    },
                    features=[],
                    target="target"
                )
            ]
        else:  # REGRESSION
            return [
                ModelConfig(
                    model_type=ModelType.RANDOM_FOREST,
                    task_type=TaskType.REGRESSION,
                    hyperparameters={'n_estimators': 100, 'max_depth': 10, 'random_state': 42},
                    features=[],
                    target="target"
                ),
                ModelConfig(
                    model_type=ModelType.GRADIENT_BOOSTING,
                    task_type=TaskType.REGRESSION,
                    hyperparameters={'n_estimators': 100, 'learning_rate': 0.1, 'max_depth': 6},
                    features=[],
                    target="target"
                ),
                ModelConfig(
                    model_type=ModelType.XGBOOST,
                    task_type=TaskType.REGRESSION,
                    hyperparameters={'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1},
                    features=[],
                    target="target"
                ),
                ModelConfig(
                    model_type=ModelType.LSTM,
                    task_type=TaskType.REGRESSION,
                    hyperparameters={'units': 50, 'layers': 2, 'epochs': 50, 'batch_size': 32},
                    features=[],
                    target="target"
                )
            ]
    
    async def compare_models(self, model_ids: List[str], test_data: Dict) -> Dict[str, Any]:
        """Modellarni solishtirish"""
        
        comparison_results = {}
        
        for model_id in model_ids:
            try:
                # Model yuklash
                trained_model = await self.model_manager.load_model(model_id)
                if trained_model is None:
                    continue
                
                # Prediction
                predictions = await self.model_predictor.predict(
                    model_id, test_data['X_test']
                )
                
                # Metrics hisoblash
                if trained_model.task_type == TaskType.CLASSIFICATION:
                    accuracy = accuracy_score(test_data['y_test'], predictions)
                    precision = precision_score(test_data['y_test'], predictions, average='weighted')
                    recall = recall_score(test_data['y_test'], predictions, average='weighted')
                    f1 = f1_score(test_data['y_test'], predictions, average='weighted')
                    
                    comparison_results[model_id] = {
                        'accuracy': accuracy,
                        'precision': precision,
                        'recall': recall,
                        'f1_score': f1,
                        'training_time': trained_model.metrics.training_time if trained_model.metrics else 0
                    }
                else:
                    mse = mean_squared_error(test_data['y_test'], predictions)
                    mae = mean_absolute_error(test_data['y_test'], predictions)
                    r2 = r2_score(test_data['y_test'], predictions)
                    
                    comparison_results[model_id] = {
                        'mse': mse,
                        'mae': mae,
                        'r2_score': r2,
                        'rmse': np.sqrt(mse),
                        'training_time': trained_model.metrics.training_time if trained_model.metrics else 0
                    }
                    
            except Exception as e:
                logger.error(f"Model solishtirishda xato {model_id}: {str(e)}")
        
        return comparison_results
    
    async def select_best_model(self, model_comparison: Dict[str, Any], metric: str = "f1_score") -> str:
        """Eng yaxshi modelni tanlash"""
        
        if not model_comparison:
            return None
        
        best_model = None
        best_score = -float('inf')
        
        for model_id, metrics in model_comparison.items():
            if metric in metrics and metrics[metric] > best_score:
                best_score = metrics[metric]
                best_model = model_id
        
        return best_model

class AutoMLPipeline:
    """Avtomatik Machine Learning pipeline"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.model_trainer = ModelTrainer(model_manager)
    
    async def auto_train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        task_type: TaskType,
        optimization_metric: str = "auto"
    ) -> Tuple[str, TrainedModel]:
        """Avtomatik model tanlash va o'qitish"""
        
        logger.info("AutoML pipeline boshlanmoqda...")
        
        # Barcha model konfiguratsiyalarini olish
        configs = self._get_comprehensive_configs(task_type)
        
        best_model = None
        best_score = -float('inf')
        best_model_id = None
        
        for config in configs:
            try:
                # Model o'qitish
                trained_model = await self.model_trainer.train_model(
                    config, X_train, y_train, X_test, y_test
                )
                
                # Performance baholash
                score = await self._evaluate_model_performance(trained_model, X_test, y_test, optimization_metric)
                
                logger.info(f"{config.model_type.value} score: {score:.4f}")
                
                if score > best_score:
                    best_score = score
                    best_model = trained_model
                    best_model_id = trained_model.model_id
                
            except Exception as e:
                logger.error(f"AutoML xatosi {config.model_type.value}: {str(e)}")
        
        logger.info(f"Eng yaxshi model: {best_model_id} (score: {best_score:.4f})")
        return best_model_id, best_model
    
    def _get_comprehensive_configs(self, task_type: TaskType) -> List[ModelConfig]:
        """Keng qamrovli model konfiguratsiyalari"""
        
        base_configs = []
        
        if task_type == TaskType.CLASSIFICATION:
            # Random Forest configs
            for n_estimators in [50, 100, 200]:
                for max_depth in [5, 10, 15, None]:
                    base_configs.append(ModelConfig(
                        model_type=ModelType.RANDOM_FOREST,
                        task_type=TaskType.CLASSIFICATION,
                        hyperparameters={
                            'n_estimators': n_estimators,
                            'max_depth': max_depth,
                            'random_state': 42
                        },
                        features=[],
                        target="target"
                    ))
            
            # XGBoost configs
            for n_estimators in [50, 100, 200]:
                for learning_rate in [0.05, 0.1, 0.2]:
                    for max_depth in [3, 6, 9]:
                        base_configs.append(ModelConfig(
                            model_type=ModelType.XGBOOST,
                            task_type=TaskType.CLASSIFICATION,
                            hyperparameters={
                                'n_estimators': n_estimators,
                                'learning_rate': learning_rate,
                                'max_depth': max_depth,
                                'random_state': 42
                            },
                            features=[],
                            target="target"
                        ))
            
            # SVM configs
            for c in [0.1, 1, 10]:
                for gamma in ['scale', 'auto']:
                    base_configs.append(ModelConfig(
                        model_type=ModelType.SVM,
                        task_type=TaskType.CLASSIFICATION,
                        hyperparameters={
                            'C': c,
                            'gamma': gamma,
                            'random_state': 42
                        },
                        features=[],
                        target="target"
                    ))
        
        else:  # REGRESSION
            # Random Forest configs
            for n_estimators in [50, 100, 200]:
                for max_depth in [5, 10, 15, None]:
                    base_configs.append(ModelConfig(
                        model_type=ModelType.RANDOM_FOREST,
                        task_type=TaskType.REGRESSION,
                        hyperparameters={
                            'n_estimators': n_estimators,
                            'max_depth': max_depth,
                            'random_state': 42
                        },
                        features=[],
                        target="target"
                    ))
            
            # XGBoost configs
            for n_estimators in [50, 100, 200]:
                for learning_rate in [0.05, 0.1, 0.2]:
                    for max_depth in [3, 6, 9]:
                        base_configs.append(ModelConfig(
                            model_type=ModelType.XGBOOST,
                            task_type=TaskType.REGRESSION,
                            hyperparameters={
                                'n_estimators': n_estimators,
                                'learning_rate': learning_rate,
                                'max_depth': max_depth,
                                'random_state': 42
                            },
                            features=[],
                            target="target"
                        ))
            
            # LSTM configs
            for units in [25, 50, 100]:
                for layers in [1, 2, 3]:
                    base_configs.append(ModelConfig(
                        model_type=ModelType.LSTM,
                        task_type=TaskType.REGRESSION,
                        hyperparameters={
                            'units': units,
                            'layers': layers,
                            'epochs': 50,
                            'batch_size': 32
                        },
                        features=[],
                        target="target"
                    ))
        
        # Faqat birinchi 20 ta config ni ishlatish (performance uchun)
        return base_configs[:20]
    
    async def _evaluate_model_performance(
        self, 
        trained_model: TrainedModel, 
        X_test: np.ndarray, 
        y_test: np.ndarray,
        metric: str
    ) -> float:
        """Model performance baholash"""
        
        try:
            model = trained_model.model
            
            # Prediction
            predictions = model.predict(X_test)
            
            if trained_model.task_type == TaskType.CLASSIFICATION:
                if metric == "accuracy":
                    return accuracy_score(y_test, predictions)
                elif metric == "f1":
                    return f1_score(y_test, predictions, average='weighted')
                else:  # auto
                    return f1_score(y_test, predictions, average='weighted')
            else:  # REGRESSION
                if metric == "r2":
                    return r2_score(y_test, predictions)
                elif metric == "mse":
                    return -mean_squared_error(y_test, predictions)  # Negative MSE (higher is better)
                else:  # auto
                    return r2_score(y_test, predictions)
                    
        except Exception as e:
            logger.error(f"Performance baholashda xato: {str(e)}")
            return 0.0

# Demo va test funksiyalari
async def demo_multi_model_ai():
    """Multi-Model AI demo"""
    
    print("🤖 Multi-Model AI System Demo")
    print("=" * 50)
    
    # Multi-Model AI tizimini yaratish
    multi_ai = MultiModelAI(storage_path="./demo_models")
    
    # Mock data yaratish
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    # Classification dataset
    X_class = np.random.randn(n_samples, n_features)
    y_class = (X_class[:, 0] + X_class[:, 1] + np.random.randn(n_samples) * 0.1 > 0).astype(int)
    
    # Regression dataset
    X_reg = np.random.randn(n_samples, n_features)
    y_reg = X_class[:, 0] * 2 + X_class[:, 1] * 3 + np.random.randn(n_samples) * 0.1
    
    # Train-test split
    X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(
        X_class, y_class, test_size=0.2, random_state=42, stratify=y_class
    )
    
    X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )
    
    print("\n📊 Classification Models Training:")
    print("-" * 40)
    
    # Classification modellari
    try:
        class_models = await multi_ai.train_multiple_models(
            X_train_class, y_train_class, X_test_class, y_test_class,
            TaskType.CLASSIFICATION
        )
        
        for model_type, model in class_models.items():
            print(f"✅ {model_type}: Accuracy = {model.metrics.accuracy:.3f}")
    except Exception as e:
        print(f"❌ Classification model xatosi: {str(e)}")
    
    print("\n📈 Regression Models Training:")
    print("-" * 40)
    
    # Regression modellari
    try:
        reg_models = await multi_ai.train_multiple_models(
            X_train_reg, y_train_reg, X_test_reg, y_test_reg,
            TaskType.REGRESSION
        )
        
        for model_type, model in reg_models.items():
            print(f"✅ {model_type}: R2 Score = {model.metrics.r2_score:.3f}")
    except Exception as e:
        print(f"❌ Regression model xatosi: {str(e)}")
    
    print("\n🎯 AutoML Pipeline Test:")
    print("-" * 40)
    
    # AutoML test
    try:
        best_model_id, best_model = await multi_ai.automl_pipeline.auto_train(
            X_train_class, y_train_class, X_test_class, y_test_class,
            TaskType.CLASSIFICATION, "f1"
        )
        print(f"🏆 Eng yaxshi model: {best_model_id}")
        print(f"   Model type: {best_model.model_type.value}")
        print(f"   F1 Score: {best_model.metrics.f1_score:.3f}")
    except Exception as e:
        print(f"❌ AutoML xatosi: {str(e)}")
    
    print("\n🔍 Model Comparison:")
    print("-" * 40)
    
    # Model solishtirish
    try:
        model_ids = list(class_models.keys())
        comparison = await multi_ai.compare_models(model_ids, {
            'X_test': X_test_class,
            'y_test': y_test_class
        })
        
        for model_id, metrics in comparison.items():
            print(f"{model_id}:")
            print(f"  Accuracy: {metrics['accuracy']:.3f}")
            print(f"  F1 Score: {metrics['f1_score']:.3f}")
            print(f"  Training time: {metrics['training_time']:.2f}s")
            
    except Exception as e:
        print(f"❌ Model comparison xatosi: {str(e)}")
    
    print("\n✅ Demo yakunlandi!")

if __name__ == "__main__":
    # Demo ishga tushirish
    asyncio.run(demo_multi_model_ai())