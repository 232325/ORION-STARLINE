"""
Quantum Genetic Optimizer
=========================

Quantum-enhanced Genetic Algorithm optimizatori.
Bu modul GA algoritmini quantum computing effektlari bilan birga qo'llaydi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import logging
import matplotlib.pyplot as plt
import random

class QuantumGeneticOptimizer:
    """
    Quantum-enhanced Genetic Algorithm Optimizer
    """
    
    def __init__(self, 
                 quantum_portfolio_theory,
                 population_size: int = 50,
                 crossover_rate: float = 0.8,
                 mutation_rate: float = 0.1,
                 elite_size: int = 5,
                 quantum_enhancement: float = 0.15,
                 max_generations: int = 200):
        """
        Initialize quantum GA optimizer
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
            population_size: Population size
            crossover_rate: Crossover probability
            mutation_rate: Mutation probability
            elite_size: Number of elite individuals to preserve
            quantum_enhancement: Quantum enhancement strength
            max_generations: Maximum generations
        """
        self.qpt = quantum_portfolio_theory
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.quantum_enhancement = quantum_enhancement
        self.max_generations = max_generations
        
        # GA state
        self.population = None
        self.fitness_scores = None
        self.best_individual = None
        self.best_fitness = float('-inf')
        
        # Evolution history
        self.generation_history = []
        self.best_fitness_history = []
        self.average_fitness_history = []
        
        self.logger = logging.getLogger(__name__)
        self._initialize_population()
    
    def _initialize_population(self):
        """Initialize random population"""
        n_assets = len(self.qpt.assets)
        
        # Create random population using Dirichlet distribution for portfolio weights
        self.population = np.random.dirichlet(np.ones(n_assets), self.population_size)
        self._evaluate_population()
    
    def _evaluate_population(self):
        """Evaluate fitness for entire population"""
        self.fitness_scores = np.array([self._evaluate_individual(individual) 
                                      for individual in self.population])
        
        # Update best individual
        best_idx = np.argmax(self.fitness_scores)
        if self.fitness_scores[best_idx] > self.best_fitness:
            self.best_fitness = self.fitness_scores[best_idx]
            self.best_individual = self.population[best_idx].copy()
    
    def _evaluate_individual(self, individual: np.ndarray) -> float:
        """Evaluate individual fitness"""
        if self.qpt.covariance_matrix is None:
            return 0.0
        
        expected_returns = self.qpt._quantum_expected_returns()
        portfolio_return = np.sum(individual * expected_returns)
        portfolio_variance = np.dot(individual, np.dot(self.qpt.covariance_matrix, individual))
        
        # Base fitness (Sharpe ratio approximation)
        portfolio_volatility = np.sqrt(portfolio_variance)
        sharpe_ratio = (portfolio_return - self.qpt.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        # Quantum enhancements
        quantum_entropy = self.qpt._calculate_quantum_entropy(individual)
        quantum_coherence = self.qpt._calculate_quantum_coherence(individual)
        
        # Combined fitness
        fitness = sharpe_ratio + quantum_entropy * 0.1 + quantum_coherence * 0.05
        
        return fitness
    
    def optimize(self, 
                objective_function: Optional[callable] = None,
                constraints: Optional[List[Dict]] = None,
                bounds: Optional[List[Tuple]] = None) -> Dict:
        """
        Quantum genetic algorithm optimization
        
        Args:
            objective_function: Custom objective function
            constraints: Optimization constraints
            bounds: Variable bounds
            
        Returns:
            Optimization results
        """
        # Use default fitness function if none provided
        if objective_function is None:
            objective_function = self._evaluate_individual
        
        # Evolution loop
        for generation in range(self.max_generations):
            # Evaluate current population
            self._evaluate_population()
            
            # Record generation statistics
            self.generation_history.append(generation)
            self.best_fitness_history.append(self.best_fitness)
            self.average_fitness_history.append(np.mean(self.fitness_scores))
            
            # Create new generation
            new_population = []
            
            # Elitism: preserve best individuals
            elite_indices = np.argsort(self.fitness_scores)[-self.elite_size:]
            for idx in elite_indices:
                new_population.append(self.population[idx].copy())
            
            # Generate rest of population through selection, crossover, and mutation
            while len(new_population) < self.population_size:
                # Selection
                parent1 = self._tournament_selection()
                parent2 = self._tournament_selection()
                
                # Quantum crossover
                if random.random() < self.crossover_rate:
                    offspring = self._quantum_crossover(parent1, parent2)
                else:
                    offspring = parent1.copy()
                
                # Quantum mutation
                if random.random() < self.mutation_rate:
                    offspring = self._quantum_mutation(offspring, generation)
                
                # Apply constraints
                offspring = self._apply_constraints(offspring, constraints, bounds)
                
                new_population.append(offspring)
            
            # Replace population
            self.population = np.array(new_population)
            
            # Progress logging
            if generation % 20 == 0:
                self.logger.info(f"GA Generation {generation}: "
                               f"Best Fitness={self.best_fitness:.6f}, "
                               f"Avg Fitness={np.mean(self.fitness_scores):.6f}")
        
        # Final evaluation
        self._evaluate_population()
        
        return {
            'best_individual': self.best_individual,
            'best_fitness': self.best_fitness,
            'best_allocation': self._create_allocation_dict(self.best_individual),
            'total_generations': generation + 1,
            'population_size': self.population_size,
            'generation_history': self.generation_history,
            'best_fitness_history': self.best_fitness_history,
            'average_fitness_history': self.average_fitness_history,
            'final_population': self.population,
            'optimization_method': 'quantum_genetic'
        }
    
    def _tournament_selection(self, tournament_size: int = 3) -> np.ndarray:
        """Tournament selection"""
        tournament_indices = random.sample(range(self.population_size), tournament_size)
        tournament_fitness = [self.fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return self.population[winner_idx].copy()
    
    def _quantum_crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
        """Quantum-enhanced crossover"""
        n_assets = len(parent1)
        
        # Standard arithmetic crossover
        alpha = random.random()
        offspring1 = alpha * parent1 + (1 - alpha) * parent2
        offspring2 = (1 - alpha) * parent1 + alpha * parent2
        
        # Quantum entanglement crossover
        if self.quantum_enhancement > 0:
            # Calculate quantum coherence between parents
            coherence = self._calculate_genetic_coherence(parent1, parent2)
            
            # Apply quantum interference
            quantum_factor = 1 + self.quantum_enhancement * coherence
            offspring1 = offspring1 * quantum_factor
            offspring2 = offspring2 * quantum_factor
            
            # Renormalize
            offspring1 = np.maximum(0, offspring1)
            offspring2 = np.maximum(0, offspring2)
            offspring1 = offspring1 / np.sum(offspring1)
            offspring2 = offspring2 / np.sum(offspring2)
        
        # Return the better offspring
        fitness1 = self._evaluate_individual(offspring1)
        fitness2 = self._evaluate_individual(offspring2)
        
        return offspring1 if fitness1 > fitness2 else offspring2
    
    def _calculate_genetic_coherence(self, individual1: np.ndarray, individual2: np.ndarray) -> float:
        """Calculate quantum coherence between two individuals"""
        # Simple coherence measure based on similarity
        similarity = 1 - np.mean(np.abs(individual1 - individual2))
        return similarity
    
    def _quantum_mutation(self, individual: np.ndarray, generation: int) -> np.ndarray:
        """Quantum-enhanced mutation"""
        mutated = individual.copy()
        n_assets = len(mutated)
        
        # Quantum tunneling mutation (allows large jumps)
        tunnel_probability = np.exp(-generation / (self.max_generations / 3))
        
        if random.random() < tunnel_probability * self.quantum_enhancement:
            # Quantum tunneling: reset a random gene
            reset_idx = random.randint(0, n_assets - 1)
            mutated[reset_idx] = random.random()
        
        # Small perturbations
        mutation_strength = 0.05 * (1 - generation / self.max_generations)  # Decreasing over time
        
        for i in range(n_assets):
            if random.random() < self.mutation_rate:
                # Gaussian mutation
                mutation = np.random.normal(0, mutation_strength)
                mutated[i] += mutation
        
        # Ensure non-negative weights
        mutated = np.maximum(0, mutated)
        
        # Normalize to maintain budget constraint
        if np.sum(mutated) > 0:
            mutated = mutated / np.sum(mutated)
        
        return mutated
    
    def _apply_constraints(self, 
                          individual: np.ndarray, 
                          constraints: Optional[List[Dict]] = None,
                          bounds: Optional[List[Tuple]] = None) -> np.ndarray:
        """Apply constraints to individual"""
        constrained_individual = individual.copy()
        
        # Apply bounds
        if bounds:
            for i, (lower, upper) in enumerate(bounds):
                constrained_individual[i] = np.clip(constrained_individual[i], lower, upper)
        
        # Ensure non-negative weights
        constrained_individual = np.maximum(0, constrained_individual)
        
        # Normalize to maintain budget constraint
        if np.sum(constrained_individual) > 0:
            constrained_individual = constrained_individual / np.sum(constrained_individual)
        
        return constrained_individual
    
    def _create_allocation_dict(self, individual: np.ndarray) -> Dict:
        """Create allocation dictionary from individual"""
        allocation = {}
        for i, weight in enumerate(individual):
            if weight > 0.001:
                allocation[self.qpt.assets[i]] = weight
        return allocation
    
    def optimize_portfolio(self, target_return: Optional[float] = None) -> Dict:
        """Portfolio-specific optimization"""
        def portfolio_fitness(individual):
            expected_returns = self.qpt._quantum_expected_returns()
            portfolio_return = np.sum(individual * expected_returns)
            portfolio_variance = np.dot(individual, np.dot(self.qpt.covariance_matrix, individual))
            
            portfolio_volatility = np.sqrt(portfolio_variance)
            sharpe_ratio = (portfolio_return - self.qpt.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Return penalty
            return_penalty = 0
            if target_return is not None and portfolio_return < target_return:
                return_penalty = (target_return - portfolio_return) ** 2
            
            return sharpe_ratio - return_penalty
        
        results = self.optimize(objective_function=portfolio_fitness)
        
        # Add portfolio statistics
        if self.best_individual is not None:
            weights = self.best_individual
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
    
    def visualize_ga_process(self, save_path: Optional[str] = None):
        """Visualize GA optimization process"""
        if not self.best_fitness_history:
            self.logger.warning("GA optimization ma'lumotlari topilmadi")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Quantum Genetic Algorithm Process', fontsize=16)
        
        # 1. Fitness evolution
        axes[0, 0].plot(self.generation_history, self.best_fitness_history, 
                       label='Best Fitness', color='red', linewidth=2)
        axes[0, 0].plot(self.generation_history, self.average_fitness_history, 
                       label='Average Fitness', color='blue', alpha=0.7)
        axes[0, 0].set_title('Fitness Evolution')
        axes[0, 0].set_xlabel('Generation')
        axes[0, 0].set_ylabel('Fitness')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Population diversity
        if self.population is not None:
            population_entropy = []
            for individual in self.population:
                # Calculate entropy of individual (diversification measure)
                positive_weights = individual[individual > 0]
                if len(positive_weights) > 1:
                    normalized_weights = positive_weights / np.sum(positive_weights)
                    entropy = -np.sum(normalized_weights * np.log2(normalized_weights + 1e-8))
                else:
                    entropy = 0
                population_entropy.append(entropy)
            
            axes[0, 1].hist(population_entropy, bins=20, alpha=0.7)
            axes[0, 1].set_title('Population Diversity Distribution')
            axes[0, 1].set_xlabel('Individual Entropy (Diversification)')
            axes[0, 1].set_ylabel('Frequency')
        
        # 3. Best allocation
        if self.best_individual is not None and len(self.best_individual) > 1:
            allocation_values = self.best_individual
            asset_names = self.qpt.assets
            
            bars = axes[1, 0].bar(range(len(allocation_values)), allocation_values, color='green', alpha=0.7)
            axes[1, 0].set_title('Best Portfolio Allocation')
            axes[1, 0].set_xlabel('Asset Index')
            axes[1, 0].set_ylabel('Weight')
            axes[1, 0].set_xticks(range(len(asset_names)))
            axes[1, 0].set_xticklabels(asset_names, rotation=45)
            
            # Add value labels on bars
            for bar, value in zip(bars, allocation_values):
                if value > 0.01:
                    axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                                  f'{value:.3f}', ha='center', va='bottom')
        
        # 4. Convergence rate
        if len(self.best_fitness_history) > 1:
            # Calculate improvement rate
            improvements = np.diff(self.best_fitness_history)
            axes[1, 1].plot(self.generation_history[1:], improvements, color='purple')
            axes[1, 1].set_title('Fitness Improvement Rate')
            axes[1, 1].set_xlabel('Generation')
            axes[1, 1].set_ylabel('Fitness Improvement')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"GA visualization saqlandi: {save_path}")
        else:
            plt.show()