// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Imports
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "../interfaces/IStockToken.sol";
import "../libraries/SecurityUtils.sol";

/**
 * @title StockToken
 * @dev Stock Token Contract - AAPL, GOOGL va boshqa aktsiyalar uchun
 */
contract StockToken is IStockToken, ERC20, ERC20Burnable, ERC20Pausable, AccessControl {
    using SecurityUtils for uint256;
    
    // Roles
    bytes32 public constant STOCK_ADMIN_ROLE = keccak256("STOCK_ADMIN_ROLE");
    bytes32 public constant PRICE_ORACLE_ROLE = keccak256("PRICE_ORACLE_ROLE");
    bytes32 public constant DIVIDEND_MANAGER_ROLE = keccak256("DIVIDEND_MANAGER_ROLE");
    
    // State variables
    StockInfo private _stockInfo;
    DividendInfo private _dividendInfo;
    uint256 private _decimals = 18; // Standard ERC20 decimals
    
    // Price feed
    mapping(address => uint256) private _priceOracles;
    uint256 private _lastPrice = 0;
    uint256 private _priceUpdateTime = 0;
    
    // Corporate actions
    mapping(bytes32 => bytes) private _corporateActions;
    uint256 private _actionCount = 0;
    
    // Events
    event PriceUpdated(uint256 oldPrice, uint256 newPrice, uint256 timestamp);
    event DividendDeclared(uint256 totalAmount, uint256 perToken, uint256 recordDate, uint256 paymentDate);
    event DividendPaid(address indexed holder, uint256 amount);
    event CorporateActionExecuted(string action, bytes32 actionHash, bytes data);
    event OracleUpdated(address oldOracle, address newOracle);
    event StockInfoUpdated(string symbol, string companyName, uint256 sharesOutstanding);
    
    // Custom errors
    error InvalidStockSymbol(string symbol);
    error InvalidPrice(uint256 price);
    error ZeroPrice();
    error InvalidDividendAmount(uint256 amount);
    error DividendAlreadyPaid(uint256 recordDate);
    error NoDividendToPay();
    error InvalidShares(uint256 shares);
    error OracleNotSet(address oracle);
    error InvalidCorporateAction(string action);
    error UnauthorizedOracle(address oracle);
    
    /**
     * @dev Constructor
     * @param stockAddress Address of the stock contract
     * @param symbol Stock symbol (e.g., "AAPL")
     * @param companyName Company name (e.g., "Apple Inc.")
     * @param sharesOutstanding Total shares outstanding
     */
    constructor(
        address stockAddress,
        string memory symbol,
        string memory companyName,
        uint256 sharesOutstanding
    ) ERC20(symbol, symbol) {
        require(bytes(symbol).length > 0 && bytes(symbol).length <= 10, "Invalid symbol length");
        require(bytes(companyName).length > 0, "Invalid company name");
        require(sharesOutstanding > 0, "Invalid shares outstanding");
        
        // Setup roles
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(STOCK_ADMIN_ROLE, msg.sender);
        _grantRole(PRICE_ORACLE_ROLE, msg.sender);
        _grantRole(DIVIDEND_MANAGER_ROLE, msg.sender);
        
        // Initialize stock info
        _stockInfo = StockInfo({
            stock: stockAddress,
            symbol: symbol,
            companyName: companyName,
            sharesOutstanding: sharesOutstanding,
            currentPrice: 0,
            lastUpdate: 0,
            active: true
        });
    }
    
    /**
     * @dev Mint tokens (only authorized minters)
     */
    function mint(address to, uint256 amount) external override onlyRole(STOCK_ADMIN_ROLE) returns (bool) {
        require(to != address(0), "Cannot mint to zero address");
        require(amount > 0, "Cannot mint zero amount");
        
        // Update total supply tracking if needed
        // In this implementation, we'll track 1:1 ratio with shares
        uint256 currentSupply = totalSupply();
        uint256 maxSupply = _stockInfo.sharesOutstanding * 10**18; // 1 share = 1 token (with 18 decimals)
        
        require(currentSupply.safeAdd(amount) <= maxSupply, "Exceeds maximum supply");
        
        _mint(to, amount);
        
        emit StockTokensMinted(to, amount);
        return true;
    }
    
    /**
     * @dev Burn tokens
     */
    function burn(address from, uint256 amount) external override onlyRole(STOCK_ADMIN_ROLE) returns (bool) {
        require(from != address(0), "Cannot burn from zero address");
        require(amount > 0, "Cannot burn zero amount");
        require(balanceOf(from) >= amount, "Insufficient balance");
        
        _burn(from, amount);
        
        emit StockTokensBurned(from, amount);
        return true;
    }
    
    /**
     * @dev Update stock price
     */
    function updatePrice(uint256 newPrice) external override {
        require(hasRole(PRICE_ORACLE_ROLE, msg.sender), "Oracle role required");
        require(newPrice > 0, "Price must be positive");
        
        uint256 oldPrice = _lastPrice;
        _lastPrice = newPrice;
        _priceUpdateTime = block.timestamp;
        
        _stockInfo.currentPrice = newPrice;
        _stockInfo.lastUpdate = block.timestamp;
        
        emit PriceUpdated(oldPrice, newPrice, block.timestamp);
    }
    
    /**
     * @dev Pay dividend to all token holders
     */
    function payDividend(uint256 totalAmount) external override onlyRole(DIVIDEND_MANAGER_ROLE) {
        require(totalAmount > 0, "Dividend amount must be positive");
        require(totalSupply() > 0, "No tokens outstanding");
        require(_dividendInfo.recordDate == 0, "Dividend already declared");
        
        // Calculate per-token dividend
        uint256 perToken = totalAmount.safeDiv(totalSupply());
        
        // Record dividend info
        _dividendInfo = DividendInfo({
            recordDate: block.timestamp,
            paymentDate: block.timestamp + 30 days, // 30 days to pay
            amount: totalAmount,
            perToken: perToken,
            totalDistributed: 0
        });
        
        emit DividendDeclared(totalAmount, perToken, _dividendInfo.recordDate, _dividendInfo.paymentDate);
    }
    
    /**
     * @dev Record corporate action
     */
    function recordCorporateAction(string memory action, bytes memory data) 
        external override onlyRole(STOCK_ADMIN_ROLE) {
        require(bytes(action).length > 0, "Action cannot be empty");
        
        _actionCount++;
        bytes32 actionHash = keccak256(abi.encodePacked(_actionCount, action, block.timestamp));
        _corporateActions[actionHash] = data;
        
        emit CorporateActionExecuted(action, actionHash, data);
    }
    
    /**
     * @dev Claim dividend for a specific holder
     */
    function claimDividend(address holder) external returns (uint256 amount) {
        require(holder != address(0), "Invalid holder address");
        
        if (_dividendInfo.recordDate == 0) {
            revert NoDividendToPay();
        }
        
        if (block.timestamp > _dividendInfo.paymentDate) {
            revert DividendPaymentPeriodExpired();
        }
        
        uint256 holderBalance = balanceOf(holder);
        if (holderBalance == 0) {
            return 0;
        }
        
        uint256 dividendAmount = holderBalance.safeMul(_dividendInfo.perToken);
        require(dividendAmount > 0, "No dividend to claim");
        
        // Transfer dividend (simplified - assumes stablecoin)
        // In practice, this would use proper dividend distribution logic
        IERC20 stablecoin = IERC20(0xA0b86a33E6B3c4E3f4dE8B3C4C5D5B4E3F2E1D0C9); // Example USDC
        stablecoin.transfer(holder, dividendAmount);
        
        _dividendInfo.totalDistributed = _dividendInfo.totalDistributed.safeAdd(dividendAmount);
        
        emit DividendPaid(holder, dividendAmount);
        
        return dividendAmount;
    }
    
    /**
     * @dev Get stock information
     */
    function getStockInfo() external view override returns (StockInfo memory) {
        return _stockInfo;
    }
    
    /**
     * @dev Get current price
     */
    function getCurrentPrice() external view override returns (uint256) {
        return _lastPrice;
    }
    
    /**
     * @dev Get dividend information
     */
    function getDividendInfo() external view override returns (DividendInfo memory) {
        return _dividendInfo;
    }
    
    /**
     * @dev Get total supply
     */
    function getTotalSupply() external view override returns (uint256) {
        return totalSupply();
    }
    
    /**
     * @dev Get last update timestamp
     */
    function getLastUpdate() external view override returns (uint256) {
        return _stockInfo.lastUpdate;
    }
    
    /**
     * @dev Set price oracle
     */
    function setPriceOracle(address oracle) external override onlyRole(STOCK_ADMIN_ROLE) {
        require(oracle != address(0), "Invalid oracle address");
        
        address oldOracle = address(uint160(_priceOracles[address(0)]));
        _priceOracles[address(0)] = oracle;
        
        emit OracleUpdated(oldOracle, oracle);
    }
    
    /**
     * @dev Get price oracle
     */
    function getPriceOracle() external view override returns (address) {
        return address(uint160(_priceOracles[address(0)]));
    }
    
    /**
     * @dev Update price from oracle
     */
    function updatePriceFromOracle() external override {
        address oracle = address(uint160(_priceOracles[address(0)]));
        require(oracle != address(0), OracleNotSet(oracle));
        
        // This would interact with actual oracle
        // For now, we'll assume the oracle calls updatePrice directly
        revert OraclePriceUpdateNotImplemented();
    }
    
    /**
     * @dev Update stock information
     */
    function updateStockInfo(string memory newSymbol, string memory newCompanyName, uint256 newSharesOutstanding) 
        external onlyRole(STOCK_ADMIN_ROLE) {
        require(bytes(newSymbol).length > 0 && bytes(newSymbol).length <= 10, "Invalid symbol");
        require(bytes(newCompanyName).length > 0, "Invalid company name");
        require(newSharesOutstanding > 0, "Invalid shares outstanding");
        
        _stockInfo.symbol = newSymbol;
        _stockInfo.companyName = newCompanyName;
        _stockInfo.sharesOutstanding = newSharesOutstanding;
        
        emit StockInfoUpdated(newSymbol, newCompanyName, newSharesOutstanding);
    }
    
    /**
     * @dev Set stock active/inactive
     */
    function setStockActive(bool active) external onlyRole(STOCK_ADMIN_ROLE) {
        _stockInfo.active = active;
    }
    
    /**
     * @dev Check if stock is active
     */
    function isStockActive() external view returns (bool) {
        return _stockInfo.active;
    }
    
    /**
     * @dev Get corporate action data
     */
    function getCorporateAction(bytes32 actionHash) external view returns (bytes memory) {
        return _corporateActions[actionHash];
    }
    
    /**
     * @dev Get total number of corporate actions
     */
    function getTotalCorporateActions() external view returns (uint256) {
        return _actionCount;
    }
    
    /**
     * @dev Pause contract
     */
    function pause() external onlyRole(STOCK_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyRole(STOCK_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Required overrides for ERC20 and Pausable
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20, ERC20Pausable) {
        require(_stockInfo.active, "Stock is not active");
        super._beforeTokenTransfer(from, to, amount);
    }
    
    // Custom errors
    error StockTokensMinted(address indexed to, uint256 amount);
    error StockTokensBurned(address indexed from, uint256 amount);
    error DividendPaymentPeriodExpired();
    error OraclePriceUpdateNotImplemented();
    
    /**
     * @dev Additional events
     */
    event StockTokensMinted(address indexed to, uint256 amount);
    event StockTokensBurned(address indexed from, uint256 amount);
}