#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evolution Analytics Engine
==========================

Advanced evolution analytics tizimi:
- Machine learning prediction
- Evolutionary algorithms
- Genetic programming
- Parameter optimization
- Strategy mutation
- Hybrid strategies
- Ensemble evolution
- Performance forecasting

Author: Orion Starline AI Team
Date: 2025-11-04
"""

import numpy as np
import pandas as pd
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
from abc import ABC, abstractmethod
import pickle
import joblib

# Machine learning imports
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Genetic algorithm imports
from deap import base, creator, tools, algorithms
import random

warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PredictionModel(Enum):
    """Prediction model turlari"""
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    LINEAR_REGRESSION = "linear_regression"

class EvolutionPhase(Enum):
    """Strategy evolution bosqichlari"""
    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    ADAPTATION = "adaptation"
    OPTIMIZATION = "optimization"
    CONVERGENCE = "convergence"

@dataclass
class EvolutionPrediction:
    """Evolution prediction natijasi"""
    prediction_id: str
    strategy_id: str
    predicted_period: str
    predicted_performance: float
    predicted_risk: float
    confidence_score: float
    prediction_date: datetime
    model_used: PredictionModel
    feature_importance: Dict[str, float]
    prediction_intervals: Dict[str, float]

@dataclass
class GeneticIndividual:
    """Genetic algorithm individual"""
    genome: Dict[str, Any]
    fitness: float
    performance_history: List[float]
    generation: int
    mutation_history: List[str]

@dataclass
class StrategyMutation:
    """Strategy mutation voqeasi"""
    mutation_id: str
    strategy_id: str
    parent_parameters: Dict[str, Any]
    child_parameters: Dict[str, Any]
    mutation_type: str
    performance_before: float
    performance_after: float
    success_score: float
    timestamp: datetime

class EvolutionAnalyticsEngine:
    """Evolution analytics engine asosiy klassi"""
    
    def __init__(self, db_path: str = "evolution_analytics.db"):
        self.db_path = db_path
        self.init_database()
        self.models = {}
        self.scalers = {}
        self.genetic_population = []
        self.ensemble_models = {}
        
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Predictions jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                predicted_period TEXT NOT NULL,
                predicted_performance REAL NOT NULL,
                predicted_risk REAL NOT NULL,
                confidence_score REAL NOT NULL,
                prediction_date TEXT NOT NULL,
                model_used TEXT NOT NULL,
                feature_importance TEXT NOT NULL,
                prediction_intervals TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Genetic individuals jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genetic_individuals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                individual_id TEXT NOT NULL,
                genome TEXT NOT NULL,
                fitness REAL NOT NULL,
                performance_history TEXT NOT NULL,
                generation INTEGER NOT NULL,
                mutation_history TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Strategy mutations jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_mutations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mutation_id TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                parent_parameters TEXT NOT NULL,
                child_parameters TEXT NOT NULL,
                mutation_type TEXT NOT NULL,
                performance_before REAL NOT NULL,
                performance_after REAL NOT NULL,
                success_score REAL NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance forecasts jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                forecast_id TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                forecast_horizon INTEGER NOT NULL,
                forecast_method TEXT NOT NULL,
                forecasted_returns TEXT NOT NULL,
                confidence_bounds TEXT NOT NULL,
                accuracy_metrics TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Evolution analytics database initialized")
    
    def train_evolution_prediction_model(self, strategy_id: str, model_type: PredictionModel = PredictionModel.RANDOM_FOREST) -> Dict[str, Any]:
        """Evolution prediction model o'qitish"""
        # Get historical data
        data = self._get_evolution_data(strategy_id, days=365)
        
        if len(data) < 50:
            return {"error": "Not enough data for training"}
        
        # Prepare features
        features = self._prepare_features(data)
        target = self._prepare_target(data)
        
        if features.empty or target.empty:
            return {"error": "Feature preparation failed"}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = MinMaxScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        if model_type == PredictionModel.RANDOM_FOREST:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == PredictionModel.GRADIENT_BOOSTING:
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_type == PredictionModel.NEURAL_NETWORK:
            model = MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
        else:
            model = RandomForestRegressor(random_state=42)
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        
        # Store model
        model_key = f"{strategy_id}_{model_type.value}"
        self.models[model_key] = model
        self.scalers[model_key] = scaler
        
        # Feature importance
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(features.columns, model.feature_importances_))
        else:
            feature_importance = {}
        
        training_results = {
            'strategy_id': strategy_id,
            'model_type': model_type.value,
            'mse': mse,
            'mae': mae,
            'r2_score': r2,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': feature_importance,
            'training_size': len(X_train),
            'test_size': len(X_test)
        }
        
        return training_results
    
    def _get_evolution_data(self, strategy_id: str, days: int = 365) -> pd.DataFrame:
        """Evolution ma'lumotlarini olish"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        
        # First check if strategy_snapshots table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_snapshots'")
        if not cursor.fetchone():
            # Create mock data if table doesn't exist
            conn.close()
            return self._create_mock_evolution_data(strategy_id, days)
        
        # Get strategy evolution data
        try:
            query = '''
                SELECT ss.*, 
                       CASE 
                           WHEN LAG(ss.performance) OVER (ORDER BY ss.timestamp) IS NOT NULL
                           THEN ss.performance - LAG(ss.performance) OVER (ORDER BY ss.timestamp)
                           ELSE 0
                       END as performance_change,
                       CASE 
                           WHEN LAG(ss.sharpe_ratio) OVER (ORDER BY ss.timestamp) IS NOT NULL
                           THEN ss.sharpe_ratio - LAG(ss.sharpe_ratio) OVER (ORDER BY ss.timestamp)
                           ELSE 0
                       END as sharpe_change
                FROM strategy_snapshots ss
                WHERE ss.strategy_id = ? AND ss.timestamp >= ?
                ORDER BY ss.timestamp
            '''
            
            df = pd.read_sql_query(query, conn, params=(strategy_id, start_date.isoformat()))
            conn.close()
            
            if df.empty:
                return self._create_mock_evolution_data(strategy_id, days)
            
            return df
            
        except Exception as e:
            print(f"SQL query failed: {e}")
            conn.close()
            return self._create_mock_evolution_data(strategy_id, days)
    
    def _create_mock_evolution_data(self, strategy_id: str, days: int) -> pd.DataFrame:
        """Mock evolution data yaratish"""
        dates = pd.date_range(end=datetime.now(), periods=min(days, 30), freq='D')
        
        # Generate mock data
        data = []
        for i, date in enumerate(dates):
            performance = 0.1 + np.random.normal(0, 0.02) + i * 0.001
            data.append({
                'timestamp': date.isoformat(),
                'strategy_id': strategy_id,
                'performance': max(0, performance),
                'sharpe_ratio': performance / 0.15 if performance > 0 else 0,
                'max_drawdown': max(0, -performance + np.random.normal(0, 0.01)),
                'volatility': abs(0.12 + np.random.normal(0, 0.02)),
                'win_rate': min(1, max(0, 0.55 + np.random.normal(0, 0.05))),
                'risk_level': 0.3 + np.random.normal(0, 0.05),
                'market_regime': np.random.choice(['bull', 'bear', 'sideways']),
                'performance_change': np.random.normal(0, 0.01),
                'sharpe_change': np.random.normal(0, 0.1)
            })
        
        return pd.DataFrame(data)
    
    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Feature preparation"""
        if data.empty:
            return pd.DataFrame()
        
        features = pd.DataFrame()
        
        # Current performance metrics
        features['performance'] = data['performance']
        features['sharpe_ratio'] = data['sharpe_ratio']
        features['max_drawdown'] = data['max_drawdown']
        features['volatility'] = data['volatility']
        features['win_rate'] = data['win_rate']
        features['risk_level'] = data['risk_level']
        
        # Historical features
        if len(data) > 1:
            features['performance_change'] = data['performance_change']
            features['sharpe_change'] = data['sharpe_change']
        
        # Rolling statistics
        window = min(5, len(data))
        if window > 1:
            features['performance_ma5'] = data['performance'].rolling(window).mean()
            features['volatility_ma5'] = data['volatility'].rolling(window).mean()
            features['sharpe_ma5'] = data['sharpe_ratio'].rolling(window).mean()
        
        # Time-based features
        timestamps = pd.to_datetime(data['timestamp'])
        features['day_of_week'] = timestamps.dt.dayofweek
        features['month'] = timestamps.dt.month
        features['quarter'] = timestamps.dt.quarter
        
        # Market regime encoding
        regime_mapping = {'bull': 1, 'bear': -1, 'sideways': 0, 'high_volatility': 2, 'low_volatility': -2}
        features['market_regime_encoded'] = data['market_regime'].map(regime_mapping)
        
        return features.fillna(0)
    
    def _prepare_target(self, data: pd.DataFrame) -> pd.Series:
        """Target preparation (next period performance)"""
        if len(data) < 2:
            return pd.Series()
        
        # Next period performance (can be adjusted)
        target = data['performance'].shift(-1)
        return target.dropna()
    
    def predict_evolution(self, strategy_id: str, model_type: PredictionModel = PredictionModel.RANDOM_FOREST, 
                         prediction_horizon: int = 30) -> EvolutionPrediction:
        """Strategy evolution predict qilish"""
        model_key = f"{strategy_id}_{model_type.value}"
        
        if model_key not in self.models:
            training_result = self.train_evolution_prediction_model(strategy_id, model_type)
            if "error" in training_result:
                raise ValueError(training_result["error"])
        
        # Get latest data
        latest_data = self._get_evolution_data(strategy_id, days=90)
        if latest_data.empty:
            raise ValueError("No recent data available")
        
        # Prepare features for prediction
        features = self._prepare_features(latest_data)
        if features.empty:
            raise ValueError("Feature preparation failed")
        
        # Use latest features
        latest_features = features.iloc[-1:].fillna(0)
        
        # Scale features
        scaler = self.scalers[model_key]
        model = self.models[model_key]
        
        features_scaled = scaler.transform(latest_features)
        
        # Make prediction
        predicted_performance = model.predict(features_scaled)[0]
        predicted_risk = self._estimate_risk(latest_features, predicted_performance)
        
        # Calculate confidence (simplified)
        confidence = self._calculate_prediction_confidence(model, features_scaled)
        
        # Feature importance
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(features.columns, model.feature_importances_))
        else:
            feature_importance = {}
        
        # Prediction intervals (bootstrap approach)
        prediction_intervals = self._calculate_prediction_intervals(model, features_scaled, n_bootstrap=100)
        
        prediction = EvolutionPrediction(
            prediction_id=f"{strategy_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            strategy_id=strategy_id,
            predicted_period=f"{prediction_horizon} days",
            predicted_performance=predicted_performance,
            predicted_risk=predicted_risk,
            confidence_score=confidence,
            prediction_date=datetime.now(),
            model_used=model_type,
            feature_importance=feature_importance,
            prediction_intervals=prediction_intervals
        )
        
        # Store prediction
        self._store_prediction(prediction)
        
        return prediction
    
    def _estimate_risk(self, features: pd.DataFrame, predicted_performance: float) -> float:
        """Risk estimate qilish"""
        # Simple risk estimation based on historical volatility and performance
        base_risk = features['volatility'].iloc[0] if not features.empty else 0.1
        
        # Adjust risk based on predicted performance
        performance_adjustment = abs(predicted_performance) * 0.5
        estimated_risk = base_risk + performance_adjustment
        
        return min(estimated_risk, 1.0)  # Cap at 1.0
    
    def _calculate_prediction_confidence(self, model, features: np.ndarray) -> float:
        """Prediction confidence hisoblash"""
        # Simple confidence based on model type
        if hasattr(model, 'predict_proba'):
            return 0.8
        else:
            return 0.6
    
    def _calculate_prediction_intervals(self, model, features: np.ndarray, n_bootstrap: int = 100) -> Dict[str, float]:
        """Prediction interval hisoblash"""
        try:
            # For tree-based models, use standard deviation of predictions
            if hasattr(model, 'estimators_'):
                predictions = []
                for estimator in model.estimators_[:min(10, len(model.estimators_))]:  # Limit for efficiency
                    pred = estimator.predict(features)[0]
                    predictions.append(pred)
                
                pred_mean = np.mean(predictions)
                pred_std = np.std(predictions)
                
                return {
                    'lower_90': pred_mean - 1.645 * pred_std,
                    'upper_90': pred_mean + 1.645 * pred_std,
                    'lower_95': pred_mean - 1.96 * pred_std,
                    'upper_95': pred_mean + 1.96 * pred_std,
                    'mean': pred_mean
                }
            else:
                # Fallback for other models
                return {
                    'lower_90': 0, 'upper_90': 0, 'lower_95': 0, 'upper_95': 0, 'mean': 0
                }
        except:
            return {
                'lower_90': 0, 'upper_90': 0, 'lower_95': 0, 'upper_95': 0, 'mean': 0
            }
    
    def _store_prediction(self, prediction: EvolutionPrediction):
        """Prediction ni saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (prediction_id, strategy_id, predicted_period, predicted_performance, 
             predicted_risk, confidence_score, prediction_date, model_used, 
             feature_importance, prediction_intervals)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction.prediction_id,
            prediction.strategy_id,
            prediction.predicted_period,
            prediction.predicted_performance,
            prediction.predicted_risk,
            prediction.confidence_score,
            prediction.prediction_date.isoformat(),
            prediction.model_used.value,
            json.dumps(prediction.feature_importance),
            json.dumps(prediction.prediction_intervals)
        ))
        
        conn.commit()
        conn.close()
    
    def run_genetic_algorithm(self, strategy_id: str, n_generations: int = 50, 
                            population_size: int = 50) -> List[GeneticIndividual]:
        """Genetic algorithm o'qitish"""
        # Define gene space
        gene_space = {
            'ma_period': (5, 50),
            'risk_per_trade': (0.001, 0.1),
            'stop_loss': (0.01, 0.2),
            'take_profit': (0.02, 0.5),
            'position_size': (0.1, 1.0)
        }
        
        # Create initial population
        population = self._create_initial_population(population_size, gene_space)
        
        # Evolution loop
        for generation in range(n_generations):
            # Evaluate fitness
            fitness_scores = [self._evaluate_fitness(individual) for individual in population]
            
            # Update fitness in population
            for i, fitness in enumerate(fitness_scores):
                population[i].fitness = fitness
                population[i].generation = generation
            
            # Select parents
            parents = self._tournament_selection(population, tournament_size=3)
            
            # Create offspring
            offspring = []
            for i in range(0, len(parents), 2):
                if i + 1 < len(parents):
                    child1, child2 = self._crossover(parents[i], parents[i+1])
                    child1 = self._mutate(child1, gene_space)
                    child2 = self._mutate(child2, gene_space)
                    offspring.extend([child1, child2])
            
            # Select next generation
            population = self._survivor_selection(population + offspring, population_size)
            
            if generation % 10 == 0:
                best_fitness = max(fitness_scores)
                logger.info(f"Generation {generation}: Best fitness = {best_fitness:.4f}")
        
        # Store final population
        self.genetic_population = population
        self._store_genetic_population(population)
        
        return sorted(population, key=lambda x: x.fitness, reverse=True)
    
    def _create_initial_population(self, size: int, gene_space: Dict[str, Tuple]) -> List[GeneticIndividual]:
        """Initial population yaratish"""
        population = []
        
        for i in range(size):
            genome = {}
            for gene_name, (min_val, max_val) in gene_space.items():
                if gene_name in ['ma_period']:
                    genome[gene_name] = random.randint(int(min_val), int(max_val))
                else:
                    genome[gene_name] = random.uniform(min_val, max_val)
            
            individual = GeneticIndividual(
                genome=genome,
                fitness=0.0,
                performance_history=[],
                generation=0,
                mutation_history=[]
            )
            population.append(individual)
        
        return population
    
    def _evaluate_fitness(self, individual: GeneticIndividual) -> float:
        """Individual fitness baholash"""
        # Simulated fitness calculation
        # In real implementation, this would run backtest with given parameters
        
        # Simple fitness function based on parameter ranges
        fitness = 0.0
        
        # Reward for balanced risk
        risk_balance = 1.0 - abs(individual.genome['risk_per_trade'] - 0.02) / 0.1
        fitness += risk_balance * 0.3
        
        # Reward for reasonable stop-loss/take-profit ratio
        sl_tp_ratio = individual.genome['stop_loss'] / individual.genome['take_profit']
        ratio_fitness = 1.0 - abs(sl_tp_ratio - 2.0) / 2.0
        fitness += max(0, ratio_fitness) * 0.3
        
        # Reward for moderate position size
        position_fitness = 1.0 - abs(individual.genome['position_size'] - 0.5) / 0.5
        fitness += position_fitness * 0.2
        
        # Reward for appropriate MA period
        ma_fitness = 1.0 - abs(individual.genome['ma_period'] - 20) / 30
        fitness += max(0, ma_fitness) * 0.2
        
        return max(0, fitness)
    
    def _tournament_selection(self, population: List[GeneticIndividual], 
                            tournament_size: int = 3) -> List[GeneticIndividual]:
        """Tournament selection"""
        selected = []
        for _ in range(len(population)):
            tournament = random.sample(population, min(tournament_size, len(population)))
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        return selected
    
    def _crossover(self, parent1: GeneticIndividual, parent2: GeneticIndividual) -> Tuple[GeneticIndividual, GeneticIndividual]:
        """Crossover operation"""
        # Uniform crossover
        child1_genome = {}
        child2_genome = {}
        
        for gene_name in parent1.genome.keys():
            if random.random() < 0.5:
                child1_genome[gene_name] = parent1.genome[gene_name]
                child2_genome[gene_name] = parent2.genome[gene_name]
            else:
                child1_genome[gene_name] = parent2.genome[gene_name]
                child2_genome[gene_name] = parent1.genome[gene_name]
        
        child1 = GeneticIndividual(
            genome=child1_genome,
            fitness=0.0,
            performance_history=[],
            generation=max(parent1.generation, parent2.generation) + 1,
            mutation_history=[]
        )
        
        child2 = GeneticIndividual(
            genome=child2_genome,
            fitness=0.0,
            performance_history=[],
            generation=max(parent1.generation, parent2.generation) + 1,
            mutation_history=[]
        )
        
        return child1, child2
    
    def _mutate(self, individual: GeneticIndividual, gene_space: Dict[str, Tuple], 
               mutation_rate: float = 0.1) -> GeneticIndividual:
        """Mutation operation"""
        mutated = individual
        
        for gene_name, (min_val, max_val) in gene_space.items():
            if random.random() < mutation_rate:
                if gene_name in ['ma_period']:
                    # Integer mutation
                    new_value = random.randint(int(min_val), int(max_val))
                else:
                    # Float mutation with gaussian noise
                    current_value = individual.genome[gene_name]
                    noise = random.gauss(0, (max_val - min_val) * 0.1)
                    new_value = np.clip(current_value + noise, min_val, max_val)
                
                individual.genome[gene_name] = new_value
                individual.mutation_history.append(f"{gene_name}: {new_value}")
        
        return individual
    
    def _survivor_selection(self, population: List[GeneticIndividual], 
                          survivor_size: int) -> List[GeneticIndividual]:
        """Survivor selection (elitism)"""
        # Sort by fitness and keep top survivors
        sorted_population = sorted(population, key=lambda x: x.fitness, reverse=True)
        return sorted_population[:survivor_size]
    
    def _store_genetic_population(self, population: List[GeneticIndividual]):
        """Genetic population saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for individual in population:
            cursor.execute('''
                INSERT INTO genetic_individuals 
                (individual_id, genome, fitness, performance_history, generation, mutation_history)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                f"{individual.genome.get('strategy_id', 'genetic')}_{individual.generation}",
                json.dumps(individual.genome),
                individual.fitness,
                json.dumps(individual.performance_history),
                individual.generation,
                json.dumps(individual.mutation_history)
            ))
        
        conn.commit()
        conn.close()
    
    def mutate_strategy(self, strategy_id: str, mutation_type: str = "parameter_tweak") -> StrategyMutation:
        """Strategy mutation qilish"""
        # Get current strategy parameters
        current_params = self._get_current_strategy_parameters(strategy_id)
        if not current_params:
            raise ValueError("Current strategy parameters not found")
        
        # Apply mutation
        if mutation_type == "parameter_tweak":
            new_params = self._parameter_tweak_mutation(current_params)
        elif mutation_type == "structural_change":
            new_params = self._structural_change_mutation(current_params)
        elif mutation_type == "hybrid_mutation":
            new_params = self._hybrid_mutation(current_params)
        else:
            new_params = current_params.copy()
        
        # Evaluate performance change
        performance_before = self._evaluate_strategy_performance(strategy_id, current_params)
        performance_after = self._evaluate_strategy_performance(strategy_id, new_params)
        
        success_score = (performance_after - performance_before) / abs(performance_before) if performance_before != 0 else 0
        
        mutation = StrategyMutation(
            mutation_id=f"{strategy_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            strategy_id=strategy_id,
            parent_parameters=current_params,
            child_parameters=new_params,
            mutation_type=mutation_type,
            performance_before=performance_before,
            performance_after=performance_after,
            success_score=success_score,
            timestamp=datetime.now()
        )
        
        self._store_mutation(mutation)
        return mutation
    
    def _get_current_strategy_parameters(self, strategy_id: str) -> Dict[str, Any]:
        """Current strategy parameters olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT parameters FROM strategy_snapshots 
            WHERE strategy_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (strategy_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            try:
                return json.loads(result[0])
            except:
                return {}
        return {}
    
    def _parameter_tweak_mutation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parameter tweak mutation"""
        new_params = params.copy()
        
        # Randomly adjust one parameter
        param_to_adjust = random.choice(list(params.keys()))
        current_value = params[param_to_adjust]
        
        # Adjust based on parameter type
        if param_to_adjust in ['ma_period']:
            adjustment = random.randint(-5, 5)
            new_value = max(1, current_value + adjustment)
        elif param_to_adjust in ['risk_per_trade', 'stop_loss', 'take_profit', 'position_size']:
            adjustment = random.uniform(-0.1, 0.1) * current_value
            new_value = max(0.001, current_value + adjustment)
        else:
            adjustment = random.uniform(-0.05, 0.05) * current_value
            new_value = current_value + adjustment
        
        new_params[param_to_adjust] = new_value
        return new_params
    
    def _structural_change_mutation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Structural change mutation"""
        new_params = params.copy()
        
        # Add or remove parameters
        if random.random() < 0.5:
            # Add new parameter
            new_param_name = f"param_{random.randint(100, 999)}"
            new_params[new_param_name] = random.uniform(0.01, 0.1)
        else:
            # Remove random parameter (if more than 2 exist)
            if len(params) > 2:
                param_to_remove = random.choice([k for k in params.keys() if not k.startswith('param_')])
                del new_params[param_to_remove]
        
        return new_params
    
    def _hybrid_mutation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Hybrid mutation (combines multiple strategies)"""
        # Simulate hybrid strategy creation
        new_params = params.copy()
        
        # Blend with random other strategy parameters
        hybrid_factor = random.uniform(0.1, 0.3)
        
        for key, value in params.items():
            noise = random.uniform(-0.1, 0.1) * value
            new_value = value * (1 - hybrid_factor) + noise * hybrid_factor
            new_params[key] = max(0, new_value)
        
        return new_params
    
    def _evaluate_strategy_performance(self, strategy_id: str, parameters: Dict[str, Any]) -> float:
        """Strategy performance baholash"""
        # Simplified performance evaluation
        # In real implementation, this would run a backtest
        
        base_performance = 0.1  # 10% base performance
        
        # Adjust based on parameter quality
        risk_adj = -abs(parameters.get('risk_per_trade', 0.02) - 0.02) * 5
        ma_adj = -abs(parameters.get('ma_period', 20) - 20) * 0.01
        size_adj = -abs(parameters.get('position_size', 0.5) - 0.5) * 0.2
        
        performance = base_performance + risk_adj + ma_adj + size_adj
        return max(0, performance)
    
    def _store_mutation(self, mutation: StrategyMutation):
        """Mutation saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO strategy_mutations 
            (mutation_id, strategy_id, parent_parameters, child_parameters, 
             mutation_type, performance_before, performance_after, success_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            mutation.mutation_id,
            mutation.strategy_id,
            json.dumps(mutation.parent_parameters),
            json.dumps(mutation.child_parameters),
            mutation.mutation_type,
            mutation.performance_before,
            mutation.performance_after,
            mutation.success_score,
            mutation.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def create_ensemble_strategy(self, strategy_ids: List[str], ensemble_method: str = "weighted_average") -> Dict[str, Any]:
        """Ensemble strategy yaratish"""
        if len(strategy_ids) < 2:
            raise ValueError("At least 2 strategies required for ensemble")
        
        # Get strategy data
        strategies_data = {}
        for strategy_id in strategy_ids:
            data = self._get_evolution_data(strategy_id, days=90)
            if not data.empty:
                strategies_data[strategy_id] = data
        
        if len(strategies_data) < 2:
            raise ValueError("Insufficient data for ensemble")
        
        # Calculate ensemble weights
        if ensemble_method == "weighted_average":
            weights = self._calculate_performance_weights(strategies_data)
        elif ensemble_method == "risk_parity":
            weights = self._calculate_risk_parity_weights(strategies_data)
        elif ensemble_method == "sharpe_weighted":
            weights = self._calculate_sharpe_weights(strategies_data)
        else:
            # Equal weights
            weights = {sid: 1.0/len(strategies_data) for sid in strategies_data}
        
        # Create ensemble performance
        ensemble_performance = self._create_ensemble_performance(strategies_data, weights)
        
        # Analyze ensemble properties
        ensemble_analysis = {
            'ensemble_id': f"ensemble_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'component_strategies': strategy_ids,
            'ensemble_method': ensemble_method,
            'weights': weights,
            'ensemble_performance': ensemble_performance,
            'diversification_benefit': self._calculate_diversification_benefit(strategies_data, weights),
            'correlation_analysis': self._analyze_correlations(strategies_data),
            'risk_metrics': self._calculate_ensemble_risk(strategies_data, weights)
        }
        
        return ensemble_analysis
    
    def _calculate_performance_weights(self, strategies_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Performance-based weights hisoblash"""
        performance_scores = {}
        
        for strategy_id, data in strategies_data.items():
            if not data.empty:
                # Calculate performance score
                avg_performance = data['performance'].mean()
                performance_stability = 1.0 / (1.0 + data['performance'].std())
                score = avg_performance * performance_stability
                performance_scores[strategy_id] = max(0, score)
        
        if not performance_scores:
            return {sid: 1.0/len(strategies_data) for sid in strategies_data}
        
        # Normalize weights
        total_score = sum(performance_scores.values())
        if total_score > 0:
            weights = {sid: score/total_score for sid, score in performance_scores.items()}
        else:
            weights = {sid: 1.0/len(strategies_data) for sid in strategies_data}
        
        return weights
    
    def _calculate_risk_parity_weights(self, strategies_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Risk parity weights hisoblash"""
        risk_scores = {}
        
        for strategy_id, data in strategies_data.items():
            if not data.empty:
                # Risk as inverse of volatility
                risk = data['volatility'].mean()
                risk_scores[strategy_id] = 1.0 / (1.0 + risk) if risk > 0 else 1.0
        
        if not risk_scores:
            return {sid: 1.0/len(strategies_data) for sid in strategies_data}
        
        # Normalize weights
        total_score = sum(risk_scores.values())
        if total_score > 0:
            weights = {sid: score/total_score for sid, score in risk_scores.items()}
        else:
            weights = {sid: 1.0/len(strategies_data) for sid in strategies_data}
        
        return weights
    
    def _calculate_sharpe_weights(self, strategies_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Sharpe ratio based weights"""
        sharpe_scores = {}
        
        for strategy_id, data in strategies_data.items():
            if not data.empty and data['volatility'].mean() > 0:
                sharpe = data['performance'].mean() / data['volatility'].mean()
                sharpe_scores[strategy_id] = max(0, sharpe)
        
        if not sharpe_scores:
            return {sid: 1.0/len(strategies_data) for sid in strategies_data}
        
        # Normalize weights
        total_score = sum(sharpe_scores.values())
        if total_score > 0:
            weights = {sid: score/total_score for sid, score in sharpe_scores.items()}
        else:
            weights = {sid: 1.0/len(strategies_data) for sid in strategies_data}
        
        return weights
    
    def _create_ensemble_performance(self, strategies_data: Dict[str, pd.DataFrame], 
                                   weights: Dict[str, float]) -> Dict[str, float]:
        """Ensemble performance yaratish"""
        # Align all strategies to common dates
        common_dates = None
        for strategy_id, data in strategies_data.items():
            dates = set(pd.to_datetime(data['timestamp']))
            if common_dates is None:
                common_dates = dates
            else:
                common_dates = common_dates.intersection(dates)
        
        if not common_dates:
            return {'error': 'No common dates found'}
        
        # Create weighted ensemble
        ensemble_returns = []
        for date in sorted(common_dates):
            daily_return = 0
            for strategy_id, data in strategies_data.items():
                strategy_data = data[pd.to_datetime(data['timestamp']) == date]
                if not strategy_data.empty:
                    daily_return += weights[strategy_id] * strategy_data['performance'].iloc[0]
            ensemble_returns.append(daily_return)
        
        if not ensemble_returns:
            return {'error': 'No ensemble returns calculated'}
        
        # Calculate ensemble metrics
        ensemble_series = pd.Series(ensemble_returns)
        
        return {
            'total_return': (1 + ensemble_series).prod() - 1,
            'mean_return': ensemble_series.mean(),
            'volatility': ensemble_series.std(),
            'sharpe_ratio': ensemble_series.mean() / ensemble_series.std() if ensemble_series.std() > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(ensemble_series),
            'win_rate': (ensemble_series > 0).sum() / len(ensemble_series)
        }
    
    def _calculate_diversification_benefit(self, strategies_data: Dict[str, pd.DataFrame], 
                                         weights: Dict[str, float]) -> float:
        """Diversification foydasi hisoblash"""
        # Calculate weighted average of individual volatilities
        weighted_vol = 0
        for strategy_id, data in strategies_data.items():
            if not data.empty:
                vol = data['volatility'].mean()
                weighted_vol += weights[strategy_id] * vol
        
        # Calculate portfolio volatility (simplified)
        portfolio_vol = np.sqrt(sum(weights[sid]**2 for sid in strategies_data)) * weighted_vol
        
        # Diversification benefit as reduction in volatility
        avg_individual_vol = weighted_vol
        benefit = (avg_individual_vol - portfolio_vol) / avg_individual_vol if avg_individual_vol > 0 else 0
        
        return max(0, benefit)
    
    def _analyze_correlations(self, strategies_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Strategy o'rtasidagi korelyatsiya tahlili"""
        if len(strategies_data) < 2:
            return {}
        
        # Get performance data
        performance_data = {}
        for strategy_id, data in strategies_data.items():
            if not data.empty:
                performance_data[strategy_id] = data.set_index('timestamp')['performance']
        
        if len(performance_data) < 2:
            return {}
        
        # Calculate correlation matrix
        returns_df = pd.DataFrame(performance_data)
        correlation_matrix = returns_df.corr()
        
        # Extract pairwise correlations
        correlations = {}
        strategies = list(correlation_matrix.columns)
        for i in range(len(strategies)):
            for j in range(i+1, len(strategies)):
                strategy_pair = f"{strategies[i]}_vs_{strategies[j]}"
                correlations[strategy_pair] = correlation_matrix.iloc[i, j]
        
        return correlations
    
    def _calculate_ensemble_risk(self, strategies_data: Dict[str, pd.DataFrame], 
                               weights: Dict[str, float]) -> Dict[str, float]:
        """Ensemble risk metrikalari hisoblash"""
        # Simplified risk calculation
        total_weighted_risk = 0
        total_weighted_var = 0
        
        for strategy_id, data in strategies_data.items():
            if not data.empty:
                vol = data['volatility'].mean()
                var = vol ** 2
                total_weighted_risk += weights[strategy_id] * vol
                total_weighted_var += weights[strategy_id] * var
        
        return {
            'weighted_average_volatility': total_weighted_risk,
            'weighted_average_variance': total_weighted_var,
            'diversified_volatility': np.sqrt(total_weighted_var),
            'risk_reduction': total_weighted_risk - np.sqrt(total_weighted_var)
        }
    
    def forecast_performance(self, strategy_id: str, forecast_horizon: int = 30, 
                           method: str = "monte_carlo") -> Dict[str, Any]:
        """Performance forecast qilish"""
        if method == "monte_carlo":
            return self._monte_carlo_forecast(strategy_id, forecast_horizon)
        elif method == "time_series":
            return self._time_series_forecast(strategy_id, forecast_horizon)
        elif method == "machine_learning":
            return self._ml_forecast(strategy_id, forecast_horizon)
        else:
            return self._simple_forecast(strategy_id, forecast_horizon)
    
    def _monte_carlo_forecast(self, strategy_id: str, horizon: int) -> Dict[str, Any]:
        """Monte Carlo simulation forecast"""
        # Get historical performance
        data = self._get_evolution_data(strategy_id, days=180)
        if data.empty:
            return {"error": "Insufficient data for Monte Carlo simulation"}
        
        returns = data['performance'].values
        volatility = np.std(returns)
        mean_return = np.mean(returns)
        
        # Monte Carlo simulation
        n_simulations = 1000
        simulated_paths = []
        
        for _ in range(n_simulations):
            path = [mean_return]
            for _ in range(horizon - 1):
                # Random walk with mean reversion
                noise = np.random.normal(0, volatility)
                new_return = mean_return + 0.1 * (mean_return - path[-1]) + noise
                path.append(new_return)
            simulated_paths.append(path)
        
        # Calculate statistics
        simulated_paths = np.array(simulated_paths)
        
        forecasts = {
            'method': 'monte_carlo',
            'forecast_horizon': horizon,
            'n_simulations': n_simulations,
            'mean_forecast': np.mean(simulated_paths, axis=0).tolist(),
            'median_forecast': np.median(simulated_paths, axis=0).tolist(),
            'percentiles': {
                '5th': np.percentile(simulated_paths, 5, axis=0).tolist(),
                '25th': np.percentile(simulated_paths, 25, axis=0).tolist(),
                '75th': np.percentile(simulated_paths, 75, axis=0).tolist(),
                '95th': np.percentile(simulated_paths, 95, axis=0).tolist()
            },
            'probability_positive': (simulated_paths > 0).mean(axis=0).tolist(),
            'expected_cumulative_return': np.prod(1 + np.mean(simulated_paths, axis=0)) - 1,
            'confidence_level': 0.95
        }
        
        # Store forecast
        self._store_forecast(forecasts, strategy_id, horizon, "monte_carlo")
        
        return forecasts
    
    def _time_series_forecast(self, strategy_id: str, horizon: int) -> Dict[str, Any]:
        """Time series forecast"""
        # Simple AR(1) model
        data = self._get_evolution_data(strategy_id, days=180)
        if data.empty or len(data) < 10:
            return {"error": "Insufficient data for time series forecast"}
        
        returns = data['performance'].values
        
        # AR(1) estimation
        x = returns[:-1]
        y = returns[1:]
        
        # Simple regression
        slope = np.cov(x, y)[0, 1] / np.var(x) if np.var(x) > 0 else 0
        intercept = np.mean(y) - slope * np.mean(x)
        residuals = y - (intercept + slope * x)
        residual_std = np.std(residuals)
        
        # Forecast
        last_return = returns[-1]
        forecasts = []
        
        for i in range(horizon):
            if i == 0:
                forecast = intercept + slope * last_return
            else:
                forecast = intercept + slope * forecasts[-1]
            
            # Add uncertainty
            forecast += np.random.normal(0, residual_std)
            forecasts.append(forecast)
        
        return {
            'method': 'time_series',
            'forecast_horizon': horizon,
            'forecasts': forecasts,
            'model_params': {
                'slope': slope,
                'intercept': intercept,
                'residual_std': residual_std
            }
        }
    
    def _ml_forecast(self, strategy_id: str, horizon: int) -> Dict[str, Any]:
        """Machine learning forecast"""
        # This would use the trained ML model for forecasting
        try:
            prediction = self.predict_evolution(strategy_id, prediction_horizon=horizon)
            
            # Extend to multiple periods (simplified)
            forecasts = [prediction.predicted_performance] * horizon
            
            # Add some decay
            for i in range(1, horizon):
                forecasts[i] = forecasts[i-1] * 0.95  # Slight decay
            
            return {
                'method': 'machine_learning',
                'forecast_horizon': horizon,
                'forecasts': forecasts,
                'model_confidence': prediction.confidence_score,
                'feature_importance': prediction.feature_importance
            }
        except Exception as e:
            return {"error": f"ML forecast failed: {str(e)}"}
    
    def _simple_forecast(self, strategy_id: str, horizon: int) -> Dict[str, Any]:
        """Simple forecast based on recent performance"""
        data = self._get_evolution_data(strategy_id, days=30)
        if data.empty:
            return {"error": "Insufficient data for simple forecast"}
        
        recent_performance = data['performance'].tail(10).mean()
        forecasts = [recent_performance] * horizon
        
        return {
            'method': 'simple',
            'forecast_horizon': horizon,
            'forecasts': forecasts,
            'basis': 'recent_average_performance'
        }
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Maximum drawdown hisoblash"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _store_forecast(self, forecast: Dict[str, Any], strategy_id: str, horizon: int, method: str):
        """Forecast saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_forecasts 
            (forecast_id, strategy_id, forecast_horizon, forecast_method, 
             forecasted_returns, confidence_bounds, accuracy_metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"{strategy_id}_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            strategy_id,
            horizon,
            method,
            json.dumps(forecast.get('forecasts', forecast.get('mean_forecast', []))),
            json.dumps(forecast.get('percentiles', {})),
            json.dumps({'method': method, 'stored_at': datetime.now().isoformat()})
        ))
        
        conn.commit()
        conn.close()
    
    def get_evolution_analytics_summary(self, strategy_id: str) -> Dict[str, Any]:
        """Evolution analytics umumiy xulosasi"""
        summary = {
            'strategy_id': strategy_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'available_analytics': {
                'predictions': 'trained' if f"{strategy_id}_random_forest" in self.models else 'not_trained',
                'genetic_algorithm': 'available' if self.genetic_population else 'not_run',
                'mutations': self._get_mutation_count(strategy_id),
                'forecasts': 'available'
            },
            'recommendations': self._generate_recommendations(strategy_id)
        }
        
        return summary
    
    def _get_mutation_count(self, strategy_id: str) -> int:
        """Strategy uchun mutation sonini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM strategy_mutations WHERE strategy_id = ?
        ''', (strategy_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def _generate_recommendations(self, strategy_id: str) -> List[str]:
        """Tavsiyalar yaratish"""
        recommendations = []
        
        # Check if model is trained
        if f"{strategy_id}_random_forest" not in self.models:
            recommendations.append("Evolution prediction model o'qitish tavsiya etiladi")
        
        # Check genetic algorithm results
        if self.genetic_population:
            best_individual = max(self.genetic_population, key=lambda x: x.fitness)
            recommendations.append(f"Best genetic parameters: {best_individual.genome}")
        
        # Check mutation success
        mutation_count = self._get_mutation_count(strategy_id)
        if mutation_count == 0:
            recommendations.append("Strategy mutations amalga oshirish tavsiya etiladi")
        elif mutation_count < 5:
            recommendations.append("Ko'proq strategy mutations sinash tavsiya etiladi")
        
        return recommendations

# Usage example
if __name__ == "__main__":
    # Initialize engine
    engine = EvolutionAnalyticsEngine()
    
    # Train prediction model
    training_result = engine.train_evolution_prediction_model("EURUSD_TREND_001")
    print("Training Result:", json.dumps(training_result, indent=2, default=str))
    
    # Make prediction
    try:
        prediction = engine.predict_evolution("EURUSD_TREND_001")
        print("Prediction:", json.dumps(asdict(prediction), indent=2, default=str))
    except Exception as e:
        print(f"Prediction failed: {e}")
    
    # Run genetic algorithm
    try:
        best_individuals = engine.run_genetic_algorithm("EURUSD_TREND_001", n_generations=10)
        print("Best Genetic Individual:", json.dumps(asdict(best_individuals[0]), indent=2, default=str))
    except Exception as e:
        print(f"Genetic algorithm failed: {e}")
    
    # Get summary
    summary = engine.get_evolution_analytics_summary("EURUSD_TREND_001")
    print("Analytics Summary:", json.dumps(summary, indent=2, default=str))