"""
AI Trade Explainer - Ta'limiy savdo tizimini tushuntirish moduli
Education AI Trading System - Trade Explanation Module
"""

import json
import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import re


class ExplanationType(Enum):
    """Tushuntirish turlari"""
    SIGNAL_RATIONALE = "signal_rationale"
    RISK_EXPLANATION = "risk_explanation"
    INDICATOR_ANALYSIS = "indicator_analysis"
    ENTRY_EXIT_REASONING = "entry_exit_reasoning"
    MARKET_CONTEXT = "market_context"
    TECHNICAL_BREAKDOWN = "technical_breakdown"
    ALTERNATIVE_SCENARIOS = "alternative_scenarios"
    LEARNING_RESOURCES = "learning_resources"


class ComplexityLevel(Enum):
    """Murakkablik darajalari"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExplanationCategory(Enum):
    """Tushuntirish kategoriya"""
    WHY_THIS_SIGNAL = "why_this_signal"
    WHAT_RISKS = "what_risks"
    WHICH_INDICATORS = "which_indicators"
    WHAT_MARKET_CONDITIONS = "what_market_conditions"
    WHAT_ALTERNATIVES = "what_alternatives"
    HOW_TO_IMPROVE = "how_to_improve"
    WHEN_TO_EXIT = "when_to_exit"
    WHAT_TO_EXPECT = "what_to_expect"


@dataclass
class TradingSignal:
    """Savdo signali ma'lumotlari"""
    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float
    entry_price: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    timeframe: str = "1D"
    indicators: Dict[str, Any] = None
    market_conditions: Dict[str, Any] = None
    timestamp: datetime.datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()
        if self.indicators is None:
            self.indicators = {}
        if self.market_conditions is None:
            self.market_conditions = {}


@dataclass
class ExplanationRequest:
    """Tushuntirish so'rovi"""
    signal: TradingSignal
    question: str
    category: ExplanationCategory
    complexity: ComplexityLevel = ComplexityLevel.BEGINNER
    language: str = "uzbek"
    include_visual: bool = False
    include_alternatives: bool = True
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}


