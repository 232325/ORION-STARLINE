// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title IGovernanceToken - DAO boshqaruv tokeni interfeysi
 * @notice Governance va staking tokenlari
 */
interface IGovernanceToken is IERC20 {
    struct StakingInfo {
        uint256 amount;
        uint256 stakingDate;
        uint256 unlockDate;
        bool active;
        uint256 rewards;
    }

    struct VotingLock {
        address account;
        uint256 amount;
        uint256 startTime;
        uint256 endTime;
        uint256 votingPowerMultiplier;
    }

    struct Distribution {
        uint256 amount;
        uint256 startDate;
        uint256 endDate;
        uint256 claimedAmount;
        bool claimable;
    }

    struct Vesting {
        address beneficiary;
        uint256 amount;
        uint256 startDate;
        uint256 duration;
        uint256 claimedAmount;
        bool revocable;
    }

    enum DistributionType {
        Airdrop,
        Mining,
        Staking,
        Team,
        Treasury,
        Community
    }

    event TokensMinted(address indexed to, uint256 amount, string reason);
    event TokensBurned(address indexed from, uint256 amount, string reason);
    event Staked(address indexed user, uint256 amount, uint256 duration);
    event Unstaked(address indexed user, uint256 amount, uint256 rewards);
    event RewardsDistributed(address indexed user, uint256 amount);
    event VotingPowerLocked(address indexed account, uint256 amount, uint256 duration);
    event VestingCreated(address indexed beneficiary, uint256 amount, uint256 duration);
    event VestingClaimed(address indexed beneficiary, uint256 amount);
    event DistributionCreated(uint256 indexed distributionId, DistributionType indexed type, uint256 amount);
    event TokenClaimed(address indexed user, uint256 indexed distributionId, uint256 amount);

    // Asosiy token funksiyalari
    function mint(address _to, uint256 _amount, string memory _reason) external;
    function burn(uint256 _amount, string memory _reason) external;
    function transferAndLock(address _to, uint256 _amount, uint256 _duration) external returns (uint256 votingPower);

    // Staking funksiyalari
    function stake(uint256 _amount, uint256 _duration) external;
    function unstake(uint256 _amount) external;
    function claimRewards() external;
    function getStakingInfo(address _user) external view returns (StakingInfo memory);
    function getTotalStaked() external view returns (uint256);
    function getStakingRewards(address _user) external view returns (uint256);

    // Voting power funksiyalari
    function getVotingPower(address _account) external view returns (uint256);
    function getVotingPowerAt(address _account, uint256 _blockNumber) external view returns (uint256);
    function lockVotingPower(uint256 _amount, uint256 _duration) external;
    function unlockVotingPower(uint256 _amount) external;
    function getVotingLocks(address _account) external view returns (VotingLock[] memory);
    function getVotingPowerMultiplier(uint256 _lockDuration) external pure returns (uint256);

    // Distribution va claim
    function createDistribution(
        DistributionType _type,
        uint256 _amount,
        uint256 _startDate,
        uint256 _duration,
        bool _claimable
    ) external returns (uint256 distributionId);

    function claimDistribution(uint256 _distributionId) external;
    function batchClaim(uint256[] memory _distributionIds) external;
    function getClaimableAmount(address _user, uint256 _distributionId) external view returns (uint256);
    function getUserDistributions(address _user) external view returns (uint256[] memory);
    function getDistribution(uint256 _distributionId) external view returns (Distribution memory);

    // Vesting
    function createVesting(
        address _beneficiary,
        uint256 _amount,
        uint256 _duration,
        bool _revocable
    ) external;

    function claimVesting(address _beneficiary) external;
    function revokeVesting(address _beneficiary) external;
    function getVestingInfo(address _beneficiary) external view returns (Vesting memory);

    // Team va airdrop
    function batchMint(address[] memory _recipients, uint256[] memory _amounts, string memory _reason) external;
    function batchClaimableMint(address[] memory _recipients, uint256[] memory _amounts, uint256 _duration) external;

    // Governance funksiyalari
    function setStakingRewards(uint256 _rewardRate) external;
    function setVotingLockMultiplier(uint256 _multiplier) external;
    function setDistributionLimit(DistributionType _type, uint256 _limit) external;

    // Utility funksiyalari
    function totalSupply() external view override returns (uint256);
    function circulatingSupply() external view returns (uint256);
    function totalLocked() external view returns (uint256);
    function getTokenomics() external view returns (
        uint256 totalSupply,
        uint256 circulating,
        uint256 staked,
        uint256 locked,
        uint256 distributed
    );

    // Emergency
    function emergencyWithdraw(address _token, address _to, uint256 _amount) external;
    function pause() external;
    function unpause() external;
    function paused() external view returns (bool);

    // Events filtering
    function getMintEvents(address _account) external view returns (uint256[] memory amounts, uint256[] memory timestamps);
    function getStakeEvents(address _user) external view returns (uint256[] memory amounts, uint256[] memory durations);
}