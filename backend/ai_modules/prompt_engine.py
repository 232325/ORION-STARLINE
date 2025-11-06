"""
Advanced Prompt Engineering System
Professional prompt engineering engine for Orion Starline AI Trading Platform

This module provides comprehensive prompt engineering capabilities including:
- Dynamic prompt generation with context awareness
- Multi-language support and translation
- A/B testing and performance optimization
- Safety and compliance validation
- Conversation management
- Performance analytics and insights
- Industry best practices integration
- Automatic prompt improvement
"""

import json
import logging
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import re
import hashlib

from prompt_templates import (
    TemplateManager, Template, PromptCategory, TemplateType, 
    SkillLevel, Language
)


class PromptResult:
    """Prompt generation result with metadata"""
    
    def __init__(self, 
                 prompt_id: str,
                 generated_prompt: str,
                 template_id: str,
                 generation_time: float,
                 context_used: Dict[str, Any],
                 user_profile: Dict[str, Any] = None):
        
        self.prompt_id = prompt_id
        self.generated_prompt = generated_prompt
        self.template_id = template_id
        self.generation_time = generation_time
        self.context_used = context_used
        self.user_profile = user_profile or {}
        self.timestamp = datetime.now(timezone.utc)
        self.quality_score = 0.0
        self.safety_validated = False
        self.compliance_checked = False
        self.performance_metrics = {}
        self.optimization_applied = False
        self.language_used = "uzbek"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'prompt_id': self.prompt_id,
            'generated_prompt': self.generated_prompt,
            'template_id': self.template_id,
            'generation_time': self.generation_time,
            'context_used': self.context_used,
            'user_profile': self.user_profile,
            'timestamp': self.timestamp.isoformat(),
            'quality_score': self.quality_score,
            'safety_validated': self.safety_validated,
            'compliance_checked': self.compliance_checked,
            'performance_metrics': self.performance_metrics,
            'optimization_applied': self.optimization_applied,
            'language_used': self.language_used
        }


class ConversationContext:
    """Multi-turn conversation context manager"""
    
    def __init__(self, conversation_id: str = None):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.history: List[Dict[str, Any]] = []
        self.current_context: Dict[str, Any] = {}
        self.user_profile: Dict[str, Any] = {}
        self.language = Language.UZBEK
        self.start_time = datetime.now(timezone.utc)
        self.last_activity = self.start_time
        
    def add_exchange(self, user_input: str, ai_response: str, metadata: Dict[str, Any] = None):
        """Add user-AI exchange to history"""
        exchange = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user_input': user_input,
            'ai_response': ai_response,
            'metadata': metadata or {}
        }
        self.history.append(exchange)
        self.last_activity = datetime.now(timezone.utc)
        
    def get_recent_history(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        return self.history[-count:] if count > 0 else self.history
        
    def update_context(self, new_context: Dict[str, Any]):
        """Update conversation context"""
        self.current_context.update(new_context)
        self.last_activity = datetime.now(timezone.utc)
        
    def update_user_profile(self, new_profile: Dict[str, Any]):
        """Update user profile"""
        self.user_profile.update(new_profile)
        
    def get_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            'conversation_id': self.conversation_id,
            'exchange_count': len(self.history),
            'duration_minutes': (self.last_activity - self.start_time).total_seconds() / 60,
            'current_context': self.current_context,
            'user_profile': self.user_profile,
            'language': self.language.value,
            'last_activity': self.last_activity.isoformat()
        }


