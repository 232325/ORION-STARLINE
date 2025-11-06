// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IDAO - DAO asosiy interfeysi
 * @notice Decentralized Autonomous Organization asosiy funksiyalari
 */
interface IDAO {
    struct Member {
        address member;
        bool active;
        uint256 joinDate;
        uint256 votingPower;
        string role;
        bool isDelegate;
    }

    struct Proposal {
        uint256 id;
        string title;
        string description;
        address proposer;
        uint256 startTime;
        uint256 endTime;
        uint256 votingPowerRequired;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 votesAbstain;
        uint256 delegationVotes;
        bool executed;
        bool cancelled;
        bytes data;
    }

    enum ProposalState {
        Pending,
        Active,
        Succeeded,
        Defeated,
        Executed,
        Cancelled,
        Expired,
        QuorumFailed,
        VotingFailed
    }

    enum VotingType {
        Simple,
        TokenWeighted,
        Quadratic,
        DelegationBased,
        MultiPhase
    }

    event MemberAdded(address indexed member, string role);
    event MemberRemoved(address indexed member);
    event MemberUpdated(address indexed member, string newRole, uint256 newVotingPower);
    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, string title);
    event VoteCast(address indexed voter, uint256 indexed proposalId, uint8 support, uint256 votingPower);
    event ProposalExecuted(uint256 indexed proposalId);
    event TreasuryDeposit(address indexed from, uint256 amount);
    event TreasuryWithdrawal(address indexed to, uint256 amount, string reason);

    // Asosiy funksiyalar
    function addMember(address _member, string memory _role) external;
    function removeMember(address _member) external;
    function updateMember(address _member, string memory _newRole) external;
    function getMember(address _member) external view returns (Member memory);
    function getMemberCount() external view returns (uint256);
    function isMember(address _member) external view returns (bool);

    // Proposal funksiyalari
    function createProposal(
        string memory _title,
        string memory _description,
        bytes memory _data,
        VotingType _votingType,
        uint256 _votingPeriod,
        uint256 _votingPowerRequired
    ) external returns (uint256);

    function castVote(uint256 _proposalId, uint8 support) external;
    function executeProposal(uint256 _proposalId) external;
    function cancelProposal(uint256 _proposalId) external;

    function getProposal(uint256 _proposalId) external view returns (Proposal memory);
    function getProposalState(uint256 _proposalId) external view returns (ProposalState);

    // Voting power funksiyalari
    function getVotingPower(address _member) external view returns (uint256);
    function delegateVoting(address _to) external;
    function undelegateVoting() external;

    // Emergency funksiyalar
    function emergencyPause() external;
    function emergencyUnpause() external;
    function emergencyTransfer(address _to, uint256 _amount, string memory _reason) external;

    // Governance funksiyalari
    function updateQuorum(uint256 _newQuorum) external;
    function updateVotingPeriod(uint256 _newPeriod) external;
    function updateGovernanceRules(bytes memory _newRules) external;

    // Statistics
    function getTotalVotingPower() external view returns (uint256);
    function getProposalCount() external view returns (uint256);
    function getActiveProposals() external view returns (uint256[] memory);
}