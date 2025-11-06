// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/**
 * @title MetalDerivativesNFT
 * @notice ERC-1155 based metal derivatives and hedging
 * @dev Supports fungible metal-backed derivatives
 */
contract MetalDerivativesNFT is ERC1155, Ownable, Pausable, ReentrancyGuard {
    
    struct MetalDerivative {
        string symbol; // XAU, XAG, XPT, XPD
        uint256 strikePrice;
        uint256 expiry;
        bool isCall;
        uint256 premium;
        uint256 openInterest;
        bool isActive;
    }
    
    struct PortfolioMetrics {
        uint256 totalValueLocked;
        uint256 delta;
        uint256 gamma;
        uint256 theta;
        uint256 vega;
        int256 pnl;
    }
    
    mapping(uint256 => MetalDerivative) public derivatives;
    mapping(uint256 => AggregatorV3Interface) public metalFeeds;
    mapping(address => mapping(uint256 => uint256)) public balances;
    mapping(address => PortfolioMetrics) public portfolioMetrics;
    
    uint256 public nextDerivativeId = 1;
    uint256 public totalOpenInterest;
    uint256 public marginRequirement = 1000; // 10% in basis points
    uint256 public liquidationThreshold = 15000; // 150% margin requirement
    
    // Metal Type constants for multi-token support
    uint256 constant GOLD_DERIVATIVE = 1;
    uint256 constant SILVER_DERIVATIVE = 2;
    uint256 constant PLATINUM_DERIVATIVE = 3;
    uint256 constant PALLADIUM_DERIVATIVE = 4;
    
    event DerivativeCreated(
        uint256 indexed derivativeId,
        string symbol,
        uint256 strikePrice,
        uint256 expiry,
        bool isCall
    );
    
    event DerivativePurchased(
        address indexed buyer,
        uint256 indexed derivativeId,
        uint256 quantity,
        uint256 premium
    );
    
    event DerivativeExercised(
        address indexed holder,
        uint256 indexed derivativeId,
        uint256 quantity
    );
    
    event PortfolioRebalanced(
        address indexed portfolio,
        uint256 newDelta,
        uint256 newGamma
    );
    
    constructor() ERC1155("") {
        // Initialize base URI and metal feeds
    }
    
    /**
     * @notice Create new metal derivative
     * @param symbol Metal symbol (XAU, XAG, XPT, XPD)
     * @param strikePrice Strike price in USD
     * @param expiry Expiry timestamp
     * @param isCall Whether it's a call option
     * @param initialPremium Initial premium per unit
     */
    function createDerivative(
        string memory symbol,
        uint256 strikePrice,
        uint256 expiry,
        bool isCall,
        uint256 initialPremium
    ) external onlyOwner returns (uint256) {
        require(expiry > block.timestamp, "Invalid expiry");
        require(strikePrice > 0, "Invalid strike price");
        
        uint256 derivativeId = nextDerivativeId++;
        
        derivatives[derivativeId] = MetalDerivative({
            symbol: symbol,
            strikePrice: strikePrice,
            expiry: expiry,
            isCall: isCall,
            premium: initialPremium,
            openInterest: 0,
            isActive: true
        });
        
        emit DerivativeCreated(derivativeId, symbol, strikePrice, expiry, isCall);
        return derivativeId;
    }
    
    /**
     * @notice Purchase metal derivative
     * @param derivativeId Derivative ID to purchase
     * @param quantity Quantity to purchase
     */
    function purchaseDerivative(uint256 derivativeId, uint256 quantity) 
        external 
        payable 
        nonReentrant 
        whenNotPaused 
    {
        MetalDerivative storage derivative = derivatives[derivativeId];
        require(derivative.isActive, "Derivative inactive");
        require(block.timestamp < derivative.expiry, "Derivative expired");
        
        uint256 totalPremium = derivative.premium * quantity;
        require(msg.value >= totalPremium, "Insufficient premium");
        
        // Update balances
        balances[msg.sender][derivativeId] += quantity;
        derivative.openInterest += quantity;
        totalOpenInterest += quantity;
        
        // Update portfolio metrics
        updatePortfolioMetrics(msg.sender, derivativeId, quantity, true);
        
        _mint(msg.sender, derivativeId, quantity, "");
        
        emit DerivativePurchased(msg.sender, derivativeId, quantity, totalPremium);
    }
    
    /**
     * @notice Exercise derivative
     * @param derivativeId Derivative ID to exercise
     * @param quantity Quantity to exercise
     */
    function exerciseDerivative(uint256 derivativeId, uint256 quantity) 
        external 
        nonReentrant 
    {
        require(balances[msg.sender][derivativeId] >= quantity, "Insufficient balance");
        require(derivatives[derivativeId].isActive, "Derivative inactive");
        
        MetalDerivative storage derivative = derivatives[derivativeId];
        require(block.timestamp >= derivative.expiry, "Not expired yet");
        
        uint256 currentMetalPrice = getMetalPrice(getMetalType(derivative.symbol));
        int256 intrinsicValue = 0;
        
        if (derivative.isCall && currentMetalPrice > derivative.strikePrice) {
            intrinsicValue = int256(currentMetalPrice - derivative.strikePrice) * int256(quantity);
        } else if (!derivative.isCall && currentMetalPrice < derivative.strikePrice) {
            intrinsicValue = int256(derivative.strikePrice - currentMetalPrice) * int256(quantity);
        }
        
        // Transfer intrinsic value if positive
        if (intrinsicValue > 0) {
            payable(msg.sender).transfer(uint256(intrinsicValue));
        }
        
        // Update balances and metrics
        balances[msg.sender][derivativeId] -= quantity;
        derivative.openInterest -= quantity;
        totalOpenInterest -= quantity;
        
        updatePortfolioMetrics(msg.sender, derivativeId, quantity, false);
        
        _burn(msg.sender, derivativeId, quantity);
        
        emit DerivativeExercised(msg.sender, derivativeId, quantity);
    }
    
    /**
     * @notice Update derivative premium using Black-Scholes-like pricing
     * @param derivativeId Derivative ID
     * @param newPremium New premium price
     */
    function updatePremium(uint256 derivativeId, uint256 newPremium) 
        external 
        onlyOwner 
    {
        require(derivatives[derivativeId].isActive, "Derivative inactive");
        derivatives[derivativeId].premium = newPremium;
    }
    
    /**
     * @notice Calculate option Greeks for portfolio
     * @param portfolio Portfolio address
     * @return delta Total delta exposure
     * @return gamma Total gamma exposure
     * @return theta Time decay
     * @return vega Volatility exposure
     */
    function calculateGreeks(address portfolio) 
        external 
        view 
        returns (
            uint256 delta,
            uint256 gamma,
            uint256 theta,
            uint256 vega
        ) 
    {
        PortfolioMetrics storage metrics = portfolioMetrics[portfolio];
        return (metrics.delta, metrics.gamma, metrics.theta, metrics.vega);
    }
    
    /**
     * @notice Auto-rebalance portfolio based on risk metrics
     * @param portfolio Portfolio address
     * @param targetDelta Target delta exposure
     */
    function rebalancePortfolio(address portfolio, uint256 targetDelta) 
        external 
        onlyOwner 
        nonReentrant 
    {
        PortfolioMetrics storage metrics = portfolioMetrics[portfolio];
        uint256 currentDelta = metrics.delta;
        
        if (currentDelta > targetDelta) {
            // Reduce delta by selling derivatives
            uint256 deltaToReduce = currentDelta - targetDelta;
            reduceDelta(portfolio, deltaToReduce);
        } else if (currentDelta < targetDelta) {
            // Increase delta by buying derivatives
            uint256 deltaToIncrease = targetDelta - currentDelta;
            increaseDelta(portfolio, deltaToIncrease);
        }
        
        emit PortfolioRebalanced(portfolio, metrics.delta, metrics.gamma);
    }
    
    /**
     * @notice Get current metal price
     * @param symbol Metal symbol
     * @return price Current price in USD
     */
    function getMetalPrice(uint256 metalType) internal view returns (uint256) {
        AggregatorV3Interface priceFeed = metalFeeds[metalType];
        require(address(priceFeed) != address(0), "Price feed not set");
        
        (
            uint80 roundId,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        
        require(price > 0, "Invalid price");
        return uint256(price);
    }
    
    /**
     * @notice Get metal type from symbol
     * @param symbol Metal symbol
     * @return metalType Metal type ID
     */
    function getMetalType(string memory symbol) internal pure returns (uint256) {
        if (keccak256(bytes(symbol)) == keccak256(bytes("XAU"))) return GOLD_DERIVATIVE;
        if (keccak256(bytes(symbol)) == keccak256(bytes("XAG"))) return SILVER_DERIVATIVE;
        if (keccak256(bytes(symbol)) == keccak256(bytes("XPT"))) return PLATINUM_DERIVATIVE;
        if (keccak256(bytes(symbol)) == keccak256(bytes("XPD"))) return PALLADIUM_DERIVATIVE;
        revert("Unknown metal symbol");
    }
    
    /**
     * @notice Update portfolio metrics after trade
     */
    function updatePortfolioMetrics(
        address portfolio,
        uint256 derivativeId,
        uint256 quantity,
        bool isPurchase
    ) internal {
        MetalDerivative storage derivative = derivatives[derivativeId];
        
        // Simplified Greeks calculation
        uint256 currentMetalPrice = getMetalPrice(getMetalType(derivative.symbol));
        int256 timeToExpiry = int256(derivative.expiry - block.timestamp);
        
        // Delta calculation (simplified)
        int256 delta = calculateDelta(
            derivative.isCall,
            currentMetalPrice,
            derivative.strikePrice,
            timeToExpiry,
            getMetalVolatility(getMetalType(derivative.symbol))
        );
        
        if (isPurchase) {
            portfolioMetrics[portfolio].delta += uint256(delta) * quantity;
            portfolioMetrics[portfolio].gamma += quantity * 1000; // Simplified gamma
            portfolioMetrics[portfolio].theta -= quantity * 50; // Time decay
            portfolioMetrics[portfolio].vega += quantity * 1000; // Simplified vega
        } else {
            portfolioMetrics[portfolio].delta -= uint256(delta) * quantity;
            portfolioMetrics[portfolio].gamma -= quantity * 1000;
            portfolioMetrics[portfolio].theta += quantity * 50;
            portfolioMetrics[portfolio].vega -= quantity * 1000;
        }
    }
    
    /**
     * @notice Calculate option delta (simplified Black-Scholes)
     */
    function calculateDelta(
        bool isCall,
        uint256 spotPrice,
        uint256 strikePrice,
        int256 timeToExpiry,
        uint256 volatility
    ) internal pure returns (int256) {
        // Simplified delta calculation
        // In production, would use full Black-Scholes formula
        int256 moneyness = int256(spotPrice) - int256(strikePrice);
        
        if (isCall) {
            return moneyness > 0 ? 1000 : 500; // Simplified binary delta
        } else {
            return moneyness < 0 ? -1000 : -500; // Simplified binary delta
        }
    }
    
    /**
     * @notice Get metal volatility
     */
    function getMetalVolatility(uint256 metalType) internal pure returns (uint256) {
        if (metalType == GOLD_DERIVATIVE) return 1500; // 15%
        if (metalType == SILVER_DERIVATIVE) return 3000; // 30%
        if (metalType == PLATINUM_DERIVATIVE) return 2500; // 25%
        return 4000; // Palladium - 40%
    }
    
    /**
     * @notice Reduce delta exposure
     */
    function reduceDelta(address portfolio, uint256 deltaReduction) internal {
        // Implementation for reducing delta exposure
        // Would involve selling derivatives or hedging
    }
    
    /**
     * @notice Increase delta exposure
     */
    function increaseDelta(address portfolio, uint256 deltaIncrease) internal {
        // Implementation for increasing delta exposure
        // Would involve buying derivatives
    }
    
    /**
     * @notice Set metal price feed
     */
    function setMetalFeed(uint256 metalType, address feedAddress) external onlyOwner {
        metalFeeds[metalType] = AggregatorV3Interface(feedAddress);
    }
    
    /**
     * @notice Emergency pause
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @notice Unpause
     */
    function unpause() external onlyOwner {
        _unpause();
    }
}