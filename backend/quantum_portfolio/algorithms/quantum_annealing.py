"""
Quantum Annealing Optimizer
============================

Quantum annealing algoritmi yordamida portfolio optimizatsiya.
Bu modul quantum annealing printsiplarini portfolio optimizatsiya uchun qo'llaydi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
import logging
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import random

class QuantumAnnealingOptimizer:
    """
    Quantum Annealing Portfolio Optimizer
    """
    
    def __init__(self, 
                 quantum_portfolio_theory,
                 initial_temperature: float = 1000.0,
                 cooling_rate: float = 0.995,
                 min_temperature: float = 0.01,
                 max_iterations: int = 10000,
                 quantum_entanglement_strength: float = 0.1):
        """
        Initialize quantum annealing optimizer
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
            initial_temperature: Initial annealing temperature
            cooling_rate: Cooling rate (0-1)
            min_temperature: Minimum temperature
            max_iterations: Maximum iterations
            quantum_entanglement_strength: Quantum entanglement strength
        """
        self.qpt = quantum_portfolio_theory
        
        # Annealing parameters
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        self.max_iterations = max_iterations
        self.quantum_entanglement_strength = quantum_entanglement_strength
        
        # Current state
        self.current_solution = None
        self.current_cost = float('inf')
        self.best_solution = None
        self.best_cost = float('inf')
        
        # Temperature schedule
        self.temperature_schedule = []
        
        # Solution history
        self.solution_history = []
        self.cost_history = []
        
        self.logger = logging.getLogger(__name__)
    
    def optimize(self, 
                objective_function: Callable,
                constraints: Optional[List[Dict]] = None,
                bounds: Optional[List[Tuple]] = None,
                initial_solution: Optional[np.ndarray] = None,
                quantum_enhancement: bool = True) -> Dict:
        """
        Quantum annealing optimization
        
        Args:
            objective_function: Objective function to minimize
            constraints: Optimization constraints
            bounds: Variable bounds
            initial_solution: Initial solution guess
            quantum_enhancement: Use quantum enhancements
            
        Returns:
            Optimization results
        """
        n_assets = len(self.qpt.assets)
        
        # Initialize solution
        if initial_solution is None:
            initial_solution = np.ones(n_assets) / n_assets
        
        self.current_solution = initial_solution.copy()
        self.current_cost = objective_function(self.current_solution)
        
        self.best_solution = self.current_solution.copy()
        self.best_cost = self.current_cost
        
        # Initialize temperature
        temperature = self.initial_temperature
        
        # Solution tracking
        accepted_moves = 0
        total_moves = 0
        
        # Main annealing loop
        for iteration in range(self.max_iterations):
            # Generate neighbor solution
            neighbor_solution = self._generate_neighbor(self.current_solution, temperature)
            
            # Apply constraints if provided
            if constraints or bounds:
                neighbor_solution = self._apply_constraints(neighbor_solution, constraints, bounds)
            
            # Calculate neighbor cost
            neighbor_cost = objective_function(neighbor_solution)
            
            # Quantum enhancement (tunneling effect)
            if quantum_enhancement:
                neighbor_cost = self._apply_quantum_tunneling(neighbor_cost, self.current_cost, temperature)
            
            # Accept or reject move
            if self._accept_move(self.current_cost, neighbor_cost, temperature):
                self.current_solution = neighbor_solution
                self.current_cost = neighbor_cost
                accepted_moves += 1
                
                # Update best solution
                if self.current_cost < self.best_cost:
                    self.best_solution = self.current_solution.copy()
                    self.best_cost = self.current_cost
            
            total_moves += 1
            
            # Record history
            self.solution_history.append(self.current_solution.copy())
            self.cost_history.append(self.current_cost)
            self.temperature_schedule.append(temperature)
            
            # Cool down
            temperature = self._cool_down(temperature)
            
            # Early stopping
            if temperature <= self.min_temperature:
                break
            
            # Progress logging
            if iteration % 1000 == 0:
                acceptance_rate = accepted_moves / total_moves
                self.logger.info(f"Iteration {iteration}: Cost={self.current_cost:.6f}, "
                               f"Temperature={temperature:.4f}, Acceptance={acceptance_rate:.3f}")
        
        # Final results
        return {
            'best_solution': self.best_solution,
            'best_cost': self.best_cost,
            'final_solution': self.current_solution,
            'final_cost': self.current_cost,
            'total_iterations': iteration + 1,
            'acceptance_rate': accepted_moves / total_moves,
            'final_temperature': temperature,
            'solution_history': self.solution_history,
            'cost_history': self.cost_history,
            'temperature_schedule': self.temperature_schedule,
            'quantum_enhancement': quantum_enhancement
        }
    
    def _generate_neighbor(self, current_solution: np.ndarray, temperature: float) -> np.ndarray:
        """
        Generate neighbor solution using quantum-inspired moves
        """
        neighbor = current_solution.copy()
        n_assets = len(neighbor)
        
        # Quantum move selection based on temperature
        if temperature > 0.5 * self.initial_temperature:
            # High temperature: larger moves
            move_type = random.choice(['single_swap', 'small_rebalance', 'quantum_superposition'])
        elif temperature > 0.1 * self.initial_temperature:
            # Medium temperature: moderate moves
            move_type = random.choice(['single_swap', 'small_rebalance'])
        else:
            # Low temperature: fine-tuning
            move_type = 'small_rebalance'
        
        if move_type == 'single_swap':
            # Swap weights between two assets
            i, j = random.sample(range(n_assets), 2)
            swap_amount = random.uniform(0, 0.1) * temperature / self.initial_temperature
            
            if neighbor[i] >= swap_amount:
                neighbor[i] -= swap_amount
                neighbor[j] += swap_amount
        
        elif move_type == 'small_rebalance':
            # Small rebalancing
            rebalance_strength = 0.05 * temperature / self.initial_temperature
            change = np.random.normal(0, rebalance_strength, n_assets)
            neighbor += change
            
            # Normalize to maintain budget constraint
            neighbor = np.maximum(0, neighbor)  # Ensure non-negative
            neighbor = neighbor / np.sum(neighbor)  # Normalize
            
        elif move_type == 'quantum_superposition':
            # Quantum-inspired superposition move
            # Create superposition of multiple solutions
            num_superpositions = random.randint(2, 4)
            superposition_weights = []
            
            for _ in range(num_superpositions):
                temp_solution = current_solution.copy()
                # Random perturbation
                temp_solution += np.random.normal(0, 0.1 * temperature / self.initial_temperature, n_assets)
                temp_solution = np.maximum(0, temp_solution)
                temp_solution = temp_solution / np.sum(temp_solution)
                superposition_weights.append(temp_solution)
            
            # Create weighted average
            weights = np.random.dirichlet(np.ones(num_superpositions))
            neighbor = sum(w * sol for w, sol in zip(weights, superposition_weights))
        
        return neighbor
    
    def _apply_constraints(self, 
                          solution: np.ndarray, 
                          constraints: Optional[List[Dict]] = None,
                          bounds: Optional[List[Tuple]] = None) -> np.ndarray:
        """Apply optimization constraints"""
        constrained_solution = solution.copy()
        
        # Apply bounds
        if bounds:
            for i, (lower, upper) in enumerate(bounds):
                constrained_solution[i] = np.clip(constrained_solution[i], lower, upper)
        
        # Normalize to maintain budget constraint
        if np.sum(constrained_solution) > 0:
            constrained_solution = constrained_solution / np.sum(constrained_solution)
        
        # Apply custom constraints
        if constraints:
            # This is a simplified constraint handling
            # In practice, more sophisticated constraint projection methods would be used
            for constraint in constraints:
                if constraint['type'] == 'eq':
                    # Equality constraint - scale to satisfy
                    if 'fun' in constraint:
                        target = constraint['fun'](constrained_solution)
                        if abs(target) > 1e-6:
                            # Simple scaling approach
                            constrained_solution *= (1 + target)
                            constrained_solution = np.maximum(0, constrained_solution)
                            constrained_solution = constrained_solution / np.sum(constrained_solution)
        
        return constrained_solution
    
    def _apply_quantum_tunneling(self, neighbor_cost: float, current_cost: float, temperature: float) -> float:
        """
        Apply quantum tunneling effect
        Quantum tunneling allows overcoming energy barriers
        """
        # Tunneling probability based on energy difference and quantum entanglement
        energy_barrier = abs(neighbor_cost - current_cost)
        tunneling_probability = np.exp(-energy_barrier / (temperature + 1e-8))
        
        # Apply quantum entanglement enhancement
        entanglement_factor = 1 + self.quantum_entanglement_strength * tunneling_probability
        
        # Quantum tunneling effect
        if np.random.random() < tunneling_probability:
            # Allow tunneling through energy barrier
            effective_cost = min(neighbor_cost, current_cost) * entanglement_factor
        else:
            effective_cost = neighbor_cost
        
        return effective_cost
    
    def _accept_move(self, current_cost: float, neighbor_cost: float, temperature: float) -> bool:
        """
        Determine if move should be accepted using quantum annealing acceptance criterion
        """
        if neighbor_cost < current_cost:
            return True
        
        # Quantum-enhanced acceptance probability
        delta_cost = neighbor_cost - current_cost
        acceptance_probability = np.exp(-delta_cost / (temperature + 1e-8))
        
        # Add quantum coherence effect
        quantum_coherence = self._calculate_quantum_coherence_factor(temperature)
        acceptance_probability *= (1 + quantum_coherence * 0.1)
        
        return np.random.random() < acceptance_probability
    
    def _calculate_quantum_coherence_factor(self, temperature: float) -> float:
        """Calculate quantum coherence factor based on temperature"""
        # Quantum coherence is higher at lower temperatures
        coherence_factor = 1 - (temperature / self.initial_temperature)
        return max(0, coherence_factor)
    
    def _cool_down(self, temperature: float) -> float:
        """Cooling schedule"""
        # Exponential cooling
        new_temperature = temperature * self.cooling_rate
        return max(new_temperature, self.min_temperature)
    
    def optimize_portfolio(self, 
                          target_return: Optional[float] = None,
                          risk_aversion: float = 1.0,
                          max_iterations: Optional[int] = None,
                          quantum_enhancement: bool = True) -> Dict:
        """
        Portfolio-specific optimization
        
        Args:
            target_return: Target portfolio return
            risk_aversion: Risk aversion parameter
            max_iterations: Maximum iterations (override default)
            quantum_enhancement: Use quantum enhancements
            
        Returns:
            Portfolio optimization results
        """
        if self.qpt.covariance_matrix is None:
            raise ValueError("Portfolio ma'lumotlari yuklanmagan")
        
        # Set custom iterations if provided
        if max_iterations:
            self.max_iterations = max_iterations
        
        # Define objective function
        def portfolio_objective(weights):
            expected_returns = self.qpt._quantum_expected_returns()
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
            
            # Base mean-variance utility
            utility = portfolio_return - 0.5 * risk_aversion * portfolio_variance
            
            # Quantum enhancements
            quantum_entropy = self.qpt._calculate_quantum_entropy(weights)
            quantum_coherence = self.qpt._calculate_quantum_coherence(weights)
            
            # Return penalty if target return specified
            return_penalty = 0
            if target_return is not None and portfolio_return < target_return:
                return_penalty = (target_return - portfolio_return) ** 2
            
            return -(utility + quantum_entropy * 0.1 + quantum_coherence * 0.05 - return_penalty)
        
        # Define constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
        ]
        
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda w: np.sum(w * self.qpt._quantum_expected_returns()) - target_return
            })
        
        # Bounds (no short selling)
        bounds = [(0, 1) for _ in range(len(self.qpt.assets))]
        
        # Initial solution
        initial_solution = np.ones(len(self.qpt.assets)) / len(self.qpt.assets)
        
        # Run optimization
        results = self.optimize(
            objective_function=portfolio_objective,
            constraints=constraints,
            bounds=bounds,
            initial_solution=initial_solution,
            quantum_enhancement=quantum_enhancement
        )
        
        # Format results
        if results['optimization_status'] == 'success':
            weights = results['best_solution']
            
            # Calculate portfolio statistics
            portfolio_return = np.sum(weights * self.qpt._quantum_expected_returns())
            portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            # Asset allocation
            allocation = {asset: weight for asset, weight in zip(self.qpt.assets, weights) 
                         if weight > 0.001}
            
            results['portfolio_statistics'] = {
                'allocation': allocation,
                'expected_return': portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': (portfolio_return - self.qpt.risk_free_rate) / portfolio_volatility,
                'quantum_entropy': self.qpt._calculate_quantum_entropy(weights),
                'quantum_coherence': self.qpt._calculate_quantum_coherence(weights)
            }
        
        return results
    
    def visualize_annealing_process(self, save_path: Optional[str] = None) -> None:
        """Visualize quantum annealing process"""
        if not self.cost_history:
            self.logger.warning("Annealing process ma'lumotlari topilmadi")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Quantum Annealing Process Visualization', fontsize=16)
        
        # 1. Cost evolution
        axes[0, 0].plot(self.cost_history)
        axes[0, 0].set_title('Cost Function Evolution')
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('Cost')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Temperature schedule
        axes[0, 1].plot(self.temperature_schedule)
        axes[0, 1].set_title('Temperature Schedule')
        axes[0, 1].set_xlabel('Iteration')
        axes[0, 1].set_ylabel('Temperature')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Solution convergence (if final solution has multiple assets)
        if self.best_solution is not None and len(self.best_solution) > 1:
            final_allocation = self.best_solution / np.sum(self.best_solution)
            asset_names = getattr(self.qpt, 'assets', [f'Asset_{i}' for i in range(len(final_allocation))])
            
            axes[1, 0].bar(range(len(final_allocation)), final_allocation)
            axes[1, 0].set_title('Final Portfolio Allocation')
            axes[1, 0].set_xlabel('Asset Index')
            axes[1, 0].set_ylabel('Weight')
            axes[1, 0].set_xticks(range(len(asset_names)))
            axes[1, 0].set_xticklabels(asset_names, rotation=45)
        
        # 4. Quantum coherence evolution
        if self.solution_history:
            coherence_history = []
            for solution in self.solution_history:
                if hasattr(self.qpt, '_calculate_quantum_coherence'):
                    coherence = self.qpt._calculate_quantum_coherence(solution)
                else:
                    # Simple coherence approximation
                    coherence = np.sum(solution ** 2)
                coherence_history.append(coherence)
            
            axes[1, 1].plot(coherence_history)
            axes[1, 1].set_title('Quantum Coherence Evolution')
            axes[1, 1].set_xlabel('Iteration')
            axes[1, 1].set_ylabel('Quantum Coherence')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Annealing visualization saqlandi: {save_path}")
        else:
            plt.show()
    
    def compare_annealing_schedules(self, 
                                  schedules: List[Dict],
                                  objective_function: Callable,
                                  save_path: Optional[str] = None) -> Dict:
        """
        Compare different annealing schedules
        
        Args:
            schedules: List of schedule parameters
            objective_function: Objective function to optimize
            save_path: Save path for comparison plot
            
        Returns:
            Comparison results
        """
        comparison_results = {}
        
        for i, schedule in enumerate(schedules):
            # Create optimizer with specific schedule
            temp_optimizer = QuantumAnnealingOptimizer(
                self.qpt,
                initial_temperature=schedule.get('initial_temperature', self.initial_temperature),
                cooling_rate=schedule.get('cooling_rate', self.cooling_rate),
                min_temperature=schedule.get('min_temperature', self.min_temperature),
                max_iterations=schedule.get('max_iterations', self.max_iterations)
            )
            
            # Run optimization
            results = temp_optimizer.optimize(
                objective_function=objective_function,
                quantum_enhancement=schedule.get('quantum_enhancement', True)
            )
            
            comparison_results[f'schedule_{i+1}'] = {
                'parameters': schedule,
                'best_cost': results['best_cost'],
                'iterations': results['total_iterations'],
                'acceptance_rate': results['acceptance_rate'],
                'final_temperature': results['final_temperature'],
                'convergence_time': results['total_iterations']
            }
        
        # Create comparison plot
        if save_path:
            self._plot_schedule_comparison(comparison_results, save_path)
        
        return comparison_results
    
    def _plot_schedule_comparison(self, results: Dict, save_path: str):
        """Plot schedule comparison"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Quantum Annealing Schedule Comparison', fontsize=16)
        
        # Extract data for plotting
        schedule_names = list(results.keys())
        costs = [results[name]['best_cost'] for name in schedule_names]
        iterations = [results[name]['iterations'] for name in schedule_names]
        acceptance_rates = [results[name]['acceptance_rate'] for name in schedule_names]
        
        # Plot 1: Final cost comparison
        axes[0].bar(schedule_names, costs)
        axes[0].set_title('Final Cost Comparison')
        axes[0].set_ylabel('Best Cost')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Plot 2: Iterations vs Acceptance Rate
        axes[1].scatter(iterations, acceptance_rates, s=100)
        for i, name in enumerate(schedule_names):
            axes[1].annotate(name, (iterations[i], acceptance_rates[i]), 
                           xytext=(5, 5), textcoords='offset points')
        axes[1].set_title('Iterations vs Acceptance Rate')
        axes[1].set_xlabel('Total Iterations')
        axes[1].set_ylabel('Acceptance Rate')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Schedule comparison plot saqlandi: {save_path}")
    
    def save_annealing_state(self, filepath: str):
        """Save annealing state"""
        state = {
            'initial_temperature': self.initial_temperature,
            'cooling_rate': self.cooling_rate,
            'min_temperature': self.min_temperature,
            'max_iterations': self.max_iterations,
            'quantum_entanglement_strength': self.quantum_entanglement_strength,
            'best_solution': self.best_solution.tolist() if self.best_solution is not None else None,
            'best_cost': self.best_cost,
            'solution_history': [sol.tolist() for sol in self.solution_history],
            'cost_history': self.cost_history,
            'temperature_schedule': self.temperature_schedule
        }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        self.logger.info(f"Annealing state saqlandi: {filepath}")
    
    def load_annealing_state(self, filepath: str):
        """Load annealing state"""
        import json
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.initial_temperature = state['initial_temperature']
        self.cooling_rate = state['cooling_rate']
        self.min_temperature = state['min_temperature']
        self.max_iterations = state['max_iterations']
        self.quantum_entanglement_strength = state['quantum_entanglement_strength']
        
        self.best_solution = np.array(state['best_solution']) if state['best_solution'] else None
        self.best_cost = state['best_cost']
        self.solution_history = [np.array(sol) for sol in state['solution_history']]
        self.cost_history = state['cost_history']
        self.temperature_schedule = state['temperature_schedule']
        
        self.logger.info(f"Annealing state yuklandi: {filepath}")