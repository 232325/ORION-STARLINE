"""
AI Trading System - Data Models and Schemas
Pydantic asosida validatsiya va serializatsiya modellari
"""

from pydantic import BaseModel, Field, EmailStr, validator, HttpUrl
from typing import List, Optional, Dict, Any, Union, Generic, TypeVar
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
from uuid import UUID

# =============================================================================
# ENUMS
# =============================================================================

class UserRole(str, Enum):
    """Foydalanuvchi rollari"""
    ADMIN = "admin"
    TRADER = "trader"
    ANALYST = "analyst"
    VIEWER = "viewer"

class SignalType(str, Enum):
    """Signal turlari"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

class QuantumState(str, Enum):
    """Quantum holat turlari"""
    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"
    COHERENT = "coherent"
    DECOHERENT = "decoherent"

class DAOProposalStatus(str, Enum):
    """DAO taklif holatlari"""
    PENDING = "pending"
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"

class NFTCollectionType(str, Enum):
    """NFT kolleksiya turlari"""
    ART = "art"
    GAMING = "gaming"
    MUSIC = "music"
    SPORTS = "sports"
    UTILITY = "utility"

class TradeStatus(str, Enum):
    """Trading holatlar"""
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    FAILED = "failed"

# =============================================================================
# BASE MODELS
# =============================================================================

class BaseResponse(BaseModel):
    """Barcha API javoblari uchun asosiy model"""
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None

class PaginationInfo(BaseModel):
    """Sahifalash ma'lumotlari"""
    page: int = Field(ge=1)
    size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    pages: int = Field(ge=0)

# =============================================================================
# AUTHENTICATION MODELS
# =============================================================================

class UserBase(BaseModel):
    """Foydalanuvchi asosiy ma'lumotlari"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.VIEWER

class UserLogin(BaseModel):
    """Foydalanuvchi login uchun"""
    username: str
    password: str

class UserCreate(UserBase):
    """Yangi foydalanuvchi yaratish"""
    password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Parollar mos kelmaydi')
        return v

class UserUpdate(BaseModel):
    """Foydalanuvchi ma'lumotlarini yangilash"""
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    """Foydalanuvchi to'liq ma'lumotlari"""
    id: UUID
    password: str  # Hashed password
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    """Foydalanuvchi javob modeli"""
    id: UUID
    is_active: bool = True
    created_at: datetime

class LoginRequest(BaseModel):
    """Login so'rovi"""
    username: str
    password: str

class TokenResponse(BaseResponse):
    """Token javob modeli"""
    access_token: str
    token_type: str
    expires_in: int
    user_info: UserResponse

# =============================================================================
# AI SIGNALS MODELS
# =============================================================================

class AISignal(BaseModel):
    """AI Signal ma'lumotlari"""
    id: UUID
    symbol: str
    signal_type: SignalType
    confidence: float = Field(ge=0, le=1)
    price: Decimal
    target_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    timeframe: str
    model_version: str
    features: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None

class AISignalCreate(BaseModel):
    """AI Signal yaratish so'rovi"""
    symbol: str
    signal_type: SignalType
    confidence: float = Field(ge=0, le=1)
    price: Decimal
    target_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    timeframe: str

class AISignalResponse(BaseResponse):
    """AI Signal javob modeli"""
    signal: AISignal

class AISignalListResponse(BaseResponse):
    """AI Signal ro'yxati javob modeli"""
    signals: List[AISignal]
    pagination: PaginationInfo

class BulkAISignalsRequest(BaseModel):
    """Ko'plab AI Signals so'rovi"""
    symbols: List[str]
    timeframes: List[str] = ["1h", "4h", "1d"]
    include_predictions: bool = True

# =============================================================================
# QUANTUM ANALYSIS MODELS
# =============================================================================

class QuantumAnalysis(BaseModel):
    """Quantum Analysis ma'lumotlari"""
    id: UUID
    symbol: str
    quantum_state: QuantumState
    coherence_time: float  # microseconds
    fidelity: float = Field(ge=0, le=1)
    entanglement_strength: float = Field(ge=0, le=1)
    qbit_count: int
    superposition_probability: float = Field(ge=0, le=1)
    market_prediction: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    created_at: datetime

