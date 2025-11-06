"""
AI Trading System - NFT Hedge Fund Endpoints
NFT hedge fund operatsiyalari uchun RESTful API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import asyncio
import numpy as np
from decimal import Decimal

from ..models.schemas import *
from ..auth.auth_handler import get_current_active_user
from ..utils.cache import cache_manager

router = APIRouter()

# NFT data storage
collections_db: Dict[str, Any] = {}
nft_positions_db: Dict[str, Any] = {}
hedge_strategies_db: Dict[str, Any] = {}
nft_trades_db: Dict[str, Any] = {}

# NFT Market data
market_data = {
    "total_market_cap": "2.4B",
    "daily_volume": "145M",
    "floor_price_avg": "2.15 ETH",
    "total_collections": 15420,
    "active_traders": 23450,
    "average_price_change_24h": "-3.2%"
}

# Portfolio allocation
portfolio_allocation = {
    "gaming": 35.2,
    "art": 28.7,
    "utility": 18.3,
    "music": 9.8,
    "sports": 8.0
}

# =============================================================================
# NFT COLLECTIONS
# =============================================================================

@router.get("/collections", response_model=NFTCollectionListResponse)
async def get_nft_collections(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    collection_type: Optional[NFTCollectionType] = Query(None),
    min_floor_price: Optional[Decimal] = Query(None),
    sort_by: str = Query("market_cap", description="Sort by: market_cap, volume, floor_price"),
    current_user: User = Depends(get_current_active_user)
):
    """NFT kolleksiyalar ro'yxati"""
    
    # Filter collections
    filtered_collections = []
    for collection_id, collection in collections_db.items():
        if collection_type and collection.collection_type != collection_type:
            continue
        if min_floor_price and collection.floor_price < min_floor_price:
            continue
        filtered_collections.append(collection)
    
    # Sort collections
    if sort_by == "market_cap":
        filtered_collections.sort(key=lambda x: x.market_cap or Decimal("0"), reverse=True)
    elif sort_by == "volume":
        filtered_collections.sort(key=lambda x: x.volume_24h, reverse=True)
    elif sort_by == "floor_price":
        filtered_collections.sort(key=lambda x: x.floor_price, reverse=True)
    
    # Paginate
    total = len(filtered_collections)
    start = (page - 1) * size
    end = start + size
    paginated_collections = filtered_collections[start:end]
    
    return NFTCollectionListResponse(
        collections=paginated_collections,
        pagination=PaginationInfo(
            page=page,
            size=size,
            total=total,
            pages=(total + size - 1) // size
        )
    )

