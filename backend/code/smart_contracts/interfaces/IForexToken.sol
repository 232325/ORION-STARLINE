// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IForexToken Interface
 * @dev Forex Token interfeysi - Valyuta juftliklarini ifodalash
 */
interface IForexToken {
    // Events
    event ExchangeRateUpdated(string indexed pair, uint256 rate, uint256 timestamp);
    event CrossRateCalculated(string indexed from, string indexed to, uint256 rate);
    
    // Enums
    enum Currency {
        USD,
        EUR,
        GBP,
        JPY,
        CHF,
        CAD,
        AUD,
        NZD
    }
    
    // Structs
    struct CurrencyInfo {
        Currency currency;
        string symbol;
        uint256 decimals;
        bool available;
    }
    
    struct ExchangeRate {
        string pair;           // e.g., "EURUSD"
        uint256 rate;          // Exchange rate (e.g., 1 EUR = 1.0956 USD)
        uint256 timestamp;     // Last update
        address oracle;        // Price oracle
        bool active;           // Is rate active
    }
    
    struct CrossRate {
        string from;
        string to;
        uint256 rate;
        uint256 timestamp;
    }
    
    // Core Functions
    function mint(address to, uint256 amount) external returns (bool);
    
    function burn(address from, uint256 amount) external returns (bool);
    
    function updateExchangeRate(string memory pair, uint256 rate) external;
    
    function convert(uint256 amount, string memory fromPair, string memory toPair) external view returns (uint256);
    
    function getExchangeRate(string memory pair) external view returns (ExchangeRate memory);
    
    function calculateCrossRate(string memory from, string memory to) external view returns (CrossRate memory);
    
    // Currency Operations
    function addCurrency(Currency currency, string memory symbol, uint256 decimals) external;
    
    function removeCurrency(Currency currency) external;
    
    function getSupportedCurrencies() external view returns (CurrencyInfo[] memory);
    
    // Oracle Integration
    function setExchangeRateOracle(string memory pair, address oracle) external;
    
    function updateRateFromOracle(string memory pair) external;
    
    // View Functions
    function getCurrencyInfo(Currency currency) external view returns (CurrencyInfo memory);
    
    function isCurrencySupported(Currency currency) external view returns (bool);
    
    function getPair(string memory base, string memory quote) external pure returns (string memory);
    
    function getRate(string memory pair) external view returns (uint256);
    
    function getLastUpdate(string memory pair) external view returns (uint256);
}