"""
Machine Learning Models for Trading
ML Models Engine - Advanced Machine Learning for Financial Markets

Features:
- Time Series Forecasting Models
- Classification Models (Trend Direction)
- Ensemble Methods
- Deep Learning Models
- Feature Engineering
- Model Validation & Backtesting
- AutoML Support
- Model Interpretability
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from decimal import Decimal, ROUND_DOWN
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Core ML Libraries
from sklearn.base import BaseEstimator, RegressorMixin, ClassifierMixin
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.model_selection import (
    train_test_split, cross_val_score, TimeSeriesSplit, 
    GridSearchCV, RandomizedSearchCV
)
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, 
    LabelEncoder, OneHotEncoder, PolynomialFeatures
)
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

# Advanced ML
from sklearn.ensemble import (
    VotingRegressor, VotingClassifier, 
    BaggingRegressor, BaggingClassifier,
    AdaBoostRegressor, AdaBoostClassifier
)
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier

# Deep Learning
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Time Series
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

# Feature Selection
from sklearn.feature_selection import (
    SelectKBest, f_regression, f_classif, 
    RFE, SelectFromModel, VarianceThreshold
)

# Dimensionality Reduction
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE

# Clustering
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering

# Interpretability
import shap
from lime.lime_tabular import LimeTabularExplainer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Machine Learning model turlari"""
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    TIME_SERIES = "time_series"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"

class ModelStatus(Enum):
    """Model holati"""
    TRAINING = "training"
    READY = "ready"
    VALIDATING = "validating"
    DEPLOYED = "deployed"
    OBSOLETE = "obsolete"

@dataclass
class ModelMetrics:
    """Model performance metrikalari"""
    model_type: ModelType
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mse: Optional[float] = None
    mae: Optional[float] = None
    r2_score: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    
    # Time series specific
    directional_accuracy: Optional[float] = None
    mean_directional_error: Optional[float] = None
    
    # Cross-validation
    cv_score_mean: Optional[float] = None
    cv_score_std: Optional[float] = None
    
    # Training info
    training_time: float = 0
    feature_count: int = 0
    sample_count: int = 0

@dataclass
class FeatureImportance:
    """Feature importance natijasi"""
    feature_name: str
    importance_score: float
    importance_type: str = "shap"  # shap, permutation, built-in

@dataclass
class PredictionResult:
    """Prediction natijasi"""
    prediction: Union[float, int, str, List]
    confidence: float
    model_name: str
    timestamp: datetime
    feature_importance: List[FeatureImportance] = field(default_factory=list)
    explanation: Optional[str] = None

