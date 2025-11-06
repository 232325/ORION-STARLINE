"""
AI Training Pipeline - Model o'qitish va ma'lumotlar boshqaruvi
Auto-learning va model training pipeline yaratish
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import pickle
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ML kutubxonalar
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, chi2, RFE
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import joblib

# Advanced ML
try:
    import lightgbm as lgb
    import xgboost as xgb
    ADVANCED_ML_AVAILABLE = True
except ImportError:
    ADVANCED_ML_AVAILABLE = False

# Data validation
try:
    from great_expectations import DataContext
    GE_AVAILABLE = True
except ImportError:
    GE_AVAILABLE = False

@dataclass
class DataQualityMetrics:
    """Ma'lumotlar sifat ko'rsatkichlari"""
    completeness: float
    accuracy: float
    consistency: float
    timeliness: float
    validity: float
    uniqueness: float
    overall_score: float
    timestamp: datetime

@dataclass
class ModelPerformance:
    """Model performance metrikalari"""
    model_name: str
    version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    mae: float
    r2_score: float
    timestamp: datetime
    training_time: float

@dataclass
class RetrainingTrigger:
    """Qayta o'qitish triggerni"""
    trigger_type: str
    trigger_value: float
    threshold: float
    severity: str
    timestamp: datetime
    description: str

