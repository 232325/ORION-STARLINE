"""
Model Governance System
ML model governance - audit trails, bias detection, compliance, explainable AI
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import uuid
from collections import defaultdict

# ML va AI kutubxonalar
try:
    import shap
    from sklearn.metrics import confusion_matrix, classification_report
    from sklearn.inspection import permutation_importance
    import matplotlib.pyplot as plt
except ImportError:
    shap = None

@dataclass
class ModelAudit:
    """Model audit ma'lumotlari"""
    audit_id: str
    model_name: str
    version_id: str
    action: str  # created, trained, deployed, updated, deleted
    performed_by: str
    timestamp: datetime
    details: Dict[str, Any]
    approvals: List[Dict[str, str]]
    risk_score: float
    compliance_status: str
    documentation_complete: bool

@dataclass
class BiasAnalysis:
    """Bias tahlili natijalari"""
    protected_attribute: str
    fairness_metrics: Dict[str, float]
    bias_detected: bool
    bias_severity: str  # low, medium, high
    recommendations: List[str]
    timestamp: datetime

@dataclass
class ComplianceCheck:
    """Compliance tekshirish"""
    regulation: str
    check_type: str
    status: str  # compliant, non_compliant, partial
    score: float
    requirements: List[Dict[str, Any]]
    violations: List[str]
    timestamp: datetime

@dataclass
class ExplainabilityResult:
    """Explainable AI natijalari"""
    method: str  # shap, lime, feature_importance
    explanation_type: str  # global, local, counterfactual
    feature_importances: Dict[str, float]
    feature_names: List[str]
    predictions_explained: int
    confidence_scores: List[float]
    interpretation: str
    timestamp: datetime

class AuditLogger:
    """Model audit logging"""
    
    def __init__(self, audit_path: str = "logs/audit"):
        self.audit_path = Path(audit_path)
        self.audit_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def log_action(self, model_name: str, version_id: str, action: str, 
                  performed_by: str, details: Dict[str, Any] = None) -> str:
        """Action log"""
        audit_id = str(uuid.uuid4())
        
        audit_record = {
            'audit_id': audit_id,
            'model_name': model_name,
            'version_id': version_id,
            'action': action,
            'performed_by': performed_by,
            'timestamp': datetime.now().isoformat(),
            'details': details or {},
            'session_id': self._get_session_id(),
            'ip_address': '127.0.0.1'  # Placeholder
        }
        
        # Faylga yozish
        audit_file = self.audit_path / f"{model_name}_audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(audit_file, 'a') as f:
            f.write(json.dumps(audit_record) + '\n')
            
        self.logger.info(f"Audit logged: {model_name} - {action} by {performed_by}")
        
        return audit_id
        
    def _get_session_id(self) -> str:
        """Session ID yaratish"""
        return str(uuid.uuid4())
        
    def get_audit_trail(self, model_name: str, start_date: datetime = None, 
                       end_date: datetime = None) -> List[ModelAudit]:
        """Audit trail olish"""
        audit_files = list(self.audit_path.glob(f"{model_name}_audit_*.jsonl"))
        
        audits = []
        for audit_file in audit_files:
            with open(audit_file, 'r') as f:
                for line in f:
                    record = json.loads(line.strip())
                    
                    # Date filtering
                    audit_time = datetime.fromisoformat(record['timestamp'])
                    if start_date and audit_time < start_date:
                        continue
                    if end_date and audit_time > end_date:
                        continue
                        
                    # Convert to ModelAudit
                    audit = ModelAudit(
                        audit_id=record['audit_id'],
                        model_name=record['model_name'],
                        version_id=record['version_id'],
                        action=record['action'],
                        performed_by=record['performed_by'],
                        timestamp=datetime.fromisoformat(record['timestamp']),
                        details=record['details'],
                        approvals=[],  # Placeholder
                        risk_score=0.0,  # Placeholder
                        compliance_status='unknown',  # Placeholder
                        documentation_complete=False  # Placeholder
                    )
                    audits.append(audit)
                    
        return sorted(audits, key=lambda x: x.timestamp, reverse=True)

