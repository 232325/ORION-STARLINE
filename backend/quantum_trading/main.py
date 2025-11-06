"""
Quantum Advantage Trading System - Main Module
=============================================

Bu asosiy modul barcha quantum trading komponentlarini birlashtiradi.

Komponentlar:
- Multi-Asset Quantum Trading
- Quantum Error Correction
- Quantum Optimization
- Performance Metrics
- Benchmark Analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from .multi_asset import QuantumMultiAssetTrader
from .optimization import QuantumOptimizer
from .error_correction import QuantumErrorCorrection
from .metrics import QuantumAdvantageMetrics
from .benchmarks import QuantumBenchmarks

@dataclass
class TradingConfig:
    """Quantum Trading konfiguratsiyasi"""
    # Trading parameters
    quantum_advantage_threshold: float = 0.15  # 15% quantum advantage
    error_correction_level: str = "surface_code"  # surface_code, steane_code
    optimization_method: str = "variational"  # variational, annealing, qaoa
    benchmark_interval: int = 3600  # 1 hour in seconds
    
    # Asset allocation
    stocks_weight: float = 0.4
    forex_weight: float = 0.3
    metals_weight: float = 0.2
    crypto_weight: float = 0.1
    
    # Risk management
    max_drawdown: float = 0.05
    var_confidence: float = 0.95
    rebalance_frequency: int = 24  # hours

class QuantumAdvantageTradingSystem:
    """
    Quantum Advantage Trading System - Asosiy sinf
    
    Bu tizim quyidagi imkoniyatlarni ta'minlaydi:
    1. Multi-asset quantum trading
    2. Real-time quantum optimization
    3. Quantum error correction
    4. Performance monitoring
    5. Adaptive learning
    """
    
    def __init__(self, config: TradingConfig = None):
        self.config = config or TradingConfig()
        self.logger = self._setup_logging()
        
        # Core components
        self.multi_asset_trader = QuantumMultiAssetTrader()
        self.quantum_optimizer = QuantumOptimizer()
        self.error_corrector = QuantumErrorCorrection()
        self.metrics_calculator = QuantumAdvantageMetrics()
        self.benchmark_system = QuantumBenchmarks()
        
        # State tracking
        self.portfolio_state = None
        self.trading_history = []
        self.quantum_circuit_states = {}
        self.performance_metrics = {}
        
        self.logger.info("Quantum Advantage Trading System initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Logging setup"""
        logger = logging.getLogger("quantum_trading")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize_system(self) -> Dict[str, Any]:
        """Tizimni boshlash va quantum kaynaklarni initsializatsiya qilish"""
        self.logger.info("Quantum Trading System initialization starting...")
        
        try:
            # Initialize quantum components
            await self.multi_asset_trader.initialize()
            await self.quantum_optimizer.initialize()
            await self.error_corrector.initialize()
            
            # Setup benchmark system
            await self.benchmark_system.initialize()
            
            # Initialize portfolio state
            self.portfolio_state = await self._create_initial_portfolio()
            
            # Setup performance monitoring
            await self.metrics_calculator.initialize()
            
            self.logger.info("Quantum Trading System initialized successfully")
            return {
                "status": "initialized",
                "timestamp": datetime.now().isoformat(),
                "components": ["multi_asset", "optimizer", "error_correction", "metrics", "benchmarks"]
            }
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            raise
    
    async def _create_initial_portfolio(self) -> Dict[str, Any]:
        """Boshlang'ich portfolio yaratish"""
        return {
            "assets": {
                "stocks": {"weight": self.config.stocks_weight, "quantum_enhanced": True},
                "forex": {"weight": self.config.forex_weight, "quantum_enhanced": True},
                "metals": {"weight": self.config.metals_weight, "quantum_enhanced": True},
                "crypto": {"weight": self.config.crypto_weight, "quantum_enhanced": True}
            },
            "quantum_state": await self.quantum_optimizer.create_portfolio_state(),
            "error_correction": await self.error_corrector.setup_portfolio_protection(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def execute_quantum_trading_cycle(self) -> Dict[str, Any]:
        """Asosiy quantum trading tsiklini bajarish"""
        cycle_start = datetime.now()
        self.logger.info(f"Starting quantum trading cycle at {cycle_start}")
        
        try:
            # 1. Market data collection with quantum enhancement
            market_data = await self._collect_quantum_market_data()
            
            # 2. Quantum portfolio optimization
            optimized_portfolio = await self._quantum_portfolio_optimization(market_data)
            
            # 3. Execute trades with error correction
            trade_results = await self._execute_quantum_trades(optimized_portfolio)
            
            # 4. Update portfolio state
            await self._update_portfolio_state(trade_results)
            
            # 5. Calculate quantum advantage metrics
            metrics = await self._calculate_cycle_metrics(trade_results)
            
            cycle_end = datetime.now()
            cycle_duration = (cycle_end - cycle_start).total_seconds()
            
            cycle_result = {
                "cycle_id": f"quantum_cycle_{cycle_start.strftime('%Y%m%d_%H%M%S')}",
                "timestamp": cycle_end.isoformat(),
                "duration_seconds": cycle_duration,
                "status": "completed",
                "portfolio_update": trade_results,
                "quantum_advantage": metrics,
                "error_correction": await self.error_corrector.get_correction_stats()
            }
            
            self.trading_history.append(cycle_result)
            self.logger.info(f"Quantum trading cycle completed in {cycle_duration:.2f}s")
            
            return cycle_result
            
        except Exception as e:
            self.logger.error(f"Trading cycle failed: {str(e)}")
            return {
                "cycle_id": f"failed_cycle_{cycle_start.strftime('%Y%m%d_%H%M%S')}",
                "timestamp": cycle_end.isoformat() if 'cycle_end' in locals() else datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }
    
    async def _collect_quantum_market_data(self) -> Dict[str, Any]:
        """Quantum enhanced market data collection"""
        self.logger.info("Collecting quantum enhanced market data...")
        
        # Multi-asset data collection
        stocks_data = await self.multi_asset_trader.collect_stocks_data()
        forex_data = await self.multi_asset_trader.collect_forex_data()
        metals_data = await self.multi_asset_trader.collect_metals_data()
        crypto_data = await self.multi_asset_trader.collect_crypto_data()
        
        # Quantum superposition of market states
        quantum_market_state = await self.quantum_optimizer.create_market_superposition({
            "stocks": stocks_data,
            "forex": forex_data,
            "metals": metals_data,
            "crypto": crypto_data
        })
        
        return {
            "stocks": stocks_data,
            "forex": forex_data,
            "metals": metals_data,
            "crypto": crypto_data,
            "quantum_superposition": quantum_market_state,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _quantum_portfolio_optimization(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Quantum portfolio optimization"""
        self.logger.info("Performing quantum portfolio optimization...")
        
        # Create quantum optimization problem
        optimization_problem = {
            "current_portfolio": self.portfolio_state,
            "market_data": market_data,
            "constraints": {
                "max_drawdown": self.config.max_drawdown,
                "quantum_advantage_target": self.config.quantum_advantage_threshold
            }
        }
        
        # Execute quantum optimization
        optimal_allocation = await self.quantum_optimizer.optimize_portfolio(optimization_problem)
        
        # Apply error correction to optimization results
        corrected_allocation = await self.error_corrector.correct_optimization_results(optimal_allocation)
        
        return corrected_allocation
    
    async def _execute_quantum_trades(self, portfolio_allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute quantum enhanced trades"""
        self.logger.info("Executing quantum enhanced trades...")
        
        # Multi-asset trade execution
        trade_results = {}
        
        for asset_type, allocation in portfolio_allocation["new_allocation"].items():
            if allocation["change"] != 0:
                trade_result = await self.multi_asset_trader.execute_quantum_trade(
                    asset_type=asset_type,
                    allocation=allocation,
                    quantum_state=portfolio_allocation.get("quantum_state")
                )
                trade_results[asset_type] = trade_result
        
        return trade_results
    
    async def _update_portfolio_state(self, trade_results: Dict[str, Any]):
        """Portfolio holatini yangilash"""
        self.logger.info("Updating portfolio state...")
        
        # Update quantum portfolio state
        new_portfolio = await self.quantum_optimizer.update_portfolio_state(
            current_state=self.portfolio_state,
            trade_results=trade_results
        )
        
        # Apply error correction to new state
        corrected_portfolio = await self.error_corrector.correct_portfolio_state(new_portfolio)
        
        self.portfolio_state = corrected_portfolio
        
        # Store quantum circuit state for future analysis
        circuit_state = await self.quantum_optimizer.get_circuit_state()
        self.quantum_circuit_states[datetime.now().isoformat()] = circuit_state
    
    async def _calculate_cycle_metrics(self, trade_results: Dict[str, Any]) -> Dict[str, Any]:
        """Tsikl metrikalarini hisoblash"""
        return await self.metrics_calculator.calculate_cycle_metrics(
            trade_results=trade_results,
            portfolio_state=self.portfolio_state,
            quantum_advantage_threshold=self.config.quantum_advantage_threshold
        )
    
    async def run_continuous_trading(self, duration_hours: int = 24) -> Dict[str, Any]:
        """Davomiy quantum trading tizimi"""
        self.logger.info(f"Starting continuous quantum trading for {duration_hours} hours...")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        cycle_count = 0
        successful_cycles = 0
        total_quantum_advantage = 0.0
        
        async def trading_loop():
            nonlocal cycle_count, successful_cycles, total_quantum_advantage
            
            while datetime.now() < end_time:
                cycle_count += 1
                
                try:
                    # Execute trading cycle
                    result = await self.execute_quantum_trading_cycle()
                    
                    if result["status"] == "completed":
                        successful_cycles += 1
                        advantage = result["quantum_advantage"].get("overall_advantage", 0.0)
                        total_quantum_advantage += advantage
                        
                        self.logger.info(
                            f"Cycle {cycle_count}: Success, "
                            f"Quantum Advantage: {advantage:.4f}"
                        )
                    
                    # Wait before next cycle
                    await asyncio.sleep(self.config.benchmark_interval)
                    
                except Exception as e:
                    self.logger.error(f"Cycle {cycle_count} failed: {str(e)}")
                    await asyncio.sleep(60)  # Wait 1 minute on error
        
        # Start trading loop
        await trading_loop()
        
        # Calculate final statistics
        final_stats = {
            "duration_hours": duration_hours,
            "total_cycles": cycle_count,
            "successful_cycles": successful_cycles,
            "success_rate": successful_cycles / cycle_count if cycle_count > 0 else 0,
            "average_quantum_advantage": total_quantum_advantage / successful_cycles if successful_cycles > 0 else 0,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "final_portfolio_state": self.portfolio_state
        }
        
        self.logger.info(f"Continuous trading completed: {final_stats}")
        return final_stats
    
    def get_system_status(self) -> Dict[str, Any]:
        """Tizim holatini olish"""
        return {
            "status": "running" if self.portfolio_state else "initialized",
            "config": self.config.__dict__,
            "portfolio_state": self.portfolio_state,
            "trading_cycles_completed": len(self.trading_history),
            "last_cycle": self.trading_history[-1] if self.trading_history else None,
            "timestamp": datetime.now().isoformat()
        }
    
    async def export_results(self, output_file: str):
        """Natijalarni faylga eksport qilish"""
        export_data = {
            "system_config": self.config.__dict__,
            "trading_history": self.trading_history,
            "portfolio_evolution": self.performance_metrics,
            "quantum_circuit_states": self.quantum_circuit_states,
            "final_status": self.get_system_status()
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Results exported to {output_file}")

# Example usage
async def main():
    """Test va demo uchun asosiy funksiya"""
    config = TradingConfig(
        quantum_advantage_threshold=0.12,
        stocks_weight=0.5,
        forex_weight=0.25,
        metals_weight=0.15,
        crypto_weight=0.1
    )
    
    # Initialize system
    system = QuantumAdvantageTradingSystem(config)
    await system.initialize_system()
    
    # Run single trading cycle
    result = await system.execute_quantum_trading_cycle()
    print(f"Trading cycle result: {result}")
    
    # Get system status
    status = system.get_system_status()
    print(f"System status: {status}")
    
    # Export results
    await system.export_results("quantum_trading_results.json")

if __name__ == "__main__":
    asyncio.run(main())