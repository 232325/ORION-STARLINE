// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IVoting - Ovoz berish tizimi interfeysi
 * @notice Turli xil ovoz berish mexanizmlari
 */
interface IVoting {
    struct Ballot {
        uint256 proposalId;
        address voter;
        uint8 support; // 0: Against, 1: For, 2: Abstain
        uint256 votingPower;
        uint256 timestamp;
        bytes signature; // Quadratic voting uchun
        bool isDelegated;
    }

    struct Delegation {
        address delegator;
        address delegatee;
        uint256 votingPower;
        uint256 timestamp;
        bool active;
    }

    struct Snapshot {
        uint256 blockNumber;
        uint256 totalVotingPower;
        mapping(address => uint256) votingPower;
        mapping(address => bool) hasVoted;
    }

    enum VotingMechanism {
        SimpleMajority,
        TokenWeighted,
        Quadratic,
        Delegation,
        MultiPhase,
        Custom
    }

    struct VotingConfig {
        VotingMechanism mechanism;
        uint256 duration;
        uint256 quorum;
        uint256 threshold;
        bool allowDelegation;
        bool requireQuorum;
        bool snapshotRequired;
        uint256 delegationCap;
        uint256 quadraticLimit;
    }

    struct VotingResult {
        uint256 proposalId;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 votesAbstain;
        uint256 delegationVotes;
        uint256 totalVotingPower;
        bool quorumReached;
        bool thresholdReached;
        bool executed;
        uint256 finalBlock;
    }

    event VoteCast(address indexed voter, uint256 indexed proposalId, uint8 support, uint256 votingPower);
    event DelegationCreated(address indexed delegator, address indexed delegatee, uint256 votingPower);
    event DelegationRevoked(address indexed delegator, address indexed delegatee);
    event SnapshotCreated(uint256 indexed proposalId, uint256 blockNumber, uint256 totalVotingPower);
    event VotingResultPublished(uint256 indexed proposalId, VotingResult result);

    // Asosiy ovoz berish
    function castVote(
        uint256 _proposalId,
        uint8 _support,
        bytes memory _signature
    ) external payable; // Quadratic voting uchun ether talab qilinadi

    function castVoteWithDelegation(
        uint256 _proposalId,
        uint8 _support
    ) external;

    // Delegatsiya boshqaruvi
    function delegateVoting(address _delegatee) external;
    function revokeDelegation(address _delegator) external;
    function batchDelegateVoting(address[] memory _delegatees, uint256[] memory _weights) external;

    // Snapshot va voting power
    function createSnapshot(uint256 _proposalId) external;
    function getVotingPowerAt(address _member, uint256 _blockNumber) external view returns (uint256);
    function getTotalVotingPowerAt(uint256 _blockNumber) external view returns (uint256);

    // Natijalar
    function getVotingResult(uint256 _proposalId) external view returns (VotingResult memory);
    function getBallot(uint256 _proposalId, address _voter) external view returns (Ballot memory);
    function hasVoted(uint256 _proposalId, address _voter) external view returns (bool);

    // Konfiguratsiya
    function setVotingConfig(uint256 _proposalId, VotingConfig memory _config) external;
    function getVotingConfig(uint256 _proposalId) external view returns (VotingConfig memory);

    // Anti-capture mexanizmlari
    function enforceDelegationLimits(address _delegatee, uint256 _proposalId) external view returns (bool);
    function checkWhaleControl(uint256 _proposalId) external view returns (bool);
    function activateTimeLock(address _target, uint256 _delay) external;

    // Statistika
    function getVotingStats(uint256 _proposalId) external view returns (
        uint256 totalVoters,
        uint256 delegationCount,
        uint256 quadraticVoters,
        uint256 participationRate
    );

    // Emergency
    function emergencyStopVoting(uint256 _proposalId) external;
    function resumeVoting(uint256 _proposalId) external;

    // Multi-phase voting
    function startPhase(
        uint256 _proposalId,
        uint256 _phase,
        string memory _phaseName,
        uint256 _duration
    ) external;

    function advancePhase(uint256 _proposalId) external;
    function getCurrentPhase(uint256 _proposalId) external view returns (uint256, string memory, uint256);
}