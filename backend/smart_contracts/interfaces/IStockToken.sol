// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IStockToken Interface
 * @dev Stock Token interfeysi - AAPL, GOOGL va boshqa aktsiyalarni ifodalash
 */
interface IStockToken {
    // Events
    event StockUpdate(address indexed stock, uint256 price, uint256 timestamp);
    event DividendPaid(address indexed stock, uint256 totalAmount, uint256 perToken);
    event CorporateAction(address indexed stock, string action, bytes data);
    
    // Structs
    struct StockInfo {
        address stock;
        string symbol;
        string companyName;
        uint256 sharesOutstanding;
        uint256 currentPrice;
        uint256 lastUpdate;
        bool active;
    }
    
    struct DividendInfo {
        uint256 recordDate;
        uint256 paymentDate;
        uint256 amount;
        uint256 perToken;
        uint256 totalDistributed;
    }
    
    // Core Functions
    function mint(address to, uint256 amount) external returns (bool);
    
    function burn(address from, uint256 amount) external returns (bool);
    
    function updatePrice(uint256 newPrice) external;
    
    function payDividend(uint256 totalAmount) external;
    
    function recordCorporateAction(string memory action, bytes memory data) external;
    
    // View Functions
    function getStockInfo() external view returns (StockInfo memory);
    
    function getCurrentPrice() external view returns (uint256);
    
    function getDividendInfo() external view returns (DividendInfo memory);
    
    function getTotalSupply() external view returns (uint256);
    
    function getLastUpdate() external view returns (uint256);
    
    // Oracle Integration
    function setPriceOracle(address oracle) external;
    
    function getPriceOracle() external view returns (address);
    
    function updatePriceFromOracle() external;
}