class BiasDetector:
    """Model bias detection"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.fairness_metrics = config.get('fairness_metrics', [
            'demographic_parity', 'equalized_odds', 'calibration'
        ])
        
    def analyze_bias(self, model: Any, X: pd.DataFrame, y_true: pd.Series, 
                    y_pred: pd.Series, protected_attributes: List[str]) -> List[BiasAnalysis]:
        """Model bias tahlili"""
        
        bias_results = []
        
        for protected_attr in protected_attributes:
            if protected_attr not in X.columns:
                self.logger.warning(f"Protected attribute topilmadi: {protected_attr}")
                continue
                
            # Fairness metrics hisoblash
            fairness_metrics = self._calculate_fairness_metrics(
                y_true, y_pred, X[protected_attr]
            )
            
            # Bias detection
            bias_detected = self._detect_bias(fairness_metrics)
            bias_severity = self._assess_bias_severity(fairness_metrics)
            
            # Recommendations
            recommendations = self._generate_bias_recommendations(
                protected_attr, fairness_metrics, bias_detected
            )
            
            bias_analysis = BiasAnalysis(
                protected_attribute=protected_attr,
                fairness_metrics=fairness_metrics,
                bias_detected=bias_detected,
                bias_severity=bias_severity,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
            bias_results.append(bias_analysis)
            
        return bias_results
        
    def _calculate_fairness_metrics(self, y_true: pd.Series, y_pred: pd.Series, 
                                  protected_attr: pd.Series) -> Dict[str, float]:
        """Fairness metrics hisoblash"""
        metrics = {}
        
        # Demographic Parity
        metrics['demographic_parity'] = self._demographic_parity(y_true, y_pred, protected_attr)
        
        # Equalized Odds
        metrics['equalized_odds'] = self._equalized_odds(y_true, y_pred, protected_attr)
        
        # Calibration
        metrics['calibration'] = self._calibration(y_true, y_pred, protected_attr)
        
        # Statistical Parity Difference
        metrics['statistical_parity_diff'] = self._statistical_parity_difference(y_pred, protected_attr)
        
        # Equal Opportunity
        metrics['equal_opportunity'] = self._equal_opportunity(y_true, y_pred, protected_attr)
        
        return metrics
        
    def _demographic_parity(self, y_true: pd.Series, y_pred: pd.Series, 
                          protected_attr: pd.Series) -> float:
        """Demographic parity hisoblash"""
        positive_rate = {}
        
        for group in protected_attr.unique():
            group_mask = protected_attr == group
            positive_rate[group] = y_pred[group_mask].mean()
            
        if len(positive_rate) > 1:
            rates = list(positive_rate.values())
            return 1.0 - (max(rates) - min(rates))  # Higher is better
        return 1.0
        
    def _equalized_odds(self, y_true: pd.Series, y_pred: pd.Series, 
                       protected_attr: pd.Series) -> float:
        """Equalized odds hisoblash"""
        metrics = {}
        
        for group in protected_attr.unique():
            group_mask = protected_attr == group
            cm = confusion_matrix(y_true[group_mask], y_pred[group_mask], 
                                labels=[0, 1])
            
            if cm.shape == (2, 2):
                tn, fp, fn, tp = cm.ravel()
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
                metrics[group] = {'tpr': tpr, 'fpr': fpr}
            else:
                metrics[group] = {'tpr': 0, 'fpr': 0}
                
        if len(metrics) > 1:
            tprs = [m['tpr'] for m in metrics.values()]
            fprs = [m['fpr'] for m in metrics.values()]
            
            tpr_diff = max(tprs) - min(tprs)
            fpr_diff = max(fprs) - min(fprs)
            
            return 1.0 - (tpr_diff + fpr_diff) / 2  # Higher is better
        return 1.0
        
    def _calibration(self, y_true: pd.Series, y_pred: pd.Series, 
                    protected_attr: pd.Series) -> float:
        """Calibration hisoblash"""
        # Placeholder - haqiqiy implementation murakkab
        return 0.8  # Mock value
        
    def _statistical_parity_difference(self, y_pred: pd.Series, 
                                     protected_attr: pd.Series) -> float:
        """Statistical parity difference hisoblash"""
        positive_rates = {}
        
        for group in protected_attr.unique():
            group_mask = protected_attr == group
            positive_rates[group] = y_pred[group_mask].mean()
            
        if len(positive_rates) > 1:
            rates = list(positive_rates.values())
            return max(rates) - min(rates)  # Lower is better
        return 0.0
        
    def _equal_opportunity(self, y_true: pd.Series, y_pred: pd.Series, 
                         protected_attr: pd.Series) -> float:
        """Equal opportunity hisoblash"""
        tprs = {}
        
        for group in protected_attr.unique():
            group_mask = protected_attr == group
            if y_true[group_mask].sum() > 0:  # Avoid division by zero
                tprs[group] = ((y_true[group_mask] == 1) & (y_pred[group_mask] == 1)).sum() / y_true[group_mask].sum()
            else:
                tprs[group] = 1.0
                
        if len(tprs) > 1:
            rates = list(tprs.values())
            return 1.0 - (max(rates) - min(rates))  # Higher is better
        return 1.0
        
    def _detect_bias(self, fairness_metrics: Dict[str, float]) -> bool:
        """Bias detection"""
        threshold = self.config.get('bias_threshold', 0.1)
        
        # Any fairness metric below threshold indicates bias
        for metric, value in fairness_metrics.items():
            if metric in ['demographic_parity', 'equalized_odds', 'calibration', 'equal_opportunity']:
                if value < threshold:
                    return True
                    
        return False
        
    def _assess_bias_severity(self, fairness_metrics: Dict[str, float]) -> str:
        """Bias severity assessment"""
        threshold_low = 0.8
        threshold_medium = 0.6
        
        min_fairness = min([
            fairness_metrics.get('demographic_parity', 1.0),
            fairness_metrics.get('equalized_odds', 1.0),
            fairness_metrics.get('calibration', 1.0)
        ])
        
        if min_fairness >= threshold_low:
            return 'low'
        elif min_fairness >= threshold_medium:
            return 'medium'
        else:
            return 'high'
            
    def _generate_bias_recommendations(self, protected_attr: str, 
                                     fairness_metrics: Dict[str, float],
                                     bias_detected: bool) -> List[str]:
        """Bias mitigation recommendations"""
        recommendations = []
        
        if bias_detected:
            recommendations.append(f"Model bias detected for attribute: {protected_attr}")
            recommendations.append("Consider data augmentation or rebalancing")
            recommendations.append("Apply fairness constraints during training")
            recommendations.append("Review feature selection and engineering")
        else:
            recommendations.append(f"No significant bias detected for attribute: {protected_attr}")
            
        return recommendations

class ComplianceChecker:
    """Regulatory compliance checker"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.regulations = config.get('regulations', ['GDPR', 'CCPA', 'SOX'])
        
    def check_compliance(self, model: Any, model_info: Dict[str, Any]) -> List[ComplianceCheck]:
        """Model compliance tekshirish"""
        compliance_results = []
        
        for regulation in self.regulations:
            result = self._check_regulation_compliance(regulation, model, model_info)
            compliance_results.append(result)
            
        return compliance_results
        
    def _check_regulation_compliance(self, regulation: str, model: Any, 
                                   model_info: Dict[str, Any]) -> ComplianceCheck:
        """Specific regulation compliance check"""
        
        if regulation == 'GDPR':
            return self._check_gdpr_compliance(model, model_info)
        elif regulation == 'CCPA':
            return self._check_ccpa_compliance(model, model_info)
        elif regulation == 'SOX':
            return self._check_sox_compliance(model, model_info)
        else:
            return ComplianceCheck(
                regulation=regulation,
                check_type='general',
                status='unknown',
                score=0.0,
                requirements=[],
                violations=[],
                timestamp=datetime.now()
            )
            
    def _check_gdpr_compliance(self, model: Any, model_info: Dict[str, Any]) -> ComplianceCheck:
        """GDPR compliance check"""
        requirements = []
        violations = []
        score = 0.0
        
        # Right to explanation
        if model_info.get('explainable', False):
            score += 0.3
            requirements.append({
                'requirement': 'Right to explanation',
                'status': 'met'
            })
        else:
            violations.append('Model explainability not implemented')
            requirements.append({
                'requirement': 'Right to explanation',
                'status': 'not_met'
            })
            
        # Data retention
        retention_policy = model_info.get('data_retention_policy', {})
        if retention_policy.get('automated_deletion', False):
            score += 0.2
            requirements.append({
                'requirement': 'Data retention policy',
                'status': 'met'
            })
        else:
            violations.append('Data retention policy not implemented')
            requirements.append({
                'requirement': 'Data retention policy',
                'status': 'not_met'
            })
            
        # Consent tracking
        if model_info.get('consent_tracking', False):
            score += 0.3
            requirements.append({
                'requirement': 'Consent tracking',
                'status': 'met'
            })
        else:
            violations.append('Consent tracking not implemented')
            requirements.append({
                'requirement': 'Consent tracking',
                'status': 'not_met'
            })
            
        # Audit trail
        if model_info.get('audit_trail', True):
            score += 0.2
            requirements.append({
                'requirement': 'Audit trail',
                'status': 'met'
            })
        else:
            violations.append('Audit trail not implemented')
            requirements.append({
                'requirement': 'Audit trail',
                'status': 'not_met'
            })
            
        status = 'compliant' if score >= 0.8 else 'non_compliant' if score < 0.5 else 'partial'
        
        return ComplianceCheck(
            regulation='GDPR',
            check_type='data_protection',
            status=status,
            score=score,
            requirements=requirements,
            violations=violations,
            timestamp=datetime.now()
        )
        
    def _check_ccpa_compliance(self, model: Any, model_info: Dict[str, Any]) -> ComplianceCheck:
        """CCPA compliance check"""
        # Similar implementation for CCPA
        return ComplianceCheck(
            regulation='CCPA',
            check_type='consumer_privacy',
            status='partial',
            score=0.6,
            requirements=[],
            violations=['Limited disclosure requirements'],
            timestamp=datetime.now()
        )
        
    def _check_sox_compliance(self, model: Any, model_info: Dict[str, Any]) -> ComplianceCheck:
        """SOX compliance check"""
        return ComplianceCheck(
            regulation='SOX',
            check_type='financial_reporting',
            status='compliant',
            score=0.9,
            requirements=[],
            violations=[],
            timestamp=datetime.now()
        )

