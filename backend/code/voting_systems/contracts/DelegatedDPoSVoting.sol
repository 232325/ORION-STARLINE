// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title DelegatedDPoSVoting
 * @dev Delegated Proof of Stake voting system
 * @author Advanced Voting Systems
 */
contract DelegatedDPoSVoting is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;

    struct Validator {
        address validator;
        uint256 totalStake;
        uint256 delegationStake;
        uint256 ownStake;
        uint256 commissionRate;
        uint256 lastRewardTime;
        bool isActive;
        uint256 performanceScore;
        uint256 slashingEvents;
    }

    struct Delegator {
        address delegator;
        mapping(address => uint256) delegatedTo;
        uint256 totalDelegated;
        uint256 votingPower;
        uint256 lastActionTime;
        bool isActive;
    }

    struct DPoSProposal {
        uint256 id;
        string title;
        string description;
        uint256 startTime;
        uint256 endTime;
        uint256 quorum;
        int256 result;
        bool executed;
        mapping(address => int256) validatorVotes;
        mapping(address => uint256) validatorStakes;
        mapping(address => bool) hasVoted;
        uint256 totalValidatorStake;
        mapping(int256 => uint256) voteCounts;
    }

    mapping(address => Validator) public validators;
    mapping(address => Delegator) public delegators;
    mapping(uint256 => DPoSProposal) public proposals;
    mapping(address => mapping(address => bool)) public delegationActive;
    mapping(address => uint256) public rewards;
    
    Counters.Counter private proposalCounter;
    IERC20 public governanceToken;
    
    uint256 public constant MIN_VALIDATOR_STAKE = 10000;
    uint256 public constant MAX_VALIDATORS = 21;
    uint256 public constant COMMISSION_RATE = 1000; // 10%
    uint256 public constant SLASHING_PENALTY = 5000; // 50%
    uint256 public constant VOTING_PERIOD = 3 days;
    
    address[] public validatorList;
    address[] public activeValidators;
    
    event ValidatorRegistered(address indexed validator, uint256 stake);
    event DelegatorAdded(address indexed delegator, address indexed validator, uint256 amount);
    event DelegatorRemoved(address indexed delegator, address indexed validator, uint256 amount);
    event DPoSProposalCreated(uint256 indexed proposalId, string title);
    event ValidatorVoted(address indexed validator, uint256 indexed proposalId, int256 choice);
    event ProposalExecuted(uint256 indexed proposalId, int256 result);
    event RewardClaimed(address indexed user, uint256 amount);
    event SlashingEvent(address indexed validator, uint256 penaltyAmount);

    constructor(address _governanceToken) {
        governanceToken = IERC20(_governanceToken);
    }

    /**
     * @dev Register as validator
     */
    function registerValidator(uint256 _stakeAmount) external nonReentrant {
        require(!validators[msg.sender].isActive, "Already validator");
        require(_stakeAmount >= MIN_VALIDATOR_STAKE, "Insufficient stake");
        require(activeValidators.length < MAX_VALIDATORS, "Max validators reached");
        
        require(
            governanceToken.transferFrom(msg.sender, address(this), _stakeAmount),
            "Token transfer failed"
        );
        
        validators[msg.sender] = Validator({
            validator: msg.sender,
            totalStake: _stakeAmount,
            delegationStake: 0,
            ownStake: _stakeAmount,
            commissionRate: COMMISSION_RATE,
            lastRewardTime: block.timestamp,
            isActive: true,
            performanceScore: 1000, // Start with perfect score
            slashingEvents: 0
        });
        
        validatorList.push(msg.sender);
        activeValidators.push(msg.sender);
        
        emit ValidatorRegistered(msg.sender, _stakeAmount);
    }

    /**
     * @dev Add delegation to validator
     */
    function delegate(address _validator, uint256 _amount) external nonReentrant {
        require(validators[_validator].isActive, "Validator not active");
        require(_amount > 0, "Amount must be positive");
        require(!delegationActive[msg.sender][_validator], "Already delegated");
        
        require(
            governanceToken.transferFrom(msg.sender, address(this), _amount),
            "Token transfer failed"
        );
        
        // Update validator stats
        Validator storage validator = validators[_validator];
        validator.totalStake += _amount;
        validator.delegationStake += _amount;
        
        // Update delegator stats
        if (!delegators[msg.sender].isActive) {
            delegators[msg.sender] = Delegator({
                delegator: msg.sender,
                totalDelegated: 0,
                votingPower: 0,
                lastActionTime: block.timestamp,
                isActive: true
            });
        }
        
        Delegator storage delegator = delegators[msg.sender];
        delegator.delegatedTo[_validator] += _amount;
        delegator.totalDelegated += _amount;
        delegator.votingPower += _amount;
        
        delegationActive[msg.sender][_validator] = true;
        
        emit DelegatorAdded(msg.sender, _validator, _amount);
    }

    /**
     * @dev Remove delegation
     */
    function undelegate(address _validator, uint256 _amount) external nonReentrant {
        require(_amount > 0, "Amount must be positive");
        require(delegationActive[msg.sender][_validator], "Not delegated");
        
        Delegator storage delegator = delegators[msg.sender];
        require(
            _amount <= delegator.delegatedTo[_validator],
            "Insufficient delegation"
        );
        
        // Update validator stats
        Validator storage validator = validators[_validator];
        validator.totalStake -= _amount;
        validator.delegationStake -= _amount;
        
        // Update delegator stats
        delegator.delegatedTo[_validator] -= _amount;
        delegator.totalDelegated -= _amount;
        delegator.votingPower -= _amount;
        
        if (delegator.totalDelegated == 0) {
            delegator.isActive = false;
        }
        
        if (_amount == delegator.delegatedTo[_validator]) {
            delegationActive[msg.sender][_validator] = false;
        }
        
        require(
            governanceToken.transfer(msg.sender, _amount),
            "Token transfer failed"
        );
        
        emit DelegatorRemoved(msg.sender, _validator, _amount);
    }

    /**
     * @dev Create DPoS proposal
     */
    function createDPoSProposal(
        string memory _title,
        string memory _description,
        uint256 _quorum
    ) external onlyOwner returns (uint256) {
        proposalCounter.increment();
        uint256 proposalId = proposalCounter.current();
        
        proposals[proposalId] = DPoSProposal({
            id: proposalId,
            title: _title,
            description: _description,
            startTime: block.timestamp,
            endTime: block.timestamp + VOTING_PERIOD,
            quorum: _quorum,
            result: 0,
            executed: false,
            totalValidatorStake: 0
        });
        
        // Calculate initial validator stake
        for (uint256 i = 0; i < activeValidators.length; i++) {
            proposals[proposalId].totalValidatorStake += validators[activeValidators[i]].totalStake;
        }
        
        emit DPoSProposalCreated(proposalId, _title);
        return proposalId;
    }

    /**
     * @dev Vote on proposal (validators and their delegators)
     */
    function vote(uint256 _proposalId, int256 _choice) external {
        require(_choice >= -1 && _choice <= 1, "Invalid choice");
        
        DPoSProposal storage proposal = proposals[_proposalId];
        require(block.timestamp >= proposal.startTime, "Voting not started");
        require(block.timestamp <= proposal.endTime, "Voting ended");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        
        uint256 votingPower = _calculateVotingPower(msg.sender);
        require(votingPower > 0, "No voting power");
        
        proposal.hasVoted[msg.sender] = true;
        proposal.validatorVotes[msg.sender] = _choice;
        proposal.validatorStakes[msg.sender] = votingPower;
        
        if (_choice != 0) {
            proposal.voteCounts[_choice] += votingPower;
        }
        
        // Update performance score based on participation
        if (validators[msg.sender].isActive) {
            validators[msg.sender].performanceScore = Math.min(
                validators[msg.sender].performanceScore + 10,
                1000
            );
        }
        
        emit ValidatorVoted(msg.sender, _proposalId, _choice);
    }

    /**
     * @dev Execute DPoS proposal
     */
    function executeDPoSProposal(uint256 _proposalId) external {
        DPoSProposal storage proposal = proposals[_proposalId];
        require(!proposal.executed, "Already executed");
        require(block.timestamp > proposal.endTime, "Voting not ended");
        
        uint256 totalStake = _getTotalValidatorStake();
        uint256 quorumReached = (proposal.voteCounts[1] + proposal.voteCounts[-1]) * 10000 / totalStake;
        
        require(quorumReached >= proposal.quorum, "Quorum not reached");
        
        int256 yesVotes = int256(proposal.voteCounts[1]);
        int256 noVotes = int256(proposal.voteCounts[-1]);
        int256 result = yesVotes > noVotes ? 1 : -1;
        
        proposal.result = result;
        proposal.executed = true;
        
        // Slash validators who voted against majority
        if (result > 0) {
            _slashMinoryValidators(_proposalId);
        }
        
        // Distribute rewards
        _distributeRewards(_proposalId, result);
        
        emit ProposalExecuted(_proposalId, result);
        
        if (result > 0) {
            _executeProposalActions(_proposalId);
        }
    }

    /**
     * @dev Calculate voting power for address
     */
    function _calculateVotingPower(address _user) internal view returns (uint256) {
        uint256 power = 0;
        
        // Direct stake power
        if (validators[_user].isActive) {
            power += validators[_user].totalStake;
        }
        
        // Delegated power as delegator
        power += delegators[_user].votingPower;
        
        return power;
    }

    /**
     * @dev Get total validator stake
     */
    function _getTotalValidatorStake() internal view returns (uint256) {
        uint256 total = 0;
        for (uint256 i = 0; i < activeValidators.length; i++) {
            total += validators[activeValidators[i]].totalStake;
        }
        return total;
    }

    /**
     * @dev Slash minority validators
     */
    function _slashMinoryValidators(uint256 _proposalId) internal {
        DPoSProposal storage proposal = proposals[_proposalId];
        int256 result = proposal.result;
        
        for (uint256 i = 0; i < validatorList.length; i++) {
            address validator = validatorList[i];
            int256 vote = proposal.validatorVotes[validator];
            
            if (vote != 0 && vote != result) {
                // Slash 50% of validator's stake
                uint256 penalty = validators[validator].totalStake * SLASHING_PENALTY / 10000;
                validators[validator].totalStake -= penalty;
                validators[validator].slashingEvents += 1;
                
                // Reduce performance score
                validators[validator].performanceScore = Math.max(
                    validators[validator].performanceScore - 100,
                    100
                );
                
                emit SlashingEvent(validator, penalty);
            }
        }
    }

    /**
     * @dev Distribute rewards based on participation and performance
     */
    function _distributeRewards(uint256 _proposalId, int256 _result) internal {
        DPoSProposal storage proposal = proposals[_proposalId];
        uint256 totalRewardPool = _calculateRewardPool();
        
        for (uint256 i = 0; i < validatorList.length; i++) {
            address validator = validatorList[i];
            uint256 validatorReward = totalRewardPool * validators[validator].performanceScore / 1000;
            
            // Apply commission for delegators
            if (validators[validator].delegationStake > 0) {
                uint256 commission = validatorReward * validators[validator].commissionRate / 10000;
                validatorReward -= commission;
            }
            
            rewards[validator] += validatorReward;
        }
    }

    /**
     * @dev Calculate reward pool size
     */
    function _calculateRewardPool() internal pure returns (uint256) {
        // Dynamic reward pool calculation
        return 1000 * 10**18; // Example: 1000 tokens
    }

    /**
     * @dev Claim rewards
     */
    function claimRewards() external nonReentrant {
        uint256 reward = rewards[msg.sender];
        require(reward > 0, "No rewards to claim");
        
        rewards[msg.sender] = 0;
        require(
            governanceToken.transfer(msg.sender, reward),
            "Transfer failed"
        );
        
        emit RewardClaimed(msg.sender, reward);
    }

    /**
     * @dev Internal execution function
     */
    function _executeProposalActions(uint256 _proposalId) internal {
        // Implementation for executing successful proposals
    }

    /**
     * @dev Get active validator count
     */
    function getActiveValidatorCount() external view returns (uint256) {
        return activeValidators.length;
    }

    /**
     * @dev Get validator voting power
     */
    function getValidatorVotingPower(address _validator) external view returns (uint256) {
        return _calculateVotingPower(_validator);
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
}