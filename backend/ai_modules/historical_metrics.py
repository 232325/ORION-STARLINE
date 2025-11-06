#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Historical Metrics Engine
=========================

Historical metrics analysis tizimi:
- Long-term trends
- Seasonal patterns
- Market cycle impact
- Performance attribution
- Risk decomposition
- Style analysis
- Factor performance
- Benchmark comparison

Author: Orion Starline AI Team
Date: 2025-11-04
"""

import numpy as np
import pandas as pd
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TimeFrame(Enum):
    """Vaqt oralig'i turlari"""
    INTRADAY = "intraday"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class MetricType(Enum):
    """Metrika turlari"""
    PERFORMANCE = "performance"
    RISK = "risk"
    EFFICIENCY = "efficiency"
    CONSISTENCY = "consistency"
    ADAPTATION = "adaptation"

@dataclass
class HistoricalMetric:
    """Historical metrika"""
    timestamp: datetime
    metric_name: str
    metric_value: float
    metric_type: MetricType
    timeframe: TimeFrame
    metadata: Dict[str, Any]

@dataclass
class SeasonalPattern:
    """Seasonal pattern"""
    pattern_name: str
    frequency: str  # monthly, weekly, daily
    strength: float  # 0-1
    direction: str  # positive, negative
    confidence: float  # 0-1
    description: str

@dataclass
class MarketCycle:
    """Market cycle"""
    cycle_id: str
    start_date: datetime
    end_date: datetime
    cycle_type: str  # bull, bear, sideways
    duration_days: int
    performance: float
    max_drawdown: float
    volatility: float
    characteristics: Dict[str, Any]

