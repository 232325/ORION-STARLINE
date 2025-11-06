"""
Predictive Analytics Engine
Predictive Analytics - Advanced Forecasting for Financial Markets

Features:
- Time Series Forecasting
- Price Prediction Models
- Volatility Forecasting
- Market Direction Prediction
- Multi-timeframe Analysis
- Scenario Analysis & Stress Testing
- Monte Carlo Simulations
- Regime-based Predictions
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from decimal import Decimal, ROUND_DOWN
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
import json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import warnings
warnings.filterwarnings('ignore')

# Time Series Analysis
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Forecasting
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor

# Monte Carlo Simulation
from scipy.stats import norm, t
import random

# Statistical Analysis
from scipy import stats
from scipy.optimize import minimize
import itertools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """Prediction turlari"""
    PRICE = "price"
    VOLATILITY = "volatility"
    DIRECTION = "direction"
    PROBABILITY = "probability"
    RETURNS = "returns"
    CORRELATION = "correlation"

class ForecastHorizon(Enum):
    """Prognoz vaqt oralig'i"""
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"

class MarketScenario(Enum):
    """Bozor senariolari"""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    TRENDING = "trending"
    MEAN_REVERTING = "mean_reverting"
    CRISIS = "crisis"
    RECOVERY = "recovery"

@dataclass
class ForecastResult:
    """Prognoz natijasi"""
    symbol: str
    prediction_type: PredictionType
    forecast_horizon: ForecastHorizon
    predictions: List[float]
    confidences: List[float]
    timestamps: List[datetime]
    
    # Additional metrics
    model_name: str = ""
    accuracy_score: Optional[float] = None
    directional_accuracy: Optional[float] = None
    mape: Optional[float] = None
    rmse: Optional[float] = None
    
    # Scenario analysis
    scenario_probabilities: Dict[MarketScenario, float] = field(default_factory=dict)
    
    # Risk metrics
    max_forecast: Optional[float] = None
    min_forecast: Optional[float] = None
    expected_value: Optional[float] = None
    volatility_forecast: Optional[float] = None
    
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MonteCarloResult:
    """Monte Carlo simulyatsiya natijasi"""
    symbol: str
    simulations: np.ndarray  # Shape: (n_simulations, n_steps)
    confidence_intervals: Dict[str, Tuple[float, float]]
    probability_metrics: Dict[str, float]
    scenario_analysis: Dict[MarketScenario, float]
    
    # Statistics
    mean_path: np.ndarray
    median_path: np.ndarray
    percentile_5: np.ndarray
    percentile_95: np.ndarray
    
    # Risk measures
    var_95: float  # Value at Risk
    expected_shortfall: float
    maximum_drawdown: float
    
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RegimePrediction:
    """Regime-based prediction"""
    current_regime: MarketScenario
    regime_confidence: float
    predicted_regime_changes: List[Dict[str, Any]]
    regime_specific_predictions: Dict[MarketScenario, ForecastResult]
    transition_probabilities: np.ndarray

