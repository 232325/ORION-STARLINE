"""
Utility functions for Forex NFT Hedge System
Yordamchi funksiyalar va utilitlar
"""

import json
import math
import numpy as np
import asyncio
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
import logging
from dataclasses import asdict
import hashlib
import base64
import csv
import io

# Logging setup
logger = logging.getLogger(__name__)

class DataValidationUtils:
    """Ma'lumotlarni validatsiya qilish utilitysi"""
    
    @staticmethod
    def validate_forex_pair(pair_str: str) -> bool:
        """Forex pair validatsiyasi"""
        valid_pairs = [
            "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD",
            "USD/CAD", "NZD/USD", "EUR/JPY", "EUR/GBP", "GBP/JPY"
        ]
        return pair_str in valid_pairs
    
    @staticmethod
    def validate_position_size(amount: float) -> bool:
        """Position size validatsiyasi"""
        return 10000 <= amount <= 100000000  # $10K to $100M
    
    @staticmethod
    def validate_hedge_ratio(ratio: float) -> bool:
        """Hedge ratio validatsiyasi"""
        return 0.0 <= ratio <= 1.0
    
    @staticmethod
    def validate_volatility(vol: float) -> bool:
        """Volatillik validatsiyasi"""
        return 0.001 <= vol <= 1.0  # 0.1% to 100%
    
    @staticmethod
    def validate_correlation(corr: float) -> bool:
        """Korrelatsiya validatsiyasi"""
        return -1.0 <= corr <= 1.0

class CalculationUtils:
    """Hisoblash utilitysi"""
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Sharpe ratio hisoblash"""
        if not returns or len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        excess_return = mean_return - (risk_free_rate / 252)  # Daily risk-free rate
        return excess_return / std_return
    
    @staticmethod
    def calculate_var(returns: List[float], confidence_level: float = 0.95) -> float:
        """Value at Risk hisoblash"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        var_percentile = (1 - confidence_level) * 100
        return np.percentile(returns_array, var_percentile)
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> float:
        """Maximum drawdown hisoblash"""
        if not equity_curve:
            return 0.0
        
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    @staticmethod
    def calculate_information_ratio(returns: List[float], benchmark_returns: List[float]) -> float:
        """Information ratio hisoblash"""
        if len(returns) != len(benchmark_returns) or len(returns) < 2:
            return 0.0
        
        excess_returns = [r - b for r, b in zip(returns, benchmark_returns)]
        mean_excess = np.mean(excess_returns)
        tracking_error = np.std(excess_returns)
        
        return mean_excess / tracking_error if tracking_error > 0 else 0.0
    
    @staticmethod
    def calculate_beta(returns: List[float], market_returns: List[float]) -> float:
        """Beta hisoblash"""
        if len(returns) != len(market_returns) or len(returns) < 2:
            return 1.0
        
        returns_array = np.array(returns)
        market_array = np.array(market_returns)
        
        covariance = np.cov(returns_array, market_array)[0, 1]
        market_variance = np.var(market_array)
        
        return covariance / market_variance if market_variance > 0 else 1.0
    
    @staticmethod
    def kelly_criterion(win_probability: float, avg_win: float, avg_loss: float) -> float:
        """Kelly Criterion hisoblash"""
        if avg_loss <= 0:
            return 0.0
        
        b = avg_win / abs(avg_loss)  # Odds ratio
        q = 1 - win_probability  # Loss probability
        
        kelly_fraction = (b * win_probability - q) / b
        
        return max(0.0, min(kelly_fraction, 1.0))  # Constrain to [0, 1]
    
    @staticmethod
    def efficient_frontier_weight(returns: List[float], covariance_matrix: np.ndarray) -> np.ndarray:
        """Efficient frontier weight hisoblash (simplified)"""
        n_assets = len(returns)
        
        if n_assets == 0:
            return np.array([])
        
        # Equal weight as baseline
        weights = np.ones(n_assets) / n_assets
        
        # Risk-adjusted optimization
        expected_returns = np.array(returns)
        risk_aversion = 2.0  # Risk aversion parameter
        
        try:
            # Simplified quadratic optimization
            inv_cov = np.linalg.inv(covariance_matrix)
            ones = np.ones(n_assets)
            
            # Calculate optimal weights
            numerator = inv_cov @ expected_returns - (risk_aversion / 2) * inv_cov @ ones
            denominator = ones.T @ inv_cov @ expected_returns - (risk_aversion / 2) * ones.T @ inv_cov @ ones
            
            if denominator != 0:
                weights = numerator / denominator
            else:
                # Fallback to equal weights
                weights = np.ones(n_assets) / n_assets
                
        except np.linalg.LinAlgError:
            # If matrix is singular, use equal weights
            weights = np.ones(n_assets) / n_assets
        
        # Ensure weights are positive and sum to 1
        weights = np.maximum(weights, 0)
        weights = weights / np.sum(weights)
        
        return weights

