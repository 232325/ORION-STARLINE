"""
Advanced NLP Tizimi - Orion Starline
Matn qayta ishlash, sentiment analysis, named entity recognition, language models
"""

import asyncio
import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize, TweetTokenizer
from nltk.corpus import stopwords, twitter_samples
from nltk.tag import pos_tag, ne_chunk
from nltk.chunk import ne_chunk_sents
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.parse.stanford import StanfordDependencyParser
import spacy
from spacy import displacy
from spacy.util import minibatch, compounding
import textblob
from textblob import TextBlob
import transformers
from transformers import (
    pipeline, AutoTokenizer, AutoModelForSequenceClassification,
    AutoModelForTokenClassification, AutoModelForQuestionAnswering,
    TrainingArguments, Trainer
)
import torch
from torch.utils.data import Dataset, DataLoader
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.cluster import KMeans
import gensim
from gensim import corpora, models
from gensim.utils import simple_preprocess
import yake
import RAKE
import warnings
warnings.filterwarnings('ignore')

# NLTK data yuklash
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('maxent_ne_chunker', quiet=True)
    nltk.download('words', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
except:
    pass

# Spacy model yuklash
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None
    logging.warning("Spacy model topilmadi. Install with: python -m spacy download en_core_web_sm")

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPTaskType(Enum):
    """NLP vazifa turlari"""
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NER = "named_entity_recognition"
    TEXT_CLASSIFICATION = "text_classification"
    QUESTION_ANSWERING = "question_answering"
    TEXT_SUMMARIZATION = "text_summarization"
    TEXT_GENERATION = "text_generation"
    LANGUAGE_DETECTION = "language_detection"
    KEYWORD_EXTRACTION = "keyword_extraction"
    TOPIC_MODELING = "topic_modeling"
    SIMILARITY_ANALYSIS = "similarity_analysis"

class SentimentType(Enum):
    """Sentiment turlari"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

@dataclass
class TextDocument:
    """Matn hujjati"""
    id: str
    text: str
    title: Optional[str] = None
    source: Optional[str] = None
    timestamp: datetime = None
    language: str = "en"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SentimentResult:
    """Sentiment tahlili natijasi"""
    text_id: str
    sentiment: SentimentType
    confidence: float
    scores: Dict[str, float]  # positive, negative, neutral scores
    sentiment_words: List[str]
    timestamp: datetime

@dataclass
class EntityResult:
    """Named Entity Recognition natijasi"""
    text_id: str
    entities: List[Dict[str, Any]]  # [{text, label_, start, end}]
    timestamp: datetime

@dataclass
class TopicResult:
    """Topic modeling natijasi"""
    text_id: str
    topics: List[Dict[str, Any]]  # [{topic_id, words, weight}]
    timestamp: datetime

class Preprocessor:
    """Matn preprocessing"""
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.tweet_tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
        
        # Custom stop words
        custom_stop_words = {
            'crypto', 'cryptocurrency', 'bitcoin', 'btc', 'ethereum', 'eth',
            'trading', 'trade', 'price', 'market', 'bull', 'bear',
            'pump', 'dump', 'moon', 'lambos'
        }
        self.stop_words.update(custom_stop_words)
    
    def clean_text(self, text: str) -> str:
        """Matnni tozalash"""
        if not text:
            return ""
        
        # URL larni o'chirish
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'www\S+', '', text)
        
        # Mention larni o'chirish
        text = re.sub(r'@\w+', '', text)
        
        # Hashtag larni tozalash (# # olish)
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Emoji larni o'chirish
        emoji_pattern = re.compile("["
                                  u"\U0001F600-\U0001F64F"  # emoticons
                                  u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                  u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                  u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                  u"\U00002702-\U000027B0"
                                  u"\U000024C2-\U0001F251"
                                  "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
        
        # Special characters larni o'chirish
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Ko'p bo'shliqlarni bitta qilish
        text = re.sub(r'\s+', ' ', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def tokenize(self, text: str, method: str = "word") -> List[str]:
        """Tokenization"""
        if not text:
            return []
        
        if method == "word":
            return word_tokenize(text)
        elif method == "sentence":
            return sent_tokenize(text)
        elif method == "tweet":
            return self.tweet_tokenizer.tokenize(text)
        else:
            return word_tokenize(text)
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Stop words ni o'chirish"""
        return [token for token in tokens if token.lower() not in self.stop_words and len(token) > 2]
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """Lemmatization"""
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """Stemming"""
        return [self.stemmer.stem(token) for token in tokens]
    
    def preprocess_pipeline(self, text: str, remove_stopwords: bool = True, 
                          lemmatize: bool = True, lowercase: bool = True) -> List[str]:
        """To'liq preprocessing pipeline"""
        if not text:
            return []
        
        # Tozalash
        cleaned_text = self.clean_text(text)
        
        # Tokenization
        tokens = self.tokenize(cleaned_text)
        
        # Lowercase
        if lowercase:
            tokens = [token.lower() for token in tokens]
        
        # Stop words o'chirish
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)
        
        # Lemmatization
        if lemmatize:
            tokens = self.lemmatize_tokens(tokens)
        
        return tokens

