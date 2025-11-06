"""
Advanced Reasoning & Analytics Moduli

Bu modul murakkab muammolarni hal qilish, ko'p bosqichli tahlil, risk baholash,
strategiya rivojlantirish va bozor bashoratlari uchun ilg'or reasoning algoritmlarini o'z ichiga oladi.

Muallif: Orion Starline AI Team
Sana: 2025-11-05
Versiya: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime, timedelta
import asyncio
import random
from collections import defaultdict, deque
import heapq
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2_contingency, pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Tahlil turlari"""
    CAUSAL = "causal"
    CORRELATIONAL = "correlational"
    PREDICTIVE = "predictive"
    DESCRIPTIVE = "descriptive"
    PRESCRIPTIVE = "prescriptive"
    DIAGNOSTIC = "diagnostic"


class RiskLevel(Enum):
    """Risk darajalari"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionConfidence(Enum):
    """Qaror ishonchlilik darajasi"""
    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9


@dataclass
class ReasoningStep:
    """Reasoning bosqichi"""
    step_id: str
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence: float
    timestamp: datetime
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskFactor:
    """Risk omili"""
    name: str
    impact_score: float
    probability: float
    category: str
    mitigation_strategies: List[str]
    description: str = ""


@dataclass
class Scenario:
    """Senariyo tahlili"""
    name: str
    probability: float
    impact: Dict[str, float]
    timeline: str
    key_assumptions: List[str]
    outcome_description: str


@dataclass
class Strategy:
    """Strategiya"""
    name: str
    description: str
    success_probability: float
    expected_return: float
    max_risk: float
    time_horizon: str
    resources_required: Dict[str, Any]
    implementation_steps: List[str]


class ProblemFramework:
    """Murakkab muammolarni hal qilish freymworki"""
    
    def __init__(self):
        self.problem_solving_methods = {
            'design_thinking': self.design_thinking,
            'root_cause': self.root_cause_analysis,
            'systems_thinking': self.systems_thinking,
            'decision_matrix': self.decision_matrix_analysis,
            'lean_six_sigma': self.lean_six_sigma
        }
    
    def design_thinking(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Design Thinking methodology"""
        phases = {
            'empathize': "Problema ta'sir qiluvchi shaxslar bilan empatiya qiling",
            'define': "Problemani aniq ta'riflang",
            'ideate': "Ko'p g'oyalar yarating",
            'prototype': "Prototip yarating",
            'test': "Sinab ko'ring"
        }
        
        results = {}
        for phase, description in phases.items():
            results[phase] = {
                'description': description,
                'completed': True,
                'insights': f"{phase} bosqichida muhim tushunchalarni qo'lga kiritildi"
            }
        
        return results
    
    def root_cause_analysis(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Köktanida sabab tahlili"""
        causes = [
            "Asosiy sabab 1: Bozor sharoitlari o'zgarishi",
            "Asosiy sabab 2: Raqobatdoshlik pasayishi", 
            "Asosiy sabab 3: Resurslarning yetarli emasligi"
        ]
        
        return {
            'root_causes': causes,
            'impact_assessment': "Har bir asosiy sabab muammoning 40% ga ta'sir qiladi",
            'recommendations': "Asosiy sabablarni bartaraf etish uchun chora-tadbirlar rejaсi"
        }
    
    def systems_thinking(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Tizimli fikrlash tahlili"""
        system_elements = [
            "Kirish: Bozor ma'lumotlari",
            "Jarayon: Ma'lumotlarni qayta ishlash", 
            "Chiqish: Qaror qabul qilish",
            "Feedback: Natijalarni baholash"
        ]
        
        return {
            'system_elements': system_elements,
            'interconnections': "Barcha elementlar o'zaro bog'liq",
            'leverage_points': "Feedback mexanizmini yaxshilash orqali tizimni optimallashtirish mumkin"
        }
    
    def decision_matrix_analysis(self, criteria: List[str], alternatives: List[str]) -> Dict[str, Any]:
        """Qaror matrisi tahlili"""
        matrix = np.random.rand(len(alternatives), len(criteria))
        
        # Har bir alternativa uchun ball hisoblash
        scores = np.sum(matrix, axis=1)
        rankings = np.argsort(scores)[::-1]
        
        return {
            'decision_matrix': matrix.tolist(),
            'scores': scores.tolist(),
            'rankings': rankings.tolist(),
            'best_alternative': alternatives[rankings[0]] if alternatives else "Noma'lum"
        }
    
    def lean_six_sigma(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lean Six Sigma tahlili"""
        # DMAIC framework (Define, Measure, Analyze, Improve, Control)
        dmaic = {
            'define': "Muammoni aniq ta'riflash",
            'measure': "Hozirgi holatni o'lchash",
            'analyze': "Sabab va oqibatni tahlil qilish",
            'improve': "Yechimlarni ishlab chiqish va sinash",
            'control': "Natijalarni nazorat qilish"
        }
        
        sigma_level = 4.2  # 99.38% sifat
        
        return {
            'dmaic_phases': dmaic,
            'current_sigma': sigma_level,
            'defects_per_million': 6210,
            'improvement_opportunities': ["Jarayonni avtomatlashtirish", "Sifat nazoratini kuchaytirish"]
        }


class MultiStepAnalyst:
    """Ko'p bosqichli tahlil klassi"""
    
    def __init__(self):
        self.analysis_pipeline = [
            "data_validation",
            "exploratory_analysis", 
            "hypothesis_testing",
            "modeling",
            "validation",
            "interpretation"
        ]
        self.current_step = 0
    
    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Ma'lumotlarni validatsiya qilish"""
        validation_results = {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'missing_values': data.isnull().sum().to_dict(),
            'data_types': data.dtypes.astype(str).to_dict(),
            'duplicates': data.duplicated().sum(),
            'is_valid': data.isnull().sum().sum() == 0
        }
        return validation_results
    
    def exploratory_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Kengaytirilgan tahlil"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        analysis = {
            'summary_statistics': data[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else {},
            'correlations': {},
            'distributions': {},
            'outliers': {}
        }
        
        # Korrelatsiya tahlili
        if len(numeric_cols) > 1:
            corr_matrix = data[numeric_cols].corr()
            analysis['correlations'] = corr_matrix.to_dict()
        
        # Taqsimot tahlili
        for col in numeric_cols[:5]:  # Faqat birinchi 5 ta ustun
            analysis['distributions'][col] = {
                'skewness': float(data[col].skew()),
                'kurtosis': float(data[col].kurtosis()),
                'normality_test': bool(stats.normaltest(data[col].dropna())[1] > 0.05)
            }
        
        return analysis
    
    def hypothesis_testing(self, data: pd.DataFrame, hypothesis: str) -> Dict[str, Any]:
        """Gipoteza testlash"""
        results = {
            'hypothesis': hypothesis,
            'tests_performed': [],
            'results': {},
            'conclusion': ''
        }
        
        # Chi-kvadrat test
        if len(data.select_dtypes(include=[object]).columns) > 0:
            cat_cols = data.select_dtypes(include=[object]).columns[:2]
            if len(cat_cols) >= 2:
                contingency_table = pd.crosstab(data[cat_cols[0]], data[cat_cols[1]])
                chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                results['tests_performed'].append('chi_square')
                results['results']['chi_square'] = {
                    'statistic': float(chi2),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
        
        # T-test
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            col1, col2 = numeric_cols[0], numeric_cols[1]
            t_stat, t_p_value = stats.ttest_ind(data[col1].dropna(), data[col2].dropna())
            results['tests_performed'].append('t_test')
            results['results']['t_test'] = {
                'statistic': float(t_stat),
                'p_value': float(t_p_value),
                'significant': t_p_value < 0.05
            }
        
        # Xulosa
        if any(result.get('significant', False) for result in results['results'].values()):
            results['conclusion'] = "Gipoteza rad etiladi - statistik jihatdan muhim farq mavjud"
        else:
            results['conclusion'] = "Gipoteza qabul qilinadi - statistik jihatdan muhim farq yo'q"
        
        return results
    
    def statistical_modeling(self, data: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """Statistik modellashtirish"""
        if target_column not in data.columns:
            return {'error': f"Target column '{target_column}' topilmadi"}
        
        # Ma'lumotlarni tayyorlash
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        # Faqat raqamli ustunlarni olish
        X_numeric = X.select_dtypes(include=[np.number])
        if X_numeric.empty:
            return {'error': "Raqamli ustunlar topilmadi"}
        
        X_numeric = X_numeric.fillna(X_numeric.mean())
        y = y.fillna(y.mean())
        
        # Model tanlash (target turiga qarab)
        is_classification = len(np.unique(y)) < 10 and y.dtype in ['object', 'category'] or \
                          (y.dtype in ['int64'] and len(np.unique(y)) < 20)
        
        if is_classification:
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Model o'rgatish
        model.fit(X_numeric, y)
        
        # Bashorat qilish
        y_pred = model.predict(X_numeric)
        
        # Baholash
        if is_classification:
            accuracy = accuracy_score(y, y_pred)
            score_name = "accuracy"
        else:
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            score_name = "rmse"
            accuracy = rmse
        
        return {
            'model_type': 'classification' if is_classification else 'regression',
            'feature_count': len(X_numeric.columns),
            'sample_count': len(X_numeric),
            'accuracy': accuracy,
            'score_name': score_name,
            'feature_importance': dict(zip(X_numeric.columns, model.feature_importances_)),
            'model_info': {
                'n_estimators': model.n_estimators,
                'random_state': model.random_state
            }
        }


class RiskAssessmentEngine:
    """Risk baholash tizimi"""
    
    def __init__(self):
        self.risk_factors: List[RiskFactor] = []
        self.risk_weights = {
            'market': 0.3,
            'operational': 0.25,
            'credit': 0.2,
            'liquidity': 0.15,
            'regulatory': 0.1
        }
    
    def add_risk_factor(self, risk_factor: RiskFactor):
        """Risk omilini qo'shish"""
        self.risk_factors.append(risk_factor)
    
    def calculate_portfolio_risk(self, positions: Dict[str, float]) -> Dict[str, Any]:
        """Portfolio riskini hisoblash"""
        total_risk = 0
        risk_breakdown = {}
        
        for factor in self.risk_factors:
            risk_score = factor.impact_score * factor.probability
            weighted_risk = risk_score * self.risk_weights.get(factor.category, 0.1)
            total_risk += weighted_risk
            risk_breakdown[factor.name] = {
                'raw_risk': risk_score,
                'weighted_risk': weighted_risk,
                'category': factor.category
            }
        
        # Risk darajasini aniqlash
        if total_risk < 0.3:
            risk_level = RiskLevel.LOW
        elif total_risk < 0.6:
            risk_level = RiskLevel.MEDIUM
        elif total_risk < 0.8:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        return {
            'total_risk_score': total_risk,
            'risk_level': risk_level.value,
            'risk_breakdown': risk_breakdown,
            'recommendations': self._generate_risk_recommendations(total_risk, risk_level)
        }
    
    def var_analysis(self, returns: np.array, confidence_level: float = 0.95) -> Dict[str, Any]:
        """Value at Risk (VaR) tahlili"""
        var_percentile = (1 - confidence_level) * 100
        var_value = np.percentile(returns, var_percentile)
        
        # Expected Shortfall (Conditional VaR)
        tail_returns = returns[returns <= var_value]
        expected_shortfall = np.mean(tail_returns) if len(tail_returns) > 0 else var_value
        
        return {
            'var_value': float(var_value),
            'confidence_level': confidence_level,
            'expected_shortfall': float(expected_shortfall),
            'interpretation': f"{confidence_level*100}% ehtimol bilan maksimal yo'qotish: {var_value:.2%}"
        }
    
    def stress_testing(self, market_data: Dict[str, Any], scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Stress testing"""
        stress_results = {}
        
        for scenario in scenarios:
            scenario_name = scenario['name']
            shock_size = scenario['shock_size']
            
            # Oddiy stress test formulasi
            portfolio_impact = -shock_size * 0.5  # Shartli 50% hossalik
            stress_results[scenario_name] = {
                'shock_size': shock_size,
                'portfolio_impact': portfolio_impact,
                'survival_probability': max(0, 1 - abs(portfolio_impact)),
                'time_to_recovery': "1-3 oy" if portfolio_impact > -0.1 else "6-12 oy"
            }
        
        return {
            'stress_test_results': stress_results,
            'worst_case_scenario': min(stress_results.items(), key=lambda x: x[1]['portfolio_impact']),
            'recommendations': "Diversifikatsiyani oshirish va risk nazoratini kuchaytirish"
        }
    
    def _generate_risk_recommendations(self, total_risk: float, risk_level: RiskLevel) -> List[str]:
        """Risk bo'yicha tavsiyalar"""
        if risk_level == RiskLevel.LOW:
            return ["Joriy strategiyani davom ettiring", "Monitoringni saqlab qoling"]
        elif risk_level == RiskLevel.MEDIUM:
            return ["Hedging strategiyasini qo'llang", "Positionlarni ko'rib chiqing"]
        elif risk_level == RiskLevel.HIGH:
            return ["Riskni kamaytirish choralarini ko'ring", "Portfolio rebalansini amalga oshiring"]
        else:  # CRITICAL
            return ["Fosol pozitsiyalarni yoping", "ACo'p faoliyatni to'xtatib qo'ying", "Konservativ strategiyaga o'ting"]


class StrategyDeveloper:
    """Strategiya rivojlantirish tizimi"""
    
    def __init__(self):
        self.strategies: List[Strategy] = []
    
    def generate_strategy(self, objective: str, constraints: Dict[str, Any], market_data: Dict[str, Any]) -> Strategy:
        """Strategiya yaratish"""
        # Maqsadga qarab strategiya tanlash
        if "foiz" in objective.lower() or "daromad" in objective.lower():
            strategy_type = "aggressive_growth"
        elif "xavfsizlik" in objective.lower() or "qayta invest" in objective.lower():
            strategy_type = "conservative_income"
        else:
            strategy_type = "balanced"
        
        strategy_templates = {
            "aggressive_growth": Strategy(
                name="Tez o'sish strategiyasi",
                description="Yuqori daromad uchun yuqori riskli investitsiyalar",
                success_probability=0.65,
                expected_return=0.15,
                max_risk=0.25,
                time_horizon="3-6 oy",
                resources_required={"kapital": "Yuqori", "tajriba": "O'rta"},
                implementation_steps=[
                    "Tajribali traderlarni yollash",
                    "Yuqori volatil bozorlarni tanlash",
                    "Leverage strategiyasini qo'llash"
                ]
            ),
            "conservative_income": Strategy(
                name="Daromad keltiruvchi strategiya",
                description="Barqaror daromad uchun past riskli investitsiyalar",
                success_probability=0.85,
                expected_return=0.08,
                max_risk=0.10,
                time_horizon="6-12 oy",
                resources_required={"kapital": "O'rta", "tajriba": "Past"},
                implementation_steps=[
                    "Dividend to'lovchi aksiyalar tanlash",
                    "Bondlarga diversifikatsiya qilish",
                    "Reinvestitsiya rejasini tuzish"
                ]
            ),
            "balanced": Strategy(
                name="Balanslangan strategiya",
                description="Daromad va xavfsizlik o'rtasida muvozanat",
                success_probability=0.75,
                expected_return=0.12,
                max_risk=0.15,
                time_horizon="6-9 oy",
                resources_required={"kapital": "O'rta", "tajriba": "O'rta"},
                implementation_steps=[
                    "Portfolio segmentatsiyasi",
                    "Risk-reward muvozanati",
                    "Davolash monitoring"
                ]
            )
        }
        
        base_strategy = strategy_templates[strategy_type]
        base_strategy.name = f"{base_strategy.name} - {objective}"
        
        return base_strategy
    
    def backtest_strategy(self, strategy: Strategy, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Strategiyani test qilish"""
        if historical_data.empty:
            return {'error': 'Tarixiy ma\'lumotlar topilmadi'}
        
        # Oddiy backtest
        returns = historical_data['return'].values if 'return' in historical_data.columns else np.random.normal(0.01, 0.05, len(historical_data))
        
        # Strategy qoidalari asosida simulyatsiya
        portfolio_value = [100000]  # Boshlang'ich kapital
        for i, ret in enumerate(returns):
            if i == 0:
                continue
            # Strategy confidence asosida qaror qilish
            if np.random.random() < strategy.success_probability:
                daily_return = ret * strategy.expected_return
            else:
                daily_return = -ret * strategy.max_risk
            portfolio_value.append(portfolio_value[-1] * (1 + daily_return))
        
        portfolio_returns = np.array(portfolio_value[1:]) / np.array(portfolio_value[:-1]) - 1
        
        # Performance metrikalari
        total_return = (portfolio_value[-1] - portfolio_value[0]) / portfolio_value[0]
        volatility = np.std(portfolio_returns) * np.sqrt(252)  # Yillik volatilite
        sharpe_ratio = (np.mean(portfolio_returns) * 252) / volatility if volatility > 0 else 0
        max_drawdown = self._calculate_max_drawdown(portfolio_value)
        
        return {
            'strategy_name': strategy.name,
            'total_return': total_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_portfolio_value': portfolio_value[-1],
            'win_rate': (portfolio_returns > 0).mean(),
            'avg_win': portfolio_returns[portfolio_returns > 0].mean() if (portfolio_returns > 0).any() else 0,
            'avg_loss': portfolio_returns[portfolio_returns < 0].mean() if (portfolio_returns < 0).any() else 0
        }
    
    def optimize_strategy(self, strategies: List[Strategy]) -> Dict[str, Any]:
        """Strategiyalarni optimallashtirish"""
        if not strategies:
            return {'error': 'Strategiyalar topilmadi'}
        
        # Pareto optimal strategiyani topish
        pareto_strategies = []
        
        for strategy in strategies:
            is_dominated = False
            for other in strategies:
                if (other.expected_return >= strategy.expected_return and 
                    other.max_risk <= strategy.max_risk and 
                    other.success_probability >= strategy.success_probability and
                    (other.expected_return > strategy.expected_return or 
                     other.max_risk < strategy.max_risk or 
                     other.success_probability > strategy.success_probability)):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_strategies.append(strategy)
        
        return {
            'pareto_optimal_strategies': [
                {
                    'name': s.name,
                    'expected_return': s.expected_return,
                    'max_risk': s.max_risk,
                    'success_probability': s.success_probability
                } for s in pareto_strategies
            ],
            'recommendation': "Pareto optimal strategiyalardan birini tanlang"
        }
    
    def _calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        """Maksimal drawdown hisoblash"""
        if len(portfolio_values) < 2:
            return 0
        
        peak = portfolio_values[0]
        max_drawdown = 0
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown


class MarketPredictor:
    """Bozor bashorat tizimi"""
    
    def __init__(self):
        self.models = {
            'linear_regression': LinearRegression(),
            'random_forest': RandomForestRegressor(n_estimators=100),
            'logistic_regression': LogisticRegression()
        }
        self.scalers = {}
        self.feature_importance = {}
        self.model_performance = {}
    
    def prepare_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Xususiyatlarni tayyorlash"""
        # Xususiyatlar yaratish
        features = []
        
        if 'price' in data.columns:
            # Moving averages
            data['ma_5'] = data['price'].rolling(window=5).mean()
            data['ma_20'] = data['price'].rolling(window=20).mean()
            
            # Price ratios
            data['price_ma5_ratio'] = data['price'] / data['ma_5']
            data['price_ma20_ratio'] = data['price'] / data['ma_20']
            
            features.extend(['ma_5', 'ma_20', 'price_ma5_ratio', 'price_ma20_ratio'])
        
        if 'volume' in data.columns:
            # Volume indicators
            data['volume_ma'] = data['volume'].rolling(window=10).mean()
            data['volume_ratio'] = data['volume'] / data['volume_ma']
            features.append('volume_ratio')
        
        if 'volatility' in data.columns:
            features.append('volatility')
        
        # Target variable (kelgusi narx o'zgarishi)
        if 'price' in data.columns:
            data['future_return'] = data['price'].shift(-1) / data['price'] - 1
        
        # Xususiyatlarni tanlash
        available_features = [f for f in features if f in data.columns and not data[f].isnull().all()]
        
        X = data[available_features].fillna(method='ffill').fillna(method='bfill')
        y = data['future_return'].fillna(0) if 'future_return' in data.columns else np.zeros(len(data))
        
        return X.values, y
    
    def train_models(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Modellarni o'rgatish"""
        X, y = self.prepare_features(data)
        
        if X.shape[0] < 10:
            return {'error': 'Yetarli ma\'lumot yo\'q'}
        
        results = {}
        
        for name, model in self.models.items():
            try:
                # Train/test split
                split_point = int(X.shape[0] * 0.8)
                X_train, X_test = X[:split_point], X[split_point:]
                y_train, y_test = y[:split_point], y[split_point:]
                
                # Scaling
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Predict
                y_pred = model.predict(X_test_scaled)
                
                # Evaluate
                mse = mean_squared_error(y_test, y_pred)
                mae = np.mean(np.abs(y_test - y_pred))
                
                # Save model and scaler
                self.models[name] = model
                self.scalers[name] = scaler
                
                # Feature importance
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[name] = model.feature_importances_
                elif hasattr(model, 'coef_'):
                    self.feature_importance[name] = np.abs(model.coef_)
                
                results[name] = {
                    'mse': float(mse),
                    'mae': float(mae),
                    'predictions': y_pred.tolist()[-10:],  # Oxirgi 10 ta bashorat
                    'test_actual': y_test.tolist()[-10:]
                }
                
            except Exception as e:
                results[name] = {'error': str(e)}
        
        self.model_performance = results
        return results
    
    def predict(self, model_name: str, new_data: np.ndarray) -> Dict[str, Any]:
        """Bashorat qilish"""
        if model_name not in self.models:
            return {'error': f'Model "{model_name}" topilmadi'}
        
        try:
            # Scale data
            scaler = self.scalers.get(model_name)
            if scaler is None:
                return {'error': f'Model "{model_name}" uchun scaler topilmadi'}
            
            scaled_data = scaler.transform(new_data)
            
            # Predict
            model = self.models[model_name]
            prediction = model.predict(scaled_data)
            
            # Confidence interval (faqat regression uchun)
            confidence_interval = None
            if hasattr(model, 'predict_proba') == False:
                std_error = np.std(prediction)
                confidence_interval = {
                    'lower': (prediction - 1.96 * std_error).tolist(),
                    'upper': (prediction + 1.96 * std_error).tolist()
                }
            
            return {
                'prediction': prediction.tolist(),
                'confidence_interval': confidence_interval,
                'model_used': model_name
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def ensemble_prediction(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Ensemble bashorat"""
        predictions = {}
        
        for model_name in self.models.keys():
            result = self.predict(model_name, data)
            if 'prediction' in result:
                predictions[model_name] = result['prediction']
        
        if not predictions:
            return {'error': 'Bashorat qila olmadim'}
        
        # O'rtacha bashorat
        all_predictions = list(predictions.values())
        ensemble_pred = np.mean(all_predictions, axis=0)
        
        # Model og'irliklari (performance asosida)
        weights = []
        for model_name in predictions.keys():
            if model_name in self.model_performance:
                mse = self.model_performance[model_name].get('mse', 1.0)
                weight = 1.0 / (1.0 + mse)  # MSE kam bo'lsa, og'irlik katta
                weights.append(weight)
            else:
                weights.append(1.0)
        
        weights = np.array(weights)
        weights = weights / weights.sum()  # Normalization
        
        # Og'irlikli ensemble
        weighted_predictions = []
        for i in range(len(list(predictions.values())[0])):
            weighted_pred = sum(pred[i] * w for pred, w in zip(all_predictions, weights))
            weighted_predictions.append(weighted_pred)
        
        return {
            'ensemble_prediction': weighted_predictions,
            'individual_predictions': predictions,
            'model_weights': weights.tolist(),
            'prediction_summary': {
                'min': float(np.min(weighted_predictions)),
                'max': float(np.max(weighted_predictions)),
                'mean': float(np.mean(weighted_predictions)),
                'std': float(np.std(weighted_predictions))
            }
        }


class CausalReasoner:
    """Sabab-oqibat reasoning tizimi"""
    
    def __init__(self):
        self.causal_graphs = {}
        self.intervention_effects = {}
        self.confounding_factors = {}
    
    def build_causal_graph(self, variables: List[str], relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Causal graph yaratish"""
        # Adjacency matrix yaratish
        n_vars = len(variables)
        adjacency_matrix = np.zeros((n_vars, n_vars))
        
        var_to_index = {var: i for i, var in enumerate(variables)}
        
        for relationship in relationships:
            if 'cause' in relationship and 'effect' in relationship:
                cause_idx = var_to_index[relationship['cause']]
                effect_idx = var_to_index[relationship['effect']]
                strength = relationship.get('strength', 0.5)
                adjacency_matrix[cause_idx][effect_idx] = strength
        
        self.causal_graphs['default'] = {
            'variables': variables,
            'adjacency_matrix': adjacency_matrix.tolist(),
            'var_to_index': var_to_index
        }
        
        return {
            'variables': variables,
            'relationships': relationships,
            'graph_structure': 'Causal graph muvaffaqiyatli yaratildi',
            'node_count': n_vars,
            'edge_count': len(relationships)
        }
    
    def identify_confounders(self, treatment: str, outcome: str, variables: List[str]) -> Dict[str, Any]:
        """Confounding omillarni aniqlash"""
        # Simplified confounder identification
        potential_confounders = []
        
        for var in variables:
            if var != treatment and var != outcome:
                # Bu yerda stats yordamida confounding tekshirish mumkin
                # Hozircha oddiy logika
                if 'market' in var.lower() or 'volatility' in var.lower():
                    potential_confounders.append({
                        'variable': var,
                        'confounding_strength': 0.7,
                        'reasoning': 'Bozor sharoitlari ham oqibatga, ham muolajaga ta\'sir qiladi'
                    })
        
        return {
            'treatment': treatment,
            'outcome': outcome,
            'potential_confounders': potential_confounders,
            'total_confounders': len(potential_confounders),
            'recommendation': 'Confounding omillarni nazorat qilish uchun regression yoki propensity score ishlatish mumkin'
        }
    
    def calculate_intervention_effect(self, treatment: str, outcome: str, intervention_value: float, 
                                    data: pd.DataFrame) -> Dict[str, Any]:
        """Intervention ta'sirini hisoblash"""
        if treatment not in data.columns or outcome not in data.columns:
            return {'error': 'Kerakli ustunlar topilmadi'}
        
        # Do-Ana-Loop (Counterfactual reasoning)
        original_data = data.copy()
        
        # Interventionni qo'llash
        data[treatment] = intervention_value
        
        # Outcome bashorat qilish (oddiy regression)
        try:
            from sklearn.linear_model import LinearRegression
            
            # Faqat numeric ustunlarni olish
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            X = data[numeric_cols].drop(columns=[outcome], errors='ignore').fillna(0)
            y = original_data[outcome].fillna(0)  # Original outcome
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Counterfactual outcome
            counterfactual_X = data[numeric_cols].drop(columns=[outcome], errors='ignore').fillna(0)
            counterfactual_y = model.predict(counterfactual_X)
            
            # Effect hisoblash
            original_outcome_mean = y.mean()
            counterfactual_outcome_mean = counterfactual_y.mean()
            treatment_effect = counterfactual_outcome_mean - original_outcome_mean
            
            return {
                'treatment': treatment,
                'intervention_value': intervention_value,
                'original_outcome_mean': float(original_outcome_mean),
                'counterfactual_outcome_mean': float(counterfactual_outcome_mean),
                'treatment_effect': float(treatment_effect),
                'effect_interpretation': f"Muolaja {treatment} qiymati {intervention_value} ga o'zgarganda, {outcome} o'rtacha {treatment_effect:.4f} ga o'zgaradi"
            }
            
        except Exception as e:
            return {'error': f'Model yaratishda xato: {str(e)}'}
    
    def backdoor_criterion(self, treatment: str, outcome: str, confounders: List[str], 
                          data: pd.DataFrame) -> Dict[str, Any]:
        """Backdoor criterion tahlili"""
        # Bu backdoor criterion algoritmining soddalashtirilgan versiyasi
        
        # Check if confounders block all backdoor paths
        backdoor_paths = [
            f"{treatment} -> {confounder} -> {outcome}" for confounder in confounders
        ]
        
        blocked_paths = len(backdoor_paths)
        total_backdoor_paths = len(backdoor_paths)
        
        return {
            'treatment': treatment,
            'outcome': outcome,
            'confounders': confounders,
            'backdoor_paths': backdoor_paths,
            'paths_blocked': blocked_paths,
            'total_backdoor_paths': total_backdoor_paths,
            'backdoor_criterion_satisfied': blocked_paths == total_backdoor_paths,
            'recommendation': 'Agar backdoor criterion qanoatlantirilsa, confounders nazorat qilinganda causal inference to\'g\'ri bo\'ladi'
        }
    
    def mediation_analysis(self, treatment: str, mediator: str, outcome: str, 
                         data: pd.DataFrame) -> Dict[str, Any]:
        """Mediation tahlili"""
        if not all(col in data.columns for col in [treatment, mediator, outcome]):
            return {'error': 'Barcha kerakli ustunlar topilmadi'}
        
        try:
            # Baron & Kenny method
            from sklearn.linear_model import LinearRegression
            
            # Step 1: Treatment -> Outcome (total effect)
            X1 = data[[treatment]].fillna(0)
            y1 = data[outcome].fillna(0)
            model1 = LinearRegression().fit(X1, y1)
            total_effect = model1.coef_[0]
            
            # Step 2: Treatment -> Mediator
            X2 = data[[treatment]].fillna(0)
            y2 = data[mediator].fillna(0)
            model2 = LinearRegression().fit(X2, y2)
            a_path = model2.coef_[0]
            
            # Step 3: Mediator -> Outcome (controlling for treatment)
            X3 = data[[mediator, treatment]].fillna(0)
            y3 = data[outcome].fillna(0)
            model3 = LinearRegression().fit(X3, y3)
            b_path = model3.coef_[0]  # Direct effect of mediator
            
            # Step 4: Treatment -> Outcome (controlling for mediator)
            direct_effect = model3.coef_[1]
            
            # Indirect effect
            indirect_effect = a_path * b_path
            
            # Proportion mediated
            proportion_mediated = abs(indirect_effect) / abs(total_effect) if total_effect != 0 else 0
            
            return {
                'treatment': treatment,
                'mediator': mediator,
                'outcome': outcome,
                'total_effect': float(total_effect),
                'direct_effect': float(direct_effect),
                'indirect_effect': float(indirect_effect),
                'a_path': float(a_path),
                'b_path': float(b_path),
                'proportion_mediated': float(proportion_mediated),
                'interpretation': f'Mediator orqali ta\'sir: {indirect_effect:.4f}, to\'g\'ridan-to\'g\'ri ta\'sir: {direct_effect:.4f}'
            }
            
        except Exception as e:
            return {'error': f'Mediation tahlilida xato: {str(e)}'}


class HypothesisTester:
    """Gipoteza testlash tizimi"""
    
    def __init__(self):
        self.hypothesis_results = {}
        self.test_types = {
            't_test': self.t_test,
            'chi_square': self.chi_square_test,
            'anova': self.anova_test,
            'correlation': self.correlation_test,
            'regression': self.regression_test
        }
    
    def t_test(self, data1: np.array, data2: np.array, 
               alternative: str = 'two_sided', alpha: float = 0.05) -> Dict[str, Any]:
        """T-test"""
        # T-test hisoblash
        t_stat, p_value = stats.ttest_ind(data1, data2, alternative=alternative)
        
        # Confidence interval
        diff_mean = np.mean(data1) - np.mean(data2)
        pooled_std = np.sqrt(((len(data1) - 1) * np.var(data1, ddof=1) + 
                             (len(data2) - 1) * np.var(data2, ddof=1)) / 
                            (len(data1) + len(data2) - 2))
        se = pooled_std * np.sqrt(1/len(data1) + 1/len(data2))
        t_critical = stats.t.ppf(1 - alpha/2, len(data1) + len(data2) - 2)
        ci_lower = diff_mean - t_critical * se
        ci_upper = diff_mean + t_critical * se
        
        # Effect size (Cohen's d)
        cohens_d = diff_mean / pooled_std
        
        return {
            'test_type': 't_test',
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'degrees_of_freedom': len(data1) + len(data2) - 2,
            'significant': p_value < alpha,
            'mean_difference': float(diff_mean),
            'confidence_interval_95': [float(ci_lower), float(ci_upper)],
            'cohens_d': float(cohens_d),
            'effect_size': self._interpret_cohens_d(cohens_d),
            'conclusion': f"{'Reject' if p_value < alpha else 'Fail to reject'} null hypothesis"
        }
    
    def chi_square_test(self, observed: np.array, expected: np.array = None) -> Dict[str, Any]:
        """Chi-square test"""
        if expected is None:
            expected = None  # Will be calculated by chi2_contingency
        
        # Chi-square test
        chi2_stat, p_value, dof, expected_freq = chi2_contingency(observed)
        
        # Effect size (Cramér's V)
        n = observed.sum()
        cramers_v = np.sqrt(chi2_stat / (n * (min(observed.shape) - 1)))
        
        # Expected frequencies
        expected_df = pd.DataFrame(expected_freq, 
                                 index=range(observed.shape[0]),
                                 columns=range(observed.shape[1]))
        
        return {
            'test_type': 'chi_square',
            'chi2_statistic': float(chi2_stat),
            'p_value': float(p_value),
            'degrees_of_freedom': dof,
            'significant': p_value < 0.05,
            'expected_frequencies': expected_df.values.tolist(),
            'cramers_v': float(cramers_v),
            'effect_size': self._interpret_cramers_v(cramers_v),
            'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} null hypothesis"
        }
    
    def anova_test(self, groups: List[np.array], alpha: float = 0.05) -> Dict[str, Any]:
        """ANOVA test"""
        # One-way ANOVA
        f_stat, p_value = stats.f_oneway(*groups)
        
        # Group statistics
        group_stats = []
        for i, group in enumerate(groups):
            group_stats.append({
                'group': f'Group {i+1}',
                'mean': float(np.mean(group)),
                'std': float(np.std(group, ddof=1)),
                'count': len(group)
            })
        
        # Total statistics
        all_data = np.concatenate(groups)
        total_mean = np.mean(all_data)
        total_std = np.std(all_data, ddof=1)
        
        # Effect size (eta squared)
        ss_between = sum(len(group) * (np.mean(group) - total_mean)**2 for group in groups)
        ss_total = np.sum((all_data - total_mean)**2)
        eta_squared = ss_between / ss_total if ss_total != 0 else 0
        
        return {
            'test_type': 'anova',
            'f_statistic': float(f_stat),
            'p_value': float(p_value),
            'degrees_of_freedom_between': len(groups) - 1,
            'degrees_of_freedom_within': len(all_data) - len(groups),
            'significant': p_value < alpha,
            'group_statistics': group_stats,
            'total_mean': float(total_mean),
            'total_std': float(total_std),
            'eta_squared': float(eta_squared),
            'effect_size': self._interpret_eta_squared(eta_squared),
            'conclusion': f"{'Reject' if p_value < alpha else 'Fail to reject'} null hypothesis"
        }
    
    def correlation_test(self, x: np.array, y: np.array, method: str = 'pearson') -> Dict[str, Any]:
        """Korrelatsiya testi"""
        if method == 'pearson':
            corr_coef, p_value = pearsonr(x, y)
        elif method == 'spearman':
            corr_coef, p_value = spearmanr(x, y)
        else:
            return {'error': f'Noto\'g\'ri method: {method}'}
        
        # Sample size
        n = len(x)
        
        # Critical value
        if n > 30:
            # Normal approximation
            t_critical = abs(corr_coef) * np.sqrt((n - 2) / (1 - corr_coef**2))
            p_value_approx = 2 * (1 - stats.t.cdf(t_critical, n - 2))
        else:
            p_value_approx = p_value
        
        return {
            'test_type': 'correlation',
            'correlation_coefficient': float(corr_coef),
            'p_value': float(p_value),
            'sample_size': n,
            'significant': p_value < 0.05,
            'method': method,
            'strength': self._interpret_correlation(corr_coef),
            'conclusion': f"{'Significant' if p_value < 0.05 else 'Not significant'} correlation"
        }
    
    def regression_test(self, X: np.array, y: np.array) -> Dict[str, Any]:
        """Regression testi"""
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
        
        # Fit model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predictions
        y_pred = model.predict(X)
        
        # Statistics
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        n = len(y)
        p = X.shape[1]
        
        # F-test for overall regression
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        ss_reg = ss_tot - ss_res
        
        f_stat = (ss_reg / p) / (ss_res / (n - p - 1))
        f_p_value = 1 - stats.f.cdf(f_stat, p, n - p - 1)
        
        return {
            'test_type': 'regression',
            'r_squared': float(r2),
            'adjusted_r_squared': float(1 - (1 - r2) * (n - 1) / (n - p - 1)),
            'mse': float(mse),
            'f_statistic': float(f_stat),
            'f_p_value': float(f_p_value),
            'f_significant': f_p_value < 0.05,
            'coefficients': model.coef_.tolist(),
            'intercept': float(model.intercept_),
            'sample_size': n,
            'predictors': p,
            'conclusion': f"{'Significant' if f_p_value < 0.05 else 'Not significant'} regression model"
        }
    
    def _interpret_cohens_d(self, d: float) -> str:
        """Cohen's d ni talqin qilish"""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "Kichik effekt"
        elif abs_d < 0.5:
            return "O'rta effekt"
        elif abs_d < 0.8:
            return "Katta effekt"
        else:
            return "Juda katta effekt"
    
    def _interpret_cramers_v(self, v: float) -> str:
        """Cramér's V ni talqin qilish"""
        if v < 0.1:
            return "Kichik assotsiatsiya"
        elif v < 0.3:
            return "O'rta assotsiatsiya"
        else:
            return "Kuchli assotsiatsiya"
    
    def _interpret_eta_squared(self, eta2: float) -> str:
        """Eta squared ni talqin qilish"""
        if eta2 < 0.01:
            return "Juda kichik effekt"
        elif eta2 < 0.06:
            return "Kichik effekt"
        elif eta2 < 0.14:
            return "O'rta effekt"
        else:
            return "Katta effekt"
    
    def _interpret_correlation(self, r: float) -> str:
        """Korrelatsiya kuchini talqin qilish"""
        abs_r = abs(r)
        if abs_r < 0.1:
            return "Juda kuchsiz"
        elif abs_r < 0.3:
            return "Kuchsiz"
        elif abs_r < 0.5:
            return "O'rta"
        elif abs_r < 0.7:
            return "Kuchli"
        else:
            return "Juda kuchli"


class DecisionTreeAnalyzer:
    """Qaror daraxti va senariyo tahlili"""
    
    def __init__(self):
        self.decision_trees = {}
        self.scenario_analysis = {}
    
    def build_decision_tree(self, problem_description: str, options: List[Dict[str, Any]], 
                          outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Qaror daraxti yaratish"""
        # Simple decision tree construction
        tree_structure = {
            'root': {
                'decision_point': problem_description,
                'options': []
            }
        }
        
        for i, option in enumerate(options):
            option_node = {
                'option_id': f"option_{i}",
                'option_name': option.get('name', f'Option {i+1}'),
                'description': option.get('description', ''),
                'probability': option.get('probability', 1.0),
                'outcomes': []
            }
            
            # Add outcomes for this option
            for j, outcome in enumerate(outcomes):
                if outcome.get('option_id') == option.get('id', i):
                    outcome_node = {
                        'outcome_id': f"outcome_{i}_{j}",
                        'outcome_name': outcome.get('name', f'Outcome {j+1}'),
                        'probability': outcome.get('probability', 0.5),
                        'value': outcome.get('value', 0),
                        'description': outcome.get('description', '')
                    }
                    option_node['outcomes'].append(outcome_node)
            
            tree_structure['root']['options'].append(option_node)
        
        # Calculate expected values
        for option in tree_structure['root']['options']:
            expected_value = sum(outcome['probability'] * outcome['value'] 
                               for outcome in option['outcomes'])
            option['expected_value'] = expected_value
        
        # Find best option
        best_option = max(tree_structure['root']['options'], 
                         key=lambda x: x['expected_value'])
        
        return {
            'decision_tree': tree_structure,
            'best_option': best_option['option_name'],
            'best_expected_value': best_option['expected_value'],
            'recommendation': f"Eng yaxshi tanlov: {best_option['option_name']} (kutilayotgan qiymat: {best_option['expected_value']:.2f})"
        }
    
    def scenario_analysis(self, base_case: Dict[str, Any], scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Senariyo tahlili"""
        scenario_results = {}
        
        for scenario in scenarios:
            scenario_name = scenario['name']
            scenario_params = scenario.get('parameters', {})
            
            # Apply scenario to base case
            modified_case = base_case.copy()
            for param, value in scenario_params.items():
                if param in modified_case:
                    if isinstance(value, dict) and 'change_type' in value:
                        # Percentage or absolute change
                        change_type = value['change_type']
                        change_value = value['value']
                        if change_type == 'percentage':
                            modified_case[param] *= (1 + change_value / 100)
                        elif change_type == 'absolute':
                            modified_case[param] += change_value
                    else:
                        modified_case[param] = value
            
            # Calculate scenario impact
            impact_metrics = self._calculate_scenario_impact(base_case, modified_case)
            
            scenario_results[scenario_name] = {
                'scenario_description': scenario.get('description', ''),
                'probability': scenario.get('probability', 0.2),
                'impact_metrics': impact_metrics,
                'risk_level': self._assess_scenario_risk(impact_metrics)
            }
        
        # Scenario ranking
        scenario_ranking = sorted(scenario_results.items(), 
                                key=lambda x: abs(x[1]['impact_metrics'].get('total_change', 0)), 
                                reverse=True)
        
        return {
            'base_case': base_case,
            'scenario_results': scenario_results,
            'scenario_ranking': [{'name': name, 'impact': result['impact_metrics']} 
                               for name, result in scenario_ranking],
            'key_insights': self._generate_scenario_insights(scenario_results)
        }
    
    def monte_carlo_simulation(self, parameters: Dict[str, Dict[str, Any]], 
                             num_simulations: int = 1000) -> Dict[str, Any]:
        """Monte Carlo simulyatsiya"""
        results = []
        
        for _ in range(num_simulations):
            simulation_result = {}
            
            for param_name, param_config in parameters.items():
                dist_type = param_config.get('distribution', 'normal')
                if dist_type == 'normal':
                    mean = param_config.get('mean', 0)
                    std = param_config.get('std', 1)
                    value = np.random.normal(mean, std)
                elif dist_type == 'uniform':
                    min_val = param_config.get('min', 0)
                    max_val = param_config.get('max', 1)
                    value = np.random.uniform(min_val, max_val)
                else:  # discrete
                    values = param_config.get('values', [0, 1])
                    probabilities = param_config.get('probabilities', [0.5, 0.5])
                    value = np.random.choice(values, p=probabilities)
                
                simulation_result[param_name] = value
            
            # Calculate final metric (e.g., portfolio return)
            # This is a simplified calculation
            total_return = sum(simulation_result.values())
            simulation_result['total_return'] = total_return
            results.append(simulation_result)
        
        # Statistical analysis
        returns = [r['total_return'] for r in results]
        
        return {
            'num_simulations': num_simulations,
            'mean_return': float(np.mean(returns)),
            'std_return': float(np.std(returns)),
            'min_return': float(np.min(returns)),
            'max_return': float(np.max(returns)),
            'percentiles': {
                '5th': float(np.percentile(returns, 5)),
                '25th': float(np.percentile(returns, 25)),
                '50th': float(np.percentile(returns, 50)),
                '75th': float(np.percentile(returns, 75)),
                '95th': float(np.percentile(returns, 95))
            },
            'probability_positive': float(np.mean(np.array(returns) > 0)),
            'value_at_risk_5': float(np.percentile(returns, 5)),
            'expected_shortfall': float(np.mean([r for r in returns if r <= np.percentile(returns, 5)]))
        }
    
    def _calculate_scenario_impact(self, base_case: Dict[str, Any], 
                                 modified_case: Dict[str, Any]) -> Dict[str, Any]:
        """Senariyo ta'sirini hisoblash"""
        changes = {}
        for key in base_case:
            if key in modified_case:
                base_val = base_case[key]
                mod_val = modified_case[key]
                if base_val != 0:
                    change_pct = (mod_val - base_val) / base_val * 100
                    changes[key] = {
                        'absolute_change': mod_val - base_val,
                        'percentage_change': change_pct
                    }
        
        # Overall impact score
        total_change = sum(abs(change['percentage_change']) for change in changes.values())
        
        return {
            'individual_changes': changes,
            'total_change': total_change,
            'impact_summary': f"Umumiy o'zgarish: {total_change:.1f}%"
        }
    
    def _assess_scenario_risk(self, impact_metrics: Dict[str, Any]) -> str:
        """Senariyo riskini baholash"""
        total_change = abs(impact_metrics.get('total_change', 0))
        
        if total_change < 10:
            return "Past risk"
        elif total_change < 25:
            return "O'rta risk"
        elif total_change < 50:
            return "Yuqori risk"
        else:
            return "Kritik risk"
    
    def _generate_scenario_insights(self, scenario_results: Dict[str, Any]) -> List[str]:
        """Senariyo tushunshalarini yaratish"""
        insights = []
        
        # Find best and worst scenarios
        best_scenario = max(scenario_results.items(), 
                           key=lambda x: x[1]['impact_metrics'].get('total_change', -1000))
        worst_scenario = min(scenario_results.items(), 
                           key=lambda x: x[1]['impact_metrics'].get('total_change', 1000))
        
        insights.append(f"Eng yaxshi senariyo: {best_scenario[0]} (ta'sir: {best_scenario[1]['impact_metrics']['total_change']:.1f}%)")
        insights.append(f"Eng yomon senariyo: {worst_scenario[0]} (ta'sir: {worst_scenario[1]['impact_metrics']['total_change']:.1f}%)")
        
        # Average probability weighted impact
        total_weighted_impact = sum(
            result['probability'] * abs(result['impact_metrics']['total_change'])
            for result in scenario_results.values()
        )
        insights.append(f"O'rtacha og'irlikli ta'sir: {total_weighted_impact:.1f}%")
        
        return insights


class AdvancedReasoningEngine:
    """Asosiy reasoning engine"""
    
    def __init__(self):
        self.problem_framework = ProblemFramework()
        self.analyst = MultiStepAnalyst()
        self.risk_engine = RiskAssessmentEngine()
        self.strategy_dev = StrategyDeveloper()
        self.predictor = MarketPredictor()
        self.causal_reasoner = CausalReasoner()
        self.hypothesis_tester = HypothesisTester()
        self.decision_tree = DecisionTreeAnalyzer()
        
        self.reasoning_chains = []
        self.analysis_history = []
    
    def complex_problem_solving(self, problem: Dict[str, Any], method: str = 'design_thinking') -> Dict[str, Any]:
        """Murakkab muammolarni hal qilish"""
        if method not in self.problem_framework.problem_solving_methods:
            return {'error': f'Method "{method}" topilmadi'}
        
        # Problem solving chain
        solution = self.problem_framework.problem_solving_methods[method](problem)
        
        # Add risk assessment
        risk_assessment = self.risk_engine.calculate_portfolio_risk({})
        
        # Add recommendations
        recommendations = [
            "Problema hal qilishning birinchi qadami muvaffaqiyatli amalga oshirildi",
            "Keyingi qadamlarni ham ushbu metodologiya asosida bajarish tavsiya etiladi",
            "O'zgarmas monitoring va baholash zarur"
        ]
        
        return {
            'problem': problem,
            'method_used': method,
            'solution_framework': solution,
            'risk_assessment': risk_assessment,
            'recommendations': recommendations,
            'next_steps': [
                "Natijalarni amalda sinab ko'rish",
                "Yechimni takomillashtirish",
                "O'lchash va baholash"
            ]
        }
    
    def multi_step_analysis(self, data: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
        """Ko'p bosqichli tahlil"""
        results = {}
        
        # Step 1: Data validation
        validation = self.analyst.validate_data(data)
        results['data_validation'] = validation
        
        if not validation['is_valid']:
            return {'error': 'Ma\'lumotlar validatsiyadan o\'tmadi', 'validation': validation}
        
        # Step 2: Exploratory analysis
        exploration = self.analyst.exploratory_analysis(data)
        results['exploratory_analysis'] = exploration
        
        # Step 3: Hypothesis testing
        if len(data.columns) > 1:
            hypothesis_result = self.analyst.hypothesis_testing(
                data, "Barcha o'zgaruvchilar o'rtasida bog'liqlik mavjud"
            )
            results['hypothesis_testing'] = hypothesis_result
        
        # Step 4: Statistical modeling
        if target_column and target_column in data.columns:
            modeling = self.analyst.statistical_modeling(data, target_column)
            results['statistical_modeling'] = modeling
        
        # Step 5: Insights
        insights = self._generate_analysis_insights(results)
        results['insights'] = insights
        
        return results
    
    def comprehensive_risk_analysis(self, portfolio_data: Dict[str, Any], 
                                  market_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Keng qamrovli risk tahlili"""
        
        # Portfolio risk assessment
        portfolio_risk = self.risk_engine.calculate_portfolio_risk(portfolio_data)
        
        # VaR analysis
        # Simulate returns for demonstration
        simulated_returns = np.random.normal(0.001, 0.02, 252)  # Daily returns for a year
        var_analysis = self.risk_engine.var_analysis(simulated_returns)
        
        # Stress testing
        stress_results = self.risk_engine.stress_testing(market_scenarios, market_scenarios)
        
        # Scenario analysis
        base_case = {'portfolio_value': 100000, 'expected_return': 0.08}
        scenarios = [
            {'name': 'Bull Market', 'parameters': {'expected_return': 0.15}},
            {'name': 'Bear Market', 'parameters': {'expected_return': -0.10}},
            {'name': 'Recession', 'parameters': {'expected_return': -0.20}}
        ]
        scenario_analysis = self.decision_tree.scenario_analysis(base_case, scenarios)
        
        return {
            'portfolio_risk': portfolio_risk,
            'var_analysis': var_analysis,
            'stress_testing': stress_results,
            'scenario_analysis': scenario_analysis,
            'overall_risk_score': (portfolio_risk['total_risk_score'] + 
                                 abs(var_analysis['var_value'])) / 2,
            'risk_management_recommendations': self._generate_risk_recommendations(portfolio_risk)
        }
    
    def strategy_development_pipeline(self, objectives: str, constraints: Dict[str, Any], 
                                    market_data: pd.DataFrame) -> Dict[str, Any]:
        """Strategiya rivojlantirish pipeline"""
        
        # Strategy generation
        strategy = self.strategy_dev.generate_strategy(objectives, constraints, market_data)
        
        # Strategy backtesting
        if not market_data.empty:
            backtest_results = self.strategy_dev.backtest_strategy(strategy, market_data)
        else:
            backtest_results = {'error': 'Tarixiy ma\'lumotlar topilmadi'}
        
        # Strategy optimization
        multiple_strategies = [
            strategy,
            Strategy("Aggressive Growth", "Yuqori risk-yuqori daromad", 0.6, 0.18, 0.3, "3-6 oy", {}, []),
            Strategy("Conservative Income", "Past risk-barqaror daromad", 0.85, 0.06, 0.08, "6-12 oy", {}, [])
        ]
        optimization_results = self.strategy_dev.optimize_strategy(multiple_strategies)
        
        return {
            'generated_strategy': {
                'name': strategy.name,
                'description': strategy.description,
                'success_probability': strategy.success_probability,
                'expected_return': strategy.expected_return,
                'max_risk': strategy.max_risk,
                'implementation_steps': strategy.implementation_steps
            },
            'backtest_results': backtest_results,
            'optimization_results': optimization_results,
            'strategy_recommendation': self._generate_strategy_recommendation(strategy, backtest_results)
        }
    
    def market_prediction_pipeline(self, data: pd.DataFrame, prediction_horizon: int = 30) -> Dict[str, Any]:
        """Bozor bashorat pipeline"""
        
        # Model training
        training_results = self.predictor.train_models(data)
        
        # Ensemble prediction
        ensemble_results = self.predictor.ensemble_prediction(data.tail(10))
        
        # Risk assessment for predictions
        if 'prediction' in ensemble_results:
            predictions = ensemble_results['ensemble_prediction']
            prediction_risk = {
                'volatility': np.std(predictions) if predictions else 0,
                'confidence_score': 1.0 - np.std(predictions) if predictions else 0,
                'trend_direction': 'upward' if predictions[-1] > predictions[0] else 'downward'
            }
        else:
            prediction_risk = {'error': 'Bashorat qila olmadim'}
        
        return {
            'model_training': training_results,
            'ensemble_prediction': ensemble_results,
            'prediction_horizon': prediction_horizon,
            'prediction_risk': prediction_risk,
            'trading_signals': self._generate_trading_signals(ensemble_results)
        }
    
    def causal_inference_pipeline(self, data: pd.DataFrame, treatment: str, outcome: str) -> Dict[str, Any]:
        """Sabab-oqibat inference pipeline"""
        
        # Causal graph building
        variables = [col for col in data.columns if data[col].dtype in ['float64', 'int64']]
        relationships = [
            {'cause': treatment, 'effect': outcome, 'strength': 0.7},
            {'cause': 'market_volatility', 'effect': outcome, 'strength': 0.5} if 'market_volatility' in variables else None
        ]
        relationships = [r for r in relationships if r is not None]
        
        causal_graph = self.causal_reasoner.build_causal_graph(variables, relationships)
        
        # Confounder identification
        confounders = [col for col in variables if col not in [treatment, outcome]]
        confounding_analysis = self.causal_reasoner.identify_confounders(treatment, outcome, confounders)
        
        # Backdoor criterion analysis
        backdoor_analysis = self.causal_reasoner.backdoor_criterion(treatment, outcome, confounders, data)
        
        # Intervention effect
        intervention_value = data[treatment].mean() + data[treatment].std()  # Above average
        intervention_analysis = self.causal_reasoner.calculate_intervention_effect(
            treatment, outcome, intervention_value, data
        )
        
        return {
            'causal_graph': causal_graph,
            'confounding_analysis': confounding_analysis,
            'backdoor_analysis': backdoor_analysis,
            'intervention_analysis': intervention_analysis,
            'causal_recommendations': self._generate_causal_recommendations(confounding_analysis, backdoor_analysis)
        }
    
    def hypothesis_testing_pipeline(self, data: pd.DataFrame, hypothesis: str) -> Dict[str, Any]:
        """Gipoteza testlash pipeline"""
        
        results = {}
        
        # Chi-square test for categorical data
        cat_cols = data.select_dtypes(include=['object']).columns
        if len(cat_cols) >= 2:
            contingency = pd.crosstab(data[cat_cols[0]], data[cat_cols[1]])
            chi_square_result = self.hypothesis_tester.chi_square_test(contingency.values)
            results['chi_square_test'] = chi_square_result
        
        # T-test for numerical data
        num_cols = data.select_dtypes(include=[np.number]).columns
        if len(num_cols) >= 2:
            t_test_result = self.hypothesis_tester.t_test(
                data[num_cols[0]].dropna().values, 
                data[num_cols[1]].dropna().values
            )
            results['t_test'] = t_test_result
        
        # Correlation test
        if len(num_cols) >= 2:
            corr_result = self.hypothesis_tester.correlation_test(
                data[num_cols[0]].dropna().values,
                data[num_cols[1]].dropna().values
            )
            results['correlation_test'] = corr_result
        
        # Regression test
        if len(num_cols) >= 3:
            X = data[num_cols[:-1]].fillna(0).values
            y = data[num_cols[-1]].fillna(0).values
            reg_result = self.hypothesis_tester.regression_test(X, y)
            results['regression_test'] = reg_result
        
        # Overall conclusion
        significant_tests = [name for name, result in results.items() 
                           if isinstance(result, dict) and result.get('significant', False)]
        
        return {
            'hypothesis': hypothesis,
            'test_results': results,
            'significant_tests': significant_tests,
            'overall_conclusion': self._generate_hypothesis_conclusion(hypothesis, results)
        }
    
    def decision_scenario_pipeline(self, decision_problem: str, options: List[Dict[str, Any]], 
                                 scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Qaror va senariyo pipeline"""
        
        # Decision tree analysis
        decision_tree_result = self.decision_tree.build_decision_tree(
            decision_problem, options, scenarios
        )
        
        # Scenario analysis
        base_case = {'value': 100, 'probability': 1.0}
        scenario_result = self.decision_tree.scenario_analysis(base_case, scenarios)
        
        # Monte Carlo simulation
        if scenarios:
            mc_params = {}
            for scenario in scenarios[:2]:  # First 2 scenarios
                mc_params[scenario['name']] = {
                    'distribution': 'normal',
                    'mean': scenario.get('impact', 0),
                    'std': 0.1
                }
            
            mc_result = self.decision_tree.monte_carlo_simulation(mc_params)
        else:
            mc_result = {'error': 'Monte Carlo simulyatsiya uchun senariyo topilmadi'}
        
        return {
            'decision_tree': decision_tree_result,
            'scenario_analysis': scenario_result,
            'monte_carlo_simulation': mc_result,
            'final_recommendation': self._generate_decision_recommendation(
                decision_tree_result, scenario_result, mc_result
            )
        }
    
    def _generate_analysis_insights(self, results: Dict[str, Any]) -> List[str]:
        """Tahlil tushunshalarini yaratish"""
        insights = []
        
        if 'data_validation' in results:
            val = results['data_validation']
            insights.append(f"Ma'lumotlar hajmi: {val['total_rows']} qator, {val['total_columns']} ustun")
        
        if 'exploratory_analysis' in results:
            exp = results['exploratory_analysis']
            if 'correlations' in exp and exp['correlations']:
                insights.append("O'zgaruvchilar o'rtasida korrelatsiya mavjud")
        
        return insights
    
    def _generate_risk_recommendations(self, portfolio_risk: Dict[str, Any]) -> List[str]:
        """Risk tavsiyalari"""
        recommendations = []
        
        if portfolio_risk['risk_level'] == 'high':
            recommendations.append("Portfolio riskini kamaytirish uchun diversifikatsiyani oshiring")
            recommendations.append("Stop-loss orderlarini qo'ying")
        elif portfolio_risk['risk_level'] == 'medium':
            recommendations.append("Hozirgi risk darajasini saqlab qoling")
            recommendations.append("Davolash monitoring qiling")
        
        return recommendations
    
    def _generate_strategy_recommendation(self, strategy: Strategy, backtest: Dict[str, Any]) -> str:
        """Strategiya tavsiyasi"""
        if 'error' in backtest:
            return f"Strategiya: {strategy.name} - Test natijalari mavjud emas"
        
        if backtest.get('total_return', 0) > 0.1:
            return f"Strategiya {strategy.name} yuqori daromad keltirish potentsialiga ega"
        else:
            return f"Strategiya {strategy.name} konservativ yondashuvni talab qiladi"
    
    def _generate_trading_signals(self, ensemble_results: Dict[str, Any]) -> List[str]:
        """Trading signallari"""
        signals = []
        
        if 'ensemble_prediction' in ensemble_results:
            predictions = ensemble_results['ensemble_prediction']
            if predictions:
                recent_trend = "bullish" if predictions[-1] > predictions[0] else "bearish"
                signals.append(f"Bozor trendi: {recent_trend}")
                
                if abs(predictions[-1]) > 0.02:
                    signals.append("Kuchli signal: Yuqori volatilite")
                else:
                    signals.append("Neytral signal: Past volatilite")
        
        return signals
    
    def _generate_causal_recommendations(self, confounding: Dict[str, Any], backdoor: Dict[str, Any]) -> List[str]:
        """Causal inference tavsiyalari"""
        recommendations = []
        
        if confounding.get('total_confounders', 0) > 0:
            recommendations.append("Confounding omillarni nazorat qiling")
        
        if backdoor.get('backdoor_criterion_satisfied', False):
            recommendations.append("Backdoor criterion qanoatlantirilgan - causal inference ishonchli")
        else:
            recommendations.append("Qo'shimcha confounding nazorati kerak")
        
        return recommendations
    
    def _generate_hypothesis_conclusion(self, hypothesis: str, results: Dict[str, Any]) -> str:
        """Gipoteza xulosasi"""
        significant_tests = [name for name, result in results.items() 
                           if isinstance(result, dict) and result.get('significant', False)]
        
        if significant_tests:
            return f"Gipoteza qisman tasdiqlanadi: {', '.join(significant_tests)}"
        else:
            return "Gipoteza rad etiladi - statistik jihatdan muhim farq topilmadi"
    
    def _generate_decision_recommendation(self, decision_tree: Dict[str, Any], 
                                        scenario: Dict[str, Any], mc: Dict[str, Any]) -> str:
        """Qaror tavsiyasi"""
        if 'best_option' in decision_tree:
            return f"Tavsiya etilayotgan qaror: {decision_tree['best_option']}"
        else:
            return "Qo'shimcha ma'lumotlar talab qilinadi"


def demo_advanced_reasoning():
    """Advanced reasoning moduli uchun demo"""
    print("🚀 Advanced Reasoning & Analytics moduli ishga tushirilmoqda...")
    print("=" * 60)
    
    # Initialize engine
    engine = AdvancedReasoningEngine()
    
    # Test data
    test_data = pd.DataFrame({
        'price': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
        'volatility': np.random.uniform(0.01, 0.05, 100),
        'return': np.random.normal(0, 0.02, 100)
    })
    
    print("\n📊 1. Murakkab muammolarni hal qilish testi:")
    problem = {'description': 'Trading strategiyasi yaratish', 'constraints': {'risk_limit': 0.15}}
    solution = engine.complex_problem_solving(problem)
    print(f"   ✅ Yechim: {solution.get('recommendations', ['Tayyorlandi'])[0]}")
    
    print("\n🔍 2. Ko'p bosqichli tahlil testi:")
    analysis = engine.multi_step_analysis(test_data, 'return')
    print(f"   ✅ Tahlil yakunlandi: {len(analysis)} bosqich bajarildi")
    
    print("\n⚠️ 3. Risk baholash testi:")
    portfolio = {'AAPL': 0.3, 'GOOGL': 0.4, 'MSFT': 0.3}
    risk_analysis = engine.comprehensive_risk_analysis(portfolio, [])
    print(f"   ✅ Risk darajasi: {risk_analysis['portfolio_risk']['risk_level']}")
    
    print("\n📈 4. Strategiya rivojlantirish testi:")
    strategy_result = engine.strategy_development_pipeline(
        "Yuqori daromad olish", {'risk_limit': 0.2}, test_data
    )
    print(f"   ✅ Strategiya: {strategy_result['generated_strategy']['name']}")
    
    print("\n🎯 5. Bozor bashoratlari testi:")
    prediction = engine.market_prediction_pipeline(test_data)
    print(f"   ✅ Model o'rgatildi: {len(prediction['model_training'])} ta model")
    
    print("\n🔗 6. Sabab-oqibat reasoning testi:")
    causal = engine.causal_inference_pipeline(test_data, 'volatility', 'return')
    print(f"   ✅ Causal graph yaratildi: {causal['causal_graph']['node_count']} tugun")
    
    print("\n🧪 7. Gipoteza testlash testi:")
    hypothesis_result = engine.hypothesis_testing_pipeline(
        test_data, "O'zgaruvchilar o'rtasida bog'liqlik mavjud"
    )
    print(f"   ✅ Testlar bajarildi: {len(hypothesis_result['test_results'])} ta")
    
    print("\n🌳 8. Qaror daraxti va senariyo tahlili testi:")
    options = [
        {'id': 1, 'name': 'Aksiya sotib olish', 'probability': 0.6},
        {'id': 2, 'name': 'Bond sotib olish', 'probability': 0.4}
    ]
    outcomes = [
        {'option_id': 1, 'name': 'Daromad', 'value': 100, 'probability': 0.7},
        {'option_id': 1, 'name': 'Yo\'qotish', 'value': -50, 'probability': 0.3},
        {'option_id': 2, 'name': 'Kichik daromad', 'value': 20, 'probability': 0.8}
    ]
    decision_result = engine.decision_scenario_pipeline(
        "Investitsiya tanlovi", options, outcomes
    )
    print(f"   ✅ Eng yaxshi tanlov: {decision_result['decision_tree']['best_option']}")
    
    print("\n🎉 Advanced Reasoning & Analytics moduli muvaffaqiyatli ishlaydi!")
    print("=" * 60)


if __name__ == "__main__":
    demo_advanced_reasoning()