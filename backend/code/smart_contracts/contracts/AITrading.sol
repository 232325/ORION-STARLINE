// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Imports
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IAITrading.sol";
import "../interfaces/IRiskManagement.sol";
import "../interfaces/ISettlement.sol";
import "../libraries/SecurityUtils.sol";
import "../libraries/MarketData.sol";
import "./PortfolioManager.sol";

/**
 * @title AITrading
 * @dev AI Trading Contract - Reinforcement Learning signal execution
 */
contract AITrading is IAITrading, AccessControl, Pausable, ReentrancyGuard {
    using Counters for Counters.Counter;
    using SecurityUtils for uint256;
    
    // Roles
    bytes32 public constant TRADER_ROLE = keccak256("TRADER_ROLE");
    bytes32 public constant AI_ORACLE_ROLE = keccak256("AI_ORACLE_ROLE");
    bytes32 public constant RISK_MANAGER_ROLE = keccak256("RISK_MANAGER_ROLE");
    
    // State variables
    Counters.Counter private _signalCounter;
    
    mapping(bytes32 => TradingSignal) private _signals;
    mapping(address => bytes32[]) private _traderSignals;
    mapping(address => bool) private _authorizedOracles;
    
    uint256 private _executionThreshold = 500; // Minimum confidence threshold (0.1% increments)
    uint256 private _maxPositionSize = 1000000; // Maximum position size in base currency
    uint256 private _minTradeAmount = 100; // Minimum trade amount
    
    PortfolioManager public portfolioManager;
    IRiskManagement public riskManager;
    ISettlement public settlement;
    
    // Market data
    mapping(address => MarketData.PriceFeed) public marketFeeds;
    
    // Events
    event ExecutionThresholdUpdated(uint256 oldThreshold, uint256 newThreshold);
    event MaxPositionSizeUpdated(uint256 oldSize, uint256 newSize);
    event OracleAuthorized(address indexed oracle, bool authorized);
    event SignalValidationFailed(bytes32 indexed signalId, string reason);
    
    // Custom errors
    error InvalidSignalData();
    error SignalNotFound(bytes32 signalId);
    error SignalAlreadyExecuted(bytes32 signalId);
    error SignalExpired(bytes32 signalId);
    error ConfidenceTooLow(uint256 confidence, uint256 threshold);
    error PositionSizeExceeded(uint256 requested, uint256 maxSize);
    error TradeAmountTooSmall(uint256 amount, uint256 minAmount);
    error UnauthorizedOracle(address oracle);
    
    /**
     * @dev Constructor
     */
    constructor(
        address portfolioManagerAddress,
        address riskManagerAddress,
        address settlementAddress
    ) {
        require(
            portfolioManagerAddress != address(0) &&
            riskManagerAddress != address(0) &&
            settlementAddress != address(0),
            "Invalid addresses"
        );
        
        // Setup roles
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(TRADER_ROLE, msg.sender);
        _grantRole(AI_ORACLE_ROLE, msg.sender);
        _grantRole(RISK_MANAGER_ROLE, msg.sender);
        
        portfolioManager = PortfolioManager(portfolioManagerAddress);
        riskManager = IRiskManagement(riskManagerAddress);
        settlement = ISettlement(settlementAddress);
    }
    
    /**
     * @dev Submit trading signal from AI/RL system
     */
    function submitSignal(
        int256 action,
        uint256 amount,
        uint256 confidence,
        bytes32 marketHash
    ) external override whenNotPaused nonReentrant returns (bytes32 signalId) {
        // Validate signal data
        if (action < -100 || action > 100) revert InvalidSignalData();
        if (amount < _minTradeAmount) revert TradeAmountTooSmall(amount, _minTradeAmount);
        if (confidence > 1000) revert InvalidSignalData();
        if (marketHash == bytes32(0)) revert InvalidSignalData();
        
        // Check confidence threshold
        if (confidence < _executionThreshold) {
            revert ConfidenceTooLow(confidence, _executionThreshold);
        }
        
        // Check position size limit
        if (amount > _maxPositionSize) {
            revert PositionSizeExceeded(amount, _maxPositionSize);
        }
        
        // Verify oracle authorization (if called by oracle)
        if (hasRole(AI_ORACLE_ROLE, msg.sender)) {
            _authorizedOracles[msg.sender] = true;
        }
        
        // Generate signal ID
        _signalCounter.increment();
        signalId = keccak256(abi.encodePacked(
            block.timestamp,
            _signalCounter.current(),
            msg.sender,
            marketHash
        ));
        
        // Create and store signal
        TradingSignal memory newSignal = TradingSignal({
            id: signalId,
            trader: msg.sender,
            action: action,
            amount: amount,
            timestamp: block.timestamp,
            confidence: confidence,
            marketHash: marketHash,
            executed: false,
            cancelled: false
        });
        
        _signals[signalId] = newSignal;
        _traderSignals[msg.sender].push(signalId);
        
        emit SignalProcessed(signalId, true, "Signal submitted successfully");
        
        return signalId;
    }
    
    /**
     * @dev Execute a trading signal
     */
    function executeSignal(bytes32 signalId) external override nonReentrant returns (ExecutionResult memory) {
        TradingSignal storage signal = _signals[signalId];
        
        // Validate signal
        if (signal.timestamp == 0) revert SignalNotFound(signalId);
        if (signal.executed) revert SignalAlreadyExecuted(signalId);
        if (signal.cancelled) revert SignalExpired(signalId);
        
        // Check signal expiry (24 hours)
        if (block.timestamp > signal.timestamp + 24 hours) {
            signal.cancelled = true;
            emit SignalProcessed(signalId, false, "Signal expired");
            revert SignalExpired(signalId);
        }
        
        // Get current market price
        address asset = address(uint160(uint256(signal.marketHash)));
        MarketData.PriceFeed storage priceFeed = marketFeeds[asset];
        
        if (priceFeed.price == 0) {
            emit SignalValidationFailed(signalId, "No price data available");
            return ExecutionResult({
                success: false,
                tradeId: bytes32(0),
                executedAmount: 0,
                avgPrice: 0,
                errorMessage: "No price data available"
            });
        }
        
        // Perform risk management checks
        (bool riskValid, string memory riskError) = riskManager.validateTrade(
            asset,
            signal.amount,
            priceFeed.price,
            1 // No leverage for now
        );
        
        if (!riskValid) {
            emit RiskAlert(signalId, "RISK_VALIDATION_FAILED", 0);
            emit SignalProcessed(signalId, false, riskError);
            return ExecutionResult({
                success: false,
                tradeId: bytes32(0),
                executedAmount: 0,
                avgPrice: 0,
                errorMessage: riskError
            });
        }
        
        // Calculate execution parameters
        uint256 executionAmount = signal.amount.safeMul(100) / 100; // 100% of requested amount
        bool isBuy = signal.action > 0;
        
        // Create order in settlement contract
        bytes32 orderId = settlement.createOrder(
            asset,
            executionAmount,
            priceFeed.price,
            0, // No stop price for market order
            ISettlement.OrderType.MARKET,
            isBuy ? ISettlement.OrderSide.BUY : ISettlement.OrderSide.SELL,
            block.timestamp + 1 hours // 1 hour expiry
        );
        
        // Update risk management with new position
        riskManager.updateRiskMetrics(signal.trader, asset, executionAmount, int256(signal.action));
        
        // Update signal as executed
        signal.executed = true;
        
        // Update portfolio
        if (isBuy) {
            portfolioManager.openPosition(asset, executionAmount, priceFeed.price);
        } else {
            portfolioManager.closePosition(asset, executionAmount, priceFeed.price);
        }
        
        emit TradeExecuted(signal.trader, signalId, signal.action, executionAmount);
        emit SignalProcessed(signalId, true, "Signal executed successfully");
        
        return ExecutionResult({
            success: true,
            tradeId: orderId,
            executedAmount: executionAmount,
            avgPrice: priceFeed.price,
            errorMessage: ""
        });
    }
    
    /**
     * @dev Cancel a trading signal
     */
    function cancelSignal(bytes32 signalId) external override {
        TradingSignal storage signal = _signals[signalId];
        
        if (signal.timestamp == 0) revert SignalNotFound(signalId);
        if (signal.executed) revert SignalAlreadyExecuted(signalId);
        if (signal.cancelled) revert SignalExpired(signalId);
        
        // Only signal owner can cancel
        if (signal.trader != msg.sender && !hasRole(DEFAULT_ADMIN_ROLE, msg.sender)) {
            revert UnauthorizedAccess();
        }
        
        signal.cancelled = true;
        emit SignalProcessed(signalId, false, "Signal cancelled by user");
    }
    
    /**
     * @dev Get signal information
     */
    function getSignal(bytes32 signalId) external view override returns (TradingSignal memory) {
        return _signals[signalId];
    }
    
    /**
     * @dev Get active signals for a trader
     */
    function getActiveSignals(address trader) external view override returns (bytes32[] memory) {
        bytes32[] memory traderSignalIds = _traderSignals[trader];
        uint256 activeCount = 0;
        
        // Count active signals
        for (uint256 i = 0; i < traderSignalIds.length; i++) {
            TradingSignal storage signal = _signals[traderSignalIds[i]];
            if (!signal.executed && !signal.cancelled) {
                activeCount++;
            }
        }
        
        // Create array of active signals
        bytes32[] memory activeSignals = new bytes32[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < traderSignalIds.length; i++) {
            TradingSignal storage signal = _signals[traderSignalIds[i]];
            if (!signal.executed && !signal.cancelled) {
                activeSignals[index] = traderSignalIds[i];
                index++;
            }
        }
        
        return activeSignals;
    }
    
    /**
     * @dev Update execution threshold
     */
    function setExecutionThreshold(uint256 threshold) external override onlyRole(DEFAULT_ADMIN_ROLE) {
        require(threshold <= 1000, "Threshold cannot exceed 100%");
        uint256 oldThreshold = _executionThreshold;
        _executionThreshold = threshold;
        emit ExecutionThresholdUpdated(oldThreshold, threshold);
    }
    
    /**
     * @dev Update maximum position size
     */
    function setMaxPositionSize(uint256 maxSize) external override onlyRole(DEFAULT_ADMIN_ROLE) {
        require(maxSize > 0, "Max size must be greater than 0");
        uint256 oldSize = _maxPositionSize;
        _maxPositionSize = maxSize;
        emit MaxPositionSizeUpdated(oldSize, maxSize);
    }
    
    /**
     * @dev Update market price feed
     */
    function updateMarketFeed(address asset, uint256 price, uint256 volume) external {
        require(hasRole(AI_ORACLE_ROLE, msg.sender), "Oracle role required");
        
        MarketData.PriceFeed storage priceFeed = marketFeeds[asset];
        
        priceFeed.price = price;
        priceFeed.volume = volume;
        priceFeed.timestamp = block.timestamp;
        priceFeed.isActive = true;
        
        int256 change = MarketData.calculateChange(priceFeed.price, price);
        priceFeed.change24h = uint256(change);
    }
    
    /**
     * @dev Emergency pause function
     */
    function emergencyPause() external override onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause function
     */
    function unpause() external override onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Check if contract is paused
     */
    function isPaused() external view override returns (bool) {
        return paused();
    }
    
    /**
     * @dev Get execution threshold
     */
    function getExecutionThreshold() external view override returns (uint256) {
        return _executionThreshold;
    }
    
    /**
     * @dev Get maximum position size
     */
    function getMaxPositionSize() external view override returns (uint256) {
        return _maxPositionSize;
    }
    
    /**
     * @dev Get total number of signals
     */
    function getTotalSignals() external view override returns (uint256) {
        return _signalCounter.current();
    }
    
    /**
     * @dev Get market feed for an asset
     */
    function getMarketFeed(address asset) external view returns (MarketData.PriceFeed memory) {
        return marketFeeds[asset];
    }
    
    /**
     * @dev Set authorized oracle
     */
    function setAuthorizedOracle(address oracle, bool authorized) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _authorizedOracles[oracle] = authorized;
        emit OracleAuthorized(oracle, authorized);
    }
    
    /**
     * @dev Check if oracle is authorized
     */
    function isOracleAuthorized(address oracle) external view returns (bool) {
        return _authorizedOracles[oracle];
    }
}