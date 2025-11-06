"""
Utility functions for Self-Learning Trading Fund

Yordamchi funksiyalar va umumiy utilitylar
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging


def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
    """Sharpe ratio hisoblash"""
    if len(returns) == 0 or np.std(returns) == 0:
        return 0.0
    
    excess_returns = returns - risk_free_rate / 252  # Kunlik risk-free rate
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)


def calculate_max_drawdown(returns: np.ndarray) -> float:
    """Maximum drawdown hisoblash"""
    if len(returns) == 0:
        return 0.0
    
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    return abs(drawdown.min())


def calculate_win_rate(returns: np.ndarray) -> float:
    """Win rate hisoblash"""
    if len(returns) == 0:
        return 0.0
    
    winning_trades = np.sum(returns > 0)
    return winning_trades / len(returns)


def normalize_data(data: np.ndarray, method: str = 'standard') -> np.ndarray:
    """Ma'lumotlarni normalizatsiya qilish"""
    if method == 'standard':
        return (data - np.mean(data)) / np.std(data)
    elif method == 'min_max':
        return (data - np.min(data)) / (np.max(data) - np.min(data))
    elif method == 'robust':
        median = np.median(data)
        mad = np.median(np.abs(data - median))
        return (data - median) / (1.4826 * mad)
    else:
        return data


def detect_outliers(data: np.ndarray, method: str = 'iqr', threshold: float = 3.0) -> np.ndarray:
    """Outlier detection"""
    if method == 'iqr':
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return (data < lower_bound) | (data > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((data - np.mean(data)) / np.std(data))
        return z_scores > threshold
    
    return np.zeros(len(data), dtype=bool)


def create_technical_indicators(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Texnik indikatorlar yaratish"""
    result = df.copy()
    
    # Moving averages
    result['ma_short'] = df['close'].rolling(window=5).mean()
    result['ma_long'] = df['close'].rolling(window=window).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    result['rsi'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    result['bb_middle'] = df['close'].rolling(window=window).mean()
    bb_std = df['close'].rolling(window=window).std()
    result['bb_upper'] = result['bb_middle'] + (bb_std * 2)
    result['bb_lower'] = result['bb_middle'] - (bb_std * 2)
    
    # MACD
    ema_12 = df['close'].ewm(span=12).mean()
    ema_26 = df['close'].ewm(span=26).mean()
    result['macd'] = ema_12 - ema_26
    result['macd_signal'] = result['macd'].ewm(span=9).mean()
    
    return result


def split_time_series_data(data: pd.DataFrame, train_ratio: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Time series ma'lumotlarini train/test ga bo'lish"""
    split_idx = int(len(data) * train_ratio)
    return data.iloc[:split_idx], data.iloc[split_idx:]


def save_model_metadata(model_path: str, metadata: Dict) -> None:
    """Model metadata saqlash"""
    import json
    metadata_path = model_path.replace('.pth', '_metadata.json')
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)


def load_model_metadata(model_path: str) -> Dict:
    """Model metadata yuklash"""
    import json
    metadata_path = model_path.replace('.pth', '_metadata.json')
    
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def setup_logging(name: str, level: str = 'INFO', log_file: str = None) -> logging.Logger:
    """Logging setup"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler (agar kerak bo'lsa)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(console_formatter)
            logger.addHandler(file_handler)
    
    return logger


class DataValidator:
    """Ma'lumot validatsiya classi"""
    
    def __init__(self):
        self.errors = []
    
    def validate_dataframe(self, df: pd.DataFrame, required_columns: List[str] = None) -> bool:
        """DataFrame validatsiyasi"""
        if df.empty:
            self.errors.append("DataFrame bo'sh")
            return False
        
        if required_columns:
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                self.errors.append(f"Kerakli ustunlar yo'q: {missing_columns}")
                return False
        
        if df.isnull().any().any():
            null_counts = df.isnull().sum()
            self.errors.append(f"Null qiymatlar mavjud: {null_counts.to_dict()}")
            return False
        
        return True
    
    def get_errors(self) -> List[str]:
        """Xatolarni qaytarish"""
        return self.errors.copy()


class PerformanceMetrics:
    """Performance metrikalari hisoblash"""
    
    @staticmethod
    def all_metrics(returns: np.ndarray) -> Dict[str, float]:
        """Barcha metrikalarni hisoblash"""
        return {
            'total_return': np.prod(1 + returns) - 1,
            'annualized_return': (np.prod(1 + returns) ** (252 / len(returns))) - 1,
            'sharpe_ratio': calculate_sharpe_ratio(returns),
            'max_drawdown': calculate_max_drawdown(returns),
            'win_rate': calculate_win_rate(returns),
            'volatility': np.std(returns) * np.sqrt(252),
            'skewness': pd.Series(returns).skew(),
            'kurtosis': pd.Series(returns).kurtosis()
        }


def create_portfolio_summary(positions: Dict, cash: float, prices: Dict) -> Dict:
    """Portfolio hisobot yaratish"""
    total_value = cash
    total_pnl = 0
    
    for symbol, position in positions.items():
        if symbol in prices:
            current_price = prices[symbol]
            market_value = position['quantity'] * current_price
            cost_basis = position['quantity'] * position['avg_price']
            pnl = market_value - cost_basis
            
            total_value += market_value
            total_pnl += pnl
    
    return {
        'total_value': total_value,
        'cash': cash,
        'total_pnl': total_pnl,
        'total_pnl_percent': (total_pnl / (total_value - total_pnl)) * 100 if total_value > total_pnl else 0,
        'num_positions': len(positions)
    }