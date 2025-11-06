"""
Quantum Trading Utilities
========================

Yordamchi funksiyalar va utilities:
1. Data validation and preprocessing
2. Configuration management
3. Logging utilities
4. Performance monitoring
5. Visualization helpers
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
import asyncio
import logging
from datetime import datetime, timedelta
import json
import yaml
import os
import warnings
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def validate_market_data(data: Dict[str, Any]) -> bool:
    """Market ma'lumotlarini validatsiya qilish"""
    required_keys = ['timestamp', 'price', 'volume']
    
    for key, value in data.items():
        if isinstance(value, dict):
            for req_key in required_keys:
                if req_key not in value:
                    warnings.warn(f"Missing required key '{req_key}' in {key}")
                    return False
        
        if 'timestamp' in value:
            try:
                datetime.fromisoformat(value['timestamp'])
            except ValueError:
                warnings.warn(f"Invalid timestamp format in {key}")
                return False
    
    return True

def preprocess_market_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Market ma'lumotlarini preprocessing qilish"""
    processed_data = {}
    
    for asset_type, asset_data in data.items():
        if isinstance(asset_data, dict) and 'data' in asset_data:
            processed_symbols = {}
            
            for symbol, market_data in asset_data['data'].items():
                # Ensure numeric types
                processed_market_data = {
                    'price': float(market_data.get('price', 0.0)),
                    'volume': float(market_data.get('volume', 0.0)),
                    'timestamp': market_data.get('timestamp', datetime.now().isoformat())
                }
                
                # Calculate returns if not present
                if 'returns' not in processed_market_data:
                    # Simulate return calculation (in real implementation, would use historical data)
                    processed_market_data['returns'] = np.random.normal(0, 0.02)
                
                processed_symbols[symbol] = processed_market_data
            
            processed_data[asset_type] = {
                'data': processed_symbols,
                'processed_at': datetime.now().isoformat()
            }
    
    return processed_data

def calculate_risk_metrics(returns: np.ndarray) -> Dict[str, float]:
    """Risk metrikalarini hisoblash"""
    if len(returns) == 0:
        return {}
    
    return {
        'volatility': float(np.std(returns)),
        'skewness': float(stats.skew(returns)),
        'kurtosis': float(stats.kurtosis(returns)),
        'max_drawdown': float(calculate_max_drawdown(returns)),
        'var_95': float(np.percentile(returns, 5)),
        'var_99': float(np.percentile(returns, 1))
    }

