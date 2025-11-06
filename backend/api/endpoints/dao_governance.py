"""
AI Trading System - DAO Governance Endpoints
DAO boshqaruvi uchun RESTful API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import asyncio

from ..models.schemas import *
from ..auth.auth_handler import get_current_active_user
from ..utils.cache import cache_manager

router = APIRouter()

# DAO data storage
proposals_db: Dict[str, Any] = {}
votes_db: Dict[str, Any] = {}
members_db: Dict[str, Any] = {}
treasury_db: Dict[str, Any] = {}

# DAO settings
dao_settings = {
    "governance_token": "AITF",
    "proposal_threshold": Decimal("10000"),  # Minimum tokens to create proposal
    "voting_period": timedelta(days=7),
    "execution_delay": timedelta(days=2),
    "quorum": Decimal("0.1"),  # 10% of total supply
    "pass_threshold": Decimal("0.51")  # 51% majority required
}

# Mock treasury balance
treasury_balance = {
    "AITF": Decimal("500000"),
    "ETH": Decimal("100.5"),
    "USDT": Decimal("250000"),
    "BTC": Decimal("10.25")
}

# =============================================================================
# DAO PROPOSALS
# =============================================================================

@router.get("/proposals", response_model=DAOProposalListResponse)
async def get_proposals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[DAOProposalStatus] = Query(None),
    proposer: Optional[str] = Query(None),
    proposal_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """DAO takliflari ro'yxati"""
    
    # Filter proposals
    filtered_proposals = []
    for proposal_id, proposal in proposals_db.items():
        if status and proposal.status != status:
            continue
        if proposer and proposal.proposer_address != proposer:
            continue
        if proposal_type and proposal.proposal_type != proposal_type:
            continue
        filtered_proposals.append(proposal)
    
    # Sort by created_at descending
    filtered_proposals.sort(key=lambda x: x.created_at, reverse=True)
    
    # Paginate
    total = len(filtered_proposals)
    start = (page - 1) * size
    end = start + size
    paginated_proposals = filtered_proposals[start:end]
    
    return DAOProposalListResponse(
        proposals=paginated_proposals,
        pagination=PaginationInfo(
            page=page,
            size=size,
            total=total,
            pages=(total + size - 1) // size
        )
    )

