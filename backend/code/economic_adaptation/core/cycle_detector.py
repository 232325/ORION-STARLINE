"""
Economic Cycle Detection Module

Ushbu modul iqtisodiy sikllarni aniqlash, economic shock'larni va 
recovery fazalarini aniqlash uchun mo'ljallangan.

Imkoniyatlar:
- Business cycle detection
- Economic shock identification  
- Recovery phase detection
- Leading indicator integration
- Cycle phase classification
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

class CycleDetector:
    """
    Economic Cycle Detection va Analysis Class
    """
    
    def __init__(self, 
                 cycle_periods: dict = None,
                 sensitivity_threshold: float = 0.1,
                 min_cycle_length: int = 6):
        """
        Cycle Detector ni initialize qilish
        
        Args:
            cycle_periods: Iqtisodiy sikl davomiyligi (oylar)
            sensitivity_threshold: Shock detection uchun sezgirligi
            min_cycle_length: Minimal sikl davomiyligi
        """
        
        self.cycle_periods = cycle_periods or {
            'business_cycle': 48,  # 4 yil
            'kitchin_cycle': 40,   # ~3.3 yil  
            'juglar_cycle': 96,    # 8 yil
            'kondratiev_wave': 480 # 40 yil
        }
        
        self.sensitivity_threshold = sensitivity_threshold
        self.min_cycle_length = min_cycle_length
        
        # Cycle detection models
        self.hamilton_filter = None
        self.baxter_king_filter = None
        self.cycle_classifier = None
        
        # Historical cycle data
        self.cycle_history = []
        self.current_cycle_phase = 'unknown'
        self.cycle_start_date = None
        
    def detect_business_cycle(self, 
                            data: pd.DataFrame, 
                            target_column: str = 'gdp',
                            date_column: str = 'date') -> dict:
        """
        Business cycle ni aniqlash
        
        Args:
            data: Iqtisodiy ma'lumotlar DataFrame
            target_column: Target o'zgaruvchi nomi
            date_column: Sana ustuni nomi
            
        Returns:
            dict: Cycle detection natijalari
        """
        
        try:
            # Data preparation
            data = data.copy()
            data[date_column] = pd.to_datetime(data[date_column])
            data = data.set_index(date_column).sort_index()
            
            # Apply Hamilton filter for cycle extraction
            cycle_data = self._apply_hamilton_filter(data[target_column])
            
            # Identify cycle phases
            cycle_phases = self._identify_cycle_phases(cycle_data)
            
            # Detect economic shocks
            shocks = self._detect_economic_shocks(cycle_data)
            
            # Identify recovery periods
            recovery_periods = self._identify_recovery_periods(cycle_data, cycle_phases)
            
            # Leading indicator analysis
            leading_indicators = self._analyze_leading_indicators(data)
            
            results = {
                'cycle_data': cycle_data,
                'current_phase': cycle_phases.get('current_phase', 'unknown'),
                'cycle_duration_months': len(cycle_data),
                'shocks_detected': len(shocks),
                'recovery_periods': recovery_periods,
                'leading_signals': leading_indicators,
                'cycle_strength': self._calculate_cycle_strength(cycle_data),
                'historical_cycles': self._get_historical_comparison(cycle_data)
            }
            
            self.cycle_history.append({
                'date': data.index[-1],
                'phase': results['current_phase'],
                'strength': results['cycle_strength'],
                'shocks_count': results['shocks_detected']
            })
            
            return results
            
        except Exception as e:
            return {'error': f'Business cycle detection failed: {str(e)}'}
    
    def _apply_hamilton_filter(self, series: pd.Series) -> pd.Series:
        """
        Hamilton filter ni apply qilish (cycle extraction)
        """
        
        # Simple implementation of Hamilton filter
        # Real implementation would use more sophisticated methods
        
        # Trend estimation (8-period moving average)
        trend = series.rolling(window=8, min_periods=1).mean()
        
        # Cycle component extraction
        cycle = series - trend
        
        # Smooth cycle component
        cycle_smoothed = cycle.rolling(window=3, min_periods=1).mean()
        
        return cycle_smoothed
    
    def _identify_cycle_phases(self, cycle_data: pd.Series) -> dict:
        """
        Cycle fazalarini aniqlash (Expansion, Peak, Contraction, Trough)
        """
        
        if len(cycle_data) < self.min_cycle_length:
            return {'current_phase': 'insufficient_data'}
        
        # Calculate cycle derivatives for phase identification
        cycle_diff = cycle_data.diff()
        cycle_diff2 = cycle_data.diff().diff()
        
        # Current phase determination
        current_cycle = cycle_data.iloc[-1] if not cycle_data.empty else 0
        current_diff = cycle_diff.iloc[-1] if not cycle_diff.empty else 0
        
        # Phase classification logic
        if current_cycle > 0 and current_diff > 0:
            phase = 'expansion'
        elif current_cycle > 0 and current_diff < 0:
            phase = 'peak'
        elif current_cycle < 0 and current_diff < 0:
            phase = 'contraction' 
        elif current_cycle < 0 and current_diff > 0:
            phase = 'trough'
        else:
            phase = 'transition'
        
        return {
            'current_phase': phase,
            'cycle_level': current_cycle,
            'cycle_momentum': current_diff,
            'phase_confidence': abs(current_cycle) / (abs(current_cycle) + 0.01)
        }
    
    def _detect_economic_shocks(self, cycle_data: pd.Series) -> list:
        """
        Economic shock'larni aniqlash
        """
        
        if len(cycle_data) < 3:
            return []
        
        shocks = []
        
        # Calculate rolling statistics
        rolling_mean = cycle_data.rolling(window=12, min_periods=6).mean()
        rolling_std = cycle_data.rolling(window=12, min_periods=6).std()
        
        # Detect outliers (potential shocks)
        z_scores = (cycle_data - rolling_mean) / (rolling_std + 0.01)
        
        shock_threshold = self.sensitivity_threshold * 3
        
        for i, z_score in enumerate(z_scores):
            if abs(z_score) > shock_threshold:
                shocks.append({
                    'date': cycle_data.index[i],
                    'magnitude': z_score,
                    'direction': 'negative' if z_score < 0 else 'positive',
                    'severity': 'high' if abs(z_score) > shock_threshold * 2 else 'moderate'
                })
        
        return shocks
    
    def _identify_recovery_periods(self, 
                                 cycle_data: pd.Series, 
                                 cycle_phases: dict) -> list:
        """
        Recovery period'larini aniqlash
        """
        
        if len(cycle_data) < self.min_cycle_length:
            return []
        
        recovery_periods = []
        
        # Find trough-to-expansion transitions
        cycle_diff = cycle_data.diff()
        
        in_recovery = False
        recovery_start = None
        
        for i in range(1, len(cycle_data)):
            if cycle_data.iloc[i] < cycle_data.iloc[i-1] and cycle_data.iloc[i-1] < 0:
                # Entering recovery phase
                if not in_recovery:
                    in_recovery = True
                    recovery_start = cycle_data.index[i-1]
            
            elif in_recovery and cycle_data.iloc[i] > 0:
                # Exiting recovery phase
                recovery_periods.append({
                    'start_date': recovery_start,
                    'end_date': cycle_data.index[i],
                    'duration_months': i - list(cycle_data.index).index(recovery_start)
                })
                in_recovery = False
        
        return recovery_periods
    
    def _analyze_leading_indicators(self, data: pd.DataFrame) -> dict:
        """
        Leading indicator analysis
        """
        
        # Common leading indicators
        leading_indicators = {
            'consumer_sentiment': 'positive_correlation',
            'business_investment': 'positive_correlation', 
            'employment_rate': 'positive_correlation',
            'stock_market_performance': 'positive_correlation',
            'credit_conditions': 'positive_correlation',
            'inventory_levels': 'inverse_correlation'
        }
        
        analysis_results = {}
        
        for indicator, expected_relation in leading_indicators.items():
            if indicator in data.columns:
                # Simple correlation analysis
                correlation = data[indicator].corr(data.select_dtypes(include=[np.number]).iloc[:, 0])
                
                analysis_results[indicator] = {
                    'correlation': correlation,
                    'expected_relation': expected_relation,
                    'signal_strength': abs(correlation),
                    'signal_direction': 'supportive' if abs(correlation) > 0.3 else 'weak'
                }
        
        return analysis_results
    
    def _calculate_cycle_strength(self, cycle_data: pd.Series) -> float:
        """
        Cycle kuchini hisoblash
        """
        
        if len(cycle_data) < 2:
            return 0.0
        
        # Calculate cycle volatility
        cycle_volatility = cycle_data.std()
        
        # Calculate cycle persistence (autocorrelation)
        if len(cycle_data) > 1:
            autocorr = cycle_data.autocorr(lag=1)
        else:
            autocorr = 0
        
        # Combined strength metric
        strength = cycle_volatility * (1 + abs(autocorr))
        
        return min(strength, 1.0)  # Normalize to [0, 1]
    
    def _get_historical_comparison(self, cycle_data: pd.Series) -> dict:
        """
        Historical cycle comparison
        """
        
        if len(self.cycle_history) < 2:
            return {'comparison': 'insufficient_history'}
        
        current_strength = self._calculate_cycle_strength(cycle_data)
        
        # Compare with historical cycles
        historical_strengths = [cycle['strength'] for cycle in self.cycle_history]
        
        percentile = stats.percentileofscore(historical_strengths, current_strength)
        
        return {
            'current_strength_percentile': percentile,
            'historical_average': np.mean(historical_strengths),
            'historical_max': np.max(historical_strengths),
            'historical_min': np.min(historical_strengths),
            'relative_position': 'above_average' if percentile > 50 else 'below_average'
        }
    
    def get_cycle_forecast(self, 
                         data: pd.DataFrame, 
                         forecast_periods: int = 12) -> dict:
        """
        Cycle forecast yaratish
        """
        
        try:
            # Simple trend extrapolation for forecasting
            cycle_data = self._apply_hamilton_filter(data.iloc[:, 0])
            
            if len(cycle_data) < 6:
                return {'error': 'Insufficient data for forecasting'}
            
            # Linear trend estimation
            x = np.arange(len(cycle_data))
            y = cycle_data.values
            
            # Remove NaN values
            valid_mask = ~np.isnan(y)
            if np.sum(valid_mask) < 3:
                return {'error': 'Insufficient valid data for forecasting'}
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x[valid_mask], y[valid_mask])
            
            # Generate forecast
            forecast_x = np.arange(len(cycle_data), len(cycle_data) + forecast_periods)
            forecast_values = slope * forecast_x + intercept
            
            # Create forecast index
            last_date = data.index[-1]
            forecast_dates = pd.date_range(start=last_date, periods=forecast_periods + 1, freq='M')[1:]
            
            forecast_series = pd.Series(forecast_values, index=forecast_dates)
            
            # Confidence intervals (simplified)
            forecast_std = np.sqrt(np.mean((y[valid_mask] - (slope * x[valid_mask] + intercept))**2))
            confidence_upper = forecast_series + 1.96 * forecast_std
            confidence_lower = forecast_series - 1.96 * forecast_std
            
            return {
                'forecast': forecast_series.to_dict(),
                'confidence_upper': confidence_upper.to_dict(),
                'confidence_lower': confidence_lower.to_dict(),
                'forecast_reliability': r_value**2,
                'trend_direction': 'expansion' if slope > 0 else 'contraction',
                'expected_turning_point': len(cycle_data) + int(-intercept / slope) if slope != 0 else None
            }
            
        except Exception as e:
            return {'error': f'Cycle forecasting failed: {str(e)}'}