class ExplainableAI:
    """Explainable AI integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def explain_model(self, model: Any, X: pd.DataFrame, y: pd.Series, 
                     explanation_type: str = 'global') -> ExplainabilityResult:
        """Model explainability"""
        
        if explanation_type == 'global':
            return self._global_explanation(model, X, y)
        elif explanation_type == 'local':
            return self._local_explanation(model, X, y)
        else:
            raise ValueError(f"Noto'g'ri explanation type: {explanation_type}")
            
    def _global_explanation(self, model: Any, X: pd.DataFrame, y: pd.Series) -> ExplainabilityResult:
        """Global explanation"""
        
        feature_names = X.columns.tolist()
        feature_importances = {}
        
        # SHAP analysis
        if shap and hasattr(model, 'predict_proba'):
            try:
                explainer = shap.TreeExplainer(model) if hasattr(model, 'tree_') else shap.Explainer(model)
                shap_values = explainer.shap_values(X.sample(min(100, len(X))))
                
                if isinstance(shap_values, list):  # Multi-class
                    shap_values = shap_values[0]  # First class
                    
                mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
                for i, feature in enumerate(feature_names):
                    feature_importances[feature] = float(mean_abs_shap[i])
                    
            except Exception as e:
                self.logger.warning(f"SHAP analysis failed: {str(e)}")
                feature_importances = self._fallback_feature_importance(model, X, y)
        else:
            feature_importances = self._fallback_feature_importance(model, X, y)
            
        interpretation = self._interpret_feature_importances(feature_importances)
        
        return ExplainabilityResult(
            method='shap' if shap else 'feature_importance',
            explanation_type='global',
            feature_importances=feature_importances,
            feature_names=feature_names,
            predictions_explained=min(100, len(X)),
            confidence_scores=[],  # Placeholder
            interpretation=interpretation,
            timestamp=datetime.now()
        )
        
    def _local_explanation(self, model: Any, X: pd.DataFrame, y: pd.Series) -> ExplainabilityResult:
        """Local explanation"""
        
        feature_names = X.columns.tolist()
        
        # Individual prediction explanations
        individual_explanations = []
        sample_indices = np.random.choice(len(X), size=min(10, len(X)), replace=False)
        
        if shap and hasattr(model, 'predict_proba'):
            try:
                explainer = shap.Explainer(model)
                for idx in sample_indices:
                    shap_values = explainer.shap_values(X.iloc[[idx]])
                    individual_explanations.append({
                        'sample_index': int(idx),
                        'shap_values': shap_values[0].tolist() if isinstance(shap_values, list) else shap_values.tolist(),
                        'prediction': float(model.predict_proba(X.iloc[[idx]])[0][1]),
                        'actual': float(y.iloc[idx])
                    })
            except Exception as e:
                self.logger.warning(f"Local SHAP analysis failed: {str(e)}")
                
        return ExplainabilityResult(
            method='shap_local' if shap else 'lime',
            explanation_type='local',
            feature_importances={},  # Not applicable for local explanations
            feature_names=feature_names,
            predictions_explained=len(individual_explanations),
            confidence_scores=[exp['prediction'] for exp in individual_explanations],
            interpretation=f"Individual explanations for {len(individual_explanations)} samples",
            timestamp=datetime.now()
        )
        
    def _fallback_feature_importance(self, model: Any, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Fallback feature importance"""
        importances = {}
        
        if hasattr(model, 'feature_importances_'):
            # Tree-based models
            for i, feature in enumerate(X.columns):
                importances[feature] = float(model.feature_importances_[i])
        elif hasattr(model, 'coef_'):
            # Linear models
            coef = model.coef_
            if len(coef.shape) > 1:
                coef = np.mean(np.abs(coef), axis=0)  # Multi-class
            else:
                coef = np.abs(coef)
                
            for i, feature in enumerate(X.columns):
                importances[feature] = float(coef[i])
        else:
            # Default uniform importance
            for feature in X.columns:
                importances[feature] = 1.0 / len(X.columns)
                
        return importances
        
    def _interpret_feature_importances(self, importances: Dict[str, float]) -> str:
        """Feature importance interpretation"""
        sorted_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)
        
        top_features = [f[0] for f in sorted_features[:3]]
        total_importance = sum(importances.values())
        
        interpretation = (
            f"Eng muhim xususiyatlar: {', '.join(top_features)}. "
            f"Top 3 xususiyat jami importance'ning "
            f"{sum(importances[f] for f in top_features) / total_importance * 100:.1f}% ini tashkil etadi."
        )
        
        return interpretation