class DataPipeline:
    """Real-time ma'lumotlar to'plam va boshqaruv pipeline"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.data_buffer = []
        self.quality_metrics = []
        self.drift_detector = None
        
    async def collect_real_time_data(self, data_source: str) -> List[Dict]:
        """Real-time ma'lumotlar to'plash"""
        self.logger.info(f"Real-time data collection started from {data_source}")
        
        # Simulate real-time data collection
        sample_data = []
        for i in range(100):
            sample_data.append({
                'timestamp': datetime.now() - timedelta(minutes=i),
                'feature_1': np.random.normal(100, 15),
                'feature_2': np.random.exponential(2),
                'feature_3': np.random.uniform(0, 1),
                'target': np.random.choice([0, 1], p=[0.7, 0.3])
            })
        
        self.data_buffer.extend(sample_data)
        self.logger.info(f"Collected {len(sample_data)} data points")
        
        return sample_data
    
    def preprocess_data(self, data: List[Dict]) -> pd.DataFrame:
        """Ma'lumotlarni oldindan ishlash"""
        self.logger.info("Starting data preprocessing")
        
        df = pd.DataFrame(data)
        
        # Handle missing values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        # Fill missing values
        for col in numeric_columns:
            df[col].fillna(df[col].mean(), inplace=True)
        
        for col in categorical_columns:
            df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown', inplace=True)
        
        # Outlier detection and handling
        for col in numeric_columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Replace outliers with median
            df[col] = np.where((df[col] < lower_bound) | (df[col] > upper_bound), 
                             df[col].median(), df[col])
        
        self.logger.info("Data preprocessing completed")
        return df
    
    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Xususiyatlarni yaratish"""
        self.logger.info("Starting feature engineering")
        
        # Create time-based features
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            df['month'] = pd.to_datetime(df['timestamp']).dt.month
        
        # Create interaction features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != 'target']
        
        # Create polynomial features for top 3 numeric features
        for i, col1 in enumerate(numeric_cols[:3]):
            for col2 in numeric_cols[i+1:4]:
                df[f'{col1}_{col2}_interaction'] = df[col1] * df[col2]
        
        # Create ratio features
        for col1 in numeric_cols[:2]:
            for col2 in numeric_cols[2:4]:
                if df[col2].sum() != 0:
                    df[f'{col1}_{col2}_ratio'] = df[col1] / (df[col2] + 1e-8)
        
        self.logger.info(f"Feature engineering completed. New features: {len(df.columns)} total")
        return df
    
    def feature_selection(self, df: pd.DataFrame, target_col: str, k: int = 20) -> pd.DataFrame:
        """Xususiyatlarni tanlash"""
        self.logger.info(f"Starting feature selection (top {k} features)")
        
        X = df.drop(columns=[target_col] if target_col in df.columns else [])
        y = df[target_col] if target_col in df.columns else None
        
        if y is None:
            self.logger.warning("No target column found, skipping feature selection")
            return df
        
        # Remove non-numeric columns
        numeric_X = X.select_dtypes(include=[np.number])
        
        if len(numeric_X.columns) <= k:
            return df
        
        # Univariate feature selection
        selector = SelectKBest(score_func=chi2 if y.dtype == 'int' else None, k=k)
        
        try:
            X_selected = selector.fit_transform(numeric_X, y)
            selected_features = numeric_X.columns[selector.get_support()]
            
            # Add back non-numeric columns and target
            result_cols = list(selected_features)
            for col in df.columns:
                if col not in numeric_X.columns and col != target_col:
                    result_cols.append(col)
            
            selected_df = df[result_cols + [target_col]]
            
            self.logger.info(f"Feature selection completed. Selected {len(selected_features)} features")
            return selected_df
            
        except Exception as e:
            self.logger.error(f"Feature selection failed: {e}")
            return df
    
    def validate_data(self, df: pd.DataFrame) -> DataQualityMetrics:
        """Ma'lumotlarni validatsiya qilish"""
        self.logger.info("Starting data validation")
        
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        completeness = (total_cells - missing_cells) / total_cells
        
        # Accuracy check (basic)
        accuracy = 0.95  # Mock accuracy
        
        # Consistency check
        consistency = 0.90  # Mock consistency
        
        # Timeliness check
        timeliness = 0.85  # Mock timeliness
        
        # Validity check
        validity = 0.88  # Mock validity
        
        # Uniqueness check
        duplicates = df.duplicated().sum()
        uniqueness = (total_cells - duplicates) / total_cells
        
        # Overall score
        overall_score = (completeness + accuracy + consistency + timeliness + validity + uniqueness) / 6
        
        quality_metrics = DataQualityMetrics(
            completeness=completeness,
            accuracy=accuracy,
            consistency=consistency,
            timeliness=timeliness,
            validity=validity,
            uniqueness=uniqueness,
            overall_score=overall_score,
            timestamp=datetime.now()
        )
        
        self.quality_metrics.append(quality_metrics)
        self.logger.info(f"Data validation completed. Overall score: {overall_score:.3f}")
        
        return quality_metrics
    
    def detect_data_drift(self, new_data: pd.DataFrame, reference_data: pd.DataFrame) -> Dict[str, float]:
        """Ma'lumotlar driftini aniqlash"""
        self.logger.info("Detecting data drift")
        
        drift_scores = {}
        
        numeric_columns = new_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in reference_data.columns:
                # Simple statistical drift detection
                new_mean = new_data[col].mean()
                new_std = new_data[col].std()
                ref_mean = reference_data[col].mean()
                ref_std = reference_data[col].std()
                
                # Calculate drift score
                mean_shift = abs(new_mean - ref_mean) / (ref_std + 1e-8)
                std_shift = abs(new_std - ref_std) / (ref_std + 1e-8)
                
                drift_scores[col] = (mean_shift + std_shift) / 2
        
        # Overall drift score
        overall_drift = np.mean(list(drift_scores.values())) if drift_scores else 0
        
        self.logger.info(f"Data drift detection completed. Overall drift: {overall_drift:.3f}")
        return {
            'feature_drifts': drift_scores,
            'overall_drift': overall_drift,
            'timestamp': datetime.now()
        }

