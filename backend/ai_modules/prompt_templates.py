"""
Prompt Templates - AI Prompt Optimizer uchun prompt shablonlari
Har xil kategoriyadagi optimallashtirilgan prompt shablonlari
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
import random

class TemplateType(Enum):
    """Shablon turi"""
    STRUCTURED = "structured"
    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical"
    EDUCATIONAL = "educational"
    DECISION_MAKING = "decision_making"
    TROUBLESHOOTING = "troubleshooting"
    CREATIVE = "creative"
    SYSTEMATIC = "systematic"
    CONTEXTUAL = "contextual"
    MULTI_TURN = "multi_turn"
    SAFETY_FOCUSED = "safety_focused"
    COMPLIANCE_DRIVEN = "compliance_driven"
    OPTIMIZED = "optimized"

class SkillLevel(Enum):
    """Treyder mahorat darajasi"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Language(Enum):
    """Qo'llab-quvvatlanadigan tillar"""
    UZBEK = "uzbek"
    ENGLISH = "english"
    RUSSIAN = "russian"

class PromptCategory(Enum):
    """Prompt kategoriyasi"""
    TECHNICAL_ANALYSIS = "technical_analysis"
    RISK_MANAGEMENT = "risk_management"
    STRATEGY_DEVELOPMENT = "strategy_development"
    MARKET_ANALYSIS = "market_analysis"
    EDUCATION = "education"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    TRADING_PSYCHOLOGY = "trading_psychology"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    NEWS_ANALYSIS = "news_analysis"
    BACKTESTING = "backtesting"
    COMPLIANCE = "compliance"
    RESEARCH = "research"
    ERROR_HANDLING = "error_handling"
    SAFETY = "safety"
    REGULATORY = "regulatory"
    SIGNAL_GENERATION = "signal_generation"
    ECONOMIC_CALENDAR = "economic_calendar"
    CONTEXT_AWARENESS = "context_awareness"

@dataclass
class Template:
    """Advanced Prompt Template with comprehensive metadata"""
    id: str
    category: PromptCategory
    template_type: TemplateType
    name: str
    description: str
    base_prompt: str
    variables: Dict[str, str]  # variable_name: description
    examples: List[str]
    best_practices: List[str]
    success_criteria: List[str]
    target_audience: str
    complexity_level: str  # beginner, intermediate, advanced
    language: str = "uzbek"
    tags: List[str] = None
    version: str = "2.0"
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    usage_count: int = 0
    success_rate: float = 0.0
    
    # Advanced fields
    skill_level: SkillLevel = SkillLevel.INTERMEDIATE
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    safety_guidelines: List[str] = field(default_factory=list)
    regulatory_notes: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    ab_test_variants: List[str] = field(default_factory=list)
    industry_knowledge: List[str] = field(default_factory=list)
    conversation_flow: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    last_optimized: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    optimization_history: List[Dict[str, Any]] = field(default_factory=list)
    multi_language_support: bool = True
    context_aware: bool = True
    safety_enhanced: bool = True
    regulatory_compliant: bool = True