class TimeSeriesNet(nn.Module):
    """LSTM network for time series prediction"""
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.2):
        super(TimeSeriesNet, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc2 = nn.Linear(hidden_size // 2, output_size)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.dropout(out[:, -1, :])  # Take last output
        out = self.relu(self.fc1(out))
        out = self.fc2(out)
        return out

class MLModelsEngine:
    """Machine Learning Models Engine"""
    
    def __init__(self, model_dir: str = "/workspace/ml_models"):
        """
        Args:
            model_dir: Model storage directory
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True, parents=True)
        
        # Model storage
        self.models = {}
        self.scalers = {}
        self.feature_encoders = {}
        self.model_metadata = {}
        
        # Feature store
        self.feature_importance_store = {}
        self.prediction_history = []
        
        # AutoML components
        self.auto_ml_enabled = True
        self.feature_selection_threshold = 0.01
        
        logger.info("ML Models Engine initialized")
    
    async def create_regression_model(self, 
                                    name: str,
                                    model_type: str = "random_forest",
                                    hyperparameters: Optional[Dict] = None) -> BaseEstimator:
        """
        Regression model yaratish
        
        Args:
            name: Model nomi
            model_type: Model turi (random_forest, xgboost, svr, etc.)
            hyperparameters: Model hyperparameters
            
        Returns:
            Trained regression model
        """
        try:
            logger.info(f"Creating regression model: {name} ({model_type})")
            
            # Default hyperparameters
            if hyperparameters is None:
                hyperparameters = {}
            
            # Create model based on type
            if model_type == "random_forest":
                model = RandomForestRegressor(
                    n_estimators=hyperparameters.get('n_estimators', 100),
                    max_depth=hyperparameters.get('max_depth', 10),
                    min_samples_split=hyperparameters.get('min_samples_split', 2),
                    random_state=42
                )
            elif model_type == "xgboost":
                model = XGBRegressor(
                    n_estimators=hyperparameters.get('n_estimators', 100),
                    max_depth=hyperparameters.get('max_depth', 6),
                    learning_rate=hyperparameters.get('learning_rate', 0.1),
                    random_state=42
                )
            elif model_type == "svr":
                model = SVR(
                    kernel=hyperparameters.get('kernel', 'rbf'),
                    C=hyperparameters.get('C', 1.0),
                    gamma=hyperparameters.get('gamma', 'scale')
                )
            elif model_type == "linear":
                model = LinearRegression()
            elif model_type == "gradient_boosting":
                model = GradientBoostingRegressor(
                    n_estimators=hyperparameters.get('n_estimators', 100),
                    learning_rate=hyperparameters.get('learning_rate', 0.1),
                    max_depth=hyperparameters.get('max_depth', 3),
                    random_state=42
                )
            else:
                raise ValueError(f"Unknown regression model type: {model_type}")
            
            # Store model
            self.models[name] = model
            self.model_metadata[name] = {
                'type': ModelType.REGRESSION,
                'model_type': model_type,
                'created_at': datetime.now(),
                'status': ModelStatus.READY
            }
            
            logger.info(f"Regression model {name} created successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create regression model {name}: {e}")
            raise
    
    async def create_classification_model(self, 
                                        name: str,
                                        model_type: str = "random_forest",
                                        hyperparameters: Optional[Dict] = None) -> BaseEstimator:
        """
        Classification model yaratish
        
        Args:
            name: Model nomi
            model_type: Model turi
            hyperparameters: Model hyperparameters
            
        Returns:
            Trained classification model
        """
        try:
            logger.info(f"Creating classification model: {name} ({model_type})")
            
            if hyperparameters is None:
                hyperparameters = {}
            
            # Create model based on type
            if model_type == "random_forest":
                model = RandomForestClassifier(
                    n_estimators=hyperparameters.get('n_estimators', 100),
                    max_depth=hyperparameters.get('max_depth', 10),
                    min_samples_split=hyperparameters.get('min_samples_split', 2),
                    random_state=42
                )
            elif model_type == "xgboost":
                model = XGBClassifier(
                    n_estimators=hyperparameters.get('n_estimators', 100),
                    max_depth=hyperparameters.get('max_depth', 6),
                    learning_rate=hyperparameters.get('learning_rate', 0.1),
                    random_state=42
                )
            elif model_type == "svm":
                model = SVC(
                    kernel=hyperparameters.get('kernel', 'rbf'),
                    C=hyperparameters.get('C', 1.0),
                    gamma=hyperparameters.get('gamma', 'scale'),
                    probability=True
                )
            elif model_type == "logistic":
                model = LogisticRegression(
                    C=hyperparameters.get('C', 1.0),
                    random_state=42
                )
            elif model_type == "naive_bayes":
                model = GaussianNB()
            else:
                raise ValueError(f"Unknown classification model type: {model_type}")
            
            # Store model
            self.models[name] = model
            self.model_metadata[name] = {
                'type': ModelType.CLASSIFICATION,
                'model_type': model_type,
                'created_at': datetime.now(),
                'status': ModelStatus.READY
            }
            
            logger.info(f"Classification model {name} created successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create classification model {name}: {e}")
            raise
    
    async def create_ensemble_model(self,
                                  name: str,
                                  models: List[str],
                                  ensemble_type: str = "voting") -> BaseEstimator:
        """
        Ensemble model yaratish
        
        Args:
            name: Ensemble model nomi
            models: Base model nomlari
            ensemble_type: Ensemble turi (voting, bagging, boosting)
            
        Returns:
            Ensemble model
        """
        try:
            logger.info(f"Creating ensemble model: {name} with {len(models)} base models")
            
            # Get base models
            base_models = []
            model_types = []
            
            for model_name in models:
                if model_name not in self.models:
                    raise ValueError(f"Base model {model_name} not found")
                
                base_models.append((model_name, self.models[model_name]))
                model_types.append(self.model_metadata[model_name]['type'])
            
            # Check all models are same type
            if len(set(model_types)) > 1:
                raise ValueError("All base models must be same type (all regression or all classification)")
            
            model_type = model_types[0]
            
            # Create ensemble
            if ensemble_type == "voting":
                if model_type == ModelType.REGRESSION:
                    ensemble = VotingRegressor(estimators=base_models)
                else:
                    ensemble = VotingClassifier(estimators=base_models)
            elif ensemble_type == "bagging":
                # BaggingClassifier/Regressor with multiple base models
                if model_type == ModelType.REGRESSION:
                    ensemble = BaggingRegressor(
                        estimator=RandomForestRegressor(random_state=42),
                        n_estimators=len(models),
                        random_state=42
                    )
                else:
                    ensemble = BaggingClassifier(
                        estimator=RandomForestClassifier(random_state=42),
                        n_estimators=len(models),
                        random_state=42
                    )
            elif ensemble_type == "boosting":
                if model_type == ModelType.REGRESSION:
                    ensemble = AdaBoostRegressor(
                        estimator=DecisionTreeRegressor(max_depth=3),
                        n_estimators=len(models),
                        random_state=42
                    )
                else:
                    ensemble = AdaBoostClassifier(
                        estimator=DecisionTreeClassifier(max_depth=3),
                        n_estimators=len(models),
                        random_state=42
                    )
            else:
                raise ValueError(f"Unknown ensemble type: {ensemble_type}")
            
            # Store ensemble
            self.models[name] = ensemble
            self.model_metadata[name] = {
                'type': model_type,
                'model_type': f"ensemble_{ensemble_type}",
                'base_models': models,
                'created_at': datetime.now(),
                'status': ModelStatus.READY
            }
            
            logger.info(f"Ensemble model {name} created successfully")
            return ensemble
            
        except Exception as e:
            logger.error(f"Failed to create ensemble model {name}: {e}")
            raise
    
    async def create_lstm_model(self,
                              name: str,
                              input_size: int,
                              hidden_size: int = 64,
                              num_layers: int = 2,
                              output_size: int = 1,
                              dropout: float = 0.2) -> TimeSeriesNet:
        """
        LSTM model yaratish
        
        Args:
            name: Model nomi
            input_size: Input feature count
            hidden_size: LSTM hidden units
            num_layers: Number of LSTM layers
            output_size: Output size
            dropout: Dropout rate
            
        Returns:
            LSTM neural network model
        """
        try:
            logger.info(f"Creating LSTM model: {name}")
            
            model = TimeSeriesNet(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                output_size=output_size,
                dropout=dropout
            )
            
            # Store model
            self.models[name] = model
            self.model_metadata[name] = {
                'type': ModelType.TIME_SERIES,
                'model_type': 'lstm',
                'input_size': input_size,
                'hidden_size': hidden_size,
                'num_layers': num_layers,
                'created_at': datetime.now(),
                'status': ModelStatus.READY
            }
            
            logger.info(f"LSTM model {name} created successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create LSTM model {name}: {e}")
            raise
    
    async def train_model(self,
                         model_name: str,
                         X: pd.DataFrame,
                         y: Union[pd.Series, np.ndarray],
                         test_size: float = 0.2,
                         cv_folds: int = 5,
                         scale_features: bool = True,
                         feature_selection: bool = False) -> ModelMetrics:
        """
        Model training
        
        Args:
            model_name: Model nomi
            X: Feature data
            y: Target data
            test_size: Test set size
            cv_folds: Cross-validation folds
            scale_features: Whether to scale features
            feature_selection: Whether to perform feature selection
            
        Returns:
            ModelMetrics: Training results
        """
        try:
            logger.info(f"Training model: {model_name}")
            
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[model_name]
            model_type = self.model_metadata[model_name]['type']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, 
                shuffle=False if model_type == ModelType.TIME_SERIES else True
            )
            
            # Feature scaling
            if scale_features:
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                self.scalers[model_name] = scaler
            else:
                X_train_scaled = X_train
                X_test_scaled = X_test
            
            # Feature selection
            selected_features = None
            if feature_selection and X_train_scaled.shape[1] > 10:
                if model_type == ModelType.REGRESSION:
                    selector = SelectKBest(score_func=f_regression, k=min(20, X_train_scaled.shape[1]))
                else:
                    selector = SelectKBest(score_func=f_classif, k=min(20, X_train_scaled.shape[1]))
                
                X_train_scaled = selector.fit_transform(X_train_scaled, y_train)
                X_test_scaled = selector.transform(X_test_scaled)
                selected_features = selector.get_support()
            
            # Train model
            start_time = datetime.now()
            
            if isinstance(model, TimeSeriesNet):
                # Deep learning training
                await self._train_deep_learning_model(model, X_train_scaled, y_train)
            else:
                # Traditional ML training
                model.fit(X_train_scaled, y_train)
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Evaluate model
            if model_type == ModelType.REGRESSION:
                y_pred = model.predict(X_test_scaled)
                
                metrics = ModelMetrics(
                    model_type=model_type,
                    mse=mean_squared_error(y_test, y_pred),
                    mae=mean_absolute_error(y_test, y_pred),
                    r2_score=r2_score(y_test, y_pred),
                    rmse=np.sqrt(mean_squared_error(y_test, y_pred)),
                    mape=np.mean(np.abs((y_test - y_pred) / y_test)) * 100,
                    training_time=training_time,
                    feature_count=X_train_scaled.shape[1],
                    sample_count=len(X_train)
                )
                
                # Cross-validation
                if cv_folds > 1 and not isinstance(model, TimeSeriesNet):
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, 
                                              cv=TimeSeriesSplit(n_splits=cv_folds) if model_type == ModelType.TIME_SERIES else cv_folds,
                                              scoring='neg_mean_squared_error')
                    metrics.cv_score_mean = -cv_scores.mean()
                    metrics.cv_score_std = cv_scores.std()
            
            else:  # Classification
                y_pred = model.predict(X_test_scaled)
                
                if hasattr(model, 'predict_proba'):
                    y_prob = model.predict_proba(X_test_scaled)
                else:
                    y_prob = None
                
                metrics = ModelMetrics(
                    model_type=model_type,
                    accuracy=accuracy_score(y_test, y_pred),
                    precision=precision_score(y_test, y_pred, average='weighted'),
                    recall=recall_score(y_test, y_pred, average='weighted'),
                    f1_score=f1_score(y_test, y_pred, average='weighted'),
                    training_time=training_time,
                    feature_count=X_train_scaled.shape[1],
                    sample_count=len(X_train)
                )
                
                # Directional accuracy for classification (if binary)
                if len(np.unique(y_test)) == 2:
                    metrics.directional_accuracy = accuracy_score(y_test, y_pred)
                
                # Cross-validation
                if cv_folds > 1 and not isinstance(model, TimeSeriesNet):
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, 
                                              cv=TimeSeriesSplit(n_splits=cv_folds) if model_type == ModelType.TIME_SERIES else cv_folds,
                                              scoring='accuracy')
                    metrics.cv_score_mean = cv_scores.mean()
                    metrics.cv_score_std = cv_scores.std()
            
            # Store metrics
            self.model_metadata[model_name]['metrics'] = metrics
            self.model_metadata[model_name]['status'] = ModelStatus.READY
            
            # Feature importance
            await self._calculate_feature_importance(model_name, X_train, y_train)
            
            logger.info(f"Model {model_name} trained successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to train model {model_name}: {e}")
            self.model_metadata[model_name]['status'] = ModelStatus.TRAINING
            raise
    
    async def _train_deep_learning_model(self, 
                                       model: TimeSeriesNet,
                                       X_train: np.ndarray,
                                       y_train: np.ndarray):
        """Deep learning model training"""
        try:
            # Convert to tensors
            X_tensor = torch.FloatTensor(X_train).unsqueeze(1)  # Add sequence dimension
            y_tensor = torch.FloatTensor(y_train).reshape(-1, 1)
            
            # Create data loader
            dataset = TensorDataset(X_tensor, y_tensor)
            dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
            
            # Training setup
            criterion = nn.MSELoss()
            optimizer = optim.Adam(model.parameters(), lr=0.001)
            
            # Training loop
            model.train()
            num_epochs = 100
            
            for epoch in range(num_epochs):
                total_loss = 0
                for batch_X, batch_y in dataloader:
                    optimizer.zero_grad()
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item()
                
                if (epoch + 1) % 20 == 0:
                    logger.info(f"Epoch {epoch+1}/{num_epochs}, Loss: {total_loss/len(dataloader):.4f}")
            
        except Exception as e:
            logger.error(f"Deep learning training failed: {e}")
            raise
    
    async def _calculate_feature_importance(self, 
                                          model_name: str,
                                          X: pd.DataFrame,
                                          y: pd.Series):
        """Feature importance hisoblash"""
        try:
            if model_name not in self.models:
                return
            
            model = self.models[model_name]
            feature_names = X.columns.tolist()
            
            # Built-in feature importance
            importance_scores = []
            
            if hasattr(model, 'feature_importances_'):
                # Tree-based models
                for i, importance in enumerate(model.feature_importances_):
                    if i < len(feature_names):
                        importance_scores.append(FeatureImportance(
                            feature_name=feature_names[i],
                            importance_score=importance,
                            importance_type="built-in"
                        ))
            
            elif hasattr(model, 'coef_'):
                # Linear models
                coefficients = np.abs(model.coef_)
                for i, coef in enumerate(coefficients):
                    if i < len(feature_names):
                        importance_scores.append(FeatureImportance(
                            feature_name=feature_names[i],
                            importance_score=float(coef),
                            importance_type="coefficient"
                        ))
            
            # SHAP values (if model supports it)
            try:
                if len(feature_names) <= 20:  # Only for smaller feature sets
                    explainer = shap.TreeExplainer(model) if hasattr(model, 'tree_') else shap.LinearExplainer(model, X)
                    shap_values = explainer.shap_values(X.sample(min(100, len(X))))
                    
                    for i, feature_name in enumerate(feature_names):
                        if i < shap_values.shape[1]:
                            importance_scores.append(FeatureImportance(
                                feature_name=feature_name,
                                importance_score=np.mean(np.abs(shap_values[:, i])),
                                importance_type="shap"
                            ))
            except Exception as e:
                logger.warning(f"SHAP calculation failed: {e}")
            
            # Store feature importance
            self.feature_importance_store[model_name] = sorted(
                importance_scores, 
                key=lambda x: x.importance_score, 
                reverse=True
            )
            
            logger.info(f"Feature importance calculated for {model_name}: {len(importance_scores)} features")
            
        except Exception as e:
            logger.error(f"Feature importance calculation failed: {e}")
    
    async def predict(self,
                     model_name: str,
                     X: pd.DataFrame,
                     return_confidence: bool = True) -> PredictionResult:
        """
        Model prediction
        
        Args:
            model_name: Model nomi
            X: Feature data
            return_confidence: Whether to return confidence scores
            
        Returns:
            PredictionResult: Prediction results
        """
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[model_name]
            
            # Apply scaling if available
            if model_name in self.scalers:
                X_scaled = self.scalers[model_name].transform(X)
            else:
                X_scaled = X.values
            
            # Make prediction
            if isinstance(model, TimeSeriesNet):
                # Deep learning model
                model.eval()
                with torch.no_grad():
                    X_tensor = torch.FloatTensor(X_scaled).unsqueeze(1)
                    predictions = model(X_tensor).numpy().flatten()
                    prediction = predictions[-1] if len(predictions) > 0 else 0
                    confidence = 0.8  # Default confidence for DL models
            else:
                # Traditional ML model
                prediction = model.predict(X_scaled)
                
                if len(prediction) == 1:
                    prediction = prediction[0]
                
                # Confidence calculation
                if return_confidence and hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(X_scaled)
                    confidence = float(np.max(probabilities))
                else:
                    confidence = 0.7  # Default confidence
            
            # Get feature importance for explanation
            feature_importance = self.feature_importance_store.get(model_name, [])
            
            # Create explanation
            explanation = self._generate_explanation(model_name, prediction, feature_importance)
            
            # Create result
            result = PredictionResult(
                prediction=prediction,
                confidence=confidence,
                model_name=model_name,
                timestamp=datetime.now(),
                feature_importance=feature_importance[:5],  # Top 5 features
                explanation=explanation
            )
            
            # Store in history
            self.prediction_history.append({
                'model_name': model_name,
                'prediction': prediction,
                'confidence': confidence,
                'timestamp': datetime.now(),
                'input_shape': X.shape
            })
            
            logger.info(f"Prediction made with {model_name}: {prediction:.4f} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed for {model_name}: {e}")
            raise
    
    def _generate_explanation(self, 
                            model_name: str, 
                            prediction: float, 
                            feature_importance: List[FeatureImportance]) -> str:
        """Prediction explanation generation"""
        try:
            top_features = feature_importance[:3]
            
            if top_features:
                feature_names = [f.feature_name for f in top_features]
                explanation = f"Prediction based on: {', '.join(feature_names)}"
                
                if isinstance(prediction, (int, float)):
                    if prediction > 0:
                        explanation += ". Positive signal detected."
                    else:
                        explanation += ". Negative signal detected."
                
                return explanation
            else:
                return "Prediction made using trained model features."
                
        except Exception as e:
            return "Unable to generate explanation"
    
    async def auto_ml_optimize(self,
                              X: pd.DataFrame,
                              y: Union[pd.Series, np.ndarray],
                              model_type: ModelType,
                              optimization_metric: str = "accuracy",
                              max_models: int = 10) -> str:
        """
        AutoML model optimization
        
        Args:
            X: Feature data
            y: Target data
            model_type: Model type (regression/classification)
            optimization_metric: Metric to optimize
            max_models: Maximum number of models to test
            
        Returns:
            Best model name
        """
        try:
            logger.info(f"Starting AutoML optimization for {model_type.value}")
            
            best_score = -np.inf
            best_model_name = None
            
            if model_type == ModelType.REGRESSION:
                models_to_test = [
                    ("rf_auto", RandomForestRegressor(random_state=42)),
                    ("xgb_auto", XGBRegressor(random_state=42)),
                    ("svr_auto", SVR()),
                    ("gb_auto", GradientBoostingRegressor(random_state=42)),
                    ("lr_auto", LinearRegression())
                ]
                
                scoring_metric = "neg_mean_squared_error"
                
            else:  # Classification
                models_to_test = [
                    ("rf_auto", RandomForestClassifier(random_state=42)),
                    ("xgb_auto", XGBClassifier(random_state=42)),
                    ("svm_auto", SVC(probability=True, random_state=42)),
                    ("lr_auto", LogisticRegression(random_state=42)),
                    ("nb_auto", GaussianNB())
                ]
                
                scoring_metric = "accuracy"
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Test models
            for model_name, model in models_to_test[:max_models]:
                try:
                    # Cross-validation
                    cv_scores = cross_val_score(
                        model, X_train_scaled, y_train, 
                        cv=5, scoring=scoring_metric
                    )
                    cv_mean = cv_scores.mean()
                    
                    # Fit and test
                    model.fit(X_train_scaled, y_train)
                    if model_type == ModelType.REGRESSION:
                        y_pred = model.predict(X_test_scaled)
                        test_score = r2_score(y_test, y_pred)
                    else:
                        y_pred = model.predict(X_test_scaled)
                        test_score = accuracy_score(y_test, y_pred)
                    
                    # Combined score
                    combined_score = (cv_mean + test_score) / 2
                    
                    logger.info(f"Model {model_name}: CV={cv_mean:.4f}, Test={test_score:.4f}, Combined={combined_score:.4f}")
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        best_model_name = model_name
                        
                        # Store best model
                        self.models[f"best_{model_name}"] = model
                        self.scalers[f"best_{model_name}"] = scaler
                        
                        self.model_metadata[f"best_{model_name}"] = {
                            'type': model_type,
                            'model_type': model_name,
                            'cv_score': cv_mean,
                            'test_score': test_score,
                            'combined_score': combined_score,
                            'created_at': datetime.now(),
                            'status': ModelStatus.READY,
                            'is_auto_ml': True
                        }
                
                except Exception as e:
                    logger.warning(f"Failed to test model {model_name}: {e}")
                    continue
            
            if best_model_name:
                final_name = f"best_{best_model_name}"
                logger.info(f"AutoML optimization completed. Best model: {final_name} (score: {best_score:.4f})")
                return final_name
            else:
                raise ValueError("No models passed optimization")
                
        except Exception as e:
            logger.error(f"AutoML optimization failed: {e}")
            raise
    
    async def save_model(self, model_name: str, filepath: Optional[str] = None):
        """Model saqlash"""
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            if filepath is None:
                filepath = self.model_dir / f"{model_name}.joblib"
            
            model = self.models[model_name]
            metadata = self.model_metadata[model_name]
            
            # Save model and metadata
            joblib.dump({
                'model': model,
                'metadata': metadata,
                'scaler': self.scalers.get(model_name),
                'feature_importance': self.feature_importance_store.get(model_name)
            }, filepath)
            
            logger.info(f"Model {model_name} saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save model {model_name}: {e}")
            raise
    
    async def load_model(self, model_name: str, filepath: Optional[str] = None):
        """Model yuklash"""
        try:
            if filepath is None:
                filepath = self.model_dir / f"{model_name}.joblib"
            
            loaded_data = joblib.load(filepath)
            
            self.models[model_name] = loaded_data['model']
            self.model_metadata[model_name] = loaded_data['metadata']
            
            if loaded_data.get('scaler'):
                self.scalers[model_name] = loaded_data['scaler']
            
            if loaded_data.get('feature_importance'):
                self.feature_importance_store[model_name] = loaded_data['feature_importance']
            
            logger.info(f"Model {model_name} loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    async def delete_model(self, model_name: str):
        """Model o'chirish"""
        try:
            if model_name in self.models:
                del self.models[model_name]
            
            if model_name in self.scalers:
                del self.scalers[model_name]
            
            if model_name in self.feature_importance_store:
                del self.feature_importance_store[model_name]
            
            if model_name in self.model_metadata:
                del self.model_metadata[model_name]
            
            # Delete file if exists
            filepath = self.model_dir / f"{model_name}.joblib"
            if filepath.exists():
                filepath.unlink()
            
            logger.info(f"Model {model_name} deleted successfully")
            
        except Exception as e:
            logger.error(f"Failed to delete model {model_name}: {e}")
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Model ma'lumotlari"""
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            info = self.model_metadata[model_name].copy()
            
            # Add current performance metrics if available
            if 'metrics' in info:
                metrics = info['metrics']
                info['performance'] = {
                    'accuracy': metrics.accuracy,
                    'r2_score': metrics.r2_score,
                    'mse': metrics.mse,
                    'cv_score_mean': metrics.cv_score_mean
                }
                del info['metrics']  # Remove dataclass object
            
            # Add feature importance
            if model_name in self.feature_importance_store:
                info['feature_importance'] = [
                    {
                        'feature': f.feature_name,
                        'importance': f.importance_score,
                        'type': f.importance_type
                    } for f in self.feature_importance_store[model_name][:10]
                ]
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get model info for {model_name}: {e}")
            return {}
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Barcha modellar ro'yxati"""
        try:
            models_list = []
            
            for name, metadata in self.model_metadata.items():
                model_info = {
                    'name': name,
                    'type': metadata.get('type', {}).value if hasattr(metadata.get('type', {}), 'value') else str(metadata.get('type')),
                    'model_type': metadata.get('model_type'),
                    'status': metadata.get('status', {}).value if hasattr(metadata.get('status', {}), 'value') else str(metadata.get('status')),
                    'created_at': metadata.get('created_at'),
                    'is_auto_ml': metadata.get('is_auto_ml', False)
                }
                
                # Add performance if available
                if 'metrics' in metadata:
                    metrics = metadata['metrics']
                    if metrics.r2_score:
                        model_info['r2_score'] = metrics.r2_score
                    if metrics.accuracy:
                        model_info['accuracy'] = metrics.accuracy
                    if metrics.cv_score_mean:
                        model_info['cv_score_mean'] = metrics.cv_score_mean
                
                models_list.append(model_info)
            
            return models_list
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

# Feature Engineering Functions
def create_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Texnik indikatorlar asosida feature yaratish"""
    try:
        features = df.copy()
        
        # Price-based features
        features['price_change'] = df['close'].pct_change()
        features['high_low_ratio'] = df['high'] / df['low']
        features['close_open_ratio'] = df['close'] / df['open']
        
        # Moving averages
        for window in [5, 10, 20, 50]:
            features[f'sma_{window}'] = df['close'].rolling(window).mean()
            features[f'price_sma_{window}_ratio'] = df['close'] / features[f'sma_{window}']
        
        # Volatility features
        features['volatility_5'] = df['close'].rolling(5).std()
        features['volatility_20'] = df['close'].rolling(20).std()
        
        # Volume features
        features['volume_change'] = df['volume'].pct_change()
        features['volume_sma_10'] = df['volume'].rolling(10).mean()
        features['price_volume_ratio'] = df['close'] / df['volume']
        
        # Lag features
        for lag in [1, 2, 3, 5]:
            features[f'price_lag_{lag}'] = df['close'].shift(lag)
            features[f'volume_lag_{lag}'] = df['volume'].shift(lag)
        
        # Rolling statistics
        for window in [5, 10, 20]:
            features[f'price_mean_{window}'] = df['close'].rolling(window).mean()
            features[f'price_std_{window}'] = df['close'].rolling(window).std()
            features[f'volume_mean_{window}'] = df['volume'].rolling(window).mean()
        
        return features.fillna(0)
        
    except Exception as e:
        logger.error(f"Feature engineering failed: {e}")
        return df

# Test function
async def test_ml_models():
    """Test ML Models Engine"""
    try:
        print("🤖 ML Models Engine Test")
        print("=" * 50)
        
        # Initialize engine
        engine = MLModelsEngine()
        
        # Create sample data
        np.random.seed(42)
        n_samples = 1000
        n_features = 10
        
        X = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        
        # Create target (price prediction)
        y = (
            X.iloc[:, 0] * 0.5 + 
            X.iloc[:, 1] * 0.3 + 
            X.iloc[:, 2] * 0.2 +
            np.random.randn(n_samples) * 0.1
        )
        
        print(f"📊 Sample Data Created:")
        print(f"  Features: {X.shape[1]}")
        print(f"  Samples: {X.shape[0]}")
        print(f"  Target range: {y.min():.3f} to {y.max():.3f}")
        
        # Test regression model
        print("\n🔧 Regression Model Test:")
        regression_model = await engine.create_regression_model(
            "test_regression", 
            model_type="random_forest"
        )
        
        metrics = await engine.train_model(
            "test_regression", 
            X, y,
            test_size=0.2,
            feature_selection=True
        )
        
        print(f"  R² Score: {metrics.r2_score:.4f}")
        print(f"  RMSE: {metrics.rmse:.4f}")
        print(f"  Training Time: {metrics.training_time:.2f}s")
        print(f"  Features Used: {metrics.feature_count}")
        
        # Test prediction
        print("\n🔮 Prediction Test:")
        test_data = X.iloc[:5]
        prediction = await engine.predict("test_regression", test_data)
        
        print(f"  Prediction: {prediction.prediction:.4f}")
        print(f"  Confidence: {prediction.confidence:.2f}")
        print(f"  Model: {prediction.model_name}")
        
        if prediction.explanation:
            print(f"  Explanation: {prediction.explanation}")
        
        # Test classification model
        print("\n📊 Classification Model Test:")
        y_class = (y > y.median()).astype(int)  # Binary classification
        
        classification_model = await engine.create_classification_model(
            "test_classification",
            model_type="random_forest"
        )
        
        metrics = await engine.train_model(
            "test_classification",
            X, y_class,
            test_size=0.2
        )
        
        print(f"  Accuracy: {metrics.accuracy:.4f}")
        print(f"  Precision: {metrics.precision:.4f}")
        print(f"  Recall: {metrics.recall:.4f}")
        print(f"  F1-Score: {metrics.f1_score:.4f}")
        
        # Test ensemble model
        print("\n🎯 Ensemble Model Test:")
        ensemble = await engine.create_ensemble_model(
            "test_ensemble",
            ["test_regression", "test_classification"],
            ensemble_type="voting"
        )
        
        print("  Ensemble model created successfully")
        
        # Test model management
        print("\n📋 Model Management:")
        models_list = engine.list_models()
        print(f"  Total Models: {len(models_list)}")
        
        for model in models_list:
            print(f"  - {model['name']}: {model['type']} ({model['model_type']})")
        
        # Test model info
        print("\nℹ️ Model Information:")
        info = engine.get_model_info("test_regression")
        print(f"  Model Type: {info.get('model_type')}")
        print(f"  Status: {info.get('status')}")
        if 'feature_importance' in info:
            print(f"  Top Features: {len(info['feature_importance'])}")
            for feature in info['feature_importance'][:3]:
                print(f"    - {feature['feature']}: {feature['importance']:.4f}")
        
        # Test AutoML
        print("\n🤖 AutoML Test:")
        best_model = await engine.auto_ml_optimize(
            X, y, 
            ModelType.REGRESSION,
            max_models=3
        )
        
        print(f"  Best AutoML Model: {best_model}")
        best_info = engine.get_model_info(best_model)
        if 'performance' in best_info:
            perf = best_info['performance']
            print(f"  AutoML R² Score: {perf.get('r2_score', 'N/A')}")
        
        print("\n✅ ML Models Engine test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ml_models())