class ModelTrainer:
    """Avtomatik model o'qitish va optimizatsiya"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.performance_history = []
        
    def automated_model_selection(self, X: pd.DataFrame, y: pd.Series, task_type: str = 'regression') -> List[str]:
        """Avtomatik model tanlash"""
        self.logger.info("Starting automated model selection")
        
        candidate_models = []
        
        if task_type == 'regression':
            candidate_models = [
                'LinearRegression',
                'Ridge',
                'Lasso',
                'RandomForestRegressor',
                'GradientBoostingRegressor'
            ]
            
            if ADVANCED_ML_AVAILABLE:
                candidate_models.extend(['XGBRegressor', 'LGBMRegressor'])
        
        # Evaluate models using cross-validation
        model_scores = {}
        
        for model_name in candidate_models:
            try:
                model = self._create_model(model_name)
                scores = cross_val_score(model, X, y, cv=5, scoring='r2')
                model_scores[model_name] = scores.mean()
            except Exception as e:
                self.logger.warning(f"Failed to evaluate {model_name}: {e}")
        
        # Select top models
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        top_models = [model[0] for model in sorted_models[:3]]
        
        self.logger.info(f"Selected top models: {top_models}")
        return top_models
    
    def _create_model(self, model_name: str):
        """Model obyektini yaratish"""
        models = {
            'LinearRegression': LinearRegression(),
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=1.0),
            'RandomForestRegressor': RandomForestRegressor(n_estimators=100, random_state=42),
            'GradientBoostingRegressor': GradientBoostingRegressor(n_estimators=100, random_state=42),
        }
        
        if ADVANCED_ML_AVAILABLE:
            models.update({
                'XGBRegressor': xgb.XGBRegressor(n_estimators=100, random_state=42),
                'LGBMRegressor': lgb.LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)
            })
        
        return models.get(model_name, LinearRegression())
    
    def hyperparameter_optimization(self, model_name: str, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Giperparametrlarni optimizatsiya qilish"""
        self.logger.info(f"Starting hyperparameter optimization for {model_name}")
        
        param_grids = {
            'RandomForestRegressor': {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10]
            },
            'GradientBoostingRegressor': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            }
        }
        
        if ADVANCED_ML_AVAILABLE:
            param_grids.update({
                'XGBRegressor': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                },
                'LGBMRegressor': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                }
            })
        
        model = self._create_model(model_name)
        param_grid = param_grids.get(model_name, {})
        
        if not param_grid:
            self.logger.warning(f"No hyperparameter grid for {model_name}")
            return {}
        
        try:
            grid_search = GridSearchCV(
                model, param_grid, cv=3, scoring='r2', n_jobs=-1
            )
            grid_search.fit(X, y)
            
            self.logger.info(f"Best parameters for {model_name}: {grid_search.best_params_}")
            return grid_search.best_params_
            
        except Exception as e:
            self.logger.error(f"Hyperparameter optimization failed for {model_name}: {e}")
            return {}
    
    def train_ensemble(self, X: pd.DataFrame, y: pd.Series, model_names: List[str]) -> Dict[str, Any]:
        """Model ensembling"""
        self.logger.info(f"Starting ensemble training with models: {model_names}")
        
        ensemble_predictions = []
        individual_models = {}
        
        for model_name in model_names:
            try:
                # Get best hyperparameters
                best_params = self.hyperparameter_optimization(model_name, X, y)
                model = self._create_model(model_name)
                
                if best_params:
                    model.set_params(**best_params)
                
                # Train model
                model.fit(X, y)
                predictions = model.predict(X)
                
                ensemble_predictions.append(predictions)
                individual_models[model_name] = {
                    'model': model,
                    'predictions': predictions,
                    'performance': self._evaluate_model(y, predictions)
                }
                
                self.logger.info(f"Trained {model_name} with performance: {individual_models[model_name]['performance']['r2']:.3f}")
                
            except Exception as e:
                self.logger.error(f"Failed to train {model_name}: {e}")
        
        # Simple averaging ensemble
        if ensemble_predictions:
            ensemble_pred = np.mean(ensemble_predictions, axis=0)
            ensemble_performance = self._evaluate_model(y, ensemble_pred)
            
            self.logger.info(f"Ensemble performance: {ensemble_performance['r2']:.3f}")
            return {
                'individual_models': individual_models,
                'ensemble_predictions': ensemble_pred,
                'ensemble_performance': ensemble_performance
            }
        
        return {}
    
    def _evaluate_model(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """Model performance baholash"""
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred)
        }
    
    def model_versioning(self, model: Any, model_name: str, version: str, metadata: Dict[str, Any]) -> str:
        """Model versiyasini boshqarish"""
        model_path = Path(f"models/{model_name}_{version}.pkl")
        model_path.parent.mkdir(exist_ok=True)
        
        # Save model
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata_path = Path(f"models/{model_name}_{version}_metadata.json")
        metadata.update({
            'model_name': model_name,
            'version': version,
            'created_at': datetime.now().isoformat(),
            'file_path': str(model_path)
        })
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Model {model_name} v{version} saved successfully")
        return str(model_path)