class ABTestManager:
    """A/B testing manager for prompt optimization"""
    
    def __init__(self):
        self.active_tests: Dict[str, Dict[str, Any]] = {}
        self.completed_tests: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        
    def create_test(self, 
                   test_name: str,
                   template_id: str,
                   base_context: Dict[str, Any],
                   test_variants: List[str],
                   test_duration_hours: int = 24,
                   success_metric: str = "user_rating") -> str:
        """Create new A/B test"""
        
        test_id = str(uuid.uuid4())
        
        self.active_tests[test_id] = {
            'test_id': test_id,
            'test_name': test_name,
            'template_id': template_id,
            'base_context': base_context,
            'test_variants': test_variants,
            'start_time': datetime.now(timezone.utc),
            'end_time': datetime.now(timezone.utc).timestamp() + (test_duration_hours * 3600),
            'success_metric': success_metric,
            'results': {variant: [] for variant in test_variants},
            'participant_count': 0
        }
        
        self.logger.info(f"Created A/B test {test_id} for template {template_id}")
        return test_id
    
    def assign_variant(self, test_id: str, user_id: str) -> Optional[str]:
        """Assign user to test variant"""
        
        if test_id not in self.active_tests:
            return None
            
        test = self.active_tests[test_id]
        
        # Simple random assignment (can be improved with user profiling)
        import random
        variant = random.choice(test['test_variants'])
        
        test['participant_count'] += 1
        
        self.logger.info(f"Assigned user {user_id} to variant {variant} in test {test_id}")
        return variant
    
    def record_result(self, test_id: str, variant: str, result: Dict[str, Any]):
        """Record test result"""
        
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            if variant in test['results']:
                test['results'][variant].append({
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'result': result
                })
    
    def get_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get current test results"""
        
        if test_id not in self.active_tests:
            return None
            
        test = self.active_tests[test_id]
        
        # Calculate variant performance
        variant_performance = {}
        for variant, results in test['results'].items():
            if results:
                # Calculate average performance for the success metric
                metric_values = [r['result'].get(test['success_metric'], 0) for r in results]
                variant_performance[variant] = {
                    'sample_size': len(results),
                    'avg_performance': sum(metric_values) / len(metric_values),
                    'std_dev': self._calculate_std_dev(metric_values)
                }
            else:
                variant_performance[variant] = {
                    'sample_size': 0,
                    'avg_performance': 0,
                    'std_dev': 0
                }
        
        return {
            'test_info': test,
            'variant_performance': variant_performance,
            'is_completed': datetime.now(timezone.utc).timestamp() > test['end_time']
        }
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5


class PromptOptimizer:
    """Automatic prompt optimization based on performance data"""
    
    def __init__(self):
        self.optimization_rules: List[Callable] = []
        self.performance_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
    def analyze_performance(self, prompt_results: List[PromptResult]) -> Dict[str, Any]:
        """Analyze prompt performance and suggest optimizations"""
        
        if not prompt_results:
            return {'suggestions': [], 'overall_score': 0.0}
        
        # Calculate performance metrics
        avg_quality_score = sum(r.quality_score for r in prompt_results) / len(prompt_results)
        avg_generation_time = sum(r.generation_time for r in prompt_results) / len(prompt_results)
        
        # Analyze success patterns
        successful_prompts = [r for r in prompt_results if r.quality_score > 0.7]
        unsuccessful_prompts = [r for r in prompt_results if r.quality_score <= 0.7]
        
        suggestions = []
        
        # Quality-based suggestions
        if avg_quality_score < 0.7:
            suggestions.append({
                'type': 'quality_improvement',
                'description': 'Overall quality score is low',
                'recommendation': 'Simplify language and add more examples',
                'priority': 'high'
            })
        
        # Speed-based suggestions
        if avg_generation_time > 2.0:  # 2 seconds
            suggestions.append({
                'type': 'speed_optimization', 
                'description': 'Generation time is slow',
                'recommendation': 'Reduce prompt complexity and optimize template structure',
                'priority': 'medium'
            })
        
        # Context effectiveness
        if len(unsuccessful_prompts) > len(successful_prompts):
            suggestions.append({
                'type': 'context_enhancement',
                'description': 'Context may not be effectively utilized',
                'recommendation': 'Improve context-aware prompt generation',
                'priority': 'high'
            })
        
        return {
            'suggestions': suggestions,
            'overall_score': avg_quality_score,
            'performance_metrics': {
                'avg_quality_score': avg_quality_score,
                'avg_generation_time': avg_generation_time,
                'success_rate': len(successful_prompts) / len(prompt_results),
                'total_prompts': len(prompt_results)
            }
        }
    
    def suggest_optimizations(self, template: Template, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest specific optimizations for a template"""
        
        suggestions = []
        
        # Template-specific optimization logic
        if performance_data.get('avg_rating', 0) < 4.0:
            suggestions.append({
                'type': 'content_enhancement',
                'change': 'Add more detailed explanations',
                'reason': 'User ratings suggest content is unclear',
                'implementation': 'Expand examples and add step-by-step guidance'
            })
        
        if performance_data.get('completion_rate', 0) < 0.8:
            suggestions.append({
                'type': 'structure_improvement',
                'change': 'Simplify prompt structure',
                'reason': 'Low completion rate indicates complexity issues',
                'implementation': 'Break complex tasks into smaller steps'
            })
        
        return suggestions


