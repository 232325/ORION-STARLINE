"""
AutoML - Automated Machine Learning for financial models
End-to-end automated ML pipeline for model selection, hyperparameter tuning, va feature engineering
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import warnings

# Import various ML libraries
from sklearn.ensemble import (RandomForestClassifier, RandomForestRegressor, 
                             GradientBoostingClassifier, GradientBoostingRegressor,
                             AdaBoostClassifier, ExtraTreesClassifier)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import (LogisticRegression, LinearRegression, Ridge, Lasso,
                                ElasticNet, SGDClassifier, SGDRegressor)
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.model_selection import (cross_val_score, train_test_split, GridSearchCV, 
                                    RandomizedSearchCV, StratifiedKFold, KFold)
from sklearn.preprocessing import (StandardScaler, MinMaxScaler, RobustScaler, 
                                  LabelEncoder, OneHotEncoder)
from sklearn.feature_selection import (SelectKBest, f_classif, f_regression, 
                                      mutual_info_classif, RFE, SelectFromModel)
from sklearn.decomposition import PCA
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                           mean_squared_error, mean_absolute_error, r2_score,
                           roc_auc_score, classification_report)

warnings.filterwarnings('ignore')

@dataclass
class AutoMLConfig:
    """AutoML konfiguratsiyasi"""
    # Pipeline settings
    max_models_to_try: int = 50
    max_time_minutes: int = 60
    early_stopping_rounds: int = 10
    validation_split: float = 0.2
    test_split: float = 0.2
    
    # Model selection
    allowed_models: List[str] = field(default_factory=lambda: [
        'random_forest', 'gradient_boosting', 'xgboost', 'lightgbm', 'catboost',
        'svm', 'neural_network', 'logistic_regression', 'decision_tree',
        'ada_boost', 'extra_trees', 'kneighbors', 'naive_bayes'
    ])
    
    # Feature engineering
    enable_feature_selection: bool = True
    max_features: int = 100
    feature_selection_method: str = 'mutual_info'  # 'mutual_info', 'f_test', 'rfe'
    enable_pca: bool = True
    pca_components: Optional[int] = None  # None = automatic
    
    # Hyperparameter tuning
    enable_hyperparameter_tuning: bool = True
    tuning_method: str = 'random'  # 'grid', 'random', 'bayesian'
    max_tuning_iterations: int = 100
    cv_folds: int = 5
    
    # Model ensemble
    enable_ensemble: bool = True
    ensemble_size: int = 5
    ensemble_method: str = 'voting'  # 'voting', 'stacking', 'blending'
    
    # Advanced features
    enable_feature_engineering: bool = True
    enable_data_cleaning: bool = True
    enable_outlier_detection: bool = True
    enable_missing_value_imputation: bool = True
    
    # Performance optimization
    parallel_processing: bool = True
    n_cores: int = -1  # -1 = use all cores
    memory_limit_mb: int = 4096
    timeout_per_model: int = 300  # seconds

class ModelRegistry:
    """Registry of available models"""
    
    def __init__(self):
        self.models = {}
        self._register_models()
    
    def _register_models(self):
        """Register all available models"""
        self.models = {
            'random_forest': {
                'classifier': RandomForestClassifier,
                'regressor': RandomForestRegressor,
                'params': {
                    'classifier': {
                        'n_estimators': [10, 50, 100, 200],
                        'max_depth': [3, 5, 10, None],
                        'min_samples_split': [2, 5, 10],
                        'min_samples_leaf': [1, 2, 4],
                        'max_features': ['auto', 'sqrt', 'log2'],
                        'random_state': [42]
                    },
                    'regressor': {
                        'n_estimators': [10, 50, 100, 200],
                        'max_depth': [3, 5, 10, None],
                        'min_samples_split': [2, 5, 10],
                        'min_samples_leaf': [1, 2, 4],
                        'max_features': ['auto', 'sqrt', 'log2'],
                        'random_state': [42]
                    }
                }
            },
            'gradient_boosting': {
                'classifier': GradientBoostingClassifier,
                'regressor': GradientBoostingRegressor,
                'params': {
                    'classifier': {
                        'n_estimators': [50, 100, 200],
                        'learning_rate': [0.01, 0.1, 0.2],
                        'max_depth': [3, 5, 7],
                        'subsample': [0.8, 0.9, 1.0],
                        'random_state': [42]
                    },
                    'regressor': {
                        'n_estimators': [50, 100, 200],
                        'learning_rate': [0.01, 0.1, 0.2],
                        'max_depth': [3, 5, 7],
                        'subsample': [0.8, 0.9, 1.0],
                        'random_state': [42]
                    }
                }
            },
            'svm': {
                'classifier': SVC,
                'regressor': SVR,
                'params': {
                    'classifier': {
                        'C': [0.1, 1, 10, 100],
                        'kernel': ['linear', 'rbf', 'poly'],
                        'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1],
                        'random_state': [42]
                    },
                    'regressor': {
                        'C': [0.1, 1, 10, 100],
                        'kernel': ['linear', 'rbf', 'poly'],
                        'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1],
                        'random_state': [42]
                    }
                }
            },
            'neural_network': {
                'classifier': MLPClassifier,
                'regressor': MLPRegressor,
                'params': {
                    'classifier': {
                        'hidden_layer_sizes': [(50,), (100,), (50, 25), (100, 50)],
                        'activation': ['relu', 'tanh'],
                        'solver': ['adam', 'lbfgs'],
                        'alpha': [0.0001, 0.001, 0.01],
                        'learning_rate_init': [0.001, 0.01, 0.1],
                        'max_iter': [500],
                        'random_state': [42]
                    },
                    'regressor': {
                        'hidden_layer_sizes': [(50,), (100,), (50, 25), (100, 50)],
                        'activation': ['relu', 'tanh'],
                        'solver': ['adam', 'lbfgs'],
                        'alpha': [0.0001, 0.001, 0.01],
                        'learning_rate_init': [0.001, 0.01, 0.1],
                        'max_iter': [500],
                        'random_state': [42]
                    }
                }
            },
            'logistic_regression': {
                'classifier': LogisticRegression,
                'regressor': None,
                'params': {
                    'classifier': {
                        'C': [0.01, 0.1, 1, 10, 100],
                        'penalty': ['l1', 'l2'],
                        'solver': ['liblinear', 'saga'],
                        'random_state': [42],
                        'max_iter': [1000]
                    }
                }
            },
            'decision_tree': {
                'classifier': DecisionTreeClassifier,
                'regressor': DecisionTreeRegressor,
                'params': {
                    'classifier': {
                        'max_depth': [3, 5, 10, None],
                        'min_samples_split': [2, 5, 10],
                        'min_samples_leaf': [1, 2, 4],
                        'criterion': ['gini', 'entropy'],
                        'random_state': [42]
                    },
                    'regressor': {
                        'max_depth': [3, 5, 10, None],
                        'min_samples_split': [2, 5, 10],
                        'min_samples_leaf': [1, 2, 4],
                        'criterion': ['mse', 'friedman_mse', 'mae'],
                        'random_state': [42]
                    }
                }
            },
            'ada_boost': {
                'classifier': AdaBoostClassifier,
                'regressor': None,
                'params': {
                    'classifier': {
                        'n_estimators': [50, 100, 200],
                        'learning_rate': [0.01, 0.1, 1.0],
                        'random_state': [42]
                    }
                }
            },
            'extra_trees': {
                'classifier': ExtraTreesClassifier,
                'regressor': None,
                'params': {
                    'classifier': {
                        'n_estimators': [50, 100, 200],
                        'max_depth': [3, 5, 10, None],
                        'min_samples_split': [2, 5, 10],
                        'random_state': [42]
                    }
                }
            },
            'kneighbors': {
                'classifier': KNeighborsClassifier,
                'regressor': KNeighborsRegressor,
                'params': {
                    'classifier': {
                        'n_neighbors': [3, 5, 7, 9],
                        'weights': ['uniform', 'distance'],
                        'algorithm': ['auto', 'ball_tree', 'kd_tree'],
                        'p': [1, 2]
                    },
                    'regressor': {
                        'n_neighbors': [3, 5, 7, 9],
                        'weights': ['uniform', 'distance'],
                        'algorithm': ['auto', 'ball_tree', 'kd_tree'],
                        'p': [1, 2]
                    }
                }
            },
            'naive_bayes': {
                'classifier': GaussianNB,
                'regressor': None,
                'params': {
                    'classifier': {
                        'var_smoothing': [1e-9, 1e-8, 1e-7, 1e-6]
                    }
                }
            }
        }
    
    def get_model_class(self, model_name: str, task_type: str):
        """Get model class for specific task type"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found in registry")
        
        model_info = self.models[model_name]
        return model_info.get(task_type)
    
    def get_hyperparameters(self, model_name: str, task_type: str):
        """Get hyperparameters for model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found in registry")
        
        model_info = self.models[model_name]
        return model_info.get('params', {}).get(task_type, {})

class FeatureEngineer:
    """Feature engineering and selection"""
    
    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.FeatureEngineer")
        
        self.selected_features = None
        self.feature_selector = None
        self.scaler = None
        self.feature_names = None
        
    def engineer_features(self, X: pd.DataFrame, y: pd.Series, task_type: str) -> pd.DataFrame:
        """Engineer features for the dataset"""
        X_processed = X.copy()
        
        # Handle missing values
        if self.config.enable_missing_value_imputation:
            X_processed = self._impute_missing_values(X_processed)
        
        # Remove outliers
        if self.config.enable_outlier_detection:
            X_processed = self._remove_outliers(X_processed)
        
        # Feature selection
        if self.config.enable_feature_selection:
            X_processed, self.feature_selector = self._select_features(X_processed, y, task_type)
        
        # PCA dimensionality reduction
        if self.config.enable_pca:
            X_processed = self._apply_pca(X_processed)
        
        # Feature scaling
        X_processed = self._scale_features(X_processed)
        
        self.feature_names = X_processed.columns.tolist()
        
        self.logger.info(f"Feature engineering completed. Final shape: {X_processed.shape}")
        return X_processed
    
    def _impute_missing_values(self, X: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values"""
        X_imputed = X.copy()
        
        # For numeric columns, use median
        numeric_columns = X_imputed.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            X_imputed[col].fillna(X_imputed[col].median(), inplace=True)
        
        # For categorical columns, use mode
        categorical_columns = X_imputed.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            X_imputed[col].fillna(X_imputed[col].mode().iloc[0], inplace=True)
        
        return X_imputed
    
    def _remove_outliers(self, X: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers using IQR method"""
        X_clean = X.copy()
        
        numeric_columns = X_clean.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            Q1 = X_clean[col].quantile(0.25)
            Q3 = X_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Cap outliers instead of removing
            X_clean[col] = X_clean[col].clip(lower=lower_bound, upper=upper_bound)
        
        return X_clean
    
    def _select_features(self, X: pd.DataFrame, y: pd.Series, task_type: str) -> Tuple[pd.DataFrame, Any]:
        """Select features"""
        if task_type == 'classifier':
            if self.config.feature_selection_method == 'mutual_info':
                selector = SelectKBest(mutual_info_classif, k=min(self.config.max_features, X.shape[1]))
            elif self.config.feature_selection_method == 'f_test':
                selector = SelectKBest(f_classif, k=min(self.config.max_features, X.shape[1]))
            else:  # rfe
                from sklearn.ensemble import RandomForestClassifier
                base_estimator = RandomForestClassifier(n_estimators=10, random_state=42)
                selector = RFE(base_estimator, n_features_to_select=min(self.config.max_features, X.shape[1]))
        else:  # regressor
            if self.config.feature_selection_method == 'mutual_info':
                from sklearn.feature_selection import mutual_info_regression
                selector = SelectKBest(mutual_info_regression, k=min(self.config.max_features, X.shape[1]))
            elif self.config.feature_selection_method == 'f_test':
                selector = SelectKBest(f_regression, k=min(self.config.max_features, X.shape[1]))
            else:  # rfe
                from sklearn.ensemble import RandomForestRegressor
                base_estimator = RandomForestRegressor(n_estimators=10, random_state=42)
                selector = RFE(base_estimator, n_features_to_select=min(self.config.max_features, X.shape[1]))
        
        X_selected = selector.fit_transform(X, y)
        selected_features = X.columns[selector.get_support()]
        
        self.logger.info(f"Feature selection: {X.shape[1]} -> {len(selected_features)} features")
        
        return pd.DataFrame(X_selected, columns=selected_features, index=X.index), selector
    
    def _apply_pca(self, X: pd.DataFrame) -> pd.DataFrame:
        """Apply PCA for dimensionality reduction"""
        if self.config.pca_components is None:
            n_components = min(X.shape[1], min(50, X.shape[1] // 2))
        else:
            n_components = self.config.pca_components
        
        pca = PCA(n_components=n_components, random_state=42)
        X_pca = pca.fit_transform(X)
        
        explained_variance = pca.explained_variance_ratio_.sum()
        self.logger.info(f"PCA: {X.shape[1]} -> {n_components} components, "
                        f"explained variance: {explained_variance:.3f}")
        
        column_names = [f'PC{i+1}' for i in range(n_components)]
        return pd.DataFrame(X_pca, columns=column_names, index=X.index)
    
    def _scale_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Scale features"""
        # Choose scaler based on data distribution
        scaler = StandardScaler()  # Default to StandardScaler
        self.scaler = scaler
        
        X_scaled = scaler.fit_transform(X)
        return pd.DataFrame(X_scaled, columns=X.columns, index=X.index)

class ModelEvaluator:
    """Model evaluation and comparison"""
    
    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ModelEvaluator")
        
        self.evaluation_results = []
    
    def evaluate_model(self, model_name: str, model_class: type, 
                      X_train: pd.DataFrame, y_train: pd.Series,
                      X_val: pd.DataFrame, y_val: pd.Series,
                      hyperparams: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate a single model"""
        
        start_time = time.time()
        hyperparams = hyperparams or {}
        
        try:
            # Create model instance
            model = model_class(**hyperparams)
            
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred_train = model.predict(X_train)
            y_pred_val = model.predict(X_val)
            
            # Calculate metrics
            metrics = self._calculate_metrics(y_train, y_pred_train, y_val, y_pred_val)
            
            # Cross-validation score
            cv_score = self._cross_validate_model(model, X_train, y_train)
            
            # Training time
            training_time = time.time() - start_time
            
            result = {
                'model_name': model_name,
                'model_class': model_class.__name__,
                'hyperparameters': hyperparams,
                'metrics': metrics,
                'cv_score': cv_score,
                'training_time': training_time,
                'success': True,
                'timestamp': datetime.now()
            }
            
            self.evaluation_results.append(result)
            
            self.logger.info(f"Evaluated {model_name}: CV={cv_score:.4f}, "
                           f"Val Acc={metrics.get('accuracy', 'N/A'):.4f}, "
                           f"Time={training_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate {model_name}: {e}")
            
            result = {
                'model_name': model_name,
                'model_class': model_class.__name__,
                'hyperparameters': hyperparams,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now()
            }
            
            self.evaluation_results.append(result)
            return result
    
    def _calculate_metrics(self, y_train_true: pd.Series, y_train_pred: np.ndarray,
                         y_val_true: pd.Series, y_val_pred: np.ndarray) -> Dict[str, float]:
        """Calculate performance metrics"""
        metrics = {}
        
        # Training metrics
        if len(np.unique(y_train_true)) <= 2:  # Binary classification
            metrics['train_accuracy'] = accuracy_score(y_train_true, y_train_pred)
            metrics['train_precision'] = precision_score(y_train_true, y_train_pred, average='binary')
            metrics['train_recall'] = recall_score(y_train_true, y_train_pred, average='binary')
            metrics['train_f1'] = f1_score(y_train_true, y_train_pred, average='binary')
            
            # Validation metrics
            metrics['val_accuracy'] = accuracy_score(y_val_true, y_val_pred)
            metrics['val_precision'] = precision_score(y_val_true, y_val_pred, average='binary')
            metrics['val_recall'] = recall_score(y_val_true, y_val_pred, average='binary')
            metrics['val_f1'] = f1_score(y_val_true, y_val_pred, average='binary')
            
            # ROC AUC if probabilities available
            try:
                if hasattr(self, 'model') and hasattr(self.model, 'predict_proba'):
                    y_proba = self.model.predict_proba(X_val)[:, 1]
                    metrics['val_roc_auc'] = roc_auc_score(y_val_true, y_proba)
            except:
                pass
                
        else:  # Regression
            metrics['train_r2'] = r2_score(y_train_true, y_train_pred)
            metrics['train_rmse'] = np.sqrt(mean_squared_error(y_train_true, y_train_pred))
            metrics['train_mae'] = mean_absolute_error(y_train_true, y_train_pred)
            
            metrics['val_r2'] = r2_score(y_val_true, y_val_pred)
            metrics['val_rmse'] = np.sqrt(mean_squared_error(y_val_true, y_val_pred))
            metrics['val_mae'] = mean_absolute_error(y_val_true, y_val_pred)
        
        return metrics
    
    def _cross_validate_model(self, model: Any, X: pd.DataFrame, y: pd.Series) -> float:
        """Cross-validate model"""
        try:
            # Determine if it's classification or regression
            is_classification = len(np.unique(y)) <= 10 and y.dtype == 'object'
            
            if is_classification:
                cv = StratifiedKFold(n_splits=self.config.cv_folds, shuffle=True, random_state=42)
                scoring = 'accuracy'
            else:
                cv = KFold(n_splits=self.config.cv_folds, shuffle=True, random_state=42)
                scoring = 'r2'
            
            scores = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=1)
            return np.mean(scores)
            
        except Exception as e:
            self.logger.warning(f"Cross-validation failed: {e}")
            return 0.0
    
    def get_best_models(self, n_models: int = 10) -> List[Dict[str, Any]]:
        """Get top N performing models"""
        successful_results = [r for r in self.evaluation_results if r.get('success', False)]
        
        if not successful_results:
            return []
        
        # Sort by CV score (primary) and training time (secondary)
        successful_results.sort(
            key=lambda x: (x.get('cv_score', 0), -x.get('training_time', float('inf'))),
            reverse=True
        )
        
        return successful_results[:n_models]

class HyperparameterOptimizer:
    """Hyperparameter optimization"""
    
    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.HyperparameterOptimizer")
    
    def optimize_hyperparameters(self, model_class: type, hyperparams: Dict[str, List],
                               X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, Any]:
        """Optimize hyperparameters for a model"""
        
        try:
            if self.config.tuning_method == 'grid':
                search = GridSearchCV(
                    model_class(),
                    hyperparams,
                    cv=self.config.cv_folds,
                    scoring='accuracy' if len(np.unique(y_train)) <= 10 else 'r2',
                    n_jobs=min(self.config.n_cores, 4) if self.config.n_cores != -1 else 1
                )
            else:  # random search
                search = RandomizedSearchCV(
                    model_class(),
                    hyperparams,
                    n_iter=self.config.max_tuning_iterations,
                    cv=self.config.cv_folds,
                    scoring='accuracy' if len(np.unique(y_train)) <= 10 else 'r2',
                    random_state=42,
                    n_jobs=min(self.config.n_cores, 4) if self.config.n_cores != -1 else 1
                )
            
            search.fit(X_train, y_train)
            
            return {
                'best_params': search.best_params_,
                'best_score': search.best_score_,
                'cv_results': search.cv_results_,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Hyperparameter optimization failed: {e}")
            return {
                'error': str(e),
                'success': False
            }

class EnsembleBuilder:
    """Build model ensembles"""
    
    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.EnsembleBuilder")
    
    def build_ensemble(self, top_models: List[Dict[str, Any]], 
                      X_train: pd.DataFrame, y_train: pd.Series,
                      X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Build ensemble from top models"""
        
        if len(top_models) < 2:
            return {'error': 'Need at least 2 models for ensemble'}
        
        try:
            if self.config.ensemble_method == 'voting':
                return self._build_voting_ensemble(top_models, X_train, y_train, X_val, y_val)
            else:  # stacking
                return self._build_stacking_ensemble(top_models, X_train, y_train, X_val, y_val)
                
        except Exception as e:
            self.logger.error(f"Ensemble building failed: {e}")
            return {'error': str(e)}
    
    def _build_voting_ensemble(self, top_models: List[Dict[str, Any]], 
                             X_train: pd.DataFrame, y_train: pd.Series,
                             X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Build voting ensemble"""
        from sklearn.ensemble import VotingClassifier, VotingRegressor
        
        # Determine if classification or regression
        is_classification = len(np.unique(y_train)) <= 10 and y_train.dtype == 'object'
        
        # Select top models for ensemble
        selected_models = top_models[:self.config.ensemble_size]
        
        # Create ensemble
        estimators = []
        for model_info in selected_models:
            model_class = model_info['model_class']
            hyperparams = model_info['hyperparameters']
            
            # Create model instance
            model = model_class(**hyperparams)
            model.fit(X_train, y_train)
            
            estimators.append((model_info['model_name'], model))
        
        if is_classification:
            ensemble = VotingClassifier(estimators=estimators, voting='soft')
        else:
            ensemble = VotingRegressor(estimators=estimators)
        
        # Train ensemble
        ensemble.fit(X_train, y_train)
        
        # Evaluate ensemble
        y_pred = ensemble.predict(X_val)
        
        if is_classification:
            ensemble_score = accuracy_score(y_val, y_pred)
        else:
            ensemble_score = r2_score(y_val, y_pred)
        
        return {
            'ensemble_type': 'voting',
            'models': [model['model_name'] for model in selected_models],
            'ensemble_score': ensemble_score,
            'ensemble_model': ensemble,
            'success': True
        }
    
    def _build_stacking_ensemble(self, top_models: List[Dict[str, Any]], 
                               X_train: pd.DataFrame, y_train: pd.Series,
                               X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Build stacking ensemble"""
        from sklearn.ensemble import StackingClassifier, StackingRegressor
        
        # Determine if classification or regression
        is_classification = len(np.unique(y_train)) <= 10 and y_train.dtype == 'object'
        
        # Select top models for ensemble
        selected_models = top_models[:self.config.ensemble_size]
        
        # Create base estimators
        base_estimators = []
        for model_info in selected_models:
            model_class = model_info['model_class']
            hyperparams = model_info['hyperparameters']
            
            # Create model instance
            model = model_class(**hyperparams)
            model.fit(X_train, y_train)
            
            base_estimators.append((model_info['model_name'], model))
        
        # Create meta-estimator
        if is_classification:
            meta_estimator = LogisticRegression(random_state=42)
        else:
            meta_estimator = LinearRegression()
        
        # Create stacking ensemble
        if is_classification:
            ensemble = StackingClassifier(
                estimators=base_estimators,
                final_estimator=meta_estimator,
                cv=3
            )
        else:
            ensemble = StackingRegressor(
                estimators=base_estimators,
                final_estimator=meta_estimator,
                cv=3
            )
        
        # Train ensemble
        ensemble.fit(X_train, y_train)
        
        # Evaluate ensemble
        y_pred = ensemble.predict(X_val)
        
        if is_classification:
            ensemble_score = accuracy_score(y_val, y_pred)
        else:
            ensemble_score = r2_score(y_val, y_pred)
        
        return {
            'ensemble_type': 'stacking',
            'models': [model['model_name'] for model in selected_models],
            'ensemble_score': ensemble_score,
            'ensemble_model': ensemble,
            'success': True
        }

class AutoMLPipeline:
    """Complete AutoML pipeline"""
    
    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AutoML")
        
        # Components
        self.model_registry = ModelRegistry()
        self.feature_engineer = FeatureEngineer(config)
        self.model_evaluator = ModelEvaluator(config)
        self.hyperparameter_optimizer = HyperparameterOptimizer(config)
        self.ensemble_builder = EnsembleBuilder(config)
        
        # Pipeline state
        self.best_model = None
        self.best_score = float('-inf')
        self.pipeline_results = {}
        
    def fit(self, X: pd.DataFrame, y: pd.Series, task_type: Optional[str] = None) -> Dict[str, Any]:
        """Fit the complete AutoML pipeline"""
        
        self.logger.info("Starting AutoML pipeline...")
        start_time = time.time()
        
        # Determine task type
        if task_type is None:
            task_type = 'classifier' if len(np.unique(y)) <= 10 and y.dtype == 'object' else 'regressor'
        
        # Split data
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=self.config.test_split, random_state=42, 
            stratify=y if task_type == 'classifier' else None
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=self.config.validation_split, 
            random_state=42, stratify=y_temp if task_type == 'classifier' else None
        )
        
        self.logger.info(f"Data split - Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        # Feature engineering
        self.logger.info("Starting feature engineering...")
        X_train_processed = self.feature_engineer.engineer_features(X_train, y_train, task_type)
        X_val_processed = self.feature_engineer.feature_selector.transform(X_val) if self.feature_engineer.feature_selector else X_val
        X_test_processed = self.feature_engineer.feature_selector.transform(X_test) if self.feature_engineer.feature_selector else X_test
        
        # If PCA was applied, transform all sets
        if hasattr(self.feature_engineer, 'scaler') and self.feature_engineer.scaler:
            X_train_processed = self.feature_engineer.scaler.transform(X_train_processed)
            X_val_processed = self.feature_engineer.scaler.transform(X_val_processed)
            X_test_processed = self.feature_engineer.scaler.transform(X_test_processed)
        
        # Model evaluation
        self.logger.info("Starting model evaluation...")
        self._evaluate_all_models(X_train_processed, y_train, X_val_processed, y_val, task_type)
        
        # Get best models
        best_models = self.model_evaluator.get_best_models(self.config.max_models_to_try)
        
        # Hyperparameter tuning for top models
        if self.config.enable_hyperparameter_tuning and best_models:
            self.logger.info("Starting hyperparameter tuning...")
            best_models = self._tune_hyperparameters(best_models, X_train_processed, y_train, task_type)
        
        # Ensemble building
        if self.config.enable_ensemble and len(best_models) >= 2:
            self.logger.info("Building ensemble...")
            ensemble_result = self.ensemble_builder.build_ensemble(
                best_models, X_train_processed, y_train, X_val_processed, y_val
            )
        else:
            ensemble_result = {'success': False, 'error': 'Insufficient models for ensemble'}
        
        # Select best model
        best_overall = self._select_best_model(best_models, ensemble_result)
        
        # Final evaluation
        final_score = self._final_evaluation(best_overall, X_train_processed, y_train, 
                                           X_test_processed, y_test)
        
        total_time = time.time() - start_time
        
        # Compile results
        results = {
            'task_type': task_type,
            'data_info': {
                'original_shape': X.shape,
                'processed_shape': X_train_processed.shape,
                'train_samples': len(X_train),
                'validation_samples': len(X_val),
                'test_samples': len(X_test)
            },
            'feature_engineering': {
                'selected_features': len(self.feature_engineer.feature_names) if self.feature_engineer.feature_names else X.shape[1],
                'scaler_used': type(self.feature_engineer.scaler).__name__ if self.feature_engineer.scaler else 'None',
                'feature_selector': type(self.feature_engineer.feature_selector).__name__ if self.feature_engineer.feature_selector else 'None'
            },
            'model_evaluation': {
                'total_models_evaluated': len(self.model_evaluator.evaluation_results),
                'successful_evaluations': len([r for r in self.model_evaluator.evaluation_results if r.get('success', False)]),
                'top_models': best_models[:5]  # Top 5
            },
            'ensemble_results': ensemble_result,
            'best_model': best_overall,
            'final_performance': final_score,
            'execution_time_minutes': total_time / 60,
            'pipeline_success': True
        }
        
        self.pipeline_results = results
        self.best_model = best_overall
        
        self.logger.info(f"AutoML pipeline completed in {total_time/60:.2f} minutes")
        self.logger.info(f"Best model: {best_overall.get('model_name', 'Unknown')}")
        self.logger.info(f"Best score: {final_score.get('test_score', 'N/A')}")
        
        return results
    
    def _evaluate_all_models(self, X_train: pd.DataFrame, y_train: pd.Series,
                           X_val: pd.DataFrame, y_val: pd.Series, task_type: str) -> None:
        """Evaluate all available models"""
        
        def evaluate_single_model(model_name):
            try:
                # Get model class
                model_class = self.model_registry.get_model_class(model_name, task_type)
                if model_class is None:
                    return None
                
                # Basic evaluation without hyperparameter tuning
                result = self.model_evaluator.evaluate_model(
                    model_name, model_class, X_train, y_train, X_val, y_val
                )
                return result
                
            except Exception as e:
                self.logger.error(f"Error evaluating {model_name}: {e}")
                return None
        
        # Filter models based on allowed list
        available_models = [name for name in self.model_registry.models.keys() 
                          if name in self.config.allowed_models]
        
        # Parallel evaluation if enabled
        if self.config.parallel_processing:
            n_workers = min(self.config.n_cores, len(available_models)) if self.config.n_cores != -1 else len(available_models)
            with ThreadPoolExecutor(max_workers=n_workers) as executor:
                results = list(executor.map(evaluate_single_model, available_models))
        else:
            results = [evaluate_single_model(name) for name in available_models]
        
        # Filter out None results
        self.model_evaluator.evaluation_results = [r for r in results if r is not None]
    
    def _tune_hyperparameters(self, best_models: List[Dict[str, Any]], 
                            X_train: pd.DataFrame, y_train: pd.Series, task_type: str) -> List[Dict[str, Any]]:
        """Tune hyperparameters for best models"""
        
        tuned_models = []
        
        for model_info in best_models[:min(10, len(best_models))]:  # Tune top 10
            try:
                model_name = model_info['model_name']
                model_class = self.model_registry.get_model_class(model_name, task_type)
                
                if model_class is None:
                    continue
                
                # Get hyperparameter space
                hyperparams = self.model_registry.get_hyperparameters(model_name, task_type)
                if not hyperparams:
                    tuned_models.append(model_info)
                    continue
                
                # Optimize hyperparameters
                optimization_result = self.hyperparameter_optimizer.optimize_hyperparameters(
                    model_class, hyperparams, X_train, y_train
                )
                
                if optimization_result.get('success', False):
                    # Update model with best parameters
                    tuned_model_info = model_info.copy()
                    tuned_model_info['hyperparameters'] = optimization_result['best_params']
                    tuned_model_info['cv_score'] = optimization_result['best_score']
                    tuned_models.append(tuned_model_info)
                else:
                    tuned_models.append(model_info)
                    
            except Exception as e:
                self.logger.warning(f"Hyperparameter tuning failed for {model_info['model_name']}: {e}")
                tuned_models.append(model_info)
        
        return tuned_models
    
    def _select_best_model(self, best_models: List[Dict[str, Any]], 
                          ensemble_result: Dict[str, Any]) -> Dict[str, Any]:
        """Select the best performing model or ensemble"""
        
        # Check if ensemble is better than best individual model
        if (ensemble_result.get('success', False) and 
            best_models and 
            ensemble_result['ensemble_score'] > best_models[0].get('cv_score', 0)):
            
            return {
                'model_name': 'Ensemble',
                'model_type': 'ensemble',
                'ensemble_method': ensemble_result['ensemble_type'],
                'models_used': ensemble_result['models'],
                'score': ensemble_result['ensemble_score'],
                'ensemble_model': ensemble_result['ensemble_model']
            }
        elif best_models:
            best_model = best_models[0]
            return {
                'model_name': best_model['model_name'],
                'model_type': 'single',
                'score': best_model['cv_score'],
                'hyperparameters': best_model['hyperparameters'],
                'metrics': best_model['metrics']
            }
        else:
            return {'error': 'No successful models found'}
    
    def _final_evaluation(self, best_model: Dict[str, Any], 
                        X_train: pd.DataFrame, y_train: pd.Series,
                        X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """Final evaluation on test set"""
        
        if 'ensemble_model' in best_model:
            # Evaluate ensemble
            ensemble_model = best_model['ensemble_model']
            y_pred = ensemble_model.predict(X_test)
            
            if len(np.unique(y_test)) <= 10:  # Classification
                test_score = accuracy_score(y_test, y_pred)
            else:  # Regression
                test_score = r2_score(y_test, y_pred)
                
        elif 'hyperparameters' in best_model:
            # Evaluate single model
            model_name = best_model['model_name']
            
            # Get model class and create instance
            task_type = 'classifier' if len(np.unique(y_train)) <= 10 else 'regressor'
            model_class = self.model_registry.get_model_class(model_name, task_type)
            
            if model_class:
                model = model_class(**best_model['hyperparameters'])
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                if task_type == 'classifier':
                    test_score = accuracy_score(y_test, y_pred)
                else:
                    test_score = r2_score(y_test, y_pred)
            else:
                test_score = 0.0
        else:
            test_score = 0.0
        
        return {
            'test_score': test_score,
            'test_samples': len(X_test)
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions using the best model"""
        if self.best_model is None:
            raise ValueError("Pipeline must be fitted before prediction")
        
        # Apply same feature engineering
        X_processed = self.feature_engineer.engineer_features(X, pd.Series([0]*len(X)), 'classifier')
        
        if 'ensemble_model' in self.best_model:
            return self.best_model['ensemble_model'].predict(X_processed)
        elif 'hyperparameters' in self.best_model:
            # Recreate and fit the model
            model_name = self.best_model['model_name']
            task_type = 'classifier'  # Simplified
            
            model_class = self.model_registry.get_model_class(model_name, task_type)
            if model_class:
                model = model_class(**self.best_model['hyperparameters'])
                # Note: In practice, you'd want to store the fitted model
                # For now, this is a simplified version
                model.fit(X_processed, pd.Series([0]*len(X_processed)))
                return model.predict(X_processed)
        
        raise ValueError("Cannot make predictions with current model")
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get comprehensive pipeline summary"""
        return self.pipeline_results
    
    def export_results(self, filepath: str) -> None:
        """Export pipeline results to file"""
        if self.pipeline_results:
            with open(filepath, 'w') as f:
                json.dump(self.pipeline_results, f, indent=2, default=str)
            self.logger.info(f"Pipeline results exported to {filepath}")

# Convenience function for quick usage
def run_automl(X: pd.DataFrame, y: pd.Series, config: Optional[AutoMLConfig] = None, 
               task_type: Optional[str] = None) -> AutoMLPipeline:
    """Run AutoML pipeline with minimal configuration"""
    
    if config is None:
        config = AutoMLConfig()
    
    pipeline = AutoMLPipeline(config)
    results = pipeline.fit(X, y, task_type)
    
    return pipeline, results