// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Imports
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../interfaces/IRiskManagement.sol";
import "../libraries/SecurityUtils.sol";
import "../libraries/MarketData.sol";

/**
 * @title RiskManagement
 * @dev Risk Management Contract - Stop-loss, take-profit va boshqa risk boshqaruvi
 */
contract RiskManagement is IRiskManagement, AccessControl, Pausable, ReentrancyGuard {
    using SecurityUtils for uint256;
    using MarketData for uint256;
    
    // Roles
    bytes32 public constant RISK_ADMIN_ROLE = keccak256("RISK_ADMIN_ROLE");
    bytes32 public constant RISK_OFFICER_ROLE = keccak256("RISK_OFFICER_ROLE");
    
    // State variables
    RiskLimits public limits;
    mapping(address => RiskMetrics) public traderMetrics;
    mapping(bytes32 => OrderInfo) public orders;
    mapping(address => int256) public dailyPnL;
    
    bool private _circuitBreakerActive = false;
    string private _circuitBreakerReason;
    uint256 private constant MAX_DAILY_PNL = 1000000 * 10**18; // $1M max daily P&L
    uint256 private constant MAX_CIRCUIT_BREAKER_DURATION = 24 hours;
    
    // Market data
    mapping(address => MarketData.PriceFeed) public assetPrices;
    
    // Events
    event CircuitBreakerActivated(string reason, address indexed activatedBy);
    event CircuitBreakerDeactivated(string reason, address indexed deactivatedBy);
    event RiskLimitBreached(address indexed trader, string limitType, uint256 current, uint256 limit);
    event PositionUpdated(address indexed trader, address indexed asset, uint256 newSize, uint256 portfolioValue);
    event RiskMetricsUpdated(address indexed trader, RiskMetrics oldMetrics, RiskMetrics newMetrics);
    
    // Custom errors
    error RiskLimitViolation(string limitType, uint256 current, uint256 limit);
    error PositionSizeExceeded(uint256 requested, uint256 max);
    error PortfolioValueExceeded(uint256 current, uint256 max);
    error DailyLossExceeded(int256 current, int256 max);
    error LeverageExceeded(uint256 current, uint256 max);
    error CircuitBreakerActive(string reason);
    error InvalidRiskParameters();
    error OrderNotFound(bytes32 orderId);
    error StopLossTriggered(bytes32 orderId, uint256 triggerPrice, uint256 currentPrice);
    error TakeProfitTriggered(bytes32 orderId, uint256 triggerPrice, uint256 currentPrice);
    error UnauthorizedRiskManagement();
    
    /**
     * @dev Constructor - Initialize with default risk limits
     */
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(RISK_ADMIN_ROLE, msg.sender);
        _grantRole(RISK_OFFICER_ROLE, msg.sender);
        
        // Set default risk limits
        limits = RiskLimits({
            maxPositionSize: 500000 * 10**18, // $500K max position
            maxPortfolioValue: 2000000 * 10**18, // $2M max portfolio
            maxDailyLoss: -100000 * 10**18, // -$100K max daily loss
            maxLeverage: 10, // 10x max leverage
            stopLossPercentage: 1000, // 10% stop loss
            takeProfitPercentage: 2000 // 20% take profit
        });
    }
    
    /**
     * @dev Set risk limits
     */
    function setRiskLimits(RiskLimits memory newLimits) external override onlyRole(RISK_ADMIN_ROLE) {
        // Validate risk parameters
        if (newLimits.maxPositionSize == 0 || newLimits.maxPortfolioValue == 0) {
            revert InvalidRiskParameters();
        }
        
        if (newLimits.maxLeverage == 0 || newLimits.stopLossPercentage == 0) {
            revert InvalidRiskParameters();
        }
        
        RiskLimits memory oldLimits = limits;
        limits = newLimits;
        
        emit RiskParameterUpdated("MAX_POSITION_SIZE", oldLimits.maxPositionSize, newLimits.maxPositionSize);
        emit RiskParameterUpdated("MAX_PORTFOLIO_VALUE", oldLimits.maxPortfolioValue, newLimits.maxPortfolioValue);
        emit RiskParameterUpdated("MAX_DAILY_LOSS", uint256(oldLimits.maxDailyLoss), uint256(newLimits.maxDailyLoss));
        emit RiskParameterUpdated("MAX_LEVERAGE", oldLimits.maxLeverage, newLimits.maxLeverage);
        emit RiskParameterUpdated("STOP_LOSS_PERCENTAGE", oldLimits.stopLossPercentage, newLimits.stopLossPercentage);
        emit RiskParameterUpdated("TAKE_PROFIT_PERCENTAGE", oldLimits.takeProfitPercentage, newLimits.takeProfitPercentage);
    }
    
    /**
     * @dev Validate trade before execution
     */
    function validateTrade(
        address asset,
        uint256 amount,
        uint256 price,
        uint256 leverage
    ) external override whenNotPaused returns (bool isValid, string memory reason) {
        // Check circuit breaker
        if (_circuitBreakerActive) {
            revert CircuitBreakerActive(_circuitBreakerReason);
        }
        
        // Validate trade parameters
        if (amount == 0 || price == 0 || leverage == 0) {
            return (false, "Invalid trade parameters");
        }
        
        uint256 tradeValue = amount.safeMul(price);
        
        // Check position size limit
        if (tradeValue > limits.maxPositionSize) {
            emit RiskLimitBreached(msg.sender, "POSITION_SIZE", tradeValue, limits.maxPositionSize);
            return (false, "Position size exceeds maximum");
        }
        
        // Get current portfolio value
        uint256 portfolioValue = calculatePortfolioValue(msg.sender);
        
        // Check portfolio value limit
        if (portfolioValue.safeAdd(tradeValue) > limits.maxPortfolioValue) {
            emit RiskLimitBreached(msg.sender, "PORTFOLIO_VALUE", portfolioValue.safeAdd(tradeValue), limits.maxPortfolioValue);
            return (false, "Portfolio value exceeds maximum");
        }
        
        // Check leverage limit
        if (leverage > limits.maxLeverage) {
            emit RiskLimitBreached(msg.sender, "LEVERAGE", leverage, limits.maxLeverage);
            return (false, "Leverage exceeds maximum");
        }
        
        // Check daily loss limit
        int256 currentDailyPnL = getDailyPnL(msg.sender);
        if (currentDailyPnL < limits.maxDailyLoss) {
            emit RiskLimitBreached(msg.sender, "DAILY_LOSS", uint256(-currentDailyPnL), uint256(-limits.maxDailyLoss));
            return (false, "Daily loss limit exceeded");
        }
        
        return (true, "");
    }
    
    /**
     * @dev Register a new order for risk monitoring
     */
    function registerOrder(
        bytes32 orderId,
        address asset,
        uint256 amount,
        uint256 entryPrice,
        uint256 stopLossPrice,
        uint256 takeProfitPrice
    ) external override {
        require(msg.sender == address(this) || hasRole(RISK_ADMIN_ROLE, msg.sender), "Unauthorized");
        require(orderId != bytes32(0), "Invalid order ID");
        require(amount > 0, "Amount must be positive");
        require(entryPrice > 0, "Entry price must be positive");
        
        OrderInfo storage order = orders[orderId];
        order.orderId = orderId;
        order.asset = asset;
        order.amount = amount;
        order.entryPrice = entryPrice;
        order.stopLossPrice = stopLossPrice;
        order.takeProfitPrice = takeProfitPrice;
        order.isActive = true;
        order.timestamp = block.timestamp;
        
        emit OrderInfoUpdated(orderId, "ORDER_REGISTERED");
    }
    
    /**
     * @dev Update order stop-loss and take-profit prices
     */
    function updateOrder(
        bytes32 orderId,
        uint256 stopLossPrice,
        uint256 takeProfitPrice
    ) external override {
        OrderInfo storage order = orders[orderId];
        if (order.orderId == bytes32(0)) {
            revert OrderNotFound(orderId);
        }
        
        // Only allow updates within reasonable bounds
        if (stopLossPrice > 0) {
            require(stopLossPrice < order.entryPrice, "Stop-loss must be below entry price");
            order.stopLossPrice = stopLossPrice;
        }
        
        if (takeProfitPrice > 0) {
            require(takeProfitPrice > order.entryPrice, "Take-profit must be above entry price");
            order.takeProfitPrice = takeProfitPrice;
        }
        
        emit OrderInfoUpdated(orderId, "ORDER_UPDATED");
    }
    
    /**
     * @dev Check if stop-loss should be triggered
     */
    function checkStopLoss(bytes32 orderId, uint256 currentPrice) external override returns (bool shouldTrigger) {
        OrderInfo storage order = orders[orderId];
        if (order.orderId == bytes32(0)) {
            revert OrderNotFound(orderId);
        }
        
        if (!order.isActive || order.stopLossPrice == 0) {
            return false;
        }
        
        if (currentPrice <= order.stopLossPrice) {
            order.isActive = false;
            emit StopLossTriggered(order.orderId, order.asset, order.amount, order.stopLossPrice);
            return true;
        }
        
        return false;
    }
    
    /**
     * @dev Check if take-profit should be triggered
     */
    function checkTakeProfit(bytes32 orderId, uint256 currentPrice) external override returns (bool shouldTrigger) {
        OrderInfo storage order = orders[orderId];
        if (order.orderId == bytes32(0)) {
            revert OrderNotFound(orderId);
        }
        
        if (!order.isActive || order.takeProfitPrice == 0) {
            return false;
        }
        
        if (currentPrice >= order.takeProfitPrice) {
            order.isActive = false;
            emit TakeProfitTriggered(order.orderId, order.asset, order.amount, order.takeProfitPrice);
            return true;
        }
        
        return false;
    }
    
    /**
     * @dev Update risk metrics after trade execution
     */
    function updateRiskMetrics(address trader, address asset, uint256 amount, int256 pnl) 
        external override {
        require(msg.sender == address(this) || hasRole(RISK_ADMIN_ROLE, msg.sender), "Unauthorized");
        
        RiskMetrics storage metrics = traderMetrics[trader];
        
        // Calculate new metrics
        uint256 newPositionSize = calculatePositionSize(trader, asset);
        uint256 newPortfolioValue = calculatePortfolioValue(trader);
        int256 newDailyPnL = getDailyPnL(trader).safeAdd(pnl);
        uint256 newLeverage = calculateLeverage(trader, asset);
        
        RiskMetrics memory oldMetrics = metrics;
        
        // Update metrics
        metrics.currentPositionSize = newPositionSize;
        metrics.currentPortfolioValue = newPortfolioValue;
        metrics.dailyPnL = newDailyPnL;
        metrics.currentLeverage = newLeverage;
        metrics.lastUpdate = block.timestamp;
        
        // Check risk limits
        checkRiskLimits(trader);
        
        emit RiskMetricsUpdated(trader, oldMetrics, metrics);
    }
    
    /**
     * @dev Activate circuit breaker
     */
    function activateCircuitBreaker(string memory reason) external override onlyRole(RISK_OFFICER_ROLE) {
        _circuitBreakerActive = true;
        _circuitBreakerReason = reason;
        
        emit CircuitBreakerActivated(reason, msg.sender);
    }
    
    /**
     * @dev Deactivate circuit breaker
     */
    function deactivateCircuitBreaker() external override onlyRole(RISK_ADMIN_ROLE) {
        require(_circuitBreakerActive, "Circuit breaker not active");
        
        string memory reason = _circuitBreakerReason;
        _circuitBreakerActive = false;
        _circuitBreakerReason = "";
        
        emit CircuitBreakerDeactivated(reason, msg.sender);
    }
    
    /**
     * @dev Get risk limits
     */
    function getRiskLimits() external view override returns (RiskLimits memory) {
        return limits;
    }
    
    /**
     * @dev Get risk metrics for a trader
     */
    function getRiskMetrics(address trader) external view override returns (RiskMetrics memory) {
        return traderMetrics[trader];
    }
    
    /**
     * @dev Get order information
     */
    function getOrderInfo(bytes32 orderId) external view override returns (OrderInfo memory) {
        return orders[orderId];
    }
    
    /**
     * @dev Check if circuit breaker is active
     */
    function isCircuitBreakerActive() external view override returns (bool) {
        return _circuitBreakerActive;
    }
    
    /**
     * @dev Calculate maximum position size for an asset
     */
    function calculateMaxPosition(address asset, uint256 portfolioValue) external view override returns (uint256) {
        return limits.maxPositionSize > portfolioValue ? limits.maxPositionSize : portfolioValue.safeMul(20) / 100;
    }
    
    /**
     * @dev Get daily P&L for a trader
     */
    function getDailyPnL(address trader) public view override returns (int256) {
        return dailyPnL[trader];
    }
    
    /**
     * @dev Update asset price for risk calculations
     */
    function updateAssetPrice(address asset, uint256 price, uint256 volume) external onlyRole(RISK_ADMIN_ROLE) {
        require(price > 0, "Invalid price");
        
        MarketData.PriceFeed storage priceFeed = assetPrices[asset];
        priceFeed.price = price;
        priceFeed.volume = volume;
        priceFeed.timestamp = block.timestamp;
        priceFeed.isActive = true;
    }
    
    /**
     * @dev Pause contract for emergency
     */
    function pause() external onlyRole(RISK_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyRole(RISK_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Get circuit breaker reason
     */
    function getCircuitBreakerReason() external view returns (string memory) {
        return _circuitBreakerReason;
    }
    
    /**
     * @dev Internal function to check risk limits
     */
    function checkRiskLimits(address trader) internal {
        RiskMetrics storage metrics = traderMetrics[trader];
        
        // Check position size limit
        if (metrics.currentPositionSize > limits.maxPositionSize) {
            emit RiskLimitBreached(trader, "POSITION_SIZE", metrics.currentPositionSize, limits.maxPositionSize);
        }
        
        // Check portfolio value limit
        if (metrics.currentPortfolioValue > limits.maxPortfolioValue) {
            emit RiskLimitBreached(trader, "PORTFOLIO_VALUE", metrics.currentPortfolioValue, limits.maxPortfolioValue);
        }
        
        // Check daily loss limit
        if (metrics.dailyPnL < limits.maxDailyLoss) {
            emit RiskLimitBreached(trader, "DAILY_LOSS", uint256(-metrics.dailyPnL), uint256(-limits.maxDailyLoss));
        }
        
        // Check leverage limit
        if (metrics.currentLeverage > limits.maxLeverage) {
            emit RiskLimitBreached(trader, "LEVERAGE", metrics.currentLeverage, limits.maxLeverage);
        }
    }
    
    /**
     * @dev Internal function to calculate portfolio value
     */
    function calculatePortfolioValue(address trader) internal view returns (uint256) {
        // This is a simplified calculation
        // In practice, you'd want to aggregate all positions
        return traderMetrics[trader].currentPortfolioValue;
    }
    
    /**
     * @dev Internal function to calculate position size
     */
    function calculatePositionSize(address trader, address asset) internal view returns (uint256) {
        // This is a simplified calculation
        // In practice, you'd want to get actual position data
        return traderMetrics[trader].currentPositionSize;
    }
    
    /**
     * @dev Internal function to calculate leverage
     */
    function calculateLeverage(address trader, address asset) internal view returns (uint256) {
        uint256 portfolioValue = traderMetrics[trader].currentPortfolioValue;
        if (portfolioValue == 0) return 1;
        
        uint256 positionValue = traderMetrics[trader].currentPositionSize;
        return positionValue.safeDiv(portfolioValue);
    }
    
    /**
     * @dev Internal function to record daily P&L
     */
    function recordDailyPnL(address trader, int256 pnl) internal {
        // Reset daily P&L at the start of each day
        uint256 lastUpdate = traderMetrics[trader].lastUpdate;
        if (block.timestamp - lastUpdate >= 24 hours) {
            dailyPnL[trader] = 0;
        }
        
        dailyPnL[trader] = dailyPnL[trader].safeAdd(pnl);
    }
    
    /**
     * @dev Event for order info updates
     */
    event OrderInfoUpdated(bytes32 indexed orderId, string updateType);
}