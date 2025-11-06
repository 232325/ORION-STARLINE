"""
Economic Adaptation System Utilities

Ushbu modul Economic Cycle Adaptation va Comprehensive Self-Learning
tizimi uchun yordamchi funksiyalar va utilities ta'minlaydi.

Imkoniyatlar:
- Data validation utilities
- Mathematical helpers
- Performance calculation utilities
- Configuration management
- Reporting utilities
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
import json
import logging
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class DataValidator:
    """
    Data validation utilities
    """
    
    @staticmethod
    def validate_economic_data(data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate economic data quality
        """
        
        validation_results = {
            'is_valid': True,
            'issues': [],
            'quality_score': 1.0,
            'recommendations': []
        }
        
        if data.empty:
            validation_results.update({
                'is_valid': False,
                'issues': ['Empty dataset'],
                'quality_score': 0.0,
                'recommendations': ['Provide non-empty dataset']
            })
            return validation_results
        
        # Check for missing values
        missing_percentage = (data.isnull().sum().sum() / (data.shape[0] * data.shape[1])) * 100
        
        if missing_percentage > 20:
            validation_results['issues'].append(f'High missing data: {missing_percentage:.1f}%')
            validation_results['recommendations'].append('Implement data imputation or improve data collection')
            validation_results['quality_score'] *= 0.7
        
        # Check data types
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        non_numeric_columns = data.select_dtypes(exclude=[np.number]).columns
        
        if len(non_numeric_columns) > 0:
            validation_results['recommendations'].append(f'Consider converting to numeric: {list(non_numeric_columns)}')
        
        # Check for extreme values
        for col in numeric_columns:
            series = data[col].dropna()
            if len(series) > 0:
                z_scores = np.abs(stats.zscore(series))
                extreme_values_count = (z_scores > 3).sum()
                
                if extreme_values_count > len(series) * 0.05:  # More than 5% extreme values
                    validation_results['issues'].append(f'{col}: {extreme_values_count} extreme values detected')
                    validation_results['quality_score'] *= 0.9
        
        # Check temporal consistency
        if hasattr(data.index, 'freq') and data.index.freq is None:
            validation_results['recommendations'].append('Consider regularizing time series frequency')
        
        validation_results['is_valid'] = len(validation_results['issues']) == 0
        return validation_results
    
    @staticmethod
    def validate_performance_data(data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate performance data
        """
        
        validation_results = {
            'is_valid': True,
            'issues': [],
            'quality_score': 1.0
        }
        
        if data.empty:
            validation_results.update({
                'is_valid': False,
                'issues': ['Empty performance data'],
                'quality_score': 0.0
            })
            return validation_results
        
        # Check for reasonable returns
        for col in data.select_dtypes(include=[np.number]).columns:
            returns = data[col].pct_change().dropna()
            
            if (returns < -0.5).any():  # More than 50% daily loss
                validation_results['issues'].append(f'{col}: Unrealistic large losses detected')
                validation_results['quality_score'] *= 0.8
            
            if (returns > 0.5).any():  # More than 50% daily gain
                validation_results['issues'].append(f'{col}: Unrealistic large gains detected')
                validation_results['quality_score'] *= 0.8
        
        validation_results['is_valid'] = len(validation_results['issues']) == 0
        return validation_results

class MathHelpers:
    """
    Mathematical helper functions
    """
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio
        """
        
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        
        if excess_returns.std() == 0:
            return 0.0
        
        return (excess_returns.mean() * np.sqrt(252)) / (excess_returns.std() * np.sqrt(252))
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, target_return: float = 0.0) -> float:
        """
        Calculate Sortino ratio
        """
        
        excess_returns = returns - target_return / 252
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return float('inf')
        
        return (excess_returns.mean() * np.sqrt(252)) / (downside_returns.std() * np.sqrt(252))
    
    @staticmethod
    def calculate_max_drawdown(returns: pd.Series) -> float:
        """
        Calculate maximum drawdown
        """
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        return drawdown.min()
    
    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series) -> float:
        """
        Calculate Calmar ratio
        """
        
        annual_return = returns.mean() * 252
        max_dd = MathHelpers.calculate_max_drawdown(returns)
        
        if max_dd == 0:
            return float('inf')
        
        return annual_return / abs(max_dd)
    
    @staticmethod
    def calculate_information_ratio(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """
        Calculate Information ratio
        """
        
        # Align returns
        aligned_returns = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
        
        if aligned_returns.empty:
            return 0.0
        
        excess_returns = aligned_returns.iloc[:, 0] - aligned_returns.iloc[:, 1]
        
        if excess_returns.std() == 0:
            return 0.0
        
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    @staticmethod
    def calculate_beta(portfolio_returns: pd.Series, market_returns: pd.Series) -> float:
        """
        Calculate portfolio beta
        """
        
        # Align returns
        aligned_returns = pd.concat([portfolio_returns, market_returns], axis=1).dropna()
        
        if aligned_returns.empty:
            return 1.0
        
        covariance = aligned_returns.iloc[:, 0].cov(aligned_returns.iloc[:, 1])
        market_variance = aligned_returns.iloc[:, 1].var()
        
        if market_variance == 0:
            return 1.0
        
        return covariance / market_variance

class PerformanceCalculator:
    """
    Performance calculation utilities
    """
    
    @staticmethod
    def calculate_comprehensive_metrics(returns: pd.Series) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics
        """
        
        if returns.empty:
            return {}
        
        metrics = {}
        
        # Basic return metrics
        metrics['total_return'] = (1 + returns).prod() - 1
        metrics['annualized_return'] = returns.mean() * 252
        metrics['volatility'] = returns.std() * np.sqrt(252)
        
        # Risk-adjusted metrics
        metrics['sharpe_ratio'] = MathHelpers.calculate_sharpe_ratio(returns)
        metrics['sortino_ratio'] = MathHelpers.calculate_sortino_ratio(returns)
        metrics['calmar_ratio'] = MathHelpers.calculate_calmar_ratio(returns)
        
        # Drawdown metrics
        metrics['max_drawdown'] = MathHelpers.calculate_max_drawdown(returns)
        
        # Downside metrics
        downside_returns = returns[returns < 0]
        metrics['downside_deviation'] = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        metrics['downside_frequency'] = len(downside_returns) / len(returns)
        
        # Tail risk metrics
        metrics['var_95'] = np.percentile(returns, 5)
        metrics['cvar_95'] = returns[returns <= metrics['var_95']].mean() if len(returns[returns <= metrics['var_95']]) > 0 else metrics['var_95']
        
        # Consistency metrics
        positive_months = (returns > 0).sum()
        metrics['win_rate'] = positive_months / len(returns)
        
        # Skewness and kurtosis
        metrics['skewness'] = stats.skew(returns)
        metrics['kurtosis'] = stats.kurtosis(returns)
        
        return metrics
    
    @staticmethod
    def calculate_attribution_metrics(portfolio_returns: pd.DataFrame, 
                                    factor_returns: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate performance attribution metrics
        """
        
        attribution = {}
        
        for portfolio_col in portfolio_returns.columns:
            portfolio_series = portfolio_returns[portfolio_col].dropna()
            
            factor_attribution = {}
            
            for factor_col in factor_returns.columns:
                factor_series = factor_returns[factor_col].dropna()
                
                # Align data
                aligned_data = pd.concat([portfolio_series, factor_series], axis=1).dropna()
                
                if aligned_data.empty:
                    continue
                
                # Calculate factor loadings and attribution
                X = aligned_data.iloc[:, 1].values.reshape(-1, 1)
                y = aligned_data.iloc[:, 0].values
                
                # Linear regression to find factor sensitivity
                if len(y) > 2:
                    beta = np.cov(X.flatten(), y)[0, 1] / np.var(X.flatten())
                    factor_attribution[factor_col] = {
                        'beta': beta,
                        'return_contribution': beta * factor_series.mean(),
                        'attribution_percentage': (beta * factor_series.mean()) / portfolio_series.mean() if portfolio_series.mean() != 0 else 0
                    }
            
            attribution[portfolio_col] = factor_attribution
        
        return attribution

class ConfigurationManager:
    """
    Configuration management utilities
    """
    
    @staticmethod
    def create_default_config() -> Dict[str, Any]:
        """
        Create default system configuration
        """
        
        return {
            'system': {
                'name': 'Economic Adaptation System',
                'version': '1.0.0',
                'debug_mode': False,
                'logging_level': 'INFO'
            },
            'components': {
                'cycle_detector': {
                    'sensitivity_threshold': 0.1,
                    'min_cycle_length': 6,
                    'cycle_periods': {
                        'business_cycle': 48,
                        'kitchin_cycle': 40,
                        'juglar_cycle': 96,
                        'kondratiev_wave': 480
                    }
                },
                'adaptation_engine': {
                    'adaptation_sensitivity': 0.1,
                    'cycle_detection_threshold': 0.05,
                    'policy_response_params': {
                        'monetary_policy_impact': 0.8,
                        'fiscal_policy_impact': 0.6,
                        'regulatory_impact': 0.4
                    }
                },
                'learning_system': {
                    'learning_rates': {
                        'intraday': 0.1,
                        'daily': 0.05,
                        'weekly': 0.02,
                        'monthly': 0.01,
                        'quarterly': 0.005,
                        'yearly': 0.001
                    },
                    'memory_decay': 0.95,
                    'meta_learning_rate': 0.1
                }
            },
            'performance': {
                'benchmark_enabled': True,
                'calculation_frequency': 'daily',
                'risk_metrics': {
                    'var_confidence': 0.95,
                    'lookback_period': 252
                }
            },
            'integration': {
                'real_time_processing': True,
                'max_concurrent_processes': 4,
                'processing_timeout': 30,
                'data_validation_strict': True
            }
        }
    
    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file
        """
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logging.error(f"Failed to load config from {config_path}: {str(e)}")
            return ConfigurationManager.create_default_config()
    
    @staticmethod
    def save_config(config: Dict[str, Any], config_path: str) -> bool:
        """
        Save configuration to file
        """
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            return True
        except Exception as e:
            logging.error(f"Failed to save config to {config_path}: {str(e)}")
            return False
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration structure
        """
        
        issues = []
        
        # Required sections
        required_sections = ['system', 'components', 'performance', 'integration']
        for section in required_sections:
            if section not in config:
                issues.append(f"Missing required section: {section}")
        
        # System section validation
        if 'system' in config:
            system_config = config['system']
            if 'name' not in system_config:
                issues.append("System name not specified")
            if 'version' not in system_config:
                issues.append("System version not specified")
        
        # Components section validation
        if 'components' in config:
            components = config['components']
            required_components = ['cycle_detector', 'adaptation_engine', 'learning_system']
            for component in required_components:
                if component not in components:
                    issues.append(f"Missing required component: {component}")
        
        return len(issues) == 0, issues

class ReportGenerator:
    """
    Report generation utilities
    """
    
    @staticmethod
    def generate_analysis_report(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report
        """
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now(),
                'report_type': 'comprehensive_analysis',
                'data_quality': 'assessed'
            },
            'executive_summary': {},
            'detailed_findings': {},
            'recommendations': {},
            'risk_assessment': {},
            'performance_summary': {}
        }
        
        # Executive summary
        if 'cycle_analysis' in analysis_results:
            cycle_data = analysis_results['cycle_analysis']
            report['executive_summary']['current_regime'] = cycle_data.get('primary_cycle_analysis', {}).get('current_phase', 'unknown')
        
        if 'risk_analysis' in analysis_results:
            risk_data = analysis_results['risk_analysis']
            report['executive_summary']['risk_level'] = risk_data.get('overall_risk_assessment', {}).get('overall_risk_rating', 'unknown')
        
        # Detailed findings
        report['detailed_findings'] = {
            'cycle_analysis': analysis_results.get('cycle_analysis', {}),
            'indicator_analysis': analysis_results.get('indicator_analysis', {}),
            'adaptation_analysis': analysis_results.get('adaptation_analysis', {})
        }
        
        # Recommendations
        if 'strategic_recommendations' in analysis_results:
            report['recommendations'] = analysis_results['strategic_recommendations']
        
        # Risk assessment
        report['risk_assessment'] = analysis_results.get('risk_analysis', {})
        
        # Performance summary
        report['performance_summary'] = analysis_results.get('performance_analysis', {})
        
        return report
    
    @staticmethod
    def generate_performance_report(performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate performance analysis report
        """
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now(),
                'report_type': 'performance_analysis',
                'performance_period': 'analyzed'
            },
            'performance_highlights': {},
            'risk_metrics': {},
            'benchmark_comparison': {},
            'improvement_opportunities': {},
            'action_items': {}
        }
        
        # Performance highlights
        if 'cycle_adjusted_performance' in performance_results:
            cycle_perf = performance_results['cycle_adjusted_performance']
            report['performance_highlights'] = cycle_perf.get('cycle_performance_summary', {})
        
        # Risk metrics
        if 'performance_analysis' in performance_results:
            perf_analysis = performance_results['performance_analysis']
            report['risk_metrics'] = perf_analysis.get('risk_adjusted_returns', {})
        
        # Benchmark comparison
        if 'performance_benchmarking' in performance_results:
            benchmarking = performance_results['performance_benchmarking']
            report['benchmark_comparison'] = benchmarking.get('relative_performance', {})
        
        # Improvement opportunities
        report['improvement_opportunities'] = performance_results.get('improvement_analysis', {})
        
        # Action items
        report['action_items'] = performance_results.get('optimization_recommendations', {})
        
        return report
    
    @staticmethod
    def generate_adaptation_report(adaptation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate adaptation analysis report
        """
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now(),
                'report_type': 'adaptation_analysis',
                'adaptation_scope': 'comprehensive'
            },
            'adaptation_summary': {},
            'implementation_plan': {},
            'risk_assessment': {},
            'monitoring_requirements': {},
            'success_metrics': {}
        }
        
        # Adaptation summary
        if 'adaptation_engine_results' in adaptation_results:
            adaptation_engine = adaptation_results['adaptation_engine_results']
            report['adaptation_summary'] = {
                'adaptations_recommended': len(adaptation_engine.get('recommendations', {})),
                'implementation_priority': adaptation_engine.get('implementation_priority', {})
            }
        
        # Implementation plan
        if 'adaptation_timing' in adaptation_results:
            timing = adaptation_results['adaptation_timing']
            report['implementation_plan'] = timing.get('recommended_implementation_schedule', {})
        
        # Risk assessment
        report['risk_assessment'] = adaptation_results.get('adaptation_effectiveness', {})
        
        # Monitoring requirements
        if 'monitoring_priorities' in adaptation_results:
            report['monitoring_requirements'] = adaptation_results['monitoring_priorities']
        
        # Success metrics
        report['success_metrics'] = adaptation_results.get('adaptation_learning', {})
        
        return report
    
    @staticmethod
    def export_report_to_json(report: Dict[str, Any], file_path: str) -> bool:
        """
        Export report to JSON file
        """
        
        try:
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            return True
        except Exception as e:
            logging.error(f"Failed to export report to {file_path}: {str(e)}")
            return False

class SystemDiagnostics:
    """
    System diagnostics utilities
    """
    
    @staticmethod
    def diagnose_performance_issues(metrics: Dict[str, float]) -> List[str]:
        """
        Diagnose performance issues
        """
        
        issues = []
        
        # Sharpe ratio issues
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        if sharpe_ratio < 0.5:
            issues.append("Low risk-adjusted returns (Sharpe ratio < 0.5)")
        
        # Drawdown issues
        max_dd = metrics.get('max_drawdown', 0)
        if max_dd < -0.3:
            issues.append("Excessive drawdowns detected (>30%)")
        
        # Volatility issues
        volatility = metrics.get('volatility', 0)
        if volatility > 0.4:
            issues.append("High volatility risk (>40% annually)")
        
        # Win rate issues
        win_rate = metrics.get('win_rate', 0.5)
        if win_rate < 0.4:
            issues.append("Low win rate (<40%)")
        
        return issues
    
    @staticmethod
    def diagnose_data_quality(data: pd.DataFrame) -> List[str]:
        """
        Diagnose data quality issues
        """
        
        issues = []
        
        # Missing data
        missing_percentage = (data.isnull().sum().sum() / (data.shape[0] * data.shape[1])) * 100
        if missing_percentage > 15:
            issues.append(f"High missing data: {missing_percentage:.1f}%")
        
        # Extreme values
        for col in data.select_dtypes(include=[np.number]).columns:
            series = data[col].dropna()
            if len(series) > 0:
                z_scores = np.abs(stats.zscore(series))
                extreme_count = (z_scores > 3).sum()
                if extreme_count > len(series) * 0.1:
                    issues.append(f"{col}: {extreme_count} extreme values detected")
        
        # Data consistency
        if hasattr(data.index, 'freq') and data.index.freq is None:
            issues.append("Irregular time series frequency detected")
        
        return issues
    
    @staticmethod
    def generate_diagnostic_summary(system_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate system diagnostic summary
        """
        
        summary = {
            'overall_health': 'unknown',
            'component_issues': [],
            'performance_issues': [],
            'data_quality_issues': [],
            'recommendations': []
        }
        
        # System health assessment
        system_state = system_status.get('system_state', {})
        error_count = system_state.get('error_count', 0)
        status = system_state.get('status', 'unknown')
        
        if status == 'operational' and error_count == 0:
            summary['overall_health'] = 'healthy'
        elif status == 'operational' and error_count < 5:
            summary['overall_health'] = 'minor_issues'
        elif status in ['warning', 'error']:
            summary['overall_health'] = 'needs_attention'
        else:
            summary['overall_health'] = 'critical'
        
        # Component status check
        component_statuses = system_status.get('component_statuses', {})
        for component, status_info in component_statuses.items():
            if isinstance(status_info, dict) and status_info.get('status') in ['error', 'inactive']:
                summary['component_issues'].append(f"{component}: {status_info.get('status', 'unknown')}")
        
        # Performance metrics check
        performance_metrics = system_status.get('performance_metrics', {})
        error_rate = performance_metrics.get('error_rate', 0)
        
        if error_rate > 0.1:
            summary['performance_issues'].append(f"High error rate: {error_rate:.2%}")
        
        memory_usage = performance_metrics.get('memory_usage_percent', 0)
        if memory_usage > 85:
            summary['performance_issues'].append(f"High memory usage: {memory_usage:.1f}%")
        
        # Recommendations
        if summary['overall_health'] == 'critical':
            summary['recommendations'].append("Immediate system attention required")
        elif summary['overall_health'] == 'needs_attention':
            summary['recommendations'].append("Review system logs and component statuses")
        elif summary['overall_health'] == 'minor_issues':
            summary['recommendations'].append("Monitor system performance closely")
        else:
            summary['recommendations'].append("System operating normally")
        
        return summary

# Helper functions
def normalize_data(data: pd.DataFrame, method: str = 'standard') -> pd.DataFrame:
    """
    Normalize data using specified method
    """
    
    if method == 'standard':
        scaler = StandardScaler()
        normalized_data = pd.DataFrame(
            scaler.fit_transform(data.select_dtypes(include=[np.number])),
            columns=data.select_dtypes(include=[np.number]).columns,
            index=data.index
        )
    elif method == 'minmax':
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        normalized_data = pd.DataFrame(
            scaler.fit_transform(data.select_dtypes(include=[np.number])),
            columns=data.select_dtypes(include=[np.number]).columns,
            index=data.index
        )
    else:
        normalized_data = data.copy()
    
    return normalized_data

def calculate_rolling_correlations(data: pd.DataFrame, window: int = 252) -> pd.DataFrame:
    """
    Calculate rolling correlations between all numeric columns
    """
    
    numeric_data = data.select_dtypes(include=[np.number])
    rolling_corr = numeric_data.rolling(window=window).corr()
    
    return rolling_corr

def detect_outliers(data: pd.Series, method: str = 'zscore', threshold: float = 3.0) -> pd.Series:
    """
    Detect outliers in time series data
    """
    
    if method == 'zscore':
        z_scores = np.abs(stats.zscore(data.dropna()))
        outliers = z_scores > threshold
    elif method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        outliers = (data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))
    else:
        outliers = pd.Series(False, index=data.index)
    
    return outliers

