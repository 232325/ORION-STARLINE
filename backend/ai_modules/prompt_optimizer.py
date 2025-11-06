"""
AI Prompt Optimizer - Meta-prompt optimization tizimi
Meta-maqsadlarga yo'naltirilgan prompt optimallashtirish va takomillashtirish
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from collections import defaultdict, Counter
import numpy as np
from context_engine import ContextAnalyzer, UserProfile, MarketContext
from prompt_templates import TemplateManager, PromptCategory, Template
import uuid

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """Prompt optimallashtirish strategiyalari"""
    CONTEXT_AWARE = "context_aware"
    PERFORMANCE_FOCUSED = "performance_focused"
    ADAPTIVE = "adaptive"
    PERSONALIZED = "personalized"
    KNOWLEDGE_INTEGRATED = "knowledge_integrated"
    REASONING_ENHANCED = "reasoning_enhanced"

class ResponseQualityMetrics(Enum):
    """Javob sifati metrikalari"""
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    ACTIONABILITY = "actionability"
    ENGAGEMENT = "engagement"

@dataclass
class OptimizationResult:
    """Optimallashtirish natijasi"""
    optimized_prompt: str
    original_prompt: str
    confidence_score: float
    optimization_applied: List[str]
    quality_metrics: Dict[str, float]
    context_used: Dict[str, Any]
    strategy_used: OptimizationStrategy
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    improvement_score: float = 0.0

@dataclass
class UserFeedback:
    """Foydalanuvchi fikr-mulohazasi"""
    user_id: str
    prompt_id: str
    quality_rating: float
    relevance_rating: float
    usefulness_rating: float
    feedback_text: Optional[str] = None
    timestamp: datetime = None
    success_outcome: bool = None

class PromptOptimizer:
    """Asosiy Prompt Optimizatsiyasi klassi"""
    
    def __init__(self, 
                 template_manager: TemplateManager = None,
                 context_analyzer: ContextAnalyzer = None,
                 knowledge_base: Dict[str, Any] = None):
        """
        Prompt Optimizer ni ishga tushirish
        
        Args:
            template_manager: Template boshqaruvchisi
            context_analyzer: Kontekst tahlil qiluvchi
            knowledge_base: Bilimlar bazasi
        """
        self.template_manager = template_manager or TemplateManager()
        self.context_analyzer = context_analyzer or ContextAnalyzer()
        self.knowledge_base = knowledge_base or {}
        
        # Performance tracking
        self.optimization_history: List[OptimizationResult] = []
        self.user_feedback: List[UserFeedback] = []
        self.quality_metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Strategy weights
        self.strategy_weights = {
            OptimizationStrategy.CONTEXT_AWARE: 0.3,
            OptimizationStrategy.PERFORMANCE_FOCUSED: 0.25,
            OptimizationStrategy.ADAPTIVE: 0.2,
            OptimizationStrategy.PERSONALIZED: 0.15,
            OptimizationStrategy.KNOWLEDGE_INTEGRATED: 0.1
        }
        
        # Pattern recognition
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        
        # A/B testing framework
        self.ab_tests = {}
        self.ab_results = {}
        
        logger.info("Prompt Optimizer initialized successfully")
    
    def optimize_prompt(self, 
                       original_prompt: str,
                       user_profile: UserProfile = None,
                       market_context: MarketContext = None,
                       strategy: OptimizationStrategy = OptimizationStrategy.ADAPTIVE,
                       context_data: Dict[str, Any] = None) -> OptimizationResult:
        """
        Promptni optimallashtirish
        
        Args:
            original_prompt: Asosiy prompt
            user_profile: Foydalanuvchi profili
            market_context: Bozor konteksti
            strategy: Optimallashtirish strategiyasi
            context_data: Qo'shimcha kontekst ma'lumotlari
            
        Returns:
            OptimizationResult: Optimallashtirilgan prompt va ma'lumotlar
        """
        try:
            # Create session ID
            session_id = str(uuid.uuid4())
            
            # Context analysis
            analysis_context = self._perform_context_analysis(
                original_prompt, user_profile, market_context, context_data
            )
            
            # Strategy-specific optimization
            optimized_prompt = self._apply_optimization_strategy(
                original_prompt, analysis_context, strategy
            )
            
            # Quality assessment
            quality_metrics = self._assess_response_quality(
                original_prompt, optimized_prompt, analysis_context
            )
            
            # Calculate improvement score
            improvement_score = self._calculate_improvement_score(
                original_prompt, optimized_prompt, quality_metrics
            )
            
            # Create result
            result = OptimizationResult(
                optimized_prompt=optimized_prompt,
                original_prompt=original_prompt,
                confidence_score=analysis_context.get('confidence', 0.5),
                optimization_applied=analysis_context.get('optimizations', []),
                quality_metrics=quality_metrics,
                context_used=analysis_context.get('context_summary', {}),
                strategy_used=strategy,
                timestamp=datetime.now(),
                user_id=user_profile.user_id if user_profile else None,
                session_id=session_id,
                improvement_score=improvement_score
            )
            
            # Store result
            self.optimization_history.append(result)
            
            # Update patterns
            self._update_success_patterns(result)
            
            logger.info(f"Prompt optimized with {improvement_score:.2%} improvement")
            return result
            
        except Exception as e:
            logger.error(f"Error in prompt optimization: {str(e)}")
            return self._create_fallback_result(original_prompt)
    
    def _perform_context_analysis(self, 
                                prompt: str,
                                user_profile: UserProfile = None,
                                market_context: MarketContext = None,
                                additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Kontekst tahlili"""
        context_data = {
            'prompt_analysis': self._analyze_prompt_structure(prompt),
            'user_context': self.context_analyzer.analyze_user_context(user_profile) if user_profile else {},
            'market_context': self.context_analyzer.analyze_market_context(market_context) if market_context else {},
            'historical_performance': self._get_historical_performance(prompt),
            'success_patterns': self._match_success_patterns(prompt)
        }
        
        if additional_context:
            context_data.update(additional_context)
        
        # Calculate confidence based on context richness
        context_richness = len([k for k, v in context_data.items() if v])
        context_data['confidence'] = min(0.9, 0.3 + (context_richness * 0.15))
        
        # Identify optimizations to apply
        context_data['optimizations'] = self._identify_optimizations(context_data)
        
        # Create context summary
        context_data['context_summary'] = self._create_context_summary(context_data)
        
        return context_data
    
    def _analyze_prompt_structure(self, prompt: str) -> Dict[str, Any]:
        """Prompt strukturasini tahlil qilish"""
        analysis = {
            'length': len(prompt),
            'word_count': len(prompt.split()),
            'complexity_score': self._calculate_complexity(prompt),
            'clarity_score': self._assess_clarity(prompt),
            'specificity_score': self._assess_specificity(prompt),
            'has_examples': 'masalan' in prompt.lower() or 'example' in prompt.lower(),
            'has_constraints': 'chegaralash' in prompt.lower() or 'constraint' in prompt.lower(),
            'has_questions': '?' in prompt,
            'sentiment': self._analyze_sentiment(prompt),
            'urgency': self._detect_urgency(prompt),
            'domain': self._identify_domain(prompt)
        }
        
        return analysis
    
    def _calculate_complexity(self, prompt: str) -> float:
        """Prompt murakkabligini hisoblash"""
        # Basic complexity metrics
        word_count = len(prompt.split())
        sentence_count = len(re.findall(r'[.!?]+', prompt))
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        
        # Technical terms detection
        technical_terms = len(re.findall(r'\b(trading|strategy|portfolio|risk|market|volatility)\b', prompt.lower()))
        
        complexity = (avg_words_per_sentence / 20) + (technical_terms / 10)
        return min(1.0, complexity)
    
    def _assess_clarity(self, prompt: str) -> float:
        """Prompt aniqligini baholash"""
        clarity_indicators = [
            'nimani' in prompt.lower(),
            'qanday' in prompt.lower(),
            'qachon' in prompt.lower(),
            'qayerda' in prompt.lower(),
            'nega' in prompt.lower()
        ]
        
        question_marks = prompt.count('?')
        has_structure = len(re.findall(r'\d+\.', prompt)) > 0
        
        clarity = (sum(clarity_indicators) / len(clarity_indicators)) + (question_marks / 3) + (has_structure * 0.3)
        return min(1.0, clarity)
    
    def _assess_specificity(self, prompt: str) -> float:
        """Prompt aniqligini baholash"""
        specific_indicators = [
            'USD' in prompt or 'EUR' in prompt or 'GBP' in prompt,
            re.search(r'\d+%', prompt),  # percentages
            re.search(r'\d+\.\d+', prompt),  # decimal numbers
            'AAPL' in prompt or 'GOOGL' in prompt or 'BTC' in prompt  # specific assets
        ]
        
        return sum(specific_indicators) / len(specific_indicators)
    
    def _analyze_sentiment(self, prompt: str) -> str:
        """Prompt kayfiyatini tahlil qilish"""
        positive_words = ['yaxshi', 'yutuq', 'foyda', 'muvaffaqiyat', 'yaxshi', 'kuchaytirish']
        negative_words = ['yomon', 'yo\'qotish', 'xavf', 'muammo', 'xavotir', 'qiyinchilik']
        
        pos_count = sum(1 for word in positive_words if word in prompt.lower())
        neg_count = sum(1 for word in negative_words if word in prompt.lower())
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _detect_urgency(self, prompt: str) -> str:
        """Darholikni aniqlash"""
        urgent_indicators = ['darhol', 'tez', 'shoshilinch', 'tugallash', 'davr']
        
        urgent_count = sum(1 for word in urgent_indicators if word in prompt.lower())
        
        if urgent_count >= 2:
            return 'high'
        elif urgent_count == 1:
            return 'medium'
        else:
            return 'low'
    
    def _identify_domain(self, prompt: str) -> str:
        """Domain sohasini aniqlash"""
        domains = {
            'trading': ['savdo', 'sotib olish', 'sotish', 'strategiya', 'pozitsiya'],
            'risk': ['xavf', 'qaytarish', 'muammo', 'chegaralash'],
            'portfolio': 'portfel',
            'market': 'bozor',
            'analysis': 'tahlil',
            'education': 'organish'
        }
        
        for domain, keywords in domains.items():
            if isinstance(keywords, str):
                keywords = [keywords]
            
            if any(keyword in prompt.lower() for keyword in keywords):
                return domain
        
        return 'general'
    
    def _apply_optimization_strategy(self, 
                                   prompt: str, 
                                   context: Dict[str, Any], 
                                   strategy: OptimizationStrategy) -> str:
        """Optimallashtirish strategiyasini qo'llash"""
        if strategy == OptimizationStrategy.CONTEXT_AWARE:
            return self._context_aware_optimization(prompt, context)
        elif strategy == OptimizationStrategy.PERFORMANCE_FOCUSED:
            return self._performance_focused_optimization(prompt, context)
        elif strategy == OptimizationStrategy.ADAPTIVE:
            return self._adaptive_optimization(prompt, context)
        elif strategy == OptimizationStrategy.PERSONALIZED:
            return self._personalized_optimization(prompt, context)
        elif strategy == OptimizationStrategy.KNOWLEDGE_INTEGRATED:
            return self._knowledge_integrated_optimization(prompt, context)
        elif strategy == OptimizationStrategy.REASONING_ENHANCED:
            return self._reasoning_enhanced_optimization(prompt, context)
        else:
            return prompt
    
    def _context_aware_optimization(self, prompt: str, context: Dict[str, Any]) -> str:
        """Kontekstga qarab optimallashtirish"""
        optimized = prompt
        
        # Add relevant context hints
        domain = context.get('prompt_analysis', {}).get('domain', 'general')
        user_context = context.get('user_context', {})
        market_context = context.get('market_context', {})
        
        # Add domain-specific enhancements
        if domain == 'trading':
            optimized = self._add_trading_context(optimized, market_context)
        elif domain == 'risk':
            optimized = self._add_risk_context(optimized, market_context)
        elif domain == 'portfolio':
            optimized = self._add_portfolio_context(optimized, user_context)
        
        # Add specificity improvements
        specificity = context.get('prompt_analysis', {}).get('specificity_score', 0.5)
        if specificity < 0.6:
            optimized = self._improve_specificity(optimized, context)
        
        # Add clarity improvements
        clarity = context.get('prompt_analysis', {}).get('clarity_score', 0.5)
        if clarity < 0.6:
            optimized = self._improve_clarity(optimized)
        
        return optimized
    
    def _performance_focused_optimization(self, prompt: str, context: Dict[str, Any]) -> str:
        """Ishlashga yo'naltirilgan optimallashtirish"""
        optimized = prompt
        
        # Use successful patterns
        success_patterns = context.get('success_patterns', [])
        if success_patterns:
            optimized = self._apply_success_patterns(optimized, success_patterns)
        
        # Add performance metrics
        optimized = self._add_performance_metrics(optimized)
        
        # Add actionability
        optimized = self._enhance_actionability(optimized)
        
        return optimized
    
    def _adaptive_optimization(self, prompt: str, context: Dict[str, Any]) -> str:
        """Moslashuvchan optimallashtirish"""
        # Combine multiple strategies
        optimized = self._context_aware_optimization(prompt, context)
        optimized = self._performance_focused_optimization(optimized, context)
        optimized = self._personalized_optimization(optimized, context)
        
        return optimized
    
    def _personalized_optimization(self, prompt: str, context: Dict[str, Any]) -> str:
        """Shaxsiylashtirilgan optimallashtirish"""
        user_context = context.get('user_context', {})
        optimized = prompt
        
        # Adapt to user skill level
        skill_level = user_context.get('skill_level', 'intermediate')
        optimized = self._adapt_to_skill_level(optimized, skill_level)
        
        # Adapt to communication style
        style = user_context.get('communication_style', 'formal')
        optimized = self._adapt_communication_style(optimized, style)
        
        # Adapt to learning preferences
        learning_pref = user_context.get('learning_preference', 'visual')
        optimized = self._adapt_learning_style(optimized, learning_pref)
        
        return optimized
    
    def _knowledge_integrated_optimization(self, prompt: str, context: Dict[str, Any]) -> str:
        """Bilimlar bazasini integratsiyalash"""
        optimized = prompt
        
        # Add relevant knowledge context
        domain = context.get('prompt_analysis', {}).get('domain', 'general')
        if domain in self.knowledge_base:
            knowledge = self.knowledge_base[domain]
            optimized = self._integrate_domain_knowledge(optimized, knowledge)
        
        # Add best practices
        optimized = self._add_best_practices(optimized, domain)
        
        # Add expert insights
        optimized = self._add_expert_insights(optimized, domain)
        
        return optimized
    
    def _reasoning_enhanced_optimization(self, prompt: str, context: Dict[str, Any]) -> str:
        """Mulohazani kuchaytirish"""
        optimized = prompt
        
        # Add reasoning frameworks
        optimized = self._add_reasoning_steps(optimized)
        
        # Add decision trees
        optimized = self._add_decision_framework(optimized)
        
        # Add logic patterns
        optimized = self._enhance_logical_structure(optimized)
        
        return optimized
    
    def _assess_response_quality(self, original: str, optimized: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Javob sifatini baholash"""
        metrics = {}
        
        # Original prompt analysis
        orig_clarity = self._assess_clarity(original)
        orig_specificity = self._assess_specificity(original)
        orig_complexity = self._calculate_complexity(original)
        
        # Optimized prompt analysis
        opt_clarity = self._assess_clarity(optimized)
        opt_specificity = self._assess_specificity(optimized)
        opt_complexity = self._calculate_complexity(optimized)
        
        # Quality scores
        metrics[ResponseQualityMetrics.ACCURACY.value] = min(1.0, (opt_specificity + orig_specificity) / 2)
        metrics[ResponseQualityMetrics.RELEVANCE.value] = min(1.0, opt_clarity)
        metrics[ResponseQualityMetrics.COMPLETENESS.value] = min(1.0, opt_complexity)
        metrics[ResponseQualityMetrics.CLARITY.value] = opt_clarity
        metrics[ResponseQualityMetrics.ACTIONABILITY.value] = self._assess_actionability(optimized)
        metrics[ResponseQualityMetrics.ENGAGEMENT.value] = self._assess_engagement(optimized, context)
        
        return metrics
    
    def _calculate_improvement_score(self, original: str, optimized: str, quality_metrics: Dict[str, float]) -> float:
        """Yaxshilash ballini hisoblash"""
        # Compare key metrics between original and optimized
        orig_clarity = self._assess_clarity(original)
        orig_specificity = self._assess_specificity(original)
        
        opt_clarity = quality_metrics.get('clarity', 0)
        opt_specificity = quality_metrics.get('accuracy', 0)
        opt_completeness = quality_metrics.get('completeness', 0)
        
        # Calculate improvements
        clarity_improvement = opt_clarity - orig_clarity
        specificity_improvement = opt_specificity - orig_specificity
        completeness_score = opt_completeness
        
        # Weighted improvement score
        improvement = (clarity_improvement * 0.3 + 
                      specificity_improvement * 0.4 + 
                      completeness_score * 0.3)
        
        return max(0.0, improvement)
    
    def _create_fallback_result(self, prompt: str) -> OptimizationResult:
        """Xato holatida rezerv natija"""
        return OptimizationResult(
            optimized_prompt=prompt,
            original_prompt=prompt,
            confidence_score=0.1,
            optimization_applied=[],
            quality_metrics={'fallback': 0.5},
            context_used={},
            strategy_used=OptimizationStrategy.ADAPTIVE,
            timestamp=datetime.now()
        )
    
    def _get_historical_performance(self, prompt: str) -> Dict[str, float]:
        """Tarixiy ishlamani olish"""
        # This would typically query a database
        # For now, return basic metrics
        return {
            'success_rate': 0.7,
            'avg_quality': 0.6,
            'usage_count': 10
        }
    
    def _match_success_patterns(self, prompt: str) -> List[str]:
        """Muvaffaqiyatli namunalarini topish"""
        # Pattern matching logic
        patterns = []
        
        if 'qanday' in prompt.lower() and 'strategiya' in prompt.lower():
            patterns.append('strategy_question')
        
        if 'risk' in prompt.lower() or 'xavf' in prompt.lower():
            patterns.append('risk_analysis')
        
        return patterns
    
    def _identify_optimizations(self, context: Dict[str, Any]) -> List[str]:
        """Qaysi optimallashtirishlarni qo'llash kerakligini aniqlash"""
        optimizations = []
        
        prompt_analysis = context.get('prompt_analysis', {})
        
        if prompt_analysis.get('clarity_score', 1) < 0.6:
            optimizations.append('improve_clarity')
        
        if prompt_analysis.get('specificity_score', 1) < 0.6:
            optimizations.append('improve_specificity')
        
        if prompt_analysis.get('complexity_score', 0) > 0.8:
            optimizations.append('reduce_complexity')
        
        if not prompt_analysis.get('has_examples', False):
            optimizations.append('add_examples')
        
        if not prompt_analysis.get('has_constraints', False):
            optimizations.append('add_constraints')
        
        return optimizations
    
    def _create_context_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Kontekst xulosasini yaratish"""
        summary = {
            'domain': context.get('prompt_analysis', {}).get('domain', 'general'),
            'complexity': context.get('prompt_analysis', {}).get('complexity_score', 0.5),
            'user_level': context.get('user_context', {}).get('skill_level', 'unknown'),
            'market_regime': context.get('market_context', {}).get('regime', 'unknown'),
            'optimization_priority': context.get('optimizations', [])
        }
        
        return summary
    
    # Additional helper methods for specific optimizations
    def _add_trading_context(self, prompt: str, market_context: Dict[str, Any]) -> str:
        """Savdo kontekstini qo'shish"""
        if market_context.get('regime') == 'volatile':
            return f"{prompt}\n\nE'tibor: hozirgi bozor yuqori o'zgaruvchan. Xavfni boshqarish strategiyalariga e'tibor bering."
        return prompt
    
    def _add_risk_context(self, prompt: str, market_context: Dict[str, Any]) -> str:
        """Xavf kontekstini qo'shish"""
        return f"{prompt}\n\nXavf boshqaruvi: barcha tavsiyalarni o'z portfel xavf profilingizga mos ravishda baholang."
    
    def _add_portfolio_context(self, prompt: str, user_context: Dict[str, Any]) -> str:
        """Portfel kontekstini qo'shish"""
        risk_profile = user_context.get('risk_profile', 'moderate')
        return f"{prompt}\n\nPortfel konteksti: Sizning {risk_profile} xavf profilingizni hisobga oling."
    
    def _improve_specificity(self, prompt: str, context: Dict[str, Any]) -> str:
        """Aniqligini yaxshilash"""
        return f"{prompt}\n\nIltimos, aniq va o'lchanadigan natijalarga e'tibor bering."
    
    def _improve_clarity(self, prompt: str) -> str:
        """Aniqligini yaxshilash"""
        return f"{prompt}\n\nAniqroq savollar bering:\n- Qanday maqsadga erishmoqchisiz?\n- Qaysi vaqt oralig'i muhim?\n- Qanday natijalarni kutmoqdisiz?"
    
    def _add_performance_metrics(self, prompt: str) -> str:
        """Ishlash metrikalarini qo'shish"""
        return f"{prompt}\n\nIshlash kuzatuvi:\n- Foydali natijalar foizini aniqlang\n- Oqilona qarorlar qabul qilish vaqtini o'lchang\n- Xatolar sonini kamaytiring"
    
    def _enhance_actionability(self, prompt: str) -> str:
        """Harakat qilish qobiliyatini kuchaytirish"""
        return f"{prompt}\n\nAmal qilish uchun:\n1. Aniq qadamlarni belgilang\n2. Vaqt jadvalini tuzing\n3. O'lchash mumkin maqsadlarni qo'ying\n4. Jarayonni kuzating"
    
    def _apply_success_patterns(self, prompt: str, patterns: List[str]) -> str:
        """Muvaffaqiyatli namunalarni qo'llash"""
        enhanced = prompt
        
        for pattern in patterns:
            if pattern == 'strategy_question':
                enhanced += "\n\nStrategiya tayyorlash:\n- Maqsadlar\n- Resurslar\n- Vaqt jadvali\n- Muvaffaqiyat mezonlari"
            elif pattern == 'risk_analysis':
                enhanced += "\n\nXavf tahlili:\n- Ehtimoliy xatarlar\n- Ta'sir darajasi\n- Oldini olish choralari\n- Zaxira reja"
        
        return enhanced
    
    def _adapt_to_skill_level(self, prompt: str, skill_level: str) -> str:
        """Malaka darajasiga moslashtirish"""
        if skill_level == 'beginner':
            return f"{prompt}\n\nBoshlang'ich tushuntirish: Har bir qadamni batafsil tushuntiring va asosiy tushunchalarni qisqacha izohlang."
        elif skill_level == 'advanced':
            return f"{prompt}\n\nIlg'or yondashuv: Chuqur tahlil va murakkab strategiyalarni qo'llang."
        return prompt
    
    def _adapt_communication_style(self, prompt: str, style: str) -> str:
        """Muloqot uslubini moslashtirish"""
        if style == 'casual':
            return f"{prompt}\n\nRasmiy bo'lmagan uslub: Oddiy tilda yozing va yaxshi muloqot qiling."
        elif style == 'formal':
            return f"{prompt}\n\nRasmiy uslub: Texnik atamalar va aniq ifodalarni qo'llang."
        return prompt
    
    def _adapt_learning_style(self, prompt: str, learning_pref: str) -> str:
        """O'rganish uslubini moslashtirish"""
        if learning_pref == 'visual':
            return f"{prompt}\n\nVizual o'rganish: Jadvallar, grafiklar va diagrammalardan foydalaning."
        elif learning_pref == 'auditory':
            return f"{prompt}\n\nAudio o'rganish: Tushuntirishlarni ovozli formatda taqdim eting."
        elif learning_pref == 'kinesthetic':
            return f"{prompt}\n\nAmaliy o'rganish: Qadamlarni bajarish va amaliy mashqlarni qo'llang."
        return prompt
    
    def _integrate_domain_knowledge(self, prompt: str, knowledge: Dict[str, Any]) -> str:
        """Domain bilimlarini integratsiyalash"""
        best_practices = knowledge.get('best_practices', [])
        if best_practices:
            practices_text = "\n".join([f"- {practice}" for practice in best_practices[:3]])
            return f"{prompt}\n\nEng yaxshi amaliyotlar:\n{practices_text}"
        return prompt
    
    def _add_best_practices(self, prompt: str, domain: str) -> str:
        """Eng yaxshi amaliyotlarni qo'shish"""
        practices = {
            'trading': [
                "Riskni diversifikatsiya qiling",
                "Stop-loss buyurtmalarini o'rnating",
                "Emotsiyalarni nazoratda saqlang"
            ],
            'risk': [
                "Hamma xavflarni hisoblang",
                "Zaxira rejalar tayyorlang",
                "Muntazam monitoring qiling"
            ]
        }
        
        if domain in practices:
            practice_text = "\n".join([f"- {p}" for p in practices[domain]])
            return f"{prompt}\n\nEng yaxshi amaliyotlar:\n{practice_text}"
        return prompt
    
    def _add_expert_insights(self, prompt: str, domain: str) -> str:
        """Ekspert fikrlarini qo'shish"""
        insights = {
            'trading': "Tajribali treyderlar ko'pincha bozor kayfiyatidan ko'ra ma'lumotlarga tayanishadi.",
            'risk': "Eng yaxshi xavf boshqaruvi - oldindan rejalash va tizimli yondashuv.",
            'portfolio': "Diversifikatsiya - bu nafaqat aktivlarni tarqatish, balki xavflarni boshqarish san'ati."
        }
        
        if domain in insights:
            return f"{prompt}\n\nEkspert maslahati: {insights[domain]}"
        return prompt
    
    def _add_reasoning_steps(self, prompt: str) -> str:
        """Mulohaz qadamlarini qo'shish"""
        return f"{prompt}\n\nMulohaz qadamlari:\n1. Ma'lumotlarni to'plang\n2. Variantlarni baholang\n3. Qaror qabul qiling\n4. Natijalarni kuzating"
    
    def _add_decision_framework(self, prompt: str) -> str:
        """Qaror qabul qilish freymvorkini qo'shish"""
        return f"{prompt}\n\nQaror qabul qilish:\n- Maqsadlar: Nima erishishni xohlaysiz?\n- Variantlar: Qanday imkoniyatlar bor?\n- Baholash: Har bir variantni qanday baholaysiz?\n- Tanlash: Eng yaxshi variantni qanday tanlaymiz?"
    
    def _enhance_logical_structure(self, prompt: str) -> str:
        """Mantiqiy tuzilmani kuchaytirish"""
        return f"{prompt}\n\nMantiqiy tuzilma:\n- **Keling**: Vazifa va maqsadlar\n- **Nega**: Sabab va asoslar\n- **Qanday**: Amal qilish yo'llari\n- **Qachon**: Vaqt jadvali va muddatlar"
    
    def _assess_actionability(self, prompt: str) -> float:
        """Harakat qilish qobiliyatini baholash"""
        action_indicators = [
            'qadamlarni', 'amal', 'qabul', 'bajarish', 'qiling', 'qollang'
        ]
        
        action_count = sum(1 for indicator in action_indicators if indicator in prompt.lower())
        return min(1.0, action_count / len(action_indicators))
    
    def _assess_engagement(self, prompt: str, context: Dict[str, Any]) -> float:
        """Jalb qilish darajasini baholash"""
        engagement_indicators = [
            'qiziqarli', 'muhokama', 'fikr', 'tajriba', 'o\'z', 'ma\'lumot'
        ]
        
        engagement_count = sum(1 for indicator in engagement_indicators if indicator in prompt.lower())
        base_score = engagement_count / len(engagement_indicators)
        
        # Adjust based on user context
        user_context = context.get('user_context', {})
        if user_context.get('interaction_style') == 'engaged':
            base_score += 0.2
        
        return min(1.0, base_score)
    
    def _update_success_patterns(self, result: OptimizationResult):
        """Muvaffaqiyatli namunalarni yangilash"""
        # This would typically be called with actual user feedback
        # For now, we'll simulate pattern updates
        pattern_key = result.context_used.get('domain', 'general')
        
        if result.improvement_score > 0.1:
            self.success_patterns[pattern_key].append({
                'prompt_hash': hashlib.md5(result.optimized_prompt.encode()).hexdigest(),
                'improvement': result.improvement_score,
                'timestamp': result.timestamp
            })
            
            # Keep only recent patterns
            cutoff_date = datetime.now() - timedelta(days=30)
            self.success_patterns[pattern_key] = [
                p for p in self.success_patterns[pattern_key] 
                if p['timestamp'] > cutoff_date
            ]
    
    def record_user_feedback(self, feedback: UserFeedback):
        """Foydalanuvchi fikr-mulohazasini qayd etish"""
        self.user_feedback.append(feedback)
        
        # Update quality metrics
        self.quality_metrics['quality_rating'].append(feedback.quality_rating)
        self.quality_metrics['relevance_rating'].append(feedback.relevance_rating)
        self.quality_metrics['usefulness_rating'].append(feedback.usefulness_rating)
        
        # Update patterns based on feedback
        if feedback.quality_rating > 0.7:
            # Positive feedback - update success patterns
            pass
        elif feedback.quality_rating < 0.3:
            # Negative feedback - update failure patterns
            pass
    
    def get_optimization_analytics(self) -> Dict[str, Any]:
        """Optimallashtirish analitikasi"""
        if not self.optimization_history:
            return {'message': 'No optimization history available'}
        
        # Calculate statistics
        total_optimizations = len(self.optimization_history)
        avg_improvement = np.mean([r.improvement_score for r in self.optimization_history])
        avg_confidence = np.mean([r.confidence_score for r in self.optimization_history])
        
        # Strategy usage
        strategy_usage = Counter([r.strategy_used.value for r in self.optimization_history])
        
        # Quality trends
        quality_trends = {}
        for metric in ResponseQualityMetrics:
            scores = [r.quality_metrics.get(metric.value, 0) for r in self.optimization_history]
            quality_trends[metric.value] = {
                'average': np.mean(scores),
                'trend': 'improving' if len(scores) > 5 and scores[-5] < scores[-1] else 'stable'
            }
        
        # Most successful optimizations
        top_optimizations = sorted(
            self.optimization_history, 
            key=lambda x: x.improvement_score, 
            reverse=True
        )[:5]
        
        return {
            'summary': {
                'total_optimizations': total_optimizations,
                'average_improvement': avg_improvement,
                'average_confidence': avg_confidence
            },
            'strategy_usage': dict(strategy_usage),
            'quality_trends': quality_trends,
            'top_optimizations': [
                {
                    'original_prompt': opt.original_prompt[:100] + '...' if len(opt.original_prompt) > 100 else opt.original_prompt,
                    'improvement_score': opt.improvement_score,
                    'strategies_used': opt.optimization_applied
                }
                for opt in top_optimizations
            ]
        }
    
    def start_ab_test(self, test_name: str, original_prompt: str, optimized_prompt: str, 
                     traffic_split: float = 0.5) -> str:
        """A/B testni boshlash"""
        test_id = str(uuid.uuid4())
        
        self.ab_tests[test_id] = {
            'name': test_name,
            'original_prompt': original_prompt,
            'optimized_prompt': optimized_prompt,
            'traffic_split': traffic_split,
            'start_time': datetime.now(),
            'results': {
                'original': {'clicks': 0, 'conversions': 0, 'quality_scores': []},
                'optimized': {'clicks': 0, 'conversions': 0, 'quality_scores': []}
            }
        }
        
        logger.info(f"Started A/B test: {test_name} with ID: {test_id}")
        return test_id
    
    def record_ab_test_interaction(self, test_id: str, variant: str, 
                                 quality_score: float = None, conversion: bool = None):
        """A/B test o'zaro ta'sirini qayd etish"""
        if test_id not in self.ab_tests:
            logger.warning(f"Test ID {test_id} not found")
            return
        
        test = self.ab_tests[test_id]
        if variant not in ['original', 'optimized']:
            logger.warning(f"Invalid variant: {variant}")
            return
        
        # Update interaction count
        test['results'][variant]['clicks'] += 1
        
        # Record conversion if provided
        if conversion is not None:
            test['results'][variant]['conversions'] += 1
        
        # Record quality score if provided
        if quality_score is not None:
            test['results'][variant]['quality_scores'].append(quality_score)
    
    def get_ab_test_results(self, test_id: str) -> Dict[str, Any]:
        """A/B test natijalarini olish"""
        if test_id not in self.ab_tests:
            return {'error': 'Test not found'}
        
        test = self.ab_tests[test_id]
        results = test['results']
        
        # Calculate metrics
        original_metrics = self._calculate_variant_metrics(results['original'])
        optimized_metrics = self._calculate_variant_metrics(results['optimized'])
        
        # Statistical significance (simplified)
        significance = self._calculate_significance(results)
        
        return {
            'test_name': test['name'],
            'duration': (datetime.now() - test['start_time']).days,
            'original': original_metrics,
            'optimized': optimized_metrics,
            'improvement': {
                'quality': optimized_metrics['avg_quality'] - original_metrics['avg_quality'],
                'conversion_rate': optimized_metrics['conversion_rate'] - original_metrics['conversion_rate']
            },
            'significance': significance,
            'winner': 'optimized' if optimized_metrics['conversion_rate'] > original_metrics['conversion_rate'] else 'original'
        }
    
    def _calculate_variant_metrics(self, variant_results: Dict[str, Any]) -> Dict[str, float]:
        """Variant metrikalarini hisoblash"""
        clicks = variant_results['clicks']
        conversions = variant_results['conversions']
        quality_scores = variant_results['quality_scores']
        
        return {
            'clicks': clicks,
            'conversions': conversions,
            'conversion_rate': conversions / max(clicks, 1),
            'avg_quality': np.mean(quality_scores) if quality_scores else 0,
            'total_interactions': clicks
        }
    
    def _calculate_significance(self, results: Dict[str, Any]) -> float:
        """Statistik muhimlikni hisoblash (soddalashtirilgan)"""
        # This is a simplified calculation
        # In practice, you'd use proper statistical tests
        original_rate = results['original']['conversions'] / max(results['original']['clicks'], 1)
        optimized_rate = results['optimized']['conversions'] / max(results['optimized']['clicks'], 1)
        
        total_clicks = results['original']['clicks'] + results['optimized']['clicks']
        if total_clicks < 100:  # Not enough data
            return 0.0
        
        # Simplified significance calculation
        difference = abs(optimized_rate - original_rate)
        significance = min(1.0, difference * total_clicks / 10)
        
        return significance

# Usage example and testing
if __name__ == "__main__":
    # Initialize optimizer
    optimizer = PromptOptimizer()
    
    # Example usage
    sample_prompt = "Yaxshi savdo strategiyasini ayting"
    
    result = optimizer.optimize_prompt(
        original_prompt=sample_prompt,
        strategy=OptimizationStrategy.CONTEXT_AWARE
    )
    
    print("Original Prompt:", result.original_prompt)
    print("Optimized Prompt:", result.optimized_prompt)
    print("Improvement Score:", f"{result.improvement_score:.2%}")
    print("Quality Metrics:", result.quality_metrics)