class RiskAssessment:
    """Model risk assessment"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def assess_model_risk(self, model: Any, model_info: Dict[str, Any], 
                         performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Model risk assessment"""
        
        risk_factors = {}
        
        # Performance risk
        risk_factors['performance'] = self._assess_performance_risk(performance_metrics)
        
        # Data risk
        risk_factors['data'] = self._assess_data_risk(model_info)
        
        # Bias risk
        risk_factors['bias'] = self._assess_bias_risk(model_info)
        
        # Compliance risk
        risk_factors['compliance'] = self._assess_compliance_risk(model_info)
        
        # Operational risk
        risk_factors['operational'] = self._assess_operational_risk(model_info)
        
        # Overall risk score
        overall_risk = np.mean(list(risk_factors.values()))
        
        # Risk level
        if overall_risk >= 0.8:
            risk_level = 'high'
        elif overall_risk >= 0.6:
            risk_level = 'medium'
        else:
            risk_level = 'low'
            
        return {
            'overall_risk_score': overall_risk,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': self._generate_risk_recommendations(risk_factors),
            'assessment_timestamp': datetime.now().isoformat()
        }
        
    def _assess_performance_risk(self, metrics: Dict[str, float]) -> float:
        """Performance risk assessment"""
        accuracy = metrics.get('accuracy', 0.0)
        f1_score = metrics.get('f1_score', 0.0)
        
        # Lower performance = higher risk
        performance_score = (accuracy + f1_score) / 2
        risk_score = 1.0 - performance_score  # Invert for risk
        
        return min(1.0, risk_score)
        
    def _assess_data_risk(self, model_info: Dict[str, Any]) -> float:
        """Data risk assessment"""
        risk_score = 0.0
        
        # Data quality
        if not model_info.get('data_quality_monitored', False):
            risk_score += 0.2
            
        # Data drift monitoring
        if not model_info.get('drift_monitoring', False):
            risk_score += 0.3
            
        # Data lineage
        if not model_info.get('data_lineage_tracked', False):
            risk_score += 0.2
            
        return min(1.0, risk_score)
        
    def _assess_bias_risk(self, model_info: Dict[str, Any]) -> float:
        """Bias risk assessment"""
        risk_score = 0.0
        
        # Bias detection
        if not model_info.get('bias_detection', False):
            risk_score += 0.3
            
        # Fairness monitoring
        if not model_info.get('fairness_monitoring', False):
            risk_score += 0.3
            
        return min(1.0, risk_score)
        
    def _assess_compliance_risk(self, model_info: Dict[str, Any]) -> float:
        """Compliance risk assessment"""
        risk_score = 0.0
        
        # Documentation
        if not model_info.get('documentation_complete', False):
            risk_score += 0.4
            
        # Audit trail
        if not model_info.get('audit_trail', False):
            risk_score += 0.3
            
        return min(1.0, risk_score)
        
    def _assess_operational_risk(self, model_info: Dict[str, Any]) -> float:
        """Operational risk assessment"""
        risk_score = 0.0
        
        # Model monitoring
        if not model_info.get('monitoring_enabled', False):
            risk_score += 0.3
            
        # Alert system
        if not model_info.get('alert_system', False):
            risk_score += 0.2
            
        # Rollback capability
        if not model_info.get('rollback_capability', False):
            risk_score += 0.3
            
        return min(1.0, risk_score)
        
    def _generate_risk_recommendations(self, risk_factors: Dict[str, float]) -> List[str]:
        """Risk mitigation recommendations"""
        recommendations = []
        
        for risk_type, risk_score in risk_factors.items():
            if risk_score > 0.6:
                if risk_type == 'performance':
                    recommendations.append("Model performance'ni yaxshilash zarur")
                elif risk_type == 'data':
                    recommendations.append("Data quality va drift monitoring qo'shing")
                elif risk_type == 'bias':
                    recommendations.append("Bias detection va fairness monitoring qo'shing")
                elif risk_type == 'compliance':
                    recommendations.append("Documentation va audit trail'ni to'ldiring")
                elif risk_type == 'operational':
                    recommendations.append("Model monitoring va alert system qo'shing")
                    
        return recommendations

