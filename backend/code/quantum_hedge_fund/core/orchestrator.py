"""
Quantum AI Hedge Fund Platform - Main Orchestrator
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from quantum.quantum_engine import QuantumEngine
from quantum.quantum_ml import QuantumMLEngine
from trading.trading_engine import TradingEngine
from analytics.analytics_engine import AnalyticsEngine
from risk.risk_manager import RiskManager
from compliance.compliance_engine import ComplianceEngine

@dataclass
class SystemConfig:
    """Tizim konfiguratsiyasi"""
    quantum_enabled: bool = True
    auto_trading: bool = False
    risk_level: str = "medium"
    max_position_size: float = 0.1
    min_profit_threshold: float = 0.02
    compliance_mode: str = "strict"

@dataclass
class FundMetrics:
    """Fond metrikalari"""
    total_value: float
    daily_pnl: float
    monthly_pnl: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    quantum_advantage: float

class QuantumHedgeFundOrchestrator:
    """Quantum AI Hedge Fund asosiy orchestrator"""
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.system_config = SystemConfig(**self.config.get("system", {}))
        
        # Core engines
        self.quantum_engine = None
        self.quantum_ml_engine = None
        self.trading_engine = None
        self.analytics_engine = None
        self.risk_manager = None
        self.compliance_engine = None
        
        # State management
        self.is_running = False
        self.last_update = None
        self.fund_metrics = None
        self.active_strategies = {}
        
        # Performance tracking
        self.performance_history = []
        self.risk_alerts = []
        self.compliance_violations = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Konfiguratsiyani yuklash"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Konfiguratsiya fayli topilmadi: {config_path}")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Standart konfiguratsiya"""
        return {
            "system": {
                "quantum_enabled": True,
                "auto_trading": False,
                "risk_level": "medium",
                "max_position_size": 0.1,
                "min_profit_threshold": 0.02,
                "compliance_mode": "strict"
            },
            "quantum": {
                "simulator_backend": "qiskit_aer",
                "shots": 1024,
                "optimization_iterations": 100
            },
            "trading": {
                "max_trades_per_day": 100,
                "min_trade_size": 1000,
                "execution_delay": 0.1
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Logging sozlamalarini o'rnatish"""
        logger = logging.getLogger("quantum_hedge_fund")
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler("logs/quantum_hedge_fund.log")
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    async def initialize(self) -> bool:
        """Tizimni ishga tushirish"""
        try:
            self.logger.info("Quantum AI Hedge Fund tizimi ishga tushirilmoqda...")
            
            # Initialize engines
            if self.system_config.quantum_enabled:
                self.quantum_engine = QuantumEngine(self.config.get("quantum", {}))
                self.quantum_ml_engine = QuantumMLEngine(self.config.get("quantum", {}))
                
                await self.quantum_engine.initialize()
                await self.quantum_ml_engine.initialize()
            
            self.trading_engine = TradingEngine(self.config.get("trading", {}))
            self.analytics_engine = AnalyticsEngine()
            self.risk_manager = RiskManager(self.config.get("risk", {}))
            self.compliance_engine = ComplianceEngine(self.config.get("compliance", {}))
            
            # Initialize engines
            await self.trading_engine.initialize()
            await self.analytics_engine.initialize()
            await self.risk_manager.initialize()
            await self.compliance_engine.initialize()
            
            self.is_running = True
            self.last_update = datetime.now()
            
            self.logger.info("✅ Quantum AI Hedge Fund tizimi muvaffaqiyatli ishga tushdi!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Tizimni ishga tushirishda xato: {e}")
            return False
    
    async def shutdown(self):
        """Tizimni to'xtatish"""
        self.logger.info("Tizim to'xtatilmoqda...")
        self.is_running = False
        
        # Close all engines
        if self.quantum_engine:
            await self.quantum_engine.close()
        if self.trading_engine:
            await self.trading_engine.close()
        if self.analytics_engine:
            await self.analytics_engine.close()
        if self.risk_manager:
            await self.risk_manager.close()
        if self.compliance_engine:
            await self.compliance_engine.close()
        
        self.logger.info("Tizim to'xtatildi.")
    
    async def start_trading(self) -> bool:
        """Tradingni boshlash"""
        if not self.is_running:
            self.logger.error("Tizim ishga tushmagan!")
            return False
        
        try:
            self.logger.info("Automated trading boshlanmoqda...")
            
            # Risk assessment
            risk_assessment = await self.risk_manager.assess_portfolio_risk()
            if risk_assessment["risk_level"] > 0.8:
                self.logger.warning("Yuqori risk darajasi aniqlandi, trading to'xtatiladi")
                return False
            
            # Compliance check
            compliance_ok = await self.compliance_engine.check_compliance()
            if not compliance_ok:
                self.logger.error("Compliance tekshiruvidan o'tmadi!")
                return False
            
            # Start trading
            self.system_config.auto_trading = True
            await self.trading_engine.start_automated_trading()
            
            self.logger.info("✅ Automated trading boshlandi!")
            return True
            
        except Exception as e:
            self.logger.error(f"Tradingni boshlashda xato: {e}")
            return False
    
    async def stop_trading(self):
        """Tradingni to'xtatish"""
        self.logger.info("Trading to'xtatilmoqda...")
        self.system_config.auto_trading = False
        await self.trading_engine.stop_automated_trading()
        self.logger.info("✅ Trading to'xtatildi")
    
    async def quantum_optimize_portfolio(self) -> Dict:
        """Portfolio kvant optimizatsiyasi"""
        if not self.quantum_engine:
            self.logger.error("Quantum engine mavjud emas!")
            return {}
        
        try:
            self.logger.info("Portfolio kvant optimizatsiyasi boshlanmoqda...")
            
            # Get current portfolio
            current_portfolio = await self.analytics_engine.get_current_portfolio()
            
            # Quantum optimization
            optimization_result = await self.quantum_engine.optimize_portfolio(
                current_portfolio,
                risk_tolerance=self.system_config.risk_level
            )
            
            self.logger.info(f"✅ Optimizatsiya yakunlandi. Potentsial foyda: {optimization_result.get('expected_return', 0):.2%}")
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Kvant optimizatsiyada xato: {e}")
            return {}
    
    async def run_market_analysis(self) -> Dict:
        """Bozor tahlili"""
        try:
            self.logger.info("Bozor tahlili boshlanmoqda...")
            
            # Traditional analysis
            traditional_analysis = await self.analytics_engine.run_technical_analysis()
            
            # Quantum analysis
            quantum_analysis = None
            if self.quantum_ml_engine:
                quantum_analysis = await self.quantum_ml_engine.analyze_market_patterns()
            
            # Combine results
            analysis_result = {
                "timestamp": datetime.now().isoformat(),
                "traditional": traditional_analysis,
                "quantum": quantum_analysis,
                "confidence": self._calculate_confidence(traditional_analysis, quantum_analysis)
            }
            
            self.logger.info("✅ Bozor tahlili yakunlandi")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Bozor tahlilida xato: {e}")
            return {}
    
    def _calculate_confidence(self, traditional: Dict, quantum: Dict) -> float:
        """Tahlil ishonchliligini hisoblash"""
        try:
            conf_scores = []
            
            if traditional:
                conf_scores.append(traditional.get("confidence", 0.5))
            
            if quantum:
                conf_scores.append(quantum.get("confidence", 0.5))
            
            return sum(conf_scores) / len(conf_scores) if conf_scores else 0.5
            
        except:
            return 0.5
    
    async def update_fund_metrics(self):
        """Fond metrikalarini yangilash"""
        try:
            # Get metrics from various engines
            portfolio_metrics = await self.analytics_engine.get_portfolio_metrics()
            risk_metrics = await self.risk_manager.get_risk_metrics()
            
            # Calculate fund metrics
            self.fund_metrics = FundMetrics(
                total_value=portfolio_metrics.get("total_value", 0),
                daily_pnl=portfolio_metrics.get("daily_pnl", 0),
                monthly_pnl=portfolio_metrics.get("monthly_pnl", 0),
                sharpe_ratio=risk_metrics.get("sharpe_ratio", 0),
                max_drawdown=risk_metrics.get("max_drawdown", 0),
                win_rate=portfolio_metrics.get("win_rate", 0),
                quantum_advantage=risk_metrics.get("quantum_advantage", 0)
            )
            
            # Add to history
            self.performance_history.append({
                "timestamp": datetime.now().isoformat(),
                "metrics": self.fund_metrics
            })
            
            # Keep only last 1000 records
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-1000:]
            
            self.last_update = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Metrikalarni yangilashda xato: {e}")
    
    async def get_system_status(self) -> Dict:
        """Tizim holatini olish"""
        return {
            "status": "running" if self.is_running else "stopped",
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "auto_trading": self.system_config.auto_trading,
            "quantum_enabled": self.system_config.quantum_enabled,
            "fund_metrics": self.fund_metrics.__dict__ if self.fund_metrics else None,
            "active_strategies": list(self.active_strategies.keys()),
            "risk_alerts": len(self.risk_alerts),
            "compliance_violations": len(self.compliance_violations)
        }
    
    async def main_loop(self):
        """Asosiy ishchi tsikl"""
        self.logger.info("Asosiy ishchi tsikl boshlanmoqda...")
        
        while self.is_running:
            try:
                # Update metrics
                await self.update_fund_metrics()
                
                # Run analysis if quantum enabled
                if self.system_config.quantum_enabled:
                    await self.run_market_analysis()
                    if self.system_config.auto_trading:
                        await self.quantum_optimize_portfolio()
                
                # Risk monitoring
                await self.risk_manager.check_risk_limits()
                
                # Compliance monitoring
                await self.compliance_engine.monitor_compliance()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # 1 minute intervals
                
            except Exception as e:
                self.logger.error(f"Asosiy tsiklda xato: {e}")
                await asyncio.sleep(10)  # Wait 10 seconds before retry
    
    async def run(self):
        """Tizimni ishga tushirish va boshqarish"""
        try:
            # Initialize system
            if not await self.initialize():
                return
            
            # Run main loop
            await self.main_loop()
            
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt qabul qilindi")
        except Exception as e:
            self.logger.error(f"Kritik xato: {e}")
        finally:
            await self.shutdown()

# CLI Interface
async def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quantum AI Hedge Fund Platform")
    parser.add_argument("--config", default="config/config.json", help="Konfiguratsiya fayli")
    parser.add_argument("--no-quantum", action="store_true", help="Quantum funksiyalarni o'chirish")
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = QuantumHedgeFundOrchestrator(args.config)
    
    if args.no_quantum:
        orchestrator.system_config.quantum_enabled = False
    
    # Run system
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())