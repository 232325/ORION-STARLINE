"""
Economic Cycle Analysis Module

Ushbu modul iqtisodiy sikllar, indicator'lar va adaptation
tizimini integratsiya qilish uchun mo'ljallangan.

Imkoniyatlar:
- Integrated cycle analysis
- Comprehensive indicator dashboard
- Adaptation strategy analysis
- Performance attribution analysis
- Risk-adjusted returns analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

from ..core.cycle_detector import CycleDetector
from ..core.indicators import EconomicIndicators
from ..core.adaptation_engine import AdaptationEngine
from ..core.learning_system import ComprehensiveLearningSystem

class EconomicCycleAnalyzer:
    """
    Comprehensive Economic Cycle Analysis Class
    """
    
    def __init__(self, 
                 enable_learning: bool = True,
                 adaptation_sensitivity: float = 0.1):
        """
        Economic Cycle Analyzer initialize qilish
        
        Args:
            enable_learning: Self-learning tizimini yoqish
            adaptation_sensitivity: Adaptation sezgirligi
        """
        
        # Initialize core components
        self.cycle_detector = CycleDetector()
        self.indicators = EconomicIndicators()
        self.adaptation_engine = AdaptationEngine(
            adaptation_sensitivity=adaptation_sensitivity
        )
        
        self.learning_enabled = enable_learning
        if enable_learning:
            self.learning_system = ComprehensiveLearningSystem()
        
        # Analysis results storage
        self.analysis_history = []
        self.current_analysis = {}
        
        # Configuration
        self.analysis_config = {
            'auto_adaptation': True,
            'learning_frequency': 'monthly',
            'performance_attribution': True,
            'risk_analysis': True
        }
    
    def perform_comprehensive_analysis(self, 
                                     data: Dict[str, pd.DataFrame],
                                     strategy_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensive economic cycle analysis
        
        Args:
            data: Economic, performance, va market ma'lumotlari
            strategy_config: Strategy konfiguratsiyasi
            
        Returns:
            dict: Comprehensive analysis results
        """
        
        try:
            # Extract data components
            economic_data = data.get('economic', pd.DataFrame())
            performance_data = data.get('performance', pd.DataFrame())
            market_data = data.get('market', pd.DataFrame())
            
            # 1. Economic Cycle Detection
            cycle_analysis = self._analyze_economic_cycles(economic_data)
            
            # 2. Economic Indicators Analysis
            indicator_analysis = self._analyze_economic_indicators(economic_data)
            
            # 3. Adaptation Analysis
            adaptation_analysis = self._analyze_adaptation_requirements(
                cycle_analysis, indicator_analysis, strategy_config
            )
            
            # 4. Performance Attribution Analysis
            if not performance_data.empty:
                performance_analysis = self._perform_performance_attribution(
                    cycle_analysis, indicator_analysis, performance_data
                )
            else:
                performance_analysis = {'error': 'No performance data available'}
            
            # 5. Risk Analysis
            risk_analysis = self._perform_risk_analysis(
                cycle_analysis, adaptation_analysis, performance_data
            )
            
            # 6. Learning and Knowledge Integration
            if self.learning_enabled:
                learning_analysis = self._perform_learning_integration(
                    cycle_analysis, indicator_analysis, performance_data, market_data
                )
            else:
                learning_analysis = {'learning_disabled': True}
            
            # 7. Integrated Dashboard
            integrated_dashboard = self._create_integrated_dashboard(
                cycle_analysis, indicator_analysis, adaptation_analysis,
                performance_analysis, risk_analysis, learning_analysis
            )
            
            # 8. Strategic Recommendations
            strategic_recommendations = self._generate_strategic_recommendations(
                integrated_dashboard, strategy_config
            )
            
            comprehensive_results = {
                'timestamp': pd.Timestamp.now(),
                'cycle_analysis': cycle_analysis,
                'indicator_analysis': indicator_analysis,
                'adaptation_analysis': adaptation_analysis,
                'performance_analysis': performance_analysis,
                'risk_analysis': risk_analysis,
                'learning_analysis': learning_analysis,
                'integrated_dashboard': integrated_dashboard,
                'strategic_recommendations': strategic_recommendations,
                'analysis_confidence': self._calculate_analysis_confidence(
                    cycle_analysis, indicator_analysis, learning_analysis
                ),
                'data_quality_assessment': self._assess_data_quality(data)
            }
            
            # Store analysis results
            self.current_analysis = comprehensive_results
            self.analysis_history.append(comprehensive_results)
            
            return comprehensive_results
            
        except Exception as e:
            return {'error': f'Comprehensive analysis failed: {str(e)}'}
    
    def _analyze_economic_cycles(self, economic_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Economic cycles analysis
        """
        
        if economic_data.empty:
            return {'error': 'No economic data available'}
        
        # Select primary economic indicator for cycle detection
        primary_indicators = ['gdp', 'gdp_growth', 'industrial_production', 'economic_activity_index']
        
        primary_indicator = None
        for indicator in primary_indicators:
            if indicator in economic_data.columns:
                primary_indicator = indicator
                break
        
        if primary_indicator is None:
            # Use first numeric column
            numeric_cols = economic_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                primary_indicator = numeric_cols[0]
            else:
                return {'error': 'No suitable economic indicator found'}
        
        # Perform cycle detection
        cycle_results = self.cycle_detector.detect_business_cycle(
            economic_data, 
            target_column=primary_indicator
        )
        
        # Generate cycle forecast
        cycle_forecast = self.cycle_detector.get_cycle_forecast(
            economic_data, 
            forecast_periods=12
        )
        
        # Multi-cycle analysis
        multi_cycle_analysis = {}
        
        # Analyze multiple economic indicators for different cycle types
        for col in economic_data.select_dtypes(include=[np.number]).columns[:5]:  # Limit to top 5 indicators
            if col != primary_indicator:
                try:
                    cycle_data = self.cycle_detector._apply_hamilton_filter(economic_data[col])
                    multi_cycle_analysis[col] = {
                        'cycle_strength': self.cycle_detector._calculate_cycle_strength(cycle_data),
                        'cycle_phase': self.cycle_detector._identify_cycle_phases(cycle_data),
                        'trend_analysis': self.cycle_detector._analyze_trend(cycle_data) if hasattr(self.cycle_detector, '_analyze_trend') else 'not_available'
                    }
                except:
                    continue
        
        return {
            'primary_cycle_analysis': cycle_results,
            'cycle_forecast': cycle_forecast,
            'multi_cycle_analysis': multi_cycle_analysis,
            'cycle_regime_classification': self._classify_cycle_regime(cycle_results, multi_cycle_analysis),
            'cycle_synchronization': self._analyze_cycle_synchronization(multi_cycle_analysis)
        }
    
    def _classify_cycle_regime(self, primary_analysis: Dict, multi_analysis: Dict) -> Dict[str, Any]:
        """
        Economic cycle regime classification
        """
        
        # Extract cycle phases from different indicators
        phases = []
        
        if 'current_phase' in primary_analysis:
            phases.append(primary_analysis['current_phase'])
        
        for indicator, analysis in multi_analysis.items():
            if 'cycle_phase' in analysis and 'current_phase' in analysis['cycle_phase']:
                phases.append(analysis['cycle_phase']['current_phase'])
        
        # Regime classification
        if len(phases) == 0:
            regime = 'unknown'
        elif all(phase in ['expansion', 'peak'] for phase in phases):
            regime = 'expansion_regime'
        elif all(phase in ['contraction', 'trough'] for phase in phases):
            regime = 'contraction_regime'
        elif phases.count('expansion') > phases.count('contraction'):
            regime = 'mixed_expansion_regime'
        elif phases.count('contraction') > phases.count('expansion'):
            regime = 'mixed_contraction_regime'
        else:
            regime = 'transition_regime'
        
        return {
            'regime': regime,
            'phase_distribution': phases,
            'regime_confidence': len(phases) / max(len(phases), 1),
            'regime_stability': self._assess_regime_stability(phases)
        }
    
    def _assess_regime_stability(self, phases: List[str]) -> str:
        """
        Regime stability assessment
        """
        
        if len(phases) < 2:
            return 'insufficient_data'
        
        unique_phases = len(set(phases))
        
        if unique_phases == 1:
            return 'very_stable'
        elif unique_phases == 2:
            return 'stable'
        elif unique_phases == 3:
            return 'moderately_stable'
        else:
            return 'unstable'
    
    def _analyze_cycle_synchronization(self, multi_analysis: Dict) -> Dict[str, Any]:
        """
        Cycle synchronization analysis
        """
        
        if not multi_analysis:
            return {'synchronization': 'no_data'}
        
        # Calculate synchronization metrics
        cycle_strengths = []
        phases = []
        
        for indicator, analysis in multi_analysis.items():
            if 'cycle_strength' in analysis:
                cycle_strengths.append(analysis['cycle_strength'])
            if 'cycle_phase' in analysis and 'current_phase' in analysis['cycle_phase']:
                phases.append(analysis['cycle_phase']['current_phase'])
        
        # Synchronization score
        if cycle_strengths:
            avg_strength = np.mean(cycle_strengths)
            strength_variance = np.var(cycle_strengths)
            synchronization_score = 1.0 / (1.0 + strength_variance)
        else:
            synchronization_score = 0
        
        return {
            'synchronization_score': synchronization_score,
            'cycle_strength_distribution': cycle_strengths,
            'phase_alignment': phases,
            'synchronization_level': (
                'high' if synchronization_score > 0.8 else
                'medium' if synchronization_score > 0.5 else
                'low'
            )
        }
    
    def _analyze_economic_indicators(self, economic_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Economic indicators comprehensive analysis
        """
        
        if economic_data.empty:
            return {'error': 'No economic data available'}
        
        # Perform comprehensive indicators analysis
        indicator_results = self.indicators.analyze_indicators(economic_data)
        
        # Additional indicator-specific analysis
        leading_indicators_analysis = self._analyze_leading_indicators(economic_data)
        
        # Composite indicator construction
        composite_analysis = self._construct_composite_indicators(economic_data)
        
        # Indicator momentum analysis
        momentum_analysis = self._analyze_indicator_momentum(economic_data)
        
        return {
            'comprehensive_indicators': indicator_results,
            'leading_indicators': leading_indicators_analysis,
            'composite_indicators': composite_analysis,
            'momentum_analysis': momentum_analysis,
            'indicator_relationships': self._analyze_indicator_relationships(economic_data),
            'economic_dashboard_score': self._calculate_economic_dashboard_score(indicator_results)
        }
    
    def _analyze_leading_indicators(self, economic_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Leading indicators specific analysis
        """
        
        # Common leading indicators
        leading_indicator_cols = [
            'consumer_sentiment', 'business_investment', 'employment_initial',
            'credit_conditions', 'stock_market', 'housing_starts'
        ]
        
        available_leading = [col for col in leading_indicator_cols if col in economic_data.columns]
        
        if not available_leading:
            return {'error': 'No leading indicators available'}
        
        leading_analysis = {}
        
        for indicator in available_leading:
            series = economic_data[indicator].dropna()
            
            if len(series) < 6:
                continue
            
            # Leading indicator characteristics
            momentum = series.tail(6).mean() - series.head(6).mean()
            volatility = series.rolling(6).std().iloc[-1]
            
            leading_analysis[indicator] = {
                'momentum': momentum,
                'current_level': series.iloc[-1],
                'volatility': volatility,
                'signal_strength': abs(momentum) / (volatility + 0.01),
                'leading_score': self._calculate_leading_score(series, indicator)
            }
        
        # Composite leading score
        if leading_analysis:
            composite_score = np.mean([data['leading_score'] for data in leading_analysis.values()])
        else:
            composite_score = 0
        
        return {
            'individual_leading_indicators': leading_analysis,
            'composite_leading_score': composite_score,
            'leading_signals_strength': self._assess_leading_signals_strength(leading_analysis)
        }
    
    def _calculate_leading_score(self, series: pd.Series, indicator_name: str) -> float:
        """
        Leading indicator score calculation
        """
        
        # Simplified leading score based on recent momentum and stability
        if len(series) < 12:
            return 0.5
        
        recent_momentum = series.tail(6).mean() - series.head(6).mean()
        historical_volatility = series.std()
        
        # Score based on momentum relative to volatility
        momentum_score = abs(recent_momentum) / (historical_volatility + 0.01)
        
        # Normalize to [0, 1] range
        normalized_score = min(momentum_score / 2, 1.0)
        
        return normalized_score
    
    def _assess_leading_signals_strength(self, leading_analysis: Dict) -> str:
        """
        Leading signals strength assessment
        """
        
        if not leading_analysis:
            return 'no_signals'
        
        signal_strengths = [data['signal_strength'] for data in leading_analysis.values()]
        avg_strength = np.mean(signal_strengths)
        
        if avg_strength > 2.0:
            return 'very_strong'
        elif avg_strength > 1.5:
            return 'strong'
        elif avg_strength > 1.0:
            return 'moderate'
        elif avg_strength > 0.5:
            return 'weak'
        else:
            return 'very_weak'
    
    def _construct_composite_indicators(self, economic_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Composite indicator construction
        """
        
        composite_indicators = {}
        
        # Leading Composite Index
        leading_cols = [col for col in ['consumer_sentiment', 'business_investment'] 
                       if col in economic_data.columns]
        
        if leading_cols:
            leading_data = economic_data[leading_cols]
            composite_indicators['leading_composite'] = self._create_weighted_composite(
                leading_data, {'consumer_sentiment': 0.6, 'business_investment': 0.4}
            )
        
        # Growth Composite Index
        growth_cols = [col for col in ['gdp_growth', 'industrial_production_growth'] 
                      if col in economic_data.columns]
        
        if growth_cols:
            growth_data = economic_data[growth_cols]
            composite_indicators['growth_composite'] = self._create_weighted_composite(
                growth_data, {'gdp_growth': 0.7, 'industrial_production_growth': 0.3}
            )
        
        # Inflation Composite Index
        inflation_cols = [col for col in ['cpi', 'core_cpi', 'ppi'] 
                         if col in economic_data.columns]
        
        if inflation_cols:
            inflation_data = economic_data[inflation_cols]
            composite_indicators['inflation_composite'] = self._create_weighted_composite(
                inflation_data, {'cpi': 0.6, 'core_cpi': 0.3, 'ppi': 0.1}
            )
        
        return {
            'composite_indicators': composite_indicators,
            'composite_analysis': self._analyze_composite_performance(composite_indicators)
        }
    
    def _create_weighted_composite(self, data: pd.DataFrame, weights: Dict[str, float]) -> pd.Series:
        """
        Weighted composite indicator creation
        """
        
        if data.empty:
            return pd.Series()
        
        # Normalize data
        normalized_data = data.apply(lambda x: (x - x.mean()) / (x.std() + 0.01))
        
        # Apply weights
        composite = pd.Series(0, index=data.index)
        
        for column in normalized_data.columns:
            weight = weights.get(column, 1.0 / len(normalized_data.columns))
            composite += normalized_data[column] * weight
        
        return composite
    
    def _analyze_composite_performance(self, composites: Dict[str, pd.Series]) -> Dict[str, Any]:
        """
        Composite indicator performance analysis
        """
        
        performance_analysis = {}
        
        for name, composite in composites.items():
            if composite.empty:
                continue
            
            performance_analysis[name] = {
                'current_level': composite.iloc[-1],
                'momentum': composite.tail(6).mean() - composite.head(6).mean(),
                'volatility': composite.std(),
                'trend_strength': abs(composite.diff().mean()) / composite.std(),
                'percentile_rank': stats.percentileofscore(composite.dropna(), composite.iloc[-1])
            }
        
        return performance_analysis
    
    def _analyze_indicator_momentum(self, economic_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Indicator momentum analysis
        """
        
        momentum_analysis = {}
        
        for column in economic_data.select_dtypes(include=[np.number]).columns:
            series = economic_data[column].dropna()
            
            if len(series) < 12:
                continue
            
            # Calculate different momentum periods
            momentum_3m = series.iloc[-1] - series.iloc[-4] if len(series) >= 4 else 0
            momentum_6m = series.iloc[-1] - series.iloc[-7] if len(series) >= 7 else 0
            momentum_12m = series.iloc[-1] - series.iloc[-13] if len(series) >= 13 else 0
            
            # Momentum classification
            if momentum_12m > 0 and momentum_6m > 0:
                momentum_direction = 'positive_accelerating'
            elif momentum_12m > 0 and momentum_6m < 0:
                momentum_direction = 'positive_decelerating'
            elif momentum_12m < 0 and momentum_6m < 0:
                momentum_direction = 'negative_accelerating'
            elif momentum_12m < 0 and momentum_6m > 0:
                momentum_direction = 'negative_decelerating'
            else:
                momentum_direction = 'neutral'
            
            momentum_analysis[column] = {
                'momentum_3m': momentum_3m,
                'momentum_6m': momentum_6m,
                'momentum_12m': momentum_12m,
                'momentum_direction': momentum_direction,
                'momentum_strength': abs(momentum_6m) / (series.std() + 0.01)
            }
        
        return momentum_analysis
    
    def _analyze_indicator_relationships(self, economic_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Indicator relationships analysis
        """
        
        numeric_data = economic_data.select_dtypes(include=[np.number])
        
        if numeric_data.empty or len(numeric_data.columns) < 2:
            return {'error': 'Insufficient data for relationship analysis'}
        
        # Correlation analysis
        correlation_matrix = numeric_data.corr()
        
        # Identify strong relationships
        strong_relationships = []
        for i, col1 in enumerate(correlation_matrix.columns):
            for j, col2 in enumerate(correlation_matrix.columns):
                if i < j:  # Avoid duplicates
                    corr = correlation_matrix.loc[col1, col2]
                    if abs(corr) > 0.7:
                        strong_relationships.append({
                            'indicator1': col1,
                            'indicator2': col2,
                            'correlation': corr,
                            'relationship_type': 'positive' if corr > 0 else 'negative',
                            'strength': 'very_strong' if abs(corr) > 0.9 else 'strong'
                        })
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_relationships': strong_relationships,
            'relationship_summary': {
                'total_strong_relationships': len(strong_relationships),
                'positive_relationships': len([r for r in strong_relationships if r['relationship_type'] == 'positive']),
                'negative_relationships': len([r for r in strong_relationships if r['relationship_type'] == 'negative'])
            }
        }
    
    def _calculate_economic_dashboard_score(self, indicator_results: Dict) -> Dict[str, Any]:
        """
        Economic dashboard score calculation
        """
        
        if 'composite_dashboard_score' in indicator_results:
            dashboard_score = indicator_results['composite_dashboard_score']
            return dashboard_score
        else:
            return {'error': 'Dashboard score not available from indicator analysis'}
    
    def _analyze_adaptation_requirements(self, 
                                       cycle_analysis: Dict,
                                       indicator_analysis: Dict,
                                       strategy_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Adaptation requirements analysis
        """
        
        # Prepare combined economic data for adaptation analysis
        combined_data = self._prepare_combined_economic_data(cycle_analysis, indicator_analysis)
        
        if combined_data.empty:
            return {'error': 'Insufficient data for adaptation analysis'}
        
        # Perform adaptation analysis
        adaptation_results = self.adaptation_engine.adapt_to_economic_cycles(
            economic_data=combined_data,
            strategy_config=strategy_config or {},
            current_positions={}
        )
        
        # Additional adaptation analysis
        adaptation_effectiveness = self._assess_adaptation_effectiveness(adaptation_results)
        
        # Adaptation timing analysis
        adaptation_timing = self._analyze_adaptation_timing(adaptation_results)
        
        return {
            'adaptation_engine_results': adaptation_results,
            'adaptation_effectiveness': adaptation_effectiveness,
            'adaptation_timing': adaptation_timing,
            'adaptation_priority_ranking': self._prioritize_adaptations(adaptation_results)
        }
    
    def _prepare_combined_economic_data(self, 
                                      cycle_analysis: Dict,
                                      indicator_analysis: Dict) -> pd.DataFrame:
        """
        Prepare combined economic data for adaptation analysis
        """
        
        # This is a simplified version - in practice would combine real data
        combined_data = pd.DataFrame()
        
        # Add simulated data based on cycle analysis
        if 'primary_cycle_analysis' in cycle_analysis:
            # Create synthetic data based on cycle detection results
            dates = pd.date_range(start='2020-01-01', periods=36, freq='M')
            
            # Simulate economic indicators based on cycle phase
            cycle_phase = cycle_analysis['primary_cycle_analysis'].get('current_phase', 'unknown')
            
            if cycle_phase == 'expansion':
                combined_data['gdp_growth'] = np.random.normal(0.03, 0.01, 36)
                combined_data['inflation'] = np.random.normal(0.02, 0.005, 36)
                combined_data['unemployment'] = np.random.normal(0.05, 0.01, 36)
            elif cycle_phase == 'contraction':
                combined_data['gdp_growth'] = np.random.normal(-0.01, 0.02, 36)
                combined_data['inflation'] = np.random.normal(0.015, 0.01, 36)
                combined_data['unemployment'] = np.random.normal(0.08, 0.02, 36)
            else:
                combined_data['gdp_growth'] = np.random.normal(0.015, 0.015, 36)
                combined_data['inflation'] = np.random.normal(0.02, 0.008, 36)
                combined_data['unemployment'] = np.random.normal(0.06, 0.015, 36)
            
            combined_data.index = dates
        
        return combined_data
    
    def _assess_adaptation_effectiveness(self, adaptation_results: Dict) -> Dict[str, Any]:
        """
        Adaptation effectiveness assessment
        """
        
        if 'error' in adaptation_results:
            return {'error': adaptation_results['error']}
        
        effectiveness_score = 0
        assessment_components = {}
        
        # Assess cycle detection quality
        if 'cycle_detection' in adaptation_results:
            cycle_detection = adaptation_results['cycle_detection']
            cycle_score = len([cycle for cycle in cycle_detection.keys() if cycle_detection[cycle].get('cycle') != 'insufficient_data'])
            assessment_components['cycle_detection_quality'] = cycle_score / max(len(cycle_detection), 1)
            effectiveness_score += assessment_components['cycle_detection_quality'] * 0.3
        
        # Assess adaptation recommendations quality
        if 'recommendations' in adaptation_results:
            recommendations = adaptation_results['recommendations']
            param_adjustments = recommendations.get('parameter_adjustments', {})
            if param_adjustments:
                assessment_components['parameter_recommendations'] = len(param_adjustments) / 4  # Max 4 parameters
                effectiveness_score += assessment_components['parameter_recommendations'] * 0.4
        
        # Assess implementation guidance
        if 'implementation_priority' in adaptation_results:
            implementation = adaptation_results['implementation_priority']
            priority_count = sum(len(actions) for actions in implementation.values())
            assessment_components['implementation_guidance'] = min(priority_count / 5, 1)  # Max 5 actions
            effectiveness_score += assessment_components['implementation_guidance'] * 0.3
        
        return {
            'overall_effectiveness_score': effectiveness_score,
            'effectiveness_components': assessment_components,
            'effectiveness_rating': (
                'excellent' if effectiveness_score > 0.8 else
                'good' if effectiveness_score > 0.6 else
                'fair' if effectiveness_score > 0.4 else
                'poor'
            )
        }
    
    def _analyze_adaptation_timing(self, adaptation_results: Dict) -> Dict[str, Any]:
        """
        Adaptation timing analysis
        """
        
        if 'error' in adaptation_results:
            return {'error': adaptation_results['error']}
        
        timing_analysis = {
            'immediate_actions': [],
            'short_term_actions': [],
            'long_term_actions': []
        }
        
        # Categorize actions by timing
        if 'implementation_priority' in adaptation_results:
            priorities = adaptation_results['implementation_priority']
            
            for category, actions in priorities.items():
                if category == 'high_priority':
                    timing_analysis['immediate_actions'].extend(actions)
                elif category == 'medium_priority':
                    timing_analysis['short_term_actions'].extend(actions)
                else:
                    timing_analysis['long_term_actions'].extend(actions)
        
        # Timing urgency assessment
        urgency_score = len(timing_analysis['immediate_actions']) * 3 + \
                       len(timing_analysis['short_term_actions']) * 2 + \
                       len(timing_analysis['long_term_actions']) * 1
        
        return {
            'timing_breakdown': timing_analysis,
            'urgency_score': urgency_score,
            'timing_urgency': (
                'critical' if urgency_score > 10 else
                'high' if urgency_score > 5 else
                'moderate' if urgency_score > 2 else
                'low'
            ),
            'recommended_implementation_schedule': self._create_implementation_schedule(timing_analysis)
        }
    
    def _create_implementation_schedule(self, timing_analysis: Dict) -> Dict[str, str]:
        """
        Create implementation schedule
        """
        
        schedule = {}
        
        if timing_analysis['immediate_actions']:
            schedule['immediate'] = 'Execute within 1-3 days'
        
        if timing_analysis['short_term_actions']:
            schedule['short_term'] = 'Execute within 1-4 weeks'
        
        if timing_analysis['long_term_actions']:
            schedule['long_term'] = 'Execute within 1-6 months'
        
        return schedule
    
    def _prioritize_adaptations(self, adaptation_results: Dict) -> Dict[str, Any]:
        """
        Adaptation prioritization
        """
        
        if 'error' in adaptation_results:
            return {'error': adaptation_results['error']}
        
        priorities = {}
        
        # Extract and rank adaptations
        all_adaptations = []
        
        if 'implementation_priority' in adaptation_results:
            for category, actions in adaptation_results['implementation_priority'].items():
                for action in actions:
                    all_adaptations.append({
                        'action': action,
                        'category': category,
                        'priority_level': category.replace('_priority', '')
                    })
        
        # Sort by priority level
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        all_adaptations.sort(key=lambda x: priority_order.get(x['priority_level'], 0), reverse=True)
        
        priorities['ranked_adaptations'] = all_adaptations[:10]  # Top 10
        priorities['total_adaptations'] = len(all_adaptations)
        priorities['high_priority_count'] = len([a for a in all_adaptations if a['priority_level'] == 'high'])
        
        return priorities
    
    def _perform_performance_attribution(self, 
                                       cycle_analysis: Dict,
                                       indicator_analysis: Dict,
                                       performance_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Performance attribution analysis
        """
        
        if performance_data.empty:
            return {'error': 'No performance data available'}
        
        # Cycle-based attribution
        cycle_attribution = self._attribute_performance_to_cycles(cycle_analysis, performance_data)
        
        # Indicator-based attribution
        indicator_attribution = self._attribute_performance_to_indicators(indicator_analysis, performance_data)
        
        # Risk-adjusted returns analysis
        risk_adjusted_returns = self._calculate_risk_adjusted_returns(performance_data)
        
        return {
            'cycle_attribution': cycle_attribution,
            'indicator_attribution': indicator_attribution,
            'risk_adjusted_returns': risk_adjusted_returns,
            'performance_summary': self._create_performance_summary(
                cycle_attribution, indicator_attribution, risk_adjusted_returns
            )
        }
    
    def _attribute_performance_to_cycles(self, cycle_analysis: Dict, performance_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Attribute performance to economic cycles
        """
        
        if 'primary_cycle_analysis' not in cycle_analysis:
            return {'error': 'No cycle analysis available'}
        
        cycle_data = cycle_analysis['primary_cycle_analysis']
        cycle_phase = cycle_data.get('current_phase', 'unknown')
        
        # Calculate performance by cycle phase
        performance_by_phase = {}
        
        if not performance_data.empty:
            for column in performance_data.select_dtypes(include=[np.number]).columns:
                series = performance_data[column].dropna()
                
                if len(series) < 12:
                    continue
                
                # Calculate performance metrics
                total_return = (series.iloc[-1] / series.iloc[0] - 1) if series.iloc[0] != 0 else 0
                annualized_return = ((series.iloc[-1] / series.iloc[0]) ** (12 / len(series)) - 1) if len(series) > 1 else 0
                volatility = series.pct_change().std() * np.sqrt(12)
                
                performance_by_phase[column] = {
                    'total_return': total_return,
                    'annualized_return': annualized_return,
                    'volatility': volatility,
                    'cycle_phase': cycle_phase,
                    'performance_rating': self._rate_performance(annualized_return, volatility)
                }
        
        return {
            'current_cycle_phase': cycle_phase,
            'performance_by_phase': performance_by_phase,
            'cycle_performance_summary': self._summarize_cycle_performance(performance_by_phase)
        }
    
    def _rate_performance(self, returns: float, volatility: float) -> str:
        """
        Performance rating
        """
        
        if returns > 0.15 and volatility < 0.2:
            return 'excellent'
        elif returns > 0.1 and volatility < 0.25:
            return 'good'
        elif returns > 0.05 and volatility < 0.3:
            return 'fair'
        elif returns > 0:
            return 'poor'
        else:
            return 'very_poor'
    
    def _summarize_cycle_performance(self, performance_by_phase: Dict) -> Dict[str, Any]:
        """
        Cycle performance summary
        """
        
        if not performance_by_phase:
            return {'summary': 'No performance data available'}
        
        returns = [data['annualized_return'] for data in performance_by_phase.values()]
        volatilities = [data['volatility'] for data in performance_by_phase.values()]
        
        summary = {
            'average_return': np.mean(returns),
            'average_volatility': np.mean(volatilities),
            'return_volatility_ratio': np.mean(returns) / (np.mean(volatilities) + 0.01),
            'performance_consistency': 1 - (np.std(returns) / (np.mean(returns) + 0.01)),
            'overall_rating': self._rate_performance(np.mean(returns), np.mean(volatilities))
        }
        
        return summary
    
    def _attribute_performance_to_indicators(self, indicator_analysis: Dict, performance_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Attribute performance to economic indicators
        """
        
        if 'comprehensive_indicators' not in indicator_analysis:
            return {'error': 'No indicator analysis available'}
        
        indicator_data = indicator_analysis['comprehensive_indicators']
        
        # Extract individual indicator scores
        if 'individual_indicators' in indicator_data:
            indicators = indicator_data['individual_indicators']
            
            attribution_by_indicator = {}
            
            for indicator_name, indicator_info in indicators.items():
                if 'leading_score' in indicator_info:
                    leading_score = indicator_info['leading_score']
                    score_value = leading_score.get('score', 0)
                    
                    attribution_by_indicator[indicator_name] = {
                        'indicator_score': score_value,
                        'score_type': leading_score.get('type', 'unknown'),
                        'contribution_potential': score_value * 0.1  # Simplified contribution
                    }
            
            return {
                'indicator_attribution': attribution_by_indicator,
                'top_performing_indicators': self._identify_top_indicators(attribution_by_indicator),
                'indicator_contribution_summary': self._summarize_indicator_contributions(attribution_by_indicator)
            }
        
        return {'error': 'Insufficient indicator data for attribution'}
    
    def _identify_top_indicators(self, attribution: Dict) -> List[Dict]:
        """
        Identify top performing indicators
        """
        
        sorted_indicators = sorted(
            attribution.items(),
            key=lambda x: x[1]['indicator_score'],
            reverse=True
        )
        
        return [
            {
                'indicator': indicator,
                'score': data['indicator_score'],
                'type': data['score_type']
            }
            for indicator, data in sorted_indicators[:5]
        ]
    
    def _summarize_indicator_contributions(self, attribution: Dict) -> Dict[str, Any]:
        """
        Indicator contributions summary
        """
        
        if not attribution:
            return {'summary': 'No indicator attribution available'}
        
        scores = [data['indicator_score'] for data in attribution.values()]
        
        return {
            'average_indicator_score': np.mean(scores),
            'score_spread': np.max(scores) - np.min(scores),
            'leading_indicators_count': len([data for data in attribution.values() if data['score_type'] == 'leading']),
            'overall_indicator_strength': 'strong' if np.mean(scores) > 0.7 else 'moderate' if np.mean(scores) > 0.5 else 'weak'
        }
    
    def _calculate_risk_adjusted_returns(self, performance_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Risk-adjusted returns calculation
        """
        
        if performance_data.empty:
            return {'error': 'No performance data available'}
        
        risk_adjusted_metrics = {}
        
        for column in performance_data.select_dtypes(include=[np.number]).columns:
            series = performance_data[column].dropna()
            
            if len(series) < 12:
                continue
            
            returns = series.pct_change().dropna()
            
            # Calculate risk-adjusted metrics
            annual_return = returns.mean() * 12
            annual_volatility = returns.std() * np.sqrt(12)
            
            sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
            sortino_ratio = annual_return / returns[returns < 0].std() * np.sqrt(12) if len(returns[returns < 0]) > 0 else float('inf')
            
            # Maximum drawdown
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            risk_adjusted_metrics[column] = {
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_drawdown': max_drawdown,
                'annual_return': annual_return,
                'annual_volatility': annual_volatility,
                'risk_adjusted_rating': self._rate_risk_adjusted_performance(sharpe_ratio, max_drawdown)
            }
        
        return {
            'risk_adjusted_metrics': risk_adjusted_metrics,
            'portfolio_risk_summary': self._create_portfolio_risk_summary(risk_adjusted_metrics)
        }
    
    def _rate_risk_adjusted_performance(self, sharpe_ratio: float, max_drawdown: float) -> str:
        """
        Risk-adjusted performance rating
        """
        
        if sharpe_ratio > 1.5 and max_drawdown > -0.15:
            return 'excellent'
        elif sharpe_ratio > 1.0 and max_drawdown > -0.25:
            return 'good'
        elif sharpe_ratio > 0.5 and max_drawdown > -0.35:
            return 'fair'
        elif sharpe_ratio > 0:
            return 'poor'
        else:
            return 'very_poor'
    
    def _create_portfolio_risk_summary(self, risk_metrics: Dict) -> Dict[str, Any]:
        """
        Portfolio risk summary
        """
        
        if not risk_metrics:
            return {'summary': 'No risk metrics available'}
        
        sharpe_ratios = [data['sharpe_ratio'] for data in risk_metrics.values()]
        max_drawdowns = [data['max_drawdown'] for data in risk_metrics.values()]
        
        return {
            'average_sharpe_ratio': np.mean(sharpe_ratios),
            'average_max_drawdown': np.mean(max_drawdowns),
            'best_performing_asset': max(risk_metrics.items(), key=lambda x: x[1]['sharpe_ratio'])[0],
            'risk_consistency': 1 - (np.std(sharpe_ratios) / (np.mean(sharpe_ratios) + 0.01)),
            'overall_risk_rating': self._rate_overall_risk(np.mean(sharpe_ratios), np.mean(max_drawdowns))
        }
    
    def _rate_overall_risk(self, avg_sharpe: float, avg_drawdown: float) -> str:
        """
        Overall risk rating
        """
        
        if avg_sharpe > 1.2 and avg_drawdown > -0.2:
            return 'excellent'
        elif avg_sharpe > 0.8 and avg_drawdown > -0.3:
            return 'good'
        elif avg_sharpe > 0.4 and avg_drawdown > -0.4:
            return 'fair'
        else:
            return 'poor'
    
    def _create_performance_summary(self, 
                                  cycle_attribution: Dict,
                                  indicator_attribution: Dict,
                                  risk_adjusted_returns: Dict) -> Dict[str, Any]:
        """
        Overall performance summary
        """
        
        summary = {
            'performance_overview': {},
            'attribution_summary': {},
            'risk_summary': {}
        }
        
        # Performance overview
        if 'performance_summary' in cycle_attribution:
            cycle_summary = cycle_attribution['performance_summary']
            summary['performance_overview']['cycle_based'] = cycle_summary
        
        if 'risk_adjusted_metrics' in risk_adjusted_returns:
            # Take average across all metrics
            metrics = risk_adjusted_returns['risk_adjusted_metrics']
            avg_sharpe = np.mean([data['sharpe_ratio'] for data in metrics.values()])
            avg_return = np.mean([data['annual_return'] for data in metrics.values()])
            
            summary['performance_overview']['risk_adjusted'] = {
                'average_sharpe_ratio': avg_sharpe,
                'average_return': avg_return,
                'overall_rating': self._rate_overall_performance(avg_sharpe, avg_return)
            }
        
        return summary
    
    def _rate_overall_performance(self, sharpe_ratio: float, annual_return: float) -> str:
        """
        Overall performance rating
        """
        
        if sharpe_ratio > 1.3 and annual_return > 0.12:
            return 'excellent'
        elif sharpe_ratio > 0.8 and annual_return > 0.08:
            return 'good'
        elif sharpe_ratio > 0.4 and annual_return > 0.04:
            return 'fair'
        elif annual_return > 0:
            return 'poor'
        else:
            return 'very_poor'
    
    def _perform_risk_analysis(self, 
                             cycle_analysis: Dict,
                             adaptation_analysis: Dict,
                             performance_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive risk analysis
        """
        
        # Economic cycle risk
        cycle_risk = self._assess_economic_cycle_risk(cycle_analysis)
        
        # Adaptation risk
        adaptation_risk = self._assess_adaptation_risk(adaptation_analysis)
        
        # Market risk
        if not performance_data.empty:
            market_risk = self._assess_market_risk(performance_data)
        else:
            market_risk = {'error': 'No performance data available for market risk assessment'}
        
        # Portfolio risk
        portfolio_risk = self._assess_portfolio_risk(cycle_risk, adaptation_risk, market_risk)
        
        return {
            'economic_cycle_risk': cycle_risk,
            'adaptation_risk': adaptation_risk,
            'market_risk': market_risk,
            'portfolio_risk': portfolio_risk,
            'overall_risk_assessment': self._create_overall_risk_assessment(
                cycle_risk, adaptation_risk, market_risk
            )
        }
    
    def _assess_economic_cycle_risk(self, cycle_analysis: Dict) -> Dict[str, Any]:
        """
        Economic cycle risk assessment
        """
        
        if 'primary_cycle_analysis' not in cycle_analysis:
            return {'error': 'No cycle analysis available for risk assessment'}
        
        cycle_data = cycle_analysis['primary_cycle_analysis']
        cycle_phase = cycle_data.get('current_phase', 'unknown')
        
        # Risk mapping by cycle phase
        phase_risks = {
            'expansion': {'level': 'low', 'description': 'Low risk during expansion phase'},
            'peak': {'level': 'medium', 'description': 'Moderate risk at economic peak'},
            'contraction': {'level': 'high', 'description': 'High risk during contraction'},
            'trough': {'level': 'medium', 'description': 'Moderate risk at economic trough'},
            'transition': {'level': 'medium', 'description': 'Uncertain risk during transition'},
            'unknown': {'level': 'unknown', 'description': 'Risk level unknown'}
        }
        
        current_risk = phase_risks.get(cycle_phase, phase_risks['unknown'])
        
        # Additional risk factors
        shocks_count = cycle_data.get('shocks_detected', 0)
        
        return {
            'cycle_phase': cycle_phase,
            'risk_level': current_risk['level'],
            'risk_description': current_risk['description'],
            'shock_risk_factor': 'high' if shocks_count > 2 else 'medium' if shocks_count > 0 else 'low',
            'cycle_stability': cycle_data.get('cycle_strength', 0),
            'overall_cycle_risk_score': self._calculate_cycle_risk_score(current_risk['level'], shocks_count)
        }
    
    def _calculate_cycle_risk_score(self, risk_level: str, shocks_count: int) -> float:
        """
        Calculate cycle risk score
        """
        
        level_scores = {'low': 0.2, 'medium': 0.5, 'high': 0.8, 'unknown': 0.5}
        base_score = level_scores.get(risk_level, 0.5)
        
        # Add shock factor
        shock_adjustment = min(shocks_count * 0.1, 0.3)
        
        return min(base_score + shock_adjustment, 1.0)
    
    def _assess_adaptation_risk(self, adaptation_analysis: Dict) -> Dict[str, Any]:
        """
        Adaptation risk assessment
        """
        
        if 'adaptation_engine_results' not in adaptation_analysis:
            return {'error': 'No adaptation analysis available for risk assessment'}
        
        adaptation_results = adaptation_analysis['adaptation_engine_results']
        
        # Implementation risk assessment
        if 'risk_assessment' in adaptation_results:
            risk_assessment = adaptation_results['risk_assessment']
            
            overall_risk_level = risk_assessment.get('overall_risk_level', 'unknown')
            risk_mitigation = risk_assessment.get('risk_mitigation_recommendations', [])
            
            return {
                'adaptation_risk_level': overall_risk_level,
                'implementation_risk': risk_assessment.get('implementation_risk', {}),
                'timing_risk': risk_assessment.get('timing_risk', {}),
                'mitigation_recommendations': risk_mitigation,
                'adaptation_confidence': self._calculate_adaptation_confidence(risk_assessment)
            }
        
        return {'error': 'Insufficient adaptation data for risk assessment'}
    
    def _calculate_adaptation_confidence(self, risk_assessment: Dict) -> str:
        """
        Adaptation confidence calculation
        """
        
        overall_risk = risk_assessment.get('overall_risk_level', 'unknown')
        
        confidence_map = {
            'low': 'high',
            'medium': 'medium', 
            'high': 'low',
            'unknown': 'unknown'
        }
        
        return confidence_map.get(overall_risk, 'unknown')
    
    def _assess_market_risk(self, performance_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Market risk assessment
        """
        
        if performance_data.empty:
            return {'error': 'No performance data available'}
        
        market_risk_metrics = {}
        
        for column in performance_data.select_dtypes(include=[np.number]).columns:
            series = performance_data[column].dropna()
            
            if len(series) < 12:
                continue
            
            returns = series.pct_change().dropna()
            
            # Risk metrics
            volatility = returns.std() * np.sqrt(252)  # Annualized volatility
            var_95 = np.percentile(returns, 5)  # 5% VaR
            skewness = returns.skew()
            kurtosis = returns.kurtosis()
            
            # Tail risk assessment
            tail_risk = 'high' if kurtosis > 3 else 'medium' if kurtosis > 0 else 'low'
            
            market_risk_metrics[column] = {
                'volatility': volatility,
                'var_95': var_95,
                'skewness': skewness,
                'kurtosis': kurtosis,
                'tail_risk': tail_risk,
                'volatility_rating': self._rate_volatility(volatility)
            }
        
        return {
            'market_risk_metrics': market_risk_metrics,
            'market_risk_summary': self._create_market_risk_summary(market_risk_metrics)
        }
    
    def _rate_volatility(self, volatility: float) -> str:
        """
        Volatility rating
        """
        
        if volatility < 0.15:
            return 'low'
        elif volatility < 0.30:
            return 'moderate'
        elif volatility < 0.50:
            return 'high'
        else:
            return 'very_high'
    
    def _create_market_risk_summary(self, risk_metrics: Dict) -> Dict[str, Any]:
        """
        Market risk summary
        """
        
        if not risk_metrics:
            return {'summary': 'No market risk metrics available'}
        
        volatilities = [data['volatility'] for data in risk_metrics.values()]
        tail_risks = [data['tail_risk'] for data in risk_metrics.values()]
        
        high_tail_risk_count = len([risk for risk in tail_risks if risk == 'high'])
        
        return {
            'average_volatility': np.mean(volatilities),
            'volatility_range': (np.min(volatilities), np.max(volatilities)),
            'tail_risk_prevalence': high_tail_risk_count / len(tail_risks),
            'market_risk_rating': self._rate_market_risk(np.mean(volatilities), high_tail_risk_count / len(tail_risks))
        }
    
    def _rate_market_risk(self, avg_volatility: float, tail_risk_prevalence: float) -> str:
        """
        Market risk rating
        """
        
        if avg_volatility < 0.2 and tail_risk_prevalence < 0.3:
            return 'low'
        elif avg_volatility < 0.4 and tail_risk_prevalence < 0.6:
            return 'moderate'
        elif avg_volatility < 0.6:
            return 'high'
        else:
            return 'very_high'
    
    def _assess_portfolio_risk(self, 
                             cycle_risk: Dict,
                             adaptation_risk: Dict,
                             market_risk: Dict) -> Dict[str, Any]:
        """
        Portfolio risk assessment
        """
        
        # Risk consolidation
        risk_levels = []
        
        if 'risk_level' in cycle_risk:
            risk_levels.append(cycle_risk['risk_level'])
        
        if 'adaptation_risk_level' in adaptation_risk:
            risk_levels.append(adaptation_risk['adaptation_risk_level'])
        
        if 'market_risk_summary' in market_risk and 'market_risk_rating' in market_risk['market_risk_summary']:
            risk_levels.append(market_risk['market_risk_summary']['market_risk_rating'])
        
        # Portfolio risk calculation
        if risk_levels:
            # Convert to numeric for calculation
            risk_mapping = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4, 'unknown': 2.5}
            numeric_risks = [risk_mapping.get(risk, 2) for risk in risk_levels]
            portfolio_risk_score = np.mean(numeric_risks)
            
            # Map back to categorical
            if portfolio_risk_score < 1.5:
                portfolio_risk_level = 'low'
            elif portfolio_risk_score < 2.5:
                portfolio_risk_level = 'medium'
            elif portfolio_risk_score < 3.5:
                portfolio_risk_level = 'high'
            else:
                portfolio_risk_level = 'very_high'
        else:
            portfolio_risk_level = 'unknown'
            portfolio_risk_score = 2.5
        
        return {
            'portfolio_risk_level': portfolio_risk_level,
            'portfolio_risk_score': portfolio_risk_score,
            'risk_component_breakdown': {
                'cycle_risk': cycle_risk.get('risk_level', 'unknown'),
                'adaptation_risk': adaptation_risk.get('adaptation_risk_level', 'unknown'),
                'market_risk': market_risk.get('market_risk_summary', {}).get('market_risk_rating', 'unknown')
            },
            'portfolio_risk_recommendations': self._generate_portfolio_risk_recommendations(portfolio_risk_level)
        }
    
    def _generate_portfolio_risk_recommendations(self, risk_level: str) -> List[str]:
        """
        Portfolio risk recommendations
        """
        
        recommendations = []
        
        if risk_level == 'high' or risk_level == 'very_high':
            recommendations.extend([
                'Consider reducing position sizes',
                'Implement additional hedging strategies',
                'Increase monitoring frequency',
                'Review and strengthen risk management protocols'
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                'Maintain current risk levels with monitoring',
                'Prepare contingency plans',
                'Review portfolio diversification'
            ])
        else:  # low risk
            recommendations.extend([
                'Current risk levels are appropriate',
                'Continue current strategy',
                'Consider gradual position increases'
            ])
        
        return recommendations
    
    def _create_overall_risk_assessment(self, 
                                      cycle_risk: Dict,
                                      adaptation_risk: Dict,
                                      market_risk: Dict) -> Dict[str, Any]:
        """
        Overall risk assessment creation
        """
        
        # Combine all risk assessments
        all_risks = []
        
        if 'risk_level' in cycle_risk:
            all_risks.append({
                'risk_type': 'Economic Cycle Risk',
                'level': cycle_risk['risk_level'],
                'impact': 'high' if cycle_risk['risk_level'] in ['high', 'very_high'] else 'medium'
            })
        
        if 'adaptation_risk_level' in adaptation_risk:
            all_risks.append({
                'risk_type': 'Adaptation Risk',
                'level': adaptation_risk['adaptation_risk_level'],
                'impact': 'high' if adaptation_risk['adaptation_risk_level'] in ['high', 'very_high'] else 'medium'
            })
        
        if 'market_risk_summary' in market_risk and 'market_risk_rating' in market_risk['market_risk_summary']:
            market_level = market_risk['market_risk_summary']['market_risk_rating']
            all_risks.append({
                'risk_type': 'Market Risk',
                'level': market_level,
                'impact': 'high' if market_level in ['high', 'very_high'] else 'medium'
            })
        
        # Overall assessment
        high_impact_risks = len([risk for risk in all_risks if risk['impact'] == 'high'])
        
        overall_rating = (
            'critical' if high_impact_risks >= 2 else
            'high' if high_impact_risks == 1 else
            'moderate' if all_risks else
            'low'
        )
        
        return {
            'overall_risk_rating': overall_rating,
            'risk_breakdown': all_risks,
            'primary_concerns': [risk['risk_type'] for risk in all_risks if risk['impact'] == 'high'],
            'overall_recommendation': self._generate_overall_risk_recommendation(overall_rating, all_risks)
        }
    
    def _generate_overall_risk_recommendation(self, rating: str, risks: List[Dict]) -> str:
        """
        Overall risk recommendation
        """
        
        if rating == 'critical':
            return 'Immediate action required - implement comprehensive risk mitigation strategies'
        elif rating == 'high':
            return 'High priority risk management actions needed'
        elif rating == 'moderate':
            return 'Monitor risks closely and prepare mitigation strategies'
        else:
            return 'Current risk levels are manageable with standard monitoring'
    
    def _perform_learning_integration(self, 
                                    cycle_analysis: Dict,
                                    indicator_analysis: Dict,
                                    performance_data: pd.DataFrame,
                                    market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Learning system integration
        """
        
        if not self.learning_enabled:
            return {'learning_disabled': True}
        
        try:
            # Prepare data for learning system
            data_dict = {
                'economic': self._prepare_learning_data(cycle_analysis, indicator_analysis),
                'performance': performance_data,
                'market': market_data if market_data is not None else pd.DataFrame()
            }
            
            # Perform comprehensive learning
            learning_results = self.learning_system.learn_from_economic_data(**data_dict)
            
            # Learning insights extraction
            learning_insights = self._extract_learning_insights(learning_results)
            
            # Knowledge integration
            knowledge_integration = self._integrate_new_knowledge(learning_results)
            
            return {
                'learning_results': learning_results,
                'learning_insights': learning_insights,
                'knowledge_integration': knowledge_integration,
                'learning_effectiveness': learning_results.get('effectiveness_assessment', {}),
                'learning_status': self.learning_system.get_learning_status()
            }
            
        except Exception as e:
            return {'error': f'Learning integration failed: {str(e)}'}
    
    def _prepare_learning_data(self, cycle_analysis: Dict, indicator_analysis: Dict) -> pd.DataFrame:
        """
        Prepare data for learning system
        """
        
        # This is a simplified version - in practice would extract and format real data
        data = pd.DataFrame()
        
        # Add synthetic data based on analysis results
        dates = pd.date_range(start='2020-01-01', periods=36, freq='M')
        
        # Extract cycle phase for data generation
        cycle_phase = cycle_analysis.get('primary_cycle_analysis', {}).get('current_phase', 'unknown')
        
        if cycle_phase == 'expansion':
            data['gdp_growth'] = np.random.normal(0.025, 0.01, 36)
            data['inflation'] = np.random.normal(0.02, 0.005, 36)
            data['unemployment'] = np.random.normal(0.055, 0.01, 36)
        elif cycle_phase == 'contraction':
            data['gdp_growth'] = np.random.normal(-0.005, 0.015, 36)
            data['inflation'] = np.random.normal(0.018, 0.008, 36)
            data['unemployment'] = np.random.normal(0.075, 0.015, 36)
        else:
            data['gdp_growth'] = np.random.normal(0.015, 0.012, 36)
            data['inflation'] = np.random.normal(0.02, 0.006, 36)
            data['unemployment'] = np.random.normal(0.06, 0.012, 36)
        
        data.index = dates
        return data
    
    def _extract_learning_insights(self, learning_results: Dict) -> Dict[str, Any]:
        """
        Extract key learning insights
        """
        
        insights = {
            'key_discoveries': [],
            'pattern_insights': [],
            'adaptation_insights': []
        }
        
        if 'learning_summary' in learning_results:
            summary = learning_results['learning_summary']
            
            # Extract achievements
            for achievement in summary.get('learning_achievements', []):
                insights['key_discoveries'].append({
                    'type': 'learning_achievement',
                    'description': achievement['achievement'],
                    'significance': 'high' if achievement.get('score', 0) >= 4 else 'medium'
                })
            
            # Extract insights
            for insight in summary.get('key_insights', []):
                insights['pattern_insights'].append({
                    'type': 'pattern_insight',
                    'description': insight['insight'],
                    'strength': insight.get('strength', 0)
                })
        
        # Extract next learning priorities
        if 'next_learning_priorities' in learning_results:
            priorities = learning_results['next_learning_priorities']
            
            for priority_type, priority_list in priorities.items():
                for priority in priority_list:
                    insights['adaptation_insights'].append({
                        'type': 'learning_priority',
                        'priority': priority.get('priority', ''),
                        'urgency': priority.get('urgency', 'medium')
                    })
        
        return insights
    
    def _integrate_new_knowledge(self, learning_results: Dict) -> Dict[str, Any]:
        """
        Integrate new knowledge into existing knowledge base
        """
        
        integration_summary = {
            'knowledge_updates': [],
            'knowledge_conflicts': [],
            'integration_effectiveness': 0
        }
        
        if 'knowledge_updates' in learning_results:
            knowledge_updates = learning_results['knowledge_updates']
            
            # Track knowledge updates
            for update_type, update_data in knowledge_updates.items():
                integration_summary['knowledge_updates'].append({
                    'type': update_type,
                    'update_count': len(update_data) if isinstance(update_data, dict) else 1,
                    'integration_status': 'successful'
                })
            
            # Calculate integration effectiveness
            total_updates = len(integration_summary['knowledge_updates'])
            integration_summary['integration_effectiveness'] = min(total_updates / 5, 1.0)  # Max 5 updates
        
        return integration_summary
    
    def _create_integrated_dashboard(self, 
                                   cycle_analysis: Dict,
                                   indicator_analysis: Dict,
                                   adaptation_analysis: Dict,
                                   performance_analysis: Dict,
                                   risk_analysis: Dict,
                                   learning_analysis: Dict) -> Dict[str, Any]:
        """
        Create integrated analysis dashboard
        """
        
        dashboard = {
            'executive_summary': {},
            'key_metrics': {},
            'alerts_and_signals': {},
            'recommendations_dashboard': {},
            'performance_dashboard': {},
            'risk_dashboard': {}
        }
        
        # Executive Summary
        dashboard['executive_summary'] = self._create_executive_summary(
            cycle_analysis, indicator_analysis, adaptation_analysis, risk_analysis
        )
        
        # Key Metrics
        dashboard['key_metrics'] = self._compile_key_metrics(
            cycle_analysis, indicator_analysis, performance_analysis, risk_analysis
        )
        
        # Alerts and Signals
        dashboard['alerts_and_signals'] = self._generate_alerts_and_signals(
            cycle_analysis, indicator_analysis, risk_analysis
        )
        
        # Recommendations Dashboard
        dashboard['recommendations_dashboard'] = self._create_recommendations_dashboard(
            adaptation_analysis, risk_analysis
        )
        
        # Performance Dashboard
        dashboard['performance_dashboard'] = self._create_performance_dashboard(performance_analysis)
        
        # Risk Dashboard
        dashboard['risk_dashboard'] = self._create_risk_dashboard(risk_analysis)
        
        return dashboard
    
    def _create_executive_summary(self, 
                                cycle_analysis: Dict,
                                indicator_analysis: Dict,
                                adaptation_analysis: Dict,
                                risk_analysis: Dict) -> Dict[str, Any]:
        """
        Create executive summary
        """
        
        summary = {
            'current_economic_regime': 'unknown',
            'overall_assessment': 'analysis_incomplete',
            'key_findings': [],
            'immediate_actions_required': [],
            'strategic_outlook': 'neutral'
        }
        
        # Economic regime
        if 'cycle_regime_classification' in cycle_analysis:
            regime_data = cycle_analysis['cycle_regime_classification']
            summary['current_economic_regime'] = regime_data.get('regime', 'unknown')
        
        # Overall assessment based on risk analysis
        if 'overall_risk_assessment' in risk_analysis:
            overall_risk = risk_analysis['overall_risk_assessment']
            risk_rating = overall_risk.get('overall_risk_rating', 'unknown')
            
            if risk_rating == 'critical':
                summary['overall_assessment'] = 'requires_immediate_attention'
            elif risk_rating == 'high':
                summary['overall_assessment'] = 'high_risk_environment'
            elif risk_rating == 'moderate':
                summary['overall_assessment'] = 'moderate_risk_environment'
            else:
                summary['overall_assessment'] = 'low_risk_environment'
        
        # Key findings
        if 'economic_dashboard_score' in indicator_analysis:
            dashboard_score = indicator_analysis['economic_dashboard_score']
            if 'score_interpretation' in dashboard_score:
                interpretation = dashboard_score['score_interpretation']
                summary['key_findings'].append(f"Economic conditions: {interpretation.get('description', 'Unknown')}")
        
        # Immediate actions
        if 'strategic_recommendations' in adaptation_analysis:
            recommendations = adaptation_analysis['strategic_recommendations']
            if 'immediate_actions' in recommendations:
                summary['immediate_actions_required'] = recommendations['immediate_actions'][:3]  # Top 3
        
        return summary
    
    def _compile_key_metrics(self, 
                           cycle_analysis: Dict,
                           indicator_analysis: Dict,
                           performance_analysis: Dict,
                           risk_analysis: Dict) -> Dict[str, Any]:
        """
        Compile key metrics for dashboard
        """
        
        metrics = {
            'economic_metrics': {},
            'performance_metrics': {},
            'risk_metrics': {},
            'learning_metrics': {}
        }
        
        # Economic metrics
        if 'primary_cycle_analysis' in cycle_analysis:
            cycle_data = cycle_analysis['primary_cycle_analysis']
            metrics['economic_metrics'] = {
                'current_cycle_phase': cycle_data.get('current_phase', 'unknown'),
                'cycle_strength': cycle_data.get('cycle_strength', 0),
                'shocks_detected': cycle_data.get('shocks_detected', 0)
            }
        
        # Performance metrics
        if 'risk_adjusted_returns' in performance_analysis and 'risk_adjusted_metrics' in performance_analysis['risk_adjusted_returns']:
            risk_metrics = performance_analysis['risk_adjusted_returns']['risk_adjusted_metrics']
            
            if risk_metrics:
                # Take average across all metrics
                avg_sharpe = np.mean([data['sharpe_ratio'] for data in risk_metrics.values()])
                avg_return = np.mean([data['annual_return'] for data in risk_metrics.values()])
                
                metrics['performance_metrics'] = {
                    'average_sharpe_ratio': avg_sharpe,
                    'average_annual_return': avg_return,
                    'performance_rating': self._rate_overall_performance(avg_sharpe, avg_return)
                }
        
        # Risk metrics
        if 'portfolio_risk' in risk_analysis:
            portfolio_risk = risk_analysis['portfolio_risk']
            metrics['risk_metrics'] = {
                'portfolio_risk_level': portfolio_risk.get('portfolio_risk_level', 'unknown'),
                'portfolio_risk_score': portfolio_risk.get('portfolio_risk_score', 0)
            }
        
        return metrics
    
    def _generate_alerts_and_signals(self, 
                                   cycle_analysis: Dict,
                                   indicator_analysis: Dict,
                                   risk_analysis: Dict) -> Dict[str, List]:
        """
        Generate alerts and signals
        """
        
        alerts = {
            'high_priority_alerts': [],
            'medium_priority_alerts': [],
            'market_signals': [],
            'early_warning_indicators': []
        }
        
        # High priority alerts from risk analysis
        if 'overall_risk_assessment' in risk_analysis:
            overall_risk = risk_analysis['overall_risk_assessment']
            
            if overall_risk.get('overall_risk_rating') in ['critical', 'high']:
                alerts['high_priority_alerts'].append({
                    'alert_type': 'risk_alert',
                    'message': f"Portfolio risk level is {overall_risk['overall_risk_rating']}",
                    'urgency': 'high',
                    'timestamp': pd.Timestamp.now()
                })
        
        # Cycle-based alerts
        if 'primary_cycle_analysis' in cycle_analysis:
            cycle_data = cycle_analysis['primary_cycle_analysis']
            shocks_count = cycle_data.get('shocks_detected', 0)
            
            if shocks_count > 2:
                alerts['high_priority_alerts'].append({
                    'alert_type': 'economic_shock',
                    'message': f"{shocks_count} economic shocks detected",
                    'urgency': 'high'
                })
        
        # Medium priority alerts
        if 'leading_indicators' in indicator_analysis:
            leading_data = indicator_analysis['leading_indicators']
            
            if 'leading_signals_strength' in leading_data:
                signal_strength = leading_data['leading_signals_strength']
                
                if signal_strength in ['weak', 'very_weak']:
                    alerts['medium_priority_alerts'].append({
                        'alert_type': 'leading_signals',
                        'message': f"Leading indicators showing {signal_strength} signals",
                        'urgency': 'medium'
                    })
        
        # Market signals
        alerts['market_signals'] = [
            {
                'signal_type': 'cycle_timing',
                'signal': 'Based on current cycle phase, timing considerations apply',
                'confidence': 'medium'
            }
        ]
        
        return alerts
    
    def _create_recommendations_dashboard(self, 
                                        adaptation_analysis: Dict,
                                        risk_analysis: Dict) -> Dict[str, Any]:
        """
        Create recommendations dashboard
        """
        
        recommendations_dashboard = {
            'strategic_recommendations': [],
            'tactical_recommendations': [],
            'risk_mitigation': [],
            'implementation_timeline': {}
        }
        
        # Strategic recommendations from adaptation analysis
        if 'strategic_recommendations' in adaptation_analysis:
            strategic = adaptation_analysis['strategic_recommendations']
            
            recommendations_dashboard['strategic_recommendations'] = strategic.get('strategic_actions', [])
            recommendations_dashboard['tactical_recommendations'] = strategic.get('tactical_actions', [])
        
        # Risk mitigation from risk analysis
        if 'portfolio_risk' in risk_analysis:
            portfolio_risk = risk_analysis['portfolio_risk']
            
            recommendations_dashboard['risk_mitigation'] = portfolio_risk.get('portfolio_risk_recommendations', [])
        
        # Implementation timeline
        if 'adaptation_timing' in adaptation_analysis:
            timing = adaptation_analysis['adaptation_timing']
            
            recommendations_dashboard['implementation_timeline'] = timing.get('recommended_implementation_schedule', {})
        
        return recommendations_dashboard
    
    def _create_performance_dashboard(self, performance_analysis: Dict) -> Dict[str, Any]:
        """
        Create performance dashboard
        """
        
        performance_dashboard = {
            'performance_summary': {},
            'attribution_analysis': {},
            'benchmark_comparison': {},
            'performance_trends': {}
        }
        
        # Performance summary
        if 'performance_summary' in performance_analysis:
            performance_dashboard['performance_summary'] = performance_analysis['performance_summary']
        
        # Attribution analysis
        if 'cycle_attribution' in performance_analysis:
            cycle_attribution = performance_analysis['cycle_attribution']
            
            performance_dashboard['attribution_analysis'] = {
                'current_cycle_phase': cycle_attribution.get('current_cycle_phase', 'unknown'),
                'cycle_performance': cycle_attribution.get('cycle_performance_summary', {})
            }
        
        # Benchmark comparison (simplified)
        performance_dashboard['benchmark_comparison'] = {
            'status': 'benchmark_data_not_available',
            'note': 'Benchmark comparison requires external benchmark data'
        }
        
        return performance_dashboard
    
    def _create_risk_dashboard(self, risk_analysis: Dict) -> Dict[str, Any]:
        """
        Create risk dashboard
        """
        
        risk_dashboard = {
            'overall_risk_level': 'unknown',
            'risk_breakdown': {},
            'risk_trends': {},
            'risk_limits_status': {}
        }
        
        # Overall risk level
        if 'overall_risk_assessment' in risk_analysis:
            overall_risk = risk_analysis['overall_risk_assessment']
            
            risk_dashboard['overall_risk_level'] = overall_risk.get('overall_risk_rating', 'unknown')
            risk_dashboard['risk_breakdown'] = overall_risk.get('risk_breakdown', [])
        
        # Individual risk components
        if 'portfolio_risk' in risk_analysis:
            portfolio_risk = risk_analysis['portfolio_risk']
            
            risk_dashboard['risk_trends'] = {
                'cycle_risk': portfolio_risk.get('risk_component_breakdown', {}).get('cycle_risk', 'unknown'),
                'adaptation_risk': portfolio_risk.get('risk_component_breakdown', {}).get('adaptation_risk', 'unknown'),
                'market_risk': portfolio_risk.get('risk_component_breakdown', {}).get('market_risk', 'unknown')
            }
        
        return risk_dashboard
    
    def _generate_strategic_recommendations(self, 
                                          integrated_dashboard: Dict,
                                          strategy_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate strategic recommendations
        """
        
        recommendations = {
            'strategic_actions': [],
            'tactical_actions': [],
            'risk_management': [],
            'monitoring_priorities': []
        }
        
        # Strategic actions based on economic regime
        executive_summary = integrated_dashboard.get('executive_summary', {})
        current_regime = executive_summary.get('current_economic_regime', 'unknown')
        
        if current_regime == 'expansion_regime':
            recommendations['strategic_actions'].append({
                'action': 'Increase equity exposure',
                'rationale': 'Favorable economic expansion phase',
                'priority': 'high'
            })
        elif current_regime == 'contraction_regime':
            recommendations['strategic_actions'].append({
                'reduce_risk_exposure',
                'rationale': 'Economic contraction requires defensive positioning',
                'priority': 'high'
            })
        
        # Tactical actions based on risk assessment
        risk_dashboard = integrated_dashboard.get('risk_dashboard', {})
        overall_risk = risk_dashboard.get('overall_risk_level', 'unknown')
        
        if overall_risk == 'high' or overall_risk == 'critical':
            recommendations['tactical_actions'].extend([
                {
                    'action': 'Implement additional hedging',
                    'priority': 'high',
                    'timeline': 'immediate'
                },
                {
                    'action': 'Reduce position sizes',
                    'priority': 'medium',
                    'timeline': 'within_week'
                }
            ])
        
        # Risk management recommendations
        alerts = integrated_dashboard.get('alerts_and_signals', {})
        high_priority_alerts = alerts.get('high_priority_alerts', [])
        
        for alert in high_priority_alerts:
            if alert.get('alert_type') == 'risk_alert':
                recommendations['risk_management'].append({
                    'measure': 'Review risk management protocols',
                    'urgency': alert.get('urgency', 'medium')
                })
        
        # Monitoring priorities
        recommendations['monitoring_priorities'] = [
            'Economic cycle phase transitions',
            'Leading indicator signals',
            'Adaptation effectiveness',
            'Risk metric changes'
        ]
        
        return recommendations
    
    def _calculate_analysis_confidence(self, 
                                     cycle_analysis: Dict,
                                     indicator_analysis: Dict,
                                     learning_analysis: Dict) -> Dict[str, Any]:
        """
        Calculate overall analysis confidence
        """
        
        confidence_scores = {}
        confidence_weights = {
            'cycle_analysis': 0.3,
            'indicator_analysis': 0.4,
            'learning_analysis': 0.3
        }
        
        # Cycle analysis confidence
        if 'primary_cycle_analysis' in cycle_analysis:
            cycle_data = cycle_analysis['primary_cycle_analysis']
            
            if 'shocks_detected' in cycle_data:
                shocks_count = cycle_data['shocks_detected']
                cycle_confidence = max(0, 1 - shocks_count * 0.1)  # Reduce confidence with more shocks
            else:
                cycle_confidence = 0.5
            
            confidence_scores['cycle_analysis'] = cycle_confidence
        
        # Indicator analysis confidence
        if 'comprehensive_indicators' in indicator_analysis:
            indicator_data = indicator_analysis['comprehensive_indicators']
            
            if 'data_quality' in indicator_data:
                data_quality = indicator_data['data_quality']
                quality_score = data_quality.get('overall_quality_score', 0)
                confidence_scores['indicator_analysis'] = quality_score
            else:
                confidence_scores['indicator_analysis'] = 0.5
        
        # Learning analysis confidence
        if 'learning_effectiveness' in learning_analysis:
            learning_effectiveness = learning_analysis['learning_effectiveness']
            overall_effectiveness = learning_effectiveness.get('overall_effectiveness', 0)
            confidence_scores['learning_analysis'] = overall_effectiveness
        
        # Overall confidence calculation
        total_confidence = 0
        total_weight = 0
        
        for component, score in confidence_scores.items():
            weight = confidence_weights.get(component, 0)
            total_confidence += score * weight
            total_weight += weight
        
        overall_confidence = total_confidence / total_weight if total_weight > 0 else 0
        
        return {
            'component_confidences': confidence_scores,
            'overall_confidence': overall_confidence,
            'confidence_rating': (
                'high' if overall_confidence > 0.8 else
                'medium' if overall_confidence > 0.6 else
                'low'
            ),
            'confidence_factors': {
                'data_availability': len(confidence_scores) / 3,
                'analysis_completeness': overall_confidence,
                'learning_effectiveness': confidence_scores.get('learning_analysis', 0)
            }
        }
    
    def _assess_data_quality(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Assess overall data quality
        """
        
        quality_assessment = {
            'data_completeness': {},
            'data_consistency': {},
            'overall_quality_score': 0,
            'quality_issues': [],
            'recommendations': []
        }
        
        total_quality_scores = []
        
        for data_type, df in data.items():
            if df.empty:
                quality_assessment['quality_issues'].append(f'{data_type}_data_missing')
                quality_assessment['data_completeness'][data_type] = 0
                continue
            
            # Completeness assessment
            total_cells = df.shape[0] * df.shape[1]
            missing_cells = df.isnull().sum().sum()
            completeness = 1 - (missing_cells / total_cells)
            
            quality_assessment['data_completeness'][data_type] = completeness
            
            # Consistency assessment (simplified)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                consistency_scores = []
                for col in numeric_cols:
                    series = df[col].dropna()
                    if len(series) > 1:
                        # Check for extreme values
                        z_scores = np.abs((series - series.mean()) / (series.std() + 0.01))
                        extreme_values = (z_scores > 3).sum()
                        consistency_score = 1 - (extreme_values / len(series))
                        consistency_scores.append(consistency_score)
                
                avg_consistency = np.mean(consistency_scores) if consistency_scores else 0.5
                quality_assessment['data_consistency'][data_type] = avg_consistency
                total_quality_scores.append((completeness + avg_consistency) / 2)
            else:
                total_quality_scores.append(completeness)
        
        # Overall quality score
        if total_quality_scores:
            quality_assessment['overall_quality_score'] = np.mean(total_quality_scores)
        
        # Quality issues and recommendations
        if quality_assessment['overall_quality_score'] < 0.7:
            quality_assessment['recommendations'].append('Improve data completeness and consistency')
        
        if any(score < 0.5 for score in quality_assessment['data_completeness'].values()):
            quality_assessment['recommendations'].append('Address missing data issues')
        
        quality_assessment['quality_rating'] = (
            'excellent' if quality_assessment['overall_quality_score'] > 0.9 else
            'good' if quality_assessment['overall_quality_score'] > 0.8 else
            'fair' if quality_assessment['overall_quality_score'] > 0.6 else
            'poor'
        )
        
        return quality_assessment
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """
        Get current analysis status
        """
        
        return {
            'analysis_history_count': len(self.analysis_history),
            'current_analysis_available': bool(self.current_analysis),
            'learning_enabled': self.learning_enabled,
            'last_analysis_timestamp': (
                self.analysis_history[-1]['timestamp'] 
                if self.analysis_history else None
            ),
            'system_components_status': {
                'cycle_detector': 'active',
                'indicators': 'active',
                'adaptation_engine': 'active',
                'learning_system': 'active' if self.learning_enabled else 'disabled'
            }
        }