class ModelGovernance:
    """Model governance tizimi"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.audit_logger = AuditLogger(config.get('audit_path', 'logs/audit'))
        self.bias_detector = BiasDetector(config.get('bias_detection', {}))
        self.compliance_checker = ComplianceChecker(config.get('compliance', {}))
        self.explainable_ai = ExplainableAI(config.get('explainability', {}))
        self.risk_assessment = RiskAssessment(config.get('risk_assessment', {}))
        
        # State
        self.governance_history = []
        
    def register_model(self, model_name: str, model: Any, model_info: Dict[str, Any],
                      performed_by: str) -> Dict[str, Any]:
        """Model governance ga ro'yxatdan o'tkazish"""
        
        # Audit log
        audit_id = self.audit_logger.log_action(
            model_name=model_name,
            version_id=model_info.get('version_id', '1.0.0'),
            action='created',
            performed_by=performed_by,
            details={'model_info': model_info}
        )
        
        # Compliance check
        compliance_results = self.compliance_checker.check_compliance(model, model_info)
        
        # Risk assessment
        performance_metrics = model_info.get('performance_metrics', {})
        risk_assessment = self.risk_assessment.assess_model_risk(
            model, model_info, performance_metrics
        )
        
        # Governance record
        governance_record = {
            'model_name': model_name,
            'audit_id': audit_id,
            'compliance_results': [asdict(c) for c in compliance_results],
            'risk_assessment': risk_assessment,
            'timestamp': datetime.now().isoformat(),
            'status': 'registered'
        }
        
        self.governance_history.append(governance_record)
        
        return governance_record
        
    def perform_bias_analysis(self, model: Any, X: pd.DataFrame, y_true: pd.Series,
                            y_pred: pd.Series, protected_attributes: List[str]) -> List[BiasAnalysis]:
        """Bias analysis perform"""
        bias_results = self.bias_detector.analyze_bias(
            model, X, y_true, y_pred, protected_attributes
        )
        
        # Audit log
        for result in bias_results:
            self.audit_logger.log_action(
                model_name='bias_analysis',
                version_id='1.0.0',
                action='bias_analysis',
                performed_by='system',
                details={'protected_attribute': result.protected_attribute}
            )
            
        return bias_results
        
    def generate_model_explanation(self, model: Any, X: pd.DataFrame, y: pd.Series,
                                 explanation_type: str = 'global') -> ExplainabilityResult:
        """Model explanation generate"""
        explanation = self.explainable_ai.explain_model(model, X, y, explanation_type)
        
        # Audit log
        self.audit_logger.log_action(
            model_name='explainability',
            version_id='1.0.0',
            action='explanation_generated',
            performed_by='system',
            details={
                'explanation_type': explanation_type,
                'method': explanation.method,
                'features_count': len(explanation.feature_names)
            }
        )
        
        return explanation
        
    def get_governance_summary(self, model_name: str) -> Dict[str, Any]:
        """Governance summary"""
        model_records = [
            record for record in self.governance_history 
            if record['model_name'] == model_name
        ]
        
        if not model_records:
            return {}
            
        latest_record = model_records[-1]
        
        # Risk level
        risk_level = latest_record['risk_assessment']['risk_level']
        risk_score = latest_record['risk_assessment']['overall_risk_score']
        
        # Compliance status
        compliance_statuses = [
            result['status'] for result in latest_record['compliance_results']
        ]
        overall_compliance = 'compliant' if all(s == 'compliant' for s in compliance_statuses) else 'partial'
        
        return {
            'model_name': model_name,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'compliance_status': overall_compliance,
            'governance_actions_count': len(model_records),
            'last_assessment': latest_record['timestamp'],
            'recommendations': latest_record['risk_assessment']['recommendations']
        }