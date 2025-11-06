"""
Economic Adaptation System Demo Dasturi

Ushbu demo dastur Economic Adaptation tizimining barcha asosiy xususiyatlarini
real ma'lumotlar va misollar bilan namoyish qiladi.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging
import warnings

# Economic Adaptation tizimi modullarini import qilish
from . import (
    EconomicCycleAnalyzer,
    SystemIntegration,
    AdaptationStrategy,
    CyclePhase,
    TimeScale
)
from .config import config, get_config
from .core.cycle_detector import CycleDetector
from .core.indicators import EconomicIndicatorAnalyzer
from .core.adaptation_engine import MacroEconomicAdaptationEngine
from .core.learning_system import ComprehensiveLearningSystem
from .performance.performance_optimizer import PerformanceOptimizer

# Xabarlar va log qo'yinganlarni yoqish
logging.basicConfig(level=logging.INFO)
warnings.filterwarnings('ignore')

class EconomicAdaptationDemo:
    """
    Economic Adaptation tizimi demo klassi.
    """
    
    def __init__(self):
        """Demo klassini ishga tushirish."""
        print("=" * 80)
        print("🌍 ECONOMIC ADAPTATION SYSTEM DEMO DASTURI")
        print("=" * 80)
        
        # Konfiguratsiyani o'qish
        self.config = get_config()
        print(f"📋 Tizim konfiguratsiyasi yuklandi: {self.config.system_name} v{self.config.version}")
        
        # Ma'lumotlarni tayyorlash
        self._prepare_demo_data()
        
        # Komponentlarni inicializatsiya qilish
        self._initialize_components()
        
    def _prepare_demo_data(self):
        """Demo uchun ma'lumotlarni tayyorlash."""
        print("\n📊 Demo ma'lumotlari tayyorlanmoqda...")
        
        # 5 yillik GDP ma'lumotlari yaratish (oylik)
        dates = pd.date_range(start='2019-01-01', end='2024-01-01', freq='M')
        
        # Real GDP o'sish surati simulyatsiyasi (business cycle bilan)
        np.random.seed(42)
        base_growth = 0.02 / 12  # 2% yillik
        
        # Business cycle phases simulation
        cycle_data = []
        current_phase = 'expansion'
        phase_duration = 0
        
        for i, date in enumerate(dates):
            # Business cycle phase belgilash
            if phase_duration > np.random.randint(18, 36):  # 18-36 oy
                if current_phase == 'expansion':
                    current_phase = 'peak'
                    phase_duration = 0
                elif current_phase == 'peak':
                    current_phase = 'contraction'
                    phase_duration = 0
                elif current_phase == 'contraction':
                    current_phase = 'trough'
                    phase_duration = 0
                else:
                    current_phase = 'expansion'
                    phase_duration = 0
            
            phase_duration += 1
            
            # Har bir fazaga mos o'sish surati
            if current_phase == 'expansion':
                growth_rate = base_growth + np.random.normal(0.001, 0.002)
            elif current_phase == 'peak':
                growth_rate = base_growth + np.random.normal(0.0005, 0.0015)
            elif current_phase == 'contraction':
                growth_rate = -0.005 + np.random.normal(0, 0.002)
            else:  # trough
                growth_rate = base_growth + np.random.normal(-0.001, 0.002)
            
            cycle_data.append({
                'date': date,
                'gdp_growth': max(-0.05, min(0.05, growth_rate)),
                'cycle_phase': current_phase
            })
        
        self.cycle_data = pd.DataFrame(cycle_data)
        
        # Economic indicators ma'lumotlari
        indicators_data = []
        for _, row in self.cycle_data.iterrows():
            # Leading indicators (growth'dan oldin)
            yield_curve = max(-0.5, min(2.0, row['gdp_growth'] * 10 + np.random.normal(0, 0.1)))
            consumer_confidence = max(50, min(120, 100 + row['gdp_growth'] * 500 + np.random.normal(0, 5)))
            manufacturing_pmi = max(30, min(70, 50 + row['gdp_growth'] * 1000 + np.random.normal(0, 3)))
            
            # Coincident indicators
            unemployment_rate = max(3, min(10, 5 - row['gdp_growth'] * 200 + np.random.normal(0, 0.3)))
            industrial_production = max(-10, min(10, row['gdp_growth'] * 800 + np.random.normal(0, 2)))
            
            # Lagging indicators
            cpi = max(-2, min(8, row['gdp_growth'] * 300 + np.random.normal(0, 1)))
            corporate_profits = max(-20, min(20, row['gdp_growth'] * 1200 + np.random.normal(0, 5)))
            
            indicators_data.append({
                'date': row['date'],
                'yield_curve': yield_curve,
                'consumer_confidence': consumer_confidence,
                'manufacturing_pmi': manufacturing_pmi,
                'unemployment_rate': unemployment_rate,
                'industrial_production': industrial_production,
                'cpi': cpi,
                'corporate_profits': corporate_profits
            })
        
        self.indicators_data = pd.DataFrame(indicators_data)
        
        # Portfolio performance ma'lumotlari
        np.random.seed(123)
        portfolio_returns = []
        for _, row in self.cycle_data.iterrows():
            # Economic cycle'ga mos portfolio returns
            if row['cycle_phase'] == 'expansion':
                base_return = 0.008 + np.random.normal(0, 0.02)
            elif row['cycle_phase'] == 'peak':
                base_return = 0.003 + np.random.normal(0, 0.025)
            elif row['cycle_phase'] == 'contraction':
                base_return = -0.015 + np.random.normal(0, 0.04)
            else:  # trough
                base_return = 0.005 + np.random.normal(0, 0.03)
            
            portfolio_returns.append({
                'date': row['date'],
                'portfolio_return': max(-0.1, min(0.1, base_return)),
                'market_return': max(-0.1, min(0.1, base_return * 0.8 + np.random.normal(0, 0.015)))
            })
        
        self.portfolio_data = pd.DataFrame(portfolio_returns)
        
        print(f"✅ {len(self.cycle_data)} oylik ma'lumotlar tayyorlandi")
        print(f"✅ {len(self.indicators_data)} indicator ma'lumotlari")
        print(f"✅ {len(self.portfolio_data)} portfolio performance ma'lumotlari")
    
    def _initialize_components(self):
        """Tizim komponentlarini inicializatsiya qilish."""
        print("\n🔧 Tizim komponentlari inicializatsiya qilinmoqda...")
        
        # Economic Cycle Analyzer
        self.cycle_analyzer = EconomicCycleAnalyzer(self.config)
        print("✅ Economic Cycle Analyzer tayyor")
        
        # Economic Indicator Analyzer
        self.indicator_analyzer = EconomicIndicatorAnalyzer(self.config)
        print("✅ Economic Indicator Analyzer tayyor")
        
        # Macro-Economic Adaptation Engine
        self.adaptation_engine = MacroEconomicAdaptationEngine(self.config)
        print("✅ Macro-Economic Adaptation Engine tayyor")
        
        # Comprehensive Learning System
        self.learning_system = ComprehensiveLearningSystem(self.config)
        print("✅ Comprehensive Learning System tayyor")
        
        # Performance Optimizer
        self.performance_optimizer = PerformanceOptimizer(self.config)
        print("✅ Performance Optimizer tayyor")
        
        # System Integration
        self.system_integration = SystemIntegration(self.config)
        print("✅ System Integration tayyor")
        
        print("\n🎯 Barcha komponentlar tayyor!")
    
    def demo_cycle_detection(self):
        """Business cycle detection namoyishi."""
        print("\n" + "="*60)
        print("📈 1. BUSINESS CYCLE DETECTION DEMO")
        print("="*60)
        
        # GDP ma'lumotlaridan cycle phases aniqlash
        cycle_phases = self.cycle_analyzer.analyze_economic_cycle(
            self.indicators_data,
            self.cycle_data['gdp_growth'].values
        )
        
        print("\n🔍 Oxirgi 12 oydagi cycle fazalari:")
        recent_phases = cycle_phases[-12:]
        for i, (date, phase) in enumerate(zip(self.cycle_data['date'].iloc[-12:], recent_phases)):
            print(f"  {date.strftime('%Y-%m')}: {phase.value}")
        
        # Cycle statistics
        phase_counts = pd.Series([p.value for p in cycle_phases]).value_counts()
        print(f"\n📊 Cycle fazalari statistikasi:")
        for phase, count in phase_counts.items():
            percentage = (count / len(cycle_phases)) * 100
            print(f"  {phase}: {count} oy ({percentage:.1f}%)")
        
        # Turning points detection
        turning_points = self.cycle_analyzer.detect_cycle_turning_points(
            self.cycle_data['gdp_growth'].values
        )
        
        print(f"\n⚡ {len(turning_points)} ta turning point topildi")
        
        return cycle_phases
    
    def demo_indicator_analysis(self):
        """Economic indicators analysis namoyishi."""
        print("\n" + "="*60)
        print("📊 2. ECONOMIC INDICATORS ANALYSIS DEMO")
        print("="*60)
        
        # Leading indicators analysis
        leading_signals = self.indicator_analyzer.analyze_leading_indicators(
            self.indicators_data[['yield_curve', 'consumer_confidence', 'manufacturing_pmi']]
        )
        
        print("\n📈 Leading indicators signallar:")
        for indicator, signal in leading_signals.items():
            strength = signal['signal_strength']
            direction = signal['signal_direction']
            print(f"  {indicator}: {direction} (kuch: {strength:.3f})")
        
        # Composite leading indicator
        cli_score = self.indicator_analyzer.calculate_composite_leading_indicator()
        print(f"\n🎯 Composite Leading Indicator: {cli_score:.3f}")
        
        # Economic momentum analysis
        momentum_data = self.indicator_analyzer.analyze_economic_momentum(self.indicators_data)
        print(f"\n⚡ Economic momentum: {momentum_data['momentum_score']:.3f}")
        print(f"📊 Momentum trend: {momentum_data['momentum_trend']}")
        
        return leading_signals, momentum_data
    
    def demo_adaptation_strategies(self):
        """Macro-economic adaptation strategies namoyishi."""
        print("\n" + "="*60)
        print("🔄 3. MACRO-ECONOMIC ADAPTATION DEMO")
        print("="*60)
        
        # Current economic conditions
        current_indicators = {
            'interest_rate': 0.045,  # 4.5%
            'inflation_rate': 0.032,  # 3.2%
            'credit_growth': 0.08,   # 8%
            'gdp_growth': 0.018,     # 1.8%
            'unemployment_rate': 0.045  # 4.5%
        }
        
        # Adaptation strategies for different cycles
        strategies = ['conservative', 'moderate', 'aggressive']
        
        print("\n🎯 Har xil adaptation strategiyalar uchun tavsiyalar:")
        for strategy in strategies:
            adaptation = self.adaptation_engine.adapt_to_macro_cycle(
                current_indicators,
                AdaptationStrategy(strategy)
            )
            
            print(f"\n  📋 {strategy.upper()} Strategy:")
            print(f"    Risk Level: {adaptation['risk_level']}")
            print(f"    Position Sizing: {adaptation['position_sizing']}")
            print(f"    Sector Rotation: {adaptation['sector_recommendation']}")
            
            # Recommended adjustments
            if 'interest_rate_adjustment' in adaptation:
                print(f"    Interest Rate Adjustment: {adaptation['interest_rate_adjustment']}")
            if 'inflation_protection' in adaptation:
                print(f"    Inflation Protection: {adaptation['inflation_protection']}")
        
        # Policy cycle integration
        policy_impact = self.adaptation_engine.assess_policy_impact(current_indicators)
        print(f"\n🏛️  Policy Impact Score: {policy_impact['policy_score']:.3f}")
        print(f"📈 Policy Direction: {policy_impact['policy_direction']}")
        
        return strategies
    
    def demo_learning_system(self):
        """Self-learning system namoyishi."""
        print("\n" + "="*60)
        print("🧠 4. SELF-LEARNING SYSTEM DEMO")
        print("="*60)
        
        # Multi-scale learning demonstration
        print("\n🔍 Multi-scale Learning Analysis:")
        
        # Intraday-scale learning (simulate 5-minute data for last month)
        intraday_data = self._generate_intraday_data()
        intraday_learning = self.learning_system.learn_from_intraday_data(intraday_data)
        print(f"  📊 Intraday Learning: {intraday_learning['accuracy']:.3f}")
        
        # Daily-scale learning
        daily_data = self.cycle_data[['date', 'gdp_growth']].copy()
        daily_learning = self.learning_system.learn_from_daily_data(daily_data)
        print(f"  📈 Daily Learning: {daily_learning['accuracy']:.3f}")
        
        # Weekly-scale learning
        weekly_data = self._aggregate_to_weekly(daily_data)
        weekly_learning = self.learning_system.learn_from_weekly_data(weekly_data)
        print(f"  📅 Weekly Learning: {weekly_learning['accuracy']:.3f}")
        
        # Meta-learning insights
        meta_learning = self.learning_system.analyze_meta_learning_patterns()
        print(f"\n🎯 Meta-Learning Insights:")
        print(f"  📚 Knowledge Accumulation: {meta_learning['knowledge_score']:.3f}")
        print(f"  🔄 Adaptation Patterns: {len(meta_learning['patterns'])} ta topildi")
        print(f"  ⚡ Learning Efficiency: {meta_learning['efficiency']:.3f}")
        
        # Performance prediction
        performance_prediction = self.learning_system.predict_performance_outlook()
        print(f"\n🔮 Performance Prediction:")
        print(f"  📈 Expected Return: {performance_prediction['expected_return']:.3f}")
        print(f"  📊 Expected Volatility: {performance_prediction['expected_volatility']:.3f}")
        print(f"  🎯 Prediction Confidence: {performance_prediction['confidence']:.3f}")
        
        return intraday_learning, meta_learning, performance_prediction
    
    def demo_performance_optimization(self):
        """Performance optimization namoyishi."""
        print("\n" + "="*60)
        print("⚡ 5. PERFORMANCE OPTIMIZATION DEMO")
        print("="*60)
        
        # Portfolio performance analysis
        portfolio_returns = self.portfolio_data['portfolio_return'].values
        market_returns = self.portfolio_data['market_return'].values
        
        # Basic performance metrics
        basic_metrics = self.performance_optimizer.calculate_basic_metrics(
            portfolio_returns, market_returns
        )
        
        print("\n📊 Basic Performance Metrics:")
        print(f"  Total Return: {basic_metrics['total_return']:.3f}")
        print(f"  Annualized Return: {basic_metrics['annualized_return']:.3f}")
        print(f"  Volatility: {basic_metrics['volatility']:.3f}")
        print(f"  Sharpe Ratio: {basic_metrics['sharpe_ratio']:.3f}")
        print(f"  Max Drawdown: {basic_metrics['max_drawdown']:.3f}")
        
        # Cycle-adjusted metrics
        cycle_adjusted = self.performance_optimizer.calculate_cycle_adjusted_metrics(
            portfolio_returns, market_returns, self.cycle_data['cycle_phase'].values
        )
        
        print("\n🔄 Cycle-Adjusted Performance:")
        for phase, metrics in cycle_adjusted.items():
            print(f"  {phase.upper()}:")
            print(f"    Return: {metrics['return']:.3f}")
            print(f"    Sharpe: {metrics['sharpe']:.3f}")
            print(f"    Alpha: {metrics['alpha']:.3f}")
        
        # Performance attribution
        attribution = self.performance_optimizer.analyze_performance_attribution(
            portfolio_returns, market_returns, self.indicators_data
        )
        
        print("\n🎯 Performance Attribution:")
        for factor, contribution in attribution.items():
            print(f"  {factor}: {contribution:.3f}")
        
        # Benchmark comparison
        benchmark_analysis = self.performance_optimizer.compare_with_benchmarks(
            portfolio_returns, market_returns
        )
        
        print(f"\n📊 Benchmark Analysis:")
        print(f"  Information Ratio: {benchmark_analysis['information_ratio']:.3f}")
        print(f"  Tracking Error: {benchmark_analysis['tracking_error']:.3f}")
        print(f"  Beta: {benchmark_analysis['beta']:.3f}")
        
        return basic_metrics, cycle_adjusted, attribution
    
    def demo_system_integration(self):
        """System integration namoyishi."""
        print("\n" + "="*60)
        print("🔗 6. SYSTEM INTEGRATION DEMO")
        print("="*60)
        
        # Simulate integration with other modules
        integration_status = self.system_integration.check_integration_status()
        print("\n📡 Integration Status:")
        for module, status in integration_status.items():
            print(f"  {module}: {status}")
        
        # Real-time data pipeline simulation
        print("\n⚡ Real-time Data Processing:")
        real_time_data = self._simulate_real_time_data()
        pipeline_status = self.system_integration.process_real_time_data(real_time_data)
        print(f"  Processing Status: {pipeline_status['status']}")
        print(f"  Latency: {pipeline_status['latency_ms']}ms")
        print(f"  Throughput: {pipeline_status['throughput']} records/sec")
        
        # Market data integration
        print("\n📈 Market Data Integration:")
        market_data = self._simulate_market_data()
        data_quality = self.system_integration.integrate_market_data(market_data)
        print(f"  Data Quality Score: {data_quality['quality_score']:.3f}")
        print(f"  Completeness: {data_quality['completeness']:.1f}%")
        print(f"  Timeliness: {data_quality['timeliness']:.3f}")
        
        return integration_status, pipeline_status, data_quality
    
    def create_visualizations(self):
        """Demo natijalarini visualization qilish."""
        print("\n" + "="*60)
        print("📊 7. VISUALIZATION YARATISH")
        print("="*60)
        
        # Set up matplotlib
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('Economic Adaptation System Demo Results', fontsize=16)
        
        # 1. GDP Growth va Cycle Phases
        ax1 = axes[0, 0]
        ax1.plot(self.cycle_data['date'], self.cycle_data['gdp_growth'], 'b-', linewidth=2)
        cycle_colors = {'expansion': 'green', 'peak': 'orange', 'contraction': 'red', 'trough': 'blue'}
        
        for phase, color in cycle_colors.items():
            mask = self.cycle_data['cycle_phase'] == phase
            ax1.fill_between(self.cycle_data['date'], 0, self.cycle_data['gdp_growth'], 
                           where=mask, alpha=0.3, color=color, label=phase.title())
        
        ax1.set_title('GDP Growth va Business Cycle Phases')
        ax1.set_ylabel('GDP Growth Rate')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Leading Indicators
        ax2 = axes[0, 1]
        ax2.plot(self.indicators_data['date'], self.indicators_data['yield_curve'], 'g-', label='Yield Curve')
        ax2.plot(self.indicators_data['date'], self.indicators_data['consumer_confidence']/100, 'r-', label='Consumer Confidence (scaled)')
        ax2.set_title('Leading Economic Indicators')
        ax2.set_ylabel('Indicator Value')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Portfolio Performance
        ax3 = axes[1, 0]
        portfolio_cumret = (1 + self.portfolio_data['portfolio_return']).cumprod()
        market_cumret = (1 + self.portfolio_data['market_return']).cumprod()
        
        ax3.plot(self.portfolio_data['date'], portfolio_cumret, 'b-', linewidth=2, label='Portfolio')
        ax3.plot(self.portfolio_data['date'], market_cumret, 'r--', linewidth=2, label='Market')
        ax3.set_title('Portfolio Performance Comparison')
        ax3.set_ylabel('Cumulative Return')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Risk-Adjusted Returns by Cycle Phase
        ax4 = axes[1, 1]
        cycle_returns = []
        cycle_names = []
        
        for phase in self.cycle_data['cycle_phase'].unique():
            mask = self.cycle_data['cycle_phase'] == phase
            phase_returns = self.portfolio_data[mask]['portfolio_return'].values
            cycle_returns.append(phase_returns)
            cycle_names.append(phase.title())
        
        bp = ax4.boxplot(cycle_returns, labels=cycle_names, patch_artist=True)
        colors = ['lightgreen', 'lightblue', 'lightcoral', 'lightyellow']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax4.set_title('Risk-Adjusted Returns by Cycle Phase')
        ax4.set_ylabel('Monthly Return')
        ax4.grid(True, alpha=0.3)
        
        # 5. Economic Momentum
        ax5 = axes[2, 0]
        momentum_data = self.indicator_analyzer.analyze_economic_momentum(self.indicators_data)
        # Simulate momentum time series
        momentum_series = np.random.normal(0, 0.1, len(self.indicators_data))
        momentum_series = np.cumsum(momentum_series) * 0.1
        
        ax5.plot(self.indicators_data['date'], momentum_series, 'purple', linewidth=2)
        ax5.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax5.fill_between(self.indicators_data['date'], momentum_series, 0, 
                        where=(momentum_series > 0), alpha=0.3, color='green', label='Positive Momentum')
        ax5.fill_between(self.indicators_data['date'], momentum_series, 0, 
                        where=(momentum_series < 0), alpha=0.3, color='red', label='Negative Momentum')
        
        ax5.set_title('Economic Momentum Indicator')
        ax5.set_ylabel('Momentum Score')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Learning System Performance
        ax6 = axes[2, 1]
        # Simulate learning accuracy over time
        weeks = range(1, 53)
        accuracy_trend = 0.5 + 0.4 * (1 - np.exp(-np.array(weeks) / 20)) + np.random.normal(0, 0.02, len(weeks))
        
        ax6.plot(weeks, accuracy_trend, 'navy', linewidth=2)
        ax6.set_title('Self-Learning System Accuracy')
        ax6.set_xlabel('Week')
        ax6.set_ylabel('Prediction Accuracy')
        ax6.grid(True, alpha=0.3)
        ax6.set_ylim(0.4, 1.0)
        
        plt.tight_layout()
        
        # Save the plot
        output_path = self.config.output_path
        plt.savefig(f"{output_path}/economic_adaptation_demo_results.png", dpi=300, bbox_inches='tight')
        print(f"✅ Visualization saved to {output_path}/economic_adaptation_demo_results.png")
        
        plt.show()
    
    def _generate_intraday_data(self):
        """Intraday data simulation for learning demo."""
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='5min')[:-1]
        data = []
        for date in dates:
            data.append({
                'timestamp': date,
                'price': 100 + np.random.normal(0, 0.5),
                'volume': np.random.randint(1000, 10000),
                'volatility': np.random.uniform(0.01, 0.05)
            })
        return pd.DataFrame(data)
    
    def _aggregate_to_weekly(self, daily_data):
        """Daily data'ni haftalik agregatsiya qilish."""
        weekly_data = daily_data.copy()
        weekly_data['week'] = weekly_data['date'].dt.isocalendar().week
        weekly_data['year'] = weekly_data['date'].dt.year
        
        weekly_agg = weekly_data.groupby(['year', 'week']).agg({
            'gdp_growth': 'mean',
            'date': 'first'
        }).reset_index()
        
        return weekly_agg
    
    def _simulate_real_time_data(self):
        """Real-time data simulation."""
        return {
            'timestamp': datetime.now(),
            'market_data': {
                'SPY': 420.50,
                'QQQ': 350.25,
                'IWM': 195.75
            },
            'economic_indicators': {
                'vix': 18.5,
                'yield_curve': 0.45,
                'credit_spread': 1.2
            },
            'portfolio_positions': {
                'equity_allocation': 0.75,
                'bond_allocation': 0.20,
                'cash_allocation': 0.05
            }
        }
    
    def _simulate_market_data(self):
        """Market data simulation for integration demo."""
        return {
            'data_sources': ['yahoo_finance', 'bloomberg', 'fred'],
            'completeness': 0.98,
            'latency_ms': 15,
            'quality_score': 0.92,
            'last_update': datetime.now(),
            'missing_points': 2,
            'outliers_detected': 1
        }
    
    def run_complete_demo(self):
        """To'liq demo dasturni ishga tushirish."""
        print("\n🚀 TO'LIQ ECONOMIC ADAPTATION DEMO BOSHLAYMIZ...")
        print("="*80)
        
        try:
            # 1. Cycle Detection
            cycle_phases = self.demo_cycle_detection()
            
            # 2. Indicator Analysis
            indicators, momentum = self.demo_indicator_analysis()
            
            # 3. Adaptation Strategies
            strategies = self.demo_adaptation_strategies()
            
            # 4. Learning System
            learning_results = self.demo_learning_system()
            
            # 5. Performance Optimization
            performance_results = self.demo_performance_optimization()
            
            # 6. System Integration
            integration_results = self.demo_system_integration()
            
            # 7. Visualizations
            self.create_visualizations()
            
            # Demo summary
            self._print_demo_summary()
            
        except Exception as e:
            print(f"\n❌ Demo jarayonida xato yuz berdi: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _print_demo_summary(self):
        """Demo natijalarini jamlash."""
        print("\n" + "="*80)
        print("🎉 ECONOMIC ADAPTATION DEMO MUVAFFAQIYATLI YAKUNLANDI!")
        print("="*80)
        
        print("\n📋 Demo davomida ko'rsatilgan asosiy xususiyatlar:")
        print("✅ Business Cycle Detection va Phase Analysis")
        print("✅ Economic Indicators Analysis (Leading, Coincident, Lagging)")
        print("✅ Macro-Economic Adaptation Strategies")
        print("✅ Multi-Scale Self-Learning System")
        print("✅ Cycle-Adjusted Performance Optimization")
        print("✅ System Integration va Real-time Processing")
        print("✅ Comprehensive Data Visualization")
        
        print(f"\n📊 Demo natijalari:")
        print(f"  📈 Analiz qilingan vaqt davri: {len(self.cycle_data)} oy")
        print(f"  🔄 Business cycle fazalari: 4 ta")
        print(f"  📊 Economic indicators: 8 ta")
        print(f"  🧠 Learning time scales: 4 ta (intraday → monthly)")
        print(f"  ⚡ Performance metrics: 10+ ta")
        print(f"  🔗 Integration modules: 4+ ta")
        
        print(f"\n💡 Keyingi qadamlar:")
        print("  1. Haqiqiy ma'lumotlar bilan integratsiya qilish")
        print("  2. Model hyperparameter'larini sozlash")
        print("  3. Real-time data pipeline'ni sozlash")
        print("  4. Risk management modullari bilan bog'lash")
        print("  5. Production environment uchun optimizatsiya qilish")
        
        print(f"\n📁 Demo natijalari va grafiklar:")
        print(f"  📊 Visualization: {self.config.output_path}/economic_adaptation_demo_results.png")
        print(f"  📁 Data logs: {self.config.logs_path}/")
        print(f"  💾 Configuration: {self.config.data_path}/")
        
        print("\n" + "="*80)
        print("✨ Demo tugadi! Economic Adaptation tizimi tayyor.")
        print("="*80)

def main():
    """Asosiy demo funksiyasi."""
    demo = EconomicAdaptationDemo()
    demo.run_complete_demo()

if __name__ == "__main__":
    main()