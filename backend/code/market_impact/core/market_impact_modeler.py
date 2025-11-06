"""
Market Impact Modeler

Bu modul barcha price impact modellari uchun unified interfeys
va comprehensive analysis ta'minlaydi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from ..models import (
    KyleLambdaModel, ObizhaevaWangModel, 
    AlmgrenChrissModel, BertsimasLoModel
)
from ..models.kyle_lambda import KyleModelParameters
from ..models.obizhaeva_wang import ObizhaevaWangParameters
from ..models.almgren_chriss import AlmgrenChrissParameters
from ..models.bertsimas_lo import BertsimasLoParameters


@dataclass
class ModelComparison:
    """Model comparison results"""
    model_name: str
    price_impact: float
    confidence_score: float
    model_fit: float
    parameters: Dict[str, float]


@dataclass
class ImpactForecast:
    """Price impact forecast"""
    forecast_horizon: int
    impact_predictions: List[float]
    confidence_intervals: List[Tuple[float, float]]
    model_contributions: Dict[str, float]


class MarketImpactModeler:
    """
    Comprehensive Market Impact Modeler
    
    Barcha price impact modellari ni birlashtirib,
    unified analysis va forecasting ta'minlaydi.
    """
    
    def __init__(self, model_config: Dict[str, Dict] = None):
        """
        Initialize modeler
        
        Args:
            model_config: Optional model configuration
        """
        # Initialize models with default or custom parameters
        self.models = self._initialize_models(model_config)
        self.model_weights = {}
        self.calibration_data = None
        self.forecast_cache = {}
        
    def _initialize_models(self, config: Dict[str, Dict] = None) -> Dict:
        """Initialize all price impact models"""
        models = {}
        
        # Default Kyle model parameters
        kyle_config = config.get('kyle', {}) if config else {}
        kyle_params = KyleModelParameters(
            lambda_param=kyle_config.get('lambda_param', 0.01),
            sigma_v=kyle_config.get('sigma_v', 0.02),
            sigma_u=kyle_config.get('sigma_u', 0.1),
            theta=kyle_config.get('theta', 0.5)
        )
        models['kyle'] = KyleLambdaModel(kyle_params)
        
        # Default Obizhaeva-Wang parameters
        ow_config = config.get('obizhaeva_wang', {}) if config else {}
        ow_params = ObizhaevaWangParameters(
            alpha=ow_config.get('alpha', 0.001),
            beta=ow_config.get('beta', 0.1),
            gamma=ow_config.get('gamma', 0.01),
            delta=ow_config.get('delta', 0.001),
            sigma=ow_config.get('sigma', 0.02)
        )
        models['obizhaeva_wang'] = ObizhaevaWangModel(ow_params)
        
        # Default Almgren-Chriss parameters
        ac_config = config.get('almgren_chriss', {}) if config else {}
        ac_params = AlmgrenChrissParameters(
            eta=ac_config.get('eta', 0.0001),
            gamma=ac_config.get('gamma', 0.01),
            sigma=ac_config.get('sigma', 0.02),
            T=ac_config.get('T', 1.0),  # 1 hour
            lambda_risk=ac_config.get('lambda_risk', 1e-6)
        )
        models['almgren_chriss'] = AlmgrenChrissModel(ac_params)
        
        # Default Bertsimas-Lo parameters
        bl_config = config.get('bertsimas_lo', {}) if config else {}
        bl_params = BertsimasLoParameters(
            kappa=bl_config.get('kappa', 0.001),
            phi=bl_config.get('phi', 0.1),
            lambda_noise=bl_config.get('lambda_noise', 0.1),
            theta_market=bl_config.get('theta_market', 0.01),
            gamma_adapt=bl_config.get('gamma_adapt', 0.5),
            sigma_info=bl_config.get('sigma_info', 0.02)
        )
        models['bertsimas_lo'] = BertsimasLoModel(bl_params)
        
        return models
        
    def calibrate_models(self, historical_data: pd.DataFrame,
                        calibration_method: str = 'ols') -> Dict[str, Dict]:
        """
        Model parametrlarini historical data dan calibrate qilish
        
        Args:
            historical_data: Historical trade data
            calibration_method: 'ols', 'mle', 'bayesian'
            
        Returns:
            Calibration results for each model
        """
        if len(historical_data) < 100:
            raise ValueError("Insufficient data for calibration (need at least 100 points)")
            
        calibration_results = {}
        
        # Kyle model calibration
        try:
            kyle_estimate = self.models['kyle'].calculate_lambda_estimate(historical_data)
            calibration_results['kyle'] = {
                'estimated_lambda': kyle_estimate,
                'calibration_success': True,
                'method': calibration_method
            }
        except Exception as e:
            calibration_results['kyle'] = {
                'error': str(e),
                'calibration_success': False
            }
            
        # Obizhaeva-Wang model calibration
        try:
            ow_coeffs = self.models['obizhaeva_wang'].calculate_market_impact_coefficients(historical_data)
            calibration_results['obizhaeva_wang'] = {
                **ow_coeffs,
                'calibration_success': True,
                'method': calibration_method
            }
        except Exception as e:
            calibration_results['obizhaeva_wang'] = {
                'error': str(e),
                'calibration_success': False
            }
            
        # Almgren-Chriss model calibration
        try:
            # Simplified calibration for AC model
            ac_backtest = self.models['almgren_chriss'].backtest_execution_strategy(
                historical_data, 1000)  # Assuming 1000 shares
            calibration_results['almgren_chriss'] = {
                **ac_backtest,
                'calibration_success': True,
                'method': calibration_method
            }
        except Exception as e:
            calibration_results['almgren_chriss'] = {
                'error': str(e),
                'calibration_success': False
            }
            
        # Bertsimas-Lo model calibration
        try:
            bl_params = self.models['bertsimas_lo'].estimate_model_parameters(historical_data)
            calibration_results['bertsimas_lo'] = {
                **bl_params,
                'calibration_success': True,
                'method': calibration_method
            }
        except Exception as e:
            calibration_results['bertsimas_lo'] = {
                'error': str(e),
                'calibration_success': False
            }
            
        # Store calibration data
        self.calibration_data = {
            'historical_data': historical_data,
            'calibration_timestamp': datetime.now(),
            'method': calibration_method,
            'results': calibration_results
        }
        
        # Update model weights based on calibration success
        self._update_model_weights(calibration_results)
        
        return calibration_results
        
    def _update_model_weights(self, calibration_results: Dict[str, Dict]) -> None:
        """Update model weights based on calibration success"""
        total_score = 0
        scores = {}
        
        for model_name, result in calibration_results.items():
            if result.get('calibration_success', False):
                # Simple scoring based on available metrics
                if 'r_squared' in result:
                    score = result['r_squared']
                elif 'model_fit_r_squared' in result:
                    score = result['model_fit_r_squared']
                elif 'relative_error' in result:
                    score = max(0, 1 - abs(result['relative_error']))
                else:
                    score = 0.5  # Default neutral score
                    
                scores[model_name] = score
                total_score += score
            else:
                scores[model_name] = 0
                
        # Normalize weights
        if total_score > 0:
            self.model_weights = {name: score / total_score for name, score in scores.items()}
        else:
            # Equal weights if no successful calibrations
            self.model_weights = {name: 1.0 / len(scores) for name in scores.keys()}
            
    def calculate_ensemble_impact(self, trade_size: float,
                                trade_duration: float = 1.0,
                                market_conditions: Dict[str, Any] = None) -> Dict[str, float]:
        """
        Ensemble price impact calculation
        
        Args:
            trade_size: Size of the trade
            trade_duration: Duration of trade execution
            market_conditions: Current market conditions
            
        Returns:
            Ensemble impact calculation
        """
        if market_conditions is None:
            market_conditions = {
                'volatility': 0.02,
                'volume': 1000000,
                'liquidity': 0.5,
                'spread': 0.001
            }
            
        individual_impacts = {}
        total_weighted_impact = 0.0
        total_weight = 0.0
        
        # Kyle model
        if 'kyle' in self.models:
            try:
                kyle_impact = self.models['kyle'].calculate_price_impact(
                    trade_size, market_conditions.get('volume', 1.0))
                individual_impacts['kyle'] = kyle_impact
                total_weighted_impact += kyle_impact * self.model_weights.get('kyle', 0.25)
                total_weight += self.model_weights.get('kyle', 0.25)
            except Exception:
                individual_impacts['kyle'] = 0.0
                
        # Obizhaeva-Wang model
        if 'obizhaeva_wang' in self.models:
            try:
                ow_impact = self.models['obizhaeva_wang'].calculate_inventory_impact(
                    trade_size, 0, market_conditions.get('volatility', 0.02))
                individual_impacts['obizhaeva_wang'] = ow_impact
                total_weighted_impact += ow_impact * self.model_weights.get('obizhaeva_wang', 0.25)
                total_weight += self.model_weights.get('obizhaeva_wang', 0.25)
            except Exception:
                individual_impacts['obizhaeva_wang'] = 0.0
                
        # Almgren-Chriss model
        if 'almgren_chriss' in self.models:
            try:
                # Convert to temporary impact rate
                trade_rate = trade_size / trade_duration
                ac_impact = self.models['almgren_chriss'].calculate_temporary_impact(
                    trade_rate, trade_size)
                individual_impacts['almgren_chriss'] = ac_impact * trade_duration
                total_weighted_impact += ac_impact * trade_duration * self.model_weights.get('almgren_chriss', 0.25)
                total_weight += self.model_weights.get('almgren_chriss', 0.25)
            except Exception:
                individual_impacts['almgren_chriss'] = 0.0
                
        # Bertsimas-Lo model
        if 'bertsimas_lo' in self.models:
            try:
                bl_impact = self.models['bertsimas_lo'].calculate_information_impact(
                    trade_size / trade_duration, market_conditions)
                individual_impacts['bertsimas_lo'] = bl_impact
                total_weighted_impact += bl_impact * self.model_weights.get('bertsimas_lo', 0.25)
                total_weight += self.model_weights.get('bertsimas_lo', 0.25)
            except Exception:
                individual_impacts['bertsimas_lo'] = 0.0
                
        # Calculate ensemble impact
        ensemble_impact = total_weighted_impact / total_weight if total_weight > 0 else 0.0
        
        # Calculate confidence metrics
        impacts_list = list(individual_impacts.values())
        impact_std = np.std(impacts_list) if impacts_list else 0.0
        impact_range = max(impacts_list) - min(impacts_list) if impacts_list else 0.0
        
        return {
            'ensemble_impact': ensemble_impact,
            'individual_impacts': individual_impacts,
            'model_weights': self.model_weights,
            'impact_std': impact_std,
            'impact_range': impact_range,
            'confidence_score': max(0, 1 - impact_std / (abs(ensemble_impact) + 1e-6)),
            'consensus_strength': 1.0 / (1.0 + impact_range)
        }
        
    def forecast_impact_evolution(self, trade_schedule: List[Dict[str, float]],
                                forecast_horizon: int = 10) -> ImpactForecast:
        """
        Price impact evolution forecast
        
        Args:
            trade_schedule: Schedule of trades (size, time, etc.)
            forecast_horizon: Number of periods to forecast
            
        Returns:
            Impact forecast results
        """
        if not trade_schedule:
            raise ValueError("Trade schedule cannot be empty")
            
        predictions = []
        confidence_intervals = []
        model_contributions = {model: [] for model in self.models.keys()}
        
        for i in range(forecast_horizon):
            # Get current trade info
            current_trade = trade_schedule[min(i, len(trade_schedule) - 1)]
            trade_size = current_trade.get('size', 1000)
            trade_time = current_trade.get('time', i)
            
            # Calculate impact for each model
            period_impacts = {}
            for model_name, model in self.models.items():
                try:
                    if model_name == 'kyle':
                        impact = model.calculate_price_impact(trade_size)
                    elif model_name == 'obizhaeva_wang':
                        impact = model.calculate_inventory_impact(trade_size, 0, 0.02)
                    elif model_name == 'almgren_chriss':
                        impact = model.calculate_temporary_impact(trade_size / 1.0, trade_size)
                    elif model_name == 'bertsimas_lo':
                        impact = model.calculate_information_impact(trade_size, {'volatility': 0.02})
                    else:
                        impact = 0.0
                        
                    period_impacts[model_name] = impact
                    model_contributions[model_name].append(impact)
                    
                except Exception:
                    period_impacts[model_name] = 0.0
                    model_contributions[model_name].append(0.0)
                    
            # Calculate ensemble prediction
            weighted_impact = sum(
                impact * self.model_weights.get(model, 0.25) 
                for model, impact in period_impacts.items()
            )
            predictions.append(weighted_impact)
            
            # Calculate confidence interval
            impacts_list = list(period_impacts.values())
            if impacts_list:
                mean_impact = np.mean(impacts_list)
                std_impact = np.std(impacts_list)
                lower_bound = mean_impact - 1.96 * std_impact
                upper_bound = mean_impact + 1.96 * std_impact
                confidence_intervals.append((lower_bound, upper_bound))
            else:
                confidence_intervals.append((0.0, 0.0))
                
        return ImpactForecast(
            forecast_horizon=forecast_horizon,
            impact_predictions=predictions,
            confidence_intervals=confidence_intervals,
            model_contributions=model_contributions
        )
        
    def compare_models(self, test_data: pd.DataFrame) -> List[ModelComparison]:
        """
        Model performance comparison
        
        Args:
            test_data: Test data for model comparison
            
        Returns:
            Model comparison results
        """
        if len(test_data) < 50:
            raise ValueError("Insufficient test data (need at least 50 points)")
            
        comparisons = []
        
        for model_name, model in self.models.items():
            try:
                # Calculate model-specific metrics
                if model_name == 'kyle':
                    # Kyle model prediction
                    predictions = self.models['kyle'].lambda_param * test_data['volume']
                    actual = test_data['price'].pct_change().dropna()
                    predictions = predictions[:len(actual)]
                    
                elif model_name == 'obizhaeva_wang':
                    # OW model prediction (simplified)
                    predictions = (self.models['obizhaeva_wang'].alpha * test_data['volume'] + 
                                 self.models['obizhaeva_wang'].gamma * test_data.get('inventory', 0))
                    actual = test_data['price'].pct_change().dropna()
                    predictions = predictions[:len(actual)]
                    
                elif model_name == 'almgren_chriss':
                    # AC model prediction
                    trade_rates = test_data['volume'] / 100  # Assuming 100 time units
                    predictions = self.models['almgren_chriss'].gamma * trade_rates**2
                    actual = test_data['price'].pct_change().dropna()
                    predictions = predictions[:len(actual)]
                    
                elif model_name == 'bertsimas_lo':
                    # BL model prediction
                    signals = test_data.get('signals', np.random.normal(0, 1, len(test_data)))
                    predictions = self.models['bertsimas_lo'].kappa * signals
                    actual = test_data['price'].pct_change().dropna()
                    predictions = predictions[:len(actual)]
                    
                else:
                    continue
                    
                # Calculate metrics
                if len(predictions) > 0 and len(actual) > 0:
                    mae = np.mean(np.abs(predictions - actual))
                    mse = np.mean((predictions - actual) ** 2)
                    correlation = np.corrcoef(predictions, actual)[0, 1] if len(predictions) > 1 else 0
                    
                    # Price impact (using average absolute prediction)
                    price_impact = np.mean(np.abs(predictions))
                    
                    # Model fit score
                    model_fit = max(0, correlation) if not np.isnan(correlation) else 0
                    
                    # Confidence score
                    confidence_score = model_fit * (1 - mae / (np.std(actual) + 1e-6))
                    
                    comparisons.append(ModelComparison(
                        model_name=model_name,
                        price_impact=price_impact,
                        confidence_score=max(0, min(1, confidence_score)),
                        model_fit=model_fit,
                        parameters=asdict(self.models[model_name]) if hasattr(self.models[model_name], '__dict__') else {}
                    ))
                    
            except Exception as e:
                # Add failed model with zero scores
                comparisons.append(ModelComparison(
                    model_name=model_name,
                    price_impact=0.0,
                    confidence_score=0.0,
                    model_fit=0.0,
                    parameters={'error': str(e)}
                ))
                
        return comparisons
        
    def calculate_market_regime_impact(self, market_regime: str,
                                     trade_size: float,
                                     market_conditions: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Market regime ga bog'liq impact calculation
        
        Args:
            market_regime: 'normal', 'volatile', 'trending', 'crisis'
            trade_size: Trade size
            market_conditions: Market conditions
            
        Returns:
            Regime-specific impact analysis
        """
        # Regime adjustments
        regime_adjustments = {
            'normal': {'volatility_factor': 1.0, 'liquidity_factor': 1.0, 'impact_multiplier': 1.0},
            'volatile': {'volatility_factor': 2.0, 'liquidity_factor': 0.7, 'impact_multiplier': 1.5},
            'trending': {'volatility_factor': 1.2, 'liquidity_factor': 0.9, 'impact_multiplier': 1.2},
            'crisis': {'volatility_factor': 3.0, 'liquidity_factor': 0.3, 'impact_multiplier': 2.0}
        }
        
        adjustment = regime_adjustments.get(market_regime, regime_adjustments['normal'])
        
        if market_conditions is None:
            market_conditions = {'volatility': 0.02, 'liquidity': 0.5}
            
        # Adjust market conditions
        adjusted_conditions = market_conditions.copy()
        adjusted_conditions['volatility'] *= adjustment['volatility_factor']
        adjusted_conditions['liquidity'] *= adjustment['liquidity_factor']
        
        # Calculate base impact
        base_impact = self.calculate_ensemble_impact(trade_size, 1.0, adjusted_conditions)
        
        # Apply regime multiplier
        regime_impact = base_impact['ensemble_impact'] * adjustment['impact_multiplier']
        
        return {
            'market_regime': market_regime,
            'base_impact': base_impact['ensemble_impact'],
            'regime_impact': regime_impact,
            'impact_multiplier': adjustment['impact_multiplier'],
            'adjusted_conditions': adjusted_conditions,
            'regime_adjustments': adjustment,
            'ensemble_analysis': base_impact
        }
        
    def generate_comprehensive_report(self, analysis_type: str = 'full',
                                    data: pd.DataFrame = None) -> str:
        """
        Generate comprehensive market impact analysis report
        
        Args:
            analysis_type: 'full', 'model_comparison', 'calibration', 'forecast'
            data: Optional data for analysis
            
        Returns:
            Formatted analysis report
        """
        report = []
        report.append("=== MARKET IMPACT MODELING REPORT ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Model status
        report.append("MODEL STATUS:")
        for model_name, model in self.models.items():
            report.append(f"  {model_name}: Initialized")
        report.append("")
        
        # Model weights
        if self.model_weights:
            report.append("MODEL WEIGHTS:")
            for model, weight in self.model_weights.items():
                report.append(f"  {model}: {weight:.3f}")
            report.append("")
            
        # Calibration results
        if self.calibration_data:
            report.append("CALIBRATION RESULTS:")
            for model, result in self.calibration_data['results'].items():
                status = "Success" if result.get('calibration_success', False) else "Failed"
                report.append(f"  {model}: {status}")
            report.append("")
            
        # Analysis based on type
        if analysis_type == 'model_comparison' and data is not None:
            try:
                comparisons = self.compare_models(data)
                report.append("MODEL COMPARISON:")
                for comp in comparisons:
                    report.append(f"  {comp.model_name}:")
                    report.append(f"    Price Impact: {comp.price_impact:.6f}")
                    report.append(f"    Confidence: {comp.confidence_score:.3f}")
                    report.append(f"    Model Fit: {comp.model_fit:.3f}")
                report.append("")
            except Exception as e:
                report.append(f"Model comparison failed: {str(e)}")
                report.append("")
                
        elif analysis_type == 'ensemble_impact':
            # Sample ensemble impact calculation
            report.append("SAMPLE ENSEMBLE IMPACT:")
            sample_sizes = [1000, 5000, 10000]
            for size in sample_sizes:
                impact_result = self.calculate_ensemble_impact(size)
                report.append(f"  Trade Size {size:,}: Impact = {impact_result['ensemble_impact']:.6f}")
            report.append("")
            
        # Recent forecast (if available)
        if hasattr(self, 'forecast_cache') and self.forecast_cache:
            report.append("RECENT FORECAST:")
            forecast = self.forecast_cache.get('latest')
            if forecast:
                report.append(f"  Horizon: {forecast.forecast_horizon}")
                report.append(f"  Latest Prediction: {forecast.impact_predictions[-1]:.6f}")
                report.append("")
                
        return "\n".join(report)
        
    def get_system_statistics(self) -> Dict[str, Any]:
        """
        System statistics
        
        Returns:
            System statistics
        """
        return {
            'models_initialized': len(self.models),
            'model_names': list(self.models.keys()),
            'model_weights': self.model_weights,
            'calibrated': self.calibration_data is not None,
            'calibration_timestamp': self.calibration_data['calibration_timestamp'].isoformat() if self.calibration_data else None,
            'forecast_cache_size': len(self.forecast_cache),
            'system_status': 'operational' if len(self.models) > 0 else 'not_initialized'
        }