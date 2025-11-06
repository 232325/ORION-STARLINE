// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Imports
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "../interfaces/IFeeManagement.sol";
import "../libraries/SecurityUtils.sol";

/**
 * @title FeeManagement
 * @dev Fee Management Contract - Trading fees va revenue distribution
 */
contract FeeManagement is IFeeManagement, AccessControl, Pausable, ReentrancyGuard {
    using Counters for Counters.Counter;
    using SecurityUtils for uint256;
    using SafeERC20 for IERC20;
    
    // Roles
    bytes32 public constant FEE_ADMIN_ROLE = keccak256("FEE_ADMIN_ROLE");
    bytes32 public constant TREASURY_ROLE = keccak256("TREASURY_ROLE");
    
    // State variables
    mapping(address => FeeStructure) private _assetFees;
    mapping(address => FeeInfo) private _traderFeeInfo;
    mapping(address => uint256) private _traderVolumes;
    mapping(address => RevenueDistribution[]) private _revenueDistributions;
    
    FeeSchedule[] private _feeSchedules;
    uint256 private _totalFeesCollected = 0;
    uint256 private _totalRevenue = 0;
    
    // Discount limits
    uint256 private _minFeeDiscount = 0; // 0% minimum discount
    uint256 private _maxFeeDiscount = 5000; // 50% maximum discount (basis points)
    
    // Constants
    uint256 private constant FEE_PRECISION = 10000; // Basis points precision
    uint256 private constant DISCOUNT_PRECISION = 10000; // Discount precision
    uint256 private constant VOLUME_DECIMALS = 18;
    
    // Events
    event FeeDiscountUpdated(address indexed trader, uint256 oldDiscount, uint256 newDiscount);
    event VolumeUpdated(address indexed trader, uint256 oldVolume, uint256 newVolume);
    event RevenueDistributionAdded(address indexed recipient, uint256 percentage, uint256 totalDistributed);
    event RevenueDistributionRemoved(address indexed recipient, uint256 index);
    event FeesDistributed(uint256 totalAmount, uint256 distributionCount);
    event FeeDiscountLimitsUpdated(uint256 oldMin, uint256 oldMax, uint256 newMin, uint256 newMax);
    
    // Custom errors
    error InvalidFeeStructure(address asset, uint256 feeType, uint256 feeAmount);
    error FeeStructureNotFound(address asset);
    error InvalidDiscountTier(uint256 tier);
    error DiscountTooHigh(uint256 discount, uint256 maxDiscount);
    error DiscountTooLow(uint256 discount, uint256 minDiscount);
    error InvalidVolumeThreshold(uint256 threshold);
    error RevenueDistributionError(string message);
    error InvalidAssetFee(address asset, uint256 feeAmount);
    error FeeCalculationError(bytes32 tradeId, string reason);
    error InsufficientRevenue(uint256 required, uint256 available);
    error InvalidDistributionPercentage(uint256 percentage, uint256 totalPercentage);
    
    /**
     * @dev Constructor
     */
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(FEE_ADMIN_ROLE, msg.sender);
        _grantRole(TREASURY_ROLE, msg.sender);
        
        // Initialize default fee schedules
        _initializeFeeSchedules();
    }
    
    /**
     * @dev Set fee structure for an asset
     */
    function setFeeStructure(address asset, FeeStructure memory fees) external override onlyRole(FEE_ADMIN_ROLE) {
        require(asset != address(0), "Invalid asset address");
        
        // Validate fee amounts (should be in basis points)
        if (fees.baseFee > FEE_PRECISION || fees.makerFee > FEE_PRECISION || 
            fees.takerFee > FEE_PRECISION || fees.withdrawalFee > FEE_PRECISION ||
            fees.depositFee > FEE_PRECISION || fees.fundingFee > FEE_PRECISION ||
            fees.managementFee > FEE_PRECISION) {
            revert InvalidFeeStructure(asset, 0, 0);
        }
        
        FeeStructure memory oldFees = _assetFees[asset];
        _assetFees[asset] = fees;
        
        emit FeeUpdated(asset, oldFees.baseFee, fees.baseFee);
        emit FeeStructureUpdated(asset, oldFees, fees);
    }
    
    /**
     * @dev Calculate trading fee for a trade
     */
    function calculateFee(
        bytes32 tradeId,
        address trader,
        address asset,
        uint256 amount,
        uint256 price,
        bool isMaker
    ) external view override returns (uint256 feeAmount) {
        FeeStructure storage fees = _assetFees[asset];
        if (fees.baseFee == 0 && fees.makerFee == 0 && fees.takerFee == 0) {
            revert FeeStructureNotFound(asset);
        }
        
        uint256 tradeValue = amount.safeMul(price);
        
        // Get base fee rate
        uint256 baseFeeRate = isMaker ? fees.makerFee : fees.takerFee;
        if (baseFeeRate == 0) {
            baseFeeRate = fees.baseFee;
        }
        
        // Calculate base fee
        uint256 baseFee = tradeValue.safeMul(baseFeeRate).safeDiv(FEE_PRECISION);
        
        // Get trader discount
        DiscountTier traderTier = getCurrentTier(trader);
        uint256 discountRate = getTierDiscountRate(traderTier);
        
        // Apply discount
        uint256 discount = baseFee.safeMul(discountRate).safeDiv(DISCOUNT_PRECISION);
        feeAmount = baseFee.safeSub(discount);
        
        return feeAmount;
    }
    
    /**
     * @dev Collect fee for a trade
     */
    function collectFee(
        bytes32 tradeId,
        address trader,
        address asset,
        uint256 amount,
        uint256 price,
        bool isMaker
    ) external override nonReentrant returns (uint256 feeAmount) {
        // Calculate fee
        feeAmount = calculateFee(tradeId, trader, asset, amount, price, isMaker);
        
        if (feeAmount > 0) {
            // Transfer fee from trader to contract
            // Assuming stablecoin payment (USDC, USDT, etc.)
            // In practice, this would be more sophisticated
            IERC20 stablecoin = IERC20(0xA0b86a33E6B3c4E3f4dE8B3C4C5D5B4E3F2E1D0C9); // Example USDC address
            
            try stablecoin.transferFrom(trader, address(this), feeAmount) {
                _totalFeesCollected = _totalFeesCollected.safeAdd(feeAmount);
                _totalRevenue = _totalRevenue.safeAdd(feeAmount);
                
                // Update trader volume for tier calculation
                uint256 tradeValue = amount.safeMul(price);
                _updateTraderVolume(trader, tradeValue);
                
                // Update trader tier if needed
                _updateTraderTier(trader);
                
                emit FeeCollected(tradeId, trader, feeAmount);
            } catch Error(string memory reason) {
                revert FeeCalculationError(tradeId, reason);
            }
        }
        
        return feeAmount;
    }
    
    /**
     * @dev Update trader tier based on volume
     */
    function updateTraderTier(address trader, uint256 volume) external override {
        require(msg.sender == address(this) || hasRole(FEE_ADMIN_ROLE, msg.sender), "Unauthorized");
        
        uint256 oldVolume = _traderVolumes[trader];
        _traderVolumes[trader] = oldVolume.safeAdd(volume);
        
        DiscountTier oldTier = getCurrentTier(trader);
        DiscountTier newTier = _calculateTier(_traderVolumes[trader]);
        
        if (oldTier != newTier) {
            FeeInfo storage feeInfo = _traderFeeInfo[trader];
            feeInfo.tier = newTier;
            
            emit FeeTierUpdated(trader, uint256(oldTier), uint256(newTier));
        }
        
        emit VolumeUpdated(trader, oldVolume, _traderVolumes[trader]);
    }
    
    /**
     * @dev Add revenue distribution
     */
    function addRevenueDistribution(RevenueDistribution[] memory distributions) 
        external override onlyRole(TREASURY_ROLE) {
        uint256 totalPercentage = 0;
        
        // Validate total percentage doesn't exceed 100%
        for (uint256 i = 0; i < distributions.length; i++) {
            totalPercentage = totalPercentage.safeAdd(distributions[i].percentage);
        }
        
        if (totalPercentage > FEE_PRECISION) {
            revert InvalidDistributionPercentage(totalPercentage, FEE_PRECISION);
        }
        
        // Add distributions
        for (uint256 i = 0; i < distributions.length; i++) {
            _revenueDistributions[address(0)].push(distributions[i]); // Global distribution
            emit RevenueDistributionAdded(distributions[i].recipient, distributions[i].percentage, 0);
        }
    }
    
    /**
     * @dev Remove revenue distribution
     */
    function removeRevenueDistribution(uint256 index) external override onlyRole(TREASURY_ROLE) {
        RevenueDistribution[] storage distributions = _revenueDistributions[address(0)];
        if (index >= distributions.length) {
            revert InvalidIndex(index);
        }
        
        address recipient = distributions[index].recipient;
        distributions[index] = distributions[distributions.length - 1];
        distributions.pop();
        
        emit RevenueDistributionRemoved(recipient, index);
    }
    
    /**
     * @dev Distribute fees to revenue recipients
     */
    function distributeFees() external override whenNotPaused nonReentrant {
        RevenueDistribution[] storage distributions = _revenueDistributions[address(0)];
        
        if (distributions.length == 0) {
            revert RevenueDistributionError("No distributions configured");
        }
        
        uint256 totalToDistribute = _totalRevenue;
        
        if (totalToDistribute == 0) {
            revert InsufficientRevenue(1, 0);
        }
        
        uint256 distributionCount = 0;
        
        // Distribute to each recipient
        for (uint256 i = 0; i < distributions.length; i++) {
            RevenueDistribution storage distribution = distributions[i];
            
            if (distribution.active && distribution.recipient != address(0)) {
                uint256 amount = totalToDistribute.safeMul(distribution.percentage).safeDiv(FEE_PRECISION);
                
                if (amount > 0) {
                    // Transfer funds to recipient
                    IERC20 stablecoin = IERC20(0xA0b86a33E6B3c4E3f4dE8B3C4C5D5B4E3F2E1D0C9); // Example USDC
                    stablecoin.transfer(distribution.recipient, amount);
                    
                    distribution.totalDistributed = distribution.totalDistributed.safeAdd(amount);
                    distributionCount++;
                    
                    emit RevenueDistributed(distribution.recipient, amount, "Fee Distribution");
                }
            }
        }
        
        // Reset total revenue after distribution
        _totalRevenue = 0;
        
        emit FeesDistributed(totalToDistribute, distributionCount);
    }
    
    /**
     * @dev Calculate 30-day volume for a trader
     */
    function calculateVolume(address trader, uint256 days) external view override returns (uint256) {
        // Simplified volume calculation
        // In practice, you'd want to track historical volumes with timestamps
        return _traderVolumes[trader];
    }
    
    /**
     * @dev Get current tier for a trader
     */
    function getCurrentTier(address trader) public view override returns (DiscountTier) {
        FeeInfo storage feeInfo = _traderFeeInfo[trader];
        return feeInfo.tier;
    }
    
    /**
     * @dev Get effective fee rate for a trader
     */
    function getEffectiveFeeRate(address trader, FeeType feeType) external view override returns (uint256) {
        DiscountTier tier = getCurrentTier(trader);
        uint256 discountRate = getTierDiscountRate(tier);
        
        // Default fee rates (would be adjusted based on feeType)
        uint256 baseFeeRate = 100; // 1% base fee (basis points)
        uint256 effectiveRate = baseFeeRate.safeMul(DISCOUNT_PRECISION).safeSub(
            baseFeeRate.safeMul(discountRate)
        ).safeDiv(DISCOUNT_PRECISION);
        
        return effectiveRate;
    }
    
    /**
     * @dev Get fee structure for an asset
     */
    function getFeeStructure(address asset) external view override returns (FeeStructure memory) {
        return _assetFees[asset];
    }
    
    /**
     * @dev Get fee info for a trader
     */
    function getFeeInfo(address trader) external view override returns (FeeInfo memory) {
        return _traderFeeInfo[trader];
    }
    
    /**
     * @dev Get revenue distributions
     */
    function getRevenueDistributions() external view override returns (RevenueDistribution[] memory) {
        return _revenueDistributions[address(0)];
    }
    
    /**
     * @dev Get total fees collected
     */
    function getTotalFeesCollected() external view override returns (uint256) {
        return _totalFeesCollected;
    }
    
    /**
     * @dev Get total revenue
     */
    function getTotalRevenue() external view override returns (uint256) {
        return _totalRevenue;
    }
    
    /**
     * @dev Set minimum fee discount
     */
    function setMinFeeDiscount(uint256 minDiscount) external override onlyRole(FEE_ADMIN_ROLE) {
        require(minDiscount <= _maxFeeDiscount, "Min discount cannot exceed max discount");
        uint256 oldMin = _minFeeDiscount;
        _minFeeDiscount = minDiscount;
        emit FeeDiscountLimitsUpdated(oldMin, _maxFeeDiscount, minDiscount, _maxFeeDiscount);
    }
    
    /**
     * @dev Set maximum fee discount
     */
    function setMaxFeeDiscount(uint256 maxDiscount) external override onlyRole(FEE_ADMIN_ROLE) {
        require(maxDiscount >= _minFeeDiscount, "Max discount cannot be below min discount");
        require(maxDiscount <= DISCOUNT_PRECISION, "Max discount cannot exceed 100%");
        uint256 oldMax = _maxFeeDiscount;
        _maxFeeDiscount = maxDiscount;
        emit FeeDiscountLimitsUpdated(_minFeeDiscount, oldMax, _minFeeDiscount, maxDiscount);
    }
    
    /**
     * @dev Pause contract
     */
    function pause() external onlyRole(FEE_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyRole(FEE_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Initialize default fee schedules
     */
    function _initializeFeeSchedules() internal {
        // Bronze tier: No volume requirement, 0% discount
        _feeSchedules.push(FeeSchedule({
            volumeThreshold: 0,
            discountRate: 0,
            tier: DiscountTier.BRONZE
        }));
        
        // Silver tier: $10,000 volume, 10% discount
        _feeSchedules.push(FeeSchedule({
            volumeThreshold: 10000 * 10**VOLUME_DECIMALS,
            discountRate: 1000, // 10%
            tier: DiscountTier.SILVER
        }));
        
        // Gold tier: $100,000 volume, 25% discount
        _feeSchedules.push(FeeSchedule({
            volumeThreshold: 100000 * 10**VOLUME_DECIMALS,
            discountRate: 2500, // 25%
            tier: DiscountTier.GOLD
        }));
        
        // Platinum tier: $1,000,000 volume, 50% discount
        _feeSchedules.push(FeeSchedule({
            volumeThreshold: 1000000 * 10**VOLUME_DECIMALS,
            discountRate: 5000, // 50%
            tier: DiscountTier.PLATINUM
        }));
    }
    
    /**
     * @dev Calculate tier based on volume
     */
    function _calculateTier(uint256 volume) internal view returns (DiscountTier) {
        for (uint256 i = _feeSchedules.length; i > 0; i--) {
            FeeSchedule storage schedule = _feeSchedules[i - 1];
            if (volume >= schedule.volumeThreshold) {
                return schedule.tier;
            }
        }
        return DiscountTier.BRONZE;
    }
    
    /**
     * @dev Get discount rate for a tier
     */
    function getTierDiscountRate(DiscountTier tier) public pure returns (uint256) {
        if (tier == DiscountTier.BRONZE) return 0;
        if (tier == DiscountTier.SILVER) return 1000; // 10%
        if (tier == DiscountTier.GOLD) return 2500; // 25%
        if (tier == DiscountTier.PLATINUM) return 5000; // 50%
        return 0;
    }
    
    /**
     * @dev Update trader volume
     */
    function _updateTraderVolume(address trader, uint256 additionalVolume) internal {
        _traderVolumes[trader] = _traderVolumes[trader].safeAdd(additionalVolume);
    }
    
    /**
     * @dev Update trader tier
     */
    function _updateTraderTier(address trader) internal {
        DiscountTier newTier = _calculateTier(_traderVolumes[trader]);
        FeeInfo storage feeInfo = _traderFeeInfo[trader];
        
        if (feeInfo.tier != newTier) {
            feeInfo.tier = newTier;
            feeInfo.volume30d = _traderVolumes[trader];
            feeInfo.lastUpdate = block.timestamp;
        }
    }
    
    // Custom errors
    error InvalidIndex(uint256 index);
    error InvalidFeeType(FeeType feeType);
    
    // Additional events
    event FeeStructureUpdated(address indexed asset, FeeStructure oldStructure, FeeStructure newStructure);
}