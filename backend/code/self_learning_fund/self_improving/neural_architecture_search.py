"""
Neural Architecture Search (NAS) - Automatic neural network architecture design
Efficient architecture search using evolutionary strategies va reinforcement learning
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import random
import copy
from abc import ABC, abstractmethod
import json
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

@dataclass
class NASConfig:
    """Neural Architecture Search konfiguratsiyasi"""
    search_space_size: int = 10000
    population_size: int = 50
    generations: int = 100
    mutation_rate: float = 0.3
    crossover_rate: float = 0.7
    elite_size: int = 10
    max_hidden_layers: int = 6
    max_neurons_per_layer: int = 512
    min_neurons_per_layer: int = 10
    allowed_activations: List[str] = field(default_factory=lambda: ['relu', 'tanh', 'logistic'])
    allowed_optimizers: List[str] = field(default_factory=lambda: ['adam', 'lbfgs', 'sgd'])
    regularization_options: List[float] = field(default_factory=lambda: [0.0001, 0.001, 0.01, 0.1])
    learning_rates: List[float] = field(default_factory=lambda: [0.0001, 0.001, 0.01, 0.1, 1.0])
    
    # Early stopping
    patience: int = 20
    min_delta: float = 0.001
    
    # Search strategies
    search_strategy: str = 'evolutionary'  # 'evolutionary', 'random', 'bayesian'
    parallel_evaluation: bool = True
    max_evaluation_time: int = 300  # seconds

@dataclass
class ArchitectureGene:
    """Neural network architecture representation"""
    hidden_layer_sizes: List[int]
    activation: str
    solver: str
    alpha: float  # L2 regularization
    learning_rate_init: float
    learning_rate: str  # 'constant', 'adaptive', 'invscaling'
    
    # Additional parameters
    early_stopping: bool = True
    validation_fraction: float = 0.1
    beta_1: float = 0.9
    beta_2: float = 0.999
    epsilon: float = 1e-8
    n_iter_no_change: int = 10
    max_iter: int = 1000
    
    fitness: float = 0.0
    training_time: float = 0.0
    validation_score: float = 0.0
    generation: int = 0
    
    def copy(self) -> 'ArchitectureGene':
        """Create a copy of the architecture gene"""
        return ArchitectureGene(
            hidden_layer_sizes=self.hidden_layer_sizes.copy(),
            activation=self.activation,
            solver=self.solver,
            alpha=self.alpha,
            learning_rate_init=self.learning_rate_init,
            learning_rate=self.learning_rate,
            early_stopping=self.early_stopping,
            validation_fraction=self.validation_fraction,
            beta_1=self.beta_1,
            beta_2=self.beta_2,
            epsilon=self.epsilon,
            n_iter_no_change=self.n_iter_no_change,
            max_iter=self.max_iter,
            fitness=self.fitness,
            training_time=self.training_time,
            validation_score=self.validation_score,
            generation=self.generation
        )

class ArchitectureSpace:
    """Neural network architecture search space"""
    
    def __init__(self, config: NASConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ArchitectureSpace")
        
        # Define search space boundaries
        self.layer_bounds = (1, config.max_hidden_layers)
        self.neuron_bounds = (config.min_neurons_per_layer, config.max_neurons_per_layer)
        
    def generate_random_architecture(self, generation: int = 0) -> ArchitectureGene:
        """Generate random architecture"""
        # Random number of hidden layers
        n_layers = random.randint(self.layer_bounds[0], self.layer_bounds[1])
        
        # Random neurons per layer (could decrease/increase)
        if n_layers == 1:
            hidden_layers = [random.randint(*self.neuron_bounds)]
        else:
            # Create layers with some pattern
            base_neurons = random.randint(self.neuron_bounds[0], self.neuron_bounds[1] // 2)
            hidden_layers = []
            
            for i in range(n_layers):
                if random.random() < 0.3:  # 30% chance of pattern change
                    # New pattern
                    layer_size = random.randint(self.neuron_bounds[0], self.neuron_bounds[1])
                else:
                    # Continue pattern or random
                    if i == 0:
                        layer_size = base_neurons
                    elif random.random() < 0.5:
                        # Increasing
                        layer_size = min(base_neurons + i * 10, self.neuron_bounds[1])
                    else:
                        # Decreasing
                        layer_size = max(base_neurons - i * 10, self.neuron_bounds[0] // 2)
                    
                    layer_size = random.randint(self.neuron_bounds[0], self.neuron_bounds[1])
                
                hidden_layers.append(layer_size)
        
        # Random hyperparameters
        activation = random.choice(self.config.allowed_activations)
        solver = random.choice(self.config.allowed_optimizers)
        alpha = random.choice(self.config.regularization_options)
        learning_rate_init = random.choice(self.config.learning_rates)
        learning_rate_type = random.choice(['constant', 'adaptive'])
        
        return ArchitectureGene(
            hidden_layer_sizes=hidden_layers,
            activation=activation,
            solver=solver,
            alpha=alpha,
            learning_rate_init=learning_rate_init,
            learning_rate=learning_rate_type,
            generation=generation
        )
    
    def mutate_architecture(self, parent: ArchitectureGene) -> ArchitectureGene:
        """Mutate architecture"""
        child = parent.copy()
        
        # Randomly choose mutation type
        mutation_type = random.choice([
            'layer_count', 'layer_size', 'activation', 'optimizer', 
            'learning_rate', 'regularization', 'comprehensive'
        ])
        
        if mutation_type == 'layer_count' or mutation_type == 'comprehensive':
            # Add or remove layers
            if len(child.hidden_layer_sizes) < self.config.max_hidden_layers and random.random() < 0.5:
                # Add layer
                new_layer_size = random.randint(*self.neuron_bounds)
                insert_pos = random.randint(0, len(child.hidden_layer_sizes))
                child.hidden_layer_sizes.insert(insert_pos, new_layer_size)
            elif len(child.hidden_layer_sizes) > 1:
                # Remove layer
                remove_pos = random.randint(0, len(child.hidden_layer_sizes) - 1)
                child.hidden_layer_sizes.pop(remove_pos)
        
        if mutation_type == 'layer_size' or mutation_type == 'comprehensive':
            # Modify layer sizes
            if child.hidden_layer_sizes:
                layer_idx = random.randint(0, len(child.hidden_layer_sizes) - 1)
                current_size = child.hidden_layer_sizes[layer_idx]
                
                # Different mutation strategies
                mutation_strategy = random.choice(['random', 'increase', 'decrease', 'neighbor'])
                
                if mutation_strategy == 'random':
                    new_size = random.randint(*self.neuron_bounds)
                elif mutation_strategy == 'increase':
                    new_size = min(current_size + random.randint(5, 50), self.neuron_bounds[1])
                elif mutation_strategy == 'decrease':
                    new_size = max(current_size - random.randint(5, 50), self.neuron_bounds[0])
                else:  # neighbor
                    neighbor_size = random.choice(child.hidden_layer_sizes)
                    new_size = int((current_size + neighbor_size) / 2 + random.randint(-10, 10))
                    new_size = np.clip(new_size, *self.neuron_bounds)
                
                child.hidden_layer_sizes[layer_idx] = new_size
        
        if mutation_type == 'activation' or mutation_type == 'comprehensive':
            # Change activation function
            if random.random() < 0.5:  # 50% chance
                current_activation = child.activation
                available_activations = [a for a in self.config.allowed_activations if a != current_activation]
                if available_activations:
                    child.activation = random.choice(available_activations)
        
        if mutation_type == 'optimizer' or mutation_type == 'comprehensive':
            # Change optimizer
            if random.random() < 0.3:  # 30% chance
                current_solver = child.solver
                available_solvers = [s for s in self.config.allowed_optimizers if s != current_solver]
                if available_solvers:
                    child.solver = random.choice(available_solvers)
        
        if mutation_type == 'learning_rate' or mutation_type == 'comprehensive':
            # Modify learning rate
            if random.random() < 0.4:  # 40% chance
                current_lr = child.learning_rate_init
                lr_factor = random.uniform(0.5, 2.0)  # 50% to 200% of current
                child.learning_rate_init = np.clip(current_lr * lr_factor, 
                                                 min(self.config.learning_rates), 
                                                 max(self.config.learning_rates))
        
        if mutation_type == 'regularization' or mutation_type == 'comprehensive':
            # Modify regularization
            if random.random() < 0.3:  # 30% chance
                current_alpha = child.alpha
                alpha_factor = random.uniform(0.1, 10.0)
                new_alpha = current_alpha * alpha_factor
                new_alpha = max(min(new_alpha, 1.0), 0.00001)
                child.alpha = new_alpha
        
        return child
    
    def crossover_architectures(self, parent1: ArchitectureGene, parent2: ArchitectureGene) -> Tuple[ArchitectureGene, ArchitectureGene]:
        """Crossover two architectures"""
        # Simple crossover: combine layers from both parents
        
        # Determine crossover point for layers
        min_layers = min(len(parent1.hidden_layer_sizes), len(parent2.hidden_layer_sizes))
        if min_layers > 1:
            crossover_point = random.randint(1, min_layers - 1)
        else:
            crossover_point = 1
        
        # Create first child
        child1_layers = (parent1.hidden_layer_sizes[:crossover_point] + 
                        parent2.hidden_layer_sizes[crossover_point:])
        
        # Create second child
        child2_layers = (parent2.hidden_layer_sizes[:crossover_point] + 
                        parent1.hidden_layer_sizes[crossover_point:])
        
        # Combine other hyperparameters (randomly choose from parents)
        child1 = ArchitectureGene(
            hidden_layer_sizes=child1_layers,
            activation=parent1.activation if random.random() < 0.5 else parent2.activation,
            solver=parent1.solver if random.random() < 0.5 else parent2.solver,
            alpha=parent1.alpha if random.random() < 0.5 else parent2.alpha,
            learning_rate_init=parent1.learning_rate_init if random.random() < 0.5 else parent2.learning_rate_init,
            learning_rate=parent1.learning_rate if random.random() < 0.5 else parent2.learning_rate,
            generation=max(parent1.generation, parent2.generation) + 1
        )
        
        child2 = ArchitectureGene(
            hidden_layer_sizes=child2_layers,
            activation=parent2.activation if random.random() < 0.5 else parent1.activation,
            solver=parent2.solver if random.random() < 0.5 else parent1.solver,
            alpha=parent2.alpha if random.random() < 0.5 else parent1.alpha,
            learning_rate_init=parent2.learning_rate_init if random.random() < 0.5 else parent1.learning_rate_init,
            learning_rate=parent2.learning_rate if random.random() < 0.5 else parent1.learning_rate,
            generation=max(parent1.generation, parent2.generation) + 1
        )
        
        return child1, child2

class ArchitectureEvaluator:
    """Evaluate neural network architectures"""
    
    def __init__(self, config: NASConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ArchitectureEvaluator")
        
        # Performance history
        self.evaluation_cache = {}
        self.performance_history = []
        
    def evaluate_architecture(self, architecture: ArchitectureGene, 
                            X_train: np.ndarray, y_train: np.ndarray,
                            X_val: np.ndarray, y_val: np.ndarray) -> float:
        """Evaluate architecture performance"""
        
        # Create cache key
        cache_key = self._create_cache_key(architecture)
        
        if cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]
        
        try:
            # Create model based on architecture
            model = self._create_model_from_architecture(architecture)
            
            # Train model and measure performance
            start_time = datetime.now()
            
            # Training with early stopping
            model.fit(X_train, y_train)
            
            # Validation performance
            val_predictions = model.predict(X_val)
            
            # Calculate performance score
            if len(np.unique(y_val)) > 2:
                # Regression task
                val_score = -mean_squared_error(y_val, val_predictions)  # Negative MSE (higher is better)
            else:
                # Classification task
                val_score = accuracy_score(y_val, val_predictions)
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Store metrics
            architecture.validation_score = val_score
            architecture.training_time = training_time
            architecture.fitness = val_score
            
            # Multi-objective fitness (performance + efficiency)
            efficiency_score = 1.0 / (1.0 + training_time / 60.0)  # Prefer faster training
            architecture.fitness = val_score * 0.8 + efficiency_score * 0.2
            
            # Cache result
            self.evaluation_cache[cache_key] = architecture.fitness
            
            # Store in history
            self.performance_history.append({
                'architecture': architecture,
                'fitness': architecture.fitness,
                'validation_score': val_score,
                'training_time': training_time,
                'timestamp': datetime.now()
            })
            
            return architecture.fitness
            
        except Exception as e:
            self.logger.warning(f"Architecture evaluation failed: {e}")
            # Return very low score for failed architectures
            failed_fitness = -1.0
            self.evaluation_cache[cache_key] = failed_fitness
            architecture.fitness = failed_fitness
            return failed_fitness
    
    def _create_model_from_architecture(self, architecture: ArchitectureGene) -> Any:
        """Create sklearn model from architecture gene"""
        
        # Determine if it's classification or regression based on target
        # For now, assume classification (can be extended)
        model_params = {
            'hidden_layer_sizes': tuple(architecture.hidden_layer_sizes),
            'activation': architecture.activation,
            'solver': architecture.solver,
            'alpha': architecture.alpha,
            'learning_rate_init': architecture.learning_rate_init,
            'learning_rate': architecture.learning_rate,
            'early_stopping': architecture.early_stopping,
            'validation_fraction': architecture.validation_fraction,
            'beta_1': architecture.beta_1,
            'beta_2': architecture.beta_2,
            'epsilon': architecture.epsilon,
            'n_iter_no_change': architecture.n_iter_no_change,
            'max_iter': architecture.max_iter,
            'random_state': 42
        }
        
        return MLPClassifier(**model_params)
    
    def _create_cache_key(self, architecture: ArchitectureGene) -> str:
        """Create cache key for architecture"""
        # Create string representation of architecture
        arch_dict = {
            'layers': architecture.hidden_layer_sizes,
            'activation': architecture.activation,
            'solver': architecture.solver,
            'alpha': architecture.alpha,
            'lr_init': architecture.learning_rate_init,
            'lr_type': architecture.learning_rate
        }
        return json.dumps(arch_dict, sort_keys=True)
    
    def cross_validate_architecture(self, architecture: ArchitectureGene, 
                                  X: np.ndarray, y: np.ndarray, 
                                  cv_folds: int = 5) -> float:
        """Cross-validate architecture"""
        try:
            model = self._create_model_from_architecture(architecture)
            
            # Perform cross-validation
            scores = cross_val_score(model, X, y, cv=cv_folds, scoring='accuracy')
            
            return np.mean(scores)
        except Exception as e:
            self.logger.warning(f"Cross-validation failed: {e}")
            return 0.0

class NeuralArchitectureSearch:
    """Main Neural Architecture Search engine"""
    
    def __init__(self, config: NASConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.NAS")
        
        # Search components
        self.architecture_space = ArchitectureSpace(config)
        self.evaluator = ArchitectureEvaluator(config)
        
        # Search state
        self.population = []
        self.generation = 0
        self.best_architecture = None
        self.best_fitness = float('-inf')
        self.search_history = []
        
        # Performance tracking
        self.architecture_performance = {}
        self.generation_stats = []
        
    def search_architecture(self, X_train: np.ndarray, y_train: np.ndarray,
                          X_val: np.ndarray, y_val: np.ndarray) -> ArchitectureGene:
        """Search for best neural network architecture"""
        
        self.logger.info("Starting neural architecture search...")
        
        # Initialize population
        self._initialize_population()
        
        # Evolution loop
        for generation in range(self.config.generations):
            self.generation = generation
            
            # Evaluate population
            fitness_scores = self._evaluate_population(X_train, y_train, X_val, y_val)
            
            # Track best architecture
            best_idx = np.argmax(fitness_scores)
            current_best = self.population[best_idx]
            
            if current_best.fitness > self.best_fitness:
                self.best_fitness = current_best.fitness
                self.best_architecture = current_best.copy()
            
            # Generate next generation
            self._evolve_population()
            
            # Record generation statistics
            generation_stats = self._record_generation_stats(fitness_scores)
            self.generation_stats.append(generation_stats)
            
            # Log progress
            if generation % 10 == 0:
                self.logger.info(
                    f"Generation {generation}: Best fitness = {current_best.fitness:.4f}, "
                    f"Avg fitness = {np.mean(fitness_scores):.4f}, "
                    f"Architecture: {current_best.hidden_layer_sizes}"
                )
        
        self.logger.info(f"NAS completed. Best architecture fitness: {self.best_fitness:.4f}")
        return self.best_architecture
    
    def _initialize_population(self) -> None:
        """Initialize random population"""
        self.population = []
        
        for _ in range(self.config.population_size):
            architecture = self.architecture_space.generate_random_architecture()
            self.population.append(architecture)
    
    def _evaluate_population(self, X_train: np.ndarray, y_train: np.ndarray,
                           X_val: np.ndarray, y_val: np.ndarray) -> List[float]:
        """Evaluate all architectures in population"""
        
        fitness_scores = []
        
        if self.config.parallel_evaluation:
            # Parallel evaluation (simplified - would need multiprocessing for true parallelism)
            for architecture in self.population:
                fitness = self.evaluator.evaluate_architecture(architecture, X_train, y_train, X_val, y_val)
                fitness_scores.append(fitness)
        else:
            # Sequential evaluation
            for i, architecture in enumerate(self.population):
                try:
                    fitness = self.evaluator.evaluate_architecture(architecture, X_train, y_train, X_val, y_val)
                    fitness_scores.append(fitness)
                except Exception as e:
                    self.logger.warning(f"Failed to evaluate architecture {i}: {e}")
                    fitness_scores.append(-1.0)
        
        return fitness_scores
    
    def _evolve_population(self) -> None:
        """Evolve population to next generation"""
        # Sort population by fitness
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Elite preservation
        next_generation = self.population[:self.config.elite_size].copy()
        
        # Generate offspring
        while len(next_generation) < self.config.population_size:
            # Selection
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            # Crossover
            if random.random() < self.config.crossover_rate:
                child1, child2 = self.architecture_space.crossover_architectures(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            if random.random() < self.config.mutation_rate:
                child1 = self.architecture_space.mutate_architecture(child1)
            if random.random() < self.config.mutation_rate:
                child2 = self.architecture_space.mutate_architecture(child2)
            
            next_generation.extend([child1, child2])
        
        # Keep only required number
        self.population = next_generation[:self.config.population_size]
        
        # Update generation numbers
        for arch in self.population:
            arch.generation = self.generation + 1
    
    def _tournament_selection(self, tournament_size: int = 3) -> ArchitectureGene:
        """Tournament selection"""
        tournament = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(tournament, key=lambda x: x.fitness)
    
    def _record_generation_stats(self, fitness_scores: List[float]) -> Dict[str, Any]:
        """Record generation statistics"""
        return {
            'generation': self.generation,
            'best_fitness': np.max(fitness_scores),
            'avg_fitness': np.mean(fitness_scores),
            'worst_fitness': np.min(fitness_scores),
            'fitness_std': np.std(fitness_scores),
            'diversity': self._calculate_population_diversity()
        }
    
    def _calculate_population_diversity(self) -> float:
        """Calculate population diversity"""
        if len(self.population) < 2:
            return 0.0
        
        # Calculate diversity based on layer configurations
        layer_configs = [tuple(arch.hidden_layer_sizes) for arch in self.population]
        unique_configs = set(layer_configs)
        
        diversity = 1.0 - (len(unique_configs) / len(self.population))
        return diversity
    
    def get_search_results(self) -> Dict[str, Any]:
        """Get comprehensive search results"""
        if not self.best_architecture:
            return {'error': 'No search has been performed'}
        
        return {
            'best_architecture': {
                'hidden_layer_sizes': self.best_architecture.hidden_layer_sizes,
                'activation': self.best_architecture.activation,
                'solver': self.best_architecture.solver,
                'alpha': self.best_architecture.alpha,
                'learning_rate_init': self.best_architecture.learning_rate_init,
                'learning_rate': self.best_architecture.learning_rate,
                'fitness': self.best_architecture.fitness,
                'validation_score': self.best_architecture.validation_score,
                'training_time': self.best_architecture.training_time
            },
            'search_summary': {
                'generations': self.generation + 1,
                'population_size': self.config.population_size,
                'total_architectures_evaluated': len(self.evaluator.evaluation_cache),
                'best_fitness': self.best_fitness
            },
            'evolution_history': self.generation_stats,
            'top_architectures': self._get_top_architectures(10),
            'performance_statistics': self._get_performance_statistics()
        }
    
    def _get_top_architectures(self, n: int) -> List[Dict[str, Any]]:
        """Get top N architectures"""
        sorted_population = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        
        top_architectures = []
        for i, arch in enumerate(sorted_population[:n]):
            top_architectures.append({
                'rank': i + 1,
                'hidden_layer_sizes': arch.hidden_layer_sizes,
                'activation': arch.activation,
                'solver': arch.solver,
                'fitness': arch.fitness,
                'validation_score': arch.validation_score,
                'training_time': arch.training_time
            })
        
        return top_architectures
    
    def _get_performance_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.evaluator.performance_history:
            return {}
        
        fitness_values = [record['fitness'] for record in self.evaluator.performance_history]
        training_times = [record['training_time'] for record in self.evaluator.performance_history]
        
        return {
            'mean_fitness': np.mean(fitness_values),
            'std_fitness': np.std(fitness_values),
            'min_fitness': np.min(fitness_values),
            'max_fitness': np.max(fitness_values),
            'mean_training_time': np.mean(training_times),
            'std_training_time': np.std(training_times),
            'architecture_success_rate': len([f for f in fitness_values if f > 0]) / len(fitness_values)
        }
    
    def get_architecture_code(self, architecture: ArchitectureGene) -> str:
        """Generate Python code for the best architecture"""
        
        code = f"""
