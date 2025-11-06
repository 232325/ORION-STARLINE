// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title GovernanceContract
 * @dev Governance contract for decentralized decision making
 */
contract GovernanceContract is AccessControl, Pausable {
    
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant PROPOSER_ROLE = keccak256("PROPOSER_ROLE");
    bytes32 public constant VOTER_ROLE = keccak256("VOTER_ROLE");
    
    struct Proposal {
        uint256 id;
        string title;
        string description;
        uint256 voteCount;
        uint256 endTime;
        bool executed;
        address proposer;
        mapping(address => bool) hasVoted;
    }
    
    struct Voter {
        uint256 weight;
        bool voted;
        address delegate;
    }
    
    // State variables
    uint256 public proposalCount;
    mapping(uint256 => Proposal) public proposals;
    mapping(address => Voter) public voters;
    
    // Events
    event ProposalCreated(uint256 indexed proposalId, string title, address indexed proposer);
    event VoteCast(uint256 indexed proposalId, address indexed voter, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId);
    event VoterDelegated(address indexed voter, address indexed delegate);
    
    // Modifiers
    modifier onlyProposer() {
        require(hasRole(PROPOSER_ROLE, msg.sender) || hasRole(ADMIN_ROLE, msg.sender), "Not authorized to propose");
        _;
    }
    
    modifier onlyVoter() {
        require(hasRole(VOTER_ROLE, msg.sender) || hasRole(ADMIN_ROLE, msg.sender), "Not authorized to vote");
        _;
    }
    
    modifier proposalExists(uint256 proposalId) {
        require(proposalId < proposalCount, "Proposal does not exist");
        _;
    }
    
    // Constructor
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(PROPOSER_ROLE, msg.sender);
        _grantRole(VOTER_ROLE, msg.sender);
    }
    
    /**
     * @dev Create a new proposal
     */
    function createProposal(string memory title, string memory description, uint256 duration) 
        external 
        onlyProposer 
        whenNotPaused 
        returns (uint256) 
    {
        require(bytes(title).length > 0, "Title cannot be empty");
        require(bytes(description).length > 0, "Description cannot be empty");
        require(duration > 0, "Duration must be positive");
        
        uint256 proposalId = proposalCount;
        proposalCount++;
        
        proposals[proposalId].id = proposalId;
        proposals[proposalId].title = title;
        proposals[proposalId].description = description;
        proposals[proposalId].proposer = msg.sender;
        proposals[proposalId].endTime = block.timestamp + duration;
        
        emit ProposalCreated(proposalId, title, msg.sender);
        
        return proposalId;
    }
    
    /**
     * @dev Vote on a proposal
     */
    function vote(uint256 proposalId, uint256 weight) 
        external 
        onlyVoter 
        proposalExists(proposalId) 
        whenNotPaused 
    {
        require(!proposals[proposalId].hasVoted[msg.sender], "Already voted");
        require(proposals[proposalId].endTime > block.timestamp, "Voting period ended");
        require(weight > 0, "Weight must be positive");
        
        proposals[proposalId].hasVoted[msg.sender] = true;
        proposals[proposalId].voteCount += weight;
        
        emit VoteCast(proposalId, msg.sender, weight);
    }
    
    /**
     * @dev Delegate voting power
     */
    function delegate(address to) external whenNotPaused {
        require(to != msg.sender, "Cannot delegate to self");
        require(to != address(0), "Invalid delegate address");
        
        voters[msg.sender].delegate = to;
        emit VoterDelegated(msg.sender, to);
    }
    
    /**
     * @dev Execute a proposal
     */
    function executeProposal(uint256 proposalId) external onlyAdmin proposalExists(proposalId) {
        require(!proposals[proposalId].executed, "Already executed");
        require(proposals[proposalId].endTime <= block.timestamp, "Voting period not ended");
        require(proposals[proposalId].voteCount > 0, "No votes cast");
        
        proposals[proposalId].executed = true;
        
        // Execute proposal logic here
        // This is where you would implement the actual proposal execution
        
        emit ProposalExecuted(proposalId);
    }
    
    /**
     * @dev Transfer tokens through governance
     */
    function transferToken(address token, address from, address to, uint256 amount) 
        external 
        onlyAdmin 
        whenNotPaused 
    {
        require(token != address(0), "Invalid token address");
        require(to != address(0), "Invalid recipient");
        require(amount > 0, "Amount must be positive");
        
        // This would require the governance contract to have approval
        // or the tokens to be in this contract's control
        // Implementation depends on your token management strategy
    }
    
    /**
     * @dev Get proposal details
     */
    function getProposal(uint256 proposalId) 
        external 
        view 
        proposalExists(proposalId) 
        returns (
            uint256 id,
            string memory title,
            string memory description,
            uint256 voteCount,
            uint256 endTime,
            bool executed,
            address proposer
        ) 
    {
        Proposal storage proposal = proposals[proposalId];
        return (
            proposal.id,
            proposal.title,
            proposal.description,
            proposal.voteCount,
            proposal.endTime,
            proposal.executed,
            proposal.proposer
        );
    }
    
    /**
     * @dev Check if address has voted on proposal
     */
    function hasVoted(uint256 proposalId, address voter) 
        external 
        view 
        proposalExists(proposalId) 
        returns (bool) 
    {
        return proposals[proposalId].hasVoted[voter];
    }
    
    /**
     * @dev Pause contract
     */
    function pause() external onlyAdmin {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyAdmin {
        _unpause();
    }
    
    /**
     * @dev Emergency withdrawal
     */
    function emergencyWithdraw() external onlyAdmin nonReentrant {
        uint256 balance = address(this).balance;
        require(balance > 0, "No balance to withdraw");
        payable(msg.sender).transfer(balance);
    }
    
    // Fallback function
    receive() external payable {}
}