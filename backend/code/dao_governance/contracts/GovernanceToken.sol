// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/draft-ERC20Permit.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

import "../interfaces/IGovernanceToken.sol";

/**
 * @title GovernanceToken Contract - DAO Boshqaruv Tokeni
 * @notice Token staking, vesting, distribution va governance funksiyalari
 */
contract GovernanceToken is IGovernanceToken, ERC20, ERC20Burnable, ERC20Pausable, ERC20Permit, Ownable, ReentrancyGuard {
    using SafeMath for uint256;
    using EnumerableSet for EnumerableSet.AddressSet;

    // Strukturalar
    mapping(address => StakingInfo) public stakingInfo;
    mapping(address => VotingLock[]) public votingLocks;
    mapping(uint256 => Distribution) public distributions;
    mapping(address => EnumerableSet.AddressSet) private userDistributions;
    
    // Staking settings
    uint256 public stakingRewardRate = 100; // 100 tokens per block per staked token
    uint256 public totalStaked = 0;
    uint256 public totalLocked = 0;
    uint256 public totalDistributed = 0;
    
    // Voting lock multipliers
    mapping(uint256 => uint256) public votingLockMultipliers;
    uint256 public constant MAX_MULTIPLIER = 500; // 5x max multiplier
    
    // Distribution settings
    mapping(DistributionType => uint256) public distributionLimits;
    uint256 public distributionIdCounter = 0;
    
    // Vesting
    mapping(address => Vesting) public vestingInfo;
    
    // Events
    event StakingRewardRateUpdated(uint256 oldRate, uint256 newRate);
    event VotingMultiplierUpdated(uint256 duration, uint256 multiplier);
    event DistributionLimitUpdated(DistributionType indexed type, uint256 oldLimit, uint256 newLimit);
    event DistributionClosed(uint256 indexed distributionId);

    // Modifiers
    modifier validAmount(uint256 _amount) {
        require(_amount > 0, "Invalid amount");
        _;
    }

    modifier sufficientBalance(address _account, uint256 _amount) {
        require(balanceOf(_account) >= _amount, "Insufficient balance");
        _;
    }

    modifier nonZeroAddress(address _address) {
        require(_address != address(0), "Invalid address");
        _;
    }

    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _initialSupply
    ) 
        ERC20(_name, _symbol) 
        ERC20Permit(_name)
        Ownable(msg.sender)
    {
        // Initial supply
        _mint(msg.sender, _initialSupply);
        
        // Default voting lock multipliers
        votingLockMultipliers[30 days] = 100; // 1x
        votingLockMultipliers[90 days] = 150; // 1.5x
        votingLockMultipliers[180 days] = 200; // 2x
        votingLockMultipliers[365 days] = 300; // 3x
        votingLockMultipliers[730 days] = 500; // 5x
        
        // Default distribution limits
        distributionLimits[DistributionType.Airdrop] = 1000000 * 10**decimals(); // 1M tokens
        distributionLimits[DistributionType.Mining] = 10000000 * 10**decimals(); // 10M tokens
        distributionLimits[DistributionType.Staking] = 5000000 * 10**decimals(); // 5M tokens
        distributionLimits[DistributionType.Team] = 2000000 * 10**decimals(); // 2M tokens
        distributionLimits[DistributionType.Treasury] = 3000000 * 10**decimals(); // 3M tokens
        distributionLimits[DistributionType.Community] = 5000000 * 10**decimals(); // 5M tokens
    }

    // ===== TOKEN BASIC FUNCTIONS =====

    /**
     * @dev Tokenlarni mint qilish
     */
    function mint(address _to, uint256 _amount, string memory _reason) 
        external 
        override 
        onlyOwner 
        validAmount(_amount) 
        nonZeroAddress(_to) 
    {
        _mint(_to, _amount);
        emit TokensMinted(_to, _amount, _reason);
    }

    /**
     * @dev Tokenlarni burn qilish
     */
    function burn(uint256 _amount, string memory _reason) 
        external 
        override 
        validAmount(_amount) 
        sufficientBalance(msg.sender, _amount) 
    {
        _burn(msg.sender, _amount);
        emit TokensBurned(msg.sender, _amount, _reason);
    }

    /**
     * @dev Transfer qilish va voting power lock qilish
     */
    function transferAndLock(address _to, uint256 _amount, uint256 _duration) 
        external 
        override 
        validAmount(_amount) 
        nonZeroAddress(_to)
        sufficientBalance(msg.sender, _amount)
        returns (uint256 votingPower) 
    {
        _transfer(msg.sender, _to, _amount);
        return lockVotingPower(_amount, _duration);
    }

    // ===== STAKING FUNCTIONS =====

    /**
     * @dev Tokenlarni staking qilish
     */
    function stake(uint256 _amount, uint256 _duration) 
        external 
        override 
        validAmount(_amount) 
        sufficientBalance(msg.sender, _amount) 
    {
        require(_duration >= 30 days, "Minimum 30 days staking");
        require(_duration <= 730 days, "Maximum 2 years staking");
        
        StakingInfo storage info = stakingInfo[msg.sender];
        
        // Claim existing rewards
        if (info.active) {
            _claimStakingRewards(msg.sender);
        }
        
        // Transfer tokens to contract
        _transfer(msg.sender, address(this), _amount);
        
        // Update staking info
        info.amount = info.amount.add(_amount);
        info.stakingDate = block.timestamp;
        info.unlockDate = block.timestamp.add(_duration);
        info.active = true;
        info.rewards = 0;
        
        totalStaked = totalStaked.add(_amount);
        
        emit Staked(msg.sender, _amount, _duration);
    }

    /**
     * @dev Staked tokenlarni undirish
     */
    function unstake(uint256 _amount) 
        external 
        override 
        validAmount(_amount) 
    {
        StakingInfo storage info = stakingInfo[msg.sender];
        require(info.active, "No active staking");
        require(_amount <= info.amount, "Insufficient staked amount");
        require(block.timestamp >= info.unlockDate, "Staking period not ended");
        
        // Calculate and claim rewards
        _calculateAndClaimRewards(msg.sender);
        
        // Update staking info
        info.amount = info.amount.sub(_amount);
        if (info.amount == 0) {
            info.active = false;
        }
        
        totalStaked = totalStaked.sub(_amount);
        
        // Transfer tokens back
        _transfer(address(this), msg.sender, _amount);
        
        emit Unstaked(msg.sender, _amount, info.rewards);
    }

    /**
     * @dev Staking rewardsni claim qilish
     */
    function claimRewards() external override nonReentrant {
        _calculateAndClaimRewards(msg.sender);
    }

    /**
     * @dev Staking ma'lumotlarini olish
     */
    function getStakingInfo(address _user) external view override returns (StakingInfo memory) {
        StakingInfo memory info = stakingInfo[_user];
        
        // Calculate current rewards
        if (info.active) {
            info.rewards = _calculateRewards(_user);
        }
        
        return info;
    }

    /**
     * @dev Jami staked tokenlarni olish
     */
    function getTotalStaked() external view override returns (uint256) {
        return totalStaked;
    }

    /**
     * @dev Staking rewardsni olish
     */
    function getStakingRewards(address _user) external view override returns (uint256) {
        return _calculateRewards(_user);
    }

    // ===== VOTING POWER FUNCTIONS =====

    /**
     * @dev Voting power olish
     */
    function getVotingPower(address _account) public view override returns (uint256) {
        uint256 basePower = balanceOf(_account);
        
        // Add staking power
        if (stakingInfo[_account].active) {
            basePower = basePower.add(stakingInfo[_account].amount);
        }
        
        // Add voting locks power with multipliers
        VotingLock[] storage locks = votingLocks[_account];
        for (uint256 i = 0; i < locks.length; i++) {
            if (block.timestamp <= locks[i].endTime && locks[i].active) {
                basePower = basePower.add(locks[i].amount.mul(locks[i].votingPowerMultiplier).div(100));
            }
        }
        
        return basePower;
    }

    /**
     * @dev Muayyan block number da voting power
     */
    function getVotingPowerAt(address _account, uint256 _blockNumber) external view override returns (uint256) {
        // Simplified implementation
        return getVotingPower(_account);
    }

    /**
     * @dev Voting power lock qilish
     */
    function lockVotingPower(uint256 _amount, uint256 _duration) 
        public 
        override 
        validAmount(_amount) 
        sufficientBalance(msg.sender, _amount) 
        returns (uint256 votingPower) 
    {
        require(_duration >= 30 days, "Minimum 30 days");
        require(_duration <= 730 days, "Maximum 2 years");
        
        // Calculate voting power multiplier
        uint256 multiplier = getVotingPowerMultiplier(_duration);
        votingPower = _amount.mul(multiplier).div(100);
        
        // Transfer tokens to lock
        _transfer(msg.sender, address(this), _amount);
        
        // Create voting lock
        VotingLock memory lock = VotingLock({
            account: msg.sender,
            amount: _amount,
            startTime: block.timestamp,
            endTime: block.timestamp.add(_duration),
            votingPowerMultiplier: multiplier
        });
        
        votingLocks[msg.sender].push(lock);
        totalLocked = totalLocked.add(_amount);
        
        emit VotingPowerLocked(msg.sender, _amount, _duration);
    }

    /**
     * @dev Lock qilingan voting power'ni ochish
     */
    function unlockVotingPower(uint256 _amount) external override validAmount(_amount) {
        VotingLock[] storage locks = votingLocks[msg.sender];
        uint256 totalUnlocked = 0;
        
        for (uint256 i = 0; i < locks.length; i++) {
            if (locks[i].account == msg.sender && 
                block.timestamp >= locks[i].endTime && 
                locks[i].amount >= _amount.sub(totalUnlocked)) {
                
                uint256 unlockAmount = _amount.sub(totalUnlocked);
                locks[i].amount = locks[i].amount.sub(unlockAmount);
                totalUnlocked = totalUnlocked.add(unlockAmount);
                
                if (locks[i].amount == 0) {
                    locks[i].active = false;
                }
                
                if (totalUnlocked >= _amount) break;
            }
        }
        
        require(totalUnlocked >= _amount, "Insufficient unlocked amount");
        
        totalLocked = totalLocked.sub(_amount);
        _transfer(address(this), msg.sender, _amount);
    }

    /**
     * @dev Voting lock ma'lumotlarini olish
     */
    function getVotingLocks(address _account) external view override returns (VotingLock[] memory) {
        return votingLocks[_account];
    }

    /**
     * @dev Voting power multiplier olish
     */
    function getVotingPowerMultiplier(uint256 _lockDuration) public pure override returns (uint256) {
        if (_lockDuration >= 730 days) return 500; // 5x
        if (_lockDuration >= 365 days) return 300; // 3x
        if (_lockDuration >= 180 days) return 200; // 2x
        if (_lockDuration >= 90 days) return 150; // 1.5x
        return 100; // 1x
    }

    // ===== DISTRIBUTION FUNCTIONS =====

    /**
     * @dev Yangi distribution yaratish
     */
    function createDistribution(
        DistributionType _type,
        uint256 _amount,
        uint256 _startDate,
        uint256 _duration,
        bool _claimable
    ) external override onlyOwner returns (uint256 distributionId) {
        require(_amount > 0, "Invalid amount");
        require(_amount <= distributionLimits[_type], "Exceeds distribution limit");
        
        distributionId = distributionIdCounter++;
        
        distributions[distributionId] = Distribution({
            amount: _amount,
            startDate: _startDate > 0 ? _startDate : block.timestamp,
            endDate: _startDate > 0 ? _startDate.add(_duration) : block.timestamp.add(_duration),
            claimedAmount: 0,
            claimable: _claimable
        });
        
        if (_claimable) {
            // Mint tokens for claimable distribution
            _mint(address(this), _amount);
        }
        
        emit DistributionCreated(distributionId, _type, _amount);
    }

    /**
     * @dev Distribution claim qilish
     */
    function claimDistribution(uint256 _distributionId) external override nonReentrant {
        Distribution storage dist = distributions[_distributionId];
        require(dist.amount > 0, "Invalid distribution");
        require(dist.claimable, "Not claimable");
        require(block.timestamp >= dist.startDate, "Distribution not started");
        require(block.timestamp <= dist.endDate, "Distribution ended");
        
        uint256 claimableAmount = getClaimableAmount(msg.sender, _distributionId);
        require(claimableAmount > 0, "No claimable amount");
        
        dist.claimedAmount = dist.claimedAmount.add(claimableAmount);
        
        // Transfer tokens
        _transfer(address(this), msg.sender, claimableAmount);
        
        emit TokenClaimed(msg.sender, _distributionId, claimableAmount);
    }

    /**
     * @dev Bir nechta distribution'ni claim qilish
     */
    function batchClaim(uint256[] memory _distributionIds) external override nonReentrant {
        for (uint256 i = 0; i < _distributionIds.length; i++) {
            claimDistribution(_distributionIds[i]);
        }
    }

    /**
     * @dev Claimable amount olish
     */
    function getClaimableAmount(address _user, uint256 _distributionId) public view override returns (uint256) {
        Distribution memory dist = distributions[_distributionId];
        if (!dist.claimable || block.timestamp < dist.startDate || block.timestamp > dist.endDate) {
            return 0;
        }
        
        // Simplified calculation - proportional to token balance
        uint256 userBalance = balanceOf(_user);
        uint256 totalSupply = ERC20(this).totalSupply();
        
        if (totalSupply == 0) return 0;
        
        uint256 userShare = dist.amount.mul(userBalance).div(totalSupply);
        uint256 alreadyClaimed = dist.claimedAmount;
        
        return userShare > alreadyClaimed ? userShare.sub(alreadyClaimed) : 0;
    }

    /**
     * @dev Foydalanuvchi distribution'larini olish
     */
    function getUserDistributions(address _user) external view override returns (uint256[] memory) {
        return userDistributions[_user].values();
    }

    /**
     * @dev Distribution ma'lumotlarini olish
     */
    function getDistribution(uint256 _distributionId) external view override returns (Distribution memory) {
        return distributions[_distributionId];
    }

    // ===== VESTING FUNCTIONS =====

    /**
     * @dev Vesting yaratish
     */
    function createVesting(
        address _beneficiary,
        uint256 _amount,
        uint256 _duration,
        bool _revocable
    ) external override onlyOwner nonZeroAddress(_beneficiary) validAmount(_amount) {
        require(_duration >= 30 days, "Minimum 30 days");
        require(_duration <= 1095 days, "Maximum 3 years");
        
        vestingInfo[_beneficiary] = Vesting({
            beneficiary: _beneficiary,
            amount: _amount,
            startDate: block.timestamp,
            duration: _duration,
            claimedAmount: 0,
            revocable: _revocable
        });
        
        emit VestingCreated(_beneficiary, _amount, _duration);
    }

    /**
     * @dev Vesting claim qilish
     */
    function claimVesting(address _beneficiary) external override nonReentrant {
        Vesting storage vesting = vestingInfo[_beneficiary];
        require(vesting.amount > 0, "No vesting");
        require(msg.sender == _beneficiary || msg.sender == owner(), "Not authorized");
        
        uint256 claimable = getVestingClaimableAmount(_beneficiary);
        require(claimable > 0, "Nothing to claim");
        
        vesting.claimedAmount = vesting.claimedAmount.add(claimable);
        
        _transfer(address(this), _beneficiary, claimable);
        
        emit VestingClaimed(_beneficiary, claimable);
    }

    /**
     * @dev Vestingni bekor qilish
     */
    function revokeVesting(address _beneficiary) external override onlyOwner {
        Vesting storage vesting = vestingInfo[_beneficiary];
        require(vesting.revocable, "Not revocable");
        require(vesting.amount > vesting.claimedAmount, "Fully claimed");
        
        uint256 remaining = vesting.amount.sub(vesting.claimedAmount);
        vesting.amount = vesting.claimedAmount; // Prevent further claims
        
        emit VestingClaimed(_beneficiary, 0); // Use same event for tracking
    }

    /**
     * @dev Vesting ma'lumotlarini olish
     */
    function getVestingInfo(address _beneficiary) external view override returns (Vesting memory) {
        return vestingInfo[_beneficiary];
    }

    // ===== BATCH FUNCTIONS =====

    /**
     * @dev To'plamli mint
     */
    function batchMint(
        address[] memory _recipients, 
        uint256[] memory _amounts, 
        string memory _reason
    ) external override onlyOwner {
        require(_recipients.length == _amounts.length, "Array length mismatch");
        
        for (uint256 i = 0; i < _recipients.length; i++) {
            require(_recipients[i] != address(0), "Invalid address");
            require(_amounts[i] > 0, "Invalid amount");
            
            _mint(_recipients[i], _amounts[i]);
            emit TokensMinted(_recipients[i], _amounts[i], _reason);
        }
    }

    /**
     * @dev To'plamli claimable mint
     */
    function batchClaimableMint(
        address[] memory _recipients, 
        uint256[] memory _amounts, 
        uint256 _duration
    ) external override onlyOwner {
        require(_recipients.length == _amounts.length, "Array length mismatch");
        
        for (uint256 i = 0; i < _recipients.length; i++) {
            createVesting(_recipients[i], _amounts[i], _duration, false);
        }
    }

    // ===== GOVERNANCE FUNCTIONS =====

    /**
     * @dev Staking reward rate'ni o'rnatish
     */
    function setStakingRewards(uint256 _rewardRate) external override onlyOwner {
        require(_rewardRate > 0 && _rewardRate <= 1000, "Invalid reward rate"); // Max 10%
        uint256 oldRate = stakingRewardRate;
        stakingRewardRate = _rewardRate;
        emit StakingRewardRateUpdated(oldRate, _rewardRate);
    }

    /**
     * @dev Voting lock multiplier'ni o'rnatish
     */
    function setVotingLockMultiplier(uint256 _multiplier) external override onlyOwner {
        require(_multiplier >= 100 && _multiplier <= MAX_MULTIPLIER, "Invalid multiplier");
        
        // Update all multipliers (simplified)
        votingLockMultipliers[30 days] = _multiplier.div(5);
        votingLockMultipliers[90 days] = _multiplier.div(3);
        votingLockMultipliers[180 days] = _multiplier.mul(2).div(5);
        votingLockMultipliers[365 days] = _multiplier.mul(3).div(5);
        votingLockMultipliers[730 days] = _multiplier;
    }

    /**
     * @dev Distribution limit'ni o'rnatish
     */
    function setDistributionLimit(DistributionType _type, uint256 _limit) external override onlyOwner {
        uint256 oldLimit = distributionLimits[_type];
        distributionLimits[_type] = _limit;
        emit DistributionLimitUpdated(_type, oldLimit, _limit);
    }

    // ===== UTILITY FUNCTIONS =====

    /**
     * @dev Circulating supply olish
     */
    function circulatingSupply() external view override returns (uint256) {
        return totalSupply().sub(balanceOf(address(this)));
    }

    /**
     * @dev Total locked amount
     */
    function totalLocked() external view override returns (uint256) {
        return totalLocked;
    }

    /**
     * @dev Tokenomics ma'lumotlari
     */
    function getTokenomics() external view override returns (
        uint256 _totalSupply,
        uint256 _circulating,
        uint256 _staked,
        uint256 _locked,
        uint256 _distributed
    ) {
        return (
            totalSupply(),
            circulatingSupply(),
            totalStaked,
            totalLocked,
            totalDistributed
        );
    }

    /**
     * @dev Mint events filtering uchun
     */
    function getMintEvents(address _account) external view override returns (uint256[] memory amounts, uint256[] memory timestamps) {
        // Simplified implementation
        amounts = new uint256[](0);
        timestamps = new uint256[](0);
    }

    /**
     * @dev Stake events filtering uchun
     */
    function getStakeEvents(address _user) external view override returns (uint256[] memory amounts, uint256[] memory durations) {
        // Simplified implementation
        amounts = new uint256[](0);
        durations = new uint256[](0);
    }

    // ===== INTERNAL FUNCTIONS =====

    /**
     * @dev Staking rewardsni hisoblash
     */
    function _calculateRewards(address _user) internal view returns (uint256) {
        StakingInfo memory info = stakingInfo[_user];
        if (!info.active || info.amount == 0) return 0;
        
        uint256 blocksElapsed = block.number.sub(info.stakingDate);
        return info.amount.mul(blocksElapsed).mul(stakingRewardRate).div(10000);
    }

    /**
     * @dev Rewardsni claim qilish
     */
    function _calculateAndClaimRewards(address _user) internal {
        uint256 rewards = _calculateRewards(_user);
        if (rewards > 0) {
            _mint(_user, rewards);
            stakingInfo[_user].rewards = stakingInfo[_user].rewards.add(rewards);
            emit RewardsDistributed(_user, rewards);
        }
    }

    /**
     * @dev Claim qilingan rewards
     */
    function _claimStakingRewards(address _user) internal {
        uint256 rewards = _calculateRewards(_user);
        if (rewards > 0) {
            _mint(_user, rewards);
            stakingInfo[_user].rewards = stakingInfo[_user].rewards.add(rewards);
        }
    }

    /**
     * @dev Vesting claimable amount hisoblash
     */
    function getVestingClaimableAmount(address _beneficiary) internal view returns (uint256) {
        Vesting memory vesting = vestingInfo[_beneficiary];
        if (vesting.amount == 0) return 0;
        
        uint256 timeElapsed = block.timestamp.sub(vesting.startDate);
        uint256 vestedAmount = vesting.amount.mul(timeElapsed).div(vesting.duration);
        
        return vestedAmount > vesting.claimedAmount ? vestedAmount.sub(vesting.claimedAmount) : 0;
    }

    // ===== OVERRIDE REQUIRED =====

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20, ERC20Pausable) {
        super._beforeTokenTransfer(from, to, amount);
    }

    // ===== EMERGENCY FUNCTIONS =====

    /**
     * @dev Emergency token yechib olish
     */
    function emergencyWithdraw(address _token, address _to, uint256 _amount) external override onlyOwner {
        require(_to != address(0), "Invalid address");
        
        if (_token == address(0)) {
            payable(_to).transfer(_amount);
        } else {
            ERC20(_token).transfer(_to, _amount);
        }
    }

    /**
     * @dev Token transfer qoidalari (override)
     */
    function transfer(address to, uint256 amount) public override returns (bool) {
        return super.transfer(to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        return super.transferFrom(from, to, amount);
    }
}