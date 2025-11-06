"""
Market Regime Detection va Cross-Asset Correlation Learning Demo
Comprehensive example showing complete system functionality
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os

warnings.filterwarnings('ignore')

# Import all modules
from regime_detection import RegimeDetector, HiddenMarkovRegimeDetector, RegimeAnalyzer
from correlation_learning import DynamicCorrelationModel, CorrelationRegimeDetector, CrossAssetFactorModel, CorrelationClustering
from adaptive_strategies import (
    TrendFollowingStrategy, MeanReversionStrategy, VolatilityTargetingStrategy,
    DynamicRiskManager, AdaptivePortfolioManager
)
from implementation_framework import RealTimeRegimeDetector, RegimeAwareBacktester, SystemIntegration
from config import (
    SystemConfig, RegimePreferences, AssetUniverse, PerformanceBenchmarks,
    get_default_config, get_conservative_config, get_aggressive_config
)

class MarketRegimeSystemDemo:
    """
    Comprehensive Market Regime Detection va Cross-Asset Correlation Learning Demo
    """
    
    def __init__(self, config_type: str = "default"):
        """
        Args:
            config_type: Configuration type ('default', 'conservative', 'aggressive')
        """
        # Load configuration
        if config_type == "default":
            self.config = get_default_config()
        elif config_type == "conservative":
            self.config = get_conservative_config()
        elif config_type == "aggressive":
            self.config = get_aggressive_config()
        else:
            self.config = get_default_config()
            
        # Initialize components
        self.setup_components()
        
    def setup_components(self):
        """Setup all system components"""
        # Regime Detection Components
        self.regime_detector = RegimeDetector(
            lookback_window=self.config.regime_detection.lookback_window,
            transition_threshold=self.config.regime_detection.transition_threshold
        )
        
        self.hmm_detector = HiddenMarkovRegimeDetector(
            n_regimes=self.config.correlation.n_regimes
        )
        
        self.regime_analyzer = RegimeAnalyzer()
        
        # Correlation Learning Components
        self.dynamic_correlation = DynamicCorrelationModel(
            window_size=self.config.correlation.correlation_window,
            min_periods=self.config.correlation.min_periods
        )
        
        self.correlation_regime_detector = CorrelationRegimeDetector(
            n_regimes=self.config.correlation.n_regimes
        )
        
        self.factor_model = CrossAssetFactorModel(
            n_factors=self.config.correlation.n_factors,
            method=self.config.correlation.factor_method
        )
        
        self.correlation_clustering = CorrelationClustering()
        
        # Strategy Components
        self.trend_strategy = TrendFollowingStrategy()
        self.mean_reversion_strategy = MeanReversionStrategy()
        self.volatility_strategy = VolatilityTargetingStrategy()
        
        self.risk_manager = DynamicRiskManager(
            max_portfolio_risk=self.config.strategy.max_portfolio_risk,
            var_confidence=self.config.strategy.var_confidence
        )
        
        # Portfolio Manager
        self.portfolio_manager = AdaptivePortfolioManager(
            strategies=[self.trend_strategy, self.mean_reversion_strategy, self.volatility_strategy],
            risk_manager=self.risk_manager
        )
        
        # Data storage
        self.market_data = None
        self.regime_data = None
        self.correlation_data = None
        
    def generate_sample_data(self, n_days: int = 1000, n_assets: int = 10) -> pd.DataFrame:
        """
        Generate realistic sample market data with regime changes
        
        Args:
            n_days: Number of days
            n_assets: Number of assets
            
        Returns:
            DataFrame: Generated market data
        """
        # Create date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=n_days)
        dates = pd.date_range(start_date, end_date, freq='D')
        
        # Asset symbols
        if n_assets == 10:
            assets = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V']
        else:
            assets = [f'Asset_{i+1}' for i in range(n_assets)]
            
        # Generate data with regime changes
        returns_data = []
        prices_data = []
        
        current_prices = np.array([100 + i * 10 for i in range(n_assets)])
        
        for i, date in enumerate(dates):
            # Define regime periods
            if i < n_days * 0.2:  # Normal market
                regime = "normal"
                drift, volatility = 0.0005, 0.015
            elif i < n_days * 0.4:  # Trending bull market
                regime = "trending"
                drift, volatility = 0.001, 0.020
            elif i < n_days * 0.6:  # High volatility
                regime = "high_vol"
                drift, volatility = -0.0002, 0.035
            elif i < n_days * 0.8:  # Range-bound
                regime = "ranging"
                drift, volatility = 0, 0.008
            else:  # Crisis period
                regime = "crisis"
                drift, volatility = -0.002, 0.045
                
            # Generate returns with regime-specific characteristics
            daily_returns = np.random.normal(drift, volatility, n_assets)
            
            # Add regime-specific patterns
            if regime == "trending":
                daily_returns += np.linspace(0, 0.002, n_assets)  # Positive trend
            elif regime == "crisis":
                daily_returns *= 2  # Double volatility
                daily_returns -= 0.01  # Negative drift
                
            # Update prices
            current_prices *= (1 + daily_returns)
            
            returns_data.append(daily_returns)
            prices_data.append(current_prices.copy())
            
        # Create DataFrames
        returns_df = pd.DataFrame(returns_data, index=dates, columns=assets)
        prices_df = pd.DataFrame(prices_data, index=dates, columns=assets)
        
        self.market_data = prices_df
        
        # Create regime labels
        regime_labels = []
        for i, date in enumerate(dates):
            if i < n_days * 0.2:
                regime_labels.append("Normal")
            elif i < n_days * 0.4:
                regime_labels.append("Trending")
            elif i < n_days * 0.6:
                regime_labels.append("High Volatility")
            elif i < n_days * 0.8:
                regime_labels.append("Ranging")
            else:
                regime_labels.append("Crisis")
                
        self.regime_data = pd.Series(regime_labels, index=dates)
        
        print(f"Generated {n_days} days of data for {n_assets} assets")
        return prices_df
    
    def run_regime_detection(self) -> Dict:
        """Run regime detection analysis"""
        print("Running Regime Detection Analysis...")
        
        if self.market_data is None:
            raise ValueError("Market data not generated. Run generate_sample_data() first.")
            
        results = {}
        
        # Basic regime detection
        print("- Detecting market regimes...")
        regime_signals = self.regime_detector.detect_all_regimes(self.market_data)
        current_regime = self.regime_detector.get_current_regime(self.market_data)
        
        results['basic_regimes'] = regime_signals
        results['current_regime'] = current_regime
        
        # HMM regime detection
        print("- Running HMM regime detection...")
        if len(self.market_data) > 100:
            self.hmm_detector.fit(self.market_data)
            hmm_regimes = self.hmm_detector.predict_regimes(self.market_data)
            hmm_probabilities = self.hmm_detector.get_regime_probabilities(self.market_data)
            
            results['hmm_regimes'] = hmm_regimes
            results['hmm_probabilities'] = hmm_probabilities
            
        # Regime analysis
        print("- Analyzing regime characteristics...")
        regime_characteristics = self.regime_analyzer.analyze_regime_characteristics(
            self.market_data, regime_signals
        )
        
        # Regime transitions
        print("- Analyzing regime transitions...")
        if len(regime_signals.get('trending', [])) > 0:
            trending_regimes = regime_signals['trending'].replace({True: 'Trending', False: 'Not_Trending'})
            transition_analysis = self.regime_detector.analyze_regime_transitions(trending_regimes)
            results['transition_analysis'] = transition_analysis
            
        results['regime_characteristics'] = regime_characteristics
        
        print(f"Regime detection completed. Current regime: {current_regime}")
        return results
    
    def run_correlation_analysis(self) -> Dict:
        """Run cross-asset correlation analysis"""
        print("Running Cross-Asset Correlation Analysis...")
        
        if self.market_data is None:
            raise ValueError("Market data not generated. Run generate_sample_data() first.")
            
        results = {}
        
        # Dynamic correlation modeling
        print("- Calculating dynamic correlations...")
        rolling_correlations = self.dynamic_correlation.rolling_correlation_matrix(self.market_data.pct_change())
        correlation_stability = self.dynamic_correlation.correlation_stability_analysis(rolling_correlations)
        
        results['rolling_correlations'] = rolling_correlations
        results['correlation_stability'] = correlation_stability
        
        # Correlation regime detection
        print("- Detecting correlation regimes...")
        correlation_regimes = self.correlation_regime_detector.detect_correlation_regimes(
            self.market_data.pct_change(), window=60
        )
        results['correlation_regimes'] = correlation_regimes
        
        # Factor model analysis
        print("- Building cross-asset factor model...")
        if len(self.market_data) > self.config.correlation.n_factors * 10:
            factor_results = self.factor_model.fit_factor_model(self.market_data.pct_change())
            factor_forecasts = self.factor_model.forecast_factor_returns(
                self.market_data.pct_change().tail(60), horizon=5
            )
            
            results['factor_analysis'] = factor_results
            results['factor_forecasts'] = factor_forecasts
            
        # Correlation clustering
        print("- Performing correlation clustering...")
        clustering_results = self.correlation_clustering.cluster_assets_by_correlation(
            self.market_data.pct_change()
        )
        results['clustering'] = clustering_results
        
        print("Correlation analysis completed")
        return results
    
    def run_strategy_analysis(self) -> Dict:
        """Run adaptive strategy analysis"""
        print("Running Adaptive Strategy Analysis...")
        
        if self.market_data is None:
            raise ValueError("Market data not generated. Run generate_sample_data() first.")
            
        results = {}
        
        # Strategy performance by regime
        print("- Testing regime-adaptive strategies...")
        
        strategy_functions = {
            'Trending': lambda x: self.trend_strategy.generate_signals(self.market_data, 'Trending'),
            'Ranging': lambda x: self.mean_reversion_strategy.generate_signals(self.market_data, 'Ranging'),
            'High Volatility': lambda x: self.volatility_strategy.generate_signals(self.market_data, 'High Volatility'),
            'Crisis': lambda x: {'AAPL': {'action': 'SELL', 'quantity': 100}},
            'Normal': lambda x: {'AAPL': {'action': 'HOLD', 'quantity': 0}}
        }
        
        # Backtest with regime awareness
        backtester = RegimeAwareBacktester(
            initial_capital=self.config.backtest.initial_capital
        )
        
        backtest_results = backtester.run_backtest(
            market_data=self.market_data,
            regime_data=self.regime_data,
            strategy_functions=strategy_functions
        )
        
        results['backtest_results'] = backtest_results
        
        # Strategy selection analysis
        print("- Analyzing optimal strategy selection...")
        strategy_weights = self.portfolio_manager.allocate_regime_weights(self.regime_data)
        results['strategy_weights'] = strategy_weights
        
        # Risk analysis
        print("- Performing regime-aware risk analysis...")
        risk_metrics = self.risk_manager.calculate_portfolio_var(
            backtest_results['daily_returns'], self.config.strategy.var_confidence
        )
        results['portfolio_var'] = risk_metrics
        
        print("Strategy analysis completed")
        return results
    
    def generate_comprehensive_report(self, regime_results: Dict, correlation_results: Dict, 
                                    strategy_results: Dict) -> str:
        """Generate comprehensive analysis report"""
        
        report = []
        report.append("=" * 80)
        report.append("MARKET REGIME DETECTION VA CROSS-ASSET CORRELATION LEARNING")
        report.append("COMPREHENSIVE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Data Period: {len(self.market_data)} days")
        report.append(f"Assets: {', '.join(self.market_data.columns)}")
        report.append("")
        
        # Regime Detection Summary
        report.append("1. REGIME DETECTION SUMMARY")
        report.append("-" * 40)
        report.append(f"Current Market Regime: {regime_results['current_regime']}")
        
        if 'transition_analysis' in regime_results:
            trans_analysis = regime_results['transition_analysis']
            if 'most_persistent_regime' in trans_analysis:
                report.append(f"Most Persistent Regime: {trans_analysis['most_persistent_regime']}")
                
        # Regime characteristics
        if 'regime_characteristics' in regime_results:
            report.append("\\nRegime Characteristics:")
            for regime_name, characteristics in regime_results['regime_characteristics'].items():
                if characteristics:
                    report.append(f"  {regime_name}:")
                    for state, metrics in characteristics.items():
                        if isinstance(metrics, dict) and 'avg_return' in metrics:
                            report.append(f"    {state}: Return={metrics['avg_return']:.4f}, "
                                        f"Vol={metrics['volatility']:.4f}, "
                                        f"Sharpe={metrics['sharpe_ratio']:.3f}")
                            
        report.append("")
        
        # Correlation Analysis Summary
        report.append("2. CROSS-ASSET CORRELATION ANALYSIS")
        report.append("-" * 40)
        
        if 'correlation_stability' in correlation_results:
            stability = correlation_results['correlation_stability']
            report.append(f"Correlation Pairs Analyzed: {len(stability)}")
            
            # Average correlation metrics
            avg_correlations = []
            for pair, metrics in stability.items():
                if 'mean_correlation' in metrics:
                    avg_correlations.append(metrics['mean_correlation'])
                    
            if avg_correlations:
                report.append(f"Average Correlation: {np.mean(avg_correlations):.4f}")
                report.append(f"Correlation Range: {np.min(avg_correlations):.4f} to {np.max(avg_correlations):.4f}")
                
        if 'clustering' in correlation_results:
            clustering = correlation_results['clustering']
            if 'asset_clusters' in clustering:
                report.append(f"Asset Clusters Identified: {len(clustering['asset_clusters'])}")
                for cluster_name, assets in clustering['asset_clusters'].items():
                    if len(assets) > 1:
                        avg_corr = clustering['cluster_characteristics'][cluster_name]['avg_correlation']
                        report.append(f"  {cluster_name}: {len(assets)} assets (avg corr: {avg_corr:.3f})")
                        
        report.append("")
        
        # Strategy Performance Summary
        report.append("3. ADAPTIVE STRATEGY PERFORMANCE")
        report.append("-" * 40)
        
        if 'backtest_results' in strategy_results:
            backtest = strategy_results['backtest_results']
            metrics = backtest.get('performance_metrics', {})
            
            if metrics:
                report.append(f"Total Return: {metrics.get('total_return', 0):.2%}")
                report.append(f"Annualized Return: {metrics.get('annualized_return', 0):.2%}")
                report.append(f"Annualized Volatility: {metrics.get('volatility', 0):.2%}")
                report.append(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
                report.append(f"Maximum Drawdown: {metrics.get('max_drawdown', 0):.2%}")
                report.append(f"Total Trades: {metrics.get('total_trades', 0)}")
                
        # Strategy weights
        if 'strategy_weights' in strategy_results:
            weights = strategy_results['strategy_weights']
            report.append("\\nStrategy Allocation:")
            for strategy, weight in weights.items():
                report.append(f"  {strategy}: {weight:.1%}")
                
        # Regime-specific performance
        if 'backtest_results' in strategy_results and 'performance_metrics' in strategy_results['backtest_results']:
            perf = strategy_results['backtest_results']['performance_metrics']
            if 'regime_metrics' in perf:
                report.append("\\nPerformance by Regime:")
                for regime, metrics in perf['regime_metrics'].items():
                    if isinstance(metrics, dict) and 'total_return' in metrics:
                        report.append(f"  {regime}: {metrics['total_return']:.2%} return, "
                                    f"{metrics['sharpe_ratio']:.3f} Sharpe")
                                    
        report.append("")
        
        # Risk Analysis Summary
        report.append("4. RISK MANAGEMENT ANALYSIS")
        report.append("-" * 40)
        
        if 'portfolio_var' in strategy_results:
            var_95 = strategy_results['portfolio_var']
            report.append(f"Portfolio VaR (95%): {var_95:.2%}")
            
        report.append(f"Max Portfolio Risk: {self.config.strategy.max_portfolio_risk:.2%}")
        report.append(f"Max Drawdown Limit: {self.config.risk.max_drawdown_limit:.2%}")
        
        report.append("")
        
        # Key Insights
        report.append("5. KEY INSIGHTS & RECOMMENDATIONS")
        report.append("-" * 40)
        
        # Market regime insights
        current_regime = regime_results['current_regime']
        if current_regime == "Trending":
            report.append("• Market is in trending regime - Trend following strategies recommended")
        elif current_regime == "High Volatility":
            report.append("• High volatility detected - Consider reduced position sizes and defensive strategies")
        elif current_regime == "Crisis":
            report.append("• Crisis conditions detected - Risk reduction and defensive positioning recommended")
            
        # Correlation insights
        if 'correlation_stability' in correlation_results:
            stability = correlation_results['correlation_stability']
            high_correlation_pairs = [pair for pair, metrics in stability.items() 
                                    if metrics.get('mean_correlation', 0) > 0.7]
            if high_correlation_pairs:
                report.append(f"• {len(high_correlation_pairs)} asset pairs show high correlation - Diversification challenges")
                
        # Strategy recommendations
        if 'strategy_weights' in strategy_results:
            weights = strategy_results['strategy_weights']
            dominant_strategy = max(weights, key=weights.get)
            report.append(f"• Dominant strategy recommended: {dominant_strategy}")
            
        report.append("")
        report.append("=" * 80)
        
        return "\\n".join(report)
    
    def create_visualizations(self, regime_results: Dict, correlation_results: Dict, 
                            strategy_results: Dict, save_plots: bool = True):
        """Create comprehensive visualizations"""
        print("Creating visualizations...")
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        
        # Figure 1: Market Data and Regime Detection
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('Market Regime Detection Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Price data
        if self.market_data is not None:
            axes[0, 0].plot(self.market_data.index, self.market_data.iloc[:, :5])
            axes[0, 0].set_title('Sample Asset Prices')
            axes[0, 0].set_ylabel('Price')
            axes[0, 0].legend(self.market_data.columns[:5])
            axes[0, 0].grid(True, alpha=0.3)
            
        # Plot 2: Regime classification
        if self.regime_data is not None:
            regime_colors = {'Normal': 'blue', 'Trending': 'green', 'High Volatility': 'orange', 
                           'Ranging': 'purple', 'Crisis': 'red'}
            colors = [regime_colors.get(reg, 'gray') for reg in self.regime_data]
            axes[0, 1].scatter(self.regime_data.index, range(len(self.regime_data)), c=colors, alpha=0.6)
            axes[0, 1].set_title('Market Regime Timeline')
            axes[0, 1].set_ylabel('Regime')
            
        # Plot 3: HMM regimes if available
        if 'hmm_regimes' in regime_results:
            hmm_regimes = regime_results['hmm_regimes']
            if len(hmm_regimes) > 0:
                axes[1, 0].plot(hmm_regimes.index, hmm_regimes.values)
                axes[1, 0].set_title('HMM Regime Detection')
                axes[1, 0].set_ylabel('Regime')
                axes[1, 0].tick_params(axis='x', rotation=45)
                
        # Plot 4: Volatility regime
        if 'basic_regimes' in regime_results and 'volatility_regime' in regime_results['basic_regimes']:
            vol_regimes = regime_results['basic_regimes']['volatility_regime']
            vol_colors = {'High': 'red', 'Low': 'green', 'Normal': 'blue', 'Unknown': 'gray'}
            colors = [vol_colors.get(vol, 'gray') for vol in vol_regimes]
            axes[1, 1].scatter(vol_regimes.index, range(len(vol_regimes)), c=colors, alpha=0.6)
            axes[1, 1].set_title('Volatility Regime Detection')
            axes[1, 1].set_ylabel('Volatility Regime')
            
        # Plot 5: Correlation clustering
        if 'clustering' in correlation_results:
            clustering = correlation_results['clustering']
            if 'asset_clusters' in clustering:
                cluster_sizes = [len(assets) for assets in clustering['asset_clusters'].values()]
                cluster_labels = list(clustering['asset_clusters'].keys())
                
                axes[2, 0].bar(cluster_labels, cluster_sizes)
                axes[2, 0].set_title('Asset Cluster Sizes')
                axes[2, 0].set_ylabel('Number of Assets')
                axes[2, 0].tick_params(axis='x', rotation=45)
                
        # Plot 6: Strategy performance
        if 'backtest_results' in strategy_results:
            backtest = strategy_results['backtest_results']
            if 'portfolio_values' in backtest:
                portfolio_values = backtest['portfolio_values']
                axes[2, 1].plot(portfolio_values)
                axes[2, 1].set_title('Portfolio Value Evolution')
                axes[2, 1].set_ylabel('Portfolio Value')
                axes[2, 1].grid(True, alpha=0.3)
                
        plt.tight_layout()
        
        if save_plots:
            os.makedirs(self.config.output_directory, exist_ok=True)
            plt.savefig(f"{self.config.output_directory}/market_regime_analysis.png", dpi=300, bbox_inches='tight')
            print(f"Plot saved to {self.config.output_directory}/market_regime_analysis.png")
            
        plt.show()
        
        # Figure 2: Correlation Analysis
        if 'rolling_correlations' in correlation_results:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Cross-Asset Correlation Analysis', fontsize=16, fontweight='bold')
            
            rolling_corr = correlation_results['rolling_correlations']
            
            # Plot correlation heatmap for recent period
            if len(rolling_corr) > 0:
                recent_corr = rolling_corr.iloc[-1]
                if isinstance(recent_corr, pd.DataFrame):
                    sns.heatmap(recent_corr, annot=True, cmap='RdBu_r', center=0, 
                              ax=axes[0, 0], fmt='.2f')
                    axes[0, 0].set_title('Recent Correlation Matrix')
                    
            # Plot correlation time series for key pairs
            if len(rolling_corr) > 0 and len(self.market_data.columns) >= 2:
                asset1, asset2 = self.market_data.columns[0], self.market_data.columns[1]
                
                # Extract correlation for first asset pair
                corr_series = []
                for date in rolling_corr.index:
                    try:
                        corr_val = rolling_corr.loc[date, (asset1, asset2)]
                        if not pd.isna(corr_val):
                            corr_series.append(corr_val)
                    except:
                        continue
                        
                if corr_series:
                    dates = rolling_corr.index[-len(corr_series):]
                    axes[0, 1].plot(dates, corr_series)
                    axes[0, 1].set_title(f'{asset1}-{asset2} Correlation')
                    axes[0, 1].set_ylabel('Correlation')
                    axes[0, 1].tick_params(axis='x', rotation=45)
                    axes[0, 1].grid(True, alpha=0.3)
                    
            plt.tight_layout()
            
            if save_plots:
                plt.savefig(f"{self.config.output_directory}/correlation_analysis.png", dpi=300, bbox_inches='tight')
                print(f"Correlation plot saved to {self.config.output_directory}/correlation_analysis.png")
                
            plt.show()
    
    def run_complete_demo(self, n_days: int = 1000, n_assets: int = 10, 
                         save_results: bool = True) -> Dict:
        """Run complete demonstration of all system components"""
        print("=" * 60)
        print("MARKET REGIME DETECTION VA CROSS-ASSET CORRELATION LEARNING")
        print("COMPREHENSIVE SYSTEM DEMO")
        print("=" * 60)
        print(f"Configuration: {self.config}")
        print("")
        
        # Step 1: Generate sample data
        print("STEP 1: GENERATING SAMPLE DATA")
        print("-" * 40)
        market_data = self.generate_sample_data(n_days, n_assets)
        print("")
        
        # Step 2: Regime Detection
        print("STEP 2: REGIME DETECTION ANALYSIS")
        print("-" * 40)
        regime_results = self.run_regime_detection()
        print("")
        
        # Step 3: Correlation Analysis
        print("STEP 3: CROSS-ASSET CORRELATION ANALYSIS")
        print("-" * 40)
        correlation_results = self.run_correlation_analysis()
        print("")
        
        # Step 4: Strategy Analysis
        print("STEP 4: ADAPTIVE STRATEGY ANALYSIS")
        print("-" * 40)
        strategy_results = self.run_strategy_analysis()
        print("")
        
        # Step 5: Generate Report
        print("STEP 5: GENERATING COMPREHENSIVE REPORT")
        print("-" * 40)
        report = self.generate_comprehensive_report(regime_results, correlation_results, strategy_results)
        
        if save_results:
            os.makedirs(self.config.output_directory, exist_ok=True)
            
            # Save report
            with open(f"{self.config.output_directory}/comprehensive_report.txt", 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to {self.config.output_directory}/comprehensive_report.txt")
            
            # Save detailed results
            results_dict = {
                'regime_results': regime_results,
                'correlation_results': correlation_results,
                'strategy_results': strategy_results,
                'config': self.config.__dict__,
                'timestamp': datetime.now().isoformat()
            }
            
            import json
            with open(f"{self.config.output_directory}/detailed_results.json", 'w') as f:
                json.dump(results_dict, f, indent=2, default=str)
            print(f"Detailed results saved to {self.config.output_directory}/detailed_results.json")
            
        # Step 6: Create Visualizations
        print("STEP 6: CREATING VISUALIZATIONS")
        print("-" * 40)
        self.create_visualizations(regime_results, correlation_results, strategy_results, save_results)
        print("")
        
        # Final Summary
        print("=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Generated comprehensive analysis for {n_days} days of market data")
        print(f"Analyzed {n_assets} assets with {len(self.market_data.columns)} different symbols")
        print(f"Detected {len(set(self.regime_data))} distinct market regimes")
        print(f"Completed correlation analysis across all asset pairs")
        print(f"Tested regime-adaptive trading strategies")
        
        if save_results:
            print(f"\\nResults saved to: {self.config.output_directory}")
            print(f"- comprehensive_report.txt: Executive summary")
            print(f"- detailed_results.json: Complete analysis results")
            print(f"- market_regime_analysis.png: Main analysis plots")
            print(f"- correlation_analysis.png: Correlation analysis plots")
            
        # Return comprehensive results
        complete_results = {
            'market_data': market_data,
            'regime_results': regime_results,
            'correlation_results': correlation_results,
            'strategy_results': strategy_results,
            'report': report,
            'config': self.config
        }
        
        return complete_results


def main():
    """Main demo function"""
    print("Market Regime Detection va Cross-Asset Correlation Learning")
    print("Complete System Demo\\n")
    
    # Run default configuration demo
    demo_default = MarketRegimeSystemDemo("default")
    results_default = demo_default.run_complete_demo(
        n_days=1000,  # 4 years of data
        n_assets=10,  # 10 major stocks
        save_results=True
    )
    
    print("\\n" + "="*80)
    print("Demo executed successfully!")
    print("Check the output directory for comprehensive results.")
    print("="*80)


if __name__ == "__main__":
    main()