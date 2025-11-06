// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IMetalToken Interface
 * @dev Metal Token interfeysi - Oltin, kumush, platina, palladiy
 */
interface IMetalToken {
    // Events
    event MetalPriceUpdated(MetalType indexed metal, uint256 pricePerOunce, uint256 timestamp);
    event StorageUpdate(address indexed storage, uint256 capacity, bool active);
    event MetalDeposit(address indexed metal, address indexed depositor, uint256 amount);
    event MetalWithdrawal(address indexed metal, address indexed withdrawer, uint256 amount);
    
    // Enums
    enum MetalType {
        GOLD,
        SILVER,
        PLATINUM,
        PALLADIUM
    }
    
    // Structs
    struct MetalInfo {
        MetalType metal;
        string symbol;
        string name;
        uint256 purity;        // 999 = 99.9% pure
        uint256 weightPerUnit; // Weight per token in grams
        uint256 currentPrice;  // Price per ounce in USD
        uint256 lastUpdate;
        bool active;
    }
    
    struct StorageInfo {
        address storage;
        string name;
        uint256 capacity;
        uint256 currentHoldings;
        bool verified;         // Whether storage is verified/certified
        bool active;
    }
    
    struct MetalBalance {
        uint256 physical;      // Physical metal holdings
        uint256 digital;       // Digital representation
        uint256 reserved;      // Reserved for pending withdrawals
        uint256 lastUpdate;
    }
    
    // Core Functions
    function mint(address to, uint256 amount) external returns (bool);
    
    function burn(address from, uint256 amount) external returns (bool);
    
    function depositPhysical(MetalType metal, uint256 amount, address storage) external;
    
    function withdrawPhysical(MetalType metal, uint256 amount, address storage) external;
    
    function updatePrice(MetalType metal, uint256 pricePerOunce) external;
    
    function addStorage(address storage, string memory name, uint256 capacity) external;
    
    // Price Management
    function updateMetalPrice(MetalType metal, uint256 pricePerOunce) external;
    
    function convertPrice(MetalType metal, uint256 amount) external view returns (uint256 usdValue);
    
    // Storage Management
    function getStorageInfo(address storage) external view returns (StorageInfo memory);
    
    function getStorageHoldings(address storage) external view returns (uint256);
    
    function transferBetweenStorages(address fromStorage, address toStorage, MetalType metal, uint256 amount) external;
    
    // View Functions
    function getMetalInfo(MetalType metal) external view returns (MetalInfo memory);
    
    function getMetalBalance(MetalType metal) external view returns (MetalBalance memory);
    
    function getMetalPrice(MetalType metal) external view returns (uint256);
    
    function getSupportedMetals() external view returns (MetalInfo[] memory);
    
    function getActiveStorages() external view returns (address[] memory);
    
    // Conversion Functions
    function ouncesToGrams(uint256 ounces) external pure returns (uint256 grams);
    
    function gramsToOunces(uint256 grams) external pure returns (uint256 ounces);
    
    function calculateValue(MetalType metal, uint256 amount) external view returns (uint256 usdValue);
    
    // Oracle Integration
    function setPriceOracle(MetalType metal, address oracle) external;
    
    function updatePriceFromOracle(MetalType metal) external;
}