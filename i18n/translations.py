#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orion Starline Translation Manager
==================================

Professional translation management system with automated translation,
quality assurance, and translation memory capabilities.

Author: Orion Starline Team
Version: 1.0.0
Created: 2025-11-05
"""

import os
import json
import yaml
import csv
import pickle
import hashlib
import re
from typing import Dict, List, Optional, Union, Tuple, Any, Set
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
import logging
from pathlib import Path
import difflib
import statistics
from collections import defaultdict, Counter
import concurrent.futures
from threading import Lock


class TranslationStatus(Enum):
    """Translation status enumeration"""
    DRAFT = "draft"
    TRANSLATED = "translated"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class TranslationType(Enum):
    """Translation type enumeration"""
    LITERAL = "literal"  # Direct word-for-word translation
    CONTEXTUAL = "contextual"  # Translation based on context
    CULTURAL = "cultural"  # Cultural adaptation required
    TECHNICAL = "technical"  # Technical documentation
    MARKETING = "marketing"  # Marketing content
    UI = "ui"  # User interface elements


@dataclass
class TranslationKey:
    """Translation key with metadata"""
    key: str
    namespace: str
    description: str = ""
    context: Optional[str] = None
    type: TranslationType = TranslationType.LITERAL
    character_limit: Optional[int] = None
    requires_review: bool = False
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    deprecated: bool = False


@dataclass
class TranslationMemoryEntry:
    """Translation memory entry for reuse"""
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    context: Optional[str] = None
    confidence_score: float = 1.0
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None


@dataclass
class TranslationSuggestion:
    """AI-powered translation suggestion"""
    translation: str
    confidence: float
    source: str  # translation memory, AI model, etc.
    context: Optional[str] = None
    requires_human_review: bool = False


@dataclass
class QualityMetrics:
    """Translation quality metrics"""
    language_pair: str
    completeness: float  # 0.0 to 1.0
    accuracy: float  # 0.0 to 1.0
    consistency: float  # 0.0 to 1.0
    cultural_appropriateness: float  # 0.0 to 1.0
    readability: float  # 0.0 to 1.0
    technical_correctness: float  # 0.0 to 1.0
    overall_score: float  # 0.0 to 1.0
    last_evaluated: datetime = field(default_factory=datetime.now)


class TranslationManager:
    """
    Professional Translation Management System
    
    Features:
    - Translation memory with fuzzy matching
    - Quality assurance and scoring
    - Automated translation suggestions
    - Translation workflow management
    - Cultural adaptation tracking
    - Performance analytics
    - Concurrent processing support
    """
    
    def __init__(self, base_path: str = "i18n"):
        """
        Initialize translation manager
        
        Args:
            base_path: Base path for translation files and data
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Core data structures
        self.translation_keys: Dict[str, TranslationKey] = {}
        self.translations: Dict[str, Dict[str, Dict]] = defaultdict(lambda: defaultdict(dict))
        self.translation_memory: List[TranslationMemoryEntry] = []
        self.quality_metrics: Dict[str, QualityMetrics] = {}
        
        # File paths
        self.keys_file = self.base_path / "translation_keys.yaml"
        self.memory_file = self.base_path / "translation_memory.pkl"
        self.metrics_file = self.base_path / "quality_metrics.json"
        self.exports_dir = self.base_path / "exports"
        self.exports_dir.mkdir(exist_ok=True)
        
        # Concurrency control
        self._lock = Lock()
        self._processing_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        # Performance tracking
        self.translation_times: List[float] = []
        self.error_counts: Dict[str, int] = defaultdict(int)
        
        # Load existing data
        self._load_translation_keys()
        self._load_translations()
        self._load_translation_memory()
        self._load_quality_metrics()
    
    def _load_translation_keys(self) -> None:
        """Load translation key definitions"""
        if self.keys_file.exists():
            try:
                with open(self.keys_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                for key, key_data in data.items():
                    translation_key = TranslationKey(
                        key=key,
                        namespace=key_data.get('namespace', 'default'),
                        description=key_data.get('description', ''),
                        context=key_data.get('context'),
                        type=TranslationType(key_data.get('type', 'literal')),
                        character_limit=key_data.get('character_limit'),
                        requires_review=key_data.get('requires_review', False),
                        tags=key_data.get('tags', [])
                    )
                    self.translation_keys[key] = translation_key
                    
            except Exception as e:
                self.logger.error(f"Error loading translation keys: {e}")
    
    def _save_translation_keys(self) -> None:
        """Save translation key definitions"""
        try:
            data = {}
            for key, translation_key in self.translation_keys.items():
                data[key] = {
                    'namespace': translation_key.namespace,
                    'description': translation_key.description,
                    'context': translation_key.context,
                    'type': translation_key.type.value,
                    'character_limit': translation_key.character_limit,
                    'requires_review': translation_key.requires_review,
                    'tags': translation_key.tags
                }
            
            with open(self.keys_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                
        except Exception as e:
            self.logger.error(f"Error saving translation keys: {e}")
    
    def _load_translations(self) -> None:
        """Load translations from files"""
        translations_dir = self.base_path / "translations"
        if not translations_dir.exists():
            return
        
        for lang_file in translations_dir.glob("*.json"):
            try:
                lang_code = lang_file.stem
                with open(lang_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for key, value in data.items():
                    self.translations[lang_code][key] = {
                        'value': value,
                        'status': TranslationStatus.DRAFT.value,
                        'translator': '',
                        'reviewed_by': '',
                        'approved_by': '',
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                        'version': 1,
                        'type': TranslationType.LITERAL.value
                    }
                    
            except Exception as e:
                self.logger.error(f"Error loading translations for {lang_code}: {e}")
    
    def _save_translations(self, language_code: Optional[str] = None) -> None:
        """Save translations to files"""
        translations_dir = self.base_path / "translations"
        translations_dir.mkdir(exist_ok=True)
        
        languages_to_save = [language_code] if language_code else list(self.translations.keys())
        
        for lang_code in languages_to_save:
            if lang_code not in self.translations:
                continue
            
            translations_file = translations_dir / f"{lang_code}.json"
            data = {}
            
            for key, translation_data in self.translations[lang_code].items():
                data[key] = translation_data['value']
            
            try:
                with open(translations_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                self.logger.error(f"Error saving translations for {lang_code}: {e}")
    
    def _load_translation_memory(self) -> None:
        """Load translation memory from pickle file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'rb') as f:
                    self.translation_memory = pickle.load(f)
            except Exception as e:
                self.logger.error(f"Error loading translation memory: {e}")
                self.translation_memory = []
    
    def _save_translation_memory(self) -> None:
        """Save translation memory to pickle file"""
        try:
            with open(self.memory_file, 'wb') as f:
                pickle.dump(self.translation_memory, f)
        except Exception as e:
            self.logger.error(f"Error saving translation memory: {e}")
    
    def _load_quality_metrics(self) -> None:
        """Load quality metrics from JSON file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for pair, metrics_data in data.items():
                    self.quality_metrics[pair] = QualityMetrics(**metrics_data)
            except Exception as e:
                self.logger.error(f"Error loading quality metrics: {e}")
    
    def _save_quality_metrics(self) -> None:
        """Save quality metrics to JSON file"""
        try:
            data = {}
            for pair, metrics in self.quality_metrics.items():
                data[pair] = {
                    'language_pair': metrics.language_pair,
                    'completeness': metrics.completeness,
                    'accuracy': metrics.accuracy,
                    'consistency': metrics.consistency,
                    'cultural_appropriateness': metrics.cultural_appropriateness,
                    'readability': metrics.readability,
                    'technical_correctness': metrics.technical_correctness,
                    'overall_score': metrics.overall_score,
                    'last_evaluated': metrics.last_evaluated.isoformat()
                }
            
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving quality metrics: {e}")
    
    def add_translation_key(self, key: str, namespace: str = "default", 
                          description: str = "", context: Optional[str] = None,
                          translation_type: TranslationType = TranslationType.LITERAL,
                          character_limit: Optional[int] = None,
                          requires_review: bool = False,
                          tags: Optional[List[str]] = None) -> bool:
        """
        Add a new translation key
        
        Args:
            key: Translation key
            namespace: Namespace for organization
            description: Description of the key
            context: Context information
            translation_type: Type of translation
            character_limit: Character limit for UI elements
            requires_review: Whether human review is required
            tags: List of tags for categorization
        
        Returns:
            bool: Success status
        """
        with self._lock:
            if key in self.translation_keys:
                self.logger.warning(f"Translation key '{key}' already exists")
                return False
            
            translation_key = TranslationKey(
                key=key,
                namespace=namespace,
                description=description,
                context=context,
                type=translation_type,
                character_limit=character_limit,
                requires_review=requires_review,
                tags=tags or []
            )
            
            self.translation_keys[key] = translation_key
            self._save_translation_keys()
            
            self.logger.info(f"Added translation key: {key}")
            return True
    
    def remove_translation_key(self, key: str) -> bool:
        """
        Remove a translation key (marks as deprecated)
        
        Args:
            key: Translation key to remove
        
        Returns:
            bool: Success status
        """
        with self._lock:
            if key not in self.translation_keys:
                return False
            
            self.translation_keys[key].deprecated = True
            self.translation_keys[key].updated_at = datetime.now()
            
            # Remove translations in all languages
            for lang_code in self.translations:
                if key in self.translations[lang_code]:
                    del self.translations[lang_code][key]
            
            self._save_translation_keys()
            self._save_translations()
            
            self.logger.info(f"Removed translation key: {key}")
            return True
    
    def update_translation(self, language_code: str, key: str, value: str,
                          status: TranslationStatus = TranslationStatus.DRAFT,
                          translator: str = "", 
                          translation_type: TranslationType = TranslationType.LITERAL) -> bool:
        """
        Update a translation
        
        Args:
            language_code: Language code
            key: Translation key
            value: Translation value
            status: Translation status
            translator: Translator name
            translation_type: Type of translation
        
        Returns:
            bool: Success status
        """
        with self._lock:
            if key not in self.translation_keys:
                self.logger.error(f"Translation key '{key}' does not exist")
                return False
            
            translation_key = self.translation_keys[key]
            if translation_key.character_limit and len(value) > translation_key.character_limit:
                self.logger.warning(f"Translation for '{key}' exceeds character limit")
            
            self.translations[language_code][key] = {
                'value': value,
                'status': status.value,
                'translator': translator,
                'reviewed_by': '',
                'approved_by': '',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'version': 1,
                'type': translation_type.value
            }
            
            # Add to translation memory
            if status in [TranslationStatus.APPROVED, TranslationStatus.PUBLISHED]:
                self._add_to_translation_memory(key, value, language_code, translation_type)
            
            self._save_translations(language_code)
            
            self.logger.info(f"Updated translation: {language_code}/{key}")
            return True
    
    def get_translation(self, language_code: str, key: str) -> Optional[str]:
        """
        Get a translation
        
        Args:
            language_code: Language code
            key: Translation key
        
        Returns:
            Translation value or None
        """
        if key in self.translations.get(language_code, {}):
            return self.translations[language_code][key]['value']
        return None
    
    def get_translation_status(self, language_code: str, key: str) -> Optional[TranslationStatus]:
        """
        Get translation status
        
        Args:
            language_code: Language code
            key: Translation key
        
        Returns:
            Translation status or None
        """
        if key in self.translations.get(language_code, {}):
            return TranslationStatus(self.translations[language_code][key]['status'])
        return None
    
    def get_all_translations(self, language_code: str) -> Dict[str, str]:
        """
        Get all translations for a language
        
        Args:
            language_code: Language code
        
        Returns:
            Dictionary of translations
        """
        return {
            key: data['value'] 
            for key, data in self.translations.get(language_code, {}).items()
        }
    
    def _add_to_translation_memory(self, key: str, translation: str, 
                                 language_code: str, translation_type: TranslationType) -> None:
        """
        Add translation to memory for reuse
        
        Args:
            key: Translation key
            translation: Translation value
            language_code: Language code
            translation_type: Type of translation
        """
        # For now, we use the key as source text
        # In a real implementation, you might want to store the actual source text
        source_text = key
        
        memory_entry = TranslationMemoryEntry(
            source_text=source_text,
            target_text=translation,
            source_lang='en',  # Assuming English as source
            target_lang=language_code,
            context=self.translation_keys.get(key, {}).context,
            confidence_score=1.0
        )
        
        self.translation_memory.append(memory_entry)
        self._save_translation_memory()
    
    def find_similar_translations(self, text: str, source_lang: str, 
                                target_lang: str, threshold: float = 0.8) -> List[TranslationSuggestion]:
        """
        Find similar translations using fuzzy matching
        
        Args:
            text: Text to find similar translations for
            source_lang: Source language code
            target_lang: Target language code
            threshold: Similarity threshold (0.0 to 1.0)
        
        Returns:
            List of translation suggestions
        """
        suggestions = []
        
        for entry in self.translation_memory:
            if entry.source_lang == source_lang and entry.target_lang == target_lang:
                similarity = difflib.SequenceMatcher(None, text.lower(), 
                                                    entry.source_text.lower()).ratio()
                if similarity >= threshold:
                    suggestion = TranslationSuggestion(
                        translation=entry.target_text,
                        confidence=similarity,
                        source="translation_memory",
                        context=entry.context
                    )
                    suggestions.append(suggestion)
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:10]  # Return top 10 suggestions
    
    def get_translation_suggestions(self, key: str, language_code: str, 
                                  count: int = 5) -> List[TranslationSuggestion]:
        """
        Get translation suggestions for a key
        
        Args:
            key: Translation key
            language_code: Target language
            count: Number of suggestions to return
        
        Returns:
            List of translation suggestions
        """
        suggestions = []
        
        # Get from translation memory
        if key in self.translation_keys:
            context = self.translation_keys[key].context
            memory_suggestions = self.find_similar_translations(
                key, 'en', language_code, threshold=0.6
            )
            suggestions.extend(memory_suggestions[:count])
        
        # Add AI-powered suggestions (placeholder - can be enhanced with actual AI)
        # For now, we'll use basic pattern matching
        if key in self.translation_keys:
            template_suggestions = self._generate_template_suggestions(
                key, language_code
            )
            suggestions.extend(template_suggestions[:count - len(suggestions)])
        
        return suggestions[:count]
    
    def _generate_template_suggestions(self, key: str, language_code: str) -> List[TranslationSuggestion]:
        """
        Generate template-based suggestions
        
        Args:
            key: Translation key
            language_code: Target language
        
        Returns:
            List of template suggestions
        """
        suggestions = []
        
        # Simple templates for common patterns
        templates = {
            'button': {
                'uz': ['Tugma', 'Bosish', 'Amal qilish'],
                'en': ['Button', 'Click', 'Action'],
                'ru': ['Кнопка', 'Нажмите', 'Действие']
            },
            'menu': {
                'uz': ['Menyu', 'Ro\'yxat', 'Tanlash'],
                'en': ['Menu', 'List', 'Select'],
                'ru': ['Меню', 'Список', 'Выбрать']
            },
            'form': {
                'uz': ['Forma', 'Kiritish', 'Yuborish'],
                'en': ['Form', 'Input', 'Submit'],
                'ru': ['Форма', 'Ввод', 'Отправить']
            }
        }
        
        # Find matching template
        for category, lang_templates in templates.items():
            if category in key.lower() and language_code in lang_templates:
                for template in lang_templates[language_code]:
                    suggestions.append(TranslationSuggestion(
                        translation=template,
                        confidence=0.5,
                        source="template",
                        requires_human_review=True
                    ))
        
        return suggestions
    
    def calculate_translation_quality(self, language_pair: str) -> QualityMetrics:
        """
        Calculate translation quality metrics
        
        Args:
            language_pair: Language pair (e.g., 'en-uz')
        
        Returns:
            QualityMetrics object
        """
        source_lang, target_lang = language_pair.split('-')
        
        if target_lang not in self.translations:
            return QualityMetrics(
                language_pair=language_pair,
                completeness=0.0,
                accuracy=0.0,
                consistency=0.0,
                cultural_appropriateness=0.0,
                readability=0.0,
                technical_correctness=0.0,
                overall_score=0.0
            )
        
        # Calculate completeness
        total_keys = len(self.translation_keys)
        translated_keys = len(self.translations[target_lang])
        completeness = translated_keys / total_keys if total_keys > 0 else 0.0
        
        # Calculate accuracy (based on translation memory matches)
        accuracy_scores = []
        for key, translation_data in self.translations[target_lang].items():
            # Check if similar translation exists in memory
            suggestions = self.find_similar_translations(key, source_lang, target_lang)
            if suggestions:
                # Use best match confidence as accuracy indicator
                accuracy_scores.append(suggestions[0].confidence)
        
        accuracy = statistics.mean(accuracy_scores) if accuracy_scores else 0.0
        
        # Calculate consistency (how often similar patterns are translated consistently)
        consistency_scores = []
        # This is a simplified calculation - can be enhanced
        consistency = 0.8 if completeness > 0.5 else 0.3
        
        # Cultural appropriateness (based on translation type and status)
        cultural_scores = []
        for key, translation_data in self.translations[target_lang].items():
            translation_key = self.translation_keys.get(key)
            if translation_key:
                if translation_key.type == TranslationType.CULTURAL:
                    cultural_scores.append(0.9 if translation_data['status'] == TranslationStatus.APPROVED.value else 0.5)
                else:
                    cultural_scores.append(0.8)
        
        cultural_appropriateness = statistics.mean(cultural_scores) if cultural_scores else 0.7
        
        # Readability (based on character limits and translation length)
        readability_scores = []
        for key, translation_data in self.translations[target_lang].items():
            translation_key = self.translation_keys.get(key)
            value = translation_data['value']
            
            if translation_key and translation_key.character_limit:
                if len(value) <= translation_key.character_limit:
                    readability_scores.append(0.9)
                else:
                    readability_scores.append(0.3)
            else:
                # Assume good readability for translations within reasonable length
                if 1 <= len(value) <= 100:
                    readability_scores.append(0.9)
                elif len(value) <= 200:
                    readability_scores.append(0.7)
                else:
                    readability_scores.append(0.5)
        
        readability = statistics.mean(readability_scores) if readability_scores else 0.7
        
        # Technical correctness (based on status and review)
        technical_scores = []
        for key, translation_data in self.translations[target_lang].items():
            status = TranslationStatus(translation_data['status'])
            if status in [TranslationStatus.APPROVED, TranslationStatus.PUBLISHED]:
                technical_scores.append(0.9)
            elif status == TranslationStatus.REVIEWED:
                technical_scores.append(0.7)
            else:
                technical_scores.append(0.5)
        
        technical_correctness = statistics.mean(technical_scores) if technical_scores else 0.5
        
        # Overall score (weighted average)
        overall_score = (
            completeness * 0.25 +
            accuracy * 0.2 +
            consistency * 0.15 +
            cultural_appropriateness * 0.15 +
            readability * 0.15 +
            technical_correctness * 0.1
        )
        
        quality_metrics = QualityMetrics(
            language_pair=language_pair,
            completeness=completeness,
            accuracy=accuracy,
            consistency=consistency,
            cultural_appropriateness=cultural_appropriateness,
            readability=readability,
            technical_correctness=technical_correctness,
            overall_score=overall_score
        )
        
        self.quality_metrics[language_pair] = quality_metrics
        self._save_quality_metrics()
        
        return quality_metrics
    
    def get_quality_report(self, language_codes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate quality report
        
        Args:
            language_codes: List of language codes to include
        
        Returns:
            Quality report dictionary
        """
        if language_codes is None:
            language_codes = list(self.translations.keys())
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'language_pairs': {},
            'recommendations': []
        }
        
        total_metrics = []
        
        for source_lang in ['en']:  # Assuming English as source
            for target_lang in language_codes:
                language_pair = f"{source_lang}-{target_lang}"
                metrics = self.calculate_translation_quality(language_pair)
                total_metrics.append(metrics.overall_score)
                
                report['language_pairs'][language_pair] = {
                    'completeness': metrics.completeness,
                    'accuracy': metrics.accuracy,
                    'consistency': metrics.consistency,
                    'cultural_appropriateness': metrics.cultural_appropriateness,
                    'readability': metrics.readability,
                    'technical_correctness': metrics.technical_correctness,
                    'overall_score': metrics.overall_score
                }
        
        # Summary statistics
        if total_metrics:
            report['summary'] = {
                'average_quality': statistics.mean(total_metrics),
                'best_language_pair': max(self.quality_metrics.keys(), 
                                        key=lambda k: self.quality_metrics[k].overall_score),
                'worst_language_pair': min(self.quality_metrics.keys(), 
                                         key=lambda k: self.quality_metrics[k].overall_score),
                'languages_needing_attention': []
            }
            
            # Identify languages needing attention
            for pair, metrics in self.quality_metrics.items():
                if metrics.overall_score < 0.6:
                    report['summary']['languages_needing_attention'].append(pair)
        
        # Generate recommendations
        recommendations = []
        
        for pair, metrics in self.quality_metrics.items():
            if metrics.completeness < 0.5:
                recommendations.append(f"Complete translations for {pair} (current: {metrics.completeness:.2%})")
            
            if metrics.accuracy < 0.7:
                recommendations.append(f"Improve accuracy for {pair} (current: {metrics.accuracy:.2%})")
            
            if metrics.cultural_appropriateness < 0.6:
                recommendations.append(f"Review cultural appropriateness for {pair} (current: {metrics.cultural_appropriateness:.2%})")
        
        report['recommendations'] = recommendations
        
        return report
    
    def export_translations(self, language_codes: List[str], format: str = "json", 
                          include_metadata: bool = False) -> str:
        """
        Export translations in various formats
        
        Args:
            language_codes: List of language codes to export
            format: Export format ('json', 'csv', 'po', 'xlsx')
            include_metadata: Whether to include metadata
        
        Returns:
            Exported content as string
        """
        if format.lower() == "json":
            export_data = {}
            for lang_code in language_codes:
                if lang_code in self.translations:
                    export_data[lang_code] = {}
                    for key, translation_data in self.translations[lang_code].items():
                        if include_metadata:
                            export_data[lang_code][key] = translation_data
                        else:
                            export_data[lang_code][key] = translation_data['value']
            
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        
        elif format.lower() == "csv":
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            header = ['key'] + language_codes
            writer.writerow(header)
            
            # Get all keys
            all_keys = set()
            for lang_code in language_codes:
                all_keys.update(self.translations[lang_code].keys())
            
            # Write data rows
            for key in sorted(all_keys):
                row = [key]
                for lang_code in language_codes:
                    if lang_code in self.translations and key in self.translations[lang_code]:
                        row.append(self.translations[lang_code][key]['value'])
                    else:
                        row.append('')
                writer.writerow(row)
            
            return output.getvalue()
        
        elif format.lower() == "po":
            result = []
            result.append('msgid ""')
            result.append('msgstr ""')
            result.append('"Content-Type: text/plain; charset=UTF-8\\n"')
            result.append("")
            
            for lang_code in language_codes:
                if lang_code in self.translations:
                    result.append(f'# Language: {lang_code}')
                    result.append("")
                    
                    for key, translation_data in self.translations[lang_code].items():
                        result.append(f'msgid "{key}"')
                        result.append(f'msgstr "{translation_data["value"]}"')
                        result.append("")
            
            return "\n".join(result)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_translations(self, content: str, format: str = "json", 
                          language_code: Optional[str] = None) -> bool:
        """
        Import translations from various formats
        
        Args:
            content: Translation content
            format: Import format ('json', 'csv', 'po')
            language_code: Language code (required for some formats)
        
        Returns:
            bool: Success status
        """
        try:
            if format.lower() == "json":
                data = json.loads(content)
                
                for lang_code, translations in data.items():
                    for key, value in translations.items():
                        if isinstance(value, dict):
                            # Handle metadata
                            self.update_translation(
                                lang_code, key, value['value'],
                                status=TranslationStatus(value.get('status', 'draft'))
                            )
                        else:
                            # Handle simple values
                            self.update_translation(lang_code, key, value)
            
            elif format.lower() == "csv":
                import io
                input_file = io.StringIO(content)
                reader = csv.reader(input_file)
                
                header = next(reader)
                language_codes = header[1:]  # Skip 'key' column
                
                for row in reader:
                    key = row[0]
                    for i, lang_code in enumerate(language_codes):
                        if i + 1 < len(row) and row[i + 1]:
                            self.update_translation(lang_code, key, row[i + 1])
            
            elif format.lower() == "po":
                # Simple PO parser
                lines = content.split('\n')
                current_msgid = None
                current_msgstr = None
                current_lang = None
                
                for line in lines:
                    line = line.strip()
                    
                    if line.startswith('"Language:'):
                        # Extract language code
                        match = re.search(r'"Language:\s*([^"]+)"', line)
                        if match:
                            current_lang = match.group(1)
                    
                    elif line.startswith('msgid '):
                        current_msgid = line[7:-1]  # Remove quotes
                    
                    elif line.startswith('msgstr '):
                        current_msgstr = line[8:-1]  # Remove quotes
                    
                    elif line == "" and current_msgid and current_msgstr:
                        if current_lang:
                            self.update_translation(current_lang, current_msgid, current_msgstr)
                        current_msgid = None
                        current_msgstr = None
            
            else:
                raise ValueError(f"Unsupported import format: {format}")
            
            self.logger.info(f"Successfully imported translations in {format} format")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing translations: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get translation statistics
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_keys': len(self.translation_keys),
            'active_keys': len([k for k in self.translation_keys.values() if not k.deprecated]),
            'deprecated_keys': len([k for k in self.translation_keys.values() if k.deprecated]),
            'languages': list(self.translations.keys()),
            'total_translations': sum(len(lang_translations) for lang_translations in self.translations.values()),
            'translation_memory_entries': len(self.translation_memory),
            'status_distribution': defaultdict(int),
            'type_distribution': defaultdict(int)
        }
        
        # Status distribution
        for lang_translations in self.translations.values():
            for translation_data in lang_translations.values():
                stats['status_distribution'][translation_data['status']] += 1
        
        # Type distribution
        for translation_key in self.translation_keys.values():
            stats['type_distribution'][translation_key.type.value] += 1
        
        # Convert defaultdicts to regular dicts for JSON serialization
        stats['status_distribution'] = dict(stats['status_distribution'])
        stats['type_distribution'] = dict(stats['type_distribution'])
        
        return stats
    
    def cleanup_old_data(self, days_old: int = 90) -> None:
        """
        Clean up old data
        
        Args:
            days_old: Number of days to consider data old
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Clean up translation memory
        self.translation_memory = [
            entry for entry in self.translation_memory 
            if entry.last_used and entry.last_used > cutoff_date
        ]
        
        self._save_translation_memory()
        
        # Clean up error logs
        self.error_counts.clear()
        
        self.logger.info("Cleanup completed")


# Example usage and demonstration
if __name__ == "__main__":
    # Initialize translation manager
    tm = TranslationManager()
    
    # Add translation keys
    tm.add_translation_key(
        key="welcome_message",
        namespace="common",
        description="Welcome message for users",
        context="UI welcome screen",
        translation_type=TranslationType.UI,
        character_limit=50
    )
    
    tm.add_translation_key(
        key="login_button",
        namespace="auth",
        description="Login button text",
        context="Authentication form",
        translation_type=TranslationType.UI,
        character_limit=20
    )
    
    # Update translations
    tm.update_translation("uz", "welcome_message", "Xush kelibsiz!")
    tm.update_translation("en", "welcome_message", "Welcome!")
    tm.update_translation("uz", "login_button", "Kirish")
    tm.update_translation("en", "login_button", "Login")
    
    # Get translations
    print("Uzbek welcome:", tm.get_translation("uz", "welcome_message"))
    print("English welcome:", tm.get_translation("en", "welcome_message"))
    
    # Get suggestions
    suggestions = tm.get_translation_suggestions("welcome_message", "ru", count=3)
    print("Translation suggestions for Russian:")
    for suggestion in suggestions:
        print(f"  - {suggestion.translation} (confidence: {suggestion.confidence:.2f})")
    
    # Quality metrics
    quality_metrics = tm.calculate_translation_quality("en-uz")
    print(f"English-Uzbek quality score: {quality_metrics.overall_score:.2f}")
    
    # Statistics
    stats = tm.get_statistics()
    print(f"Total keys: {stats['total_keys']}")
    print(f"Languages: {stats['languages']}")
    print(f"Total translations: {stats['total_translations']}")
    
    # Export translations
    export_data = tm.export_translations(["en", "uz"], format="json", include_metadata=True)
    print("Export sample:")
    print(export_data[:200] + "...")  # Print first 200 characters