class RetrainingManager:
    """Qayta o'qitish boshqaruvi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.triggers = []
        self.thresholds = config.get('retraining_thresholds', {})
        
    def check_performance_degradation(self, current_performance: float, baseline_performance: float) -> Optional[RetrainingTrigger]:
        """Performance paslashishini tekshirish"""
        degradation_threshold = self.thresholds.get('performance_degradation', 0.05)
        
        if current_performance < baseline_performance * (1 - degradation_threshold):
            return RetrainingTrigger(
                trigger_type='performance_degradation',
                trigger_value=current_performance,
                threshold=baseline_performance * (1 - degradation_threshold),
                severity='high' if current_performance < baseline_performance * 0.9 else 'medium',
                timestamp=datetime.now(),
                description=f"Performance dropped from {baseline_performance:.3f} to {current_performance:.3f}"
            )
        return None
    
    def check_data_drift(self, drift_score: float) -> Optional[RetrainingTrigger]:
        """Ma'lumotlar driftini tekshirish"""
        drift_threshold = self.thresholds.get('data_drift', 0.3)
        
        if drift_score > drift_threshold:
            return RetrainingTrigger(
                trigger_type='data_drift',
                trigger_value=drift_score,
                threshold=drift_threshold,
                severity='high' if drift_score > 0.5 else 'medium',
                timestamp=datetime.now(),
                description=f"Data drift detected: {drift_score:.3f}"
            )
        return None
    
    def check_scheduled_retraining(self) -> Optional[RetrainingTrigger]:
        """Reja bo'yicha qayta o'qitishni tekshirish"""
        retrain_frequency = self.thresholds.get('retrain_frequency_days', 30)
        last_retrain = self.thresholds.get('last_retrain_date', datetime.now() - timedelta(days=retrain_frequency + 1))
        
        if datetime.now() - last_retrain > timedelta(days=retrain_frequency):
            return RetrainingTrigger(
                trigger_type='scheduled_retraining',
                trigger_value=0,
                threshold=retrain_frequency,
                severity='low',
                timestamp=datetime.now(),
                description=f"Scheduled retraining after {retrain_frequency} days"
            )
        return None
    
    def check_market_regime_changes(self, market_data: Dict[str, float]) -> Optional[RetrainingTrigger]:
        """Bozor rejimlari o'zgarishini tekshirish"""
        # Mock implementation
        regime_change_threshold = self.thresholds.get('regime_change', 0.2)
        
        # Check volatility change
        if 'volatility_change' in market_data:
            volatility_change = abs(market_data['volatility_change'])
            if volatility_change > regime_change_threshold:
                return RetrainingTrigger(
                    trigger_type='market_regime_change',
                    trigger_value=volatility_change,
                    threshold=regime_change_threshold,
                    severity='high' if volatility_change > 0.4 else 'medium',
                    timestamp=datetime.now(),
                    description=f"Market regime change detected: {volatility_change:.3f}"
                )
        return None

