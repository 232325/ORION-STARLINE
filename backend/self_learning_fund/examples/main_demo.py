"""
Asosiy demo - Self-Learning Trading Fund tizimini ishlatish misoli

Ushbu fayl barcha komponentlarning qanday ishlashini ko'rsatadi
"""

import sys
import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datetime import datetime, timedelta
import asyncio
import logging

# Projektdagi modullarni import qilish
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_algorithm import BaseTradingAlgorithm
from core.adaptive_model import AdaptiveModel
from core.performance_tracker import PerformanceTracker
from self_improving.online_learning import OnlineLearningEngine
from self_improving.evolutionary_strategies import EvolutionaryOptimizer
from self_improving.meta_learning import MetaLearningManager
from self_improving.neural_architecture_search import NeuralArchitectureSearch
from self_improving.automl import AutoMLPipeline
from adaptive_mechanisms.concept_drift import ConceptDriftDetector
from adaptive_mechanisms.rolling_window import RollingWindowOptimizer
from adaptive_mechanisms.transfer_learning import TransferLearningManager
from adaptive_mechanisms.continual_learning import ContinualLearningManager
from multi_market.stock_adaptation import StockMarketAdapter
from multi_market.forex_adaptation import ForexMarketAdapter
from multi_market.crypto_adaptation import CryptoMarketAdapter
from multi_market.metal_adaptation import MetalMarketAdapter
from multi_market.cross_market_transfer import CrossMarketTransfer
from optimization.dynamic_learning import DynamicLearningRate
from optimization.adaptive_batch_sizes import AdaptiveBatchSizeManager
from optimization.online_hyperparameter_tuning import OnlineHyperparameterTuner
from optimization.model_ensemble_adaptation import AdaptiveEnsembleManager
from implementation.streaming_data_processing import StreamingDataProcessor
from implementation.real_time_model_updates import RealTimeModelUpdater
from implementation.ab_testing_integration import ABTestingFramework
from implementation.performance_monitoring import PerformanceMonitoringSystem
from implementation.rollback_mechanisms import RollbackManager


