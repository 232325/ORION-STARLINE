"""
Macro-Economic Adaptation Engine Module

Ushbu modul turli xil iqtisodiy sikllar va makro-iktisodiy o'zgarishlarga
adaptation qilish uchun mo'ljallangan.

Imkoniyatlar:
- Interest rate cycle adaptation
- Inflation cycle adaptation  
- Credit cycle adaptation
- Growth cycle adaptation
- Policy cycle integration
- Dynamic parameter adjustment
- Risk-adjusted strategy adaptation
"""

import numpy as np
import pandas as pd
from scipy import optimize, stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class AdaptationEngine:
    """
    Macro-Economic Adaptation Engine Class
    """
    
    def __init__(self, 
                 adaptation_sensitivity: float = 0.1,
                 cycle_detection_threshold: float = 0.05):
        """
        Adaptation Engine ni initialize qilish
        
        Args:
            adaptation_sensitivity: Adaptation sezgirligi
            cycle_detection_threshold: Cycle detection uchun threshold
        """
        
        self.adaptation_sensitivity = adaptation_sensitivity
        self.cycle_detection_threshold = cycle_detection_threshold
        
        # Economic cycle states
        self.current_interest_cycle = 'neutral'
        self.current_inflation_cycle = 'neutral'
        self.current_credit_cycle = 'neutral'
        self.current_growth_cycle = 'neutral'
        
        # Adaptation parameters
        self.adaptation_parameters = {
            'position_sizing': 1.0,
            'risk_tolerance': 0.5,
            'time_horizon': 12,
            'volatility_adjustment': 1.0,
            'momentum_weight': 0.5,
            'mean_reversion_weight': 0.5
        }
        
        # Historical adaptations tracking
        self.adaptation_history = []
        self.performance_by_cycle = {}
        
        # Policy response parameters
        self.policy_response_params = {
            'monetary_policy_impact': 0.8,
            'fiscal_policy_impact': 0.6,
            'regulatory_impact': 0.4
        }
        
    def adapt_to_economic_cycles(self, 
                               economic_data: pd.DataFrame,
                               strategy_config: dict,
                               current_positions: dict = None) -> dict:
        """
        Iqtisodiy sikllarga adaptation qilish
        
        Args:
            economic_data: Iqtisodiy ma'lumotlar
            strategy_config: Strategy konfiguratsiyasi
            current_positions: Hozirgi pozitsiyalar
            
        Returns:
            dict: Adaptation recommendations
        """
        
        try:
            # Detect current economic cycles
            cycle_detection = self._detect_economic_cycles(economic_data)
            
            # Analyze policy environment
            policy_analysis = self._analyze_policy_environment(economic_data)
            
            # Calculate adaptation requirements
            adaptation_requirements = self._calculate_adaptation_requirements(
                cycle_detection, policy_analysis, strategy_config
            )
            
            # Generate adaptation recommendations
            adaptation_recommendations = self._generate_adaptation_recommendations(
                adaptation_requirements, current_positions
            )
            
            # Validate and optimize adaptations
            optimized_adaptations = self._optimize_adaptations(
                adaptation_recommendations, economic_data, strategy_config
            )
            
            results = {
                'cycle_detection': cycle_detection,
                'policy_analysis': policy_analysis,
                'adaptation_requirements': adaptation_requirements,
                'recommendations': adaptation_recommendations,
                'optimized_adaptations': optimized_adaptations,
                'implementation_priority': self._prioritize_implementations(optimized_adaptations),
                'risk_assessment': self._assess_adaptation_risks(optimized_adaptations),
                'expected_impact': self._estimate_adaptation_impact(optimized_adaptations)
            }
            
            # Track adaptation decision
            self._track_adaptation_decision(results)
            
            return results
            
        except Exception as e:
            return {'error': f'Economic cycle adaptation failed: {str(e)}'}
    
    def _detect_economic_cycles(self, data: pd.DataFrame) -> dict:
        """
        Iqtisodiy sikllarni aniqlash
        """
        
        cycle_detection = {}
        
        # Interest rate cycle detection
        if 'interest_rate' in data.columns or 'fed_funds_rate' in data.columns:
            rate_col = 'interest_rate' if 'interest_rate' in data.columns else 'fed_funds_rate'
            cycle_detection['interest_rate'] = self._detect_interest_rate_cycle(data[rate_col])
        
        # Inflation cycle detection
        inflation_cols = ['cpi', 'inflation_rate', 'core_cpi', 'core_inflation']
        for col in inflation_cols:
            if col in data.columns:
                cycle_detection['inflation'] = self._detect_inflation_cycle(data[col])
                break
        
        # Credit cycle detection
        credit_cols = ['credit_growth', 'credit_spreads', 'loan_growth', 'm2_growth']
        for col in credit_cols:
            if col in data.columns:
                cycle_detection['credit'] = self._detect_credit_cycle(data[col])
                break
        
        # Growth cycle detection
        growth_cols = ['gdp_growth', 'industrial_production', 'employment_growth']
        for col in growth_cols:
            if col in data.columns:
                cycle_detection['growth'] = self._detect_growth_cycle(data[col])
                break
        
        return cycle_detection
    
    def _detect_interest_rate_cycle(self, rate_series: pd.Series) -> dict:
        """
        Interest rate cycle detection
        """
        
        if len(rate_series) < 12:
            return {'cycle': 'insufficient_data'}
        
        # Calculate rate changes and trend
        rate_change = rate_series.diff()
        
        # Cycle phase determination
        current_rate = rate_series.iloc[-1]
        recent_trend = rate_series.tail(6).mean() - rate_series.head(6).mean()
        
        # Historical rate levels
        rate_percentile = stats.percentileofscore(rate_series.dropna(), current_rate)
        
        # Cycle classification
        if rate_percentile > 80 and recent_trend < 0:
            cycle = 'tightening_end'
        elif rate_percentile > 60 and recent_trend < 0:
            cycle = 'tightening'
        elif rate_percentile < 20 and recent_trend > 0:
            cycle = 'easing_end'
        elif rate_percentile < 40 and recent_trend > 0:
            cycle = 'easing'
        else:
            cycle = 'neutral'
        
        return {
            'cycle': cycle,
            'current_level': current_rate,
            'trend': recent_trend,
            'percentile': rate_percentile,
            'cycle_strength': abs(recent_trend) / rate_series.std(),
            'expected_reversal': self._predict_rate_reversal(rate_series, cycle)
        }
    
    def _detect_inflation_cycle(self, inflation_series: pd.Series) -> dict:
        """
        Inflation cycle detection
        """
        
        if len(inflation_series) < 12:
            return {'cycle': 'insufficient_data'}
        
        # Inflation momentum
        inflation_momentum = inflation_series.tail(6).mean() - inflation_series.head(6).mean()
        inflation_acceleration = inflation_series.diff().tail(3).mean()
        
        # Target analysis (assuming 2% target)
        target = 0.02
        current_inflation = inflation_series.iloc[-1]
        target_deviation = current_inflation - target
        
        # Cycle classification
        if current_inflation > target + 0.01 and inflation_momentum > 0:
            cycle = 'heating_up'
        elif current_inflation > target + 0.01 and inflation_momentum < 0:
            cycle = 'cooling'
        elif current_inflation < target - 0.01 and inflation_momentum < 0:
            cycle = 'deflation_risk'
        elif current_inflation < target - 0.01 and inflation_momentum > 0:
            cycle = 'recovering'
        else:
            cycle = 'target_range'
        
        return {
            'cycle': cycle,
            'current_level': current_inflation,
            'momentum': inflation_momentum,
            'acceleration': inflation_acceleration,
            'target_deviation': target_deviation,
            'expected_policy_response': self._predict_inflation_policy_response(cycle),
            'cycle_duration': len(inflation_series)
        }
    
    def _detect_credit_cycle(self, credit_series: pd.Series) -> dict:
        """
        Credit cycle detection
        """
        
        if len(credit_series) < 12:
            return {'cycle': 'insufficient_data'}
        
        # Credit growth momentum
        credit_momentum = credit_series.tail(6).mean() - credit_series.head(6).mean()
        
        # Credit volatility
        credit_volatility = credit_series.rolling(12).std().iloc[-1]
        historical_volatility = credit_series.std()
        
        # Cycle classification based on growth levels and momentum
        current_level = credit_series.iloc[-1]
        level_percentile = stats.percentileofscore(credit_series.dropna(), current_level)
        
        if level_percentile > 80 and credit_momentum > 0:
            cycle = 'credit_boom'
        elif level_percentile > 60 and credit_momentum > 0:
            cycle = 'credit_expansion'
        elif level_percentile < 20 and credit_momentum < 0:
            cycle = 'credit_contraction'
        elif level_percentile < 40 and credit_momentum < 0:
            cycle = 'credit_weakness'
        else:
            cycle = 'credit_neutral'
        
        return {
            'cycle': cycle,
            'current_level': current_level,
            'momentum': credit_momentum,
            'volatility_ratio': credit_volatility / historical_volatility,
            'percentile': level_percentile,
            'financial_stability_risk': self._assess_credit_stability_risk(credit_series, cycle)
        }
    
    def _detect_growth_cycle(self, growth_series: pd.Series) -> dict:
        """
        Growth cycle detection
        """
        
        if len(growth_series) < 12:
            return {'cycle': 'insufficient_data'}
        
        # Growth momentum and volatility
        growth_momentum = growth_series.tail(6).mean() - growth_series.head(6).mean()
        growth_volatility = growth_series.rolling(12).std().iloc[-1]
        
        # Current growth level
        current_growth = growth_series.iloc[-1]
        growth_trend = (growth_series.tail(12).mean() - growth_series.head(12).mean()) / abs(growth_series.head(12).mean()) if growth_series.head(12).mean() != 0 else 0
        
        # Cycle classification
        if current_growth > 0.03 and growth_momentum > 0:  # >3% growth
            cycle = 'strong_expansion'
        elif current_growth > 0.015 and growth_momentum > 0:  # >1.5% growth
            cycle = 'moderate_expansion'
        elif current_growth > 0 and growth_momentum > 0:
            cycle = 'slow_expansion'
        elif current_growth > 0 and growth_momentum < 0:
            cycle = 'expansion_slowing'
        elif current_growth < 0 and growth_momentum < 0:
            cycle = 'recession'
        elif current_growth < 0 and growth_momentum > 0:
            cycle = 'recovery_from_recession'
        else:
            cycle = 'stagnation'
        
        return {
            'cycle': cycle,
            'current_level': current_growth,
            'momentum': growth_momentum,
            'volatility': growth_volatility,
            'trend_strength': abs(growth_trend),
            'cycle_probability': self._estimate_cycle_probability(growth_series, cycle)
        }
    
    def _predict_rate_reversal(self, rate_series: pd.Series, cycle: str) -> dict:
        """
        Interest rate reversal prediction
        """
        
        # Simplified prediction based on cycle position
        reversal_probabilities = {
            'tightening_end': {'probability': 0.7, 'timeframe_months': 6},
            'tightening': {'probability': 0.4, 'timeframe_months': 12},
            'easing_end': {'probability': 0.8, 'timeframe_months': 4},
            'easing': {'probability': 0.5, 'timeframe_months': 10},
            'neutral': {'probability': 0.3, 'timeframe_months': 18}
        }
        
        return reversal_probabilities.get(cycle, {'probability': 0.2, 'timeframe_months': 24})
    
    def _predict_inflation_policy_response(self, cycle: str) -> dict:
        """
        Inflation policy response prediction
        """
        
        policy_responses = {
            'heating_up': {'response': 'tightening', 'intensity': 'high', 'lag_months': 3},
            'cooling': {'response': 'neutral', 'intensity': 'low', 'lag_months': 6},
            'deflation_risk': {'response': 'stimulus', 'intensity': 'high', 'lag_months': 2},
            'recovering': {'response': 'neutral', 'intensity': 'medium', 'lag_months': 8},
            'target_range': {'response': 'hold', 'intensity': 'minimal', 'lag_months': 12}
        }
        
        return policy_responses.get(cycle, {'response': 'monitoring', 'intensity': 'low', 'lag_months': 12})
    
    def _assess_credit_stability_risk(self, credit_series: pd.Series, cycle: str) -> str:
        """
        Credit stability risk assessment
        """
        
        # High-risk cycles
        high_risk_cycles = ['credit_boom', 'credit_contraction']
        moderate_risk_cycles = ['credit_expansion', 'credit_weakness']
        
        if cycle in high_risk_cycles:
            return 'high'
        elif cycle in moderate_risk_cycles:
            return 'moderate'
        else:
            return 'low'
    
    def _estimate_cycle_probability(self, growth_series: pd.Series, cycle: str) -> float:
        """
        Cycle probability estimation
        """
        
        # Simplified probability based on cycle characteristics
        cycle_probabilities = {
            'strong_expansion': 0.8,
            'moderate_expansion': 0.7,
            'slow_expansion': 0.6,
            'expansion_slowing': 0.5,
            'recession': 0.9,
            'recovery_from_recession': 0.8,
            'stagnation': 0.6
        }
        
        return cycle_probabilities.get(cycle, 0.5)
    
    def _analyze_policy_environment(self, data: pd.DataFrame) -> dict:
        """
        Policy environment analysis
        """
        
        policy_analysis = {}
        
        # Monetary policy stance
        if 'fed_funds_rate' in data.columns or 'interest_rate' in data.columns:
            rate_col = 'fed_funds_rate' if 'fed_funds_rate' in data.columns else 'interest_rate'
            policy_analysis['monetary_stance'] = self._analyze_monetary_policy_stance(data[rate_col])
        
        # Fiscal policy indicators
        fiscal_indicators = ['government_spending', 'budget_deficit', 'debt_to_gdp']
        available_fiscal = [ind for ind in fiscal_indicators if ind in data.columns]
        
        if available_fiscal:
            policy_analysis['fiscal_stance'] = self._analyze_fiscal_policy_stance(data[available_fiscal])
        
        # Regulatory environment
        regulatory_cols = ['financial_regulation_index', 'business_regulation_index', 'regulatory_cost_index']
        available_reg = [col for col in regulatory_cols if col in data.columns]
        
        if available_reg:
            policy_analysis['regulatory_environment'] = self._analyze_regulatory_environment(data[available_reg])
        
        # Policy coordination assessment
        policy_analysis['coordination'] = self._assess_policy_coordination(policy_analysis)
        
        return policy_analysis
    
    def _analyze_monetary_policy_stance(self, rate_series: pd.Series) -> dict:
        """
        Monetary policy stance analysis
        """
        
        if len(rate_series) < 12:
            return {'stance': 'unknown'}
        
        # Rate level and trend
        current_rate = rate_series.iloc[-1]
        rate_trend = rate_series.tail(6).mean() - rate_series.head(6).mean()
        
        # Policy stance classification
        if current_rate > 0.04 and rate_trend < 0:  # >4% and declining
            stance = 'tightening_ending'
        elif current_rate > 0.03 and rate_trend < 0:  # >3% and declining
            stance = 'gradual_tightening'
        elif current_rate < 0.005 and rate_trend > 0:  # <0.5% and rising
            stance = 'easing_ending'
        elif current_rate < 0.015 and rate_trend > 0:  # <1.5% and rising
            stance = 'gradual_easing'
        elif rate_trend > 0:
            stance = 'accommodative'
        elif rate_trend < 0:
            stance = 'restrictive'
        else:
            stance = 'neutral'
        
        return {
            'stance': stance,
            'policy_rate': current_rate,
            'rate_trend': rate_trend,
            'policy_intensity': abs(rate_trend) / rate_series.std(),
            'expected_duration': self._estimate_policy_duration(stance)
        }
    
    def _analyze_fiscal_policy_stance(self, fiscal_data: pd.DataFrame) -> dict:
        """
        Fiscal policy stance analysis
        """
        
        stance_indicators = {}
        
        for col in fiscal_data.columns:
            if col == 'government_spending':
                # Spending growth analysis
                spending_growth = fiscal_data[col].pct_change(12).iloc[-1]
                if spending_growth > 0.05:  # >5% growth
                    stance_indicators[col] = 'expansionary'
                elif spending_growth < 0:
                    stance_indicators[col] = 'contractionary'
                else:
                    stance_indicators[col] = 'neutral'
            
            elif col == 'budget_deficit':
                # Deficit level analysis
                deficit_level = fiscal_data[col].iloc[-1]
                if deficit_level > 0.05:  # >5% deficit
                    stance_indicators[col] = 'expansionary'
                elif deficit_level < 0.02:  # <2% deficit
                    stance_indicators[col] = 'neutral'
                else:
                    stance_indicators[col] = 'moderate_expansionary'
            
            elif col == 'debt_to_gdp':
                # Debt sustainability
                debt_ratio = fiscal_data[col].iloc[-1]
                if debt_ratio > 1.0:  # >100% debt ratio
                    stance_indicators[col] = 'debt_concern'
                else:
                    stance_indicators[col] = 'sustainable'
        
        # Overall fiscal stance
        expansionary_count = sum(1 for stance in stance_indicators.values() if 'expansion' in stance)
        contractionary_count = sum(1 for stance in stance_indicators.values() if 'contraction' in stance)
        
        if expansionary_count > contractionary_count:
            overall_stance = 'expansionary'
        elif contractionary_count > expansionary_count:
            overall_stance = 'contractionary'
        else:
            overall_stance = 'neutral'
        
        return {
            'overall_stance': overall_stance,
            'component_stances': stance_indicators,
            'policy_sustainability': self._assess_fiscal_sustainability(fiscal_data)
        }
    
    def _analyze_regulatory_environment(self, reg_data: pd.DataFrame) -> dict:
        """
        Regulatory environment analysis
        """
        
        if reg_data.empty:
            return {'environment': 'unknown'}
        
        # Regulatory trend analysis
        reg_trends = {}
        for col in reg_data.columns:
            reg_trend = reg_data[col].tail(6).mean() - reg_data[col].head(6).mean()
            reg_trends[col] = 'tightening' if reg_trend > 0 else 'loosening'
        
        # Overall regulatory environment
        tightening_count = sum(1 for trend in reg_trends.values() if trend == 'tightening')
        total_indicators = len(reg_trends)
        
        if tightening_count / total_indicators > 0.6:
            environment = 'tightening'
        elif tightening_count / total_indicators < 0.4:
            environment = 'loosening'
        else:
            environment = 'neutral'
        
        return {
            'environment': environment,
            'component_trends': reg_trends,
            'regulatory_intensity': abs(reg_data.diff().iloc[-6:].mean().mean())
        }
    
    def _assess_policy_coordination(self, policy_analysis: dict) -> dict:
        """
        Policy coordination assessment
        """
        
        coordination_score = 0
        policy_count = 0
        
        # Monetary-fiscal coordination
        if 'monetary_stance' in policy_analysis and 'fiscal_stance' in policy_analysis:
            monetary_stance = policy_analysis['monetary_stance'].get('stance', 'neutral')
            fiscal_stance = policy_analysis['fiscal_stance'].get('overall_stance', 'neutral')
            
            # Coordination logic (simplified)
            if 'expansion' in monetary_stance and 'expansion' in fiscal_stance:
                coordination_score += 1  # Coordinated expansion
            elif 'tightening' in monetary_stance and 'contraction' in fiscal_stance:
                coordination_score += 1  # Coordinated tightening
            elif ('expansion' in monetary_stance and 'contraction' in fiscal_stance) or \
                 ('tightening' in monetary_stance and 'expansion' in fiscal_stance):
                coordination_score -= 1  # Counterproductive policies
            
            policy_count += 1
        
        # Overall coordination
        if policy_count > 0:
            coordination = 'high' if coordination_score > 0 else 'low' if coordination_score < 0 else 'moderate'
        else:
            coordination = 'unknown'
        
        return {
            'coordination_level': coordination,
            'coordination_score': coordination_score,
            'policy_interaction': self._analyze_policy_interactions(policy_analysis)
        }
    
    def _analyze_policy_interactions(self, policy_analysis: dict) -> dict:
        """
        Policy interactions analysis
        """
        
        interactions = {}
        
        # Monetary-Fiscal interaction
        if 'monetary_stance' in policy_analysis and 'fiscal_stance' in policy_analysis:
            monetary = policy_analysis['monetary_stance'].get('stance', 'neutral')
            fiscal = policy_analysis['fiscal_stance'].get('overall_stance', 'neutral')
            
            interaction_effect = 'neutral'
            if 'expansion' in monetary and 'expansion' in fiscal:
                interaction_effect = 'highly_accommodative'
            elif 'tightening' in monetary and 'contraction' in fiscal:
                interaction_effect = 'highly_restrictive'
            elif ('expansion' in monetary and 'contraction' in fiscal) or \
                 ('tightening' in monetary and 'expansion' in fiscal):
                interaction_effect = 'policy_conflict'
            
            interactions['monetary_fiscal'] = {
                'effect': interaction_effect,
                'net_impact': self._calculate_net_policy_impact(monetary, fiscal)
            }
        
        return interactions
    
    def _calculate_net_policy_impact(self, monetary_stance: str, fiscal_stance: str) -> float:
        """
        Net policy impact calculation
        """
        
        # Simplified impact scoring
        stance_impacts = {
            'tightening_ending': -0.5,
            'gradual_tightening': -0.7,
            'accommodative': 0.8,
            'easing_ending': 0.5,
            'gradual_easing': 0.7,
            'restrictive': -0.8,
            'neutral': 0,
            'unknown': 0
        }
        
        fiscal_impacts = {
            'expansionary': 0.6,
            'contractionary': -0.6,
            'neutral': 0,
            'moderate_expansionary': 0.3,
            'debt_concern': -0.3,
            'sustainable': 0.1
        }
        
        monetary_impact = stance_impacts.get(monetary_stance, 0)
        fiscal_impact = fiscal_impacts.get(fiscal_stance, 0)
        
        return (monetary_impact + fiscal_impact) / 2
    
    def _estimate_policy_duration(self, stance: str) -> int:
        """
        Policy duration estimation (months)
        """
        
        duration_estimates = {
            'tightening_ending': 6,
            'gradual_tightening': 18,
            'easing_ending': 4,
            'gradual_easing': 15,
            'accommodative': 12,
            'restrictive': 15,
            'neutral': 24
        }
        
        return duration_estimates.get(stance, 12)
    
    def _assess_fiscal_sustainability(self, fiscal_data: pd.DataFrame) -> str:
        """
        Fiscal sustainability assessment
        """
        
        sustainability_score = 0
        
        # Debt-to-GDP assessment
        if 'debt_to_gdp' in fiscal_data.columns:
            debt_ratio = fiscal_data['debt_to_gdp'].iloc[-1]
            if debt_ratio < 0.6:  # <60%
                sustainability_score += 1
            elif debt_ratio > 1.0:  # >100%
                sustainability_score -= 1
        
        # Deficit trend assessment
        if 'budget_deficit' in fiscal_data.columns:
            deficit_trend = fiscal_data['budget_deficit'].tail(12).mean() - fiscal_data['budget_deficit'].head(12).mean()
            if deficit_trend < 0:  # Deficit improving
                sustainability_score += 1
            else:
                sustainability_score -= 0.5
        
        if sustainability_score > 0.5:
            return 'high'
        elif sustainability_score < -0.5:
            return 'low'
        else:
            return 'moderate'
    
    def _calculate_adaptation_requirements(self, 
                                         cycle_detection: dict,
                                         policy_analysis: dict,
                                         strategy_config: dict) -> dict:
        """
        Adaptation requirements calculation
        """
        
        requirements = {
            'position_sizing_adjustment': 0,
            'risk_tolerance_adjustment': 0,
            'time_horizon_adjustment': 0,
            'volatility_adjustment': 0,
            'strategy_rotation': []
        }
        
        # Interest rate cycle adaptation
        if 'interest_rate' in cycle_detection:
            rate_cycle = cycle_detection['interest_rate']['cycle']
            rate_adjustment = self._calculate_rate_cycle_adjustment(rate_cycle)
            requirements['position_sizing_adjustment'] += rate_adjustment * 0.3
        
        # Inflation cycle adaptation
        if 'inflation' in cycle_detection:
            inflation_cycle = cycle_detection['inflation']['cycle']
            inflation_adjustment = self._calculate_inflation_cycle_adjustment(inflation_cycle)
            requirements['risk_tolerance_adjustment'] += inflation_adjustment * 0.2
        
        # Credit cycle adaptation
        if 'credit' in cycle_detection:
            credit_cycle = cycle_detection['credit']['cycle']
            credit_adjustment = self._calculate_credit_cycle_adjustment(credit_cycle)
            requirements['volatility_adjustment'] += credit_adjustment * 0.4
        
        # Growth cycle adaptation
        if 'growth' in cycle_detection:
            growth_cycle = cycle_detection['growth']['cycle']
            growth_adjustment = self._calculate_growth_cycle_adjustment(growth_cycle)
            requirements['time_horizon_adjustment'] += growth_adjustment * 0.1
        
        # Policy adaptation
        policy_adjustment = self._calculate_policy_adjustment(policy_analysis)
        requirements['position_sizing_adjustment'] += policy_adjustment * 0.2
        
        # Strategy rotation recommendations
        requirements['strategy_rotation'] = self._recommend_strategy_rotation(
            cycle_detection, policy_analysis, strategy_config
        )
        
        return requirements
    
    def _calculate_rate_cycle_adjustment(self, cycle: str) -> float:
        """
        Interest rate cycle adaptation calculation
        """
        
        adjustments = {
            'tightening_end': -0.2,  # Reduce exposure as tightening ends
            'tightening': -0.4,      # Reduce exposure during tightening
            'easing_end': 0.3,       # Increase exposure as easing ends
            'easing': 0.2,           # Increase exposure during easing
            'neutral': 0.0
        }
        
        return adjustments.get(cycle, 0.0)
    
    def _calculate_inflation_cycle_adjustment(self, cycle: str) -> float:
        """
        Inflation cycle adaptation calculation
        """
        
        adjustments = {
            'heating_up': -0.3,      # Reduce risk tolerance during inflation heating
            'cooling': 0.1,          # Slightly increase risk tolerance
            'deflation_risk': 0.2,   # Increase risk tolerance during deflation risk
            'recovering': 0.1,       # Increase risk tolerance during recovery
            'target_range': 0.0      # No adjustment in target range
        }
        
        return adjustments.get(cycle, 0.0)
    
    def _calculate_credit_cycle_adjustment(self, cycle: str) -> float:
        """
        Credit cycle adaptation calculation
        """
        
        adjustments = {
            'credit_boom': -0.4,     # Reduce volatility exposure during credit boom
            'credit_expansion': -0.2, # Slightly reduce exposure
            'credit_contraction': -0.6, # Reduce exposure during contraction
            'credit_weakness': -0.3,  # Reduce exposure during weakness
            'credit_neutral': 0.0    # No adjustment
        }
        
        return adjustments.get(cycle, 0.0)
    
    def _calculate_growth_cycle_adjustment(self, cycle: str) -> float:
        """
        Growth cycle adaptation calculation
        """
        
        adjustments = {
            'strong_expansion': 0.3,  # Increase time horizon
            'moderate_expansion': 0.2,
            'slow_expansion': 0.1,
            'expansion_slowing': -0.1, # Decrease time horizon
            'recession': -0.4,        # Significantly decrease time horizon
            'recovery_from_recession': 0.2, # Increase time horizon during recovery
            'stagnation': -0.2        # Decrease time horizon during stagnation
        }
        
        return adjustments.get(cycle, 0.0)
    
    def _calculate_policy_adjustment(self, policy_analysis: dict) -> float:
        """
        Policy environment adaptation calculation
        """
        
        total_adjustment = 0
        policy_count = 0
        
        # Monetary policy adjustment
        if 'monetary_stance' in policy_analysis:
            monetary_impact = self._get_monetary_policy_impact(policy_analysis['monetary_stance'])
            total_adjustment += monetary_impact
            policy_count += 1
        
        # Fiscal policy adjustment
        if 'fiscal_stance' in policy_analysis:
            fiscal_impact = self._get_fiscal_policy_impact(policy_analysis['fiscal_stance'])
            total_adjustment += fiscal_impact
            policy_count += 1
        
        # Regulatory environment adjustment
        if 'regulatory_environment' in policy_analysis:
            reg_impact = self._get_regulatory_environment_impact(policy_analysis['regulatory_environment'])
            total_adjustment += reg_impact
            policy_count += 1
        
        return total_adjustment / policy_count if policy_count > 0 else 0
    
    def _get_monetary_policy_impact(self, monetary_stance: dict) -> float:
        """
        Monetary policy impact on position sizing
        """
        
        stance = monetary_stance.get('stance', 'neutral')
        
        impacts = {
            'tightening_ending': -0.2,
            'gradual_tightening': -0.3,
            'easing_ending': 0.3,
            'gradual_easing': 0.2,
            'accommodative': 0.4,
            'restrictive': -0.4,
            'neutral': 0.0
        }
        
        return impacts.get(stance, 0.0) * self.policy_response_params['monetary_policy_impact']
    
    def _get_fiscal_policy_impact(self, fiscal_stance: dict) -> float:
        """
        Fiscal policy impact on position sizing
        """
        
        stance = fiscal_stance.get('overall_stance', 'neutral')
        
        impacts = {
            'expansionary': 0.3,
            'contractionary': -0.2,
            'neutral': 0.0
        }
        
        return impacts.get(stance, 0.0) * self.policy_response_params['fiscal_policy_impact']
    
    def _get_regulatory_environment_impact(self, regulatory_env: dict) -> float:
        """
        Regulatory environment impact on position sizing
        """
        
        environment = regulatory_env.get('environment', 'neutral')
        
        impacts = {
            'tightening': -0.2,  # Tightening regulations reduce opportunities
            'loosening': 0.2,    # Loosening regulations increase opportunities
            'neutral': 0.0
        }
        
        return impacts.get(environment, 0.0) * self.policy_response_params['regulatory_impact']
    
    def _recommend_strategy_rotation(self, 
                                   cycle_detection: dict,
                                   policy_analysis: dict,
                                   strategy_config: dict) -> list:
        """
        Strategy rotation recommendations
        """
        
        rotations = []
        
        # Defensive strategies during tightening/uncertain periods
        if ('interest_rate' in cycle_detection and 
            cycle_detection['interest_rate']['cycle'] in ['tightening', 'tightening_end']):
            rotations.append({
                'from': 'growth_stocks',
                'to': 'defensive_stocks',
                'reason': 'Interest rate tightening reduces growth stock valuations',
                'priority': 'high'
            })
        
        # Rotation to inflation-protected assets during inflation heating
        if ('inflation' in cycle_detection and 
            cycle_detection['inflation']['cycle'] == 'heating_up'):
            rotations.append({
                'from': 'nominal_bonds',
                'to': 'inflation_protected_bonds',
                'reason': 'Inflation heating reduces nominal bond returns',
                'priority': 'high'
            })
        
        # Rotation to credit-sensitive assets during credit expansion
        if ('credit' in cycle_detection and 
            cycle_detection['credit']['cycle'] in ['credit_boom', 'credit_expansion']):
            rotations.append({
                'from': 'government_bonds',
                'to': 'corporate_bonds',
                'reason': 'Credit expansion improves corporate bond prospects',
                'priority': 'medium'
            })
        
        # Rotation to cyclical assets during strong growth
        if ('growth' in cycle_detection and 
            cycle_detection['growth']['cycle'] == 'strong_expansion'):
            rotations.append({
                'from': 'consumer_staples',
                'to': 'consumer_discretionary',
                'reason': 'Strong growth supports cyclical consumer spending',
                'priority': 'medium'
            })
        
        return rotations
    
    def _generate_adaptation_recommendations(self, 
                                           requirements: dict,
                                           current_positions: dict = None) -> dict:
        """
        Adaptation recommendations generation
        """
        
        recommendations = {
            'parameter_adjustments': {},
            'position_adjustments': {},
            'risk_adjustments': {},
            'timing_recommendations': {}
        }
        
        # Parameter adjustments
        base_position_sizing = self.adaptation_parameters['position_sizing']
        base_risk_tolerance = self.adaptation_parameters['risk_tolerance']
        base_time_horizon = self.adaptation_parameters['time_horizon']
        base_volatility = self.adaptation_parameters['volatility_adjustment']
        
        # Apply adjustments with sensitivity scaling
        sensitivity = self.adaptation_sensitivity
        
        recommendations['parameter_adjustments'] = {
            'position_sizing': {
                'current': base_position_sizing,
                'recommended': base_position_sizing * (1 + requirements['position_sizing_adjustment'] * sensitivity),
                'adjustment_factor': requirements['position_sizing_adjustment'] * sensitivity,
                'confidence': 'high' if abs(requirements['position_sizing_adjustment']) > 0.2 else 'medium'
            },
            'risk_tolerance': {
                'current': base_risk_tolerance,
                'recommended': base_risk_tolerance * (1 + requirements['risk_tolerance_adjustment'] * sensitivity),
                'adjustment_factor': requirements['risk_tolerance_adjustment'] * sensitivity,
                'confidence': 'medium'
            },
            'time_horizon': {
                'current': base_time_horizon,
                'recommended': int(base_time_horizon * (1 + requirements['time_horizon_adjustment'] * sensitivity)),
                'adjustment_factor': requirements['time_horizon_adjustment'] * sensitivity,
                'confidence': 'low'
            },
            'volatility_adjustment': {
                'current': base_volatility,
                'recommended': base_volatility * (1 + requirements['volatility_adjustment'] * sensitivity),
                'adjustment_factor': requirements['volatility_adjustment'] * sensitivity,
                'confidence': 'high' if abs(requirements['volatility_adjustment']) > 0.3 else 'medium'
            }
        }
        
        # Position adjustments based on strategy rotations
        if requirements['strategy_rotation']:
            rotation_adjustments = []
            for rotation in requirements['strategy_rotation']:
                rotation_adjustments.append({
                    'action': 'rotate',
                    'from_asset': rotation['from'],
                    'to_asset': rotation['to'],
                    'reason': rotation['reason'],
                    'priority': rotation['priority'],
                    'expected_impact': self._estimate_rotation_impact(rotation)
                })
            recommendations['position_adjustments']['strategy_rotations'] = rotation_adjustments
        
        # Risk adjustments
        recommendations['risk_adjustments'] = {
            'hedge_recommendations': self._generate_hedge_recommendations(requirements),
            'stop_loss_adjustments': self._adjust_stop_loss_parameters(requirements),
            'portfolio_concentration': self._adjust_portfolio_concentration(requirements)
        }
        
        # Timing recommendations
        recommendations['timing_recommendations'] = {
            'immediate_actions': [rot for rot in requirements['strategy_rotation'] if rot['priority'] == 'high'],
            'phased_implementation': self._plan_phased_implementation(requirements),
            'monitoring_frequency': self._recommend_monitoring_frequency(requirements),
            'review_schedule': self._recommend_review_schedule(requirements)
        }
        
        return recommendations
    
    def _estimate_rotation_impact(self, rotation: dict) -> dict:
        """
        Strategy rotation impact estimation
        """
        
        # Simplified impact estimation
        impact_estimates = {
            ('growth_stocks', 'defensive_stocks'): {'expected_return_impact': -0.1, 'risk_impact': -0.2},
            ('nominal_bonds', 'inflation_protected_bonds'): {'expected_return_impact': 0.05, 'risk_impact': -0.1},
            ('government_bonds', 'corporate_bonds'): {'expected_return_impact': 0.08, 'risk_impact': 0.15},
            ('consumer_staples', 'consumer_discretionary'): {'expected_return_impact': 0.12, 'risk_impact': 0.10}
        }
        
        rotation_key = (rotation['from'], rotation['to'])
        if rotation_key in impact_estimates:
            return impact_estimates[rotation_key]
        else:
            return {'expected_return_impact': 0.0, 'risk_impact': 0.0}
    
    def _generate_hedge_recommendations(self, requirements: dict) -> list:
        """
        Hedge recommendations based on economic conditions
        """
        
        hedges = []
        
        # Inflation hedge during heating
        if requirements.get('volatility_adjustment', 0) > 0.3:
            hedges.append({
                'hedge_type': 'inflation_protection',
                'instruments': ['TIPS', 'commodities', 'real_estate'],
                'allocation': '5-10%',
                'priority': 'medium'
            })
        
        # Credit hedge during contraction
        if requirements.get('position_sizing_adjustment', 0) < -0.2:
            hedges.append({
                'hedge_type': 'credit_protection',
                'instruments': ['high_quality_corporate_bonds', 'government_bonds'],
                'allocation': '10-15%',
                'priority': 'high'
            })
        
        return hedges
    
    def _adjust_stop_loss_parameters(self, requirements: dict) -> dict:
        """
        Stop loss parameter adjustments
        """
        
        base_stop_loss = 0.05  # 5% base stop loss
        
        # Tighten stop losses during high volatility periods
        if requirements.get('volatility_adjustment', 0) > 0.2:
            adjusted_stop_loss = base_stop_loss * 0.8  # Tighten by 20%
        else:
            adjusted_stop_loss = base_stop_loss
        
        return {
            'current_stop_loss': base_stop_loss,
            'recommended_stop_loss': adjusted_stop_loss,
            'adjustment_reason': 'volatility_adjustment' if requirements.get('volatility_adjustment', 0) > 0.2 else 'no_change',
            'confidence': 'medium'
        }
    
    def _adjust_portfolio_concentration(self, requirements: dict) -> dict:
        """
        Portfolio concentration adjustments
        """
        
        max_concentration_base = 0.20  # 20% base max concentration
        
        # Reduce concentration during uncertain periods
        if requirements.get('position_sizing_adjustment', 0) < -0.1:
            max_concentration = max_concentration_base * 0.8  # Reduce to 16%
        else:
            max_concentration = max_concentration_base
        
        return {
            'current_max_concentration': max_concentration_base,
            'recommended_max_concentration': max_concentration,
            'adjustment_reason': 'position_sizing_adjustment' if requirements.get('position_sizing_adjustment', 0) < -0.1 else 'no_change'
        }
    
    def _plan_phased_implementation(self, requirements: dict) -> dict:
        """
        Phased implementation planning
        """
        
        phases = {
            'phase_1_immediate': [],
            'phase_2_short_term': [],
            'phase_3_medium_term': []
        }
        
        # Phase 1: Immediate adjustments
        if requirements.get('position_sizing_adjustment', 0) != 0:
            phases['phase_1_immediate'].append('adjust_position_sizing')
        
        if requirements.get('volatility_adjustment', 0) > 0.2:
            phases['phase_1_immediate'].append('tighten_risk_controls')
        
        # Phase 2: Short-term adjustments (1-3 months)
        if requirements['strategy_rotation']:
            phases['phase_2_short_term'].extend([
                rot['from'] + '_to_' + rot['to'] 
                for rot in requirements['strategy_rotation'] 
                if rot['priority'] in ['high', 'medium']
            ])
        
        # Phase 3: Medium-term adjustments (3-6 months)
        if requirements.get('time_horizon_adjustment', 0) != 0:
            phases['phase_3_medium_term'].append('adjust_investment_horizon')
        
        return phases
    
    def _recommend_monitoring_frequency(self, requirements: dict) -> str:
        """
        Monitoring frequency recommendation
        """
        
        # Increase monitoring during periods of high adaptation requirements
        total_adjustment = sum([
            abs(requirements.get('position_sizing_adjustment', 0)),
            abs(requirements.get('volatility_adjustment', 0)),
            abs(requirements.get('risk_tolerance_adjustment', 0))
        ])
        
        if total_adjustment > 0.5:
            return 'daily'
        elif total_adjustment > 0.2:
            return 'weekly'
        else:
            return 'monthly'
    
    def _recommend_review_schedule(self, requirements: dict) -> dict:
        """
        Review schedule recommendation
        """
        
        return {
            'next_review_date': pd.Timestamp.now() + pd.Timedelta(days=30),
            'review_frequency': 'monthly' if any(abs(req) > 0.3 for req in requirements.values() if isinstance(req, float)) else 'quarterly',
            'trigger_conditions': [
                'position_sizing_change > 20%',
                'major_cycle_phase_change',
                'policy_stance_shift'
            ]
        }
    
    def _optimize_adaptations(self, 
                            recommendations: dict,
                            economic_data: pd.DataFrame,
                            strategy_config: dict) -> dict:
        """
        Adaptation optimization
        """
        
        optimized = {}
        
        # Parameter optimization
        optimized['parameters'] = self._optimize_parameters(
            recommendations['parameter_adjustments'], 
            economic_data,
            strategy_config
        )
        
        # Position optimization
        optimized['positions'] = self._optimize_positions(
            recommendations['position_adjustments'],
            economic_data
        )
        
        # Risk optimization
        optimized['risk'] = self._optimize_risk_management(
            recommendations['risk_adjustments'],
            economic_data
        )
        
        # Timing optimization
        optimized['timing'] = self._optimize_timing(
            recommendations['timing_recommendations'],
            economic_data
        )
        
        # Overall optimization score
        optimized['optimization_score'] = self._calculate_optimization_score(optimized)
        
        return optimized
    
    def _optimize_parameters(self, parameter_adj: dict, economic_data: pd.DataFrame, strategy_config: dict) -> dict:
        """
        Parameter optimization
        """
        
        # Simplified parameter optimization using historical relationships
        optimized_params = {}
        
        for param_name, param_data in parameter_adj.items():
            recommended_value = param_data['recommended']
            
            # Apply bounds and constraints
            if param_name == 'position_sizing':
                optimized_value = max(0.1, min(2.0, recommended_value))  # 10%-200% bounds
            elif param_name == 'risk_tolerance':
                optimized_value = max(0.1, min(1.0, recommended_value))  # 10%-100% bounds
            elif param_name == 'time_horizon':
                optimized_value = max(1, min(60, recommended_value))     # 1-60 months bounds
            else:
                optimized_value = recommended_value
            
            optimized_params[param_name] = {
                'optimized_value': optimized_value,
                'confidence': param_data['confidence'],
                'optimization_notes': 'bounds_applied' if optimized_value != recommended_value else 'no_bounds_applied'
            }
        
        return optimized_params
    
    def _optimize_positions(self, position_adj: dict, economic_data: pd.DataFrame) -> dict:
        """
        Position optimization
        """
        
        optimized_positions = {}
        
        if 'strategy_rotations' in position_adj:
            rotations = position_adj['strategy_rotations']
            
            # Optimize rotation timing and size
            for rotation in rotations:
                optimized_rotation = {
                    'from_asset': rotation['from_asset'],
                    'to_asset': rotation['to_asset'],
                    'optimized_allocation': self._calculate_optimal_allocation(rotation, economic_data),
                    'implementation_timeline': self._optimize_rotation_timeline(rotation),
                    'risk_considerations': self._assess_rotation_risks(rotation)
                }
                optimized_positions[f"rotation_{rotation['from_asset']}_to_{rotation['to_asset']}"] = optimized_rotation
        
        return optimized_positions
    
    def _optimize_risk_management(self, risk_adj: dict, economic_data: pd.DataFrame) -> dict:
        """
        Risk management optimization
        """
        
        optimized_risk = {}
        
        # Hedge optimization
        if 'hedge_recommendations' in risk_adj:
            hedges = risk_adj['hedge_recommendations']
            optimized_hedges = []
            
            for hedge in hedges:
                optimal_allocation = self._calculate_optimal_hedge_allocation(hedge, economic_data)
                optimized_hedge = {
                    'hedge_type': hedge['hedge_type'],
                    'optimal_allocation': optimal_allocation,
                    'instruments': hedge['instruments'],
                    'cost_benefit': self._analyze_hedge_cost_benefit(hedge, economic_data)
                }
                optimized_hedges.append(optimized_hedge)
            
            optimized_risk['hedges'] = optimized_hedges
        
        return optimized_risk
    
    def _optimize_timing(self, timing_adj: dict, economic_data: pd.DataFrame) -> dict:
        """
        Timing optimization
        """
        
        optimized_timing = {}
        
        # Optimize implementation timing
        if 'phased_implementation' in timing_adj:
            phases = timing_adj['phased_implementation']
            
            optimized_timing['implementation_schedule'] = {
                'phase_1': self._optimize_phase_timing(phases['phase_1_immediate']),
                'phase_2': self._optimize_phase_timing(phases['phase_2_short_term']),
                'phase_3': self._optimize_phase_timing(phases['phase_3_medium_term'])
            }
        
        optimized_timing['monitoring_enhanced'] = {
            'frequency': timing_adj['monitoring_frequency'],
            'key_indicators': self._identify_key_monitoring_indicators(),
            'alert_thresholds': self._define_alert_thresholds()
        }
        
        return optimized_timing
    
    def _calculate_optimal_allocation(self, rotation: dict, economic_data: pd.DataFrame) -> dict:
        """
        Optimal allocation calculation for rotations
        """
        
        # Simplified allocation calculation
        base_allocation = 0.1  # 10% base rotation size
        
        # Adjust based on cycle conditions
        if 'growth' in economic_data.columns:
            growth_momentum = economic_data['growth'].tail(6).mean() - economic_data['growth'].head(6).mean()
            if growth_momentum > 0:
                allocation = base_allocation * 1.2  # Increase allocation during positive momentum
            else:
                allocation = base_allocation * 0.8  # Decrease allocation during negative momentum
        else:
            allocation = base_allocation
        
        return {
            'recommended_allocation': min(allocation, 0.2),  # Cap at 20%
            'allocation_rationale': 'growth_momentum_adjusted' if 'growth' in economic_data.columns else 'default_allocation'
        }
    
    def _optimize_rotation_timeline(self, rotation: dict) -> dict:
        """
        Rotation timeline optimization
        """
        
        priority_timeline = {
            'high': {'start_days': 1, 'completion_days': 7},
            'medium': {'start_days': 7, 'completion_days': 30},
            'low': {'start_days': 30, 'completion_days': 90}
        }
        
        timeline = priority_timeline.get(rotation['priority'], priority_timeline['medium'])
        
        return {
            'start_date': pd.Timestamp.now() + pd.Timedelta(days=timeline['start_days']),
            'completion_date': pd.Timestamp.now() + pd.Timedelta(days=timeline['completion_days']),
            'timeline_rationale': f'based_on_{rotation["priority"]}_priority'
        }
    
    def _assess_rotation_risks(self, rotation: dict) -> dict:
        """
        Rotation risk assessment
        """
        
        # Risk factors for different rotations
        risk_factors = {
            'growth_to_defensive': ['opportunity_cost', 'timing_risk', 'market_impact'],
            'nominal_to_tips': ['tracking_error', 'liquidity_risk', 'duration_risk'],
            'govt_to_corp': ['credit_risk', 'spread_risk', 'call_risk']
        }
        
        rotation_key = rotation['from_asset'] + '_to_' + rotation['to_asset']
        relevant_risks = risk_factors.get(rotation_key, ['general_timing_risk'])
        
        return {
            'identified_risks': relevant_risks,
            'risk_mitigation': self._recommend_risk_mitigation(relevant_risks),
            'overall_risk_level': 'medium' if len(relevant_risks) <= 2 else 'high'
        }
    
    def _recommend_risk_mitigation(self, risks: list) -> list:
        """
        Risk mitigation recommendations
        """
        
        mitigation_strategies = {
            'timing_risk': 'implement_over_time_rather_than_lump_sum',
            'opportunity_cost': 'monitor_performance_and_adjust_quickly',
            'liquidity_risk': 'use_liquid_instruments_and_allow_time_for_transition',
            'credit_risk': 'focus_on_high_quality_credits_initially'
        }
        
        return [mitigation_strategies.get(risk, 'standard_risk_management') for risk in risks]
    
    def _calculate_optimal_hedge_allocation(self, hedge: dict, economic_data: pd.DataFrame) -> dict:
        """
        Optimal hedge allocation calculation
        """
        
        # Base hedge allocation
        base_allocation = 0.05  # 5% base
        
        # Adjust based on economic conditions
        if hedge['hedge_type'] == 'inflation_protection':
            if 'inflation' in economic_data.columns:
                inflation_level = economic_data['inflation'].iloc[-1]
                if inflation_level > 0.03:  # >3% inflation
                    allocation = base_allocation * 1.5  # 7.5%
                else:
                    allocation = base_allocation
            else:
                allocation = base_allocation
        elif hedge['hedge_type'] == 'credit_protection':
            allocation = base_allocation * 1.2  # 6%
        else:
            allocation = base_allocation
        
        return {
            'recommended_allocation': min(allocation, 0.15),  # Cap at 15%
            'allocation_basis': 'economic_conditions_adjusted'
        }
    
    def _analyze_hedge_cost_benefit(self, hedge: dict, economic_data: pd.DataFrame) -> dict:
        """
        Hedge cost-benefit analysis
        """
        
        # Simplified cost-benefit analysis
        cost_factors = {
            'hedge_type': hedge['hedge_type'],
            'estimated_cost': 'annual_cost_as_percentage',
            'expected_benefit': 'risk_reduction_estimated',
            'cost_effectiveness': 'high'  # Would need more detailed analysis
        }
        
        return cost_factors
    
    def _optimize_phase_timeline(self, phase_actions: list) -> dict:
        """
        Phase timeline optimization
        """
        
        if not phase_actions:
            return {'actions': [], 'timeline': 'no_actions'}
        
        # Optimize timing for phase actions
        optimized_timeline = {
            'total_actions': len(phase_actions),
            'estimated_completion_days': len(phase_actions) * 3,  # 3 days per action
            'priority_actions': [action for action in phase_actions if any(word in action.lower() for word in ['position', 'risk'])],
            'sequential_vs_parallel': 'parallel_when_possible'
        }
        
        return optimized_timeline
    
    def _identify_key_monitoring_indicators(self) -> list:
        """
        Key monitoring indicators identification
        """
        
        return [
            'gdp_growth_rate',
            'inflation_rate', 
            'interest_rate_level',
            'credit_spreads',
            'equity_market_performance',
            'volatility_indices'
        ]
    
    def _define_alert_thresholds(self) -> dict:
        """
        Alert thresholds definition
        """
        
        return {
            'economic_data_changes': 'monthly_review_required',
            'performance_deviation': '10%_from_target',
            'volatility_spike': 'volatility_above_2x_historical_average',
            'policy_changes': 'immediate_review_required'
        }
    
    def _calculate_optimization_score(self, optimized_adaptations: dict) -> float:
        """
        Optimization score calculation
        """
        
        # Simplified optimization scoring
        score_components = []
        
        # Parameter optimization score
        if 'parameters' in optimized_adaptations:
            param_count = len(optimized_adaptations['parameters'])
            param_score = min(param_count * 0.2, 1.0)  # Each parameter adds 0.2, max 1.0
            score_components.append(param_score)
        
        # Position optimization score
        if 'positions' in optimized_adaptations:
            pos_count = len(optimized_adaptations['positions'])
            pos_score = min(pos_count * 0.15, 0.8)  # Each position adds 0.15, max 0.8
            score_components.append(pos_score)
        
        # Risk optimization score
        if 'risk' in optimized_adaptations:
            score_components.append(0.6)  # Fixed score for risk optimization
        
        # Timing optimization score
        if 'timing' in optimized_adaptations:
            score_components.append(0.4)  # Fixed score for timing optimization
        
        return sum(score_components) if score_components else 0.0
    
    def _prioritize_implementations(self, optimized_adaptations: dict) -> dict:
        """
        Implementation prioritization
        """
        
        priorities = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': [],
            'optional': []
        }
        
        # High priority: Immediate parameter adjustments
        if 'parameters' in optimized_adaptations:
            for param_name, param_data in optimized_adaptations['parameters'].items():
                if param_data['confidence'] == 'high':
                    priorities['high_priority'].append(f'adjust_{param_name}')
                else:
                    priorities['medium_priority'].append(f'adjust_{param_name}')
        
        # Medium priority: Position rotations
        if 'positions' in optimized_adaptations:
            for pos_name in optimized_adaptations['positions'].keys():
                priorities['medium_priority'].append(f'implement_{pos_name}')
        
        # Low priority: Risk adjustments
        if 'risk' in optimized_adaptations:
            priorities['low_priority'].append('implement_risk_adjustments')
        
        return priorities
    
    def _assess_adaptation_risks(self, optimized_adaptations: dict) -> dict:
        """
        Adaptation risk assessment
        """
        
        risks = {
            'implementation_risk': self._assess_implementation_risk(optimized_adaptations),
            'timing_risk': self._assess_timing_risk(optimized_adaptations),
            'market_impact_risk': self._assess_market_impact_risk(optimized_adaptations),
            'performance_risk': self._assess_performance_risk(optimized_adaptations)
        }
        
        # Overall risk level
        risk_levels = [risk['risk_level'] for risk in risks.values() if isinstance(risk, dict) and 'risk_level' in risk]
        if 'high' in risk_levels:
            overall_risk = 'high'
        elif 'medium' in risk_levels:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        risks['overall_risk_level'] = overall_risk
        risks['risk_mitigation_recommendations'] = self._generate_risk_mitigation_recommendations(risks)
        
        return risks
    
    def _assess_implementation_risk(self, adaptations: dict) -> dict:
        """
        Implementation risk assessment
        """
        
        implementation_complexity = 0
        
        # Count number of adaptations
        adaptation_count = 0
        if 'parameters' in adaptations:
            adaptation_count += len(adaptations['parameters'])
        if 'positions' in adaptations:
            adaptation_count += len(adaptations['positions'])
        
        if adaptation_count > 5:
            complexity = 'high'
            risk_level = 'high'
        elif adaptation_count > 2:
            complexity = 'medium'
            risk_level = 'medium'
        else:
            complexity = 'low'
            risk_level = 'low'
        
        return {
            'complexity': complexity,
            'risk_level': risk_level,
            'recommendation': 'implement_gradually' if complexity == 'high' else 'implement_systematically'
        }
    
    def _assess_timing_risk(self, adaptations: dict) -> dict:
        """
        Timing risk assessment
        """
        
        # Assess based on economic uncertainty
        uncertainty_level = 'medium'  # Simplified
        
        timing_risks = {
            'high': 'market_timing_very_difficult',
            'medium': 'market_timing_challenging', 
            'low': 'market_timing_manageable'
        }
        
        return {
            'timing_difficulty': timing_risks[uncertainty_level],
            'risk_level': uncertainty_level,
            'recommendation': 'use_phased_implementation'
        }
    
    def _assess_market_impact_risk(self, adaptations: dict) -> dict:
        """
        Market impact risk assessment
        """
        
        # Large position changes could cause market impact
        position_changes = 0
        if 'positions' in adaptations:
            for pos_data in adaptations['positions'].values():
                if isinstance(pos_data, dict) and 'optimized_allocation' in pos_data:
                    allocation = pos_data['optimized_allocation'].get('recommended_allocation', 0)
                    position_changes += allocation
        
        if position_changes > 0.3:  # >30% total position changes
            risk_level = 'high'
            recommendation = 'implement_over_extended_period'
        elif position_changes > 0.15:  # >15% total changes
            risk_level = 'medium'
            recommendation = 'use_qualified_execution'
        else:
            risk_level = 'low'
            recommendation = 'standard_execution'
        
        return {
            'estimated_market_impact': position_changes,
            'risk_level': risk_level,
            'recommendation': recommendation
        }
    
    def _assess_performance_risk(self, adaptations: dict) -> dict:
        """
        Performance risk assessment
        """
        
        # Risk of underperforming during adaptation period
        return {
            'underperformance_risk': 'medium',
            'tracking_error_risk': 'low',
            'risk_level': 'medium',
            'recommendation': 'monitor_performance_closely_during_transition'
        }
    
    def _generate_risk_mitigation_recommendations(self, risks: dict) -> list:
        """
        Risk mitigation recommendations
        """
        
        recommendations = [
            'implement_adaptations_gradually_over_time',
            'maintain_detailed_performance_monitoring',
            'have_contingency_plans_for_rapid_reversals',
            'ensure_adequate_liquidity_for_position_changes'
        ]
        
        if risks.get('overall_risk_level') == 'high':
            recommendations.extend([
                'consider_paper_trading_adaptations_first',
                'consult_with_economic_advisors_before_major_changes'
            ])
        
        return recommendations
    
    def _estimate_adaptation_impact(self, optimized_adaptations: dict) -> dict:
        """
        Adaptation impact estimation
        """
        
        impact_estimates = {
            'expected_return_impact': self._estimate_return_impact(optimized_adaptations),
            'risk_impact': self._estimate_risk_impact(optimized_adaptations),
            'volatility_impact': self._estimate_volatility_impact(optimized_adaptations),
            'tracking_error_impact': self._estimate_tracking_error_impact(optimized_adaptations)
        }
        
        # Overall impact assessment
        impact_scores = [abs(impact) for impact in impact_estimates.values() if isinstance(impact, (int, float))]
        avg_impact = np.mean(impact_scores) if impact_scores else 0
        
        impact_estimates['overall_impact_level'] = (
            'high' if avg_impact > 0.15 else 
            'medium' if avg_impact > 0.05 else 
            'low'
        )
        
        return impact_estimates
    
    def _estimate_return_impact(self, adaptations: dict) -> float:
        """
        Expected return impact estimation
        """
        
        # Simplified return impact calculation
        return_impact = 0
        
        # Parameter adjustments impact
        if 'parameters' in adaptations:
            if 'position_sizing' in adaptations['parameters']:
                sizing_impact = adaptations['parameters']['position_sizing']['optimized_value'] - 1.0
                return_impact += sizing_impact * 0.1  # 10% of sizing change
        
        # Position rotation impact
        if 'positions' in adaptations:
            rotation_count = len(adaptations['positions'])
            return_impact += rotation_count * 0.01  # 1% per rotation
        
        return min(return_impact, 0.2)  # Cap at 20%
    
    def _estimate_risk_impact(self, adaptations: dict) -> float:
        """
        Risk impact estimation
        """
        
        risk_impact = 0
        
        # Volatility adjustment impact
        if 'parameters' in adaptations and 'volatility_adjustment' in adaptations['parameters']:
            vol_impact = adaptations['parameters']['volatility_adjustment']['optimized_value'] - 1.0
            risk_impact += abs(vol_impact) * 0.5
        
        return risk_impact
    
    def _estimate_volatility_impact(self, adaptations: dict) -> float:
        """
        Volatility impact estimation
        """
        
        volatility_impact = 0
        
        if 'parameters' in adaptations and 'volatility_adjustment' in adaptations['parameters']:
            vol_adjustment = adaptations['parameters']['volatility_adjustment']['optimized_value']
            volatility_impact = vol_adjustment - 1.0
        
        return volatility_impact
    
    def _estimate_tracking_error_impact(self, adaptations: dict) -> float:
        """
        Tracking error impact estimation
        """
        
        # Implementation could cause tracking error
        tracking_impact = 0
        
        if 'positions' in adaptations:
            position_count = len(adaptations['positions'])
            tracking_impact = position_count * 0.02  # 2% per position change
        
        return tracking_impact
    
    def _track_adaptation_decision(self, adaptation_results: dict):
        """
        Adaptation decision tracking
        """
        
        decision_record = {
            'timestamp': pd.Timestamp.now(),
            'cycle_detection': adaptation_results.get('cycle_detection', {}),
            'policy_analysis': adaptation_results.get('policy_analysis', {}),
            'recommendations_summary': {
                'parameter_changes': len(adaptations.get('optimized_adaptations', {}).get('parameters', {})),
                'position_changes': len(adaptations.get('optimized_adaptations', {}).get('positions', {})),
                'overall_risk_level': adaptation_results.get('risk_assessment', {}).get('overall_risk_level', 'unknown')
            }
        }
        
        self.adaptation_history.append(decision_record)
        
        # Update current cycle states
        if 'cycle_detection' in adaptation_results:
            cycle_detection = adaptation_results['cycle_detection']
            
            if 'interest_rate' in cycle_detection:
                self.current_interest_cycle = cycle_detection['interest_rate']['cycle']
            if 'inflation' in cycle_detection:
                self.current_inflation_cycle = cycle_detection['inflation']['cycle']
            if 'credit' in cycle_detection:
                self.current_credit_cycle = cycle_detection['credit']['cycle']
            if 'growth' in cycle_detection:
                self.current_growth_cycle = cycle_detection['growth']['cycle']
    
    def get_adaptation_status(self) -> dict:
        """
        Current adaptation status olish
        """
        
        return {
            'current_cycles': {
                'interest_rate': self.current_interest_cycle,
                'inflation': self.current_inflation_cycle,
                'credit': self.current_credit_cycle,
                'growth': self.current_growth_cycle
            },
            'current_parameters': self.adaptation_parameters,
            'adaptation_history_count': len(self.adaptation_history),
            'last_adaptation': self.adaptation_history[-1] if self.adaptation_history else None,
            'performance_by_cycle': self.performance_by_cycle
        }