class ABTesting:
    """Model A/B testing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.test_results = []
    
    def create_test(self, control_model: Any, test_model: Any, test_name: str, 
                   traffic_split: float = 0.1) -> Dict[str, Any]:
        """A/B test yaratish"""
        self.logger.info(f"Creating A/B test: {test_name}")
        
        test_config = {
            'test_name': test_name,
            'control_model': control_model,
            'test_model': test_model,
            'traffic_split': traffic_split,
            'status': 'running',
            'start_time': datetime.now(),
            'results': {}
        }
        
        self.test_results.append(test_config)
        return test_config
    
    def evaluate_test(self, test_config: Dict[str, Any], control_metrics: Dict[str, float], 
                     test_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Test natijalarini baholash"""
        # Statistical significance test
        improvement = {}
        for metric in control_metrics:
            if metric in test_metrics:
                change = (test_metrics[metric] - control_metrics[metric]) / control_metrics[metric]
                improvement[metric] = change
        
        # Decision logic
        is_significant = all(change > 0.05 for change in improvement.values())  # 5% improvement threshold
        
        test_config['results'] = {
            'control_metrics': control_metrics,
            'test_metrics': test_metrics,
            'improvement': improvement,
            'is_significant': is_significant,
            'evaluation_time': datetime.now()
        }
        
        if is_significant:
            test_config['status'] = 'passed'
            self.logger.info(f"A/B test {test_config['test_name']} PASSED")
        else:
            test_config['status'] = 'failed'
            self.logger.info(f"A/B test {test_config['test_name']} FAILED")
        
        return test_config['results']

class ModelMonitoring:
    """Model monitoring va performance kuzatish"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.monitoring_data = []
        
    def monitor_model_performance(self, model_name: str, predictions: np.ndarray, 
                                actuals: np.Series, timestamp: datetime) -> Dict[str, float]:
        """Model performance kuzatish"""
        metrics = {
            'mse': mean_squared_error(actuals, predictions),
            'mae': mean_absolute_error(actuals, predictions),
            'r2': r2_score(actuals, predictions),
            'timestamp': timestamp,
            'model_name': model_name
        }
        
        self.monitoring_data.append(metrics)
        self.logger.info(f"Model {model_name} performance: R2={metrics['r2']:.3f}, MAE={metrics['mae']:.3f}")
        
        return metrics
    
    def detect_performance_drift(self, model_name: str, window_size: int = 100) -> Dict[str, float]:
        """Performance drift aniqlash"""
        model_data = [m for m in self.monitoring_data if m['model_name'] == model_name]
        
        if len(model_data) < window_size:
            return {'drift_score': 0, 'status': 'insufficient_data'}
        
        recent_metrics = model_data[-window_size:]
        baseline_metrics = model_data[-2*window_size:-window_size] if len(model_data) >= 2*window_size else model_data[:window_size]
        
        # Calculate drift in performance metrics
        r2_drift = abs(np.mean([m['r2'] for m in recent_metrics]) - np.mean([m['r2'] for m in baseline_metrics]))
        mae_drift = abs(np.mean([m['mae'] for m in recent_metrics]) - np.mean([m['mae'] for m in baseline_metrics]))
        
        overall_drift = (r2_drift + mae_drift) / 2
        
        return {
            'drift_score': overall_drift,
            'r2_drift': r2_drift,
            'mae_drift': mae_drift,
            'status': 'high_drift' if overall_drift > 0.1 else 'normal_drift'
        }

class OnlineLearning:
    """Online learning algoritmlar"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.scaler = StandardScaler()
        
    def incremental_training(self, X_batch: pd.DataFrame, y_batch: pd.Series) -> Dict[str, float]:
        """Inkremental o'qitish"""
        if self.model is None:
            self.model = Ridge(alpha=1.0)
            # Initial fit
            X_scaled = self.scaler.fit_transform(X_batch)
            self.model.fit(X_scaled, y_batch)
        else:
            # Incremental update (simplified)
            X_scaled = self.scaler.transform(X_batch)
            
            # For Ridge regression, we can do partial updates
            # This is a simplified approach
            predictions = self.model.predict(X_scaled)
            residuals = y_batch - predictions
            
            # Update model parameters (simplified)
            learning_rate = self.config.get('learning_rate', 0.01)
            n_features = X_scaled.shape[1]
            
            # Simplified gradient update
            gradient = np.dot(X_scaled.T, residuals) / len(X_batch)
            self.model.coef_ += learning_rate * gradient
        
        # Evaluate
        X_scaled = self.scaler.transform(X_batch)
        predictions = self.model.predict(X_scaled)
        performance = {
            'mse': mean_squared_error(y_batch, predictions),
            'r2': r2_score(y_batch, predictions)
        }
        
        self.logger.info(f"Incremental training completed. Performance: {performance}")
        return performance