class PredictiveAnalytics:
    """Predictive Analytics Engine"""
    
    def __init__(self, 
                 risk_free_rate: float = 0.02,
                 confidence_level: float = 0.95):
        """
        Args:
            risk_free_rate: Risk-free rate (annual)
            confidence_level: Confidence level for predictions
        """
        self.risk_free_rate = risk_free_rate
        self.confidence_level = confidence_level
        
        # Model storage
        self.models = {}
        self.model_performance = {}
        self.feature_importance = {}
        
        # Prediction cache
        self.forecast_cache = {}
        self.regime_cache = {}
        
        # Simulation parameters
        self.monte_carlo_runs = 1000
        self.bootstrap_samples = 500
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.process_executor = ProcessPoolExecutor(max_workers=2)
        
        logger.info("Predictive Analytics Engine initialized")
    
    async def predict_price(self,
                          symbol: str,
                          price_data: pd.DataFrame,
                          forecast_horizon: ForecastHorizon,
                          model_type: str = "ensemble") -> ForecastResult:
        """
        Narx prognozi
        
        Args:
            symbol: Trading pair
            price_data: Historical price data
            forecast_horizon: Forecast time horizon
            model_type: Prediction model type
            
        Returns:
            ForecastResult: Price predictions
        """
        try:
            logger.info(f"Predicting price for {symbol} with {model_type} model")
            
            # Prepare data
            returns = price_data['close'].pct_change().dropna()
            
            # Determine steps to forecast
            steps = self._get_forecast_steps(forecast_horizon, len(price_data))
            
            if model_type == "arima":
                predictions = await self._arima_forecast(price_data['close'], steps)
            elif model_type == "lstm":
                predictions = await self._lstm_forecast(price_data, steps)
            elif model_type == "ensemble":
                predictions = await self._ensemble_forecast(price_data, steps)
            elif model_type == "random_forest":
                predictions = await self._random_forest_forecast(price_data, steps)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            # Calculate confidence intervals
            confidences = self._calculate_confidence_intervals(returns, len(predictions))
            
            # Generate timestamps
            last_timestamp = price_data['timestamp'].iloc[-1]
            timestamps = [self._add_time_period(last_timestamp, forecast_horizon, i+1) 
                         for i in range(len(predictions))]
            
            # Create result
            result = ForecastResult(
                symbol=symbol,
                prediction_type=PredictionType.PRICE,
                forecast_horizon=forecast_horizon,
                predictions=predictions,
                confidences=confidences,
                timestamps=timestamps,
                model_name=model_type,
                expected_value=np.mean(predictions),
                max_forecast=max(predictions),
                min_forecast=min(predictions)
            )
            
            # Cache result
            cache_key = f"{symbol}_{model_type}_{forecast_horizon.value}"
            self.forecast_cache[cache_key] = result
            
            logger.info(f"Price prediction completed for {symbol}: {len(predictions)} steps")
            return result
            
        except Exception as e:
            logger.error(f"Price prediction failed for {symbol}: {e}")
            raise
    
    async def predict_volatility(self,
                               symbol: str,
                               price_data: pd.DataFrame,
                               forecast_horizon: ForecastHorizon,
                               model_type: str = "garch") -> ForecastResult:
        """
        Volatilita prognozi
        
        Args:
            symbol: Trading pair
            price_data: Historical price data
            forecast_horizon: Forecast time horizon
            model_type: Volatility model type
            
        Returns:
            ForecastResult: Volatility predictions
        """
        try:
            logger.info(f"Predicting volatility for {symbol}")
            
            # Calculate returns
            returns = price_data['close'].pct_change().dropna()
            
            # Calculate realized volatility (rolling std)
            realized_vol = returns.rolling(window=24).std() * np.sqrt(365 * 24)  # Annualized
            
            # Simple volatility forecast using EWMA
            alpha = 0.06  # Decay factor
            ewma_vol = realized_vol.ewm(alpha=alpha).mean()
            
            # Forecast steps
            steps = self._get_forecast_steps(forecast_horizon, len(price_data))
            
            # Generate volatility forecasts
            last_vol = ewma_vol.iloc[-1]
            volatility_forecasts = []
            
            for i in range(steps):
                # Mean reversion to long-term average
                long_term_vol = realized_vol.mean()
                mean_reverted_vol = last_vol * np.exp(-0.1 * (i + 1)) + long_term_vol * (1 - np.exp(-0.1 * (i + 1)))
                volatility_forecasts.append(mean_reverted_vol)
            
            # Calculate confidence intervals
            vol_std = realized_vol.std()
            upper_bound = [vol + 1.96 * vol_std for vol in volatility_forecasts]
            lower_bound = [vol - 1.96 * vol_std for vol in volatility_forecasts]
            confidences = [(upper - lower) / mean * 100 for upper, lower, mean in 
                          zip(upper_bound, lower_bound, volatility_forecasts)]
            
            # Generate timestamps
            last_timestamp = price_data['timestamp'].iloc[-1]
            timestamps = [self._add_time_period(last_timestamp, forecast_horizon, i+1) 
                         for i in range(len(volatility_forecasts))]
            
            result = ForecastResult(
                symbol=symbol,
                prediction_type=PredictionType.VOLATILITY,
                forecast_horizon=forecast_horizon,
                predictions=volatility_forecasts,
                confidences=confidences,
                timestamps=timestamps,
                model_name=model_type,
                expected_value=np.mean(volatility_forecasts),
                max_forecast=max(volatility_forecasts),
                min_forecast=min(volatility_forecasts),
                volatility_forecast=np.mean(volatility_forecasts)
            )
            
            logger.info(f"Volatility prediction completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Volatility prediction failed for {symbol}: {e}")
            raise
    
    async def predict_direction(self,
                              symbol: str,
                              market_data: pd.DataFrame,
                              forecast_horizon: ForecastHorizon) -> ForecastResult:
        """
        Bozor yo'nalishi prognozi
        
        Args:
            symbol: Trading pair
            market_data: Market data with features
            forecast_horizon: Forecast time horizon
            
        Returns:
            ForecastResult: Direction predictions
        """
        try:
            logger.info(f"Predicting direction for {symbol}")
            
            # Create features
            features = await self._create_direction_features(market_data)
            
            # Create target variable (1 for up, 0 for down)
            returns = market_data['close'].pct_change()
            direction = (returns > 0).astype(int)
            
            # Split data
            split_idx = int(len(features) * 0.8)
            X_train, X_test = features[:split_idx], features[split_idx:]
            y_train, y_test = direction[:split_idx], direction[split_idx:]
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Predict probabilities for test set
            prob_predictions = model.predict(X_test)
            direction_predictions = (prob_predictions > 0.5).astype(int)
            
            # Calculate accuracy
            accuracy = np.mean(direction_predictions == y_test)
            directional_accuracy = accuracy
            
            # Generate future predictions
            steps = self._get_forecast_steps(forecast_horizon, len(market_data))
            
            # For simplicity, use last few predictions as forecast
            recent_probs = prob_predictions[-min(steps, len(prob_predictions)):]
            
            # If we need more steps, extend with noise around recent average
            if len(recent_probs) < steps:
                avg_prob = np.mean(recent_probs)
                additional_probs = np.random.normal(avg_prob, 0.1, steps - len(recent_probs))
                recent_probs = np.concatenate([recent_probs, additional_probs])
            
            # Convert to direction (1=up, 0=down)
            direction_forecasts = (recent_probs > 0.5).astype(int).tolist()
            confidence_scores = [abs(prob - 0.5) * 2 for prob in recent_probs]  # 0-1 scale
            
            # Generate timestamps
            last_timestamp = market_data['timestamp'].iloc[-1]
            timestamps = [self._add_time_period(last_timestamp, forecast_horizon, i+1) 
                         for i in range(len(direction_forecasts))]
            
            result = ForecastResult(
                symbol=symbol,
                prediction_type=PredictionType.DIRECTION,
                forecast_horizon=forecast_horizon,
                predictions=direction_forecasts,
                confidences=confidence_scores,
                timestamps=timestamps,
                model_name="random_forest",
                directional_accuracy=directional_accuracy,
                accuracy_score=accuracy
            )
            
            logger.info(f"Direction prediction completed for {symbol}: {accuracy:.2%} accuracy")
            return result
            
        except Exception as e:
            logger.error(f"Direction prediction failed for {symbol}: {e}")
            raise
    
    async def monte_carlo_simulation(self,
                                   symbol: str,
                                   price_data: pd.DataFrame,
                                   forecast_horizon: ForecastHorizon,
                                   n_simulations: int = 1000,
                                   initial_price: Optional[float] = None) -> MonteCarloResult:
        """
        Monte Carlo simulyatsiya
        
        Args:
            symbol: Trading pair
            price_data: Historical price data
            forecast_horizon: Forecast time horizon
            n_simulations: Number of simulations
            initial_price: Starting price
            
        Returns:
            MonteCarloResult: Simulation results
        """
        try:
            logger.info(f"Running Monte Carlo simulation for {symbol}: {n_simulations} simulations")
            
            # Calculate returns statistics
            returns = price_data['close'].pct_change().dropna()
            mu = returns.mean()  # Drift
            sigma = returns.std()  # Volatility
            
            # Parameters
            if initial_price is None:
                initial_price = price_data['close'].iloc[-1]
            
            steps = self._get_forecast_steps(forecast_horizon, len(price_data))
            dt = 1.0  # Time step (assuming daily data)
            
            # Generate random walks
            simulations = np.zeros((n_simulations, steps + 1))
            simulations[:, 0] = initial_price
            
            for i in range(1, steps + 1):
                # Random shock
                random_shock = np.random.normal(0, 1, n_simulations)
                
                # Geometric Brownian Motion
                price_change = mu * dt + sigma * np.sqrt(dt) * random_shock
                simulations[:, i] = simulations[:, i-1] * np.exp(price_change)
            
            # Calculate statistics
            final_prices = simulations[:, -1]
            mean_path = np.mean(simulations, axis=0)
            median_path = np.median(simulations, axis=0)
            percentile_5 = np.percentile(simulations, 5, axis=0)
            percentile_95 = np.percentile(simulations, 95, axis=0)
            
            # Confidence intervals
            confidence_intervals = {
                '95%': (np.percentile(final_prices, 2.5), np.percentile(final_prices, 97.5)),
                '90%': (np.percentile(final_prices, 5), np.percentile(final_prices, 95)),
                '80%': (np.percentile(final_prices, 10), np.percentile(final_prices, 90))
            }
            
            # Probability metrics
            prob_profit = np.mean(final_prices > initial_price)
            prob_loss_10pct = np.mean(final_prices < initial_price * 0.9)
            prob_gain_10pct = np.mean(final_prices > initial_price * 1.1)
            
            probability_metrics = {
                'probability_profit': prob_profit,
                'probability_loss_10pct': prob_loss_10pct,
                'probability_gain_10pct': prob_gain_10pct,
                'expected_return': np.mean((final_prices - initial_price) / initial_price),
                'median_return': np.median((final_prices - initial_price) / initial_price)
            }
            
            # Value at Risk (VaR)
            returns_distribution = (final_prices - initial_price) / initial_price
            var_95 = np.percentile(returns_distribution, 5)
            expected_shortfall = np.mean(returns_distribution[returns_distribution <= var_95])
            
            # Maximum drawdown simulation
            max_drawdowns = []
            for sim in simulations:
                peak = np.maximum.accumulate(sim)
                drawdown = (sim - peak) / peak
                max_drawdowns.append(abs(np.min(drawdown)))
            
            maximum_drawdown = np.mean(max_drawdowns)
            
            # Scenario analysis
            scenario_analysis = self._analyze_scenarios(final_prices, initial_price)
            
            result = MonteCarloResult(
                symbol=symbol,
                simulations=simulations,
                confidence_intervals=confidence_intervals,
                probability_metrics=probability_metrics,
                scenario_analysis=scenario_analysis,
                mean_path=mean_path,
                median_path=median_path,
                percentile_5=percentile_5,
                percentile_95=percentile_95,
                var_95=var_95,
                expected_shortfall=expected_shortfall,
                maximum_drawdown=maximum_drawdown
            )
            
            logger.info(f"Monte Carlo simulation completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Monte Carlo simulation failed for {symbol}: {e}")
            raise
    
    async def regime_based_prediction(self,
                                    symbol: str,
                                    market_data: pd.DataFrame,
                                    forecast_horizon: ForecastHorizon) -> RegimePrediction:
        """
        Regime-based prediction
        
        Args:
            symbol: Trading pair
            market_data: Market data
            forecast_horizon: Forecast time horizon
            
        Returns:
            RegimePrediction: Regime-based forecast
        """
        try:
            logger.info(f"Running regime-based prediction for {symbol}")
            
            # Detect current regime
            current_regime = await self._detect_market_regime(market_data)
            
            # Calculate regime confidence
            regime_confidence = await self._calculate_regime_confidence(market_data, current_regime)
            
            # Predict regime changes
            regime_changes = await self._predict_regime_changes(market_data, current_regime)
            
            # Generate regime-specific predictions
            regime_predictions = {}
            for regime in MarketScenario:
                if regime == current_regime:
                    # Current regime - use regular prediction
                    predictions = await self.predict_price(symbol, market_data, forecast_horizon)
                else:
                    # Alternative regime - adjust predictions
                    predictions = await self._predict_alternative_regime(
                        symbol, market_data, forecast_horizon, regime
                    )
                
                regime_predictions[regime] = predictions
            
            # Calculate transition probabilities
            transition_probs = await self._calculate_transition_probabilities(
                market_data, current_regime
            )
            
            result = RegimePrediction(
                current_regime=current_regime,
                regime_confidence=regime_confidence,
                predicted_regime_changes=regime_changes,
                regime_specific_predictions=regime_predictions,
                transition_probabilities=transition_probs
            )
            
            logger.info(f"Regime-based prediction completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Regime-based prediction failed for {symbol}: {e}")
            raise
    
    async def multi_timeframe_analysis(self,
                                     symbol: str,
                                     price_data: pd.DataFrame,
                                     timeframes: List[ForecastHorizon]) -> Dict[ForecastHorizon, ForecastResult]:
        """
        Ko'p vaqt doirasi tahlili
        
        Args:
            symbol: Trading pair
            price_data: Historical price data
            timeframes: List of timeframes to analyze
            
        Returns:
            Dict of timeframe -> predictions
        """
        try:
            logger.info(f"Multi-timeframe analysis for {symbol}: {len(timeframes)} timeframes")
            
            # Run predictions in parallel
            tasks = [
                self.predict_price(symbol, price_data, tf, model_type="ensemble")
                for tf in timeframes
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            timeframe_predictions = {}
            for i, tf in enumerate(timeframes):
                if isinstance(results[i], Exception):
                    logger.error(f"Failed prediction for {tf.value}: {results[i]}")
                    continue
                
                timeframe_predictions[tf] = results[i]
            
            # Find consensus
            consensus = self._find_timeframe_consensus(timeframe_predictions)
            
            # Add consensus to results
            if consensus:
                timeframe_predictions['consensus'] = consensus
            
            logger.info(f"Multi-timeframe analysis completed for {symbol}")
            return timeframe_predictions
            
        except Exception as e:
            logger.error(f"Multi-timeframe analysis failed for {symbol}: {e}")
            raise
    
    # Helper methods
    
    def _get_forecast_steps(self, forecast_horizon: ForecastHorizon, data_length: int) -> int:
        """Forecast steps hisoblash"""
        horizon_map = {
            ForecastHorizon.M5: min(data_length // 12, 24),  # Max 24 periods
            ForecastHorizon.M15: min(data_length // 4, 24),
            ForecastHorizon.M30: min(data_length // 2, 24),
            ForecastHorizon.H1: min(data_length, 48),
            ForecastHorizon.H4: min(data_length // 4, 30),
            ForecastHorizon.D1: min(data_length // 24, 30),
            ForecastHorizon.W1: min(data_length // 168, 12),
            ForecastHorizon.MN1: min(data_length // 720, 12)
        }
        
        return horizon_map.get(forecast_horizon, 24)
    
    def _add_time_period(self, timestamp: datetime, forecast_horizon: ForecastHorizon, steps: int) -> datetime:
        """Timestamp ga vaqt qo'shish"""
        if forecast_horizon == ForecastHorizon.M5:
            return timestamp + timedelta(minutes=5 * steps)
        elif forecast_horizon == ForecastHorizon.M15:
            return timestamp + timedelta(minutes=15 * steps)
        elif forecast_horizon == ForecastHorizon.M30:
            return timestamp + timedelta(minutes=30 * steps)
        elif forecast_horizon == ForecastHorizon.H1:
            return timestamp + timedelta(hours=steps)
        elif forecast_horizon == ForecastHorizon.H4:
            return timestamp + timedelta(hours=4 * steps)
        elif forecast_horizon == ForecastHorizon.D1:
            return timestamp + timedelta(days=steps)
        elif forecast_horizon == ForecastHorizon.W1:
            return timestamp + timedelta(weeks=steps)
        elif forecast_horizon == ForecastHorizon.MN1:
            return timestamp + timedelta(days=30 * steps)
        else:
            return timestamp + timedelta(hours=steps)
    
    async def _arima_forecast(self, prices: pd.Series, steps: int) -> List[float]:
        """ARIMA model forecast"""
        try:
            # Fit ARIMA model
            model = ARIMA(prices, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Forecast
            forecast = fitted_model.forecast(steps=steps)
            return forecast.tolist()
            
        except Exception as e:
            logger.warning(f"ARIMA forecast failed, using simple mean: {e}")
            # Fallback to simple mean
            mean_price = prices.mean()
            return [mean_price] * steps
    
    async def _lstm_forecast(self, price_data: pd.DataFrame, steps: int) -> List[float]:
        """LSTM model forecast (simplified)"""
        try:
            # Simple LSTM-like forecast using exponential smoothing
            alpha = 0.3
            smoothed_prices = price_data['close'].ewm(alpha=alpha).mean()
            
            # Forecast using trend
            last_price = price_data['close'].iloc[-1]
            last_trend = (price_data['close'].iloc[-1] - price_data['close'].iloc[-5]) / 5
            
            forecasts = []
            for i in range(steps):
                forecast_price = last_price + last_trend * (i + 1)
                forecasts.append(forecast_price)
            
            return forecasts
            
        except Exception as e:
            logger.warning(f"LSTM forecast failed, using simple trend: {e}")
            return [price_data['close'].iloc[-1]] * steps
    
    async def _ensemble_forecast(self, price_data: pd.DataFrame, steps: int) -> List[float]:
        """Ensemble model forecast"""
        try:
            # Combine multiple forecasts
            arima_forecast = await self._arima_forecast(price_data['close'], steps)
            lstm_forecast = await self._lstm_forecast(price_data, steps)
            
            # Simple average ensemble
            ensemble_forecast = [(a + l) / 2 for a, l in zip(arima_forecast, lstm_forecast)]
            
            return ensemble_forecast
            
        except Exception as e:
            logger.warning(f"Ensemble forecast failed, using ARIMA: {e}")
            return await self._arima_forecast(price_data['close'], steps)
    
    async def _random_forest_forecast(self, price_data: pd.DataFrame, steps: int) -> List[float]:
        """Random Forest forecast"""
        try:
            # Create simple features
            features = []
            targets = []
            
            for i in range(5, len(price_data)):
                feature_row = [
                    price_data['close'].iloc[i-5:i].mean(),
                    price_data['close'].iloc[i-5:i].std(),
                    price_data['close'].iloc[i-1],
                    price_data['volume'].iloc[i-5:i].mean() if 'volume' in price_data.columns else 0
                ]
                features.append(feature_row)
                targets.append(price_data['close'].iloc[i])
            
            if len(features) < 10:
                raise ValueError("Insufficient data for Random Forest")
            
            # Train model
            X = np.array(features)
            y = np.array(targets)
            
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X[:-1], y[1:])  # Predict next value
            
            # Forecast
            forecasts = []
            last_features = features[-1]
            
            for _ in range(steps):
                prediction = model.predict([last_features])[0]
                forecasts.append(prediction)
                
                # Update features for next prediction
                last_features = last_features[1:] + [prediction]
            
            return forecasts
            
        except Exception as e:
            logger.warning(f"Random Forest forecast failed: {e}")
            return await self._arima_forecast(price_data['close'], steps)
    
    def _calculate_confidence_intervals(self, returns: pd.Series, n_steps: int) -> List[float]:
        """Confidence intervals hisoblash"""
        try:
            volatility = returns.std()
            mean_return = returns.mean()
            
            # Calculate confidence intervals
            confidence_intervals = []
            for i in range(n_steps):
                # Simplified confidence based on time and volatility
                time_factor = np.sqrt(i + 1)
                confidence = max(50, 100 - time_factor * 5)  # Decreases over time
                confidence_intervals.append(confidence)
            
            return confidence_intervals
            
        except Exception as e:
            return [70] * n_steps  # Default confidence
    
    async def _create_direction_features(self, market_data: pd.DataFrame) -> np.ndarray:
        """Direction prediction features yaratish"""
        try:
            features = []
            
            # Price-based features
            prices = market_data['close']
            
            for i in range(5, len(market_data)):
                feature_row = [
                    prices.iloc[i-1] / prices.iloc[i-5] - 1,  # 5-period return
                    (prices.iloc[i-1] - prices.iloc[i-3]) / prices.iloc[i-3],  # 3-period return
                    prices.iloc[i-1] / prices.rolling(20).mean().iloc[i-1] - 1 if i >= 20 else 0,  # Distance from MA
                    (prices.iloc[i-1] - prices.min(i-20, prices.iloc[i-1])) / (prices.max(i-20, prices.iloc[i-1]) - prices.min(i-20, prices.iloc[i-1])) if i >= 20 else 0.5,  # Position in range
                ]
                
                # Volume features if available
                if 'volume' in market_data.columns:
                    vol = market_data['volume']
                    feature_row.extend([
                        vol.iloc[i-1] / vol.iloc[i-5:i].mean() - 1 if i >= 5 else 0,  # Volume ratio
                        vol.rolling(10).mean().iloc[i-1] if i >= 10 else vol.iloc[i-1]
                    ])
                else:
                    feature_row.extend([0, 0])
                
                features.append(feature_row)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Feature creation failed: {e}")
            return np.array([])
    
    async def _detect_market_regime(self, market_data: pd.DataFrame) -> MarketScenario:
        """Market regime detection"""
        try:
            returns = market_data['close'].pct_change().dropna()
            
            # Calculate regime indicators
            recent_returns = returns.tail(20)
            volatility = recent_returns.std()
            avg_volatility = returns.std()
            
            price_trend = (market_data['close'].iloc[-1] / market_data['close'].iloc[-20] - 1)
            
            # Determine regime
            if volatility > avg_volatility * 1.5:
                if price_trend > 0.05:
                    return MarketScenario.HIGH_VOLATILITY
                else:
                    return MarketScenario.CRISIS
            elif price_trend > 0.1:
                return MarketScenario.BULL_MARKET
            elif price_trend < -0.1:
                return MarketScenario.BEAR_MARKET
            elif abs(price_trend) < 0.02:
                return MarketScenario.MEAN_REVERTING
            else:
                return MarketScenario.TRENDING
                
        except Exception as e:
            logger.error(f"Regime detection failed: {e}")
            return MarketScenario.TRENDING
    
    async def _calculate_regime_confidence(self, market_data: pd.DataFrame, regime: MarketScenario) -> float:
        """Regime confidence calculation"""
        try:
            # Simplified confidence calculation
            returns = market_data['close'].pct_change().dropna()
            
            if regime in [MarketScenario.BULL_MARKET, MarketScenario.BEAR_MARKET]:
                # Trend-based regime
                recent_trend = (market_data['close'].iloc[-1] / market_data['close'].iloc[-10] - 1)
                confidence = min(95, abs(recent_trend) * 500 + 50)
            else:
                # Volatility-based regime
                recent_vol = returns.tail(10).std()
                avg_vol = returns.std()
                confidence = min(95, (recent_vol / avg_vol) * 50 + 50)
            
            return confidence
            
        except Exception as e:
            return 50.0
    
    async def _predict_regime_changes(self, market_data: pd.DataFrame, current_regime: MarketScenario) -> List[Dict[str, Any]]:
        """Regime change predictions"""
        try:
            # Simplified regime change prediction
            changes = []
            
            # Add scenario analysis
            if current_regime == MarketScenario.BULL_MARKET:
                changes.append({
                    'probability': 0.3,
                    'scenario': MarketScenario.HIGH_VOLATILITY.value,
                    'timeframe': '1-2 weeks',
                    'description': 'Potential volatility spike'
                })
            elif current_regime == MarketScenario.BEAR_MARKET:
                changes.append({
                    'probability': 0.4,
                    'scenario': MarketScenario.RECOVERY.value,
                    'timeframe': '2-4 weeks',
                    'description': 'Potential recovery phase'
                })
            
            return changes
            
        except Exception as e:
            return []
    
    async def _predict_alternative_regime(self,
                                        symbol: str,
                                        market_data: pd.DataFrame,
                                        forecast_horizon: ForecastHorizon,
                                        regime: MarketScenario) -> ForecastResult:
        """Alternative regime prediction"""
        try:
            # Get base prediction
            base_prediction = await self.predict_price(symbol, market_data, forecast_horizon)
            
            # Adjust based on regime
            adjustments = {
                MarketScenario.BULL_MARKET: 1.05,
                MarketScenario.BEAR_MARKET: 0.95,
                MarketScenario.HIGH_VOLATILITY: 1.0,
                MarketScenario.LOW_VOLATILITY: 1.0,
                MarketScenario.TRENDING: 1.02,
                MarketScenario.MEAN_REVERTING: 0.98,
                MarketScenario.CRISIS: 0.90,
                MarketScenario.RECOVERY: 1.08
            }
            
            adjustment = adjustments.get(regime, 1.0)
            adjusted_predictions = [p * adjustment for p in base_prediction.predictions]
            
            # Update result
            base_prediction.predictions = adjusted_predictions
            base_prediction.model_name = f"{base_prediction.model_name}_{regime.value}"
            
            return base_prediction
            
        except Exception as e:
            logger.error(f"Alternative regime prediction failed: {e}")
            return await self.predict_price(symbol, market_data, forecast_horizon)
    
    async def _calculate_transition_probabilities(self, 
                                                market_data: pd.DataFrame, 
                                                current_regime: MarketScenario) -> np.ndarray:
        """Regime transition probabilities"""
        try:
            # Simplified transition matrix (in reality would be learned from historical data)
            # Rows: current regime, Columns: next regime
            transition_matrix = {
                MarketScenario.BULL_MARKET: {
                    MarketScenario.BULL_MARKET: 0.6,
                    MarketScenario.HIGH_VOLATILITY: 0.2,
                    MarketScenario.TRENDING: 0.15,
                    MarketScenario.MEAN_REVERTING: 0.05
                },
                MarketScenario.BEAR_MARKET: {
                    MarketScenario.BEAR_MARKET: 0.5,
                    MarketScenario.RECOVERY: 0.25,
                    MarketScenario.MEAN_REVERTING: 0.15,
                    MarketScenario.HIGH_VOLATILITY: 0.1
                },
                MarketScenario.HIGH_VOLATILITY: {
                    MarketScenario.HIGH_VOLATILITY: 0.4,
                    MarketScenario.TRENDING: 0.3,
                    MarketScenario.BULL_MARKET: 0.15,
                    MarketScenario.BEAR_MARKET: 0.15
                }
            }
            
            # Return probabilities for current regime
            current_probs = transition_matrix.get(current_regime, {
                MarketScenario.TRENDING: 0.4,
                MarketScenario.MEAN_REVERTING: 0.3,
                MarketScenario.HIGH_VOLATILITY: 0.3
            })
            
            return np.array(list(current_probs.values()))
            
        except Exception as e:
            return np.array([0.4, 0.3, 0.2, 0.1])  # Default probabilities
    
    def _analyze_scenarios(self, final_prices: np.ndarray, initial_price: float) -> Dict[MarketScenario, float]:
        """Scenario analysis"""
        try:
            returns = (final_prices - initial_price) / initial_price
            
            scenarios = {
                MarketScenario.BULL_MARKET: np.mean(returns > 0.1),  # >10% gain
                MarketScenario.BEAR_MARKET: np.mean(returns < -0.1),  # >10% loss
                MarketScenario.HIGH_VOLATILITY: np.mean(np.abs(returns) > 0.2),  # >20% move
                MarketScenario.MEAN_REVERTING: np.mean(np.abs(returns) < 0.05),  # <5% move
                MarketScenario.TRENDING: np.mean(returns > 0.05),  # >5% gain
                MarketScenario.RECOVERY: np.mean(returns > 0.02),  # Small gain
            }
            
            return scenarios
            
        except Exception as e:
            return {}
    
    def _find_timeframe_consensus(self, 
                                timeframe_predictions: Dict[ForecastHorizon, ForecastResult]) -> Optional[ForecastResult]:
        """Find consensus across timeframes"""
        try:
            # Simple consensus: average of predictions
            if len(timeframe_predictions) < 2:
                return None
            
            predictions_list = list(timeframe_predictions.values())
            first_pred = predictions_list[0]
            
            # Average predictions
            avg_predictions = []
            for i in range(len(first_pred.predictions)):
                preds = [p.predictions[i] for p in predictions_list if i < len(p.predictions)]
                avg_predictions.append(np.mean(preds))
            
            # Average confidences
            avg_confidences = []
            for i in range(len(first_pred.confidences)):
                confs = [p.confidences[i] for p in predictions_list if i < len(p.confidences)]
                avg_confidences.append(np.mean(confs))
            
            # Create consensus result
            consensus = ForecastResult(
                symbol=first_pred.symbol,
                prediction_type=first_pred.prediction_type,
                forecast_horizon=first_pred.forecast_horizon,
                predictions=avg_predictions,
                confidences=avg_confidences,
                timestamps=first_pred.timestamps,
                model_name="consensus",
                expected_value=np.mean(avg_predictions)
            )
            
            return consensus
            
        except Exception as e:
            logger.error(f"Consensus calculation failed: {e}")
            return None
    
    async def cleanup(self):
        """Resurslarni tozalash"""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            
            if hasattr(self, 'process_executor'):
                self.process_executor.shutdown(wait=True)
            
            # Clear caches
            self.forecast_cache.clear()
            self.regime_cache.clear()
            
            logger.info("Predictive Analytics cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

# Test function
async def test_predictive_analytics():
    """Test Predictive Analytics Engine"""
    try:
        print("🔮 Predictive Analytics Engine Test")
        print("=" * 50)
        
        # Initialize engine
        engine = PredictiveAnalytics()
        
        # Create sample data
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=500, freq='H')
        
        # Generate realistic price data
        base_price = 50000
        returns = np.random.normal(0.001, 0.02, 500)
        prices = [base_price]
        
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(new_price)
        
        # Create OHLCV data
        price_data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices[1:] + [prices[-1]],
            'volume': np.random.exponential(1000, 500)
        })
        
        print(f"📊 Sample Data Created:")
        print(f"  Date Range: {dates[0].date()} to {dates[-1].date()}")
        print(f"  Data Points: {len(price_data)}")
        print(f"  Price Range: ${min(prices):,.2f} - ${max(prices):,.2f}")
        
        # Test price prediction
        print("\n💰 Price Prediction Test:")
        price_forecast = await engine.predict_price(
            "BTCUSDT", 
            price_data, 
            ForecastHorizon.H1,
            model_type="ensemble"
        )
        
        print(f"  Model: {price_forecast.model_name}")
        print(f"  Steps: {len(price_forecast.predictions)}")
        print(f"  Current Price: ${price_data['close'].iloc[-1]:,.2f}")
        print(f"  Next Prediction: ${price_forecast.predictions[0]:,.2f}")
        print(f"  Expected Value: ${price_forecast.expected_value:,.2f}")
        print(f"  Range: ${price_forecast.min_forecast:,.2f} - ${price_forecast.max_forecast:,.2f}")
        
        # Test volatility prediction
        print("\n📈 Volatility Prediction Test:")
        vol_forecast = await engine.predict_volatility(
            "BTCUSDT",
            price_data,
            ForecastHorizon.H1
        )
        
        print(f"  Model: {vol_forecast.model_name}")
        print(f"  Current Volatility: {price_data['close'].pct_change().std()*100:.2f}%")
        print(f"  Predicted Volatility: {vol_forecast.volatility_forecast*100:.2f}%")
        print(f"  Volatility Range: {vol_forecast.min_forecast*100:.2f}% - {vol_forecast.max_forecast*100:.2f}%")
        
        # Test direction prediction
        print("\n🎯 Direction Prediction Test:")
        direction_forecast = await engine.predict_direction(
            "BTCUSDT",
            price_data,
            ForecastHorizon.H1
        )
        
        print(f"  Model: {direction_forecast.model_name}")
        print(f"  Accuracy: {direction_forecast.accuracy_score:.2%}")
        print(f"  Directional Accuracy: {direction_forecast.directional_accuracy:.2%}")
        print(f"  Predictions: {direction_forecast.predictions[:5]}")
        
        # Test Monte Carlo simulation
        print("\n🎲 Monte Carlo Simulation Test:")
        mc_result = await engine.monte_carlo_simulation(
            "BTCUSDT",
            price_data,
            ForecastHorizon.D1,
            n_simulations=500
        )
        
        current_price = price_data['close'].iloc[-1]
        print(f"  Simulations: {mc_result.simulations.shape[0]}")
        print(f"  Steps: {mc_result.simulations.shape[1]}")
        print(f"  Initial Price: ${current_price:,.2f}")
        print(f"  Final Price (Mean): ${mc_result.mean_path[-1]:,.2f}")
        print(f"  Expected Return: {mc_result.probability_metrics['expected_return']:.2%}")
        print(f"  Probability of Profit: {mc_result.probability_metrics['probability_profit']:.2%}")
        print(f"  VaR (95%): {mc_result.var_95:.2%}")
        print(f"  Expected Shortfall: {mc_result.expected_shortfall:.2%}")
        
        # Test regime-based prediction
        print("\n🏛️ Regime-based Prediction Test:")
        regime_pred = await engine.regime_based_prediction(
            "BTCUSDT",
            price_data,
            ForecastHorizon.D1
        )
        
        print(f"  Current Regime: {regime_pred.current_regime.value}")
        print(f"  Regime Confidence: {regime_pred.regime_confidence:.1f}%")
        print(f"  Regime Changes: {len(regime_pred.predicted_regime_changes)}")
        
        for change in regime_pred.predicted_regime_changes:
            print(f"    - {change['scenario']}: {change['probability']:.1%} ({change['timeframe']})")
        
        # Test multi-timeframe analysis
        print("\n⏰ Multi-timeframe Analysis Test:")
        timeframes = [ForecastHorizon.H1, ForecastHorizon.H4, ForecastHorizon.D1]
        mtf_result = await engine.multi_timeframe_analysis(
            "BTCUSDT",
            price_data,
            timeframes
        )
        
        print(f"  Timeframes Analyzed: {len(mtf_result)}")
        for tf, forecast in mtf_result.items():
            if tf != 'consensus':
                print(f"    - {tf.value}: ${forecast.predictions[0]:,.2f}")
        
        if 'consensus' in mtf_result:
            consensus = mtf_result['consensus']
            print(f"  Consensus Prediction: ${consensus.predictions[0]:,.2f}")
        
        await engine.cleanup()
        
        print("\n✅ Predictive Analytics Engine test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_predictive_analytics())