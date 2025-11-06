"""
AutoML Integration
Avtomatik ML - hyperparameter tuning, feature selection, model selection
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import pickle

# ML libraries
try:
    import sklearn
    from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
    from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
    from sklearn.svm import SVC, SVR
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
    from sklearn.naive_bayes import GaussianNB
    from sklearn.neural_network import MLPClassifier, MLPRegressor
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
    from sklearn.feature_selection import SelectKBest, f_classif, f_regression, RFE
    from sklearn.decomposition import PCA
    from sklearn.model_selection import cross_val_score, GridSearchCV, RandomizedSearchCV
    from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error
    from sklearn.model_selection import train_test_split
except ImportError:
    sklearn = None

try:
    from scipy.stats import uniform, randint
except ImportError:
    uniform = randint = None

@dataclass
class AutoMLConfig:
    """AutoML konfiguratsiyasi"""
    task_type: str  # classification, regression
    algorithms: List[str]
    search_strategy: str  # grid, random, bayesian
    max_trials: int
    timeout_hours: float
    cv_folds: int
    validation_split: float
    random_state: int
    preprocessing_enabled: bool
    feature_selection_enabled: bool
    ensemble_enabled: bool
    optimization_metric: str
    optimization_direction: str  # maximize, minimize
    
@dataclass
class TrialResult:
    """AutoML trial natijasi"""
    trial_id: str
    algorithm: str
    hyperparameters: Dict[str, Any]
    preprocessing_steps: List[str]
    feature_selection_method: str
    cv_score: float
    train_score: float
    test_score: float
    training_time_seconds: float
    model_size_mb: float
    complexity_score: float
    timestamp: datetime
    status: str  # completed, failed, timeout

class DataPreprocessor:
    """Ma'lumotlar preprocessing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler(),
            'none': None
        }
        self.encoders = {}
        
    def auto_preprocess(self, X: pd.DataFrame, y: pd.Series, 
                       task_type: str) -> Tuple[pd.DataFrame, List[str]]:
        """Avtomatik preprocessing"""
        X_processed = X.copy()
        preprocessing_steps = []
        
        # Missing values
        missing_imputed = self._handle_missing_values(X_processed)
        if missing_imputed:
            preprocessing_steps.append('missing_value_imputation')
            X_processed = missing_imputed
            
        # Outliers
        outliers_removed = self._handle_outliers(X_processed)
        if outliers_removed:
            preprocessing_steps.append('outlier_removal')
            X_processed = outliers_removed
            
        # Feature scaling
        scaled_features = self._scale_features(X_processed, task_type)
        if scaled_features:
            preprocessing_steps.append('feature_scaling')
            X_processed = scaled_features
            
        # Encoding categorical variables
        encoded_features = self._encode_categorical(X_processed)
        if encoded_features:
            preprocessing_steps.append('categorical_encoding')
            X_processed = encoded_features
            
        return X_processed, preprocessing_steps
        
    def _handle_missing_values(self, X: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Yo'qolgan qiymatlarni boshqarish"""
        missing_ratio = X.isnull().sum() / len(X)
        
        # Agar column da 50% dan ko'p missing bo'lsa, o'chirish
        cols_to_drop = missing_ratio[missing_ratio > 0.5].index
        if len(cols_to_drop) > 0:
            X_cleaned = X.drop(columns=cols_to_drop)
        else:
            X_cleaned = X.copy()
            
        # Qo'lgan missing value larni fill qilish
        for column in X_cleaned.columns:
            if X_cleaned[column].isnull().sum() > 0:
                if X_cleaned[column].dtype in ['object']:
                    X_cleaned[column] = X_cleaned[column].fillna(X_cleaned[column].mode()[0] if not X_cleaned[column].mode().empty else 'unknown')
                else:
                    X_cleaned[column] = X_cleaned[column].fillna(X_cleaned[column].median())
                    
        return X_cleaned
        
    def _handle_outliers(self, X: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Outlier larni boshqarish"""
        # Faqat numeric columns uchun
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return None
            
        X_cleaned = X.copy()
        outlier_indices = set()
        
        for col in numeric_cols:
            Q1 = X_cleaned[col].quantile(0.25)
            Q3 = X_cleaned[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            col_outliers = ((X_cleaned[col] < lower_bound) | 
                          (X_cleaned[col] > upper_bound)).index
            outlier_indices.update(col_outliers)
            
        # Agar outlier lar 10% dan kam bolsa o'chirish
        outlier_ratio = len(outlier_indices) / len(X_cleaned)
        if outlier_ratio <= 0.1:
            X_cleaned = X_cleaned.drop(index=outlier_indices)
            return X_cleaned
            
        return None  # Outlier larni o'chirish kerak emas
        
    def _scale_features(self, X: pd.DataFrame, task_type: str) -> Optional[pd.DataFrame]:
        """Feature scaling"""
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return None
            
        X_scaled = X.copy()
        
        # Algorithm ga qarab scaling tanlash
        # Random Forest kabi tree-based algoritmalar scaling talab qilmaydi
        if task_type == 'classification':
            scaler = self.scalers['standard']
        else:
            scaler = self.scalers['robust']  # Regression uchun robust
            
        if scaler:
            X_scaled[numeric_cols] = scaler.fit_transform(X_scaled[numeric_cols])
            
        return X_scaled
        
    def _encode_categorical(self, X: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Categorical variable encoding"""
        categorical_cols = X.select_dtypes(include=['object']).columns
        
        if len(categorical_cols) == 0:
            return None
            
        X_encoded = X.copy()
        
        for col in categorical_cols:
            unique_count = X_encoded[col].nunique()
            
            if unique_count <= 10:  # Low cardinality - one-hot encoding
                dummies = pd.get_dummies(X_encoded[col], prefix=col)
                X_encoded = pd.concat([X_encoded.drop(columns=[col]), dummies], axis=1)
            else:  # High cardinality - label encoding
                X_encoded[col] = pd.Categorical(X_encoded[col]).codes
                
        return X_encoded

class FeatureSelector:
    """Feature selection"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def auto_select_features(self, X: pd.DataFrame, y: pd.Series, 
                           task_type: str, algorithm: str) -> Tuple[pd.DataFrame, str]:
        """Avtomatik feature selection"""
        
        # Tree-based algoritmlar uchun feature selection zarur emas
        if algorithm in ['random_forest', 'gradient_boosting', 'decision_tree']:
            return X, 'none'
            
        # Korrelatsiya hisoblash
        correlation_threshold = 0.9
        corr_matrix = X.corr().abs()
        
        # Yuqori korrelatsiyali feature larni topish
        upper_triangle = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )
        
        high_corr_features = [column for column in upper_triangle.columns 
                            if any(upper_triangle[column] > correlation_threshold)]
        
        if high_corr_features:
            X_filtered = X.drop(columns=high_corr_features)
            return X_filtered, 'correlation_filter'
            
        # Statistical feature selection
        if task_type == 'classification':
            selector = SelectKBest(score_func=f_classif, k='all')
        else:
            selector = SelectKBest(score_func=f_regression, k='all')
            
        X_selected = selector.fit_transform(X, y)
        
        # Feature importance asosida top features ni tanlash
        feature_scores = selector.scores_
        num_features = min(max(10, len(feature_scores) // 3), len(feature_scores))
        
        top_indices = np.argsort(feature_scores)[-num_features:]
        X_reduced = X.iloc[:, top_indices]
        
        return X_reduced, 'statistical_selection'

class ModelSelector:
    """Model tanlash va konfiguratsiya"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Algorithm search spaces
        self.search_spaces = self._initialize_search_spaces()
        
    def _initialize_search_spaces(self) -> Dict[str, Dict[str, List]]:
        """Algorithm hyperparameter search spaces"""
        spaces = {
            'random_forest': {
                'n_estimators': [50, 100, 200, 300],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'max_features': ['sqrt', 'log2', None]
            },
            'gradient_boosting': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 0.9, 1.0]
            },
            'logistic_regression': {
                'C': [0.001, 0.01, 0.1, 1, 10, 100],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            },
            'svm': {
                'C': [0.1, 1, 10, 100],
                'kernel': ['linear', 'rbf', 'poly'],
                'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1]
            },
            'neural_network': {
                'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
                'activation': ['relu', 'tanh'],
                'alpha': [0.0001, 0.001, 0.01],
                'learning_rate': ['constant', 'adaptive']
            },
            'decision_tree': {
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'criterion': ['gini', 'entropy']
            },
            'k_neighbors': {
                'n_neighbors': [3, 5, 7, 9, 11],
                'weights': ['uniform', 'distance'],
                'algorithm': ['auto', 'ball_tree', 'kd_tree']
            }
        }
        
        return spaces
        
    def get_algorithm(self, algorithm_name: str, task_type: str, hyperparameters: Dict[str, Any]):
        """Algorithm instance yaratish"""
        
        if not sklearn:
            raise ImportError("scikit-learn not available")
            
        classifiers = {
            'random_forest': RandomForestClassifier,
            'gradient_boosting': GradientBoostingClassifier,
            'logistic_regression': LogisticRegression,
            'svm': SVC,
            'neural_network': MLPClassifier,
            'decision_tree': DecisionTreeClassifier,
            'k_neighbors': KNeighborsClassifier,
            'naive_bayes': GaussianNB
        }
        
        regressors = {
            'random_forest': RandomForestRegressor,
            'gradient_boosting': GradientBoostingRegressor,
            'linear_regression': LinearRegression,
            'ridge': Ridge,
            'lasso': Lasso,
            'svm': SVR,
            'neural_network': MLPRegressor,
            'decision_tree': DecisionTreeRegressor,
            'k_neighbors': KNeighborsRegressor
        }
        
        if task_type == 'classification':
            if algorithm_name in classifiers:
                return classifiers[algorithm_name](**hyperparameters)
            elif algorithm_name == 'linear_regression':
                return LinearRegression(**hyperparameters)
        else:
            if algorithm_name in regressors:
                return regressors[algorithm_name](**hyperparameters)
            elif algorithm_name == 'logistic_regression':
                return LogisticRegression(**hyperparameters)
                
        raise ValueError(f"Algorithm not supported: {algorithm_name}")
        
    def generate_hyperparameters(self, algorithm_name: str, search_strategy: str, 
                               max_trials: int) -> List[Dict[str, Any]]:
        """Hyperparameter combinations generate qilish"""
        
        if algorithm_name not in self.search_spaces:
            return [{}]  # Default parameters
            
        param_space = self.search_spaces[algorithm_name]
        
        # Grid search
        if search_strategy == 'grid':
            return self._grid_search_combinations(param_space, max_trials)
        
        # Random search
        elif search_strategy == 'random':
            return self._random_search_combinations(param_space, max_trials)
            
        else:
            return [{}]  # Default
            
    def _grid_search_combinations(self, param_space: Dict[str, List], 
                                max_trials: int) -> List[Dict[str, Any]]:
        """Grid search combinations"""
        import itertools
        
        # Parameter combinations
        keys, values = zip(*param_space.items())
        combinations = list(itertools.product(*values))
        
        # Trial limit
        if len(combinations) > max_trials:
            # Select random subset
            random.shuffle(combinations)
            combinations = combinations[:max_trials]
            
        return [dict(zip(keys, combo)) for combo in combinations]
        
    def _random_search_combinations(self, param_space: Dict[str, List], 
                                  max_trials: int) -> List[Dict[str, Any]]:
        """Random search combinations"""
        combinations = []
        
        for _ in range(max_trials):
            params = {}
            for param_name, param_values in param_space.items():
                params[param_name] = random.choice(param_values)
            combinations.append(params)
            
        return combinations

