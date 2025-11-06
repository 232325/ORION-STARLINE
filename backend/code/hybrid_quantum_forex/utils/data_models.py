"""
Data Models - Hybrid Quantum Forex System
Ma'lumot modellari
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from enum import Enum
import uuid
import numpy as np

class CurrencyPair:
    """Valuta juftliklari"""
    EURUSD = "EURUSD"
    GBPUSD = "GBPUSD"
    USDJPY = "USDJPY"
    USDCHF = "USDCHF"
    USDCAD = "USDCAD"
    AUDUSD = "AUDUSD"
    NZDUSD = "NZDUSD"
    
    # Cross pairs
    EURJPY = "EURJPY"
    EURGBP = "EURGBP"
    EURCHF = "EURCHF"
    GBPJPY = "GBPJPY"
    GBPCHF = "GBPCHF"
    CHFJPY = "CHFJPY"
    
    # Minor pairs
    AUDCAD = "AUDCAD"
    AUDCHF = "AUDCHF"
    AUDJPY = "AUDJPY"
    AUDNZD = "AUDNZD"
    CADCHF = "CADCHF"
    CADJPY = "CADJPY"

class SystemState(Enum):
    """Tizim holatlari"""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"
    MAINTENANCE = "maintenance"

class TradeType(Enum):
    """Trade turlari"""
    BUY = "buy"
    SELL = "sell"

class ArbitrageType(Enum):
    """Arbitrage turlari"""
    TRIANGULAR = "triangular"
    CROSS_CURRENCY = "cross_currency"
    TIME_ZONE = "time_zone"
    CORRELATION = "correlation"
    VOLATILITY = "volatility"

class QuantumState(Enum):
    """Quantum holatlar"""
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    BUSY = "busy"

@dataclass
class MarketPrice:
    """Market narx ma'lumotlari"""
    pair: str
    bid: float
    ask: float
    timestamp: datetime
    source: str
    spread: float = field(init=False)
    mid_price: float = field(init=False)
    
    def __post_init__(self):
        self.spread = self.ask - self.bid
        self.mid_price = (self.bid + self.ask) / 2
    
    @property
    def effective_spread_pct(self) -> float:
        """Foiz hisobida spread"""
        return (self.spread / self.mid_price) * 100

@dataclass
class MarketData:
    """Kengaytirilgan market data"""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    prices: Dict[str, MarketPrice] = field(default_factory=dict)
    volume: Dict[str, float] = field(default_factory=dict)
    volatility: Dict[str, float] = field(default_factory=dict)
    correlation_matrix: Optional[np.ndarray] = None
    session: str = ""
    market_hours: bool = False
    
    def add_price(self, pair: str, bid: float, ask: float, source: str = "default"):
        """Price qo'shish"""
        self.prices[pair] = MarketPrice(
            pair=pair,
            bid=bid,
            ask=ask,
            timestamp=datetime.now(timezone.utc),
            source=source
        )
    
    def get_price(self, pair: str) -> Optional[MarketPrice]:
        """Price olish"""
        return self.prices.get(pair)
    
    def get_cross_rate(self, base: str, quote: str) -> Optional[float]:
        """Cross rate hisoblash"""
        direct_pair = f"{base}{quote}"
        reverse_pair = f"{quote}{base}"
        
        if direct_pair in self.prices:
            return self.prices[direct_pair].mid_price
        elif reverse_pair in self.prices:
            return 1.0 / self.prices[reverse_pair].mid_price
        else:
            # Triangular calculation needed
            return self._calculate_triangular_rate(base, quote)
    
    def _calculate_triangular_rate(self, base: str, quote: str) -> Optional[float]:
        """Triangular rate hisoblash"""
        # Example: EUR/GBP through USD
        if f"{base}USD" in self.prices and f"USD{quote}" in self.prices:
            base_usd = self.prices[f"{base}USD"].mid_price
            usd_quote = self.prices[f"USD{quote}"].mid_price
            return base_usd * usd_quote
        
        elif f"{quote}USD" in self.prices and f"USD{base}" in self.prices:
            quote_usd = self.prices[f"{quote}USD"].mid_price
            usd_base = self.prices[f"USD{base}"].mid_price
            return 1.0 / (quote_usd * usd_base)
        
        return None

@dataclass
class QuantumFeatures:
    """Quantum computed features"""
    correlation_entanglement: float  # -1 to 1
    volatility_superposition: float  # 0 to 1
    momentum_entanglement: float     # -1 to 1
    market_quantum_state: Dict[str, float]  # Quantum state per currency
    coherence_time: float           # Quantum coherence duration
    error_rate: float               # Quantum error rate

@dataclass
class ArbitrageCalculation:
    """Arbitrage hisoblash natijalari"""
    direct_rate: float
    cross_rate: float
    arbitrage_spread: float
    profit_potential: float
    risk_score: float
    time_sensitivity: float  # 0-1, how time-sensitive
    market_depth: float      # Available liquidity

