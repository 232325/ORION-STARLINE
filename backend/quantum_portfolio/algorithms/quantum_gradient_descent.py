"""
Quantum Gradient Descent
========================

Quantum-enhanced gradient descent algoritmi.
Bu modul quantum computing yordamida gradient descent optimizatsiyasini amalga oshiradi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
import logging
import matplotlib.pyplot as plt

class QuantumGradientDescent:
    """
    Quantum-enhanced Gradient Descent Optimizer
    """
    
    def __init__(self, 
                 quantum_portfolio_theory,
                 learning_rate: float = 0.01,
                 momentum: float = 0.9,
                 quantum_enhancement: float = 0.1,
                 max_iterations: int = 1000):
        """
        Initialize quantum gradient descent
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
            learning_rate: Learning rate for gradient descent
            momentum: Momentum parameter (0-1)
            quantum_enhancement: Quantum enhancement strength
            max_iterations: Maximum iterations
        """
        self.qpt = quantum_portfolio_theory
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.quantum_enhancement = quantum_enhancement
        self.max_iterations = max_iterations
        
        # Optimization state
        self.velocity = None
        self.best_solution = None
        self.best_cost = float('inf')
        
        # History tracking
        self.cost_history = []
        self.gradient_history = []
        self.solution_history = []
        
        self.logger = logging.getLogger(__name__)
    
    def optimize(self, 
                objective_function: Callable,
                initial_solution: Optional[np.ndarray] = None,
                constraints: Optional[List[Dict]] = None,
                bounds: Optional[List[Tuple]] = None) -> Dict:
        """
        Quantum gradient descent optimization
        
        Args:
            objective_function: Objective function to minimize
            initial_solution: Initial solution guess
            constraints: Optimization constraints
            bounds: Variable bounds
            
        Returns:
            Optimization results
        """
        n_assets = len(self.qpt.assets)
        
        # Initialize solution
        if initial_solution is None:
            initial_solution = np.ones(n_assets) / n_assets
        
        current_solution = initial_solution.copy()
        self.velocity = np.zeros_like(current_solution)
        
        # Optimization loop
        for iteration in range(self.max_iterations):
            # Calculate gradient
            gradient = self._calculate_quantum_gradient(objective_function, current_solution)
            
            # Apply quantum enhancement
            enhanced_gradient = self._enhance_gradient_with_quantum_effects(gradient, iteration)
            
            # Momentum update
            self.velocity = self.momentum * self.velocity - self.learning_rate * enhanced_gradient
            
            # Update solution
            current_solution = current_solution + self.velocity
            
            # Apply constraints
            current_solution = self._apply_constraints(current_solution, constraints, bounds)
            
            # Evaluate cost
            current_cost = objective_function(current_solution)
            
            # Track history
            self.cost_history.append(current_cost)
            self.gradient_history.append(enhanced_gradient.copy())
            self.solution_history.append(current_solution.copy())
            
            # Update best solution
            if current_cost < self.best_cost:
                self.best_cost = current_cost
                self.best_solution = current_solution.copy()
            
            # Progress logging
            if iteration % 100 == 0:
                gradient_norm = np.linalg.norm(enhanced_gradient)
                self.logger.info(f"GD Iteration {iteration}: Cost={current_cost:.6f}, "
                               f"Grad Norm={gradient_norm:.6f}")
        
        return {
            'best_solution': self.best_solution,
            'best_cost': self.best_cost,
            'final_solution': current_solution,
            'final_cost': current_cost,
            'total_iterations': iteration + 1,
            'cost_history': self.cost_history,
            'gradient_history': self.gradient_history,
            'solution_history': self.solution_history
        }
    
    def _calculate_quantum_gradient(self, objective_function: Callable, solution: np.ndarray) -> np.ndarray:
        """Calculate gradient with quantum corrections"""
        # Standard numerical gradient
        h = 1e-6
        gradient = np.zeros_like(solution)
        
        for i in range(len(solution)):
            # Forward difference
            solution_plus = solution.copy()
            solution_plus[i] += h
            cost_plus = objective_function(solution_plus)
            
            # Central difference for better accuracy
            solution_minus = solution.copy()
            solution_minus[i] -= h
            cost_minus = objective_function(solution_minus)
            
            # Gradient approximation
            gradient[i] = (cost_plus - cost_minus) / (2 * h)
        
        return gradient
    
    def _enhance_gradient_with_quantum_effects(self, gradient: np.ndarray, iteration: int) -> np.ndarray:
        """Apply quantum effects to gradient"""
        # Quantum coherence enhancement
        coherence_factor = self._calculate_quantum_coherence_factor()
        
        # Quantum entanglement between variables
        entanglement_factor = self._calculate_entanglement_factor(gradient)
        
        # Quantum tunneling effect for escaping local minima
        tunneling_factor = self._calculate_tunneling_factor(iteration)
        
        # Combine quantum effects
        quantum_multiplier = (1 + coherence_factor * self.quantum_enhancement +
                            entanglement_factor * self.quantum_enhancement * 0.5 +
                            tunneling_factor * self.quantum_enhancement * 0.3)
        
        return gradient * quantum_multiplier
    
    def _calculate_quantum_coherence_factor(self) -> float:
        """Calculate quantum coherence factor"""
        # Based on current solution's quantum properties
        if self.best_solution is not None:
            coherence = self.qpt._calculate_quantum_coherence(self.best_solution)
            return coherence
        return 0.0
    
    def _calculate_entanglement_factor(self, gradient: np.ndarray) -> float:
        """Calculate quantum entanglement factor"""
        # Simplified entanglement based on gradient correlation
        if len(gradient) < 2:
            return 0.0
        
        # Calculate gradient correlation
        correlation_matrix = np.corrcoef(gradient.reshape(1, -1), gradient.reshape(1, -1))
        
        # Entanglement measure (simplified)
        entanglement = np.sum(np.abs(correlation_matrix - np.eye(len(gradient))))
        entanglement = entanglement / (len(gradient) * (len(gradient) - 1))
        
        return entanglement
    
    def _calculate_tunneling_factor(self, iteration: int) -> float:
        """Calculate quantum tunneling factor"""
        # Tunneling probability decreases over time
        tunnel_prob = np.exp(-iteration / (self.max_iterations / 4))
        return tunnel_prob
    
    def _apply_constraints(self, 
                          solution: np.ndarray, 
                          constraints: Optional[List[Dict]] = None,
                          bounds: Optional[List[Tuple]] = None) -> np.ndarray:
        """Apply constraints to solution"""
        constrained_solution = solution.copy()
        
        # Apply bounds
        if bounds:
            for i, (lower, upper) in enumerate(bounds):
                constrained_solution[i] = np.clip(constrained_solution[i], lower, upper)
        
        # Ensure non-negative weights
        constrained_solution = np.maximum(0, constrained_solution)
        
        # Normalize to maintain budget constraint
        if np.sum(constrained_solution) > 0:
            constrained_solution = constrained_solution / np.sum(constrained_solution)
        
        return constrained_solution
    
    def optimize_portfolio(self, 
                          target_return: Optional[float] = None,
                          risk_aversion: float = 1.0) -> Dict:
        """Portfolio-specific optimization"""
        if self.qpt.covariance_matrix is None:
            raise ValueError("Portfolio ma'lumotlari yuklanmagan")
        
        def portfolio_objective(weights):
            expected_returns = self.qpt._quantum_expected_returns()
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
            
            utility = portfolio_return - 0.5 * risk_aversion * portfolio_variance
            
            # Quantum enhancements
            quantum_entropy = self.qpt._calculate_quantum_entropy(weights)
            quantum_coherence = self.qpt._calculate_quantum_coherence(weights)
            
            # Return penalty
            return_penalty = 0
            if target_return is not None and portfolio_return < target_return:
                return_penalty = (target_return - portfolio_return) ** 2
            
            return -(utility + quantum_entropy * 0.1 + quantum_coherence * 0.05 - return_penalty)
        
        # Constraints and bounds
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
        bounds = [(0, 1) for _ in range(len(self.qpt.assets))]
        
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda w: np.sum(w * self.qpt._quantum_expected_returns()) - target_return
            })
        
        initial_solution = np.ones(len(self.qpt.assets)) / len(self.qpt.assets)
        
        results = self.optimize(
            objective_function=portfolio_objective,
            initial_solution=initial_solution,
            constraints=constraints,
            bounds=bounds
        )
        
        # Add portfolio statistics
        if results['optimization_status'] == 'success':
            weights = results['best_solution']
            portfolio_return = np.sum(weights * self.qpt._quantum_expected_returns())
            portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            results['portfolio_statistics'] = {
                'expected_return': portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': (portfolio_return - self.qpt.risk_free_rate) / portfolio_volatility,
                'quantum_entropy': self.qpt._calculate_quantum_entropy(weights),
                'quantum_coherence': self.qpt._calculate_quantum_coherence(weights)
            }
        
        return results
    
    def visualize_gd_process(self, save_path: Optional[str] = None):
        """Visualize gradient descent process"""
        if not self.cost_history:
            self.logger.warning("Gradient descent ma'lumotlari topilmadi")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Quantum Gradient Descent Process', fontsize=16)
        
        # 1. Cost convergence
        axes[0, 0].plot(self.cost_history)
        axes[0, 0].set_title('Cost Function Convergence')
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('Cost')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Gradient norms
        if self.gradient_history:
            gradient_norms = [np.linalg.norm(grad) for grad in self.gradient_history]
            axes[0, 1].plot(gradient_norms)
            axes[0, 1].set_title('Gradient Norm Evolution')
            axes[0, 1].set_xlabel('Iteration')
            axes[0, 1].set_ylabel('Gradient Norm')
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Solution components (if available)
        if self.best_solution is not None and len(self.best_solution) > 1:
            asset_names = getattr(self.qpt, 'assets', [f'Asset_{i}' for i in range(len(self.best_solution))])
            axes[1, 0].bar(range(len(self.best_solution)), self.best_solution)
            axes[1, 0].set_title('Optimal Portfolio Allocation')
            axes[1, 0].set_xlabel('Asset Index')
            axes[1, 0].set_ylabel('Weight')
            axes[1, 0].set_xticks(range(len(asset_names)))
            axes[1, 0].set_xticklabels(asset_names, rotation=45)
        
        # 4. Learning curve
        if len(self.cost_history) > 10:
            # Calculate moving average
            window = min(10, len(self.cost_history) // 4)
            moving_avg = pd.Series(self.cost_history).rolling(window).mean()
            axes[1, 1].plot(moving_avg, label='Moving Average', color='red')
            axes[1, 1].plot(self.cost_history, alpha=0.3, label='Raw Cost')
            axes[1, 1].set_title('Learning Curve')
            axes[1, 1].set_xlabel('Iteration')
            axes[1, 1].set_ylabel('Cost')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"GD visualization saqlandi: {save_path}")
        else:
            plt.show()