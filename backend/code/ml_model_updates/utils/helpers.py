"""
ML Model Updates Utilities
Yordamchi funksiyalar va utilities
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import yaml
import pickle
import hashlib
from collections import defaultdict, deque
import time

class DataLoader:
    """Ma'lumotlarni yuklash utility"""
    
    @staticmethod
    def load_csv(file_path: str, **kwargs) -> pd.DataFrame:
        """CSV faylni yuklash"""
        try:
            return pd.read_csv(file_path, **kwargs)
        except Exception as e:
            logging.error(f"CSV yuklash xatosi: {str(e)}")
            raise
            
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """JSON faylni yuklash"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"JSON yuklash xatosi: {str(e)}")
            raise
            
    @staticmethod
    def load_pickle(file_path: str) -> Any:
        """Pickle faylni yuklash"""
        try:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logging.error(f"Pickle yuklash xatosi: {str(e)}")
            raise
            
class DataSaver:
    """Ma'lumotlarni saqlash utility"""
    
    @staticmethod
    def save_csv(data: pd.DataFrame, file_path: str, **kwargs):
        """CSV faylni saqlash"""
        try:
            data.to_csv(file_path, **kwargs)
        except Exception as e:
            logging.error(f"CSV saqlash xatosi: {str(e)}")
            raise
            
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str, indent: int = 2):
        """JSON faylni saqlash"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=indent, default=str)
        except Exception as e:
            logging.error(f"JSON saqlash xatosi: {str(e)}")
            raise
            
    @staticmethod
    def save_pickle(data: Any, file_path: str):
        """Pickle faylni saqlash"""
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logging.error(f"Pickle saqlash xatosi: {str(e)}")
            raise
            
class ModelValidator:
    """Model validatsiya utility"""
    
    @staticmethod
    def validate_model_input(data: pd.DataFrame, required_columns: List[str] = None) -> bool:
        """Model input validatsiya"""
        try:
            # Required columns
            if required_columns:
                missing_cols = set(required_columns) - set(data.columns)
                if missing_cols:
                    logging.error(f"Kerakli ustunlar topilmadi: {missing_cols}")
                    return False
                    
            # Data type validatsiya
            for col in data.columns:
                if data[col].dtype == 'object':
                    # String columns
                    if data[col].isna().any():
                        logging.warning(f"Column {col} da null qiymatlar mavjud")
                        
            # Missing values check
            missing_ratio = data.isnull().sum().sum() / (len(data) * len(data.columns))
            if missing_ratio > 0.5:
                logging.warning(f"Ma'lumotlarda juda ko'p missing values: {missing_ratio:.2%}")
                
            return True
            
        except Exception as e:
            logging.error(f"Model input validation xatosi: {str(e)}")
            return False
            
    @staticmethod
    def validate_model_output(predictions: np.ndarray, expected_shape: Tuple[int, ...] = None) -> bool:
        """Model output validatsiya"""
        try:
            if not isinstance(predictions, np.ndarray):
                logging.error("Predictions numpy array bo'lishi kerak")
                return False
                
            if np.isnan(predictions).any():
                logging.error("Predictions da NaN qiymatlar mavjud")
                return False
                
            if np.isinf(predictions).any():
                logging.error("Predictions da infinity qiymatlar mavjud")
                return False
                
            if expected_shape and predictions.shape != expected_shape:
                logging.error(f"Shape mos emas: expected {expected_shape}, got {predictions.shape}")
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Model output validation xatosi: {str(e)}")
            return False

class MetricsCalculator:
    """Metrikalar hisoblash utility"""
    
    @staticmethod
    def calculate_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Classification metrikalar"""
        try:
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            metrics = {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, average='weighted'),
                'recall': recall_score(y_true, y_pred, average='weighted'),
                'f1_score': f1_score(y_true, y_pred, average='weighted')
            }
            
            return metrics
            
        except ImportError:
            # Fallback metrics
            return MetricsCalculator._fallback_classification_metrics(y_true, y_pred)
            
    @staticmethod
    def _fallback_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Fallback classification metrikalar"""
        correct = (y_true == y_pred).sum()
        total = len(y_true)
        
        return {
            'accuracy': correct / total,
            'precision': correct / total,  # Approximation
            'recall': correct / total,     # Approximation
            'f1_score': correct / total    # Approximation
        }
        
    @staticmethod
    def calculate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Regression metrikalar"""
        try:
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            metrics = {
                'mse': mean_squared_error(y_true, y_pred),
                'mae': mean_absolute_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'r2_score': r2_score(y_true, y_pred)
            }
            
            return metrics
            
        except ImportError:
            # Fallback metrics
            return MetricsCalculator._fallback_regression_metrics(y_true, y_pred)
            
    @staticmethod
    def _fallback_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Fallback regression metrikalar"""
        mse = np.mean((y_true - y_pred) ** 2)
        mae = np.mean(np.abs(y_true - y_pred))
        
        return {
            'mse': mse,
            'mae': mae,
            'rmse': np.sqrt(mse),
            'r2_score': 0.0  # Placeholder
        }

class PerformanceProfiler:
    """Model performance profiling"""
    
    def __init__(self):
        self.profile_data = deque(maxlen=1000)
        
    def profile_model_inference(self, model: Any, test_data: pd.DataFrame, 
                              iterations: int = 100) -> Dict[str, float]:
        """Model inference profiling"""
        try:
            # Import only if available
            try:
                import time
            except ImportError:
                return {'error': 'time module not available'}
                
            inference_times = []
            
            for _ in range(iterations):
                start_time = time.time()
                
                # Model prediction
                predictions = model.predict(test_data)
                
                end_time = time.time()
                inference_times.append(end_time - start_time)
                
            return {
                'mean_inference_time': np.mean(inference_times),
                'median_inference_time': np.median(inference_times),
                'min_inference_time': np.min(inference_times),
                'max_inference_time': np.max(inference_times),
                'std_inference_time': np.std(inference_times),
                'total_iterations': iterations,
                'iterations_per_second': iterations / sum(inference_times)
            }
            
        except Exception as e:
            logging.error(f"Model profiling xatosi: {str(e)}")
            return {'error': str(e)}
            
    def profile_model_size(self, model: Any) -> Dict[str, Any]:
        """Model size profiling"""
        try:
            import pickle
            
            # Model size
            model_bytes = pickle.dumps(model)
            size_bytes = len(model_bytes)
            size_mb = size_bytes / (1024 * 1024)
            
            return {
                'size_bytes': size_bytes,
                'size_mb': size_mb,
                'size_mb_formatted': f"{size_mb:.2f} MB"
            }
            
        except Exception as e:
            logging.error(f"Model size profiling xatosi: {str(e)}")
            return {'error': str(e)}

class DataProcessor:
    """Ma'lumotlar processing utility"""
    
    @staticmethod
    def clean_data(data: pd.DataFrame) -> pd.DataFrame:
        """Ma'lumotlarni tozalash"""
        cleaned_data = data.copy()
        
        # Missing values handling
        for col in cleaned_data.columns:
            if cleaned_data[col].dtype in ['object']:
                # String columns
                cleaned_data[col] = cleaned_data[col].fillna('unknown')
            else:
                # Numeric columns
                cleaned_data[col] = cleaned_data[col].fillna(cleaned_data[col].median())
                
        # Duplicate rows
        cleaned_data = cleaned_data.drop_duplicates()
        
        return cleaned_data
        
    @staticmethod
    def detect_outliers(data: pd.DataFrame, method: str = 'iqr') -> Dict[str, List[int]]:
        """Outlier detection"""
        outliers = {}
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if method == 'iqr':
            for col in numeric_cols:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_indices = data[
                    (data[col] < lower_bound) | (data[col] > upper_bound)
                ].index.tolist()
                
                outliers[col] = outlier_indices
                
        return outliers
        
    @staticmethod
    def encode_categorical(data: pd.DataFrame, strategy: str = 'one_hot') -> pd.DataFrame:
        """Categorical encoding"""
        encoded_data = data.copy()
        categorical_cols = data.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            unique_count = data[col].nunique()
            
            if strategy == 'one_hot' or (strategy == 'auto' and unique_count <= 10):
                # One-hot encoding
                dummies = pd.get_dummies(data[col], prefix=col)
                encoded_data = pd.concat([encoded_data.drop(columns=[col]), dummies], axis=1)
                
            else:
                # Label encoding
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                encoded_data[col] = le.fit_transform(data[col].astype(str))
                
        return encoded_data
        
    @staticmethod
    def scale_features(data: pd.DataFrame, strategy: str = 'standard') -> pd.DataFrame:
        """Feature scaling"""
        scaled_data = data.copy()
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return scaled_data
            
        try:
            from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
            
            if strategy == 'standard':
                scaler = StandardScaler()
            elif strategy == 'minmax':
                scaler = MinMaxScaler()
            elif strategy == 'robust':
                scaler = RobustScaler()
            else:
                return scaled_data
                
            scaled_data[numeric_cols] = scaler.fit_transform(scaled_data[numeric_cols])
            return scaled_data
            
        except ImportError:
            # Fallback - no scaling
            logging.warning("Sklearn not available, skipping scaling")
            return scaled_data

