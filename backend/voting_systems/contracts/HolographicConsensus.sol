// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title HolographicConsensus
 * @dev Holographic consensus for scalable governance
 * @author Advanced Voting Systems
 */
contract HolographicConsensus is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;

    struct SubDAOMember {
        address member;
        uint256 weight;
        uint256 lastActivity;
        bool isActive;
        uint256 reputationScore;
    }

    struct SubDAO {
        uint256 id;
        string name;
        string description;
        uint256 requiredStake;
        uint256 memberCount;
        bool isActive;
        mapping(address => SubDAOMember) members;
        mapping(address => bool) isMember;
    }

    struct HolographicProposal {
        uint256 id;
        string title;
        string description;
        uint256 submissionTime;
        uint256 subDAOProposalEndTime;
        uint256 consensusEndTime;
        uint256 requiredSubDAOs;
        uint256 targetSubDAO;
        bool consensusReached;
        bool executed;
        mapping(uint256 => int256) subDAOOutcomes; // Per SubDAO
        mapping(uint256 => uint256) subDAOStakes;
        mapping(address => int256) finalVotes;
        int256 finalConsensus;
    }

    mapping(uint256 => SubDAO) public subDAOs;
    mapping(uint256 => HolographicProposal) public proposals;
    mapping(address => mapping(uint256 => bool)) public hasVotedInSubDAO;
    mapping(address => uint256) public userStakes;
    
    Counters.Counter private subDAOCounter;
    Counters.Counter private proposalCounter;
    IERC20 public governanceToken;
    
    uint256 public constant MIN_STAKE = 1000;
    uint256 public constant MAX_SUB_DAOS = 100;
    uint256 public constant CONSENSUS_THRESHOLD = 8000; // 80%
    uint256 public constant SUB_DAO_VOTING_PERIOD = 3 days;
    uint256 public constant CONSENSUS_PERIOD = 5 days;
    
    event SubDAOCreated(uint256 indexed subDAOId, string name, address[] initialMembers);
    event MemberJoinedSubDAO(uint256 indexed subDAOId, address indexed member, uint256 weight);
    event MemberLeftSubDAO(uint256 indexed subDAOId, address indexed member);
    event HolographicProposalCreated(uint256 indexed proposalId, string title, uint256 targetSubDAO);
    event SubDAOVoted(uint256 indexed proposalId, uint256 indexed subDAOId, int256 outcome, uint256 stake);
    event HolographicConsensusReached(uint256 indexed proposalId, int256 consensus);
    event HolographicProposalExecuted(uint256 indexed proposalId);

    constructor(address _governanceToken) {
        governanceToken = IERC20(_governanceToken);
    }

    /**
     * @dev Create a new SubDAO
     */
    function createSubDAO(
        string memory _name,
        string memory _description,
        uint256 _requiredStake,
        address[] memory _initialMembers,
        uint256[] memory _initialWeights
    ) external returns (uint256) {
        require(_initialMembers.length == _initialWeights.length, "Array length mismatch");
        require(subDAOCounter.current() < MAX_SUB_DAOS, "Max SubDAOs reached");
        
        subDAOCounter.increment();
        uint256 subDAOId = subDAOCounter.current();
        
        SubDAO storage subDAO = subDAOs[subDAOId];
        subDAO.id = subDAOId;
        subDAO.name = _name;
        subDAO.description = _description;
        subDAO.requiredStake = _requiredStake;
        subDAO.memberCount = 0;
        subDAO.isActive = true;
        
        // Add initial members
        for (uint256 i = 0; i < _initialMembers.length; i++) {
            _joinSubDAO(subDAOId, _initialMembers[i], _initialWeights[i]);
        }
        
        emit SubDAOCreated(subDAOId, _name, _initialMembers);
        return subDAOId;
    }

    /**
     * @dev Join a SubDAO
     */
    function joinSubDAO(uint256 _subDAOId, uint256 _weight) external nonReentrant {
        SubDAO storage subDAO = subDAOs[_subDAOId];
        require(subDAO.isActive, "SubDAO not active");
        require(!subDAO.isMember[msg.sender], "Already member");
        require(_weight >= subDAO.requiredStake, "Insufficient weight");
        
        require(
            governanceToken.transferFrom(msg.sender, address(this), _weight),
            "Token transfer failed"
        );
        
        _joinSubDAO(_subDAOId, msg.sender, _weight);
        
        emit MemberJoinedSubDAO(_subDAOId, msg.sender, _weight);
    }

    /**
     * @dev Leave a SubDAO
     */
    function leaveSubDAO(uint256 _subDAOId) external nonReentrant {
        SubDAO storage subDAO = subDAOs[_subDAOId];
        require(subDAO.isMember[msg.sender], "Not a member");
        
        SubDAOMember storage member = subDAO.members[msg.sender];
        uint256 stakeToReturn = member.weight;
        
        // Remove member
        delete subDAO.members[msg.sender];
        delete subDAO.isMember[msg.sender];
        subDAO.memberCount--;
        
        // Return stake
        require(
            governanceToken.transfer(msg.sender, stakeToReturn),
            "Transfer failed"
        );
        
        emit MemberLeftSubDAO(_subDAOId, msg.sender);
    }

    /**
     * @dev Create holographic proposal
     */
    function createHolographicProposal(
        string memory _title,
        string memory _description,
        uint256 _requiredSubDAOs,
        uint256 _targetSubDAO
    ) external onlyOwner returns (uint256) {
        proposalCounter.increment();
        uint256 proposalId = proposalCounter.current();
        
        proposals[proposalId] = HolographicProposal({
            id: proposalId,
            title: _title,
            description: _description,
            submissionTime: block.timestamp,
            subDAOProposalEndTime: block.timestamp + SUB_DAO_VOTING_PERIOD,
            consensusEndTime: block.timestamp + CONSENSUS_PERIOD,
            requiredSubDAOs: _requiredSubDAOs,
            targetSubDAO: _targetSubDAO,
            consensusReached: false,
            executed: false,
            finalConsensus: 0
        });
        
        emit HolographicProposalCreated(proposalId, _title, _targetSubDAO);
        return proposalId;
    }

    /**
     * @dev Vote within a SubDAO on holographic proposal
     */
    function subDAOVote(
        uint256 _proposalId,
        int256 _choice,
        uint256 _stakeAmount
    ) external {
        require(_choice >= -1 && _choice <= 1, "Invalid choice");
        
        HolographicProposal storage proposal = proposals[_proposalId];
        require(block.timestamp <= proposal.subDAOProposalEndTime, "SubDAO voting ended");
        require(proposal.targetSubDAO > 0, "Invalid target SubDAO");
        
        SubDAO storage subDAO = subDAOs[proposal.targetSubDAO];
        require(subDAO.isMember[msg.sender], "Not a member of target SubDAO");
        require(!hasVotedInSubDAO[msg.sender][_proposalId], "Already voted");
        require(_stakeAmount > 0, "Must stake tokens");
        
        // Update proposal data
        proposal.subDAOOutcomes[proposal.targetSubDAO] += int256(_stakeAmount) * _choice;
        proposal.subDAOStakes[proposal.targetSubDAO] += _stakeAmount;
        
        hasVotedInSubDAO[msg.sender][_proposalId] = true;
        
        // Update member reputation
        subDAO.members[msg.sender].reputationScore = Math.min(
            subDAO.members[msg.sender].reputationScore + 10,
            1000
        );
        
        emit SubDAOVoted(_proposalId, proposal.targetSubDAO, _choice, _stakeAmount);
    }

    /**
     * @dev Reach holographic consensus
     */
    function reachHolographicConsensus(uint256 _proposalId) external {
        HolographicProposal storage proposal = proposals[_proposalId];
        require(!proposal.consensusReached, "Consensus already reached");
        require(block.timestamp > proposal.subDAOProposalEndTime, "SubDAO voting not ended");
        require(block.timestamp <= proposal.consensusEndTime, "Consensus period ended");
        
        uint256 participatingSubDAOs = _countParticipatingSubDAOs(_proposalId);
        require(participatingSubDAOs >= proposal.requiredSubDAOs, "Insufficient participation");
        
        // Calculate holographic consensus using weighted voting across all SubDAOs
        int256 totalWeightedOutcome = _calculateWeightedOutcome(_proposalId);
        uint256 totalStake = _calculateTotalStake(_proposalId);
        
        int256 consensus = totalWeightedOutcome * 10000 / int256(totalStake);
        require(Math.abs(consensus) >= int256(CONSENSUS_THRESHOLD), "Consensus threshold not met");
        
        proposal.consensusReached = true;
        proposal.finalConsensus = consensus;
        
        emit HolographicConsensusReached(_proposalId, consensus);
    }

    /**
     * @dev Execute holographic proposal
     */
    function executeHolographicProposal(uint256 _proposalId) external {
        HolographicProposal storage proposal = proposals[_proposalId];
        require(!proposal.executed, "Already executed");
        require(proposal.consensusReached, "Consensus not reached");
        require(block.timestamp > proposal.consensusEndTime, "Consensus period not ended");
        
        proposal.executed = true;
        
        if (proposal.finalConsensus > 0) {
            _executeProposalActions(_proposalId);
        }
        
        emit HolographicProposalExecuted(_proposalId);
    }

    /**
     * @dev Internal function to join SubDAO
     */
    function _joinSubDAO(uint256 _subDAOId, address _member, uint256 _weight) internal {
        SubDAO storage subDAO = subDAOs[_subDAOId];
        
        subDAO.members[_member] = SubDAOMember({
            member: _member,
            weight: _weight,
            lastActivity: block.timestamp,
            isActive: true,
            reputationScore: 500 // Initial neutral score
        });
        
        subDAO.isMember[_member] = true;
        subDAO.memberCount++;
        
        userStakes[_member] += _weight;
    }

    /**
     * @dev Count participating SubDAOs in proposal
     */
    function _countParticipatingSubDAOs(uint256 _proposalId) internal view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 1; i <= subDAOCounter.current(); i++) {
            if (subDAOs[i].isActive && proposals[_proposalId].subDAOStakes[i] > 0) {
                count++;
            }
        }
        return count;
    }

    /**
     * @dev Calculate weighted outcome across all SubDAOs
     */
    function _calculateWeightedOutcome(uint256 _proposalId) internal view returns (int256) {
        int256 totalOutcome = 0;
        
        for (uint256 i = 1; i <= subDAOCounter.current(); i++) {
            if (subDAOs[i].isActive) {
                SubDAO storage subDAO = subDAOs[i];
                int256 subDAOOutcome = proposals[_proposalId].subDAOOutcomes[i];
                uint256 subDAOStake = proposals[_proposalId].subDAOStakes[i];
                
                // Weight by SubDAO size and activity
                uint256 weight = subDAO.memberCount * subDAOStake / subDAO.requiredStake;
                totalOutcome += subDAOOutcome * int256(weight);
            }
        }
        
        return totalOutcome;
    }

    /**
     * @dev Calculate total stake in proposal
     */
    function _calculateTotalStake(uint256 _proposalId) internal view returns (uint256) {
        uint256 total = 0;
        for (uint256 i = 1; i <= subDAOCounter.current(); i++) {
            total += proposals[_proposalId].subDAOStakes[i];
        }
        return total;
    }

    /**
     * @dev Internal execution function
     */
    function _executeProposalActions(uint256 _proposalId) internal {
        // Implementation for executing successful holographic proposals
    }

    /**
     * @dev Get SubDAO member information
     */
    function getSubDAOMember(uint256 _subDAOId, address _member) external view returns (
        SubDAOMember memory memberInfo
    ) {
        return subDAOs[_subDAOId].members[_member];
    }

    /**
     * @dev Get proposal consensus progress
     */
    function getProposalProgress(uint256 _proposalId) external view returns (
        bool consensusReached,
        int256 finalConsensus,
        uint256 participatingSubDAOs
    ) {
        HolographicProposal storage proposal = proposals[_proposalId];
        return (
            proposal.consensusReached,
            proposal.finalConsensus,
            _countParticipatingSubDAOs(_proposalId)
        );
    }

    /**
     * @dev Emergency pause
     */
    bool public paused = false;
    
    modifier whenNotPaused() {
        require(!paused, "Contract paused");
        _;
    }

    function pause() external onlyOwner {
        paused = true;
    }

    function unpause() external onlyOwner {
        paused = false;
    }
}

// Math library
library Math {
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
    
    function max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a : b;
    }
    
    function abs(int256 x) internal pure returns (uint256) {
        return x >= 0 ? uint256(x) : uint256(-x);
    }
}