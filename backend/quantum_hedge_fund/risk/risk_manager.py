"""
Risk Management Engine
Comprehensive risk assessment va management tizimi
"""
import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskType(Enum):
    MARKET_RISK = "market_risk"
    CREDIT_RISK = "credit_risk"
    LIQUIDITY_RISK = "liquidity_risk"
    OPERATIONAL_RISK = "operational_risk"
    QUANTUM_RISK = "quantum_risk"

@dataclass
class RiskAssessment:
    """Risk assessment natijasi"""
    risk_level: RiskLevel
    risk_score: float
    var_1d: float
    var_5d: float
    expected_shortfall: float
    max_drawdown: float
    volatility: float
    correlation_risk: float
    quantum_risk: float
    timestamp: datetime
    details: Dict[str, Any]

@dataclass
class RiskLimit:
    """Risk limit"""
    risk_type: RiskType
    limit_value: float
    current_value: float
    utilization: float
    status: str
    threshold: float = 0.8  # Alert at 80% utilization

class RiskManager:
    """Risk Management Engine"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("risk_manager")
        self.is_initialized = False
        
        # Risk state
        self.current_risk_level = RiskLevel.MEDIUM
        self.risk_limits: Dict[RiskType, RiskLimit] = {}
        self.risk_history: List[RiskAssessment] = []
        self.stress_tests: Dict[str, Dict] = {}
        
        # Risk models
        self.var_models = {}
        self.correlation_models = {}
        self.factor_models = {}
        
        # Portfolio data
        self.portfolio_data: Dict[str, Any] = {}
        self.market_data: Dict[str, pd.DataFrame] = {}
        self.factor_exposures: Dict[str, np.ndarray] = {}
        
        # Risk monitoring
        self.risk_alerts: List[Dict] = []
        self.risk_monitoring_active = False
        
        # Configuration
        self.confidence_levels = config.get("confidence_levels", [0.95, 0.99])
        self.var_horizon = config.get("var_horizon", 1)  # 1 day
        self.stress_test_frequency = config.get("stress_test_frequency", 24)  # hours
        
        # Risk limits
        self.max_portfolio_var = config.get("max_portfolio_var", 0.05)  # 5% of portfolio
        self.max_position_var = config.get("max_position_var", 0.02)  # 2% of portfolio
        self.max_sector_concentration = config.get("max_sector_concentration", 0.3)  # 30%
        self.max_single_position = config.get("max_single_position", 0.1)  # 10%
        
    async def initialize(self):
        """Risk Manager'ni ishga tushirish"""
        try:
            self.logger.info("Risk Manager ishga tushirilmoqda...")
            
            # Initialize risk models
            await self._initialize_risk_models()
            
            # Setup risk limits
            await self._setup_risk_limits()
            
            # Load portfolio data
            await self._load_portfolio_data()
            
            # Start risk monitoring
            await self._start_risk_monitoring()
            
            self.is_initialized = True
            self.logger.info("✅ Risk Manager muvaffaqiyatli ishga tushdi!")
            
        except Exception as e:
            self.logger.error(f"Risk Manager ishga tushirishda xato: {e}")
            raise
    
    async def _initialize_risk_models(self):
        """Risk modellarni ishga tushirish"""
        try:
            # Initialize VaR models
            self.var_models = {
                "historical_var": self._historical_var,
                "parametric_var": self._parametric_var,
                "monte_carlo_var": self._monte_carlo_var,
                "quantum_enhanced_var": self._quantum_enhanced_var
            }
            
            # Initialize correlation models
            self.correlation_models = {
                "pearson_correlation": self._pearson_correlation,
                "spearman_correlation": self._spearman_correlation,
                "dynamic_correlation": self._dynamic_correlation
            }
            
            # Initialize factor models
            self.factor_models = {
                "capm_factor_model": self._capm_factor_model,
                "multi_factor_model": self._multi_factor_model,
                "quantum_factor_model": self._quantum_factor_model
            }
            
            self.logger.info("Risk modellar muvaffaqiyatli ishga tushirildi")
            
        except Exception as e:
            self.logger.error(f"Risk models initializationda xato: {e}")
    
    async def _setup_risk_limits(self):
        """Risk limitlarni sozlab olish"""
        try:
            self.risk_limits = {
                RiskType.MARKET_RISK: RiskLimit(
                    risk_type=RiskType.MARKET_RISK,
                    limit_value=self.max_portfolio_var,
                    current_value=0.0,
                    utilization=0.0,
                    status="OK"
                ),
                RiskType.CREDIT_RISK: RiskLimit(
                    risk_type=RiskType.CREDIT_RISK,
                    limit_value=0.05,  # 5% credit exposure limit
                    current_value=0.02,
                    utilization=0.4,
                    status="OK"
                ),
                RiskType.LIQUIDITY_RISK: RiskLimit(
                    risk_type=RiskType.LIQUIDITY_RISK,
                    limit_value=0.10,  # 10% illiquid assets limit
                    current_value=0.05,
                    utilization=0.5,
                    status="OK"
                ),
                RiskType.OPERATIONAL_RISK: RiskLimit(
                    risk_type=RiskType.OPERATIONAL_RISK,
                    limit_value=1000000,  # $1M operational risk capital
                    current_value=200000,
                    utilization=0.2,
                    status="OK"
                ),
                RiskType.QUANTUM_RISK: RiskLimit(
                    risk_type=RiskType.QUANTUM_RISK,
                    limit_value=0.02,  # 2% quantum algorithm risk
                    current_value=0.01,
                    utilization=0.5,
                    status="OK"
                )
            }
            
            self.logger.info("Risk limitlar muvaffaqiyatli sozlandi")
            
        except Exception as e:
            self.logger.error(f"Risk limits setupda xato: {e}")
    
    async def _load_portfolio_data(self):
        """Portfolio data yuklash"""
        try:
            # Simulate comprehensive portfolio data
            self.portfolio_data = {
                "positions": {
                    "AAPL": {"quantity": 1000, "market_value": 150000, "sector": "Technology"},
                    "GOOGL": {"quantity": 200, "market_value": 560000, "sector": "Technology"},
                    "MSFT": {"quantity": 800, "market_value": 240000, "sector": "Technology"},
                    "TSLA": {"quantity": 300, "market_value": 75000, "sector": "Consumer Discretionary"},
                    "AMZN": {"quantity": 400, "market_value": 120000, "sector": "Consumer Discretionary"},
                    "NVDA": {"quantity": 500, "market_value": 200000, "sector": "Technology"}
                },
                "total_value": 1345000,
                "cash": 50000,
                "currency": "USD"
            }
            
            # Update sector concentrations
            total_value = self.portfolio_data["total_value"]
            sector_values = {}
            for position in self.portfolio_data["positions"].values():
                sector = position["sector"]
                if sector not in sector_values:
                    sector_values[sector] = 0
                sector_values[sector] += position["market_value"]
            
            for sector, value in sector_values.items():
                concentration = value / total_value
                if sector == "Technology":
                    self.risk_limits[RiskType.MARKET_RISK].current_value = concentration
                    self.risk_limits[RiskType.MARKET_RISK].utilization = concentration / self.max_sector_concentration
            
            self.logger.info("Portfolio data muvaffaqiyatli yuklandi")
            
        except Exception as e:
            self.logger.error(f"Portfolio data yuklashda xato: {e}")
    
    async def _start_risk_monitoring(self):
        """Risk monitoring'ni boshlash"""
        try:
            self.risk_monitoring_active = True
            
            # Start monitoring tasks
            asyncio.create_task(self._risk_monitoring_loop())
            asyncio.create_task(self._stress_testing_loop())
            asyncio.create_task(self._var_calculation_loop())
            
            self.logger.info("Risk monitoring muvaffaqiyatli boshlandi")
            
        except Exception as e:
            self.logger.error(f"Risk monitoring startda xato: {e}")
    
    async def assess_portfolio_risk(self) -> RiskAssessment:
        """Portfolio risk assessment"""
        try:
            self.logger.info("Portfolio risk assessment boshlanmoqda...")
            
            # Calculate various risk metrics
            var_1d = await self._calculate_portfolio_var(confidence_level=0.95)
            var_5d = await self._calculate_portfolio_var(confidence_level=0.95, horizon=5)
            expected_shortfall = await self._calculate_expected_shortfall(var_1d)
            max_drawdown = await self._calculate_max_drawdown()
            volatility = await self._calculate_portfolio_volatility()
            correlation_risk = await self._assess_correlation_risk()
            quantum_risk = await self._assess_quantum_risk()
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(var_1d, volatility, correlation_risk, quantum_risk)
            
            # Determine risk level
            if risk_score > 0.8:
                risk_level = RiskLevel.CRITICAL
            elif risk_score > 0.6:
                risk_level = RiskLevel.HIGH
            elif risk_score > 0.3:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            self.current_risk_level = risk_level
            
            # Create assessment
            assessment = RiskAssessment(
                risk_level=risk_level,
                risk_score=risk_score,
                var_1d=var_1d,
                var_5d=var_5d,
                expected_shortfall=expected_shortfall,
                max_drawdown=max_drawdown,
                volatility=volatility,
                correlation_risk=correlation_risk,
                quantum_risk=quantum_risk,
                timestamp=datetime.now(),
                details={
                    "portfolio_value": self.portfolio_data["total_value"],
                    "positions_count": len(self.portfolio_data["positions"]),
                    "largest_position": await self._get_largest_position(),
                    "sector_concentration": await self._get_sector_concentration(),
                    "var_confidence": 0.95
                }
            )
            
            # Add to history
            self.risk_history.append(assessment)
            
            # Keep only last 1000 assessments
            if len(self.risk_history) > 1000:
                self.risk_history = self.risk_history[-1000:]
            
            self.logger.info(f"✅ Risk assessment yakunlandi. Risk level: {risk_level.value}, Score: {risk_score:.3f}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Portfolio risk assessmentda xato: {e}")
            # Return default assessment
            return RiskAssessment(
                risk_level=RiskLevel.HIGH,
                risk_score=1.0,
                var_1d=0.05,
                var_5d=0.12,
                expected_shortfall=0.08,
                max_drawdown=0.15,
                volatility=0.20,
                correlation_risk=0.50,
                quantum_risk=0.30,
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    async def _calculate_portfolio_var(self, confidence_level: float = 0.95, horizon: int = 1) -> float:
        """Portfolio VaR hisoblash"""
        try:
            # Use multiple VaR models for robustness
            var_results = []
            
            # Historical VaR
            historical_var = await self._historical_var(confidence_level, horizon)
            if historical_var > 0:
                var_results.append(historical_var)
            
            # Parametric VaR
            parametric_var = await self._parametric_var(confidence_level, horizon)
            if parametric_var > 0:
                var_results.append(parametric_var)
            
            # Monte Carlo VaR
            mc_var = await self._monte_carlo_var(confidence_level, horizon)
            if mc_var > 0:
                var_results.append(mc_var)
            
            # Quantum Enhanced VaR
            quantum_var = await self._quantum_enhanced_var(confidence_level, horizon)
            if quantum_var > 0:
                var_results.append(quantum_var)
            
            # Return average VaR
            if var_results:
                return np.mean(var_results)
            else:
                # Fallback to conservative estimate
                portfolio_volatility = await self._estimate_portfolio_volatility()
                return portfolio_volatility * stats.norm.ppf(1 - confidence_level) * np.sqrt(horizon)
                
        except Exception as e:
            self.logger.error(f"Portfolio VaR calculationda xato: {e}")
            return 0.05  # Default 5% VaR
    
    async def _historical_var(self, confidence_level: float, horizon: int) -> float:
        """Historical VaR"""
        try:
            # Simulate historical returns
            np.random.seed(42)
            returns = np.random.normal(0.001, 0.02, 252)  # 1 year of daily returns
            
            # Sort returns
            sorted_returns = np.sort(returns)
            
            # Calculate VaR
            var_index = int((1 - confidence_level) * len(sorted_returns))
            var_1d = -sorted_returns[var_index]  # VaR is positive number
            
            # Scale for horizon
            return var_1d * np.sqrt(horizon)
            
        except Exception as e:
            self.logger.error(f"Historical VaR calculationda xato: {e}")
            return 0.0
    
    async def _parametric_var(self, confidence_level: float, horizon: int) -> float:
        """Parametric VaR"""
        try:
            # Estimate portfolio parameters
            portfolio_volatility = await self._estimate_portfolio_volatility()
            
            # Calculate VaR using normal distribution
            z_score = stats.norm.ppf(1 - confidence_level)
            var_1d = -z_score * portfolio_volatility
            
            return abs(var_1d) * np.sqrt(horizon)
            
        except Exception as e:
            self.logger.error(f"Parametric VaR calculationda xato: {e}")
            return 0.0
    
    async def _monte_carlo_var(self, confidence_level: float, horizon: int) -> float:
        """Monte Carlo VaR"""
        try:
            # Simulate portfolio returns using Monte Carlo
            np.random.seed(42)
            n_simulations = 10000
            
            portfolio_volatility = await self._estimate_portfolio_volatility()
            
            # Generate simulated returns
            simulated_returns = np.random.normal(0, portfolio_volatility, (n_simulations, horizon))
            portfolio_returns = np.sum(simulated_returns, axis=1)
            
            # Calculate VaR
            sorted_returns = np.sort(portfolio_returns)
            var_index = int((1 - confidence_level) * len(sorted_returns))
            var = -sorted_returns[var_index]
            
            return abs(var)
            
        except Exception as e:
            self.logger.error(f"Monte Carlo VaR calculationda xato: {e}")
            return 0.0
    
    async def _quantum_enhanced_var(self, confidence_level: float, horizon: int) -> float:
        """Quantum Enhanced VaR"""
        try:
            # Base VaR calculation
            base_var = await self._monte_carlo_var(confidence_level, horizon)
            
            # Quantum enhancement factors
            quantum_factors = await self._calculate_quantum_risk_factors()
            
            # Apply quantum enhancement
            quantum_boost = 1 + quantum_factors["quantum_uncertainty"] * 0.1
            quantum_var = base_var * quantum_boost
            
            return quantum_var
            
        except Exception as e:
            self.logger.error(f"Quantum Enhanced VaR calculationda xato: {e}")
            return 0.0
    
    async def _estimate_portfolio_volatility(self) -> float:
        """Portfolio volatility estimate"""
        try:
            # Weighted average of position volatilities
            total_value = self.portfolio_data["total_value"]
            portfolio_var = 0.0
            
            for symbol, position in self.portfolio_data["positions"].items():
                weight = position["market_value"] / total_value
                # Assume 20% volatility for each position (simplified)
                position_vol = 0.20
                portfolio_var += (weight ** 2) * (position_vol ** 2)
            
            # Add correlation effects (simplified)
            correlation_factor = 0.3
            portfolio_var += correlation_factor * (np.sqrt(portfolio_var) ** 2)
            
            return np.sqrt(portfolio_var)
            
        except Exception as e:
            self.logger.error(f"Portfolio volatility estimationda xato: {e}")
            return 0.20  # Default 20% volatility
    
    async def _calculate_expected_shortfall(self, var: float) -> float:
        """Expected Shortfall hisoblash"""
        try:
            # ES is typically 1.3-1.5 times VaR
            es_multiplier = 1.4
            return var * es_multiplier
            
        except Exception as e:
            self.logger.error(f"Expected Shortfall calculationda xato: {e}")
            return var * 1.4
    
    async def _calculate_max_drawdown(self) -> float:
        """Maximum drawdown hisoblash"""
        try:
            # Simulate historical drawdowns
            np.random.seed(42)
            portfolio_value = 1000000
            drawdowns = []
            
            # Simulate portfolio path
            for i in range(252):  # 1 year
                daily_return = np.random.normal(0.001, 0.02)
                portfolio_value *= (1 + daily_return)
                
                # Calculate running maximum
                if i == 0:
                    peak = portfolio_value
                else:
                    peak = max(peak, portfolio_value)
                
                # Calculate drawdown
                drawdown = (peak - portfolio_value) / peak
                drawdowns.append(drawdown)
            
            return max(drawdowns)
            
        except Exception as e:
            self.logger.error(f"Max drawdown calculationda xato: {e}")
            return 0.15  # Default 15% drawdown
    
    async def _calculate_portfolio_volatility(self) -> float:
        """Portfolio volatility hisoblash"""
        try:
            return await self._estimate_portfolio_volatility()
            
        except Exception as e:
            self.logger.error(f"Portfolio volatility calculationda xato: {e}")
            return 0.20
    
    async def _assess_correlation_risk(self) -> float:
        """Correlation risk assessment"""
        try:
            # Calculate average correlation between positions
            positions = list(self.portfolio_data["positions"].keys())
            
            if len(positions) < 2:
                return 0.0
            
            # Simulate correlations
            np.random.seed(42)
            correlations = []
            
            # Generate random correlation matrix
            for i in range(min(len(positions), 5)):
                for j in range(i + 1, min(len(positions), 5)):
                    correlation = np.random.uniform(0.1, 0.8)
                    correlations.append(correlation)
            
            avg_correlation = np.mean(correlations) if correlations else 0.5
            
            # Higher correlation = higher risk
            correlation_risk = avg_correlation * 0.5  # Scale to 0-0.5 range
            
            return correlation_risk
            
        except Exception as e:
            self.logger.error(f"Correlation risk assessmentda xato: {e}")
            return 0.25
    
    async def _assess_quantum_risk(self) -> float:
        """Quantum risk assessment"""
        try:
            # Assess risks specific to quantum algorithms
            quantum_risk_factors = {
                "algorithm_accuracy": 0.1,
                "quantum_advantage_uncertainty": 0.15,
                "hardware_dependencies": 0.05,
                "calibration_risk": 0.08
            }
            
            total_quantum_risk = sum(quantum_risk_factors.values())
            
            return min(total_quantum_risk, 0.4)  # Cap at 40%
            
        except Exception as e:
            self.logger.error(f"Quantum risk assessmentda xato: {e}")
            return 0.3
    
    async def _calculate_quantum_risk_factors(self) -> Dict:
        """Quantum risk factors hisoblash"""
        try:
            return {
                "quantum_uncertainty": np.random.uniform(0.05, 0.15),
                "quantum_noise": np.random.uniform(0.02, 0.08),
                "quantum_decoherence": np.random.uniform(0.01, 0.05)
            }
            
        except Exception as e:
            self.logger.error(f"Quantum risk factors calculationda xato: {e}")
            return {"quantum_uncertainty": 0.1, "quantum_noise": 0.05, "quantum_decoherence": 0.03}
    
    def _calculate_risk_score(self, var: float, volatility: float, correlation_risk: float, quantum_risk: float) -> float:
        """Overall risk score hisoblash"""
        try:
            # Weight different risk components
            weights = {
                "var": 0.3,
                "volatility": 0.2,
                "correlation": 0.25,
                "quantum": 0.25
            }
            
            # Normalize risk metrics (0-1 scale)
            var_score = min(var / 0.1, 1.0)  # Cap VaR at 10%
            volatility_score = min(volatility / 0.3, 1.0)  # Cap volatility at 30%
            correlation_score = min(correlation_risk / 0.5, 1.0)  # Cap correlation risk at 50%
            quantum_score = min(quantum_risk / 0.4, 1.0)  # Cap quantum risk at 40%
            
            # Calculate weighted score
            risk_score = (
                weights["var"] * var_score +
                weights["volatility"] * volatility_score +
                weights["correlation"] * correlation_score +
                weights["quantum"] * quantum_score
            )
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Risk score calculationda xato: {e}")
            return 0.5
    
    async def _get_largest_position(self) -> Dict:
        """Largest position olish"""
        try:
            largest_position = max(
                self.portfolio_data["positions"].items(),
                key=lambda x: x[1]["market_value"]
            )
            
            return {
                "symbol": largest_position[0],
                "value": largest_position[1]["market_value"],
                "percentage": largest_position[1]["market_value"] / self.portfolio_data["total_value"]
            }
            
        except Exception as e:
            self.logger.error(f"Largest position olishda xato: {e}")
            return {}
    
    async def _get_sector_concentration(self) -> Dict:
        """Sector concentration olish"""
        try:
            sector_values = {}
            total_value = self.portfolio_data["total_value"]
            
            for position in self.portfolio_data["positions"].values():
                sector = position["sector"]
                if sector not in sector_values:
                    sector_values[sector] = 0
                sector_values[sector] += position["market_value"]
            
            # Calculate concentrations
            concentrations = {sector: value / total_value for sector, value in sector_values.items()}
            
            return concentrations
            
        except Exception as e:
            self.logger.error(f"Sector concentration olishda xato: {e}")
            return {}
    
    async def _pearson_correlation(self, returns1: np.ndarray, returns2: np.ndarray) -> float:
        """Pearson correlation"""
        try:
            correlation = np.corrcoef(returns1, returns2)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    async def _spearman_correlation(self, returns1: np.ndarray, returns2: np.ndarray) -> float:
        """Spearman correlation"""
        try:
            correlation = stats.spearmanr(returns1, returns2)[0]
            return correlation if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    async def _dynamic_correlation(self, returns1: np.ndarray, returns2: np.ndarray, window: int = 50) -> float:
        """Dynamic correlation"""
        try:
            if len(returns1) < window or len(returns2) < window:
                return await self._pearson_correlation(returns1, returns2)
            
            # Calculate rolling correlation
            correlations = []
            for i in range(window, len(returns1)):
                corr = await self._pearson_correlation(returns1[i-window:i], returns2[i-window:i])
                correlations.append(corr)
            
            return np.mean(correlations) if correlations else 0.0
            
        except Exception as e:
            self.logger.error(f"Dynamic correlation calculationda xato: {e}")
            return 0.0
    
    async def _capm_factor_model(self) -> Dict:
        """CAPM factor model"""
        try:
            # Simplified CAPM model implementation
            market_beta = np.random.uniform(0.8, 1.2)  # Market beta
            alpha = np.random.normal(0, 0.01)  # Alpha
            market_premium = 0.06  # 6% market premium
            
            expected_return = alpha + market_beta * market_premium
            
            return {
                "expected_return": expected_return,
                "beta": market_beta,
                "alpha": alpha,
                "r_squared": np.random.uniform(0.6, 0.9)
            }
            
        except Exception as e:
            self.logger.error(f"CAPM factor modelda xato: {e}")
            return {}
    
    async def _multi_factor_model(self) -> Dict:
        """Multi-factor model"""
        try:
            # Multi-factor model with multiple risk factors
            factors = {
                "market": np.random.uniform(0.8, 1.2),
                "size": np.random.uniform(-0.2, 0.2),
                "value": np.random.uniform(-0.1, 0.1),
                "momentum": np.random.uniform(-0.1, 0.1),
                "quality": np.random.uniform(-0.1, 0.1)
            }
            
            return {
                "factor_loadings": factors,
                "model_r_squared": np.random.uniform(0.7, 0.95)
            }
            
        except Exception as e:
            self.logger.error(f"Multi-factor modelda xato: {e}")
            return {}
    
    async def _quantum_factor_model(self) -> Dict:
        """Quantum factor model"""
        try:
            # Quantum-enhanced factor model
            quantum_factors = {
                "quantum_momentum": np.random.uniform(-0.1, 0.1),
                "quantum_mean_reversion": np.random.uniform(-0.1, 0.1),
                "quantum_correlation": np.random.uniform(-0.05, 0.05)
            }
            
            return {
                "quantum_factors": quantum_factors,
                "quantum_advantage": np.random.uniform(0.05, 0.15),
                "quantum_r_squared": np.random.uniform(0.75, 0.95)
            }
            
        except Exception as e:
            self.logger.error(f"Quantum factor modelda xato: {e}")
            return {}
    
    async def check_risk_limits(self) -> List[Dict]:
        """Risk limitlarni tekshirish"""
        try:
            violations = []
            
            for risk_type, limit in self.risk_limits.items():
                # Update current values (simplified)
                if risk_type == RiskType.MARKET_RISK:
                    limit.current_value = await self._calculate_portfolio_var(0.95)
                    limit.utilization = limit.current_value / limit.limit_value
                
                # Check limit violation
                if limit.utilization > limit.threshold:
                    status = "WARNING" if limit.utilization < 1.0 else "CRITICAL"
                    violation = {
                        "risk_type": risk_type.value,
                        "limit_value": limit.limit_value,
                        "current_value": limit.current_value,
                        "utilization": limit.utilization,
                        "status": status,
                        "timestamp": datetime.now()
                    }
                    violations.append(violation)
                    
                    limit.status = status
                    
                    # Add to alerts
                    self.risk_alerts.append({
                        "type": "risk_limit_violation",
                        "violation": violation,
                        "timestamp": datetime.now()
                    })
            
            if violations:
                self.logger.warning(f"Risk limit violations detected: {len(violations)}")
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Risk limits checkda xato: {e}")
            return []
    
    async def get_risk_metrics(self) -> Dict:
        """Risk metrikalarini olish"""
        try:
            # Get latest risk assessment
            latest_assessment = None
            if self.risk_history:
                latest_assessment = self.risk_history[-1]
            
            return {
                "current_risk_level": self.current_risk_level.value,
                "risk_score": latest_assessment.risk_score if latest_assessment else 0.5,
                "var_1d": latest_assessment.var_1d if latest_assessment else 0.05,
                "var_5d": latest_assessment.var_5d if latest_assessment else 0.12,
                "expected_shortfall": latest_assessment.expected_shortfall if latest_assessment else 0.08,
                "max_drawdown": latest_assessment.max_drawdown if latest_assessment else 0.15,
                "volatility": latest_assessment.volatility if latest_assessment else 0.20,
                "correlation_risk": latest_assessment.correlation_risk if latest_assessment else 0.25,
                "quantum_advantage": latest_assessment.quantum_risk if latest_assessment else 0.30,
                "risk_limits": {
                    risk_type.value: {
                        "limit": limit.limit_value,
                        "current": limit.current_value,
                        "utilization": limit.utilization,
                        "status": limit.status
                    } for risk_type, limit in self.risk_limits.items()
                },
                "active_alerts": len(self.risk_alerts),
                "assessments_count": len(self.risk_history)
            }
            
        except Exception as e:
            self.logger.error(f"Risk metrics olishda xato: {e}")
            return {}
    
    async def run_stress_test(self, scenario: str = "historical_crash") -> Dict:
        """Stress test o'tkazish"""
        try:
            self.logger.info(f"Stress test boshlanmoqda: {scenario}")
            
            # Define stress scenarios
            stress_scenarios = {
                "historical_crash": {
                    "market_shock": -0.30,  # 30% market decline
                    "volatility_spike": 3.0,  # 3x volatility
                    "correlation_spike": 0.95,  # High correlation
                    "liquidity_crisis": True
                },
                "financial_crisis": {
                    "market_shock": -0.40,
                    "volatility_spike": 4.0,
                    "correlation_spike": 0.98,
                    "liquidity_crisis": True
                },
                "quantum_algorithm_failure": {
                    "quantum_model_accuracy": 0.50,  # 50% accuracy loss
                    "quantum_advantage_loss": 0.15,
                    "operational_risk": 0.25
                }
            }
            
            scenario_params = stress_scenarios.get(scenario, stress_scenarios["historical_crash"])
            
            # Calculate stress impact
            portfolio_value = self.portfolio_data["total_value"]
            market_impact = portfolio_value * scenario_params.get("market_shock", 0)
            vol_impact = portfolio_value * scenario_params.get("volatility_spike", 1.0) * 0.1
            liquidity_impact = portfolio_value * 0.1 if scenario_params.get("liquidity_crisis") else 0
            
            total_impact = market_impact + vol_impact + liquidity_impact
            
            stress_result = {
                "scenario": scenario,
                "timestamp": datetime.now().isoformat(),
                "portfolio_value": portfolio_value,
                "estimated_loss": total_impact,
                "loss_percentage": total_impact / portfolio_value,
                "impact_breakdown": {
                    "market_impact": market_impact,
                    "volatility_impact": vol_impact,
                    "liquidity_impact": liquidity_impact
                },
                "stress_parameters": scenario_params,
                "survival_probability": max(0, 1 - abs(total_impact) / portfolio_value)
            }
            
            # Store stress test result
            self.stress_tests[scenario] = stress_result
            
            self.logger.info(f"✅ Stress test yakunlandi: {scenario}, Loss: {total_impact:.0f}")
            return stress_result
            
        except Exception as e:
            self.logger.error(f"Stress testda xato: {e}")
            return {"error": str(e)}
    
    async def _risk_monitoring_loop(self):
        """Risk monitoring loop"""
        while self.risk_monitoring_active and self.is_initialized:
            try:
                # Check risk limits
                await self.check_risk_limits()
                
                # Monitor for new risk alerts
                if len(self.risk_alerts) > 10:
                    self.logger.warning(f"High number of risk alerts: {len(self.risk_alerts)}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Risk monitoring loopda xato: {e}")
                await asyncio.sleep(60)
    
    async def _stress_testing_loop(self):
        """Stress testing loop"""
        while self.risk_monitoring_active and self.is_initialized:
            try:
                # Run periodic stress tests
                await self.run_stress_test("historical_crash")
                
                await asyncio.sleep(self.stress_test_frequency * 3600)  # Convert hours to seconds
                
            except Exception as e:
                self.logger.error(f"Stress testing loopda xato: {e}")
                await asyncio.sleep(3600)
    
    async def _var_calculation_loop(self):
        """VaR calculation loop"""
        while self.risk_monitoring_active and self.is_initialized:
            try:
                # Update risk metrics
                await self.assess_portfolio_risk()
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"VaR calculation loopda xato: {e}")
                await asyncio.sleep(300)
    
    async def close(self):
        """Risk Manager'ni yopish"""
        try:
            self.logger.info("Risk Manager yopilmoqda...")
            
            # Stop monitoring
            self.risk_monitoring_active = False
            
            # Clear data
            self.risk_limits.clear()
            self.risk_history.clear()
            self.stress_tests.clear()
            self.risk_alerts.clear()
            self.portfolio_data.clear()
            self.market_data.clear()
            self.factor_exposures.clear()
            self.var_models.clear()
            self.correlation_models.clear()
            self.factor_models.clear()
            
            self.is_initialized = False
            self.logger.info("✅ Risk Manager muvaffaqiyatli yopildi")
            
        except Exception as e:
            self.logger.error(f"Risk Manager'ni yopishda xato: {e}")
    
    async def get_risk_statistics(self) -> Dict:
        """Risk statistikalarini olish"""
        return {
            "initialized": self.is_initialized,
            "monitoring_active": self.risk_monitoring_active,
            "current_risk_level": self.current_risk_level.value,
            "risk_limits_configured": len(self.risk_limits),
            "risk_assessments": len(self.risk_history),
            "stress_tests_completed": len(self.stress_tests),
            "active_alerts": len(self.risk_alerts),
            "configuration": self.config
        }