class FileManager:
    """Fayl boshqaruvchi utility"""
    
    @staticmethod
    def create_directory_structure(base_path: str, subdirs: List[str]):
        """Directory structure yaratish"""
        base_path = Path(base_path)
        base_path.mkdir(parents=True, exist_ok=True)
        
        for subdir in subdirs:
            (base_path / subdir).mkdir(parents=True, exist_ok=True)
            
    @staticmethod
    def backup_file(source_path: str, backup_dir: str = "backups") -> str:
        """Fayl backup qilish"""
        source_path = Path(source_path)
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_path = backup_dir / backup_name
        
        import shutil
        shutil.copy2(source_path, backup_path)
        
        return str(backup_path)
        
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Fayl hash hisoblash"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    @staticmethod
    def get_directory_size(directory_path: str) -> Dict[str, float]:
        """Directory hajmi hisoblash"""
        directory_path = Path(directory_path)
        
        total_size = 0
        file_count = 0
        dir_count = 0
        
        for path in directory_path.rglob('*'):
            if path.is_file():
                total_size += path.stat().st_size
                file_count += 1
            elif path.is_dir():
                dir_count += 1
                
        return {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'file_count': file_count,
            'directory_count': dir_count
        }

class TimeUtils:
    """Vaqt utility funksiyalari"""
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Davr formatlash"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
            
    @staticmethod
    def get_next_scheduled_time(frequency: str, base_time: datetime = None) -> datetime:
        """Keyingi reja vaqt"""
        if base_time is None:
            base_time = datetime.now()
            
        if frequency == 'daily':
            return base_time + timedelta(days=1)
        elif frequency == 'weekly':
            return base_time + timedelta(weeks=1)
        elif frequency == 'monthly':
            if base_time.month == 12:
                next_month = base_time.replace(year=base_time.year + 1, month=1, day=1)
            else:
                next_month = base_time.replace(month=base_time.month + 1, day=1)
            return next_month
        else:
            return base_time + timedelta(days=1)  # Default
            
    @staticmethod
    def calculate_time_difference(start_time: datetime, end_time: datetime) -> Dict[str, float]:
        """Vaqt farqi hisoblash"""
        diff = end_time - start_time
        
        return {
            'total_seconds': diff.total_seconds(),
            'total_minutes': diff.total_seconds() / 60,
            'total_hours': diff.total_seconds() / 3600,
            'total_days': diff.days
        }