@router.post("/proposals", response_model=DAOProposalResponse, status_code=status.HTTP_201_CREATED)
async def create_proposal(
    proposal_data: DAOProposalCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Yangi DAO taklif yaratish"""
    
    # Check if user has enough tokens to create proposal
    user_balance = get_user_token_balance(current_user.id.hex, "AITF")
    
    if user_balance < dao_settings["proposal_threshold"]:
        raise HTTPException(
            status_code=400,
            detail=f"Taklif yaratish uchun kamida {dao_settings['proposal_threshold']} {dao_settings['governance_token']} kerak"
        )
    
    # Create proposal
    proposal_id = str(uuid.uuid4())
    proposal = DAOProposal(
        id=proposal_id,
        title=proposal_data.title,
        description=proposal_data.description,
        proposer_address=f"0x{current_user.id.hex[:12].upper()}",
        proposal_type=proposal_data.proposal_type,
        status=DAOProposalStatus.PENDING,
        voting_deadline=proposal_data.voting_deadline,
        created_at=datetime.utcnow()
    )
    
    # Store proposal
    proposals_db[proposal_id] = proposal
    
    # Schedule activation
    background_tasks.add_task(schedule_proposal_activation, proposal_id)
    
    return DAOProposalResponse(
        proposal=proposal,
        message="DAO taklif muvaffaqiyatli yaratildi"
    )

@router.get("/proposals/{proposal_id}", response_model=Dict[str, Any])
async def get_proposal_details(
    proposal_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Taklif tafsilotlarini olish"""
    
    if proposal_id not in proposals_db:
        raise HTTPException(
            status_code=404,
            detail="Taklif topilmadi"
        )
    
    proposal = proposals_db[proposal_id]
    
    # Get votes for this proposal
    proposal_votes = [
        vote for vote in votes_db.values()
        if vote.proposal_id == proposal_id
    ]
    
    # Calculate vote statistics
    votes_for = sum(1 for vote in proposal_votes if vote.vote_type == "for")
    votes_against = sum(1 for vote in proposal_votes if vote.vote_type == "against")
    votes_abstain = sum(1 for vote in proposal_votes if vote.vote_type == "abstain")
    
    total_votes = len(proposal_votes)
    
    # Calculate voting power
    total_for_power = sum(vote.voting_power for vote in proposal_votes if vote.vote_type == "for")
    total_against_power = sum(vote.voting_power for vote in proposal_votes if vote.vote_type == "against")
    
    return {
        "proposal": proposal,
        "voting_stats": {
            "total_votes": total_votes,
            "votes_for": votes_for,
            "votes_against": votes_against,
            "votes_abstain": votes_abstain,
            "total_for_power": str(total_for_power),
            "total_against_power": str(total_against_power),
            "participation_rate": round(total_votes / 100, 3)  # Mock participation
        },
        "timeline": {
            "created": proposal.created_at.isoformat(),
            "voting_deadline": proposal.voting_deadline.isoformat(),
            "time_remaining": str(proposal.voting_deadline - datetime.utcnow()),
            "status_updated": proposal.created_at.isoformat()
        },
        "recent_votes": [
            {
                "voter": vote.voter_address,
                "vote": vote.vote_type,
                "voting_power": str(vote.voting_power),
                "timestamp": vote.created_at.isoformat()
            }
            for vote in proposal_votes[-10:]  # Last 10 votes
        ]
    }

@router.post("/proposals/{proposal_id}/vote", response_model=BaseResponse)
async def cast_vote(
    proposal_id: str,
    vote_request: VoteRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Taklifga ovoz berish"""
    
    if proposal_id not in proposals_db:
        raise HTTPException(
            status_code=404,
            detail="Taklif topilmadi"
        )
    
    proposal = proposals_db[proposal_id]
    
    # Check voting period
    if datetime.utcnow() > proposal.voting_deadline:
        raise HTTPException(
            status_code=400,
            detail="Ovoz berish muddati tugagan"
        )
    
    # Check if user already voted
    existing_vote = get_user_vote(proposal_id, current_user.id.hex)
    if existing_vote:
        raise HTTPException(
            status_code=400,
            detail="Siz allaqachon bu taklifga ovoz berdingiz"
        )
    
    # Get user's voting power
    voting_power = get_user_token_balance(current_user.id.hex, "AITF")
    
    if voting_power <= 0:
        raise HTTPException(
            status_code=400,
            detail="Ovoz berish uchun token kerak"
        )
    
    # Create vote
    vote_id = str(uuid.uuid4())
    vote = {
        "id": vote_id,
        "proposal_id": proposal_id,
        "voter_address": f"0x{current_user.id.hex[:12].upper()}",
        "vote_type": vote_request.vote,
        "voting_power": voting_power,
        "created_at": datetime.utcnow()
    }
    
    # Store vote
    votes_db[vote_id] = vote
    
    # Update proposal vote counts
    if vote_request.vote == "for":
        proposal.votes_for += 1
    elif vote_request.vote == "against":
        proposal.votes_against += 1
    else:
        proposal.votes_abstain += 1
    
    return BaseResponse(
        message="Ovozingiz muvaffaqiyatli qabul qilindi"
    )

@router.post("/proposals/{proposal_id}/execute", response_model=BaseResponse)
async def execute_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Taklifni bajarish"""
    
    if proposal_id not in proposals_db:
        raise HTTPException(
            status_code=404,
            detail="Taklif topilmadi"
        )
    
    proposal = proposals_db[proposal_id]
    
    # Check if proposal can be executed
    if proposal.status != DAOProposalStatus.PASSED:
        raise HTTPException(
            status_code=400,
            detail="Faqat o'tkazilgan takliflar bajarilishi mumkin"
        )
    
    # Check execution delay
    if datetime.utcnow() < proposal.voting_deadline + dao_settings["execution_delay"]:
        raise HTTPException(
            status_code=400,
            detail="Bajarish muddati hali kelmagan"
        )
    
    # Execute proposal (mock implementation)
    proposal.status = DAOProposalStatus.EXECUTED
    
    return BaseResponse(
        message="Taklif muvaffaqiyatli bajarildi"
    )

# =============================================================================
# DAO GOVERNANCE ANALYSIS
# =============================================================================

@router.get("/governance/overview", response_model=Dict[str, Any])
async def get_governance_overview(current_user: User = Depends(get_current_active_user)):
    """Boshqaruv umumiy ko'rinish"""
    
    # Calculate statistics
    total_proposals = len(proposals_db)
    active_proposals = len([p for p in proposals_db.values() if p.status == DAOProposalStatus.ACTIVE])
    passed_proposals = len([p for p in proposals_db.values() if p.status == DAOProposalStatus.PASSED])
    
    # Get recent proposals
    recent_proposals = sorted(
        proposals_db.values(),
        key=lambda x: x.created_at,
        reverse=True
    )[:5]
    
    return {
        "dao_info": {
            "name": "AI Trading Fund DAO",
            "governance_token": dao_settings["governance_token"],
            "total_members": 1247,
            "total_proposals": total_proposals,
            "active_proposals": active_proposals,
            "passed_proposals": passed_proposals
        },
        "governance_settings": {
            "proposal_threshold": str(dao_settings["proposal_threshold"]),
            "voting_period_days": dao_settings["voting_period"].days,
            "execution_delay_days": dao_settings["execution_delay"].days,
            "quorum_percentage": float(dao_settings["quorum"]) * 100,
            "pass_threshold_percentage": float(dao_settings["pass_threshold"]) * 100
        },
        "recent_proposals": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status.value,
                "created_at": p.created_at.isoformat(),
                "votes_for": p.votes_for,
                "votes_against": p.votes_against
            }
            for p in recent_proposals
        ],
        "voting_activity": {
            "total_votes_cast": len(votes_db),
            "average_turnout": "23.5%",
            "most_active_voter": "0x1234567890AB",
            "voting_power_distribution": {
                "top_10_holders": "45.2%",
                "next_40_holders": "32.1%",
                "remaining_holders": "22.7%"
            }
        }
    }