class PerformanceUtils:
    """Performance hisoblash utilitysi"""
    
    @staticmethod
    def calculate_total_return(start_value: float, end_value: float) -> float:
        """Jami return hisoblash"""
        if start_value <= 0:
            return 0.0
        return (end_value - start_value) / start_value
    
    @staticmethod
    def calculate_annualized_return(total_return: float, periods: int, periods_per_year: int = 252) -> float:
        """Yilliklashtirilgan return hisoblash"""
        if total_return <= -1 or periods <= 0:
            return 0.0
        
        return (1 + total_return) ** (periods_per_year / periods) - 1
    
    @staticmethod
    def calculate_volatility(returns: List[float], periods_per_year: int = 252) -> float:
        """Volatillik hisoblash"""
        if not returns or len(returns) < 2:
            return 0.0
        
        std_returns = np.std(returns)
        return std_returns * math.sqrt(periods_per_year)
    
    @staticmethod
    def calculate_calmar_ratio(annualized_return: float, max_drawdown: float) -> float:
        """Calmar ratio hisoblash"""
        if max_drawdown <= 0:
            return 0.0
        return annualized_return / max_drawdown
    
    @staticmethod
    def calculate_sortino_ratio(returns: List[float], target_return: float = 0.0, periods_per_year: int = 252) -> float:
        """Sortino ratio hisoblash"""
        if not returns:
            return 0.0
        
        excess_returns = [r - target_return for r in returns]
        negative_returns = [r for r in excess_returns if r < 0]
        
        if not negative_returns:
            return float('inf') if target_return <= 0 else 0.0
        
        downside_std = np.std(negative_returns) * math.sqrt(periods_per_year)
        mean_excess = np.mean(excess_returns) * periods_per_year
        
        return mean_excess / downside_std if downside_std > 0 else 0.0
    
    @staticmethod
    def calculate_omega_ratio(returns: List[float], threshold: float = 0.0) -> float:
        """Omega ratio hisoblash"""
        if not returns:
            return 1.0
        
        gains = sum(max(r - threshold, 0) for r in returns)
        losses = sum(max(threshold - r, 0) for r in returns)
        
        if losses == 0:
            return float('inf')
        
        return gains / losses
    
    @staticmethod
    def calculate_up_capture(returns: List[float], benchmark_returns: List[float]) -> float:
        """Up capture ratio hisoblash"""
        if len(returns) != len(benchmark_returns):
            return 100.0
        
        up_bench = [b for b in benchmark_returns if b > 0]
        if not up_bench:
            return 100.0
        
        up_port = [r for r, b in zip(returns, benchmark_returns) if b > 0]
        
        if not up_port:
            return 100.0
        
        port_up_return = sum(up_port) / len(up_port)
        bench_up_return = sum(up_bench) / len(up_bench)
        
        return (port_up_return / bench_up_return) * 100 if bench_up_return != 0 else 100.0
    
    @staticmethod
    def calculate_down_capture(returns: List[float], benchmark_returns: List[float]) -> float:
        """Down capture ratio hisoblash"""
        if len(returns) != len(benchmark_returns):
            return 100.0
        
        down_bench = [b for b in benchmark_returns if b < 0]
        if not down_bench:
            return 100.0
        
        down_port = [r for r, b in zip(returns, benchmark_returns) if b < 0]
        
        if not down_port:
            return 100.0
        
        port_down_return = sum(down_port) / len(down_port)
        bench_down_return = sum(down_bench) / len(down_bench)
        
        return (port_down_return / bench_down_return) * 100 if bench_down_return != 0 else 100.0