class ValidationUtils:
    """Validatsiya utility"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Email validatsiya"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    @staticmethod
    def validate_model_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Model konfiguratsiya validatsiya"""
        errors = []
        
        # Required fields
        required_fields = ['model_name', 'model_type', 'framework']
        for field in required_fields:
            if field not in config:
                errors.append(f"Kerakli maydon topilmadi: {field}")
                
        # Model name validation
        model_name = config.get('model_name', '')
        if not model_name or not isinstance(model_name, str):
            errors.append("Model name noto'g'ri")
            
        # Model type validation
        valid_types = ['classification', 'regression', 'clustering']
        if config.get('model_type') not in valid_types:
            errors.append(f"Model type noto'g'ri, valid options: {valid_types}")
            
        return len(errors) == 0, errors
        
    @staticmethod
    def validate_data_schema(data: pd.DataFrame, expected_schema: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Data schema validatsiya"""
        errors = []
        
        for column, expected_type in expected_schema.items():
            if column not in data.columns:
                errors.append(f"Column topilmadi: {column}")
                continue
                
            actual_type = str(data[column].dtype)
            
            if expected_type == 'numeric' and not np.issubdtype(data[column].dtype, np.number):
                errors.append(f"Column {column} numeric bo'lishi kerak, got {actual_type}")
            elif expected_type == 'categorical' and not np.issubdtype(data[column].dtype, np.object_):
                errors.append(f"Column {column} categorical bo'lishi kerak, got {actual_type}")
                
        return len(errors) == 0, errors

# Global utility instances
data_loader = DataLoader()
data_saver = DataSaver()
model_validator = ModelValidator()
metrics_calculator = MetricsCalculator()
performance_profiler = PerformanceProfiler()
data_processor = DataProcessor()
file_manager = FileManager()
time_utils = TimeUtils()
validation_utils = ValidationUtils()

def setup_default_directories():
    """Default directory structure setup"""
    directories = [
        'data/raw',
        'data/processed',
        'data/training',
        'models',
        'models/registry',
        'models/automl',
        'logs',
        'logs/audit',
        'config',
        'backups',
        'reports',
        'exports'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
    logging.info("Default directories created")

if __name__ == "__main__":
    # Setup default directories
    setup_default_directories()
    
    # Test utilities
    print("ML Model Updates Utilities initialized successfully")