# Neural Network Architecture Generated by NAS
from sklearn.neural_network import MLPClassifier

# Best Architecture Configuration
architecture_config = {{
    'hidden_layer_sizes': {architecture.hidden_layer_sizes},
    'activation': '{architecture.activation}',
    'solver': '{architecture.solver}',
    'alpha': {architecture.alpha},
    'learning_rate_init': {architecture.learning_rate_init},
    'learning_rate': '{architecture.learning_rate}',
    'early_stopping': {architecture.early_stopping},
    'validation_fraction': {architecture.validation_fraction},
    'beta_1': {architecture.beta_1},
    'beta_2': {architecture.beta_2},
    'epsilon': {architecture.epsilon},
    'n_iter_no_change': {architecture.n_iter_no_change},
    'max_iter': {architecture.max_iter},
    'random_state': 42
}}

# Create and use the model
model = MLPClassifier(**architecture_config)
"""
        
        return code
    
    def visualize_architecture_evolution(self, save_path: str = None) -> Dict[str, str]:
        """Create visualizations of architecture evolution"""
        import matplotlib.pyplot as plt
        
        plots = {}
        
        if not self.generation_stats:
            return plots
        
        # Plot fitness evolution
        plt.figure(figsize=(12, 8))
        
        generations = [stat['generation'] for stat in self.generation_stats]
        best_fitness = [stat['best_fitness'] for stat in self.generation_stats]
        avg_fitness = [stat['avg_fitness'] for stat in self.generation_stats]
        
        plt.subplot(2, 2, 1)
        plt.plot(generations, best_fitness, 'b-', label='Best Fitness')
        plt.plot(generations, avg_fitness, 'r-', label='Average Fitness')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.title('Fitness Evolution')
        plt.legend()
        plt.grid(True)
        
        # Plot diversity evolution
        diversities = [stat['diversity'] for stat in self.generation_stats]
        plt.subplot(2, 2, 2)
        plt.plot(generations, diversities, 'g-')
        plt.xlabel('Generation')
        plt.ylabel('Population Diversity')
        plt.title('Population Diversity Evolution')
        plt.grid(True)
        
        # Plot architecture complexity over time
        if self.best_architecture:
            layer_counts = [len(arch.hidden_layer_sizes) for arch in self.population]
            plt.subplot(2, 2, 3)
            plt.hist(layer_counts, bins=range(1, max(layer_counts) + 2), alpha=0.7)
            plt.xlabel('Number of Hidden Layers')
            plt.ylabel('Frequency')
            plt.title('Architecture Complexity Distribution')
            plt.grid(True)
            
            # Plot neuron distribution
            all_neurons = []
            for arch in self.population:
                all_neurons.extend(arch.hidden_layer_sizes)
            
            plt.subplot(2, 2, 4)
            plt.hist(all_neurons, bins=20, alpha=0.7)
            plt.xlabel('Number of Neurons')
            plt.ylabel('Frequency')
            plt.title('Neuron Distribution')
            plt.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plot_path = f"{save_path}/nas_evolution_plots.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plots['evolution'] = plot_path
        
        plt.close()
        
        return plots

class BayesianArchitectureSearch:
    """Bayesian Optimization for Neural Architecture Search"""
    
    def __init__(self, config: NASConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.BayesianNAS")
        
        # Bayesian optimization components (simplified)
        self.evaluated_architectures = []
        self.performance_history = []
        self.acquisition_function = 'expected_improvement'
    
    def search_architecture(self, X_train: np.ndarray, y_train: np.ndarray,
                          X_val: np.ndarray, y_val: np.ndarray) -> ArchitectureGene:
        """Bayesian optimization search"""
        
        # Simplified Bayesian search (would use GPyOpt or similar in practice)
        best_architecture = None
        best_performance = float('-inf')
        
        # Initial random search
        n_initial = min(20, self.config.population_size // 2)
        for _ in range(n_initial):
            architecture = self.architecture_space.generate_random_architecture()
            performance = self._evaluate_single_architecture(architecture, X_train, y_train, X_val, y_val)
            
            if performance > best_performance:
                best_performance = performance
                best_architecture = architecture.copy()
            
            self.evaluated_architectures.append(architecture)
            self.performance_history.append(performance)
        
        # Bayesian optimization loop
        for iteration in range(n_initial, self.config.search_space_size):
            # Select next architecture using acquisition function
            next_architecture = self._select_next_architecture()
            
            # Evaluate
            performance = self._evaluate_single_architecture(next_architecture, X_train, y_train, X_val, y_val)
            
            # Update
            if performance > best_performance:
                best_performance = performance
                best_architecture = next_architecture.copy()
            
            self.evaluated_architectures.append(next_architecture)
            self.performance_history.append(performance)
            
            # Early stopping if convergence
            if len(self.performance_history) > 50:
                recent_performance = self.performance_history[-10:]
                if np.std(recent_performance) < 0.001:
                    break
        
        return best_architecture
    
    def _evaluate_single_architecture(self, architecture: ArchitectureGene,
                                    X_train: np.ndarray, y_train: np.ndarray,
                                    X_val: np.ndarray, y_val: np.ndarray) -> float:
        """Evaluate single architecture"""
        # Use ArchitectureEvaluator
        evaluator = ArchitectureEvaluator(self.config)
        return evaluator.evaluate_architecture(architecture, X_train, y_train, X_val, y_val)
    
    def _select_next_architecture(self) -> ArchitectureGene:
        """Select next architecture using acquisition function"""
        # Simplified acquisition - randomly select from mutations of best architecture
        if not self.evaluated_architectures:
            return self.architecture_space.generate_random_architecture()
        
        best_arch = max(self.evaluated_architectures, key=lambda x: x.fitness)
        
        # Generate several candidates and select best based on acquisition function
        candidates = []
        for _ in range(10):
            candidate = self.architecture_space.mutate_architecture(best_arch)
            candidates.append(candidate)
        
        # Simple acquisition function: prefer architectures with different layer counts
        best_candidate = None
        best_score = -float('inf')
        
        for candidate in candidates:
            # Acquisition score based on exploration vs exploitation
            diversity_score = abs(len(candidate.hidden_layer_sizes) - len(best_arch.hidden_layer_sizes))
            candidate.fitness = -diversity_score  # Placeholder
            candidates.sort(key=lambda x: x.fitness)
            
            if candidate.fitness > best_score:
                best_score = candidate.fitness
                best_candidate = candidate
        
        return best_candidate or self.architecture_space.generate_random_architecture()