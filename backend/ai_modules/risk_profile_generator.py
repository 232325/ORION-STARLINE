"""
Risk Profile Generator
======================

AI-powered risk profiling system for investment decision support.
This module provides comprehensive risk assessment and profile generation capabilities.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import json
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskProfileType(Enum):
    """Risk profile classification types"""
    CONSERVATIVE = "conservative"
    MODERATELY_CONSERVATIVE = "moderately_conservative"
    MODERATE = "moderate"
    MODERATELY_AGGRESSIVE = "moderately_aggressive"
    AGGRESSIVE = "aggressive"
    ULTRA_AGGRESSIVE = "ultra_aggressive"
    CUSTOM = "custom"

@dataclass
class RiskAssessment:
    """Risk assessment data structure"""
    risk_tolerance_score: float
    experience_level: str
    financial_situation_score: float
    behavioral_score: float
    investment_horizon: str
    liquidity_need: str
    loss_response: str
    decision_style: str
    confidence_level: float

@dataclass
class UserProfile:
    """Complete user risk profile"""
    user_id: str
    profile_type: RiskProfileType
    risk_score: float
    assessment: RiskAssessment
    investment_goals: List[str]
    time_horizon: int  # months
    liquidity_need: str
    risk_capacity: float
    behavioral_biases: Dict[str, float]
    recommendations: List[str]
    last_updated: datetime
    confidence_level: float
    version: str = "1.0"

class RiskProfileGenerator:
    """AI-powered risk profile generator"""
    
    def __init__(self):
        """Initialize the risk profile generator"""
        self.profile_weights = {
            'risk_tolerance': 0.25,
            'experience': 0.20,
            'financial_situation': 0.20,
            'behavioral': 0.15,
            'investment_goals': 0.10,
            'liquidity_need': 0.05,
            'decision_style': 0.05
        }
        
        # Initialize ML model for risk assessment
        self.ml_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_model_trained = False
        
        # Profile type configurations
        self.profile_configs = {
            RiskProfileType.CONSERVATIVE: {
                'risk_range': (0, 20),
                'max_volatility': 5.0,
                'expected_return': 4.0,
                'max_loss': 5.0,
                'diversification': 'high'
            },
            RiskProfileType.MODERATELY_CONSERVATIVE: {
                'risk_range': (20, 40),
                'max_volatility': 8.0,
                'expected_return': 6.0,
                'max_loss': 8.0,
                'diversification': 'high'
            },
            RiskProfileType.MODERATE: {
                'risk_range': (40, 60),
                'max_volatility': 12.0,
                'expected_return': 8.0,
                'max_loss': 12.0,
                'diversification': 'medium'
            },
            RiskProfileType.MODERATELY_AGGRESSIVE: {
                'risk_range': (60, 75),
                'max_volatility': 15.0,
                'expected_return': 10.0,
                'max_loss': 15.0,
                'diversification': 'medium'
            },
            RiskProfileType.AGGRESSIVE: {
                'risk_range': (75, 90),
                'max_volatility': 20.0,
                'expected_return': 12.0,
                'max_loss': 20.0,
                'diversification': 'low'
            },
            RiskProfileType.ULTRA_AGGRESSIVE: {
                'risk_range': (90, 100),
                'max_volatility': 30.0,
                'expected_return': 15.0,
                'max_loss': 30.0,
                'diversification': 'low'
            }
        }
    
    def assess_risk_tolerance(self, questionnaire_data: Dict[str, Any]) -> float:
        """
        Assess risk tolerance based on questionnaire responses
        
        Args:
            questionnaire_data: Survey responses and behavioral data
            
        Returns:
            Risk tolerance score (0-100)
        """
        try:
            # Risk tolerance questions scoring
            scores = []
            
            # Age factor
            age = questionnaire_data.get('age', 30)
            if age < 30:
                scores.append(80)  # Young, higher risk tolerance
            elif age < 50:
                scores.append(60)  # Middle-aged
            else:
                scores.append(40)  # Older, lower risk tolerance
            
            # Income stability
            income_stability = questionnaire_data.get('income_stability', 'medium')
            stability_scores = {
                'very_stable': 70,
                'stable': 60,
                'medium': 50,
                'unstable': 30,
                'very_unstable': 20
            }
            scores.append(stability_scores.get(income_stability, 50))
            
            # Emergency fund
            emergency_months = questionnaire_data.get('emergency_fund_months', 3)
            if emergency_months >= 12:
                scores.append(80)
            elif emergency_months >= 6:
                scores.append(70)
            elif emergency_months >= 3:
                scores.append(60)
            else:
                scores.append(30)
            
            # Investment experience
            experience_years = questionnaire_data.get('investment_experience_years', 0)
            if experience_years >= 10:
                scores.append(80)
            elif experience_years >= 5:
                scores.append(70)
            elif experience_years >= 2:
                scores.append(60)
            elif experience_years >= 1:
                scores.append(50)
            else:
                scores.append(40)
            
            # Risk perception questions
            risk_questions = questionnaire_data.get('risk_questions', [])
            for answer in risk_questions:
                if isinstance(answer, dict):
                    # Convert qualitative answers to numerical scores
                    if 'high_risk_high_reward' in str(answer).lower():
                        scores.append(75)
                    elif 'balanced' in str(answer).lower():
                        scores.append(60)
                    elif 'low_risk_low_return' in str(answer).lower():
                        scores.append(35)
            
            # Calculate average risk tolerance
            risk_tolerance = np.mean(scores) if scores else 50
            return min(100, max(0, risk_tolerance))
            
        except Exception as e:
            logger.error(f"Error assessing risk tolerance: {e}")
            return 50.0
    
    def analyze_financial_situation(self, financial_data: Dict[str, Any]) -> float:
        """
        Analyze financial situation to determine risk capacity
        
        Args:
            financial_data: Financial information (income, expenses, assets, etc.)
            
        Returns:
            Financial situation score (0-100)
        """
        try:
            scores = []
            
            # Income-to-expense ratio
            monthly_income = financial_data.get('monthly_income', 0)
            monthly_expenses = financial_data.get('monthly_expenses', 0)
            
            if monthly_income > 0:
                ratio = monthly_income / max(monthly_expenses, 1)
                if ratio >= 2.0:
                    scores.append(80)  # Strong financial position
                elif ratio >= 1.5:
                    scores.append(70)  # Good position
                elif ratio >= 1.2:
                    scores.append(60)  # Adequate position
                else:
                    scores.append(40)  # Tight budget
            
            # Net worth
            total_assets = financial_data.get('total_assets', 0)
            total_liabilities = financial_data.get('total_liabilities', 0)
            net_worth = total_assets - total_liabilities
            
            if net_worth > 1000000:  # 1M+
                scores.append(80)
            elif net_worth > 500000:  # 500K+
                scores.append(70)
            elif net_worth > 100000:  # 100K+
                scores.append(60)
            elif net_worth > 0:
                scores.append(50)
            else:
                scores.append(30)
            
            # Debt-to-income ratio
            debt_monthly = financial_data.get('monthly_debt_payments', 0)
            if monthly_income > 0:
                debt_ratio = debt_monthly / monthly_income
                if debt_ratio <= 0.1:
                    scores.append(80)
                elif debt_ratio <= 0.2:
                    scores.append(70)
                elif debt_ratio <= 0.3:
                    scores.append(60)
                else:
                    scores.append(40)
            
            # Investment capital available
            investment_amount = financial_data.get('available_investment_capital', 0)
            if investment_amount >= 100000:
                scores.append(80)
            elif investment_amount >= 50000:
                scores.append(70)
            elif investment_amount >= 10000:
                scores.append(60)
            else:
                scores.append(40)
            
            # Calculate average financial situation score
            financial_score = np.mean(scores) if scores else 50
            return min(100, max(0, financial_score))
            
        except Exception as e:
            logger.error(f"Error analyzing financial situation: {e}")
            return 50.0
    
    def evaluate_experience_level(self, experience_data: Dict[str, Any]) -> str:
        """
        Evaluate investment experience level
        
        Args:
            experience_data: Investment experience information
            
        Returns:
            Experience level string
        """
        try:
            investment_years = experience_data.get('investment_experience_years', 0)
            knowledge_score = experience_data.get('investment_knowledge_score', 0)
            asset_types = len(experience_data.get('asset_types_experienced', []))
            frequency = experience_data.get('trading_frequency', 'occasional')
            
            # Calculate composite experience score
            score = 0
            
            # Years of experience (30% weight)
            if investment_years >= 10:
                score += 30
            elif investment_years >= 5:
                score += 25
            elif investment_years >= 2:
                score += 20
            elif investment_years >= 1:
                score += 15
            else:
                score += 10
            
            # Knowledge score (30% weight)
            score += (knowledge_score / 100) * 30
            
            # Asset type experience (20% weight)
            score += min(asset_types * 5, 20)
            
            # Trading frequency (20% weight)
            frequency_scores = {
                'daily': 20,
                'weekly': 15,
                'monthly': 10,
                'quarterly': 8,
                'occasional': 5
            }
            score += frequency_scores.get(frequency, 5)
            
            # Classify experience level
            if score >= 80:
                return 'expert'
            elif score >= 60:
                return 'advanced'
            elif score >= 40:
                return 'intermediate'
            elif score >= 20:
                return 'beginner'
            else:
                return 'novice'
                
        except Exception as e:
            logger.error(f"Error evaluating experience level: {e}")
            return 'intermediate'
    
    def calculate_overall_risk_score(self, assessment: RiskAssessment) -> float:
        """
        Calculate overall risk score based on all factors
        
        Args:
            assessment: Complete risk assessment data
            
        Returns:
            Overall risk score (0-100)
        """
        try:
            # Weighted combination of all risk factors
            risk_score = (
                assessment.risk_tolerance_score * self.profile_weights['risk_tolerance'] +
                self._experience_to_score(assessment.experience_level) * self.profile_weights['experience'] +
                assessment.financial_situation_score * self.profile_weights['financial_situation'] +
                assessment.behavioral_score * self.profile_weights['behavioral'] +
                self._goals_to_score(assessment) * self.profile_weights['investment_goals'] +
                self._liquidity_to_score(assessment.liquidity_need) * self.profile_weights['liquidity_need'] +
                self._decision_style_to_score(assessment.decision_style) * self.profile_weights['decision_style']
            )
            
            return min(100, max(0, risk_score))
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 50.0
    
    def _experience_to_score(self, experience_level: str) -> float:
        """Convert experience level to numerical score"""
        experience_scores = {
            'expert': 85,
            'advanced': 70,
            'intermediate': 55,
            'beginner': 40,
            'novice': 25
        }
        return experience_scores.get(experience_level, 50)
    
    def _goals_to_score(self, assessment: RiskAssessment) -> float:
        """Convert investment goals to risk score"""
        # Higher risk for growth-oriented goals
        goal_scores = {
            'capital_preservation': 20,
            'income_generation': 40,
            'balanced_growth': 60,
            'aggressive_growth': 80,
            'speculation': 95
        }
        return goal_scores.get(assessment.investment_goals, 50)
    
    def _liquidity_to_score(self, liquidity_need: str) -> float:
        """Convert liquidity need to risk score"""
        liquidity_scores = {
            'immediate': 20,
            'short_term': 35,
            'medium_term': 50,
            'long_term': 70,
            'no_liquidity_need': 85
        }
        return liquidity_scores.get(liquidity_need, 50)
    
    def _decision_style_to_score(self, decision_style: str) -> float:
        """Convert decision style to risk score"""
        style_scores = {
            'very_conservative': 25,
            'conservative': 35,
            'balanced': 50,
            'aggressive': 70,
            'very_aggressive': 85
        }
        return style_scores.get(decision_style, 50)
    
    def determine_profile_type(self, risk_score: float) -> RiskProfileType:
        """
        Determine risk profile type based on calculated risk score
        
        Args:
            risk_score: Overall risk score (0-100)
            
        Returns:
            RiskProfileType enum
        """
        for profile_type, config in self.profile_configs.items():
            risk_range = config['risk_range']
            if risk_range[0] <= risk_score <= risk_range[1]:
                return profile_type
        
        return RiskProfileType.MODERATE  # Default fallback
    
    def generate_profile(
        self, 
        user_id: str,
        questionnaire_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        experience_data: Dict[str, Any],
        behavioral_data: Dict[str, Any],
        investment_goals: List[str]
    ) -> UserProfile:
        """
        Generate complete user risk profile
        
        Args:
            user_id: Unique user identifier
            questionnaire_data: Risk tolerance questionnaire responses
            financial_data: Financial information
            experience_data: Investment experience
            behavioral_data: Behavioral analysis data
            investment_goals: List of investment objectives
            
        Returns:
            Complete UserProfile object
        """
        try:
            # Perform individual assessments
            risk_tolerance = self.assess_risk_tolerance(questionnaire_data)
            financial_score = self.analyze_financial_situation(financial_data)
            experience_level = self.evaluate_experience_level(experience_data)
            behavioral_score = behavioral_data.get('behavioral_score', 50)
            investment_horizon = questionnaire_data.get('investment_horizon_years', 5) * 12
            liquidity_need = questionnaire_data.get('liquidity_need', 'medium_term')
            loss_response = behavioral_data.get('loss_response_pattern', 'moderate')
            decision_style = behavioral_data.get('decision_making_style', 'balanced')
            
            # Create risk assessment
            assessment = RiskAssessment(
                risk_tolerance_score=risk_tolerance,
                experience_level=experience_level,
                financial_situation_score=financial_score,
                behavioral_score=behavioral_score,
                investment_horizon=f"{investment_horizon//12} yil" if investment_horizon >= 12 else f"{investment_horizon} oy",
                liquidity_need=liquidity_need,
                loss_response=loss_response,
                decision_style=decision_style,
                confidence_level=0.85  # Initial confidence
            )
            
            # Calculate overall risk score
            risk_score = self.calculate_overall_risk_score(assessment)
            
            # Determine profile type
            profile_type = self.determine_profile_type(risk_score)
            
            # Calculate risk capacity (max risk user can take)
            risk_capacity = min(financial_score, 100 - (assessment.risk_tolerance_score * 0.3))
            
            # Generate recommendations
            recommendations = self._generate_recommendations(profile_type, assessment)
            
            # Detect behavioral biases
            behavioral_biases = self._analyze_behavioral_biases(behavioral_data)
            
            # Create user profile
            profile = UserProfile(
                user_id=user_id,
                profile_type=profile_type,
                risk_score=risk_score,
                assessment=assessment,
                investment_goals=investment_goals,
                time_horizon=investment_horizon,
                liquidity_need=liquidity_need,
                risk_capacity=risk_capacity,
                behavioral_biases=behavioral_biases,
                recommendations=recommendations,
                last_updated=datetime.now(),
                confidence_level=assessment.confidence_level
            )
            
            logger.info(f"Generated risk profile for user {user_id}: {profile_type.value} (score: {risk_score})")
            return profile
            
        except Exception as e:
            logger.error(f"Error generating profile: {e}")
            # Return default profile
            return self._create_default_profile(user_id)
    
    def _analyze_behavioral_biases(self, behavioral_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze behavioral biases from trading data"""
        biases = {
            'loss_aversion': behavioral_data.get('loss_aversion_score', 50),
            'overconfidence': behavioral_data.get('overconfidence_score', 50),
            'recency_bias': behavioral_data.get('recency_bias_score', 50),
            'anchoring_effect': behavioral_data.get('anchoring_score', 50),
            'mental_accounting': behavioral_data.get('mental_accounting_score', 50),
            'herding_behavior': behavioral_data.get('herding_score', 50),
            'confirmation_bias': behavioral_data.get('confirmation_bias_score', 50)
        }
        return biases
    
    def _generate_recommendations(self, profile_type: RiskProfileType, assessment: RiskAssessment) -> List[str]:
        """Generate personalized investment recommendations"""
        recommendations = []
        
        # Base recommendations by profile type
        if profile_type == RiskProfileType.CONSERVATIVE:
            recommendations.extend([
                "Yuqori sifatli obligatsiyalarga e'tibor qaratish",
                "Dividend to'lovchi aktsiyalarni tanlash",
                "Kichik hajmli va boshqariladigan portfoll yaratish",
                "Moliyaviy maslahat olishni ko'rib chiqish"
            ])
        elif profile_type == RiskProfileType.AGGRESSIVE:
            recommendations.extend([
                "Tez o'sadigan texnologiya sektoriga investitsiya qilish",
                "Tovar bozorlarida diversifikatsiya qilish",
                "Forreign investitsiyalarni ko'rib chiqish",
                "Yuqori potentsial bor startaplarga o'ylab qarash"
            ])
        else:
            recommendations.extend([
                "Diversifikatsiyalangan portfel yaratish",
                "Regulyar rebalans qilish",
                "Investitsiya maqsadlarini qayta ko'rib chiqish",
                "Xavf boshqaruv strategiyalarni o'rganish"
            ])
        
        # Experience-based recommendations
        if assessment.experience_level in ['beginner', 'novice']:
            recommendations.append("Investitsiya bo'yicha ta'lim olish")
        elif assessment.experience_level == 'expert':
            recommendations.append("Murakkab moliyaviy vositalarni o'rganish")
        
        # Behavioral recommendations
        if assessment.behavioral_score < 40:
            recommendations.append("Xavfni kamaytirish strategiyalarini qo'llash")
        elif assessment.behavioral_score > 80:
            recommendations.append("Yuqori xavfli investitsiyalarni o'lchab baholash")
        
        return recommendations
    
    def _create_default_profile(self, user_id: str) -> UserProfile:
        """Create default profile for error cases"""
        return UserProfile(
            user_id=user_id,
            profile_type=RiskProfileType.MODERATE,
            risk_score=50.0,
            assessment=RiskAssessment(
                risk_tolerance_score=50.0,
                experience_level='intermediate',
                financial_situation_score=50.0,
                behavioral_score=50.0,
                investment_horizon="5 yil",
                liquidity_need='medium_term',
                loss_response='moderate',
                decision_style='balanced',
                confidence_level=0.5
            ),
            investment_goals=['balanced_growth'],
            time_horizon=60,
            liquidity_need='medium_term',
            risk_capacity=50.0,
            behavioral_biases={bias: 50.0 for bias in [
                'loss_aversion', 'overconfidence', 'recency_bias', 
                'anchoring_effect', 'mental_accounting', 'herding_behavior', 'confirmation_bias'
            ]},
            recommendations=['Standart diversifyatsiyalangan portfel'],
            last_updated=datetime.now(),
            confidence_level=0.5
        )
    
    def update_profile(self, existing_profile: UserProfile, new_data: Dict[str, Any]) -> UserProfile:
        """
        Update existing profile with new data
        
        Args:
            existing_profile: Current user profile
            new_data: New assessment data
            
        Returns:
            Updated UserProfile object
        """
        try:
            # Update risk score based on new data
            if 'questionnaire_data' in new_data:
                risk_tolerance = self.assess_risk_tolerance(new_data['questionnaire_data'])
                existing_profile.assessment.risk_tolerance_score = risk_tolerance
            
            if 'financial_data' in new_data:
                financial_score = self.analyze_financial_situation(new_data['financial_data'])
                existing_profile.assessment.financial_situation_score = financial_score
            
            if 'behavioral_data' in new_data:
                behavioral_score = new_data['behavioral_data'].get('behavioral_score', 50)
                existing_profile.assessment.behavioral_score = behavioral_score
                
                # Update behavioral biases
                new_biases = self._analyze_behavioral_biases(new_data['behavioral_data'])
                existing_profile.behavioral_biases.update(new_biases)
            
            # Recalculate overall risk score
            existing_profile.risk_score = self.calculate_overall_risk_score(existing_profile.assessment)
            
            # Update profile type if significant change
            new_profile_type = self.determine_profile_type(existing_profile.risk_score)
            if new_profile_type != existing_profile.profile_type:
                existing_profile.profile_type = new_profile_type
                existing_profile.recommendations = self._generate_recommendations(
                    new_profile_type, existing_profile.assessment
                )
            
            # Update timestamp
            existing_profile.last_updated = datetime.now()
            
            logger.info(f"Updated profile for user {existing_profile.user_id}")
            return existing_profile
            
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return existing_profile
    
    def export_profile(self, profile: UserProfile, format: str = 'json') -> str:
        """
        Export user profile to specified format
        
        Args:
            profile: UserProfile to export
            format: Export format ('json', 'dict')
            
        Returns:
            Exported profile data
        """
        try:
            if format == 'dict':
                return asdict(profile)
            elif format == 'json':
                return json.dumps(asdict(profile), default=str, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting profile: {e}")
            return "{}"
    
    def train_ml_model(self, training_data: List[Dict[str, Any]]) -> bool:
        """
        Train machine learning model for risk assessment
        
        Args:
            training_data: Historical risk assessment data
            
        Returns:
            Success status
        """
        try:
            if len(training_data) < 50:
                logger.warning("Insufficient training data for ML model")
                return False
            
            # Prepare features and targets
            features = []
            targets = []
            
            for data in training_data:
                feature_vector = [
                    data.get('risk_tolerance', 0),
                    data.get('financial_score', 0),
                    data.get('experience_score', 0),
                    data.get('behavioral_score', 0),
                    data.get('age', 30),
                    data.get('income_stability', 0),
                    data.get('emergency_fund', 0)
                ]
                features.append(feature_vector)
                targets.append(data.get('profile_type', 'moderate'))
            
            # Convert to numpy arrays
            X = np.array(features)
            y = np.array(targets)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.ml_model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            accuracy = self.ml_model.score(X_test_scaled, y_test)
            logger.info(f"ML model trained with accuracy: {accuracy:.3f}")
            
            self.is_model_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            return False
    
    def predict_profile_ml(self, user_data: Dict[str, Any]) -> str:
        """
        Predict risk profile using trained ML model
        
        Args:
            user_data: User assessment data
            
        Returns:
            Predicted profile type
        """
        try:
            if not self.is_model_trained:
                logger.warning("ML model not trained, using rule-based prediction")
                return 'moderate'
            
            # Prepare feature vector
            feature_vector = np.array([[
                user_data.get('risk_tolerance', 0),
                user_data.get('financial_score', 0),
                user_data.get('experience_score', 0),
                user_data.get('behavioral_score', 0),
                user_data.get('age', 30),
                user_data.get('income_stability', 0),
                user_data.get('emergency_fund', 0)
            ]])
            
            # Scale and predict
            feature_vector_scaled = self.scaler.transform(feature_vector)
            prediction = self.ml_model.predict(feature_vector_scaled)[0]
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return 'moderate'

# Example usage and testing
if __name__ == "__main__":
    # Initialize risk profile generator
    generator = RiskProfileGenerator()
    
    # Sample user data
    sample_questionnaire = {
        'age': 35,
        'income_stability': 'stable',
        'emergency_fund_months': 8,
        'investment_experience_years': 3,
        'risk_questions': ['high_risk_high_reward', 'balanced'],
        'investment_horizon_years': 10,
        'liquidity_need': 'long_term'
    }
    
    sample_financial = {
        'monthly_income': 8000,
        'monthly_expenses': 5000,
        'total_assets': 150000,
        'total_liabilities': 30000,
        'monthly_debt_payments': 500,
        'available_investment_capital': 50000
    }
    
    sample_experience = {
        'investment_experience_years': 3,
        'investment_knowledge_score': 75,
        'asset_types_experienced': ['stocks', 'bonds', 'etf'],
        'trading_frequency': 'monthly'
    }
    
    sample_behavioral = {
        'behavioral_score': 65,
        'loss_response_pattern': 'moderate',
        'decision_making_style': 'balanced',
        'loss_aversion_score': 60,
        'overconfidence_score': 70,
        'recency_bias_score': 50
    }
    
    investment_goals = ['balanced_growth', 'retirement_planning']
    
    # Generate profile
    profile = generator.generate_profile(
        user_id="user_123",
        questionnaire_data=sample_questionnaire,
        financial_data=sample_financial,
        experience_data=sample_experience,
        behavioral_data=sample_behavioral,
        investment_goals=investment_goals
    )
    
    # Print results
    print(f"Generated Profile:")
    print(f"User ID: {profile.user_id}")
    print(f"Profile Type: {profile.profile_type.value}")
    print(f"Risk Score: {profile.risk_score:.2f}")
    print(f"Experience Level: {profile.assessment.experience_level}")
    print(f"Time Horizon: {profile.time_horizon} months")
    print(f"Risk Capacity: {profile.risk_capacity:.2f}")
    print("\nRecommendations:")
    for rec in profile.recommendations:
        print(f"- {rec}")
    
    # Export profile
    json_export = generator.export_profile(profile, 'json')
    print(f"\nJSON Export (first 200 chars): {json_export[:200]}...")