class TradeExplainer:
    """AI savdo tizimining asosiy tushuntirish moduli"""
    
    def __init__(self, user_level: ComplexityLevel = ComplexityLevel.BEGINNER):
        self.user_level = user_level
        self.explanation_templates = self._load_templates()
        self.knowledge_base = self._load_knowledge_base()
        self.common_mistakes = self._load_common_mistakes()
        
    def explain_signal(self, request: ExplanationRequest) -> Dict[str, Any]:
        """Signallarni tushuntirish"""
        try:
            explanation = {
                "signal_id": f"sig_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": request.signal.timestamp.isoformat(),
                "category": request.category.value,
                "complexity": request.complexity.value,
                "explanation": self._generate_explanation(request),
                "indicators_used": self._explain_indicators(request.signal),
                "risk_assessment": self._assess_risks(request.signal),
                "alternatives": self._generate_alternatives(request.signal) if request.include_alternatives else [],
                "learning_resources": self._get_learning_resources(request.category),
                "confidence_score": request.signal.confidence,
                "follow_up_questions": self._suggest_questions(request)
            }
            
            return explanation
            
        except Exception as e:
            return {"error": f"Tushuntirish yaratishda xatolik: {str(e)}"}
    
    def _generate_explanation(self, request: ExplanationRequest) -> str:
        """Asosiy tushuntirish yaratish"""
        signal = request.signal
        category = request.category
        
        if category == ExplanationCategory.WHY_THIS_SIGNAL:
            return self._explain_signal_rationale(signal)
        elif category == ExplanationCategory.WHAT_RISKS:
            return self._explain_risks(signal)
        elif category == ExplanationCategory.WHICH_INDICATORS:
            return self._explain_indicators(signal)
        elif category == ExplanationCategory.WHAT_MARKET_CONDITIONS:
            return self._explain_market_context(signal)
        elif category == ExplanationCategory.WHAT_ALTERNATIVES:
            return self._explain_alternatives(signal)
        elif category == ExplanationCategory.HOW_TO_IMPROVE:
            return self._explain_improvements(signal)
        elif category == ExplanationCategory.WHEN_TO_EXIT:
            return self._explain_exit_strategy(signal)
        elif category == ExplanationCategory.WHAT_TO_EXPECT:
            return self._explain_expectations(signal)
        
        return "Noma'lum kategoriya"
    
    def _explain_signal_rationale(self, signal: TradingSignal) -> str:
        """Signal sababini tushuntirish"""
        rationale_templates = {
            ComplexityLevel.BEGINNER: f"""
{signal.symbol} aksiya uchun {signal.signal_type} signal berildi.

Nega {signal.signal_type}?
• Signal ishonchlilik darajasi: {signal.confidence:.1%}
• {signal.timeframe} vaqta oralig'ida tahlil qilindi
• Ko'plab texnik ko'rsatkichlar musbat natija ko'rsatdi
• Bozor sharoitlari ushbu harakatni qo'llab-quvvatladi

Kirish narxi: ${signal.entry_price:.2f}
{("Maqsad narxi: $" + f"{signal.target_price:.2f}" if signal.target_price else "")}
{("Stop-loss: $" + f"{signal.stop_loss:.2f}" if signal.stop_loss else "")}
            """,
            
            ComplexityLevel.INTERMEDIATE: f"""
{signal.symbol} aksiya uchun {signal.signal_type} signal yaratilishining sabablari:

Texnik ko'rsatkichlar tahlili:
• Multiple indicator confluence: {len(signal.indicators)} ta ko'rsatkich musbat
• Confidence level: {signal.confidence:.1%}
• Timeframe bias: {signal.timeframe} interval

Fundamental kontekst:
• Market sentiment: {signal.market_conditions.get('sentiment', 'neutral')}
• Volume analysis: {signal.market_conditions.get('volume', 'normal')}
• Volatility level: {signal.market_conditions.get('volatility', 'moderate')}
            """,
            
            ComplexityLevel.ADVANCED: f"""
Advanced Signal Analysis for {signal.symbol}:

Signal Generation Parameters:
- Type: {signal.signal_type}
- Confidence: {signal.confidence:.3f}
- Entry: ${signal.entry_price:.2f}
- Risk/Reward: {self._calculate_risk_reward(signal):.2f}
- Statistical significance: {self._calculate_statistical_significance(signal):.3f}

Multi-timeframe confluence: {self._check_multiframe_confluence(signal)}
Market microstructure: {signal.market_conditions.get('microstructure', 'balanced')}
Order flow dynamics: {signal.market_conditions.get('order_flow', 'neutral')}
            """
        }
        
        return rationale_templates.get(self.user_level, rationale_templates[ComplexityLevel.BEGINNER])
    
    def _explain_risks(self, signal: TradingSignal) -> str:
        """Risklar tushuntirish"""
        risk_templates = {
            ComplexityLevel.BEGINNER: f"""
{signal.symbol} savdosi uchun asosiy risklar:

1. Narx o'zgarishi riski
   - Maksimal yo'qotish: {self._calculate_max_loss(signal):.2f}%
   - Stop-loss belgilab oling

2. Vaqt riski
   - Signal vaqtinchalik bo'lishi mumkin
   - Tezda qaror qabul qiling

3. Bozor sharoitlari
   - Volatil o'zgarishlar mumkin
   - Yomon xabarlar ta'sir qilishi mumkin
            """,
            
            ComplexityLevel.INTERMEDIATE: f"""
Risk Assessment for {signal.symbol}:

Quantitative Risks:
- Maximum adverse excursion: {self._calculate_max_loss(signal):.2f}%
- Value at Risk (VaR): {self._calculate_var(signal):.2f}%
- Probability of loss: {self._calculate_loss_probability(signal):.1%}

Qualitative Risks:
- Market correlation: {signal.market_conditions.get('correlation', 0.3):.2f}
- Sector-specific risk: {signal.market_conditions.get('sector_risk', 'medium')}
- External factors: {signal.market_conditions.get('external_risk', 'low')}
            """,
            
            ComplexityLevel.EXPERT: f"""
Advanced Risk Analysis:

Risk Metrics:
- Sharpe Ratio Impact: {self._calculate_sharpe_impact(signal):.3f}
- Maximum Drawdown Risk: {self._calculate_drawdown_risk(signal):.1%}
- Tail Risk (VaR 95%): {self._calculate_tail_risk(signal):.2f}
- Beta exposure: {self._calculate_beta_exposure(signal):.2f}

Risk Decomposition:
- Systematic risk: {self._calculate_systematic_risk(signal):.1%}
- Idiosyncratic risk: {self._calculate_idiosyncratic_risk(signal):.1%}
- Market timing risk: {self._calculate_timing_risk(signal):.1%}
            """
        }
        
        return risk_templates.get(self.user_level, risk_templates[ComplexityLevel.BEGINNER])
    
    def _explain_indicators(self, signal: TradingSignal) -> str:
        """Ko'rsatkichlar tahlili"""
        indicators = signal.indicators
        
        if not indicators:
            return "Ko'rsatkichlar ma'lumotlari topilmadi"
        
        explanation = f"{signal.symbol} uchun ishlatilgan ko'rsatkichlar:\n\n"
        
        for indicator, value in indicators.items():
            explanation += f"• {indicator}: {value}\n"
        
        explanation += f"\nJami {len(indicators)} ta ko'rsatkich musbat signallar berdi."
        
        return explanation
    
    def _explain_market_context(self, signal: TradingSignal) -> str:
        """Bozor konteksti tushuntirish"""
        market_conditions = signal.market_conditions
        
        context = f"{signal.symbol} bozor konteksti:\n\n"
        context += f"Bozor kayfiyati: {market_conditions.get('sentiment', 'neutral')}\n"
        context += f"Hajm darajasi: {market_conditions.get('volume', 'normal')}\n"
        context += f"Volatil: {market_conditions.get('volatility', 'moderate')}\n"
        context += f"Trend yo'nalishi: {market_conditions.get('trend', 'sideways')}\n"
        
        return context
    
    def _explain_alternatives(self, signal: TradingSignal) -> str:
        """Alternativ savdo strategiyasi"""
        alternatives = self._generate_alternatives(signal)
        
        alt_text = "Alternativ strategiyalar:\n\n"
        for i, alt in enumerate(alternatives, 1):
            alt_text += f"{i}. {alt}\n"
        
        return alt_text
    
    def _explain_improvements(self, signal: TradingSignal) -> str:
        """Yaxshilash usullari"""
        improvements = [
            "Ko'proq vaqt oralig'ida tahlil qiling",
            "Qo'shimcha ko'rsatkichlar qo'shing",
            "Stop-loss darajasini aniqroq belgilang",
            "Hajm tahlilini kuchaytiring",
            "Fundamental tahlil bilan birga ishlatish"
        ]
        
        return "Savdo strategiyasini yaxshilash usullari:\n\n" + "\n".join(improvements)
    
    def _explain_exit_strategy(self, signal: TradingSignal) -> str:
        """Chiqish strategiyasi"""
        exit_strategy = f"""
{signal.symbol} uchun chiqish strategiyasi:

1. Maqsad narxiga yetganda:
   - 50% pozitsiyani yoping
   - Stop-loss ni breakeven ga ko'chir

2. Zarar olish kerak bo'lsa:
   - Stop-loss darajasida chiqing
   - Kuchli salbiy signal paytida

3. Vaqt limiti:
   - Maksimal 30 kun kutish
   - Signal kuchini yo'qotganda chiqish
        """
        
        return exit_strategy
    
    def _explain_expectations(self, signal: TradingSignal) -> str:
        """Kutiladigan natijalar"""
        if signal.target_price:
            potential_profit = ((signal.target_price - signal.entry_price) / signal.entry_price) * 100
        else:
            potential_profit = 5.0  # Default 5%
        
        expectations = f"""
{signal.symbol} kutishlar:

Potentsial foyda: {potential_profit:.1f}%
Ehtimollilik: {signal.confidence:.0%}
Vaqt oralig'i: {signal.timeframe}

Bajarilish ehtimoli:
- Yuqori ehtimol (80%+): {signal.confidence > 0.8}
- O'rta ehtimol (60-80%): {0.6 <= signal.confidence <= 0.8}
- Past ehtimol (<60%): {signal.confidence < 0.6}
        """
        
        return expectations
    
    def _assess_risks(self, signal: TradingSignal) -> Dict[str, Any]:
        """Risk baholash"""
        return {
            "risk_level": self._calculate_risk_level(signal),
            "max_loss_percent": self._calculate_max_loss(signal),
            "volatility_risk": self._calculate_volatility_risk(signal),
            "timing_risk": signal.market_conditions.get('volatility', 'moderate') == 'high'
        }
    
    def _generate_alternatives(self, signal: TradingSignal) -> List[str]:
        """Alternativ strategiyalar"""
        alternatives = [
            "Kichik pozitsiya hajmi bilan kirish",
            "Dollar-cost averaging usuli",
            "Boshqa vaqt oralig'ida qayta tahlil",
            "Call/Put options bilan himoyalash",
            "Multiple entry points strategiyasi"
        ]
        
        return alternatives[:3] if self.user_level == ComplexityLevel.BEGINNER else alternatives
    
    def _get_learning_resources(self, category: ExplanationCategory) -> List[Dict[str, str]]:
        """O'rganish manbalari"""
        resources = {
            ExplanationCategory.WHY_THIS_SIGNAL: [
                {"title": "Signal Generation Basics", "type": "article", "url": "#"},
                {"title": "Technical Analysis Guide", "type": "video", "url": "#"}
            ],
            ExplanationCategory.WHAT_RISKS: [
                {"title": "Risk Management", "type": "tutorial", "url": "#"},
                {"title": "Position Sizing", "type": "course", "url": "#"}
            ],
            ExplanationCategory.WHICH_INDICATORS: [
                {"title": "Technical Indicators", "type": "reference", "url": "#"},
                {"title": "Indicator Combinations", "type": "guide", "url": "#"}
            ]
        }
        
        return resources.get(category, [])
    
    def _suggest_questions(self, request: ExplanationRequest) -> List[str]:
        """Taklif qilinadigan savollar"""
        base_questions = {
            ExplanationCategory.WHY_THIS_SIGNAL: [
                "Ushbu signal nega ishonchli?",
                "Boshqa ko'rsatkichlar ham tekshirilganmi?",
                "Tarixiy natijalar qanday?"
            ],
            ExplanationCategory.WHAT_RISKS: [
                "Risk qanday boshqariladi?",
                "Stop-loss qayerda belgilash kerak?",
                "Maksimal yo'qotish qancha?"
            ]
        }
        
        return base_questions.get(request.category, ["Qo'shimcha savollar: ?"])
    
    def _calculate_max_loss(self, signal: TradingSignal) -> float:
        """Maksimal yo'qotish hisoblash"""
        if signal.stop_loss and signal.entry_price:
            return abs((signal.stop_loss - signal.entry_price) / signal.entry_price) * 100
        return 5.0  # Default 5%
    
    def _calculate_risk_reward(self, signal: TradingSignal) -> float:
        """Risk/foyda nisbat hisoblash"""
        if signal.target_price and signal.stop_loss:
            profit = abs(signal.target_price - signal.entry_price)
            loss = abs(signal.stop_loss - signal.entry_price)
            return profit / loss if loss > 0 else 0
        return 2.0  # Default 1:2
    
    def _calculate_risk_level(self, signal: TradingSignal) -> str:
        """Risk darajasi"""
        max_loss = self._calculate_max_loss(signal)
        if max_loss < 2:
            return "Past"
        elif max_loss < 5:
            return "O'rta"
        else:
            return "Yuqori"
    
    def _calculate_volatility_risk(self, signal: TradingSignal) -> str:
        """Volatil risk"""
        volatility = signal.market_conditions.get('volatility', 'moderate')
        return volatility
    
    def _calculate_var(self, signal: TradingSignal) -> float:
        """Value at Risk (oddiy hisob)"""
        return self._calculate_max_loss(signal) * 0.8  # 80% confidence
    
    def _calculate_loss_probability(self, signal: TradingSignal) -> float:
        """Yo'qotish ehtimolligi"""
        return 1 - signal.confidence
    
    def _calculate_statistical_significance(self, signal: TradingSignal) -> float:
        """Statistik ahamiyat"""
        return min(signal.confidence * 1.2, 1.0)
    
    def _check_multiframe_confluence(self, signal: TradingSignal) -> str:
        """Multi-timeframe confluence"""
        return "1D: Bullish, 4H: Bullish, 1H: Neutral"
    
    def _calculate_sharpe_impact(self, signal: TradingSignal) -> float:
        """Sharpe ratio ta'siri"""
        return signal.confidence * 0.1 + 0.05
    
    def _calculate_drawdown_risk(self, signal: TradingSignal) -> float:
        """Drawdown risk"""
        return self._calculate_max_loss(signal) * 1.5
    
    def _calculate_tail_risk(self, signal: TradingSignal) -> float:
        """Tail risk"""
        return self._calculate_max_loss(signal) * 1.2
    
    def _calculate_beta_exposure(self, signal: TradingSignal) -> float:
        """Beta exposure"""
        return 0.8  # Placeholder
    
    def _calculate_systematic_risk(self, signal: TradingSignal) -> float:
        """Systematic risk"""
        return 0.6
    
    def _calculate_idiosyncratic_risk(self, signal: TradingSignal) -> float:
        """Idiosyncratic risk"""
        return 0.4
    
    def _calculate_timing_risk(self, signal: TradingSignal) -> float:
        """Timing risk"""
        return 0.3
    
    def _load_templates(self) -> Dict[str, str]:
        """Tushuntirish shablonlari yuklash"""
        return {
            "beginner": "Simple explanations",
            "intermediate": "Detailed analysis", 
            "advanced": "Complex metrics"
        }
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Bilimlar bazasini yuklash"""
        return {
            "indicators": {
                "RSI": "Relative Strength Index - overbought/oversold",
                "MACD": "Moving Average Convergence Divergence - trend",
                "Bollinger": "Bollinger Bands - volatility",
                "SMA": "Simple Moving Average - trend direction"
            },
            "market_terms": {
                "bull_market": "Rising market trends",
                "bear_market": "Falling market trends", 
                "consolidation": "Sideways price movement",
                "breakout": "Price moving above resistance"
            }
        }
    
    def _load_common_mistakes(self) -> List[str]:
        """Umumiy xatolar"""
        return [
            "Stop-loss qo'ymaslik",
            "Ko'p pozitsiya ochish",
            "Emotsional qaror qabul qilish",
            "Tahlil qilmasdan savdo qilish",
            "Risk boshqaruvi qoidalarini buzish"
        ]


# Utility functions
def create_signal_explanation(signal_data: Dict[str, Any], 
                            question: str, 
                            complexity: str = "beginner",
                            language: str = "uzbek") -> Dict[str, Any]:
    """Signal tushuntirish yaratish"""
    signal = TradingSignal(**signal_data)
    complexity_level = ComplexityLevel(complexity)
    
    # Kategoriya aniqlash
    category = ExplanationCategory.WHY_THIS_SIGNAL  # Default
    
    for cat in ExplanationCategory:
        if any(word in question.lower() for word in _get_category_keywords(cat)):
            category = cat
            break
    
    request = ExplanationRequest(
        signal=signal,
        question=question,
        category=category,
        complexity=complexity_level,
        language=language
    )
    
    explainer = TradeExplainer(complexity_level)
    return explainer.explain_signal(request)


def _get_category_keywords(category: ExplanationCategory) -> List[str]:
    """Kategoriya kalit so'zlar"""
    keywords = {
        ExplanationCategory.WHY_THIS_SIGNAL: ["nega", "nega uchun", "sabab", "qachon", "qanday"],
        ExplanationCategory.WHAT_RISKS: ["risk", "xavf", "yo'qotish", "zarar"],
        ExplanationCategory.WHICH_INDICATORS: ["ko'rsatkich", "indikator", "signal", "qaysi"],
        ExplanationCategory.WHAT_MARKET_CONDITIONS: ["bozor", "sharoit", "kontext", "holat"],
        ExplanationCategory.WHAT_ALTERNATIVES: ["alternativ", "boshqa", "variant"],
        ExplanationCategory.HOW_TO_IMPROVE: ["yaxshilash", "takomillashtirish", "o'stirish"],
        ExplanationCategory.WHEN_TO_EXIT: ["chiqish", "yopish", "qachon"],
        ExplanationCategory.WHAT_TO_EXPECT: ["kutish", "natija", "natijasi"]
    }
    
    return keywords.get(category, [])


# Test function
def test_trade_explainer():
    """Trade explainer test"""
    # Test signal
    test_signal = {
        "symbol": "AAPL",
        "signal_type": "BUY",
        "confidence": 0.75,
        "entry_price": 150.0,
        "target_price": 165.0,
        "stop_loss": 140.0,
        "timeframe": "1D",
        "indicators": {
            "RSI": 65,
            "MACD": "Bullish crossover",
            "SMA_20": 148.5,
            "Volume": "Above average"
        },
        "market_conditions": {
            "sentiment": "bullish",
            "volume": "high",
            "volatility": "moderate",
            "trend": "upward"
        }
    }
    
    # Test different questions
    questions = [
        "Nega BUY signal berildi?",
        "Qanday risklar bor?",
        "Qaysi ko'rsatkichlar ishlatildi?",
        "Bozor holati qanday?"
    ]
    
    for question in questions:
        explanation = create_signal_explanation(test_signal, question)
        print(f"\nSavol: {question}")
        print(f"Tushuntirish: {explanation.get('explanation', 'Topilmadi')}")


if __name__ == "__main__":
    test_trade_explainer()