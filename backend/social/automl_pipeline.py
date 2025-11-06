"""
AutoML Pipeline - Avtomatik Mashina O'rganish Pipeline
Barcha turdagi ML modellari uchun avtomatik trening va optimizatsiya
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, f1_score, roc_auc_score, classification_report
from sklearn.impute import SimpleImputer
import warnings
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import time

warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """ML model turlari"""
    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    SUPPORT_VECTOR_MACHINE = "svm"
    K_NEIGHBORS = "knn"
    DECISION_TREE = "decision_tree"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"
    GRU = "gru"
    TRANSFORMER = "transformer"
    ENSEMBLE = "ensemble"


class TaskType(Enum):
    """ML vazifa turlari"""
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    PREDICTION = "prediction"
    BUY_SELL_HOLD = "buy_sell_hold"


class OptimizationMethod(Enum):
    """Optimizatsiya metodlari"""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian"
    GENETIC_ALGORITHM = "genetic"
    HYPERBAND = "hyperband"
    AUTO_SKLEARN = "auto_sklearn"
    TPOT = "tpot"


class DataPreprocessor:
    """Ma'lumotlarni oldindan qayta ishlash sinfi"""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.imputer = None
        
    def fit_transform(self, X: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Ma'lumotlarni o'qitish va o'zgartirish"""
        X_processed = X.copy()
        preprocessing_info = {}
        
        # NaN qiymatlarni to'ldirish
        self.imputer = SimpleImputer(strategy='median')
        numeric_cols = X_processed.select_dtypes(include=[np.number]).columns
        X_processed[numeric_cols] = self.imputer.fit_transform(X_processed[numeric_cols])
        preprocessing_info['imputation'] = 'median'
        
        # Kategorik o'zgaruvchilarni kodlash
        categorical_cols = X_processed.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            X_processed[col] = self.label_encoders[col].fit_transform(X_processed[col].astype(str))
        preprocessing_info['categorical_encoding'] = 'label_encoder'
        
        # Ma'lumotlarni normallash
        X_processed[numeric_cols] = self.scaler.fit_transform(X_processed[numeric_cols])
        preprocessing_info['scaling'] = 'standard_scaler'
        
        return X_processed, preprocessing_info
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """O'qitilgan preprocessor bilan yangi ma'lumotlarni o'zgartirish"""
        X_processed = X.copy()
        
        # NaN qiymatlarni to'ldirish
        numeric_cols = X_processed.select_dtypes(include=[np.number]).columns
        X_processed[numeric_cols] = self.imputer.transform(X_processed[numeric_cols])
        
        # Kategorik o'zgaruvchilarni kodlash
        categorical_cols = X_processed.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col in self.label_encoders:
                X_processed[col] = self.label_encoders[col].transform(X_processed[col].astype(str))
        
        # Ma'lumotlarni normallash
        X_processed[numeric_cols] = self.scaler.transform(X_processed[numeric_cols])
        
        return X_processed


class ModelSelector:
    """Model tanlovchi sinfi"""
    
    @staticmethod
    def get_model_class(model_type: ModelType, task_type: TaskType):
        """Model turiga qarab class qaytarish"""
        model_mapping = {
            ModelType.LINEAR_REGRESSION: {
                TaskType.REGRESSION: LinearRegression,
                TaskType.PREDICTION: LinearRegression
            },
            ModelType.LOGISTIC_REGRESSION: {
                TaskType.CLASSIFICATION: LogisticRegression,
                TaskType.SENTIMENT_ANALYSIS: LogisticRegression,
                TaskType.BUY_SELL_HOLD: LogisticRegression
            },
            ModelType.RANDOM_FOREST: {
                TaskType.REGRESSION: RandomForestRegressor,
                TaskType.CLASSIFICATION: RandomForestClassifier,
                TaskType.BUY_SELL_HOLD: RandomForestClassifier,
                TaskType.SENTIMENT_ANALYSIS: RandomForestClassifier
            },
            ModelType.GRADIENT_BOOSTING: {
                TaskType.REGRESSION: GradientBoostingRegressor,
                TaskType.CLASSIFICATION: GradientBoostingClassifier,
                TaskType.BUY_SELL_HOLD: GradientBoostingClassifier,
                TaskType.SENTIMENT_ANALYSIS: GradientBoostingClassifier
            },
            ModelType.SUPPORT_VECTOR_MACHINE: {
                TaskType.REGRESSION: SVR,
                TaskType.CLASSIFICATION: SVC,
                TaskType.BUY_SELL_HOLD: SVC,
                TaskType.SENTIMENT_ANALYSIS: SVC
            },
            ModelType.K_NEIGHBORS: {
                TaskType.REGRESSION: KNeighborsRegressor,
                TaskType.CLASSIFICATION: KNeighborsClassifier,
                TaskType.BUY_SELL_HOLD: KNeighborsClassifier,
                TaskType.SENTIMENT_ANALYSIS: KNeighborsClassifier
            },
            ModelType.DECISION_TREE: {
                TaskType.REGRESSION: DecisionTreeRegressor,
                TaskType.CLASSIFICATION: DecisionTreeClassifier,
                TaskType.BUY_SELL_HOLD: DecisionTreeClassifier,
                TaskType.SENTIMENT_ANALYSIS: DecisionTreeClassifier
            },
            ModelType.NEURAL_NETWORK: {
                TaskType.REGRESSION: MLPRegressor,
                TaskType.CLASSIFICATION: MLPClassifier,
                TaskType.BUY_SELL_HOLD: MLPClassifier,
                TaskType.SENTIMENT_ANALYSIS: MLPClassifier
            }
        }
        
        return model_mapping.get(model_type, {}).get(task_type, LinearRegression)
    
    @staticmethod
    def get_hyperparameter_grid(model_type: ModelType, task_type: TaskType) -> Dict:
        """Model uchun giperparametrlar gridini qaytarish"""
        grid_mapping = {
            ModelType.RANDOM_FOREST: {
                TaskType.REGRESSION: {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20, 30],
                    'min_samples_split': [2, 5, 10]
                },
                TaskType.CLASSIFICATION: {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20, 30],
                    'min_samples_split': [2, 5, 10],
                    'criterion': ['gini', 'entropy']
                }
            },
            ModelType.GRADIENT_BOOSTING: {
                TaskType.REGRESSION: {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                },
                TaskType.CLASSIFICATION: {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7],
                    'criterion': ['friedman_mse', 'squared_error']
                }
            },
            ModelType.SUPPORT_VECTOR_MACHINE: {
                TaskType.REGRESSION: {
                    'C': [0.1, 1, 10],
                    'gamma': ['scale', 'auto', 0.001, 0.01]
                },
                TaskType.CLASSIFICATION: {
                    'C': [0.1, 1, 10],
                    'gamma': ['scale', 'auto', 0.001, 0.01],
                    'kernel': ['rbf', 'linear']
                }
            },
            ModelType.K_NEIGHBORS: {
                TaskType.REGRESSION: {
                    'n_neighbors': [3, 5, 7, 11],
                    'weights': ['uniform', 'distance']
                },
                TaskType.CLASSIFICATION: {
                    'n_neighbors': [3, 5, 7, 11],
                    'weights': ['uniform', 'distance']
                }
            },
            ModelType.DECISION_TREE: {
                TaskType.REGRESSION: {
                    'max_depth': [None, 5, 10, 20],
                    'min_samples_split': [2, 5, 10]
                },
                TaskType.CLASSIFICATION: {
                    'max_depth': [None, 5, 10, 20],
                    'min_samples_split': [2, 5, 10],
                    'criterion': ['gini', 'entropy']
                }
            },
            ModelType.NEURAL_NETWORK: {
                TaskType.REGRESSION: {
                    'hidden_layer_sizes': [(50,), (100,), (50, 50)],
                    'alpha': [0.0001, 0.001, 0.01]
                },
                TaskType.CLASSIFICATION: {
                    'hidden_layer_sizes': [(50,), (100,), (50, 50)],
                    'alpha': [0.0001, 0.001, 0.01]
                }
            }
        }
        
        return grid_mapping.get(model_type, {}).get(task_type, {})


