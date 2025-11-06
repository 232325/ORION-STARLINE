"""
Liquidity Analysis Module
========================

Liquidity tahlil moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class LiquidityAnalyzer:
    """Liquidity tahlil moduli"""
    
    def __init__(self):
        self.liquidity_thresholds = {
            'excellent': 10000000,  # $10M+
            'good': 5000000,        # $5M+
            'fair': 1000000,        # $1M+
            'poor': 500000,         # $500K+
            'very_poor': 100000     # $100K+
        }
        
        self.volume_thresholds = {
            'high': 2.0,   # 200% of average
            'normal': 1.0, # 100% of average
            'low': 0.5,    # 50% of average
            'very_low': 0.2 # 20% of average
        }
    
    def analyze_liquidity_depth(self, data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """Liquidity chuqurligini tahlil qilish"""
        df = data.copy()
        
        # Basic liquidity metrics
        df['volume_ma'] = df['volume'].rolling(window=window).mean()
        df['volume_std'] = df['volume'].rolling(window=window).std()
        df['volume_zscore'] = (df['volume'] - df['volume_ma']) / df['volume_std']
        
        # Volume-based liquidity score
        df['liquidity_score'] = self._calculate_liquidity_score(df)
        
        # Spread estimation (using high-low as proxy)
        if all(col in df.columns for col in ['high', 'low', 'close']):
            df['hl_spread'] = (df['high'] - df['low']) / df['close']
            df['spread_score'] = 1 / (1 + df['hl_spread'] * 10000)  # Normalize to 0-1
            
            # Combined liquidity score
            df['combined_liquidity'] = (df['liquidity_score'] * 0.7 + 
                                      df['spread_score'] * 0.3)
        else:
            df['combined_liquidity'] = df['liquidity_score']
        
        # Liquidity classification
        df['liquidity_regime'] = self._classify_liquidity(df['combined_liquidity'])
        
        return df
    
    def _calculate_liquidity_score(self, df: pd.DataFrame) -> pd.Series:
        """Liquidity score hisoblash"""
        # Volume ratio compared to moving average
        volume_ratio = df['volume'] / df['volume_ma']
        
        # Volume stability (inverse of coefficient of variation)
        volume_cv = df['volume_std'] / df['volume_ma']
        stability_score = 1 / (1 + volume_cv)
        
        # Volume consistency score
        consistency_score = np.where(volume_ratio > 1.2, 1.0,
                           np.where(volume_ratio > 0.8, 0.8,
                           np.where(volume_ratio > 0.5, 0.6, 0.3)))
        
        # Combined score
        liquidity_score = (consistency_score * 0.6 + 
                          stability_score * 0.4)
        
        return pd.Series(liquidity_score, index=df.index)
    
    def _classify_liquidity(self, liquidity_scores: pd.Series) -> pd.Series:
        """Liquidity rejimini klassifikatsiya qilish"""
        return pd.cut(liquidity_scores, 
                     bins=[0, 0.3, 0.5, 0.7, 0.85, 1.0],
                     labels=['very_poor', 'poor', 'fair', 'good', 'excellent'],
                     include_lowest=True)
    
    def calculate_liquidity_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Liquidity metriklari hisoblash"""
        if data.empty:
            return {}
        
        # Basic statistics
        metrics = {
            'avg_volume': data['volume'].mean(),
            'median_volume': data['volume'].median(),
            'volume_std': data['volume'].std(),
            'volume_cv': data['volume'].std() / data['volume'].mean() if data['volume'].mean() > 0 else 0,
            'avg_range': ((data['high'] - data['low']) / data['close']).mean() if all(col in data.columns for col in ['high', 'low', 'close']) else 0
        }
        
        # Liquidity efficiency (volume/price range ratio)
        if all(col in data.columns for col in ['volume', 'high', 'low', 'close']):
            price_range = (data['high'] - data['low']) / data['close']
            metrics['liquidity_efficiency'] = (data['volume'] / price_range).mean()
            metrics['efficiency_std'] = (data['volume'] / price_range).std()
        
        # Volume distribution analysis
        metrics['high_volume_percentile'] = data['volume'].quantile(0.9)
        metrics['low_volume_percentile'] = data['volume'].quantile(0.1)
        metrics['volume_skewness'] = stats.skew(data['volume'])
        metrics['volume_kurtosis'] = stats.kurtosis(data['volume'])
        
        # Liquidity regime distribution
        if 'liquidity_regime' in data.columns:
            regime_counts = data['liquidity_regime'].value_counts()
            metrics['regime_distribution'] = regime_counts.to_dict()
            metrics['dominant_regime'] = regime_counts.index[0] if not regime_counts.empty else 'unknown'
        
        return metrics
    
    def detect_liquidity_events(self, data: pd.DataFrame, threshold: float = 2.0) -> pd.DataFrame:
        """Liquidity voqealarini aniqlash"""
        df = data.copy()
        
        if 'volume_zscore' not in df.columns:
            df['volume_zscore'] = self.analyze_liquidity_depth(df)['volume_zscore']
        
        # Volume spikes (high liquidity events)
        df['volume_spike'] = df['volume_zscore'] > threshold
        
        # Volume droughts (low liquidity events)
        df['volume_drought'] = df['volume_zscore'] < -threshold
        
        # Liquidity consolidation (low volatility + low volume)
        if 'combined_liquidity' in df.columns:
            df['liquidity_consolidation'] = (
                (df['combined_liquidity'] < 0.4) & 
                (df['volume_zscore'] < -1)
            )
        
        # Rapid liquidity shifts
        df['liquidity_shift'] = df['combined_liquidity'].diff().abs() > 0.3
        
        # Event scoring
        df['liquidity_event_score'] = 0
        df.loc[df['volume_spike'], 'liquidity_event_score'] += 3
        df.loc[df['volume_drought'], 'liquidity_event_score'] += 2
        df.loc[df['liquidity_consolidation'], 'liquidity_event_score'] += 1
        df.loc[df['liquidity_shift'], 'liquidity_event_score'] += 1
        
        return df
    
    def analyze_liquidity_patterns(self, data: pd.DataFrame) -> Dict[str, any]:
        """Liquidity patternlarini tahlil qilish"""
        if data.empty:
            return {}
        
        patterns = {}
        
        # Daily liquidity patterns
        if isinstance(data.index, pd.DatetimeIndex):
            daily_patterns = self._analyze_daily_liquidity_patterns(data)
            patterns['daily_patterns'] = daily_patterns
            
            # Session-based patterns
            session_patterns = self._analyze_session_liquidity_patterns(data)
            patterns['session_patterns'] = session_patterns
        
        # Volume clustering
        volume_clusters = self._analyze_volume_clustering(data)
        patterns['volume_clusters'] = volume_clusters
        
        # Liquidity persistence
        liquidity_persistence = self._analyze_liquidity_persistence(data)
        patterns['liquidity_persistence'] = liquidity_persistence
        
        return patterns
    
    def _analyze_daily_liquidity_patterns(self, data: pd.DataFrame) -> Dict[str, any]:
        """Kunlik liquidity patternlarini tahlil qilish"""
        if 'liquidity_score' not in data.columns:
            data = self.analyze_liquidity_depth(data)
        
        # Hourly patterns
        hourly_liquidity = data.groupby(data.index.hour)['liquidity_score'].agg([
            'mean', 'std', 'count'
        ]).round(4)
        
        # Day of week patterns  
        daily_liquidity = data.groupby(data.index.dayofweek)['liquidity_score'].agg([
            'mean', 'std', 'count'
        ]).round(4)
        
        return {
            'hourly_statistics': hourly_liquidity.to_dict('index'),
            'daily_statistics': daily_liquidity.to_dict('index'),
            'peak_hours': hourly_liquidity['mean'].nlargest(3).index.tolist(),
            'low_hours': hourly_liquidity['mean'].nsmallest(3).index.tolist(),
            'most_liquid_day': daily_liquidity['mean'].idxmax(),
            'least_liquid_day': daily_liquidity['mean'].idxmin()
        }
    
    def _analyze_session_liquidity_patterns(self, data: pd.DataFrame) -> Dict[str, any]:
        """Session liquidity patternlarini tahlil qilish"""
        # Define sessions
        def get_session(hour):
            if 0 <= hour < 8:
                return 'Asian'
            elif 8 <= hour < 13:
                return 'Europe_Asia_Overlap'
            elif 13 <= hour < 17:
                return 'America_Europe_Overlap'
            elif 17 <= hour < 24:
                return 'American'
            else:
                return 'Unknown'
        
        data['session'] = data.index.hour.apply(get_session)
        
        session_stats = data.groupby('session').agg({
            'volume': ['mean', 'std', 'count'],
            'liquidity_score': ['mean', 'std'],
            'combined_liquidity': ['mean', 'std']
        }).round(4)
        
        return {
            'session_statistics': session_stats.to_dict('index'),
            'liquidity_ranking': session_stats[('liquidity_score', 'mean')].sort_values(ascending=False).to_dict(),
            'volume_ranking': session_stats[('volume', 'mean')].sort_values(ascending=False).to_dict()
        }
    
    def _analyze_volume_clustering(self, data: pd.DataFrame) -> Dict[str, any]:
        """Volume clustering tahlili"""
        if len(data) < 50:  # Need sufficient data
            return {'status': 'insufficient_data'}
        
        # Prepare data for clustering
        volume_data = data['volume'].values.reshape(-1, 1)
        
        # Standardize volumes
        scaler = StandardScaler()
        volume_scaled = scaler.fit_transform(volume_data)
        
        # K-means clustering
        n_clusters = min(4, len(data) // 20)  # Adaptive number of clusters
        
        if n_clusters < 2:
            return {'status': 'insufficient_data_for_clustering'}
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(volume_scaled)
        
        # Analyze clusters
        cluster_stats = {}
        for i in range(n_clusters):
            cluster_mask = clusters == i
            cluster_volumes = data['volume'][cluster_mask]
            
            cluster_stats[f'cluster_{i}'] = {
                'size': int(cluster_mask.sum()),
                'percentage': float(cluster_mask.sum() / len(data) * 100),
                'mean_volume': float(cluster_volumes.mean()),
                'median_volume': float(cluster_volumes.median()),
                'volume_range': [float(cluster_volumes.min()), float(cluster_volumes.max())]
            }
        
        return {
            'n_clusters': n_clusters,
            'cluster_statistics': cluster_stats,
            'cluster_labels': clusters.tolist(),
            'silhouette_score': 0.0  # Would need sklearn.metrics.silhouette_score
        }
    
    def _analyze_liquidity_persistence(self, data: pd.DataFrame) -> Dict[str, any]:
        """Liquidity persistence tahlili"""
        if 'liquidity_regime' not in data.columns:
            data = self.analyze_liquidity_depth(data)
            data = self.detect_liquidity_events(data)
        
        # Calculate regime persistence
        regime_changes = data['liquidity_regime'].ne(data['liquidity_regime'].shift()).cumsum()
        regime_durations = regime_changes.groupby(regime_changes).size()
        
        # Statistics on how long liquidity regimes persist
        persistence_stats = {
            'avg_regime_duration': float(regime_durations.mean()),
            'median_regime_duration': float(regime_durations.median()),
            'regime_duration_std': float(regime_durations.std()),
            'min_regime_duration': int(regime_durations.min()),
            'max_regime_duration': int(regime_durations.max()),
            'total_regime_changes': int(data['liquidity_regime'].ne(data['liquidity_regime'].shift()).sum())
        }
        
        # Liquidity volatility (how quickly liquidity changes)
        if 'combined_liquidity' in data.columns:
            liquidity_volatility = data['combined_liquidity'].std()
            persistence_stats['liquidity_volatility'] = float(liquidity_volatility)
            
            # Liquidity correlation with time
            if isinstance(data.index, pd.DatetimeIndex):
                time_numeric = pd.to_numeric(data.index)
                liquidity_corr = data['combined_liquidity'].corr(time_numeric)
                persistence_stats['time_correlation'] = float(liquidity_corr)
        
        return persistence_stats
    
    def forecast_liquidity(self, data: pd.DataFrame, horizon: int = 5) -> Dict[str, any]:
        """Liquidity bashoratlash (simple moving average based)"""
        if len(data) < 20:
            return {'status': 'insufficient_data'}
        
        df = self.analyze_liquidity_depth(data)
        
        # Simple forecasts using recent trends
        liquidity_forecast = df['combined_liquidity'].tail(20).mean()
        volume_forecast = df['volume'].tail(20).mean()
        
        # Forecast confidence intervals (using historical volatility)
        liquidity_std = df['combined_liquidity'].tail(20).std()
        volume_std = df['volume'].tail(20).std()
        
        forecasts = {
            'liquidity_forecast': liquidity_forecast,
            'volume_forecast': volume_forecast,
            'liquidity_confidence_interval': [
                liquidity_forecast - 1.96 * liquidity_std,
                liquidity_forecast + 1.96 * liquidity_std
            ],
            'volume_confidence_interval': [
                volume_forecast - 1.96 * volume_std,
                volume_forecast + 1.96 * volume_std
            ],
            'forecast_horizon': horizon,
            'forecast_method': 'moving_average',
            'data_quality': 'good' if len(df) > 100 else 'fair'
        }
        
        return forecasts
    
    def get_liquidity_recommendations(self, data: pd.DataFrame, 
                                    trade_size: float) -> Dict[str, any]:
        """Liquidity asosida tavsiyalar"""
        if data.empty:
            return {'status': 'no_data'}
        
        # Analyze current liquidity conditions
        df = self.analyze_liquidity_depth(data)
        latest_liquidity = df['combined_liquidity'].iloc[-1]
        avg_volume = df['volume'].mean()
        
        recommendations = {
            'current_liquidity_score': latest_liquidity,
            'liquidity_regime': df['liquidity_regime'].iloc[-1] if 'liquidity_regime' in df.columns else 'unknown',
            'recommendations': []
        }
        
        # Size recommendations
        if latest_liquidity > 0.8:
            recommendations['max_recommended_size'] = trade_size * 2  # Can handle larger trades
            recommendations['optimal_execution'] = 'aggressive'
            recommendations['recommendations'].append('Yuqori likvidlik: Katta trade lar bajarish mumkin')
        elif latest_liquidity > 0.6:
            recommendations['max_recommended_size'] = trade_size * 1.2
            recommendations['optimal_execution'] = 'moderate'
            recommendations['recommendations'].append('O\'rtacha likvidlik: Ehtiyotkor trade size')
        elif latest_liquidity > 0.4:
            recommendations['max_recommended_size'] = trade_size * 0.8
            recommendations['optimal_execution'] = 'conservative'
            recommendations['recommendations'].append('Past likvidlik: Kichik trade size va ehtiyot')
        else:
            recommendations['max_recommended_size'] = trade_size * 0.5
            recommendations['optimal_execution'] = 'avoid'
            recommendations['recommendations'].append('Juda past likvidlik: Trade lar Avoid qiling')
        
        # Volume comparison
        current_volume = df['volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio > 1.5:
            recommendations['volume_status'] = 'high'
            recommendations['recommendations'].append('Yuqori volume: Yaxshi execution shartlari')
        elif volume_ratio > 0.8:
            recommendations['volume_status'] = 'normal'
            recommendations['recommendations'].append('Normal volume: Standart execution')
        else:
            recommendations['volume_status'] = 'low'
            recommendations['recommendations'].append('Past volume: Execution qiyinchiliklari bo\'lishi mumkin')
        
        # Time-based recommendations
        if isinstance(data.index, pd.DatetimeIndex):
            current_hour = data.index[-1].hour
            if 8 <= current_hour <= 17:  # European/American overlap
                recommendations['time_recommendation'] = 'optimal'
                recommendations['recommendations'].append('Optimal vaqt: Yuqori likvidlik davri')
            elif 0 <= current_hour <= 8:  # Asian session
                recommendations['time_recommendation'] = 'caution'
                recommendations['recommendations'].append('Ehtiyot: Past likvidlik davri')
            else:
                recommendations['time_recommendation'] = 'poor'
                recommendations['recommendations'].append('Yomon vaqt: Minimal likvidlik')
        
        return recommendations