class SelfLearningTradingDemo:
    """Self-Learning Trading Fund demo tizimi"""
    
    def __init__(self):
        # Logging sozlamalar
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_demo.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Ma'lumotlar yaratish (real trading uchun API dan olinadi)
        self.generate_sample_data()
        
        # Tizim komponentlarini ishga tushirish
        self.setup_components()
        
        # Performance tracking
        self.performance_history = []
        
    def generate_sample_data(self):
        """Sinov uchun namuna ma'lumotlar yaratish"""
        self.logger.info("Namuna ma'lumotlar yaratilmoqda...")
        
        # Kunlik narxlar
        dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='D')
        n_days = len(dates)
        
        # Aktsiyalar narxi simulyatsiyasi
        np.random.seed(42)
        self.stock_data = pd.DataFrame({
            'date': dates,
            'open': np.random.randn(n_days).cumsum() + 100,
            'high': np.random.randn(n_days).cumsum() + 105,
            'low': np.random.randn(n_days).cumsum() + 95,
            'close': np.random.randn(n_days).cumsum() + 100,
            'volume': np.random.randint(1000000, 10000000, n_days)
        })
        
        # Forex ma'lumotlar (USD/EUR)
        self.forex_data = pd.DataFrame({
            'date': dates,
            'usd_eur': 1.1 + 0.1 * np.random.randn(n_days).cumsum(),
            'usd_gbp': 1.3 + 0.1 * np.random.randn(n_days).cumsum(),
            'eur_jpy': 120 + 5 * np.random.randn(n_days).cumsum()
        })
        
        # Crypto ma'lumotlar
        self.crypto_data = pd.DataFrame({
            'date': dates,
            'btc_price': 50000 + 10000 * np.random.randn(n_days).cumsum(),
            'eth_price': 3000 + 1000 * np.random.randn(n_days).cumsum(),
            'ada_price': 1.0 + 0.5 * np.random.randn(n_days).cumsum()
        })
        
        # Metallar narxi
        self.metal_data = pd.DataFrame({
            'date': dates,
            'gold': 1800 + 50 * np.random.randn(n_days).cumsum(),
            'silver': 25 + 2 * np.random.randn(n_days).cumsum(),
            'platinum': 1000 + 30 * np.random.randn(n_days).cumsum()
        })
        
        self.logger.info("Ma'lumotlar tayyorlandi")
        
    def setup_components(self):
        """Tizim komponentlarini sozlash"""
        self.logger.info("Tizim komponentlari ishga tushirilmoqda...")
        
        # Asosiy algoritm
        self.base_algorithm = BaseTradingAlgorithm(
            initial_capital=100000,
            risk_per_trade=0.02,
            max_positions=10
        )
        
        # Adaptiv model
        self.adaptive_model = AdaptiveModel(
            input_features=20,
            hidden_layers=[64, 32, 16],
            output_size=1,
            learning_rate=0.001
        )
        
        # Performance tracker
        self.performance_tracker = PerformanceTracker()
        
        # Self-improving komponentlar
        self.online_learner = OnlineLearningEngine(
            model=self.adaptive_model,
            update_frequency=1,  # Har kuni
            adaptation_threshold=0.05
        )
        
        self.evolutionary_optimizer = EvolutionaryOptimizer(
            population_size=20,
            elite_size=5,
            mutation_rate=0.1,
            crossover_rate=0.8
        )
        
        self.meta_learner = MetaLearningManager(
            fast_learning_rate=0.1,
            meta_learning_rate=0.01,
            adaptation_steps=5
        )
        
        # NAS va AutoML
        self.nas_manager = NeuralArchitectureSearch(
            search_space='standard',
            max_epochs=50,
            patience=10
        )
        
        self.automl_pipeline = AutoMLPipeline(
            max_trials=100,
            time_budget=3600,  # 1 soat
            metric='sharpe_ratio'
        )
        
        # Adaptive mechanisms
        self.concept_drift_detector = ConceptDriftDetector(
            window_size=100,
            threshold=0.05,
            method='ks_test'
        )
        
        self.rolling_window_optimizer = RollingWindowOptimizer(
            window_size=252,  # 1 yil
            step_size=21,     # 1 oy
            validation_split=0.2
        )
        
        self.transfer_learning = TransferLearningManager(
            source_domains=['stocks', 'forex'],
            target_domains=['crypto'],
            adaptation_method='fine_tuning'
        )
        
        # Multi-market adapters
        self.stock_adapter = StockMarketAdapter()
        self.forex_adapter = ForexMarketAdapter()
        self.crypto_adapter = CryptoMarketAdapter()
        self.metal_adapter = MetalMarketAdapter()
        self.cross_market_transfer = CrossMarketTransfer()
        
        # Optimization komponentlar
        self.dynamic_learning = DynamicLearningRate(
            min_lr=0.0001,
            max_lr=0.1,
            decay_rate=0.95
        )
        
        self.adaptive_batch_manager = AdaptiveBatchSizeManager(
            min_batch_size=16,
            max_batch_size=256,
            target_utilization=0.8
        )
        
        self.hyperparameter_tuner = OnlineHyperparameterTuner(
            search_space={
                'learning_rate': [0.0001, 0.1],
                'batch_size': [16, 32, 64, 128],
                'hidden_layers': [[32], [64, 32], [128, 64, 32]]
            },
            optimization_metric='sharpe_ratio'
        )
        
        self.ensemble_manager = AdaptiveEnsembleManager(
            base_models=['lstm', 'transformer', 'cnn'],
            ensemble_method='dynamic_weighting'
        )
        
        # Implementation features
        self.streaming_processor = StreamingDataProcessor(
            buffer_size=1000,
            processing_interval=60  # 1 daqiqa
        )
        
        self.real_time_updater = RealTimeModelUpdater(
            model=self.adaptive_model,
            update_threshold=0.02,
            rollback_enabled=True
        )
        
        self.ab_testing = ABTestingFramework(
            traffic_split=0.5,
            significance_level=0.05,
            power=0.8
        )
        
        self.performance_monitor = PerformanceMonitoringSystem(
            metrics=['sharpe_ratio', 'max_drawdown', 'win_rate'],
            alert_thresholds={
                'sharpe_ratio': 1.0,
                'max_drawdown': 0.2,
                'win_rate': 0.4
            }
        )
        
        self.rollback_manager = RollbackManager(
            checkpoint_frequency=100,
            max_checkpoints=10
        )
        
        # Continual Learning
        self.continual_learning = ContinualLearningManager({
            'model_type': 'pnn',
            'input_dim': 20,
            'hidden_dims': [64, 32, 16],
            'strategy': 'ewc',
            'epochs_per_task': 50,
            'memory_buffer_size': 2000
        })
        
        self.logger.info("Barcha komponentlar tayyorlandi")
        
    async def run_trading_simulation(self, simulation_days=100):
        """Trading simulyatsiyasi ishga tushirish"""
        self.logger.info(f"{simulation_days} kunlik trading simulyatsiyasi boshlanmoqda...")
        
        # Simulyatsiya uchun ma'lumotlar
        simulation_data = self.stock_data.tail(simulation_days)
        
        for i, (date, row) in enumerate(simulation_data.iterrows()):
            current_date = row['date']
            current_price = row['close']
            
            # Streaming ma'lumotlarni qayta ishlash
            market_data = {
                'date': current_date,
                'price': current_price,
                'volume': row['volume'],
                'high': row['high'],
                'low': row['low']
            }
            
            await self.streaming_processor.process_data(market_data)
            
            # Concept drift tekshirish
            is_drift = self.concept_drift_detector.detect_drift(
                current_window=simulation_data.iloc[:i+1]['close'].values
            )
            
            # Real-time model yangilash
            if is_drift or i % 7 == 0:  # Haftasiga yoki drift bo'lsa
                await self.real_time_updater.update_model(
                    new_data=market_data,
                    force_update=False
                )
            
            # Trading signal yaratish
            signal = await self.generate_trading_signal(market_data)
            
            # Position boshqarish
            if signal['action'] == 'buy':
                self.base_algorithm.open_position(
                    symbol='SAMPLE_STOCK',
                    entry_price=current_price,
                    signal_strength=signal['confidence']
                )
            elif signal['action'] == 'sell':
                self.base_algorithm.close_position(
                    symbol='SAMPLE_STOCK',
                    exit_price=current_price
                )
            
            # Performance tracking
            daily_performance = self.calculate_daily_performance()
            self.performance_history.append({
                'date': current_date,
                'portfolio_value': daily_performance['portfolio_value'],
                'daily_return': daily_performance['daily_return'],
                'cumulative_return': daily_performance['cumulative_return'],
                'sharpe_ratio': daily_performance['sharpe_ratio']
            })
            
            # AB testing
            if i % 30 == 0:  # Har oyda
                self.ab_testing.evaluate_performance()
            
            # Performance monitoring
            self.performance_monitor.update_metrics(daily_performance)
            
            # Progress log
            if i % 10 == 0:
                self.logger.info(
                    f"Kun {i+1}/{simulation_days} | "
                    f"Portfolio: ${daily_performance['portfolio_value']:,.2f} | "
                    f"Return: {daily_performance['daily_return']:.2%}"
                )
        
        self.logger.info("Trading simulyatsiyasi tugallandi")
        
    async def generate_trading_signal(self, market_data):
        """Trading signal yaratish"""
        # Oddiy moving average crossover
        recent_prices = self.stock_data['close'].tail(20).values
        current_price = market_data['price']
        
        short_ma = np.mean(recent_prices[-5:])
        long_ma = np.mean(recent_prices)
        
        if short_ma > long_ma and current_price > short_ma:
            action = 'buy'
            confidence = min((short_ma - long_ma) / long_ma * 10, 1.0)
        elif short_ma < long_ma and current_price < short_ma:
            action = 'sell'
            confidence = min((long_ma - short_ma) / long_ma * 10, 1.0)
        else:
            action = 'hold'
            confidence = 0.0
            
        return {
            'action': action,
            'confidence': confidence,
            'price_target': current_price * (1 + confidence * 0.05 if action == 'buy' else -confidence * 0.05)
        }
    
    def calculate_daily_performance(self):
        """Kunlik performance hisoblash"""
        current_positions = self.base_algorithm.get_positions()
        current_price = self.stock_data['close'].iloc[-1]
        
        # Portfolio qiymati hisoblash
        position_value = sum(
            pos['quantity'] * current_price if pos['symbol'] == 'SAMPLE_STOCK' else 0
            for pos in current_positions
        )
        
        cash = self.base_algorithm.cash
        portfolio_value = cash + position_value
        
        # Returns hisoblash
        initial_value = 100000
        cumulative_return = (portfolio_value - initial_value) / initial_value
        
        # Sharpe ratio (oddiy hisoblash)
        if len(self.performance_history) > 1:
            daily_returns = [p['daily_return'] for p in self.performance_history[1:]]
            avg_return = np.mean(daily_returns)
            return_std = np.std(daily_returns)
            sharpe_ratio = avg_return / return_std if return_std > 0 else 0
        else:
            sharpe_ratio = 0
        
        daily_return = cumulative_return  # Soddalashtirilgan
        
        return {
            'portfolio_value': portfolio_value,
            'cash': cash,
            'position_value': position_value,
            'daily_return': daily_return,
            'cumulative_return': cumulative_return,
            'sharpe_ratio': sharpe_ratio
        }
    
    async def run_optimization_pipeline(self):
        """Model optimizatsiya pipeline"""
        self.logger.info("Model optimizatsiya boshlangan...")
        
        # Rolling window optimizatsiya
        window_results = await self.rolling_window_optimizer.optimize(
            data=self.stock_data,
            model_config={'learning_rate': 0.001}
        )
        
        # Online hyperparameter tuning
        best_params = await self.hyperparameter_tuner.tune(
            train_data=self.stock_data[:-50],
            validation_data=self.stock_data[-50:]
        )
        
        # Meta-learning adaptation
        meta_results = await self.meta_learner.adapt_to_new_market(
            source_performance=window_results,
            target_market='forex'
        )
        
        # Neural Architecture Search
        best_architecture = await self.nas_manager.search(
            input_shape=(20,),
            max_trials=50
        )
        
        # AutoML pipeline
        automl_results = await self.automl_pipeline.optimize(
            data=self.stock_data,
            target_column='close',
            time_column='date'
        )
        
        # Evolutionary optimization
        evolutionary_results = await self.evolutionary_optimizer.evolve(
            population_size=20,
            generations=50,
            fitness_function=self.fitness_function
        )
        
        self.logger.info("Model optimizatsiya tugallandi")
        
        return {
            'rolling_window': window_results,
            'hyperparameter_tuning': best_params,
            'meta_learning': meta_results,
            'neural_architecture': best_architecture,
            'automl': automl_results,
            'evolutionary': evolutionary_results
        }
    
    def fitness_function(self, model_params):
        """Model uchun fitness function"""
        # Model yaratish va performance test qilish
        try:
            # Oddiy model
            model = nn.Sequential(
                nn.Linear(20, 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1)
            )
            
            # Simulyatsiya (qisqartirilgan)
            # Real implementation da train/val data ishlatiladi
            fitness_score = np.random.uniform(0.1, 0.9)  # Placeholder
            
            return fitness_score
        except Exception as e:
            self.logger.error(f"Fitness function xatosi: {e}")
            return 0.0
    
    def run_multi_market_demo(self):
        """Multi-market adaptatsiya demo"""
        self.logger.info("Multi-market adaptatsiya demo boshlanmoqda...")
        
        # Har bir market uchun adaptatsiya
        markets = {
            'stocks': self.stock_data,
            'forex': self.forex_data,
            'crypto': self.crypto_data,
            'metals': self.metal_data
        }
        
        adaptation_results = {}
        
        for market_name, data in markets.items():
            self.logger.info(f"{market_name} market adaptatsiyasi...")
            
            # Market-specific features
            features = self.extract_market_features(data, market_name)
            
            # Model adaptation
            adapted_model = self.adaptive_model.adapt_to_market(
                market_data=data,
                market_type=market_name,
                adaptation_method='fine_tuning'
            )
            
            # Performance evaluation
            performance = self.evaluate_market_performance(
                adapted_model, data, market_name
            )
            
            adaptation_results[market_name] = performance
            
            self.logger.info(f"{market_name} adaptatsiyasi tugallandi: {performance['accuracy']:.3f}")
        
        # Cross-market transfer learning
        self.logger.info("Cross-market transfer learning...")
        transfer_results = self.cross_market_transfer.transfer_knowledge(
            source_markets=['stocks', 'forex'],
            target_market='crypto',
            transfer_method='domain_adaptation'
        )
        
        return {
            'market_adaptations': adaptation_results,
            'cross_market_transfer': transfer_results
        }
    
    def extract_market_features(self, data, market_type):
        """Market-specific features extract qilish"""
        features = {}
        
        if market_type == 'stocks':
            features = {
                'price_change': data['close'].pct_change(),
                'volume_ratio': data['volume'] / data['volume'].rolling(20).mean(),
                'volatility': data['close'].rolling(20).std()
            }
        elif market_type == 'forex':
            features = {
                'currency_strength': data.select_dtypes(include=[np.number]).mean(axis=1),
                'correlation_matrix': data.select_dtypes(include=[np.number]).corr(),
                'momentum': data.select_dtypes(include=[np.number]).pct_change().rolling(10).mean()
            }
        elif market_type == 'crypto':
            features = {
                'crypto_volatility': data.select_dtypes(include=[np.number]).std(axis=1),
                'market_cap_proxy': data.select_dtypes(include=[np.number]).sum(axis=1),
                'trend_strength': data.select_dtypes(include=[np.number]).rolling(10).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == 10 else 0)
            }
        elif market_type == 'metals':
            features = {
                'metal_index': data.select_dtypes(include=[np.number]).mean(axis=1),
                'price_volatility': data.select_dtypes(include=[np.number]).std(),
                'seasonal_pattern': data.select_dtypes(include=[np.number]).rolling(30).mean()
            }
        
        return features
    
    def evaluate_market_performance(self, model, data, market_name):
        """Market uchun model performance"""
        # Oddiy performance evaluation
        predictions = np.random.uniform(0.1, 0.9, len(data))  # Placeholder
        actuals = np.random.uniform(0.1, 0.9, len(data))      # Placeholder
        
        accuracy = 1 - np.mean(np.abs(predictions - actuals))
        precision = accuracy + np.random.uniform(-0.1, 0.1)
        recall = accuracy + np.random.uniform(-0.1, 0.1)
        
        return {
            'accuracy': max(0, min(1, accuracy)),
            'precision': max(0, min(1, precision)),
            'recall': max(0, min(1, recall)),
            'f1_score': 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        }
    
    def generate_comprehensive_report(self):
        """Keng qamrovli hisobot yaratish"""
        self.logger.info("Keng qamrovli hisobot yaratilmoqda...")
        
        # Performance hisoboti
        perf_report = self.performance_tracker.generate_report()
        
        # Multi-market report
        market_report = self.run_multi_market_demo()
        
        # Continual learning results
        if hasattr(self, 'continual_learning'):
            continual_report = self.continual_learning.get_performance_report()
        else:
            continual_report = {}
        
        # Rollback va AB testing report
        rollback_report = self.rollback_manager.get_rollback_history()
        ab_test_report = self.ab_testing.get_test_results()
        
        # Overall statistics
        if self.performance_history:
            final_performance = self.performance_history[-1]
            total_return = final_performance['cumulative_return']
            avg_daily_return = np.mean([p['daily_return'] for p in self.performance_history])
            max_drawdown = self.calculate_max_drawdown()
            sharpe_ratio = final_performance['sharpe_ratio']
        else:
            total_return = 0
            avg_daily_return = 0
            max_drawdown = 0
            sharpe_ratio = 0
        
        comprehensive_report = {
            'simulation_summary': {
                'total_days': len(self.performance_history),
                'initial_capital': 100000,
                'final_portfolio_value': final_performance['portfolio_value'] if self.performance_history else 100000,
                'total_return': total_return,
                'avg_daily_return': avg_daily_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'win_rate': self.calculate_win_rate()
            },
            'performance_metrics': perf_report,
            'market_adaptation': market_report,
            'continual_learning': continual_report,
            'system_health': {
                'rollback_history': rollback_report,
                'ab_test_results': ab_test_report,
                'model_updates': len(self.real_time_updater.update_history),
                'alerts_triggered': self.performance_monitor.alert_count
            },
            'technical_details': {
                'concept_drift_detections': len(self.concept_drift_detector.drift_history),
                'model_adaptations': len(self.adaptive_model.adaptation_history),
                'optimization_iterations': len(self.hyperparameter_tuner.optimization_history),
                'ensemble_size': len(self.ensemble_manager.models)
            }
        }
        
        return comprehensive_report
    
    def calculate_max_drawdown(self):
        """Maximum drawdown hisoblash"""
        if not self.performance_history:
            return 0
        
        values = [p['portfolio_value'] for p in self.performance_history]
        peak = values[0]
        max_dd = 0
        
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def calculate_win_rate(self):
        """Win rate hisoblash"""
        if len(self.performance_history) < 2:
            return 0
        
        wins = 0
        total_trades = 0
        
        for i in range(1, len(self.performance_history)):
            if abs(self.performance_history[i]['daily_return']) > 0.001:  # Minimal trade size
                total_trades += 1
                if self.performance_history[i]['daily_return'] > 0:
                    wins += 1
        
        return wins / total_trades if total_trades > 0 else 0


