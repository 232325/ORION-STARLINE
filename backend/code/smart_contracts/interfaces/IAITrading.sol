// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IAITrading Interface
 * @dev AI Trading Contract interfeysi - reinforcement learning signal execution
 */
interface IAITrading {
    // Events
    event TradeExecuted(address indexed trader, bytes32 indexed signalId, int256 action, uint256 amount);
    event SignalProcessed(bytes32 indexed signalId, bool executed, string reason);
    event RiskAlert(bytes32 indexed signalId, string alertType, uint256 riskLevel);
    
    // Structs
    struct TradingSignal {
        bytes32 id;
        address trader;
        int256 action; // -100 to 100 (short to long)
        uint256 amount; // Amount in base currency
        uint256 timestamp;
        uint256 confidence; // 0-1000 (0.1% to 100%)
        bytes32 marketHash; // Hash of market data
        bool executed;
        bool cancelled;
    }
    
    struct ExecutionResult {
        bool success;
        bytes32 tradeId;
        uint256 executedAmount;
        uint256 avgPrice;
        string errorMessage;
    }
    
    // Core Functions
    function submitSignal(
        int256 action,
        uint256 amount,
        uint256 confidence,
        bytes32 marketHash
    ) external returns (bytes32 signalId);
    
    function executeSignal(bytes32 signalId) external returns (ExecutionResult memory);
    
    function cancelSignal(bytes32 signalId) external;
    
    function getSignal(bytes32 signalId) external view returns (TradingSignal memory);
    
    function getActiveSignals(address trader) external view returns (bytes32[] memory);
    
    function setExecutionThreshold(uint256 threshold) external;
    
    function setMaxPositionSize(uint256 maxSize) external;
    
    function emergencyPause() external;
    
    function unpause() external;
    
    // View Functions
    function isPaused() external view returns (bool);
    
    function getExecutionThreshold() external view returns (uint256);
    
    function getMaxPositionSize() external view returns (uint256);
    
    function getTotalSignals() external view returns (uint256);
}