def create_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Create common technical indicators
    """
    
    indicators = data.copy()
    
    for col in data.select_dtypes(include=[np.number]).columns:
        series = data[col]
        
        # Moving averages
        indicators[f'{col}_ma_5'] = series.rolling(5).mean()
        indicators[f'{col}_ma_20'] = series.rolling(20).mean()
        
        # Momentum indicators
        indicators[f'{col}_roc'] = series.pct_change(10) * 100
        
        # Volatility indicators
        indicators[f'{col}_volatility'] = series.rolling(20).std()
        
        # RSI (simplified)
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        indicators[f'{col}_rsi'] = 100 - (100 / (1 + rs))
    
    return indicators

def calculate_portfolio_metrics(returns_data: Dict[str, pd.Series], 
                               weights: Dict[str, float] = None) -> Dict[str, float]:
    """
    Calculate portfolio-level metrics
    """
    
    if weights is None:
        weights = {asset: 1.0/len(returns_data) for asset in returns_data}
    
    # Create weighted portfolio returns
    portfolio_returns = pd.Series(0, index=list(returns_data.values())[0].index)
    
    for asset, returns in returns_data.items():
        weight = weights.get(asset, 0)
        portfolio_returns += returns * weight
    
    # Calculate portfolio metrics
    portfolio_metrics = PerformanceCalculator.calculate_comprehensive_metrics(portfolio_returns)
    
    return portfolio_metrics