"""
Multi-Market Adaptation Demo - Cross-market knowledge transfer

Ushbu demo turli moliya bozorlariga adaptatsiya va
cross-market knowledge transfer qanday ishlashini ko'rsatadi
"""

import sys
import os
import numpy as np
import pandas as pd
import torch
import asyncio
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_market.stock_adaptation import StockMarketAdapter
from multi_market.forex_adaptation import ForexMarketAdapter
from multi_market.crypto_adaptation import CryptoMarketAdapter
from multi_market.metal_adaptation import MetalMarketAdapter
from multi_market.cross_market_transfer import CrossMarketTransfer
from adaptive_mechanisms.transfer_learning import TransferLearningManager
from core.adaptive_model import AdaptiveModel


class MultiMarketDemo:
    """Multi-market adaptation demo"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Market adapters
        self.stock_adapter = StockMarketAdapter()
        self.forex_adapter = ForexMarketAdapter()
        self.crypto_adapter = CryptoMarketAdapter()
        self.metal_adapter = MetalMarketAdapter()
        self.cross_market_transfer = CrossMarketTransfer()
        self.transfer_learning = TransferLearningManager()
        
        # Base model
        self.base_model = AdaptiveModel(
            input_features=15,
            hidden_layers=[64, 32, 16],
            output_size=1,
            learning_rate=0.001
        )
        
        # Market-specific models
        self.market_models = {}
        
        # Demo ma'lumotlari
        self.markets_data = {}
        self.generate_market_data()
        
    def setup_logging(self):
        """Logging sozlamalar"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def generate_market_data(self):
        """Har bir market uchun namuna ma'lumotlar yaratish"""
        self.logger.info("Market ma'lumotlar yaratilmoqda...")
        
        # Stock market (aktsiyalar)
        np.random.seed(42)
        stock_dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        n_days = len(stock_dates)
        
        self.markets_data['stocks'] = {
            'dates': stock_dates,
            'prices': 100 + np.random.randn(n_days).cumsum() * 2,
            'volume': np.random.randint(1000000, 10000000, n_days),
            'volatility': 0.02 + np.random.rand(n_days) * 0.03,
            'sector_rotation': np.random.choice(['tech', 'finance', 'healthcare', 'energy'], n_days),
            'sentiment': np.random.randn(n_days) * 0.5,
            'features': self.generate_stock_features(n_days)
        }
        
        # Forex market
        np.random.seed(123)
        forex_dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='H')
        n_hours = len(forex_dates)
        
        self.markets_data['forex'] = {
            'dates': forex_dates,
            'eur_usd': 1.1 + np.random.randn(n_hours).cumsum() * 0.001,
            'gbp_usd': 1.3 + np.random.randn(n_hours).cumsum() * 0.001,
            'usd_jpy': 110 + np.random.randn(n_hours).cumsum() * 0.5,
            'interest_rate_diff': np.random.randn(n_hours) * 0.01,
            'economic_indicators': np.random.randn(n_hours) * 0.1,
            'market_hours': self.get_forex_market_hours(forex_dates),
            'features': self.generate_forex_features(n_hours)
        }
        
        # Crypto market
        np.random.seed(456)
        crypto_dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='15T')
        n_periods = len(crypto_dates)
        
        self.markets_data['crypto'] = {
            'dates': crypto_dates,
            'btc_price': 50000 + np.random.randn(n_periods).cumsum() * 1000,
            'eth_price': 3000 + np.random.randn(n_periods).cumsum() * 100,
            'market_cap': np.random.randint(1000000000, 2000000000, n_periods),
            'defi_tvl': np.random.randint(50000000, 500000000, n_periods),
            'whale_movements': np.random.choice([0, 1], n_periods, p=[0.9, 0.1]),
            'features': self.generate_crypto_features(n_periods)
        }
        
        # Metal market
        np.random.seed(789)
        metal_dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        n_days_metal = len(metal_dates)
        
        self.markets_data['metals'] = {
            'dates': metal_dates,
            'gold': 1800 + np.random.randn(n_days_metal).cumsum() * 20,
            'silver': 25 + np.random.randn(n_days_metal).cumsum() * 1,
            'platinum': 1000 + np.random.randn(n_days_metal).cumsum() * 15,
            'industrial_demand': np.random.randint(80, 120, n_days_metal),
            'mining_production': np.random.randint(85, 115, n_days_metal),
            'seasonal_pattern': np.sin(2 * np.pi * np.arange(n_days_metal) / 365),
            'features': self.generate_metal_features(n_days_metal)
        }
        
        self.logger.info("Barcha market ma'lumotlari yaratildi")
    
    def generate_stock_features(self, n_samples):
        """Stock market features"""
        features = np.random.randn(n_samples, 15)
        features[:, 0] = np.random.randn(n_samples).cumsum()  # Price momentum
        features[:, 1] = np.random.rand(n_samples) * 0.5     # Volume ratio
        features[:, 2] = np.random.randn(n_samples)           # RSI
        features[:, 3] = np.random.randn(n_samples) * 0.1    # MACD
        features[:, 4] = np.random.randn(n_samples)           # Bollinger position
        features[:, 5] = np.random.rand(n_samples)            # Money flow index
        features[:, 6:15] = np.random.randn(n_samples, 9)     # Other features
        return features
    
    def generate_forex_features(self, n_samples):
        """Forex market features"""
        features = np.random.randn(n_samples, 15)
        features[:, 0] = np.random.randn(n_samples).cumsum()  # Carry trade ratio
        features[:, 1] = np.random.randn(n_samples)           # Interest rate spread
        features[:, 2] = np.random.randn(n_samples)           # Economic calendar impact
        features[:, 3] = np.random.randn(n_samples) * 0.1     # Central bank intervention
        features[:, 4] = np.random.randn(n_samples)           # Market sentiment
        features[:, 5:15] = np.random.randn(n_samples, 10)    # Other features
        return features
    
    def generate_crypto_features(self, n_samples):
        """Crypto market features"""
        features = np.random.randn(n_samples, 15)
        features[:, 0] = np.random.randn(n_samples).cumsum()  # Fear/Greed index
        features[:, 1] = np.random.randn(n_samples) * 0.5     # On-chain metrics
        features[:, 2] = np.random.rand(n_samples)            # Exchange flows
        features[:, 3] = np.random.randn(n_samples)           # Social sentiment
        features[:, 4] = np.random.randn(n_samples) * 0.2     # Regulatory news
        features[:, 5:15] = np.random.randn(n_samples, 10)    # Other features
        return features
    
    def generate_metal_features(self, n_samples):
        """Metal market features"""
        features = np.random.randn(n_samples, 15)
        features[:, 0] = np.random.randn(n_samples).cumsum()  # Industrial demand
        features[:, 1] = np.random.randn(n_samples)           # Mining supply
        features[:, 2] = np.random.rand(n_samples)            # Inventory levels
        features[:, 3] = np.random.randn(n_samples)           # Currency impact
        features[:, 4] = np.random.randn(n_samples) * 0.1     # Geopolitical events
        features[:, 5:15] = np.random.randn(n_samples, 10)    # Other features
        return features
    
    def get_forex_market_hours(self, dates):
        """Forex market soatlari (UTC)"""
        hours = dates.hour
        return ((hours >= 8) & (hours <= 17)) | ((hours >= 21) | (hours <= 6))
    
    async def run_market_adaptation_demo(self):
        """Market adaptatsiya demo"""
        self.logger.info("Market adaptatsiya demo boshlanmoqda...")
        
        adaptation_results = {}
        
        # Har bir market uchun adaptatsiya
        for market_name, market_data in self.markets_data.items():
            self.logger.info(f"\n{market_name.upper()} market adaptatsiyasi...")
            
            # Market-specific model yaratish
            adapted_model = self.create_adapted_model(market_name)
            
            # Market-specific features extract qilish
            features = market_data['features']
            
            # Training data yaratish (simulyatsiya)
            if market_name == 'stocks':
                target = self.create_stock_targets(features)
            elif market_name == 'forex':
                target = self.create_forex_targets(features)
            elif market_name == 'crypto':
                target = self.create_crypto_targets(features)
            elif market_name == 'metals':
                target = self.create_metal_targets(features)
            
            # Model training
            training_results = await self.train_market_model(
                adapted_model, features, target, market_name
            )
            
            # Performance evaluation
            performance = await self.evaluate_model_performance(
                adapted_model, features, target, market_name
            )
            
            self.market_models[market_name] = adapted_model
            adaptation_results[market_name] = {
                'training_results': training_results,
                'performance': performance,
                'model_params': sum(p.numel() for p in adapted_model.parameters())
            }
            
            self.logger.info(f"{market_name} adaptatsiyasi tugallandi")
        
        return adaptation_results
    
    def create_adapted_model(self, market_name):
        """Market-specific model yaratish"""
        base_config = {
            'input_features': 15,
            'hidden_layers': [64, 32, 16],
            'output_size': 1,
            'learning_rate': 0.001
        }
        
        # Market-specific adjustments
        if market_name == 'crypto':
            # Crypto uchun yuqori volatilite
            base_config['hidden_layers'] = [128, 64, 32]
            base_config['learning_rate'] = 0.0005
        elif market_name == 'forex':
            # Forex uchun tezkor learning
            base_config['learning_rate'] = 0.002
        elif market_name == 'metals':
            # Metals uchun katta batch size
            base_config['batch_size'] = 128
        
        return AdaptiveModel(**base_config)
    
    def create_stock_targets(self, features):
        """Stock targets yaratish"""
        # Trend va momentum asosida target yaratish
        trend = features[:, 0] * 0.7 + features[:, 1] * 0.3
        noise = np.random.randn(len(features)) * 0.1
        return trend + noise
    
    def create_forex_targets(self, features):
        """Forex targets yaratish"""
        # Carry trade va interest rate spread asosida
        carry = features[:, 0] * 0.5 + features[:, 1] * 0.5
        noise = np.random.randn(len(features)) * 0.05
        return carry + noise
    
    def create_crypto_targets(self, features):
        """Crypto targets yaratish"""
        # High volatility uchun katta coefficients
        sentiment = features[:, 0] * 1.2 + features[:, 1] * 0.8
        noise = np.random.randn(len(features)) * 0.2
        return sentiment + noise
    
    def create_metal_targets(self, features):
        """Metal targets yaratish"""
        # Seasonal pattern va industrial demand
        demand = features[:, 0] * 0.6 + features[:, 1] * 0.4
        noise = np.random.randn(len(features)) * 0.08
        return demand + noise
    
    async def train_market_model(self, model, features, target, market_name):
        """Market-specific model training"""
        self.logger.info(f"{market_name} model train qilinmoqda...")
        
        # Data split
        train_size = int(0.8 * len(features))
        train_features = torch.tensor(features[:train_size], dtype=torch.float32)
        train_target = torch.tensor(target[:train_size], dtype=torch.float32).unsqueeze(1)
        
        val_features = torch.tensor(features[train_size:], dtype=torch.float32)
        val_target = torch.tensor(target[train_size:], dtype=torch.float32).unsqueeze(1)
        
        # Training
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = torch.nn.MSELoss()
        
        epochs = 50
        train_losses = []
        val_losses = []
        
        for epoch in range(epochs):
            model.train()
            optimizer.zero_grad()
            
            # Forward pass
            train_pred = model(train_features)
            train_loss = criterion(train_pred, train_target)
            
            # Backward pass
            train_loss.backward()
            optimizer.step()
            
            # Validation
            model.eval()
            with torch.no_grad():
                val_pred = model(val_features)
                val_loss = criterion(val_pred, val_target)
            
            train_losses.append(train_loss.item())
            val_losses.append(val_loss.item())
            
            if epoch % 10 == 0:
                self.logger.info(f"  Epoch {epoch}: Train={train_loss:.4f}, Val={val_loss:.4f}")
        
        return {
            'final_train_loss': train_losses[-1],
            'final_val_loss': val_losses[-1],
            'train_losses': train_losses,
            'val_losses': val_losses,
            'epochs_trained': epochs
        }
    
    async def evaluate_model_performance(self, model, features, target, market_name):
        """Model performance evaluation"""
        model.eval()
        
        with torch.no_grad():
            features_tensor = torch.tensor(features, dtype=torch.float32)
            predictions = model(features_tensor).numpy().flatten()
            actual = target
            
            # Metrics hisoblash
            mae = np.mean(np.abs(predictions - actual))
            rmse = np.sqrt(np.mean((predictions - actual)**2))
            mape = np.mean(np.abs((actual - predictions) / actual)) * 100
            r2 = 1 - (np.sum((actual - predictions)**2) / np.sum((actual - np.mean(actual))**2))
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'r2_score': r2,
            'prediction_std': np.std(predictions),
            'actual_std': np.std(actual)
        }
    
    async def run_cross_market_transfer_demo(self):
        """Cross-market transfer learning demo"""
        self.logger.info("Cross-market transfer learning demo boshlanmoqda...")
        
        # Source markets (yuqori performance ga ega bo'lganlar)
        source_markets = ['stocks', 'forex']
        target_market = 'crypto'
        
        self.logger.info(f"Transfer: {source_markets} → {target_market}")
        
        # Cross-market transfer
        transfer_results = await self.cross_market_transfer.transfer_knowledge(
            source_markets=source_markets,
            target_market=target_market,
            transfer_method='domain_adaptation'
        )
        
        # Performance comparison
        crypto_model = self.market_models['crypto']
        target_features = self.markets_data['crypto']['features']
        target_targets = self.create_crypto_targets(target_features)
        
        # Baseline (without transfer)
        baseline_performance = await self.evaluate_model_performance(
            crypto_model, target_features, target_targets, 'crypto_baseline'
        )
        
        # Transfer learning performance
        transfer_performance = await self.evaluate_model_performance(
            crypto_model, target_features, target_targets, 'crypto_transfer'
        )
        
        return {
            'transfer_results': transfer_results,
            'baseline_performance': baseline_performance,
            'transfer_performance': transfer_performance,
            'improvement': {
                'mae': baseline_performance['mae'] - transfer_performance['mae'],
                'rmse': baseline_performance['rmse'] - transfer_performance['rmse'],
                'r2': transfer_performance['r2_score'] - baseline_performance['r2_score']
            }
        }
    
    def create_comprehensive_report(self, adaptation_results, transfer_results):
        """Keng qamrovli hisobot yaratish"""
        self.logger.info("Keng qamrovli hisobot yaratilmoqda...")
        
        report = {
            'market_adaptation_summary': {},
            'cross_market_transfer': transfer_results,
            'overall_insights': {},
            'recommendations': []
        }
        
        # Market adaptation summary
        for market, results in adaptation_results.items():
            report['market_adaptation_summary'][market] = {
                'model_complexity': results['model_params'],
                'training_efficiency': results['training_results']['final_val_loss'],
                'prediction_accuracy': results['performance']['r2_score'],
                'mae': results['performance']['mae'],
                'rmse': results['performance']['rmse']
            }
        
        # Overall insights
        performances = [r['performance']['r2_score'] for r in adaptation_results.values()]
        report['overall_insights'] = {
            'best_performing_market': max(adaptation_results.keys(), 
                                        key=lambda x: adaptation_results[x]['performance']['r2_score']),
            'worst_performing_market': min(adaptation_results.keys(), 
                                         key=lambda x: adaptation_results[x]['performance']['r2_score']),
            'average_r2_score': np.mean(performances),
            'performance_variance': np.var(performances)
        }
        
        # Recommendations
        if report['overall_insights']['average_r2_score'] > 0.7:
            report['recommendations'].append("Yuqori performance - current strategy saqlanishi mumkin")
        
        if report['overall_insights']['performance_variance'] > 0.1:
            report['recommendations'].append("Performance variance yuqori - market-specific tuning kerak")
        
        transfer_improvement = transfer_results['improvement']
        if transfer_improvement['r2'] > 0.05:
            report['recommendations'].append("Cross-market transfer foydali - kengaytirish mumkin")
        
        return report
    
    def create_market_comparison_visualization(self, adaptation_results):
        """Market comparison visualization"""
        self.logger.info("Market comparison visualization yaratilmoqda...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        markets = list(adaptation_results.keys())
        
        # 1. R2 Scores
        r2_scores = [adaptation_results[m]['performance']['r2_score'] for m in markets]
        axes[0, 0].bar(markets, r2_scores, color=['blue', 'green', 'red', 'orange'])
        axes[0, 0].set_title('R² Scores by Market')
        axes[0, 0].set_ylabel('R² Score')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. MAE Comparison
        mae_scores = [adaptation_results[m]['performance']['mae'] for m in markets]
        axes[0, 1].bar(markets, mae_scores, color=['blue', 'green', 'red', 'orange'])
        axes[0, 1].set_title('Mean Absolute Error by Market')
        axes[0, 1].set_ylabel('MAE')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Model Complexity
        model_params = [adaptation_results[m]['model_params'] for m in markets]
        axes[0, 2].bar(markets, model_params, color=['blue', 'green', 'red', 'orange'])
        axes[0, 2].set_title('Model Complexity (Parameters)')
        axes[0, 2].set_ylabel('Parameters Count')
        axes[0, 2].tick_params(axis='x', rotation=45)
        
        # 4. Training Convergence
        for market in markets:
            train_losses = adaptation_results[market]['training_results']['train_losses']
            epochs = range(1, len(train_losses) + 1)
            axes[1, 0].plot(epochs, train_losses, label=market, marker='o', markersize=3)
        axes[1, 0].set_title('Training Loss Convergence')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Training Loss')
        axes[1, 0].legend()
        axes[1, 0].set_yscale('log')
        
        # 5. Market Characteristics
        market_chars = {
            'Stocks': {'volatility': 'O\'rtacha', 'liquidity': 'Yuqori', 'regulation': 'Yuqori'},
            'Forex': {'volatility': 'Past', 'liquidity': 'Juda yuqori', 'regulation': 'O\'rtacha'},
            'Crypto': {'volatility': 'Juda yuqori', 'liquidity': 'O\'rtacha', 'regulation': 'Past'},
            'Metals': {'volatility': 'O\'rtacha', 'liquidity': 'Past', 'regulation': 'O\'rtacha'}
        }
        
        volatility_scores = [3, 2, 5, 3]  # 1-5 scale
        liquidity_scores = [4, 5, 3, 2]
        
        x = np.arange(len(markets))
        width = 0.35
        
        axes[1, 1].bar(x - width/2, volatility_scores, width, label='Volatility', alpha=0.7)
        axes[1, 1].bar(x + width/2, liquidity_scores, width, label='Liquidity', alpha=0.7)
        axes[1, 1].set_title('Market Characteristics')
        axes[1, 1].set_xlabel('Markets')
        axes[1, 1].set_ylabel('Score (1-5)')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(markets, rotation=45)
        axes[1, 1].legend()
        
        # 6. Performance vs Complexity
        complexity = [adaptation_results[m]['model_params'] for m in markets]
        performance = [adaptation_results[m]['performance']['r2_score'] for m in markets]
        
        colors = ['blue', 'green', 'red', 'orange']
        for i, (comp, perf, market, color) in enumerate(zip(complexity, performance, markets, colors)):
            axes[1, 2].scatter(comp, perf, c=color, s=100, alpha=0.7, label=market)
            axes[1, 2].annotate(market, (comp, perf), xytext=(5, 5), textcoords='offset points')
        
        axes[1, 2].set_title('Performance vs Complexity')
        axes[1, 2].set_xlabel('Model Complexity (Parameters)')
        axes[1, 2].set_ylabel('R² Score')
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('multi_market_comparison.png', dpi=300, bbox_inches='tight')
        self.logger.info("Visualization 'multi_market_comparison.png' ga saqlandi")


async def main():
    """Asosiy demo funksiya"""
    print("🌍 MULTI-MARKET ADAPTATION DEMO")
    print("="*50)
    
    try:
        demo = MultiMarketDemo()
        
        # 1. Market adaptation demo
        print("\n1️⃣ MARKET ADAPTATION...")
        adaptation_results = await demo.run_market_adaptation_demo()
        
        # 2. Cross-market transfer demo
        print("\n2️⃣ CROSS-MARKET TRANSFER...")
        transfer_results = await demo.run_cross_market_transfer_demo()
        
        # 3. Comprehensive report
        print("\n3️⃣ COMPREHENSIVE REPORT...")
        report = demo.create_comprehensive_report(adaptation_results, transfer_results)
        
        # 4. Visualization
        print("\n4️⃣ VISUALIZATION...")
        demo.create_market_comparison_visualization(adaptation_results)
        
        # Natijalarni chiqarish
        print(f"\n📊 DEMO NATIJALARI:")
        print(f"   • Markets tested: {len(adaptation_results)}")
        print(f"   • Best market: {report['overall_insights']['best_performing_market']}")
        print(f"   • Average R²: {report['overall_insights']['average_r2_score']:.3f}")
        print(f"   • Transfer improvement: {transfer_results['improvement']['r2']:.3f}")
        print(f"   • Recommendations: {len(report['recommendations'])}")
        
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"     {i}. {rec}")
        
        # Faylga saqlash
        import json
        with open('multi_market_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'adaptation_results': adaptation_results,
                'transfer_results': transfer_results,
                'comprehensive_report': report
            }, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ Demo muvaffaqiyatli tugallandi!")
        print(f"   • Results saved: multi_market_results.json")
        print(f"   • Visualization: multi_market_comparison.png")
        
    except Exception as e:
        print(f"\n❌ Demo xatosi: {e}")
        logging.error(f"Demo xatosi: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())