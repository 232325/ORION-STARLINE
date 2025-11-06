"""
DAO Governance Integration

Governance-based decision approval
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

@dataclass
class GovernanceProposal:
    """Governance proposal structure"""
    proposal_id: str
    title: str
    description: str
    proposal_type: str  # "trading_decision", "parameter_change", "strategy_change"
    parameters: Dict[str, Any]
    requested_by: str
    created_at: datetime
    voting_deadline: datetime
    status: str  # "pending", "approved", "rejected", "expired"

@dataclass
class VotingResult:
    """Voting result"""
    proposal_id: str
    total_votes: int
    approved_votes: int
    rejected_votes: int
    abstain_votes: int
    result: str  # "approved", "rejected", "tie"
    approval_rate: float

class DAOGovernance:
    """
    DAO Governance Integration
    
    - Proposal creation and management
    - Voting mechanisms
    - Stakeholder consensus building
    - Decision approval workflows
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Governance parameters
        self.voting_period = config.get("governance_voting_period", 86400)  # 24 hours
        self.quorum_threshold = config.get("governance_quorum", 0.1)  # 10% participation
        self.approval_threshold = config.get("governance_approval_threshold", 0.6)  # 60% approval
        
        # Proposal storage
        self.proposals = {}
        self.voting_records = {}
        self.stakeholder_weights = {}  # Stakeholder voting weights
        
        # Governance rules
        self.large_trade_threshold = config.get("large_trade_threshold", 0.1)  # 10% of portfolio
        self.strategy_change_threshold = config.get("strategy_change_threshold", 0.05)  # 5% confidence
        
        self.is_running = False
    
    def start(self):
        """DAO governance ni ishga tushirish"""
        if self.is_running:
            self.logger.warning("DAO governance allaqachon ishlayapti")
            return
        
        self.is_running = True
        self.logger.info("DAO governance started")
    
    def stop(self):
        """DAO governance ni to'xtatish"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info("DAO governance stopped")
    
    async def create_proposal(self, proposal_data: Dict[str, Any]) -> str:
        """
        Proposal yaratish
        """
        if not self.is_running:
            raise RuntimeError("DAO governance is not running")
        
        try:
            proposal_id = f"prop_{datetime.now().isoformat()}"
            
            # Proposal validation
            validation_result = await self._validate_proposal(proposal_data)
            if not validation_result["valid"]:
                raise ValueError(f"Proposal validation failed: {validation_result['errors']}")
            
            # Create proposal
            proposal = GovernanceProposal(
                proposal_id=proposal_id,
                title=proposal_data.get("title", "Trading Decision Proposal"),
                description=proposal_data.get("description", ""),
                proposal_type=proposal_data.get("type", "trading_decision"),
                parameters=proposal_data.get("parameters", {}),
                requested_by=proposal_data.get("requested_by", "system"),
                created_at=datetime.now(),
                voting_deadline=datetime.now() + timedelta(seconds=self.voting_period),
                status="pending"
            )
            
            # Store proposal
            self.proposals[proposal_id] = proposal
            
            # Initialize voting record
            self.voting_records[proposal_id] = {
                "votes": {},
                "total_weight": 0.0,
                "approved_weight": 0.0,
                "rejected_weight": 0.0
            }
            
            # Start voting process
            await self._initiate_voting(proposal)
            
            self.logger.info(f"Proposal created: {proposal_id}")
            return proposal_id
            
        except Exception as e:
            self.logger.error(f"Proposal creation xatosi: {str(e)}")
            raise
    
    async def _validate_proposal(self, proposal_data: Dict) -> Dict[str, Any]:
        """Proposal validation"""
        validation_result = {
            "valid": True,
            "errors": []
        }
        
        # Required fields check
        required_fields = ["type", "description"]
        for field in required_fields:
            if field not in proposal_data or not proposal_data[field]:
                validation_result["errors"].append(f"Missing required field: {field}")
        
        # Trading decision specific validation
        if proposal_data.get("type") == "trading_decision":
            parameters = proposal_data.get("parameters", {})
            
            # Check if it's a large trade requiring governance
            trade_size = parameters.get("trade_size", 0)
            if trade_size > self.large_trade_threshold:
                self.logger.info(f"Large trade detected: {trade_size:.2%}")
            
            # Check confidence level
            confidence = parameters.get("confidence", 0)
            if confidence < self.strategy_change_threshold:
                validation_result["errors"].append("Low confidence decision requires governance")
        
        if validation_result["errors"]:
            validation_result["valid"] = False
        
        return validation_result
    
    async def _initiate_voting(self, proposal: GovernanceProposal):
        """Voting jarayonini boshlash"""
        # Notify stakeholders
        await self._notify_stakeholders(proposal)
        
        # Start voting monitoring
        asyncio.create_task(self._monitor_voting_period(proposal.proposal_id))
        
        self.logger.info(f"Voting initiated for proposal: {proposal.proposal_id}")
    
    async def _notify_stakeholders(self, proposal: GovernanceProposal):
        """Stakeholder larni notification qilish"""
        # Mock notification implementation
        notification_data = {
            "proposal_id": proposal.proposal_id,
            "title": proposal.title,
            "description": proposal.description,
            "type": proposal.proposal_type,
            "voting_deadline": proposal.voting_deadline.isoformat()
        }
        
        self.logger.info(f"Stakeholders notified about proposal: {proposal.proposal_id}")
    
    async def _monitor_voting_period(self, proposal_id: str):
        """Voting period monitoring"""
        try:
            proposal = self.proposals.get(proposal_id)
            if not proposal:
                return
            
            # Monitor until voting deadline
            while datetime.now() < proposal.voting_deadline:
                await asyncio.sleep(60)  # Check every minute
            
            # Close voting and count results
            await self._close_voting_and_count(proposal_id)
            
        except Exception as e:
            self.logger.error(f"Voting monitoring xatosi: {str(e)}")
    
    async def _close_voting_and_count(self, proposal_id: str):
        """Voting ni yopish va natijalarni hisoblash"""
        try:
            voting_record = self.voting_records.get(proposal_id)
            proposal = self.proposals.get(proposal_id)
            
            if not voting_record or not proposal:
                return
            
            # Calculate results
            total_weight = voting_record["total_weight"]
            approved_weight = voting_record["approved_weight"]
            rejected_weight = voting_record["rejected_weight"]
            
            # Determine result
            if total_weight > 0:
                approval_rate = approved_weight / total_weight
                participation_rate = total_weight / self._get_total_stakeholder_weight()
                
                # Check if quorum is met
                if participation_rate >= self.quorum_threshold:
                    if approval_rate >= self.approval_threshold:
                        result = "approved"
                        proposal.status = "approved"
                    elif (1 - approval_rate) >= self.approval_threshold:
                        result = "rejected"
                        proposal.status = "rejected"
                    else:
                        result = "tie"
                        proposal.status = "rejected"  # Default to rejection
                else:
                    result = "quorum_not_met"
                    proposal.status = "expired"
            else:
                result = "no_votes"
                proposal.status = "expired"
            
            # Update proposal status
            self.proposals[proposal_id] = proposal
            
            # Create voting result
            voting_result = VotingResult(
                proposal_id=proposal_id,
                total_votes=len(voting_record["votes"]),
                approved_votes=int(approved_weight * 100),  # Mock vote count
                rejected_votes=int(rejected_weight * 100),
                abstain_votes=0,
                result=result,
                approval_rate=approval_rate if total_weight > 0 else 0
            )
            
            # Emit voting result event
            await self._emit_voting_result_event(voting_result)
            
            self.logger.info(f"Voting closed for {proposal_id}: {result}")
            
        except Exception as e:
            self.logger.error(f"Voting count xatosi: {str(e)}")
    
    def _get_total_stakeholder_weight(self) -> float:
        """Total stakeholder weight olish"""
        return sum(self.stakeholder_weights.values())
    
    async def _emit_voting_result_event(self, voting_result: VotingResult):
        """Voting result event emit qilish"""
        event_data = asdict(voting_result)
        
        # In a real implementation, this would emit to the event system
        self.logger.info(f"Voting result: {voting_result.result} ({voting_result.approval_rate:.2%})")
    
    async def submit_vote(self, proposal_id: str, stakeholder_id: str, 
                         vote: str, weight: float = 1.0) -> Dict[str, Any]:
        """
        Vote qabul qilish
        """
        if not self.is_running:
            raise RuntimeError("DAO governance is not running")
        
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        proposal = self.proposals[proposal_id]
        
        # Check if voting is still open
        if datetime.now() > proposal.voting_deadline:
            return {"success": False, "error": "Voting period has ended"}
        
        # Validate vote
        if vote not in ["approve", "reject", "abstain"]:
            return {"success": False, "error": "Invalid vote option"}
        
        # Record vote
        voting_record = self.voting_records[proposal_id]
        voting_record["votes"][stakeholder_id] = {
            "vote": vote,
            "weight": weight,
            "timestamp": datetime.now()
        }
        
        # Update totals
        voting_record["total_weight"] += weight
        
        if vote == "approve":
            voting_record["approved_weight"] += weight
        elif vote == "reject":
            voting_record["rejected_weight"] += weight
        
        self.logger.info(f"Vote received: {stakeholder_id} voted {vote} on {proposal_id}")
        
        return {"success": True, "message": "Vote recorded successfully"}
    
    def get_proposal_status(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Proposal status olish"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return None
        
        voting_record = self.voting_records.get(proposal_id, {})
        
        return {
            "proposal_id": proposal_id,
            "title": proposal.title,
            "description": proposal.description,
            "type": proposal.proposal_type,
            "status": proposal.status,
            "created_at": proposal.created_at.isoformat(),
            "voting_deadline": proposal.voting_deadline.isoformat(),
            "voting_stats": {
                "total_votes": len(voting_record.get("votes", {})),
                "total_weight": voting_record.get("total_weight", 0),
                "approved_weight": voting_record.get("approved_weight", 0),
                "rejected_weight": voting_record.get("rejected_weight", 0)
            }
        }
    
    def list_proposals(self, status: Optional[str] = None, 
                      limit: int = 10) -> List[Dict[str, Any]]:
        """Proposal ro'yxati"""
        proposals = list(self.proposals.values())
        
        if status:
            proposals = [p for p in proposals if p.status == status]
        
        # Sort by creation date (newest first)
        proposals.sort(key=lambda p: p.created_at, reverse=True)
        
        # Limit results
        proposals = proposals[:limit]
        
        result = []
        for proposal in proposals:
            result.append({
                "proposal_id": proposal.proposal_id,
                "title": proposal.title,
                "type": proposal.proposal_type,
                "status": proposal.status,
                "created_at": proposal.created_at.isoformat(),
                "voting_deadline": proposal.voting_deadline.isoformat()
            })
        
        return result
    
    def get_governance_stats(self) -> Dict[str, Any]:
        """Governance statistikalari"""
        total_proposals = len(self.proposals)
        pending_proposals = len([p for p in self.proposals.values() if p.status == "pending"])
        approved_proposals = len([p for p in self.proposals.values() if p.status == "approved"])
        rejected_proposals = len([p for p in self.proposals.values() if p.status == "rejected"])
        
        return {
            "total_proposals": total_proposals,
            "pending_proposals": pending_proposals,
            "approved_proposals": approved_proposals,
            "rejected_proposals": rejected_proposals,
            "approval_rate": approved_proposals / total_proposals if total_proposals > 0 else 0,
            "quorum_threshold": self.quorum_threshold,
            "approval_threshold": self.approval_threshold,
            "voting_period_hours": self.voting_period / 3600
        }