@dataclass
class ArbitrageOpportunity:
    """Arbitrage imkoniyati"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    arbitrage_type: ArbitrageType = ArbitrageType.TRIANGULAR
    
    # Currency information
    currencies: List[str] = field(default_factory=list)
    pairs: List[str] = field(default_factory=list)
    
    # Rates
    rates: Dict[str, float] = field(default_factory=dict)
    calculations: Optional[ArbitrageCalculation] = None
    
    # Quantum features
    quantum_features: Optional[QuantumFeatures] = None
    
    # Risk assessment
    risk_level: float = 0.0  # 0-1
    max_profit: float = 0.0
    required_capital: float = 0.0
    execution_time_estimate: float = 0.0
    
    # Market conditions
    liquidity_score: float = 0.0
    volatility_score: float = 0.0
    time_window: float = 0.0  # Seconds available for execution
    
    # Validation
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    
    def calculate_profit_potential(self, capital: float = 100000) -> float:
        """Profit potential hisoblash"""
        if self.calculations:
            return (self.calculations.profit_potential / 100) * capital
        return 0.0
    
    def get_expected_return(self) -> float:
        """Expected return percentage"""
        if self.calculations:
            return self.calculations.profit_potential
        return 0.0
    
    def get_risk_adjusted_return(self) -> float:
        """Risk-adjusted return"""
        expected_return = self.get_expected_return()
        return expected_return / (1 + self.risk_level)

@dataclass
class TradeExecution:
    """Trade execution natijasi"""
    opportunity_id: str
    success: bool = False
    profit: float = 0.0
    loss: float = 0.0
    execution_time: float = 0.0
    slippage: float = 0.0
    
    # Execution details
    trades: List[Dict[str, Any]] = field(default_factory=list)
    total_cost: float = 0.0
    net_profit: float = 0.0
    
    # Market impact
    market_impact: float = 0.0
    liquidity_used: float = 0.0
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Error information
    error_message: str = ""
    failed_steps: List[str] = field(default_factory=list)
    
    def calculate_net_profit(self):
        """Net profit hisoblash"""
        self.net_profit = self.profit - self.loss - self.total_cost - self.slippage

@dataclass
class QuantumCircuitResult:
    """Quantum circuit hisoblash natijasi"""
    circuit_id: str
    result_data: Dict[str, Any]
    quantum_state: np.ndarray
    measurement_results: Dict[str, float]
    coherence_metrics: Dict[str, float]
    processing_time: float
    error_correction_applied: bool
    
@dataclass
class SystemMetrics:
    """Tizim metrikalari"""
    # Performance metrics
    total_processing_time: float = 0.0
    quantum_processing_time: float = 0.0
    classical_processing_time: float = 0.0
    total_latency: float = 0.0
    
    # Trading metrics
    total_opportunities: int = 0
    executed_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    total_profit: float = 0.0
    total_loss: float = 0.0
    
    # Risk metrics
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    average_profit_per_trade: float = 0.0
    
    # System metrics
    error_rate: float = 0.0
    uptime: float = 0.0
    quantum_fidelity: float = 0.0
    system_utilization: float = 0.0
    
    # Real-time metrics
    current_positions: Dict[str, float] = field(default_factory=dict)
    unrealized_pnl: float = 0.0
    available_capital: float = 1000000.0
    
    def calculate_performance_metrics(self):
        """Performance metrics hisoblash"""
        if self.executed_trades > 0:
            self.win_rate = (self.successful_trades / self.executed_trades) * 100
            self.average_profit_per_trade = self.total_profit / self.executed_trades
        
        if self.total_profit + self.total_loss > 0:
            self.sharpe_ratio = self.total_profit / (self.total_profit + self.total_loss)
        
        if self.total_opportunities > 0:
            self.system_utilization = (self.executed_trades / self.total_opportunities) * 100

@dataclass
class AuditLogEntry:
    """Audit log entry"""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    risk_level: str = "LOW"
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary ga konvert qilish"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'event_data': self.event_data,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'risk_level': self.risk_level
        }

@dataclass
class RiskAssessment:
    """Risk assessment natijasi"""
    overall_risk_score: float  # 0-1
    market_risk: float = 0.0
    liquidity_risk: float = 0.0
    operational_risk: float = 0.0
    quantum_risk: float = 0.0
    
    # Risk factors
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    
    # Limits
    position_limit: float = 0.0
    stop_loss_level: float = 0.0
    max_drawdown_limit: float = 0.0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    def get_risk_category(self) -> str:
        """Risk kategoriyasini olish"""
        if self.overall_risk_score <= 0.2:
            return "LOW"
        elif self.overall_risk_score <= 0.5:
            return "MEDIUM"
        elif self.overall_risk_score <= 0.8:
            return "HIGH"
        else:
            return "CRITICAL"

@dataclass
class TimeSeriesData:
    """Time series ma'lumotlar"""
    timestamps: List[datetime] = field(default_factory=list)
    values: List[float] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    
    def add_point(self, timestamp: datetime, value: float, label: str = ""):
        """Point qo'shish"""
        self.timestamps.append(timestamp)
        self.values.append(value)
        if label:
            self.labels.append(label)
    
    def get_latest_value(self) -> Optional[float]:
        """Oxirgi qiymatni olish"""
        return self.values[-1] if self.values else None
    
    def get_values_in_range(self, start_time: datetime, end_time: datetime) -> List[float]:
        """Vaqt oralig'ida qiymatlarni olish"""
        values = []
        for i, ts in enumerate(self.timestamps):
            if start_time <= ts <= end_time:
                values.append(self.values[i])
        return values
    
    def calculate_returns(self) -> List[float]:
        """Returns hisoblash"""
        if len(self.values) < 2:
            return []
        
        returns = []
        for i in range(1, len(self.values)):
            ret = (self.values[i] - self.values[i-1]) / self.values[i-1]
            returns.append(ret)
        return returns