class TemplateManager:
    """Prompt shablonlarini boshqarish"""
    
    def __init__(self):
        """Template Manager ni ishga tushirish"""
        self.templates: Dict[str, Template] = {}
        self.category_templates: Dict[PromptCategory, List[str]] = {}
        self.template_analytics: Dict[str, Dict[str, Any]] = {}
        
        # Initialize templates
        self._initialize_templates()
        self._setup_analytics()
    
    def _initialize_templates(self):
        """Shablonlarni dastlabki sozlamalar bilan yaratish"""
        
        # TECHNICAL ANALYSIS TEMPLATES
        self.templates["tech_analysis_basic"] = Template(
            id="tech_analysis_basic",
            category=PromptCategory.TECHNICAL_ANALYSIS,
            template_type=TemplateType.ANALYTICAL,
            name="Texnik tahlil - Asosiy",
            description="Aktivlar uchun asosiy texnik tahlil shabloni",
            base_prompt="""**TEXNIK TAHLIL SO'ROVI**

Aktiv: {asset}
Vaqt oralig'i: {timeframe}
Tahlil sanasi: {analysis_date}

Iltimos quyidagi jihatlarni tahlil qiling:

1. **Trend tahlili:**
   - Hozirgi trend yo'nalishi (ko'tarilish/tushish/yon)
   - Trend kuchlilik darajasi
   - Trend o'zgarish ehtimoli

2. **Texnik indikatorlar:**
   - RSI holati va xulosa
   - MACD signal va divergensiyalar
   - Bollinger Bands pozitsiyasi
   - Volume tahlili

3. **Support va Resistance:**
   - Muhim darajalar
   - Potentsial o'zgarish nuqtalari
   - Breakout ehtimollari

4. **Narx harakati:**
   - Candlestick patternlar
   - Volume-price harakati
   - Gap tahlili

5. **Tahlil xulosasi:**
   - Qisqa muddatli (1-3 kun) ko'rinish
   - O'rta muddatli (1-4 hafta) ko'rinish
   - Tavsiyalar va xavf darajasi

Tahlilni aniq, amaliy va tushunarli formatda taqdim eting.""",
            variables={
                "asset": "Tahlil qilinadigan aktiv (masalan, EUR/USD, AAPL, BTC)",
                "timeframe": "Vaqt oralig'i (1h, 4h, 1d, 1w, 1M)",
                "analysis_date": "Tahlil sanasi"
            },
            examples=[
                "EUR/USD uchun 1 kunlik texnik tahlil",
                "AAPL aksiyalari uchun haftalik tahlil"
            ],
            best_practices=[
                "Har bir indikatrni alohida tushuntiring",
                "Volume ma'lumotlarini ham ko'rsating",
                "Xavf omillarini aytib o'ting"
            ],
            success_criteria=[
                "Barcha asosiy indikatorlar tahlil qilingan",
                "Aniq darajalar ko'rsatilgan",
                "Amaliy tavsiyalar berilgan"
            ],
            target_audience="Boshlang'ich va o'rta darajadagi treyderlar",
            complexity_level="intermediate"
        )

        self.templates["tech_analysis_advanced"] = Template(
            id="tech_analysis_advanced",
            category=PromptCategory.TECHNICAL_ANALYSIS,
            template_type=TemplateType.ANALYTICAL,
            name="Texnik tahlil - Ilg'or",
            description="Professional darajadagi chuqur texnik tahlil",
            base_prompt="""**ILG'OR TEXNIK TAHLIL**

**Aktiv ma'lumotlari:**
- Asset: {asset}
- Market: {market}
- Timeframe: {timeframe}
- Tahlil davri: {period}
- Asosiy trading session: {session}

**Chuqur Tahlil Talablari:**

**A. Market Structure Analysis:**
- Higher Highs / Lower Lows pattern
- Market structure shift (MSD) aniqlash
- Liquidity zone identification
- Order block tahlili
- Fair value gap (FVG) aniqlash

**B. Advanced Indicator Fusion:**
- Multi-timeframe confluence
- Custom indicator combination
- Volume Profile analysis
- Market maker model
- Institutional levels

**C. Price Action Mastery:**
- Candlestick psychology
- Wyckoff method qo'llash
- Smart money concepts
- Market microstructure
- Execution timing

**D. Risk-Reward Optimization:**
- Position sizing recommendation
- Entry/exit strategy
- Stop-loss placement
- Profit-taking levels
- Risk-adjusted returns

**E. Alternative Scenarios:**
- Base case (60% probability)
- Bull case (25% probability)
- Bear case (15% probability)
- Contingency plans

**F. Execution Framework:**
- Order type recommendations
- Time-based execution
- Volatility considerations
- News impact assessment
- Correlation analysis

Provide quantitative backing, historical data references, and probability assessments for each recommendation.""",
            variables={
                "asset": "Aniq aktiv nomi va symboli",
                "market": "Bozor turi (Forex, Equity, Crypto, Commodities)",
                "timeframe": "Asosiy va confirmation timeframe",
                "period": "Tahlil davri (kunlik, haftalik, oylik)",
                "session": "Asosiy trading session (London, New York, Asia)"
            },
            examples=[
                "GBP/JPY uchun institutional level tahlili",
                "TSLA options flow tahlili"
            ],
            best_practices=[
                "Multiple confluence factors qo'llang",
                "Quantitative probability estimates",
                "Risk management integration"
            ],
            success_criteria=[
                "Chuqur market structure understanding",
                "Precise level identification",
                "Actionable execution plan"
            ],
            target_audience="Professional va institutional treyderlar",
            complexity_level="advanced"
        )

        # RISK MANAGEMENT TEMPLATES
        self.templates["risk_assessment"] = Template(
            id="risk_assessment",
            category=PromptCategory.RISK_MANAGEMENT,
            template_type=TemplateType.DECISION_MAKING,
            name="Xavf baholash va boshqarish",
            description="Comprehensive risk assessment framework",
            base_prompt=""""**XAVF BAHOLASH FRAMEWORKI**

**Portfolio va Trader profili:**
- Joriy portfel qiymati: {portfolio_value}
- Risk profili: {risk_profile}
- Experience darajasi: {experience_level}
- Trading capital: {trading_capital}
- Time horizon: {time_horizon}

**Xavf Tahlil Kriterilari:**

**1. Position Risk Assessment:**
- Individual position xavfi (%)
- Portfolio correlation
- Sector/asset concentration
- Geographic risk
- Liquidity risk

**2. Market Risk Analysis:**
- Volatility environment
- Correlation breakdown risk
- Systematic risk factors
- Black swan events
- Regulatory changes

**3. Operational Risk:**
- Execution risk
- Technology failures
- Counterparty risk
- Settlement risk
- Counterparty concentration

**4. Psychological Risk:**
- Overconfidence bias
- Loss aversion impact
- FOMO-driven decisions
- Revenge trading tendency
- Decision fatigue

**5. Risk Management Framework:**

**Stop-Loss Strategy:**
- Fixed percentage stops
- ATR-based stops
- Support/resistance stops
- Time-based stops
- Volatility stops

**Position Sizing:**
- 1% rule application
- Kelly criterion
- Risk parity
- Maximum drawdown limits
- Correlation adjustments

**Portfolio Protection:**
- Hedging strategies
- Diversification metrics
- Risk contribution analysis
- Stress testing
- Scenario analysis

**6. Action Plan:**
- Immediate risk reduction steps
- Medium-term adjustments
- Long-term strategic changes
- Monitoring protocols
- Review schedules

Tahlilni raqamli metrikalar, aniq tavsiyalar va vaqt jadvali bilan taqdim eting.""",
            variables={
                "portfolio_value": "Joriy portfel qiymati (USD)",
                "risk_profile": "Risk profili (conservative, moderate, aggressive)",
                "experience_level": "Tajriba darajasi (beginner, intermediate, advanced)",
                "trading_capital": "Trading uchun ajratilgan kapital",
                "time_horizon": "Investment muddati (short, medium, long-term)"
            },
            examples=[
                "50K USD portfel uchun risk assessment",
                "Aggressive trader uchun risk management plan"
            ],
            best_practices=[
                "Quantitative risk metrics",
                "Stress testing scenarios",
                "Regular monitoring protocols"
            ],
            success_criteria=[
                "Clear risk exposure identification",
                "Actionable mitigation steps",
                "Quantified risk limits"
            ],
            target_audience="Barcha darajadagi investorlar va treyderlar",
            complexity_level="intermediate"
        )

        # STRATEGY DEVELOPMENT TEMPLATES
        self.templates["strategy_framework"] = Template(
            id="strategy_framework",
            category=PromptCategory.STRATEGY_DEVELOPMENT,
            template_type=TemplateType.STRUCTURED,
            name="Strategy Development Framework",
            description="Structured approach to trading strategy development",
            base_prompt=""""**TRADING STRATEGY DEVELOPMENT**

**Strategy Background:**
- Target market: {market}
- Trading style: {trading_style}
- Capital allocation: {capital_allocation}
- Time commitment: {time_commitment}
- Performance target: {performance_target}

**Strategy Development Process:**

**1. Market Analysis & Opportunity Identification:**
- Market inefficiency discovery
- Volatility patterns
- Seasonal trends
- Event-driven opportunities
- Statistical anomalies

**2. Strategy Conceptualization:**
- Core trading idea
- Edge hypothesis
- Market behavior assumption
- Risk-reward premise
- Scalability factors

**3. Technical Implementation:**
- Entry criteria definition
- Exit logic development
- Risk management rules
- Position sizing method
- Order management

**4. Backtesting Framework:**
- Historical data period
- Performance metrics
- Benchmark comparison
- Risk-adjusted returns
- Drawdown analysis

**5. Optimization Process:**
- Parameter optimization
- Walk-forward analysis
- Out-of-sample testing
- Robustness testing
- Monte Carlo simulation

**6. Forward Testing:**
- Paper trading phase
- Live market validation
- Performance monitoring
- Strategy refinement
- Scaling preparation

**7. Risk Management Integration:**
- Maximum drawdown limits
- Risk contribution monitoring
- Correlation analysis
- Tail risk management
- Stress testing

**Strategy Validation Criteria:**

**Performance Metrics:**
- Win rate: {target_win_rate}%
- Risk-Reward ratio: {target_rr_ratio}
- Maximum drawdown: {max_dd}%
- Sharpe ratio: {target_sharpe}
- Calmar ratio: {target_calmar}

**Robustness Tests:**
- Parameter sensitivity
- Market regime changes
- Transaction cost impact
- Slippage modeling
- Capacity analysis

**Risk Management Rules:**
- Maximum daily loss: {max_daily_loss}%
- Maximum position size: {max_position_size}%
- Correlation limits: {correlation_limit}%
- Liquidity requirements: {liquidity_requirements}

Provide detailed implementation timeline, performance expectations, and risk mitigation strategies.""",
            variables={
                "market": "Target bozor (forex, stocks, crypto, commodities)",
                "trading_style": "Trading uslubi (scalping, day trading, swing, position)",
                "capital_allocation": "Strategiyaga ajratilgan kapital foizi",
                "time_commitment": "Kundalik vaqt ajratish",
                "performance_target": "Yillik performance maqsadi",
                "target_win_rate": "Maqsadli win rate (%)",
                "target_rr_ratio": "Maqsadli risk-reward ratio",
                "max_dd": "Maksimal drawdown (%)",
                "target_sharpe": "Maqsadli Sharpe ratio",
                "target_calmar": "Maqsadli Calmar ratio",
                "max_daily_loss": "Kundalik maksimal yo'qotish (%)",
                "max_position_size": "Maksimal pozitsiya hajmi (%)",
                "correlation_limit": "Korrelatsiya limiti (%)",
                "liquidity_requirements": "Likvidlik talablari"
            },
            examples=[
                "Mean reversion strategy development",
                "Momentum-based swing trading system"
            ],
            best_practices=[
                "Data-driven development",
                "Multiple validation stages",
                "Risk-first approach"
            ],
            success_criteria=[
                "Quantified performance expectations",
                "Robust risk management",
                "Scalable implementation"
            ],
            target_audience="Professional strategy developers",
            complexity_level="advanced"
        )

        # MARKET ANALYSIS TEMPLATES
        self.templates["market_outlook"] = Template(
            id="market_outlook",
            category=PromptCategory.MARKET_ANALYSIS,
            template_type=TemplateType.ANALYTICAL,
            name="Market Outlook & Analysis",
            description="Comprehensive market outlook and analysis",
            base_prompt=""""**BOZOR KO'RINISH VA TAHLIL**

**Analysis Parameters:**
- Market focus: {market_focus}
- Analysis period: {analysis_period}
- Key assets: {key_assets}
- Economic indicators: {economic_indicators}
- Analysis date: {analysis_date}

**Comprehensive Market Analysis:**

**1. Macroeconomic Environment:**
- Global economic trends
- Central bank policies
- Inflation outlook
- Interest rate expectations
- Economic data impact

**2. Market Sentiment Analysis:**
- Retail trader sentiment
- Institutional positioning
- Fear & Greed index
- Options flow analysis
- Positioning reports

**3. Technical Market Structure:**
- Index performance
- Sector rotation
- Breadth analysis
- Volume patterns
- Momentum indicators

**4. Key Level Analysis:**
- Major support/resistance
- Fibonacci retracements
- Trend lines
- Chart patterns
- Volume profile

**5. Cross-Asset Analysis:**
- Equity-bond correlation
- Currency trends
- Commodity performance
- Crypto market health
- International flows

**6. Event Risk Assessment:**
- Upcoming economic releases
- Central bank meetings
- Earnings season impact
- Geopolitical events
- Seasonal factors

**Market Scenarios:**

**Bull Case (Probability: {bull_probability}%):**
- Key catalysts
- Expected performance
- Best-performing sectors
- Risk factors

**Base Case (Probability: {base_probability}%):**
- Most likely scenario
- Market range expectations
- Balanced sector performance
- Key risks

**Bear Case (Probability: {bear_probability}%):**
- Downside risks
- Sector vulnerabilities
- Flight to safety
- Recovery timeline

**Actionable Recommendations:**

**Short-term (1-2 weeks):**
- Immediate opportunities
- Risk management focus
- Key levels to watch
- Event-driven trades

**Medium-term (1-3 months):**
- Strategic positioning
- Sector allocation
- Trend following
- Value opportunities

**Long-term (3-12 months):**
- Structural trends
- Demographic impacts
- Technology disruption
- Regulatory changes

Provide probability-weighted scenarios, specific entry/exit strategies, and risk management guidelines.""",
            variables={
                "market_focus": "Asosiy bozor (US, European, Asian, Global)",
                "analysis_period": "Tahlil davri (1 hafta, 1 oy, 1 chorak)",
                "key_assets": "Asosiy aktivlar (SPY, QQQ, VIX, etc.)",
                "economic_indicators": "Muhim iqtisodiy ko'rsatkichlar",
                "analysis_date": "Tahlil sanasi",
                "bull_probability": "Bull case ehtimoli (%)",
                "base_probability": "Base case ehtimoli (%)",
                "bear_probability": "Bear case ehtimoli (%)"
            },
            examples=[
                "US equity market Q4 outlook",
                "Global forex market monthly outlook"
            ],
            best_practices=[
                "Multiple scenario analysis",
                "Quantitative probability assessment",
                "Risk-adjusted recommendations"
            ],
            success_criteria=[
                "Clear market direction",
                "Specific price targets",
                "Actionable timing"
            ],
            target_audience="Portfolio managers va market analysts",
            complexity_level="intermediate"
        )

        # EDUCATION TEMPLATES
        self.templates["trading_education"] = Template(
            id="trading_education",
            category=PromptCategory.EDUCATION,
            template_type=TemplateType.EDUCATIONAL,
            name="Trading Education & Learning",
            description="Comprehensive trading education framework",
            base_prompt=""""**TRADING BILIM VA TA'LIM**

**Student Profile:**
- Current knowledge level: {knowledge_level}
- Trading experience: {experience_years}
- Learning objectives: {learning_goals}
- Available time: {study_time}
- Preferred learning style: {learning_style}

**Learning Path Framework:**

**Phase 1: Foundation Building**
- Market basics
- Order types
- Risk management
- Chart reading
- Trading psychology

**Phase 2: Technical Analysis**
- Candlestick patterns
- Trend analysis
- Support/resistance
- Indicators
- Chart patterns

**Phase 3: Fundamental Analysis**
- Economic indicators
- Company analysis
- Sector analysis
- Global factors
- Earnings analysis

**Phase 4: Strategy Development**
- Strategy creation
- Backtesting
- Optimization
- Forward testing
- Performance evaluation

**Phase 5: Advanced Topics**
- Options strategies
- Portfolio management
- Automated trading
- Risk modeling
- Professional trading

**Interactive Learning Components:**

**1. Conceptual Understanding:**
- Simple explanations
- Real-world examples
- Visual aids
- Interactive exercises
- Self-assessment quizzes

**2. Practical Application:**
- Paper trading exercises
- Case studies
- Simulation games
- Strategy building
- Performance tracking

**3. Skill Development:**
- Analysis techniques
- Decision making
- Emotional control
- Risk assessment
- Continuous improvement

**4. Knowledge Assessment:**
- Progressive difficulty
- Practical tests
- Real-world scenarios
- Peer review
- Expert feedback

**Learning Resources:**

**Recommended Materials:**
- Books and publications
- Video courses
- Webinars
- Research papers
- Expert interviews

**Tools and Platforms:**
- Charting software
- Data providers
- Backtesting platforms
- Trading simulators
- News feeds

**Community Engagement:**
- Study groups
- Mentorship programs
- Discussion forums
- Trading communities
- Expert networks

**Performance Tracking:**
- Learning progress
- Skill assessment
- Knowledge retention
- Application success
- Continuous feedback

Customize the learning path based on individual needs, progress tracking, and goal achievement metrics.""",
            variables={
                "knowledge_level": "Boshlang'ich, o'rta, yoki ilg'or",
                "experience_years": "Trading tajribasi (yil)",
                "learning_goals": "O'rganish maqsadlari",
                "study_time": "O'rganish uchun vaqt",
                "learning_style": "Visual, auditory, kinesthetic"
            },
            examples=[
                "Beginner to intermediate trading course",
                "Advanced technical analysis masterclass"
            ],
            best_practices=[
                "Progressive learning",
                "Interactive engagement",
                "Practical application"
            ],
            success_criteria=[
                "Clear knowledge progression",
                "Practical skill development",
                "Measurable improvement"
            ],
            target_audience="Barcha darajadagi traderlar",
            complexity_level="beginner"
        )

        # PERFORMANCE ANALYSIS TEMPLATES
        self.templates["performance_review"] = Template(
            id="performance_review",
            category=PromptCategory.PERFORMANCE_ANALYSIS,
            template_type=TemplateType.ANALYTICAL,
            name="Performance Review & Analysis",
            description="Comprehensive trading performance analysis",
            base_prompt=""""**TRADING PERFORMANS TAHLILI**

**Performance Period:**
- Review period: {review_period}
- Analysis date: {analysis_date}
- Trading capital: {trading_capital}
- Benchmark: {benchmark}
- Account type: {account_type}

**Performance Metrics Analysis:**

**1. Returns Analysis:**
- Total return: {total_return}%
- Annualized return: {annualized_return}%
- Monthly returns: {monthly_returns}
- Best performing month: {best_month}
- Worst performing month: {worst_month}
- Positive months: {positive_months}
- Negative months: {negative_months}

**2. Risk Metrics:**
- Maximum drawdown: {max_drawdown}%
- Average drawdown: {avg_drawdown}%
- Drawdown duration: {dd_duration}
- Volatility: {volatility}%
- VaR (95%): {var_95}%
- CVaR: {cvar}%

**3. Risk-Adjusted Returns:**
- Sharpe ratio: {sharpe_ratio}
- Sortino ratio: {sortino_ratio}
- Calmar ratio: {calmar_ratio}
- Information ratio: {information_ratio}
- Treynor ratio: {treynor_ratio}

**4. Trading Statistics:**
- Total trades: {total_trades}
- Winning trades: {winning_trades}
- Losing trades: {losing_trades}
- Win rate: {win_rate}%
- Average win: {avg_win}%
- Average loss: {avg_loss}%
- Profit factor: {profit_factor}
- Largest win: {largest_win}%
- Largest loss: {largest_loss}%

**5. Strategy Performance:**
- Best strategy: {best_strategy}
- Worst strategy: {worst_strategy}
- Strategy correlation: {strategy_correlation}
- Strategy contribution: {strategy_contribution}

**6. Time Analysis:**
- Best trading day: {best_day}
- Worst trading day: {worst_day}
- Best trading hour: {best_hour}
- Seasonal performance: {seasonal_performance}

**Performance Attribution:**

**What's Working:**
- Profitable strategies
- Strong entries
- Good risk management
- Successful timing
- Effective tools

**What Needs Improvement:**
- Underperforming areas
- Risk management gaps
- Entry/exit issues
- Strategy weaknesses
- Behavioral biases

**Benchmark Comparison:**
- vs. Market return
- Risk-adjusted comparison
- Style analysis
- Peer comparison
- Consistency metrics

**Improvement Recommendations:**

**Short-term Actions:**
- Immediate risk adjustments
- Strategy refinements
- Process improvements
- Tool upgrades
- Education focus

**Long-term Strategy:**
- Portfolio rebalancing
- Strategy diversification
- Risk model updates
- Performance targets
- System enhancements

**Action Plan:**
- Specific improvement steps
- Timeline and milestones
- Resource requirements
- Success metrics
- Review schedule

Provide data-driven insights, specific recommendations, and measurable improvement targets.""",
            variables={
                "review_period": "Tahlil davri (1 oy, 3 oy, 1 yil)",
                "analysis_date": "Tahlil sanasi",
                "trading_capital": "Joriy trading kapitali",
                "benchmark": "Benchmark index",
                "account_type": "Hisob turi (individual, IRA, corporate)",
                "total_return": "Umumiy return (%)",
                "annualized_return": "Yillik return (%)",
                "monthly_returns": "Oylik returns",
                "best_month": "Eng yaxshi oy",
                "worst_month": "Eng yomon oy",
                "positive_months": "Musbat oylar soni",
                "negative_months": "Manfiy oylar soni",
                "max_drawdown": "Maksimal drawdown (%)",
                "avg_drawdown": "O'rtacha drawdown (%)",
                "dd_duration": "Drawdown davomiyligi",
                "volatility": "Volatillik (%)",
                "var_95": "95% VaR (%)",
                "cvar": "Conditional VaR (%)",
                "sharpe_ratio": "Sharpe ratio",
                "sortino_ratio": "Sortino ratio",
                "calmar_ratio": "Calmar ratio",
                "information_ratio": "Information ratio",
                "treynor_ratio": "Treynor ratio",
                "total_trades": "Umumiy trade soni",
                "winning_trades": "Yutuqli trade soni",
                "losing_trades": "Yo'qotishli trade soni",
                "win_rate": "Win rate (%)",
                "avg_win": "O'rtacha yutuq (%)",
                "avg_loss": "O'rtacha yo'qotish (%)",
                "profit_factor": "Profit factor",
                "largest_win": "Eng katta yutuq (%)",
                "largest_loss": "Eng katta yo'qotish (%)",
                "best_strategy": "Eng yaxshi strategiya",
                "worst_strategy": "Eng yomon strategiya",
                "strategy_correlation": "Strategy correlation",
                "strategy_contribution": "Strategy contribution",
                "best_day": "Eng yaxshi kun",
                "worst_day": "Eng yomon kun",
                "best_hour": "Eng yaxshi soat",
                "seasonal_performance": "Seasonal performance"
            },
            examples=[
                "Monthly performance review for swing trader",
                "Annual portfolio performance analysis"
            ],
            best_practices=[
                "Multi-dimensional analysis",
                "Benchmark comparison",
                "Actionable insights"
            ],
            success_criteria=[
                "Comprehensive metrics",
                "Clear improvement areas",
                "Measurable targets"
            ],
            target_audience="Portfolio managers va individual treyderlar",
            complexity_level="intermediate"
        )

        # TRADING PSYCHOLOGY TEMPLATES
        self.templates["psychology_coaching"] = Template(
            id="psychology_coaching",
            category=PromptCategory.TRADING_PSYCHOLOGY,
            template_type=TemplateType.CONVERSATIONAL,
            name="Trading Psychology Coaching",
            description="Psychology coaching and mental training for traders",
            base_prompt=""""**TRADING PSIXOLOGIYA KO'CHATUVI**

**Trader Profile:**
- Experience level: {experience_level}
- Trading challenges: {challenges}
- Emotional patterns: {emotional_patterns}
- Stress level: {stress_level}
- Goals: {psychological_goals}

**Psychology Assessment Areas:**

**1. Emotional Intelligence:**
- Self-awareness
- Emotional regulation
- Empathy and social awareness
- Relationship management
- Stress tolerance

**2. Cognitive Biases:**
- Overconfidence bias
- Confirmation bias
- Loss aversion
- Anchoring bias
- Herding behavior

**3. Mental Resilience:**
- Stress management
- Recovery from losses
- Maintaining focus
- Decision-making under pressure
- Confidence building

**4. Behavioral Patterns:**
- Trading discipline
- Risk management consistency
- Pre-trade preparation
- Post-trade review
- Learning from mistakes

**Psychology Coaching Framework:**

**Mindset Development:**
- Growth mindset cultivation
- Success visualization
- Goal setting and achievement
- Positive self-talk
- Mental rehearsal

**Emotional Regulation Techniques:**
- Breathing exercises
- Meditation practices
- Visualization methods
- Stress reduction techniques
- Confidence building

**Decision-Making Process:**
- Systematic approach
- Emotional filter application
- Risk assessment protocols
- Information processing
- Time management

**Behavioral Interventions:**

**1. Pre-Market Routine:**
- Mental preparation
- Focus enhancement
- Risk awareness
- Goal setting
- Strategy review

**2. During Trading:**
- Emotional monitoring
- Decision validation
- Risk management
- Performance tracking
- Adjustment protocols

**3. Post-Market Review:**
- Emotional assessment
- Performance analysis
- Lesson identification
- Improvement planning
- Stress recovery

**Common Psychology Issues & Solutions:**

**FOMO (Fear of Missing Out):**
- Symptoms identification
- Trigger awareness
- Counter-strategies
- Practice exercises
- Peer support

**Revenge Trading:**
- Early warning signs
- Stop mechanisms
- Recovery protocols
- Prevention strategies
- Reflection techniques

**Overconfidence:**
- Reality check methods
- Performance tracking
- Humility building
- Learning mindset
- Mentor feedback

**Loss Aversion:**
- Bias recognition
- Risk adjustment
- Perspective shift
- Recovery planning
- Emotional healing

**Stress Management Tools:**

**Quick Techniques:**
- 4-7-8 breathing
- Progressive muscle relaxation
- Positive affirmations
- Grounding exercises
- Visualization

**Long-term Strategies:**
- Regular exercise
- Adequate sleep
- Nutrition optimization
- Social support
- Professional help

**Progress Tracking:**
- Weekly emotional check-ins
- Monthly performance reviews
- Quarterly psychology assessments
- Annual goal setting
- Continuous improvement

Create a personalized psychology coaching plan based on individual needs, challenges, and goals.""",
            variables={
                "experience_level": "Tajriba darajasi",
                "challenges": "Trading qiyinchiliklari",
                "emotional_patterns": "Emotsional patternlar",
                "stress_level": "Stress darajasi",
                "psychological_goals": "Psixologik maqsadlar"
            },
            examples=[
                "Beginner psychology coaching",
                "Professional trader mental training"
            ],
            best_practices=[
                "Personalized approach",
                "Regular assessment",
                "Progressive improvement"
            ],
            success_criteria=[
                "Improved emotional control",
                "Better decision making",
                "Consistent performance"
            ],
            target_audience="Barcha darajadagi treyderlar",
            complexity_level="intermediate"
        )

        # PORTFOLIO MANAGEMENT TEMPLATES
        self.templates["portfolio_optimization"] = Template(
            id="portfolio_optimization",
            category=PromptCategory.PORTFOLIO_MANAGEMENT,
            template_type=TemplateType.STRUCTURED,
            name="Portfolio Optimization & Management",
            description="Comprehensive portfolio optimization and management",
            base_prompt=""""**PORTFEL OPTIMALLASHTIRISH VA BOSHQARUV**

**Current Portfolio:**
- Portfolio value: {portfolio_value}
- Asset allocation: {asset_allocation}
- Geographic exposure: {geographic_exp}
- Sector allocation: {sector_allocation}
- Risk profile: {risk_profile}
- Time horizon: {time_horizon}

**Optimization Objectives:**
- Return target: {return_target}%
- Risk tolerance: {risk_tolerance}%
- Income requirements: {income_req}%
- Liquidity needs: {liquidity_needs}
- ESG preferences: {esg_preferences}

**Portfolio Analysis Framework:**

**1. Current Portfolio Assessment:**
- Asset allocation efficiency
- Geographic diversification
- Sector diversification
- Currency exposure
- Correlation analysis
- Concentration risk

**2. Risk Analysis:**
- Portfolio volatility
- Value at Risk (VaR)
- Maximum drawdown
- Tail risk assessment
- Stress testing
- Scenario analysis

**3. Performance Analysis:**
- Risk-adjusted returns
- Benchmark comparison
- Attribution analysis
- Factor exposure
- Performance persistence
- Market timing

**4. Optimization Recommendations:**

**Rebalancing Strategy:**
- Target allocation weights
- Rebalancing frequency
- Transaction cost consideration
- Tax implications
- Market timing

**Asset Allocation:**
- Strategic allocation
- Tactical adjustments
- Dynamic rebalancing
- Risk parity approach
- Core-satellite approach

**Security Selection:**
- Individual security analysis
- Quality assessment
- Growth vs. value tilt
- Factor exposure
- ESG integration

**Risk Management:**
- Position limits
- Correlation monitoring
- Tail risk hedging
- Currency hedging
- Liquidity management

**5. Alternative Strategies:**

**Conservative Approach:**
- Lower volatility target
- Income generation focus
- Capital preservation
- Defensive positioning
- Quality emphasis

**Aggressive Approach:**
- Higher return target
- Growth orientation
- Higher volatility tolerance
- Dynamic positioning
- Performance focus

**Balanced Approach:**
- Moderate return target
- Balanced risk-return
- Diversified approach
- Income and growth
- Long-term focus

**Implementation Plan:**

**Phase 1: Current State Analysis**
- Portfolio audit
- Performance attribution
- Risk assessment
- Cost analysis
- Benchmark comparison

**Phase 2: Optimization**
- Target allocation design
- Security selection
- Rebalancing strategy
- Risk management setup
- Monitoring framework

**Phase 3: Implementation**
- Transaction execution
- Cost management
- Tax optimization
- Performance monitoring
- Regular review

**Phase 4: Ongoing Management**
- Periodic rebalancing
- Performance review
- Strategy adjustment
- Risk monitoring
- Goal alignment

**Performance Monitoring:**
- Monthly reporting
- Quarterly review
- Annual rebalancing
- Performance attribution
- Risk assessment

**Risk Management:**
- Position limits
- Correlation monitoring
- VaR limits
- Drawdown protection
- Stress testing

Provide specific recommendations with quantitative targets, implementation timeline, and monitoring protocols.""",
            variables={
                "portfolio_value": "Joriy portfel qiymati",
                "asset_allocation": "Joriy asset allocation",
                "geographic_exp": "Geographic exposure",
                "sector_allocation": "Sector allocation",
                "risk_profile": "Risk profili",
                "time_horizon": "Investment muddati",
                "return_target": "Return maqsadi (%)",
                "risk_tolerance": "Risk tolerance (%)",
                "income_req": "Income talablari (%)",
                "liquidity_needs": "Likvidlik ehtiyojlari",
                "esg_preferences": "ESG preferences"
            },
            examples=[
                "Retirement portfolio optimization",
                "Growth-oriented portfolio rebalancing"
            ],
            best_practices=[
                "Quantified targets",
                "Risk-adjusted approach",
                "Regular monitoring"
            ],
            success_criteria=[
                "Optimal risk-return profile",
                "Efficient implementation",
                "Clear monitoring"
            ],
            target_audience="Portfolio managers va individual investorlar",
            complexity_level="advanced"
        )

        # Build category mapping
        for template_id, template in self.templates.items():
            if template.category not in self.category_templates:
                self.category_templates[template.category] = []
            self.category_templates[template.category].append(template_id)
    
    def _setup_analytics(self):
        """Analytics sozlamalari"""
        for template_id in self.templates.keys():
            self.template_analytics[template_id] = {
                'usage_count': 0,
                'success_rate': 0.0,
                'avg_rating': 0.0,
                'last_used': None,
                'user_feedback': []
            }
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Shablon olish"""
        return self.templates.get(template_id)
    
    def get_templates_by_category(self, category: PromptCategory) -> List[Template]:
        """Kategoriyaga ko'ra shablonlarni olish"""
        template_ids = self.category_templates.get(category, [])
        return [self.templates[tid] for tid in template_ids]
    
    def get_templates_by_complexity(self, complexity_level: str) -> List[Template]:
        """Murakkablik darajasiga ko'ra shablonlarni olish"""
        return [t for t in self.templates.values() if t.complexity_level == complexity_level]
    
    def get_templates_by_audience(self, target_audience: str) -> List[Template]:
        """Auditoriyaga ko'ra shablonlarni olish"""
        return [t for t in self.templates.values() if target_audience.lower() in t.target_audience.lower()]
    
    def search_templates(self, query: str) -> List[Template]:
        """Shablonlarni qidirish"""
        query = query.lower()
        results = []
        
        for template in self.templates.values():
            if (query in template.name.lower() or 
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags or [])):
                results.append(template)
        
        return results
    
    def get_template_variables(self, template_id: str) -> Dict[str, str]:
        """Shablon o'zgaruvchilarini olish"""
        template = self.get_template(template_id)
        return template.variables if template else {}
    
    def fill_template(self, template_id: str, variables: Dict[str, Any]) -> str:
        """Shablonni o'zgaruvchilar bilan to'ldirish"""
        template = self.get_template(template_id)
        if not template:
            return ""
        
        try:
            filled_prompt = template.base_prompt
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                if placeholder in filled_prompt:
                    filled_prompt = filled_prompt.replace(placeholder, str(value))
            
            return filled_prompt
        except Exception as e:
            logger.error(f"Error filling template {template_id}: {str(e)}")
            return template.base_prompt
    
    def get_recommended_templates(self, user_profile: Dict[str, Any]) -> List[Template]:
        """Foydalanuvchi profili bo'yicha tavsiya qilingan shablonlar"""
        recommendations = []
        user_level = user_profile.get('experience_level', 'intermediate')
        user_interests = user_profile.get('interests', [])
        
        for template in self.templates.values():
            score = 0
            
            # Experience level matching
            if (user_level == 'beginner' and template.complexity_level == 'beginner') or \
               (user_level == 'advanced' and template.complexity_level == 'advanced') or \
               (user_level == 'intermediate'):
                score += 1
            
            # Interest matching
            if user_interests:
                template_tags = set(template.tags or [])
                user_interests_set = set(user_interests)
                if template_tags.intersection(user_interests_set):
                    score += 2
            
            # Category preference
            preferred_categories = user_profile.get('preferred_categories', [])
            if template.category.value in preferred_categories:
                score += 1
            
            if score > 0:
                recommendations.append((template, score))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [template for template, score in recommendations]
    
    def update_template_usage(self, template_id: str, success: bool, rating: float = None):
        """Shablon foydalanish statistikasini yangilash"""
        if template_id not in self.template_analytics:
            return
        
        analytics = self.template_analytics[template_id]
        analytics['usage_count'] += 1
        analytics['last_used'] = datetime.now()
        
        if success:
            # Update success rate (simple average)
            current_rate = analytics['success_rate']
            new_rate = (current_rate * (analytics['usage_count'] - 1) + 1) / analytics['usage_count']
            analytics['success_rate'] = new_rate
        
        if rating is not None:
            analytics['user_feedback'].append(rating)
            analytics['avg_rating'] = sum(analytics['user_feedback']) / len(analytics['user_feedback'])
    
    def get_template_performance(self, template_id: str) -> Dict[str, Any]:
        """Shablon ishlamasini olish"""
        template = self.get_template(template_id)
        if not template:
            return {}
        
        analytics = self.template_analytics.get(template_id, {})
        template_data = {
            'template_info': {
                'id': template.id,
                'name': template.name,
                'category': template.category.value,
                'complexity': template.complexity_level,
                'target_audience': template.target_audience
            },
            'performance_metrics': {
                'usage_count': analytics.get('usage_count', 0),
                'success_rate': analytics.get('success_rate', 0.0),
                'avg_rating': analytics.get('avg_rating', 0.0),
                'last_used': analytics.get('last_used'),
                'feedback_count': len(analytics.get('user_feedback', []))
            }
        }
        
        return template_data
    
    def get_all_categories(self) -> List[PromptCategory]:
        """Barcha kategoriyalarni olish"""
        return list(PromptCategory)
    
    def get_category_stats(self) -> Dict[str, Dict[str, Any]]:
        """Kategoriya statistikasi"""
        stats = {}
        
        for category in PromptCategory:
            category_templates = self.get_templates_by_category(category)
            
            usage_counts = []
            success_rates = []
            for template_id in category_templates:
                if template_id in self.template_analytics:
                    usage_counts.append(self.template_analytics[template_id]['usage_count'])
                    success_rates.append(self.template_analytics[template_id]['success_rate'])
            
            stats[category.value] = {
                'template_count': len(category_templates),
                'total_usage': sum(usage_counts),
                'avg_success_rate': sum(success_rates) / len(success_rates) if success_rates else 0,
                'popular_templates': sorted(
                    [(tid, self.template_analytics[tid]['usage_count']) 
                     for tid in [t.id for t in category_templates] 
                     if tid in self.template_analytics],
                    key=lambda x: x[1], 
                    reverse=True
                )[:3]
            }
        
        return stats
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Umumiy analytics xulosasi"""
        total_templates = len(self.templates)
        total_usage = sum(analytics['usage_count'] for analytics in self.template_analytics.values())
        
        success_rates = [analytics['success_rate'] for analytics in self.template_analytics.values() if analytics['usage_count'] > 0]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
        
        # Most popular templates
        popular_templates = sorted(
            [(tid, self.template_analytics[tid]['usage_count']) 
             for tid in self.template_analytics],
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            'total_templates': total_templates,
            'total_usage': total_usage,
            'average_success_rate': avg_success_rate,
            'most_popular_templates': popular_templates,
            'category_distribution': self.get_category_stats(),
            'template_complexity': {
                'beginner': len([t for t in self.templates.values() if t.complexity_level == 'beginner']),
                'intermediate': len([t for t in self.templates.values() if t.complexity_level == 'intermediate']),
                'advanced': len([t for t in self.templates.values() if t.complexity_level == 'advanced'])
            }
        }
    
    # ===============================
    # ADVANCED PROMPT ENGINEERING FEATURES
    # ===============================
    
    def generate_context_aware_prompt(self, 
                                    template_id: str, 
                                    context: Dict[str, Any],
                                    user_profile: Dict[str, Any],
                                    conversation_history: List[Dict[str, Any]] = None) -> str:
        """Generate context-aware prompt with conversation history and user profile"""
        
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Get base template
        base_prompt = template.base_prompt
        
        # Apply user profile adaptations
        adapted_prompt = self._apply_user_profile_adaptations(base_prompt, user_profile, template)
        
        # Add conversation context
        if conversation_history and template.conversation_flow:
            conversation_context = self._build_conversation_context(conversation_history, template)
            adapted_prompt = f"{conversation_context}\n\n{adapted_prompt}"
        
        # Add market context
        market_context = self._build_market_context(context)
        adapted_prompt = adapted_prompt.format(**{**context, **market_context})
        
        # Add safety guidelines
        if template.safety_guidelines:
            safety_section = self._build_safety_section(template.safety_guidelines, context)
            adapted_prompt = f"{adapted_prompt}\n\n**XAVFSIZLIK QOIDALARI:**\n{safety_section}"
        
        # Add regulatory compliance
        if template.regulatory_notes:
            compliance_section = self._build_compliance_section(template.regulatory_notes)
            adapted_prompt = f"{adapted_prompt}\n\n**REGULATOR TALABLAR:**\n{compliance_section}"
        
        return adapted_prompt
    
    def _apply_user_profile_adaptations(self, prompt: str, user_profile: Dict[str, Any], template: Template) -> str:
        """Apply user profile adaptations to prompt"""
        
        skill_level = user_profile.get('skill_level', 'intermediate')
        language = user_profile.get('preferred_language', template.language)
        experience = user_profile.get('trading_experience', '1-2 years')
        
        # Adjust complexity based on user skill
        if skill_level == SkillLevel.BEGINNER.value and template.skill_level != SkillLevel.BEGINNER:
            prompt = f"**Boshlang'ich traderlar uchun moslashtirilgan:**\n{prompt}"
            prompt += "\n\nIltimos, tushuntirishlarni sodda tilda va amaliy misollar bilan bering."
        elif skill_level == SkillLevel.EXPERT.value and template.skill_level != SkillLevel.EXPERT:
            prompt = f"**Tajribali treyderlar uchun chuqurlashtirilgan:**\n{prompt}"
            prompt += "\n\nQuantitative analysis va institutional insights qo'shing."
        
        # Language adaptation
        if language != template.language:
            prompt = f"**Til: {language.title()}**\n{prompt}"
        
        return prompt
    
    def _build_conversation_context(self, conversation_history: List[Dict[str, Any]], template: Template) -> str:
        """Build conversation context for multi-turn interactions"""
        
        if not conversation_history:
            return ""
        
        context_parts = ["**OLDINKI SUHBAT KONTEKSTI:**"]
        
        # Add recent conversation history (last 3 exchanges)
        recent_history = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
        
        for i, exchange in enumerate(recent_history, 1):
            user_msg = exchange.get('user', '')
            assistant_msg = exchange.get('assistant', '')
            
            context_parts.append(f"{i}. Foydalanuvchi: {user_msg}")
            if assistant_msg:
                context_parts.append(f"   AI: {assistant_msg}")
        
        return "\n".join(context_parts)
    
    def _build_market_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build additional market context"""
        
        market_context = {}
        
        # Add time-based context
        current_time = datetime.now(timezone.utc)
        market_context['current_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Add market session info (simplified)
        hour = current_time.hour
        if 8 <= hour <= 16:
            market_context['market_session'] = "London Session"
        elif 13 <= hour <= 22:
            market_context['market_session'] = "New York Session"
        elif 0 <= hour <= 8:
            market_context['market_session'] = "Asian Session"
        else:
            market_context['market_session'] = "Off-hours"
        
        # Add volatility indicator
        market_context['volatility_environment'] = "Normal"  # Can be enhanced with real data
        
        return market_context
    
    def _build_safety_section(self, safety_guidelines: List[str], context: Dict[str, Any]) -> str:
        """Build safety guidelines section"""
        
        safety_parts = []
        for guideline in safety_guidelines:
            safety_parts.append(f"• {guideline}")
        
        # Add dynamic safety alerts based on context
        symbol = context.get('symbol', '')
        if symbol in ['BTC', 'ETH', 'CRYPTO']:
            safety_parts.append("• Cryptocurrency narxlari yuqori volatilga ega")
        
        return "\n".join(safety_parts)
    
    def _build_compliance_section(self, regulatory_notes: List[str]) -> str:
        """Build regulatory compliance section"""
        
        compliance_parts = []
        for note in regulatory_notes:
            compliance_parts.append(f"• {note}")
        
        return "\n".join(compliance_parts)
    
    def create_ab_test_variants(self, template_id: str, 
                               base_context: Dict[str, Any],
                               test_variants: List[str]) -> Dict[str, str]:
        """Create A/B test variants for prompt optimization"""
        
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        variants = {}
        
        for i, variant_name in enumerate(test_variants):
            # Create variant-specific context
            variant_context = base_context.copy()
            variant_context['test_variant'] = variant_name
            
            # Generate variant prompt
            if variant_name == 'simplified':
                # Simplified version
                variant_prompt = self._create_simplified_prompt(template, variant_context)
            elif variant_name == 'detailed':
                # Detailed version
                variant_prompt = self._create_detailed_prompt(template, variant_context)
            elif variant_name == 'conversational':
                # Conversational version
                variant_prompt = self._create_conversational_prompt(template, variant_context)
            else:
                # Default variant
                variant_prompt = self.generate_context_aware_prompt(template_id, variant_context, {})
            
            variants[variant_name] = variant_prompt
        
        return variants
    
    def _create_simplified_prompt(self, template: Template, context: Dict[str, Any]) -> str:
        """Create simplified version of prompt"""
        simplified = template.base_prompt
        
        # Remove complex sections and jargon
        simplified = re.sub(r'\*\*[^*]+\*\*:', '', simplified)  # Remove headers
        simplified = re.sub(r'\d+\.', '', simplified)  # Remove numbered lists
        simplified = re.sub(r'[-•]\s+', '', simplified)  # Remove bullet points
        
        return simplified.format(**context)
    
    def _create_detailed_prompt(self, template: Template, context: Dict[str, Any]) -> str:
        """Create detailed version of prompt"""
        detailed = template.base_prompt
        
        # Add additional analysis sections
        additional_sections = [
            "\n**Qo'shimcha tahlil:**",
            "• Historical pattern analysis",
            "• Market correlation study", 
            "• Volume profile analysis",
            "• Risk assessment matrix"
        ]
        
        detailed += "\n".join(additional_sections)
        return detailed.format(**context)
    
    def _create_conversational_prompt(self, template: Template, context: Dict[str, Any]) -> str:
        """Create conversational version of prompt"""
        conversational = template.base_prompt
        
        # Convert to more conversational tone
        conversational = conversational.replace('Iltimos', 'Siz')
        conversational = conversational.replace('tahlil qiling', 'tahlil qilasizmi')
        
        return conversational.format(**context)
    
    def optimize_prompt_performance(self, template_id: str, 
                                  performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically optimize prompt based on performance data"""
        
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        optimization_results = {
            'template_id': template_id,
            'optimization_date': datetime.now(timezone.utc).isoformat(),
            'changes_made': [],
            'expected_improvement': 0.0
        }
        
        # Analyze performance data
        success_rate = performance_data.get('success_rate', 0.0)
        user_rating = performance_data.get('user_rating', 0.0)
        completion_time = performance_data.get('avg_completion_time', 0.0)
        
        # Optimization rules
        if success_rate < 0.7:
            # Low success rate - make prompt more clear
            template.base_prompt = self._clarify_prompt(template.base_prompt)
            optimization_results['changes_made'].append('Added clarity improvements')
            optimization_results['expected_improvement'] += 0.15
        
        if user_rating < 4.0:
            # Low user rating - improve explanations
            template.base_prompt = self._enhance_explanations(template.base_prompt)
            optimization_results['changes_made'].append('Enhanced explanations')
            optimization_results['expected_improvement'] += 0.1
        
        if completion_time > 300:  # 5 minutes
            # Too slow - simplify language
            template.base_prompt = self._simplify_language(template.base_prompt)
            optimization_results['changes_made'].append('Simplified language')
            optimization_results['expected_improvement'] += 0.05
        
        # Update template metadata
        template.last_optimized = datetime.now(timezone.utc)
        template.optimization_history.append(optimization_results)
        template.quality_score = (success_rate + user_rating/5.0) / 2.0
        
        return optimization_results
    
    def _clarify_prompt(self, prompt: str) -> str:
        """Clarify prompt for better understanding"""
        clarifications = [
            "\n**Tushuntirish uchun qo'shimcha ko'rsatma:**",
            "• Har bir qadamni aniq tushuntiring",
            "• Texnik terminlarni sodda tilda izohlang",
            "• Amaliy misollar keltiring"
        ]
        return prompt + "\n".join(clarifications)
    
    def _enhance_explanations(self, prompt: str) -> str:
        """Enhance explanations in prompt"""
        enhancements = [
            "\n**Chuqur tushuntirish uchun:**",
            "• Har bir xulosani asoslab bering",
            "• Alternativ senariylarni ko'rsating", 
            "• Risk omillarini aniq ta'riflang"
        ]
        return prompt + "\n".join(enhancements)
    
    def _simplify_language(self, prompt: str) -> str:
        """Simplify language in prompt"""
        simplifications = {
            'analiyq': 'tahlil',
            'qilishimiz': 'qilish',
            'kerak': 'zarur',
            'xulosa': 'yakun'
        }
        
        simplified = prompt
        for complex_word, simple_word in simplifications.items():
            simplified = simplified.replace(complex_word, simple_word)
        
        return simplified
    
    def validate_prompt_safety(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate prompt for safety and compliance"""
        
        safety_report = {
            'is_safe': True,
            'warnings': [],
            'compliance_issues': [],
            'recommendations': []
        }
        
        # Check for financial advice indicators
        financial_advice_indicators = [
            "sotib oling", "soting", "investitsiya qiling", "investitsiyangizni",
            "ma'lum summa", "aniq narx", "mutloq ishonch"
        ]
        
        for indicator in financial_advice_indicators:
            if indicator in prompt.lower():
                safety_report['warnings'].append(f"Financial advice indicator found: {indicator}")
                safety_report['is_safe'] = False
        
        # Check regulatory compliance
        regulatory_keywords = [
            "sertifikat", "ruxsat", "regulator", "qonun", "talab"
        ]
        
        has_compliance = any(keyword in prompt.lower() for keyword in regulatory_keywords)
        if not has_compliance:
            safety_report['compliance_issues'].append("No regulatory compliance mention found")
            safety_report['recommendations'].append("Add regulatory compliance statement")
        
        # Check risk warnings
        risk_warnings = ["xavf", "risk", "yo'qotish", "ehtimol"]
        has_risk_warning = any(warning in prompt.lower() for warning in risk_warnings)
        
        if not has_risk_warning:
            safety_report['warnings'].append("No risk warning found")
            safety_report['recommendations'].append("Add risk warning statement")
        
        return safety_report
    
    def get_template_analytics(self, template_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a template"""
        
        template = self.get_template(template_id)
        if not template:
            return {}
        
        analytics = self.template_analytics.get(template_id, {})
        
        # Performance trends
        performance_trends = {
            'usage_trend': 'increasing' if analytics.get('usage_count', 0) > 100 else 'stable',
            'success_trend': 'improving' if analytics.get('success_rate', 0) > 0.8 else 'stable',
            'user_satisfaction': analytics.get('avg_rating', 0.0)
        }
        
        # Template quality metrics
        quality_metrics = {
            'overall_score': template.quality_score,
            'optimization_count': len(template.optimization_history),
            'last_optimization': template.last_optimized.isoformat() if template.last_optimized else None,
            'multilingual_support': template.multi_language_support,
            'context_awareness': template.context_aware,
            'safety_level': 'high' if template.safety_enhanced else 'medium'
        }
        
        return {
            'template_info': {
                'id': template.id,
                'name': template.name,
                'category': template.category.value,
                'version': template.version,
                'created_date': template.created_date.isoformat()
            },
            'usage_analytics': {
                'total_uses': analytics.get('usage_count', 0),
                'success_rate': analytics.get('success_rate', 0.0),
                'avg_rating': analytics.get('avg_rating', 0.0),
                'last_used': analytics.get('last_used', {}).isoformat() if analytics.get('last_used') else None
            },
            'performance_trends': performance_trends,
            'quality_metrics': quality_metrics,
            'ab_test_data': {
                'variants_tested': len(template.ab_test_variants),
                'best_variant': 'control',  # Simplified for now
                'improvement_achieved': 0.0
            }
        }

# Template examples and utilities
class TemplateExamples:
    """Template foydalanish namunalari"""
    
    @staticmethod
    def get_quick_start_templates() -> List[Dict[str, str]]:
        """Tezkor boshlanish uchun shablonlar"""
        return [
            {
                'name': 'Texnik Tahlil',
                'description': 'Aktivlar uchun tez texnik tahlil',
                'template_id': 'tech_analysis_basic'
            },
            {
                'name': 'Xavf Baholash',
                'description': 'Portfolio xavfini baholash',
                'template_id': 'risk_assessment'
            },
            {
                'name': 'Performance Tahlil',
                'description': 'Trading natijalarini tahlil qilish',
                'template_id': 'performance_review'
            }
        ]
    
    @staticmethod
    def get_advanced_templates() -> List[Dict[str, str]]:
        """Ilg'or foydalanish uchun shablonlar"""
        return [
            {
                'name': 'Chuqur Texnik Tahlil',
                'description': 'Professional darajadagi texnik tahlil',
                'template_id': 'tech_analysis_advanced'
            },
            {
                'name': 'Strategy Framework',
                'description': 'Trading strategiyasini ishlab chiqish',
                'template_id': 'strategy_framework'
            },
            {
                'name': 'Portfolio Optimization',
                'description': 'Portfel optimallashtirish',
                'template_id': 'portfolio_optimization'
            }
        ]
    
    @staticmethod
    def get_learning_templates() -> List[Dict[str, str]]:
        """O'rganish uchun shablonlar"""
        return [
            {
                'name': 'Trading Ta\'lim',
                'description': 'Trading bilimlarini o\'rganish',
                'template_id': 'trading_education'
            },
            {
                'name': 'Psixologiya Coaching',
                'description': 'Trading psixologiyasi',
                'template_id': 'psychology_coaching'
            }
        ]

# Usage example
if __name__ == "__main__":
    # Initialize template manager
    manager = TemplateManager()
    
    # Get all categories
    print("Available categories:")
    for category in manager.get_all_categories():
        print(f"- {category.value}")
    
    # Get templates for technical analysis
    tech_templates = manager.get_templates_by_category(PromptCategory.TECHNICAL_ANALYSIS)
    print(f"\nTechnical Analysis templates: {len(tech_templates)}")
    
    # Fill a template
    variables = {
        'asset': 'EUR/USD',
        'timeframe': '1d',
        'analysis_date': '2025-01-15'
    }
    
    filled_prompt = manager.fill_template('tech_analysis_basic', variables)
    print(f"\nFilled template preview:")
    print(filled_prompt[:200] + "...")
    
    # Get analytics
    analytics = manager.get_analytics_summary()
    print(f"\nTemplate Analytics:")
    print(f"Total templates: {analytics['total_templates']}")
    print(f"Total usage: {analytics['total_usage']}")
