// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title QuadraticVoting
 * @dev Quadratic voting implementation where voting power is square root of tokens
 * @author Advanced Voting Systems
 */
contract QuadraticVoting is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;

    struct QuadraticVote {
        uint256 proposalId;
        address voter;
        uint256 tokensSpent;
        int256 voteChoice; // -1 for no, 0 for abstain, 1 for yes
        uint256 timestamp;
        bool executed;
    }

    struct Proposal {
        uint256 id;
        string title;
        string description;
        uint256 startTime;
        uint256 endTime;
        uint256 minTokensRequired;
        int256 result; // -1 to 1 scale
        bool executed;
        mapping(address => uint256) votes;
        mapping(address => uint256) tokensSpent;
        uint256 totalTokensSpent;
        mapping(int256 => uint256) voteCounts; // -1, 0, 1
        Counters.Counter voterCount;
    }

    mapping(uint256 => Proposal) public proposals;
    mapping(address => QuadraticVote[]) public voterHistory;
    mapping(address => uint256) public lastVoteBlock;
    
    Counters.Counter private proposalCounter;
    IERC20 public governanceToken;
    
    uint256 public constant VOTING_PERIOD = 7 days;
    uint256 public constant MIN_TOKEN_THRESHOLD = 1000;
    uint256 public constant MAX_VOTES_PER_PROPOSAL = 1000;
    
    event ProposalCreated(uint256 indexed proposalId, string title, uint256 endTime);
    event Voted(address indexed voter, uint256 indexed proposalId, int256 choice, uint256 tokensSpent);
    event ProposalExecuted(uint256 indexed proposalId, bool success, int256 result);

    constructor(address _governanceToken) {
        governanceToken = IERC20(_governanceToken);
    }

    modifier onlyTokenHolder() {
        require(governanceToken.balanceOf(msg.sender) > 0, "Must hold tokens");
        _;
    }

    modifier validTimeframe(uint256 proposalId) {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp >= proposal.startTime, "Voting not started");
        require(block.timestamp <= proposal.endTime, "Voting ended");
        _;
    }

    /**
     * @dev Create a new quadratic voting proposal
     */
    function createProposal(
        string memory _title,
        string memory _description,
        uint256 _minTokensRequired
    ) external onlyOwner returns (uint256) {
        proposalCounter.increment();
        uint256 proposalId = proposalCounter.current();
        
        proposals[proposalId].id = proposalId;
        proposals[proposalId].title = _title;
        proposals[proposalId].description = _description;
        proposals[proposalId].startTime = block.timestamp;
        proposals[proposalId].endTime = block.timestamp + VOTING_PERIOD;
        proposals[proposalId].minTokensRequired = _minTokensRequired;
        proposals[proposalId].result = 0;
        proposals[proposalId].executed = false;
        
        emit ProposalCreated(proposalId, _title, proposals[proposalId].endTime);
        return proposalId;
    }

    /**
     * @dev Cast quadratic vote with tokens
     */
    function vote(
        uint256 _proposalId,
        int256 _choice,
        uint256 _tokensToSpend
    ) external nonReentrant onlyTokenHolder validTimeframe(_proposalId) {
        require(_choice >= -1 && _choice <= 1, "Invalid choice");
        require(_tokensToSpend > 0, "Must spend tokens");
        require(_tokensToSpend <= MAX_VOTES_PER_PROPOSAL, "Exceeds max votes");
        require(block.number > lastVoteBlock[msg.sender], "One vote per block");

        Proposal storage proposal = proposals[_proposalId];
        uint256 balance = governanceToken.balanceOf(msg.sender);
        uint256 tokensSpent = proposal.tokensSpent[msg.sender];
        
        require(balance >= tokensSpent + _tokensToSpend, "Insufficient tokens");
        
        // Transfer tokens to contract (burn/lock mechanism)
        require(
            governanceToken.transferFrom(msg.sender, address(this), _tokensToSpend),
            "Token transfer failed"
        );

        // Update vote counts
        proposal.votes[msg.sender] += uint256(_choice) * _tokensToSpend;
        proposal.tokensSpent[msg.sender] += _tokensToSpend;
        proposal.totalTokensSpent += _tokensToSpend;
        
        if (_choice != 0) {
            proposal.voteCounts[_choice] += _tokensToSpend;
        }
        
        lastVoteBlock[msg.sender] = block.number;
        
        // Record vote history
        voterHistory[msg.sender].push(QuadraticVote({
            proposalId: _proposalId,
            voter: msg.sender,
            tokensSpent: _tokensToSpend,
            voteChoice: _choice,
            timestamp: block.timestamp,
            executed: false
        }));
        
        emit Voted(msg.sender, _proposalId, _choice, _tokensToSpend);
    }

    /**
     * @dev Execute proposal if conditions are met
     */
    function executeProposal(uint256 _proposalId) external {
        Proposal storage proposal = proposals[_proposalId];
        require(!proposal.executed, "Already executed");
        require(block.timestamp > proposal.endTime, "Voting not ended");
        require(proposal.totalTokensSpent >= proposal.minTokensRequired, "Min tokens not met");

        // Calculate quadratic result
        int256 yesVotes = int256(proposal.voteCounts[1]);
        int256 noVotes = int256(proposal.voteCounts[-1]);
        
        // Calculate weighted result using square root of total spent
        uint256 totalSpent = proposal.totalTokensSpent;
        int256 result = (yesVotes - noVotes) / int256(totalSpent);
        
        proposal.result = result;
        proposal.executed = true;
        
        emit ProposalExecuted(_proposalId, result > 0, result);
        
        // Execute proposal actions if result is positive
        if (result > 0) {
            _executeProposalActions(_proposalId);
        }
    }

    /**
     * @dev Get voter power for a proposal (square root of tokens)
     */
    function getVotingPower(uint256 _proposalId, address _voter) external view returns (uint256) {
        uint256 tokensSpent = proposals[_proposalId].tokensSpent[_voter];
        return _sqrt(tokensSpent);
    }

    /**
     * @dev Get proposal results
     */
    function getProposalResults(uint256 _proposalId) external view returns (
        int256 result,
        uint256 yesVotes,
        uint256 noVotes,
        uint256 abstainVotes,
        uint256 totalTokensSpent
    ) {
        Proposal storage proposal = proposals[_proposalId];
        return (
            proposal.result,
            proposal.voteCounts[1],
            proposal.voteCounts[-1],
            proposal.voteCounts[0],
            proposal.totalTokensSpent
        );
    }

    /**
     * @dev Get voter history
     */
    function getVoterHistory(address _voter) external view returns (QuadraticVote[] memory) {
        return voterHistory[_voter];
    }

    /**
     * @dev Square root calculation
     */
    function _sqrt(uint256 x) internal pure returns (uint256) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        uint256 y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
        return y;
    }

    /**
     * @dev Internal function to execute proposal actions
     */
    function _executeProposalActions(uint256 _proposalId) internal {
        // Implementation depends on specific governance needs
        // This could call other contracts, transfer funds, change parameters, etc.
    }

    /**
     * @dev Withdraw unused tokens (emergency)
     */
    function withdrawTokens(uint256 _amount) external onlyOwner {
        require(governanceToken.transfer(owner(), _amount), "Transfer failed");
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