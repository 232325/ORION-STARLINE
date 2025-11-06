// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

import "../interfaces/IVoting.sol";

/**
 * @title Voting Contract - Turli Xil Ovoz Berish Mexanizmlari
 * @notice Token-weighted, quadratic, delegation-based va boshqa ovoz berish turlari
 */
contract Voting is IVoting, Ownable, ReentrancyGuard, Pausable {
    using SafeMath for uint256;
    using ECDSA for bytes32;

    // Strukturalar
    mapping(uint256 => Ballot) public ballots;
    mapping(uint256 => Delegation) public delegations;
    mapping(uint256 => Snapshot) public snapshots;
    mapping(uint256 => VotingConfig) public votingConfigs;
    mapping(uint256 => VotingResult) public votingResults;
    
    // Multi-phase voting uchun
    mapping(uint256 => mapping(uint256 => PhaseInfo)) public phaseInfo;
    mapping(uint256 => uint256) public currentPhase;
    
    // Anti-capture mexanizmlari
    mapping(address => uint256) public delegationWeight;
    mapping(address => mapping(uint256 => bool)) public whaleControlCheck;
    mapping(uint256 => uint256) public timeLockEnd;
    
    // Settings
    uint256 public constant MAX_DELEGATION_WEIGHT = 1000; // 1000x weight cap
    uint256 public constant MAX_QUADRATIC_VOTES = 100000; // 100k votes max
    uint256 public delegationGracePeriod = 86400; // 1 day
    
    // Events
    event DelegationCapUpdated(address indexed delegatee, uint256 oldCap, uint256 newCap);
    event QuadraticLimitUpdated(uint256 oldLimit, uint256 newLimit);
    event TimeLockActivated(uint256 indexed proposalId, address indexed target, uint256 endTime);
    event AntiCaptureActivated(uint256 indexed proposalId, address indexed trigger);
    event PhaseStarted(uint256 indexed proposalId, uint256 indexed phase, string phaseName, uint256 endTime);

    // Modifiers
    modifier validProposal(uint256 _proposalId) {
        require(_proposalId > 0 && _proposalId <= getProposalCount(), "Invalid proposal");
        _;
    }

    modifier onlyProposalCreator(uint256 _proposalId) {
        // This would typically check against the proposal contract
        require(true, "Only proposal creator"); // Simplified
        _;
    }

    modifier notTimeLocked(uint256 _proposalId) {
        require(block.timestamp > timeLockEnd[_proposalId], "Time locked");
        _;
    }

    constructor() {
        // Initialize
    }

    // ===== BASIC VOTING =====

    /**
     * @dev Oddiy ovoz berish
     */
    function castVote(
        uint256 _proposalId,
        uint8 _support,
        bytes memory _signature
    ) external payable override validProposal(_proposalId) notTimeLocked(_proposalId) nonReentrant whenNotPaused {
        require(_support <= 2, "Invalid support value");
        
        Ballot storage ballot = ballots[uint256(keccak256(abi.encode(_proposalId, msg.sender)))];
        require(ballot.votingPower == 0, "Already voted");
        
        VotingConfig memory config = votingConfigs[_proposalId];
        require(config.mechanism != VotingMechanism.Uninitialized, "No voting config");
        
        uint256 votingPower = getVotingPower(msg.sender, _proposalId);
        require(votingPower > 0, "No voting power");
        
        // Store ballot
        ballot = Ballot({
            proposalId: _proposalId,
            voter: msg.sender,
            support: _support,
            votingPower: votingPower,
            timestamp: block.timestamp,
            signature: _signature,
            isDelegated: false
        });
        
        // Apply vote based on mechanism
        if (config.mechanism == VotingMechanism.Quadratic) {
            _applyQuadraticVote(_proposalId, _support, votingPower, _signature);
        } else if (config.mechanism == VotingMechanism.SimpleMajority) {
            _applySimpleVote(_proposalId, _support, votingPower);
        } else if (config.mechanism == VotingMechanism.TokenWeighted) {
            _applyTokenWeightedVote(_proposalId, _support, votingPower);
        }
        
        // Update result
        _updateVotingResult(_proposalId, _support, votingPower);
        
        emit VoteCast(msg.sender, _proposalId, _support, votingPower);
    }

    /**
     * @dev Delegatsiya bilan ovoz berish
     */
    function castVoteWithDelegation(
        uint256 _proposalId,
        uint8 _support
    ) external override validProposal(_proposalId) notTimeLocked(_proposalId) nonReentrant whenNotPaused {
        require(_support <= 2, "Invalid support value");
        
        address delegatee = getDelegatedTo(msg.sender);
        require(delegatee != address(0), "No delegation");
        
        // Check if delegatee has voted
        bytes32 ballotKey = keccak256(abi.encode(_proposalId, delegatee));
        Ballot storage delegateeBallot = ballots[uint256(ballotKey)];
        
        require(delegateeBallot.votingPower > 0, "Delegatee hasn't voted");
        
        uint256 delegationPower = getDelegatedVotingPower(msg.sender);
        require(delegationPower > 0, "No delegated power");
        
        // Apply the vote
        _updateVotingResult(_proposalId, _support, delegationPower);
        
        // Store ballot for the original voter
        Ballot storage ballot = ballots[uint256(keccak256(abi.encode(_proposalId, msg.sender)))];
        ballot = Ballot({
            proposalId: _proposalId,
            voter: msg.sender,
            support: _support,
            votingPower: delegationPower,
            timestamp: block.timestamp,
            signature: "",
            isDelegated: true
        });
        
        emit VoteCast(msg.sender, _proposalId, _support, delegationPower);
    }

    // ===== DELEGATION MANAGEMENT =====

    /**
     * @dev Ovoz topshirish (delegatsiya)
     */
    function delegateVoting(address _delegatee) external override nonReentrant whenNotPaused {
        require(_delegatee != msg.sender, "Cannot delegate to self");
        require(_delegatee != address(0), "Invalid delegatee");
        
        address currentDelegate = getDelegatedTo(msg.sender);
        
        // Remove old delegation
        if (currentDelegate != address(0)) {
            _revokeOldDelegation(currentDelegate);
        }
        
        // Set new delegation
        _setNewDelegation(_delegatee);
        
        emit DelegationCreated(msg.sender, _delegatee, getVotingPower(msg.sender, 0));
    }

    /**
     * @dev Delegatsiyani bekor qilish
     */
    function revokeDelegation(address _delegator) external override nonReentrant whenNotPaused {
        require(_delegator != msg.sender, "Cannot revoke own delegation");
        require(getDelegatedTo(_delegator) == msg.sender, "Not your delegatee");
        
        _revokeOldDelegation(msg.sender);
        emit DelegationRevoked(_delegator, msg.sender);
    }

    /**
     * @dev To'plamli delegatsiya
     */
    function batchDelegateVoting(
        address[] memory _delegatees, 
        uint256[] memory _weights
    ) external override nonReentrant whenNotPaused {
        require(_delegatees.length == _weights.length, "Array length mismatch");
        require(_delegatees.length <= 10, "Too many delegates");
        
        uint256 totalWeight = 0;
        for (uint256 i = 0; i < _weights.length; i++) {
            require(_weights[i] > 0, "Invalid weight");
            totalWeight = totalWeight.add(_weights[i]);
        }
        require(totalWeight <= 10000, "Total weight exceeds 100%");
        
        // Remove current delegation if exists
        address currentDelegate = getDelegatedTo(msg.sender);
        if (currentDelegate != address(0)) {
            _revokeOldDelegation(currentDelegate);
        }
        
        // Set new delegations with weights
        for (uint256 i = 0; i < _delegatees.length; i++) {
            delegationWeight[msg.sender] = delegationWeight[msg.sender].add(_weights[i]);
            // Store delegation info (simplified)
        }
        
        emit DelegationCreated(msg.sender, address(0), getVotingPower(msg.sender, 0));
    }

    // ===== SNAPSHOT MANAGEMENT =====

    /**
     * @dev Snapshot yaratish (voting power hisobga olish uchun)
     */
    function createSnapshot(uint256 _proposalId) external override validProposal(_proposalId) onlyProposalCreator(_proposalId) {
        require(snapshots[_proposalId].blockNumber == 0, "Snapshot already exists");
        
        Snapshot storage snapshot = snapshots[_proposalId];
        snapshot.blockNumber = block.number;
        snapshot.totalVotingPower = getTotalVotingPower();
        
        // Record voting power for all members (simplified)
        // In practice, this would iterate through members or use an event-driven approach
        
        emit SnapshotCreated(_proposalId, block.number, snapshot.totalVotingPower);
    }

    /**
     * @dev Muayyan block number da voting power olish
     */
    function getVotingPowerAt(address _member, uint256 _blockNumber) external view override returns (uint256) {
        // Simplified implementation
        // In practice, you'd need to track historical voting power changes
        return getVotingPower(_member, 0); // Current power as fallback
    }

    /**
     * @dev Muayyan block number da umumiy voting power
     */
    function getTotalVotingPowerAt(uint256 _blockNumber) external view override returns (uint256) {
        // Simplified implementation
        return getTotalVotingPower();
    }

    // ===== VOTING RESULTS =====

    /**
     * @dev Ovoz berish natijasini olish
     */
    function getVotingResult(uint256 _proposalId) public view override validProposal(_proposalId) returns (VotingResult memory) {
        return votingResults[_proposalId];
    }

    /**
     * @dev Ballot ma'lumotlarini olish
     */
    function getBallot(uint256 _proposalId, address _voter) external view override returns (Ballot memory) {
        return ballots[uint256(keccak256(abi.encode(_proposalId, _voter)))];
    }

    /**
     * @dev Ovoz berganligini tekshirish
     */
    function hasVoted(uint256 _proposalId, address _voter) external view override returns (bool) {
        Ballot memory ballot = ballots[uint256(keccak256(abi.encode(_proposalId, _voter)))];
        return ballot.votingPower > 0;
    }

    // ===== CONFIGURATION =====

    /**
     * @dev Ovoz berish konfiguratsiyasini o'rnatish
     */
    function setVotingConfig(uint256 _proposalId, VotingConfig memory _config) external override validProposal(_proposalId) onlyProposalCreator(_proposalId) {
        require(_config.duration >= 86400, "Minimum 1 day duration");
        require(_config.quorum > 0, "Quorum must be positive");
        require(_config.threshold > 0 && _config.threshold <= 10000, "Threshold must be between 1 and 10000 basis points");
        
        votingConfigs[_proposalId] = _config;
    }

    /**
     * @dev Ovoz berish konfiguratsiyasini olish
     */
    function getVotingConfig(uint256 _proposalId) external view override validProposal(_proposalId) returns (VotingConfig memory) {
        return votingConfigs[_proposalId];
    }

    // ===== ANTI-CAPTURE MECHANISMS =====

    /**
     * @dev Delegatsiya limitlarini tekshirish
     */
    function enforceDelegationLimits(address _delegatee, uint256 _proposalId) external view override returns (bool) {
        uint256 totalWeight = getDelegatedWeight(_delegatee, _proposalId);
        return totalWeight <= MAX_DELEGATION_WEIGHT;
    }

    /**
     * @dev Whale control tekshirish
     */
    function checkWhaleControl(uint256 _proposalId) external view override returns (bool) {
        VotingResult memory result = getVotingResult(_proposalId);
        if (result.totalVotingPower == 0) return false;
        
        uint256 whalePercentage = (result.votesFor * 10000) / result.totalVotingPower;
        return whalePercentage > 5000; // More than 50% from single entity
    }

    /**
     * @dev Time lock aktivatsiya
     */
    function activateTimeLock(address _target, uint256 _delay) external override onlyOwner {
        uint256 proposalId = getNextProposalId();
        timeLockEnd[proposalId] = block.timestamp.add(_delay);
        
        emit TimeLockActivated(proposalId, _target, timeLockEnd[proposalId]);
    }

    // ===== MULTI-PHASE VOTING =====

    /**
     * @dev Yangi bosqich boshlash
     */
    function startPhase(
        uint256 _proposalId,
        uint256 _phase,
        string memory _phaseName,
        uint256 _duration
    ) external override validProposal(_proposalId) onlyProposalCreator(_proposalId) {
        require(_phase > 0, "Invalid phase");
        require(_duration >= 3600, "Minimum 1 hour duration"); // Minimum 1 hour
        
        phaseInfo[_proposalId][_phase] = PhaseInfo({
            name: _phaseName,
            endTime: block.timestamp.add(_duration),
            votesFor: 0,
            votesAgainst: 0,
            votesAbstain: 0,
            active: true
        });
        
        currentPhase[_proposalId] = _phase;
        
        emit PhaseStarted(_proposalId, _phase, _phaseName, block.timestamp.add(_duration));
    }

    /**
     * @dev Keyingi bosqichga o'tish
     */
    function advancePhase(uint256 _proposalId) external override validProposal(_proposalId) onlyProposalCreator(_proposalId) {
        uint256 current = currentPhase[_proposalId];
        require(current > 0, "No active phase");
        require(block.timestamp >= phaseInfo[_proposalId][current].endTime, "Phase not ended");
        
        // Finalize current phase
        phaseInfo[_proposalId][current].active = false;
        currentPhase[_proposalId] = current + 1;
    }

    /**
     * @dev Joriy bosqich ma'lumotlarini olish
     */
    function getCurrentPhase(uint256 _proposalId) external view override returns (uint256 phase, string memory name, uint256 endTime) {
        phase = currentPhase[_proposalId];
        if (phase == 0) return (0, "", 0);
        
        PhaseInfo memory info = phaseInfo[_proposalId][phase];
        return (phase, info.name, info.endTime);
    }

    // ===== STATISTICS =====

    /**
     * @dev Ovoz berish statistikasi
     */
    function getVotingStats(uint256 _proposalId) external view override returns (
        uint256 totalVoters,
        uint256 delegationCount,
        uint256 quadraticVoters,
        uint256 participationRate
    ) {
        // Simplified statistics calculation
        VotingConfig memory config = votingConfigs[_proposalId];
        uint256 totalVotingPower = getTotalVotingPower();
        
        // Calculate participation rate
        if (totalVotingPower > 0) {
            participationRate = (getVotesCast(_proposalId) * 10000) / totalVotingPower;
        }
        
        return (getVotesCast(_proposalId), getDelegationCount(_proposalId), getQuadraticVoteCount(_proposalId), participationRate);
    }

    // ===== EMERGENCY FUNCTIONS =====

    /**
     * @dev Ovoz berishni to'xtatish
     */
    function emergencyStopVoting(uint256 _proposalId) external override onlyOwner {
        _pause();
        emit AntiCaptureActivated(_proposalId, msg.sender);
    }

    /**
     * @dev Ovoz berishni davom ettirish
     */
    function resumeVoting(uint256 _proposalId) external override onlyOwner {
        _unpause();
    }

    // ===== INTERNAL FUNCTIONS =====

    /**
     * @dev Oddiy ovoz berish
     */
    function _applySimpleVote(uint256 _proposalId, uint8 _support, uint256 _votingPower) internal {
        // Simple majority logic - no special calculations needed
    }

    /**
     * @dev Token-weighted ovoz berish
     */
    function _applyTokenWeightedVote(uint256 _proposalId, uint8 _support, uint256 _votingPower) internal {
        // Token-weighted logic - voting power is already weighted by token holdings
    }

    /**
     * @dev Quadratic ovoz berish
     */
    function _applyQuadraticVote(
        uint256 _proposalId,
        uint8 _support,
        uint256 _votingPower,
        bytes memory _signature
    ) internal {
        require(msg.value > 0, "Quadratic voting requires payment");
        require(_votingPower <= MAX_QUADRATIC_VOTES, "Exceeds quadratic limit");
        
        // Verify signature for quadratic voting (simplified)
        bytes32 message = keccak256(abi.encodePacked(_proposalId, _support, msg.value));
        require(message.recover(_signature) == msg.sender, "Invalid signature");
        
        // Apply quadratic cost: cost = votingPower^2
        uint256 cost = _votingPower.mul(_votingPower);
        require(msg.value >= cost, "Insufficient payment");
        
        // Refund excess payment
        if (msg.value > cost) {
            payable(msg.sender).transfer(msg.value.sub(cost));
        }
    }

    /**
     * @dev Ovoz berish natijasini yangilash
     */
    function _updateVotingResult(uint256 _proposalId, uint8 _support, uint256 _votingPower) internal {
        if (votingResults[_proposalId].proposalId == 0) {
            votingResults[_proposalId] = VotingResult({
                proposalId: _proposalId,
                votesFor: 0,
                votesAgainst: 0,
                votesAbstain: 0,
                delegationVotes: 0,
                totalVotingPower: getTotalVotingPower(),
                quorumReached: false,
                thresholdReached: false,
                executed: false,
                finalBlock: 0
            });
        }
        
        VotingResult storage result = votingResults[_proposalId];
        
        if (_support == 0) {
            result.votesAgainst = result.votesAgainst.add(_votingPower);
        } else if (_support == 1) {
            result.votesFor = result.votesFor.add(_votingPower);
        } else {
            result.votesAbstain = result.votesAbstain.add(_votingPower);
        }
        
        // Check if quorum and threshold are reached
        VotingConfig memory config = votingConfigs[_proposalId];
        result.quorumReached = result.votesFor >= config.quorum;
        result.thresholdReached = result.votesFor >= (result.totalVotingPower * config.threshold / 10000);
        
        emit VotingResultPublished(_proposalId, result);
    }

    /**
     * @dev Eski delegatsiyani bekor qilish
     */
    function _revokeOldDelegation(address _currentDelegate) internal {
        // Simplified implementation
        delegationWeight[msg.sender] = 0;
    }

    /**
     * @dev Yangi delegatsiya o'rnatish
     */
    function _setNewDelegation(address _delegatee) internal {
        // Simplified implementation
        delegationWeight[msg.sender] = 10000; // 100%
    }

    // ===== UTILITY FUNCTIONS =====

    function getDelegatedTo(address _delegator) internal view returns (address) {
        // Simplified implementation
        return address(0);
    }

    function getDelegatedVotingPower(address _delegator) internal view returns (uint256) {
        // Simplified implementation
        return getVotingPower(_delegator, 0);
    }

    function getVotingPower(address _member, uint256 _proposalId) internal view returns (uint256) {
        // This would integrate with the DAO contract
        return 1000; // Simplified
    }

    function getTotalVotingPower() internal view returns (uint256) {
        // This would integrate with the DAO contract
        return 1000000; // Simplified
    }

    function getNextProposalId() internal pure returns (uint256) {
        return 1; // Simplified
    }

    function getProposalCount() internal pure returns (uint256) {
        return 1000; // Simplified
    }

    function getDelegatedWeight(address _delegatee, uint256 _proposalId) internal view returns (uint256) {
        return delegationWeight[_delegatee];
    }

    function getVotesCast(uint256 _proposalId) internal view returns (uint256) {
        VotingResult memory result = getVotingResult(_proposalId);
        return result.votesFor.add(result.votesAgainst).add(result.votesAbstain);
    }

    function getDelegationCount(uint256 _proposalId) internal view returns (uint256) {
        return 0; // Simplified
    }

    function getQuadraticVoteCount(uint256 _proposalId) internal view returns (uint256) {
        return 0; // Simplified
    }
}