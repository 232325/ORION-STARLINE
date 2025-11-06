"""
NFT Hedge Fund Governance System
Advanced governance structure for NFT-based hedge funds with performance fees
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import json
import hashlib
from collections import defaultdict
import math
from scipy.stats import norm
import logging

class ProposalType(Enum):
    PERFORMANCE_FEE_CHANGE = "performance_fee_change"
    MANAGEMENT_FEE_CHANGE = "management_fee_change"
    RISK_LIMIT_CHANGE = "risk_limit_change"
    STRATEGY_CHANGE = "strategy_change"
    NFT_HOLDING_CHANGE = "nft_holding_change"
    GOVERNANCE_TOKEN_ISSUE = "governance_token_issue"
    EMERGENCY_PAUSE = "emergency_pause"

class ProposalStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"

@dataclass
class GovernanceProposal:
    """Governance proposal structure"""
    proposal_id: str
    proposal_type: ProposalType
    title: str
    description: str
    proposer: str
    created_at: float
    voting_deadline: float
    status: ProposalStatus
    votes_for: int = 0
    votes_against: int = 0
    votes_abstain: int = 0
    parameters: Dict[str, Union[float, int, str]] = field(default_factory=dict)
    quantum_signature: Optional[str] = None
    
@dataclass
class NFTPosition:
    """NFT position in the hedge fund"""
    token_id: str
    metal_type: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    hedge_ratio: float
    created_at: float
    
@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    sortino_ratio: float
    calmar_ratio: float
    var_95: float  # Value at Risk (95%)
    cvar_95: float  # Conditional VaR
    beta: float
    alpha: float
    
@dataclass
class HighWaterMark:
    """High water mark tracking for performance fees"""
    nav: float
    timestamp: float
    performance_fee_applied: float

class NFTHedgeFundGovernance:
    """
    NFT Hedge Fund Governance System
    Manages proposals, voting, performance fees, and high-water marks
    """
    
    def __init__(self, fund_name: str, initial_nav: float):
        self.fund_name = fund_name
        self.current_nav = initial_nav
        self.initial_nav = initial_nav
        
        # Governance parameters
        self.proposals: Dict[str, GovernanceProposal] = {}
        self.vote_weights: Dict[str, float] = {}  # Address to voting weight
        self.total_voting_power = 0.0
        
        # Performance parameters
        self.performance_fee_rate = 0.20  # 20% performance fee
        self.management_fee_rate = 0.02   # 2% annual management fee
        self.high_water_marks: List[HighWaterMark] = []
        self.performance_fee_accrued = 0.0
        self.management_fee_accrued = 0.0
        
        # Risk limits
        self.max_drawdown_limit = 0.20  # 20% max drawdown
        self.var_limit = 0.05           # 5% daily VaR limit
        self.concentration_limit = 0.30  # 30% max concentration per metal
        
        # NFT positions tracking
        self.nft_positions: Dict[str, NFTPosition] = {}
        self.total_nft_value = 0.0
        
        # Quantum governance enhancements
        self.quantum_governance_enabled = True
        self.proposal_quorum_threshold = 0.10  # 10% of total voting power
        self.proposal_pass_threshold = 0.60    # 60% supermajority required
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize high water mark
        self._initialize_high_water_marks()
    
    def create_proposal(
        self,
        proposer: str,
        proposal_type: ProposalType,
        title: str,
        description: str,
        parameters: Dict[str, Union[float, int, str]],
        voting_period_days: float = 7.0
    ) -> str:
        """Create a new governance proposal"""
        
        # Generate unique proposal ID
        proposal_id = self._generate_proposal_id(proposer, title, int(time.time()))
        
        # Create proposal
        proposal = GovernanceProposal(
            proposal_id=proposal_id,
            proposal_type=proposal_type,
            title=title,
            description=description,
            proposer=proposer,
            created_at=time.time(),
            voting_deadline=time.time() + (voting_period_days * 86400),
            status=ProposalStatus.PENDING,
            parameters=parameters
        )
        
        # Add quantum signature if enabled
        if self.quantum_governance_enabled:
            proposal.quantum_signature = self._generate_quantum_signature(proposal)
        
        self.proposals[proposal_id] = proposal
        
        self.logger.info(f"Created proposal {proposal_id}: {title}")
        return proposal_id
    
    def cast_vote(
        self,
        proposal_id: str,
        voter: str,
        vote: int,  # 1 = for, -1 = against, 0 = abstain
        voting_power: float
    ) -> bool:
        """Cast vote on a proposal"""
        
        if proposal_id not in self.proposals:
            self.logger.error(f"Proposal {proposal_id} not found")
            return False
        
        proposal = self.proposals[proposal_id]
        
        # Check if voting is still open
        if time.time() > proposal.voting_deadline:
            self.logger.error(f"Voting closed for proposal {proposal_id}")
            return False
        
        # Validate vote
        if vote not in [-1, 0, 1]:
            self.logger.error("Invalid vote value")
            return False
        
        # Apply voting power
        if vote == 1:
            proposal.votes_for += voting_power
        elif vote == -1:
            proposal.votes_against += voting_power
        else:
            proposal.votes_abstain += voting_power
        
        self.logger.info(f"Vote cast on {proposal_id}: {vote} with power {voting_power}")
        return True
    
    def process_proposal_votes(self, proposal_id: str) -> ProposalStatus:
        """Process votes for a proposal and determine outcome"""
        
        if proposal_id not in self.proposals:
            return ProposalStatus.PENDING
        
        proposal = self.proposals[proposal_id]
        
        # Check if voting period has ended
        if time.time() < proposal.voting_deadline:
            return ProposalStatus.ACTIVE
        
        # Check quorum
        total_votes = proposal.votes_for + proposal.votes_against + proposal.votes_abstain
        if total_votes < (self.total_voting_power * self.proposal_quorum_threshold):
            proposal.status = ProposalStatus.REJECTED
            return ProposalStatus.REJECTED
        
        # Determine outcome
        if proposal.votes_for > proposal.votes_against:
            # Check for supermajority
            total_voting_power_cast = proposal.votes_for + proposal.votes_against
            if total_voting_power_cast > 0:
                support_ratio = proposal.votes_for / total_voting_power_cast
                if support_ratio >= self.proposal_pass_threshold:
                    proposal.status = ProposalStatus.PASSED
                else:
                    proposal.status = ProposalStatus.REJECTED
            else:
                proposal.status = ProposalStatus.REJECTED
        else:
            proposal.status = ProposalStatus.REJECTED
        
        self.logger.info(f"Proposal {proposal_id} status: {proposal.status}")
        return proposal.status
    
    def execute_proposal(self, proposal_id: str) -> bool:
        """Execute a passed proposal"""
        
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != ProposalStatus.PASSED:
            self.logger.error(f"Proposal {proposal_id} not passed")
            return False
        
        try:
            # Execute based on proposal type
            if proposal.proposal_type == ProposalType.PERFORMANCE_FEE_CHANGE:
                new_rate = proposal.parameters.get("new_rate", self.performance_fee_rate)
                self._update_performance_fee_rate(new_rate)
            
            elif proposal.proposal_type == ProposalType.MANAGEMENT_FEE_CHANGE:
                new_rate = proposal.parameters.get("new_rate", self.management_fee_rate)
                self._update_management_fee_rate(new_rate)
            
            elif proposal.proposal_type == ProposalType.RISK_LIMIT_CHANGE:
                self._update_risk_limits(proposal.parameters)
            
            elif proposal.proposal_type == ProposalType.STRATEGY_CHANGE:
                self._update_strategy_parameters(proposal.parameters)
            
            elif proposal.proposal_type == ProposalType.NFT_HOLDING_CHANGE:
                self._update_nft_holdings(proposal.parameters)
            
            elif proposal.proposal_type == ProposalType.EMERGENCY_PAUSE:
                self._trigger_emergency_pause()
            
            proposal.status = ProposalStatus.EXECUTED
            self.logger.info(f"Executed proposal {proposal_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute proposal {proposal_id}: {str(e)}")
            return False
    
    def calculate_performance_fees(self) -> float:
        """Calculate performance fees based on high-water mark"""
        
        current_nav = self.current_nav
        
        # Get the highest NAV since last fee calculation
        last_high_water = self._get_last_high_water_mark()
        
        if current_nav > last_high_water.nav:
            # Performance fee is charged on the excess return
            excess_return = current_nav - last_high_water.nav
            performance_fee = excess_return * self.performance_fee_rate
            
            # Update high water mark
            self._update_high_water_mark(current_nav, performance_fee)
            
            self.performance_fee_accrued += performance_fee
            
            self.logger.info(f"Performance fee calculated: {performance_fee:.2f}")
            return performance_fee
        
        return 0.0
    
    def calculate_management_fees(self, period_days: float) -> float:
        """Calculate management fees for the period"""
        
        # Annual management fee prorated for the period
        annual_management_fee = self.current_nav * self.management_fee_rate
        period_management_fee = annual_management_fee * (period_days / 365.0)
        
        self.management_fee_accrued += period_management_fee
        
        self.logger.info(f"Management fee for {period_days:.1f} days: {period_management_fee:.2f}")
        return period_management_fee
    
    def update_performance_metrics(
        self, 
        returns_history: List[float],
        benchmark_returns: Optional[List[float]] = None
    ) -> PerformanceMetrics:
        """Update and calculate comprehensive performance metrics"""
        
        if len(returns_history) < 2:
            return self._get_default_metrics()
        
        # Basic statistics
        total_return = np.prod([1 + r for r in returns_history]) - 1
        
        # Annualized return
        years = len(returns_history) / 252.0  # Assuming daily returns
        if years > 0:
            annualized_return = (1 + total_return) ** (1/years) - 1
        else:
            annualized_return = 0.0
        
        # Volatility (annualized)
        volatility = np.std(returns_history) * math.sqrt(252) if len(returns_history) > 1 else 0.0
        
        # Sharpe ratio
        risk_free_rate = 0.02  # 2% risk-free rate
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0.0
        
        # Maximum drawdown
        cumulative_returns = np.cumprod([1 + r for r in returns_history])
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = np.min(drawdown)
        
        # Sortino ratio (downside deviation)
        negative_returns = [r for r in returns_history if r < 0]
        if negative_returns:
            downside_deviation = np.std(negative_returns) * math.sqrt(252)
            sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0.0
        else:
            sortino_ratio = float('inf')
        
        # Calmar ratio
        calmar_ratio = abs(annualized_return / max_drawdown) if max_drawdown != 0 else 0.0
        
        # Value at Risk (95%)
        var_95 = np.percentile(returns_history, 5) if len(returns_history) > 0 else 0.0
        
        # Conditional VaR (95%)
        tail_returns = [r for r in returns_history if r <= var_95]
        cvar_95 = np.mean(tail_returns) if tail_returns else var_95
        
        # Beta and Alpha (if benchmark provided)
        beta = 0.0
        alpha = 0.0
        
        if benchmark_returns and len(benchmark_returns) == len(returns_history):
            # Calculate beta
            fund_var = np.var(returns_history)
            if fund_var > 0:
                covariance = np.cov(returns_history, benchmark_returns)[0, 1]
                benchmark_var = np.var(benchmark_returns)
                beta = covariance / benchmark_var if benchmark_var > 0 else 0.0
            
            # Calculate alpha
            alpha = annualized_return - (risk_free_rate + beta * (np.mean(benchmark_returns) * 252 - risk_free_rate))
        
        metrics = PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            var_95=var_95,
            cvar_95=cvar_95,
            beta=beta,
            alpha=alpha
        )
        
        self.logger.info(f"Updated performance metrics - Sharpe: {sharpe_ratio:.3f}, Max DD: {max_drawdown:.3f}")
        return metrics
    
    def add_nft_position(self, position: NFTPosition) -> bool:
        """Add NFT position to the fund"""
        
        # Check concentration limits
        metal_allocation = self._calculate_metal_allocation(position.metal_type)
        new_allocation = (metal_allocation + position.quantity) / self.total_nft_value if self.total_nft_value > 0 else 1.0
        
        if new_allocation > self.concentration_limit:
            self.logger.warning(f"Concentration limit exceeded for {position.metal_type}")
            return False
        
        # Add position
        self.nft_positions[position.token_id] = position
        self.total_nft_value += position.quantity * position.current_price
        
        self.logger.info(f"Added NFT position {position.token_id} for {position.metal_type}")
        return True
    
    def update_nft_position_price(self, token_id: str, new_price: float) -> bool:
        """Update NFT position market price"""
        
        if token_id not in self.nft_positions:
            return False
        
        position = self.nft_positions[token_id]
        old_value = position.quantity * position.current_price
        position.current_price = new_price
        position.unrealized_pnl = position.quantity * (new_price - position.entry_price)
        
        # Update total value
        new_value = position.quantity * new_price
        self.total_nft_value += (new_value - old_value)
        
        return True
    
    def risk_check(self) -> Dict[str, bool]:
        """Perform comprehensive risk checks"""
        
        risk_checks = {
            "drawdown_ok": True,
            "var_ok": True,
            "concentration_ok": True,
            "liquidity_ok": True
        }
        
        # Check drawdown
        current_drawdown = self._calculate_current_drawdown()
        if current_drawdown < -self.max_drawdown_limit:
            risk_checks["drawdown_ok"] = False
            self.logger.warning(f"Drawdown limit breached: {current_drawdown:.3f}")
        
        # Check VaR
        var_breach = self._calculate_current_var()
        if var_breach < -self.var_limit:
            risk_checks["var_ok"] = False
            self.logger.warning(f"VaR limit breached: {var_breach:.3f}")
        
        # Check concentration
        if not self._check_concentration_limits():
            risk_checks["concentration_ok"] = False
            self.logger.warning("Concentration limits breached")
        
        return risk_checks
    
    def quantum_governance_enhancement(self) -> Dict[str, float]:
        """Apply quantum governance enhancements"""
        
        if not self.quantum_governance_enabled:
            return {}
        
        enhancements = {}
        
        # Quantum voting power calculation
        quantum_voting_weights = self._calculate_quantum_voting_weights()
        enhancements.update(quantum_voting_weights)
        
        # Quantum proposal scoring
        proposal_scores = self._calculate_quantum_proposal_scores()
        enhancements.update(proposal_scores)
        
        # Quantum risk assessment
        quantum_risk_scores = self._calculate_quantum_risk_scores()
        enhancements.update(quantum_risk_scores)
        
        return enhancements
    
    def generate_governance_report(self) -> Dict[str, any]:
        """Generate comprehensive governance report"""
        
        report = {
            "fund_name": self.fund_name,
            "current_nav": self.current_nav,
            "performance_metrics": self._get_latest_metrics(),
            "fee_structure": {
                "performance_fee_rate": self.performance_fee_rate,
                "management_fee_rate": self.management_fee_rate,
                "performance_fee_accrued": self.performance_fee_accrued,
                "management_fee_accrued": self.management_fee_accrued
            },
            "nft_positions": {
                "total_positions": len(self.nft_positions),
                "total_value": self.total_nft_value,
                "metal_breakdown": self._get_metal_breakdown()
            },
            "governance": {
                "active_proposals": len([p for p in self.proposals.values() if p.status == ProposalStatus.ACTIVE]),
                "total_voting_power": self.total_voting_power,
                "quantum_governance_enabled": self.quantum_governance_enabled
            },
            "risk_metrics": self.risk_check(),
            "high_water_marks": len(self.high_water_marks)
        }
        
        return report
    
    # Private helper methods
    
    def _initialize_high_water_marks(self):
        """Initialize high water mark tracking"""
        self.high_water_marks.append(
            HighWaterMark(nav=self.initial_nav, timestamp=time.time(), performance_fee_applied=0.0)
        )
    
    def _generate_proposal_id(self, proposer: str, title: str, timestamp: int) -> str:
        """Generate unique proposal ID"""
        data = f"{proposer}_{title}_{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_quantum_signature(self, proposal: GovernanceProposal) -> str:
        """Generate quantum signature for proposal"""
        # Simplified quantum signature
        data = f"{proposal.proposal_id}_{proposal.created_at}_{proposal.parameters}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _update_performance_fee_rate(self, new_rate: float):
        """Update performance fee rate"""
        if 0 <= new_rate <= 0.50:  # Max 50% performance fee
            old_rate = self.performance_fee_rate
            self.performance_fee_rate = new_rate
            self.logger.info(f"Performance fee updated from {old_rate:.1%} to {new_rate:.1%}")
    
    def _update_management_fee_rate(self, new_rate: float):
        """Update management fee rate"""
        if 0 <= new_rate <= 0.10:  # Max 10% management fee
            old_rate = self.management_fee_rate
            self.management_fee_rate = new_rate
            self.logger.info(f"Management fee updated from {old_rate:.1%} to {new_rate:.1%}")
    
    def _update_risk_limits(self, parameters: Dict[str, Union[float, int, str]]):
        """Update risk limit parameters"""
        if "max_drawdown" in parameters:
            self.max_drawdown_limit = float(parameters["max_drawdown"])
        if "var_limit" in parameters:
            self.var_limit = float(parameters["var_limit"])
        if "concentration_limit" in parameters:
            self.concentration_limit = float(parameters["concentration_limit"])
        
        self.logger.info("Risk limits updated")
    
    def _update_strategy_parameters(self, parameters: Dict[str, Union[float, int, str]]):
        """Update strategy parameters"""
        # Implementation would depend on specific strategies
        self.logger.info("Strategy parameters updated")
    
    def _update_nft_holdings(self, parameters: Dict[str, Union[float, int, str]]):
        """Update NFT holdings based on proposal"""
        # Implementation would handle NFT allocation changes
        self.logger.info("NFT holdings updated")
    
    def _trigger_emergency_pause(self):
        """Trigger emergency pause of fund operations"""
        # Implementation would pause all trading and operations
        self.logger.info("Emergency pause triggered")
    
    def _get_last_high_water_mark(self) -> HighWaterMark:
        """Get the last high water mark"""
        return self.high_water_marks[-1] if self.high_water_marks else HighWaterMark(0, 0, 0)
    
    def _update_high_water_mark(self, nav: float, performance_fee: float):
        """Update high water mark"""
        self.high_water_marks.append(
            HighWaterMark(nav=nav, timestamp=time.time(), performance_fee_applied=performance_fee)
        )
    
    def _calculate_metal_allocation(self, metal_type: str) -> float:
        """Calculate allocation percentage for a metal type"""
        if self.total_nft_value == 0:
            return 0.0
        
        metal_value = sum(
            pos.quantity * pos.current_price 
            for pos in self.nft_positions.values() 
            if pos.metal_type == metal_type
        )
        
        return metal_value / self.total_nft_value
    
    def _calculate_current_drawdown(self) -> float:
        """Calculate current drawdown from peak"""
        if not self.high_water_marks:
            return 0.0
        
        peak_nav = max(hwm.nav for hwm in self.high_water_marks)
        current_drawdown = (self.current_nav - peak_nav) / peak_nav
        
        return current_drawdown
    
    def _calculate_current_var(self) -> float:
        """Calculate current Value at Risk"""
        # Simplified VaR calculation
        # In practice, would use historical returns or Monte Carlo simulation
        return -0.03  # -3% daily VaR (placeholder)
    
    def _check_concentration_limits(self) -> bool:
        """Check if concentration limits are maintained"""
        metal_allocations = {}
        for metal in set(pos.metal_type for pos in self.nft_positions.values()):
            allocation = self._calculate_metal_allocation(metal)
            metal_allocations[metal] = allocation
        
        return all(alloc <= self.concentration_limit for alloc in metal_allocations.values())
    
    def _calculate_quantum_voting_weights(self) -> Dict[str, float]:
        """Calculate quantum-enhanced voting weights"""
        # Simplified quantum voting power calculation
        weights = {}
        for address in self.vote_weights:
            classical_weight = self.vote_weights[address]
            # Apply quantum enhancement factor
            quantum_factor = 1.0 + 0.1 * np.random.random()  # 0-10% quantum boost
            weights[address] = classical_weight * quantum_factor
        
        return {"quantum_voting_weights": np.mean(list(weights.values())) if weights else 0}
    
    def _calculate_quantum_proposal_scores(self) -> Dict[str, float]:
        """Calculate quantum scores for active proposals"""
        scores = {}
        for proposal_id, proposal in self.proposals.items():
            if proposal.status == ProposalStatus.ACTIVE:
                # Quantum proposal scoring
                classical_score = proposal.votes_for / max(1, proposal.votes_for + proposal.votes_against)
                quantum_enhancement = np.sin(proposal.created_at) * 0.05  # Time-based quantum factor
                scores[proposal_id] = classical_score + quantum_enhancement
        
        return {"quantum_proposal_scores": np.mean(list(scores.values())) if scores else 0}
    
    def _calculate_quantum_risk_scores(self) -> Dict[str, float]:
        """Calculate quantum-enhanced risk scores"""
        # Quantum risk assessment
        drawdown_risk = abs(self._calculate_current_drawdown())
        var_risk = abs(self._calculate_current_var())
        
        # Quantum enhancement of risk assessment
        quantum_factor = 1.0 + 0.05 * np.random.random()
        
        enhanced_risk = (drawdown_risk + var_risk) * quantum_factor
        
        return {"quantum_risk_score": enhanced_risk}
    
    def _get_default_metrics(self) -> PerformanceMetrics:
        """Return default metrics when insufficient data"""
        return PerformanceMetrics(
            total_return=0.0, annualized_return=0.0, volatility=0.0,
            sharpe_ratio=0.0, max_drawdown=0.0, sortino_ratio=0.0,
            calmar_ratio=0.0, var_95=0.0, cvar_95=0.0, beta=0.0, alpha=0.0
        )
    
    def _get_latest_metrics(self) -> Dict[str, float]:
        """Get latest performance metrics (placeholder)"""
        return {
            "total_return": 0.15,      # 15% placeholder
            "sharpe_ratio": 1.2,       # 1.2 placeholder
            "max_drawdown": -0.08,     # -8% placeholder
            "volatility": 0.12         # 12% placeholder
        }
    
    def _get_metal_breakdown(self) -> Dict[str, float]:
        """Get breakdown of NFT positions by metal"""
        breakdown = {}
        total_value = self.total_nft_value if self.total_nft_value > 0 else 1
        
        for metal in set(pos.metal_type for pos in self.nft_positions.values()):
            metal_value = sum(
                pos.quantity * pos.current_price 
                for pos in self.nft_positions.values() 
                if pos.metal_type == metal
            )
            breakdown[metal] = metal_value / total_value
        
        return breakdown


# Example usage
if __name__ == "__main__":
    # Initialize hedge fund governance
    fund = NFTHedgeFundGovernance("QuantumMetal NFT Fund", 10000000)  # $10M fund
    
    # Add some voting power
    fund.vote_weights["alice"] = 1000.0
    fund.vote_weights["bob"] = 1500.0
    fund.vote_weights["charlie"] = 2000.0
    fund.total_voting_power = 4500.0
    
    # Create a proposal to change performance fee
    proposal_id = fund.create_proposal(
        proposer="alice",
        proposal_type=ProposalType.PERFORMANCE_FEE_CHANGE,
        title="Reduce Performance Fee to 15%",
        description="Proposal to reduce performance fee from 20% to 15% to be more competitive",
        parameters={"new_rate": 0.15},
        voting_period_days=7.0
    )
    
    print(f"Created proposal: {proposal_id}")
    
    # Cast votes
    fund.cast_vote(proposal_id, "alice", 1, 1000.0)  # Vote for
    fund.cast_vote(proposal_id, "bob", 1, 1500.0)    # Vote for  
    fund.cast_vote(proposal_id, "charlie", 1, 2000.0) # Vote for
    
    # Process proposal
    status = fund.process_proposal_votes(proposal_id)
    print(f"Proposal status: {status}")
    
    if status == ProposalStatus.PASSED:
        success = fund.execute_proposal(proposal_id)
        print(f"Proposal executed: {success}")
    
    # Add NFT positions
    nft_pos = NFTPosition(
        token_id="1",
        metal_type="GOLD",
        quantity=100.0,
        entry_price=2000.0,
        current_price=2050.0,
        unrealized_pnl=5000.0,
        hedge_ratio=0.8,
        created_at=time.time()
    )
    fund.add_nft_position(nft_pos)
    
    # Calculate performance fees
    fund.current_nav = 11000000  # $11M NAV
    performance_fee = fund.calculate_performance_fees()
    print(f"Performance fee: ${performance_fee:.2f}")
    
    # Generate governance report
    report = fund.generate_governance_report()
    print("\nGovernance Report:")
    print(json.dumps(report, indent=2, default=str))