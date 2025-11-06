"""
Cross-Asset Correlation Learning Module
Dynamic correlation modeling and regime-specific correlation analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
import warnings

warnings.filterwarnings('ignore')

class DynamicCorrelationModel:
    """
    Dynamic correlation modeling for multiple assets
    """
    
    def __init__(self, window_size: int = 60, min_periods: int = 30):
        """
        Args:
            window_size: Rolling correlation window
            min_periods: Minimum periods for calculation
        """
        self.window_size = window_size
        self.min_periods = min_periods
        self.correlation_history = []
        
    def rolling_correlation_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """
        Rolling correlation matrix calculation
        
        Args:
            returns: Asset returns DataFrame
            
        Returns:
            DataFrame: Rolling correlation matrices
        """
        rolling_corr = returns.rolling(
            window=self.window_size, 
            min_periods=self.min_periods
        ).corr()
        
        return rolling_corr
        
    def correlation_stability_analysis(self, correlation_matrix: pd.DataFrame) -> Dict:
        """
        Correlation stability tahlili
        
        Args:
            correlation_matrix: Correlation matrix time series
            
        Returns:
            Dict: Stability metrics
        """
        if len(correlation_matrix) < 10:
            return {'error': 'Insufficient data for stability analysis'}
            
        # Calculate correlation persistence
        asset_pairs = []
        stability_metrics = {}
        
        # Get all asset pairs
        assets = correlation_matrix.columns.get_level_values(0).unique()
        
        for i, asset1 in enumerate(assets):
            for j, asset2 in enumerate(assets[i+1:], i+1):
                asset_pairs.append((asset1, asset2))
                
                # Extract correlation time series for this pair
                pair_corr = []
                for date in correlation_matrix.index:
                    try:
                        if date in correlation_matrix.index:
                            corr_value = correlation_matrix.loc[date, (asset1, asset2)]
                            if not pd.isna(corr_value):
                                pair_corr.append(corr_value)
                    except (KeyError, pd.errors.Accessor):
                        continue
                        
                if len(pair_corr) > 10:
                    pair_corr_series = np.array(pair_corr)
                    
                    # Stability metrics
                    stability_metrics[f"{asset1}_{asset2}"] = {
                        'mean_correlation': np.mean(pair_corr_series),
                        'std_correlation': np.std(pair_corr_series),
                        'min_correlation': np.min(pair_corr_series),
                        'max_correlation': np.max(pair_corr_series),
                        'correlation_range': np.max(pair_corr_series) - np.min(pair_corr_series),
                        'persistence': self._calculate_correlation_persistence(pair_corr_series),
                        'volatility_regime_correlation': self._regime_aware_correlation(pair_corr_series)
                    }
                    
        return stability_metrics
        
    def _calculate_correlation_persistence(self, corr_series: np.ndarray) -> float:
        """Correlation persistence hisoblash"""
        if len(corr_series) < 2:
            return 0.0
            
        # Count of periods where correlation direction doesn't change
        direction_changes = 0
        for i in range(1, len(corr_series)):
            if (corr_series[i] > 0) != (corr_series[i-1] > 0):
                direction_changes += 1
                
        return 1 - (direction_changes / (len(corr_series) - 1))
        
    def _regime_aware_correlation(self, corr_series: np.ndarray) -> Dict:
        """Correlation regime tahlili"""
        if len(corr_series) < 20:
            return {'low_regime_avg': np.mean(corr_series), 'high_regime_avg': np.mean(corr_series)}
            
        # Identify correlation regimes (high/low correlation periods)
        median_corr = np.median(corr_series)
        
        low_regime = corr_series[corr_series <= median_corr]
        high_regime = corr_series[corr_series > median_corr]
        
        return {
            'low_regime_avg': np.mean(low_regime) if len(low_regime) > 0 else np.mean(corr_series),
            'high_regime_avg': np.mean(high_regime) if len(high_regime) > 0 else np.mean(corr_series),
            'regime_switch_frequency': self._count_regime_switches(corr_series, median_corr)
        }
        
    def _count_regime_switches(self, corr_series: np.ndarray, threshold: float) -> int:
        """Regime switch count"""
        if len(corr_series) < 2:
            return 0
            
        switches = 0
        current_regime = corr_series[0] > threshold
        
        for value in corr_series[1:]:
            new_regime = value > threshold
            if new_regime != current_regime:
                switches += 1
                current_regime = new_regime
                
        return switches


class CorrelationRegimeDetector:
    """
    Correlation regime identification
    """
    
    def __init__(self, n_regimes: int = 3):
        """
        Args:
            n_regimes: Number of correlation regimes
        """
        self.n_regimes = n_regimes
        self.correlation_clusters = None
        
    def detect_correlation_regimes(self, returns: pd.DataFrame, window: int = 60) -> pd.DataFrame:
        """
        Correlation regime detection
        
        Args:
            returns: Asset returns
            window: Rolling window for correlation calculation
            
        Returns:
            DataFrame: Correlation regime classifications
        """
        if len(returns) < window:
            return pd.DataFrame(index=returns.index)
            
        # Calculate rolling correlations
        correlation_matrices = self._calculate_rolling_correlations(returns, window)
        
        # Flatten correlation matrices for clustering
        correlation_features = self._flatten_correlation_matrices(correlation_matrices)
        
        # Detect correlation regimes using clustering
        regimes = self._cluster_correlation_features(correlation_features)
        
        # Map back to time series
        regime_series = pd.Series(regimes, index=correlation_matrices.index)
        
        return regime_series
        
    def _calculate_rolling_correlations(self, returns: pd.DataFrame, window: int) -> Dict:
        """Rolling correlation matrices hisoblash"""
        correlations = {}
        
        for i in range(window, len(returns)):
            date = returns.index[i]
            window_data = returns.iloc[i-window:i]
            
            if len(window_data) >= self.n_regimes:
                corr_matrix = window_data.corr()
                correlations[date] = corr_matrix
                
        return correlations
        
    def _flatten_correlation_matrices(self, correlations: Dict) -> np.ndarray:
        """Correlation matricalarni feature vectorlarga aylantirish"""
        features = []
        dates = list(correlations.keys())
        
        if not dates:
            return np.array([])
            
        # Get correlation values (upper triangle to avoid redundancy)
        n_assets = len(list(correlations.values())[0])
        
        for date in dates:
            corr_matrix = correlations[date]
            
            # Extract upper triangle (excluding diagonal)
            upper_triangle = []
            for i in range(n_assets):
                for j in range(i+1, n_assets):
                    upper_triangle.append(corr_matrix.iloc[i, j])
                    
            features.append(upper_triangle)
            
        return np.array(features)
        
    def _cluster_correlation_features(self, features: np.ndarray) -> List[int]:
        """Correlation features clustering"""
        if len(features) == 0:
            return []
            
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=self.n_regimes, random_state=42, n_init=10)
        regimes = kmeans.fit_predict(features_scaled)
        
        self.correlation_clusters = {
            'model': kmeans,
            'scaler': scaler,
            'feature_importance': self._calculate_feature_importance(kmeans, features_scaled)
        }
        
        return regimes.tolist()
        
    def _calculate_feature_importance(self, kmeans, features: np.ndarray) -> Dict:
        """Feature importance calculation"""
        cluster_centers = kmeans.cluster_centers_
        
        # Calculate variance across clusters for each feature
        feature_variance = np.var(cluster_centers, axis=0)
        feature_importance = feature_variance / np.sum(feature_variance)
        
        return {
            'importance_scores': feature_importance.tolist(),
            'top_features': np.argsort(feature_importance)[::-1].tolist()
        }
        
    def predict_correlation_regime(self, returns: pd.DataFrame) -> int:
        """
        Future correlation regime bashorat qilish
        
        Args:
            returns: Recent returns data
            
        Returns:
            int: Predicted regime (0 to n_regimes-1)
        """
        if self.correlation_clusters is None:
            raise ValueError("Model must be fitted first using detect_correlation_regimes")
            
        if len(returns) < 10:
            return 0  # Default regime
            
        # Calculate correlation matrix
        corr_matrix = returns.corr()
        
        # Flatten correlation features
        upper_triangle = []
        n_assets = len(corr_matrix)
        
        for i in range(n_assets):
            for j in range(i+1, n_assets):
                upper_triangle.append(corr_matrix.iloc[i, j])
                
        features = np.array(upper_triangle).reshape(1, -1)
        
        # Scale features
        features_scaled = self.correlation_clusters['scaler'].transform(features)
        
        # Predict regime
        predicted_regime = self.correlation_clusters['model'].predict(features_scaled)[0]
        
        return predicted_regime


class CrossAssetFactorModel:
    """
    Cross-asset factor model
    """
    
    def __init__(self, n_factors: int = 5, method: str = 'pca'):
        """
        Args:
            n_factors: Number of factors
            method: Factor extraction method ('pca' or 'factor_analysis')
        """
        self.n_factors = n_factors
        self.method = method
        self.factor_model = None
        self.loadings = None
        self.scaler = StandardScaler()
        
    def fit_factor_model(self, returns: pd.DataFrame) -> Dict:
        """
        Factor model fit qilish
        
        Args:
            returns: Asset returns
            
        Returns:
            Dict: Factor model results
        """
        if len(returns) < self.n_factors:
            raise ValueError("Insufficient data for factor model")
            
        # Standardize returns
        returns_scaled = self.scaler.fit_transform(returns)
        
        # Extract factors
        if self.method == 'pca':
            self.factor_model = PCA(n_components=self.n_factors)
            factors = self.factor_model.fit_transform(returns_scaled)
            self.loadings = self.factor_model.components_.T
            
        elif self.method == 'factor_analysis':
            self.factor_model = FactorAnalysis(n_components=self.n_factors, random_state=42)
            factors = self.factor_model.fit_transform(returns_scaled)
            self.loadings = self.factor_model.components_.T
            
        else:
            raise ValueError("Method must be 'pca' or 'factor_analysis'")
            
        # Calculate factor returns
        factor_returns = pd.DataFrame(
            factors,
            index=returns.index,
            columns=[f'Factor_{i+1}' for i in range(self.n_factors)]
        )
        
        # Calculate residual returns
        reconstructed = factors @ self.loadings.T
        residuals = returns_scaled - reconstructed
        
        # Model statistics
        explained_variance_ratio = self.factor_model.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance_ratio)
        
        model_results = {
            'factor_returns': factor_returns,
            'loadings': pd.DataFrame(
                self.loadings,
                index=returns.columns,
                columns=[f'Factor_{i+1}' for i in range(self.n_factors)]
            ),
            'residuals': pd.DataFrame(
                residuals,
                index=returns.index,
                columns=returns.columns
            ),
            'explained_variance_ratio': explained_variance_ratio,
            'cumulative_variance': cumulative_variance,
            'total_variance_explained': cumulative_variance[-1]
        }
        
        return model_results
        
    def calculate_factor_exposures(self, returns: pd.DataFrame, regime_classification: pd.Series) -> pd.DataFrame:
        """
        Factor exposures by regime
        
        Args:
            returns: Asset returns
            regime_classification: Regime classification
            
        Returns:
            DataFrame: Factor exposures by regime
        """
        if self.factor_model is None:
            raise ValueError("Factor model must be fitted first")
            
        # Align data
        common_index = returns.index.intersection(regime_classification.index)
        returns_aligned = returns[common_index]
        regimes_aligned = regime_classification[common_index]
        
        if len(common_index) == 0:
            return pd.DataFrame()
            
        # Calculate exposures for each regime
        exposures_by_regime = {}
        
        for regime in regimes_aligned.unique():
            if pd.isna(regime):
                continue
                
            regime_mask = regimes_aligned == regime
            regime_returns = returns_aligned[regime_mask]
            
            if len(regime_returns) > self.n_factors:
                regime_returns_scaled = self.scaler.transform(regime_returns)
                
                # Calculate factor exposures (loadings)
                exposures = regime_returns_scaled.T @ self.factor_model.transform(regime_returns_scaled)
                exposures /= len(regime_returns)  # Normalize
                
                exposures_by_regime[regime] = exposures.mean(axis=1)
                
        return pd.DataFrame(exposures_by_regime).T
        
    def forecast_factor_returns(self, recent_returns: pd.DataFrame, horizon: int = 5) -> Dict:
        """
        Factor return forecasting
        
        Args:
            recent_returns: Recent return data
            horizon: Forecasting horizon
            
        Returns:
            Dict: Forecast results
        """
        if self.factor_model is None:
            raise ValueError("Factor model must be fitted first")
            
        if len(recent_returns) < 20:
            # Simple mean forecast
            recent_factors = self.scaler.transform(recent_returns)
            factor_returns = self.factor_model.transform(recent_factors)
            mean_factors = factor_returns.mean(axis=0)
            
            forecasts = {}
            for i, factor_name in enumerate([f'Factor_{j+1}' for j in range(self.n_factors)]):
                forecasts[factor_name] = {
                    'forecast': mean_factors[i],
                    'confidence': 0.1,  # Low confidence for short data
                    'method': 'mean_reversion'
                }
                
            return forecasts
            
        # AR(1) model for factor returns
        recent_factors = self.scaler.transform(recent_returns)
        factor_returns = self.factor_model.transform(recent_factors)
        
        forecasts = {}
        
        for i, factor_name in enumerate([f'Factor_{j+1}' for j in range(self.n_factors)]):
            factor_series = factor_returns[:, i]
            
            # Fit AR(1)
            if len(factor_series) > 2:
                y = factor_series[1:]
                x = factor_series[:-1]
                
                # Simple linear regression
                beta = np.corrcoef(x, y)[0, 1] * np.std(y) / np.std(x)
                alpha = np.mean(y) - beta * np.mean(x)
                
                # Forecast
                last_value = factor_series[-1]
                forecast_value = alpha + beta * last_value
                
                # Confidence interval
                residuals = y - (alpha + beta * x)
                forecast_std = np.std(residuals)
                
                forecasts[factor_name] = {
                    'forecast': forecast_value,
                    'confidence': forecast_std,
                    'method': 'ar1_regression',
                    'alpha': alpha,
                    'beta': beta
                }
            else:
                forecasts[factor_name] = {
                    'forecast': np.mean(factor_series),
                    'confidence': np.std(factor_series),
                    'method': 'mean'
                }
                
        return forecasts


class CorrelationClustering:
    """
    Cross-asset correlation clustering
    """
    
    def __init__(self):
        self.cluster_model = None
        self.cluster_labels = None
        
    def cluster_assets_by_correlation(self, returns: pd.DataFrame, method: str = 'hierarchical') -> Dict:
        """
        Assetlarni correlation bo'yicha clusterlash
        
        Args:
            returns: Asset returns
            method: Clustering method ('hierarchical' or 'kmeans')
            
        Returns:
            Dict: Clustering results
        """
        # Calculate correlation matrix
        corr_matrix = returns.corr()
        
        # Convert correlation to distance
        distance_matrix = np.sqrt(2 * (1 - corr_matrix))
        
        if method == 'hierarchical':
            # Hierarchical clustering
            condensed_dist = squareform(distance_matrix.values, checks=False)
            linkage_matrix = linkage(condensed_dist, method='ward')
            
            # Get cluster labels
            cluster_labels = fcluster(linkage_matrix, t=5, criterion='maxclust') - 1
            
        elif method == 'kmeans':
            # K-means clustering on correlation features
            features = []
            for i in range(len(corr_matrix)):
                features.append(corr_matrix.iloc[i].values)
                
            features = np.array(features)
            
            kmeans = KMeans(n_clusters=5, random_state=42)
            cluster_labels = kmeans.fit_predict(features)
            
            self.cluster_model = kmeans
            
        else:
            raise ValueError("Method must be 'hierarchical' or 'kmeans'")
            
        self.cluster_labels = cluster_labels
        
        # Organize results
        asset_clusters = {}
        for i, label in enumerate(cluster_labels):
            cluster_name = f"Cluster_{label}"
            if cluster_name not in asset_clusters:
                asset_clusters[cluster_name] = []
            asset_clusters[cluster_name].append(returns.columns[i])
            
        # Calculate cluster characteristics
        cluster_characteristics = {}
        for cluster_name, assets in asset_clusters.items():
            if len(assets) > 1:
                cluster_returns = returns[assets]
                cluster_characteristics[cluster_name] = {
                    'assets': assets,
                    'avg_correlation': cluster_returns.corr().values[np.triu_indices_from(cluster_returns.corr().values, k=1)].mean(),
                    'volatility': cluster_returns.std().mean(),
                    'size': len(assets)
                }
            else:
                cluster_characteristics[cluster_name] = {
                    'assets': assets,
                    'avg_correlation': 0.0,
                    'volatility': returns[assets[0]].std(),
                    'size': 1
                }
                
        return {
            'asset_clusters': asset_clusters,
            'cluster_characteristics': cluster_characteristics,
            'distance_matrix': distance_matrix,
            'method': method
        }
        
    def get_regime_specific_clusters(self, returns: pd.DataFrame, regime_classification: pd.Series) -> Dict:
        """
        Rejim-specific correlation clustering
        
        Args:
            returns: Asset returns
            regime_classification: Market regime classification
            
        Returns:
            Dict: Regime-specific clustering results
        """
        common_index = returns.index.intersection(regime_classification.index)
        
        if len(common_index) == 0:
            return {}
            
        returns_aligned = returns[common_index]
        regimes_aligned = regime_classification[common_index]
        
        regime_clusters = {}
        
        for regime in regimes_aligned.unique():
            if pd.isna(regime):
                continue
                
            regime_mask = regimes_aligned == regime
            regime_returns = returns_aligned[regime_mask]
            
            if len(regime_returns) > 50:  # Sufficient data for clustering
                regime_clustering = self.cluster_assets_by_correlation(regime_returns)
                regime_clusters[regime] = regime_clustering
                
        return regime_clusters


if __name__ == "__main__":
    # Test cross-asset correlation learning
    np.random.seed(42)
    
    # Generate sample multi-asset data
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    assets = ['Asset_A', 'Asset_B', 'Asset_C', 'Asset_D', 'Asset_E']
    
    # Create correlated returns
    base_returns = np.random.normal(0, 0.02, (500, 5))
    
    # Add some correlation structure
    for i in range(1, 5):
        base_returns[:, i] = 0.7 * base_returns[:, 0] + 0.3 * base_returns[:, i]
        
    returns_df = pd.DataFrame(base_returns, index=dates, columns=assets)
    
    # Test dynamic correlation model
    dyn_corr = DynamicCorrelationModel(window_size=60)
    rolling_corr = dyn_corr.rolling_correlation_matrix(returns_df)
    
    # Test correlation regime detection
    corr_regime_detector = CorrelationRegimeDetector(n_regimes=3)
    correlation_regimes = corr_regime_detector.detect_correlation_regimes(returns_df, window=60)
    
    # Test factor model
    factor_model = CrossAssetFactorModel(n_factors=3, method='pca')
    factor_results = factor_model.fit_factor_model(returns_df)
    
    # Test clustering
    clusterer = CorrelationClustering()
    clustering_results = clusterer.cluster_assets_by_correlation(returns_df)
    
    print(f"Dynamic correlation analysis completed for {len(assets)} assets")
    print(f"Correlation regimes detected: {len(correlation_regimes.dropna())}")
    print(f"Factor model explains {factor_results['total_variance_explained']:.2%} of variance")
    print(f"Asset clusters identified: {len(clustering_results['asset_clusters'])}")