@router.post("/collections", response_model=NFTCollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_nft_collection(
    collection_data: NFTCollectionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Yangi NFT kolleksiya yaratish"""
    
    collection_id = str(uuid.uuid4())
    
    # Create collection
    collection = NFTCollection(
        id=collection_id,
        name=collection_data.name,
        collection_type=collection_data.collection_type,
        floor_price=collection_data.floor_price,
        volume_24h=Decimal(str(np.random.uniform(10, 500))),
        total_supply=1000 + int(np.random.uniform(100, 10000)),
        market_cap=collection_data.floor_price * 1000,  # Mock calculation
        rarity_score=np.random.uniform(0.7, 0.95),
        metadata={
            "creator": f"0x{uuid.uuid4().hex[:40]}",
            "description": f"Premium {collection_data.collection_type.value} collection",
            "royalty_fee": "5%",
            "blockchain": "Ethereum"
        },
        created_at=datetime.utcnow()
    )
    
    # Store collection
    collections_db[collection_id] = collection
    
    # Background task to fetch real market data
    background_tasks.add_task(fetch_collection_market_data, collection_id)
    
    return NFTCollectionResponse(
        collection=collection,
        message="NFT kolleksiya muvaffaqiyatli yaratildi"
    )

@router.get("/collections/{collection_id}", response_model=Dict[str, Any])
async def get_collection_details(
    collection_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """NFT kolleksiya tafsilotlari"""
    
    if collection_id not in collections_db:
        raise HTTPException(
            status_code=404,
            detail="NFT kolleksiya topilmadi"
        )
    
    collection = collections_db[collection_id]
    
    # Mock additional collection data
    return {
        "collection": collection,
        "market_analytics": {
            "floor_price_change_24h": np.random.uniform(-10, 10),
            "volume_change_24h": np.random.uniform(-20, 30),
            "holder_count": np.random.randint(500, 5000),
            "listed_items": np.random.randint(50, 500),
            "average_sale_price": collection.floor_price * Decimal(str(np.random.uniform(1.1, 2.5))),
            "total_sales_24h": np.random.randint(10, 100)
        },
        "rarity_distribution": {
            "common": "65.2%",
            "uncommon": "25.8%",
            "rare": "7.5%",
            "epic": "1.2%",
            "legendary": "0.3%"
        },
        "price_history": [
            {
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "floor_price": float(collection.floor_price) * (1 + np.random.uniform(-0.05, 0.05))
            }
            for i in range(24)  # 24 hours of data
        ],
        "top_holders": [
            {
                "address": f"0x{i:040x}",
                "holdings": np.random.randint(1, 20),
                "percentage": round(np.random.uniform(0.5, 5.0), 2)
            }
            for i in range(10)
        ]
    }

@router.get("/collections/{collection_id}/floor-price", response_model=Dict[str, Any])
async def get_collection_floor_price(
    collection_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Kolleksiya floor price tarixi"""
    
    if collection_id not in collections_db:
        raise HTTPException(
            status_code=404,
            detail="NFT kolleksiya topilmadi"
        )
    
    collection = collections_db[collection_id]
    
    # Generate floor price history
    base_price = float(collection.floor_price)
    price_history = []
    
    for i in range(30):  # 30 days
        date = datetime.utcnow() - timedelta(days=i)
        price_variation = np.random.uniform(-0.15, 0.20)
        price = base_price * (1 + price_variation)
        
        price_history.append({
            "date": date.strftime("%Y-%m-%d"),
            "floor_price": round(price, 4),
            "volume": np.random.randint(5, 50),
            "sales": np.random.randint(1, 15)
        })
    
    return {
        "collection_id": collection_id,
        "collection_name": collection.name,
        "current_floor_price": float(collection.floor_price),
        "price_change_24h": np.random.uniform(-5, 8),
        "price_change_7d": np.random.uniform(-15, 20),
        "price_history": price_history,
        "price_predictions": {
            "1d": round(base_price * np.random.uniform(0.95, 1.05), 4),
            "7d": round(base_price * np.random.uniform(0.90, 1.10), 4),
            "30d": round(base_price * np.random.uniform(0.85, 1.15), 4)
        }
    }

# =============================================================================
# NFT HEDGE POSITIONS
# =============================================================================

@router.get("/positions", response_model=Dict[str, Any])
async def get_nft_positions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    collection_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="Position status: active, closed, hedged"),
    current_user: User = Depends(get_current_active_user)
):
    """NFT hedge pozitsiyalar ro'yxati"""
    
    # Filter positions
    filtered_positions = []
    for position_id, position in nft_positions_db.items():
        if collection_id and position.collection_id != collection_id:
            continue
        if status and position.get("status") != status:
            continue
        filtered_positions.append(position)
    
    # Sort by created_at descending
    filtered_positions.sort(key=lambda x: x.created_at, reverse=True)
    
    # Calculate portfolio metrics
    total_value = sum(position.current_value for position in filtered_positions)
    total_pnl = sum(position.pnl for position in filtered_positions)
    total_risk_score = np.mean([position.risk_score for position in filtered_positions])
    
    return {
        "positions": filtered_positions,
        "total": len(filtered_positions),
        "pagination": {
            "page": page,
            "size": size,
            "pages": (len(filtered_positions) + size - 1) // size
        },
        "portfolio_metrics": {
            "total_value": str(total_value),
            "total_pnl": str(total_pnl),
            "pnl_percentage": round((total_pnl / total_value) * 100 if total_value > 0 else 0, 2),
            "average_risk_score": round(total_risk_score, 3),
            "best_performer": max(filtered_positions, key=lambda x: x.pnl).token_id if filtered_positions else None,
            "worst_performer": min(filtered_positions, key=lambda x: x.pnl).token_id if filtered_positions else None
        }
    }