@router.get("/governance/treasury", response_model=Dict[str, Any])
async def get_treasury_status(current_user: User = Depends(get_current_active_user)):
    """Xazinma holati"""
    
    # Calculate total value in USD
    total_value_usd = Decimal("0")
    
    token_prices = {
        "AITF": 5.25,
        "ETH": 2100.0,
        "USDT": 1.0,
        "BTC": 45000.0
    }
    
    for token, balance in treasury_balance.items():
        value_usd = balance * Decimal(str(token_prices[token]))
        total_value_usd += value_usd
    
    return {
        "treasury_overview": {
            "total_value_usd": str(total_value_usd),
            "total_tokens": len(treasury_balance),
            "last_updated": datetime.utcnow().isoformat()
        },
        "token_balances": {
            token: {
                "balance": str(balance),
                "usd_value": str(balance * Decimal(str(token_prices[token]))),
                "percentage_of_total": str(round(balance * Decimal(str(token_prices[token])) / total_value_usd * 100, 2))
            }
            for token, balance in treasury_balance.items()
        },
        "treasury_operations": {
            "total_revenue_30d": "45,230 USD",
            "total_expenses_30d": "12,450 USD",
            "net_income_30d": "32,780 USD",
            "treasury_growth": "+15.2% this month"
        },
        "allocation_strategy": {
            "AI_development": "40%",
            "Marketing": "25%",
            "Operations": "20%",
            "Reserve": "15%"
        }
    }

@router.get("/governance/members", response_model=Dict[str, Any])
async def get_dao_members(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("voting_power", description="Sort by: voting_power, tokens, activity"),
    current_user: User = Depends(get_current_active_user)
):
    """DAO a'zolari ro'yxati"""
    
    # Mock member data
    members = []
    for i in range(50):
        member_address = f"0x{(i * 1234567890) & 0xffffffffffff:012x}"
        token_balance = Decimal(str(1000 + i * 500))
        voting_power = token_balance
        activity_score = np.random.randint(1, 100)
        
        members.append({
            "address": member_address,
            "token_balance": str(token_balance),
            "voting_power": str(voting_power),
            "activity_score": activity_score,
            "proposals_created": np.random.randint(0, 5),
            "votes_cast": np.random.randint(0, 20),
            "joined_date": (datetime.utcnow() - timedelta(days=i * 30)).isoformat(),
            "rank": i + 1
        })
    
    # Sort members
    if sort_by == "voting_power":
        members.sort(key=lambda x: float(x["voting_power"]), reverse=True)
    elif sort_by == "tokens":
        members.sort(key=lambda x: float(x["token_balance"]), reverse=True)
    elif sort_by == "activity":
        members.sort(key=lambda x: x["activity_score"], reverse=True)
    
    # Paginate
    total = len(members)
    start = (page - 1) * size
    end = start + size
    paginated_members = members[start:end]
    
    return {
        "members": paginated_members,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
        "sort_by": sort_by
    }

# =============================================================================
# VOTING ANALYTICS
# =============================================================================