class HyperparameterOptimizer:
    """Hyperparameter optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def optimize_algorithm(self, algorithm_name: str, task_type: str, 
                          X: pd.DataFrame, y: pd.Series,
                          search_strategy: str, max_trials: int,
                          cv_folds: int, timeout_hours: float) -> List[TrialResult]:
        """Algorithm optimization"""
        
        model_selector = ModelSelector(self.config)
        results = []
        
        start_time = time.time()
        timeout_seconds = timeout_hours * 3600
        
        # Hyperparameter combinations
        param_combinations = model_selector.generate_hyperparameters(
            algorithm_name, search_strategy, max_trials
        )
        
        for i, hyperparameters in enumerate(param_combinations):
            if time.time() - start_time > timeout_seconds:
                self.logger.warning("Optimization timeout")
                break
                
            trial_id = f"{algorithm_name}_trial_{i+1}"
            
            try:
                # Model yaratish
                model = model_selector.get_algorithm(algorithm_name, task_type, hyperparameters)
                
                # Cross validation
                if sklearn:
                    cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring='accuracy' if task_type == 'classification' else 'neg_mean_squared_error')
                    cv_score = np.mean(cv_scores)
                else:
                    cv_score = 0.5  # Fallback
                    
                # Train/test split for additional validation
                if sklearn:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                    
                    train_start = time.time()
                    model.fit(X_train, y_train)
                    training_time = time.time() - train_start
                    
                    train_score = model.score(X_train, y_train)
                    test_score = model.score(X_test, y_test)
                else:
                    train_score = test_score = cv_score
                    training_time = 1.0
                    
                # Model complexity
                complexity_score = self._calculate_complexity_score(model)
                model_size_mb = self._estimate_model_size(model)
                
                result = TrialResult(
                    trial_id=trial_id,
                    algorithm=algorithm_name,
                    hyperparameters=hyperparameters,
                    preprocessing_steps=[],
                    feature_selection_method='none',
                    cv_score=cv_score,
                    train_score=train_score,
                    test_score=test_score,
                    training_time_seconds=training_time,
                    model_size_mb=model_size_mb,
                    complexity_score=complexity_score,
                    timestamp=datetime.now(),
                    status='completed'
                )
                
                results.append(result)
                self.logger.info(f"Trial completed: {trial_id}, cv_score={cv_score:.4f}")
                
            except Exception as e:
                self.logger.error(f"Trial failed: {trial_id}, error={str(e)}")
                result = TrialResult(
                    trial_id=trial_id,
                    algorithm=algorithm_name,
                    hyperparameters=hyperparameters,
                    preprocessing_steps=[],
                    feature_selection_method='none',
                    cv_score=0.0,
                    train_score=0.0,
                    test_score=0.0,
                    training_time_seconds=0.0,
                    model_size_mb=0.0,
                    complexity_score=0.0,
                    timestamp=datetime.now(),
                    status='failed'
                )
                results.append(result)
                
        return results
        
    def _calculate_complexity_score(self, model) -> float:
        """Model complexity score hisoblash"""
        if sklearn and hasattr(model, 'n_estimators'):
            # Tree-based models
            if hasattr(model, 'estimators_'):
                return len(model.estimators_)
            else:
                return getattr(model, 'n_estimators', 100)
        elif sklearn and hasattr(model, 'n_layers_'):
            # Neural networks
            return len(model.hidden_layer_sizes)
        else:
            return 1.0  # Default complexity
            
    def _estimate_model_size(self, model) -> float:
        """Model size estimation"""
        try:
            # Pickle model and get size
            model_bytes = pickle.dumps(model)
            return len(model_bytes) / (1024 * 1024)  # MB
        except:
            return 0.1  # Default 0.1 MB

class AutoMLSystem:
    """AutoML tizimi"""
    
    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.preprocessor = DataPreprocessor({})
        self.feature_selector = FeatureSelector({})
        self.optimizer = HyperparameterOptimizer({})
        
        # State
        self.best_model = None
        self.best_score = 0.0
        self.all_results = []
        self.optimization_history = []
        
    def run_automl(self, X: pd.DataFrame, y: pd.Series, 
                  model_output_path: str = None) -> Dict[str, Any]:
        """AutoML pipeline ishga tushirish"""
        
        start_time = time.time()
        self.logger.info("AutoML pipeline boshlandi")
        
        try:
            # 1. Data preprocessing
            X_processed, preprocessing_steps = self.preprocessor.auto_preprocess(
                X, y, self.config.task_type
            )
            self.logger.info(f"Preprocessing completed: {len(preprocessing_steps)} steps")
            
            # 2. Feature selection
            selected_features = self.feature_selector.auto_select_features(
                X_processed, y, self.config.task_type, 'random_forest'
            )
            
            # 3. Model optimization
            all_trials = []
            for algorithm in self.config.algorithms:
                self.logger.info(f"Optimizing algorithm: {algorithm}")
                
                trials = self.optimizer.optimize_algorithm(
                    algorithm, self.config.task_type, X_processed, y,
                    self.config.search_strategy, self.config.max_trials,
                    self.config.cv_folds, self.config.timeout_hours
                )
                
                # Add preprocessing info
                for trial in trials:
                    trial.preprocessing_steps = preprocessing_steps
                    trial.feature_selection_method = selected_features[1]
                    
                all_trials.extend(trials)
                
            # 4. Select best model
            best_trial = self._select_best_trial(all_trials)
            
            # 5. Train final model
            final_model = self._train_final_model(
                best_trial, X_processed, y
            )
            
            # 6. Save model
            if model_output_path:
                self._save_model(final_model, model_output_path, best_trial)
                
            optimization_time = time.time() - start_time
            
            # 7. Results summary
            results = {
                'status': 'completed',
                'optimization_time_seconds': optimization_time,
                'best_trial': asdict(best_trial),
                'all_trials_count': len(all_trials),
                'successful_trials_count': len([t for t in all_trials if t.status == 'completed']),
                'algorithms_tested': list(set([t.algorithm for t in all_trials])),
                'final_model_path': model_output_path,
                'optimization_summary': self._generate_optimization_summary(all_trials)
            }
            
            self.all_results = all_trials
            self.optimization_history.append(results)
            
            self.logger.info(f"AutoML completed in {optimization_time:.2f} seconds")
            self.logger.info(f"Best model: {best_trial.algorithm}, score: {best_trial.cv_score:.4f}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"AutoML xatosi: {str(e)}")
            return {
                'status': 'failed',
                'error_message': str(e),
                'optimization_time_seconds': time.time() - start_time
            }
            
    def _select_best_trial(self, trials: List[TrialResult]) -> TrialResult:
        """Eng yaxshi trial ni tanlash"""
        completed_trials = [t for t in trials if t.status == 'completed']
        
        if not completed_trials:
            raise ValueError("Hech qanday successful trial topilmadi")
            
        # Optimization direction ga qarab sorting
        if self.config.optimization_direction == 'maximize':
            best_trial = max(completed_trials, key=lambda t: t.cv_score)
        else:
            best_trial = min(completed_trials, key=lambda t: t.cv_score)
            
        return best_trial
        
    def _train_final_model(self, trial: TrialResult, X: pd.DataFrame, y: pd.Series):
        """Final model o'qitish"""
        model_selector = ModelSelector({})
        
        model = model_selector.get_algorithm(
            trial.algorithm, self.config.task_type, trial.hyperparameters
        )
        
        model.fit(X, y)
        
        return model
        
    def _save_model(self, model, output_path: str, trial: TrialResult):
        """Model va metadata saqlash"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Model saqlash
        with open(output_path, 'wb') as f:
            pickle.dump(model, f)
            
        # Metadata saqlash
        metadata = {
            'trial_info': asdict(trial),
            'config': asdict(self.config),
            'saved_at': datetime.now().isoformat()
        }
        
        metadata_path = output_path.replace('.pkl', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
            
        self.logger.info(f"Model saved: {output_path}")
        
    def _generate_optimization_summary(self, trials: List[TrialResult]) -> Dict[str, Any]:
        """Optimization summary yaratish"""
        completed_trials = [t for t in trials if t.status == 'completed']
        
        if not completed_trials:
            return {}
            
        algorithm_scores = {}
        for trial in completed_trials:
            algorithm = trial.algorithm
            if algorithm not in algorithm_scores:
                algorithm_scores[algorithm] = []
            algorithm_scores[algorithm].append(trial.cv_score)
            
        summary = {
            'total_trials': len(trials),
            'successful_trials': len(completed_trials),
            'success_rate': len(completed_trials) / len(trials) if trials else 0,
            'best_cv_score': max([t.cv_score for t in completed_trials]),
            'average_cv_score': np.mean([t.cv_score for t in completed_trials]),
            'algorithm_performance': {}
        }
        
        for algorithm, scores in algorithm_scores.items():
            summary['algorithm_performance'][algorithm] = {
                'trials_count': len(scores),
                'best_score': max(scores),
                'average_score': np.mean(scores),
                'std_score': np.std(scores)
            }
            
        return summary
        
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Optimization tarixini olish"""
        return self.optimization_history
        
    def compare_algorithms(self, algorithm_names: List[str] = None) -> Dict[str, Any]:
        """Algorithm performance taqqoslash"""
        if not self.all_results:
            return {}
            
        completed_trials = [t for t in self.all_results if t.status == 'completed']
        
        if algorithm_names:
            completed_trials = [t for t in completed_trials if t.algorithm in algorithm_names]
            
        if not completed_trials:
            return {}
            
        # Algorithm performance
        algorithm_stats = {}
        for trial in completed_trials:
            algorithm = trial.algorithm
            if algorithm not in algorithm_stats:
                algorithm_stats[algorithm] = {
                    'cv_scores': [],
                    'training_times': [],
                    'complexity_scores': []
                }
                
            algorithm_stats[algorithm]['cv_scores'].append(trial.cv_score)
            algorithm_stats[algorithm]['training_times'].append(trial.training_time_seconds)
            algorithm_stats[algorithm]['complexity_scores'].append(trial.complexity_score)
            
        # Statistics calculation
        comparison = {}
        for algorithm, stats in algorithm_stats.items():
            comparison[algorithm] = {
                'cv_score_mean': np.mean(stats['cv_scores']),
                'cv_score_std': np.std(stats['cv_scores']),
                'training_time_mean': np.mean(stats['training_times']),
                'complexity_mean': np.mean(stats['complexity_scores']),
                'trials_count': len(stats['cv_scores'])
            }
            
        return comparison