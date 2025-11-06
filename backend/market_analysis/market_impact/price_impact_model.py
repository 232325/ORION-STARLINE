"""
Price Impact Model
=================

Price impact modeling va tahlil moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from scipy.optimize import minimize_scalar, minimize
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class PriceImpactModel:
    """Price impact modeling sinfi"""
    
    def __init__(self, model_type: str = 'permanent'):
        """
        Args:
            model_type: 'permanent', 'temporary', or 'hybrid'
        """
        self.model_type = model_type
        self.permanent_model = None
        self.temporary_model = None
        self.hybrid_model = None
        self.is_fitted = False
        
        # Model parameters
        self.alpha = 0.1  # Permanent impact coefficient
        self.beta = 0.05  # Temporary impact coefficient
        self.gamma = 0.02  # Recovery coefficient
        
        # Feature scalers
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
    
    def calculate_permanent_impact(self, volume: float, avg_volume: float, 
                                 volatility: float, time_of_day: float) -> float:
        """Doimiy (permanent) impact hisoblash"""
        if avg_volume <= 0 or volatility < 0:
            return 0.0
        
        # Volume ratio (trade size relative to average)
        volume_ratio = volume / avg_volume
        
        # Volatility adjustment
        vol_adjustment = 1 + volatility
        
        # Time of day adjustment (liquidity varies throughout day)
        time_adjustment = self._get_time_adjustment(time_of_day)
        
        # Permanent impact formula
        impact = self.alpha * (volume_ratio ** 0.6) * vol_adjustment * time_adjustment
        
        return impact
    
    def calculate_temporary_impact(self, volume: float, avg_volume: float,
                                 order_book_depth: float, spread: float) -> float:
        """Vaqtinchalik (temporary) impact hisoblash"""
        if avg_volume <= 0 or order_book_depth <= 0:
            return 0.0
        
        # Volume pressure relative to available liquidity
        volume_pressure = volume / order_book_depth
        
        # Spread adjustment (wider spreads = less liquidity)
        spread_adjustment = 1 + (spread / 0.001)  # Normalize to 1 pip
        
        # Temporary impact formula
        impact = self.beta * (volume_pressure ** 0.8) * spread_adjustment
        
        return impact
    
    def calculate_total_impact(self, volume: float, avg_volume: float,
                             volatility: float, time_of_day: float,
                             order_book_depth: float, spread: float) -> Dict[str, float]:
        """Jami (total) impact hisoblash"""
        permanent = self.calculate_permanent_impact(
            volume, avg_volume, volatility, time_of_day)
        
        temporary = self.calculate_temporary_impact(
            volume, avg_volume, order_book_depth, spread)
        
        # Recovery component (temporary impact diminishes over time)
        recovery = self.gamma * temporary
        
        total = permanent + temporary - recovery
        
        return {
            'permanent_impact': permanent,
            'temporary_impact': temporary,
            'recovery': recovery,
            'total_impact': total,
            'impact_per_unit': total / volume if volume > 0 else 0
        }
    
    def _get_time_adjustment(self, time_of_day: float) -> float:
        """Vaqtga qarab likvidlik sozlamasi"""
        # Typical forex session liquidity patterns (UTC hours)
        # Asian session: 0-8 (lower liquidity)
        # European session: 8-17 (higher liquidity) 
        # American session: 13-22 (higher liquidity)
        # Overlap periods: 8-13, 13-17 (highest liquidity)
        
        if 8 <= time_of_day <= 17:  # European + American overlap
            return 0.7  # Higher liquidity = lower impact
        elif 13 <= time_of_day <= 22:  # American session
            return 0.8
        elif 0 <= time_of_day <= 8:  # Asian session
            return 1.5  # Lower liquidity = higher impact
        else:  # Low activity period
            return 1.3
    
    def fit_from_historical_data(self, trades_data: pd.DataFrame, 
                                market_data: pd.DataFrame) -> Dict[str, float]:
        """
        Tarixiy ma'lumotlardan model parametrlarini o'rganish
        
        Args:
            trades_data: Trade execution ma'lumotlari
            market_data: Market ma'lumotlari (OHLCV)
        """
        if trades_data.empty or market_data.empty:
            raise ValueError("Bo'sh ma'lumotlar berildi")
        
        # Prepare features for ML model
        features = self._prepare_features(trades_data, market_data)
        
        if features.empty:
            return {'status': 'no_data'}
        
        # Target: price impact (price change after trade)
        targets = self._calculate_price_impact(trades_data, market_data)
        
        # Align features and targets
        common_index = features.index.intersection(targets.index)
        if len(common_index) < 10:
            return {'status': 'insufficient_data', 'records': len(common_index)}
        
        X = features.loc[common_index]
        y = targets.loc[common_index]
        
        # Handle missing values
        X = X.fillna(X.mean())
        y = y.fillna(y.mean())
        
        # Split data for training and validation
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        if len(X_train) < 5:
            return {'status': 'insufficient_training_data', 'records': len(X_train)}
        
        # Scale features
        X_train_scaled = self.scaler_X.fit_transform(X_train)
        X_test_scaled = self.scaler_X.transform(X_test)
        
        # Train model
        self.hybrid_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.hybrid_model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.hybrid_model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Extract feature importance for interpretability
        feature_importance = dict(zip(X.columns, self.hybrid_model.feature_importances_))
        
        self.is_fitted = True
        
        return {
            'status': 'success',
            'mse': mse,
            'r2_score': r2,
            'feature_importance': feature_importance,
            'training_records': len(X_train),
            'test_records': len(X_test)
        }
    
    def _prepare_features(self, trades_data: pd.DataFrame, 
                         market_data: pd.DataFrame) -> pd.DataFrame:
        """ML model uchun xususiyatlarni tayyorlash"""
        features = pd.DataFrame(index=trades_data.index)
        
        # Trade features
        if 'volume' in trades_data.columns:
            features['trade_size'] = trades_data['volume']
            features['log_trade_size'] = np.log1p(trades_data['volume'])
        
        # Market context features
        if not market_data.empty:
            # Merge with market data
            market_features = market_data.copy()
            
            # Calculate features
            market_features['returns'] = market_features['close'].pct_change()
            market_features['volatility'] = market_features['returns'].rolling(20).std()
            market_features['volume_ma'] = market_features['volume'].rolling(20).mean()
            market_features['price_change'] = market_features['close'].diff()
            
            # Hour from timestamp
            if isinstance(market_features.index, pd.DatetimeIndex):
                market_features['hour'] = market_features.index.hour
                market_features['day_of_week'] = market_features.index.dayofweek
            
            # Align with trades
            for col in market_features.columns:
                features[f'market_{col}'] = market_features[col]
        
        # Calculate volume ratios
        if 'volume' in trades_data.columns and 'market_volume_ma' in features.columns:
            features['volume_ratio'] = (trades_data['volume'] / 
                                      features['market_volume_ma'].reindex(trades_data.index))
        
        return features.fillna(method='ffill').fillna(0)
    
    def _calculate_price_impact(self, trades_data: pd.DataFrame, 
                              market_data: pd.DataFrame) -> pd.Series:
        """Price impact ni hisoblash"""
        impacts = pd.Series(index=trades_data.index, dtype=float)
        
        for idx in trades_data.index:
            # Get trade details
            trade_volume = trades_data.loc[idx, 'volume']
            trade_side = trades_data.loc[idx, 'side'] if 'side' in trades_data.columns else 1
            
            # Find price before and after trade
            trade_time = idx
            
            # Price before (previous close)
            before_mask = market_data.index < trade_time
            if not before_mask.any():
                continue
            
            price_before = market_data[before_mask]['close'].iloc[-1]
            
            # Price after (next close or current if available)
            after_mask = market_data.index >= trade_time
            if after_mask.any():
                price_after = market_data[after_mask]['close'].iloc[0]
            else:
                price_after = price_before
            
            # Calculate impact as percentage
            if price_before > 0:
                raw_impact = (price_after - price_before) / price_before
                # Adjust for trade side (buy = positive impact expectation)
                if trade_side < 0:  # sell
                    raw_impact = -raw_impact
                impacts.loc[idx] = raw_impact
        
        return impacts.dropna()
    
    def predict_impact(self, volume: float, market_conditions: Dict[str, float]) -> Dict[str, float]:
        """Model orqali impact bashoratlash"""
        if not self.is_fitted or self.hybrid_model is None:
            # Fallback to analytical model
            return self._analytical_prediction(volume, market_conditions)
        
        # Prepare features for prediction
        features = self._prepare_prediction_features(volume, market_conditions)
        
        if features.empty:
            return self._analytical_prediction(volume, market_conditions)
        
        # Scale features and predict
        features_scaled = self.scaler_X.transform(features)
        predicted_impact = self.hybrid_model.predict(features_scaled)[0]
        
        return {
            'predicted_impact': predicted_impact,
            'impact_per_unit': predicted_impact / volume if volume > 0 else 0,
            'method': 'ml_model'
        }
    
    def _analytical_prediction(self, volume: float, market_conditions: Dict[str, float]) -> Dict[str, float]:
        """Analytical model orqali prediction"""
        impact = self.calculate_total_impact(
            volume=volume,
            avg_volume=market_conditions.get('avg_volume', 1000000),
            volatility=market_conditions.get('volatility', 0.02),
            time_of_day=market_conditions.get('time_of_day', 12),
            order_book_depth=market_conditions.get('order_book_depth', 10000000),
            spread=market_conditions.get('spread', 0.001)
        )
        
        return {**impact, 'method': 'analytical'}
    
    def _prepare_prediction_features(self, volume: float, 
                                   market_conditions: Dict[str, float]) -> pd.DataFrame:
        """Prediction uchun xususiyatlarni tayyorlash"""
        # Create single row DataFrame
        data = {
            'trade_size': [volume],
            'log_trade_size': [np.log1p(volume)],
            'market_volatility': [market_conditions.get('volatility', 0.02)],
            'market_volume_ma': [market_conditions.get('avg_volume', 1000000)],
            'volume_ratio': [volume / market_conditions.get('avg_volume', 1000000)],
            'hour': [market_conditions.get('time_of_day', 12)],
            'day_of_week': [market_conditions.get('day_of_week', 1)]
        }
        
        df = pd.DataFrame(data, index=[0])
        return df
    
    def optimize_trade_size(self, target_impact: float, 
                          market_conditions: Dict[str, float]) -> Dict[str, any]:
        """Optimal trade size ni topish"""
        def objective(volume):
            impact = self._analytical_prediction(volume, market_conditions)
            return abs(impact['total_impact'] - target_impact)
        
        # Constraints
        max_volume = market_conditions.get('max_volume', 10000000)
        
        # Optimization
        result = minimize_scalar(
            objective,
            bounds=(1, max_volume),
            method='bounded'
        )
        
        optimal_volume = result.x
        optimal_impact = self._analytical_prediction(optimal_volume, market_conditions)
        
        return {
            'optimal_volume': optimal_volume,
            'expected_impact': optimal_impact['total_impact'],
            'impact_breakdown': optimal_impact,
            'optimization_success': result.success,
            'optimization_message': result.message
        }
    
    def calculate_market_impact_cost(self, trades: List[Dict]) -> Dict[str, float]:
        """Bir nechta trade uchun jami impact cost hisoblash"""
        total_impact_cost = 0
        total_volume = 0
        impact_details = []
        
        for trade in trades:
            volume = trade.get('volume', 0)
            market_conditions = trade.get('market_conditions', {})
            
            impact = self._analytical_prediction(volume, market_conditions)
            
            total_impact_cost += impact['total_impact'] * volume
            total_volume += volume
            
            impact_details.append({
                'trade_id': trade.get('id', 'unknown'),
                'volume': volume,
                'impact': impact['total_impact'],
                'cost': impact['total_impact'] * volume
            })
        
        avg_impact = total_impact_cost / total_volume if total_volume > 0 else 0
        
        return {
            'total_impact_cost': total_impact_cost,
            'average_impact': avg_impact,
            'total_volume': total_volume,
            'impact_per_unit': total_impact_cost / total_volume if total_volume > 0 else 0,
            'trade_details': impact_details
        }
    
    def get_model_parameters(self) -> Dict[str, float]:
        """Model parametrlarini olish"""
        return {
            'alpha_permanent': self.alpha,
            'beta_temporary': self.beta,
            'gamma_recovery': self.gamma,
            'model_type': self.model_type,
            'is_fitted': self.is_fitted
        }
    
    def update_parameters(self, alpha: float = None, beta: float = None, gamma: float = None):
        """Model parametrlarini yangilash"""
        if alpha is not None:
            self.alpha = alpha
        if beta is not None:
            self.beta = beta
        if gamma is not None:
            self.gamma = gamma