@router.post("/positions", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_nft_position(
    position_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Yangi NFT hedge pozitsiya yaratish"""
    
    # Validate collection exists
    if position_data["collection_id"] not in collections_db:
        raise HTTPException(
            status_code=404,
            detail="NFT kolleksiya topilmadi"
        )
    
    collection = collections_db[position_data["collection_id"]]
    
    position_id = str(uuid.uuid4())
    
    # Create position
    position = NFTHedgePosition(
        id=position_id,
        collection_id=position_data["collection_id"],
        token_id=position_data["token_id"],
        purchase_price=Decimal(str(position_data["purchase_price"])),
        current_value=Decimal(str(position_data["purchase_price"])) * Decimal(str(1.1)),  # Mock current value
        pnl=Decimal(str(position_data["purchase_price"])) * Decimal("0.1"),  # Mock 10% gain
        risk_score=np.random.uniform(0.3, 0.9),
        created_at=datetime.utcnow()
    )
    
    # Store position
    nft_positions_db[position_id] = position
    
    # Calculate hedge strategy
    hedge_strategy = calculate_hedge_strategy(position)
    
    return {
        "position": position,
        "hedge_strategy": hedge_strategy,
        "risk_assessment": {
            "volatility_score": np.random.uniform(0.4, 0.8),
            "liquidity_score": np.random.uniform(0.6, 0.95),
            "market_impact": "LOW" if position.risk_score < 0.6 else "MEDIUM",
            "recommendation": "HOLD" if position.risk_score < 0.7 else "CONSIDER_HEDGE"
        },
        "message": "NFT hedge pozitsiya muvaffaqiyatli yaratildi"
    }

@router.get("/positions/{position_id}/hedge-recommendation", response_model=Dict[str, Any])
async def get_hedge_recommendation(
    position_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Hedge tavsiyasini olish"""
    
    if position_id not in nft_positions_db:
        raise HTTPException(
            status_code=404,
            detail="NFT pozitsiya topilmadi"
        )
    
    position = nft_positions_db[position_id]
    collection = collections_db.get(position.collection_id)
    
    hedge_strategy = calculate_hedge_strategy(position)
    
    return {
        "position_id": position_id,
        "current_position": {
            "token_id": position.token_id,
            "purchase_price": str(position.purchase_price),
            "current_value": str(position.current_value),
            "unrealized_pnl": str(position.pnl),
            "pnl_percentage": round(float(position.pnl / position.purchase_price) * 100, 2)
        },
        "hedge_recommendations": {
            "primary_strategy": hedge_strategy["primary"],
            "hedge_ratio": hedge_strategy["hedge_ratio"],
            "recommended_actions": hedge_strategy["actions"],
            "expected_risk_reduction": f"{hedge_strategy['risk_reduction']}%",
            "estimated_cost": f"{hedge_strategy['estimated_cost']} ETH"
        },
        "market_analysis": {
            "collection_trend": "bullish" if position.pnl > 0 else "bearish",
            "market_sentiment": np.random.choice(["positive", "neutral", "negative"]),
            "liquidity_assessment": "high" if collection and collection.floor_price > Decimal("1") else "medium",
            "volatility_outlook": "stable" if position.risk_score < 0.5 else "volatile"
        },
        "alternative_strategies": [
            {
                "strategy": "Opensea Short",
                "description": "Short the collection floor price",
                "risk_level": "MEDIUM",
                "cost": "2.5 ETH"
            },
            {
                "strategy": "Floor Derivatives",
                "description": "Use floor price derivatives",
                "risk_level": "LOW",
                "cost": "1.2 ETH"
            }
        ]
    }

# =============================================================================
# HEDGE STRATEGIES
# =============================================================================

@router.get("/strategies", response_model=Dict[str, Any])
async def get_hedge_strategies(
    strategy_type: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None, description="Risk level: low, medium, high"),
    current_user: User = Depends(get_current_active_user)
):
    """Hedge strategialari ro'yxati"""
    
    # Filter strategies
    filtered_strategies = []
    for strategy_id, strategy in hedge_strategies_db.items():
        if strategy_type and strategy.get("type") != strategy_type:
            continue
        if risk_level and strategy.get("risk_level") != risk_level:
            continue
        filtered_strategies.append(strategy)
    
    return {
        "strategies": filtered_strategies,
        "total": len(filtered_strategies),
        "strategy_types": {
            "floor_hedging": 4,
            "index_hedging": 3,
            "derivative_hedging": 2,
            "pairs_trading": 2
        }
    }

@router.post("/strategies/execute", response_model=Dict[str, Any])
async def execute_hedge_strategy(
    strategy_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Hedge strategiya bajarish"""
    
    strategy_id = str(uuid.uuid4())
    
    # Mock execution
    execution_result = {
        "strategy_id": strategy_id,
        "status": "executing",
        "strategy_type": strategy_data.get("type"),
        "execution_details": {
            "estimated_duration": "5-15 minutes",
            "expected_cost": f"{np.random.uniform(1.0, 5.0):.2f} ETH",
            "hedge_ratio": np.random.uniform(0.5, 0.9),
            "risk_reduction": f"{np.random.uniform(20, 60):.1f}%"
        },
        "positions_opened": [
            {
                "position_type": "long",
                "symbol": f"COLLECTION_{strategy_data.get('collection_id', 'ABC')}_FLOOR",
                "size": np.random.uniform(0.1, 2.0),
                "entry_price": np.random.uniform(1.5, 3.0)
            }
        ],
        "started_at": datetime.utcnow().isoformat()
    }
    
    # Store execution result
    hedge_strategies_db[strategy_id] = execution_result
    
    return execution_result

# =============================================================================
# MARKET ANALYSIS
# =============================================================================

@router.get("/market/overview", response_model=Dict[str, Any])
async def get_nft_market_overview(current_user: User = Depends(get_current_active_user)):
    """NFT bozor umumiy ko'rinish"""
    
    return {
        "market_summary": {
            "total_market_cap": market_data["total_market_cap"],
            "daily_volume": market_data["daily_volume"],
            "floor_price_average": market_data["floor_price_avg"],
            "total_collections": market_data["total_collections"],
            "active_traders": market_data["active_traders"],
            "price_change_24h": market_data["average_price_change_24h"]
        },
        "top_collections": [
            {
                "name": "CryptoPunks",
                "floor_price": "67.5 ETH",
                "market_cap": "246M",
                "volume_24h": "1.2M",
                "change_24h": "+5.2%"
            },
            {
                "name": "Bored Ape Yacht Club",
                "floor_price": "45.8 ETH",
                "market_cap": "189M",
                "volume_24h": "856K",
                "change_24h": "-2.1%"
            },
            {
                "name": "Azuki",
                "floor_price": "12.3 ETH",
                "market_cap": "78M",
                "volume_24h": "432K",
                "change_24h": "+8.7%"
            }
        ],
        "category_performance": {
            "gaming": {"change_24h": "+12.3%", "volume": "45M"},
            "art": {"change_24h": "-3.1%", "volume": "38M"},
            "utility": {"change_24h": "+7.8%", "volume": "28M"},
            "music": {"change_24h": "+15.2%", "volume": "15M"},
            "sports": {"change_24h": "-1.5%", "volume": "19M"}
        },
        "portfolio_allocation": portfolio_allocation,
        "market_trends": {
            "emerging_trends": ["AI-generated art", "Utility NFTs", "Gaming assets"],
            "declining_trends": ["Purely speculative", "Low utility"],
            "institutional_interest": "increasing"
        }
    }

@router.get("/market/trends", response_model=Dict[str, Any])
async def get_market_trends(
    time_period: str = Query("7d", description="Time period: 1d, 7d, 30d"),
    category: Optional[NFTCollectionType] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """NFT bozor trendlari tahlili"""
    
    # Mock trend analysis
    return {
        "analysis_period": time_period,
        "category_filter": category.value if category else "all",
        "trend_analysis": {
            "overall_trend": np.random.choice(["bullish", "bearish", "sideways"]),
            "confidence_score": np.random.uniform(0.6, 0.9),
            "key_factors": [
                "Institutional adoption",
                "Regulatory clarity",
                "Utility development",
                "Market maturity"
            ]
        },
        "price_trends": {
            "floor_price_trend": "increasing",
            "volume_trend": "stable",
            "new_listings_trend": "decreasing",
            "average_sale_time": "2.3 days"
        },
        "market_sentiment": {
            "social_sentiment": 0.67,
            "trading_activity": "moderate",
            "whale_activity": "high",
            "retail_participation": "low"
        },
        "predictive_indicators": {
            "technical_score": np.random.uniform(0.5, 0.8),
            "fundamental_score": np.random.uniform(0.6, 0.9),
            "sentiment_score": np.random.uniform(0.4, 0.7),
            "overall_score": np.random.uniform(0.55, 0.8)
        },
        "recommendations": {
            "short_term": "monitor_floor_prices",
            "medium_term": "consider_portfolio_diversification",
            "long_term": "focus_on_utility_nfts"
        }
    }

@router.get("/market/scan", response_model=Dict[str, Any])
async def scan_market_opportunities(
    min_potential: float = Query(0.1, description="Minimum potential return"),
    max_risk: float = Query(0.3, description="Maximum risk score"),
    current_user: User = Depends(get_current_active_user)
):
    """Bozor imkoniyatlarini skanerlash"""
    
    opportunities = []
    
    for i, collection in enumerate(list(collections_db.values())[:10]):
        potential_return = np.random.uniform(0.05, 0.5)
        risk_score = np.random.uniform(0.2, 0.8)
        
        if potential_return >= min_potential and risk_score <= max_risk:
            opportunities.append({
                "collection_id": collection.id,
                "collection_name": collection.name,
                "current_floor_price": str(collection.floor_price),
                "potential_return": f"{potential_return * 100:.1f}%",
                "risk_score": round(risk_score, 3),
                "confidence": np.random.uniform(0.6, 0.9),
                "time_horizon": np.random.choice(["1-7 days", "1-4 weeks", "1-3 months"]),
                "key_metrics": {
                    "liquidity": np.random.choice(["high", "medium", "low"]),
                    "volume_24h": str(collection.volume_24h),
                    "holder_count": np.random.randint(200, 2000)
                },
                "action_recommendation": np.random.choice(["BUY", "MONITOR", "RESEARCH"])
            })
    
    return {
        "scan_timestamp": datetime.utcnow().isoformat(),
        "opportunities_found": len(opportunities),
        "filters_applied": {
            "min_potential_return": f"{min_potential * 100}%",
            "max_risk_score": max_risk,
            "category_filter": "all"
        },
        "opportunities": opportunities,
        "market_summary": {
            "total_opportunities": len(opportunities),
            "average_potential": f"{np.mean([float(op['potential_return'].rstrip('%')) for op in opportunities]):.1f}%" if opportunities else "0%",
            "highest_potential": opportunities[0]["potential_return"] if opportunities else "N/A",
            "best_risk_reward": "collection_with_highest_ratio" if opportunities else None
        }
    }

# =============================================================================
# NFT TRADES
# =============================================================================

@router.get("/trades", response_model=Dict[str, Any])
async def get_nft_trades(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    trade_type: Optional[str] = Query(None, description="Trade type: buy, sell, hedge"),
    collection_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """NFT trade operatsiyalari"""
    
    # Filter trades
    filtered_trades = []
    for trade_id, trade in nft_trades_db.items():
        if trade_type and trade.get("type") != trade_type:
            continue
        if collection_id and trade.get("collection_id") != collection_id:
            continue
        filtered_trades.append(trade)
    
    # Mock trade data enhancement
    enhanced_trades = []
    for trade in filtered_trades[start:start+size]:
        enhanced_trade = trade.copy()
        enhanced_trade.update({
            "execution_quality": np.random.choice(["excellent", "good", "fair"]),
            "gas_cost": f"{np.random.uniform(0.01, 0.05):.3f} ETH",
            "market_impact": np.random.choice(["minimal", "low", "medium"]),
            "profit_loss": Decimal(str(np.random.uniform(-0.5, 2.0)))
        })
        enhanced_trades.append(enhanced_trade)
    
    return {
        "trades": enhanced_trades,
        "total": len(filtered_trades),
        "page": page,
        "size": size,
        "pages": (len(filtered_trades) + size - 1) // size,
        "trade_statistics": {
            "total_volume": "234.5 ETH",
            "total_trades": len(filtered_trades),
            "win_rate": "68.2%",
            "average_profit": "15.7%",
            "total_profit": "45.2 ETH"
        }
    }

# =============================================================================
# BACKGROUND TASKS & UTILITIES
# =============================================================================

async def fetch_collection_market_data(collection_id: str):
    """Kolleksiya market data olish"""
    try:
        logger.info(f"NFT kolleksiya market data olinmoqda: {collection_id}")
        
        # Simulate API call to NFT marketplace
        await asyncio.sleep(np.random.uniform(1, 3))
        
        if collection_id in collections_db:
            collection = collections_db[collection_id]
            
            # Update with real market data
            collection.volume_24h *= Decimal(str(np.random.uniform(0.8, 1.2)))
            collection.floor_price *= Decimal(str(np.random.uniform(0.95, 1.05)))
            
            logger.info(f"NFT kolleksiya market data yangilandi: {collection_id}")
        
    except Exception as e:
        logger.error(f"Market data olish xatosi: {e}")

def calculate_hedge_strategy(position: NFTHedgePosition) -> Dict[str, Any]:
    """Hedge strategiya hisoblash"""
    
    risk_score = position.risk_score
    
    if risk_score < 0.4:
        strategy = "PASSIVE_MONITORING"
        hedge_ratio = 0.0
        actions = ["Continue monitoring", "Set price alerts"]
        risk_reduction = 0
        estimated_cost = 0.0
    elif risk_score < 0.7:
        strategy = "PARTIAL_HEDGE"
        hedge_ratio = 0.3 + (risk_score - 0.4) * 2.33  # Scale between 0.3-1.0
        actions = ["Reduce position size", "Consider floor short"]
        risk_reduction = hedge_ratio * 100
        estimated_cost = hedge_ratio * 2.5
    else:
        strategy = "FULL_HEDGE"
        hedge_ratio = 1.0
        actions = ["Full hedge recommended", "Consider derivatives", "Portfolio rebalancing"]
        risk_reduction = 75
        estimated_cost = 5.0
    
    return {
        "primary": strategy,
        "hedge_ratio": round(hedge_ratio, 2),
        "actions": actions,
        "risk_reduction": risk_reduction,
        "estimated_cost": round(estimated_cost, 2),
        "recommendation": "STRONG_BUY" if risk_score > 0.8 else "BUY" if risk_score > 0.6 else "HOLD"
    }

# Initialize mock data
def init_mock_nft_data():
    """Mock NFT ma'lumotlarini yaratish"""
    if not collections_db:
        collection_types = list(NFTCollectionType)
        collection_names = [
            "Cyber Cats", "Digital Dreams", "Crypto Warriors", "Pixel Punks",
            "Virtual Lands", "AI Avatars", "Space Explorers", "Mystic Creatures",
            "Retro Games", "Future Tech", "Musical Beats", "Sport Legends"
        ]
        
        for i, name in enumerate(collection_names):
            collection_id = str(uuid.uuid4())
            
            collection = NFTCollection(
                id=collection_id,
                name=name,
                collection_type=collection_types[i % len(collection_types)],
                floor_price=Decimal(str(np.random.uniform(0.5, 10.0))),
                volume_24h=Decimal(str(np.random.uniform(50, 500))),
                total_supply=1000 + int(np.random.uniform(100, 10000)),
                market_cap=Decimal(str(np.random.uniform(100000, 10000000))),
                rarity_score=np.random.uniform(0.6, 0.95),
                metadata={
                    "creator": f"0x{uuid.uuid4().hex[:40]}",
                    "description": f"Premium {collection_types[i % len(collection_types)].value} NFT collection",
                    "royalty_fee": f"{np.random.choice(['2.5%', '5%', '7.5%'])}",
                    "blockchain": np.random.choice(["Ethereum", "Polygon", "Arbitrum"])
                },
                created_at=datetime.utcnow() - timedelta(days=i * 7)
            )
            
            collections_db[collection_id] = collection
        
        # Create mock hedge positions
        for i in range(30):
            position_id = str(uuid.uuid4())
            collection_list = list(collections_db.keys())
            
            position = NFTHedgePosition(
                id=position_id,
                collection_id=collection_list[i % len(collection_list)],
                token_id=f"#{i:04d}",
                purchase_price=Decimal(str(np.random.uniform(1.0, 5.0))),
                current_value=Decimal(str(np.random.uniform(0.8, 6.0))),
                pnl=Decimal(str(np.random.uniform(-1.0, 2.0))),
                risk_score=np.random.uniform(0.3, 0.9),
                created_at=datetime.utcnow() - timedelta(hours=i * 6)
            )
            
            nft_positions_db[position_id] = position
        
        # Create mock NFT trades
        for i in range(50):
            trade_id = str(uuid.uuid4())
            collection_list = list(collections_db.keys())
            
            nft_trades_db[trade_id] = {
                "id": trade_id,
                "type": np.random.choice(["buy", "sell", "hedge"]),
                "collection_id": collection_list[i % len(collection_list)],
                "token_id": f"#{i:04d}",
                "price": np.random.uniform(1.0, 8.0),
                "quantity": 1,
                "timestamp": datetime.utcnow() - timedelta(hours=i * 3),
                "status": np.random.choice(["completed", "pending", "failed"]),
                "transaction_hash": f"0x{uuid.uuid4().hex}"
            }

# Initialize mock data on module load
import logging
logger = logging.getLogger(__name__)
init_mock_nft_data()