class SentimentAnalyzer:
    """Sentiment analyzer"""
    
    def __init__(self):
        # NLTK VADER
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Transformers models
        try:
            self.transformers_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
        except:
            self.transformers_analyzer = None
        
        # Custom models
        self.custom_models = {}
        
    async def analyze_sentiment(self, text: str, method: str = "vader") -> SentimentResult:
        """Sentiment tahlili"""
        
        if not text:
            return SentimentResult(
                text_id="",
                sentiment=SentimentType.NEUTRAL,
                confidence=0.0,
                scores={"positive": 0.33, "negative": 0.33, "neutral": 0.34},
                sentiment_words=[],
                timestamp=datetime.now()
            )
        
        if method == "vader":
            return await self._analyze_with_vader(text)
        elif method == "transformers":
            return await self._analyze_with_transformers(text)
        elif method == "textblob":
            return await self._analyze_with_textblob(text)
        else:
            return await self._analyze_with_vader(text)
    
    async def _analyze_with_vader(self, text: str) -> SentimentResult:
        """VADER bilan sentiment tahlili"""
        
        scores = self.vader_analyzer.polarity_scores(text)
        
        # Sentiment aniqlash
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = SentimentType.POSITIVE
        elif compound <= -0.05:
            sentiment = SentimentType.NEGATIVE
        else:
            sentiment = SentimentType.NEUTRAL
        
        # Confidence hisoblash
        confidence = abs(compound)
        
        # Sentiment words extraction
        sentiment_words = self._extract_sentiment_words(text)
        
        return SentimentResult(
            text_id=f"vader_{datetime.now().timestamp()}",
            sentiment=sentiment,
            confidence=confidence,
            scores=scores,
            sentiment_words=sentiment_words,
            timestamp=datetime.now()
        )
    
    async def _analyze_with_transformers(self, text: str) -> SentimentResult:
        """Transformers model bilan sentiment tahlili"""
        
        if not self.transformers_analyzer:
            return await self._analyze_with_vader(text)
        
        try:
            results = self.transformers_analyzer(text)
            
            # Eng yuqori confidence li natijani olish
            best_result = max(results[0], key=lambda x: x['score'])
            
            label = best_result['label']
            score = best_result['score']
            
            # Label mapping
            if label == 'LABEL_0':  # Negative
                sentiment = SentimentType.NEGATIVE
            elif label == 'LABEL_1':  # Neutral
                sentiment = SentimentType.NEUTRAL
            else:  # LABEL_2 - Positive
                sentiment = SentimentType.POSITIVE
            
            scores = {
                'negative': results[0][0]['score'],
                'neutral': results[0][1]['score'],
                'positive': results[0][2]['score']
            }
            
            sentiment_words = self._extract_sentiment_words(text)
            
            return SentimentResult(
                text_id=f"transformers_{datetime.now().timestamp()}",
                sentiment=sentiment,
                confidence=score,
                scores=scores,
                sentiment_words=sentiment_words,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Transformers sentiment analysis xatosi: {str(e)}")
            return await self._analyze_with_vader(text)
    
    async def _analyze_with_textblob(self, text: str) -> SentimentResult:
        """TextBlob bilan sentiment tahlili"""
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Sentiment aniqlash
            if polarity > 0.1:
                sentiment = SentimentType.POSITIVE
            elif polarity < -0.1:
                sentiment = SentimentType.NEGATIVE
            else:
                sentiment = SentimentType.NEUTRAL
            
            confidence = abs(polarity)
            
            scores = {
                'positive': max(0, polarity),
                'negative': max(0, -polarity),
                'neutral': 1 - abs(polarity)
            }
            
            sentiment_words = self._extract_sentiment_words(text)
            
            return SentimentResult(
                text_id=f"textblob_{datetime.now().timestamp()}",
                sentiment=sentiment,
                confidence=confidence,
                scores=scores,
                sentiment_words=sentiment_words,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"TextBlob sentiment analysis xatosi: {str(e)}")
            return await self._analyze_with_vader(text)
    
    def _extract_sentiment_words(self, text: str) -> List[str]:
        """Sentiment words ni ajratib olish"""
        
        # Positive words
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic',
            'bullish', 'pump', 'moon', 'up', 'gain', 'profit', 'buy',
            'strong', 'positive', 'growth', 'increase', 'rise'
        }
        
        # Negative words
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'disgusting',
            'bearish', 'dump', 'down', 'loss', 'sell', 'weak',
            'negative', 'decrease', 'fall', 'crash'
        }
        
        tokens = text.lower().split()
        sentiment_words = []
        
        for token in tokens:
            if token in positive_words or token in negative_words:
                sentiment_words.append(token)
        
        return sentiment_words
    
    def train_custom_model(self, texts: List[str], labels: List[str], model_type: str = "logistic_regression"):
        """Custom sentiment model o'qitish"""
        
        try:
            # Text vectorization
            vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
            X = vectorizer.fit_transform(texts)
            
            # Model yaratish
            if model_type == "naive_bayes":
                model = MultinomialNB()
            elif model_type == "svm":
                model = SVC(probability=True)
            elif model_type == "random_forest":
                model = RandomForestClassifier(n_estimators=100)
            else:  # logistic_regression
                model = LogisticRegression(max_iter=1000)
            
            # Training
            model.fit(X, labels)
            
            # Model ni saqlash
            self.custom_models[model_type] = {
                'model': model,
                'vectorizer': vectorizer
            }
            
            logger.info(f"Custom sentiment model muvaffaqiyatli o'qitildi: {model_type}")
            
        except Exception as e:
            logger.error(f"Custom model o'qitishda xato: {str(e)}")
    
    async def predict_with_custom_model(self, text: str, model_type: str = "logistic_regression") -> SentimentResult:
        """Custom model bilan prediction"""
        
        if model_type not in self.custom_models:
            raise ValueError(f"Model topilmadi: {model_type}")
        
        try:
            model_info = self.custom_models[model_type]
            model = model_info['model']
            vectorizer = model_info['vectorizer']
            
            # Vectorization
            X = vectorizer.transform([text])
            
            # Prediction
            prediction = model.predict(X)[0]
            probability = model.predict_proba(X)[0]
            
            # Sentiment mapping
            sentiment_map = {0: SentimentType.NEGATIVE, 1: SentimentType.NEUTRAL, 2: SentimentType.POSITIVE}
            sentiment = sentiment_map.get(prediction, SentimentType.NEUTRAL)
            
            scores = {
                'negative': probability[0],
                'neutral': probability[1],
                'positive': probability[2]
            }
            
            confidence = max(probability)
            
            sentiment_words = self._extract_sentiment_words(text)
            
            return SentimentResult(
                text_id=f"custom_{datetime.now().timestamp()}",
                sentiment=sentiment,
                confidence=confidence,
                scores=scores,
                sentiment_words=sentiment_words,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Custom model prediction xatosi: {str(e)}")
            raise

class NamedEntityRecognizer:
    """Named Entity Recognition"""
    
    def __init__(self):
        self.nlp_model = nlp
        
    async def extract_entities(self, text: str, method: str = "spacy") -> EntityResult:
        """Entities extraction"""
        
        if not text:
            return EntityResult(
                text_id="",
                entities=[],
                timestamp=datetime.now()
            )
        
        if method == "spacy":
            return await self._extract_with_spacy(text)
        elif method == "nltk":
            return await self._extract_with_nltk(text)
        else:
            return await self._extract_with_spacy(text)
    
    async def _extract_with_spacy(self, text: str) -> EntityResult:
        """Spacy bilan NER"""
        
        if not self.nlp_model:
            return await self._extract_with_nltk(text)
        
        try:
            doc = self.nlp_model(text)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'description': spacy.explain(ent.label_)
                })
            
            return EntityResult(
                text_id=f"spacy_{datetime.now().timestamp()}",
                entities=entities,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Spacy NER xatosi: {str(e)}")
            return await self._extract_with_nltk(text)
    
    async def _extract_with_nltk(self, text: str) -> EntityResult:
        """NLTK bilan NER"""
        
        try:
            # Tokenization va POS tagging
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            
            # NER
            chunks = ne_chunk(pos_tags)
            entities = []
            
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    entity_text = ' '.join([token for token, pos in chunk.leaves()])
                    entities.append({
                        'text': entity_text,
                        'label': chunk.label(),
                        'start': None,  # NLTK start/end ni bermaydi
                        'end': None,
                        'description': chunk.label()
                    })
            
            return EntityResult(
                text_id=f"nltk_{datetime.now().timestamp()}",
                entities=entities,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"NLTK NER xatosi: {str(e)}")
            return EntityResult(
                text_id=f"nltk_error_{datetime.now().timestamp()}",
                entities=[],
                timestamp=datetime.now()
            )

class KeywordExtractor:
    """Keyword extraction"""
    
    def __init__(self):
        self.rake = RAKE.Rake("SmartStoplist.txt")
        
    async def extract_keywords(self, text: str, method: str = "yake", max_keywords: int = 10) -> List[Dict[str, Any]]:
        """Keywords extraction"""
        
        if not text:
            return []
        
        if method == "yake":
            return await self._extract_with_yake(text, max_keywords)
        elif method == "rake":
            return await self._extract_with_rake(text, max_keywords)
        elif method == "tfidf":
            return await self._extract_with_tfidf(text, max_keywords)
        else:
            return await self._extract_with_yake(text, max_keywords)
    
    async def _extract_with_yake(self, text: str, max_keywords: int) -> List[Dict[str, Any]]:
        """YAKE algorithm"""
        
        try:
            kw_extractor = yake.KeywordExtractor(
                lan="en",
                n=3,
                dedupLim=0.7,
                top=max_keywords,
                features=None
            )
            
            keywords = kw_extractor.extract_keywords(text)
            
            return [
                {
                    'keyword': keyword,
                    'score': score,
                    'method': 'yake'
                }
                for keyword, score in keywords
            ]
            
        except Exception as e:
            logger.error(f"YAKE keyword extraction xatosi: {str(e)}")
            return []
    
    async def _extract_with_rake(self, text: str, max_keywords: int) -> List[Dict[str, Any]]:
        """RAKE algorithm"""
        
        try:
            keywords = self.rake.run(text, max_keywords)
            
            return [
                {
                    'keyword': keyword,
                    'score': score,
                    'method': 'rake'
                }
                for keyword, score in keywords
            ]
            
        except Exception as e:
            logger.error(f"RAKE keyword extraction xatosi: {str(e)}")
            return []
    
    async def _extract_with_tfidf(self, text: str, max_keywords: int) -> List[Dict[str, Any]]:
        """TF-IDF method"""
        
        try:
            # Single document uchun TF-IDF
            docs = [text]
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english', ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(docs)
            feature_names = vectorizer.get_feature_names_out()
            
            # TF-IDF scores
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Top keywords
            keyword_scores = list(zip(feature_names, tfidf_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [
                {
                    'keyword': keyword,
                    'score': score,
                    'method': 'tfidf'
                }
                for keyword, score in keyword_scores[:max_keywords]
            ]
            
        except Exception as e:
            logger.error(f"TF-IDF keyword extraction xatosi: {str(e)}")
            return []

class TopicModeler:
    """Topic modeling"""
    
    def __init__(self):
        self.lda_model = None
        self.dictionary = None
        self.corpus = None
    
    async def perform_topic_modeling(self, documents: List[str], num_topics: int = 5) -> List[TopicResult]:
        """Topic modeling bajarish"""
        
        try:
            # Text preprocessing
            processed_docs = [simple_preprocess(doc) for doc in documents]
            
            # Dictionary yaratish
            self.dictionary = corpora.Dictionary(processed_docs)
            
            # Corpus yaratish
            self.corpus = [self.dictionary.doc2bow(doc) for doc in processed_docs]
            
            # LDA model
            self.lda_model = models.LdaModel(
                corpus=self.corpus,
                id2word=self.dictionary,
                num_topics=num_topics,
                random_state=42,
                passes=10,
                alpha='auto',
                per_word_topics=True
            )
            
            # Document topics
            results = []
            for i, doc in enumerate(documents):
                doc_topics = self.lda_model.get_document_topics(self.corpus[i])
                
                topics = []
                for topic_id, prob in doc_topics:
                    topic_words = self.lda_model.show_topic(topic_id, topn=10)
                    topics.append({
                        'topic_id': topic_id,
                        'weight': prob,
                        'words': [word for word, weight in topic_words],
                        'top_words': dict(topic_words)
                    })
                
                results.append(TopicResult(
                    text_id=f"topic_{i}_{datetime.now().timestamp()}",
                    topics=topics,
                    timestamp=datetime.now()
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Topic modeling xatosi: {str(e)}")
            return []

class TextSimilarityAnalyzer:
    """Text similarity analysis"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
    
    async def calculate_similarity(self, text1: str, text2: str, method: str = "cosine") -> float:
        """Text o'rtasidagi o'xshashlik"""
        
        if not text1 or not text2:
            return 0.0
        
        try:
            if method == "cosine":
                return await self._cosine_similarity(text1, text2)
            elif method == "jaccard":
                return await self._jaccard_similarity(text1, text2)
            else:
                return await self._cosine_similarity(text1, text2)
                
        except Exception as e:
            logger.error(f"Similarity calculation xatosi: {str(e)}")
            return 0.0
    
    async def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Cosine similarity"""
        
        try:
            # TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            
            # Cosine similarity
            similarity = sklearn.metrics.pairwise.cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Cosine similarity xatosi: {str(e)}")
            return 0.0
    
    async def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Jaccard similarity"""
        
        try:
            # Token sets
            tokens1 = set(simple_preprocess(text1))
            tokens2 = set(simple_preprocess(text2))
            
            # Jaccard index
            intersection = len(tokens1.intersection(tokens2))
            union = len(tokens1.union(tokens2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception as e:
            logger.error(f"Jaccard similarity xatosi: {str(e)}")
            return 0.0

class AdvancedNLP:
    """Advanced NLP asosiy klassi"""
    
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ner = NamedEntityRecognizer()
        self.keyword_extractor = KeywordExtractor()
        self.topic_modeler = TopicModeler()
        self.similarity_analyzer = TextSimilarityAnalyzer()
        
        # Caches
        self.processing_cache = {}
    
    async def comprehensive_analysis(self, text: str, doc_id: str = None) -> Dict[str, Any]:
        """Keng qamrovli matn tahlili"""
        
        if not text:
            return {}
        
        if doc_id is None:
            doc_id = f"doc_{datetime.now().timestamp()}"
        
        # Cache check
        cache_key = f"{doc_id}_{hash(text)}"
        if cache_key in self.processing_cache:
            return self.processing_cache[cache_key]
        
        try:
            # Parallel processing
            tasks = [
                self.sentiment_analyzer.analyze_sentiment(text),
                self.ner.extract_entities(text),
                self.keyword_extractor.extract_keywords(text),
                # Topic modeling uchun multiple documents kerak
            ]
            
            sentiment_result, ner_result, keyword_result = await asyncio.gather(*tasks)
            
            # Similarity analysis (baseline text bilan)
            baseline_text = "This is a baseline financial market text."
            similarity = await self.similarity_analyzer.calculate_similarity(text, baseline_text)
            
            # Text preprocessing
            processed_tokens = self.preprocessor.preprocess_pipeline(text)
            
            # Statistics
            stats = {
                'word_count': len(text.split()),
                'char_count': len(text),
                'sentence_count': len(sent_tokenize(text)),
                'avg_word_length': np.mean([len(word) for word in text.split()]) if text.split() else 0,
                'processed_tokens': len(processed_tokens),
                'language': self._detect_language(text)
            }
            
            # Combined result
            result = {
                'document_id': doc_id,
                'text': text,
                'sentiment': asdict(sentiment_result),
                'entities': asdict(ner_result),
                'keywords': keyword_result,
                'similarity_to_baseline': similarity,
                'statistics': stats,
                'processed_tokens': processed_tokens,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Cache ga saqlash
            self.processing_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Comprehensive analysis xatosi: {str(e)}")
            return {'error': str(e), 'document_id': doc_id}
    
    async def batch_sentiment_analysis(self, texts: List[str], method: str = "vader") -> List[SentimentResult]:
        """Batch sentiment analysis"""
        
        tasks = [
            self.sentiment_analyzer.analyze_sentiment(text, method)
            for text in texts
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Exceptionlarni tozalash
        cleaned_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch sentiment analysis xatosi: {str(result)}")
                continue
            cleaned_results.append(result)
        
        return cleaned_results
    
    async def batch_ner(self, texts: List[str]) -> List[EntityResult]:
        """Batch named entity recognition"""
        
        tasks = [self.ner.extract_entities(text) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        cleaned_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch NER xatosi: {str(result)}")
                continue
            cleaned_results.append(result)
        
        return cleaned_results
    
    async def topic_analysis(self, documents: List[str], num_topics: int = 5) -> List[TopicResult]:
        """Topic analysis multiple documents"""
        
        return await self.topic_modeler.perform_topic_modeling(documents, num_topics)
    
    async def compare_documents(self, doc1: str, doc2: str) -> Dict[str, Any]:
        """Hujjatlarni solishtirish"""
        
        comparison = {
            'text1': doc1,
            'text2': doc2,
            'similarity': {}
        }
        
        # Similarity metrics
        try:
            comparison['similarity']['cosine'] = await self.similarity_analyzer.calculate_similarity(doc1, doc2, "cosine")
            comparison['similarity']['jaccard'] = await self.similarity_analyzer.calculate_similarity(doc1, doc2, "jaccard")
        except Exception as e:
            logger.error(f"Document comparison xatosi: {str(e)}")
        
        # Individual analyses
        try:
            analysis1 = await self.comprehensive_analysis(doc1, "doc1")
            analysis2 = await self.comprehensive_analysis(doc2, "doc2")
            
            comparison['analysis1'] = analysis1
            comparison['analysis2'] = analysis2
        except Exception as e:
            logger.error(f"Individual analysis xatosi: {str(e)}")
        
        return comparison
    
    def _detect_language(self, text: str) -> str:
        """Oddiy language detection"""
        
        # Bu oddiy heuristic - real implementationda langdetect library ishlatish mumkin
        english_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that'
        }
        
        words = text.lower().split()
        english_count = sum(1 for word in words if word in english_words)
        total_words = len(words)
        
        if total_words == 0:
            return "unknown"
        
        english_ratio = english_count / total_words
        
        if english_ratio > 0.1:
            return "en"
        else:
            return "unknown"  # Boshqa tillar uchun
    
    async def generate_report(self, analysis_result: Dict[str, Any]) -> str:
        """Analysis report yaratish"""
        
        try:
            report_parts = [
                "📊 MATN TAHLILI HISOBOTI",
                "=" * 50,
                f"Hujjat ID: {analysis_result.get('document_id', 'N/A')}",
                f"Tahlil sanasi: {analysis_result.get('analysis_timestamp', 'N/A')}",
                "",
                "📈 ASOSIY STATISTIKALAR:",
                f"  • So'zlar soni: {analysis_result.get('statistics', {}).get('word_count', 0)}",
                f"  • Belgi soni: {analysis_result.get('statistics', {}).get('char_count', 0)}",
                f"  • Gaplar soni: {analysis_result.get('statistics', {}).get('sentence_count', 0)}",
                f"  • O'rtacha so'z uzunligi: {analysis_result.get('statistics', {}).get('avg_word_length', 0):.2f}",
                "",
            ]
            
            # Sentiment analysis
            sentiment_data = analysis_result.get('sentiment', {})
            if sentiment_data:
                report_parts.extend([
                    "💭 SENTIMENT TAHLILI:",
                    f"  • Sentiment: {sentiment_data.get('sentiment', 'N/A')}",
                    f"  • Ishonchlilik: {sentiment_data.get('confidence', 0):.2f}",
                    f"  • Ijobiy: {sentiment_data.get('scores', {}).get('positive', 0):.2f}",
                    f"  • Salbiy: {sentiment_data.get('scores', {}).get('negative', 0):.2f}",
                    f"  • Neytral: {sentiment_data.get('scores', {}).get('neutral', 0):.2f}",
                    "",
                ])
            
            # Named entities
            entities_data = analysis_result.get('entities', {})
            if entities_data and entities_data.get('entities'):
                report_parts.append("🏷️  NOMLANGAN OBYEKTLAR:")
                for entity in entities_data['entities'][:5]:  # Top 5
                    report_parts.append(f"  • {entity.get('text', '')} ({entity.get('label', '')})")
                report_parts.append("")
            
            # Keywords
            keywords = analysis_result.get('keywords', [])
            if keywords:
                report_parts.append("🔑 MUHIM KALIT SO'ZLAR:")
                for kw in keywords[:5]:  # Top 5
                    report_parts.append(f"  • {kw.get('keyword', '')} (score: {kw.get('score', 0):.3f})")
                report_parts.append("")
            
            # Similarity
            similarity = analysis_result.get('similarity_to_baseline', 0)
            report_parts.extend([
                "🔗 O'XSHASHLIK:",
                f"  • Baseline ga o'xshashlik: {similarity:.3f}",
                "",
            ])
            
            return "\n".join(report_parts)
            
        except Exception as e:
            logger.error(f"Report generation xatosi: {str(e)}")
            return f"Hisobot yaratishda xato: {str(e)}"

# Demo va test funksiyalari
async def demo_nlp_system():
    """NLP tizimi demo"""
    
    print("🧠 Advanced NLP System Demo")
    print("=" * 50)
    
    # NLP tizimini yaratish
    nlp_system = AdvancedNLP()
    
    # Test matnlari
    test_texts = [
        "Bitcoin is going to the moon! This is such a bullish market right now. Everyone is buying! 🚀",
        "The market is crashing hard. Bitcoin just dropped 10% in one hour. Bears are in control! 😱",
        "Ethereum shows stable performance with consistent growth over the past months.",
        "Apple Inc. announced quarterly earnings that exceeded analyst expectations."
    ]
    
    print("\n📝 Text Analysis Examples:")
    print("-" * 40)
    
    # Har bir matn uchun tahlin qilish
    for i, text in enumerate(test_texts, 1):
        print(f"\n📄 Matn {i}:")
        print(f"'{text[:60]}...'")
        
        try:
            # Comprehensive analysis
            result = await nlp_system.comprehensive_analysis(text, f"demo_doc_{i}")
            
            # Sentiment
            sentiment = result.get('sentiment', {})
            print(f"💭 Sentiment: {sentiment.get('sentiment', 'N/A')} ({sentiment.get('confidence', 0):.2f})")
            
            # Entities
            entities = result.get('entities', {})
            if entities and entities.get('entities'):
                entity_names = [e.get('text', '') for e in entities['entities'][:3]]
                print(f"🏷️  Entities: {', '.join(entity_names)}")
            
            # Keywords
            keywords = result.get('keywords', [])
            if keywords:
                keyword_names = [k.get('keyword', '') for k in keywords[:3]]
                print(f"🔑 Keywords: {', '.join(keyword_names)}")
            
        except Exception as e:
            print(f"❌ Xato: {str(e)}")
    
    print("\n⚡ Batch Sentiment Analysis:")
    print("-" * 40)
    
    # Batch sentiment analysis
    try:
        sentiment_results = await nlp_system.batch_sentiment_analysis(test_texts, "vader")
        
        for i, result in enumerate(sentiment_results, 1):
            print(f"Matn {i}: {result.sentiment.value} (confidence: {result.confidence:.2f})")
            
    except Exception as e:
        print(f"❌ Batch sentiment xatosi: {str(e)}")
    
    print("\n🔍 Document Comparison:")
    print("-" * 40)
    
    # Hujjatlarni solishtirish
    try:
        doc1 = "Bitcoin is a revolutionary cryptocurrency that will change the world."
        doc2 = "Ethereum is a smart contract platform that enables decentralized applications."
        
        comparison = await nlp_system.compare_documents(doc1, doc2)
        
        print(f"Cosine similarity: {comparison['similarity']['cosine']:.3f}")
        print(f"Jaccard similarity: {comparison['similarity']['jaccard']:.3f}")
        
    except Exception as e:
        print(f"❌ Document comparison xatosi: {str(e)}")
    
    print("\n📊 Topic Modeling:")
    print("-" * 40)
    
    # Topic modeling
    try:
        topic_results = await nlp_system.topic_analysis(test_texts, num_topics=2)
        
        print(f"Top 2 topics extracted from {len(test_texts)} documents:")
        for i, result in enumerate(topic_results, 1):
            print(f"Document {i}:")
            for topic in result.topics:
                words = ', '.join(topic['words'][:5])
                print(f"  Topic {topic['topic_id']}: {words}")
            print()
            
    except Exception as e:
        print(f"❌ Topic modeling xatosi: {str(e)}")
    
    print("\n📋 Report Generation:")
    print("-" * 40)
    
    # Report generation
    try:
        full_analysis = await nlp_system.comprehensive_analysis(test_texts[0], "report_demo")
        report = await nlp_system.generate_report(full_analysis)
        
        print(report)
        
    except Exception as e:
        print(f"❌ Report generation xatosi: {str(e)}")
    
    print("\n✅ Demo yakunlandi!")

if __name__ == "__main__":
    # Demo ishga tushirish
    asyncio.run(demo_nlp_system())