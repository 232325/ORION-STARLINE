// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Imports
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "../interfaces/ISettlement.sol";
import "../interfaces/IFeeManagement.sol";
import "../libraries/SecurityUtils.sol";
import "../libraries/MarketData.sol";

/**
 * @title Settlement
 * @dev Settlement Contract - Order fulfillment va transaction execution
 */
contract Settlement is ISettlement, AccessControl, Pausable, ReentrancyGuard {
    using Counters for Counters.Counter;
    using SecurityUtils for uint256;
    using SafeERC20 for IERC20;
    
    // Roles
    bytes32 public constant SETTLEMENT_ADMIN_ROLE = keccak256("SETTLEMENT_ADMIN_ROLE");
    bytes32 public constant MARKET_MAKER_ROLE = keccak256("MARKET_MAKER_ROLE");
    bytes32 public constant TRADING_BOT_ROLE = keccak256("TRADING_BOT_ROLE");
    
    // State variables
    Counters.Counter private _orderCounter;
    mapping(bytes32 => Order) private _orders;
    mapping(address => bytes32[]) private _traderOrders;
    mapping(address => mapping(ISettlement.OrderSide => bytes32[])) private _orderBook;
    mapping(bytes32 => SettlementInfo) private _settlements;
    mapping(address => bool) private _whitelistedAssets;
    
    IFeeManagement public feeManager;
    
    // Order book limits
    uint256 private _maxOrderAmount = 10000000 * 10**18; // $10M max order
    uint256 private _minOrderAmount = 100 * 10**18; // $100 min order
    uint256 private _maxOrdersPerTrader = 100;
    
    // Events
    event OrderBookUpdated(address indexed asset, ISettlement.OrderSide side, uint256 orderCount);
    event OrderFilled(bytes32 indexed orderId, uint256 filledAmount, uint256 remainingAmount, address indexed counterparty);
    event SettlementExecuted(bytes32 indexed orderId, uint256 totalAmount, uint256 totalFees);
    event AssetWhitelisted(address indexed asset, bool whitelisted);
    event OrderLimitsUpdated(uint256 oldMax, uint256 newMax, uint256 oldMin, uint256 newMin);
    event WhitelistUpdated(address indexed asset, bool whitelisted);
    
    // Custom errors
    error InvalidOrderParameters(address asset, uint256 amount, uint256 price);
    error OrderAmountTooLarge(uint256 amount, uint256 maxAmount);
    error OrderAmountTooSmall(uint256 amount, uint256 minAmount);
    error AssetNotWhitelisted(address asset);
    error MaxOrdersExceeded(address trader, uint256 current, uint256 max);
    error OrderNotFound(bytes32 orderId);
    error OrderExpired(bytes32 orderId);
    error InsufficientBalance(address trader, address asset, uint256 required, uint256 available);
    error SettlementFailed(bytes32 orderId, string reason);
    error UnauthorizedMarketMaker(address maker);
    error InvalidPrice(uint256 price);
    error InvalidStopPrice(uint256 stopPrice, uint256 orderPrice, ISettlement.OrderSide side);
    
    /**
     * @dev Constructor
     */
    constructor(address feeManagerAddress) {
        require(feeManagerAddress != address(0), "Invalid fee manager address");
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(SETTLEMENT_ADMIN_ROLE, msg.sender);
        _grantRole(MARKET_MAKER_ROLE, msg.sender);
        _grantRole(TRADING_BOT_ROLE, msg.sender);
        
        feeManager = IFeeManagement(feeManagerAddress);
    }
    
    /**
     * @dev Create a new order
     */
    function createOrder(
        address asset,
        uint256 amount,
        uint256 price,
        uint256 stopPrice,
        ISettlement.OrderType orderType,
        ISettlement.OrderSide side,
        uint256 expiry
    ) external override whenNotPaused nonReentrant returns (bytes32 orderId) {
        // Validate inputs
        if (!_whitelistedAssets[asset]) {
            revert AssetNotWhitelisted(asset);
        }
        
        if (amount == 0 || price == 0) {
            revert InvalidOrderParameters(asset, amount, price);
        }
        
        if (amount > _maxOrderAmount) {
            revert OrderAmountTooLarge(amount, _maxOrderAmount);
        }
        
        if (amount < _minOrderAmount) {
            revert OrderAmountTooSmall(amount, _minOrderAmount);
        }
        
        if (expiry <= block.timestamp) {
            revert InvalidOrderParameters(asset, amount, price);
        }
        
        // Check maximum orders per trader
        if (_traderOrders[msg.sender].length >= _maxOrdersPerTrader) {
            revert MaxOrdersExceeded(msg.sender, _traderOrders[msg.sender].length, _maxOrdersPerTrader);
        }
        
        // Validate stop prices for stop orders
        if (orderType == ISettlement.OrderType.STOP_LOSS || orderType == ISettlement.OrderType.TAKE_PROFIT) {
            if (stopPrice == 0) {
                revert InvalidOrderParameters(asset, amount, price);
            }
            
            if (side == ISettlement.OrderSide.BUY && stopPrice <= price) {
                revert InvalidStopPrice(stopPrice, price, side);
            }
            
            if (side == ISettlement.OrderSide.SELL && stopPrice >= price) {
                revert InvalidStopPrice(stopPrice, price, side);
            }
        }
        
        // Generate unique order ID
        _orderCounter.increment();
        orderId = keccak256(abi.encodePacked(
            block.timestamp,
            _orderCounter.current(),
            msg.sender,
            asset
        ));
        
        // Create and store order
        Order memory newOrder = Order({
            id: orderId,
            trader: msg.sender,
            asset: asset,
            amount: amount,
            filledAmount: 0,
            price: price,
            stopPrice: stopPrice,
            orderType: orderType,
            side: side,
            status: ISettlement.OrderStatus.PENDING,
            timestamp: block.timestamp,
            expiry: expiry,
            isActive: true
        });
        
        _orders[orderId] = newOrder;
        _traderOrders[msg.sender].push(orderId);
        _orderBook[asset][side].push(orderId);
        
        // Check if order can be executed immediately (market orders)
        if (orderType == ISettlement.OrderType.MARKET) {
            _tryExecuteOrder(orderId);
        }
        
        emit OrderCreated(orderId, msg.sender, asset, amount, price);
        emit OrderBookUpdated(asset, side, _orderBook[asset][side].length);
        
        return orderId;
    }
    
    /**
     * @dev Cancel an order
     */
    function cancelOrder(bytes32 orderId) external override whenNotPaused nonReentrant {
        Order storage order = _orders[orderId];
        
        if (order.id == bytes32(0)) {
            revert OrderNotFound(orderId);
        }
        
        // Only order owner or admin can cancel
        if (order.trader != msg.sender && !hasRole(SETTLEMENT_ADMIN_ROLE, msg.sender)) {
            revert UnauthorizedAccess();
        }
        
        if (!order.isActive || order.status == ISettlement.OrderStatus.FILLED) {
            revert OrderExpired(orderId);
        }
        
        order.isActive = false;
        order.status = ISettlement.OrderStatus.CANCELLED;
        
        emit OrderCancelled(orderId, "Cancelled by user");
        emit OrderBookUpdated(order.asset, order.side, _orderBook[order.asset][order.side].length);
    }
    
    /**
     * @dev Fill an order (called by market makers or execution bots)
     */
    function fillOrder(bytes32 orderId, uint256 fillAmount, uint256 fillPrice, address counterparty) 
        external override whenNotPaused nonReentrant {
        // Only authorized fillers can execute fills
        require(
            hasRole(MARKET_MAKER_ROLE, msg.sender) ||
            hasRole(TRADING_BOT_ROLE, msg.sender) ||
            hasRole(SETTLEMENT_ADMIN_ROLE, msg.sender),
            "Unauthorized filler"
        );
        
        Order storage order = _orders[orderId];
        
        if (order.id == bytes32(0)) {
            revert OrderNotFound(orderId);
        }
        
        if (!order.isActive) {
            revert OrderExpired(orderId);
        }
        
        if (block.timestamp > order.expiry) {
            order.isActive = false;
            order.status = ISettlement.OrderStatus.EXPIRED;
            revert OrderExpired(orderId);
        }
        
        // Validate fill amount
        uint256 remainingAmount = order.amount.safeSub(order.filledAmount);
        if (fillAmount > remainingAmount) {
            revert InvalidOrderParameters(order.asset, fillAmount, fillPrice);
        }
        
        // Calculate fees
        uint256 feeAmount = feeManager.calculateFee(
            orderId,
            order.trader,
            order.asset,
            fillAmount,
            fillPrice,
            hasRole(MARKET_MAKER_ROLE, counterparty)
        );
        
        // Update order fill
        order.filledAmount = order.filledAmount.safeAdd(fillAmount);
        
        // Check if order is fully filled
        if (order.filledAmount >= order.amount) {
            order.isActive = false;
            order.status = ISettlement.OrderStatus.FILLED;
        } else {
            order.status = ISettlement.OrderStatus.PARTIALLY_FILLED;
        }
        
        // Create fill info
        FillInfo memory fillInfo = FillInfo({
            amount: fillAmount,
            price: fillPrice,
            fee: feeAmount,
            timestamp: block.timestamp,
            counterparty: counterparty
        });
        
        // Store settlement info
        SettlementInfo storage settlement = _settlements[orderId];
        if (settlement.orderId == bytes32(0)) {
            settlement.orderId = orderId;
            settlement.totalAmount = 0;
            settlement.totalFee = 0;
            settlement.avgPrice = 0;
            settlement.settled = false;
            settlement.settlementTimestamp = 0;
        }
        
        settlement.totalAmount = settlement.totalAmount.safeAdd(fillAmount);
        settlement.totalFee = settlement.totalFee.safeAdd(feeAmount);
        
        // Calculate new average price
        settlement.avgPrice = (
            settlement.avgPrice.safeMul(settlement.totalAmount.safeSub(fillAmount))
        ).safeAdd(fillPrice.safeMul(fillAmount)).safeDiv(settlement.totalAmount);
        
        emit OrderFilled(orderId, fillAmount, order.amount.safeSub(order.filledAmount), counterparty);
        emit OrderBookUpdated(order.asset, order.side, _orderBook[order.asset][order.side].length);
        
        // If order is fully filled, settle it
        if (order.status == ISettlement.OrderStatus.FILLED) {
            _settleOrderInternal(orderId);
        }
    }
    
    /**
     * @dev Settle order and execute transfers
     */
    function settleOrder(bytes32 orderId) external override whenNotPaused nonReentrant returns (bool success) {
        return _settleOrderInternal(orderId);
    }
    
    /**
     * @dev Batch fill multiple orders
     */
    function batchFill(
        bytes32[] memory orderIds,
        uint256[] memory fillAmounts,
        uint256[] memory fillPrices,
        address[] memory counterparties
    ) external override whenNotPaused nonReentrant {
        require(
            hasRole(MARKET_MAKER_ROLE, msg.sender) ||
            hasRole(TRADING_BOT_ROLE, msg.sender) ||
            hasRole(SETTLEMENT_ADMIN_ROLE, msg.sender),
            "Unauthorized filler"
        );
        
        require(
            orderIds.length == fillAmounts.length &&
            fillAmounts.length == fillPrices.length &&
            fillPrices.length == counterparties.length,
            "Array length mismatch"
        );
        
        for (uint256 i = 0; i < orderIds.length; i++) {
            fillOrder(orderIds[i], fillAmounts[i], fillPrices[i], counterparties[i]);
        }
    }
    
    /**
     * @dev Batch cancel orders
     */
    function batchCancel(bytes32[] memory orderIds) external override whenNotPaused nonReentrant {
        for (uint256 i = 0; i < orderIds.length; i++) {
            cancelOrder(orderIds[i]);
        }
    }
    
    /**
     * @dev Batch settle orders
     */
    function batchSettle(bytes32[] memory orderIds) external override whenNotPaused nonReentrant returns (bool[] memory success) {
        success = new bool[](orderIds.length);
        
        for (uint256 i = 0; i < orderIds.length; i++) {
            success[i] = _settleOrderInternal(orderIds[i]);
        }
        
        return success;
    }
    
    /**
     * @dev Get order information
     */
    function getOrder(bytes32 orderId) external view override returns (Order memory) {
        return _orders[orderId];
    }
    
    /**
     * @dev Get active orders for a trader
     */
    function getActiveOrders(address trader) external view override returns (bytes32[] memory) {
        bytes32[] memory traderOrders = _traderOrders[trader];
        uint256 activeCount = 0;
        
        // Count active orders
        for (uint256 i = 0; i < traderOrders.length; i++) {
            Order storage order = _orders[traderOrders[i]];
            if (order.isActive && order.status == ISettlement.OrderStatus.PENDING) {
                activeCount++;
            }
        }
        
        // Create result array
        bytes32[] memory activeOrders = new bytes32[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < traderOrders.length; i++) {
            Order storage order = _orders[traderOrders[i]];
            if (order.isActive && order.status == ISettlement.OrderStatus.PENDING) {
                activeOrders[index] = traderOrders[i];
                index++;
            }
        }
        
        return activeOrders;
    }
    
    /**
     * @dev Get order book for an asset
     */
    function getOrderBook(address asset, ISettlement.OrderSide side) external view override returns (Order[] memory) {
        bytes32[] memory orderIds = _orderBook[asset][side];
        uint256 activeCount = 0;
        
        // Count active orders
        for (uint256 i = 0; i < orderIds.length; i++) {
            Order storage order = _orders[orderIds[i]];
            if (order.isActive) {
                activeCount++;
            }
        }
        
        // Create result array
        Order[] memory activeOrders = new Order[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < orderIds.length; i++) {
            Order storage order = _orders[orderIds[i]];
            if (order.isActive) {
                activeOrders[index] = order;
                index++;
            }
        }
        
        return activeOrders;
    }
    
    /**
     * @dev Get settlement information
     */
    function getSettlementInfo(bytes32 orderId) external view override returns (SettlementInfo memory) {
        return _settlements[orderId];
    }
    
    /**
     * @dev Calculate fees for an order
     */
    function calculateFees(bytes32 orderId, uint256 fillAmount) external view override returns (uint256) {
        Order storage order = _orders[orderId];
        if (order.id == bytes32(0)) {
            revert OrderNotFound(orderId);
        }
        
        return feeManager.calculateFee(
            orderId,
            order.trader,
            order.asset,
            fillAmount,
            order.price,
            false // Assume taker fee for calculation
        );
    }
    
    /**
     * @dev Check if order is expired
     */
    function isOrderExpired(bytes32 orderId) external view override returns (bool) {
        Order storage order = _orders[orderId];
        return block.timestamp > order.expiry;
    }
    
    /**
     * @dev Set order expiry
     */
    function setOrderExpiry(bytes32 orderId, uint256 expiry) external override onlyRole(SETTLEMENT_ADMIN_ROLE) {
        Order storage order = _orders[orderId];
        if (order.id == bytes32(0)) {
            revert OrderNotFound(orderId);
        }
        
        require(expiry > block.timestamp, "Expiry must be in future");
        order.expiry = expiry;
    }
    
    /**
     * @dev Set maximum order amount
     */
    function setMaxOrderAmount(uint256 maxAmount) external override onlyRole(SETTLEMENT_ADMIN_ROLE) {
        require(maxAmount > _minOrderAmount, "Max amount must exceed min amount");
        uint256 oldMax = _maxOrderAmount;
        _maxOrderAmount = maxAmount;
        emit OrderLimitsUpdated(oldMax, maxAmount, _minOrderAmount, _minOrderAmount);
    }
    
    /**
     * @dev Set minimum order amount
     */
    function setMinOrderAmount(uint256 minAmount) external override onlyRole(SETTLEMENT_ADMIN_ROLE) {
        require(minAmount > 0 && minAmount < _maxOrderAmount, "Invalid min amount");
        uint256 oldMin = _minOrderAmount;
        _minOrderAmount = minAmount;
        emit OrderLimitsUpdated(_maxOrderAmount, _maxOrderAmount, oldMin, minAmount);
    }
    
    /**
     * @dev Pause trading
     */
    function pauseTrading() external override onlyRole(SETTLEMENT_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause trading
     */
    function unpauseTrading() external override onlyRole(SETTLEMENT_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Add/remove asset from whitelist
     */
    function setAssetWhitelist(address asset, bool whitelisted) external onlyRole(SETTLEMENT_ADMIN_ROLE) {
        _whitelistedAssets[asset] = whitelisted;
        emit AssetWhitelisted(asset, whitelisted);
    }
    
    /**
     * @dev Internal function to try execute market orders
     */
    function _tryExecuteOrder(bytes32 orderId) internal {
        Order storage order = _orders[orderId];
        
        // Simplified execution logic for market orders
        // In practice, this would match against existing orders in the order book
        // For now, we'll just mark it as pending for manual execution
        
        // This is a placeholder - actual order matching would happen here
    }
    
    /**
     * @dev Internal function to settle order
     */
    function _settleOrderInternal(bytes32 orderId) internal returns (bool success) {
        SettlementInfo storage settlement = _settlements[orderId];
        Order storage order = _orders[orderId];
        
        if (order.id == bytes32(0)) {
            revert OrderNotFound(orderId);
        }
        
        if (settlement.settled) {
            return true; // Already settled
        }
        
        if (order.status != ISettlement.OrderStatus.FILLED) {
            revert SettlementFailed(orderId, "Order not fully filled");
        }
        
        // Calculate total value
        uint256 totalValue = settlement.totalAmount.safeMul(settlement.avgPrice);
        
        // Transfer funds (simplified - would need proper escrow/margin logic)
        // This is where you would handle actual asset transfers
        
        settlement.settled = true;
        settlement.settlementTimestamp = block.timestamp;
        
        // Collect fees
        feeManager.collectFee(
            orderId,
            order.trader,
            order.asset,
            settlement.totalAmount,
            settlement.avgPrice,
            true // isMaker (would be determined by actual order flow)
        );
        
        emit SettlementExecuted(orderId, settlement.totalAmount, settlement.totalFee);
        
        return true;
    }
    
    // Custom errors
    error UnauthorizedAccess();
    
    /**
     * @dev Event for additional logging
     */
    event OrderExecuted(bytes32 indexed orderId, address indexed executor, uint256 amount, uint256 price);
}