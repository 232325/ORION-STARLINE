// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IGovernanceManager
 * @dev Interface for DAO governance integration
 * @author MultiSig Wallet System
 */
interface IGovernanceManager {
    // Events
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed creator,
        string description,
        uint256 startTime,
        uint256 endTime
    );
    event VoteCast(
        uint256 indexed proposalId,
        address indexed voter,
        uint8 support,
        uint256 weight
    );
    event ProposalExecuted(uint256 indexed proposalId);
    event ProposalCancelled(uint256 indexed proposalId);
    event DelegationCreated(address indexed delegator, address indexed delegate);
    event DelegationRevoked(address indexed delegator, address indexed delegate);
    
    // Enums
    enum ProposalState {
        PENDING,
        ACTIVE,
        SUCCEEDED,
        DEFEATED,
        EXECUTED,
        CANCELLED
    }
    
    enum VoteType {
        AGAINST,
        FOR,
        ABSTAIN
    }
    
    struct Proposal {
        uint256 id;
        address creator;
        string description;
        uint256 startTime;
        uint256 endTime;
        ProposalState state;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        uint256 totalVotingPower;
        bytes actions; // Encoded actions to execute if proposal passes
    }
    
    struct Vote {
        address voter;
        VoteType support;
        uint256 weight;
        uint256 timestamp;
    }
    
    struct Delegation {
        address delegate;
        uint256 amount;
        uint256 startTime;
        uint256 endTime;
        bool active;
    }
    
    struct VotingPower {
        uint256 owned;
        uint256 delegated;
        uint256 total;
    }
    
    // Core functions
    function createProposal(
        string calldata description,
        bytes calldata actions,
        uint256 duration
    ) external returns (uint256 proposalId);
    
    function castVote(
        uint256 proposalId,
        VoteType support,
        uint256 weight
    ) external;
    
    function executeProposal(uint256 proposalId) external;
    
    function cancelProposal(uint256 proposalId) external;
    
    // Delegation functions
    function delegateVotingPower(
        address delegatee,
        uint256 amount,
        uint256 duration
    ) external;
    
    function revokeDelegation(address delegatee) external;
    
    // View functions
    function getProposal(uint256 proposalId) external view returns (Proposal memory);
    
    function getVote(uint256 proposalId, address voter) external view returns (Vote memory);
    
    function getDelegation(address delegator) external view returns (Delegation memory);
    
    function getVotingPower(address account) external view returns (VotingPower memory);
    
    function getProposalState(uint256 proposalId) external view returns (ProposalState);
    
    function hasVoted(uint256 proposalId, address voter) external view returns (bool);
    
    // Quorum and threshold functions
    function getQuorum(uint256 proposalId) external view returns (uint256 quorum);
    
    function isProposalPassed(uint256 proposalId) external view returns (bool);
    
    function canExecute(uint256 proposalId) external view returns (bool);
}