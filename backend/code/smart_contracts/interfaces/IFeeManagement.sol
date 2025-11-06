// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IFeeManagement Interface
 * @dev Fee Management Contract interfeysi - Trading fees
 */
interface IFeeManagement {
    // Events
    event FeeUpdated(address indexed asset, uint256 oldFee, uint256 newFee);
    event FeeCollected(bytes32 indexed tradeId, address indexed trader, uint256 feeAmount);
    event FeeTierUpdated(address indexed trader, uint256 oldTier, uint256 newTier);
    event RevenueDistributed(address indexed recipient, uint256 amount, string source);
    event FeeDiscountApplied(address indexed trader, uint256 discount);
    
    // Enums
    enum FeeType {
        TRADING_FEE,
        WITHDRAWAL_FEE,
        DEPOSIT_FEE,
        FUNDING_FEE,
        MANAGEMENT_FEE
    }
    
    enum DiscountTier {
        BRONZE,    // 0% discount
        SILVER,    // 10% discount
        GOLD,      // 25% discount
        PLATINUM   // 50% discount
    }
    
    // Structs
    struct FeeStructure {
        uint256 baseFee;           // Base fee in basis points
        uint256 makerFee;          // Maker fee in basis points
        uint256 takerFee;          // Taker fee in basis points
        uint256 withdrawalFee;     // Withdrawal fee in basis points
        uint256 depositFee;        // Deposit fee in basis points
        uint256 fundingFee;        // Funding fee in basis points
        uint256 managementFee;     // Management fee in basis points
    }
    
    struct FeeSchedule {
        uint256 volumeThreshold;   // Volume threshold for tier
        uint256 discountRate;      // Discount rate in basis points
        DiscountTier tier;
    }
    
    struct FeeInfo {
        uint256 totalFees;
        uint256 monthlyFees;
        uint256 volume30d;
        DiscountTier tier;
        uint256 lastUpdate;
    }
    
    struct RevenueDistribution {
        address recipient;
        uint256 percentage; // Basis points
        uint256 totalDistributed;
        bool active;
    }
    
    // Core Functions
    function setFeeStructure(address asset, FeeStructure memory fees) external;
    
    function calculateFee(
        bytes32 tradeId,
        address trader,
        address asset,
        uint256 amount,
        uint256 price,
        bool isMaker
    ) external view returns (uint256 feeAmount);
    
    function collectFee(
        bytes32 tradeId,
        address trader,
        address asset,
        uint256 amount,
        uint256 price,
        bool isMaker
    ) external returns (uint256 feeAmount);
    
    function updateTraderTier(address trader, uint256 volume) external;
    
    function addRevenueDistribution((address recipient, uint256 percentage)[] memory distributions) external;
    
    function removeRevenueDistribution(uint256 index) external;
    
    function distributeFees() external;
    
    // Utility Functions
    function calculateVolume(address trader, uint256 days) external view returns (uint256);
    
    function getCurrentTier(address trader) external view returns (DiscountTier);
    
    function getEffectiveFeeRate(address trader, FeeType feeType) external view returns (uint256);
    
    // View Functions
    function getFeeStructure(address asset) external view returns (FeeStructure memory);
    
    function getFeeInfo(address trader) external view returns (FeeInfo memory);
    
    function getRevenueDistributions() external view returns (RevenueDistribution[] memory);
    
    function getTotalFeesCollected() external view returns (uint256);
    
    function getTotalRevenue() external view returns (uint256);
    
    function setMinFeeDiscount(uint256 minDiscount) external;
    
    function setMaxFeeDiscount(uint256 maxDiscount) external;
}