class FederatedLearning:
    """Federated learning"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.local_models = {}
        self.global_model = None
        
    def register_client(self, client_id: str) -> None:
        """Client ro'yxatga olish"""
        self.local_models[client_id] = {
            'model_state': None,
            'data_count': 0,
            'last_update': datetime.now()
        }
        self.logger.info(f"Client {client_id} registered for federated learning")
    
    def local_training(self, client_id: str, X_local: pd.DataFrame, y_local: pd.Series) -> Dict[str, Any]:
        """Lokal model o'qitish"""
        if client_id not in self.local_models:
            self.register_client(client_id)
        
        # Local model training
        local_model = Ridge(alpha=1.0)
        local_model.fit(X_local, y_local)
        
        # Store model state
        self.local_models[client_id]['model_state'] = local_model.coef_
        self.local_models[client_id]['data_count'] = len(X_local)
        self.local_models[client_id]['last_update'] = datetime.now()
        
        # Evaluate local model
        predictions = local_model.predict(X_local)
        performance = {
            'mse': mean_squared_error(y_local, predictions),
            'r2': r2_score(y_local, predictions)
        }
        
        self.logger.info(f"Local training completed for client {client_id}")
        return {
            'model_state': local_model.coef_,
            'data_count': len(X_local),
            'performance': performance
        }
    
    def aggregate_models(self) -> Dict[str, np.ndarray]:
        """Modellarni agregatsiya qilish"""
        self.logger.info("Aggregating federated models")
        
        total_weight = 0
        weighted_coefficients = None
        
        for client_id, client_data in self.local_models.items():
            if client_data['model_state'] is not None:
                weight = client_data['data_count']
                total_weight += weight
                
                if weighted_coefficients is None:
                    weighted_coefficients = weight * client_data['model_state']
                else:
                    weighted_coefficients += weight * client_data['model_state']
        
        if total_weight > 0 and weighted_coefficients is not None:
            global_coefficients = weighted_coefficients / total_weight
            
            # Create global model
            self.global_model = Ridge(alpha=1.0)
            self.global_model.coef_ = global_coefficients
            
            self.logger.info("Federated aggregation completed")
            return {
                'global_coefficients': global_coefficients,
                'total_clients': len([c for c in self.local_models.values() if c['model_state'] is not None]),
                'total_samples': total_weight
            }
        
        return {}

