"""
Quantum Particle Swarm Optimizer
=================================

Quantum-enhanced Particle Swarm Optimization algoritmi.
Bu modul PSO algoritmini quantum computing effektlari bilan birga qo'llaydi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
import matplotlib.pyplot as plt
import random

class QuantumParticleSwarmOptimizer:
    """
    Quantum-enhanced Particle Swarm Optimizer
    """
    
    def __init__(self, 
                 quantum_portfolio_theory,
                 num_particles: int = 30,
                 inertia_weight: float = 0.9,
                 cognitive_coefficient: float = 2.0,
                 social_coefficient: float = 2.0,
                 quantum_coherence: float = 0.1,
                 max_iterations: int = 1000):
        """
        Initialize quantum PSO optimizer
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
            num_particles: Number of particles in swarm
            inertia_weight: Inertia weight (0-1)
            cognitive_coefficient: Cognitive coefficient
            social_coefficient: Social coefficient
            quantum_coherence: Quantum coherence strength
            max_iterations: Maximum iterations
        """
        self.qpt = quantum_portfolio_theory
        self.num_particles = num_particles
        self.inertia_weight = inertia_weight
        self.cognitive_coefficient = cognitive_coefficient
        self.social_coefficient = social_coefficient
        self.quantum_coherence = quantum_coherence
        self.max_iterations = max_iterations
        
        # Swarm state
        self.particles = None
        self.velocities = None
        self.personal_best_positions = None
        self.personal_best_costs = None
        self.global_best_position = None
        self.global_best_cost = float('inf')
        
        # History tracking
        self.cost_history = []
        self.global_best_history = []
        
        self.logger = logging.getLogger(__name__)
        self._initialize_swarm()
    
    def _initialize_swarm(self):
        """Initialize particle swarm"""
        n_assets = len(self.qpt.assets)
        
        # Initialize particles (positions)
        self.particles = np.random.dirichlet(np.ones(n_assets), self.num_particles)
        
        # Initialize velocities
        self.velocities = np.random.uniform(-0.1, 0.1, (self.num_particles, n_assets))
        
        # Initialize personal bests
        self.personal_best_positions = self.particles.copy()
        self.personal_best_costs = np.full(self.num_particles, float('inf'))
        
        # Evaluate initial particles
        for i in range(self.num_particles):
            cost = self._evaluate_particle(self.particles[i])
            self.personal_best_costs[i] = cost
            
            if cost < self.global_best_cost:
                self.global_best_cost = cost
                self.global_best_position = self.particles[i].copy()
    
    def _evaluate_particle(self, position: np.ndarray) -> float:
        """Evaluate particle fitness"""
        if self.qpt.covariance_matrix is None:
            return 0.0
        
        expected_returns = self.qpt._quantum_expected_returns()
        portfolio_return = np.sum(position * expected_returns)
        portfolio_variance = np.dot(position, np.dot(self.qpt.covariance_matrix, position))
        
        # Base mean-variance utility
        utility = portfolio_return - 0.5 * portfolio_variance
        
        # Quantum enhancements
        quantum_entropy = self.qpt._calculate_quantum_entropy(position)
        quantum_coherence = self.qpt._calculate_quantum_coherence(position)
        
        return -(utility + quantum_entropy * 0.1 + quantum_coherence * 0.05)
    
    def optimize(self, 
                objective_function: Optional[callable] = None,
                constraints: Optional[List[Dict]] = None,
                bounds: Optional[List[Tuple]] = None) -> Dict:
        """
        Quantum PSO optimization
        
        Args:
            objective_function: Custom objective function
            constraints: Optimization constraints
            bounds: Variable bounds
            
        Returns:
            Optimization results
        """
        # Use default portfolio objective if none provided
        if objective_function is None:
            objective_function = self._evaluate_particle
        
        # Optimization loop
        for iteration in range(self.max_iterations):
            for i in range(self.num_particles):
                # Update velocity
                r1, r2 = random.random(), random.random()
                
                cognitive_velocity = (self.cognitive_coefficient * r1 * 
                                    (self.personal_best_positions[i] - self.particles[i]))
                social_velocity = (self.social_coefficient * r2 * 
                                 (self.global_best_position - self.particles[i]))
                
                # Quantum-enhanced velocity update
                quantum_velocity = self._calculate_quantum_velocity(i, iteration)
                
                self.velocities[i] = (self.inertia_weight * self.velocities[i] + 
                                    cognitive_velocity + social_velocity + quantum_velocity)
                
                # Update position
                self.particles[i] = self.particles[i] + self.velocities[i]
                
                # Apply constraints and bounds
                self.particles[i] = self._apply_constraints(self.particles[i], constraints, bounds)
                
                # Evaluate new position
                current_cost = objective_function(self.particles[i])
                
                # Update personal best
                if current_cost < self.personal_best_costs[i]:
                    self.personal_best_costs[i] = current_cost
                    self.personal_best_positions[i] = self.particles[i].copy()
                    
                    # Update global best
                    if current_cost < self.global_best_cost:
                        self.global_best_cost = current_cost
                        self.global_best_position = self.particles[i].copy()
            
            # Record history
            self.cost_history.append(current_cost)
            self.global_best_history.append(self.global_best_cost)
            
            # Progress logging
            if iteration % 100 == 0:
                self.logger.info(f"PSO Iteration {iteration}: Best Cost={self.global_best_cost:.6f}")
        
        return {
            'best_position': self.global_best_position,
            'best_cost': self.global_best_cost,
            'best_allocation': self._create_allocation_dict(self.global_best_position),
            'total_iterations': iteration + 1,
            'num_particles': self.num_particles,
            'cost_history': self.cost_history,
            'global_best_history': self.global_best_history,
            'final_particles': self.particles,
            'optimization_method': 'quantum_particle_swarm'
        }
    
    def _calculate_quantum_velocity(self, particle_index: int, iteration: int) -> np.ndarray:
        """Calculate quantum-enhanced velocity component"""
        n_assets = len(self.qpt.assets)
        
        # Quantum tunneling effect
        tunneling_strength = np.exp(-iteration / (self.max_iterations / 3))
        
        # Quantum coherence between particles
        coherence_velocity = np.zeros(n_assets)
        if self.quantum_coherence > 0:
            for j in range(self.num_particles):
                if j != particle_index:
                    # Calculate quantum coherence between particles
                    coherence = self._calculate_particle_coherence(
                        self.particles[particle_index], self.particles[j]
                    )
                    coherence_velocity += coherence * tunneling_strength * self.quantum_coherence
        
        # Quantum entanglement with global best
        entanglement_velocity = np.zeros(n_assets)
        if self.global_best_position is not None:
            entanglement = self._calculate_particle_coherence(
                self.particles[particle_index], self.global_best_position
            )
            entanglement_velocity = entanglement * tunneling_strength * self.quantum_coherence * 0.5
        
        return coherence_velocity + entanglement_velocity
    
    def _calculate_particle_coherence(self, particle1: np.ndarray, particle2: np.ndarray) -> np.ndarray:
        """Calculate quantum coherence between two particles"""
        # Simplified coherence measure based on position similarity
        coherence = np.abs(particle1 - particle2)
        return coherence
    
    def _apply_constraints(self, 
                          position: np.ndarray, 
                          constraints: Optional[List[Dict]] = None,
                          bounds: Optional[List[Tuple]] = None) -> np.ndarray:
        """Apply constraints to particle position"""
        constrained_position = position.copy()
        
        # Apply bounds
        if bounds:
            for i, (lower, upper) in enumerate(bounds):
                constrained_position[i] = np.clip(constrained_position[i], lower, upper)
        
        # Ensure non-negative weights
        constrained_position = np.maximum(0, constrained_position)
        
        # Normalize to maintain budget constraint
        if np.sum(constrained_position) > 0:
            constrained_position = constrained_position / np.sum(constrained_position)
        
        return constrained_position
    
    def _create_allocation_dict(self, position: np.ndarray) -> Dict:
        """Create allocation dictionary from position"""
        allocation = {}
        for i, weight in enumerate(position):
            if weight > 0.001:
                allocation[self.qpt.assets[i]] = weight
        return allocation
    
    def optimize_portfolio(self, target_return: Optional[float] = None) -> Dict:
        """Portfolio-specific optimization"""
        def portfolio_objective(weights):
            expected_returns = self.qpt._quantum_expected_returns()
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
            
            utility = portfolio_return - 0.5 * portfolio_variance
            
            # Return penalty
            return_penalty = 0
            if target_return is not None and portfolio_return < target_return:
                return_penalty = (target_return - portfolio_return) ** 2
            
            return -(utility - return_penalty)
        
        # Define constraints
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
        bounds = [(0, 1) for _ in range(len(self.qpt.assets))]
        
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda w: np.sum(w * self.qpt._quantum_expected_returns()) - target_return
            })
        
        results = self.optimize(
            objective_function=portfolio_objective,
            constraints=constraints,
            bounds=bounds
        )
        
        # Add portfolio statistics
        if self.global_best_position is not None:
            weights = self.global_best_position
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
    
    def visualize_pso_process(self, save_path: Optional[str] = None):
        """Visualize PSO optimization process"""
        if not self.global_best_history:
            self.logger.warning("PSO optimization ma'lumotlari topilmadi")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Quantum Particle Swarm Optimization Process', fontsize=16)
        
        # 1. Global best convergence
        axes[0, 0].plot(self.global_best_history)
        axes[0, 0].set_title('Global Best Convergence')
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('Best Cost')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Particle distribution (final)
        if self.particles is not None and len(self.particles[0]) > 1:
            # Show particle positions in 2D space (first 2 assets)
            particles_2d = self.particles[:, :2]
            axes[0, 1].scatter(particles_2d[:, 0], particles_2d[:, 1], alpha=0.6, s=30)
            axes[0, 1].scatter(self.global_best_position[0], self.global_best_position[1], 
                             color='red', s=100, label='Global Best', marker='*')
            axes[0, 1].set_title('Final Particle Distribution')
            axes[0, 1].set_xlabel(f'{self.qpt.assets[0]} Weight')
            axes[0, 1].set_ylabel(f'{self.qpt.assets[1]} Weight')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Cost evolution over iterations
        axes[1, 0].plot(self.cost_history, alpha=0.7, label='All Particles')
        axes[1, 0].plot(self.global_best_history, color='red', linewidth=2, label='Global Best')
        axes[1, 0].set_title('Cost Evolution')
        axes[1, 0].set_xlabel('Iteration')
        axes[1, 0].set_ylabel('Cost')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Best allocation
        if self.global_best_position is not None and len(self.global_best_position) > 1:
            allocation_values = self.global_best_position
            asset_names = self.qpt.assets
            
            bars = axes[1, 1].bar(range(len(allocation_values)), allocation_values)
            axes[1, 1].set_title('Optimal Portfolio Allocation')
            axes[1, 1].set_xlabel('Asset Index')
            axes[1, 1].set_ylabel('Weight')
            axes[1, 1].set_xticks(range(len(asset_names)))
            axes[1, 1].set_xticklabels(asset_names, rotation=45)
            
            # Add value labels on bars
            for bar, value in zip(bars, allocation_values):
                if value > 0.01:
                    axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                                  f'{value:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"PSO visualization saqlandi: {save_path}")
        else:
            plt.show()