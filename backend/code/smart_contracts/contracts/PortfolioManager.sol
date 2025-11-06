// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Imports
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../interfaces/IPortfolioManager.sol";
import "../libraries/SecurityUtils.sol";
import "../libraries/MarketData.sol";

/**
 * @title PortfolioManager
 * @dev Portfolio Manager Contract - Multi-asset management
 */
contract PortfolioManager is IPortfolioManager, AccessControl, Pausable, ReentrancyGuard {
    using SecurityUtils for uint256;
    using SafeERC20 for IERC20;
    
    // Roles
    bytes32 public constant PORTFOLIO_ADMIN_ROLE = keccak256("PORTFOLIO_ADMIN_ROLE");
    bytes32 public constant REBALANCER_ROLE = keccak256("REBALANCER_ROLE");
    
    // State variables
    mapping(address => Portfolio) private _portfolios;
    mapping(address => AssetConfig) private _assetConfigs;
    mapping(address => MarketData.PriceFeed) private _assetPrices;
    
    uint256 private _totalPortfolios = 0;
    uint256 private _rebalanceThreshold = 500; // 5% deviation threshold (basis points)
    uint256 private _maxAssetsPerPortfolio = 10;
    
    // Events
    event PortfolioCreated(address indexed owner, address indexed portfolio);
    event AssetConfigUpdated(address indexed asset, AssetConfig oldConfig, AssetConfig newConfig);
    event RebalanceThresholdUpdated(uint256 oldThreshold, uint256 newThreshold);
    event MaxAssetsUpdated(uint256 oldMax, uint256 newMax);
    event PositionUpdated(address indexed trader, address indexed asset, Position oldPosition, Position newPosition);
    event PortfolioValueCalculated(address indexed trader, uint256 totalValue, uint256 lastUpdate);
    
    // Custom errors
    error PortfolioAlreadyExists(address owner);
    error PortfolioNotFound(address owner);
    error AssetAlreadyExists(address asset);
    error AssetNotConfigured(address asset);
    error MaxAssetsExceeded(uint256 current, uint256 max);
    error InvalidWeight(uint256 weight, uint256 maxWeight);
    error RebalanceNotRequired(address trader);
    error InsufficientBalance(address trader, address asset, uint256 required, uint256 available);
    error InvalidPrice(address asset);
    error ZeroAmount();
    error UnauthorizedRebalancer(address caller);
    
    /**
     * @dev Constructor
     */
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(PORTFOLIO_ADMIN_ROLE, msg.sender);
        _grantRole(REBALANCER_ROLE, msg.sender);
    }
    
    /**
     * @dev Create a new portfolio for a trader
     */
    function createPortfolio() external override whenNotPaused returns (address portfolio) {
        if (_portfolios[msg.sender].owner != address(0)) {
            revert PortfolioAlreadyExists(msg.sender);
        }
        
        // Create portfolio
        Portfolio storage newPortfolio = _portfolios[msg.sender];
        newPortfolio.owner = msg.sender;
        newPortfolio.totalValue = 0;
        newPortfolio.lastRebalance = block.timestamp;
        newPortfolio.isActive = true;
        
        _totalPortfolios++;
        portfolio = address(this);
        
        emit PortfolioCreated(msg.sender, portfolio);
        
        return portfolio;
    }
    
    /**
     * @dev Add an asset to the global asset configuration
     */
    function addAsset(address asset, uint256 weight, uint256 maxWeight, uint256 minWeight) 
        external override onlyRole(PORTFOLIO_ADMIN_ROLE) {
        require(weight <= maxWeight, "Weight exceeds maximum");
        require(minWeight <= weight, "Min weight exceeds target weight");
        
        AssetConfig memory config = AssetConfig({
            asset: asset,
            weight: weight,
            maxWeight: maxWeight,
            minWeight: minWeight,
            enabled: true
        });
        
        AssetConfig storage existingConfig = _assetConfigs[asset];
        
        emit AssetConfigUpdated(asset, existingConfig, config);
        
        _assetConfigs[asset] = config;
    }
    
    /**
     * @dev Remove an asset from configuration
     */
    function removeAsset(address asset) external override onlyRole(PORTFOLIO_ADMIN_ROLE) {
        AssetConfig storage config = _assetConfigs[asset];
        if (config.asset == address(0)) {
            revert AssetNotConfigured(asset);
        }
        
        config.enabled = false;
        emit AssetConfigUpdated(asset, config, config);
    }
    
    /**
     * @dev Open a position in a portfolio
     */
    function openPosition(address asset, uint256 amount, uint256 price) 
        external override whenNotPaused nonReentrant {
        Portfolio storage portfolio = _portfolios[msg.sender];
        if (portfolio.owner == address(0)) {
            revert PortfolioNotFound(msg.sender);
        }
        
        if (amount == 0) revert ZeroAmount();
        if (_assetConfigs[asset].asset == address(0)) {
            revert AssetNotConfigured(asset);
        }
        
        Position storage position = portfolio.positions[asset];
        
        // Calculate new average price
        uint256 totalValue = position.amount.safeMul(position.avgPrice).safeAdd(amount.safeMul(price));
        uint256 newAmount = position.amount.safeAdd(amount);
        uint256 newAvgPrice = totalValue.safeDiv(newAmount);
        
        // Update position
        Position memory oldPosition = position;
        position.amount = newAmount;
        position.avgPrice = newAvgPrice;
        position.timestamp = block.timestamp;
        
        // Update portfolio value
        portfolio.totalValue = portfolio.totalValue.safeAdd(amount.safeMul(price));
        
        emit PositionUpdated(msg.sender, asset, oldPosition, position);
    }
    
    /**
     * @dev Close a position in a portfolio
     */
    function closePosition(address asset, uint256 amount, uint256 price) 
        external override whenNotPaused nonReentrant {
        Portfolio storage portfolio = _portfolios[msg.sender];
        if (portfolio.owner == address(0)) {
            revert PortfolioNotFound(msg.sender);
        }
        
        if (amount == 0) revert ZeroAmount();
        
        Position storage position = portfolio.positions[asset];
        if (position.amount == 0) {
            revert InsufficientBalance(msg.sender, asset, amount, 0);
        }
        
        if (amount > position.amount) {
            revert InsufficientBalance(msg.sender, asset, amount, position.amount);
        }
        
        Position memory oldPosition = position;
        
        // Calculate realized P&L
        uint256 costBasis = amount.safeMul(position.avgPrice);
        uint256 currentValue = amount.safeMul(price);
        int256 realizedPnL = int256(currentValue) - int256(costBasis);
        
        position.realizedPnL = position.realizedPnL.safeAdd(uint256(realizedPnL));
        
        // Update position amount
        position.amount = position.amount.safeSub(amount);
        position.timestamp = block.timestamp;
        
        // Update portfolio value
        if (position.amount > 0) {
            portfolio.totalValue = portfolio.totalValue.safeSub(amount.safeMul(price));
        } else {
            // Close entire position
            portfolio.totalValue = portfolio.totalValue.safeSub(position.avgPrice.safeMul(amount));
        }
        
        emit PositionUpdated(msg.sender, asset, oldPosition, position);
    }
    
    /**
     * @dev Update position with current market price
     */
    function updatePosition(address asset, uint256 amount, uint256 price) 
        external override whenNotPaused nonReentrant {
        Portfolio storage portfolio = _portfolios[msg.sender];
        if (portfolio.owner == address(0)) {
            revert PortfolioNotFound(msg.sender);
        }
        
        Position storage position = portfolio.positions[asset];
        if (position.amount == 0) {
            revert PositionNotFound(asset);
        }
        
        // Calculate unrealized P&L
        uint256 currentValue = position.amount.safeMul(price);
        uint256 costBasis = position.amount.safeMul(position.avgPrice);
        int256 unrealizedPnL = int256(currentValue) - int256(costBasis);
        
        Position memory oldPosition = position;
        position.unrealizedPnL = uint256(unrealizedPnL);
        position.timestamp = block.timestamp;
        
        emit PositionUpdated(msg.sender, asset, oldPosition, position);
    }
    
    /**
     * @dev Rebalance portfolio to target weights
     */
    function rebalancePortfolio() external override whenNotPaused nonReentrant {
        Portfolio storage portfolio = _portfolios[msg.sender];
        if (portfolio.owner == address(0)) {
            revert PortfolioNotFound(msg.sender);
        }
        
        if (!hasRole(REBALANCER_ROLE, msg.sender) && msg.sender != portfolio.owner) {
            revert UnauthorizedRebalancer(msg.sender);
        }
        
        // Check if rebalancing is needed
        (bool needsRebalance, AssetConfig[] memory deviations) = calculateRequiredRebalance(msg.sender);
        
        if (!needsRebalance) {
            revert RebalanceNotRequired(msg.sender);
        }
        
        // Perform rebalancing (simplified - would need actual trading logic)
        portfolio.lastRebalance = block.timestamp;
        
        emit PortfolioRebalanced(msg.sender, portfolio.totalValue);
    }
    
    /**
     * @dev Get portfolio information
     */
    function getPortfolio(address owner) external view override returns (Portfolio memory) {
        return _portfolios[owner];
    }
    
    /**
     * @dev Get position for a specific asset
     */
    function getPosition(address owner, address asset) external view override returns (Position memory) {
        return _portfolios[owner].positions[asset];
    }
    
    /**
     * @dev Calculate portfolio value
     */
    function getPortfolioValue(address owner) external view override returns (uint256) {
        Portfolio storage portfolio = _portfolios[owner];
        if (portfolio.owner == address(0)) {
            revert PortfolioNotFound(owner);
        }
        
        uint256 totalValue = 0;
        
        // Get all assets in the portfolio
        address[] memory portfolioAssets = getPortfolioAssets(owner);
        
        for (uint256 i = 0; i < portfolioAssets.length; i++) {
            address asset = portfolioAssets[i];
            Position storage position = portfolio.positions[asset];
            
            if (position.amount > 0) {
                MarketData.PriceFeed storage priceFeed = _assetPrices[asset];
                if (priceFeed.price > 0) {
                    totalValue = totalValue.safeAdd(position.amount.safeMul(priceFeed.price));
                }
            }
        }
        
        return totalValue;
    }
    
    /**
     * @dev Get asset weights configuration
     */
    function getAssetWeights(address owner) external view override returns (AssetConfig[] memory) {
        Portfolio storage portfolio = _portfolios[owner];
        if (portfolio.owner == address(0)) {
            revert PortfolioNotFound(owner);
        }
        
        AssetConfig[] memory configs = new AssetConfig[](_maxAssetsPerPortfolio);
        uint256 configCount = 0;
        
        // Get all configured assets
        address[] memory configuredAssets = getConfiguredAssets();
        
        for (uint256 i = 0; i < configuredAssets.length; i++) {
            AssetConfig storage config = _assetConfigs[configuredAssets[i]];
            if (config.enabled) {
                configs[configCount] = config;
                configCount++;
            }
        }
        
        // Resize array
        AssetConfig[] memory result = new AssetConfig[](configCount);
        for (uint256 i = 0; i < configCount; i++) {
            result[i] = configs[i];
        }
        
        return result;
    }
    
    /**
     * @dev Calculate if rebalancing is required
     */
    function calculateRequiredRebalance(address owner) 
        public view override returns (bool, AssetConfig[] memory) {
        Portfolio storage portfolio = _portfolios[owner];
        if (portfolio.owner == address(0)) {
            revert PortfolioNotFound(owner);
        }
        
        uint256 portfolioValue = getPortfolioValue(owner);
        if (portfolioValue == 0) {
            return (false, new AssetConfig[](0));
        }
        
        AssetConfig[] memory configs = getAssetWeights(owner);
        AssetConfig[] memory deviations = new AssetConfig[](configs.length);
        uint256 deviationCount = 0;
        bool needsRebalance = false;
        
        for (uint256 i = 0; i < configs.length; i++) {
            AssetConfig memory config = configs[i];
            Position storage position = portfolio.positions[config.asset];
            
            if (position.amount > 0) {
                MarketData.PriceFeed storage priceFeed = _assetPrices[config.asset];
                if (priceFeed.price > 0) {
                    uint256 positionValue = position.amount.safeMul(priceFeed.price);
                    uint256 currentWeight = positionValue.safeMul(10000).safeDiv(portfolioValue);
                    
                    // Check if weight deviation exceeds threshold
                    uint256 weightDiff = currentWeight > config.weight ? 
                        currentWeight - config.weight : config.weight - currentWeight;
                    
                    if (weightDiff > _rebalanceThreshold) {
                        needsRebalance = true;
                        deviations[deviationCount] = AssetConfig({
                            asset: config.asset,
                            weight: currentWeight,
                            maxWeight: config.maxWeight,
                            minWeight: config.minWeight,
                            enabled: config.enabled
                        });
                        deviationCount++;
                    }
                }
            }
        }
        
        // Resize deviations array
        AssetConfig[] memory result = new AssetConfig[](deviationCount);
        for (uint256 i = 0; i < deviationCount; i++) {
            result[i] = deviations[i];
        }
        
        return (needsRebalance, result);
    }
    
    /**
     * @dev Update asset price
     */
    function updateAssetPrice(address asset, uint256 price, uint256 volume) 
        external onlyRole(PORTFOLIO_ADMIN_ROLE) {
        require(price > 0, "Invalid price");
        
        MarketData.PriceFeed storage priceFeed = _assetPrices[asset];
        priceFeed.price = price;
        priceFeed.volume = volume;
        priceFeed.timestamp = block.timestamp;
        priceFeed.isActive = true;
    }
    
    /**
     * @dev Get total number of portfolios
     */
    function getTotalPortfolios() external view override returns (uint256) {
        return _totalPortfolios;
    }
    
    /**
     * @dev Update rebalance threshold
     */
    function setRebalanceThreshold(uint256 threshold) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(threshold <= 2000, "Threshold cannot exceed 20%");
        uint256 oldThreshold = _rebalanceThreshold;
        _rebalanceThreshold = threshold;
        emit RebalanceThresholdUpdated(oldThreshold, threshold);
    }
    
    /**
     * @dev Update maximum assets per portfolio
     */
    function setMaxAssetsPerPortfolio(uint256 maxAssets) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(maxAssets > 0, "Max assets must be positive");
        uint256 oldMax = _maxAssetsPerPortfolio;
        _maxAssetsPerPortfolio = maxAssets;
        emit MaxAssetsUpdated(oldMax, maxAssets);
    }
    
    /**
     * @dev Helper function to get portfolio assets
     */
    function getPortfolioAssets(address owner) internal view returns (address[] memory) {
        Portfolio storage portfolio = _portfolios[owner];
        address[] memory assets = new address[](_maxAssetsPerPortfolio);
        uint256 assetCount = 0;
        
        // This is a simplified version - in practice, you'd want to track which assets are actually in use
        address[] memory configuredAssets = getConfiguredAssets();
        
        for (uint256 i = 0; i < configuredAssets.length && assetCount < _maxAssetsPerPortfolio; i++) {
            if (portfolio.positions[configuredAssets[i]].amount > 0) {
                assets[assetCount] = configuredAssets[i];
                assetCount++;
            }
        }
        
        // Resize array
        address[] memory result = new address[](assetCount);
        for (uint256 i = 0; i < assetCount; i++) {
            result[i] = assets[i];
        }
        
        return result;
    }
    
    /**
     * @dev Helper function to get configured assets
     */
    function getConfiguredAssets() internal view returns (address[] memory) {
        // This is a simplified implementation
        // In practice, you'd want to maintain a list of configured assets
        address[] memory assets = new address[](0);
        return assets;
    }
    
    /**
     * @dev Pause contract
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
    
    // Custom errors for better error handling
    error PositionNotFound(address asset);
    error InvalidWeightConfiguration();
    error AssetConfigurationNotFound(address asset);
}