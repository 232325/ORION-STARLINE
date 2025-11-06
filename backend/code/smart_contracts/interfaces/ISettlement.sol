// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ISettlement Interface
 * @dev Settlement Contract interfeysi - Order fulfillment
 */
interface ISettlement {
    // Events
    event OrderCreated(bytes32 indexed orderId, address indexed trader, address asset, uint256 amount, uint256 price);
    event OrderFilled(bytes32 indexed orderId, uint256 filledAmount, uint256 avgPrice);
    event OrderCancelled(bytes32 indexed orderId, string reason);
    event SettlementCompleted(bytes32 indexed orderId, address indexed trader, uint256 totalAmount);
    event SettlementFailed(bytes32 indexed orderId, string reason);
    
    // Enums
    enum OrderType {
        MARKET,
        LIMIT,
        STOP_LOSS,
        TAKE_PROFIT
    }
    
    enum OrderSide {
        BUY,
        SELL
    }
    
    enum OrderStatus {
        PENDING,
        PARTIALLY_FILLED,
        FILLED,
        CANCELLED,
        REJECTED
    }
    
    // Structs
    struct Order {
        bytes32 id;
        address trader;
        address asset;
        uint256 amount;
        uint256 filledAmount;
        uint256 price;
        uint256 stopPrice;
        OrderType orderType;
        OrderSide side;
        OrderStatus status;
        uint256 timestamp;
        uint256 expiry;
        bool isActive;
    }
    
    struct FillInfo {
        uint256 amount;
        uint256 price;
        uint256 fee;
        uint256 timestamp;
        address counterparty;
    }
    
    struct SettlementInfo {
        bytes32 orderId;
        uint256 totalAmount;
        uint256 totalFee;
        uint256 avgPrice;
        FillInfo[] fills;
        bool settled;
        uint256 settlementTimestamp;
    }
    
    // Core Functions
    function createOrder(
        address asset,
        uint256 amount,
        uint256 price,
        uint256 stopPrice,
        OrderType orderType,
        OrderSide side,
        uint256 expiry
    ) external returns (bytes32 orderId);
    
    function cancelOrder(bytes32 orderId) external;
    
    function fillOrder(bytes32 orderId, uint256 fillAmount, uint256 fillPrice, address counterparty) external;
    
    function settleOrder(bytes32 orderId) external returns (bool success);
    
    function batchFill(bytes32[] memory orderIds, uint256[] memory fillAmounts, uint256[] memory fillPrices, address[] memory counterparties) external;
    
    // Batch Operations
    function batchCancel(bytes32[] memory orderIds) external;
    
    function batchSettle(bytes32[] memory orderIds) external returns (bool[] memory success);
    
    // View Functions
    function getOrder(bytes32 orderId) external view returns (Order memory);
    
    function getActiveOrders(address trader) external view returns (bytes32[] memory);
    
    function getOrderBook(address asset, OrderSide side) external view returns (Order[] memory);
    
    function getSettlementInfo(bytes32 orderId) external view returns (SettlementInfo memory);
    
    function calculateFees(bytes32 orderId, uint256 fillAmount) external view returns (uint256);
    
    function isOrderExpired(bytes32 orderId) external view returns (bool);
    
    // State Management
    function setOrderExpiry(bytes32 orderId, uint256 expiry) external;
    
    function setMaxOrderAmount(uint256 maxAmount) external;
    
    function setMinOrderAmount(uint256 minAmount) external;
    
    function pauseTrading() external;
    
    function unpauseTrading() external;
}