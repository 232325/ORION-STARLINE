// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/**
 * @title MetalHedgeNFT
 * @notice Physical metal-backed NFT hedging strategy
 * @dev ERC-721 based metal hedging with oracle integration
 */
contract MetalHedgeNFT is ERC721, ERC721Enumerable, Ownable, Pausable, ReentrancyGuard {
    
    enum MetalType { GOLD, SILVER, PLATINUM, PALLADIUM }
    
    struct MetalPosition {
        MetalType metalType;
        uint256 metalAmount; // in grams
        uint256 purchasePrice; // USD per troy ounce
        uint256 currentPrice; // USD per troy ounce
        uint256 hedgeRatio; // 0-10000 basis points
        bool isActive;
        uint256 createdAt;
        uint256 lastRebalanced;
    }
    
    struct HedgingMetrics {
        int256 pnl; // Profit/Loss
        uint256 volatility;
        uint256 sharpeRatio;
        int256 maxDrawdown;
        uint256 beta; // Correlation with metal index
    }
    
    // NFT ID to Metal Position
    mapping(uint256 => MetalPosition) public positions;
    mapping(MetalType => AggregatorV3Interface) public priceFeeds;
    mapping(address => bool) public authorizedManagers;
    mapping(address => HedgingMetrics) public userMetrics;
    
    uint256 public totalAUM; // Assets Under Management
    uint256 public performanceFee = 200; // 2% in basis points
    uint256 public managementFee = 50; // 0.5% in basis points
    uint256 public highWaterMark;
    uint256 public nextTokenId = 1;
    
    uint256 private constant BASIS_POINTS = 10000;
    uint256 private constant GRAMS_PER_TROY_OUNCE = 31.1035;
    
    event PositionCreated(
        uint256 indexed tokenId,
        MetalType metalType,
        uint256 metalAmount,
        uint256 hedgeRatio
    );
    
    event PositionRebalanced(
        uint256 indexed tokenId,
        uint256 newHedgeRatio,
        uint256 newPrice
    );
    
    event FeesUpdated(uint256 newPerformanceFee, uint256 newManagementFee);
    
    modifier onlyAuthorized() {
        require(
            owner() == msg.sender || authorizedManagers[msg.sender],
            "Not authorized"
        );
        _;
    }
    
    constructor() ERC721("MetalHedgeNFT", "MHNFT") {
        // Initialize price feeds (would need to be set via functions)
    }
    
    /**
     * @notice Create a new metal-backed NFT position
     * @param metalType The type of metal
     * @param metalAmount Amount in grams
     * @param hedgeRatio Initial hedge ratio (0-10000 basis points)
     */
    function createPosition(
        MetalType metalType,
        uint256 metalAmount,
        uint256 hedgeRatio
    ) external payable nonReentrant whenNotPaused returns (uint256) {
        require(hedgeRatio <= BASIS_POINTS, "Invalid hedge ratio");
        require(metalAmount > 0, "Invalid amount");
        
        uint256 tokenId = nextTokenId++;
        
        // Calculate position value in USD
        uint256 metalPriceUSD = getMetalPrice(metalType);
        uint256 positionValueUSD = (metalAmount * metalPriceUSD) / GRAMS_PER_TROY_OUNCE;
        
        require(msg.value >= positionValueUSD, "Insufficient payment");
        
        positions[tokenId] = MetalPosition({
            metalType: metalType,
            metalAmount: metalAmount,
            purchasePrice: metalPriceUSD,
            currentPrice: metalPriceUSD,
            hedgeRatio: hedgeRatio,
            isActive: true,
            createdAt: block.timestamp,
            lastRebalanced: block.timestamp
        });
        
        totalAUM += positionValueUSD;
        _mint(msg.sender, tokenId);
        
        emit PositionCreated(tokenId, metalType, metalAmount, hedgeRatio);
        return tokenId;
    }
    
    /**
     * @notice Rebalance position hedge ratio
     * @param tokenId NFT position ID
     * @param newHedgeRatio New hedge ratio
     */
    function rebalancePosition(uint256 tokenId, uint256 newHedgeRatio)
        external
        onlyAuthorized
        nonReentrant
    {
        require(_exists(tokenId), "Position doesn't exist");
        require(newHedgeRatio <= BASIS_POINTS, "Invalid hedge ratio");
        
        MetalPosition storage position = positions[tokenId];
        require(position.isActive, "Position inactive");
        
        uint256 oldHedgeRatio = position.hedgeRatio;
        position.hedgeRatio = newHedgeRatio;
        position.currentPrice = getMetalPrice(position.metalType);
        position.lastRebalanced = block.timestamp;
        
        emit PositionRebalanced(tokenId, newHedgeRatio, position.currentPrice);
    }
    
    /**
     * @notice Calculate dynamic hedge ratio based on volatility
     * @param tokenId NFT position ID
     * @param targetVolatility Target volatility level
     */
    function calculateDynamicHedge(uint256 tokenId, uint256 targetVolatility)
        external
        view
        returns (uint256)
    {
        MetalPosition storage position = positions[tokenId];
        
        uint256 volatility = calculateMetalVolatility(position.metalType);
        uint256 currentHedgeRatio = position.hedgeRatio;
        
        // Dynamic adjustment based on volatility
        uint256 volatilityAdjustment = (volatility * 10000) / targetVolatility;
        uint256 newHedgeRatio = (currentHedgeRatio * volatilityAdjustment) / 10000;
        
        return min(newHedgeRatio, BASIS_POINTS);
    }
    
    /**
     * @notice Get metal price from oracle
     * @param metalType The type of metal
     * @return price USD price per troy ounce
     */
    function getMetalPrice(MetalType metalType) public view returns (uint256) {
        AggregatorV3Interface priceFeed = priceFeeds[metalType];
        require(address(priceFeed) != address(0), "Price feed not set");
        
        (
            uint80 roundId,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        
        require(price > 0, "Invalid price");
        require(block.timestamp - updatedAt < 86400, "Price too old"); // 24 hours
        
        return uint256(price);
    }
    
    /**
     * @notice Calculate position P&L
     * @param tokenId NFT position ID
     * @return pnl Profit/Loss in USD
     */
    function calculatePnL(uint256 tokenId) external view returns (int256) {
        MetalPosition storage position = positions[tokenId];
        require(position.isActive, "Position inactive");
        
        int256 currentValue = int256(
            (position.metalAmount * position.currentPrice) / GRAMS_PER_TROY_OUNCE
        );
        int256 purchaseValue = int256(
            (position.metalAmount * position.purchasePrice) / GRAMS_PER_TROY_OUNCE
        );
        
        return currentValue - purchaseValue;
    }
    
    /**
     * @notice Calculate Sharpe ratio for position
     * @param tokenId NFT position ID
     * @return sharpe The Sharpe ratio
     */
    function calculateSharpeRatio(uint256 tokenId) external view returns (uint256) {
        MetalPosition storage position = positions[tokenId];
        
        int256 pnl = int256(
            (position.metalAmount * (position.currentPrice - position.purchasePrice)) /
                GRAMS_PER_TROY_OUNCE
        );
        
        uint256 returns = uint256((pnl * BASIS_POINTS) / int256(position.currentPrice));
        uint256 volatility = calculateMetalVolatility(position.metalType);
        
        if (volatility == 0) return 0;
        return (returns * BASIS_POINTS) / volatility;
    }
    
    /**
     * @notice Calculate metal volatility (simplified)
     * @param metalType The type of metal
     * @return volatility Standard deviation of returns
     */
    function calculateMetalVolatility(MetalType metalType) 
        internal 
        view 
        returns (uint256) 
    {
        // Simplified volatility calculation
        // In production, would use historical price data
        if (metalType == MetalType.GOLD) return 1500; // 15% annualized
        if (metalType == MetalType.SILVER) return 3000; // 30% annualized
        if (metalType == MetalType.PLATINUM) return 2500; // 25% annualized
        return 4000; // Palladium - 40% annualized
    }
    
    /**
     * @notice Set price feed for metal type
     * @param metalType The metal type
     * @param priceFeed Chainlink price feed address
     */
    function setPriceFeed(MetalType metalType, address priceFeed) external onlyOwner {
        priceFeeds[metalType] = AggregatorV3Interface(priceFeed);
    }
    
    /**
     * @notice Set authorized manager
     * @param manager Manager address
     * @param authorized Authorization status
     */
    function setAuthorizedManager(address manager, bool authorized) external onlyOwner {
        authorizedManagers[manager] = authorized;
    }
    
    /**
     * @notice Update fee structure
     * @param newPerformanceFee New performance fee (basis points)
     * @param newManagementFee New management fee (basis points)
     */
    function updateFees(uint256 newPerformanceFee, uint256 newManagementFee) 
        external 
        onlyOwner 
    {
        require(newPerformanceFee <= 1000, "Performance fee too high"); // Max 10%
        require(newManagementFee <= 200, "Management fee too high"); // Max 2%
        
        performanceFee = newPerformanceFee;
        managementFee = newManagementFee;
        
        emit FeesUpdated(newPerformanceFee, newManagementFee);
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
    
    /**
     * @notice Withdraw fees
     */
    function withdrawFees() external onlyOwner {
        uint256 totalFees = calculateTotalFees();
        payable(owner()).transfer(totalFees);
    }
    
    /**
     * @notice Calculate total fees owed
     */
    function calculateTotalFees() public view returns (uint256) {
        int256 performanceAmount = 0;
        if (totalAUM > highWaterMark) {
            performanceAmount = int256(totalAUM - highWaterMark) * int256(performanceFee) / int256(BASIS_POINTS);
        }
        
        uint256 managementAmount = (totalAUM * managementFee) / BASIS_POINTS;
        return uint256(performanceAmount + int256(managementAmount));
    }
    
    // Utility functions
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
    
    // Override required by Solidity
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId
    ) internal override(ERC721, ERC721Enumerable) {
        super._beforeTokenTransfer(from, to, tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}