@dataclass
class ModelConfig:
    """Model konfiguratsiyasi"""
    model_type: ModelType
    task_type: TaskType
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    target: str = ""
    sequence_length: int = 60  # Time series uchun
    
    def to_dict(self) -> Dict:
        return {
            'model_type': self.model_type.value,
            'task_type': self.task_type.value,
            'hyperparameters': self.hyperparameters,
            'features': self.features,
            'target': self.target,
            'sequence_length': self.sequence_length,
        }


@dataclass
class TrainingResult:
    """Training natijasi"""
    run_id: str
    model_config: ModelConfig
    train_score: float = 0.0
    val_score: float = 0.0
    test_score: float = 0.0
    training_time: float = 0.0  # soniyalarda
    best_hyperparameters: Dict[str, Any] = field(default_factory=dict)
    feature_importance: Dict[str, float] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    model_path: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'run_id': self.run_id,
            'model_config': self.model_config.to_dict(),
            'train_score': self.train_score,
            'val_score': self.val_score,
            'test_score': self.test_score,
            'training_time': self.training_time,
            'best_hyperparameters': self.best_hyperparameters,
            'feature_importance': self.feature_importance,
            'metrics': self.metrics,
            'model_path': self.model_path,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class DatasetInfo:
    """Dataset ma'lumotlari"""
    name: str
    total_samples: int
    train_samples: int
    val_samples: int
    test_samples: int
    features_count: int
    class_distribution: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'total_samples': self.total_samples,
            'train_samples': self.train_samples,
            'val_samples': self.val_samples,
            'test_samples': self.test_samples,
            'features_count': self.features_count,
            'class_distribution': self.class_distribution,
        }