def calculate_max_drawdown(returns: np.ndarray) -> float:
    """Maximum drawdown hisoblash"""
    if len(returns) == 0:
        return 0.0
    
    cumulative = np.cumprod(1 + returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    
    return float(np.min(drawdown))

def setup_logging(name: str = "quantum_trading", level: str = "INFO") -> logging.Logger:
    """Logging sozlanishi"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / f"{name}.log")
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

class PerformanceMonitor:
    """Performance monitoring class"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Timer boshlash"""
        self.start_times[operation] = datetime.now()
    
    def end_timer(self, operation: str) -> float:
        """Timer tugatish va vaqt qaytarish"""
        if operation not in self.start_times:
            raise ValueError(f"Timer for '{operation}' was not started")
        
        end_time = datetime.now()
        duration = (end_time - self.start_times[operation]).total_seconds()
        
        if operation not in self.metrics:
            self.metrics[operation] = []
        
        self.metrics[operation].append(duration)
        del self.start_times[operation]
        
        return duration
    
    def get_average_time(self, operation: str) -> float:
        """O'rtacha vaqt olish"""
        if operation in self.metrics:
            return np.mean(self.metrics[operation])
        return 0.0
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Performance hisobotini olish"""
        report = {}
        
        for operation, times in self.metrics.items():
            report[operation] = {
                'count': len(times),
                'average_time': np.mean(times),
                'min_time': np.min(times),
                'max_time': np.max(times),
                'std_time': np.std(times)
            }
        
        return report

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Konfiguratsiya faylini yuklash"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        return get_default_config()
    
    try:
        with open(config_file, 'r') as f:
            if config_path.endswith('.json'):
                return json.load(f)
            elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                return yaml.safe_load(f)
    except Exception as e:
        logging.warning(f"Failed to load config from {config_path}: {e}")
        return get_default_config()
    
    return get_default_config()

def save_config(config: Dict[str, Any], config_path: str = "config.yaml"):
    """Konfiguratsiyani saqlash"""
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_file, 'w') as f:
            if config_path.endswith('.json'):
                json.dump(config, f, indent=2)
            elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                yaml.dump(config, f, default_flow_style=False)
    except Exception as e:
        logging.error(f"Failed to save config to {config_path}: {e}")

def get_default_config() -> Dict[str, Any]:
    """Default konfiguratsiya"""
    return {
        'quantum_trading': {
            'enabled': True,
            'quantum_advantage_threshold': 0.15,
            'n_qubits': 8,
            'circuit_depth': 6,
            'optimization_method': 'variational'
        },
        'error_correction': {
            'enabled': True,
            'code_type': 'surface_code',
            'error_threshold': 0.001,
            'fidelity_target': 0.999
        },
        'benchmarking': {
            'enabled': True,
            'iterations': 100,
            'warmup_iterations': 10,
            'output_dir': 'benchmarks'
        },
        'logging': {
            'level': 'INFO',
            'file': True,
            'console': True
        }
    }

def create_visualization(data: Dict[str, Any], chart_type: str = 'line', 
                        output_path: str = 'chart.png', **kwargs) -> str:
    """Visualization yaratish"""
    plt.style.use('seaborn-v0_8')
    fig, ax = plt.subplots(figsize=(12, 8))
    
    if chart_type == 'line':
        for label, values in data.items():
            ax.plot(values, label=label, **kwargs)
        ax.legend()
        ax.set_title('Time Series Data')
    
    elif chart_type == 'bar':
        labels = list(data.keys())
        values = list(data.values())
        ax.bar(labels, values, **kwargs)
        ax.set_title('Bar Chart')
        plt.xticks(rotation=45)
    
    elif chart_type == 'heatmap':
        df = pd.DataFrame(data)
        sns.heatmap(df, annot=True, cmap='coolwarm', center=0, ax=ax)
        ax.set_title('Correlation Heatmap')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path

def format_number(number: Union[int, float], precision: int = 2) -> str:
    """Raqamlarni formatlash"""
    if isinstance(number, float):
        return f"{number:.{precision}f}"
    return f"{number:,}"

def convert_to_percentage(value: float, precision: int = 2) -> str:
    """Foiz ga aylantirish"""
    return f"{value * 100:.{precision}f}%"

def calculate_correlation_matrix(data: Dict[str, np.ndarray]) -> np.ndarray:
    """Correlation matrix hisoblash"""
    # Convert to DataFrame for correlation calculation
    df = pd.DataFrame(data)
    return df.corr().values

def normalize_data(data: np.ndarray, method: str = 'minmax') -> np.ndarray:
    """Ma'lumotlarni normalizatsiya qilish"""
    if method == 'minmax':
        min_val = np.min(data)
        max_val = np.max(data)
        return (data - min_val) / (max_val - min_val) if max_val != min_val else data
    elif method == 'zscore':
        mean_val = np.mean(data)
        std_val = np.std(data)
        return (data - mean_val) / std_val if std_val != 0 else data
    else:
        raise ValueError(f"Unknown normalization method: {method}")

def generate_sample_data(n_periods: int = 252, n_assets: int = 5) -> Dict[str, np.ndarray]:
    """Namuna ma'lumotlar yaratish"""
    dates = pd.date_range(start='2023-01-01', periods=n_periods, freq='D')
    
    # Generate correlated returns
    correlation_matrix = np.random.uniform(0.2, 0.8, (n_assets, n_assets))
    correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
    np.fill_diagonal(correlation_matrix, 1.0)
    
    # Generate correlated random data
    L = np.linalg.cholesky(correlation_matrix)
    uncorrelated = np.random.normal(0, 1, (n_periods, n_assets))
    correlated = uncorrelated @ L.T
    
    # Convert to prices
    returns = correlated * 0.02  # 2% daily volatility
    prices = 100 * np.cumprod(1 + returns, axis=0)
    
    assets = [f'Asset_{i+1}' for i in range(n_assets)]
    data = {f'price_{asset}': prices[:, i] for i, asset in enumerate(assets)}
    data['dates'] = dates.values
    
    return data

async def simulate_network_latency(min_latency: float = 0.001, 
                                 max_latency: float = 0.01) -> float:
    """Tarmoq kechikishini simulyatsiya qilish"""
    import random
    await asyncio.sleep(random.uniform(min_latency, max_latency))
    return random.uniform(min_latency, max_latency)

def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
    """Sharpe ratio hisoblash"""
    if len(returns) == 0:
        return 0.0
    
    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    return np.mean(excess_returns) / np.std(returns) if np.std(returns) != 0 else 0.0

def calculate_information_ratio(portfolio_returns: np.ndarray, 
                              benchmark_returns: np.ndarray) -> float:
    """Information ratio hisoblash"""
    if len(portfolio_returns) != len(benchmark_returns):
        raise ValueError("Portfolio and benchmark returns must have same length")
    
    excess_returns = portfolio_returns - benchmark_returns
    return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else 0.0

def portfolio_variance(weights: np.ndarray, covariance_matrix: np.ndarray) -> float:
    """Portfolio variansini hisoblash"""
    return float(weights.T @ covariance_matrix @ weights)

def portfolio_expected_return(weights: np.ndarray, expected_returns: np.ndarray) -> float:
    """Portfolio kutish returnini hisoblash"""
    return float(weights @ expected_returns)

def efficient_frontier(expected_returns: np.ndarray, 
                      covariance_matrix: np.ndarray, 
                      n_portfolios: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Samarali frontiera hisoblash"""
    from scipy.optimize import minimize
    
    n_assets = len(expected_returns)
    
    def portfolio_stats(weights):
        ret = portfolio_expected_return(weights, expected_returns)
        var = portfolio_variance(weights, covariance_matrix)
        return ret, var
    
    def negative_sharpe(weights):
        ret, var = portfolio_stats(weights)
        return -ret / np.sqrt(var) if var > 0 else 0
    
    # Constraints
    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
    bounds = tuple((0, 1) for _ in range(n_assets))
    
    # Generate efficient frontier
    min_ret = np.min(expected_returns)
    max_ret = np.max(expected_returns)
    
    target_returns = np.linspace(min_ret, max_ret, n_portfolios)
    
    efficient_portfolios = []
    for target_ret in target_returns:
        def ret_constraint(weights):
            ret, _ = portfolio_stats(weights)
            return ret - target_ret
        
        constraints_with_ret = constraints + [{'type': 'eq', 'fun': ret_constraint}]
        
        result = minimize(negative_sharpe, np.ones(n_assets)/n_assets, 
                         method='SLSQP', bounds=bounds, constraints=constraints_with_ret)
        
        if result.success:
            weights = result.x
            ret, var = portfolio_stats(weights)
            efficient_portfolios.append((ret, np.sqrt(var), weights))
    
    if efficient_portfolios:
        returns, risks, weights = zip(*efficient_portfolios)
        return np.array(returns), np.array(risks), np.array(weights)
    else:
        return np.array([]), np.array([]), np.array([])

class QuantumStateValidator:
    """Quantum holat validatori"""
    
    @staticmethod
    def is_valid_quantum_state(state: np.ndarray) -> bool:
        """Quantum holatni validatsiya qilish"""
        if len(state.shape) != 1:
            return False
        
        # Check normalization
        norm = np.linalg.norm(state)
        if abs(norm - 1.0) > 1e-10:
            return False
        
        # Check for complex numbers (quantum states can be complex)
        if not np.iscomplexobj(state):
            return False
        
        # Check for NaN or Inf
        if np.any(np.isnan(state)) or np.any(np.isinf(state)):
            return False
        
        return True
    
    @staticmethod
    def normalize_quantum_state(state: np.ndarray) -> np.ndarray:
        """Quantum holatni normalizatsiya qilish"""
        norm = np.linalg.norm(state)
        if norm == 0:
            return state
        return state / norm
    
    @staticmethod
    def calculate_fidelity(state1: np.ndarray, state2: np.ndarray) -> float:
        """Ikki quantum holat orasidagi fidelity hisoblash"""
        if not (QuantumStateValidator.is_valid_quantum_state(state1) and 
                QuantumStateValidator.is_valid_quantum_state(state2)):
            return 0.0
        
        # Fidelity = |<ψ1|ψ2>|^2
        fidelity = abs(np.vdot(state1, state2))**2
        return float(fidelity)

def memory_usage_mb() -> float:
    """Xotira ishlatish miqdorini MB da olish"""
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def cpu_usage_percent() -> float:
    """CPU ishlatish foizini olish"""
    return psutil.cpu_percent()

class CircuitComplexityAnalyzer:
    """Quantum circuit murakkablik analizatori"""
    
    @staticmethod
    def calculate_depth(circuit_gates: List[Dict[str, Any]]) -> int:
        """Circuit chuqurligini hisoblash"""
        if not circuit_gates:
            return 0
        
        # Simplified depth calculation
        max_time_step = 0
        for gate in circuit_gates:
            # Estimate time step based on gate type
            if gate.get('type') in ['H', 'X', 'Y', 'Z']:
                time_step = 1
            elif gate.get('type') in ['CNOT', 'CZ']:
                time_step = 2
            else:
                time_step = 1
            
            max_time_step = max(max_time_step, time_step)
        
        return max_time_step
    
    @staticmethod
    def count_gates(circuit_gates: List[Dict[str, Any]]) -> Dict[str, int]:
        """Gate turlari sonini hisoblash"""
        gate_counts = {}
        for gate in circuit_gates:
            gate_type = gate.get('type', 'unknown')
            gate_counts[gate_type] = gate_counts.get(gate_type, 0) + 1
        return gate_counts
    
    @staticmethod
    def estimate_qubit_usage(gates: List[Dict[str, Any]]) -> int:
        """Qubit ishlatishni baholash"""
        qubits_used = set()
        for gate in gates:
            target = gate.get('target')
            control = gate.get('control')
            
            if target is not None:
                qubits_used.add(target)
            if control is not None:
                qubits_used.add(control)
        
        return len(qubits_used)