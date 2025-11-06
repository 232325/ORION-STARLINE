// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IRiskManagement Interface
 * @dev Risk Management Contract interfeysi - Stop-loss, take-profit
 */
interface IRiskManagement {
    // Events
    event StopLossTriggered(address indexed trader, address indexed asset, uint256 amount, uint256 triggerPrice);
    event TakeProfitTriggered(address indexed trader, address indexed asset, uint256 amount, uint256 triggerPrice);
    event RiskLimitExceeded(address indexed trader, string limitType, uint256 currentValue, uint256 limit);
    event RiskParameterUpdated(string parameter, uint256 oldValue, uint256 newValue);
    event CircuitBreakerActivated(string reason);
    
    // Structs
    struct RiskLimits {
        uint256 maxPositionSize; // Maximum position size per asset
        uint256 maxPortfolioValue; // Maximum total portfolio value
        uint256 maxDailyLoss; // Maximum daily loss
        uint256 maxLeverage; // Maximum leverage ratio
        uint256 stopLossPercentage; // Stop loss percentage (basis points)
        uint256 takeProfitPercentage; // Take profit percentage (basis points)
    }
    
    struct RiskMetrics {
        uint256 currentPositionSize;
        uint256 currentPortfolioValue;
        uint256 dailyPnL;
        uint256 currentLeverage;
        uint256 lastUpdate;
    }
    
    struct OrderInfo {
        bytes32 orderId;
        address asset;
        uint256 amount;
        uint256 entryPrice;
        uint256 stopLossPrice;
        uint256 takeProfitPrice;
        bool isActive;
        uint256 timestamp;
    }
    
    // Core Functions
    function setRiskLimits(RiskLimits memory newLimits) external;
    
    function validateTrade(address asset, uint256 amount, uint256 price, uint256 leverage) external returns (bool, string memory);
    
    function registerOrder(
        bytes32 orderId,
        address asset,
        uint256 amount,
        uint256 entryPrice,
        uint256 stopLossPrice,
        uint256 takeProfitPrice
    ) external;
    
    function updateOrder(
        bytes32 orderId,
        uint256 stopLossPrice,
        uint256 takeProfitPrice
    ) external;
    
    function checkStopLoss(bytes32 orderId, uint256 currentPrice) external returns (bool);
    
    function checkTakeProfit(bytes32 orderId, uint256 currentPrice) external returns (bool);
    
    function updateRiskMetrics(address trader, address asset, uint256 amount, int256 pnl) external;
    
    function activateCircuitBreaker(string memory reason) external;
    
    function deactivateCircuitBreaker() external;
    
    // View Functions
    function getRiskLimits() external view returns (RiskLimits memory);
    
    function getRiskMetrics(address trader) external view returns (RiskMetrics memory);
    
    function getOrderInfo(bytes32 orderId) external view returns (OrderInfo memory);
    
    function isCircuitBreakerActive() external view returns (bool);
    
    function calculateMaxPosition(address asset, uint256 portfolioValue) external view returns (uint256);
    
    function getDailyPnL(address trader) external view returns (int256);
}