"""
Evolutionary Strategies - Algoritmlar evolyutsiyasi va optimizatsiyasi
Genetic algorithms, particle swarm optimization, va differential evolution
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import random
import copy
from concurrent.futures import ThreadPoolExecutor
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

@dataclass
class EvolutionConfig:
    """Evolutionary algorithm konfiguratsiyasi"""
    population_size: int = 50
    elite_size: int = 10
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    tournament_size: int = 5
    max_generations: int = 100
    convergence_threshold: float = 1e-6
    patience: int = 20
    parallel_evolution: bool = True
    n_cores: int = 4

@dataclass
class Individual:
    """Evolutionary individual (model parameters)"""
    genes: np.ndarray
    fitness: float = 0.0
    generation: int = 0
    mutation_count: int = 0
    crossover_count: int = 0
    birth_time: datetime = field(default_factory=datetime.now)
    
    def copy(self) -> 'Individual':
        """Individual ni ko'chirib olish"""
        return Individual(
            genes=self.genes.copy(),
            fitness=self.fitness,
            generation=self.generation,
            mutation_count=self.mutation_count,
            crossover_count=self.crossover_count,
            birth_time=self.birth_time
        )

class GeneticAlgorithm:
    """Classic Genetic Algorithm for model optimization"""
    
    def __init__(self, config: EvolutionConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.GeneticAlgorithm")
        
        # Evolution state
        self.population: List[Individual] = []
        self.generation = 0
        self.best_individual: Optional[Individual] = None
        self.fitness_history = []
        self.convergence_history = []
        
        # Fitness evaluation function (to be set)
        self.fitness_function: Optional[Callable] = None
        
        # Evolution statistics
        self.evolution_stats = {
            'total_mutations': 0,
            'total_crossovers': 0,
            'convergence_generation': None,
            'diversity_score': 0.0
        }
    
    def set_fitness_function(self, fitness_func: Callable[[Individual], float]) -> None:
        """Fitness function ni o'rnatish"""
        self.fitness_function = fitness_func
    
    def initialize_population(self, gene_bounds: List[Tuple[float, float]]) -> None:
        """Population ni inicializatsiya qilish"""
        self.population = []
        
        for _ in range(self.config.population_size):
            # Random genes within bounds
            genes = np.array([
                np.random.uniform(low, high) 
                for low, high in gene_bounds
            ])
            
            individual = Individual(genes=genes)
            self.population.append(individual)
        
        self.logger.info(f"Initialized population with {len(self.population)} individuals")
    
    def evolve(self, gene_bounds: List[Tuple[float, float]]) -> Individual:
        """Evolution jarayonini boshqarish"""
        if self.fitness_function is None:
            raise ValueError("Fitness function must be set before evolution")
        
        # Initialize population
        self.initialize_population(gene_bounds)
        
        # Evaluate initial population
        self._evaluate_population()
        
        # Evolution loop
        patience_counter = 0
        prev_best_fitness = float('-inf')
        
        for generation in range(self.config.max_generations):
            self.generation = generation
            
            # Generate offspring
            offspring = self._generate_offspring()
            
            # Evaluate offspring
            if self.config.parallel_evolution:
                self._evaluate_population_parallel(offspring)
            else:
                self._evaluate_population_sequential(offspring)
            
            # Select next generation
            self._select_next_generation(offspring)
            
            # Track best individual
            current_best = max(self.population, key=lambda x: x.fitness)
            if current_best.fitness > self.best_individual.fitness if self.best_individual else False:
                self.best_individual = current_best.copy()
            
            # Track fitness history
            self.fitness_history.append(current_best.fitness)
            
            # Check convergence
            improvement = current_best.fitness - prev_best_fitness
            self.convergence_history.append(improvement)
            
            if abs(improvement) < self.config.convergence_threshold:
                patience_counter += 1
                if patience_counter >= self.config.patience:
                    self.evolution_stats['convergence_generation'] = generation
                    self.logger.info(f"Converged at generation {generation}")
                    break
            else:
                patience_counter = 0
            
            prev_best_fitness = current_best.fitness
            
            # Log progress
            if generation % 10 == 0:
                self.logger.info(
                    f"Generation {generation}: Best fitness = {current_best.fitness:.6f}, "
                    f"Population diversity = {self._calculate_diversity():.4f}"
                )
        
        self.logger.info(f"Evolution completed. Best fitness: {self.best_individual.fitness:.6f}")
        return self.best_individual
    
    def _evaluate_population(self) -> None:
        """Population ni baholash"""
        for individual in self.population:
            if self.fitness_function:
                individual.fitness = self.fitness_function(individual)
    
    def _evaluate_population_parallel(self, offspring: List[Individual]) -> None:
        """Parallel population evaluation"""
        def evaluate_individual(ind):
            if self.fitness_function:
                ind.fitness = self.fitness_function(ind)
            return ind
        
        with ThreadPoolExecutor(max_workers=self.config.n_cores) as executor:
            evaluated_offspring = list(executor.map(evaluate_individual, offspring))
        
        self.population.extend(evaluated_offspring)
    
    def _evaluate_population_sequential(self, offspring: List[Individual]) -> None:
        """Sequential population evaluation"""
        for individual in offspring:
            if self.fitness_function:
                individual.fitness = self.fitness_function(individual)
        self.population.extend(offspring)
    
    def _generate_offspring(self) -> List[Individual]:
        """Offspring generation"""
        offspring = []
        
        while len(offspring) < self.config.population_size:
            # Selection
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            # Crossover
            if np.random.random() < self.config.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
                offspring.extend([child1, child2])
            else:
                offspring.extend([parent1.copy(), parent2.copy()])
        
        # Mutations
        for individual in offspring:
            if np.random.random() < self.config.mutation_rate:
                self._mutate(individual)
        
        return offspring[:self.config.population_size]
    
    def _tournament_selection(self) -> Individual:
        """Tournament selection"""
        tournament = random.sample(self.population, min(self.config.tournament_size, len(self.population)))
        return max(tournament, key=lambda x: x.fitness)
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Single-point crossover"""
        # Choose crossover point
        crossover_point = np.random.randint(1, len(parent1.genes))
        
        # Create offspring
        child1_genes = np.concatenate([parent1.genes[:crossover_point], parent2.genes[crossover_point:]])
        child2_genes = np.concatenate([parent2.genes[:crossover_point], parent1.genes[crossover_point:]])
        
        child1 = Individual(genes=child1_genes, generation=self.generation + 1)
        child2 = Individual(genes=child2_genes, generation=self.generation + 1)
        
        # Update crossover statistics
        parent1.crossover_count += 1
        parent2.crossover_count += 1
        self.evolution_stats['total_crossovers'] += 1
        
        return child1, child2
    
    def _mutate(self, individual: Individual) -> None:
        """Gaussian mutation"""
        # Mutation with gaussian noise
        mutation_strength = 0.1 * (1.0 / (1.0 + individual.generation * 0.01))
        
        for i in range(len(individual.genes)):
            if np.random.random() < 0.1:  # 10% chance per gene
                individual.genes[i] += np.random.normal(0, mutation_strength)
        
        individual.mutation_count += 1
        self.evolution_stats['total_mutations'] += 1
    
    def _select_next_generation(self, offspring: List[Individual]) -> None:
        """Next generation selection (elitism)"""
        # Combine current population and offspring
        combined_population = self.population + offspring
        
        # Sort by fitness
        combined_population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Select elite individuals
        elite_individuals = combined_population[:self.config.elite_size]
        
        # Select remaining individuals using tournament selection
        remaining_population = combined_population[self.config.elite_size:]
        selected_remaining = []
        
        while len(selected_remaining) < self.config.population_size - self.config.elite_size:
            selected = self._tournament_selection_from_list(remaining_population)
            selected_remaining.append(selected)
        
        # Create new population
        self.population = elite_individuals + selected_remaining
    
    def _tournament_selection_from_list(self, population: List[Individual]) -> Individual:
        """Tournament selection from specific population"""
        tournament = random.sample(population, min(self.config.tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness)
    
    def _calculate_diversity(self) -> float:
        """Population diversity ni hisoblash"""
        if len(self.population) < 2:
            return 0.0
        
        # Calculate pairwise distances
        distances = []
        for i in range(len(self.population)):
            for j in range(i + 1, len(self.population)):
                dist = np.linalg.norm(self.population[i].genes - self.population[j].genes)
                distances.append(dist)
        
        return np.mean(distances)
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """Evolution progress report"""
        if not self.fitness_history:
            return {"error": "No evolution data available"}
        
        best_fitness = max(self.fitness_history)
        final_fitness = self.fitness_history[-1]
        
        return {
            'evolution_summary': {
                'total_generations': self.generation + 1,
                'best_fitness': best_fitness,
                'final_fitness': final_fitness,
                'improvement': best_fitness - (self.fitness_history[0] if self.fitness_history else 0),
                'convergence_generation': self.evolution_stats['convergence_generation']
            },
            'population_statistics': {
                'population_size': len(self.population),
                'diversity_score': self._calculate_diversity(),
                'avg_fitness': np.mean([ind.fitness for ind in self.population]),
                'fitness_variance': np.var([ind.fitness for ind in self.population])
            },
            'genetic_operations': {
                'total_mutations': self.evolution_stats['total_mutations'],
                'total_crossovers': self.evolution_stats['total_crossovers'],
                'mutation_rate': self.evolution_stats['total_mutations'] / (self.generation + 1) if self.generation > 0 else 0,
                'crossover_rate': self.evolution_stats['total_crossovers'] / (self.generation + 1) if self.generation > 0 else 0
            },
            'fitness_trend': {
                'fitness_history': self.fitness_history[-50:],  # Last 50 generations
                'convergence_history': self.convergence_history[-50:]
            },
            'best_individual': {
                'genes': self.best_individual.genes.tolist() if self.best_individual else None,
                'fitness': self.best_individual.fitness if self.best_individual else None,
                'generation': self.best_individual.generation if self.best_individual else None
            }
        }

class ParticleSwarmOptimization:
    """Particle Swarm Optimization for model parameter tuning"""
    
    def __init__(self, config: EvolutionConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.PSO")
        
        # PSO parameters
        self.inertia_weight = 0.9
        self.cognitive_weight = 2.0
        self.social_weight = 2.0
        
        # Swarm state
        self.particles = []
        self.velocities = []
        self.personal_best_positions = []
        self.personal_best_scores = []
        self.global_best_position = None
        self.global_best_score = float('-inf')
        
        # Evolution history
        self.iteration_history = []
        self.convergence_history = []
        
        # Fitness function
        self.fitness_function: Optional[Callable] = None
    
    def set_fitness_function(self, fitness_func: Callable[[np.ndarray], float]) -> None:
        """Fitness function ni o'rnatish"""
        self.fitness_function = fitness_func
    
    def optimize(self, bounds: List[Tuple[float, float]], 
                 n_iterations: Optional[int] = None) -> Tuple[np.ndarray, float]:
        """PSO optimization"""
        if self.fitness_function is None:
            raise ValueError("Fitness function must be set before optimization")
        
        n_iterations = n_iterations or self.config.max_generations
        n_dimensions = len(bounds)
        
        # Initialize swarm
        self._initialize_swarm(bounds)
        
        # Optimization loop
        for iteration in range(n_iterations):
            # Evaluate all particles
            for i in range(self.config.population_size):
                score = self.fitness_function(self.particles[i])
                
                # Update personal best
                if score > self.personal_best_scores[i]:
                    self.personal_best_scores[i] = score
                    self.personal_best_positions[i] = self.particles[i].copy()
                
                # Update global best
                if score > self.global_best_score:
                    self.global_best_score = score
                    self.global_best_position = self.particles[i].copy()
            
            # Update velocities and positions
            self._update_particles(bounds, n_dimensions)
            
            # Record iteration data
            self.iteration_history.append({
                'iteration': iteration,
                'global_best_score': self.global_best_score,
                'average_score': np.mean(self.personal_best_scores),
                'diversity': self._calculate_swarm_diversity()
            })
            
            # Adaptive parameters
            self._adapt_parameters(iteration, n_iterations)
            
            # Log progress
            if iteration % 10 == 0:
                self.logger.info(
                    f"PSO Iteration {iteration}: Global best = {self.global_best_score:.6f}, "
                    f"Swarm diversity = {self._calculate_swarm_diversity():.4f}"
                )
        
        self.logger.info(f"PSO optimization completed. Best score: {self.global_best_score:.6f}")
        return self.global_best_position, self.global_best_score
    
    def _initialize_swarm(self, bounds: List[Tuple[float, float]]) -> None:
        """Swarm ni inicializatsiya qilish"""
        self.particles = []
        self.velocities = []
        self.personal_best_positions = []
        self.personal_best_scores = []
        
        for _ in range(self.config.population_size):
            # Random position within bounds
            position = np.array([
                np.random.uniform(low, high) 
                for low, high in bounds
            ])
            
            # Random velocity
            velocity = np.random.uniform(-1, 1, len(bounds))
            
            self.particles.append(position)
            self.velocities.append(velocity)
            self.personal_best_positions.append(position.copy())
            self.personal_best_scores.append(float('-inf'))
        
        self.global_best_position = None
        self.global_best_score = float('-inf')
    
    def _update_particles(self, bounds: List[Tuple[float, float]], n_dimensions: int) -> None:
        """Particle velocities va positions ni yangilash"""
        for i in range(self.config.population_size):
            # Update velocity
            r1, r2 = np.random.random(2)
            
            cognitive_component = self.cognitive_weight * r1 * (
                self.personal_best_positions[i] - self.particles[i]
            )
            social_component = self.social_weight * r2 * (
                self.global_best_position - self.particles[i]
            )
            
            self.velocities[i] = (
                self.inertia_weight * self.velocities[i] + 
                cognitive_component + 
                social_component
            )
            
            # Apply velocity limits
            max_velocity = 0.5
            self.velocities[i] = np.clip(self.velocities[i], -max_velocity, max_velocity)
            
            # Update position
            self.particles[i] += self.velocities[i]
            
            # Apply bounds constraints
            for j in range(n_dimensions):
                if self.particles[i][j] < bounds[j][0]:
                    self.particles[i][j] = bounds[j][0]
                    self.velocities[i][j] *= -0.5  # Bounce back
                elif self.particles[i][j] > bounds[j][1]:
                    self.particles[i][j] = bounds[j][1]
                    self.velocities[i][j] *= -0.5  # Bounce back
    
    def _calculate_swarm_diversity(self) -> float:
        """Swarm diversity ni hisoblash"""
        if len(self.particles) < 2:
            return 0.0
        
        centroid = np.mean(self.particles, axis=0)
        distances = [np.linalg.norm(particle - centroid) for particle in self.particles]
        return np.mean(distances)
    
    def _adapt_parameters(self, iteration: int, total_iterations: int) -> None:
        """PSO parameters ni adapt qilish"""
        # Linear decrease in inertia weight
        self.inertia_weight = 0.9 - (0.4 * iteration / total_iterations)

class ModelEvolutionaryOptimizer:
    """Model parameter evolution using evolutionary strategies"""
    
    def __init__(self, config: EvolutionConfig, model_class: type):
        self.config = config
        self.model_class = model_class
        self.logger = logging.getLogger(f"{__name__}.ModelEvolutionaryOptimizer")
        
        self.best_model_params = None
        self.optimization_history = []
        self.model_templates = {}
    
    def optimize_model_parameters(self, param_bounds: Dict[str, Tuple[float, float]], 
                                X_train: np.ndarray, y_train: np.ndarray,
                                X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Model parameters ni evolutionary optimization qilish"""
        
        # Convert parameter bounds to list format for GA
        param_names = list(param_bounds.keys())
        bounds_list = [param_bounds[name] for name in param_names]
        
        # Define fitness function
        def fitness_function(individual: Individual) -> float:
            # Convert genes to parameters
            params = {}
            for i, name in enumerate(param_names):
                params[name] = individual.genes[i]
            
            # Create and evaluate model
            try:
                model = self.model_class(**params)
                model.fit(X_train, y_train)
                predictions = model.predict(X_val)
                score = accuracy_score(y_val, predictions)
                return score
            except Exception as e:
                self.logger.warning(f"Fitness evaluation failed: {e}")
                return 0.0
        
        # Initialize and run genetic algorithm
        ga = GeneticAlgorithm(self.config)
        ga.set_fitness_function(fitness_function)
        
        best_individual = ga.evolve(bounds_list)
        
        # Convert best genes back to parameters
        self.best_model_params = {
            name: best_individual.genes[i] 
            for i, name in enumerate(param_names)
        }
        
        # Get optimization report
        report = ga.get_evolution_report()
        
        return {
            'best_parameters': self.best_model_params,
            'best_score': best_individual.fitness,
            'optimization_report': report,
            'evolution_stats': ga.evolution_stats
        }
    
    def optimize_hyperparameters_advanced(self, param_grid: Dict[str, List], 
                                        X_train: np.ndarray, y_train: np.ndarray,
                                        X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Advanced hyperparameter optimization with multiple strategies"""
        
        results = {}
        
        # 1. Grid Search
        grid_results = self._grid_search(param_grid, X_train, y_train, X_val, y_val)
        results['grid_search'] = grid_results
        
        # 2. Genetic Algorithm
        ga_results = self._genetic_algorithm_optimization(param_grid, X_train, y_train, X_val, y_val)
        results['genetic_algorithm'] = ga_results
        
        # 3. PSO
        pso_results = self._pso_optimization(param_grid, X_train, y_train, X_val, y_val)
        results['particle_swarm'] = pso_results
        
        # Compare and select best
        best_method = max(results.keys(), key=lambda k: results[k]['best_score'])
        best_result = results[best_method]
        
        self.best_model_params = best_result['best_parameters']
        
        self.logger.info(f"Advanced optimization completed. Best method: {best_method} "
                        f"with score: {best_result['best_score']:.6f}")
        
        return {
            'best_method': best_method,
            'best_parameters': self.best_model_params,
            'best_score': best_result['best_score'],
            'all_results': results,
            'comparison': {
                method: {
                    'score': result['best_score'],
                    'parameters': result['best_parameters']
                }
                for method, result in results.items()
            }
        }
    
    def _grid_search(self, param_grid: Dict[str, List], 
                    X_train: np.ndarray, y_train: np.ndarray,
                    X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Grid search optimization"""
        best_score = 0.0
        best_params = {}
        
        # Generate all parameter combinations
        param_combinations = self._generate_param_combinations(param_grid)
        
        for params in param_combinations:
            try:
                model = self.model_class(**params)
                model.fit(X_train, y_train)
                predictions = model.predict(X_val)
                score = accuracy_score(y_val, predictions)
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
            except Exception as e:
                continue
        
        return {
            'method': 'grid_search',
            'best_parameters': best_params,
            'best_score': best_score,
            'total_combinations': len(param_combinations)
        }
    
    def _genetic_algorithm_optimization(self, param_grid: Dict[str, List],
                                      X_train: np.ndarray, y_train: np.ndarray,
                                      X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Genetic algorithm optimization"""
        # Convert parameter grid to bounds
        param_names = list(param_grid.keys())
        
        # For continuous parameters, use min/max bounds
        bounds_list = []
        for name in param_names:
            values = param_grid[name]
            if all(isinstance(v, (int, float)) for v in values):
                bounds_list.append((min(values), max(values)))
            else:
                # Categorical parameters - use indices
                bounds_list.append((0, len(values) - 1))
        
        # Fitness function
        def fitness_function(individual: Individual) -> float:
            params = {}
            for i, name in enumerate(param_names):
                if all(isinstance(v, (int, float)) for v in param_grid[name]):
                    # Continuous parameter
                    params[name] = individual.genes[i]
                else:
                    # Categorical parameter
                    param_index = int(round(individual.genes[i]))
                    param_index = max(0, min(param_index, len(param_grid[name]) - 1))
                    params[name] = param_grid[name][param_index]
            
            try:
                model = self.model_class(**params)
                model.fit(X_train, y_train)
                predictions = model.predict(X_val)
                score = accuracy_score(y_val, predictions)
                return score
            except:
                return 0.0
        
        # Run genetic algorithm
        ga = GeneticAlgorithm(self.config)
        ga.set_fitness_function(fitness_function)
        
        best_individual = ga.evolve(bounds_list)
        
        # Convert best genes back to parameters
        best_params = {}
        for i, name in enumerate(param_names):
            if all(isinstance(v, (int, float)) for v in param_grid[name]):
                best_params[name] = best_individual.genes[i]
            else:
                param_index = int(round(best_individual.genes[i]))
                param_index = max(0, min(param_index, len(param_grid[name]) - 1))
                best_params[name] = param_grid[name][param_index]
        
        return {
            'method': 'genetic_algorithm',
            'best_parameters': best_params,
            'best_score': best_individual.fitness,
            'optimization_report': ga.get_evolution_report()
        }
    
    def _pso_optimization(self, param_grid: Dict[str, List],
                        X_train: np.ndarray, y_train: np.ndarray,
                        X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """PSO optimization"""
        # Convert parameter grid to bounds
        param_names = list(param_grid.keys())
        
        bounds_list = []
        for name in param_names:
            values = param_grid[name]
            if all(isinstance(v, (int, float)) for v in values):
                bounds_list.append((min(values), max(values)))
            else:
                bounds_list.append((0, len(values) - 1))
        
        # Fitness function
        def fitness_function(genes: np.ndarray) -> float:
            params = {}
            for i, name in enumerate(param_names):
                if all(isinstance(v, (int, float)) for v in param_grid[name]):
                    params[name] = genes[i]
                else:
                    param_index = int(round(genes[i]))
                    param_index = max(0, min(param_index, len(param_grid[name]) - 1))
                    params[name] = param_grid[name][param_index]
            
            try:
                model = self.model_class(**params)
                model.fit(X_train, y_train)
                predictions = model.predict(X_val)
                score = accuracy_score(y_val, predictions)
                return score
            except:
                return 0.0
        
        # Run PSO
        pso = ParticleSwarmOptimization(self.config)
        pso.set_fitness_function(fitness_function)
        
        best_position, best_score = pso.optimize(bounds_list)
        
        # Convert best position back to parameters
        best_params = {}
        for i, name in enumerate(param_names):
            if all(isinstance(v, (int, float)) for v in param_grid[name]):
                best_params[name] = best_position[i]
            else:
                param_index = int(round(best_position[i]))
                param_index = max(0, min(param_index, len(param_grid[name]) - 1))
                best_params[name] = param_grid[name][param_index]
        
        return {
            'method': 'particle_swarm_optimization',
            'best_parameters': best_params,
            'best_score': best_score,
            'optimization_history': pso.iteration_history
        }
    
    def _generate_param_combinations(self, param_grid: Dict[str, List]) -> List[Dict[str, Any]]:
        """Generate all parameter combinations for grid search"""
        param_names = list(param_grid.keys())
        param_values = [param_grid[name] for name in param_names]
        
        # Use itertools.product to generate combinations
        from itertools import product
        
        combinations = []
        for values in product(*param_values):
            params = dict(zip(param_names, values))
            combinations.append(params)
        
        return combinations