class QuantumAnalysisCreate(BaseModel):
    """Quantum Analysis yaratish so'rovi"""
    symbol: str
    quantum_state: QuantumState
    qbit_count: int

class QuantumAnalysisResponse(BaseResponse):
    """Quantum Analysis javob modeli"""
    analysis: QuantumAnalysis

class QuantumAnalysisListResponse(BaseResponse):
    """Quantum Analysis ro'yxati javob modeli"""
    analyses: List[QuantumAnalysis]
    pagination: PaginationInfo

class QuantumParameters(BaseModel):
    """Quantum parametrlari"""
    coherence_threshold: float = 0.95
    entanglement_threshold: float = 0.80
    min_qbits: int = 64
    max_qbits: int = 512

# =============================================================================
# BLOCKCHAIN MODELS
# =============================================================================

class BlockchainTransaction(BaseModel):
    """Blockchain tranzaksiya ma'lumotlari"""
    id: UUID
    transaction_hash: str
    block_number: int
    from_address: str
    to_address: str
    value: Decimal
    gas_used: int
    gas_price: Decimal
    status: str
    created_at: datetime

class BlockchainTransactionCreate(BaseModel):
    """Blockchain tranzaksiya yaratish so'rovi"""
    to_address: str
    value: Decimal
    gas_price: Optional[Decimal] = None

class BlockchainResponse(BaseResponse):
    """Blockchain javob modeli"""
    transaction: BlockchainTransaction

class BlockchainListResponse(BaseResponse):
    """Blockchain tranzaksiyalar ro'yxati"""
    transactions: List[BlockchainTransaction]
    pagination: PaginationInfo

class WalletBalance(BaseModel):
    """Hamyon balansi"""
    address: str
    balance: Decimal
    currency: str
    last_updated: datetime

# =============================================================================
# DAO GOVERNANCE MODELS
# =============================================================================

class DAOProposal(BaseModel):
    """DAO taklif ma'lumotlari"""
    id: UUID
    title: str
    description: str
    proposer_address: str
    proposal_type: str
    status: DAOProposalStatus
    voting_deadline: datetime
    votes_for: int = 0
    votes_against: int = 0
    votes_abstain: int = 0
    created_at: datetime

class DAOProposalCreate(BaseModel):
    """DAO taklif yaratish so'rovi"""
    title: str
    description: str
    proposal_type: str
    voting_deadline: datetime

class DAOProposalResponse(BaseResponse):
    """DAO taklif javob modeli"""
    proposal: DAOProposal

class DAOProposalListResponse(BaseResponse):
    """DAO takliflar ro'yxati javob modeli"""
    proposals: List[DAOProposal]
    pagination: PaginationInfo

class VoteRequest(BaseModel):
    """Ovoz berish so'rovi"""
    proposal_id: UUID
    vote: str  # "for", "against", "abstain"

# =============================================================================
# HFT ENGINE MODELS
# =============================================================================

class HFTTrade(BaseModel):
    """HFT Trading operatsiya"""
    id: UUID
    symbol: str
    side: str  # "buy", "sell"
    quantity: Decimal
    price: Decimal
    execution_time: float  # milliseconds
    latency: float  # microseconds
    profit_loss: Optional[Decimal] = None
    status: TradeStatus
    created_at: datetime

class HFTTradeCreate(BaseModel):
    """HFT Trading yaratish so'rovi"""
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal

class HFTTradeResponse(BaseResponse):
    """HFT Trading javob modeli"""
    trade: HFTTrade

class HFTTradeListResponse(BaseResponse):
    """HFT Trading ro'yxati javob modeli"""
    trades: List[HFTTrade]
    pagination: PaginationInfo

class HFTMetrics(BaseModel):
    """HFT metrikalar"""
    total_trades: int
    successful_trades: int
    failed_trades: int
    average_latency: float  # microseconds
    max_latency: float
    min_latency: float
    profit_loss: Decimal
    sharpe_ratio: float
    win_rate: float

# =============================================================================
# NFT HEDGE FUND MODELS
# =============================================================================

