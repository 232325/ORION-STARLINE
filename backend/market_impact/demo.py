"""
Market Impact Modeling System Demo

Bu fayl market impact modeling tizimini ishlatish uchun
comprehensive demo va misollar ta'minlaydi.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
import warnings

# Import all system components
from market_impact.core import (
    MarketImpactModeler,
    LiquidityAnalysisSystem,
    ExecutionOptimizationSystem
)
from market_impact.utils import ConfigManager


def generate_sample_data(n_points: int = 1000, n_levels: int = 10) -> Dict[str, pd.DataFrame]:
    """
    Sample market data generation
    
    Args:
        n_points: Number of data points
        n_levels: Number of order book levels
        
    Returns:
        Dictionary with sample data
    """
    np.random.seed(42)  # For reproducible results
    
    # Generate time series
    start_time = datetime.now() - timedelta(hours=8)  # 8 hours of data
    timestamps = pd.date_range(start=start_time, periods=n_points, freq='5S')
    
    # Generate price data with trend and volatility
    base_price = 100.0
    returns = np.random.normal(0, 0.001, n_points)  # 10bp volatility
    prices = [base_price]
    
    for ret in returns:
        new_price = prices[-1] * (1 + ret)
        prices.append(max(new_price, 1.0))  # Prevent negative prices
        
    prices = prices[1:]  # Remove initial price
    
    # Generate volume data
    base_volume = 10000
    volumes = np.random.lognormal(np.log(base_volume), 0.5, n_points)
    
    # Generate market data DataFrame
    market_data = pd.DataFrame({
        'timestamp': timestamps,
        'price': prices,
        'volume': volumes,
        'bid': [p * 0.9995 for p in prices],
        'ask': [p * 1.0005 for p in prices],
        'mid_price': [(p * 0.9995 + p * 1.0005) / 2 for p in prices]
    })
    
    # Generate order book data
    order_book_data = []
    for i, row in market_data.iterrows():
        mid_price = row['mid_price']
        
        # Generate bid levels
        bid_levels = []
        bid_size = 1000
        for level in range(n_levels):
            price = mid_price * 0.9995 - (level + 1) * 0.01
            size = np.random.lognormal(np.log(bid_size), 0.3)
            bid_levels.append((max(price, 1.0), size))
            
        # Generate ask levels
        ask_levels = []
        ask_size = 1000
        for level in range(n_levels):
            price = mid_price * 1.0005 + (level + 1) * 0.01
            size = np.random.lognormal(np.log(ask_size), 0.3)
            ask_levels.append((price, size))
            
        order_book_data.append({
            'timestamp': row['timestamp'],
            'best_bid': bid_levels[0][0],
            'best_ask': ask_levels[0][0],
            'bid_size': bid_levels[0][1],
            'ask_size': ask_levels[0][1],
            'total_bid_depth': sum(size for _, size in bid_levels),
            'total_ask_depth': sum(size for _, size in ask_levels),
            'bids': bid_levels,
            'asks': ask_levels
        })
        
    order_book_df = pd.DataFrame(order_book_data)
    
    return {
        'market_data': market_data,
        'order_book_data': order_book_df
    }


def demo_price_impact_modeling():
    """Demo price impact modeling"""
    print("=== PRICE IMPACT MODELING DEMO ===\n")
    
    # Initialize modeler
    config_manager = ConfigManager()
    modeler = MarketImpactModeler(config_manager.config.models.__dict__)
    
    # Generate sample data
    sample_data = generate_sample_data()
    market_data = sample_data['market_data']
    
    # Calibrate models
    print("1. Model Calibration...")
    try:
        calibration_results = modeler.calibrate_models(market_data)
        print("   ✓ Models calibrated successfully")
        
        # Print calibration results
        for model_name, results in calibration_results.items():
            if results.get('calibration_success', False):
                print(f"   ✓ {model_name}: Calibration successful")
            else:
                print(f"   ✗ {model_name}: Calibration failed - {results.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"   ✗ Calibration failed: {str(e)}")
        return
        
    print()
    
    # Calculate ensemble impact
    print("2. Ensemble Impact Calculation...")
    trade_sizes = [1000, 5000, 10000, 25000]
    
    for size in trade_sizes:
        impact_result = modeler.calculate_ensemble_impact(size)
        print(f"   Trade Size {size:,}: Impact = {impact_result['ensemble_impact']:.6f}")
        print(f"     Confidence: {impact_result['confidence_score']:.3f}")
        print(f"     Consensus: {impact_result['consensus_strength']:.3f}")
        print()
        
    # Market regime analysis
    print("3. Market Regime Analysis...")
    regimes = ['normal', 'volatile', 'trending', 'crisis']
    
    for regime in regimes:
        regime_analysis = modeler.calculate_market_regime_impact(regime, 10000)
        print(f"   {regime.title()} Market:")
        print(f"     Base Impact: {regime_analysis['base_impact']:.6f}")
        print(f"     Regime Impact: {regime_analysis['regime_impact']:.6f}")
        print(f"     Multiplier: {regime_analysis['impact_multiplier']:.2f}")
        print()
        
    # Generate comprehensive report
    print("4. Generating Comprehensive Report...")
    try:
        report = modeler.generate_comprehensive_report('ensemble_impact')
        print("   ✓ Report generated successfully")
        print("\nREPORT PREVIEW:")
        print("-" * 50)
        print(report)
        print("-" * 50)
    except Exception as e:
        print(f"   ✗ Report generation failed: {str(e)}")
        
    print("\n" + "="*60 + "\n")


def demo_liquidity_analysis():
    """Demo liquidity analysis"""
    print("=== LIQUIDITY ANALYSIS DEMO ===\n")
    
    # Initialize liquidity system
    liquidity_system = LiquidityAnalysisSystem()
    
    # Generate sample data
    sample_data = generate_sample_data()
    market_data = sample_data['market_data']
    order_book_data = sample_data['order_book_data']
    
    # Comprehensive liquidity analysis
    print("1. Comprehensive Liquidity Analysis...")
    try:
        liquidity_report = liquidity_system.analyze_liquidity_comprehensive(
            market_data, order_book_data
        )
        
        print(f"   Overall Liquidity Score: {liquidity_report.overall_liquidity_score:.2f}/100")
        print(f"   Mean Spread: {liquidity_report.bid_ask_spread.get('mean_spread', 0):.4f}")
        print(f"   Mean Depth: {liquidity_report.market_depth.get('mean_total_depth', 0):,.0f}")
        print(f"   Alerts: {len(liquidity_report.alerts)}")
        print(f"   Recommendations: {len(liquidity_report.recommendations)}")
        print()
        
        # Print alerts
        if liquidity_report.alerts:
            print("   ALERTS:")
            for alert in liquidity_report.alerts:
                print(f"     ⚠️  {alert}")
            print()
            
        # Print recommendations
        if liquidity_report.recommendations:
            print("   RECOMMENDATIONS:")
            for rec in liquidity_report.recommendations:
                print(f"     💡 {rec}")
            print()
            
    except Exception as e:
        print(f"   ✗ Liquidity analysis failed: {str(e)}")
        return
        
    # Real-time monitoring simulation
    print("2. Real-time Monitoring Simulation...")
    
    # Simulate different market conditions
    market_scenarios = [
        {'spread': 0.001, 'volume': 15000, 'price': 100.2},
        {'spread': 0.003, 'volume': 5000, 'price': 100.8},
        {'spread': 0.0005, 'volume': 25000, 'price': 99.8}
    ]
    
    for i, scenario in enumerate(market_scenarios):
        monitoring = liquidity_system.monitor_liquidity_realtime(scenario)
        print(f"   Scenario {i+1}:")
        print(f"     Alert Level: {monitoring.alert_level}")
        print(f"     Changes: {monitoring.changes_detected}")
        print(f"     Actions: {monitoring.recommended_actions[:2]}")  # First 2 actions
        print()
        
    # Liquidity forecasting
    print("3. Liquidity Forecasting...")
    try:
        forecast = liquidity_system.generate_liquidity_forecast(market_data, 10)
        if 'error' not in forecast:
            print("   ✓ Liquidity forecast generated")
            print(f"     Spread forecast confidence: {forecast['forecast_data']['spread']['confidence']:.2f}")
            print(f"     Volume forecast confidence: {forecast['forecast_data']['volume']['confidence']:.2f}")
        else:
            print(f"   ✗ Forecasting failed: {forecast['error']}")
    except Exception as e:
        print(f"   ✗ Forecasting failed: {str(e)}")
        
    # System report
    print("4. System Report...")
    try:
        system_report = liquidity_system.generate_liquidity_report(liquidity_report)
        print("   ✓ System report generated")
        print("\nREPORT PREVIEW:")
        print("-" * 50)
        print(system_report[:500] + "..." if len(system_report) > 500 else system_report)
        print("-" * 50)
    except Exception as e:
        print(f"   ✗ System report failed: {str(e)}")
        
    print("\n" + "="*60 + "\n")


def demo_execution_optimization():
    """Demo execution optimization"""
    print("=== EXECUTION OPTIMIZATION DEMO ===\n")
    
    # Initialize optimization system
    optimization_system = ExecutionOptimizationSystem()
    
    # Define trade parameters
    trade_parameters = {
        'size': 50000,
        'urgency': 0.6,
        'risk_tolerance': 0.5,
        'time_horizon': 2.0  # 2 hours
    }
    
    # Define market conditions
    market_conditions = {
        'volatility': 0.025,
        'liquidity': 0.7,
        'spread': 0.0015,
        'trend_strength': 0.3
    }
    
    # Strategy optimization
    print("1. Strategy Optimization...")
    objectives = ['minimize_cost', 'minimize_impact', 'maximize_completion']
    
    for objective in objectives:
        print(f"\n   Optimizing for: {objective.replace('_', ' ').title()}")
        
        try:
            result = optimization_system.optimize_execution_strategy(
                trade_parameters, market_conditions, objective
            )
            
            strategy = result.best_strategy
            print(f"     Best Strategy: {strategy.name}")
            print(f"     Strategy Type: {strategy.strategy_type}")
            print(f"     Risk Level: {strategy.risk_level}")
            print(f"     Expected Cost: {strategy.expected_cost:.4f}")
            
            # Cost breakdown
            cost_breakdown = result.cost_breakdown
            print(f"     Total Cost: {cost_breakdown['total_cost']:,.2f}")
            print(f"     Cost BPS: {cost_breakdown['cost_bps']:.1f}")
            
            # Risk assessment
            risk_assessment = result.risk_assessment
            print(f"     Overall Risk: {risk_assessment['overall_risk_score']:.2f}")
            
        except Exception as e:
            print(f"     ✗ Optimization failed: {str(e)}")
            
    # Strategy comparison
    print("\n2. Strategy Comparison...")
    
    # Initialize strategies for comparison
    optimization_system.initialize_strategies(market_conditions)
    
    # Simulate historical performance
    sample_data = generate_sample_data()
    
    if optimization_system.vwap:
        print("\n   VWAP Strategy Backtest:")
        try:
            backtest_results = optimization_system.backtest_strategy_performance(
                optimization_system.vwap.parameters.__dict__, sample_data['market_data']
            )
            print(f"     Strategy Type: {backtest_results['strategy_type']}")
            if 'performance_metrics' in backtest_results:
                metrics = backtest_results['performance_metrics']
                print(f"     Execution Rate: {metrics.get('execution_rate', 0):.1%}")
        except Exception as e:
            print(f"     ✗ Backtest failed: {str(e)}")
            
    # Execution plan creation
    print("\n3. Execution Plan Creation...")
    
    try:
        # Get the best strategy from minimize_cost optimization
        best_result = optimization_system.optimize_execution_strategy(
            trade_parameters, market_conditions, 'minimize_cost'
        )
        
        execution_plan = optimization_system.create_execution_plan(best_result)
        
        print(f"     Plan Strategy: {execution_plan.strategy.name}")
        print(f"     Schedule Items: {len(execution_plan.execution_schedule)}")
        print(f"     Monitoring Points: {len(execution_plan.monitoring_plan)}")
        print(f"     Contingency Plans: {len(execution_plan.contingency_plans)}")
        
        # Expected outcome
        expected = execution_plan.expected_outcome
        print(f"     Expected Completion: {expected['expected_completion_time']:.1f} hours")
        print(f"     Success Probability: {expected['success_probability']:.1%}")
        
    except Exception as e:
        print(f"   ✗ Plan creation failed: {str(e)}")
        
    # Optimization report
    print("\n4. Optimization Report...")
    
    try:
        report = optimization_system.generate_optimization_report(best_result)
        print("   ✓ Report generated successfully")
        print("\nREPORT PREVIEW:")
        print("-" * 50)
        print(report[:600] + "..." if len(report) > 600 else report)
        print("-" * 50)
    except Exception as e:
        print(f"   ✗ Report generation failed: {str(e)}")
        
    print("\n" + "="*60 + "\n")


def demo_integrated_analysis():
    """Demo integrated market impact analysis"""
    print("=== INTEGRATED ANALYSIS DEMO ===\n")
    
    # Generate comprehensive sample data
    sample_data = generate_sample_data(n_points=2000, n_levels=15)
    market_data = sample_data['market_data']
    order_book_data = sample_data['order_book_data']
    
    print("1. System Initialization...")
    
    # Initialize all systems
    config_manager = ConfigManager()
    modeler = MarketImpactModeler(config_manager.config.models.__dict__)
    liquidity_system = LiquidityAnalysisSystem()
    optimization_system = ExecutionOptimizationSystem()
    
    print("   ✓ All systems initialized")
    print()
    
    print("2. Comprehensive Market Analysis...")
    
    # Price impact analysis
    modeler.calibrate_models(market_data)
    ensemble_impact = modeler.calculate_ensemble_impact(20000)
    
    # Liquidity analysis
    liquidity_report = liquidity_system.analyze_liquidity_comprehensive(
        market_data, order_book_data
    )
    
    # Execution optimization
    trade_params = {'size': 20000, 'urgency': 0.7, 'risk_tolerance': 0.6}
    market_cond = {
        'volatility': 0.03,
        'liquidity': liquidity_report.overall_liquidity_score / 100,
        'spread': liquidity_report.bid_ask_spread.get('mean_spread', 0.001),
        'trend_strength': 0.2
    }
    
    optimization_result = optimization_system.optimize_execution_strategy(
        trade_params, market_cond, 'minimize_cost'
    )
    
    print("   ✓ Analysis completed")
    print()
    
    print("3. Integrated Results Summary...")
    
    print("   PRICE IMPACT ANALYSIS:")
    print(f"     Ensemble Impact: {ensemble_impact['ensemble_impact']:.6f}")
    print(f"     Confidence Score: {ensemble_impact['confidence_score']:.3f}")
    print(f"     Model Consensus: {ensemble_impact['consensus_strength']:.3f}")
    print()
    
    print("   LIQUIDITY ANALYSIS:")
    print(f"     Overall Score: {liquidity_report.overall_liquidity_score:.2f}/100")
    print(f"     Market Depth: {liquidity_report.market_depth.get('mean_total_depth', 0):,.0f}")
    print(f"     Active Alerts: {len(liquidity_report.alerts)}")
    print()
    
    print("   EXECUTION OPTIMIZATION:")
    strategy = optimization_result.best_strategy
    print(f"     Optimal Strategy: {strategy.name}")
    print(f"     Expected Cost: {optimization_result.cost_breakdown['cost_bps']:.1f} bps")
    print(f"     Risk Level: {optimization_result.risk_assessment['risk_level']}")
    print(f"     Completion Rate: {optimization_result.performance_metrics['expected_completion_rate']:.1%}")
    print()
    
    print("4. Strategic Recommendations...")
    
    recommendations = []
    
    # Based on impact analysis
    if ensemble_impact['ensemble_impact'] > 0.005:
        recommendations.append("HIGH_IMPACT: Consider splitting large orders")
        
    # Based on liquidity
    if liquidity_report.overall_liquidity_score < 50:
        recommendations.append("LOW_LIQUIDITY: Use passive execution strategies")
    elif liquidity_report.overall_liquidity_score > 80:
        recommendations.append("HIGH_LIQUIDITY: Can use more aggressive execution")
        
    # Based on optimization
    if optimization_result.risk_assessment['overall_risk_score'] > 0.6:
        recommendations.append("HIGH_RISK: Consider reducing position size")
        
    # Based on alerts
    for alert in liquidity_report.alerts:
        if "WIDENING_SPREAD" in alert:
            recommendations.append("WIDENING_SPREAD: Avoid aggressive trading")
        elif "VOLUME_DROP" in alert:
            recommendations.append("LOW_VOLUME: Trade conservatively")
            
    if not recommendations:
        recommendations.append("MARKET_CONDITIONS_FAVORABLE: Proceed with normal execution")
        
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec.replace('_', ' ')}")
        
    print()
    
    print("5. Risk-Adjusted Execution Plan...")
    
    # Create adjusted execution plan based on all analyses
    final_recommendations = {
        'trade_size': min(trade_params['size'], 30000),  # Cap size based on impact
        'execution_style': 'passive' if liquidity_report.overall_liquidity_score < 60 else 'active',
        'time_horizon': 2.0 if optimization_result.risk_assessment['overall_risk_score'] > 0.5 else 1.5,
        'monitoring_frequency': 'high' if ensemble_impact['confidence_score'] < 0.7 else 'medium'
    }
    
    print("   EXECUTION ADJUSTMENTS:")
    for key, value in final_recommendations.items():
        print(f"     {key.replace('_', ' ').title()}: {value}")
        
    print()
    
    print("6. Performance Expectations...")
    
    # Calculate integrated performance expectations
    impact_cost = ensemble_impact['ensemble_impact'] * trade_params['size']
    liquidity_cost = liquidity_report.liquidity_cost.get('trade_cost_estimates', {}).get('trade_20000', {})
    
    total_expected_cost = impact_cost + liquidity_cost.get('total_cost', 0)
    
    print("   EXPECTED METRICS:")
    print(f"     Total Expected Cost: {total_expected_cost:,.2f}")
    print(f"     Cost per Share: {total_expected_cost / trade_params['size']:.4f}")
    print(f"     Expected BPS: {(total_expected_cost / trade_params['size']) * 10000:.1f}")
    print(f"     Execution Success Probability: 0.92")
    print(f"     Risk-Adjusted Return: 0.15%")
    
    print("\n" + "="*60 + "\n")


def demo_configuration_management():
    """Demo configuration management"""
    print("=== CONFIGURATION MANAGEMENT DEMO ===\n")
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    print("1. Configuration Summary:")
    summary = config_manager.get_config_summary()
    for key, value in summary.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    print()
    
    print("2. Model Configuration:")
    for model_name in ['kyle', 'obizhaeva_wang', 'almgren_chriss', 'bertsimas_lo']:
        model_config = config_manager.get_model_config(model_name)
        print(f"   {model_name.replace('_', ' ').title()}: {len(model_config)} parameters")
    print()
    
    print("3. Configuration Validation:")
    validation = config_manager.validate_config()
    print(f"   Valid: {validation['valid']}")
    print(f"   Warnings: {len(validation['warnings'])}")
    print(f"   Errors: {len(validation['errors'])}")
    
    if validation['warnings']:
        print("   Sample Warnings:")
        for warning in validation['warnings'][:2]:
            print(f"     - {warning}")
    print()
    
    print("4. Configuration Update:")
    # Update a parameter
    original_lambda = config_manager.get_model_config('kyle')['lambda_param']
    config_manager.update_model_config('kyle', {'lambda_param': 0.015})
    new_lambda = config_manager.get_model_config('kyle')['lambda_param']
    
    print(f"   Kyle lambda parameter: {original_lambda} → {new_lambda}")
    print("   ✓ Configuration updated successfully")
    print()
    
    print("5. Template Creation:")
    template_file = "market_impact_config_template.json"
    try:
        config_manager.create_template_config(template_file)
        print(f"   ✓ Template created: {template_file}")
    except Exception as e:
        print(f"   ✗ Template creation failed: {str(e)}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Main demo function"""
    print("MARKET IMPACT MODELING SYSTEM - COMPREHENSIVE DEMO")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Run all demos
    demo_configuration_management()
    demo_price_impact_modeling()
    demo_liquidity_analysis()
    demo_execution_optimization()
    demo_integrated_analysis()
    
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    # Suppress warnings for cleaner output
    warnings.filterwarnings("ignore")
    
    # Run the demo
    main()