class TrainingPipeline:
    """Asosiy o'qitish pipeline"""
    
    def __init__(self, config_path: str = "config/training_config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize components
        self.data_pipeline = DataPipeline(self.config)
        self.model_trainer = ModelTrainer(self.config)
        self.retraining_manager = RetrainingManager(self.config)
        self.ab_testing = ABTesting(self.config)
        self.model_monitoring = ModelMonitoring(self.config)
        self.online_learning = OnlineLearning(self.config)
        self.federated_learning = FederatedLearning(self.config)
        
        self.logger.info("Training Pipeline initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Konfiguratsiyani yuklash"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                "data_sources": ["api", "database", "file"],
                "model_types": ["regression", "classification"],
                "retraining_thresholds": {
                    "performance_degradation": 0.05,
                    "data_drift": 0.3,
                    "retrain_frequency_days": 30,
                    "regime_change": 0.2
                },
                "model_versioning": {
                    "save_path": "models/",
                    "backup_enabled": True
                },
                "monitoring": {
                    "metrics": ["accuracy", "precision", "recall", "f1"],
                    "alert_threshold": 0.1
                }
            }
    
    def _setup_logging(self) -> logging.Logger:
        """Logging sozlamalari"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def run_full_pipeline(self) -> Dict[str, Any]:
        """To'liq pipeline ishga tushirish"""
        self.logger.info("Starting full training pipeline")
        
        results = {
            'pipeline_start': datetime.now(),
            'stages': {},
            'errors': [],
            'final_model': None
        }
        
        try:
            # Stage 1: Data Collection
            self.logger.info("Stage 1: Data Collection")
            data = await self.data_pipeline.collect_real_time_data("default_source")
            results['stages']['data_collection'] = {'status': 'completed', 'records': len(data)}
            
            # Stage 2: Data Preprocessing
            self.logger.info("Stage 2: Data Preprocessing")
            df_processed = self.data_pipeline.preprocess_data(data)
            results['stages']['preprocessing'] = {'status': 'completed', 'features': len(df_processed.columns)}
            
            # Stage 3: Feature Engineering
            self.logger.info("Stage 3: Feature Engineering")
            df_engineered = self.data_pipeline.feature_engineering(df_processed)
            results['stages']['feature_engineering'] = {'status': 'completed', 'features': len(df_engineered.columns)}
            
            # Stage 4: Feature Selection
            self.logger.info("Stage 4: Feature Selection")
            target_col = 'target' if 'target' in df_engineered.columns else df_engineered.columns[-1]
            df_selected = self.data_pipeline.feature_selection(df_engineered, target_col)
            results['stages']['feature_selection'] = {'status': 'completed', 'features': len(df_selected.columns)}
            
            # Stage 5: Data Validation
            self.logger.info("Stage 5: Data Validation")
            quality_metrics = self.data_pipeline.validate_data(df_selected)
            results['stages']['validation'] = {'status': 'completed', 'quality_score': quality_metrics.overall_score}
            
            # Stage 6: Model Training
            self.logger.info("Stage 6: Model Training")
            X = df_selected.drop(columns=[target_col])
            y = df_selected[target_col]
            
            selected_models = self.model_trainer.automated_model_selection(X, y, 'regression')
            ensemble_results = self.model_trainer.train_ensemble(X, y, selected_models)
            results['stages']['model_training'] = {'status': 'completed', 'models_trained': len(selected_models)}
            
            # Stage 7: Model Versioning
            self.logger.info("Stage 7: Model Versioning")
            best_model_name = max(ensemble_results.get('individual_models', {}).keys(), 
                                key=lambda k: ensemble_results['individual_models'][k]['performance']['r2'])
            best_model = ensemble_results['individual_models'][best_model_name]['model']
            
            version = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model_path = self.model_trainer.model_versioning(
                best_model, 
                best_model_name, 
                version, 
                {'accuracy': ensemble_results['individual_models'][best_model_name]['performance']['r2']}
            )
            results['final_model'] = model_path
            results['stages']['model_versioning'] = {'status': 'completed', 'model_path': model_path}
            
            # Stage 8: Monitoring Setup
            self.logger.info("Stage 8: Monitoring Setup")
            test_predictions = best_model.predict(X[:10])  # Test with small batch
            monitoring_results = self.model_monitoring.monitor_model_performance(
                best_model_name, test_predictions, y[:10], datetime.now()
            )
            results['stages']['monitoring'] = {'status': 'completed', 'metrics': monitoring_results}
            
            results['pipeline_end'] = datetime.now()
            results['total_duration'] = (results['pipeline_end'] - results['pipeline_start']).total_seconds()
            
            self.logger.info(f"Pipeline completed successfully in {results['total_duration']:.2f} seconds")
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            results['errors'].append(str(e))
            results['pipeline_end'] = datetime.now()
        
        return results
    
    async def retrain_if_needed(self, current_performance: float, baseline_performance: float, 
                              drift_score: float, market_data: Dict[str, float]) -> bool:
        """Agar kerak bo'lsa qayta o'qitish"""
        triggers = []
        
        # Check various triggers
        performance_trigger = self.retraining_manager.check_performance_degradation(
            current_performance, baseline_performance)
        if performance_trigger:
            triggers.append(performance_trigger)
        
        drift_trigger = self.retraining_manager.check_data_drift(drift_score)
        if drift_trigger:
            triggers.append(drift_trigger)
        
        scheduled_trigger = self.retraining_manager.check_scheduled_retraining()
        if scheduled_trigger:
            triggers.append(scheduled_trigger)
        
        regime_trigger = self.retraining_manager.check_market_regime_changes(market_data)
        if regime_trigger:
            triggers.append(regime_trigger)
        
        # Determine if retraining is needed
        high_priority_triggers = [t for t in triggers if t.severity == 'high']
        if high_priority_triggers:
            self.logger.info(f"Retraining triggered by {len(high_priority_triggers)} high-priority events")
            
            # Run pipeline
            results = await self.run_full_pipeline()
            
            if not results.get('errors'):
                self.logger.info("Retraining completed successfully")
                self.retraining_manager.triggers.extend(triggers)
                return True
            else:
                self.logger.error(f"Retraining failed: {results['errors']}")
                return False
        
        return False
    
    def explain_model(self, model: Any, feature_names: List[str]) -> Dict[str, float]:
        """Model tushuntirish (Explainable AI)"""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_importance = dict(zip(feature_names, importances))
            
            # Normalize importances
            total_importance = sum(importances)
            if total_importance > 0:
                feature_importance = {k: v/total_importance for k, v in feature_importance.items()}
            
            return {
                'feature_importance': feature_importance,
                'top_features': sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        
        # Fallback: SHAP-like explanation (simplified)
        if hasattr(model, 'coef_'):
            coefficients = model.coef_
            feature_importance = dict(zip(feature_names, np.abs(coefficients)))
            
            # Normalize
            total_importance = sum(np.abs(coefficients))
            if total_importance > 0:
                feature_importance = {k: v/total_importance for k, v in feature_importance.items()}
            
            return {
                'feature_importance': feature_importance,
                'top_features': sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        
        return {'error': 'Model explanation not available for this model type'}
    
    def detect_bias(self, predictions: np.ndarray, actuals: pd.Series, sensitive_features: pd.DataFrame) -> Dict[str, float]:
        """Model biasini aniqlash"""
        bias_metrics = {}
        
        for column in sensitive_features.columns:
            unique_groups = sensitive_features[column].unique()
            group_metrics = {}
            
            for group in unique_groups:
                group_mask = sensitive_features[column] == group
                group_predictions = predictions[group_mask]
                group_actuals = actuals[group_mask]
                
                if len(group_actuals) > 0:
                    group_metrics[group] = {
                        'mean_prediction': np.mean(group_predictions),
                        'mean_actual': np.mean(group_actuals),
                        'bias': np.mean(group_predictions) - np.mean(group_actuals)
                    }
            
            # Calculate overall bias
            group_biases = [metrics['bias'] for metrics in group_metrics.values()]
            bias_metrics[column] = {
                'group_metrics': group_metrics,
                'max_bias': max(group_biases) if group_biases else 0,
                'min_bias': min(group_biases) if group_biases else 0,
                'bias_range': max(group_biases) - min(group_biases) if group_biases else 0
            }
        
        return bias_metrics

# Main execution
if __name__ == "__main__":
    async def main():
        """Test va demo"""
        config = {
            "retraining_thresholds": {
                "performance_degradation": 0.05,
                "data_drift": 0.3,
                "retrain_frequency_days": 7
            }
        }
        
        pipeline = TrainingPipeline()
        
        # Test full pipeline
        results = await pipeline.run_full_pipeline()
        print("\nPipeline Results:")
        print(f"Status: {'SUCCESS' if not results.get('errors') else 'FAILED'}")
        print(f"Duration: {results.get('total_duration', 0):.2f} seconds")
        print(f"Final Model: {results.get('final_model', 'None')}")
        
        if results.get('errors'):
            print(f"Errors: {results['errors']}")
    
    # Run the demo
    asyncio.run(main())