class NFTCollection(BaseModel):
    """NFT kolleksiya ma'lumotlari"""
    id: UUID
    name: str
    collection_type: NFTCollectionType
    floor_price: Decimal
    volume_24h: Decimal
    total_supply: int
    market_cap: Optional[Decimal] = None
    rarity_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class NFTCollectionCreate(BaseModel):
    """NFT kolleksiya yaratish so'rovi"""
    name: str
    collection_type: NFTCollectionType
    floor_price: Decimal

class NFTCollectionResponse(BaseResponse):
    """NFT kolleksiya javob modeli"""
    collection: NFTCollection

class NFTCollectionListResponse(BaseResponse):
    """NFT kolleksiyalar ro'yxati javob modeli"""
    collections: List[NFTCollection]
    pagination: PaginationInfo

class NFTHedgePosition(BaseModel):
    """NFT Hedge pozitsiya"""
    id: UUID
    collection_id: UUID
    token_id: str
    purchase_price: Decimal
    current_value: Decimal
    pnl: Decimal
    risk_score: float
    created_at: datetime

# =============================================================================
# SELF-LEARNING MODELS
# =============================================================================

class SelfLearningModel(BaseModel):
    """Self-Learning model ma'lumotlari"""
    id: UUID
    name: str
    model_type: str
    version: str
    accuracy: float
    training_data_size: int
    last_trained: datetime
    performance_metrics: Dict[str, float]
    is_active: bool = True

class SelfLearningModelCreate(BaseModel):
    """Self-Learning model yaratish so'rovi"""
    name: str
    model_type: str
    training_data: List[Dict[str, Any]]

class SelfLearningModelResponse(BaseResponse):
    """Self-Learning model javob modeli"""
    model: SelfLearningModel

class ModelPrediction(BaseModel):
    """Model bashorat ma'lumotlari"""
    model_id: UUID
    input_data: Dict[str, Any]
    prediction: Any
    confidence: float
    created_at: datetime

class TrainingJob(BaseModel):
    """Model trening vazifasi"""
    id: UUID
    model_id: UUID
    status: str  # "pending", "training", "completed", "failed"
    progress: int = 0  # 0-100
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

# =============================================================================
# FILE OPERATIONS MODELS
# =============================================================================

class FileInfo(BaseModel):
    """Fayl ma'lumotlari"""
    id: UUID
    filename: str
    file_size: int
    content_type: str
    uploaded_at: datetime
    uploaded_by: UUID

class FileUploadResponse(BaseResponse):
    """Fayl yuklash javob modeli"""
    filename: str
    file_size: int
    content_type: str
    upload_path: str
    upload_time: datetime

class FileListResponse(BaseResponse):
    """Fayllar ro'yxati javob modeli"""
    files: List[FileInfo]
    total: int
    page: int
    size: int
    pages: int

# =============================================================================
# BULK OPERATIONS MODELS
# =============================================================================

class BulkOperationResponse(BaseResponse):
    """Bulk operatsiya javob modeli"""
    operation_id: str
    status: str
    total_requests: int
    processed: int
    estimated_completion: datetime

class BulkStatusResponse(BaseResponse):
    """Bulk operatsiya holati javob modeli"""
    operation_id: str
    status: str
    progress: int
    completed_items: int
    failed_items: int
    started_at: datetime
    completed_at: Optional[datetime] = None

# =============================================================================
# SYSTEM MODELS
# =============================================================================

class HealthResponse(BaseResponse):
    """Sog'liq tekshirish javob modeli"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]

class SystemStatusResponse(BaseResponse):
    """Tizim holati javob modeli"""
    uptime: str
    cpu_usage: float
    memory_usage: float
    active_connections: int
    api_calls_today: int
    system_load: str

# =============================================================================
# WEBSOCKET MODELS
# =============================================================================

class WebSocketMessage(BaseModel):
    """WebSocket xabar modeli"""
    type: str
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[UUID] = None

class WebSocketConnection(BaseModel):
    """WebSocket ulanish modeli"""
    websocket_id: UUID
    user_id: Optional[UUID] = None
    connection_type: str  # "trading", "quantum", "blockchain"
    connected_at: datetime
    last_activity: datetime

# =============================================================================
# PAGINATION AND FILTERING MODELS
# =============================================================================

class PaginationParams(BaseModel):
    """Sahifalash parametrlari"""
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")

class FilterParams(BaseModel):
    """Filtrlash parametrlari"""
    symbol: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[str] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None