"""
Economic Indicators Analysis Module

Ushbu modul turli xil iqtisodiy ko'rsatkichlarni tahlil qilish,
leading, coincident va lagging indicator'larni aniqlash uchun mo'ljallangan.

Imkoniyatlar:
- Leading indicator integration
- Coincident indicator monitoring  
- Lagging indicator tracking
- Composite indicator construction
- Indicator synchronization analysis
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import mutual_info_score
import warnings
warnings.filterwarnings('ignore')

class EconomicIndicators:
    """
    Economic Indicators Analysis va Integration Class
    """
    
    def __init__(self):
        """
        Economic Indicators ni initialize qilish
        """
        
        # Indicator classifications
        self.indicator_types = {
            'leading': {
                'consumer_sentiment': {'weight': 1.0, 'lag_months': 0},
                'business_investment': {'weight': 1.2, 'lag_months': 1},
                'employment_initial': {'weight': 1.1, 'lag_months': 0},
                'credit_conditions': {'weight': 1.0, 'lag_months': 2},
                'stock_market': {'weight': 0.9, 'lag_months': 1},
                'housing_starts': {'weight': 1.1, 'lag_months': 3},
                'manufacturing_new_orders': {'weight': 1.0, 'lag_months': 1}
            },
            'coincident': {
                'gdp': {'weight': 1.0, 'lag_months': 0},
                'industrial_production': {'weight': 1.0, 'lag_months': 0},
                'employment_rate': {'weight': 1.0, 'lag_months': 0},
                'personal_income': {'weight': 1.0, 'lag_months': 0},
                'retail_sales': {'weight': 1.0, 'lag_months': 0}
            },
            'lagging': {
                'unemployment_rate': {'weight': 0.8, 'lag_months': 6},
                'inventory_levels': {'weight': 0.7, 'lag_months': 8},
                'labor_cost': {'weight': 0.6, 'lag_months': 12},
                'consumer_price_index': {'weight': 0.8, 'lag_months': 6},
                'producer_price_index': {'weight': 0.7, 'lag_months': 9}
            }
        }
        
        # Composite indicators
        self.composite_indicators = {}
        
        # Synchronization metrics
        self.synchronization_matrix = None
        self.correlation_matrix = None
        
    def analyze_indicators(self, 
                          data: pd.DataFrame,
                          target_indicators: list = None) -> dict:
        """
        Iqtisodiy ko'rsatkichlarni comprehensive tahlil
        
        Args:
            data: Indicator ma'lumotlar DataFrame
            target_indicators: Tahlil qilinadigan indikatorlar ro'yxati
            
        Returns:
            dict: Comprehensive indicator analysis
        """
        
        try:
            if target_indicators is None:
                target_indicators = list(data.columns)
            
            # Data validation
            data_clean = self._validate_and_clean_data(data)
            
            if data_clean.empty:
                return {'error': 'Invalid or empty data'}
            
            # Individual indicator analysis
            indicator_analysis = self._analyze_individual_indicators(data_clean, target_indicators)
            
            # Composite indicator construction
            composite_analysis = self._construct_composite_indicators(data_clean)
            
            # Leading indicator integration
            leading_analysis = self._integrate_leading_indicators(data_clean)
            
            # Synchronization analysis
            sync_analysis = self._analyze_synchronization(data_clean, target_indicators)
            
            # Composite dashboard score
            composite_score = self._calculate_composite_dashboard_score(
                indicator_analysis, composite_analysis, leading_analysis
            )
            
            results = {
                'individual_indicators': indicator_analysis,
                'composite_indicators': composite_analysis,
                'leading_integration': leading_analysis,
                'synchronization': sync_analysis,
                'composite_dashboard_score': composite_score,
                'data_quality': self._assess_data_quality(data_clean),
                'summary': self._generate_summary_report(
                    indicator_analysis, composite_analysis, leading_analysis, composite_score
                )
            }
            
            return results
            
        except Exception as e:
            return {'error': f'Indicator analysis failed: {str(e)}'}
    
    def _validate_and_clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Ma'lumotlarni validatsiya va tozalash
        """
        
        data_clean = data.copy()
        
        # Remove columns with too many NaN values (>50%)
        nan_threshold = len(data_clean) * 0.5
        data_clean = data_clean.dropna(axis=1, thresh=nan_threshold)
        
        # Forward fill missing values
        data_clean = data_clean.fillna(method='ffill')
        
        # Backward fill remaining NaNs
        data_clean = data_clean.fillna(method='bfill')
        
        return data_clean
    
    def _analyze_individual_indicators(self, 
                                     data: pd.DataFrame, 
                                     indicators: list) -> dict:
        """
        Individual indicator'larni tahlil qilish
        """
        
        analysis = {}
        
        for indicator in indicators:
            if indicator not in data.columns:
                continue
                
            series = data[indicator]
            
            # Basic statistics
            stats_analysis = {
                'mean': series.mean(),
                'std': series.std(),
                'min': series.min(),
                'max': series.max(),
                'skewness': stats.skew(series.dropna()),
                'kurtosis': stats.kurtosis(series.dropna())
            }
            
            # Trend analysis
            trend_analysis = self._analyze_trend(series)
            
            # Volatility analysis
            volatility_analysis = self._analyze_volatility(series)
            
            # Momentum analysis
            momentum_analysis = self._analyze_momentum(series)
            
            # Cycle characteristics
            cycle_analysis = self._analyze_cycle_characteristics(series)
            
            # Leading indicator score
            leading_score = self._calculate_leading_indicator_score(series, indicator)
            
            analysis[indicator] = {
                'statistics': stats_analysis,
                'trend': trend_analysis,
                'volatility': volatility_analysis,
                'momentum': momentum_analysis,
                'cycle': cycle_analysis,
                'leading_score': leading_score,
                'current_level': series.iloc[-1] if not series.empty else None,
                'normalized_score': self._normalize_indicator_score(series, indicator)
            }
        
        return analysis
    
    def _analyze_trend(self, series: pd.Series) -> dict:
        """
        Trend tahlili
        """
        
        if len(series) < 3:
            return {'trend': 'insufficient_data'}
        
        # Linear trend test
        x = np.arange(len(series))
        y = series.values
        
        # Remove NaN values
        valid_mask = ~np.isnan(y)
        if np.sum(valid_mask) < 3:
            return {'trend': 'insufficient_valid_data'}
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x[valid_mask], y[valid_mask])
        
        # Trend classification
        if p_value < 0.05:
            if slope > 0:
                trend = 'strong_upward' if abs(slope) > std_err * 2 else 'weak_upward'
            else:
                trend = 'strong_downward' if abs(slope) > std_err * 2 else 'weak_downward'
        else:
            trend = 'no_significant_trend'
        
        return {
            'trend': trend,
            'slope': slope,
            'r_squared': r_value**2,
            'p_value': p_value,
            'trend_strength': abs(r_value)
        }
    
    def _analyze_volatility(self, series: pd.Series) -> dict:
        """
        Volatility tahlili
        """
        
        if len(series) < 2:
            return {'volatility': 'insufficient_data'}
        
        # Rolling volatility
        rolling_vol = series.rolling(window=min(12, len(series)//2), min_periods=3).std()
        
        # Current vs historical volatility
        current_vol = series.tail(12).std() if len(series) >= 12 else series.std()
        historical_vol = series.std()
        
        volatility_ratio = current_vol / (historical_vol + 0.01)
        
        return {
            'current_volatility': current_vol,
            'historical_volatility': historical_vol,
            'volatility_ratio': volatility_ratio,
            'volatility_regime': 'high' if volatility_ratio > 1.5 else 'low' if volatility_ratio < 0.7 else 'normal',
            'volatility_trend': 'increasing' if rolling_vol.tail(3).mean() > rolling_vol.head(3).mean() else 'decreasing'
        }
    
    def _analyze_momentum(self, series: pd.Series) -> dict:
        """
        Momentum tahlili
        """
        
        if len(series) < 5:
            return {'momentum': 'insufficient_data'}
        
        # Various momentum indicators
        momentum_1m = series.iloc[-1] - series.iloc[-2] if len(series) >= 2 else 0
        momentum_3m = series.iloc[-1] - series.iloc[-4] if len(series) >= 4 else 0
        momentum_6m = series.iloc[-1] - series.iloc[-7] if len(series) >= 7 else 0
        
        # Relative momentum
        if len(series) >= 13:
            roc_12m = (series.iloc[-1] - series.iloc[-13]) / series.iloc[-13] * 100
        else:
            roc_12m = None
        
        return {
            'momentum_1m': momentum_1m,
            'momentum_3m': momentum_3m,
            'momentum_6m': momentum_6m,
            'rate_of_change_12m': roc_12m,
            'momentum_direction': 'positive' if momentum_3m > 0 else 'negative',
            'momentum_strength': abs(momentum_3m) / (series.std() + 0.01)
        }
    
    def _analyze_cycle_characteristics(self, series: pd.Series) -> dict:
        """
        Cycle characteristics tahlili
        """
        
        if len(series) < 24:
            return {'cycle': 'insufficient_data'}
        
        # Simple cycle detection using peaks and troughs
        from scipy.signal import find_peaks
        
        # Find peaks and troughs
        peaks, _ = find_peaks(series.values, distance=6)
        troughs, _ = find_peaks(-series.values, distance=6)
        
        # Cycle characteristics
        cycle_length = len(series) / (len(peaks) + len(troughs) + 1) if (len(peaks) + len(troughs)) > 0 else len(series)
        
        return {
            'peak_count': len(peaks),
            'trough_count': len(troughs),
            'estimated_cycle_length': cycle_length,
            'cycle_strength': (len(peaks) + len(troughs)) / (len(series) / 12),
            'current_cycle_phase': self._determine_current_phase(series, peaks, troughs)
        }
    
    def _determine_current_phase(self, series: pd.Series, peaks: np.ndarray, troughs: np.ndarray) -> str:
        """
        Hozirgi cycle fazani aniqlash
        """
        
        if len(peaks) == 0 and len(troughs) == 0:
            return 'no_clear_phase'
        
        current_value = series.iloc[-1]
        
        # Simple phase determination
        if len(peaks) > 0 and peaks[-1] > len(series) - 6:
            return 'peak'
        elif len(troughs) > 0 and troughs[-1] > len(series) - 6:
            return 'trough'
        else:
            return 'expansion_or_contraction'
    
    def _calculate_leading_indicator_score(self, series: pd.Series, indicator_name: str) -> dict:
        """
        Leading indicator score hisoblash
        """
        
        # Find indicator type
        indicator_type = None
        for type_name, indicators in self.indicator_types.items():
            if indicator_name in indicators:
                indicator_type = type_name
                break
        
        if indicator_type is None:
            return {'type': 'unknown', 'score': 0.0, 'confidence': 0.0}
        
        # Calculate score based on type and recent performance
        if indicator_type == 'leading':
            # Leading indicators get higher scores
            score = 0.8 + self._calculate_recent_performance_score(series)
        elif indicator_type == 'coincident':
            # Coincident indicators get moderate scores
            score = 0.6 + self._calculate_recent_performance_score(series)
        else:  # lagging
            # Lagging indicators get lower scores
            score = 0.4 + self._calculate_recent_performance_score(series)
        
        confidence = self._calculate_indicator_confidence(series, indicator_type)
        
        return {
            'type': indicator_type,
            'score': min(score, 1.0),
            'confidence': confidence,
            'weight': self.indicator_types[indicator_type].get(indicator_name, {}).get('weight', 1.0)
        }
    
    def _calculate_recent_performance_score(self, series: pd.Series) -> float:
        """
        Oxirgi davrdagi performance score
        """
        
        if len(series) < 6:
            return 0.0
        
        recent_performance = series.tail(6).std() / series.std() if series.std() > 0 else 0
        return min(recent_performance, 1.0)
    
    def _calculate_indicator_confidence(self, series: pd.Series, indicator_type: str) -> float:
        """
        Indicator confidence hisoblash
        """
        
        # Data quality and consistency factors
        data_completeness = 1.0 - (series.isnull().sum() / len(series))
        
        # Consistency over time
        if len(series) >= 12:
            rolling_stability = series.rolling(6).std().std()
            consistency_score = 1.0 / (1.0 + rolling_stability)
        else:
            consistency_score = 0.5
        
        # Type-specific confidence adjustments
        type_adjustment = {'leading': 0.9, 'coincident': 1.0, 'lagging': 0.8}
        type_score = type_adjustment.get(indicator_type, 0.5)
        
        confidence = (data_completeness * 0.4 + consistency_score * 0.3 + type_score * 0.3)
        return confidence
    
    def _normalize_indicator_score(self, series: pd.Series, indicator_name: str) -> float:
        """
        Indicator score'ini normalize qilish
        """
        
        if len(series) < 12:
            return 0.5
        
        # Z-score normalization
        z_score = (series.iloc[-1] - series.mean()) / series.std()
        
        # Convert to [0, 1] range
        normalized_score = 0.5 + 0.4 * np.tanh(z_score / 2)
        
        return max(0.0, min(1.0, normalized_score))
    
    def _construct_composite_indicators(self, data: pd.DataFrame) -> dict:
        """
        Composite indicator'lar qurish
        """
        
        composite_indicators = {}
        
        # Leading Composite Index
        leading_data = self._get_indicator_subset(data, 'leading')
        if not leading_data.empty:
            composite_indicators['leading_composite'] = self._create_weighted_composite(
                leading_data, self.indicator_types['leading']
            )
        
        # Coincident Composite Index
        coincident_data = self._get_indicator_subset(data, 'coincident')
        if not coincident_data.empty:
            composite_indicators['coincident_composite'] = self._create_weighted_composite(
                coincident_data, self.indicator_types['coincident']
            )
        
        # Economic Surprise Index
        surprise_index = self._create_economic_surprise_index(data)
        if surprise_index is not None:
            composite_indicators['economic_surprise'] = surprise_index
        
        return composite_indicators
    
    def _get_indicator_subset(self, data: pd.DataFrame, indicator_type: str) -> pd.DataFrame:
        """
        Specific indicator type subset olish
        """
        
        if indicator_type not in self.indicator_types:
            return pd.DataFrame()
        
        type_indicators = list(self.indicator_types[indicator_type].keys())
        available_indicators = [ind for ind in type_indicators if ind in data.columns]
        
        return data[available_indicators] if available_indicators else pd.DataFrame()
    
    def _create_weighted_composite(self, indicator_data: pd.DataFrame, weights: dict) -> pd.Series:
        """
        Weighted composite indicator yaratish
        """
        
        if indicator_data.empty:
            return pd.Series()
        
        # Normalize all indicators
        normalized_data = pd.DataFrame()
        
        for column in indicator_data.columns:
            series = indicator_data[column].dropna()
            if len(series) > 0:
                # Standard normalization
                normalized = (series - series.mean()) / series.std()
                normalized_data[column] = normalized
        
        if normalized_data.empty:
            return pd.Series()
        
        # Apply weights and calculate composite
        composite_scores = pd.Series(index=normalized_data.index, dtype=float)
        
        for idx in normalized_data.index:
            weighted_sum = 0
            total_weight = 0
            
            for column in normalized_data.columns:
                if not pd.isna(normalized_data.loc[idx, column]):
                    weight = weights.get(column, {}).get('weight', 1.0)
                    weighted_sum += normalized_data.loc[idx, column] * weight
                    total_weight += weight
            
            composite_scores[idx] = weighted_sum / total_weight if total_weight > 0 else 0
        
        return composite_scores.dropna()
    
    def _create_economic_surprise_index(self, data: pd.DataFrame) -> pd.Series:
        """
        Economic Surprise Index yaratish
        """
        
        # This is a simplified version - in practice would use actual vs expected data
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) < 3:
            return None
        
        surprise_scores = []
        
        for idx in data.index:
            surprises = []
            
            for col in numeric_columns[:10]:  # Limit to avoid noise
                if not pd.isna(data.loc[idx, col]):
                    # Simple surprise calculation (deviation from trend)
                    recent_mean = data[col].tail(6).mean() if len(data) >= 6 else data[col].mean()
                    current_value = data.loc[idx, col]
                    
                    if not pd.isna(recent_mean) and recent_mean != 0:
                        surprise = (current_value - recent_mean) / abs(recent_mean)
                        surprises.append(surprise)
            
            if surprises:
                composite_surprise = np.mean(surprises)
            else:
                composite_surprise = 0
            
            surprise_scores.append(composite_surprise)
        
        return pd.Series(surprise_scores, index=data.index)
    
    def _integrate_leading_indicators(self, data: pd.DataFrame) -> dict:
        """
        Leading indicator'larni integration qilish
        """
        
        leading_data = self._get_indicator_subset(data, 'leading')
        
        if leading_data.empty:
            return {'error': 'No leading indicators available'}
        
        # Lead-lag analysis
        lead_lag_analysis = self._analyze_lead_lag_relationships(leading_data)
        
        # Leading indicator strength
        strength_analysis = self._assess_leading_indicator_strength(leading_data)
        
        # Early warning signals
        warning_signals = self._detect_early_warning_signals(leading_data)
        
        # Leading composite score
        leading_composite = self._create_weighted_composite(
            leading_data, self.indicator_types['leading']
        )
        
        return {
            'lead_lag_analysis': lead_lag_analysis,
            'strength_analysis': strength_analysis,
            'early_warning_signals': warning_signals,
            'current_leading_score': leading_composite.iloc[-1] if not leading_composite.empty else None,
            'leading_trend': self._analyze_leading_trend(leading_composite),
            'signal_quality': self._assess_signal_quality(leading_data)
        }
    
    def _analyze_lead_lag_relationships(self, data: pd.DataFrame) -> dict:
        """
        Lead-lag munosabatlarini tahlil qilish
        """
        
        correlations = {}
        
        for col1 in data.columns:
            for col2 in data.columns:
                if col1 != col2:
                    # Calculate cross-correlation at different lags
                    for lag in range(-12, 13):
                        if lag == 0:
                            continue
                        
                        try:
                            if lag > 0:
                                corr = data[col1].corr(data[col2].shift(lag))
                            else:
                                corr = data[col1].shift(-lag).corr(data[col2])
                            
                            if not pd.isna(corr):
                                correlations[f'{col1}_leads_{col2}_{lag}'] = corr
                        except:
                            continue
        
        return {'cross_correlations': correlations}
    
    def _assess_leading_indicator_strength(self, data: pd.DataFrame) -> dict:
        """
        Leading indicator strength assessment
        """
        
        strength_scores = {}
        
        for col in data.columns:
            # Calculate signal-to-noise ratio
            signal_power = data[col].std()**2
            noise_power = data[col].rolling(3).std().mean()**2
            snr = signal_power / (noise_power + 0.01)
            
            # Calculate consistency score
            consistency = 1.0 - data[col].rolling(6).std().std() / (data[col].std() + 0.01)
            
            strength_scores[col] = {
                'signal_to_noise_ratio': snr,
                'consistency_score': max(0, consistency),
                'overall_strength': min(snr, 2.0) * 0.5 + max(0, consistency) * 0.5
            }
        
        return strength_scores
    
    def _detect_early_warning_signals(self, data: pd.DataFrame) -> dict:
        """
        Early warning signals detection
        """
        
        warnings = []
        
        for col in data.columns:
            series = data[col].dropna()
            
            if len(series) < 12:
                continue
            
            # Detect rapid changes
            recent_change = series.iloc[-1] - series.iloc[-6]
            historical_std = series.std()
            
            if abs(recent_change) > 2 * historical_std:
                warnings.append({
                    'indicator': col,
                    'signal_type': 'rapid_change',
                    'magnitude': recent_change / historical_std,
                    'direction': 'upward' if recent_change > 0 else 'downward'
                })
            
            # Detect trend reversals
            if len(series) >= 24:
                long_term_trend = (series.iloc[-12:].mean() - series.iloc[-24:-12].mean()) / series.std()
                recent_trend = (series.iloc[-6:].mean() - series.iloc[-12:-6].mean()) / series.std()
                
                if long_term_trend * recent_trend < -0.5:  # Opposite directions
                    warnings.append({
                        'indicator': col,
                        'signal_type': 'trend_reversal',
                        'long_term_trend': long_term_trend,
                        'recent_trend': recent_trend
                    })
        
        return {'active_warnings': warnings}
    
    def _analyze_leading_trend(self, leading_composite: pd.Series) -> dict:
        """
        Leading indicator trend tahlili
        """
        
        if leading_composite.empty or len(leading_composite) < 6:
            return {'trend': 'insufficient_data'}
        
        # Recent trend analysis
        recent_trend = leading_composite.tail(6).mean() - leading_composite.head(6).mean()
        
        # Momentum analysis
        if len(leading_composite) >= 12:
            momentum = leading_composite.iloc[-1] - leading_composite.iloc[-12]
        else:
            momentum = leading_composite.iloc[-1] - leading_composite.iloc[0]
        
        return {
            'recent_trend': recent_trend,
            'momentum': momentum,
            'trend_direction': 'improving' if recent_trend > 0 else 'deteriorating',
            'momentum_strength': abs(momentum) / leading_composite.std()
        }
    
    def _assess_signal_quality(self, data: pd.DataFrame) -> dict:
        """
        Signal quality assessment
        """
        
        # Calculate correlation stability
        correlation_stability = self._calculate_correlation_stability(data)
        
        # Calculate noise level
        noise_level = self._estimate_noise_level(data)
        
        # Overall quality score
        quality_score = (correlation_stability * 0.6 + (1 - noise_level) * 0.4)
        
        return {
            'correlation_stability': correlation_stability,
            'noise_level': noise_level,
            'overall_quality': quality_score,
            'quality_rating': 'high' if quality_score > 0.7 else 'medium' if quality_score > 0.4 else 'low'
        }
    
    def _calculate_correlation_stability(self, data: pd.DataFrame) -> float:
        """
        Correlation stability hisoblash
        """
        
        if len(data.columns) < 2 or len(data) < 24:
            return 0.5
        
        stability_scores = []
        
        for i in range(0, len(data) - 12, 6):
            window1 = data.iloc[i:i+12]
            window2 = data.iloc[i+6:i+18] if i + 18 <= len(data) else data.iloc[i+6:]
            
            if len(window1) >= 6 and len(window2) >= 6:
                corr1 = window1.corr().values[np.triu_indices_from(corr1, k=1)]
                corr2 = window2.corr().values[np.triu_indices_from(corr2, k=1)]
                
                if len(corr1) > 0 and len(corr2) > 0:
                    stability = 1.0 - np.mean(np.abs(corr1 - corr2))
                    stability_scores.append(stability)
        
        return np.mean(stability_scores) if stability_scores else 0.5
    
    def _estimate_noise_level(self, data: pd.DataFrame) -> float:
        """
        Noise level estimation
        """
        
        noise_levels = []
        
        for col in data.columns:
            series = data[col].dropna()
            
            if len(series) < 12:
                continue
            
            # Signal-to-noise ratio
            signal_power = series.std()**2
            noise_power = series.rolling(3).std().mean()**2
            noise_level = noise_power / (signal_power + 0.01)
            
            noise_levels.append(noise_level)
        
        return np.mean(noise_levels) if noise_levels else 0.5
    
    def _analyze_synchronization(self, 
                               data: pd.DataFrame, 
                               indicators: list) -> dict:
        """
        Indicator synchronization tahlili
        """
        
        if len(indicators) < 2:
            return {'synchronization': 'insufficient_indicators'}
        
        # Correlation matrix
        correlation_matrix = data[indicators].corr()
        
        # Synchronization clustering
        sync_clusters = self._identify_synchronization_clusters(correlation_matrix)
        
        # Cross-correlation analysis
        cross_correlations = self._analyze_cross_correlations(data, indicators)
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'synchronization_clusters': sync_clusters,
            'cross_correlations': cross_correlations,
            'synchronization_strength': self._calculate_overall_synchronization(correlation_matrix)
        }
    
    def _identify_synchronization_clusters(self, correlation_matrix: pd.DataFrame) -> dict:
        """
        Synchronization clusters identification
        """
        
        if len(correlation_matrix) < 3:
            return {'clusters': 'insufficient_data'}
        
        # Simple clustering based on correlation thresholds
        high_corr_threshold = 0.7
        low_corr_threshold = 0.3
        
        clusters = []
        processed = set()
        
        for i, indicator1 in enumerate(correlation_matrix.columns):
            if indicator1 in processed:
                continue
            
            cluster = [indicator1]
            processed.add(indicator1)
            
            for j, indicator2 in enumerate(correlation_matrix.columns):
                if (indicator2 not in processed and 
                    abs(correlation_matrix.loc[indicator1, indicator2]) > high_corr_threshold):
                    cluster.append(indicator2)
                    processed.add(indicator2)
            
            if len(cluster) > 1:
                clusters.append(cluster)
        
        return {'clusters': clusters}
    
    def _analyze_cross_correlations(self, data: pd.DataFrame, indicators: list) -> dict:
        """
        Cross-correlation analysis
        """
        
        cross_corr_results = {}
        
        for i, ind1 in enumerate(indicators):
            for j, ind2 in enumerate(indicators):
                if i >= j:  # Avoid duplicates and self-correlation
                    continue
                
                # Calculate cross-correlation at optimal lag
                max_corr = 0
                optimal_lag = 0
                
                for lag in range(-12, 13):
                    try:
                        if lag > 0:
                            corr = data[ind1].corr(data[ind2].shift(lag))
                        else:
                            corr = data[ind1].shift(-lag).corr(data[ind2])
                        
                        if not pd.isna(corr) and abs(corr) > abs(max_corr):
                            max_corr = corr
                            optimal_lag = lag
                    except:
                        continue
                
                cross_corr_results[f'{ind1}_{ind2}'] = {
                    'max_correlation': max_corr,
                    'optimal_lag': optimal_lag,
                    'relationship': 'positive' if max_corr > 0 else 'negative'
                }
        
        return cross_corr_results
    
    def _calculate_overall_synchronization(self, correlation_matrix: pd.DataFrame) -> float:
        """
        Overall synchronization hisoblash
        """
        
        # Extract upper triangle correlations (excluding diagonal)
        correlations = correlation_matrix.values[np.triu_indices_from(correlation_matrix, k=1)]
        
        # Calculate average absolute correlation
        avg_correlation = np.mean(np.abs(correlations))
        
        return avg_correlation
    
    def _calculate_composite_dashboard_score(self, 
                                           individual_analysis: dict,
                                           composite_analysis: dict,
                                           leading_analysis: dict) -> dict:
        """
        Composite dashboard score hisoblash
        """
        
        # Weighted component scores
        component_scores = {}
        
        # Leading indicators score
        if 'current_leading_score' in leading_analysis and leading_analysis['current_leading_score'] is not None:
            component_scores['leading_score'] = self._normalize_score(
                leading_analysis['current_leading_score'], -3, 3
            )
        
        # Coincident indicators score
        if 'coincident_composite' in composite_analysis:
            coincident_score = composite_analysis['coincident_composite'].iloc[-1] if not composite_analysis['coincident_composite'].empty else 0
            component_scores['coincident_score'] = self._normalize_score(
                coincident_score, -3, 3
            )
        
        # Economic momentum score
        momentum_score = self._calculate_economic_momentum(individual_analysis)
        if momentum_score is not None:
            component_scores['momentum_score'] = momentum_score
        
        # Data quality adjustment
        quality_adjustment = self._assess_overall_data_quality(individual_analysis)
        
        # Weighted composite score
        weights = {'leading_score': 0.3, 'coincident_score': 0.4, 'momentum_score': 0.3}
        
        composite_score = 0
        total_weight = 0
        
        for component, weight in weights.items():
            if component in component_scores:
                composite_score += component_scores[component] * weight
                total_weight += weight
        
        if total_weight > 0:
            composite_score /= total_weight
        
        composite_score *= quality_adjustment
        
        return {
            'composite_score': composite_score,
            'component_scores': component_scores,
            'quality_adjustment': quality_adjustment,
            'score_interpretation': self._interpret_composite_score(composite_score),
            'confidence_level': self._calculate_score_confidence(component_scores, quality_adjustment)
        }
    
    def _normalize_score(self, score: float, min_val: float, max_val: float) -> float:
        """
        Score'ini [0, 1] range ga normalize qilish
        """
        
        if max_val == min_val:
            return 0.5
        
        normalized = (score - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    def _calculate_economic_momentum(self, individual_analysis: dict) -> float:
        """
        Economic momentum calculation
        """
        
        momentum_scores = []
        
        for indicator, analysis in individual_analysis.items():
            if 'momentum' in analysis and 'momentum_strength' in analysis['momentum']:
                momentum_scores.append(analysis['momentum']['momentum_strength'])
        
        return np.mean(momentum_scores) if momentum_scores else None
    
    def _assess_overall_data_quality(self, individual_analysis: dict) -> float:
        """
        Overall data quality assessment
        """
        
        quality_scores = []
        
        for indicator, analysis in individual_analysis.items():
            if 'leading_score' in analysis and 'confidence' in analysis['leading_score']:
                quality_scores.append(analysis['leading_score']['confidence'])
        
        return np.mean(quality_scores) if quality_scores else 0.5
    
    def _interpret_composite_score(self, score: float) -> dict:
        """
        Composite score interpretation
        """
        
        if score >= 0.8:
            interpretation = 'very_strong'
            description = 'Economic conditions are very strong'
        elif score >= 0.6:
            interpretation = 'strong'
            description = 'Economic conditions are strong'
        elif score >= 0.4:
            interpretation = 'moderate'
            description = 'Economic conditions are moderate'
        elif score >= 0.2:
            interpretation = 'weak'
            description = 'Economic conditions are weak'
        else:
            interpretation = 'very_weak'
            description = 'Economic conditions are very weak'
        
        return {
            'interpretation': interpretation,
            'description': description,
            'score_range': f'{score:.2f}'
        }
    
    def _calculate_score_confidence(self, component_scores: dict, quality_adjustment: float) -> str:
        """
        Score confidence level calculation
        """
        
        # Number of available components
        num_components = len(component_scores)
        
        # Confidence based on component availability and quality
        if num_components >= 3 and quality_adjustment > 0.7:
            confidence = 'high'
        elif num_components >= 2 and quality_adjustment > 0.5:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return confidence
    
    def _assess_data_quality(self, data: pd.DataFrame) -> dict:
        """
        Data quality assessment
        """
        
        total_cells = data.shape[0] * data.shape[1]
        missing_cells = data.isnull().sum().sum()
        missing_percentage = missing_cells / total_cells * 100
        
        # Data completeness
        completeness = 100 - missing_percentage
        
        # Data consistency (based on coefficient of variation)
        consistency_scores = []
        for col in data.select_dtypes(include=[np.number]).columns:
            series = data[col].dropna()
            if len(series) > 1:
                cv = series.std() / abs(series.mean()) if series.mean() != 0 else float('inf')
                consistency_scores.append(1.0 / (1.0 + cv))  # Lower CV = higher consistency
        
        avg_consistency = np.mean(consistency_scores) if consistency_scores else 0.5
        
        overall_quality = (completeness * 0.6 + avg_consistency * 100 * 0.4) / 100
        
        return {
            'completeness_percentage': completeness,
            'consistency_score': avg_consistency,
            'overall_quality_score': overall_quality,
            'quality_rating': 'high' if overall_quality > 0.8 else 'medium' if overall_quality > 0.6 else 'low',
            'recommendations': self._generate_quality_recommendations(missing_percentage, avg_consistency)
        }
    
    def _generate_quality_recommendations(self, missing_pct: float, consistency: float) -> list:
        """
        Data quality recommendations generation
        """
        
        recommendations = []
        
        if missing_pct > 10:
            recommendations.append('High percentage of missing data - consider data imputation')
        
        if consistency < 0.5:
            recommendations.append('Low data consistency - verify data sources and collection methods')
        
        if missing_pct > 20:
            recommendations.append('Very high missing data percentage - consider alternative data sources')
        
        return recommendations
    
    def _generate_summary_report(self, 
                               individual_analysis: dict,
                               composite_analysis: dict,
                               leading_analysis: dict,
                               composite_score: dict) -> dict:
        """
        Summary report generation
        """
        
        # Key findings
        key_findings = []
        
        # Leading indicators summary
        if 'current_leading_score' in leading_analysis and leading_analysis['current_leading_score'] is not None:
            leading_trend = leading_analysis.get('leading_trend', {})
            trend_direction = leading_trend.get('trend_direction', 'unknown')
            key_findings.append(f"Leading indicators showing {trend_direction} trend")
        
        # Composite score summary
        if 'score_interpretation' in composite_score:
            interpretation = composite_score['score_interpretation']['interpretation']
            key_findings.append(f"Overall economic conditions are {interpretation}")
        
        # Risk factors
        risk_factors = []
        if 'early_warning_signals' in leading_analysis:
            active_warnings = leading_analysis['early_warning_signals'].get('active_warnings', [])
            if active_warnings:
                risk_factors.append(f"{len(active_warnings)} active early warning signals detected")
        
        # Recommendations
        recommendations = []
        if composite_score.get('confidence_level') == 'low':
            recommendations.append('Consider gathering more data to improve confidence in analysis')
        
        return {
            'key_findings': key_findings,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'overall_assessment': composite_score.get('score_interpretation', {}).get('description', 'Analysis incomplete')
        }