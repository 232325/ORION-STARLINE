"""
VWAP (Volume Weighted Average Price) Implementation

VWAP - Volume Weighted Average Price, bu market volume ga asoslangan
optimal execution strategiyasi hisoblanadi.

VWAP strategiyasi maqsadi: maqsadli vaqt davomida
market volume bo'yicha proportional ravishda trading qilib,
VWAP ga yaqin narxda execution qilish.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


@dataclass
class VWAPParameters:
    """VWAP parameters"""
    start_time: datetime
    end_time: datetime
    target_volume: float
    min_slice_size: float = 100
    max_slice_size: float = 10000
    participation_rate: float = 0.1  # % of market volume to participate
    aggressiveness: float = 0.5  # 0=passive, 1=aggressive


@dataclass
class VWAPExecution:
    """Individual VWAP execution details"""
    timestamp: datetime
    slice_size: float
    executed_price: float
    market_volume: float
    participation_rate: float
    cumulative_volume: float
    vwap_contribution: float


class VWAP:
    """
    Volume Weighted Average Price Strategy
    
    VWAP implementation with real-time adjustment va
    market conditions consideration
    """
    
    def __init__(self, parameters: VWAPParameters):
        """
        Initialize VWAP strategy
        
        Args:
            parameters: VWAP parameters
        """
        self.parameters = parameters
        self.execution_history = []
        self.remaining_volume = parameters.target_volume
        self.elapsed_time = 0.0
        self.total_time = (parameters.end_time - parameters.start_time).total_seconds()
        
        # Market data storage
        self.volume_profile = []
        self.price_levels = []
        
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
        # Time-based allocation
        time_remaining = (self.parameters.end_time - current_time).total_seconds()
        time_elapsed = (current_time - self.parameters.start_time).total_seconds()
        
        if time_remaining <= 0:
            return self.remaining_volume  # Execute all remaining
            
        # Volume remaining
        volume_remaining = self.remaining_volume
        
        # Base allocation: equal time distribution
        time_based_allocation = volume_remaining * (time_elapsed / self.total_time)
        base_slice = volume_remaining - time_based_allocation
        
        # Participation rate adjustment
        market_volume = market_conditions.get('avg_volume_per_minute', 1000)
        target_participation = self.parameters.participation_rate
        
        # Dynamic adjustment based on market conditions
        volatility = market_conditions.get('volatility', 0.02)
        spread = market_conditions.get('spread', 0.001)
        
        # Adjust participation for market conditions
        if volatility > 0.03:  # High volatility
            target_participation *= 0.8  # More passive
        if spread > 0.002:     # Wide spread
            target_participation *= 0.9  # Slightly more passive
            
        # Calculate slice size
        slice_size = max(self.parameters.min_slice_size,
                        min(self.parameters.max_slice_size,
                           target_participation * market_volume * 60))  # per minute
            
        # Ensure we don't exceed remaining volume
        slice_size = min(slice_size, volume_remaining)
        
        # Time urgency adjustment
        time_urgency = 1.0 + (1.0 - time_remaining / self.total_time) * 0.5
        slice_size *= time_urgency
        
        return min(slice_size, volume_remaining)
        
    def execute_slice(self, current_time: datetime,
                     market_conditions: Dict[str, float],
                     order_book: Dict[str, any] = None) -> VWAPExecution:
        """
        Execute a single slice according to VWAP strategy
        
        Args:
            current_time: Current time
            market_conditions: Current market conditions
            order_book: Current order book data
            
        Returns:
            VWAPExecution result
        """
        if self.remaining_volume <= 0:
            raise ValueError("No remaining volume to execute")
            
        # Calculate optimal slice
        slice_size = self.calculate_optimal_slice_size(current_time, market_conditions)
        
        # Get current market price
        if order_book and 'mid_price' in order_book:
            current_price = order_book['mid_price']
        elif 'current_price' in market_conditions:
            current_price = market_conditions['current_price']
        else:
            current_price = 100.0  # Default fallback
            
        # Apply execution price with slippage estimate
        volatility = market_conditions.get('volatility', 0.02)
        spread = market_conditions.get('spread', 0.001)
        
        # Calculate slippage based on slice size and market conditions
        participation = slice_size / (market_conditions.get('avg_volume_per_minute', 1000) * 60)
        slippage_estimate = (participation ** 0.5) * volatility + spread * 0.5
        
        # Aggressiveness adjustment
        aggressiveness = self.parameters.aggressiveness
        execution_price = current_price * (1 + slippage_estimate * aggressiveness)
        
        # Create execution record
        execution = VWAPExecution(
            timestamp=current_time,
            slice_size=slice_size,
            executed_price=execution_price,
            market_volume=market_conditions.get('volume_this_minute', 0),
            participation_rate=slice_size / (market_conditions.get('avg_volume_per_minute', 1000) * 60 + 1e-6),
            cumulative_volume=sum(ex.slice_size for ex in self.execution_history) + slice_size,
            vwap_contribution=slice_size * execution_price
        )
        
        # Update tracking
        self.execution_history.append(execution)
        self.remaining_volume -= slice_size
        
        return execution
        
    def calculate_current_vwap(self) -> float:
        """
        Current VWAP hisoblash
        
        Returns:
            Current VWAP price
        """
        if not self.execution_history:
            return 0.0
            
        total_volume = sum(ex.slice_size for ex in self.execution_history)
        total_value = sum(ex.vwap_contribution for ex in self.execution_history)
        
        return total_value / total_volume if total_volume > 0 else 0.0
        
    def compare_to_benchmark(self, benchmark_price: float) -> Dict[str, float]:
        """
        VWAP performance ni benchmark ga taqqoslash
        
        Args:
            benchmark_price: Benchmark price (e.g., day's VWAP)
            
        Returns:
            Performance comparison metrics
        """
        current_vwap = self.calculate_current_vwap()
        total_volume = sum(ex.slice_size for ex in self.execution_history)
        
        if total_volume == 0:
            return {}
            
        # Calculate metrics
        price_difference = current_vwap - benchmark_price
        percentage_difference = (price_difference / benchmark_price) * 100 if benchmark_price > 0 else 0
        
        # Cost calculation (assuming benchmark is good price)
        cost_vs_benchmark = price_difference * total_volume
        cost_bps = (price_difference / benchmark_price) * 10000 if benchmark_price > 0 else 0
        
        return {
            'current_vwap': current_vwap,
            'benchmark_price': benchmark_price,
            'price_difference': price_difference,
            'percentage_difference': percentage_difference,
            'total_cost': cost_vs_benchmark,
            'cost_bps': cost_bps,
            'execution_completion': (total_volume / self.parameters.target_volume) * 100
        }
        
    def calculate_market_impact(self, average_market_price: float) -> Dict[str, float]:
        """
        Market impact hisoblash
        
        Args:
            average_market_price: Average market price during execution
            
        Returns:
            Market impact analysis
        """
        current_vwap = self.calculate_current_vwap()
        
        if current_vwap == 0 or average_market_price == 0:
            return {}
            
        # Direct market impact vs average market price
        impact = current_vwap - average_market_price
        impact_percentage = (impact / average_market_price) * 100
        
        # Volume-weighted impact
        total_volume = sum(ex.slice_size for ex in self.execution_history)
        if total_volume == 0:
            return {}
            
        # Calculate impact by execution slice
        slice_impacts = []
        for execution in self.execution_history:
            slice_impact = (execution.executed_price - average_market_price) / average_market_price
            slice_impacts.append(slice_impact * execution.slice_size)
            
        weighted_impact = sum(slice_impacts) / total_volume
        
        return {
            'absolute_impact': impact,
            'percentage_impact': impact_percentage,
            'weighted_impact': weighted_impact * 100,
            'impact_trend': self._analyze_impact_trend(average_market_price)
        }
        
    def _analyze_impact_trend(self, average_market_price: float) -> Dict[str, any]:
        """Impact trend analysis"""
        if len(self.execution_history) < 2:
            return {}
            
        impacts = []
        for execution in self.execution_history:
            impact = (execution.executed_price - average_market_price) / average_market_price
            impacts.append(impact)
            
        # Simple trend analysis
        if len(impacts) > 1:
            trend_slope = np.polyfit(range(len(impacts)), impacts, 1)[0]
            return {
                'trend_slope': trend_slope,
                'trend_direction': 'increasing' if trend_slope > 0 else 'decreasing',
                'impact_volatility': np.std(impacts)
            }
            
        return {}
        
    def simulate_vwap_execution(self, market_data: pd.DataFrame,
                              simulation_time: int = 60) -> Dict[str, any]:
        """
        VWAP strategy simulation
        
        Args:
            market_data: Historical market data
            simulation_time: Simulation duration in minutes
            
        Returns:
            Simulation results
        """
        start_time = market_data.index[0] if hasattr(market_data.index[0], 'time') else datetime.now()
        
        # Reset for simulation
        sim_vwap = VWAP(self.parameters)
        sim_vwap.execution_history = []
        sim_vwap.remaining_volume = self.parameters.target_volume
        
        simulation_results = []
        
        for i in range(min(simulation_time, len(market_data))):
            if sim_vwap.remaining_volume <= 0:
                break
                
            current_time = start_time + timedelta(minutes=i)
            
            # Market conditions from data
            market_row = market_data.iloc[i]
            market_conditions = {
                'current_price': market_row.get('price', 100.0),
                'volume_this_minute': market_row.get('volume', 1000),
                'avg_volume_per_minute': market_data['volume'].rolling(window=10).mean().iloc[i] if 'volume' in market_data.columns else 1000,
                'volatility': 0.02,  # Default
                'spread': 0.001  # Default
            }
            
            # Execute slice
            try:
                execution = sim_vwap.execute_slice(current_time, market_conditions)
                simulation_results.append({
                    'time': current_time,
                    'slice_size': execution.slice_size,
                    'execution_price': execution.executed_price,
                    'participation_rate': execution.participation_rate,
                    'cumulative_volume': execution.cumulative_volume
                })
            except Exception as e:
                break
                
        # Calculate final results
        final_vwap = sim_vwap.calculate_current_vwap()
        execution_rate = (sim_vwap.parameters.target_volume - sim_vwap.remaining_volume) / sim_vwap.parameters.target_volume
        
        return {
            'simulation_results': simulation_results,
            'final_vwap': final_vwap,
            'execution_rate': execution_rate,
            'total_executions': len(simulation_results),
            'remaining_volume': sim_vwap.remaining_volume,
            'strategy_parameters': {
                'target_volume': self.parameters.target_volume,
                'participation_rate': self.parameters.participation_rate,
                'aggressiveness': self.parameters.aggressiveness
            }
        }
        
    def optimize_parameters(self, historical_data: pd.DataFrame,
                          optimization_objective: str = 'minimize_cost') -> Dict[str, any]:
        """
        VWAP parameters optimization
        
        Args:
            historical_data: Historical market data
            optimization_objective: 'minimize_cost' or 'minimize_impact'
            
        Returns:
            Optimization results
        """
        # Test different parameter combinations
        participation_rates = [0.05, 0.1, 0.15, 0.2]
        aggressiveness_levels = [0.3, 0.5, 0.7, 0.9]
        
        best_result = None
        best_score = float('inf')
        
        results = []
        
        for participation in participation_rates:
            for aggressiveness in aggressiveness_levels:
                # Create test parameters
                test_params = VWAPParameters(
                    start_time=self.parameters.start_time,
                    end_time=self.parameters.end_time,
                    target_volume=self.parameters.target_volume,
                    participation_rate=participation,
                    aggressiveness=aggressiveness
                )
                
                # Test strategy
                test_vwap = VWAP(test_params)
                simulation = test_vwap.simulate_vwap_execution(historical_data)
                
                # Calculate score
                if optimization_objective == 'minimize_cost':
                    # Cost vs benchmark
                    benchmark_price = historical_data['price'].mean() if 'price' in historical_data.columns else 100.0
                    score = abs(simulation['final_vwap'] - benchmark_price)
                else:
                    # Market impact (simplified)
                    score = simulation['execution_rate'] * 0.01  # Higher completion = lower impact
                    
                results.append({
                    'participation_rate': participation,
                    'aggressiveness': aggressiveness,
                    'final_vwap': simulation['final_vwap'],
                    'execution_rate': simulation['execution_rate'],
                    'score': score,
                    'simulation': simulation
                })
                
                if score < best_score:
                    best_score = score
                    best_result = results[-1]
                    
        return {
            'best_parameters': {
                'participation_rate': best_result['participation_rate'],
                'aggressiveness': best_result['aggressiveness']
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
        current_vwap = total_cost / total_volume if total_volume > 0 else 0
        
        # Calculate timing statistics
        start_time = self.execution_history[0].timestamp
        end_time = self.execution_history[-1].timestamp
        execution_duration = (end_time - start_time).total_seconds()
        
        # Participation rate statistics
        participation_rates = [ex.participation_rate for ex in self.execution_history]
        
        return {
            'status': 'Execution completed' if self.remaining_volume <= 0 else 'Execution in progress',
            'total_volume': total_volume,
            'remaining_volume': self.remaining_volume,
            'execution_progress': (total_volume / self.parameters.target_volume) * 100,
            'current_vwap': current_vwap,
            'total_cost': total_cost,
            'number_of_slices': len(self.execution_history),
            'execution_duration_minutes': execution_duration / 60,
            'average_slice_size': total_volume / len(self.execution_history),
            'participation_stats': {
                'mean': np.mean(participation_rates),
                'std': np.std(participation_rates),
                'min': np.min(participation_rates),
                'max': np.max(participation_rates)
            },
            'time_window': {
                'start': self.parameters.start_time,
                'end': self.parameters.end_time,
                'total_planned_minutes': self.total_time / 60
            }
        }
        
    def generate_execution_report(self, benchmark_price: float = None) -> str:
        """
        VWAP execution report generation
        
        Args:
            benchmark_price: Optional benchmark price for comparison
            
        Returns:
            Formatted execution report
        """
        report = []
        summary = self.get_execution_summary()
        
        report.append("=== VWAP EXECUTION REPORT ===")
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
        
        # VWAP results
        report.append("VWAP RESULTS:")
        report.append(f"  Current VWAP: {summary.get('current_vwap', 0):.4f}")
        report.append(f"  Total Cost: {summary.get('total_cost', 0):,.2f}")
        report.append(f"  Number of Slices: {summary.get('number_of_slices', 0)}")
        report.append(f"  Average Slice Size: {summary.get('average_slice_size', 0):,.0f}")
        report.append("")
        
        # Participation statistics
        if 'participation_stats' in summary:
            p_stats = summary['participation_stats']
            report.append("PARTICIPATION RATE:")
            report.append(f"  Mean: {p_stats['mean']:.3f}")
            report.append(f"  Std Dev: {p_stats['std']:.3f}")
            report.append(f"  Range: [{p_stats['min']:.3f}, {p_stats['max']:.3f}]")
            report.append("")
            
        # Benchmark comparison
        if benchmark_price:
            comparison = self.compare_to_benchmark(benchmark_price)
            if comparison:
                report.append("BENCHMARK COMPARISON:")
                report.append(f"  Benchmark Price: {benchmark_price:.4f}")
                report.append(f"  Price Difference: {comparison['price_difference']:.4f}")
                report.append(f"  Cost vs Benchmark: {comparison['cost_bps']:.1f} bps")
                report.append("")
                
        # Strategy parameters
        report.append("STRATEGY PARAMETERS:")
        report.append(f"  Participation Rate: {self.parameters.participation_rate:.1%}")
        report.append(f"  Aggressiveness: {self.parameters.aggressiveness:.1%}")
        report.append(f"  Min Slice Size: {self.parameters.min_slice_size:,.0f}")
        report.append(f"  Max Slice Size: {self.parameters.max_slice_size:,.0f}")
        
        return "\n".join(report)