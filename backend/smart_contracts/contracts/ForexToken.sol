// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Imports
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "../interfaces/IForexToken.sol";
import "../libraries/SecurityUtils.sol";

/**
 * @title ForexToken
 * @dev Forex Token Contract - Valyuta juftliklar uchun
 */
contract ForexToken is IForexToken, ERC20, ERC20Burnable, ERC20Pausable, AccessControl {
    using SecurityUtils for uint256;
    
    // Roles
    bytes32 public constant FOREX_ADMIN_ROLE = keccak256("FOREX_ADMIN_ROLE");
    bytes32 public constant PRICE_ORACLE_ROLE = keccak256("PRICE_ORACLE_ROLE");
    bytes32 public constant CURRENCY_MANAGER_ROLE = keccak256("CURRENCY_MANAGER_ROLE");
    
    // State variables
    mapping(Currency => CurrencyInfo) private _currencyInfo;
    mapping(string => ExchangeRate) private _exchangeRates;
    mapping(address => mapping(string => CrossRate)) private _crossRates;
    
    uint256 private _decimals = 6; // Forex typically uses 6 decimal places
    
    // Supported currencies
    Currency[] private _supportedCurrencies;
    string[] private _supportedPairs;
    uint256 private _currencyCount = 0;
    
    // Events
    event CurrencyAdded(Currency currency, string symbol, uint256 decimals);
    event CurrencyRemoved(Currency currency, string symbol);
    event ExchangeRateUpdated(string indexed pair, uint256 rate, address indexed oracle);
    event CrossRateCalculated(string indexed from, string indexed to, uint256 rate);
    event CurrencyDecimalsUpdated(Currency indexed currency, uint256 oldDecimals, uint256 newDecimals);
    
    // Custom errors
    error CurrencyAlreadySupported(Currency currency);
    error CurrencyNotSupported(Currency currency);
    error InvalidCurrencySymbol(string symbol);
    error InvalidDecimals(uint256 decimals);
    error ExchangeRateNotFound(string pair);
    error InvalidPair(string pair);
    error RateTooLarge(uint256 rate);
    error OracleNotSet(string pair);
    error ConversionFailed(string from, string to, string reason);
    error UnsupportedPair(string from, string to);
    
    /**
     * @dev Constructor
     */
    constructor() ERC20("FOREX", "FOREX") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(FOREX_ADMIN_ROLE, msg.sender);
        _grantRole(PRICE_ORACLE_ROLE, msg.sender);
        _grantRole(CURRENCY_MANAGER_ROLE, msg.sender);
        
        // Initialize supported currencies
        _initializeCurrencies();
    }
    
    /**
     * @dev Mint tokens (for representing forex positions)
     */
    function mint(address to, uint256 amount) external override onlyRole(FOREX_ADMIN_ROLE) returns (bool) {
        require(to != address(0), "Cannot mint to zero address");
        require(amount > 0, "Cannot mint zero amount");
        
        _mint(to, amount);
        
        emit ForexTokensMinted(to, amount);
        return true;
    }
    
    /**
     * @dev Burn tokens
     */
    function burn(address from, uint256 amount) external override onlyRole(FOREX_ADMIN_ROLE) returns (bool) {
        require(from != address(0), "Cannot burn from zero address");
        require(amount > 0, "Cannot burn zero amount");
        require(balanceOf(from) >= amount, "Insufficient balance");
        
        _burn(from, amount);
        
        emit ForexTokensBurned(from, amount);
        return true;
    }
    
    /**
     * @dev Update exchange rate for a currency pair
     */
    function updateExchangeRate(string memory pair, uint256 rate) external override {
        require(hasRole(PRICE_ORACLE_ROLE, msg.sender), "Oracle role required");
        require(bytes(pair).length >= 6, "Invalid pair format");
        require(rate > 0, "Rate must be positive");
        
        _exchangeRates[pair] = ExchangeRate({
            pair: pair,
            rate: rate,
            timestamp: block.timestamp,
            oracle: msg.sender,
            active: true
        });
        
        emit ExchangeRateUpdated(pair, rate, msg.sender);
    }
    
    /**
     * @dev Convert currency using exchange rates
     */
    function convert(uint256 amount, string memory fromPair, string memory toPair) 
        external view override returns (uint256 convertedAmount) {
        require(amount > 0, "Amount must be positive");
        
        // Get exchange rates
        ExchangeRate storage fromRate = _exchangeRates[fromPair];
        ExchangeRate storage toRate = _exchangeRates[toPair];
        
        if (fromRate.rate == 0) {
            revert ExchangeRateNotFound(fromPair);
        }
        
        if (toRate.rate == 0) {
            revert ExchangeRateNotFound(toPair);
        }
        
        // Extract currencies from pairs
        (string memory baseCurrency, string memory quoteCurrency) = _parsePair(fromPair);
        (string memory targetBase, string memory targetQuote) = _parsePair(toPair);
        
        // Simple conversion logic - in practice this would be more sophisticated
        if (keccak256(bytes(baseCurrency)) == keccak256(bytes(targetBase))) {
            // Same base currency
            convertedAmount = amount.safeMul(toRate.rate).safeDiv(fromRate.rate);
        } else if (keccak256(bytes(quoteCurrency)) == keccak256(bytes(targetQuote))) {
            // Same quote currency
            convertedAmount = amount.safeMul(fromRate.rate).safeDiv(toRate.rate);
        } else {
            // Cross currency conversion
            convertedAmount = _calculateCrossRate(baseCurrency, quoteCurrency, targetBase, targetQuote, amount);
        }
        
        return convertedAmount;
    }
    
    /**
     * @dev Get exchange rate for a pair
     */
    function getExchangeRate(string memory pair) external view override returns (ExchangeRate memory) {
        return _exchangeRates[pair];
    }
    
    /**
     * @dev Calculate cross rate between currencies
     */
    function calculateCrossRate(string memory from, string memory to) 
        external view override returns (CrossRate memory) {
        uint256 crossRate = _calculateDirectCrossRate(from, to);
        
        return CrossRate({
            from: from,
            to: to,
            rate: crossRate,
            timestamp: block.timestamp
        });
    }
    
    /**
     * @dev Add a new currency
     */
    function addCurrency(Currency currency, string memory symbol, uint256 decimals) 
        external override onlyRole(CURRENCY_MANAGER_ROLE) {
        require(!_currencyInfo[currency].available, "Currency already supported");
        require(bytes(symbol).length >= 3 && bytes(symbol).length <= 5, "Invalid currency symbol");
        require(decimals >= 2 && decimals <= 8, "Invalid decimal places");
        
        _currencyInfo[currency] = CurrencyInfo({
            currency: currency,
            symbol: symbol,
            decimals: decimals,
            available: true
        });
        
        _supportedCurrencies.push(currency);
        _currencyCount++;
        
        emit CurrencyAdded(currency, symbol, decimals);
    }
    
    /**
     * @dev Remove a currency
     */
    function removeCurrency(Currency currency) external override onlyRole(CURRENCY_MANAGER_ROLE) {
        CurrencyInfo storage info = _currencyInfo[currency];
        require(info.available, "Currency not supported");
        
        info.available = false;
        
        emit CurrencyRemoved(currency, info.symbol);
    }
    
    /**
     * @dev Get all supported currencies
     */
    function getSupportedCurrencies() external view override returns (CurrencyInfo[] memory) {
        CurrencyInfo[] memory currencies = new CurrencyInfo[](_currencyCount);
        uint256 count = 0;
        
        for (uint256 i = 0; i < _supportedCurrencies.length && count < _currencyCount; i++) {
            CurrencyInfo storage info = _currencyInfo[_supportedCurrencies[i]];
            if (info.available) {
                currencies[count] = info;
                count++;
            }
        }
        
        // Resize array
        CurrencyInfo[] memory result = new CurrencyInfo[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = currencies[i];
        }
        
        return result;
    }
    
    /**
     * @dev Set exchange rate oracle for a pair
     */
    function setExchangeRateOracle(string memory pair, address oracle) 
        external override onlyRole(CURRENCY_MANAGER_ROLE) {
        require(oracle != address(0), "Invalid oracle address");
        
        ExchangeRate storage rate = _exchangeRates[pair];
        rate.oracle = oracle;
        
        emit OracleUpdated(pair, oracle);
    }
    
    /**
     * @dev Update rate from oracle
     */
    function updateRateFromOracle(string memory pair) external override {
        ExchangeRate storage rate = _exchangeRates[pair];
        
        if (rate.oracle == address(0)) {
            revert OracleNotSet(pair);
        }
        
        require(msg.sender == rate.oracle, "Only oracle can update rate");
        
        // This would interact with actual price feeds
        // For now, we'll assume oracle calls updateExchangeRate directly
        revert OraclePriceUpdateNotImplemented();
    }
    
    /**
     * @dev Get currency information
     */
    function getCurrencyInfo(Currency currency) external view override returns (CurrencyInfo memory) {
        return _currencyInfo[currency];
    }
    
    /**
     * @dev Check if currency is supported
     */
    function isCurrencySupported(Currency currency) external view override returns (bool) {
        return _currencyInfo[currency].available;
    }
    
    /**
     * @dev Generate pair string from base and quote currencies
     */
    function getPair(string memory base, string memory quote) 
        external pure override returns (string memory pair) {
        return string(abi.encodePacked(base, quote));
    }
    
    /**
     * @dev Get rate for a pair
     */
    function getRate(string memory pair) external view override returns (uint256) {
        return _exchangeRates[pair].rate;
    }
    
    /**
     * @dev Get last update time for a pair
     */
    function getLastUpdate(string memory pair) external view override returns (uint256) {
        return _exchangeRates[pair].timestamp;
    }
    
    /**
     * @dev Pause contract
     */
    function pause() external onlyRole(FOREX_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyRole(FOREX_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Initialize default currencies
     */
    function _initializeCurrencies() internal {
        // Major currencies
        addCurrency(Currency.USD, "USD", 2);
        addCurrency(Currency.EUR, "EUR", 2);
        addCurrency(Currency.GBP, "GBP", 2);
        addCurrency(Currency.JPY, "JPY", 0);
        addCurrency(Currency.CHF, "CHF", 2);
        addCurrency(Currency.CAD, "CAD", 2);
        addCurrency(Currency.AUD, "AUD", 2);
        addCurrency(Currency.NZD, "NZD", 2);
    }
    
    /**
     * @dev Parse currency pair
     */
    function _parsePair(string memory pair) internal pure returns (string memory base, string memory quote) {
        bytes memory pairBytes = bytes(pair);
        require(pairBytes.length >= 6, "Invalid pair format");
        
        // Assume 3-character currency codes
        base = string(abi.encodePacked(pairBytes[0], pairBytes[1], pairBytes[2]));
        quote = string(abi.encodePacked(pairBytes[3], pairBytes[4], pairBytes[5]));
        
        return (base, quote);
    }
    
    /**
     * @dev Calculate cross rate between two currencies
     */
    function _calculateCrossRate(
        string memory fromBase,
        string memory fromQuote,
        string memory toBase,
        string memory toQuote,
        uint256 amount
    ) internal view returns (uint256) {
        string memory fromPair = string(abi.encodePacked(fromBase, fromQuote));
        string memory toPair = string(abi.encodePacked(toBase, toQuote));
        
        ExchangeRate storage fromRate = _exchangeRates[fromPair];
        ExchangeRate storage toRate = _exchangeRates[toPair];
        
        if (fromRate.rate == 0 || toRate.rate == 0) {
            revert UnsupportedPair(fromPair, toPair);
        }
        
        // Cross rate calculation through USD
        if (keccak256(bytes(fromBase)) == keccak256(bytes("USD"))) {
            // Direct USD to target
            return amount.safeMul(toRate.rate).safeDiv(1000000); // Adjust for precision
        } else if (keccak256(bytes(fromQuote)) == keccak256(bytes("USD"))) {
            // USD to base currency
            return amount.safeMul(1000000).safeDiv(fromRate.rate).safeMul(toRate.rate).safeDiv(1000000);
        } else if (keccak256(bytes(toBase)) == keccak256(bytes("USD"))) {
            // Source to USD
            return amount.safeMul(fromRate.rate).safeDiv(1000000);
        } else {
            // Both through USD
            return amount.safeMul(fromRate.rate).safeDiv(toRate.rate);
        }
    }
    
    /**
     * @dev Calculate direct cross rate
     */
    function _calculateDirectCrossRate(string memory from, string memory to) 
        internal view returns (uint256 rate) {
        // This is a simplified cross rate calculation
        // In practice, you'd want to use actual forex data
        string memory pair = string(abi.encodePacked(from, to));
        
        if (_exchangeRates[pair].rate > 0) {
            return _exchangeRates[pair].rate;
        }
        
        // Try reverse pair
        string memory reversePair = string(abi.encodePacked(to, from));
        if (_exchangeRates[reversePair].rate > 0) {
            return 1000000000 / _exchangeRates[reversePair].rate; // Simple inverse
        }
        
        return 0;
    }
    
    /**
     * @dev Required overrides for ERC20 and Pausable
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20, ERC20Pausable) {
        super._beforeTokenTransfer(from, to, amount);
    }
    
    // Custom errors and events
    error ForexTokensMinted(address indexed to, uint256 amount);
    error ForexTokensBurned(address indexed from, uint256 amount);
    error OracleUpdated(string indexed pair, address indexed oracle);
    error OraclePriceUpdateNotImplemented();
    
    /**
     * @dev Additional events
     */
    event ForexTokensMinted(address indexed to, uint256 amount);
    event ForexTokensBurned(address indexed from, uint256 amount);
    event OracleUpdated(string indexed pair, address indexed oracle);
}