class DataProcessingUtils:
    """Ma'lumotlarni qayta ishlash utilitysi"""
    
    @staticmethod
    def normalize_data(data: List[float], method: str = "zscore") -> List[float]:
        """Ma'lumotlarni normalizatsiya qilish"""
        if not data:
            return []
        
        if method == "zscore":
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return [0.0] * len(data)
            return [(x - mean) / std for x in data]
        
        elif method == "minmax":
            min_val = min(data)
            max_val = max(data)
            if max_val == min_val:
                return [0.0] * len(data)
            return [(x - min_val) / (max_val - min_val) for x in data]
        
        elif method == "robust":
            median = np.median(data)
            mad = np.median([abs(x - median) for x in data])
            if mad == 0:
                return [0.0] * len(data)
            return [(x - median) / mad for x in data]
        
        else:
            return data
    
    @staticmethod
    def smooth_data(data: List[float], window: int = 5, method: str = "moving_average") -> List[float]:
        """Ma'lumotlarni smooth qilish"""
        if len(data) < window:
            return data
        
        if method == "moving_average":
            smoothed = []
            for i in range(len(data)):
                start = max(0, i - window // 2)
                end = min(len(data), i + window // 2 + 1)
                smoothed.append(np.mean(data[start:end]))
            return smoothed
        
        elif method == "exponential":
            alpha = 2.0 / (window + 1)
            smoothed = [data[0]]
            for i in range(1, len(data)):
                smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[-1])
            return smoothed
        
        else:
            return data
    
    @staticmethod
    def detect_outliers(data: List[float], method: str = "iqr", threshold: float = 1.5) -> List[int]:
        """Outlierlarni aniqlash"""
        if len(data) < 4:
            return []
        
        if method == "iqr":
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            return [i for i, x in enumerate(data) if x < lower_bound or x > upper_bound]
        
        elif method == "zscore":
            z_scores = np.abs((data - np.mean(data)) / np.std(data))
            return [i for i, z in enumerate(z_scores) if z > threshold]
        
        elif method == "modified_zscore":
            median = np.median(data)
            mad = np.median([abs(x - median) for x in data])
            if mad == 0:
                return []
            
            modified_z_scores = [0.6745 * (x - median) / mad for x in data]
            return [i for i, z in enumerate(modified_z_scores) if abs(z) > threshold]
        
        else:
            return []
    
    @staticmethod
    def calculate_rolling_statistics(data: List[float], window: int = 20) -> Dict[str, List[float]]:
        """Rolling statistics hisoblash"""
        if len(data) < window:
            return {}
        
        rolling_stats = {
            "rolling_mean": [],
            "rolling_std": [],
            "rolling_min": [],
            "rolling_max": []
        }
        
        for i in range(len(data)):
            if i < window - 1:
                # Not enough data points
                rolling_stats["rolling_mean"].append(data[i])
                rolling_stats["rolling_std"].append(0.0)
                rolling_stats["rolling_min"].append(min(data[:i+1]))
                rolling_stats["rolling_max"].append(max(data[:i+1]))
            else:
                # Full window
                window_data = data[i-window+1:i+1]
                rolling_stats["rolling_mean"].append(np.mean(window_data))
                rolling_stats["rolling_std"].append(np.std(window_data))
                rolling_stats["rolling_min"].append(min(window_data))
                rolling_stats["rolling_max"].append(max(window_data))
        
        return rolling_stats

class CryptoUtils:
    """Cryptographic utilitysi"""
    
    @staticmethod
    def generate_secure_hash(data: str, algorithm: str = "sha256") -> str:
        """Secure hash yaratish"""
        if algorithm == "sha256":
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data.encode()).hexdigest()
        elif algorithm == "blake2b":
            return hashlib.blake2b(data.encode()).hexdigest()
        else:
            return hashlib.md5(data.encode()).hexdigest()
    
    @staticmethod
    def create_checksum(data: Union[str, bytes]) -> str:
        """Checksum yaratish"""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def generate_token_id(seed_data: str) -> str:
        """Unique token ID yaratish"""
        timestamp = str(datetime.now().timestamp())
        seed = f"{seed_data}_{timestamp}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]
    
    @staticmethod
    def encode_metadata(metadata: Dict) -> str:
        """Metadata encoding"""
        json_str = json.dumps(metadata, separators=(',', ':'), sort_keys=True)
        return base64.b64encode(json_str.encode()).decode()
    
    @staticmethod
    def decode_metadata(encoded: str) -> Dict:
        """Metadata decoding"""
        try:
            json_str = base64.b64decode(encoded.encode()).decode()
            return json.loads(json_str)
        except:
            return {}

