"""
Comprehensive Self-Learning System Module

Ushbu modul multi-scale learning, hierarchical learning systems, 
meta-learning across cycles va continuous adaptation framework uchun mo'ljallangan.

Imkoniyatlar:
- Multi-scale learning (intraday to multi-year)
- Hierarchical learning systems
- Meta-learning across cycles
- Continuous adaptation framework
- Knowledge accumulation system
- Learning effectiveness measurement
"""

import numpy as np
import pandas as pd
from scipy import stats, optimize
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveLearningSystem:
    """
    Comprehensive Self-Learning System Class
    """
    
    def __init__(self, 
                 learning_rates: dict = None,
                 memory_decay: float = 0.95,
                 meta_learning_rate: float = 0.1):
        """
        Comprehensive Learning System initialize qilish
        
        Args:
            learning_rates: Turli scale'lar uchun learning rates
            memory_decay: Memory decay rate
            meta_learning_rate: Meta-learning rate
        """
        
        self.learning_rates = learning_rates or {
            'intraday': 0.1,
            'daily': 0.05,
            'weekly': 0.02,
            'monthly': 0.01,
            'quarterly': 0.005,
            'yearly': 0.001
        }
        
        self.memory_decay = memory_decay
        self.meta_learning_rate = meta_learning_rate
        
        # Multi-scale learning models
        self.scale_models = {}
        self.meta_learner = None
        self.knowledge_base = {}
        
        # Learning history and performance tracking
        self.learning_history = []
        self.performance_by_scale = {}
        self.adaptation_effectiveness = {}
        
        # Hierarchical knowledge structure
        self.hierarchical_knowledge = {
            'micro_patterns': {},      # Intraday patterns
            'market_regimes': {},      # Short-term regimes
            'economic_cycles': {},     # Medium-term cycles
            'structural_shifts': {},   # Long-term shifts
            'cross_cycle_patterns': {} # Meta-patterns
        }
        
        # Learning configuration
        self.learning_config = {
            'multi_scale_enabled': True,
            'meta_learning_enabled': True,
            'continual_learning': True,
            'knowledge_transfer': True
        }
        
    def learn_from_economic_data(self, 
                               economic_data: pd.DataFrame,
                               performance_data: pd.DataFrame,
                               market_data: pd.DataFrame = None) -> dict:
        """
        Economic data dan learning qilish
        
        Args:
            economic_data: Iqtisodiy ma'lumotlar
            performance_data: Performance ma'lumotlar
            market_data: Market ma'lumotlar (optional)
            
        Returns:
            dict: Learning results
        """
        
        try:
            # Multi-scale data preparation
            multi_scale_data = self._prepare_multi_scale_data(
                economic_data, performance_data, market_data
            )
            
            # Hierarchical learning across scales
            hierarchical_results = self._perform_hierarchical_learning(multi_scale_data)
            
            # Meta-learning across cycles
            meta_learning_results = self._perform_meta_learning(
                hierarchical_results, economic_data
            )
            
            # Knowledge accumulation
            knowledge_updates = self._accumulate_knowledge(
                hierarchical_results, meta_learning_results
            )
            
            # Learning effectiveness assessment
            effectiveness_assessment = self._assess_learning_effectiveness(
                hierarchical_results, meta_learning_results
            )
            
            # Continuous adaptation updates
            adaptation_updates = self._update_adaptation_framework(
                knowledge_updates, effectiveness_assessment
            )
            
            results = {
                'hierarchical_learning': hierarchical_results,
                'meta_learning': meta_learning_results,
                'knowledge_updates': knowledge_updates,
                'effectiveness_assessment': effectiveness_assessment,
                'adaptation_updates': adaptation_updates,
                'learning_summary': self._generate_learning_summary(
                    hierarchical_results, meta_learning_results
                ),
                'next_learning_priorities': self._identify_learning_priorities(
                    effectiveness_assessment, adaptation_updates
                )
            }
            
            # Track learning session
            self._track_learning_session(results)
            
            return results
            
        except Exception as e:
            return {'error': f'Comprehensive learning failed: {str(e)}'}
    
    def _prepare_multi_scale_data(self, 
                                 economic_data: pd.DataFrame,
                                 performance_data: pd.DataFrame,
                                 market_data: pd.DataFrame = None) -> dict:
        """
        Multi-scale data preparation
        """
        
        scale_data = {}
        
        # Intraday data (if available)
        if market_data is not None and 'hour' in market_data.columns:
            scale_data['intraday'] = self._create_intraday_features(
                market_data, economic_data
            )
        
        # Daily data
        scale_data['daily'] = self._create_daily_features(
            economic_data, performance_data
        )
        
        # Weekly data
        scale_data['weekly'] = self._aggregate_to_weekly(
            economic_data, performance_data
        )
        
        # Monthly data
        scale_data['monthly'] = self._aggregate_to_monthly(
            economic_data, performance_data
        )
        
        # Quarterly data
        scale_data['quarterly'] = self._aggregate_to_quarterly(
            economic_data, performance_data
        )
        
        # Yearly data
        scale_data['yearly'] = self._aggregate_to_yearly(
            economic_data, performance_data
        )
        
        return scale_data
    
    def _create_intraday_features(self, 
                                market_data: pd.DataFrame,
                                economic_data: pd.DataFrame) -> pd.DataFrame:
        """
        Intraday features creation
        """
        
        intraday_features = pd.DataFrame()
        
        # Price-based features
        if 'price' in market_data.columns:
            price_series = market_data['price']
            
            # Intraday volatility
            intraday_features['intraday_volatility'] = price_series.groupby(market_data['date']).std()
            
            # Price momentum
            intraday_features['price_momentum_1h'] = price_series.pct_change(4)  # 4 hours
            intraday_features['price_momentum_4h'] = price_series.pct_change(16)  # 4 hours * 4
            
            # Volume-based features
            if 'volume' in market_data.columns:
                volume_series = market_data['volume']
                intraday_features['volume_trend'] = volume_series.rolling(8).mean()
                intraday_features['volume_volatility'] = volume_series.rolling(8).std()
        
        # Intraday economic indicators
        if not economic_data.empty:
            # Align with economic data (simplified)
            daily_economic = economic_data.resample('D').last().dropna()
            
            for col in daily_economic.select_dtypes(include=[np.number]).columns:
                intraday_features[f'ec_{col}_daily'] = daily_economic[col]
        
        return intraday_features.dropna()
    
    def _create_daily_features(self, 
                             economic_data: pd.DataFrame,
                             performance_data: pd.DataFrame) -> pd.DataFrame:
        """
        Daily features creation
        """
        
        daily_features = pd.DataFrame()
        
        # Economic indicators
        for col in economic_data.select_dtypes(include=[np.number]).columns:
            series = economic_data[col].dropna()
            
            # Momentum features
            daily_features[f'{col}_momentum_5d'] = series.pct_change(5)
            daily_features[f'{col}_momentum_20d'] = series.pct_change(20)
            
            # Volatility features
            daily_features[f'{col}_volatility_10d'] = series.rolling(10).std()
            daily_features[f'{col}_volatility_30d'] = series.rolling(30).std()
            
            # Trend features
            daily_features[f'{col}_trend_ma5'] = series.rolling(5).mean()
            daily_features[f'{col}_trend_ma20'] = series.rolling(20).mean()
        
        # Performance features
        if not performance_data.empty:
            for col in performance_data.select_dtypes(include=[np.number]).columns:
                series = performance_data[col].dropna()
                daily_features[f'perf_{col}_return'] = series.pct_change()
                daily_features[f'perf_{col}_rolling_return_10d'] = series.rolling(10).sum()
        
        return daily_features.dropna()
    
    def _aggregate_to_weekly(self, 
                           economic_data: pd.DataFrame,
                           performance_data: pd.DataFrame) -> pd.DataFrame:
        """
        Weekly aggregation
        """
        
        weekly_data = {}
        
        # Economic data aggregation
        for col in economic_data.select_dtypes(include=[np.number]).columns:
            series = economic_data[col].dropna()
            
            weekly_data[f'{col}_mean'] = series.resample('W').mean()
            weekly_data[f'{col}_std'] = series.resample('W').std()
            weekly_data[f'{col}_last'] = series.resample('W').last()
            weekly_data[f'{col}_first'] = series.resample('W').first()
            weekly_data[f'{col}_sum'] = series.resample('W').sum()
        
        # Performance data aggregation
        if not performance_data.empty:
            for col in performance_data.select_dtypes(include=[np.number]).columns:
                series = performance_data[col].dropna()
                weekly_data[f'perf_{col}_weekly_return'] = series.resample('W').sum()
                weekly_data[f'perf_{col}_weekly_volatility'] = series.resample('W').std()
        
        return pd.DataFrame(weekly_data).dropna()
    
    def _aggregate_to_monthly(self, 
                            economic_data: pd.DataFrame,
                            performance_data: pd.DataFrame) -> pd.DataFrame:
        """
        Monthly aggregation
        """
        
        monthly_data = {}
        
        # Economic data aggregation
        for col in economic_data.select_dtypes(include=[np.number]).columns:
            series = economic_data[col].dropna()
            
            monthly_data[f'{col}_mean'] = series.resample('M').mean()
            monthly_data[f'{col}_std'] = series.resample('M').std()
            monthly_data[f'{col}_last'] = series.resample('M').last()
            monthly_data[f'{col}_growth'] = series.resample('M').apply(lambda x: x.iloc[-1] / x.iloc[0] - 1 if len(x) > 1 else 0)
        
        # Performance data aggregation
        if not performance_data.empty:
            for col in performance_data.select_dtypes(include=[np.number]).columns:
                series = performance_data[col].dropna()
                monthly_data[f'perf_{col}_monthly_return'] = series.resample('M').sum()
                monthly_data[f'perf_{col}_monthly_sharpe'] = (
                    series.resample('M').sum() / series.resample('M').std()
                ).fillna(0)
        
        return pd.DataFrame(monthly_data).dropna()
    
    def _aggregate_to_quarterly(self, 
                              economic_data: pd.DataFrame,
                              performance_data: pd.DataFrame) -> pd.DataFrame:
        """
        Quarterly aggregation
        """
        
        quarterly_data = {}
        
        # Economic data aggregation
        for col in economic_data.select_dtypes(include=[np.number]).columns:
            series = economic_data[col].dropna()
            
            quarterly_data[f'{col}_mean'] = series.resample('Q').mean()
            quarterly_data[f'{col}_std'] = series.resample('Q').std()
            quarterly_data[f'{col}_growth_qoq'] = series.resample('Q').apply(lambda x: x.iloc[-1] / x.iloc[0] - 1 if len(x) > 1 else 0)
            quarterly_data[f'{col}_trend'] = series.resample('Q').apply(self._calculate_trend)
        
        # Performance data aggregation
        if not performance_data.empty:
            for col in performance_data.select_dtypes(include=[np.number]).columns:
                series = performance_data[col].dropna()
                quarterly_data[f'perf_{col}_quarterly_return'] = series.resample('Q').sum()
                quarterly_data[f'perf_{col}_quarterly_volatility'] = series.resample('Q').std()
                quarterly_data[f'perf_{col}_quarterly_max_drawdown'] = series.resample('Q').apply(self._calculate_max_drawdown)
        
        return pd.DataFrame(quarterly_data).dropna()
    
    def _aggregate_to_yearly(self, 
                           economic_data: pd.DataFrame,
                           performance_data: pd.DataFrame) -> pd.DataFrame:
        """
        Yearly aggregation
        """
        
        yearly_data = {}
        
        # Economic data aggregation
        for col in economic_data.select_dtypes(include=[np.number]).columns:
            series = economic_data[col].dropna()
            
            yearly_data[f'{col}_mean'] = series.resample('A').mean()
            yearly_data[f'{col}_std'] = series.resample('A').std()
            yearly_data[f'{col}_growth_yoy'] = series.resample('A').apply(lambda x: x.iloc[-1] / x.iloc[0] - 1 if len(x) > 1 else 0)
            yearly_data[f'{col}_correlation_with_previous'] = series.resample('A').apply(self._calculate_autocorrelation)
        
        # Performance data aggregation
        if not performance_data.empty:
            for col in performance_data.select_dtypes(include=[np.number]).columns:
                series = performance_data[col].dropna()
                yearly_data[f'perf_{col}_annual_return'] = series.resample('A').sum()
                yearly_data[f'perf_{col}_annual_volatility'] = series.resample('A').std()
                yearly_data[f'perf_{col}_annual_sharpe'] = (
                    series.resample('A').sum() / series.resample('A').std()
                ).fillna(0)
        
        return pd.DataFrame(yearly_data).dropna()
    
    def _calculate_trend(self, series: pd.Series) -> float:
        """
        Series trend calculation
        """
        
        if len(series) < 2:
            return 0
        
        x = np.arange(len(series))
        slope, _, r_value, _, _ = stats.linregress(x, series.values)
        return slope * r_value  # Weighted slope
    
    def _calculate_max_drawdown(self, series: pd.Series) -> float:
        """
        Maximum drawdown calculation
        """
        
        if len(series) < 2:
            return 0
        
        cumulative = (1 + series).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        
        return drawdown.min()
    
    def _calculate_autocorrelation(self, series: pd.Series) -> float:
        """
        Series autocorrelation calculation
        """
        
        if len(series) < 2:
            return 0
        
        return series.autocorr(lag=1)
    
    def _perform_hierarchical_learning(self, multi_scale_data: dict) -> dict:
        """
        Hierarchical learning across scales
        """
        
        hierarchical_results = {}
        
        for scale, data in multi_scale_data.items():
            if data.empty:
                continue
            
            # Scale-specific learning
            scale_results = self._learn_at_scale(scale, data)
            
            # Cross-scale pattern identification
            scale_patterns = self._identify_scale_patterns(scale, data, scale_results)
            
            hierarchical_results[scale] = {
                'model_performance': scale_results,
                'patterns': scale_patterns,
                'learning_effectiveness': self._assess_scale_learning_effectiveness(scale_results),
                'prediction_capabilities': self._assess_prediction_capabilities(scale_results, data)
            }
        
        # Cross-scale knowledge transfer
        transfer_results = self._perform_knowledge_transfer(hierarchical_results)
        hierarchical_results['cross_scale_transfer'] = transfer_results
        
        return hierarchical_results
    
    def _learn_at_scale(self, scale: str, data: pd.DataFrame) -> dict:
        """
        Learning at specific scale
        """
        
        if scale not in self.scale_models:
            self.scale_models[scale] = self._initialize_scale_model(scale)
        
        model = self.scale_models[scale]
        learning_rate = self.learning_rates.get(scale, 0.01)
        
        # Prepare features and targets
        features, targets = self._prepare_learning_data(data)
        
        if features.empty or targets.empty:
            return {'error': 'Insufficient data for learning'}
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=3)
        fold_performances = []
        
        for train_idx, test_idx in tscv.split(features):
            X_train, X_test = features.iloc[train_idx], features.iloc[test_idx]
            y_train, y_test = targets.iloc[train_idx], targets.iloc[test_idx]
            
            # Train model
            try:
                model.fit(X_train, y_train)
                
                # Predict
                y_pred = model.predict(X_test)
                
                # Evaluate
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                fold_performances.append({
                    'mse': mse,
                    'r2': r2,
                    'scale': scale,
                    'fold': len(fold_performances) + 1
                })
                
            except Exception as e:
                fold_performances.append({
                    'error': str(e),
                    'scale': scale,
                    'fold': len(fold_performances) + 1
                })
        
        # Aggregate performance
        avg_mse = np.mean([p['mse'] for p in fold_performances if 'mse' in p])
        avg_r2 = np.mean([p['r2'] for p in fold_performances if 'r2' in p])
        
        return {
            'model': model,
            'performance': {
                'average_mse': avg_mse,
                'average_r2': avg_r2,
                'fold_results': fold_performances
            },
            'learning_rate': learning_rate,
            'data_size': len(data)
        }
    
    def _initialize_scale_model(self, scale: str):
        """
        Scale-specific model initialization
        """
        
        # Different models for different scales
        if scale == 'intraday':
            # High-frequency, low complexity
            return MLPRegressor(hidden_layer_sizes=(50,), max_iter=100, random_state=42)
        elif scale == 'daily':
            return RandomForestRegressor(n_estimators=50, random_state=42)
        elif scale == 'weekly':
            return GradientBoostingRegressor(n_estimators=50, random_state=42)
        elif scale == 'monthly':
            return RandomForestRegressor(n_estimators=100, random_state=42)
        elif scale == 'quarterly':
            return GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif scale == 'yearly':
            return MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=200, random_state=42)
        else:
            return RandomForestRegressor(n_estimators=50, random_state=42)
    
    def _prepare_learning_data(self, data: pd.DataFrame) -> tuple:
        """
        Learning data preparation
        """
        
        # Separate features and targets
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return pd.DataFrame(), pd.Series()
        
        # Use all numeric columns as features
        features = data[numeric_cols[:-1]].fillna(method='ffill').fillna(0)
        
        # Use last column as target
        targets = data[numeric_cols[-1]].fillna(method='ffill').fillna(0)
        
        # Ensure equal lengths
        min_length = min(len(features), len(targets))
        features = features.iloc[:min_length]
        targets = targets.iloc[:min_length]
        
        return features, targets
    
    def _identify_scale_patterns(self, scale: str, data: pd.DataFrame, scale_results: dict) -> dict:
        """
        Scale-specific pattern identification
        """
        
        patterns = {}
        
        # Statistical patterns
        for col in data.select_dtypes(include=[np.number]).columns:
            series = data[col].dropna()
            
            patterns[col] = {
                'mean': series.mean(),
                'std': series.std(),
                'skewness': stats.skew(series),
                'kurtosis': stats.kurtosis(series),
                'autocorrelation': series.autocorr(lag=1),
                'trend_strength': abs(stats.linregress(range(len(series)), series.values)[0]) if len(series) > 1 else 0
            }
        
        # Temporal patterns
        if hasattr(data.index, 'freq') or len(data) > 10:
            patterns['temporal'] = self._identify_temporal_patterns(data, scale)
        
        # Model-specific insights
        if 'model' in scale_results:
            patterns['model_insights'] = self._extract_model_insights(scale_results['model'], data)
        
        return patterns
    
    def _identify_temporal_patterns(self, data: pd.DataFrame, scale: str) -> dict:
        """
        Temporal pattern identification
        """
        
        temporal_patterns = {}
        
        # Seasonal patterns (if applicable)
        if hasattr(data.index, 'dayofweek'):
            data_with_dow = data.copy()
            data_with_dow['day_of_week'] = data.index.dayofweek
            weekly_patterns = data_with_dow.groupby('day_of_week').mean()
            temporal_patterns['weekly_seasonality'] = weekly_patterns.to_dict()
        
        if hasattr(data.index, 'month'):
            data_with_month = data.copy()
            data_with_month['month'] = data.index.month
            monthly_patterns = data_with_month.groupby('month').mean()
            temporal_patterns['monthly_seasonality'] = monthly_patterns.to_dict()
        
        # Cycle detection
        if len(data) > 20:
            cycle_length = self._detect_dominant_cycle(data)
            if cycle_length:
                temporal_patterns['dominant_cycle_length'] = cycle_length
        
        return temporal_patterns
    
    def _detect_dominant_cycle(self, data: pd.DataFrame) -> int:
        """
        Dominant cycle detection
        """
        
        # Simple cycle detection using autocorrelation
        max_corr = 0
        optimal_lag = 0
        
        for lag in range(2, min(len(data)//2, 50)):
            try:
                corr = data.corrwith(data.shift(lag), axis=0).mean()
                if abs(corr) > abs(max_corr):
                    max_corr = corr
                    optimal_lag = lag
            except:
                continue
        
        return optimal_lag if abs(max_corr) > 0.3 else None
    
    def _extract_model_insights(self, model, data: pd.DataFrame) -> dict:
        """
        Model insights extraction
        """
        
        insights = {}
        
        # Feature importance (for tree-based models)
        if hasattr(model, 'feature_importances_'):
            feature_names = data.select_dtypes(include=[np.number]).columns[:-1]
            importance_dict = dict(zip(feature_names, model.feature_importances_))
            insights['feature_importance'] = importance_dict
        
        # Model complexity
        if hasattr(model, 'n_estimators'):
            insights['complexity'] = f"ensemble_with_{model.n_estimators}_estimators"
        elif hasattr(model, 'hidden_layer_sizes'):
            insights['complexity'] = f"neural_network_with_{model.hidden_layer_sizes}"
        else:
            insights['complexity'] = "simple_model"
        
        return insights
    
    def _assess_scale_learning_effectiveness(self, scale_results: dict) -> dict:
        """
        Scale learning effectiveness assessment
        """
        
        if 'performance' not in scale_results:
            return {'effectiveness': 'unknown', 'score': 0}
        
        performance = scale_results['performance']
        r2 = performance.get('average_r2', 0)
        
        # Effectiveness scoring
        if r2 > 0.8:
            effectiveness = 'excellent'
            score = 4
        elif r2 > 0.6:
            effectiveness = 'good'
            score = 3
        elif r2 > 0.4:
            effectiveness = 'fair'
            score = 2
        elif r2 > 0.2:
            effectiveness = 'poor'
            score = 1
        else:
            effectiveness = 'very_poor'
            score = 0
        
        return {
            'effectiveness': effectiveness,
            'score': score,
            'r2_score': r2,
            'confidence_level': 'high' if score >= 3 else 'medium' if score >= 2 else 'low'
        }
    
    def _assess_prediction_capabilities(self, scale_results: dict, data: pd.DataFrame) -> dict:
        """
        Prediction capabilities assessment
        """
        
        if 'model' not in scale_results:
            return {'capability': 'unknown'}
        
        model = scale_results['model']
        data_size = len(data)
        
        # Prediction horizon capability
        if data_size > 100:
            capability = 'long_term'
        elif data_size > 30:
            capability = 'medium_term'
        elif data_size > 10:
            capability = 'short_term'
        else:
            capability = 'very_short_term'
        
        # Stability assessment
        if 'performance' in scale_results:
            mse = scale_results['performance'].get('average_mse', float('inf'))
            data_variance = data.select_dtypes(include=[np.number]).var().mean()
            stability = 1.0 / (1.0 + mse / (data_variance + 0.01))
        else:
            stability = 0
        
        return {
            'prediction_capability': capability,
            'stability_score': stability,
            'reliability': 'high' if stability > 0.7 else 'medium' if stability > 0.4 else 'low'
        }
    
    def _perform_knowledge_transfer(self, hierarchical_results: dict) -> dict:
        """
        Cross-scale knowledge transfer
        """
        
        transfer_results = {
            'scale_relationships': {},
            'transfer_potential': {},
            'knowledge_synthesis': {}
        }
        
        scales = list(hierarchical_results.keys())
        scales = [s for s in scales if s != 'cross_scale_transfer']
        
        # Analyze relationships between scales
        for i, scale1 in enumerate(scales):
            for scale2 in scales[i+1:]:
                relationship = self._analyze_scale_relationship(
                    hierarchical_results[scale1], 
                    hierarchical_results[scale2],
                    scale1, scale2
                )
                
                transfer_results['scale_relationships'][f'{scale1}_vs_{scale2}'] = relationship
        
        # Assess transfer potential
        transfer_results['transfer_potential'] = self._assess_transfer_potential(
            hierarchical_results
        )
        
        # Synthesize knowledge
        transfer_results['knowledge_synthesis'] = self._synthesize_cross_scale_knowledge(
            hierarchical_results
        )
        
        return transfer_results
    
    def _analyze_scale_relationship(self, results1: dict, results2: dict, scale1: str, scale2: str) -> dict:
        """
        Scale relationship analysis
        """
        
        # Performance correlation
        perf1 = results1.get('model_performance', {}).get('performance', {})
        perf2 = results2.get('model_performance', {}).get('performance', {})
        
        r2_1 = perf1.get('average_r2', 0)
        r2_2 = perf2.get('average_r2', 0)
        
        # Relationship strength
        performance_diff = abs(r2_1 - r2_2)
        
        if performance_diff < 0.1:
            relationship = 'highly_correlated'
        elif performance_diff < 0.3:
            relationship = 'moderately_correlated'
        else:
            relationship = 'weakly_correlated'
        
        # Transfer potential
        if r2_1 > 0.6 and r2_2 < 0.4:
            transfer_direction = f'{scale1}_to_{scale2}'
            transfer_potential = 'high'
        elif r2_2 > 0.6 and r2_1 < 0.4:
            transfer_direction = f'{scale2}_to_{scale1}'
            transfer_potential = 'high'
        else:
            transfer_direction = 'bidirectional'
            transfer_potential = 'medium'
        
        return {
            'relationship_type': relationship,
            'performance_difference': performance_diff,
            'transfer_direction': transfer_direction,
            'transfer_potential': transfer_potential,
            'scale1_r2': r2_1,
            'scale2_r2': r2_2
        }
    
    def _assess_transfer_potential(self, hierarchical_results: dict) -> dict:
        """
        Transfer potential assessment
        """
        
        transfer_assessment = {}
        
        # Find best performing scales
        scale_performances = {}
        for scale, results in hierarchical_results.items():
            if scale == 'cross_scale_transfer':
                continue
            
            r2 = results.get('model_performance', {}).get('performance', {}).get('average_r2', 0)
            scale_performances[scale] = r2
        
        # Identify learning opportunities
        best_scale = max(scale_performances.items(), key=lambda x: x[1])
        worst_scale = min(scale_performances.items(), key=lambda x: x[1])
        
        if best_scale[1] - worst_scale[1] > 0.3:
            transfer_assessment['learning_opportunity'] = {
                'from_scale': best_scale[0],
                'to_scale': worst_scale[0],
                'potential_benefit': best_scale[1] - worst_scale[1]
            }
        
        # Cross-scale coherence
        coherence_score = self._calculate_scale_coherence(scale_performances)
        transfer_assessment['coherence_score'] = coherence_score
        
        return transfer_assessment
    
    def _calculate_scale_coherence(self, scale_performances: dict) -> float:
        """
        Scale coherence calculation
        """
        
        if len(scale_performances) < 2:
            return 0
        
        performances = list(scale_performances.values())
        return 1.0 - (np.std(performances) / (np.mean(performances) + 0.01))
    
    def _synthesize_cross_scale_knowledge(self, hierarchical_results: dict) -> dict:
        """
        Cross-scale knowledge synthesis
        """
        
        synthesis = {
            'unified_insights': [],
            'scale_interactions': {},
            'meta_patterns': []
        }
        
        # Extract unified insights
        for scale, results in hierarchical_results.items():
            if scale == 'cross_scale_transfer':
                continue
            
            if 'patterns' in results:
                patterns = results['patterns']
                
                # Identify consistent patterns across scales
                for pattern_name, pattern_data in patterns.items():
                    if isinstance(pattern_data, dict) and 'trend_strength' in pattern_data:
                        if pattern_data['trend_strength'] > 0.5:
                            synthesis['unified_insights'].append({
                                'pattern': pattern_name,
                                'scale': scale,
                                'strength': pattern_data['trend_strength'],
                                'type': 'strong_trend'
                            })
        
        # Identify meta-patterns
        synthesis['meta_patterns'] = self._identify_meta_patterns(hierarchical_results)
        
        return synthesis
    
    def _identify_meta_patterns(self, hierarchical_results: dict) -> list:
        """
        Meta-pattern identification across scales
        """
        
        meta_patterns = []
        
        # Pattern consistency across scales
        pattern_consistency = {}
        
        for scale, results in hierarchical_results.items():
            if scale == 'cross_scale_transfer' or 'patterns' not in results:
                continue
            
            for pattern_name, pattern_data in results['patterns'].items():
                if isinstance(pattern_data, dict) and 'trend_strength' in pattern_data:
                    if pattern_name not in pattern_consistency:
                        pattern_consistency[pattern_name] = []
                    
                    pattern_consistency[pattern_name].append({
                        'scale': scale,
                        'strength': pattern_data['trend_strength']
                    })
        
        # Identify meta-patterns
        for pattern_name, scale_data in pattern_consistency.items():
            if len(scale_data) >= 3:  # At least 3 scales
                avg_strength = np.mean([data['strength'] for data in scale_data])
                if avg_strength > 0.4:
                    meta_patterns.append({
                        'meta_pattern': pattern_name,
                        'scales_involved': len(scale_data),
                        'average_strength': avg_strength,
                        'persistence_across_scales': 'high' if avg_strength > 0.6 else 'medium'
                    })
        
        return meta_patterns
    
    def _perform_meta_learning(self, hierarchical_results: dict, economic_data: pd.DataFrame) -> dict:
        """
        Meta-learning across cycles
        """
        
        meta_learning_results = {
            'cycle_pattern_recognition': self._recognize_cycle_patterns(hierarchical_results),
            'meta_learner_performance': self._train_meta_learner(hierarchical_results),
            'cross_cycle_transfer': self._identify_cross_cycle_transfer(economic_data),
            'meta_knowledge_base': self._update_meta_knowledge_base(hierarchical_results)
        }
        
        return meta_learning_results
    
    def _recognize_cycle_patterns(self, hierarchical_results: dict) -> dict:
        """
        Cycle pattern recognition
        """
        
        cycle_patterns = {
            'economic_regimes': {},
            'market_conditions': {},
            'structural_breaks': {}
        }
        
        # Analyze patterns across different scales for regime identification
        for scale_name, scale_results in hierarchical_results.items():
            if scale_name == 'cross_scale_transfer':
                continue
            
            # Regime detection at each scale
            if 'patterns' in scale_results:
                patterns = scale_results['patterns']
                
                # Market condition classification
                if 'temporal' in patterns:
                    temporal = patterns['temporal']
                    if 'dominant_cycle_length' in temporal:
                        cycle_length = temporal['dominant_cycle_length']
                        
                        # Classify economic regime based on cycle length
                        if cycle_length < 12:
                            regime = 'high_frequency_regime'
                        elif cycle_length < 48:
                            regime = 'business_cycle_regime'
                        else:
                            regime = 'secular_regime'
                        
                        cycle_patterns['economic_regimes'][f'{scale_name}_{cycle_length}'] = {
                            'regime': regime,
                            'cycle_length': cycle_length,
                            'scale': scale_name
                        }
        
        return cycle_patterns
    
    def _train_meta_learner(self, hierarchical_results: dict) -> dict:
        """
        Meta-learner training
        """
        
        # Prepare meta-features from hierarchical results
        meta_features = []
        meta_targets = []
        
        for scale_name, results in hierarchical_results.items():
            if scale_name == 'cross_scale_transfer':
                continue
            
            # Extract meta-features
            if 'model_performance' in results:
                performance = results['model_performance'].get('performance', {})
                
                feature_vector = [
                    performance.get('average_r2', 0),
                    performance.get('average_mse', 1),
                    results.get('learning_effectiveness', {}).get('score', 0),
                    results.get('prediction_capabilities', {}).get('stability_score', 0)
                ]
                
                meta_features.append(feature_vector)
                
                # Target: overall learning success (combination of metrics)
                target = (
                    performance.get('average_r2', 0) * 0.4 +
                    (1.0 / (1.0 + performance.get('average_mse', 1))) * 0.3 +
                    results.get('learning_effectiveness', {}).get('score', 0) * 0.3
                )
                
                meta_targets.append(target)
        
        if len(meta_features) < 2:
            return {'status': 'insufficient_data_for_meta_learning'}
        
        # Train meta-learner
        X_meta = np.array(meta_features)
        y_meta = np.array(meta_targets)
        
        if self.meta_learner is None:
            self.meta_learner = RandomForestRegressor(n_estimators=10, random_state=42)
        
        try:
            self.meta_learner.fit(X_meta, y_meta)
            
            # Meta-learner performance
            y_pred_meta = self.meta_learner.predict(X_meta)
            meta_r2 = r2_score(y_meta, y_pred_meta)
            
            return {
                'status': 'meta_learning_completed',
                'meta_r2': meta_r2,
                'feature_importance': dict(zip(
                    ['r2_score', 'mse_score', 'effectiveness', 'stability'],
                    self.meta_learner.feature_importances_
                ))
            }
            
        except Exception as e:
            return {
                'status': 'meta_learning_failed',
                'error': str(e)
            }
    
    def _identify_cross_cycle_transfer(self, economic_data: pd.DataFrame) -> dict:
        """
        Cross-cycle transfer identification
        """
        
        if economic_data.empty:
            return {'transfer_opportunities': []}
        
        transfer_opportunities = []
        
        # Identify similar historical periods
        current_period = economic_data.tail(12).mean()  # Last 12 periods
        
        if len(economic_data) > 24:
            historical_periods = []
            
            for i in range(12, len(economic_data) - 12, 6):  # Every 6 periods
                period_data = economic_data.iloc[i-12:i]
                period_mean = period_data.mean()
                historical_periods.append({
                    'period_index': i,
                    'period_data': period_mean,
                    'period_length': 12
                })
            
            # Find similar periods
            for period in historical_periods:
                similarity = self._calculate_period_similarity(current_period, period['period_data'])
                
                if similarity > 0.7:  # High similarity threshold
                    transfer_opportunities.append({
                        'similar_period': period['period_index'],
                        'similarity_score': similarity,
                        'transfer_type': 'pattern_transfer',
                        'confidence': 'high' if similarity > 0.8 else 'medium'
                    })
        
        return {
            'transfer_opportunities': transfer_opportunities,
            'total_opportunities': len(transfer_opportunities)
        }
    
    def _calculate_period_similarity(self, period1: pd.Series, period2: pd.Series) -> float:
        """
        Period similarity calculation
        """
        
        common_indices = period1.index.intersection(period2.index)
        
        if len(common_indices) == 0:
            return 0
        
        values1 = period1[common_indices].values
        values2 = period2[common_indices].values
        
        # Normalize values
        norm1 = (values1 - np.mean(values1)) / (np.std(values1) + 0.01)
        norm2 = (values2 - np.mean(values2)) / (np.std(values2) + 0.01)
        
        # Calculate correlation
        correlation = np.corrcoef(norm1, norm2)[0, 1]
        
        return abs(correlation) if not np.isnan(correlation) else 0
    
    def _update_meta_knowledge_base(self, hierarchical_results: dict) -> dict:
        """
        Meta-knowledge base updating
        """
        
        meta_knowledge_update = {
            'successful_patterns': [],
            'failed_patterns': [],
            'performance_forecasts': {},
            'learning_recommendations': []
        }
        
        # Identify successful patterns
        for scale, results in hierarchical_results.items():
            if scale == 'cross_scale_transfer':
                continue
            
            effectiveness = results.get('learning_effectiveness', {})
            
            if effectiveness.get('score', 0) >= 3:  # Good or excellent
                meta_knowledge_update['successful_patterns'].append({
                    'scale': scale,
                    'effectiveness_score': effectiveness.get('score', 0),
                    'pattern_type': 'high_performance'
                })
            elif effectiveness.get('score', 0) <= 1:  # Poor performance
                meta_knowledge_update['failed_patterns'].append({
                    'scale': scale,
                    'effectiveness_score': effectiveness.get('score', 0),
                    'pattern_type': 'low_performance'
                })
        
        # Learning recommendations
        if 'successful_patterns' in meta_knowledge_update:
            successful_scales = [p['scale'] for p in meta_knowledge_update['successful_patterns']]
            
            if 'intraday' in successful_scales and 'daily' in successful_scales:
                meta_knowledge_update['learning_recommendations'].append({
                    'recommendation': 'leverage_intraday_daily_combination',
                    'rationale': 'Both intraday and daily patterns showing strong performance'
                })
        
        return meta_knowledge_update
    
    def _accumulate_knowledge(self, 
                            hierarchical_results: dict,
                            meta_learning_results: dict) -> dict:
        """
        Knowledge accumulation across learning sessions
        """
        
        knowledge_updates = {
            'scale_knowledge': {},
            'cycle_knowledge': {},
            'pattern_knowledge': {},
            'meta_knowledge': {}
        }
        
        # Accumulate scale-specific knowledge
        for scale_name, results in hierarchical_results.items():
            if scale_name == 'cross_scale_transfer':
                continue
            
            scale_knowledge = {
                'performance_history': results.get('model_performance', {}).get('performance', {}),
                'learning_effectiveness': results.get('learning_effectiveness', {}),
                'prediction_capabilities': results.get('prediction_capabilities', {}),
                'patterns_discovered': results.get('patterns', {}),
                'last_updated': pd.Timestamp.now()
            }
            
            knowledge_updates['scale_knowledge'][scale_name] = scale_knowledge
        
        # Accumulate cycle knowledge
        if 'cycle_pattern_recognition' in meta_learning_results:
            cycle_patterns = meta_learning_results['cycle_pattern_recognition'].get('economic_regimes', {})
            
            for regime_key, regime_data in cycle_patterns.items():
                if regime_key not in self.hierarchical_knowledge['economic_cycles']:
                    self.hierarchical_knowledge['economic_cycles'][regime_key] = []
                
                self.hierarchical_knowledge['economic_cycles'][regime_key].append({
                    'regime_data': regime_data,
                    'discovery_timestamp': pd.Timestamp.now()
                })
            
            knowledge_updates['cycle_knowledge'] = cycle_patterns
        
        # Accumulate pattern knowledge
        pattern_updates = self._accumulate_pattern_knowledge(hierarchical_results)
        knowledge_updates['pattern_knowledge'] = pattern_updates
        
        # Accumulate meta-knowledge
        if 'meta_knowledge_base' in meta_learning_results:
            meta_knowledge = meta_learning_results['meta_knowledge_base']
            knowledge_updates['meta_knowledge'] = meta_knowledge
        
        # Apply memory decay to existing knowledge
        self._apply_memory_decay()
        
        return knowledge_updates
    
    def _accumulate_pattern_knowledge(self, hierarchical_results: dict) -> dict:
        """
        Pattern knowledge accumulation
        """
        
        pattern_updates = {}
        
        for scale_name, results in hierarchical_results.items():
            if scale_name == 'cross_scale_transfer' or 'patterns' not in results:
                continue
            
            patterns = results['patterns']
            
            # Update pattern knowledge for each scale
            for pattern_name, pattern_data in patterns.items():
                if pattern_name not in self.hierarchical_knowledge.get('micro_patterns', {}):
                    self.hierarchical_knowledge['micro_patterns'][pattern_name] = {}
                
                if scale_name not in self.hierarchical_knowledge['micro_patterns'][pattern_name]:
                    self.hierarchical_knowledge['micro_patterns'][pattern_name][scale_name] = []
                
                self.hierarchical_knowledge['micro_patterns'][pattern_name][scale_name].append({
                    'pattern_data': pattern_data,
                    'timestamp': pd.Timestamp.now(),
                    'scale': scale_name
                })
            
            pattern_updates[scale_name] = patterns
        
        return pattern_updates
    
    def _apply_memory_decay(self):
        """
        Apply memory decay to existing knowledge
        """
        
        current_time = pd.Timestamp.now()
        
        for knowledge_type in self.hierarchical_knowledge.keys():
            knowledge_category = self.hierarchical_knowledge[knowledge_type]
            
            if isinstance(knowledge_category, dict):
                for key, value in knowledge_category.items():
                    if isinstance(value, list):
                        # Decay list-based knowledge
                        decayed_list = []
                        for item in value:
                            if isinstance(item, dict) and 'timestamp' in item:
                                age_days = (current_time - item['timestamp']).days
                                decay_factor = self.memory_decay ** age_days
                                
                                if decay_factor > 0.1:  # Keep if still significant
                                    item['decay_factor'] = decay_factor
                                    decayed_list.append(item)
                        
                        knowledge_category[key] = decayed_list
    
    def _assess_learning_effectiveness(self, 
                                     hierarchical_results: dict,
                                     meta_learning_results: dict) -> dict:
        """
        Learning effectiveness assessment
        """
        
        effectiveness_assessment = {
            'overall_effectiveness': 0,
            'scale_effectiveness': {},
            'meta_learning_effectiveness': 0,
            'knowledge_retention': 0,
            'learning_velocity': 0,
            'improvement_trajectory': []
        }
        
        # Assess scale effectiveness
        total_effectiveness = 0
        scale_count = 0
        
        for scale_name, results in hierarchical_results.items():
            if scale_name == 'cross_scale_transfer':
                continue
            
            scale_effectiveness = results.get('learning_effectiveness', {})
            effectiveness_score = scale_effectiveness.get('score', 0)
            
            effectiveness_assessment['scale_effectiveness'][scale_name] = {
                'score': effectiveness_score,
                'effectiveness_level': scale_effectiveness.get('effectiveness', 'unknown'),
                'confidence': scale_effectiveness.get('confidence_level', 'unknown')
            }
            
            total_effectiveness += effectiveness_score
            scale_count += 1
        
        if scale_count > 0:
            effectiveness_assessment['overall_effectiveness'] = total_effectiveness / scale_count
        
        # Meta-learning effectiveness
        if 'meta_learner_performance' in meta_learning_results:
            meta_performance = meta_learning_results['meta_learner_performance']
            if 'meta_r2' in meta_performance:
                effectiveness_assessment['meta_learning_effectiveness'] = meta_performance['meta_r2']
        
        # Knowledge retention assessment
        effectiveness_assessment['knowledge_retention'] = self._assess_knowledge_retention()
        
        # Learning velocity (improvement over time)
        effectiveness_assessment['learning_velocity'] = self._calculate_learning_velocity()
        
        # Improvement trajectory
        effectiveness_assessment['improvement_trajectory'] = self._calculate_improvement_trajectory()
        
        return effectiveness_assessment
    
    def _assess_knowledge_retention(self) -> float:
        """
        Knowledge retention assessment
        """
        
        total_knowledge_items = 0
        retained_items = 0
        
        for knowledge_type in self.hierarchical_knowledge.values():
            if isinstance(knowledge_type, dict):
                for key, value in knowledge_type.items():
                    if isinstance(value, list):
                        total_knowledge_items += len(value)
                        retained_items += len([item for item in value if item.get('decay_factor', 1) > 0.1])
        
        return retained_items / total_knowledge_items if total_knowledge_items > 0 else 0
    
    def _calculate_learning_velocity(self) -> float:
        """
        Learning velocity calculation
        """
        
        if len(self.learning_history) < 2:
            return 0
        
        recent_effectiveness = self._get_recent_learning_effectiveness()
        historical_effectiveness = self._get_historical_learning_effectiveness()
        
        time_diff = (recent_effectiveness['timestamp'] - historical_effectiveness['timestamp']).days
        effectiveness_diff = recent_effectiveness['score'] - historical_effectiveness['score']
        
        if time_diff > 0:
            velocity = effectiveness_diff / time_diff
            return max(0, velocity)  # Non-negative velocity
        
        return 0
    
    def _get_recent_learning_effectiveness(self) -> dict:
        """
        Recent learning effectiveness
        """
        
        if not self.learning_history:
            return {'timestamp': pd.Timestamp.now(), 'score': 0}
        
        return {
            'timestamp': self.learning_history[-1]['timestamp'],
            'score': self.learning_history[-1].get('overall_effectiveness', 0)
        }
    
    def _get_historical_learning_effectiveness(self) -> dict:
        """
        Historical learning effectiveness
        """
        
        if len(self.learning_history) < 2:
            return {'timestamp': pd.Timestamp.now(), 'score': 0}
        
        midpoint = len(self.learning_history) // 2
        return {
            'timestamp': self.learning_history[midpoint]['timestamp'],
            'score': self.learning_history[midpoint].get('overall_effectiveness', 0)
        }
    
    def _calculate_improvement_trajectory(self) -> list:
        """
        Improvement trajectory calculation
        """
        
        trajectory = []
        
        for i, session in enumerate(self.learning_history):
            trajectory.append({
                'session': i + 1,
                'timestamp': session['timestamp'],
                'effectiveness': session.get('overall_effectiveness', 0),
                'learning_scope': session.get('learning_scope', 'unknown')
            })
        
        return trajectory
    
    def _update_adaptation_framework(self, 
                                   knowledge_updates: dict,
                                   effectiveness_assessment: dict) -> dict:
        """
        Continuous adaptation framework updates
        """
        
        adaptation_updates = {
            'parameter_adjustments': {},
            'learning_rate_updates': {},
            'knowledge_base_updates': {},
            'framework_improvements': []
        }
        
        # Parameter adjustments based on effectiveness
        overall_effectiveness = effectiveness_assessment['overall_effectiveness']
        
        if overall_effectiveness < 2:  # Poor effectiveness
            # Increase learning rates
            for scale in self.learning_rates:
                adaptation_updates['learning_rate_updates'][scale] = {
                    'current_rate': self.learning_rates[scale],
                    'recommended_rate': min(self.learning_rates[scale] * 1.2, 0.2),
                    'adjustment_reason': 'low_effectiveness_boost'
                }
            
            adaptation_updates['framework_improvements'].append({
                'improvement': 'increase_learning_rates',
                'rationale': 'Poor effectiveness detected, need faster adaptation'
            })
        
        # Knowledge base updates
        if 'meta_knowledge' in knowledge_updates:
            successful_patterns = knowledge_updates['meta_knowledge'].get('successful_patterns', [])
            
            if successful_patterns:
                adaptation_updates['knowledge_base_updates']['emphasize_patterns'] = successful_patterns
                adaptation_updates['framework_improvements'].append({
                    'improvement': 'emphasize_successful_patterns',
                    'rationale': f'Found {len(successful_patterns)} successful patterns'
                })
        
        # Framework-specific improvements
        if effectiveness_assessment.get('learning_velocity', 0) < 0.01:
            adaptation_updates['framework_improvements'].append({
                'improvement': 'optimize_learning_velocity',
                'rationale': 'Low learning velocity detected'
            })
        
        if effectiveness_assessment.get('knowledge_retention', 0) < 0.5:
            adaptation_updates['framework_improvements'].append({
                'improvement': 'adjust_memory_decay',
                'rationale': 'Low knowledge retention'
            })
        
        return adaptation_updates
    
    def _generate_learning_summary(self, 
                                 hierarchical_results: dict,
                                 meta_learning_results: dict) -> dict:
        """
        Learning summary generation
        """
        
        summary = {
            'learning_achievements': [],
            'key_insights': [],
            'performance_highlights': [],
            'areas_for_improvement': []
        }
        
        # Learning achievements
        for scale_name, results in hierarchical_results.items():
            if scale_name == 'cross_scale_transfer':
                continue
            
            effectiveness = results.get('learning_effectiveness', {})
            if effectiveness.get('score', 0) >= 3:
                summary['learning_achievements'].append({
                    'achievement': f'Excellent learning at {scale_name} scale',
                    'score': effectiveness.get('score', 0),
                    'effectiveness': effectiveness.get('effectiveness', 'unknown')
                })
        
        # Key insights
        if 'knowledge_synthesis' in meta_learning_results.get('cross_scale_transfer', {}):
            synthesis = meta_learning_results['cross_scale_transfer']['knowledge_synthesis']
            
            for insight in synthesis.get('unified_insights', [])[:3]:  # Top 3 insights
                summary['key_insights'].append({
                    'insight': f"Strong {insight['pattern']} pattern at {insight['scale']} scale",
                    'strength': insight['strength'],
                    'type': insight['type']
                })
        
        # Performance highlights
        best_scale = max(
            [(scale, results) for scale, results in hierarchical_results.items() if scale != 'cross_scale_transfer'],
            key=lambda x: x[1].get('model_performance', {}).get('performance', {}).get('average_r2', 0),
            default=('none', {})
        )
        
        if best_scale[0] != 'none':
            r2 = best_scale[1].get('model_performance', {}).get('performance', {}).get('average_r2', 0)
            summary['performance_highlights'].append({
                'highlight': f"Best performance at {best_scale[0]} scale",
                'r2_score': r2,
                'scale': best_scale[0]
            })
        
        # Areas for improvement
        for scale_name, results in hierarchical_results.items():
            if scale_name == 'cross_scale_transfer':
                continue
            
            effectiveness = results.get('learning_effectiveness', {})
            if effectiveness.get('score', 0) <= 1:
                summary['areas_for_improvement'].append({
                    'area': f"Learning effectiveness at {scale_name} scale",
                    'current_score': effectiveness.get('score', 0),
                    'effectiveness': effectiveness.get('effectiveness', 'unknown')
                })
        
        return summary
    
    def _identify_learning_priorities(self, 
                                    effectiveness_assessment: dict,
                                    adaptation_updates: dict) -> dict:
        """
        Learning priorities identification
        """
        
        priorities = {
            'immediate_priorities': [],
            'short_term_priorities': [],
            'long_term_priorities': []
        }
        
        # Immediate priorities based on low effectiveness
        scale_effectiveness = effectiveness_assessment.get('scale_effectiveness', {})
        
        for scale_name, eff_data in scale_effectiveness.items():
            if eff_data.get('score', 0) <= 1:
                priorities['immediate_priorities'].append({
                    'priority': f'Improve {scale_name} learning',
                    'current_score': eff_data.get('score', 0),
                    'urgency': 'high',
                    'action': 'increase_learning_rate_and_data_quality'
                })
        
        # Short-term priorities
        learning_velocity = effectiveness_assessment.get('learning_velocity', 0)
        if learning_velocity < 0.01:
            priorities['short_term_priorities'].append({
                'priority': 'Accelerate learning velocity',
                'current_velocity': learning_velocity,
                'urgency': 'medium',
                'action': 'optimize_meta_learning_parameters'
            })
        
        # Long-term priorities
        knowledge_retention = effectiveness_assessment.get('knowledge_retention', 0)
        if knowledge_retention < 0.5:
            priorities['long_term_priorities'].append({
                'priority': 'Improve knowledge retention',
                'current_retention': knowledge_retention,
                'urgency': 'low',
                'action': 'review_memory_decay_and_knowledge_structure'
            })
        
        return priorities
    
    def _track_learning_session(self, results: dict):
        """
        Learning session tracking
        """
        
        session_record = {
            'timestamp': pd.Timestamp.now(),
            'learning_scope': len(results.get('hierarchical_learning', {})),
            'meta_learning_performed': bool(results.get('meta_learning', {})),
            'knowledge_updates_count': len(results.get('knowledge_updates', {})),
            'overall_effectiveness': results.get('effectiveness_assessment', {}).get('overall_effectiveness', 0)
        }
        
        self.learning_history.append(session_record)
        
        # Update performance tracking
        for scale, effectiveness_data in results.get('effectiveness_assessment', {}).get('scale_effectiveness', {}).items():
            if scale not in self.performance_by_scale:
                self.performance_by_scale[scale] = []
            
            self.performance_by_scale[scale].append({
                'timestamp': pd.Timestamp.now(),
                'score': effectiveness_data.get('score', 0),
                'effectiveness': effectiveness_data.get('effectiveness', 'unknown')
            })
    
    def get_learning_status(self) -> dict:
        """
        Current learning status
        """
        
        return {
            'learning_history_count': len(self.learning_history),
            'scale_models_count': len(self.scale_models),
            'knowledge_base_size': sum(
                len(items) if isinstance(items, list) else 1 
                for items in self.hierarchical_knowledge.values() 
                if isinstance(items, (list, dict))
            ),
            'meta_learner_trained': self.meta_learner is not None,
            'current_effectiveness': (
                self.learning_history[-1].get('overall_effectiveness', 0) 
                if self.learning_history else 0
            ),
            'last_learning_session': self.learning_history[-1] if self.learning_history else None
        }