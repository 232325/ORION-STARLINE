// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IPortfolioManager Interface
 * @dev Portfolio Manager Contract interfeysi - Multi-asset management
 */
interface IPortfolioManager {
    // Events
    event AssetAdded(address indexed asset, uint256 weight);
    event AssetRemoved(address indexed asset);
    event PortfolioRebalanced(address indexed rebalancer, uint256 totalValue);
    event PositionOpened(address indexed trader, address indexed asset, uint256 amount);
    event PositionClosed(address indexed trader, address indexed asset, uint256 amount);
    
    // Structs
    struct Portfolio {
        address owner;
        address[] assets;
        mapping(address => Position) positions;
        uint256 totalValue;
        uint256 lastRebalance;
        bool isActive;
    }
    
    struct Position {
        uint256 amount;
        uint256 avgPrice;
        uint256 unrealizedPnL;
        uint256 realizedPnL;
        uint256 timestamp;
    }
    
    struct AssetConfig {
        address asset;
        uint256 weight; // 0-10000 basis points
        uint256 maxWeight;
        uint256 minWeight;
        bool enabled;
    }
    
    // Core Functions
    function createPortfolio() external returns (address portfolio);
    
    function addAsset(address asset, uint256 weight, uint256 maxWeight, uint256 minWeight) external;
    
    function removeAsset(address asset) external;
    
    function openPosition(address asset, uint256 amount, uint256 price) external;
    
    function closePosition(address asset, uint256 amount, uint256 price) external;
    
    function rebalancePortfolio() external;
    
    function updatePosition(address asset, uint256 amount, uint256 price) external;
    
    // View Functions
    function getPortfolio(address owner) external view returns (Portfolio memory);
    
    function getPosition(address owner, address asset) external view returns (Position memory);
    
    function getPortfolioValue(address owner) external view returns (uint256);
    
    function getAssetWeights(address owner) external view returns (AssetConfig[] memory);
    
    function calculateRequiredRebalance(address owner) external view returns (bool, AssetConfig[] memory);
    
    function getTotalPortfolios() external view returns (uint256);
}