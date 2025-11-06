// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title ConvictionVoting
 * @dev Conviction-based voting for long-term decisions
 * @author Advanced Voting Systems
 */
contract ConvictionVoting is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;

    struct ConvictionStake {
        uint256 amount;
        uint256 lastActionTime;
        uint256 convictionLevel;
        uint256 totalStakedTime;
        bool isActive;
    }

    struct LongTermProposal {
        uint256 id;
        string title;
        string description;
        uint256 submissionTime;
        uint256 votingStartTime;
        uint256 votingEndTime;
        uint256 requiredConviction;
        int256 outcome;
        bool executed;
        mapping(address => int256) votes;
        mapping(address => uint256) convictionSpent;
        uint256 totalConvictionSpent;
        mapping(int256 => uint256) voteCounts;
    }

    struct ConvictionVote {
        uint256 proposalId;
        address voter;
        uint256 convictionSpent;
        int256 voteChoice;
        uint256 timestamp;
        uint256 convictionGained;
    }

    mapping(address => ConvictionStake) public userStakes;
    mapping(uint256 => LongTermProposal) public proposals;
    mapping(address => ConvictionVote[]) public convictionHistory;
    mapping(address => mapping(address => uint256)) public delegationConviction;
    
    Counters.Counter private proposalCounter;
    IERC20 public stakingToken;
    
    uint256 public constant CONVICTION_DECAY_RATE = 1000; // 1% per day
    uint256 public constant MIN_STAKING_DURATION = 30 days;
    uint256 public constant MAX_CONVICTION_LEVEL = 100;
    uint256 public constant VOTING_PERIOD = 14 days;
    
    event StakeAdded(address indexed user, uint256 amount, uint256 newConviction);
    event StakeWithdrawn(address indexed user, uint256 amount, uint256 convictionLost);
    event LongTermProposalCreated(uint256 indexed proposalId, string title, uint256 requiredConviction);
    event ConvictionVoted(address indexed voter, uint256 indexed proposalId, int256 choice, uint256 convictionSpent);
    event LongTermProposalExecuted(uint256 indexed proposalId, int256 outcome);

    constructor(address _stakingToken) {
        stakingToken = IERC20(_stakingToken);
    }

    /**
     * @dev Add stake to build conviction
     */
    function addStake(uint256 _amount) external nonReentrant {
        require(_amount > 0, "Amount must be positive");
        
        ConvictionStake storage stake = userStakes[msg.sender];
        
        // Calculate conviction decay
        if (stake.isActive) {
            uint256 decayPeriod = block.timestamp - stake.lastActionTime;
            uint256 decayAmount = (stake.convictionLevel * decayPeriod * CONVICTION_DECAY_RATE) / (365 days);
            if (decayAmount < stake.convictionLevel) {
                stake.convictionLevel -= decayAmount;
            } else {
                stake.convictionLevel = 0;
            }
        }
        
        // Add new stake
        require(
            stakingToken.transferFrom(msg.sender, address(this), _amount),
            "Token transfer failed"
        );
        
        stake.amount += _amount;
        stake.totalStakedTime += block.timestamp;
        stake.lastActionTime = block.timestamp;
        
        // Increase conviction based on staking duration
        uint256 convictionIncrease = _calculateConvictionIncrease(_amount);
        stake.convictionLevel = Math.min(stake.convictionLevel + convictionIncrease, MAX_CONVICTION_LEVEL);
        stake.isActive = true;
        
        emit StakeAdded(msg.sender, _amount, stake.convictionLevel);
    }

    /**
     * @dev Withdraw stake with conviction penalty
     */
    function withdrawStake(uint256 _amount) external nonReentrant {
        ConvictionStake storage stake = userStakes[msg.sender];
        require(_amount <= stake.amount, "Insufficient stake");
        require(stake.isActive, "No active stake");
        
        uint256 convictionLost = (stake.convictionLevel * _amount) / stake.amount;
        
        stake.amount -= _amount;
        stake.convictionLevel -= convictionLost;
        stake.lastActionTime = block.timestamp;
        
        if (stake.amount == 0) {
            stake.isActive = false;
        }
        
        require(
            stakingToken.transfer(msg.sender, _amount),
            "Token transfer failed"
        );
        
        emit StakeWithdrawn(msg.sender, _amount, convictionLost);
    }

    /**
     * @dev Create long-term proposal requiring high conviction
     */
    function createLongTermProposal(
        string memory _title,
        string memory _description,
        uint256 _requiredConviction
    ) external returns (uint256) {
        // Only users with sufficient conviction can create proposals
        require(
            getUserConviction(msg.sender) >= _requiredConviction,
            "Insufficient conviction"
        );
        
        proposalCounter.increment();
        uint256 proposalId = proposalCounter.current();
        
        proposals[proposalId].id = proposalId;
        proposals[proposalId].title = _title;
        proposals[proposalId].description = _description;
        proposals[proposalId].submissionTime = block.timestamp;
        proposals[proposalId].votingStartTime = block.timestamp + 7 days; // Discussion period
        proposals[proposalId].votingEndTime = block.timestamp + 21 days; // Long voting period
        proposals[proposalId].requiredConviction = _requiredConviction;
        proposals[proposalId].outcome = 0;
        proposals[proposalId].executed = false;
        
        emit LongTermProposalCreated(proposalId, _title, _requiredConviction);
        return proposalId;
    }

    /**
     * @dev Vote with conviction on long-term proposals
     */
    function convictionVote(
        uint256 _proposalId,
        int256 _choice,
        uint256 _convictionToSpend
    ) external nonReentrant {
        require(_choice >= -1 && _choice <= 1, "Invalid choice");
        
        LongTermProposal storage proposal = proposals[_proposalId];
        require(block.timestamp >= proposal.votingStartTime, "Voting not started");
        require(block.timestamp <= proposal.votingEndTime, "Voting ended");
        
        ConvictionStake storage stake = userStakes[msg.sender];
        require(stake.isActive, "No active stake");
        require(_convictionToSpend > 0, "Must spend conviction");
        
        uint256 availableConviction = getUserConviction(msg.sender);
        require(_convictionToSpend <= availableConviction, "Insufficient conviction");
        
        // Use conviction (reduces available conviction)
        stake.convictionLevel = Math.min(stake.convictionLevel - _convictionToSpend, MAX_CONVICTION_LEVEL);
        stake.lastActionTime = block.timestamp;
        
        // Record vote
        proposal.votes[msg.sender] += _choice;
        proposal.convictionSpent[msg.sender] += _convictionToSpend;
        proposal.totalConvictionSpent += _convictionToSpend;
        
        if (_choice != 0) {
            proposal.voteCounts[_choice] += _convictionToSpend;
        }
        
        // Record conviction history
        convictionHistory[msg.sender].push(ConvictionVote({
            proposalId: _proposalId,
            voter: msg.sender,
            convictionSpent: _convictionToSpend,
            voteChoice: _choice,
            timestamp: block.timestamp,
            convictionGained: _calculateConvictionGain(_convictionToSpend)
        }));
        
        emit ConvictionVoted(msg.sender, _proposalId, _choice, _convictionToSpend);
    }

    /**
     * @dev Execute long-term proposal
     */
    function executeLongTermProposal(uint256 _proposalId) external {
        LongTermProposal storage proposal = proposals[_proposalId];
        require(!proposal.executed, "Already executed");
        require(block.timestamp > proposal.votingEndTime, "Voting not ended");
        
        // Calculate weighted conviction result
        int256 yesConviction = int256(proposal.voteCounts[1]);
        int256 noConviction = int256(proposal.voteCounts[-1]);
        
        // Require minimum engagement
        require(
            proposal.totalConvictionSpent >= proposal.requiredConviction * 10,
            "Insufficient engagement"
        );
        
        int256 outcome = yesConviction > noConviction ? 1 : -1;
        proposal.outcome = outcome;
        proposal.executed = true;
        
        emit LongTermProposalExecuted(_proposalId, outcome);
        
        if (outcome > 0) {
            _executeProposal(_proposalId);
        }
    }

    /**
     * @dev Get user's current conviction level
     */
    function getUserConviction(address _user) public view returns (uint256) {
        ConvictionStake storage stake = userStakes[_user];
        if (!stake.isActive) return 0;
        
        uint256 decayPeriod = block.timestamp - stake.lastActionTime;
        uint256 currentConviction = stake.convictionLevel;
        
        if (decayPeriod > 0) {
            uint256 decayAmount = (stake.convictionLevel * decayPeriod * CONVICTION_DECAY_RATE) / (365 days);
            if (decayAmount < stake.convictionLevel) {
                currentConviction = stake.convictionLevel - decayAmount;
            }
        }
        
        return currentConviction;
    }

    /**
     * @dev Get conviction voting power (includes delegation)
     */
    function getConvictionPower(address _user) external view returns (uint256) {
        uint256 ownConviction = getUserConviction(_user);
        uint256 delegatedConviction = 0;
        
        // Sum delegated conviction
        for (uint256 i = 0; i < _delegators[_user].length; i++) {
            delegatedConviction += delegationConviction[_delegators[_user][i]][_user];
        }
        
        return ownConviction + delegatedConviction;
    }

    /**
     * @dev Calculate conviction increase for staking
     */
    function _calculateConvictionIncrease(uint256 _amount) internal pure returns (uint256) {
        // Conviction increases based on amount and commitment
        return (_amount * 10) / 1000; // 1% conviction per unit staked
    }

    /**
     * @dev Calculate conviction gain from voting
     */
    function _calculateConvictionGain(uint256 _convictionSpent) internal pure returns (uint256) {
        return (_convictionSpent * 5) / 1000; // 0.5% conviction gained from voting
    }

    /**
     * @dev Internal execution function
     */
    function _executeProposal(uint256 _proposalId) internal {
        // Implementation for executing successful proposals
        // Could include parameter changes, fund allocations, etc.
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

// Math library for conviction calculations
library Math {
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
}