@router.get("/analytics/voting-patterns", response_model=Dict[str, Any])
async def get_voting_patterns(
    proposal_type: Optional[str] = Query(None),
    time_period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
    current_user: User = Depends(get_current_active_user)
):
    """Ovoz berish namunalari tahlili"""
    
    # Calculate time period
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map.get(time_period, 30)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Filter recent votes
    recent_votes = [
        vote for vote in votes_db.values()
        if vote.created_at > cutoff_date
    ]
    
    # Analyze voting patterns
    for_votes = [v for v in recent_votes if v.vote_type == "for"]
    against_votes = [v for v in recent_votes if v.vote_type == "against"]
    abstain_votes = [v for v in recent_votes if v.vote_type == "abstain"]
    
    return {
        "analysis_period": time_period,
        "proposal_type_filter": proposal_type,
        "total_votes": len(recent_votes),
        "vote_distribution": {
            "for": len(for_votes),
            "against": len(against_votes),
            "abstain": len(abstain_votes)
        },
        "voting_power_distribution": {
            "for_power": sum(v.voting_power for v in for_votes),
            "against_power": sum(v.voting_power for v in against_votes),
            "abstain_power": sum(v.voting_power for v in abstain_votes)
        },
        "participation_metrics": {
            "unique_voters": len(set(v.voter_address for v in recent_votes)),
            "average_votes_per_proposal": round(len(recent_votes) / max(1, len(set(v.proposal_id for v in recent_votes))), 1),
            "participation_rate": "23.5%"
        },
        "trends": {
            "voting_activity_trend": "+15% this period",
            "proposal_success_rate": "78.2%",
            "average_voting_power": "1,250 AITF"
        },
        "top_voters": [
            {
                "address": f"0x{i:012x}",
                "votes_cast": 5 + i,
                "voting_power": 5000 + i * 1000
            }
            for i in range(10)
        ]
    }

# =============================================================================
# BACKGROUND TASKS
# =============================================================================

async def schedule_proposal_activation(proposal_id: str):
    """Taklif aktivatsiyasini rejalash"""
    try:
        logger.info(f"Taklif aktivatsiyasi rejalanyapti: {proposal_id}")
        
        # Wait for voting delay (if any)
        await asyncio.sleep(1)  # Mock delay
        
        # Activate proposal
        if proposal_id in proposals_db:
            proposal = proposals_db[proposal_id]
            proposal.status = DAOProposalStatus.ACTIVE
            
            logger.info(f"Taklif aktivlashtirildi: {proposal_id}")
        
    except Exception as e:
        logger.error(f"Taklif aktivatsiya xatosi: {e}")

def get_user_token_balance(user_address: str, token: str) -> Decimal:
    """Foydalanuvchi token balansini olish"""
    # Mock balance calculation
    return Decimal(str(1000 + int(user_address[:8], 16) % 5000))

def get_user_vote(proposal_id: str, user_address: str) -> Optional[Dict[str, Any]]:
    """Foydalanuvchi ovozini olish"""
    for vote in votes_db.values():
        if vote.proposal_id == proposal_id and vote.voter_address == f"0x{user_address[:12].upper()}":
            return vote
    return None

# Initialize mock data
def init_mock_dao_data():
    """Mock DAO ma'lumotlarini yaratish"""
    if not proposals_db:
        proposal_types = ["treasury", "governance", "technical", "partnership"]
        proposal_titles = [
            "Allocate funds for AI model development",
            "Update governance parameters",
            "Implement new trading strategies",
            "Partner with external protocol",
            "Adjust treasury allocation",
            "Launch new feature voting",
            "Update token economics",
            "Community grants program"
        ]
        
        for i in range(20):
            proposal_id = str(uuid.uuid4())
            status_options = list(DAOProposalStatus)
            current_status = status_options[i % len(status_options)]
            
            proposal = DAOProposal(
                id=proposal_id,
                title=proposal_titles[i % len(proposal_titles)],
                description=f"Detailed description for proposal {i+1}. This proposal aims to improve the DAO's functionality and value for all members.",
                proposer_address=f"0x{(i * 1234567890) & 0xffffffffffff:012x}",
                proposal_type=proposal_types[i % len(proposal_types)],
                status=current_status,
                voting_deadline=datetime.utcnow() + timedelta(days=i % 7),
                votes_for=np.random.randint(5, 50),
                votes_against=np.random.randint(1, 20),
                votes_abstain=np.random.randint(0, 10),
                created_at=datetime.utcnow() - timedelta(days=i)
            )
            
            proposals_db[proposal_id] = proposal
        
        # Create mock votes
        for i in range(100):
            vote_id = str(uuid.uuid4())
            proposal_list = list(proposals_db.keys())
            
            vote = {
                "id": vote_id,
                "proposal_id": proposal_list[i % len(proposal_list)],
                "voter_address": f"0x{(i * 987654321) & 0xffffffffffff:012x}",
                "vote_type": ["for", "against", "abstain"][i % 3],
                "voting_power": Decimal(str(100 + i * 50)),
                "created_at": datetime.utcnow() - timedelta(hours=i * 2)
            }
            
            votes_db[vote_id] = vote

# Initialize mock data on module load
import logging
logger = logging.getLogger(__name__)
import numpy as np
init_mock_dao_data()