class AdvancedPromptEngine:
    """Main prompt engineering engine with advanced features"""
    
    def __init__(self, 
                 template_manager: TemplateManager = None,
                 enable_ab_testing: bool = True,
                 enable_auto_optimization: bool = True,
                 default_language: Language = Language.UZBEK):
        
        self.template_manager = template_manager or TemplateManager()
        self.ab_test_manager = ABTestManager() if enable_ab_testing else None
        self.optimizer = PromptOptimizer() if enable_auto_optimization else None
        self.default_language = default_language
        
        # Conversation management
        self.conversations: Dict[str, ConversationContext] = {}
        
        # Performance tracking
        self.prompt_history: List[PromptResult] = []
        self.performance_metrics: Dict[str, Any] = {
            'total_generated': 0,
            'avg_quality_score': 0.0,
            'avg_generation_time': 0.0,
            'total_conversations': 0
        }
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
    def generate_prompt(self,
                       template_id: str,
                       context: Dict[str, Any],
                       user_profile: Dict[str, Any] = None,
                       conversation_id: str = None,
                       language: Language = None,
                       ab_test_enabled: bool = True) -> PromptResult:
        """
        Generate advanced prompt with context awareness and optimization
        
        Args:
            template_id: ID of template to use
            context: Market/user context data
            user_profile: User skill level, preferences, etc.
            conversation_id: Optional conversation ID for context
            language: Output language preference
            ab_test_enabled: Whether to include in A/B tests
        
        Returns:
            PromptResult with generated prompt and metadata
        """
        
        start_time = time.time()
        prompt_id = str(uuid.uuid4())
        
        # Set language
        output_language = language or user_profile.get('preferred_language', self.default_language) if user_profile else self.default_language
        
        try:
            # Get conversation context
            conversation_context = self._get_or_create_conversation(conversation_id)
            
            # Get recent conversation history
            conversation_history = conversation_context.get_recent_history(3)
            
            # Generate context-aware prompt
            generated_prompt = self.template_manager.generate_context_aware_prompt(
                template_id=template_id,
                context=context,
                user_profile=user_profile or {},
                conversation_history=conversation_history
            )
            
            # Apply A/B testing if enabled
            if ab_test_enabled and self.ab_test_manager:
                # Check for active tests
                test_result = self._apply_ab_testing(template_id, context, user_profile)
                if test_result:
                    generated_prompt = test_result
            
            # Validate safety and compliance
            safety_report = self.template_manager.validate_prompt_safety(generated_prompt, context)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(generated_prompt, context, safety_report)
            
            # Create result
            result = PromptResult(
                prompt_id=prompt_id,
                generated_prompt=generated_prompt,
                template_id=template_id,
                generation_time=time.time() - start_time,
                context_used=context,
                user_profile=user_profile or {}
            )
            
            # Set additional metadata
            result.quality_score = quality_score
            result.safety_validated = safety_report['is_safe']
            result.compliance_checked = len(safety_report['compliance_issues']) == 0
            result.language_used = output_language.value
            
            # Update performance metrics
            self._update_performance_metrics(result)
            
            # Store in history
            self.prompt_history.append(result)
            
            # Update conversation context
            conversation_context.update_context(context)
            if user_profile:
                conversation_context.update_user_profile(user_profile)
            
            self.logger.info(f"Generated prompt {prompt_id} using template {template_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating prompt {prompt_id}: {str(e)}")
            # Return error result
            return PromptResult(
                prompt_id=prompt_id,
                generated_prompt=f"Error: {str(e)}",
                template_id=template_id,
                generation_time=time.time() - start_time,
                context_used=context,
                user_profile=user_profile or {}
            )
    
    def _get_or_create_conversation(self, conversation_id: str = None) -> ConversationContext:
        """Get existing conversation or create new one"""
        
        if conversation_id and conversation_id in self.conversations:
            return self.conversations[conversation_id]
        
        # Create new conversation
        new_conversation = ConversationContext(conversation_id)
        self.conversations[new_conversation.conversation_id] = new_conversation
        self.performance_metrics['total_conversations'] += 1
        
        return new_conversation
    
    def _apply_ab_testing(self, template_id: str, context: Dict[str, Any], user_profile: Dict[str, Any]) -> Optional[str]:
        """Apply A/B testing variants"""
        
        if not self.ab_test_manager:
            return None
        
        # Find active tests for this template
        for test_id, test in self.ab_test_manager.active_tests.items():
            if test['template_id'] == template_id:
                # Assign variant (simplified - would need user ID in real implementation)
                user_id = hashlib.md5(str(user_profile).encode()).hexdigest()[:8]
                variant = self.ab_test_manager.assign_variant(test_id, user_id)
                
                if variant:
                    # Generate variant prompt
                    variants = self.template_manager.create_ab_test_variants(
                        template_id, context, [variant]
                    )
                    return variants.get(variant)
        
        return None
    
    def _calculate_quality_score(self, prompt: str, context: Dict[str, Any], safety_report: Dict[str, Any]) -> float:
        """Calculate prompt quality score"""
        
        score = 0.0
        
        # Safety score (30% weight)
        if safety_report['is_safe'] and not safety_report['warnings']:
            score += 0.3
        elif safety_report['is_safe']:
            score += 0.2
        
        # Completeness score (25% weight)
        if len(prompt) > 100:  # Minimum length check
            score += 0.15
        if prompt.count('\n') > 5:  # Structure check
            score += 0.1
        
        # Context relevance (25% weight)
        symbol = context.get('symbol', '')
        if symbol and symbol in prompt:
            score += 0.25
        
        # Language clarity (20% weight)
        if not re.search(r'[A-Z]{5,}', prompt):  # Check for excessive acronyms
            score += 0.1
        if prompt.count('•') > 0:  # Check for bullet points
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _update_performance_metrics(self, result: PromptResult):
        """Update overall performance metrics"""
        
        metrics = self.performance_metrics
        metrics['total_generated'] += 1
        
        # Update running averages
        total = metrics['total_generated']
        current_avg_time = metrics['avg_generation_time']
        current_avg_quality = metrics['avg_quality_score']
        
        metrics['avg_generation_time'] = (
            (current_avg_time * (total - 1) + result.generation_time) / total
        )
        
        metrics['avg_quality_score'] = (
            (current_avg_quality * (total - 1) + result.quality_score) / total
        )
    
    def translate_prompt(self, prompt: str, target_language: Language) -> str:
        """Translate prompt to target language"""
        
        # This is a simplified implementation
        # In production, you would use a proper translation service
        
        language_mappings = {
            Language.UZBEK: {
                'analysis': 'tahlil',
                'trend': 'trend',
                'market': 'bozor',
                'price': 'narx',
                'volume': 'hajm'
            },
            Language.RUSSIAN: {
                'analysis': 'анализ',
                'trend': 'тренд', 
                'market': 'рынок',
                'price': 'цена',
                'volume': 'объем'
            }
        }
        
        translations = language_mappings.get(target_language, {})
        
        translated = prompt
        for english_word, native_word in translations.items():
            translated = translated.replace(english_word, native_word)
        
        return translated
    
    def optimize_prompt_templates(self) -> Dict[str, Any]:
        """Automatically optimize prompt templates based on performance data"""
        
        if not self.optimizer:
            return {'message': 'Auto-optimization not enabled'}
        
        optimization_results = {}
        
        # Group results by template
        template_results = {}
        for result in self.prompt_history:
            if result.template_id not in template_results:
                template_results[result.template_id] = []
            template_results[result.template_id].append(result)
        
        # Optimize each template
        for template_id, results in template_results.items():
            template = self.template_manager.get_template(template_id)
            if template:
                # Prepare performance data
                performance_data = {
                    'avg_rating': sum(r.quality_score for r in results) / len(results),
                    'completion_rate': len([r for r in results if r.quality_score > 0.7]) / len(results),
                    'avg_generation_time': sum(r.generation_time for r in results) / len(results)
                }
                
                # Run optimization
                optimization = self.template_manager.optimize_prompt_performance(
                    template_id, performance_data
                )
                
                optimization_results[template_id] = optimization
        
        return optimization_results
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get comprehensive performance analytics"""
        
        # Recent performance (last 100 prompts)
        recent_prompts = self.prompt_history[-100:] if self.prompts_history else self.prompt_history
        
        if not recent_prompts:
            return self.performance_metrics
        
        # Calculate recent metrics
        recent_quality = sum(r.quality_score for r in recent_prompts) / len(recent_prompts)
        recent_time = sum(r.generation_time for r in recent_prompts) / len(recent_prompts)
        
        # Template performance
        template_performance = {}
        for result in recent_prompts:
            if result.template_id not in template_performance:
                template_performance[result.template_id] = {
                    'count': 0,
                    'avg_quality': 0.0,
                    'success_rate': 0.0
                }
            
            perf = template_performance[result.template_id]
            perf['count'] += 1
            perf['avg_quality'] = (perf['avg_quality'] * (perf['count'] - 1) + result.quality_score) / perf['count']
            perf['success_rate'] = (perf['success_rate'] * (perf['count'] - 1) + (1 if result.quality_score > 0.7 else 0)) / perf['count']
        
        return {
            **self.performance_metrics,
            'recent_performance': {
                'avg_quality_score': recent_quality,
                'avg_generation_time': recent_time,
                'recent_count': len(recent_prompts)
            },
            'template_performance': template_performance,
            'active_conversations': len(self.conversations),
            'active_ab_tests': len(self.ab_test_manager.active_tests) if self.ab_test_manager else 0
        }
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old prompt history and completed tests"""
        
        cutoff_date = datetime.now(timezone.utc).timestamp() - (days * 24 * 3600)
        
        # Clean up old prompt history
        self.prompt_history = [
            r for r in self.prompt_history 
            if r.timestamp.timestamp() > cutoff_date
        ]
        
        # Clean up completed A/B tests
        if self.ab_test_manager:
            for test_id in list(self.ab_test_manager.active_tests.keys()):
                test = self.ab_test_manager.active_tests[test_id]
                if test['end_time'] < datetime.now(timezone.utc).timestamp():
                    self.ab_test_manager.completed_tests[test_id] = test
                    del self.ab_test_manager.active_tests[test_id]
    
    def export_analytics(self, format: str = 'json') -> str:
        """Export analytics data"""
        
        analytics = self.get_performance_analytics()
        
        if format == 'json':
            return json.dumps(analytics, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize the engine
    engine = AdvancedPromptEngine(
        enable_ab_testing=True,
        enable_auto_optimization=True,
        default_language=Language.UZBEK
    )
    
    # Example context
    context = {
        'symbol': 'EURUSD',
        'current_price': '1.0850',
        'daily_change': '+0.25%',
        'volume': '1250000',
        'timeframe': '1d'
    }
    
    user_profile = {
        'skill_level': 'intermediate',
        'preferred_language': 'uzbek',
        'trading_experience': '2-3 years',
        'risk_tolerance': 'moderate'
    }
    
    # Generate prompt
    result = engine.generate_prompt(
        template_id='tech_analysis_basic',
        context=context,
        user_profile=user_profile
    )
    
    print(f"Generated Prompt ID: {result.prompt_id}")
    print(f"Quality Score: {result.quality_score:.2f}")
    print(f"Generated in: {result.generation_time:.2f}s")
    print(f"Safety Validated: {result.safety_validated}")
    print(f"\nGenerated Prompt:\n{result.generated_prompt}")
    
    # Get analytics
    analytics = engine.get_performance_analytics()
    print(f"\nAnalytics Summary:")
    print(f"Total Generated: {analytics['total_generated']}")
    print(f"Average Quality: {analytics['avg_quality_score']:.2f}")