class ExportUtils:
    """Export utilitysi"""
    
    @staticmethod
    def export_to_json(data: Any, filename: str) -> bool:
        """JSON ga export qilish"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            logger.error(f"JSON export error: {e}")
            return False
    
    @staticmethod
    def export_to_csv(data: List[Dict], filename: str) -> bool:
        """CSV ga export qilish"""
        try:
            if not data:
                return False
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            logger.error(f"CSV export error: {e}")
            return False
    
    @staticmethod
    def export_performance_report(performance_data: Dict, filename: str) -> bool:
        """Performance report export"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "performance_metrics": performance_data,
                "summary": {
                    "total_return": performance_data.get("total_return", 0),
                    "sharpe_ratio": performance_data.get("sharpe_ratio", 0),
                    "max_drawdown": performance_data.get("max_drawdown", 0),
                    "win_rate": performance_data.get("win_rate", 0)
                }
            }
            return ExportUtils.export_to_json(report, filename)
        except Exception as e:
            logger.error(f"Performance report export error: {e}")
            return False
    
    @staticmethod
    def create_html_report(data: Dict, filename: str) -> bool:
        """HTML report yaratish"""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Forex NFT Hedge Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .metric {{ margin: 10px 0; padding: 10px; background: #f5f5f5; }}
                    .positive {{ color: green; }}
                    .negative {{ color: red; }}
                </style>
            </head>
            <body>
                <h1>Forex NFT Hedge Performance Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>Performance Metrics</h2>
                {ExportUtils._format_metrics_html(data.get('performance_metrics', {}))}
                
                <h2>System Status</h2>
                {ExportUtils._format_status_html(data.get('system_status', {}))}
            </body>
            </html>
            """
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            logger.error(f"HTML report export error: {e}")
            return False
    
    @staticmethod
    def _format_metrics_html(metrics: Dict) -> str:
        """HTML format metrics"""
        html = ""
        for key, value in metrics.items():
            css_class = "positive" if (isinstance(value, (int, float)) and value > 0) else ""
            if isinstance(value, float):
                formatted_value = f"{value:.2%}" if "ratio" in key or "return" in key else f"{value:.4f}"
            else:
                formatted_value = str(value)
            
            html += f'<div class="metric {css_class}">{key}: {formatted_value}</div>'
        return html
    
    @staticmethod
    def _format_status_html(status: Dict) -> str:
        """HTML format status"""
        html = ""
        for key, value in status.items():
            html += f'<div class="metric">{key}: {value}</div>'
        return html

class AsyncUtils:
    """Asynchronous utilitysi"""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float = 30.0):
        """Timeout bilan coroutine ishga tushirish"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Operation timed out after {timeout}s")
            return None
    
    @staticmethod
    async def retry_async(func, max_retries: int = 3, delay: float = 1.0):
        """Retry logic bilan async funksiya"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay}s")
                await asyncio.sleep(delay)
    
    @staticmethod
    async def gather_with_limiter(coros, limit: int = 5):
        """Coroutine'larni limit bilan gather qilish"""
        semaphore = asyncio.Semaphore(limit)
        
        async def limited_coro(coro):
            async with semaphore:
                return await coro
        
        limited_coros = [limited_coro(coro) for coro in coros]
        return await asyncio.gather(*limited_coros, return_exceptions=True)

class ValidationUtils:
    """Validation utilitysi"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Email validatsiyasi"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_ethereum_address(address: str) -> bool:
        """Ethereum address validatsiyasi"""
        if not address.startswith('0x'):
            return False
        if len(address) != 42:
            return False
        try:
            int(address, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_percentage(value: float, min_val: float = 0.0, max_val: float = 100.0) -> bool:
        """Foiz validatsiyasi"""
        return min_val <= value <= max_val
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Filename sanitization"""
        import re
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        return filename[:255]

class ConfigUtils:
    """Configuration utilitysi"""
    
    @staticmethod
    def load_config(config_file: str) -> Dict:
        """Config file yuklash"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Config loading error: {e}")
            return {}
    
    @staticmethod
    def save_config(config_data: Dict, config_file: str) -> bool:
        """Config file saqlash"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Config saving error: {e}")
            return False
    
    @staticmethod
    def merge_configs(*configs: Dict) -> Dict:
        """Config'larni birlashtirish"""
        merged = {}
        for config in configs:
            if isinstance(config, dict):
                merged.update(config)
        return merged

class LoggingUtils:
    """Logging utilitysi"""
    
    @staticmethod
    def setup_logging(level: str = "INFO", log_file: str = None):
        """Logging setup"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        handlers = [logging.StreamHandler()]
        if log_file:
            handlers.append(logging.FileHandler(log_file))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
    
    @staticmethod
    def log_performance_metrics(metrics: Dict, logger_name: str = "performance"):
        """Performance metrics logging"""
        logger = logging.getLogger(logger_name)
        logger.info(f"Performance metrics: {metrics}")
    
    @staticmethod
    def log_trade_execution(trade_data: Dict, logger_name: str = "trading"):
        """Trade execution logging"""
        logger = logging.getLogger(logger_name)
        logger.info(f"Trade executed: {trade_data}")
    
    @staticmethod
    def log_risk_alerts(alert_data: Dict, logger_name: str = "risk"):
        """Risk alerts logging"""
        logger = logging.getLogger(logger_name)
        logger.warning(f"Risk alert: {alert_data}")

# Export all utilities
__all__ = [
    'DataValidationUtils',
    'CalculationUtils',
    'PerformanceUtils',
    'DataProcessingUtils',
    'CryptoUtils',
    'ExportUtils',
    'AsyncUtils',
    'ValidationUtils',
    'ConfigUtils',
    'LoggingUtils'
]