class AutoMLPipeline:
    """
    AutoML Pipeline - Avtomatik model training,
    hyperparameter optimization va model selection
    """
    
    def __init__(self, random_state: int = 42, n_jobs: int = -1):
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.training_runs: Dict[str, TrainingResult] = {}
        self.datasets: Dict[str, DatasetInfo] = {}
        self.best_models: Dict[str, TrainingResult] = {}  # task_name -> best model
        self.preprocessor = DataPreprocessor()
        self.model_selector = ModelSelector()
        self.trained_models = {}
        self.training_history = []
        self.feature_importance_cache = {}
        self.model_scores = defaultdict(dict)
        
        # Default hyperparameter spaces
        self.hyperparameter_spaces = {
            ModelType.RANDOM_FOREST: {
                'n_estimators': [100, 200, 300, 500],
                'max_depth': [10, 20, 30, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
            },
            ModelType.GRADIENT_BOOSTING: {
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.01, 0.05, 0.1, 0.2],
                'max_depth': [3, 5, 7, 10],
                'subsample': [0.8, 0.9, 1.0],
            },
            ModelType.XGBOOST: {
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.01, 0.05, 0.1],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 0.9, 1.0],
                'colsample_bytree': [0.8, 0.9, 1.0],
            },
            ModelType.LIGHTGBM: {
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.01, 0.05, 0.1],
                'max_depth': [3, 5, 7, -1],
                'num_leaves': [31, 63, 127],
                'subsample': [0.8, 0.9, 1.0],
            },
            ModelType.NEURAL_NETWORK: {
                'hidden_layers': [[64, 32], [128, 64], [256, 128, 64]],
                'learning_rate': [0.001, 0.005, 0.01],
                'batch_size': [32, 64, 128],
                'epochs': [50, 100, 200],
                'dropout': [0.2, 0.3, 0.5],
            },
            ModelType.LSTM: {
                'units': [50, 100, 200],
                'layers': [1, 2, 3],
                'learning_rate': [0.001, 0.005],
                'batch_size': [32, 64],
                'epochs': [50, 100],
                'dropout': [0.2, 0.3],
            },
        }
    
    async def prepare_data(
        self,
        data: np.ndarray,
        labels: np.ndarray,
        dataset_name: str = "default",
        test_size: float = 0.2,
        val_size: float = 0.1
    ) -> Tuple[Any, Any, Any, Any, Any, Any]:
        """
        Datani tayyorlash va bo'lish
        
        Args:
            data: Feature data
            labels: Target labels
            dataset_name: Dataset nomi
            test_size: Test set hajmi
            val_size: Validation set hajmi
            
        Returns:
            (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        try:
            # Train/test split
            X_temp, X_test, y_temp, y_test = train_test_split(
                data, labels, test_size=test_size, random_state=42
            )
            
            # Train/val split
            val_ratio = val_size / (1 - test_size)
            X_train, X_val, y_train, y_val = train_test_split(
                X_temp, y_temp, test_size=val_ratio, random_state=42
            )
            
            # Normalization
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_val = scaler.transform(X_val)
            X_test = scaler.transform(X_test)
            
            # Dataset info saqlash
            dataset_info = DatasetInfo(
                name=dataset_name,
                total_samples=len(data),
                train_samples=len(X_train),
                val_samples=len(X_val),
                test_samples=len(X_test),
                features_count=data.shape[1] if len(data.shape) > 1 else 1,
            )
            
            # Class distribution (classification uchun)
            if len(labels.shape) == 1:
                unique, counts = np.unique(labels, return_counts=True)
                dataset_info.class_distribution = dict(zip(
                    [str(u) for u in unique],
                    [int(c) for c in counts]
                ))
            
            self.datasets[dataset_name] = dataset_info
            
            logger.info(
                f"Data tayyorlandi: {dataset_name} "
                f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}"
            )
            
            return X_train, X_val, X_test, y_train, y_val, y_test
            
        except Exception as e:
            logger.error(f"Datani tayyorlashda xatolik: {e}")
            raise
    
    async def auto_train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        task_type: TaskType = TaskType.CLASSIFICATION,
        model_types: Optional[List[ModelType]] = None,
        optimization_method: OptimizationMethod = OptimizationMethod.RANDOM_SEARCH,
        max_trials: int = 20,
        timeout_seconds: Optional[int] = None
    ) -> List[TrainingResult]:
        """
        Avtomatik model training va selection
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            task_type: Task turi
            model_types: Qaysi model turlarini sinash
            optimization_method: Optimization usuli
            max_trials: Maksimal sinashlar soni
            timeout_seconds: Timeout
            
        Returns:
            Barcha training natijalar ro'yxati
        """
        try:
            if model_types is None:
                # Default model turlari
                if task_type == TaskType.TIME_SERIES:
                    model_types = [ModelType.LSTM, ModelType.GRU]
                else:
                    model_types = [
                        ModelType.RANDOM_FOREST,
                        ModelType.GRADIENT_BOOSTING,
                        ModelType.XGBOOST,
                        ModelType.LIGHTGBM,
                    ]
            
            results = []
            start_time = datetime.now()
            
            # Har bir model turini sinash
            for model_type in model_types:
                # Timeout tekshirish
                if timeout_seconds:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed > timeout_seconds:
                        logger.warning(f"Timeout yetdi: {elapsed}s")
                        break
                
                logger.info(f"Training boshlandi: {model_type.value}")
                
                # Hyperparameter optimization
                result = await self._optimize_hyperparameters(
                    X_train, y_train, X_val, y_val,
                    model_type, task_type,
                    optimization_method, max_trials
                )
                
                if result:
                    results.append(result)
                    self.training_runs[result.run_id] = result
            
            # Eng yaxshi modelni saqlash
            if results:
                best_result = max(results, key=lambda x: x.val_score)
                task_name = f"{task_type.value}_best"
                self.best_models[task_name] = best_result
                
                logger.info(
                    f"AutoML yakunlandi. Eng yaxshi model: {best_result.model_config.model_type.value} "
                    f"Validation score: {best_result.val_score:.4f}"
                )
            
            return results
            
        except Exception as e:
            logger.error(f"AutoML training xatosi: {e}")
            return []
    
    async def _optimize_hyperparameters(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        model_type: ModelType,
        task_type: TaskType,
        method: OptimizationMethod,
        max_trials: int
    ) -> Optional[TrainingResult]:
        """
        Hyperparameter optimization
        
        Args:
            X_train, y_train, X_val, y_val: Data
            model_type: Model turi
            task_type: Task turi
            method: Optimization usuli
            max_trials: Maksimal sinashlar
            
        Returns:
            TrainingResult yoki None
        """
        try:
            run_id = f"run_{datetime.now().timestamp()}"
            
            # Hyperparameter space
            param_space = self.hyperparameter_spaces.get(model_type, {})
            
            if not param_space:
                logger.warning(f"Hyperparameter space topilmadi: {model_type.value}")
                return None
            
            best_score = -float('inf')
            best_params = {}
            start_time = datetime.now()
            
            # Optimization method ga qarab
            if method == OptimizationMethod.RANDOM_SEARCH:
                trials_results = await self._random_search(
                    X_train, y_train, X_val, y_val,
                    model_type, task_type, param_space, max_trials
                )
            elif method == OptimizationMethod.GRID_SEARCH:
                trials_results = await self._grid_search(
                    X_train, y_train, X_val, y_val,
                    model_type, task_type, param_space
                )
            elif method == OptimizationMethod.BAYESIAN:
                trials_results = await self._bayesian_optimization(
                    X_train, y_train, X_val, y_val,
                    model_type, task_type, param_space, max_trials
                )
            else:
                # Default: random search
                trials_results = await self._random_search(
                    X_train, y_train, X_val, y_val,
                    model_type, task_type, param_space, max_trials
                )
            
            # Eng yaxshi natijani topish
            if trials_results:
                best_trial = max(trials_results, key=lambda x: x['val_score'])
                best_score = best_trial['val_score']
                best_params = best_trial['params']
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            # ModelConfig yaratish
            model_config = ModelConfig(
                model_type=model_type,
                task_type=task_type,
                hyperparameters=best_params,
            )
            
            # Training result yaratish
            result = TrainingResult(
                run_id=run_id,
                model_config=model_config,
                train_score=best_trial.get('train_score', 0.0) if trials_results else 0.0,
                val_score=best_score,
                test_score=0.0,  # Test score keyinroq hisoblanadi
                training_time=training_time,
                best_hyperparameters=best_params,
                feature_importance=best_trial.get('feature_importance', {}) if trials_results else {},
                metrics=best_trial.get('metrics', {}) if trials_results else {},
            )
            
            logger.info(
                f"Optimization yakunlandi: {model_type.value} "
                f"Best val score: {best_score:.4f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Hyperparameter optimization xatosi: {e}")
            return None
    
    async def _random_search(
        self,
        X_train, y_train, X_val, y_val,
        model_type: ModelType,
        task_type: TaskType,
        param_space: Dict,
        max_trials: int
    ) -> List[Dict]:
        """Random search optimization"""
        results = []
        
        for i in range(max_trials):
            # Random hyperparameters tanlash
            params = {
                key: np.random.choice(values)
                for key, values in param_space.items()
            }
            
            # Model train qilish
            trial_result = await self._train_single_model(
                X_train, y_train, X_val, y_val,
                model_type, task_type, params
            )
            
            if trial_result:
                results.append(trial_result)
                logger.info(
                    f"Trial {i+1}/{max_trials}: Val score = {trial_result['val_score']:.4f}"
                )
        
        return results
    
    async def _grid_search(
        self,
        X_train, y_train, X_val, y_val,
        model_type: ModelType,
        task_type: TaskType,
        param_space: Dict
    ) -> List[Dict]:
        """Grid search optimization"""
        from itertools import product
        
        # Barcha kombinatsiyalar
        keys = list(param_space.keys())
        values = list(param_space.values())
        
        results = []
        
        for combination in product(*values):
            params = dict(zip(keys, combination))
            
            # Model train qilish
            trial_result = await self._train_single_model(
                X_train, y_train, X_val, y_val,
                model_type, task_type, params
            )
            
            if trial_result:
                results.append(trial_result)
        
        return results
    
    async def _bayesian_optimization(
        self,
        X_train, y_train, X_val, y_val,
        model_type: ModelType,
        task_type: TaskType,
        param_space: Dict,
        max_trials: int
    ) -> List[Dict]:
        """Bayesian optimization (soddalashtirilgan versiya)"""
        # Bu yerda real Bayesian optimization (masalan, Optuna) ishlatilishi kerak
        # Hozircha random search ishlatamiz
        return await self._random_search(
            X_train, y_train, X_val, y_val,
            model_type, task_type, param_space, max_trials
        )
    
    async def _train_single_model(
        self,
        X_train, y_train, X_val, y_val,
        model_type: ModelType,
        task_type: TaskType,
        params: Dict
    ) -> Optional[Dict]:
        """
        Bitta modelni train qilish
        
        Returns:
            Trial natijasi (params, scores, metrics)
        """
        try:
            # Bu yerda real model training bo'lishi kerak
            # Hozircha mock data qaytaramiz
            
            # Sodda simulation
            train_score = np.random.uniform(0.7, 0.95)
            val_score = train_score - np.random.uniform(0.0, 0.1)  # Overfitting simulation
            
            # Feature importance (mock)
            feature_importance = {
                f'feature_{i}': np.random.uniform(0, 1)
                for i in range(min(10, X_train.shape[1] if len(X_train.shape) > 1 else 1))
            }
            
            # Metrics
            if task_type == TaskType.CLASSIFICATION:
                metrics = {
                    'accuracy': val_score,
                    'precision': np.random.uniform(0.6, 0.9),
                    'recall': np.random.uniform(0.6, 0.9),
                    'f1_score': np.random.uniform(0.6, 0.9),
                }
            else:  # Regression
                metrics = {
                    'mse': np.random.uniform(0.01, 0.1),
                    'rmse': np.random.uniform(0.1, 0.3),
                    'mae': np.random.uniform(0.05, 0.2),
                    'r2_score': val_score,
                }
            
            return {
                'params': params,
                'train_score': train_score,
                'val_score': val_score,
                'feature_importance': feature_importance,
                'metrics': metrics,
            }
            
        except Exception as e:
            logger.error(f"Model training xatosi: {e}")
            return None
    
    async def get_best_model(
        self,
        task_name: str = "classification_best"
    ) -> Optional[TrainingResult]:
        """
        Eng yaxshi modelni olish
        
        Args:
            task_name: Task nomi
            
        Returns:
            TrainingResult yoki None
        """
        return self.best_models.get(task_name)
    
    async def get_training_history(
        self,
        limit: int = 100
    ) -> List[TrainingResult]:
        """
        Training tarixini olish
        
        Args:
            limit: Maksimal soni
            
        Returns:
            Training natijalar ro'yxati
        """
        results = list(self.training_runs.values())
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results[:limit]
    
    async def compare_models(
        self,
        run_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Modellarni solishtirish
        
        Args:
            run_ids: Training run IDlar
            
        Returns:
            Solishtirish natijalari
        """
        results = []
        
        for run_id in run_ids:
            if run_id in self.training_runs:
                results.append(self.training_runs[run_id])
        
        if not results:
            return {}
        
        comparison = {
            'models': [r.to_dict() for r in results],
            'best_val_score': max(r.val_score for r in results),
            'best_model': max(results, key=lambda x: x.val_score).run_id,
            'avg_training_time': sum(r.training_time for r in results) / len(results),
        }
        
        return comparison
    
    async def get_feature_importance(
        self,
        run_id: str,
        top_n: int = 10
    ) -> Dict[str, float]:
        """
        Feature importance olish
        
        Args:
            run_id: Training run ID
            top_n: Top N features
            
        Returns:
            Feature importance dict
        """
        if run_id not in self.training_runs:
            return {}
        
        result = self.training_runs[run_id]
        importance = result.feature_importance
        
        # Sort va top N
        sorted_features = sorted(
            importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return dict(sorted_features[:top_n])
    
    async def export_model(
        self,
        run_id: str,
        export_path: str
    ) -> bool:
        """
        Modelni export qilish
        
        Args:
            run_id: Training run ID
            export_path: Export fayl yo'li
            
        Returns:
            bool: Muvaffaqiyatli bo'lsa True
        """
        try:
            if run_id not in self.training_runs:
                logger.error(f"Training run topilmadi: {run_id}")
                return False
            
            result = self.training_runs[run_id]
            
            # Model ma'lumotlarini saqlash
            model_data = result.to_dict()
            
            with open(export_path, 'w') as f:
                json.dump(model_data, f, indent=2)
            
            logger.info(f"Model export qilindi: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Model export qilishda xatolik: {e}")
            return False
    
    async def get_dataset_info(
        self,
        dataset_name: str
    ) -> Optional[DatasetInfo]:
        """
        Dataset ma'lumotlarini olish
        
        Args:
            dataset_name: Dataset nomi
            
        Returns:
            DatasetInfo yoki None
        """
        return self.datasets.get(dataset_name)
    
    async def get_recommendations(
        self,
        task_type: TaskType,
        dataset_size: int,
        features_count: int,
        data_quality: Optional[Dict] = None,
        target_distribution: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Task uchun model recommendations
        
        Args:
            task_type: Task turi
            dataset_size: Dataset hajmi
            features_count: Featurelar soni
            data_quality: Ma'lumotlar sifati
            target_distribution: Target taqsimoti
            
        Returns:
            Recommendations
        """
        recommendations = {
            'recommended_models': [],
            'optimization_method': OptimizationMethod.RANDOM_SEARCH.value,
            'max_trials': 20,
            'notes': [],
            'data_preprocessing': [],
            'model_selection': [],
            'optimization': [],
            'evaluation': []
        }
        
        # Dataset hajmiga qarab
        if dataset_size < 1000:
            recommendations['recommended_models'] = [
                ModelType.RANDOM_FOREST.value,
                ModelType.GRADIENT_BOOSTING.value,
                ModelType.DECISION_TREE.value,
            ]
            recommendations['max_trials'] = 10
            recommendations['notes'].append("Kichik dataset uchun oddiy modellar tavsiya etiladi")
        elif dataset_size < 10000:
            recommendations['recommended_models'] = [
                ModelType.XGBOOST.value,
                ModelType.LIGHTGBM.value,
                ModelType.RANDOM_FOREST.value,
            ]
            recommendations['max_trials'] = 20
        else:
            recommendations['recommended_models'] = [
                ModelType.LIGHTGBM.value,
                ModelType.NEURAL_NETWORK.value,
                ModelType.XGBOOST.value,
            ]
            recommendations['max_trials'] = 30
            recommendations['optimization_method'] = OptimizationMethod.BAYESIAN_OPTIMIZATION.value
        
        # Task type bo'yicha
        if task_type == TaskType.TIME_SERIES:
            recommendations['recommended_models'] = [
                ModelType.LSTM.value,
                ModelType.GRU.value,
                ModelType.TRANSFORMER.value,
            ]
            recommendations['notes'].append("Time series uchun RNN modellar tavsiya etiladi")
        elif task_type == TaskType.BUY_SELL_HOLD:
            recommendations['recommended_models'] = [
                ModelType.RANDOM_FOREST.value,
                ModelType.GRADIENT_BOOSTING.value,
                ModelType.LOGISTIC_REGRESSION.value,
            ]
            recommendations['notes'].append("Financial trading uchun tree-based modellar samarali")
        elif task_type == TaskType.SENTIMENT_ANALYSIS:
            recommendations['recommended_models'] = [
                ModelType.NEURAL_NETWORK.value,
                ModelType.SUPPORT_VECTOR_MACHINE.value,
                ModelType.LOGISTIC_REGRESSION.value,
            ]
        
        # Ma'lumotlar sifati asosida tavsiyalar
        if data_quality:
            if data_quality.get('missing_percentage', 0) > 10:
                recommendations['data_preprocessing'].append(
                    "Ma'lumotlarning 10% dan ko'proq qismi yo'q. Imputation strategiyalarini ko'rib chiqing."
                )
            
            if data_quality.get('outlier_percentage', 0) > 5:
                recommendations['data_preprocessing'].append(
                    "Ko'p outlier qiymatlar mavjud. Outlier detection va treatment qo'llang."
                )
            
            if data_quality.get('feature_correlation', 0) > 0.8:
                recommendations['data_preprocessing'].append(
                    "Yuqori korrelyatsiyali xususiyatlar mavjud. Feature selection qo'llang."
                )
        
        # Target distribution asosida tavsiyalar
        if target_distribution and target_distribution.get('class_imbalance_ratio', 1) > 3:
            recommendations['model_selection'].append(
                "Class imbalance mavjud. SMOTE yoki boshqa resampling texnikalarini sinab ko'ring."
            )
        
        return recommendations

    def auto_train(self, X: pd.DataFrame, y: pd.Series, task_type: TaskType, 
                  optimization_method: OptimizationMethod = OptimizationMethod.RANDOM_SEARCH,
                  test_size: float = 0.2, cv_folds: int = 5,
                  models_to_test: Optional[List[ModelType]] = None) -> Dict[str, Any]:
        """Avtomatik model treningi"""
        
        logger.info(f"AutoML pipeline boshlanmoqda - {task_type.value}")
        
        # Ma'lumotlarni bo'lish
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state,
            stratify=y if task_type == TaskType.CLASSIFICATION else None
        )
        
        # Ma'lumotlarni oldindan qayta ishlash
        X_train_processed, preprocessing_info = self.preprocessor.fit_transform(X_train)
        X_test_processed = self.preprocessor.transform(X_test)
        
        logger.info(f"Ma'lumotlar oldindan qayta ishlash: {preprocessing_info}")
        
        # Test qilish kerak bo'lgan modellarni aniqlash
        if models_to_test is None:
            models_to_test = [
                ModelType.RANDOM_FOREST,
                ModelType.GRADIENT_BOOSTING,
                ModelType.LOGISTIC_REGRESSION,
                ModelType.SUPPORT_VECTOR_MACHINE,
                ModelType.K_NEIGHBORS,
                ModelType.DECISION_TREE
            ]
        
        best_model = None
        best_score = float('-inf')
        best_model_name = ""
        model_results = {}
        
        for model_type in models_to_test:
            try:
                logger.info(f"Testing {model_type.value}")
                
                # Model yaratish
                model_class = self.model_selector.get_model_class(model_type, task_type)
                
                # Random state parametrsini faqat support qiladigan modellar uchun qo'llash
                if model_type in [ModelType.RANDOM_FOREST, ModelType.GRADIENT_BOOSTING, 
                                ModelType.SUPPORT_VECTOR_MACHINE, ModelType.DECISION_TREE, 
                                ModelType.NEURAL_NETWORK]:
                    model = model_class(random_state=self.random_state)
                else:
                    model = model_class()
                
                # Giperparametrlar optimizatsiyasi
                if optimization_method == OptimizationMethod.GRID_SEARCH:
                    param_grid = self.model_selector.get_hyperparameter_grid(model_type, task_type)
                    if param_grid:
                        scoring = 'accuracy' if task_type in [TaskType.CLASSIFICATION, TaskType.BUY_SELL_HOLD, TaskType.SENTIMENT_ANALYSIS] else 'neg_mean_squared_error'
                        search = GridSearchCV(
                            model, param_grid, cv=cv_folds, 
                            scoring=scoring,
                            n_jobs=self.n_jobs
                        )
                        search.fit(X_train_processed, y_train)
                        best_model_ = search.best_estimator_
                    else:
                        best_model_ = model
                        best_model_.fit(X_train_processed, y_train)
                
                elif optimization_method == OptimizationMethod.RANDOM_SEARCH:
                    param_grid = self.model_selector.get_hyperparameter_grid(model_type, task_type)
                    if param_grid:
                        scoring = 'accuracy' if task_type in [TaskType.CLASSIFICATION, TaskType.BUY_SELL_HOLD, TaskType.SENTIMENT_ANALYSIS] else 'neg_mean_squared_error'
                        search = RandomizedSearchCV(
                            model, param_grid, n_iter=20, cv=cv_folds,
                            scoring=scoring,
                            random_state=self.random_state,
                            n_jobs=self.n_jobs
                        )
                        search.fit(X_train_processed, y_train)
                        best_model_ = search.best_estimator_
                    else:
                        best_model_ = model
                        best_model_.fit(X_train_processed, y_train)
                
                else:
                    # Oddiy fit (optimizatsiya yo'q)
                    best_model_ = model
                    best_model_.fit(X_train_processed, y_train)
                
                # Baholash
                y_pred = best_model_.predict(X_test_processed)
                
                if task_type in [TaskType.CLASSIFICATION, TaskType.BUY_SELL_HOLD, TaskType.SENTIMENT_ANALYSIS]:
                    score = accuracy_score(y_test, y_pred)
                    f1 = f1_score(y_test, y_pred, average='weighted')
                    
                    # AUC faqat binary classification uchun
                    auc = None
                    if len(np.unique(y_test)) == 2:
                        try:
                            auc = roc_auc_score(y_test, best_model_.predict_proba(X_test_processed)[:, 1])
                        except:
                            pass
                    
                    model_results[model_type.value] = {
                        'accuracy': score,
                        'f1_score': f1,
                        'auc_score': auc,
                        'model': best_model_
                    }
                    
                    current_score = score  # accuracy as primary metric for classification
                    
                else:
                    mse = mean_squared_error(y_test, y_pred)
                    model_results[model_type.value] = {
                        'mse': mse,
                        'rmse': np.sqrt(mse),
                        'model': best_model_
                    }
                    
                    current_score = -mse  # negative because we want higher scores
                
                # Best model saqlash
                if current_score > best_score:
                    best_score = current_score
                    best_model = best_model_
                    best_model_name = model_type.value
                
                logger.info(f"{model_type.value} - Score: {current_score:.4f}")
                
            except Exception as e:
                logger.error(f"{model_type.value} modelida xato: {str(e)}")
                continue
        
        # Natijalarni saqlash
        self.trained_models[best_model_name] = best_model
        self.model_scores[best_model_name] = model_results[best_model_name]
        
        # Training history yangilash
        training_record = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task_type.value,
            'optimization_method': optimization_method.value,
            'best_model': best_model_name,
            'best_score': best_score,
            'all_results': model_results,
            'preprocessing_info': preprocessing_info
        }
        self.training_history.append(training_record)
        
        logger.info(f"Eng yaxshi model: {best_model_name}, Baho: {best_score:.4f}")
        
        return {
            'best_model': best_model,
            'best_model_name': best_model_name,
            'best_score': best_score,
            'all_results': model_results,
            'preprocessing_info': preprocessing_info,
            'model_comparison': pd.DataFrame({k: [v.get('accuracy', -v.get('mse', 0))] 
                                           for k, v in model_results.items()}).T
        }

    def get_best_model(self, model_name: Optional[str] = None) -> Optional[Any]:
        """Eng yaxshi modelni olish"""
        if model_name:
            return self.trained_models.get(model_name)
        
        if not self.training_history:
            return None
        
        # So'nggi trening natijasidan eng yaxshi modelni qaytarish
        latest_training = self.training_history[-1]
        best_model_name = latest_training['best_model']
        return self.trained_models.get(best_model_name)

    def get_training_history(self) -> List[Dict]:
        """Trening tarixini olish"""
        return self.training_history

    def get_feature_importance(self, model_name: Optional[str] = None, 
                              X_sample: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """Xususiyatlar muhimligini hisoblash"""
        
        if model_name is None:
            latest_training = self.training_history[-1]
            model_name = latest_training.get('best_model')
        
        model = self.trained_models.get(model_name)
        if model is None:
            raise ValueError(f"Model '{model_name}' topilmadi")
        
        # Feature importance olish
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importance = np.abs(model.coef_).flatten()
        else:
            # Fallback - permutation importance
            if X_sample is not None:
                importance = self._calculate_permutation_importance(model, X_sample)
            else:
                raise ValueError("Model feature_importances_ yoki coef_ atributiga ega emas")
        
        # Xususiyat nomlarini olish
        if X_sample is not None:
            feature_names = X_sample.columns.tolist()
        else:
            feature_names = [f"feature_{i}" for i in range(len(importance))]
        
        # Dictionary qilish
        feature_importance = dict(zip(feature_names, importance))
        
        # Cache-lash
        self.feature_importance_cache[model_name] = feature_importance
        
        return feature_importance

    def _calculate_permutation_importance(self, model, X: pd.DataFrame, n_repeats: int = 5) -> np.ndarray:
        """Permutation importance hisoblash (fallback)"""
        from sklearn.inspection import permutation_importance
        
        # Dummy calculation - actual permutation importance requires true predictions
        # This is a simplified version
        baseline_score = model.score(X, np.random.choice([0, 1], size=len(X)))
        
        importance = []
        for col in X.columns:
            X_permuted = X.copy()
            X_permuted[col] = np.random.permutation(X_permuted[col])
            permuted_score = model.score(X_permuted, np.random.choice([0, 1], size=len(X)))
            importance.append(abs(baseline_score - permuted_score))
        
        return np.array(importance)

    def get_recommendations(self, data_quality: Optional[Dict] = None,
                           target_distribution: Optional[Dict] = None) -> Dict[str, Any]:
        """Ma'lumotlar va model haqida tavsiyalar"""
        
        recommendations = {
            'data_preprocessing': [],
            'model_selection': [],
            'optimization': [],
            'evaluation': [],
            'improvement_suggestions': []
        }
        
        # Ma'lumotlar sifati asosida tavsiyalar
        if data_quality:
            if data_quality.get('missing_percentage', 0) > 10:
                recommendations['data_preprocessing'].append(
                    "Ma'lumotlarning 10% dan ko'proq qismi yo'q. Imputation strategiyalarini ko'rib chiqing."
                )
            
            if data_quality.get('outlier_percentage', 0) > 5:
                recommendations['data_preprocessing'].append(
                    "Ko'p outlier qiymatlar mavjud. Outlier detection va treatment qo'llang."
                )
            
            if data_quality.get('feature_correlation', 0) > 0.8:
                recommendations['data_preprocessing'].append(
                    "Yuqori korrelyatsiyali xususiyatlar mavjud. Feature selection qo'llang."
                )
        
        # Target distribution asosida tavsiyalar
        if target_distribution and target_distribution.get('class_imbalance_ratio', 1) > 3:
            recommendations['model_selection'].append(
                "Class imbalance mavjud. SMOTE yoki boshqa resampling texnikalarini sinab ko'ring."
            )
        
        # Model selection tavsiyalari
        if not self.training_history:
            recommendations['model_selection'].append(
                "Hali model o'qitilmagan. Avval basic model bilan boshlang."
            )
        else:
            latest_training = self.training_history[-1]
            best_model = latest_training['best_model']
            
            if best_model == 'random_forest':
                recommendations['model_selection'].append(
                    "Random Forest yaxshi ishlayapti. Gradient Boosting ham sinab ko'ring."
                )
            elif best_model == 'gradient_boosting':
                recommendations['model_selection'].append(
                    "Gradient Boosting samarali. XGBoost yoki LightGBM ham sinab ko'ring."
                )
        
        # Optimizatsiya tavsiyalari
        if len(self.training_history) < 3:
            recommendations['optimization'].append(
                "Ko'proq optimization metodlarini sinab ko'ring (Grid Search, Bayesian Optimization)."
            )
        
        # Evaluation tavsiyalar
        if target_distribution and target_distribution.get('task_type') == 'classification':
            recommendations['evaluation'].append(
                "F1-score, Precision, Recall metrikalarini ham kuzating."
            )
        elif target_distribution and target_distribution.get('task_type') == 'regression':
            recommendations['evaluation'].append(
                "MAE, MAPE, R-squared metrikalarini ham hisoblang."
            )
        
        # Improvement suggestions
        recommendations['improvement_suggestions'].extend([
            "Cross-validation natijalarini baseline model bilan taqqoshing",
            "Feature engineering (polynomial features, interactions) sinab ko'ring",
            "Ensemble metodlar (Voting, Stacking) qo'llang",
            "Hyperparameter tuning uchun Bayesian optimization ishlatish",
            "Ma'lumotlarni ko'proq to'plash yoki data augmentation qo'llash"
        ])
        
        return recommendations

    def predict(self, X: pd.DataFrame, model_name: Optional[str] = None) -> np.ndarray:
        """Bashorat qilish"""
        model = self.get_best_model(model_name)
        if model is None:
            raise ValueError("Model topilmadi. Avval auto_train chaqiring.")
        
        X_processed = self.preprocessor.transform(X)
        return model.predict(X_processed)

    def predict_proba(self, X: pd.DataFrame, model_name: Optional[str] = None) -> np.ndarray:
        """Ehtimollik bilan bashorat qilish (classification uchun)"""
        model = self.get_best_model(model_name)
        if model is None:
            raise ValueError("Model topilmadi. Avval auto_train chaqiring.")
        
        if not hasattr(model, 'predict_proba'):
            raise ValueError("Bu model ehtimollik qaytarmaydi")
        
        X_processed = self.preprocessor.transform(X)
        return model.predict_proba(X_processed)

    def save_model(self, filepath: str, model_name: Optional[str] = None):
        """Modelni faylga saqlash"""
        model = self.get_best_model(model_name)
        if model is None:
            raise ValueError("Saqlanadigan model topilmadi")
        
        model_data = {
            'model': model,
            'preprocessor': self.preprocessor,
            'training_info': self.training_history[-1] if self.training_history else None
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model {filepath} ga saqlandi")

    def load_model(self, filepath: str):
        """Modelni fayldan yuklash"""
        model_data = joblib.load(filepath)
        
        self.trained_models = {'loaded_model': model_data['model']}
        self.preprocessor = model_data['preprocessor']
        
        if model_data.get('training_info'):
            self.training_history.append(model_data['training_info'])
        
        logger.info(f"Model {filepath} dan yuklandi")

    def compare_models(self) -> pd.DataFrame:
        """Barcha modellarni taqqoslash"""
        if not self.model_scores:
            return pd.DataFrame()
        
        comparison_data = {}
        for model_name, scores in self.model_scores.items():
            comparison_data[model_name] = {}
            
            # Barcha metrikalarni olish
            for metric, value in scores.items():
                if metric != 'model':
                    comparison_data[model_name][metric] = value
        
        return pd.DataFrame(comparison_data).T

    def generate_report(self, output_path: str = None) -> str:
        """Trening hisobotini generatsiya qilish"""
        
        if not self.training_history:
            return "Hali hech qanday trening amalga oshirilmagan"
        
        report = f"""
# AutoML Pipeline Training Report

## So'nggi Trening Natijalari
- Sana: {self.training_history[-1]['timestamp']}
- Vazifa turi: {self.training_history[-1]['task_type']}
- Optimizatsiya metod: {self.training_history[-1]['optimization_method']}
- Eng yaxshi model: {self.training_history[-1]['best_model']}
- Eng yaxshi baho: {self.training_history[-1]['best_score']:.4f}

## Model Performance
{self.compare_models().to_string()}

## Feature Importance
"""
        
        # Feature importance qo'shish
        try:
            feature_importance = self.get_feature_importance()
            if feature_importance:
                report += "\nTop 10 muhim xususiyatlar:\n"
                sorted_features = sorted(feature_importance.items(), 
                                       key=lambda x: x[1], reverse=True)[:10]
                for feature, importance in sorted_features:
                    report += f"- {feature}: {importance:.4f}\n"
        except:
            report += "\nFeature importance hisoblanmadi\n"
        
        # Tavsiyalar qo'shish
        recommendations = self.get_recommendations()
        report += "\n## Tavsiyalar\n"
        for category, suggestions in recommendations.items():
            if suggestions:
                report += f"\n### {category.replace('_', ' ').title()}\n"
                for suggestion in suggestions:
                    report += f"- {suggestion}\n"
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Hisobot {output_path} ga saqlandi")
        
        return report


# Utility functions
def create_sample_data(n_samples: int = 1000, task_type: TaskType = TaskType.REGRESSION) -> Tuple[pd.DataFrame, pd.Series]:
    """Namuna ma'lumotlar yaratish"""
    np.random.seed(42)
    
    # Xususiyatlar yaratish
    n_features = 10
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    
    # Target yaratish
    if task_type == TaskType.REGRESSION:
        y = (X.iloc[:, 0] * 2 + X.iloc[:, 1] * 3 + 
             np.random.randn(n_samples) * 0.5 + 10)
    elif task_type == TaskType.BUY_SELL_HOLD:
        y = pd.Series(np.random.choice([0, 1, 2], size=n_samples, p=[0.3, 0.4, 0.3]))  # Buy, Hold, Sell
    else:  # classification
        y = pd.Series(np.random.choice([0, 1], size=n_samples))
        y = (X.iloc[:, 0] + X.iloc[:, 1] > 0).astype(int)
    
    return X, y


def evaluate_data_quality(X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
    """Ma'lumotlar sifati tahlili"""
    quality_report = {}
    
    # Missing values
    missing_percentage = (X.isnull().sum() / len(X) * 100).mean()
    quality_report['missing_percentage'] = missing_percentage
    
    # Outliers (simple IQR method)
    outlier_counts = 0
    for col in X.select_dtypes(include=[np.number]).columns:
        Q1 = X[col].quantile(0.25)
        Q3 = X[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((X[col] < (Q1 - 1.5 * IQR)) | (X[col] > (Q3 + 1.5 * IQR))).sum()
        outlier_counts += outliers
    
    quality_report['outlier_percentage'] = (outlier_counts / (len(X) * len(X.select_dtypes(include=[np.number]).columns))) * 100
    
    # Feature correlation
    corr_matrix = X.corr().abs()
    upper_triangle = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    high_correlation = (upper_triangle > 0.8).any().sum()
    quality_report['feature_correlation'] = high_correlation / len(X.columns)
    
    # Target distribution for classification
    if len(np.unique(y)) == 2:
        class_counts = y.value_counts()
        majority_class = class_counts.max()
        minority_class = class_counts.min()
        quality_report['class_imbalance_ratio'] = majority_class / minority_class
        quality_report['task_type'] = 'classification'
    elif len(np.unique(y)) == 3:
        class_counts = y.value_counts()
        majority_class = class_counts.max()
        minority_class = class_counts.min()
        quality_report['class_imbalance_ratio'] = majority_class / minority_class
        quality_report['task_type'] = 'multiclass_classification'
    else:
        quality_report['task_type'] = 'regression'
    
    return quality_report


# Misol foydalanish
if __name__ == "__main__":
    # AutoML Pipeline test qilish
    print("AutoML Pipeline Test Qilish...")
    
    # Namuna ma'lumotlar
    X, y = create_sample_data(n_samples=1000, task_type=TaskType.BUY_SELL_HOLD)
    
    # Pipeline yaratish
    automl = AutoMLPipeline(random_state=42)
    
    # Ma'lumotlar sifati tahlili
    data_quality = evaluate_data_quality(X, y)
    print(f"Ma'lumotlar sifati: {data_quality}")
    
    # Auto training
    results = automl.auto_train(
        X=X, 
        y=y, 
        task_type=TaskType.BUY_SELL_HOLD,
        optimization_method=OptimizationMethod.RANDOM_SEARCH
    )
    
    print(f"Eng yaxshi model: {results['best_model_name']}")
    print(f"Eng yaxshi baho: {results['best_score']:.4f}")
    
    # Model comparison
    comparison = automl.compare_models()
    print("\nModel taqqoslash:")
    print(comparison)
    
    # Feature importance
    try:
        feature_importance = automl.get_feature_importance()
        print("\nTop 5 muhim xususiyatlar:")
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
        for feature, importance in sorted_features:
            print(f"- {feature}: {importance:.4f}")
    except Exception as e:
        print(f"Feature importance xatosi: {e}")
    
    # Tavsiyalar
    recommendations = automl.get_recommendations(data_quality)
    print("\nTavsiyalar:")
    for category, suggestions in recommendations.items():
        if suggestions:
            print(f"\n{category}:")
            for suggestion in suggestions:
                print(f"- {suggestion}")
    
    # Hisobot generatsiya qilish
    report = automl.generate_report()
    print("\n" + "="*50)
    print("TRENING HISOBOTI")
    print("="*50)
    print(report)