async def main():
    """Asosiy demo"""
    print("=" * 60)
    print("🎯 SELF-LEARNING TRADING FUND DEMO")
    print("=" * 60)
    
    # Demo tizimi yaratish
    demo = SelfLearningTradingDemo()
    
    try:
        # 1. Trading simulyatsiyasi
        print("\n1️⃣ TRADING SIMULYATSIYASI")
        print("-" * 40)
        await demo.run_trading_simulation(simulation_days=100)
        
        # 2. Model optimizatsiya
        print("\n2️⃣ MODEL OPTIMIZATSIYA")
        print("-" * 40)
        optimization_results = await demo.run_optimization_pipeline()
        print(f"✓ Hyperparameter tuning natija: {len(optimization_results['hyperparameter_tuning'])} parameter")
        print(f"✓ NAS eng yaxshi arxitektura: {optimization_results['neural_architecture']}")
        
        # 3. Multi-market adaptatsiya
        print("\n3️⃣ MULTI-MARKET ADAPTATSIYA")
        print("-" * 40)
        market_results = demo.run_multi_market_demo()
        print(f"✓ {len(market_results['market_adaptations'])} market adaptatsiya tugallandi")
        
        # 4. Keng qamrovli hisobot
        print("\n4️⃣ KENG QAMROVLI HISOBOT")
        print("-" * 40)
        comprehensive_report = demo.generate_comprehensive_report()
        
        # Hisobotni konsolga chiqarish
        summary = comprehensive_report['simulation_summary']
        print(f"📊 Simulyatsiya muddati: {summary['total_days']} kun")
        print(f"💰 Boshlang'ich kapital: ${summary['initial_capital']:,.2f}")
        print(f"📈 Yakuniy qiymat: ${summary['final_portfolio_value']:,.2f}")
        print(f"📊 Umumiy return: {summary['total_return']:.2%}")
        print(f"⚡ Sharpe ratio: {summary['sharpe_ratio']:.3f}")
        print(f"📉 Max drawdown: {summary['max_drawdown']:.2%}")
        print(f"🏆 Win rate: {summary['win_rate']:.2%}")
        
        # Faylga saqlash
        import json
        with open('demo_results.json', 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ Hisobot 'demo_results.json' ga saqlandi")
        
        print("\n" + "=" * 60)
        print("🎉 DEMO MUVAFFAQIYATLI TUGALLANDI!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo xatosi: {e}")
        logging.error(f"Demo xatosi: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())