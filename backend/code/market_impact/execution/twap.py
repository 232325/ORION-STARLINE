"""
TWAP (Time Weighted Average Price) Implementation

TWAP - Time Weighted Average Price, bu vaqt ga asoslangan
optimal execution strategiyasi hisoblanadi.

TWAP strategiyasi maqsadi: maqsadli vaqt davomida
equal intervals da trading qilish, shunday qilib
time-weighted average price ga yetishish.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from scipy import stats


@dataclass
class TWAPParameters:
    """TWAP parameters"""
    start_time: datetime
    end_time: datetime
    target_volume: float
    slice_frequency: int = 60  # seconds between slices
    min_slice_size: float = 100
    max_slice_size: float = 5000
    volume_variance_tolerance: float = 0.2  # Allowable variance in slice sizes


@dataclass
class TWAPExecution:
    """Individual TWAP execution details"""
    timestamp: datetime
    slice_size: float
    executed_price: float
    time_elapsed: float
    volume_cumulative: float
    twap_contribution: float
    market_impact: float


class TWAP:
    """
    Time Weighted Average Price Strategy
    
    TWAP implementation with time-based execution scheduling
    va market conditions consideration
    """
    
    def __init__(self, parameters: TWAPParameters):
        """
        Initialize TWAP strategy
        
        Args:
            parameters: TWAP parameters
        """
        self.parameters = parameters
        self.execution_history = []
        self.remaining_volume = parameters.target_volume
        self.last_execution_time = parameters.start_time
        self.target_intervals = self._calculate_target_intervals()
        
        # Execution tracking
        self.execution_schedule = []
        self.current_interval = 0
        
    def _calculate_target_intervals(self) -> List[datetime]:
        """Calculate target execution intervals"""
        intervals = []
        current_time = self.parameters.start_time
        
        while current_time < self.parameters.end_time:
            intervals.append(current_time)
            current_time += timedelta(seconds=self.parameters.slice_frequency)
            
        return intervals
        
    def calculate_optimal_slice_size(self, current_time: datetime,
                                   market_conditions: Dict[str, float]) -> float:
        """
        Optimal slice size hisoblash
        
        Args:
            current_time: Current time
            market_conditions: Current market conditions
            
        Returns:
            Optimal slice size
        """
        time_elapsed = (current_time - self.parameters.start_time).total_seconds()
        total_duration = (self.parameters.end_time - self.parameters.start_time).total_seconds()
        
        # Time-based allocation (equal time distribution)
        time_based_allocation = self.parameters.target_volume * (time_elapsed / total_duration)
        
        # Volume remaining
        volume_executed = sum(ex.slice_size for ex in self.execution_history)
        volume_remaining = self.parameters.target_volume - volume_executed
        
        # Base slice size
        base_slice = max(volume_remaining - time_based_allocation, 0) + time_based_allocation / (len(self.target_intervals) - self.current_interval + 1)
        
        # Market conditions adjustment
        volatility = market_conditions.get('volatility', 0.02)
        spread = market_conditions.get('spread', 0.001)
        liquidity = market_conditions.get('liquidity_score', 0.5)
        
        # Adjust slice size based on market conditions
        if volatility > 0.03:  # High volatility - smaller slices
            base_slice *= 0.8
        if spread > 0.002:     # Wide spread - more conservative
            base_slice *= 0.9
        if liquidity < 0.3:    # Low liquidity - smaller slices
            base_slice *= 0.7
            
        # Time pressure adjustment (if we're behind schedule)
        expected_executions = time_elapsed / self.parameters.slice_frequency
        actual_executions = len(self.execution_history)
        
        if actual_executions < expected_executions * 0.8:  # Behind schedule
            # Increase slice size to catch up
            catch_up_factor = 1.2
            base_slice *= catch_up_factor
            
        # Ensure slice size is within bounds
        slice_size = max(self.parameters.min_slice_size,
                        min(self.parameters.max_slice_size, base_slice))
        
        # Don't exceed remaining volume
        slice_size = min(slice_size, volume_remaining)
        
        return slice_size
        
    def execute_slice(self, current_time: datetime,
                     market_conditions: Dict[str, float],
                     order_book: Dict[str, any] = None) -> TWAPExecution:
        """
        Execute a single slice according to TWAP strategy
        
        Args:
            current_time: Current time
            market_conditions: Current market conditions
            order_book: Current order book data
            
        Returns:
            TWAPExecution result
        """
        if self.remaining_volume <= 0:
            raise ValueError("No remaining volume to execute")
            
        # Calculate time elapsed
        time_elapsed = (current_time - self.parameters.start_time).total_seconds()
        
        # Calculate optimal slice
        slice_size = self.calculate_optimal_slice_size(current_time, market_conditions)
        
        # Get current market price
        if order_book and 'mid_price' in order_book:
            current_price = order_book['mid_price']
        elif 'current_price' in market_conditions:
            current_price = market_conditions['current_price']
        else:
            current_price = 100.0  # Default fallback
            
        # Calculate execution price with market impact
        volatility = market_conditions.get('volatility', 0.02)
        spread = market_conditions.get('spread', 0.001)
        
        # Time-based impact (TWAP typically has lower impact than VWAP)
        time_pressure = time_elapsed / ((self.parameters.end_time - self.parameters.start_time).total_seconds())
        
        # Slippage estimation
        base_slippage = spread * 0.5  # TWAP is usually more passive
        impact_factor = (slice_size / 1000) ** 0.7 * volatility  # Market impact
        time_factor = time_pressure * 0.1  # Time pressure factor
        
        total_slippage = base_slippage + impact_factor + time_factor
        
        execution_price = current_price * (1 + total_slippage)
        
        # Calculate market impact vs reference price
        reference_price = market_conditions.get('reference_price', current_price)
        market_impact = (execution_price - reference_price) / reference_price
        
        # Create execution record
        execution = TWAPExecution(
            timestamp=current_time,
            slice_size=slice_size,
            executed_price=execution_price,
            time_elapsed=time_elapsed,
            volume_cumulative=sum(ex.slice_size for ex in self.execution_history) + slice_size,
            twap_contribution=slice_size * execution_price,
            market_impact=market_impact
        )
        
        # Update tracking
        self.execution_history.append(execution)
        self.remaining_volume -= slice_size
        self.current_interval += 1
        self.last_execution_time = current_time
        
        return execution
        
    def calculate_current_twap(self) -> float:
        """
        Current TWAP hisoblash
        
        Returns:
            Current TWAP price
        """
        if not self.execution_history:
            return 0.0
            
        total_volume = sum(ex.slice_size for ex in self.execution_history)
        total_value = sum(ex.twap_contribution for ex in self.execution_history)
        
        return total_value / total_volume if total_volume > 0 else 0.0
        
    def compare_to_benchmark(self, benchmark_prices: List[float],
                           time_weights: List[float] = None) -> Dict[str, float]:
        """
        TWAP performance ni benchmark ga taqqoslash
        
        Args:
            benchmark_prices: Benchmark prices over time
            time_weights: Optional time weights for benchmark calculation
            
        Returns:
            Performance comparison metrics
        """
        current_twap = self.calculate_current_twap()
        total_volume = sum(ex.slice_size for ex in self.execution_history)
        
        if not benchmark_prices:
            return {}
            
        # Calculate benchmark TWAP
        if time_weights:
            # Weighted benchmark TWAP
            benchmark_twap = sum(price * weight for price, weight in zip(benchmark_prices, time_weights))
        else:
            # Simple average benchmark TWAP
            benchmark_twap = np.mean(benchmark_prices)
            
        # Calculate performance metrics
        price_difference = current_twap - benchmark_twap
        percentage_difference = (price_difference / benchmark_twap) * 100 if benchmark_twap > 0 else 0
        
        # Cost metrics
        cost_vs_benchmark = price_difference * total_volume
        cost_bps = (price_difference / benchmark_twap) * 10000 if benchmark_twap > 0 else 0
        
        # Execution timing
        total_planned_time = (self.parameters.end_time - self.parameters.start_time).total_seconds()
        actual_executions = len(self.execution_history)
        expected_executions = total_planned_time / self.parameters.slice_frequency
        timing_accuracy = actual_executions / expected_executions if expected_executions > 0 else 0
        
        return {
            'current_twap': current_twap,
            'benchmark_twap': benchmark_twap,
            'price_difference': price_difference,
            'percentage_difference': percentage_difference,
            'total_cost': cost_vs_benchmark,
            'cost_bps': cost_bps,
            'execution_completion': (total_volume / self.parameters.target_volume) * 100,
            'timing_accuracy': timing_accuracy * 100,
            'number_of_executions': actual_executions
        }
        
    def analyze_execution_timing(self) -> Dict[str, any]:
        """
        Execution timing analysis
        
        Returns:
            Timing analysis metrics
        """
        if len(self.execution_history) < 2:
            return {}
            
        # Calculate execution intervals
        intervals = []
        for i in range(1, len(self.execution_history)):
            interval = (self.execution_history[i].timestamp - 
                       self.execution_history[i-1].timestamp).total_seconds()
            intervals.append(interval)
            
        # Compare to target frequency
        target_frequency = self.parameters.slice_frequency
        interval_variance = np.var(intervals) if intervals else 0
        
        # Timing accuracy
        total_time = (self.execution_history[-1].timestamp - 
                     self.execution_history[0].timestamp).total_seconds()
        actual_frequency = total_time / len(intervals) if intervals else 0
        
        return {
            'target_frequency': target_frequency,
            'actual_frequency': actual_frequency,
            'frequency_accuracy': (target_frequency / actual_frequency) * 100 if actual_frequency > 0 else 0,
            'interval_variance': interval_variance,
            'timing_regularity': 1.0 / (1.0 + interval_variance / target_frequency),
            'execution_punctuality': self._calculate_punctuality()
        }
        
    def _calculate_punctuality(self) -> float:
        """Calculate execution punctuality score"""
        if not self.execution_history or len(self.target_intervals) == 0:
            return 0.0
            
        punctuality_scores = []
        
        for i, execution in enumerate(self.execution_history):
            if i < len(self.target_intervals):
                target_time = self.target_intervals[i]
                actual_time = execution.timestamp
                
                # Calculate time difference (in seconds)
                time_diff = abs((actual_time - target_time).total_seconds())
                
                # Convert to punctuality score (0-1)
                max_acceptable_diff = self.parameters.slice_frequency * 0.5  # 50% tolerance
                punctuality = max(0, 1 - time_diff / max_acceptable_diff)
                punctuality_scores.append(punctuality)
                
        return np.mean(punctuality_scores) if punctuality_scores else 0.0
        
    def calculate_volume_distribution_accuracy(self) -> Dict[str, float]:
        """
        Volume distribution accuracy analysis
        
        Returns:
            Volume distribution metrics
        """
        if not self.execution_history:
            return {}
            
        # Expected volume per interval
        total_time = (self.parameters.end_time - self.parameters.start_time).total_seconds()
        intervals_count = len(self.target_intervals)
        expected_volume_per_interval = self.parameters.target_volume / intervals_count
        
        # Actual volumes
        actual_volumes = [ex.slice_size for ex in self.execution_history]
        
        # Calculate variance metrics
        volume_variance = np.var(actual_volumes)
        volume_std = np.std(actual_volumes)
        coefficient_of_variation = volume_std / np.mean(actual_volumes) if np.mean(actual_volumes) > 0 else 0
        
        # Distribution smoothness
        smoothness_score = 1.0 / (1.0 + coefficient_of_variation)
        
        return {
            'expected_volume_per_interval': expected_volume_per_interval,
            'mean_actual_volume': np.mean(actual_volumes),
            'volume_variance': volume_variance,
            'volume_std': volume_std,
            'coefficient_of_variation': coefficient_of_variation,
            'distribution_smoothness': smoothness_score,
            'tolerance_adherence': 1.0 if coefficient_of_variation < self.parameters.volume_variance_tolerance else 0.0
        }
        
    def simulate_twap_execution(self, market_data: pd.DataFrame,
                              simulation_time_minutes: int = 60) -> Dict[str, any]:
        """
        TWAP strategy simulation
        
        Args:
            market_data: Historical market data
            simulation_time_minutes: Simulation duration in minutes
            
        Returns:
            Simulation results
        """
        start_time = market_data.index[0] if hasattr(market_data.index[0], 'time') else datetime.now()
        
        # Reset for simulation
        sim_twap = TWAP(self.parameters)
        sim_twap.execution_history = []
        sim_twap.remaining_volume = self.parameters.target_volume
        
        simulation_results = []
        current_sim_time = start_time
        execution_count = 0
        
        # Simulate until we run out of volume or reach time limit
        while (sim_twap.remaining_volume > 0 and 
               execution_count < simulation_time_minutes * 60 / self.parameters.slice_frequency):
            
            # Market conditions from data
            if execution_count < len(market_data):
                market_row = market_data.iloc[execution_count]
                market_conditions = {
                    'current_price': market_row.get('price', 100.0),
                    'reference_price': market_row.get('price', 100.0),
                    'volatility': 0.02,
                    'spread': 0.001,
                    'liquidity_score': 0.5
                }
            else:
                break
                
            # Execute slice
            try:
                execution = sim_twap.execute_slice(current_sim_time, market_conditions)
                simulation_results.append({
                    'time': current_sim_time,
                    'slice_size': execution.slice_size,
                    'execution_price': execution.executed_price,
                    'time_elapsed': execution.time_elapsed,
                    'cumulative_volume': execution.volume_cumulative,
                    'market_impact': execution.market_impact
                })
                
                # Advance time
                current_sim_time += timedelta(seconds=self.parameters.slice_frequency)
                execution_count += 1
                
            except Exception as e:
                break
                
        # Calculate final results
        final_twap = sim_twap.calculate_current_twap()
        execution_rate = (self.parameters.target_volume - sim_twap.remaining_volume) / self.parameters.target_volume
        
        return {
            'simulation_results': simulation_results,
            'final_twap': final_twap,
            'execution_rate': execution_rate,
            'total_executions': len(simulation_results),
            'remaining_volume': sim_twap.remaining_volume,
            'timing_analysis': sim_twap.analyze_execution_timing(),
            'volume_distribution': sim_twap.calculate_volume_distribution_accuracy()
        }
        
    def optimize_parameters(self, historical_data: pd.DataFrame,
                          optimization_objective: str = 'minimize_cost') -> Dict[str, any]:
        """
        TWAP parameters optimization
        
        Args:
            historical_data: Historical market data
            optimization_objective: 'minimize_cost' or 'maximize_timing_accuracy'
            
        Returns:
            Optimization results
        """
        # Test different parameter combinations
        slice_frequencies = [30, 60, 120, 300]  # seconds
        min_slice_sizes = [50, 100, 200]
        max_slice_sizes = [2000, 5000, 10000]
        
        best_result = None
        best_score = float('inf') if optimization_objective == 'minimize_cost' else 0
        
        results = []
        
        for frequency in slice_frequencies:
            for min_size in min_slice_sizes:
                for max_size in max_slice_sizes:
                    if min_size >= max_size:
                        continue
                        
                    # Create test parameters
                    test_params = TWAPParameters(
                        start_time=self.parameters.start_time,
                        end_time=self.parameters.end_time,
                        target_volume=self.parameters.target_volume,
                        slice_frequency=frequency,
                        min_slice_size=min_size,
                        max_slice_size=max_size
                    )
                    
                    # Test strategy
                    test_twap = TWAP(test_params)
                    simulation = test_twap.simulate_twap_execution(historical_data)
                    
                    # Calculate score
                    if optimization_objective == 'minimize_cost':
                        # Cost vs benchmark
                        benchmark_price = historical_data['price'].mean() if 'price' in historical_data.columns else 100.0
                        score = abs(simulation['final_twap'] - benchmark_price)
                    else:
                        # Timing accuracy
                        timing_analysis = simulation.get('timing_analysis', {})
                        score = timing_analysis.get('timing_accuracy', 0)
                        
                    results.append({
                        'slice_frequency': frequency,
                        'min_slice_size': min_size,
                        'max_slice_size': max_size,
                        'final_twap': simulation['final_twap'],
                        'execution_rate': simulation['execution_rate'],
                        'score': score,
                        'simulation': simulation
                    })
                    
                    if ((optimization_objective == 'minimize_cost' and score < best_score) or
                        (optimization_objective == 'maximize_timing_accuracy' and score > best_score)):
                        best_score = score
                        best_result = results[-1]
                    
        return {
            'best_parameters': {
                'slice_frequency': best_result['slice_frequency'],
                'min_slice_size': best_result['min_slice_size'],
                'max_slice_size': best_result['max_slice_size']
            },
            'best_score': best_score,
            'optimization_results': results,
            'objective': optimization_objective
        }
        
    def get_execution_summary(self) -> Dict[str, any]:
        """
        Execution summary
        
        Returns:
            Complete execution summary
        """
        if not self.execution_history:
            return {
                'status': 'No executions completed',
                'remaining_volume': self.remaining_volume
            }
            
        total_volume = sum(ex.slice_size for ex in self.execution_history)
        total_cost = sum(ex.slice_size * ex.executed_price for ex in self.execution_history)
        current_twap = total_cost / total_volume if total_volume > 0 else 0
        
        # Timing statistics
        timing_analysis = self.analyze_execution_timing()
        volume_distribution = self.calculate_volume_distribution_accuracy()
        
        # Market impact statistics
        market_impacts = [ex.market_impact for ex in self.execution_history]
        
        return {
            'status': 'Execution completed' if self.remaining_volume <= 0 else 'Execution in progress',
            'total_volume': total_volume,
            'remaining_volume': self.remaining_volume,
            'execution_progress': (total_volume / self.parameters.target_volume) * 100,
            'current_twap': current_twap,
            'total_cost': total_cost,
            'number_of_slices': len(self.execution_history),
            'timing_analysis': timing_analysis,
            'volume_distribution': volume_distribution,
            'market_impact_stats': {
                'mean_impact': np.mean(market_impacts) if market_impacts else 0,
                'impact_volatility': np.std(market_impacts) if market_impacts else 0,
                'max_impact': np.max(market_impacts) if market_impacts else 0,
                'min_impact': np.min(market_impacts) if market_impacts else 0
            },
            'time_window': {
                'start': self.parameters.start_time,
                'end': self.parameters.end_time,
                'planned_intervals': len(self.target_intervals)
            }
        }
        
    def generate_execution_report(self, benchmark_price: float = None) -> str:
        """
        TWAP execution report generation
        
        Args:
            benchmark_price: Optional benchmark price for comparison
            
        Returns:
            Formatted execution report
        """
        report = []
        summary = self.get_execution_summary()
        
        report.append("=== TWAP EXECUTION REPORT ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Status: {summary['status']}")
        report.append("")
        
        # Execution progress
        report.append("EXECUTION PROGRESS:")
        report.append(f"  Target Volume: {self.parameters.target_volume:,.0f}")
        report.append(f"  Executed Volume: {summary.get('total_volume', 0):,.0f}")
        report.append(f"  Progress: {summary.get('execution_progress', 0):.1f}%")
        report.append(f"  Remaining: {summary.get('remaining_volume', 0):,.0f}")
        report.append("")
        
        # TWAP results
        report.append("TWAP RESULTS:")
        report.append(f"  Current TWAP: {summary.get('current_twap', 0):.4f}")
        report.append(f"  Total Cost: {summary.get('total_cost', 0):,.2f}")
        report.append(f"  Number of Slices: {summary.get('number_of_slices', 0)}")
        report.append("")
        
        # Timing analysis
        if 'timing_analysis' in summary:
            timing = summary['timing_analysis']
            report.append("TIMING ANALYSIS:")
            report.append(f"  Target Frequency: {timing.get('target_frequency', 0):.0f} seconds")
            report.append(f"  Actual Frequency: {timing.get('actual_frequency', 0):.0f} seconds")
            report.append(f"  Timing Accuracy: {timing.get('timing_accuracy', 0):.1f}%")
            report.append(f"  Punctuality Score: {timing.get('execution_punctuality', 0):.2f}")
            report.append("")
            
        # Volume distribution
        if 'volume_distribution' in summary:
            volume_dist = summary['volume_distribution']
            report.append("VOLUME DISTRIBUTION:")
            report.append(f"  Expected Volume/Interval: {volume_dist.get('expected_volume_per_interval', 0):,.0f}")
            report.append(f"  Mean Actual Volume: {volume_dist.get('mean_actual_volume', 0):,.0f}")
            report.append(f"  Distribution Smoothness: {volume_dist.get('distribution_smoothness', 0):.2f}")
            report.append("")
            
        # Market impact
        if 'market_impact_stats' in summary:
            impact_stats = summary['market_impact_stats']
            report.append("MARKET IMPACT:")
            report.append(f"  Mean Impact: {impact_stats.get('mean_impact', 0):.4f}")
            report.append(f"  Impact Volatility: {impact_stats.get('impact_volatility', 0):.4f}")
            report.append(f"  Max Impact: {impact_stats.get('max_impact', 0):.4f}")
            report.append("")
            
        # Benchmark comparison
        if benchmark_price:
            comparison = self.compare_to_benchmark([benchmark_price])
            if comparison:
                report.append("BENCHMARK COMPARISON:")
                report.append(f"  Benchmark Price: {benchmark_price:.4f}")
                report.append(f"  Price Difference: {comparison['price_difference']:.4f}")
                report.append(f"  Cost vs Benchmark: {comparison['cost_bps']:.1f} bps")
                report.append("")
                
        # Strategy parameters
        report.append("STRATEGY PARAMETERS:")
        report.append(f"  Slice Frequency: {self.parameters.slice_frequency} seconds")
        report.append(f"  Min Slice Size: {self.parameters.min_slice_size:,.0f}")
        report.append(f"  Max Slice Size: {self.parameters.max_slice_size:,.0f}")
        report.append(f"  Volume Variance Tolerance: {self.parameters.volume_variance_tolerance:.1%}")
        
        return "\n".join(report)