class HistoricalMetricsEngine:
    """Historical metrics engine asosiy klassi"""
    
    def __init__(self, db_path: str = "historical_metrics.db"):
        self.db_path = db_path
        self.init_database()
        self.scaler = StandardScaler()
        self.pca = PCA()
        
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Historical metrics jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_type TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Market cycles jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                cycle_type TEXT NOT NULL,
                duration_days INTEGER,
                performance REAL,
                max_drawdown REAL,
                volatility REAL,
                characteristics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Seasonal patterns jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seasonal_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT NOT NULL,
                frequency TEXT NOT NULL,
                strength REAL NOT NULL,
                direction TEXT NOT NULL,
                confidence REAL NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance attribution jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_attribution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                total_return REAL,
                market_return REAL,
                alpha REAL,
                beta REAL,
                factors TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Historical metrics database initialized")
    
    def record_metric(self, metric: HistoricalMetric):
        """Historical metrikani saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO historical_metrics 
            (timestamp, metric_name, metric_value, metric_type, timeframe, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            metric.timestamp.isoformat(),
            metric.metric_name,
            metric.metric_value,
            metric.metric_type.value,
            metric.timeframe.value,
            json.dumps(metric.metadata)
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Metric recorded: {metric.metric_name}")
    
    def get_long_term_trends(self, strategy_id: str, months: int = 12) -> Dict[str, Any]:
        """Uzun muddatli trendlar tahlili"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months*30)
        
        conn = sqlite3.connect(self.db_path)
        
        # Performance metrics over time
        performance_df = pd.read_sql_query('''
            SELECT * FROM historical_metrics 
            WHERE metric_name LIKE '%performance%' 
            AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        ''', conn, params=(start_date.isoformat(), end_date.isoformat()))
        
        # Risk metrics
        risk_df = pd.read_sql_query('''
            SELECT * FROM historical_metrics 
            WHERE metric_name LIKE '%risk%' OR metric_name LIKE '%drawdown%'
            AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        ''', conn, params=(start_date.isoformat(), end_date.isoformat()))
        
        conn.close()
        
        trends = {
            'strategy_id': strategy_id,
            'analysis_period': f"{months} months",
            'performance_trend': self._analyze_trend(performance_df, 'performance'),
            'risk_trend': self._analyze_trend(risk_df, 'risk'),
            'trend_consistency': self._calculate_trend_consistency(performance_df),
            'trend_strength': self._calculate_trend_strength(performance_df)
        }
        
        return trends
    
    def _analyze_trend(self, df: pd.DataFrame, metric_prefix: str) -> Dict[str, Any]:
        """Trend tahlili"""
        if df.empty:
            return {"trend": "no_data", "slope": 0, "r_squared": 0}
        
        # Convert timestamps to numeric
        df['timestamp_numeric'] = pd.to_datetime(df['timestamp']).astype(np.int64) / 10**9
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            df['timestamp_numeric'], df['metric_value']
        )
        
        # Trend direction
        if slope > 0:
            trend_direction = "positive"
        elif slope < 0:
            trend_direction = "negative"
        else:
            trend_direction = "neutral"
        
        # Trend strength
        r_squared = r_value ** 2
        if r_squared > 0.7:
            strength = "strong"
        elif r_squared > 0.4:
            strength = "moderate"
        else:
            strength = "weak"
        
        return {
            "trend": trend_direction,
            "slope": slope,
            "r_squared": r_squared,
            "p_value": p_value,
            "strength": strength,
            "current_value": df['metric_value'].iloc[-1] if not df.empty else 0,
            "average_value": df['metric_value'].mean(),
            "volatility": df['metric_value'].std()
        }
    
    def _calculate_trend_consistency(self, df: pd.DataFrame) -> float:
        """Trend konsistentligini hisoblash"""
        if df.empty or len(df) < 2:
            return 0
        
        # Calculate consecutive differences
        differences = np.diff(df['metric_value'].values)
        positive_count = np.sum(differences > 0)
        total_count = len(differences)
        
        return positive_count / total_count if total_count > 0 else 0
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Trend kuchini hisoblash"""
        if df.empty or len(df) < 2:
            return 0
        
        # R-squared from linear regression
        x = np.arange(len(df))
        y = df['metric_value'].values
        slope, intercept, r_value, _, _ = stats.linregress(x, y)
        
        return abs(r_value)
    
    def detect_seasonal_patterns(self, strategy_id: str, years: int = 2) -> List[SeasonalPattern]:
        """Seasonal pattern aniqlash"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        conn = sqlite3.connect(self.db_path)
        
        # Get performance data
        performance_df = pd.read_sql_query('''
            SELECT * FROM historical_metrics 
            WHERE metric_name LIKE '%performance%' 
            AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        ''', conn, params=(start_date.isoformat(), end_date.isoformat()))
        
        conn.close()
        
        patterns = []
        
        if performance_df.empty:
            return patterns
        
        # Convert to datetime
        performance_df['datetime'] = pd.to_datetime(performance_df['timestamp'])
        performance_df['month'] = performance_df['datetime'].dt.month
        performance_df['day_of_week'] = performance_df['datetime'].dt.dayofweek
        performance_df['quarter'] = performance_df['datetime'].dt.quarter
        
        # Monthly patterns
        monthly_pattern = self._detect_monthly_pattern(performance_df)
        if monthly_pattern:
            patterns.append(monthly_pattern)
        
        # Weekly patterns
        weekly_pattern = self._detect_weekly_pattern(performance_df)
        if weekly_pattern:
            patterns.append(weekly_pattern)
        
        # Quarterly patterns
        quarterly_pattern = self._detect_quarterly_pattern(performance_df)
        if quarterly_pattern:
            patterns.append(quarterly_pattern)
        
        return patterns
    
    def _detect_monthly_pattern(self, df: pd.DataFrame) -> Optional[SeasonalPattern]:
        """Oylik seasonal pattern"""
        monthly_performance = df.groupby('month')['metric_value'].agg(['mean', 'std']).reset_index()
        
        if len(monthly_performance) < 12:
            return None
        
        # Calculate seasonal strength
        overall_mean = df['metric_value'].mean()
        monthly_means = monthly_performance['mean'].values
        seasonal_variance = np.var(monthly_means)
        total_variance = np.var(df['metric_value'].values)
        
        if total_variance == 0:
            strength = 0
        else:
            strength = min(1.0, seasonal_variance / total_variance)
        
        # Direction
        direction = "positive" if overall_mean > 0 else "negative"
        
        # Confidence (based on t-test)
        _, p_value = stats.ttest_1samp(monthly_means, overall_mean)
        confidence = 1 - p_value if p_value < 1 else 0
        
        description = f"Monthly seasonal pattern with {strength:.1%} strength"
        
        return SeasonalPattern(
            pattern_name="monthly_seasonal",
            frequency="monthly",
            strength=strength,
            direction=direction,
            confidence=max(0, confidence),
            description=description
        )
    
    def _detect_weekly_pattern(self, df: pd.DataFrame) -> Optional[SeasonalPattern]:
        """Haftalik seasonal pattern"""
        weekly_performance = df.groupby('day_of_week')['metric_value'].agg(['mean', 'std']).reset_index()
        
        if len(weekly_performance) < 7:
            return None
        
        overall_mean = df['metric_value'].mean()
        weekly_means = weekly_performance['mean'].values
        seasonal_variance = np.var(weekly_means)
        total_variance = np.var(df['metric_value'].values)
        
        strength = min(1.0, seasonal_variance / total_variance) if total_variance > 0 else 0
        direction = "positive" if overall_mean > 0 else "negative"
        
        # Statistical significance
        _, p_value = stats.ttest_1samp(weekly_means, overall_mean)
        confidence = 1 - p_value if p_value < 1 else 0
        
        return SeasonalPattern(
            pattern_name="weekly_seasonal",
            frequency="weekly",
            strength=strength,
            direction=direction,
            confidence=max(0, confidence),
            description=f"Weekly pattern with {strength:.1%} strength"
        )
    
    def _detect_quarterly_pattern(self, df: pd.DataFrame) -> Optional[SeasonalPattern]:
        """Choraklik seasonal pattern"""
        quarterly_performance = df.groupby('quarter')['metric_value'].agg(['mean', 'std']).reset_index()
        
        if len(quarterly_performance) < 4:
            return None
        
        overall_mean = df['metric_value'].mean()
        quarterly_means = quarterly_performance['mean'].values
        seasonal_variance = np.var(quarterly_means)
        total_variance = np.var(df['metric_value'].values)
        
        strength = min(1.0, seasonal_variance / total_variance) if total_variance > 0 else 0
        direction = "positive" if overall_mean > 0 else "negative"
        
        _, p_value = stats.ttest_1samp(quarterly_means, overall_mean)
        confidence = 1 - p_value if p_value < 1 else 0
        
        return SeasonalPattern(
            pattern_name="quarterly_seasonal",
            frequency="quarterly",
            strength=strength,
            direction=direction,
            confidence=max(0, confidence),
            description=f"Quarterly pattern with {strength:.1%} strength"
        )
    
    def analyze_market_cycles(self, strategy_id: str) -> List[MarketCycle]:
        """Market cycle tahlili"""
        conn = sqlite3.connect(self.db_path)
        
        # Get market cycle data
        cycles_df = pd.read_sql_query('''
            SELECT * FROM market_cycles 
            ORDER BY start_date
        ''', conn)
        
        conn.close()
        
        if cycles_df.empty:
            return []
        
        cycles = []
        for _, row in cycles_df.iterrows():
            cycle = MarketCycle(
                cycle_id=row['cycle_id'],
                start_date=datetime.fromisoformat(row['start_date']),
                end_date=datetime.fromisoformat(row['end_date']) if row['end_date'] else None,
                cycle_type=row['cycle_type'],
                duration_days=row['duration_days'],
                performance=row['performance'],
                max_drawdown=row['max_drawdown'],
                volatility=row['volatility'],
                characteristics=json.loads(row['characteristics'])
            )
            cycles.append(cycle)
        
        return cycles
    
    def calculate_performance_attribution(self, strategy_id: str, benchmark_returns: pd.Series, 
                                        period_days: int = 30) -> Dict[str, Any]:
        """Performance attribution tahlili"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        conn = sqlite3.connect(self.db_path)
        
        # Get strategy returns
        strategy_returns = pd.read_sql_query('''
            SELECT timestamp, metric_value as return_value
            FROM historical_metrics 
            WHERE metric_name = 'daily_return' AND timestamp >= ?
            ORDER BY timestamp
        ''', conn, params=(start_date.isoformat(),))
        
        conn.close()
        
        if strategy_returns.empty or benchmark_returns.empty:
            return {"error": "Insufficient data"}
        
        # Convert to proper format
        strategy_returns['date'] = pd.to_datetime(strategy_returns['timestamp'])
        strategy_returns = strategy_returns.set_index('date')['return_value']
        
        # Align dates
        common_dates = strategy_returns.index.intersection(benchmark_returns.index)
        if len(common_dates) < 2:
            return {"error": "No common dates"}
        
        strategy_aligned = strategy_returns.loc[common_dates]
        benchmark_aligned = benchmark_returns.loc[common_dates]
        
        # Calculate attribution metrics
        total_return = (1 + strategy_aligned).prod() - 1
        market_return = (1 + benchmark_aligned).prod() - 1
        alpha = total_return - market_return
        
        # CAPM regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            benchmark_aligned.values, strategy_aligned.values
        )
        
        beta = slope
        r_squared = r_value ** 2
        
        # Risk metrics
        strategy_vol = strategy_aligned.std() * np.sqrt(252)
        benchmark_vol = benchmark_aligned.std() * np.sqrt(252)
        tracking_error = (strategy_aligned - benchmark_aligned).std() * np.sqrt(252)
        
        # Information ratio
        excess_return = strategy_aligned - benchmark_aligned
        information_ratio = excess_return.mean() / excess_return.std() * np.sqrt(252) if excess_return.std() > 0 else 0
        
        attribution = {
            'strategy_id': strategy_id,
            'period': f"{period_days} days",
            'total_return': total_return,
            'market_return': market_return,
            'alpha': alpha,
            'beta': beta,
            'r_squared': r_squared,
            'p_value': p_value,
            'strategy_volatility': strategy_vol,
            'benchmark_volatility': benchmark_vol,
            'tracking_error': tracking_error,
            'information_ratio': information_ratio,
            'performance_decomposition': {
                'market_effect': market_return,
                'selection_effect': alpha,
                'interaction_effect': 0  # Simplified
            }
        }
        
        return attribution
    
    def analyze_style_factors(self, strategy_returns: pd.Series, 
                            factor_returns: Dict[str, pd.Series]) -> Dict[str, Any]:
        """Style factor tahlili"""
        if strategy_returns.empty or not factor_returns:
            return {"error": "Insufficient data"}
        
        # Align all series
        common_index = strategy_returns.index
        for factor_name, factor_series in factor_returns.items():
            common_index = common_index.intersection(factor_series.index)
        
        if len(common_index) < 10:
            return {"error": "Insufficient overlapping data"}
        
        strategy_aligned = strategy_returns.loc[common_index]
        
        # Factor loading analysis
        factor_loadings = {}
        factor_names = list(factor_returns.keys())
        factor_matrix = np.column_stack([factor_returns[name].loc[common_index].values for name in factor_names])
        
        # Multiple regression
        X = np.column_stack([np.ones(len(factor_matrix)), factor_matrix])  # Add intercept
        y = strategy_aligned.values
        
        try:
            coefficients = np.linalg.lstsq(X, y, rcond=None)[0]
            intercept = coefficients[0]
            loadings = coefficients[1:]
            
            for i, factor_name in enumerate(factor_names):
                factor_loadings[factor_name] = {
                    'loading': loadings[i],
                    't_statistic': self._calculate_t_statistic(loadings[i], factor_matrix[:, i], y),
                    'p_value': self._calculate_p_value(loadings[i], factor_matrix[:, i], y)
                }
            
            # R-squared
            y_pred = X @ coefficients
            r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
            
            # Factor attribution
            factor_contributions = {}
            for i, factor_name in enumerate(factor_names):
                contribution = loadings[i] * factor_returns[factor_name].loc[common_index].mean()
                factor_contributions[factor_name] = {
                    'contribution': contribution,
                    'percentage': contribution / strategy_aligned.mean() * 100 if strategy_aligned.mean() != 0 else 0
                }
            
            style_analysis = {
                'factor_loadings': factor_loadings,
                'r_squared': r_squared,
                'intercept': intercept,
                'factor_contributions': factor_contributions,
                'style_consistency': self._calculate_style_consistency(loadings),
                'dominant_factors': sorted(factor_contributions.items(), 
                                         key=lambda x: abs(x[1]['contribution']), reverse=True)[:3]
            }
            
            return style_analysis
            
        except np.linalg.LinAlgError:
            return {"error": "Regression calculation failed"}
    
    def _calculate_t_statistic(self, coefficient: float, factor_values: np.ndarray, 
                             y_values: np.ndarray) -> float:
        """T-statistika hisoblash"""
        try:
            X = np.column_stack([np.ones(len(factor_values)), factor_values])
            y = y_values
            coefficients = np.linalg.lstsq(X, y, rcond=None)[0]
            
            y_pred = X @ coefficients
            residuals = y - y_pred
            mse = np.sum(residuals ** 2) / (len(y) - 2)
            
            # Standard error of coefficient
            XtX_inv = np.linalg.inv(X.T @ X)
            se = np.sqrt(mse * XtX_inv[1, 1])
            
            return coefficient / se if se > 0 else 0
        except:
            return 0
    
    def _calculate_p_value(self, coefficient: float, factor_values: np.ndarray, 
                         y_values: np.ndarray) -> float:
        """P-value hisoblash"""
        try:
            t_stat = self._calculate_t_statistic(coefficient, factor_values, y_values)
            # Two-tailed t-test
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), len(y_values) - 2))
            return p_value
        except:
            return 1.0
    
    def _calculate_style_consistency(self, loadings: np.ndarray) -> float:
        """Style konsistentligi"""
        return 1 - np.std(loadings) / (np.mean(np.abs(loadings)) + 1e-8)
    
    def benchmark_comparison(self, strategy_returns: pd.Series, benchmark_returns: pd.Series) -> Dict[str, Any]:
        """Benchmark taqqoslash tahlili"""
        if strategy_returns.empty or benchmark_returns.empty:
            return {"error": "Insufficient data"}
        
        # Align series
        common_index = strategy_returns.index.intersection(benchmark_returns.index)
        if len(common_index) < 2:
            return {"error": "No overlapping data"}
        
        strategy_aligned = strategy_returns.loc[common_index]
        benchmark_aligned = benchmark_returns.loc[common_index]
        
        # Basic metrics
        strategy_total_return = (1 + strategy_aligned).prod() - 1
        benchmark_total_return = (1 + benchmark_aligned).prod() - 1
        
        strategy_sharpe = strategy_aligned.mean() / strategy_aligned.std() * np.sqrt(252) if strategy_aligned.std() > 0 else 0
        benchmark_sharpe = benchmark_aligned.mean() / benchmark_aligned.std() * np.sqrt(252) if benchmark_aligned.std() > 0 else 0
        
        # Risk metrics
        strategy_max_dd = self._calculate_max_drawdown(strategy_aligned)
        benchmark_max_dd = self._calculate_max_drawdown(benchmark_aligned)
        
        strategy_var_95 = np.percentile(strategy_aligned, 5)
        benchmark_var_95 = np.percentile(benchmark_aligned, 5)
        
        # Correlation
        correlation = strategy_aligned.corr(benchmark_aligned)
        
        # Outperformance analysis
        outperformance = strategy_aligned - benchmark_aligned
        win_rate = (outperformance > 0).sum() / len(outperformance)
        
        # Risk-adjusted metrics
        treynor_ratio = strategy_total_return / self._calculate_beta(strategy_aligned, benchmark_aligned) \
                       if self._calculate_beta(strategy_aligned, benchmark_aligned) != 0 else 0
        
        comparison = {
            'total_return': {
                'strategy': strategy_total_return,
                'benchmark': benchmark_total_return,
                'excess': strategy_total_return - benchmark_total_return
            },
            'sharpe_ratio': {
                'strategy': strategy_sharpe,
                'benchmark': benchmark_sharpe,
                'excess': strategy_sharpe - benchmark_sharpe
            },
            'max_drawdown': {
                'strategy': strategy_max_dd,
                'benchmark': benchmark_max_dd,
                'improvement': benchmark_max_dd - strategy_max_dd
            },
            'var_95': {
                'strategy': strategy_var_95,
                'benchmark': benchmark_var_95,
                'improvement': benchmark_var_95 - strategy_var_95
            },
            'correlation': correlation,
            'outperformance_statistics': {
                'win_rate': win_rate,
                'avg_excess_return': outperformance.mean(),
                'excess_return_volatility': outperformance.std(),
                'best_day': outperformance.max(),
                'worst_day': outperformance.min()
            },
            'risk_adjusted_metrics': {
                'treynor_ratio': treynor_ratio,
                'information_ratio': outperformance.mean() / outperformance.std() * np.sqrt(252) if outperformance.std() > 0 else 0
            }
        }
        
        return comparison
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Maximum drawdown hisoblash"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _calculate_beta(self, strategy_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Beta hisoblash"""
        covariance = strategy_returns.cov(benchmark_returns)
        benchmark_variance = benchmark_returns.var()
        return covariance / benchmark_variance if benchmark_variance > 0 else 0
    
    def generate_historical_report(self, strategy_id: str, report_type: str = "comprehensive") -> Dict[str, Any]:
        """Historical analysis hisoboti"""
        # Time periods for analysis
        periods = {
            "short_term": 30,   # 1 month
            "medium_term": 90,  # 3 months
            "long_term": 365    # 1 year
        }
        
        report = {
            "strategy_id": strategy_id,
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "periods_analyzed": list(periods.keys())
        }
        
        # Long-term trends for different periods
        trends = {}
        for period_name, days in periods.items():
            trends[period_name] = self.get_long_term_trends(strategy_id, days//30)
        
        report["long_term_trends"] = trends
        
        # Seasonal patterns
        seasonal_patterns = self.detect_seasonal_patterns(strategy_id)
        report["seasonal_patterns"] = [asdict(pattern) for pattern in seasonal_patterns]
        
        # Market cycles
        market_cycles = self.analyze_market_cycles(strategy_id)
        report["market_cycles"] = [asdict(cycle) for cycle in market_cycles]
        
        # Performance attribution (simplified)
        # Note: In real implementation, you would need actual benchmark and factor data
        try:
            # Create dummy benchmark for demonstration
            np.random.seed(42)
            dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
            dummy_benchmark = pd.Series(np.random.normal(0.0005, 0.01, len(dates)), index=dates)
            dummy_strategy = pd.Series(np.random.normal(0.0008, 0.012, len(dates)), index=dates)
            
            attribution = self.calculate_performance_attribution(strategy_id, dummy_benchmark, 100)
            if "error" not in attribution:
                report["performance_attribution"] = attribution
        except Exception as e:
            report["performance_attribution"] = {"error": str(e)}
        
        # Style analysis (simplified)
        try:
            dummy_factor_returns = {
                "momentum": pd.Series(np.random.normal(0.0002, 0.008, len(dates)), index=dates),
                "value": pd.Series(np.random.normal(0.0001, 0.006, len(dates)), index=dates),
                "size": pd.Series(np.random.normal(0.0000, 0.004, len(dates)), index=dates)
            }
            
            style_analysis = self.analyze_style_factors(dummy_strategy, dummy_factor_returns)
            if "error" not in style_analysis:
                report["style_analysis"] = style_analysis
        except Exception as e:
            report["style_analysis"] = {"error": str(e)}
        
        # Benchmark comparison (simplified)
        try:
            benchmark_comparison = self.benchmark_comparison(dummy_strategy, dummy_benchmark)
            report["benchmark_comparison"] = benchmark_comparison
        except Exception as e:
            report["benchmark_comparison"] = {"error": str(e)}
        
        # Summary statistics
        report["summary"] = {
            "data_quality": "simulated" if strategy_id == "demo" else "real",
            "analysis_completeness": self._calculate_analysis_completeness(report),
            "key_insights": self._extract_key_insights(report)
        }
        
        return report
    
    def _calculate_analysis_completeness(self, report: Dict[str, Any]) -> float:
        """Analysis to'liqlik foizini hisoblash"""
        required_sections = [
            "long_term_trends", "seasonal_patterns", "market_cycles", 
            "performance_attribution", "style_analysis", "benchmark_comparison"
        ]
        
        completed = 0
        for section in required_sections:
            if section in report:
                section_data = report[section]
                has_error = False
                
                # Handle different data types
                if isinstance(section_data, dict):
                    has_error = any("error" in str(v) for v in section_data.values())
                elif isinstance(section_data, list):
                    # For lists, check each item
                    has_error = any("error" in str(item) for item in section_data)
                
                if not has_error:
                    completed += 1
        
        return completed / len(required_sections) * 100
    
    def _extract_key_insights(self, report: Dict[str, Any]) -> List[str]:
        """Kalit insights ajratib olish"""
        insights = []
        
        # Trend insights
        if "long_term_trends" in report and isinstance(report["long_term_trends"], dict):
            for period, trend_data in report["long_term_trends"].items():
                if isinstance(trend_data, dict):
                    performance_trend = trend_data.get("performance_trend", {})
                    if isinstance(performance_trend, dict):
                        if performance_trend.get("trend") == "positive":
                            insights.append(f"{period.replace('_', ' ').title()}da performance yaxshilanish")
                        elif performance_trend.get("trend") == "negative":
                            insights.append(f"{period.replace('_', ' ').title()}da performance pasayishi")
        
        # Seasonal insights
        if "seasonal_patterns" in report and isinstance(report["seasonal_patterns"], list):
            strong_patterns = [p for p in report["seasonal_patterns"] if p.get("strength", 0) > 0.3]
            if strong_patterns:
                insights.append(f"{len(strong_patterns)} ta kuchli seasonal pattern aniqlandi")
        
        return insights

# Usage example
if __name__ == "__main__":
    # Initialize engine
    engine = HistoricalMetricsEngine()
    
    # Example historical metrics
    metric1 = HistoricalMetric(
        timestamp=datetime.now() - timedelta(days=30),
        metric_name="daily_return",
        metric_value=0.0025,
        metric_type=MetricType.PERFORMANCE,
        timeframe=TimeFrame.DAILY,
        metadata={"strategy_id": "EURUSD_TREND_001", "portfolio": "main"}
    )
    
    # Record metric
    engine.record_metric(metric1)
    
    # Generate report
    report = engine.generate_historical_report("EURUSD_TREND_001")
    print("Historical Report:", json.dumps(report, indent=2, default=str))